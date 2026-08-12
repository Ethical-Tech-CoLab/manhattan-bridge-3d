# FOIL submission log

Every records request this project has filed, what came back, and where it landed in the register.
The request texts are in [FOIL-REQUEST.md](../../FOIL-REQUEST.md); this file is the running record of
what was actually sent.

The point of keeping it here rather than in someone's inbox: when records arrive they become
`SRC-0xx` rows in [SOURCE-REGISTER.md](../../SOURCE-REGISTER.md), and a source whose provenance
begins "someone emailed it to me" is weaker than one that can be traced to a dated, numbered request
to a named agency. This file is that trace.

---

## FOIL-2026-030-00205 — Department of City Planning

| | |
|---|---|
| **Reference** | `FOIL-2026-030-00205` |
| **Agency** | Department of City Planning (DCP) |
| **Records Access Officer** | Jennifer Bartholomew — Jbartholomew@planning.nyc.gov |
| **Submitted** | Tuesday 11 August 2026 |
| **Status at filing** | Open · Under Review |
| **Portal record** | https://a860-openrecords.nyc.gov/request/view/FOIL-2026-030-00205 |
| **Request text sent** | [`dot-request-portal.txt`](dot-request-portal.txt) |
| **Attachment** | [`NYCDOT-FOIL-Manhattan-Bridge.pdf`](NYCDOT-FOIL-Manhattan-Bridge.pdf) |

### Statutory dates

| Date | What is due |
|---|---|
| **Tue 18 Aug 2026** | 5 business days: DCP must grant, deny in writing, or acknowledge with an approximate date |
| **Wed 9 Sep 2026** | 20 business days: outside date for a determination if it acknowledged |
| **Thu 10 Sep 2026** | 30 calendar days from a denial: the appeal window closes |

Silence past 18 August is a **constructive denial** and is appealable exactly like a written one.

### ⚠ This went to the wrong agency

The request asks for bridge structural record drawings, contract drawings, biennial inspection
reports and survey control. **DCP does not hold any of those.** DCP is the city's land-use and
zoning agency: zoning maps and text, PLUTO and MapPLUTO, the LION street centreline, the NYC 3-D
Building Model, environmental review. Its collections contain no bridge engineering records, and the
3-D building model does not include bridges.

The custodian is **NYC DOT**, which owns and inspects the structure. Both BINs named in the request
— 2240027 and 2240028 — are DOT structures in DOT's own Bridges and Tunnels Annual Condition Report,
and the rehabilitation contracts the request names are DOT contracts.

For reference, so the mistake is not repeated: on the OpenRecords portal the middle segment of the
reference number is the agency. `030` is DCP. **DOT is `841`** — a DOT request looks like
`FOIL-2026-841-#####`.

| | DCP (where it went) | DOT (where it should go) |
|---|---|---|
| Records Access Officer | Jennifer Bartholomew | Judith Falk — foiladmin@dot.nyc.gov |
| Appeals | — | Edalia George and Michael Twomey — foilappeal@dot.nyc.gov |
| Holds bridge structural drawings? | **No** | Yes |

### What to do about it

**Superseded: the DOT request was filed on 11 August 2026 as `FOIL-2026-841-04819`** — see the entry
below. There is now a live request with the agency that actually holds the records, so this one no
longer matters.

Optionally send [`dcp-reroute-message.txt`](dcp-reroute-message.txt) through **Contact the Agency**
on the request page, asking DCP to close it. Courtesy rather than strategy: it stops a records
officer searching for records that were never theirs. It was important not to withdraw this one
before the DOT request existed; that condition is now met.

**A "no records" response from DCP is not a denial worth appealing.** It would be correct. The
appeal machinery in FOIL-REQUEST.md §6b is aimed at an agency that holds records and will not
produce them; it does not apply to an agency that genuinely has none.

### Outcome

*To be recorded.* When a determination arrives, note it here, then follow
[FOIL-REQUEST.md §8](../../FOIL-REQUEST.md) before extracting a single dimension: register each
document as `SRC-0xx` marked **registered, not read**, record its SHA-256, and index every sheet
before the first control is edited.

---

## FOIL-2026-841-04819 — Department of Transportation ✅ the real one

| | |
|---|---|
| **Reference** | `FOIL-2026-841-04819` |
| **Agency** | **Department of Transportation (DOT)** — the correct custodian |
| **Records Access Officer** | Judith Falk — foiladmin@dot.nyc.gov |
| **Appeals Officers** | Edalia George and Michael Twomey — foilappeal@dot.nyc.gov |
| **Title** | FOIL request - Manhattan Bridge structural record drawings and inspection reports |
| **Submitted** | Tuesday 11 August 2026 |
| **Status** | Open · Under Review · *"The agency is working on a response."* |
| **Portal record** | https://a860-openrecords.nyc.gov/request/view/FOIL-2026-841-04819 |
| **Request text sent** | [`dot-request-portal.txt`](dot-request-portal.txt) |
| **Attachment** | [`NYCDOT-FOIL-Manhattan-Bridge.pdf`](NYCDOT-FOIL-Manhattan-Bridge.pdf) |

