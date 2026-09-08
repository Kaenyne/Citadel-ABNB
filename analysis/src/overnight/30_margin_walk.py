"""
30. Quarterly margin walk and EPS proxy, 3Q26-4Q27, consuming the workstream-29 revenue bridge.

Adjusted EBITDA = revenue - cash cost lines (ex-SBC) + D&A + other add-backs. Each cash line is driven by its
natural unit, as in workstream 07 (annual): cost of revenue by GBV dollars, operations and support by nights,
the rest by cash growth against the same quarter a year earlier. Below EBITDA: SBC, D&A, interest income and
expense, tax, share count -> a GAAP EPS proxy (ABNB's published consensus EPS is GAAP).

Inputs: 07_cost_lines_per_night.csv (quarterly cash stack), 29_q4_2026_bridge.csv, 29_fy27_quarterly_path.csv,
29_fx_refresh.csv, 10_regional_forecast.csv. Street from 04_current_consensus.csv, comparison only.
Run: py -3.13 analysis/src/overnight/30_margin_walk.py
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
FIG = ROOT / "analysis" / "figures" / "overnight"
cl = pd.read_csv(OUT / "07_cost_lines_per_night.csv").set_index("quarter")
q4b = pd.read_csv(OUT / "29_q4_2026_bridge.csv")
ph = pd.read_csv(OUT / "29_fy27_quarterly_path.csv")
fx = pd.read_csv(OUT / "29_fx_refresh.csv")
reg = pd.read_csv(OUT / "10_regional_forecast.csv")
SCEN = ["bear", "base", "bull"]
PY = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}

def regt(period, s, col):
    return float(reg[(reg.period == period) & (reg.region == "TOTAL") & (reg.scenario == s)][col].iloc[0])

# ---------------------------------------------------------------- 1. revenue, nights, GBV by quarter and scenario (from 29 / 10)
top = {}
for s in SCEN:
    fxp = {"bear": "strong_usd", "base": "consensus", "bull": "weak_usd"}[s]
    fxq = lambda q: float(fx[(fx.path == fxp) & (fx.quarter == q)].revenue_fx_fit_pp.iloc[0])
    q3g = 15.51 + {"bear": -2.4, "base": 1.0, "bull": 4.9}[s]
    rows = {"3Q26": dict(nights_yoy=regt("3Q26", s, "nights_yoy_pct"), adr_exfx=regt("3Q26", s, "adr_exfx_yoy_pct"), fx_pp=3.0,
                         resid=q3g - 3.0 - regt("3Q26", s, "nights_yoy_pct") - regt("3Q26", s, "adr_exfx_yoy_pct"), rev_g=q3g),
            "4Q26": dict(nights_yoy=regt("4Q26", s, "nights_yoy_pct"), adr_exfx=regt("4Q26", s, "adr_exfx_yoy_pct"), fx_pp=fxq("2026Q4"),
                         resid={"bear": -2.0, "base": -0.51, "bull": 1.0}[s], rev_g=float(q4b[(q4b.scenario == s) & (q4b.kind == "end")].value_pp.iloc[0]))}
    for _, r in ph[ph.scenario == s].iterrows():
        q = f"{r.quarter[-1]}Q27"
        rows[q] = dict(nights_yoy=r.nights_yoy_pct, adr_exfx=r.adr_exfx_pct, fx_pp=r.fx_pp, resid=r.residual_pp, rev_g=r.reported_growth_pct)
    top[s] = rows

# ---------------------------------------------------------------- 2. cost levers (cash, y/y vs same quarter prior year); 07's annual set, phased
LEV = {  # (bear, base, bull); keys: "3Q26", "4Q26" (phased H2, 1H26 cash costs ran +16.3% / +14.7% y/y), "27" (FY27 quarters)
    "cor_per_gbv_chg":  {"3Q26": (4.0, 2.0, 0.0), "4Q26": (4.0, 2.0, 0.0), "27": (2.0, 1.0, -0.5)},      # % change in cash cost of revenue per $ GBV; AI hosting (+$15m 1H26, $1.7bn commitment)
    "ops_per_night_chg": {"3Q26": (-3.0, -5.0, -7.0), "4Q26": (-3.0, -5.0, -7.0), "27": (-3.0, -5.0, -6.0)},  # AI support: -3.8% realised 1H26, -16% per booking 2Q26
    "pd_cash_g":        {"3Q26": (12.5, 11.0, 10.0), "4Q26": (12.5, 11.0, 10.0), "27": (10.5, 10.0, 9.0)},
    "brand_g":          {"3Q26": (35.0, 28.0, 20.0), "4Q26": (25.0, 10.0, 5.0), "27": (14.0, 16.0, 12.0)},  # 1H26 +32%; Q3 "investment timing"; 4Q25 base $391m; H2 base ~+19%
    "field_g":          {"3Q26": (20.0, 14.0, 10.0), "4Q26": (15.0, 10.0, 6.0), "27": (10.0, 14.0, 12.0)},  # 1H26 +24%; 4Q25 base was +71% y/y
    "ga_cash_g":        {"3Q26": (5.0, 2.0, 0.0), "4Q26": (5.0, 2.0, 0.0), "27": (5.5, 5.5, 5.0)},
    "sbc_g":            {"3Q26": (16.0, 13.0, 10.0), "4Q26": (16.0, 13.0, 10.0), "27": (14.0, 10.0, 6.0)},
    "tax_rate":         {"3Q26": (20.0, 19.0, 18.0), "4Q26": (20.0, 19.0, 18.0), "27": (21.0, 20.0, 19.0)},
    "int_income_q":     {"3Q26": (160.0, 168.0, 175.0), "4Q26": (150.0, 162.0, 172.0), "27": (135.0, 155.0, 172.0)},  # $m/qtr; 1H26 $338m
    "int_expense_q":    {"3Q26": (31.0, 31.0, 31.0), "4Q26": (31.0, 31.0, 31.0), "27": (31.0, 31.0, 31.0)},        # $2.5bn notes at 4.4-5.25%
    "share_chg_q":      {"3Q26": (-0.8, -1.0, -1.2), "4Q26": (-0.8, -1.0, -1.2), "27": (-0.8, -1.0, -1.2)},        # % per quarter; $1.1bn/qtr buyback less RSU issuance
}
DA_Q = 20.0
def lev(name, q, s):
    return LEV[name][q if q.endswith("26") else "27"][SCEN.index(s)]

# ---------------------------------------------------------------- 3. build the quarterly P&L
pnl = []
hist_shares = {"2Q26": 597.0}
for s in SCEN:
    shares = hist_shares["2Q26"]
    built = {}
    for q in ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]:
        py = PY[q]
        base = cl.loc[py] if py in cl.index else built[py]      # 3Q27/4Q27 compare to our own 3Q26/4Q26
        t = top[s][q]
        rev = float(base["revenue_musd"]) * (1 + t["rev_g"] / 100)
        nights = float(base["nights_m"]) * (1 + t["nights_yoy"] / 100)
        gbv = float(base["gbv_musd"]) * (1 + (t["nights_yoy"] + t["adr_exfx"] + t["fx_pp"]) / 100)     # ADR reported ~ ex-FX + FX
        cor = float(base["cor_cash_per_100gbv"]) * (1 + lev("cor_per_gbv_chg", q, s) / 100) / 100 * gbv
        ops = float(base["ops_cash_per_night"]) * (1 + lev("ops_per_night_chg", q, s) / 100) * nights
        pdc = float(base["pd_cash_musd"]) * (1 + lev("pd_cash_g", q, s) / 100)
        brand = float(base["sm_brand_perf_musd"]) * (1 + lev("brand_g", q, s) / 100)
        # field ops cash = field ops GAAP less S&M SBC (07 convention); 4Q25 G&A carried an $83m item added back in adj EBITDA
        field_base = float(base["sm_field_ops_musd"]) - (float(base["sm_sbc_musd"]) if py in cl.index else 0.0)
        field = field_base * (1 + lev("field_g", q, s) / 100)
        ga_base = float(base["ga_cash_musd"]) - (float(base["other_addbacks_musd"]) if py in cl.index and py == "4Q25" else 0.0)
        ga = ga_base * (1 + lev("ga_cash_g", q, s) / 100)
        cash_cost = cor + ops + pdc + brand + field + ga
        ebitda = rev - cash_cost + DA_Q
        sbc = float(base["sbc_total_musd"]) * (1 + lev("sbc_g", q, s) / 100)
        op_inc = ebitda - DA_Q - sbc
        pretax = op_inc + lev("int_income_q", q, s) - lev("int_expense_q", q, s)
        ni = pretax * (1 - lev("tax_rate", q, s) / 100)
        shares = shares * (1 + lev("share_chg_q", q, s) / 100)
        row = dict(scenario=s, quarter=q, revenue_musd=rev, nights_m=nights, gbv_musd=gbv, rev_per_night=rev / nights,
                   cor_cash_musd=cor, ops_cash_musd=ops, pd_cash_musd=pdc, sm_brand_perf_musd=brand, sm_field_ops_musd=field, ga_cash_musd=ga,
                   total_cash_cost_musd=cash_cost, adj_ebitda_musd=ebitda, adj_ebitda_margin_pct=ebitda / rev * 100,
                   sbc_total_musd=sbc, operating_income_musd=op_inc, gaap_op_margin_pct=op_inc / rev * 100,
                   interest_income_musd=lev("int_income_q", q, s), interest_expense_musd=lev("int_expense_q", q, s),
                   tax_rate_pct=lev("tax_rate", q, s), net_income_musd=ni, diluted_shares_m=shares, eps_gaap_proxy=ni / shares,
                   cor_cash_per_100gbv=cor / gbv * 100, ops_cash_per_night=ops / nights, sm_brand_perf_per_night=brand / nights,
                   nights_yoy=t["nights_yoy"], adr_exfx=t["adr_exfx"], fx_pp=t["fx_pp"], resid_pp=t["resid"], rev_yoy=t["rev_g"],
                   py_margin_pct=float(base["adj_ebitda_margin_pct"]) if py in cl.index else built[py]["adj_ebitda_margin_pct"],
                   brand_yoy=lev("brand_g", q, s), sm_sbc_musd=float(base["sm_sbc_musd"]) if py in cl.index else built[py]["sm_sbc_musd"],
                   other_addbacks_musd=0.0)
        built[q] = row
        pnl.append(row)
pnl = pd.DataFrame(pnl)
pnl.round(2).to_csv(OUT / "30_quarterly_pnl.csv", index=False)

# ---------------------------------------------------------------- 4. FY summaries vs Street
h1 = cl.loc[["1Q26", "2Q26"]]
h1_rev, h1_ebitda = h1.revenue_musd.sum(), h1.adj_ebitda_musd.sum()
h1_ni = 816.0 + 0.0  # placeholder replaced below from XBRL-derived net income in cost lines? not carried; use letters: 1Q26 -? -> use op income proxy
# GAAP net income 1H26 from letters: Q1 2026 and Q2 2026 (2Q26 letter: $816m Q2). Q1 2026 net income $154m (1Q26 letter).
h1_ni = 160.0 + 816.0
h1_eps = 160.0 / 608.0 + 816.0 / 597.0   # 1Q26 and 2Q26 GAAP net income (02 panel), diluted WA shares
fy = []
street = {"FY26": dict(rev=(14100, 14160), eps=(5.23, 5.28), ebitda_margin_floor=35.5), "FY27": dict(rev=(15730, 15760), eps=(6.02, 6.14))}
for s in SCEN:
    p = pnl[pnl.scenario == s].set_index("quarter")
    fy26_rev = h1_rev + p.loc[["3Q26", "4Q26"], "revenue_musd"].sum()
    fy26_ebitda = h1_ebitda + p.loc[["3Q26", "4Q26"], "adj_ebitda_musd"].sum()
    fy26_eps = h1_eps + p.loc[["3Q26", "4Q26"], "eps_gaap_proxy"].sum()
    fy27_rev = p.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "revenue_musd"].sum()
    fy27_ebitda = p.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "adj_ebitda_musd"].sum()
    fy27_eps = p.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "eps_gaap_proxy"].sum()
    fy.append(dict(scenario=s, fy26_revenue_musd=fy26_rev, fy26_adj_ebitda_musd=fy26_ebitda, fy26_margin_pct=fy26_ebitda / fy26_rev * 100,
                   fy26_vs_floor_pts=fy26_ebitda / fy26_rev * 100 - 35.5, fy26_eps_gaap_proxy=fy26_eps, fy26_street_eps="5.23-5.28",
                   q3_margin_pct=p.loc["3Q26", "adj_ebitda_margin_pct"], q4_margin_pct=p.loc["4Q26", "adj_ebitda_margin_pct"],
                   q3_eps=p.loc["3Q26", "eps_gaap_proxy"], q3_street_eps=2.87, q4_eps=p.loc["4Q26", "eps_gaap_proxy"], q4_street_eps=0.82,
                   fy27_revenue_musd=fy27_rev, fy27_adj_ebitda_musd=fy27_ebitda, fy27_margin_pct=fy27_ebitda / fy27_rev * 100,
                   fy27_margin_chg_pts=fy27_ebitda / fy27_rev * 100 - fy26_ebitda / fy26_rev * 100, fy27_eps_gaap_proxy=fy27_eps, fy27_street_eps="6.02-6.14",
                   h1_27_margin_pct=p.loc[["1Q27", "2Q27"], "adj_ebitda_musd"].sum() / p.loc[["1Q27", "2Q27"], "revenue_musd"].sum() * 100,
                   h1_26_margin_pct=h1_ebitda / h1_rev * 100))
fy = pd.DataFrame(fy)
fy.round(2).to_csv(OUT / "30_fy_summary.csv", index=False)

# ---------------------------------------------------------------- 5. the margin walk, 4Q25 -> 4Q26 and FY26 -> FY27 (base), in margin points
LINES = [("cor_cash_musd", "Cost of revenue"), ("ops_cash_musd", "Ops & support"), ("pd_cash_musd", "Product dev (cash)"),
         ("sm_brand_perf_musd", "Brand & perf marketing"), ("sm_field_ops_musd", "Field ops & policy (cash)"), ("ga_cash_musd", "G&A (cash)")]
def walk(prior: dict, now: dict, label_from: str, label_to: str, s: str, wname: str = "") -> list[dict]:
    """Split each line's change in share of revenue into a unit-cost effect (cost per night moved) and a revenue-per-night effect."""
    rp0, rp1 = prior["rev_per_night"], now["rev_per_night"]
    rows = [dict(scenario=s, walk=wname, order=0, term=label_from, value_pts=prior["margin"], kind="start")]
    lev_total = 0.0
    unit = []
    for col, name in LINES:
        c0, c1 = prior[col] / prior["nights"], now[col] / now["nights"]
        lev_total += c0 / rp0 - c0 / rp1                  # leverage: same unit cost over a higher revenue per night
        unit.append((name, -(c1 - c0) / rp1 * 100))        # unit-cost effect
    # split the revenue-per-night leverage across ADR ex-FX, FX and residual by their share of the rev/night change
    parts = {"ADR ex-FX": now["adr_exfx"], "FX": now["fx_pp"], "Take-rate / timing": now["resid"]}
    tot = sum(parts.values()) or 1.0
    o = 1
    for k, v in parts.items():
        rows.append(dict(scenario=s, walk=wname, order=o, term=f"Revenue per night: {k}", value_pts=lev_total * 100 * v / tot, kind="step")); o += 1
    for name, v in unit:
        rows.append(dict(scenario=s, walk=wname, order=o, term=f"{name} per night", value_pts=v, kind="step")); o += 1
    da = (now["da"] / now["revenue"] - prior["da"] / prior["revenue"]) * 100
    rows.append(dict(scenario=s, walk=wname, order=o, term="D&A and add-backs", value_pts=da, kind="step")); o += 1
    rows.append(dict(scenario=s, walk=wname, order=o, term=label_to, value_pts=now["margin"], kind="end"))
    chk = rows[0]["value_pts"] + sum(r["value_pts"] for r in rows if r["kind"] == "step")
    assert abs(chk - now["margin"]) < 0.05, (label_to, chk, now["margin"])
    return rows

