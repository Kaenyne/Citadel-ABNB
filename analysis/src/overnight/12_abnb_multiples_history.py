"""
Workstream 12, part 1 and part 4: ABNB multiple history and which lens tracks the stock.

Reads
  data/processed/abnb_daily_close.csv                   daily close (yfinance, 10 Dec 2020 to 4 Sep 2026)
  data/processed/abnb_quarterly_costlines.csv           1Q20+ revenue, adj. EBITDA, SBC (letters / XBRL)
  data/processed/abnb_quarterly_kpis_from_study.csv     nights, GBV 1Q21+
  data/processed/abnb_capital_return_quarterly.csv      FCF, buybacks, withholding, diluted WA shares 1Q21+
  data/processed/abnb_revenue_guidance_vs_actual.csv    next-quarter revenue guides (Theo's dataset)
  data/processed/abnb_earnings_reactions.csv            reaction_date = first session after each print (availability date)
  data/raw/xbrl/ABNB_companyfacts.json                  cash, ST investments, debt, funds held, net income, 2020 CFO/capex, 2020 shares
  scratchpad/12/DGS10.csv                               FRED 10y constant-maturity yield (downloaded if missing)
  hard-coded Nasdaq-100 forward P/E anchors (Siblis Research quarterly table; earlier anchors, see NDX_FWD_PE below)

Writes
  data/processed/overnight/12_abnb_multiples_history.csv        quarterly 4Q20..3Q26-to-date, as-reported basis
  data/processed/overnight/12_abnb_multiples_monthly.csv        month-ends Jan 2021..Sep 2026, point-in-time basis
  data/processed/overnight/12_abnb_multiple_regressions.csv     time-series regressions of the multiple on growth, margin, rates, QQQ
  data/processed/overnight/12_abnb_lens_tracking.csv            which fundamental tracks log price (levels and 12m changes)
  data/processed/overnight/12_abnb_print_decomposition.csv      day-1 move split into estimate change vs multiple change
  analysis/figures/overnight/12_abnb_multiples_history.png
  analysis/figures/overnight/12_abnb_multiple_drivers.png
  analysis/figures/overnight/12_abnb_lens_tracking.png

Run: py -3.13 analysis/src/overnight/12_abnb_multiples_history.py   (from the repo root)
"""
import json, os, sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = lambda *a: os.path.join(ROOT, *a)
SCRATCH = r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\12"
OUT = P("data", "processed", "overnight")
FIG = P("analysis", "figures", "overnight")
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)
LAST_DATE = pd.Timestamp("2026-09-04")

# ---------------------------------------------------------------- helpers
def qlabel(ts):
    return f"{(ts.month - 1) // 3 + 1}Q{str(ts.year)[2:]}"

def qend(label):  # '4Q20' -> Timestamp('2020-12-31')
    q, y = int(label[0]), 2000 + int(label[2:])
    return pd.Timestamp(year=y, month=3 * q, day=1) + pd.offsets.MonthEnd(0)

QORDER = [f"{q}Q{y:02d}" for y in range(20, 27) for q in range(1, 5)]
QORDER = QORDER[: QORDER.index("3Q26") + 1]

# ---------------------------------------------------------------- XBRL
xb = json.load(open(P("data", "raw", "xbrl", "ABNB_companyfacts.json")))["facts"]["us-gaap"]

def xbrl_instant(tag):
    rows = [r for r in xb[tag]["units"]["USD"] if r["form"] in ("10-Q", "10-K")]
    df = pd.DataFrame(rows).sort_values(["end", "filed"]).drop_duplicates("end", keep="last")
    s = df.set_index(pd.to_datetime(df["end"]))["val"] / 1e6
    return s

def xbrl_quarterly_duration(tag, unit="USD", scale=1e6):
    """Quarterly values from 10-Q/10-K duration facts; Q4 = FY - 9M YTD, YTD cash-flow items differenced."""
    rows = [r for r in xb[tag]["units"][unit] if r["form"] in ("10-Q", "10-K")]
    df = pd.DataFrame(rows)
    df["start"] = pd.to_datetime(df["start"]); df["end"] = pd.to_datetime(df["end"])
    df["days"] = (df["end"] - df["start"]).dt.days
    df = df.sort_values(["end", "filed"]).drop_duplicates(["start", "end"], keep="last")
    out = {}
    # true quarters
    for _, r in df[(df.days > 80) & (df.days < 100)].iterrows():
        out[qlabel(r.end)] = r.val / scale
    # YTD (6M, 9M, FY) -> difference to get the quarter
    ytd = df[df.days > 100].copy()
    for _, r in ytd.iterrows():
        lab = qlabel(r.end)
        if lab in out:
            continue
        prev_end = r.end - pd.offsets.QuarterEnd(1)
        prev = ytd[(ytd.start == r.start) & (ytd.end == prev_end)]
        if len(prev):
            out[lab] = (r.val - prev.iloc[0].val) / scale
    return pd.Series(out)

