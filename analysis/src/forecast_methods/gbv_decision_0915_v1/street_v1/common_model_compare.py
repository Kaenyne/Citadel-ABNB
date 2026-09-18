"""Fair common-row display and independent calendar-point binding, no new forecasts."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
MODELS=["fixed","joint","guide_growth","revenue_growth"]


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    paired=ROOT/"data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/results_v3/paired_rows.csv"
    calendar=ROOT/"data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/calendar_arm_v1/predictions.csv"
    checks=ROOT/"data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/calendar_arm_v1/information_equivalence_checks.csv"
    livepoints=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/results_v1/points.csv"
    livecons=ROOT/"data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/results_v3/live_quarter_coverage.csv"
    d=pd.read_csv(paired);c=pd.read_csv(calendar);proof=pd.read_csv(checks)
    if not proof.point_reuse_allowed.all() or not proof.known_actuals_identical.all() or not proof.issued_guides_identical.all():raise ValueError("Calendar equivalence failed")
    dc=d[d.arm.eq("calendar_minus16")]
    bc=c[c.model.isin(MODELS)]
    match=dc.merge(bc,on=["origin_date","model","target"],suffixes=("_street","_quant"),validate="one_to_one")
    if len(match)!=len(dc):raise ValueError("Calendar points missing in quant artifact")
    for col in ["revenue_musd","guide_mid_musd","cushion_divisor","actual_guide_mid_musd","actual_revenue_musd"]:
        if not np.allclose(match[col+"_street"],match[col+"_quant"],atol=1e-8,equal_nan=True):raise ValueError(f"Calendar binding changed {col}")
    metrics=[];commonrows=[];coverage=[]
    for (arm,h),g in d.groupby(["arm","horizon_quarters"]):
        for window,start in [("W1","2023Q1"),("W2","2024Q1")]:
            x=g[g.target>=start]
            for kind in ["guide_common_cushion_proxy","revenue_same_object","guide_vs_raw_revenue_different_objects"]:
                tc,mc,sc=("actual_revenue_musd","revenue_musd","street_revenue_musd") if kind=="revenue_same_object" else ("actual_guide_mid_musd","guide_mid_musd","street_implied_guide_musd" if kind=="guide_common_cushion_proxy" else "street_revenue_musd")
                sets=[set(x[x.model.eq(model)].dropna(subset=[tc,mc,sc]).target) for model in MODELS]
                shared=set.intersection(*sets)
                z=x[x.target.isin(shared)].copy()
                coverage.append(dict(arm=arm,horizon_quarters=h,window=window,comparison=kind,n_common=len(shared),n_models=len(MODELS),target_quarters="|".join(sorted(shared))))
                if not len(shared):continue
                z["window"]=window;z["comparison"]=kind;commonrows.append(z)
                unique=z.drop_duplicates("target").sort_values("target")
                for model in MODELS+["DoltHub"]:
                    group=z[z.model.eq(model)].sort_values("target") if model!="DoltHub" else unique
                    pred=group[mc] if model!="DoltHub" else group[sc]
                    error=(pred-group[tc]).to_numpy();streeterr=(group[sc]-group[tc]).to_numpy()
                    rmse=np.sqrt(np.mean(error**2));srmse=np.sqrt(np.mean(streeterr**2))
                    years=group.target.str[:4].to_numpy();uy=np.unique(years);rng=np.random.default_rng(20260915);ratios=[]
                    for _ in range(2000):
                        idx=np.concatenate([np.flatnonzero(years==y) for y in rng.choice(uy,len(uy),replace=True)])
                        den=np.mean(streeterr[idx]**2)
                        if den>0:ratios.append(np.sqrt(np.mean(error[idx]**2)/den))
                    metrics.append(dict(arm=arm,horizon_quarters=h,window=window,comparison=kind,model=model,n=len(group),n_years=len(uy),rmse_musd=rmse,mae_musd=np.mean(np.abs(error)),bias_musd=np.mean(error),error_sd_musd=np.std(error,ddof=1),rmse_ratio_to_street=rmse/srmse,ratio_year_bootstrap90_lo=np.quantile(ratios,.05),ratio_year_bootstrap90_hi=np.quantile(ratios,.95),status="inherited snapshot conditional diagnostic"))
    lp=pd.read_csv(livepoints);ls=pd.read_csv(livecons);lr=[]
    for r in lp.itertuples():
        s=ls[ls.target.eq(r.target)].iloc[0]
        divisor=1+r.cushion_pct/100
        implied=s.revenue_musd/divisor
        lr.append(dict(model=r.model,target=r.target,origin_date=r.origin_date,model_revenue_musd=r.revenue_musd,model_guide_musd=r.guide_mid_musd,street_revenue_musd=s.revenue_musd,street_implied_guide_musd=implied,cushion_pct=r.cushion_pct,raw_guide_minus_revenue_consensus_musd=r.guide_mid_musd-s.revenue_musd,common_cushion_guide_gap_musd=r.guide_mid_musd-implied,common_cushion_relative_gap_pct=100*(r.guide_mid_musd/implied-1),revenue_relative_gap_pct=100*(r.revenue_musd/s.revenue_musd-1),vendor=s.vendor,snapshot_date=s.snapshot_date,street_object="eventual revenue; common cushion guide is assumed proxy",no_realized_outcome=True))
    out.mkdir(parents=True)
    pd.DataFrame(metrics).to_csv(out/"common_model_metrics.csv",index=False)
    pd.DataFrame(coverage).to_csv(out/"common_model_coverage.csv",index=False)
    pd.concat(commonrows,ignore_index=True).to_csv(out/"common_model_rows.csv",index=False)
    pd.DataFrame(lr).to_csv(out/"live_comparison.csv",index=False)
    inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [paired,calendar,checks,livepoints,livecons]}
    receipt=dict(calendar_comparison_rows_verified=len(match),company_origin_groups_verified=len(proof),all_reused_points_numerically_equal=True,models=MODELS,common_metric_rows=len(metrics),input_sha256=inputs)
    (out/"manifest.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":main()
