"""A09 audit reproduction. Run from repo root; stdlib + pandas; no writes/network."""
from pathlib import Path
from statistics import NormalDist, mean, pstdev
import json
import math
import random
import pandas as pd

ROOT = Path.cwd()
assert (ROOT / "docs/pitch-forecasts/QUESTIONS.md").exists(), "Run from repo root"
Q = ROOT / "docs/pitch-forecasts/questions"
A = Q / "risk-q3-nights-meets-guide"
C = Q / "rnpl-gbv-share-disclosed"
N = NormalDist()


def read(path):
    return pd.read_csv(ROOT / path)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def qi(q):
    return (2000 + int(q[-2:])) * 4 + int(q[0]) - 1


def tail(mu, sd, threshold):
    return N.cdf((mu - threshold) / sd)


def report_rate(name, values, thresholds):
    values = list(values)
    print(name, "n =", len(values),
          [(t, sum(x >= t for x in values),
            round(sum(x >= t for x in values) / len(values), 6))
           for t in thresholds])


# Guidance and sequential-change reference classes: originals, no typed history.
g = read("data/processed/overnight/02_guidance_ledger.csv")
g = g[g.metric.eq("nights_yoy_pct")].sort_values("print_date")
resolved = g[g.actual.notna()]
print("Guidance outcomes:", g.outcome.value_counts().to_dict())
print("Resolved guides meeting/exceeding coded guidance:",
      resolved.outcome.isin(["met", "above_range"]).sum(), "/", len(resolved))
levels = dict(zip(resolved.target_period, resolved.actual))
levels["2Q22"] = float(
    g.loc[g.print_quarter.eq("2Q22"), "comparator_value"].iloc[0]
)
keys = sorted(levels, key=qi)
changes = [(q, levels[q] - levels[keys[i-1]])
           for i, q in enumerate(keys) if i]
for label, rows in [
    ("All 3Q22-2Q26", changes),
    ("W1 target 1Q23+", [(q, x) for q, x in changes if qi(q) >= qi("1Q23")]),
    ("W2 target 1Q24+", [(q, x) for q, x in changes if qi(q) >= qi("1Q24")]),
    ("Q2-to-Q3", [(q, x) for q, x in changes if q.startswith("3Q")]),
]:
    report_rate(label, [x for _, x in rows], [-0.34, 0.26])
    print("  members:", rows)
print("Stable/approximate comparators:")
print(g[g.direction.isin(["stable", "approx"])][
    ["target_period", "comparator_value", "actual", "distance_from_mid", "quote"]
].to_string(index=False))

# Original nowcast rows and full-precision errors; W2 has 7 models, W1 only 6.
nc = read("data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv")
wf = read("data/processed/q3nowcast/E_aug/backtest_wf_paths.csv")
wf = wf[wf.target.eq("nights_yoy") & wf.lag.eq(0)]
rev = read("data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv")
v1 = rev.loc[rev.variant.str.startswith("v1"), "wf_ratio_vs_naive"].iloc[0]
factor = (
    rev.loc[rev.variant.str.startswith("b:"), "wf_ratio_vs_naive"].iloc[0] / v1
)
print("Revintage inputs:", rev[
    ["variant", "wf_n", "wf_rmse", "wf_ratio_vs_naive"]
].to_string(index=False))
thresholds = [10.0, 10.6, (147.8 / 133.6 - 1) * 100]
features = [f"{r.region}|{r.measure}|{r.weighting}" for r in nc.itertuples()]
kernel_w2 = None
for window in ["2023Q1+", "2022Q1+"]:
    probs = []
    print("ERROR WINDOW", window)
    for r, feature in zip(nc.itertuples(), features):
        e = wf[wf.feature.eq(feature) & wf.window.eq(window)].sort_values("qi")
        if e.empty:
            print("  MISSING:", feature)
            continue
        errors = e.err_feature.tolist()
        actual = [r.implied_nights_yoy - x for x in errors]
        plug = [sum(x >= t for x in actual) / len(actual) for t in thresholds]
        kernel = [
            mean(tail(r.implied_nights_yoy - factor*x, 0.5, t) for x in errors)
            for t in thresholds
        ]
        probs.append(kernel)
        print(feature, "n", len(e), "bias", mean(errors),
              "sample_sd", e.err_feature.std(),
              "rmse", math.sqrt(mean(x*x for x in errors)),
              "overpredictions", sum(x > 0 for x in errors),
              "plugin", plug, "scaled_kernel", kernel)
    mix = [mean(p[i] for p in probs) for i in range(len(thresholds))]
    print("Equal-model kernel mixture:", mix, "models", len(probs))
    if window == "2023Q1+":
        kernel_w2 = mix
        panel = wf[
            wf.feature.isin(features) & wf.window.eq(window)
        ].pivot(index="qi", columns="feature", values="err_feature")
        print("All models underpredicted:", [
            f"{int(q)//4}Q{int(q)%4+1}"
            for q in panel.index[(panel < 0).all(axis=1)]
        ])
        print("Minimum pairwise error correlation:", panel.corr().min().min())
