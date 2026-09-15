"""Frozen GBV rules versus simple guide/revenue growth across future guide horizons.

No model or feature search. Existing sources are read-only; output paths must be new.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
CORE_PATH=ROOT/"analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/run.py"
CORE_SHA="6f395b2956762f179701e78f4c6743ba523da55e45cb7c9f742a2151aa2495af"
SPEC=ROOT/"docs/revenue-forecast-strategy/WORKBOARD_GBV_DECISION_0915_v1.md"
SEED=20260915
WINDOWS={"W1":"2023Q1","W2":"2024Q1"}
MODELS=["joint","fixed","guide_growth","revenue_growth"]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def accepted_core():
    if sha(CORE_PATH)!=CORE_SHA:raise ValueError("Accepted frozen core hash changed")
    spec=importlib.util.spec_from_file_location("gbv_joint_frozen",CORE_PATH)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def qshift(q,k):return str(pd.Period(q,freq="Q")+k)


def fixed_scale(known,season):
    """Exact accepted fixed-rule same-season EWM, with explicit provenance."""
    lookup=known.set_index("quarter").gbv_musd.to_dict();rows=[]
    for r in known.itertuples():
        if r.season!=season:continue
        a=lookup.get(qshift(r.quarter,-1));b=lookup.get(qshift(r.quarter,-2))
        if a is None or b is None:continue
        rows.append((r.quarter,r.revenue_musd/(2/3*a+1/3*b)))
    if not rows:raise ValueError("No fixed same-season observations")
    weight=2**(-np.arange(len(rows)-1,-1,-1)/2)
    return float(np.average([r[1] for r in rows],weights=weight)),[r[0] for r in rows]


def guides_available(calendar,asof):
    g=calendar.dropna(subset=["next_quarter_guided","guide_mid"]).copy()
    g["issue_date"]=pd.to_datetime(g.print_date)
    g=g[g.issue_date<=pd.Timestamp(asof)]
    if g.next_quarter_guided.duplicated().any():raise ValueError("Duplicate initial guides")
    return g.sort_values("next_quarter_guided").set_index("next_quarter_guided")


def simple_baselines(known,calendar,target,asof,cushion):
    rows=[];skips=[];anchors=[]
    lookup=known.set_index("quarter").revenue_musd.to_dict();latest=known.quarter.max()
    try:
        base_q=qshift(target,-4);growth_q=qshift(latest,-4)
        if base_q not in lookup or growth_q not in lookup:raise ValueError("Missing published year-ago revenue anchor")
        growth=lookup[latest]/lookup[growth_q]
        revenue=lookup[base_q]*growth
        rows.append(dict(model="revenue_growth",revenue_musd=revenue,guide_mid_musd=revenue/(1+cushion),
                         n_train=0,n_source_anchors=len({base_q,latest,growth_q}),n_params_revenue=0,n_params_guide=1,
                         growth_pct=100*(growth-1),latest_growth_target=latest,
                         target_year_ago_anchor=base_q,seasonal_lambda_pct=np.nan,
                         revenue_basis="seasonal_year_ago_revenue_times_latest_known_yoy"))
        for q in sorted({base_q,latest,growth_q}):
            source=known.loc[known.quarter==q].iloc[0]
            anchors.append(dict(model="revenue_growth",anchor_quarter=q,value_musd=lookup[q],
                                source_publication=str(source.print_date.date()),source_type="reported_revenue"))
    except ValueError as exc:skips.append(dict(model="revenue_growth",reason=str(exc)))
    try:
        g=guides_available(calendar,asof);valid=[]
        for q in g.index:
            yearago=qshift(q,-4)
            if yearago in g.index:valid.append(q)
        base_q=qshift(target,-4)
        if not valid or base_q not in g.index:raise ValueError("Missing already-issued guide growth/base anchor")
        latest_guide=max(valid);growth_q=qshift(latest_guide,-4)
        growth=float(g.loc[latest_guide,"guide_mid"]/g.loc[growth_q,"guide_mid"])
        guide=float(g.loc[base_q,"guide_mid"]*growth)
        rows.append(dict(model="guide_growth",revenue_musd=guide*(1+cushion),guide_mid_musd=guide,
                         n_train=0,n_source_anchors=len({base_q,latest_guide,growth_q}),n_params_revenue=1,n_params_guide=0,
                         growth_pct=100*(growth-1),latest_growth_target=latest_guide,
                         target_year_ago_anchor=base_q,seasonal_lambda_pct=np.nan,
                         revenue_basis="issued_guide_growth_forecast_times_common_cushion_proxy"))
        for q in sorted({base_q,latest_guide,growth_q}):
            anchors.append(dict(model="guide_growth",anchor_quarter=q,value_musd=float(g.loc[q,"guide_mid"]),
                                source_publication=str(g.loc[q,"issue_date"].date()),source_type="initial_issued_guide"))
    except ValueError as exc:skips.append(dict(model="guide_growth",reason=str(exc)))
    return rows,skips,anchors


class FrozenForecasts:
    def __init__(self,panel,calendar):
        self.panel=panel.copy();self.calendar=calendar.copy();self.core=accepted_core();self.cache={}

    def origin(self,asof):
        key=str(pd.Timestamp(asof).date())
        if key in self.cache:return self.cache[key]
        known=self.panel[self.panel.print_date<=pd.Timestamp(asof)].copy().sort_values("quarter")
        train=self.core.features(known,[3,4])
        fit=None
        if len(train)>=8 and train.season.nunique()==4:fit=self.core.fit_shape(train)
        cushion,nc=self.core.cushion_at_origin(known,self.calendar)
        value=(known,train,fit,cushion,nc);self.cache[key]=value;return value

    def predict(self,target,asof,is_live=False):
        known,train,fit,cushion,nc=self.origin(asof)
        p=known.quarter.max();h=pd.Period(target,freq="Q").ordinal-pd.Period(p,freq="Q").ordinal
        if h not in [2,3,4]:raise ValueError("Only next one/two/three unissued guides (p+2..4)")
        lastpub=str(known.print_date.max().date());origin=str(pd.Timestamp(asof).date())
        actual=self.panel[self.panel.quarter==target]
        calendar_row=self.calendar[self.calendar.print_quarter==qshift(target,-1)]
        actual_revenue=float(actual.revenue_musd.iloc[0]) if len(actual) else np.nan
        actual_guide=float(calendar_row.guide_mid.iloc[0]) if len(calendar_row) else np.nan
        event_date=str(pd.Timestamp(calendar_row.print_date.iloc[0]).date()) if len(calendar_row) else ""
        common=dict(origin_date=origin,last_reported_quarter=p,last_company_publication=lastpub,
                    target=target,quarter=target,year=int(target[:4]),horizon_quarters=h,guide_announcements_ahead=h-1,
                    is_live=is_live,guide_event_date=event_date,actual_revenue_musd=actual_revenue,
                    actual_guide_mid_musd=actual_guide,cushion_pct=100*cushion,cushion_divisor=1+cushion,
                    n_cushion=nc,knowable_from=lastpub,coefficient_information_date=lastpub,
                    point_in_time_eligible=True,oracle_future_information_used=False,predictive_interval="not_calculated")
        known_gbv=known.set_index("quarter").gbv_musd.to_dict()
        full_gbv=self.panel.set_index("quarter").gbv_musd.to_dict()
        inputs=[];gvalues=[];oracle_g=[]
        for lag in range(5):
            q=qshift(target,-lag)
            if q in known_gbv:
                value=known_gbv[q];status="reported";growth=np.nan
                inputpub=str(known.loc[known.quarter==q,"print_date"].iloc[0].date())
            else:
                value,growth,inputpub=self.core.forecast_gbv(self.panel,q,asof);status="forecast"
            gvalues.append(value);oracle_g.append(full_gbv.get(q,np.nan))
            inputs.append(dict(**common,gbv_quarter=q,lag=lag,gbv_musd=value,gbv_status=status,
                               input_last_publication=inputpub,forecast_growth_pct=100*growth,
                               oracle_realized_gbv_musd=full_gbv.get(q,np.nan)))
        gvalues=np.array(gvalues);oracle_g=np.array(oracle_g)
        rows=[];skips=[];parts=[];fit_rows=[]
        models=[]
        if fit is None:
            skips.append(dict(**common,model="joint",n_train=len(train),reason="requires >=8 complete rows and all4 seasons"))
        else:
            w=np.r_[fit["phi"][:3],fit["phi"][3]/2,fit["phi"][3]/2]
            models.append(("joint",w,fit["lambda"][int(target[-1])-1],len(train),7,8))
            fit_rows.append(dict(origin_date=origin,last_reported_quarter=p,last_company_publication=lastpub,
                                 n_train=len(train),min_training_quarter=train.quarter.min(),max_training_quarter=train.quarter.max(),
                                 training_quarters="|".join(train.quarter),n_params=7,
                                 **{f"weight_group_{k}":fit["phi"][k] for k in range(4)},
                                 **{f"lambda_Q{s}_pct":100*fit["lambda"][s-1] for s in range(1,5)}))
        try:
            lam,quarters=fixed_scale(known,int(target[-1]))
            models.append(("fixed",np.array([0,2/3,1/3,0,0]),lam,len(quarters),4,5))
        except ValueError as exc:skips.append(dict(**common,model="fixed",n_train=0,reason=str(exc)))
        for name,w,lam,n,npr,npg in models:
            dollars=gvalues*w*lam;total=float(dollars.sum())
            known_mask=np.array([r["gbv_status"]=="reported" for r in inputs])
            known_dollars=float(dollars[known_mask].sum());projected=total-known_dollars
            row=dict(**common,model=name,revenue_musd=total,guide_mid_musd=total/(1+cushion),
                     n_train=n,n_source_anchors=np.nan,n_params_revenue=npr,n_params_guide=npg,
                     seasonal_lambda_pct=100*lam,growth_pct=np.nan,latest_growth_target=p,
                     target_year_ago_anchor=qshift(target,-4),known_gbv_revenue_exposure_musd=known_dollars,
                     projected_gbv_revenue_exposure_musd=projected,known_gbv_dollar_share=known_dollars/total,
                     projected_gbv_dollar_share=projected/total,revenue_basis="frozen_GBV_rule",
                     max_training_quarter=train.quarter.max() if name=="joint" else known.quarter.max())
            rows.append(row)
            for lag in range(5):
                parts.append(dict(**common,model=name,lag=lag,booking_quarter=qshift(target,-lag),
                                  gbv_musd=gvalues[lag],gbv_status=inputs[lag]["gbv_status"],
                                  exposure_weight=w[lag],seasonal_lambda_pct=100*lam,
                                  revenue_contribution_musd=dollars[lag],guide_contribution_musd=dollars[lag]/(1+cushion),
                                  conditional_dollar_share=dollars[lag]/total,
                                  basis="model_exposure_not_observed_booking_share"))
            if not is_live and np.isfinite(oracle_g).all():
                oracle_total=float(np.sum(oracle_g*w*lam))
                orow=row.copy();orow.update(model=name+"_oracle",revenue_musd=oracle_total,
                     guide_mid_musd=oracle_total/(1+cushion),known_gbv_revenue_exposure_musd=np.nan,
                     projected_gbv_revenue_exposure_musd=np.nan,known_gbv_dollar_share=np.nan,projected_gbv_dollar_share=np.nan,
                     knowable_from=str(actual.print_date.iloc[0].date()),point_in_time_eligible=False,
                     oracle_future_information_used=True,
                     revenue_basis="unavailable_realized_future_GBV_oracle_no_refitting")
                rows.append(orow)
        simple,missing,anchors=simple_baselines(known,self.calendar,target,asof,cushion)
        for r in simple:
            rows.append(dict(**common,**r,known_gbv_revenue_exposure_musd=np.nan,projected_gbv_revenue_exposure_musd=np.nan,
                             known_gbv_dollar_share=np.nan,projected_gbv_dollar_share=np.nan,max_training_quarter=p))
        skips += [dict(**common,**r,n_train=0) for r in missing]
        anchors=[dict(**common,**r) for r in anchors]
        return rows,skips,inputs,parts,fit_rows,anchors


def metric(error,actual):
    error=np.asarray(error,float);actual=np.asarray(actual,float)
    return dict(n=len(error),rmse_musd=float(np.sqrt(np.mean(error**2))),mae_musd=float(np.mean(abs(error))),
                bias_musd=float(np.mean(error)),error_sd_musd=float(np.std(error,ddof=1)) if len(error)>1 else np.nan,
                worst_abs_miss_musd=float(np.max(abs(error))),relative_rmse_pct=float(100*np.sqrt(np.mean((error/actual)**2))))


def evaluate(predictions):
    hist=predictions[~predictions.is_live].copy();common_metrics=[];all_metrics=[];comparisons=[];deletions=[];coverage=[]
    common_rows=[];variance=[];exposures=[];flags=[]
    for horizon in [2,3,4]:
        for window,lower in WINDOWS.items():
            d=hist[(hist.horizon_quarters==horizon)&(hist.target>=lower)]
            presence=d[d.model.isin(MODELS)].groupby(["origin_date","target"]).model.nunique()
            keys=set(presence[presence==len(MODELS)].index)
            paired=d[d.apply(lambda r:(r.origin_date,r.target) in keys,axis=1)].copy()
            targets=sorted(paired.target.unique());years=np.array([int(t[:4]) for t in targets]);unique_years=np.unique(years)
            for model in d.model.unique():
                x=d[d.model==model]
                coverage.append(dict(horizon_quarters=horizon,window=window,model=model,n_available=len(x),
                                     n_common=len(paired[paired.model==model]),n_year_clusters=x.year.nunique(),
                                     available_targets="|".join(x.target),common_targets="|".join(targets)))
                for object_,col,actualcol in [("guide","guide_mid_musd","actual_guide_mid_musd"),("revenue","revenue_musd","actual_revenue_musd")]:
                    all_metrics.append(dict(horizon_quarters=horizon,window=window,model=model,object=object_,
                                            basis="unpaired_own_available_rows",**metric(x[col]-x[actualcol],x[actualcol])))
            if paired.empty:continue
            common_rows.append(paired.assign(window=window))
            rng=np.random.default_rng(SEED+horizon)
            sampled=rng.integers(0,len(unique_years),size=(2000,len(unique_years)))
            counts=np.stack([(sampled==i).sum(axis=1) for i in range(len(unique_years))],axis=1)
            yearly_n=np.array([(years==y).sum() for y in unique_years]);boot_n=counts@yearly_n
            for object_,col,actualcol in [("guide","guide_mid_musd","actual_guide_mid_musd"),("revenue","revenue_musd","actual_revenue_musd")]:
                matrix=paired.pivot(index="target",columns="model",values=col).sort_index()
                actual=paired.drop_duplicates("target").set_index("target")[actualcol].reindex(matrix.index).to_numpy()
                errors=matrix.to_numpy()-actual[:,None]
                for j,model in enumerate(matrix.columns):
                    common_metrics.append(dict(horizon_quarters=horizon,window=window,model=model,object=object_,
                                               basis="common_joint_fixed_guidegrowth_revenuegrowth_rows",
                                               n_year_clusters=len(unique_years),**metric(errors[:,j],actual)))
                for candidate in ["joint","fixed","joint_oracle","fixed_oracle"]:
                    for reference in ["fixed","guide_growth","revenue_growth"]:
                        if candidate==reference:continue
                        ec=matrix[candidate].to_numpy()-actual;eb=matrix[reference].to_numpy()-actual
                        sc=np.array([np.sum(ec[years==y]**2) for y in unique_years]);sb=np.array([np.sum(eb[years==y]**2) for y in unique_years])
                        bc=counts@sc;bb=counts@sb
                        ratios=np.sqrt(bc/bb);loss=(bc-bb)/boot_n
                        comparisons.append(dict(horizon_quarters=horizon,window=window,object=object_,candidate=candidate,reference=reference,
                                                n=len(actual),n_year_clusters=len(unique_years),n_bootstrap=2000,
                                                candidate_rmse_musd=np.sqrt(np.mean(ec**2)),reference_rmse_musd=np.sqrt(np.mean(eb**2)),
                                                rmse_ratio=np.sqrt(np.sum(ec**2)/np.sum(eb**2)),
                                                ratio_p05=np.quantile(ratios,.05),ratio_p95=np.quantile(ratios,.95),
                                                loss_difference_p05_musd2=np.quantile(loss,.05),loss_difference_p95_musd2=np.quantile(loss,.95),
                                                basis="paired_year_cluster_conditional_uncertainty_reused_history"))
                        if object_=="guide" and candidate in ["joint","fixed"]:
                            for unit,values in [("year",years),("quarter",np.array(targets))]:
                                for value in np.unique(values):
                                    keep=values!=value
                                    if not keep.any():continue
                                    ratio=np.sqrt(np.sum(ec[keep]**2)/np.sum(eb[keep]**2))
                                    deletions.append(dict(horizon_quarters=horizon,window=window,candidate=candidate,reference=reference,
                                                          deleted_unit=unit,deleted_value=str(value),n=int(keep.sum()),guide_rmse_ratio=ratio))
                for model in ["joint","fixed"]:
                    production=matrix[model].to_numpy();oracle=matrix[model+"_oracle"].to_numpy()
                    input_error=production-oracle;residual=oracle-actual;total=production-actual
                    cov=np.cov(input_error,residual,ddof=1)
                    variance.append(dict(horizon_quarters=horizon,window=window,model=model,object=object_,n=len(actual),
                                         gbv_input_component_mean_musd=input_error.mean(),oracle_residual_mean_musd=residual.mean(),
                                         gbv_input_component_variance_musd2=cov[0,0],oracle_residual_variance_musd2=cov[1,1],
                                         twice_covariance_musd2=2*cov[0,1],total_error_variance_musd2=np.var(total,ddof=1),
                                         identity_error_musd2=np.var(total,ddof=1)-cov[0,0]-cov[1,1]-2*cov[0,1],
                                         basis="holding_frozen_fit_fixed_not_causal_decomposition"))
            for model in ["joint","fixed"]:
                x=paired[paired.model==model]
                exposures.append(dict(horizon_quarters=horizon,window=window,model=model,n=len(x),
                                      known_mean_pct=100*x.known_gbv_dollar_share.mean(),known_min_pct=100*x.known_gbv_dollar_share.min(),
                                      known_max_pct=100*x.known_gbv_dollar_share.max(),projected_mean_pct=100*x.projected_gbv_dollar_share.mean(),
                                      basis="predictor_dollar_exposure_not_observed_reservation_share"))
    cmp=pd.DataFrame(comparisons);delete=pd.DataFrame(deletions)
    for horizon in [2,3,4]:
        for candidate in ["joint","fixed"]:
            p=cmp[(cmp.horizon_quarters==horizon)&(cmp.candidate==candidate)&(cmp.object=="guide")&cmp.reference.isin(["guide_growth","revenue_growth"])]
            d=delete[(delete.horizon_quarters==horizon)&(delete.candidate==candidate)&delete.reference.isin(["guide_growth","revenue_growth"])]
            coverage_ok=len(p)==4 and (p.n>=8).all()
            magnitude_ok=coverage_ok and (p.rmse_ratio<=.9).all()
            deletion_ok=len(d)>0 and (d.guide_rmse_ratio<1).all()
            interval_ok=len(p[p.reference=="guide_growth"])==2 and (p.loc[p.reference=="guide_growth","ratio_p95"]<1).all()
            flags.append(dict(horizon_quarters=horizon,model=candidate,coverage_pass=bool(coverage_ok),magnitude_pass=bool(magnitude_ok),
                              deletion_pass=bool(deletion_ok),paired_guidegrowth_interval_pass=bool(interval_ok),
                              promotion_pass=bool(coverage_ok and magnitude_ok and deletion_ok and interval_ok),
                              evaluated_windows_overlap=True,reused_historical_data=True))
    return {"scores_common":pd.DataFrame(common_metrics),"scores_all_available":pd.DataFrame(all_metrics),
            "paired_comparisons":cmp,"score_deletions":delete,"coverage":pd.DataFrame(coverage),
            "common_predictions":pd.concat(common_rows,ignore_index=True),"error_variance_decomposition":pd.DataFrame(variance),
            "exposure_summary":pd.DataFrame(exposures),"promotion_gates":pd.DataFrame(flags)}


def wide_table(predictions):
    keys=["origin_date","last_reported_quarter","target","horizon_quarters","guide_announcements_ahead","is_live"]
    metadata=["last_company_publication","guide_event_date","actual_revenue_musd","actual_guide_mid_musd","cushion_pct","cushion_divisor","knowable_from"]
    out=predictions.drop_duplicates(keys)[keys+metadata].copy().set_index(keys)
    for model,prefix in [("joint","candidate"),("fixed","baseline"),("joint_oracle","oracle"),("fixed_oracle","fixed_oracle"),("guide_growth","guide_growth"),("revenue_growth","revenue_growth")]:
        a=predictions[predictions.model==model].set_index(keys)
        for col,label in [("revenue_musd","revenue_musd"),("guide_mid_musd","guide_musd"),("n_train","n_train"),("n_params_revenue","n_params_revenue"),("n_params_guide","n_params_guide")]:
            out[f"{prefix}_{label}"]=a[col]
    return out.reset_index()


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=ROOT/"data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v1")
    args=p.parse_args();out=args.out.resolve()
    if out.exists():raise FileExistsError("Output path must be new")
    core=accepted_core();sources={"kpi":core.SOURCES["kpi"],"calendar":core.SOURCES["calendar"],"accepted_core":CORE_PATH,"decision_spec":SPEC}
    before={name:sha(path) for name,path in sources.items()}
    panel,calendar=core.load_inputs();engine=FrozenForecasts(panel,calendar)
    dates=calendar.set_index("print_quarter").print_date
    records=[];skips=[];inputs=[];parts=[];fits=[];anchors=[]
    for h in [2,3,4]:
        print(f"Frozen historical horizon p+{h}",flush=True)
        for target in panel.loc[panel.quarter>="2023Q1","quarter"]:
            origin_q=qshift(target,-h);asof=str(dates.loc[origin_q])
            values=engine.predict(target,asof)
            for destination,rows in zip([records,skips,inputs,parts,fits,anchors],values):destination.extend(rows)
    for target in ["2026Q4","2027Q1","2027Q2"]:
        values=engine.predict(target,"2026-09-15",True)
        for destination,rows in zip([records,skips,inputs,parts,fits,anchors],values):destination.extend(rows)
    predictions=pd.DataFrame(records).sort_values(["is_live","horizon_quarters","target","model"]).reset_index(drop=True)
    tables={"predictions":predictions,"wide_predictions":wide_table(predictions),"skipped_predictions":pd.DataFrame(skips),
            "gbv_inputs":pd.DataFrame(inputs),"gbv_contributions":pd.DataFrame(parts),
            "origin_fits":pd.DataFrame(fits).drop_duplicates("origin_date"),"baseline_source_anchors":pd.DataFrame(anchors)}
    tables.update(evaluate(predictions))
    out.mkdir(parents=True)
    for name,frame in tables.items():frame.to_csv(out/f"{name}.csv",index=False)
    summary={"spec":"frozen_core_and_two_preregistered_simple_baselines","core_sha256":CORE_SHA,"seed":SEED,
             "historical_target_windows":WINDOWS,"bootstrap_draws":2000,"primary_evaluation":"same rows for all4 production models",
             "W1_W2_overlap":"W2subsetofW1; long-horizon eligible samples may be identical",
             "physical_cohorts":"UNAVAILABLE; not required to test reduced-form total forecasts",
             "new_feature_or_weight_search":False,"live_cutoff":"2026-09-15","live_last_company_publication":"2026-08-06",
             "promotion_gates":tables["promotion_gates"].to_dict("records"),
             "historical_rows":int((~predictions.is_live).sum()),"live_rows":int(predictions.is_live.sum()),
             "unique_fitted_origins":len(tables["origin_fits"]),"predictive_intervals":None}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    if before!={name:sha(path) for name,path in sources.items()}:raise AssertionError("Existing source changed")
    manifest={"source_hashes":before,"source_paths":{name:str(path.relative_to(ROOT)) for name,path in sources.items()},
              "code_sha256":sha(__file__),"outputs":{path.name:sha(path) for path in sorted(out.iterdir())}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(tables["promotion_gates"].to_string(index=False),flush=True)
    print(predictions[predictions.is_live][["target","model","revenue_musd","guide_mid_musd","known_gbv_dollar_share"]].to_string(index=False),flush=True)
    print(f"Completed {out}",flush=True)


if __name__=="__main__":main()
