# Confidence Model

Every part in the digital twin carries an explicit confidence grade. The grade describes *how the geometry was
obtained*, not how good it looks.

---

## 1. Grades

| Grade | Definition | Typical basis | May be cited as a dimension? |
|---|---|---|---|
| **A** | Derived from an official dimension or an archival drawing. | `SRC-001`..`SRC-004`, `SRC-009` | Yes |
| **B** | Derived from multiple consistent photographs combined with known control geometry. | `SRC-003`, `SRC-005`, `SRC-006` plus a Tier A control | Yes, with the deviation recorded |
| **C** | Derived from an existing mesh or from photogrammetry that has been aligned to the control skeleton. | `SRC-006`..`SRC-008` | No |
| **D** | Inferred, decorative, or placeholder. | no source | No. Never. |

Rule of the weakest link: a part's confidence is the **minimum** of its own basis grade and the grades of every
control value it consumes. A tower envelope that uses an `A` height and a `D` plan width is a `D` part.

`scripts/build_control_skeleton.py` enforces this rule automatically when it assembles each part.

---

## 2. Required metadata on every part

No part enters the model without all of these. The build script fails if any are missing.

```json
{
  "part_id": "tower_manhattan_envelope",
  "system": "towers",
  "source_basis": ["control_dimension", "inferred"],
  "confidence": "D",
  "prototype_units": "meters",
  "ho_scale_units": "millimeters",
  "notes": "Envelope only. Plan dimensions are placeholders, see OQ-007.",
  "scale": "1:1 prototype, HO 1:87.1",
  "last_modified_by_agent": "build_control_skeleton.py@<version>",
  "review_status": "unreviewed"
}
```

| Field | Allowed values |
|---|---|
| `part_id` | lowercase snake_case, unique across the model |
| `system` | one of the taxonomy systems in section 3 |
| `source_basis` | non-empty array from `drawing`, `official_facts`, `photo`, `mesh_reference`, `photogrammetry`, `control_dimension`, `inferred` |
| `confidence` | `A`, `B`, `C`, `D` |
| `prototype_units` | `meters` |
| `ho_scale_units` | `millimeters` |
| `notes` | free text, must name the open question ID for any `D` part |
| `scale` | scale statement |
| `last_modified_by_agent` | agent or script identifier plus version |
| `review_status` | `unreviewed`, `agent_reviewed`, `human_reviewed`, `rejected` |

`control_refs` is additionally emitted by the build script: the list of `CTL-###` IDs that the part's geometry
consumed. This is what makes the weakest-link rule auditable.

**Solid volumes versus planes.** A `box` asserts extent in all three axes; a `quad` is a plane and asserts extent
in two. Both are subject to the weakest-link rule. Milestone 2 additionally capped all boxes at `B`; that cap was
retired in Milestone 3 once the tower caissons became fully sourced, and replaced by `GRT-068`, which pins the
expected grade of representative parts across all four bands.

---

## 3. Systems

From the taxonomy in `AGENT-INSTRUCTIONS.md` section 6:

`reference` (datum and stations), `anchorages`, `towers`, `cables`, `suspenders`, `deck_system`
(`upper_roadway`, `lower_roadway`, `subway_tracks`, `stiffening_trusses`, `cross_girders`, `floor_beams`),
`approaches`, `details`.

---

## 4. Promotion and demotion

**Promotion** `D` -> `C` -> `B` -> `A` requires:

1. A registered, verified source ID in `SOURCE-REGISTER.md`.
2. Replacement of every placeholder control value the part consumes with a sourced control value in
   `GEOMETRY-CONTROL.md`.
3. Closure of every open question listed in the part's `notes`.
4. A recorded deviation against the previous geometry in the alignment or validation report.
5. `review_status` advanced to at least `agent_reviewed`.

**Demotion** is automatic and immediate if a cited source fails verification, or if a control value it depends on is
moved back to the placeholder table.

Milestone 3 status: the tower caissons and piers are solid volumes whose every dimension comes from directly
examined period primary sources, so they are graded `A`.

| Grade | Parts | Notes |
|---|---:|---|
| A | 25 | Stations, datum, bridge axis, tower centerlines, caissons, piers, sixteen stiffening truss planes. |
| B | 6 | Tower shafts, anchorages, approach-end stations. |
| C | 0 | Nothing derived from meshes or photogrammetry yet. |
| D | 30 | Cables, suspenders, deck and track envelopes, approaches — each blocked by one of the seven remaining placeholders. |

---

## 5. Colour coding in the viewer

| Grade | Colour | Hex |
|---|---|---|
| A | green | `#2e9e4f` |
| B | blue | `#3b7dd8` |
| C | amber | `#d89a3b` |
| D | red | `#c4453c` |

The viewer's confidence overlay recolours every part by this table so that unverified geometry is visually obvious.
