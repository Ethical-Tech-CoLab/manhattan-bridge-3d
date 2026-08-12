"""Render the full NYC DOT FOIL request as a PDF for portal upload.

The OpenRecords portal caps the free-text box at 5,000 characters. The full request is longer, so it
travels as an attachment and `sources/foil/dot-request-portal.txt` -- which is deliberately complete
and self-contained on its own -- goes in the box.

What this PDF deliberately does NOT contain: the statutory clock, the appeal letter, the fallback
plan, and the rules for grading records once they arrive. All of that lives in FOIL-REQUEST.md and is
addressed to us, not to the agency. Sending a records officer our appeal strategy would be strange
and faintly adversarial; this document is a request letter and reads as one.

Chromium via Playwright, so no new dependency: reportlab, weasyprint and fpdf are all absent and
Playwright is already here for viewer testing.

    python scripts/build_foil_pdf.py
"""

from __future__ import annotations

import hashlib
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "sources" / "foil" / "NYCDOT-FOIL-Manhattan-Bridge.pdf"
PORTAL_TXT = REPO_ROOT / "sources" / "foil" / "dot-request-portal.txt"

# Both BINs, from the 2024 Bridges and Tunnels Annual Condition Report. Naming both is the single
# most important thing in this request: a search on one may return half the structure.
BINS = [
    ("2240027", "MANHATTAN BRIDGE (LL)", "East River", "14 Nov 2024", "6.3 FAIR"),
    ("2240028", "MANHATTAN BRIDGE (UL)", "NYCTA tracks — BMT", "3 Nov 2022", "5.4 FAIR"),
]

# As published by NYC DOT on its own Manhattan Bridge page. Quoting the agency's own contract
# numbers describes the records in its filing terms, which is what makes a search cheap.
CONTRACTS = [
    ("8", "1992–1997", "Rehabilitation of the South Side Approach and Suspended Spans"),
    ("8C", "1997–2001", "Painting of South Side Towers, Cables A and B, interim steel rehabilitation"),
    ("10", "2001–2004", "Rehabilitation of North Main Span, North Bikeway, Approach Tunnels"),
    ("11", "2005–2008", "Rehabilitation of Lower Roadway, including Manhattan Approach Spans"),
    ("14", "2010–2013", "Cable re-wrapping, necklace lighting and suspender replacement"),
    ("15", "2018–2021", "Saddles and saddle housings, anchorage housings, truss members, "
                        "transit floor beams, tower ornamental features"),
]

ITEMS = [
    (
        "1. Record and as-built drawings of the main bridge",
        "Original construction era, approximately 1901–1912, and any later as-built revisions, "
        "including but not limited to:",
        [
            "Tower elevations, plans and sections, including the plan dimensions of the tower "
            "shafts, the leg spacing, and the dimensions of the arch openings through the towers.",
            "Details of the tower tops at the cable saddles: the saddle castings and their "
            "bearings, and the vertical relationship between the saddle seat and the top of the "
            "cable.",
            "Transverse sections through the deck at midspan, at a tower line, and on each "
            "approach — dimensioned — showing the out-to-out width, the positions of the four "
            "stiffening trusses, the structural depths of the upper roadway, the lower roadway and "
            "the transit floor, and the lateral positions of the four transit track centrelines.",
            "The cable and suspender schedule: the main cable profile with sag, and the schedule "
            "of suspender lengths along the span. If the original is not available, the equivalent "
            "produced for Contract 14 (2010–2013), which replaced all suspenders, would serve "
            "equally well.",
            "The longitudinal profile of the upper and lower roadways, with elevations referenced "
            "to a stated datum, and a statement of which datum that is.",
        ],
    ),
    (
        "2. Record and as-built drawings of the anchorages",
        "Both sides: plan dimensions, elevations and sections, including the vaulted thoroughfare "
        "passing through each anchorage.",
        [],
    ),
    (
        "3. Record and as-built drawings of the approach viaducts",
        "Manhattan and Brooklyn, showing bent or pier spacing, the type and structural depth of "
        "the longitudinal girders or trusses, and the longitudinal grade down to street level.",
        [],
    ),
    (
        "4. Foundation and caisson drawings for both towers",
        "Showing the depth of the cutting edge, the height of the caisson, the founding level and "
        "the top of the masonry pier, each referenced to a stated datum.",
        [],
    ),
    (
        "5. Contract and record drawings from the rehabilitation programme begun in 1982",
        "The Department's own Manhattan Bridge page lists these contracts. I am asking for the "
        "as-built geometry they document rather than temporary works or means and methods.",
        [],
    ),
    (
        "6. The two most recent biennial inspection reports for each BIN",
        "Including attached sketches, load ratings and element-level condition data. The most "
        "recent inspections recorded in the 2024 Annual Condition Report are 14 November 2024 for "
        "BIN 2240027 and 3 November 2022 for BIN 2240028.",
        [],
    ),
    (
        "7. Any survey control on the structure",
        "Geodetic coordinates, monument descriptions or control diagrams for the tower centres or "
        "anchorage corners, in any stated coordinate system. A single surveyed tower position "
        "would be sufficient.",
        [],
    ),
    (
        "8. Any existing three-dimensional survey of the structure",
        "Laser scan, LiDAR or point cloud data, or a photogrammetric survey, produced for any of "
        "the contracts above or for inspection purposes. I would take this in whatever form it "
        "exists, including a raw point cloud.",
        [],
    ),
    (
        "9. Any index, drawing register, aperture-card list or file inventory",
        "Covering the above, together with the portion of the Department's subject matter list "
        "maintained under Public Officers Law §87(3)(c) that covers bridge engineering records. "
        "If producing the drawings themselves is burdensome, I would value the index first — it "
        "would let me identify a much smaller set of specific sheets and resubmit a narrower "
        "request.",
        [],
    ),
]

