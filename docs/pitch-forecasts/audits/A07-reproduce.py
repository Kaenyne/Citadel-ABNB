"""A07 audit reproduction. Dependencies: Python stdlib + pandas only."""
from pathlib import Path
from statistics import NormalDist
import json
import math
import sys

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
S02 = Q / "close-15dec-2026"
S04 = Q / "sellside-mean-target-cut-by-15dec"
PROC = ROOT / "data/processed"
N = NormalDist()


def read(path, **kwargs):
    return pd.read_csv(path, **kwargs)


def report(label, values):
    x = pd.Series(list(values), dtype=float).dropna()
    print(label, {
        "n": len(x),
        "mean": x.mean(),
        "sd_sample": x.std(),
        "median": x.median(),
        "positive": int((x > 0).sum()),
    })


def ols(frame, dependent, predictors):
    """OLS by pivoted elimination, avoiding numpy/statsmodels imports."""
    rows = [
        [1.0] + [float(r[x]) for x in predictors]
        for _, r in frame.iterrows()
    ]
    ys = frame[dependent].astype(float).tolist()
    k = len(predictors) + 1
    a = [
        [sum(r[i] * r[j] for r in rows) for j in range(k)]
        + [sum(r[i] * y for r, y in zip(rows, ys))]
        for i in range(k)
    ]
    for i in range(k):
        pivot = max(range(i, k), key=lambda j: abs(a[j][i]))
        a[i], a[pivot] = a[pivot], a[i]
        divisor = a[i][i]
        if abs(divisor) < 1e-12:
            raise ValueError("Singular regression")
        a[i] = [v / divisor for v in a[i]]
        for j in range(k):
            if j != i:
                factor = a[j][i]
                a[j] = [v - factor * u for v, u in zip(a[j], a[i])]
    beta = [a[i][-1] for i in range(k)]
    residual = [
        y - sum(b * z for b, z in zip(beta, row))
        for row, y in zip(rows, ys)
    ]
    sse = sum(e * e for e in residual)
    mean = sum(ys) / len(ys)
    r2 = 1 - sse / sum((y - mean) ** 2 for y in ys)
    return beta, math.sqrt(sse / (len(ys) - k)), r2


# 1. Price-window base rates, tails, and realized volatility.
prices = read(
    S02 / "datasets/abnb_close_merged_to_20260916.csv",
    parse_dates=["Date"],
).set_index("Date").Close.sort_index()
assert not prices.index.duplicated().any()
rx = read(PROC / "abnb_earnings_reactions.csv",
          parse_dates=["reaction_date"])

for horizon in (63, 103):
    returns = 100 * (prices.shift(-horizon) / prices - 1)
    for label, x in (
        ("all", returns.dropna()),
        ("starts_2023plus", returns.loc["2023":].dropna()),
        ("starts_2024plus", returns.loc["2024":].dropna()),
    ):
        report(f"price_return_{horizon}_{label}", x)
        print("quantiles", x.quantile(
            [.01, .05, .10, .25, .50, .75, .90, .95]
        ).to_dict())
        print("thresholds", {
            "le150": (x <= 100 * (150 / 167.51 - 1)).mean(),
            "le143": (x <= 100 * (143 / 167.51 - 1)).mean(),
            "ge180": (x >= 100 * (180 / 167.51 - 1)).mean(),
            "minimum": x.min(),
            "minimum_start": str(x.idxmin().date()),
            "overlapping_windows_le_minus40": int((x <= -40).sum()),
        })

logret = (prices / prices.shift(1)).apply(math.log)
for label, x in (
    ("2023plus", logret.loc["2023":]),
    ("2024plus", logret.loc["2024":]),
):
    no_event = x[~x.index.isin(rx.reaction_date)]
    print("annualized_vol", label, {
        "all_pct": x.std() * math.sqrt(252) * 100,
        "excluding_prints_pct": no_event.std() * math.sqrt(252) * 100,
    })

# 2. Earnings reactions, February history, guide gates, W1/W2.
for column in ("abnb_1d_pct", "excess_1d_pct"):
    x = rx[column]
    report(column, x)
    print("rms_and_absolute", {
        "rms": math.sqrt(x.pow(2).mean()),
        "mean_abs": x.abs().mean(),
        "abs_ge7": int((x.abs() >= 7).sum()),
        "abs_ge10": int((x.abs() >= 10).sum()),
    })

feb = rx[rx.quarter.str.endswith("Q4")]
print("February_rows",
      feb[["quarter", "abnb_1d_pct", "excess_1d_pct"]].to_dict("records"))
report("February_raw", feb.abnb_1d_pct)

