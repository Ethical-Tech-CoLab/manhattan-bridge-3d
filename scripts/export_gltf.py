"""Minimal, dependency-free glTF 2.0 / GLB writer.

Milestone 1 deliberately avoids third-party 3D libraries so that the authoritative export path has no
binary dependencies and can be audited line by line. The writer supports exactly what the control
skeleton needs:

* TRIANGLES primitives with POSITION and NORMAL,
* LINES primitives with POSITION,
* per-node ``extras`` (this is how part metadata reaches the browser),
* unlit materials for line work (``KHR_materials_unlit``),
* a single interleaved-free binary buffer packed into a ``.glb`` container.

Authoring coordinates are Z-up (see GEOMETRY-CONTROL.md section 1). glTF is Y-up, so the scene root
node carries a -90 degree rotation about X. Vertex data therefore stays in prototype bridge
coordinates and remains directly comparable to the control tables.

Usage as a library::

    from export_gltf import GltfBuilder, MODE_LINES, MODE_TRIANGLES
    b = GltfBuilder(generator="build_control_skeleton.py@1.0.0")
    mat = b.add_material("cable", (0.9, 0.7, 0.2, 1.0), unlit=True)
    mesh = b.add_mesh("cable_mesh", [b.line_primitive(points, mat)])
    node = b.add_node("north_main_cable_1", mesh=mesh, extras={...})
    b.add_to_root(node)
    b.save_glb("out.glb")
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path
from typing import Any, Iterable, Sequence

COMPONENT_FLOAT = 5126
COMPONENT_UINT32 = 5125
TARGET_ARRAY_BUFFER = 34962
TARGET_ELEMENT_ARRAY_BUFFER = 34963

MODE_LINES = 1
MODE_TRIANGLES = 4

# -90 deg about X: converts an authoring Z-up frame into the glTF Y-up frame.
ZUP_TO_YUP_QUAT = [-0.7071067811865476, 0.0, 0.0, 0.7071067811865476]

Vec3 = Sequence[float]


class GltfBuilder:
    """Accumulates nodes, meshes and buffer data, then serialises a ``.glb``."""

    def __init__(self, generator: str, scale: float = 1.0, copyright_text: str | None = None) -> None:
        self.generator = generator
        self.scale = float(scale)
        self.copyright_text = copyright_text
        self._buffer = bytearray()
        self._buffer_views: list[dict[str, Any]] = []
        self._accessors: list[dict[str, Any]] = []
        self._meshes: list[dict[str, Any]] = []
        self._materials: list[dict[str, Any]] = []
        self._material_index: dict[str, int] = {}
        self._nodes: list[dict[str, Any]] = []
        self._uses_unlit = False
        self._root = self.add_node("root", rotation=ZUP_TO_YUP_QUAT)

    # ------------------------------------------------------------------ buffers

    def _align(self, boundary: int = 4, pad_byte: int = 0) -> None:
        while len(self._buffer) % boundary:
            self._buffer.append(pad_byte)

    def _add_buffer_view(self, data: bytes, target: int | None) -> int:
        self._align()
        offset = len(self._buffer)
        self._buffer.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        self._buffer_views.append(view)
        return len(self._buffer_views) - 1

    def _add_vec3_accessor(self, values: Iterable[Vec3], apply_scale: bool) -> int:
        rows = [tuple(float(c) for c in v) for v in values]
        if not rows:
            raise ValueError("cannot build an accessor from zero vertices")
        if apply_scale and self.scale != 1.0:
            rows = [(x * self.scale, y * self.scale, z * self.scale) for x, y, z in rows]
        blob = bytearray()
        for row in rows:
            blob.extend(struct.pack("<3f", *row))
        view = self._add_buffer_view(bytes(blob), TARGET_ARRAY_BUFFER)
        mins = [min(r[i] for r in rows) for i in range(3)]
        maxs = [max(r[i] for r in rows) for i in range(3)]
        self._accessors.append(
            {
                "bufferView": view,
                "componentType": COMPONENT_FLOAT,
                "count": len(rows),
                "type": "VEC3",
                "min": mins,
                "max": maxs,
            }
        )
        return len(self._accessors) - 1

    def _add_index_accessor(self, indices: Sequence[int]) -> int:
        if not indices:
            raise ValueError("cannot build an index accessor from zero indices")
        blob = bytearray()
        for i in indices:
            blob.extend(struct.pack("<I", int(i)))
        view = self._add_buffer_view(bytes(blob), TARGET_ELEMENT_ARRAY_BUFFER)
        self._accessors.append(
            {
                "bufferView": view,
                "componentType": COMPONENT_UINT32,
                "count": len(indices),
                "type": "SCALAR",
                "min": [int(min(indices))],
                "max": [int(max(indices))],
            }
        )
        return len(self._accessors) - 1

    # ---------------------------------------------------------------- materials

    def add_material(
        self,
        name: str,
        color: Sequence[float],
        unlit: bool = False,
        metallic: float = 0.0,
        roughness: float = 0.85,
        double_sided: bool = True,
    ) -> int:
        """Return the index of a material, creating it on first use. Deduplicated by name."""
        if name in self._material_index:
            return self._material_index[name]
        rgba = [float(c) for c in color]
        if len(rgba) == 3:
            rgba.append(1.0)
        material: dict[str, Any] = {
            "name": name,
            "doubleSided": bool(double_sided),
            "pbrMetallicRoughness": {
                "baseColorFactor": rgba,
                "metallicFactor": float(metallic),
                "roughnessFactor": float(roughness),
            },
        }
        if rgba[3] < 1.0:
            material["alphaMode"] = "BLEND"
        if unlit:
            material["extensions"] = {"KHR_materials_unlit": {}}
            self._uses_unlit = True
        self._materials.append(material)
        index = len(self._materials) - 1
        self._material_index[name] = index
        return index

    # --------------------------------------------------------------- primitives

    def line_primitive(self, segments: Sequence[Sequence[Vec3]], material: int) -> dict[str, Any]:
        """``segments`` is a sequence of (start, end) point pairs."""
        positions: list[Vec3] = []
        indices: list[int] = []
        for start, end in segments:
            base = len(positions)
            positions.append(start)
            positions.append(end)
            indices.extend((base, base + 1))
        return {
            "mode": MODE_LINES,
            "positions": positions,
            "normals": None,
            "indices": indices,
            "material": material,
        }

    def polyline_primitive(self, points: Sequence[Vec3], material: int) -> dict[str, Any]:
        if len(points) < 2:
            raise ValueError("a polyline needs at least two points")
        segments = [(points[i], points[i + 1]) for i in range(len(points) - 1)]
        return self.line_primitive(segments, material)

    def triangle_primitive(
        self,
        positions: Sequence[Vec3],
        normals: Sequence[Vec3],
        indices: Sequence[int],
        material: int,
    ) -> dict[str, Any]:
        return {
            "mode": MODE_TRIANGLES,
            "positions": list(positions),
            "normals": list(normals),
            "indices": list(indices),
            "material": material,
        }

    def add_mesh(self, name: str, primitives: Sequence[dict[str, Any]]) -> int:
        gltf_primitives = []
        for prim in primitives:
            attributes = {"POSITION": self._add_vec3_accessor(prim["positions"], apply_scale=True)}
            if prim.get("normals"):
                attributes["NORMAL"] = self._add_vec3_accessor(prim["normals"], apply_scale=False)
            gltf_primitives.append(
                {
                    "attributes": attributes,
                    "indices": self._add_index_accessor(prim["indices"]),
                    "material": prim["material"],
                    "mode": prim["mode"],
                }
            )
        self._meshes.append({"name": name, "primitives": gltf_primitives})
        return len(self._meshes) - 1

    # -------------------------------------------------------------------- nodes

    def add_node(
        self,
        name: str,
        mesh: int | None = None,
        children: Sequence[int] | None = None,
        extras: dict[str, Any] | None = None,
        rotation: Sequence[float] | None = None,
    ) -> int:
        node: dict[str, Any] = {"name": name}
        if mesh is not None:
            node["mesh"] = mesh
        if children:
            node["children"] = list(children)
        if extras:
            node["extras"] = extras
        if rotation:
            node["rotation"] = list(rotation)
        self._nodes.append(node)
        return len(self._nodes) - 1

    def add_child(self, parent: int, child: int) -> None:
        self._nodes[parent].setdefault("children", []).append(child)

    def add_to_root(self, node: int) -> None:
        self.add_child(self._root, node)

    @property
    def root(self) -> int:
        return self._root

    def set_root_extras(self, extras: dict[str, Any]) -> None:
        self._nodes[self._root]["extras"] = extras

    def set_root_name(self, name: str) -> None:
        self._nodes[self._root]["name"] = name

    # ------------------------------------------------------------- serialisation

    def to_gltf_dict(self) -> dict[str, Any]:
        asset: dict[str, Any] = {"version": "2.0", "generator": self.generator}
        if self.copyright_text:
            asset["copyright"] = self.copyright_text
        gltf: dict[str, Any] = {
            "asset": asset,
            "scene": 0,
            "scenes": [{"nodes": [self._root]}],
            "nodes": self._nodes,
            "meshes": self._meshes,
            "materials": self._materials,
            "accessors": self._accessors,
            "bufferViews": self._buffer_views,
            "buffers": [{"byteLength": len(self._buffer)}],
        }
        if self._uses_unlit:
            gltf["extensionsUsed"] = ["KHR_materials_unlit"]
        return gltf

    def save_glb(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self._align()  # final BIN chunk length must be a multiple of 4
        bin_chunk = bytes(self._buffer)
        json_bytes = json.dumps(self.to_gltf_dict(), separators=(",", ":")).encode("utf-8")
        while len(json_bytes) % 4:
            json_bytes += b" "

        total = 12 + 8 + len(json_bytes) + 8 + len(bin_chunk)
        with path.open("wb") as fh:
            fh.write(struct.pack("<III", 0x46546C67, 2, total))
            fh.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
            fh.write(json_bytes)
            fh.write(struct.pack("<II", len(bin_chunk), 0x004E4942))
            fh.write(bin_chunk)
        return path

    def save_gltf(self, path: str | Path) -> Path:
        """Write a .gltf plus a sibling .bin. Used for human-readable review of the export."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        bin_path = path.with_suffix(".bin")
        gltf = self.to_gltf_dict()
        gltf["buffers"][0]["uri"] = bin_path.name
        bin_path.write_bytes(bytes(self._buffer))
        path.write_text(json.dumps(gltf, indent=2), encoding="utf-8")
        return path


