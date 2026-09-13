"""Rebuild K0 outputs: python analysis/src/forecast_methods/kernel_engine_v1/run.py."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import engine as E

EXPECTED = {
    "2024Q1":13.034,"2025Q1":12.325,"2026Q1":12.612,
    "2024Q2":13.449,"2025Q2":13.946,"2026Q2":13.736,
    "2023Q3":17.391,"2024Q3":17.145,"2025Q3":17.182,
    "2023Q4":11.946,"2024Q4":12.117,"2025Q4":12.026,
}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--as-of", default="2026-09-12")
    args=parser.parse_args()
    started=time.perf_counter()
    out=E.ROOT / "data/processed/forecast_methods/kernel_engine_v1"
    out.mkdir(parents=True,exist_ok=True)
    panel=E._panel(args.as_of)
    table=E.lambda_table(args.as_of,panel=panel)
    table.to_csv(out/"lambda_table.csv",index=False)
    acceptance=table[table.quarter.isin(EXPECTED)].copy()
    acceptance["expected_pct"]=acceptance.quarter.map(EXPECTED)
    acceptance["match_2dp"]=acceptance.lambda_pct.round(2)==acceptance.expected_pct.round(2)
    acceptance.to_csv(out/"acceptance.csv",index=False)
    ok=len(acceptance)==12 and bool(acceptance.match_2dp.all())
    print("acceptance test:","PASS on all 12 cells" if ok else "FAIL",flush=True)
    print(acceptance[["quarter","lambda_pct","expected_pct","match_2dp"]].to_string(index=False),flush=True)
    if not ok:
        return 2
    rows=E._lambda_rows(panel)
    loo=E._loo(rows)
    loo.to_csv(out/"loo_variant_selection.csv",index=False)
    default=E._variant(rows,None)
    print("LIVE DEFAULT",default,"(historical default selection is nested before each origin)",flush=True)
    print(loo.to_string(index=False),flush=True)
    terms=E.term_structure(args.as_of,panel=panel)
    terms.to_csv(out/f"term_structure_{args.as_of}.csv",index=False)
    print(terms[["quarter","point","guide_mid_musd","status"]].to_string(index=False),flush=True)
    chart=E.control_chart(args.as_of,panel=panel)
    chart["chart"].to_csv(out/"control_chart.csv",index=False)
    chart["alarms"].to_csv(out/"historical_false_alarms.csv",index=False)
    (out/"control_rule.json").write_text(json.dumps(chart["rule"],indent=2)+"\n",encoding="utf-8")
    q3=E.kernel_guide("2026Q3",args.as_of,panel=panel)
    pd.DataFrame([{k:v for k,v in q3.items() if not isinstance(v,(list,dict))}]).to_csv(out/"live_q3_guide.csv",index=False)
    calendar=pd.read_csv(E.ROOT/"data/processed/forecast_methods/harness/calendar.csv")
    audit=[]
    for row in calendar.itertuples():
        target=row.next_quarter_guided
        if not isinstance(target,str) or not "2023Q1"<=target<="2026Q2":
            continue
        try:
            E.kernel_forecast(target,row.guide_date,variant="last3")
            audit.append(dict(quarter=target,as_of=row.guide_date,status="available",reason=""))
        except E.DataUnavailable as exc:
            audit.append(dict(quarter=target,as_of=row.guide_date,status="refused",reason=str(exc)))
    pd.DataFrame(audit).to_csv(out/"guide_origin_availability.csv",index=False)
    elapsed=time.perf_counter()-started
    metadata=dict(as_of=args.as_of,acceptance_pass=ok,acceptance_n=12,live_default=default,
                  historical_default="nested W1 LOO within the pre-origin information set; ex_covid fallback below eight common cells",
                  run_seconds=elapsed,under_60_seconds=elapsed<60,guide_origins=len(audit),
                  guide_origins_refused=sum(x["status"]=="refused" for x in audit),
                  rnpl_scenario_available=str(E.RNPL_SCENARIO_AVAILABLE.date()),
                  frozen_files_modified=False,registered_forecasts=0)
    (out/"run_metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(metadata,indent=2),flush=True)
    return 0 if elapsed<60 else 2


if __name__=="__main__":
    raise SystemExit(main())