print("Analytic alt-only blend at original thresholds:",
      [(kernel_w2[i] + tail(9.55, 1.7, thresholds[i])) / 2 for i in [0, 1]])

# Saved market fields: fixed-point strings are real volume/OI fields.
market = load(A / "sources/kalshi_markets_KXABNB_open_20260917T032158Z.json")
mids = {}
for m in market["markets"]:
    strike = m["floor_strike"] / 1e6
    mids[strike] = (
        float(m["yes_bid_dollars"]) + float(m["yes_ask_dollars"])
    ) / 2
    print("Kalshi", strike, "mid", mids[strike], "last", m["last_price_dollars"],
          "volume", m["volume_fp"], "OI", m["open_interest_fp"],
          "24h", m["volume_24h_fp"], "updated", m["updated_time"])


def interp(x):
    return mids[146] + (mids[148] - mids[146]) * (x - 146) / 2


print("Market interpolation, printed thresholds:", interp(147), interp(147.8))
print("Market interpolation, original script:",
      interp(133.6*1.10), interp(133.6*1.106))

# Original JSON algebra and cross-question consistency.
f = load(A / "datasets/a09_final.json")
for q in ["r01", "r02"]:
    calc = (
        0.6*f["alt_data"]["used"][q]
        + 0.3*f["base_rate"]["used"][q]
        + 0.1*f["market"]["kalshi_mid_interp"][q]
    )
    print("Original blend", q, calc, "saved", f["final"][q],
          "remove market and renormalize",
          (calc - 0.1*f["market"]["kalshi_mid_interp"][q]) / 0.9)
print("Impact normal P(R02):",
      tail(f["final_calibrated_normal"]["centre"], 1.7, 10.6))
c06 = load(C / "forecasts/2026-09-17-forecast.json")
pa = c06["final"]["vector"]["a_ge_25pct"]
print("Current C06 revision/vector:", c06["revision"], c06["final"]["vector"])
print("Current C06 times old conditional:", pa*f["r03"]["p_r01_given_a"])
print("R03 base-rate formula with stated lift:", .16*.55*(.51/.42),
      "with unexplained .7:", .16*.55*.7)

# RNPL disclosure continuation from both saved matrices.
for name in [
    "metric_persistence_matrix_4Q20-2Q26.csv",
    "metric_persistence_matrix_v2_4Q20-2Q26.csv",
]:
    d = pd.read_csv(C / "datasets" / name, keep_default_na=False)
    cols = list(d.columns)[1:]
    for start in ["4Q20", "1Q23", "1Q24"]:
        hit = den = 0
        for row in d.itertuples(index=False, name=None):
            cells = row[1:]
            for i in range(max(1, cols.index(start)), len(cols)):
                if "L" in cells[i-1] or "C" in cells[i-1]:
                    den += 1
                    hit += int("L" in cells[i] or "C" in cells[i])
        print("Disclosure continuation", name, start, hit, den, hit/den)

