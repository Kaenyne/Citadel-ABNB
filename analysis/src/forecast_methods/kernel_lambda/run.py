#!/usr/bin/env python
"""kernel-lambda entry point.  Rebuilds every output of the package.

    cd "<repo>"
    /Users/theomachado/.venvs/citadel-abnb/bin/python \
        analysis/src/forecast_methods/kernel_lambda/run.py

Writes progressively: every stage flushes its CSV before the next stage starts,
so a crash still leaves the completed stages on disk.  Exit code 0 on success.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
FM = HERE.parent                      # analysis/src/forecast_methods
REPO = FM.parents[2]                  # repo root
sys.path.insert(0, str(FM))

from harness import (GUIDE_EVENTS_ALL, history_as_of, load_targets,  # noqa: E402
                     register, window_of_target, quarters as Q, TODAY)

import kernel as K  # noqa: E402

KPI = REPO / "data/processed/overnight/02_kpi_panel_quarterly.csv"
OUT = REPO / "data/processed/forecast_methods/kernel_lambda"
OUT.mkdir(parents=True, exist_ok=True)

W_PUB = 2.0 / 3.0          # published kernel weight
W_ALT = 0.38               # M6 proposal, carried as the mandatory sensitivity
SENS = (0.33, 2.0 / 3.0)       # propagated sensitivity band

ACCEPT = {  # architect's table, percent
    1: [13.034, 12.325, 12.612], 2: [13.449, 13.946, 13.736],
    3: [17.391, 17.145, 17.182], 4: [11.946, 12.117, 12.026]}
ACCEPT_CELLS = {1: ["2024Q1", "2025Q1", "2026Q1"], 2: ["2024Q2", "2025Q2", "2026Q2"],
                3: ["2023Q3", "2024Q3", "2025Q3"], 4: ["2023Q4", "2024Q4", "2025Q4"]}

LOG = []


def say(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)


# ================================================================ (a) acceptance
def stage_a(panel):
    f = K.usable(panel)
    f = f.assign(lam_w23=K.lam_pct(f, W_PUB), lam_w38=K.lam_pct(f, W_ALT),
                 base_w23=K.base(f, W_PUB), base_w38=K.base(f, W_ALT))
    f["lam_w033"] = K.lam_pct(f, 0.33)
    f["lam_w0667"] = K.lam_pct(f, 0.667)
    cols = ["q", "season", "revenue_musd", "gbv_l1", "gbv_l2", "base_w23",
            "lam_w23", "base_w38", "lam_w38", "lam_w033", "lam_w0667"]
    f[cols].to_csv(OUT / "01_lambda_table.csv", index=False)

    rows, ok = [], True
    for s, qs in ACCEPT_CELLS.items():
        for i, q in enumerate(qs):
            got = float(f.loc[f["q"] == q, "lam_w23"].iloc[0])
            exp = ACCEPT[s][i]
            hit = abs(round(got, 3) - exp) <= 0.0015
            ok &= hit
            rows.append({"season": s, "quarter": q, "expected_pct": exp,
                         "computed_pct": round(got, 4), "abs_diff_pp": round(abs(got - exp), 5),
                         "match_2dp": bool(hit)})
    extra = []
    for q in ["2023Q1", "2023Q2"]:
        extra.append({"season": int(q[-1]), "quarter": q, "expected_pct": np.nan,
                      "computed_pct": round(float(f.loc[f["q"] == q, "lam_w23"].iloc[0]), 4),
                      "abs_diff_pp": np.nan, "match_2dp": None})
    acc = pd.DataFrame(rows + extra)
    acc.to_csv(OUT / "01_acceptance_test.csv", index=False)
    q4 = [r["computed_pct"] for r in rows if r["season"] == 4]
    say(f"[A] acceptance test: {'PASS' if ok else 'FAIL'} on all 12 cells to 2dp; "
        f"Q4 within-season range {max(q4) - min(q4):.3f}pp (expected 0.171)")
    say("[A] extra usable cells not in the architect table: "
        f"1Q23 {extra[0]['computed_pct']:.3f}, 2Q23 {extra[1]['computed_pct']:.3f}")
    return f, ok


# ================================================================ (b) weights
def stage_b(panel):
    f = K.usable(panel)
    subs = {"n22_2021Q1plus": f,
            "n18_2022Q1plus": f[f["q"] >= "2022Q1"].reset_index(drop=True),
            "n14_2023Q1plus": f[f["q"] >= "2023Q1"].reset_index(drop=True),
            "n12_accept_cells": f[f["q"].isin(sum(ACCEPT_CELLS.values(), []))].reset_index(drop=True)}
    grids, summ = [], []
    for name, sub in subs.items():
        g = K.weight_grid(sub)
        g.insert(0, "sample", name)
        grids.append(g)
        bw = K.block_bootstrap_w(sub, n_boot=400, block=4)
        lo, hi = (np.nanpercentile(bw, [2.5, 97.5]) if len(bw) > 20 else (np.nan, np.nan))
        d23 = float(g.loc[g.w.round(2) == 0.67, "loo_rmse_pct"].iloc[0])
        d38 = float(g.loc[g.w.round(2) == 0.38, "loo_rmse_pct"].iloc[0])
        summ.append({"sample": name, "n": int(g["n"].iloc[0]),
                     "argmin_w_disp": float(g.loc[g.pooled_rel_disp_pct.idxmin(), "w"]),
                     "argmin_w_loo": float(g.loc[g.loo_rmse_pct.idxmin(), "w"]),
                     "loo_min_pct": float(g.loo_rmse_pct.min()),
                     "loo_at_0667_pct": d23, "loo_at_038_pct": d38,
                     "flat_band_w_lo": float(g.loc[g.loo_rmse_pct <= 1.05 * g.loo_rmse_pct.min(), "w"].min()),
                     "flat_band_w_hi": float(g.loc[g.loo_rmse_pct <= 1.05 * g.loo_rmse_pct.min(), "w"].max()),
                     "boot_w_ci_lo": lo, "boot_w_ci_hi": hi, "n_boot_ok": len(bw)})
    pd.concat(grids).to_csv(OUT / "02_weight_grid.csv", index=False)
    s = pd.DataFrame(summ)
    s.to_csv(OUT / "03_weight_summary.csv", index=False)
    for r in summ:
        say(f"[B] {r['sample']:18s} n={r['n']:2d} argmin(LOO) w={r['argmin_w_loo']:.2f} "
            f"LOO {r['loo_min_pct']:.3f}% | at 2/3 {r['loo_at_0667_pct']:.3f}% | at 0.38 "
            f"{r['loo_at_038_pct']:.3f}% | +5% flat band [{r['flat_band_w_lo']:.2f},"
            f"{r['flat_band_w_hi']:.2f}] | boot 95% CI on argmin "
            f"[{r['boot_w_ci_lo']:.2f},{r['boot_w_ci_hi']:.2f}] (n_boot={r['n_boot_ok']})")

    # season means at each weight, on the 2023Q1+ estimation window
    est = subs["n14_2023Q1plus"]
    tab = []
    for w in [0.20, 0.33, W_ALT, 0.50, W_PUB, 0.80]:
        for s_ in (1, 2, 3, 4):
            m, n = K.season_lambda(est, s_, w)
            tab.append({"w": round(w, 4), "season": s_, "lambda_pct": m, "n_cells": n})
    pd.DataFrame(tab).to_csv(OUT / "04_season_lambda_by_weight.csv", index=False)
    return s, est


def stage_b_cost(panel, est):
    """Cost of the flatness: the 4Q26 print at each weight."""
    gbv = dict(zip(panel["q"], panel["gbv_musd"]))
    g3_central = 26300.0
    rows = []
    for w in [0.20, 0.33, W_ALT, 0.50, W_PUB, 0.76, 0.80]:
        lam4, n4 = K.season_lambda(est, 4, w)
        b = w * g3_central + (1 - w) * gbv["2026Q2"]
        rows.append({"w": round(w, 4), "lambda_q4_pct": lam4, "n_cells": n4,
                     "gbv_3q26_assumed_musd": g3_central, "base_musd": b,
                     "print_4q26_musd": lam4 / 100 * b})
    c = pd.DataFrame(rows)
    c.to_csv(OUT / "05_flatness_cost_4q26.csv", index=False)
    p23 = float(c.loc[c.w.round(4) == round(W_PUB, 4), "print_4q26_musd"].iloc[0])
    p38 = float(c.loc[c.w.round(4) == W_ALT, "print_4q26_musd"].iloc[0])
    say(f"[B] cost of flatness on 4Q26 at GBV_3Q26=26,300: w=2/3 base "
        f"{float(c.loc[c.w.round(4) == round(W_PUB, 4), 'base_musd'].iloc[0]):,.0f} x "
        f"{float(c.loc[c.w.round(4) == round(W_PUB, 4), 'lambda_q4_pct'].iloc[0]):.3f}% = "
        f"{p23:,.0f}M ; w=0.38 base "
        f"{float(c.loc[c.w.round(4) == W_ALT, 'base_musd'].iloc[0]):,.0f} x "
        f"{float(c.loc[c.w.round(4) == W_ALT, 'lambda_q4_pct'].iloc[0]):.3f}% = {p38:,.0f}M ; "
        f"gap {p23 - p38:+,.0f}M ({100 * (p23 - p38) / p23:+.2f}%)")
    lo = float(c.loc[c.w.round(4) == 0.33, "print_4q26_musd"].iloc[0])
    hi = float(c.loc[c.w.round(4) == round(W_PUB, 4), "print_4q26_musd"].iloc[0])
    say(f"[B] sensitivity band w in [0.33, 2/3]: 4Q26 print {min(lo, hi):,.0f}"
        f"-{max(lo, hi):,.0f}M")
    return c


# ================================================================ (c) lag polynomial
def stage_c(panel):
    f = panel.dropna(subset=["revenue_musd", "gbv_musd", "gbv_l1", "gbv_l2", "gbv_l3"])
    rows = []
    for name, sub in [("n22_2021Q1plus", f), ("n18_2022Q1plus", f[f["q"] >= "2022Q1"]),
                      ("n14_2023Q1plus", f[f["q"] >= "2023Q1"])]:
        sub = sub.reset_index(drop=True)
        if len(sub) < 10:
            continue
        fit = K.fit_lag_polynomial(sub)
        fit0 = K.fit_lag_polynomial(sub, restrict_phi0=True)
        loo_free, n_loo = K.loo_lag_polynomial(sub)
        loo_rest, _ = K.loo_lag_polynomial(sub, restrict_phi0=True)
        bp = K.bootstrap_phi0(sub, n_boot=300)
        ci = (np.nanpercentile(bp[:, 0], [2.5, 97.5]) if len(bp) > 20 else (np.nan, np.nan))
        rows.append({"sample": name, "n": fit["n"], "n_params": fit["n_params"],
                     "phi0": fit["phi"][0], "phi1": fit["phi"][1], "phi2": fit["phi"][2],
                     "phi3": fit["phi"][3], "rmse_pct": fit["rmse_pct"],
                     "phi0_boot_lo": ci[0], "phi0_boot_hi": ci[1],
                     "phi0_boot_p_gt_0.02": float(np.mean(bp[:, 0] > 0.02)) if len(bp) else np.nan,
                     "implied_mean_lag_q": float(np.dot(fit["phi"], [0, 1, 2, 3])),
                     "n_boot_ok": len(bp),
                     "restricted_phi0_0_phi1": fit0["phi"][1],
                     "restricted_phi0_0_phi2": fit0["phi"][2],
                     "restricted_phi0_0_phi3": fit0["phi"][3],
                     "restricted_mean_lag_q": float(np.dot(fit0["phi"], [0, 1, 2, 3])),
                     "restricted_rmse_pct": fit0["rmse_pct"],
                     "loo_rmse_free_pct": loo_free, "loo_rmse_phi0_zero_pct": loo_rest,
                     "n_loo": n_loo})
        for s_, v in fit["lam_pct"].items():
            rows[-1][f"lambda_q{s_}_pct"] = v
    lp = pd.DataFrame(rows)
    lp.to_csv(OUT / "06_lag_polynomial.csv", index=False)
    for _, r in lp.iterrows():
        say(f"[C] lag poly {r['sample']:18s} n={int(r['n'])} p={int(r['n_params'])} "
            f"phi = [{r.phi0:.3f}, {r.phi1:.3f}, {r.phi2:.3f}, {r.phi3:.3f}] "
            f"mean lag {r['implied_mean_lag_q']:.2f}q  rel-RMSE {r.rmse_pct:.2f}%  "
            f"phi0 95% block-boot CI [{r['phi0_boot_lo']:.3f},{r['phi0_boot_hi']:.3f}] "
            f"P(phi0>0.02)={r['phi0_boot_p_gt_0.02']:.2f}")
        say(f"[C]   phi0=0 restricted: phi = [0, {r['restricted_phi0_0_phi1']:.3f}, "
            f"{r['restricted_phi0_0_phi2']:.3f}, {r['restricted_phi0_0_phi3']:.3f}] "
            f"mean lag {r['restricted_mean_lag_q']:.2f}q  in-sample {r['restricted_rmse_pct']:.2f}%"
            f"  ||  LOO free {r['loo_rmse_free_pct']:.2f}% vs phi0=0 "
            f"{r['loo_rmse_phi0_zero_pct']:.2f}% (n={int(r['n_loo'])})")
    return lp


# ================================================================ (d) FX wedge
def stage_d(panel):
    """Is the booking-to-check-in FX remeasurement inside lambda distinguishable
    from zero?  Regress the relative deviation of lambda from its season mean on
    the FX WEDGE = stated revenue FX pts minus the ADR FX pts already carried into
    the lagged GBV base through the same kernel."""
    f = K.usable(panel).copy()
    f["adr_fx_l1"] = f["fx_pts_adr"].shift(1)
    f["adr_fx_l2"] = f["fx_pts_adr"].shift(2)
    f["wedge"] = f["fx_pts_revenue"] - (W_PUB * f["adr_fx_l1"] + (1 - W_PUB) * f["adr_fx_l2"])
    f["lam"] = K.lam_pct(f, W_PUB)
    f["lam_dev_pct"] = 100 * (f["lam"] / f.groupby("season")["lam"].transform("mean") - 1)

    def ols(sub):
        x = sub["wedge"].values
        y = sub["lam_dev_pct"].values
        X = np.column_stack([np.ones(len(x)), x])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ b
        n, k = len(x), 2
        s2 = (r ** 2).sum() / max(n - k, 1)
        se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
        return b[1], se[1], b[1] / se[1] if se[1] else np.nan, n

    out = []
    sets = {"architect_12_cells": f[f["q"].isin(sum(ACCEPT_CELLS.values(), []))],
            "all_seasons_2023Q1plus_n14": f[f["q"] >= "2023Q1"],
            "all_available": f}
    for name, sub in sets.items():
        sub = sub.dropna(subset=["wedge", "lam_dev_pct"])
        if len(sub) < 4:
            continue
        sl, se, t, n = ols(sub)
        # interval likelihood: revenue and ADR FX pts are letter-rounded integers,
        # so the wedge is only known inside a box.  Report the SET of slopes
        # attainable when each latent FX integer moves within +/- 0.5.
        rng = np.random.default_rng(7)
        slopes = []
        for _ in range(2000):
            j = sub.copy()
            j["wedge"] = ((j["fx_pts_revenue"] + rng.uniform(-.5, .5, len(j)))
                          - (W_PUB * (j["adr_fx_l1"] + rng.uniform(-.5, .5, len(j)))
                             + (1 - W_PUB) * (j["adr_fx_l2"] + rng.uniform(-.5, .5, len(j)))))
            slopes.append(ols(j)[0])
        slopes = np.array(slopes)
        out.append({"sample": name, "n": n, "slope": sl, "se": se, "t": t,
                    "p_two_sided": 2 * (1 - _norm_cdf(abs(t))),
                    "interval_set_lo": float(np.min(slopes)),
                    "interval_set_hi": float(np.max(slopes)),
                    "interval_p05": float(np.percentile(slopes, 5)),
                    "interval_p95": float(np.percentile(slopes, 95)),
                    "distinguishable_from_zero": bool(abs(t) > 2.0)})
    w = pd.DataFrame(out)
    w.to_csv(OUT / "07_fx_wedge_regression.csv", index=False)
    f[["q", "season", "fx_pts_revenue", "fx_pts_adr", "adr_fx_l1", "adr_fx_l2",
       "wedge", "lam", "lam_dev_pct"]].to_csv(OUT / "07_fx_wedge_cells.csv", index=False)
    for _, r in w.iterrows():
        say(f"[D] FX wedge {r['sample']:28s} n={int(r.n):2d} slope {r.slope:+.3f} "
            f"se {r.se:.3f} t {r.t:+.2f} p {r.p_two_sided:.2f}  interval-likelihood "
            f"slope set [{r.interval_set_lo:+.3f},{r.interval_set_hi:+.3f}]  "
            f"distinguishable from zero: {r.distinguishable_from_zero}")
    return w


def _norm_cdf(x):
    from math import erf, sqrt
    return 0.5 * (1 + erf(x / sqrt(2)))


# ================================================================ (c/backtest)
def pit_frame(panel, vintage_date, full_sample=False):
    """The kernel panel truncated to quarters PRINTED by vintage_date."""
    if full_sample:
        return K.usable(panel)
    h = history_as_of(vintage_date)
    printed = set(h["quarter"])
    return K.usable(panel[panel["q"].isin(printed)].reset_index(drop=True))


def kernel_forecast(panel, vintage_date, target_q, w, full_sample, horizon,
                    n_recent=None, min_quarter=None):
    """horizon 0: both GBV lags are printed.  horizon 1: GBV_{q-1} is NOT printed and
    is filled by the NAIVE rule GBV_{q-1} = GBV_{q-5} * (1 + last observed GBV y/y)."""
    est = pit_frame(panel, vintage_date, full_sample)
    if min_quarter is not None:
        est = est[est["q"] >= min_quarter].reset_index(drop=True)
    prt = pit_frame(panel, vintage_date, False)       # what is actually printed
    gbv = dict(zip(panel["q"], panel["gbv_musd"]))
    printed_q = set(prt["q"]) | set(pit_frame(panel, vintage_date, False)["q"])
    h = history_as_of(vintage_date)
    printed_q = set(h["quarter"])
    l1q, l2q = Q.shift(target_q, -1), Q.shift(target_q, -2)
    gbv_fill = {}
    for qq in (l1q, l2q):
        if qq in printed_q:
            gbv_fill[qq] = gbv[qq]
        else:
            hist_g = [(q_, gbv[q_]) for q_ in sorted(printed_q) if q_ in gbv and
                      not np.isnan(gbv[q_])]
            last_q = hist_g[-1][0]
            g_yoy = gbv[last_q] / gbv[Q.shift(last_q, -4)] - 1
            gbv_fill[qq] = gbv[Q.shift(qq, -4)] * (1 + g_yoy)
    b = w * gbv_fill[l1q] + (1 - w) * gbv_fill[l2q]
    season = int(target_q[-1])
    lam, n_cells = K.season_lambda(est, season, w, n_recent=n_recent)
    if not np.isfinite(lam) or n_cells == 0:
        return None
    point = lam / 100.0 * b
    rel_sd = K.relative_sigma(est, w)
    if horizon >= 1:                      # add the GBV-forecast error, naive-rule scale
        rel_sd = float(np.sqrt(rel_sd ** 2 + (w * 0.045) ** 2))
    qs = K.quantiles_lognormal(point, rel_sd)
    return {"point": point, "sd": point * rel_sd, "n_train": len(est),
            "n_cells": n_cells, "lam": lam, "base": b, **qs}


def build_object(panel, obj, w, target_metric, horizon, spec, note,
                 n_recent=None, min_quarter=None):
    tg = load_targets()
    rev4 = dict(zip(tg["quarter"], tg["revenue_musd"]))
    rows = []
    for gdate, tq_guide in GUIDE_EVENTS_ALL:
        tq = Q.shift(tq_guide, horizon)
        wins = window_of_target(tq)
        if not wins:
            continue
        for win in wins:
            if win == "LIVE":
                continue                       # LIVE handled by the live objects
            for basis in ("PIT", "full_sample"):
                f = kernel_forecast(panel, gdate, tq, w, basis == "full_sample", horizon,
                                    n_recent=n_recent, min_quarter=min_quarter)
                if f is None:
                    continue
                pt = f["point"]
                if target_metric == "revenue_yoy":
                    b4 = rev4.get(Q.shift(tq, -4))
                    if b4 is None or not np.isfinite(b4):
                        continue
                    conv = lambda v: 100.0 * (v / b4 - 1.0)  # noqa: E731
                else:
                    conv = lambda v: v  # noqa: E731
                rows.append({
                    "method": "kernel-lambda", "object": obj, "target": target_metric,
                    "quarter": tq, "vintage_date": gdate,
                    "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(gdate)),
                    "point": conv(pt), "q50": conv(pt),
                    "q05": conv(f["q05"]), "q10": conv(f["q10"]), "q25": conv(f["q25"]),
                    "q75": conv(f["q75"]), "q90": conv(f["q90"]), "q95": conv(f["q95"]),
                    "sd": abs(conv(pt + f["sd"]) - conv(pt)),
                    "window": win, "prior_basis": basis, "n_params": 5,
                    "n_train": f["n_train"], "knowable_from": gdate,
                    "spec_id": spec, "notes": note})
    df = pd.DataFrame(rows)
    if len(df):
        register(df)
    return df


# ================================================================ (e) live
def stage_e(panel, est):
    gbv = dict(zip(panel["q"], panel["gbv_musd"]))
    rows = []
    # --- 3Q26: both GBV lags printed.  NO GBV forecast is required.
    for w in [0.33, W_ALT, W_PUB]:
        lam3, n3 = K.season_lambda(est, 3, w)
        b = w * gbv["2026Q2"] + (1 - w) * gbv["2026Q1"]
        rows.append({"quarter": "2026Q3", "w": round(w, 4), "lambda_pct": lam3,
                     "n_cells": n3, "base_musd": b, "print_musd": lam3 / 100 * b,
                     "gbv_l1_musd": gbv["2026Q2"], "gbv_l2_musd": gbv["2026Q1"]})
    live3 = pd.DataFrame(rows)
    live3.to_csv(OUT / "08_live_3q26.csv", index=False)
    pub3 = float(live3.loc[live3.w.round(4) == round(W_PUB, 4), "print_musd"].iloc[0])
    b3 = float(live3.loc[live3.w.round(4) == round(W_PUB, 4), "base_musd"].iloc[0])
    l3 = float(live3.loc[live3.w.round(4) == round(W_PUB, 4), "lambda_pct"].iloc[0])
    say(f"[E] 3Q26 print object: {b3:,.0f}M x {l3:.3f}% = {pub3:,.0f}M "
        f"(w=2/3, no GBV forecast).  sensitivity w in [0.33,0.667]: "
        f"{live3.print_musd.min():,.0f}-{live3.print_musd.max():,.0f}M")

    # --- 4Q26 on a GBV_3Q26 grid
    g4 = []
    for g3 in np.arange(25900, 27001, 100):
        for w in [0.33, W_ALT, W_PUB]:
            lam4, n4 = K.season_lambda(est, 4, w)
            b = w * g3 + (1 - w) * gbv["2026Q2"]
            pr = lam4 / 100 * b
            g4.append({"quarter": "2026Q4", "gbv_3q26_musd": float(g3), "w": round(w, 4),
                       "lambda_pct": lam4, "base_musd": b, "print_musd": pr,
                       "guide_mid_musd": pr / 1.0186})
    live4 = pd.DataFrame(g4)
    live4.to_csv(OUT / "09_live_4q26_grid.csv", index=False)
    c = live4[(live4.gbv_3q26_musd == 26300) & (live4.w.round(4) == round(W_PUB, 4))].iloc[0]
    say(f"[E] 4Q26 central (GBV_3Q26=26,300, w=2/3): base {c.base_musd:,.0f}M x "
        f"{c.lambda_pct:.3f}% = print {c.print_musd:,.0f}M, guide mid "
        f"{c.guide_mid_musd:,.0f}M (cushion +1.86%).  No fee step, no FX added.")

    # --- share of quarter-q revenue whose GBV driver is already printed
    sh = []
    for label, date, tq, printed_through in [
            ("pitch_2026-10-02", "2026-10-02", "2026Q4", "2026Q2"),
            ("guide_2026-11-05", "2026-11-05", "2026Q4", "2026Q3"),
            ("guide_2027-02", "2027-02-12", "2027Q1", "2026Q4"),
            ("guide_2027-05", "2027-05-06", "2027Q2", "2027Q1")]:
        for w in [0.33, W_ALT, W_PUB]:
            l1q, l2q = Q.shift(tq, -1), Q.shift(tq, -2)
            s = (w if l1q <= printed_through else 0.0) + ((1 - w) if l2q <= printed_through else 0.0)
            sh.append({"as_of_label": label, "as_of_date": date, "quarter": tq, "w": round(w, 4),
                       "gbv_printed_through": printed_through,
                       "driver_share_printed": s})
    share = pd.DataFrame(sh)
    share.to_csv(OUT / "10_ledger_share.csv", index=False)
    for lab in share.as_of_label.unique():
        s = share[share.as_of_label == lab]
        say(f"[E] driver-printed share {lab} ({s.quarter.iloc[0]}): "
            f"w=2/3 {float(s.loc[s.w.round(4) == round(W_PUB, 4), 'driver_share_printed'].iloc[0]):.3f} | "
            f"w=0.38 {float(s.loc[s.w.round(4) == W_ALT, 'driver_share_printed'].iloc[0]):.3f}")

    # register the two live objects at TODAY
    rel_sd = K.relative_sigma(est, W_PUB)
    reg = []
    for obj, tq, pt in [("live_3q26_print", "2026Q3", pub3),
                        ("live_4q26_print", "2026Q4", float(c.print_musd))]:
        qs = K.quantiles_lognormal(pt, rel_sd)
        reg.append({"method": "kernel-lambda", "object": obj, "target": "revenue_musd",
                    "quarter": tq, "vintage_date": TODAY,
                    "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(TODAY)),
                    "point": pt, "q50": pt, **qs, "sd": pt * rel_sd,
                    "window": "LIVE", "prior_basis": "PIT", "n_params": 5,
                    "n_train": len(est), "knowable_from": "2026-08-06",
                    "spec_id": f"kernel|w={W_PUB:.4f}|season_mean|2023Q1+",
                    "notes": ("3Q26 needs no GBV forecast" if tq == "2026Q3"
                              else "4Q26 at assumed GBV_3Q26=26300")})
    dfl = pd.DataFrame(reg)
    est_full = K.usable(panel)
    fs = dfl.copy()
    fs["prior_basis"] = "full_sample"
    rs = K.relative_sigma(est_full, W_PUB)
    for i, r in fs.iterrows():
        s_ = int(r["quarter"][-1])
        lam, _ = K.season_lambda(est_full, s_, W_PUB)
        b = (W_PUB * gbv["2026Q2"] + (1 - W_PUB) * gbv["2026Q1"]) if s_ == 3 else \
            (W_PUB * 26300 + (1 - W_PUB) * gbv["2026Q2"])
        p = lam / 100 * b
        fs.loc[i, ["point", "q50", "sd"]] = [p, p, p * rs]
        for k, v in K.quantiles_lognormal(p, rs).items():
            fs.loc[i, k] = v
        fs.loc[i, "n_train"] = len(est_full)
    both = pd.concat([dfl, fs], ignore_index=True)
    both.to_csv(OUT / "13_live_registry_rows.csv", index=False)
    for obj in both["object"].unique():
        sub = both[both["object"] == obj].reset_index(drop=True)
        if not window_of_target(sub["quarter"].iloc[0]):
            # HARNESS CHANGE REQUEST: window_of_target() maps only 2026Q3 to LIVE,
            # so a 2026Q4 object cannot be registered even though README section 2.5
            # says "LIVE requires 2026Q3 or later".  Written locally instead.
            sub.to_csv(OUT / f"13_local_{obj}_registry_format.csv", index=False)
            try:
                register(sub, strict_windows=False)
                say(f"[E] {obj}: registered with strict_windows=False "
                    f"(quarter {sub['quarter'].iloc[0]} maps to no window); also written locally")
            except Exception as e:
                say(f"[E] {obj}: NOT registered ({type(e).__name__}); written locally only")
            continue
        register(sub)

    return live3, live4, share


# ================================================================ main
def main():
    panel = K.build_panel(KPI)
    tg = load_targets()
    m = tg[["quarter", "revenue_musd", "gbv_musd"]].merge(
        panel[["q", "revenue_musd", "gbv_musd"]], left_on="quarter", right_on="q",
        suffixes=("_h", "_k")).dropna()
    assert (m.revenue_musd_h - m.revenue_musd_k).abs().max() < 1e-6, "panel/harness revenue mismatch"
    assert (m.gbv_musd_h - m.gbv_musd_k).abs().max() < 1e-6, "panel/harness GBV mismatch"
    say(f"[0] KPI panel and harness targets agree on revenue and GBV over {len(m)} quarters")

    f, ok = stage_a(panel)
    if not ok:
        say("[A] ACCEPTANCE TEST FAILED -- stopping before any modelling, per the spec.")
        return 2

    summ, est = stage_b(panel)
    stage_b_cost(panel, est)
    stage_c(panel)
    stage_d(panel)

    # ---- (c) backtests
    objs = [
        ("revenue_level_next_q", W_PUB, "revenue_musd", 0,
         f"kernel|w={W_PUB:.4f}|season_mean|h0", "h0: both GBV lags printed at the guide date"),
        ("revenue_level_next_q_w038", W_ALT, "revenue_musd", 0,
         f"kernel|w={W_ALT}|season_mean|h0", "M6 weight sensitivity"),
        ("revenue_level_next_q_w033", 0.33, "revenue_musd", 0,
         "kernel|w=0.33|season_mean|h0", "lower sensitivity bound"),
        ("revenue_yoy_next_q", W_PUB, "revenue_yoy", 0,
         f"kernel|w={W_PUB:.4f}|season_mean|h0|yoy", "same object mapped to y/y growth"),
        ("revenue_level_h1", W_PUB, "revenue_musd", 1,
         f"kernel|w={W_PUB:.4f}|season_mean|h1|naive_gbv",
         "h1: GBV_(q-1) unprinted; filled by naive y/y rule"),
    ]
    variants = [
        ("revenue_level_next_q_last3", dict(n_recent=3),
         f"kernel|w={W_PUB:.4f}|season_mean_last3|h0",
         "season mean over the 3 most recent same-quarter cells only"),
        ("revenue_level_next_q_ex_covid", dict(min_quarter="2022Q1"),
         f"kernel|w={W_PUB:.4f}|season_mean|h0|est_from_2022Q1",
         "COVID-era 2021 lambda cells excluded from the estimation window"),
        ("revenue_level_next_q_last3_ex_covid", dict(n_recent=3, min_quarter="2022Q1"),
         f"kernel|w={W_PUB:.4f}|season_mean_last3|h0|est_from_2022Q1",
         "both: last-3 same-quarter cells and no 2021"),
    ]
    for obj, kw, spec, note in variants:
        objs.append((obj, W_PUB, "revenue_musd", 0, spec, note, kw))
    objs = [(o if len(o) == 7 else o + ({},)) for o in objs]

    sizes = {}
    for obj, w, tm, h, spec, note, kw in objs:
        df = build_object(panel, obj, w, tm, h, spec, note, **kw)
        sizes[obj] = len(df)
        say(f"[C] registered kernel-lambda__{obj}: {len(df)} rows "
            f"({df.window.value_counts().to_dict() if len(df) else {}})")

    live3, live4, share = stage_e(panel, est)

    # ---- (f) parameter count and pre-registration card
    pc = pd.DataFrame([
        {"object": "kernel (published)", "free_params": 5,
         "detail": "4 seasonal conversions + 1 lag weight (asserted at 2/3, counted)",
         "identities": 23, "note": "23 printed revenue identities 2021Q1-2026Q2 (22 with both lags)"},
        {"object": "lag polynomial (test only)", "free_params": 7,
         "detail": "4 seasonal conversions + 3 free simplex weights over lags 0-3",
         "identities": 21, "note": "needs three GBV lags, so 2021Q2-2026Q2"},
    ])
    pc.to_csv(OUT / "11_parameter_count.csv", index=False)

    prereg = pd.DataFrame([
        {"id": "KL-1", "statement": "3Q26 printed revenue lands in [4700, 4910] MUSD",
         "basis": "kernel w=2/3, both GBV lags printed, q10-q90",
         "resolves": "2026-11-05", "status": "open"},
        {"id": "KL-2", "statement": "4Q26 guide midpoint < 3200 (Zacks 2026-09-04)",
         "basis": "print/(1+cushion) at GBV_3Q26=26300", "resolves": "2026-11-05", "status": "open"},
        {"id": "KL-3", "statement": "phi_0 (same-quarter GBV weight) is not distinguishable from 0",
         "basis": "constrained simplex lag polynomial, block bootstrap",
         "resolves": "tested tonight", "status": "see 06_lag_polynomial.csv"},
        {"id": "KL-4", "statement": "the kernel weight is not identified better than +/-0.2",
         "basis": "LOO grid + block bootstrap on the argmin",
         "resolves": "tested tonight", "status": "see 03_weight_summary.csv"},
    ])
    prereg.to_csv(OUT / "12_prereg_card.csv", index=False)

    pd.DataFrame({"line": LOG}).to_csv(OUT / "00_run_log.csv", index=False)
    say("[done] all stages complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
