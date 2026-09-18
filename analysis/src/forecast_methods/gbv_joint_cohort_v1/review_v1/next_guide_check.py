"""Independent bounded Q4 snapshot checks; no fitting or candidate imports."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1"


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def shift(q,k):return str(pd.Period(q,freq="Q")+k)


def main(source,out):
    source,out=Path(source).resolve(),Path(out).resolve()
    if out.exists() or not out.is_relative_to(BASE/"review_v1"):raise ValueError("Use a NEW review output directory")
    out.mkdir(parents=True);checks=[]
    def yes(name,value):checks.append(dict(check=name,passed=bool(value),max_abs_error=0 if value else 1))
    def eq(name,a,b):checks.append(dict(check=name,passed=bool(np.allclose(a,b,atol=1e-8,rtol=1e-10)),max_abs_error=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))))
    manifest=json.loads((source/"manifest.json").read_text());meta=json.loads((source/"model.json").read_text())
    expected=json.loads((BASE/"review_v1/next_guide_inputs_v1.json").read_text())
    for key,h in manifest["source_hashes"].items():yes("source hash:"+key,sha(ROOT/manifest["source_paths"][key])==h)
    for name,h in manifest["outputs"].items():yes("output hash:"+name,sha(source/name)==h)
    code=ROOT/"analysis/src/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/run.py"
    yes("new adapter code hash",sha(code)==manifest["code_sha256"])
    yes("accepted frozen fit code hash",manifest["source_hashes"]["accepted_core"]=="6f395b2956762f179701e78f4c6743ba523da55e45cb7c9f742a2151aa2495af")
    points=pd.read_csv(source/"points.csv").set_index("model");gbv=pd.read_csv(source/"gbv_inputs.csv").set_index("lag")
    train=pd.read_csv(source/"training_rows.csv");con=pd.read_csv(source/"contributions.csv");history=pd.read_csv(source/"cushion_history.csv")
    raw=pd.read_csv(ROOT/"data/processed/overnight/02_kpi_panel_quarterly.csv")
    raw["quarter"]=raw.quarter.map(lambda q:f"20{q[2:]}Q{q[0]}");raw=raw.set_index("quarter")
    cal=pd.read_csv(ROOT/"data/processed/forecast_methods/harness/calendar.csv").set_index("print_quarter")
    yes("same cutoff and actual publication",(points.origin_date=="2026-09-15").all() and (points.last_company_publication=="2026-08-06").all())
    yes("all eligible prior history, not W1 subset",train.quarter.tolist()==expected["primary_training_quarters"] and meta["training_quarters"]==expected["primary_training_quarters"])
    eq("training counts",[len(train),points.loc["joint","n_train"],points.loc["fixed","n_train"]],[20,20,5])
    phi=np.array(meta["joint_weight_groups"]);eq("simplex",phi.sum(),1.);yes("nonnegative weights",(phi>=0).all())
    for row in train.itertuples():
        q=row.quarter
        eq("training revenue:"+q,row.revenue_musd,raw.loc[q,"revenue_musd"])
        eq("training exposure:"+q,[row.g0,row.g1,row.g2,row.g3,row.g4,row.gtail],
           [raw.loc[shift(q,-k),"gbv_musd"] for k in range(5)]+[np.mean([raw.loc[shift(q,-k),"gbv_musd"] for k in [3,4]])])
        yes("training publication:"+q,pd.Timestamp(row.print_date)==pd.Timestamp(cal.loc[q,"print_date"])<=pd.Timestamp("2026-09-15"))
    lams=[]
    for season in range(1,5):
        d=train[train.season==season].sort_values("quarter")
        exposure=d[["g0","g1","g2","gtail"]].to_numpy()@phi
        ratios=d.revenue_musd.to_numpy()/exposure
        lam=np.average(ratios,weights=2.**(-np.arange(len(ratios)-1,-1,-1)/2));lams.append(lam)
        eq(f"full-history seasonal scale Q{season}",100*lam,meta["joint_seasonal_lambda_pct"][season-1])
    forecast_g=np.array([expected["q4_gbv_forecast_musd"],expected["q3_gbv_forecast_musd"],raw.loc["2026Q2","gbv_musd"],raw.loc["2026Q1","gbv_musd"],raw.loc["2025Q4","gbv_musd"]])
    eq("five common GBV inputs",gbv.sort_index().gbv_musd,forecast_g)
    yes("GBV statuses",gbv.loc[0,"status"]=="forecast" and gbv.loc[1,"status"]=="forecast" and (gbv.loc[[2,3,4],"status"]=="reported").all())
    eq("forecast growth rule",gbv.loc[[0,1],"latest_published_gbv_yoy_pct"],np.repeat(expected["latest_gbv_yoy_pct"],2))
    yes("cushion quarters",history.quarter.tolist()==expected["cushion_quarters"])
    for r in history.itertuples():
        eq("cushion arithmetic:"+r.quarter,r.actual_over_guide_minus_one_pct,100*(raw.loc[r.quarter,"revenue_musd"]/r.issued_guide_mid_musd-1))
        yes("cushion guide/actual availability:"+r.quarter,pd.Timestamp(r.guide_issued_date)<=pd.Timestamp(r.actual_publication)<=pd.Timestamp("2026-09-15"))
    cushion=expected["mean_cushion_pct"]/100;eq("same mean cushion",points.cushion_pct,np.repeat(expected["mean_cushion_pct"],2))
    values={}
    for model in ["joint","fixed"]:
        weights=np.r_[phi[:3],phi[3]/2,phi[3]/2] if model=="joint" else np.array([0,2/3,1/3,0,0])
        lam=lams[3] if model=="joint" else expected["baseline_lambda_pct"]/100
        dollars=forecast_g*weights*lam;revenue=dollars.sum();guide=revenue/(1+cushion)
        eq(model+" point arithmetic",[points.loc[model,"revenue_musd"],points.loc[model,"guide_mid_musd"]],[revenue,guide])
        d=con[con.model==model].sort_values("lag")
        eq(model+" contributions",d.revenue_contribution_musd,dollars)
        eq(model+" guide contributions",d.guide_contribution_musd,dollars/(1+cushion))
        eq(model+" backward conditional shares",d.conditional_allocation_share,dollars/revenue)
        eq(model+" effective forward rates",d.effective_fee_per_reported_gbv,weights*lam)
        eq(model+" same GBV",d.gbv_musd,forecast_g)
        values[model]={"revenue_musd":revenue,"guide_mid_musd":guide,"lambda_pct":100*lam}
    yes("no predictive interval fabricated",meta["predictive_interval"] is None and (points.predictive_interval=="not_calculated").all())
    yes("no re-promotion",meta["prior_forecast_promotion"]=="FAIL_unchanged" and meta["new_predictive_test"] is False)
    yes("physical cohort status unchanged",meta["physical_cohort_measurement"]=="UNAVAILABLE_unchanged")
    pd.DataFrame(checks).to_csv(out/"checks.csv",index=False)
    receipt={"checks":len(checks),"passed":sum(c["passed"] for c in checks),"status":"PASS_bounded_same_cutoff_snapshot","imports_candidate_functions":False,"new_optimization_or_predictive_race":False,"values":values,
             "guide_difference_musd":values["joint"]["guide_mid_musd"]-values["fixed"]["guide_mid_musd"],
             "guide_difference_pct":100*(values["joint"]["guide_mid_musd"]/values["fixed"]["guide_mid_musd"]-1),
             "sha256":{str((source/"manifest.json").relative_to(ROOT)):sha(source/"manifest.json"),str(code.relative_to(ROOT)):sha(code),str(Path(__file__).relative_to(ROOT)):sha(__file__)}}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8");print(json.dumps(receipt))
    if receipt["checks"]!=receipt["passed"]:raise AssertionError("Snapshot review failed; outputs retained")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",required=True);a=p.parse_args();main(a.source,a.out)
