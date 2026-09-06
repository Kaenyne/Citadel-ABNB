"""
04_margin_predictability.py -- can Adjusted EBITDA margin surprises be predicted from the
cost-line trends?

Reads data/processed/predictive/04_print_features.csv (built by 04_reaction_function.py) and
data/processed/hotel_price_monitor_monthly.csv.

Margin surprise, per quarter from 1Q23 (14 quarters):
  surprise_vs_bound_pts     actual margin minus the numeric bound guided for that quarter at the prior
                            print (floor / point / ceiling), economic sign: + = margin above the bound
  surprise_specsign_pts     as specified in the brief: for ceiling guides, ceiling minus actual
                            (+ = came in below the ceiling, i.e. the guide held); floor/point: actual minus bound
  surprise_yoy_pts          actual minus same-quarter-prior-year margin

Predictors: trailing (t-1, known before the print) S&M cash growth, S&M deleverage, ops-and-support cash
per night y/y, take-rate change, SBC %-of-revenue change; FX impact on revenue growth by year as stated in the
letters (2022 -6, 2023 +1, 2024 0, 2025 0, 1H26 +3); quarter-average CPI lodging y/y. Contemporaneous
versions (from the print itself) are included as an explanatory, not predictive, comparison.

Statistics: Pearson / Spearman with p, permutation p (20k shuffles), leave-one-out univariate OLS RMSE versus
(a) the naive "same as last quarter's surprise" and (b) the leave-one-out mean.

Margin model: margin_yoy_pts = b0 + b1 * ADR ex-FX y/y + b2 * S&M deleverage, leave-one-out, and RMSE of the
implied margin forecast (same-quarter-prior-year + fitted change) against the guide bound used as a forecast.

Outputs: data/processed/predictive/04_margin_predictability.csv
Run: python analysis/src/predictive/04_margin_predictability.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data" / "processed" / "predictive"
N_PERM = 20000
RNG = np.random.default_rng(20260906)

FX_BY_YEAR = {2021: np.nan, 2022: -6.0, 2023: 1.0, 2024: 0.0, 2025: 0.0, 2026: 3.0}
# letter-stated ADR ex-FX y/y where given (hotel_price_monitor_monthly.csv, abnb_adr_exfx_yoy_pct)
ADR_EXFX_LETTER = {"2025Q4": 3.0, "2026Q1": 4.0, "2026Q2": 4.0}


def q_idx(std: str) -> int:
    y, q = std.split("Q")
    return int(y) * 4 + int(q) - 1


feat = pd.read_csv(OUT_DIR / "04_print_features.csv")
feat["i"] = feat["print_quarter"].map(q_idx)
feat = feat.set_index("i").sort_index()
feat["year"] = feat["print_quarter"].str[:4].astype(int)
feat["fx_pts"] = feat["year"].map(FX_BY_YEAR)
feat["adr_exfx_yoy"] = feat["adr_yoy"] - feat["fx_pts"]
for q, v in ADR_EXFX_LETTER.items():
    feat.loc[q_idx(q), "adr_exfx_yoy"] = v
    feat.loc[q_idx(q), "fx_pts"] = feat.loc[q_idx(q), "adr_yoy"] - v

# surprises
feat["surprise_vs_bound_pts"] = feat["margin_vs_bound_pts"]
feat["surprise_specsign_pts"] = feat["margin_surprise_specsign_pts"]
feat["surprise_yoy_pts"] = feat["margin_yoy_pts"]

# lagged predictors (known at the prior print)
for c in ["sm_cash_yoy", "sm_delev_pts", "ops_per_night_yoy", "take_rate_chg_bps", "sbc_pct_rev_chg_pts",
          "surprise_vs_bound_pts", "surprise_specsign_pts", "surprise_yoy_pts", "adr_exfx_yoy"]:
    feat[f"{c}_lag1"] = feat[c].shift(1)
feat["sm_delev_trail2"] = feat["sm_delev_pts"].shift(1).rolling(2).mean()
feat["hotel_cpi_q_yoy"] = feat["pre_hotel_cpi_q_yoy"]

SAMPLE = feat[feat.index >= q_idx("2023Q1")].copy()
TARGETS = ["surprise_vs_bound_pts", "surprise_specsign_pts", "surprise_yoy_pts"]
PRED_LAG = ["sm_cash_yoy_lag1", "sm_delev_pts_lag1", "sm_delev_trail2", "ops_per_night_yoy_lag1",
            "take_rate_chg_bps_lag1", "sbc_pct_rev_chg_pts_lag1", "adr_exfx_yoy_lag1", "fx_pts", "hotel_cpi_q_yoy",
            "pre_this_guide_mid_yoy", "pre_this_guide_width_pct", "pre_prev_rev_beat_mid_pct", "pre_prev_streak_signed"]
PRED_CONTEMP = ["sm_cash_yoy", "sm_delev_pts", "ops_per_night_yoy", "take_rate_chg_bps", "sbc_pct_rev_chg_pts",
                "adr_exfx_yoy", "adr_yoy", "rev_beat_mid_pct", "nights_accel"]


def loo_uni(x, y):
    n = len(x)
    pred = np.empty(n)
    mean_pred = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b1, b0 = np.polyfit(x[m], y[m], 1)
        pred[i] = b0 + b1 * x[i]
        mean_pred[i] = y[m].mean()
    return pred, mean_pred


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


rows = []
for tgt in TARGETS:
    naive_col = f"{tgt}_lag1"
    for kind, preds in [("lagged (pre-print)", PRED_LAG), ("contemporaneous (in the print)", PRED_CONTEMP)]:
        for f in preds:
            d = SAMPLE[[f, tgt, naive_col]].dropna()
            n = len(d)
            if n < 6:
                rows.append(dict(block="univariate", kind=kind, target=tgt, predictor=f, n=n))
                continue
            x, y, nv = d[f].to_numpy(float), d[tgt].to_numpy(float), d[naive_col].to_numpy(float)
            r, p = stats.pearsonr(x, y)
            rho, ps = stats.spearmanr(x, y)
            cnt = sum(abs(np.corrcoef(x, RNG.permutation(y))[0, 1]) >= abs(r) - 1e-12 for _ in range(N_PERM))
            pred, mean_pred = loo_uni(x, y)
            rows.append(dict(block="univariate", kind=kind, target=tgt, predictor=f, n=n,
                             pearson_r=r, pearson_p=p, spearman_rho=rho, spearman_p=ps,
                             perm_p=(cnt + 1) / (N_PERM + 1),
                             loo_rmse=rmse(y, pred), naive_last_rmse=rmse(y, nv), loo_mean_rmse=rmse(y, mean_pred),
                             loo_r2_vs_mean=1 - np.sum((y - pred) ** 2) / np.sum((y - mean_pred) ** 2),
                             beats_naive_last=int(rmse(y, pred) < rmse(y, nv)),
                             beats_loo_mean=int(rmse(y, pred) < rmse(y, mean_pred))))

# baselines for the surprise itself
for tgt in TARGETS:
    d = SAMPLE[[tgt, f"{tgt}_lag1"]].dropna()
    y, nv = d[tgt].to_numpy(float), d[f"{tgt}_lag1"].to_numpy(float)
    _, mean_pred = loo_uni(nv, y)
    rows.append(dict(block="baseline", kind="baseline", target=tgt, predictor="zero (guide/SQPY exactly right)", n=len(y),
                     loo_rmse=rmse(y, np.zeros_like(y)), mean_surprise=y.mean(), median_surprise=np.median(y),
                     share_positive=(y > 0).mean()))
    rows.append(dict(block="baseline", kind="baseline", target=tgt, predictor="naive last-quarter surprise", n=len(y),
                     loo_rmse=rmse(y, nv), naive_last_rmse=rmse(y, nv), loo_mean_rmse=rmse(y, mean_pred),
                     pearson_r=stats.pearsonr(nv, y)[0], pearson_p=stats.pearsonr(nv, y)[1]))

# ----------------------------------------------------------------------------
# margin model: margin_yoy = b0 + b1*ADR ex-FX y/y + b2*S&M deleverage
# ----------------------------------------------------------------------------
def fit_model(df, cols, label):
    d = df[cols + ["margin_yoy_pts", "margin_pct", "margin_bound_pct", "print_quarter"]].dropna(subset=cols + ["margin_yoy_pts"])
    n = len(d)
    X = d[cols].to_numpy(float)
    y = d["margin_yoy_pts"].to_numpy(float)
    A = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    dof = n - A.shape[1]
    se = np.sqrt(np.diag(resid @ resid / dof * np.linalg.inv(A.T @ A)))
    pv = 2 * stats.t.sf(np.abs(beta / se), dof)
    r2 = 1 - (resid @ resid) / ((y - y.mean()) ** 2).sum()
    loo = np.empty(n)
    signs = np.zeros(len(cols))
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b, *_ = np.linalg.lstsq(A[m], y[m], rcond=None)
        loo[i] = A[i] @ b
        signs += np.sign(b[1:]) == np.sign(beta[1:])
    sqpy = d["margin_pct"].to_numpy(float) - y  # same-quarter-prior-year margin
    actual = d["margin_pct"].to_numpy(float)
    pred_margin_loo = sqpy + loo
    has_bound = d["margin_bound_pct"].notna().to_numpy()
    out = dict(block="margin_model", kind=label, target="margin_pct", predictor=" + ".join(cols), n=n,
               r2_full=r2, loo_r2=1 - ((y - loo) ** 2).sum() / ((y - y.mean()) ** 2).sum(),
               rmse_model_loo=rmse(actual, pred_margin_loo),
               rmse_sqpy_naive=rmse(actual, sqpy),
               rmse_model_loo_on_bound_rows=rmse(actual[has_bound], pred_margin_loo[has_bound]),
               rmse_guide_bound=rmse(actual[has_bound], d["margin_bound_pct"].to_numpy(float)[has_bound]),
               rmse_sqpy_on_bound_rows=rmse(actual[has_bound], sqpy[has_bound]),
               n_bound_rows=int(has_bound.sum()),
               coefs="; ".join([f"b0={beta[0]:.2f} (p={pv[0]:.2f})"] +
                               [f"{c}: b={beta[k + 1]:.3f} (p={pv[k + 1]:.2f}, sign_stab={signs[k] / n:.2f})"
                                for k, c in enumerate(cols)]),
               quarters=" ".join(d["print_quarter"]))
    rows.append(out)
    return d.assign(loo_pred_margin=pred_margin_loo, sqpy=sqpy)


full = feat[feat.index >= q_idx("2022Q1")]
m_full = fit_model(full, ["adr_exfx_yoy", "sm_delev_pts"], "all quarters with cost lines (from 2022Q1)")
m_s = fit_model(SAMPLE, ["adr_exfx_yoy", "sm_delev_pts"], "guided sample (from 2023Q1)")
fit_model(SAMPLE, ["adr_exfx_yoy"], "guided sample, ADR ex-FX only")
fit_model(SAMPLE, ["sm_delev_pts"], "guided sample, S&M deleverage only")
fit_model(SAMPLE, ["adr_yoy", "sm_delev_pts"], "guided sample, reported ADR (no FX adj)")
# lagged-input version: only what is known before the print
fit_model(SAMPLE, ["adr_exfx_yoy_lag1", "sm_delev_pts_lag1"], "guided sample, LAGGED inputs (pre-print)")

# ----------------------------------------------------------------------------
# 3Q26 nowcast from the lagged (pre-print) inputs known today: 2Q26 S&M deleverage, 2Q26 ADR ex-FX,
# and the 3Q26 ceiling guide of 50.1% ("down slightly" vs 3Q25's 50.1%)
# ----------------------------------------------------------------------------
last = feat.loc[q_idx("2026Q2")]
sm_lag, adr_lag = last["sm_delev_pts"], last["adr_exfx_yoy"]
d = SAMPLE[["sm_delev_pts_lag1", "surprise_vs_bound_pts"]].dropna()
b1, b0 = np.polyfit(d["sm_delev_pts_lag1"], d["surprise_vs_bound_pts"], 1)
nowcast_uni = b0 + b1 * sm_lag
d2 = SAMPLE[["adr_exfx_yoy_lag1", "sm_delev_pts_lag1", "margin_yoy_pts"]].dropna()
A = np.column_stack([np.ones(len(d2)), d2[["adr_exfx_yoy_lag1", "sm_delev_pts_lag1"]].to_numpy(float)])
bb, *_ = np.linalg.lstsq(A, d2["margin_yoy_pts"].to_numpy(float), rcond=None)
nowcast_2f = bb[0] + bb[1] * adr_lag + bb[2] * sm_lag
Q3_25_MARGIN, Q3_26_CEILING = float(feat.loc[q_idx("2025Q3"), "margin_pct"]), 50.1
rows.append(dict(block="nowcast_3Q26", kind="lagged univariate: surprise_vs_bound ~ S&M delev(t-1)", target="3Q26 margin",
                 predictor=f"sm_delev_2Q26={sm_lag:.1f}", n=len(d), nowcast_surprise_vs_bound_pts=nowcast_uni,
                 nowcast_margin_pct=Q3_26_CEILING + nowcast_uni, guide_bound_pct=Q3_26_CEILING, sqpy_margin_pct=Q3_25_MARGIN,
                 coefs=f"b0={b0:.2f}, b1={b1:.3f}"))
rows.append(dict(block="nowcast_3Q26", kind="lagged 2-factor: margin_yoy ~ ADR exFX(t-1) + S&M delev(t-1)", target="3Q26 margin",
                 predictor=f"adr_exfx_2Q26={adr_lag:.1f}, sm_delev_2Q26={sm_lag:.1f}", n=len(d2),
                 nowcast_margin_yoy_pts=nowcast_2f, nowcast_margin_pct=Q3_25_MARGIN + nowcast_2f,
                 guide_bound_pct=Q3_26_CEILING, sqpy_margin_pct=Q3_25_MARGIN,
                 coefs=f"b0={bb[0]:.2f}, b_adr={bb[1]:.3f}, b_sm={bb[2]:.3f}"))

res = pd.DataFrame(rows)
res.to_csv(OUT_DIR / "04_margin_predictability.csv", index=False, float_format="%.4f")

# per-quarter table for the note
tbl = SAMPLE[["print_quarter", "margin_pct", "margin_bound_type", "margin_bound_pct", "surprise_vs_bound_pts",
              "surprise_specsign_pts", "surprise_yoy_pts", "sm_delev_pts_lag1", "ops_per_night_yoy_lag1",
              "take_rate_chg_bps_lag1", "sbc_pct_rev_chg_pts_lag1", "fx_pts", "hotel_cpi_q_yoy", "adr_exfx_yoy",
              "sm_delev_pts"]].copy()
tbl = tbl.merge(m_s[["print_quarter", "loo_pred_margin"]], on="print_quarter", how="left")
tbl.to_csv(OUT_DIR / "04_margin_predictability_quarters.csv", index=False, float_format="%.2f")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print(tbl.round(2).to_string(index=False))
u = res[res.block == "univariate"].copy()
for tgt in TARGETS:
    print(f"\n--- predictors of {tgt} ---")
    print(u[u.target == tgt].sort_values("pearson_r", key=abs, ascending=False)[
        ["kind", "predictor", "n", "pearson_r", "pearson_p", "spearman_rho", "perm_p", "loo_rmse", "naive_last_rmse",
         "loo_mean_rmse", "beats_naive_last", "beats_loo_mean"]].round(3).to_string(index=False))
print("\n--- baselines ---")
print(res[res.block == "baseline"][["target", "predictor", "n", "loo_rmse", "mean_surprise", "median_surprise", "share_positive", "pearson_r", "pearson_p"]].round(3).to_string(index=False))
print("\n--- 3Q26 nowcast ---")
print(res[res.block == "nowcast_3Q26"][["kind", "predictor", "n", "nowcast_surprise_vs_bound_pts", "nowcast_margin_yoy_pts",
                                        "nowcast_margin_pct", "guide_bound_pct", "sqpy_margin_pct", "coefs"]].round(2).to_string(index=False))
print("\n--- margin models ---")
print(res[res.block == "margin_model"][["kind", "predictor", "n", "r2_full", "loo_r2", "rmse_model_loo", "rmse_sqpy_naive",
                                        "n_bound_rows", "rmse_model_loo_on_bound_rows", "rmse_guide_bound", "rmse_sqpy_on_bound_rows", "coefs"]].round(3).to_string(index=False))
