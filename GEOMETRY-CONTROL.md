# Geometry Control

**This file is the source of truth for all dimensional values in this repository.**

`scripts/build_control_skeleton.py` *parses this file*. It does not carry its own copy of any dimension. If a number
is not in a control table below, it does not exist in the model. To change the model, change this file.

Milestone 2 status: 19 placeholders at Milestone 1 have been reduced to 7. Milestone 3 examined both period
engineering journals directly — *Scientific American* (1908) and *The Engineering Record* (1904) — which promoted
roughly twenty controls to grade `A`, corrected the saddle elevation, corrected the pier capstone elevation, and
exposed one citation error in a downstream source. Every retirement and correction is attributed below.

---

## 1. Coordinate system and datum

| Item | Definition |
|---|---|
| World units | meters |
| Origin | midpoint of the main span, on the bridge longitudinal centerline, at the vertical datum |
| Vertical datum | mean high water (MHW), `z = 0` |
| +X | along the bridge longitudinal axis, toward the **Brooklyn** end |
| -X | along the bridge longitudinal axis, toward the **Manhattan** end |
| +Y | across the bridge, toward the **north** side |
| +Z | vertical, up |
| Handedness | right-handed, Z-up (glTF export converts to Y-up) |
| HO export scale | 1 : 87.1, see [SCALE-HO.md](/c:/Dev/manhattan-bridge-3d/SCALE-HO.md) |

The Manhattan-is-negative-X convention is a **modelling convention**, not a survey fact. Real-world azimuth of the
bridge axis is not yet registered; see Open Question OQ-009.

**Transverse naming.** SRC-011 designates the four stiffening trusses **A, B, C, D from south to north**. This
repository therefore maps truss A to `y = -48 ft`, B to `y = -20 ft`, C to `y = +20 ft`, D to `y = +48 ft`. Each main
cable lies directly above its truss (SRC-011, SRC-012).

---

## 2. Tier A / B control dimensions

Machine-parsed. Column contract: `Control ID | Key | Value | Unit | Source IDs | Confidence | Notes`.
`Value` must be a bare decimal number with no thousands separators. `Unit` must be one of
`ft`, `in`, `m`, `mm`, `count`, `ratio`.

