"""Ingest external sources into /sources with licence and provenance capture.

STATUS: not implemented. Planned for Milestone 3.

Milestone 1 deliberately imports nothing. Implementing this script requires the verification queue in
SOURCE-REGISTER.md to be worked first, because every ingested file must land with:

  * a registered ``SRC-###`` ID,
  * a retrieval URL and retrieval date,
  * a licence record written to ``/sources/licenses/<source_id>.md``,
  * a checksum so that later runs can detect a changed upstream file.

Refusing to run is intentional: a silent no-op would let downstream scripts assume sources exist.
"""

from __future__ import annotations

import sys

MILESTONE = 3
REASON = (
    "Source ingestion is Milestone 3 work. Verify SRC-001..SRC-004 in SOURCE-REGISTER.md first; "
    "no source files may enter /sources without a licence record."
)


def main() -> int:
    print(f"ingest_sources.py is not implemented (planned for Milestone {MILESTONE}).")
    print(REASON)
    return 2


if __name__ == "__main__":
    sys.exit(main())
