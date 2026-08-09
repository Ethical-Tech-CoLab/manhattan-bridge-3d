"""Parser for GEOMETRY-CONTROL.md.

GEOMETRY-CONTROL.md is the single source of truth for every dimension in this repository. Scripts do
not carry their own copies of any number; they read the control tables from that document through
this module.

Column contract for a control row (see GEOMETRY-CONTROL.md sections 2 and 3)::

    | Control ID | Key | Value | Unit | Source IDs | Confidence | Notes |

Any markdown table row whose first cell matches ``CTL-<digits>`` is treated as a control row,
regardless of which table or section it lives in. Rows in the placeholder table are identified by
their confidence grade of ``D`` and are exposed as ``Control.is_placeholder``.
"""

from __future__ import annotations

import fnmatch
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from normalize_units import ALLOWED_UNITS, to_meters

CONTROL_ID_RE = re.compile(r"^CTL-\d+$")
MATERIAL_ID_RE = re.compile(r"^MAT-\d+$")
CONFIDENCE_GRADES = ("A", "B", "C", "D")
EXPECTED_COLUMNS = 7
MATERIAL_COLUMNS = 6

# Closed vocabulary. A renderer maps these to an appearance; anything outside the set would mean the
# control document and the viewer had silently drifted apart, so parsing rejects it.
ALLOWED_MATERIALS = (
    "masonry",
    "concrete",
    "steel_structural",
    "steel_wire",
    "roadway_surface",
    "reference",
)


class ControlDocumentError(ValueError):
    """Raised when GEOMETRY-CONTROL.md cannot be parsed or fails its internal contract."""


@dataclass(frozen=True)
class Control:
    control_id: str
    key: str
    value: float
    unit: str
    source_ids: tuple[str, ...]
    confidence: str
    notes: str
    value_m: float

    @property
    def is_placeholder(self) -> bool:
        return self.confidence == "D"


@dataclass(frozen=True)
class MaterialRule:
    """One row of the material table in GEOMETRY-CONTROL.md section 7.

    Order matters: the rules are matched in document order and the first glob that matches a
    part_id wins, so the table runs from most specific to least.
    """

    material_id: str
    pattern: str
    material: str
    source_ids: tuple[str, ...]
    confidence: str
    notes: str

    @property
    def is_placeholder(self) -> bool:
        return self.confidence == "D"


@dataclass
class ControlModel:
    document_path: Path
    document_sha256: str
    controls: dict[str, Control] = field(default_factory=dict)
    by_id: dict[str, Control] = field(default_factory=dict)
    materials: list[MaterialRule] = field(default_factory=list)

    def material_for(self, part_id: str) -> MaterialRule:
        """The first material rule whose glob matches, or a hard failure.

        There is no default. A part with no matching rule means the control document does not
        describe how it should look, and silently painting it grey would be exactly the kind of
        unsourced claim this project exists to prevent.
        """
        for rule in self.materials:
            if fnmatch.fnmatchcase(part_id, rule.pattern):
                return rule
        raise ControlDocumentError(
            f"no material rule in GEOMETRY-CONTROL.md section 7 matches part {part_id!r}; "
            "add a row rather than letting the renderer choose"
        )

    def get(self, key: str) -> Control:
        try:
            return self.controls[key]
        except KeyError as exc:
            raise ControlDocumentError(
                f"control key {key!r} is not declared in {self.document_path.name}; "
                "add it to a control table instead of hard-coding a value"
            ) from exc

    def m(self, key: str) -> float:
        """Control value in meters."""
        return self.get(key).value_m

    def raw(self, key: str) -> float:
        """Control value in its declared unit."""
        return self.get(key).value

    def id_of(self, key: str) -> str:
        return self.get(key).control_id

    def ids_of(self, *keys: str) -> list[str]:
        return [self.id_of(k) for k in keys]

    def require(self, *keys: str) -> None:
        missing = [k for k in keys if k not in self.controls]
        if missing:
            raise ControlDocumentError(
                f"{self.document_path.name} is missing required control keys: {', '.join(sorted(missing))}"
            )

    @property
    def placeholders(self) -> list[Control]:
        return [c for c in self.controls.values() if c.is_placeholder]


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _parse_source_ids(cell: str) -> tuple[str, ...]:
    cleaned = cell.strip()
    if not cleaned or cleaned.lower() in {"none", "n/a", "-"}:
        return ()
    return tuple(part.strip() for part in cleaned.split(",") if part.strip())


