"""43a_sm_evidence: the statistics behind Thesis 3 (sales & marketing).

Pre-registered in docs/margin-build/notes/43a_prereg.md (written before this file existed).
Run from the repo root:  py -3.13 -X utf8 analysis/src/margin_build/43a_sm_evidence/run.py
Writes data/processed/margin_build/43a_sm_evidence/*.csv and exits 0.

Nothing here is a forecast. Every number is a description of the printed history, and every test carries its n.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
OUT = ROOT / "data/processed/margin_build/43a_sm_evidence"
OUT.mkdir(parents=True, exist_ok=True)
PANEL = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
TENQ = ROOT / "docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq"
TENK = Path("C:/Users/krish/citadel-abnb/data/raw/filings")  # main tree, read-only; optional (verification only)
REGIONAL = ROOT / "data/processed/adr/04_regional_quarterly_wide.csv"

W = {"J": ("1Q22", "2Q26"), "W1": ("1Q23", "2Q26"), "W2": ("1Q24", "2Q26")}


def qi(q: str) -> int:
    return int(q[2:]) * 4 + int(q[0]) - 1


def in_win(q: str, w: str) -> bool:
    a, b = W[w]
    return qi(a) <= qi(q) <= qi(b)


def hac(y, X, lags, one_sided_col=None, alt="greater"):
    m = sm.OLS(np.asarray(y, float), np.asarray(X, float)).fit(cov_type="HAC", cov_kwds={"maxlags": lags, "use_correction": True})
    return m


def one_sided_p(t, df, alt="greater"):
    return float(stats.t.sf(t, df)) if alt == "greater" else float(stats.t.cdf(t, df))


# --------------------------------------------------------------------------------------------------------------------
# 0. Panel
# --------------------------------------------------------------------------------------------------------------------
p = pd.read_csv(PANEL)
p = p[p.quarter.str.match(r"^[1-4]Q\d\d$")].copy()
p["qi"] = p.quarter.map(qi)
p = p.sort_values("qi").reset_index(drop=True)
p["qn"] = p.quarter.str[0].astype(int)
p["year"] = 2000 + p.quarter.str[2:].astype(int)
p["t"] = np.arange(len(p))
LINES = {"sm_cash": "Sales & marketing", "cor_cash": "Cost of revenue", "ops_cash": "Ops & support", "pd_cash": "Product dev.", "ga_cash": "G&A"}
for c in ["sm_cash", "revenue", "nights_m", "cor_cash", "ops_cash", "pd_cash", "ga_cash"]:
    p[f"g_{c}"] = np.log(p[c] / p[c].shift(4))
p["g_sm"], p["g_rev"], p["g_nights"] = p.g_sm_cash, p.g_revenue, p.g_nights_m
p["d_gap"] = p.g_sm - p.g_rev
for c in ["sm_cash", "revenue", "nights_m", "sm_gaap"]:
    p[f"{c}_t4"] = p[c].rolling(4).sum()


def win(df, w):
    return df[df.quarter.map(lambda q: in_win(q, w))].copy()


# --------------------------------------------------------------------------------------------------------------------
# H1. The levels regression (Jessie's 1.41) and what it is
# --------------------------------------------------------------------------------------------------------------------
def levels_reg(df, ycol, add_trend=False, lags=2):
    X = pd.DataFrame({"const": 1.0, "log_rev": np.log(df.revenue)})
    for k in (2, 3, 4):
        X[f"q{k}"] = (df.qn == k).astype(float)
    if add_trend:
        X["t"] = df.t.astype(float) - df.t.iloc[0]
    y = np.log(df[ycol])
    m = hac(y, X, lags)
    ols = sm.OLS(np.asarray(y, float), np.asarray(X, float)).fit()
    r = ols.resid
    ar1 = float(np.corrcoef(r[1:], r[:-1])[0, 1])
    bg = acorr_breusch_godfrey(ols, nlags=2)
    try:
        adf_p = float(adfuller(r, maxlag=1, regression="n", autolag=None)[1])
    except Exception:
        adf_p = np.nan
    b, se = float(m.params[1]), float(m.bse[1])
    return dict(coef=b, se_hac=se, t=b / se, ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se, p_two_sided=float(m.pvalues[1]),
                r2=float(ols.rsquared), dw=float(durbin_watson(r)), resid_ar1=ar1, bg_p_lag2=float(bg[1]), adf_resid_p=adf_p, n=int(len(df)),
                trend_coef=(float(m.params[-1]) if add_trend else np.nan), trend_t=(float(m.params[-1] / m.bse[-1]) if add_trend else np.nan))


def trend_reg(df, col):
    X = pd.DataFrame({"const": 1.0, "t": df.t.astype(float) - df.t.iloc[0]})
    for k in (2, 3, 4):
        X[f"q{k}"] = (df.qn == k).astype(float)
    m = hac(np.log(df[col]), X, 2)
    return float(m.params[1]), float(m.bse[1])


rows = []
J = win(p, "J")
for col, name in LINES.items():
    r = levels_reg(J, col)
    rows.append(dict(sample="J 1Q22-2Q26", line=name, spec="log(line) ~ log(rev) + q dummies", **r))
for w in ("W1", "W2"):
    r = levels_reg(win(p, w), "sm_cash")
    rows.append(dict(sample=w, line="Sales & marketing", spec="log(line) ~ log(rev) + q dummies", **r))
for w in ("J", "W1", "W2"):
    r = levels_reg(win(p, w), "sm_cash", add_trend=True)
    rows.append(dict(sample=w, line="Sales & marketing", spec="log(line) ~ log(rev) + t + q dummies", **r))
h1 = pd.DataFrame(rows)
# trend ratio
tr = []
for w in ("J", "W1", "W2"):
    d = win(p, w)
    bs, ss = trend_reg(d, "sm_cash")
    br, sr = trend_reg(d, "revenue")
    lev = float(h1[(h1["sample"].str.startswith(w)) & (h1.line == "Sales & marketing") & (~h1.spec.str.contains("+ t", regex=False))].coef.iloc[0])
    tr.append(dict(sample=w, n=len(d), trend_sm_per_q=bs, trend_sm_se=ss, trend_rev_per_q=br, trend_rev_se=sr, trend_ratio=bs / br,
                   levels_elasticity=lev, diff=lev - bs / br, within_0p15=abs(lev - bs / br) <= 0.15))
h1b = pd.DataFrame(tr)
h1.to_csv(OUT / "43a_h1_levels_elasticity.csv", index=False)
h1b.to_csv(OUT / "43a_h1b_trend_ratio.csv", index=False)

# --------------------------------------------------------------------------------------------------------------------
# H2. Growth rates: k, the gap, the CAGR ratio
# --------------------------------------------------------------------------------------------------------------------
rows, gaps = [], []
for w in ("J", "W1", "W2"):
    d = win(p, w).dropna(subset=["g_sm", "g_rev"])
    X = pd.DataFrame({"const": 1.0, "g_rev": d.g_rev})
    m = hac(d.g_sm, X, 3)
    rows.append(dict(sample=w, n=len(d), spec="g_sm ~ c + k g_rev (y/y logs, HAC3)", c=float(m.params[0]), c_se=float(m.bse[0]),
                     k=float(m.params[1]), k_se=float(m.bse[1]), k_t=float(m.params[1] / m.bse[1]), k_ci_lo=float(m.params[1] - 1.96 * m.bse[1]),
                     k_ci_hi=float(m.params[1] + 1.96 * m.bse[1]), r2=float(sm.OLS(np.asarray(d.g_sm), np.asarray(X)).fit().rsquared)))
    g = d.d_gap.values
    mg = hac(g, np.ones((len(g), 1)), 3)
    tstat = float(mg.params[0] / mg.bse[0])
    npos = int((g > 0).sum())
    gaps.append(dict(sample=w, n=len(g), mean_gap_logpts=float(g.mean()), mean_gap_pp=float(100 * (np.exp(g.mean()) - 1)), hac_se=float(mg.bse[0]), t=tstat,
                     p_one_sided=one_sided_p(tstat, len(g) - 1), n_positive=npos, sign_p=float(stats.binomtest(npos, len(g), 0.5, alternative="greater").pvalue),
                     median_gap_logpts=float(np.median(g)), min_gap=float(g.min()), max_gap=float(g.max())))
h2a, h2b = pd.DataFrame(rows), pd.DataFrame(gaps)
req = {"W1": 10, "W2": 7}
h2b["pass_line"] = [(r.p_one_sided <= 0.10 and r.n_positive >= req.get(r["sample"], 0)) if r["sample"] in req else np.nan for _, r in h2b.iterrows()]
h2a.to_csv(OUT / "43a_h2a_growth_elasticity.csv", index=False)
h2b.to_csv(OUT / "43a_h2b_growth_gap.csv", index=False)

fy = p.groupby("year").agg(revenue=("revenue", "sum"), sm_cash=("sm_cash", "sum"), sm_gaap=("sm_gaap", "sum"), nights_m=("nights_m", "sum"), sbc_sm=("sbc_sm", "sum"), n=("quarter", "count"))
fy = fy[fy.n == 4]
h1s = p[p.qn <= 2].groupby("year").agg(revenue=("revenue", "sum"), sm_cash=("sm_cash", "sum"), sm_gaap=("sm_gaap", "sum"), nights_m=("nights_m", "sum"), sbc_sm=("sbc_sm", "sum"))


def cagr_row(label, a, b, yrs, base, end):
    rs, rr = (end.sm_cash / base.sm_cash) ** (1 / yrs) - 1, (end.revenue / base.revenue) ** (1 / yrs) - 1
    return dict(span=label, years=yrs, sm_cash_start=base.sm_cash, sm_cash_end=end.sm_cash, rev_start=base.revenue, rev_end=end.revenue,
                sm_cagr_pct=100 * rs, rev_cagr_pct=100 * rr, cagr_ratio=rs / rr, log_growth_ratio=np.log(end.sm_cash / base.sm_cash) / np.log(end.revenue / base.revenue),
                gap_pp_per_year=100 * (rs - rr))


h2c = pd.DataFrame([
    cagr_row("FY22->FY25", 2022, 2025, 3, fy.loc[2022], fy.loc[2025]),
    cagr_row("FY23->FY25", 2023, 2025, 2, fy.loc[2023], fy.loc[2025]),
    cagr_row("FY24->FY25", 2024, 2025, 1, fy.loc[2024], fy.loc[2025]),
    cagr_row("1H24->1H26", 2024, 2026, 2, h1s.loc[2024], h1s.loc[2026]),
    cagr_row("1H25->1H26", 2025, 2026, 1, h1s.loc[2025], h1s.loc[2026]),
    cagr_row("FY19->FY25", 2019, 2025, 6, fy.loc[2019], fy.loc[2025]),
])
h2c.to_csv(OUT / "43a_h2c_cagr_ratio.csv", index=False)
# the same CAGR comparison for every cash cost line (the memo's cross-line sentence, restated in growth terms)
fyl = p.groupby("year")[["revenue", "sm_cash", "cor_cash", "ops_cash", "pd_cash", "ga_cash_ex_lodging", "total_cash_costs"]].sum()
lines_cagr = []
for col in ["revenue", "sm_cash", "cor_cash", "ops_cash", "pd_cash", "ga_cash_ex_lodging", "total_cash_costs"]:
    for a, b in ((2022, 2025), (2023, 2025)):
        g = (fyl.loc[b, col] / fyl.loc[a, col]) ** (1 / (b - a)) - 1
        gr = (fyl.loc[b, "revenue"] / fyl.loc[a, "revenue"]) ** (1 / (b - a)) - 1
        lines_cagr.append(dict(line=col, span=f"FY{a % 100}->FY{b % 100}", start=fyl.loc[a, col], end=fyl.loc[b, col], cagr_pct=100 * g, rev_cagr_pct=100 * gr, cagr_ratio=g / gr,
                               pct_rev_start=100 * fyl.loc[a, col] / fyl.loc[a, "revenue"], pct_rev_end=100 * fyl.loc[b, col] / fyl.loc[b, "revenue"]))
h2c_lines = pd.DataFrame(lines_cagr)
h2c_lines.to_csv(OUT / "43a_h2c_cagr_all_lines.csv", index=False)

# --------------------------------------------------------------------------------------------------------------------
# H3. Acceleration: trailing-4Q measures on time
# --------------------------------------------------------------------------------------------------------------------
p["share_t4"] = p.sm_cash_t4 / p.revenue_t4
p["inc_sm_per_rev_t4"] = (p.sm_cash_t4 - p.sm_cash_t4.shift(4)) / (p.revenue_t4 - p.revenue_t4.shift(4))
p["gap_t4"] = np.log(p.sm_cash_t4 / p.sm_cash_t4.shift(4)) - np.log(p.revenue_t4 / p.revenue_t4.shift(4))
p["rev_per_sm_t4"] = 1 / p.inc_sm_per_rev_t4
p["nights_per_smusd_t4"] = (p.nights_m_t4 - p.nights_m_t4.shift(4)) / (p.sm_cash_t4 - p.sm_cash_t4.shift(4))
p["g_sm_t4"] = np.log(p.sm_cash_t4 / p.sm_cash_t4.shift(4))
p["g_rev_t4"] = np.log(p.revenue_t4 / p.revenue_t4.shift(4))
p[["quarter", "revenue", "sm_cash", "nights_m", "g_rev", "g_sm", "g_nights", "d_gap", "revenue_t4", "sm_cash_t4", "share_t4", "inc_sm_per_rev_t4", "gap_t4", "rev_per_sm_t4",
   "nights_per_smusd_t4", "g_sm_t4", "g_rev_t4"]].to_csv(OUT / "43a_series_quarterly.csv", index=False)

rows = []
for meas, label, alt in [("share_t4", "(a) S&M cash share of revenue, T4Q", "greater"), ("inc_sm_per_rev_t4", "(b) incremental S&M per incremental revenue $, T4Q y/y", "greater"),
                         ("gap_t4", "(c) growth gap log(sm_T4Q y/y) - log(rev_T4Q y/y)", "greater"), ("rev_per_sm_t4", "(H5c) incremental revenue per incremental S&M $, T4Q y/y", "less"),
                         ("nights_per_smusd_t4", "(H5c) incremental nights (m) per incremental S&M $M, T4Q y/y", "less")]:
    for w in ("W1", "W2"):
        d = win(p, w).dropna(subset=[meas])
        X = pd.DataFrame({"const": 1.0, "t": np.arange(len(d), dtype=float)})
        m = hac(d[meas], X, 3)
        tstat = float(m.params[1] / m.bse[1])
        rows.append(dict(measure=label, window=w, n=len(d), first=d.quarter.iloc[0], last=d.quarter.iloc[-1], start_value=float(d[meas].iloc[0]), end_value=float(d[meas].iloc[-1]),
                         slope_per_q=float(m.params[1]), slope_se=float(m.bse[1]), t=tstat, alternative=alt, p_one_sided=one_sided_p(tstat, len(d) - 2, alt),
                         passes_0p10=one_sided_p(tstat, len(d) - 2, alt) <= 0.10))
h3 = pd.DataFrame(rows)
h3.to_csv(OUT / "43a_h3_acceleration.csv", index=False)

by = []
for y in range(2020, 2026):
    if y - 1 in fy.index and y in fy.index:
        a, b = fy.loc[y - 1], fy.loc[y]
        by.append(dict(period=f"FY{y}", revenue=b.revenue, sm_cash=b.sm_cash, sm_gaap=b.sm_gaap, rev_growth_pct=100 * (b.revenue / a.revenue - 1), sm_cash_growth_pct=100 * (b.sm_cash / a.sm_cash - 1),
                       gap_pp=100 * (b.sm_cash / a.sm_cash - b.revenue / a.revenue), sm_cash_pct_rev=100 * b.sm_cash / b.revenue, d_share_pp=100 * (b.sm_cash / b.revenue - a.sm_cash / a.revenue),
                       inc_sm_per_inc_rev=(b.sm_cash - a.sm_cash) / (b.revenue - a.revenue), inc_rev_per_inc_sm=(b.revenue - a.revenue) / (b.sm_cash - a.sm_cash),
                       inc_nights_m_per_inc_sm_musd=(b.nights_m - a.nights_m) / (b.sm_cash - a.sm_cash), nights_growth_pct=100 * (b.nights_m / a.nights_m - 1)))
for y in (2025, 2026):
    a, b = h1s.loc[y - 1], h1s.loc[y]
    by.append(dict(period=f"1H{y % 100}", revenue=b.revenue, sm_cash=b.sm_cash, sm_gaap=b.sm_gaap, rev_growth_pct=100 * (b.revenue / a.revenue - 1), sm_cash_growth_pct=100 * (b.sm_cash / a.sm_cash - 1),
                   gap_pp=100 * (b.sm_cash / a.sm_cash - b.revenue / a.revenue), sm_cash_pct_rev=100 * b.sm_cash / b.revenue, d_share_pp=100 * (b.sm_cash / b.revenue - a.sm_cash / a.revenue),
                   inc_sm_per_inc_rev=(b.sm_cash - a.sm_cash) / (b.revenue - a.revenue), inc_rev_per_inc_sm=(b.revenue - a.revenue) / (b.sm_cash - a.sm_cash),
                   inc_nights_m_per_inc_sm_musd=(b.nights_m - a.nights_m) / (b.sm_cash - a.sm_cash), nights_growth_pct=100 * (b.nights_m / a.nights_m - 1)))
h3y = pd.DataFrame(by)
h3y.to_csv(OUT / "43a_h3_by_year.csv", index=False)

# --------------------------------------------------------------------------------------------------------------------
# H4. Component split (GAAP, from the filings). Hard-coded with the printed source; verified against the cached filings
# --------------------------------------------------------------------------------------------------------------------
ANNUAL = [  # (FY, brand & performance marketing, field operations & policy, source)
    (2018, 666.455, 434.872, "10-K FY2020 S&M table"), (2019, 1140.366, 481.153, "10-K FY2020/FY2021 S&M table"), (2020, 478.608, 696.717, "10-K FY2020/FY2021 S&M table"),
    (2021, 723.167, 463.165, "10-K FY2021/FY2022 S&M table"), (2022, 1030, 486, "10-K FY2022/FY2023 S&M table"), (2023, 1208, 555, "10-K FY2023/FY2024 S&M table"),
    (2024, 1455, 693, "10-K FY2024/FY2025 S&M table"), (2025, 1595, 993, "10-K FY2025 S&M table")]
QTR = [  # (period, bpm, fop, how)
    ("1Q22", 231, 114, "1H22 (10-Q 2Q23: 513/211) minus 2Q22"), ("2Q22", 282, 97, "10-Q 2Q23 three-month"), ("3Q22", 259, 124, "10-Q 3Q23 three-month"), ("4Q22", 258, 150, "FY22 minus 9M22 (10-Q 3Q23: 772/336)"),
    ("1Q23", 307, 143, "10-Q 1Q24 three-month"), ("2Q23", 361, 125, "10-Q 2Q23/2Q24 three-month"), ("3Q23", 264, 139, "10-Q 3Q23/3Q24 three-month"), ("4Q23", 276, 148, "FY23 minus 9M23 (932/407)"),
    ("1Q24", 370, 144, "10-Q 1Q24/1Q25 three-month"), ("2Q24", 384, 189, "10-Q 2Q24/2Q25 three-month"), ("3Q24", 332, 182, "10-Q 3Q24 three-month"), ("4Q24", 369, 178, "FY24 minus 9M24 (1086/515)"),
    ("1Q25", 378, 185, "10-Q 1Q25 three-month"), ("2Q25", 446, 245, "10-Q 2Q25/2Q26 three-month"), ("2H25", 771, 563, "FY25 minus 1H25 (824/430); 3Q25 10-Q not in repo"),
    ("1Q26", 512, 239, "1H26 (10-Q 2Q26: 1091/535) minus 2Q26"), ("2Q26", 579, 296, "10-Q 2Q26 three-month")]


def parse_split(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", html.unescape(t))
    m = re.search(r"Brand and performance marketing((?: \$ [\d,\.]+)+)", t)
    f = re.search(r"Field operations and policy((?: [\d,\.]+)+)", t[m.start():m.start() + 600]) if m else None
    if not m or not f:
        return None
    b = [float(x.replace(",", "")) for x in re.findall(r"[\d,\.]+", m.group(1))]
    toks = t[m.start() + f.start():m.start() + f.start() + 400].split()[4:]  # after "Field operations and policy"
    v = []
    for i, tok in enumerate(toks):
        if re.fullmatch(r"[\d,\.]+", tok) and (i + 1 >= len(toks) or toks[i + 1] != "%"):
            v.append(float(tok.replace(",", "")))
        else:
            break
    return b, v


verif = []
printed = {"1Q23": ("abnb-20240331.htm", 0), "1Q24": ("abnb-20240331.htm", 1), "1Q25": ("abnb-20250331.htm", 1), "2Q22": ("abnb-20230630.htm", 0), "2Q23": ("abnb-20230630.htm", 1),
           "2Q24": ("abnb-20240630.htm", 1), "2Q25": ("abnb-20250630.htm", 1), "2Q26": ("abnb-20260630.htm", 1), "3Q22": ("abnb-20230930.htm", 0), "3Q23": ("abnb-20230930.htm", 1),
           "3Q24": ("abnb-20240930.htm", 1)}
qd = {q: (b, f) for q, b, f, _ in QTR}
for q, (fn, idx) in printed.items():
    fp = TENQ / fn
    if fp.exists():
        r = parse_split(fp)
        ok = r is not None and abs(r[0][idx] - qd[q][0]) < 0.5 and abs(r[1][idx] - qd[q][1]) < 0.5
        verif.append(dict(period=q, file=fn, parsed_bpm=(r[0][idx] if r else np.nan), parsed_fop=(r[1][idx] if r else np.nan), coded_bpm=qd[q][0], coded_fop=qd[q][1], match=ok))
for y, b, f, _ in ANNUAL:
    fp = TENK / f"abnb_10k_FY{y}.htm"
    if fp.exists():
        r = parse_split(fp)
        if r:
            # the FY's own column is the last printed value (thousands in FY2020/21 10-Ks)
            pb, pf = r[0][-1], r[1][-1]
            if pb > 20000:
                pb, pf = pb / 1000, pf / 1000
            verif.append(dict(period=f"FY{y}", file=fp.name, parsed_bpm=pb, parsed_fop=pf, coded_bpm=b, coded_fop=f, match=abs(pb - b) < 0.6 and abs(pf - f) < 0.6))
verif = pd.DataFrame(verif)
verif.to_csv(OUT / "43a_h4_filing_verification.csv", index=False)
assert verif.match.all(), verif[~verif.match]

# annual component table with panel revenue, nights, SBC
ann = []
for y, b, f, src in ANNUAL:
    if y not in fy.index or y < 2019:  # 2018 has no nights in the panel
        continue
    r = fy.loc[y]
    ann.append(dict(fy=y, revenue=r.revenue, nights_m=r.nights_m, sm_gaap_panel=r.sm_gaap, bpm=b, fop=f, bpm_plus_fop=b + f, sbc_sm=r.sbc_sm, fop_cash_if_all_sbc_in_fop=f - r.sbc_sm,
                    bpm_pct_rev=100 * b / r.revenue, fop_pct_rev=100 * f / r.revenue, bpm_per_night_usd=b / r.nights_m, source=src))
ann = pd.DataFrame(ann)
for c in ("revenue", "nights_m", "bpm", "fop", "sm_gaap_panel"):
    ann[f"{c}_yoy_pct"] = 100 * (ann[c] / ann[c].shift(1) - 1)
ann["bpm_contrib_to_sm_growth_pp"] = 100 * (ann.bpm - ann.bpm.shift(1)) / ann.sm_gaap_panel.shift(1)
ann["fop_contrib_to_sm_growth_pp"] = 100 * (ann.fop - ann.fop.shift(1)) / ann.sm_gaap_panel.shift(1)
ann["sm_minus_rev_growth_pp"] = ann.sm_gaap_panel_yoy_pct - ann.revenue_yoy_pct
ann["inc_nights_m_per_inc_bpm_musd"] = (ann.nights_m - ann.nights_m.shift(1)) / (ann.bpm - ann.bpm.shift(1))
ann["inc_rev_per_inc_bpm"] = (ann.revenue - ann.revenue.shift(1)) / (ann.bpm - ann.bpm.shift(1))
ann["split_check_gap"] = ann.bpm_plus_fop - ann.sm_gaap_panel
assert ann.split_check_gap.abs().max() < 2.0, ann[["fy", "split_check_gap"]]
ann.to_csv(OUT / "43a_h4_components_annual.csv", index=False)

# half-year rows (1H24, 1H25, 1H26) from the quarterly table
qt = pd.DataFrame(QTR, columns=["period", "bpm", "fop", "how"])
pan = p.set_index("quarter")


def half(y):
    qs = [f"1Q{y % 100}", f"2Q{y % 100}"]
    b = sum(qd[q][0] for q in qs)
    f = sum(qd[q][1] for q in qs)
    r = pan.loc[qs]
    return dict(period=f"1H{y % 100}", revenue=r.revenue.sum(), nights_m=r.nights_m.sum(), sm_gaap_panel=r.sm_gaap.sum(), bpm=b, fop=f, sbc_sm=r.sbc_sm.sum())


hh = pd.DataFrame([half(y) for y in (2023, 2024, 2025, 2026)])
for c in ("revenue", "nights_m", "bpm", "fop", "sm_gaap_panel"):
    hh[f"{c}_yoy_pct"] = 100 * (hh[c] / hh[c].shift(1) - 1)
hh["bpm_contrib_to_sm_growth_pp"] = 100 * (hh.bpm - hh.bpm.shift(1)) / hh.sm_gaap_panel.shift(1)
hh["fop_contrib_to_sm_growth_pp"] = 100 * (hh.fop - hh.fop.shift(1)) / hh.sm_gaap_panel.shift(1)
hh["sm_minus_rev_growth_pp"] = hh.sm_gaap_panel_yoy_pct - hh.revenue_yoy_pct
hh["bpm_pct_rev"], hh["fop_pct_rev"] = 100 * hh.bpm / hh.revenue, 100 * hh.fop / hh.revenue
hh["inc_nights_m_per_inc_bpm_musd"] = (hh.nights_m - hh.nights_m.shift(1)) / (hh.bpm - hh.bpm.shift(1))
hh["inc_rev_per_inc_bpm"] = (hh.revenue - hh.revenue.shift(1)) / (hh.bpm - hh.bpm.shift(1))
hh["split_check_gap"] = hh.bpm + hh.fop - hh.sm_gaap_panel
assert hh.split_check_gap.abs().max() < 2.0
hh.to_csv(OUT / "43a_h4_components_halfyear.csv", index=False)

# quarterly component table with y/y growth (2H25 kept as one row; y/y for 1Q26/2Q26 use 1Q25/2Q25)
qt["sm_gaap_panel"] = [pan.loc[[q], "sm_gaap"].iloc[0] if q != "2H25" else pan.loc[["3Q25", "4Q25"], "sm_gaap"].sum() for q in qt.period]
qt["revenue"] = [pan.loc[[q], "revenue"].iloc[0] if q != "2H25" else pan.loc[["3Q25", "4Q25"], "revenue"].sum() for q in qt.period]
qt["split_check_gap"] = qt.bpm + qt.fop - qt.sm_gaap_panel
assert qt.split_check_gap.abs().max() < 2.0, qt
qmap = {r.period: r for r in qt.itertuples()}


def yoy(q, col):
    y, n = int(q[2:]), q[0]
    prev = f"{n}Q{y - 1:02d}"
    return 100 * (getattr(qmap[q], col) / getattr(qmap[prev], col) - 1) if prev in qmap else np.nan


qt["bpm_yoy_pct"] = [yoy(q, "bpm") if q != "2H25" else np.nan for q in qt.period]
qt["fop_yoy_pct"] = [yoy(q, "fop") if q != "2H25" else np.nan for q in qt.period]
qt["rev_yoy_pct"] = [yoy(q, "revenue") if q != "2H25" else np.nan for q in qt.period]
qt["bpm_pct_rev"], qt["fop_pct_rev"] = 100 * qt.bpm / qt.revenue, 100 * qt.fop / qt.revenue
qt["g_bpm"] = np.log(1 + qt.bpm_yoy_pct / 100)
qt.to_csv(OUT / "43a_h4_components_quarterly.csv", index=False)

# --------------------------------------------------------------------------------------------------------------------
# H5. Lead/lag with nights; efficiency; regional mix
# --------------------------------------------------------------------------------------------------------------------
def ccf_table(x: pd.Series, y: pd.Series, qs: pd.Series, w: str, xname: str):
    """lead L>0: x at t-L against y at t (x leads y). Pearson on the pairs whose x- and y-dates are both inside window w."""
    out = []
    df = pd.DataFrame({"q": qs.values, "x": x.values, "y": y.values}).reset_index(drop=True)
    for L in range(-4, 5):
        xs = df.x.shift(L)  # positive L: x from L quarters earlier
        pairs = pd.DataFrame({"q": df.q, "qx": df.q.shift(L), "x": xs, "y": df.y}).dropna()
        pairs = pairs[pairs.q.map(lambda q: in_win(q, w)) & pairs.qx.map(lambda q: in_win(q, w))]  # both dates inside the window
        n = len(pairs)
        r = float(np.corrcoef(pairs.x, pairs.y)[0, 1]) if n > 2 else np.nan
        out.append(dict(x=xname, window=w, lead_quarters=L, reading=("x leads nights" if L > 0 else "nights lead x" if L < 0 else "contemporaneous"), n=n, r=r,
                        band95=1.96 / np.sqrt(n) if n else np.nan, outside_band=(abs(r) > 1.96 / np.sqrt(n)) if n else False))
    return out


rows = []
for w in ("J", "W1", "W2"):
    rows += ccf_table(p.g_sm, p.g_nights, p.quarter, w, "g_sm (S&M cash y/y)")
# marketing-only growth (quarterly component table; 3Q25/4Q25 missing)
gb = pd.Series({q: v for q, v in zip(qt.period, qt.g_bpm) if q != "2H25"})
p["g_bpm"] = p.quarter.map(gb)
for w in ("J", "W1"):
    rows += ccf_table(p.g_bpm, p.g_nights, p.quarter, w, "g_bpm (brand & performance marketing y/y, GAAP)")
h5a = pd.DataFrame(rows)
# R-style ccf reproduction for Jessie's number (biased estimator, series means), J sample, S&M cash
d = win(p, "J")
xs, ys = d.g_sm.values - d.g_sm.mean(), d.g_nights.values - d.g_nights.mean()
den = np.sqrt((xs ** 2).sum() * (ys ** 2).sum())
rstyle = {L: float((xs[:len(xs) - L] * ys[L:]).sum() / den) if L >= 0 else float((xs[-L:] * ys[:len(ys) + L]).sum() / den) for L in range(-4, 5)}
h5a["r_Rstyle_J"] = [rstyle[int(L)] if (w == "J" and x.startswith("g_sm")) else np.nan for w, L, x in zip(h5a.window, h5a.lead_quarters, h5a.x)]
# Jessie's exact object: arithmetic y/y (x/x[-4]-1), R ccf estimator, 1Q22-2Q26
xa, ya = (d.sm_cash / d.sm_cash.shift(4)).values, (d.nights_m / d.nights_m.shift(4)).values
d2 = win(p, "J")
xa, ya = (d2.sm_cash.values / p.sm_cash.shift(4).loc[d2.index].values - 1), (d2.nights_m.values / p.nights_m.shift(4).loc[d2.index].values - 1)
xa, ya = xa - xa.mean(), ya - ya.mean()
den = np.sqrt((xa ** 2).sum() * (ya ** 2).sum())
rarith = {L: float((xa[:len(xa) - L] * ya[L:]).sum() / den) if L >= 0 else float((xa[-L:] * ya[:len(ya) + L]).sum() / den) for L in range(-4, 5)}
h5a["r_Rstyle_arith_J"] = [rarith[int(L)] if (w == "J" and x.startswith("g_sm")) else np.nan for w, L, x in zip(h5a.window, h5a.lead_quarters, h5a.x)]
h5a.to_csv(OUT / "43a_h5a_ccf.csv", index=False)

# H5a rule
def h5a_rule(xname):
    ok = True
    for w in ("J", "W1"):
        s = h5a[(h5a.x == xname) & (h5a.window == w)].set_index("lead_quarters")
        if not (s.loc[0, "outside_band"] and not s.loc[1, "outside_band"] and not s.loc[2, "outside_band"]):
            ok = False
    return ok


# H5b partial regression
d = p.copy()
d["g_nights_l1"], d["g_sm_l1"], d["g_sm_l2"], d["q_l2"] = p.g_nights.shift(1), p.g_sm.shift(1), p.g_sm.shift(2), p.quarter.shift(2)
d = win(d, "J").dropna(subset=["g_nights", "g_nights_l1", "g_sm", "g_sm_l1", "g_sm_l2", "q_l2"])
d = d[d.q_l2.map(lambda q: in_win(q, "J"))]  # all lags inside 1Q22+ (no 2020/2021 base effects), n 16
X = d[["g_nights_l1", "g_sm", "g_sm_l1", "g_sm_l2"]].assign(const=1.0)[["const", "g_nights_l1", "g_sm", "g_sm_l1", "g_sm_l2"]]
m = hac(d.g_nights, X, 3)
h5b = pd.DataFrame(dict(term=X.columns, coef=m.params, se_hac=m.bse, t=m.params / m.bse, p_two_sided=m.pvalues, n=len(d), r2=sm.OLS(np.asarray(d.g_nights), np.asarray(X)).fit().rsquared))
h5b.to_csv(OUT / "43a_h5b_partial.csv", index=False)

# H5d regional revenue mix
reg = p.dropna(subset=["rev_na"]).copy()
reg["rev_lat_apac"] = reg.rev_latam + reg.rev_apac
reg["rev_na_emea"] = reg.rev_na + reg.rev_emea
rfy = reg.groupby("year")[["revenue", "rev_na", "rev_emea", "rev_latam", "rev_apac", "rev_lat_apac", "rev_na_emea"]].sum()
rfy = rfy[reg.groupby("year").size() == 4]
rh1 = reg[reg.qn <= 2].groupby("year")[["revenue", "rev_na", "rev_emea", "rev_latam", "rev_apac", "rev_lat_apac", "rev_na_emea"]].sum()
rows = []
for lab, tab, ys in (("FY", rfy, [2023, 2024, 2025]), ("1H", rh1, [2024, 2025, 2026])):
    for y in ys:
        a, b = tab.loc[y - 1], tab.loc[y]
        inc = b - a
        rows.append(dict(period=f"{lab}{y % 100}", revenue_growth_pct=100 * (b.revenue / a.revenue - 1), lat_apac_share_of_revenue_pct=100 * b.rev_lat_apac / b.revenue,
                         lat_apac_share_of_incremental_revenue_pct=100 * inc.rev_lat_apac / inc.revenue, na_emea_share_of_incremental_revenue_pct=100 * inc.rev_na_emea / inc.revenue,
                         latam_growth_pct=100 * (b.rev_latam / a.rev_latam - 1), apac_growth_pct=100 * (b.rev_apac / a.rev_apac - 1), na_growth_pct=100 * (b.rev_na / a.rev_na - 1), emea_growth_pct=100 * (b.rev_emea / a.rev_emea - 1)))
h5d = pd.DataFrame(rows)
if REGIONAL.exists():
    rw = pd.read_csv(REGIONAL)
    rw = rw[rw.quarter.isin(["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"])]
    adr = {f"modelled_adr_{r}_fy25_1h26_mean": float(rw[f"adr_{r}_usd_anchored"].mean()) for r in ("na", "emea", "latam", "apac")}
    for k, v in adr.items():
        h5d[k] = v
    h5d["adr_note"] = "regional ADR is MODELLED (data/processed/adr/04_regional_quarterly_wide.csv), not disclosed"
h5d.to_csv(OUT / "43a_h5d_regional_mix.csv", index=False)

# --------------------------------------------------------------------------------------------------------------------
# Tests summary
# --------------------------------------------------------------------------------------------------------------------
tests = []
lev_J = h1[(h1["sample"].str.startswith("J")) & (h1.line == "Sales & marketing") & (~h1.spec.str.contains("\\+ t"))].iloc[0]
tests.append(dict(test="H1a reproduce 1.41", pre_registered="expect 1.41 +- 0.02, DW ~0.93", result=f"{lev_J.coef:.3f} (NW se {lev_J.se_hac:.3f}), DW {lev_J.dw:.2f}, n {lev_J.n}", verdict="reproduced" if abs(lev_J.coef - 1.41) <= 0.02 else "NOT reproduced"))
tests.append(dict(test="H1b levels elasticity within 0.15 of trend ratio", pre_registered="|elasticity - trend ratio| <= 0.15 (J)", result=f"elasticity {h1b.iloc[0].levels_elasticity:.3f}, trend ratio {h1b.iloc[0].trend_ratio:.3f}, diff {h1b.iloc[0]['diff']:.3f}", verdict="holds" if h1b.iloc[0].within_0p15 else "does not hold"))
lt = h1[(h1["sample"] == "J") & (h1.spec.str.contains("\\+ t"))].iloc[0]
tests.append(dict(test="H1c add trend: log(rev) loses significance", pre_registered="95% NW interval includes 1 or sign unstable", result=f"coef {lt.coef:.3f}, CI [{lt.ci_lo:.2f}, {lt.ci_hi:.2f}], trend t {lt.trend_t:.2f}", verdict="holds" if (lt.ci_lo <= 1 <= lt.ci_hi or lt.coef < 0) else "does not hold"))
tests.append(dict(test="H1d spurious-regression risk", pre_registered="DW < 1.2 => high", result=f"DW {lev_J.dw:.2f}, resid AR1 {lev_J.resid_ar1:.2f}, BG p {lev_J.bg_p_lag2:.3f}, EG-ADF p {lev_J.adf_resid_p:.3f}", verdict="high" if lev_J.dw < 1.2 else "moderate"))
for w in ("W1", "W2"):
    r = h2b[h2b["sample"] == w].iloc[0]
    tests.append(dict(test=f"H2b S&M grows faster than revenue ({w})", pre_registered=f"mean gap > 0, HAC p <= 0.10, positive in >= {req[w]} of {r.n}", result=f"mean {100 * r.mean_gap_logpts:.1f} log-pp, p {r.p_one_sided:.3f}, positive {r.n_positive}/{r.n}", verdict="PASS" if r.pass_line else "FAIL"))
tests.append(dict(test="H2b both windows", pre_registered="must pass W1 and W2 to be quoted", result="", verdict="PASS" if h2b[h2b["sample"].isin(["W1", "W2"])].pass_line.all() else "FAIL"))
for meas in h3.measure.unique():
    s = h3[h3.measure == meas]
    tests.append(dict(test=f"H3/H5c trend on time: {meas}", pre_registered="one-sided p <= 0.10 in both windows", result="; ".join(f"{r.window} slope {r.slope_per_q:.4f} p {r.p_one_sided:.3f} (n {r.n})" for r in s.itertuples()), verdict="PASS both" if s.passes_0p10.all() else ("PASS W1 only" if s[s.window == "W1"].passes_0p10.all() else "FAIL")))
for xn in h5a.x.unique():
    tests.append(dict(test=f"H5a 'this quarter's nights, not the next' rule: {xn}", pre_registered="contemporaneous r outside band AND leads 1,2 inside band, in J and W1", result="; ".join(f"{r.window} L{r.lead_quarters:+d} r {r.r:.2f} (band {r.band95:.2f}, n {r.n})" for r in h5a[(h5a.x == xn) & (h5a.lead_quarters.isin([0, 1, 2])) & (h5a.window.isin(['J', 'W1']))].itertuples()), verdict="supported" if h5a_rule(xn) else "NOT supported"))
pd.DataFrame(tests).to_csv(OUT / "43a_tests.csv", index=False)

# console summary
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print("H1 levels:\n", h1[["sample", "line", "spec", "coef", "se_hac", "ci_lo", "ci_hi", "r2", "dw", "resid_ar1", "bg_p_lag2", "adf_resid_p", "trend_t", "n"]].round(3).to_string())
print("\nH1b trend ratio:\n", h1b.round(4).to_string())
print("\nH2a growth elasticity:\n", h2a.round(3).to_string())
print("\nH2b gap:\n", h2b.round(3).to_string())
print("\nH2c CAGR:\n", h2c.round(3).to_string())
print("\nH2c all lines:\n", h2c_lines.round(3).to_string())
print("\nH3 acceleration:\n", h3.round(4).to_string())
print("\nH3 by year:\n", h3y.round(2).to_string())
print("\nH4 annual components:\n", ann.round(2).to_string())
print("\nH4 half-year components:\n", hh.round(2).to_string())
print("\nH4 quarterly components:\n", qt.round(2).to_string())
print("\nH5a ccf:\n", h5a.round(3).to_string())
print("\nH5b partial:\n", h5b.round(3).to_string())
print("\nH5d regional:\n", h5d.round(2).to_string())
print("\nTests:\n", pd.DataFrame(tests).to_string())
print("\nOK: wrote", OUT)
