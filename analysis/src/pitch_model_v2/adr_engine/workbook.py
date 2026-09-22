"""adr_engine / workbook.py — line 2 of the official model: the ADR engine cell by cell, one sheet after Nights_Engine,
and rows 8–11 of Income_Statement (GBV, ADR) wired to it. The nights workbook builder (frozen file) is executed unchanged
and its Workbook object captured before it saves, so the nights sheets and charts are preserved; nothing under
analysis/src/forecast_methods/ is modified. Blue = input with source; black = formula; green = link.
Run: PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.workbook"""
from __future__ import annotations
import importlib.util, json, sys
import numpy as np
import pandas as pd
import openpyxl.workbook.workbook as OW
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
from openpyxl.chart import LineChart, Reference
from . import config as C, fx_data as F, exfx as M

RAUSCH, INK = "FF385C", "222222"
F_HDR = Font(name="Arial", bold=True, color="FFFFFF", size=10); FILL_HDR = PatternFill("solid", fgColor=RAUSCH)
F_SEC = Font(name="Arial", bold=True, color="FFFFFF", size=10); FILL_SEC = PatternFill("solid", fgColor=INK)
F_IN = Font(name="Arial", color="0000FF", size=10); F_FX = Font(name="Arial", color="000000", size=10)
F_LINK = Font(name="Arial", color="008000", size=10); F_LBL = Font(name="Arial", size=10); F_NOTE = Font(name="Arial", italic=True, color="666666", size=9)
F_BOLD = Font(name="Arial", bold=True, size=10); FILL_KEY = PatternFill("solid", fgColor="FFE1E7")
PCT2, NUM2, NUM3, NUM4, NUM6 = "0.00%", "0.00", "0.000", "0.0000", "0.000000"
Q = [f"{q}Q{y}" for y in range(21, 28) for q in range(1, 5)]      # 1Q21..4Q27, same as Nights_Engine
COL0 = 3; col = {lab: COL0 + i for i, lab in enumerate(Q)}
IS_Q = [f"{q}Q{y}" for y in range(23, 28) for q in range(1, 5)]   # Income_Statement columns C..V = 1Q23..4Q27
is_col = {lab: 3 + i for i, lab in enumerate(IS_Q)}
HIST_LAST = "2Q26"; FIRST_TARGET = "2Q22"
CCY_LABEL = {"EUR": "DEXUSEU", "GBP": "DEXUSUK", "BRL": "DEXBZUS", "MXN": "DEXMXUS", "JPY": "DEXJPUS", "AUD": "DEXUSAL", "KRW": "DEXKOUS", "CAD": "DEXCAUS", "INR": "DEXINUS"}


def A(lab, r): return f"{L(col[lab])}{r}"
def put(ws, r, c, v, font=F_FX, fmt=None, fill=None):
    cell = ws.cell(r, c, v); cell.font = font
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    return cell
def hdr(ws, r, text, cols):
    for c in range(1, cols + 1): ws.cell(r, c).fill = FILL_HDR; ws.cell(r, c).font = F_HDR
    ws.cell(r, 1, text)
def sec(ws, r, text, cols):
    for c in range(1, cols + 1): ws.cell(r, c).fill = FILL_SEC; ws.cell(r, c).font = F_SEC
    ws.cell(r, 1, text)
def label(ws, r, text, note=None):
    put(ws, r, 1, text, F_LBL)
    if note: put(ws, r, 2, note, F_NOTE)
def is_hist(lab): return C.qlabel_to_period(lab) <= C.qlabel_to_period(HIST_LAST)
def qi(lab): return Q.index(lab)


def capture_nights_workbook():
    """Run the frozen nights builder and capture its Workbook before it saves."""
    path = C.ROOT / "analysis/src/forecast_methods/reviews_index_v2/workbook.py"
    spec = importlib.util.spec_from_file_location("nights_workbook", path); mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent)); spec.loader.exec_module(mod)
    cap = {}; orig = OW.Workbook.save
    def _cap(self, filename): cap["wb"] = self
    OW.Workbook.save = _cap
    try: _, refs = mod.build()
    finally: OW.Workbook.save = orig
    return cap["wb"], refs


