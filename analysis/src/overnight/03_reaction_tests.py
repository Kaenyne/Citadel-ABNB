"""Workstream 03: do call-language features explain the post-print stock reaction?

Reads
  data/processed/overnight/03_call_features.csv   per-call language features (03_call_features.py)
  data/processed/abnb_earnings_reactions.csv       1/5/20-session ABNB minus QQQ excess returns per print
                                                   (Theo's market_returns.csv; 20-day missing for 2026Q2)

Writes
  data/processed/overnight/03_reaction_tests.csv      every test: feature x horizon x sample, Pearson r, Spearman rho,
                                                      permutation p, leave-one-out R2 vs a zero-mean baseline, sign-hit rate
  data/processed/overnight/03_reaction_summary.csv    the features that pass a BH 10% screen on any horizon, with the
                                                      total number of tests run so the reader can discount them
  analysis/figures/overnight/03_feature_vs_reaction.png  scatter panels for the six headline features

Method
  n = 23 prints (22 for the 20-day horizon; 22 for change-in-feature tests). Smallest detectable |r| at n = 23,
  two-sided 5%, is about 0.41. Every feature is tested on three horizons and two samples (all prints; 2023Q1 onward,
  n = 14) so the test count is large; the summary reports Benjamini-Hochberg q-values across the whole grid.
  Leave-one-out: univariate OLS fitted on n-1 prints, predict the held-out print, R2_loo = 1 - SSE_loo / SSE_zero
  where SSE_zero is the error from predicting the sample mean excess return (recomputed without the held-out print).
  Permutation p: 5,000 shuffles of the return vector.

Point-in-time: call features are known at ~17:30 ET on print day, after the letter and before the next open, so
they can explain the day-1 reaction but are not a pre-print predictor of anything.

Run: py -3.13 analysis/src/overnight/03_reaction_tests.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
FIG = ROOT / "analysis" / "figures" / "overnight"
FIG.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(3)

feat = pd.read_csv(OUT / "03_call_features.csv")
rx = pd.read_csv(ROOT / "data" / "processed" / "abnb_earnings_reactions.csv")
df = feat.merge(rx[["quarter", "excess_1d_pct", "excess_5d_pct", "excess_20d_pct"]], on="quarter", how="left")

THEMES = ["demand_macro", "pricing_adr", "take_rate_fees", "marketing", "margins_profitability", "supply_hosts",
          "regulation", "ai", "new_businesses", "international", "buybacks_sbc", "competition", "long_term_targets"]

LEVEL_FEATURES = (
    ["prepared_words", "qa_mgmt_words", "qa_share_of_mgmt_words", "n_analysts", "n_analyst_turns", "n_analyst_questions",
     "ceo_share_prepared", "ceo_share_qa", "ceo_share_total", "cfo_share_total",
     "lm_net_prepared", "lm_net_qa", "lm_net_total", "lm_neg_prepared_per1k", "lm_neg_qa_per1k",
     "lm_unc_prepared_per1k", "lm_unc_qa_per1k", "hedge_prepared_per1k", "hedge_qa_per1k",
     "tone_gap_qa_minus_prepared", "hedge_gap_qa_minus_prepared",
     "analyst_lm_net_per1k", "analyst_neg_kw_per_question", "analyst_pos_kw_per_question",
     "n_numbers_prepared", "numbers_prepared_per1k", "numbers_qa_per1k", "fwd_prepared_per1k", "fwd_qa_per1k",
     "n_guide_decline_phrases_qa", "n_declines_hand_verified"]
    + [f"theme_{t}_share_total" for t in THEMES]
    + [f"theme_{t}_share_prepared" for t in THEMES]
)
CHANGE_FEATURES = [f"d_theme_{t}_share_total" for t in THEMES] + [
    "d_lm_net_total", "d_lm_net_prepared", "d_lm_net_qa", "d_hedge_prepared_per1k", "d_hedge_qa_per1k",
    "d_numbers_prepared_per1k", "d_analyst_lm_net_per1k", "d_n_analyst_questions", "d_ceo_share_total"]
HORIZONS = ["excess_1d_pct", "excess_5d_pct", "excess_20d_pct"]
SAMPLES = {"all": lambda d: d, "post2022": lambda d: d[d.quarter >= "2023Q1"]}


def loo_r2(x, y):
    n = len(x)
    sse_m, sse_0 = 0.0, 0.0
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        b, a = np.polyfit(x[m], y[m], 1)
        sse_m += (y[i] - (a + b * x[i])) ** 2
        sse_0 += (y[i] - y[m].mean()) ** 2
    return 1 - sse_m / sse_0


def perm_p(x, y, r_obs, n_perm=5000):
    cnt = 0
    for _ in range(n_perm):
        r = np.corrcoef(x, rng.permutation(y))[0, 1]
        if abs(r) >= abs(r_obs):
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


rows = []
for sname, sel in SAMPLES.items():
    d0 = sel(df)
    for kind, feats in (("level", LEVEL_FEATURES), ("change_vs_prior_call", CHANGE_FEATURES)):
        for f in feats:
            for h in HORIZONS:
                d = d0[[f, h]].apply(pd.to_numeric, errors="coerce").dropna()
                if len(d) < 8 or d[f].std() == 0:
                    continue
                x, y = d[f].values.astype(float), d[h].values.astype(float)
                r = np.corrcoef(x, y)[0, 1]
                rho = stats.spearmanr(x, y).correlation
                p_perm = perm_p(x, y, r)
                r2 = loo_r2(x, y)
                # sign test: does above-median feature go with positive excess return?
                hi = x > np.median(x)
                sign_hit = np.mean((y[hi] > 0)) if hi.any() else np.nan
                rows.append({"sample": sname, "kind": kind, "feature": f, "horizon": h, "n": len(d), "pearson_r": round(r, 3),
                             "spearman_rho": round(rho, 3), "perm_p": round(p_perm, 4), "loo_r2_vs_mean": round(r2, 3),
                             "mean_excess_above_median": round(y[hi].mean(), 2), "mean_excess_below_median": round(y[~hi].mean(), 2),
                             "share_positive_above_median": round(sign_hit, 2)})

res = pd.DataFrame(rows)
# Benjamini-Hochberg across the whole grid
res = res.sort_values("perm_p").reset_index(drop=True)
m = len(res)
res["bh_q"] = (res["perm_p"] * m / (np.arange(m) + 1)).round(3)
res["bh_q"] = res["bh_q"][::-1].cummin()[::-1].round(3)
res = res.sort_values(["sample", "kind", "horizon", "perm_p"]).reset_index(drop=True)
res.to_csv(OUT / "03_reaction_tests.csv", index=False)

n_tests = len(res)
summ = res[(res.perm_p < 0.05)].copy()
summ["n_tests_total"] = n_tests
summ["expected_false_positives_at_5pct"] = round(0.05 * n_tests, 1)
summ.to_csv(OUT / "03_reaction_summary.csv", index=False)
print(f"tests run: {n_tests}; nominal p<0.05: {len(summ)}; expected by chance: {0.05*n_tests:.1f}; BH q<0.10: {(res.bh_q<0.10).sum()}; BH q<0.25: {(res.bh_q<0.25).sum()}")
print(summ.sort_values("perm_p")[["sample", "kind", "feature", "horizon", "n", "pearson_r", "spearman_rho", "perm_p", "loo_r2_vs_mean", "bh_q"]].to_string(index=False))
print("\nbest loo_r2 by horizon (all prints, level features):")
for h in HORIZONS:
    sub = res[(res["sample"] == "all") & (res.kind == "level") & (res.horizon == h)].sort_values("loo_r2_vs_mean", ascending=False).head(5)
    print(sub[["feature", "n", "pearson_r", "perm_p", "loo_r2_vs_mean"]].to_string(index=False))

# figure: six headline features vs day-1 excess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
panels = [("theme_demand_macro_share_total", "Macro/softness sentence share (all mgmt)"),
          ("d_theme_demand_macro_share_total", "Change in macro share vs prior call"),
          ("lm_net_qa", "LM net tone, management Q&A (per 1k words)"),
          ("tone_gap_qa_minus_prepared", "Tone gap: Q&A minus prepared"),
          ("hedge_qa_per1k", "Hedging words, management Q&A (per 1k)"),
          ("n_numbers_prepared", "Numeric quantifications in prepared remarks")]
fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
for ax, (f, title) in zip(axes.flat, panels):
    d = df[[f, "excess_1d_pct", "quarter"]].apply(lambda c: pd.to_numeric(c, errors="ignore")).dropna()
    ax.scatter(d[f], d["excess_1d_pct"], s=28, color="#1f5f8b")
    for _, r in d.iterrows():
        if abs(r["excess_1d_pct"]) >= 8:
            ax.annotate(r["quarter"], (r[f], r["excess_1d_pct"]), fontsize=7, xytext=(3, 2), textcoords="offset points")
    rr = np.corrcoef(d[f].astype(float), d["excess_1d_pct"].astype(float))[0, 1]
    ax.set_title(f"{title}\nr = {rr:+.2f}, n = {len(d)}", fontsize=9)
    ax.axhline(0, color="grey", lw=0.6)
    ax.set_ylabel("Day-1 excess vs QQQ, %", fontsize=8)
    ax.tick_params(labelsize=8)
fig.suptitle("ABNB earnings calls Q4 2020 to Q2 2026: call language vs day-1 excess return (features known only at the call)", fontsize=10)
fig.tight_layout()
fig.savefig(FIG / "03_feature_vs_reaction.png", dpi=150)
print("wrote figure")


# ==================================================================================================
# Part 2: are these correlations anything more than a shared time trend, and do they add anything
# to the numbers the market already had at 16:05 ET?
#
# Two controls:
#   time      linear index over the 23 prints. Reactions improved over 2025-26 and several language
#             features (prepared_words, quantification, long-term-target talk) trend the same way,
#             so a raw correlation can be pure trend. We report the feature's own correlation with
#             time and the partial correlation of feature vs reaction after removing time from both.
#   numbers   the print itself: revenue beat vs guide midpoint, next-quarter guide acceleration, and
#             the change in year-over-year nights growth. Source data/processed/abnb_reaction_inputs.csv
#             (1Q22 onward, n = 18) plus nights growth from abnb_driver_history_quarterly.csv.
#             The predictive-study note found the sign of nights acceleration sets the day-1 reaction
#             in 17 of 21 prints, so this is the right benchmark to beat.
# Writes data/processed/overnight/03_reaction_controls.csv
# ==================================================================================================
def _resid(y, X):
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in X])
    beta, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return np.asarray(y, float) - X @ beta


drv = pd.read_csv(ROOT / "data" / "processed" / "abnb_driver_history_quarterly.csv")
drv["quarter_std"] = "20" + drv.quarter.str[-2:] + "Q" + drv.quarter.str[0]
drv = drv.sort_values("quarter_std")
drv["nights_yoy"] = 100 * (drv.nights_m / drv.nights_m.shift(4) - 1)
drv["nights_accel"] = drv.nights_yoy - drv.nights_yoy.shift(1)
ri = pd.read_csv(ROOT / "data" / "processed" / "abnb_reaction_inputs.csv")
ri["quarter_std"] = "20" + ri.print_quarter.str[-2:] + "Q" + ri.print_quarter.str[0]

ctl = (df.merge(drv[["quarter_std", "nights_yoy", "nights_accel"]], left_on="quarter", right_on="quarter_std", how="left")
         .merge(ri[["quarter_std", "beat_vs_mid_pct", "guide_accel_pts"]], on="quarter_std", how="left"))
ctl["time_idx"] = np.arange(len(ctl), dtype=float)

CTL_FEATURES = [f for f in LEVEL_FEATURES + CHANGE_FEATURES]
crows = []
for f in CTL_FEATURES:
    for h in HORIZONS:
        base = ctl[[f, h, "time_idx"]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(base) < 10 or base[f].std() == 0:
            continue
        x, y, t = base[f].values.astype(float), base[h].values.astype(float), base["time_idx"].values
        r_raw = np.corrcoef(x, y)[0, 1]
        r_time = np.corrcoef(x, t)[0, 1]
        rx, ry = _resid(x, [t]), _resid(y, [t])
        r_detr = np.corrcoef(rx, ry)[0, 1]
        p_detr = perm_p(rx, ry, r_detr, 2000)
        row = {"feature": f, "horizon": h, "n_raw": len(base), "r_raw": round(r_raw, 3),
               "r_feature_vs_time": round(r_time, 3), "r_detrended": round(r_detr, 3), "perm_p_detrended": round(p_detr, 4)}
        # control for the print's own numbers
        sub = ctl[[f, h, "beat_vs_mid_pct", "guide_accel_pts", "nights_accel"]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(sub) >= 12 and sub[f].std() > 0:
            X = [sub["beat_vs_mid_pct"].values, sub["guide_accel_pts"].values, sub["nights_accel"].values]
            rxn, ryn = _resid(sub[f].values.astype(float), X), _resid(sub[h].values.astype(float), X)
            r_num = np.corrcoef(rxn, ryn)[0, 1]
            row.update({"n_numctl": len(sub), "r_ctl_numbers": round(r_num, 3),
                        "perm_p_ctl_numbers": round(perm_p(rxn, ryn, r_num, 2000), 4)})
        crows.append(row)

ctlres = pd.DataFrame(crows).sort_values(["horizon", "perm_p_detrended"])
ctlres.to_csv(OUT / "03_reaction_controls.csv", index=False)
n_ctl = len(ctlres)
print(f"\ncontrol tests: {n_ctl}; detrended perm p<0.05: {(ctlres.perm_p_detrended<0.05).sum()} "
      f"(expected by chance {0.05*n_ctl:.1f}); numbers-controlled p<0.05: {(ctlres.get('perm_p_ctl_numbers', pd.Series(dtype=float))<0.05).sum()}")
print("\ntop 12 by detrended day-1 correlation:")
print(ctlres[ctlres.horizon == "excess_1d_pct"].reindex(
    ctlres[ctlres.horizon == "excess_1d_pct"].r_detrended.abs().sort_values(ascending=False).index).head(12).to_string(index=False))

# how much of the raw signal survives detrending, for the six headline features
print("\nheadline features, raw vs detrended vs numbers-controlled (day-1 excess):")
head = ["theme_long_term_targets_share_prepared", "theme_international_share_total", "prepared_words",
        "n_numbers_prepared", "lm_net_qa", "tone_gap_qa_minus_prepared", "hedge_qa_per1k",
        "analyst_lm_net_per1k", "n_analyst_questions", "d_theme_demand_macro_share_total"]
print(ctlres[(ctlres.horizon == "excess_1d_pct") & (ctlres.feature.isin(head))].to_string(index=False))


# ==================================================================================================
# Part 3: Benjamini-Hochberg over the control grid, and the only question that matters for a model:
# does adding one language feature to a numbers-only day-1 model beat the numbers-only model
# out of sample (leave-one-out)?  Baseline: excess_1d ~ beat_vs_mid + guide_accel + nights_accel.
# ==================================================================================================
c = ctlres.dropna(subset=["perm_p_detrended"]).sort_values("perm_p_detrended").reset_index(drop=True)
mm = len(c)
c["bh_q_detrended"] = (c["perm_p_detrended"] * mm / (np.arange(mm) + 1))
c["bh_q_detrended"] = c["bh_q_detrended"][::-1].cummin()[::-1].round(3)
c.sort_values(["horizon", "perm_p_detrended"]).to_csv(OUT / "03_reaction_controls.csv", index=False)
print(f"\nBH over {mm} detrended control tests: q<0.10 -> {(c.bh_q_detrended<0.10).sum()}, q<0.25 -> {(c.bh_q_detrended<0.25).sum()}")
print(c.head(6)[["feature", "horizon", "r_detrended", "perm_p_detrended", "bh_q_detrended"]].to_string(index=False))


def loo_multi(X, y):
    X = np.asarray(X, float); y = np.asarray(y, float); n = len(y)
    sse_m = sse_0 = 0.0
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        A = np.column_stack([np.ones(m.sum()), X[m]])
        beta, *_ = np.linalg.lstsq(A, y[m], rcond=None)
        sse_m += (y[i] - (np.r_[1.0, X[i]] @ beta)) ** 2
        sse_0 += (y[i] - y[m].mean()) ** 2
    return 1 - sse_m / sse_0


inc = []
base_cols = ["beat_vs_mid_pct", "guide_accel_pts", "nights_accel"]
for h in HORIZONS:
    b = ctl[base_cols + [h]].apply(pd.to_numeric, errors="coerce").dropna()
    r2_base = loo_multi(b[base_cols].values, b[h].values)
    for f in CTL_FEATURES:
        s = ctl[base_cols + [f, h]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(s) < 14 or s[f].std() == 0:
            continue
        r2_b = loo_multi(s[base_cols].values, s[h].values)
        r2_f = loo_multi(s[base_cols + [f]].values, s[h].values)
        inc.append({"horizon": h, "feature": f, "n": len(s), "loo_r2_numbers_only": round(r2_b, 3),
                    "loo_r2_numbers_plus_feature": round(r2_f, 3), "delta_loo_r2": round(r2_f - r2_b, 3)})
incr = pd.DataFrame(inc).sort_values(["horizon", "delta_loo_r2"], ascending=[True, False])
incr.to_csv(OUT / "03_reaction_incremental.csv", index=False)
print("\nincremental leave-one-out R2 over a numbers-only day-1 model (n = 17 prints with all inputs):")
d1 = incr[incr.horizon == "excess_1d_pct"]
print(f"  numbers-only LOO R2 = {d1.loo_r2_numbers_only.iloc[0]:+.3f}; features that improve it: "
      f"{(d1.delta_loo_r2>0).sum()} of {len(d1)}")
print(d1.head(8).to_string(index=False))
print("\nworst 4 (language actively hurts):")
print(d1.tail(4).to_string(index=False))
