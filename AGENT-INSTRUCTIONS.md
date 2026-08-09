# Manhattan Bridge Digital Twin CAD/Mesh Build Handoff

Purpose: create a self-contained instruction package for a VS Code agentic build harness to produce the most accurate browser-renderable CAD/mesh digital twin of the Manhattan Bridge possible, with enough part-level structure to support HO-scale study and future 3D-print preparation.

This handoff prioritizes geometry accuracy, source traceability, component addressability, and browser-renderable visual fidelity. It does not prioritize slicer settings, infill, supports, or other print-production details.

---

## 1. Core Build Objective

Build a browser-renderable, part-addressable Manhattan Bridge digital twin that supports:

- Whole-bridge visual rendering in a browser.
- Drill-down by component and subsystem.
- Source-linked geometry confidence levels.
- HO-scale dimensional reference.
- Export to `.glb/.gltf`, plus archival CAD/mesh working files.
- Future conversion into printable components if needed.

Primary rule: do not treat any existing 3D model as authoritative. Use official dimensions, archival drawings, HAER/LOC records, engineering references, and known bridge measurements as control geometry. Use photogrammetry, video, images, and marketplace/community meshes only as secondary visual/detail references.

---

## 2. Known Control Dimensions From Prior Research

Use these as initial control values and validate them against the source register before finalizing geometry.

| Feature | Prototype Dimension | HO Dimension, 1:87.1 |
|---|---:|---:|
| Total bridge and approaches | 6,855 ft | 944.43 in / 78.70 ft / 23,988.6 mm |
| Lower-level abutment-to-abutment | 5,790 ft | 797.70 in / 66.48 ft / 20,261.7 mm |
| Upper roadway portal-to-portal | 6,090 ft | 839.04 in / 69.92 ft / 21,311.5 mm |
| Anchorage-to-anchorage suspended length | 2,920 ft | 402.30 in / 33.53 ft / 10,218.3 mm |
| Main span | 1,470 ft | 202.53 in / 16.88 ft / 5,144.2 mm |
| Each side span | 725 ft | 99.89 in / 8.32 ft / 2,537.1 mm |
| Tower height above mean high water | 322 ft | 44.36 in / 1,126.8 mm |
| Center clearance above mean high water | 135 ft | 18.60 in / 472.4 mm |
| Roadway width | 46 ft | 6.34 in / 161.0 mm |
| Stiffening truss depth, ASCE reference | 24 ft | 3.31 in / 84.0 mm |
| Stiffening truss depth, alternate reference | 26 ft | 3.58 in / 91.0 mm |
| Cable length | 3,224 ft | 444.18 in / 37.02 ft / 11,282.1 mm |
| Main cable diameter, ASCE | 20.75 in | 0.238 in / 6.05 mm |
| Main cable diameter, HAER/NYCRoads | 21.25 in | 0.244 in / 6.20 mm |

Important implication: a complete HO bridge model is extremely large. Treat the full bridge as a digital twin first. Use modular extraction later for physical study pieces.

---

## 3. Source Hierarchy

### Tier A: Control Geometry

Use these to establish the canonical bridge coordinate system and dimensions.

1. NYC DOT Manhattan Bridge official facts.
2. ASCE Manhattan Bridge engineering facts.
3. HAER / Library of Congress Manhattan Bridge record.
4. 1907 to 1909 contract drawings.
5. Smithsonian and NYC Municipal Archives drawing records.
6. Known bridge measurements from prior research, including main span, side spans, suspended length, total bridge and approach length, tower height, cable diameter, and deck organization.

### Tier B: Detail Geometry

Use for secondary validation and missing part-level detail.

1. HistoricBridges.org full-size detail photo galleries.
2. Wikimedia Commons Manhattan Bridge categories and subcategories.
3. Wikimedia Commons construction, close-up, anchorage, footpath, rail track, and arch/colonnade images.
4. HAER / LOC public-domain photographs.
5. 360-degree pedestrian path videos.
6. Aerial video and high-resolution city images.

### Tier C: Existing 3D Meshes

Use only as reference overlays or visual scaffolds.

1. Sketchfab Manhattan Bridge models.
2. Free3D Manhattan Bridge models.
3. CGTrader Manhattan Bridge models.
4. TurboSquid Manhattan Bridge models.
5. STL aggregators such as STLFinder and Yeggi.

