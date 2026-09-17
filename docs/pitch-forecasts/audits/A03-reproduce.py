from pathlib import Path
from statistics import NormalDist
import json
import math
import re

import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "docs/pitch-forecasts/QUESTIONS.md").exists():
    ROOT = Path(__file__).resolve().parents[3]


def read(rel):
    return pd.read_csv(ROOT / rel, comment="#")


def ordinal(q):
    m = re.fullmatch(r"([1-4])Q(\d{2})", q)
    if not m:
        raise ValueError(q)
    return (2000 + int(m[2])) * 4 + int(m[1])


def family(quote):
    text = quote.lower()
    # 3Q25: "flat-to-down slightly" describes dollars, not margin.
    if "and for adjusted ebitda margin" in text:
        text = text[text.index("and for adjusted ebitda margin"):]
    if "flat to down" in text or "at or slightly below" in text:
        return "flat_to_down"
    if "in-line to modestly higher" in text:
        return "flat_to_up"
    if "approximately flat" in text:
        return "flat"
    if any(word in text for word in ("decline", "lower", "down")):
        return "down"
    return "up"


def counts(frame):
    mapped = frame.family.replace(
        {"flat_to_down": "down", "flat_to_up": "up"}
    )
    return mapped.value_counts().reindex(
        ["down", "flat", "up", "none"], fill_value=0
    ).to_dict()


ledger = read("data/processed/overnight/02_guidance_ledger.csv")
margin = ledger[ledger.metric.isin([
    "adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts"
])].copy()
fy = margin[margin.target_period.str.startswith("FY")].copy()

base = ROOT / "docs/pitch-forecasts/questions"
d4 = base / "fy26-margin-sentence"
d9 = base / "q4-margin-direction-sentence"

copied = pd.read_csv(d4 / "datasets/fy_margin_guide_ledger.csv")
print("FY EBITDA-margin rows:", len(fy))
print("Copied rows / FCF rows:", len(copied),
      int(copied.quote.str.contains("Free Cash Flow", case=False).sum()))

quarterly = margin[
    margin.target_period.str.fullmatch(r"[1-4]Q\d{2}")
].copy()
quarterly["horizon_check"] = [
    ordinal(t) - ordinal(p)
    for t, p in zip(quarterly.target_period, quarterly.print_quarter)
]
q = quarterly[
    (quarterly.horizon_check == 1)
    & (quarterly.print_date >= "2021-08-12")
].copy()
q["family"] = q.quote.map(family)
print("Exact next-quarter sentences:", len(q),
      q.family.value_counts().to_dict())

reaction = read("data/processed/abnb_guidance_reaction_panel.csv")
calendar = reaction[
    reaction.print_date >= "2021-08-12"
][["quarter", "print_date"]]
calendar = calendar.merge(
    q[["print_quarter", "family"]],
    left_on="quarter", right_on="print_quarter",
    how="left", validate="one_to_one"
)
calendar["family"] = calendar.family.fillna("none")
print("All print opportunities:", len(calendar), counts(calendar))
print("No quarterly sentence:",
      calendar.loc[calendar.family == "none", "quarter"].tolist())

recent = q[q.print_date >= "2024-08-06"]
nov = q[pd.to_datetime(q.print_date).dt.month == 11]
print("Since 2Q24:", len(recent), counts(recent))
print("Novembers:", len(nov), counts(nov))
for start in ["1Q23", "1Q24"]:
    w = q[q.target_period.map(ordinal).between(
        ordinal(start), ordinal("2Q26")
    )]
    print("Target window", start, "through 2Q26:", len(w), counts(w))

mid = reaction[
    pd.to_datetime(reaction.print_date).dt.month.isin([5, 8])
    & (reaction.print_date >= "2022-01-01")
]
print("Midyear actions:", mid[
    ["quarter", "fy_margin_action", "fy_margin_raised"]
].to_dict("records"))
pre = mid[mid.print_date < "2026-01-01"]
print("Pre-2026 coded raises:",
      int((pre.fy_margin_raised == 1).sum()), "/", len(pre))

