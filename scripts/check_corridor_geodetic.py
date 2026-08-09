"""Test the district's `foreign_assets` tile list against the placement the district itself published.

This deliberately uses no coordinate that this module invented. There are exactly three inputs:

  1. the placement in bridge-manifest.json (origin and azimuth), proposed by the district
  2. the district's own tile grid and `foreign_assets` declarations
  3. the ASCE landmark plaque coordinate, SRC-002 -- the only independently sourced geodetic
     point on the structure in the register

Anything else -- tower latitudes, portal positions, approach coordinates -- would have to be made
up, and a made-up coordinate cannot verify anything.

    python scripts/check_corridor_geodetic.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DISTRICT_TILES = Path(r"c:\Dev\dumbo-district-3d\viewer\public\district\tile-index.json")
PROXY_URN = "urn:d3d:manhattan-bridge:bridge_proxy"

# SRC-002, ASCE National Historic Civil Engineering Landmark plaque coordinate.
# 40 deg 42' 27.0" N, 73 deg 59' 26.9" W.
ASCE_PLAQUE = (-(73 + 59 / 60 + 26.9 / 3600), 40 + 42 / 60 + 27.0 / 3600)


def geodetic_to_enu(lon: float, lat: float, anchor_lon: float, anchor_lat: float):
    """Local tangent-plane ENU about the frozen anchor, spherical approximation.

    Over the ~2 km of interest the spherical/ellipsoidal difference is a few centimetres, far
    below the +/- 0.61 m accuracy of the underlying footprint data.
    """
    r = 6378137.0
    lat0 = math.radians(anchor_lat)
    return (
        math.radians(lon - anchor_lon) * r * math.cos(lat0),
        math.radians(lat - anchor_lat) * r,
    )


def principal_azimuth(points) -> float:
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points) / n
    syy = sum((p[1] - my) ** 2 for p in points) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points) / n
    theta = 0.5 * math.atan2(2 * sxy, sxx - syy)
    return math.degrees(math.atan2(math.cos(theta), math.sin(theta))) % 180


def main() -> int:
    frame = json.loads(
        (REPO / "viewer" / "public" / "frames" / "nyc-harbor-enu.json").read_text("utf-8")
    )
    alon, alat = frame["anchor"]["lon"], frame["anchor"]["lat"]

    manifest = json.loads((REPO / "viewer" / "public" / "bridge-manifest.json").read_text("utf-8"))
    tx, ty, _ = manifest["placement"]["translation_m"]
    yaw = manifest["placement"]["yaw_deg"]

    # yaw rotates module +X into the scene, so the along-axis unit vector is (cos yaw, sin yaw)
    # and its compass azimuth is 90 - yaw.
    ax, ay = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    azimuth = (90.0 - yaw) % 360

    index = json.loads(DISTRICT_TILES.read_text("utf-8"))
    declared = {t["tile_id"] for t in index["tiles"] if PROXY_URN in (t.get("foreign_assets") or [])}

    def tile_at(x: float, y: float):
        for t in index["tiles"]:
            b = t["bbox"]
            if b["min"][0] <= x <= b["max"][0] and b["min"][1] <= y <= b["max"][1]:
                return t
        return None

    print(f"placement origin   : ({tx:.1f}, {ty:.1f})   yaw {yaw} deg -> axis azimuth {azimuth:.2f} deg")
    px, py = geodetic_to_enu(*ASCE_PLAQUE, alon, alat)
    print(f"ASCE plaque SRC-002: ({px:.1f}, {py:.1f})  -> {math.hypot(px - tx, py - ty):.1f} m from origin")

    print("\nWalking the published axis across the district's own grid.")
    print("s is distance along the axis; s = 0 is the placement origin, positive toward Brooklyn.\n")
    print(f"{'s (m)':>8s} {'east':>9s} {'north':>9s}  tile      declared?")
    walked: dict[str, int] = {}
    for s in range(-1100, 1101, 25):
        x, y = tx + ax * s, ty + ay * s
        t = tile_at(x, y)
        if t is None:
            continue
        walked.setdefault(t["tile_id"], s)
        if s % 200 == 0:
            print(f"{s:8d} {x:9.1f} {y:9.1f}  {t['tile_id']:9s} "
                  f"{'yes' if t['tile_id'] in declared else 'NO'}")

    on_axis = set(walked)
    print(f"\ntiles the published axis crosses : {len(on_axis)}")
    print(f"tiles the district declared      : {len(declared)}")
    print(f"  crossed and declared           : {len(on_axis & declared)}")
    print(f"  crossed but NOT declared       : {sorted(on_axis - declared)}")
    print(f"  declared but NOT crossed       : {sorted(declared - on_axis)}")

    centres = []
    for t in index["tiles"]:
        if t["tile_id"] in declared:
            b = t["bbox"]
            centres.append(((b["min"][0] + b["max"][0]) / 2, (b["min"][1] + b["max"][1]) / 2))
    tile_az = principal_azimuth(centres)
    print(f"\nprincipal azimuth, declared tile set : {tile_az:6.1f} deg (mod 180)")
    print(f"principal azimuth, published axis    : {azimuth % 180:6.1f} deg (mod 180)")
    diff = abs(tile_az - azimuth % 180)
    print(f"disagreement                         : {min(diff, 180 - diff):6.1f} deg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
