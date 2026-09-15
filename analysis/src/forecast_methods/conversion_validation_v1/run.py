"""Immutable, offline five-parameter GBV-to-revenue validation. No registrations."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
def local_module(name):
    """Load package-owned modules without sharing generic run/model names."""
    spec = importlib.util.spec_from_file_location("_conversion_validation_v1_"+name, Path(__file__).with_name(name+".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_model = local_module("model")
from _conversion_validation_v1_model import FIXED_W, GRID, calibration_error, fit, fitted_values, lag_rows, predict, profile, quarter, sequential_band, validate_panel

ROOT = Path(__file__).resolve().parents[4]
AS_OF = "2026-09-13"
SEED = 20260913
REG = "data/processed/forecast_methods/registry/"
BENCHMARKS = {
    "legacy_fixed_season_mean": REG+"kernel-lambda__revenue_level_next_q.csv",
    "legacy_fixed_last3_ex2021": REG+"kernel-lambda__revenue_level_next_q_last3_ex_covid.csv",
    "harness_naive": REG+"baselines__naive.csv",
    "harness_ar1": REG+"baselines__ar1.csv",
    "guide_cushion_postguide": REG+"baselines__guide_cushion.csv",
}
INPUTS = ["data/processed/overnight/02_kpi_panel_quarterly.csv", "data/processed/forecast_methods/harness/calendar.csv",
          "data/processed/forecast_methods/harness/targets.csv", "analysis/src/forecast_methods/kernel_engine_v2/engine.py",
          "docs/revenue-forecast-strategy/05_backtests/L3_CONVERSION_PREREG_v1.md", *BENCHMARKS.values()]


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rmse(e): return float(np.sqrt(np.mean(np.square(e)))) if len(e) else np.nan


def load():
    raw = pd.read_csv(ROOT/INPUTS[0])
    cal = pd.read_csv(ROOT/INPUTS[1])
    raw=raw.copy()
    raw["quarter"] = raw.quarter.map(quarter)
    dates = cal.set_index("print_quarter")
    raw["print_date"] = raw.quarter.map(dates.print_date)
    raw["print_date_basis"] = raw.quarter.map(dates.print_date_basis)
    raw = validate_panel(raw)
    targets = pd.read_csv(ROOT/INPUTS[2])
    return raw, targets


def parameter_row(f, sample, model, loss, **extra):
    return dict(sample=sample, model=model, loss=loss, n=f["n"], n_parameters=f["n_parameters"], w=f["w"],
                **{f"lambda_Q{s}_pct": 100*f["lambdas"][s-1] for s in range(1,5)}, **extra)


def fullsample(d):
    params, profiles, fitted, bootstrap, loyo = [], [], [], [], []
    for sample, start in [("all22", "2021Q1"), ("exclude2021", "2022Q1"), ("2023plus", "2023Q1")]:
        z = d[d.quarter >= start]
        for loss in ["usd", "relative"]:
            losses, rates = profile(z, GRID, loss)
            for i,w in enumerate(GRID):
                profiles.append(dict(sample=sample, loss=loss, n=len(z), w=w, rmse_loss=np.sqrt(losses[i]/len(z)),
                                     **{f"lambda_Q{s}_pct":100*rates[i,s-1] for s in range(1,5)}))
            for model, fixed in [("free_w", None), ("fixed_2_3", FIXED_W)]:
                f = fit(z, fixed, loss)
                pred = fitted_values(z, f); err=pred-z.revenue_musd.to_numpy()
                params.append(parameter_row(f,sample,model,loss,rmse_musd=rmse(err),rmse_relative_pct=100*rmse(err/z.revenue_musd)))
                if sample=="all22" and loss=="usd":
                    for r,p in zip(z.itertuples(),pred):
                        fitted.append(dict(quarter=r.quarter,season=r.season,model=model,n_fit=len(z),w=f["w"],
                                           weighted_gbv_musd=f["w"]*r.gbv_l1+(1-f["w"])*r.gbv_l2,
                                           actual_musd=r.revenue_musd,predicted_musd=p,error_musd=p-r.revenue_musd,
                                           evidence_status="full_sample_descriptive_not_PIT"))
    rng=np.random.default_rng(SEED); years=sorted(d.year.unique()); rejected=0
    for draw in range(1000):
        selected=rng.choice(years,len(years),replace=True)
        z=pd.concat([d[d.year==y] for y in selected],ignore_index=True)
        try: f=fit(z)
        except ValueError: rejected+=1;continue
        bootstrap.append(parameter_row(f,"year_block_bootstrap","free_w","usd",draw=draw,selected_years="|".join(map(str,selected))))
    for year in years:
        tr,te=d[d.year!=year],d[d.year==year]
        for name,w in [("free_w",None),("fixed_2_3",FIXED_W)]:
            f=fit(tr,w);p=fitted_values(te,f)
            loyo.append(parameter_row(f,"leave_one_year_out",name,"usd",held_out_year=year,n_test=len(te),
                                      held_out_rmse_musd=rmse(p-te.revenue_musd)))
    return list(map(pd.DataFrame,[params,profiles,fitted,bootstrap,loyo])),rejected


def chronological(panel,targets):
    rows=[]; histories={m:[] for m in ["free_w_usd","fixed_2_3_usd","free_w_relative","fixed_2_3_relative"]}
    s=importlib.util.spec_from_file_location("conversion_frozen_k0",ROOT/INPUTS[3])
    k0=importlib.util.module_from_spec(s);s.loader.exec_module(k0)
    selected=targets[(targets.quarter>="2023Q1")&(targets.quarter<="2026Q2")].copy()
    for target in selected.itertuples():
        date=pd.Timestamp(target.guide_date)
        known=panel[panel.print_date<=date].copy()
        for loss in ["usd","relative"]:
            for name,w in [("free_w",None),("fixed_2_3",FIXED_W)]:
                f=predict(known,target.quarter,date,w,loss);model=name+"_"+loss
                past=[v for v,printed in histories[model] if printed<=date]
                lo,hi,ncal=sequential_band(f["point"],past)
                row=dict(quarter=target.quarter,year=int(target.quarter[:4]),season=int(target.quarter[-1]),
                         vintage_date=date.strftime("%Y-%m-%d"),actual_print_date=target.print_date,
                         model=model,loss=loss,point=f["point"],actual=target.revenue_musd,n_train=f["n"],
                         w=f["w"],**{f"lambda_Q{s}_pct":100*f["lambdas"][s-1] for s in range(1,5)},
                         train_quarters="|".join(f["training_quarters"]),max_input_date=f["max_input_date"],
                         last_train_outcome_date=f["last_train_outcome_date"],gbv_l1=f["gbv_l1"],gbv_l2=f["gbv_l2"],
                         lag1_print_date=f["lag1_print_date"],lag2_print_date=f["lag2_print_date"],n_parameters=f["n_parameters"],
                         q10=lo,q90=hi,n_cal=ncal,evidence_status="chronological_PIT_post_letter_no_target_guide_used",
                         info_set="prior-quarter print available at same-day letter close; target outcome and target GBV excluded")
                rows.append(row)
                histories[model].append((calibration_error(target.revenue_musd,f["point"]),pd.Timestamp(target.print_date)))
        # Existing engine is unmodified. Its stricter API needs the documented next-day wrapper.
        try:
            k=k0.kernel_forecast(target.quarter,date+pd.Timedelta(days=1))
        except k0.DataUnavailable as exc:
            rows.append(dict(quarter=target.quarter,year=int(target.quarter[:4]),season=int(target.quarter[-1]),
                             vintage_date=date.strftime("%Y-%m-%d"),actual_print_date=target.print_date,model="K0_fixed_operational",
                             point=np.nan,actual=target.revenue_musd,w=FIXED_W,n_train=0,
                             evidence_status="inherited_operational_abstention",info_set=str(exc)))
            continue
        rows.append(dict(quarter=target.quarter,year=int(target.quarter[:4]),season=int(target.quarter[-1]),vintage_date=date.strftime("%Y-%m-%d"),
                         actual_print_date=target.print_date,model="K0_fixed_operational",loss="inherited_K0_policy",point=k["point"],
                         actual=target.revenue_musd,n_train=k["n_train"],w=FIXED_W,n_parameters=np.nan,
                         max_input_date=k["knowable_from"],variant=k["variant"],
                         evidence_status="frozen_operational_comparator_PIT_post_letter",
                         info_set="K0 API as_of=guide_date+1; recorded source max date must remain <=guide date"))
    for model,path in BENCHMARKS.items():
        b=pd.read_csv(ROOT/path)
        b=b[(b.target=="revenue_musd")&(b.prior_basis=="PIT")&(b.window=="W1")&b.quarter.between("2023Q1","2026Q2")]
        if b.duplicated(["quarter","vintage_date"]).any():raise ValueError("duplicate frozen comparator")
        b=b.merge(selected[["quarter","guide_date","print_date","revenue_musd"]],on="quarter",validate="one_to_one")
        if len(b)!=14 or not (b.vintage_date==b.guide_date).all():raise ValueError("comparator cells do not align")
        for r in b.itertuples():
            rows.append(dict(quarter=r.quarter,year=int(r.quarter[:4]),season=int(r.quarter[-1]),vintage_date=r.vintage_date,
                             actual_print_date=r.print_date,model=model,loss="frozen_registry_method",point=r.point,actual=r.revenue_musd,
                             n_train=r.n_train,n_parameters=r.n_params,
                             evidence_status="postguide_advantaged_benchmark" if model=="guide_cushion_postguide" else "frozen_PIT_registry_comparator",
                             info_set="uses already-issued target guide and trailing cushion" if model=="guide_cushion_postguide" else "same target/vintage PIT registry row",
                             source_reference=path))
    p=pd.DataFrame(rows);p["error_musd"]=p.point-p.actual;p["relative_error_pct"]=100*p.error_musd/p.actual
    p["covered_80"]=np.where(p.q10.notna(),(p.actual>=p.q10)&(p.actual<=p.q90),np.nan)
    return p


def score(p):
    scores=[];paired=[];boot=[];rng=np.random.default_rng(SEED)
    for window,start in [("W1","2023Q1"),("W2","2024Q1")]:
        z=p[p.quarter>=start]
        fixed=z[z.model=="fixed_2_3_usd"].set_index("quarter")
        naive=z[z.model=="harness_naive"].set_index("quarter")
        for model,g in z.groupby("model",sort=False):
            n_origins=len(g)
            g=g[np.isfinite(g.point)&np.isfinite(g.actual)].copy()
            aligned=g.set_index("quarter").join(fixed[["error_musd"]],rsuffix="_fixed").join(naive[["error_musd"]],rsuffix="_naive")
            e=g.error_musd;mask=g.q10.notna()
            scores.append(dict(window=window,model=model,n=len(g),n_origins=n_origins,n_missing=n_origins-len(g),rmse_musd=rmse(e),mae_musd=float(e.abs().mean()),bias_musd=float(e.mean()),
                               rmse_relative_pct=rmse(g.relative_error_pct),
                               ratio_to_fixed_ols=rmse(e)/rmse(aligned.error_musd_fixed),ratio_to_naive_usd=rmse(e)/rmse(aligned.error_musd_naive),
                               n_interval=int(mask.sum()),coverage_80=float(g.loc[mask,"covered_80"].mean()) if mask.any() else np.nan,
                               mean_interval_width_pct=float((100*(g.loc[mask,"q90"]-g.loc[mask,"q10"])/g.loc[mask,"point"]).mean()) if mask.any() else np.nan))
        free=z[z.model=="free_w_usd"].set_index("quarter")
        pair=free[["year","vintage_date","point","actual","error_musd"]].join(fixed[["point","error_musd"]],rsuffix="_fixed")
        pair["sq_error_delta_musd2"]=pair.error_musd**2-pair.error_musd_fixed**2
        pair["absolute_error_delta_musd"]=pair.error_musd.abs()-pair.error_musd_fixed.abs()
        pair["window"]=window;paired.append(pair.reset_index())
        years=sorted(pair.year.unique())
        for draw in range(2000):
            years_drawn=rng.choice(years,len(years),replace=True)
            sample=pd.concat([pair[pair.year==y] for y in years_drawn])
            boot.append(dict(window=window,draw=draw,n=len(sample),n_year_blocks=len(years),
                             rmse_ratio=rmse(sample.error_musd)/rmse(sample.error_musd_fixed),
                             mean_sq_error_delta_musd2=float(sample.sq_error_delta_musd2.mean())))
    return pd.DataFrame(scores),pd.concat(paired,ignore_index=True),pd.DataFrame(boot)


def run(out):
    out=Path(out)
    if out.exists():raise FileExistsError("Use a new immutable output directory: "+str(out))
    before={p:digest(ROOT/p) for p in INPUTS}
    panel,targets=load();d=lag_rows(panel);d=d[d.quarter.between("2021Q1","2026Q2")].copy()
    if len(d)!=22 or d.quarter.duplicated().any():raise AssertionError("exact 22 lag-complete quarters required")
    truth=targets.set_index("quarter")
    if not np.array_equal(d.revenue_musd.to_numpy(),truth.loc[d.quarter,"revenue_musd"].to_numpy()):raise AssertionError("revenue source mismatch")
    if not np.array_equal(d.gbv_musd.to_numpy(),truth.loc[d.quarter,"gbv_musd"].to_numpy()):raise AssertionError("GBV source mismatch")
    start=time.perf_counter()
    (params,profiles,fitted,bootstrap,loyo),rejected=fullsample(d)
    paths=chronological(panel,targets);scores,paired,paired_boot=score(paths)
    own=paths[paths.model.isin(["free_w_usd","fixed_2_3_usd","free_w_relative","fixed_2_3_relative","K0_fixed_operational"])&paths.point.notna()]
    maxdates=pd.to_datetime(own.max_input_date,utc=True)
    origins=pd.to_datetime(own.vintage_date,utc=True)
    if (maxdates>origins).any():raise AssertionError("future input in chronological prediction")
    if (pd.to_datetime(own.actual_print_date)<=pd.to_datetime(own.vintage_date)).any():raise AssertionError("target outcome already known")
    complete=scores[scores.model!="K0_fixed_operational"]
    if not (complete.n==complete.window.map({"W1":14,"W2":10})).all():raise AssertionError("unmatched comparison windows")
    primary=scores[scores.model=="free_w_usd"]
    passes=bool((primary.ratio_to_fixed_ols<1).all())
    interval_rows=[]
    for c in ["w",*[f"lambda_Q{s}_pct" for s in range(1,5)]]:
        q=bootstrap[c].quantile([.025,.5,.975])
        interval_rows.append(dict(parameter=c,draws=len(bootstrap),attempted=1000,lower=q.iloc[0],median=q.iloc[1],upper=q.iloc[2],
                                  method="calendar_year_block_percentile_sensitivity_six_blocks"))
    uncertainty=pd.DataFrame(interval_rows)
    paired_summary=[]
    for window,g in paired_boot.groupby("window"):
        q=g.rmse_ratio.quantile([.025,.5,.975]);sq=g.mean_sq_error_delta_musd2.quantile([.025,.5,.975])
        paired_summary.append(dict(window=window,n_year_blocks=int(g.n_year_blocks.iloc[0]),draws=len(g),
                                   rmse_ratio_lower=q.iloc[0],rmse_ratio_median=q.iloc[1],rmse_ratio_upper=q.iloc[2],
                                   mse_delta_lower=sq.iloc[0],mse_delta_median=sq.iloc[1],mse_delta_upper=sq.iloc[2]))
    paired_summary=pd.DataFrame(paired_summary)
    flatness=[]
    for (sample,loss),g in profiles.groupby(["sample","loss"]):
        p=params[(params["sample"]==sample)&(params.loss==loss)&(params.model=="free_w")].iloc[0]
        minimum=p.rmse_musd if loss=="usd" else p.rmse_relative_pct/100
        good=g[g.rmse_loss<=1.05*minimum]
        flatness.append(dict(sample=sample,loss=loss,n=int(p.n),best_w=p.w,minimum_rmse=minimum,
                             threshold_rmse=1.05*minimum,w_lower=float(good.w.min()),w_upper=float(good.w.max()),
                             grid_step=.005,evidence_status="within5pct_RMSE_grid_range_not_confidence_interval"))
    out.mkdir(parents=True)
    def save(name,df):df.to_csv(out/name,index=False,float_format="%.12g",lineterminator="\n")
    for name,frame in [("dataset_22.csv",d[["quarter","season","year","print_date","print_date_basis","revenue_musd","gbv_musd","gbv_l1","gbv_l2","gbv_l1_date","gbv_l2_date"]]),
                       ("parameters.csv",params),("profile_loss.csv",profiles),("fullsample_fitted.csv",fitted),
                       ("parameter_bootstrap.csv",bootstrap),("parameter_uncertainty.csv",uncertainty),("leave_year_out.csv",loyo),
                       ("chronological_paths.csv",paths),("chronological_scores.csv",scores),("paired_error_deltas.csv",paired),
                       ("paired_year_bootstrap.csv",paired_boot),("paired_uncertainty.csv",paired_summary),
                       ("profile_flatness.csv",pd.DataFrame(flatness))]:save(name,frame)
    primary_fit=params[(params["sample"]=="all22")&(params.model=="free_w")&(params.loss=="usd")].iloc[0]
    spec={"validation_protocol_status":"accepted_audited_specification_pending_independent_review",
          "model_id":"conversion_validation_v1_shared_w_four_seasons","formula":"R_t=lambda_s*(w*GBV_t-1+(1-w)*GBV_t-2)",
          "units":"R and GBV in USD millions; lambda fraction; w scalar fraction","fit_window":"2021Q1-2026Q2","n":22,"n_parameters":5,
          "loss":"USD-level SSE with analytical season-through-origin OLS profile, common bounded w",
          "descriptive_calibration":{"w":float(primary_fit.w),"lambda_by_season":{f"Q{s}":float(primary_fit[f"lambda_Q{s}_pct"])/100 for s in range(1,5)}},
          "descriptive_calibration_status":"auditable_fullsample_fit_not_PIT_forecast_or_booking_share",
          "prospective_free_weight_hurdle":"PASS" if passes else "FAIL",
          "prospective_hurdle_definition":"USD RMSE lower than identically fitted fixed 2/3 in BOTH matched W1 and W2",
          "production_benchmark":"existing fixed 2/3 operational engine retained; no new all22 OLS coefficients adopted",
          "adoption_status":"pending_L4_and_team_review; validation acceptance is separate from model adoption",
          "parameter_uncertainty":"year-block sensitivity: six calendar years including partial 2026; not precise structural identification",
          "forbidden_interpretations":["w as booking-to-stay probability or measured revenue share","lambda as commission take rate",
                                        "in-sample fit as prospective edge","all future revenue already booked","double-add FX to reported USD GBV"]}
    (out/"accepted_validation_spec.json").write_text(json.dumps(spec,indent=2)+"\n",encoding="utf-8")
    l4=[]
    for metric,v,unit in [("shared_lag_w",float(primary_fit.w),"fraction_of_lagged_GBV_driver_coefficient"),
                          *[(f"seasonal_conversion_Q{s}",float(primary_fit[f"lambda_Q{s}_pct"]),"percent_of_weighted_lagged_GBV_coefficient_level") for s in range(1,5)]]:
        key="w" if metric=="shared_lag_w" else "lambda_"+metric[-2:]+"_pct"
        u=uncertainty.set_index("parameter").loc[key]
        l4.append(dict(quarter="historical",metric=metric,scenario="full22_free_w_USD_OLS_descriptive",value=v,lower=u.lower,upper=u.upper,units=unit,
                       information_date=AS_OF,evidence_status="fullsample_descriptive_calibration_n22_five_parameters",
                       source_reference="conversion_validation_v1/accepted_validation_spec.json; parameters.csv",
                       treatment="descriptive_do_not_apply_as_production_replacement",
                       baseline_being_replaced="existing fixed 2/3 operational specification would require joint five-parameter replacement; none adopted",
                       embedded_fx="reported USD GBV already translated at booking-period FX; lambda inherits residual conversion effects",
                       adoption_status="pending_L4_and_team_review",limitations="w is not measured booking probability or actual contribution share; year-block bounds are sensitivity with only six blocks"))
    for r in primary.itertuples():
        l4.append(dict(quarter="historical",metric="free_to_fixed_PIT_RMSE_ratio",scenario=r.window,value=r.ratio_to_fixed_ols,lower=np.nan,upper=np.nan,
                       units="USD_level_RMSE_ratio",information_date=AS_OF,evidence_status=f"chronological_PIT_n{r.n}_post_letter_no_guide_input",
                       source_reference="conversion_validation_v1/chronological_scores.csv",treatment="descriptive",
                       baseline_being_replaced="none; validation evidence only",embedded_fx="both models use the same reported USD GBV",
                       adoption_status="pending_L4_and_team_review",limitations="overlapping windows; compare paired year-block uncertainty before any promotion"))
    save("l4_conversion_inputs.csv",pd.DataFrame(l4))
    usd_free=params[(params.model=="free_w")&(params.loss=="usd")].set_index("sample")
    pit_free=primary.set_index("window")
    claims=[
        ("allowed","The audited descriptive model has four seasonal conversion rates and one shared bounded lag coefficient, fitted jointly to 22 quarters.","fullsample calibration",22),
        ("allowed",f"The full22 descriptive fit estimates w={primary_fit.w:.6f}; seasonal conversion rates Q1/Q2/Q3/Q4 are "+"/".join(f"{primary_fit[f'lambda_Q{s}_pct']:.4f}%" for s in range(1,5))+".","USD-level OLS; coefficients are not measured booking shares or take rates",22),
        ("allowed",f"Excluding 2021 gives fitted shared weight {usd_free.loc['exclude2021','w']:.3f}; starting in 2023 gives {usd_free.loc['2023plus','w']:.3f}.","predeclared estimation-period sensitivity; all22 remains primary",22),
        ("allowed",f"The free/fixed chronological RMSE ratios are {pit_free.loc['W1','ratio_to_fixed_ols']:.3f} on W1 (n=14) and {pit_free.loc['W2','ratio_to_fixed_ols']:.3f} on W2 (n=10).", "preregistered USD-level promotion hurdle evaluated on both windows",14),
        ("allowed",f"The free-weight chronological RMSE hurdle is {'PASS' if passes else 'FAIL'} against an identically fitted fixed benchmark on W1/W2; production adoption remains pending.","chronological validation",14),
        ("allowed","Once management has supplied a guide, guide-plus-cushion is an advantaged revenue benchmark; this test does not establish guide-surprise alpha.","information-set distinction",14),
        ("forbidden","The fitted lag coefficient is the percentage of bookings or revenue recognized one quarter later.","reduced-form coefficients do not identify booking cohorts",22),
        ("forbidden","A high in-sample R-squared or close actual/fitted plot establishes forecasting skill.","descriptive fit is not prospective validation",22),
        ("forbidden","The estimated seasonal conversion rate is Airbnb's commission take rate.","lagged GBV conversion differs from contemporaneous accounting ratio",22),
        ("forbidden","All future revenue is already booked; the two lag weights are measured probabilities.","current-quarter booking flow omitted, not proven zero",22),
        ("forbidden","The free-weight or newly fitted all22 fixed-OLS calibration is automatically the team's production kernel.","L4/team adoption is separate from validation",22),
    ]
    save("claim_ledger.csv",pd.DataFrame(claims,columns=["status","claim","reason_or_scope","n"]))
    after={p:digest(ROOT/p) for p in INPUTS}
    if before!=after:raise AssertionError("frozen input changed")
    save("source_manifest.csv",pd.DataFrame([dict(path=p,sha256=before[p],after_sha256=after[p]) for p in INPUTS]))
    summary=dict(implementation="PASS",n_fullsample=22,n_W1=14,n_W2=10,free_weight_hurdle="PASS" if passes else "FAIL",
                 free_weight=float(primary_fit.w),parameter_bootstrap_attempted=1000,parameter_bootstrap_accepted=len(bootstrap),
                 parameter_bootstrap_rejected=rejected,parameter_bootstrap_endpoint_fraction=float(((bootstrap.w<1e-8)|(bootstrap.w>1-1e-8)).mean()),
                 source_hashes_unchanged=len(before),l4_rows=len(l4),investment_adoption="pending; existing fixed operational engine retained")
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    local_module("charts").render(out,params,profiles,fitted,uncertainty,paths,scores,paired_summary,loyo,passes)
    print(json.dumps(summary,indent=2));print(f"elapsed_seconds={time.perf_counter()-start:.3f}")


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True)
    run(ap.parse_args().out)