Do not use any marketplace/community mesh as the canonical model unless it can be validated against Tier A sources.

---

## 4. Recommended Repository Structure

```text
manhattan-bridge-digital-twin/
  README.md
  AGENT-INSTRUCTIONS.md
  SOURCE-REGISTER.md
  GEOMETRY-CONTROL.md
  CONFIDENCE-MODEL.md
  SCALE-HO.md

  /sources/
    /drawings/
    /photos/
    /videos/
    /existing-meshes/
    /photogrammetry/
    /licenses/

  /cad/
    /blender/
    /freecad/
    /rhino-or-step/
    /procedural/

  /mesh/
    /raw/
    /cleaned/
    /segmented/
    /lod0_full/
    /lod1_browser/
    /lod2_mobile/
    /glb/

  /photogrammetry/
    /image-sets/
    /colmap/
    /meshroom/
    /point-clouds/
    /dense-meshes/

  /viewer/
    /public/
    /src/
    /components/
    /metadata/
    /annotations/

  /scripts/
    ingest_sources.py
    normalize_units.py
    build_control_skeleton.py
    import_reference_meshes.py
    align_mesh_to_control.py
    segment_components.py
    export_gltf.py
    validate_dimensions.py

  /tests/
    geometry_regression_tests.json
    source_traceability_tests.json
```

---

## 5. Phase 1: Establish Control Skeleton

Agent goal: create a mathematically constrained bridge skeleton before touching visual meshes.

Tasks:

1. Define world units in meters.
2. Add optional HO-scale export using 1:87.1 scale.
3. Set bridge origin at midpoint of main span.
4. Define X axis along bridge length.
5. Define Y axis across bridge width.
6. Define Z axis vertical.
7. Create reference stations:
   - Manhattan anchorage.
   - Manhattan tower.
   - Main-span midpoint.
   - Brooklyn tower.
   - Brooklyn anchorage.
   - Approach endpoints.
8. Encode known dimensions in `GEOMETRY-CONTROL.md`.
9. Build initial control curves:
   - deck centerline.
   - main cable parabolic/catenary approximation.
   - tower centerlines.
   - suspender spacing placeholders.
   - stiffening truss envelope.
   - roadway deck envelope.
   - subway track envelope.

Expected outputs:

```text
/cad/procedural/control_skeleton.blend
/cad/procedural/control_skeleton.step
/mesh/glb/control_skeleton.glb
```

---

## 6. Phase 2: Component Taxonomy

Agent goal: every visible part should belong to a named system.

Minimum hierarchy:

```json
{
  "bridge": {
    "anchorages": ["manhattan_anchorage", "brooklyn_anchorage"],
    "towers": ["manhattan_tower", "brooklyn_tower"],
    "cables": [
      "north_main_cable_1",
      "north_main_cable_2",
      "south_main_cable_1",
      "south_main_cable_2"
    ],
    "suspenders": [],
    "deck_system": {
      "upper_roadway": [],
      "lower_roadway": [],
      "subway_tracks": ["track_1", "track_2", "track_3", "track_4"],
      "stiffening_trusses": [],
      "cross_girders": [],
      "floor_beams": []
    },
    "approaches": ["manhattan_approach", "brooklyn_approach"],
    "details": [
      "railings",
      "stairs",
      "catenary",
      "lamp_posts",
      "signage",
      "maintenance_platforms"
    ]
  }
}
```

Each part should carry metadata:

```json
{
  "part_id": "tower_manhattan_arch_panel_001",
  "system": "tower",
  "source_basis": ["drawing", "photo", "mesh_reference", "inferred"],
  "confidence": "A|B|C|D",
  "prototype_units": "meters",
  "ho_scale_units": "millimeters",
  "notes": ""
}
```

---

## 7. Phase 3: Photogrammetry Pipeline

Agent goal: create photogrammetric point clouds and meshes for visual detail and relative placement, not as sole dimensional truth.

### Route A: COLMAP

Use COLMAP for Structure-from-Motion and Multi-View Stereo reconstruction from ordered or unordered image collections.

Expected workspace:

