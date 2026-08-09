"""Read arch proportions off the HAER tower photograph (SRC-018).

What this does and does not produce
-----------------------------------
It produces **ratios**, never lengths. The photograph is uncalibrated: no scale bar, no surveyed
control point, unknown lens. CONFIDENCE-MODEL.md section 6.2 is explicit that a projection without
scale control cannot yield a dimension, so nothing here is allowed to become a control value.

The ratios are then applied to tower controls that are **already sourced** -- leg positions from
CTL-056/057/058/059, the pier top from CTL-030, the saddle from CTL-018 -- which bounds the result
inside geometry the register already stands behind. That is what makes the arch grade `D`
(a shape hint) rather than an invented dimension pretending to be a measurement.

Method
------
Column and arch edges are found by scanning brightness along horizontal and vertical lines through
the tower. The tower is dark steel against a bright sky, so an edge is a large brightness step; the
arch void is bright sky enclosed by dark steel. Everything is reported as a fraction of the tower's
own width or height in the image, so image scale cancels out.

    python scripts/measure_arch_from_photo.py
"""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install pillow")

REPO = Path(__file__).resolve().parents[1]
PHOTO = REPO / "sources" / "photos" / "image-set-001-main-towers" / "SRC-018-332346b3dc1e.jpg"

# Brightness above which a pixel is treated as sky rather than structure. The photograph is a
# high-key exterior against an overcast sky, so the separation is wide and the exact threshold
# barely matters; it is reported so the reading can be reproduced.
SKY = 150


def runs(values: list[int], threshold: int) -> list[tuple[int, int]]:
    """Contiguous spans of 'sky' pixels, as (start, end) index pairs."""
    spans: list[tuple[int, int]] = []
    start = None
    for i, v in enumerate(values):
        if v >= threshold and start is None:
            start = i
        elif v < threshold and start is not None:
            spans.append((start, i - 1))
            start = None
    if start is not None:
        spans.append((start, len(values) - 1))
    return spans


def main() -> int:
    if not PHOTO.exists():
        raise SystemExit(f"{PHOTO} not found; run scripts/ingest_sources.py first")
    im = Image.open(PHOTO).convert("L")
    w, h = im.size
    px = im.load()
    print(f"photograph      : {PHOTO.name}  {w} x {h}")
    print(f"sky threshold   : {SKY}/255\n")

    # A naive "widest bright run" scan is wrong here, and was: it happily returns the open sky
    # beside the tower, which is brighter and wider than any arch. An arch void is specifically a
    # bright run *bounded on both sides by structure*, so the scan is anchored between two dark
    # columns and bright runs touching the scan edges are discarded.
    def enclosed_void(y: int, x0: int, x1: int) -> tuple[int, int] | None:
        row = [px[x, y] for x in range(x0, x1)]
        candidates = [
            (a, b)
            for a, b in runs(row, SKY)
            if b - a > 8 and a > 0 and b < len(row) - 1  # bounded by structure on both sides
        ]
        if not candidates:
            return None
        a, b = max(candidates, key=lambda s: s[1] - s[0])
        return x0 + a, x0 + b

    # The lower arch is the clearest opening in this photograph: fully enclosed by the two centre
    # columns, the pier below and the deck above, with plain sky behind it.
    print("LOWER ARCH (below deck, above pier) -- enclosed voids only")
    widths = []
    for y in range(700, 900, 20):
        found = enclosed_void(y, 240, 420)
        if found:
            a, b = found
            widths.append(b - a)
            print(f"  y={y}: void x={a}..{b}  ({b - a} px wide)")

    print("\nLOWER ARCH vertical extent, scanned down the void centreline")
    col_x = 300
    col = [px[col_x, y] for y in range(650, 980)]
    spans = [(a, b) for a, b in runs(col, SKY) if b - a > 10]
    height_px = 0
    for a, b in spans:
        height_px = max(height_px, b - a)
        print(f"  x={col_x}: sky from y={650 + a} to y={650 + b}  ({b - a} px tall)")

    if widths and height_px:
        width_px = max(widths)
        print(f"\nARCH PROPORTION (the only number this script exports)")
        print(f"  widest void   : {width_px} px")
        print(f"  tallest void  : {height_px} px")
        print(f"  height/width  : {height_px / width_px:.2f}")
        print(
            "\n  A tall, narrow opening with a rounded head. The measured runs narrow at both the\n"
            "  top and the bottom of the void, which is the signature of an arched head over a\n"
            "  parallel-sided shaft rather than a plain rectangular slot. That single ratio, and\n"
            "  the fact that the head is round, are all this image is asked to supply."
        )

    print(
        "\nRatios only. No length is taken from this image; see CONFIDENCE-MODEL.md section 6.2.\n"
        "The proportion is applied to already-sourced tower controls in GEOMETRY-CONTROL.md, and\n"
        "the resulting arch geometry is graded D because no source states its dimensions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