def pack_hist(q):
    r = cl.loc[q]
    d = {c: float(r[c]) for c, _ in LINES}
    d["sm_field_ops_musd"] = float(r["sm_field_ops_musd"]) - float(r["sm_sbc_musd"])
    d["ga_cash_musd"] = float(r["ga_cash_musd"]) - (float(r["other_addbacks_musd"]) if q == "4Q25" else 0.0)
    d.update(nights=float(r["nights_m"]), revenue=float(r["revenue_musd"]), rev_per_night=float(r["revenue_musd"]) / float(r["nights_m"]),
             margin=float(r["adj_ebitda_margin_pct"]), da=float(r["da_musd"]) + (float(r["other_addbacks_musd"]) if q != "4Q25" else 0.0),
             adr_exfx=np.nan, fx_pp=np.nan, resid=np.nan)
    return d
def pack_now(s, q):
    r = pnl[(pnl.scenario == s) & (pnl.quarter == q)].iloc[0]
    d = {c: float(r[c]) for c, _ in LINES}
    d.update(nights=float(r.nights_m), revenue=float(r.revenue_musd), rev_per_night=float(r.rev_per_night), margin=float(r.adj_ebitda_margin_pct),
             da=DA_Q, adr_exfx=float(r.adr_exfx), fx_pp=float(r.fx_pp), resid=float(r.resid_pp))
    return d

