"""Ingest a photo, video or mesh into /sources with licence and provenance capture.

Every asset that could influence geometry enters through here, so the register and the files on disk
cannot drift apart. An asset is refused unless it carries:

  * a registered ``SRC-###`` ID that already exists in SOURCE-REGISTER.md
  * a licence, named explicitly -- "Wikimedia Commons" is a platform, not a licence
  * an attribution string, because most open licences require one
  * an observation date, separate from the retrieval date, because a photograph describes a moment

Refusing is the point. A silent no-op would let an unlicensed or undated file reach the model, and
CONFIDENCE-MODEL.md section 6.3 records that per-file licence and observation date are the two
things that most often go wrong with crowdsourced imagery.

What this script does NOT do is grade anything. Ingesting a photograph makes it citable; it does not
promote a control. See CONFIDENCE-MODEL.md section 6.2 for what a photograph may and may not grade.

Examples::

    python scripts/ingest_sources.py --list-sets
    python scripts/ingest_sources.py --verify

    python scripts/ingest_sources.py \\
        --file "C:/photos/anchorage.jpg" \\
        --source-id SRC-006 \\
        --kind photo \\
        --licence "CC BY-SA 4.0" \\
        --attribution "Jane Doe, via Wikimedia Commons" \\
        --observed 2024-06-11 \\
        --url https://commons.wikimedia.org/wiki/File:Example.jpg \\
        --image-set image-set-007-anchorages \\
        --coverage "Brooklyn anchorage, north face"
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCES = REPO / "sources"
REGISTER = REPO / "SOURCE-REGISTER.md"
MANIFEST = SOURCES / "asset-manifest.json"

SOURCE_ID_RE = re.compile(r"^SRC-\d{3}$")

KINDS = {
    "photo": SOURCES / "photos",
    "video": SOURCES / "videos",
    "drawing": SOURCES / "drawings",
    "mesh": SOURCES / "existing-meshes",
    "photogrammetry": SOURCES / "photogrammetry",
}

# Image sets from AGENT-INSTRUCTIONS.md section 8. Ingesting without a set is allowed; inventing a
# set name is not, because these names are how coverage gaps stay visible.
IMAGE_SETS = (
    "image-set-001-main-towers",
    "image-set-002-main-cables",
    "image-set-003-suspenders",
    "image-set-004-deck-trusses",
    "image-set-005-subway-track-bays",
    "image-set-006-pedestrian-path",
    "image-set-007-anchorages",
    "image-set-008-approach-spans",
    "image-set-009-ornamental-details",
)

USES = ("visual_reference", "photogrammetry", "texture", "measurement_aid")

# Licences that permit redistributing a stored copy. Anything else may be cited by URL and
# checksum but is not copied into the repository, which is what SRC-005 warns about.
REDISTRIBUTABLE = (
    "cc0",
    "cc by 4.0",
    "cc by-sa 4.0",
    "cc by 3.0",
    "cc by-sa 3.0",
    "cc by 2.0",
    "cc by-sa 2.0",
    "public domain",
    "pd-us",
)


class IngestError(RuntimeError):
    """Raised when an asset does not satisfy the ingest contract."""


def registered_source_ids() -> set[str]:
    return set(re.findall(r"\bSRC-\d{3}\b", REGISTER.read_text(encoding="utf-8")))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {
        "note": (
            "Every asset under /sources that may influence geometry. Written by "
            "scripts/ingest_sources.py; do not hand-edit. Ingestion makes an asset citable, not "
            "authoritative -- see CONFIDENCE-MODEL.md section 6."
        ),
        "assets": [],
    }


def save_manifest(manifest: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_licence_record(asset: dict) -> Path:
    path = SOURCES / "licenses" / f"{asset['source_id']}-{asset['sha256'][:12]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# Licence record for {asset['original_name']}",
                "",
                f"- **Source ID**: {asset['source_id']}",
                f"- **Licence**: {asset['licence']}",
                f"- **Attribution**: {asset['attribution']}",
                f"- **Retrieved from**: {asset['url'] or 'not recorded'}",
                f"- **Retrieved on**: {asset['retrieved_date']}",
                f"- **Observed on**: {asset['observed_date']}",
                f"- **SHA-256**: `{asset['sha256']}`",
                f"- **Stored in repository**: {asset['stored_copy']}",
                f"- **May be displayed**: {asset['display_permitted']}",
                f"- **Stored as**: {asset['stored_as']}",
                "",
                "The observation date is the date the photograph or video records, not the date it",
                "was downloaded. Geometry derived from this asset inherits that date, because a",
                "source describes a moment; see CONFIDENCE-MODEL.md section 6.3.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def ingest(args: argparse.Namespace) -> int:
    source_path = Path(args.file)
    if not source_path.is_file():
        raise IngestError(f"{source_path} is not a file")
    if not SOURCE_ID_RE.match(args.source_id):
        raise IngestError(f"{args.source_id!r} is not a SRC-### identifier")
    if args.source_id not in registered_source_ids():
        raise IngestError(
            f"{args.source_id} is not registered in SOURCE-REGISTER.md. Register the source first; "
            "assets may not enter ahead of the register."
        )
    if args.image_set and args.image_set not in IMAGE_SETS:
        raise IngestError(f"{args.image_set!r} is not a known image set")
    # "unknown" is a first-class answer. An earlier version of this script demanded an ISO date
    # with no way out, and the first real ingest fabricated one for an undated archival photograph
    # -- a required field with no "unknown" option does not produce knowledge, it produces
    # invention. Unknown dates are recorded as such and reported by --verify, so they stay visible
    # instead of being laundered into a plausible-looking number.
    if args.observed.strip().lower() in {"unknown", "unk", "?"}:
        observed_value = "unknown"
    else:
        try:
            observed = dt.date.fromisoformat(args.observed)
        except ValueError as exc:
            raise IngestError(
                "--observed must be an ISO date such as 2024-06-11, or the literal 'unknown'. "
                "Do not guess: an invented date is worse than an absent one."
            ) from exc
        if observed > dt.date.today():
            raise IngestError(f"observation date {observed} is in the future")
        observed_value = observed.isoformat()

    digest = sha256_file(source_path)
    manifest = load_manifest()
    for existing in manifest["assets"]:
        if existing["sha256"] == digest:
            print(f"already ingested as {existing['stored_as']} (identical checksum)")
            return 0

    licence_key = args.licence.strip().lower()
    redistributable = any(licence_key.startswith(ok) for ok in REDISTRIBUTABLE)

    # Storage and display are different permissions, and conflating them is how an
    # all-rights-reserved image ends up on a public page. A viewer gallery that reads this manifest
    # must be able to tell "cite this" from "you may show this", so the answer is recorded per
    # asset rather than re-derived from the licence string by whatever consumes it later.
    #
    # SRC-005 is the case in point: HistoricBridges.org grants publication only by written Letter of
    # Agreement, per image, for "one-time, one edition use only" -- which no open repository can
    # satisfy, because anyone may fork it. Linking to the gallery is unaffected and is what this
    # project does instead.
    display_permitted = redistributable

    stored_as = None
    if redistributable:
        target_dir = KINDS[args.kind]
        if args.image_set:
            target_dir = target_dir / args.image_set
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{args.source_id}-{digest[:12]}{source_path.suffix.lower()}"
        shutil.copy2(source_path, target)
        stored_as = str(target.relative_to(REPO)).replace("\\", "/")
    else:
        print(
            f"licence {args.licence!r} is not on the redistributable list, so this file is recorded "
            "by reference and checksum but NOT copied into the repository."
        )

    asset = {
        "source_id": args.source_id,
        "kind": args.kind,
        "image_set": args.image_set,
        "coverage": args.coverage,
        "use": args.use,
        "licence": args.licence,
        "attribution": args.attribution,
        "url": args.url,
        "observed_date": observed_value,
        "retrieved_date": dt.date.today().isoformat(),
        "sha256": digest,
        "byte_size": source_path.stat().st_size,
        "original_name": source_path.name,
        "stored_copy": bool(stored_as),
        "display_permitted": display_permitted,
        "stored_as": stored_as or f"(by reference) {args.url or source_path.name}",
        "camera_metadata_available": bool(args.exif),
        "quality": args.quality,
    }
    manifest["assets"].append(asset)
    save_manifest(manifest)
    licence_record = write_licence_record(asset)

    print(f"ingested {source_path.name}")
    print(f"  source    : {asset['source_id']}  ({args.licence})")
    print(f"  observed  : {asset['observed_date']}")
    print(f"  sha256    : {digest[:16]}...")
    print(f"  stored as : {asset['stored_as']}")
    print(f"  display   : {'permitted' if display_permitted else 'NOT PERMITTED - cite by link only'}")
    print(f"  licence   : {licence_record.relative_to(REPO)}")
    print(f"  manifest  : {len(manifest['assets'])} asset(s) total")
    print()
    print(
        "Ingested, not graded. A photograph may promote a MATERIAL row and may move geometry "
        "provenance from ASSUMED to INFERRED; it may not promote a dimensional control above D on "
        "its own. See CONFIDENCE-MODEL.md section 6.2."
    )
    return 0


def verify() -> int:
    """Re-check every stored copy against its recorded checksum, and report coverage."""
    manifest = load_manifest()
    assets = manifest["assets"]

    bad = 0
    for asset in assets:
        if not asset["stored_copy"]:
            continue
        path = REPO / asset["stored_as"]
        if not path.exists():
            print(f"MISSING  {asset['stored_as']}")
            bad += 1
        elif sha256_file(path) != asset["sha256"]:
            print(f"CHANGED  {asset['stored_as']}")
            bad += 1

    covered = {a["image_set"] for a in assets if a["image_set"]}
    undated = [a for a in assets if a.get("observed_date") == "unknown"]
    restricted = [a for a in assets if not a.get("display_permitted", False)]
    print(f"{len(assets)} asset(s) ingested; {bad} problem(s)")
    if restricted:
        print(f"{len(restricted)} asset(s) may NOT be displayed, only cited by link:")
        for asset in restricted:
            print(f"  ! {asset['original_name']}  ({asset['source_id']}, {asset['licence']})")
    if undated:
        print(f"{len(undated)} asset(s) have an UNKNOWN observation date:")
        for asset in undated:
            print(f"  ? {asset['original_name']}  ({asset['source_id']})")
        print("  An undated source cannot support a claim about present condition. Date them or")
        print("  keep any derived geometry at ASSUMED; see CONFIDENCE-MODEL.md section 6.3.")
    print(f"coverage: {len(covered)} of {len(IMAGE_SETS)} image sets have at least one asset")
    for name in IMAGE_SETS:
        print(f"  [{'x' if name in covered else ' '}] {name}")
    if not assets:
        print()
        print("Nothing ingested yet, which is why the confidence C band is empty: no photographic")
        print("or photogrammetric evidence has entered the model. See CONFIDENCE-MODEL.md 6.4 for")
        print("the cheapest promotions available.")
    return 1 if bad else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--file")
    parser.add_argument("--source-id")
    parser.add_argument("--kind", choices=sorted(KINDS), default="photo")
    parser.add_argument("--licence", help='Exact licence, e.g. "CC BY-SA 4.0". Not a platform name.')
    parser.add_argument("--attribution", help="Credit line the licence requires")
    parser.add_argument("--observed", help="ISO date the image records, not the download date")
    parser.add_argument("--url", default="")
    parser.add_argument("--image-set", choices=IMAGE_SETS)
    parser.add_argument("--coverage", default="", help="What part of the structure this shows")
    parser.add_argument("--use", choices=USES, default="visual_reference")
    parser.add_argument("--quality", choices=("high", "medium", "low"), default="medium")
    parser.add_argument("--exif", action="store_true", help="Camera metadata is present")
    parser.add_argument("--verify", action="store_true", help="Re-check checksums, report coverage")
    parser.add_argument("--list-sets", action="store_true")
    args = parser.parse_args()

    if args.list_sets:
        print("Image sets (AGENT-INSTRUCTIONS.md section 8):")
        for name in IMAGE_SETS:
            print(f"  {name}")
        return 0
    if args.verify:
        return verify()

    required = ("file", "source_id", "licence", "attribution", "observed")
    missing = [f"--{name.replace('_', '-')}" for name in required if not getattr(args, name)]
    if missing:
        parser.error("missing required arguments: " + ", ".join(missing))

    try:
        return ingest(args)
    except IngestError as exc:
        print(f"refused: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
