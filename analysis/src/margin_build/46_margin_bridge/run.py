"""
46_margin_bridge: adjusted EBITDA margin bridge from the Street to the team's official model, for 3Q26, 4Q26 and FY27.

Run:  py -3.13 analysis/src/margin_build/46_margin_bridge/run.py   (exit 0; writes data/processed/margin_build/46_margin_bridge/)

Steps, in order:
  1. Street margin (LSEG, 11 Sep 2026: quarterly means for 3Q26/4Q26, the annual n-44 mean for FY27).
  2. Revenue: our revenue (official model v2, DEC-0018) with the Street's total costs flexed at the measured elasticity (k 0.364, M6),
     i.e. costs come down with revenue at the historical rate. This is operating deleverage, independent of any cost view.
  3. Cost lines: our lines (the 40_line_build base cost dollars the official model plugs, DEC-0022/0042) against the Street's flexed
     cost plan. No vendor publishes Street cost lines, so the Street plan is allocated to lines at one uniform growth rate on the
     prior-year base (3Q25/4Q25 actuals for the quarters; FY26 = 1H26 actual + 2H26 line build for FY27). Each line's step is how much
     our line differs from growing at the Street's average rate. Cost of revenue is split into hosting & AI compute vs payments & other;
     ops & support into AI support automation (the build's support-cost-per-booking decline in the period) vs payroll & other.
  4. Our margin (equals the official income statement: 49.17% / 27.43% / 33.97%).
Cash lines are GAAP less SBC and include D&A; the Street's flexed cash costs add back our D&A, so the steps sum exactly. No fitted
parameters. Hosting base: 3Q25/4Q25 at the line build's $224M/yr run-rate; 1H26 at $112M + $15M (2Q26 10-Q six-month server-cost
increase) - both estimates, flagged.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[4]
MB = ROOT / "data/processed/margin_build"
OUT = MB / "46_margin_bridge"; OUT.mkdir(parents=True, exist_ok=True)
K = 0.364
pan = pd.read_csv(MB / "02_financial_panel/02_panel_quarterly.csv").set_index("quarter")
lb = pd.read_csv(MB / "40_line_build/40_lines_quarterly.csv"); lb = lb[lb.scenario == "base"].set_index("quarter")
prm = pd.read_csv(MB / "40_line_build/40_params.csv").set_index("name")["base"]
cq = pd.read_csv(MB / "06_fy27_path_v2/06_consensus_quarterly_2027.csv").set_index("quarter")
V, G_FIX = float(prm["ops_variable_share"]), float(prm["ops_fixed_growth"]) / 100
NPB = {"3Q25": 3.7, "4Q25": 3.7, "1Q26": 3.65, "2Q26": 3.65}
PREV = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}
Q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
LINES = ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]

ws = load_workbook(ROOT / "model/ABNB_official_model_complete.xlsx", read_only=True, data_only=True)["Income_Statement"]
rows = {r: [ws.cell(r, c).value for c in range(1, 30)] for r in range(1, 40)}
col = {h[:4]: i for i, h in enumerate(rows[4]) if isinstance(h, str) and h.endswith("E")}
lab = {str(v[0]).strip(): r for r, v in rows.items() if v[0]}
r_rev = next(r for k, r in lab.items() if k.startswith("Revenue")); r_e = next(r for k, r in lab.items() if k.startswith("Adjusted EBITDA") and "margin" not in k.lower())
OFF = {q: dict(rev=float(rows[r_rev][i]), ebitda=float(rows[r_e][i])) for q, i in col.items()}

def actual_lines(q):
    r = pan.loc[q]
    return dict(cor_cash=float(r.cor_cash), ops_cash=float(r.ops_cash), pd_cash=float(r.pd_cash), sm_cash=float(r.sm_cash), ga_cash=float(r.ga_cash_ex_lodging))
def lb_lines(q): return {c: float(lb.loc[q, c]) for c in LINES}
def bookings(q): return float(pan.loc[q, "nights_m"]) / NPB[q] if q in NPB else float(lb.loc[q, "bookings_m"])
def ops_prev(q): return float(pan.loc[q, "ops_cash"]) if q in NPB else float(lb.loc[q, "ops_cash"])
def ops_no_ai(q):
    """Ops & support in quarter q with the period's support-cost-per-booking decline set to zero (prior quarter as built)."""
    p = PREV[q]
    return ops_prev(p) * (V * float(lb.loc[q, "bookings_m"]) / bookings(p) + (1 - V) * (1 + G_FIX))
HOST_BASE = {"3Q25": 224.0 / 4, "4Q25": 224.0 / 4, "1H26": 112.0 + 15.0}

