"""
short_case_inputs.py: the two-pager's short-case inputs for Graph 2 (nights) and Graph 3 (margin bridges).

Run:  python analysis/src/pitch_charts/short_case_inputs.py   (exit 0; after prepare_data.py)
Writes data/processed/pitch_charts/n06_nights_short.csv and r06_margin_bridge_short.csv.

The pitch runs on the short case priced at $128 (krish/cost-leg, 48_short_case_v3: FY27 revenue $15,035M, adj. EBITDA $4,873M,
32.41%, 13.68x EV/EBITDA on the spot-anchored growth-linked multiple). Costs at management's budget, no Q4 marketing cut.
(28 Sep: first built on 44's $108 judgement path; switched to 48 the same day.)

Graph 3: a copy of margin_build/46_margin_bridge/run.py (krish/cost-leg 32ceee0e) with one change: "our" lines, D&A, bookings,
hosting, revenue and EBITDA come from 48's short-case quarterly lines instead of the 40 base line build. Street margin, the revenue
flex (k 0.364), the uniform-growth allocation of the Street's cost plan and the two splits are unchanged, except that the short
case's +4% RNPL ops uplift is booked in 'payroll, make-goods, insurance' rather than in AI support automation. The bridge sums exactly
to the short case's margin (asserted).

Graph 2: nights totals for 3Q26-4Q27 are 48's path = the team line + the bear RNPL cancellation tail (n01 with_tail_bear). Underlying,
bundle, World Cup and Middle East legs are n01's; the tail (n02 bear drag_pp) is its own negative component in forecast quarters.
No fitted parameters.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/pitch_charts"
CL = ROOT.parent / "marginaudit"                               # krish/cost-leg worktree (.worktrees/marginaudit)
MB = CL / "data/processed/margin_build"
K = 0.364
pan = pd.read_csv(MB / "02_financial_panel/02_panel_quarterly.csv").set_index("quarter")
sc = pd.read_csv(MB / "48_short_case_v3/40_short_case_quarterly.csv").set_index("quarter")
prm = pd.read_csv(MB / "40_line_build/40_params.csv").set_index("name")["base"]
cq = pd.read_csv(MB / "06_fy27_path_v2/06_consensus_quarterly_2027.csv").set_index("quarter")
price = pd.read_csv(MB / "48_short_case_v3/48_short_case_price.csv")
V, G_FIX = float(prm["ops_variable_share"]), float(prm["ops_fixed_growth"]) / 100
NPB = {"3Q25": 3.7, "4Q25": 3.7, "1Q26": 3.65, "2Q26": 3.65}
PREV = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}
Q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
LINES = ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]
assert float(sc.loc["4Q26", "lodging_reserves"]) == 0 and (sc.lodging_reserves == 0).all()

pr = price[(price.version == "v48") & price.convention.str.startswith("spot")].iloc[0]
assert abs(pr.price - 127.72) < 0.01 and abs(sc.loc[Q27, "adj_ebitda"].sum() - pr.fy27_ebitda) < 1e-6


def actual_lines(q):
    r = pan.loc[q]
    return dict(cor_cash=float(r.cor_cash), ops_cash=float(r.ops_cash), pd_cash=float(r.pd_cash), sm_cash=float(r.sm_cash), ga_cash=float(r.ga_cash_ex_lodging))
def sc_lines(q): return {c: float(sc.loc[q, c]) for c in LINES}
def bookings(q): return float(pan.loc[q, "nights_m"]) / NPB[q] if q in NPB else float(sc.loc[q, "bookings_m"])
def ops_prev(q): return float(pan.loc[q, "ops_cash"]) if q in NPB else float(sc.loc[q, "ops_cash"])
UPLIFT = 1.04                                                  # 44/48's RNPL overlay: +4% ops & support per booking (make-goods, refunds)
def ops_no_ai(q):
    """Ops & support in q with the support-cost-per-booking decline set to zero. The RNPL uplift stays in the counterfactual when
    the prior quarter is an actual (no uplift in it), so it lands in 'payroll, make-goods, insurance', not in AI support."""
    p = PREV[q]
    return ops_prev(p) * (V * float(sc.loc[q, "bookings_m"]) / bookings(p) + (1 - V) * (1 + G_FIX)) * (UPLIFT if p in NPB else 1.0)
HOST_BASE = {"3Q25": 224.0 / 4, "4Q25": 224.0 / 4, "1H26": 112.0 + 15.0}
LABEL = {"Street consensus": "Street consensus",
         "Revenue below the Street, costs flexing at the historical rate": "Lower revenue (costs flex down)",
         "Payments & other cost of revenue": "Payments & other cost of revenue",
         "Hosting & AI compute": "Hosting & AI compute",
         "Ops & support: AI support automation": "AI support automation",
         "Ops & support: payroll, make-goods, insurance": "Ops & support: payroll, other",
         "Product development": "Product development",
         "Sales & marketing": "Sales & marketing",
         "General & administrative": "G&A",
         "Our model (short case)": "Our model"}


def bridge(period):
    if period in ("3Q26", "4Q26"):
        base = actual_lines(PREV[period]); ours = sc_lines(period); da = float(sc.loc[period, "da"])
        host_b = HOST_BASE[PREV[period]]; host_o = float(sc.loc[period, "cor_hosting"]); ops_noai = ops_no_ai(period)
        st_rev, st_e = float(cq.loc[period, "revenue_mean_musd"]), float(cq.loc[period, "ebitda_mean_musd"])
        rev, e_ours = float(sc.loc[period, "revenue"]), float(sc.loc[period, "adj_ebitda"])
    else:
        base = {c: sum(actual_lines(q)[c] for q in ("1Q26", "2Q26")) + sum(sc_lines(q)[c] for q in ("3Q26", "4Q26")) for c in LINES}
        ours = {c: sum(sc_lines(q)[c] for q in Q27) for c in LINES}; da = float(sc.loc[Q27, "da"].sum())
        host_b = HOST_BASE["1H26"] + float(sc.loc[["3Q26", "4Q26"], "cor_hosting"].sum()); host_o = float(sc.loc[Q27, "cor_hosting"].sum())
        ops_noai = sum(ops_no_ai(q) for q in Q27)
        st_rev, st_e = float(cq.loc["FY27", "revenue_mean_musd"]), float(cq.loc["FY27", "ebitda_mean_musd"])
        rev, e_ours = float(sc.loc[Q27, "revenue"].sum()), float(sc.loc[Q27, "adj_ebitda"].sum())
    m_st = st_e / st_rev * 100
    gap = rev / st_rev - 1
    st_costs_flex = (st_rev - st_e) * (1 + K * gap)
    m_flex = (rev - st_costs_flex) / rev * 100
    T = st_costs_flex + da
    f = T / sum(base.values())
    cf = {c: base[c] * f for c in LINES}
    pp = lambda usd: -usd / rev * 100
    steps = [
        ("Street consensus", "total", m_st),
        ("Revenue below the Street, costs flexing at the historical rate", "step", m_flex - m_st),
        ("Payments & other cost of revenue", "step", pp((ours["cor_cash"] - host_o) - (cf["cor_cash"] - host_b * f))),
        ("Hosting & AI compute", "step", pp(host_o - host_b * f)),
        ("Ops & support: AI support automation", "step", pp(ours["ops_cash"] - ops_noai)),
        ("Ops & support: payroll, make-goods, insurance", "step", pp(ops_noai - cf["ops_cash"])),
        ("Product development", "step", pp(ours["pd_cash"] - cf["pd_cash"])),
        ("Sales & marketing", "step", pp(ours["sm_cash"] - cf["sm_cash"])),
        ("General & administrative", "step", pp(ours["ga_cash"] - cf["ga_cash"])),
    ]
    out, run = [], None
    for name, kind, v in steps:
        if kind == "total":
            run = v; out.append(dict(period=period, item=name, label=LABEL[name], kind=kind, value_pp=v, start=0.0, end=v))
        else:
            out.append(dict(period=period, item=name, label=LABEL[name], kind=kind, value_pp=v, start=run, end=run + v)); run += v
    m_ours = e_ours / rev * 100
    assert abs(run - m_ours) < 1e-6, (period, run, m_ours)
    out.append(dict(period=period, item="Our model (short case)", label="Our model", kind="total", value_pp=m_ours, start=0.0, end=m_ours))
    return out


br = pd.DataFrame([r for p in ("3Q26", "4Q26", "FY27") for r in bridge(p)])
br.to_csv(DATA / "r06_margin_bridge_short.csv", index=False)

nd = pd.read_csv(DATA / "n01_nights_decomposition.csv")
tail = pd.read_csv(DATA / "n02_cancellation_tail.csv").query("scenario == 'bear'").set_index("quarter")["drag_pp"]
fc = nd.kind == "forecast"
nd["cancel"] = np.where(fc, nd.quarter.map(tail), 0.0)
nd["total"] = np.where(fc, nd.total + nd.cancel, nd.total)
assert (nd.loc[fc, "total"] - nd.loc[fc, "with_tail_bear"]).abs().max() < 0.01
path48 = pd.read_csv(MB / "48_short_case_v3/40_short_case_revenue_path.csv").set_index("quarter")["nights_yoy_pct"]
assert (nd.loc[fc].set_index("quarter")["total"] - path48).abs().max() < 0.01          # the chart plots the path the price is built on
nd[["quarter", "kind", "total", "underlying", "bundle", "cancel", "wc", "me", "street"]].to_csv(DATA / "n06_nights_short.csv", index=False)

pd.set_option("display.width", 200)
print(br[br.kind == "total"][["period", "label", "value_pp"]].round(2).to_string(index=False))
print(nd.loc[fc, ["quarter", "total", "underlying", "bundle", "cancel", "wc", "me", "street"]].round(2).to_string(index=False))
