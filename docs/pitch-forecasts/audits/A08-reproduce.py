from pathlib import Path
from statistics import NormalDist
import json
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path.cwd()
QROOT = ROOT / "docs/pitch-forecasts/questions"


def read(path):
    return pd.read_csv(ROOT / path, comment="#")


def show(label, value):
    print("\n" + label)
    if isinstance(value, pd.DataFrame):
        print(value.to_string(index=False))
    else:
        print(value)


def qkey(q):
    return (2000 + int(q[2:])) * 4 + int(q[0])


g = read("data/processed/overnight/02_guidance_ledger.csv")
p = read("data/processed/abnb_guidance_reaction_panel.csv")
k = read("data/processed/overnight/02_kpi_panel_quarterly.csv")[
    ["quarter", "gbv_musd", "revenue_musd", "nights_m"]
].copy()
k = k.assign(order=k.quarter.map(qkey)).sort_values("order")
k["lag_gbv"] = 2 * k.gbv_musd.shift(1) / 3 + k.gbv_musd.shift(2) / 3
k["lambda_pct"] = 100 * k.revenue_musd / k.lag_gbv

# F01: count statements, not repeated commentary about the same guide.
n = g[g.metric.str.contains("nights")].copy()
pre = n[pd.to_datetime(n.print_date).dt.year < 2025]
show("F01 pre-2025 formats", pre.guide_type.value_counts().to_dict())

bucket = n[n.guide_type == "bucket"].copy()
bucket["top_beat"] = bucket.actual - bucket.value_high
show("F01 bucket outcomes", bucket[
    ["print_quarter", "target_period", "value_mid",
     "value_high", "actual", "top_beat"]
])
resolved = bucket.dropna(subset=["actual", "value_high"])
show("F01 resolved bucket beats", {
    "n": len(resolved),
    "above_top": int((resolved.top_beat > 0).sum()),
})
show("F01 nights statements since 2Q22",
     len(n[n.print_quarter.map(qkey) >= qkey("2Q22")]))

old = n[(n.print_quarter == "4Q21") &
        (n.target_period == "1Q22")].iloc[0]
prior = k.set_index("quarter").loc["1Q21", "nights_m"]
show("F01 2019-comparator implied lower growth bound",
     100 * (old.comparator_value / prior - 1))

# F02: actual / dollar-guide midpoint, without rounded growth integers.
q = g[(g.metric == "revenue_usd_m") &
      g.print_quarter.str.startswith("4Q")].copy()
q["cushion_pct"] = 100 * (q.actual / q.value_mid - 1)
show("F02 Q1 cushions", q[
    ["print_quarter", "target_period", "value_mid",
     "actual", "cushion_pct"]
])
show("F02 cushion statistics",
     q.cushion_pct.agg(["mean", "median", "std"]).to_dict())

for year in [23, 24]:
    s = q[q.target_period.map(qkey) >= qkey("1Q" + str(year))]
    show(f"Q1 target window 20{year}+", {
        "n": len(s), "mean": s.cushion_pct.mean(),
        "sample_sd": s.cushion_pct.std(),
    })

l = k[k.quarter.str.startswith("1Q")].copy()
l["pred"] = l.lambda_pct.shift().rolling(2).mean() / 100 * l.lag_gbv
l["error_pct"] = 100 * (l.pred / l.revenue_musd - 1)
show("F02 Q1 lambda and last-two-season PIT errors",
     l[["quarter", "lambda_pct", "pred", "error_pct"]])

pp = p.set_index("quarter")
changes = pd.Series([
    pp.loc[f"4Q{y}", "nq_rev_guide_growth"] -
    pp.loc[f"3Q{y}", "nq_rev_guide_growth"]
    for y in range(22, 26)
])
show("F02 dollar-implied Q1-minus-Q4 growth changes", {
    "values": changes.tolist(), "mean": changes.mean(),
    "sample_sd": changes.std(),
})
show("F02 listed rounded-change sample SD",
     pd.Series([-1.5, 0, -4, 6.5]).std())
