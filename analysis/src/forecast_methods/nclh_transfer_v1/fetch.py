"""Public issuer release extraction; raw HTML remains in a temporary cache."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[4]
INDEX = "https://www.nclhltd.com/investors/financial-information/financial-results"
INPUT = ROOT / "data/processed/forecast_methods/nclh_transfer_v1/inputs_v3"
CACHE = Path(tempfile.gettempdir()) / "citadel_nclh_transfer_v1_public_cache"


def retrieve(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    path = CACHE / f"{key}.html"
    meta = CACHE / f"{key}.json"
    if path.exists() and meta.exists():
        return path.read_bytes(), json.loads(meta.read_text())
    response = requests.get(url, headers={"User-Agent": "University equity research data audit"}, timeout=45)
    response.raise_for_status()
    raw = response.content
    metadata = {"source_url": url, "resolved_url": response.url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    path.write_bytes(raw)
    meta.write_text(json.dumps(metadata, indent=2))
    time.sleep(0.2)
    return raw, metadata


def row_parts(tr):
    cells = [re.sub(r"\s+", " ", x.get_text(" ", strip=True)).strip() for x in tr.find_all(["td", "th"], recursive=False)]
    cells = [x for x in cells if x]
    if not cells:
        return "", [], ""
    label = re.sub(r"\s*\(\d+\)$", "", cells[0]).strip()
    nums = re.findall(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?", " ".join(cells[1:]))
    return label, [float(x.replace(",", "")) for x in nums], " | ".join(cells)


def publication(soup):
    stamp = soup.select_one("time[datetime].date")
    if stamp is None:
        raise ValueError("No issuer publication timestamp")
    value, printed = stamp["datetime"], stamp.get_text(" ", strip=True)
    if "T" in value and ("EDT" in printed or "EST" in printed):
        return value + ("-04:00" if "EDT" in printed else "-05:00"), "issuer_clock_timezone", printed
    # Conservative date-only cutoff; no invented intraday knowledge.
    day = value[:10]
    # UTC next-day 04:59:59 is conservatively no earlier than NY end-of-day year-round.
    ts = pd.Timestamp(day, tz="UTC") + pd.Timedelta(days=1, hours=4, minutes=59, seconds=59)
    return ts.isoformat(), "date_only_conservative_nextday_045959_utc", printed


def parse_release(raw, quarter, metadata):
    soup = BeautifulSoup(raw, "html.parser")
    published, precision, display = publication(soup)
    observations, candidates = {}, []
    patterns = {
        "passenger_ticket_revenue_usd_m": r"passenger ticket(?: revenue)?",
        "onboard_other_revenue_usd_m": r"onboard and other(?: revenue)?",
        "total_revenue_usd_m": r"total revenues?",
        "advance_ticket_sales_current_usd_m": r"advance ticket sales",
        "capacity_days": r"capacity days",
        "occupancy_pct": r"occupancy(?: percentage)?",
        "net_yield_usd_per_capacity_day": r"net yield",
    }
    for tr in soup.select("tr"):
        label, nums, row = row_parts(tr)
        for metric, pattern in patterns.items():
            if not re.fullmatch(pattern, label, flags=re.I) or not nums:
                continue
            candidates.append({"quarter": quarter, "metric": metric, "row": row,
                               "source_url": metadata["source_url"]})
            # Exact primary current-quarter row. Revenue/deposits expressed in thousands.
            # Suspended-sailing KPI tables leave current cells blank. Never take a
            # later comparative cell as the current period during these excluded years.
            if quarter[:4] in ("2020", "2021") and not metric.endswith("usd_m"):
                continue
            if metric == "capacity_days" and (nums[0] < 100_000 or "million" in row.lower()):
                continue
            if metric == "occupancy_pct" and label.lower() != "occupancy percentage":
                continue
            if metric == "net_yield_usd_per_capacity_day" and (nums[0] < 10 or "$" not in row or "%" in row or "~" in row):
                continue
            if metric not in observations:
                observations[metric] = {"quarter": quarter, "metric": metric,
                    "value": nums[0] / 1000 if metric.endswith("usd_m") else nums[0],
                    "units": "USD million" if metric.endswith("usd_m") else ("percent" if metric == "occupancy_pct" else "days" if metric == "capacity_days" else "USD per capacity day"),
                    "published_at": published, "timestamp_precision": precision,
                    "publication_display": display, "source_reference": metadata["source_url"],
                    "source_sha256": metadata["sha256"], "retrieved_at": metadata["retrieved_at"],
                    "source_row": row, "column_selection": "first numeric value in current-quarter row", "evidence_status": "original_quarter_issuer_release_retrieved_2026"}
    guide_rows = []
    # Retain short matched-metric inventory, not the full copyrighted release text.
    for c in candidates:
        if c["metric"] == "net_yield_usd_per_capacity_day" and "%" in c["row"]:
            guide_rows.append(c["row"])
    inventory = {"quarter_printed": quarter, "published_at": published,
        "source_reference": metadata["source_url"],
        "guidance_metric_observed": "net_yield_or_eps_cost_ebitda; requires metric match",
        "gaap_revenue_guide_available": False,
        "matched_consensus_available": False,
        "status": "not_comparable_to_GAAP_revenue_kernel",
        "guide_table_rows": " || ".join(guide_rows[:2])}
    return list(observations.values()), candidates, inventory


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=INPUT)
    args = p.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        raise FileExistsError("Input snapshot is immutable; choose a NEW --out directory")
    raw, metadata = retrieve(INDEX)
    soup = BeautifulSoup(raw, "html.parser")
    urls = {}
    for h in soup.select("h3"):
        m = re.fullmatch(r"(?:Q([1-4])|FY) (20\d\d)", h.get_text(strip=True))
        if not m:
            continue
        q = f"{m[2]}Q{m[1] or '4'}"
        if not "2015Q1" <= q <= "2026Q2":
            continue
        row = h.find_parent("div", class_="row")
        links = row.select("a[href]") if row else []
        url = next((x["href"].rstrip("/") for x in links if "press-releases/detail/" in x["href"]), None)
        if url:
            urls[q] = urljoin(INDEX, url)
    all_obs, all_candidates, manifest, inventories, errors = [], [], [metadata], [], []
    for quarter, url in sorted(urls.items()):
        try:
            raw, meta = retrieve(url)
            obs, candidates, inv = parse_release(raw, quarter, meta)
            all_obs.extend(obs)
            all_candidates.extend(candidates)
            inventories.append(inv)
            manifest.append({"quarter": quarter, **meta})
            print(quarter, len(obs), flush=True)
        except (requests.RequestException, ValueError) as e:
            errors.append({"quarter": quarter, "source_url": url, "error": str(e)})
            print(quarter, "ERROR", str(e), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_obs).to_csv(args.out / "observations.csv", index=False)
    pd.DataFrame(all_candidates).to_csv(args.out / "extraction_candidates.csv", index=False)
    pd.DataFrame(inventories).to_csv(args.out / "guidance_inventory.csv", index=False)
    (args.out / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.out / "fetch_errors.json").write_text(json.dumps(errors, indent=2) + "\n")
    print(json.dumps({"quarters_discovered": len(urls), "observations": len(all_obs), "errors": len(errors)}))


if __name__ == "__main__":
    main()