CSS = """
@page { size: Letter; margin: 22mm 20mm 20mm 20mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 Georgia, "Times New Roman", serif; color: #111; margin: 0; }
h1 { font-size: 15pt; margin: 0 0 2mm; line-height: 1.25; }
.sub { font-size: 9.5pt; color: #444; margin: 0 0 6mm; }
h2 { font-size: 11pt; margin: 6mm 0 2mm; border-bottom: 1px solid #bbb; padding-bottom: 1mm; }
p { margin: 0 0 3mm; }
.item { margin: 0 0 4mm; page-break-inside: avoid; }
.item h3 { font-size: 10.5pt; margin: 0 0 1mm; }
.item p { margin: 0 0 1.5mm; }
ol.sub-items { margin: 1mm 0 0 5mm; padding: 0 0 0 4mm; }
ol.sub-items li { margin: 0 0 1.5mm; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4mm; font-size: 9.5pt; }
th, td { border: 1px solid #999; padding: 1.4mm 2mm; text-align: left; vertical-align: top; }
th { background: #eee; font-weight: bold; }
.note { background: #f4f4f4; border-left: 3px solid #777; padding: 2.5mm 3mm; margin: 0 0 4mm; }
.sig { margin-top: 8mm; padding-top: 3mm; border-top: 1px solid #bbb; }
.fill { color: #777; }
small { font-size: 8.5pt; color: #555; }
"""


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_html() -> str:
    bins = "".join(
        "<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(map(esc, r))
        for r in BINS
    )
    contracts = "".join(
        "<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % tuple(map(esc, r)) for r in CONTRACTS
    )

    items = []
    for heading, lede, subs in ITEMS:
        sub_html = ""
        if subs:
            sub_html = "<ol class='sub-items' type='a'>%s</ol>" % "".join(
                "<li>%s</li>" % esc(s) for s in subs
            )
        extra = contracts_table() if heading.startswith("5.") else ""
        items.append(
            "<div class='item'><h3>%s</h3><p>%s</p>%s%s</div>"
            % (esc(heading), esc(lede), sub_html, extra)
        )

    return """<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>
<h1>Freedom of Information Law request — Manhattan Bridge structural records</h1>
<p class="sub">To the Records Access Officer, New York City Department of Transportation ·
55 Water Street, 4th floor, New York, NY 10041 · foiladmin@dot.nyc.gov</p>

<p>Under Article 6 of the New York State Public Officers Law, I request access to the records
described below concerning the <b>Manhattan Bridge</b>, which opened in 1909 and spans the East
River between Canal Street, Manhattan and the Flatbush Avenue Extension, Brooklyn.</p>

<h2>The structure is registered under two BINs</h2>
<p>The Department registers this bridge as two structures, inspected on different dates and rated
separately. <b>Please treat every item below as applying to both.</b> A search limited to one BIN
would return only part of the structure, and several of the records I am seeking — particularly the
deck framing depths — concern the upper level.</p>
<table><tr><th>BIN</th><th>As named in the Condition Report</th><th>Carries / crosses</th>
<th>Last inspection</th><th>Rating</th></tr>%s</table>
<p><small>Source: NYC DOT Bridges and Tunnels Annual Condition Report, 2024 edition.</small></p>

<h2>Form of production</h2>
<p>I request <b>electronic copies</b> where they exist, delivered by download link or electronic
transfer. I do not require certified copies. Where a record exists only on paper, microfilm or
aperture card, please tell me its extent and the estimated copying cost before producing it, so that
I can narrow the request rather than incur an avoidable fee.</p>
<div class="note"><b>One request about scans.</b> Where drawings are scanned, please provide the
<b>full sheet including the title block and the graphic scale bar</b>, rather than a cropped detail.
A cropped scan cannot be scaled reliably and is of limited use for my purpose.</div>

<h2>Records requested</h2>
%s

<h2>Context, offered to help locate the records</h2>
<p>This is not part of the request. I am building an openly published, source-documented
three-dimensional model of the bridge in which every dimension is traceable to a cited source, and
anything unsourced is labelled a placeholder and drawn as one. The records above would replace
fourteen placeholder dimensions with documented ones. The project is public at
<b>github.com/Ethical-Tech-CoLab/manhattan-bridge-3d</b> and any records provided will be credited
to NYC DOT.</p>

<h2>Already reviewed, and not requested</h2>
<p>So as not to ask for what is already published, I have already obtained and reviewed: the
Department's published Manhattan Bridge facts page; the Bridges and Tunnels Annual Condition Report;
NYC Open Data holdings; the Historic American Engineering Record survey at the Library of Congress
(HAER NY-164, item ny0980, which contains photographs and <b>no measured drawings</b>); and the 2010
National Bridge Inventory data sheet for structure 36-2240027. None contains the dimensions sought.</p>

<h2>If any part is denied</h2>
<p>If any part of this request is denied, please cite the specific statutory exemption for each
withheld record and release the remainder, including any reasonably segregable portions.</p>
<p>If security review is required before the release of structural drawings, I am content to receive
a <b>redacted set</b>, or to narrow the request to the <b>1901–1912 construction-era drawings
alone</b>, which are more than a century old and describe a structure whose form is visible from the
public walkway.</p>
<p>Please acknowledge receipt and provide a date certain for a response.</p>

<div class="sig">
<p><span class="fill">[Name]</span><br>
<span class="fill">[Postal address]</span><br>
<span class="fill">[Email]</span> · <span class="fill">[Phone]</span><br>
<span class="fill">[Date]</span></p>
</div>
</body></html>""" % (CSS, bins, "".join(items))


