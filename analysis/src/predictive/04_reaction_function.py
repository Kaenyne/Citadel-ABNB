"""
04_reaction_function.py -- what explains Airbnb's earnings-day stock reaction,
and which of it is knowable before the print.

Inputs (all relative to repo root):
  data/external/abnb_earnings_reactions.csv           ABNB / QQQ 1, 5, 20-session moves per print
  data/processed/abnb_revenue_guidance_vs_actual.csv  next-quarter revenue guide vs actual
  data/processed/abnb_quarterly_kpis_from_study.csv   nights, GBV, ADR, revenue, adj EBITDA, 1Q21-2Q26
  data/processed/abnb_quarterly_cost_stack_exsbc.csv  cash cost lines, SBC, per-night costs
  data/external/guidance_items_with_margin.csv        Theo's guidance_items incl. 44 adj_ebitda_margin rows
  data/processed/hotel_price_monitor_monthly.csv      CPI lodging y/y by month (pre-print macro read)
  data/external/abnb_daily_close.csv                  ABNB closes (pre-print run-up)

Outputs:
  data/processed/predictive/04_print_features.csv     one row per print (2021Q1-2026Q2), features + targets
  data/processed/predictive/04_reaction_results.csv   long table: univariate, multivariate, two-way sorts, pre-print

2020 quarterly KPIs are hand-entered from the shareholder letters (needed for 2021 y/y):
revenue 842/335/1342/859, nights 56.7/28.0/61.8/46.3 M, GBV 6.8/3.2/8.0/5.9 B, adj EBITDA -334/-397/501/-21.
They reproduce the letter-stated 2021 growth rates (Q1'21 nights +13%, Q2 +197%, Q3 +29%, Q4 +59%).

Run: python analysis/src/predictive/04_reaction_function.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data" / "processed" / "predictive"
OUT_DIR.mkdir(parents=True, exist_ok=True)
N_PERM = 20000
RNG = np.random.default_rng(20260906)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def q_std(label: str) -> str:
    """'1Q21' -> '2021Q1'; '2021Q1' passes through."""
    label = label.strip()
    if label[0].isdigit() and label[1] == "Q":
        return f"20{label[2:]}Q{label[0]}"
    return label


def q_idx(std: str) -> int:
    y, q = std.split("Q")
    return int(y) * 4 + int(q) - 1


def idx_q(i: int) -> str:
    return f"{i // 4}Q{i % 4 + 1}"


def pct(a, b):
    return (a / b - 1.0) * 100.0


def corr_block(x: pd.Series, y: pd.Series, n_perm: int = N_PERM) -> dict:
    d = pd.concat([x, y], axis=1).dropna()
    n = len(d)
    out = dict(n=n, pearson_r=np.nan, pearson_p=np.nan, spearman_rho=np.nan,
               spearman_p=np.nan, perm_p=np.nan, loo_rmse=np.nan, naive_rmse=np.nan,
               loo_r2=np.nan)
    if n < 6:
        return out
    xv, yv = d.iloc[:, 0].to_numpy(float), d.iloc[:, 1].to_numpy(float)
    if np.std(xv) == 0 or np.std(yv) == 0:
        return out
    r, p = stats.pearsonr(xv, yv)
    rho, ps = stats.spearmanr(xv, yv)
    # permutation p: shuffle y, two-sided on |r|
    cnt = 0
    for _ in range(n_perm):
        rp = np.corrcoef(xv, RNG.permutation(yv))[0, 1]
        if abs(rp) >= abs(r) - 1e-12:
            cnt += 1
    perm_p = (cnt + 1) / (n_perm + 1)
    # leave-one-out univariate OLS vs leave-one-out mean
    loo_pred = np.empty(n)
    naive_pred = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b1, b0 = np.polyfit(xv[m], yv[m], 1)
        loo_pred[i] = b0 + b1 * xv[i]
        naive_pred[i] = yv[m].mean()
    loo_rmse = float(np.sqrt(np.mean((yv - loo_pred) ** 2)))
    naive_rmse = float(np.sqrt(np.mean((yv - naive_pred) ** 2)))
    loo_r2 = 1.0 - np.sum((yv - loo_pred) ** 2) / np.sum((yv - naive_pred) ** 2)
    out.update(pearson_r=r, pearson_p=p, spearman_rho=rho, spearman_p=ps, perm_p=perm_p,
               loo_rmse=loo_rmse, naive_rmse=naive_rmse, loo_r2=loo_r2)
    return out


def ols_loo(X: np.ndarray, y: np.ndarray):
    """OLS with intercept; returns coefs, full R2, LOO R2, sign stability per coef, p-values."""
    n, k = X.shape
    A = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    ss_res = float(resid @ resid)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot
    dof = n - k - 1
    sigma2 = ss_res / dof
    cov = sigma2 * np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    tvals = beta / se
    pvals = 2 * stats.t.sf(np.abs(tvals), dof)
    loo = np.empty(n)
    naive = np.empty(n)
    signs = np.zeros(k)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b, *_ = np.linalg.lstsq(A[m], y[m], rcond=None)
        loo[i] = A[i] @ b
        naive[i] = y[m].mean()
        signs += (np.sign(b[1:]) == np.sign(beta[1:]))
    loo_r2 = 1 - ((y - loo) ** 2).sum() / ((y - naive) ** 2).sum()
    return dict(beta=beta, r2=r2, loo_r2=loo_r2, sign_stab=signs / n, p=pvals,
                loo_rmse=float(np.sqrt(np.mean((y - loo) ** 2))),
                naive_rmse=float(np.sqrt(np.mean((y - naive) ** 2))))


# ----------------------------------------------------------------------------
# 1. quarterly panel 2020Q1 - 2026Q2
# ----------------------------------------------------------------------------
kpi = pd.read_csv(ROOT / "data/processed/abnb_quarterly_kpis_from_study.csv")
kpi["q"] = kpi["quarter"].map(q_std)
stack = pd.read_csv(ROOT / "data/processed/abnb_quarterly_cost_stack_exsbc.csv")
stack["q"] = stack["quarter"].map(q_std)

k2020 = pd.DataFrame({
    "q": ["2020Q1", "2020Q2", "2020Q3", "2020Q4"],
    "nights_m": [56.7, 28.0, 61.8, 46.3],
    "gbv_b": [6.8, 3.2, 8.0, 5.9],
    "revenue_musd": [842.0, 335.0, 1342.0, 859.0],
    "adj_ebitda_musd": [-334.0, -397.0, 501.0, -21.0],
})
panel = pd.concat([k2020, kpi[["q", "nights_m", "gbv_b", "revenue_musd", "adj_ebitda_musd"]]],
                  ignore_index=True)
panel["adr"] = panel["gbv_b"] * 1000 / panel["nights_m"]
panel["take_rate_pct"] = panel["revenue_musd"] / (panel["gbv_b"] * 1000) * 100
panel["margin_pct"] = panel["adj_ebitda_musd"] / panel["revenue_musd"] * 100
panel = panel.merge(stack[["q", "sm_cash", "ops_cash", "sbc_total", "ops_cash_per_night",
                           "sm_cash_pct_rev", "ops_cash_pct_rev"]], on="q", how="left")
panel["i"] = panel["q"].map(q_idx)
panel = panel.set_index("i").sort_index()


def lag(col, k):
    return panel[col].shift(k)


panel["rev_yoy"] = pct(panel["revenue_musd"], lag("revenue_musd", 4))
panel["nights_yoy"] = pct(panel["nights_m"], lag("nights_m", 4))
panel["gbv_yoy"] = pct(panel["gbv_b"], lag("gbv_b", 4))
panel["adr_yoy"] = pct(panel["adr"], lag("adr", 4))
panel["rev_accel"] = panel["rev_yoy"] - panel["rev_yoy"].shift(1)
panel["nights_accel"] = panel["nights_yoy"] - panel["nights_yoy"].shift(1)
panel["gbv_accel"] = panel["gbv_yoy"] - panel["gbv_yoy"].shift(1)
panel["take_rate_chg_bps"] = (panel["take_rate_pct"] - lag("take_rate_pct", 4)) * 100
panel["margin_yoy_pts"] = panel["margin_pct"] - lag("margin_pct", 4)
panel["sm_cash_yoy"] = pct(panel["sm_cash"], lag("sm_cash", 4))
panel["sm_delev_pts"] = panel["sm_cash_yoy"] - panel["rev_yoy"]
panel["ops_per_night_yoy"] = pct(panel["ops_cash_per_night"], lag("ops_cash_per_night", 4))
panel["sbc_pct_rev"] = panel["sbc_total"] / panel["revenue_musd"] * 100
panel["sbc_pct_rev_chg_pts"] = panel["sbc_pct_rev"] - lag("sbc_pct_rev", 4)
panel["rev_yoy_trail4"] = panel["rev_yoy"].rolling(4).mean()

# ----------------------------------------------------------------------------
# 2. revenue guidance (issued at print t for quarter t+1)
# ----------------------------------------------------------------------------
g = pd.read_csv(ROOT / "data/processed/abnb_revenue_guidance_vs_actual.csv")
g["i_target"] = g["guided_quarter"].map(q_idx)
g["i_issued"] = g["issued_on_call"].map(q_idx)
g = g.set_index("i_target")
beat_mid = g["actual_vs_mid_pct"]  # indexed by target quarter, realised at that print
beat_mid_trail4 = beat_mid.rolling(4).mean()  # avg of last 4 realised beats up to and incl. target quarter

# ----------------------------------------------------------------------------
# 3. margin guidance items
# ----------------------------------------------------------------------------
gi = pd.read_csv(ROOT / "data/external/guidance_items_with_margin.csv")
gi = gi[gi["metric_code"] == "adj_ebitda_margin"].copy()
gi["issued_q"] = gi["guidance_event_id"].str.extract(r"ABNB-(\d{4}Q\d)-")[0]
gi["i_issued"] = gi["issued_q"].map(q_idx)
gi["i_target"] = gi["target_period"].map(q_idx)
gi["is_fy"] = gi["derivation_formula"].fillna("").str.startswith("FULL-YEAR")


def bound_of(row):
    mt = row["measure_type"]
    if mt == "absolute_floor":
        return row["value_low"]
    if mt == "absolute_ceiling":
        return row["value_high"]
    if mt == "absolute_point":
        return row["value_mid"]
    return np.nan


gi["bound"] = gi.apply(bound_of, axis=1)
nextq = gi[(~gi["is_fy"]) & (gi["i_target"] == gi["i_issued"] + 1)].set_index("i_target")
fy = gi[gi["is_fy"]].copy()
# FY floor action at each print: compare to the prior print's guide for the same FY
TYPE_RANK = {"absolute_ceiling": 0, "absolute_point": 1, "absolute_floor": 2, "qualitative_direction": -1}
fy["type_rank"] = fy["measure_type"].map(TYPE_RANK)
fy = fy.sort_values("i_issued")
fy_action = {}
for i_issued, grp in fy.groupby("i_issued"):
    row = grp.iloc[-1]
    if pd.isna(row["bound"]):
        fy_action[i_issued] = "none"
        continue
    prev = fy[(fy["i_target"] == row["i_target"]) & (fy["i_issued"] < i_issued) & fy["bound"].notna()]
    if prev.empty:
        fy_action[i_issued] = "introduced"
        continue
    prow = prev.sort_values("i_issued").iloc[-1]
    dv = row["bound"] - prow["bound"]
    if dv > 0.25 or (abs(dv) <= 0.25 and row["type_rank"] > prow["type_rank"]):
        fy_action[i_issued] = "raised"
    elif dv < -0.25 or (abs(dv) <= 0.25 and row["type_rank"] < prow["type_rank"]):
        fy_action[i_issued] = "lowered"
    else:
        fy_action[i_issued] = "held"
ACTION_SCORE = {"raised": 1.0, "introduced": 0.5, "held": 0.0, "none": 0.0, "lowered": -1.0}

# ----------------------------------------------------------------------------
# 4. reactions, hotel CPI, pre-print run-up
# ----------------------------------------------------------------------------
rx = pd.read_csv(ROOT / "data/external/abnb_earnings_reactions.csv")
rx["i"] = rx["quarter"].map(q_idx)
rx = rx.set_index("i")

cpi = pd.read_csv(ROOT / "data/processed/hotel_price_monitor_monthly.csv")
cpi["dt"] = pd.to_datetime(cpi["month"])
cpi["i"] = cpi["dt"].dt.year * 4 + (cpi["dt"].dt.month - 1) // 3
cpi_q = cpi.groupby("i")["cpi_lodging_yoy_pct"].mean()

px = pd.read_csv(ROOT / "data/external/abnb_daily_close.csv", parse_dates=["Date"]).sort_values("Date")
px = px.set_index("Date")["Close"]


def runup_20d(reaction_date: str) -> float:
    """ABNB close-to-close move over the 20 sessions ending the session before the reaction day."""
    d = pd.Timestamp(reaction_date)
    before = px[px.index < d]
    if len(before) < 21:
        return np.nan
    return pct(before.iloc[-1], before.iloc[-21])


# ----------------------------------------------------------------------------
# 5. assemble one row per print, 2021Q1 .. 2026Q2
# ----------------------------------------------------------------------------
rows = []
for i in range(q_idx("2021Q1"), q_idx("2026Q2") + 1):
    p = panel.loc[i]
    r = {"print_quarter": idx_q(i), "reaction_date": rx["reaction_date"].get(i)}
    # --- contemporaneous (in the letter) ---
    r["rev_beat_mid_pct"] = beat_mid.get(i, np.nan)
    r["rev_beat_high_pct"] = g["actual_vs_high_pct"].get(i, np.nan)
    for c in ["rev_yoy", "rev_accel", "nights_yoy", "nights_accel", "gbv_yoy", "gbv_accel",
              "adr_yoy", "take_rate_chg_bps", "margin_pct", "margin_yoy_pts", "sm_cash_yoy",
              "sm_delev_pts", "ops_per_night_yoy", "sbc_pct_rev_chg_pts"]:
        r[c] = p[c]
    # margin vs the bound guided for THIS quarter at the prior print
    if i in nextq.index and pd.notna(nextq.loc[i, "bound"]):
        b = nextq.loc[i]
        r["margin_bound_type"] = b["measure_type"].replace("absolute_", "")
        r["margin_bound_pct"] = b["bound"]
        r["margin_vs_bound_pts"] = p["margin_pct"] - b["bound"]  # economic sign: + = above bound
        if b["measure_type"] == "absolute_floor":
            met = p["margin_pct"] >= b["bound"] - 0.5
        elif b["measure_type"] == "absolute_ceiling":
            met = p["margin_pct"] <= b["bound"] + 0.5
        else:
            met = abs(p["margin_pct"] - b["bound"]) <= 1.0
        r["margin_guide_met"] = int(bool(met))
        # spec'd alternative: ceiling minus actual so "positive means beat" for ceiling guides
        r["margin_surprise_specsign_pts"] = (b["bound"] - p["margin_pct"]
                                             if b["measure_type"] == "absolute_ceiling"
                                             else p["margin_pct"] - b["bound"])
    else:
        r.update(margin_bound_type="none", margin_bound_pct=np.nan, margin_vs_bound_pts=np.nan,
                 margin_guide_met=np.nan, margin_surprise_specsign_pts=np.nan)
    # next-quarter guide issued at this print
    if (i + 1) in g.index and g.loc[i + 1, "i_issued"] == i:
        mid = g.loc[i + 1, "guide_mid_musd"]
        base = panel.loc[i - 3, "revenue_musd"]  # same quarter prior year of t+1
        guide_yoy = pct(mid, base)
        r["next_guide_mid_yoy"] = guide_yoy
        r["guide_implied_accel_pts"] = guide_yoy - p["rev_yoy"]
        r["next_guide_width_pct"] = g.loc[i + 1, "range_width_pct_of_mid"]
        cushion = beat_mid_trail4.get(i, np.nan)
        if pd.isna(cushion):
            cushion = beat_mid.loc[:i].mean() if (beat_mid.index <= i).any() else np.nan
        r["trail4_cushion_pct"] = cushion
        r["guide_vs_cushion_trend_pts"] = (pct(mid * (1 + cushion / 100), base) - p["rev_yoy_trail4"]
                                           if pd.notna(cushion) else np.nan)
    else:
        r.update(next_guide_mid_yoy=np.nan, guide_implied_accel_pts=np.nan, next_guide_width_pct=np.nan,
                 trail4_cushion_pct=np.nan, guide_vs_cushion_trend_pts=np.nan)
    r["fy_floor_action"] = fy_action.get(i, "none")
    r["fy_floor_action_score"] = ACTION_SCORE[r["fy_floor_action"]]
    r["fy_floor_raised"] = int(r["fy_floor_action"] == "raised")
    # --- targets ---
    r["excess_1d"] = rx["excess_1d_pct"].get(i, np.nan)
    r["excess_5d"] = rx["excess_5d_pct"].get(i, np.nan)
    r["excess_20d"] = rx["excess_20d_pct"].get(i, np.nan)
    r["abnb_1d"] = rx["abnb_1d_pct"].get(i, np.nan)
    # --- pre-print (knowable before print t) ---
    r["pre_prev_excess_1d"] = rx["excess_1d_pct"].get(i - 1, np.nan)
    # signed streak of same-sign 1-day excess reactions through t-1
    s = 0
    j = i - 1
    sign0 = np.sign(rx["excess_1d_pct"].get(j, np.nan))
    while j in rx.index and np.sign(rx.loc[j, "excess_1d_pct"]) == sign0 and sign0 != 0:
        s += 1
        j -= 1
    r["pre_prev_streak_signed"] = s * sign0 if sign0 != 0 else 0
    r["pre_prev_rev_beat_mid_pct"] = beat_mid.get(i - 1, np.nan)
    r["pre_this_guide_width_pct"] = g["range_width_pct_of_mid"].get(i, np.nan)
    r["pre_this_guide_mid_yoy"] = (pct(g.loc[i, "guide_mid_musd"], panel.loc[i - 4, "revenue_musd"])
                                   if i in g.index else np.nan)
    r["pre_prev_fy_floor_action_score"] = ACTION_SCORE[fy_action.get(i - 1, "none")]
    r["pre_prev_sm_delev_pts"] = panel["sm_delev_pts"].get(i - 1, np.nan)
    r["pre_trail4_sm_delev_pts"] = panel["sm_delev_pts"].loc[i - 4:i - 1].mean() if i - 4 in panel.index else np.nan
    r["pre_prev_margin_vs_bound_pts"] = rows[-1]["margin_vs_bound_pts"] if rows else np.nan
    r["pre_prev_nights_accel"] = panel["nights_accel"].get(i - 1, np.nan)
    r["pre_hotel_cpi_q_yoy"] = cpi_q.get(i, np.nan)
    r["pre_runup_20d_pct"] = runup_20d(r["reaction_date"]) if isinstance(r["reaction_date"], str) else np.nan
    rows.append(r)

feat = pd.DataFrame(rows)
feat.to_csv(OUT_DIR / "04_print_features.csv", index=False, float_format="%.3f")

# ----------------------------------------------------------------------------
# 6. tests
# ----------------------------------------------------------------------------
TARGETS = ["excess_1d", "excess_5d", "excess_20d"]
CONTEMP = ["rev_beat_mid_pct", "rev_beat_high_pct", "rev_yoy", "rev_accel", "nights_yoy",
           "nights_accel", "gbv_yoy", "gbv_accel", "adr_yoy", "take_rate_chg_bps", "margin_yoy_pts",
           "margin_vs_bound_pts", "margin_guide_met", "next_guide_mid_yoy", "guide_implied_accel_pts",
           "guide_vs_cushion_trend_pts", "fy_floor_action_score", "fy_floor_raised", "sm_delev_pts",
           "ops_per_night_yoy", "sbc_pct_rev_chg_pts"]
PRE = [c for c in feat.columns if c.startswith("pre_")]

SAMPLES = {
    "all": feat["print_quarter"].notna(),
    "from_2022Q1": feat["print_quarter"].map(q_idx) >= q_idx("2022Q1"),   # drops pandemic-base quarters
    "ex_2026Q2": feat["print_quarter"] != "2026Q2",                        # drops the +16% outlier print
}
results = []
for smp, mask in SAMPLES.items():
    for tgt in TARGETS:
        for f in CONTEMP:
            d = corr_block(feat.loc[mask, f], feat.loc[mask, tgt])
            results.append(dict(block="univariate", sample=smp, target=tgt, feature=f, **d))

# multivariate, ex-ante spec
MV = ["nights_accel", "guide_implied_accel_pts", "margin_vs_bound_pts"]
for tgt in TARGETS:
    d = feat[MV + [tgt]].dropna()
    o = ols_loo(d[MV].to_numpy(float), d[tgt].to_numpy(float))
    results.append(dict(block="multivariate", sample="all", target=tgt, feature="+".join(MV), n=len(d),
                        r2_full=o["r2"], loo_r2=o["loo_r2"], loo_rmse=o["loo_rmse"], naive_rmse=o["naive_rmse"],
                        notes="; ".join(f"{m}: b={o['beta'][k + 1]:.2f} p={o['p'][k + 1]:.2f} sign_stab={o['sign_stab'][k]:.2f}"
                                        for k, m in enumerate(MV))))

# two-way sorts
def two_way(df, a, a_cut, b, b_cut, label):
    d = df.dropna(subset=[a, b])
    ha = d[a] > a_cut
    hb = d[b] > b_cut
    for na, ma in [("above", ha), ("below", ~ha)]:
        for nb, mb in [("accel", hb), ("decel", ~hb)]:
            cell = d[ma & mb]
            results.append(dict(block="twoway", target="excess_1d/5d/20d", feature=label,
                                cell=f"{a} {na} median x {b} {nb}", n=len(cell),
                                mean_1d=cell["excess_1d"].mean(), median_1d=cell["excess_1d"].median(),
                                mean_5d=cell["excess_5d"].mean(), mean_20d=cell["excess_20d"].mean(),
                                share_positive_1d=(cell["excess_1d"] > 0).mean() if len(cell) else np.nan,
                                quarters=" ".join(cell["print_quarter"])))


two_way(feat, "rev_beat_mid_pct", feat["rev_beat_mid_pct"].median(), "guide_implied_accel_pts", 0.0,
        "revenue beat x guide-implied accel (accel = guide y/y above reported y/y)")
two_way(feat, "rev_beat_mid_pct", feat["rev_beat_mid_pct"].median(), "guide_implied_accel_pts",
        feat["guide_implied_accel_pts"].median(), "revenue beat x guide-implied accel (split at median)")
# margin met/missed x nights accel/decel
d = feat.dropna(subset=["margin_guide_met", "nights_accel"])
for nm, mm in [("met", d["margin_guide_met"] == 1), ("missed", d["margin_guide_met"] == 0)]:
    for nb, mb in [("accel", d["nights_accel"] > 0), ("decel", d["nights_accel"] <= 0)]:
        cell = d[mm & mb]
        results.append(dict(block="twoway", target="excess_1d/5d/20d", feature="margin guide x nights accel",
                            cell=f"margin {nm} x nights {nb}", n=len(cell),
                            mean_1d=cell["excess_1d"].mean(), median_1d=cell["excess_1d"].median(),
                            mean_5d=cell["excess_5d"].mean(), mean_20d=cell["excess_20d"].mean(),
                            share_positive_1d=(cell["excess_1d"] > 0).mean() if len(cell) else np.nan,
                            quarters=" ".join(cell["print_quarter"])))
# also nights accel alone and guide accel alone (one-way, for the note), with a permutation
# p-value on the accel-minus-decel difference in mean 1-day excess return
def perm_diff_p(a, b, n_perm=N_PERM):
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = a.mean() - b.mean()
    pool = np.concatenate([a, b])
    cnt = 0
    for _ in range(n_perm):
        RNG.shuffle(pool)
        if abs(pool[:len(a)].mean() - pool[len(a):].mean()) >= abs(obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


for f in ["nights_accel", "guide_implied_accel_pts", "rev_accel", "gbv_accel", "margin_guide_met"]:
    d = feat.dropna(subset=[f])
    hi = d[f] > 0 if f != "margin_guide_met" else d[f] == 1
    pdiff = perm_diff_p(d.loc[hi, "excess_1d"], d.loc[~hi, "excess_1d"])
    mw = stats.mannwhitneyu(d.loc[hi, "excess_1d"], d.loc[~hi, "excess_1d"]).pvalue
    # direction concordance: feature up <-> 1-day excess up, two-sided binomial test against 50%
    hits = int((hi == (d["excess_1d"] > 0)).sum())
    conc = hits / len(d)
    binom_p = stats.binomtest(hits, len(d), 0.5).pvalue
    for nm, m in [("accel" if f != "margin_guide_met" else "met", hi),
                  ("decel" if f != "margin_guide_met" else "missed", ~hi)]:
        cell = d[m]
        results.append(dict(block="oneway", target="excess_1d/5d/20d", feature=f, cell=f"{f} {nm}", n=len(cell),
                            perm_p_diff_1d=pdiff, mannwhitney_p_1d=mw, direction_concordance=conc,
                            concordance_hits=hits, concordance_n=len(d), binomial_p=binom_p,
                            mean_1d=cell["excess_1d"].mean(), median_1d=cell["excess_1d"].median(),
                            mean_5d=cell["excess_5d"].mean(), mean_20d=cell["excess_20d"].mean(),
                            share_positive_1d=(cell["excess_1d"] > 0).mean() if len(cell) else np.nan,
                            quarters=" ".join(cell["print_quarter"])))

# pre-print signals vs next print's reaction and margin surprise
PRE_TARGETS = ["excess_1d", "excess_5d", "margin_vs_bound_pts", "margin_yoy_pts", "rev_beat_mid_pct"]
for smp, mask in SAMPLES.items():
    for tgt in PRE_TARGETS:
        for f in PRE:
            d = corr_block(feat.loc[mask, f], feat.loc[mask, tgt])
            results.append(dict(block="preprint", sample=smp, target=tgt, feature=f, **d))

res = pd.DataFrame(results)
res.to_csv(OUT_DIR / "04_reaction_results.csv", index=False, float_format="%.4f")

# ----------------------------------------------------------------------------
# 7. console summary
# ----------------------------------------------------------------------------
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
print("features written:", OUT_DIR / "04_print_features.csv", feat.shape)
print(feat[["print_quarter", "rev_beat_mid_pct", "nights_yoy", "nights_accel", "guide_implied_accel_pts",
            "guide_vs_cushion_trend_pts", "margin_bound_type", "margin_vs_bound_pts", "margin_guide_met",
            "fy_floor_action", "sm_delev_pts", "excess_1d", "excess_5d", "excess_20d"]].round(1).to_string())
u = res[res.block == "univariate"].copy()
u["abs_r"] = u["pearson_r"].abs()
for smp in SAMPLES:
    for tgt in TARGETS:
        print(f"\n--- univariate vs {tgt} [{smp}], ranked by |r| ---")
        print(u[(u.target == tgt) & (u["sample"] == smp)].sort_values("abs_r", ascending=False)[
            ["feature", "n", "pearson_r", "pearson_p", "spearman_rho", "spearman_p", "perm_p", "loo_r2"]].round(3).to_string(index=False))
print("\n--- multivariate ---")
print(res[res.block == "multivariate"][["target", "n", "r2_full", "loo_r2", "loo_rmse", "naive_rmse", "notes"]].round(3).to_string(index=False))
print("\n--- two-way sorts ---")
print(res[res.block.isin(["twoway", "oneway"])][["feature", "cell", "n", "mean_1d", "median_1d", "mean_5d", "mean_20d", "share_positive_1d", "perm_p_diff_1d", "mannwhitney_p_1d"]].round(3).to_string(index=False))
pp = res[res.block == "preprint"].copy()
pp["abs_r"] = pp["pearson_r"].abs()
for smp in SAMPLES:
    for tgt in PRE_TARGETS:
        print(f"\n--- pre-print vs {tgt} [{smp}] ---")
        print(pp[(pp.target == tgt) & (pp["sample"] == smp)].sort_values("abs_r", ascending=False)[
            ["feature", "n", "pearson_r", "pearson_p", "spearman_rho", "perm_p", "loo_rmse", "naive_rmse", "loo_r2"]].round(3).to_string(index=False))
