"""A2 guide-close signal and executable returns. Rebuild from repository root."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as K
from harness_v1_1 import RUN_DATE
from harness_v1_1 import registry as R

OUT = ROOT / "data/processed/forecast_methods/alpha_a2"
SEED = 20260913
INPUTS = {
    "calendar": "data/processed/forecast_methods/harness/calendar.csv",
    "targets": "data/processed/forecast_methods/harness/targets.csv",
    "ledger": "data/processed/overnight/02_guidance_ledger.csv",
    "merged": "data/processed/overnight/16_consensus_at_print_merged.csv",
    "vintages": "data/processed/forecast_methods/L0/L0_vintage_register.csv",
    "returns": "data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv",
    "kpi": "data/processed/overnight/02_kpi_panel_quarterly.csv",
    "cushion": "data/processed/overnight/02_guidance_cushion_series.csv",
    "kernel": "analysis/src/forecast_methods/kernel_engine_v2/engine.py",
    "scenario": "analysis/src/forecast_methods/kernel_phi_v2/stage_d.py",
    "lane1_cells": "data/processed/forecast_methods/alpha_a/pit_cells.csv",
    "lane1_diagnostic": "data/processed/forecast_methods/alpha_a/post_letter_diagnostic.csv",
}
QCOLS = R.QUANTILE_COLUMNS


def truth(x):
    return str(x).strip().lower() == "true"


def valid_consensus(register, quarter, date, role="pre_guide", metric="revenue", attributed=True):
    """Return audited source row even when unusable; never override quarantine."""
    rows = register[(register.period == quarter) & (register.role == role) & (register.metric == metric)].copy()
    if rows.empty:
        return None, "no_registered_row"
    if role != "current" and len(rows) != 1:
        raise ValueError(f"Ambiguous historical source: {quarter} {role} {metric}")
    rows["stamp"] = pd.to_datetime(rows.as_of_timestamp, errors="coerce")
    row = rows.sort_values("stamp", na_position="first").iloc[-1]
    if not truth(row.pit_usable):
        return row, "pit_usable_false: " + str(row.note)
    if pd.isna(row.stamp):
        return row, "missing_timestamp"
    if row.stamp.normalize() > pd.Timestamp(date).normalize():
        return row, "timestamp_after_origin"
    if role == "current":
        return row, "current_not_historical"
    if attributed and not truth(row.vendor_attributed):
        return row, "vendor_unattributed"
    if not np.isfinite(row.value) or row.value <= 0:
        return row, "invalid_value"
    return row, "available"


def sign_interval(low, high):
    if not np.isfinite([low, high]).all():
        return np.nan
    if low > high:
        raise ValueError("Reversed interval")
    return 1. if low > 0 else -1. if high < 0 else 0.


def wilson(hits, n, level=.95):
    if n == 0:
        return np.nan, np.nan
    z = norm.ppf((1 + level) / 2)
    p = hits/n
    den = 1 + z*z/n
    centre = (p + z*z/(2*n))/den
    half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return centre-half, centre+half


def correlation(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) < 1e-12 or np.ptp(y) < 1e-12:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def block_indices(n, rng, draws=2000, length=2):
    if n <= 0:
        return np.empty((draws, 0), dtype=int)
    starts = rng.integers(0, n, size=(draws, int(np.ceil(n/length))))
    return ((starts[..., None] + np.arange(length)) % n).reshape(draws, -1)[:, :n]


def boot_mean(values, level=.90):
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    if not len(v):
        return 0, np.nan, np.nan, np.nan
    means = v[block_indices(len(v), np.random.default_rng(SEED))].mean(axis=1)
    lo, hi = np.quantile(means, [(1-level)/2, (1+level)/2])
    return len(v), float(v.mean()), float(lo), float(hi)


def boot_corr(x, y):
    a = np.column_stack([x, y]).astype(float)
    a = a[np.isfinite(a).all(axis=1)]
    value = correlation(a[:, 0], a[:, 1])
    vals = [correlation(a[i, 0], a[i, 1]) for i in block_indices(len(a), np.random.default_rng(SEED))]
    vals = np.asarray(vals); vals = vals[np.isfinite(vals)]
    lo, hi = np.quantile(vals, [.025, .975]) if len(vals) else (np.nan, np.nan)
    return value, lo, hi, len(vals)


def permutation_p(signals, labels, draws=9999):
    s, y = np.asarray(signals), np.asarray(labels)
    if not len(s):
        return np.nan
    hits = np.sum(s == y)
    rng = np.random.default_rng(SEED)
    exceed = sum(np.sum(s == rng.permutation(y)) >= hits for _ in range(draws))
    return (exceed + 1)/(draws + 1)


def partial_corr(frame, controls):
    a = frame[["signal_pct", "excess_open_20d_pct", *controls]].dropna().to_numpy(float)
    n = len(a)
    if n < len(controls)+3:
        return n, np.nan, np.nan, "insufficient_complete_cases"
    design = np.column_stack([np.ones(n), a[:, 2:]])
    if np.linalg.matrix_rank(design) < design.shape[1]:
        return n, correlation(a[:, 0], a[:, 1]), np.nan, "rank_deficient_controls"
    residual = a[:, :2] - design @ np.linalg.lstsq(design, a[:, :2], rcond=None)[0]
    return n, correlation(a[:, 0], a[:, 1]), correlation(residual[:, 0], residual[:, 1]), "available"


def ridge_fit(x, y, penalty=1.):
    """OLS intercept and ridge slope shrunk toward one; inputs in percentage points."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 6 or not np.isfinite(np.r_[x, y]).all():
        raise ValueError("Ridge requires six finite prior pairs")
    dx, dy = x-x.mean(), y-y.mean()
    slope = (dx@dy + penalty)/(dx@dx + penalty)
    return float(y.mean()-slope*x.mean()), float(slope)


