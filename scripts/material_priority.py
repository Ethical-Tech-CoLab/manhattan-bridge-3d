"""Rank material rows by how much model confidence each one is holding back.

Answers "what should we push on to get better material design?" with a computed number rather
than an opinion, and recomputes it on every run so it cannot go stale the way three hand-typed
counts already have (see STT-013).

The method, and why it is not just "count the D materials":

Every part carries two independent grades -- `basis_confidence`, how well its *shape and position*
are sourced, and `material_confidence`, how well its *fabric* is sourced. The part's own grade is
the weaker of the two. So a material row only costs the model anything where it is **strictly worse
than the basis it sits on**. A grade-D material on grade-D geometry is not the bottleneck; the
geometry is. A grade-D material on grade-A geometry is throwing away sourced work.

That distinction is the whole point. Counting placeholders by grade would put the approaches near
the top because there are sixteen of them; counting *binding* placeholders puts the stiffening
trusses there instead, because their geometry is already good and only the fabric is missing.

    python scripts/material_priority.py
    python scripts/material_priority.py --json
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTS = REPO_ROOT / "viewer" / "public" / "parts.json"

ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}

# `reference` is not a material. It marks datum planes, axes and station markers -- construction
# geometry that is never rendered as fabric. Those rows sit at grade D because the grade vocabulary
# has no "not applicable", which means they can never be promoted by any amount of research and
# would otherwise sit permanently at the top of a priority list they can never leave. Excluded, and
# counted separately so the exclusion is visible rather than silent.
NON_MATERIAL = "reference"


def load_parts() -> list[dict]:
    if not PARTS.exists():
        print("no %s -- run build_control_skeleton.py first" % PARTS.relative_to(REPO_ROOT))
        raise SystemExit(1)
    return json.loads(PARTS.read_text(encoding="utf-8"))["parts"]


def rank(parts: list[dict]) -> tuple[list[dict], dict]:
    physical = [p for p in parts if p.get("material") != NON_MATERIAL]
    excluded = len(parts) - len(physical)

    rows: dict[str, dict] = collections.defaultdict(
        lambda: {"parts": 0, "binding": 0, "steps": 0, "material": "", "grade": "", "examples": []}
    )
    for part in physical:
        basis = part["basis_confidence"]
        mat = part["material_confidence"]
        row = rows[part.get("material_id") or "(unassigned)"]
        row["parts"] += 1
        row["material"] = part.get("material", "")
        row["grade"] = mat
        if ORDER[mat] > ORDER[basis]:
            row["binding"] += 1
            row["steps"] += ORDER[mat] - ORDER[basis]
            if len(row["examples"]) < 3:
                row["examples"].append(part["part_id"])

    ranked = [
        dict(material_id=k, **v)
        for k, v in sorted(rows.items(), key=lambda kv: (-kv[1]["steps"], -kv[1]["binding"]))
        if v["steps"] > 0
    ]
    totals = {
        "physical_parts": len(physical),
        "reference_parts_excluded": excluded,
        "parts_bound_by_material": sum(r["binding"] for r in ranked),
        "recoverable_grade_steps": sum(r["steps"] for r in ranked),
    }
    return ranked, totals


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()

    ranked, totals = rank(load_parts())

    if args.json:
        print(json.dumps({"ranking": ranked, "totals": totals}, indent=2))
        return 0

    print("Material rows ranked by the confidence they are holding back")
    print()
    print("  %-9s %-5s %-17s %6s %8s %7s" % ("row", "grade", "material", "parts", "binding", "steps"))
    print("  " + "-" * 60)
    for r in ranked:
        print("  %-9s %-5s %-17s %6d %8d %7d"
              % (r["material_id"], r["grade"], r["material"][:17], r["parts"], r["binding"], r["steps"]))
    print("  " + "-" * 60)
    print("  %d of %d physical parts have MATERIAL as the binding constraint"
          % (totals["parts_bound_by_material"], totals["physical_parts"]))
    print("  %d grade-steps are recoverable by sourcing fabric alone"
          % totals["recoverable_grade_steps"])
    print("  %d reference parts excluded: a datum plane has no fabric"
          % totals["reference_parts_excluded"])
    print()
    print("  'binding' counts parts whose material is strictly worse than their own geometry,")
    print("  i.e. where sourced shape is being wasted for want of a sourced surface.")
    print("  A photograph settles material -- see CONFIDENCE-MODEL.md sections 6.2 and 6.4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