show("F02 February numeric growth-range count", len(g[
    g.print_quarter.str.startswith("4Q") &
    (g.metric == "revenue_yoy_pct") &
    (g.guide_type == "range")
]))

feb = p[p.quarter.str.startswith("4Q")].copy()
show("February reaction and guide-gap panel", feb[
    ["quarter", "print_date", "ret_1d", "exc_1d",
     "guide_vs_street_pct"]
])
show("February positive returns", {
    "n": len(feb),
    "raw_positive": int((feb.ret_1d > 0).sum()),
    "excess_positive": int((feb.exc_1d > 0).sum()),
})
for year in [2022, 2023, 2024]:
    s = feb[pd.to_datetime(feb.print_date).dt.year >= year]
    s = s.dropna(subset=["guide_vs_street_pct"])
    show(f"February guide vs Street, {year}+", {
        "n": len(s),
        "above": int((s.guide_vs_street_pct > 0).sum()),
        "mean_gap_pct": s.guide_vs_street_pct.mean(),
    })

reg = read("data/processed/forecast_methods/L0/L0_vintage_register.csv")
show("F02 historical pre-guide vendor/timestamp rows", reg[
    reg.period.isin(
        ["2022Q1", "2023Q1", "2024Q1", "2025Q1", "2026Q1"]
    ) & (reg.role == "pre_guide")
][["period", "vendor", "value", "as_of_timestamp"]])
show("F02 2027Q1 L0 row count", int(reg.period.eq("2027Q1").sum()))
cons = read(
    "data/processed/margin_build/06_fy27_path_v2/"
    "06_consensus_quarterly_2027.csv"
)
show("F02 separate 1Q27 consensus observation",
     cons[cons.quarter == "1Q27"])

# Rebuild the SAME-TARGET consensus revision relationship.
cs = read("data/processed/overnight/16_consensus_at_print_merged.csv")
rows = []
for _, r in cs.iterrows():
    if not isinstance(r.next_quarter, str):
        continue
    following = cs[cs.print_quarter == r.next_quarter]
    if len(following) != 1:
        continue
    pre_c = r.next_q_cons_revenue_musd
    guide = r.next_q_guide_mid_musd
    post_c = following.iloc[0].cons_revenue_musd
    if any(pd.isna(x) for x in [pre_c, guide, post_c]):
        continue
    rows.append({
        "print_date": r.print_date,
        "target": r.next_quarter,
        "kappa": 100 * (post_c / guide - 1),
        "gap": 100 * (guide / pre_c - 1),
        "revision": 100 * (post_c / pre_c - 1),
    })
rev = pd.DataFrame(rows)
for start in ["1900", "2023", "2024"]:
    s = rev[rev.print_date >= start]
    show("Same-target revision regression " + start + "+", {
        "n": len(s),
        "mean_kappa": s.kappa.mean(),
        "slope": s.gap.cov(s.revision) / s.gap.var(),
        "correlation": s.gap.corr(s.revision),
    })

# F03: ledger "point=0" is not a numeric margin in the public sentence.
fy = g[
    g.print_quarter.str.startswith("4Q") &
    g.target_period.str.startswith("FY") &
    g.metric.str.startswith("adj_ebitda_margin") &
    g.print_quarter.map(qkey).ge(qkey("4Q21"))
].copy()
fy["numeric_in_quote"] = fy.quote.str.contains(
    r"\d+(?:\.\d+)?\s*%", regex=True
)
show("F03 February FY statements",
     fy[["print_quarter", "target_period", "quote", "numeric_in_quote"]])
show("F03 numeric/qualitative counts",
     fy.numeric_in_quote.value_counts().to_dict())
floors = fy[fy.numeric_in_quote &
            fy.guide_type.eq("floor")].copy()
floors["beat_bp"] = 100 * (floors.actual - floors.value_low)
show("F03 resolved February numeric floor beats",
     floors[["target_period", "value_low", "actual", "beat_bp"]])

