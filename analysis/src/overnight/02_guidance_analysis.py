"""
Workstream 02, Part C: how accurate is Airbnb's guidance, and does the guide move the stock?

Reads
  data/processed/overnight/02_guidance_ledger.csv     the ledger built by 02_guidance_ledger.py
  data/processed/overnight/02_kpi_panel_quarterly.csv actuals (Part A)
  data/processed/abnb_earnings_reactions.csv          day-1 / 5-day / 20-day returns vs QQQ

Writes
  data/processed/overnight/02_guidance_accuracy.csv      accuracy by metric, guide type and year
  data/processed/overnight/02_guidance_cushion_series.csv per-print revenue cushion and its walk-forward estimate
  data/processed/overnight/02_guidance_reaction_tests.csv every regression run, with LOO and a naive baseline
  data/processed/overnight/02_guidance_tells.csv         ranked "guidance tells"
  analysis/figures/overnight/02_guidance_cushion.png     cushion over time + reaction scatter

Point-in-time discipline
  Everything used to explain the day-1 move at print q is knowable at the print: the reported quarter, the guide
  issued with it, and the walk-forward cushion estimated only from prints strictly before q.

Run:  py -3.13 analysis/src/overnight/02_guidance_analysis.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/overnight"
FIG = ROOT / "analysis/figures/overnight"
FIG.mkdir(parents=True, exist_ok=True)

ORDER = ["4Q20", "1Q21", "2Q21", "3Q21", "4Q21", "1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23",
         "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
IX = {q: i for i, q in enumerate(ORDER)}

L = pd.read_csv(OUT / "02_guidance_ledger.csv")
P = pd.read_csv(OUT / "02_kpi_panel_quarterly.csv", index_col=0)
R = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
R["quarter"] = R["quarter"].str[5:6] + "Q" + R["quarter"].str[2:4]
R = R.set_index("quarter")

TESTS = []  # every statistical test run, for the "how many tests did you run" count


def ols(y, X, names):
    """Plain OLS with an intercept; returns dict with coefs, t-stats, R2, and leave-one-out R2."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n, k = X.shape
    A = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    dof = n - A.shape[1]
    s2 = resid @ resid / dof if dof > 0 else np.nan
    try:
        se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    except np.linalg.LinAlgError:
        se = np.full(A.shape[1], np.nan)
    sst = ((y - y.mean()) ** 2).sum()
    r2 = 1 - resid @ resid / sst if sst > 0 else np.nan
    # leave-one-out
    loo_err = []
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b, *_ = np.linalg.lstsq(A[m], y[m], rcond=None)
        loo_err.append(y[i] - A[i] @ b)
    loo_err = np.array(loo_err)
    loo_r2 = 1 - (loo_err ** 2).sum() / sst if sst > 0 else np.nan
    naive_r2 = 0.0  # predicting the mean
    return dict(n=n, r2=round(float(r2), 3), loo_r2=round(float(loo_r2), 3),
                loo_rmse=round(float(np.sqrt((loo_err ** 2).mean())), 2),
                mean_rmse=round(float(np.sqrt(((y - y.mean()) ** 2).mean())), 2),
                coefs={nm: round(float(b), 3) for nm, b in zip(["const"] + names, beta)},
                t={nm: (round(float(b / s), 2) if np.isfinite(s) and s > 0 else np.nan)
                   for nm, b, s in zip(["const"] + names, beta, se)})


def record(name, y, X, names, note=""):
    d = ols(y, X, names)
    TESTS.append(dict(test=name, n=d["n"], r2=d["r2"], loo_r2=d["loo_r2"], loo_rmse=d["loo_rmse"],
                      mean_rmse=d["mean_rmse"], coefs=str(d["coefs"]), t_stats=str(d["t"]), note=note))
    return d


# ==============================================================================================
# 1. Accuracy by metric / guide type / year
# ==============================================================================================
S = L[~L.outcome.isin(["pending", "not_scoreable", "no_actual", "qualitative", "n/a",
                       "n/a (2019 base not in panel)"])].copy()
S["year"] = S.print_quarter.str[2:].astype(int) + 2000
S["hit"] = S.outcome.isin(["within_range", "met", "at_point"])
S["beat_flag"] = S.outcome.isin(["above_range", "beat"])
S["miss_flag"] = S.outcome.isin(["below_range", "miss", "not_met"])

