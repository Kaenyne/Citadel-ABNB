from pathlib import Path
from statistics import NormalDist
import json
import math
import pandas as pd

ROOT = Path.cwd()
D = ROOT / "data/processed"
Q = ROOT / "docs/pitch-forecasts/questions/day1-move-5nov"
Phi = NormalDist().cdf

rx = pd.read_csv(D / "abnb_earnings_reactions.csv")
panel = pd.read_csv(D / "reverse_dcf/C/C_print_panel.csv")
ex = panel.loc[panel.sample_ex_reopening].copy()


def describe(name, frame):
    x = frame.ret_1d_cc_raw_pct
    e = frame.ret_1d_cc_excess_pct
    result = {
        "n": len(frame),
        "mean_raw": x.mean(),
        "median_raw": x.median(),
        "sd_raw_sample": x.std(ddof=1),
        "rms_raw": math.sqrt(x.pow(2).mean()),
        "positive_raw": int((x > 0).sum()),
        "positive_excess": int((e > 0).sum()),
        "abs_ge_7": int((x.abs() >= 7).sum()),
        "abs_ge_10": int((x.abs() >= 10).sum()),
        "abs_gt_15": int((x.abs() > 15).sum()),
    }
    print(name, result)


def solve(a, b):
    """Small dense linear system: pivoted Gauss-Jordan elimination."""
    m = [list(map(float, row)) + [float(v)]
         for row, v in zip(a, b)]
    n = len(b)
    for j in range(n):
        k = max(range(j, n), key=lambda i: abs(m[i][j]))
        m[j], m[k] = m[k], m[j]
        if abs(m[j][j]) < 1e-12:
            raise ValueError("Singular regression")
        scale = m[j][j]
        m[j] = [v / scale for v in m[j]]
        for i in range(n):
            if i != j:
                scale = m[i][j]
                m[i] = [v - scale * w for v, w in zip(m[i], m[j])]
    return [row[-1] for row in m]


def fit(x, y):
    k = len(x[0])
    a = [[sum(row[i] * row[j] for row in x)
          for j in range(k)] for i in range(k)]
    b = [sum(row[i] * v for row, v in zip(x, y))
         for i in range(k)]
    return solve(a, b)


def regression(frame, columns):
    x = [[1.0] + list(row)
         for row in frame[columns].itertuples(index=False, name=None)]
    y = frame.ret_1d_cc_excess_pct.tolist()
    beta = fit(x, y)
    sse = sum(
        (v - sum(a * b for a, b in zip(row, beta))) ** 2
        for row, v in zip(x, y)
    )
    loo_error = baseline_error = 0.0
    for i, v in enumerate(y):
        xx, yy = x[:i] + x[i + 1:], y[:i] + y[i + 1:]
        bb = fit(xx, yy)
        pred = sum(a * b for a, b in zip(x[i], bb))
        loo_error += (v - pred) ** 2
        baseline_error += (v - sum(yy) / len(yy)) ** 2
    return {
        "coefficients": beta,
        "residual_sd": math.sqrt(sse / (len(y) - len(beta))),
        "loo_r2": 1 - loo_error / baseline_error,
    }


def fisher_sign(frame):
    a = frame.loc[frame.nights_accel_sign == 1]
    b = frame.loc[frame.nights_accel_sign == -1]
    n1, n2 = len(a), len(b)
    observed = int((a.ret_1d_cc_excess_pct > 0).sum())
    successes = observed + int((b.ret_1d_cc_excess_pct > 0).sum())

    def mass(k):
        return (math.comb(n1, k) * math.comb(n2, successes - k)
                / math.comb(n1 + n2, successes))

    p0 = mass(observed)
    return sum(
        mass(k)
        for k in range(max(0, successes - n2), min(n1, successes) + 1)
        if mass(k) <= p0 + 1e-12
    )


