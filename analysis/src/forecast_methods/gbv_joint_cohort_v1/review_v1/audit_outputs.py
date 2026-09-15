"""Independent saved-output audit; does not import the candidate's functions."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from economic_contract import joint_variance

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data/processed/forecast_methods/gbv_joint_cohort_v1"
GROUPS = ["same_quarter", "one_earlier", "two_earlier", "older_finite_tail"]


def qshift(q, k):
    return str(pd.Period(q, freq="Q") + k)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def audit(core_dir, diagnostics_dir, out):
    core_dir, out = Path(core_dir).resolve(), Path(out).resolve()
    if not out.is_relative_to(BASE / "review_v1") or out.exists():
        raise ValueError("Use a NEW child of review_v1")
    out.mkdir(parents=True)
    checks = []

    def eq(name, actual, expected, tolerance=1e-7):
        a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
        error = float(np.max(np.abs(a-b))) if a.size else 0.
        passed = a.shape == b.shape and np.allclose(a, b, atol=tolerance, rtol=1e-10, equal_nan=True)
        checks.append(dict(check=name, passed=bool(passed), max_abs_error=error))

    def yes(name, value):
        checks.append(dict(check=name, passed=bool(value), max_abs_error=0. if value else 1.))

    def read(name):
        return pd.read_csv(core_dir / (name + ".csv"))

    manifest = json.loads((core_dir / "manifest.json").read_text())
    for name, expected in manifest["outputs"].items():
        yes("core output hash " + name, sha(core_dir/name) == expected)
    for name, row in manifest["inputs"].items():
        yes("core input hash " + name, sha(ROOT/row["path"]) == row["sha256"])
    yes("core code hash", sha(ROOT/"analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/run.py") == manifest["code_sha256"])
    raw = pd.read_csv(ROOT/"data/processed/overnight/02_kpi_panel_quarterly.csv")
    raw["quarter"] = raw.quarter.map(lambda q: f"20{q[2:]}Q{q[0]}")
    p = raw.set_index("quarter")
    calendar = pd.read_csv(ROOT/"data/processed/forecast_methods/harness/calendar.csv")
    cal = calendar.set_index("print_quarter")
    dates = pd.to_datetime(cal.print_date)
    fits = read("retrospective_fit").set_index("window")
    matrices = {name: read(name) for name in ["model_matrix", "realized_conditional_matrix"]}
    for name, matrix in matrices.items():
        for (window, quarter), d in matrix.groupby(["window", "quarter"]):
            d = d.sort_values("lag")
            fit = fits.loc[window]
            phi = fit[[f"weight_{k}" for k in range(4)]].to_numpy(float)
            y = float(p.loc[quarter, "revenue_musd"])
            g = np.array([p.loc[qshift(quarter, -k), "gbv_musd"] for k in range(5)])
            weight = np.r_[phi[:3], phi[3]/2, phi[3]/2]
            lam = fit[f"lambda_Q{quarter[-1]}_pct"] / 100
            amount = g*weight*lam
            if name == "realized_conditional_matrix":
                amount = amount/amount.sum()*y
            label = f"{name}:{window}:{quarter}:"
            eq(label+"lags", d.lag, np.arange(5))
            eq(label+"booking-denominators", d.reported_booking_quarter_gbv_musd, g)
            eq(label+"dollars", d.allocated_revenue_musd, amount)
            eq(label+"backward", d.backward_share, amount/amount.sum())
            eq(label+"actual-revenue-share", d.actual_revenue_attribution_share, amount/y)
            eq(label+"forward", d.effective_forward_fee_per_net_gbv, amount/g)
            eq(label+"residual", d.column_residual_musd, np.repeat(y-amount.sum(), 5))
            eq(label+"share-plus-residual", d.actual_revenue_attribution_share.sum()+d.unallocated_residual_share.iloc[0], 1.)
            yes(label+"nonnegative", d.allocated_revenue_musd.ge(-1e-10).all())

    # Independent within-season sample statistics and the complete covariance matrix.
    conditional = matrices["realized_conditional_matrix"]
    temporal, covariance, identities = read("conditional_temporal_variance"), read("conditional_dollar_covariance"), read("covariance_identity")
    grouped = conditional.groupby(["window", "quarter", "season", "group"]).agg(
        dollars=("allocated_revenue_musd", "sum"), share=("backward_share", "sum"),
        coefficient_sum=("effective_forward_fee_per_net_gbv", "sum")).reset_index()
    for (window, season), d in grouped.groupby(["window", "season"]):
        dollar_matrix = d.pivot(index="quarter", columns="group", values="dollars")[GROUPS]
        independent = joint_variance(dollar_matrix.to_numpy())
        identity = identities.loc[(identities.window==window)&(identities.season==season)].iloc[0]
        for own, col in [("diagonal", "diagonal_sum_musd2"), ("off_diagonal", "offdiagonal_sum_musd2"), ("direct_total_variance", "total_variance_musd2")]:
            eq(f"covariance-total:{window}:{season}:{own}", identity[col], independent[own], 1e-5)
        for i, ga in enumerate(GROUPS):
            for j, gb in enumerate(GROUPS):
                cell = covariance.loc[(covariance.window==window)&(covariance.season==season)&(covariance.group_a==ga)&(covariance.group_b==gb)].iloc[0]
                eq(f"covariance:{window}:{season}:{ga}:{gb}", cell.covariance_musd2, independent["covariance"][i,j], 1e-5)
            for actual_col, output_col in [("share", "backward_share"), ("coefficient_sum", "effective_coefficient_sum")]:
                values = d.loc[d.group==ga, actual_col].to_numpy()*100
                cell = temporal.loc[(temporal.window==window)&(temporal.season==season)&(temporal.group==ga)&(temporal.metric==output_col)].iloc[0]
                eq(f"temporal:{window}:{season}:{ga}:{output_col}",
                   [cell.n, cell.mean_pct, cell.sd_pp, cell.variance_pp2, cell.range_pp],
                   [len(values), values.mean(), values.std(ddof=1), values.var(ddof=1), np.ptp(values)])

    # Near-fit shapes: independent dollar exposure, conditional shares and effective-rate ranges.
    shapes, bounds = read("nearfit_shapes"), read("nearfit_bounds")
    for (window, quarter), d in bounds.groupby(["window", "quarter"]):
        selected = shapes.loc[shapes.window==window]
        phi = selected[[f"weight_{k}" for k in range(4)]].to_numpy(float)
        g = np.array([p.loc[qshift(quarter,-k),"gbv_musd"] for k in range(5)])
        x = np.r_[g[:3], g[3:].mean()]
        share = phi*x/(phi@x)[:,None]*100
        rate = phi*(float(p.loc[quarter,"revenue_musd"])/(phi@x))[:,None]*100
        for k, group in enumerate(GROUPS):
            cell = d.loc[d.group==group].iloc[0]
            eq(f"nearfit:{window}:{quarter}:{group}",
               [cell.n_nearfit, cell.share_low_pct, cell.share_high_pct, cell.share_width_pp, cell.effective_low_pct, cell.effective_high_pct],
               [len(selected), share[:,k].min(), share[:,k].max(), np.ptp(share[:,k]), rate[:,k].min(), rate[:,k].max()])

    # Bound witness cells are evaluated directly, not by reusing the author's LP assembly.
    witnesses = read("flexible_witness_matrices")
    broad = read("flexible_identification_bounds")
    for (window, optimized, witness, quarter), d in witnesses.groupby(["window", "optimized_quarter", "witness", "quarter"]):
        y = float(p.loc[quarter,"revenue_musd"])
        g = np.array([p.loc[b,"gbv_musd"] for b in d.booking_quarter])
        amount = d.effective_forward_fee_per_net_gbv.to_numpy()*g
        label = f"LP:{window}:{optimized}:{witness}:{quarter}:"
        eq(label+"dollars", d.allocated_revenue_musd, amount)
        eq(label+"share", d.backward_share, amount/amount.sum())
        yes(label+"revenue-feasibility", abs(amount.sum()/y-1)<=.010000001)
        yes(label+"nonnegative", (amount>=-1e-9).all())
        if optimized==quarter:
            row = broad.loc[(broad.window==window)&(broad.quarter==quarter)&(broad.group=="same_quarter")&(broad.max_lag==8)&(broad.tolerance_pct==1)].iloc[0]
            bound = row.share_low_pct if witness=="minimum_same" else row.share_high_pct
            eq(label+"attained-endpoint", d.loc[d.lag==0,"backward_share"].iloc[0]*100, bound)

    replay, scores, deletion = read("pit_predictions"), read("pit_scores"), read("pit_score_deletions")
    tails = {"tail34":[3,4], "tail3":[3], "tail38":list(range(3,9))}
    for r in replay.itertuples():
        origin = pd.Timestamp(r.origin)
        known_quarters = sorted(q for q in p.index if dates.loc[q]<=origin)
        known = p.loc[known_quarters]
        latest = known_quarters[-1]
        yes(f"PIT:{r.spec}:{r.quarter}:origin", latest==qshift(r.quarter,-2) and origin==dates.loc[latest] and pd.Timestamp(r.guide_event_date)>origin)
        yes(f"PIT:{r.spec}:{r.quarter}:guide-target", cal.loc[qshift(r.quarter,-1),"next_quarter_guided"]==r.quarter)
        lookup = known.gbv_musd.to_dict()
        growth = lookup[latest]/lookup[qshift(latest,-4)]
        g1 = lookup[qshift(r.quarter,-5)]*growth
        g0 = lookup[qshift(r.quarter,-4)]*growth
        phi = np.array([getattr(r,f"weight_{k}") for k in range(4)])
        tail = tails[r.spec]
        x = np.array([g0,g1,lookup[qshift(r.quarter,-2)],np.mean([lookup[qshift(r.quarter,-k)] for k in tail])])
        train = [q for q in known_quarters if all(qshift(q,-k) in lookup for k in range(max(tail)+1))]
        seasonal = [q for q in train if q[-1]==r.quarter[-1]]
        ratios = []
        for q in seasonal:
            gx=np.array([lookup[qshift(q,-k)] for k in [0,1,2]]+[np.mean([lookup[qshift(q,-k)] for k in tail])])
            ratios.append(known.loc[q,"revenue_musd"]/(gx@phi))
        lam = np.average(ratios,weights=2.**(-np.arange(len(ratios)-1,-1,-1)/2))
        baseline_season = [q for q in known_quarters if q[-1]==r.quarter[-1] and all(qshift(q,-k) in lookup for k in [1,2])]
        base_ratio=[known.loc[q,"revenue_musd"]/(2/3*lookup[qshift(q,-1)]+1/3*lookup[qshift(q,-2)]) for q in baseline_season]
        base_lam=np.average(base_ratio,weights=2.**(-np.arange(len(base_ratio)-1,-1,-1)/2))
        candidate=x@phi*lam
        baseline=(2/3*g1+1/3*lookup[qshift(r.quarter,-2)])*base_lam
        cushion=[]
        for q in known_quarters:
            guides=calendar.loc[calendar.next_quarter_guided.eq(q)].dropna(subset=["guide_mid"])
            if len(guides):
                yes(f"PIT:{r.spec}:{r.quarter}:cushion-guide-available:{q}", pd.Timestamp(guides.print_date.iloc[0])<=origin)
                cushion.append(known.loc[q,"revenue_musd"]/guides.guide_mid.iloc[0]-1)
        c=np.mean(cushion[-8:])
        eq(f"PIT:{r.spec}:{r.quarter}:forecast", [r.n_train,r.gbv_forecast_musd,r.lag1_gbv_forecast_musd,r.candidate_lambda_pct,r.baseline_lambda_pct,r.cushion_pct,r.candidate_revenue_musd,r.baseline_revenue_musd,r.candidate_guide_musd,r.baseline_guide_musd],
           [len(train),g0,g1,100*lam,100*base_lam,100*c,candidate,baseline,candidate/(1+c),baseline/(1+c)], 1e-6)
        eq(f"PIT:{r.spec}:{r.quarter}:actuals", [r.revenue_actual_musd,r.guide_actual_musd],
           [p.loc[r.quarter,"revenue_musd"],cal.loc[qshift(r.quarter,-1),"guide_mid"]])
    for r in scores.itertuples():
        d=replay.loc[(replay.spec==r.spec)&replay.quarter.ge("2023Q1" if r.window=="W1" else "2024Q1")]
        e=d[f"{r.model}_{r.target}_musd"]-d[f"{r.target}_actual_musd"]
        b=d[f"baseline_{r.target}_musd"]-d[f"{r.target}_actual_musd"]
        rmse=np.sqrt(np.mean(e**2))
        eq(f"score:{r.spec}:{r.window}:{r.target}:{r.model}", [r.n,r.rmse_musd,r.mae_musd,r.bias_musd,r.ratio_to_baseline],
           [len(d),rmse,np.abs(e).mean(),e.mean(),rmse/np.sqrt(np.mean(b**2))])
    for r in deletion.itertuples():
        d=replay.loc[(replay.spec==r.spec)&replay.quarter.ge("2023Q1" if r.window=="W1" else "2024Q1")]
        d=d.loc[d[r.deleted_unit].astype(str).ne(str(r.deleted_value))]
        ec=d.candidate_guide_musd-d.guide_actual_musd;eb=d.baseline_guide_musd-d.guide_actual_musd
        eq(f"score-delete:{r.spec}:{r.window}:{r.deleted_unit}:{r.deleted_value}", [r.n,r.guide_rmse_ratio], [len(d),np.sqrt(np.mean(ec**2)/np.mean(eb**2))])

    if diagnostics_dir:
        dd=Path(diagnostics_dir).resolve()
        dm=json.loads((dd/"manifest.json").read_text())
        for name,expected in dm["outputs"].items():yes("diagnostic output hash "+name,sha(dd/name)==expected)
        forecast=pd.read_csv(dd/"live_nearfit_forecasts.csv")
        identity=pd.read_csv(dd/"nearfit_covariance_identity.csv")
        for (window,target),d in forecast.groupby(["window","target"]):
            parts=d[[f"contribution_{k}_musd" for k in range(4)]].to_numpy()
            eq(f"future-parts:{window}:{target}",parts.sum(axis=1),d.revenue_musd)
            eq(f"future-shares:{window}:{target}",parts/parts.sum(axis=1)[:,None]*100,d[[f"share_{k}_pct" for k in range(4)]])
            v=joint_variance(parts);r=identity.loc[(identity.window==window)&(identity.target==target)].iloc[0]
            eq(f"future-covariance:{window}:{target}",[r.total_variance_musd2,r.diagonal_sum_musd2,r.offdiagonal_sum_musd2],
               [v["direct_total_variance"],v["diagonal"],v["off_diagonal"]],1e-5)
        fw=pd.read_csv(dd/"forward_booking_rows.csv")
        for r in fw.itertuples():
            d=conditional.loc[(conditional.window==r.window)&(conditional.booking_quarter==r.booking_quarter)]
            amount=d.allocated_revenue_musd.sum();b=p.loc[r.booking_quarter,"gbv_musd"]
            eq(f"forward-row:{r.window}:{r.booking_quarter}",[r.cumulative_allocated_fee_musd,r.observed_effective_fee_per_net_gbv], [amount,amount/b])
            yes(f"forward-censor:{r.window}:{r.booking_quarter}", r.right_censored==(d.lag.max()<4) and r.left_censored==(d.lag.min()>0))

    pd.DataFrame(checks).to_csv(out/"checks.csv",index=False)
    record={"checks":len(checks),"passed":sum(r["passed"] for r in checks),"imports_candidate_functions":False,
            "scope":"independent source arithmetic, allocation, covariance, near-fit ranges, LP witnesses, forecast chronology/levels, matched scores and all evaluation deletions",
            "bound_sha256":{str((core_dir/"manifest.json").relative_to(ROOT)):sha(core_dir/"manifest.json"),
                            str(Path(__file__).relative_to(ROOT)):sha(__file__)}}
    if diagnostics_dir:record["bound_sha256"][str((Path(diagnostics_dir).resolve()/"manifest.json").relative_to(ROOT))]=sha(Path(diagnostics_dir)/"manifest.json")
    (out/"receipt.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record))
    if record["checks"]!=record["passed"]:raise AssertionError("Independent checks failed; retained output identifies each row")


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--core",required=True);parser.add_argument("--diagnostics");parser.add_argument("--out",required=True)
    args=parser.parse_args();audit(args.core,args.diagnostics,args.out)
