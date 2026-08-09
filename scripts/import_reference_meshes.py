"""Import Tier C reference meshes into /mesh/raw without touching the authoritative model.

STATUS: not implemented. Planned for Milestone 4.

Rules this script must enforce when it is written (AGENT-INSTRUCTIONS.md sections 3 and 9):

  1. Raw files are preserved byte-for-byte in ``/mesh/raw`` alongside their licence record.
  2. Imported meshes are never merged into ``control_skeleton.glb``. They live in their own scene
     graph and are loaded as overlays.
  3. Every imported mesh is tagged ``source_basis: ["mesh_reference"]`` and confidence ``C`` at best,
     and only after ``align_mesh_to_control.py`` has produced an alignment report.
  4. Nothing imported here may change a value in GEOMETRY-CONTROL.md.
"""

from __future__ import annotations

import sys

MILESTONE = 4
REASON = (
    "Reference mesh import is Milestone 4 work. The control skeleton must be dimensionally frozen "
    "and reviewed first, otherwise an imported mesh will end up defining the geometry it is "
    "supposed to be checked against."
)


def main() -> int:
    print(f"import_reference_meshes.py is not implemented (planned for Milestone {MILESTONE}).")
    print(REASON)
    return 2


if __name__ == "__main__":
    sys.exit(main())
