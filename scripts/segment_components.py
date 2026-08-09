"""Split aligned geometry into named, metadata-carrying components.

STATUS: not implemented. Planned for Milestone 4.

The taxonomy this script must target already exists: see ``taxonomy`` in
``viewer/metadata/parts.json`` and AGENT-INSTRUCTIONS.md section 6. Every emitted component must
satisfy the same metadata contract the control skeleton already satisfies (CONFIDENCE-MODEL.md
section 2), which ``scripts/validate_dimensions.py`` already enforces.
"""

from __future__ import annotations

import sys

MILESTONE = 4
REASON = (
    "Component segmentation is Milestone 4 work. Run it only on geometry that has an alignment "
    "report, so that each component inherits a traceable source basis."
)


def main() -> int:
    print(f"segment_components.py is not implemented (planned for Milestone {MILESTONE}).")
    print(REASON)
    return 2


if __name__ == "__main__":
    sys.exit(main())