def contracts_table() -> str:
    rows = "".join(
        "<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % tuple(map(esc, r)) for r in CONTRACTS
    )
    return ("<table><tr><th>Contract</th><th>Period</th><th>Scope, as the Department describes it"
            "</th></tr>%s</table>" % rows)


def check_portal_text() -> list[str]:
    """Verify the 5,000-character portal version is still a faithful, complete request.

    The condensed text and this PDF are edited by hand and will drift if nothing watches them. What
    matters is not that they match word for word -- the whole point is that one is shorter -- but
    that the short one is still a *legally complete request on its own*, because it is the version
    the agency actually receives in the box. If the attachment is mislaid, the pasted text is the
    request.

    So this checks for the parts that carry legal effect, not for prose.
    """
    if not PORTAL_TXT.exists():
        return ["%s is missing" % PORTAL_TXT.name]

    body = PORTAL_TXT.read_text(encoding="utf-8").strip()
    problems: list[str] = []

    crlf = len(body.replace("\n", "\r\n"))
    if crlf > 5000:
        problems.append("portal text is %d characters at CRLF, over the 5,000 limit" % crlf)

    # Every numbered item must survive: each one defines a slice of the scope, and a dropped item
    # is a record the agency is never asked for.
    for n in range(1, len(ITEMS) + 1):
        if "\n%d. " % n not in body:
            problems.append("portal text is missing item %d" % n)

    required = {
        "BIN 2240027": "the lower-level BIN",
        "BIN 2240028": "the upper-level BIN",
        "BOTH BINs": "the instruction that every item covers both structures",
        "Article 6": "the statutory invocation",
        "segregable": "the demand for segregable portions",
        "statutory exemption": "the demand for a specific exemption per withheld record",
        "redacted set": "the offer to accept redactions, which pre-empts a security denial",
        "date certain": "the request for a date certain, which starts the appeal clock",
        "electronic copies": "the request for electronic rather than paper copies",
    }
    for needle, why in required.items():
        if needle not in body:
            problems.append("portal text is missing %r -- %s" % (needle, why))

    return problems