| Control ID | Key | Value | Unit | Source IDs | Confidence | Notes |
|---|---|---:|---|---|---|---|
| CTL-001 | total_bridge_and_approaches_length | 6855 | ft | SRC-000, SRC-001, SRC-011, SRC-013 | A | Total bridge including approaches, excluding plazas. Corroborated by the 1909 plaque. |
| CTL-002 | lower_level_abutment_to_abutment | 5790 | ft | SRC-000, SRC-001 | A | See CONF-003; SRC-011 gives 5779 ft. Placement assumed symmetric, see OQ-002. |
| CTL-003 | upper_roadway_portal_to_portal | 6090 | ft | SRC-000, SRC-001 | A | See CONF-004; SRC-011 gives 6086 ft. Placement assumed symmetric, see OQ-002. |
| CTL-004 | anchorage_to_anchorage_suspended_length | 2920 | ft | SRC-000, SRC-001, SRC-002, SRC-011 | A | Suspended length. Consistent with CTL-005 + 2 x CTL-006. |
| CTL-005 | main_span | 1470 | ft | SRC-000, SRC-002, SRC-011, SRC-013, SRC-015, SRC-016, SRC-024 | A | **Corroborated in 2010 by federal inventory data**: SRC-024 records the maximum span as 448 m = 1469.8 ft, agreeing to 0.01 percent with a source a century newer than the period primaries. Tower centerline to tower centerline. Confirmed by two period primaries. See CONF-006. |
| CTL-006 | side_span_each | 725 | ft | SRC-000, SRC-002, SRC-011, SRC-015 | A | Each suspended side span. Confirmed by a period primary. |
| CTL-007 | tower_height_above_mhw | 322 | ft | SRC-000, SRC-001 | A | Retained as the handoff value. NOT used for geometry; see CTL-018 and CONF-005. |
| CTL-008 | center_clearance_above_mhw | 135 | ft | SRC-000, SRC-001, SRC-013, SRC-015, SRC-016, SRC-024 | A | Design clearance at midspan, underside of the suspended structure. Confirmed by two period primaries. SRC-014 surveys 134 ft, see CONF-007. |
| CTL-009 | roadway_width | 46 | ft | SRC-000, SRC-001 | A | Resolved by Milestone 2: this is the sum of the two upper roadways (CTL-026 + CTL-027 = 46.5 ft), not a single deck width. Retained for traceability; geometry uses the individual widths. |
| CTL-010 | stiffening_truss_depth_asce | 24 | ft | SRC-000, SRC-002, SRC-011 | A | ACTIVE truss depth control. Three independent sources agree. See CONF-002. |
| CTL-011 | stiffening_truss_depth_alt | 26 | ft | SRC-000, SRC-012 | B | Alternate reference depth. Recorded, not used for geometry. |
| CTL-012 | main_cable_length | 3224 | ft | SRC-000, SRC-001, SRC-013 | A | The 1909 plaque states "length of each of the four cables". This resolves OQ-005: the figure is per cable and includes the anchorage-embedded run. |
| CTL-013 | main_cable_diameter_asce | 20.75 | in | SRC-000, SRC-002 | A | See CONF-001. |
| CTL-014 | main_cable_diameter_haer | 21.25 | in | SRC-000, SRC-015 | A | **Measured on the wires, excluding wrapping and sheathing** (SRC-015, direct). This qualifier largely explains CONF-001. |
| CTL-015 | main_cable_count | 4 | count | SRC-002, SRC-011, SRC-013, SRC-015 | A | |
| CTL-016 | subway_track_count | 4 | count | SRC-011, SRC-012 | A | Present-day arrangement: two tracks under each of the two upper roadways, all on the lower level. The 1908 design differed, see CONF-011. |
| CTL-017 | subway_track_gauge | 4.708333 | ft | SRC-010 | B | Standard gauge, 4 ft 8.5 in. Applicability to be confirmed against SRC-004. |
| CTL-018 | cable_saddle_elevation | 322.5 | ft | SRC-015 | A | **ACTIVE saddle control.** SRC-015: the fixed saddles bolted to the tower tops, carrying the main cables, are 322.5 ft above mean high water. Agrees with the handoff's CTL-007. Replaces the 330 ft transmitted figure. See CONF-005. |
| CTL-019 | tower_height_plaque | 336 | ft | SRC-013 | A | "Height of steel towers above mean high water" on the 1909 plaque. Recorded, not used for geometry. |
| CTL-020 | tower_finial_height | 350 | ft | SRC-012 | B | Ornamental finials above high water. **Now used**: with CTL-018 it derives CTL-113, the finial height above the saddle, which is what the tower-top ornament is built from. |
| CTL-021 | deck_overall_width | 120 | ft | SRC-011, SRC-013, SRC-015, SRC-016 | A | "A double-deck structure about 120 feet wide" (SRC-016); "the total width of the floor of the bridge will be 120 feet" (SRC-015). |
| CTL-022 | truss_offset_inner | 20 | ft | SRC-011, SRC-015 | A | Trusses B and C. SRC-015: "a spacing of 40 feet between the inside trusses", so 20 ft each side of centerline. |
| CTL-023 | truss_offset_outer | 48 | ft | SRC-011, SRC-015 | A | Trusses A and D. SRC-015: "each pair of trusses will measure 28 feet from center to center", so 20 + 28 ft. |
| CTL-024 | lower_roadway_width | 35 | ft | SRC-011, SRC-013, SRC-015 | A | SRC-015: "the central roadway for vehicles 35 feet wide will occupy the center of the bridge on the level of the lower deck of the trusses". |
| CTL-025 | footwalk_width | 10 | ft | SRC-011, SRC-013, SRC-015 | A | SRC-015: "two footways each 10 feet wide, will be [carried on] the outside of the outer trusses, on cantilever extensions of the floor beams". |
| CTL-026 | upper_roadway_east_width | 24 | ft | SRC-012 | B | Manhattan-bound, north-east side, carried on trusses C-D. A later arrangement than SRC-015 describes. |
| CTL-027 | upper_roadway_west_width | 22.5 | ft | SRC-012 | B | Brooklyn-bound, south-west side, carried on trusses A-B. |
| CTL-028 | tower_pier_extent_x | 68 | ft | SRC-016 | A | Masonry pier at the capstone, measured along the bridge. "About 68 feet wide ... on top" (SRC-016, direct). |
| CTL-029 | tower_pier_extent_y | 134 | ft | SRC-016 | A | Masonry pier at the capstone, measured transversely. Slightly wider than the 120 ft deck, as expected. |
| CTL-030 | tower_pier_top_above_mhw | 23 | ft | SRC-016 | A | "At a height of about 23 feet above mean high tide" (SRC-016, direct, explicit). Supersedes the 31 ft I derived from SRC-015's summary heights. See CONF-009 and OQ-016. |
| CTL-031 | tower_foundation_depth_below_mhw | 92 | ft | SRC-015, SRC-016 | A | "The cutting edge was sunk to a depth of 92 feet below mean high water" (SRC-016). Independently confirmed by SRC-015. Retires OQ-003. |
| CTL-032 | tower_pedestal_extent_x | 18 | ft | SRC-012 | B | Steel pedestal, longitudinal. The SRC-015 figure is damaged in OCR ("158 feet by 43 feet"), so the transmitted value is retained. |
| CTL-033 | tower_pedestal_extent_y | 43 | ft | SRC-012, SRC-015 | A | Steel pedestal, transverse. Confirmed directly by SRC-015. |
| CTL-034 | anchorage_extent_x | 237 | ft | SRC-012, SRC-015 | A | Anchorage length on the base, confirmed by the SRC-015 plate caption. |
| CTL-035 | anchorage_extent_y | 182 | ft | SRC-012 | B | Anchorage width. The SRC-015 sentence is damaged in OCR ("covers ... feet 10 inches"), so the transmitted value is retained. |
| CTL-036 | anchorage_extent_z | 135 | ft | SRC-012, SRC-015 | A | Anchorage height, confirmed by the SRC-015 plate caption. |
| CTL-037 | suspender_panel_points_total | 628 | count | SRC-011 | A | Panel points across all four cables, from the 2009-2013 suspender replacement contract. |
| CTL-038 | suspender_rope_count | 1256 | count | SRC-011 | A | Two ropes per panel point. |
| CTL-039 | manhattan_approach_and_plaza_length | 2510 | ft | SRC-012 | B | As quoted when the bridge was built. Used only for the approach length **ratio**, see CTL-119 derivation. |
| CTL-040 | brooklyn_approach_and_plaza_length | 2370 | ft | SRC-012 | B | As above. |
| CTL-041 | cable_wire_count | 9472 | count | SRC-011, SRC-015 | A | 37 strands of 256 wires, confirmed by a period primary. See CONF-008. |
| CTL-042 | main_cable_diameter_measured | 21.2 | in | SRC-011 | A | Modern measured overall diameter, 55.2 cm. See CONF-001. |
| CTL-043 | cable_wire_diameter | 0.198 | in | SRC-011 | A | 5 mm, modern measurement. See CONF-010. |
| CTL-044 | cable_wire_diameter_sa | 0.1875 | in | SRC-015 | A | 3/16 in as designed. See CONF-010. Recorded, not used for geometry. |
| CTL-045 | tower_steel_height_1904 | 330 | ft | SRC-016 | A | "The towers are to be of steel 330 feet high" (SRC-016, direct). This is the height of the steel tower, **not** the tops of the cables as SRC-012 glossed it. Consistent with a saddle at 322.5 ft sitting below the tower top. Recorded, not used for geometry. |
| CTL-046 | tower_caisson_height | 47.5 | ft | SRC-016 | A | "The New York caisson is 78 feet wide, 144 feet long and 47.5 feet high" (SRC-016, direct). See CONF-013. |
| CTL-047 | tower_pier_masonry_height | 67 | ft | SRC-015 | A | Solid masonry carried above the caisson (SRC-015). Does not reconcile with the SRC-016 elevations, see OQ-016. Recorded, not used for geometry. |
| CTL-048 | tower_foundation_to_capstone_height | 123 | ft | SRC-015 | A | Total height, foundation to pier capstone (SRC-015). Against SRC-016's explicit elevations this would be 115 ft. Recorded, not used for geometry. See OQ-016. |
| CTL-049 | tower_caisson_extent_x | 78 | ft | SRC-015, SRC-016 | A | Foundation footprint along the length of the bridge. Confirmed by both period primaries. |
| CTL-050 | tower_caisson_extent_y | 144 | ft | SRC-015, SRC-016 | A | Foundation footprint measured transversely. Confirmed by both period primaries. |
| CTL-051 | tower_pedestal_depth | 5.5 | ft | SRC-015 | A | Wrought-steel pedestal total depth. Recorded, not used for geometry. |
| CTL-052 | anchorage_arch_width | 46 | ft | SRC-015 | A | Street thoroughfare arch through each anchorage. Recorded for Milestone 4. |
| CTL-053 | tower_caisson_height_sa | 56 | ft | SRC-015 | A | Alternate caisson height. Recorded, not used for geometry. See CONF-013. |
| CTL-054 | tower_pier_footing_below_mhw | 33 | ft | SRC-016 | A | Piers "seated on concrete footings about 33 feet below high water level". The masonry pier runs from here to the capstone. |
| CTL-055 | tower_rock_depth_min_below_mhw | 100 | ft | SRC-016 | A | Test borings located rock 100 to 129 ft below MHW. The caisson stopped above it, on dense sand and gravel. Recorded for context. |
| CTL-056 | tower_leg_width_transverse | 5 | ft | SRC-015 | A | "Each leg having a uniform width transversely to the axis of the bridge of 5 feet" (SRC-015, direct). |
| CTL-062 | floor_beam_depth | 37 | in | SRC-012, SRC-018 | B | Floor beams under the lower level. Stated by SRC-018 without a citation and by SRC-012 citing a 1930s newspaper account; no engineering primary examined. Used only to ground the CTL-104 placeholder, see OQ-013. |
| CTL-057 | tower_leg_length_at_base | 32 | ft | SRC-015 | A | Leg dimension parallel to the bridge axis at the pedestal. "Varying from 32 feet at the base to 10 feet at the top." |
| CTL-058 | tower_leg_length_at_top | 10 | ft | SRC-015 | A | Leg dimension parallel to the bridge axis at the tower top. |
| CTL-059 | tower_leg_count | 4 | count | SRC-015 | A | "Four huge box-section legs heavily braced together." The legs stand in the planes of the four stiffening trusses (SRC-015: "the suspended roadway will consist of four trusses carried in the planes of the legs of the towers"), so their transverse positions are CTL-022 and CTL-023. |
| CTL-060 | tower_diaphragm_depth | 7.5 | ft | SRC-015 | B | "Two intersecting plate-steel diaphragms of a general I section, which are 7.5 feet in depth." The OCR reads "714 feet", almost certainly 7 1/2. Recorded, not used for geometry. |
| CTL-061 | truss_panel_length | 18.6076 | ft | SRC-011 | B | Warren truss panel length, derived from the sourced 628 panel points (CTL-037). Recorded here so the truss webbing and the suspender pitch share one control. See section 4.4. |