```text
/photogrammetry/colmap/
  /workspace/
    /images/
    /sparse/
    /dense/
      fused.ply
      meshed-poisson.ply
      meshed-delaunay.ply
```

Recommended agent tasks:

1. Ingest images into named photo sets.
2. Preserve source URLs, licenses, and metadata.
3. Run sparse reconstruction.
4. Run dense reconstruction.
5. Export point cloud and mesh.
6. Align output to control skeleton.
7. Use photogrammetry mesh for local visual detail only.

### Route B: Meshroom / AliceVision

Use Meshroom for alternate open-source reconstruction and textured visual outputs.

Expected stages:

1. Camera initialization.
2. Feature extraction.
3. Image matching.
4. Feature matching.
5. Structure from motion.
6. Dense scene preparation.
7. Depth map generation.
8. Depth map filtering.
9. Meshing.
10. Mesh filtering.
11. Texturing.

Use Meshroom when texturing and visual reconstruction are more important than dimensional authority.

---

## 8. Photogrammetry Capture and Source Plan

Create image sets by zone:

```text
image-set-001-main-towers
image-set-002-main-cables
image-set-003-suspenders
image-set-004-deck-trusses
image-set-005-subway-track-bays
image-set-006-pedestrian-path
image-set-007-anchorages
image-set-008-approach-spans
image-set-009-ornamental-details
```

For each image set, create a manifest:

```json
{
  "image_set_id": "image-set-004-deck-trusses",
  "source": "Wikimedia / field photo / video frame / HistoricBridges",
  "license": "",
  "camera_metadata_available": true,
  "coverage": "north side lower deck truss",
  "use": "visual reference | photogrammetry | texture | measurement aid",
  "quality": "high | medium | low"
}
```

Important: extracted 360-degree video frames can help with continuity and detail orientation, but they should not override measured geometry unless scale control points exist.

---

## 9. Mesh Alignment Workflow

For every imported mesh:

1. Import raw model into `/mesh/raw`.
2. Preserve original file and license.
3. Convert to neutral working format such as `.obj`, `.fbx`, `.blend`, or `.ply`.
4. Align to the control skeleton using:
   - tower centerlines.
   - deck elevation.
   - main-span endpoints.
   - anchorage positions.
5. Scale against known total/main-span dimensions.
6. Mark deviations in `mesh_alignment_report.md`.
7. Split into named components.
8. Delete or isolate non-bridge scenery.
9. Replace texture-only details with actual geometry where needed.
10. Export review version as `.glb`.

---

## 10. Browser Render Target

Primary delivery format: `.glb` and `.gltf`.

Viewer requirements:

```text
- Load full bridge GLB.
- Toggle systems on/off.
- Click part to show metadata.
- Show source/confidence overlay.
- Toggle HO-scale dimensions.
- Toggle archival drawing overlay.
- Toggle photogrammetry point cloud.
- Support LOD switching.
- Support exploded part schematic view.
```

Recommended browser stack:

```text
- Three.js or React Three Fiber.
- GLTFLoader for GLB/glTF assets.
- Sidebar metadata panel.
- Component tree explorer.
- Source/confidence legend.
- Measurement overlay.
```

---

## 11. Accuracy and Confidence Model

Use explicit confidence tags:

```text
A = derived from official dimension or archival drawing.
B = derived from multiple consistent photos plus known control geometry.
C = derived from existing mesh or photogrammetry aligned to controls.
D = inferred, decorative, or placeholder.
```

No part should enter the final model without:

```text
part_id
source_basis
confidence
scale
last_modified_by_agent
review_status
```

---

## 12. Agent Instruction Block

```markdown
You are building an accurate digital twin of the Manhattan Bridge for browser rendering and HO-scale study.

Primary rule:
Do not treat any existing 3D model as authoritative. Use official dimensions, archival drawings, HAER/LOC data, and known bridge measurements as control geometry. Use photogrammetry and marketplace/community meshes only as secondary visual references.

Deliverables:
1. Build a source-linked control skeleton.
2. Create component taxonomy.
3. Ingest and align external meshes.
4. Build or refine geometry by component.
5. Create LOD0, LOD1, and LOD2 versions.
6. Export GLB/glTF for browser rendering.
7. Attach metadata to every named component.
8. Produce dimension validation reports.
9. Produce confidence overlays for source traceability.

Do not optimize for printer infill. Optimize for visual accuracy, component addressability, scale fidelity, source traceability, and browser renderability.
```

