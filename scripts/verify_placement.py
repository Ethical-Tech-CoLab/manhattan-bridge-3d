"""Verify the published placement puts the bridge over the district tiles that expect it.

This is the geometric end-to-end check for the shared-contract integration. It does not trust the
placement numbers; it applies them and tests the consequence.

  1. read the proxy GLB back out of the published artifact
  2. undo the glTF Y-up root rotation to recover module-local Z-up coordinates
  3. apply the placement from bridge-manifest.json exactly as the shared kernel would
  4. compare the footprint against the district tiles that name this module's proxy URN in
     `foreign_assets`

A placement can validate against every schema and still be wrong by a hundred metres. Only this
check would notice.

    python scripts/verify_placement.py
"""

from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DISTRICT_TILES = Path(r"c:\Dev\dumbo-district-3d\viewer\public\district\tile-index.json")

PROXY_URN = "urn:d3d:manhattan-bridge:bridge_proxy"


def read_glb_triangles(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    """Every triangle in a GLB, in module-local coordinates.

    The exporter puts the Z-up -> Y-up conversion on the single root node and leaves every child
    node transform-free, so the raw accessor data is already module-local Z-up. Assert that,
    rather than assume it: a future exporter change that bakes transforms into nodes would
    otherwise silently invalidate every number below.
    """
    data = path.read_bytes()
    magic, version, total = struct.unpack("<III", data[:12])
    if magic != 0x46546C67 or version != 2:
        raise SystemExit(f"{path} is not a glTF 2.0 binary")
    offset, chunks = 12, {}
    while offset < total:
        length, kind = struct.unpack("<II", data[offset : offset + 8])
        offset += 8
        chunks[kind] = data[offset : offset + length]
        offset += length
    gltf = json.loads(chunks[0x4E4F534A])
    blob = chunks[0x004E4942]

    roots = gltf["scenes"][gltf.get("scene", 0)]["nodes"]
    if len(roots) != 1:
        raise SystemExit("expected exactly one root node")
    for i, node in enumerate(gltf["nodes"]):
        if i in roots:
            continue
        if any(k in node for k in ("matrix", "translation", "rotation", "scale")):
            raise SystemExit(
                f"node {node.get('name', i)!r} carries a transform; this reader assumes "
                "geometry is pre-baked into module-local coordinates"
            )

    component = {5121: ("<B", 1), 5123: ("<H", 2), 5125: ("<I", 4)}

    def read_accessor(idx: int):
        acc = gltf["accessors"][idx]
        view = gltf["bufferViews"][acc["bufferView"]]
        start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
        if acc["type"] == "VEC3":
            return [struct.unpack_from("<3f", blob, start + i * 12) for i in range(acc["count"])]
        fmt, size = component[acc["componentType"]]
        return [struct.unpack_from(fmt, blob, start + i * size)[0] for i in range(acc["count"])]

    tris = []
    for mesh in gltf["meshes"]:
        for prim in mesh["primitives"]:
            pos = read_accessor(prim["attributes"]["POSITION"])
            idx = read_accessor(prim["indices"]) if "indices" in prim else range(len(pos))
            idx = list(idx)
            for i in range(0, len(idx) - 2, 3):
                tris.append((pos[idx[i]], pos[idx[i + 1]], pos[idx[i + 2]]))
    return tris


def densify(tris, step: float = 4.0):
    """Sample along every triangle edge so coverage does not depend on vertex spacing.

    A proxy mesh is deliberately low-poly: the deck is a handful of long quads, so consecutive
    vertices can be hundreds of metres apart and a 128 m tile can be crossed without containing a
    single vertex. Sampling edges at 4 m removes that blind spot.
    """
    out = []
    for tri in tris:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            length = math.sqrt(dx * dx + dy * dy + dz * dz)
            n = max(1, int(length / step))
            for k in range(n + 1):
                t = k / n
                out.append((a[0] + dx * t, a[1] + dy * t, a[2] + dz * t))
    return out


def main() -> int:
    manifest = json.loads((REPO / "viewer" / "public" / "bridge-manifest.json").read_text("utf-8"))
    placement = manifest["placement"]
    tx, ty, tz = placement["translation_m"]
    yaw = math.radians(placement["yaw_deg"])
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)

    proxy = REPO / "viewer" / "public" / "assets" / "bridge.lod2.glb"
    tris = read_glb_triangles(proxy)
    local_points = densify(tris)
    print(f"proxy triangles       : {len(tris):,}")
    print(f"sampled points (4 m)  : {len(local_points):,}")

    scene: list[tuple[float, float, float]] = []
    for lx, ly, lz in local_points:
        scene.append(
            (
                tx + cos_y * lx - sin_y * ly,
                ty + sin_y * lx + cos_y * ly,
                tz + lz,
            )
        )

    xs = [p[0] for p in scene]
    ys = [p[1] for p in scene]
    zs = [p[2] for p in scene]
    print(f"scene bbox X          : {min(xs):9.1f} .. {max(xs):9.1f}")
    print(f"scene bbox Y          : {min(ys):9.1f} .. {max(ys):9.1f}")
    print(f"scene bbox Z (NAVD88) : {min(zs):9.1f} .. {max(zs):9.1f}")

    index = json.loads(DISTRICT_TILES.read_text("utf-8"))
    expecting = [t for t in index["tiles"] if PROXY_URN in (t.get("foreign_assets") or [])]
    print(f"\ndistrict tiles naming {PROXY_URN}: {len(expecting)}")

    # An axis-aligned box around a 2 km structure skewed 292.6 deg from the axes covers far more
    # ground than the structure does, so AABB-vs-AABB would over-report coverage badly. Test
    # densely sampled surface points instead.
    def covering(tile) -> bool:
        b = tile["bbox"]
        x0, y0 = b["min"][0], b["min"][1]
        x1, y1 = b["max"][0], b["max"][1]
        return any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in scene)

    hit = [t for t in expecting if covering(t)]
    missed = [t for t in expecting if not covering(t)]
    print(f"  the proxy actually occupies     : {len(hit)}")
    print(f"  declared but NOT occupied       : {len(missed)}")
    for t in missed:
        b = t["bbox"]
        print(
            f"    {t['tile_id']}  x[{b['min'][0]:.0f},{b['max'][0]:.0f}] "
            f"y[{b['min'][1]:.0f},{b['max'][1]:.0f}]"
        )

    # The inverse error matters more: a tile the bridge crosses but which does not name the proxy
    # would never stream it, so the bridge would vanish as a visitor walked into that tile.
    undeclared = [
        t
        for t in index["tiles"]
        if PROXY_URN not in (t.get("foreign_assets") or []) and covering(t)
    ]
    print(f"  occupied but NOT declared       : {len(undeclared)}")
    for t in undeclared:
        b = t["bbox"]
        print(
            f"    {t['tile_id']}  x[{b['min'][0]:.0f},{b['max'][0]:.0f}] "
            f"y[{b['min'][1]:.0f},{b['max'][1]:.0f}]  zone={t.get('zone')}"
        )

    # Vertical sanity: the deck should clear the district's ground, and the towers should not be
    # absurd. Compare against the clearance the control document publishes.
    print(f"\nlowest point (caisson underside) : {min(zs):.2f} m NAVD88")
    print(f"highest point (cable at saddle)  : {max(zs):.2f} m NAVD88")
    print(f"MHW->NAVD88 offset applied       : {tz:.2f} m")

    ok = len(missed) == 0 and len(undeclared) == 0
    if ok:
        print("\nPASS: the district's tile declarations match the proxy footprint")
    else:
        # A mismatch here is not necessarily a fault in this module. The placement origin is
        # corroborated to 10.5 m by the ASCE plaque coordinate (SRC-002) in
        # check_corridor_geodetic.py, whereas the declared tile set's principal axis differs from
        # the published azimuth by 40 deg. The evidence points at the tile list, which the
        # district owns. Emit the corrected set so the fix is a copy-paste.
        occupied = sorted(
            t["tile_id"] for t in index["tiles"] if covering(t)
        )
        print("\nDISCREPANCY: the declared tile set does not match the proxy footprint.")
        print("Corrected `foreign_assets` membership, for the district to apply:")
        print(json.dumps(occupied, indent=2))
        out = REPO / "viewer" / "metadata" / "proposed_foreign_assets.json"
        out.write_text(
            json.dumps(
                {
                    "note": (
                        "Tiles actually occupied by urn:d3d:manhattan-bridge:bridge_proxy under "
                        "the placement published in bridge-manifest.json. Proposed correction to "
                        "dumbo-district-3d/viewer/public/district/tile-index.json foreign_assets. "
                        "Owned by dumbo-district; offered, not applied."
                    ),
                    "proxy_urn": PROXY_URN,
                    "declared_by_district": sorted(t["tile_id"] for t in expecting),
                    "occupied_by_proxy": occupied,
                    "declared_but_not_occupied": sorted(t["tile_id"] for t in missed),
                    "occupied_but_not_declared": sorted(t["tile_id"] for t in undeclared),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\nwritten: {out.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