---

## 3. Placeholder parameters — NOT dimensional facts

Machine-parsed with the same column contract. **Every row here is confidence `D`.** These are shape hints, not
measurements. They must not be cited, exported as dimensions, or used to validate any imported mesh.

Milestone 2 reduced this table from 19 rows to 7. The survivors are all small vertical framing offsets and the
transverse track positions.

| Control ID | Key | Value | Unit | Source IDs | Confidence | Notes |
|---|---|---:|---|---|---|---|
| CTL-101 | min_suspender_length_at_midspan | 3 | ft | none | D | PLACEHOLDER. Vertical gap between the truss top chord and the main cable at midspan, which is what sets the sag. Bounded above by the fact that the cable must clear the chord and below by zero, so the derived sag is accurate to a few feet. Retired by SRC-004. See OQ-001. |
| CTL-102 | cable_saddle_drop_below_cable_top | 0 | ft | none | D | PLACEHOLDER. Drop from the top of the cable at the tower (CTL-018) to the cable centerline at the saddle seat. Currently zero, so the model treats CTL-018 as the cable centerline. Retired by SRC-004. |
| CTL-103 | upper_deck_structure_depth | 3 | ft | none | D | PLACEHOLDER. Structural depth of the upper roadway deck above the truss top chord. Retired by SRC-004. See OQ-013. |
| CTL-104 | lower_deck_offset_above_clearance | 3.4 | ft | none | D | PLACEHOLDER, but no longer arbitrary. The floor beams under the lower level are 37 in deep (CTL-062), so the running surface must sit at least that far above the clearance plane; 3.4 ft adds a nominal 4 in of deck. Was a flat 2 ft guess at Milestone 1. Retired by SRC-004. See OQ-013. |
| CTL-105 | subway_track_bay_inner_offset | 27 | ft | none | D | PLACEHOLDER. Transverse offset to the innermost track centerline of each side. **Now bounded**: SRC-011 places the tracks between the inner truss (CTL-022, 20 ft) and the outer truss (CTL-023, 48 ft), so this value cannot be far wrong. Retired by SRC-004. See OQ-010. |
| CTL-106 | subway_track_spacing_y | 14 | ft | none | D | PLACEHOLDER. Transverse spacing between the two tracks in the same bay. Bounded by the 28 ft truss bay. Retired by SRC-004. See OQ-010. |
| CTL-107 | subway_track_structure_depth | 1.5 | ft | none | D | PLACEHOLDER. Rail-top height above the lower deck reference plane, used only to separate the track envelope from the deck envelope visually. Retired by SRC-004. See OQ-013. |
| CTL-108 | approach_bent_spacing | 100 | ft | none | D | PLACEHOLDER. Longitudinal spacing of the approach viaduct bents. Chosen only so the approach reads as a supported viaduct rather than a floating slab; no source gives it. The *extent* it is applied over is sourced (CTL-002, CTL-003), the rhythm is not. Retired by SRC-004. See OQ-020. |
| CTL-109 | approach_bent_width_y | 8 | ft | none | D | PLACEHOLDER. Transverse width of an approach viaduct bent column. See OQ-020. |
| CTL-110 | approach_girder_depth | 10 | ft | none | D | PLACEHOLDER. Structural depth carrying the approach decks between bents. See OQ-020. |
| CTL-111 | tower_arch_height_to_width_ratio | 3.3 | ratio | none | D | PLACEHOLDER, but not arbitrary: **measured off the HAER photograph** (SRC-018) by `scripts/measure_arch_from_photo.py`, which reports 162 px tall against 49 px wide for the lower opening. A ratio survives an uncalibrated projection where a length does not, so this is the one quantity that image is asked to supply. The *width* it multiplies is sourced (the gap between the centre legs, from CTL-056 and the truss offsets); the ratio is not. See OQ-023. |
| CTL-112 | tower_arch_head_rise_fraction | 0.5 | ratio | none | D | PLACEHOLDER. Fraction of the arch width taken by the rounded head, i.e. a semicircular head. The photograph shows the void narrowing at the top over a parallel-sided shaft, which is a round head; the exact rise is not measurable from one uncalibrated view. See OQ-023. |
| CTL-113 | tower_finial_top_above_saddle | 27.5 | ft | SRC-012, SRC-015 | B | **Derived, not guessed.** CTL-020 puts the ornamental finials 350 ft above high water and CTL-018 puts the cable saddle at 322.5 ft, so the finials stand 27.5 ft above the saddle. Both inputs are registered, so this inherits the weaker of their grades. It is the *height* only: the shape of the casting is unregistered, see OQ-023. |
| CTL-115 | anchorage_arch_springing_height | 30 | ft | none | D | PLACEHOLDER. Height at which the semicircular head of the anchorage thoroughfare arch springs from its jambs. SRC-005's view under the arch shows a tall opening carrying a street with buildings visible through it, which bounds this loosely but does not measure it. Note the head itself is NOT a placeholder: a semicircular vault has rise = half-width, so CTL-052 fixes the crown once the springing is set. See OQ-024. |
| CTL-116 | anchorage_arch_jamb_width | 12 | ft | none | D | PLACEHOLDER. Thickness of the masonry jamb either side of the opening. Affects only how heavy the arch reads, not where anything else sits. See OQ-024. |
| CTL-114 | navigation_horizontal_clearance | 1230 | ft | SRC-024 | A | Federal navigation clearance between the tower piers, 374.9 m. Not the same quantity as CTL-005: the main span is measured tower centreline to centreline, while this is the clear water opening, so the 240 ft difference is the two piers plus their standoff. Recorded; not yet used for geometry. |

