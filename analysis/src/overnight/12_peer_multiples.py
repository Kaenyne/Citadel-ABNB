"""
Workstream 12, part 2: cross-sectional multiples for ABNB and 18 peers, and what the cross-section implies for ABNB's exit multiple.

Reads
  scratchpad/12/facts/<TICKER>.json     EDGAR XBRL companyfacts (fetched 6 Sep 2026 with UA 'citadel-abnb research ksurapaneni@ufl.edu')
  scratchpad/12/peer_info.json          yfinance .info snapshot (price, market cap, shares, total debt/cash, forward P/E), 6 Sep 2026
  scratchpad/12/peer_estimates.json     yfinance revenue_estimate / earnings_estimate (consensus FY0, FY+1), 6 Sep 2026
  scratchpad/12/peer_prices_daily.csv   yfinance closes to 4 Sep 2026
  data/processed/abnb_valuation_scenarios.csv   driver-model FY27E bear/base/bull fundamentals
  data/processed/abnb_multiples_today.csv       ABNB EV and LTM figures at $181.94

Writes
  data/processed/overnight/12_peer_multiples.csv           one row per company with LTM, NTM and multiples and the source of each block
  data/processed/overnight/12_peer_regressions.csv         cross-sectional fits and ABNB implied multiples by scenario
  analysis/figures/overnight/12_peer_crosssection.png

Method notes
  LTM = last four reported quarters from XBRL 10-Q/10-K duration facts (Q4 = FY - 9M). 20-F filers (TCOM, MMYT, SPOT) have annual-only XBRL,
  so their LTM comes from yfinance quarterly statements (source column says which). DESP was taken private by Prosus in May 2025 and is not listed.
  Adj. EBITDA = operating income + D&A + SBC (the company-style definition ABNB uses); GAAP-ish EBITDA = operating income + D&A.
  NTM revenue = time-weighted consensus FY0/FY+1 from yfinance (as of 6 Sep 2026; Dec year-ends except MMYT which is March).
  NTM EBITDA and NTM FCF hold the LTM margin on NTM revenue (no EBITDA consensus available free), so EV/NTM EBITDA differences across
  companies are driven by growth and today's margin, not by consensus margin change. NTM P/E uses the yfinance consensus EPS.
  EV = market cap (yfinance) - cash - short-term investments + total debt (yfinance totalDebt, which includes leases). Customer float is
  not removed for anyone (BKNG, EXPE, ABNB all carry it); ABNB's own row is recomputed from abnb_multiples_today.csv for consistency with the model.
Run: py -3.13 analysis/src/overnight/12_peer_multiples.py
"""
import json, os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = lambda *a: os.path.join(ROOT, *a)
S = r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\12"
OUT = P("data", "processed", "overnight"); FIG = P("analysis", "figures", "overnight")
AS_OF = pd.Timestamp("2026-09-04")

TICKERS = ["ABNB", "BKNG", "EXPE", "TRIP", "TCOM", "MMYT", "UBER", "DASH", "META", "NFLX", "SPOT", "DUOL", "GOOGL", "AMZN", "MAR", "HLT", "H", "ETSY", "EBAY"]
GROUP = {"ABNB": "ABNB", "BKNG": "OTA", "EXPE": "OTA", "TRIP": "OTA", "TCOM": "OTA", "MMYT": "OTA", "UBER": "Marketplace", "DASH": "Marketplace",
         "ETSY": "Marketplace", "EBAY": "Marketplace", "META": "Mega-cap internet", "GOOGL": "Mega-cap internet", "AMZN": "Mega-cap internet",
         "NFLX": "Subscription", "SPOT": "Subscription", "DUOL": "Subscription", "MAR": "Hotel franchisor", "HLT": "Hotel franchisor", "H": "Hotel franchisor"}
FYE_MONTH = {t: 12 for t in TICKERS}; FYE_MONTH["MMYT"] = 3