def _parse_material_row(model, path: Path, line_no: int, cells: list[str]) -> None:
    """Parse one MAT- row, applying the same source/confidence contract as a dimension.

    A material is not a dimension, but an unsourced material is still an unsourced claim about the
    bridge, so it is graded identically: only confidence D may be sourceless, and D may not cite
    sources.
    """
    if len(cells) != MATERIAL_COLUMNS:
        raise ControlDocumentError(
            f"{path.name}:{line_no}: material row {cells[0]} has {len(cells)} columns, "
            f"expected {MATERIAL_COLUMNS}"
        )
    material_id, pattern, material, sources, confidence, notes = cells

    pattern = pattern.strip().strip("`")
    if not pattern:
        raise ControlDocumentError(
            f"{path.name}:{line_no}: material {material_id} declares an empty applies_to pattern"
        )
    if material not in ALLOWED_MATERIALS:
        raise ControlDocumentError(
            f"{path.name}:{line_no}: material {material_id} declares {material!r}, which is not in "
            f"the closed vocabulary {ALLOWED_MATERIALS}"
        )
    if confidence not in CONFIDENCE_GRADES:
        raise ControlDocumentError(
            f"{path.name}:{line_no}: material {material_id} declares invalid confidence {confidence!r}"
        )

    source_ids = _parse_source_ids(sources)
    if confidence != "D" and not source_ids:
        raise ControlDocumentError(
            f"{path.name}:{line_no}: material {material_id} is graded {confidence} but cites no "
            "source; only confidence D rows may be sourceless"
        )
    if confidence == "D" and source_ids:
        raise ControlDocumentError(
            f"{path.name}:{line_no}: material {material_id} is a placeholder (D) but cites sources "
            f"{source_ids}; a placeholder must not appear to rest on evidence"
        )

    model.materials.append(
        MaterialRule(
            material_id=material_id,
            pattern=pattern,
            material=material,
            source_ids=source_ids,
            confidence=confidence,
            notes=notes,
        )
    )


def load_control_model(path: str | Path) -> ControlModel:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    model = ControlModel(
        document_path=path,
        document_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )

    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_row(stripped)
        if not cells:
            continue
        if MATERIAL_ID_RE.match(cells[0]):
            _parse_material_row(model, path, line_no, cells)
            continue
        if not CONTROL_ID_RE.match(cells[0]):
            continue
        if len(cells) != EXPECTED_COLUMNS:
            raise ControlDocumentError(
                f"{path.name}:{line_no}: control row {cells[0]} has {len(cells)} columns, "
                f"expected {EXPECTED_COLUMNS}"
            )

        control_id, key, raw_value, unit, sources, confidence, notes = cells

        if unit not in ALLOWED_UNITS:
            raise ControlDocumentError(
                f"{path.name}:{line_no}: control {control_id} declares unsupported unit {unit!r}"
            )
        if confidence not in CONFIDENCE_GRADES:
            raise ControlDocumentError(
                f"{path.name}:{line_no}: control {control_id} declares invalid confidence {confidence!r}"
            )
        try:
            value = float(raw_value)
        except ValueError as exc:
            raise ControlDocumentError(
                f"{path.name}:{line_no}: control {control_id} value {raw_value!r} is not a bare "
                "decimal number (thousands separators are not allowed)"
            ) from exc

        source_ids = _parse_source_ids(sources)
        if confidence != "D" and not source_ids:
            raise ControlDocumentError(
                f"{path.name}:{line_no}: control {control_id} is graded {confidence} but cites no source; "
                "only confidence D rows may be sourceless"
            )
        if confidence == "D" and source_ids:
            raise ControlDocumentError(
                f"{path.name}:{line_no}: control {control_id} is a placeholder (D) but cites sources "
                f"{source_ids}; promote it out of the placeholder table instead"
            )

        control = Control(
            control_id=control_id,
            key=key,
            value=value,
            unit=unit,
            source_ids=source_ids,
            confidence=confidence,
            notes=notes,
            value_m=to_meters(value, unit),
        )

        if key in model.controls:
            raise ControlDocumentError(f"{path.name}:{line_no}: duplicate control key {key!r}")
        if control_id in model.by_id:
            raise ControlDocumentError(f"{path.name}:{line_no}: duplicate control ID {control_id!r}")
        model.controls[key] = control
        model.by_id[control_id] = control

    if not model.controls:
        raise ControlDocumentError(f"{path.name}: no control rows found")
    return model


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    repo_root = Path(__file__).resolve().parents[1]
    m = load_control_model(repo_root / "GEOMETRY-CONTROL.md")
    sourced = len(m.controls) - len(m.placeholders)
    print(f"{m.document_path.name}  sha256={m.document_sha256[:12]}")
    print(f"  controls        : {len(m.controls)}")
    print(f"  sourced (A/B/C) : {sourced}")
    print(f"  placeholders (D): {len(m.placeholders)}")