---

## 4. Derivation rules

Computed by `scripts/build_control_skeleton.py` from the tables above. `ft2m = 0.3048`.

### 4.1 Longitudinal stations (X, meters)

| Station ID | Rule | Confidence | Note |
|---|---|---|---|
| STA-MID | `0` | A | Origin, main span midpoint. |
| STA-TWR-M | `-main_span / 2` | A | Manhattan tower centerline. |
| STA-TWR-B | `+main_span / 2` | A | Brooklyn tower centerline. |
| STA-ANC-M | `-(main_span / 2 + side_span_each)` | A | Manhattan anchorage cable point. |
| STA-ANC-B | `+(main_span / 2 + side_span_each)` | A | Brooklyn anchorage cable point. |
| STA-ABUT-M / B | `-/+ lower_level_abutment_to_abutment / 2` | D | Symmetric placement assumed, see OQ-002. |
| STA-PORTAL-M / B | `-/+ upper_roadway_portal_to_portal / 2` | D | Symmetric placement assumed, see OQ-002. |
| STA-APPR-END-M | `-(anchor_x + approach_total * manhattan_approach_fraction)` | B | `approach_total = CTL-001 - CTL-004`. `manhattan_approach_fraction = CTL-039 / (CTL-039 + CTL-040) = 0.5143`. Upgraded from a `D` 50/50 guess at Milestone 1. |
| STA-APPR-END-B | `+(anchor_x + approach_total * (1 - manhattan_approach_fraction))` | B | As above. |

Consistency identity checked at build time: `main_span + 2 * side_span_each == anchorage_to_anchorage_suspended_length`.

### 4.2 Elevations (Z, meters relative to MHW)

| Elevation ID | Rule | Confidence | Note |
|---|---|---|---|
| ELV-FOUNDATION | `-tower_foundation_depth_below_mhw` | A | Caisson cutting edge, 92 ft below MHW. Confirmed by both period primaries. |
| ELV-CAISSON-TOP | `ELV-FOUNDATION + tower_caisson_height` | A | Top of the New York caisson, 44.5 ft below MHW. |
| ELV-PIER-FOOTING | `-tower_pier_footing_below_mhw` | A | Concrete footing on which the masonry pier is seated, 33 ft below MHW. |
| ELV-DATUM | `0` | A | Mean high water. |
| ELV-PIER-TOP | `tower_pier_top_above_mhw` | A | Pier capstone, base of the steel tower, 23 ft above MHW. See CONF-009 and OQ-016. |
| ELV-CLEARANCE | `center_clearance_above_mhw` | A | Underside of the suspended structure at midspan. |
| ELV-TRUSS-BOTTOM | `ELV-CLEARANCE` | B | Bottom chord taken at the clearance plane. |
| ELV-TRUSS-TOP | `ELV-CLEARANCE + stiffening_truss_depth_asce` | A | Both inputs are `A`. |
| ELV-LOWER-DECK | `ELV-CLEARANCE + lower_deck_offset_above_clearance` | D | Placeholder offset. |
| ELV-UPPER-DECK | `ELV-TRUSS-TOP + upper_deck_structure_depth` | D | Placeholder deck depth. |
| ELV-SADDLE | `cable_saddle_elevation - cable_saddle_drop_below_cable_top` | A | Now stated directly by a period primary source (SRC-015). |
| ELV-CABLE-MID | `ELV-TRUSS-TOP + min_suspender_length_at_midspan` | D | **Derived, not guessed.** Fixed by the geometry: the cable must meet the truss top chord at midspan, where suspenders reach minimum length. |
| ELV-ANCHOR-POINT | `anchorage_extent_z` | A | Cable enters the anchorage at the top of the block. |

**Derived main span sag** = `ELV-SADDLE - ELV-CABLE-MID` = 322.5 - (135 + 24 + 3) = **160.5 ft**, a sag ratio of 1/9.16.

This sits inside the 1/7 to 1/12 band typical of suspension bridges. It moved from 168 ft at Milestone 2 because
SRC-015 supplied a saddle elevation of 322.5 ft in place of the 330 ft previously transmitted through SRC-012.

Cross-check against CTL-012: a parabola of 1470 ft span and 160.5 ft sag has an arc length of about 1516 ft; the two
side span chords add about 745 ft each; the total is about 3006 ft against the stated 3224 ft per cable. The 218 ft
residual is the run embedded in the two anchorages, roughly 109 ft per end, which is close to the 110 ft eyebars
recorded in SRC-012. This is a **consistency check, not a determination** — the cable length is only weakly
sensitive to sag.

### 4.3 Transverse layout (Y, meters)

| Item | Rule | Confidence |
|---|---|---|
| Truss A / cable south outer | `-truss_offset_outer` | A |
| Truss B / cable south inner | `-truss_offset_inner` | A |
| Truss C / cable north inner | `+truss_offset_inner` | A |
| Truss D / cable north outer | `+truss_offset_outer` | A |
| Upper roadway, Brooklyn-bound | centered in the A-B bay, width `upper_roadway_west_width` | B |
| Upper roadway, Manhattan-bound | centered in the C-D bay, width `upper_roadway_east_width` | B |
| Lower roadway | centered on the centerline, width `lower_roadway_width` | A |
| Footwalk / bikeway | outboard of trusses A and D, width `footwalk_width` | A |
| Subway tracks | two per side, in the A-B and C-D bays, at `subway_track_bay_inner_offset` and `+ subway_track_spacing_y` | D |

### 4.4 Curves