def forecast(quarter, date, variant):
    as_of = pd.Timestamp(date)+pd.Timedelta(days=1)
    try:
        result = K.kernel_guide(quarter, as_of, variant=variant)
        if pd.Timestamp(result["knowable_from"]) > pd.Timestamp(date):
            raise ValueError("K0 returned an input later than guide close")
        result["quantile_basis"] = "K0 kernel and cushion predictive bootstrap"
        if not all(np.isfinite(result.get(q, np.nan)) for q in QCOLS):
            # K0 cannot estimate lambda dispersion from one seasonal observation.
            # A2's requested cushion residual ladder is conditional on that lambda;
            # it must not be called a full predictive interval.
            ratios = K._cushions(as_of).ratio.to_numpy(float)
            result.update(cushion_only_quantiles(result["point"], ratios))
            result["quantile_basis"] = "empirical cushion-only conditional; kernel dispersion unavailable"
        return result, "available"
    except K.DataUnavailable as exc:
        return {}, str(exc)


def cushion_only_quantiles(point, ratios):
    ratios = np.asarray(ratios, float)
    if len(ratios) == 0 or not np.isfinite(ratios).all() or (ratios <= 0).any():
        raise ValueError("Cushion quantiles require finite positive realised ratios")
    conditional = point*np.median(ratios)/ratios
    return {q:float(np.quantile(conditional, R.QUANTILE_LEVELS[q])) for q in QCOLS}


