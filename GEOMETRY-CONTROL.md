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
| CTL-005 | main_span | 1470 | ft | SRC-000, SRC-002, SRC-011, SRC-013, SRC-015, SRC-016 | A | Tower centerline to tower centerline. Confirmed by two period primaries. See CONF-006. |
| CTL-006 | side_span_each | 725 | ft | SRC-000, SRC-002, SRC-011, SRC-015 | A | Each suspended side span. Confirmed by a period primary. |
| CTL-007 | tower_height_above_mhw | 322 | ft | SRC-000, SRC-001 | A | Retained as the handoff value. NOT used for geometry; see CTL-018 and CONF-005. |
| CTL-008 | center_clearance_above_mhw | 135 | ft | SRC-000, SRC-001, SRC-013, SRC-015, SRC-016 | A | Design clearance at midspan, underside of the suspended structure. Confirmed by two period primaries. SRC-014 surveys 134 ft, see CONF-007. |
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
| CTL-020 | tower_finial_height | 350 | ft | SRC-012 | B | Ornamental finials above high water. Recorded, not used for geometry. |
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
| OQ-009 | Real-world azimuth and geodetic anchor of the bridge axis. | Georeferencing | SRC-001, SRC-003 | Open. SRC-002 gives a landmark coordinate of roughly 40 deg 42' 27" N, 73 deg 59' 27" W, not yet adopted as a control. |
| OQ-010 | Exact transverse centerlines of the four subway tracks. | Track placement | SRC-004 | **Mitigated**: tracks are confirmed to lie in the A-B and C-D truss bays, bounding them between 20 ft and 48 ft from centerline. Note CONF-011: the 1908 design put two of them on the upper deck. |
| OQ-011 | Conflict CONF-001, main cable diameter. | Cable solid geometry | SRC-004 | **Largely explained**: SRC-015's 21.25 in is on the wires excluding wrapping, which reconciles three of the four figures. |
| OQ-012 | Conflict CONF-002, stiffening truss depth. | Truss depth | — | **Effectively resolved** toward 24 ft. The SRC-015 sentence is OCR-damaged at exactly that number. |
| OQ-013 | Vertical framing depths of the upper deck, lower deck and track structure. | Deck envelope thicknesses | SRC-004 | Open. These are the last significant placeholders. |
| OQ-014 | The transverse layout closes to 116 ft against a sourced 120 ft deck, leaving about 2 ft per side unaccounted. | Deck edge detail | SRC-004 | **Explained, not closed.** SRC-015 states the footways are carried "on cantilever extensions of the floor beams" outside the outer trusses, so the residual is the cantilever tip, fascia and railing beyond the 10 ft walking surface. No source gives that dimension. Tracked by GRT-009. |
| OQ-015 | Top of the masonry pier above MHW. | Tower pier height | SRC-016 | **Retired.** SRC-016 states 23 ft explicitly; see CONF-009. |
| OQ-016 | The two period primaries give vertical build-ups that differ by 8 ft. SRC-016: cutting edge -92 ft, caisson 47.5 ft high, footing seat -33 ft, capstone +23 ft (115 ft overall). SRC-015: caisson 56 ft, masonry 67 ft, 123 ft overall, which against -92 ft implies a capstone at +31 ft. | Tower foundation internals | SRC-004 | New at Milestone 3. The model follows SRC-016 throughout because its figures are explicit elevations rather than summary heights, and they are internally consistent. The SRC-015 heights are recorded as CTL-047, CTL-048 and CTL-053 but are not used. |
| OQ-017 | Warren truss diagonal direction at each panel, chord and diagonal member sections, and the tower bracing arrangement. | Truss and tower web detail | SRC-004, SRC-005 | New at Milestone 4. The truss depth, spacing and panel count are all sourced, so the panel *positions* are correct; the alternating diagonal pattern is the Warren form named by three sources but its handedness at each panel is not documented. Detail photographs (SRC-005) could settle it to grade B. |
