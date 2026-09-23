"""
47_pitch_charts / prepare_data.py: assemble the datasets behind the thesis-3 chart candidates from committed outputs.

Run:  py -3.13 analysis/src/margin_build/47_pitch_charts/prepare_data.py   (exit 0; writes data/processed/margin_build/47_pitch_charts/)
Then: Rscript analysis/src/margin_build/47_pitch_charts/charts.R
Every number is read from a committed CSV (02 panel, 41, 42, 45, 46) or, for d08, the cached 2Q26 10-Q MD&A (quoted in 45).
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
MB = ROOT / "data/processed/margin_build"
OUT = MB / "47_pitch_charts"; OUT.mkdir(parents=True, exist_ok=True)
pan = pd.read_csv(MB / "02_financial_panel/02_panel_quarterly.csv").set_index("quarter")
pan["costs"] = pan.revenue - pan.adj_ebitda_reported
yq = lambda y: [f"{i}Q{y}" for i in range(1, 5)]
S = lambda qs, c: float(pan.loc[qs, c].sum())

# d01 margin bridges
pd.read_csv(MB / "46_margin_bridge/46_bridge.csv").to_csv(OUT / "d01_bridge.csv", index=False)

# d02 annual S&M vs revenue growth
rows = []
for lab, cur, prev in [("FY22", yq("22"), yq("21")), ("FY23", yq("23"), yq("22")), ("FY24", yq("24"), yq("23")), ("FY25", yq("25"), yq("24")),
                       ("1H26", ["1Q26", "2Q26"], ["1Q25", "2Q25"])]:
    rows.append(dict(period=lab, revenue_growth=(S(cur, "revenue") / S(prev, "revenue") - 1) * 100, sm_growth=(S(cur, "sm_cash") / S(prev, "sm_cash") - 1) * 100,
                     sm_share=S(cur, "sm_cash") / S(cur, "revenue") * 100,
                     incr_rev_per_incr_sm=(S(cur, "revenue") - S(prev, "revenue")) / (S(cur, "sm_cash") - S(prev, "sm_cash"))))
pd.DataFrame(rows).to_csv(OUT / "d02_sm_vs_revenue_annual.csv", index=False)

# d03 quarterly y/y growth
qs = [f"{q}Q{y}" for y in ("22", "23", "24", "25", "26") for q in "1234" if f"{q}Q{y}" in pan.index]
rows = []
for q in qs:
    p = f"{q[0]}Q{int(q[2:]) - 1}"
    if p in pan.index:
        rows.append(dict(quarter=q, order=len(rows), revenue_yoy=(pan.loc[q, "revenue"] / pan.loc[p, "revenue"] - 1) * 100,
                         sm_yoy=(pan.loc[q, "sm_cash"] / pan.loc[p, "sm_cash"] - 1) * 100))
pd.DataFrame(rows).to_csv(OUT / "d03_quarterly_growth.csv", index=False)

# d04 cost lines as % of revenue: FY22-FY25 actual; FY26E/FY27E line build on the official model's revenue
lb = pd.read_csv(MB / "40_line_build/40_lines_quarterly.csv"); lb = lb[lb.scenario == "base"].set_index("quarter")
meta = pd.read_csv(MB / "46_margin_bridge/46_bridge_meta.csv").set_index("period")
off_rev = {"FY26": 14117.72, "FY27": float(meta.loc["FY27", "our_revenue"])}
LN = {"sm_cash": "Sales & marketing", "cor_cash": "Cost of revenue", "pd_cash": "Product development", "ops_cash": "Ops & support", "ga_cash_ex_lodging": "G&A"}
rows = []
for y in ("22", "23", "24", "25"):
    rev = S(yq(y), "revenue")
    for c, n in LN.items(): rows.append(dict(period=f"FY{y}", line=n, pct=S(yq(y), c) / rev * 100, kind="actual"))
h1 = ["1Q26", "2Q26"]; h2 = ["3Q26", "4Q26"]; q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
for c, n in LN.items():
    lbc = "ga_cash" if c == "ga_cash_ex_lodging" else c
    rows.append(dict(period="FY26E", line=n, pct=(S(h1, c) + float(lb.loc[h2, lbc].sum())) / off_rev["FY26"] * 100, kind="ours"))
    rows.append(dict(period="FY27E", line=n, pct=float(lb.loc[q27, lbc].sum()) / off_rev["FY27"] * 100, kind="ours"))
pd.DataFrame(rows).to_csv(OUT / "d04_line_shares.csv", index=False)

# d05 annual cost growth: actual FY21-FY25, Street FY26-FY28, ours FY27, break-even FY27 on our revenue
ann = pd.read_csv(MB / "41_cost_leg/41_annual_cost_growth.csv")
be = pd.read_csv(MB / "45_ai_margin/45_breakeven.csv").set_index("revenue_path")
fy20, fy21 = S(yq("20"), "costs"), S(yq("21"), "costs")
rows = [dict(period="FY21", growth=(fy21 / fy20 - 1) * 100, kind="actual"), dict(period="FY22", growth=(S(yq("22"), "costs") / fy21 - 1) * 100, kind="actual")]
for _, r in ann[ann.source == "actual"].dropna(subset=["cost_growth_pct"]).iterrows():
    rows.append(dict(period=r.period, growth=r.cost_growth_pct, kind="actual"))
for _, r in ann[ann.source == "street_annual"].iterrows():
    rows.append(dict(period=r.period + "E", growth=r.cost_growth_pct, kind="street"))
rows.append(dict(period="FY27E", growth=float(ann[(ann.period == "FY27") & (ann.source == "line_build_base")].cost_growth_pct.iloc[0]), kind="ours"))
rows.append(dict(period="FY27E", growth=float(be.loc["official v2", "growth_to_hold_street_margin_pct"]), kind="breakeven"))
pd.DataFrame(rows).to_csv(OUT / "d05_cost_growth.csv", index=False)

# d06 break-even curves: FY27 margin vs FY27 cost growth on the Street's FY26 cost base
st26 = float(be.loc["official v2", "street_fy26_costs"])
street_rev, our_rev = 15819.34, float(be.loc["official v2", "fy27_revenue"])
rows = []
for g in [x / 10 for x in range(40, 161)]:
    c = st26 * (1 + g / 100)
    rows.append(dict(cost_growth=g, margin_street_rev=(street_rev - c) / street_rev * 100, margin_our_rev=(our_rev - c) / our_rev * 100))
pd.DataFrame(rows).to_csv(OUT / "d06_breakeven_curves.csv", index=False)
grid = pd.read_csv(MB / "45_ai_margin/45_fy27_grid.csv")
grid.to_csv(OUT / "d11_fy27_grid.csv", index=False)

# d07 cost surprise at print
cs = pd.read_csv(MB / "41_cost_leg/41_cost_surprise_history.csv")[["print_quarter", "cost_surprise", "cost_surprise_pct", "revenue_surprise", "ebitda_surprise"]]
cs.to_csv(OUT / "d07_cost_surprise.csv", index=False)

# d08 AI saving vs spending growth, 1H26 (2Q26 10-Q MD&A, six months; quoted in 45_ai_margin.md)
pd.DataFrame([
    dict(item="Third-party support costs (credited to AI)", usd_m=-15, group="ai"),
    dict(item="Server costs", usd_m=15, group="other"),
    dict(item="Ops & support payroll", usd_m=41, group="other"),
    dict(item="Product development payroll", usd_m=132, group="other"),
    dict(item="Sales & marketing", usd_m=372, group="sm"),
]).to_csv(OUT / "d08_ai_vs_spend.csv", index=False)

# d10 stock reaction vs forward EBITDA revision (W1 prints) + R1 fit
p42 = pd.read_csv(MB / "42_margin_reaction/42_panel.csv")
p42[p42.print_quarter >= "2023Q1"][["print_quarter", "reaction_date", "ntm_ebitda_rev_pct", "ntm_revenue_rev_pct", "ntm_margin_rev_pts", "excess_5d_pct", "excess_1d_pct"]].to_csv(OUT / "d10_reaction.csv", index=False)
reg = pd.read_csv(MB / "42_margin_reaction/42_regressions.csv")
reg[(reg.test == "R1") & reg.window.isin(["W1", "W2"])].to_csv(OUT / "d10_r1_fit.csv", index=False)

# d12 FY margin history and forecasts
hist = [dict(period=f"FY{y}", margin=S(yq(y), "adj_ebitda_reported") / S(yq(y), "revenue") * 100, series="Reported") for y in ("22", "23", "24", "25")]
hist += [dict(period="FY26E", margin=float(ann[(ann.period == "FY26") & (ann.source == "street_annual")].margin_pct.iloc[0]), series="Street"),
         dict(period="FY27E", margin=float(meta.loc["FY27", "street_margin"]), series="Street"),
         dict(period="FY26E", margin=float(ann[(ann.period == "FY26") & (ann.source == "official_v2")].margin_pct.iloc[0]), series="Ours"),
         dict(period="FY27E", margin=float(meta.loc["FY27", "our_margin"]), series="Ours")]
pd.DataFrame(hist).to_csv(OUT / "d12_margin_history.csv", index=False)

# d13 Q3 margin history
q3 = [dict(period=f"3Q{y}", margin=float(pan.loc[f"3Q{y}", "adj_ebitda_margin_pct"]), series="Reported") for y in ("22", "23", "24", "25")]
q3 += [dict(period="3Q26E", margin=float(meta.loc["3Q26", "street_margin"]), series="Street"), dict(period="3Q26E", margin=float(meta.loc["3Q26", "our_margin"]), series="Ours")]
pd.DataFrame(q3).to_csv(OUT / "d13_q3_margins.csv", index=False)
print("wrote", OUT, sorted(p.name for p in OUT.glob("*.csv")))