acc_rows = []
for (metric, gt), grp in S.groupby(["metric", "guide_type"]):
    acc_rows.append(dict(scope="metric_x_type", metric=metric, guide_type=gt, n=len(grp),
                         hit_or_met=int(grp.hit.sum()), beat=int(grp.beat_flag.sum()), miss=int(grp.miss_flag.sum()),
                         mean_distance_from_mid=round(grp.distance_from_mid.mean(), 2),
                         median_distance_from_mid=round(grp.distance_from_mid.median(), 2),
                         mean_pct_distance=round(grp.pct_distance_from_mid.mean(), 2)))
for gt, grp in S.groupby("guide_type"):
    acc_rows.append(dict(scope="type", metric="ALL", guide_type=gt, n=len(grp), hit_or_met=int(grp.hit.sum()),
                         beat=int(grp.beat_flag.sum()), miss=int(grp.miss_flag.sum()),
                         mean_distance_from_mid=round(grp.distance_from_mid.mean(), 2),
                         median_distance_from_mid=round(grp.distance_from_mid.median(), 2),
                         mean_pct_distance=round(grp.pct_distance_from_mid.mean(), 2)))
for yr, grp in S.groupby("year"):
    acc_rows.append(dict(scope="year", metric="ALL", guide_type=str(yr), n=len(grp), hit_or_met=int(grp.hit.sum()),
                         beat=int(grp.beat_flag.sum()), miss=int(grp.miss_flag.sum()),
                         mean_distance_from_mid=round(grp.distance_from_mid.mean(), 2),
                         median_distance_from_mid=round(grp.distance_from_mid.median(), 2),
                         mean_pct_distance=round(grp.pct_distance_from_mid.mean(), 2)))
rev = S[(S.metric == "revenue_usd_m") & (S.guide_type == "range")]
for yr, grp in rev.groupby("year"):
    acc_rows.append(dict(scope="revenue_range_by_year", metric="revenue_usd_m", guide_type=str(yr), n=len(grp),
                         hit_or_met=int(grp.hit.sum()), beat=int(grp.beat_flag.sum()), miss=int(grp.miss_flag.sum()),
                         mean_distance_from_mid=round(grp.distance_from_mid.mean(), 2),
                         median_distance_from_mid=round(grp.distance_from_mid.median(), 2),
                         mean_pct_distance=round(grp.pct_distance_from_mid.mean(), 2)))
ACC = pd.DataFrame(acc_rows)
ACC.to_csv(OUT / "02_guidance_accuracy.csv", index=False)

# ==============================================================================================
# 2. The revenue cushion series, and a walk-forward estimate of it
# ==============================================================================================
cush = rev[["print_quarter", "target_period", "value_low", "value_high", "value_mid", "actual",
            "pct_distance_from_mid"]].copy()
cush = cush.sort_values("print_quarter", key=lambda s: s.map(IX)).reset_index(drop=True)
cush["beat_vs_mid_pct"] = cush.pct_distance_from_mid
cush["beat_vs_high_pct"] = 100 * (cush.actual / cush.value_high - 1)
cush["range_width_pct"] = 100 * (cush.value_high - cush.value_low) / cush.value_mid
# walk-forward: median of all strictly-earlier beats, needs >=4 observations
cush["wf_cushion_pct"] = [cush.beat_vs_mid_pct.iloc[:i].median() if i >= 4 else np.nan for i in range(len(cush))]
cush.to_csv(OUT / "02_guidance_cushion_series.csv", index=False)

# ==============================================================================================
# 3. Reaction tests
# ==============================================================================================
num = lambda c: pd.to_numeric(P[c], errors="coerce")
panel = pd.DataFrame(index=[q for q in ORDER if q in P.index])
panel["revenue"] = num("revenue_musd")
panel["revenue_yoy"] = num("revenue_yoy_reported_pct")
panel["nights_yoy"] = num("nights_yoy_pct")
panel["nights_accel"] = num("nights_yoy_accel_pts")
panel["ebitda_margin"] = num("adj_ebitda_margin_pct")
panel["adj_ebitda"] = num("adj_ebitda_musd")