walks = []
for s in SCEN:
    walks += walk(pack_hist("4Q25"), pack_now(s, "4Q26"), "4Q25 adj. EBITDA margin", "4Q26 adj. EBITDA margin", s, "q4")
    # FY: aggregate quarters into one 'quarter' for the same decomposition
    def agg(qs, hist_qs):
        out = {c: 0.0 for c, _ in LINES}; n = rv = da = 0.0; ax = fxp = rs = 0.0
        for q in qs:
            d = pack_now(s, q); w = d["revenue"]
            for c, _ in LINES: out[c] += d[c]
            n += d["nights"]; rv += d["revenue"]; da += d["da"]; ax += d["adr_exfx"] * w; fxp += d["fx_pp"] * w; rs += d["resid"] * w
        for q in hist_qs:
            d = pack_hist(q)
            for c, _ in LINES: out[c] += d[c]
            n += d["nights"]; rv += d["revenue"]; da += d["da"]
        out.update(nights=n, revenue=rv, rev_per_night=rv / n, margin=(rv - sum(out[c] for c, _ in LINES) + da) / rv * 100, da=da,
                   adr_exfx=ax / max(rv, 1), fx_pp=fxp / max(rv, 1), resid=rs / max(rv, 1))
        return out
    fy26 = agg(["3Q26", "4Q26"], ["1Q26", "2Q26"])
    fy27 = agg(["1Q27", "2Q27", "3Q27", "4Q27"], [])
    # for the FY walk the revenue-per-night split uses FY27's own terms
    walks += walk(fy26, fy27, "FY26 adj. EBITDA margin", "FY27 adj. EBITDA margin", s, "fy")
