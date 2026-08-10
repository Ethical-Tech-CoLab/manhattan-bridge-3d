# Manhattan Bridge Digital Twin

**▶ [View the model in your browser](https://ethical-tech-colab.github.io/manhattan-bridge-3d/)** ·
**[🔍 Photograph audit](https://ethical-tech-colab.github.io/manhattan-bridge-3d/review/)** — 253
openly-licensed photographs, **0 reviewed so far**, every one still `auto_screened`

A source-governed, part-addressable digital twin of the Manhattan Bridge for browser rendering and
HO-scale (1:87.1) study.

**Current state: Milestone 10 — anchorage thoroughfare arch modelled; 103 parts, 74 tests passing.**

The governing rule, from [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md): no existing 3D model is
authoritative. Official dimensions and archival drawings are the control geometry. Photogrammetry
and marketplace meshes are secondary visual references only. Nothing here invents a dimension:
anything without a registered source is tagged confidence `D`, named as a placeholder, and linked to
the open question that would retire it.

Rebuilt and republished from `GEOMETRY-CONTROL.md` on every push to `main`, and the deploy is gated
on the regression suite, so the published model is always one that passed its own tests.

One caveat about the published build: the geometry regression suite runs in CI and gates the
deploy, but **schema validation is skipped there**. It needs the `digital-3d-shared-contracts`
checkout for both the schemas and its Ajv install, which is not present on the runner, so
`validate_contract.mjs` says so plainly rather than reporting a pass it did not perform. Run it
locally before relying on the published contract documents.

## Read these first

| Document | What it governs |
|---|---|
| [GEOMETRY-CONTROL.md](GEOMETRY-CONTROL.md) | **Source of truth for every dimension.** Scripts parse it; they carry no numbers of their own. |
| [SOURCE-REGISTER.md](SOURCE-REGISTER.md) | Every source that may influence geometry, its verification state, and the open conflicts. |
| [CONFIDENCE-MODEL.md](CONFIDENCE-MODEL.md) | Grades A–D, the weakest-link rule, and the metadata contract every part must satisfy. |
| [SCALE-HO.md](SCALE-HO.md) | 1:87.1 reporting scale and what it implies physically. |
| [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) | The original build handoff and milestone plan for this bridge. |
| [HOW-TO-DESIGN.md](HOW-TO-DESIGN.md) | **Starting a sibling bridge?** The transferable method — governance model, the three grading axes, the verified HAER source landscape for all three East River bridges, and every trap this project hit. |

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

95 parts across 7 systems: reference (datum, control curves, 11 stations), towers (centerlines,
caissons, piers, eight tapered legs, bracing), anchorages, four main cables, four suspender groups,
the deck system (two offset upper roadways, lower roadway, sixteen truss chord sets and sixteen truss
web sets, two footwalks, four subway tracks), and the approaches (lower deck to the sourced abutment,
upper roadway to the sourced portal, continued trackwork, and viaduct bents).

Every part also carries a **material**, assigned and graded in
[GEOMETRY-CONTROL.md](GEOMETRY-CONTROL.md) section 7 rather than chosen in the renderer. Material
grade is tracked separately from dimensional grade: the tower piers are grade-A masonry on the
strength of a period primary, while the anchorages are grade-D masonry because no registered source
says what they are built from, even though every photograph shows stone.

Every part also carries a **geometry provenance** — `MEASURED`, `DOCUMENTED`, `INFERRED` or
`ASSUMED` — which is a different question from source confidence and is kept on its own axis
([section 8](GEOMETRY-CONTROL.md)). It is drawn into the geometry as solid, dashed and dotted
outlines, so uncertainty is visible by default rather than behind a toggle:

| | count |
|---|---:|
| measured | **0** |
| documented | 37 |
| inferred | 56 |
| assumed | 2 |

Switching `inferred` and `assumed` off in the viewer leaves the towers, the anchorages and the
station markers. That is the whole of what this model can be said to document.

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

**Milestone 5** published the module to the shared district contract so the neighbouring
`dumbo-district-3d` twin can place the bridge: a schema-valid manifest, a level-2 proxy, a
hash-verified copy of the canonical frame, and the vertical datum declared rather than silently
converted.

**Milestone 6** fixed a defect the earlier renders concealed. All deck geometry stopped at the
anchorage face, ±445 m, while two grade-A controls say otherwise: CTL-002 puts the lower level's
abutments 5790 ft apart and CTL-003 puts the upper roadway's portals 6090 ft apart. The tracks and
steelwork therefore ended in mid-air, 437 m and 483 m short of stations the register already
documented. The approaches are now structure rather than a flat slab — lower deck, upper roadway,
continued trackwork and viaduct bents — with the *extent* sourced and the *form* held as three new
placeholders under OQ-020. The same milestone added the graded material table.

It also adopted the two-field provenance model from SRC-018 after establishing something worth
recording: the noise-dumbo schematics that set the visual bar are **not** built from measured
drawings either. That framework states plainly that no element of either East River subway bridge
reaches `MEASURED` or `DOCUMENTED`. Their visual quality comes from rendering discipline, not from
sources this project lacks, which means the same standard is reachable here without inventing a
single dimension.

Thirteen conflicts are carried openly in [SOURCE-REGISTER.md](SOURCE-REGISTER.md) rather than
silently resolved. Seven are settled by weight of evidence.

## Photographs, video and crowdsourced imagery

No photographic evidence has entered this model yet. That is why the confidence `C` band is empty
and why `MEASURED` provenance is zero -- both are honest readings, not oversights.

Assets enter only through `scripts/ingest_sources.py`, which refuses anything lacking a registered
`SRC-###`, an explicit licence, an attribution and an **observation date** (the date the image
records, not the date it was downloaded). Files under a redistributable licence are copied in and
checksummed; everything else is recorded by reference, so the repository never stores something it
has no right to.

```powershell
python scripts/ingest_sources.py --list-sets   # the nine capture zones
python scripts/ingest_sources.py --verify      # checksums plus coverage against those zones
```

**What a photograph is allowed to prove** is set out in
[CONFIDENCE-MODEL.md section 6](CONFIDENCE-MODEL.md). The short version: a photograph can promote a
**material** row to `A`, and can move a part's geometry provenance from `ASSUMED` to `INFERRED`. It
cannot promote a **dimensional** control above `D` on its own, because a projection without scale
control cannot yield a length.

The cheapest promotion available anywhere in this repository is one licensed, dated photograph of an
anchorage face. `MAT-010` grades the anchorage masonry `D` even though every photograph shows stone,
because no *registered* source says so. There, the register is the bottleneck, not the fact.

One expectation worth setting in advance. Crowdsourced photography is not a random sample of the
structure -- it is shot from where people stand, which is the riverbank, the parks and the
pedestrian path. That is excellent coverage of the **underside and outboard faces**, which is
exactly what aerial survey cannot see, and poor coverage of the **truss-bay interiors and deck
framing**, which is exactly where the remaining placeholders are. Ten thousand photographs from
Brooklyn Bridge Park still do not see inside a truss bay. The occlusion is structural, not a
sample-size problem.

## Repository layout

```text
sources/         drawings, photos, videos, existing meshes, photogrammetry inputs, licences (empty)
cad/             blender, freecad, rhino-or-step, procedural (the procedural definition lives here)
mesh/            raw, cleaned, segmented, lod0_full, lod1_browser, lod2_mobile, glb
photogrammetry/  image-sets, colmap, meshroom, point-clouds, dense-meshes (empty)
viewer/          Vite + React + three.js browser viewer
viewer/public/   the published module contract: bridge-manifest.json, frames/, bridge/, assets/
scripts/         build and validation pipeline
tests/           regression and traceability suites
```

## Publishing to the shared district contract

This module publishes itself to `digital-3d-shared-contracts` so the neighbouring
`dumbo-district-3d` twin can render the bridge where it crosses DUMBO. Serve `viewer/public/` at
the site root; `bridge-manifest.json` is the entry point and everything else is reached from it.

```powershell
python scripts/export_proxy.py            # level-2 proxy for district range
python scripts/publish_module_contract.py # manifest, ladder, registry, metadata, frame copy
node   scripts/validate_contract.mjs      # every document, both deployment layouts
python scripts/verify_placement.py        # placement vs the district's tile declarations
```

Elevations are authored against **mean high water** and declared as such; the 0.59 m conversion to
NAVD88 happens at placement time, from the frozen shared frame. See GEOMETRY-CONTROL.md section 6.

## Scripts

| Script | Status |
|---|---|
| `build_control_skeleton.py` | Implemented. Parses GEOMETRY-CONTROL.md, derives stations and elevations, exports GLB/glTF and metadata. |
| `validate_dimensions.py` | Implemented. Runs both suites in `/tests`, writes `tests/validation_report.json`. |
| `control_model.py` | Implemented. Shared parser for GEOMETRY-CONTROL.md. |
| `normalize_units.py` | Implemented. The single unit-conversion implementation. |
| `export_gltf.py` | Implemented. Dependency-free glTF 2.0 / GLB writer. |
| `export_proxy.py` | Implemented. Level-2 district proxy, ~4.6k triangles, authored in the module frame. |
| `publish_module_contract.py` | Implemented. Emits the shared-contract surface: manifest, LOD ladder, asset registry, shared-schema metadata, and a hash-verified copy of the canonical frame. |
| `validate_contract.mjs` | Implemented. Validates every published document, all 81 metadata records, six cross-document invariants, and URL resolution under both deployment layouts. |
| `verify_placement.py` | Implemented. Re-derives the occupied tile set from the published GLB and compares it with the consuming district's declarations. Exits non-zero while they disagree. |
| `check_corridor_geodetic.py` | Implemented. Tests the district's tile declarations against the placement axis, using only sourced coordinates. |
| `ingest_sources.py` | Implemented. The only way an asset enters `/sources`. Refuses anything without a registered `SRC-###`, an explicit licence, an attribution and an observation date; stores a copy only under a redistributable licence, and records everything else by reference and checksum. |
| `adapt_brief_for_bridge.py` | Implemented. Adapts this repository's build brief for a sibling bridge, quarantining the Manhattan control dimensions as a negative control. |
| `import_reference_meshes.py` | Stub. Milestone 8. |
| `align_mesh_to_control.py` | Stub. Milestone 8. |
| `segment_components.py` | Stub. Milestone 8. |

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