novfy = fy[pd.to_datetime(fy.print_date).dt.month == 11]
rule_results = []
for row in novfy.itertuples():
    earlier = fy[
        (fy.target_period == row.target_period)
        & (fy.print_date < row.print_date)
    ].sort_values("print_date")
    if earlier.empty:
        continue
    previous = earlier.iloc[-1]
    if (previous.metric == "adj_ebitda_margin_pct"
            and previous.guide_type == "floor"
            and pd.notna(previous.value_low)):
        predicted = previous.value_low + 0.5
        rule_results.append({
            "print": row.print_quarter,
            "predicted": predicted,
            "stated": row.value_mid,
            "exact": abs(predicted - row.value_mid) < 1e-9,
        })
print("Numeric-floor November rule:", rule_results)
print("Exact matches:",
      sum(r["exact"] for r in rule_results), "/", len(rule_results))
print("Ledger November cushions:",
      (novfy.actual - novfy.value_mid).tolist())
print("Mean ledger November cushion:",
      (novfy.actual - novfy.value_mid).mean())
print("FY2022 pre-November guide:",
      fy.loc[fy.print_quarter == "2Q22", "quote"].tolist())

m3 = "data/processed/margin_build/M3_guide_policy_margin/"
back = read(m3 + "M3_guide_forecast_november_backtest.csv")
print("November type hits:", int(back.type_hit.sum()), "/", len(back))
cushion = read(m3 + "M3_cushion_history.csv")
print("Cushions by bucket:", cushion.groupby("bucket").cushion_pp.agg(
    ["count", "mean"]
).to_dict("index"))

features = read("data/processed/predictive/04_print_features.csv")
for start in ["2023Q1", "2024Q1"]:
    w = features[features.print_quarter.between(start, "2026Q2")]
    print("Realised window", start, "n", len(w),
          "guide met", int(w.margin_guide_met.sum()),
          "yoy mean/median/positive",
          w.margin_yoy_pts.mean(), w.margin_yoy_pts.median(),
          int((w.margin_yoy_pts > 0).sum()))

slightly = read(m3 + "M3_slightly_magnitude.csv")
s = slightly[
    (slightly.adverb == "slightly")
    & slightly.realised_yoy_pp.notna()
]
print("Stored slightly:", len(s), s.realised_yoy_pp.abs().mean())
s = s[s.quarter != "2025Q4"]
print("Margin-only slightly:", len(s), s.realised_yoy_pp.abs().mean())

bt = read(m3 + "M3_q4_implied_backtest.csv")
bt = bt[bt.rev4_source == "guide_mid"].copy()
bt["recomputed_q4"] = 100 * (
    bt.fy_sentence_level_pct / 100 * (bt.ytd_rev + bt.rev4)
    - bt.ytd_ebitda
) / bt.rev4
print("Historical identity maximum error:",
      (bt.recomputed_q4 - bt.q4_margin_implied_pct).abs().max())
print("Q4 actual minus November-implied:",
      len(bt), (bt.q4_margin_actual_pct - bt.recomputed_q4).mean())
print("Pre-November Street:", bt[
    ["quarter", "street_q4_margin_pct", "seasonal_naive_q4_margin_pct"]
].to_dict("records"))
direction = bt.quarter.map({
    "2023Q4": 1, "2024Q4": -1, "2025Q4": -1
})
matches = (
    (bt.street_q4_margin_pct - bt.seasonal_naive_q4_margin_pct)
    * direction > 0
)
print("Street direction matches:", int(matches.sum()), "/", len(bt))
actuals = pd.Series(
    [bt.iloc[0].seasonal_naive_q4_margin_pct]
    + bt.q4_margin_actual_pct.tolist()
)
print("2022-25 Q4 mean/sample SD:", actuals.mean(), actuals.std())