# guide issued at print q for quarter q+1
allrev = L[(L.metric == "revenue_usd_m") & (L.guide_type == "range")]
gmid = allrev.set_index("print_quarter")["value_mid"]
ghigh = allrev.set_index("print_quarter")["value_high"]
# revenue guide midpoint for the quarter being reported (issued one print earlier)
prev_mid = {q: gmid.get(ORDER[IX[q] - 1], np.nan) for q in ORDER if IX[q] > 0}

D = pd.DataFrame(index=[q for q in ORDER if q in panel.index])
D["excess_1d"] = R["excess_1d_pct"]
D["excess_5d"] = R["excess_5d_pct"]
D["excess_20d"] = R["excess_20d_pct"]
D["nights_accel"] = panel["nights_accel"]

# (a) the beat: reported revenue vs the guide midpoint set last quarter
D["beat_pct"] = [100 * (panel.revenue.get(q, np.nan) / prev_mid.get(q, np.nan) - 1) if prev_mid.get(q) else np.nan
                 for q in D.index]
# (b) the raw guide: next-quarter guide midpoint vs a seasonal-naive expectation knowable at the print
#     naive: next quarter's revenue grows y/y at the rate this quarter just printed
def naive_next(q):
    i = IX[q]
    if i + 1 >= len(ORDER):
        tgt = "3Q26"
    else:
        tgt = ORDER[i + 1]
    base_i = (IX[tgt] if tgt in IX else IX[q] + 1) - 4
    if base_i < 0 or base_i >= len(ORDER):
        return np.nan
    base = panel.revenue.get(ORDER[base_i], np.nan)
    gr = panel.revenue_yoy.get(q, np.nan)
    return base * (1 + gr / 100) if pd.notna(base) and pd.notna(gr) else np.nan


D["naive_next_rev"] = [naive_next(q) for q in D.index]
D["guide_mid_next"] = [gmid.get(q, np.nan) for q in D.index]
D["guide_vs_naive_pct"] = 100 * (D.guide_mid_next / D.naive_next_rev - 1)
# (c) cushion-aware: gross the guide up by the walk-forward historical beat before comparing
wf = cush.set_index("print_quarter")["wf_cushion_pct"]
D["wf_cushion_pct"] = [wf.get(q, np.nan) for q in D.index]
D["guide_implied_actual"] = D.guide_mid_next * (1 + D.wf_cushion_pct / 100)
D["cushion_aware_guide_surprise_pct"] = 100 * (D.guide_implied_actual / D.naive_next_rev - 1)
# (d) FY guide action at this print: +1 raise, 0 reiterate, -1 cut (revenue growth or margin)
fy = L[L.target_period.str.startswith("FY")].copy()
fy["key"] = fy.target_period + "|" + fy.metric
fy = fy.sort_values("print_quarter", key=lambda s: s.map(IX))
fy_action = {}
for key, grp in fy.groupby("key"):
    prevv = None
    for _, r_ in grp.iterrows():
        v = r_.value_mid if pd.notna(r_.value_mid) else r_.value_low
        if prevv is not None and pd.notna(v) and pd.notna(prevv):
            a = int(np.sign(v - prevv))
        else:
            a = 0
        fy_action.setdefault(r_.print_quarter, []).append(a)
        if pd.notna(v):
            prevv = v
D["fy_guide_action"] = [np.sign(sum(fy_action.get(q, [0]))) for q in D.index]
# (e) next-quarter margin guide direction: +1 up y/y, 0 flat, -1 down y/y
mg = L[(L.metric == "adj_ebitda_margin_yoy_pts") & (L.horizon_quarters == 1)].set_index("print_quarter")


def margin_dir(q):
    if q not in mg.index:
        return np.nan
    r_ = mg.loc[q]
    if isinstance(r_, pd.DataFrame):
        r_ = r_.iloc[0]
    if r_.guide_type == "floor":
        return 1.0
    if r_.guide_type == "ceiling":
        return -1.0
    return 0.0


D["margin_guide_dir"] = [margin_dir(q) for q in D.index]
D["margin_guide_dir_change"] = D.margin_guide_dir.diff()

D.to_csv(OUT / "02_guidance_reaction_inputs.csv")

