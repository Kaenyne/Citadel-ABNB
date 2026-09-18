"""A02 read-only audit reproduction.
Dependencies: Python standard library and pandas. No writes or network calls.
"""
from pathlib import Path
from math import erf, sqrt
import json
import re
import html
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "data/processed/overnight/02_guidance_ledger.csv").exists():
    ROOT = next(
        p for p in Path(__file__).resolve().parents
        if (p / "data/processed/overnight/02_guidance_ledger.csv").exists()
    )


def read(path):
    return pd.read_csv(ROOT / path, comment="#")


def show(label, value):
    print("\n" + label)
    print(value.to_string(index=False)
          if isinstance(value, pd.DataFrame) else value)


def key(q):
    return (2000 + int(q[-2:])) * 4 + int(q[0]) - 1


def period(q):
    return "20" + q[-2:] + "Q" + q[0]


def phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def vector(values):
    return dict(zip("abcde", [round(float(x), 6) for x in values]))


ledger = read("data/processed/overnight/02_guidance_ledger.csv")
history = read(
    "data/processed/abnb_driver_history_quarterly.csv"
).set_index("quarter")

nights = ledger[
    (ledger.metric == "nights_yoy_pct")
    & (ledger.horizon_quarters == 1)
].copy()
nights["key"] = nights.print_quarter.map(key)
nights = nights.sort_values("key")
nights["printed_growth"] = nights.print_quarter.map(
    history.nights_m_yoy_pct
)

# Verify ledger quotations against original saved letters.
def normalize(s):
    return re.sub("[^a-z0-9]", "", s.lower())


fy_revenue = ledger[
    (ledger.metric == "revenue_yoy_pct")
    & ledger.target_period.str.startswith("FY")
].copy()

for _, row in pd.concat([nights, fy_revenue]).iterrows():
    raw = (ROOT / row.source_file).read_text(
        encoding="utf-8", errors="replace"
    )
    text = html.unescape(re.sub("<[^>]+>", " ", raw))
    assert normalize(row.quote) in normalize(text), row.guide_id

show("Original-letter quote checks", len(nights) + len(fy_revenue))

# 1Q23 compares nights with next-quarter revenue growth.
# Its revenue-guide upper bound is below just-printed nights growth.
r23 = ledger[
    (ledger.print_quarter == "1Q23")
    & (ledger.metric == "revenue_usd_m")
].iloc[0]
upper23 = 100 * (
    r23.value_high / history.loc["2Q22", "revenue_musd"] - 1
)
assert upper23 < history.loc["1Q23", "nights_m_yoy_pct"]

# 4Q24 compares with 1Q24 EXCLUDING Leap Day, not printed 4Q24.
assert (
    history.loc["1Q24", "nights_m_yoy_pct"] - 1
    < history.loc["4Q24", "nights_m_yoy_pct"]
)


def classify(row):
    if row.guide_type == "bucket":
        delta = row.value_mid - row.printed_growth
        return (
            "down" if delta < -0.5
            else "up" if delta > 0.5
            else "stable"
        )
    if row.print_quarter == "4Q24":
        return "down"
    return {
        "below": "down",
        "below_revenue_growth": "down",
        "above": "up",
        "stable": "stable",
        "approx": "stable",
    }[row.direction]


nights["class"] = nights.apply(classify, axis=1)
show("Corrected descriptor classes", nights[
    ["print_quarter", "guide_type", "direction",
     "printed_growth", "class"]
])

for label, sample in [
    ("all observable guides", nights),
    ("resolved target quarters only", nights[nights.actual.notna()]),
    ("W1: print quarter 1Q23+", nights[nights.key >= key("1Q23")]),
    ("W2: print quarter 1Q24+", nights[nights.key >= key("1Q24")]),
    (
        "direct-comparison-only sensitivity",
        nights[~nights.print_quarter.isin(["1Q23", "4Q24"])],
    ),
]:
    show(label, {
        "n": len(sample),
        **sample["class"].value_counts().to_dict(),
    })

show("Format counts, all 17",
     nights.guide_type.value_counts().to_dict())
show("Format counts, print before 2025",
     nights[nights.key < key("1Q25")]
     .guide_type.value_counts().to_dict())
show("November nights classes",
     nights[nights.print_quarter.str.startswith("3Q")]
     ["class"].value_counts().to_dict())

reaction = read("data/processed/abnb_guidance_reaction_panel.csv")
show("Reaction-panel direction counts",
     reaction.nq_nights_dir.value_counts(dropna=False).to_dict())

vol = ledger[
    (ledger.guide_type == "bucket")
    & ledger.metric.isin(["nights_yoy_pct", "gbv_yoy_pct"])
    & ledger.actual.notna()
].copy()
vol["beat_mid_pp"] = vol.actual - vol.value_mid
vol["beat_top_pp"] = vol.actual - vol.value_high
show("Resolved volume buckets", vol[
    ["print_quarter", "metric", "actual",
     "beat_mid_pp", "beat_top_pp"]
])
show("Volume sample dependence", {
    "rows": len(vol),
    "print_events": vol.print_quarter.nunique(),
    "above_top": int((vol.actual > vol.value_high).sum()),
    "nights_rows": int((vol.metric == "nights_yoy_pct").sum()),
})