guide = read(PROC / "abnb_guidance_reaction_panel.csv")
gated = guide[
    (guide.guide_vs_street_pct < 0) & (guide.nq_nights_dir == -1)
]
print("guide_below_and_nights_lower",
      gated[["print_quarter", "ret_1d", "exc_1d"]].to_dict("records"))
report("guide_below_lower_raw", gated.ret_1d)

cp = read(PROC / "reverse_dcf/C/C_print_panel.csv")
for start in ("2022Q3", "2023Q1", "2024Q1"):
    for sign in (-1, 0, 1):
        g = cp[
            (cp.print_quarter >= start) & (cp.nights_accel_sign == sign)
        ]
        report(f"sign_{start}_{sign}_excess", g.ret_1d_cc_excess_pct)
        report(f"sign_{start}_{sign}_raw", g.ret_1d_cc_raw_pct)
        report(
            f"sign_{start}_{sign}_paired_cumulative_difference",
            g.ret_20d_cc_excess_pct - g.ret_1d_cc_excess_pct,
        )

old = rx.merge(
    cp[["print_quarter", "nights_yoy_accel_pts"]],
    left_on="quarter", right_on="print_quarter",
)
old = old[
    (old.quarter >= "2023Q1") & (old.nights_yoy_accel_pts >= 0)
].dropna(subset=["excess_20d_pct"])
report("old_accelerating_paired_difference",
       old.excess_20d_pct - old.excess_1d_pct)

ledger = read(PROC / "overnight/02_guidance_ledger.csv")
nights = ledger[ledger.metric.str.contains("nights", na=False)]
print("nights_guide_outcomes",
      nights[["print_quarter", "target_period", "direction",
              "value_mid", "actual", "outcome"]].to_dict("records"))

# 3. Reconstruct legacy drift and correctly rebased excess returns.
px = read(PROC / "overnight/09_prices_daily.csv",
          parse_dates=["Date"]).set_index("Date")
px = px.dropna(subset=["ABNB"])
drift_rows = []
for _, event in rx.iterrows():
    i = px.index.get_loc(event.reaction_date)
    anchor, before, day = px.iloc[i - 21], px.iloc[i - 1], px.iloc[i]
    row = {
        "q": event.quarter,
        "date": event.reaction_date,
        "legacy_day1": 100 * (
            (day.ABNB - before.ABNB) / anchor.ABNB
            - (day.QQQ - before.QQQ) / anchor.QQQ
        ),
    }
    for h in (20, 27, 60):
        if i + h >= len(px):
            continue
        end = px.iloc[i + h]
        row[f"legacy{h}"] = 100 * (
            (end.ABNB - day.ABNB) / anchor.ABNB
            - (end.QQQ - day.QQQ) / anchor.QQQ
        )
        row[f"proper{h}"] = 100 * (
            end.ABNB / day.ABNB - end.QQQ / day.QQQ
        )
    drift_rows.append(row)
drift = pd.DataFrame(drift_rows)
for label, g in (
    ("all", drift),
    ("reaction_dates_2023plus", drift[drift.date >= "2023-01-01"]),
    ("W1", drift[drift.q >= "2023Q1"]),
    ("W2", drift[drift.q >= "2024Q1"]),
    ("day1_up", drift[drift.legacy_day1 >= 0]),
    ("day1_down", drift[drift.legacy_day1 < 0]),
):
    for column in ("legacy20", "proper20", "proper27",
                   "legacy60", "proper60"):
        report(f"drift_{label}_{column}", g[column])

monthly = px[["ABNB", "QQQ"]].resample("ME").last().pct_change() * 100
monthly = monthly.loc["2021":]
monthly["excess"] = monthly.ABNB - monthly.QQQ
for month in (1, 2, 9, 10, 11, 12):
    report(f"calendar_month_{month}",
           monthly.loc[monthly.index.month == month, "excess"])

# 4. Target tape and exact threshold.
ud = read(
    S04 / "sources/yfinance_upgrades_downgrades_20260917T031221Z.csv",
    parse_dates=["GradeDate"],
)
live = ud[
    (ud.GradeDate >= "2025-09-16")
    & (ud.GradeDate < "2026-09-17")
    & (ud.currentPriceTarget > 0)
].sort_values("GradeDate").groupby("Firm").tail(1)
base = live.currentPriceTarget.mean()
ms_base = live.currentPriceTarget.where(
    live.Firm != "Morgan Stanley", 170.0
).mean()
print("live_tape", {
    "n": len(live), "mean": base,
    "median": live.currentPriceTarget.median(),
    "MS_adjusted_mean": ms_base,
    "oldest": str(live.GradeDate.min()),
})
exact_log_threshold = math.log(176.8 / ms_base)

