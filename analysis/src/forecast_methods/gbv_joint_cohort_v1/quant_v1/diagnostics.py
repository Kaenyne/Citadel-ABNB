"""Preregistered small diagnostics; requires completed immutable core output."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import run as core
LINEAGE=core.ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/flight_lineage_v1/flight_vintage_checks.csv"


def paired_uncertainty(replay, draws=2000):
    rng=np.random.default_rng(core.SEED)
    rows=[]
    for spec in replay.spec.unique():
        for window,lower in core.WINDOWS.items():
            data=replay[(replay.spec==spec)&(replay.quarter>=lower)].copy()
            years=data.year.unique()
            ratios=[];deltas=[]
            for _ in range(draws):
                selected=rng.choice(years,len(years),replace=True)
                b=pd.concat([data[data.year==y] for y in selected])
                ec=(b.candidate_guide_musd-b.guide_actual_musd).to_numpy()
                eb=(b.baseline_guide_musd-b.guide_actual_musd).to_numpy()
                ratios.append(np.sqrt(np.mean(ec**2)/np.mean(eb**2)))
                deltas.append(np.mean(ec**2-eb**2))
            rows.append(dict(spec=spec,window=window,n=len(data),n_year_clusters=len(years),n_draws=draws,
                             ratio_p05=np.quantile(ratios,.05),ratio_p95=np.quantile(ratios,.95),
                             loss_difference_p05_musd2=np.quantile(deltas,.05),loss_difference_p95_musd2=np.quantile(deltas,.95),
                             interpretation="conditional paired cluster bootstrap; few independent years"))
    return pd.DataFrame(rows)


def flight_source():
    f=pd.read_csv(core.SOURCES["pr60_flights"])
    lineage=pd.read_csv(LINEAGE)
    f=f.merge(lineage[["quarter","committed_utc","commit_full"]],on="quarter",how="left",validate="one_to_one")
    f["quarter"]=f.quarter.map(lambda q:f"20{q[2:]}Q{q[0]}")
    f["commit_date"]=pd.to_datetime(f.commit_date)
    f["committed_utc"]=pd.to_datetime(f.committed_utc,utc=True)
    if f.committed_utc.isna().any():raise ValueError("Missing exact commit timestamp")
    if f.quarter.duplicated().any():raise ValueError("Duplicate quarterly flight vintages")
    return f


def eligible_flight(flights, origin, latest_company_q):
    # Date-only company origins: conservative UTC-midnight gate for external commits.
    # This refuses any same-day commit, even if it may precede the after-close letter.
    cutoff=pd.Timestamp(origin)
    cutoff=cutoff.tz_localize("UTC") if cutoff.tzinfo is None else cutoff.tz_convert("UTC")
    f=flights[flights.committed_utc<=cutoff].copy()
    f=f[(f.days_cur_present>=75)&np.isfinite(f.eu40_flt_da_yoy)]
    if f.empty:raise ValueError("No eligible historical flight commit")
    f=f.sort_values(["quarter","commit_date"])
    row=f.iloc[-1]
    age=pd.Period(latest_company_q,freq="Q").ordinal-pd.Period(row.quarter,freq="Q").ordinal
    if age>2:raise ValueError("Flight feature more than two quarters stale")
    # A flight quarter may be later than latest company quarter if already publicly committed.
    return row


def flight_training(panel,calendar,flights,asof):
    known=panel[panel.print_date<=pd.Timestamp(asof)].copy()
    lookup=known.set_index("quarter").gbv_musd.to_dict()
    dates=calendar.set_index("print_quarter").print_date
    records=[]
    for r in known.itertuples():
        prev=core.qshift(r.quarter,-1)
        if any(q not in lookup for q in [prev,core.qshift(prev,-4),core.qshift(r.quarter,-4)]):continue
        origin=pd.Timestamp(dates.loc[prev])
        try:f=eligible_flight(flights,origin,prev)
        except ValueError:continue
        last_growth=lookup[prev]/lookup[core.qshift(prev,-4)]-1
        actual_growth=r.gbv_musd/lookup[core.qshift(r.quarter,-4)]-1
        records.append(dict(target=r.quarter,origin=str(origin.date()),flight_quarter=f.quarter,
                            flight_commit_date=str(f.commit_date.date()),outcome_available=str(r.print_date.date()),
                            flight_commit_utc=f.committed_utc.isoformat(),
                            x=f.eu40_flt_da_yoy/100-last_growth,y=actual_growth-last_growth))
    return pd.DataFrame(records)


def flight_ablation(panel,calendar,replay):
    flights=flight_source();rows=[];skip=[];training=[]
    for r in replay[replay.spec=="tail34"].itertuples():
        origin=pd.Timestamp(r.origin);known=panel[panel.print_date<=origin].copy()
        latest=known.quarter.max();lookup=known.set_index("quarter").gbv_musd.to_dict()
        tr=flight_training(panel,calendar,flights,origin)
        try:
            current=eligible_flight(flights,origin,latest)
            if len(tr)<6:raise ValueError("fewer than six eligible dated training pairs")
            denominator=float(np.sum(tr.x**2))
            if denominator<=1e-12:raise ValueError("degenerate flight predictor")
            beta=float(np.clip(np.sum(tr.x*tr.y)/denominator,-2,2))
            growth=lookup[latest]/lookup[core.qshift(latest,-4)]-1
            adjusted=growth+beta*(current.eu40_flt_da_yoy/100-growth)
            if adjusted<=-1:raise ValueError("nonpositive adjusted GBV forecast")
        except ValueError as exc:
            skip.append(dict(quarter=r.quarter,origin=r.origin,n_training_pairs=len(tr),reason=str(exc)));continue
        for record in tr.to_dict("records"):training.append(dict(evaluation_target=r.quarter,**record))
        q=core.qshift(latest,1)
        while q<=r.quarter:
            lookup[q]=lookup[core.qshift(q,-4)]*(1+adjusted)
            q=core.qshift(q,1)
        x=np.array([lookup[r.quarter],lookup[core.qshift(r.quarter,-1)],lookup[core.qshift(r.quarter,-2)],
                    np.mean([lookup[core.qshift(r.quarter,-k)] for k in [3,4]])])
        phi=np.array([getattr(r,f"weight_{k}") for k in range(4)])
        prediction=x@phi*r.candidate_lambda_pct/100
        base,_,_=core.baseline_forecast(known,r.quarter,lookup[core.qshift(r.quarter,-1)])
        rows.append(dict(quarter=r.quarter,year=r.year,origin=r.origin,flight_quarter=current.quarter,
                         flight_commit_date=str(current.commit_date.date()),source_commit=current.commit,
                         flight_commit_utc=current.committed_utc.isoformat(),
                         n_training_pairs=len(tr),slope=beta,extra_parameter_count=1,gbv_growth_pct=100*adjusted,
                         candidate_revenue_musd=prediction,candidate_guide_musd=prediction/(1+r.cushion_pct/100),
                         flight_baseline_guide_musd=base/(1+r.cushion_pct/100),
                         noflight_candidate_guide_musd=r.candidate_guide_musd,
                         noflight_baseline_guide_musd=r.baseline_guide_musd,
                         guide_actual_musd=r.guide_actual_musd,revenue_actual_musd=r.revenue_actual_musd,
                         source_qualification="inherited stored historical commit; raw mirror absent; states completeness unrecertified"))
    frame=pd.DataFrame(rows);scores=[]
    if len(frame):
        for window,lower in core.WINDOWS.items():
            d=frame[frame.quarter>=lower]
            for name in ["candidate","flight_baseline","noflight_candidate","noflight_baseline"]:
                e=d[f"{name}_guide_musd"]-d.guide_actual_musd
                ref=d.noflight_baseline_guide_musd-d.guide_actual_musd
                scores.append(dict(window=window,model=name,n=len(d),rmse_musd=np.sqrt(np.mean(e**2)),
                                   ratio_to_same_origin_noflight_baseline=np.sqrt(np.mean(e**2)/np.mean(ref**2))))
    return frame,pd.DataFrame(skip),pd.DataFrame(training),pd.DataFrame(scores)


def live_sensitivity(panel,calendar,nearfit):
    origin=panel.print_date.max()
    known=panel[panel.print_date<=origin];latest=known.quarter.max()
    initial=known.set_index("quarter").gbv_musd.to_dict()
    cushion,_=core.cushion_at_origin(known,calendar)
    allrows=[];summaries=[]
    for window in core.WINDOWS:
        shapes=nearfit[nearfit.window==window]
        for target in ["2026Q3","2026Q4","2027Q1","2027Q2"]:
            lookup=initial.copy()
            for q in pd.period_range(core.qshift(latest,1),target,freq="Q"):
                value,_,_=core.forecast_gbv(panel,str(q),origin)
                lookup[str(q)]=value
            x=np.array([lookup[target],lookup[core.qshift(target,-1)],lookup[core.qshift(target,-2)],
                        np.mean([lookup[core.qshift(target,-k)] for k in [3,4]])])
            subset=[]
            for r in shapes.itertuples():
                phi=np.array([getattr(r,f"weight_{k}") for k in range(4)])
                lam=getattr(r,f"lambda_Q{target[-1]}")
                dollars=x*phi*lam;total=dollars.sum()
                record=dict(window=window,target=target,origin=str(origin.date()),shape_id=r.shape_id,
                            guide_status="already_issued_implied_guide_diagnostic" if target==core.qshift(latest,1) else "conditional_future_guide_sensitivity",
                            revenue_musd=total,guide_musd=total/(1+cushion),
                            **{f"contribution_{k}_musd":dollars[k] for k in range(4)},
                            **{f"share_{k}_pct":100*dollars[k]/total for k in range(4)})
                subset.append(record);allrows.append(record)
            d=pd.DataFrame(subset)
            summaries.append(dict(window=window,target=target,n_shapes=len(d),
                                  guide_status="already_issued_implied_guide_diagnostic" if target==core.qshift(latest,1) else "conditional_future_guide_sensitivity",
                                  revenue_low_musd=d.revenue_musd.min(),revenue_high_musd=d.revenue_musd.max(),
                                  revenue_range_musd=np.ptp(d.revenue_musd),
                                  guide_low_musd=d.guide_musd.min(),guide_high_musd=d.guide_musd.max(),
                                  guide_range_musd=np.ptp(d.guide_musd),
                                  same_share_low_pct=d.share_0_pct.min(),same_share_high_pct=d.share_0_pct.max(),
                                  basis="conditional nearfit model sensitivity; not forecast interval or live promotion"))
    return pd.DataFrame(allrows),pd.DataFrame(summaries)


def nearfit_covariance(frame):
    cells=[];checks=[]
    for (window,target),d in frame.groupby(["window","target"]):
        columns=[f"contribution_{k}_musd" for k in range(4)]
        cov=d[columns].cov().to_numpy()
        for a in range(4):
            for b in range(4):
                cells.append(dict(window=window,target=target,n_shapes=len(d),group_a=core.GROUPS[a],group_b=core.GROUPS[b],
                                  covariance_musd2=cov[a,b],basis="unweighted nearfit-grid sensitivity; not probability distribution"))
        diag=np.trace(cov);off=cov.sum()-diag;total=d.revenue_musd.var(ddof=1)
        checks.append(dict(window=window,target=target,n_shapes=len(d),total_variance_musd2=total,
                           diagonal_sum_musd2=diag,offdiagonal_sum_musd2=off,
                           reconciliation_error_musd2=total-diag-off))
    return pd.DataFrame(cells),pd.DataFrame(checks)


def forward_rows(matrix):
    records=[]
    for (window,bq),d in matrix.groupby(["window","booking_quarter"]):
        denominator=d.reported_booking_quarter_gbv_musd.iloc[0]
        if not np.allclose(d.reported_booking_quarter_gbv_musd,denominator):raise AssertionError("Cohort denominator mismatch")
        observed=sorted(d.lag.unique())
        records.append(dict(window=window,booking_quarter=bq,reported_net_gbv_musd=denominator,
                            cumulative_allocated_fee_musd=d.allocated_revenue_musd.sum(),
                            observed_effective_fee_per_net_gbv=d.allocated_revenue_musd.sum()/denominator,
                            min_lag_in_window=min(observed),max_lag_in_window=max(observed),
                            n_recognition_quarters=len(d),
                            missing_within_support=",".join(str(k) for k in range(5) if k not in observed),
                            right_censored=max(observed)<4,left_censored=min(observed)>0,
                            tail_beyond4="unobserved",basis="conditional accounting allocation,not survival"))
    return pd.DataFrame(records)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--core",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve()
    if out.exists():raise FileExistsError("Output directory must be new")
    panel,calendar=core.load_inputs()
    replay=pd.read_csv(args.core/"pit_predictions.csv")
    shapes=pd.read_csv(args.core/"nearfit_shapes.csv")
    matrix=pd.read_csv(args.core/"realized_conditional_matrix.csv")
    outputs={"paired_forecast_uncertainty":paired_uncertainty(replay),"forward_booking_rows":forward_rows(matrix)}
    a,b,c,d=flight_ablation(panel,calendar,replay)
    outputs.update(pr60_flight_predictions=a,pr60_flight_skipped=b,pr60_flight_training_pairs=c,pr60_flight_scores=d)
    a,b=live_sensitivity(panel,calendar,shapes)
    outputs.update(live_nearfit_forecasts=a,live_nearfit_sensitivity=b)
    c,d=nearfit_covariance(a)
    outputs.update(nearfit_contribution_covariance=c,nearfit_covariance_identity=d)
    out.mkdir(parents=True)
    for name,frame in outputs.items():frame.to_csv(out/f"{name}.csv",index=False)
    (out/"evidence_status.json").write_text(json.dumps({"physical_current_corporate_cohort_measurement":"UNAVAILABLE",
          "clarification":"Core evidence gate uses FAIL_no_current_direct... as a policy gate failure; it is data unavailability, not an empirical rejection of actual cohort stability.",
          "cushion":"arithmetic trailing-eight mean of actual revenue/issued guide minus1,known at origin; same for both methods; earlier GE package used median",
          "flight_cutoff":"exact commit UTC timestamp <= date-only origin UTC midnight; conservative same-day exclusion",
          "live_Q3_2026_guide":"already issued; implied-guide diagnostic only"},indent=2),encoding="utf-8")
    manifest={"code_sha256":core.sha(__file__),"core_code_sha256":core.sha(core.__file__),
              "inputs":{p.name:core.sha(p) for p in args.core.iterdir() if p.is_file()},
              "flight_source_sha256":core.sha(core.SOURCES["pr60_flights"]),
              "flight_lineage_sha256":core.sha(LINEAGE),
              "outputs":{p.name:core.sha(p) for p in out.iterdir()}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(outputs["paired_forecast_uncertainty"].to_string(index=False))
    print(outputs["pr60_flight_scores"].to_string(index=False))
    print(outputs["live_nearfit_sensitivity"].to_string(index=False))


if __name__=="__main__":main()