cash = xbrl_instant("CashAndCashEquivalentsAtCarryingValue")
sti = xbrl_instant("ShortTermInvestments")
debt = xbrl_instant("LongTermDebtNoncurrent").add(xbrl_instant("LongTermDebtCurrent"), fill_value=0)
funds = xbrl_instant("FundsHeldForClients")
bs = pd.DataFrame({"cash_musd": cash, "st_inv_musd": sti, "debt_musd": debt, "funds_held_musd": funds})
bs.index = [qlabel(t) for t in bs.index]
bs = bs[bs.index.isin(QORDER)]
bs["net_cash_ex_float_musd"] = bs.cash_musd + bs.st_inv_musd.fillna(0) - bs.debt_musd.fillna(0)

ni_q = xbrl_quarterly_duration("NetIncomeLoss")
cfo_q = xbrl_quarterly_duration("NetCashProvidedByUsedInOperatingActivities")
capex_q = xbrl_quarterly_duration("PaymentsToAcquirePropertyPlantAndEquipment")
sh_q = xbrl_quarterly_duration("WeightedAverageNumberOfDilutedSharesOutstanding", "shares", 1e6)

# ---------------------------------------------------------------- fundamentals panel (quarterly)
cost = pd.read_csv(P("data", "processed", "abnb_quarterly_costlines.csv")).set_index("quarter")
kpi = pd.read_csv(P("data", "processed", "abnb_quarterly_kpis_from_study.csv")).set_index("quarter")
cap = pd.read_csv(P("data", "processed", "abnb_capital_return_quarterly.csv")).set_index("quarter")

f = pd.DataFrame(index=[q for q in QORDER if q != "3Q26"])
f["revenue_musd"] = cost["revenue_musd"]
f["adj_ebitda_musd"] = cost["adjusted_ebitda_musd"]
f["sbc_musd"] = cost["stock_based_comp_total_musd"]
f["net_income_musd"] = ni_q
f["nights_m"] = kpi["nights_m"]
f["fcf_musd"] = cap["fcf_musd"]
# 2020 FCF from XBRL CFO - capex (capital-return panel starts 1Q21)
for q in ["1Q20", "2Q20", "3Q20", "4Q20"]:
    if pd.isna(f.loc[q, "fcf_musd"]):
        f.loc[q, "fcf_musd"] = cfo_q.get(q, np.nan) - capex_q.get(q, np.nan)
f["buybacks_musd"] = cap["buybacks_musd"].fillna(0)
f["withholding_musd"] = cap["rsu_tax_withholding_musd"].fillna(0)
f["diluted_shares_m"] = cap["diluted_wa_shares_m"]
f.loc["4Q20", "diluted_shares_m"] = cap.loc["1Q21", "diluted_wa_shares_m"]  # IPO quarter: weighted-average count is not meaningful; use 1Q21 diluted count (601M) as the period-end proxy
f["nights_m_yoy_pct"] = 100 * (f.nights_m / f.nights_m.shift(4) - 1)
f["net_income_musd"] = f["net_income_musd"].astype(float)

# LTM sums
for c in ["revenue_musd", "adj_ebitda_musd", "sbc_musd", "net_income_musd", "fcf_musd", "buybacks_musd", "withholding_musd", "nights_m"]:
    f[c + "_ltm"] = f[c].rolling(4).sum()
f["ltm_revenue_growth_pct"] = 100 * (f.revenue_musd_ltm / f.revenue_musd_ltm.shift(4) - 1)
f["ltm_nights_growth_pct"] = 100 * (f.nights_m_ltm / f.nights_m_ltm.shift(4) - 1)
f["ltm_ebitda_margin_pct"] = 100 * f.adj_ebitda_musd_ltm / f.revenue_musd_ltm
f["ltm_fcf_margin_pct"] = 100 * f.fcf_musd_ltm / f.revenue_musd_ltm
f["ltm_sbc_pct_rev"] = 100 * f.sbc_musd_ltm / f.revenue_musd_ltm
f["ltm_sbc_adj_fcf_musd"] = f.fcf_musd_ltm - f.sbc_musd_ltm
f["ltm_eps_gaap"] = f.net_income_musd_ltm / f.diluted_shares_m
f = f.join(bs)

