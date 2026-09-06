"""Workstream 13: the integrated ABNB driver model (Python mirror + the Excel workbook it writes).

WHAT THIS IS
  One set of inputs, two engines. The Python engine in this file is the reference implementation.
  The same input tables are written into `model/ABNB_driver_model.xlsx` as an `Inputs` block, and
  every downstream number in the workbook is a live Excel formula off that block, so a teammate can
  flex an assumption in Excel and see the whole model move. A reviewer re-runs this script.

READS  (paths relative to the repo root)
  data/processed/overnight/02_kpi_panel_quarterly.csv       quarterly KPI + cost history 3Q20-2Q26 (WS02)
  data/processed/overnight/07_margin_levers_fy26_fy28.csv   lever-by-lever cost model FY26-FY28 (WS07)
  data/processed/overnight/07_cost_lines_per_night.csv      brand+performance vs field-ops split (WS07)
  data/processed/overnight/10_regional_forecast.csv         regional nights build 3Q26/4Q26/FY27 (WS10)
  data/processed/overnight/10_regional_panel_quarterly.csv  regional nights shares, history (WS10)
  data/processed/overnight/05_fx_schedule.csv               FX effect on ADR and revenue by quarter (WS05)
  data/processed/overnight/11_new_business_scenarios.csv    hotels/experiences/services/ads (WS11)
  data/processed/overnight/11_regulatory_overlay.csv        regulatory drag median/mean/p95 (WS11)
  data/processed/overnight/12_exit_multiple_recommendation.csv exit multiples (WS12)
  data/processed/overnight/04_current_consensus.csv         Street FY26/FY27 (WS04)
  data/processed/overnight/02_q3_2026_guide_card.csv        cushion-adjusted 3Q26 revenue (WS02)
  data/processed/overnight/04_q3_2026_breakeven.csv         3Q26 Street bars (WS04)
  data/processed/overnight/08_q3_2026_nowcast.csv,
  data/processed/overnight/08_demand_index_quarterly.csv    alt-data nowcast + demand index (WS08)
  data/processed/abnb_capital_return_quarterly.csv          buybacks, SBC, withholding, share count

WRITES
  model/ABNB_driver_model.xlsx                       8 sheets, live formulas
  data/processed/overnight/13_model_quarterly.csv    3Q26-4Q27 by scenario
  data/processed/overnight/13_model_annual.csv       FY26-FY28 by scenario
  data/processed/overnight/13_valuation_summary.csv  price per lens per scenario, DCF, reverse DCF
  data/processed/overnight/13_scenario_grid.csv      revenue growth x margin x multiple -> price
  data/processed/overnight/13_reconciliation.csv     Python mirror vs the workbook

RUN   py -3.13 analysis/src/overnight/13_driver_model.py
"""
from __future__ import annotations

import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
OD = lambda name: P("data", "processed", "overnight", name)

SCENARIOS = ["Bear", "Base", "Bull"]
SIDX = {"Bear": 0, "Base": 1, "Bull": 2}
YEARS = [2026, 2027, 2028]
FQ = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]          # forecast quarters
PRIOR_Q = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26",
           "3Q27": "3Q26", "4Q27": "4Q26"}
QYEAR = {"3Q26": 2026, "4Q26": 2026, "1Q27": 2027, "2Q27": 2027, "3Q27": 2027, "4Q27": 2027}
REGIONS = ["na", "emea", "latam", "apac"]
RLABEL = {"na": "North America", "emea": "EMEA", "latam": "Latin America", "apac": "Asia Pacific"}