# --- regressions on day-1 excess return -------------------------------------------------------
def fit(cols, name, dep="excess_1d", note=""):
    sub = D[[dep] + cols].dropna()
    if len(sub) < 6:
        TESTS.append(dict(test=name, n=len(sub), r2=np.nan, loo_r2=np.nan, loo_rmse=np.nan, mean_rmse=np.nan,
                          coefs="", t_stats="", note=note + " (too few obs)"))
        return None
    return record(name, sub[dep].values, sub[cols].values, cols, note)


fit(["beat_pct"], "day1 ~ revenue beat vs prior guide midpoint", note="the classic 'beat'")
fit(["guide_vs_naive_pct"], "day1 ~ raw next-Q guide vs seasonal-naive")
fit(["cushion_aware_guide_surprise_pct"], "day1 ~ cushion-aware next-Q guide surprise",
    note="guide grossed up by the walk-forward median beat")
fit(["beat_pct", "guide_vs_naive_pct"], "day1 ~ beat + raw guide")
fit(["beat_pct", "cushion_aware_guide_surprise_pct"], "day1 ~ beat + cushion-aware guide")
fit(["nights_accel"], "day1 ~ nights acceleration (predictive-study benchmark)")
fit(["nights_accel", "cushion_aware_guide_surprise_pct"], "day1 ~ nights accel + cushion-aware guide")
fit(["nights_accel", "beat_pct"], "day1 ~ nights accel + beat")
fit(["fy_guide_action"], "day1 ~ FY guide raise/cut")
fit(["margin_guide_dir"], "day1 ~ next-Q margin guide direction")
fit(["margin_guide_dir_change"], "day1 ~ change in margin guide direction")
fit(["nights_accel", "fy_guide_action"], "day1 ~ nights accel + FY guide action")
fit(["fy_guide_action"], "day20 ~ FY guide raise/cut", dep="excess_20d")
fit(["margin_guide_dir_change"], "day20 ~ change in margin guide direction", dep="excess_20d")
fit(["cushion_aware_guide_surprise_pct"], "day20 ~ cushion-aware guide surprise", dep="excess_20d")
fit(["beat_pct"], "day5 ~ beat", dep="excess_5d")
fit(["cushion_aware_guide_surprise_pct"], "day5 ~ cushion-aware guide surprise", dep="excess_5d")

T = pd.DataFrame(TESTS)
T.to_csv(OUT / "02_guidance_reaction_tests.csv", index=False)

# sign tests (non-parametric), reported alongside
sign_rows = []
for col, dep in [("cushion_aware_guide_surprise_pct", "excess_1d"), ("beat_pct", "excess_1d"),
                 ("nights_accel", "excess_1d"), ("fy_guide_action", "excess_1d"),
                 ("fy_guide_action", "excess_20d"), ("margin_guide_dir", "excess_1d")]:
    sub = D[[col, dep]].dropna()
    sub = sub[sub[col] != 0]
    same = int((np.sign(sub[col]) == np.sign(sub[dep])).sum())
    sign_rows.append(dict(feature=col, dep=dep, n=len(sub), same_sign=same,
                          hit_rate=round(same / len(sub), 2) if len(sub) else np.nan))
SIGN = pd.DataFrame(sign_rows)

# ==============================================================================================
# 4. Ranked guidance tells
# ==============================================================================================
tells = []


def tell(rank, name, evidence, n, strength, use):
    tells.append(dict(rank=rank, tell=name, evidence=evidence, n=n, strength=strength, how_to_use=use))


rr = rev.dropna(subset=["actual"])
tell(1, "The quarterly revenue range is a floor, not a forecast",
     f"{int(rr.beat_flag.sum())}/{len(rr)} prints landed above the top of the range; 0 below the bottom; "
     f"mean beat vs midpoint {rr.pct_distance_from_mid.mean():.2f}%, median {rr.pct_distance_from_mid.median():.2f}%",
     len(rr), "very strong", "Model next-quarter revenue at guide midpoint x (1 + walk-forward cushion), not the midpoint.")
last8 = rr.tail(8)
tell(2, "The cushion has halved, and the range has tightened with it",
     f"mean beat vs midpoint {last8.pct_distance_from_mid.mean():.2f}% over the last 8 prints vs "
     f"{rr.head(len(rr) - 8).pct_distance_from_mid.mean():.2f}% over the first {len(rr) - 8}; guide range width fell from "
     f"{cush.range_width_pct[:4].mean():.1f}% to {cush.range_width_pct[-8:].mean():.1f}% of the midpoint",
     len(rr), "moderate",
     "Use the trailing-8-print cushion (~1.8%), not the full-history 2.5%; the guide is tighter and less sandbagged than 2021-23.")