| Curve | Rule | Confidence |
|---|---|---|
| Main cable, main span | Parabola through `(STA-TWR-M, ELV-SADDLE)`, `(0, ELV-CABLE-MID)`, `(STA-TWR-B, ELV-SADDLE)` | B (endpoints A, sag D) |
| Main cable, side span | Chord from `(STA-TWR, ELV-SADDLE)` to `(STA-ANC, ELV-ANCHOR-POINT)` less a parabolic sag term `4 * f_side * t * (1 - t)`, `f_side = sag_main * (side_span / main_span)^2` | D |
| Deck centerline | Straight line at `y = 0`, `z = ELV-UPPER-DECK`, from `STA-APPR-END-M` to `STA-APPR-END-B` | B |
| Suspenders | Vertical lines at the derived panel pitch from the cable curve down to `ELV-TRUSS-TOP`, within the suspended length | B |

**Derived suspender panel pitch.** `CTL-037 / CTL-015 = 157` panel points per cable. Searching integer panel counts
against the sourced spans gives a unique consistent solution: 79 panels in the main span and 39 in each side span,
totalling 157, at a pitch of `1470 / 79 = 18.608 ft` (side spans `725 / 39 = 18.590 ft`). No other integer solution
in the plausible range reproduces 157. This replaces the arbitrary 30 ft pitch used at Milestone 1.

---

## 5. Open questions

| ID | Question | Blocks | Retired by | Status |
|---|---|---|---|---|
| OQ-001 | Main span cable sag is not stated by any registered source. | Cable profile, suspender lengths | SRC-004, SRC-015 | **Mitigated.** Now derived geometrically to within a few feet, and cross-checked against cable length. Only CTL-101 remains free. |
| OQ-002 | Longitudinal placement of abutments and portals relative to midspan is unregistered; symmetry is assumed. | Abutment and portal stations | SRC-001, SRC-004 | Open, immaterial to built geometry. |
| OQ-003 | Tower foundation depth below MHW. | Tower base | SRC-015 | **Retired** by CTL-031 (92 ft), now from a directly examined primary. |
| OQ-004 | Which deck the 46 ft roadway width refers to. | Deck widths | SRC-011, SRC-013 | **Retired**: it is the sum of the two upper roadways. Individual widths are now controls. |
| OQ-005 | Measurement extent of the 3224 ft cable length. | Cable length check | SRC-013 | **Retired**: per cable, including the anchorage run. |
| OQ-006 | Split of approach length between the two sides. | Approach stations | SRC-012 | **Mitigated**: ratio derived from CTL-039/CTL-040 as 0.5143. Absolute lengths still include plazas, so the split is a ratio only. |
| OQ-007 | Tower plan dimensions, leg spacing, arch openings. | Tower geometry | SRC-004 | **Mostly retired**: caisson (78 x 144 ft), pier (68 x 134 ft), pedestal (18 x 43 ft) and the full vertical build-up are registered. SRC-015 adds that the towers have four columns in the planes of the trusses. Arch openings and column taper still open. |
| OQ-008 | Anchorage plan dimensions. | Anchorage geometry | SRC-015 | **Retired** by CTL-034/035/036, two of the three now confirmed directly. |
| OQ-009 | Real-world azimuth and geodetic anchor of the bridge axis. | Georeferencing | SRC-001, SRC-003, SRC-004 | **Mitigated, still open.** A placement is now published and ratified at confidence C; see section 6. It remains open because both horizontal estimates derive from mapped alignments rather than survey. **Milestone 9: a second independent geodetic point.** SRC-024, the 2010 federal inventory, gives 40.706667, -73.990278 for this structure. Projected into the shared frame it lies 111.4 m along the published bridge axis and only **0.6 m off the published centreline**. That is corroboration of the azimuth from a dataset that played no part in deriving it, which previously rested on OpenStreetMap alone. It does not refine the estimate: NBI coordinates are given only to the nearest second, so about +/-15 m here, which at 111 m along the axis bounds the azimuth error to roughly +/-8 deg -- far looser than the +/-0.35 deg already established. It excludes gross error and nothing finer. Still open. |
| OQ-010 | Exact transverse centerlines of the four subway tracks. | Track placement | SRC-004 | **Mitigated**: tracks are confirmed to lie in the A-B and C-D truss bays, bounding them between 20 ft and 48 ft from centerline. Note CONF-011: the 1908 design put two of them on the upper deck. |
| OQ-011 | Conflict CONF-001, main cable diameter. | Cable solid geometry | SRC-004 | **Largely explained**: SRC-015's 21.25 in is on the wires excluding wrapping, which reconciles three of the four figures. |
| OQ-012 | Conflict CONF-002, stiffening truss depth. | Truss depth | — | **Effectively resolved** toward 24 ft. The SRC-015 sentence is OCR-damaged at exactly that number. |
| OQ-013 | Vertical framing depths of the upper deck, lower deck and track structure. | Deck envelope thicknesses | SRC-004 | Open. These are the last significant placeholders. |
| OQ-014 | The transverse layout closes to 116 ft against a sourced 120 ft deck, leaving about 2 ft per side unaccounted. | Deck edge detail | SRC-004 | **Explained, not closed.** SRC-015 states the footways are carried "on cantilever extensions of the floor beams" outside the outer trusses, so the residual is the cantilever tip, fascia and railing beyond the 10 ft walking surface. No source gives that dimension. Tracked by GRT-009. |
| OQ-015 | Top of the masonry pier above MHW. | Tower pier height | SRC-016 | **Retired.** SRC-016 states 23 ft explicitly; see CONF-009. |
| OQ-016 | The two period primaries give vertical build-ups that differ by 8 ft. SRC-016: cutting edge -92 ft, caisson 47.5 ft high, footing seat -33 ft, capstone +23 ft (115 ft overall). SRC-015: caisson 56 ft, masonry 67 ft, 123 ft overall, which against -92 ft implies a capstone at +31 ft. | Tower foundation internals | SRC-004 | New at Milestone 3. The model follows SRC-016 throughout because its figures are explicit elevations rather than summary heights, and they are internally consistent. The SRC-015 heights are recorded as CTL-047, CTL-048 and CTL-053 but are not used. |
| OQ-017 | Warren truss diagonal direction at each panel, chord and diagonal member sections, and the tower bracing arrangement. | Truss and tower web detail | SRC-004, SRC-005 | New at Milestone 4. The truss depth, spacing and panel count are all sourced, so the panel *positions* are correct; the alternating diagonal pattern is the Warren form named by three sources but its handedness at each panel is not documented. Detail photographs (SRC-005) could settle it to grade B. **Milestone 9: the verticals question is answered, and the model was already right.** SRC-005's gallery carries separate captioned views of "Diagonal members" and "Vertical members", and the photographs show both: built-up riveted diagonals with lattice bracing, and vertical members rising to panel points on the top chord. The web this model already draws -- alternating diagonals with a vertical at every panel point -- is therefore corroborated rather than corrected. What remains open is narrower than before: not *whether* verticals exist, but the diagonal handedness at each panel and the member sections. Photography establishes existence, not position, so the web stays grade D. |
| OQ-018 | The consuming district's `foreign_assets` tile declarations disagree with the placement that same district published. | District-side streaming of the proxy, not this module's geometry | dumbo-district-3d | New at Milestone 5. Not a defect in this repository; see section 6.3. A corrected tile set has been computed and offered at `viewer/metadata/proposed_foreign_assets.json`. Open until the district accepts or rebuts it. |
| OQ-019 | Materials are unregistered for the anchorages, the caissons, the cables, the stiffening trusses and both roadway surfaces. | Rendered appearance, not dimensions | SRC-004, SRC-005 | New at Milestone 6. See section 7. The tower pier (masonry), its footing (concrete) and the tower steel are grade A from period primaries; everything else is inferred or placeholder. No dimension depends on this, but the rendered image does, so it is graded rather than assumed silently. |
| OQ-020 | The approach viaducts' structural form is unregistered: bent spacing, girder type and depth, pier form, and the longitudinal grade down to street level. | Approach geometry between the anchorage and the abutment/portal | SRC-004, SRC-011 | New at Milestone 6. The *extent* is sourced — CTL-002 puts the lower level's abutments at +/-882.4 m and CTL-003 puts the upper roadway's portals at +/-928.1 m, both grade A — so the structure demonstrably continues past the anchorage. What it looks like is not registered. The approach is therefore modelled to the sourced stations with a placeholder bent spacing, and drawn level because no source gives the grade. **Milestone 9: the form is now partly registered.** SRC-024 codes the approach design as "Truss - Deck [09]" in steel, which is a real statement about the structural type: the approaches are deck trusses, not the girder-on-bent arrangement the placeholder geometry draws. That is a qualitative fact and not a dimension, so CTL-108..110 remain placeholders and the geometry is unchanged, but the eventual replacement now has a named form to build toward. |
| OQ-021 | The presentation layer stands in for evidence that does not exist yet, and must be replaced by measured capture. | Rendered appearance only. **No dimension depends on this.** | SRC-004, a walkway image set, SfM with scale control | New at Milestone 8. See CONFIDENCE-MODEL.md section 7. Open items: (a) **partly addressed** — the tower arch openings and finials are now modelled as graded geometry (see OQ-023), but their dimensions rest on a photograph rather than a drawing; (b) the truss web is drawn as lines rather than members, because OQ-017 leaves the diagonal handedness unknown; (c) no surface carries real texture, only a graded material finish; (d) the finial *shape* is engineering judgement; only its height is derived from a source. Retired progressively as each becomes sourced geometry. |
| OQ-022 | SRC-018 supplies a HAER photograph captioned **NY-127-7**, but this repository's register records the Manhattan Bridge HAER survey as **NY-164** (item `ny0980`), verified by direct Library of Congress API query. | Citation accuracy for the photographic record | SRC-003 | New at Milestone 8. The photograph is unmistakably this bridge — the four-column towers, arch portal and two-level deck all match. Either NY-127 is an earlier or parallel survey number, or the caption is wrong. Recorded rather than resolved, because a citation that cannot be reproduced is not yet a citation. The image is used as visual reference only, which no grade depends on. |
| OQ-023 | The tower arch openings and the ornamental finials are modelled from a photograph, not from a dimension. | Tower appearance. **No other geometry depends on them.** | SRC-004 | New at Milestone 8. SRC-018 establishes beyond doubt that the openings and finials *exist*, what shape they are, and where they sit relative to the legs and the deck — so the geometry is `INFERRED`, not `ASSUMED`. What no source gives is their size. CTL-111 is a proportion measured off the photograph, CTL-112 assumes a semicircular head, and CTL-113 is a frank guess at finial height. The arch *width* is sourced, being the gap between the centre legs; only its height and head shape are not. A single elevation drawing retires all three at once. |
| OQ-024 | The anchorage thoroughfare arch's springing height and jamb thickness are unregistered. | Anchorage appearance. No other geometry depends on it. | SRC-004, SRC-015 | New at Milestone 10. Unusually well constrained for a new open question: CTL-052 gives the opening width as 46 ft at grade A, and a semicircular head means the rise equals the half-width, so the crown is derived rather than guessed. Only the height at which the vault springs and the jamb thickness remain judgement, as CTL-115 and CTL-116. SRC-005 photographs establish the form -- dressed coursed ashlar, semicircular barrel vault -- which is why the part is graded C rather than D. A single elevation drawing retires both placeholders. |

