"""ABNB driver model: revenue decomposition, reaction-function regression, scenarios and valuation lenses.

Built 2026-09-05 on top of the margin-drivers branch (cost stack, FY26/FY27 margin scenarios, capital-return
panel) and Theo's guidance dataset. Everything the Street argues about (pitch landscape note, section 3) is a
multiple applied to a consensual ~10-12% growth path, so this model keeps the growth path explicit (nights x ADR
x take rate) and shows the same cash flow through every lens the pitches use, plus what the price already implies.

Inputs (data/processed/):
  abnb_quarterly_kpis_from_study.csv        nights, GBV, ADR, revenue, Adj. EBITDA, take rate, 1Q21-2Q26
  abnb_quarterly_costlines.csv              GAAP cost lines and SBC (margin-drivers branch)
  abnb_capital_return_quarterly.csv         SBC, buybacks, FCF, diluted shares (margin-drivers branch)
  abnb_margin_scenarios.csv                 Bear/Base/Bull FY2026E-FY2027E revenue and Adj. EBITDA (margin-drivers)
  abnb_revenue_guidance_vs_actual.csv       next-quarter revenue guide vs actual, Q4 2021 to Q3 2026
  abnb_earnings_reactions.csv               1/5/20-day ABNB, QQQ and excess returns per print
  theos-past-research/.../quarterly_actuals.csv   reported vs constant-currency revenue growth (FX split)
  abnb_daily_close.csv                      last close

Outputs (data/processed/ and analysis/figures/):
  abnb_driver_history_quarterly.csv   quarterly drivers with y/y growth, FX, SBC, FCF, shares
  abnb_revenue_decomposition.csv      y/y revenue growth split into nights, ADR ex-FX, FX, take rate (log-additive)
  abnb_reaction_regression.csv        OLS of day-1 and day-5 excess return on beat, guide acceleration, margin
  abnb_reaction_inputs.csv            per-print regressors
  abnb_valuation_scenarios.csv        FY2026E-FY2028E P&L to FCF per share, bear/base/bull, and prices per lens
  abnb_valuation_sensitivity.csv      FY2027E price grid: EV/EBITDA multiple x scenario, margin x nights growth
  abnb_reverse_dcf.csv                growth the current price implies at several WACC / terminal assumptions
Run: py -3.13 analysis/src/abnb_driver_model.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data/processed"
FIG = ROOT / "analysis/figures"
THEO = ROOT / "theos-past-research/research/guidance/data/normalized"

# ------------------------------------------------------------------------------------------- balance sheet, 30 Jun 2026
# SEC XBRL company facts (CIK 1559720), 10-Q for the quarter ended 2026-06-30. Funds held for clients ($12.2B) are
# excluded from corporate cash: they are guest prepayments matched by a liability (the "guest float" debate).
BS = dict(cash_musd=6821.0, short_term_investments_musd=5248.0, debt_musd=2500.0, funds_held_for_clients_musd=12224.0,
          diluted_shares_m=597.0, as_of="2026-06-30")
# Q3 2026 guide (6 Aug 2026 letter): revenue $4.69B to $4.77B, nights "low double digits", FY margin "at least 35.5%"
Q3_GUIDE_MID = 4730.0


def qkey(q):
    """'1Q21' -> (2021, 1); '2021Q1' -> (2021, 1)."""
    q = str(q).strip()
    if len(q) == 4 and q[1] == "Q":          # 1Q21
        return 2000 + int(q[2:4]), int(q[0])
    return int(q[:4]), int(q[-1])            # 2021Q1


def qlabel(y, n):
    return f"{n}Q{str(y)[2:]}"


# ------------------------------------------------------------------------------------------- 1. history
def history():
    k = pd.read_csv(PROC / "abnb_quarterly_kpis_from_study.csv")
    c = pd.read_csv(PROC / "abnb_quarterly_costlines.csv")
    cr = pd.read_csv(PROC / "abnb_capital_return_quarterly.csv")
    a = pd.read_csv(THEO / "quarterly_actuals.csv")[["fiscal_period", "yoy_growth_reported", "yoy_growth_constant_currency"]]
    a["quarter"] = [qlabel(*qkey(p)) for p in a.fiscal_period]
    k, c, cr, a = (df.drop_duplicates("quarter") for df in (k, c, cr, a))
    h = k.merge(c[["quarter", "stock_based_comp_total_musd", "sales_and_marketing_musd", "product_development_musd", "operations_and_support_musd", "cost_of_revenue_musd", "general_and_administrative_musd"]], on="quarter", how="left")
    h = h.merge(cr[["quarter", "buybacks_musd", "rsu_tax_withholding_musd", "fcf_musd", "diluted_wa_shares_m"]], on="quarter", how="left")
    h = h.merge(a[["quarter", "yoy_growth_reported", "yoy_growth_constant_currency"]], on="quarter", how="left")
    h["year"], h["q"] = zip(*h.quarter.map(qkey))
    h = h.sort_values(["year", "q"]).reset_index(drop=True)
    h["gbv_musd"] = h.gbv_b * 1000
    h["take_rate_calc_pct"] = h.revenue_musd / h.gbv_musd * 100
    h["adj_ebitda_margin_pct"] = h.adj_ebitda_musd / h.revenue_musd * 100
    h["sbc_pct_rev"] = h.stock_based_comp_total_musd / h.revenue_musd * 100
    h["fcf_margin_pct"] = h.fcf_musd / h.revenue_musd * 100
    h["sbc_adj_fcf_musd"] = h.fcf_musd - h.stock_based_comp_total_musd
    for col in ("nights_m", "gbv_musd", "adr", "revenue_musd", "adj_ebitda_musd", "take_rate_calc_pct", "diluted_wa_shares_m", "fcf_musd"):
        h[col + "_yoy_pct"] = (h[col] / h[col].shift(4) - 1) * 100
    h["fx_pts"] = (h.yoy_growth_reported - h.yoy_growth_constant_currency) * 100  # reported minus constant-currency revenue growth
    # trailing four quarters
    for col in ("revenue_musd", "adj_ebitda_musd", "fcf_musd", "stock_based_comp_total_musd", "nights_m", "gbv_musd"):
        h[col + "_ltm"] = h[col].rolling(4).sum()
    return h


def decomposition(h):
    """log(1+g_rev) = log(1+g_nights) + log(1+g_adr) + log(1+g_takerate); ADR then split into ex-FX and FX using the
    reported-vs-constant-currency revenue growth gap (all FX assumed to sit in ADR)."""
    d = h[["quarter", "revenue_musd_yoy_pct", "nights_m_yoy_pct", "adr_yoy_pct", "take_rate_calc_pct_yoy_pct", "fx_pts"]].dropna(subset=["revenue_musd_yoy_pct"]).copy()
    for src, dst in (("nights_m_yoy_pct", "nights"), ("adr_yoy_pct", "adr"), ("take_rate_calc_pct_yoy_pct", "take_rate")):
        d[dst + "_log"] = np.log1p(d[src] / 100)
    d["rev_log"] = np.log1p(d.revenue_musd_yoy_pct / 100)
    d["resid_log"] = d.rev_log - d[["nights_log", "adr_log", "take_rate_log"]].sum(axis=1)
    tot = d.rev_log.replace(0, np.nan)
    # contributions in percentage points of reported y/y growth, allocated proportionally to log shares
    for part in ("nights", "adr", "take_rate", "resid"):
        d[part + "_pts"] = d[part + "_log"] / tot * d.revenue_musd_yoy_pct
    d["fx_pts"] = d.fx_pts.fillna(0)
    d["adr_exfx_pts"] = d.adr_pts - d.fx_pts
    out = d[["quarter", "revenue_musd_yoy_pct", "nights_pts", "adr_exfx_pts", "fx_pts", "take_rate_pts", "resid_pts"]].round(2)
    out.columns = ["quarter", "revenue_yoy_pct", "nights_pts", "adr_exfx_pts", "fx_pts", "take_rate_pts", "residual_pts"]
    return out


# ------------------------------------------------------------------------------------------- 2. reaction function
def reaction(h):
    g = pd.read_csv(PROC / "abnb_revenue_guidance_vs_actual.csv")
    r = pd.read_csv(PROC / "abnb_earnings_reactions.csv")
    hh = h.set_index("quarter")
    rows = []
    for _, x in g.iterrows():
        if pd.isna(x.actual_musd):
            continue
        y, n = qkey(x.guided_quarter)
        qg = qlabel(y, n)                     # the quarter that was guided and then reported
        py_q = qlabel(y - 1, n)               # same quarter a year earlier
        # the print at which qg's actual was reported is the call for period qg; the next-quarter guide given on that
        # call is the row whose issued_on_call == guided_quarter
        nxt = g[g.issued_on_call == x.guided_quarter]
        if nxt.empty or qg not in hh.index or py_q not in hh.index:
            continue
        nq = nxt.iloc[0]
        ny, nn = qkey(nq.guided_quarter)
        nq_py = qlabel(ny - 1, nn)
        guide_growth = (nq.guide_mid_musd / hh.loc[nq_py, "revenue_musd"] - 1) * 100 if nq_py in hh.index else np.nan
        rep = r[r.quarter == f"{y}Q{n}"]
        if rep.empty:
            continue
        rep = rep.iloc[0]
        rows.append(dict(print_quarter=qg, reaction_date=rep.reaction_date,
                         beat_vs_mid_pct=x.actual_vs_mid_pct, beat_vs_high_pct=x.actual_vs_high_pct,
                         revenue_yoy_pct=hh.loc[qg, "revenue_musd_yoy_pct"], nights_yoy_pct=hh.loc[qg, "nights_m_yoy_pct"],
                         next_q_guide_growth_pct=guide_growth, guide_accel_pts=guide_growth - hh.loc[qg, "revenue_musd_yoy_pct"],
                         margin_yoy_pts=hh.loc[qg, "adj_ebitda_margin_pct"] - hh.loc[py_q, "adj_ebitda_margin_pct"],
                         take_rate_yoy_pts=hh.loc[qg, "take_rate_calc_pct"] - hh.loc[py_q, "take_rate_calc_pct"],
                         excess_1d_pct=rep.excess_1d_pct, excess_5d_pct=rep.excess_5d_pct, excess_20d_pct=rep.excess_20d_pct, abnb_1d_pct=rep.abnb_1d_pct))
    inp = pd.DataFrame(rows)
    for c in inp.columns:
        if c not in ("print_quarter", "reaction_date"):
            inp[c] = pd.to_numeric(inp[c], errors="coerce")
    res = []
    specs = {"beat_only": ["beat_vs_mid_pct"], "guide_only": ["guide_accel_pts"],
             "beat_guide": ["beat_vs_mid_pct", "guide_accel_pts"],
             "beat_guide_margin": ["beat_vs_mid_pct", "guide_accel_pts", "margin_yoy_pts"],
             "beat_guide_nights": ["beat_vs_mid_pct", "guide_accel_pts", "nights_yoy_pct"]}
    for dep in ("excess_1d_pct", "excess_5d_pct"):
        for name, xs in specs.items():
            d = inp.dropna(subset=xs + [dep])
            X = sm.add_constant(d[xs]); m = sm.OLS(d[dep], X).fit(cov_type="HC1")
            row = dict(dependent=dep, spec=name, n=int(m.nobs), r2=m.rsquared, adj_r2=m.rsquared_adj, const=m.params["const"])
            for v in xs:
                row[f"b_{v}"] = m.params[v]; row[f"t_{v}"] = m.tvalues[v]; row[f"p_{v}"] = m.pvalues[v]
            res.append(row)
    # leave-one-out on the main spec: does Q2 2026 (+17%) drive it?
    xs = ["beat_vs_mid_pct", "guide_accel_pts"]
    d = inp.dropna(subset=xs + ["excess_1d_pct"])
    loo = []
    for i in d.index:
        dd = d.drop(i); m = sm.OLS(dd.excess_1d_pct, sm.add_constant(dd[xs])).fit()
        loo.append(dict(dropped=d.loc[i, "print_quarter"], b_beat=m.params["beat_vs_mid_pct"], b_guide=m.params["guide_accel_pts"], r2=m.rsquared))
    return inp, pd.DataFrame(res), pd.DataFrame(loo)


# ------------------------------------------------------------------------------------------- 3. scenarios and valuation
# Operating cases FY2026E-FY2027E come from the margin-drivers branch (abnb_margin_scenarios.csv). FY2028E extends
# them with the same logic. Cash conversion, SBC and buybacks are this model's assumptions (see model/assumptions.md).
SCEN = {
    "Bear": dict(fy28_rev_growth=6.0, fy28_margin=33.5, sbc_pct_rev=14.0, fcf_conv=0.92, buyback_musd=3000, ev_ebitda=18.0, ev_fcf=15.0, p_sbc_adj_fcf=20.0, pe=20.0),
    "Base": dict(fy28_rev_growth=11.0, fy28_margin=37.0, sbc_pct_rev=13.0, fcf_conv=1.00, buyback_musd=4000, ev_ebitda=22.0, ev_fcf=19.0, p_sbc_adj_fcf=26.0, pe=26.0),
    "Bull": dict(fy28_rev_growth=14.0, fy28_margin=40.5, sbc_pct_rev=12.0, fcf_conv=1.05, buyback_musd=4500, ev_ebitda=25.5, ev_fcf=23.0, p_sbc_adj_fcf=32.0, pe=32.0),
}
DA_PCT_REV, CAPEX_PCT_REV, TAX_RATE, INT_YIELD, DEBT_COST = 0.7, 0.3, 21.0, 3.5, 5.0  # D&A, capex % revenue; tax on GAAP-ish pre-tax; yield on cash and float; coupon on the 2026 notes


def scenarios(h, price):
    ms = pd.read_csv(PROC / "abnb_margin_scenarios.csv")
    ms = ms[ms.period.isin(["FY2026E", "FY2027E"])]
    ltm = h.iloc[-1]
    shares0 = BS["diluted_shares_m"]
    net_cash0 = BS["cash_musd"] + BS["short_term_investments_musd"] - BS["debt_musd"]
    rows = []
    for scen, p in SCEN.items():
        m = ms[ms.scenario == scen].set_index("period")
        rev = {"FY2026E": m.loc["FY2026E", "revenue_musd"], "FY2027E": m.loc["FY2027E", "revenue_musd"]}
        rev["FY2028E"] = rev["FY2027E"] * (1 + p["fy28_rev_growth"] / 100)
        marg = {"FY2026E": m.loc["FY2026E", "adj_ebitda_margin_pct"], "FY2027E": m.loc["FY2027E", "adj_ebitda_margin_pct"], "FY2028E": p["fy28_margin"]}
        shares, net_cash = shares0, net_cash0
        for fy in ("FY2026E", "FY2027E", "FY2028E"):
            r = rev[fy]; ebitda = r * marg[fy] / 100; sbc = r * p["sbc_pct_rev"] / 100
            fcf = ebitda * p["fcf_conv"]; sbc_adj_fcf = fcf - sbc
            da = r * DA_PCT_REV / 100
            # interest is earned on corporate cash AND the guest float (FY2025 interest income was about $0.8B);
            # the float scales with GBV, approximated here as growing with revenue
            float_ = BS["funds_held_for_clients_musd"] * r / 13159.0
            interest = (net_cash + BS["debt_musd"] + float_) * INT_YIELD / 100 - BS["debt_musd"] * DEBT_COST / 100
            ni = (ebitda - sbc - da + interest) * (1 - TAX_RATE / 100)   # GAAP-ish net income proxy
            bb = p["buyback_musd"] if fy != "FY2026E" else 2139 + p["buyback_musd"] / 2  # H1 2026 actual $2.14B plus half a year
            # shares: buybacks retire bb / price; SBC issues roughly sbc / price (RSUs at market); withholding nets some
            avg_price = price if fy == "FY2026E" else price * (1 + 0.05 * (["FY2026E", "FY2027E", "FY2028E"].index(fy)))
            shares = shares - bb / avg_price * 1000 / 1000 + sbc / avg_price * 0.65   # 35% of RSU value withheld for tax (historical ~0.35)
            net_cash = net_cash + fcf - bb
            eps = ni / shares; fcf_ps = fcf / shares; sbc_adj_fcf_ps = sbc_adj_fcf / shares
            rows.append(dict(scenario=scen, period=fy, revenue_musd=r, rev_growth_pct=(r / (rev.get(prev_fy(fy)) if prev_fy(fy) in rev else ltm.revenue_musd_ltm) - 1) * 100 if fy != "FY2026E" else m.loc["FY2026E", "rev_growth_pct"],
                             adj_ebitda_musd=ebitda, adj_ebitda_margin_pct=marg[fy], sbc_musd=sbc, sbc_pct_rev=p["sbc_pct_rev"], fcf_musd=fcf, fcf_margin_pct=fcf / r * 100,
                             sbc_adj_fcf_musd=sbc_adj_fcf, net_income_proxy_musd=ni, buybacks_musd=bb, diluted_shares_m=shares, net_cash_musd=net_cash,
                             eps_proxy=eps, fcf_per_share=fcf_ps, sbc_adj_fcf_per_share=sbc_adj_fcf_ps,
                             price_ev_ebitda=(ebitda * p["ev_ebitda"] + net_cash) / shares, ev_ebitda_x=p["ev_ebitda"],
                             price_ev_fcf=(fcf * p["ev_fcf"] + net_cash) / shares, ev_fcf_x=p["ev_fcf"],
                             price_p_sbc_adj_fcf=sbc_adj_fcf_ps * p["p_sbc_adj_fcf"], p_sbc_adj_fcf_x=p["p_sbc_adj_fcf"],
                             price_pe=eps * p["pe"], pe_x=p["pe"]))
    s = pd.DataFrame(rows)
    return s


def prev_fy(fy):
    return {"FY2027E": "FY2026E", "FY2028E": "FY2027E"}.get(fy)


def sensitivity(s, h, price):
    """FY2027E price grids: (a) EV/EBITDA multiple x scenario; (b) FY27 margin x FY27 revenue growth at the base multiple."""
    rows = []
    for scen in SCEN:
        r = s[(s.scenario == scen) & (s.period == "FY2027E")].iloc[0]
        for mult in (16, 18, 20, 22, 24, 25.5, 28):
            rows.append(dict(grid="ev_ebitda_x_scenario", scenario=scen, ev_ebitda_x=mult, price=(r.adj_ebitda_musd * mult + r.net_cash_musd) / r.diluted_shares_m))
    base = s[(s.scenario == "Base") & (s.period == "FY2027E")].iloc[0]
    fy26 = s[(s.scenario == "Base") & (s.period == "FY2026E")].iloc[0]
    for g in (4, 8, 10, 12, 14, 16):
        for mg in (33, 35, 36.5, 38, 40):
            rev = fy26.revenue_musd * (1 + g / 100); ebitda = rev * mg / 100
            rows.append(dict(grid="fy27_growth_x_margin_base_multiple", scenario="Base", rev_growth_pct=g, margin_pct=mg,
                             price=(ebitda * SCEN["Base"]["ev_ebitda"] + base.net_cash_musd) / base.diluted_shares_m))
    return pd.DataFrame(rows)


def reverse_dcf(h, price, years=10):
    """Constant growth g1 for `years` years then terminal growth, on LTM FCF (and SBC-adjusted FCF), that equates PV to
    the current EV. Solved by bisection."""
    ltm = h.iloc[-1]
    ev = price * BS["diluted_shares_m"] - (BS["cash_musd"] + BS["short_term_investments_musd"] - BS["debt_musd"])
    rows = []
    for label, base in (("fcf_ltm", ltm.fcf_musd_ltm), ("sbc_adjusted_fcf_ltm", ltm.fcf_musd_ltm - ltm.stock_based_comp_total_musd_ltm)):
        for wacc in (9.0, 10.0, 11.0):
            for tg in (2.5, 3.0, 4.0):
                def pv(g1):
                    v, f = 0.0, base
                    for t in range(1, years + 1):
                        f *= 1 + g1 / 100; v += f / (1 + wacc / 100) ** t
                    return v + f * (1 + tg / 100) / (wacc / 100 - tg / 100) / (1 + wacc / 100) ** years
                lo, hi = -20.0, 60.0
                for _ in range(80):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if pv(mid) < ev else (lo, mid)
                rows.append(dict(cash_flow=label, base_musd=base, ev_musd=ev, wacc_pct=wacc, terminal_growth_pct=tg, years=years, implied_growth_pct=mid))
    return pd.DataFrame(rows)


def multiples_today(h, price):
    ltm = h.iloc[-1]
    mcap = price * BS["diluted_shares_m"]
    net_cash = BS["cash_musd"] + BS["short_term_investments_musd"] - BS["debt_musd"]
    ev = mcap - net_cash
    sbc_adj = ltm.fcf_musd_ltm - ltm.stock_based_comp_total_musd_ltm
    return dict(price=price, diluted_shares_m=BS["diluted_shares_m"], market_cap_musd=mcap, net_cash_ex_float_musd=net_cash, funds_held_for_clients_musd=BS["funds_held_for_clients_musd"], ev_musd=ev,
                ltm_revenue_musd=ltm.revenue_musd_ltm, ltm_adj_ebitda_musd=ltm.adj_ebitda_musd_ltm, ltm_fcf_musd=ltm.fcf_musd_ltm, ltm_sbc_musd=ltm.stock_based_comp_total_musd_ltm, ltm_sbc_adj_fcf_musd=sbc_adj,
                ev_ltm_ebitda_x=ev / ltm.adj_ebitda_musd_ltm, ev_ltm_fcf_x=ev / ltm.fcf_musd_ltm, p_ltm_fcf_x=mcap / ltm.fcf_musd_ltm, fcf_yield_pct=ltm.fcf_musd_ltm / mcap * 100,
                sbc_adj_fcf_yield_pct=sbc_adj / mcap * 100, p_sbc_adj_fcf_x=mcap / sbc_adj, ev_ltm_revenue_x=ev / ltm.revenue_musd_ltm)


# ------------------------------------------------------------------------------------------- figures
def figures(dec, inp, s, sens, price):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    foot = "Sources: shareholder letters (KPIs), SEC XBRL (costs, cash flow), Theo's guidance dataset (FX split, guides); Citadel-ABNB driver model"
    # 1. decomposition stacked bars
    d = dec[dec.quarter.map(lambda q: qkey(q)[0]) >= 2023]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(d)); bottom_pos = np.zeros(len(d)); bottom_neg = np.zeros(len(d))
    for col, lab, colr in (("nights_pts", "Nights", "#4C72B0"), ("adr_exfx_pts", "ADR ex-FX", "#55A868"), ("fx_pts", "FX", "#C44E52"), ("take_rate_pts", "Take rate (incl. timing)", "#DD8452"), ("residual_pts", "Residual", "#999999")):
        v = d[col].values; pos = np.where(v > 0, v, 0); neg = np.where(v < 0, v, 0)
        ax.bar(x, pos, bottom=bottom_pos, color=colr, label=lab, width=0.7); ax.bar(x, neg, bottom=bottom_neg, color=colr, width=0.7)
        bottom_pos += pos; bottom_neg += neg
    ax.plot(x, d.revenue_yoy_pct, "k_", ms=18, mew=2, label="Revenue y/y")
    ax.set_xticks(x); ax.set_xticklabels(d.quarter); ax.axhline(0, color="grey", lw=0.8)
    ax.set_title("Revenue growth decomposition: nights x ADR (ex-FX, FX) x take rate, y/y percentage points", loc="left", fontweight="bold", fontsize=11)
    ax.set_ylabel("pts of y/y revenue growth"); ax.legend(ncol=6, fontsize=8, frameon=False); ax.grid(alpha=0.3, axis="y")
    fig.text(0.01, 0.005, foot, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "abnb_revenue_decomposition.png", dpi=150); plt.close(fig)
    # 2. reaction scatter
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, xcol, lab in ((axes[0], "beat_vs_mid_pct", "Revenue beat vs guide midpoint, %"), (axes[1], "guide_accel_pts", "Next-quarter guide growth minus reported growth, pts")):
        ax.scatter(inp[xcol], inp.excess_1d_pct, color="#4C72B0")
        for _, r in inp.iterrows():
            ax.annotate(r.print_quarter, (r[xcol], r.excess_1d_pct), fontsize=7, xytext=(3, 3), textcoords="offset points")
        m = np.polyfit(inp[xcol].dropna(), inp.loc[inp[xcol].notna(), "excess_1d_pct"], 1); xx = np.linspace(inp[xcol].min(), inp[xcol].max(), 10)
        ax.plot(xx, np.polyval(m, xx), color="#DD8452", lw=1.2); ax.axhline(0, color="grey", lw=0.8); ax.set_xlabel(lab); ax.set_ylabel("Day-1 excess return vs QQQ, %"); ax.grid(alpha=0.3)
    fig.suptitle(f"Reaction function: what the day-one move responds to ({len(inp)} guided prints, {inp.print_quarter.iloc[0]} to {inp.print_quarter.iloc[-1]})", x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.text(0.01, 0.005, foot, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "abnb_reaction_function.png", dpi=150); plt.close(fig)
    # 3. football field FY2027E
    f = s[s.period == "FY2027E"].set_index("scenario")
    lenses = [("price_ev_ebitda", "EV / FY27E Adj. EBITDA"), ("price_ev_fcf", "EV / FY27E FCF"), ("price_p_sbc_adj_fcf", "P / FY27E SBC-adjusted FCF"), ("price_pe", "P / FY27E earnings proxy")]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for i, (col, lab) in enumerate(lenses):
        lo, base, hi = f.loc["Bear", col], f.loc["Base", col], f.loc["Bull", col]
        ax.barh(i, hi - lo, left=lo, color="#4C72B0", alpha=0.35, height=0.5); ax.plot([base], [i], "o", color="#4C72B0")
        ax.text(hi + 2, i, f"{lo:.0f} / {base:.0f} / {hi:.0f}", va="center", fontsize=8)
    ax.axvline(price, color="#C44E52", lw=1.2, ls="--"); ax.text(price + 1, -0.45, f"last {price:.0f}", color="#C44E52", fontsize=8)
    ax.set_yticks(range(len(lenses))); ax.set_yticklabels([l for _, l in lenses]); ax.set_xlabel("implied price, USD (bear / base / bull scenario and multiple)")
    ax.set_title("Valuation lenses the pitches use, applied to the FY2027E bear, base and bull cases", loc="left", fontweight="bold", fontsize=11); ax.grid(alpha=0.3, axis="x")
    fig.text(0.01, 0.005, foot, fontsize=7, color="grey"); fig.tight_layout(); fig.savefig(FIG / "abnb_football_field.png", dpi=150); plt.close(fig)


def main():
    price = float(pd.read_csv(PROC / "abnb_daily_close.csv").iloc[-1, 1])
    h = history()
    dec = decomposition(h)
    inp, reg, loo = reaction(h)
    s = scenarios(h, price)
    sens = sensitivity(s, h, price)
    rdcf = reverse_dcf(h, price)
    today = multiples_today(h, price)
    h.round(3).to_csv(PROC / "abnb_driver_history_quarterly.csv", index=False)
    dec.to_csv(PROC / "abnb_revenue_decomposition.csv", index=False)
    inp.round(3).to_csv(PROC / "abnb_reaction_inputs.csv", index=False)
    reg.round(4).to_csv(PROC / "abnb_reaction_regression.csv", index=False)
    loo.round(4).to_csv(PROC / "abnb_reaction_regression_loo.csv", index=False)
    s.round(3).to_csv(PROC / "abnb_valuation_scenarios.csv", index=False)
    sens.round(2).to_csv(PROC / "abnb_valuation_sensitivity.csv", index=False)
    rdcf.round(3).to_csv(PROC / "abnb_reverse_dcf.csv", index=False)
    pd.DataFrame([today]).round(3).to_csv(PROC / "abnb_multiples_today.csv", index=False)
    figures(dec, inp, s, sens, price)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print("== today"); print(pd.Series(today).round(2).to_string())
    print("== decomposition"); print(dec.tail(10).to_string(index=False))
    print("== reaction inputs"); print(inp.round(2).to_string(index=False))
    print("== regression"); print(reg.round(3).to_string(index=False))
    print("== leave-one-out"); print(loo.round(3).to_string(index=False))
    print("== scenarios"); print(s.round(2)[["scenario", "period", "revenue_musd", "rev_growth_pct", "adj_ebitda_margin_pct", "fcf_musd", "sbc_adj_fcf_musd", "diluted_shares_m", "eps_proxy", "fcf_per_share", "price_ev_ebitda", "price_ev_fcf", "price_p_sbc_adj_fcf", "price_pe"]].to_string(index=False))
    print("== reverse dcf"); print(rdcf.round(2).to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