# ---------------------------------------------------------------- NTM proxy from the next-quarter guide
g = pd.read_csv(P("data", "processed", "abnb_revenue_guidance_vs_actual.csv"))
g["issued_q"] = g.issued_on_call.str.replace(r"(\d{4})Q(\d)", lambda m: f"{m.group(2)}Q{m.group(1)[2:]}", regex=True)
g["guided_q"] = g.guided_quarter.str.replace(r"(\d{4})Q(\d)", lambda m: f"{m.group(2)}Q{m.group(1)[2:]}", regex=True)
g = g.set_index("issued_q")
# cushion = mean beat vs mid over the prior four resolved guides (point-in-time)
g["cushion_pct"] = g.actual_vs_mid_pct.shift(1).rolling(4, min_periods=1).mean()

def ntm_proxy(q):
    """NTM revenue known right after quarter q's print: guide(q+1)*(1+cushion) then the guide-implied y/y growth applied
    to the three following prior-year quarters. Returns (ntm_rev, implied_growth_pct, label)."""
    if q not in g.index:
        return np.nan, np.nan, "no guide"
    row = g.loc[q]
    i = QORDER.index(q)
    cushion = 0.0 if pd.isna(row.cushion_pct) else row.cushion_pct / 100
    q1 = row.guide_mid_musd * (1 + cushion)
    base_prev = f.revenue_musd.get(QORDER[i - 3], np.nan)  # same quarter last year for q+1
    growth = q1 / base_prev - 1
    rest = sum(f.revenue_musd.get(QORDER[i + k - 4], np.nan) * (1 + growth) for k in range(2, 5))
    return q1 + rest, 100 * growth, f"guide mid x (1+{100*cushion:.1f}% cushion), growth {100*growth:.1f}% applied to q+2..q+4"

for q in f.index:
    r, gr, lab = ntm_proxy(q)
    f.loc[q, "ntm_revenue_proxy_musd"] = r
    f.loc[q, "ntm_growth_proxy_pct"] = gr
    f.loc[q, "ntm_proxy_method"] = lab
# 2Q26 print (Aug 2026): also record consensus (stockanalysis.com forecast page, 3 Sep 2026: FY26 $14.16B, FY27 $15.76B, 46 analysts)
f["ntm_ebitda_proxy_musd"] = f.ntm_revenue_proxy_musd * f.ltm_ebitda_margin_pct / 100

