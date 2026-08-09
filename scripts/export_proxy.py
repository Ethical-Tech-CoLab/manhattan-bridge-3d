"""Export the level-2 district proxy: one decimated GLB of the whole bridge.

Why this exists
---------------
`dumbo-district-3d` must show the Manhattan Bridge where it crosses their district, but the
anti-duplication rule in the shared contract forbids them from modelling a single bridge triangle.
The resolution is that this module publishes a cheap stand-in they consume by URN.

This is what a pedestrian on Washington Street actually sees: correct silhouette, correct position,
a few thousand triangles, no rivets.

What it is
----------
Every dimension comes from GEOMETRY-CONTROL.md through the same parser the LOD0 control skeleton
uses, so the proxy cannot drift from the control document. It is a simplification of that geometry,
never an independent model:

  deck        one slab spanning the full structural envelope, truss bottom chord to upper roadway
  towers      the four sourced tapered legs per tower, plus pier and caisson above water
  anchorages  one block each
  cables      four swept tubes on the derived parabolic profile
  suspenders  every Nth panel point, enough to read as a suspension bridge at district range

Frame
-----
Authored in the module's own frame exactly like LOD0: origin at the main-span midpoint, +X toward
Brooklyn, +Z up, meters, z = 0 at mean high water. It is NOT pre-transformed into the shared scene
frame; `placement` in bridge-manifest.json does that, and the consuming kernel composes it.

Usage
-----
    python scripts/export_proxy.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_control_skeleton import (  # noqa: E402
    AGENT_ID,
    CableProfile,
    derive_skeleton,
    derive_suspender_pitch,
)
from control_model import load_control_model  # noqa: E402
from export_gltf import (  # noqa: E402
    GltfBuilder,
    box_mesh_data,
    prism_mesh_data,
    tube_mesh_data,
)

REPO_ROOT = SCRIPT_DIR.parent

# Level 2 on the shared ladder. The dominant simplification is representing the whole deck system —
# four trusses, two upper roadways, the lower roadway, four tracks and two footwalks — as a single
# solid slab. That slab is 8.23 m deep, so a point inside it can be up to about 8 m from the nearest
# real surface. Declaring 8.0 is therefore honest rather than flattering.
MAX_GEOMETRIC_ERROR_M = 8.0

# Keep every fourth panel point. Individual suspenders are far below the level-2 error budget, but
# omitting them entirely loses the one visual cue that says "suspension bridge" at street range.
SUSPENDER_STRIDE = 4

Point = tuple[float, float, float]


def merge(target: tuple[list, list, list], source: tuple[list, list, list]) -> None:
    base = len(target[0])
    target[0].extend(source[0])
    target[1].extend(source[1])
    target[2].extend(i + base for i in source[2])


def build_proxy(model, sk) -> dict[str, tuple[list, list, list]]:
    """Return named merged meshes, each (positions, normals, indices)."""
    m = model.m
    half_main = m("main_span") / 2.0
    anchor_x = sk.x("STA-ANC-B")
    appr_m = sk.x("STA-APPR-END-M")
    appr_b = sk.x("STA-APPR-END-B")

    truss_bottom = sk.z("ELV-TRUSS-BOTTOM")
    upper_deck = sk.z("ELV-UPPER-DECK")
    pier_top = sk.z("ELV-PIER-TOP")
    saddle_z = sk.z("ELV-SADDLE")
    foundation = sk.z("ELV-FOUNDATION")
    deck_half = m("deck_overall_width") / 2.0

    truss_inner = m("truss_offset_inner")
    truss_outer = m("truss_offset_outer")
    planes = (-truss_outer, -truss_inner, truss_inner, truss_outer)

    meshes: dict[str, tuple[list, list, list]] = {}

    # ---- deck: one slab over the suspended length, thinner slabs over the approaches
    deck: tuple[list, list, list] = ([], [], [])
    merge(deck, box_mesh_data((-anchor_x, -deck_half, truss_bottom), (anchor_x, deck_half, upper_deck)))
    for x0, x1 in ((appr_m, -anchor_x), (anchor_x, appr_b)):
        merge(deck, box_mesh_data((x0, -deck_half, upper_deck - 3.0), (x1, deck_half, upper_deck)))
    meshes["bridge_proxy_deck"] = deck

    # ---- towers: the four sourced tapered legs, on the pier and caisson
    leg_hw = m("tower_leg_width_transverse") / 2.0
    half_base = m("tower_leg_length_at_base") / 2.0
    half_top = m("tower_leg_length_at_top") / 2.0
    pier_hx = m("tower_pier_extent_x") / 2.0
    pier_hy = m("tower_pier_extent_y") / 2.0

    for side, station in (("manhattan", "STA-TWR-M"), ("brooklyn", "STA-TWR-B")):
        x = sk.x(station)
        tower: tuple[list, list, list] = ([], [], [])
        merge(tower, box_mesh_data((x - pier_hx, -pier_hy, foundation), (x + pier_hx, pier_hy, pier_top)))
        for y in planes:
            merge(
                tower,
                prism_mesh_data(
                    [
                        (x - half_base, y - leg_hw, pier_top),
                        (x + half_base, y - leg_hw, pier_top),
                        (x + half_base, y + leg_hw, pier_top),
                        (x - half_base, y + leg_hw, pier_top),
                    ],
                    [
                        (x - half_top, y - leg_hw, saddle_z),
                        (x + half_top, y - leg_hw, saddle_z),
                        (x + half_top, y + leg_hw, saddle_z),
                        (x - half_top, y + leg_hw, saddle_z),
                    ],
                ),
            )
        # One transverse strut near the top so the towers read as portals, not four posts.
        strut_z = pier_top + (saddle_z - pier_top) * 0.93
        merge(
            tower,
            box_mesh_data(
                (x - half_top, -truss_outer, strut_z - 2.5),
                (x + half_top, truss_outer, strut_z + 2.5),
            ),
        )
        meshes[f"bridge_proxy_tower_{side}"] = tower

    # ---- anchorages
    anc_hy = m("anchorage_extent_y") / 2.0
    ext_x = m("anchorage_extent_x")
    for side, station, direction in (("manhattan", "STA-ANC-M", -1.0), ("brooklyn", "STA-ANC-B", 1.0)):
        x = sk.x(station)
        x0, x1 = sorted((x, x + direction * ext_x))
        meshes[f"bridge_proxy_anchorage_{side}"] = box_mesh_data(
            (x0, -anc_hy, 0.0), (x1, anc_hy, m("anchorage_extent_z"))
        )

    # ---- cables and a reduced suspender set
    profile = CableProfile(model, sk)
    pitch, _ = derive_suspender_pitch(model)
    radius = m("main_cable_diameter_measured") / 2.0
    truss_top = sk.z("ELV-TRUSS-TOP")
    tower_xs = (sk.x("STA-TWR-M"), sk.x("STA-TWR-B"))

    cables: tuple[list, list, list] = ([], [], [])
    suspenders: tuple[list, list, list] = ([], [], [])
    for y in planes:
        merge(cables, tube_mesh_data(profile.polyline_points(y, 40, 16), radius, sides=6))
        count = int(math.floor(anchor_x / pitch))
        for i in range(-count, count + 1, SUSPENDER_STRIDE):
            x = i * pitch
            if any(abs(x - tx) < pitch * 0.5 for tx in tower_xs):
                continue
            top = profile.z_at(x)
            if top - truss_top < 2.0:
                continue
            merge(
                suspenders,
                tube_mesh_data([(x, y, top), (x, y, truss_top)], 0.45, sides=4),
            )
    meshes["bridge_proxy_cables"] = cables
    meshes["bridge_proxy_suspenders"] = suspenders

    return meshes


STYLES = {
    "bridge_proxy_deck": (0.44, 0.46, 0.49, 1.0),
    "bridge_proxy_tower_manhattan": (0.62, 0.60, 0.57, 1.0),
    "bridge_proxy_tower_brooklyn": (0.62, 0.60, 0.57, 1.0),
    "bridge_proxy_anchorage_manhattan": (0.66, 0.63, 0.58, 1.0),
    "bridge_proxy_anchorage_brooklyn": (0.66, 0.63, 0.58, 1.0),
    "bridge_proxy_cables": (0.80, 0.68, 0.34, 1.0),
    "bridge_proxy_suspenders": (0.72, 0.72, 0.70, 1.0),
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export the level-2 district proxy GLB.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root: Path = args.repo_root

    model = load_control_model(root / "GEOMETRY-CONTROL.md")
    sk = derive_skeleton(model)
    meshes = build_proxy(model, sk)

    builder = GltfBuilder(
        generator=f"export_proxy.py via {AGENT_ID}",
        copyright_text=(
            "Manhattan Bridge level-2 district proxy. Simplified from the control skeleton in "
            "GEOMETRY-CONTROL.md; see SOURCE-REGISTER.md. Not for measurement: "
            f"max_geometric_error_m = {MAX_GEOMETRIC_ERROR_M}."
        ),
    )
    builder.set_root_name("manhattan_bridge_proxy")
    builder.set_root_extras(
        {
            "asset_id": "urn:d3d:manhattan-bridge:bridge_proxy",
            "module_id": "manhattan-bridge",
            "level": 2,
            "max_geometric_error_m": MAX_GEOMETRIC_ERROR_M,
            "frame": "manhattan-bridge-local",
            "vertical_datum": "MHW",
            "units": "meters",
            "control_document_sha256": model.document_sha256,
            "note": (
                "Module-local frame: origin at the main-span midpoint, +X toward Brooklyn, +Y north, "
                "+Z up, z = 0 at mean high water. The root node applies the contract's fixed "
                "scene-to-render rotation (x, y, z) -> (x, z, -y), so a glTF loader yields Y-up "
                "module-local geometry. Apply bridge-manifest.json placement to reach the shared "
                "scene frame; that placement carries the +0.59 m MHW to NAVD88 correction."
            ),
        }
    )

    triangles = 0
    for name, (positions, normals, indices) in meshes.items():
        material = builder.add_material(name, STYLES[name], double_sided=False)
        mesh = builder.add_mesh(
            f"{name}_mesh", [builder.triangle_primitive(positions, normals, indices, material)]
        )
        builder.add_to_root(builder.add_node(name, mesh=mesh))
        triangles += len(indices) // 3

    out = root / "viewer" / "public" / "assets" / "bridge.lod2.glb"
    builder.save_glb(out)

    all_pts = [p for mesh in meshes.values() for p in mesh[0]]
    bbox_min = [min(p[i] for p in all_pts) for i in range(3)]
    bbox_max = [max(p[i] for p in all_pts) for i in range(3)]

    report = {
        "asset_id": "urn:d3d:manhattan-bridge:bridge_proxy",
        "level": 2,
        "max_geometric_error_m": MAX_GEOMETRIC_ERROR_M,
        "triangle_count": triangles,
        "byte_size": out.stat().st_size,
        "node_count": len(meshes),
        "bbox_local_m": {"min": bbox_min, "max": bbox_max},
        "frame": "manhattan-bridge-local",
        "vertical_datum": "MHW",
        "control_document_sha256": model.document_sha256,
        "generated_by": f"export_proxy.py via {AGENT_ID}",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "suspender_stride": SUSPENDER_STRIDE,
    }
    (root / "viewer" / "metadata" / "proxy_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    print(f"nodes      : {len(meshes)}")
    print(f"triangles  : {triangles:,}")
    print(f"bytes      : {out.stat().st_size:,}")
    print(f"bbox min   : [{bbox_min[0]:.1f}, {bbox_min[1]:.1f}, {bbox_min[2]:.1f}]")
    print(f"bbox max   : [{bbox_max[0]:.1f}, {bbox_max[1]:.1f}, {bbox_max[2]:.1f}]")
    print(f"wrote      : {out.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
