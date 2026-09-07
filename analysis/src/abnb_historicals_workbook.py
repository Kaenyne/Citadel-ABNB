"""Build model/ABNB_historicals.xlsx: historical-only consolidation of ABNB P&L, KPIs,
revenue-growth decomposition, margin decomposition, and earnings beat/meet/miss with stock moves.

Nothing forward-looking. Every derived line is a live Excel formula over the input rows so it can be audited.

Inputs (all on main):
  data/processed/overnight/02_kpi_panel_quarterly.csv      nights, GBV, revenue, letters' FX splits, shares, net income
  data/processed/overnight/07_cost_lines_per_night.csv     GAAP and cash (ex-SBC) cost lines, SBC by line, D&A, add-backs, FCF
  data/processed/overnight/02_guidance_ledger.csv          194 management guidance statements with outcomes
  data/processed/overnight/02_fy_guide_revisions.csv       full-year guides and their revisions
  data/processed/overnight/16_consensus_at_print_merged.csv consensus at each print (press/vendor quotes) and surprises
  data/processed/abnb_earnings_reactions.csv               close-to-close 1/5/20-session moves vs QQQ
  data/processed/overnight/20_executable_returns.csv       next-open entry returns (gap, open-to-close, 5d, 20d)

Run:  py -3.13 analysis/src/abnb_historicals_workbook.py
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "model" / "ABNB_historicals.xlsx"

# ----------------------------------------------------------------------------- inputs
kpi = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv").set_index("quarter")
cost = pd.read_csv(ROOT / "data/processed/overnight/07_cost_lines_per_night.csv").set_index("quarter")
ledger = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_ledger.csv")
fyrev = pd.read_csv(ROOT / "data/processed/overnight/02_fy_guide_revisions.csv")
cons = pd.read_csv(ROOT / "data/processed/overnight/16_consensus_at_print_merged.csv").set_index("print_quarter")
react = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv").set_index("quarter")
execr = pd.read_csv(ROOT / "data/processed/overnight/20_executable_returns.csv").set_index("print_quarter")

QUARTERS = ["1Q21", "2Q21", "3Q21", "4Q21",
            "1Q22", "2Q22", "3Q22", "4Q22",
            "1Q23", "2Q23", "3Q23", "4Q23",
            "1Q24", "2Q24", "3Q24", "4Q24",
            "1Q25", "2Q25", "3Q25", "4Q25",
            "1Q26", "2Q26"]
FYS = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"]


def q_to_iso(q: str) -> str:  # "4Q21" -> "2021Q4"
    return f"20{q[2:]}Q{q[0]}"


def v(x):
    if x is None:
        return None
    try:
        if isinstance(x, float) and math.isnan(x):
            return None
    except TypeError:
        pass
    return x


# ----------------------------------------------------------------------------- styles
BOLD = Font(bold=True)
HDR = Font(bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="1F3A5F")
SEC_FILL = PatternFill("solid", fgColor="DCE6F1")
BASE_FILL = PatternFill("solid", fgColor="F2F2F2")
INPUT_FONT = Font(color="0000FF")          # blue = hard-coded input from the CSVs
CALC_FONT = Font(color="000000")           # black = formula
NOTE_FONT = Font(italic=True, color="666666", size=9)
THIN = Side(style="thin", color="BBBBBB")
TOP = Border(top=Side(style="medium", color="1F3A5F"))

FMT = {
    "m": '#,##0;(#,##0)',
    "m1": '#,##0.0;(#,##0.0)',
    "b": '0.00',
    "usd": '$#,##0.00',
    "pct": '0.0%;(0.0%)',
    "pts": '0.0;(0.0)',
    "pct1": '0.0"%";(0.0"%")',
    "x": '0.00',
    "int": '0',
}

wb = Workbook()

# ============================================================================= SHEET 1: Historicals
ws = wb.active
ws.title = "Historicals"

FIRST_COL = 3                                   # column C = 1Q21
QCOL = {q: FIRST_COL + i for i, q in enumerate(QUARTERS)}
GAP = FIRST_COL + len(QUARTERS)                 # blank column
FYCOL = {fy: GAP + 1 + i for i, fy in enumerate(FYS)}
LTM_COL = GAP + 1 + len(FYS)
LAST_COL = LTM_COL

ws["A1"] = "Airbnb (ABNB): historical P&L, KPIs, growth decomposition and margin decomposition, 1Q21 to 2Q26"
ws["A1"].font = Font(bold=True, size=13)
ws["A2"] = ("Blue = value taken from the source CSVs (shareholder letters, 10-Q/10-K XBRL, call transcripts). "
            "Black = Excel formula. 2021 columns are shown only as the base year for 2022 growth. "
            "$ in millions unless stated. Nothing here is forward-looking.")
ws["A2"].font = NOTE_FONT

row = 4
ws.cell(row=row, column=1, value="Line").font = HDR
ws.cell(row=row, column=2, value="Unit").font = HDR
for q, c in QCOL.items():
    cell = ws.cell(row=row, column=c, value=q)
    cell.font = HDR
    cell.alignment = Alignment(horizontal="center")
for fy, c in FYCOL.items():
    cell = ws.cell(row=row, column=c, value=fy)
    cell.font = HDR
    cell.alignment = Alignment(horizontal="center")
cell = ws.cell(row=row, column=LTM_COL, value="LTM 2Q26")
cell.font = HDR
cell.alignment = Alignment(horizontal="center")
for c in range(1, LAST_COL + 1):
    ws.cell(row=row, column=c).fill = HDR_FILL
HEADER_ROW = row
ws.freeze_panes = ws.cell(row=HEADER_ROW + 1, column=FIRST_COL)

ROWS: dict[str, int] = {}          # key -> row number
row = HEADER_ROW + 1


def section(title: str):
    global row
    row += 1
    c = ws.cell(row=row, column=1, value=title)
    c.font = BOLD
    for cc in range(1, LAST_COL + 1):
        ws.cell(row=row, column=cc).fill = SEC_FILL
    row += 1


def qcells(key: str):
    """Yield (quarter, column_letter, prior_year_column_letter or None)."""
    for i, q in enumerate(QUARTERS):
        col = L(QCOL[q])
        prev = L(QCOL[QUARTERS[i - 4]]) if i >= 4 else None
        yield q, col, prev


def put(key: str, label: str, unit: str, fmt: str, quarterly, annual=None, ltm=None, note: str | None = None,
        input_row: bool = False):
    """quarterly: callable(q, col, prev) -> value or formula string. annual: callable(fy, col, prevfy_col) ."""
    global row
    ROWS[key] = row
    ws.cell(row=row, column=1, value=label)
    ws.cell(row=row, column=2, value=unit).font = NOTE_FONT
    for q, col, prev in qcells(key):
        val = quarterly(q, col, prev)
        if val is None:
            continue
        cell = ws.cell(row=row, column=QCOL[q], value=val)
        cell.number_format = FMT[fmt]
        cell.font = INPUT_FONT if input_row else CALC_FONT
        if q.endswith("21"):
            cell.fill = BASE_FILL
    if annual is not None:
        for i, fy in enumerate(FYS):
            col = L(FYCOL[fy])
            prevfy = L(FYCOL[FYS[i - 1]]) if i >= 1 else None
            val = annual(fy, col, prevfy)
            if val is None:
                continue
            cell = ws.cell(row=row, column=FYCOL[fy], value=val)
            cell.number_format = FMT[fmt]
            cell.font = CALC_FONT
    if ltm is not None:
        val = ltm(L(LTM_COL))
        if val is not None:
            cell = ws.cell(row=row, column=LTM_COL, value=val)
            cell.number_format = FMT[fmt]
    if note:
        ws.cell(row=row, column=LAST_COL + 1, value=note).font = NOTE_FONT
    row += 1


def r(key: str) -> int:
    return ROWS[key]


def fy_quarters(fy: str) -> list[str]:
    yy = fy[-2:]
    return [f"{i}Q{yy}" for i in range(1, 5)]


def sum_fy(key: str):
    def f(fy, col, prevfy):
        qs = fy_quarters(fy)
        return f"=SUM({L(QCOL[qs[0]])}{r(key)}:{L(QCOL[qs[-1]])}{r(key)})"
    return f


def sum_ltm(key: str):
    def f(col):
        return f"=SUM({L(QCOL['3Q25'])}{r(key)}:{L(QCOL['2Q26'])}{r(key)})"
    return f


def yoy(key: str):
    def fq(q, col, prev):
        return f"={col}{r(key)}/{prev}{r(key)}-1" if prev else None
    def fa(fy, col, prevfy):
        return f"={col}{r(key)}/{prevfy}{r(key)}-1" if prevfy else None
    return fq, fa


def ratio(num: str, den: str, scale: float = 1.0):
    def fq(q, col, prev):
        return f"={col}{r(num)}/{col}{r(den)}" + (f"*{scale}" if scale != 1.0 else "")
    def fa(fy, col, prevfy):
        return f"={col}{r(num)}/{col}{r(den)}" + (f"*{scale}" if scale != 1.0 else "")
    def fl(col):
        return f"={col}{r(num)}/{col}{r(den)}" + (f"*{scale}" if scale != 1.0 else "")
    return fq, fa, fl


def val_from(df, colname, scale=1.0, quarters_iso=False):
    def f(q, col, prev):
        key = q_to_iso(q) if quarters_iso else q
        if key not in df.index:
            return None
        x = v(df.loc[key, colname])
        return None if x is None else x * scale
    return f


# ---------------------------------------------------------------- A. Volume, price, revenue
section("A. Volume, price and revenue (letters)")
put("nights", "Nights & Seats Booked", "M", "m1", val_from(kpi, "nights_m"), sum_fy("nights"), sum_ltm("nights"), input_row=True,
    note="Renamed from Nights & Experiences Booked in 2025; seats immaterial per CFO.")
put("gbv", "Gross Booking Value", "$M", "m", val_from(kpi, "gbv_busd", 1000), sum_fy("gbv"), sum_ltm("gbv"), input_row=True)
put("adr", "ADR (GBV / nights)", "$", "usd", *ratio("gbv", "nights"))
put("rev", "Revenue", "$M", "m", val_from(kpi, "revenue_musd"), sum_fy("rev"), sum_ltm("rev"), input_row=True)
put("tr", "Take rate (revenue / GBV)", "%", "pct", *ratio("rev", "gbv"),
    note="Seasonal: revenue recognised at check-in, GBV at booking. Compare same quarter only.")
put("rpn", "Revenue per night", "$", "usd", *ratio("rev", "nights"))

section("B. Year-over-year growth")
put("g_nights", "Nights y/y", "%", "pct", *yoy("nights"))
put("g_gbv", "GBV y/y", "%", "pct", *yoy("gbv"))
put("g_adr", "ADR y/y (reported)", "%", "pct", *yoy("adr"))
put("g_rev", "Revenue y/y (reported)", "%", "pct", *yoy("rev"))
put("g_tr", "Take rate y/y change", "pts", "pts",
    (lambda q, col, prev: f"=({col}{r('tr')}-{prev}{r('tr')})*100" if prev else None),
    (lambda fy, col, prevfy: f"=({col}{r('tr')}-{prevfy}{r('tr')})*100" if prevfy else None))
put("g_rpn", "Revenue per night y/y", "%", "pct", *yoy("rpn"))

section("C. FX, as disclosed by the company (shareholder letters)")
put("g_rev_exfx", "Revenue y/y ex-FX (letter)", "%", "pct", val_from(kpi, "revenue_yoy_exfx_pct", 0.01), input_row=True,
    note="Company-stated constant-currency revenue growth.")
put("fx_rev", "FX effect on revenue growth (reported minus ex-FX)", "pts", "pts",
    (lambda q, col, prev: f"=IF({col}{r('g_rev_exfx')}=\"\",\"\",ROUND({col}{r('g_rev')}*100,0)-{col}{r('g_rev_exfx')}*100)" if prev else None),
    note="Letters round both growth rates to whole points, so FX is a whole-point figure.")
put("g_adr_exfx", "ADR y/y ex-FX (letter)", "%", "pct", val_from(kpi, "adr_yoy_exfx_pct", 0.01), input_row=True,
    note="Company-stated. Disclosed from 2Q22; approximate ('roughly flat' = 0.5) in some quarters.")
put("fx_adr", "FX effect on ADR growth (reported minus ex-FX)", "pts", "pts",
    (lambda q, col, prev: f"=IF({col}{r('g_adr_exfx')}=\"\",\"\",({col}{r('g_adr')}-{col}{r('g_adr_exfx')})*100)" if prev else None))

section("D. Revenue growth decomposition (points of reported y/y growth; exact log-share attribution)")
# hidden helper: prior-year revenue by quarter (for annual FX weighting)
put("rev_prior", "  memo: prior-year quarter revenue", "$M", "m",
    (lambda q, col, prev: f"={prev}{r('rev')}" if prev else None),
    (lambda fy, col, prevfy: f"={prevfy}{r('rev')}" if prevfy else None))

put("L", "ln(revenue / prior-year revenue)", "", "x",
    (lambda q, col, prev: f"=LN({col}{r('rev')}/{prev}{r('rev')})" if prev else None),
    (lambda fy, col, prevfy: f"=LN({col}{r('rev')}/{prevfy}{r('rev')})" if prevfy else None))
put("d_nights", "  from nights", "pts", "pts",
    (lambda q, col, prev: f"=LN({col}{r('nights')}/{prev}{r('nights')})/{col}{r('L')}*{col}{r('g_rev')}*100" if prev else None),
    (lambda fy, col, prevfy: f"=LN({col}{r('nights')}/{prevfy}{r('nights')})/{col}{r('L')}*{col}{r('g_rev')}*100" if prevfy else None))
put("d_adr", "  from ADR (reported, incl. FX)", "pts", "pts",
    (lambda q, col, prev: f"=LN({col}{r('adr')}/{prev}{r('adr')})/{col}{r('L')}*{col}{r('g_rev')}*100" if prev else None),
    (lambda fy, col, prevfy: f"=LN({col}{r('adr')}/{prevfy}{r('adr')})/{col}{r('L')}*{col}{r('g_rev')}*100" if prevfy else None))
put("d_fx", "    of which FX (letter)", "pts", "pts",
    (lambda q, col, prev: f"=IF({col}{r('fx_rev')}=\"\",\"\",{col}{r('fx_rev')})" if prev else None),
    (lambda fy, col, prevfy: (f"=SUMPRODUCT({L(QCOL[fy_quarters(fy)[0]])}{r('fx_rev')}:{L(QCOL[fy_quarters(fy)[-1]])}{r('fx_rev')},"
                              f"{L(QCOL[fy_quarters(fy)[0]])}{r('rev_prior')}:{L(QCOL[fy_quarters(fy)[-1]])}{r('rev_prior')})/{col}{r('rev_prior')}")
     if prevfy and fy != "FY2022" else None),
    note="Annual FX = quarterly FX points weighted by prior-year quarterly revenue (FY2022 omitted: 1H21 FX not disclosed).")
put("d_adr_exfx", "    of which ADR ex-FX (residual)", "pts", "pts",
    (lambda q, col, prev: f"=IF({col}{r('d_fx')}=\"\",\"\",{col}{r('d_adr')}-{col}{r('d_fx')})" if prev else None),
    (lambda fy, col, prevfy: f"=IF({col}{r('d_fx')}=\"\",\"\",{col}{r('d_adr')}-{col}{r('d_fx')})" if prevfy else None))
put("d_tr", "  from take rate (booking-to-stay timing and fee mix)", "pts", "pts",
    (lambda q, col, prev: f"=LN({col}{r('tr')}/{prev}{r('tr')})/{col}{r('L')}*{col}{r('g_rev')}*100" if prev else None),
    (lambda fy, col, prevfy: f"=LN({col}{r('tr')}/{prevfy}{r('tr')})/{col}{r('L')}*{col}{r('g_rev')}*100" if prevfy else None))
put("d_check", "  check: nights + ADR + take rate = reported growth", "pts", "pts",
    (lambda q, col, prev: f"={col}{r('d_nights')}+{col}{r('d_adr')}+{col}{r('d_tr')}-{col}{r('g_rev')}*100" if prev else None),
    (lambda fy, col, prevfy: f"={col}{r('d_nights')}+{col}{r('d_adr')}+{col}{r('d_tr')}-{col}{r('g_rev')}*100" if prevfy else None),
    note="Should read 0.0. Method: each factor's share of log growth times reported growth.")
section("E. Regional and mix disclosures (letters; growth bands as stated)")
put("na", "Nights y/y: North America", "%", "pct", val_from(kpi, "nights_yoy_na_pct", 0.01), input_row=True)
put("emea", "Nights y/y: EMEA", "%", "pct", val_from(kpi, "nights_yoy_emea_pct", 0.01), input_row=True)
put("latam", "Nights y/y: Latin America", "%", "pct", val_from(kpi, "nights_yoy_latam_pct", 0.01), input_row=True)
put("apac", "Nights y/y: Asia Pacific", "%", "pct", val_from(kpi, "nights_yoy_apac_pct", 0.01), input_row=True,
    note="Management gives bands ('high single digits'); the panel stores the midpoint. Blank = not disclosed.")
put("adr_na", "ADR y/y: North America", "%", "pct", val_from(kpi, "adr_yoy_na_pct", 0.01), input_row=True)
put("adr_emea", "ADR y/y: EMEA", "%", "pct", val_from(kpi, "adr_yoy_emea_pct", 0.01), input_row=True)
put("adr_latam", "ADR y/y: Latin America", "%", "pct", val_from(kpi, "adr_yoy_latam_pct", 0.01), input_row=True)
put("adr_apac", "ADR y/y: Asia Pacific", "%", "pct", val_from(kpi, "adr_yoy_apac_pct", 0.01), input_row=True)
put("bedroom", "Bedroom nights booked y/y", "%", "pct", val_from(kpi, "bedroom_nights_yoy_pct", 0.01), input_row=True,
    note="First disclosed 2Q26.")
put("xborder", "Cross-border share of nights", "%", "pct", val_from(kpi, "cross_border_share_pct", 0.01), input_row=True,
    note="Disclosure stopped after 1Q24.")
put("urban", "Urban share of nights", "%", "pct", val_from(kpi, "urban_share_pct", 0.01), input_row=True, note="Stopped after 4Q23.")
put("lts", "Long-term stays (28+ nights) share", "%", "pct", val_from(kpi, "long_term_stays_share_pct", 0.01), input_row=True,
    note="Stopped after 1Q24.")
put("app", "App share of nights", "%", "pct", val_from(kpi, "app_share_of_nights_pct", 0.01), input_row=True)
put("listings", "Active listings", "M", "b", val_from(kpi, "active_listings_m"), input_row=True, note="Disclosed irregularly.")

# ---------------------------------------------------------------- F. P&L
section("F. GAAP cost lines and profit (10-Q/10-K; Q4 = FY less nine months)")
for key, label, colname in [
    ("cor_g", "Cost of revenue", "cor_gaap_musd"), ("ops_g", "Operations and support", "ops_gaap_musd"),
    ("pd_g", "Product development", "pd_gaap_musd"), ("sm_g", "Sales and marketing", "sm_gaap_musd"),
    ("ga_g", "General and administrative", "ga_gaap_musd")]:
    put(key, label, "$M", "m", val_from(cost, colname), sum_fy(key), sum_ltm(key), input_row=True)
put("restr", "Restructuring charges", "$M", "m", val_from(kpi, "restructuring_musd"), sum_fy("restr"), sum_ltm("restr"), input_row=True,
    note="Blank = none reported.")
put("opinc", "Operating income (reported)", "$M", "m", val_from(cost, "operating_income_musd"), sum_fy("opinc"), sum_ltm("opinc"), input_row=True)
put("opinc_chk", "  check: revenue less lines less restructuring", "$M", "m",
    (lambda q, col, prev: f"={col}{r('rev')}-{col}{r('cor_g')}-{col}{r('ops_g')}-{col}{r('pd_g')}-{col}{r('sm_g')}-{col}{r('ga_g')}-N({col}{r('restr')})-{col}{r('opinc')}"),
    note="Small differences = rounding in the letter/XBRL lines.")
put("intinc", "Interest income", "$M", "m", val_from(cost, "interest_income_musd"), sum_fy("intinc"), sum_ltm("intinc"), input_row=True)
put("tax", "Income tax provision (benefit)", "$M", "m", val_from(kpi, "income_tax_musd"), sum_fy("tax"), sum_ltm("tax"), input_row=True,
    note="3Q23 = $2.7bn valuation-allowance release.")
put("ni", "Net income (loss)", "$M", "m", val_from(kpi, "net_income_musd"), sum_fy("ni"), sum_ltm("ni"), input_row=True)
put("dil_sh", "Diluted weighted-average shares", "M", "m1", val_from(kpi, "diluted_wa_shares_m"), input_row=True,
    note="Annual columns blank on purpose: Q4 counts are derived and the FY average is in the 10-K.")
put("eps_gaap", "GAAP diluted EPS (net income / diluted shares)", "$", "usd",
    (lambda q, col, prev: f"=IF({col}{r('dil_sh')}=\"\",\"\",{col}{r('ni')}/{col}{r('dil_sh')})"))
put("eps_adj", "Adjusted EPS as reported in press / vendor basis", "$", "usd",
    val_from(cons, "actual_eps_usd", quarters_iso=True), input_row=True,
    note="Basis differs by quarter (see Earnings sheet); GAAP incl. one-offs before 4Q21 and in 3Q23/4Q23.")

section("G. Stock-based compensation by line (letters) and cash (ex-SBC) cost lines")
put("sbc", "SBC total", "$M", "m", val_from(cost, "sbc_total_musd"), sum_fy("sbc"), sum_ltm("sbc"), input_row=True)
for key, label, colname in [
    ("sbc_cor", "  SBC in cost of revenue", "cor_sbc_musd"), ("sbc_ops", "  SBC in operations and support", "ops_sbc_musd"),
    ("sbc_pd", "  SBC in product development", "pd_sbc_musd"), ("sbc_sm", "  SBC in sales and marketing", "sm_sbc_musd"),
    ("sbc_ga", "  SBC in G&A", "ga_sbc_musd")]:
    put(key, label, "$M", "m", val_from(cost, colname), sum_fy(key), sum_ltm(key), input_row=True)
for key, label, g, s in [
    ("cor_c", "Cost of revenue, cash", "cor_g", "sbc_cor"), ("ops_c", "Operations and support, cash", "ops_g", "sbc_ops"),
    ("pd_c", "Product development, cash", "pd_g", "sbc_pd"), ("sm_c", "Sales and marketing, cash", "sm_g", "sbc_sm"),
    ("ga_c", "G&A, cash", "ga_g", "sbc_ga")]:
    put(key, label, "$M", "m",
        (lambda q, col, prev, g=g, s=s: f"={col}{r(g)}-{col}{r(s)}"),
        (lambda fy, col, prevfy, g=g, s=s: f"={col}{r(g)}-{col}{r(s)}"),
        (lambda col, g=g, s=s: f"={col}{r(g)}-{col}{r(s)}"))
put("sm_bp", "  S&M: brand and performance marketing", "$M", "m", val_from(cost, "sm_brand_perf_musd"), input_row=True,
    note="10-K/10-Q split; quarterly from 2023 where disclosed. Cash basis approximated by the filing split.")
put("sm_fo", "  S&M: field operations and policy", "$M", "m", val_from(cost, "sm_field_ops_musd"), input_row=True)
put("cash_tot", "Total cash cost", "$M", "m",
    (lambda q, col, prev: f"={col}{r('cor_c')}+{col}{r('ops_c')}+{col}{r('pd_c')}+{col}{r('sm_c')}+{col}{r('ga_c')}"),
    (lambda fy, col, prevfy: f"={col}{r('cor_c')}+{col}{r('ops_c')}+{col}{r('pd_c')}+{col}{r('sm_c')}+{col}{r('ga_c')}"),
    (lambda col: f"={col}{r('cor_c')}+{col}{r('ops_c')}+{col}{r('pd_c')}+{col}{r('sm_c')}+{col}{r('ga_c')}"))
put("da", "Depreciation and amortisation", "$M", "m", val_from(cost, "da_musd"), sum_fy("da"), sum_ltm("da"), input_row=True)
put("addb", "Other Adjusted EBITDA add-backs (net)", "$M", "m", val_from(cost, "other_addbacks_musd"), sum_fy("addb"), sum_ltm("addb"), input_row=True,
    note="Lodging-tax reserves, restructuring, acquisition costs. 4Q23 = $928M Italy withholding settlement (sits in G&A cash).")
put("ebitda", "Adjusted EBITDA (reported)", "$M", "m", val_from(cost, "adj_ebitda_musd"), sum_fy("ebitda"), sum_ltm("ebitda"), input_row=True)
put("ebitda_chk", "  check: revenue less cash cost plus D&A and add-backs, minus reported", "$M", "m",
    (lambda q, col, prev: f"={col}{r('rev')}-{col}{r('cash_tot')}+{col}{r('da')}+{col}{r('addb')}-{col}{r('ebitda')}"),
    (lambda fy, col, prevfy: f"={col}{r('rev')}-{col}{r('cash_tot')}+{col}{r('da')}+{col}{r('addb')}-{col}{r('ebitda')}"),
    (lambda col: f"={col}{r('rev')}-{col}{r('cash_tot')}+{col}{r('da')}+{col}{r('addb')}-{col}{r('ebitda')}"),
    note="0 from 3Q22. 1Q21 (-113) and 2Q22 (-90): letters' SBC-by-line footnotes do not tie.")
put("fcf", "Free cash flow (letter)", "$M", "m", val_from(cost, "fcf_musd"), sum_fy("fcf"), sum_ltm("fcf"), input_row=True)

section("H. Margins and cost ratios (% of revenue)")
put("m_ebitda", "Adjusted EBITDA margin", "%", "pct", *ratio("ebitda", "rev"))
put("m_op", "GAAP operating margin", "%", "pct", *ratio("opinc", "rev"))
put("m_ni", "Net margin", "%", "pct", *ratio("ni", "rev"))
put("m_fcf", "FCF margin", "%", "pct", *ratio("fcf", "rev"))
put("m_sbc", "SBC % revenue", "%", "pct", *ratio("sbc", "rev"))
for key, label in [("cor_g", "Cost of revenue (GAAP)"), ("ops_g", "Operations and support (GAAP)"), ("pd_g", "Product development (GAAP)"),
                   ("sm_g", "Sales and marketing (GAAP)"), ("ga_g", "G&A (GAAP)")]:
    put("p_" + key, label, "%", "pct", *ratio(key, "rev"))
for key, label in [("cor_c", "Cost of revenue (cash)"), ("ops_c", "Operations and support (cash)"), ("pd_c", "Product development (cash)"),
                   ("sm_c", "Sales and marketing (cash)"), ("ga_c", "G&A (cash)")]:
    put("p_" + key, label, "%", "pct", *ratio(key, "rev"))
put("p_sm_bp", "  Brand and performance marketing", "%", "pct",
    (lambda q, col, prev: f"=IF({col}{r('sm_bp')}=\"\",\"\",{col}{r('sm_bp')}/{col}{r('rev')})"))
put("p_addb", "D&A plus add-backs", "%", "pct",
    (lambda q, col, prev: f"=({col}{r('da')}+{col}{r('addb')})/{col}{r('rev')}"),
    (lambda fy, col, prevfy: f"=({col}{r('da')}+{col}{r('addb')})/{col}{r('rev')}"),
    (lambda col: f"=({col}{r('da')}+{col}{r('addb')})/{col}{r('rev')}"))
put("p_cor_gbv", "Cost of revenue (cash) per $100 of GBV", "$", "usd",
    (lambda q, col, prev: f"={col}{r('cor_c')}/{col}{r('gbv')}*100"),
    (lambda fy, col, prevfy: f"={col}{r('cor_c')}/{col}{r('gbv')}*100"),
    (lambda col: f"={col}{r('cor_c')}/{col}{r('gbv')}*100"),
    note="Payments cost scales with GBV, not revenue.")

section("I. What moved the Adjusted EBITDA margin: y/y change in margin points, by line (cash basis)")
put("dm_total", "Change in Adjusted EBITDA margin y/y", "pts", "pts",
    (lambda q, col, prev: f"=({col}{r('m_ebitda')}-{prev}{r('m_ebitda')})*100" if prev else None),
    (lambda fy, col, prevfy: f"=({col}{r('m_ebitda')}-{prevfy}{r('m_ebitda')})*100" if prevfy else None))
for key, label in [("cor_c", "  Cost of revenue"), ("ops_c", "  Operations and support"), ("pd_c", "  Product development"),
                   ("sm_c", "  Sales and marketing"), ("ga_c", "  G&A")]:
    put("dm_" + key, label + " (lower ratio = positive)", "pts", "pts",
        (lambda q, col, prev, key=key: f"=-({col}{r('p_' + key)}-{prev}{r('p_' + key)})*100" if prev else None),
        (lambda fy, col, prevfy, key=key: f"=-({col}{r('p_' + key)}-{prevfy}{r('p_' + key)})*100" if prevfy else None))
put("dm_addb", "  D&A and add-backs", "pts", "pts",
    (lambda q, col, prev: f"=({col}{r('p_addb')}-{prev}{r('p_addb')})*100" if prev else None),
    (lambda fy, col, prevfy: f"=({col}{r('p_addb')}-{prevfy}{r('p_addb')})*100" if prevfy else None))
put("dm_resid", "  Residual (identity gaps)", "pts", "pts",
    (lambda q, col, prev: f"={col}{r('dm_total')}-{col}{r('dm_cor_c')}-{col}{r('dm_ops_c')}-{col}{r('dm_pd_c')}-{col}{r('dm_sm_c')}-{col}{r('dm_ga_c')}-{col}{r('dm_addb')}" if prev else None),
    (lambda fy, col, prevfy: f"={col}{r('dm_total')}-{col}{r('dm_cor_c')}-{col}{r('dm_ops_c')}-{col}{r('dm_pd_c')}-{col}{r('dm_sm_c')}-{col}{r('dm_ga_c')}-{col}{r('dm_addb')}" if prevfy else None),
    note="4Q23: the $928M Italy settlement inflates cash G&A and the add-back equally; both lines swing, net zero.")

section("J. Per-night economics: revenue per night vs cash cost per night (why the ratio moved)")
put("cpn_tot", "Cash cost per night, total", "$", "usd", *ratio("cash_tot", "nights"))
for key, label in [("cor_c", "  Cost of revenue per night"), ("ops_c", "  Operations and support per night"),
                   ("pd_c", "  Product development per night"), ("sm_c", "  Sales and marketing per night"), ("ga_c", "  G&A per night")]:
    put("cpn_" + key, label, "$", "usd", *ratio(key, "nights"))
put("g_cpn_tot", "Cash cost per night y/y", "%", "pct", *yoy("cpn_tot"))
put("g_cpn_sm", "  S&M cash per night y/y", "%", "pct", *yoy("cpn_sm_c"))
put("g_cpn_ops", "  Ops & support cash per night y/y", "%", "pct", *yoy("cpn_ops_c"))

ws.cell(row=row, column=1, value="Split of each line's margin contribution into (a) unit cost per night and (b) revenue per night. "
        "Exact identity: -delta(c/p) = -(c1-c0)/p0 - c1*(1/p1-1/p0).").font = NOTE_FONT
row += 1
for key, label in [("cor_c", "Cost of revenue"), ("ops_c", "Operations and support"), ("pd_c", "Product development"),
                   ("sm_c", "Sales and marketing"), ("ga_c", "G&A")]:
    put("uc_" + key, f"  {label}: unit-cost effect", "pts", "pts",
        (lambda q, col, prev, key=key: f"=-({col}{r('cpn_' + key)}-{prev}{r('cpn_' + key)})/{prev}{r('rpn')}*100" if prev else None),
        (lambda fy, col, prevfy, key=key: f"=-({col}{r('cpn_' + key)}-{prevfy}{r('cpn_' + key)})/{prevfy}{r('rpn')}*100" if prevfy else None))
    put("rp_" + key, f"  {label}: revenue-per-night effect", "pts", "pts",
        (lambda q, col, prev, key=key: f"=-{col}{r('cpn_' + key)}*(1/{col}{r('rpn')}-1/{prev}{r('rpn')})*100" if prev else None),
        (lambda fy, col, prevfy, key=key: f"=-{col}{r('cpn_' + key)}*(1/{col}{r('rpn')}-1/{prevfy}{r('rpn')})*100" if prevfy else None))
put("uc_sum", "Total unit-cost effect (all lines)", "pts", "pts",
    (lambda q, col, prev: "=" + "+".join(f"{col}{r('uc_' + k)}" for k in ["cor_c", "ops_c", "pd_c", "sm_c", "ga_c"]) if prev else None),
    (lambda fy, col, prevfy: "=" + "+".join(f"{col}{r('uc_' + k)}" for k in ["cor_c", "ops_c", "pd_c", "sm_c", "ga_c"]) if prevfy else None))
put("rp_sum", "Total revenue-per-night effect (all lines)", "pts", "pts",
    (lambda q, col, prev: "=" + "+".join(f"{col}{r('rp_' + k)}" for k in ["cor_c", "ops_c", "pd_c", "sm_c", "ga_c"]) if prev else None),
    (lambda fy, col, prevfy: "=" + "+".join(f"{col}{r('rp_' + k)}" for k in ["cor_c", "ops_c", "pd_c", "sm_c", "ga_c"]) if prevfy else None))
ws.cell(row=row, column=1, value="Revenue-per-night effect split by log weights of its drivers: revenue per night = ADR x take rate; "
        "ADR split into FX (letter) and ADR ex-FX. Quarterly where the letter gives FX; annual on the weighted FX.").font = NOTE_FONT
row += 1
put("w_L", "  memo: ln(revenue per night / prior)", "", "x",
    (lambda q, col, prev: f"=LN({col}{r('rpn')}/{prev}{r('rpn')})" if prev else None),
    (lambda fy, col, prevfy: f"=LN({col}{r('rpn')}/{prevfy}{r('rpn')})" if prevfy else None))
put("rp_tr", "  of which take rate", "pts", "pts",
    (lambda q, col, prev: f"={col}{r('rp_sum')}*LN({col}{r('tr')}/{prev}{r('tr')})/{col}{r('w_L')}" if prev else None),
    (lambda fy, col, prevfy: f"={col}{r('rp_sum')}*LN({col}{r('tr')}/{prevfy}{r('tr')})/{col}{r('w_L')}" if prevfy else None))
put("rp_fx", "  of which FX", "pts", "pts",
    (lambda q, col, prev: f"=IF({col}{r('fx_rev')}=\"\",\"\",{col}{r('rp_sum')}*LN(1+{col}{r('fx_rev')}/100)/{col}{r('w_L')})" if prev else None),
    (lambda fy, col, prevfy: f"=IF({col}{r('d_fx')}=\"\",\"\",{col}{r('rp_sum')}*LN(1+{col}{r('d_fx')}/100)/{col}{r('w_L')})" if prevfy else None))
put("rp_adr", "  of which ADR ex-FX", "pts", "pts",
    (lambda q, col, prev: f"=IF({col}{r('rp_fx')}=\"\",\"\",{col}{r('rp_sum')}-{col}{r('rp_tr')}-{col}{r('rp_fx')})" if prev else None),
    (lambda fy, col, prevfy: f"=IF({col}{r('rp_fx')}=\"\",\"\",{col}{r('rp_sum')}-{col}{r('rp_tr')}-{col}{r('rp_fx')})" if prevfy else None))
put("bridge_chk", "Check: unit cost + revenue per night + D&A/add-backs = margin change", "pts", "pts",
    (lambda q, col, prev: f"={col}{r('uc_sum')}+{col}{r('rp_sum')}+{col}{r('dm_addb')}-{col}{r('dm_total')}" if prev else None),
    (lambda fy, col, prevfy: f"={col}{r('uc_sum')}+{col}{r('rp_sum')}+{col}{r('dm_addb')}-{col}{r('dm_total')}" if prevfy else None),
    note="0.0 where the EBITDA identity holds (from 3Q22).")

section("K. Cash flow and capital return (letters, XBRL)")
put("cfo", "Cash from operations", "$M", "m", val_from(kpi, "cfo_musd"), sum_fy("cfo"), sum_ltm("cfo"), input_row=True)
put("capex", "Capex", "$M", "m", val_from(kpi, "capex_musd"), sum_fy("capex"), sum_ltm("capex"), input_row=True)
put("buyb", "Share repurchases", "$M", "m", val_from(kpi, "buybacks_musd"), sum_fy("buyb"), sum_ltm("buyb"), input_row=True)
put("rsu", "RSU tax withholding (net share settlement)", "$M", "m", val_from(kpi, "rsu_tax_withholding_musd"), sum_fy("rsu"), sum_ltm("rsu"), input_row=True)
put("unearned", "Unearned fees (quarter end)", "$M", "m", val_from(kpi, "unearned_fees_musd"), input_row=True)
put("funds", "Funds held for clients (quarter end)", "$M", "m", val_from(kpi, "funds_held_for_clients_musd"), input_row=True)
put("g_unearned", "Unearned fees y/y", "%", "pct", (lambda q, col, prev: f"={col}{r('unearned')}/{prev}{r('unearned')}-1" if prev else None))
put("g_funds", "Funds held y/y", "%", "pct", (lambda q, col, prev: f"={col}{r('funds')}/{prev}{r('funds')}-1" if prev else None))

# column widths
ws.column_dimensions["A"].width = 58
ws.column_dimensions["B"].width = 6
for c in range(FIRST_COL, LAST_COL + 1):
    ws.column_dimensions[L(c)].width = 10.5
ws.column_dimensions[L(GAP)].width = 2
ws.column_dimensions[L(LAST_COL + 1)].width = 90

# ============================================================================= SHEET 2: Earnings
es = wb.create_sheet("Earnings")
es["A1"] = "ABNB earnings prints: reported vs management guidance and vs consensus, with the stock move"
es["A1"].font = Font(bold=True, size=13)
es["A2"] = ("Consensus reconstructed from dated press and vendor quotes at each print (LSEG/Refinitiv, StreetAccount, Zacks, FactSet); vendor noted. "
            "Beat / meet / miss vs consensus uses +/-0.5% (revenue, EBITDA, GBV), +/-1.0% (nights), +/-3% (EPS). "
            "Guide outcome is against the company's own range/floor/ceiling/point for that quarter, issued at the prior print. "
            "Stock moves: close-to-close on the reaction day (prints are after the close) and on an executable next-open entry.")
es["A2"].font = NOTE_FONT
es["A2"].alignment = Alignment(wrap_text=True, vertical="top")
es.merge_cells("A2:AZ2")
es.row_dimensions[2].height = 42

PRINTS = ["4Q20"] + QUARTERS  # 23 prints


def ledger_for(target: str, metrics: list[str]):
    rows = ledger[(ledger.target_period == target) & (ledger.metric.isin(metrics)) & (ledger.horizon_quarters == 1)]
    return rows


def guide_text(rows: pd.DataFrame) -> tuple[str, str]:
    """Return (guide description, outcome) for the most specific row."""
    if rows.empty:
        return "", ""
    order = {"range": 0, "floor": 1, "ceiling": 1, "point": 1, "bucket": 2, "directional": 3, "qualitative": 4}
    rows = rows.assign(_o=rows.guide_type.map(order).fillna(9)).sort_values("_o")
    g = rows.iloc[0]
    t = g.guide_type
    u = "" if pd.isna(g.unit) else str(g.unit)
    if t == "range":
        desc = f"{g.value_low:g} to {g.value_high:g} {u}"
    elif t == "floor":
        desc = f"at least {g.value_low:g} {u}"
    elif t == "ceiling":
        desc = f"at most {g.value_high:g} {u}"
    elif t == "point":
        desc = f"about {g.value_mid:g} {u}"
    elif t == "bucket":
        desc = f"{g.value_low:g} to {g.value_high:g} {u} ({g.direction})" if not pd.isna(g.value_low) else str(g.direction)
    else:
        comp = "" if pd.isna(g.comparator_value) else f" vs {g.comparator_value:g}"
        desc = f"{g.direction}{comp}"
    out = "" if pd.isna(g.outcome) else str(g.outcome)
    return desc, out


COLS = [
    ("Print", 8), ("Print date", 11), ("Reaction date", 11),
    # revenue vs guide
    ("Rev guide low", 10), ("Rev guide high", 10), ("Rev actual", 10), ("vs guide mid", 9), ("vs guide top", 9), ("Rev guide outcome", 14),
    # revenue vs consensus
    ("Rev consensus", 10), ("Rev surprise", 9), ("Rev vs Street", 9), ("Rev vendor", 12),
    # nights
    ("Nights cons (M)", 10), ("Nights actual", 10), ("Nights surprise", 9), ("Nights vs Street", 9), ("Nights guide", 26), ("Nights guide outcome", 12),
    # GBV
    ("GBV cons ($B)", 10), ("GBV actual", 9), ("GBV surprise", 9), ("GBV vs Street", 9), ("GBV guide", 22), ("GBV guide outcome", 12),
    # ADR
    ("ADR cons", 9), ("ADR actual", 9), ("ADR surprise", 9), ("ADR guide (y/y)", 22), ("ADR guide outcome", 12),
    # EBITDA / margin
    ("EBITDA cons", 10), ("EBITDA actual", 10), ("EBITDA surprise", 9), ("EBITDA vs Street", 9), ("Margin actual", 9),
    ("Margin guide", 22), ("Margin guide outcome", 12), ("Take-rate guide", 22), ("Take-rate outcome", 12),
    # EPS
    ("EPS cons", 8), ("EPS actual", 8), ("EPS basis", 24), ("EPS surprise", 9), ("EPS vs Street", 9),
    # next quarter guide vs street
    ("Next-Q rev consensus", 11), ("Next-Q guide mid", 11), ("Guide vs Street", 9),
    # stock
    ("ABNB 1d", 8), ("QQQ 1d", 8), ("Excess 1d", 8), ("ABNB 5d", 8), ("Excess 5d", 8), ("ABNB 20d", 8), ("Excess 20d", 8),
    ("Gap at open", 8), ("Open-to-close 1d", 9), ("Open entry 5d", 9), ("Open entry 20d", 9),
]
HDR_E = 4
for i, (name, width) in enumerate(COLS, start=1):
    c = es.cell(row=HDR_E, column=i, value=name)
    c.font = HDR
    c.fill = HDR_FILL
    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    es.column_dimensions[L(i)].width = width
es.row_dimensions[HDR_E].height = 32
es.freeze_panes = es.cell(row=HDR_E + 1, column=4)
CI = {name: i for i, (name, _) in enumerate(COLS, start=1)}


def cls_formula(cell_ref: str, thr: float) -> str:
    return f'=IF({cell_ref}="","",IF({cell_ref}>{thr},"beat",IF({cell_ref}<-{thr},"miss","meet")))'


rr = HDR_E + 1
FIRST_DATA = rr
for q in PRINTS:
    iso = q_to_iso(q)
    c = cons.loc[iso] if iso in cons.index else None
    x = react.loc[iso] if iso in react.index else None
    e = execr.loc[iso] if iso in execr.index else None

    def w(name, value, fmt=None, font=INPUT_FONT):
        cell = es.cell(row=rr, column=CI[name], value=v(value))
        if fmt:
            cell.number_format = FMT[fmt]
        cell.font = font
        return cell

    w("Print", q, font=BOLD)
    w("Print date", None if c is None else c.print_date)
    w("Reaction date", None if c is None else c.reaction_date)

    rev_rows = ledger_for(q, ["revenue_usd_m"])
    rev_rows = rev_rows[rev_rows.guide_type == "range"]
    if not rev_rows.empty:
        g = rev_rows.iloc[0]
        w("Rev guide low", g.value_low, "m")
        w("Rev guide high", g.value_high, "m")
        w("Rev guide outcome", g.outcome)
    A = L(CI["Rev actual"]); GL = L(CI["Rev guide low"]); GH = L(CI["Rev guide high"])
    w("Rev actual", None if c is None else c.actual_revenue_musd, "m")
    es.cell(row=rr, column=CI["vs guide mid"], value=f'=IF({GL}{rr}="","",{A}{rr}/(({GL}{rr}+{GH}{rr})/2)-1)').number_format = FMT["pct"]
    es.cell(row=rr, column=CI["vs guide top"], value=f'=IF({GH}{rr}="","",{A}{rr}/{GH}{rr}-1)').number_format = FMT["pct"]

    w("Rev consensus", None if c is None else c.cons_revenue_musd, "m")
    RC = L(CI["Rev consensus"]); RS = L(CI["Rev surprise"])
    es.cell(row=rr, column=CI["Rev surprise"], value=f'=IF({RC}{rr}="","",{A}{rr}/{RC}{rr}-1)').number_format = FMT["pct"]
    es.cell(row=rr, column=CI["Rev vs Street"], value=cls_formula(f"{RS}{rr}", 0.005))
    w("Rev vendor", None if c is None else c.cons_revenue_vendor)

    # nights
    w("Nights cons (M)", None if c is None else c.cons_nights_m, "m1")
    w("Nights actual", None if c is None else c.actual_nights_m, "m1")
    NC = L(CI["Nights cons (M)"]); NA = L(CI["Nights actual"]); NS = L(CI["Nights surprise"])
    es.cell(row=rr, column=CI["Nights surprise"], value=f'=IF({NC}{rr}="","",{NA}{rr}/{NC}{rr}-1)').number_format = FMT["pct"]
    es.cell(row=rr, column=CI["Nights vs Street"], value=cls_formula(f"{NS}{rr}", 0.01))
    d, o = guide_text(ledger_for(q, ["nights_yoy_pct", "nights_m"]))
    w("Nights guide", d); w("Nights guide outcome", o)

    # GBV
    w("GBV cons ($B)", None if c is None else c.cons_gbv_busd, "b")
    w("GBV actual", None if c is None else c.actual_gbv_busd, "b")
    GC = L(CI["GBV cons ($B)"]); GA = L(CI["GBV actual"]); GS = L(CI["GBV surprise"])
    es.cell(row=rr, column=CI["GBV surprise"], value=f'=IF({GC}{rr}="","",{GA}{rr}/{GC}{rr}-1)').number_format = FMT["pct"]
    es.cell(row=rr, column=CI["GBV vs Street"], value=cls_formula(f"{GS}{rr}", 0.005))
    d, o = guide_text(ledger_for(q, ["gbv_yoy_pct", "gbv_usd_b"]))
    w("GBV guide", d); w("GBV guide outcome", o)

    # ADR
    w("ADR cons", None if c is None else c.cons_adr, "usd")
    adr_actual = None if c is None or v(c.actual_gbv_busd) is None or v(c.actual_nights_m) is None else c.actual_gbv_busd * 1000 / c.actual_nights_m
    w("ADR actual", adr_actual, "usd", font=CALC_FONT)
    AC = L(CI["ADR cons"]); AA = L(CI["ADR actual"])
    es.cell(row=rr, column=CI["ADR surprise"], value=f'=IF({AC}{rr}="","",{AA}{rr}/{AC}{rr}-1)').number_format = FMT["pct"]
    d, o = guide_text(ledger_for(q, ["adr_yoy_pct", "adr_usd_seq"]))
    w("ADR guide (y/y)", d); w("ADR guide outcome", o)

    # EBITDA and margin
    w("EBITDA cons", None if c is None else c.cons_adj_ebitda_musd, "m")
    w("EBITDA actual", None if c is None else c.actual_adj_ebitda_musd, "m")
    EC = L(CI["EBITDA cons"]); EA = L(CI["EBITDA actual"]); ES_ = L(CI["EBITDA surprise"])
    es.cell(row=rr, column=CI["EBITDA surprise"], value=f'=IF({EC}{rr}="","",{EA}{rr}/{EC}{rr}-1)').number_format = FMT["pct"]
    es.cell(row=rr, column=CI["EBITDA vs Street"], value=cls_formula(f"{ES_}{rr}", 0.005))
    es.cell(row=rr, column=CI["Margin actual"], value=f'=IF({EA}{rr}="","",{EA}{rr}/{A}{rr})').number_format = FMT["pct"]
    d, o = guide_text(ledger_for(q, ["adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts", "adj_ebitda_usd_m"]))
    w("Margin guide", d); w("Margin guide outcome", o)
    d, o = guide_text(ledger_for(q, ["take_rate_yoy_pts", "take_rate_pct_seq"]))
    w("Take-rate guide", d); w("Take-rate outcome", o)

    # EPS
    w("EPS cons", None if c is None else c.cons_eps_usd, "usd")
    w("EPS actual", None if c is None else c.actual_eps_usd, "usd")
    w("EPS basis", None if c is None else c.eps_basis)
    PC = L(CI["EPS cons"]); PA = L(CI["EPS actual"]); PS = L(CI["EPS surprise"])
    es.cell(row=rr, column=CI["EPS surprise"], value=f'=IF(OR({PC}{rr}="",{PC}{rr}=0),"",({PA}{rr}-{PC}{rr})/ABS({PC}{rr}))').number_format = FMT["pct"]
    es.cell(row=rr, column=CI["EPS vs Street"], value=cls_formula(f"{PS}{rr}", 0.03))

    # next quarter guide vs street
    w("Next-Q rev consensus", None if c is None else c.next_q_cons_revenue_musd, "m")
    w("Next-Q guide mid", None if c is None else c.next_q_guide_mid_musd, "m")
    QC = L(CI["Next-Q rev consensus"]); QG = L(CI["Next-Q guide mid"])
    es.cell(row=rr, column=CI["Guide vs Street"], value=f'=IF(OR({QC}{rr}="",{QG}{rr}=""),"",{QG}{rr}/{QC}{rr}-1)').number_format = FMT["pct"]

    # stock
    if x is not None:
        w("ABNB 1d", x.abnb_1d_pct / 100, "pct"); w("QQQ 1d", x.qqq_1d_pct / 100, "pct"); w("Excess 1d", x.excess_1d_pct / 100, "pct")
        w("ABNB 5d", x.abnb_5d_pct / 100, "pct"); w("Excess 5d", x.excess_5d_pct / 100, "pct")
        w("ABNB 20d", x.abnb_20d_pct / 100, "pct"); w("Excess 20d", x.excess_20d_pct / 100, "pct")
    if e is not None:
        w("Gap at open", e.gap_pct / 100, "pct"); w("Open-to-close 1d", e.open_1d_pct / 100, "pct")
        w("Open entry 5d", e.open_5d_pct / 100, "pct"); w("Open entry 20d", e.open_20d_pct / 100, "pct")
    rr += 1
LAST_DATA = rr - 1
# fill any missing 20-session move from the daily price file (pre-print close to the exit date in the executable file)
prices = pd.read_csv(ROOT / "data/processed/overnight/09_prices_daily.csv").set_index("Date")
for i, q in enumerate(PRINTS):
    iso = q_to_iso(q)
    if iso in react.index and pd.isna(react.loc[iso, "abnb_20d_pct"]) and iso in execr.index:
        e = execr.loc[iso]
        d0, d1 = e.pre_close_date, e.exit_date_20d
        if d0 in prices.index and d1 in prices.index:
            a = prices.loc[d1, "ABNB"] / prices.loc[d0, "ABNB"] - 1
            qq = prices.loc[d1, "QQQ"] / prices.loc[d0, "QQQ"] - 1
            rowi = FIRST_DATA + i
            for name, val in [("ABNB 20d", a), ("Excess 20d", a - qq)]:
                cell = es.cell(row=rowi, column=CI[name], value=round(val, 4))
                cell.number_format = FMT["pct"]
                cell.font = INPUT_FONT
            es.cell(row=rowi, column=len(COLS) + 1, value=f"20-session move computed from daily closes {d0} to {d1}").font = NOTE_FONT

# summary block
rr += 2
es.cell(row=rr, column=1, value="Summary across prints").font = BOLD
for cc in range(1, len(COLS) + 1):
    es.cell(row=rr, column=cc).fill = SEC_FILL
rr += 1


def rng(name):
    return f"{L(CI[name])}{FIRST_DATA}:{L(CI[name])}{LAST_DATA}"


summ = [
    ("Prints with a numeric revenue range", f'=COUNT({rng("Rev guide low")})'),
    ("  above the range", f'=COUNTIF({rng("Rev guide outcome")},"above_range")'),
    ("  within the range", f'=COUNTIF({rng("Rev guide outcome")},"within_range")'),
    ("  below the range", f'=COUNTIF({rng("Rev guide outcome")},"below_range")'),
    ("  mean beat vs guide midpoint", f'=AVERAGE({rng("vs guide mid")})', "pct"),
    ("  median beat vs guide midpoint", f'=MEDIAN({rng("vs guide mid")})', "pct"),
    ("Revenue vs consensus: beat / meet / miss",
     f'=COUNTIF({rng("Rev vs Street")},"beat")&" / "&COUNTIF({rng("Rev vs Street")},"meet")&" / "&COUNTIF({rng("Rev vs Street")},"miss")'),
    ("  mean revenue surprise", f'=AVERAGE({rng("Rev surprise")})', "pct"),
    ("  median revenue surprise", f'=MEDIAN({rng("Rev surprise")})', "pct"),
    ("Nights vs consensus: beat / meet / miss",
     f'=COUNTIF({rng("Nights vs Street")},"beat")&" / "&COUNTIF({rng("Nights vs Street")},"meet")&" / "&COUNTIF({rng("Nights vs Street")},"miss")'),
    ("  median nights surprise", f'=MEDIAN({rng("Nights surprise")})', "pct"),
    ("GBV vs consensus: beat / meet / miss",
     f'=COUNTIF({rng("GBV vs Street")},"beat")&" / "&COUNTIF({rng("GBV vs Street")},"meet")&" / "&COUNTIF({rng("GBV vs Street")},"miss")'),
    ("EBITDA vs consensus: beat / meet / miss",
     f'=COUNTIF({rng("EBITDA vs Street")},"beat")&" / "&COUNTIF({rng("EBITDA vs Street")},"meet")&" / "&COUNTIF({rng("EBITDA vs Street")},"miss")'),
    ("EPS vs consensus: beat / meet / miss",
     f'=COUNTIF({rng("EPS vs Street")},"beat")&" / "&COUNTIF({rng("EPS vs Street")},"meet")&" / "&COUNTIF({rng("EPS vs Street")},"miss")'),
    ("Margin guide: met / not met",
     f'=COUNTIF({rng("Margin guide outcome")},"met")+COUNTIF({rng("Margin guide outcome")},"beat")+COUNTIF({rng("Margin guide outcome")},"at_point")&" / "&COUNTIF({rng("Margin guide outcome")},"not_met")+COUNTIF({rng("Margin guide outcome")},"miss")'),
    ("Guide below Street (next-quarter midpoint under consensus)", f'=COUNTIF({rng("Guide vs Street")},"<0")'),
    ("  of which 20-day excess negative",
     f'=SUMPRODUCT(({rng("Guide vs Street")}<0)*({rng("Guide vs Street")}<>"")*({rng("Excess 20d")}<0))'),
    ("Day-1 excess return: mean", f'=AVERAGE({rng("Excess 1d")})', "pct"),
    ("Day-1 excess return: positive count", f'=COUNTIF({rng("Excess 1d")},">0")&" of "&COUNT({rng("Excess 1d")})'),
    ("Day-1 absolute move: mean", f'=SUMPRODUCT(ABS({rng("ABNB 1d")}))/COUNT({rng("ABNB 1d")})', "pct"),
    ("Day-1 absolute move: median", f'=MEDIAN(INDEX(ABS({rng("ABNB 1d")}),0))', "pct"),
    ("Prints with |day-1 move| > 7%", f'=SUMPRODUCT(--(ABS({rng("ABNB 1d")})>0.07))'),
    ("20-day excess return: mean", f'=AVERAGE({rng("Excess 20d")})', "pct"),
    ("20-day excess return: positive count", f'=COUNTIF({rng("Excess 20d")},">0")&" of "&COUNT({rng("Excess 20d")})'),
    ("Open-to-close day 1 (executable): mean", f'=AVERAGE({rng("Open-to-close 1d")})', "pct"),
    ("Sum of |overnight gap| over sum of |day-1 move|", f'=SUMPRODUCT(ABS({rng("Gap at open")}))/SUMPRODUCT(ABS({rng("ABNB 1d")}))', "pct"),
]
for item in summ:
    label, formula = item[0], item[1]
    es.cell(row=rr, column=1, value=label)
    cell = es.cell(row=rr, column=4, value=formula)
    if len(item) > 2:
        cell.number_format = FMT[item[2]]
    rr += 1

# ============================================================================= SHEET 3: FY guides
fs = wb.create_sheet("FY guides")
fs["A1"] = "Full-year guidance and revisions vs actual (Adjusted EBITDA margin, revenue growth, SBC, S&M ratio)"
fs["A1"].font = Font(bold=True, size=13)
fs["A2"] = "Each row is one guide statement as issued at a print; the same target period appears once per print at which it was stated or revised."
fs["A2"].font = NOTE_FONT
hdr = ["Target", "Metric", "Issued at print", "Print date", "Guide type", "Low", "High", "Mid", "Unit", "Actual", "Outcome", "Cushion", "Quote"]
for i, h in enumerate(hdr, start=1):
    c = fs.cell(row=4, column=i, value=h)
    c.font = HDR
    c.fill = HDR_FILL
fr = 5
for _, g in fyrev.iterrows():
    vals = [g.target_period, g.metric, g.print_quarter, g.print_date, g.guide_type, v(g.value_low), v(g.value_high), v(g.value_mid),
            v(g.unit), v(g.actual), v(g.outcome), v(g.cushion), v(g.quote)]
    for i, val in enumerate(vals, start=1):
        fs.cell(row=fr, column=i, value=val)
    fr += 1
for i, wdt in enumerate([9, 26, 12, 11, 11, 8, 8, 8, 9, 9, 13, 9, 120], start=1):
    fs.column_dimensions[L(i)].width = wdt
fs.freeze_panes = "A5"

# ============================================================================= SHEET 4: Sources
ss = wb.create_sheet("Sources")
lines = [
    ("Workbook", "model/ABNB_historicals.xlsx, built by analysis/src/abnb_historicals_workbook.py. Historical only; no forecasts."),
    ("KPIs, revenue, FX splits, shares, net income", "data/processed/overnight/02_kpi_panel_quarterly.csv: 23 shareholder letters (SEC 8-K Ex. 99.1), 10-Q/10-K XBRL (CIK 1559720), call transcripts. 342 verbatim quotes re-verified."),
    ("Cost lines, SBC by line, D&A, add-backs, FCF", "data/processed/overnight/07_cost_lines_per_night.csv: GAAP lines from XBRL (Q4 = FY less 9M), SBC-by-function footnotes from each letter, Adjusted EBITDA reconciliation from each letter. Cash line = GAAP line less that line's SBC."),
    ("Management guidance", "data/processed/overnight/02_guidance_ledger.csv (194 statements) and 02_fy_guide_revisions.csv: Outlook sections of the letters, quoted verbatim, scored against the reported actual."),
    ("Consensus at each print", "data/processed/overnight/16_consensus_at_print_merged.csv: 145 dated press/vendor quotes (Yahoo, Reuters/LSEG, StreetAccount via press, Zacks, FactSet). Vendors disagree by up to 2%; vendor kept per row. EPS basis varies (GAAP before 4Q21 and for 3Q23/4Q23 one-offs)."),
    ("Stock moves", "data/processed/abnb_earnings_reactions.csv (close-to-close, reaction day = day after the after-close print; QQQ excess) and data/processed/overnight/20_executable_returns.csv (next-open entry: gap, open-to-close, 5 and 20 sessions)."),
    ("Definitions", "ADR = GBV / nights. Take rate = revenue / GBV (revenue at check-in, GBV at booking, so seasonal). FX effect = company-stated reported minus constant-currency growth. Adjusted EBITDA = operating income + SBC + D&A + other add-backs (company definition)."),
    ("Known data caveats", "1Q21 and 2Q22 cash stacks do not tie to Adjusted EBITDA (SBC footnote gaps). 4Q23 G&A cash includes the $928M Italy withholding settlement, added back in Adjusted EBITDA. ADR ex-FX before 4Q25 is approximate where the letter said 'roughly flat'. 2Q26 20-session move taken from the overnight WS09 note (reactions CSV predates it)."),
]
for i, (k, t) in enumerate(lines, start=1):
    ss.cell(row=i, column=1, value=k).font = BOLD
    ss.cell(row=i, column=2, value=t).alignment = Alignment(wrap_text=True, vertical="top")
ss.column_dimensions["A"].width = 40
ss.column_dimensions["B"].width = 140

OUT.parent.mkdir(exist_ok=True)
wb.save(OUT)
print("wrote", OUT)