# ---------------------------------------------------------------- prices, rates, QQQ multiple
px = pd.read_csv(P("data", "processed", "abnb_daily_close.csv"), parse_dates=["Date"]).set_index("Date")["Close"]
dgs_path = os.path.join(SCRATCH, "DGS10.csv")
if not os.path.exists(dgs_path):
    import requests
    open(dgs_path, "wb").write(requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10").content)
dgs = pd.read_csv(dgs_path, na_values=".")
dgs.columns = ["date", "dgs10"]; dgs["date"] = pd.to_datetime(dgs.date); dgs = dgs.set_index("date")["dgs10"].dropna()

# Nasdaq-100 forward P/E anchors. Quarterly rows from Siblis Research (siblisresearch.com/data/nasdaq-100-pe-ratio, fetched 6 Sep 2026).
# Earlier anchors: see note; values marked approx are read from published charts (Yardeni / FactSet commentary), +/- 1 turn.
NDX_FWD_PE = {  # date: (value, source)
    "2020-12-31": (30.5, "approx, Yardeni Nasdaq-100 forward P/E chart"),
    "2021-03-31": (28.5, "approx"), "2021-06-30": (28.5, "approx"), "2021-09-30": (27.5, "approx"), "2021-12-31": (27.5, "approx"),
    "2022-03-31": (24.5, "approx"), "2022-05-12": (20.7, "search result, gurufocus/siblis 'P/E on 12 May 2022 20.71'"),
    "2022-06-30": (20.5, "approx"), "2022-09-30": (20.0, "approx"), "2022-12-31": (21.0, "approx"),
    "2023-03-31": (24.0, "approx"), "2023-06-30": (26.5, "approx"), "2023-09-30": (24.0, "approx"),
    "2023-12-31": (24.94, "Siblis"), "2024-03-31": (26.5, "approx, between Siblis rows"), "2024-06-30": (26.62, "Siblis"),
    "2024-09-30": (26.5, "approx, between Siblis rows"), "2024-12-31": (26.41, "Siblis"), "2025-03-31": (24.41, "Siblis"),
    "2025-06-30": (27.62, "Siblis"), "2025-09-30": (28.09, "Siblis"), "2025-12-31": (27.44, "Siblis"),
    "2026-03-31": (23.23, "Siblis"), "2026-06-30": (25.17, "Siblis"), "2026-09-04": (25.0, "approx, carried from Jun 2026"),
}
ndx = pd.Series({pd.Timestamp(k): v[0] for k, v in NDX_FWD_PE.items()}).sort_index()
ndx_daily = ndx.reindex(pd.date_range(ndx.index.min(), LAST_DATE)).interpolate("time")

def asof(series, date):
    s = series[:date]
    return s.iloc[-1] if len(s) else np.nan

# ---------------------------------------------------------------- quarterly table (as-reported basis)
rows = []
for q in QORDER:
    if q == "3Q26":
        d = LAST_DATE; fq = "2Q26"; basis = "3Q26 to date: 4 Sep 2026 price on 2Q26 fundamentals"
    else:
        d = qend(q); fq = q; basis = "quarter-end price on the quarter's own LTM (reported ~5 weeks later)"
    if fq not in f.index or pd.isna(f.loc[fq, "revenue_musd_ltm"]):
        continue
    r = f.loc[fq].copy()
    price = asof(px, d)
    mcap = price * r.diluted_shares_m
    ev = mcap - r.net_cash_ex_float_musd
    rows.append(dict(
        quarter=q, date=d.date(), basis=basis, price=price, diluted_shares_m=r.diluted_shares_m, market_cap_musd=mcap,
        net_cash_ex_float_musd=r.net_cash_ex_float_musd, funds_held_musd=r.funds_held_musd, ev_musd=ev,
        ltm_revenue_musd=r.revenue_musd_ltm, ltm_adj_ebitda_musd=r.adj_ebitda_musd_ltm, ltm_fcf_musd=r.fcf_musd_ltm,
        ltm_sbc_musd=r.sbc_musd_ltm, ltm_sbc_adj_fcf_musd=r.ltm_sbc_adj_fcf_musd, ltm_net_income_musd=r.net_income_musd_ltm,
        ev_ltm_revenue_x=ev / r.revenue_musd_ltm,
        ev_ltm_ebitda_x=ev / r.adj_ebitda_musd_ltm if r.ltm_ebitda_margin_pct > 5 else np.nan,
        ev_ltm_fcf_x=ev / r.fcf_musd_ltm if r.fcf_musd_ltm > 0 else np.nan,
        p_ltm_sbc_adj_fcf_x=mcap / r.ltm_sbc_adj_fcf_musd if r.ltm_sbc_adj_fcf_musd > 0 else np.nan,
        p_ltm_gaap_eps_x=mcap / r.net_income_musd_ltm if r.net_income_musd_ltm > 0 else np.nan,
        fcf_yield_pct=100 * r.fcf_musd_ltm / mcap, sbc_adj_fcf_yield_pct=100 * r.ltm_sbc_adj_fcf_musd / mcap,
        ntm_revenue_proxy_musd=r.ntm_revenue_proxy_musd, ntm_growth_proxy_pct=r.ntm_growth_proxy_pct,
        ev_ntm_revenue_x=ev / r.ntm_revenue_proxy_musd, ev_ntm_ebitda_x=ev / r.ntm_ebitda_proxy_musd if r.ltm_ebitda_margin_pct > 5 else np.nan,
        ntm_proxy_method=r.ntm_proxy_method,
        ltm_revenue_growth_pct=r.ltm_revenue_growth_pct, ltm_nights_growth_pct=r.ltm_nights_growth_pct,
        quarter_nights_growth_pct=r.nights_m_yoy_pct, ltm_ebitda_margin_pct=r.ltm_ebitda_margin_pct,
        ltm_fcf_margin_pct=r.ltm_fcf_margin_pct, ltm_sbc_pct_rev=r.ltm_sbc_pct_rev,
        buyback_yield_pct=100 * r.buybacks_musd_ltm / mcap,
        net_cash_return_yield_pct=100 * (r.buybacks_musd_ltm + r.withholding_musd_ltm - r.sbc_musd_ltm) / mcap,
        dgs10_pct=asof(dgs, d), ndx_fwd_pe=asof(ndx_daily, d),
    ))
Q = pd.DataFrame(rows)
Q.to_csv(os.path.join(OUT, "12_abnb_multiples_history.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- monthly point-in-time table
rx = pd.read_csv(P("data", "processed", "abnb_earnings_reactions.csv"), parse_dates=["reaction_date"])
rx["q"] = rx.quarter.str.replace(r"(\d{4})Q(\d)", lambda m: f"{m.group(2)}Q{m.group(1)[2:]}", regex=True)
avail = rx.set_index("q")["reaction_date"]  # results known from this session on
mends = list(pd.date_range("2021-01-31", "2026-08-31", freq="ME")) + [LAST_DATE]
mrows = []
for d in mends:
    known = avail[avail <= d]
    if known.empty:
        continue
    fq = known.index[-1]
    r = f.loc[fq]
    if pd.isna(r.revenue_musd_ltm):
        continue
    price = asof(px, d); mcap = price * r.diluted_shares_m; ev = mcap - r.net_cash_ex_float_musd
    mrows.append(dict(
        month_end=d.date(), last_reported_quarter=fq, price=price, diluted_shares_m=r.diluted_shares_m, market_cap_musd=mcap, ev_musd=ev,
        ev_ltm_revenue_x=ev / r.revenue_musd_ltm,
        ev_ltm_ebitda_x=ev / r.adj_ebitda_musd_ltm if r.ltm_ebitda_margin_pct > 5 else np.nan,
        ev_ltm_fcf_x=ev / r.fcf_musd_ltm if r.fcf_musd_ltm > 0 else np.nan,
        p_ltm_sbc_adj_fcf_x=mcap / r.ltm_sbc_adj_fcf_musd if r.ltm_sbc_adj_fcf_musd > 0 else np.nan,
        p_ltm_gaap_eps_x=mcap / r.net_income_musd_ltm if r.net_income_musd_ltm > 0 else np.nan,
        ev_ntm_revenue_x=ev / r.ntm_revenue_proxy_musd, ev_ntm_ebitda_x=ev / r.ntm_ebitda_proxy_musd if r.ltm_ebitda_margin_pct > 5 else np.nan,
        fcf_yield_pct=100 * r.fcf_musd_ltm / mcap,
        ltm_revenue_musd=r.revenue_musd_ltm, ltm_adj_ebitda_musd=r.adj_ebitda_musd_ltm, ltm_fcf_musd=r.fcf_musd_ltm,
        ltm_sbc_adj_fcf_musd=r.ltm_sbc_adj_fcf_musd, ltm_net_income_musd=r.net_income_musd_ltm,
        ntm_revenue_proxy_musd=r.ntm_revenue_proxy_musd, ntm_growth_proxy_pct=r.ntm_growth_proxy_pct,
        ltm_revenue_growth_pct=r.ltm_revenue_growth_pct, ltm_nights_growth_pct=r.ltm_nights_growth_pct,
        ltm_ebitda_margin_pct=r.ltm_ebitda_margin_pct, ltm_fcf_margin_pct=r.ltm_fcf_margin_pct, ltm_sbc_pct_rev=r.ltm_sbc_pct_rev,
        buyback_yield_pct=100 * r.buybacks_musd_ltm / mcap, dgs10_pct=asof(dgs, d), ndx_fwd_pe=asof(ndx_daily, d),
    ))
M = pd.DataFrame(mrows)
M.to_csv(os.path.join(OUT, "12_abnb_multiples_monthly.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- regressions
def ols(df, y, xs, label, hac_lags=None):
    d = df[[y] + xs].dropna()
    X = sm.add_constant(d[xs])
    if hac_lags:
        m = sm.OLS(d[y], X).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    else:
        m = sm.OLS(d[y], X).fit(cov_type="HC1")
    dw = sm.stats.durbin_watson(m.resid)
    idx = d.index
    span = f"{df.loc[idx[0], 'quarter'] if 'quarter' in df.columns else df.loc[idx[0], 'month_end'] if 'month_end' in df.columns else idx[0]} to {df.loc[idx[-1], 'quarter'] if 'quarter' in df.columns else df.loc[idx[-1], 'month_end'] if 'month_end' in df.columns else idx[-1]}"
    out = dict(sample=label, span=span, dependent=y, regressors="+".join(xs), n=int(m.nobs), r2=m.rsquared, adj_r2=m.rsquared_adj, durbin_watson=dw)
    for x in ["const"] + xs:
        out[f"b_{x}"] = m.params[x]; out[f"t_{x}"] = m.tvalues[x]
    return out, m

reg_rows = []
Qr = Q[(Q.quarter != "3Q26") & Q.ev_ltm_ebitda_x.notna() & (Q.ltm_revenue_growth_pct < 60)].copy()  # drops 4Q20-3Q21 (COVID base) and negative EBITDA
Mr = M[M.ev_ltm_ebitda_x.notna() & (M.ltm_revenue_growth_pct < 60)].copy()
specs = [
    ("ev_ltm_ebitda_x", ["ltm_revenue_growth_pct"]),
    ("ev_ltm_ebitda_x", ["ntm_growth_proxy_pct"]),
    ("ev_ltm_ebitda_x", ["ltm_revenue_growth_pct", "ltm_ebitda_margin_pct"]),
    ("ev_ltm_ebitda_x", ["ltm_revenue_growth_pct", "dgs10_pct"]),
    ("ev_ltm_ebitda_x", ["ltm_revenue_growth_pct", "ndx_fwd_pe"]),
    ("ev_ltm_ebitda_x", ["ltm_revenue_growth_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
    ("ev_ltm_ebitda_x", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
    ("ev_ltm_fcf_x", ["ltm_revenue_growth_pct"]),
    ("ev_ltm_fcf_x", ["ltm_revenue_growth_pct", "ltm_fcf_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
    ("ev_ntm_ebitda_x", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
    ("ev_ntm_revenue_x", ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
    ("p_ltm_sbc_adj_fcf_x", ["ltm_revenue_growth_pct", "ltm_fcf_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
]
models = {}
for y, xs in specs:
    o, m = ols(Qr, y, xs, "quarterly as-reported (LTM growth < 60%, margin > 5%)"); reg_rows.append(o); models[("Q", y, tuple(xs))] = m
    o, m = ols(Mr, y, xs, "monthly point-in-time, Newey-West 6 lags", hac_lags=6); reg_rows.append(o); models[("M", y, tuple(xs))] = m
# post-2022 subsample (excludes the 2022 de-rating from a 40% growth base)
Mr2 = Mr[pd.to_datetime(Mr.month_end) >= "2023-01-01"]
for y, xs in [("ev_ltm_ebitda_x", ["ltm_revenue_growth_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"]),
              ("ev_ltm_ebitda_x", ["ntm_growth_proxy_pct", "dgs10_pct", "ndx_fwd_pe"]),
              ("ev_ltm_fcf_x", ["ltm_revenue_growth_pct", "ltm_fcf_margin_pct", "dgs10_pct", "ndx_fwd_pe"])]:
    o, m = ols(Mr2, y, xs, "monthly 2023-2026 point-in-time, Newey-West 6 lags", hac_lags=6); reg_rows.append(o); models[("M23", y, tuple(xs))] = m
# first differences (12-month changes) to strip the common trend
Md = Mr.set_index(pd.to_datetime(Mr.month_end))
D = pd.DataFrame({c + "_d12": Md[c].diff(12) for c in ["ev_ltm_ebitda_x", "ev_ltm_fcf_x", "ltm_revenue_growth_pct", "ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "ltm_fcf_margin_pct", "dgs10_pct", "ndx_fwd_pe"]}).dropna()
for y, xs in [("ev_ltm_ebitda_x_d12", ["ltm_revenue_growth_pct_d12", "ltm_ebitda_margin_pct_d12", "dgs10_pct_d12", "ndx_fwd_pe_d12"]),
              ("ev_ltm_ebitda_x_d12", ["ntm_growth_proxy_pct_d12", "dgs10_pct_d12", "ndx_fwd_pe_d12"]),
              ("ev_ltm_fcf_x_d12", ["ltm_revenue_growth_pct_d12", "ltm_fcf_margin_pct_d12", "dgs10_pct_d12", "ndx_fwd_pe_d12"])]:
    o, m = ols(D, y, xs, "monthly 12m changes, Newey-West 12 lags", hac_lags=12); reg_rows.append(o)
R = pd.DataFrame(reg_rows)
R.to_csv(os.path.join(OUT, "12_abnb_multiple_regressions.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- part 4: which lens tracks the stock
Ml = M.set_index(pd.to_datetime(M.month_end))
# Per-share lenses: the question is which fundamental the SHARE PRICE tracks, so divide each LTM/NTM total by the
# diluted share count of the last reported quarter. Buybacks have cut the count ~4%/yr since 2023, so the per-share
# and whole-company answers differ.
lens = {"LTM revenue": "ltm_revenue_musd", "LTM adj. EBITDA": "ltm_adj_ebitda_musd", "LTM FCF": "ltm_fcf_musd",
        "LTM SBC-adjusted FCF": "ltm_sbc_adj_fcf_musd", "LTM GAAP net income": "ltm_net_income_musd",
        "NTM revenue (guide proxy)": "ntm_revenue_proxy_musd"}
for col in lens.values():
    Ml[col + "_ps"] = Ml[col] / Ml.diluted_shares_m
lrows = []
for win, (a, b) in {"2021-2026": ("2021-01-01", "2026-12-31"), "2022-2026": ("2022-01-01", "2026-12-31"), "2023-2026": ("2023-01-01", "2026-12-31")}.items():
    w = Ml[a:b]
    for name, col in lens.items():
        d0 = w[[col, col + "_ps", "market_cap_musd", "price"]].copy()
        d0 = d0[d0[col] > 0]
        lv = np.log(d0["market_cap_musd"]).corr(np.log(d0[col]))
        lp = np.log(d0["price"]).corr(np.log(d0[col + "_ps"]))
        ch = (np.log(d0["market_cap_musd"]).diff(12)).corr(np.log(d0[col]).diff(12))
        ch_ps = (np.log(d0["price"]).diff(12)).corr(np.log(d0[col + "_ps"]).diff(12))
        # fit log price = a + b log X_ps: slope and residual sd (how stable the implied per-share multiple is)
        d = d0.dropna()
        X = sm.add_constant(np.log(d[col + "_ps"])); m = sm.OLS(np.log(d["price"]), X).fit()
        lrows.append(dict(window=win, lens=name, n=len(d), corr_log_mcap_vs_total=lv, corr_log_price_vs_per_share=lp,
                          corr_12m_log_changes_total=ch, corr_12m_log_changes_per_share=ch_ps,
                          slope_log_price_on_log_ps=m.params.iloc[1], resid_sd_log_price=np.sqrt(m.mse_resid),
                          months_positive=len(d0), months_total=len(w)))
L = pd.DataFrame(lrows)
L.to_csv(os.path.join(OUT, "12_abnb_lens_tracking.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- part 4b: day-1 move = estimate change + multiple change
# For each guided print: NTM revenue proxy before (from prior quarter's guide, rolled) vs after (new guide); price day before vs reaction day.
prow = []
for _, r in rx.iterrows():
    q = r.q
    if q not in f.index or q not in QORDER:
        continue
    i = QORDER.index(q); pq = QORDER[i - 1]
    d1 = r.reaction_date; d0 = px[:d1].index[-2]  # last close before the reaction session
    p0, p1 = px[d0], px[d1]
    new = f.loc[q, "ntm_revenue_proxy_musd"]
    # "old" NTM as of just before the print: the prior proxy (q-1 basis) rolled one quarter: drop q, add q+4 at the same implied growth
    old_g = f.loc[pq, "ntm_growth_proxy_pct"] / 100 if pq in f.index else np.nan
    if pd.isna(old_g) or pd.isna(new):
        continue
    old = sum(f.revenue_musd.get(QORDER[i + k - 4], np.nan) * (1 + old_g) for k in range(1, 5))
    # EV before/after with the newly reported net cash (balance sheet is the same in both, so the split is not affected)
    sh = f.loc[q, "diluted_shares_m"]; nc = f.loc[q, "net_cash_ex_float_musd"]
    ev0, ev1 = p0 * sh - nc, p1 * sh - nc
    prow.append(dict(quarter=q, reaction_date=d1.date(), price_before=p0, price_after=p1, ret_1d_pct=100 * (p1 / p0 - 1),
                     ntm_rev_before_musd=old, ntm_rev_after_musd=new, estimate_change_pct=100 * (new / old - 1),
                     ev_ntm_rev_before_x=ev0 / old, ev_ntm_rev_after_x=ev1 / new, multiple_change_pct=100 * ((ev1 / new) / (ev0 / old) - 1),
                     ev_change_pct=100 * (ev1 / ev0 - 1), quarter_nights_growth_pct=f.loc[q, "nights_m_yoy_pct"],
                     nights_accel_pts=f.loc[q, "nights_m_yoy_pct"] - f.loc[pq, "nights_m_yoy_pct"] if pq in f.index else np.nan,
                     excess_1d_pct=r.excess_1d_pct))
PD = pd.DataFrame(prow)
PD.to_csv(os.path.join(OUT, "12_abnb_print_decomposition.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
t = pd.to_datetime(Ml.index)
ax[0].plot(t, Ml.ev_ltm_ebitda_x, label="EV / LTM adj. EBITDA", color="#1f4e79")
ax[0].plot(t, Ml.ev_ltm_fcf_x, label="EV / LTM FCF", color="#c55a11")
ax[0].plot(t, Ml.p_ltm_sbc_adj_fcf_x, label="P / LTM SBC-adjusted FCF", color="#7f7f7f", ls="--")
ax[0].plot(t, Ml.ev_ntm_ebitda_x, label="EV / NTM EBITDA (guide proxy)", color="#2e75b6", ls=":")
ax[0].set_ylim(0, 80); ax[0].set_ylabel("x"); ax[0].legend(ncol=2, frameon=False); ax[0].set_title("ABNB multiples, month-end, point-in-time (last reported LTM)")
ax[1].plot(t, Ml.ltm_revenue_growth_pct, label="LTM revenue growth %", color="#1f4e79")
ax[1].plot(t, Ml.ntm_growth_proxy_pct, label="NTM growth proxy % (guide)", color="#2e75b6", ls=":")
ax[1].plot(t, Ml.ltm_ebitda_margin_pct, label="LTM adj. EBITDA margin %", color="#c55a11")
ax[1].set_ylim(0, 80); ax[1].legend(ncol=3, frameon=False); ax[1].set_ylabel("%")
ax[2].plot(t, Ml.dgs10_pct, label="10y UST %", color="#7f7f7f")
ax2 = ax[2].twinx(); ax2.plot(t, Ml.ndx_fwd_pe, label="Nasdaq-100 fwd P/E (anchors, interpolated)", color="#548235"); ax2.set_ylim(15, 35)
ax[2].legend(loc="upper left", frameon=False); ax2.legend(loc="upper right", frameon=False); ax[2].set_ylabel("%"); ax2.set_ylabel("x")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_abnb_multiples_history.png"), dpi=150); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(13, 4))
for a, x, xl in zip(ax, ["ltm_revenue_growth_pct", "ntm_growth_proxy_pct", "ndx_fwd_pe"], ["LTM revenue growth %", "NTM growth proxy %", "Nasdaq-100 forward P/E"]):
    d = Mr[[x, "ev_ltm_ebitda_x", "month_end"]].dropna()
    yr = pd.to_datetime(d.month_end).dt.year
    sc = a.scatter(d[x], d.ev_ltm_ebitda_x, c=yr, cmap="viridis", s=18)
    a.set_xlabel(xl); a.set_ylabel("EV / LTM adj. EBITDA (x)")
    for yy in sorted(yr.unique()):
        dd = d[yr == yy]; a.annotate(str(yy), (dd[x].mean(), dd.ev_ltm_ebitda_x.mean()), fontsize=8)
plt.suptitle("ABNB EV/EBITDA against growth and the market multiple, monthly 2021-2026 (colour = year)")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_abnb_multiple_drivers.png"), dpi=150); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
w = Ml["2022-01-01":]
for name, col in lens.items():
    s = w[col].where(w[col] > 0)
    ax[0].plot(w.index, s / s.dropna().iloc[0], label=name)
ax[0].plot(w.index, w.market_cap_musd / w.market_cap_musd.iloc[0], label="Market cap", color="black", lw=2)
ax[0].set_title("Indexed to Jan 2022 = 1: market cap vs LTM fundamentals"); ax[0].legend(frameon=False, fontsize=7)
sub = L[L.window == "2022-2026"].set_index("lens")
ax[1].barh(sub.index, sub.corr_12m_log_changes_per_share, color="#1f4e79"); ax[1].set_title("Correlation of 12-month log changes: price vs per-share lens, 2022-2026"); ax[1].axvline(0, color="k", lw=0.5)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_abnb_lens_tracking.png"), dpi=150); plt.close()

# ---------------------------------------------------------------- console summary
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(Q[["quarter", "price", "ev_musd", "ev_ltm_revenue_x", "ev_ltm_ebitda_x", "ev_ltm_fcf_x", "p_ltm_sbc_adj_fcf_x", "p_ltm_gaap_eps_x", "ev_ntm_revenue_x", "ev_ntm_ebitda_x", "ltm_revenue_growth_pct", "ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"]].round(1).to_string())
print(R[["sample", "dependent", "regressors", "n", "r2", "durbin_watson"] + [c for c in R.columns if c.startswith("b_") or c.startswith("t_")]].round(2).to_string())
print(L.round(3).to_string())
print(PD.round(1).to_string())