# ----------------------------------------------------------------- mesh helpers

_BOX_FACES = (
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 1, 0), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
)


def box_mesh_data(bmin: Vec3, bmax: Vec3) -> tuple[list[Vec3], list[Vec3], list[int]]:
    """Axis-aligned box as 24 vertices / 12 triangles with flat per-face normals."""
    positions: list[Vec3] = []
    normals: list[Vec3] = []
    indices: list[int] = []
    for normal, corners in _BOX_FACES:
        base = len(positions)
        for cx, cy, cz in corners:
            positions.append(
                (
                    bmin[0] + (bmax[0] - bmin[0]) * cx,
                    bmin[1] + (bmax[1] - bmin[1]) * cy,
                    bmin[2] + (bmax[2] - bmin[2]) * cz,
                )
            )
            normals.append(normal)
        indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
    return positions, normals, indices


def quad_mesh_data(corners: Sequence[Vec3]) -> tuple[list[Vec3], list[Vec3], list[int]]:
    """Planar quad from four corners in order, with a computed face normal."""
    if len(corners) != 4:
        raise ValueError("a quad needs exactly four corners")
    p0, p1, p2 = corners[0], corners[1], corners[2]
    u = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    v = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    length = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 or 1.0
    normal = (n[0] / length, n[1] / length, n[2] / length)
    return list(corners), [normal] * 4, [0, 1, 2, 0, 2, 3]