def rd(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fl(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


# =====================================================================================================
# 1. ACTUALS
# =====================================================================================================
PANEL = {r["quarter"]: r for r in rd(OD("02_kpi_panel_quarterly.csv"))}
COSTQ = {r["quarter"]: r for r in rd(OD("07_cost_lines_per_night.csv"))}
CAPRET = {r["quarter"]: r for r in rd(P("data", "processed", "abnb_capital_return_quarterly.csv"))}
REGPANEL = {r["quarter"]: r for r in rd(OD("10_regional_panel_quarterly.csv"))}

HIST_Q = sorted([q for q in PANEL if q not in ("3Q20", "4Q20")], key=lambda q: (int(q[2:]), int(q[0])))

# FY2025 actual base for the cost engine (same construction as WS07's actuals(); see 07_margin_lever_model.py)
FY25 = dict(rev=12241.0, nights=533.0, gbv=91300.0, cor=2086.0, ops=1237.0, pd=1337.0,
            bpm=1595.0, fop=781.0, ga=1069.0, sbc=1581.0, adj=4297.0, new_business=12.0)
FY25["adr"] = FY25["gbv"] / FY25["nights"]
FY25["take"] = FY25["rev"] / FY25["gbv"]

# 1H2026 actual: FY2026 = 1H26 actual + the 3Q26 and 4Q26 forecast quarters
H1_26 = dict(rev=2678.0 + 3608.0, nights=156.2 + 148.3, gbv=29200.0 + 27200.0,
             adj=519.0 + 1261.0, fcf=1704.0 + 1253.0, buybacks=1088.0 + 1051.0,
             withholding=140.0 + 165.0)

QB = {}                                    # prior-year quarters the forecast grows off
for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
    r = PANEL[q]
    QB[q] = dict(nights=fl(r["nights_m"]), gbv=fl(r["gbv_musd"]), adr=fl(r["adr_usd"]),
                 rev=fl(r["revenue_musd"]), take=fl(r["take_rate_pct"]) / 100.0)

QSHARE = {}                                # regional nights shares of those quarters, normalised
for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
    raw = {rg: fl(REGPANEL[q][f"{rg}_nights_share_est_pct"]) for rg in REGIONS}
    t = sum(raw.values())
    QSHARE[q] = {rg: raw[rg] / t for rg in REGIONS}

_r = {rg: 0.0 for rg in REGIONS}           # FY2025 regional share, nights-weighted
for q in ["1Q25", "2Q25", "3Q25", "4Q25"]:
    raw = {rg: fl(REGPANEL[q][f"{rg}_nights_share_est_pct"]) for rg in REGIONS}
    t, n = sum(raw.values()), fl(PANEL[q]["nights_m"])
    for rg in REGIONS:
        _r[rg] += n * raw[rg] / t
FY25_SHARE = {rg: _r[rg] / FY25["nights"] for rg in REGIONS}

# Seasonal adj. EBITDA margin spread, points vs the full-year margin, 2023-2025 mean
SEAS_MARGIN = {}
for qn in ["1Q", "2Q", "3Q", "4Q"]:
    v = []
    for yy in ("23", "24", "25"):
        fr = sum(fl(PANEL[f"{i}Q{yy}"]["revenue_musd"]) for i in (1, 2, 3, 4))
        fa = sum(fl(PANEL[f"{i}Q{yy}"]["adj_ebitda_musd"]) for i in (1, 2, 3, 4))
        v.append(fl(PANEL[f"{qn}{yy}"]["adj_ebitda_margin_pct"]) - 100.0 * fa / fr)
    SEAS_MARGIN[qn] = sum(v) / len(v)

# Seasonal nights and revenue shares, 2023-2025 mean (used on the Revenue sheet as a cross-check)
SEAS_SHARE = {}
for qn in ["1Q", "2Q", "3Q", "4Q"]:
    n, r_ = [], []
    for yy in ("23", "24", "25"):
        fn = sum(fl(PANEL[f"{i}Q{yy}"]["nights_m"]) for i in (1, 2, 3, 4))
        fr = sum(fl(PANEL[f"{i}Q{yy}"]["revenue_musd"]) for i in (1, 2, 3, 4))
        n.append(100 * fl(PANEL[f"{qn}{yy}"]["nights_m"]) / fn)
        r_.append(100 * fl(PANEL[f"{qn}{yy}"]["revenue_musd"]) / fr)
    SEAS_SHARE[qn] = (sum(n) / 3, sum(r_) / 3)

LTM_FCF = sum(fl(PANEL[q]["fcf_musd"]) for q in ["3Q25", "4Q25", "1Q26", "2Q26"])
LTM_SBC = sum(fl(PANEL[q]["sbc_musd"]) for q in ["3Q25", "4Q25", "1Q26", "2Q26"])
LTM_EBITDA = sum(fl(PANEL[q]["adj_ebitda_musd"]) for q in ["3Q25", "4Q25", "1Q26", "2Q26"])
LTM_REV = sum(fl(PANEL[q]["revenue_musd"]) for q in ["3Q25", "4Q25", "1Q26", "2Q26"])


# =====================================================================================================
# 2. INPUTS   -- every row becomes a cell on the Inputs sheet; (bear, base, bull, unit, source)
# =====================================================================================================
ANNUAL_ORDER = ["take_bps", "cor_per_gbv", "ops_cpn", "pd_cash", "bpm_cash", "fop_cash", "ga_cash",
                "addback_pct", "sbc_growth", "int_income", "int_expense", "cash_tax_pct",
                "d_unearned_pct", "eff_tax_rate", "ai_referral_pct", "new_business", "buybacks",
                "reg_mult", "capex_pct", "wc_resid_pct", "da_pct"]
ANNUAL_LABEL = {
    "take_bps": "Take rate change vs prior year (bps)",
    "cor_per_gbv": "Cost of revenue per $ GBV, y/y change",
    "ops_cpn": "Operations & support cash per night, y/y change",
    "pd_cash": "Product development cash (ex-SBC), y/y growth",
    "bpm_cash": "Brand & performance marketing, y/y growth",
    "fop_cash": "Field operations & policy cash (new-business investment), y/y growth",
    "ga_cash": "G&A cash, y/y growth",
    "addback_pct": "D&A + other add-backs, % of revenue",
    "sbc_growth": "SBC, y/y growth",
    "int_income": "Interest income ($M)",
    "int_expense": "Interest expense ($M)",
    "cash_tax_pct": "Cash taxes, % of revenue",
    "d_unearned_pct": "Change in unearned fees, % of revenue",
    "eff_tax_rate": "Effective tax rate (net income)",
    "ai_referral_pct": "AI referral cost, % of revenue",
    "new_business": "New business outside GBV x take (ads + Services), $M",
    "buybacks": "Buybacks ($M)",
    "reg_mult": "Regulatory drag multiplier (x WS11 median)",
    "capex_pct": "Capex, % of revenue",
    "wc_resid_pct": "Working-capital residual, % of revenue",
    "da_pct": "D&A, % of revenue",
}
ANNUAL_INPUTS = {
    2026: {
        "take_bps": (-5.0, 0.0, 5.0, "bps", "WS07 lever; management guided FY26 take rate flat (2Q26 call)"),
        "cor_per_gbv": (0.005, 0.000, -0.005, "y/y", "WS07 lever; 2Q26 10-Q merchant fees and chargebacks"),
        "ops_cpn": (-0.040, -0.050, -0.060, "y/y", "WS07 lever; 1H26 -3.8%, support cost per booking -16%"),
        "pd_cash": (0.115, 0.110, 0.105, "y/y", "WS07 lever; 1H26 +11%"),
        "bpm_cash": (0.280, 0.250, 0.230, "y/y", "WS07 lever; 1H26 brand+performance +32%"),
        "fop_cash": (0.200, 0.180, 0.160, "y/y", "WS07 lever; field ops +24% in 1H26"),
        "ga_cash": (0.030, 0.020, 0.000, "y/y", "WS07 lever; 1H26 +1%"),
        "addback_pct": (0.009, 0.009, 0.009, "% rev", "WS07 lever"),
        "sbc_growth": (0.160, 0.130, 0.100, "y/y", "WS07 lever; 1H26 +14.7%, guided below FY25"),
        "int_income": (620.0, 660.0, 700.0, "$M", "WS07 lever; $12.1bn cash + ST investments"),
        "int_expense": (125.0, 120.0, 115.0, "$M", "WS07 lever; $2.5bn notes at 4.40-5.25%"),
        "cash_tax_pct": (0.035, 0.026, 0.020, "% rev", "WS07 lever; FY25 cash taxes 1.9% of revenue"),
        "d_unearned_pct": (-0.005, 0.000, 0.005, "% rev", "WS07 lever; RNPL has switched the float off"),
        "eff_tax_rate": (0.210, 0.190, 0.180, "% pretax", "WS02: FY26 guide 17-19%, guides run ~50bp hot; FY25 actual 20.0%"),
        "ai_referral_pct": (0.000, 0.000, 0.000, "% rev", "WS11: zero in 2026 in every case"),
        "new_business": (24.0, 42.0, 60.0, "$M", "WS11 11_new_business_scenarios: Services + sponsored listings only"),
        "buybacks": (4200.0, 4200.0, 4200.0, "$M", "1H26 actual $2,139M + H2 at the 1H run rate; $3.4bn authorisation left"),
        "reg_mult": (1.67, 1.67, 0.00, "x", "WS11 says use the mean in the base and the p95 in the bear; mean/median = 0.251/0.150 = 1.67, p95/median = 6.10. The bear keeps the mean because WS10's demand bear and WS05's strong-dollar bear already carry the tail; the p95 is a documented alternative"),
        "capex_pct": (0.003, 0.003, 0.003, "% rev", "WS07; $33-34M a year"),
        "wc_resid_pct": (-0.011, -0.011, -0.011, "% rev", "WS07; FY24 and FY25 both -$140M"),
        "da_pct": (0.007, 0.007, 0.007, "% rev", "WS07; D&A 0.6-0.8% of revenue since 2023"),
    },
    2027: {
        "take_bps": (-15.0, 0.0, 15.0, "bps", "WS07 lever; single fee vs the 6-10% direct-link pilot (WS11)"),
        "cor_per_gbv": (0.015, 0.000, -0.010, "y/y", "WS07 lever"),
        "ops_cpn": (-0.020, -0.050, -0.070, "y/y", "WS07 lever"),
        "pd_cash": (0.090, 0.100, 0.100, "y/y", "WS07 lever"),
        "bpm_cash": (0.120, 0.160, 0.145, "y/y", "WS07 lever"),
        "fop_cash": (0.100, 0.140, 0.120, "y/y", "WS07 lever"),
        "ga_cash": (0.050, 0.055, 0.045, "y/y", "WS07 lever"),
        "addback_pct": (0.009, 0.009, 0.009, "% rev", "WS07 lever"),
        "sbc_growth": (0.140, 0.100, 0.060, "y/y", "WS07 lever"),
        "int_income": (540.0, 620.0, 690.0, "$M", "WS07 lever"),
        "int_expense": (128.0, 125.0, 122.0, "$M", "WS07 lever"),
        "cash_tax_pct": (0.045, 0.034, 0.026, "% rev", "WS07 lever"),
        "d_unearned_pct": (-0.005, 0.000, 0.003, "% rev", "WS07 lever"),
        "eff_tax_rate": (0.210, 0.200, 0.190, "% pretax", "WS02; FY25 actual 20.0%"),
        "ai_referral_pct": (0.0228, 0.0038, 0.000, "% rev", "WS11 11_ai_exposure_scenarios, high/low/zero at a 5% referral fee"),
        "new_business": (38.0, 212.0, 430.0, "$M", "WS11 Services + sponsored listings"),
        "buybacks": (3000.0, 4000.0, 4500.0, "$M", "model/assumptions.md; FY24 $3.4bn, FY25 $3.8bn"),
        "reg_mult": (1.67, 1.67, 0.00, "x", "WS11 mean/median = 0.752/0.451 = 1.67 (p95/median = 6.08, the documented alternative)"),
        "capex_pct": (0.003, 0.003, 0.003, "% rev", "WS07"),
        "wc_resid_pct": (-0.011, -0.011, -0.011, "% rev", "WS07"),
        "da_pct": (0.007, 0.007, 0.007, "% rev", "WS07"),
    },
    2028: {
        "take_bps": (-10.0, 5.0, 20.0, "bps", "WS07 lever; bull is the sponsored-listings case"),
        "cor_per_gbv": (0.010, -0.005, -0.015, "y/y", "WS07 lever"),
        "ops_cpn": (-0.020, -0.050, -0.070, "y/y", "WS07 lever"),
        "pd_cash": (0.085, 0.095, 0.095, "y/y", "WS07 lever"),
        "bpm_cash": (0.110, 0.135, 0.125, "y/y", "WS07 lever"),
        "fop_cash": (0.090, 0.120, 0.105, "y/y", "WS07 lever"),
        "ga_cash": (0.050, 0.050, 0.040, "y/y", "WS07 lever"),
        "addback_pct": (0.009, 0.009, 0.009, "% rev", "WS07 lever"),
        "sbc_growth": (0.120, 0.080, 0.040, "y/y", "WS07 lever"),
        "int_income": (500.0, 590.0, 680.0, "$M", "WS07 lever"),
        "int_expense": (128.0, 125.0, 122.0, "$M", "WS07 lever"),
        "cash_tax_pct": (0.052, 0.040, 0.032, "% rev", "WS07 lever"),
        "d_unearned_pct": (-0.005, 0.000, 0.003, "% rev", "WS07 lever"),
        "eff_tax_rate": (0.210, 0.200, 0.190, "% pretax", "WS02"),
        "ai_referral_pct": (0.0383, 0.0077, 0.000, "% rev", "WS11 11_ai_exposure_scenarios"),
        "new_business": (114.0, 516.0, 1096.0, "$M", "WS11 Services + sponsored listings"),
        "buybacks": (3000.0, 4000.0, 4500.0, "$M", "model/assumptions.md"),
        "reg_mult": (1.42, 1.42, 0.00, "x", "WS11 mean/median = 1.230/0.868 = 1.42 (p95/median = 4.56, the documented alternative)"),
        "capex_pct": (0.003, 0.003, 0.003, "% rev", "WS07"),
        "wc_resid_pct": (-0.011, -0.011, -0.011, "% rev", "WS07"),
        "da_pct": (0.007, 0.007, 0.007, "% rev", "WS07"),
    },
}

# FY2028 total nights growth (no regional build exists that far out) -- WS07 lever
NIGHTS_2028 = (0.050, 0.080, 0.095)
ADR_EXFX_2028 = (0.010, 0.025, 0.035)

# Regional nights growth %, by forecast quarter and scenario -- WS10 10_regional_forecast.csv.
# FY2027 uses WS10's FY27 annual regional rates in every quarter (WS10 gives no quarterly FY27 split).
REGIONAL_G = {
    "3Q26": {"Bear": (5.0, 6.0, 15.0, 14.0), "Base": (7.0, 8.0, 18.0, 17.0), "Bull": (9.0, 10.0, 21.0, 19.0)},
    "4Q26": {"Bear": (4.0, 5.0, 14.0, 13.0), "Base": (7.0, 7.0, 18.0, 17.0), "Bull": (9.0, 9.0, 21.0, 19.0)},
}
for _q in ["1Q27", "2Q27", "3Q27", "4Q27"]:
    REGIONAL_G[_q] = {"Bear": (3.0, 4.0, 12.0, 11.0), "Base": (6.0, 7.0, 16.0, 15.0),
                      "Bull": (8.0, 9.0, 19.0, 18.0)}

# Regulatory nights drag, incremental pp of y/y growth in the year, median case (WS11 11_regulatory_overlay).
# Cumulative run-rate loss vs the 2Q26 baseline: EMEA 0.36 / 1.07 / 2.07 %; NA 0.03 / 0.08 / 0.15 %.
REG_DRAG_PP = {2026: dict(na=0.03, emea=0.36, latam=0.0, apac=0.0),
               2027: dict(na=0.05, emea=0.71, latam=0.0, apac=0.0),
               2028: dict(na=0.07, emea=1.00, latam=0.0, apac=0.0)}

# Quarterly ADR ex-FX growth, % (WS10 for the 2026 quarters; WS06 and WS07 agree on +2.5% base for FY27)
ADR_EXFX_Q = {q: ({"Bear": 2.0, "Base": 3.0, "Bull": 4.0} if q in ("3Q26", "4Q26")
                  else {"Bear": 1.0, "Base": 2.5, "Bull": 3.5}) for q in FQ}

# Quarterly FX, pp: (revenue FX, ADR FX). WS05 05_fx_schedule.csv; bear = strong_usd, bull = weak_usd.
# Revenue FX is the LAGGED fit (mean EUR/USD y/y at t-1,t-2; n 17, r 0.80). ADR FX is the
# contemporaneous broad-USD fit that WS08 re-estimated independently (r 0.96, walk-forward 0.44x naive).
# 3Q26 revenue FX is set to the company's guided +3.0pp (2Q26 letter), which WS05 used to validate the
# fit; the fit's own +2.19pp is carried as a documented alternative.
FX_Q = {
    "3Q26": {"Bear": (3.00, 0.80), "Base": (3.00, 0.80), "Bull": (3.00, 0.80)},
    "4Q26": {"Bear": (-0.43, -1.42), "Base": (-0.43, -0.36), "Bull": (-0.43, 0.70)},
    "1Q27": {"Bear": (-1.56, -2.68), "Base": (-1.03, -0.40), "Bull": (-0.50, 1.18)},
    "2Q27": {"Bear": (-2.48, -2.81), "Base": (-0.80, 0.02), "Bull": (0.53, 2.15)},
    "3Q27": {"Bear": (-3.18, -2.38), "Base": (-0.61, 0.66), "Bull": (1.25, 2.99)},
    "4Q27": {"Bear": (-3.02, -1.31), "Base": (-0.07, 0.49), "Bull": (2.16, 1.86)},
}
FX_2028 = {"Bear": (0.0, 0.0), "Base": (0.0, 0.0), "Bull": (0.0, 0.0)}

# 3Q26 and 4Q26 adj. EBITDA margin, % -- WS07's 5 Nov card and its implied-Q4 table
Q_MARGIN_26 = {"3Q26": {"Bear": 48.3, "Base": 49.0, "Bull": 50.2},
               "4Q26": {"Bear": 26.5, "Base": 32.5, "Bull": 36.8}}

VAL_ORDER = ["price", "net_cash_2q26", "shares_2q26", "cost_of_equity", "terminal_growth",
             "dcf_start_growth", "exit_ev_ebitda", "exit_ev_fcf", "exit_p_sbcfcf", "exit_p_earnings",
             "withholding_pct", "price_growth", "nb_incr_margin", "margin_cap", "dcf_years"]
VAL_LABEL = {
    "price": "Share price (4 Sep 2026 close)", "net_cash_2q26": "Net cash ex float, 30 Jun 2026 ($M)",
    "shares_2q26": "Diluted shares, 2Q26 (M)", "cost_of_equity": "Cost of equity",
    "terminal_growth": "Terminal growth", "exit_ev_ebitda": "Exit EV / FY27E adj. EBITDA (x)",
    "exit_ev_fcf": "Exit EV / FY27E FCF (x)", "exit_p_sbcfcf": "Exit P / FY27E SBC-adj. FCF (x)",
    "exit_p_earnings": "Exit P / FY27E earnings proxy (x)", "withholding_pct": "RSU tax withholding, % of SBC",
    "price_growth": "Share price growth used for buyback/issuance math",
    "nb_incr_margin": "Incremental EBITDA margin on new-business revenue", "dcf_years": "DCF fade period (years)",
    "dcf_start_growth": "DCF start growth (year-1 FCF growth, fades to terminal)",
    "margin_cap": "Adj. EBITDA margin cap",
}
VAL_INPUTS = {
    "price": (181.94, 181.94, 181.94, "$", "Close 4 Sep 2026"),
    "net_cash_2q26": (9593.0, 9593.0, 9593.0, "$M", "WS12; 2Q26 XBRL. Funds held for clients ($12,224M) excluded"),
    "shares_2q26": (597.0, 597.0, 597.0, "M", "2Q26 diluted weighted-average (XBRL)"),
    "cost_of_equity": (0.115, 0.105, 0.103, "", "WS09 10.5-11.5% (Rf 4.78% + beta 1.2-1.3 x ERP 4.5-5.5%); WS12 CAPM 10.3%"),
    "terminal_growth": (0.025, 0.030, 0.030, "", "WS12 2.5-3.0%"),
    "exit_ev_ebitda": (13.5, 16.5, 18.5, "x", "WS12 12_exit_multiple_recommendation.csv (time-series / cross-section / intrinsic blend)"),
    "exit_ev_fcf": (11.3, 14.3, 17.3, "x", "5 Sep set (15/19/23x) rescaled by WS12's 0.75x haircut to the EBITDA multiple"),
    "exit_p_sbcfcf": (15.0, 19.5, 24.0, "x", "same 0.75x haircut on the 5 Sep 20/26/32x"),
    "exit_p_earnings": (15.0, 19.5, 24.0, "x", "same 0.75x haircut on the 5 Sep 20/26/32x"),
    "withholding_pct": (0.35, 0.35, 0.35, "", "FY2025 withholding $561M on SBC $1,581M = 35.5%"),
    "price_growth": (0.05, 0.05, 0.05, "", "5 Sep convention: buybacks and RSU issuance at a price rising 5% a year"),
    "nb_incr_margin": (0.70, 0.70, 0.70, "", "incremental margin on sponsored listings and Services; ads near 100%, Services lower"),
    "dcf_years": (10.0, 10.0, 10.0, "yrs", "5 Sep reverse-DCF convention: 10-year fade to terminal"),
    "dcf_start_growth": (0.00, 0.09, 0.15, "", "a round number just under the model's own FY2026E-FY2028E FCF CAGR of 9.9%, clipped to 0-15%. A ten-year fade started from a single scenario year's FCF growth (-21% bear, +26% bull) is an extrapolation artefact, not a valuation"),
    "margin_cap": (0.38, 0.38, 0.38, "", "WS07: the realistic adj. EBITDA ceiling is 38%, against BKNG's five-year EBITDA-proxy range of 30.0-37.4%. Binds only in the bull case"),
}

ALTERNATIVES = [
    ("FY27 revenue FX", "0.0 pp -- contemporaneous FX (WS10, and the 5 Sep driver model)",
     "-0.63 pp -- WS05 lagged fit (in the base)",
     "WS05 fits revenue FX on the mean EUR/USD y/y at t-1 and t-2 (n 17, r 0.80) and validates it against the guided +3.0pp for 3Q26. The contemporaneous version has no such validation and 84% of the 4Q26 driver is already realised."),
    ("3Q26 revenue FX", "+2.19 pp -- WS05 lagged fit", "+3.00 pp -- 2Q26 letter guide (in the base)",
     "The company quantified it; the fit's +/-0.8pp error band covers the guide."),
    ("FY27 ADR FX", "-0.11 pp -- WS05 EUR/USD-basis ADR fit", "+0.19 pp -- broad-USD-basis fit (in the base)",
     "WS08 re-estimated the broad-USD version on 2022Q2-2026Q2 (r 0.96) and walk-forward tested it at 0.44x the naive error. The choice moves the ADR/GBV display only; revenue runs off the revenue-FX line."),
    ("FY27 revenue growth", "+12.4% (WS10 regional build, gross of regulation, FX 0); +10.3% (WS05 probability-weighted); +11.2% (WS07 levers)",
     "model output (WS10 nights net of WS11 regulation, WS06/WS07 ADR ex-FX, WS05 FX)",
     "The base takes the only bottom-up nights build (WS10), the ADR ex-FX that two workstreams agree on (WS06 and WS07 both +2.5% against WS10's +3.0%), WS05's FX schedule and WS11's regulatory drag."),
    ("FY27 adj. EBITDA margin", "36.4% -- WS05 probability-weighted macro scenarios",
     "model output -- WS07 lever build (36.6% on WS07's own revenue)",
     "WS05's figure is a sensitivity-weighted overlay on WS07's base; WS07's is bottom-up by cost line. The gap is 0.2pp."),
    ("Exit multiple, FY27E EV / adj. EBITDA", "18 / 22 / 25.5x -- model/assumptions.md, 5 Sep",
     "13.5 / 16.5 / 18.5x -- WS12 (in the base)",
     "The 5 Sep set held today's LTM multiple flat. WS12 blends a time-series regression (+0.48 turns per point of NTM growth), a peer cross-section and an intrinsic fade DCF; all three land below 22x."),
    ("Cost of equity", "10.3% -- WS12 CAPM on beta 1.161", "10.5% -- WS09 low end (in the base)",
     "WS09 estimated beta over several windows and factor models (1.16-1.32) and recommends 10.5-11.5%."),
    ("FY27 AI referral cost", "1.14% of revenue -- WS11 mid", "0.38% -- WS11 low (in the base)",
     "WS11's own evidence (Booking put AI tools at <1% of room nights in 2Q26; the Third Bridge AI expert sees no EBITDA impact for 12-24 months) puts the mid case beyond 2027."),
    ("New-business uplift", "the full WS11 incremental column ($412M FY27 base)",
     "sponsored listings + Services only (in the base)",
     "Hotel and Experiences nights are already inside 'nights and experiences booked' and therefore inside the nights build; only ads and Services sit outside GBV x take rate."),
    ("Regulatory drag", "0.75% of FY27 revenue -- WS11 mean, applied globally",
     "regional nights drag: EMEA -0.71pp, NA -0.05pp of FY27 nights growth -- WS11 median",
     "WS01's census recommends applying the drag to EMEA nights rather than to global revenue; they are the same loss expressed differently."),
    ("FY26 nights growth", "+10.0% -- WS07 lever; +9.9% -- WS10 gross of regulation",
     "model output (WS10 build net of WS11 regulation)", "Difference is the 0.15pp regulatory drag."),
]


def pick(t, scen):
    return t[SIDX[scen]]


# =====================================================================================================
# 3. ENGINE
# =====================================================================================================
def build_quarters(scen):
    out, known, kshare = [], dict(QB), dict(QSHARE)
    for q in FQ:
        pq, yr = PRIOR_Q[q], QYEAR[q]
        b, sh = known[pq], kshare[pq]
        regmult = pick(ANNUAL_INPUTS[yr]["reg_mult"], scen)
        rows, nights = {}, 0.0
        for i, rg in enumerate(REGIONS):
            g = REGIONAL_G[q][scen][i] / 100.0
            drag = regmult * REG_DRAG_PP[yr][rg] / 100.0
            n0 = b["nights"] * sh[rg]
            n1 = n0 * (1 + g - drag)
            rows[rg] = dict(prior=n0, growth_pct=100 * g, drag_pp=100 * drag, nights=n1)
            nights += n1
        adr_exfx = ADR_EXFX_Q[q][scen] / 100.0
        rev_fx, adr_fx = [x / 100.0 for x in FX_Q[q][scen]]
        adr = b["adr"] * (1 + adr_exfx) * (1 + adr_fx)
        gbv = nights * adr
        take = b["take"] + pick(ANNUAL_INPUTS[yr]["take_bps"], scen) / 10000.0
        wedge = (1 + rev_fx) / (1 + adr_fx) - 1.0
        core = gbv * take * (1 + wedge)
        out.append(dict(quarter=q, scenario=scen, prior_quarter=pq, year=yr, regions=rows,
                        nights=nights, nights_yoy_pct=100 * (nights / b["nights"] - 1),
                        adr_exfx_pct=100 * adr_exfx, adr_fx_pp=100 * adr_fx, adr=adr,
                        adr_yoy_pct=100 * (adr / b["adr"] - 1), gbv=gbv,
                        gbv_yoy_pct=100 * (gbv / b["gbv"] - 1), take_rate_pct=100 * take,
                        rev_fx_pp=100 * rev_fx, fx_wedge_pp=100 * wedge, core_revenue=core,
                        prior_revenue=b["rev"]))
        known[q] = dict(nights=nights, gbv=gbv, adr=adr, rev=core, take=take)
        kshare[q] = {rg: rows[rg]["nights"] / nights for rg in REGIONS}
    return out


def build_annual(scen):
    qs = {r["quarter"]: r for r in build_quarters(scen)}
    prev = dict(FY25)
    prev_share = dict(FY25_SHARE)
    V = {k: pick(v, scen) for k, v in VAL_INPUTS.items()}
    shares = V["shares_2q26"]
    net_cash = V["net_cash_2q26"]
    out = []
    for yr in YEARS:
        I = {k: pick(v, scen) for k, v in ANNUAL_INPUTS[yr].items()}
        if yr == 2026:
            qlist = ["3Q26", "4Q26"]
            nights = H1_26["nights"] + sum(qs[q]["nights"] for q in qlist)
            gbv = H1_26["gbv"] + sum(qs[q]["gbv"] for q in qlist)
            core = H1_26["rev"] + sum(qs[q]["core_revenue"] for q in qlist)
            take_assumed = (H1_26["rev"] + sum(qs[q]["gbv"] * qs[q]["take_rate_pct"] / 100 for q in qlist)) / gbv
            reg_rows = {rg: dict(nights=qs["4Q26"]["regions"][rg]["nights"]) for rg in REGIONS}
            share_next = {rg: qs["4Q26"]["regions"][rg]["nights"] / qs["4Q26"]["nights"] for rg in REGIONS}
        elif yr == 2027:
            qlist = ["1Q27", "2Q27", "3Q27", "4Q27"]
            nights = sum(qs[q]["nights"] for q in qlist)
            gbv = sum(qs[q]["gbv"] for q in qlist)
            core = sum(qs[q]["core_revenue"] for q in qlist)
            take_assumed = sum(qs[q]["gbv"] * qs[q]["take_rate_pct"] / 100 for q in qlist) / gbv
            reg_rows = {rg: dict(nights=sum(qs[q]["regions"][rg]["nights"] for q in qlist)) for rg in REGIONS}
            share_next = {rg: reg_rows[rg]["nights"] / nights for rg in REGIONS}
        else:
            g = pick(NIGHTS_2028, scen)
            drag = sum(prev_share[rg] * I["reg_mult"] * REG_DRAG_PP[yr][rg] / 100.0 for rg in REGIONS)
            nights = prev["nights"] * (1 + g - drag)
            adr_exfx = pick(ADR_EXFX_2028, scen)
            rev_fx, adr_fx = [x / 100.0 for x in FX_2028[scen]]
            adr = prev["adr"] * (1 + adr_exfx) * (1 + adr_fx)
            gbv = nights * adr
            take = prev["take_assumed"] + I["take_bps"] / 10000.0
            take_assumed = take
            core = gbv * take * ((1 + rev_fx) / (1 + adr_fx))
            reg_rows = {rg: dict(nights=nights * prev_share[rg]) for rg in REGIONS}
            share_next = dict(prev_share)
        adr = gbv / nights
        take_rate = core / gbv
        nb_incr = I["new_business"] - FY25["new_business"] * core / FY25["rev"]
        revenue = core + nb_incr
        # cost lines
        cor = (prev["cor"] / prev["gbv"]) * (1 + I["cor_per_gbv"]) * gbv
        ops = (prev["ops"] / prev["nights"]) * (1 + I["ops_cpn"]) * nights
        pdv = prev["pd"] * (1 + I["pd_cash"])
        bpm = prev["bpm"] * (1 + I["bpm_cash"])
        fop = prev["fop"] * (1 + I["fop_cash"])
        ga = prev["ga"] * (1 + I["ga_cash"])
        nb_cost = nb_incr * (1 - V["nb_incr_margin"])
        ai_cost = revenue * I["ai_referral_pct"]
        addb = revenue * I["addback_pct"]
        cash_costs = cor + ops + pdv + bpm + fop + ga + nb_cost + ai_cost
        adj_uncapped = revenue - cash_costs + addb
        adj = min(adj_uncapped, revenue * V["margin_cap"])
        sbc = prev["sbc"] * (1 + I["sbc_growth"])
        da = revenue * I["da_pct"]
        op_income = adj - sbc - addb
        pretax = op_income + I["int_income"] - I["int_expense"]
        net_income = pretax * (1 - I["eff_tax_rate"])
        cash_tax = revenue * I["cash_tax_pct"]
        d_unearned = revenue * I["d_unearned_pct"]
        capex = revenue * I["capex_pct"]
        wc = revenue * I["wc_resid_pct"]
        other_income = 0.0          # WS07's projection sets other income/(expense) to zero
        fcf = adj + I["int_income"] - I["int_expense"] + other_income - cash_tax + d_unearned + wc - capex
        sbcfcf = fcf - sbc
        px = V["price"] * (1 + V["price_growth"]) ** (yr - 2026)
        wh = sbc * V["withholding_pct"]
        shares = shares - I["buybacks"] / px + sbc / px * (1 - V["withholding_pct"])
        d_fcf = fcf - H1_26["fcf"] if yr == 2026 else fcf
        d_bb = I["buybacks"] - H1_26["buybacks"] if yr == 2026 else I["buybacks"]
        d_wh = wh - H1_26["withholding"] if yr == 2026 else wh
        net_cash = net_cash + d_fcf - d_bb - d_wh
        out.append(dict(
            scenario=scen, year=yr, nights=nights, nights_yoy_pct=100 * (nights / prev["nights"] - 1),
            adr=adr, adr_yoy_pct=100 * (adr / prev["adr"] - 1), gbv=gbv,
            gbv_yoy_pct=100 * (gbv / prev["gbv"] - 1), take_rate_pct=100 * take_rate,
            take_rate_assumed_pct=100 * take_assumed,
            core_revenue=core, new_business_incr=nb_incr, revenue=revenue,
            revenue_yoy_pct=100 * (revenue / prev["rev"] - 1),
            cor=cor, ops=ops, pd=pdv, bpm=bpm, fop=fop, ga=ga, nb_cost=nb_cost, ai_cost=ai_cost,
            cash_costs=cash_costs, addbacks=addb, adj_ebitda_uncapped=adj_uncapped,
            adj_ebitda_margin_uncapped_pct=100 * adj_uncapped / revenue, adj_ebitda=adj,
            adj_ebitda_margin_pct=100 * adj / revenue, sbc=sbc, sbc_pct_rev=100 * sbc / revenue,
            da=da, gaap_op_income=op_income, gaap_op_margin_pct=100 * op_income / revenue,
            interest_income=I["int_income"], interest_expense=I["int_expense"], pretax=pretax,
            eff_tax_rate_pct=100 * I["eff_tax_rate"], net_income=net_income, eps=net_income / shares,
            cash_taxes=cash_tax, d_unearned=d_unearned, capex=capex, wc_resid=wc, fcf=fcf,
            fcf_margin_pct=100 * fcf / revenue, fcf_conv_pct=100 * fcf / adj, sbc_adj_fcf=sbcfcf,
            sbc_adj_fcf_margin_pct=100 * sbcfcf / revenue, buybacks=I["buybacks"], withholding=wh,
            share_price=px, shares_end=shares, fcf_per_share=fcf / shares,
            sbc_adj_fcf_per_share=sbcfcf / shares, net_cash=net_cash, regions=reg_rows))
        prev = dict(rev=revenue, nights=nights, gbv=gbv, adr=adr, take=take_rate,
                    take_assumed=take_assumed, cor=cor, ops=ops,
                    pd=pdv, bpm=bpm, fop=fop, ga=ga, sbc=sbc, adj=adj)
        prev_share = share_next
    return out


def quarterly_pl(scen, annual):
    """Attach an adj. EBITDA path to the forecast quarters.

    2026: 1Q and 2Q are actual, 3Q and 4Q come from WS07's 5 Nov card. Those four margins are already
    consistent with the FY2026 margin (they reproduce it on a revenue weighting).
    2027: each quarter takes the FY2027 margin plus its own 2026 seasonal spread, then a constant
    correction so the revenue-weighted quarters reproduce the FY2027 margin exactly. Using the 2026
    spread rather than the 2023-2025 mean keeps 3Q27 continuous with the 3Q26 card margin."""
    A = {a["year"]: a for a in annual}
    qs = build_quarters(scen)
    for r in qs:
        qlist = ["3Q26", "4Q26"] if r["year"] == 2026 else ["1Q27", "2Q27", "3Q27", "4Q27"]
        wt = r["core_revenue"] / sum(x["core_revenue"] for x in qs if x["quarter"] in qlist)
        r["new_business_incr"] = A[r["year"]]["new_business_incr"] * wt
        r["revenue"] = r["core_revenue"] + r["new_business_incr"]
        r["revenue_yoy_pct"] = 100 * (r["revenue"] / r["prior_revenue"] - 1)
    m26 = A[2026]["adj_ebitda_margin_pct"]
    m27 = A[2027]["adj_ebitda_margin_pct"]
    spread = {"1Q27": fl(PANEL["1Q26"]["adj_ebitda_margin_pct"]) - m26,
              "2Q27": fl(PANEL["2Q26"]["adj_ebitda_margin_pct"]) - m26,
              "3Q27": Q_MARGIN_26["3Q26"][scen] - m26,
              "4Q27": Q_MARGIN_26["4Q26"][scen] - m26}
    q27 = [r for r in qs if r["year"] == 2027]
    delta = -sum(spread[r["quarter"]] * r["revenue"] for r in q27) / sum(r["revenue"] for r in q27)
    for r in qs:
        q = r["quarter"]
        m = Q_MARGIN_26[q][scen] if q in Q_MARGIN_26 else m27 + spread[q] + delta
        r["adj_ebitda_margin_pct"] = m
        r["adj_ebitda"] = r["revenue"] * m / 100.0
    return qs


# =====================================================================================================
# 4. VALUATION
# =====================================================================================================
def dcf(fcf0, g_start, years, g_end, coe, g_term):
    pv, f = 0.0, fcf0
    n = int(years)
    for t in range(1, n + 1):
        gt = g_start + (g_end - g_start) * (t - 1) / max(n - 1, 1)
        f *= (1 + gt)
        pv += f / (1 + coe) ** t
    return pv + (f * (1 + g_term) / (coe - g_term)) / (1 + coe) ** n


def dcf_constant(fcf0, g, years, coe, g_term):
    """Constant growth for `years`, then a Gordon terminal. This is the 5 Sep note's reverse-DCF
    convention and the closed form used on the Valuation sheet's reverse-DCF grid, so the two agree."""
    n = int(years)
    a = (1 + g) / (1 + coe)
    pv = fcf0 * n * a if abs(a - 1.0) < 1e-12 else fcf0 * a * (1 - a ** n) / (1 - a)
    f_n = fcf0 * (1 + g) ** n
    return pv + f_n * (1 + g_term) / (coe - g_term) / (1 + coe) ** n


def implied_growth(target_ev, fcf0, years, coe, g_term):
    """Constant growth that equates the PV to today's EV. Matches analysis/src/abnb_driver_model.py."""
    lo, hi = -0.20, 0.60
    for _ in range(300):
        mid = (lo + hi) / 2
        if dcf_constant(fcf0, mid, years, coe, g_term) < target_ev:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def valuation(annual, scen):
    A = {a["year"]: a for a in annual}
    V = {k: pick(v, scen) for k, v in VAL_INPUTS.items()}
    f27, f28 = A[2027], A[2028]
    px = {}
    px["EV / adj. EBITDA, FY27E"] = (V["exit_ev_ebitda"] * f27["adj_ebitda"] + f27["net_cash"]) / f27["shares_end"]
    px["EV / FCF, FY27E"] = (V["exit_ev_fcf"] * f27["fcf"] + f27["net_cash"]) / f27["shares_end"]
    px["P / SBC-adjusted FCF, FY27E"] = V["exit_p_sbcfcf"] * f27["sbc_adj_fcf"] / f27["shares_end"]
    px["P / earnings proxy, FY27E"] = V["exit_p_earnings"] * f27["eps"]
    px["EV / adj. EBITDA, FY28E"] = (V["exit_ev_ebitda"] * f28["adj_ebitda"] + f28["net_cash"]) / f28["shares_end"]
    g0 = V["dcf_start_growth"]
    ev = dcf(f27["fcf"], g0, V["dcf_years"], V["terminal_growth"], V["cost_of_equity"], V["terminal_growth"])
    px["DCF on FCF"] = (ev + f27["net_cash"]) / f27["shares_end"]
    ev2 = dcf(f27["sbc_adj_fcf"], g0, V["dcf_years"], V["terminal_growth"], V["cost_of_equity"], V["terminal_growth"])
    px["DCF on SBC-adjusted FCF"] = (ev2 + f27["net_cash"]) / f27["shares_end"]
    # legacy 5 Sep multiples, kept as the documented alternative
    legacy = {"Bear": 18.0, "Base": 22.0, "Bull": 25.5}[scen]
    px["EV / adj. EBITDA, FY27E (5 Sep multiples 18/22/25.5x)"] = \
        (legacy * f27["adj_ebitda"] + f27["net_cash"]) / f27["shares_end"]
    rows = [dict(scenario=scen, lens=k, price=v, upside_pct=100 * (v / V["price"] - 1)) for k, v in px.items()]
    # the football field spans the six primary lenses; the SBC-adjusted DCF and the legacy 5 Sep
    # multiples are shown but excluded, so the workbook and this mirror agree
    core = {k: v for k, v in px.items() if "5 Sep" not in k and k != "DCF on SBC-adjusted FCF"}
    rows += [dict(scenario=scen, lens="Football field low", price=min(core.values()),
                  upside_pct=100 * (min(core.values()) / V["price"] - 1)),
             dict(scenario=scen, lens="Football field high", price=max(core.values()),
                  upside_pct=100 * (max(core.values()) / V["price"] - 1)),
             dict(scenario=scen, lens="Football field mean", price=sum(core.values()) / len(core),
                  upside_pct=100 * (sum(core.values()) / len(core) / V["price"] - 1))]
    return rows, px, g0


def reverse_dcf():
    V = {k: pick(v, "Base") for k, v in VAL_INPUTS.items()}
    ev_today = V["price"] * V["shares_2q26"] - V["net_cash_2q26"]
    rows = []
    for label, base in [("Reported FCF (LTM $%.0fM)" % LTM_FCF, LTM_FCF),
                        ("SBC-adjusted FCF (LTM $%.0fM)" % (LTM_FCF - LTM_SBC), LTM_FCF - LTM_SBC)]:
        for coe in (0.09, 0.10, 0.105, 0.11):
            for g in (0.025, 0.030, 0.040):
                rows.append(dict(basis=label, cost_of_equity_pct=100 * coe, terminal_growth_pct=100 * g,
                                 implied_10y_fcf_growth_pct=100 * implied_growth(ev_today, base, V["dcf_years"], coe, g)))
    return rows, ev_today


# =====================================================================================================
# 5. WRITE
# =====================================================================================================
def write_csv(path, rows, cols=None):
    if not rows:
        return
    cols = cols or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: (round(r[c], 4) if isinstance(r.get(c), float) else r.get(c, "")) for c in cols})


