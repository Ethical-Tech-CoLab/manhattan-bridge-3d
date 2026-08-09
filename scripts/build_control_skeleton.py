"""Build the Manhattan Bridge control skeleton (Milestone 1).

Reads every dimension from GEOMETRY-CONTROL.md, derives the reference stations and elevations
declared in that document's section 4, emits the control skeleton as glTF/GLB, and writes the
part metadata that the browser viewer consumes.

    python scripts/build_control_skeleton.py

Outputs
-------
    mesh/glb/control_skeleton.glb            authoritative skeleton, prototype meters
    mesh/glb/control_skeleton.gltf + .bin     human-readable review copy
    mesh/glb/control_skeleton_ho.glb          uniformly scaled HO copy, 1:87.1
    cad/procedural/control_skeleton_geometry.json  tool-neutral procedural definition
    viewer/metadata/parts.json                part metadata + taxonomy + stations
    viewer/metadata/scale_ho.json             HO reporting table
    viewer/metadata/build_report.json         derived values and measures for regression tests
    viewer/public/*                           copies consumed by the dev viewer

Non-goals for Milestone 1: no marketplace meshes, no photogrammetry, no invented dimensions.
Anything not backed by a registered source is emitted as confidence D and names the open question
that would retire it.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from control_model import ControlDocumentError, ControlModel, load_control_model  # noqa: E402
from export_gltf import (  # noqa: E402
    GltfBuilder,
    box_mesh_data,
    prism_mesh_data,
    quad_mesh_data,
    tube_mesh_data,
)
from normalize_units import HO_SCALE_DENOMINATOR, ho_report, is_linear  # noqa: E402

SCRIPT_VERSION = "1.0.0"
AGENT_ID = f"build_control_skeleton.py@{SCRIPT_VERSION}"
REPO_ROOT = SCRIPT_DIR.parent

CONFIDENCE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}
CONFIDENCE_COLORS = {"A": "#2e9e4f", "B": "#3b7dd8", "C": "#d89a3b", "D": "#c4453c"}

ALLOWED_SOURCE_BASIS = {
    "drawing",
    "official_facts",
    "photo",
    "mesh_reference",
    "photogrammetry",
    "control_dimension",
    "inferred",
}

# Presentation only. Colours carry no dimensional or confidence meaning; the viewer's confidence
# overlay recolours everything from CONFIDENCE_COLORS.
STYLES: dict[str, dict[str, Any]] = {
    "datum": {"color": (0.36, 0.45, 0.55, 0.10), "unlit": False},
    "reference_line": {"color": (0.62, 0.68, 0.76, 1.0), "unlit": True},
    "station_line": {"color": (0.95, 0.95, 0.95, 1.0), "unlit": True},
    "tower_line": {"color": (0.98, 0.62, 0.30, 1.0), "unlit": True},
    "tower_solid": {"color": (0.74, 0.71, 0.66, 0.30), "unlit": False},
    "tower_steel": {"color": (0.80, 0.78, 0.74, 1.0), "unlit": False},
    "truss_member": {"color": (0.72, 0.76, 0.80, 1.0), "unlit": True},
    "truss_web": {"color": (0.58, 0.66, 0.72, 1.0), "unlit": True},
    "anchorage_solid": {"color": (0.68, 0.63, 0.56, 0.38), "unlit": False},
    "cable_line": {"color": (0.98, 0.78, 0.24, 1.0), "unlit": True},
    "cable_solid": {"color": (0.86, 0.70, 0.32, 1.0), "unlit": False},
    "suspender_line": {"color": (0.80, 0.64, 0.30, 1.0), "unlit": True},
    "deck_solid": {"color": (0.42, 0.62, 0.82, 0.34), "unlit": False},
    "truss_panel": {"color": (0.55, 0.75, 0.72, 0.28), "unlit": False},
    "track_solid": {"color": (0.88, 0.40, 0.42, 0.55), "unlit": False},
    "approach_solid": {"color": (0.50, 0.55, 0.60, 0.26), "unlit": False},
}

Point = tuple[float, float, float]


# --------------------------------------------------------------------------- parts


@dataclass
class Part:
    part_id: str
    system: str
    source_basis: list[str]
    basis_confidence: str
    control_refs: list[str]
    notes: str
    geometry: list[dict[str, Any]]
    style: str
    subsystem: str | None = None
    open_questions: list[str] = field(default_factory=list)
    confidence: str = ""

    def resolve_confidence(self, model: ControlModel) -> None:
        """Weakest-link rule from CONFIDENCE-MODEL.md section 1."""
        worst = self.basis_confidence
        for ref in self.control_refs:
            control = model.by_id.get(ref)
            if control is None:
                raise ControlDocumentError(
                    f"part {self.part_id} references unknown control {ref}"
                )
            if CONFIDENCE_ORDER[control.confidence] > CONFIDENCE_ORDER[worst]:
                worst = control.confidence
        self.confidence = worst

    def points(self) -> Iterable[Point]:
        for prim in self.geometry:
            kind = prim["kind"]
            if kind == "box":
                yield tuple(prim["min"])
                yield tuple(prim["max"])
            elif kind == "quad":
                yield from (tuple(c) for c in prim["corners"])
            elif kind == "prism":
                yield from (tuple(c) for c in prim["bottom"])
                yield from (tuple(c) for c in prim["top"])
            elif kind == "tube":
                r = prim["radius"]
                for p in prim["points"]:
                    yield (p[0] - r, p[1] - r, p[2] - r)
                    yield (p[0] + r, p[1] + r, p[2] + r)
            elif kind == "polyline":
                yield from (tuple(p) for p in prim["points"])
            elif kind == "lines":
                for a, b in prim["segments"]:
                    yield tuple(a)
                    yield tuple(b)
            else:  # pragma: no cover - guarded by builders
                raise ValueError(f"unknown geometry kind {kind!r}")

    def bbox(self) -> dict[str, list[float]]:
        pts = list(self.points())
        return {
            "min": [min(p[i] for p in pts) for i in range(3)],
            "max": [max(p[i] for p in pts) for i in range(3)],
        }

    def metadata(self) -> dict[str, Any]:
        bbox = self.bbox()
        size = [round(bbox["max"][i] - bbox["min"][i], 6) for i in range(3)]
        return {
            "part_id": self.part_id,
            "system": self.system,
            "subsystem": self.subsystem,
            "source_basis": list(self.source_basis),
            "confidence": self.confidence,
            "prototype_units": "meters",
            "ho_scale_units": "millimeters",
            "notes": self.notes,
            "scale": f"1:1 prototype, HO 1:{HO_SCALE_DENOMINATOR}",
            "last_modified_by_agent": AGENT_ID,
            "review_status": "unreviewed",
            "control_refs": list(self.control_refs),
            "open_questions": list(self.open_questions),
            "basis_confidence": self.basis_confidence,
            "geometry_kinds": sorted({prim["kind"] for prim in self.geometry}),
            "bbox_prototype_m": {
                "min": [round(v, 6) for v in bbox["min"]],
                "max": [round(v, 6) for v in bbox["max"]],
                "size": size,
            },
            "bbox_ho_mm": {
                "size": [round(v / HO_SCALE_DENOMINATOR * 1000.0, 2) for v in size],
            },
        }


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


# ------------------------------------------------------------------ geometry prims


def box(bmin: Sequence[float], bmax: Sequence[float]) -> dict[str, Any]:
    return {"kind": "box", "min": [float(v) for v in bmin], "max": [float(v) for v in bmax]}


def quad(corners: Sequence[Point]) -> dict[str, Any]:
    return {"kind": "quad", "corners": [list(map(float, c)) for c in corners]}


def polyline(points: Sequence[Point]) -> dict[str, Any]:
    return {"kind": "polyline", "points": [list(map(float, p)) for p in points]}


def prism(bottom: Sequence[Point], top: Sequence[Point]) -> dict[str, Any]:
    """Solid between two four-corner rings, used for tapered tower legs."""
    return {
        "kind": "prism",
        "bottom": [list(map(float, p)) for p in bottom],
        "top": [list(map(float, p)) for p in top],
    }


def tube(points: Sequence[Point], radius: float) -> dict[str, Any]:
    """Swept tube of sourced radius, used where real thickness is known."""
    return {"kind": "tube", "points": [list(map(float, p)) for p in points], "radius": float(radius)}


def lines(segments: Sequence[tuple[Point, Point]]) -> dict[str, Any]:
    return {"kind": "lines", "segments": [[list(map(float, a)), list(map(float, b))] for a, b in segments]}


# ----------------------------------------------------------------- control geometry


@dataclass
class Skeleton:
    """Everything derived from the control document, per GEOMETRY-CONTROL.md section 4."""

    model: ControlModel
    stations: dict[str, dict[str, Any]] = field(default_factory=dict)
    elevations: dict[str, dict[str, Any]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def x(self, station_id: str) -> float:
        return self.stations[station_id]["x_m"]

    def z(self, elevation_id: str) -> float:
        return self.elevations[elevation_id]["z_m"]


REQUIRED_CONTROL_KEYS = (
    "total_bridge_and_approaches_length",
    "lower_level_abutment_to_abutment",
    "upper_roadway_portal_to_portal",
    "anchorage_to_anchorage_suspended_length",
    "main_span",
    "side_span_each",
    "center_clearance_above_mhw",
    "stiffening_truss_depth_asce",
    "main_cable_length",
    "main_cable_count",
    "subway_track_count",
    "subway_track_gauge",
    "cable_saddle_elevation",
    "tower_caisson_height",
    "tower_caisson_extent_x",
    "tower_caisson_extent_y",
    "tower_pier_footing_below_mhw",
    "deck_overall_width",
    "truss_offset_inner",
    "truss_offset_outer",
    "lower_roadway_width",
    "footwalk_width",
    "upper_roadway_east_width",
    "upper_roadway_west_width",
    "tower_pier_extent_x",
    "tower_pier_extent_y",
    "tower_pier_top_above_mhw",
    "tower_foundation_depth_below_mhw",
    "tower_pedestal_extent_x",
    "tower_pedestal_extent_y",
    "tower_leg_width_transverse",
    "tower_leg_length_at_base",
    "tower_leg_length_at_top",
    "tower_leg_count",
    "anchorage_extent_x",
    "anchorage_extent_y",
    "anchorage_extent_z",
    "suspender_panel_points_total",
    "manhattan_approach_and_plaza_length",
    "brooklyn_approach_and_plaza_length",
    "min_suspender_length_at_midspan",
    "cable_saddle_drop_below_cable_top",
    "upper_deck_structure_depth",
    "lower_deck_offset_above_clearance",
    "subway_track_bay_inner_offset",
    "subway_track_spacing_y",
    "subway_track_structure_depth",
)


def derive_skeleton(model: ControlModel) -> Skeleton:
    model.require(*REQUIRED_CONTROL_KEYS)
    sk = Skeleton(model=model)

    main_span = model.m("main_span")
    side_span = model.m("side_span_each")
    suspended = model.m("anchorage_to_anchorage_suspended_length")

    identity_error = abs(main_span + 2.0 * side_span - suspended)
    if identity_error > 1e-6:
        raise ControlDocumentError(
            "control identity failed: main_span + 2 * side_span_each != "
            f"anchorage_to_anchorage_suspended_length (off by {identity_error:.6f} m)"
        )
    sk.notes.append(
        "Control identity verified: main_span + 2 x side_span_each == "
        "anchorage_to_anchorage_suspended_length."
    )

    half_main = main_span / 2.0
    anchor_x = half_main + side_span
    approach_total = model.m("total_bridge_and_approaches_length") - suspended
    if approach_total < 0:
        raise ControlDocumentError("total bridge length is shorter than the suspended length")
    # Approach split is now a sourced ratio (CTL-039 / CTL-040), not a 50/50 guess.
    manhattan_quoted = model.m("manhattan_approach_and_plaza_length")
    brooklyn_quoted = model.m("brooklyn_approach_and_plaza_length")
    manhattan_fraction = manhattan_quoted / (manhattan_quoted + brooklyn_quoted)
    sk.notes.append(
        f"Approach length split derived from CTL-039/CTL-040 as {manhattan_fraction:.4f} "
        "(Manhattan side), replacing the Milestone 1 placeholder of 0.5."
    )

    def station(
        station_id: str, name: str, x_m: float, confidence: str, refs: list[str], notes: str
    ) -> None:
        sk.stations[station_id] = {
            "station_id": station_id,
            "name": name,
            "x_m": x_m,
            "confidence": confidence,
            "control_refs": refs,
            "notes": notes,
            "ho": ho_report(abs(x_m)),
        }

    a_span_refs = model.ids_of("main_span", "side_span_each")
    station("STA-MID", "Main span midpoint (origin)", 0.0, "A", model.ids_of("main_span"), "Model origin.")
    station("STA-TWR-M", "Manhattan tower centerline", -half_main, "A", model.ids_of("main_span"), "")
    station("STA-TWR-B", "Brooklyn tower centerline", half_main, "A", model.ids_of("main_span"), "")
    station("STA-ANC-M", "Manhattan anchorage cable point", -anchor_x, "A", a_span_refs, "")
    station("STA-ANC-B", "Brooklyn anchorage cable point", anchor_x, "A", a_span_refs, "")

    abut_half = model.m("lower_level_abutment_to_abutment") / 2.0
    portal_half = model.m("upper_roadway_portal_to_portal") / 2.0
    sym_note = "Symmetric placement about the main span midpoint is an assumption, see OQ-002."
    station(
        "STA-ABUT-M", "Manhattan lower-level abutment", -abut_half, "D",
        model.ids_of("lower_level_abutment_to_abutment"), sym_note,
    )
    station(
        "STA-ABUT-B", "Brooklyn lower-level abutment", abut_half, "D",
        model.ids_of("lower_level_abutment_to_abutment"), sym_note,
    )
    station(
        "STA-PORTAL-M", "Manhattan upper roadway portal", -portal_half, "D",
        model.ids_of("upper_roadway_portal_to_portal"), sym_note,
    )
    station(
        "STA-PORTAL-B", "Brooklyn upper roadway portal", portal_half, "D",
        model.ids_of("upper_roadway_portal_to_portal"), sym_note,
    )

    appr_refs = model.ids_of(
        "total_bridge_and_approaches_length",
        "anchorage_to_anchorage_suspended_length",
        "manhattan_approach_and_plaza_length",
        "brooklyn_approach_and_plaza_length",
    )
    appr_note = (
        "Approach split derived from the quoted approach-and-plaza lengths, see OQ-006. "
        "The quoted lengths include plazas, so only their ratio is used."
    )
    station(
        "STA-APPR-END-M", "Manhattan approach end",
        -(anchor_x + approach_total * manhattan_fraction), "B", appr_refs, appr_note,
    )
    station(
        "STA-APPR-END-B", "Brooklyn approach end",
        anchor_x + approach_total * (1.0 - manhattan_fraction), "B", appr_refs, appr_note,
    )

    def elevation(
        elev_id: str, name: str, z_m: float, confidence: str, refs: list[str], notes: str
    ) -> None:
        sk.elevations[elev_id] = {
            "elevation_id": elev_id,
            "name": name,
            "z_m": z_m,
            "confidence": confidence,
            "control_refs": refs,
            "notes": notes,
            "ho": ho_report(z_m),
        }

    clearance = model.m("center_clearance_above_mhw")
    truss_depth = model.m("stiffening_truss_depth_asce")

    elevation(
        "ELV-FOUNDATION", "Underside of tower caisson", -model.m("tower_foundation_depth_below_mhw"),
        "A", model.ids_of("tower_foundation_depth_below_mhw"),
        "92 ft below mean high water (SRC-015, direct). Retires OQ-003.",
    )
    elevation("ELV-DATUM", "Mean high water datum", 0.0, "A", [], "Vertical datum, z = 0.")
    elevation(
        "ELV-CAISSON-TOP", "Top of tower caisson",
        -model.m("tower_foundation_depth_below_mhw") + model.m("tower_caisson_height"), "A",
        model.ids_of("tower_foundation_depth_below_mhw", "tower_caisson_height"),
        "Top of the New York caisson (SRC-016). See CONF-013.",
    )
    elevation(
        "ELV-PIER-FOOTING", "Masonry pier footing seat",
        -model.m("tower_pier_footing_below_mhw"), "A",
        model.ids_of("tower_pier_footing_below_mhw"),
        "Concrete footing on which the masonry pier is seated (SRC-016).",
    )
    elevation(
        "ELV-PIER-TOP", "Top of masonry pier", model.m("tower_pier_top_above_mhw"), "A",
        model.ids_of("tower_pier_top_above_mhw"),
        "Pier capstone, base of the steel tower. Stated explicitly by SRC-016, see CONF-009 and OQ-016.",
    )
    elevation(
        "ELV-CLEARANCE", "Navigation clearance at midspan", clearance, "A",
        model.ids_of("center_clearance_above_mhw"),
        "Design clearance; SRC-014 surveys 134 ft, see CONF-007.",
    )
    elevation(
        "ELV-TRUSS-BOTTOM", "Stiffening truss bottom chord", clearance, "B",
        model.ids_of("center_clearance_above_mhw"), "Bottom chord taken at the clearance plane.",
    )
    elevation(
        "ELV-TRUSS-TOP", "Stiffening truss top chord", clearance + truss_depth, "A",
        model.ids_of("center_clearance_above_mhw", "stiffening_truss_depth_asce"),
        "Both inputs are grade A. CONF-002 is effectively resolved toward 24 ft.",
    )
    elevation(
        "ELV-LOWER-DECK", "Lower roadway running surface",
        clearance + model.m("lower_deck_offset_above_clearance"), "D",
        model.ids_of("center_clearance_above_mhw", "lower_deck_offset_above_clearance"),
        "Placeholder offset above the clearance plane, see OQ-013.",
    )
    elevation(
        "ELV-UPPER-DECK", "Upper roadway running surface",
        clearance + truss_depth + model.m("upper_deck_structure_depth"), "D",
        model.ids_of(
            "center_clearance_above_mhw", "stiffening_truss_depth_asce", "upper_deck_structure_depth"
        ),
        "Placeholder deck structure depth above the top chord, see OQ-013.",
    )
    saddle = model.m("cable_saddle_elevation") - model.m("cable_saddle_drop_below_cable_top")
    elevation(
        "ELV-SADDLE", "Main cable saddle seat", saddle, "A",
        model.ids_of("cable_saddle_elevation", "cable_saddle_drop_below_cable_top"),
        "Stated directly by SRC-015: the fixed saddles carrying the main cables are 322.5 ft above "
        "mean high water. See CONF-005.",
    )
    elevation(
        "ELV-CABLE-MID", "Main cable low point at midspan",
        clearance + truss_depth + model.m("min_suspender_length_at_midspan"), "D",
        model.ids_of(
            "center_clearance_above_mhw", "stiffening_truss_depth_asce",
            "min_suspender_length_at_midspan",
        ),
        "Derived: the cable meets the truss top chord at midspan where suspenders are shortest. "
        "Only the minimum suspender length remains a placeholder, see OQ-001.",
    )
    elevation(
        "ELV-ANCHOR-POINT", "Cable point at the anchorage", model.m("anchorage_extent_z"), "A",
        model.ids_of("anchorage_extent_z"), "Cable enters at the top of the anchorage block.",
    )
    sk.notes.append(
        f"Derived main span sag = {saddle - (clearance + truss_depth + model.m('min_suspender_length_at_midspan')):.4f} m "
        f"(ratio 1/{model.m('main_span') / max(saddle - (clearance + truss_depth + model.m('min_suspender_length_at_midspan')), 1e-9):.2f})."
    )
    return sk


# --------------------------------------------------------------------- cable curves


class CableProfile:
    """Longitudinal main cable profile, per GEOMETRY-CONTROL.md section 4.4."""

    def __init__(self, model: ControlModel, sk: Skeleton) -> None:
        self.half_main = model.m("main_span") / 2.0
        self.side_span = model.m("side_span_each")
        self.saddle_z = sk.z("ELV-SADDLE")
        self.mid_z = sk.z("ELV-CABLE-MID")
        self.anchor_z = sk.z("ELV-ANCHOR-POINT")
        self.sag_main = self.saddle_z - self.mid_z
        if self.sag_main <= 0:
            raise ControlDocumentError(
                "derived main span sag is not positive; the cable midspan elevation is at or above "
                "the saddle, which means the control values are inconsistent"
            )
        # Side span sag scaled from the main span sag by the square of the span ratio, the parabolic
        # relation for equal cable tension under uniform load.
        self.sag_side = self.sag_main * (self.side_span / (2.0 * self.half_main)) ** 2

    def z_at(self, x: float) -> float:
        ax = abs(x)
        if ax <= self.half_main:
            return self.saddle_z - self.sag_main * (1.0 - (ax / self.half_main) ** 2)
        t = min((ax - self.half_main) / self.side_span, 1.0)
        chord = self.saddle_z + (self.anchor_z - self.saddle_z) * t
        return chord - 4.0 * self.sag_side * t * (1.0 - t)

    def polyline_points(self, y: float, main_segments: int = 64, side_segments: int = 32) -> list[Point]:
        xs: list[float] = []
        anchor_x = self.half_main + self.side_span
        for i in range(side_segments + 1):
            xs.append(-anchor_x + (self.side_span * i / side_segments))
        for i in range(1, main_segments):
            xs.append(-self.half_main + (2.0 * self.half_main * i / main_segments))
        for i in range(side_segments + 1):
            xs.append(self.half_main + (self.side_span * i / side_segments))
        return [(x, y, self.z_at(x)) for x in xs]


def derive_suspender_pitch(model: ControlModel) -> tuple[float, dict[str, Any]]:
    """Panel pitch derived from the sourced panel-point count (GEOMETRY-CONTROL.md section 4.4).

    CTL-037 gives the total number of suspender panel points across all cables. Dividing by the
    cable count gives points per cable. The unique integer split of the main and side spans that
    reproduces that count fixes the panel pitch.
    """
    points_per_cable = model.raw("suspender_panel_points_total") / model.raw("main_cable_count")
    main_ft = model.raw("main_span")
    side_ft = model.raw("side_span_each")

    solutions: list[tuple[int, int, float]] = []
    for n_main in range(int(main_ft / 40), int(main_ft / 10) + 1):
        pitch = main_ft / n_main
        n_side_exact = side_ft / pitch
        n_side = round(n_side_exact)
        if n_side <= 0 or abs(n_side_exact - n_side) > 0.06:
            continue
        if n_main + 2 * n_side == round(points_per_cable):
            solutions.append((n_main, n_side, pitch))

    if len(solutions) != 1:
        raise ControlDocumentError(
            f"suspender panel pitch is not uniquely determined: {len(solutions)} integer solutions "
            f"reproduce {points_per_cable:g} panel points per cable"
        )
    n_main, n_side, pitch_ft = solutions[0]
    evidence = {
        "points_per_cable": points_per_cable,
        "main_span_panels": n_main,
        "side_span_panels": n_side,
        "pitch_ft": pitch_ft,
        "pitch_m": pitch_ft * 0.3048,
        "note": (
            "Unique integer solution reproducing CTL-037. Replaces the Milestone 1 placeholder pitch."
        ),
    }
    return pitch_ft * 0.3048, evidence


def polyline_length(points: Sequence[Point]) -> float:
    return sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))


# ------------------------------------------------------------------- part assembly



def build_parts(model: ControlModel, sk: Skeleton) -> list[Part]:
    m = model.m
    ids = model.ids_of
    parts: list[Part] = []

    half_main = m("main_span") / 2.0
    anchor_x = sk.x("STA-ANC-B")
    deck_half_w = m("deck_overall_width") / 2.0
    truss_inner = m("truss_offset_inner")
    truss_outer = m("truss_offset_outer")
    foundation = sk.z("ELV-FOUNDATION")
    pier_top = sk.z("ELV-PIER-TOP")
    saddle_z = sk.z("ELV-SADDLE")
    truss_bottom = sk.z("ELV-TRUSS-BOTTOM")
    truss_top = sk.z("ELV-TRUSS-TOP")
    upper_deck = sk.z("ELV-UPPER-DECK")
    lower_deck = sk.z("ELV-LOWER-DECK")

    # Truss A..D, south to north (SRC-011).
    truss_planes = (
        ("a", -truss_outer, "south outer"),
        ("b", -truss_inner, "south inner"),
        ("c", truss_inner, "north inner"),
        ("d", truss_outer, "north outer"),
    )
    transverse_refs = ids("truss_offset_inner", "truss_offset_outer")

    # ---------------------------------------------------------------- reference
    parts.append(
        Part(
            part_id="reference_datum_mhw_plane",
            system="reference",
            subsystem="datum",
            source_basis=["control_dimension", "official_facts"],
            basis_confidence="A",
            control_refs=ids("main_span", "side_span_each", "deck_overall_width"),
            notes=(
                "Visualisation of the z = 0 mean high water datum, drawn to the sourced 120 ft deck "
                "width (CTL-021). The datum and its extent are both grade A."
            ),
            geometry=[
                quad(
                    [
                        (-anchor_x, -deck_half_w, 0.0),
                        (anchor_x, -deck_half_w, 0.0),
                        (anchor_x, deck_half_w, 0.0),
                        (-anchor_x, deck_half_w, 0.0),
                    ]
                )
            ],
            style="datum",
        )
    )
    parts.append(
        Part(
            part_id="reference_bridge_axis",
            system="reference",
            subsystem="control_curves",
            source_basis=["control_dimension"],
            basis_confidence="A",
            control_refs=ids("main_span", "side_span_each"),
            notes=(
                "Longitudinal bridge axis at the datum, anchorage cable point to anchorage cable point. "
                "Real-world azimuth is unregistered, see OQ-009."
            ),
            geometry=[polyline([(-anchor_x, 0.0, 0.0), (anchor_x, 0.0, 0.0)])],
            style="reference_line",
        )
    )
    parts.append(
        Part(
            part_id="control_curve_deck_centerline",
            system="reference",
            subsystem="control_curves",
            source_basis=["control_dimension", "inferred"],
            basis_confidence="A",
            control_refs=ids(
                "center_clearance_above_mhw",
                "stiffening_truss_depth_asce",
                "upper_deck_structure_depth",
                "total_bridge_and_approaches_length",
                "manhattan_approach_and_plaza_length",
                "brooklyn_approach_and_plaza_length",
            ),
            open_questions=["OQ-002", "OQ-006", "OQ-013"],
            notes=(
                "Deck centerline control curve at the upper roadway elevation. Drawn level over the "
                "full length; approach grades are unregistered and the approach split is a ratio only "
                "(OQ-006)."
            ),
            geometry=[
                polyline(
                    [
                        (sk.x("STA-APPR-END-M"), 0.0, upper_deck),
                        (sk.x("STA-APPR-END-B"), 0.0, upper_deck),
                    ]
                )
            ],
            style="reference_line",
        )
    )

    for station in sk.stations.values():
        x = station["x_m"]
        parts.append(
            Part(
                part_id=f"station_{station['station_id'].lower().replace('-', '_')}",
                system="reference",
                subsystem="stations",
                source_basis=["control_dimension"],
                basis_confidence=station["confidence"],
                control_refs=station["control_refs"],
                open_questions=["OQ-002"] if station["confidence"] == "D" else [],
                notes=f"{station['name']}. {station['notes']}".strip(),
                geometry=[
                    lines(
                        [
                            ((x, 0.0, 0.0), (x, 0.0, saddle_z)),
                            ((x, -truss_outer, 0.0), (x, truss_outer, 0.0)),
                        ]
                    )
                ],
                style="station_line",
            )
        )

    # ------------------------------------------------------------------- towers
    for side, station_id in (("manhattan", "STA-TWR-M"), ("brooklyn", "STA-TWR-B")):
        x = sk.x(station_id)
        parts.append(
            Part(
                part_id=f"tower_{side}_centerline",
                system="towers",
                subsystem="centerlines",
                source_basis=["control_dimension"],
                basis_confidence="A",
                control_refs=ids(
                    "main_span", "cable_saddle_elevation", "tower_foundation_depth_below_mhw"
                ),
                notes=(
                    "Tower centerline from the caisson underside to the cable saddles. Both ends are "
                    "now stated directly by SRC-015, retiring OQ-003."
                ),
                geometry=[polyline([(x, 0.0, foundation), (x, 0.0, saddle_z)])],
                style="tower_line",
            )
        )
        caisson_hx = m("tower_caisson_extent_x") / 2.0
        caisson_hy = m("tower_caisson_extent_y") / 2.0
        parts.append(
            Part(
                part_id=f"tower_{side}_caisson",
                system="towers",
                subsystem="foundations",
                source_basis=["control_dimension"],
                basis_confidence="A",
                control_refs=ids(
                    "main_span", "tower_caisson_extent_x", "tower_caisson_extent_y",
                    "tower_caisson_height", "tower_foundation_depth_below_mhw",
                ),
                notes=(
                    "Timber-and-concrete caisson envelope, 78 by 144 ft in plan and 47.5 ft high, "
                    "with its cutting edge 92 ft below mean high water. All extents from SRC-016 "
                    "directly, the footprint independently confirmed by SRC-015. See CONF-013."
                ),
                geometry=[
                    box(
                        (x - caisson_hx, -caisson_hy, foundation),
                        (x + caisson_hx, caisson_hy, sk.z("ELV-CAISSON-TOP")),
                    )
                ],
                style="tower_solid",
            )
        )
        pier_hx = m("tower_pier_extent_x") / 2.0
        pier_hy = m("tower_pier_extent_y") / 2.0
        parts.append(
            Part(
                part_id=f"tower_{side}_pier",
                system="towers",
                subsystem="foundations",
                source_basis=["control_dimension"],
                basis_confidence="A",
                control_refs=ids(
                    "main_span", "tower_pier_extent_x", "tower_pier_extent_y",
                    "tower_pier_top_above_mhw", "tower_caisson_height",
                    "tower_foundation_depth_below_mhw",
                ),
                open_questions=["OQ-016"],
                notes=(
                    "Masonry pier envelope from the caisson top to the capstone 23 ft above mean high "
                    "water. Plan (68 by 134 ft on top) and capstone elevation are both stated "
                    "explicitly by SRC-016. The pier is drawn from the caisson top rather than from "
                    "its footing seat at -33 ft, so the envelope is conservative. See OQ-016."
                ),
                geometry=[
                    box(
                        (x - pier_hx, -pier_hy, sk.z("ELV-CAISSON-TOP")),
                        (x + pier_hx, pier_hy, pier_top),
                    )
                ],
                style="tower_solid",
            )
        )
        # Four box-section legs standing in the planes of the four stiffening trusses (SRC-015).
        leg_hw = m("tower_leg_width_transverse") / 2.0
        leg_half_base = m("tower_leg_length_at_base") / 2.0
        leg_half_top = m("tower_leg_length_at_top") / 2.0
        expected_legs = int(model.raw("tower_leg_count"))
        if len(truss_planes) != expected_legs:
            raise ControlDocumentError(
                f"tower_leg_count is {expected_legs} but {len(truss_planes)} leg planes were built"
            )
        for letter, y, position in truss_planes:
            parts.append(
                Part(
                    part_id=f"tower_{side}_leg_{letter}",
                    system="towers",
                    subsystem="legs",
                    source_basis=["control_dimension"],
                    basis_confidence="A",
                    control_refs=ids(
                        "main_span", "cable_saddle_elevation", "tower_pier_top_above_mhw",
                        "tower_leg_width_transverse", "tower_leg_length_at_base",
                        "tower_leg_length_at_top", "truss_offset_inner", "truss_offset_outer",
                    ),
                    notes=(
                        f"Box-section tower leg in the plane of truss {letter.upper()} ({position}). "
                        "SRC-015: four legs, each 5 ft wide transversely, tapering from 32 ft to 10 ft "
                        "parallel to the bridge axis, and the trusses are carried in the planes of the "
                        "legs. Straight taper assumed between the two stated end dimensions."
                    ),
                    geometry=[
                        prism(
                            [
                                (x - leg_half_base, y - leg_hw, pier_top),
                                (x + leg_half_base, y - leg_hw, pier_top),
                                (x + leg_half_base, y + leg_hw, pier_top),
                                (x - leg_half_base, y + leg_hw, pier_top),
                            ],
                            [
                                (x - leg_half_top, y - leg_hw, saddle_z),
                                (x + leg_half_top, y - leg_hw, saddle_z),
                                (x + leg_half_top, y + leg_hw, saddle_z),
                                (x - leg_half_top, y + leg_hw, saddle_z),
                            ],
                        )
                    ],
                    style="tower_steel",
                )
            )

        # Transverse bracing between the legs. The struts are placeholders in elevation only.
        brace_levels = [pier_top + (saddle_z - pier_top) * f for f in (0.28, 0.52, 0.76, 0.97)]
        brace_segments: list[tuple[Point, Point]] = []
        leg_ys = [y for _, y, _ in truss_planes]
        for z in brace_levels:
            for y0, y1 in zip(leg_ys, leg_ys[1:]):
                brace_segments.append(((x, y0, z), (x, y1, z)))
        for z0, z1 in zip(brace_levels, brace_levels[1:]):
            for y0, y1 in zip(leg_ys, leg_ys[1:]):
                brace_segments.append(((x, y0, z0), (x, y1, z1)))
                brace_segments.append(((x, y1, z0), (x, y0, z1)))
        parts.append(
            Part(
                part_id=f"tower_{side}_bracing",
                system="towers",
                subsystem="legs",
                source_basis=["control_dimension", "inferred"],
                basis_confidence="D",
                control_refs=ids(
                    "main_span", "cable_saddle_elevation", "tower_pier_top_above_mhw",
                    "truss_offset_inner", "truss_offset_outer",
                ),
                open_questions=["OQ-007"],
                notes=(
                    "Transverse bracing between the tower legs. SRC-015 states the legs are 'heavily "
                    "braced together' and a 1904 account describes a 'great open arch' at the centre, "
                    "but no source gives the panel levels or the arch profile, so the number and "
                    "elevation of these struts are placeholders. See OQ-007."
                ),
                geometry=[lines(brace_segments)],
                style="tower_line",
            )
        )

    # --------------------------------------------------------------- anchorages
    for side, station_id, direction in (
        ("manhattan", "STA-ANC-M", -1.0),
        ("brooklyn", "STA-ANC-B", 1.0),
    ):
        x = sk.x(station_id)
        ext_x = m("anchorage_extent_x")
        half_y = m("anchorage_extent_y") / 2.0
        x0, x1 = sorted((x, x + direction * ext_x))
        parts.append(
            Part(
                part_id=f"{side}_anchorage",
                system="anchorages",
                source_basis=["control_dimension"],
                basis_confidence="B",
                control_refs=ids(
                    "main_span", "side_span_each", "anchorage_extent_x",
                    "anchorage_extent_y", "anchorage_extent_z",
                ),
                notes=(
                    "Anchorage envelope, 237 ft long by 182 ft wide by 135 ft tall, all sourced "
                    "(CTL-034/035/036), retiring OQ-008. Extends outboard from the cable point. "
                    "The Cherry Street and Water Street arches are not modelled."
                ),
                geometry=[box((x0, -half_y, 0.0), (x1, half_y, m("anchorage_extent_z")))],
                style="anchorage_solid",
            )
        )

    # ------------------------------------------------------------------- cables
    profile = CableProfile(model, sk)
    cable_refs = ids(
        "main_span", "side_span_each", "cable_saddle_elevation",
        "cable_saddle_drop_below_cable_top", "min_suspender_length_at_midspan",
        "center_clearance_above_mhw", "stiffening_truss_depth_asce",
        "truss_offset_inner", "truss_offset_outer", "anchorage_extent_z",
    )
    cable_names = {
        "a": "south_main_cable_1",
        "b": "south_main_cable_2",
        "c": "north_main_cable_2",
        "d": "north_main_cable_1",
    }
    expected_cables = int(model.raw("main_cable_count"))
    if len(truss_planes) != expected_cables:
        raise ControlDocumentError(
            f"main_cable_count is {expected_cables} but {len(truss_planes)} cable planes were built"
        )
    for letter, y, position in truss_planes:
        parts.append(
            Part(
                part_id=cable_names[letter],
                system="cables",
                source_basis=["control_dimension", "inferred"],
                basis_confidence="B",
                control_refs=cable_refs + ids("main_cable_diameter_measured"),
                open_questions=["OQ-001"],
                notes=(
                    f"Main cable over truss {letter.upper()} ({position}), drawn at its sourced "
                    "diameter of 21.2 in. SRC-011 measures 21.2 in overall and SRC-015 states 21.25 in "
                    "on the wires excluding wrapping, so the two agree to within 0.05 in and the "
                    "thickness is no longer speculative. Saddle and anchorage elevations are sourced; "
                    "the sag is derived from the truss top chord, see OQ-001."
                ),
                geometry=[
                    tube(
                        profile.polyline_points(y, 128, 64),
                        m("main_cable_diameter_measured") / 2.0,
                    )
                ],
                style="cable_solid",
            )
        )

    # --------------------------------------------------------------- suspenders
    pitch, pitch_evidence = derive_suspender_pitch(model)
    sk.notes.append(
        "Suspender pitch derived as {pitch_ft:.4f} ft from {points_per_cable:g} panel points per "
        "cable ({main_span_panels} main + 2 x {side_span_panels} side panels).".format(**pitch_evidence)
    )
    suspender_refs = cable_refs + ids(
        "suspender_panel_points_total", "main_cable_count", "suspender_rope_count"
    )
    tower_xs = (sk.x("STA-TWR-M"), sk.x("STA-TWR-B"))
    for letter, y, position in truss_planes:
        segments: list[tuple[Point, Point]] = []
        count = int(math.floor(anchor_x / pitch))
        for i in range(-count, count + 1):
            x = i * pitch
            if any(abs(x - tx) < pitch * 0.5 for tx in tower_xs):
                continue
            top = profile.z_at(x)
            if top - truss_top < 0.5:
                continue
            segments.append(((x, y, top), (x, y, truss_top)))
        parts.append(
            Part(
                part_id=f"suspenders_truss_{letter}",
                system="suspenders",
                source_basis=["control_dimension", "inferred"],
                basis_confidence="B",
                control_refs=suspender_refs,
                open_questions=["OQ-001"],
                notes=(
                    f"Suspender set on truss {letter.upper()} ({position}), grouped as one addressable "
                    "part. Pitch is derived from the sourced 628 panel points (CTL-037): "
                    "{main_span_panels} panels in the main span and {side_span_panels} in each side "
                    "span at {pitch_ft:.3f} ft, the unique integer solution. Two ropes per panel point "
                    "(CTL-038) are not modelled individually.".format(**pitch_evidence)
                ),
                geometry=[lines(segments)]
                if segments
                else [polyline([(0.0, y, truss_top), (0.0, y, truss_top + 0.001)])],
                style="suspender_line",
            )
        )

    # -------------------------------------------------------------- deck system
    span_segments = (
        ("main_span", -half_main, half_main),
        ("side_span_manhattan", -anchor_x, -half_main),
        ("side_span_brooklyn", half_main, anchor_x),
    )

    # Upper roadways sit over the A-B and C-D truss bays (SRC-011), not on the centerline.
    bay_center = (truss_inner + truss_outer) / 2.0
    upper_roadways = (
        ("brooklyn_bound", -bay_center, m("upper_roadway_west_width"), "west, over trusses A-B"),
        ("manhattan_bound", bay_center, m("upper_roadway_east_width"), "east, over trusses C-D"),
    )

    for segment_name, x0, x1 in span_segments:
        for road_name, y_center, width, description in upper_roadways:
            half_w = width / 2.0
            parts.append(
                Part(
                    part_id=f"upper_roadway_{road_name}_{segment_name}",
                    system="deck_system",
                    subsystem="upper_roadway",
                    source_basis=["control_dimension"],
                    basis_confidence="B",
                    control_refs=ids(
                        "main_span", "side_span_each", "upper_roadway_east_width",
                        "upper_roadway_west_width", "truss_offset_inner", "truss_offset_outer",
                        "center_clearance_above_mhw", "stiffening_truss_depth_asce",
                        "upper_deck_structure_depth",
                    ),
                    open_questions=["OQ-013"],
                    notes=(
                        f"Upper roadway envelope, {description}, over the "
                        f"{segment_name.replace('_', ' ')}. SRC-011 states the upper levels rest on "
                        "trusses A-B and C-D, so the roadways are offset from the centerline. Width is "
                        "sourced; only the deck structure depth is a placeholder (OQ-013)."
                    ),
                    geometry=[
                        box((x0, y_center - half_w, truss_top), (x1, y_center + half_w, upper_deck))
                    ],
                    style="deck_solid",
                )
            )

        half_lower = m("lower_roadway_width") / 2.0
        parts.append(
            Part(
                part_id=f"lower_roadway_envelope_{segment_name}",
                system="deck_system",
                subsystem="lower_roadway",
                source_basis=["control_dimension"],
                basis_confidence="B",
                control_refs=ids(
                    "main_span", "side_span_each", "lower_roadway_width",
                    "center_clearance_above_mhw", "lower_deck_offset_above_clearance",
                ),
                open_questions=["OQ-013"],
                notes=(
                    "Lower roadway envelope over the "
                    f"{segment_name.replace('_', ' ')}, centered on the bridge centerline at the "
                    "sourced 35 ft width (CTL-024, 1909 cross-section)."
                ),
                geometry=[box((x0, -half_lower, truss_bottom), (x1, half_lower, lower_deck))],
                style="deck_solid",
            )
        )

        for letter, y, position in truss_planes:
            # Chords and panel points are fully sourced; the web pattern is not. They are emitted as
            # separate parts so the grades stay honest and each is independently addressable.
            n_panels = max(1, int(round((x1 - x0) / pitch)))
            panel = (x1 - x0) / n_panels
            chord_refs = ids(
                "main_span", "side_span_each", "center_clearance_above_mhw",
                "stiffening_truss_depth_asce", "truss_offset_inner", "truss_offset_outer",
            )
            parts.append(
                Part(
                    part_id=f"stiffening_truss_{letter}_chords_{segment_name}",
                    system="deck_system",
                    subsystem="stiffening_trusses",
                    source_basis=["control_dimension"],
                    basis_confidence="A",
                    control_refs=chord_refs,
                    notes=(
                        f"Top and bottom chords of stiffening truss {letter.upper()} ({position}) "
                        f"over the {segment_name.replace('_', ' ')}. Depth 24 ft and the 28-40-28 ft "
                        "transverse spacing are sourced from SRC-002, SRC-011 and SRC-015. Chord "
                        "member sections are not modelled."
                    ),
                    geometry=[
                        lines(
                            [
                                ((x0, y, truss_bottom), (x1, y, truss_bottom)),
                                ((x0, y, truss_top), (x1, y, truss_top)),
                            ]
                        )
                    ],
                    style="truss_member",
                )
            )
            web: list[tuple[Point, Point]] = []
            for i in range(n_panels):
                xa = x0 + i * panel
                xb = xa + panel
                if i % 2 == 0:
                    web.append(((xa, y, truss_bottom), (xb, y, truss_top)))
                else:
                    web.append(((xa, y, truss_top), (xb, y, truss_bottom)))
                web.append(((xb, y, truss_bottom), (xb, y, truss_top)))
            web.append(((x0, y, truss_bottom), (x0, y, truss_top)))
            parts.append(
                Part(
                    part_id=f"stiffening_truss_{letter}_web_{segment_name}",
                    system="deck_system",
                    subsystem="stiffening_trusses",
                    source_basis=["control_dimension", "inferred"],
                    basis_confidence="D",
                    control_refs=chord_refs + ids(
                        "suspender_panel_points_total", "main_cable_count"
                    ),
                    open_questions=["OQ-017"],
                    notes=(
                        f"Web members of truss {letter.upper()} ({position}) over the "
                        f"{segment_name.replace('_', ' ')}: {n_panels} panels at "
                        f"{panel / 0.3048:.2f} ft. The panel *positions* are sourced, being the unique "
                        "integer solution to the 628 panel points in CTL-037. The alternating diagonal "
                        "pattern follows the Warren form named by SRC-002, SRC-011 and SRC-012, but no "
                        "source gives the diagonal handedness at each panel or whether verticals are "
                        "present, so the web itself is inferred. See OQ-017."
                    ),
                    geometry=[lines(web)],
                    style="truss_web",
                )
            )

    for side_name, sign in (("south", -1.0), ("north", 1.0)):
        y_inner = sign * truss_outer
        y_outer = sign * (truss_outer + m("footwalk_width"))
        y0, y1 = sorted((y_inner, y_outer))
        parts.append(
            Part(
                part_id=f"footwalk_{side_name}",
                system="deck_system",
                subsystem="lower_roadway",
                source_basis=["control_dimension"],
                basis_confidence="B",
                control_refs=ids(
                    "main_span", "side_span_each", "footwalk_width", "truss_offset_outer",
                    "deck_overall_width", "center_clearance_above_mhw",
                    "lower_deck_offset_above_clearance",
                ),
                open_questions=["OQ-013"],
                notes=(
                    f"{side_name.capitalize()} footwalk envelope, 10 ft wide (CTL-025), outboard of "
                    f"truss {'A' if sign < 0 else 'D'}. Today the south path is the walkway and the "
                    "north path is the bikeway. Placement follows the 1909 cross-section, which closes "
                    "to the sourced 120 ft deck width."
                ),
                geometry=[box((-anchor_x, y0, lower_deck), (anchor_x, y1, lower_deck + 0.3))],
                style="deck_solid",
            )
        )

    gauge_half = m("subway_track_gauge") / 2.0
    inner = m("subway_track_bay_inner_offset")
    track_spacing = m("subway_track_spacing_y")
    track_planes = [
        ("track_1", inner + track_spacing),
        ("track_2", inner),
        ("track_3", -inner),
        ("track_4", -(inner + track_spacing)),
    ]
    expected_tracks = int(model.raw("subway_track_count"))
    if len(track_planes) != expected_tracks:
        raise ControlDocumentError(
            f"subway_track_count is {expected_tracks} but {len(track_planes)} tracks were built"
        )
    for track_id, y in track_planes:
        if not (truss_inner - 1e-6 <= abs(y) - gauge_half and abs(y) + gauge_half <= truss_outer + 1e-6):
            raise ControlDocumentError(
                f"{track_id} at y={y:.3f} m falls outside the sourced truss bay "
                f"({truss_inner:.3f} to {truss_outer:.3f} m); SRC-011 places all four tracks "
                "inside the A-B and C-D bays"
            )
        parts.append(
            Part(
                part_id=track_id,
                system="deck_system",
                subsystem="subway_tracks",
                source_basis=["control_dimension", "inferred"],
                basis_confidence="B",
                control_refs=ids(
                    "main_span", "side_span_each", "subway_track_gauge",
                    "subway_track_bay_inner_offset", "subway_track_spacing_y",
                    "truss_offset_inner", "truss_offset_outer", "center_clearance_above_mhw",
                    "lower_deck_offset_above_clearance", "subway_track_structure_depth",
                ),
                open_questions=["OQ-010", "OQ-013"],
                notes=(
                    "Subway track envelope over the suspended length. SRC-011 confirms two tracks in "
                    "each of the A-B and C-D truss bays, which bounds the transverse position between "
                    "20 ft and 48 ft from the centerline; the exact centerline within that bay is "
                    "still a placeholder, see OQ-010. Approach trackwork is not modelled."
                ),
                geometry=[
                    box(
                        (-anchor_x, y - gauge_half, lower_deck),
                        (anchor_x, y + gauge_half, lower_deck + m("subway_track_structure_depth")),
                    )
                ],
                style="track_solid",
            )
        )

    # --------------------------------------------------------------- approaches
    for side, station_id, end_station, direction in (
        ("manhattan", "STA-ANC-M", "STA-APPR-END-M", -1.0),
        ("brooklyn", "STA-ANC-B", "STA-APPR-END-B", 1.0),
    ):
        inner_x = sk.x(station_id) + direction * m("anchorage_extent_x")
        outer_x = sk.x(end_station)
        x0, x1 = sorted((inner_x, outer_x))
        parts.append(
            Part(
                part_id=f"{side}_approach",
                system="approaches",
                source_basis=["control_dimension", "inferred"],
                basis_confidence="C",
                control_refs=ids(
                    "total_bridge_and_approaches_length", "anchorage_to_anchorage_suspended_length",
                    "manhattan_approach_and_plaza_length", "brooklyn_approach_and_plaza_length",
                    "deck_overall_width", "anchorage_extent_x", "center_clearance_above_mhw",
                    "stiffening_truss_depth_asce", "upper_deck_structure_depth",
                ),
                open_questions=["OQ-002", "OQ-006", "OQ-013"],
                notes=(
                    "Approach deck envelope, drawn level from the outboard face of the anchorage to "
                    "the approach end station. The length split is now a sourced ratio (OQ-006 "
                    "mitigated), but grade, plan curvature and the continuous Warren truss structure "
                    "described by SRC-011 are not modelled."
                ),
                geometry=[box((x0, -deck_half_w, truss_top), (x1, deck_half_w, upper_deck))],
                style="approach_solid",
            )
        )

    for part in parts:
        part.resolve_confidence(model)
    return parts


# --------------------------------------------------------------------- validation


def validate_parts(parts: Sequence[Part]) -> None:
    seen: set[str] = set()
    for part in parts:
        meta = part.metadata()
        missing = [f for f in REQUIRED_METADATA_FIELDS if not meta.get(f)]
        if missing:
            raise ControlDocumentError(
                f"part {part.part_id} is missing required metadata: {', '.join(missing)}"
            )
        if part.part_id in seen:
            raise ControlDocumentError(f"duplicate part_id {part.part_id}")
        seen.add(part.part_id)
        if part.part_id != part.part_id.lower():
            raise ControlDocumentError(f"part_id {part.part_id} must be lowercase snake_case")
        bad_basis = set(part.source_basis) - ALLOWED_SOURCE_BASIS
        if bad_basis:
            raise ControlDocumentError(
                f"part {part.part_id} declares unknown source_basis values: {sorted(bad_basis)}"
            )
        if part.confidence == "D" and "OQ-" not in part.notes and not part.open_questions:
            raise ControlDocumentError(
                f"part {part.part_id} is confidence D but names no open question in its notes"
            )
        if not part.geometry:
            raise ControlDocumentError(f"part {part.part_id} has no geometry")


# ------------------------------------------------------------------------ export


def emit_gltf(parts: Sequence[Part], model: ControlModel, sk: Skeleton, scale: float,
              title: str) -> GltfBuilder:
    builder = GltfBuilder(
        generator=AGENT_ID,
        scale=scale,
        copyright_text=(
            "Manhattan Bridge digital twin control skeleton. Geometry derived from GEOMETRY-CONTROL.md; "
            "see SOURCE-REGISTER.md and CONFIDENCE-MODEL.md. Placeholder geometry is tagged confidence D."
        ),
    )
    builder.set_root_name(title)
    builder.set_root_extras(
        {
            "model": "control_skeleton",
            "milestone": 2,
            "scale": f"1:{1/scale:.4g}" if scale != 1.0 else "1:1 prototype",
            "control_document_sha256": model.document_sha256,
            "coordinate_system": "authoring Z-up, +X toward Brooklyn, +Y north; root node rotates to glTF Y-up",
            "units": "meters",
        }
    )

    system_nodes: dict[str, int] = {}
    for part in parts:
        style = STYLES[part.style]
        material = builder.add_material(
            part.style, style["color"], unlit=style["unlit"], double_sided=True
        )
        primitives = []
        for prim in part.geometry:
            kind = prim["kind"]
            if kind == "box":
                pos, nrm, idx = box_mesh_data(prim["min"], prim["max"])
                primitives.append(builder.triangle_primitive(pos, nrm, idx, material))
            elif kind == "quad":
                pos, nrm, idx = quad_mesh_data(prim["corners"])
                primitives.append(builder.triangle_primitive(pos, nrm, idx, material))
            elif kind == "prism":
                pos, nrm, idx = prism_mesh_data(prim["bottom"], prim["top"])
                primitives.append(builder.triangle_primitive(pos, nrm, idx, material))
            elif kind == "tube":
                pos, nrm, idx = tube_mesh_data(prim["points"], prim["radius"])
                primitives.append(builder.triangle_primitive(pos, nrm, idx, material))
            elif kind == "polyline":
                primitives.append(builder.polyline_primitive(prim["points"], material))
            elif kind == "lines":
                primitives.append(builder.line_primitive(prim["segments"], material))
            else:  # pragma: no cover
                raise ValueError(f"unknown geometry kind {kind!r}")

        mesh = builder.add_mesh(f"{part.part_id}_mesh", primitives)
        node = builder.add_node(part.part_id, mesh=mesh, extras=part.metadata())

        key = part.system if not part.subsystem else f"{part.system}/{part.subsystem}"
        if key not in system_nodes:
            if part.subsystem:
                if part.system not in system_nodes:
                    system_nodes[part.system] = builder.add_node(part.system)
                    builder.add_to_root(system_nodes[part.system])
                system_nodes[key] = builder.add_node(f"{part.system}.{part.subsystem}")
                builder.add_child(system_nodes[part.system], system_nodes[key])
            else:
                system_nodes[key] = builder.add_node(part.system)
                builder.add_to_root(system_nodes[key])
        builder.add_child(system_nodes[key], node)
    return builder


def build_taxonomy(parts: Sequence[Part]) -> dict[str, Any]:
    tree: dict[str, Any] = {}
    for part in parts:
        system = tree.setdefault(part.system, {"parts": [], "subsystems": {}})
        if part.subsystem:
            system["subsystems"].setdefault(part.subsystem, []).append(part.part_id)
        else:
            system["parts"].append(part.part_id)
    return tree


def compute_measures(parts: Sequence[Part], model: ControlModel, sk: Skeleton) -> dict[str, Any]:
    profile = CableProfile(model, sk)
    cable_points = profile.polyline_points(model.m("truss_offset_outer"), 512, 256)
    pitch, pitch_evidence = derive_suspender_pitch(model)
    by_id = {p.part_id: p for p in parts}

    all_points = [pt for p in parts for pt in p.points()]
    bbox_min = [min(pt[i] for pt in all_points) for i in range(3)]
    bbox_max = [max(pt[i] for pt in all_points) for i in range(3)]

    suspender_count = sum(
        len(prim["segments"])
        for p in parts
        if p.system == "suspenders"
        for prim in p.geometry
        if prim["kind"] == "lines"
    )

    confidence_histogram: dict[str, int] = {grade: 0 for grade in CONFIDENCE_ORDER}
    for part in parts:
        confidence_histogram[part.confidence] += 1

    deck_curve = by_id["control_curve_deck_centerline"].geometry[0]["points"]
    sag = profile.sag_main

    return {
        "part_count": len(parts),
        "confidence_histogram": confidence_histogram,
        "suspender_segment_count": suspender_count,
        "suspender_pitch_m": pitch,
        "suspender_pitch_derivation": pitch_evidence,
        "model_bbox_prototype_m": {"min": bbox_min, "max": bbox_max},
        "model_length_prototype_m": bbox_max[0] - bbox_min[0],
        "model_height_prototype_m": bbox_max[2] - bbox_min[2],
        "model_width_prototype_m": bbox_max[1] - bbox_min[1],
        "single_main_cable_polyline_length_m": polyline_length(cable_points),
        "cable_sag_main_span_m": sag,
        "cable_sag_ratio_denominator": model.m("main_span") / sag,
        "cable_sag_side_span_derived_m": profile.sag_side,
        "deck_centerline_length_m": polyline_length([tuple(p) for p in deck_curve]),
        "tower_spacing_m": sk.x("STA-TWR-B") - sk.x("STA-TWR-M"),
        "anchorage_spacing_m": sk.x("STA-ANC-B") - sk.x("STA-ANC-M"),
        "placeholder_control_count": len(model.placeholders),
        "sourced_control_count": len(model.controls) - len(model.placeholders),
    }


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Manhattan Bridge control skeleton.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--no-viewer-copy", action="store_true", help="skip copying into viewer/public")
    args = parser.parse_args(argv)

    root: Path = args.repo_root
    control_doc = root / "GEOMETRY-CONTROL.md"
    model = load_control_model(control_doc)
    sk = derive_skeleton(model)
    parts = build_parts(model, sk)
    validate_parts(parts)

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    measures = compute_measures(parts, model, sk)

    prototype = emit_gltf(parts, model, sk, 1.0, "manhattan_bridge_control_skeleton")
    glb_path = prototype.save_glb(root / "mesh" / "glb" / "control_skeleton.glb")
    gltf_path = emit_gltf(parts, model, sk, 1.0, "manhattan_bridge_control_skeleton").save_gltf(
        root / "mesh" / "glb" / "control_skeleton.gltf"
    )
    ho = emit_gltf(parts, model, sk, 1.0 / HO_SCALE_DENOMINATOR, "manhattan_bridge_control_skeleton_ho")
    ho_path = ho.save_glb(root / "mesh" / "glb" / "control_skeleton_ho.glb")

    provenance = {
        "schema_version": "1.0",
        "model": "control_skeleton",
        "milestone": 2,
        "generated_by": AGENT_ID,
        "generated_at": generated_at,
        "control_document": {
            "path": "GEOMETRY-CONTROL.md",
            "sha256": model.document_sha256,
        },
        "source_register": "SOURCE-REGISTER.md",
        "confidence_model": "CONFIDENCE-MODEL.md",
        "ho_scale_denominator": HO_SCALE_DENOMINATOR,
    }

    parts_payload = {
        **provenance,
        "coordinate_system": {
            "units": "meters",
            "origin": "main span midpoint at mean high water",
            "x": "+X toward Brooklyn",
            "y": "+Y toward the north side",
            "z": "+Z up from mean high water",
            "gltf_note": "the exported GLB root node rotates the Z-up authoring frame into the glTF Y-up frame",
        },
        "confidence_colors": CONFIDENCE_COLORS,
        "taxonomy": build_taxonomy(parts),
        "stations": list(sk.stations.values()),
        "elevations": list(sk.elevations.values()),
        "controls": [
            {
                "control_id": c.control_id,
                "key": c.key,
                "value": c.value,
                "unit": c.unit,
                "value_m": c.value_m,
                "source_ids": list(c.source_ids),
                "confidence": c.confidence,
                "is_placeholder": c.is_placeholder,
                "notes": c.notes,
                "ho": ho_report(c.value_m) if is_linear(c.unit) else None,
            }
            for c in model.controls.values()
        ],
        "measures": measures,
        "parts": [p.metadata() for p in parts],
    }
    parts_json = write_json(root / "viewer" / "metadata" / "parts.json", parts_payload)

    scale_payload = {
        **provenance,
        "note": "Computed from GEOMETRY-CONTROL.md. Compare against the reference table in SCALE-HO.md.",
        "controls": [
            {
                "control_id": c.control_id,
                "key": c.key,
                "prototype": f"{c.value:g} {c.unit}",
                "confidence": c.confidence,
                **ho_report(c.value_m),
            }
            for c in model.controls.values()
            if is_linear(c.unit)
        ],
    }
    scale_json = write_json(root / "viewer" / "metadata" / "scale_ho.json", scale_payload)

    report_payload = {
        **provenance,
        "checks": sk.notes,
        "stations": {k: v["x_m"] for k, v in sk.stations.items()},
        "elevations": {k: v["z_m"] for k, v in sk.elevations.items()},
        "controls_m": {c.key: c.value_m for c in model.controls.values()},
        "controls_raw": {c.key: c.value for c in model.controls.values()},
        "control_confidence": {c.key: c.confidence for c in model.controls.values()},
        "measures": measures,
        "outputs": {
            "glb": str(glb_path.relative_to(root)).replace("\\", "/"),
            "gltf": str(gltf_path.relative_to(root)).replace("\\", "/"),
            "glb_ho": str(ho_path.relative_to(root)).replace("\\", "/"),
            "parts_json": str(parts_json.relative_to(root)).replace("\\", "/"),
            "scale_json": str(scale_json.relative_to(root)).replace("\\", "/"),
        },
    }
    report_json = write_json(root / "viewer" / "metadata" / "build_report.json", report_payload)

    geometry_payload = {
        **provenance,
        "note": (
            "Tool-neutral procedural definition of the control skeleton. Consumed by "
            "cad/procedural/build_in_blender.py to produce control_skeleton.blend and, via FreeCAD or "
            "Rhino, control_skeleton.step."
        ),
        "styles": {k: {"color": list(v["color"]), "unlit": v["unlit"]} for k, v in STYLES.items()},
        "parts": [{**p.metadata(), "style": p.style, "geometry": p.geometry} for p in parts],
    }
    geometry_json = write_json(
        root / "cad" / "procedural" / "control_skeleton_geometry.json", geometry_payload
    )

    if not args.no_viewer_copy:
        public = root / "viewer" / "public"
        public.mkdir(parents=True, exist_ok=True)
        shutil.copy2(glb_path, public / glb_path.name)
        shutil.copy2(ho_path, public / ho_path.name)
        shutil.copy2(parts_json, public / "parts.json")

    print(f"control document : GEOMETRY-CONTROL.md sha256={model.document_sha256[:12]}")
    print(f"controls         : {len(model.controls)} ({len(model.placeholders)} placeholders)")
    print(f"stations         : {len(sk.stations)}")
    print(f"parts            : {len(parts)}")
    hist = measures["confidence_histogram"]
    print("confidence       : " + "  ".join(f"{g}={hist[g]}" for g in "ABCD"))
    print(f"model length     : {measures['model_length_prototype_m']:.3f} m prototype "
          f"({measures['model_length_prototype_m'] / HO_SCALE_DENOMINATOR * 1000.0:.1f} mm HO)")
    for label, path in (
        ("glb", glb_path), ("gltf", gltf_path), ("glb_ho", ho_path), ("parts", parts_json),
        ("scale", scale_json), ("report", report_json), ("geometry", geometry_json),
    ):
        print(f"  {label:<9} -> {path.relative_to(root)} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
