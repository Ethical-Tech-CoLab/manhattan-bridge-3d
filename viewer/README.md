# Viewer

A minimal, config-driven browser viewer for source-governed GLB digital twins. It is not
Manhattan-Bridge-specific: point `public/model.config.json` at any GLB whose part nodes carry the
metadata contract from [CONFIDENCE-MODEL.md](../CONFIDENCE-MODEL.md) in their glTF `extras`, plus a
matching `parts.json` manifest, and the same build will render it.

## Run

```bash
# from the repository root, generate the model and metadata first
python scripts/build_control_skeleton.py

cd viewer
npm install
npm run dev        # http://localhost:5173
```

`npm run build` type-checks and produces a static bundle in `viewer/dist`.

## What it reads

| File | Purpose |
|---|---|
| `public/model.config.json` | title, model URL, metadata URL, camera framing, HO scale denominator |
| `public/control_skeleton.glb` | the model; part metadata lives in each node's glTF `extras` |
| `public/parts.json` | taxonomy, stations, elevations, controls, and the full part manifest |

`control_skeleton.glb`, `control_skeleton_ho.glb` and `parts.json` in `public/` are **generated**.
`scripts/build_control_skeleton.py` copies them there on every run. Do not edit them by hand.

## Milestone 1 features

- [x] Load the full GLB.
- [x] Toggle systems and individual parts on and off.
- [x] Click a part in the scene or the tree to show its metadata.
- [x] Source and confidence overlay, recolouring every part by grade.
- [x] HO-scale dimension toggle (readout only; the scene is never rescaled).
- [x] Component tree explorer grouped by system and subsystem.
- [x] Confidence legend with per-grade part counts.
- [x] Measurement panel listing control dimensions, reference stations, and placeholders in force.

Deferred, and listed in `notImplementedYet` inside `model.config.json`:

- [ ] LOD switching (Milestone 5).
- [ ] Exploded part schematic view (Milestone 5).
- [ ] Archival drawing overlay (Milestone 3).
- [ ] Photogrammetry point cloud overlay (Milestone 3).

## Why plain three.js

The 3D layer is written directly against three.js rather than through a React reconciler.

React Three Fiber was used initially, but in this environment its `Canvas` intermittently failed to complete
initialisation: the canvas element and render clock were created, yet `onCreated` never fired and the scene
children never mounted, so the model silently never loaded. The failure depended on how the container's size was
resolved, which made it a layout race rather than a bug we could pin down quickly.

The viewer needs only four things from the 3D layer — load a GLB, orbit, raycast-pick, and recolour materials — so
a direct implementation is roughly the same amount of code, has an explicit and debuggable lifecycle, and removes a
dependency. React still owns all the surrounding UI; `BridgeViewer.tsx` owns the canvas and exposes its state
through ordinary props.

## Layout

```text
index.html
vite.config.ts
tsconfig.json
src/main.tsx           React entry point
src/App.tsx            application shell, selection and visibility state
src/BridgeViewer.tsx   model-agnostic three.js canvas: load, orbit, pick, confidence recolouring
src/model.ts           metadata types and unit formatting
src/styles.css
components/PartTree.tsx
components/MetadataPanel.tsx
components/ConfidenceLegend.tsx
components/DimensionPanel.tsx
components/Toolbar.tsx
metadata/              generated manifests, mirrored into public/
annotations/           reserved for viewer annotations (Milestone 5)
```

## Notes

- Coordinates are authored Z-up in prototype meters. The GLB root node carries the rotation into the
  glTF Y-up frame, so vertex data stays directly comparable to
  [GEOMETRY-CONTROL.md](../GEOMETRY-CONTROL.md).
- Line geometry (cables, suspenders, stations, centerlines) is picked with a raycaster threshold set
  by `lineRaycastThreshold` in the config, expressed in world meters.
- Materials are cloned per part on load, because the exporter deduplicates materials by style.
- The canvas is absolutely positioned inside `.canvas-host`. A percentage-height canvas inside a flex
  container oscillates during layout, which made pointer interaction unreliable.
- `npm audit` reports a `nanoid` advisory reached through the Vite dev-server dependency chain. The
  advisory's fixed version is not published on this registry, and `npm audit fix` would downgrade
  Vite by seven major versions. It affects dev tooling only, not the shipped bundle.