panel = read(PROC / "reverse_dcf/D/D_target_panel_daily.csv",
             parse_dates=["date"])
panel = panel[panel.n_targets >= 10].set_index("date").sort_index()
forward = (panel.mean_target.shift(-63) / panel.mean_target).apply(
    math.log
).dropna()
for threshold in (-.035, exact_log_threshold, math.log(176.8 / base)):
    for label, x in (
        ("all", forward),
        ("2023plus", forward.loc["2023":]),
        ("2024plus", forward.loc["2024":]),
    ):
        print("target_daily_rate", label, {
            "threshold_log": threshold, "n": len(x),
            "hits": int((x <= threshold).sum()),
            "p": (x <= threshold).mean(),
        })

# Rebuild the original -36/+27 print windows.
rows = []
for _, event in rx.iterrows():
    if event.reaction_date not in panel.index:
        continue
    i = panel.index.get_loc(event.reaction_date)
    if i < 36 or i + 27 >= len(panel):
        continue
    a, b = panel.iloc[i - 36], panel.iloc[i + 27]
    rows.append({
        "q": event.quarter,
        "target": 100 * (b.mean_target / a.mean_target - 1),
        "price": 100 * (b.close / a.close - 1),
        "day1": event.abnb_1d_pct,
    })
windows = pd.DataFrame(rows)
for label, g in (
    ("all", windows),
    ("W1", windows[windows.q >= "2023Q1"]),
    ("W2", windows[windows.q >= "2024Q1"]),
):
    print("target_print_windows", label, {
        "n": len(g), "hits_simple_le_minus3_5": int((g.target <= -3.5).sum()),
        "ols_beta_residual_sd_r2": ols(g, "target", ["price", "day1"]),
    })

lp = panel.close.apply(math.log)
lt = panel.mean_target.apply(math.log)
reg = pd.DataFrame({
    "y": lt.diff(21), "x0": lp.diff(21),
    "x1": lp.diff(21).shift(21), "x2": lp.diff(21).shift(42),
}).dropna()
for label, g in (
    ("all", reg), ("2023plus", reg.loc["2023":]),
    ("2024plus", reg.loc["2024":]),
):
    print("target_chase", label, len(g),
          ols(g, "y", ["x0", "x1", "x2"]))

revisions = read(PROC / "reverse_dcf/D/D_print_revisions.csv")
for label, g in revisions.groupby("print_class"):
    print("print_target_changes", label, {
        "n": len(g), "mean20": g.d_mean_target_plus20_pct.mean(),
        "mean40": g.d_mean_target_plus40_pct.mean(),
        "any_cut": int((g.d_mean_target_plus20_pct < 0).sum()),
        "cut_ge3_8": int((g.d_mean_target_plus20_pct <= -3.8).sum()),
    })
    print(g[["quarter", "price_move_day1_pct",
             "d_mean_target_plus20_pct"]].to_dict("records"))

# 5. Reviews-index correction and calendar arithmetic.
print("reviews_revintaging",
      read(PROC / "q3nowcast_v2/E/t1_fail_e5_rerun.csv").to_dict("records"))
holidays = pd.to_datetime([
    "2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18",
])
for a, b in (
    ("2026-09-16", "2026-11-05"),
    ("2026-11-06", "2026-12-15"),
    ("2026-12-15", "2027-02-11"),
    ("2026-09-16", "2026-12-15"),
    ("2026-09-16", "2027-02-12"),
):
    print("sessions", a, b,
          len(pd.bdate_range(a, b, inclusive="right").difference(holidays)))

# 6. Actual saved blend anchor and event-variance correction.
imp = json.loads(
    (S02 / "datasets/implied_dist_20260917T031221Z.json").read_text()
)
for question, key in (("S02", "dec15"), ("S03", "feb12")):
    d = imp[key]
    median = d["smile_rnd"]["50"] * math.exp(.03 * d["T_years"])
    sd = d["sigma_pct"] / 100 * math.sqrt(d["T_years"])
    probabilities = {
        str(k): N.cdf(math.log(k / median) / sd)
        for k in (100, 143, 150, 180, 260)
    }
    print("actual_lognormal_anchor", question, median, probabilities)
    cdf = read(S02 / f"datasets/{question}_final_cdf.csv")
    assert cdf.cdf_final.diff().dropna().ge(0).all()
    assert cdf.cdf_final.between(0, 1).all()
    print("saved_final_CDF_at_thresholds", question,
          cdf[cdf.price.isin([100, 143, 150, 180, 260])].to_dict("records"))