wk = pd.DataFrame(walks)
wk.round(2).to_csv(OUT / "30_margin_walk.csv", index=False)

# ---------------------------------------------------------------- 6. management-language forecast for 5 Nov and Feb, from the base case and the 02 ledger rules
b = fy[fy.scenario == "base"].iloc[0]
lang = [
    ("5 Nov", "FY26 adj. EBITDA margin", f"floor replaced by a point: 'approximately {round(b.fy26_margin_pct * 2) / 2:.1f}%'", "Pattern: FY floor becomes a point at the Q3 print in 2024 and 2025; base FY26 lands %.1f%%" % b.fy26_margin_pct, 0.70),
    ("5 Nov", "4Q26 adj. EBITDA margin", "'up year-over-year' vs 28.3%" if b.q4_margin_pct > 28.3 + 0.5 else "'roughly flat to slightly up year-over-year'", f"base 4Q26 {b.q4_margin_pct:.1f}% vs 28.3%; bear {fy[fy.scenario=='bear'].q4_margin_pct.iloc[0]:.1f}%, bull {fy[fy.scenario=='bull'].q4_margin_pct.iloc[0]:.1f}%", 0.60),
    ("5 Nov", "4Q26 revenue", "midpoint implying +11-13% with an FX sentence ('modest FX headwind after hedging')", "29 bridge base +12.0%; Q3 letter quantified FX, Q1 letter did, Q4 letter did", 0.55),
    ("5 Nov", "S&M commentary", "'marketing to grow faster than revenue in Q4' reiterated, softer than 1H", f"base H2 brand +18% vs 1H +32%; floor only breached above ~+29%", 0.65),
    ("5 Nov", "2027 margin", "no number; 'opportunity for further expansion' language only", "no 2027 guide has ever been given before February", 0.75),
    ("Feb 2027", "FY27 adj. EBITDA margin", f"floor 'at least {np.floor(b.fy27_margin_pct * 2) / 2 - 0.5:.1f}%'" if True else "", f"base FY27 {b.fy27_margin_pct:.1f}%; floors have been set 60-140bps below the eventual print", 0.55),
    ("Feb 2027", "FY27 revenue growth", "'low double digits' with FX quantified as a headwind", "29 bridge base +11.6%, 1H27 ~+10%", 0.55),
    ("Feb 2027", "1Q27 revenue guide", "midpoint implying +9-11%, 'approximately one point FX headwind'", "29 phasing 1Q27 +9.9%, FX -1.0pp on the consensus path", 0.50),
]
pd.DataFrame(lang, columns=["print", "item", "forecast_language", "basis", "probability"]).to_csv(OUT / "30_mgmt_language.csv", index=False)

