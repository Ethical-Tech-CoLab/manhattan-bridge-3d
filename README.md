# Manhattan Bridge Digital Twin

A source-governed, part-addressable digital twin of the Manhattan Bridge for browser rendering and
HO-scale (1:87.1) study.

**Current state: Milestone 4 — sourced detail geometry. Both period engineering primaries examined directly.**

The governing rule, from [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md): no existing 3D model is
authoritative. Official dimensions and archival drawings are the control geometry. Photogrammetry
and marketplace meshes are secondary visual references only. Nothing here invents a dimension:
anything without a registered source is tagged confidence `D`, named as a placeholder, and linked to
the open question that would retire it.

## Read these first

| Document | What it governs |
|---|---|
| [GEOMETRY-CONTROL.md](GEOMETRY-CONTROL.md) | **Source of truth for every dimension.** Scripts parse it; they carry no numbers of their own. |
| [SOURCE-REGISTER.md](SOURCE-REGISTER.md) | Every source that may influence geometry, its verification state, and the open conflicts. |
| [CONFIDENCE-MODEL.md](CONFIDENCE-MODEL.md) | Grades A–D, the weakest-link rule, and the metadata contract every part must satisfy. |
| [SCALE-HO.md](SCALE-HO.md) | 1:87.1 reporting scale and what it implies physically. |
| [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) | The original build handoff and milestone plan. |

## Quick start

```bash
# 1. Build the control skeleton from GEOMETRY-CONTROL.md
python scripts/build_control_skeleton.py

# 2. Check it against the regression and traceability suites
python scripts/validate_dimensions.py

# 3. Run the viewer
cd viewer && npm install && npm run dev     # http://localhost:5173
```

Python 3.10+ with no third-party packages. Node 18+ for the viewer.

## What the build produces

```text
mesh/glb/control_skeleton.glb              authoritative skeleton, prototype meters
mesh/glb/control_skeleton.gltf + .bin      human-readable review copy
mesh/glb/control_skeleton_ho.glb           uniformly scaled HO copy, 1:87.1
cad/procedural/control_skeleton_geometry.json  tool-neutral procedural definition
viewer/metadata/parts.json                 taxonomy, stations, elevations, controls, part manifest
viewer/metadata/scale_ho.json              HO reporting table
viewer/metadata/build_report.json          derived values and measures used by the tests
tests/validation_report.json               last test run
```

81 parts across 7 systems: reference (datum, control curves, 11 stations), towers (centerlines,
caissons, piers, eight tapered legs, bracing), anchorages, four main cables, four suspender groups,
the deck system (two offset upper roadways, lower roadway, sixteen truss chord sets and sixteen truss
web sets, two footwalks, four subway tracks), and two approaches.

`.blend` and `.step` are **not** produced by the default path, because it has no binary dependencies.
[cad/procedural/build_in_blender.py](cad/procedural/build_in_blender.py) rebuilds the identical
skeleton inside Blender from the tool-neutral JSON when a `.blend` is needed.

## Honest status of the geometry

| Grade | Parts | What it is |
|---|---:|---|
| A | 33 | Stations, datum, bridge axis, tower centerlines, caissons, piers, the eight tower legs, and all sixteen stiffening truss chord sets. |
| B | 4 | Anchorages and approach-end stations. |
| C | 0 | Nothing from meshes or photogrammetry yet. |
| D | 44 | Truss web members, suspenders, deck and track envelopes, approaches, tower bracing. |

**7 of 69 control values are placeholders**, down from 19 of 36 at Milestone 1.

**Milestone 2** sourced the transverse layout: stiffening truss spacing **28–40–28 ft** (trusses A–D,
south to north), which also fixes the four cable positions since each cable sits directly above its
truss; deck **120 ft**, lower roadway **35 ft**, footwalks **10 ft**; anchorages **237 × 182 × 135 ft**.
The cable sag and suspender pitch were *derived* rather than guessed.

**Milestone 3** examined both period engineering journals directly.

*Scientific American*, 1 February 1908, pp. 77–78 (archive.org) gave the saddle elevation as
**322.5 ft**, replacing a 330 ft figure that had reached the model second-hand; established that the
21.25 in cable diameter is measured **on the wires, excluding wrapping**; and described the tower
legs in full: **four box-section legs, each 5 ft wide transversely, tapering from 32 ft to 10 ft**
parallel to the bridge axis, standing **in the planes of the four stiffening trusses**.

