"""Reacquire every catalogued observation for the team's 13-market churn panel.

Two paced workers; no date probing or retry after errors. Existing raw captures are
reused and verified. Failures remain in the manifest and may not become absent IDs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
CATALOG = "data/processed/inside_airbnb_city_snapshots.csv"
# Public paths documented in the same pinned team source, inside_airbnb_supply_panel.py.
MARKETS = {
    "austin": ("united-states/tx/austin", "United States", "North America"),
    "barcelona": ("spain/catalonia/barcelona", "Spain", "Europe"),
    "chicago": ("united-states/il/chicago", "United States", "North America"),
    "london": ("united-kingdom/england/london", "United Kingdom", "Europe"),
    "los-angeles": ("united-states/ca/los-angeles", "United States", "North America"),
    "mexico-city": ("mexico/df/mexico-city", "Mexico", "Latin America"),
    "nashville": ("united-states/tn/nashville", "United States", "North America"),
    "new-orleans": ("united-states/la/new-orleans", "United States", "North America"),
    "new-york-city": ("united-states/ny/new-york-city", "United States", "North America"),
    "paris": ("france/ile-de-france/paris", "France", "Europe"),
    "rome": ("italy/lazio/rome", "Italy", "Europe"),
    "san-diego": ("united-states/ca/san-diego", "United States", "North America"),
    "sydney": ("australia/nsw/sydney", "Australia", "Asia Pacific"),
}


def inspect_file(path, expected_rows):
    ids, complete, count = set(), "", 0
    required = {"id", "last_scraped", "source", "room_type", "minimum_nights", "number_of_reviews_ltm", "host_id"}
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as h:
        reader = csv.DictReader(h)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required fields")
        for r in reader:
            if not r["id"].isdigit() or r["id"] in ids:
                raise ValueError("Duplicate or invalid listing ID")
            ids.add(r["id"])
            count += 1
            complete = max(complete, r["last_scraped"][:10])
    if count != expected_rows:
        raise ValueError(f"Row count changed: {count} vs {expected_rows}")
    with path.open("rb") as h:
        digest = hashlib.file_digest(h, "sha256").hexdigest()
    return count, complete, digest


def acquire(entry, raw_dir, reuse_dir, commit):
    market, start = entry["city"], entry["dump_date"]
    name = f"{market}_{start}_listings.csv.gz"
    url = f"https://data.insideairbnb.com/{MARKETS[market][0]}/{start}/data/listings.csv.gz"
    path = raw_dir/name
    if not path.exists() and (reuse_dir/name).exists():
        path = reuse_dir/name
    result = dict(market=market, snapshot_start=start, expected_rows=int(entry["listings"]),
                  source_partial_scope=entry["partial_scope"],
                  source_partial_scope_pit=entry.get("partial_scope_pit", ""),
                  url=url, source_commit=commit, checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  status="", acquisition="", rows="", snapshot_complete="", bytes="", sha256="",
                  local_path=path.relative_to(ROOT).as_posix(), error="")
    try:
        if path.exists():
            result["acquisition"] = "reused"
        else:
            time.sleep(0.5)
            request = urllib.request.Request(url, headers={"User-Agent":"Citadel-ABNB listing-churn research"})
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
            path.write_bytes(body)
            result["acquisition"] = "downloaded"
        count, complete, digest = inspect_file(path, result["expected_rows"])
        result.update(status="ok", rows=count, snapshot_complete=complete,
                      bytes=path.stat().st_size, sha256=digest)
    except Exception as exc:
        result.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rev", required=True)
    parser.add_argument("--start", default="2025-09-01")
    parser.add_argument("--raw-dir", type=Path, default=ROOT/"data/raw/listing_churn_panel")
    parser.add_argument("--reuse-dir", type=Path, default=ROOT/"data/raw/listing_churn_execution")
    args = parser.parse_args()
    commit = subprocess.check_output(["git","rev-parse",f"{args.source_rev}^{{commit}}"],cwd=ROOT).decode().strip()
    source = subprocess.check_output(["git","show",f"{commit}:{CATALOG}"],cwd=ROOT)
    catalog = list(csv.DictReader(io.StringIO(source.decode("utf-8-sig"))))
    observed_markets = {r["city"] for r in catalog}
    if observed_markets != set(MARKETS):
        raise ValueError("Team inventory changed; review the market mapping before selection")
    selected = [r for r in catalog if r["dump_date"] >= args.start]
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    (args.raw_dir/"team_snapshot_catalog.csv").write_bytes(source)
    (args.raw_dir/"source.json").write_text(json.dumps({"source_commit":commit,
        "catalog":CATALOG,"catalog_sha256":hashlib.sha256(source).hexdigest(),
        "start":args.start,"selection":"all catalogued markets and dates on/after start",
        "expected_snapshots":len(selected),"markets":MARKETS},indent=2)+"\n",encoding="utf-8")
    print(f"Acquiring {len(selected)} snapshots across {len(observed_markets)} markets",flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(acquire,r,args.raw_dir,args.reuse_dir,commit) for r in selected]
        for job in as_completed(jobs):
            r = job.result(); results.append(r)
            with (args.raw_dir/"download_manifest.csv").open("w",newline="",encoding="utf-8") as h:
                w=csv.DictWriter(h,fieldnames=list(r)); w.writeheader()
                w.writerows(sorted(results,key=lambda x:(x["market"],x["snapshot_start"])))
            print(f"{len(results)}/{len(selected)} {r['market']} {r['snapshot_start']} {r['status']} {r['rows']} {r['error']}",flush=True)
    if any(r["status"] != "ok" for r in results):
        raise SystemExit("Acquisition gaps recorded; analysis must exclude incomplete market histories.")


if __name__ == "__main__":
    main()
