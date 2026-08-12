# NYC DOT FOIL request — Manhattan Bridge record drawings

Everything needed to file, plus what to do with the response. The request text is in §4 and is meant
to be pasted with only the bracketed identity fields changed.

Verified against [NYC DOT's FOIL page](https://www.nyc.gov/html/dot/html/about/foil.shtml) and
[NYC DOT's Manhattan Bridge page](https://www.nyc.gov/html/dot/html/infrastructure/manhattan-bridge.shtml),
both checked 11 August 2026.

Modelled on [the Brooklyn Bridge request](https://github.com/Ethical-Tech-CoLab/brooklyn-bridge-3d/blob/main/FOIL-REQUEST.md).
Four things differ, and they are the reason this is not a copy:

1. **This bridge has two BINs**, not one. A request naming only one may be answered for only half
   the structure. See §2.
2. **The subway tracks are not DOT's.** Four NYCTA tracks run on the lower level, and two of our
   open questions are about them. That is an MTA request, filed in parallel. See §7.
3. **The rehabilitation is a numbered contract series, 1982 to date, and DOT publishes the list.**
   Naming the contracts is how you describe records *in the agency's own filing terms*. See §4 item 5.
4. **Ask for the suspender schedule from Contract 14 by name.** It is one document and it retires
   the cable geometry. See §4 item 1(d).

---

## 1. Where it goes

| | |
|---|---|
| **Preferred** | [NYC OpenRecords Portal](https://a860-openrecords.nyc.gov/) — the agency states it "strongly recommends" electronic submission. Requires a free NYC account. Select **Department of Transportation**. |
| **By mail** | New York City Department of Transportation, Records Access Officer, 55 Water Street, 4th floor, New York, NY 10041 |
| **Records Access Officer** | Judith Falk — foiladmin@dot.nyc.gov |
| **Appeals Officers** | Edalia George and Michael Twomey — foilappeal@dot.nyc.gov |
| **Copying fee** | 25¢ per page for paper. Electronic copies should be free — ask for electronic. |

> **Check the agency dropdown before you submit.** This has already gone wrong once: request
> `FOIL-2026-030-00205` was filed against the **Department of City Planning**, which holds zoning and
> land-use records and no bridge engineering records at all. On the portal the middle segment of the
> reference number is the agency — **DOT is `841`**, so a correctly routed request reads
> `FOIL-2026-841-#####`. See [`sources/foil/SUBMISSIONS.md`](sources/foil/SUBMISSIONS.md) for the
> full record and the remedy.

**Filed.** This request is live with NYC DOT as **`FOIL-2026-841-04819`**, submitted 11 August 2026,
acknowledgment due **18 August 2026**. Status and what to do when it lands:
[`sources/foil/SUBMISSIONS.md`](sources/foil/SUBMISSIONS.md). The MTA request in §7 is still to file.

**Every request filed, and what came back, is logged in
[`sources/foil/SUBMISSIONS.md`](sources/foil/SUBMISSIONS.md).** Keep it current: a source whose
provenance begins "someone emailed it to me" is weaker than one traceable to a dated, numbered
request to a named agency.

**Use the portal.** It timestamps the request, which is what starts the statutory clock and what you
will rely on if you need to appeal.

### The 5,000-character box, and what to paste in it

The OpenRecords free-text field caps at **5,000 characters**. The full request in §4 is about 6,900,
so it does not fit. Two files are committed for this, and you need both:

| File | What it is | Where it goes |
|---|---|---|
| [`sources/foil/dot-request-portal.txt`](sources/foil/dot-request-portal.txt) | The request condensed to **4,890 characters**, worst case | Paste into the portal box |
| [`sources/foil/NYCDOT-FOIL-Manhattan-Bridge.pdf`](sources/foil/NYCDOT-FOIL-Manhattan-Bridge.pdf) | The full request, four pages, formatted as a letter | Attach as an upload |

**The pasted text is deliberately complete on its own.** It keeps all nine numbered items, both
BINs, the statutory invocation, the demand for a specific exemption per withheld record and for
segregable portions, the offer to take redactions, and the request for a date certain. Nothing in it
says "see attached", because if the attachment is mislaid or never opened, a request that depends on
it could be read far more narrowly than intended. The PDF adds detail and formatting; it does not
add scope.

What the condensed version drops: the sub-detail under each item, the contract scope table, the
inspection dates, and some of the explanatory framing. All of that is in the PDF.

**Watch the character count when you fill in your details.** The count above already assumes the
worst case, where the portal counts a line break as two characters. It leaves about **110
characters** of headroom, and the `[Name] - [Postal address] - [Email] - [Phone]` placeholder is 45
of them. A real name and address is typically 70–110, so you will land near 4,960 — under, but not
by much. If the box rejects it, delete the "Context, to help you locate the records" paragraph,
which is explicitly not part of the request and buys you 385 characters.

Regenerate the PDF after any edit to the request:

```powershell
python scripts\build_foil_pdf.py
```

### The MTA request is short enough to paste

The parallel MTA request in §7 is about 1,400 characters and needs no attachment.

**Follow the agency's own three tips**, which are printed on that page and are the difference
between a search and a brush-off:

- *"Be specific as to the records requested."*
- *"Indicate the date or date range of records requested."* — the request below dates every item.
- *"The request must only be for records and not a question requiring an answer."* — this one bites.
  We have a live 14 ft disagreement about the deck width (CONF-014) and it is tempting to ask "which
  is right?". That is a question, and a records officer may properly refuse it. It is asked below as
  a request for *the dimensioned section that would settle it*, which is a record.

## 2. The two BINs — get this right or get half an answer

The Manhattan Bridge is registered by NYC DOT as **two structures**, inspected on different dates
and rated separately. From the
[2024 Bridges and Tunnels Annual Condition Report](https://www.nyc.gov/html/dot/downloads/pdf/dot_bridgereport24.pdf):

| BIN | As DOT names it | Carries / crosses | Last inspection | Rating |
|---|---|---|---|---|
| **2240027** | MANHATTAN BRIDGE (LL) | EAST RIVER | 14 Nov 2024 | 6.3 FAIR |
| **2240028** | MANHATTAN BRIDGE (UL) | NYCTA TRACKS-BMT | 3 Nov 2022 | 5.4 FAIR |

Two consequences, both practical:

- **Name both BINs in every item.** A search on 2240027 alone will not necessarily return upper-level
  records, and the upper level is where OQ-013's framing depths live.
- **This may explain CONF-014.** Our register carries an unresolved 14 ft conflict: 120 ft deck width
  out-to-out from four sources, against 106.0 ft (32.3 m) from the 2010 federal inventory sheet
  (SRC-024). That sheet is for structure **36-2240027 — the lower level only**. If the federal figure
  measures the lower level and the 120 ft figure is out-to-out of the whole structure, the conflict is
  not a contradiction at all but two different measurements. **This is a hypothesis, not a finding.**
  It is not recorded as resolved anywhere in `SOURCE-REGISTER.md`, and it will not be until a
  dimensioned transverse section says so. Item 1(c) asks for exactly that section.

## 3. Before filing — the agency asks you to check what is already public

Doing this is not just courtesy; a request for something already published invites a brush-off that
costs weeks.

**First, search the OpenRecords archive — someone may have asked already.** Every FOIL request filed
through the portal is public, *including the records agencies upload in response*, at
[a860-openrecords.nyc.gov/request/view_all](https://a860-openrecords.nyc.gov/request/view_all)
(no login needed to search; 631,703 requests as of August 2026). If DOT has already released bridge
drawings to someone else, they may be sitting there and the fastest request is the one you do not
have to file. A bare keyword search for "Manhattan Bridge" returns about 6,000 results sorted by
date and is mostly noise — use **Advanced Search Options** to restrict to **Department of
Transportation** and to search agency descriptions, which is where drawing titles would appear.

Already checked and *not* sufficient:

- **NYC DOT's own Manhattan Bridge page** — directly examined on 11 August 2026 and registered as
  SRC-001. It carries exactly four figures: 5,790 ft abutment to abutment at the lower level;
  6,090 ft portal to portal on the upper roadway; 1,470 ft main span; 3,224 ft per cable. All four
  are already grade `A` in this model. No structural geometry beyond them — and note **OQ-025**,
  opened while preparing this request: five further controls cite that page for values it does not
  state, which is one more reason to want the agency's own records rather than its summary.
- **NYC DOT Bridges and Tunnels Annual Condition Report** — condition ratings and the BINs in §2. No
  geometry.
- **NYC Open Data** — no bridge structural drawings.
- **HAER NY-164 / item `ny0980`** (already held, SRC-003) — **11 photographs, 3 data pages and no
  measured drawings**, verified by direct Library of Congress API query. This is the crux: for the
  Brooklyn Bridge, HAER supplied one measured sheet. For this bridge it supplied none. There is no
  public measured drawing of the Manhattan Bridge that we have been able to find.
- **National Bridge Inventory 2010 sheet, structure 36-2240027** (already held, SRC-024) — corroborates
  the main span and gives the 1,230 ft navigation clearance. Inventory data, not geometry, and lower
  level only.
- **Period engineering press** (already held, SRC-015 *Scientific American* 1908, SRC-016 and SRC-017
  *The Engineering Record* 1904) — these are genuinely good and carry the tower and anchorage
  build-ups. They also disagree with each other by 8 ft (CONF-013, OQ-016), which is why a drawing is
  needed to adjudicate.

Say so in the request. It demonstrates the records are not already available and narrows what you
are asking for.

## 4. Request text

This is the full request, and it is what the **PDF** carries. It is about 6,900 characters, so it
does **not** fit the portal's 5,000-character box — paste
[`sources/foil/dot-request-portal.txt`](sources/foil/dot-request-portal.txt) there instead and
attach [the PDF](sources/foil/NYCDOT-FOIL-Manhattan-Bridge.pdf). See §1.

> **Subject: FOIL request — Manhattan Bridge structural record drawings, contract drawings and inspection reports**
>
> To the Records Access Officer:
>
> Under Article 6 of the New York State Public Officers Law, I request access to the following
> records concerning the **Manhattan Bridge**, which I understand NYC DOT registers as two
> structures: **BIN 2240027 (Manhattan Bridge, lower level, over the East River)** and
> **BIN 2240028 (Manhattan Bridge, upper level)**. Please treat every item below as applying to
> **both** BINs. The bridge spans the East River between Canal Street, Manhattan and the Flatbush
> Avenue Extension, Brooklyn, and opened in 1909.
>
> I request **electronic copies** where they exist, delivered by download link or electronic
> transfer. I do not require certified copies. Where a record exists only on paper, microfilm or
> aperture card, please tell me its extent and the estimated copying cost before producing it, so I
> can narrow the request rather than incur an avoidable fee.
>
> **A note on scans, which matters for my purpose:** where drawings are scanned, please provide the
> **full sheet including the title block and the graphic scale bar**, rather than a cropped detail.
> A cropped scan cannot be scaled reliably and is of limited use to me.
>
> **1. Record and as-built drawings of the main bridge** — original construction era, approximately
> **1901–1912**, and any later as-built revisions — including but not limited to:
> a. Tower elevations, plans and sections, including plan dimensions of the tower shafts, the leg
>    spacing, and the dimensions of the arch openings through the towers.
> b. Details of the tower tops at the cable saddles: the saddle castings and their bearings, and the
>    vertical relationship between the saddle seat and the top of the cable.
> c. **Transverse sections through the deck at midspan, at a tower line, and on each approach**,
>    dimensioned, showing the out-to-out width, the positions of the four stiffening trusses, the
>    structural depths of the upper roadway, the lower roadway and the transit floor, and the
>    lateral positions of the four transit track centrelines.
> d. **The cable and suspender schedule**: the main cable profile with sag, and the schedule of
>    suspender lengths along the span. If the original is not available, the equivalent produced for
>    **Contract 14 (2010–2013)**, which replaced all suspenders, would serve equally well.
> e. The longitudinal profile of the upper and lower roadways, with elevations referenced to a
>    **stated datum**, and a statement of which datum that is.
>
> **2. Record and as-built drawings of the anchorages**, both sides: plan dimensions, elevations and
> sections, including the vaulted thoroughfare passing through each anchorage.
>
> **3. Record and as-built drawings of the approach viaducts**, Manhattan and Brooklyn, showing bent
> or pier spacing, the type and structural depth of the longitudinal girders or trusses, and the
> longitudinal grade down to street level.
>
> **4. Foundation and caisson drawings** for both towers, showing the depth of the cutting edge, the
> height of the caisson, the founding level and the top of the masonry pier, each referenced to a
> stated datum.
>
> **5. Contract and record drawings from the rehabilitation programme begun in 1982.** DOT's own
> Manhattan Bridge page lists these; I am asking for the as-built geometry they document rather than
> temporary works or means and methods. Specifically:
>
> | Contract | Period | Scope, as DOT describes it |
> |---|---|---|
> | 8 | 1992–1997 | South Side Approach and Suspended Spans |
> | 8C | 1997–2001 | South Side Towers, Cables A and B |
> | 10 | 2001–2004 | North Main Span, North Bikeway, Approach Tunnels |
> | 11 | 2005–2008 | Lower Roadway, including Manhattan Approach Spans |
> | 14 | 2010–2013 | Cable re-wrapping and suspender replacement |
> | 15 | 2018–2021 | Saddles and saddle housings, anchorage housings, truss members, transit floor beams, tower ornamental features |
>
> **6. The two most recent biennial inspection reports for each BIN**, including attached sketches,
> load ratings and element-level condition data. I note the most recent inspections recorded in the
> 2024 Annual Condition Report are **14 November 2024 for BIN 2240027** and **3 November 2022 for
> BIN 2240028**.
>
> **7. Any survey control on the structure** — geodetic coordinates, monument descriptions or
> control diagrams for the tower centres or anchorage corners, in any stated coordinate system.
> A single surveyed tower position would be sufficient.
>
> **8. Any existing three-dimensional survey of the structure** — laser scan, LiDAR or point cloud
> data, or a photogrammetric survey — produced for any of the contracts above or for inspection
> purposes. I would take this in whatever form it exists, including a raw point cloud.
>
> **9. Any index, drawing register, aperture-card list or file inventory** covering the above, and
> **the portion of the Department's subject matter list** maintained under Public Officers Law
> §87(3)(c) that covers bridge engineering records. **If producing the drawings themselves is
> burdensome, I would value the index first** — it would let me identify a much smaller set of
> specific sheets and resubmit a narrower request.
>
> **Context, offered to help you locate the records rather than as part of the request:** I am
> building an openly published, source-documented three-dimensional model of the bridge, in which
> every dimension is traceable to a cited source and anything unsourced is labelled a placeholder and
> drawn as such. The records above would replace **fourteen placeholder dimensions** with documented
> ones and would close or materially advance most of the twenty-five open questions the project
> currently records. The project is public at
> https://github.com/Ethical-Tech-CoLab/manhattan-bridge-3d and any records provided will be credited
> to NYC DOT.
>
> I have already reviewed and am **not** requesting: NYC DOT's published Manhattan Bridge facts page;
> the Bridges and Tunnels Annual Condition Report; NYC Open Data holdings; the HAER survey at the
> Library of Congress (HAER NY-164, item ny0980, which contains photographs but **no measured
> drawings**); and the 2010 National Bridge Inventory sheet for structure 36-2240027. Those are held
> already and do not contain the dimensions sought.
>
> If any part of this request is denied, please cite the specific statutory exemption for each
> withheld record and release the remainder, including any reasonably segregable portions.
>
> If security review is required before release of structural drawings, I am content to receive a
> redacted set, or to discuss narrowing the request to the **original 1901–1912 construction-era
> drawings alone**, which are more than a century old and describe a structure whose form is visible
> from the public walkway.
>
> Please acknowledge receipt and provide a date certain for a response.
>
> [Name] · [Postal address] · [Email] · [Phone]

**Why it is shaped this way.** FOIL requires records be *reasonably described* — the commonest
denial is "the request is overbroad", not "these records are exempt". Every item names a structure, a
record type, a date range and a purpose. Item 5 describes the records in DOT's own filing terms,
using the contract numbers DOT itself publishes, which is the single strongest thing you can do to
make a search cheap for the agency. Item 9 is the escape hatch: a drawing index is cheap to produce
and lets a second, surgical request follow, and the subject matter list must exist by statute.
Naming what you already hold pre-empts the "already publicly available" response. Offering to narrow
to the 1901–1912 drawings pre-empts the security objection, which is the one genuinely likely to
bite on a landmark East River crossing — and a 1909 drawing is a much easier release for an agency
than a current one.

## 5. What this retires

Fourteen controls in `GEOMETRY-CONTROL.md` are grade `D` placeholders. `GRT-070` holds that count at
14 and fails if it rises. Every one of them is waiting on a drawing.

| Control | What is invented today | Request item |
|---|---|---|
| CTL-101 | Minimum suspender length at midspan, 3 ft — this is what sets the cable sag | 1(d) |
| CTL-102 | Saddle drop below cable top, **currently zero**, so the model treats the cable top as the saddle seat | 1(b), 5 (Contract 15) |
| CTL-103 | Upper deck structural depth, 3 ft | 1(c) |
| CTL-104 | Lower deck offset above clearance, 3.4 ft | 1(c) |
| CTL-105 | Innermost subway track offset, 27 ft | 1(c), §7 |
| CTL-106 | Track spacing within a bay, 14 ft | 1(c), §7 |
| CTL-107 | Track structure depth, 1.5 ft | 1(c), §7 |
| CTL-108 | Approach bent spacing, 100 ft — chosen only so the approach reads as a viaduct | 3 |
| CTL-109 | Approach bent width, 8 ft | 3 |
| CTL-110 | Approach girder depth, 10 ft | 3 |
| CTL-111 | Tower arch height-to-width ratio — measured off a photograph, not a drawing | 1(a) |
| CTL-112 | Tower arch head rise fraction | 1(a) |
| CTL-115 | Anchorage arch springing height, 30 ft | 2 |
| CTL-116 | Anchorage arch jamb width, 12 ft | 2 |

Open questions retired or materially advanced — **22 of the 25** on the register: **OQ-001** (cable
sag), **OQ-002**, **OQ-003**
(foundation depth), **OQ-004** (which deck the 46 ft roadway belongs to), **OQ-005**, **OQ-006**,
**OQ-007** (tower plan), **OQ-008** (anchorage plan), **OQ-009** (geodetic anchor, via item 7),
**OQ-010** (track centrelines), **OQ-011**/**OQ-012** (the cable-diameter and truss-depth conflicts),
**OQ-013** (framing depths), **OQ-014** (the 2 ft per side that does not close), **OQ-015**,
**OQ-016** (the 8 ft build-up disagreement), **OQ-017** (truss members and diagonal handedness),
**OQ-019** (materials), **OQ-020** (approach form), **OQ-021** (measured capture, via item 8),
**OQ-023** and **OQ-024** (the arches). Also **CONF-014**, per §2.

Not touched by this request, and honest about it: **OQ-018** is a disagreement inside a consuming
module's tile index and is ours to fix; **OQ-022** is a citation discrepancy for the Library of
Congress to answer. **OQ-025** is half-touched: item 1 would confirm or correct the five contested
values directly, but the question of what NYC DOT's web page said in the past is answered by a web
archive, not by FOIL.

## 6. The statutory clock

| When | What must happen |
|---|---|
| **5 business days** from receipt | The agency must grant access, deny in writing, or acknowledge in writing with an approximate date |
| **20 business days** | If it acknowledged, that is the outside date for granting or denying; beyond it the agency must give a **date certain** and a reason |
| **Failure to meet the above** | Is a **constructive denial** — appealable exactly like a written one |
| **30 days** from a denial | Your window to appeal, in writing, to the Appeals Officers |
| **10 business days** from your appeal | The agency must fully explain in writing or grant access. Missing this is itself a denial (§89(4)(b)) and opens Article 78 review |

Diary the 5-day and 20-day dates when you file. Agencies respond to requesters who track dates.

If the appeal fails, the **NYS Committee on Open Government** issues free advisory opinions
(docs@dos.ny.gov). They carry no force but agencies take them seriously and it costs nothing.

### 6b. The appeal, ready to send

The likeliest outcome is not a refusal on the merits — it is **silence**, or a partial release that
omits the drawings. Both are appealable, and the appeal is a short letter. Statutory basis: Public
Officers Law §89(4)(a) gives you thirty days and gives the agency ten business days to answer in full.

Send to **foilappeal@dot.nyc.gov** (Edalia George and Michael Twomey), copying foiladmin@dot.nyc.gov,
with the original request and any response attached.

> **Subject: FOIL appeal — [request number] — Manhattan Bridge structural records**
>
> To the Records Access Appeals Officer:
>
> Under Public Officers Law §89(4)(a) I appeal the determination on my request of [date], reference
> [number], for record drawings, contract drawings and inspection reports for the Manhattan Bridge
> (BIN 2240027 and BIN 2240028).
>
> *[Use whichever applies.]*
>
> **If nothing was received:** The agency has neither granted access, denied the request in writing,
> nor furnished a written acknowledgement within five business days. Under §89(4)(a) and the
> Committee on Open Government's guidance, that failure constitutes a constructive denial, and I
> appeal it as such.
>
> **If the date has slipped:** The agency acknowledged the request on [date] with an approximate date
> of [date], which has now passed without a determination or a further date certain. I appeal that
> constructive denial.
>
> **If records were withheld:** The response withheld [describe] without citing a specific exemption
> for each withheld record. FOIL presumes access; the burden of justifying a withholding rests with
> the agency, and any reasonably segregable portion of an exempt record must still be released. I ask
> that the withholding be reversed or, at minimum, that each exemption be cited specifically and the
> segregable remainder produced.
>
> **If only one structure was searched:** The response appears to address only BIN [number]. NYC DOT
> registers this bridge as two structures, BIN 2240027 and BIN 2240028, and the original request
> applied to both. I ask that the search be extended to the second structure.
>
> I remain willing to accept redacted drawings, or to narrow the request to the 1901–1912
> construction-era drawings, if security review is the obstacle. I would also accept the drawing
> index and the relevant portion of the subject matter list alone as a first step, which item 9 of
> the original request offered.
>
> Please respond within ten business days as §89(4)(a) requires. That subdivision also provides that
> the agency shall immediately forward a copy of this appeal, and of your determination on it, to the
> Committee on Open Government.
>
> [Name] · [Address] · [Email] · [Phone]

That last sentence matters more than its length suggests: the forwarding duty is the agency's, not
yours, and citing it signals that the deadline will be noticed by someone other than the requester.

**If the appeal is not determined within ten business days**, that failure is itself a denial, and
§89(4)(b) opens review by the courts under CPLR Article 78. That is a real step with real cost, so in
practice the sequence before it is: a polite reminder at the ten-day mark, then a free advisory
opinion from the Committee on Open Government (docs@dos.ny.gov), then Article 78 only if the records
genuinely matter more than the effort. For this project they probably do not — the fallbacks in §9
are cheaper than litigation and often faster.

## 7. The parallel MTA request — this bridge only

The Brooklyn Bridge carries no railway. This one carries four NYCTA tracks on the lower level, and
DOT's own condition report describes BIN 2240028 as crossing "NYCTA TRACKS-BMT". Three of our
placeholders — **CTL-105**, **CTL-106**, **CTL-107** — and two open questions — **OQ-010** and part
of **OQ-013** — are about track geometry that DOT may not hold at all.

File a second, short request with the MTA at the same time. The MTA is a state public authority and
is subject to the same Article 6.

| | |
|---|---|
| **Preferred** | [MTA FOIL portal](https://www.mta.info/transparency/foil) |
| **By mail** | FOIL Team, MTA Legal Department, 2 Broadway, 4th Floor, New York, NY 10004 |
| **Note** | The MTA FOIL team processes requests for all MTA agencies, so one request covers NYCTA |

> **Subject: FOIL request — Manhattan Bridge transit track structure, records**
>
> Under Article 6 of the Public Officers Law I request records held by the MTA or New York City
> Transit concerning the **four transit tracks carried on the lower level of the Manhattan Bridge**
> (NYC DOT BIN 2240027), on the BMT alignment serving the B, D, N and Q services:
>
> 1. **Track charts or track alignment drawings** for the bridge crossing, showing track centrelines
>    and the spacing between tracks, and the transverse position of each track relative to the bridge
>    structure.
> 2. **Sections through the transit floor** showing the structural depth of the track support system,
>    from the running rail down to the supporting floor beams.
> 3. Drawings or records from the **transit floor beam retrofit on the approach spans** carried out
>    under NYC DOT Contract 15 (2018–2021), to the extent MTA or NYCT holds them.
> 4. Any **index or drawing register** covering the above.
>
> I request electronic copies. I am building an openly published, source-documented model of the
> bridge in which every dimension is traceable to a cited source; these records would replace three
> invented placeholder dimensions with documented ones. The project is public at
> https://github.com/Ethical-Tech-CoLab/manhattan-bridge-3d and any records provided will be credited.
>
> [Name] · [Address] · [Email] · [Phone]

## 8. Processing the response — the part that matters

Records arriving is where a source-governed model is most at risk, because a drawing *feels*
authoritative and the temptation is to start typing numbers.

**Register before reading.** Give every document a `SRC-0xx` row in `SOURCE-REGISTER.md`, marked
**registered, not read**, before extracting a single dimension. Commit the file bytes and record a
SHA-256. A number whose source row was written afterwards is a number nobody can audit. `SRC-004`
already exists as a stub for the 1907–1909 contract drawings; fill it in rather than opening a new row.

**Index the whole thing before using any of it.** The sibling Brooklyn project lost a 272-photograph
campaign to exactly this: a source was marked read on the strength of its data pages while its 77
photographs — which answered two open questions — went unindexed for the entire project. Produce a
`sources/<src>-index.json` listing every sheet and what it depicts **before** the first control is
edited. We have the same exposure here: our own `SRC-003` (HAER NY-164) carries 11 photographs and
3 data pages, and OQ-022 is an unresolved discrepancy about its own call number.

**Grade honestly, per document, not per delivery.**

| Document | Grade | Why |
|---|---|---|
| As-built / record drawing, dimension printed on it | `A` | An official measured statement |
| Same drawing, dimension *scaled off* it | `B`, and say so | Scaling is arithmetic on an image, which is why the request asks for full sheets with the title block and graphic scale rather than cropped details |
| Contract drawing marked "proposed", or a rehabilitation drawing showing intended work | `B` at best | Intent is not as-built. CONF-012 already records the 1904 design differing from what was built — 9,330 ft and 120 ft wide against the as-built figures |
| Inspection report, condition and element data | `A` for condition | It is an inspection, its purpose |
| Inspection report, dimensions | `B` unless dimensioned | Field notes are not survey |
| Point cloud or laser scan (item 8) | `C` — this is what `MEASURED` means here | An instrument reading of the actual structure, which is what OQ-021 asks for |

**Check the datum before any elevation is used.** This model is entirely referenced to **mean high
water** and never converts; the shared contract declares `"vertical_datum": "MHW"` and the 0.59 m
offset to NAVD88 is applied at placement time, not in the geometry. NYC DOT drawings may use NAVD88,
the Borough of Manhattan datum, or a project datum. An elevation adopted without checking its datum
is a silent error of about two feet that every downstream check will pass. If the datum is unstated,
the elevation is not usable — record it and open an OQ rather than assuming. This is why item 1(e)
asks the agency to state the datum rather than leaving it to be inferred.

**Expect conflicts and register them; do not overwrite.** Fifteen `CONF-0xx` rows already exist, and
several are between sources that are each individually credible — CONF-005 has four different tower
heights, CONF-013 has two caisson heights 8.5 ft apart from two contemporaneous engineering journals.
A newer document is not automatically right: it may be a proposal, a different datum, a different
measuring point, or the other BIN. Add a row stating both values and the reasoning.

**Change one control at a time and let the harness object.** After each edit run:

```powershell
python scripts\build_control_skeleton.py
python scripts\validate_dimensions.py
```

`STT-012` will fail until the model is rebuilt from the edited document — that is the hash guard
working. The cross-source checks are the interesting ones: a real dimension that breaks one has found
either a mistake in the reading or a genuine disagreement, and both are worth more than a clean run.

**Retire placeholders explicitly, and ratchet the guard.** A `D` control becoming `A` should close its
open question and **lower `GRT-070`'s expected count from 14**. That test exists so the number can
only go down; lowering it is the point, and leaving it at 14 after a placeholder is retired hides the
win.

**Watch for the reverse failure.** A sourced dimension that never reaches geometry is invisible. The
Brooklyn project registered eight saddle bearings at grade `A` and left them unmodelled for its whole
life. Here, `CTL-102` is the live example in the other direction: a placeholder of *zero* that the
geometry silently depends on.

## 9. If the drawings do not come

The likeliest outcomes are a security-based denial or a partial release. Fallbacks, in order:

1. **Ask for the index and the subject matter list alone** (item 9). Rarely refused, and it makes the
   next request precise.
2. **Narrow to the 1901–1912 drawings.** Century-old drawings of a structure you can walk across
   attract far fewer security objections than current ones, and they answer most of the open
   questions, which are about original geometry rather than present condition.
3. **NYC Municipal Archives** — holds the Department of Bridges and Department of Plant and
   Structures records. Already registered here as `SRC-009` and `SRC-023` and still unexamined. A
   different custodian with a different disposition, and archival material attracts fewer security
   objections. **This is the strongest fallback for this bridge** and is arguably worth doing in
   parallel rather than in sequence.
4. **NYSDOT** — holds biennial inspection records for all NYS bridges including city-owned ones, and
   submitted the federal inventory sheet we already hold as `SRC-024`.
5. **The MTA request in §7**, which covers the track geometry regardless of what DOT does.
6. **Commission a survey, or run photogrammetry from the public walkway.** The walkway is open and
   the bridge is photographable from it. This retires `OQ-021` and is the only route to `MEASURED`
   geometry that does not depend on anyone else's cooperation.