# F04: recompute from GAAP expense less functional SBC.
annual = read(
    "data/processed/margin_build/02_financial_panel/02_panel_annual.csv"
)[["year", "revenue", "sm_gaap", "sbc_sm", "sm_cash"]].copy()
annual["share"] = 100 * (annual.sm_gaap - annual.sbc_sm) / annual.revenue
annual["change_pp"] = annual.share.diff()
show("F04 reported annual ex-SBC shares", annual)
for start in [2022, 2023, 2024]:
    s = annual[annual.year.between(start, 2025)]
    show(f"F04 observed >=0.6pp increases, {start}-2025", {
        "n": len(s), "hits": int((s.change_pp >= 0.6).sum()),
    })

quarterly = read(
    "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
)
for year in [2025, 2026]:
    h = quarterly[(quarterly.year == year) & quarterly.qn.le(2)]
    show(f"F04 H1 {year}", {
        "sm_cash": h.sm_cash.sum(), "revenue": h.revenue.sum(),
        "share": 100 * h.sm_cash.sum() / h.revenue.sum(),
    })

line = read("data/processed/margin_build/40_line_build/40_annual.csv")
b = line[(line.period == "FY27") & (line.scenario == "base")].iloc[0]
street = read(
    "data/processed/margin_build/23_final_model/23_vs_consensus.csv"
)
v = street[street.period == "FY27"].iloc[0]
other = b[["cor_cash", "ops_cash", "pd_cash", "ga_cash"]].sum()
raw = v.lseg_revenue_musd - v.lseg_ebitda_musd - other
corrected = raw + b.da
show("F04 Street residual accounting bridge", {
    "other_costs": other, "DA": b.da,
    "uncorrected_SM": raw,
    "uncorrected_share": 100 * raw / v.lseg_revenue_musd,
    "corrected_SM": corrected,
    "corrected_share": 100 * corrected / v.lseg_revenue_musd,
    "dispersion_tail_NOT_predictive": 1 - NormalDist(
        corrected, v.lseg_ebitda_sd_musd
    ).cdf(0.219 * v.lseg_revenue_musd),
})
show("F04 exact line-build base share", 100 * b.sm_cash / b.revenue)

# Published vector/coherence checks; these are not new simulations.
f3 = json.loads((
    QROOT / "fy27-margin-guide/forecasts/2026-09-17-forecast.json"
).read_text(encoding="utf-8"))
f4 = json.loads((
    QROOT / "fy27-sm-share-above-219/forecasts/2026-09-17-forecast.json"
).read_text(encoding="utf-8"))
weights = list(f3["final"]["vector"].values())
conditional = list(f4["conditionals"]["p_given_f03"].values())
show("Published F03 vector sum", sum(weights))
show("Published strict F03 vector sum",
     sum(f3["final"]["strict_convention_vector"].values()))
show("Published F03/F04 total probability",
     sum(w * c for w, c in zip(weights, conditional)))

saved = read(
    "docs/pitch-forecasts/questions/fy27-sm-share-above-219/"
    "datasets/f04_sensitivity.csv"
)
model_c = saved[saved["case"].str.startswith("F03")]["p_ge_21.9"]
show("Saved model conditional weighted probability (CSV rounded)",
     sum(w * c for w, c in zip(weights, model_c)))

# Inspect the actual saved API fields, not deprecated field names.
source = QROOT / "q1-27-nights-guide-above-82/sources"
for name in [
    "kalshi_KXABNBA_open_20260917T031845Z.json",
    "kalshi_KXABNB_open_20260917T031845Z.json",
]:
    markets = json.loads((source / name).read_text())["markets"]
    fields = [
        "ticker", "yes_bid_dollars", "yes_ask_dollars",
        "volume_fp", "volume_24h_fp", "open_interest_fp", "updated_time",
    ]
    show(name, pd.DataFrame([
        {field: market.get(field) for field in fields}
        for market in markets
    ]))