rev = ledger[
    (ledger.metric == "revenue_usd_m")
    & (ledger.guide_type == "range")
    & ledger.actual.notna()
].copy()
rev["key"] = rev.target_period.map(key)
rev = rev.sort_values("key")
rev["cushion_pct"] = 100 * (rev.actual / rev.value_mid - 1)

for label, sample in [
    ("all", rev),
    ("W1 target 1Q23+", rev[rev.key >= key("1Q23")]),
    ("W2 target 1Q24+", rev[rev.key >= key("1Q24")]),
]:
    show("Revenue beats " + label, {
        "n": len(sample),
        "above_mid": int((sample.actual > sample.value_mid).sum()),
        "above_top": int((sample.actual > sample.value_high).sum()),
    })

t8 = rev.tail(8).cushion_pct
show("Trailing-eight cushion mean/median/sample SD",
     (t8.mean(), t8.median(), t8.std()))

q4 = rev[rev.target_period.str.startswith("4Q")]
show("Q4 cushions", q4[["target_period", "cushion_pct"]])
show("Q4 mean/median/last-three mean", (
    q4.cushion_pct.mean(),
    q4.cushion_pct.median(),
    q4.tail(3).cushion_pct.mean(),
))

fy_revenue["key"] = fy_revenue.print_quarter.map(key)
fy_revenue = fy_revenue.sort_values("key")
fy_revenue["change"] = (
    fy_revenue.groupby("target_period").value_mid.diff()
)
show("FY revenue guide updates", fy_revenue[
    ["print_quarter", "target_period", "value_mid", "change"]
])
show("Revenue raises/updates", (
    int((fy_revenue.change > 0).sum()),
    int(fy_revenue.change.notna().sum()),
))

margin = read(
    "data/processed/margin_build/05_mgmt_statements_v2/"
    "05_guide_language_pattern.csv"
)
nov = margin[
    margin.is_november.astype(str).str.lower().eq("true")
]
show("All November margin sentences", nov[
    ["print", "fy_sentence_type", "actual_minus_guide_bp",
     "q4_actual_minus_implied_pts"]
])
show("November point beats: n/mean bp", (
    int(nov.actual_minus_guide_bp.notna().sum()),
    nov.actual_minus_guide_bp.mean(),
))
eligible = nov[
    nov["print"].isin(["3Q22", "3Q23", "3Q24", "3Q25"])
]
show("November letters with an existing same-year FY guide", {
    "n": len(eligible),
    "approx_point": int(
        eligible.fy_sentence_type.str.startswith("approx").sum()
    ),
    "omitted": int(eligible.fy_sentence_type.eq("none").sum()),
})

# Recompute quarterly kappa from L0's named at-print vintage rows.
vintages = read(
    "data/processed/forecast_methods/L0/L0_vintage_register.csv"
)
ap = vintages[
    vintages.register_id.eq("AP-" + vintages.period + "-revenue")
]
rev["period"] = rev.target_period.map(period)
pairs = rev.merge(ap, on="period")
pairs["kappa_pct"] = 100 * (pairs.value / pairs.value_mid - 1)
lseg = pairs[pairs.vendor == "LSEG"].sort_values("key")
show("L0 quarterly kappa: n/mean/sample SD/trailing-eight mean", (
    len(lseg),
    lseg.kappa_pct.mean(),
    lseg.kappa_pct.std(),
    lseg.tail(8).kappa_pct.mean(),
))

current = read(
    "data/processed/margin_build/03_consensus_pit/"
    "03_current_consensus.csv"
)
current = current[
    (current.vendor == "LSEG")
    & current.period.isin(["3Q26", "4Q26", "FY26"])
].set_index("period")
show("Actual consensus provenance", current.reset_index()[
    ["period", "as_of_row_date", "revenue_obs_date",
     "revenue_mean", "revenue_n", "revenue_sd", "revenue_high"]
])

fy25 = history.loc[
    ["1Q25", "2Q25", "3Q25", "4Q25"], "revenue_musd"
].sum()
h1 = history.loc[["1Q26", "2Q26"], "revenue_musd"].sum()
annual = current.loc["FY26", "revenue_mean"]
q4street = current.loc["4Q26", "revenue_mean"]

for label, total in [
    ("log: deflate entire FY", annual / 1.006),
    (
        "illustrative: deflate only Q4",
        annual - q4street + q4street / 1.006,
    ),
    (
        "quarter-sum version",
        h1 + current.loc["3Q26", "revenue_mean"]
        + q4street / 1.006,
    ),
]:
    show(label, {
        "musd": total,
        "growth_pct": 100 * (total / fy25 - 1),
    })

