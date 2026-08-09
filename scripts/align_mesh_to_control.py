"""Align an imported mesh to the control skeleton and report its deviation.

STATUS: not implemented. Planned for Milestone 4.

Planned alignment controls (AGENT-INSTRUCTIONS.md section 9), all of which already exist in
``viewer/metadata/build_report.json``:

  * tower centerlines      -> ``STA-TWR-M`` / ``STA-TWR-B``
  * anchorage cable points -> ``STA-ANC-M`` / ``STA-ANC-B``
  * deck elevation         -> ``ELV-UPPER-DECK`` / ``ELV-LOWER-DECK``
  * main span endpoints    -> ``tower_spacing_m``

Output: ``mesh_alignment_report.md`` recording scale factor, rigid transform, per-control residuals,
and an explicit statement that the control skeleton was not modified to fit the mesh.
"""

from __future__ import annotations

import sys

MILESTONE = 4
REASON = (
    "Mesh alignment is Milestone 4 work. It depends on import_reference_meshes.py and on a reviewed "
    "control skeleton to align against."
)


def main() -> int:
    print(f"align_mesh_to_control.py is not implemented (planned for Milestone {MILESTONE}).")
    print(REASON)
    return 2


if __name__ == "__main__":
    sys.exit(main())