cons = read(
    "data/processed/margin_build/03_consensus_pit/"
    "03_current_consensus.csv"
)
row = cons[(cons.period == "4Q26") & (cons.vendor == "LSEG")].iloc[0]
print("Current LSEG fields:", row[[
    "as_of_row_date", "ebitda_obs_date", "revenue_obs_date",
    "ebitda_mean", "revenue_mean", "ebitda_n", "revenue_n",
    "implied_margin_pct", "lseg_margin_mean_pct"
]].to_dict())
print("Ratio margin:", 100 * row.ebitda_mean / row.revenue_mean)
print("EBITDA dispersion / fixed revenue:",
      100 * row.ebitda_sd / row.revenue_mean)

bridge = read("data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv")
r3 = bridge.loc[bridge.quarter == "3Q26", "revenue_musd"].iloc[0]
r4 = bridge.loc[bridge.quarter == "4Q26", "revenue_musd"].iloc[0]
print("Live identity multipliers:", (6286 + r3 + r4) / r4, -r3 / r4)
print("FY36/Q4 28.3 requires Q3 margin:",
      100 * (0.36 * (6286 + r3 + r4) - 1780 - 0.283 * r4) / r3)
print("Bridge implied Q4 guide:", r4 / 1.0388)

f4 = json.loads(
    (d4 / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8")
)
f9 = json.loads(
    (d9 / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8")
)
print("Final sums:",
      sum(f4["final"]["vector"].values()),
      sum(f9["final"]["vector"].values()))
c4, c9, p = f4["conditionals"], f9["conditionals"], 0.80
print("C04 b implied by published conditionals:",
      p * c4["p_b_given_q4_guide_below_street"]
      + (1-p) * c4["p_b_given_q4_guide_not_below"])
print("C09 implied by published conditionals:", {
    k: p * c9["given_q4_guide_below_street"][k]
       + (1-p) * c9["given_q4_guide_not_below"][k]
    for k in "abcd"
})

joint = json.loads(
    (d4 / "datasets/mc_joint_and_conditionals.json").read_text(
        encoding="utf-8")
)["joint_C04xC09"]
v4 = dict(zip("abcde", f4["final"]["vector"].values()))
print("Raw joint reweighted to final C04:", {
    b: sum(
        v4[a] * joint[a+b] / sum(joint[a+c] for c in "abcd")
        for a in "abcde"
    )
    for b in "abcd"
})

source = json.loads(
    (d4 / "sources/polymarket_search_airbnb.json").read_text(
        encoding="utf-8")
)
print("Polymarket pagination:", source["pagination"])
kalshi = json.loads(
    (d4 / "sources/kalshi_KXABNB_markets.json").read_text(
        encoding="utf-8")
)
for market in kalshi["markets"]:
    if market["ticker"].endswith(("148000000", "146000000")):
        print("Kalshi saved liquidity:", {
            k: market.get(k)
            for k in ["ticker", "volume", "volume_fp",
                      "yes_bid_dollars", "yes_ask_dollars"]
        })

old = [.26, .42, .05, .24, .03]
for new in [[.26, .40, .06, .24, .04],
            [.26, .40, .05, .24, .05]]:
    print("Expected log cost, nats:",
          sum(a * math.log(a/b) for a, b in zip(old, new)))

print("Independent C04 affordability blend:",
      .25 * .75 + .75 * (
          1 - NormalDist(35.72661108582304, .6).cdf(36.1)
      ))
distribution = NormalDist((28.3 + row.implied_margin_pct) / 2, 1.8)
print("Independent C09 before rounding:", [
    .95 * distribution.cdf(27.7),
    .95 * (distribution.cdf(28.9) - distribution.cdf(27.7)),
    .95 * (1 - distribution.cdf(28.9)),
    .05,
])
print("No files written.")
