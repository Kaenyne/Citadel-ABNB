"""
caimanes_inputs.py: two-pager chart inputs taken from the team model, model/Caimanes_Citadel_ABNB_Model_v2.xlsx.

Run:  py -3.13 analysis/src/pitch_charts/caimanes_inputs.py   (exit 0; needs openpyxl; after prepare_data.py)
Writes data/processed/pitch_charts/n07_nights_caimanes.csv and r07_margin_bridge_caimanes.csv.

Graph 2 (nights). Totals, Street nights and the event terms come from the workbook (Income_Statement row 4-5; Nights_Engine section F:
underlying, fee/cancellation lap, ex-NA RNPL lap, events; rows 87-88 Street). The workbook states the bundle as laps against an
underlying that still contains it; the chart keeps the team's leg split (n01: bundle, World Cup, Middle East) so history and forecast
read the same way, and underlying = workbook total - bundle - World Cup - Middle East. Events agree with n01 (Middle East +1.0 in 1Q27,
World Cup -0.5 in 2Q27; asserted). v2 carries RNPL cancellations in the base print (Nights_Engine row 91); the chart shows them as their own part; v1 has none.

Graph 3 (margin bridge, Street to our model; 3Q26, 4Q26, FY27). Method of margin_build/46_margin_bridge (krish/cost-leg 32ceee0e):
Street margin, then our revenue with the Street's costs flexed at k 0.364, then each cost line against the Street's flexed cost plan
spread at one growth rate on the prior-year base. Every "ours" number and the Street numbers are the workbook's: cash cost lines
(rows 15-19), D&A (22), hosting & AI compute (132), revenue and adjusted EBITDA (11, 23), Street revenue and adj. EBITDA (38, 40,
LSEG 13 Sep 2026; FY27 = sum of the four quarters). Prior-year base = the workbook's actual quarters; hosting base = 46's estimates.
Ops & support splits as in 46: "AI support automation" = the workbook's cut in support cost per booking (rows 62-63, -14% 2H26,
-10% FY27, applied to the variable share in row 137), i.e. ops variable - ops variable / (1 + cut); the rest of ops against the
Street plan is "payroll, other". No fitted parameters.
"""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/pitch_charts"
# The team model, committed at model/ (v2, 28 Sep: 3Q26 nights 9.2% all-in and RNPL cancellations in the base print).
XL = ROOT / "model" / os.environ.get("CAIMANES_XL", "Caimanes_Citadel_ABNB_Model_v2.xlsx")
K = 0.364
HOST_BASE = {"3Q25": 224.0 / 4, "4Q25": 224.0 / 4, "1H26": 112.0 + 15.0}

wb = load_workbook(XL, data_only=True)
IS, NE = wb["Income_Statement"], wb["Nights_Engine"]

def row_by_quarter(ws, hdr_row, r):
    hdr = [c.value for c in ws[hdr_row]]; vals = [c.value for c in ws[r]]
    return {str(h).rstrip("AE"): v for h, v in zip(hdr, vals) if isinstance(h, str) and h[:1].isdigit() and "Q" in h and v is not None}
def find(ws, label, start=1):
    for r in range(start, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if isinstance(v, str) and v.strip().startswith(label.strip()): return r
    raise KeyError(label)

H = find(IS, "Quarter")
isr = lambda label, start=1: row_by_quarter(IS, H, find(IS, label, start))
rev, ebitda, da = isr("Revenue"), isr("Adjusted EBITDA"), isr("Depreciation & amortisation")
lines = {"cor_cash": isr("Cost of revenue (cash)"), "ops_cash": isr("Operations & support (cash)"), "pd_cash": isr("Product development (cash)"),
         "sm_cash": isr("Sales & marketing (cash)"), "ga_cash": isr("General & administrative (cash")}
st_rev, st_e = isr("Street revenue"), isr("Street adj. EBITDA")
nights = isr("Nights & seats booked")
# forward cost-line block (rows 127+): labels are indented, quarters in the same columns as the header
CL = find(IS, "Cost lines by quarter")
host = row_by_quarter(IS, H, find(IS, "    CoR: hosting & AI compute", CL))
ops_var = row_by_quarter(IS, H, find(IS, "    ops variable (support cost per booking)", CL))
param = lambda label: float(IS.cell(find(IS, label), 2).value)
CUT = {q: param("Ops variable cost per booking y/y, " + ("2H26" if q.endswith("26") else "FY27")) / 100 for q in ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]}
ai_saving = {q: ops_var[q] - ops_var[q] / (1 + CUT[q]) for q in CUT}          # negative $: support cost the AI cut removes
Q_F = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]; Q27 = Q_F[2:]
PREV = {"3Q26": "3Q25", "4Q26": "4Q25"}
LINES = list(lines)
for q in Q_F:                                                            # the workbook's own identity (lodging reserves 0 forward)
    assert abs(rev[q] - sum(lines[c][q] for c in LINES) + da[q] - ebitda[q]) < 1e-6, q

