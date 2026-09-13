"""Rebuild this run's reviewed candidates from immutable public capture facts."""
from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/consensus_stamp_v2"
CAPTURE = OUT / "capture_20260913T152058Z"


def build() -> list[dict]:
    # Explicit mapping for the 13 September 2026 snapshot. Yahoo's year-ago
    # revenues 4,095M / 2,778M / 12,241M corroborate Q3 / Q4 / FY2025.
    mapping = {"0q": "2026Q3", "+1q": "2026Q4", "0y": "FY2026", "+1y": "FY2027"}
    rows = []
    for attribute, metric, divisor, unit in (("revenue", "revenue", Decimal(1000000), "musd"), ("earnings", "eps_estimate", Decimal(1), "usd")):
        source = CAPTURE / f"yfinance_{attribute}_estimate.csv"
        for observation in csv.DictReader(source.open(encoding="utf-8")):
            period = mapping[observation["period"]]
            low = float(Decimal(observation["low"]) / divisor)
            high = float(Decimal(observation["high"]) / divisor)
            method = f"yfinance.Ticker(ABNB).{attribute}_estimate"
            basis = "EPS basis unspecified in returned table; registered as eps_estimate, not asserted to be adjusted EPS." if metric == "eps_estimate" else "USD source converted to USD millions exactly."
            rows.append({
                "register_id": f"CU-{period}-{metric}-Yahoo-20260913T1520Z",
                "vendor": "Yahoo Finance (LSEG family)", "period": period, "metric": metric,
                "value": float(Decimal(observation["avg"]) / divisor), "unit": unit,
                "n_estimates": int(observation["numberOfAnalysts"]), "as_of_timestamp": "2026-09-13T15:20Z",
                "url": "https://finance.yahoo.com/quote/ABNB/analysis/", "source_path": source.relative_to(ROOT).as_posix(),
                "role": "current", "pit_usable": True, "vendor_attributed": True,
                "note": f"capture_method={method}; captured_utc=2026-09-13T15:20:58Z; source_period={observation['period']}; high={high}; low={low}; same LSEG-family panel as Alpha Vantage, count once. {basis}",
                "capture_method": method, "high": high, "low": low,
                "n_basis": "metric-specific numberOfAnalysts from Yahoo table",
                "vendor_publication_timestamp": None,
            })
    source = OUT / "stockanalysis_web_capture.json"
    capture = json.loads(source.read_text(encoding="utf-8"))
    for observation in capture["observations"]:
        if not observation["admitted"]:
            continue
        period, metric = observation["period"], observation["metric"]
        rows.append({
            "register_id": f"CU-{period}-{metric}-SPGlobal-20260913T1523Z",
            "vendor": capture["vendor"], "period": period, "metric": metric,
            "value": observation["value"], "unit": observation["unit"], "n_estimates": observation["n_estimates"],
            "as_of_timestamp": "2026-09-13T15:23Z", "url": capture["url"], "source_path": source.relative_to(ROOT).as_posix(),
            "role": "current", "pit_usable": True, "vendor_attributed": True,
            "note": f"capture_method=web.run public page text; observation recorded 2026-09-13T15:23Z; vendor_last_updated=2026-09-10; annual financial forecast table; high={observation['high']}; low={observation['low']}; n=43 is the displayed FY2026 panel count, not an independently disclosed metric-specific count. No new vendor publication is inferred from the recapture.",
            "capture_method": capture["capture_method"], "high": observation["high"], "low": observation["low"],
            "n_basis": observation["n_basis"], "vendor_publication_timestamp": "2026-09-10",
        })
    return rows


if __name__ == "__main__":
    candidates = OUT / "candidates_20260913.json"
    content = json.dumps(build(), indent=2) + "\n"
    if candidates.exists():
        assert candidates.read_text(encoding="utf-8") == content, "Immutable candidates differ"
        print("Candidate reproduction PASS: 10 rows; no file changed")
    else:
        with candidates.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)
        print("Prepared 10 reviewed candidate rows; register unchanged")
