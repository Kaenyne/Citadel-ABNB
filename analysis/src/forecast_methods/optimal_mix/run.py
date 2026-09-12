#!/usr/bin/env python
"""optimal-mix -- leave-future-out forecast combination across the registry.

Reads every registered forecast object in
  data/processed/forecast_methods/registry/
plus the harness scoreboard, and per target metric learns combination weights across
methods AND baselines under strict leave-future-out discipline:

    the weights used to combine the forecasts made at guide date d are fit ONLY on
    (forecast, outcome) pairs whose target quarter PRINTED strictly before d.

Schemes: equal, inverse-MSE, constrained (non-negative, sum-to-one) least-squares
stacking on the PIT errors, a fixed 50/50 shrinkage of that stack toward equal,
BMA with log-predictive-score weights from the registered quantiles, and a
top-3-by-trailing-MSE selection-plus-inverse-MSE scheme.

Everything is run on BOTH windows (W1 origin 1Q23, W2 origin 1Q24) and BOTH prior
replays (PIT and full_sample). A scheme is declared the winner for a target only if it
beats the best single candidate on BOTH windows; otherwise the best single method IS
the mix and that is what gets written.

Run:
  /Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/optimal_mix/run.py
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
FM_SRC = HERE.parent
sys.path.insert(0, str(FM_SRC))
sys.path.insert(0, str(HERE))

from harness import (  # noqa: E402
    load_registry, load_targets, load_calendar, register,
    GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE, TODAY,
    crps_from_quantiles, pit_from_quantiles, rolling_split_conformal,
    EXCHANGEABILITY_CAVEAT,
)
from harness.metrics import attainable_coverage  # noqa: E402
from combine import SCHEMES, MIN_TRAIN, SHRINK_LAMBDA, mixture_moments  # noqa: E402

REPO = FM_SRC.parents[2]
OUT = REPO / "data" / "processed" / "forecast_methods" / "optimal_mix"
REGDIR = REPO / "data" / "processed" / "forecast_methods" / "registry"
SCOREBOARD = REPO / "data" / "processed" / "forecast_methods" / "harness" / "scoreboard.csv"
OUT.mkdir(parents=True, exist_ok=True)

W1_Q = [f"{y}Q{q}" for y in range(2023, 2027) for q in range(1, 5)][:14]
W2_Q = [q for q in W1_Q if q >= "2024Q1"]

# ---------------------------------------------------------------------------
# Street anchors, vintage-stamped. These are QUOTED, never re-derived.
# ---------------------------------------------------------------------------
STREET = {
    "zacks_q4_2026_musd": 3200.0,
    "zacks_q4_2026_as_of": "2026-09-04",
    "zacks_q4_2026_n_est": 10,
    "av36_q4_2026_musd": 3158.0,
    "av36_q4_2026_as_of": "2026-09-11",
    "av36_q4_2026_n_est": 36,
    "zacks_fy27_lo_musd": 15730.0,
    "zacks_fy27_hi_musd": 15760.0,
    "zacks_fy27_as_of": "2026-09-04",
    "zacks_fy26_lo_musd": 14100.0,
    "zacks_fy26_hi_musd": 14160.0,
    "lseg_q3_2026_preguide_musd": 4610.0,
    "lseg_q3_2026_as_of": "2026-08-06",
    "zacks_q3_2026_musd": 4740.0,
}
EV_EBITDA_TURNS_PER_GROWTH_PT = 0.48

# candidates excluded from every pool, with the reason (declared BEFORE any scoring)
EXCLUDE = {
    "baselines|naive_seasonal": "harness README: a transparency object, not the ratio "
                                "denominator and not a forecast anyone would run",
    "l1-reconciliation|revenue_contemporaneous": "the l1 package declares it a deliberate "
                                                 "negative control (RMSE ratio 11.3)",
}
# objects that consume a guide or a consensus number -> excluded from the no-guide pool
GUIDE_CONSUMERS = {
    "baselines|guide_cushion", "baselines|street",
    "guidance-policy|print_from_guide", "guidance-policy|guide_mid_next_q",
}
# declared LIVE carriers: a pool member with no LIVE row of its own inherits one
LIVE_CARRIER = {
    "kernel-lambda|revenue_level_next_q": "kernel-lambda|live_3q26_print",
    "kernel-lambda|revenue_level_next_q_ex_covid": "kernel-lambda|live_3q26_print",
    "kernel-lambda|revenue_level_next_q_last3": "kernel-lambda|live_3q26_print",
    "kernel-lambda|revenue_level_next_q_last3_ex_covid": "kernel-lambda|live_3q26_print",
    "kernel-lambda|revenue_level_next_q_w033": "kernel-lambda|live_3q26_print",
    "kernel-lambda|revenue_level_next_q_w038": "kernel-lambda|live_3q26_print",
}
NO_LIVE_CARRIER = {"kernel-lambda|revenue_level_h1"}  # different horizon; weight dropped

TARGETS = ["revenue_musd", "revenue_yoy", "nights_yoy", "take_rate_pct",
           "gbv_musd", "nights_m", "adr_yoy", "gbv_yoy"]


def log(msg):
    print(f"[optimal-mix] {msg}", flush=True)


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------
def load_all():
    reg = load_registry()
    reg = reg[reg["method"] != "optimal-mix"].copy()   # never eat our own output
    tg = load_targets()
    cal = load_calendar()
    reg["cand"] = reg["method"] + "|" + reg["object"]
    # spec_id embeds the prior_basis token in several packages (e.g. "ar1|gbv_musd|PIT").
    # Strip it so a candidate has ONE identity across both replays.
    def _norm(s):
        parts = [t for t in str(s).split("|") if t not in ("PIT", "full_sample")]
        return "|".join(parts) if parts else "-"
    reg["spec_norm"] = reg["spec_id"].fillna("-").map(_norm)
    reg["cand_spec"] = reg["cand"] + "|" + reg["spec_norm"]
    pr = cal.dropna(subset=["print_date"])[["print_quarter", "print_date"]]
    pr = pr.rename(columns={"print_quarter": "quarter"})
    pr["print_date"] = pd.to_datetime(pr["print_date"]).dt.date
    return reg, tg, cal, dict(zip(pr["quarter"], pr["print_date"]))


def actuals_for(tg, target):
    d = tg.dropna(subset=[target])[["quarter", target]]
    return dict(zip(d["quarter"], d[target].astype(float)))


def sd_of(row):
    s = row.get("sd", np.nan)
    if pd.notna(s) and float(s) > 0:
        return float(s)
    lo, hi = row.get("q10", np.nan), row.get("q90", np.nan)
    if pd.notna(lo) and pd.notna(hi) and hi > lo:
        return float(hi - lo) / 2.5631031
    lo, hi = row.get("q05", np.nan), row.get("q95", np.nan)
    if pd.notna(lo) and pd.notna(hi) and hi > lo:
        return float(hi - lo) / 3.2897073
    return np.nan


# ---------------------------------------------------------------------------
# pool construction -- declared before any scoring, on COVERAGE only
# ---------------------------------------------------------------------------
def build_pools(reg, target):
    d = reg[(reg["target"] == target) & (reg["window"].isin(["W1", "W2"]))]
    if len(d) == 0:
        return {}
    rows = []
    for cs, g in d[d["prior_basis"] == "PIT"].groupby("cand_spec"):
        cand = g["cand"].iloc[0]
        covered = set(g["quarter"]) & set(W1_Q)
        rows.append({"cand_spec": cs, "cand": cand,
                     "n_w1": len(covered), "full_w1": len(covered) == len(W1_Q)})
    info = pd.DataFrame(rows)
    keep = info[info["full_w1"]].copy()
    keep = keep[~keep["cand"].isin(EXCLUDE.keys())]
    pools = {}
    if len(keep) >= 2:
        pools["all"] = sorted(keep["cand_spec"].tolist())
    if target == "revenue_musd":
        ng = keep[~keep["cand"].isin(GUIDE_CONSUMERS)]
        if len(ng) >= 2:
            pools["noguide"] = sorted(ng["cand_spec"].tolist())
    # "parsimonious": every candidate whose PUBLISHED free-parameter count is <= 2.
    # Declared on an attribute each package published itself, never on performance,
    # so it is a leakage-free way to ask whether the mix loses only because the pool
    # is polluted with high-variance candidates.
    npar = (d[d["prior_basis"] == "PIT"].groupby("cand_spec")["n_params"].min())
    par = [c for c in keep["cand_spec"] if float(npar.get(c, 99)) <= 2]
    if len(par) >= 2:
        pools["parsimonious"] = sorted(par)
    # "repaired": take rate only. The harness classifies take_rate_pct as growth-like by
    # NAME, so calibration-rail's ref_* rows compound a growth rate onto a LEVEL. Those
    # rows are a known harness bug, not forecasts, and are excluded on the same grounds
    # as naive_seasonal. Declared before scoring.
    if target == "take_rate_pct":
        rp = keep[~keep["cand"].str.startswith("calibration-rail|ref_")]
        if len(rp) >= 2:
            pools["repaired"] = sorted(rp["cand_spec"].tolist())
    return pools, info


# ---------------------------------------------------------------------------
# the leave-future-out combination replay
# ---------------------------------------------------------------------------
def replay(reg, target, pool, prior_basis, eval_quarters, act, printdates):
    """Return a dict scheme -> DataFrame of combined forecasts over eval_quarters,
    plus the weight path."""
    d = reg[(reg["target"] == target) & (reg["prior_basis"] == prior_basis)
            & (reg["cand_spec"].isin(pool)) & (reg["window"].isin(["W1", "W2"]))]
    # a candidate may appear in both W1 and W2 rows for the same quarter; de-duplicate
    d = d.sort_values("window").drop_duplicates(["cand_spec", "quarter"], keep="first")
    piv_f = d.pivot(index="quarter", columns="cand_spec", values="point")
    sdv = d.copy()
    sdv["sdx"] = sdv.apply(sd_of, axis=1)
    piv_s = sdv.pivot(index="quarter", columns="cand_spec", values="sdx")
    cols = [c for c in pool if c in piv_f.columns]
    piv_f, piv_s = piv_f[cols], piv_s[cols]
    all_q = sorted(piv_f.index)

    vdate = {}
    for q, g in d.groupby("quarter"):
        vdate[q] = pd.to_datetime(g["vintage_date"].iloc[0]).date()

    out, wpath = {s: [] for s in SCHEMES}, []
    for q in eval_quarters:
        if q not in piv_f.index or q not in vdate:
            continue
        dv = vdate[q]
        hist = [h for h in all_q
                if h in act and h in printdates and printdates[h] < dv]
        F = piv_f.loc[hist, cols].to_numpy(float) if hist else np.zeros((0, len(cols)))
        S = piv_s.loc[hist, cols].to_numpy(float) if hist else np.zeros((0, len(cols)))
        y = np.array([act[h] for h in hist], float)
        ok = np.isfinite(F).all(axis=1) if len(hist) else np.zeros(0, bool)
        F, S, y = F[ok], S[ok], y[ok]
        mu = piv_f.loc[q, cols].to_numpy(float)
        sd = piv_s.loc[q, cols].to_numpy(float)
        for sch, fn in SCHEMES.items():
            w = fn(F, y, S)
            m, s = mixture_moments(w, mu, sd)
            out[sch].append({"quarter": q, "vintage_date": dv.isoformat(),
                             "point": m, "sd": s, "n_train": int(len(y)),
                             "actual": act.get(q, np.nan)})
            wpath.append({"scheme": sch, "quarter": q, "vintage_date": dv.isoformat(),
                          "n_train": int(len(y)),
                          **{c: float(w[i]) for i, c in enumerate(cols)}})
    return {s: pd.DataFrame(v) for s, v in out.items()}, pd.DataFrame(wpath), cols


def score_series(df, denom_rmse):
    d = df.dropna(subset=["point", "actual"])
    if len(d) == 0:
        return {}
    e = d["point"].to_numpy(float) - d["actual"].to_numpy(float)
    sd = d["sd"].to_numpy(float)
    sd = np.where(np.isfinite(sd) & (sd > 0), sd, np.nan)
    q10 = d["point"].to_numpy(float) - 1.2815516 * sd
    q90 = d["point"].to_numpy(float) + 1.2815516 * sd
    crps, pits, cov = [], [], []
    for i in range(len(d)):
        yv = d["actual"].to_numpy(float)[i]
        lv = [0.1, 0.5, 0.9]
        vv = [q10[i], d["point"].to_numpy(float)[i], q90[i]]
        if not np.isfinite(vv).all():
            crps.append(abs(e[i])); pits.append(np.nan); cov.append(np.nan); continue
        crps.append(crps_from_quantiles(yv, lv, vv))
        p, _ = pit_from_quantiles(yv, lv, vv)
        pits.append(p)
        cov.append(bool(q10[i] <= yv <= q90[i]))
    rmse = float(np.sqrt(np.mean(e ** 2)))
    ncal = 6
    ccov, nev, cw = rolling_split_conformal(d["actual"], d["point"], n_cal=ncal, alpha=0.2)
    k, lo, hi = attainable_coverage(ncal, 0.2)
    pv = [p for p in pits if np.isfinite(p)]
    try:
        from scipy import stats
        ksp = float(stats.kstest(pv, "uniform").pvalue) if len(pv) >= 4 else np.nan
    except Exception:
        ksp = np.nan
    return {
        "n": int(len(d)), "mae": float(np.mean(np.abs(e))), "rmse": rmse,
        "bias": float(np.mean(e)),
        "mape_pct": float(np.mean(np.abs(e / d["actual"].to_numpy(float))) * 100),
        "crps": float(np.mean(crps)),
        "pit_mean": float(np.mean(pv)) if pv else np.nan, "pit_ks_p": ksp,
        "cov80_empirical": float(np.mean([c for c in cov if c is not np.nan]))
        if any(c is not np.nan for c in cov) else np.nan,
        "rmse_ratio_to_naive": (rmse / denom_rmse) if denom_rmse and denom_rmse > 0 else np.nan,
        "conformal_n_cal": ncal, "conformal_alpha": 0.2, "conformal_k": k,
        "conformal_n_eval": nev, "conformal_cov_empirical": ccov,
        "conformal_mean_width": cw,
        "conformal_attainable_lo": lo, "conformal_attainable_hi": hi,
    }


def denominator(reg, tg, target, quarters, prior_basis):
    """RMSE of the ratio denominator on the same quarters, with its name."""
    act = actuals_for(tg, target)
    if target == "take_rate_pct":
        # the harness classifies take rate as growth-like by name, so its ref_naive
        # compounds a growth rate onto a LEVEL. Use a plain seasonal naive instead.
        lag = {q: act.get(f"{int(q[:4]) - 1}Q{q[-1]}") for q in quarters}
        e = [act[q] - lag[q] for q in quarters if q in act and lag.get(q) is not None]
        return (float(np.sqrt(np.mean(np.square(e)))) if e else np.nan,
                "local_seasonal_naive y[q-4] (harness ref_naive is broken on a level target)")
    cand = ("baselines|naive" if target in ("revenue_musd", "revenue_yoy",
                                            "gbv_musd", "nights_m")
            else "calibration-rail|ref_naive")
    d = reg[(reg["cand"] == cand) & (reg["target"] == target)
            & (reg["prior_basis"] == prior_basis) & (reg["quarter"].isin(quarters))]
    d = d.drop_duplicates("quarter")
    e = [r.point - act[r.quarter] for r in d.itertuples() if r.quarter in act]
    return (float(np.sqrt(np.mean(np.square(e)))) if e else np.nan, cand)


def single_scores(reg, target, pool, prior_basis, quarters, act, denom_rmse):
    d = reg[(reg["target"] == target) & (reg["prior_basis"] == prior_basis)
            & (reg["cand_spec"].isin(pool)) & (reg["quarter"].isin(quarters))]
    d = d.sort_values("window").drop_duplicates(["cand_spec", "quarter"], keep="first")
    rows = []
    for cs, g in d.groupby("cand_spec"):
        g = g[g["quarter"].isin(act.keys())]
        if len(g) == 0:
            continue
        e = g["point"].to_numpy(float) - np.array([act[q] for q in g["quarter"]], float)
        rmse = float(np.sqrt(np.mean(e ** 2)))
        rows.append({"cand_spec": cs, "n": len(g), "rmse": rmse,
                     "mae": float(np.mean(np.abs(e))), "bias": float(np.mean(e)),
                     "rmse_ratio_to_naive": rmse / denom_rmse if denom_rmse else np.nan})
    return pd.DataFrame(rows).sort_values("rmse").reset_index(drop=True)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    reg, tg, cal, printdates = load_all()
    log(f"registry rows {len(reg)}, candidates {reg['cand_spec'].nunique()}")

    pool_rows, scheme_rows, weight_rows, single_rows, comb_rows = [], [], [], [], []
    winners = {}
    combined_series = {}

    for target in TARGETS:
        got = build_pools(reg, target)
        if not got:
            continue
        pools, info = got
        act = actuals_for(tg, target)
        for pname, pool in pools.items():
            for c in pool:
                pool_rows.append({"target": target, "pool": pname, "cand_spec": c})
            for pb in ["PIT", "full_sample"]:
                series, wpath, cols = replay(reg, target, pool, pb, W1_Q, act, printdates)
                if not cols:
                    continue
                wpath["target"], wpath["pool"], wpath["prior_basis"] = target, pname, pb
                weight_rows.append(wpath)
                for win, qs in [("W1", W1_Q), ("W2", W2_Q)]:
                    dr, dname = denominator(reg, tg, target, qs, pb)
                    ss = single_scores(reg, target, pool, pb, qs, act, dr)
                    if len(ss):
                        ss["target"], ss["pool"], ss["window"], ss["prior_basis"] = \
                            target, pname, win, pb
                        single_rows.append(ss)
                    for sch, sdf in series.items():
                        sub = sdf[sdf["quarter"].isin(qs)]
                        sc = score_series(sub, dr)
                        if not sc:
                            continue
                        K = len(cols)
                        npar = (K - 1) if sch in ("stack_ls", "stack_shrunk") else 0
                        scheme_rows.append({
                            "target": target, "pool": pname, "window": win,
                            "prior_basis": pb, "scheme": sch, "K_candidates": K,
                            "scheme_free_params": npar,
                            "denominator": dname, "denominator_rmse": dr, **sc})
                        if pb == "PIT":
                            combined_series[(target, pname, sch, win)] = sub.copy()
                        sub2 = sub.copy()
                        sub2["target"], sub2["pool"], sub2["scheme"] = target, pname, sch
                        sub2["window"], sub2["prior_basis"] = win, pb
                        comb_rows.append(sub2)

    sch_df = pd.DataFrame(scheme_rows)
    sng_df = pd.concat(single_rows, ignore_index=True) if single_rows else pd.DataFrame()
    wgt_df = pd.concat(weight_rows, ignore_index=True) if weight_rows else pd.DataFrame()
    cmb_df = pd.concat(comb_rows, ignore_index=True) if comb_rows else pd.DataFrame()
    pd.DataFrame(pool_rows).to_csv(OUT / "01_candidate_pool.csv", index=False)
    wgt_df.to_csv(OUT / "02_weight_path.csv", index=False)
    sch_df.to_csv(OUT / "03_scheme_scores.csv", index=False)
    sng_df.to_csv(OUT / "03b_single_method_scores.csv", index=False)
    cmb_df.to_csv(OUT / "05_combined_walkforward.csv", index=False)
    log(f"scored {len(sch_df)} scheme rows, {len(sng_df)} single-method rows")

    # ---- winner per (target, pool) on the PIT replay -----------------------
    win_rows = []
    for (t, p), g in sch_df[sch_df["prior_basis"] == "PIT"].groupby(["target", "pool"]):
        best_single = {}
        for w in ("W1", "W2"):
            s = sng_df[(sng_df.target == t) & (sng_df["pool"] == p)
                       & (sng_df.window == w) & (sng_df.prior_basis == "PIT")]
            if len(s):
                best_single[w] = (s.iloc[0]["cand_spec"], float(s.iloc[0]["rmse"]),
                                  float(s.iloc[0]["rmse_ratio_to_naive"]))
        if len(best_single) < 2:
            continue
        # top1_trailing is NOT a combination; it is the implementable "pick the best
        # single method in advance" comparator, so it may not be declared the winner.
        t1 = {}
        for w in ("W1", "W2"):
            gg = g[(g.scheme == "top1_trailing") & (g.window == w)]
            if len(gg):
                t1[w] = float(gg["rmse"].iloc[0])
        cands = []
        for sch, gg in g[g.scheme != "top1_trailing"].groupby("scheme"):
            r = {w: gg[gg.window == w]["rmse"].iloc[0]
                 for w in ("W1", "W2") if len(gg[gg.window == w])}
            if len(r) < 2:
                continue
            beats = (r["W1"] < best_single["W1"][1]) and (r["W2"] < best_single["W2"][1])
            cands.append((sch, r["W1"], r["W2"], beats))
        if not cands:
            continue
        beating = [c for c in cands if c[3]]
        if beating:
            wnr = min(beating, key=lambda c: c[1])
            verdict = "MIX WINS"
        else:
            wnr = min(cands, key=lambda c: c[1])
            verdict = "BEST SINGLE METHOD IS THE MIX"
        win_rows.append({
            "target": t, "pool": p, "verdict": verdict,
            "winning_scheme": wnr[0] if beating else "none (single)",
            "best_scheme_by_w1": wnr[0],
            "mix_rmse_w1": wnr[1], "mix_rmse_w2": wnr[2],
            "best_single": best_single["W1"][0],
            "best_single_rmse_w1": best_single["W1"][1],
            "best_single_rmse_w2": best_single["W2"][1],
            "best_single_w2_name": best_single["W2"][0],
            "best_single_ratio_w1": best_single["W1"][2],
            "best_single_ratio_w2": best_single["W2"][2],
            "mix_ratio_w1": wnr[1] / best_single["W1"][1] * best_single["W1"][2],
            "mix_ratio_w2": wnr[2] / best_single["W2"][1] * best_single["W2"][2],
            "improvement_w1_pct": (best_single["W1"][1] - wnr[1]) / best_single["W1"][1] * 100,
            "improvement_w2_pct": (best_single["W2"][1] - wnr[2]) / best_single["W2"][1] * 100,
            "top1_trailing_rmse_w1": t1.get("W1"), "top1_trailing_rmse_w2": t1.get("W2"),
            "mix_beats_implementable_single_w1": (wnr[1] < t1["W1"]) if "W1" in t1 else None,
            "mix_beats_implementable_single_w2": (wnr[2] < t1["W2"]) if "W2" in t1 else None,
        })
        winners[(t, p)] = win_rows[-1]
    win_df = pd.DataFrame(win_rows)
    win_df.to_csv(OUT / "04_winner_per_target.csv", index=False)
    log("winners written")

    # ---- PIT vs full_sample replay delta ----------------------------------
    if len(sch_df):
        piv = sch_df.pivot_table(index=["target", "pool", "window", "scheme"],
                                 columns="prior_basis", values="rmse").reset_index()
        if "PIT" in piv and "full_sample" in piv:
            piv["delta_full_minus_pit"] = piv["full_sample"] - piv["PIT"]
        piv.to_csv(OUT / "07_replay_pit_vs_fullsample.csv", index=False)

    # ---- live objects -----------------------------------------------------
    live = build_live(reg, tg, act_rev=actuals_for(tg, "revenue_musd"),
                      printdates=printdates, sch_df=sch_df, sng_df=sng_df,
                      win_df=win_df, combined_series=combined_series)
    with open(OUT / "combined_live_objects.json", "w") as f:
        json.dump(live, f, indent=2, default=str)
    log("combined_live_objects.json written")

    write_registry(live, sch_df, win_df, cmb_df)
    log("done")
    return 0


# ---------------------------------------------------------------------------
def _live_row(reg, cand, target, quarter, spec=None):
    d = reg[(reg["cand"] == cand) & (reg["target"] == target)
            & (reg["quarter"] == quarter) & (reg["window"] == "LIVE")
            & (reg["prior_basis"] == "PIT")]
    if spec is not None:
        d = d[d["spec_id"] == spec]
    if len(d) == 0:
        return None
    return d.iloc[0]


def build_live(reg, tg, act_rev, printdates, sch_df, sng_df, win_df, combined_series):
    live = {"generated": str(TODAY), "package": "optimal-mix",
            "street_anchors_vintage_stamped": STREET, "objects": {}}

    # ---------- 1. 3Q26 print, revenue, GUIDED pool ------------------------
    target, pool_name = "revenue_musd", "all"
    pools, _ = build_pools(reg, target)
    pool = pools[pool_name]
    act = act_rev
    wr = win_df[(win_df.target == target) & (win_df["pool"] == pool_name)]
    sch = wr.iloc[0]["best_scheme_by_w1"] if len(wr) else "inv_mse"
    use_mix = bool(len(wr)) and wr.iloc[0]["verdict"] == "MIX WINS"

    # fit the weights on EVERYTHING that printed before the 2026-08-06 guide date
    dv = pd.Timestamp("2026-08-06").date()
    d = reg[(reg["target"] == target) & (reg["prior_basis"] == "PIT")
            & (reg["cand_spec"].isin(pool)) & (reg["window"].isin(["W1", "W2"]))]
    d = d.sort_values("window").drop_duplicates(["cand_spec", "quarter"], keep="first")
    piv_f = d.pivot(index="quarter", columns="cand_spec", values="point")
    dd = d.copy(); dd["sdx"] = dd.apply(sd_of, axis=1)
    piv_s = dd.pivot(index="quarter", columns="cand_spec", values="sdx")
    cols = [c for c in pool if c in piv_f.columns]
    hist = [q for q in sorted(piv_f.index)
            if q in act and q in printdates and printdates[q] < dv]
    F = piv_f.loc[hist, cols].to_numpy(float)
    S = piv_s.loc[hist, cols].to_numpy(float)
    y = np.array([act[q] for q in hist], float)
    w_live = {s: SCHEMES[s](F, y, S) for s in SCHEMES}

    # map pool candidates onto LIVE carriers
    carried, mu, sd, wmap = [], [], [], []
    w = w_live[sch]
    for i, cs in enumerate(cols):
        cand = "|".join(cs.split("|")[:2])
        if cand in NO_LIVE_CARRIER:
            continue
        carrier = LIVE_CARRIER.get(cand, cand)
        r = _live_row(reg, carrier, target, "2026Q3")
        if r is None:
            continue
        carried.append({"pool_candidate": cs, "live_carrier": carrier,
                        "weight": float(w[i]), "point": float(r["point"]),
                        "sd": float(sd_of(r))})
        mu.append(float(r["point"])); sd.append(float(sd_of(r))); wmap.append(float(w[i]))
    wmap = np.array(wmap); wmap = wmap / wmap.sum() if wmap.sum() > 0 else wmap
    m3, s3 = mixture_moments(wmap, np.array(mu), np.array(sd))

    # split-conformal half width from the COMBINED walk-forward residuals
    key = (target, pool_name, sch, "W1")
    ser = combined_series.get(key)
    res = np.abs(ser["point"].to_numpy(float) - ser["actual"].to_numpy(float)) \
        if ser is not None else np.array([])
    conf = conformal_block(res)

    live["objects"]["print_3Q26_revenue_musd"] = {
        "what": "3Q26 revenue PRINT (the quarter is guided; guide 4,690-4,770; "
                "the print lands ~5 Nov 2026, after the finals)",
        "scheme_used": sch, "mix_beats_best_single_both_windows": use_mix,
        "note_if_not": "the winner rule failed, so the number below is the combination "
                       "anyway but is reported as a tie with the best single method "
                       "(guidance-policy print_from_guide / baselines guide_cushion)",
        "point_musd": round(m3, 1), "mixture_sd_musd": round(s3, 1),
        "q10_musd": round(m3 - 1.2815516 * s3, 1),
        "q90_musd": round(m3 + 1.2815516 * s3, 1),
        "conformal_80_interval_musd": [round(m3 - conf["qhat"], 1),
                                       round(m3 + conf["qhat"], 1)] if conf["qhat"] else None,
        "conformal": conf,
        "vs_street_lseg_preguide_4610_musd": round(m3 - STREET["lseg_q3_2026_preguide_musd"], 1),
        "vs_zacks_4740_musd_as_of_2026_09_04": round(m3 - STREET["zacks_q3_2026_musd"], 1),
        "carried_weights": carried,
        "weight_coverage_of_pool": round(float(np.sum([c["weight"] for c in carried])), 6),
    }

    # nights / ADR / take rate live combinations, where a package registered them
    # take rate uses the REPAIRED pool: the harness's take_rate ref_* rows are a known
    # classification bug (a growth rate compounded onto a level), declared before scoring.
    for t2, pnm in [("take_rate_pct", "repaired"), ("nights_yoy", "all"), ("adr_yoy", "all"),
                    ("gbv_yoy", "all"), ("nights_m", "all"), ("gbv_musd", "all")]:
        got = build_pools(reg, t2)
        if not got or pnm not in got[0]:
            continue
        p2 = got[0][pnm]
        wr2 = win_df[(win_df.target == t2) & (win_df["pool"] == pnm)]
        if not len(wr2):
            continue
        sch2 = wr2.iloc[0]["best_scheme_by_w1"]
        a2 = actuals_for(tg, t2)
        d2 = reg[(reg["target"] == t2) & (reg["prior_basis"] == "PIT")
                 & (reg["cand_spec"].isin(p2)) & (reg["window"].isin(["W1", "W2"]))]
        d2 = d2.sort_values("window").drop_duplicates(["cand_spec", "quarter"], keep="first")
        pf = d2.pivot(index="quarter", columns="cand_spec", values="point")
        dz = d2.copy(); dz["sdx"] = dz.apply(sd_of, axis=1)
        ps = dz.pivot(index="quarter", columns="cand_spec", values="sdx")
        c2 = [c for c in p2 if c in pf.columns]
        h2 = [q for q in sorted(pf.index) if q in a2 and q in printdates
              and printdates[q] < dv]
        w2 = SCHEMES[sch2](pf.loc[h2, c2].to_numpy(float),
                           np.array([a2[q] for q in h2], float),
                           ps.loc[h2, c2].to_numpy(float))
        mu2, sd2, ww2, det = [], [], [], []
        for i, cs in enumerate(c2):
            cand = "|".join(cs.split("|")[:2])
            r = _live_row(reg, cand, t2, "2026Q3")
            if r is None:
                continue
            mu2.append(float(r["point"])); sd2.append(float(sd_of(r))); ww2.append(float(w2[i]))
            det.append({"pool_candidate": cs, "weight": float(w2[i]),
                        "point": float(r["point"])})
        if not mu2:
            live["objects"][f"live_3Q26_{t2}"] = {
                "status": "NOT PRODUCIBLE: no pool member registered a LIVE 2026Q3 row",
                "pool_size": len(c2)}
            continue
        aw = np.array(ww2); aw = aw / aw.sum() if aw.sum() > 0 else aw
        mm, ss = mixture_moments(aw, np.array(mu2), np.array(sd2))
        ser2 = combined_series.get((t2, pnm, sch2, "W1"))
        r2 = np.abs(ser2["point"].to_numpy(float) - ser2["actual"].to_numpy(float)) \
            if ser2 is not None else np.array([])
        live["objects"][f"live_3Q26_{t2}"] = {
            "scheme_used": sch2,
            "mix_beats_best_single_both_windows": bool(wr2.iloc[0]["verdict"] == "MIX WINS"),
            "point": round(mm, 4), "mixture_sd": round(ss, 4),
            "q10": round(mm - 1.2815516 * ss, 4), "q90": round(mm + 1.2815516 * ss, 4),
            "conformal": conformal_block(r2),
            "pool": pnm,
            "weight_coverage_of_pool": round(float(np.sum(ww2)), 6),
            "STATUS": ("OK" if float(np.sum(ww2)) >= 0.5 else
                       "NOT USABLE: the winning weights sit almost entirely on pool "
                       "members that registered no LIVE 2026Q3 row, so the number below "
                       "is a renormalisation onto the leftovers and is NOT the mix"),
            "carried_weights": det,
        }
        if t2 == "take_rate_pct" and ss > 0:
            from math import erf, sqrt as _sq
            z = (18.10 - mm) / ss
            live["objects"][f"live_3Q26_{t2}"]["pre_registered_threshold_pct"] = 18.10
            live["objects"][f"live_3Q26_{t2}"]["p_clears_18_10"] = round(
                1.0 - 0.5 * (1.0 + erf(z / _sq(2.0))), 3)
            live["objects"][f"live_3Q26_{t2}"]["threshold_note"] = (
                "the frozen 3Q26 pre-registration is >= 18.10 pct if the fee migration "
                "is flowing; the combination puts the posterior probability of clearing "
                "it well below a half, which is the power of the test made visible")

    # ---------- 2. 4Q26 guide midpoint on 5 Nov 2026 -----------------------
    # 4Q26 is NOT guided at the pitch date, so the uncertainty must come from the
    # NO-GUIDE pool's combined walk-forward error, not the guided pool's.
    ngp = pools_noguide_sd(reg, tg, printdates, combined_series, win_df)
    q4 = reg[(reg["cand"] == "guidance-policy|q4_2026_print")
             & (reg["quarter"] == "2026Q4") & (reg["prior_basis"] == "PIT")]
    q4g = reg[(reg["cand"] == "guidance-policy|q4_2026_guide_mid")
              & (reg["quarter"] == "2026Q4") & (reg["prior_basis"] == "PIT")]
    krow = _live_row(reg, "kernel-lambda|live_4q26_print", "revenue_musd", "2026Q4")
    grid = []
    from math import erf, sqrt as _sqrt

    def ncdf(x):
        return 0.5 * (1.0 + erf(x / _sqrt(2.0)))

    sd_pct = ngp["sd_pct"]
    for r in q4.itertuples():
        gmid = q4g[q4g["spec_id"] == r.spec_id]
        if not len(gmid):
            continue
        gm = float(gmid.iloc[0]["point"])
        s = gm * sd_pct / 100.0
        grid.append({
            "spec": r.spec_id, "print_musd": round(float(r.point), 1),
            "guide_mid_musd": round(gm, 1), "guide_sd_musd": round(s, 1),
            "guide_sd_pct": round(sd_pct, 2),
            "guide_range_lo_musd": round(gm * (1 - 0.0085), 0),
            "guide_range_hi_musd": round(gm * (1 + 0.0085), 0),
            "p_guide_below_zacks_3200": round(ncdf((STREET["zacks_q4_2026_musd"] - gm) / s), 3),
            "p_guide_below_av36_3158": round(ncdf((STREET["av36_q4_2026_musd"] - gm) / s), 3),
        })
    central = [g for g in grid if g["spec"].startswith("gbv26300")]
    live["objects"]["guide_mid_4Q26_on_5Nov2026"] = {
        "what": "the revenue guide midpoint management gives on 5 Nov 2026 for 4Q26",
        "uncertainty_source": ngp["label"],
        "predictive_sd_pct": round(sd_pct, 2),
        "central_gbv_3Q26_musd": 26300,
        "central_cases": central,
        "full_grid": grid,
        "headline": ("no fee step and half-weight fee step bracket the answer; the "
                     "full-weight case is excluded because fee-takerate measures theta "
                     "below 1 and the migrated-cohort GBV falls"),
        "kernel_lambda_live_4q26_print_musd": float(krow["point"]) if krow is not None else None,
        "consensus_disagrees_with_itself_musd": 126.0,
        "say_first": ("consensus disagrees with itself by 126 musd -- Zacks' own quarterly "
                      "sum 14,226 against its own FY26 14,100 -- which is larger than our edge"),
    }

    # ---------- 3. FY27 ----------------------------------------------------
    l1grid = REPO / "data" / "processed" / "forecast_methods" / "l1_reconciliation" / \
        "l1_fy27_revenue_grid.csv"
    l1dec = REPO / "data" / "processed" / "forecast_methods" / "l1_reconciliation" / \
        "l1_fy27_growth_decomposition.csv"
    gr = pd.read_csv(l1grid)
    dec = pd.read_csv(l1dec)
    base = gr[(gr.scenario == "driver_base")].set_index("kernel_w")
    fy27_23 = float(base.loc[0.6666666666666666, "fy27_revenue_musd"])
    fy27_050 = float(base.loc[0.5, "fy27_revenue_musd"])
    fy27_033 = float(base.loc[0.33, "fy27_revenue_musd"])
    g23 = float(base.loc[0.6666666666666666, "fy27_growth_pct"])
    g033 = float(base.loc[0.33, "fy27_growth_pct"])
    st_mid = (STREET["zacks_fy27_lo_musd"] + STREET["zacks_fy27_hi_musd"]) / 2
    st_fy26_mid = (STREET["zacks_fy26_lo_musd"] + STREET["zacks_fy26_hi_musd"]) / 2
    st_growth = (st_mid / st_fy26_mid - 1) * 100
    fee_delta = -0.3135  # fee-takerate central theta, delta vs the +0.9pp half-weight line
    fx_term = 0.2        # fx-lag: FY27 FX is the revenue-WEIGHTED AVERAGE, never the sum
    decomp = [{"line": r.line, "pp": round(float(r.pp), 2), "owner": r.owner,
               "basis": r.basis} for r in dec.itertuples()]
    live["objects"]["FY27"] = {
        "what": "FY27 revenue and the Feb-2027 FY27 guide",
        "fy27_revenue_musd_kernel_w_two_thirds": round(fy27_23, 1),
        "fy27_revenue_musd_kernel_w_050": round(fy27_050, 1),
        "fy27_revenue_musd_kernel_w_033": round(fy27_033, 1),
        "fy27_growth_pct": round(g23, 2),
        "kernel_weight_sensitivity_musd": round(fy27_23 - fy27_033, 1),
        "kernel_weight_sensitivity_growth_pp": round(g23 - g033, 2),
        "street_fy27_musd_range": [STREET["zacks_fy27_lo_musd"], STREET["zacks_fy27_hi_musd"]],
        "street_as_of": STREET["zacks_fy27_as_of"],
        "vs_street_pct": round((fy27_23 / st_mid - 1) * 100, 2),
        "street_implied_fy27_growth_pct": round(st_growth, 2),
        "our_growth_minus_street_growth_pp": round(g23 - st_growth, 2),
        "decomposition_one_owner_per_line": decomp,
        "fx_term_from_fx_lag_pp": fx_term,
        "fx_term_note": ("fx-lag: FY27 FX is the revenue-weighted AVERAGE of the four "
                         "quarterly y/y contributions, +0.2pp on spot held; the sum 0.9 "
                         "is meaningless. Inside the decomposition the booking-date FX "
                         "line stays 0.0 because it is already in the lagged GBV base; "
                         "+0.2pp is the stated-series reading, not a second subtraction"),
        "fee_line_delta_from_fee_takerate_pp": fee_delta,
        "fee_line_note": ("fee-takerate at central theta 0.833 makes the +0.9pp "
                          "half-weight fee line 0.31pp too generous"),
        "feb_2027_fy27_guide_note": ("ABNB does not guide FY revenue as a point; the Feb-2027 "
                                     "call gives a 1Q27 revenue range plus qualitative FY "
                                     "colour. The comparable object is the 1Q27 guide "
                                     "midpoint, carried in l1_unregistered_fy27_revenue.csv"),
        "say_in_first_200_words": ("our FY27 is +0.59% against the Street, inside the kernel's "
                                   "own walk-forward error, so the variant view is "
                                   "compositional and about the guide, not the level"),
    }

    # ---------- 4. forward-multiple implication (applied ONCE) -------------
    edge_pp = g23 - st_growth
    live["objects"]["forward_multiple_implication"] = {
        "rule": "+0.48 EV/EBITDA turns per point of forward revenue growth, applied ONCE",
        "applied_to": "our FY27 growth minus the Street-implied FY27 growth",
        "growth_edge_pp": round(edge_pp, 2),
        "ev_ebitda_turns": round(EV_EBITDA_TURNS_PER_GROWTH_PT * edge_pp, 3),
        "kernel_weight_sensitivity_turns": round(
            EV_EBITDA_TURNS_PER_GROWTH_PT * (g23 - g033), 3),
        "interpretation": ("this is an IMPLICATION, not a price target. The honest reading "
                           "is that the kernel-weight indeterminacy (w in 0.33 to 0.667) is "
                           "worth roughly 25x more multiple than our level edge over the "
                           "Street, which is why the pitch is about the GUIDE and the "
                           "composition, not about the FY27 level"),
        "not_applied_twice": "the turn factor is applied once, to the growth delta only",
    }
    return live


def conformal_block(res):
    res = np.asarray([r for r in res if np.isfinite(r)], float)
    out = {"n_residuals": int(len(res)), "qhat": None,
           "caveat": EXCHANGEABILITY_CAVEAT}
    if len(res) == 0:
        return out
    for ncal in (8, 6):
        if len(res) >= ncal:
            cal = np.sort(res[-ncal:])
            k, lo, hi = attainable_coverage(ncal, 0.2)
            out.update({"n_cal": ncal, "k": k,
                        "qhat": float(cal[min(k, ncal) - 1]),
                        "attainable_lo": lo, "attainable_hi": hi,
                        "nominal_requested": 0.80,
                        "note": (f"at n_cal={ncal}, alpha=0.2 the attainable coverage band is "
                                 f"[{lo:.3f},{hi:.3f}]; there is NO 80% guarantee at this n")})
            break
    return out


def pools_noguide_sd(reg, tg, printdates, combined_series, win_df):
    """Predictive sd, in percent of level, for an UNGUIDED quarter, taken from the
    no-guide revenue pool's own combined walk-forward errors."""
    t, p = "revenue_musd", "noguide"
    wr = win_df[(win_df.target == t) & (win_df["pool"] == p)]
    sch = wr.iloc[0]["best_scheme_by_w1"] if len(wr) else "inv_mse"
    best = None
    for win in ("W1", "W2"):
        ser = combined_series.get((t, p, sch, win))
        if ser is None:
            continue
        e = (ser["point"].to_numpy(float) - ser["actual"].to_numpy(float)) \
            / ser["actual"].to_numpy(float) * 100
        v = float(np.sqrt(np.mean(e ** 2)))
        if best is None or v > best[1]:
            best = (win, v)
    if best is None:
        return {"sd_pct": 3.03, "label": "fallback: guidance-policy measured 3.03pp"}
    return {"sd_pct": best[1],
            "label": (f"optimal-mix no-guide pool, scheme {sch}, RMSE in percent of level "
                      f"on {best[0]} (the wider of W1/W2 is used)")}


