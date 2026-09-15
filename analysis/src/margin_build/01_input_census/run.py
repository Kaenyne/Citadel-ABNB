"""WS01 input census: every repo input that could bear on a cost line, an add-back or a below-EBITDA item.

Builds (from the inline registry, opening every file to record real first/last periods and n):
  data/processed/margin_build/01_input_census/01_input_census.csv
  data/processed/margin_build/01_input_census/01_gaps.csv
  data/processed/margin_build/01_input_census/01_census_summary_by_line.csv
Validates: every file_path exists, every script_path exists (when given), required columns present.
Exit code 0 on success, 1 on any validation failure.

Run from the worktree root:  python analysis/src/margin_build/01_input_census/run.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]  # <repo>/analysis/src/margin_build/01_input_census/run.py
OUT = ROOT / "data" / "processed" / "margin_build" / "01_input_census"
OUT.mkdir(parents=True, exist_ok=True)

COLS = [
    "series_id", "description", "file_path", "script_path", "frequency", "first_period", "last_period", "n_obs",
    "pit_lag_days", "target_lines", "mechanism", "prior_evidence", "status", "suggested_method",
]
GAP_COLS = [
    "gap_id", "input", "target_lines", "mechanism", "suggested_source", "url_pattern_or_field", "reachability",
    "frequency", "history", "pit_note", "priority", "ws04_action",
]

# ----------------------------------------------------------------------------------------------------------------
# period parsing
# ----------------------------------------------------------------------------------------------------------------
_PATS = [
    (re.compile(r"^(\d)Q(\d{2})$"), lambda m: (2000 + int(m.group(2)), int(m.group(1)) * 3, 0)),
    (re.compile(r"^(\d{4})Q(\d)$"), lambda m: (int(m.group(1)), int(m.group(2)) * 3, 0)),
    (re.compile(r"^(?:FY|fy)(\d{4})[A-Za-z]*$"), lambda m: (int(m.group(1)), 12, 0)),
    (re.compile(r"^(\d{4})-(\d{2})-(\d{2})"), lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    (re.compile(r"^(\d{4})-(\d{2})$"), lambda m: (int(m.group(1)), int(m.group(2)), 0)),
    (re.compile(r"^(\d{4})$"), lambda m: (int(m.group(1)), 12, 0)),
    (re.compile(r"^(\d{4})\.0$"), lambda m: (int(m.group(1)), 12, 0)),
]
PERIOD_CANDIDATES = [
    "quarter", "period", "print_quarter", "quarter_end", "date", "Date", "observation_date", "month", "month_end",
    "settlement_date", "year", "fiscal_year", "run_date", "as_of", "print", "target_period", "quarter_label",
    "print_date", "obs_date", "start_month",
]


def pkey(s):
    s = str(s).strip()
    for pat, fn in _PATS:
        m = pat.match(s)
        if m:
            return fn(m)
    return None


def read_table(path: Path) -> pd.DataFrame | None:
    try:
        if path.suffix == ".csv":
            return pd.read_csv(path, comment="#", low_memory=False, on_bad_lines="skip")
        if path.suffix == ".gz":
            return pd.read_csv(path, compression="gzip", low_memory=False, nrows=200000)
        if path.suffix == ".json":
            return None
    except Exception as exc:  # noqa: BLE001
        print(f"  warn: could not read {path.relative_to(ROOT)}: {exc}")
    return None


def periods_from_table(df: pd.DataFrame, pcol: str | None):
    cols = [pcol] if pcol else [c for c in PERIOD_CANDIDATES if c in df.columns]
    for c in cols:
        if c not in df.columns:
            continue
        keys = [(pkey(v), v) for v in df[c].dropna().astype(str)]
        keys = [(k, v) for k, v in keys if k is not None]
        if len(keys) >= max(2, int(0.5 * max(1, df[c].notna().sum()))):
            keys.sort(key=lambda kv: kv[0])
            return str(keys[0][1]), str(keys[-1][1]), len(keys)
    return "", "", len(df)


def fill_periods(row: dict):
    """Fill first_period/last_period/n_obs from the file unless the registry row already gives them."""
    if row.get("first_period") and row.get("last_period") and row.get("n_obs") not in (None, ""):
        return
    p = ROOT / row["file_path"]
    if p.is_dir():
        files = sorted(x.name for x in p.iterdir() if x.is_file())
        row.setdefault("n_obs", len(files)) if row.get("n_obs") in (None, "") else None
        if row.get("n_obs") in (None, ""):
            row["n_obs"] = len(files)
        if not row.get("first_period"):
            qs = sorted({(pkey(f[:4]), f[:4]) for f in files if pkey(f[:4])}, key=lambda kv: kv[0])
            if qs:
                row["first_period"], row["last_period"] = qs[0][1], qs[-1][1]
        return
    df = read_table(p)
    if df is None:
        if row.get("n_obs") in (None, ""):
            row["n_obs"] = ""
        return
    f, l, n = periods_from_table(df, row.pop("pcol", None))
    if not row.get("first_period"):
        row["first_period"] = f
    if not row.get("last_period"):
        row["last_period"] = l
    if row.get("n_obs") in (None, ""):
        row["n_obs"] = n


# ----------------------------------------------------------------------------------------------------------------
# registry
# ----------------------------------------------------------------------------------------------------------------
REG: list[dict] = []


def R(series_id, description, file_path, script_path="", frequency="quarterly", pit_lag_days=40, target_lines="",
      mechanism="", prior_evidence="", status="available", suggested_method="M1 driver", first_period="",
      last_period="", n_obs="", pcol=None):
    REG.append(dict(series_id=series_id, description=description, file_path=file_path, script_path=script_path,
                    frequency=frequency, first_period=first_period, last_period=last_period, n_obs=n_obs,
                    pit_lag_days=pit_lag_days, target_lines=target_lines, mechanism=mechanism,
                    prior_evidence=prior_evidence, status=status, suggested_method=suggested_method, pcol=pcol))


ON = "data/processed/overnight/"
FM = "data/processed/forecast_methods/"
SRC = "analysis/src/"

# ---- P: disclosed P&L panels ------------------------------------------------------------------------------------
R("P01_gaap_costlines", "GAAP cost lines (CoR, ops&support, product dev, S&M, G&A, restructuring), SBC total, operating income, adj. EBITDA, % of revenue; Q4 = FY less 9M; XBRL companyfacts + letters",
  "data/processed/abnb_quarterly_costlines.csv", SRC + "abnb_costlines_from_xbrl.py", pit_lag_days=40,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;margin_total",
  mechanism="The target series themselves (GAAP basis); every method scores against these or the ex-SBC stack.",
  prior_evidence="Backbone of margin-drivers, 07, 31a/31b, predictive/04. WS02 rebuilds with provenance and 1Q19-4Q19 pre-IPO quarters.",
  suggested_method="M1 driver;M2 ts;M6 cycle")
R("P02_cash_cost_stack", "Cash (ex-SBC) cost per line, SBC by function (ops/pd/sm/ga), D&A, other add-backs, identity to adj. EBITDA, per night and % of revenue; letters footnotes",
  "data/processed/abnb_quarterly_cost_stack_exsbc.csv", SRC + "abnb_exsbc_stack.py", pit_lag_days=40,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;da;addbacks;margin_total",
  mechanism="Adj. EBITDA = revenue - cash lines - restructuring + D&A + add-backs; the six cash lines are the objects the margin methods forecast.",
  prior_evidence="Identity holds within $1.7M except 4Q23 (-$36M letter-vs-XBRL Q4 derivation). 31b: only CoR has a promotable elasticity (GBV +1.01, n 14).",
  suggested_method="M1 driver;M2 ts;M7 below-EBITDA")
R("P03_cost_lines_per_night", "22-quarter panel: each line GAAP and cash, $ per night, per $100 GBV, % revenue, y/y; brand+performance vs field-ops S&M split (10-Q three-month tables, Q4 = 10-K less 9M); D&A, interest income, tax, FCF, unearned-fee change",
  ON + "07_cost_lines_per_night.csv", SRC + "overnight/07_cost_lines_per_night.py", pit_lag_days=42,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;da;int_inc;tax;fcf_timing",
  mechanism="Per-unit cost bases (per night, per $ GBV) are the natural forecasting units; the brand/field split separates media (reversible) from headcount (sticky).",
  prior_evidence="07: 85% of the rise in cash cost per night since 2Q22 is S&M; 1H26 brand+perf +32%, field +24%. predictive/04: prior-quarter S&M deleverage predicts next margin surprise r -0.62, n 14, LOO 2.61 vs 2.79 guide.",
  suggested_method="M1 driver;M4 alt")
R("P04_cost_components_annual", "Disclosed cost components FY2019-FY2025: merchant fees+chargebacks % GBV, brand/perf and field-ops $, XBRL advertising, headcount, third-party support workers, cloud and insurance cost deltas, payroll deltas, non-income tax delta, interest income, tax provision current/deferred, cash taxes, lease cost, purchase obligations, hosting commitment, D&A, capex, revenue per employee",
  ON + "07_cost_components_annual.csv", SRC + "overnight/07_cost_lines_per_night.py", frequency="annual", pit_lag_days=50,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;da;int_inc;tax;capex",
  mechanism="Sub-line drivers management discloses only annually (payments rate, cloud delta, insurance delta, headcount, hosting commitments) anchor the per-unit assumptions.",
  prior_evidence="07: payment processing 1.82% of GBV (+/-10bp, derived from MD&A deltas); hosting commitment $672M->$1.7B through 2031; revenue per employee fell 1.8% in 2025.",
  status="available", suggested_method="M1 driver;M4 alt", first_period="FY2019", last_period="FY2025", n_obs=39)
R("P05_kpi_panel_quarterly", "Definitive KPI panel, 119 columns: nights, GBV, ADR, revenue, adj. EBITDA, SBC, FCF, buybacks, RSU withholding, diluted shares, GAAP lines, op income, CFO, capex, net income, tax, cash/investments, funds held, unearned fees, debt, regional nights and ADR y/y, app share, cross-border share, etc.",
  ON + "02_kpi_panel_quarterly.csv", SRC + "overnight/02_kpi_panel.py", pit_lag_days=40,
  target_lines="rev_drivers;sbc;shares;tax;int_inc;fcf_timing;margin_total",
  mechanism="One-stop denominators (nights, GBV, ADR, take rate) and balance-sheet stocks (funds held, cash) for every per-unit and yield calculation.",
  prior_evidence="342 verbatim quotes re-verify; 02_metric_coverage.csv says when each series starts/stops (cross-border share stops 1Q24, active listings 4Q25).",
  suggested_method="M1 driver;M7 below-EBITDA")
R("P06_kpi_panel_long", "Source quotes behind the KPI panel (1,050 rows, letter sentence per number)", ON + "02_kpi_panel_long.csv",
  SRC + "overnight/02_kpi_panel.py", pit_lag_days=40, target_lines="rev_drivers;margin_total",
  mechanism="Provenance for every panel cell; lets WS02 cite the letter for each value.", prior_evidence="Used by WS02/15 crosschecks.",
  suggested_method="M1 driver", pcol="quarter")
R("P07_margin_bridge", "Adj. EBITDA margin bridge FY22->FY25 by line (cost per night), revenue per night (take rate, FX, ADR ex-FX), add-backs",
  "data/processed/abnb_margin_bridge.csv", SRC + "abnb_margin_bridge.py", frequency="annual", pit_lag_days=50,
  target_lines="margin_total;cor;ops;pd;sm_brand;sm_field;ga", mechanism="Decomposes margin change into unit-cost and revenue-per-night effects; template for the forward bridge.",
  prior_evidence="FY22->25 +0.5pt: revenue/night +5.1, S&M -4.2. 31b corrects: ADR ex-FX +3.7 is +5.4 size/price net of -2.5 regional mix.",
  suggested_method="M1 driver;M6 cycle", first_period="FY2022", last_period="FY2025", n_obs="")
R("P08_margin_scenarios", "Base/bear/bull FY2026E, FY2027E, 3Q26E, 4Q26E margin scenarios (5 Sep)", "data/processed/abnb_margin_scenarios.csv",
  SRC + "abnb_margin_bridge.py", frequency="scenario", pit_lag_days=0, target_lines="margin_total",
  mechanism="Earliest house scenario set; a comparison column only.", prior_evidence="07 reconciles: base FY26 +0.25pt, FY27 +0.05pt; bear too kind on S&M.",
  suggested_method="M6 cycle", first_period="3Q26E", last_period="FY2027E", n_obs="")
R("P09_lever_model_fy26_28", "WS07 lever-by-lever margin model: levers (bear/base/bull, evidence strings), attribution, results, path-to-40% Monte Carlo",
  ON + "07_margin_levers_fy26_fy28.csv", SRC + "overnight/07_margin_lever_model.py", frequency="scenario", pit_lag_days=0,
  target_lines="margin_total;cor;ops;pd;sm_brand;sm_field;ga;sbc;int_inc;tax;fcf_timing;capex",
  mechanism="Cost lines driven by natural unit (CoR by GBV, ops by nights, others by cash growth); runs to GAAP op margin, FCF, SBC-adjusted FCF.",
  prior_evidence="Base 36.1/36.6/37.5%; P(>=40% FY28) 21%; FCF/EBITDA 99/95/93%; working-capital residual -1.1% of revenue (FY24 -$140M, FY25 -$139M).",
  suggested_method="M1 driver;M7 below-EBITDA", first_period="FY2026E", last_period="FY2028E", n_obs="")
R("P10_ops_initiatives", "22 operational initiatives since 2022 scored realised / in progress / not evidenced, with cost line, claim source and filed evidence",
  ON + "07_ops_initiatives.csv", SRC + "overnight/07_ops_initiatives.py", frequency="event", pit_lag_days=0,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc", mechanism="Step-dummy candidates (AI support, payments reset, third-party support network, RSU/buyback policy) for line models.",
  prior_evidence="14 realised, 3 in progress, 5 not evidenced (AI engineering productivity, cloud efficiency, performance-marketing efficiency, AI spend in guide, hotels).",
  suggested_method="M4 alt", first_period="2020-Q4", last_period="2026-Q2", n_obs=22)
R("P11_peer_margin_benchmark", "10-company peer benchmark FY2021-FY2025 (ABNB, BKNG, EXPE, TRIP, UBER, DASH, META, NFLX, DUOL, SPOT): EBITDA proxy margin, SBC %, S&M %, FCF, revenue per employee",
  ON + "07_peer_margin_benchmark.csv", SRC + "overnight/07_peer_benchmark.py", frequency="annual", pit_lag_days=60,
  target_lines="margin_total;sbc;sm_brand;pd", mechanism="Peer cost mixes bound the realistic margin ceiling and give cyclical cost-flex comparators (BKNG/EXPE marketing through 2020-22).",
  prior_evidence="07: BKNG 37.4% EBITDA proxy is the ceiling; ABNB SBC-adjusted FCF margin 24.6% vs BKNG 31.5%.", suggested_method="M6 cycle;M2 ts",
  first_period="FY2021", last_period="FY2025", n_obs="")
R("P12_abnb_vs_bkng_annual", "ABNB vs BKNG vs EXPE FY2021-FY2025: take rate, marketing % rev, SBC %, op margin, FCF conversion, buybacks % FCF, share change",
  "data/processed/abnb_vs_bkng_annual.csv", SRC + "bkng_head_to_head.py", frequency="annual", pit_lag_days=60,
  target_lines="margin_total;sbc;sm_brand;shares", mechanism="Head-to-head cost structure; BKNG marketing flex in downturns is the cyclical analogue for M6.",
  prior_evidence="margin-drivers s13: the 12pt GAAP op-margin gap is SBC (13.0% vs 2.3%).", suggested_method="M6 cycle", first_period="FY2021", last_period="FY2025", n_obs="")
R("P13_quarterly_pnl_ws30", "WS30 quarterly P&L 3Q26-4Q27 by scenario: cash lines, adj. EBITDA, SBC, op income, interest income/expense, tax rate, net income, diluted shares, EPS proxy, per-unit costs",
  ON + "30_quarterly_pnl.csv", SRC + "overnight/30_margin_walk.py", frequency="scenario", pit_lag_days=0,
  target_lines="margin_total;cor;ops;pd;sm_brand;sm_field;ga;sbc;int_inc;tax;shares",
  mechanism="Existing quarterly forward P&L; the margin harness compares new methods against it.", prior_evidence="Base FY26 36.2%, FY27 36.4%; 31b base is 0.9pt lower on FY26 (brand +27% vs H2 phase-down).",
  suggested_method="M2 ts;M7 below-EBITDA", first_period="3Q26", last_period="4Q27", n_obs="")
R("P14_margin_walk_ws30", "WS30 margin walk 4Q25 -> 4Q26 by scenario with FY summary, assumptions and management-language rows",
  ON + "30_margin_walk.csv", SRC + "overnight/30_margin_walk.py", frequency="scenario", pit_lag_days=0, target_lines="margin_total",
  mechanism="Quarterly walk of margin y/y by driver.", prior_evidence="Companion files 30_fy_summary.csv, 30_margin_assumptions.csv, 30_mgmt_language.csv.",
  suggested_method="M2 ts", first_period="4Q25", last_period="4Q26", n_obs="")
R("P15_31b_line_elasticities", "31b: elasticity of each cash line to its natural driver (1Q23-2Q26 y/y logs, n 14), t, LOO range, intercept (fixed) share, per-unit trend, promote flag",
  ON + "31b_line_elasticities.csv", SRC + "overnight/31b_operating_profile.py", frequency="parameter", pit_lag_days=0,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga", mechanism="The current M1 parameter set: CoR-GBV 1.01 (promoted); ops-nights 1.39 LOO 0.41-1.66 (imposed 1.0); four discretionary lines imposed 0.",
  prior_evidence="Only CoR passes the promotion rule (n>=12, |t|>2, LOO range <0.6, admissible sign). Fixed shares G&A 61%, PD 32%, ops 19%, CoR 1%.",
  suggested_method="M1 driver", first_period="1Q23", last_period="2Q26", n_obs="")
R("P16_31b_decomposition_annual", "31b annual margin decomposition FY2019-FY2025 and 1H26: unit-cost vs revenue-per-night effects, ADR split into regional mix / size mix / FX / LOS / price, nights leverage vs per-unit decisions",
  ON + "31b_margin_decomposition_annual.csv", SRC + "overnight/31b_operating_profile.py", frequency="annual", pit_lag_days=50,
  target_lines="margin_total;cor;ops;pd;sm_brand;sm_field;ga;rev_drivers", mechanism="Attributes every historical margin move; regional mix drag (-0.5 to -0.7pt/yr) is its own line.",
  prior_evidence="FY19->22 +39.8pt of which revenue/night +30.0; FY22->25 +0.5pt; 1H26 support +0.4, brand -3.2.", suggested_method="M1 driver;M6 cycle",
  first_period="FY2019", last_period="1H2026", n_obs="")
R("P17_31b_overlay_parameters", "31b overlay table: per line x year x profile (historical / management / base) target, trend, overlay, judgement flag, management confidence and 31a statement IDs",
  ON + "31b_overlay_parameters.csv", SRC + "overnight/31b_operating_profile.py", frequency="parameter", pit_lag_days=0,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;addbacks", mechanism="Single place the forward cost assumptions live; M1/M3 read management vs base values from here.",
  prior_evidence="Management silent on 5 of 6 lines for FY28; expansion-market count NOT DISCLOSED; brand fixed share -2% (unidentified).", suggested_method="M1 driver;M3 guide",
  first_period="FY2026E", last_period="FY2028E", n_obs="")
R("P18_31b_forward_by_profile", "31b forward margin by profile x scenario x line, quarterly 3Q26-4Q27 and annual FY26-FY28; plus 31b_margin_bridge_fy26_fy28.csv and 31b_sensitivities.csv",
  ON + "31b_forward_margin_by_profile.csv", SRC + "overnight/31b_operating_profile.py", frequency="scenario", pit_lag_days=0,
  target_lines="margin_total;cor;ops;pd;sm_brand;sm_field;ga", mechanism="Comparison column for every stage-2 method (historical 34.6 / management 37.4 / base 36.9 at FY28).",
  prior_evidence="Sensitivities FY28: support -10% +0.84; brand +5pt -0.66; take +10bp +0.47; ADR ex-FX +1pt +0.42; nights +1pt +0.34; mix 1pt NA->LatAm/APAC -0.33.",
  suggested_method="M1 driver;M6 cycle", first_period="3Q26", last_period="FY2028E", n_obs="")
R("P19_historicals_workbook", "model/ABNB_historicals.xlsx: quarterly historicals, regressions and guidance-vs-move sheets (openpyxl on py -3.13)",
  "model/ABNB_historicals.xlsx", SRC + "abnb_historicals_workbook.py", frequency="workbook", pit_lag_days=40,
  target_lines="margin_total;rev_drivers", mechanism="Workbook mirror of the historic panel for the pitch model.", prior_evidence="Built 7 Sep; carries earnings regressions.",
  status="available", suggested_method="M2 ts", first_period="1Q21", last_period="2Q26", n_obs="")
R("P20_driver_model_workbook", "model/ABNB_driver_model.xlsx (9 sheets, 2,353 formulas): regional nights x ADR x FX x take rate to adj. EBITDA, GAAP, FCF, share count, valuation; mirrored by 13_driver_model.py",
  "model/ABNB_driver_model.xlsx", SRC + "overnight/13_driver_model.py", frequency="workbook", pit_lag_days=0,
  target_lines="margin_total;sbc;da;int_inc;tax;shares;fcf_timing;capex", mechanism="The existing full P&L-to-FCF model; the margin model must reconcile to or replace its cost stack.",
  prior_evidence="Outputs in 13_model_quarterly.csv / 13_model_annual.csv (base FY27 margin 35.9%, FCF conv 95%).", suggested_method="M7 below-EBITDA",
  first_period="3Q26", last_period="FY2028E", n_obs="")
R("P21_model_annual_ws13", "13_model_annual.csv: scenario x year FY2026-FY2028 full P&L (cash lines, SBC, D&A, GAAP op income, interest, tax rate, net income, EPS, cash taxes, unearned-fee change, capex, FCF, share count)",
  ON + "13_model_annual.csv", SRC + "overnight/13_driver_model.py", frequency="scenario", pit_lag_days=0,
  target_lines="margin_total;sbc;da;int_inc;tax;shares;fcf_timing;capex", mechanism="Below-EBITDA assumptions currently in the house model (cash taxes, RSU withholding, buybacks $4.2B).",
  prior_evidence="Companion 13_model_quarterly.csv (3Q26-4Q27).", suggested_method="M7 below-EBITDA", first_period="FY2026", last_period="FY2028", n_obs="")

# ---- B: below-EBITDA, cash, balance sheet ------------------------------------------------------------------------
R("B01_fcf_bridge", "Adj. EBITDA -> CFO -> FCF bridge 1Q21-2Q26 + FY21-FY25: interest income, interest expense, tax provision, other income/expense, change in unearned fees, residual, capex, unearned fees and funds payable balances, cash taxes (10-K memo), source letter",
  "data/processed/abnb_fcf_bridge.csv", SRC + "abnb_fcf_bridge.py", pit_lag_days=40,
  target_lines="int_inc;other_inc;tax;fcf_timing;capex;da;sbc",
  mechanism="Every below-EBITDA item from the letters; CFO - capex ties to letter FCF in all 22 quarters.",
  prior_evidence="margin-drivers s12: TTM FCF margin 44.2% (3Q23) -> 36.7% (2Q26) entirely below EBITDA: taxes, RNPL float, interest income.",
  suggested_method="M7 below-EBITDA")
R("B02_capital_return_quarterly", "SBC, buybacks, RSU tax withholding, CFO, capex, FCF, diluted and basic weighted shares, net cash return, FCF per share 1Q21-2Q26 (XBRL YTD differenced; letters from 1Q23)",
  "data/processed/abnb_capital_return_quarterly.csv", SRC + "capital_return_panel.py", pit_lag_days=42,
  target_lines="sbc;shares;fcf_timing", mechanism="Share-count path = f(buyback $, price, SBC issuance, RSU withholding); EPS denominator.",
  prior_evidence="capital-return note: diluted count -4.6% y/y at 2Q26; $1.4B per 1% of count; buybacks stepped $0.5B -> $0.75B -> $1.0-1.1B/quarter.",
  suggested_method="M7 below-EBITDA")
R("B03_capital_return_scorecard", "Peer cannibal scorecard FY2021-FY2025 (ABNB, BKNG, EXPE, META, NFLX, UBER, DASH): SBC % rev/FCF, buybacks % FCF, net return, share change",
  "data/processed/capital_return_scorecard_annual.csv", SRC + "capital_return_panel.py", frequency="annual", pit_lag_days=60,
  target_lines="sbc;shares", mechanism="Benchmarks the SBC ratio path and buyback conversion.", prior_evidence="ABNB heaviest SBC load in the set (13.1% of revenue FY25).",
  suggested_method="M7 below-EBITDA", first_period="FY2021", last_period="FY2025", n_obs="")
R("B04_backlog_indicators", "Quarter-end unearned fees and funds held for clients (XBRL) with y/y, next-quarter revenue, pre-RNPL OLS fit and RNPL gap",
  "data/processed/abnb_backlog_indicators.csv", SRC + "abnb_eu_platform_and_backlog.py", pit_lag_days=42,
  target_lines="fcf_timing;int_inc;rev_drivers", mechanism="Unearned fees change is the float term in CFO; funds held x short rates is the interest-income base.",
  prior_evidence="WS08/20: unearned fees R2 0.96 in-sample but walk-forward 1.85x AR(1) (kill list: not a forecast); RNPL switched the float off (2Q26 -0.9% y/y vs revenue +16.5%).",
  suggested_method="M7 below-EBITDA;M4 alt", pcol="quarter")
R("B05_qog_cash_reality", "RNPL short-audit cash-reality panel 1Q21-2Q26: revenue, adj. EBITDA, SBC, CFO, capex, FCF, unearned fees, funds payable, cash, ST investments, restricted cash, interest income, FCF ex-float, FCF less SBC, customer float, interest-earning balances, implied annualised yield",
  "data/processed/rnpl_short_audit/qog_cash_reality_quarterly.csv", SRC + "rnpl_short_audit/", pit_lag_days=42,
  target_lines="int_inc;fcf_timing;sbc", mechanism="Implied yield on interest-earning balances (interest income / avg balances) is the M7 interest-income model; customer float split shows the RNPL drag.",
  prior_evidence="Built for the RNPL short audit (docs/rnpl-short-audit); interest yield series not yet tested against T-bill rates.",
  suggested_method="M7 below-EBITDA")
R("B06_tracker_backlog_rebuild", "Lane 1 tracker-backlog rebuild: unearned fees and funds held with RNPL-era flags, coverage ratios, circularity verdict (do not use restated unearned fees as a feature)",
  FM + "tracker_backlog/01_backlog_rebuild.csv", SRC + "forecast_methods/tracker_backlog/", pit_lag_days=42,
  target_lines="fcf_timing", mechanism="Same stocks as B04 with the harness-registered walk-forward gate results.", prior_evidence="Gate G1 walk-forward summary in 03_gate_g1_walkforward_summary.csv; restated unearned fees are on the kill list (circular).",
  suggested_method="M7 below-EBITDA")
R("B07_fx_hedge_disclosures", "10-Q/10-K derivative notes 1Q23-2Q26: designated/non-designated notional, AOCI, realised hedge gains reclassified to revenue (pp on growth), expected next-12M reclass, gross FX ex hedge; plus 28_fx_hedge_tests.csv and 28_fx_hedge_forward.csv",
  ON + "28_fx_hedge_disclosures.csv", SRC + "overnight/28_fx_hedge_disclosures.py", pit_lag_days=45,
  target_lines="rev_drivers;other_inc", mechanism="Non-designated hedge remeasurement lands in other income (expense); designated hedges shape reported revenue FX (and so margin via 84% flow-through).",
  prior_evidence="28: lag fits of hedge effect; forward drag from the next-12M disclosure. Balance-sheet FX: 10% adverse move ~$38M in other income (margin-drivers s14).",
  suggested_method="M7 below-EBITDA;M1 driver")
R("B08_multiples_monthly", "Monthly point-in-time ABNB multiples on last-reported LTM (price, diluted shares, EV, LTM revenue/EBITDA/FCF/SBC-adj FCF/net income, NTM proxies)",
  ON + "12_abnb_multiples_monthly.csv", SRC + "overnight/12_abnb_multiples_history.py", frequency="monthly", pit_lag_days=1,
  target_lines="shares;sbc", mechanism="Share price path sets buyback share retirement per $ and the grant-date value of SBC.", prior_evidence="WS12: margin moves the multiple zero (t 0.3); growth +0.48 turns per pt.",
  suggested_method="M7 below-EBITDA", pcol="month_end")
R("B09_prices_daily", "Daily closes ABNB and 19 tickers/factors (QQQ, SPY, BKNG, EXPE, MAR, HLT, ^TNX, ^VIX ...) Dec 2020-Sep 2026", ON + "09_prices_daily.csv",
  SRC + "overnight/09_stock_behaviour.py", frequency="daily", pit_lag_days=0, target_lines="shares;sbc",
  mechanism="Average price per quarter converts buyback dollars to shares; ^TNX is a rates proxy for interest income.", prior_evidence="Also data/processed/abnb_daily_close.csv (1,440 sessions).",
  suggested_method="M7 below-EBITDA", pcol="Date")
R("B10_reverse_dcf_mgmt_inputs", "Management-implied model inputs by scenario x quarter (3Q26-4Q27): nights, ADR, FX, take-rate, SBC growth, D&A %, interest income/expense, tax rate, buyback $, buyback price, RSU net, FCF conversion, margin change",
  "data/processed/reverse_dcf/mgmt_implied_inputs.csv", SRC + "reverse_dcf/", frequency="scenario", pit_lag_days=0,
  target_lines="sbc;da;int_inc;tax;shares;fcf_timing;margin_total", mechanism="The 12-13 Sep management-implied and market-implied below-EBITDA assumption sets (Street FY27 = guide + cushion).",
  prior_evidence="docs/reverse_dcf/SYNTHESIS.md: $182 mid target vs $170 spot; market-implied cases in reverse_dcf/market/.", suggested_method="M7 below-EBITDA;M5 street",
  first_period="3Q26", last_period="4Q27", n_obs="")
R("B11_options_ledger", "ABNB options ledger (Yahoo chains, runs 5-6 Sep 2026): ATM IV, straddles, skew, event classification (estimator withdrawn A08)", "data/processed/abnb_options_ledger.csv",
  SRC + "abnb_options_ledger.py", frequency="snapshot", pit_lag_days=0, target_lines="sbc",
  mechanism="Implied vol is an input to the Black-Scholes value of option grants (minor; RSUs dominate ABNB SBC).", prior_evidence="Kill list: no event-implied move until the 6 Nov weekly lists.",
  status="available", suggested_method="M7 below-EBITDA", pcol="run_date")

# ---- G: guidance, statements, consensus, reactions ------------------------------------------------------------
R("G01_guidance_ledger", "194 guidance statements from all 23 letters (159 scoreable): metric, type (range/floor/point/ceiling/qualitative), values, actual, outcome, cushion, quote; incl. adj_ebitda_margin_pct rows",
  ON + "02_guidance_ledger.csv", SRC + "overnight/02_guidance_ledger.py", frequency="event", pit_lag_days=0,
  target_lines="margin_total;guide;rev_drivers", mechanism="The margin guide (floor/ceiling/point) is the M3 object; the ledger gives every historical pairing of guide and actual.",
  prior_evidence="31a corrections: letter-sourced, so the FY24 flat-marketing and FY25 +20bp take-rate call guides are missing (S071/S072/S110 in 31a).",
  suggested_method="M3 guide", pcol="print_quarter")
R("G02_guidance_accuracy", "Guidance hit/beat/miss statistics by metric x guide type (n, mean/median distance from mid)", ON + "02_guidance_accuracy.csv",
  SRC + "overnight/02_guidance_ledger.py", frequency="summary", pit_lag_days=0, target_lines="margin_total;guide",
  mechanism="Base rates for the floor-cushion model.", prior_evidence="Mean cushion on the seven FY floor rows 1.51pt (31a).", suggested_method="M3 guide",
  first_period="4Q20", last_period="2Q26", n_obs="")
R("G03_fy_guide_revisions", "Every FY guide by print (revenue, margin, SBC, take rate ...) with revisions and the eventual actual", ON + "02_fy_guide_revisions.csv",
  SRC + "overnight/02_guidance_ledger.py", frequency="event", pit_lag_days=0, target_lines="margin_total;guide;sbc",
  mechanism="February floor -> November point pattern; the raise/hold decision is the 5 Nov language object.", prior_evidence="Floor beats FY24 +140bp, FY25 +60bp (31a corrects the 60-180bp claim).",
  suggested_method="M3 guide", pcol="print_quarter")
R("G04_guidance_cushion_series", "Revenue guide ranges vs actual 4Q21-3Q26 with walk-forward cushion", ON + "02_guidance_cushion_series.csv",
  SRC + "overnight/02_guidance_ledger.py", pit_lag_days=0, target_lines="guide;rev_drivers",
  mechanism="Revenue surprise vs guide feeds incremental margin (M5 flow-through).", prior_evidence="19 of 19 above midpoint; trailing-8 median cushion +1.79%.",
  suggested_method="M3 guide;M5 street", pcol="print_quarter")
R("G05_disclosure_changes", "Ledger of metric definition and disclosure changes (rename to Nights and Seats 2Q25, regional buckets from 4Q24, FY margin floor from 4Q23, hedging language from 2Q25, ...)",
  ON + "02_disclosure_changes.csv", SRC + "overnight/02_guidance_ledger.py", frequency="event", pit_lag_days=0,
  target_lines="guide;rev_drivers", mechanism="Tells the harness when a series changes basis (needed for PIT refits).", prior_evidence="23 rows.", suggested_method="M3 guide",
  first_period="4Q20", last_period="2Q26", n_obs="")
R("G06_31a_mgmt_statements", "194 verified management margin/cost statements 4Q20-2Q26 (letters, calls, 5 conferences): cost line, horizon, quantified, implied direction, verdict kept/partly/missed",
  ON + "31a_mgmt_margin_statements.csv", SRC + "overnight/31a_mgmt_margin_statements.py", frequency="event", pit_lag_days=0,
  target_lines="margin_total;cor;ops;pd;sm_brand;sm_field;ga;sbc;tax;guide",
  mechanism="Line-level management guidance and its reliability (total margin 91% kept n 43; brand 63% n 35; take rate 59% n 17; SBC 40% n 5).",
  prior_evidence="Only quantified forward cost number is support cost per booking -10%/-16%; FY27/28 silent. WS05 extends to conferences and filings.",
  suggested_method="M3 guide", pcol="date")
R("G07_31a_implied_profile", "31a management-implied cost profile: 9 lines x FY2026/27/28 with confidence and mgmt_silent flags; plus 31a_margin_algorithm_quotes.csv (25 quotes)",
  ON + "31a_mgmt_implied_profile.csv", SRC + "overnight/31a_mgmt_margin_statements.py", frequency="parameter", pit_lag_days=0,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;tax", mechanism="Qualitative trajectory per line from statements; the management profile in 31b.",
  prior_evidence="12 of 30 rows mgmt_silent.", suggested_method="M3 guide", first_period="FY2026", last_period="FY2028", n_obs=30)
R("G08_mgmt_language_ws30", "WS30 management margin-language table (floor wording, beats)", ON + "30_mgmt_language.csv", SRC + "overnight/30_margin_walk.py",
  frequency="event", pit_lag_days=0, target_lines="guide;margin_total", mechanism="Historical wording of the FY guide by print (floor/point).",
  prior_evidence="Says 60-140bp (consistent with 31a).", suggested_method="M3 guide", first_period="4Q23", last_period="2Q26", n_obs="")
R("G09_call_features", "132 language features per earnings call (tone, hedging, numbers per 1k words, theme shares incl. margins/profitability and marketing, CEO/CFO share)",
  ON + "03_call_features.csv", SRC + "overnight/03_call_features.py", pit_lag_days=0, target_lines="guide;margin_total;sm_brand",
  mechanism="Marketing and margin theme intensity on the call could lead spend decisions; tone as a cost-discipline signal.",
  prior_evidence="WS03: 948 tests vs the stock, zero survive BH; never tested against cost lines.", suggested_method="M4 alt;M3 guide")
R("G10_credibility_scorecard", "83 management claims scored for credibility by theme/speaker/horizon (03_forward_claims.csv has the claims)", ON + "03_credibility_scorecard.csv",
  SRC + "overnight/03_call_features.py", frequency="summary", pit_lag_days=0, target_lines="guide",
  mechanism="Discount factor for speaker/horizon when translating statements to cost assumptions.", prior_evidence="Chesky 42%, multi-year 26%.", suggested_method="M3 guide",
  first_period="4Q20", last_period="2Q26", n_obs="")
R("G11_call_topics", "23 calls x 14 topics: keyword mentions per 1k words by prepared remarks / management Q&A / analyst questions", "data/processed/abnb_call_topics.csv",
  SRC + "transcript_analytics.py", pit_lag_days=0, target_lines="guide;sm_brand;margin_total", mechanism="Analyst pressure on margin/marketing (asked 2.8x prepared rate) as a guide-language predictor.",
  prior_evidence="transcript-analytics note; untested vs costs.", suggested_method="M4 alt;M3 guide")
R("G12_declined_to_quantify", "37 hand-verified instances where management declined a number (Experiences/hotels economics, AI spend, long-term margin never sized)",
  "data/processed/abnb_declined_to_quantify.csv", SRC + "transcript_analytics.py", frequency="event", pit_lag_days=0, target_lines="guide;pd;sm_field;cor",
  mechanism="Maps the unsized items in the FY26 P&L (AI spend, new-business field investment, incentive drag).", prior_evidence="4 of the 37 matter for margins (07/31a).",
  suggested_method="M3 guide", first_period="4Q20", last_period="2Q26", n_obs=37)
R("G13_consensus_at_print_merged", "Consensus at all 23 prints (145 sourced press/vendor quotes): revenue 23/23, EPS 17/23, adj. EBITDA 8/23, nights, GBV, next-Q revenue; reactions",
  ON + "16_consensus_at_print_merged.csv", SRC + "overnight/16_merge_and_rerun.py", pit_lag_days=0, target_lines="margin_total;guide",
  mechanism="Street EBITDA/EPS surprise history for M5 (bias) and the comparison column; only 8 EBITDA points so WS03 must rebuild from LSEG.",
  prior_evidence="Vendors spliced (LSEG, Refinitiv, StreetAccount, Zacks); keep the vendor column.", suggested_method="M5 street", pcol="print_quarter")
R("G14_L0_vintage_register", "Frozen L0 consensus vintage register: vendor + timestamp per value at guide/print dates (append-only, dated backup first)",
  FM + "L0/L0_vintage_register.csv", SRC + "forecast_methods/L0/", frequency="event", pit_lag_days=0, target_lines="guide;margin_total",
  mechanism="Point-in-time consensus spine; WS03 writes an append-candidate file in this schema.", prior_evidence="Frozen; 167 rows incl. comment header.",
  status="available", suggested_method="M5 street", first_period="2023Q1", last_period="2026Q3", n_obs=167)
R("G15_harness_targets_calendar", "Frozen forecast-harness targets (revenue, GBV, nights, ADR, take rate, FX pts, guide, Street) and calendar (print/guide/letter/reaction dates, W1/W2 windows)",
  FM + "harness/targets.csv", SRC + "forecast_methods/harness/", pit_lag_days=0, target_lines="guide;rev_drivers",
  mechanism="The margin harness imports this calendar and validator; margin targets are NOT in targets.csv (WS10 adds them).",
  prior_evidence="harness/README.md FORMAT 1.0; calendar.csv 25 rows 2020Q3-2026Q3.", suggested_method="M2 ts;M5 street", pcol="quarter")
R("G16_current_consensus", "Current Street snapshot 3-4 Sep 2026 (Q3/Q4/FY26/FY27 revenue, EPS) and 04_consensus_sources.csv", ON + "04_current_consensus.csv",
  SRC + "overnight/04_consensus_at_print.py", frequency="snapshot", pit_lag_days=0, target_lines="guide;margin_total",
  mechanism="Street comparison column for the 5 Nov card.", prior_evidence="Q3 revenue $4,740M, EPS $2.87, Q4 $3,200M.", suggested_method="M5 street",
  first_period="2026-09-03", last_period="2026-09-04", n_obs="")
R("G17_analyst_targets", "31 live sell-side targets (1 Sep 2026) with implied FY27 EV/EBITDA and P/SBC-adj FCF; 09_analyst_actions.csv has 466 actions",
  ON + "12_analyst_targets.csv", SRC + "overnight/12_exit_multiples_and_targets.py", frequency="snapshot", pit_lag_days=0, target_lines="margin_total",
  mechanism="Implied Street EBITDA per target; comparison only.", prior_evidence="Every Buy is an EBITDA lens; every Sell a cash-after-SBC lens.", suggested_method="M5 street", pcol="date")
R("G18_print_features_pred04", "22 prints x 47 features: revenue beat, nights/GBV acceleration, margin vs bound, S&M deleverage, ops per night y/y, SBC ratio change, guide actions, 1/5/20-day excess",
  "data/processed/predictive/04_print_features.csv", SRC + "predictive/04_reaction_function.py", pit_lag_days=0,
  target_lines="margin_total;sm_brand;ops;sbc;guide", mechanism="Feature set already aligned to prints; the lagged S&M deleverage feature is the one pre-print margin predictor.",
  prior_evidence="Prior-quarter S&M deleverage vs next margin surprise r -0.62 (p 0.017, n 14), LOO RMSE 2.61 vs 2.79 guide, 3.03 naive-last. Ops per night lag, take-rate lag, SBC lag, CPI lodging all fail LOO.",
  suggested_method="M2 ts;M4 alt", pcol="print_quarter")
R("G19_margin_predictability", "Margin-surprise predictability results (66 tests) and quarter table 1Q23-2Q26 (guide type/bound, surprise, S&M deleverage, LOO forecasts)",
  "data/processed/predictive/04_margin_predictability.csv", SRC + "predictive/04_margin_predictability.py", frequency="summary", pit_lag_days=0,
  target_lines="margin_total;guide", mechanism="The existing margin-surprise test bed; WS10 baselines should reproduce its RMSEs (guide 2.79, naive-last 3.03, mean 2.97).",
  prior_evidence="Directional margin guide held 13 of 14 since 1Q23; floors beaten +1.3 to +6.3, ceilings undershot -0.5 to -2.5 (8 of 9). Companion 04_margin_predictability_quarters.csv.",
  suggested_method="M2 ts;M3 guide", first_period="1Q23", last_period="2Q26", n_obs="")
R("G20_print_base_rates", "Per-print beat, guide direction, margin met, FY floor action, 1/5/20-day excess with permutation/Fisher base rates", "data/processed/predictive/01_print_base_rates.csv",
  SRC + "predictive/01_print_base_rates.py", pit_lag_days=0, target_lines="guide;margin_total", mechanism="Base rates for floor raise/hold at each print type.",
  prior_evidence="FY floor raised at 3 of last 4 prints.", suggested_method="M3 guide", pcol="print_quarter")
R("G21_earnings_reactions", "1/5/20-session ABNB, QQQ and excess returns for all 23 prints; plus abnb_earnings_regressions.csv and abnb_guidance_reaction_results.csv (surprise regressions, descriptive)",
  "data/processed/abnb_earnings_reactions.csv", SRC + "abnb_from_theo_guidance.py", pit_lag_days=1, target_lines="guide",
  mechanism="Only for the reaction card; margin surprises do not move the stock alone (predictive/04).", prior_evidence="Margin met + nights accel +5.0% (6/7); met + decel -2.1% (2/11).",
  suggested_method="M3 guide", pcol="quarter")
R("G22_theo_guidance_items", "Theo's guidance dataset: guidance_items.csv (100 + 44 margin rows on the margin branch), guidance_events.csv, quarterly_actuals.csv, market_returns.csv, consensus_snapshots.csv (23 rows of missing)",
  "theos-past-research/research/guidance/data/normalized/guidance_items.csv", SRC + "abnb_margin_guidance_items.py", frequency="event", pit_lag_days=0,
  target_lines="guide;margin_total", mechanism="Structured guide fields (floor/point/ceiling) with excerpts; earlier schema than 02_guidance_ledger.",
  prior_evidence="Validator reports no findings on the 44 margin rows; FY items encoded as Q4 (ABNB-ISSUE-FY-PERIOD-ENCODING).", suggested_method="M3 guide",
  first_period="2020Q4", last_period="2026Q3", n_obs="")
R("G23_frozen_q3_card", "Pre-registered 5 Nov card (spec ABNB-WS20-v1): nights, ADR, GBV, revenue forecasts with baselines and consensus vintage (frozen)", ON + "20_frozen_q3_2026.csv",
  SRC + "overnight/20_temporal_validation.py", frequency="snapshot", pit_lag_days=0, target_lines="guide;rev_drivers",
  mechanism="Revenue-side card the margin card must sit beside; do not edit.", prior_evidence="Frozen 6 Sep; spec_id must not change.", suggested_method="M3 guide",
  first_period="2026Q3", last_period="2026Q3", n_obs=18)

# ---- R: revenue-side driver series (per-unit denominators) -----------------------------------------------------
R("R01_kpis_from_study", "Nights, GBV, ADR, revenue, adj. EBITDA, take rate 1Q21-2Q26 (letters; cross-check only)", "data/processed/abnb_quarterly_kpis_from_study.csv",
  SRC + "abnb_exsbc_stack.py", pit_lag_days=40, target_lines="rev_drivers", mechanism="Nights and GBV are the per-unit denominators for ops (per night) and CoR (per $ GBV).",
  prior_evidence="All 22 match the exsbc stack parse; implied ADR within $0.50.", suggested_method="M1 driver")
R("R02_adr_takerate_jessie", "ADR and quarterly take rate 2021Q1-2026Q2 (Jessie)", "data/processed/airbnb_adr_takerate_quarterly.csv", "", pit_lag_days=40,
  target_lines="rev_drivers", mechanism="Take rate is the revenue-per-GBV lever: +10bp = +0.47pt margin (31b).", prior_evidence="Same basis as R01.", suggested_method="M1 driver")
R("R03_revenue_decomposition", "Revenue y/y 1Q22-2Q26 decomposed into nights, ADR ex-FX, FX and take-rate points (residual < 0.5pp)", "data/processed/abnb_revenue_decomposition.csv",
  SRC + "abnb_driver_model.py", pit_lag_days=40, target_lines="rev_drivers;margin_total",
  mechanism="Each component has a different cost pass-through: nights carry ops/CoR, ADR ex-FX and FX carry only CoR (84% flow-through), take rate ~100%.",
  prior_evidence="2Q26: nights 10.6, ADR ex-FX 1.6, FX 4.0, take +0.7.", suggested_method="M1 driver")
R("R04_adr_full_decomposition", "Annual ADR y/y 2021-2025 split into geo mix, LOS, FX, size mix, within-region price (validated r 0.988 vs disclosed quarters)", "data/processed/adr/07_full_decomposition.csv",
  SRC + "adr/", frequency="annual", pit_lag_days=50, target_lines="rev_drivers;margin_total;cor",
  mechanism="Regional mix drag (-0.5 to -2.8pp of ADR/yr) is a structural margin drag no earlier model quoted; size mix raises revenue per night without raising support cost per night.",
  prior_evidence="31b: regional mix -2.5pt of margin FY22-25; -0.33pt per 1pt of nights share NA->LatAm/APAC.", suggested_method="M1 driver", pcol="year")
R("R05_adr_history_extended", "ADR history back to 1Q19 with FX backcast and ex-FX ADR (letters, S-1)", "data/processed/adr/02b_adr_history_extended.csv", SRC + "adr/",
  pit_lag_days=40, target_lines="rev_drivers", mechanism="Extends the revenue-per-night denominator to 2019 for the seasonal profile and 2020 shock (M6).", prior_evidence="usable_for_calibration flag per quarter.",
  suggested_method="M6 cycle")
R("R06_regional_panel", "Regional panel 23 quarters x 79 columns: NA/EMEA/LatAm/APAC nights y/y bands and share estimates, regional ADR reported/ex-FX, regional revenue (XBRL), cross-border, urban, long-term-stay shares",
  ON + "10_regional_panel_quarterly.csv", SRC + "overnight/10_regional_panel.py", pit_lag_days=40, target_lines="rev_drivers;cor;ops;sm_brand",
  mechanism="Regional mix moves ADR (cost per $ GBV vs per night), payment-processing mix (cross-border/FX fees), support language cost, and expansion-market brand spend.",
  prior_evidence="Share-weighted sum reconciles to total nights within 1.1pp; regional ADR index NA 1.42 / EMEA 0.97 / LatAm 0.68 / APAC 0.59.", suggested_method="M1 driver")
R("R07_regional_forecast", "Regional nights growth 3Q26, 4Q26, FY27 (bear/base/bull) with ADR ex-FX and FX pp", ON + "10_regional_forecast.csv", SRC + "overnight/10_regional_panel.py",
  frequency="scenario", pit_lag_days=0, target_lines="rev_drivers", mechanism="Regional path drives the mix term in the cost model.", prior_evidence="Base FY27 NA/EMEA/LatAm/APAC 6/7/16/15.",
  suggested_method="M1 driver", first_period="3Q26", last_period="FY27", n_obs="")
R("R08_regional_revenue_xbrl", "Revenue by geography from XBRL (10_regional_revenue_xbrl.csv, 10_xbrl_revenue_geography.csv 258 rows) and Jessie's airbnb_regional_revenue_quarterly.csv (10-Q basis, Q4 = FY less 9M)",
  ON + "10_regional_revenue_xbrl.csv", SRC + "overnight/10_fetch_xbrl_geography.py", pit_lag_days=45, target_lines="rev_drivers;tax;other_inc",
  mechanism="Geographic revenue mix informs the effective tax rate mix (US vs Ireland/Singapore) and non-USD cost share.", prior_evidence="NA 42.4% of revenue / ~29% of nights.",
  suggested_method="M1 driver;M7 below-EBITDA")
R("R09_fx_quarterly", "Quarterly average and y/y of 9 bilateral rates (AUD, BRL, CAD, EUR, GBP, INR, JPY, KRW, MXN) 1Q18-2026; 10_fx_daily.csv (19,467 rows), 10_fx_basket.csv, 10_regional_fx_passthrough.csv",
  ON + "10_fx_quarterly.csv", SRC + "overnight/10_fetch_fx.py", pit_lag_days=1, target_lines="rev_drivers;cor;other_inc",
  mechanism="FX moves reported revenue (ADR FX contemporaneous r -0.96 to broad USD), CoR in local currency (55% non-USD), and remeasurement in other income.",
  prior_evidence="Survivor: ADR FX = 0.52 - 0.715 x broad USD y/y; revenue FX lags 1-2 quarters (r 0.80).", suggested_method="M1 driver;M7 below-EBITDA",
  first_period="1Q18", last_period="2Q26", n_obs="")
R("R10_fx_schedule", "EUR/USD and broad-USD paths to 4Q27 (consensus/strong/weak USD) with fitted ADR FX and revenue FX per quarter and realised share", ON + "05_fx_schedule.csv",
  SRC + "overnight/05_macro_transmission.py", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers;margin_total",
  mechanism="Revenue FX x 84% flow-through = margin FX term; 4Q26 -0.4pp is a mechanical step-down.", prior_evidence="Refresh weekly (one FRED pull); FXSWAP note swapped bridge FX to the fx_lag_v2 kernel.",
  suggested_method="M1 driver", pcol="quarter")
R("R11_fx_lag_v2_kernel", "Lane 1 fx_lag_v2 package: currency baskets (spot-held), 4Q26 and FY27 FX forecasts (23_forecast_4q26_v2.csv, 23b_fy27_annualisation_v2.csv), hedge gross vs after (22_hedge_gross_vs_after.csv), PIT window scores",
  FM + "fx_lag_v2/23_forecast_4q26_v2.csv", SRC + "forecast_methods/fx_lag_v2/", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers;margin_total",
  mechanism="Adopted FX line for 4Q26 (+0.15pp kernel vs +1.0 bridge v2); the margin model reads FX from here.", prior_evidence="Registered in the frozen harness; survives W1/W2 (SCOREBOARD_v2).",
  suggested_method="M1 driver", first_period="4Q26", last_period="FY27", n_obs="")
R("R12_h2_bridge_v3", "Adopted 3Q26/4Q26 revenue view: nights +9.9/+8.1%, ADR ex-FX +3.9/+4.1%, revenue dollars, FX line, transitions, deviations, event catalogue (h2_bridge_v3/*.csv)",
  "data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv", SRC + "h1_to_h2_bridge_v3.py", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers",
  mechanism="The revenue path the margin model consumes for 3Q26-4Q26 (4Q26 revenue $3,178M, implied guide mid $3,059M).", prior_evidence="REBASE_h2_bridge_v3 note; WS06 carries it unchanged into the FY27 path file.",
  suggested_method="M1 driver", first_period="3Q26", last_period="4Q26", n_obs="")
R("R13_nights_quarterly_pr32", "PR #32 quarterly nights path 3Q26-4Q27 by scenario (three-feature NA lap on real quarters; total and NA files)", "data/processed/nights_quarterly_total.csv",
  SRC + "nights_quarterly.py", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers", mechanism="FY27 nights denominators (WS06 audits and reissues as v2).",
  prior_evidence="research/notes/nights_quarterly.md; memory: FY26 reconciles, FY27 is the trade.", suggested_method="M1 driver", first_period="3Q26", last_period="4Q27", n_obs="")
R("R14_ws29_fy27_path", "WS29 FY27 quarterly revenue path by scenario (nights y/y, ADR ex-FX, residual, FX pp, hedge memo) and 29_fy27_bridge.csv, 29_q4_2026_bridge.csv, 29_bridge_assumptions.csv",
  ON + "29_fy27_quarterly_path.csv", SRC + "overnight/29_q4_fy27_bridge.py", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers",
  mechanism="Revenue path 31b/30 currently run on; WS06 reconciles.", prior_evidence="Re-run weekly (pulls FRED).", suggested_method="M1 driver", first_period="1Q27", last_period="4Q27", n_obs="")
R("R15_fee_timeline_elasticities", "19 dated fee events 2019-2026 (06_fee_timeline.csv) and 25 sourced elasticities (06_elasticities.csv: single-fee migration +40-50bp, FX service fee +20bp, BKNG ceiling 14.5%)",
  ON + "06_fee_timeline.csv", SRC + "overnight/06_evidence_tables.py", frequency="event", pit_lag_days=0, target_lines="rev_drivers;cor",
  mechanism="Fee structure sets take rate (revenue per $ GBV) and the guest FX-fee revenue that offsets cross-border payment cost.", prior_evidence="Single fee worth +40-45bp fully migrated, not 200-300bp.",
  suggested_method="M1 driver", pcol="month")
R("R16_fee_takerate_lane1", "Lane 1 fee_takerate package: take-rate history (04a), regression (04b), migration effect by quarter (05a), FY27 mechanism (05b), live 3Q26 take rate (07a), 4Q26 fee step (07b), backtest scorecard (06c)",
  FM + "fee_takerate/04a_takerate_history.csv", SRC + "forecast_methods/fee_takerate/", pit_lag_days=0, target_lines="rev_drivers",
  mechanism="Mechanism-based take-rate path replaces the bps lever; take rate is the highest-flow-through revenue driver.", prior_evidence="fee-takerate.md and VERIFY r1/r2 notes; kill list: '+4.05% fee uplift as measured'.",
  suggested_method="M1 driver")
R("R17_revenue_by_line", "Revenue by line (homes, hotels, Experiences seats, Services, ads) quarterly 3Q26-4Q27 and annual by scenario; take rate and incentive drag by line (14_revenue_by_line_*.csv, model/ABNB_revenue_by_line.xlsx)",
  ON + "14_revenue_by_line_quarterly.csv", SRC + "overnight/14_revenue_by_line.py", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers;sm_field;cor",
  mechanism="New businesses carry customer incentives (contra-revenue / take-rate drag), field-ops headcount and different payment/insurance costs per $ GBV.", prior_evidence="Seats share ~1.5%, hotels ~4% of nights (3Q26 base).",
  suggested_method="M1 driver", first_period="3Q26", last_period="4Q27", n_obs="")
R("R18_seats_dilution", "Seats (Experiences/Services) dilution of ADR, quarterly 3Q26-4Q27 and annual, by case (adr/15_seats_dilution_*.csv)", "data/processed/adr/15_seats_dilution_quarterly.csv",
  SRC + "adr/", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers", mechanism="Seats lower blended ADR (-0.1 to -0.4pp) without lowering per-booking support cost.", prior_evidence="seats-dilution note 9 Sep.",
  suggested_method="M1 driver", first_period="3Q26", last_period="4Q27", n_obs="")
R("R19_new_business_scenarios", "Hotels, Experiences, Services, sponsored listings revenue FY25-FY28 bear/base/bull with assumptions", ON + "11_new_business_scenarios.csv",
  SRC + "overnight/11_competition_supply_overlays.py", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers;sm_field",
  mechanism="New-business revenue at an assumed 70% incremental margin in the driver model; field-ops investment $200-250M FY25 guided, +$300M realised.",
  prior_evidence="Optionality bucket $235M/$914M/$1,987M FY28.", suggested_method="M1 driver;M6 cycle", first_period="FY25", last_period="FY28", n_obs="")
R("R20_ai_exposure_scenarios", "AI referral cost scenarios 2026-2028 (share of GBV via paid AI referral x fee %) as a performance-marketing cost line", ON + "11_ai_exposure_scenarios.csv",
  SRC + "overnight/11_competition_supply_overlays.py", frequency="scenario", pit_lag_days=0, target_lines="sm_brand;cor",
  mechanism="If AI agents intermediate bookings, a referral fee becomes a new variable cost (performance marketing or CoR).", prior_evidence="Low case $16M (0.1% of revenue) 2026; experts: ~3% AI-native bookings in 12-24 months.",
  suggested_method="M4 alt;M6 cycle", pcol="year")
R("R21_los_bucket_shares", "Length-of-stay bucket shares (nights and bookings <7 / 7-27 / 28+) by region and year, solved from disclosed ALOS (adr/14b_*); airbnb_nights_per_booking.csv (annual ALOS by region 2019-2025)",
  "data/processed/adr/14b_los_bucket_shares.csv", SRC + "adr/", frequency="annual", pit_lag_days=50, target_lines="ops;cor;rev_drivers",
  mechanism="Support contacts and payment transactions scale per BOOKING; nights per booking (ALOS) converts management's per-booking claims (-16%) to the per-night line basis.",
  prior_evidence="ALOS disclosed globally (~4.0-4.4 nights) and never by region; 28+ share stopped 1Q24 at 17%. Never used in a cost model.", suggested_method="M1 driver", pcol="period")
R("R22_party_size_quarterly", "Airbnb party composition from 74M review texts (123 markets): global and regional quarterly party-size index, capacity, solo/couple/family shares (abnb_party_size_reviews_*.csv)",
  "data/processed/abnb_party_size_reviews_quarterly.csv", SRC + "abnb_party_size_reviews.py", pit_lag_days=45, target_lines="rev_drivers",
  mechanism="Bigger units per night raise ADR without raising per-night support or hosting cost; validated r 0.96-0.99 vs Hawaii DBEDT.", prior_evidence="party-size notes; 'half of ADR growth is bigger units' is on the kill list (it is +0.46-0.8pp).",
  suggested_method="M1 driver", pcol="q")
R("R23_q3nowcast_reviews_index", "Reviews-based stays index, 123 markets, monthly/quarterly, global and regional (q3nowcast/E, E_aug): beats naive 0.68x for nights; 3Q26 band 8.5-11.0",
  "data/processed/q3nowcast/E/index_quarterly.csv", SRC + "q3nowcast/", frequency="monthly", pit_lag_days=35, target_lines="rev_drivers",
  mechanism="Intra-quarter nights nowcast (the ops-per-night and CoR-per-GBV denominators before the print).", prior_evidence="docs/q3nowcast/SYNTHESIS.md: 3Q26 nights 9.5-10.0%.", suggested_method="M1 driver")
R("R24_q3nowcast_external_panel", "External-series quarterly panel (TSA, CPI lodging, NTTO, Spain INE, hotel RevPAR ...) with QTD readings and backtests (q3nowcast/G)", "data/processed/q3nowcast/G/G_quarterly_panel.csv",
  SRC + "q3nowcast/", pit_lag_days=15, target_lines="rev_drivers", mechanism="Same-quarter demand readings for the revenue denominators; source_inventory.csv ranks 39 external sources by reachability.",
  prior_evidence="WS-G: few beat naive; hotel RevPAR weekly the best-covered.", suggested_method="M4 alt", pcol=None, first_period="2018Q1", last_period="2026Q3", n_obs="")
R("R25_adr_card_v3", "ADR v3 card: 3Q26 ADR ex-FX +3.3% $176.9, 4Q26 +3.8% with FX estimator, residual rule, bands (adrv3/P)", "data/processed/adrv3/P/adr_card_v3.csv", SRC + "adrv3/",
  frequency="scenario", pit_lag_days=0, target_lines="rev_drivers", mechanism="ADR path adopted by bridge v3; ADR ex-FX +1pt = +0.42pt margin.", prior_evidence="PR #46; v3 last_q rule beats naive on dollar target (S).",
  suggested_method="M1 driver", first_period="3Q26", last_period="4Q26", n_obs="")
R("R26_rnpl_cohort_scenarios", "RNPL cohort scenario grid (2,025 rows) for 3Q26/4Q26 nights effect; rnpl_statement_ledger.csv; D1_rnpl_parameters.csv", "data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv",
  SRC + "overnight2/", frequency="scenario", pit_lag_days=0, target_lines="rev_drivers;fcf_timing", mechanism="RNPL shifts cash collection toward check-in: kills the unearned-fee float and raises cancellation/chargeback exposure.",
  prior_evidence="docs/overnight2/SYNTHESIS.md; RNPL >20% of GBV, laps US 3Q26 / global 1Q27.", suggested_method="M7 below-EBITDA", first_period="3Q26", last_period="4Q26", n_obs="")
R("R27_backlog_tests", "WS08 backlog tests: unearned fees / funds held vs next-quarter revenue and GBV, RNPL-era gap", ON + "08_backlog_tests.csv", SRC + "overnight/08_altdata_backtests.py",
  frequency="summary", pit_lag_days=0, target_lines="fcf_timing;rev_drivers", mechanism="Documents the float break for the FCF timing line.", prior_evidence="Funds-held-to-GBV gap 3.8pp (2Q25) -> 5.2pp (2Q26).",
  suggested_method="M7 below-EBITDA", first_period="2021Q1", last_period="2026Q2", n_obs="")
R("R28_eurostat_platform_quarterly", "EU27 platform nights quarterly y/y next to Airbnb EMEA revenue y/y (Eurostat tour_ce_omr, monthly to Mar 2026)", "data/processed/eurostat_platform_nights_quarterly.csv",
  SRC + "abnb_eu_platform_and_backlog.py", pit_lag_days=150, target_lines="rev_drivers", mechanism="EMEA volume benchmark; too lagged to nowcast.", prior_evidence="Lead correlation -0.11 as a nowcast; corr 0.81 with EMEA ex-FX.",
  suggested_method="M6 cycle")
R("R29_kpi_vs_category", "ABNB KPIs vs BEA PCE accommodations/hotels nominal, real and price; inbound/outbound travel; CPI lodging and airfare, 1Q21-2Q26", "data/processed/abnb_kpi_vs_category_quarterly.csv",
  SRC + "abnb_kpi_vs_category.py", pit_lag_days=30, target_lines="rev_drivers", mechanism="US category demand and price for the cycle model.", prior_evidence="US category is price not volume (real +1.8%, price +3.4% Jul 2026).",
  suggested_method="M6 cycle")

# ---- M: macro, rates, wages, prices (repo copies) --------------------------------------------------------------
R("M01_macro_quarterly_panel", "Quarterly macro panel 2019Q1-2026Q2: fed funds, UST 2y/10y, unemployment, payrolls, leisure & hospitality employment, initial claims, CPI (all, lodging, airfare), sentiment, real DPI/PCE, saving rate, consumer credit, USD and 6 bilateral rates, WTI, jet fuel, EU27 platform nights",
  ON + "05_macro_quarterly_panel.csv", SRC + "overnight/05_macro_transmission.py", pit_lag_days=15, target_lines="int_inc;ga;ops;pd;margin_total;rev_drivers",
  mechanism="Short rates x interest-earning balances = interest income; labour-market tightness (leisure & hospitality employment, claims) proxies wage pressure in ops/PD/G&A payroll; sentiment/claims define the demand-cycle state for M6.",
  prior_evidence="WS05: 1,408 macro tests vs nights/revenue, none survive; NEVER tested against cost lines or interest income.", suggested_method="M7 below-EBITDA;M6 cycle;M4 alt",
  pcol="quarter")
R("M02_fred_cache_42", "42 FRED series cached as CSV (FEDFUNDS, DGS2, DGS10, T10YIE, UNRATE, PAYEMS, USLAH, ICSA, CPIAUCSL, CUSR0000SEHB, CUSR0000SETG01, DSPIC96, PCEC96, PSAVERT, RSXFS, UMCSENT, MICH, DTWEXBGS, DEXUSEU, DEX* 9 pairs, DCOILWTICO, WJFUELUSGULF, AIRRPMTSID11, GDPC1, A191RL1Q225SBEA, TDSP, TOTALSL ...)",
  ON + "05_fred_cache/FEDFUNDS.csv", SRC + "overnight/05_macro_transmission.py", frequency="monthly/daily", pit_lag_days=1,
  target_lines="int_inc;ga;ops;pd;margin_total", mechanism="FEDFUNDS/DGS2 are the yield drivers for interest income on ~$12B cash + ~$10B funds held; 3-month bill (DTB3) is NOT cached (gap).",
  prior_evidence="Used for macro transmission only.", status="needs_refresh", suggested_method="M7 below-EBITDA;M6 cycle", first_period="1954-07", last_period="2026-08", n_obs=42)
R("M03_macro_us_monthly_jessie", "FRED monthly 2021-01 to 2026-08: Michigan sentiment, unemployment, CPI, real DPI, saving rate, fed funds, 10y, broad dollar, WTI, real PCE, EUR/USD (Jessie)", "data/processed/macro_us_monthly.csv",
  "", frequency="monthly", pit_lag_days=15, target_lines="int_inc;margin_total", mechanism="Duplicate of M01/M02 at monthly grain.", prior_evidence="Overlaps 05_fred_cache.",
  suggested_method="M6 cycle", pcol="month")
R("M04_shock_episodes", "Four demand-shock episodes (2022 rate/USD shock, 2024 US softness, spring-2025 tariff shock, 1Q26 Middle East) with macro, guide, print, stock and lesson", ON + "05_shock_episodes.csv",
  SRC + "overnight/05_macro_transmission.py", frequency="event", pit_lag_days=0, target_lines="margin_total;sm_brand;sm_field",
  mechanism="Episode set for the cost-flex model (how did S&M and margin respond when growth decelerated?). WS02 extends with 2020.", prior_evidence="Not yet paired with cost-line responses.",
  suggested_method="M6 cycle", first_period="2022Q2", last_period="2026Q2", n_obs=4)
R("M05_price_gap_series", "Quarterly price context 1Q21-2Q26: CPI lodging, BEA hotel price index, STR US hotel ADR/RevPAR/occupancy, MAR and HLT RevPAR y/y, ABNB ADR reported/ex-FX (06_price_gap_series.csv, 06_price_gap_monthly.csv)",
  ON + "06_price_gap_series.csv", SRC + "overnight/06_price_gap.py", pit_lag_days=15, target_lines="rev_drivers;margin_total",
  mechanism="Hotel ADR/RevPAR cycle is the pricing-power state variable for M6; CPI lodging tested against margin surprise.", prior_evidence="predictive/04: CPI lodging y/y vs margin surprise r 0.13, fails LOO (n 14).",
  suggested_method="M6 cycle")
R("M06_hotel_price_monitor", "Monthly 2023-01 to 2026-07: CPI lodging y/y, BEA hotel price y/y, ABNB ADR reported and ex-FX on quarter-end months", "data/processed/hotel_price_monitor_monthly.csv",
  SRC + "hotel_price_monitor.py", frequency="monthly", pit_lag_days=12, target_lines="rev_drivers", mechanism="Price benchmark for ADR ex-FX.", prior_evidence="Oct 2025 CPI missing at source.",
  suggested_method="M6 cycle", pcol="month")
R("M07_govdata_price_panel", "Government price series panel (HICP accommodation by country, INE Spain HDPI/IPH, UK ONS 11.2, Japan CPI hotel, BLS PPI hotels, IBGE IPCA hospedagem ...) monthly y/y and quarterly features with backtests (govdata/P)",
  "data/processed/govdata/P/P_feature_quarterly_panel.csv", SRC + "govdata/", pit_lag_days=20, target_lines="rev_drivers",
  mechanism="Regional accommodation price indices for ADR ex-FX by region.", prior_evidence="PR #50/#51: no full workstream warranted; corroboration only.", suggested_method="M6 cycle", pcol="Unnamed: 0")
R("M08_govdata_volume_panel", "Government volume series panel (ANAC Brazil, IBGE PMS, StatCan arrivals, JNTO, JTA nights, ABS, NZ MBIE, INE EOAP, Hawaii VR, Census QSS ...) with backtests (govdata/V)",
  "data/processed/govdata/V/V_feature_panel.csv", SRC + "govdata/", pit_lag_days=30, target_lines="rev_drivers", mechanism="Regional volume benchmarks for the nights denominator.",
  prior_evidence="V_ranked_table.md; none beat naive on both windows.", suggested_method="M6 cycle")
R("M09_google_trends_weekly", "Google Trends weekly 2019-2026, 9 terms (airbnb, vrbo, booking, hotels ...), US and worldwide, stitched windows (08_trends_weekly.csv; quarterly features and tests in 08_trends_*)",
  ON + "08_trends_weekly.csv", SRC + "overnight/08_trends_pull.py", frequency="weekly", pit_lag_days=2, target_lines="sm_brand;rev_drivers",
  mechanism="Branded search is the output brand marketing buys; search per $ of brand spend is a marketing-efficiency series, and search spikes date campaign flights.",
  prior_evidence="WS08: 0 of 162 Trends features beat naive for nights; NOT point-in-time (renormalised each pull); never tested against S&M spend.", status="needs_refresh",
  suggested_method="M4 alt", pcol="date")
R("M10_short_interest", "84 short-interest settlements Feb 2023-Sep 2026 (marketbeat/Nasdaq)", ON + "09_short_interest.csv", SRC + "overnight/09_stock_behaviour.py", frequency="semi-monthly",
  pit_lag_days=10, target_lines="guide", mechanism="Positioning only; no cost-line content.", prior_evidence="WS09: no predictive value.", suggested_method="M5 street", pcol="settlement_date")
R("M11_peer_prints", "BKNG, EXPE, MAR, HLT print KPIs by ABNB quarter 2021Q1-2026Q2 (room nights, gross bookings, revenue y/y, adj. EBITDA margin, next-quarter direction, reaction) from 93 8-K Ex. 99.1",
  "data/processed/predictive/02_peer_prints.csv", SRC + "predictive/02_peer_prints_build.py", pit_lag_days=-8, target_lines="margin_total;sm_brand",
  mechanism="BKNG/EXPE adj. EBITDA margin and marketing ratios print ~8 days before ABNB: a same-quarter cost-cycle read (marketing intensity in a soft quarter).",
  prior_evidence="predictive/02: BKNG room-night acceleration r +0.91 with ABNB nights (n 7); peer margins never tested against ABNB margin.", suggested_method="M4 alt;M6 cycle", pcol="quarter")
R("M12_alt_accom_share", "BKNG alternative-accommodation mix and nights y/y vs Airbnb nights y/y 2Q22-2Q26", ON + "11_alt_accom_share_quarterly.csv", SRC + "overnight/11_competition_supply_overlays.py",
  pit_lag_days=-8, target_lines="rev_drivers;sm_brand", mechanism="Competitive intensity in alt-accommodation drives performance-marketing bidding.", prior_evidence="BKNG alt-accom premium +6pt (3Q24) -> -1pt (2Q26).",
  suggested_method="M6 cycle")

# ---- A: supply, marketing, support, payments alt-data already in the repo -------------------------------------
R("A01_supply_economics", "82 dated supply facts (active listings, hosts, new listings, Co-Host Network, removed listings) from filings and letters 2020-2026", ON + "11_supply_economics.csv",
  SRC + "overnight/11_competition_supply_overlays.py", frequency="event", pit_lag_days=0, target_lines="sm_field;sm_brand",
  mechanism="Host acquisition (field ops, referral incentives) scales with new-listing needs; listings growth 'in line with nights'.", prior_evidence="Active listings disclosure stopped 4Q25.",
  suggested_method="M4 alt", pcol="date")
R("A02_inside_airbnb_city_snapshots", "Inside Airbnb 13-city snapshots, 168 dumps Dec 2022-Aug 2026: listings, reviews LTM/L30D, entire-home, superhost, multi-listing shares, price basis flags (plus like-for-like pairs and host concentration)",
  "data/processed/inside_airbnb_city_snapshots.csv", SRC + "inside_airbnb_supply_panel.py", frequency="dump", pit_lag_days=35, target_lines="sm_field;ops;rev_drivers",
  mechanism="New-listing flow and multi-listing (professional) share proxy host-acquisition effort and support intensity (pro hosts generate fewer contacts per night).",
  prior_evidence="WS08: listings y/y 3.6x worse than naive for nights; supply index loses to 'same as last quarter'; never mapped to field ops.", suggested_method="M4 alt", pcol="dump_date")
R("A03_listing_churn_pooled", "Pooled listing ID-attrition rates, 12-13 markets, Sep 2025-Aug 2026 (listing_churn_panel, listing_churn_archive, fee_churn_history pooled_interval_rates 115 markets)",
  "data/processed/listing_churn_panel/pooled_rates.csv", SRC + "measure_churn_panel.py", frequency="interval", pit_lag_days=35, target_lines="sm_field",
  mechanism="Churn 20-30%/yr sets the replacement supply the field/host-acquisition budget must buy.", prior_evidence="Availability-selected panel; not a random sample; fee-related churn scenarios in fee_churn_history.",
  suggested_method="M4 alt", first_period="2025-09", last_period="2026-08", n_obs="")
R("A04_market_summary_2026", "Theo's 120-market summary (listings, hosts, entire-home / multi-host / superhost / licence shares, median asking price) single 2026 vintage", "data/processed/market_summary_2026.csv",
  SRC + "build_market_summary.py", frequency="snapshot", pit_lag_days=35, target_lines="sm_field;ops", mechanism="Cross-section of professionalisation by market (support cost per night differs by host type).",
  prior_evidence="One vintage; no time dimension.", suggested_method="M4 alt", first_period="2026-06", last_period="2026-07", n_obs="")
R("A05_booking_curves", "Blocked-night rate by market x snapshot x horizon (600 rows) and daily (44,379 rows); single June 2026 vintage; 2026 calendars carry no price", "data/processed/booking_curves_by_market.csv",
  SRC + "build_booking_curves.py", frequency="snapshot", pit_lag_days=35, target_lines="rev_drivers", mechanism="Forward pace proxy for nights; not occupancy.", prior_evidence="q3nowcast F: calendar pace built on later vintages.",
  suggested_method="M4 alt", first_period="2026-06", last_period="2026-07", n_obs="")
R("A06_cc_listing_survival", "Common Crawl listing survival by crawl and by age 2021-2026 (1.2M ids, 1,500 matched pairs); no price in any era", "data/processed/cc_listing_survival.csv",
  SRC + "cc_listing_panel.py", frequency="crawl", pit_lag_days=60, target_lines="sm_field", mechanism="Survival 85-90%/yr is another replacement-supply read.", prior_evidence="Review velocity flat five years.",
  suggested_method="M4 alt", pcol=None, first_period="2021", last_period="2026", n_obs="")
R("A07_quote_line_items", "1.71M fee-inclusive search quotes Mar-Aug 2026 by city: service-fee share of quote, discounts (06_quote_line_items.csv, 06_quote_discount_panel.csv; fee-panel capture running)",
  ON + "06_quote_line_items.csv", SRC + "overnight/06_quote_panel.py", frequency="monthly", pit_lag_days=5, target_lines="rev_drivers",
  mechanism="Guest-fee share and discount penetration read the take-rate mechanism and coupon (contra-revenue) intensity.", prior_evidence="Kill list: do not call the panel 'fee-inclusive'; quote indices do not track disclosed ADR.",
  suggested_method="M4 alt", pcol="month", first_period="2026-03", last_period="2026-08", n_obs="")
R("A08_regulatory_profile", "20 regulatory events with probabilities, Monte Carlo revenue-loss and EBITDA-hit percentiles 2027/2030; abnb_regulatory_events.csv, abnb_regulatory_contributions.csv, 11_regulatory_overlay.csv; SQLite with 48 sources",
  "data/processed/abnb_regulatory_profile.csv", SRC + "abnb_regulatory_forecast.py", frequency="scenario", pit_lag_days=0, target_lines="ga;rev_drivers",
  mechanism="Regulation drives G&A (legal, lodging-tax reserves, fines such as Spain EUR64M, Italy tax settlement) and the EMEA nights drag.", prior_evidence="Median EBITDA hit $72M (2027) at 70% contribution; 93% European.",
  suggested_method="M6 cycle;M4 alt", first_period="2026", last_period="2030", n_obs="")
R("A09_altdata_quarterly_pred03", "Inside Airbnb and Common Crawl quarterly alt-data features (like-for-like price, matched reviews, retention, listings y/y) 2023Q4-2026Q2", "data/processed/predictive/03_altdata_quarterly.csv",
  SRC + "predictive/03_nowcast_tests.py", pit_lag_days=35, target_lines="rev_drivers;sm_field", mechanism="Same content as A02 aligned to quarters.", prior_evidence="predictive/03: no alt-data feature beats naive on both windows.",
  suggested_method="M4 alt", pcol="quarter")
R("A10_demand_supply_indexes", "WS08 composite demand, supply and price indexes quarterly with walk-forward backtests (08_demand_index_quarterly.csv, 08_supply_index_quarterly.csv, 08_price_index_quarterly.csv, 08_index_backtests.csv, 08_feature_tests_all.csv 598 rows)",
  ON + "08_demand_index_quarterly.csv", SRC + "overnight/08_altdata_backtests.py", pit_lag_days=35, target_lines="rev_drivers",
  mechanism="Composite alt-data state variables; all lose to naive for revenue targets.", prior_evidence="Kill list: say 'nothing beats AR(1) on both windows' (52 of 598 beat AR(1), all mechanical FX or window-dependent).",
  suggested_method="M4 alt", pcol="quarter")
R("A11_edgar_filing_kpis", "368 KPI sentences from 14 10-Q/10-K filings 2023Q1-2026Q2 (Theo; evidence-grade) and abnb_edgar_quarterly_kpis.csv (43 rows incl. deferred revenue)", "data/processed/abnb_filing_kpis.csv",
  SRC + "acquisition/run_edgar_filings.py", frequency="event", pit_lag_days=45, target_lines="fcf_timing;rev_drivers", mechanism="Filing-text extraction pattern reusable for cost-line MD&A sentences (WS02).",
  prior_evidence="Clean tables are HTML, not prose.", suggested_method="M1 driver", first_period="2023Q1", last_period="2026Q2", n_obs="")
R("A12_hawaii_party_size_monthly", "Hawaii DBEDT monthly party size and accommodation counts Jan 2013-Jul 2026 (only public party-size time series)", "data/processed/hawaii_party_size_monthly.csv",
  SRC + "hawaii_party_size_series.py", frequency="monthly", pit_lag_days=25, target_lines="rev_drivers", mechanism="Validates the review-derived party-size index (unit-size ADR term).",
  prior_evidence="Rental parties 2.28 -> 2.49 (2013-24).", suggested_method="M1 driver", pcol=None, first_period="2013-01", last_period="2026-07", n_obs="")

# ---- X: raw primary sources junctioned in (read-only) ----------------------------------------------------------
R("X01_xbrl_companyfacts", "SEC XBRL companyfacts JSON (CIK 1559720): every tagged fact incl. cost lines, SBC by function (ShareBasedCompensation*), D&A, interest income/expense, other nonoperating income, tax provision, current/deferred tax, OCI hedges, funds held, unearned fees, weighted/diluted shares, dei shares outstanding, lease cost, capitalized software amortization, treasury stock",
  "data/raw/xbrl/ABNB_companyfacts.json", SRC + "abnb_costlines_from_xbrl.py", frequency="quarterly/annual", pit_lag_days=45,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;da;int_inc;other_inc;tax;shares;fcf_timing;capex",
  mechanism="Primary source for WS02's panel and for below-EBITDA tags never yet pulled (OtherNonoperatingIncomeExpense, CurrentIncomeTaxExpenseBenefit, DeferredIncomeTaxExpenseBenefit, OperatingLeaseCost, CapitalizedComputerSoftwareAmortization1, PaymentsForRepurchaseOfCommonStock, dei:EntityCommonStockSharesOutstanding).",
  prior_evidence="Used by costlines, capital-return, backlog, 28 hedges. YTD values must be de-cumulated; PurchaseObligation has no CY frames (07).", suggested_method="M7 below-EBITDA;M1 driver",
  first_period="FY2018", last_period="2Q26", n_obs="")
R("X02_10k_text_fy2020_25", "Six 10-K primary documents FY2020-FY2025 (.htm and .txt): MD&A cost-line definitions and $ deltas (payroll, marketing activities, third-party providers, insurance, cloud, non-income taxes), S&M split table, SBC by function, Note 13 commitments (hosting, purchase obligations), Item 1 headcount and third-party support workers, tax rate reconciliation, Item 7A FX and rates sensitivity, share repurchase table",
  "data/raw/filings/txt", SRC + "overnight/07_cost_lines_per_night.py", frequency="annual", pit_lag_days=50,
  target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;da;int_inc;other_inc;tax;shares;capex",
  mechanism="The only source of sub-line components (MD&A deltas) and forward commitments; the tax-rate reconciliation gives the structural ETR.", prior_evidence="07_cost_components_annual.csv extracts ~35 items; MD&A deltas 2022-2025 not yet turned into a quarterly series (10-Qs missing in this tree).",
  status="available", suggested_method="M1 driver;M7 below-EBITDA", first_period="FY2020", last_period="FY2025", n_obs=6)
R("X03_10q_2q26_and_10k_pdf", "Latest 10-Q (2Q26 HTML) and FY2025 10-K PDF/JSON under data/raw/regulatory/quantification/; other 10-Qs 1Q21-1Q26 are NOT in the tree (gap)", "data/raw/regulatory/quantification/abnb_2026q2_10q.html",
  SRC + "pull_regulatory_quant_sources.py", frequency="quarterly", pit_lag_days=42, target_lines="cor;ops;pd;sm_brand;sm_field;ga;sbc;tax;shares",
  mechanism="10-Q three-month MD&A gives the quarterly $ deltas by component and the monthly share-repurchase table (Item 2).", prior_evidence="07 built the brand/field split from 10-Q three-month tables (pulled live from EDGAR at the time).",
  status="needs_refresh", suggested_method="M1 driver;M7 below-EBITDA", first_period="2Q26", last_period="2Q26", n_obs=1)
R("X04_shareholder_letters", "23 shareholder letters 4Q20-2Q26 (8-K Ex. 99.1 HTML): adj. EBITDA reconciliation, SBC by function footnote, FCF reconciliation, balance sheet, outlook sentences, KPI box", "data/raw/letters",
  SRC + "abnb_exsbc_stack.py", frequency="quarterly", pit_lag_days=40, target_lines="margin_total;sbc;da;int_inc;other_inc;tax;fcf_timing;capex;guide",
  mechanism="Letter-basis series (the numbers the Street scores against) and the guide text.", prior_evidence="Parsed by exsbc_stack, fcf_bridge, 02 ledger, 31a.", suggested_method="M3 guide;M7 below-EBITDA", n_obs=23)
R("X05_call_transcripts_web", "23 earnings-call transcripts 4Q20-2Q26 plus 5 conference transcripts (MS23, MS24, BERN24, GS24, GS25) as HTML (stockanalysis / IR)", "data/raw/transcripts/web",
  SRC + "download_abnb_transcripts.py", frequency="event", pit_lag_days=0, target_lines="guide;cor;ops;pd;sm_brand;sm_field;ga;sbc;tax",
  mechanism="Source of spoken cost guides absent from letters (FY24 flat marketing, FY25 +20bp take rate) and AI-spend statements; WS05 extends.", prior_evidence="31a used these plus IR PDFs; pre-2023 rows tagged -sa (audio-aligned).",
  suggested_method="M3 guide", n_obs=28)
R("X06_ir_transcripts_factset", "FactSet-corrected IR transcripts 1Q23-2Q26 (PDF + JSON) under data/raw/regulatory/transcripts/ with manifest", "data/raw/regulatory/transcripts", SRC + "complete_regulatory_archive.py",
  frequency="event", pit_lag_days=0, target_lines="guide", mechanism="Corrected wording for 2023+ statements.", prior_evidence="31a quote verification runs against these.", suggested_method="M3 guide", n_obs=30)
R("X07_bea_pce_travel", "BEA PCE travel panel monthly 2015-01 to 2026-07 (accommodations, hotels, air, inbound/outbound foreign travel; nominal, real, price)", "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv", SRC + "abnb_kpi_vs_category.py",
  frequency="monthly", pit_lag_days=30, target_lines="rev_drivers", mechanism="US demand cycle state (M6).", prior_evidence="Committed as a raw exception.", suggested_method="M6 cycle", pcol="date")
R("X08_regulatory_sqlite", "Regulatory research database: 32 factors, 48 sources, 14 transcript records, 9 earnings observations, market inventory, cohorts (Barcelona, Maui), Hawaii vintages, NYC benchmark", "data/processed/abnb_regulatory.sqlite",
  SRC + "build_regulatory_database.py", frequency="event", pit_lag_days=0, target_lines="ga;rev_drivers", mechanism="Dated legal/fine events for the G&A legal-cost series.", prior_evidence="PR #19.",
  suggested_method="M4 alt", first_period="2019", last_period="2026", n_obs="")
R("X09_manifests", "Acquisition manifests: edgar_filings_log.csv, macro_download_log.csv, inside_airbnb_download_log.csv, expansion_source_manifest.csv, municipal_download_log.csv (URL, status, sha256 per file)", "data/manifests/edgar_filings_log.csv",
  SRC + "acquisition/", frequency="event", pit_lag_days=0, target_lines="guide", mechanism="Provenance pattern WS04 must follow for data/manifests/margin_build/.", prior_evidence="Append-only.",
  suggested_method="M4 alt", first_period="2026-09-05", last_period="2026-09-07", n_obs="")

# ---- L: licensed local (read in place; derived statistics only) -----------------------------------------------
R("L01_bloomberg_long_export", "Bloomberg long export (6,365 rows): PX_LAST, 30d vol, comps, target/rating history, BEST_SALES / BEST_EBITDA / BEST_EPS for 1FQ, 2FQ, 1FY, 2FY by obs_date for ABNB, BKNG, EXPE, MAR, HLT, H, IHG (sheet 1_Consensus_TS)",
  "data/raw/theo_onedrive/AIRBNB DATA/raw_expansion_licensed/v2_2026-09-05/bloomberg/bbg_extracted_long.csv", "", frequency="daily", pit_lag_days=0,
  target_lines="margin_total;guide", mechanism="Consensus EBITDA/EPS revision history (secondary to LSEG); WS03 tests whether obs_date is true history or pull-date anchored.",
  prior_evidence="Memory: pull-date anchored, not point-in-time (FY1 revenue at 31 Dec 2020 reads 14,270).", status="licensed_local", suggested_method="M5 street",
  first_period="2020-12", last_period="2026-09", n_obs=6365)
R("L02_bloomberg_options_workbook", "Bloomberg options workbook (4 Sep 2026): daily implied/realised vol since IPO (1,436 rows), IV term structure, 67 monthly ATM straddles, full chain", "data/raw/theo_onedrive/AIRBNB DATA/ABNB_Options_Bloomberg_Pull (1).xlsx",
  "", frequency="daily", pit_lag_days=0, target_lines="sbc", mechanism="Historical IV for option-grant valuation (minor).", prior_evidence="Aug 2026 implied 10.0% vs realised 33.7%.", status="licensed_local",
  suggested_method="M7 below-EBITDA", first_period="2020-12", last_period="2026-09", n_obs=1436)
R("L03_factset_transcripts", "FactSet transcripts Q4 2020, Q4 2021, Q4 2022, Q3 23, Q2 24, Q2 25 (OneDrive, licensed)", "data/raw/theo_onedrive/AIRBNB DATA/raw_expansion_licensed/v2_2026-09-05/transcripts_factset", "",
  frequency="event", pit_lag_days=0, target_lines="guide", mechanism="Corrected wording for the pre-2023 -sa rows in 31a.", prior_evidence="Not yet used by 31a.", status="licensed_local", suggested_method="M3 guide",
  first_period="4Q20", last_period="2Q25", n_obs="")
R("L04_lseg_story_bodies", "LSEG/Refinitiv story bodies and headline rows for regulatory events (data/raw/regulatory/lseg, local only)", "data/raw/regulatory/lseg", SRC + "pull_regulatory_documents.py",
  frequency="event", pit_lag_days=0, target_lines="ga", mechanism="Fine/settlement news dates for G&A one-offs; LSEG news API reachable for a margin-news count (WS04/05).", prior_evidence="Used by the regulatory package.",
  status="licensed_local", suggested_method="M4 alt", first_period="2019", last_period="2026", n_obs="")

# ---- T: Theo / Crossover packages ---------------------------------------------------------------------------------
R("T01_theo_source_registry", "Theo's source_registry.csv (45 sources) and free_api_registry.csv (27 APIs): provider, mechanism, URL, auth, lag, licence, PIT support (H.10, ECB, BLS CPI, ALFRED, TSA, BTS, Eurostat, Trends, Wikimedia, Census QSS ...)",
  "theos-past-research/research/source_registry.csv", "", frequency="registry", pit_lag_days=0, target_lines="guide",
  mechanism="Reachability and PIT notes for macro sources WS04 will reuse (ALFRED vintages for rates/CPI).", prior_evidence="Theo: 'forecast edge unproven'.", suggested_method="M4 alt",
  first_period="2026-09", last_period="2026-09", n_obs="")
R("T02_crossover_web_traffic_schema", "ABNB-Crossover web_traffic_snapshot (Similarweb free tier; SIG domains, schema/template only) and bb_consensus_at_call.csv (schema only, no ABNB rows)", "ABNB-Crossover/data/web_traffic_snapshot_2026-08.csv", "",
  frequency="snapshot", pit_lag_days=11, target_lines="sm_brand", mechanism="Template for a Similarweb visits-per-marketing-dollar series (ABNB not yet captured).", prior_evidence="03_ACCESS_MAP.md describes free-tier limits.",
  status="candidate_pull", suggested_method="M4 alt", first_period="2026-07", last_period="2026-07", n_obs="")

for r in REG:
    fill_periods(r)

# ----------------------------------------------------------------------------------------------------------------
# gaps: inputs not in the repo that plausibly bear on a line (WS04 pull list)
# ----------------------------------------------------------------------------------------------------------------
GAPS: list[dict] = []


def Gp(gap_id, inp, target_lines, mechanism, source, url, reach, freq, hist, pit, prio, action):
    GAPS.append(dict(gap_id=gap_id, input=inp, target_lines=target_lines, mechanism=mechanism, suggested_source=source,
                     url_pattern_or_field=url, reachability=reach, frequency=freq, history=hist, pit_note=pit, priority=prio, ws04_action=action))


Gp("GAP01", "Quarterly headcount / job-posting counts", "pd;ga;ops;sbc",
   "Product development and G&A are payroll (10-K: 'increase in payroll-related expenses driven by an increase in headcount'); headcount is disclosed only at 31 Dec. Open-role counts lead hires by 1-2 quarters.",
   "Wayback captures of careers.airbnb.com (count of /positions/ links per capture) at monthly spacing 2019-2026; LinkedIn public company page employee count via Wayback; Common Crawl as fallback",
   "http://web.archive.org/cdx/search/cdx?url=careers.airbnb.com/positions*&output=json&from=2019&collapse=timestamp:6 ; http://archive.org/wayback/available?url=careers.airbnb.com&timestamp=YYYYMM01 ; http://web.archive.org/cdx/search/cdx?url=linkedin.com/company/airbnb&from=2019&output=json",
   "archives", "monthly (capture-dependent)", "2019-2026 if captures exist", "Capture timestamp = PIT date; no revision", 1,
   "Pull CDX list, fetch 1 capture/month, parse role counts by team (Engineering, Trust & Safety, Sales) and location; save HTML raw + manifest")
Gp("GAP02", "Headcount statements in transcripts (quarterly)", "pd;ga;sbc",
   "Management occasionally states headcount growth on calls ('grew headcount ~12%', 'lower than 2025'); a quarterly interpolation anchor.",
   "grep data/raw/transcripts/web/*.html and data/raw/regulatory/transcripts/*.json for 'headcount', 'employees', 'hiring'", "local grep", "repo", "event", "4Q20-2Q26", "statement date", 2,
   "Extract sentences with numbers to a dated table (feeds WS05 statements file too)")
Gp("GAP03", "Tech-wage and SF cost-of-living indices", "pd;ga;ops",
   "Payroll per employee (SBC per employee $193k, cash comp undisclosed) moves with software-labour wage inflation; deflates the headcount plan into $.",
   "FRED/BLS CES average hourly earnings: software publishers (CES5051200003), computer systems design (CES6054150003), ECI private wages (ECIWAG), SF-Oakland CPI (CUURS49BSA0); BLS OES SOC 15-1252 annual",
   "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CES5051200003 ; ...?id=CES6054150003 ; ...?id=ECIWAG ; ...?id=CUURS49BSA0", "FRED (keyless)", "monthly / quarterly", "2006+", "ALFRED vintages available for PIT", 2,
   "Pull four series; build y/y; test vs PD and G&A cash per employee (annual, n 5) and per night (quarterly, n 22)")
Gp("GAP04", "3-month T-bill and 1-year yields (interest-income yield driver)", "int_inc",
   "Interest income = yield x (corporate cash + funds held). Airbnb holds T-bills/commercial paper (10-K); DTB3 is not in the FRED cache (only FEDFUNDS, DGS2, DGS10).",
   "FRED DTB3, DGS1, DGS3MO, TB3MS; ECB deposit rate for EUR balances", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3 ; ...?id=DGS3MO ; ...?id=DGS1 ; ...?id=TB3MS", "FRED (keyless)", "daily", "1954+",
   "Daily; quarterly average is knowable at quarter end (lag 0)", 1, "Pull; regress quarterly interest income / avg interest-earning balances (B05) on avg DTB3 with a 1-quarter lag, n 22; supply yield beta and lag to M7")
Gp("GAP05", "Funds-held vs corporate-cash split of interest income", "int_inc;fcf_timing",
   "10-K: interest income 'consists primarily of interest earned on cash, cash equivalents, marketable securities, and amounts held on behalf of customers' - split never disclosed; needed because funds held is seasonal (Q1/Q2 peak) and RNPL is shrinking it.",
   "10-K/10-Q balance sheets (XBRL FundsReceivableAndAmountsHeldOnBehalfOfCustomers, FundsHeldForClients) + Note on investments; model as blended yield",
   "data/raw/xbrl/ABNB_companyfacts.json tags FundsHeldForClients, CashAndCashEquivalentsAtCarryingValue, ShortTermInvestments; EDGAR full-text search 'interest income' 'funds held'", "EDGAR", "quarterly", "4Q20+",
   "10-Q filing date (~40-45 days)", 1, "Build avg interest-earning balance by component; fit blended yield (GAP04)")
Gp("GAP06", "10-Q primary documents 1Q21-1Q26 (three-month MD&A deltas, repurchase table, hedge notes)", "cor;ops;pd;sm_brand;sm_field;ga;shares;other_inc",
   "Only the 2Q26 10-Q and the 10-Ks are in the tree; the quarterly $ deltas by component (payroll, marketing activities, third-party providers, insurance, cloud, non-income taxes) and the monthly buyback table exist only in 10-Qs.",
   "EDGAR submissions API -> primary 10-Q documents (User-Agent 'citadel-abnb research ksurapaneni@ufl.edu')",
   "https://data.sec.gov/submissions/CIK0001559720.json ; https://www.sec.gov/Archives/edgar/data/1559720/<accession-no-dashes>/<primary-doc>.htm ; EDGAR FTS https://efts.sec.gov/LATEST/search-index?q=%22marketing%20activities%22&ciks=0001559720&forms=10-Q",
   "EDGAR", "quarterly", "1Q21-2Q26 (22 filings)", "Filing acceptance timestamp is the PIT date", 1,
   "Fetch 22 10-Qs to data/raw/margin_build/04_alt_signals/edgar/, manifest with sha256; parse MD&A component deltas into a quarterly long table for WS02/M1")
Gp("GAP07", "Peer XBRL companyfacts (BKNG CIK 1075531, EXPE 1324424, MAR, HLT) for quarterly marketing and cost lines", "sm_brand;margin_total",
   "Cyclical cost-flex comparators: how BKNG/EXPE marketing and margins responded to 2020, 2022 and 2024-25 deceleration; only ABNB companyfacts is in this tree (BKNG/EXPE JSON referenced in data/README live in the main tree).",
   "SEC companyfacts API", "https://data.sec.gov/api/xbrl/companyfacts/CIK0001075531.json ; CIK0001324424.json ; MAR CIK0001048286 ; HLT CIK0001585689", "EDGAR", "quarterly", "2009+", "Filing dates", 2,
   "Pull four JSONs; extract SellingAndMarketingExpense / AdvertisingExpense / OperatingIncomeLoss quarterly; build peer marketing-intensity vs growth panel for M6")
Gp("GAP08", "Support-load proxies: Trustpilot / BBB / Sitejabber review and complaint counts, app-store review counts and ratings, Downdetector", "ops",
   "Contacts per night drive operations & support; public complaint volumes are the only outside read of contact intensity and of AI-deflection success.",
   "Wayback captures of trustpilot.com/review/www.airbnb.com (total reviews, rating), bbb.org Airbnb profile (complaints closed last 3 yrs), apps.apple.com/us/app/airbnb/id401626263 rating count, play.google.com Airbnb listing",
   "http://web.archive.org/cdx/search/cdx?url=trustpilot.com/review/www.airbnb.com&from=2019&output=json&collapse=timestamp:6 ; ...url=bbb.org/us/ca/san-francisco/profile/vacation-rentals/airbnb-inc-1116-393811 ; ...url=apps.apple.com/us/app/airbnb/id401626263",
   "archives", "monthly captures", "2019-2026 (Trustpilot dense)", "Capture date is PIT; cumulative counts -> difference for flow", 2,
   "Parse cumulative review/complaint counts per capture; compute quarterly flow per million nights; test vs ops cash per night y/y (n ~14)")
Gp("GAP09", "Payment processing rate changes: Visa/Mastercard interchange and cross-border fee announcements, Adyen/Stripe published pricing, EU IFR, Reg II", "cor",
   "Merchant fees are ~1.8% of GBV (07); scheme fee changes (April/October cycles), cross-border assessment fees and the regional mix of card vs local methods move the rate.",
   "Public announcements (Visa/Mastercard pricing bulletins via press), Adyen pricing page and Stripe pricing page via Wayback; Airbnb 10-K payments description",
   "http://web.archive.org/cdx/search/cdx?url=stripe.com/pricing&from=2019&output=json ; ...url=adyen.com/pricing ; LSEG news search 'interchange' 'Visa' 'Mastercard' 2019-2026", "archives / third_party_public / LSEG news", "event", "2019+",
   "Announcement date", 2, "Build a dated event table of scheme-fee changes; step dummies for CoR per $ GBV")
Gp("GAP10", "Cross-border / cross-currency share of GBV (payment FX cost driver)", "cor;rev_drivers",
   "Cross-border nights carry FX conversion cost and the 3% guest FX fee; cross-border share disclosure stopped 1Q24 (46%); cross-currency GBV share given once (1Q25).",
   "Repo: Lane 1 X package od_nights_matrix.csv / observed_share_triple.csv (regional_kernel_v1); 02_kpi_panel cross_border_share_pct; letters", "data/processed/forecast_methods/regional_kernel_v1/od_nights_matrix.csv", "repo", "quarterly", "1Q21-1Q24 disclosed; modelled after",
   "Disclosed at print", 2, "Extend the cross-border share series with the X-package O-D matrix; use as a CoR-per-GBV mix driver")
Gp("GAP11", "Cloud / hosting price indices and AWS price announcements; contracted hosting obligations by year", "cor",
   "Third-party data-center cost sits in CoR; server costs +$15M 1H26 on reserved-instance amortisation; hosting commitment $1.7B through 2031 (~$280M/yr vs ~$220M).",
   "10-K Note 13 (in repo, annual); AWS price-change announcements (aws.amazon.com/blogs/aws/category/price-reduction via Wayback); Cloud price indices (none official); 10-Q commitments updates",
   "http://web.archive.org/cdx/search/cdx?url=aws.amazon.com/blogs/aws/category/price-reduction*&from=2019&output=json ; 10-K Note 13 'data hosting' sentences in data/raw/filings/txt", "archives / EDGAR", "annual + event", "FY2022+",
   "10-K filing date", 2, "Table of hosting commitment by year from Note 13 (6 10-Ks); annual step in CoR ex-payments (07 cor_cash_ex_payments_musd)")
Gp("GAP12", "AirCover / host-protection claims and insurance premium proxies", "ops;cor",
   "Ops & support includes 'customer relations costs ... expenses associated with our host protection programs' and insurance premiums (+$14M FY25 'as a result of higher nights booked'); no public claims data.",
   "10-K MD&A insurance deltas (in repo); insurer/captive filings not public; news counts (LSEG) for AirCover payouts; nothing else reachable",
   "data/raw/filings/txt (grep 'insurance'); LSEG ld.news headlines query 'Airbnb AirCover'", "EDGAR / LSEG news / not reachable for claims", "annual", "FY2021+", "10-K date", 3,
   "Log as not reachable beyond MD&A deltas; carry insurance as % of nights from 07")
Gp("GAP13", "Chargeback and fraud loss series", "cor",
   "10-K FY2025: 'total chargeback expense was $67 million'; merchant fees + chargebacks 1.82% of GBV; RNPL and cancellation changes raise chargeback exposure.",
   "10-K text FY2021-FY2025 (chargeback sentence each year); Visa/Mastercard chargeback-ratio programme thresholds", "grep 'chargeback' in data/raw/filings/txt/*.txt", "EDGAR", "annual", "FY2020+", "10-K date", 2,
   "Extract annual chargeback $ and % GBV; test 2025-26 step vs RNPL share")
Gp("GAP14", "Marketing spend trackers: Meta Ad Library (EU transparency), Google Ads Transparency Center, TV ad-spend press (iSpot, MediaRadar quotes), app-install rank history", "sm_brand",
   "Brand + performance marketing is the least-guided, most-missed line (63% kept); outside reads of media flighting would date the Q1 campaign and the 2026 ramp.",
   "Meta Ad Library report (EU DSA transparency: advertiser 'Airbnb' spend ranges) via https://www.facebook.com/ads/library/report/ ; Google Ads Transparency Center (no spend, creative counts); iSpot.tv public estimated TV spend pages via Wayback; AppFigures/SensorTower free rank pages via Wayback",
   "https://www.facebook.com/ads/library/report/?country=ALL ; https://adstransparency.google.com/advertiser/<id> ; http://web.archive.org/cdx/search/cdx?url=ispot.tv/brands/*/airbnb&from=2019&output=json", "third_party_public / archives (partial)", "monthly / daily", "2019+ (iSpot), 2023+ (DSA)",
   "Capture/report dates; Meta ranges are coarse", 2, "Try each; log reachability; where a series exists, test y/y vs brand+perf cash y/y (n 18 quarters)")
Gp("GAP15", "Google Trends re-pull with pull-date stamp (branded search per marketing $)", "sm_brand",
   "Repo has 08_trends_weekly (not PIT); a fresh weekly capture with the pull date stamped is the insurance series; search y/y per brand-spend y/y is a marketing-efficiency read.",
   "pytrends (py -3.13): 'airbnb', 'vrbo', 'booking.com', 'hotels' worldwide and US/GB/DE/FR/BR/JP/AU, monthly 2019-2026", "pytrends TrendReq().build_payload(kw_list, timeframe='2019-01-01 2026-09-13', geo=...)", "third_party_public", "weekly/monthly", "2004+",
   "NOT point-in-time (renormalised per pull); stamp pull date", 3, "Pull, stamp, test vs S&M cash growth (never done: WS08 tested only nights)")
Gp("GAP16", "Sponsorship and campaign calendar (IOC TOP partner 2021-2028, Paris 2024, Milan-Cortina 2026, LA 2028; FIFA 2026; Super Bowl-period campaigns)", "sm_brand",
   "Brand marketing has a fixed multi-year component (Olympic partnership reported ~$500M over 9 years) and event-quarter spikes (3Q24 Paris, 1Q26 Milan-Cortina) that explain seasonality residuals.",
   "Press (IOC announcement Nov 2019, Airbnb newsroom via archives), 10-K commitments; dated table hand-built", "https://olympics.com/ioc/news/ioc-and-airbnb-announce-major-global-olympic-partnership ; Wayback of news.airbnb.com posts", "third_party_public / archives", "event", "2019+",
   "Announcement dates", 2, "Build a dated campaign/sponsorship table with quarter dummies for M4")
Gp("GAP17", "Effective-tax-rate reconciliation and cash-tax schedule", "tax",
   "ETR guided 'high teens' (OBBBA); cash taxes $232M FY25 vs $626M provision as released deferred tax assets are used; FCF loses 2-3pt of revenue as they converge.",
   "10-K income-tax note (rate reconciliation, DTA balances, NOLs) FY2020-FY2025 in data/raw/filings/txt; XBRL tags IncomeTaxExpenseBenefit, CurrentIncomeTaxExpenseBenefit, DeferredIncomeTaxExpenseBenefit, DeferredTaxAssetsNet, IncomeTaxesPaidNet",
   "grep 'effective tax rate' / 'deferred tax assets' in data/raw/filings/txt/*.txt; companyfacts tags above", "EDGAR (repo)", "annual (quarterly tags)", "FY2020+", "10-K date", 1,
   "Extract rate reconciliation table by year; DTA run-down schedule; supply ETR and cash-tax path to M7")
Gp("GAP18", "Period-end shares outstanding, buyback cadence by month, RSU vesting schedule", "shares;sbc",
   "EPS uses weighted diluted shares; period-end (dei:EntityCommonStockSharesOutstanding on the 10-Q cover) plus the monthly repurchase table and unvested RSU count (10-K equity note) give a forward count path.",
   "XBRL dei tag (in companyfacts JSON, repo); 10-Q Item 2 monthly repurchase table (GAP06); 10-K stock-comp note: unvested RSUs, weighted grant value, unrecognised SBC and weighted period",
   "data/raw/xbrl/ABNB_companyfacts.json -> facts.dei.EntityCommonStockSharesOutstanding ; 10-K note 'Unrecognized stock-based compensation'", "EDGAR (repo + GAP06)", "quarterly", "4Q20+", "Cover date ~ filing date", 1,
   "Build count path: shares_end(t) = shares_end(t-1) - buyback$/avg price + RSU vests - withheld; unrecognised SBC gives 12-month-forward SBC floor")
Gp("GAP19", "Lodging-tax and non-income-tax reserves, fines and settlements ledger", "ga",
   "G&A includes 'indirect taxes, including lodging tax reserves'; FY23 G&A distorted +1,160bp by Italian reserves; 1H26 G&A -$38M non-income taxes; Spain EUR64M fine 2026.",
   "10-K/10-Q 'reserves for lodging taxes' and contingencies notes (repo 10-Ks + GAP06); LSEG news for fines; regulatory SQLite events", "grep 'lodging tax' 'reserve' 'settlement' in data/raw/filings/txt; abnb_regulatory_events.csv", "EDGAR / repo / LSEG news", "event", "FY2020+",
   "Filing / announcement date", 2, "Dated one-off ledger with $ and line; strip from G&A to get underlying payroll trend")
Gp("GAP20", "Restructuring / other add-back history and forward D&A schedule (capitalised software, acquired intangibles)", "da;addbacks",
   "D&A ~0.7% of revenue; amortisation of internally developed software sits in CoR; add-backs 0.9%; no restructuring since 2020.",
   "XBRL DepreciationDepletionAndAmortization, CapitalizedComputerSoftwareAmortization1, RestructuringCharges; 10-K property note", "data/raw/xbrl/ABNB_companyfacts.json", "EDGAR (repo)", "quarterly", "2019+", "Filing date", 3,
   "Extract; hold D&A % revenue with capex 0.3%")
Gp("GAP21", "Consensus for cost lines, EBITDA, EPS, FCF by date (LSEG) and EBITDA-margin surprise history", "margin_total;guide",
   "Only 8 of 23 prints have EBITDA consensus in the repo; M5 needs Street EBITDA at each guide date and print date.",
   "LSEG desktop session (brief snippet): TR.EBITDAMean/.date/.periodenddate, TR.EPSMean, TR.FCFMean, TR.SGAExpMean, TR.RDExpMean, TR.COGSMean; Period FQ1-FQ4, FY1-FY3", "ld.get_data('ABNB.O', ['TR.EBITDAMean','TR.EBITDAMean.date','TR.EBITDAMean.periodenddate'], {'SDate':'2021-01-01','EDate':'2026-09-13','Frq':'D','Period':'FQ1'})",
   "LSEG", "daily", "2021+", "Observation date = PIT", 1, "WS03 owns this; WS04 only if WS03 fails")
Gp("GAP22", "Layoff / WARN notices and hiring-freeze events", "pd;ga;ops;sbc",
   "Headcount step changes (May 2020 -25%) and hiring pauses are visible in California EDD WARN filings and layoffs.fyi before the 10-K headcount.",
   "California EDD WARN report (public xlsx), layoffs.fyi (public sheet via Wayback)", "https://edd.ca.gov/en/jobs_and_training/Layoff_Services_WARN/ (WARN report xlsx) ; http://web.archive.org/cdx/search/cdx?url=layoffs.fyi&from=2020&output=json", "third_party_public / archives", "event", "2020+",
   "Notice date", 3, "Pull; dated dummies (only 2020 expected for ABNB)")
Gp("GAP23", "Similarweb free-tier airbnb.com monthly visits and channel mix (direct vs paid)", "sm_brand",
   "'~90% of traffic direct or unpaid' is management's efficiency claim; a paid-channel share series tests performance-marketing intensity.",
   "similarweb.com/website/airbnb.com free tile (3-month aggregate, top channels) captured monthly; Wayback for history", "https://www.similarweb.com/website/airbnb.com/ ; http://web.archive.org/cdx/search/cdx?url=similarweb.com/website/airbnb.com*&from=2020&output=json", "third_party_public / archives", "monthly", "2020+ (captures sparse)",
   "Capture date", 3, "Capture now and via Wayback; paid share x visits vs brand+perf cash (n small)")
Gp("GAP24", "Third-party support-provider and BPO cost indices (Philippines/India BPO wage, Teleperformance/Concentrix pricing commentary)", "ops",
   "'The vast majority of our community support is performed by third-party service providers' (13,000 workers FY25); BPO wage inflation and the AI-deflection substitution set ops cost per contact.",
   "Teleperformance / Concentrix / TaskUs quarterly reports (EDGAR for TaskUs CIK 1829864, Concentrix CIK 1803599: revenue per employee, pricing commentary); Philippines BSP wage data", "https://data.sec.gov/api/xbrl/companyfacts/CIK0001829864.json ; CIK0001803599.json", "EDGAR", "quarterly", "2020+",
   "Filing date", 3, "Pull BPO peer revenue/headcount as a unit-cost index; low priority")
Gp("GAP25", "ALFRED vintages for rates and CPI used in any PIT refit", "int_inc;ga",
   "Macro inputs must be the vintage known at the guide date; FRED cache is latest-vintage.", "ALFRED", "https://alfred.stlouisfed.org/series/downloaddata?seid=DTB3 ; https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&realtime_start=YYYY-MM-DD (needs free key)", "FRED/ALFRED",
   "as source", "1950+", "True vintages", 3, "Only for series that survive a first-pass test (rates are unrevised; CPI revisions are tiny)")
Gp("GAP26", "Support automation timeline as a step series (AI resolution share 15% -> 33% -> 40% -> 45%; support cost per booking -10% / -16%)", "ops",
   "Management's only quantified line-level cost claims; a dated step series lets M4 test whether the line moved when the claims were made.",
   "31a statements S141/S145/S151/S152/S160/S188 (repo); WS05 statement file", "data/processed/overnight/31a_mgmt_margin_statements.csv", "repo", "event", "2Q23+", "Statement date", 2,
   "Build quarterly series of stated AI resolution share and per-booking cost change; interpolate; test vs ops cash per night")

# ----------------------------------------------------------------------------------------------------------------
# validate and write
# ----------------------------------------------------------------------------------------------------------------
errors: list[str] = []
seen = set()
for r in REG:
    if r["series_id"] in seen:
        errors.append(f"duplicate series_id {r['series_id']}")
    seen.add(r["series_id"])
    if not (ROOT / r["file_path"]).exists():
        errors.append(f"missing file_path {r['file_path']} ({r['series_id']})")
    if r["script_path"] and not (ROOT / r["script_path"]).exists():
        errors.append(f"missing script_path {r['script_path']} ({r['series_id']})")
    if not r["target_lines"] or not r["mechanism"]:
        errors.append(f"empty target_lines/mechanism for {r['series_id']}")
    for k in COLS:
        r.setdefault(k, "")

census = pd.DataFrame([{k: r[k] for k in COLS} for r in REG])
gaps = pd.DataFrame(GAPS, columns=GAP_COLS)

LINES = ["cor", "ops", "pd", "sm_brand", "sm_field", "ga", "sbc", "da", "addbacks", "int_inc", "other_inc", "tax", "shares",
         "fcf_timing", "capex", "rev_drivers", "margin_total", "guide"]
rows = []
for line in LINES:
    m = census["target_lines"].str.split(";").apply(lambda xs: line in xs)
    g = gaps["target_lines"].str.split(";").apply(lambda xs: line in xs)
    rows.append(dict(target_line=line,
                     n_series=int(m.sum()),
                     n_available=int((m & (census["status"] == "available")).sum()),
                     n_needs_refresh=int((m & (census["status"] == "needs_refresh")).sum()),
                     n_licensed_local=int((m & (census["status"] == "licensed_local")).sum()),
                     n_candidate_pull_in_census=int((m & (census["status"] == "candidate_pull")).sum()),
                     n_gaps=int(g.sum()),
                     n_gaps_priority1=int((g & (gaps["priority"] == 1)).sum())))
summary = pd.DataFrame(rows)

census.to_csv(OUT / "01_input_census.csv", index=False, quoting=csv.QUOTE_MINIMAL)
gaps.to_csv(OUT / "01_gaps.csv", index=False, quoting=csv.QUOTE_MINIMAL)
summary.to_csv(OUT / "01_census_summary_by_line.csv", index=False)

# re-validate the written CSV (paths exist, columns present)
chk = pd.read_csv(OUT / "01_input_census.csv")
if list(chk.columns) != COLS:
    errors.append("column mismatch in written census")
for p in chk["file_path"]:
    if not (ROOT / p).exists():
        errors.append(f"post-write missing {p}")
gchk = pd.read_csv(OUT / "01_gaps.csv")
if list(gchk.columns) != GAP_COLS:
    errors.append("column mismatch in written gaps")
n_concrete = int((gchk["url_pattern_or_field"].str.len() > 10).sum())

print(f"census rows: {len(chk)}  (available {int((chk.status=='available').sum())}, needs_refresh {int((chk.status=='needs_refresh').sum())}, "
      f"licensed_local {int((chk.status=='licensed_local').sum())}, candidate_pull {int((chk.status=='candidate_pull').sum())})")
print(f"gap rows: {len(gchk)}  with concrete source string: {n_concrete}  priority-1: {int((gchk.priority==1).sum())}")
print(summary.to_string(index=False))
if n_concrete < 10:
    errors.append("fewer than 10 concrete candidate pulls")
if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("OK: all paths exist, columns present, pass line met (>=10 concrete candidate pulls).")
sys.exit(0)