def build_cells(data):
    targets, register = data["targets"], data["vintages"]
    indexed = targets.set_index("quarter")
    events = data["returns"].set_index("event_date")
    fixed_variant = K.pit_lambda(4, str(RUN_DATE))["variant"]
    rows = []
    for t in targets[targets.quarter.between("2021Q4", "2026Q2")].itertuples():
        d, q = t.guide_date, t.quarter
        printed_q = str(pd.Period(q, freq="Q")-1)
        c, reason = valid_consensus(register, q, d)
        raw_c, _ = valid_consensus(register, q, d, attributed=False)
        cons = float(c.value) if reason == "available" else np.nan
        row = dict(quarter=q, guide_date=d, print_quarter=printed_q, extension=q<"2023Q1",
                   consensus_musd=cons, consensus_status=reason,
                   consensus_register_id=c.register_id if c is not None else "",
                   street_vendor=c.vendor if c is not None else "",
                   street_as_of=c.as_of_timestamp if c is not None else "",
                   vendor_attributed=truth(c.vendor_attributed) if c is not None else False,
                   consensus_source_value=c.value if c is not None else np.nan,
                   guide_mid_musd=t.guide_mid, guide_mid_lo=t.guide_mid-.5, guide_mid_hi=t.guide_mid+.5,
                   actual_gap_pct=100*(t.guide_mid/cons-1),
                   actual_gap_lo=100*((t.guide_mid-.5)/cons-1),
                   actual_gap_hi=100*((t.guide_mid+.5)/cons-1),
                   gbv_q_musd=indexed.loc[printed_q, "gbv_musd"],
                   gbv_q_minus_1_musd=indexed.loc[str(pd.Period(printed_q, freq="Q")-1), "gbv_musd"])
        row["actual_sign"] = sign_interval(row["actual_gap_lo"], row["actual_gap_hi"])
        for name, variant in (("default", None), ("ex_covid", "ex_covid"), ("full_sample", fixed_variant)):
            f, status = forecast(q, d, variant)
            row[name+"_kernel_status"] = status
            row[name+"_kernel_guide_musd"] = f.get("point", np.nan)
            row[name+"_signal_pct"] = 100*(f.get("point", np.nan)/cons-1)
            for key in ("base_musd", "lambda_pct", "variant", "n_train", "knowable_from", "cushion", "cushion_n", "training_quarters", "quantile_basis", *QCOLS):
                value = f.get(key, np.nan)
                row[name+"_"+key] = json.dumps(value) if isinstance(value, list) else value
        row["signal_pct"] = row["default_signal_pct"]
        row["evaluable"] = bool(np.isfinite([row["signal_pct"], row["actual_gap_pct"]]).all())
        row["availability_reason"] = "available" if row["evaluable"] else reason if reason != "available" else row["default_kernel_status"]
        row["engine_as_of"] = str((pd.Timestamp(d)+pd.Timedelta(days=1)).date())
        row["unattributed_sensitivity_gap_pct"] = (100*(t.guide_mid/raw_c.value-1)
             if raw_c is not None and truth(raw_c.pit_usable) and pd.notna(raw_c.as_of_timestamp) else np.nan)
        row["entry_date"] = events.loc[d, "entry_date"] if d in events.index else ""
        for h in (1, 5, 20, 60):
            col = f"excess_open_{h}d_pct"
            row[col] = events.loc[d, col] if d in events.index else np.nan
        for metric, actual_col in (("gbv", "gbv_musd"), ("revenue", "revenue_musd")):
            ap, ap_reason = valid_consensus(register, printed_q, d, role="at_print", metric=metric)
            row[metric+"_consensus_status"] = ap_reason
            row[metric+"_consensus_vendor"] = ap.vendor if ap is not None else ""
            row[metric+"_consensus_stamp"] = ap.as_of_timestamp if ap is not None else ""
            row[metric+"_consensus_register_id"] = ap.register_id if ap is not None else ""
            value = float(ap.value) if ap_reason == "available" else np.nan
            if ap is not None and ap_reason == "available":
                if ap.unit == "busd":
                    value *= 1000
                elif ap.unit != "musd":
                    raise ValueError(f"Unexpected {metric} consensus unit {ap.unit}")
            row[metric+"_consensus_musd"] = value
            row[metric+"_actual_musd"] = indexed.loc[printed_q, actual_col]
            row[metric+"_surprise_pct"] = 100*(row[metric+"_actual_musd"]/value-1)
        rows.append(row)
    cells = pd.DataFrame(rows).sort_values("guide_date").reset_index(drop=True)
    cells["previous_gap_sign"] = cells.actual_sign.shift(1)
    return cells, fixed_variant


