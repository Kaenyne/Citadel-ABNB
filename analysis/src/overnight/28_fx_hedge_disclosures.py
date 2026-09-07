"""Workstream 28: Airbnb's FX cash-flow hedge disclosures, 1Q23-2Q26, and what they do to revenue FX.

Sources: 10-Q/10-K Note "Derivative Instruments and Hedging" (hand-extracted sentences, values below,
raw text in data/raw/edgar/hedge_paragraphs.txt, gitignored, rebuilt by the download block in this file's
history), XBRL companyfacts (OCI on cash flow hedges; amount expected to be reclassified within 12 months),
02_kpi_panel_quarterly.csv (revenue, letter-stated FX points on revenue and ADR), 10_fx_quarterly.csv (EUR, GBP y/y).

Run:  py -3.13 analysis/src/overnight/28_fx_hedge_disclosures.py
Writes: data/processed/overnight/28_fx_hedge_disclosures.csv, 28_fx_hedge_tests.csv, 28_fx_hedge_forward.csv
"""
import csv
import json
import os
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OD = lambda f: os.path.join(ROOT, "data", "processed", "overnight", f)
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))
fl = lambda x: float(x) if x not in ("", None, "nan") else np.nan

# Hand-extracted from the filings (USD M). Notionals are period-end. Reclass = realised gain (loss) on
# designated hedges reclassified from AOCI to revenue in the quarter; "immaterial" recorded as 0.
# 4Q25 reclass = FY25 (-64) less 9M25 (-41). 4Q OCI = FY less 9M from XBRL.
DISC = {  # quarter: (designated notional, non-designated notional, AOCI cumulative net of tax, reclass to revenue, expected reclass next 12m)
    "1Q23": (494.3, 3300, -4.1, 0, np.nan), "2Q23": (918, 3900, -2, 0, np.nan), "3Q23": (1400, 3100, 35, 0, np.nan),
    "4Q23": (2000, 2400, -31, 0, -11), "1Q24": (2200, 3100, 17, 0, 16), "2Q24": (2200, 2200, 62, 0, 25),
    "3Q24": (2200, 1600, -37, 0, -34), "4Q24": (2500, 2100, 80, 0, 68), "1Q25": (2500, 1600, 7, 0, 16),
    "2Q25": (2400, 1900, -123, 0, -104), "3Q25": (2600, 1300, -77, -42, -76), "4Q25": (3100, 2700, -59, -23, -63),
    "1Q26": (3300, 3200, 14, -15, -7), "2Q26": (3400, 2900, 39, -19, -26),
}
# XBRL OtherComprehensiveIncomeLossCashFlowHedgeGainLossAfterReclassificationAndTaxParent, quarterly (4Q = FY - 9M)
OCI = {"1Q23": -4, "2Q23": 2, "3Q23": 37, "4Q23": -66, "1Q24": 48, "2Q24": 14, "3Q24": -68, "4Q24": 117,
       "1Q25": -73, "2Q25": -130, "3Q25": 46, "4Q25": 18, "1Q26": 73, "2Q26": 25}
NON_USD_SHARE = {2023: 0.54, 2024: 0.54, 2025: 0.56, 2026: 0.56}  # 10-K: share of revenue in non-USD currencies

kpi = {r["quarter"]: r for r in rd(OD("02_kpi_panel_quarterly.csv"))}
fxr = list(csv.reader(open(OD("10_fx_quarterly.csv"), encoding="utf-8")))[2:]  # two header rows; cols 13/14 = EUR, GBP y/y
fxq = {r[0]: {"EUR": fl(r[13]), "GBP": fl(r[14])} for r in fxr}
prev = lambda q: f"{q[0]}Q{int(q[2:]) - 1:02d}"
Q = list(DISC)

rows = []
for q in Q:
    n_des, n_non, aoci, recl, exp12 = DISC[q]
    rev, rev_py = fl(kpi[q]["revenue_musd"]), fl(kpi[prev(q)]["revenue_musd"])
    hedge_pp = recl / rev_py * 100
    stated = fl(kpi[q]["fx_pts_revenue"])
    yr = 2000 + int(q[2:])
    ltm = sum(fl(r["revenue_musd"]) for r in list(kpi.values())[list(kpi).index(q) - 3: list(kpi).index(q) + 1])
    rows.append(dict(quarter=q, designated_notional_musd=n_des, non_designated_notional_musd=n_non,
                     aoci_cash_flow_hedges_musd=aoci, oci_cash_flow_hedges_in_quarter_musd=OCI[q],
                     reclassified_to_revenue_musd=recl, expected_reclass_next_12m_musd=exp12,
                     revenue_musd=rev, revenue_prior_year_musd=rev_py, hedge_effect_on_revenue_growth_pp=round(hedge_pp, 2),
                     stated_revenue_fx_pp=stated, gross_fx_ex_hedge_pp=round(stated - hedge_pp, 2) if not np.isnan(stated) else np.nan,
                     stated_adr_fx_pp=fl(kpi[q]["fx_pts_adr"]), eur_usd_yoy_pct=fxq[q]["EUR"], gbp_usd_yoy_pct=fxq[q]["GBP"],
                     ltm_revenue_musd=ltm, non_usd_revenue_share=NON_USD_SHARE[yr],
                     designated_notional_pct_of_ltm_non_usd_revenue=round(n_des / (ltm * NON_USD_SHARE[yr]) * 100, 1),
                     expected_reclass_pp_of_ltm_revenue=round(exp12 / ltm * 100, 2) if not np.isnan(exp12) else np.nan))