# assumptions table
arows = [(k, f'3Q26 {v["3Q26"]} / 4Q26 {v["4Q26"]}', v["27"], "bear / base / bull") for k, v in LEV.items()]
arows += [("D&A per quarter, $m", DA_Q, DA_Q, "FY23-25 ~0.7% of revenue; 2Q26 $17m"),
          ("4Q25 G&A base", "cash $340m less $83m add-back", "", "other add-backs in the 4Q25 adj. EBITDA reconciliation sit in G&A"),
          ("Field ops cash", "GAAP field ops less all S&M SBC", "", "07 convention: no SBC inside brand & performance"),
          ("1H26 actuals", f"revenue {h1_rev:.0f}, adj. EBITDA {h1_ebitda:.0f}, GAAP EPS {h1_eps:.2f}", "", "letters; Q1 NI $160m / 608m sh, Q2 $816m / 597m sh"),
          ("Top line", "workstream 29 bridge by scenario", "", "29_q4_2026_bridge.csv, 29_fy27_quarterly_path.csv; GBV y/y = nights + ADR ex-FX + FX")]
pd.DataFrame(arows, columns=["item", "h2_2026", "fy2027", "source"]).to_csv(OUT / "30_margin_assumptions.csv", index=False)

# ---------------------------------------------------------------- 7. figure: base-case walks
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
POS, NEG, TOT = "#2a78d6", "#e34948", "#898781"
def wf(ax, df, title, ylo):
    vals, kinds, run = df.value_pts.tolist(), df.kind.tolist(), 0.0
    for i, (v, k) in enumerate(zip(vals, kinds)):
        if k in ("start", "end"):
            bottom, height, color, run = ylo, v - ylo, TOT, v
        else:
            bottom, height = (run, v) if v >= 0 else (run + v, -v); color = POS if v >= 0 else NEG; run += v
        ax.bar(i, height, bottom=bottom, width=0.62, color=color, edgecolor=SURF, linewidth=1.5, zorder=3)
        ax.text(i, bottom + height + 0.15, f"{v:+.1f}" if k == "step" else f"{v:.1f}%", ha="center", va="bottom", fontsize=8.5, color=INK, zorder=4)
        if k != "end":
            ax.plot([i + 0.31, i + 0.69], [run, run], color=MUTED, linewidth=0.8, linestyle=(0, (2, 2)), zorder=2)
    short = {"ADR ex-FX": "ADR\nex-FX", "FX": "FX", "Take-rate / timing": "Take-rate/\ntiming", "Cost of revenue": "Cost of\nrevenue", "Ops & support": "Ops &\nsupport", "Product dev (cash)": "Product\ndev", "Brand & perf marketing": "Brand\nmarketing", "Field ops & policy (cash)": "Field\nops", "G&A (cash)": "G&A", "D&A and add-backs": "D&A"}
    labels = [short.get(t.replace("Revenue per night: ", "").replace(" per night", ""), t.split(" adj.")[0]) for t in df.term]
    ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels, fontsize=7.5, color=INK2, rotation=0)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10); ax.set_ylabel("adj. EBITDA margin, %", fontsize=9, color=INK2)
    ax.set_ylim(ylo, max(vals[0], vals[-1]) + 4); ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0); ax.set_axisbelow(True)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7"); ax.tick_params(axis="y", colors=MUTED, labelsize=8.5, length=0); ax.tick_params(axis="x", length=0); ax.set_facecolor(SURF)