describe("All prints", panel)
windows = {
    "ex_reopening": ex,
    "W1": panel.loc[panel.print_quarter >= "2023Q1"],
    "W2": panel.loc[panel.print_quarter >= "2024Q1"],
}
for name, frame in windows.items():
    describe(name, frame)
    for sign in (-1, 0, 1):
        describe(f"{name}: sign={sign}",
                 frame.loc[frame.nights_accel_sign == sign])
    below = frame.guide_vs_street_pct < 0
    decel = frame.nights_accel_sign == -1
    strict = frame.loc[below & decel & (frame.guide_dir_code < 0)]
    broad = frame.loc[below & decel & (frame.guide_dir_code <= 0)]
    describe(f"{name}: strict historical proxy", strict)
    describe(f"{name}: broad historical proxy", broad)
    for cols in (
        ["nights_accel_sign"],
        ["nights_accel_sign", "guide_vs_street_pct"],
        ["guide_vs_street_pct"],
    ):
        print(name, cols, regression(frame, cols))
    print(name, "Fisher two-sided excess positivity", fisher_sign(frame))

for sign in (-1, 0, 1):
    for below in (True, False):
        cell = ex.loc[
            (ex.nights_accel_sign == sign)
            & ((ex.guide_vs_street_pct < 0) == below)
        ]
        print("Historical cross-cell", sign, below,
              "n", len(cell),
              "mean", cell.ret_1d_cc_raw_pct.mean(),
              "labels", cell.label.tolist())

old = pd.read_csv(D / "abnb_guidance_reaction_panel.csv")
old_cell = old.loc[
    (old.guide_vs_street_pct < 0) & (old.nq_nights_dir < 0)
]
new_cell = ex.loc[
    (ex.guide_vs_street_pct < 0) & (ex.guide_dir_code < 0)
]
print("Legacy below+lower", len(old_cell),
      old_cell.ret_1d.mean(), old_cell.ret_1d.median())
print("C-panel below+lower", len(new_cell),
      new_cell.ret_1d_cc_raw_pct.mean(),
      new_cell.ret_1d_cc_raw_pct.median())

eligible = ex.loc[
    (ex.nights_accel_sign == -1) & (ex.guide_vs_street_pct < 0)
]
print("Eligible >=10% successes",
      int((eligible.ret_1d_cc_raw_pct >= 10).sum()), "/", len(eligible))
print("0/n one-sided 95% upper bound",
      1 - 0.05 ** (1 / len(eligible)))

g = pd.read_csv(D / "overnight/02_guidance_ledger.csv")
g = g.loc[
    (g.metric == "revenue_usd_m")
    & (g.horizon_quarters == 1)
    & g.actual.notna() & g.value_mid.notna()
].sort_values("print_date")
print("Revenue guides", len(g),
      "above midpoint", int((g.actual > g.value_mid).sum()),
      "above top", int((g.actual > g.value_high).sum()),
      "last8 cushion", (g.tail(8).actual / g.tail(8).value_mid - 1).mean())

big = rx.loc[rx.abnb_1d_pct.abs() >= 7]
recent = big.loc[big.reaction_date >= "2023-01-01"]
print("Large moves: all/negative", len(big),
      int((big.abnb_1d_pct < 0).sum()))
print("Large moves since 2023: all/negative", len(recent),
      int((recent.abnb_1d_pct < 0).sum()))

street = pd.read_csv(D / "reverse_dcf/E/E_street_sign_history.csv")
print("4Q24 Street classification",
      street.loc[street["print"] == "4Q24",
                 ["street_positioned_for", "printed"]].to_dict("records"))
crush = pd.read_csv(D / "reverse_dcf/B/B_bbg_print_implied_vs_realised.csv")
print("IV-crush mean/correlation",
      crush.implied_event_sd_crush_pct.mean(),
      crush.implied_event_sd_crush_pct.corr(
          crush.realised_raw_cc_1d_pct.abs()))

kalshi = json.loads(
    (Q / "sources/kalshi_markets_KXABNB_open_20260917T030925Z.json")
    .read_text(encoding="utf-8")
)
for key in ("volume_fp", "open_interest_fp", "volume_24h_fp"):
    print("Kalshi", key,
          sum(float(m.get(key) or 0) for m in kalshi["markets"]))

# Exact historical Gaussian-kernel estimate, without Monte Carlo.
weights = [2.0 if q >= "2023Q1" else 1.0 for q in rx.quarter]
weight_sum = sum(weights)


def historical_cdf(x):
    return sum(
        w * Phi((x - v) / 3)
        for w, v in zip(weights, rx.abnb_1d_pct)
    ) / weight_sum


def quantile(cdf, probability):
    lo, hi = -200.0, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if cdf(mid) < probability:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


percentiles = (.05, .10, .25, .50, .75, .90, .95)
print("Historical KDE percentiles",
      [quantile(historical_cdf, p) for p in percentiles])
