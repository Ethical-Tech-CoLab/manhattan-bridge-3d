"""Adapt the Manhattan Bridge build brief for a sibling bridge repository.

`AGENT-INSTRUCTIONS.md` is deliberately bridge-specific: it names its bridge, lists that bridge's
sources, and — most dangerously — carries a table of Manhattan Bridge control dimensions under the
heading "Use these as initial control values". Copying it verbatim into the Brooklyn or Williamsburg
repository would seed those projects with another bridge's numbers, which SOURCE-REGISTER.md
identifies as the single most likely way this programme produces a confident wrong number.

So the copy is adapted rather than literal:

  * the bridge is renamed throughout, in prose and in the source hierarchy
  * the control-dimension table is replaced by an empty skeleton and a negative-control warning
  * a provenance banner records where the file came from and what was changed

What is deliberately NOT renamed: the end-names `manhattan_anchorage`, `manhattan_tower`,
`manhattan_approach` and friends. All three bridges span the same river between the same two
boroughs, so those names are geographically correct for every one of them.

    python scripts/adapt_brief_for_bridge.py --bridge Brooklyn --out c:/Dev/brooklyn-bridge-3d
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE_BRIEF = REPO / "AGENT-INSTRUCTIONS.md"

# The Manhattan control-dimension table, replaced wholesale. Matching on the heading and the
# sentence that follows the table keeps this robust to edits inside the table itself.
TABLE_START = "## 2. Known Control Dimensions From Prior Research"
TABLE_END = "Important implication:"

REPLACEMENT_SECTION = """## 2. Control dimensions — none yet, deliberately

**This table is empty on purpose, and it must stay empty until you have read a source.**

The Manhattan Bridge brief this file was adapted from carried a filled-in table here under the
heading "use these as initial control values". Those are *Manhattan Bridge* figures. They are not
approximations of {bridge} Bridge figures, they are a different structure's measurements, and
seeding them here would be the exact failure this programme is built to prevent.

> **Negative control.** The Manhattan Bridge's dimensions are registered in
> `manhattan-bridge-3d/SOURCE-REGISTER.md` and **must never enter this model**. Three similar East
> River suspension bridges are the most likely route to a confident wrong number. Register the other
> two bridges' figures explicitly as sources that may not be used, so cross-contamination becomes a
> test failure rather than a silent error.

Fill this in one row at a time, each from a source you have actually opened:

| Control ID | Key | Value | Unit | Source IDs | Confidence | Notes |
|---|---|---:|---|---|---|---|
| CTL-001 | | | | | | |

Rules the parser enforces, not the reviewer:

- Only grade `D` may cite no source. Anything `A`/`B`/`C` without a source is a parse error.
- Grade `D` may not cite sources. A placeholder must not appear to rest on evidence.
- Values are bare decimals. No thousands separators, no ranges, no "approx".

A complete HO model of a bridge this size is very large. Treat the full bridge as a digital twin
first, and extract modular study pieces later.

"""

BANNER = """<!--
  Adapted from manhattan-bridge-3d/AGENT-INSTRUCTIONS.md.

  Changed on copy:
    * renamed throughout for the {bridge} Bridge
    * section 2's Manhattan control-dimension table removed and replaced with an empty skeleton
      plus a negative-control warning -- those numbers describe a different bridge
    * repository name updated

  Unchanged, and correct as-is: the end-names manhattan_anchorage / manhattan_tower /
  manhattan_approach. All three East River bridges run between the same two boroughs.

  The transferable method lives alongside this file in HOW-TO-DESIGN.md.
-->

"""


def adapt(text: str, bridge: str, slug: str) -> str:
    # Rename FIRST, splice SECOND. Doing it the other way round rewrites the literal
    # "Manhattan Bridge" inside the replacement warning into the target bridge's own name, which
    # turns it into nonsense: "those are Williamsburg Bridge figures ... not approximations of
    # Williamsburg Bridge figures". The markers below survive the rename because neither contains
    # the phrase being replaced.
    text = text.replace("Manhattan Bridge", f"{bridge} Bridge")
    text = text.replace("manhattan-bridge-digital-twin/", f"{slug}/")

    start = text.index(TABLE_START)
    end = text.index(TABLE_END, start)
    text = text[:start] + REPLACEMENT_SECTION.format(bridge=bridge) + text[end:]

    # Drop the now-orphaned sentence fragment left by the splice.
    text = text.replace(
        "Important implication: a complete HO bridge model is extremely large. Treat the full "
        "bridge as a digital twin first. Use modular extraction later for physical study pieces.\n",
        "",
    )
    return BANNER.format(bridge=bridge) + text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", required=True, help="Bridge name, e.g. Brooklyn")
    parser.add_argument("--slug", required=True, help="Repository folder name")
    parser.add_argument("--out", required=True, type=Path, help="Target repository root")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    adapted = adapt(SOURCE_BRIEF.read_text(encoding="utf-8"), args.bridge, args.slug)
    target = args.out / "AGENT-INSTRUCTIONS.md"
    target.write_text(adapted, encoding="utf-8")

    remaining = adapted.count("Manhattan Bridge")
    # Every surviving mention must come from the negative-control warning, which names the bridge
    # whose figures may not be used. Deriving the expected count from the warning text itself keeps
    # this honest if the wording changes; a hardcoded number would just drift.
    expected = REPLACEMENT_SECTION.format(bridge=args.bridge).count("Manhattan Bridge")
    print(f"wrote {target}  ({len(adapted):,} bytes)")
    print(f"  'Manhattan Bridge' mentions: {remaining} (all should be the negative-control warning)")
    if remaining != expected:
        print(f"  WARNING: expected {expected}; a mention leaked outside the warning, or the "
              "warning was renamed away")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
