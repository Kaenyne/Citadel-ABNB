"""Independent bootstrap, flight-vintage and forward-sensitivity replay."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1"
GROUPS=["same_quarter","one_earlier","two_earlier","older_finite_tail"]


def shift(q,k):return str(pd.Period(q,freq="Q")+k)


def main(core,diag,out):
    core,diag,out=Path(core).resolve(),Path(diag).resolve(),Path(out).resolve()
    if out.exists() or not out.is_relative_to(BASE/"review_v1"):raise ValueError("New review directory required")
    out.mkdir(parents=True);checks=[]
    def eq(name,a,b):
        checks.append(dict(check=name,passed=bool(np.allclose(a,b,atol=1e-7,rtol=1e-10,equal_nan=True)),max_abs_error=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))))
    def yes(name,v):checks.append(dict(check=name,passed=bool(v),max_abs_error=0 if v else 1))
    p=pd.read_csv(ROOT/"data/processed/overnight/02_kpi_panel_quarterly.csv")
    p["quarter"]=p.quarter.map(lambda q:f"20{q[2:]}Q{q[0]}");p=p.set_index("quarter")
    cal=pd.read_csv(ROOT/"data/processed/forecast_methods/harness/calendar.csv").set_index("print_quarter")
    dates=pd.to_datetime(cal.print_date)
    replay=pd.read_csv(core/"pit_predictions.csv")
    draws=pd.read_csv(core/"bootstrap_draws.csv");intervals=pd.read_csv(core/"bootstrap_intervals.csv")
    for (window,season),d in intervals.groupby(["window","season"]):
        lower="2023Q1" if window=="W1" else "2024Q1"
        qs=[q for q in p.index if q>=lower and int(q[-1])==season]
        x=np.array([[p.loc[shift(q,-k),"gbv_musd"] for k in [0,1,2]]+[np.mean([p.loc[shift(q,-k),"gbv_musd"] for k in [3,4]])] for q in qs])
        sample=draws[draws.window==window];phi=sample[[f"weight_{k}" for k in range(4)]].to_numpy()
        sh=np.stack([x*w/(x@w)[:,None] for w in phi])*100
        rate=phi*sample[f"lambda_Q{season}"].to_numpy()[:,None]*100
        for k,group in enumerate(GROUPS):
            row=d[d.group==group].iloc[0];s=sh[:,:,k].mean(axis=1);r=rate[:,k]
            eq(f"bootstrap-interval:{window}:{season}:{group}",[row.share_p05_pct,row.share_p95_pct,row.share_width_pp,row.effective_p05_pct,row.effective_p95_pct,row.n_draws,row.n_quarters],
               [np.quantile(s,.05),np.quantile(s,.95),np.quantile(s,.95)-np.quantile(s,.05),np.quantile(r,.05),np.quantile(r,.95),len(sample),len(qs)])
    paired=pd.read_csv(diag/"paired_forecast_uncertainty.csv");rng=np.random.default_rng(20260915)
    for spec in replay.spec.unique():
        for window,lower in [("W1","2023Q1"),("W2","2024Q1")]:
            d=replay[(replay.spec==spec)&(replay.quarter>=lower)].copy();years=d.year.unique()
            losses=[]
            for year in years:
                y=d[d.year==year];ec=(y.candidate_guide_musd-y.guide_actual_musd).to_numpy();eb=(y.baseline_guide_musd-y.guide_actual_musd).to_numpy()
                losses.append([len(y),ec@ec,eb@eb])
            losses=np.array(losses);index={y:i for i,y in enumerate(years)};rr=[];dd=[]
            for _ in range(2000):
                selected=rng.choice(years,len(years),replace=True)
                aggregate=losses[[index[y] for y in selected]].sum(axis=0)
                rr.append(np.sqrt(aggregate[1]/aggregate[2]));dd.append((aggregate[1]-aggregate[2])/aggregate[0])
            row=paired[(paired.spec==spec)&(paired.window==window)].iloc[0]
            eq(f"paired-bootstrap:{spec}:{window}",[row.n,row.n_year_clusters,row.ratio_p05,row.ratio_p95,row.loss_difference_p05_musd2,row.loss_difference_p95_musd2],
               [len(d),len(years),np.quantile(rr,.05),np.quantile(rr,.95),np.quantile(dd,.05),np.quantile(dd,.95)])

    f=pd.read_csv(ROOT/"data/processed/govdata_v2/qtd75_pit.csv")
    lineage=pd.read_csv(BASE/"data_audit_v1/flight_lineage_v1/flight_vintage_checks.csv")
    f=f.merge(lineage[["quarter","committed_utc","commit_full"]],on="quarter",validate="one_to_one")
    f["quarter"]=f.quarter.map(lambda q:f"20{q[2:]}Q{q[0]}");f["committed_utc"]=pd.to_datetime(f.committed_utc,utc=True)
    def selected_flight(origin):
        x=f[(f.committed_utc<=pd.Timestamp(origin).tz_localize("UTC"))&(f.days_cur_present>=75)&np.isfinite(f.eu40_flt_da_yoy)]
        return None if x.empty else x.sort_values(["quarter","commit_date"]).iloc[-1]
    ft=pd.read_csv(diag/"pr60_flight_training_pairs.csv");fp=pd.read_csv(diag/"pr60_flight_predictions.csv")
    for row in ft.itertuples():
        origin=pd.Timestamp(row.origin);flt=selected_flight(origin)
        actual_q=row.target;prev=shift(actual_q,-1)
        last=p.loc[prev,"gbv_musd"]/p.loc[shift(prev,-4),"gbv_musd"]-1
        actual=p.loc[actual_q,"gbv_musd"]/p.loc[shift(actual_q,-4),"gbv_musd"]-1
        yes(f"flight-train:{row.evaluation_target}:{actual_q}:vintage",flt is not None and flt.quarter==row.flight_quarter and pd.Timestamp(row.flight_commit_utc)<=origin.tz_localize("UTC"))
        evaluation_origin=pd.Timestamp(fp.loc[fp.quarter==row.evaluation_target,"origin"].iloc[0])
        yes(f"flight-train:{row.evaluation_target}:{actual_q}:outcome",dates.loc[actual_q]<=evaluation_origin and dates.loc[prev]==origin)
        eq(f"flight-train:{row.evaluation_target}:{actual_q}:xy",[row.x,row.y],[flt.eu40_flt_da_yoy/100-last,actual-last])
    for row in fp.itertuples():
        d=ft[ft.evaluation_target==row.quarter];r=replay[(replay.spec=="tail34")&(replay.quarter==row.quarter)].iloc[0]
        beta=np.clip(np.dot(d.x,d.y)/np.dot(d.x,d.x),-2,2);origin=pd.Timestamp(row.origin);flt=selected_flight(origin)
        latest=shift(row.quarter,-2);growth=p.loc[latest,"gbv_musd"]/p.loc[shift(latest,-4),"gbv_musd"]-1
        growth+=beta*(flt.eu40_flt_da_yoy/100-growth)
        g0=p.loc[shift(row.quarter,-4),"gbv_musd"]*(1+growth);g1=p.loc[shift(row.quarter,-5),"gbv_musd"]*(1+growth)
        x=np.array([g0,g1,p.loc[latest,"gbv_musd"],np.mean([p.loc[shift(row.quarter,-k),"gbv_musd"] for k in [3,4]])])
        phi=r[[f"weight_{k}" for k in range(4)]].to_numpy(float);pred=x@phi*r.candidate_lambda_pct/100
        base=(2/3*g1+1/3*p.loc[latest,"gbv_musd"])*r.baseline_lambda_pct/100
        eq(f"flight-predict:{row.quarter}",[row.n_training_pairs,row.slope,row.gbv_growth_pct,row.candidate_revenue_musd,row.candidate_guide_musd,row.flight_baseline_guide_musd],
           [len(d),beta,growth*100,pred,pred/(1+r.cushion_pct/100),base/(1+r.cushion_pct/100)])
        yes(f"flight-predict:{row.quarter}:eligibility",len(d)>=6 and pd.Period(latest,freq="Q").ordinal-pd.Period(flt.quarter,freq="Q").ordinal<=2)
    scores=pd.read_csv(diag/"pr60_flight_scores.csv")
    for row in scores.itertuples():
        d=fp[fp.quarter.ge("2023Q1" if row.window=="W1" else "2024Q1")]
        e=d[f"{row.model}_guide_musd"]-d.guide_actual_musd;b=d.noflight_baseline_guide_musd-d.guide_actual_musd
        eq(f"flight-score:{row.window}:{row.model}",[row.n,row.rmse_musd,row.ratio_to_same_origin_noflight_baseline],
           [len(d),np.sqrt(np.mean(e**2)),np.sqrt(np.mean(e**2)/np.mean(b**2))])
    # Both displayed flight windows use the exact same eight target rows.
    yes("flight-nested-windows-same-sample",set(fp.loc[fp.quarter.ge("2023Q1"),"quarter"])==set(fp.loc[fp.quarter.ge("2024Q1"),"quarter"]))

    live=pd.read_csv(diag/"live_nearfit_forecasts.csv");shapes=pd.read_csv(core/"nearfit_shapes.csv")
    origin=dates.loc[p.index].max();latest=max(p.index);growth=p.loc[latest,"gbv_musd"]/p.loc[shift(latest,-4),"gbv_musd"]
    guide_by_target=cal.dropna(subset=["next_quarter_guided","guide_mid"]).set_index("next_quarter_guided").guide_mid
    cushion=np.mean([p.loc[q,"revenue_musd"]/guide_by_target.loc[q]-1 for q in sorted(p.index) if q in guide_by_target.index][-8:])
    for (window,target),d in live.groupby(["window","target"]):
        lookup=p.gbv_musd.to_dict()
        for q in pd.period_range(shift(latest,1),target,freq="Q"):
            lookup[str(q)]=lookup[shift(str(q),-4)]*growth
        x=np.array([lookup[target],lookup[shift(target,-1)],lookup[shift(target,-2)],np.mean([lookup[shift(target,-k)] for k in [3,4]])])
        selected=shapes[shapes.window==window].set_index("shape_id").loc[d.shape_id]
        phi=selected[[f"weight_{k}" for k in range(4)]].to_numpy();lam=selected[f"lambda_Q{target[-1]}"].to_numpy()
        expected=(phi*x).sum(axis=1)*lam
        eq(f"conditional-future-inputs:{window}:{target}:revenue",d.revenue_musd,expected)
        eq(f"conditional-future-inputs:{window}:{target}:guide",d.guide_musd,expected/(1+cushion))
        yes(f"conditional-future-inputs:{window}:{target}:date",(pd.to_datetime(d.origin)==origin).all())
        if target=="2026Q3":yes(f"Q3-already-issued:{window}",(d.guide_status=="already_issued_implied_guide_diagnostic").all())
    pd.DataFrame(checks).to_csv(out/"checks.csv",index=False)
    receipt={"checks":len(checks),"passed":sum(c["passed"] for c in checks),"imports_candidate_functions":False,
             "scope":"bootstrap parameter intervals, paired year-resampled errors, exact UTC flight inputs/training/outcomes/slopes/scores, conditional future GBV/fee/guide inputs",
             "bound_sha256":{str((diag/"manifest.json").relative_to(ROOT)):hashlib.sha256((diag/"manifest.json").read_bytes()).hexdigest(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8");print(json.dumps(receipt))
    if receipt["checks"]!=receipt["passed"]:raise AssertionError("Diagnostic review failed; outputs retained")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--core",required=True);p.add_argument("--diagnostics",required=True);p.add_argument("--out",required=True);a=p.parse_args();main(a.core,a.diagnostics,a.out)