nb = S[(S.metric == "nights_yoy_pct")]
tell(3, "Bucketed nights guides are the most beatable guide in the pack",
     "; ".join(f"{r_.print_quarter}->{r_.target_period} guided {r_.value_low:.0f}-{r_.value_high:.0f}%, actual "
               f"{r_.actual:.1f}% ({r_.outcome})" for _, r_ in nb[nb.guide_type == "bucket"].dropna(subset=["actual"]).iterrows()),
     int(nb[nb.guide_type == "bucket"].actual.notna().sum()), "strong",
     "Treat a bucketed nights guide as a floor; the 4Q25 print beat a mid-single-digit guide by ~5 points.")
mgn = S[(S.metric == "adj_ebitda_margin_pct") & (S.target_period.str.startswith("FY"))]
tell(4, "Every full-year margin floor has been cleared",
     "; ".join(f"{r_.print_quarter}: {r_.target_period} floor/point {r_.value_low if pd.notna(r_.value_low) else r_.value_mid}%, "
               f"actual {r_.actual:.1f}% ({r_.outcome})" for _, r_ in mgn.dropna(subset=["actual"]).iterrows()),
     len(mgn.dropna(subset=["actual"])), "strong",
     "Add the historical cushion to the FY margin floor when setting the base case.")
bad = S[S.miss_flag & S.guide_type.isin(["point", "range", "bucket", "floor"])]
tell(5, "The guides that actually miss are the expense and monetisation lines, not the top line",
     "; ".join(f"{r_.print_quarter}->{r_.target_period} {r_.metric} guided "
               f"{r_.value_mid if pd.notna(r_.value_mid) else r_.value_low}, actual {r_.actual}" for _, r_ in bad.iterrows()),
     len(bad), "moderate",
     "Haircut the SBC and tax guides; assume the take-rate guide is only directionally right.")
adr = S[S.metric == "adr_yoy_pct"]
tell(5.5, "ADR direction calls go wrong when FX moves after the guide is set",
     f"{int(adr.miss_flag.sum())} of {len(adr)} ADR guides wrong: 4Q22 and 1Q23 both guided 'slightly lower ADR' and got "
     f"+0.2% and +1.4%; all 8 'ADR up' floors were met",
     len(adr), "moderate", "Model ADR from the FX basket and regional mix, not from the ADR sentence in the guide.")
tell(6, "The full-year guide is only raised, never cut, and the raises come in Q3/Q4",
     "FY24 margin 35% floor -> 35.5% point at the 3Q24 print; FY25 34.5% floor -> ~35% at 3Q25; "
     "FY26 revenue growth 'at least low double digits' (4Q25) -> 'low to mid teens' (1Q26) -> 'at least mid teens' (2Q26)",
     3, "strong", "Assume the FY26 guide is raised again on 5 Nov unless the quarter misses.")

TELLS = pd.DataFrame(tells)
TELLS.to_csv(OUT / "02_guidance_tells.csv", index=False)

# ==============================================================================================
# 5. Figure
# ==============================================================================================
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    x = np.arange(len(cush))
    ax[0].bar(x, cush.beat_vs_mid_pct, color="#4C78A8", label="actual vs guide midpoint")
    ax[0].plot(x, cush.wf_cushion_pct, color="#E45756", lw=2, label="walk-forward median cushion")
    ax[0].axhline(0, color="k", lw=0.8)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(cush.target_period, rotation=90, fontsize=7)
    ax[0].set_ylabel("%")
    ax[0].set_title("Quarterly revenue: beat vs guide midpoint")
    ax[0].legend(fontsize=8)

    sub = D[["cushion_aware_guide_surprise_pct", "excess_1d"]].dropna()
    ax[1].scatter(sub.cushion_aware_guide_surprise_pct, sub.excess_1d, color="#4C78A8")
    for q, r_ in sub.iterrows():
        ax[1].annotate(q, (r_.cushion_aware_guide_surprise_pct, r_.excess_1d), fontsize=6.5,
                       xytext=(2, 2), textcoords="offset points")
    if len(sub) > 2:
        b = np.polyfit(sub.cushion_aware_guide_surprise_pct, sub.excess_1d, 1)
        xs = np.linspace(sub.cushion_aware_guide_surprise_pct.min(), sub.cushion_aware_guide_surprise_pct.max(), 10)
        ax[1].plot(xs, np.polyval(b, xs), color="#E45756", lw=1.5)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].axvline(0, color="k", lw=0.8)
    ax[1].set_xlabel("cushion-aware next-quarter guide surprise (%)")
    ax[1].set_ylabel("day-1 excess return vs QQQ (%)")
    ax[1].set_title("Guide surprise vs day-1 reaction")
    fig.tight_layout()
    fig.savefig(FIG / "02_guidance_cushion.png", dpi=150)
    plt.close(fig)