# Reaction reference classes use fiscal-quarter windows, not announcement years.
p = read("data/processed/reverse_dcf/C/C_print_panel.csv")
for label, s in [
    ("W1", p[p.print_quarter >= "2023Q1"]),
    ("W2", p[p.print_quarter >= "2024Q1"]),
]:
    for sign, group in s.groupby("nights_accel_sign"):
        v = group.ret_1d_cc_excess_pct
        print("Reaction", label, sign, "n", len(v), "mean", v.mean(),
              "positive", int((v > 0).sum()))
s = read("data/processed/reverse_dcf/E/E_street_sign_history.csv")
s = s[s.day1_excess_pct.notna() & s.street_positioned_for.eq("acceleration")]
print("Accelerating Street bars:",
      s[["print", "day1_excess_pct"]].to_dict("records"),
      "mean", s.day1_excess_pct.mean())
hist = p.set_index("label").nights_yoy_pct
for year in [22, 23, 25]:
    print("Accelerating Q3 to Q4:", year,
          hist[f"3Q{year}"], hist[f"4Q{year}"])

# Keep original dollar shocks to isolate the impact accounting errors.
annual = read("data/processed/margin_build/23_final_model/23_forecast_annual.csv")
annual = annual[annual.scenario.eq("base")].set_index("period")
impact = pd.read_csv(A / "datasets/a09_impact.csv")
for r in impact.itertuples():
    fixed = {}
    for year, dr in [
        ("FY26", r.rev_3q26_musd+r.rev_4q26_musd),
        ("FY27", r.rev_fy27_musd),
    ]:
        revenue = annual.loc[year, "revenue_musd"]
        ebitda = annual.loc[year, "adj_ebitda_musd"]
        fixed[year] = 100*((ebitda+dr)/(revenue+dr)-ebitda/revenue)
    published_p = {"R01": .42, "R02": .32, "R03": .07}[r.question]
    print("Impact", r.question, "held-cost margin changes", fixed,
          "held-cost EPS27", r.rev_fy27_musd*.0014,
          "EV from displayed p/stock",
          published_p*r.stock_usd_per_share_vs_base_case)
print("S01 mean of chosen cells:",
      (.08*5+.17*1.8+.08*(-2.9)+.04*.2)/.37)
print("S01 omitted 10.00-10.09 mass:",
      N.cdf((10.09-9.55)/1.48)-N.cdf((10-9.55)/1.48))

# Auditor benchmarks: one repo-nowcast location/scale, no market weight.
t1, t2 = [(m/133.6-1)*100 for m in [147, 147.8]]
print("Auditor normal probabilities:",
      tail(9.5, 1.7, t1), tail(9.5, 1.7, t2))
for sd in [1.0, 1.48, 1.633596, 1.7, 1.815866, 2.159143, 2.5]:
    print("Auditor sd sensitivity:", sd,
          tail(9.5, sd, t1), tail(9.5, sd, t2))

# Rebuild C06-v2 share draws, then a weak common-cause sensitivity.
# Share priors and k are assumptions, not measured causal coefficients.
rng = random.Random(7)
xs, high = [], []
while len(xs) < 200000:
    s1, step = rng.uniform(19, 21), rng.uniform(.5, 3.5)
    s2 = s1 + step
    if not 20.5 <= s2 <= 23.5:
        continue
    ramp = rng.uniform(0, .5)*step
    exp_mean = 1.4 if rng.random() < .75 else 3.5
    x = min(8, rng.expovariate(1/exp_mean))
    share = s2 + ramp + x + rng.uniform(-1, 1)
    xs.append(x)
    high.append(share >= 24.5)
print("C06-v2 true high share / disclosed-a:",
      mean(high), mean(high)*.75*.85)
for k in [0, .1, .2/1.4, .3/1.4]:
    sigma = math.sqrt(1.7**2-k*k*pstdev(xs)**2)
    ex = mean(xs)
    conditional = [tail(9.5+k*(x-ex), sigma, t1) for x in xs]
    p_given_a = sum(v for v, h in zip(conditional, high) if h)/sum(high)
    print("Auditor joint sensitivity k", k,
          "nights marginal", mean(conditional),
          "P(R01|a)", p_given_a,
          "joint at current C06", pa*p_given_a)
