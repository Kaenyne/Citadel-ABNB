"""T0 provenance check for G1b: is the DoltHub post-no-preference/earnings history immutable?

Runs at most 8 keyless GETs against the DoltHub SQL API, 10 s apart, via curl -sL -G
--data-urlencode (the API returned 403 after ~40 requests in 20 minutes on 14 Sep 2026).

    python analysis/src/forecast_methods/L0_dolthub_v2/t0_provenance.py

Writes data/processed/forecast_methods/L0_dolthub_v2/t0_provenance.json (every query, every
raw response, the comparison) and prints a verdict: PASS (history immutable), FAIL (an AS OF row
differs from the current row) or NOT_RUN (API unreachable / 403 / timeout before completion).
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
SAMPLE = (REPO / "data/processed/github_altdata/samples/"
          "dolthub-post-no-preference-earnings-consensus-vintages/sales_estimate_ABNB_BKNG_EXPE.csv")
OUT_DIR = REPO / "data/processed/forecast_methods/L0_dolthub_v2"
OUT = OUT_DIR / "t0_provenance.json"

API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/earnings/master"
SPACING_S = 10
MAX_REQUESTS = 12
SNAPSHOTS = ["2022-08-07", "2024-02-11", "2025-08-03"]
COMPARE_COLS = ["consensus", "count", "high", "low"]

_n_requests = 0


def query(sql: str, log: list) -> dict | None:
    """One curl GET. Returns the parsed JSON or None; records everything in `log`."""
    global _n_requests
    if _n_requests >= MAX_REQUESTS:
        log.append({"sql": sql, "skipped": "request budget exhausted"})
        return None
    if _n_requests > 0:
        time.sleep(SPACING_S)
    _n_requests += 1
    cmd = ["curl", "-sL", "-G", "--max-time", "60", "-w", "\n%{http_code}",
           "--data-urlencode", f"q={sql}", API]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        body, _, code = p.stdout.rpartition("\n")
    except subprocess.TimeoutExpired:
        body, code = "", "timeout"
    entry = {"n": _n_requests, "sql": sql, "http": code, "seconds": round(time.time() - t0, 1),
             "at": dt.datetime.now().isoformat(timespec="seconds")}
    try:
        js = json.loads(body) if body else None
    except json.JSONDecodeError:
        js = None
        entry["raw_head"] = body[:300]
    entry["response"] = js
    log.append(entry)
    print(f"[{_n_requests}] http={code} {entry['seconds']}s :: {sql[:90]}", file=sys.stderr)
    if js is None or code != "200" or js.get("query_execution_status") not in ("Success", "RowLimit"):
        return None
    return js


def main() -> int:
    """Attempt 1 (default): 8 requests. dolt_log head/tail, then per snapshot the FIRST commit
    within 14 days after the snapshot date and an AS OF query at it.

    Attempt 2 (--by-message): 4 requests, run after attempt 1 returned zero AS OF rows because
    every DoltHub day carries four commits seconds apart (rank_score, eps_estimate,
    sales_estimate, eps_history) and the first commit of the day predates that day's
    sales_estimate commit. One dolt_log query filtered on the commit message
    'sales_estimate <snapshot> update' returns all three hashes, then three AS OF queries.
    Attempt 1 + attempt 2 = 12 requests, the pre-registered cap.
    """
    by_message = "--by-message" in sys.argv
    out = OUT_DIR / ("t0_provenance_attempt2.json" if by_message else "t0_provenance.json")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log: list = []
    result = {"api": API, "attempt": 2 if by_message else 1,
              "started": dt.datetime.now().isoformat(timespec="seconds"),
              "queries": log, "snapshot_checks": [], "verdict": "NOT_RUN"}

    commits_by_msg = {}
    if by_message:
        likes = " or ".join(f"message like 'sales_estimate {s} update%'" for s in SNAPSHOTS)
        c = query(f"select commit_hash, date, message from dolt_log where {likes} order by date", log)
        for r in (c or {}).get("rows", []):
            for s in SNAPSHOTS:
                if r["message"].startswith(f"sales_estimate {s} update"):
                    commits_by_msg[s] = r
    else:
        latest = query("select commit_hash, committer, date, message from dolt_log order by date desc limit 5", log)
        earliest = query("select commit_hash, committer, date, message from dolt_log order by date asc limit 3", log)
        result["dolt_log_latest"] = latest["rows"] if latest else None
        result["dolt_log_earliest"] = earliest["rows"] if earliest else None

    sample = pd.read_csv(SAMPLE)
    sample = sample[sample["act_symbol"] == "ABNB"]

    all_ok, any_ran = True, False
    for snap in SNAPSHOTS:
        hi = (dt.date.fromisoformat(snap) + dt.timedelta(days=14)).isoformat()
        if by_message:
            c = {"rows": [commits_by_msg[snap]]} if snap in commits_by_msg else None
        else:
            c = query(f"select commit_hash, date from dolt_log where date between '{snap}' and '{hi} 23:59:59' "
                      f"order by date limit 1", log)
        check = {"snapshot": snap, "commit": None, "commit_date": None, "rows_as_of": None,
                 "rows_current": None, "match": None}
        if c and c.get("rows"):
            check["commit"] = c["rows"][0]["commit_hash"]
            check["commit_date"] = c["rows"][0]["date"]
            check["commit_message"] = c["rows"][0].get("message")
            asof = query(f"select * from sales_estimate as of '{check['commit']}' "
                         f"where act_symbol = 'ABNB' and date = '{snap}'", log)
            if asof is not None:
                any_ran = True
                rows_asof = asof.get("rows", [])
                cur = sample[sample["date"] == snap]
                check["rows_as_of"] = rows_asof
                check["rows_current"] = cur.to_dict("records")
                # compare per (period, period_end_date)
                ok = len(rows_asof) == len(cur) and len(cur) > 0
                diffs = []
                for r in rows_asof:
                    m = cur[(cur["period"] == r["period"]) & (cur["period_end_date"] == r["period_end_date"])]
                    if len(m) != 1:
                        ok = False
                        diffs.append({"period": r["period"], "issue": "no matching current row"})
                        continue
                    for col in COMPARE_COLS:
                        a = r.get(col)
                        b = m[col].iloc[0]
                        a_f = None if a in (None, "") else float(a)
                        b_f = None if pd.isna(b) else float(b)
                        if a_f != b_f:
                            ok = False
                            diffs.append({"period": r["period"], "col": col, "as_of": a_f, "current": b_f})
                check["diffs"] = diffs
                check["match"] = ok
                all_ok &= ok
            else:
                all_ok = False
        else:
            all_ok = False
        result["snapshot_checks"].append(check)

    ran = [c for c in result["snapshot_checks"] if c["match"] is not None]
    if len(ran) == len(SNAPSHOTS) and all(c["match"] for c in ran):
        result["verdict"] = "PASS"
    elif any(c["match"] is False for c in ran):
        result["verdict"] = "FAIL"
    else:
        result["verdict"] = "NOT_RUN" if not ran else "PARTIAL"
    result["n_requests"] = _n_requests
    result["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    out.write_text(json.dumps(result, indent=1, default=str))
    print(f"T0 verdict: {result['verdict']} ({len(ran)}/{len(SNAPSHOTS)} snapshot checks ran, "
          f"{_n_requests} requests) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