The `841` in the reference confirms it reached DOT rather than City Planning, and the portal names
the assigned agency as Department of Transportation.

### Statutory dates

| Date | What is due | Source |
|---|---|---|
| **Tue 18 Aug 2026** | 5 business days: acknowledge, grant, or deny in writing | **Stated by the portal** as the Acknowledgment Due Date |
| **Wed 9 Sep 2026** | 20 business days: outside date for a determination if it acknowledged | Computed |
| **Thu 10 Sep 2026** | 30 calendar days from a denial: appeal window closes | Computed |

The portal's own acknowledgment date agrees with the independently computed one, which is a small
but useful check that the 5-day clock started on 11 August.

**Diary 18 August.** Silence past that date is a **constructive denial** and is appealable exactly
like a written refusal — the letter is ready in [FOIL-REQUEST.md §6b](../../FOIL-REQUEST.md).

### What a good outcome looks like

Any one of these would be worth the filing on its own:

- **The Contract 14 suspender schedule** (item 1d) — retires `CTL-101` and with it the cable sag.
- **A dimensioned transverse section** (item 1c) — retires `CTL-103`, `CTL-104`, `CTL-105`,
  `CTL-106`, `CTL-107` in one document, and settles `CONF-014`.
- **The drawing index alone** (item 9) — cheap for DOT to produce and lets a surgical second request
  follow.

### Outcome

*Awaiting response.* When records arrive, follow
[FOIL-REQUEST.md §8](../../FOIL-REQUEST.md) **before** extracting a single dimension: register each
document as `SRC-0xx` marked **registered, not read**, record its SHA-256, and index every sheet
before the first control is edited. Then grade per document, check the datum on every elevation, and
ratchet `GRT-070` down from 14 as placeholders retire.

---

## R016646-081226 — MTA / New York City Transit ✅

