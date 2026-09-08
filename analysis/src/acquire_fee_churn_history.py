"""Extend existing churn captures for fee-event timing, using documented dates only.

Select every indexed observation for markets with both Oct/Nov 2025 history, and
the team's pre-Sep-2025 catalog from Sep 2024 onward. Reuse verified captures;
single attempts for missing files, with failures retained as missing observations.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
from pathlib import Path

from acquire_churn_archive import ROOT, acquire


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    raw = ROOT / "data/raw/fee_churn_history"
    raw.mkdir(parents=True, exist_ok=True)
    index = json.loads((ROOT / "data/manifests/inside_airbnb_archive_index_2026-09-07.json").read_text(encoding="utf-8"))["data"]["allData"]["datasets"]
    monthly = set(r["link"] for r in index if r["publishDate"].startswith("2025-10")) & set(r["link"] for r in index if r["publishDate"].startswith("2025-11"))
    selected = {(r["link"], r["publishDate"]): r for r in index if r["link"] in monthly}
    catalog = read(ROOT / "data/raw/listing_churn_panel/team_snapshot_catalog.csv")
    paths = json.loads((ROOT / "data/raw/listing_churn_panel/source.json").read_text(encoding="utf-8"))["markets"]
    for row in catalog:
        if "2024-09-01" <= row["dump_date"] < "2025-09-01":
            market = row["city"]
            selected[(market, row["dump_date"])] = dict(link=market, publishDate=row["dump_date"],
                country=paths[market][1], dataRoot="https://data.insideairbnb.com/" + paths[market][0] + "/")
    prior = {}
    failures = {}
    for name in ("listing_churn_panel", "listing_churn_archive", "fee_churn_history"):
        path = ROOT / f"data/raw/{name}/download_manifest.csv"
        if path.exists():
            for row in read(path):
                if row["status"] == "ok":
                    prior[(row["market"], row["snapshot_start"])] = row
                elif name == "fee_churn_history":
                    failures[(row["market"], row["snapshot_start"])] = row
    counts = {(r["city"], r["dump_date"]): r for r in catalog}
    current = {r["url"]: r for r in read(ROOT / "data/manifests/inside_airbnb_download_log.csv") if r["kind"] == "listings" and r["http_status"] == "200"}
    (raw / "selection.json").write_text(json.dumps(dict(
        source_commit="df833f5f3980078beef09c1327940bfa58d57acf",
        selection="All public-index dates in markets with October and November 2025; plus team catalog September 2024 to August 2025",
        monthly_markets=sorted(monthly), selected_snapshots=len(selected),
        selected_dates=[dict(market=k[0], date=k[1]) for k in sorted(selected)]), indent=2), encoding="utf-8")
    results = [row for key, row in failures.items() if key in selected]
    print(f"Selected {len(selected)} snapshots; {len(monthly)} monthly markets", flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(acquire, row, raw, prior, counts, current) for key, row in sorted(selected.items()) if key not in failures]
        for job in as_completed(jobs):
            row = job.result()
            results.append(row)
            with (raw / "download_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row))
                writer.writeheader()
                writer.writerows(sorted(results, key=lambda r: (r["market"], r["snapshot_start"])))
            print(f"{len(results)}/{len(selected)} {row['market']} {row['snapshot_start']} {row['status']} {row['acquisition']} {row['error']}", flush=True)
    print("Failures remain unknown; measurement must exclude failed/flagged pairs.", flush=True)


if __name__ == "__main__":
    main()
