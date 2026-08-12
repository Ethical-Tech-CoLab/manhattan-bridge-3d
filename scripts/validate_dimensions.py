"""Run the geometry regression and source traceability suites.

    python scripts/validate_dimensions.py
    python scripts/validate_dimensions.py --suite geometry
    python scripts/validate_dimensions.py --json

Inputs are the test definitions in /tests, the control document, the source register, and the
artifacts produced by ``build_control_skeleton.py``. A report is written to
``tests/validation_report.json``.

Exit code is 0 when every ``assert`` test passes. ``report_only`` tests never fail the run; their
deviation is recorded so that resolving an open question shows up as a visible change.
"""

from __future__ import annotations

import argparse
import ast
import json
import operator
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from control_model import CONFIDENCE_GRADES, load_control_model  # noqa: E402
from normalize_units import ho_millimeters  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parent

ALLOWED_SOURCE_BASIS = {
    "drawing",
    "official_facts",
    "photo",
    "mesh_reference",
    "photogrammetry",
    "control_dimension",
    "inferred",
}
CONFIDENCE_ORDER = {grade: i for i, grade in enumerate(CONFIDENCE_GRADES)}
# A quad is a plane, not a volume. Only boxes represent claimed solid extents, so only boxes are
# subject to the "no solid geometry above grade" ceiling.
SOLID_GEOMETRY_KINDS = {"box"}
SNAKE_CASE_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
SOURCE_ROW_RE = re.compile(r"^\|\s*(SRC-\d+)\s*\|")
OQ_ROW_RE = re.compile(r"^\|\s*(OQ-\d+)\s*\|")

_BIN_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


@dataclass
class Result:
    test_id: str
    title: str
    suite: str
    mode: str
    status: str  # pass | fail | error | reported
    detail: str
    actual: Any = None
    expected: Any = None
    deviation: float | None = None
    findings: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        payload = {
            "id": self.test_id,
            "title": self.title,
            "suite": self.suite,
            "mode": self.mode,
            "status": self.status,
            "detail": self.detail,
        }
        if self.actual is not None:
            payload["actual"] = self.actual
        if self.expected is not None:
            payload["expected"] = self.expected
        if self.deviation is not None:
            payload["deviation"] = self.deviation
        if self.findings:
            payload["findings"] = self.findings
        return payload


