"""Regress ABNB's post-print stock move on each earnings item: consensus surprise, a beat dummy, and y/y growth.

Dependent variables (all 23 prints, Q4 2020 to Q2 2026):
  ret_1d      close-to-close return on the reaction day (prints are after the close)
  exc_1d      the same less QQQ
  ret_5d      close-to-close over the next 5 sessions from the pre-print close
  exc_5d      the same less QQQ
Independent variables per item (revenue, EPS, GBV, nights, Adjusted EBITDA, ADR, margin, take rate, next-quarter guide):
  surprise    actual vs consensus, % (EPS in $ per share because the % base is near zero in early quarters)
  beat        1 if surprise above the threshold used on the Earnings sheet (0.5% rev/EBITDA/GBV, 1% nights, $0.03 EPS), else 0
  growth      reported y/y growth of the item (margin: y/y change in points; take rate: y/y change in points)
  accel       change in y/y growth vs the prior quarter (nights, revenue)
Each regression is univariate OLS on the prints where both sides exist; n, slope, t, p, R2, and mean return for beat vs not.
Also a few bivariate specs. No leave-one-out or walk-forward here: this is the descriptive table the user asked for.

Outputs:
  data/processed/abnb_earnings_regression_panel.csv   the pairs used
  data/processed/abnb_earnings_regressions.csv        the results
Run: py -3.13 analysis/src/abnb_earnings_regressions.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT_PANEL = ROOT / "data/processed/abnb_earnings_regression_panel.csv"
OUT_RES = ROOT / "data/processed/abnb_earnings_regressions.csv"


def q_from_iso(iso: str) -> str:  # 2021Q4 -> 4Q21
    return f"{iso[5]}Q{iso[2:4]}"


def build_panel() -> pd.DataFrame:
    kpi = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv").set_index("quarter")
    cons = pd.read_csv(ROOT / "data/processed/overnight/16_consensus_at_print_merged.csv")
    react = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv").set_index("quarter")
    prices = pd.read_csv(ROOT / "data/processed/overnight/09_prices_daily.csv").set_index("Date")
    execr = pd.read_csv(ROOT / "data/processed/overnight/20_executable_returns.csv").set_index("print_quarter")

    rows = []
    quarters = list(kpi.index)
    for _, c in cons.iterrows():
        iso = c.print_quarter
        q = q_from_iso(iso)
        k = kpi.loc[q]
        i = quarters.index(q)
        prev = kpi.loc[quarters[i - 1]] if i >= 1 else None
        prev4 = kpi.loc[quarters[i - 4]] if i >= 4 else None
        x = react.loc[iso]
        d = dict(print_quarter=iso, quarter=q, print_date=c.print_date)
        # returns
        d["ret_1d"] = x.abnb_1d_pct
        d["exc_1d"] = x.excess_1d_pct
        d["ret_5d"] = x.abnb_5d_pct
        d["exc_5d"] = x.excess_5d_pct
        if pd.isna(d["ret_5d"]) and iso in execr.index:  # fill from prices if the reactions file is short
            e = execr.loc[iso]
            if e.pre_close_date in prices.index and e.exit_date_5d in prices.index:
                a = prices.loc[e.exit_date_5d, "ABNB"] / prices.loc[e.pre_close_date, "ABNB"] - 1
                qq = prices.loc[e.exit_date_5d, "QQQ"] / prices.loc[e.pre_close_date, "QQQ"] - 1
                d["ret_5d"], d["exc_5d"] = a * 100, (a - qq) * 100
        # surprises
        d["rev_surprise"] = c.revenue_surprise_pct
        d["nights_surprise"] = c.nights_surprise_pct
        d["gbv_surprise"] = c.gbv_surprise_pct
        d["ebitda_surprise"] = c.ebitda_surprise_pct
        d["adr_surprise"] = (c.actual_gbv_busd * 1000 / c.actual_nights_m / c.cons_adr - 1) * 100 if pd.notna(c.cons_adr) else np.nan
        d["eps_surprise_usd"] = (c.actual_eps_usd - c.cons_eps_usd) if (c.eps_comparable == 1 and pd.notna(c.cons_eps_usd)) else np.nan
        d["eps_surprise_pct"] = c.eps_surprise_pct if c.eps_comparable == 1 else np.nan
        d["guide_vs_street"] = c.guide_vs_street_pct
        # beat dummies (same thresholds as the Earnings sheet)
        d["rev_beat"] = np.nan if pd.isna(d["rev_surprise"]) else float(d["rev_surprise"] > 0.5)
        d["nights_beat"] = np.nan if pd.isna(d["nights_surprise"]) else float(d["nights_surprise"] > 1.0)
        d["gbv_beat"] = np.nan if pd.isna(d["gbv_surprise"]) else float(d["gbv_surprise"] > 0.5)
        d["ebitda_beat"] = np.nan if pd.isna(d["ebitda_surprise"]) else float(d["ebitda_surprise"] > 0.5)
        d["eps_beat"] = np.nan if pd.isna(d["eps_surprise_usd"]) else float(d["eps_surprise_usd"] > 0.03)
        d["guide_below_street"] = np.nan if pd.isna(d["guide_vs_street"]) else float(d["guide_vs_street"] < 0)
        # growth (reported y/y)
        d["rev_growth"] = k.revenue_yoy_reported_pct
        d["nights_growth"] = k.nights_yoy_pct
        d["gbv_growth"] = k.gbv_yoy_pct
        d["adr_growth"] = k.adr_yoy_pct
        d["ebitda_growth"] = (k.adj_ebitda_musd / prev4.adj_ebitda_musd - 1) * 100 if prev4 is not None and prev4.adj_ebitda_musd > 0 else np.nan
        d["margin_change_pts"] = (k.adj_ebitda_margin_pct - prev4.adj_ebitda_margin_pct) if prev4 is not None else np.nan
        d["take_rate_change_pts"] = (k.take_rate_pct - prev4.take_rate_pct) if prev4 is not None else np.nan
        d["nights_accel_pts"] = (k.nights_yoy_pct - prev.nights_yoy_pct) if prev is not None and pd.notna(prev.nights_yoy_pct) else np.nan
        d["rev_accel_pts"] = (k.revenue_yoy_reported_pct - prev.revenue_yoy_reported_pct) if prev is not None and pd.notna(prev.revenue_yoy_reported_pct) else np.nan
        # EPS growth on the adjusted basis only, both quarters positive
        prev_iso = cons[cons.print_quarter == f"{int(iso[:4]) - 1}{iso[4:]}"]
        if (c.eps_comparable == 1 and not prev_iso.empty and prev_iso.iloc[0].eps_comparable == 1
                and "adjusted" in str(c.eps_basis) and "adjusted" in str(prev_iso.iloc[0].eps_basis)
                and prev_iso.iloc[0].actual_eps_usd > 0):
            d["eps_growth"] = (c.actual_eps_usd / prev_iso.iloc[0].actual_eps_usd - 1) * 100
        else:
            d["eps_growth"] = np.nan
        rows.append(d)
    return pd.DataFrame(rows)


ITEMS = [
    # item, feature column, feature label, kind
    ("Revenue", "rev_surprise", "surprise vs consensus (%)", "surprise"),
    ("Revenue", "rev_beat", "beat consensus (1/0, >0.5%)", "dummy"),
    ("Revenue", "rev_growth", "y/y growth (%)", "growth"),
    ("Revenue", "rev_accel_pts", "acceleration vs prior quarter (pts)", "growth"),
    ("EPS", "eps_surprise_usd", "surprise vs consensus ($/share)", "surprise"),
    ("EPS", "eps_beat", "beat consensus (1/0, >$0.03)", "dummy"),
    ("EPS", "eps_growth", "y/y growth, adjusted basis (%)", "growth"),
    ("GBV", "gbv_surprise", "surprise vs consensus (%)", "surprise"),
    ("GBV", "gbv_beat", "beat consensus (1/0, >0.5%)", "dummy"),
    ("GBV", "gbv_growth", "y/y growth (%)", "growth"),
    ("Nights", "nights_surprise", "surprise vs consensus (%)", "surprise"),
    ("Nights", "nights_beat", "beat consensus (1/0, >1%)", "dummy"),
    ("Nights", "nights_growth", "y/y growth (%)", "growth"),
    ("Nights", "nights_accel_pts", "acceleration vs prior quarter (pts)", "growth"),
    ("Adj. EBITDA", "ebitda_surprise", "surprise vs consensus (%)", "surprise"),
    ("Adj. EBITDA", "ebitda_beat", "beat consensus (1/0, >0.5%)", "dummy"),
    ("Adj. EBITDA", "ebitda_growth", "y/y growth (%)", "growth"),
    ("Adj. EBITDA margin", "margin_change_pts", "y/y change (pts)", "growth"),
    ("ADR", "adr_surprise", "surprise vs consensus (%)", "surprise"),
    ("ADR", "adr_growth", "y/y growth (%)", "growth"),
    ("Take rate", "take_rate_change_pts", "y/y change (pts)", "growth"),
    ("Next-quarter revenue guide", "guide_vs_street", "guide midpoint vs Street (%)", "surprise"),
    ("Next-quarter revenue guide", "guide_below_street", "guide below Street (1/0)", "dummy"),
]
DEPS = [("ret_1d", "Day 1, raw"), ("exc_1d", "Day 1, excess vs QQQ"), ("ret_5d", "5 sessions, raw"), ("exc_5d", "5 sessions, excess vs QQQ")]


WINDOWS = [("all prints", lambda p: p), ("2023 onward", lambda p: p[p.print_quarter >= "2023Q1"])]


def univariate(panel: pd.DataFrame) -> pd.DataFrame:
    out = []
    for win, sel in WINDOWS:
      sub = sel(panel)
      for item, col, label, kind in ITEMS:
        for dep, dep_label in DEPS:
            d = sub[[col, dep]].dropna()
            n = len(d)
            rec = dict(item=item, feature=label, horizon=dep_label, window=win, n=n)
            if n >= 6 and d[col].nunique() > 1:
                X = sm.add_constant(d[col].values)
                m = sm.OLS(d[dep].values, X).fit()
                rec.update(slope=m.params[1], intercept=m.params[0], t=m.tvalues[1], p=m.pvalues[1], r2=m.rsquared)
                rho, rp = stats.spearmanr(d[col], d[dep])
                rec.update(spearman=rho, spearman_p=rp)
                if kind == "dummy":
                    a = d.loc[d[col] == 1, dep]
                    b = d.loc[d[col] == 0, dep]
                    rec.update(mean_ret_if_1=a.mean(), n_1=len(a), mean_ret_if_0=b.mean(), n_0=len(b),
                               share_positive_if_1=(a > 0).mean() if len(a) else np.nan,
                               share_positive_if_0=(b > 0).mean() if len(b) else np.nan)
                    if len(a) >= 2 and len(b) >= 2:
                        rec["welch_p"] = stats.ttest_ind(a, b, equal_var=False).pvalue
                else:
                    # sign concordance: share of prints where feature and return have the same sign (feature demeaned for growth)
                    f = d[col] - (d[col].median() if kind == "growth" else 0)
                    rec["sign_agreement"] = (np.sign(f) == np.sign(d[dep])).mean()
            out.append(rec)
    return pd.DataFrame(out)


BIVARIATE = [
    ("Revenue surprise + nights growth", ["rev_surprise", "nights_growth"]),
    ("Nights surprise + nights acceleration", ["nights_surprise", "nights_accel_pts"]),
    ("Revenue beat + guide below Street", ["rev_beat", "guide_below_street"]),
    ("EPS surprise ($) + revenue surprise", ["eps_surprise_usd", "rev_surprise"]),
    ("Nights growth + margin change", ["nights_growth", "margin_change_pts"]),
]


def bivariate(panel: pd.DataFrame) -> pd.DataFrame:
    out = []
    for win, sel in WINDOWS:
      sub = sel(panel)
      for label, cols in BIVARIATE:
        for dep, dep_label in DEPS:
            d = sub[cols + [dep]].dropna()
            n = len(d)
            rec = dict(item="Bivariate", feature=label, horizon=dep_label, window=win, n=n)
            if n >= 8:
                X = sm.add_constant(d[cols].values)
                m = sm.OLS(d[dep].values, X).fit()
                rec.update(slope=m.params[1], t=m.tvalues[1], p=m.pvalues[1], slope_2=m.params[2], t_2=m.tvalues[2], p_2=m.pvalues[2],
                           r2=m.rsquared, adj_r2=m.rsquared_adj)
            out.append(rec)
    return pd.DataFrame(out)


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = build_panel()
    res = pd.concat([univariate(panel), bivariate(panel)], ignore_index=True)
    panel.to_csv(OUT_PANEL, index=False)
    res.round(4).to_csv(OUT_RES, index=False)
    return panel, res


if __name__ == "__main__":
    panel, res = run()
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 200)
    cols = ["item", "feature", "horizon", "window", "n", "slope", "t", "p", "r2", "mean_ret_if_1", "mean_ret_if_0", "welch_p", "sign_agreement"]
    print(res[[c for c in cols if c in res.columns]].round(3).to_string())
    print("wrote", OUT_PANEL, OUT_RES)