def main():
    quarterly, annual, valrows = [], [], []
    prices = {}
    for scen in SCENARIOS:
        ann = build_annual(scen)
        qs = quarterly_pl(scen, ann)
        for r in qs:
            row = {k: v for k, v in r.items() if k != "regions"}
            for rg in REGIONS:
                row[f"{rg}_nights_m"] = r["regions"][rg]["nights"]
                row[f"{rg}_growth_pct"] = r["regions"][rg]["growth_pct"]
                row[f"{rg}_reg_drag_pp"] = r["regions"][rg]["drag_pp"]
            quarterly.append(row)
        for a in ann:
            row = {k: v for k, v in a.items() if k != "regions"}
            for rg in REGIONS:
                row[f"{rg}_nights_m"] = a["regions"][rg]["nights"]
            annual.append(row)
        v, px, _ = valuation(ann, scen)
        valrows += v
        prices[scen] = px
    rev, ev_today = reverse_dcf()

    write_csv(OD("13_model_quarterly.csv"), quarterly)
    write_csv(OD("13_model_annual.csv"), annual)
    write_csv(OD("13_valuation_summary.csv"),
              valrows + [dict(scenario="Base",
                              lens=f"Reverse DCF | {r['basis']} | CoE {r['cost_of_equity_pct']:.1f}% | g {r['terminal_growth_pct']:.1f}%",
                              price="", upside_pct=r["implied_10y_fcf_growth_pct"]) for r in rev],
              cols=["scenario", "lens", "price", "upside_pct"])

    A = {a["year"]: a for a in annual if a["scenario"] == "Base"}
    grid = []
    for g in [0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16]:
        for m in [0.32, 0.34, 0.355, 0.365, 0.375, 0.39, 0.41]:
            r_ = A[2026]["revenue"] * (1 + g)
            e = r_ * m
            for mult in [12.0, 13.5, 15.0, 16.5, 18.0, 18.5, 20.0, 22.0, 25.5]:
                p = (mult * e + A[2027]["net_cash"]) / A[2027]["shares_end"]
                grid.append(dict(fy27_revenue_growth_pct=100 * g, fy27_margin_pct=100 * m,
                                 exit_ev_ebitda_x=mult, fy27_revenue_musd=r_, fy27_adj_ebitda_musd=e,
                                 price=p, upside_vs_spot_pct=100 * (p / 181.94 - 1)))
    write_csv(OD("13_scenario_grid.csv"), grid)

    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "xlbuild13", os.path.join(os.path.dirname(os.path.abspath(__file__)), "13_excel_builder.py"))
    XLB = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(XLB)
    checks = XLB.build_workbook(quarterly, annual, valrows, rev, grid, prices, ev_today)
    write_csv(OD("13_reconciliation.csv"), checks)

    for a in annual:
        if a["scenario"] == "Base":
            print(f"FY{a['year']} base: rev ${a['revenue']:,.0f}M ({a['revenue_yoy_pct']:+.1f}%) "
                  f"| EBITDA ${a['adj_ebitda']:,.0f}M ({a['adj_ebitda_margin_pct']:.1f}%) "
                  f"| FCF ${a['fcf']:,.0f}M | FCF/sh ${a['fcf_per_share']:.2f} "
                  f"| SBC-adj FCF/sh ${a['sbc_adj_fcf_per_share']:.2f} | shares {a['shares_end']:.0f}M "
                  f"| EPS ${a['eps']:.2f}")
    for scen in SCENARIOS:
        print(scen, {k: round(v, 0) for k, v in prices[scen].items()})
    bad = [c for c in checks if c["status"] != "ok"]
    print(f"reconciliation: {len(checks)} checks, {len(bad)} mismatches")
    for c in bad[:15]:
        print("  MISMATCH", c["item"], c["python_value"], c["workbook_value"])


if __name__ == "__main__":
    main()
