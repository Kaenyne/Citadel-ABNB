"""Joint effective GBV allocation: identification, variance and PIT replay.

Every reconstructed A cell is model-conditional, never an observed reservation.
Run from the repository root; existing inputs and output directories are read-only.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import linprog, minimize

ROOT = Path(__file__).resolve().parents[5]
SOURCES = {
    "kpi": ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv",
    "calendar": ROOT / "data/processed/forecast_methods/harness/calendar.csv",
    "k2": ROOT / "data/processed/forecast_methods/kernel_leadtime_v2/K2_recommended_prior.csv",
    "prereg": ROOT / "docs/revenue-forecast-strategy/05_backtests/JOINT_COHORT_QUANT_PREREG_v1.md",
    "prereg_addendum": ROOT / "docs/revenue-forecast-strategy/05_backtests/JOINT_COHORT_QUANT_PREREG_ADDENDUM_v1.md",
    "pr60_flights": ROOT / "data/processed/govdata_v2/qtd75_pit.csv",
}
WINDOWS = {"W1": "2023Q1", "W2": "2024Q1"}
TAILS = {"tail34": [3, 4], "tail3": [3], "tail38": list(range(3, 9))}
GROUPS = ["same_quarter", "one_earlier", "two_earlier", "older_finite_tail"]
SEED = 20260915


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def qshift(q, k):
    return str(pd.Period(q, freq="Q") + k)


def load_inputs():
    raw = pd.read_csv(SOURCES["kpi"])
    p = raw[["quarter", "gbv_musd", "revenue_musd"]].copy()
    p["quarter"] = p.quarter.map(lambda q: f"20{q[2:]}Q{q[0]}")
    c = pd.read_csv(SOURCES["calendar"])
    dates = c.set_index("print_quarter").print_date
    p["print_date"] = pd.to_datetime(p.quarter.map(dates))
    p["season"] = p.quarter.str[-1].astype(int)
    p["year"] = p.quarter.str[:4].astype(int)
    if p.quarter.duplicated().any() or p.print_date.isna().any():
        raise ValueError("Quarter uniqueness/publication dates failed")
    if not np.isfinite(p[["gbv_musd", "revenue_musd"]]).all().all() or (p[["gbv_musd", "revenue_musd"]] <= 0).any().any():
        raise ValueError("Positive finite corporate dollars required")
    return p.sort_values("quarter").reset_index(drop=True), c


def features(panel, tail):
    f = panel.copy()
    lookup = f.set_index("quarter").gbv_musd.to_dict()
    for k in range(max(tail) + 1):
        f[f"g{k}"] = [lookup.get(qshift(q, -k), np.nan) for q in f.quarter]
    f["gtail"] = f[[f"g{k}" for k in tail]].mean(axis=1, skipna=False)
    return f.dropna(subset=["g0", "g1", "g2", "gtail"]).reset_index(drop=True)


def xvalues(rows):
    return rows[["g0", "g1", "g2", "gtail"]].to_numpy(float)


def time_weights(rows, multiplicity=None):
    weight = np.zeros(len(rows))
    for s in range(1, 5):
        ix = np.where(rows.season.to_numpy() == s)[0]
        weight[ix] = 2.0 ** (-np.arange(len(ix)-1, -1, -1) / 2)
    if multiplicity is not None:
        weight *= np.asarray(multiplicity)
    return weight


def scale_fit(rows, phi, weights=None):
    x, y = xvalues(rows), rows.revenue_musd.to_numpy(float)
    weights = time_weights(rows) if weights is None else weights
    base = x @ np.asarray(phi)
    if (base <= 0).any():
        raise ValueError("Positive exposure base required")
    lam = np.zeros(4)
    for s in range(1, 5):
        ix = rows.season.to_numpy() == s
        if weights[ix].sum() <= 0:
            raise ValueError(f"Missing training season {s}")
        lam[s-1] = np.average(y[ix] / base[ix], weights=weights[ix])
    pred = base * lam[rows.season.to_numpy()-1]
    return lam, pred


def fit_shape(rows, multiplicity=None):
    weights = time_weights(rows, multiplicity)
    y = rows.revenue_musd.to_numpy(float)
    def objective(phi):
        _, pred = scale_fit(rows, phi, weights)
        return np.average((pred/y-1)**2, weights=weights)
    candidates = []
    for start in ([.25]*4, [.5, .3, .15, .05], [0, 2/3, 1/3, 0]):
        opt = minimize(objective, start, method="SLSQP", bounds=[(0, 1)]*4,
                       constraints={"type": "eq", "fun": lambda w: w.sum()-1},
                       options={"maxiter": 350, "ftol": 1e-13})
        if opt.success and np.isfinite(opt.fun) and abs(opt.x.sum()-1) < 1e-7:
            candidates.append(opt)
    if not candidates:
        raise RuntimeError("All three prespecified SLSQP starts failed")
    opt = min(candidates, key=lambda o: o.fun)
    phi = np.maximum(opt.x, 0); phi /= phi.sum()
    lam, pred = scale_fit(rows, phi, weights)
    return {"phi": phi, "lambda": lam, "prediction": pred,
            "weighted_relative_rmse_pct": 100*np.sqrt(opt.fun),
            "relative_rmse_pct": 100*np.sqrt(np.mean((pred/y-1)**2)),
            "n": len(rows), "n_params": 7, "successful_starts": len(candidates)}


def allocation(rows, fit, tail, observed_scale=False):
    """Use exactly one dollar matrix for backward shares and forward rates."""
    records = []
    x = xvalues(rows)
    basis = x @ fit["phi"]
    for i, r in enumerate(rows.itertuples()):
        lam = r.revenue_musd / basis[i] if observed_scale else fit["lambda"][r.season-1]
        total = lam * basis[i]
        for k in [0, 1, 2] + tail:
            group = k if k < 3 else 3
            exposure_weight = fit["phi"][group] / (len(tail) if k >= 3 else 1)
            gbv = getattr(r, f"g{k}")
            dollars = lam * exposure_weight * gbv
            records.append(dict(quarter=r.quarter, booking_quarter=qshift(r.quarter, -k),
                                season=r.season, year=r.year, lag=k, group=GROUPS[group],
                                reported_booking_quarter_gbv_musd=gbv,
                                allocated_revenue_musd=dollars,
                                backward_share=dollars/total,
                                actual_revenue_attribution_share=dollars/r.revenue_musd,
                                unallocated_residual_share=(r.revenue_musd-total)/r.revenue_musd,
                                effective_forward_fee_per_net_gbv=dollars/gbv,
                                allocated_column_musd=total,
                                actual_revenue_musd=r.revenue_musd,
                                column_residual_musd=r.revenue_musd-total,
                                basis="realized_total_conditional_allocation" if observed_scale else "seasonal_model_allocation",
                                max_lag_assumed=max(tail), older_than_support="unobserved_assumed_zero_in_this_spec"))
    return pd.DataFrame(records)


def grouped_allocation(a):
    keys = ["quarter", "season", "year", "group"]
    # For tail, sum A/G over different booking-quarter denominators: labelled coefficient sum,
    # not a single cohort conversion. Per-booking-quarter rates remain in the detailed matrix.
    return a.groupby(keys, sort=True).agg(
        allocated_revenue_musd=("allocated_revenue_musd", "sum"),
        backward_share=("backward_share", "sum"),
        effective_coefficient_sum=("effective_forward_fee_per_net_gbv", "sum")).reset_index()


def grid_profile(rows, optimum):
    phis = []
    for a in range(21):
        for b in range(21-a):
            for c in range(21-a-b):
                phis.append(np.array([a,b,c,20-a-b-c])/20)
    phis += [optimum["phi"], np.array([0, 2/3, 1/3, 0])]
    profiles = []
    for i, phi in enumerate(phis):
        lam, pred = scale_fit(rows, phi)
        rmse = 100*np.sqrt(np.mean((pred/rows.revenue_musd.to_numpy()-1)**2))
        profiles.append((i, phi, lam, rmse))
    minimum = min(r[3] for r in profiles)
    kept = [r for r in profiles if r[3] <= minimum + .25 + 1e-10]
    details, bounds = [], []
    x = xvalues(rows)
    all_shares, all_rates = [], []
    for i, phi, lam, rmse in kept:
        share = x*phi / (x@phi)[:,None]
        rate = (rows.revenue_musd.to_numpy()/(x@phi))[:,None]*phi
        all_shares.append(share); all_rates.append(rate)
        details.append(dict(shape_id=i, rmse_pct=rmse,
                            **{f"weight_{j}": phi[j] for j in range(4)},
                            **{f"lambda_Q{s}": lam[s-1] for s in range(1,5)}))
    for i, row in enumerate(rows.itertuples()):
        for k, group in enumerate(GROUPS):
            sh = np.array(all_shares)[:,i,k]*100
            co = np.array(all_rates)[:,i,k]*100
            bounds.append(dict(quarter=row.quarter,season=row.season,group=group,
                               n_nearfit=len(kept), n_grid=len(phis),
                               share_low_pct=sh.min(),share_high_pct=sh.max(),share_width_pp=np.ptp(sh),
                               effective_low_pct=co.min(),effective_high_pct=co.max(),effective_width_pp=np.ptp(co),
                               nearfit_minimum_rmse_pct=minimum,rmse_tolerance_pp=.25))
    # Count a deterministic greedy packing, not an estimate of all possible solutions.
    packed = []
    for share in all_shares:
        if all(np.max(np.abs(share-old)) >= .10-1e-10 for old in packed):
            packed.append(share)
    return pd.DataFrame(details), pd.DataFrame(bounds), len(packed)


def parameter_uncertainty(rows, fit, draws=200):
    rng = np.random.default_rng(SEED)
    years = np.sort(rows.year.unique())
    x = xvalues(rows)
    point_shares = x*fit["phi"]/(x@fit["phi"])[:,None]
    boot = []; rejected=0; attempts=0
    while len(boot) < draws:
        attempts += 1
        sampled = rng.choice(years, len(years), replace=True)
        counts = {year: np.sum(sampled == year) for year in years}
        mult = rows.year.map(counts).to_numpy()
        if len(set(rows.loc[mult>0,"season"])) < 4:
            rejected += 1; continue
        if attempts > draws*10:
            raise RuntimeError("Insufficient bootstrap draws with all seasons")
        bfit = fit_shape(rows, mult)
        share = x*bfit["phi"]/(x@bfit["phi"])[:,None]
        # Coefficients based on bootstrapped seasonal scale, not original actuals.
        rate = bfit["lambda"][rows.season.to_numpy()-1,None]*bfit["phi"]
        boot.append((bfit,share,rate))
    samples, intervals = [], []
    for i,(bfit,_,_) in enumerate(boot):
        samples.append(dict(draw=i,**{f"weight_{k}":bfit["phi"][k] for k in range(4)},
                            **{f"lambda_Q{s}":bfit["lambda"][s-1] for s in range(1,5)}))
    sh = np.stack([v[1] for v in boot]); rates=np.stack([v[2] for v in boot])
    for s in range(1,5):
        ix=rows.season.to_numpy()==s
        for k,g in enumerate(GROUPS):
            a=100*sh[:,ix,k].mean(axis=1); b=100*rates[:,ix,k].mean(axis=1)
            intervals.append(dict(season=s,group=g,n_quarters=int(ix.sum()),n_year_clusters=len(years),
                                  n_draws=draws,rejected_missing_seasons=rejected,
                                  share_p05_pct=np.quantile(a,.05),share_p95_pct=np.quantile(a,.95),
                                  share_width_pp=np.quantile(a,.95)-np.quantile(a,.05),
                                  effective_p05_pct=np.quantile(b,.05),effective_p95_pct=np.quantile(b,.95),
                                  effective_width_pp=np.quantile(b,.95)-np.quantile(b,.05)))
    deletion=[]
    for year in years:
        train=rows[rows.year!=year].reset_index(drop=True)
        if len(train.season.unique())<4:
            deletion.append(dict(deleted_year=int(year),status="missing_season",n_train=len(train)));continue
        dfit=fit_shape(train)
        dsh=x*dfit["phi"]/(x@dfit["phi"])[:,None]
        for s in range(1,5):
            ix=rows.season.to_numpy()==s
            for k,g in enumerate(GROUPS):
                shift=100*(dsh[ix,k].mean()-point_shares[ix,k].mean())
                deletion.append(dict(deleted_year=int(year),season=s,group=g,n_train=len(train),
                                     status="ok",share_shift_pp=shift,abs_share_shift_pp=abs(shift)))
    return pd.DataFrame(samples),pd.DataFrame(intervals),pd.DataFrame(deletion)


def temporal_stats(matrix):
    grouped=grouped_allocation(matrix)
    stats=[]; covariance=[]; identities=[]
    for s in range(1,5):
        data=grouped[grouped.season==s]
        for group in GROUPS:
            a=data[data.group==group]
            for metric,scale in [("backward_share",100),("effective_coefficient_sum",100)]:
                value=a[metric]*scale
                stats.append(dict(season=s,group=group,metric=metric,n=len(value),mean_pct=value.mean(),
                                  sd_pp=value.std(ddof=1),variance_pp2=value.var(ddof=1),range_pp=np.ptp(value)))
        dollars=data.pivot(index="quarter",columns="group",values="allocated_revenue_musd")[GROUPS]
        cov=dollars.cov()
        for g1 in GROUPS:
            for g2 in GROUPS:
                covariance.append(dict(season=s,group_a=g1,group_b=g2,n=len(dollars),covariance_musd2=cov.loc[g1,g2]))
        diag=np.trace(cov.to_numpy()); total=dollars.sum(axis=1).var(ddof=1)
        off=cov.to_numpy().sum()-diag
        identities.append(dict(season=s,n=len(dollars),total_variance_musd2=total,
                               diagonal_sum_musd2=diag,offdiagonal_sum_musd2=off,
                               reconciliation_error_musd2=total-diag-off))
    return pd.DataFrame(stats),pd.DataFrame(covariance),pd.DataFrame(identities)


def lp_problem(rows, lags, tolerance, prior=None):
    # Single season. Normalize each target row by its actual revenue for conditioning.
    z=rows[[f"g{k}" for k in lags]].to_numpy()/rows.revenue_musd.to_numpy()[:,None]
    upper=np.vstack([z,-z]); bound=np.r_[np.full(len(z),1+tolerance),np.full(len(z),-(1-tolerance))]
    if prior is not None:
        # K2 bounds constrain model backward column shares, not forward beta.
        for i in range(len(z)):
            for k in range(4):
                obj=z[i]*np.array([j==k if k<3 else j>=3 for j in lags])
                lo,hi=prior[k]
                upper=np.vstack([upper,obj-hi*z[i],lo*z[i]-obj]);bound=np.r_[bound,0,0]
    return z,upper,bound


def ratio_bounds(z,upper,bound,target,mask):
    # Charnes-Cooper: y=beta/(z_target beta), u=1/(z_target beta).
    # Works because positive bounded target total is guaranteed by revenue constraints.
    p=z.shape[1]
    aub=np.c_[upper,-bound]
    aeq=np.r_[z[target],0][None,:]
    objective=np.r_[z[target]*mask,0]
    solutions=[]
    for sign in [1,-1]:
        opt=linprog(sign*objective,A_ub=aub,b_ub=np.zeros(len(bound)),A_eq=aeq,b_eq=[1],bounds=(0,None),method="highs")
        if not opt.success:
            raise RuntimeError(f"Fractional LP failed: {opt.message}")
        value=float(objective@opt.x)
        if opt.x[-1]<=0:
            raise RuntimeError("Nonpositive Charnes-Cooper scale")
        solutions.append((value,opt.x[:p]/opt.x[-1]))
    return solutions


def identification(panel, k2):
    allrows=features(panel,list(range(3,9)))
    bounds=[];design=[];witnesses=[];conditional=[]
    for window,lower in WINDOWS.items():
        data=allrows[allrows.quarter>=lower].reset_index(drop=True)
        for maxlag,tol in itertools.product([3,4,8],[.005,.01,.02]):
            lags=list(range(maxlag+1))
            for s in range(1,5):
                rows=data[data.season==s].reset_index(drop=True)
                z,a,b=lp_problem(rows,lags,tol)
                feasible=linprog(np.zeros(len(lags)),A_ub=a,b_ub=b,bounds=(0,None),method="highs")
                design.append(dict(window=window,season=s,max_lag=maxlag,tolerance_pct=100*tol,
                                   n=len(rows),n_params=len(lags),rank=int(np.linalg.matrix_rank(z)),
                                   nullity=len(lags)-np.linalg.matrix_rank(z),feasible=bool(feasible.success)))
                if not feasible.success:continue
                for i,r in enumerate(rows.itertuples()):
                    for g,name in enumerate(GROUPS):
                        mask=np.array([j==g if g<3 else j>=3 for j in lags],int)
                        lo,hi=ratio_bounds(z,a,b,i,mask)
                        beta_ext=[]
                        for sign in [1,-1]:
                            opt=linprog(sign*mask,A_ub=a,b_ub=b,bounds=(0,None),method="highs")
                            if not opt.success:raise RuntimeError(opt.message)
                            beta_ext.append(float(mask@opt.x))
                        bounds.append(dict(window=window,quarter=r.quarter,season=s,group=name,max_lag=maxlag,
                                           tolerance_pct=100*tol,n_season=len(rows),share_low_pct=lo[0]*100,
                                           share_high_pct=hi[0]*100,share_width_pp=(hi[0]-lo[0])*100,
                                           effective_low_pct=beta_ext[0]*100,effective_high_pct=beta_ext[1]*100))
                        if maxlag==8 and tol==.01 and g==0:
                            for label,(_,beta) in [("minimum_same",lo),("maximum_same",hi)]:
                                for j,r2 in enumerate(rows.itertuples()):
                                    alloc=z[j]*beta*r2.revenue_musd
                                    for k in lags:
                                        witnesses.append(dict(window=window,optimized_quarter=r.quarter,witness=label,
                                                              quarter=r2.quarter,booking_quarter=qshift(r2.quarter,-k),lag=k,
                                                              allocated_revenue_musd=alloc[k],backward_share=alloc[k]/alloc.sum(),
                                                              effective_forward_fee_per_net_gbv=beta[k],
                                                              actual_revenue_musd=r2.revenue_musd,
                                                              residual_musd=r2.revenue_musd-alloc.sum()))
        # Deliberately stale assumed share restriction, not an eligibility upgrade.
        for mapping in ["melbourne_calendar_months","original_northern_season_analogy"]:
            for s in range(1,5):
                rows=data[data.season==s].reset_index(drop=True)
                priorrow=k2.loc[k2.melbourne_months=={1:"1-2-3",2:"4-5-6",3:"7-8-9",4:"10-11-12"}[s]].iloc[0] if mapping=="melbourne_calendar_months" else k2.loc[k2.northern_stay_quarter==f"Q{s}"].iloc[0]
                for widening in [0,.1]:
                    prior=[(max(0,priorrow[f"phi{k}_lo"]-widening),min(1,priorrow[f"phi{k}_hi"]+widening)) for k in range(4)]
                    z,a,b=lp_problem(rows,list(range(9)),.01,prior)
                    feasible=linprog(np.zeros(9),A_ub=a,b_ub=b,bounds=(0,None),method="highs")
                    for i,r in enumerate(rows.itertuples()):
                        for g,name in enumerate(GROUPS):
                            rec=dict(window=window,mapping=mapping,widening_pp=100*widening,quarter=r.quarter,season=s,group=name,
                                     feasible=bool(feasible.success),n_season=len(rows),basis="stale_K2_accommodation_share_assumption")
                            if feasible.success:
                                mask=np.array([j==g if g<3 else j>=3 for j in range(9)],int)
                                lo,hi=ratio_bounds(z,a,b,i,mask)
                                rec.update(share_low_pct=100*lo[0],share_high_pct=100*hi[0],share_width_pp=100*(hi[0]-lo[0]))
                            conditional.append(rec)
    return pd.DataFrame(bounds),pd.DataFrame(design),pd.DataFrame(witnesses),pd.DataFrame(conditional)


def forecast_gbv(panel, target, asof):
    """Only published values enter; target GBV cannot enter even if supplied."""
    known=panel[panel.print_date<=pd.Timestamp(asof)].sort_values("quarter")
    lookup=known.set_index("quarter").gbv_musd.to_dict()
    if not lookup:raise ValueError("No published GBV")
    latest=known.quarter.iloc[-1]
    if target<=latest:raise ValueError("Forecast target must be unprinted")
    denominator=lookup.get(qshift(latest,-4))
    if denominator is None or denominator<=0:raise ValueError("No year-ago growth denominator")
    growth=lookup[latest]/denominator
    q=qshift(latest,1)
    while q<=target:
        base=lookup.get(qshift(q,-4))
        if base is None or base<=0:raise ValueError("No seasonal-naive GBV base")
        lookup[q]=base*growth
        q=qshift(q,1)
    return lookup[target],growth-1,str(known.print_date.max().date())


def baseline_forecast(known,target,lag1_forecast=None):
    lookup=known.set_index("quarter").gbv_musd.to_dict()
    season=int(target[-1]);ratios=[]
    for r in known.itertuples():
        a=lookup.get(qshift(r.quarter,-1));b=lookup.get(qshift(r.quarter,-2))
        if r.season==season and a is not None and b is not None:
            ratios.append(r.revenue_musd/(2/3*a+1/3*b))
    if not ratios:raise ValueError("No baseline same-season training")
    lam=np.average(ratios,weights=2**(-np.arange(len(ratios)-1,-1,-1)/2))
    g1=lookup.get(qshift(target,-1),lag1_forecast)
    if g1 is None:raise ValueError("Unprinted lag1 GBV requires an origin-dated forecast")
    return lam*(2/3*g1+1/3*lookup[qshift(target,-2)]),len(ratios),lam


def cushion_at_origin(known,calendar):
    guide=calendar.dropna(subset=["next_quarter_guided","guide_mid"]).set_index("next_quarter_guided").guide_mid
    rows=[]
    for r in known.itertuples():
        if r.quarter in guide.index:
            rows.append((r.quarter,r.revenue_musd/guide.loc[r.quarter]-1))
    if not rows:raise ValueError("No completed guided-quarter cushion observations")
    return float(np.mean([r[1] for r in rows[-8:]])),len(rows[-8:])


def pit_replay(panel,calendar):
    records=[];skipped=[]
    c=calendar.set_index("print_quarter")
    for tail_name,tail in TAILS.items():
        for target in panel.loc[panel.quarter>="2023Q1","quarter"]:
            prev=qshift(target,-1);origin_quarter=qshift(target,-2)
            asof=pd.Timestamp(c.loc[origin_quarter,"print_date"])
            known=panel[panel.print_date<=asof].copy()
            train=features(known,tail)
            if len(train)<8 or len(train.season.unique())<4:
                skipped.append(dict(spec=tail_name,quarter=target,origin=str(asof.date()),n_train=len(train),
                                    reason="requires >=8 complete published rows and all seasons"));continue
            fit=fit_shape(train)
            g0,growth,knowable=forecast_gbv(panel,target,asof)
            g1,_,_=forecast_gbv(panel,prev,asof)
            lookup=known.set_index("quarter").gbv_musd.to_dict()
            x=np.array([g0,g1,lookup[qshift(target,-2)],np.mean([lookup[qshift(target,-k)] for k in tail])])
            lam=fit["lambda"][int(target[-1])-1]
            candidate=(x@fit["phi"])*lam
            actual=panel.loc[panel.quarter==target].iloc[0]
            oracle_x=x.copy();oracle_x[0]=actual.gbv_musd
            oracle_x[1]=panel.loc[panel.quarter==prev,"gbv_musd"].iloc[0]
            oracle=(oracle_x@fit["phi"])*lam
            base,n_base,base_lam=baseline_forecast(known,target,g1)
            cushion,n_cushion=cushion_at_origin(known,calendar)
            actual_guide=float(c.loc[prev,"guide_mid"])
            records.append(dict(spec=tail_name,quarter=target,year=int(target[:4]),origin=str(asof.date()),
                                guide_event_date=str(pd.Timestamp(c.loc[prev,"print_date"]).date()),
                                information_set="after_release_t_minus_2_predicting_next_release_guide",
                                knowable_from=knowable,max_training_quarter=train.quarter.max(),
                                n_train=len(train),n_params=7,n_baseline_same_season=n_base,
                                gbv_forecast_musd=g0,gbv_actual_musd=actual.gbv_musd,
                                lag1_gbv_forecast_musd=g1,lag1_gbv_actual_musd=oracle_x[1],
                                gbv_known_yoy_pct=100*growth,revenue_actual_musd=actual.revenue_musd,
                                guide_actual_musd=actual_guide,cushion_pct=100*cushion,n_cushion=n_cushion,
                                candidate_revenue_musd=candidate,baseline_revenue_musd=base,oracle_revenue_musd=oracle,
                                candidate_guide_musd=candidate/(1+cushion),baseline_guide_musd=base/(1+cushion),
                                oracle_guide_musd=oracle/(1+cushion),candidate_lambda_pct=100*lam,
                                baseline_lambda_pct=100*base_lam,
                                **{f"weight_{k}":fit["phi"][k] for k in range(4)}))
    return pd.DataFrame(records),pd.DataFrame(skipped)


def score_replay(replay):
    scores=[];deletions=[]
    def score(d,model,target):
        e=d[f"{model}_{target}_musd"]-d[f"{target}_actual_musd"]
        return dict(n=len(d),rmse_musd=np.sqrt(np.mean(e**2)),mae_musd=np.mean(abs(e)),bias_musd=np.mean(e))
    for spec in replay.spec.unique():
        for window,lower in WINDOWS.items():
            d=replay[(replay.spec==spec)&(replay.quarter>=lower)]
            if d.empty:continue
            for target in ["revenue","guide"]:
                b=score(d,"baseline",target)
                for model in ["candidate","baseline","oracle"]:
                    row=score(d,model,target)
                    scores.append(dict(spec=spec,window=window,target=target,model=model,**row,
                                       ratio_to_baseline=row["rmse_musd"]/b["rmse_musd"],
                                       basis="PIT_replay" if model!="oracle" else "not_tradable_realized_target_GBV_oracle"))
            for unit in ["year","quarter"]:
                for val in d[unit].unique():
                    subset=d[d[unit]!=val]
                    if subset.empty:continue
                    ratio=score(subset,"candidate","guide")["rmse_musd"]/score(subset,"baseline","guide")["rmse_musd"]
                    deletions.append(dict(spec=spec,window=window,deleted_unit=unit,deleted_value=val,n=len(subset),guide_rmse_ratio=ratio))
    return pd.DataFrame(scores),pd.DataFrame(deletions)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1")
    parser.add_argument("--bootstrap-draws",type=int,default=200)
    args=parser.parse_args();out=args.out.resolve()
    if out.exists():raise FileExistsError(f"Choose a NEW output directory: {out}")
    if args.bootstrap_draws<1:raise ValueError("Positive bootstrap draw count required")
    before={k:sha(v) for k,v in SOURCES.items()}
    panel,calendar=load_inputs();k2=pd.read_csv(SOURCES["k2"]);k2=k2[k2.weighting=="value"]
    out.mkdir(parents=True)
    tables={};fits=[];profiles_summary=[]
    for window,lower in WINDOWS.items():
        print(f"Retrospective {window}: fit, profile, bootstrap",flush=True)
        rows=features(panel,TAILS["tail34"])
        rows=rows[rows.quarter>=lower].reset_index(drop=True)
        fit=fit_shape(rows)
        fits.append(dict(window=window,**{k:v for k,v in fit.items() if k not in ["phi","lambda","prediction"]},
                         **{f"weight_{k}":fit["phi"][k] for k in range(4)},
                         **{f"lambda_Q{s}_pct":100*fit["lambda"][s-1] for s in range(1,5)}))
        matrix=allocation(rows,fit,TAILS["tail34"])
        realized=allocation(rows,fit,TAILS["tail34"],observed_scale=True)
        detail,profile,packing=grid_profile(rows,fit)
        boot,intervals,deleted=parameter_uncertainty(rows,fit,args.bootstrap_draws)
        stats,cov,covcheck=temporal_stats(realized)
        profiles_summary.append(dict(window=window,n=len(rows),n_nearfit=len(detail),
                                     greedy_10pp_separated_shapes=packing,max_share_width_pp=profile.share_width_pp.max(),
                                     max_bootstrap_share_width_pp=intervals.share_width_pp.max(),
                                     max_year_deletion_shift_pp=deleted.get("abs_share_shift_pp",pd.Series(dtype=float)).max()))
        for key,table in {"model_matrix":matrix,"realized_conditional_matrix":realized,"nearfit_shapes":detail,
                          "nearfit_bounds":profile,"bootstrap_draws":boot,"bootstrap_intervals":intervals,
                          "parameter_year_deletion":deleted,"conditional_temporal_variance":stats,
                          "conditional_dollar_covariance":cov,"covariance_identity":covcheck}.items():
            table.insert(0,"window",window)
            tables.setdefault(key,[]).append(table)
    for key,parts in tables.items():pd.concat(parts,ignore_index=True).to_csv(out/f"{key}.csv",index=False)
    pd.DataFrame(fits).to_csv(out/"retrospective_fit.csv",index=False)
    pd.DataFrame(profiles_summary).to_csv(out/"parsimonious_identification_summary.csv",index=False)
    print("Flexible LP identification and stale-K2 conditional stress",flush=True)
    bounds,design,witness,conditional=identification(panel,k2)
    bounds.to_csv(out/"flexible_identification_bounds.csv",index=False)
    design.to_csv(out/"flexible_design_rank.csv",index=False)
    witness.to_csv(out/"flexible_witness_matrices.csv",index=False)
    conditional.to_csv(out/"stale_k2_conditional_bounds.csv",index=False)
    print("PIT forecast replay and score stability",flush=True)
    replay,skipped=pit_replay(panel,calendar)
    scores,deletions=score_replay(replay)
    replay.to_csv(out/"pit_predictions.csv",index=False);skipped.to_csv(out/"pit_skipped_origins.csv",index=False)
    scores.to_csv(out/"pit_scores.csv",index=False);deletions.to_csv(out/"pit_score_deletions.csv",index=False)
    main_scores=scores[(scores.spec=="tail34")&(scores.target=="guide")&(scores.model=="candidate")]
    promotion=bool(len(main_scores)==2 and (main_scores.n>=8).all() and (main_scores.ratio_to_baseline<=.9).all() and
                   (deletions.loc[deletions.spec=="tail34","guide_rmse_ratio"]<1).all())
    verdict={"physical_cohort_evidence_gate":"FAIL_no_current_direct_booking_recognition_fee_cancellation_panel",
             "headline_current_corporate_cohort_shares_eligible":False,"forecast_promotion_pass":promotion,
             "n_primary_candidate_parameters":7,"flexible_main_parameters":36,
             "bootstrap_draws":args.bootstrap_draws,"seed":SEED,
             "share_policy_max_width_pp":10,"share_policy_max_deletion_pp":5,
             "unobserved":"gross booking survival, RNPL causality, tail beyond finite support, fee-cohort representativeness",
             "forecast_policy":"guide RMSE<=.90 baseline both windows,n>=8,no deletion ratio>=1",
             "parsimonious_summary":profiles_summary}
    (out/"verdict.json").write_text(json.dumps(verdict,indent=2),encoding="utf-8")
    after={k:sha(v) for k,v in SOURCES.items()}
    if before!=after:raise AssertionError("Existing input hash changed")
    manifest={"inputs":{k:{"path":str(SOURCES[k].relative_to(ROOT)),"sha256":v} for k,v in before.items()},
              "code_sha256":sha(__file__),"python_version":sys.version,
              "outputs":{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(verdict,indent=2),flush=True)
    print(f"Wrote {out}",flush=True)


if __name__=="__main__":main()