def evaluate(cells):
    statistics, returns, controls, ridge = [], [], [], []
    for variant in ("default", "ex_covid", "full_sample"):
        working = cells.copy()
        working["signal_pct"] = working[variant+"_signal_pct"]
        for i, row in working.iterrows():
            prior = working.iloc[:i].dropna(subset=["signal_pct", "actual_gap_pct"])
            if len(prior) >= 6 and np.isfinite(row.signal_pct):
                intercept, slope = ridge_fit(prior.signal_pct, prior.actual_gap_pct)
                ridge.append(dict(variant=variant, quarter=row.quarter, guide_date=row.guide_date, n_train=len(prior),
                                  intercept=intercept, slope=slope, prediction_pct=intercept+slope*row.signal_pct,
                                  actual_gap_pct=row.actual_gap_pct, latest_training_date=prior.guide_date.max()))
        for window, lo in (("W1", "2023Q1"), ("W2", "2024Q1"), ("extension", "2021Q4")):
            w = working[working.quarter.between(lo, "2022Q4" if window == "extension" else "2026Q2")].copy()
            e = w.dropna(subset=["signal_pct", "actual_gap_pct"])
            high = e[e.signal_pct.abs() > 1]
            scored = high[high.actual_sign.abs() == 1]
            hits = int((np.sign(scored.signal_pct) == scored.actual_sign).sum())
            wilson_lo, wilson_hi = wilson(hits, len(scored))
            corr, corr_lo, corr_hi, corr_draws = boot_corr(e.signal_pct, e.actual_gap_pct)
            cn, cr, cp, cs = partial_corr(e, ["gbv_surprise_pct", "actual_gap_pct"])
            nret, mean, meanlo, meanhi = boot_mean(np.sign(high.signal_pct)*high.excess_open_20d_pct)
            condition1 = len(scored) >= 6 and hits/len(scored) >= .70
            condition2 = nret > 0 and mean > 0 and meanlo > 0
            sign_kept = np.isfinite([cr, cp]).all() and cr*cp > 0
            pass_sample = e.dropna(subset=["signal_pct", "excess_open_20d_pct", "gbv_surprise_pct", "actual_gap_pct"])
            unknown_pass_vendor = int(pass_sample.gbv_consensus_vendor.isin(["vendor_not_recorded", "", "nan"]).sum())
            condition3 = bool(sign_kept and unknown_pass_vendor == 0)
            criterion3_status = "provenance_limited" if unknown_pass_vendor else "met" if condition3 else "not_established"
            verdict = ("underpowered" if len(scored)<6 else "pass" if condition1 and condition2 and condition3
                       else "partial" if condition1 else "fail")
            statistics.append(dict(variant=variant, window=window, n_candidates=len(w), n_consensus=w.consensus_musd.notna().sum(),
                 n_kernel=w[variant+"_kernel_guide_musd"].notna().sum(), n_evaluable=len(e), n_high=len(high), n_scored=len(scored),
                 n_ambiguous=len(high)-len(scored), hits=hits, hit_rate=hits/len(scored) if len(scored) else np.nan,
                 wilson95_lo=wilson_lo, wilson95_hi=wilson_hi, permutation_p=permutation_p(np.sign(scored.signal_pct), scored.actual_sign),
                 corr_signal_gap=corr, corr95_lo=corr_lo, corr95_hi=corr_hi, n_finite_corr_draws=corr_draws,
                 n_return20=nret, signed_return20_mean=mean, signed_return20_90lo=meanlo, signed_return20_90hi=meanhi,
                 n_pass_control=cn, control_raw_corr=cr, pass_partial_corr=cp, control_status=cs,
                 condition1=condition1, condition2=condition2, condition3=condition3, condition3_numerical_sign_kept=sign_kept,
                 condition3_status=criterion3_status, n_pass_control_vendor_unrecorded=unknown_pass_vendor, verdict=verdict))
            for name, cols in (("gbv", ["gbv_surprise_pct"]), ("guide_gap", ["actual_gap_pct"]),
                               ("revenue", ["revenue_surprise_pct"]), ("gbv_and_guide_gap", ["gbv_surprise_pct", "actual_gap_pct"]),
                               ("all_three", ["gbv_surprise_pct", "actual_gap_pct", "revenue_surprise_pct"])):
                n, raw, partial, status = partial_corr(e, cols)
                complete = e.dropna(subset=["signal_pct", "excess_open_20d_pct", *cols])
                unknown_vendor = int(complete.gbv_consensus_vendor.isin(["vendor_not_recorded", "", "nan"]).sum()) if "gbv_surprise_pct" in cols else 0
                controls.append(dict(variant=variant, window=window, controls=name, n=n, raw_corr_same_sample=raw,
                                     partial_corr=partial, sign_kept=raw*partial>0 if np.isfinite([raw,partial]).all() else False,
                                     status=status, control_columns="|".join(cols), n_gbv_vendor_unrecorded=unknown_vendor,
                                     vendor_provenance="L0 usable/attributed flags; GBV vendor name unrecorded" if unknown_vendor else "named_vendors_or_no_GBV_control"))
            strategies = {"kernel": w.signal_pct, "guide_gap_only": w.actual_gap_pct,
                          "zero": pd.Series(0., index=w.index), "previous_surprise_sign": w.previous_gap_sign}
            for strategy, signal in strategies.items():
                for threshold in ("all", "abs_signal_gt1"):
                    # Previous-sign rule has unit position, so the threshold refers to the current kernel signal.
                    select = (signal.notna() & (w.signal_pct.abs()>1)) if threshold != "all" else signal.notna()
                    for side in ("positive", "negative", "direction_adjusted"):
                        mask = select & (signal>0 if side=="positive" else signal<0 if side=="negative" else signal.notna())
                        for horizon in (1, 5, 20, 60):
                            vals = w.loc[mask, f"excess_open_{horizon}d_pct"].copy()
                            if side == "direction_adjusted":
                                vals *= np.sign(signal.loc[mask])
                            n, m, lower, upper = boot_mean(vals)
                            returns.append(dict(variant=variant, window=window, strategy=strategy, subset=threshold, side=side,
                                                horizon=horizon, n=n, mean_pct=m, bootstrap90_lo=lower, bootstrap90_hi=upper))
    return pd.DataFrame(statistics), pd.DataFrame(returns), pd.DataFrame(controls), pd.DataFrame(ridge)