print("Historical KDE P<=-8 / P>=5",
      historical_cdf(-8), 1 - historical_cdf(5))

# Pair arithmetic from the independently replayed saved term structure.
ts = pd.read_csv(Q / "datasets/options_term_structure.csv").set_index("expiry")
for pre in ("2026-10-16", "2026-10-30"):
    for post in ("2026-11-20", "2026-12-18"):
        a, b = ts.loc[pre], ts.loc[post]
        variance = b["T"] * (
            (b.atm_iv_pct / 100) ** 2 - (a.atm_iv_pct / 100) ** 2
        )
        print("Options pair", pre, post, 100 * math.sqrt(max(0, variance)))

meta = json.loads(
    (Q / "sources/yfinance_abnb_chain_meta_20260917T030919Z.json")
    .read_text(encoding="utf-8")
)
chain = pd.read_csv(Q / "sources/yfinance_abnb_chain_20260917T030919Z.csv")
straddle = chain.loc[
    (chain.expiry == "2026-11-20") & (chain.strike == 170)
]
assert len(straddle) == 2
print("20Nov $170 straddle bid/mid/ask %spot",
      100 * straddle.bid.sum() / meta["spot"],
      50 * (straddle.bid.sum() + straddle.ask.sum()) / meta["spot"],
      100 * straddle.ask.sum() / meta["spot"])
print("Split-normal imposed mean",
      -.3 + math.sqrt(2 / math.pi) * (8.1 - 9.9))
print("Implemented dollars per +0.5pt nights", .0032 * .5 * 3161)
print("Log's displayed SD formula",
      math.sqrt(7.5**2 + 2.4**2 + 1.3**2 + 3.5**2))

saved = json.loads(
    (Q / "datasets/s01_components.json").read_text(encoding="utf-8")
)
print("Saved cell-weighted mean",
      sum(c["prob"] * c["mean"] for c in saved["cells_model"]))
print("Saved final mean", saved["estimates"]["FINAL_mixture"]["mean"])

# Auditor's explicit joint distribution: judgmental parameters, not a fit.
states = {
    -1: Phi((10.09 - 9.55) / 1.48),
    1: 1 - Phi((10.59 - 9.55) / 1.48),
}
states[0] = 1 - sum(states.values())
below = {-1: .77, 0: .72}
below[1] = (.72 - sum(states[s] * below[s] for s in (-1, 0))) / states[1]
cd = {-1: .80, 0: .50}
cd[1] = (.61 - sum(states[s] * cd[s] for s in (-1, 0))) / states[1]

prior = float(ex.ret_1d_cc_raw_pct.mean())
cells = []
for sign in (-1, 0, 1):
    for is_below in (True, False):
        sample = ex.loc[
            (ex.nights_accel_sign == sign)
            & ((ex.guide_vs_street_pct < 0) == is_below)
        ]
        mean = (sample.ret_1d_cc_raw_pct.sum() + 4 * prior) / (len(sample) + 4)
        weight = states[sign] * (
            below[sign] if is_below else 1 - below[sign]
        )
        cells.append((float(weight), float(mean)))


def mixture_cdf(x, components=cells):
    return sum(
        w * (.95 * Phi((x - mu) / 8) + .05 * Phi((x - mu) / 18))
        for w, mu in components
    )


assert abs(sum(w for w, _ in cells) - 1) < 1e-12
print("Auditor states/below/C02cd", states, below, cd)
print("Auditor percentiles", [quantile(mixture_cdf, p) for p in percentiles])
print("Auditor thresholds",
      mixture_cdf(-8), mixture_cdf(-5),
      1 - mixture_cdf(5), 1 - mixture_cdf(10))
mean = sum(w * mu for w, mu in cells)
variance = sum(w * (77 + mu * mu) for w, mu in cells) - mean * mean
print("Auditor mean/sd", mean, math.sqrt(variance))
print("Auditor boundary masses", mixture_cdf(-40), 1 - mixture_cdf(40))
base_components = [(1.0, cells[0][1])]
base_cdf = lambda x: mixture_cdf(x, base_components)
print("Auditor three-gate base probability",
      states[-1] * below[-1] * cd[-1])
print("Auditor base median/Pdown/P<=-8",
      quantile(base_cdf, .5), base_cdf(0), base_cdf(-8))
