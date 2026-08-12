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
confidence legend, so this table is a snapshot rather than the authority. As of Milestone 10, across 103 parts:

| Grade | Parts | Notes |
|---|---:|---|
| A | 33 | Stations, datum, bridge axis, tower centerlines, caissons, piers, tower legs, stiffening truss chords. |
| B | 4 | Anchorages and the approach-end stations. |
| C | 0 | **Still nothing derived from a mesh or from photogrammetry.** This band stays empty until an image set is ingested and aligned; see section 6. |
| D | 66 | Cables, suspenders, deck, tracks, approaches, arches and finials — each blocked by one of the fourteen remaining placeholders. |

The empty `C` band is the single most informative cell in this table: it records that no photographic or
photogrammetric evidence has yet entered the model at all.

### 4.1 When an engineering standard may stand in for a source

A published standard is evidence about *practice*, not about *this structure*. It may support a
control only where the standard is **forced** rather than merely customary — that is, where the
thing could not physically be otherwise.

| | Standard usable? | Why |
|---|---|---|
| **Track gauge** (`CTL-017`, grade `B` from `SRC-010`) | **Yes** | The B, D, N and Q trains crossing this bridge run through the rest of the network. Rolling stock cannot run on a different gauge, so interoperability *forces* the standard figure. |
| **Track spacing** (`CTL-106`, grade `D`) | **Not to fix it — but it bounds it** | Nothing forces two adjacent tracks to a *particular* separation; they need only clear each other. But they must clear each other, so the 10 ft B Division car width does set a floor. See below. |

The test is not "does a standard exist" but "could this dimension have been anything else?" Where
the answer is yes, adopting the standard is *a number lifted out of the scope in which it was set* —
the failure mode `SRC-018` records as its own most-repeated error, having committed it five times
including once in the document written to prevent it. A standard-backed control is capped at `B`
regardless, because a standard states what is normal rather than what was built.

**But a forced standard can *bound* a value even when it cannot *fix* one, and a bound is worth
registering.** This is the useful middle case, and the model missed it until it was challenged.
`SRC-026` records that the B, D, N and Q services crossing this bridge are B Division, whose cars
are 10 ft wide with a dynamic envelope of roughly 11 in each side. That fixes nothing about this
bridge — but two trains cannot pass at a centre-to-centre spacing under about 11.8 ft, so `CTL-106`
now has a hard floor it did not have before. It stays grade `D`, because a floor is not a value; the
placeholder simply stopped being unconstrained.

So a system-wide fact has three possible uses here, and they should not be confused:

| | Example |
|---|---|
| **Fixes a value** (usable, `B`) | Gauge — interoperability compels the figure |
| **Bounds a value** (registrable, grade unchanged) | Car width bounds track spacing from below |
| **Neither** | Nothing about the network locates a track relative to *this bridge's* axis (`CTL-105`) |

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

---

## 7. The presentation layer

A render can be improved in two entirely different ways, and keeping them apart is what lets this
project make the model look better while its dimensions are still uncertain.

| | Changes geometry? | Governed by |
|---|---|---|
| **Evidence layer** | Yes | Controls, sources, grades. Nothing enters without a source. |
| **Presentation layer** | **No, ever** | This section. Lighting, sky, water, haze, surface finish. |

**The rule.** A presentation change may alter how a surface is *lit, shaded or coloured*. It may not
alter where that surface *is*, how large it is, or how many of them there are. Anything that moves a
vertex is geometry and goes through `GEOMETRY-CONTROL.md` like everything else.

That boundary is testable, and `GRT-078` tests it: the mesh a presentation change produces must be
byte-identical to the mesh before it. A commit that improves the look and shifts the geometry fails.

### 7.1 What the presentation layer may assume

Some scene furniture is not a claim about the bridge at all, and some quietly is. The distinction:

| Element | Status |
|---|---|
| Sky, haze, exposure, tone | **Not a claim.** No source needed. |
| A water plane at `z = 0` | **Sourced, and worth stating.** `z = 0` is mean high water, a registered datum, so a water plane sits exactly where the datum says. It is the one piece of scene furniture that is dimensionally honest. |
| Surface finish per material | **Governed by section 7's material table**, which is graded. Stone looks like stone because `MAT-001` says masonry, not because it looked better. |
| Ground, terrain, buildings | **Not modelled here, deliberately.** Those belong to `dumbo-district-3d`. Drawing our own would duplicate another module's data and put two answers in the world. |
| Texture photographs mapped onto surfaces | **Not adopted.** See 7.2. |

### 7.2 Why photographic textures are not used

It is tempting to project the HAER tower photograph onto the tower. It is refused, for a reason that
matters more than it first appears: a photographic texture carries *apparent detail the geometry
does not have*. Rivet lines, lattice bracing and arch openings would appear on a surface that is
modelled as a plain tapered box. A reader cannot tell painted detail from modelled detail, and the
confidence overlay cannot mark it, because there is no part to mark.

So photographs are used as **reference** — to check proportion and to decide material — and are shown
in the viewer *beside* the model, never *on* it. When the arch openings are sourced they will be
modelled as geometry, graded, and rendered like everything else.

### 7.3 The obligation this creates

Any visual improvement made ahead of the survey is a loan against future work, and loans get
recorded. `OQ-021` tracks it: every presentation-layer decision that stands in for missing evidence
is listed there, with what would retire it. The viewer states the same thing on screen rather than
only in this document, because a render travels further than a methods section.

### 6.5 Licensing is a gate on display, not only on storage

Storage and display are different permissions and conflating them is how an all-rights-reserved
image ends up on a public page. Every ingested asset therefore records `display_permitted`
separately from `stored_copy`, so a viewer gallery reading the manifest can tell "cite this" from
"you may show this" rather than re-deriving it from a licence string.

**The worked example is HistoricBridges.org, SRC-005.** It is the most thorough photographic
documentation of this bridge available, and none of it may be used here. Its terms, read directly
from `historicbridges.org/info/about/`, require written permission secured before publication,
confirmed by a Letter of Agreement and an invoice, at a website fee of $50.00 per image, and grant
permission for **"one-time, one edition use only"** with **"all rights ... reserved in full"**.

The fee is not the obstacle. **One-edition permission cannot be satisfied by an open repository at
all**, because anyone may fork and redistribute it, which is precisely what CC BY 4.0 invites. No
payment would fix that, so the question is closed rather than deferred.

What remains permitted, and what this project does instead:

- **Link to the gallery.** Linking is not reproduction. `SOURCE-REGISTER.md` carries the URL and
  the viewer offers it as an outbound reference.
- **Use the data on the same site that is not theirs to license.** The National Bridge Inventory
  sheet at that domain is federal data submitted by NYSDOT to FHWA. The *form layout* is
  HistoricBridges.org's; the *data* is public domain. Registered separately as SRC-024 for exactly
  that reason, and it turned out to be the more valuable half.
- **Look at the photographs while modelling.** Reading a source and republishing it are different
  acts. Proportions checked against a copyrighted photograph are fine; the photograph does not come
  with them.
