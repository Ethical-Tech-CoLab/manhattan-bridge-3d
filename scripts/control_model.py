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

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from normalize_units import ALLOWED_UNITS, to_meters

CONTROL_ID_RE = re.compile(r"^CTL-\d+$")
CONFIDENCE_GRADES = ("A", "B", "C", "D")
EXPECTED_COLUMNS = 7


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


@dataclass
class ControlModel:
    document_path: Path
    document_sha256: str
    controls: dict[str, Control] = field(default_factory=dict)
    by_id: dict[str, Control] = field(default_factory=dict)

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
        if not cells or not CONTROL_ID_RE.match(cells[0]):
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