_PRISM_FACES = (
    (0, 1, 2, 3),  # bottom, corners given counter-clockwise seen from below
    (7, 6, 5, 4),  # top
    (0, 4, 5, 1),
    (1, 5, 6, 2),
    (2, 6, 7, 3),
    (3, 7, 4, 0),
)


def prism_mesh_data(
    bottom: Sequence[Vec3], top: Sequence[Vec3]
) -> tuple[list[Vec3], list[Vec3], list[int]]:
    """Solid between two four-corner rings, e.g. a tapered tower leg.

    ``bottom`` and ``top`` are each four points in matching order. Faces carry flat normals.
    """
    if len(bottom) != 4 or len(top) != 4:
        raise ValueError("a prism needs four bottom and four top corners")
    ring = [tuple(map(float, p)) for p in bottom] + [tuple(map(float, p)) for p in top]
    positions: list[Vec3] = []
    normals: list[Vec3] = []
    indices: list[int] = []
    for face in _PRISM_FACES:
        pts = [ring[i] for i in face]
        base = len(positions)
        p0, p1, p2 = pts[0], pts[1], pts[2]
        u = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        v = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        length = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 or 1.0
        normal = (n[0] / length, n[1] / length, n[2] / length)
        positions.extend(pts)
        normals.extend([normal] * 4)
        indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
    return positions, normals, indices


