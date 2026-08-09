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

The live counts are emitted by every build into `viewer/metadata/parts.json` and surfaced in the viewer's
confidence legend, so this table is a snapshot rather than the authority. As of Milestone 7, across 95 parts:

| Grade | Parts | Notes |
|---|---:|---|
| A | 33 | Stations, datum, bridge axis, tower centerlines, caissons, piers, tower legs, stiffening truss chords. |
| B | 4 | Anchorages and the approach-end stations. |
| C | 0 | **Still nothing derived from a mesh or from photogrammetry.** This band stays empty until an image set is ingested and aligned; see section 6. |
| D | 58 | Cables, suspenders, deck, tracks and approaches — each blocked by one of the ten remaining placeholders. |

The empty `C` band is the single most informative cell in this table: it records that no photographic or
photogrammetric evidence has yet entered the model at all.

---

## 5. Colour coding in the viewer

| Grade | Colour | Hex |
|---|---|---|
| A | green | `#2e9e4f` |
| B | blue | `#3b7dd8` |
| C | amber | `#d89a3b` |
| D | red | `#c4453c` |

The viewer's confidence overlay recolours every part by this table so that unverified geometry is visually obvious.

---

## 6. Photographic and crowdsourced evidence

A photograph is the most abundant evidence available for this bridge and the most easily misused.
This section states exactly what one is allowed to prove, because "we have thousands of tourist
photos" is true and is *not* the same claim as "we can measure the deck framing".

### 6.1 What a photograph is

A photograph is a projection of a structure onto a plane at one instant, through an unknown lens,
from an unrecorded position. It records **existence, arrangement, material, condition and date**. It
does not record **dimension**. Recovering dimension from it requires either a second view with known
geometry, or a scale reference in frame.

That distinction maps onto the two axes this repository already keeps separate: photographs are
strong evidence for *geometry provenance* and for *material*, and weak evidence for a *control
dimension*.

### 6.2 What a photograph may and may not grade

| Claim | Best grade a photograph alone supports | Why |
|---|---|---|
| This element exists | `A` for existence, but existence is not a dimension | Visible fact |
| This element is made of stone | `A` for the material row | Visible fact, if the photograph is registered and dated |
| These elements are arranged in this order | `B` | Visible, but foreshortening can mislead about spacing |
| This element is *N* feet long | **`D`. Never higher from a photograph alone.** | A projection without scale control cannot yield a length |
| This element is *N* feet long, measured against a control dimension visible in the same frame | `B` | This is photogrammetric measurement, and the deviation must be recorded |
| Geometry from `SfM` aligned to the control skeleton | `C` | Registered to controls, not independent of them |
| Geometry from `SfM` with surveyed scale control points | `MEASURED`, with a stated Level of Accuracy | The only route to `MEASURED` on this project |

**The rule that follows.** A photograph may promote a *material* row to `A` and may move a part's
geometry provenance from `ASSUMED` to `INFERRED`. It may not promote a *dimensional* control above
`D` on its own. Those are different tables and the promotion rules differ.

**A worked example already sitting in the model.** `MAT-010` grades the anchorage masonry `D`
because no registered source states what it is built from, even though every photograph shows stone.
That row is not waiting for a drawing. It is waiting for **one registered, licensed, dated
photograph** of an anchorage face. This is the cheapest grade promotion available in the entire
repository, and it is the clearest demonstration that the register — not the fact — is the
bottleneck.

### 6.3 Crowdsourced pools: the three things that go wrong

**Licence, per file, not per pool.** Wikimedia Commons is not a licence; it is a hosting platform
whose files carry many different licences, some incompatible with redistribution. `SRC-006` records
"licence must be captured per file" for this reason. `scripts/ingest_sources.py` refuses to ingest a
file without one.

**Date, because a photograph describes a moment.** The bridge was rehabilitated over decades. A 1970s
photograph of the truss web is evidence about the 1970s. Every ingested asset records an
`observed_date` separate from its retrieval date, and geometry derived from it inherits that date.

**Viewpoint bias, which is the subtle one.** Crowdsourced photography is not a random sample of the
structure. It is overwhelmingly shot from Brooklyn Bridge Park, DUMBO's Washington Street, and the
pedestrian path — because that is where people stand. That distribution is genuinely useful for the
**underside and the outboard faces**, which is exactly what aerial survey cannot see. It is close to
useless for the **interior of the truss bays and the deck framing**, which is exactly where this
model's remaining placeholders are (`OQ-013`, `OQ-010`).

So the honest expectation is worth stating in advance: a large tourist photo set will improve the
*layers on top of* the skeleton — material, arrangement, ornament, condition, texture — and will
probably not retire `OQ-013`. The occlusion is structural, not a matter of sample size. Ten thousand
photographs from the riverbank still do not see inside a truss bay.

### 6.4 What would retire the placeholders

Ranked by cost, cheapest first:

1. **One licensed photograph of each anchorage and tower face** — promotes `MAT-003` and `MAT-010`,
   and moves several parts from `ASSUMED` toward `INFERRED`.
2. **A walkway-level image set along the pedestrian path** — the path runs *inside* the structure,
   between the trusses. This is the only publicly accessible viewpoint that sees the deck framing,
   and it is the one capture that could plausibly reach `OQ-013`.
3. **`SfM` with scale control** — a survey target, or any control dimension physically measured on
   site. This is what makes `MEASURED` non-zero for the first time.
