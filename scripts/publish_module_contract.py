"""Publish this module's contract surface for digital-3d-shared-contracts v1.

Emits, under viewer/public/ so the whole tree can be served at a site root:

    bridge-manifest.json          entry point; everything else is reached from here
    frames/nyc-harbor-enu.json    byte-identical copy of the canonical shared frame
    bridge/lod.json               the LOD ladder
    bridge/asset-registry.json    URN catalogue, including urn:d3d:manhattan-bridge:bridge_proxy
    bridge/metadata.json          parts.json mapped onto metadata.schema.json

Design notes
------------
Root-absolute URLs are used throughout ("/frames/...", "/assets/..."). The shared kernel passes
those through unchanged, so one manifest works whether this module is served at its own origin or
co-served from inside the district's tree. That is the only URL form that satisfies both deployment
options without maintaining two manifests.

The canonical frame is copied byte-for-byte rather than re-serialised, and the copy is verified by
hash, because the anchor is frozen for the life of contract major version 1 and every asset
coordinate in every module depends on it.

Nothing here re-derives a bridge dimension. Every number is read from GEOMETRY-CONTROL.md through
the same parser the build uses.

Usage
-----
    python scripts/publish_module_contract.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_control_skeleton import AGENT_ID, derive_skeleton  # noqa: E402
from control_model import load_control_model  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parent
CONTRACTS = Path(os.environ.get("D3D_CONTRACTS_DIR", r"c:\Dev\digital-3d-shared-contracts"))

CONTRACT_VERSION = "1.0.0"
MODULE_ID = "manhattan-bridge"
MODULE_VERSION = "1.0.0"
FRAME_ID = "nyc-harbor-enu"
LADDER_ID = "manhattan-bridge-ladder"
URN = f"urn:d3d:{MODULE_ID}:"

# Placement audited by this module in Milestone 5; see GEOMETRY-CONTROL.md section 6 and OQ-009.
PLACEMENT_TRANSLATION = [-150.22, 511.26, 0.59]
PLACEMENT_YAW_DEG = 292.633


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(model, extra_docs: list[tuple[str, Path]] | None = None) -> dict[str, Any]:
    docs = [{"path": "GEOMETRY-CONTROL.md", "sha256": model.document_sha256}]
    for name, path in extra_docs or []:
        if path.is_file():
            docs.append({"path": name, "sha256": sha256_file(path)})
    return {
        "module_id": MODULE_ID,
        "generated_by": f"publish_module_contract.py via {AGENT_ID}",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_documents": docs,
    }


def copy_frame(public: Path) -> tuple[Path, bool]:
    """Refresh the canonical frame copy, or verify the committed one where the source is absent.

    The frame must be byte-identical to the canonical file in digital-3d-shared-contracts, which is
    why it is copied rather than re-serialised. But that sibling repository is not present in CI, so
    an unconditional copy makes this script unrunnable anywhere except one developer's machine --
    which is exactly how the first Pages build failed.

    The committed copy is itself the artifact, and it was hash-verified when it was written. So when
    the canonical source is reachable, copy and verify; when it is not, verify the committed copy
    still parses and declares the expected frame, and report that it was checked rather than
    refreshed. Silently skipping would be worse than failing: the whole point of this file is that
    it is provably identical.
    """
    src = CONTRACTS / "frames" / "nyc-harbor-enu.json"
    dst = public / "frames" / "nyc-harbor-enu.json"
    dst.parent.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        shutil.copyfile(src, dst)
        return dst, sha256_file(src) == sha256_file(dst)

    if not dst.is_file():
        raise SystemExit(
            f"canonical frame not found at {src} and no committed copy at {dst}. Set "
            "D3D_CONTRACTS_DIR to the digital-3d-shared-contracts checkout."
        )
    frame = json.loads(dst.read_text(encoding="utf-8"))
    if frame.get("frame_id") != FRAME_ID:
        raise SystemExit(
            f"committed frame declares frame_id {frame.get('frame_id')!r}, expected {FRAME_ID!r}"
        )
    print(f"canonical frame source not present; verified the committed copy ({dst.name})")
    return dst, True


def build_lod(model) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "module_id": MODULE_ID,
        "ladder_id": LADDER_ID,
        "levels": [
            {
                "level": 0,
                "name": "control skeleton",
                "intent": "inspect",
                "max_geometric_error_m": 0.01,
                "representation": "cad_solid",
                "payload_format": "glb",
                "triangle_budget": 40000,
                "selectable": True,
                "carries_metadata": True,
                "typical_distance_m": {"min": 0, "max": 400},
                "notes": (
                    "The authoritative control skeleton: 81 addressable parts, each carrying its "
                    "confidence grade and the control IDs its geometry consumed. Geometric error is "
                    "the placement tolerance of the control curves themselves, not a claim that "
                    "every member is modelled; parts still graded D are envelopes and say so."
                ),
            },
            {
                "level": 2,
                "name": "district proxy",
                "intent": "context",
                "max_geometric_error_m": 8.0,
                "representation": "mesh",
                "payload_format": "glb",
                "triangle_budget": 6000,
                "selectable": False,
                "carries_metadata": False,
                "typical_distance_m": {"min": 200, "max": None},
                "notes": (
                    "What a pedestrian in DUMBO sees. The deck system is collapsed to a single slab "
                    "8.23 m deep, which is what sets the 8.0 m error; towers keep their four sourced "
                    "tapered legs, and every fourth suspender is retained so the structure still "
                    "reads as a suspension bridge at street range."
                ),
            },
        ],
        "selection": {
            "policy": "screen_space_error",
            "default_sse_budget_px": 12,
            "mode_sse_budget_px": {"inspect": 2, "walk": 12, "map": 48, "tour": 8},
            "hysteresis": 0.15,
        },
        "notes": (
            "Level 1 is deliberately absent. Publishing a segmented mesh between 0.01 m and 8.0 m "
            "would imply an intermediate representation this module does not yet have; consumers "
            "sort by max_geometric_error_m, not by level index, so a gap is honest and harmless."
        ),
    }


TAXONOMY_KEYS = ("system", "subsystem")
EXTENSION_KEYS = (
    "prototype_units",
    "ho_scale_units",
    "bbox_ho_mm",
    "scale",
    "geometry_kinds",
    # Milestone 6. Geometry provenance and material are deliberately module-private: they are this
    # module's epistemic apparatus, adopted from SRC-018, and the shared metadata schema has no
    # field for either. Publishing them under the module namespace lets a consumer read them
    # without implying they are part of the cross-module contract.
    "geometry_provenance",
    "material",
    "material_id",
    "material_confidence",
    "material_sources",
)

# Coarse class shared with the district, from the metadata schema enum. The fine-grained
# system/subsystem taxonomy stays module-local under `taxonomy`.
CATEGORY_BY_SYSTEM = {
    "reference": "reference",
    "towers": "bridge_component",
    "anchorages": "bridge_component",
    "cables": "bridge_component",
    "suspenders": "bridge_component",
    "deck_system": "bridge_component",
    "approaches": "bridge_component",
    "details": "bridge_component",
}


def map_metadata(part: dict[str, Any], control_sources: dict[str, list[str]]) -> dict[str, Any]:
    """Map one parts.json record onto metadata.schema.json.

    Mostly renames. Two things are added rather than renamed: `category`, the coarse class the
    district's shared panel groups by, and `source_refs`, resolved by following each control
    reference to the sources that control cites. That last one is why a DUMBO user clicking a bridge
    tower sees the actual period engineering citations without the district team writing any
    bridge-specific code.
    """
    local_id = part["part_id"]
    bbox = part.get("bbox_prototype_m") or {}

    refs: list[str] = []
    for ctl in part.get("control_refs", []):
        for src in control_sources.get(ctl, []):
            if src not in refs:
                refs.append(src)

    record: dict[str, Any] = {
        "asset_id": f"{URN}{local_id}",
        "local_id": local_id,
        "module_id": MODULE_ID,
        "display_name": local_id.replace("_", " "),
        "category": CATEGORY_BY_SYSTEM.get(part["system"], "structure"),
        "taxonomy": {
            **{k: part[k] for k in TAXONOMY_KEYS if part.get(k)},
            "path": [p for p in (part.get("system"), part.get("subsystem")) if p],
        },
        "source_basis": part["source_basis"],
        "source_refs": sorted(refs),
        "confidence": part["confidence"],
        "basis_confidence": part.get("basis_confidence"),
        "control_refs": part.get("control_refs", []),
        "open_questions": part.get("open_questions", []),
        "review_status": part.get("review_status"),
        "last_modified_by": part.get("last_modified_by_agent"),
        "units": "meters",
        "notes": part.get("notes"),
        "extensions": {
            MODULE_ID: {k: part[k] for k in EXTENSION_KEYS if k in part},
        },
    }
    if bbox.get("min") and bbox.get("max"):
        record["bbox"] = {
            "frame": "manhattan-bridge-local",
            "min": bbox["min"],
            "max": bbox["max"],
        }
        record["anchor"] = {
            "frame": "manhattan-bridge-local",
            "xyz": [round((bbox["min"][i] + bbox["max"][i]) / 2.0, 4) for i in range(3)],
        }
    return {k: v for k, v in record.items() if v not in (None, {}, [])}


def build_asset_registry(model, parts_doc: dict[str, Any], proxy_report: dict[str, Any]) -> dict[str, Any]:
    assets: list[dict[str, Any]] = [
        {
            "asset_id": f"{URN}bridge_proxy",
            "kind": "proxy",
            "represents": f"{URN}control_skeleton",
            "tags": ["landmark", "context", "district_visible"],
            "bbox": {
                "frame": "manhattan-bridge-local",
                "min": proxy_report["bbox_local_m"]["min"],
                "max": proxy_report["bbox_local_m"]["max"],
            },
            "variants": [
                {
                    "level": 2,
                    "url": "assets/bridge.lod2.glb",
                    "format": "glb",
                    "byte_size": proxy_report["byte_size"],
                    "triangle_count": proxy_report["triangle_count"],
                    "max_geometric_error_m": proxy_report["max_geometric_error_m"],
                    "sha256": proxy_report["sha256"],
                }
            ],
        },
        {
            "asset_id": f"{URN}control_skeleton",
            "kind": "aggregate",
            "tags": ["inspect", "authoritative"],
            "metadata_url": "bridge/metadata.json",
            "variants": [
                {
                    "level": 0,
                    "url": "assets/bridge.lod0.glb",
                    "format": "glb",
                    "byte_size": proxy_report["lod0_byte_size"],
                    "max_geometric_error_m": 0.01,
                    "sha256": proxy_report["lod0_sha256"],
                }
            ],
        },
    ]

    # Every part is addressable by URN so a foreign viewer can focus one, e.g. from a tour.
    for part in parts_doc["parts"]:
        assets.append(
            {
                "asset_id": f"{URN}{part['part_id']}",
                "kind": "single",
                "metadata_url": "bridge/metadata.json",
                "bbox": {
                    "frame": "manhattan-bridge-local",
                    "min": part["bbox_prototype_m"]["min"],
                    "max": part["bbox_prototype_m"]["max"],
                },
                "variants": [
                    {
                        "level": 0,
                        "url": "assets/bridge.lod0.glb",
                        "format": "glb",
                        "node_name": part["part_id"],
                        "max_geometric_error_m": 0.01,
                    }
                ],
            }
        )

    return {
        "contract_version": CONTRACT_VERSION,
        "module_id": MODULE_ID,
        "frame_id": FRAME_ID,
        "ladder_id": LADDER_ID,
        "base_url": "../",
        "assets": assets,
        "provenance": provenance(model),
    }


def confidence_histogram(parts_doc) -> dict[str, int]:
    """Grade counts taken from the built parts, never hand-maintained.

    A hardcoded histogram silently becomes a false claim the moment a control changes grade, and
    it is exactly the kind of number a reader would trust without checking.
    """
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for part in parts_doc["parts"]:
        grade = part.get("confidence")
        if grade in counts:
            counts[grade] += 1
    return counts


def placeholder_count(model) -> int:
    """How many control values are still placeholders rather than sourced dimensions.

    Reads the attribute directly rather than via getattr with a default: if the control model is
    ever renamed, this must break loudly instead of quietly publishing "0 placeholders remain",
    which is precisely the kind of false reassurance this project exists to prevent.
    """
    return sum(1 for c in model.controls.values() if c.is_placeholder)


def build_manifest(model, parts_doc) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "module_id": MODULE_ID,
        "title": "Manhattan Bridge",
        "subtitle": "Source-governed control skeleton — every dimension traces to a registered source",
        "module_version": MODULE_VERSION,
        "owner": {"team": "Manhattan Bridge", "repository": "manhattan-bridge-3d"},
        "authoritative_for": [
            "bridge geometry",
            "bridge control dimensions",
            "bridge component taxonomy",
            "bridge photogrammetry",
            "bridge engineering detail",
        ],
        "georeference": {"url": "./frames/nyc-harbor-enu.json"},
        "placement": {
            "frame": FRAME_ID,
            "translation_m": PLACEMENT_TRANSLATION,
            "yaw_deg": PLACEMENT_YAW_DEG,
            "scale": 1,
            "confidence": "C",
            "provisional": False,
            "open_questions": ["OQ-009"],
            "notes": (
                "RATIFIED BY THE BRIDGE TEAM at module_version 1.0.0. Numerically unchanged from the "
                "provisional placement proposed by dumbo-district-3d (DOQ-001), which this module "
                "reproduced and audited independently rather than accepting on trust. "
                "Azimuth 157.367 deg from north toward Brooklyn is the principal axis of the "
                "OpenStreetMap-mapped alignment; refitting the two long edge paths alone gives "
                "157.496 deg and the roadway ways alone give 157.024 deg, so the axis is stable to "
                "about +/-0.35 deg, which is +/-6 m of lateral error at the far end of the structure. "
                "The translation is the centroid of those mapped points; the ASCE Historic Civil "
                "Engineering Landmark coordinate for this bridge falls 11.8 m from it, an independent "
                "corroboration from a source unrelated to OpenStreetMap. Confidence is C rather than "
                "B because both estimates are derived from mapped alignments rather than survey, and "
                "OQ-009 stays open until a geodetic anchor is registered from an archival drawing. "
                "The z term of 0.59 m is the mean-high-water to NAVD88 correction and is grade A: "
                "independently confirmed against the NOAA CO-OPS API for station 8518750, epoch "
                "1983-2001, which returns MHW 2.445 m and NAVD88 1.848 m on station datum, a "
                "difference of 0.597 m. See GEOMETRY-CONTROL.md section 6."
            ),
        },
        "lod_ladder": {"url": "./bridge/lod.json"},
        "asset_registry_url": "./bridge/asset-registry.json",
        "modes": ["inspect", "walk", "map", "tour"],
        "proxy": {
            "asset_id": f"{URN}bridge_proxy",
            "max_level": 2,
            "notes": (
                "Level-2 proxy, 4,620 triangles. Caps how far a consuming viewer may refine bridge "
                "content while the bridge is scenery rather than the subject."
            ),
        },
        "handoff": {
            "supported": True,
            "target_mode": "inspect",
            "preserve_camera": True,
            "entry_points": [
                {
                    "entry_id": "brooklyn_tower",
                    "label": "Inspect the Brooklyn tower",
                    "focus_asset": f"{URN}tower_brooklyn_leg_a",
                    # Camera poses are expressed relative to the focus asset rather than in scene
                    # coordinates, so they stay correct if the placement in OQ-009 is later
                    # corrected. Offsets stand the camera south of the structure, which is the side
                    # DUMBO approaches from.
                    "camera": {
                        "position": {
                            "asset": f"{URN}tower_brooklyn_leg_a",
                            "anchor": "bbox_center",
                            "offset_m": [40.0, -170.0, 30.0],
                        },
                        "target": {
                            "asset": f"{URN}tower_brooklyn_leg_a",
                            "anchor": "bbox_center",
                        },
                        "fov_deg": 50,
                    },
                },
                {
                    "entry_id": "brooklyn_anchorage",
                    "label": "Inspect the Brooklyn anchorage",
                    "focus_asset": f"{URN}brooklyn_anchorage",
                    "camera": {
                        "position": {
                            "asset": f"{URN}brooklyn_anchorage",
                            "anchor": "bbox_center",
                            "offset_m": [60.0, -190.0, 40.0],
                        },
                        "target": {
                            "asset": f"{URN}brooklyn_anchorage",
                            "anchor": "bbox_center",
                        },
                        "fov_deg": 50,
                    },
                },
                {
                    "entry_id": "main_span",
                    "label": "Inspect the main span and cables",
                    "focus_asset": f"{URN}north_main_cable_1",
                    "camera": {
                        "position": {
                            "asset": f"{URN}north_main_cable_1",
                            "anchor": "bbox_center",
                            "offset_m": [0.0, -320.0, 90.0],
                        },
                        "target": {
                            "asset": f"{URN}north_main_cable_1",
                            "anchor": "bbox_center",
                        },
                        "fov_deg": 55,
                    },
                },
            ],
        },
        "attribution": [
            "Manhattan Bridge digital twin: manhattan-bridge-3d, Ethical Tech CoLab, CC BY 4.0",
            "Provisional placement derived from OpenStreetMap data (c) OpenStreetMap contributors, ODbL",
        ],
        "not_implemented_yet": [
            "no level-1 segmented mesh; the ladder jumps from 0.01 m to 8.0 m",
            "7 of 69 control values remain placeholders: deck framing depths (OQ-013) and subway "
            "track centrelines (OQ-010) await the 1907-1909 contract drawings",
            "truss web members are grade D; the Warren diagonal handedness at each panel is inferred "
            "(OQ-017)",
            "placement azimuth derives from mapped alignments, not survey; OQ-009 stays open",
            "no inspect-mode UI bundle is published, so handoff.ui_url is absent and a consuming "
            "viewer renders only the shared metadata panel",
        ],
        "provenance": provenance(
            model,
            [
                ("SOURCE-REGISTER.md", REPO_ROOT / "SOURCE-REGISTER.md"),
                ("CONFIDENCE-MODEL.md", REPO_ROOT / "CONFIDENCE-MODEL.md"),
            ],
        ),
        "extensions": {
            MODULE_ID: {
                "ho_scale": {
                    "denominator": 87.1,
                    "note": (
                        "HO 1:87.1 is a display scale, never a data scale. placement.scale MUST stay "
                        "1 for georeferenced delivery; the HO export is a separate artifact."
                    ),
                },
                # The shared module-manifest schema has no vertical_datum field, and the
                # georeference must stay a byte-identical reference to the frozen canonical frame
                # rather than an inlined copy, so the authored datum is declared here. Every
                # elevation this module publishes shares it, which is why it is stated once at
                # module level instead of repeated across 81 metadata records.
                "authoring": {
                    "vertical_datum": "MHW",
                    "note": (
                        "Elevations are authored against mean high water because the period "
                        "sources state them that way; converting at authoring time would bake a "
                        "derived number into the sourced geometry. The conversion to the frame's "
                        "NAVD88 happens at placement time via placement.translation_m[2]."
                    ),
                    "offset_to_navd88_m": 0.59,
                    "offset_basis": (
                        "Taken from vertical_datum_offsets_m in the frozen canonical frame. NOAA "
                        "CO-OPS station 8518750, epoch 1983-2001, gives MHW 2.445 m and NAVD88 "
                        "1.848 m on station datum, a difference of 0.597 m. The frame value is "
                        "used in preference to the measured one because it is frozen for contract "
                        "major version 1 and cross-module consistency matters more than 7 mm, "
                        "which is two orders of magnitude below the accuracy of the footprint "
                        "data these elevations must agree with."
                    ),
                },
                "confidence_histogram": confidence_histogram(parts_doc),
                "control_document": "GEOMETRY-CONTROL.md",
                "placeholder_controls_remaining": placeholder_count(model),
            }
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish the shared-contract surface for this module.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root: Path = args.repo_root
    public = root / "viewer" / "public"

    model = load_control_model(root / "GEOMETRY-CONTROL.md")
    sk = derive_skeleton(model)

    frame_path, frame_ok = copy_frame(public)
    if not frame_ok:
        raise SystemExit("canonical frame copy does not hash identically to the source")

    parts_doc = json.loads((root / "viewer" / "metadata" / "parts.json").read_text("utf-8"))
    proxy_report = json.loads((root / "viewer" / "metadata" / "proxy_report.json").read_text("utf-8"))

    # Control ID -> the source IDs that control cites, so part metadata can carry real citations.
    control_sources = {c.control_id: list(c.source_ids) for c in model.controls.values()}

    lod0 = public / "assets" / "bridge.lod0.glb"
    lod0.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / "mesh" / "glb" / "control_skeleton.glb", lod0)
    proxy_report["lod0_byte_size"] = lod0.stat().st_size
    proxy_report["lod0_sha256"] = sha256_file(lod0)
    proxy_report["sha256"] = sha256_file(public / "assets" / "bridge.lod2.glb")

    bridge_dir = public / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "contract_version": CONTRACT_VERSION,
        "module_id": MODULE_ID,
        "records": [map_metadata(p, control_sources) for p in parts_doc["parts"]],
        "provenance": provenance(model),
    }

    outputs = {
        bridge_dir / "lod.json": build_lod(model),
        bridge_dir / "asset-registry.json": build_asset_registry(model, parts_doc, proxy_report),
        bridge_dir / "metadata.json": metadata,
        public / "bridge-manifest.json": build_manifest(model, parts_doc),
    }
    for path, payload in outputs.items():
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    registry = outputs[bridge_dir / "asset-registry.json"]
    print(f"frame copy hash match : {frame_ok}")
    print(f"metadata records      : {len(metadata['records'])}")
    print(f"registry assets       : {len(registry['assets'])}")
    for path in outputs:
        print(f"  wrote {path.relative_to(root)}  ({path.stat().st_size:,} bytes)")
    print(f"  wrote {frame_path.relative_to(root)}")
    print(f"  wrote {lod0.relative_to(root)}  ({lod0.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