*The Engineering Record*, 12 March 1904, Vol 49 pp. 332–333 (HathiTrust, human-assisted retrieval)
gave the pier capstone at **23 ft above mean high tide**, pier **68 × 134 ft on top**, caisson
**78 × 144 ft, 47.5 ft high**, cutting edge **92 ft below MHW**. It **overturned an earlier
derivation** of mine that had inferred 31 ft from summary heights; the 8 ft disagreement between the
two primaries is recorded as OQ-016 and kept visible by a report-only test. It also corrected a
citation error: the article says the towers are "of steel 330 feet high", not 330 ft to the tops of
the cables.

**Milestone 4** turned that sourced detail into visible structure — tapered tower legs, Warren truss
chords and web at the derived 18.61 ft panel pitch, and main cables drawn at their sourced 21.2 in
diameter. Truss chords and web are **separate parts** because the chords are grade A and only the web
pattern is inferred.

Thirteen conflicts are carried openly in [SOURCE-REGISTER.md](SOURCE-REGISTER.md) rather than
silently resolved. Seven are settled by weight of evidence.

## Repository layout

```text
sources/         drawings, photos, videos, existing meshes, photogrammetry inputs, licences (empty)
cad/             blender, freecad, rhino-or-step, procedural (the procedural definition lives here)
mesh/            raw, cleaned, segmented, lod0_full, lod1_browser, lod2_mobile, glb
photogrammetry/  image-sets, colmap, meshroom, point-clouds, dense-meshes (empty)
viewer/          Vite + React + three.js browser viewer
scripts/         build and validation pipeline
tests/           regression and traceability suites
```

## Scripts

| Script | Status |
|---|---|
| `build_control_skeleton.py` | Implemented. Parses GEOMETRY-CONTROL.md, derives stations and elevations, exports GLB/glTF and metadata. |
| `validate_dimensions.py` | Implemented. Runs both suites in `/tests`, writes `tests/validation_report.json`. |
| `control_model.py` | Implemented. Shared parser for GEOMETRY-CONTROL.md. |
| `normalize_units.py` | Implemented. The single unit-conversion implementation. |
| `export_gltf.py` | Implemented. Dependency-free glTF 2.0 / GLB writer. |
| `ingest_sources.py` | Stub. Milestone 5. |
| `import_reference_meshes.py` | Stub. Milestone 6. |
| `align_mesh_to_control.py` | Stub. Milestone 6. |
| `segment_components.py` | Stub. Milestone 6. |

The stubs exit with status 2 and explain what must happen first. They do not silently no-op.

## The remaining blocker is administrative, not technical

Every dimension still missing — the vertical framing depths (OQ-013), the exact subway track
centrelines (OQ-010), and the 8 ft foundation discrepancy (OQ-016) — lives in NYCDOT record and
rehabilitation drawings, or in the 1907–1909 contract drawings. None are public.

This conclusion is reached independently by
[Ethical-Tech-CoLab/manhattan-bridge-noise-dumbo](https://github.com/Ethical-Tech-CoLab/manhattan-bridge-noise-dumbo)
(SRC-018, CC BY 4.0), whose `VISUAL-MODEL-FRAMEWORK.md` states that record drawings "are the only
plausible route to the level of detail this programme needs, and none of them are public", and which
ranks a FOIL request to NYCDOT as its own priority-one action. Two projects arriving at the same
blocker from different directions is a strong signal about where the next effort belongs.

See [SOURCE-REGISTER.md](SOURCE-REGISTER.md) for the full verification queue.

## License

Research content and data are released under [CC BY 4.0](LICENSE.md); the build pipeline and viewer
code are released under the MIT License. See [LICENSE.md](LICENSE.md) for the full terms and for the
incorporated-material notices.

## Acknowledgements

Bridge geometry derives from the sources registered in [SOURCE-REGISTER.md](SOURCE-REGISTER.md).
Trackform characterisation and the floor beam depth (CTL-062) are used under CC BY 4.0 from
*Silencing the Span*, Ethical Tech CoLab, 2026.