| | |
|---|---|
| **Reference** | `R016646-081226` |
| **Agency** | Metropolitan Transportation Authority — the FOIL team processes for all MTA agencies, including NYCT |
| **Received** | Wednesday 12 August 2026 (date stated by the agency) |
| **Status** | Receipt confirmed; acknowledgment promised within 5 business days |
| **Tracking** | [My Records Center](https://mtany.govqa.us/WEBAPP/_rs/CustomerIssues.aspx) — GovQA, a different system from NYC OpenRecords |
| **Request text** | [`mta-request-portal.txt`](mta-request-portal.txt) |
| **Attachment** | none needed |

The account used to file is deliberately **not recorded here**. This repository is public, and a
personal email address committed to it would be scraped. It is in the filer's own inbox and in the
GovQA account; it does not need to be in version control to make the request traceable — the
reference number and date do that.

### Statutory dates

| Date | What is due |
|---|---|
| **Wed 19 Aug 2026** | 5 business days: acknowledge, grant, or deny in writing |
| **Thu 10 Sep 2026** | 20 business days: outside date for a determination if acknowledged |
| **Fri 11 Sep 2026** | 30 calendar days from a denial: appeal window closes |

One day later than the DOT request throughout, because it was received on the 12th rather than the
11th. Diary both.

### Three clauses were dropped in transit

The submitted text is very slightly shorter than
[`mta-request-portal.txt`](mta-request-portal.txt) as committed. Comparing the agency's own echo of
the request against the file:

| Clause | Committed | Submitted |
|---|---|---|
| BIN 2240027, items 1–4, electronic copies, cost before production, per-record exemption | ✅ | ✅ |
| "including any reasonably segregable portions" | ✅ | ✗ |
| "provide a date certain for a response" | ✅ | ✗ |
| "Please acknowledge receipt" | ✅ | ✗ |

**None of this is worth refiling for**, and all three losses are recoverable:

- **Segregable portions is a statutory duty, not a favour.** Public Officers Law §87(2) requires an
  agency to redact an exempt portion and release the rest whether or not you ask. Asking makes it
  harder to overlook; not asking does not waive it.
- **The acknowledgment is already promised.** The receipt states one will follow within five
  business days, which is the same outcome the "date certain" sentence exists to force.
- **Receipt is already acknowledged.** The confirmation is itself the acknowledgment of receipt.

If the response withholds records without citing an exemption per record, the appeal in
[FOIL-REQUEST.md §6b](../../FOIL-REQUEST.md) still applies — it argues from the statute, not from
what the request happened to say.

### What it would retire

`CTL-105` (innermost track offset, 27 ft), `CTL-106` (track spacing, 14 ft), `CTL-107` (track
structure depth, 1.5 ft) and `OQ-010`. Item 1 alone — a track chart showing centrelines and spacing
— would retire all three, and none of them is answerable from the DOT request if DOT does not hold
transit track geometry.

**Still worth having after SRC-026.** System-wide rolling-stock dimensions now bound `CTL-106`
from below at about 11.8 ft, which is real progress and came from a standard rather than an
archive. It does not narrow this request. A floor is not a value, and `CTL-105` — where the pair
sits relative to *this bridge's* axis — is untouched by any network-wide fact, which is exactly
what item 1's phrase *"relative to the bridge structure"* is there to obtain.

### Outcome

*Awaiting response.* Same discipline as the DOT request:
[FOIL-REQUEST.md §8](../../FOIL-REQUEST.md) before any dimension is extracted.

---

## Filing checklist

Everything below is prepared and ready to paste. Filing requires a logged-in NYC account and puts
your name, address and telephone number on a legal request, so it has to be done by a person.

### 1. The DOT request — ✅ filed 11 August 2026 as `FOIL-2026-841-04819`

Kept for the record, and as the recipe if a narrower second request follows once the drawing index
arrives.

1. Log in at <https://a860-openrecords.nyc.gov/auth/login>, then **Request a Record**.
2. Agency: **Department of Transportation**.
   Check the reference number you get back starts `FOIL-2026-841-` — `841` is DOT. If it says
   `030` you have hit City Planning again.
3. Paste [`dot-request-portal.txt`](dot-request-portal.txt) into the request box.
   It is 4,890 characters against a 5,000 limit, so **replace the `[Name] - [Postal address] -
   [Email] - [Phone]` line with your details and watch the counter.** If it will not fit, delete the
   paragraph beginning "Context, to help you locate the records" — that is explicitly not part of
   the request and frees 385 characters.
4. Attach [`NYCDOT-FOIL-Manhattan-Bridge.pdf`](NYCDOT-FOIL-Manhattan-Bridge.pdf).
5. Record the reference number and date in the table at the top of this file, and diary the
   five-business-day date.

### 2. The MTA request — ✅ filed 12 August 2026 as `R016646-081226`

Different portal: <https://www.mta.info/transparency/foil>. The MTA is a state public authority and
is not on OpenRecords; it runs GovQA, so requests are tracked in
[My Records Center](https://mtany.govqa.us/WEBAPP/_rs/CustomerIssues.aspx) rather than on the NYC
portal, and reference numbers look like `R######-MMDDYY` rather than `FOIL-YYYY-AAA-#####`.

Paste [`mta-request-portal.txt`](mta-request-portal.txt). It is about 1,800 characters and needs no
attachment. It covers `CTL-105`, `CTL-106`, `CTL-107` and `OQ-010` — track geometry DOT may not hold
at all.

**Paste the whole file.** Three closing clauses were lost from the submitted version — see the
`R016646-081226` entry above. No harm done in this instance, but the last paragraphs are the ones
carrying the statutory asks, and they are the easiest to lose to a scroll box.

### 3. Tidy up the DCP request — optional, one minute

On the [DCP request page](https://a860-openrecords.nyc.gov/request/view/FOIL-2026-030-00205) use
**Contact the Agency** and send [`dcp-reroute-message.txt`](dcp-reroute-message.txt). Courtesy rather
than strategy: it stops a records officer searching for records that were never theirs.

**Do not withdraw the DCP request until the DOT one is filed.** Keep at least one live request at
all times.

---

## Not yet filed

| Request | Agency | Text | Reference | Filed |
|---|---|---|---|---|
| Manhattan Bridge structural records | **NYC DOT** | [`dot-request-portal.txt`](dot-request-portal.txt) + [PDF](NYCDOT-FOIL-Manhattan-Bridge.pdf) | **FOIL-2026-841-04819** | **11 Aug 2026** ✅ |
| Transit track structure on the lower level | **MTA / NYCT** | [`mta-request-portal.txt`](mta-request-portal.txt) | **R016646-081226** | **12 Aug 2026** ✅ |
| Misfiled duplicate, superseded | DCP | — | FOIL-2026-030-00205 | 11 Aug 2026 ✗ |

**Both live requests are filed.** Nothing further to submit; the next action is a diary entry, not a
form. Watch **19 August** (MTA) and **18 August** (DOT) — silence past either is a constructive
denial, and the appeal letter is ready in [FOIL-REQUEST.md §6b](../../FOIL-REQUEST.md).