def live_scenarios(register):
    term = K.term_structure(str(RUN_DATE))
    f = term[term.quarter == "2026Q4"].iloc[0]
    if f.status != "conditional_scenario":
        raise ValueError("Expected explicitly conditional Q4 live scenario")
    rows = register[(register.role=="current") & (register.period=="2026Q4") & (register.metric=="revenue")].copy()
    rows = rows[rows.pit_usable.map(truth) & rows.vendor_attributed.map(truth)]
    rows = rows[pd.to_datetime(rows.as_of_timestamp) <= pd.Timestamp(RUN_DATE)]
    family = lambda v: "LSEG-family" if "Alpha Vantage" in v or "Yahoo" in v or "LSEG" in v else "S&P" if "S&P" in v else "Zacks" if "Zacks" in v else v
    rows["vendor_family"] = rows.vendor.map(family)
    rows["preference"] = rows.vendor.str.contains("Alpha Vantage").astype(int)
    chosen = rows.sort_values(["as_of_timestamp", "preference"]).groupby("vendor_family", sort=True).tail(1)
    chosen = chosen[chosen.vendor_family.isin(["LSEG-family", "S&P", "Zacks"])]
    out = []
    for r in chosen.itertuples():
        row = dict(quarter="2026Q4", vintage_date=str(RUN_DATE), event_date="2026-11-05", scenario=True,
                   vendor_family=r.vendor_family, street_vendor=r.vendor, street_as_of=r.as_of_timestamp,
                   register_id=r.register_id, consensus_musd=r.value, kernel_guide_musd=f.guide_mid_musd,
                   signal_pct=100*(f.guide_mid_musd/r.value-1), n_train=int(f.n_train),
                   status=f.status, caveat=f.caveat)
        for q in QCOLS:
            row[q] = f.get("guide_"+q, np.nan)
        out.append(row)
    if len(out) != 3 or len(set(r["vendor_family"] for r in out)) != 3:
        raise ValueError("Expected exactly three independent live consensus families")
    return pd.DataFrame(out)


def registry_rows(cells, live, fixed_variant):
    out = []
    # Consensus is not an input to guide dollars; kernel-valid rows register even if gap cannot be evaluated.
    for r in cells[cells.quarter >= "2023Q1"].to_dict("records"):
        for replay, prefix in (("PIT", "default"), ("full_sample", "full_sample")):
            point = r[prefix+"_kernel_guide_musd"]
            if not np.isfinite(point):
                continue
            for window in (["W1", "W2"] if r["quarter"] >= "2024Q1" else ["W1"]):
                row = dict(method="alpha-a2", object="guide_mid_next_q", target="guide_mid", quarter=r["quarter"],
                           vintage_date=r["guide_date"], horizon_q=pd.Period(r["quarter"], freq="Q").ordinal-pd.Period(r["guide_date"],freq="Q").ordinal,
                           point=point, window=window, prior_basis=replay, n_params=2, n_train=int(r[prefix+"_n_train"]),
                           knowable_from=r[prefix+"_knowable_from"], spec_id="nested_PIT" if replay=="PIT" else "retrospective_fixed_"+fixed_variant,
                           notes="Guide-close via K0 d+1; " + str(r[prefix+"_quantile_basis"]) + "; " + ("nested PIT" if replay=="PIT" else "retrospective selection"))
                row.update({q:r[prefix+"_"+q] for q in QCOLS})
                out.append(row)
    r = live[live.vendor_family=="LSEG-family"].iloc[0]
    for replay in ("PIT", "full_sample"):
        row = dict(method="alpha-a2", object="guide_mid_next_q", target="guide_mid", quarter="2026Q4", vintage_date=str(RUN_DATE),
                   horizon_q=pd.Period("2026Q4", freq="Q").ordinal-pd.Period(RUN_DATE,freq="Q").ordinal,
                   point=r.kernel_guide_musd, window="LIVE", prior_basis=replay, n_params=4, n_train=int(r.n_train),
                   knowable_from="2026-09-11", spec_id="conditional_RNPL_ledger_scenario",
                   notes="5 Nov guide scenario; unknown Q3 GBV from K0 conditional ledger; 2 extra regression parameters")
        row.update({q:r[q] for q in QCOLS})
        out.append(row)
    return pd.DataFrame(out)


