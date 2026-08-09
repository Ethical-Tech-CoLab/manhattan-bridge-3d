"""Unit normalisation for the Manhattan Bridge digital twin.

Authoring units are meters (GEOMETRY-CONTROL.md section 1). Every control value declared in
GEOMETRY-CONTROL.md is converted to meters through this module so that there is exactly one
conversion implementation in the repository.

HO reporting scale is 1:87.1 (SCALE-HO.md).

Run directly to print the HO conversion table derived from GEOMETRY-CONTROL.md::

    python scripts/normalize_units.py
"""

from __future__ import annotations

from typing import Any

HO_SCALE_DENOMINATOR = 87.1

FT_TO_M = 0.3048
IN_TO_M = 0.0254
MM_TO_M = 0.001

LINEAR_UNITS = {
    "ft": FT_TO_M,
    "in": IN_TO_M,
    "m": 1.0,
    "mm": MM_TO_M,
}

DIMENSIONLESS_UNITS = {"count", "ratio"}

ALLOWED_UNITS = set(LINEAR_UNITS) | DIMENSIONLESS_UNITS


class UnitError(ValueError):
    """Raised when a control row declares a unit this project does not accept."""


def is_linear(unit: str) -> bool:
    return unit in LINEAR_UNITS


def to_meters(value: float, unit: str) -> float:
    """Convert a linear control value to meters. Dimensionless units pass through unchanged."""
    if unit in DIMENSIONLESS_UNITS:
        return float(value)
    try:
        return float(value) * LINEAR_UNITS[unit]
    except KeyError as exc:
        raise UnitError(f"unsupported unit {unit!r}; allowed: {sorted(ALLOWED_UNITS)}") from exc


def meters_to_feet(value_m: float) -> float:
    return value_m / FT_TO_M


def meters_to_inches(value_m: float) -> float:
    return value_m / IN_TO_M


def ho_meters(prototype_m: float) -> float:
    return prototype_m / HO_SCALE_DENOMINATOR


def ho_millimeters(prototype_m: float) -> float:
    return ho_meters(prototype_m) * 1000.0


def ho_inches(prototype_m: float) -> float:
    return meters_to_inches(ho_meters(prototype_m))


def ho_feet(prototype_m: float) -> float:
    return meters_to_feet(ho_meters(prototype_m))


def ho_report(prototype_m: float) -> dict[str, float]:
    """Full HO reporting block for a prototype length in meters.

    Rounding follows SCALE-HO.md section 4: report-time only, never in the authoring data.
    """
    inches = ho_inches(prototype_m)
    mm = ho_millimeters(prototype_m)
    return {
        "prototype_m": round(prototype_m, 6),
        "prototype_ft": round(meters_to_feet(prototype_m), 4),
        "prototype_in": round(meters_to_inches(prototype_m), 4),
        "ho_mm": round(mm, 2 if abs(mm) < 10.0 else 1),
        "ho_in": round(inches, 3 if abs(inches) < 1.0 else 2),
        "ho_ft": round(ho_feet(prototype_m), 2),
    }


def _main() -> int:  # pragma: no cover - CLI convenience
    from pathlib import Path

    from control_model import load_control_model

    repo = Path(__file__).resolve().parents[1]
    model = load_control_model(repo / "GEOMETRY-CONTROL.md")
    header = f"{'Control':<9} {'Key':<42} {'Prototype (m)':>14} {'HO (mm)':>11} {'HO (in)':>9}"
    print(header)
    print("-" * len(header))
    for control in model.controls.values():
        if not is_linear(control.unit):
            continue
        rep = ho_report(control.value_m)
        print(
            f"{control.control_id:<9} {control.key:<42} {rep['prototype_m']:>14.4f} "
            f"{rep['ho_mm']:>11.1f} {rep['ho_in']:>9.3f}"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    raise SystemExit(_main())
