"""Read-only source inventory; writes a NEW receipt directory, never source inputs.

python analysis/src/forecast_methods/gbv_event_v1/sources/run.py --name run_v1 --probe-yahoo
The optional public probe makes one request for ABNB, then QQQ only if ABNB succeeds.
No credentials, retries, package installation, forecast fitting, or registration.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data/processed/forecast_methods/gbv_event_v1/sources_v1"
INPUTS = [
    "docs/revenue-forecast-strategy/05_backtests/GE_PREREG_v1.md",
    "docs/thesis-kernel-topdown/lane2/CONVENTION.md",
    "data/processed/forecast_methods/returns_v1/ohlc_daily.csv",
    "data/processed/forecast_methods/returns_v1/manifest.json",
    "data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv",
    "data/processed/overnight/20_prices_ohlc.csv",
    "data/processed/abnb_earnings_reactions.csv",
    "data/processed/peer_readthrough/05_t1_gap_vs_intraday.csv",
    "data/processed/forecast_methods/harness/calendar.csv",
    "data/processed/forecast_methods/L0/L0_vintage_register.csv",
    "data/processed/forecast_methods/l3_source_contract_v1/precision/results_v2/source_manifest.csv",
    "data/processed/forecast_methods/consensus_stamp_v2/capture_20260913T152058Z/yfinance_revenue_estimate.csv",
    "data/processed/forecast_methods/consensus_stamp_v2/stockanalysis_web_capture.json",
    "research/notes/github_altdata/catalog.csv",
    "docs/revenue-forecast-strategy/05_backtests/G1b_dolthub_consensus_history.md",
    "docs/revenue-forecast-strategy/05_backtests/M_CONSENSUS_2026-09-13.md",
]

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))

def write_csv(path, records):
    if not records:
        path.write_text("", encoding="utf-8")
        return
    with path.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

def family(vendor):
    if any(t in vendor.lower() for t in ("zacks", "dolthub")):
        return "Zacks family; DoltHub is a mirror, not independent"
    if any(t in vendor.lower() for t in ("yahoo", "alpha vantage", "lseg", "refinitiv")):
        return "LSEG/Refinitiv family; distribution channels not independent"
    if "S&P" in vendor:
        return "S&P stated family; not independently refreshed quarterly on Sep13"
    return "Other / not promoted"

def probe(out):
    attempts = []
    start = int(dt.datetime(2026, 8, 6, tzinfo=dt.timezone.utc).timestamp())
    end = int(dt.datetime(2026, 8, 8, tzinfo=dt.timezone.utc).timestamp())
    for ticker in ("ABNB", "QQQ"):
        query = urllib.parse.urlencode(dict(period1=start, period2=end, interval="5m", includePrePost="true", events="history"))
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?{query}"
        a = dict(ticker=ticker, url=url, retrieved_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(), status="", error="", bars=0)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Python-urllib/source-inventory"})
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = response.read()
                a["http_status"] = response.status
            doc = json.loads(raw)
            if doc["chart"].get("error"):
                raise ValueError(str(doc["chart"]["error"]))
            result = doc["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            q = result["indicators"]["quote"][0]
            records = []
            for i, stamp in enumerate(timestamps):
                records.append(dict(ticker=ticker, timestamp_utc=dt.datetime.fromtimestamp(stamp, dt.timezone.utc).isoformat(), **{k:q.get(k, [None]*len(timestamps))[i] for k in ("open", "high", "low", "close", "volume")}))
            if not records:
                raise ValueError("No timestamped bars in response")
            (out / f"{ticker}_yahoo_5m_response.json").write_bytes(raw)
            write_csv(out / f"{ticker}_yahoo_5m.csv", records)
            a.update(status="available_recent_event_only_unvalidated", bars=len(records), source_timezone=result.get("meta", {}).get("exchangeTimezoneName"), source_interval=result.get("meta", {}).get("dataGranularity"), response_sha256=hashlib.sha256(raw).hexdigest())
        except Exception as exc:
            # Error class and server reason only; this public URL has no credential.
            a.update(status="unavailable_one_bounded_attempt", error=f"{type(exc).__name__}: {exc}")
        attempts.append(a)
        if a["status"].startswith("unavailable"):
            break
    return attempts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--probe-yahoo", action="store_true")
    args = parser.parse_args()
    if not args.name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("name must be a simple new directory name")
    out = BASE / args.name
    out.mkdir(parents=True, exist_ok=False)
    manifest = []
    for relative in INPUTS:
        p = ROOT / relative
        manifest.append(dict(path=relative, exists=p.is_file(), bytes=p.stat().st_size if p.is_file() else None, sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None))
    write_csv(out / "input_manifest.csv", manifest)

    price_inventory = []
    for relative in INPUTS[2:8]:
        p = ROOT / relative
        if p.suffix != ".csv":
            continue
        r = rows(p)
        date_col = next(k for k in ("date", "event_date", "reaction_date") if k in r[0])
        dates = [x.get(date_col, "") for x in r]
        price_inventory.append(dict(path=relative, rows=len(r), columns="|".join(r[0]), first_date=min(dates), last_date=max(dates), actual_timestamped_intraday=False, admissible_use="daily OHLC or derived event returns; cannot identify call-only leg"))
    write_csv(out / "held_price_inventory.csv", price_inventory)

    l0 = rows(ROOT / INPUTS[9])
    primary = [r for r in l0 if r.get("role") == "pre_guide" and r.get("metric") == "revenue"]
    write_csv(out / "historical_primary_expectation_inventory.csv", primary)
    selected = {}
    for r in l0:
        if r.get("metric") != "revenue" or r.get("period") not in ("2026Q3", "2026Q4", "2027Q1", "2027Q2"):
            continue
        if r.get("role") not in ("current", "pit_history"):
            continue
        key = (r["vendor"], r["period"])
        if key not in selected or r["as_of_timestamp"] > selected[key]["as_of_timestamp"]:
            selected[key] = r
    current = []
    for key, r in sorted(selected.items()):
        current.append({**r, "source_family": family(r["vendor"]), "expectation_object": "realized-quarter revenue, not observed guide midpoint expectation", "current_at_audit": "dated retained value; no fresh estimate pull in this audit"})
    write_csv(out / "dated_current_expectation_inventory.csv", current)

    cal = [r for r in rows(ROOT / INPUTS[8]) if r["print_date_basis"] == "ledger" and r["letter_date"]]
    timing = []
    for r in cal:
        timing.append(dict(print_quarter=r["print_quarter"], letter_date=r["letter_date"], reaction_date=r["reaction_date"], release_date_basis=r["print_date_basis"], release_clock="not independently established in this audit", call_start_clock="17:00 America/New_York; primary verified" if r["print_quarter"] in ("2025Q3", "2026Q1", "2026Q2") else "not independently established in this audit", call_end_clock="unavailable", timestamped_intraday_held=False))
    write_csv(out / "event_timing_inventory.csv", timing)
    candidates = []
    for r in rows(ROOT / INPUTS[13]):
        txt = " ".join(str(v) for v in r.values()).lower()
        if "intraday" in txt and any(t in txt for t in ("price", "stock", "equity", "earnings")):
            candidates.append(r)
    write_csv(out / "catalogue_intraday_candidates.csv", candidates)
    attempts = probe(out) if args.probe_yahoo else []
    receipt = dict(created_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(), l0_rows=len(l0), dolthub_rows=sum("DoltHub" in r["vendor"] for r in l0), original_pre_guide_rows=len(primary), original_pre_guide_admissible_attributed=sum(r["pit_usable"].lower()=="true" and r["vendor_attributed"].lower()=="true" and bool(r["value"]) for r in primary), current_expected_periods_present=sorted(set(r["period"] for r in current if r["pit_usable"].lower()=="true")), direct_guide_expectation_rows=sum("guide" in r.get("metric", "").lower() for r in l0), historical_events=len(cal), held_timestamped_intraday_events=0, catalogue_intraday_candidate_rows=len(candidates), public_probe_attempts=attempts, scope="Structured source inventory only; no model fit, strategy test, registry, scorer, or original source mutation.", limits="Daily gaps include release, call, overnight and premarket news. Public availability at a source date is not an exact release timestamp. No calibrated inference from source rounding or displayed precision.")
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    print(f"OUTPUT={out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