---

## 6. Georeferencing and the shared scene frame

This section registers where the module frame defined in section 1 sits in the real world. It exists
because `manhattan-bridge-3d` is consumed by `dumbo-district-3d` through the
`digital-3d-shared-contracts` v1 interface, and a consumer cannot place geometry authored in a
private frame without it. The published form is `viewer/public/bridge-manifest.json`.

Authoring does not change. Geometry stays in the module frame with `z = 0` at mean high water; the
transform to the shared frame happens at placement time.

### 6.1 Vertical datum — grade A

| Item | Value |
|---|---|
| Module vertical datum | MHW (mean high water) |
| Shared frame vertical datum | NAVD88 |
| Correction applied at placement | `z_navd88 = z_mhw + 0.59` |

**Independently verified.** Queried the NOAA CO-OPS API for station 8518750 (The Battery, NY), epoch
1983-2001, in meters on station datum:

| Datum | Value | |
|---|---:|---|
| MHHW | 2.543 | |
| MHW | **2.445** | |
| MSL | 1.785 | |
| MLW | 1.065 | |
| MLLW | 1.002 | |
| NAVD88 | **1.848** | |

`MHW - NAVD88 = 2.445 - 1.848 = 0.597 m`, which corroborates the 0.596 m NYSAPLS figure to 1 mm.

The shared frame publishes **0.59 m**. That is 7 mm below the measured 0.597 m, and 0.597 would
conventionally round to 0.60. The module adopts 0.59 anyway: the frame is frozen for the life of
contract major version 1, consistency across modules matters more than 7 mm, and 7 mm is two orders
of magnitude below the +/-0.61 m accuracy of the building footprints the bridge is placed against.
Recorded rather than silently accepted.

### 6.2 Horizontal placement — grade C, OQ-009 remains open

