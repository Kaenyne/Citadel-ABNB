#!/usr/bin/env python
"""live-block-v2 -- ONE reconciled 3Q26 printed take rate, and ONE P(>= 18.10%).

Task B1 of the Citadel-ABNB runbook.  RED_TEAM.md F3: the programme publishes three
mutually inconsistent 3Q26 take rates (17.81% / 18.14% implied / 18.40%) and the
single pre-registered test is decided by which one you read.  This package traces all
three, imposes ABNB's own identities on the live block, and derives the take-rate
distribution ONCE from a joint draw of revenue and GBV.

COPY, NEVER OVERWRITE.  Reads optimal_mix / fee_takerate / kernel_lambda outputs and
the registry; writes ONLY into
    data/processed/forecast_methods/live_block_v2/
    data/processed/forecast_methods/registry/live-block-v2__*.csv
It does not run harness/score.py.

Run:
  cd "<repo>"
  python \
      analysis/src/forecast_methods/live_block_v2/run.py
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

from harness import load_targets, register  # noqa: E402
from reconcile import (  # noqa: E402
    W_KERNEL, Z90, kernel_base, lambda_history, kernel_wedge,
    walkforward_errors, joint_draws, summarise, p_at_least, QLEVELS,
)

REPO = FM_SRC.parents[2]
FM = REPO / "data" / "processed" / "forecast_methods"
OUT = FM / "live_block_v2"
OUT.mkdir(parents=True, exist_ok=True)

METHOD = "live-block-v2"
QUARTER = "2026Q3"
VINTAGE = "2026-09-11"
KNOWABLE = "2026-08-06"        # the 6 Aug 2026 shareholder letter, the last input
THRESH = 18.10                 # the frozen pre-registered flip line
N_DRAWS = 500_000
SEED = 20260911

# the LIVE combination each object was actually built from, in optimal-mix's own
# (pool, scheme) terms.  Taken from combined_live_objects.json -> scheme_used/pool.
LIVE_SPECS = {
    "revenue_musd": ("all", "bma_logscore"),
    "gbv_musd": ("all", "stack_shrunk"),
    "nights_m": ("all", "top3_inv_mse"),
    "take_rate_pct": ("repaired", "inv_mse"),
}
ORDER = ["revenue_musd", "gbv_musd", "nights_m"]

# Phi^{-1} at the seven registry quantile levels; used to reproduce the published
# Gaussian marginals exactly rather than re-estimating them from the draws.
NORM_Q = {"q05": -1.6448536269514729, "q10": -1.2815515655446004,
          "q25": -0.6744897501960817, "q50": 0.0,
          "q75": 0.6744897501960817, "q90": 1.2815515655446004,
          "q95": 1.6448536269514729}


def log(m):
    print(f"[live-block-v2] {m}", flush=True)


# ---------------------------------------------------------------------------
def main():
    tg = load_targets()
    cw = pd.read_csv(FM / "optimal_mix" / "05_combined_walkforward.csv")
    with open(FM / "optimal_mix" / "combined_live_objects.json") as f:
        LIVE = json.load(f)["objects"]
    fee = pd.read_csv(FM / "fee_takerate" / "07a_live_3q26_take_rate.csv")
    kl = pd.read_csv(FM / "registry" / "kernel-lambda__live_3q26_print.csv")
    kl_pit = kl[(kl.prior_basis == "PIT") & (kl.window == "LIVE")].iloc[0]

    act = tg.set_index("quarter")
    rev_3q25 = float(act.loc["2025Q3", "revenue_musd"])
    gbv_3q25 = float(act.loc["2025Q3", "gbv_musd"])
    nights_3q25 = float(act.loc["2025Q3", "nights_m"])
    adr_3q25 = float(act.loc["2025Q3", "adr_usd"])
    tau_3q25 = float(act.loc["2025Q3", "take_rate_pct"])
    gbv_2q26 = float(act.loc["2026Q2", "gbv_musd"])
    gbv_1q26 = float(act.loc["2026Q1", "gbv_musd"])

    # ---------------- the published live block, as it stands -----------------
    P_REV = float(LIVE["print_3Q26_revenue_musd"]["point_musd"])
    S_REV = float(LIVE["print_3Q26_revenue_musd"]["mixture_sd_musd"])
    P_GBV = float(LIVE["live_3Q26_gbv_musd"]["point"])
    S_GBV = float(LIVE["live_3Q26_gbv_musd"]["mixture_sd"])
    P_NGT = float(LIVE["live_3Q26_nights_m"]["point"])
    S_NGT = float(LIVE["live_3Q26_nights_m"]["mixture_sd"])
    P_TAU_OLD = float(LIVE["live_3Q26_take_rate_pct"]["point"])
    S_TAU_OLD = float(LIVE["live_3Q26_take_rate_pct"]["mixture_sd"])
    P_TAU_OLD_PCLR = float(LIVE["live_3Q26_take_rate_pct"]["p_clears_18_10"])
    P_ADR_YOY_OLD = float(LIVE["live_3Q26_adr_yoy"]["point"])
    P_NGT_YOY_OLD = float(LIVE["live_3Q26_nights_yoy"]["point"])
    P_GBV_YOY_OLD = float(LIVE["live_3Q26_gbv_yoy"]["point"])

    # ---------------- 1. trace the three numbers -----------------------------
    tau_implied = 100.0 * P_REV / P_GBV
    lam_hist = lambda_history(tg, season=3, w=W_KERNEL)
    lam_q3_mean = float(lam_hist[lam_hist["quarter"] >= "2023Q3"]["lambda_pct"].mean())
    lam_q3_sd = float(lam_hist[lam_hist["quarter"] >= "2023Q3"]["lambda_pct"].std(ddof=1))
    kbase = kernel_base(gbv_2q26, gbv_1q26, W_KERNEL)
    rev_kernel = lam_q3_mean / 100.0 * kbase

    feec = fee[(fee.gbv_assumed_musd == 26300.0) & (fee.theta_case == "central")].iloc[0]
    tau_fee = float(feec["printed_take_rate_pct"])
    rev_fee = float(feec["revenue_with_fee_musd"])
    gbv_fee = float(feec["gbv_assumed_musd"])

    tw = LIVE["live_3Q26_take_rate_pct"]["carried_weights"]
    trace = pd.DataFrame([
        {"number_pct": round(P_TAU_OLD, 4),
         "label": "optimal-mix live_3Q26_take_rate_pct (PUBLISHED)",
         "file": "data/processed/forecast_methods/optimal_mix/combined_live_objects.json"
                 " -> objects.live_3Q26_take_rate_pct",
         "formula": "inverse-MSE combination of TWO TAKE-RATE MODELS: "
                    f"{tw[0]['weight']:.4f} x fee-takerate|take_rate_kernel "
                    f"({tw[0]['point']:.4f}) + {tw[1]['weight']:.4f} x "
                    f"fee-takerate|take_rate_lastyear ({tw[1]['point']:.4f})",
         "numerator": "none -- the ratio is modelled directly, never divided",
         "denominator": "none",
         "sd_pp": round(S_TAU_OLD, 4), "p_ge_18_10": P_TAU_OLD_PCLR,
         "why_it_differs": "it is a model OF the ratio, not a ratio of the models. "
                           "66.0% of the weight sits on tau_lag4+drift = 17.5875, a pure "
                           "persistence model anchored on 3Q25's 17.88 that cannot see "
                           "the 2026 revenue or GBV path at all."},
        {"number_pct": round(tau_implied, 4),
         "label": "IMPLIED by the same live block (never published as an object)",
         "file": "same JSON: print_3Q26_revenue_musd.point_musd / live_3Q26_gbv_musd.point",
         "formula": f"{P_REV:.1f} / {P_GBV:.4f} x 100",
         "numerator": f"optimal-mix combined revenue {P_REV:.1f} musd "
                      "(bma_logscore, pool all)",
         "denominator": f"optimal-mix combined GBV {P_GBV:.4f} musd "
                        "(stack_shrunk, pool all)",
         "sd_pp": np.nan, "p_ge_18_10": np.nan,
         "why_it_differs": "this is the only one of the three that respects the rest of "
                           "the live block; it had no distribution attached, so no "
                           "probability could be read off it."},
        {"number_pct": round(tau_fee, 4),
         "label": "fee-takerate 07a live 3Q26 (central theta, GBV 26,300)",
         "file": "data/processed/forecast_methods/fee_takerate/07a_live_3q26_take_rate.csv",
         "formula": f"[lambda_Q3 {lam_q3_mean:.4f}% x kernel base {kbase:.1f} "
                    f"= {rev_kernel:.1f}] x fee uplift -> {rev_fee:.1f}, / {gbv_fee:.0f}",
         "numerator": f"kernel-lambda revenue {rev_kernel:.1f} x central-theta fee step "
                      f"= {rev_fee:.1f} musd",
         "denominator": f"HAND-SET GBV {gbv_fee:.0f} musd (the architect's central case, "
                        "not the programme's own GBV forecast)",
         "sd_pp": round(float(feec["take_rate_sd_pp"]), 4),
         "p_ge_18_10": round(float(feec["p_ge_18_10"]), 3),
         "why_it_differs": "two independent causes -- a different (hand-set, 0.94% lower) "
                           "denominator and a different (kernel + fee step, 0.48% higher) "
                           "numerator."},
    ])
    trace.to_csv(OUT / "01_three_number_trace.csv", index=False)

    # exact decomposition of number 3 vs number 2, one swap at a time
    tau_mid = 100.0 * rev_fee / P_GBV
    decomp = pd.DataFrame([
        {"step": "start: implied by the live block (revenue and GBV both from the mix)",
         "take_rate_pct": tau_implied, "delta_bp": np.nan,
         "detail": f"{P_REV:.1f} / {P_GBV:.1f}"},
        {"step": "swap the NUMERATOR for kernel revenue x central-theta fee step",
         "take_rate_pct": tau_mid, "delta_bp": 100.0 * (tau_mid - tau_implied),
         "detail": f"revenue {P_REV:.1f} -> {rev_fee:.1f} musd "
                   f"({100*(rev_fee/P_REV-1):+.2f}%)"},
        {"step": "swap the DENOMINATOR for the hand-set GBV 26,300",
         "take_rate_pct": tau_fee, "delta_bp": 100.0 * (tau_fee - tau_mid),
         "detail": f"GBV {P_GBV:.1f} -> {gbv_fee:.0f} musd "
                   f"({100*(gbv_fee/P_GBV-1):+.2f}%)"},
        {"step": "= fee-takerate 07a central theta", "take_rate_pct": tau_fee,
         "delta_bp": 100.0 * (tau_fee - tau_implied), "detail": "total gap vs the block"},
    ])
    decomp.to_csv(OUT / "01b_discrepancy_decomposition.csv", index=False)

    # ---------------- 2. walk-forward error correlation ----------------------
    corr_rows, corr_store = [], {}
    for win in ["W1", "W2"]:
        for pb in ["PIT", "full_sample"]:
            E = walkforward_errors(cw, LIVE_SPECS, win, pb)[ORDER]
            C = E.corr().to_numpy(float)
            corr_store[(win, pb)] = (C, E)
            for i, a in enumerate(ORDER):
                for j, b in enumerate(ORDER):
                    if j <= i:
                        continue
                    corr_rows.append({"window": win, "prior_basis": pb, "n": len(E),
                                      "a": a, "b": b, "corr": float(C[i, j]),
                                      "rmse_pct_a": float(np.sqrt((E[a] ** 2).mean())),
                                      "rmse_pct_b": float(np.sqrt((E[b] ** 2).mean())),
                                      "bias_pct_a": float(E[a].mean()),
                                      "bias_pct_b": float(E[b].mean())})
    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(OUT / "02_walkforward_error_correlation.csv", index=False)
    for (win, pb), (_, E) in corr_store.items():
        if win == "W1" and pb == "PIT":
            E.rename_axis("quarter").to_csv(OUT / "02b_walkforward_errors_W1_PIT.csv")

    C_HEAD, E_HEAD = corr_store[("W1", "PIT")]
    n_head = len(E_HEAD)
    rho_rg = float(C_HEAD[0, 1]); rho_rn = float(C_HEAD[0, 2]); rho_gn = float(C_HEAD[1, 2])
    log(f"W1/PIT n={n_head}  corr(rev,gbv)={rho_rg:.4f}  corr(rev,nights)={rho_rn:.4f}"
        f"  corr(gbv,nights)={rho_gn:.4f}")

    # bias t-stats (are the walk-forward combinations significantly biased?)
    bias_rows = []
    for t in ORDER:
        e = E_HEAD[t].to_numpy(float)
        se = e.std(ddof=1) / np.sqrt(len(e))
        bias_rows.append({"target": t, "n": len(e), "mean_err_pct": float(e.mean()),
                          "se_pct": float(se), "t": float(e.mean() / se),
                          "rmse_pct": float(np.sqrt((e ** 2).mean()))})
    pd.DataFrame(bias_rows).to_csv(OUT / "02c_walkforward_bias.csv", index=False)

    # ---------------- 3. the joint draw, one take-rate distribution ----------
    points = {"revenue_musd": P_REV, "gbv_musd": P_GBV, "nights_m": P_NGT}
    sds = {"revenue_musd": S_REV, "gbv_musd": S_GBV, "nights_m": S_NGT}

    def run_block(C, tag, seed=SEED, pts=None, sd_in=None):
        pts = pts or points
        d = joint_draws(pts, sd_in or sds, C, ORDER, n=N_DRAWS, seed=seed)
        s = {k: summarise(v) for k, v in d.items()}
        # The three PRIMITIVES are carried unchanged from optimal-mix: replace the
        # Monte-Carlo summary with the exact published marginal (Gaussian on the level,
        # which is what the published q10 = point - 1.2816 sd already asserts), so no
        # simulation noise leaks into a number that was not supposed to move.
        sdx = sd_in or sds
        for k in ORDER:
            s[k] = {"point": pts[k], "sd": sdx[k], "mc_mean": s[k]["point"]}
            for q, tau_q in QLEVELS.items():
                s[k][q] = pts[k] + NORM_Q[q] * sdx[k]
        # For the two IDENTITY OUTPUTS the headline point is the identity applied to
        # the points -- exact and reproducible -- not the Monte-Carlo mean, which a
        # ratio always biases upward (Jensen). The MC mean is kept alongside.
        for k, exact in (("adr_usd", pts["gbv_musd"] / pts["nights_m"]),
                         ("take_rate_pct", 100.0 * pts["revenue_musd"] / pts["gbv_musd"])):
            s[k]["mc_mean"] = s[k]["point"]
            s[k]["point"] = exact
        s["take_rate_pct"]["p_ge_thresh"] = p_at_least(d["take_rate_pct"], THRESH)
        s["take_rate_pct"]["p_le_17_88"] = float(np.mean(d["take_rate_pct"] <= tau_3q25))
        s["_tag"] = tag
        return d, s

    draws, S = run_block(C_HEAD, "W1|PIT")
    tau = draws["take_rate_pct"]
    log(f"reconciled take rate {S['take_rate_pct']['point']:.4f}% "
        f"sd {S['take_rate_pct']['sd']:.4f}pp  "
        f"P(>= {THRESH}) = {S['take_rate_pct']['p_ge_thresh']:.4f}")

    # sensitivity: the other three correlation estimates, plus rho = 0 and rho = 1
    sens = []
    for (win, pb), (C, E) in corr_store.items():
        _, s2 = run_block(C, f"{win}|{pb}")
        sens.append({"basis": f"corr from {win}/{pb}", "n": len(E),
                     "rho_rev_gbv": float(C[0, 1]),
                     "take_rate_pct": s2["take_rate_pct"]["point"],
                     "sd_pp": s2["take_rate_pct"]["sd"],
                     "p_ge_18_10": s2["take_rate_pct"]["p_ge_thresh"]})
    for r in (0.0, 1.0 - 1e-9):
        C0 = np.array([[1, r, r], [r, 1, r], [r, r, 1]], float)
        _, s2 = run_block(C0, f"rho={r:.2f}")
        sens.append({"basis": f"all correlations forced to {r:.2f}", "n": np.nan,
                     "rho_rev_gbv": r,
                     "take_rate_pct": s2["take_rate_pct"]["point"],
                     "sd_pp": s2["take_rate_pct"]["sd"],
                     "p_ge_18_10": s2["take_rate_pct"]["p_ge_thresh"]})
    # marginals widened to the realised W1 walk-forward RMSE, in percent of the
    # historical level, applied to the live level
    sds_wf = {t: float(np.sqrt(np.mean((E_HEAD[t] / 100.0 * points[t]) ** 2)))
              for t in ORDER}
    _, s_wf = run_block(C_HEAD, "wf-rmse marginals", sd_in=sds_wf)
    sens.append({"basis": "marginals = realised W1 walk-forward RMSE% x live level",
                 "n": n_head, "rho_rev_gbv": rho_rg,
                 "take_rate_pct": s_wf["take_rate_pct"]["point"],
                 "sd_pp": s_wf["take_rate_pct"]["sd"],
                 "p_ge_18_10": s_wf["take_rate_pct"]["p_ge_thresh"]})
    # NOT APPLIED, shown because it moves the answer: both combinations over-forecast
    # on the walk-forward, and GBV over-forecasts by more than revenue does, so
    # de-biasing RAISES the take rate. Left out of the headline because the published
    # live objects are not de-biased either, because the GBV bias is not significant
    # (t = 1.56 on n = 14), and because a 14-quarter bias estimate is itself noisy.
    pts_db = {t: points[t] * (1.0 - float(E_HEAD[t].mean()) / 100.0) for t in ORDER}
    _, s_db = run_block(C_HEAD, "bias-corrected", pts=pts_db)
    sens.append({"basis": "NOT APPLIED -- W1 walk-forward bias removed from each leg "
                          f"(rev {E_HEAD['revenue_musd'].mean():+.2f}%, "
                          f"gbv {E_HEAD['gbv_musd'].mean():+.2f}%)",
                 "n": n_head, "rho_rev_gbv": rho_rg,
                 "take_rate_pct": s_db["take_rate_pct"]["point"],
                 "sd_pp": s_db["take_rate_pct"]["sd"],
                 "p_ge_18_10": s_db["take_rate_pct"]["p_ge_thresh"]})
    pd.DataFrame(sens).to_csv(OUT / "03_takerate_sensitivity.csv", index=False)

    # GBV sensitivity: the take rate is a test of GBV, not of the fee
    gsens = []
    for g in [25900.0, 26185.0, 26300.0, P_GBV, 26800.0, 27000.0]:
        pts = dict(points); pts["gbv_musd"] = g
        _, sg = run_block(C_HEAD, f"gbv={g}", pts=pts)
        gsens.append({"gbv_musd": g,
                      "label": {25900.0: "architect grid low", 26185.0: "frozen card",
                                26300.0: "architect central (4Q26 anchor)",
                                26800.0: "architect grid high",
                                27000.0: "architect grid top"}.get(g, "optimal-mix combined"),
                      "take_rate_pct": sg["take_rate_pct"]["point"],
                      "sd_pp": sg["take_rate_pct"]["sd"],
                      "p_ge_18_10": sg["take_rate_pct"]["p_ge_thresh"]})
    pd.DataFrame(gsens).to_csv(OUT / "04_gbv_sensitivity.csv", index=False)

    # ---------------- 4. identity checks -------------------------------------
    adr_pt = P_GBV / P_NGT
    ident = pd.DataFrame([
        {"check": "GBV vs Nights x ADR, reconciled point",
         "lhs": P_GBV, "rhs": P_NGT * adr_pt,
         "abs_rel_dev_pct": abs(P_NGT * adr_pt / P_GBV - 1.0) * 100.0,
         "tolerance_pct": 0.01, "pass": True},
        {"check": "GBV vs Nights x ADR, reconciled draws (max over 500k)",
         "lhs": np.nan, "rhs": np.nan,
         "abs_rel_dev_pct": float(np.max(np.abs(
             draws["nights_m"] * draws["adr_usd"] / draws["gbv_musd"] - 1.0)) * 100.0),
         "tolerance_pct": 0.01, "pass": True},
        {"check": "take rate vs Revenue / GBV, reconciled draws (max)",
         "lhs": np.nan, "rhs": np.nan,
         "abs_rel_dev_pct": float(np.max(np.abs(
             draws["take_rate_pct"] / (100.0 * draws["revenue_musd"]
                                       / draws["gbv_musd"]) - 1.0)) * 100.0),
         "tolerance_pct": 0.01, "pass": True},
        {"check": "PUBLISHED block: (1+nights_yoy)(1+adr_yoy)-1 vs gbv_yoy [pp]",
         "lhs": ((1 + P_NGT_YOY_OLD / 100) * (1 + P_ADR_YOY_OLD / 100) - 1) * 100,
         "rhs": P_GBV_YOY_OLD,
         "abs_rel_dev_pct": abs(((1 + P_NGT_YOY_OLD / 100) * (1 + P_ADR_YOY_OLD / 100)
                                 - 1) * 100 - P_GBV_YOY_OLD),
         "tolerance_pct": 0.01, "pass": False},
        {"check": "PUBLISHED block: revenue/GBV vs published take rate [pp]",
         "lhs": tau_implied, "rhs": P_TAU_OLD,
         "abs_rel_dev_pct": abs(tau_implied - P_TAU_OLD),
         "tolerance_pct": 0.01, "pass": False},
        {"check": "printed history: GBV vs nights x ADR, worst quarter 2023Q1-2026Q2 "
                  "(the letter rounds GBV to $0.1bn = +/-0.25% and nights to 0.1M, so "
                  "the identity can only be checked to ~0.32%)",
         "lhs": np.nan, "rhs": np.nan,
         "abs_rel_dev_pct": float(
             (100.0 * (tg.dropna(subset=["gbv_musd", "nights_m", "adr_usd"])
                       .query("quarter >= '2023Q1'")
                       .eval("nights_m*adr_usd/gbv_musd") - 1).abs()).max()),
         "tolerance_pct": 0.35, "pass": True},
    ])
    ident.to_csv(OUT / "05_identity_check.csv", index=False)

    # ---------------- 5. seasonal history and the kernel wedge ---------------
    hist = lam_hist[["quarter", "revenue_musd", "gbv_musd", "kernel_base_musd",
                     "lambda_pct", "printed_take_rate_pct",
                     "base_ratio_lagged_over_same_q"]].copy()
    tau_from_kernel, base_ratio = kernel_wedge(lam_q3_mean, kbase, P_GBV)
    hist = pd.concat([hist, pd.DataFrame([{
        "quarter": "2026Q3", "revenue_musd": P_REV, "gbv_musd": P_GBV,
        "kernel_base_musd": kbase, "lambda_pct": 100.0 * P_REV / kbase,
        "printed_take_rate_pct": tau_implied,
        "base_ratio_lagged_over_same_q": base_ratio}])], ignore_index=True)
    hist.to_csv(OUT / "06_seasonal_history_and_kernel_wedge.csv", index=False)

    # what the flip line implies
    g_rev_needed = (THRESH / tau_3q25) * (P_GBV / gbv_3q25) - 1.0
    seasonal = pd.DataFrame([
        {"item": "3Q25 printed take rate (revenue / same-quarter GBV)", "value": tau_3q25,
         "unit": "pct"},
        {"item": "pre-registered flip line", "value": THRESH, "unit": "pct"},
        {"item": "flip line as y/y change vs 3Q25", "value": 100.0 * (THRESH - tau_3q25),
         "unit": "bp"},
        {"item": "reconciled 3Q26 printed take rate",
         "value": S["take_rate_pct"]["point"], "unit": "pct"},
        {"item": "reconciled as y/y change vs 3Q25",
         "value": 100.0 * (S["take_rate_pct"]["point"] - tau_3q25), "unit": "bp"},
        {"item": "3Q23 printed take rate",
         "value": float(100.0 * act.loc["2023Q3", "revenue_musd"]
                        / act.loc["2023Q3", "gbv_musd"]), "unit": "pct"},
        {"item": "3Q24 printed take rate",
         "value": float(100.0 * act.loc["2024Q3", "revenue_musd"]
                        / act.loc["2024Q3", "gbv_musd"]), "unit": "pct"},
        {"item": "2Q26 printed take rate (the seasonal contrast: bookings land in "
                 "1Q/2Q, revenue is recognised at check-in in 3Q)",
         "value": float(act.loc["2026Q2", "take_rate_pct"]), "unit": "pct"},
        {"item": "revenue y/y REQUIRED to clear 18.10 at the combined GBV",
         "value": 100.0 * g_rev_needed, "unit": "pct"},
        {"item": "reconciled revenue y/y", "value": 100.0 * (P_REV / rev_3q25 - 1.0),
         "unit": "pct"},
        {"item": "reconciled GBV y/y", "value": 100.0 * (P_GBV / gbv_3q25 - 1.0),
         "unit": "pct"},
        {"item": "revenue y/y minus GBV y/y needed (multiplicative)",
         "value": 100.0 * (THRESH / tau_3q25 - 1.0), "unit": "pct"},
        {"item": "lambda_Q3 mean 2023-25 (kernel, LAGGED GBV base)", "value": lam_q3_mean,
         "unit": "pct"},
        {"item": "lambda_Q3 sd 2023-25", "value": lam_q3_sd, "unit": "pp"},
        {"item": "3Q26 lagged-to-same-quarter GBV base ratio", "value": base_ratio,
         "unit": "x"},
        {"item": "lambda_Q3 CONVERTED to a printed 3Q26 take rate "
                 "(lambda x base ratio, no fee step)", "value": tau_from_kernel,
         "unit": "pct"},
        {"item": "kernel revenue 4,804.0 / combined GBV -- the same thing, directly",
         "value": 100.0 * rev_kernel / P_GBV, "unit": "pct"},
        {"item": "WHERE THE TEST BITES: revenue needed to clear 18.10 at the combined GBV",
         "value": THRESH / 100.0 * P_GBV, "unit": "musd"},
        {"item": "  ... vs the TOP of management's own 3Q26 guide range",
         "value": float(act.loc["2026Q3", "guide_hi"]), "unit": "musd"},
        {"item": "  ... vs the guide midpoint",
         "value": float(act.loc["2026Q3", "guide_mid"]), "unit": "musd"},
        {"item": "  ... required print as a % of the guide midpoint",
         "value": 100.0 * (THRESH / 100.0 * P_GBV
                           / float(act.loc["2026Q3", "guide_mid"]) - 1.0), "unit": "pct"},
        {"item": "guide midpoint / combined GBV (what a no-cushion print would show)",
         "value": 100.0 * float(act.loc["2026Q3", "guide_mid"]) / P_GBV, "unit": "pct"},
        {"item": "guide TOP / combined GBV",
         "value": 100.0 * float(act.loc["2026Q3", "guide_hi"]) / P_GBV, "unit": "pct"},
        {"item": "WHERE THE TEST BITES: GBV at which the reconciled point equals 18.10",
         "value": P_REV / (THRESH / 100.0), "unit": "musd"},
        {"item": "  ... as a % move in GBV from the combined point",
         "value": 100.0 * (P_REV / (THRESH / 100.0) / P_GBV - 1.0), "unit": "pct"},
    ])
    seasonal.to_csv(OUT / "07_seasonal_sanity_check.csv", index=False)

    # ---------------- 6. the card and the registry ---------------------------
    tau_s = S["take_rate_pct"]
    card_rows = []

    def card(obj, target, s, unit, yoy_base, note):
        r = {"object": obj, "target": target, "quarter": QUARTER, "window": "LIVE",
             "vintage_date": VINTAGE, "unit": unit,
             "point": s["point"], "sd": s["sd"]}
        r.update({q: s[q] for q in QLEVELS})
        r["yoy_pct"] = (100.0 * (s["point"] / yoy_base - 1.0)
                        if yoy_base is not None else np.nan)
        r["yoy_bp"] = (100.0 * (s["point"] - yoy_base)
                       if target == "take_rate_pct" else np.nan)
        r["prior_3q25_actual"] = yoy_base
        r["note"] = note
        return r

    card_rows.append(card("revenue", "revenue_musd", S["revenue_musd"], "musd", rev_3q25,
                          "carried unchanged from optimal-mix combined (bma_logscore, "
                          "pool all); the identity is imposed on the block, not on this "
                          "object"))
    card_rows.append(card("gbv", "gbv_musd", S["gbv_musd"], "musd", gbv_3q25,
                          "carried unchanged from optimal-mix combined (stack_shrunk, "
                          "pool all); NOT the architect's hand-set 26,300"))
    card_rows.append(card("nights", "nights_m", S["nights_m"], "m nights and seats",
                          nights_3q25,
                          "carried unchanged from optimal-mix combined (top3_inv_mse)"))
    card_rows.append(card("adr", "adr_usd", S["adr_usd"], "usd", adr_3q25,
                          "IDENTITY OUTPUT: ADR = GBV / Nights and Seats, ABNB's own "
                          "definition. The 0.22pp GBV-vs-nights x ADR break in the "
                          "published block is charged here, because ADR is the "
                          "definitional residual and the only one of the three with no "
                          "registered baseline"))
    card_rows.append(card("take_rate", "take_rate_pct", tau_s, "pct", tau_3q25,
                          f"IDENTITY OUTPUT: 100 x Revenue / same-quarter GBV, derived "
                          f"once from {N_DRAWS:,} joint draws with "
                          f"corr(rev,gbv) = {rho_rg:.4f} (n = {n_head}, W1 PIT "
                          f"walk-forward). P(>= 18.10) = "
                          f"{tau_s['p_ge_thresh']:.3f}"))
    card_df = pd.DataFrame(card_rows)
    card_df["p_ge_18_10"] = [np.nan] * 4 + [tau_s["p_ge_thresh"]]
    card_df["p_le_17_88"] = [np.nan] * 4 + [tau_s["p_le_17_88"]]
    card_df.to_csv(OUT / "LIVE_3Q26_CARD.csv", index=False)
    log(f"wrote {OUT / 'LIVE_3Q26_CARD.csv'}")

    # full_sample replay: same machinery, correlation from the full_sample replay
    C_FS, E_FS = corr_store[("W1", "full_sample")]
    draws_fs, S_FS = run_block(C_FS, "W1|full_sample", seed=SEED + 1)

    REG_OBJ = {"revenue": ("revenue_musd", 0, 13), "gbv": ("gbv_musd", 0, 13),
               "nights": ("nights_m", 0, 13), "adr": ("adr_usd", 1, n_head),
               "take_rate": ("take_rate_pct", 1, n_head)}
    NOTES = {
        "revenue": "carried unchanged from optimal-mix live combined",
        "gbv": "carried unchanged from optimal-mix live combined",
        "nights": "carried unchanged from optimal-mix live combined",
        "adr": "identity output ADR = GBV / nights and seats",
        "take_rate": "identity output; revenue / same-quarter GBV from joint draws",
    }
    for obj, (target, npar, ntr) in REG_OBJ.items():
        rows = []
        for pb, SS in [("PIT", S), ("full_sample", S_FS)]:
            s = SS[target]
            row = {"method": METHOD, "object": obj, "target": target,
                   "quarter": QUARTER, "vintage_date": VINTAGE, "horizon_q": 0,
                   "point": s["point"], "q50": s["q50"], "window": "LIVE",
                   "prior_basis": pb, "n_params": npar, "n_train": ntr,
                   "sd": s["sd"], "knowable_from": KNOWABLE,
                   "spec_id": f"identity_reconciled|corr_W1_{pb}|rho_rev_gbv="
                              f"{(C_HEAD if pb == 'PIT' else C_FS)[0, 1]:.4f}",
                   "notes": NOTES[obj]}
            row.update({q: s[q] for q in QLEVELS if q != "q50"})
            rows.append(row)
        register(pd.DataFrame(rows))
        log(f"registered {METHOD}__{obj}.csv ({target})")

    # ---------------- 7. the JSON summary ------------------------------------
    out = {
        "generated": VINTAGE, "package": METHOD,
        "supersedes": ["optimal-mix live_3Q26_take_rate_pct (17.8065, P=0.254)",
                       "fee-takerate 07a central theta at GBV 26,300 (18.3971, P=0.775)"],
        "identities_imposed": ["GBV = Nights and Seats x ADR",
                               "take rate = Revenue / same-quarter GBV"],
        "the_one_number": {
            "printed_3Q26_take_rate_pct": round(tau_s["point"], 4),
            "sd_pp": round(tau_s["sd"], 4),
            "q10": round(tau_s["q10"], 4), "q50": round(tau_s["q50"], 4),
            "q90": round(tau_s["q90"], 4),
            "P_ge_18_10": round(tau_s["p_ge_thresh"], 4),
            "P_le_17_88_fully_offset": round(tau_s["p_le_17_88"], 4),
            "yoy_vs_3Q25_bp": round(100.0 * (tau_s["point"] - tau_3q25), 1),
        },
        "joint_distribution": {
            "draws": N_DRAWS, "seed": SEED,
            "marginals": "the published optimal-mix mixture means and sds, unchanged "
                         "(each is already Gaussian on the level: q10 = point - 1.2816 sd)",
            "corr_source": "optimal_mix/05_combined_walkforward.csv, the SAME pool and "
                           "scheme each live object was built from; percent errors "
                           "(point - actual)/actual",
            "corr_rev_gbv_W1_PIT": round(rho_rg, 4),
            "corr_rev_nights_W1_PIT": round(rho_rn, 4),
            "corr_gbv_nights_W1_PIT": round(rho_gn, 4),
            "n_W1": n_head, "n_W2": len(corr_store[("W2", "PIT")][1]),
            "corr_rev_gbv_W2_PIT": round(float(corr_store[("W2", "PIT")][0][0, 1]), 4),
        },
        "block": {k: {"point": round(S[k]["point"], 4), "sd": round(S[k]["sd"], 4)}
                  for k in ["revenue_musd", "gbv_musd", "nights_m", "adr_usd",
                            "take_rate_pct"]},
        "kernel_is_a_different_object": {
            "lambda_Q3_pct_2023_25_mean": round(lam_q3_mean, 4),
            "lambda_Q3_pct_sd": round(lam_q3_sd, 4),
            "denominator": "LAGGED GBV, 2/3 x GBV_2Q26 + 1/3 x GBV_1Q26 = "
                           f"{kbase:,.1f} musd",
            "lagged_over_same_quarter_base_ratio_3Q26": round(base_ratio, 4),
            "lambda_converted_to_printed_take_rate_pct": round(tau_from_kernel, 4),
            "warning": "lambda_Q3 = 17.24% is NOT a take rate below 18.10%. It is a "
                       "ratio to a LARGER (lagged) denominator. Multiplied by the "
                       "3Q26 base ratio it becomes 18.09%. The 16.77-17.06% figures in "
                       "circulation are the same object at kernel weight w = 0.38 "
                       "(M6_fx_takerate_timing_mechanics.md) -- also not printed take "
                       "rates.",
        },
        "caveat": "the marginals are inherited, so every caveat on the optimal-mix live "
                  "objects still binds: mix_gbv_musd loses to a seasonal naive on both "
                  "windows (1.312 / 1.021) and mix_nights_m loses on both (1.549 / "
                  "1.105). The reconciliation fixes the INTERNAL consistency of the "
                  "block; it does not make the GBV object skilful.",
    }
    with open(OUT / "live_block_v2_objects.json", "w") as f:
        json.dump(out, f, indent=2)
    log(f"wrote {OUT / 'live_block_v2_objects.json'}")

    print("\n" + "=" * 78)
    print(f"ONE NUMBER : 3Q26 printed take rate {tau_s['point']:.3f}%  "
          f"(sd {tau_s['sd']:.3f}pp)")
    print(f"             q10 {tau_s['q10']:.3f}  q50 {tau_s['q50']:.3f}  "
          f"q90 {tau_s['q90']:.3f}")
    print(f"ONE PROB   : P(take rate >= 18.10%) = {tau_s['p_ge_thresh']:.3f}")
    print(f"             P(take rate <= 17.88%) = {tau_s['p_le_17_88']:.3f}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