---

## 13. First Build Milestone

Build this first:

```text
Milestone 1: Control Skeleton + Browser Viewer
- bridge centerline.
- towers.
- deck envelope.
- main cables.
- side spans.
- anchorages.
- four subway tracks.
- basic truss envelope.
- clickable metadata.
- HO-scale dimension toggle.
```

This milestone creates a stable truth model before importing noisy meshes, photogrammetry products, or existing commercial/community models.

---

## 14. Validation Checklist

Before accepting any geometry:

```text
[ ] Does it align to the control skeleton?
[ ] Is its source recorded?
[ ] Is the confidence level assigned?
[ ] Is it part-addressable?
[ ] Is it named consistently?
[ ] Is it assigned to a system and subsystem?
[ ] Has it been exported to GLB for browser review?
[ ] Has it been checked against at least one Tier A or Tier B source where possible?
[ ] Is the deviation from known dimensions recorded?
```

---

## 15. Notes for Claude / OpenAI VS Code Agentic Harness

Recommended execution pattern:

1. Read `SOURCE-REGISTER.md` and `GEOMETRY-CONTROL.md` first.
2. Build `control_skeleton.blend` procedurally.
3. Export `control_skeleton.glb`.
4. Build a modular minimal browser viewer usable for other similar models
5. Add metadata panel and component picking.
6. Import reference meshes one at a time.
7. Never merge raw meshes directly into the authoritative model.
8. Use alignment reports to compare external meshes against the control skeleton.
9. Promote geometry only when it has traceable source basis.
10. Keep all inferred or decorative geometry tagged as confidence D until reviewed.

---

## 16. Suggested File Outputs From First Agent Run

```text
README.md
SOURCE-REGISTER.md
GEOMETRY-CONTROL.md
CONFIDENCE-MODEL.md
SCALE-HO.md
AGENT-INSTRUCTIONS.md
/cad/procedural/control_skeleton.blend
/mesh/glb/control_skeleton.glb
/viewer/README.md
/viewer/src/App.tsx
/viewer/src/BridgeViewer.tsx
/viewer/public/control_skeleton.glb
/tests/geometry_regression_tests.json
```

---

## 17. Minimum Source Register Template

```markdown
# Source Register

| Source ID | Title | URL or Archive Ref | Type | License | Use | Confidence Impact | Notes |
|---|---|---|---|---|---|---|---|
| SRC-001 | NYC DOT Manhattan Bridge facts | TBD | Official facts | TBD | Control dimensions | A | Validate length/span values |
| SRC-002 | ASCE Manhattan Bridge facts | TBD | Engineering reference | TBD | Cable/truss/span dimensions | A | Validate cable diameter and truss depth |
| SRC-003 | HAER NY-127 LOC record | TBD | Archival engineering/photos | TBD | Historic reference and photos | A/B | Pull photos and captions |
| SRC-004 | 1909 contract drawings | TBD | Archival drawings | TBD | Railings, stairs, roadways, track, electrical | A | Highest value for detail geometry |
| SRC-005 | HistoricBridges photo galleries | TBD | Modern detail photos | TBD | Visual/detail reference | B | Good for truss, deck, and cable details |
| SRC-006 | Wikimedia Commons categories | TBD | Public image collections | Varies | Photogrammetry/reference | B/C | Check license per file |
| SRC-007 | 360-degree pedestrian path video | TBD | Video | TBD | Frame extraction/reference | C | Useful for path and deck continuity |
| SRC-008 | Existing marketplace/community meshes | TBD | 3D mesh | Varies | Overlay/reference only | C/D | Do not treat as authoritative |
```

---

## 18. Final Operating Principle

The digital twin should be model-first and source-governed. The correct sequence is:

```text
sources -> control dimensions -> skeleton -> parts taxonomy -> validated geometry -> visual detail -> browser render -> optional print modules
```

Avoid the opposite pattern:

```text
existing mesh -> cleanup -> assumed bridge model
```

That path will produce a visually plausible asset, but not a trustworthy Manhattan Bridge digital twin.