def bridge(period):
    if period in ("3Q26", "4Q26"):
        base = actual_lines(PREV[period]); ours = lb_lines(period); da = float(lb.loc[period, "da"])
        host_b = HOST_BASE[PREV[period]]; host_o = float(lb.loc[period, "cor_hosting"])
        ops_noai = ops_no_ai(period)
        st_rev, st_e = float(cq.loc[period, "revenue_mean_musd"]), float(cq.loc[period, "ebitda_mean_musd"])
        rev, e_off = OFF[period]["rev"], OFF[period]["ebitda"]
    else:
        base = {c: sum(actual_lines(q)[c] for q in ("1Q26", "2Q26")) + sum(lb_lines(q)[c] for q in ("3Q26", "4Q26")) for c in LINES}
        ours = {c: sum(lb_lines(q)[c] for q in Q27) for c in LINES}; da = float(lb.loc[Q27, "da"].sum())
        host_b = HOST_BASE["1H26"] + float(lb.loc[["3Q26", "4Q26"], "cor_hosting"].sum()); host_o = float(lb.loc[Q27, "cor_hosting"].sum())
        ops_noai = sum(ops_no_ai(q) for q in Q27)
        st_rev, st_e = float(cq.loc["FY27", "revenue_mean_musd"]), float(cq.loc["FY27", "ebitda_mean_musd"])
        rev, e_off = sum(OFF[q]["rev"] for q in Q27), sum(OFF[q]["ebitda"] for q in Q27)
    m_st = st_e / st_rev * 100
    gap = rev / st_rev - 1
    st_costs_flex = (st_rev - st_e) * (1 + K * gap)                  # EBITDA-cost basis
    m_flex = (rev - st_costs_flex) / rev * 100
    T = st_costs_flex + da                                            # cash-line basis (lines include D&A)
    f = T / sum(base.values())
    cf = {c: base[c] * f for c in LINES}
    pp = lambda usd: -usd / rev * 100                                  # cost above the counterfactual cuts margin
    steps = [
        ("Street consensus", "total", m_st, None),
        ("Revenue below the Street, costs flexing at the historical rate", "step", m_flex - m_st, (rev - st_rev)),
        ("Payments & other cost of revenue", "step", pp((ours["cor_cash"] - host_o) - (cf["cor_cash"] - host_b * f)), (ours["cor_cash"] - host_o) - (cf["cor_cash"] - host_b * f)),
        ("Hosting & AI compute", "step", pp(host_o - host_b * f), host_o - host_b * f),
        ("Ops & support: AI support automation", "step", pp(ours["ops_cash"] - ops_noai), ours["ops_cash"] - ops_noai),
        ("Ops & support: payroll, make-goods, insurance", "step", pp(ops_noai - cf["ops_cash"]), ops_noai - cf["ops_cash"]),
        ("Product development", "step", pp(ours["pd_cash"] - cf["pd_cash"]), ours["pd_cash"] - cf["pd_cash"]),
        ("Sales & marketing", "step", pp(ours["sm_cash"] - cf["sm_cash"]), ours["sm_cash"] - cf["sm_cash"]),
        ("General & administrative", "step", pp(ours["ga_cash"] - cf["ga_cash"]), ours["ga_cash"] - cf["ga_cash"]),
    ]
    out, run = [], None
    for name, kind, v, usd in steps:
        if kind == "total":
            run = v; out.append(dict(period=period, item=name, kind=kind, value_pp=v, start=0.0, end=v, ebitda_impact_musd=np.nan))
        else:
            impact = ((rev - st_costs_flex) - st_e) if name.startswith("Revenue") else -usd     # EBITDA impact vs the Street, $M
            out.append(dict(period=period, item=name, kind=kind, value_pp=v, start=run, end=run + v, ebitda_impact_musd=impact)); run += v
    m_ours = e_off / rev * 100
    assert abs(run - m_ours) < 1e-6, (period, run, m_ours)
    out.append(dict(period=period, item="Our model (official income statement)", kind="total", value_pp=m_ours, start=0.0, end=m_ours, ebitda_impact_musd=np.nan))
    meta = dict(period=period, street_revenue=st_rev, street_ebitda=st_e, street_margin=m_st, our_revenue=rev, our_ebitda=e_off, our_margin=m_ours,
                revenue_gap_pct=gap * 100, street_costs_flexed=st_costs_flex, margin_after_revenue=m_flex, street_cost_growth_uniform_pct=(f - 1) * 100,
                ours_cash_costs=sum(ours.values()), street_flexed_cash_costs=T, ebitda_gap=e_off - st_e)
    return out, meta

allrows, metas = [], []
for p in ("3Q26", "4Q26", "FY27"):
    r, m = bridge(p); allrows += r; metas.append(m)
    assert abs(sum(x["ebitda_impact_musd"] for x in r if x["kind"] == "step") - m["ebitda_gap"]) < 1e-6
df = pd.DataFrame(allrows); df.to_csv(OUT / "46_bridge.csv", index=False)
meta = pd.DataFrame(metas); meta.to_csv(OUT / "46_bridge_meta.csv", index=False)
(OUT / "46_bridge.json").write_text(json.dumps(dict(steps=df.round(4).replace({np.nan: None}).to_dict("records"), meta=meta.round(4).to_dict("records")), indent=1), encoding="utf-8")
pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 70)
print(df.round(3).to_string(index=False)); print(meta.round(2).T.to_string())