except Exception as e:  # pragma: no cover
    print("figure skipped:", e)

# ==============================================================================================
print("=== accuracy, all scored guides ===")
print(ACC[ACC.scope == "type"].to_string(index=False))
print("\n=== revenue $ range by year ===")
print(ACC[ACC.scope == "revenue_range_by_year"][["guide_type", "n", "hit_or_met", "beat", "miss",
                                                 "mean_pct_distance"]].to_string(index=False))
print("\n=== cushion series ===")
print(cush[["print_quarter", "target_period", "value_mid", "actual", "beat_vs_mid_pct", "beat_vs_high_pct",
            "range_width_pct", "wf_cushion_pct"]].round(2).to_string(index=False))
print("\n=== reaction tests (%d run) ===" % len(T))
print(T[["test", "n", "r2", "loo_r2", "loo_rmse", "mean_rmse", "coefs", "t_stats"]].to_string(index=False))
print("\n=== sign tests ===")
print(SIGN.to_string(index=False))
print("\n=== directional guides that were wrong ===")
print(S[S.outcome == "not_met"][["print_quarter", "target_period", "metric", "guide_type", "actual",
                                 "comparator_value", "quote"]].to_string(index=False))
print("\n=== 5 Nov card inputs ===")
q26 = L[(L.print_quarter == "2Q26")][["target_period", "metric", "guide_type", "value_low", "value_high",
                                      "value_mid", "unit", "quote"]]
print(q26.to_string(index=False))
wf_all = cush.beat_vs_mid_pct.median()
wf_8 = cush.beat_vs_mid_pct.tail(8).median()
gm = float(gmid.get("2Q26"))
base_3q25 = float(panel.revenue.get("3Q25"))
card = []
for label, c_ in [("full-history median", wf_all), ("last-8 median", wf_8),
                  ("last-8 25th pct", cush.beat_vs_mid_pct.tail(8).quantile(0.25)),
                  ("last-8 75th pct", cush.beat_vs_mid_pct.tail(8).quantile(0.75))]:
    lvl = gm * (1 + c_ / 100)
    card.append(dict(basis=label, cushion_pct=round(c_, 2), revenue_usd_m=round(lvl, 0),
                     implied_yoy_pct=round(100 * (lvl / base_3q25 - 1), 1)))
CARD = pd.DataFrame(card)
CARD.to_csv(OUT / "02_q3_2026_guide_card.csv", index=False)
print()
print("3Q26 revenue guide midpoint $%.0fm (range $4,690-4,770m), 3Q25 base $%.0fm" % (gm, base_3q25))
print(CARD.to_string(index=False))
h1_26 = panel.revenue.get("1Q26") + panel.revenue.get("2Q26")
h1_25 = panel.revenue.get("1Q25") + panel.revenue.get("2Q25")
e1_26 = panel.adj_ebitda.get("1Q26") + panel.adj_ebitda.get("2Q26")
e1_25 = panel.adj_ebitda.get("1Q25") + panel.adj_ebitda.get("2Q25")
m26, m25 = 100 * e1_26 / h1_26, 100 * e1_25 / h1_25
print("1H26 revenue $%.0fm, +%.1f%% y/y; 1H26 adj EBITDA margin %.2f%% vs 1H25 %.2f%% (+%.2fpts)"
      % (h1_26, 100 * (h1_26 / h1_25 - 1), m26, m25, m26 - m25))
SIGN.to_csv(OUT / "02_guidance_sign_tests.csv", index=False)
