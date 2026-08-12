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

**Refile with DOT now rather than waiting.** DCP may reroute the request, but nothing obliges it to,
and the likely outcome is a "no records" determination that costs the full five to twenty business
days and leaves you no further forward. Filing with DOT today starts a second, independent clock
against the agency that actually holds the records. There is no penalty for having two open
requests, and the wasted one costs nothing but its own reference number.

See [the filing checklist](#filing-checklist) below — everything is prepared, and it is about two
minutes of work.

**A "no records" response from DCP is not a denial worth appealing.** It would be correct. The
appeal machinery in FOIL-REQUEST.md §6b is aimed at an agency that holds records and will not
produce them; it does not apply to an agency that genuinely has none.

### Outcome

*To be recorded.* When a determination arrives, note it here, then follow
[FOIL-REQUEST.md §8](../../FOIL-REQUEST.md) before extracting a single dimension: register each
document as `SRC-0xx` marked **registered, not read**, record its SHA-256, and index every sheet
before the first control is edited.

---

## Filing checklist

Everything below is prepared and ready to paste. Filing requires a logged-in NYC account and puts
your name, address and telephone number on a legal request, so it has to be done by a person.

### 1. The DOT request — the one that matters

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

### 2. The MTA request — file at the same time

Different portal: <https://www.mta.info/transparency/foil>. The MTA is a state public authority and
is not on OpenRecords.

Paste [`mta-request-portal.txt`](mta-request-portal.txt). It is about 1,800 characters and needs no
attachment. It covers `CTL-105`, `CTL-106`, `CTL-107` and `OQ-010` — track geometry DOT may not hold
at all.

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
| Manhattan Bridge structural records | **NYC DOT** — the one that matters | [`dot-request-portal.txt`](dot-request-portal.txt) + [PDF](NYCDOT-FOIL-Manhattan-Bridge.pdf) | *pending* | *pending* |
| Transit track structure on the lower level | MTA / NYCT | [`mta-request-portal.txt`](mta-request-portal.txt) | *pending* | *pending* |
