"""Explicit DoltHub origin/period audit and paired forecast comparisons; additive only."""
from pathlib import Path
import argparse
import hashlib
import json
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "data/processed/forecast_methods/gbv_decision_0915_v1/street_v1"
VENDOR = "DoltHub post-no-preference/earnings"
SAMPLE = "data/processed/github_altdata/samples/dolthub-post-no-preference-earnings-consensus-vintages/sales_estimate_ABNB_BKNG_EXPE.csv"
PANEL = "data/processed/forecast_methods/L0_dolthub_v2/dolthub_weekly_panel.csv"
CALENDAR = "data/processed/forecast_methods/harness/calendar.csv"
PROOF = "data/processed/forecast_methods/L0_dolthub_v2/t0_provenance_attempt2.json"
FIRST = "data/processed/forecast_methods/L0_dolthub_v2/t0_provenance.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f"Choose a NEW output directory: {out}")
    inputs = {p:digest(ROOT/p) for p in [SAMPLE,PANEL,CALENDAR,PROOF,FIRST,"docs/revenue-forecast-strategy/WORKBOARD_GBV_DECISION_0915_v1.md","docs/revenue-forecast-strategy/05_backtests/GD_CALENDAR_ORIGIN_ADDENDUM_v1.md"]}
    sample = pd.read_csv(ROOT/SAMPLE)
    abnb = sample[sample.act_symbol.eq("ABNB")].copy()
    if abnb.duplicated(["date","period"]).any():
        raise ValueError("Duplicate snapshot/slot")
    quarterly = abnb[abnb.period.isin(["Current Quarter","Next Quarter"])].copy()
    quarterly["target"] = pd.to_datetime(quarterly.period_end_date).dt.to_period("Q").astype(str)
    if not (pd.to_datetime(quarterly.period_end_date).dt.is_quarter_end).all():
        raise ValueError("Non-quarter-end mapping")
    eligible = quarterly[np.isfinite(quarterly.consensus)&quarterly.consensus.gt(0)&quarterly["count"].gt(0)].copy()
    eligible["street_revenue_musd"] = eligible.consensus/1e6
    processed = pd.read_csv(ROOT/PANEL)
    joined = eligible.merge(processed, left_on=["date","period","target"], right_on=["date","slot","period"], suffixes=("_raw","_processed"), validate="one_to_one")
    if len(joined) != len(eligible) or not np.allclose(joined.street_revenue_musd, joined.value_musd, atol=1e-9):
        raise ValueError("Raw-to-processed quarter rows do not reconcile")
    proof = json.loads((ROOT/PROOF).read_text())
    checks, commit_rows = [], []
    for s in proof["snapshot_checks"]:
        for row in s["rows_as_of"]:
            match = abnb[abnb.date.eq(s["snapshot"])&abnb.period.eq(row["period"])&abnb.period_end_date.eq(row["period_end_date"])]
            if len(match) != 1:
                raise ValueError("Missing/duplicate proof row")
            same = all(float(row[c]) == float(match.iloc[0][c]) for c in ["consensus","count","high","low"])
            if not same:
                raise ValueError("Stored AS OF proof no longer agrees")
            checks.append(dict(snapshot_date=s["snapshot"],slot=row["period"],period_end_date=row["period_end_date"],commit=s["commit"],commit_datetime_raw=s["commit_date"],numeric_fields_checked=4,all_numeric_equal=same,timezone="not encoded in source datetime"))
        commit_rows.append(dict(snapshot_date=s["snapshot"],commit=s["commit"],commit_datetime_raw=s["commit_date"],row_asof_equality_verified=True))
    first = json.loads((ROOT/FIRST).read_text())
    for row in first.get("dolt_log_latest",[]):
        m = re.match(r"sales_estimate (\d{4}-\d{2}-\d{2}) update",row.get("message",""))
        if m:
            commit_rows.append(dict(snapshot_date=m.group(1),commit=row["commit_hash"],commit_datetime_raw=row["date"],row_asof_equality_verified=False))
    commits = {r["snapshot_date"]:r for r in commit_rows}
    cal = pd.read_csv(ROOT/CALENDAR).fillna("")
    published = cal[(cal.is_forecast_row.astype(str).str.lower().eq("false"))&cal.print_date.ne("")].copy()
    issued = {r.next_quarter_guided:(float(r.guide_mid) if r.guide_mid!="" else np.nan,r.guide_date) for r in published.itertuples() if r.next_quarter_guided!=""}
    origin_rows = []
    for r in published.itertuples():
        p = pd.Period(r.print_quarter,freq="Q")
        alternate = ((p+2).start_time-pd.Timedelta(days=16)).date().isoformat()
        if alternate < r.print_date:
            continue
        between = published[(published.print_date>r.print_date)&(published.print_date<=alternate)]
        between_guide = published[(published.guide_date>r.print_date)&(published.guide_date<=alternate)]
        for h in (2,3,4):
            target = str(p+h)
            if not "2023Q1"<=target<="2026Q2":
                continue
            for arm,origin in [("release_day",r.print_date),("calendar_minus16",alternate)]:
                candidates = eligible[(eligible.target==target)&(eligible.date<origin)].sort_values("date")
                selected = candidates.iloc[-1] if len(candidates) else None
                all_target = eligible[eligible.target==target].sort_values("date")
                row = dict(arm=arm,origin_date=origin,release_origin_date=r.print_date,last_reported_quarter=str(p),target=target,horizon_quarters=h,guide_announcements_ahead=h-1,vendor=VENDOR,street_available=selected is not None,street_revenue_musd=np.nan,street_snapshot_date="",snapshot_age_days=np.nan,street_count=np.nan,street_high_musd=np.nan,street_low_musd=np.nan,actual_guide_mid_musd=issued.get(target,(np.nan,""))[0],guide_event_date=issued.get(target,(np.nan,""))[1],new_company_releases_between=len(between) if arm!="release_day" else 0,new_guides_between=len(between_guide) if arm!="release_day" else 0,model_point_reuse_allowed=len(between)==0 and len(between_guide)==0 if arm!="release_day" else True,source_status="UNAVAILABLE",selected_commit_datetime_raw="",selected_commit="",row_specific_asof_proof=False,earliest_target_snapshot=all_target.date.min() if len(all_target) else "",first_appearance_diagnostic_only=True)
                if len(all_target):
                    row["days_origin_to_first_target_snapshot"]=(pd.Timestamp(all_target.date.min())-pd.Timestamp(origin)).days
                if selected is not None:
                    c=commits.get(selected.date,{})
                    row.update(street_revenue_musd=float(selected.street_revenue_musd),street_snapshot_date=selected.date,snapshot_age_days=(pd.Timestamp(origin)-pd.Timestamp(selected.date)).days,street_count=float(selected["count"]),street_high_musd=selected.high/1e6,street_low_musd=selected.low/1e6,source_status="inherited publisher-date snapshot; all-row original-vintage availability unverified",selected_commit_datetime_raw=c.get("commit_datetime_raw",""),selected_commit=c.get("commit",""),row_specific_asof_proof=bool(c.get("row_asof_equality_verified",False)))
                origin_rows.append(row)
    origins=pd.DataFrame(origin_rows)
    if origins.duplicated(["arm","last_reported_quarter","target"]).any():
        raise ValueError("Duplicate target-origin")
    coverage=[]
    for (arm,h),g in origins.groupby(["arm","horizon_quarters"]):
        for window,start in [("W1","2023Q1"),("W2","2024Q1")]:
            x=g[g.target>=start]
            coverage.append(dict(arm=arm,horizon_quarters=h,window=window,n_origins=len(x),n_street=int(x.street_available.sum()),n_row_specific_proof=int(x.row_specific_asof_proof.sum()),n_years=x.target.str[:4].nunique(),min_age_days=x.snapshot_age_days.min(),max_age_days=x.snapshot_age_days.max()))
    live=[]
    for target in ["2026Q4","2027Q1","2027Q2"]:
        c=eligible[(eligible.target==target)&(eligible.date<"2026-09-15")].sort_values("date")
        live.append(dict(asof="2026-09-15",target=target,vendor=VENDOR,available=len(c)>0,snapshot_date=c.iloc[-1].date if len(c) else "",revenue_musd=float(c.iloc[-1].street_revenue_musd) if len(c) else np.nan,n=float(c.iloc[-1]["count"]) if len(c) else np.nan,object="eventual revenue consensus, not direct guide expectation"))
    out.mkdir(parents=True)
    origins.to_csv(out/"origin_consensus.csv",index=False)
    pd.DataFrame(coverage).to_csv(out/"coverage.csv",index=False)
    pd.DataFrame(checks).to_csv(out/"historical_proof_checks.csv",index=False)
    pd.DataFrame(commit_rows).to_csv(out/"held_commit_evidence.csv",index=False)
    pd.DataFrame(live).to_csv(out/"live_quarter_coverage.csv",index=False)
    metric_rows=[]
    if args.predictions:
        pp=args.predictions.resolve()
        inputs[str(pp)]=digest(pp)
        preds=pd.read_csv(pp)
        required={"origin_date","last_reported_quarter","target","horizon_quarters","model","revenue_musd","guide_mid_musd","cushion_divisor","actual_revenue_musd","actual_guide_mid_musd"}
        if not required.issubset(preds):
            raise ValueError(f"Missing predictions fields: {required-set(preds)}")
        preds=preds[preds.model.isin(["joint","fixed","guide_growth","revenue_growth"])].copy()
        if preds.duplicated(["origin_date","target","model"]).any():
            raise ValueError("Duplicate prediction key")
        # Independently audited no-new-publication condition is required for any date shift.
        if not origins.model_point_reuse_allowed.all():
            raise ValueError("New company publication requires an actual-cutoff frozen refit")
        merged=pd.concat([g.merge(preds,left_on=["release_origin_date","last_reported_quarter","target","horizon_quarters"],right_on=["origin_date","last_reported_quarter","target","horizon_quarters"],suffixes=("","_forecast"),validate="one_to_many") for _,g in origins.groupby("arm")],ignore_index=True)
        same=np.isclose(merged.actual_guide_mid_musd,merged.actual_guide_mid_musd_forecast,equal_nan=True)
        if not same.all():
            raise ValueError("Guide target disagreement")
        merged["street_implied_guide_musd"]=merged.street_revenue_musd/merged.cushion_divisor
        merged["raw_actual_guide_minus_street_revenue_pct"]=100*(merged.actual_guide_mid_musd/merged.street_revenue_musd-1)
        merged["raw_predicted_guide_minus_street_revenue_pct"]=100*(merged.guide_mid_musd/merged.street_revenue_musd-1)
        merged["common_cushion_actual_guide_gap_pct"]=100*(merged.actual_guide_mid_musd/merged.street_implied_guide_musd-1)
        merged["common_cushion_predicted_gap_pct"]=100*(merged.guide_mid_musd/merged.street_implied_guide_musd-1)
        merged["model_revenue_minus_street_revenue_pct"]=100*(merged.revenue_musd/merged.street_revenue_musd-1)
        ok=merged[["common_cushion_predicted_gap_pct","model_revenue_minus_street_revenue_pct"]].notna().all(axis=1)&merged.revenue_musd.notna()
        if not np.allclose(merged.loc[ok,"common_cushion_predicted_gap_pct"],merged.loc[ok,"model_revenue_minus_street_revenue_pct"],atol=1e-8):
            raise ValueError("Common-cushion identity failed")
        merged.to_csv(out/"paired_rows.csv",index=False)
        for (arm,h,model),g in merged.groupby(["arm","horizon_quarters","model"]):
            for window,start in [("W1","2023Q1"),("W2","2024Q1")]:
                x=g[g.target>=start]
                for kind in ["guide_common_cushion_proxy","revenue_same_object","guide_vs_raw_revenue_different_objects"]:
                    target_col,model_col,street_col=("actual_revenue_musd","revenue_musd","street_revenue_musd") if kind=="revenue_same_object" else ("actual_guide_mid_musd","guide_mid_musd","street_implied_guide_musd" if kind=="guide_common_cushion_proxy" else "street_revenue_musd")
                    z=x.dropna(subset=[target_col,model_col,street_col]).copy()
                    row=dict(arm=arm,horizon_quarters=h,model=model,window=window,comparison=kind,n_origins=len(x),n_paired=len(z),n_years=z.target.str[:4].nunique(),measurement_status="inherited snapshot diagnostic" if len(z) else "UNAVAILABLE: no paired quarterly consensus",model_rmse_musd=np.nan,street_rmse_musd=np.nan,rmse_ratio=np.nan,model_mae_musd=np.nan,street_mae_musd=np.nan,model_bias_musd=np.nan,street_bias_musd=np.nan,gap_sign_accuracy=np.nan,actual_gap_mean_musd=np.nan,predicted_gap_mean_musd=np.nan,rmse_ratio_year_bootstrap90_lo=np.nan,rmse_ratio_year_bootstrap90_hi=np.nan)
                    if len(z):
                        me=(z[model_col]-z[target_col]).to_numpy();se=(z[street_col]-z[target_col]).to_numpy();mr=np.sqrt(np.mean(me**2));sr=np.sqrt(np.mean(se**2)); actualgap=(z[target_col]-z[street_col]).to_numpy();predgap=(z[model_col]-z[street_col]).to_numpy()
                        rng=np.random.default_rng(20260915); years=z.target.str[:4].to_numpy(); unique=np.unique(years); boot=[]
                        for _ in range(2000):
                            idx=np.concatenate([np.flatnonzero(years==year) for year in rng.choice(unique,size=len(unique),replace=True)])
                            denom=np.mean(se[idx]**2)
                            if denom>0:boot.append(np.sqrt(np.mean(me[idx]**2)/denom))
                        row.update(model_rmse_musd=mr,street_rmse_musd=sr,rmse_ratio=mr/sr if sr else np.nan,model_mae_musd=np.mean(np.abs(me)),street_mae_musd=np.mean(np.abs(se)),model_bias_musd=np.mean(me),street_bias_musd=np.mean(se),gap_sign_accuracy=np.mean(np.sign(actualgap)==np.sign(predgap)),actual_gap_mean_musd=np.mean(actualgap),predicted_gap_mean_musd=np.mean(predgap),rmse_ratio_year_bootstrap90_lo=np.quantile(boot,.05) if boot else np.nan,rmse_ratio_year_bootstrap90_hi=np.quantile(boot,.95) if boot else np.nan)
                    metric_rows.append(row)
        pd.DataFrame(metric_rows).to_csv(out/"paired_metrics.csv",index=False)
    summary=dict(vendor=VENDOR,abnb_rows=len(abnb),snapshots=abnb.date.nunique(),quarterly_rows=len(quarterly),eligible_quarterly_rows=len(eligible),raw_processed_reconciliation=True,asof_verified_snapshots=len(proof["snapshot_checks"]),asof_verified_rows=len(checks),all_snapshot_immutability_established=False,all_snapshot_publication_time_established=False,timezone_of_raw_sql_commit_datetime="unspecified",origin_rows=len(origins),coverage=coverage,model_compared=bool(args.predictions),metric_rows=len(metric_rows),interval_label="paired target-year-cluster bootstrap on reused small historical sample; not live predictive intervals",input_sha256=inputs)
    for p,h in inputs.items():
        path=Path(p) if Path(p).is_absolute() else ROOT/p
        if digest(path)!=h:raise ValueError(f"Input changed: {p}")
    (out/"manifest.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ["input_sha256","coverage"]},indent=2))
    print(pd.DataFrame(coverage).to_string(index=False))


if __name__=="__main__":
    main()