w = 28 / 63
d = imp["feb12"]
variance = (d["sigma_pct"] / 100) ** 2 * d["T_years"]
print("February_event_corrected_log_sd",
      math.sqrt(variance + (1 - w) * .095 ** 2))

# Negative-density diagnostic from the saved fitted smile coefficients.
term = read(
    S02 / "datasets/implied_term_structure_20260917T031221Z.csv"
).set_index("expiry")


def gradient(y, dx):
    return (
        [(y[1] - y[0]) / dx]
        + [(y[i + 1] - y[i - 1]) / (2 * dx)
           for i in range(1, len(y) - 1)]
        + [(y[-1] - y[-2]) / dx]
    )


def area(y, dx):
    return dx * (sum(y) - .5 * (y[0] + y[-1]))


for target, first, second in (
    ("2026-12-15", "2026-12-18", None),
    ("2027-02-12", "2027-01-15", "2027-03-19"),
):
    T = (pd.Timestamp(target) - pd.Timestamp("2026-09-16")).days / 365
    z = term.loc[first]
    coeff = [z.atm_iv / 100, z.smile_b, z.smile_c]
    if second:
        z2 = term.loc[second]
        weight = (T - z["T"]) / (z2["T"] - z["T"])
        coeff = [
            (1 - weight) * a + weight * b
            for a, b in zip(coeff, [z2.atm_iv / 100,
                                    z2.smile_b, z2.smile_c])
        ]
    F = imp["spot"] * math.exp(.0397 * T)
    calls = []
    for i in range(2601):
        K = 60 + .1 * i
        x = max(-.45, min(.45, math.log(K / F)))
        vol = max(.05, min(2, coeff[0] + coeff[1] * x + coeff[2] * x*x))
        d1 = (math.log(F / K) + .5 * vol*vol*T) / (vol * math.sqrt(T))
        calls.append(F * N.cdf(d1) - K * N.cdf(d1 - vol * math.sqrt(T)))
    density = gradient(gradient(calls, .1), .1)
    print("negative_RND_mass", target,
          area([max(-v, 0) for v in density], .1))

# 7. Independent comparison distributions.
spot, bg, total_drift = 167.51, .30, .0697
nov_mean, nov_sd, feb_mean, feb_sd = -.027, .095, .026, .095
nov_var = math.log1p((nov_sd / (1 + nov_mean)) ** 2)
feb_var = math.log1p((feb_sd / (1 + feb_mean)) ** 2)

for question, sessions, include_feb in (
    ("S02", 62, False), ("S03", 101, True),
):
    mu = (
        math.log(spot) + (total_drift - bg*bg/2) * sessions / 252
        + math.log1p(nov_mean) - nov_var/2
    )
    variance = bg*bg * sessions / 252 + nov_var
    if include_feb:
        mu += math.log1p(feb_mean) - feb_var/2
        variance += feb_var
    sd = math.sqrt(variance)
    print("independent_price", question, {
        "percentiles": {
            q: math.exp(mu + sd * N.inv_cdf(q / 100))
            for q in (5, 10, 25, 50, 75, 90, 95)
        },
        "CDF": {
            k: N.cdf((math.log(k) - mu) / sd)
            for k in (100, 143, 150, 180, 260)
        },
    })

beta, residual_sd, _ = ols(windows, "target", ["price", "day1"])
expected_gross = math.exp(total_drift * 62 / 252) * (1 + nov_mean)
v = bg*bg * 62 / 252 + nov_var
return_mean = 100 * (expected_gross - 1)
return_variance = expected_gross**2 * math.expm1(v) * 10000
covariance = expected_gross / (1 + nov_mean) * nov_sd**2 * 10000
mu = beta[0] + beta[1] * return_mean + beta[2] * nov_mean * 100
sd = math.sqrt(
    residual_sd**2 + beta[1]**2 * return_variance
    + beta[2]**2 * (nov_sd * 100)**2
    + 2 * beta[1] * beta[2] * covariance
)
gate = 100 * (176.8 / ms_base - 1)
model_p = N.cdf((gate - mu) / sd)
recent = windows[windows.q >= "2023Q1"]
outside = (
    (forward.loc["2023":] <= exact_log_threshold).mean()
    + (recent.target <= gate).mean()
) / 2
print("independent_S04", {
    "target_change_mean_pct": mu, "target_change_sd_pct": sd,
    "required_simple_change_pct": gate, "model_p": model_p,
    "outside_p": outside, "final_p": (2 * model_p + outside) / 3,
})