class Context:
    """Everything the tests can look at."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.model = load_control_model(root / "GEOMETRY-CONTROL.md")
        self.build_report = json.loads((root / "viewer" / "metadata" / "build_report.json").read_text("utf-8"))
        self.parts_doc = json.loads((root / "viewer" / "metadata" / "parts.json").read_text("utf-8"))
        self.parts: list[dict[str, Any]] = self.parts_doc["parts"]
        control_doc_text = (root / "GEOMETRY-CONTROL.md").read_text("utf-8")
        register_text = (root / "SOURCE-REGISTER.md").read_text("utf-8")
        self.open_question_ids = {
            m.group(1) for line in control_doc_text.splitlines() if (m := OQ_ROW_RE.match(line.strip()))
        }
        self.source_ids: set[str] = set()
        self.source_verified: dict[str, bool] = {}
        for line in register_text.splitlines():
            stripped = line.strip()
            m = SOURCE_ROW_RE.match(stripped)
            if not m:
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            src_id = m.group(1)
            self.source_ids.add(src_id)
            # The Verified cell is written in markdown, e.g. "**yes**" or "no - HTTP 403".
            verified_cell = re.sub(r"[*_`]", "", cells[7]).strip().lower() if len(cells) > 7 else "no"
            self.source_verified[src_id] = verified_cell.startswith("yes")
        self.control_confidence_by_id = {
            c["control_id"]: c["confidence"] for c in self.parts_doc["controls"]
        }

    @property
    def namespace(self) -> dict[str, float]:
        ns: dict[str, float] = dict(self.build_report["controls_m"])
        for key, value in self.build_report["stations"].items():
            ns[key.replace("-", "_")] = value
        for key, value in self.build_report["elevations"].items():
            ns[key.replace("-", "_")] = value
        for key, value in self.build_report["measures"].items():
            if isinstance(value, (int, float)):
                ns[key] = float(value)
        return ns


def safe_eval(expr: str, namespace: dict[str, float]) -> float:
    node = ast.parse(expr, mode="eval").body

    def visit(n: ast.AST) -> float:
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id not in namespace:
                raise KeyError(f"unknown symbol {n.id!r} in expression {expr!r}")
            return float(namespace[n.id])
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN_OPS:
            return _BIN_OPS[type(n.op)](visit(n.left), visit(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            value = visit(n.operand)
            return value if isinstance(n.op, ast.UAdd) else -value
        raise ValueError(f"expression {expr!r} contains an unsupported construct")

    return visit(node)


# ------------------------------------------------------------------ numeric tests


def _numeric_result(test: dict[str, Any], suite: str, actual: float, expected: float) -> Result:
    tolerance = float(test.get("tolerance", 1e-6))
    deviation = actual - expected
    ok = abs(deviation) <= tolerance
    mode = test.get("mode", "assert")
    unit = test.get("unit", "")
    if mode == "report_only":
        status = "reported"
        detail = f"actual {actual:.6g} {unit}, reference {expected:.6g} {unit}, deviation {deviation:+.6g} {unit}"
        if not ok:
            detail += f" (outside the recorded tolerance of {tolerance:g})"
    else:
        status = "pass" if ok else "fail"
        detail = f"actual {actual:.6g} {unit}, expected {expected:.6g} {unit}, deviation {deviation:+.3g}"
    return Result(
        test_id=test["id"],
        title=test["title"],
        suite=suite,
        mode=mode,
        status=status,
        detail=detail,
        actual=round(actual, 9),
        expected=round(expected, 9),
        deviation=round(deviation, 9),
    )


def run_numeric(test: dict[str, Any], ctx: Context, suite: str) -> Result:
    kind = test["kind"]
    ns = ctx.namespace
    if kind == "control":
        actual = ctx.model.m(test["key"])
    elif kind == "station":
        actual = ctx.build_report["stations"][test["station"]]
    elif kind == "elevation":
        actual = ctx.build_report["elevations"][test["elevation"]]
    elif kind == "measure":
        raw = ctx.build_report["measures"][test["measure"]]
        # A digest is a measure but not a number. Report it verbatim rather than coercing it,
        # which is what an earlier version did -- and it errored rather than reporting, so the
        # check silently stopped covering anything.
        if isinstance(raw, str):
            return Result(
                test_id=test["id"],
                title=test["title"],
                suite=suite,
                mode=test.get("mode", "report"),
                status="reported",
                detail=f"{test['measure']} = {raw}",
                actual=raw,
                expected=test.get("expected"),
            )
        actual = float(raw)
    elif kind == "expression":
        actual = safe_eval(test["expr"], ns)
    elif kind == "ho_conversion":
        actual = ho_millimeters(ctx.model.m(test["key"]))
    else:  # pragma: no cover
        raise ValueError(f"unknown numeric test kind {kind!r}")

    if "expected_expr" in test:
        expected = safe_eval(test["expected_expr"], ns)
    elif "expected_mm" in test:
        expected = float(test["expected_mm"])
    else:
        expected = float(test["expected"])
    return _numeric_result(test, suite, actual, expected)


# --------------------------------------------------------------------- rule tests

REQUIRED_METADATA_FIELDS = (
    "part_id",
    "system",
    "source_basis",
    "confidence",
    "prototype_units",
    "ho_scale_units",
    "notes",
    "scale",
    "last_modified_by_agent",
    "review_status",
)


def _rule_result(test: dict[str, Any], suite: str, findings: list[str], summary: str) -> Result:
    mode = test.get("mode", "assert")
    if mode == "report_only":
        status = "reported"
    else:
        status = "pass" if not findings else "fail"
    detail = summary if not findings else f"{summary}; {len(findings)} finding(s)"
    return Result(
        test_id=test["id"],
        title=test["title"],
        suite=suite,
        mode=mode,
        status=status,
        detail=detail,
        findings=findings[:40],
    )


def run_rule(test: dict[str, Any], ctx: Context, suite: str) -> Result:
    rule = test["rule"]
    parts = ctx.parts
    findings: list[str] = []
    summary = ""

    if rule == "required_fields":
        for part in parts:
            for fieldname in REQUIRED_METADATA_FIELDS:
                if not part.get(fieldname):
                    findings.append(f"{part.get('part_id', '<unnamed>')}: missing {fieldname}")
        summary = f"{len(parts)} parts checked against {len(REQUIRED_METADATA_FIELDS)} required fields"

    elif rule == "unique_snake_case_part_ids":
        seen: set[str] = set()
        for part in parts:
            pid = part["part_id"]
            if pid in seen:
                findings.append(f"duplicate part_id {pid}")
            seen.add(pid)
            if not SNAKE_CASE_RE.match(pid):
                findings.append(f"{pid}: not lowercase snake_case")
        summary = f"{len(seen)} unique part_id values"

    elif rule == "valid_confidence_grades":
        for part in parts:
            if part["confidence"] not in CONFIDENCE_GRADES:
                findings.append(f"{part['part_id']}: confidence {part['confidence']!r}")
        summary = f"{len(parts)} parts checked"

    elif rule == "source_basis_vocabulary":
        for part in parts:
            unknown = set(part["source_basis"]) - ALLOWED_SOURCE_BASIS
            if unknown:
                findings.append(f"{part['part_id']}: unknown source_basis {sorted(unknown)}")
        summary = f"vocabulary of {len(ALLOWED_SOURCE_BASIS)} terms"

    elif rule == "weakest_link_confidence":
        for part in parts:
            worst = part.get("basis_confidence", part["confidence"])
            for ref in part.get("control_refs", []):
                grade = ctx.control_confidence_by_id.get(ref)
                if grade and CONFIDENCE_ORDER[grade] > CONFIDENCE_ORDER[worst]:
                    worst = grade
            if part["confidence"] != worst:
                findings.append(
                    f"{part['part_id']}: graded {part['confidence']} but its weakest control is {worst}"
                )
        summary = f"{len(parts)} parts checked against their control references"

    elif rule == "d_parts_cite_open_question":
        d_parts = [p for p in parts if p["confidence"] == "D"]
        for part in d_parts:
            cited = part.get("open_questions") or re.findall(r"OQ-\d+", part.get("notes", ""))
            if not cited:
                findings.append(f"{part['part_id']}: confidence D with no open question cited")
        summary = f"{len(d_parts)} confidence D parts"

    elif rule == "required_part_ids":
        present = {p["part_id"] for p in parts}
        for required in test["required"]:
            if required not in present:
                findings.append(f"missing required part {required}")
        summary = f"{len(test['required'])} required part IDs"

    elif rule == "required_systems":
        present = {p["system"] for p in parts}
        for required in test["required"]:
            if required not in present:
                findings.append(f"system {required} has no parts")
        summary = f"{len(test['required'])} required systems"

    elif rule == "part_grade_expectations":
        expected: dict[str, str] = test["expected_grades"]
        actual = {p["part_id"]: p["confidence"] for p in parts}
        for part_id, grade in expected.items():
            if part_id not in actual:
                findings.append(f"{part_id}: part is missing")
            elif actual[part_id] != grade:
                findings.append(f"{part_id}: graded {actual[part_id]}, expected {grade}")
        summary = f"{len(expected)} part grades pinned"

    elif rule == "no_solid_geometry_above_grade":
        limit = CONFIDENCE_ORDER[test["max_grade"]]
        for part in parts:
            kinds = set(part.get("geometry_kinds", []))
            if kinds & SOLID_GEOMETRY_KINDS and CONFIDENCE_ORDER[part["confidence"]] < limit:
                findings.append(
                    f"{part['part_id']}: solid geometry graded {part['confidence']}, "
                    f"better than the {test['max_grade']} ceiling"
                )
        summary = f"ceiling {test['max_grade']} for box/quad geometry"

    elif rule == "placeholder_control_census":
        placeholders = [c for c in ctx.parts_doc["controls"] if c["is_placeholder"]]
        sourced = len(ctx.parts_doc["controls"]) - len(placeholders)
        summary = (
            f"{len(placeholders)} placeholder controls remain, {sourced} sourced; "
            f"{sum(1 for p in parts if p['confidence'] == 'D')} of {len(parts)} parts are confidence D"
        )

    elif rule == "cited_sources_registered":
        for control in ctx.parts_doc["controls"]:
            for src in control["source_ids"]:
                if src not in ctx.source_ids:
                    findings.append(f"{control['control_id']}: cites unregistered source {src}")
        summary = f"{len(ctx.source_ids)} registered sources"

    elif rule == "graded_controls_have_sources":
        for control in ctx.parts_doc["controls"]:
            if control["confidence"] != "D" and not control["source_ids"]:
                findings.append(f"{control['control_id']}: graded {control['confidence']} with no source")
        summary = f"{len(ctx.parts_doc['controls'])} controls"

    elif rule == "placeholders_have_no_sources":
        for control in ctx.parts_doc["controls"]:
            if control["is_placeholder"] and control["source_ids"]:
                findings.append(f"{control['control_id']}: placeholder citing {control['source_ids']}")
        summary = f"{sum(1 for c in ctx.parts_doc['controls'] if c['is_placeholder'])} placeholders"

    elif rule == "part_control_refs_resolve":
        known = set(ctx.control_confidence_by_id)
        for part in parts:
            for ref in part.get("control_refs", []):
                if ref not in known:
                    findings.append(f"{part['part_id']}: unknown control reference {ref}")
        summary = f"{sum(len(p.get('control_refs', [])) for p in parts)} control references"

    elif rule == "open_questions_registered":
        for part in parts:
            cited = set(part.get("open_questions", [])) | set(re.findall(r"OQ-\d+", part.get("notes", "")))
            for oq in cited:
                if oq not in ctx.open_question_ids:
                    findings.append(f"{part['part_id']}: cites unregistered {oq}")
        summary = f"{len(ctx.open_question_ids)} registered open questions"

    elif rule == "parts_have_source_basis":
        for part in parts:
            if not part.get("source_basis"):
                findings.append(f"{part['part_id']}: empty source_basis")
        summary = f"{len(parts)} parts"

    elif rule == "forbidden_source_basis":
        forbidden = set(test["forbidden"])
        for part in parts:
            used = forbidden & set(part["source_basis"])
            if used:
                findings.append(f"{part['part_id']}: claims {sorted(used)} in Milestone 1")
        summary = f"forbidden in Milestone 1: {sorted(forbidden)}"

    elif rule == "verification_pending_census":
        pending = []
        for control in ctx.parts_doc["controls"]:
            srcs = control["source_ids"]
            if srcs and not any(ctx.source_verified.get(s, False) for s in srcs):
                pending.append(control["control_id"])
        summary = (
            f"{len(pending)} controls depend only on unverified sources: "
            f"{', '.join(pending) if pending else 'none'}"
        )

    elif rule == "cited_sources_have_verification_state":
        for control in ctx.parts_doc["controls"]:
            for src in control["source_ids"]:
                if src not in ctx.source_verified:
                    findings.append(f"{src}: no Verified column value in SOURCE-REGISTER.md")
        summary = f"{len(ctx.source_verified)} sources carry a verification state"

    elif rule == "parts_have_known_system":
        known = set(test["known"])
        for part in parts:
            if part["system"] not in known:
                findings.append(f"{part['part_id']}: system {part['system']!r} is not in the taxonomy")
        summary = f"taxonomy of {len(known)} systems"

    elif rule == "parts_have_review_fields":
        for part in parts:
            if not part.get("review_status") or not part.get("last_modified_by_agent"):
                findings.append(f"{part['part_id']}: missing review_status or last_modified_by_agent")
        summary = f"{len(parts)} parts"

    elif rule == "control_document_hash_matches":
        built = ctx.parts_doc["control_document"]["sha256"]
        current = ctx.model.document_sha256
        if built != current:
            findings.append(
                f"parts.json was built from GEOMETRY-CONTROL.md sha256 {built[:12]}, "
                f"current document is {current[:12]}; re-run build_control_skeleton.py"
            )
        summary = f"control document sha256 {current[:12]}"

    elif rule == "documented_counts_match_model":
        # Prose drifts. Three published counts had already gone stale before this rule existed:
        # the manifest said "7 of 69 control values remain placeholders" when it was 14 of 78,
        # the README claimed 44 grade-D parts and thirteen conflicts against 66 and fifteen, and
        # CONFIDENCE-MODEL.md was still describing a 95-part model at Milestone 7.
        #
        # None of those was a lie anyone told; each was true when written and nobody re-typed it.
        # That is precisely the class of error a guard catches and vigilance does not, and this
        # repository already refuses to trust vigilance anywhere else.
        #
        # Only unambiguous, machine-checkable phrasings are matched. The aim is to catch the
        # sentence that quietly goes out of date, not to police prose.
        live = {
            "parts": len(parts),
            "placeholders": sum(1 for c in ctx.model.controls.values() if c.is_placeholder),
            "controls": len(ctx.model.controls),
            "grade_d": sum(1 for p in parts if p.get("confidence") == "D"),
        }
        patterns = [
            # "14 of 78 control values" / "14 of 78 controls"
            (re.compile(r"(\d+)\s+of\s+(\d+)\s+control", re.I),
             lambda m: (int(m.group(1)) == live["placeholders"]
                        and int(m.group(2)) == live["controls"]),
             lambda: f'{live["placeholders"]} of {live["controls"]} control'),
            # "across 103 parts"
            (re.compile(r"across\s+(\d+)\s+parts", re.I),
             lambda m: int(m.group(1)) == live["parts"],
             lambda: f'across {live["parts"]} parts'),
        ]
        for rel in ("README.md", "CONFIDENCE-MODEL.md", "GEOMETRY-CONTROL.md"):
            path = REPO_ROOT / rel
            if not path.exists():
                continue
            text = path.read_text("utf-8")
            for regex, ok, expected in patterns:
                for match in regex.finditer(text):
                    if not ok(match):
                        findings.append(
                            f"{rel}: {match.group(0).strip()!r} is stale; "
                            f"the model says {expected()!r}"
                        )
        summary = (f'{live["parts"]} parts, {live["placeholders"]} of {live["controls"]} '
                   f'controls are placeholders')

    else:  # pragma: no cover
        raise ValueError(f"unknown rule {rule!r}")

    return _rule_result(test, suite, findings, summary)


# ------------------------------------------------------------------------ runner

NUMERIC_KINDS = {"control", "station", "elevation", "measure", "expression", "ho_conversion"}
RULE_KINDS = {"metadata", "traceability"}


def run_suite(path: Path, ctx: Context) -> tuple[dict[str, Any], list[Result]]:
    doc = json.loads(path.read_text("utf-8"))
    suite = doc["suite"]
    results: list[Result] = []
    for test in doc["tests"]:
        try:
            if test["kind"] in NUMERIC_KINDS:
                results.append(run_numeric(test, ctx, suite))
            elif test["kind"] in RULE_KINDS:
                results.append(run_rule(test, ctx, suite))
            else:
                raise ValueError(f"unknown test kind {test['kind']!r}")
        except Exception as exc:  # noqa: BLE001 - a broken test must not hide the others
            results.append(
                Result(
                    test_id=test.get("id", "<unknown>"),
                    title=test.get("title", ""),
                    suite=suite,
                    mode=test.get("mode", "assert"),
                    status="error",
                    detail=f"{type(exc).__name__}: {exc}",
                )
            )
    return doc, results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the control skeleton against the test suites.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--suite",
        choices=["all", "geometry", "traceability"],
        default="all",
    )
    parser.add_argument("--json", action="store_true", help="print the machine-readable report only")
    args = parser.parse_args(argv)

    root: Path = args.repo_root
    suite_files: list[Path] = []
    if args.suite in ("all", "geometry"):
        suite_files.append(root / "tests" / "geometry_regression_tests.json")
    if args.suite in ("all", "traceability"):
        suite_files.append(root / "tests" / "source_traceability_tests.json")

    ctx = Context(root)
    all_results: list[Result] = []
    for path in suite_files:
        _, results = run_suite(path, ctx)
        all_results.extend(results)

    failures = [r for r in all_results if r.status in ("fail", "error")]
    counts = {
        "pass": sum(1 for r in all_results if r.status == "pass"),
        "reported": sum(1 for r in all_results if r.status == "reported"),
        "fail": sum(1 for r in all_results if r.status == "fail"),
        "error": sum(1 for r in all_results if r.status == "error"),
    }
    report = {
        "schema_version": "1.0",
        "control_document_sha256": ctx.model.document_sha256,
        "built_from_sha256": ctx.parts_doc["control_document"]["sha256"],
        "generated_by_build": ctx.parts_doc["generated_by"],
        "summary": counts,
        "results": [r.to_json() for r in all_results],
    }
    report_path = root / "tests" / "validation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        symbols = {"pass": "PASS", "fail": "FAIL", "error": "ERR ", "reported": "RPT "}
        for r in all_results:
            print(f"{symbols[r.status]} {r.test_id}  {r.title}")
            print(f"       {r.detail}")
            for finding in r.findings:
                print(f"         - {finding}")
        print()
        print(
            f"{counts['pass']} passed, {counts['reported']} reported, "
            f"{counts['fail']} failed, {counts['error']} errored"
        )
        print(f"report -> {report_path.relative_to(root)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