bridge = read(
    "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv"
).set_index("quarter")
b4 = bridge.loc["4Q26"]
show("Bridge range is fixed-GBV conversion extrema", (
    1000 * b4.lagged_gbv_busd * b4.conversion_min,
    1000 * b4.lagged_gbv_busd * b4.conversion_max,
))
show("Bridge points",
     bridge.reset_index()[["quarter", "revenue_musd"]])

# Distribution assumptions are explicit; not fitted here.
cond = [
    [.42, .20, .28, .08, .02],
    [.10, .22, .50, .15, .03],
    [.05, .10, .40, .40, .05],
]


def mix(weights):
    return [
        sum(weights[j] * cond[j][i] for j in range(3))
        for i in range(5)
    ]


show("C02 original decomposition", vector(mix([.38, .42, .20])))
for mu in [9.5, 9.6]:
    bins = [
        1 - phi((10 - mu) / 1.48),
        phi((10 - mu) / 1.48) - phi((9 - mu) / 1.48),
        phi((9 - mu) / 1.48),
    ]
    show("C02 normal bins " + str(mu), bins)
    show("C02 repaired-bin tree " + str(mu), vector(mix(bins)))

show("Maximum one-point interval mass under SD 1.48",
     2 * phi(.5 / 1.48) - 1)
show("Original P(Q3 >=10 | C02=a)",
     .38 * .42 / mix([.38, .42, .20])[0])

paths = read("data/processed/q3nowcast/E/backtest_wf_paths.csv")
errors = paths[
    (paths.feature == "GLOBAL|yoy_all|w_equal")
    & (paths.lag == 0)
    & (paths.target == "nights_yoy")
    & (paths.window == "2023Q1+")
]
show("Reviews error sample: n/RMSE/naive RMSE/mean/sample SD", (
    len(errors),
    sqrt(errors.err_feature.pow(2).mean()),
    sqrt(errors.err_naive.pow(2).mean()),
    errors.err_feature.mean(),
    errors.err_feature.std(),
))


def c03(q3m=4795, q3s=40, q4m=3085, q4s=80, rho=0):
    mu = h1 + q3m + q4m
    sd = sqrt(q3s*q3s + q4s*q4s + 2*rho*q3s*q4s)

    def below(rate):
        return phi((fy25*(1+rate/100)-mu)/sd)

    a = (.5*(1-below(15.5)) + .5*(1-below(16))) / 1.02
    c = (
        .5*(below(15.5)-below(14.5))
        + .5*(below(16)-below(15))
    ) / 1.02
    d = (.5*below(14.5) + .5*below(15)) / 1.02
    return {
        "fy_mean": mu,
        "growth_pct": 100*(mu/fy25-1),
        "sd_pp": 100*sd/fy25,
        "p_ge16": 1-below(16),
        "vector": vector([
            .55*a+.35*.30,
            .55*.02/1.02+.35*.45,
            .55*c+.35*.15,
            .55*d+.35*.10,
            .10,
        ]),
    }


show("C03 original", c03())
show("C03 Street-centred", c03(q3m=4744, q3s=30))
show("C03 B2 guide", c03(q4m=3161, q4s=117))
show("C03 positive-correlation sensitivity", c03(rho=.5))

questions = ROOT / "docs/pitch-forecasts/questions"
for slug in ["q4-nights-bucket", "fy26-revenue-guide-language"]:
    f = json.loads(
        (questions/slug/"forecasts/2026-09-17-forecast.json")
        .read_text(encoding="utf-8")
    )
    assert abs(sum(f["final"]["vector"].values()) - 1) < 1e-12

market = json.loads(
    (
        questions/"q4-nights-bucket/sources/"
        "kalshi_market_KXABNB-26NOVNEB-148000000_20260917T025502Z.json"
    ).read_text(encoding="utf-8")
)["market"]
show("Kalshi stored fields", {
    k: market.get(k) for k in [
        "volume", "volume_fp",
        "open_interest", "open_interest_fp",
        "liquidity_dollars", "yes_bid_dollars", "yes_ask_dollars",
    ]
})

# Audit comparisons: judgmental weights, NOT fitted estimates.
p10 = 1 - phi((10-9.5)/1.48)
explicit = [.20, .15, .50, .15, 0]
directional = [.40*p10, .40*(1-p10), 0, .60, 0]
own02 = [
    .60*explicit[i] + .35*directional[i]
    + (.05 if i == 4 else 0)
    for i in range(5)
]
show("Audit C02 unrounded", vector(own02))

mu = (
    h1
    + bridge.loc["3Q26", "revenue_musd"]
    + b4.revenue_musd/(1+q4.tail(3).cushion_pct.mean()/100)
)


def below(rate):
    return phi((fy25*(1+rate/100)-mu)/110)


a = .5*(1-below(15.5)) + .5*(1-below(16))
d = .5*below(14.5) + .5*below(15)
own03 = [
    .50*a+.35*.25,
    .35*.55,
    .50*(1-a-d)+.35*.10,
    .50*d+.35*.10,
    .15,
]
show("Audit C03 unrounded", {
    "mean_musd": mu,
    "vector": vector(own03),
})
