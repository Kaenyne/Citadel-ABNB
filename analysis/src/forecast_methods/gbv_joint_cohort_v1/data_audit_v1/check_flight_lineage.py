"""Verify stored PR60 flight vintage lineage, not missing original git blobs."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/flight_lineage_v1")
    out = parser.parse_args().out.resolve()
    if out.exists():
        raise FileExistsError(f"Choose a NEW output directory: {out}")
    rels = ["data/processed/govdata_v2/"+name for name in ["qtd75_pit.csv", "git_commits.csv", "revision_check.csv", "revision_summary.csv", "C_feature_panel.csv"]]
    rels += ["analysis/src/govdata_v2/C2_vintages.py"]
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in rels}
    pit = pd.read_csv(ROOT/rels[0])
    commits = pd.read_csv(ROOT/rels[1])
    revisions = pd.read_csv(ROOT/rels[2])
    rows = []
    for r in pit.itertuples():
        matched = commits[commits.commit.str.startswith(r.commit)]
        if len(matched) != 1:
            raise ValueError(f"Non-unique/missing git prefix for {r.quarter}")
        stamp = pd.Timestamp(matched.iloc[0].committed)
        day = pd.Timestamp(r.commit_date)
        checks = {
            "timestamp_date_matches": str(stamp.date()) == r.commit_date,
            "commit_after_day75": day >= pd.Timestamp(r.day75),
            "lag_reconciles": (day-pd.Timestamp(r.day75)).days == r.lag_days,
            "days_present_75": r.days_cur_present == 75,
            "eu40_yoy_reconciles": bool(np.isclose(r.eu40_flt_da_yoy, 100*(r.eu40_flt_da_cur/r.eu40_flt_da_prev-1), atol=1e-9)),
            "core_yoy_reconciles": bool(np.isclose(r.eu_core_flt_da_yoy, 100*(r.eu_core_flt_da_cur/r.eu_core_flt_da_prev-1), atol=1e-9)),
        }
        if not all(checks.values()):
            raise ValueError(f"Stored lineage check failed: {r.quarter}, {checks}")
        rows.append(dict(quarter=r.quarter, day75=r.day75, commit_date=r.commit_date, committed_utc=stamp.isoformat(), commit_full=matched.iloc[0].commit, lag_days=r.lag_days, **checks))
    maxrow = revisions.loc[revisions.eu40_rev_pct.abs().idxmax()]
    summary = dict(n_quarters=len(rows), first_quarter=pit.iloc[0].quarter, last_quarter=pit.iloc[-1].quarter, n_git_commits=len(commits), all_stored_lineage_checks_pass=True, max_lag_days=int(pit.lag_days.max()),
                   source_label="inherited stored historical-commit-vintage diagnostic; original blobs not locally recertified",
                   feature_admission="Select eu40_flt_da_yoy only when committed_utc is no later than origin timestamp; do not treat target-quarter day75 as known at prior-quarter guide.",
                   completeness_caveat="Upstream code guards75 dates but not40states per date; raw historical blobs absent locally.",
                   median_abs_daily_revision_pct=float(revisions.eu40_rev_pct.abs().median()), max_abs_daily_revision_pct=float(maxrow.eu40_rev_pct), max_revision_entry_date=str(maxrow.entry_date), max_revision_before=float(maxrow.eu40_a), max_revision_after=float(maxrow.eu40_b),
                   max_revision_relevance="Extreme date2026-03-22 lies after1Q26 day75; not evidence the saved QTD75 reading contains that anomaly. Median0 does not imply all daily revisions nil.",
                   direct_cohort_measurement_status="UNAVAILABLE; an unmet data-admission gate is not a rejected physical survival hypothesis", input_sha256=hashes)
    out.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(out/"flight_vintage_checks.csv", index=False)
    (out/"summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "input_sha256"}, indent=2))


if __name__ == "__main__":
    main()
