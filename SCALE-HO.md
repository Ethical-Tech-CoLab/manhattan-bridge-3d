# HO Scale Reference — 1:87.1

The model is authored at prototype scale in **meters**. HO is a *derived reporting scale*, never an authoring scale.

```text
ho_value = prototype_value / 87.1
```

All HO figures in this repository are computed from [GEOMETRY-CONTROL.md](/c:/Dev/manhattan-bridge-3d/GEOMETRY-CONTROL.md)
by `scripts/build_control_skeleton.py` and written to `viewer/metadata/scale_ho.json`. The table below is the
independently transcribed reference from `AGENT-INSTRUCTIONS.md` section 2; the build compares its own computed
values against it and reports any deviation.

---

## 1. Reference conversions

| Feature | Control ID | Prototype | HO 1:87.1 |
|---|---|---:|---:|
| Total bridge and approaches | CTL-001 | 6855 ft | 944.43 in / 78.70 ft / 23988.6 mm |
| Lower-level abutment to abutment | CTL-002 | 5790 ft | 797.70 in / 66.48 ft / 20261.7 mm |
| Upper roadway portal to portal | CTL-003 | 6090 ft | 839.04 in / 69.92 ft / 21311.5 mm |
| Anchorage to anchorage suspended length | CTL-004 | 2920 ft | 402.30 in / 33.53 ft / 10218.3 mm |
| Main span | CTL-005 | 1470 ft | 202.53 in / 16.88 ft / 5144.2 mm |
| Each side span | CTL-006 | 725 ft | 99.89 in / 8.32 ft / 2537.1 mm |
| Tower height above MHW | CTL-007 | 322 ft | 44.36 in / 1126.8 mm |
| Center clearance above MHW | CTL-008 | 135 ft | 18.60 in / 472.4 mm |
| Roadway width | CTL-009 | 46 ft | 6.34 in / 161.0 mm |
| Stiffening truss depth, ASCE | CTL-010 | 24 ft | 3.31 in / 84.0 mm |
| Stiffening truss depth, alternate | CTL-011 | 26 ft | 3.58 in / 91.0 mm |
| Cable length | CTL-012 | 3224 ft | 444.18 in / 37.02 ft / 11282.1 mm |
| Main cable diameter, ASCE | CTL-013 | 20.75 in | 0.238 in / 6.05 mm |
| Main cable diameter, HAER | CTL-014 | 21.25 in | 0.244 in / 6.20 mm |

Placeholder parameters (CTL-101 and above) are deliberately **not** listed here. They are not dimensions and must not
be used to cut material.

---

## 2. Consequences of the scale

At 1:87.1 the complete structure is about **24 m / 78.7 ft** long. That is not a layout object; it is a study
reference. Practical implications:

1. Treat the full bridge as a digital twin. Do not attempt a single physical print.
2. A single main-span cable at HO is 6.05 mm to 6.20 mm in diameter — printable, but at 5.14 m span it must be a
   tensioned physical member, not printed geometry.
3. Stiffening truss depth at HO is 84 mm to 91 mm. Truss members will be far below reliable FDM resolution and are a
   resin or photo-etch problem.
4. Modular extraction is the only realistic physical route: cut the model at defined stations and export study
   modules. Candidate module joints are the tower centerlines (`STA-TWR-M`, `STA-TWR-B`) and the anchorage cable
   points (`STA-ANC-M`, `STA-ANC-B`).

---

## 3. Export policy

| Artifact | Units | Scale | Path |
|---|---|---|---|
| Authoritative skeleton | meters | 1:1 prototype | `mesh/glb/control_skeleton.glb` |
| HO study export | meters (numerically 1:87.1 of prototype) | 1:87.1 | `mesh/glb/control_skeleton_ho.glb` |
| Scale report | mm and in | 1:87.1 | `viewer/metadata/scale_ho.json` |

The HO GLB is a uniformly scaled copy of the authoritative skeleton. It carries the same `part_id` values so that
metadata joins across both files. Part metadata always reports `prototype_units: meters` and
`ho_scale_units: millimeters` regardless of which file it came from.

The viewer's **HO dimension toggle** switches the measurement readout between prototype units (ft / m) and HO units
(mm / in). It does not rescale the scene.

---

## 4. Rounding

Report HO millimeter values to 1 decimal place, or 2 decimals below 10 mm. Report HO inch values to 2 decimal
places, or 3 decimals below 1 in. Never round in the authoring data — rounding happens at report time only.
