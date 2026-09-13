"""Offline reproducible current-information cohort FX sensitivity, no registrations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as kernel
from cohort_fx_v1.engine import apply_timing, from_reported_contributions, period, yoy_bridge

AS_OF = "2026-09-13"
SOURCE_DATE = "2026-09-11"
BASIS = "fixed_2025_daily_average_usd_per_unit"
FX_PATH = ROOT / "data/processed/forecast_methods/fx_lag_v2/fx_daily_2026-09-11.csv"
KPI_PATH = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
FOREIGN = {"EUR":.32, "GBP":.07,"CAD":.05,"AUD":.04,"BRL":.04,"MXN":.04}
SOURCE_URL = "https://fred.stlouisfed.org/series/"
SEC_K = "https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm"
SEC_Q = "https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm"


def rate_table(daily, periods, multiplier, as_of=AS_OF, source_date=SOURCE_DATE, max_stale_days=14):
    if pd.Timestamp(source_date)>pd.Timestamp(as_of):
        raise ValueError("Cached source was unavailable at as-of")
    if not np.isfinite(multiplier) or multiplier<=0:
        raise ValueError("Foreign currency multiplier must be positive")
    d=daily[daily.unit.eq("usd_per_foreign_unit")].copy()
    d["date"]=pd.to_datetime(d.date)
    # Future quote perturbations are excluded. Source vintage remains current-only.
    d=d[d.date.le(pd.Timestamp(as_of))]
    if d.duplicated(["date","ccy"]).any():
        raise ValueError("Duplicate daily currency dates")
    if not np.isfinite(d.usd_per_unit).all() or (d.usd_per_unit<=0).any():
        raise ValueError("Invalid daily FX rate")
    out=[]
    for c in ["USD", *FOREIGN]:
        dc=d[d.ccy.eq(c)].sort_values("date")
        if c!="USD":
            if dc.empty:
                raise ValueError(f"Missing currency: {c}")
            cutoff=dc.date.max()
            if (pd.Timestamp(as_of)-cutoff).days>max_stale_days:
                raise ValueError(f"Stale FX cache for {c}: {cutoff.date()}")
            ref=dc[dc.date.dt.year.eq(2025)].usd_per_unit
            if ref.empty or dc.date.max()<pd.Timestamp("2025-12-31"):
                raise ValueError("Complete 2025 reference unavailable")
            reference=float(ref.mean()); last=float(dc.usd_per_unit.iloc[-1]); sid=dc.fred_id.iloc[0]
        else:
            cutoff=pd.Timestamp(as_of);reference=1.;last=1.;sid="USD_identity"
        for p in sorted(periods):
            pr=period(p);start=pr.start_time.normalize();end=pr.end_time.normalize()
            if c=="USD":
                value=1.;nobs=0;nflat=0;status="observed" if end<=pd.Timestamp(as_of) else "flat_assumption"
                quote_cutoff=min(pd.Timestamp(as_of),end)
            else:
                obs=dc[dc.date.between(start,end)]
                quote_cutoff=obs.date.max() if len(obs) else cutoff
                future=pd.bdate_range(max(start,cutoff+pd.Timedelta(days=1)),end)
                nobs=len(obs);nflat=len(future)
                if not nobs and not nflat:
                    raise ValueError(f"Missing period rate {p}/{c}")
                value=(obs.usd_per_unit.sum()+nflat*last*multiplier)/(nobs+nflat)
                status="observed_plus_flat" if nobs and nflat else ("flat_assumption" if nflat else "observed")
            out.append(dict(period=p,currency=c,usd_per_unit=value,reference_usd_per_unit=reference,
                information_date=source_date,reference_basis=BASIS,source_ref=SOURCE_URL+sid if c!="USD" else "USD identity",
                evidence_status="public_FRED_time_average_proxy" if c!="USD" else "identity",
                rate_status=status,quote_cutoff=str(quote_cutoff.date()),
                observed_daily_n=nobs,flat_weekday_n=nflat,foreign_usd_multiplier=multiplier,
                averaging="arithmetic observed daily quotes plus unobserved future weekdays at last cached spot; not transaction weighted"))
    return pd.DataFrame(out)


def load_kernel_inputs():
    kpi=pd.read_csv(KPI_PATH)
    kpi["quarter"]=kpi.quarter.map(lambda x:"20"+x[2:]+"Q"+x[0])
    byq=kpi.set_index("quarter")
    rows=[];checks=[]
    for q,origin in [("2026Q3",AS_OF),("2025Q3","2025-08-07")]:
        lam=kernel.pit_lambda(3,origin)
        forecast=kernel.kernel_forecast(q,origin)
        for lag,coef in [(1,kernel.WEIGHT),(2,1-kernel.WEIGHT)]:
            b=str(pd.Period(q,freq="Q")-lag)
            gbv=float(byq.loc[b,"gbv_musd"])*1e6
            rows.append(dict(quarter=q,booking_quarter=b,kernel_coefficient=coef,
                gbv_reported_usd=gbv,lambda_pct=lam["lambda_pct"],
                reported_contribution_usd=lam["lambda_pct"]/100*coef*gbv,
                kernel_origin=origin,kernel_variant=lam["variant"],n_lambda_train=lam["n_train"],
                lambda_knowable_from=lam["knowable_from"],information_date=AS_OF,
                source_ref="kernel_engine_v2 public APIs; "+str(KPI_PATH.relative_to(ROOT)),
                evidence_status="inherited_kernel_not_literal_booking_to_stay_probability"))
        got=sum(r["reported_contribution_usd"] for r in rows if r["quarter"]==q)/1e6
        if abs(got-forecast["point"])>1e-8:
            raise ValueError("K0 public API identity failed")
        checks.append(dict(quarter=q,kernel_origin=origin,kernel_point_musd=forecast["point"],
            reconstructed_musd=got,difference_musd=got-forecast["point"],n_booking_cohorts=2,
            evidence_status="2025 lambda originally PIT; this assembled FX scenario retrospective"))
    return pd.DataFrame(rows),pd.DataFrame(checks)


def reported_rows(kernel_rows, nonusd, u):
    if not 0<=nonusd<=1 or not 0<=u<=1:
        raise ValueError("Exposure shares out of bounds")
    shares={"USD":1-nonusd,**{c:nonusd*v/.56 for c,v in FOREIGN.items()}}
    out=[]
    for r in kernel_rows.itertuples():
        for c,s in shares.items():
            out.append(dict(quarter=r.quarter,booking_quarter=r.booking_quarter,currency=c,
                reported_contribution_usd=r.reported_contribution_usd*s,rnpl_share=u,
                reported_currency_share=s,reference_basis=BASIS,information_date=AS_OF,
                source_ref=r.source_ref+"; L3_COHORT_FX_PREREG.md exposure assumptions",
                evidence_status="assumed_currency_and_revenue_RNPL_shares_not_L2_stock"))
    return pd.DataFrame(out)


def allocation_rows(cohorts,timing):
    out=[]
    for r in cohorts.itertuples():
        target=period(r.quarter);m0=target.asfreq("M",how="start")
        if timing=="equal_recognition_months":
            vals=[(str(m0+i),1/3,"recognition_month") for i in range(3)]
        elif timing=="first_recognition_month":
            vals=[(str(m0),1.,"recognition_month")]
        elif timing=="last_recognition_month":
            vals=[(str(m0+2),1.,"recognition_month")]
        elif timing=="prior_month_payment_fixing":
            vals=[(str(m0-1),1.,"payment_fixing_proxy")]
        else:
            raise ValueError("Unknown timing scenario")
        for p,weight,hyp in vals:
            out.append(dict(quarter=r.quarter,booking_quarter=r.booking_quarter,currency=r.currency,
                fx_period=p,p=weight,timing_hypothesis=hyp,reference_basis=BASIS,
                information_date=AS_OF,source_ref="L3_COHORT_FX_PREREG.md timing hypotheses",
                evidence_status="assumed_unidentified_timing"))
    return pd.DataFrame(out)


def source_manifest(bundle):
    refs=[(str(p.relative_to(ROOT)),p,"repo_read_only") for p in [KPI_PATH,FX_PATH,
        ROOT/"analysis/src/forecast_methods/kernel_engine_v2/engine.py",
        ROOT/"analysis/src/forecast_methods/fx_lag_v2/fetch_fx_v2.py",
        ROOT/"data/processed/forecast_methods/harness/calendar.csv",
        ROOT/"data/raw/regulatory/quantification/abnb_2025_10k.json",
        ROOT/"data/raw/regulatory/quantification/abnb_2026q2_10q.html",
        ROOT/"docs/revenue-forecast-strategy/05_backtests/ALPHA_F_RNPL.md",
        ROOT/"docs/revenue-forecast-strategy/05_backtests/L3_COHORT_FX_PREREG.md"]]
    for p in sorted(Path(__file__).parent.glob("*.py")):
        refs.append((str(p.relative_to(ROOT)),p,"package_source"))
    if bundle:
        for rel in ["FX_ENGINE_MENTAL_MAP.md","reusable_r/fx-engine-validation.md",
                    "reusable_r/fx_engine/README.md","reusable_r/fx_engine/contract.R",
                    "reusable_r/fx_engine/engine.R"]:
            refs.append(("EXTERNAL_FX_BUNDLE/"+rel,bundle/rel,"external_read_only_interface_audit_not_runtime_dependency"))
    return pd.DataFrame([dict(source_ref=ref.replace("\\","/"),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
        bytes=p.stat().st_size,treatment=t,information_date=AS_OF) for ref,p,t in refs])


def write_csv(df,path):
    df.to_csv(path,index=False,float_format="%.12g",lineterminator="\n")


def run(out,bundle=None):
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Copy-never-overwrite: choose a new empty output directory")
    out.mkdir(parents=True,exist_ok=True)
    kr,identity=load_kernel_inputs();daily=pd.read_csv(FX_PATH)
    periods=set(kr.booking_quarter)
    for q in kr.quarter.unique():
        m0=period(q).asfreq("M",how="start")
        periods.update(str(m0+i) for i in [-1,0,1,2])
    rate_sets={m:rate_table(daily,periods,m) for m in [.95,1.,1.05]}
    summaries=[];details=[];allocations=[];bridges=[];adapter=[]
    timings=["equal_recognition_months","first_recognition_month","last_recognition_month","prior_month_payment_fixing"]
    for nonusd in [.40,.56,.70]:
        priorc=from_reported_contributions(reported_rows(kr[kr.quarter.eq("2025Q3")],nonusd,0),rate_sets[1.],AS_OF)
        prior=apply_timing(priorc,allocation_rows(priorc,timings[0]),rate_sets[1.],AS_OF)["summary"].iloc[0].to_dict()
        for u in [0.,.1,.2,.3,1.]:
            for timing in timings:
                for mult,rates in rate_sets.items():
                    name=f"fx{mult:.2f}_nonusd{nonusd:.2f}_u{u:.2f}_{timing}"
                    c=from_reported_contributions(reported_rows(kr[kr.quarter.eq("2026Q3")],nonusd,u),rates,AS_OF)
                    result=apply_timing(c,allocation_rows(c,timing),rates,AS_OF)
                    labels=dict(scenario=name,foreign_usd_multiplier=mult,assumed_nonusd_reported_share=nonusd,
                        assumed_rnpl_revenue_share=u,timing_scenario=timing)
                    s=result["summary"].iloc[0].to_dict();summaries.append({**labels,**s})
                    for key,acc in [("detail",details),("allocations",allocations)]:
                        acc.extend({**labels,**r} for r in result[key].to_dict("records"))
                    bridges.append({**labels,**yoy_bridge(s,prior),"information_date":AS_OF,
                        "source_ref":"kernel_identity.csv; cohort_currency_detail.csv; rates.csv",
                        "prior_assumption":"year_ago_kernel_with_ordinary_booking_FX_and_u_zero"})
                    for metric,field,unit,treatment in [
                        ("reference_normalized_kernel_revenue","reference_revenue_usd","USD","diagnostic_reference_only_not_new_forecast"),
                        ("ordinary_booking_kernel_revenue","booking_revenue_usd","USD","baseline_identity_do_not_add"),
                        ("rnpl_retimed_kernel_revenue","retimed_revenue_usd","USD","conditional_replacement_level"),
                        ("rnpl_fx_incremental_replacement","incremental_replacement_usd","USD","incremental_replacement_only_after_compatibility_check"),
                        ("rnpl_fx_replacement_multiplier","replacement_multiplier","ratio","multiply_only_matching_ordinary_booking_baseline"),
                        ("rnpl_fx_level_multiplier","retimed_level_multiplier","ratio","reference_level_only_never_multiply_reported_kernel")]:
                        adapter.append(dict(quarter="2026Q3",metric=metric,scenario=name,value=s[field],
                            lower=np.nan,upper=np.nan,units=unit,information_date=AS_OF,
                            evidence_status="scenario_only_unidentified_exposure_and_timing",source_ref="cohort_fx_v1/scenario_summary.csv; L3_COHORT_FX_ACCOUNTING.md",
                            treatment=treatment,baseline_being_replaced="inherited_K0_Q3_2026_reported_USD_kernel",
                            baseline_value_usd=s["booking_revenue_usd"],embedded_fx="booking_period_currency_FX_conditionally_reconstructed",
                            embedded_hedges="unresolved_in_inherited_lambda_no_hedge_addition_permitted",
                            adoption_status="pending_baseline_and_accounting_reconciliation",reference_basis=BASIS))
    paths={"kernel_inputs.csv":kr,"kernel_identity.csv":identity,
        "rates.csv":pd.concat([v.assign(fx_scenario=f"fx{k:.2f}") for k,v in rate_sets.items()],ignore_index=True),
        "scenario_summary.csv":pd.DataFrame(summaries),"cohort_currency_detail.csv":pd.DataFrame(details),
        "cohort_currency_recognition_weights.csv":pd.DataFrame(allocations),"yoy_bridge.csv":pd.DataFrame(bridges),
        "l4_adapter.csv":pd.DataFrame(adapter),"input_manifest.csv":source_manifest(bundle)}
    for name,df in paths.items():
        write_csv(df,out/name)
    metadata=dict(information_date=AS_OF,package="cohort_fx_v1",research_status="PARTIAL",
        implementation_status="complete_subject_to_test_receipt",historical_W1_n=0,historical_W2_n=0,
        scenario_n=len(summaries),new_fitted_parameters=0,
        inherited_lambda="K0 public PIT API; no changed weights or fit policy",reference_basis=BASIS,
        rate_cutoff_by_currency=daily[daily.ccy.isin(FOREIGN)].groupby("ccy").date.max().to_dict(),
        currency_inputs="hypothetical currency mix; 0.56 nonUSD only annual company anchor",
        cohort_rnpl_inputs="unidentified sensitivities, not stock percentages or disclosed booking flow",
        accounting_sources=[SEC_K,SEC_Q],hedge_policy="none_added; absolute reference basis not certified prehedge",
        R_bundle="interface audited; synthetic inputs and historical coefficients not deployed",
        scope="L3 research inputs only; no forecast registration or investment adoption")
    (out/"metadata.json").write_text(json.dumps(metadata,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    hashes=[dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
        for p in sorted(out.iterdir()) if p.is_file()]
    write_csv(pd.DataFrame(hashes),out/"output_checksums.csv")
    print(json.dumps(dict(output=str(out),scenarios=len(summaries),cohort_currency_rows=len(details),
        allocation_rows=len(allocations),adapter_rows=len(adapter),research="PARTIAL",W1_n=0,W2_n=0)))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--fx-bundle",type=Path,help="Optional read-only interface audit dependency; never staged")
    a=p.parse_args();run(a.out.resolve(),a.fx_bundle.resolve() if a.fx_bundle else None)
