"""Paginated pull of the NCLH sales_estimate table from DoltHub for WP-E1 (G1b step 9).

    python analysis/src/forecast_methods/L0_dolthub_v2/nclh_pull.py

Keyless GET, 500 rows per page, 60 s between calls, stop on 403 or an empty page. Writes
data/processed/forecast_methods/L0_dolthub_v2/dolthub_sales_estimate_NCLH.csv and a small
.json log. NCLH is NOT appended to the register (the register is ABNB-only).
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUT_DIR = REPO / "data/processed/forecast_methods/L0_dolthub_v2"
OUT = OUT_DIR / "dolthub_sales_estimate_NCLH.csv"
LOG = OUT_DIR / "dolthub_sales_estimate_NCLH.pull_log.json"
API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/earnings/master"
PAGE, SPACING_S, MAX_PAGES = 500, 60, 12


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames, log = [], []
    for i in range(MAX_PAGES):
        if i:
            time.sleep(SPACING_S)
        off = i * PAGE
        sql = f"select * from sales_estimate where act_symbol='NCLH' order by date, period limit {PAGE} offset {off}"
        p = subprocess.run(["curl", "-sL", "-G", "--max-time", "90", "-w", "\n%{http_code}",
                            "--data-urlencode", f"q={sql}", API], capture_output=True, text=True, timeout=120)
        body, _, code = p.stdout.rpartition("\n")
        entry = {"offset": off, "http": code, "at": dt.datetime.now().isoformat(timespec="seconds")}
        try:
            js = json.loads(body) if body else {}
        except json.JSONDecodeError:
            js = {}
            entry["raw_head"] = body[:200]
        rows = js.get("rows", []) if isinstance(js, dict) else []
        entry["status"] = js.get("query_execution_status") if isinstance(js, dict) else None
        entry["message"] = js.get("query_execution_message") if isinstance(js, dict) else None
        entry["n_rows"] = len(rows)
        log.append(entry)
        print(f"offset {off}: http={code} status={entry['status']} rows={len(rows)}", file=sys.stderr)
        if code == "403":
            entry["stop"] = "403 rate limit"
            break
        if code != "200" or entry["status"] not in ("Success", "RowLimit"):
            entry["stop"] = "query failed"
            break
        if rows:
            frames.append(pd.DataFrame(rows))
        if len(rows) < PAGE:
            entry["stop"] = "last page"
            break
    if frames:
        df = pd.concat(frames, ignore_index=True).drop_duplicates()
        df.to_csv(OUT, index=False)
        print(f"NCLH: {len(df)} rows, {df['date'].min()}..{df['date'].max()} -> {OUT}", file=sys.stderr)
    LOG.write_text(json.dumps({"pages": log, "rows_written": int(sum(len(f) for f in frames)),
                               "finished": dt.datetime.now().isoformat(timespec="seconds")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
