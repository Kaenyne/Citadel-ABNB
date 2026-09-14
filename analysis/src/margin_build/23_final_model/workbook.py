"""WS23 step 6: model/ABNB_margin_model.xlsx.

Sheets: README, Inputs, Lines, Bridge, Scenarios, Consensus, Seasonality, Weights.
Every forecast cell traces to a CSV in data/processed/margin_build/23_final_model/.
Formulas are used where the logic is an identity (margin = EBITDA / revenue,
operating income = adj EBITDA - D&A - SBC, EPS = net income / diluted shares,
FY = sum of quarters); values carry a source column everywhere else.

Interpreter: py -3.13   (openpyxl)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[4]
PROC = ROOT / "data" / "processed" / "margin_build"
OUT = PROC / "23_final_model"
XLSX = ROOT / "model" / "ABNB_margin_model.xlsx"

HDR = Font(bold=True, color="FFFFFF")
HDRFILL = PatternFill("solid", fgColor="1F3B57")
SUB = Font(bold=True)
SUBFILL = PatternFill("solid", fgColor="DCE6F1")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
QF = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]


def write_table(ws, df, start_row=1, title=None, number_format="#,##0.00", widths=None):
    r = start_row
    if title:
        ws.cell(row=r, column=1, value=title).font = SUB
        ws.cell(row=r, column=1).fill = SUBFILL
        r += 1
    for j, c in enumerate(df.columns, start=1):
        cell = ws.cell(row=r, column=j, value=str(c))
        cell.font = HDR
        cell.fill = HDRFILL
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
    for _, row in df.iterrows():
        for j, c in enumerate(df.columns, start=1):
            v = row[c]
            if isinstance(v, (np.floating, float)) and not isinstance(v, bool):
                v = None if (v is None or (isinstance(v, float) and np.isnan(v))) else float(v)
            elif isinstance(v, (np.integer,)):
                v = int(v)
            elif v is not None and not isinstance(v, (int, float, str)):
                v = str(v)
            cell = ws.cell(row=r, column=j, value=v)
            cell.border = BOX
            if isinstance(v, float):
                cell.number_format = number_format
        r += 1
    for j, c in enumerate(df.columns, start=1):
        w = (widths or {}).get(c, min(max(12, len(str(c)) + 2), 46))
        ws.column_dimensions[get_column_letter(j)].width = w
    return r + 1


def main():
    XLSX.parent.mkdir(parents=True, exist_ok=True)
    live = pd.read_csv(OUT / "23_combination_live.csv")
    path = pd.read_csv(OUT / "23_path_rule.csv")
    bands = pd.read_csv(OUT / "23_bands.csv")
    lines = pd.read_csv(OUT / "23_lines_quarterly.csv")
    pl = pd.read_csv(OUT / "23_forecast_quarterly.csv")
    ann = pd.read_csv(OUT / "23_forecast_annual.csv")
    cons = pd.read_csv(OUT / "23_vs_consensus.csv")
    scen = pd.read_csv(OUT / "23_scenarios.csv")
    seas = pd.read_csv(OUT / "23_seasonality.csv")
    macro = pd.read_csv(OUT / "23_macro_sensitivity.csv")
    floor = pd.read_csv(OUT / "23_fy26_floor_breakeven.csv")
    card = pd.read_csv(OUT / "23_card_5nov.csv")
    bi = pd.read_csv(OUT / "23_card_budget_identity.csv")
    wts = pd.read_csv(OUT / "23_combination_weights.csv")
    sc23 = pd.read_csv(OUT / "23_combination_scores.csv")
    diag = pd.read_csv(OUT / "23_diag_leave_one_out.csv")
    dmem = pd.read_csv(OUT / "23_diag_member_scores.csv")
    rev = pd.read_csv(PROC / "06_fy27_path_v2" / "06_revenue_path_3q26_4q27_v2b.csv")
    revb = rev[rev.line == "revenue_musd"].pivot(index="quarter", columns="scenario", values="value")

    wb = Workbook()

    # ---------------------------------------------------------------- README
    ws = wb.active
    ws.title = "README"
    txt = [
        ("ABNB margin model — WS23 final", True),
        ("Built 14 Sep 2026 by the margin-build run (docs/margin-build/SYNTHESIS.md).", False),
        ("Vintage: 2026-09-11 (LSEG consensus row). Revenue path: bridge v3 / WS06 v2b.", False),
        ("", False),
        ("What this workbook is", True),
        ("A margin model on top of an adopted revenue path. It does NOT forecast revenue.", False),
        ("The adj EBITDA margin for 3Q26 comes from final-margin|combined|stack_clip, a", False),
        ("six-member leave-future-out combination plus a zero-parameter management-sentence clip.", False),
        ("4Q26 comes from the Street baseline (the combination loses to it at h=1).", False),
        ("2027 is a SCENARIO: the combination fails its test at h>=2.", False),
        ("FY28 is the FY27 margin rolled flat — an extrapolation, not a forecast.", False),
        ("", False),
        ("Sheets", True),
        ("Inputs      revenue path, model parameters, sources", False),
        ("Lines       six cash cost lines, history 1Q21-2Q26 and forecast 3Q26-4Q27", False),
        ("Bridge      adj EBITDA -> operating income -> EPS -> FCF, quarterly and annual", False),
        ("Scenarios   bear/base/bull revenue x cost-response variant (M6 k), macro sensitivity, FY26 floor", False),
        ("Consensus   model vs LSEG / Bloomberg / management, with n and dispersion", False),
        ("Seasonality quarterly profile with the mechanical / discretionary cost split", False),
        ("Weights     the combination's member weights, backtest scores and diagnostics", False),
        ("Card        the 5 Nov card and the FY-guide budget identity", False),
        ("", False),
        ("Traceability", True),
        ("Every forecast number is in data/processed/margin_build/23_final_model/*.csv.", False),
        ("Rebuild: py -3.13 analysis/src/margin_build/23_final_model/run.py", False),
        ("", False),
        ("Numbers that must NOT be quoted (kill list, AGENT_BRIEF §6 + WS21 addendum + WS22)", True),
        ("M3 LIVE 4Q26 34.51% / FY26 37.03%; M6 FY28 31.3%; M5 '+0.41pt beat' as a model output;", False),
        ("M1 d_steps_rw; any oracle spec; 'survives both windows' as evidence of skill;", False),
        ("any margin MAE ratio without its p-value and quarters-better count;", False),
        ("any quarterly FCF forecast; 'M7 tax quantiles under-cover'.", False),
    ]
    for i, (t, bold) in enumerate(txt, start=1):
        c = ws.cell(row=i, column=1, value=t)
        if bold:
            c.font = SUB
            c.fill = SUBFILL
    ws.column_dimensions["A"].width = 108

    # ---------------------------------------------------------------- Inputs
    ws = wb.create_sheet("Inputs")
    r = write_table(ws, revb.reset_index().rename(columns={"quarter": "quarter"}),
                    1, "Revenue path, USD m (bridge v3 / WS06 v2b, 06_revenue_path_3q26_4q27_v2b.csv)")
    params = pd.DataFrame([
        ("3Q25 adj EBITDA margin (the 'down slightly' ceiling)", 50.085470, "%", "harness targets.csv"),
        ("1H26 actual revenue", 6286.0, "USD m", "WS02 panel / targets.csv"),
        ("1H26 actual adj EBITDA", 1780.0, "USD m", "WS02 panel / targets.csv"),
        ("FY26 management margin floor (2Q26 letter)", 35.5, "%", "guides_margin.csv id ...FY2026-190"),
        ("Forecast 5 Nov FY26 sentence (floor + 50bp)", 36.0, "%", "M3 November rule, exact 2 of 2"),
        ("Combination shrinkage lambda", 0.5, "ratio", "prereg.json, fixed a priori"),
        ("k on total cash costs (revenue elasticity)", 0.364173, "elasticity", "M6 k_table 1Q22+ rw lag0, t 6.58"),
        ("k cost of revenue", 0.561589, "elasticity", "M6, t 5.61; the only line significant vs drift"),
        ("k operations & support", 0.438174, "elasticity", "M6, t 3.43"),
        ("k product development", -0.210634, "elasticity", "M6, t -1.59, NOT significant"),
        ("k sales & marketing", 0.418480, "elasticity", "M6, t 2.25, unstable"),
        ("k G&A", -0.110228, "elasticity", "M6, t -0.29, NOT significant"),
        ("ABNB total opex elasticity to revenue", 0.139141, "elasticity", "M6 peer table, t 0.47 (ns)"),
        ("BKNG / TRIP / EXPE total opex elasticity", 0.608, "elasticity", "M6 peer table (0.61 / 0.63 / 0.44)"),
        ("D&A per quarter", 20.633971, "USD m", "M7 parameter sheet, recency-weighted last 4"),
        ("Interest expense per quarter", 37.0, "USD m", "M7, 2Q26 10-Q printed"),
        ("Other income per quarter", 3.707412, "USD m", "M7, rw mean of last 8"),
        ("Interest income yield beta", 0.876498, "ratio to 3m T-bill", "M7, WS04 diagnostic"),
        ("3m T-bill spot (10 Sep 2026)", 3.86, "%", "FRED DTB3"),
        ("Effective tax rate FY26", 18.0, "%", "M7 / WS05 S157 'high teens'"),
        ("Effective tax rate FY27-28", 17.5, "%", "M7 / WS05 S148"),
        ("SBC y/y growth rule", 13.18, "%", "M7, rw mean of last 4 y/y"),
        ("Diluted share delta per quarter", -5.324187, "m shares", "M7, -buyback/price + issuance"),
        ("Capex per quarter", 8.929321, "USD m", "M7, rw last-4 mean"),
        ("EPS per $M of adj EBITDA", 0.001386, "USD/share per USD m", "(1 - ETR) / diluted shares"),
        ("Residual allocation weights (pd / sm / ga)", np.nan, "share", "PIT error variance 211 / 1721 / 315"),
    ], columns=["parameter", "value", "unit", "source"])
    r = write_table(ws, params, r, "Model parameters and their sources", widths={"source": 56, "parameter": 46})
    write_table(ws, bands, r, "Conformal bands (split conformal on the combination's own PIT errors)")

    # ---------------------------------------------------------------- Lines
    ws = wb.create_sheet("Lines")
    hist = lines[lines.scenario == "actual"].copy()
    keep = ["quarter", "revenue_musd", "cor_cash_musd", "ops_cash_musd", "pd_cash_musd",
            "sm_cash_musd", "ga_cash_musd", "total_cash_costs_musd", "adj_ebitda_musd",
            "adj_ebitda_margin_pct"]
    r = write_table(ws, hist[keep], 1, "History — actual cash cost lines ex-SBC, 1Q21-2Q26 (WS02 panel)")
    fc = lines[lines.scenario != "actual"].copy()
    keep2 = ["quarter", "scenario", "revenue_musd", "cor_cash_musd", "ops_cash_musd", "pd_cash_musd",
             "sm_cash_musd", "ga_cash_musd", "other_net_musd", "residual_allocated_musd",
             "total_cash_costs_musd", "adj_ebitda_musd", "adj_ebitda_margin_pct"]
    keep2 = [c for c in keep2 if c in fc.columns]
    r = write_table(ws, fc[keep2], r,
                    "Forecast — M1 driver lines reconciled to the adopted adj EBITDA; "
                    "the residual is allocated to pd / sm / ga in proportion to their PIT error variance")
    write_table(ws, fc[["quarter", "scenario"] + [c for c in fc.columns if c.endswith("_pct_rev")]],
                r, "Forecast lines as a percentage of revenue")

    # ---------------------------------------------------------------- Bridge
    ws = wb.create_sheet("Bridge")
    base = pl[pl.scenario == "base"].set_index("quarter").reindex(QF).reset_index()
    hdr = ["line"] + QF
    ws.cell(row=1, column=1, value="Quarterly bridge, base case — adj EBITDA to EPS "
                                   "(formula cells: op income, pretax, net income, EPS, margins)").font = SUB
    ws.cell(row=1, column=1).fill = SUBFILL
    for j, h in enumerate(hdr, start=1):
        c = ws.cell(row=2, column=j, value=h)
        c.font = HDR
        c.fill = HDRFILL
    rowmap = [
        ("Revenue", "revenue_musd", None),
        ("Cost of revenue", "cor_cash_musd", None),
        ("Operations & support", "ops_cash_musd", None),
        ("Product development", "pd_cash_musd", None),
        ("Sales & marketing", "sm_cash_musd", None),
        ("G&A ex reserves", "ga_cash_musd", None),
        ("Total cash costs", "total_cash_costs_musd", None),
        ("Adj EBITDA", "adj_ebitda_musd", None),
        ("Adj EBITDA margin %", None, "ebitda_margin"),
        ("  80% band low %", "margin_q10", None),
        ("  80% band high %", "margin_q90", None),
        ("Stock-based compensation", "sbc_musd", None),
        ("Depreciation & amortisation", "da_musd", None),
        ("GAAP operating income", None, "op"),
        ("GAAP operating margin %", None, "opm"),
        ("Interest income", "interest_income_musd", None),
        ("Interest expense", "interest_expense_musd", None),
        ("Other income", "other_income_musd", None),
        ("Pretax income", None, "pretax"),
        ("Effective tax rate %", "tax_rate_pct", None),
        ("Tax provision", None, "tax"),
        ("Net income", None, "ni"),
        ("Diluted shares (m)", "diluted_shares_m", None),
        ("EPS, diluted (GAAP = Street definition)", None, "eps"),
        ("  EPS 80% band low", "eps_q10", None),
        ("  EPS 80% band high", "eps_q90", None),
        ("Capex", "capex_musd", None),
        ("CFO (DIAGNOSTIC — quarterly FCF failed its backtest)", "cfo_musd_diagnostic", None),
        ("FCF (DIAGNOSTIC — do not quote quarterly)", "fcf_musd_diagnostic", None),
    ]
    ridx = {label: 3 + i for i, (label, _c, _f) in enumerate(rowmap)}
    for i, (label, col, formula) in enumerate(rowmap):
        rr = 3 + i
        ws.cell(row=rr, column=1, value=label)
        for j, q in enumerate(QF, start=2):
            L = get_column_letter(j)
            v = None
            if col is not None:
                v = float(base.loc[base.quarter == q, col].iloc[0]) if col in base.columns else None
                ws.cell(row=rr, column=j, value=v).number_format = "#,##0.00"
            else:
                f = {
                    "ebitda_margin": f"={L}{ridx['Adj EBITDA']}/{L}{ridx['Revenue']}*100",
                    "op": f"={L}{ridx['Adj EBITDA']}-{L}{ridx['Depreciation & amortisation']}-{L}{ridx['Stock-based compensation']}",
                    "opm": f"={L}{ridx['GAAP operating income']}/{L}{ridx['Revenue']}*100",
                    "pretax": f"={L}{ridx['GAAP operating income']}+{L}{ridx['Interest income']}-{L}{ridx['Interest expense']}+{L}{ridx['Other income']}",
                    "tax": f"={L}{ridx['Pretax income']}*{L}{ridx['Effective tax rate %']}/100",
                    "ni": f"={L}{ridx['Pretax income']}-{L}{ridx['Tax provision']}",
                    "eps": f"={L}{ridx['Net income']}/{L}{ridx['Diluted shares (m)']}",
                }[formula]
                ws.cell(row=rr, column=j, value=f).number_format = "#,##0.00"
    ws.column_dimensions["A"].width = 46
    for j in range(2, len(hdr) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 14
    r = 3 + len(rowmap) + 2
    r = write_table(ws, ann, r, "Annual forecast — FY26 / FY27 / FY28, three revenue scenarios "
                                "(FY26 = 1H26 actual + 3Q26 combination + 4Q26 Street)")

    # ---------------------------------------------------------------- Scenarios
    ws = wb.create_sheet("Scenarios")
    r = write_table(ws, scen, 1, "Revenue scenario x cost response. k = M6's fitted elasticity of "
                                 "total cash costs to revenue (0.364); 'held' = costs do not move; "
                                 "'full_flex' = costs move one-for-one (not observed at ABNB)")
    r = write_table(ws, macro, r, "Macro sensitivity: margin change per 1 percentage point of revenue shortfall")
    write_table(ws, floor, r, "FY26 'at least 35.5%' floor — how large a 2H26 revenue shortfall it survives")

    # ---------------------------------------------------------------- Consensus
    ws = wb.create_sheet("Consensus")
    r = write_table(ws, cons, 1, "Model vs consensus. LSEG pull 2026-09-11 (WS03); "
                                 "Bloomberg BEST pull 2026-09-05")
    other = pd.DataFrame([
        ("Management, 3Q26", "margin down slightly vs 3Q25 (50.085%)", "2Q26 letter 6 Aug 2026"),
        ("Management, FY26", "adj EBITDA margin at least 35.5%", "2Q26 letter 6 Aug 2026"),
        ("WS30 margin walk, 3Q26 / 4Q26", "50.80% / 29.70%", "research/notes/overnight/30_margin-walk.md"),
        ("WS31b base profile, 3Q26 / 4Q26", "51.30% / 24.65%", "31b_operating-profile.md — 4Q26 is 3-4pp "
                                                               "below every method and the Street; NOT carried"),
        ("WS31b management profile, 3Q26 / 4Q26", "52.15% / 25.93%", "same — NOT carried"),
        ("WS07 lever model", "cost lines per night", "research/notes/overnight/07_ops-and-margin-levers.md"),
    ], columns=["prior team number", "value", "source / status"])
    write_table(ws, other, r, "Prior team numbers, and which are carried")

    # ---------------------------------------------------------------- Seasonality
    ws = wb.create_sheet("Seasonality")
    write_table(ws, seas, 1, "Quarterly seasonal profile with the mechanical (cost of revenue + "
                             "operations & support) vs discretionary (product dev + S&M + G&A) split")

    # ---------------------------------------------------------------- Weights
    ws = wb.create_sheet("Weights")
    lw = live[live.spec_id == "stack_clip"]
    wcols = ["target", "quarter", "point", "raw_point", "clip", "weight_source"] + \
            [c for c in lw.columns if c.startswith("w__") or c.startswith("p__")]
    r = write_table(ws, lw[wcols], 1, "LIVE member weights and points, vintage 2026-09-11")
    hw = wts[(wts.target == "adj_ebitda_margin_pct") & (wts.window == "W1") & (wts.horizon_q == 0)] \
        .pivot_table(index="quarter", columns="member", values="weight").reset_index()
    r = write_table(ws, hw, r, "Backtest weights by vintage (leave-future-out, W1, h=0, margin)")
    s0 = sc23[(sc23.prior_basis == "PIT") & (sc23.spec_id == "stack_clip")]
    keepc = [c for c in ["target", "window", "horizon_q", "n", "mae", "rw_mae", "rmse", "bias",
                         "mae_ratio_seasonal_naive", "rw_mae_ratio_seasonal_naive",
                         "mae_ratio_seasonal_naive_drift", "mae_ratio_street", "rw_mae_ratio_street",
                         "t_nw1_seasonal_naive", "p_nw1_seasonal_naive", "k_better_seasonal_naive",
                         "n_cmp_seasonal_naive", "p_sign_seasonal_naive", "p_sign_street",
                         "cov80", "cov90", "n_clipped"] if c in s0.columns]
    r = write_table(ws, s0[keepc], r, "Backtest scoreboard of the combination (PIT, spec stack_clip)")
    r = write_table(ws, dmem, r, "Each member's own PIT MAE on the same matched quarters")
    write_table(ws, diag, r, "Leave-one-member-out and the no-clip / Street-independent variants")

    # ---------------------------------------------------------------- Card
    ws = wb.create_sheet("Card")
    r = write_table(ws, card, 1, "The 5 November 2026 card", widths={"note": 70, "item": 42, "vs": 28})
    r = write_table(ws, path, r, "Which object supplies which quarter, and why",
                    widths={"rationale": 70, "source": 46})
    write_table(ws, bi, r, "M3 budget identity: the FY sentence, the Q3 pin and the 4Q26 residual")

    wb.save(XLSX)
    print(f"wrote {XLSX} ({XLSX.stat().st_size / 1024:.0f} KB), sheets: {wb.sheetnames}")


if __name__ == "__main__":
    main()