`dumbo-district-3d` proposed a provisional placement (DOQ-001) so integration could proceed. This
module reproduced their derivation from the same inputs and audited it rather than accepting it.

| Term | Value |
|---|---|
| Frame | `nyc-harbor-enu` |
| Translation | `[-150.22, 511.26, 0.59]` m |
| `yaw_deg` | 292.633 (module +X onto scene East, CCW looking down) |
| Azimuth of +X | 157.367 deg from north, toward Brooklyn |

**What the audit found.**

*The azimuth is stable.* Refitting the principal axis over subsets of the mapped alignment gives
157.367 deg for all 72 points, 157.496 deg for the two long edge paths alone, and 157.024 deg for
the roadway ways alone. The spread is about +/-0.35 deg, which is +/-6 m of lateral error at the far
end of a 2,089 m structure and under +/-3 m across the DUMBO district.

*The translation has independent corroboration.* The ASCE Historic Civil Engineering Landmark
coordinate for this bridge, 40 deg 42' 27.0" N, 73 deg 59' 26.9" W, falls **11.8 m** from the
centroid of the mapped alignment. Two unrelated sources agreeing to 11.8 m over a 2 km structure is
materially better evidence than either alone.

*A defect was found and rejected as immaterial.* The mapped ways are edge paths, not a centreline:
37 points on the north bike path, 27 on the south pedestrian path, 8 on the roadway. The centroid is
therefore about 2.3 m north of the midline between the two paths. That is below the accuracy of the
placement as a whole and is not corrected.

*An alternative estimator was tested and rejected.* Using the midpoint of the mapped extent instead
of the centroid moves the origin 43.4 m along the axis and **away** from the ASCE coordinate, to
34.3 m. The mapped extent is 1,891 m against the 2,089 m of CTL-001, so OSM omits roughly 198 m of
approach, and asymmetric omission biases an extent midpoint more than it biases a centroid. The
centroid is retained.

*An unexpected cross-check on deck width.* The two mapped edge paths are 35.3 m apart. CTL-021 gives
a 120 ft (36.58 m) deck, and CTL-023 plus CTL-025 put the footwalk centrelines 32.3 m apart. The
mapped separation falls between those two, which is where paths inboard of the deck edge should sit.
This is weak corroboration of the sourced deck width from a completely independent dataset.

**Why grade C and not higher.** Both horizontal terms derive from mapped alignments, not survey.
OpenStreetMap is community mapping; the ASCE landmark coordinate is a representative point for the
structure and is not documented as the main-span midpoint. Grade C matches CONFIDENCE-MODEL.md:
derived from an existing dataset aligned to controls.

**Why `provisional: false` nonetheless.** In the shared contract, `provisional` means "proposed by a
consumer and not yet ratified by the owning module". This module has now audited and adopted it, so
the flag is cleared and ownership moves here. The honest signal moves to `confidence: C` and to
OQ-009, which stays open until a geodetic anchor is registered from an archival drawing or survey.

**What would retire OQ-009.** A tower centre coordinate from SRC-004, or any survey monument on the
structure. Because the tower centrelines are exactly `+/- main_span / 2` from the origin along the
axis, a single surveyed tower position would fix both the anchor and the azimuth to grade A.


### 6.3 The consuming district's tile declarations disagree with its own placement — OQ-018

The district's tile index names `urn:d3d:manhattan-bridge:bridge_proxy` in the `foreign_assets` of
twelve tiles, so that walking into one of those tiles streams the bridge. Applying the placement
published in section 6.2 to the level-2 proxy and asking which tiles the geometry actually occupies
gives a different set of twelve, overlapping the declared set in only six.

This is not a rounding disagreement. Walking the published axis across the district grid
(`scripts/check_corridor_geodetic.py`) shows the declared tile set has a principal azimuth of
**17.8 deg**, while the published placement axis runs at **157.4 deg** — a disagreement of
**40.4 deg**. Tile `t_5_2` lies about 358 m from the bridge axis, an order of magnitude beyond any
plausible deck half-width.

**The evidence favours the placement, not the tile list.** The placement origin sits **10.5 m** from
the ASCE landmark plaque coordinate (SRC-002), which is the only independently sourced geodetic
point on the structure in the register and played no part in deriving either artifact. Nothing
independent corroborates the declared tile set, and its azimuth is inconsistent with the placement
published in the same repository.

Both artifacts are owned by the district, so this repository does not change either. The corrected
membership is computed and written to `viewer/metadata/proposed_foreign_assets.json` by
`scripts/verify_placement.py`, and offered as a proposal.

The practical consequence, if it is not corrected, is that a visitor walking south-east along the
bridge would have the proxy unload while still underneath it, and see it appear over ground it does
not cross. That is a visible failure, which is why it is recorded here rather than left to the
integration to discover.

**Guard against regression.** `scripts/verify_placement.py` re-derives the occupied tile set from
the published GLB on every run and exits non-zero while the two disagree, so this cannot be
silently forgotten and cannot be broken by a future geometry change without notice.

---

## 7. Material assignments

Material is a geometric fact in the sense that matters here: it decides whether a rendered surface
reads as stone or as steel, and a viewer that paints the tower piers the same colour as the trusses
is making an unsourced claim just as surely as one that invents a dimension. So materials are
controlled here, with the same grading discipline as dimensions, rather than being chosen in the
renderer.

`applies_to` is matched against `part_id` as a glob. The first matching row wins, so order is
significant and the table runs from most specific to least. `material` is a closed vocabulary:
`masonry`, `concrete`, `steel_structural`, `steel_wire`, `roadway_surface`, `reference`.