fig, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor=SURF)
wf(axes[0], wk[(wk.scenario == "base") & (wk.walk == "q4")], "4Q25 to 4Q26 base: adjusted EBITDA margin by lever", 20)
wf(axes[1], wk[(wk.scenario == "base") & (wk.walk == "fy")], "FY26 base to FY27 base: adjusted EBITDA margin by lever", 30)
fig.legend(handles=[Patch(color=NEG, label="reduces margin"), Patch(color=POS, label="adds to margin"), Patch(color=TOT, label="level")], loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.035))
fig.text(0.01, 0.002, "Cash cost lines ex-SBC, each per night; revenue-per-night leverage split by the workstream-29 terms. Field ops = GAAP less S&M SBC; 4Q25 G&A ex the $83m add-back. Base case.", fontsize=7.5, color=MUTED)
plt.tight_layout(rect=(0, 0.09, 1, 1)); FIG.mkdir(exist_ok=True, parents=True); fig.savefig(FIG / "30_margin_walk.png", dpi=160, facecolor=SURF)

pd.set_option("display.width", 220)
print(pnl[["scenario", "quarter", "revenue_musd", "adj_ebitda_musd", "adj_ebitda_margin_pct", "py_margin_pct", "sm_brand_perf_musd", "eps_gaap_proxy"]].round(2).to_string(index=False))
print(fy.round(2).T.to_string())
print(wk[wk.scenario == "base"].round(2).to_string(index=False))