def make_reproducible(path: pathlib.Path, content_digest: str) -> None:
    """Strip the timestamps Chromium stamps into the PDF, so identical input gives identical bytes.

    Without this, every rebuild produces a different file even when nothing changed, because a PDF
    records its own creation time and a random document ID. The artifact is committed, so that means
    permanent churn and -- worse in a repository built on byte-level provenance -- a diff that cannot
    distinguish "the request changed" from "someone ran the script".

    The document ID is derived from the **source HTML**, not from Chromium's output. Deriving it from
    the output was the first attempt and could not work: the output already carries the varying
    timestamp, so the ID varied with it.
    """
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import ArrayObject, ByteStringObject, NameObject

    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # A fixed date rather than "now". It is not a claim about when the request was written; the
    # request carries its own [Date] field for that.
    fixed = "D:20000101000000Z"
    writer.add_metadata({
        "/Title": "FOIL request - Manhattan Bridge structural records (BIN 2240027 / 2240028)",
        "/Subject": "Request under Article 6 of the New York State Public Officers Law",
        "/Creator": "manhattan-bridge-3d/scripts/build_foil_pdf.py",
        "/Producer": "Chromium via Playwright",
        "/CreationDate": fixed,
        "/ModDate": fixed,
    })

    # Chromium also embeds an XMP packet carrying its own CreateDate. Left in place it would defeat
    # everything above, because it is a second, independent copy of the timestamp.
    for page in writer.pages:
        page.get_object().pop(NameObject("/Metadata"), None)
    root = writer._root_object  # noqa: SLF001
    root.pop(NameObject("/Metadata"), None)

    ident = ByteStringObject(content_digest[:16].encode("ascii"))
    writer._ID = ArrayObject([ident, ident])  # noqa: SLF001 - pypdf exposes no public setter

    with path.open("wb") as fh:
        writer.write(fh)


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is required: pip install playwright && playwright install chromium")
        return 1

    html = build_html()
    tmp = OUT.parent / "_foil.html"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(html, encoding="utf-8")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(tmp.resolve().as_uri(), wait_until="load")
        page.pdf(
            path=str(OUT),
            format="Letter",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(
                "<div style='font:8pt Georgia,serif;color:#666;width:100%;padding:0 20mm;"
                "display:flex;justify-content:space-between;'>"
                "<span>FOIL request &mdash; Manhattan Bridge (BIN 2240027 / 2240028)</span>"
                "<span class='pageNumber'></span> / <span class='totalPages'></span></div>"
            ),
            margin={"top": "16mm", "bottom": "16mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()

    tmp.unlink()
    make_reproducible(OUT, hashlib.sha256(html.encode("utf-8")).hexdigest())
    print("wrote %s (%d bytes)" % (OUT.relative_to(REPO_ROOT), OUT.stat().st_size))

    problems = check_portal_text()
    if problems:
        print()
        print("  ! THE PORTAL TEXT IS NOT A COMPLETE REQUEST")
        for p in problems:
            print("    %s" % p)
        print()
        print("  The pasted text is what the agency receives if the attachment is mislaid.")
        return 1

    body = PORTAL_TXT.read_text(encoding="utf-8").strip()
    crlf = len(body.replace("\n", "\r\n"))
    print("portal text: %d chars (LF) / %d chars (CRLF worst case), limit 5000, %d spare"
          % (len(body), crlf, 5000 - crlf))
    print("             all %d items present, both BINs, statutory clauses intact"
          % len(ITEMS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