with open(OD("28_fx_hedge_disclosures.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# Tests
tests = []
# 1. Does "expected to be reclassified within 12 months" predict the realised reclass over the next four quarters?
for i, q in enumerate(Q):
    exp12 = DISC[q][4]
    nxt = Q[i + 1: i + 5]
    if np.isnan(exp12) or len(nxt) < 4:
        continue
    real = sum(DISC[x][3] for x in nxt)
    tests.append(dict(test="expected_vs_realised_next_4q", quarter=q, x=exp12, y=real, note="expected reclass at quarter end vs realised reclass to revenue over the following four quarters"))
# 2. Gross FX ex hedge vs EUR y/y at lags 0-2 (WS05 used the stated number; here the hedge is removed first)
def ols(x, y):
    m = ~np.isnan(x) & ~np.isnan(y); x, y = x[m], y[m]
    if len(x) < 5: return np.nan, np.nan, np.nan, len(x)
    b, a = np.polyfit(x, y, 1); r = np.corrcoef(x, y)[0, 1]; return a, b, r, len(x)
qs = [r["quarter"] for r in rows]
allq = list(kpi)
eur_all = {q: fxq.get(q, {}).get("EUR", np.nan) for q in allq}
for dep, lab in [("stated_revenue_fx_pp", "stated (WS05 basis)"), ("gross_fx_ex_hedge_pp", "gross ex hedge")]:
    y = np.array([fl(r[dep]) for r in rows])
    for lag in (0, 1, 2, "mean12"):
        if lag == "mean12":
            x = np.array([np.nanmean([eur_all.get(allq[allq.index(q) - 1], np.nan), eur_all.get(allq[allq.index(q) - 2], np.nan)]) for q in qs])
        else:
            x = np.array([eur_all.get(allq[allq.index(q) - lag], np.nan) for q in qs])
        a, b, r, n = ols(x, y)
        tests.append(dict(test=f"revenue_fx_vs_eur_lag_{lag}", quarter=lab, x=round(b, 3) if not np.isnan(b) else np.nan, y=round(r, 3) if not np.isnan(r) else np.nan,
                          note=f"slope pp per 1% EUR y/y (x) and r (y); n={n}; 1Q23-2Q26"))
with open(OD("28_fx_hedge_tests.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(tests[0])); w.writeheader(); w.writerows(tests)

# Forward: spread the 2Q26 expected reclass (-26) over 3Q26-2Q27 by 2025 revenue seasonality; express in pp of prior-year revenue
seas = {q[0]: fl(kpi[q]["revenue_musd"]) for q in ["1Q25", "2Q25", "3Q25", "4Q25"]}; tot = sum(seas.values())
fwd = []
for q, py in [("3Q26", "3Q25"), ("4Q26", "4Q25"), ("1Q27", "1Q26"), ("2Q27", "2Q26")]:
    amt = DISC["2Q26"][4] * seas[q[0]] / tot
    fwd.append(dict(quarter=q, hedge_reclass_musd=round(amt, 1), prior_year_revenue_musd=fl(kpi[py]["revenue_musd"]),
                    hedge_effect_on_revenue_growth_pp=round(amt / fl(kpi[py]["revenue_musd"]) * 100, 2),
                    note="2Q26 10-Q: ~$26M of deferred net losses expected to be reclassified to revenue in the next 12 months; spread by 2025 revenue seasonality"))
with open(OD("28_fx_hedge_forward.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(fwd[0])); w.writeheader(); w.writerows(fwd)

for r in rows:
    print(f"{r['quarter']} des {r['designated_notional_musd']:6.0f} ({r['designated_notional_pct_of_ltm_non_usd_revenue']:4.1f}% of LTM non-USD rev) aoci {r['aoci_cash_flow_hedges_musd']:6.1f} oci {r['oci_cash_flow_hedges_in_quarter_musd']:5.0f} recl {r['reclassified_to_revenue_musd']:4.0f} = {r['hedge_effect_on_revenue_growth_pp']:5.2f}pp | stated FX {r['stated_revenue_fx_pp']:5.1f} gross {r['gross_fx_ex_hedge_pp']:5.2f} | EUR {r['eur_usd_yoy_pct']:6.1f} | exp12 {r['expected_reclass_next_12m_musd']}")
for t in tests: print(t["test"], t["quarter"], t["x"], t["y"])
for f_ in fwd: print(f_["quarter"], f_["hedge_reclass_musd"], f_["hedge_effect_on_revenue_growth_pp"])
