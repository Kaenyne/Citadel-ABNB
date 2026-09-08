"""Reacquire the team's observed Inside Airbnb snapshots, without URL discovery.

Only catalogued dates are requested. Raw files and acquisition metadata stay in the
gitignored raw directory. Structural checks and exact source-count reconciliation
run on both newly downloaded and cached files. No access restrictions are retried.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

MARKET_PATHS = {
    "san-diego": "united-states/ca/san-diego",
    "chicago": "united-states/il/chicago",
}
CATALOG = "data/processed/inside_airbnb_city_snapshots.csv"
ROOT = Path(__file__).resolve().parents[2]
REGISTRY_URL = "https://seshat.datasd.org/stro_licenses/stro_licenses_datasd.csv"


def fetch_registry(raw_dir, registry_date):
    """Cache the current municipal register without pretending it is historical."""
    target = raw_dir / f"san_diego_stro_licenses_{registry_date}.csv"
    metadata_path = target.with_suffix(".json")
    if target.exists() and metadata_path.exists():
        body = target.read_bytes()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if hashlib.sha256(body).hexdigest() != metadata["sha256"]:
            raise ValueError("Cached municipal register checksum changed")
        print(f"Municipal register: {metadata['rows']:,} rows, verified cache")
        return
    if registry_date != datetime.now(timezone.utc).date().isoformat():
        raise ValueError("Historical register is not cached. Restore the original dated raw capture; the current URL is not a historical API.")
    with urllib.request.urlopen(REGISTRY_URL, timeout=40) as response:
        body = response.read()
    records = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig"))))
    if not records or not {"license_id", "address", "date_expiration"}.issubset(records[0]):
        raise ValueError("Unexpected municipal register schema")
    target.write_bytes(body)
    metadata_path.write_text(json.dumps({"url": REGISTRY_URL,
        "sha256": hashlib.sha256(body).hexdigest(), "rows": len(records),
        "retrieved_date": registry_date}, indent=2)+"\n", encoding="utf-8")
    print(f"Municipal register: {len(records):,} rows, downloaded")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rev", required=True)
    parser.add_argument("--markets", nargs="+", choices=MARKET_PATHS, required=True)
    parser.add_argument("--start", default="2025-09-01")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/listing_churn_execution")
    parser.add_argument("--registry-date", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "rev-parse", f"{args.source_rev}^{{commit}}"], cwd=ROOT).decode().strip()
    source = subprocess.check_output(["git", "show", f"{revision}:{CATALOG}"], cwd=ROOT)
    catalog = list(csv.DictReader(io.StringIO(source.decode("utf-8-sig"))))
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    (args.raw_dir / "team_snapshot_catalog.csv").write_bytes(source)
    (args.raw_dir / "team_source.json").write_text(json.dumps({
        "commit": revision, "catalog_path": CATALOG, "catalog_sha256": hashlib.sha256(source).hexdigest(),
        "markets": args.markets, "start": args.start,
    }, indent=2) + "\n", encoding="utf-8")
    log = []
    for entry in catalog:
        market, snapshot = entry["city"], entry["dump_date"]
        if market not in args.markets or snapshot < args.start:
            continue
        url = f"https://data.insideairbnb.com/{MARKET_PATHS[market]}/{snapshot}/data/listings.csv.gz"
        target = args.raw_dir / f"{market}_{snapshot}_listings.csv.gz"
        item = {"market": market, "snapshot_date": snapshot, "url": url,
                "expected_rows": int(entry["listings"]), "source_partial_scope": entry["partial_scope"],
                "checked_at_utc": datetime.now(timezone.utc).isoformat(), "status": "", "rows": None,
                "bytes": None, "sha256": None, "source_commit": revision, "error": ""}
        try:
            if target.exists():
                body = target.read_bytes()
                acquisition = "cached"
            else:
                request = urllib.request.Request(url, headers={"User-Agent": "Citadel-ABNB listing-churn research"})
                with urllib.request.urlopen(request, timeout=40) as response:
                    body = response.read()
                acquisition = "downloaded"
                time.sleep(0.5)
            if len(body) < 2048:
                raise ValueError("Unexpectedly small gzip response")
            records = list(csv.DictReader(io.StringIO(gzip.decompress(body).decode("utf-8-sig"))))
            if not records or not {"id", "name", "last_scraped", "latitude", "longitude", "license"}.issubset(records[0]):
                raise ValueError("Required listing fields missing")
            identifiers = [r["id"] for r in records]
            if any(not identifier.isdigit() for identifier in identifiers) or len(set(identifiers)) != len(identifiers):
                raise ValueError("Invalid or duplicate listing IDs")
            if len(records) != item["expected_rows"]:
                raise ValueError(f"Source changed: expected {item['expected_rows']} rows, found {len(records)}")
            item.update(status="ok", rows=len(records), bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            if acquisition == "downloaded":
                target.write_bytes(body)
            print(f"{market} {snapshot}: {len(records):,} rows, {acquisition}, source-count match", flush=True)
        except urllib.error.HTTPError as error:
            item.update(status=f"http_{error.code}", error=str(error))
            print(f"{market} {snapshot}: HTTP {error.code}; no retry", flush=True)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
            item.update(status="failed", error=str(error))
            print(f"{market} {snapshot}: {error}", flush=True)
        log.append(item)
        with (args.raw_dir / "download_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(item))
            writer.writeheader()
            writer.writerows(log)
    if not log or any(r["status"] != "ok" for r in log):
        raise SystemExit("One or more requested snapshots are unavailable; inspect the manifest before cohort selection.")
    if "san-diego" in args.markets:
        fetch_registry(args.raw_dir, args.registry_date)


if __name__ == "__main__":
    main()