def tube_mesh_data(
    points: Sequence[Vec3], radius: float, sides: int = 8
) -> tuple[list[Vec3], list[Vec3], list[int]]:
    """Swept tube of constant radius along a polyline.

    Used for members whose real diameter is a sourced dimension, such as the main cables and the
    stiffening truss chords, so that the render shows true thickness rather than a hairline.
    """
    if len(points) < 2:
        raise ValueError("a tube needs at least two points")
    pts = [tuple(map(float, p)) for p in points]

    def normalise(v: tuple[float, float, float]) -> tuple[float, float, float]:
        length = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5 or 1.0
        return (v[0] / length, v[1] / length, v[2] / length)

    positions: list[Vec3] = []
    normals: list[Vec3] = []
    rings: list[list[int]] = []
    for i, point in enumerate(pts):
        nxt = pts[min(i + 1, len(pts) - 1)]
        prv = pts[max(i - 1, 0)]
        tangent = normalise((nxt[0] - prv[0], nxt[1] - prv[1], nxt[2] - prv[2]))
        # Pick any axis not parallel to the tangent to seed the ring frame.
        seed = (0.0, 1.0, 0.0) if abs(tangent[1]) < 0.9 else (1.0, 0.0, 0.0)
        u = normalise(
            (
                tangent[1] * seed[2] - tangent[2] * seed[1],
                tangent[2] * seed[0] - tangent[0] * seed[2],
                tangent[0] * seed[1] - tangent[1] * seed[0],
            )
        )
        v = normalise(
            (
                tangent[1] * u[2] - tangent[2] * u[1],
                tangent[2] * u[0] - tangent[0] * u[2],
                tangent[0] * u[1] - tangent[1] * u[0],
            )
        )
        ring: list[int] = []
        for k in range(sides):
            angle = 2.0 * math.pi * k / sides
            ca, sa = math.cos(angle), math.sin(angle)
            normal = (u[0] * ca + v[0] * sa, u[1] * ca + v[1] * sa, u[2] * ca + v[2] * sa)
            ring.append(len(positions))
            positions.append(
                (
                    point[0] + normal[0] * radius,
                    point[1] + normal[1] * radius,
                    point[2] + normal[2] * radius,
                )
            )
            normals.append(normal)
        rings.append(ring)

    indices: list[int] = []
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(sides):
            k2 = (k + 1) % sides
            indices.extend((a[k], b[k], b[k2], a[k], b[k2], a[k2]))
    return positions, normals, indices


if __name__ == "__main__":  # pragma: no cover - smoke test only
    b = GltfBuilder(generator="export_gltf.py self-test")
    mat = b.add_material("test", (0.5, 0.5, 0.5, 1.0))
    pos, nrm, idx = box_mesh_data((0, 0, 0), (1, 1, 1))
    mesh = b.add_mesh("box", [b.triangle_primitive(pos, nrm, idx, mat)])
    b.add_to_root(b.add_node("box", mesh=mesh, extras={"part_id": "test_box"}))
    out = b.save_glb(Path(__file__).resolve().parent / "_selftest.glb")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