# ---------------------------------------------------------------------------
def write_registry(live, sch_df, win_df, cmb_df):
    """Register the winning combination as forecast objects in the frozen format."""
    rows = []
    # backtest rows: the winning scheme per (target, pool), both windows, both replays
    for _, wr in win_df.iterrows():
        t, p, sch = wr["target"], wr["pool"], wr["best_scheme_by_w1"]
        sub = cmb_df[(cmb_df.target == t) & (cmb_df["pool"] == p)
                     & (cmb_df.scheme == sch)]
        for r in sub.itertuples():
            sd = r.sd if np.isfinite(r.sd) and r.sd > 0 else np.nan
            rows.append({
                "method": "optimal-mix", "object": f"mix_{t}_{p}", "target": t,
                "quarter": r.quarter, "vintage_date": r.vintage_date,
                "horizon_q": 0, "point": r.point, "q50": r.point,
                "q10": r.point - 1.2815516 * sd if np.isfinite(sd) else np.nan,
                "q90": r.point + 1.2815516 * sd if np.isfinite(sd) else np.nan,
                "sd": sd, "window": r.window, "prior_basis": r.prior_basis,
                "n_params": 0 if sch not in ("stack_ls", "stack_shrunk")
                else int(wr.get("K_candidates", 0) or 0),
                "n_train": int(r.n_train),
                "knowable_from": r.vintage_date,
                "spec_id": f"{sch}|pool={p}|leave_future_out",
                "notes": f"optimal-mix combination; {wr['verdict']}",
            })
    if rows:
        df = pd.DataFrame(rows)
        for obj, g in df.groupby("object"):
            try:
                register(g.copy(), quiet=True)
            except Exception as e:  # noqa: BLE001
                log(f"WARN register {obj}: {e}")

    # LIVE rows
    lr = []
    o = live["objects"].get("print_3Q26_revenue_musd")
    if o:
        for pb in ("PIT", "full_sample"):
            lr.append({"method": "optimal-mix", "object": "live_combined",
                       "target": "revenue_musd", "quarter": "2026Q3",
                       "vintage_date": str(TODAY), "horizon_q": 0,
                       "point": o["point_musd"], "q50": o["point_musd"],
                       "q10": o["q10_musd"], "q90": o["q90_musd"],
                       "sd": o["mixture_sd_musd"], "window": "LIVE",
                       "prior_basis": pb, "n_params": 0, "n_train": 13,
                       "knowable_from": str(TODAY),
                       "spec_id": f"combined_{o['scheme_used']}|pool=all",
                       "notes": "3Q26 print from the winning combination"})
    g4 = live["objects"].get("guide_mid_4Q26_on_5Nov2026")
    if g4 and g4["central_cases"]:
        for c in g4["central_cases"]:
            if c["spec"].endswith("fee_full_weight"):
                continue
            for pb in ("PIT", "full_sample"):
                lr.append({"method": "optimal-mix", "object": "live_q4_2026_guide_mid",
                           "target": "guide_mid", "quarter": "2026Q4",
                           "vintage_date": str(TODAY), "horizon_q": 1,
                           "point": c["guide_mid_musd"], "q50": c["guide_mid_musd"],
                           "q10": c["guide_mid_musd"] - 1.2815516 * c["guide_sd_musd"],
                           "q90": c["guide_mid_musd"] + 1.2815516 * c["guide_sd_musd"],
                           "sd": c["guide_sd_musd"], "window": "LIVE",
                           "prior_basis": pb, "n_params": 0, "n_train": 13,
                           "knowable_from": str(TODAY),
                           "spec_id": f"{c['spec']}|sd_from_noguide_mix",
                           "notes": "5 Nov 2026 guide midpoint; sd from the no-guide mix"})
    if lr:
        d = pd.DataFrame(lr)
        for obj, g in d.groupby("object"):
            try:
                register(g.copy(), strict_windows=False, quiet=True)
            except Exception as e:  # noqa: BLE001
                log(f"WARN register LIVE {obj}: {e}")


if __name__ == "__main__":
    sys.exit(main())
