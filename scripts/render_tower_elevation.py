"""Render an orthographic transverse elevation of one tower straight from the exported GLB.

Not a substitute for the viewer. It exists because verifying tower detail through a browser harness
proved unreliable -- wheel-zoom hangs, and the harness window resizes itself -- and because reading
the *exported* file is a stronger check than reading the scene the viewer happens to build. If the
arch is missing from the GLB, no amount of viewer inspection would reveal that.

Draws every triangle whose part lies within a window around the tower, projected onto the X-Z plane,
so the result is directly comparable with SRC-018's photograph.

    python scripts/render_tower_elevation.py
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install pillow")

REPO = Path(__file__).resolve().parents[1]
GLB = REPO / "mesh" / "glb" / "control_skeleton.glb"
OUT = REPO / "viewer" / "metadata" / "tower_elevation.png"

# Manhattan tower centreline, from CTL-005 main_span / 2.
TOWER_X = -224.0
HALF_WINDOW = 24.0
Z_LO, Z_HI = -20.0, 115.0
WIDTH, HEIGHT = 900, 1400

INTEREST = ("tower_manhattan",)


def read_glb(path: Path):
    data = path.read_bytes()
    total = struct.unpack("<I", data[8:12])[0]
    offset, chunks = 12, {}
    while offset < total:
        length, kind = struct.unpack("<II", data[offset : offset + 8])
        offset += 8
        chunks[kind] = data[offset : offset + length]
        offset += length
    return json.loads(chunks[0x4E4F534A]), chunks[0x004E4942]


def main() -> int:
    gltf, blob = read_glb(GLB)
    comp = {5121: ("<B", 1), 5123: ("<H", 2), 5125: ("<I", 4)}

    def accessor(idx: int):
        acc = gltf["accessors"][idx]
        view = gltf["bufferViews"][acc["bufferView"]]
        start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
        if acc["type"] == "VEC3":
            return [struct.unpack_from("<3f", blob, start + i * 12) for i in range(acc["count"])]
        fmt, size = comp[acc["componentType"]]
        return [struct.unpack_from(fmt, blob, start + i * size)[0] for i in range(acc["count"])]

    img = Image.new("RGB", (WIDTH, HEIGHT), (232, 236, 240))
    draw = ImageDraw.Draw(img)

    def project(p):
        # The GLB root node carries a -90 deg X rotation, so raw accessor positions are still in
        # the authoring frame: x along the bridge, y transverse, z up.
        #
        # The arch spans BETWEEN the legs, and the legs are spread transversely (all four share one
        # x). So the view that shows an arch is the one looking along the bridge axis: y against z.
        # An earlier version plotted x against z, which looks at the tower edge-on and collapses all
        # four columns onto each other -- exactly why the first render showed a featureless slab.
        sy, sz = p[1], p[2]
        u = WIDTH / 2 + sy / HALF_WINDOW * (WIDTH / 2)
        v = HEIGHT - (sz - Z_LO) / (Z_HI - Z_LO) * HEIGHT
        return u, v

    drawn = 0
    for node in gltf["nodes"]:
        name = node.get("name", "")
        if "mesh" not in node or not any(k in name for k in INTEREST):
            continue
        colour = (150, 40, 40) if "arch" in name else (70, 80, 95) if "finial" in name else (120, 130, 145)
        mesh = gltf["meshes"][node["mesh"]]
        for prim in mesh["primitives"]:
            pos = accessor(prim["attributes"]["POSITION"])
            idx = list(accessor(prim["indices"])) if "indices" in prim else list(range(len(pos)))
            for i in range(0, len(idx) - 2, 3):
                tri = [pos[idx[i]], pos[idx[i + 1]], pos[idx[i + 2]]]
                if all(abs(p[0] - TOWER_X) > HALF_WINDOW for p in tri):
                    continue
                draw.polygon([project(p) for p in tri], fill=colour)
                drawn += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"drew {drawn:,} triangles from {GLB.name}")
    print(f"wrote {OUT.relative_to(REPO)}")
    print("arches in red, finials in dark blue-grey, rest of the tower in grey")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