| ID | applies_to | material | Sources | Confidence | Notes |
|---|---|---|---|---|---|
| MAT-001 | `tower_*_pier` | masonry | SRC-016 | A | CTL-028 and CTL-029 describe the "masonry pier at the capstone" directly. The **stone type is not registered** — the model says masonry, not granite. |
| MAT-002 | `tower_*_footing` | concrete | SRC-016 | A | CTL-054, piers "seated on concrete footings about 33 feet below high water level". |
| MAT-003 | `tower_*_caisson` | concrete | none | D | PLACEHOLDER. The caisson dimensions are grade A from both period primaries but **no registered source states what it is made of**. Period practice was a timber box with concrete fill; that is not a registered fact. See OQ-019. |
| MAT-004 | `tower_*_pedestal` | steel_structural | SRC-012, SRC-015 | A | CTL-032 "steel pedestal"; CTL-051 "wrought-steel pedestal total depth". |
| MAT-005 | `tower_*_leg*` | steel_structural | SRC-016 | A | CTL-045, "the towers are to be of steel 330 feet high", direct quotation. Corroborated by the 1909 plaque, CTL-019, "height of steel towers above mean high water". |
| MAT-006 | `tower_*_diaphragm*` | steel_structural | SRC-015 | B | CTL-060, "two intersecting plate-steel diaphragms". OCR-damaged at the dimension but not at the material. |
| MAT-017 | `tower_*_bracing` | steel_structural | SRC-016 | B | Part of the steel tower of CTL-045. The bracing *arrangement* is unregistered (OQ-017); only its material is carried here. |
| MAT-020 | `tower_*_arch_*` | steel_structural | SRC-016 | B | The arch openings are formed in the steel tower of CTL-045, so the surrounding material is the tower's own. The opening's *dimensions* are not sourced (OQ-023); its material is. |
| MAT-021 | `tower_*_finials` | steel_structural | SRC-012 | C | CTL-020 registers the finials' height above high water but names no material. Steel is inferred from their being carried on the steel tower; SRC-018's photograph shows a dark casting consistent with metal, not stone. Graded C rather than B because inference from a photograph is not a statement. |
| MAT-018 | `tower_*_centerline` | reference | none | D | Construction geometry, not fabric. See MAT-014. |
| MAT-007 | `*_main_cable_*` | steel_wire | SRC-011, SRC-015 | C | The sources establish the cable is built of 9472 drawn wires in 37 strands (CTL-041) and give the wire diameter (CTL-043), but **no registered passage names the metal**. Steel is inferred from the structure type and period. See OQ-019. |
| MAT-008 | `suspenders_*` | steel_wire | SRC-011 | C | As MAT-007. Suspender pitch is derived, not the material. |
| MAT-009 | `stiffening_truss_*` | steel_structural | SRC-011 | C | Three sources agree the stiffening trusses are Warren trusses 24 ft deep (CTL-010) but none that is registered names the metal. Inferred, consistent with the sourced steel towers. See OQ-019. |
| MAT-022 | `*_anchorage_arch` | masonry | SRC-005, SRC-015 | B | The thoroughfare arch is cut through the anchorage, so it is the same fabric: SRC-005's view under the south anchorage arch shows dressed, coursed ashlar forming the vault itself. Same grade and reasoning as MAT-010. |
| MAT-010 | `*_anchorage` | masonry | SRC-005, SRC-018 | B | **Promoted from D at Milestone 9.** Two registered photographic sources show coursed ashlar masonry: SRC-005's "View under south anchorage arch" shows a semicircular masonry barrel vault of dressed, coursed stone, and SRC-018's HAER view shows the same construction on the tower piers. Grade B rather than A because these are photographs rather than a specification, and SRC-005's images are undated. The stone *type* remains unregistered: the model says masonry, not granite. |
| MAT-011 | `*_approach*` | steel_structural | none | D | PLACEHOLDER. See OQ-020; the approach viaduct's structural form and material are both unregistered. |
| MAT-012 | `track_*` | steel_structural | none | D | PLACEHOLDER. Rail is steel by definition, but no registered source describes this bridge's rail, and SRC-010 is a gauge standard rather than a statement about the Manhattan Bridge. Graded D deliberately rather than borrowing authority from a source that does not carry it. |
| MAT-019 | `footwalk_*` | roadway_surface | none | D | PLACEHOLDER. SRC-015 establishes the footwalks are carried on cantilever extensions of the floor beams (OQ-014) but says nothing about the walking surface. |
| MAT-013 | `*_roadway_*` | roadway_surface | none | D | PLACEHOLDER. No registered source describes the wearing surface on either level. |
| MAT-014 | `reference_*` | reference | none | D | Non-physical construction geometry: datum planes, axes, station markers. Never rendered as material. |
| MAT-015 | `control_curve_*` | reference | none | D | As MAT-014. |
| MAT-016 | `station_*` | reference | none | D | As MAT-014. |

**Why the two stone rows differ in grade.** The tower pier is grade A because a period primary says
"masonry" in a sentence that also gives its dimensions. The anchorage is grade D because no
registered source says anything about what it is built from, even though every photograph shows
stone. A photograph is not in the register, so it cannot grade a control; that asymmetry is the
point of the register, not a defect in it.

---

## 8. Geometry provenance — how the shape is known

Adopted from SRC-018 (`manhattan-bridge-noise-dumbo`, `VISUAL-MODEL-FRAMEWORK.md` sections 5.4 and
5.5), whose central argument this project accepts: **how thoroughly a source was read and what that
source establishes about an element's geometry are two different claims, and collapsing them into
one field hides the more important of the two.** A source can be opened, read and quoted -- fully
verified -- and still support only `ASSUMED` geometry, because a sentence establishing that an
element exists says nothing about where it is. That framework's own reference implementation records
having made exactly this mistake, labelling eight components "verified" on the strength of a source
that located none of them.

This repository already grades sources (`SOURCE-REGISTER.md`) and dimensions (section 2). Geometry
provenance is the third, independent axis, derived per part in `build_control_skeleton.py`:

| State | Meaning | Rendered as | Count |
|---|---|---|---:|
| `MEASURED` | Derived from an instrument reading of the actual structure. | Solid outline, full opacity | **0** |
| `DOCUMENTED` | *This element's* own position or dimension is stated in a source that was read. | Solid outline, full opacity | 37 |
| `INFERRED` | The element's *existence* is documented, but its position or dimension is reasoned. | Dashed outline, reduced opacity | 56 |
| `ASSUMED` | Placed by engineering judgement, with no source statement locating it at all. | Dotted outline, low opacity, **no dimension callouts** | 2 |

**Nothing on this bridge is `MEASURED`,** and SRC-018 reaches the same conclusion independently for
both East River subway bridges. `GRT-074` reports that count on every run so the day it changes, it
changes visibly.

**The `INFERRED`/`ASSUMED` boundary is drawn on whether anything sourced speaks to the element at
all**, not on how confident its shape is. The two `ASSUMED` parts are the approach bent groups: no
registered source mentions a bent on either approach. The approach *decks* are `INFERRED`, because
CTL-002 and CTL-003 document that they exist and how far they run while leaving depth and grade to
judgement. `GRT-076` pins the assumed count at 2, so geometry that nothing documents cannot be added
quietly.

**The rule that follows, adopted verbatim:**

> No dimension may be annotated on any element whose geometry provenance is `ASSUMED`. If we do not
> know where it is, we do not get to say how big it is.

**The filter hides rather than fades.** SRC-018 is explicit about why, and it is worth repeating: "a
faded outline is still a shape a reader will trace, and the honest experience of switching both off
on this project is an empty frame." Switching `INFERRED` and `ASSUMED` off in the viewer leaves the
towers, the anchorages and the station markers. That is the whole of what this model can be said to
document.