info = json.load(open(os.path.join(S, "peer_info.json")))
est = json.load(open(os.path.join(S, "peer_estimates.json")))
px = pd.read_csv(os.path.join(S, "peer_prices_daily.csv"), index_col=0, parse_dates=True)

TAGS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "op_income": ["OperatingIncomeLoss"],
    "da": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet", "DepreciationAmortizationAndOther", "Depreciation"],
    "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets", "PaymentsForCapitalImprovements"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
}
INSTANT = {
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "sti": ["ShortTermInvestments", "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "DebtSecuritiesAvailableForSaleCurrent"],
}

def qlabel(ts): return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"

def quarterly(facts, tag):
    units = facts[tag]["units"]; unit = "USD" if "USD" in units else list(units)[0]
    rows = [r for r in units[unit] if r["form"] in ("10-Q", "10-K")]
    if not rows: return pd.Series(dtype=float)
    df = pd.DataFrame(rows); df["start"] = pd.to_datetime(df.start); df["end"] = pd.to_datetime(df.end)
    df["days"] = (df.end - df.start).dt.days
    df = df.sort_values(["end", "filed"]).drop_duplicates(["start", "end"], keep="last")
    out = {}
    for _, r in df[(df.days > 80) & (df.days < 100)].iterrows(): out[r.end] = r.val / 1e6
    ytd = df[df.days > 100]
    for _, r in ytd.iterrows():
        if r.end in out: continue
        prev_end = r.end - pd.offsets.QuarterEnd(1)
        prev = ytd[(ytd.start == r.start) & (abs((ytd.end - prev_end).dt.days) < 8)]
        if len(prev): out[r.end] = (r.val - prev.iloc[0].val) / 1e6
    return pd.Series(out).sort_index()

def instant(facts, tag):
    units = facts[tag]["units"]; rows = [r for r in units.get("USD", []) if r["form"] in ("10-Q", "10-K")]
    if not rows: return pd.Series(dtype=float)
    df = pd.DataFrame(rows).sort_values(["end", "filed"]).drop_duplicates("end", keep="last")
    return pd.Series(df.val.values / 1e6, index=pd.to_datetime(df.end)).sort_index()

def ltm_from_xbrl(t):
    fp = os.path.join(S, "facts", f"{t}.json")
    if not os.path.exists(fp): return {}, {}
    facts = json.load(open(fp))["facts"].get("us-gaap", {})
    vals, src = {}, {}
    for k, tags in TAGS.items():
        for tag in tags:
            if tag in facts:
                q = quarterly(facts, tag)
                if q.empty: continue
                q = q[q.index <= AS_OF]
                if len(q) >= 4 and (AS_OF - q.index[-1]).days < 120:
                    vals[k] = q.iloc[-4:].sum(); src[k] = f"xbrl:{tag}"; vals[k + "_last_q_end"] = q.index[-1].date(); break
    for k, tags in INSTANT.items():
        for tag in tags:
            if tag in facts:
                s = instant(facts, tag)
                if s.empty: continue
                s = s[s.index <= AS_OF]
                if len(s) and (AS_OF - s.index[-1]).days < 120:
                    vals[k] = s.iloc[-1]; src[k] = f"xbrl:{tag}"; break
    return vals, src

def ltm_from_yf(t):
    import yfinance as yf
    tk = yf.Ticker(t); vals, src = {}, {}
    try:
        inc = tk.quarterly_income_stmt; cf = tk.quarterly_cashflow; bs = tk.quarterly_balance_sheet
    except Exception as e:
        return vals, src
    def s4(df, row):
        if df is None or row not in df.index: return np.nan
        s = df.loc[row].dropna().sort_index()
        return s.iloc[-4:].sum() / 1e6 if len(s) >= 4 else np.nan
    def last(df, row):
        if df is None or row not in df.index: return np.nan
        s = df.loc[row].dropna().sort_index(); return s.iloc[-1] / 1e6 if len(s) else np.nan
    m = {"revenue": ("inc", "Total Revenue"), "op_income": ("inc", "Operating Income"), "da": ("inc", "Reconciled Depreciation"),
         "sbc": ("cf", "Stock Based Compensation"), "cfo": ("cf", "Operating Cash Flow"), "capex": ("cf", "Capital Expenditure"),
         "buybacks": ("cf", "Repurchase Of Capital Stock"), "net_income": ("inc", "Net Income")}
    for k, (which, row) in m.items():
        v = s4({"inc": inc, "cf": cf}[which], row)
        if not pd.isna(v): vals[k] = abs(v) if k in ("capex", "buybacks") else v; src[k] = f"yfinance:{row}"
    for k, row in {"cash": "Cash And Cash Equivalents", "sti": "Other Short Term Investments"}.items():
        v = last(bs, row)
        if not pd.isna(v): vals[k] = v; src[k] = f"yfinance:{row}"
    return vals, src

def ltm_from_yf_annual(t, ltm_rev_local):
    """Last resort for 20-F filers with no quarterly cash-flow statement (TCOM, MMYT): take the most recent fiscal-year
    value and scale it to LTM by the revenue ratio. Marked 'yfinance-FY-scaled' in the sources column."""
    import yfinance as yf
    tk = yf.Ticker(t); vals, src = {}, {}
    try:
        inc = tk.income_stmt; cf = tk.cashflow
    except Exception:
        return vals, src
    def col0(df, row):
        if df is None or row not in df.index: return np.nan
        srs = df.loc[row].dropna().sort_index()
        return srs.iloc[-1] / 1e6 if len(srs) else np.nan
    fy_rev = col0(inc, "Total Revenue")
    k = (ltm_rev_local / fy_rev) if (fy_rev and not pd.isna(fy_rev) and not pd.isna(ltm_rev_local)) else 1.0
    m = {"da": ("cf", "Depreciation And Amortization"), "sbc": ("cf", "Stock Based Compensation"),
         "cfo": ("cf", "Operating Cash Flow"), "capex": ("cf", "Capital Expenditure"),
         "buybacks": ("cf", "Repurchase Of Capital Stock"), "net_income": ("inc", "Net Income"),
         "op_income": ("inc", "Operating Income")}
    for kk, (which, row) in m.items():
        v = col0({"inc": inc, "cf": cf}[which], row)
        if not pd.isna(v):
            vals[kk] = abs(v) * k if kk in ("capex", "buybacks") else v * k
            src[kk] = f"yfinance-FY-scaled:{row} x{k:.2f}"
    return vals, src

# Reporting-currency fixes. TCOM reports in CNY and SPOT in EUR; yfinance gives their price and market cap in USD but
# their statements, totalDebt and consensus estimates in the reporting currency. Convert every statement-derived item,
# totalDebt and the consensus revenue/EPS to USD so EV and the multiples are in one currency. (MMYT reports in USD.)
STMT_CCY = {"TCOM": "CNY", "SPOT": "EUR"}
fx_path = os.path.join(S, "fx_rates.json")
if not os.path.exists(fx_path):
    import yfinance as yf
    json.dump({"CNY": float(yf.Ticker("CNY=X").history(period="10d")["Close"].iloc[-1]),
               "EUR": float(yf.Ticker("EURUSD=X").history(period="10d")["Close"].iloc[-1])}, open(fx_path, "w"))
FX = json.load(open(fx_path))          # CNY = USD/CNY (units of CNY per USD); EUR = USD per EUR
TO_USD = {"CNY": 1.0 / FX["CNY"], "EUR": FX["EUR"]}
rows = []
for t in TICKERS:
    v, s = ltm_from_xbrl(t)
    NEED = ["revenue", "op_income", "da", "sbc", "cfo", "capex", "buybacks", "net_income", "cash", "sti"]
    need = [k for k in NEED if k not in v]
    if need:
        v2, s2 = ltm_from_yf(t)
        for k in need:
            if k in v2: v[k] = v2[k]; s[k] = s2[k]
    need = [k for k in NEED if k not in v and k not in ("cash", "sti")]
    if need and "revenue" in v:
        v3, s3 = ltm_from_yf_annual(t, v["revenue"])
        for k in need:
            if k in v3: v[k] = v3[k]; s[k] = s3[k]
    ccy = STMT_CCY.get(t); k_usd = TO_USD.get(ccy, 1.0)
    if ccy:
        for k in list(v):
            if not k.endswith("_last_q_end"): v[k] = v[k] * k_usd
        s["fx"] = f"{ccy} statements, estimates and totalDebt x {k_usd:.4f} USD/{ccy} (yfinance, 4-6 Sep 2026)"
    i = info.get(t, {}); e = est.get(t, {}) or {}
    price = px[t].dropna().iloc[-1]
    mcap = i.get("marketCap", np.nan) / 1e6
    shares = mcap / price
    debt = (i.get("totalDebt") or 0) / 1e6 * k_usd
    cash = v.get("cash", np.nan); sti = v.get("sti", 0) if not pd.isna(v.get("sti", np.nan)) else 0
    net_cash = cash + sti - debt
    ev = mcap - net_cash
    rev = v.get("revenue", np.nan); oi = v.get("op_income", np.nan); da = v.get("da", np.nan); sbc = v.get("sbc", np.nan)
    fcf = v.get("cfo", np.nan) - v.get("capex", np.nan)
    ebitda_adj = oi + da + sbc; ebitda_gaap = oi + da
    # consensus NTM revenue: weight FY0 / FY+1 by months remaining in FY0 from AS_OF
    ntm_rev = np.nan; ntm_g = np.nan; ntm_eps = np.nan; ntm_src = "n/a"
    try:
        ke = TO_USD.get(e["rev"]["0y"].get("currency", "USD"), 1.0)
        r0 = e["rev"]["0y"]["avg"] / 1e6 * ke; r1 = e["rev"]["+1y"]["avg"] / 1e6 * ke
        fye = FYE_MONTH[t]; months_left = (fye - AS_OF.month) % 12 or 12
        w0 = months_left / 12
        ntm_rev = w0 * r0 + (1 - w0) * r1; ntm_g = 100 * (ntm_rev / rev - 1)
        ntm_src = f"yfinance consensus FY0 {r0:,.0f} / FY1 {r1:,.0f}, w0={w0:.2f}"
        kp = TO_USD.get(e["eps"]["0y"].get("currency", "USD"), 1.0)
        e0 = e["eps"]["0y"]["avg"] * kp; e1 = e["eps"]["+1y"]["avg"] * kp; ntm_eps = w0 * e0 + (1 - w0) * e1
    except Exception:
        pass
    rows.append(dict(
        ticker=t, group=GROUP[t], price=price, market_cap_musd=mcap, shares_m=shares, net_cash_musd=net_cash, total_debt_musd=debt, ev_musd=ev,
        ltm_revenue_musd=rev, ltm_op_income_musd=oi, ltm_da_musd=da, ltm_sbc_musd=sbc, ltm_adj_ebitda_musd=ebitda_adj, ltm_gaap_ebitda_musd=ebitda_gaap,
        ltm_fcf_musd=fcf, ltm_sbc_adj_fcf_musd=fcf - sbc, ltm_net_income_musd=v.get("net_income", np.nan), ltm_buybacks_musd=v.get("buybacks", np.nan),
        ntm_revenue_musd=ntm_rev, ntm_revenue_growth_pct=ntm_g, ntm_eps=ntm_eps, ntm_source=ntm_src,
        adj_ebitda_margin_pct=100 * ebitda_adj / rev, gaap_ebitda_margin_pct=100 * ebitda_gaap / rev, fcf_margin_pct=100 * fcf / rev,
        sbc_pct_rev=100 * sbc / rev, fcf_conversion_pct=100 * fcf / ebitda_adj, net_cash_pct_mcap=100 * net_cash / mcap,
        buyback_yield_pct=100 * v.get("buybacks", np.nan) / mcap, fcf_yield_pct=100 * fcf / mcap,
        ev_ltm_revenue_x=ev / rev, ev_ltm_adj_ebitda_x=ev / ebitda_adj, ev_ltm_gaap_ebitda_x=ev / ebitda_gaap, ev_ltm_fcf_x=ev / fcf,
        ev_ltm_sbc_adj_fcf_x=ev / (fcf - sbc) if fcf - sbc > 0 else np.nan,
        ev_ntm_revenue_x=ev / ntm_rev, ev_ntm_adj_ebitda_x=ev / (ntm_rev * ebitda_adj / rev), ev_ntm_gaap_ebitda_x=ev / (ntm_rev * ebitda_gaap / rev),
        ev_ntm_fcf_x=ev / (ntm_rev * fcf / rev), ev_ntm_sbc_adj_fcf_x=ev / (ntm_rev * (fcf - sbc) / rev) if fcf - sbc > 0 else np.nan,
        pe_ntm_x=price / ntm_eps if ntm_eps and ntm_eps > 0 else np.nan, pe_ltm_x=mcap / v.get("net_income", np.nan) if v.get("net_income", 0) > 0 else np.nan,
        rule_of_40=ntm_g + 100 * fcf / rev, rule_of_40_sbc_adj=ntm_g + 100 * (fcf - sbc) / rev,
        ltm_last_q_end=v.get("revenue_last_q_end", ""), sources="; ".join(f"{k}={s[k]}" for k in s),
    ))
D = pd.DataFrame(rows)

# ABNB row: align with the model's EV (ex float, per abnb_multiples_today.csv) but keep consensus NTM from yfinance / stockanalysis
today = pd.read_csv(P("data", "processed", "abnb_multiples_today.csv")).iloc[0]
a = D.index[D.ticker == "ABNB"][0]
D.loc[a, "market_cap_musd"] = today.market_cap_musd; D.loc[a, "net_cash_musd"] = today.net_cash_ex_float_musd; D.loc[a, "ev_musd"] = today.ev_musd
D.loc[a, "ltm_adj_ebitda_musd"] = today.ltm_adj_ebitda_musd; D.loc[a, "ltm_fcf_musd"] = today.ltm_fcf_musd; D.loc[a, "ltm_sbc_musd"] = today.ltm_sbc_musd
D.loc[a, "ltm_revenue_musd"] = today.ltm_revenue_musd; D.loc[a, "ltm_sbc_adj_fcf_musd"] = today.ltm_sbc_adj_fcf_musd
# stockanalysis.com consensus (3 Sep 2026, 46 analysts): FY26 $14.16B, FY27 $15.76B -> NTM Sep26-Aug27 = 4/12*14.16 + 8/12*15.76
D.loc[a, "ntm_revenue_musd"] = (4 / 12) * 14160 + (8 / 12) * 15760
D.loc[a, "ntm_source"] = "stockanalysis.com consensus 3 Sep 2026: FY26 $14.16B, FY27 $15.76B, 46 analysts"
r = D.loc[a]
D.loc[a, "ntm_revenue_growth_pct"] = 100 * (r.ntm_revenue_musd / r.ltm_revenue_musd - 1)
D.loc[a, "adj_ebitda_margin_pct"] = 100 * r.ltm_adj_ebitda_musd / r.ltm_revenue_musd
D.loc[a, "fcf_margin_pct"] = 100 * r.ltm_fcf_musd / r.ltm_revenue_musd; D.loc[a, "sbc_pct_rev"] = 100 * r.ltm_sbc_musd / r.ltm_revenue_musd
D.loc[a, "fcf_conversion_pct"] = 100 * r.ltm_fcf_musd / r.ltm_adj_ebitda_musd; D.loc[a, "net_cash_pct_mcap"] = 100 * r.net_cash_musd / r.market_cap_musd
D.loc[a, "fcf_yield_pct"] = 100 * r.ltm_fcf_musd / r.market_cap_musd
D.loc[a, "ev_ltm_revenue_x"] = r.ev_musd / r.ltm_revenue_musd; D.loc[a, "ev_ltm_adj_ebitda_x"] = r.ev_musd / r.ltm_adj_ebitda_musd
D.loc[a, "ev_ltm_fcf_x"] = r.ev_musd / r.ltm_fcf_musd; D.loc[a, "ev_ltm_sbc_adj_fcf_x"] = r.ev_musd / r.ltm_sbc_adj_fcf_musd
r = D.loc[a]
D.loc[a, "ev_ntm_revenue_x"] = r.ev_musd / r.ntm_revenue_musd
D.loc[a, "ev_ntm_adj_ebitda_x"] = r.ev_musd / (r.ntm_revenue_musd * r.adj_ebitda_margin_pct / 100)
D.loc[a, "ev_ntm_fcf_x"] = r.ev_musd / (r.ntm_revenue_musd * r.fcf_margin_pct / 100)
D.loc[a, "ev_ntm_sbc_adj_fcf_x"] = r.ev_musd / (r.ntm_revenue_musd * (r.fcf_margin_pct - r.sbc_pct_rev) / 100)
D.loc[a, "gaap_ebitda_margin_pct"] = r.adj_ebitda_margin_pct - r.sbc_pct_rev
D.loc[a, "ltm_gaap_ebitda_musd"] = r.ltm_adj_ebitda_musd - r.ltm_sbc_musd
D.loc[a, "ev_ltm_gaap_ebitda_x"] = r.ev_musd / (r.ltm_adj_ebitda_musd - r.ltm_sbc_musd)
D.loc[a, "ev_ntm_gaap_ebitda_x"] = r.ev_musd / (r.ntm_revenue_musd * (r.adj_ebitda_margin_pct - r.sbc_pct_rev) / 100)
D.loc[a, "rule_of_40"] = r.ntm_revenue_growth_pct + r.fcf_margin_pct; D.loc[a, "rule_of_40_sbc_adj"] = r.ntm_revenue_growth_pct + r.fcf_margin_pct - r.sbc_pct_rev
D.to_csv(os.path.join(OUT, "12_peer_multiples.csv"), index=False, float_format="%.3f")

# ------------------------------------------------------------- cross-sectional fits (ABNB excluded from the fit, then placed on the line)
peers = D[(D.ticker != "ABNB")].copy()
fits = []
def fit(y, xs, label, logy=True, sample=None):
    d = (sample if sample is not None else peers)[[y] + xs + ["ticker"]].replace([np.inf, -np.inf], np.nan).dropna()
    d = d[d[y] > 0]
    if "fcf" in y: d = d[d[y] < 150]  # drops names whose LTM FCF is near zero or negative (AMZN capex cycle, H)
    Y = np.log(d[y]) if logy else d[y]
    X = sm.add_constant(d[xs]); m = sm.OLS(Y, X).fit(cov_type="HC1")
    ab = D[D.ticker == "ABNB"].iloc[0]
    xa = np.array([1.0] + [ab[x] for x in xs])
    pred_abnb = float(np.exp(xa @ m.params.values)) if logy else float(xa @ m.params.values)
    out = dict(fit=label, dependent=y, regressors="+".join(xs), n=int(m.nobs), r2=m.rsquared, log_dependent=logy,
               abnb_actual=ab[y], abnb_fitted=pred_abnb, abnb_premium_pct=100 * (ab[y] / pred_abnb - 1))
    for x in ["const"] + xs: out[f"b_{x}"] = m.params[x]; out[f"t_{x}"] = m.tvalues[x]
    # loo: drop each peer, refit, ABNB fitted range
    preds = []
    for tk in d.ticker:
        dd = d[d.ticker != tk]; mm = sm.OLS(np.log(dd[y]) if logy else dd[y], sm.add_constant(dd[xs])).fit()
        preds.append(float(np.exp(xa @ mm.params.values)) if logy else float(xa @ mm.params.values))
    out["abnb_fitted_loo_min"] = min(preds); out["abnb_fitted_loo_max"] = max(preds)
    return out, m

# scenario fundamentals for FY27E from the driver model (growth is FY27 revenue growth; margin FY27 adj. EBITDA; SBC % rev; FCF conversion)
sc = pd.read_csv(P("data", "processed", "abnb_valuation_scenarios.csv"))
sc27 = sc[sc.period == "FY2027E"].set_index("scenario")
scen = {s: dict(ntm_revenue_growth_pct=sc27.loc[s, "rev_growth_pct"], adj_ebitda_margin_pct=sc27.loc[s, "adj_ebitda_margin_pct"],
                sbc_pct_rev=sc27.loc[s, "sbc_pct_rev"], fcf_conversion_pct=100 * sc27.loc[s, "fcf_musd"] / sc27.loc[s, "adj_ebitda_musd"],
                fcf_margin_pct=sc27.loc[s, "fcf_margin_pct"]) for s in ["Bear", "Base", "Bull"]}
for s in scen:
    scen[s]["rule_of_40"] = scen[s]["ntm_revenue_growth_pct"] + scen[s]["fcf_margin_pct"]
    scen[s]["rule_of_40_sbc_adj"] = scen[s]["rule_of_40"] - scen[s]["sbc_pct_rev"]
    scen[s]["gaap_ebitda_margin_pct"] = scen[s]["adj_ebitda_margin_pct"] - scen[s]["sbc_pct_rev"]

peers["gaap_ebitda_margin_pct"] = peers["gaap_ebitda_margin_pct"]
SPECS = [
    ("ev_ntm_adj_ebitda_x", ["ntm_revenue_growth_pct"], "all peers"),
    ("ev_ntm_adj_ebitda_x", ["rule_of_40"], "all peers"),
    ("ev_ntm_adj_ebitda_x", ["ntm_revenue_growth_pct", "adj_ebitda_margin_pct"], "all peers"),
    ("ev_ntm_adj_ebitda_x", ["ntm_revenue_growth_pct", "adj_ebitda_margin_pct", "sbc_pct_rev", "fcf_conversion_pct"], "all peers"),
    ("ev_ntm_gaap_ebitda_x", ["ntm_revenue_growth_pct", "gaap_ebitda_margin_pct"], "all peers, SBC-burdened EBITDA"),
    ("ev_ntm_fcf_x", ["ntm_revenue_growth_pct"], "all peers"),
    ("ev_ntm_fcf_x", ["ntm_revenue_growth_pct", "fcf_margin_pct", "sbc_pct_rev"], "all peers"),
    ("ev_ntm_sbc_adj_fcf_x", ["ntm_revenue_growth_pct"], "all peers, SBC-adjusted FCF"),
    ("ev_ntm_sbc_adj_fcf_x", ["rule_of_40_sbc_adj"], "all peers, SBC-adjusted FCF"),
    ("pe_ntm_x", ["ntm_revenue_growth_pct"], "all peers"),
    # EV / NTM revenue on growth + margin. This is the spec to use when the question is "what is a higher-margin ABNB
    # worth"; regressing EV/EBITDA on the margin loads a mechanical -1/margin term (a higher margin makes the EBITDA
    # denominator bigger at unchanged EV/revenue), so that spec measures the artefact, not the market's view of margin.
    ("ev_ntm_revenue_x", ["ntm_revenue_growth_pct", "adj_ebitda_margin_pct"], "all peers, EV/NTM revenue"),
    ("ev_ntm_revenue_x", ["ntm_revenue_growth_pct"], "all peers, EV/NTM revenue"),
]
frows = []
travel = peers[peers.group.isin(["OTA", "Hotel franchisor", "Marketplace"])]
for y, xs, label in SPECS:
    for samp, sname in [(peers, f"all {len(peers)} peers"), (travel, f"travel + marketplace ({len(travel)})")]:
        try:
            o, m = fit(y, xs, f"{label} | {sname}", sample=samp)
        except Exception as ex:
            print("fit failed", y, xs, sname, ex); continue
        for s, fv in scen.items():
            xa = np.array([1.0] + [fv.get(x, np.nan) for x in xs])
            o[f"implied_{s.lower()}_fy27"] = float(np.exp(xa @ m.params.values))
        frows.append(o)
F = pd.DataFrame(frows)
F.to_csv(os.path.join(OUT, "12_peer_regressions.csv"), index=False, float_format="%.3f")

# ------------------------------------------------------------- figure
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
cols = {"ABNB": "#c00000", "OTA": "#1f4e79", "Marketplace": "#2e75b6", "Mega-cap internet": "#7f7f7f", "Subscription": "#548235", "Hotel franchisor": "#c55a11"}
for a, y, yl in zip(ax, ["ev_ntm_adj_ebitda_x", "ev_ntm_sbc_adj_fcf_x"], ["EV / NTM adj. EBITDA (x, LTM margin held)", "EV / NTM SBC-adjusted FCF (x)"]):
    d = D[[y, "ntm_revenue_growth_pct", "ticker", "group"]].replace([np.inf, -np.inf], np.nan).dropna()
    d = d[(d[y] > 0) & (d[y] < 80)]
    for _, r in d.iterrows():
        a.scatter(r.ntm_revenue_growth_pct, r[y], color=cols[r.group], s=40 if r.ticker != "ABNB" else 90, zorder=3)
        a.annotate(r.ticker, (r.ntm_revenue_growth_pct, r[y]), fontsize=8, xytext=(3, 3), textcoords="offset points")
    dd = d[d.ticker != "ABNB"]; m = np.polyfit(dd.ntm_revenue_growth_pct, np.log(dd[y]), 1)
    xx = np.linspace(dd.ntm_revenue_growth_pct.min(), dd.ntm_revenue_growth_pct.max(), 50); a.plot(xx, np.exp(m[1] + m[0] * xx), color="k", lw=0.8, ls="--")
    a.set_xlabel("NTM consensus revenue growth %"); a.set_ylabel(yl); a.set_yscale("log")
for g, c in cols.items(): ax[0].scatter([], [], color=c, label=g)
ax[0].legend(frameon=False, fontsize=8)
plt.suptitle("Cross-section, 4 Sep 2026 prices: multiple vs consensus growth (dashed = log-linear fit ex ABNB)")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_peer_crosssection.png"), dpi=150); plt.close()

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
print(D[["ticker", "group", "market_cap_musd", "ev_musd", "ltm_revenue_musd", "ntm_revenue_growth_pct", "adj_ebitda_margin_pct", "sbc_pct_rev", "fcf_margin_pct", "fcf_conversion_pct", "net_cash_pct_mcap", "buyback_yield_pct", "ev_ntm_adj_ebitda_x", "ev_ntm_gaap_ebitda_x", "ev_ntm_fcf_x", "ev_ntm_sbc_adj_fcf_x", "pe_ntm_x"]].round(1).to_string())
print(D[["ticker", "sources"]].to_string())
print(F[["fit", "dependent", "regressors", "n", "r2", "abnb_actual", "abnb_fitted", "abnb_premium_pct", "abnb_fitted_loo_min", "abnb_fitted_loo_max", "implied_bear_fy27", "implied_base_fy27", "implied_bull_fy27"]].round(2).to_string())
