"""Acquire the public archive's September/December/March/June listing snapshots.

Dates come from Inside Airbnb's published Gatsby data, never guessed URLs. Two
paced workers, no automatic retries. Reuse and verify prior team/pilot captures.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
import re
from pathlib import Path
import time
import urllib.parse
import urllib.request

from acquire_churn_panel import ROOT
from execute_listing_churn import write_csv
from research_integrity import verify_sha256

MONTHS = ("2025-09", "2025-12", "2026-03", "2026-06")
KEEP = ("id", "host_id", "room_type", "minimum_nights", "number_of_reviews_ltm",
        "license", "latitude", "longitude", "bedrooms")


def validate_source_row(row):
    root = urllib.parse.urlsplit(row['dataRoot'])
    if root.scheme != 'https' or root.netloc != 'data.insideairbnb.com' or root.query or root.fragment:
        raise ValueError('Unexpected source domain or URL components')
    if not re.fullmatch(r'[^\W_]+(?:-[^\W_]+)*', row['link']):
        raise ValueError('Market ID must be a safe filename component')
    if date.fromisoformat(row['publishDate']).isoformat() != row['publishDate']:
        raise ValueError('Snapshot date must use YYYY-MM-DD')
    if not root.path.endswith('/') or '..' in urllib.parse.unquote(root.path).split('/'):
        raise ValueError('Invalid source path')


def select_snapshots(datasets):
    groups = defaultdict(list)
    for row in datasets:
        if not row["dataRoot"].startswith("https://data.insideairbnb.com/"):
            raise ValueError("Unexpected source domain")
        validate_source_row(row)
        groups[row["link"]].append(row)
    selected, inventory = [], []
    for market, rows in sorted(groups.items()):
        quarters = []
        for month in MONTHS:
            choices = [r for r in rows if r["publishDate"].startswith(month)]
            if choices:
                # A common month, with the last published capture in that month.
                quarters.append(max(choices, key=lambda r:r["publishDate"]))
        eligible = {r["publishDate"][:7] for r in quarters}.issuperset((MONTHS[0], MONTHS[-1]))
        inventory.append(dict(market=market, country=rows[0]["country"],
            selected_snapshots=len(quarters) if eligible else 0,
            acquisition_eligible=eligible, reason="" if eligible else "No September 2025 baseline and June 2026 endpoint"))
        if eligible:
            selected.extend(quarters)
    return selected, inventory


def inspect_capture(path, compact_path, start):
    ids, sources, dates = set(), Counter(), Counter()
    temporary = compact_path.with_suffix(".tmp")
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as h, gzip.open(temporary,"wt",encoding="utf-8",newline="") as out:
        reader=csv.DictReader(h)
        if not set(KEEP).union(("source","last_scraped")).issubset(reader.fieldnames or []):
            raise ValueError("Missing required fields")
        writer=csv.DictWriter(out,fieldnames=KEEP); writer.writeheader()
        for row in reader:
            identifier=row["id"]
            if not identifier.isdigit() or identifier in ids:
                raise ValueError("Invalid or duplicate listing ID")
            ids.add(identifier); sources[row["source"]]+=1
            dates[date.fromisoformat(row["last_scraped"][:10])]+=1
            writer.writerow({k:row[k] for k in KEEP})
    if not ids or min(dates)<date.fromisoformat(start) or (max(dates)-date.fromisoformat(start)).days>30:
        raise ValueError("Empty file or inconsistent scrape dates")
    if compact_path.exists():
        with gzip.open(temporary, 'rb') as proposed, gzip.open(compact_path, 'rb') as existing:
            if proposed.read() != existing.read():
                raise ValueError('Existing compact content differs; preserve it and use a new capture directory')
        temporary.unlink()
    else:
        temporary.replace(compact_path)
    with path.open("rb") as h: digest=hashlib.file_digest(h,"sha256").hexdigest()
    with compact_path.open("rb") as h: compact_digest=hashlib.file_digest(h,"sha256").hexdigest()
    return dict(rows=len(ids),snapshot_complete=max(dates).isoformat(),sha256=digest,
        compact_sha256=compact_digest,city_scrape=sources["city scrape"],previous_scrape=sources["previous scrape"],
        unknown_source_rows=sum(v for k,v in sources.items() if k not in ("city scrape","previous scrape")))


def acquire(row, raw_dir, prior, team_counts, team_current):
    validate_source_row(row)
    market,start=row["link"],row["publishDate"]
    url=urllib.parse.quote(row["dataRoot"]+start+"/data/listings.csv.gz",safe=":/")
    name=f"{market}_{start}_listings.csv.gz"
    path=raw_dir/name
    if not path.exists() and (market,start) in prior:
        path=ROOT/prior[(market,start)]["local_path"]
    compact=raw_dir/f"{market}_{start}_compact.csv.gz"
    team=team_counts.get((market,start),{})
    current=team_current.get(url,{})
    result=dict(market=market,country=row["country"],snapshot_start=start,url=url,
        local_path=path.relative_to(ROOT).as_posix(),compact_path=compact.relative_to(ROOT).as_posix(),
        source_partial_scope=team.get("partial_scope",""),team_historical_count=team.get("listings",""),
        team_current_count=current.get("row_count",""),team_current_sha256=current.get("sha256",""),
        checked_at_utc=datetime.now(timezone.utc).isoformat(),status="",acquisition="",rows="",
        snapshot_complete="",sha256="",compact_sha256="",bytes="",city_scrape="",previous_scrape="",unknown_source_rows="",error="")
    try:
        if path.exists():
            result["acquisition"]="reused"
            previous = prior.get((market, start))
            if previous and previous.get('sha256'):
                verify_sha256(path, previous['sha256'])
        else:
            time.sleep(.5)
            req=urllib.request.Request(url,headers={"User-Agent":"Citadel-ABNB listing-churn research"})
            with urllib.request.urlopen(req,timeout=60) as response: body=response.read()
            path.write_bytes(body); result["acquisition"]="downloaded"
        result.update(inspect_capture(path,compact,start)); result["bytes"]=path.stat().st_size
        for key in ("team_historical_count","team_current_count"):
            if result[key] and int(result[key])!=result["rows"]:
                raise ValueError(f"Count differs from {key}")
        if result["team_current_sha256"] and result["team_current_sha256"]!=result["sha256"]:
            raise ValueError("Hash differs from team's current-data manifest")
        result["status"]="ok"
    except Exception as exc:
        result.update(status="failed",error=f"{type(exc).__name__}: {exc}")
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata",type=Path,default=ROOT/"data/manifests/inside_airbnb_archive_index_2026-09-07.json")
    parser.add_argument("--raw-dir",type=Path,default=ROOT/"data/raw/listing_churn_archive")
    args=parser.parse_args(); args.raw_dir.mkdir(parents=True,exist_ok=True)
    body=args.metadata.read_bytes()
    selected,inventory=select_snapshots(json.loads(body)["data"]["allData"]["datasets"])
    (args.raw_dir/"public_archive_metadata.json").write_bytes(body)
    write_csv(args.raw_dir/"market_selection.csv",inventory)
    prior={}
    with (ROOT/"data/raw/listing_churn_panel/download_manifest.csv").open(encoding="utf-8",newline="") as h:
        for r in csv.DictReader(h):
            if r["status"]=="ok": prior[(r["market"],r["snapshot_start"])]=r
    with (ROOT/"data/raw/listing_churn_panel/team_snapshot_catalog.csv").open(encoding="utf-8-sig",newline="") as h:
        team={(r["city"],r["dump_date"]):r for r in csv.DictReader(h)}
    with (ROOT/"data/manifests/inside_airbnb_download_log.csv").open(encoding="utf-8-sig",newline="") as h:
        current={r["url"]:r for r in csv.DictReader(h) if r["kind"]=="listings" and r["classification"]=="ok"}
    source=dict(index_url="https://insideairbnb.com/get-the-data/",
        metadata_url="https://insideairbnb.com/page-data/sq/d/3008393846.json",
        metadata_sha256=hashlib.sha256(body).hexdigest(),months=MONTHS,
        selection="Last publicly indexed snapshot in each selected month; require September baseline and June endpoint",
        expected_snapshots=len(selected),catalogued_markets=len(inventory),eligible_markets=sum(r["acquisition_eligible"] for r in inventory),
        captured_at_utc=datetime.now(timezone.utc).isoformat())
    (args.raw_dir/"source.json").write_text(json.dumps(source,indent=2)+"\n",encoding="utf-8")
    print(f"Acquiring {len(selected)} snapshots across {source['eligible_markets']} markets",flush=True)
    results=[]
    # Endpoints first, then supporting history. Order does not depend on observed rates.
    selected.sort(key=lambda r:(r["publishDate"][:7] not in (MONTHS[0],MONTHS[-1]),r["link"],r["publishDate"]))
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(acquire,r,args.raw_dir,prior,team,current) for r in selected]
        for job in as_completed(jobs):
            r=job.result();results.append(r)
            write_csv(args.raw_dir/"download_manifest.csv",sorted(results,key=lambda x:(x["market"],x["snapshot_start"])))
            print(f"{len(results)}/{len(selected)} {r['market']} {r['snapshot_start']} {r['status']} {r['rows']} {r['error']}",flush=True)
    if any(r["status"]!="ok" for r in results):
        raise SystemExit("Failures recorded. Exclude incomplete histories; never interpret download failures as delisting.")


if __name__=="__main__": main()