def make_figure(cells):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    e = cells[(cells.quarter>="2023Q1") & cells.evaluable]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    for ax, y, label in ((axes[0], "actual_gap_pct", "Actual guide / pre-guide Street − 1 (%)"),
                         (axes[1], "excess_open_20d_pct", "Next-open 20-day ABNB − QQQ (pp)")):
        ax.axhline(0, color="#9ca3af", lw=.8); ax.axvline(0, color="#9ca3af", lw=.8)
        ax.axvspan(-1, 1, color="#e5e7eb", alpha=.5)
        ax.scatter(e.signal_pct, e[y], color="#255f85", s=32)
        for r in e.itertuples():
            ax.annotate(r.quarter, (r.signal_pct, getattr(r, y)), fontsize=7, xytext=(3,3), textcoords="offset points")
        ax.set(xlabel="Kernel guide / pre-guide Street − 1 (%)", ylabel=label)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"A2: guide-close PIT signal, W1 n={len(e)}; gray band |S| ≤ 1pp", fontsize=12)
    fig.savefig(OUT / "signal_gap_returns.png", dpi=180)
    plt.close(fig)


def reconcile(cells, data):
    lane = data["lane1_cells"]
    diagnostic = data["lane1_diagnostic"]
    out = cells[["quarter", "evaluable", "consensus_status", "default_kernel_status", "default_kernel_guide_musd"]].merge(
        lane[["quarter", "consensus_status", "kernel_status"]], on="quarter", suffixes=("_a2", "_lane1"), validate="one_to_one")
    out = out.merge(diagnostic[["quarter", "kernel_guide_musd"]], on="quarter", how="left", validate="one_to_one")
    out["diagnostic_difference_musd"] = out.default_kernel_guide_musd-out.kernel_guide_musd
    return out


def run(register=True):
    start = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    data = {key:pd.read_csv(ROOT/path, comment="#") for key,path in INPUTS.items() if path.endswith(".csv")}
    cells, fixed_variant = build_cells(data)
    cells.to_csv(OUT/"cells.csv", index=False)
    stats, returns, controls, ridge = evaluate(cells)
    for frame, name in ((stats,"statistics"),(returns,"conditional_returns"),(controls,"controls"),(ridge,"ridge_expanding")):
        frame.to_csv(OUT/(name+".csv"), index=False)
    live = live_scenarios(data["vintages"])
    live.to_csv(OUT/"live_november_guide_scenario.csv", index=False)
    reconcile(cells, data).to_csv(OUT/"lane1_reconciliation.csv", index=False)
    make_figure(cells)
    reg = registry_rows(cells, live, fixed_variant)
    clean = R.validate_registry_frame(reg)
    clean.to_csv(OUT/"registry_preview.csv", index=False)
    registry_path = R.register(reg) if register else None
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS.values()}
    audit = dict(run_date=str(RUN_DATE), seed=SEED, runtime_seconds=time.perf_counter()-start,
                 fixed_full_sample_variant=fixed_variant, register_rows=len(reg),
                 registry_path=str(registry_path), inputs_sha256=hashes,
                 notes="Only PIT default enters verdict; full_sample uses retrospective variant choice with PIT coefficients; scorers owned by parent")
    (OUT/"audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(stats[(stats.variant=="default") & stats.window.isin(["W1","W2"])].to_string(index=False))
    print(live[["vendor_family","street_as_of","consensus_musd","kernel_guide_musd","signal_pct"]].to_string(index=False))
    print(json.dumps({k:v for k,v in audit.items() if k!="inputs_sha256"}, indent=2))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-register", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run(not args.no_register))