def build():
    wb, nrefs = capture_nights_workbook()
    daily = F.load_daily(); shares = F.gbv_shares(); pdts = F.print_dates(); tg = F.disclosed_targets()
    kpi = pd.read_csv(C.KPI_PANEL).set_index("quarter")
    fc = pd.read_csv(C.OUT / "fx_forecast_asof.csv"); fc = fc[fc["asof"] == "2026-09-21"].set_index("quarter")
    sc = pd.read_csv(C.OUT / "fx_scores.csv"); post = pd.read_csv(C.OUT / "fx_weights_posterior.csv").set_index("region")
    hist = M.history(); fwd = M.forward(); bund = M.bundle_schedule(); rg = M.regional_growth_forward(); rb = M.regional_base(); gmf = M.geo_mix_forward()
    env = pd.read_csv(C.OUT / "exfx_envelope.csv").set_index("quarter"); path = pd.read_csv(C.OUT / "adr_path.csv").set_index("quarter")
    scen = pd.read_csv(C.OUT / "adr_scenarios.csv")

    ws = wb.create_sheet("ADR_Engine", index=wb.sheetnames.index("Nights_Engine") + 1)
    ws.column_dimensions["A"].width = 50; ws.column_dimensions["B"].width = 40
    for lab in Q: ws.column_dimensions[L(col[lab])].width = 9.5
    ncols = COL0 + len(Q) - 1
    hdr(ws, 1, "Airbnb — ADR engine (line 2). reported ADR y/y = ex-FX mechanism + FX translation identity (ex ante, spot held). Blue = input with source; black = formula; green = link.", ncols)
    put(ws, 2, 1, "Engine: analysis/src/pitch_model_v2/adr_engine (python3 -m pitch_model_v2.adr_engine.run); pre-registration docs/pitch-model-v2/lines/adr_fx_prereg.md; design adr_v1_design.md; rationale final_adr.md. FX through FRED 2026-09-18; forward quarters hold the last print (spot held).", F_NOTE)
    r = 4; sec(ws, r, "Quarter", ncols); put(ws, r, 2, "A = printed, E = engine", F_NOTE)
    for lab in Q: put(ws, r, col[lab], lab + ("A" if is_hist(lab) else "E"), F_HDR, fill=FILL_HDR).alignment = Alignment(horizontal="center")

    # ---------------- A. printed ADR and the disclosed identity ----------------
    r = 6; sec(ws, r, "A. Printed ADR and the disclosed identity: reported y/y − ex-FX y/y = FX effect (closes to ≤0.04pp)", ncols)
    R_ADR, R_YOY, R_EXFX, R_FXD = 7, 8, 9, 10
    label(ws, R_ADR, "ADR ($, GBV ÷ nights, printed; forward = engine path)", "data/processed/overnight/02_kpi_panel_quarterly.csv adr_usd (letters / 10-Q)")
    label(ws, R_YOY, "    reported y/y", "→ ADR / ADR four quarters earlier − 1")
    label(ws, R_EXFX, "    ex-FX y/y, as stated in the letter (whole points; 3Q23/4Q23 'less than 1%' → 0.5)", "02_kpi_panel_quarterly.csv adr_yoy_exfx_pct; 2Q22 onward")
    label(ws, R_FXD, "    FX effect on ADR (pp) — the disclosed target", "→ reported y/y × 100 − ex-FX y/y")
    for lab in Q:
        c = col[lab]
        if is_hist(lab): put(ws, R_ADR, c, float(kpi.loc[lab, "adr_usd"]), F_IN, NUM2)
        if qi(lab) >= 4: put(ws, R_YOY, c, f"={A(lab, R_ADR)}/{A(Q[qi(lab)-4], R_ADR)}-1", F_FX, PCT2)
        if is_hist(lab) and C.qlabel_to_period(lab) >= C.qlabel_to_period(FIRST_TARGET):
            put(ws, R_EXFX, c, float(kpi.loc[lab, "adr_yoy_exfx_pct"]), F_IN, NUM2)
            put(ws, R_FXD, c, f"={A(lab, R_YOY)}*100-{A(lab, R_EXFX)}", F_FX, NUM2)

    # ---------------- B. FX translation identity ----------------
    r = 12; sec(ws, r, "B. FX translation identity (ex ante): FX pp = Σ_region GBV share × Σ_currency κ × (avg rate / avg rate a year earlier − 1) — zero fitted parameters", ncols)
    R_CCY0 = 13
    for i, ccy in enumerate(C.CCYS):
        label(ws, R_CCY0 + i, f"Quarterly average USD per {ccy} (business days; forward = spot held from 2026-09-18)", f"FRED {CCY_LABEL[ccy]} → adr_engine/fx_daily_2026-09-21.csv (fetch_fx.py)")
    R_OBS = R_CCY0 + len(C.CCYS)
    label(ws, R_OBS, "    share of the quarter's business days printed at 18 Sep 2026", "engine fx_forecast_asof.csv obs_frac_at_asof")
    for lab in Q:
        avg, f = F.quarter_avg(daily, lab, None)
        for i, ccy in enumerate(C.CCYS): put(ws, R_CCY0 + i, col[lab], float(avg[ccy]), F_IN, NUM6)
        put(ws, R_OBS, col[lab], float(f), F_IN, NUM3)
    R_YY0 = R_OBS + 2
    for i, ccy in enumerate(C.CCYS):
        label(ws, R_YY0 + i, f"    {ccy} y/y of the quarterly average (%)", "→ (avg / avg four quarters earlier − 1) × 100")
        for lab in Q:
            if qi(lab) >= 4: put(ws, R_YY0 + i, col[lab], f"=({A(lab, R_CCY0+i)}/{A(Q[qi(lab)-4], R_CCY0+i)}-1)*100", F_FX, NUM3)
    R_KAP = R_YY0 + len(C.CCYS) + 1
    label(ws, R_KAP, "Destination-currency basket weights κ (frozen judgement, 01b_basket_weights_used.csv; USD legs carry 0)", "rows = region; columns C..K = EUR GBP BRL MXN JPY AUD KRW CAD INR; L = USD")
    for j, ccy in enumerate(C.CCYS + ["USD"]): put(ws, R_KAP, COL0 + j, ccy, F_BOLD)
    for i, reg in enumerate(C.REGIONS):
        label(ws, R_KAP + 1 + i, f"    κ {reg}")
        for j, ccy in enumerate(C.CCYS + ["USD"]): put(ws, R_KAP + 1 + i, COL0 + j, float(C.KAPPA[reg].get(ccy, 0.0)), F_IN, NUM3)
    R_BSK0 = R_KAP + 6
    for i, reg in enumerate(C.REGIONS):
        label(ws, R_BSK0 + i, f"    basket y/y, {reg} (%)", "→ Σ_currency κ × currency y/y")
        for lab in Q:
            if qi(lab) >= 4:
                terms = "+".join(f"${L(COL0+j)}${R_KAP+1+i}*{A(lab, R_YY0+j)}" for j, ccy in enumerate(C.CCYS) if C.KAPPA[reg].get(ccy, 0.0) > 0)
                put(ws, R_BSK0 + i, col[lab], f"={terms}", F_FX, NUM3)
    R_SH0 = R_BSK0 + 5
    label(ws, R_SH0 - 1, "Regional GBV shares (10-K Geographic Mix, latest fiscal year filed before the quarter's print; FY2025 forward)", "data/processed/adr/01_regional_annual.csv gbv_share_pct")
    R_FY = R_SH0 + 4
    for i, reg in enumerate(C.REGIONS): label(ws, R_SH0 + i, f"    GBV share, {reg}")
    label(ws, R_FY, "    fiscal year of the shares used")
    for lab in Q:
        info = pdts[lab] if lab in pdts.index and is_hist(lab) else None
        g, fy = F.shares_at(shares, info)
        for i, reg in enumerate(C.REGIONS): put(ws, R_SH0 + i, col[lab], float(g[reg]), F_IN, NUM4)
        put(ws, R_FY, col[lab], int(fy), F_IN)
    R_FXI = R_FY + 2
    label(ws, R_FXI, "FX effect on ADR — translation identity (pp)", "→ SUMPRODUCT(GBV shares, regional basket y/y); the promoted leg (pre-registration §5, V0)")
    R_ERR, R_NERR = R_FXI + 1, R_FXI + 2
    label(ws, R_ERR, "    error: identity − disclosed (pp), completed quarters", "→ identity − row 10")
    label(ws, R_NERR, "    naive error: last quarter's disclosed − disclosed (pp)")
    for lab in Q:
        if qi(lab) >= 4:
            put(ws, R_FXI, col[lab], f"=SUMPRODUCT({A(lab, R_SH0)}:{A(lab, R_SH0+3)},{A(lab, R_BSK0)}:{A(lab, R_BSK0+3)})", F_FX, NUM3, FILL_KEY if not is_hist(lab) else None)
        if is_hist(lab) and C.qlabel_to_period(lab) >= C.qlabel_to_period("3Q22"):
            put(ws, R_ERR, col[lab], f"={A(lab, R_FXI)}-{A(lab, R_FXD)}", F_FX, NUM3)
            put(ws, R_NERR, col[lab], f"={A(Q[qi(lab)-1], R_FXD)}-{A(lab, R_FXD)}", F_FX, NUM3)
    R_RMSE = R_NERR + 1
    label(ws, R_RMSE, "    RMSE identity / RMSE naive, 1Q23–2Q26 (n 14; full-quarter rates = origin O3)", "→ SQRT(SUMSQ)/n; point-in-time O1/O2 ratios are in block E")
    put(ws, R_RMSE, COL0, f"=SQRT(SUMSQ({A('1Q23', R_ERR)}:{A('2Q26', R_ERR)})/14)", F_FX, NUM3)
    put(ws, R_RMSE, COL0 + 1, f"=SQRT(SUMSQ({A('1Q23', R_NERR)}:{A('2Q26', R_NERR)})/14)", F_FX, NUM3)
    put(ws, R_RMSE, COL0 + 2, f"={L(COL0)}{R_RMSE}/{L(COL0+1)}{R_RMSE}", F_FX, NUM3, FILL_KEY); put(ws, R_RMSE, COL0 + 3, "ratio (pass line ≤ 0.75)", F_NOTE)
    R_P10, R_P50, R_P90 = R_RMSE + 2, R_RMSE + 3, R_RMSE + 4
    label(ws, R_P10, "    P10 of the ex-ante band (pp)", "engine: moving-block bootstrap of daily FX returns on the unobserved days, 4,000 paths")
    label(ws, R_P50, "    P50"); label(ws, R_P90, "    P90")
    for lab in C.FORWARD_QUARTERS:
        put(ws, R_P10, col[lab], float(fc.loc[lab, "p10"]), F_IN, NUM2); put(ws, R_P50, col[lab], float(fc.loc[lab, "p50"]), F_IN, NUM2); put(ws, R_P90, col[lab], float(fc.loc[lab, "p90"]), F_IN, NUM2)

    # ---------------- C. ex-FX mechanism ----------------
    r = R_P90 + 2; sec(ws, r, "C. Ex-FX ADR mechanism: ex-FX y/y = core + bundle (laps on filed dates) + geo mix (from the nights line) + unit size + LOS + seats + interaction", ncols)
    R_DEX = r + 1; R_GEO, R_UNIT, R_LOS, R_SEAT, R_INT = r + 2, r + 3, r + 4, r + 5, r + 6
    R_RES, R_CORE = r + 7, r + 8; R_L1, R_L2, R_L3, R_BUN = r + 10, r + 11, r + 12, r + 13; R_EXM = r + 15
    label(ws, R_DEX, "Disclosed ex-FX ADR y/y (pp)", "→ link to row 9")
    label(ws, R_GEO, "    geographic mix (pp)", "history: H decomposition adr_history_components.csv; forward: block C1 arithmetic on the nights line's regional path")
    label(ws, R_UNIT, "    unit size / party size (pp)", "history: H; forward: card v3 measured 3Q26 term +0.797 carried (I_mix_terms_3q26.csv)")
    label(ws, R_LOS, "    length-of-stay mix (pp)", "history: H; forward: card +0.056 carried")
    label(ws, R_SEAT, "    seats / new business dilution (pp)", "history: H 15_seats_dilution; forward: −0.483 (2026), −0.565 (2027), assumed")
    label(ws, R_INT, "    interaction (pp)", "H, descriptive −0.10")
    label(ws, R_RES, "    like-for-like residual (pp) = ex-FX − the five terms above", "history: formula; forward: core + bundle")
    label(ws, R_CORE, "    core (pp) = residual − bundle live in the quarter", "history: formula; forward: carried at the last observed value (2Q26) — the same carry rule the card applies to the residual")
    label(ws, R_L1, "    bundle leg: RNPL North America (larger-home mix), live 3Q25–2Q26, laps 3Q26", "ledger D014/D032 (~1pp bundle ADR, transcript-only) split by K4 residual steps 0.92:0.88")
    label(ws, R_L2, "    bundle leg: cancellation redesign + single fee, live 4Q25–3Q26 (global), laps 4Q26", "same sizing; dates ledger D012/D013/D024/D060")
    label(ws, R_L3, "    bundle leg: RNPL ex-NA (live 17 Feb 2026), base 0.0 (unsized by management); high 1.15", "alternative in block F")
    label(ws, R_BUN, "    bundle live (pp)", "→ sum of the three legs")
    label(ws, R_EXM, "EX-FX ADR y/y — mechanism (pp)", "→ core + bundle + geo + unit + LOS + seats + interaction; history = disclosed")
    for lab in Q:
        c = col[lab]
        if is_hist(lab) and lab in hist.index:
            h = hist.loc[lab]
            put(ws, R_DEX, c, f"={A(lab, R_EXFX)}", F_LINK, NUM2)
            put(ws, R_GEO, c, float(h.geo_mix), F_IN, NUM3); put(ws, R_UNIT, c, float(h.unit_size), F_IN, NUM3); put(ws, R_LOS, c, float(h.los_mix), F_IN, NUM3)
            put(ws, R_SEAT, c, float(h.seats), F_IN, NUM3); put(ws, R_INT, c, float(h.interaction), F_IN, NUM3)
            put(ws, R_RES, c, f"={A(lab, R_DEX)}-SUM({A(lab, R_GEO)}:{A(lab, R_INT)})", F_FX, NUM3)
            put(ws, R_CORE, c, f"={A(lab, R_RES)}-{A(lab, R_BUN)}", F_FX, NUM3)
            put(ws, R_EXM, c, f"={A(lab, R_DEX)}", F_LINK, NUM3)
        if lab in bund.index:
            put(ws, R_L1, c, float(bund.loc[lab, "rnpl_na_leg"]), F_IN, NUM3); put(ws, R_L2, c, float(bund.loc[lab, "fee_cancel_leg"]), F_IN, NUM3); put(ws, R_L3, c, float(bund.loc[lab, "rnpl_exna_leg"]), F_IN, NUM3)
            put(ws, R_BUN, c, f"=SUM({A(lab, R_L1)}:{A(lab, R_L3)})", F_FX, NUM3)
    # C1 regional block for the forward geo mix
    R_C1 = R_EXM + 2; label(ws, R_C1, "C1. Geo-mix arithmetic for the forward quarters: regional nights growth from the nights line (nights_v2_design.md §2.1), base-quarter shares and regional ADR levels held", "regional_growth_forward.csv; 04_regional_quarterly_wide.csv (disclosed-chained)")
    R_G0, R_S0, R_A0 = R_C1 + 1, R_C1 + 5, R_C1 + 9; R_GT, R_GM = R_C1 + 13, R_C1 + 14
    for i, reg in enumerate(C.REGIONS):
        label(ws, R_G0 + i, f"    nights growth, {reg} (%)", "NA = nights line; ex-NA = 2Q26 bucket pattern (EMEA 8 / LatAm 20 / APAC 18) scaled to the line's ex-NA rate")
        label(ws, R_S0 + i, f"    base-quarter nights share, {reg}"); label(ws, R_A0 + i, f"    base-quarter regional ADR ($, anchored)")
    label(ws, R_GT, "    total nights growth (%)", "→ SUMPRODUCT(shares, growth)")
    label(ws, R_GM, "    geo mix (pp)", "→ (Σ share×(1+g)×ADR) / ((1+g_tot) × Σ share×ADR) − 1, ×100")
    adr_levels = None
    for lab in C.FORWARD_QUARTERS:
        c = col[lab]; row = rg.loc[lab]
        if row.base_quarter in rb.index: adr_levels = {reg: float(rb.loc[row.base_quarter, f"adr_{reg}"]) for reg in C.REGIONS}
        for i, reg in enumerate(C.REGIONS):
            put(ws, R_G0 + i, c, float(row[f"g_{reg}"]), F_IN, NUM3); put(ws, R_S0 + i, c, float(row[f"share_{reg}"]), F_IN, NUM4); put(ws, R_A0 + i, c, adr_levels[reg], F_IN, NUM2)
        put(ws, R_GT, c, f"=SUMPRODUCT({A(lab, R_S0)}:{A(lab, R_S0+3)},{A(lab, R_G0)}:{A(lab, R_G0+3)})", F_FX, NUM3)
        put(ws, R_GM, c, f"=(SUMPRODUCT({A(lab, R_S0)}:{A(lab, R_S0+3)},1+{A(lab, R_G0)}:{A(lab, R_G0+3)}/100,{A(lab, R_A0)}:{A(lab, R_A0+3)})/((1+{A(lab, R_GT)}/100)*SUMPRODUCT({A(lab, R_S0)}:{A(lab, R_S0+3)},{A(lab, R_A0)}:{A(lab, R_A0+3)}))-1)*100", F_FX, NUM3)
        # forward mechanism rows
        put(ws, R_GEO, c, f"={A(lab, R_GM)}", F_LINK, NUM3); put(ws, R_UNIT, c, M.CARD_TERMS["unit_size"], F_IN, NUM3); put(ws, R_LOS, c, M.CARD_TERMS["los_mix"], F_IN, NUM3)
        put(ws, R_SEAT, c, M.CARD_TERMS["seats_2026"] if lab.endswith("26") else M.CARD_TERMS["seats_2027"], F_IN, NUM3); put(ws, R_INT, c, M.CARD_TERMS["interaction"], F_IN, NUM3)
        put(ws, R_CORE, c, f"={A(HIST_LAST, R_CORE)}", F_FX, NUM3); put(ws, R_RES, c, f"={A(lab, R_CORE)}+{A(lab, R_BUN)}", F_FX, NUM3)
        put(ws, R_EXM, c, f"={A(lab, R_CORE)}+{A(lab, R_BUN)}+SUM({A(lab, R_GEO)}:{A(lab, R_INT)})", F_FX, NUM3, FILL_KEY)

    # ---------------- D. reported ADR path ----------------
    r = R_GM + 2; sec(ws, r, "D. Reported ADR path — ADR = year-ago ADR × (1 + (ex-FX mechanism + FX identity) / 100); band; the Street; GBV on the nights line", ncols)
    R_FXP, R_REP, R_LVL, R_BH, R_LO, R_HI, R_ST, R_STY, R_Z, R_PGE, R_NTS, R_GBV = [r + k for k in range(1, 13)]
    label(ws, R_FXP, "    FX effect on ADR (pp)", "→ block B identity"); label(ws, R_REP, "    reported ADR y/y (%)", "→ ex-FX mechanism + FX")
    label(ws, R_LVL, "ADR ($) — the line", "→ year-ago ADR × (1 + y/y/100)"); label(ws, R_BH, "    band half-width (pp)", "engine exfx_envelope.csv: RSS of parameter half-ranges ⊕ FX bootstrap sd")
    label(ws, R_LO, "    ADR low ($)"); label(ws, R_HI, "    ADR high ($)")
    label(ws, R_ST, "    Street ADR ($)", "Bloomberg MODL screenshot 12 Sep 2026 (Krish): 3Q26 177.06 n 26 (173.71–179.12), 4Q26 171.33 n 25; no FY row exists")
    label(ws, R_STY, "    Street implied y/y (%)"); label(ws, R_Z, "    z: (ours − Street) / band"); label(ws, R_PGE, "    P(print ≥ Street)", "→ 1 − NORM.S.DIST((Street y/y − ours)/band, TRUE)")
    label(ws, R_NTS, "    nights (m) — line 1", "→ Income_Statement row 5 (nights line)"); label(ws, R_GBV, "    GBV ($bn) = nights × ADR", "cross-check only; the take-rate line is built next")
    for lab in C.FORWARD_QUARTERS:
        c = col[lab]; base = Q[qi(lab) - 4]
        put(ws, R_FXP, c, f"={A(lab, R_FXI)}", F_LINK, NUM3); put(ws, R_REP, c, f"={A(lab, R_EXM)}+{A(lab, R_FXP)}", F_FX, NUM3)
        put(ws, R_LVL, c, f"={A(base, R_ADR)}*(1+{A(lab, R_REP)}/100)", F_FX, NUM2, FILL_KEY); put(ws, R_ADR, c, f"={A(lab, R_LVL)}", F_LINK, NUM2)
        put(ws, R_BH, c, float(env.loc[lab, "reported_half_band_pp"]), F_IN, NUM3)
        put(ws, R_LO, c, f"={A(base, R_ADR)}*(1+({A(lab, R_REP)}-{A(lab, R_BH)})/100)", F_FX, NUM2); put(ws, R_HI, c, f"={A(base, R_ADR)}*(1+({A(lab, R_REP)}+{A(lab, R_BH)})/100)", F_FX, NUM2)
        if lab in C.STREET_ADR:
            put(ws, R_ST, c, C.STREET_ADR[lab][0], F_IN, NUM2); put(ws, R_STY, c, f"=({A(lab, R_ST)}/{A(base, R_ADR)}-1)*100", F_FX, NUM3)
            put(ws, R_Z, c, f"=({A(lab, R_REP)}-{A(lab, R_STY)})/{A(lab, R_BH)}", F_FX, NUM3); put(ws, R_PGE, c, f"=1-NORM.S.DIST(({A(lab, R_STY)}-{A(lab, R_REP)})/{A(lab, R_BH)},TRUE)", F_FX, PCT2)
        put(ws, R_NTS, c, f"=Income_Statement!{L(is_col[lab])}5", F_LINK, NUM2); put(ws, R_GBV, c, f"={A(lab, R_NTS)}*{A(lab, R_LVL)}/1000", F_FX, NUM3)
    for lab in Q:
        if is_hist(lab) and lab in IS_Q:
            put(ws, R_NTS, col[lab], f"=Income_Statement!{L(is_col[lab])}5", F_LINK, NUM2); put(ws, R_GBV, col[lab], f"={A(lab, R_NTS)}*{A(lab, R_ADR)}/1000", F_FX, NUM3)

    # ---------------- E. engine reference values ----------------
    r = R_GBV + 2; sec(ws, r, "E. Engine reference values (Python) — for tie-out after an Excel recalculation", ncols); R_REF = r + 1
    rows = [("walk-forward RMSE ratio vs naive, V0 identity, W1 O1 / O2 / O3", [float(sc[(sc.variant=="V0_translation")&(sc.window=="W1")&(sc.origin==o)].ratio_vs_naive.iloc[0]) for o in C.ORIGINS]),
            ("… W2 O1 / O2 / O3 (pass line ≤ 0.75 at O2 and O3 on both windows)", [float(sc[(sc.variant=="V0_translation")&(sc.window=="W2")&(sc.origin==o)].ratio_vs_naive.iloc[0]) for o in C.ORIGINS]),
            ("V1 fitted pass-through, W1 O1 / O2 / O3", [float(sc[(sc.variant=="V1_passthrough")&(sc.window=="W1")&(sc.origin==o)].ratio_vs_naive.iloc[0]) for o in C.ORIGINS]),
            ("euro-only OLS (comparator), W1 O1 / O2 / O3", [float(sc[(sc.variant=="V2_eur_ols")&(sc.window=="W1")&(sc.origin==o)].ratio_vs_naive.iloc[0]) for o in C.ORIGINS]),
            ("posterior pass-through β (NA / EMEA / LatAm / APAC), prior N(1, 0.25²)", [float(post.loc[reg, "post_mean"]) for reg in C.REGIONS]),
            ("FX effect 3Q26 / 4Q26 / 1Q27 / 2Q27 (pp, spot held)", [float(fc.loc[q, "fx_pp_point_spot_held"]) for q in ["3Q26", "4Q26", "1Q27", "2Q27"]]),
            ("ADR $ 3Q26 / 4Q26 / 1Q27 / 2Q27 (engine)", [float(path.loc[q, "adr_usd"]) for q in ["3Q26", "4Q26", "1Q27", "2Q27"]]),
            ("ex-FX mechanism 3Q26 / 4Q26 / 1Q27 / 2Q27 (pp)", [float(fwd.loc[q, "exfx_yoy"]) for q in ["3Q26", "4Q26", "1Q27", "2Q27"]]),
            ("card v3 ADR $ 3Q26 / 4Q26 (DEC-0008, without K, midpoint FX −0.43 / +0.15)", [176.88, 173.94]),
            ("geo-mix method check: mean |bucket arithmetic − H| on 2Q24–2Q26 (pp)", [float(M.geo_mix_history_check().loc["2Q24":"2Q26"].diff_pp.abs().mean())])]
    for i, (lbl, vals) in enumerate(rows):
        label(ws, R_REF + i, lbl)
        for j, v in enumerate(vals): put(ws, R_REF + i, COL0 + j, v, F_IN, NUM3)

    # ---------------- F. alternatives ----------------
    r = R_REF + len(rows) + 1; sec(ws, r, "F. Alternatives carried beside the base (never blended): ex-FX rule → reported ADR $ at the same FX", ncols); R_ALT = r + 1
    put(ws, R_ALT, 1, "rule", F_BOLD); put(ws, R_ALT, 2, "quarter → ex-FX (pp) | ADR ($) | GBV ($bn)", F_NOTE)
    for j, q in enumerate(["3Q26", "4Q26", "1Q27", "2Q27"]): put(ws, R_ALT, COL0 + j * 3, q, F_BOLD)
    for i, (rule, g) in enumerate(scen.groupby("rule", sort=False)):
        label(ws, R_ALT + 1 + i, rule); g = g.set_index("quarter")
        for j, q in enumerate(["3Q26", "4Q26", "1Q27", "2Q27"]):
            put(ws, R_ALT + 1 + i, COL0 + j * 3, float(g.loc[q, "exfx_pct"]), F_IN, NUM2); put(ws, R_ALT + 1 + i, COL0 + j * 3 + 1, float(g.loc[q, "adr_usd"]), F_IN, NUM2); put(ws, R_ALT + 1 + i, COL0 + j * 3 + 2, float(g.loc[q, "gbv_busd"]), F_IN, NUM2)

    # ---------------- G. evidence: the v2 geo-mix layer and the four mitigations of 22 Sep ----------------
    R_EV = R_ALT + len(scen.rule.unique()) + 2
    sec(ws, R_EV, "G. Evidence behind line 2 \u2014 the v2 geo-mix layer and the four mitigations of 22 Sep. Labelled attribution and falsifiers; none of this is in the base path above.", ncols)
    def _csv(name):
        q = C.OUT / name
        return pd.read_csv(q) if q.exists() else None
    ev = []   # (label, [(sublabel, value), ...])

    sg, sgf, h2 = _csv("geomix_subregional_term.csv"), _csv("geomix_subregional_term_forward.csv"), _csv("geomix_h2_scores.csv")
    if sg is not None and sgf is not None:
        s = sg.set_index("quarter").subgeo_pp; f2 = sgf.set_index("quarter").subgeo_pp
        # the file carries a partial quarter-to-date row past HIST_LAST; history stops at HIST_LAST
        s = s[[q for q in s.index if C.qlabel_to_period(q) <= C.qlabel_to_period(HIST_LAST)]]
        ev.append(("G1. Sub-regional (within-region country) mix, pp of ADR \u2014 DEC-0038: attribution + forward row, NOT the base",
                   [("mean 1Q23\u20132Q26", float(s.loc["1Q23":"2Q26"].mean())), ("last 4 q to 2Q26", float(s.iloc[-4:].mean())),
                    ("fwd 3Q26", float(f2.loc["3Q26"])), ("fwd 4Q26", float(f2.loc["4Q26"])), ("4Q26 ADR effect ($)", -0.24)]))
    if h2 is not None:
        ev.append(("      H2 forecast-content test, RMSE ratio vs the residual carry \u2014 pass line 0.75 on BOTH windows \u2192 FAILS, so the term stays out of the base",
                   [("W1 (n 10)", float(h2[h2.window == "W1"].ratio_v2_vs_carry.iloc[0])), ("W2 (n 6)", float(h2[h2.window == "W2"].ratio_v2_vs_carry.iloc[0])), ("pass line", 0.75)]))

    rp = _csv("reconcile_pooled_regressions.csv")
    if rp is not None:
        d = rp[(rp["sample"] == "disclosed_only")].set_index("spec")
        pr = d.loc["primary: FE + CPI P1 + size/LOS"]
        ev.append(("G2. Reconciliation to the company's own accounting (mitigation C): disclosed constant-currency rate minus regional accommodation inflation, regressed on our within-region mix. The identity implies a slope of 1.0.",
                   [("slope", float(pr.b)), ("cluster-by-region p", float(pr.p_b0_cluster)), ("90% lo", float(pr.ci90_lo)), ("90% hi", float(pr.ci90_hi)), ("n prints", float(pr.n))]))
        alt = [("drop LatAm", "primary, drop LatAm"), ("drop EMEA", "primary, drop EMEA"), ("drop NAM", "primary, drop NAM"), ("drop APAC", "primary, drop APAC")]
        ev.append(("      the slope is carried by ONE region \u2014 leave-one-region-out (LatAm's own comparator is Brazil alone, 24\u201333% coverage)",
                   [(lbl, float(d.loc[k].b)) for lbl, k in alt if k in d.index]))
        em = [("EMEA only, n 7", "EMEA alone, upgrade-3 y and window (n 7 replication)"), ("EMEA only, n 9", "EMEA alone, upgrade-3 y (gap on mix), all 9")]
        ev.append(("      and the earlier EMEA-only reading is window-dependent: admitting two further disclosed quarters flips its sign",
                   [(lbl, float(d.loc[k].b)) for lbl, k in em if k in d.index]))

    sz = _csv("sizemix_rebased_plug.csv")
    if sz is not None:
        for var, tag in [("B adopted H size, 03 LOS", "H size"), ("C adopted H size and H LOS", "H size + H LOS"), ("A as filed (05 pooled size, 03 LOS)", "as filed (withdrawn)")]:
            g = sz[sz.variant == var].set_index("year")
            if len(g) == 3:
                ev.append((f"G3. Implied like-for-like price by year, pp \u2014 DEC-0040 route: {tag}" if tag == "H size" else f"      same, route: {tag}",
                           [("2023", float(g.loc[2023].implied_lfl_price_pp)), ("2024", float(g.loc[2024].implied_lfl_price_pp)), ("2025", float(g.loc[2025].implied_lfl_price_pp)),
                            ("2025 size term", float(g.loc[2025].size_pp))]))
        ev.append(("      DEC-0040: the filed route's NEGATIVE 2025 size term is a Paris-weighting artefact; the H route is adopted and sits inside the filed bedroom-nights bracket. 2025 like-for-like price is FLAT, so the 2026 core step is LARGER, not smaller \u2014 stated against our own interest.",
                   [("bracket lo", 0.42), ("bracket hi", 1.29)]))

    mp = _csv("market_panel_scores.csv")
    if mp is not None:
        m2 = mp[mp.spec.str.startswith("M2 ")].iloc[0]; mx = mp[mp.spec == "M2-exUS"]
        pair = [("elasticity b", float(m2.b)), ("p", float(m2.p)), ("CI lo", float(m2.ci_lo)), ("CI hi", float(m2.ci_hi)), ("n pairs", float(m2.n))]
        if len(mx): pair.append(("ex-US b", float(mx.iloc[0].b)))
        ev.append(("G4. Price-to-utilisation elasticity, market-level panel (mitigation B) \u2014 registered pass line b>0 and p\u22640.05 \u2192 FAILS. Buys at most 0.6pp of the core and in the wrong direction for a give-back; the fix is a Sept-2026 capture wave.", pair))

    rl, pmx, psum = _csv("origin_lang_rotation_ltm.csv"), _csv("origin_lang_price_mix_effect.csv"), _csv("origin_lang_price_summary.csv")
    if rl is not None and psum is not None:
        gl = rl[rl.region == "GLOBAL"].set_index("lang")
        w = psum.total_reviews_ltm_2026; rel = float((psum.rel_price_vs_en_median * w).sum() / w.sum())
        row = [("non-English +%", float(gl.loc["ALL_NON_EN"].growth_pct_24_26)), ("English +%", float(gl.loc["en"].growth_pct_24_26)),
               ("English share 2024 %", float(gl.loc["en"].share_pct_2024)), ("English share 2026 %", float(gl.loc["en"].share_pct_2026)),
               ("non-En price vs En", rel)]
        if pmx is not None:
            g = pmx[pmx.region == "GLOBAL"]
            if len(g): row.append(("mix effect %/yr", float(g.iloc[0].mix_pct_24_26_wtd) / 2))
        ev.append(("G5. Guest-origin rotation, priced (mitigation D) \u2014 day-matched LTM windows 2024\u21922026 on 53m reviews; within a market a non-English-reviewed listing is cheaper, so the rotation itself costs price.", row))

    rr = R_EV + 1
    for lbl, pairs in ev:
        label(ws, rr, lbl)
        for j, (sl, v) in enumerate(pairs):
            put(ws, rr, COL0 + j * 2, sl, F_NOTE); put(ws, rr, COL0 + j * 2 + 1, v, F_IN, NUM3)
        rr += 1
    R_EV_END = rr

    # ---------------- charts ----------------
    R_CH = R_EV_END + 2
    label(ws, R_CH, "chart helper: ADR $ (printed, then engine)"); label(ws, R_CH + 1, "chart helper: Street ADR $"); label(ws, R_CH + 2, "chart helper: FX identity (pp)"); label(ws, R_CH + 3, "chart helper: disclosed FX (pp)")
    for lab in Q:
        c = col[lab]
        if qi(lab) >= 12:
            put(ws, R_CH, c, f"={A(lab, R_ADR)}", F_LINK, NUM2)
            if lab in C.STREET_ADR: put(ws, R_CH + 1, c, f"={A(lab, R_ST)}", F_LINK, NUM2)
            put(ws, R_CH + 2, c, f"={A(lab, R_FXI)}", F_LINK, NUM2)
            if is_hist(lab): put(ws, R_CH + 3, c, f"={A(lab, R_FXD)}", F_LINK, NUM2)
    def chart(title, rows_, anchor, h_, w_):
        ch = LineChart(); ch.title = title; ch.height, ch.width = h_, w_; ch.style = 2
        for rr in rows_:
            ref = Reference(ws, min_col=col["1Q24"], max_col=col["4Q27"], min_row=rr, max_row=rr); ch.add_data(ref, from_rows=True, titles_from_data=False)
        ch.set_categories(Reference(ws, min_col=col["1Q24"], max_col=col["4Q27"], min_row=4, max_row=4))
        for s_, name in zip(ch.series, [ws.cell(rr, 1).value.replace("chart helper: ", "") for rr in rows_]):
            from openpyxl.chart.series import SeriesLabel; s_.tx = SeriesLabel(v=name); s_.smooth = False; s_.marker.symbol = "circle"
        ws.add_chart(ch, anchor)
    chart("ADR $: printed, then the engine path, vs the Street", [R_CH, R_CH + 1], f"C{R_CH+5}", 8, 22)
    chart("FX effect on ADR (pp): translation identity vs disclosed", [R_CH + 2, R_CH + 3], f"N{R_CH+5}", 8, 22)
    ws.freeze_panes = "C5"

    # ---------------- Income_Statement rows 8–11 ----------------
    isws = wb["Income_Statement"]
    put(isws, 8, 1, "Gross booking value ($bn)", F_LBL); put(isws, 8, 2, "→ nights × ADR ÷ 1000 (line 1 × line 2)", F_NOTE)
    put(isws, 9, 1, "    y/y", F_LBL); put(isws, 10, 1, "ADR ($ = GBV / nights)", F_LBL); put(isws, 10, 2, "ADR_Engine: printed (A), engine path (E) — line 2", F_NOTE); put(isws, 11, 1, "    y/y", F_LBL)
    for lab in IS_Q:
        c = is_col[lab]
        put(isws, 10, c, f"=ADR_Engine!{A(lab, R_ADR)}", F_LINK, NUM2); put(isws, 8, c, f"={L(c)}5*{L(c)}10/1000", F_FX, NUM3)
        if lab in IS_Q[4:]:
            put(isws, 11, c, f"={L(c)}10/{L(is_col[IS_Q[IS_Q.index(lab)-4]])}10-1", F_FX, PCT2); put(isws, 9, c, f"={L(c)}8/{L(is_col[IS_Q[IS_Q.index(lab)-4]])}8-1", F_FX, PCT2)
        else:
            put(isws, 11, c, f"=ADR_Engine!{A(lab, R_YOY)}", F_LINK, PCT2)
    for rr in (8, 9, 10, 11):
        for c in range(3, 3 + len(IS_Q)):
            isws.cell(rr, c).fill = PatternFill(fill_type=None)
    put(isws, 2, 1, "Row 5 nights: green = link to Nights_Engine. Rows 8–11 GBV and ADR: link to ADR_Engine (line 2). Other lines: labels only until built together (yellow = to build). Quarters A = printed, E = engine.", F_NOTE)
    # Cover + Sources
    cv = wb["Cover"]; cv["A1"] = "Airbnb (ABNB) — official model, built line by line. Line 1: nights. Line 2: ADR."
    for row in cv.iter_rows(min_row=3, max_row=12, max_col=2):
        if row[0].value == "Status":
            row[1].value = "Nights: built (DEC-0029 base 146.8m). ADR: built (ADR_Engine; pre-registered FX identity promoted, ex-FX mechanism with the bundle lapping on filed dates; proposed DEC-0034/0035 pending Theo), then extended with the v2 geo-mix layer and hardened by the four mitigations of 22 Sep (block G; DEC-0037–0041 pending Theo). Base ADR path unchanged by the mitigations: 3Q26 $177.68, 4Q26 $173.03. GBV = nights × ADR on Income_Statement row 8. Next: take rate / revenue, together, one at a time."
        if row[0].value == "Verification":
            row[1].value = "Nights: formulas recalculated in Excel and checked against the engine (block 'Engine reference values'). ADR: formulas written by adr_engine/workbook.py; open in Excel to recalculate, then tie out block E (walk-forward ratios, FX pp, ADR $)."
    src = wb["Sources"]; n0 = src.max_row + 1
    for i, (a_, b_, c_) in enumerate([("ADR, ex-FX ADR, FX effect (letters)", "data/processed/overnight/02_kpi_panel_quarterly.csv (adr_usd, adr_yoy_exfx_pct, fx_pts_adr)", "X1 §2a"),
        ("Daily FX (FRED H.10, 9 bilaterals + broad dollar)", "data/processed/pitch_model_v2/adr_engine/fx_daily_2026-09-21.csv (fetch_fx.py)", "adr_fx_prereg §1"),
        ("Destination-currency baskets κ", "data/processed/forecast_methods/fx_lag_v2/01b_basket_weights_used.csv (judgement, frozen)", "adr_fx_prereg §2"),
        ("Regional GBV shares (10-K Geographic Mix)", "data/processed/adr/01_regional_annual.csv gbv_share_pct", "adr_fx_prereg §2"),
        ("Ex-FX decomposition history", "data/processed/q3nowcast/H/adr_history_components.csv; adrq3/I/I_mix_terms_3q26.csv; adrv3/K/K4_*", "D4, adr_v1_design §3"),
        ("Bundle ADR contribution (~1pp, transcript-only)", "ledger D014 (4Q25 call), D032 (1Q26 call); filed substitute D031 'roughly 20% of GBV from RNPL'", "adr_v1_design §3"),
        ("Regional ADR levels and shares", "data/processed/adr/04_regional_quarterly_wide.csv (disclosed-chained)", "adr_v1_design §3.3"),
        ("Street ADR", "Bloomberg MODL screenshot 12 Sep 2026 (3Q26 n 26, 4Q26 n 25)", "DEC-0005 / V1"),
        ("ADR engine outputs", "data/processed/pitch_model_v2/adr_engine/ (fx_scores.csv, fx_forecast_asof.csv, adr_path.csv, …)", "adr_fx_prereg §9"),
        ("Sub-regional mix inputs (v2)", "Inside Airbnb capture store → refresh_prices.py: 123 markets, 30 priced countries", "adr_v2_geomix_prereg"),
        ("Origin→destination flows", "NTTO, JNTO, ABS, StatCan arrivals by origin (od_layer.py)", "adr_v2_upgrade2"),
        ("Mitigation outputs (block G)", "adr_engine/: reconcile_pooled_regressions.csv, sizemix_rebased_plug.csv, market_panel_scores.csv, origin_lang_*.csv", "adr_v2_mitigation_A–D")], start=n0):
        put(src, i, 1, a_, F_LBL); put(src, i, 2, b_, F_LBL); put(src, i, 3, c_, F_LBL)
    wb.save(C.XLSX)
    refs = dict(R_EV=R_EV, R_ADR=R_ADR, R_FXD=R_FXD, R_FXI=R_FXI, R_EXM=R_EXM, R_LVL=R_LVL, R_REP=R_REP, R_GM=R_GM, R_CORE=R_CORE, R_BUN=R_BUN, R_REF=R_REF, R_ALT=R_ALT, R_RMSE=R_RMSE)
    (C.OUT / "workbook_refs.json").write_text(json.dumps(refs)); print("wrote", C.XLSX, refs)
    return C.XLSX, refs


if __name__ == "__main__":
    build()