def bridge(period):
    if period in PREV:
        p = PREV[period]; qs = [period]
        base = {c: lines[c][p] for c in LINES}; host_b = HOST_BASE[p]
    else:
        qs = Q27
        base = {c: sum(lines[c][q] for q in ("1Q26", "2Q26", "3Q26", "4Q26")) for c in LINES}
        host_b = HOST_BASE["1H26"] + host["3Q26"] + host["4Q26"]
    ours = {c: sum(lines[c][q] for q in qs) for c in LINES}; d = sum(da[q] for q in qs); host_o = sum(host[q] for q in qs)
    r_o, e_o = sum(rev[q] for q in qs), sum(ebitda[q] for q in qs)
    r_s, e_s = sum(st_rev[q] for q in qs), sum(st_e[q] for q in qs)
    m_st = e_s / r_s * 100; gap = r_o / r_s - 1
    st_costs_flex = (r_s - e_s) * (1 + K * gap); m_flex = (r_o - st_costs_flex) / r_o * 100
    f = (st_costs_flex + d) / sum(base.values()); cf = {c: base[c] * f for c in LINES}
    pp = lambda usd: -usd / r_o * 100
    steps = [("Street consensus", "total", m_st),
             ("Lower revenue (costs flex down)", "step", m_flex - m_st),
             ("Payments & other cost of revenue", "step", pp((ours["cor_cash"] - host_o) - (cf["cor_cash"] - host_b * f))),
             ("Hosting & AI compute", "step", pp(host_o - host_b * f)),
             ("AI support automation", "step", pp(sum(ai_saving[q] for q in qs))),
             ("Ops & support: payroll, other", "step", pp(ours["ops_cash"] - sum(ai_saving[q] for q in qs) - cf["ops_cash"])),
             ("Product development", "step", pp(ours["pd_cash"] - cf["pd_cash"])),
             ("Sales & marketing", "step", pp(ours["sm_cash"] - cf["sm_cash"])),
             ("G&A", "step", pp(ours["ga_cash"] - cf["ga_cash"]))]
    out, run = [], None
    for name, kind, v in steps:
        if kind == "total": run = v; out.append(dict(period=period, label=name, kind=kind, value_pp=v, start=0.0, end=v))
        else: out.append(dict(period=period, label=name, kind=kind, value_pp=v, start=run, end=run + v)); run += v
    m_o = e_o / r_o * 100
    assert abs(run - m_o) < 1e-6, (period, run, m_o)
    out.append(dict(period=period, label="Our model", kind="total", value_pp=m_o, start=0.0, end=m_o))
    return out, dict(period=period, street_revenue=r_s, street_ebitda=e_s, street_margin=m_st, our_revenue=r_o, our_ebitda=e_o, our_margin=m_o)

rows, meta = [], []
for p in ("3Q26", "4Q26", "FY27"):
    r, m = bridge(p); rows += r; meta.append(m)
pd.DataFrame(rows).to_csv(DATA / "r07_margin_bridge_caimanes.csv", index=False)
pd.DataFrame(meta).to_csv(DATA / "r07_margin_bridge_caimanes_meta.csv", index=False)

# ---- nights -----------------------------------------------------------------------------------------------------------
HN = find(NE, "Quarter")
ner = lambda label: row_by_quarter(NE, HN, find(NE, label))
ev = ner("  events (pp)"); st_n = ner("  Street consensus nights (m)")
try: canc = ner("  RNPL cancellations (pp)")                               # v2 row 91; absent in v1
except KeyError: canc = {}
nd = pd.read_csv(DATA / "n01_nights_decomposition.csv")
nd["total"] = [ (nights[q] / nights[f"{q[:2]}{int(q[2:]) - 1}"] - 1) * 100 for q in nd.quarter ]
for q in Q_F:
    wc_me = float(nd.loc[nd.quarter == q, "wc"].iloc[0] + nd.loc[nd.quarter == q, "me"].iloc[0])
    assert abs(ev.get(q, 0.0) - wc_me) < 1e-9, (q, ev.get(q), wc_me)
nd["street"] = [ (st_n[q] / nights[f"{q[:2]}{int(q[2:]) - 1}"] - 1) * 100 if q in st_n else np.nan for q in nd.quarter ]
nd["cancel"] = [float(canc.get(q, 0.0)) if k == "forecast" else 0.0 for q, k in zip(nd.quarter, nd.kind)]
nd["underlying"] = nd.total - nd.bundle - nd.wc - nd.me - nd.cancel
nd[["quarter", "kind", "total", "underlying", "bundle", "cancel", "wc", "me", "street"]].to_csv(DATA / "n07_nights_caimanes.csv", index=False)

pd.set_option("display.width", 200)
print(pd.DataFrame(meta).round(2).to_string(index=False))
print(pd.DataFrame(rows).pivot_table(index="label", columns="period", values="value_pp", sort=False).round(2))
print(nd[nd.kind == "forecast"][["quarter", "total", "underlying", "bundle", "wc", "me", "street"]].round(2).to_string(index=False))
