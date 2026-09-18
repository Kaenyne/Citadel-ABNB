"""Bounded live continuation of the frozen joint and fixed GBV rules."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
CORE_PATH=Path(__file__).resolve().parents[1]/"quant_v1/run.py"
ACCEPTED_CORE_SHA="6f395b2956762f179701e78f4c6743ba523da55e45cb7c9f742a2151aa2495af"
SPEC_PATH=ROOT/"docs/revenue-forecast-strategy/WORKBOARD_JOINT_COHORT_NEXT_GUIDE_v1.md"


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_core():
    if sha(CORE_PATH)!=ACCEPTED_CORE_SHA:raise ValueError("Accepted core source hash changed")
    spec=importlib.util.spec_from_file_location("joint_core_frozen",CORE_PATH)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def calculate(panel,calendar,asof="2026-09-15",target="2026Q4"):
    core=frozen_core();cutoff=pd.Timestamp(asof)
    known=panel[panel.print_date<=cutoff].copy().sort_values("quarter")
    if target in set(known.quarter):raise ValueError("Target already printed")
    latest=known.quarter.max();last_publication=known.print_date.max()
    if latest!=core.qshift(target,-2):raise ValueError("This snapshot requires two unprinted GBV quarters")
    train=core.features(known,[3,4])
    if len(train)<8 or train.season.nunique()!=4:raise ValueError("Insufficient complete eligible training history")
    fit=core.fit_shape(train)
    lookup=known.set_index("quarter").gbv_musd.to_dict()
    input_rows=[]
    for lag in range(5):
        quarter=core.qshift(target,-lag)
        if quarter in lookup:
            value=lookup[quarter];status="reported"
            available=known.loc[known.quarter==quarter,"print_date"].iloc[0]
            yoy=np.nan
        else:
            value,yoy,available=core.forecast_gbv(panel,quarter,cutoff)
            status="forecast";lookup[quarter]=value
        input_rows.append(dict(target=target,quarter=quarter,lag=lag,gbv_musd=value,status=status,
                               origin_date=str(cutoff.date()),last_underlying_publication=str(pd.Timestamp(available).date()),
                               latest_published_gbv_yoy_pct=100*yoy if status=="forecast" else np.nan,
                               rule="year_ago_GBV_times_latest_published_yoy_factor" if status=="forecast" else "frozen_reported_company_GBV"))
    gbv=pd.DataFrame(input_rows)
    x=np.array([lookup[target],lookup[core.qshift(target,-1)],lookup[core.qshift(target,-2)],
                np.mean([lookup[core.qshift(target,-k)] for k in [3,4]])])
    season=int(target[-1]);lam=fit["lambda"][season-1]
    joint=float(x@fit["phi"]*lam)
    fixed,nfixed,fixedlam=core.baseline_forecast(known,target,lookup[core.qshift(target,-1)])
    cushion,ncushion=core.cushion_at_origin(known,calendar)
    guides=calendar.dropna(subset=["next_quarter_guided","guide_mid"]).set_index("next_quarter_guided")
    history=[]
    for row in known.itertuples():
        if row.quarter not in guides.index:continue
        g=guides.loc[row.quarter]
        history.append(dict(quarter=row.quarter,actual_revenue_musd=row.revenue_musd,issued_guide_mid_musd=g.guide_mid,
                            guide_issued_date=g.print_date,actual_publication=str(row.print_date.date()),
                            actual_over_guide_minus_one_pct=100*(row.revenue_musd/g.guide_mid-1)))
    history=pd.DataFrame(history).tail(8).reset_index(drop=True)
    assert len(history)==ncushion
    assert np.isclose(history.actual_over_guide_minus_one_pct.mean(),100*cushion,atol=1e-12)
    points=[];contributions=[]
    for model,total,l,n,npr,npg in [("joint",joint,lam,len(train),7,8),("fixed",fixed,fixedlam,nfixed,4,5)]:
        points.append(dict(model=model,target=target,quarter=target,origin_date=str(cutoff.date()),asof=str(cutoff.date()),
                           last_company_publication=str(last_publication.date()),last_company_quarter=latest,
                           revenue_musd=total,guide_mid_musd=total/(1+cushion),n_train=n,
                           n_train_basis="all_complete_quarters" if model=="joint" else "target_same_season_quarters",
                           n_params_revenue=npr,n_params_guide=npg,seasonal_lambda_pct=100*l,cushion_pct=100*cushion,
                           n_cushion=ncushion,knowable_from=str(last_publication.date()),
                           status="LIVE_research_snapshot_not_promoted",predictive_interval="not_calculated"))
        for lag in range(5):
            group=lag if lag<3 else 3
            weight=fit["phi"][group]/(2 if lag>=3 else 1) if model=="joint" else {1:2/3,2:1/3}.get(lag,0)
            g=lookup[core.qshift(target,-lag)];dollars=g*weight*l
            contributions.append(dict(model=model,target=target,booking_quarter=core.qshift(target,-lag),lag=lag,
                                      gbv_musd=g,gbv_status=gbv.loc[gbv.lag==lag,"status"].iloc[0],
                                      exposure_weight=weight,seasonal_lambda_pct=100*l,
                                      effective_fee_per_reported_gbv=weight*l,revenue_contribution_musd=dollars,
                                      guide_contribution_musd=dollars/(1+cushion),conditional_allocation_share=dollars/total,
                                      basis="model_contribution_not_observed_reservation_cohort",
                                      beyond_lag4="unobserved_finite_support_assumption"))
    metadata={"asof":str(cutoff.date()),"target":target,"last_company_publication":str(last_publication.date()),
              "core_sha256":ACCEPTED_CORE_SHA,"n_train":len(train),"training_quarters":train.quarter.tolist(),
              "joint_weight_groups":fit["phi"].tolist(),"joint_seasonal_lambda_pct":(100*fit["lambda"]).tolist(),
              "successful_optimizer_starts":fit["successful_starts"],"n_cushion":ncushion,
              "cushion_quarters":history.quarter.tolist(),"cushion_pct":100*cushion,
              "all_complete_published_history":True,"comparison":"same GBV growth carry rule and same cushion",
              "prior_forecast_promotion":"FAIL_unchanged","physical_cohort_measurement":"UNAVAILABLE_unchanged",
              "new_predictive_test":False,"predictive_interval":None,
              "fixed_parameter_count_basis":"four seasonal scales across model; target uses one; plus shared cushion for guide",
              "limits":"No new market data, Street comparison, physical survival or causal RNPL estimate"}
    return pd.DataFrame(points),gbv,pd.DataFrame(contributions),history,train,metadata


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,default=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/results_v1")
    args=parser.parse_args();out=args.out.resolve()
    if out.exists():raise FileExistsError("Use a NEW output directory")
    core=frozen_core()
    sources={"kpi":core.SOURCES["kpi"],"calendar":core.SOURCES["calendar"],"accepted_core":CORE_PATH,"frozen_spec":SPEC_PATH}
    before={name:sha(path) for name,path in sources.items()}
    panel,calendar=core.load_inputs()
    points,gbv,contrib,cushion,train,metadata=calculate(panel,calendar)
    out.mkdir(parents=True)
    for name,frame in [("points",points),("gbv_inputs",gbv),("contributions",contrib),("cushion_history",cushion),("training_rows",train)]:
        frame.to_csv(out/f"{name}.csv",index=False)
    (out/"model.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    after={name:sha(path) for name,path in sources.items()}
    if before!=after:raise AssertionError("Read-only source hash changed")
    manifest={"source_hashes":before,"source_paths":{name:str(path.relative_to(ROOT)) for name,path in sources.items()},
              "code_sha256":sha(__file__),"outputs":{path.name:sha(path) for path in sorted(out.iterdir())}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(points.to_string(index=False));print(gbv.to_string(index=False));print(json.dumps(metadata,indent=2))


if __name__=="__main__":main()
