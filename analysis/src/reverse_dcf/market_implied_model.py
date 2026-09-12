"""Market-implied model for ABNB: what the price, the options market and the sell-side tape are pricing.

Krish with Claude Code, 12-13 Sep 2026.  Run with:  py -3.13 analysis/src/reverse_dcf/market_implied_model.py

Builds model/ABNB_market_implied.xlsx (formula-driven; yellow = input; blue = value carried from a workstream CSV),
recalculates it through Excel COM, reconciles the live formulas against the Python mirror below, and writes
data/processed/reverse_dcf/market/*.csv.  Reads the workstream outputs under data/processed/reverse_dcf/{A,B,C,D}/
so that repairs there flow through on a rebuild.

Method (Krish's decisions, docs/reverse_dcf/BRIEF.md):
  1. The share price is the market's fair value.  Joint solve first: the multiple is endogenous to growth (WS12,
     re-estimated by workstream A: EV/NTM EBITDA = a + b x NTM revenue growth), so EV = M(g) x EBITDA(g) is a
     quadratic in g with a closed-form root.  The fixed-multiple hold is carried alongside as the fallback.
  2. NTM growth is mapped to FY27 two ways (proportional: minus the Delivered-case NTM-to-FY27 spread; direct:
     the same quadratic on the FY26 base at the FY27 margin) and the headline is quoted as the range between them.
  3. Nights are backed out of revenue growth log-additively at ADR ex-FX +3.0%, FX -0.6pp, take rate flat.
  4. The options market (workstream B) supplies the 5 Nov event sd and the 12-month risk-neutral percentiles;
     the sell-side tape (D) the target percentiles; the reaction function (C) the expected 5 Nov move by scenario.
"""
from __future__ import annotations

import os
import json
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
OUT_XLSX = P("model", "ABNB_market_implied.xlsx")
OUT_DIR = P("data", "processed", "reverse_dcf", "market")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------------------------------------------
# Anchors (BRIEF)
# ---------------------------------------------------------------------------------------------------------------
PRICE, PRICE_DATE = 170.19, "11 Sep 2026"
SHARES, NET_CASH = 597.0, 9593.0
LTM_REV, LTM_EBITDA = 13159.0, 4617.0
LTM_MARGIN = LTM_EBITDA / LTM_REV
MG = pd.read_csv(P("data", "processed", "reverse_dcf", "mgmt_implied_summary.csv"))
def mg(case, per, col):
    return float(MG[(MG.scenario == case) & (MG.period == per)][col].iloc[0])
FY26_BASE = mg("Delivered", "FY26", "revenue_musd")
MARGIN = 36.2
DELIV_NTM_REV = mg("Delivered", "3Q26", "revenue_musd") + mg("Delivered", "4Q26", "revenue_musd") + 3003.832 + 4055.161  # 3Q26E+4Q26E+1Q27E+2Q27E
DELIV_FY27_G = (mg("Delivered", "FY27", "revenue_musd") / FY26_BASE - 1) * 100
SPREAD = (DELIV_NTM_REV / LTM_REV - 1) * 100 - DELIV_FY27_G           # NTM-to-FY27 growth spread in the Delivered case (~1.4pp)
ADR, FX, TAKE = 3.0, -0.6, 0.0
SBC27, DA_PCT, NET_INT27, TAX, SH27_AVG = mg("Delivered", "FY27", "sbc_musd"), 0.65, 516.0, 18.0, mg("Delivered", "FY27", "diluted_shares_m")
MULT_MID = 16.5
STREET_Q4_REV = 3154.0    # Bloomberg FA 4 Sep (workstream C's comparator)
STREET_2H26 = 4744.0 + (3154.0 + 3200.0) / 2   # Street 3Q26 + 4Q26 midpoint, for the chained NTM-to-FY27 mapping (workstream A)
H1_26_REV = 2678.0 + 3608.0
ACCEL_HI, ACCEL_LO = 10.6, 10.1   # C: accelerating if 3Q26 nights > 10.6%, decelerating if < 10.1% (2Q26 printed 10.34%)

# workstream outputs
A_JS = pd.read_csv(P("data", "processed", "reverse_dcf", "A", "A_joint_solve.csv"))
A_PRIMARY = A_JS[A_JS.spec.str.startswith("A. ")].iloc[0]
A_LOW = A_JS[A_JS.spec.str.startswith("A-low")].iloc[0]
A_HIGH = A_JS[A_JS.spec.str.startswith("A-high")].iloc[0]
REG_A, REG_B = float(A_PRIMARY.intercept), float(A_PRIMARY.slope_turns_per_pt)
REG_B_LO, REG_A_LO = float(A_LOW.slope_turns_per_pt), float(A_LOW.intercept)
REG_B_HI, REG_A_HI = float(A_HIGH.slope_turns_per_pt), float(A_HIGH.intercept)
A_RDCF = pd.read_csv(P("data", "processed", "reverse_dcf", "A", "A_reverse_dcf.csv"))
HAS_BAND = "implied_ntm_growth_lo_pct" in A_JS.columns   # delta-method fitted-line band added by A after the audit
_ap = A_JS[A_JS.spec.str.startswith("A. ")].copy()
A_PRIM_ALL = _ap.set_index(_ap.price_usd.round(2))
B_PP = pd.read_csv(P("data", "processed", "reverse_dcf", "B", "B_price_points_for_synthesis.csv"))
B_HEAD = pd.read_csv(P("data", "processed", "reverse_dcf", "B", "B_headline.csv")).set_index("item")["value"]
B_PCT = pd.read_csv(P("data", "processed", "reverse_dcf", "B", "B_dist_12m_percentiles.csv"))
B_SKEW = pd.read_csv(P("data", "processed", "reverse_dcf", "B", "B_skew.csv"))
B_BASE = pd.read_csv(P("data", "processed", "reverse_dcf", "B", "B_print_base_rates.csv"))
C_COEF = pd.read_csv(P("data", "processed", "reverse_dcf", "C", "C_coefficients_used.csv")).set_index("spec_id")
C_SCEN = pd.read_csv(P("data", "processed", "reverse_dcf", "C", "C_scenarios.csv"))
D_PCT = pd.read_csv(P("data", "processed", "reverse_dcf", "D", "D_tape_percentiles.csv"))
D_EST = pd.read_csv(P("data", "processed", "reverse_dcf", "D", "D_estimate_dispersion.csv"))

def bval(k):
    try:
        return float(B_HEAD[k])
    except Exception:
        return np.nan

EVENT_SD = bval("event_sd_central_pct")
EVENT_ABS = bval("event_exp_abs_move_central_pct")

# price points: brief seven plus the options-implied 12-month quartiles
PP = [(150.0, "bear tape"), (165.0, "p25 sell-side target"), (170.19, "price, close 11 Sep 2026"), (179.5, "mean sell-side target"),
      (185.0, "median yfinance target"), (197.5, "p75 sell-side target"), (220.0, "top sell-side target")]
for q in ["p25", "p50", "p75"]:
    cand = B_PP[B_PP.label.str.contains(f"12M {q}") & B_PP.label.str.contains("lognormal", case=False)]
    if not len(cand):
        cand = B_PP[B_PP.label.str.contains(f"12M {q}")]
    if len(cand):
        r = cand.iloc[0]
        PP.append((round(float(r.price_point), 2), f"options-implied 12M {q} ({'lognormal' if 'lognormal' in r.label.lower() else 'skew-adjusted RND'})"))
PP = sorted(PP)

# ---------------------------------------------------------------------------------------------------------------
# Python mirror
# ---------------------------------------------------------------------------------------------------------------
def solve_quadratic(a, b, ev, base_rev, margin_pct):
    """(a + b g)(1 + g/100) base margin = ev  ->  positive root in %."""
    m = margin_pct / 100
    c2 = b / 100
    c1 = a / 100 + b
    c0 = a - ev / (base_rev * m)
    disc = c1 * c1 - 4 * c2 * c0
    return (-c1 + np.sqrt(disc)) / (2 * c2)


def nights_from_growth(g, adr=ADR, fx=FX, take=TAKE):
    return (np.exp(np.log(1 + g / 100) - np.log(1 + adr / 100) - np.log(1 + fx / 100) - np.log(1 + take / 100)) - 1) * 100


def eps_from_rev(rev, margin_pct=MARGIN):
    return ((rev * margin_pct / 100 - SBC27 - DA_PCT / 100 * rev) + NET_INT27) * (1 - TAX / 100) / SH27_AVG


def price_from_fy27_growth(g27, a=REG_A, b=REG_B):
    g = g27 + SPREAD
    ev = (a + b * g) * LTM_REV * (1 + g / 100) * LTM_MARGIN
    return (ev + NET_CASH) / SHARES


def interp_p_above(price, col):
    d = B_PP.sort_values("price_point")
    return float(np.interp(price, d.price_point, d[col]))


def market_rows():
    rows = []
    for price, label in PP:
        ev = price * SHARES - NET_CASH
        g_ntm = solve_quadratic(REG_A, REG_B, ev, LTM_REV, LTM_MARGIN * 100)
        if HAS_BAND and round(price, 2) in A_PRIM_ALL.index:
            g_lo = float(A_PRIM_ALL.loc[round(price, 2), "implied_ntm_growth_lo_pct"]); g_hi = float(A_PRIM_ALL.loc[round(price, 2), "implied_ntm_growth_hi_pct"])
        else:
            g_lo = solve_quadratic(REG_A_LO, REG_B_LO, ev, LTM_REV, LTM_MARGIN * 100)
            g_hi = solve_quadratic(REG_A_HI, REG_B_HI, ev, LTM_REV, LTM_MARGIN * 100)
        m_ntm = REG_A + REG_B * g_ntm
        g27p = g_ntm - SPREAD
        g27d = ((LTM_REV * (1 + g_ntm / 100) - STREET_2H26) / H1_26_REV - 1) * 100   # chained through the Street's 2H26 (H1 27 growth)
        rev27 = FY26_BASE * (1 + g27p / 100)
        ebitda27 = rev27 * MARGIN / 100
        eps27 = eps_from_rev(rev27)
        n27p = nights_from_growth(g27p)
        n27d = nights_from_growth(g27d)
        g_fixed = (ev / MULT_MID / (MARGIN / 100) / FY26_BASE - 1) * 100
        rd = A_RDCF[(A_RDCF.price_usd.round(2) == round(price, 2)) & (A_RDCF.wacc_pct == 10.0) & (A_RDCF.terminal_growth_pct == 3.0)]
        rd_rep = float(rd[rd.fcf_basis.str.contains("reported")].implied_fy28_starting_fcf_growth_pct.iloc[0]) if len(rd[rd.fcf_basis.str.contains("reported")]) else np.nan
        rd_sbc = float(rd[rd.fcf_basis.str.contains("SBC")].implied_fy28_starting_fcf_growth_pct.iloc[0]) if len(rd[rd.fcf_basis.str.contains("SBC")]) else np.nan
        rows.append(dict(price=price, label=label, ev=ev, g_ntm=g_ntm, g_ntm_lo=min(g_lo, g_hi), g_ntm_hi=max(g_lo, g_hi), m_ntm=m_ntm, g27_prop=g27p, g27_direct=g27d,
                         rev27=rev27, ebitda27=ebitda27, eps27=eps27, ev_fy27_ebitda=ev / ebitda27, nights27_prop=n27p, nights27_direct=n27d,
                         g27_fixed=g_fixed, nights27_fixed=nights_from_growth(g_fixed),
                         p_above_12m=interp_p_above(price, "p_above_12m_skew_rnd"), p_above_20nov=interp_p_above(price, "p_above_20nov_rnd"),
                         rdcf_reported=rd_rep, rdcf_sbc=rd_sbc))
    return pd.DataFrame(rows)


CASES = [
    ("Management literal", (mg("Literal", "FY27", "revenue_musd") / FY26_BASE - 1) * 100, mg("Literal", "FY27", "adj_ebitda_musd")),
    ("Management delivered", DELIV_FY27_G, mg("Delivered", "FY27", "adj_ebitda_musd")),
    ("Management ambition", (mg("Ambition", "FY27", "revenue_musd") / FY26_BASE - 1) * 100, mg("Ambition", "FY27", "adj_ebitda_musd")),
    ("Street FY27 $15,745m", (15745.0 / FY26_BASE - 1) * 100, 15745.0 * MARGIN / 100),
    ("Team base (WS29/30) $15,804m", (15803.69 / FY26_BASE - 1) * 100, 5757.93),
    ("Team bear (WS29) $14,318m", (14318.33 / FY26_BASE - 1) * 100, 4375.0),
    ("Team bull (WS29) $16,910m", (16909.76 / FY26_BASE - 1) * 100, 6977.35),
]


def case_rows():
    rows = []
    for name, g27, ebitda in CASES:
        pj = price_from_fy27_growth(g27)
        pf = (MULT_MID * FY26_BASE * (1 + g27 / 100) * MARGIN / 100 + NET_CASH) / SHARES
        pf_own = (MULT_MID * ebitda + NET_CASH) / SHARES
        rows.append(dict(case=name, fy27_growth=g27, fy27_ebitda_own=ebitda, price_joint=pj, upside_joint=(pj / PRICE - 1) * 100, price_fixed_16_5=pf, price_fixed_own_ebitda=pf_own,
                         nights27=nights_from_growth(g27), p_above_12m=interp_p_above(pj, "p_above_12m_skew_rnd")))
    return pd.DataFrame(rows)


def reaction(spec, sign, gvs):
    c = C_COEF.loc[spec]
    return float(c.c + c.b_sign * sign + c.b_gvs * gvs)


PRINT_SCEN = [
    # name, 3Q26 nights %, 4Q26 revenue guide midpoint $M
    ("Team base (WS29/30)", 9.9, 3111.0),
    ("Team base, ex-NA lap adopted", 9.9, 3055.0),
    ("Q3 nowcast central (reviews index), 4Q26 at team revenue", 9.75, 3107.0),
    ("Street (Bloomberg FA 4 Sep)", 11.1, 3154.0),
    ("Management delivered", 11.5, 3130.0),
    ("Flat print: 3Q26 = 2Q26 rate, guide at Street", 10.34, 3154.0),
    ("Accelerating print, guide 2% below Street", 11.0, 3091.0),
    ("Decelerating print, guide 3% above Street", 9.9, 3249.0),
    ("2Q26 replay: accelerating print, guide +2.6% vs Street", 11.0, 3236.0),
]


def sign_of(n):
    return 1.0 if n > ACCEL_HI else (-1.0 if n < ACCEL_LO else 0.0)


def print_rows():
    rows = []
    for name, n, q4 in PRINT_SCEN:
        s = sign_of(n); gvs = (q4 / STREET_Q4_REV - 1) * 100
        rows.append(dict(scenario=name, nights_3q26=n, accel_sign=s, rev_guide_4q26=q4, guide_vs_street_pct=gvs,
                         E_S2_ex_reopening=reaction("S2_ex_reopening", s, gvs), E_S1_post2022=reaction("S1_post2022", s, 0.0),
                         E_S2_post2022=reaction("S2_post2022", s, gvs)))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------------------------------------------
YELLOW = PatternFill("solid", fgColor="FFF2CC"); HDR = PatternFill("solid", fgColor="D9E1F2")
BLUE = Font(color="0000FF"); BOLD = Font(bold=True); GREY = Font(color="808080", italic=True)


def hdr(ws, r, labels, c0=1):
    for j, h in enumerate(labels):
        c = ws.cell(row=r, column=c0 + j, value=h); c.font = BOLD; c.fill = HDR; c.alignment = Alignment(wrap_text=True, vertical="top")


def build(mkt, cases, prt):
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    # ---------------- Cover
    ws = wb.create_sheet("Cover")
    ws["A1"] = "ABNB: the market-implied model"; ws["A1"].font = Font(bold=True, size=14)
    lines = [
        f"Built 13 Sep 2026 by analysis/src/reverse_dcf/market_implied_model.py from the workstream outputs under data/processed/reverse_dcf/A-D. Rebuild: py -3.13 analysis/src/reverse_dcf/market_implied_model.py",
        "Question: what do the share price, the options market and the sell-side tape imply for FY27 revenue growth, EBITDA and nights, and for the 5 Nov print, against management's cases and the team's forecasts?",
        "Inputs        - anchors, the multiple-vs-growth regression (workstream A), decomposition assumptions, EPS map, reaction coefficients (C), options numbers (B). Yellow = editable.",
        "Market_Implied- one row per price point: the joint solve (closed-form quadratic), both FY27 mappings, implied nights, the fixed-multiple fallback, options probabilities, reverse-DCF growth.",
        "Cases         - management literal / delivered / ambition, Street, team base / bear / bull: the price each is worth on the joint solve and at 16.5x, and the options-implied probability of reaching it.",
        "Print_5Nov    - the reaction function (C) applied to print scenarios; the breakeven guide; the options-implied event sd (B).",
        "SellSide      - the target tape percentiles (D) and what each requires at 16.5x.",
        "Options       - B's headline numbers, 12-month percentiles, skew by expiry, print base rates.",
        "Comparison    - the one table: what is priced by whom.",
        "Recon         - Excel recalculated values vs the Python mirror (must be ~0).",
        "Labels: ANCHOR = brief; MEASURED = computed by a workstream; JUDGEMENT = analyst choice. Blue cells are values carried from workstream CSVs; black cells are live formulas.",
    ]
    for i, t in enumerate(lines):
        ws[f"A{3+i}"] = t
    ws.column_dimensions["A"].width = 170
    # ---------------- Inputs
    wi = wb.create_sheet("Inputs")
    wi["A1"] = "Inputs"; wi["A1"].font = Font(bold=True, size=13)
    IN = {}
    items = [
        ("price", "Share price ($)", PRICE, f"close {PRICE_DATE}; ANCHOR"),
        ("shares", "Diluted shares (M)", SHARES, "2Q26 diluted WA; ANCHOR"),
        ("netcash", "Net cash ex float ($M)", NET_CASH, "30 Jun 2026; ANCHOR"),
        ("ltm_rev", "LTM revenue, 3Q25-2Q26 ($M)", LTM_REV, "letters; the base the NTM multiple was fitted on"),
        ("ltm_margin", "LTM adj. EBITDA margin (%)", LTM_MARGIN * 100, "4,617 / 13,159"),
        ("fy26_base", "FY26E revenue base ($M)", FY26_BASE, "management Delivered case (BRIEF)"),
        ("margin", "FY27E adj. EBITDA margin (%)", MARGIN, "management Delivered case; 35.5 / 37.0 sensitivities"),
        ("reg_a", "Multiple regression intercept a (EV/NTM EBITDA, x)", REG_A, "workstream A primary: EV/NTM EBITDA on NTM growth proxy, 2023-26 monthly, n 45, R2 0.23, NW t 3.1; MEASURED"),
        ("reg_b", "Multiple regression slope b (turns per pt of NTM growth)", REG_B, "same; +0.40 vs WS12's +0.48 on the LTM multiple; weakly identified (see audit_A)"),
        ("reg_a_lo", "Slope band: intercept at b - 1 s.e.", REG_A_LO, "line rotated about the sample means"),
        ("reg_b_lo", "Slope band: b - 1 s.e.", REG_B_LO, ""),
        ("reg_a_hi", "Slope band: intercept at b + 1 s.e.", REG_A_HI, ""),
        ("reg_b_hi", "Slope band: b + 1 s.e.", REG_B_HI, ""),
        ("spread", "NTM-to-FY27 growth spread (pp)", SPREAD, "Delivered case: NTM growth 14.0% less FY27 12.6%; used by the proportional mapping"),
        ("adr", "FY27 ADR ex-FX growth (%)", ADR, "management: mix and price appreciation; team H note"),
        ("fx", "FY27 revenue FX after hedging (pp)", FX, "WS29 consensus EUR path"),
        ("take", "FY27 take-rate change (%)", TAKE, "management: flat"),
        ("mult_mid", "Fixed-multiple fallback: EV / FY27E EBITDA (x)", MULT_MID, "WS12 mid"),
        ("sbc27", "FY27E SBC ($M)", SBC27, "Delivered case; EPS map"),
        ("da_pct", "D&A (% revenue)", DA_PCT, "EPS map"),
        ("netint27", "FY27E net interest income ($M)", NET_INT27, "4 x 160 - 4 x 31"),
        ("tax", "Effective tax rate (%)", TAX, "high teens"),
        ("sh27", "FY27E average diluted shares (M)", SH27_AVG, "Delivered case"),
        ("street_q4", "Street 4Q26 revenue comparator ($M)", STREET_Q4_REV, "Bloomberg FA 4 Sep; Zacks $3,200m alternative"),
        ("accel_hi", "3Q26 nights growth above which the print is 'accelerating' (%)", ACCEL_HI, "workstream C threshold (2Q26 printed 10.34%)"),
        ("accel_lo", "3Q26 nights growth below which the print is 'decelerating' (%)", ACCEL_LO, "workstream C threshold"),
        ("c_S2", "Reaction S2 (ex-reopening, n 16): intercept (%)", float(C_COEF.loc["S2_ex_reopening", "c"]), "C: E[r] = c + b_sign x sign(accel) + b_gvs x guide-vs-Street %; post-hoc spec, LOO R2 0.22"),
        ("bs_S2", "Reaction S2: b_sign (% per unit sign)", float(C_COEF.loc["S2_ex_reopening", "b_sign"]), ""),
        ("bg_S2", "Reaction S2: b_gvs (% per 1% guide vs Street)", float(C_COEF.loc["S2_ex_reopening", "b_gvs"]), ""),
        ("c_S1", "Reaction S1 (post-2022 sign rule, n 14): intercept (%)", float(C_COEF.loc["S1_post2022", "c"]), "C: pre-stated sign rule; LOO R2 0.28, perm p 0.013"),
        ("bs_S1", "Reaction S1: b_sign (% per unit sign)", float(C_COEF.loc["S1_post2022", "b_sign"]), ""),
        ("event_sd", "Options-implied 5 Nov event sd (%)", EVENT_SD, "B central reading (8.3 to 11.0 across specs); JUDGEMENT"),
        ("event_abs", "Options-implied expected absolute 5 Nov move (%)", EVENT_ABS, "0.80 x sd"),
    ]
    hdr(wi, 3, ["Item", "Value", "Source / label"])
    for i, (k, lab, v, src) in enumerate(items):
        r = 4 + i; IN[k] = f"Inputs!$B${r}"
        wi[f"A{r}"] = lab; wi[f"B{r}"] = float(v); wi[f"B{r}"].fill = YELLOW; wi[f"C{r}"] = src; wi[f"C{r}"].font = GREY
    wi.column_dimensions["A"].width = 70; wi.column_dimensions["B"].width = 14; wi.column_dimensions["C"].width = 120
    # ---------------- Market_Implied
    wm = wb.create_sheet("Market_Implied")
    wm["A1"] = "Market-implied operating case by price point (joint solve: EV = (a + b g) x base x (1 + g/100) x margin, closed-form root)"; wm["A1"].font = Font(bold=True, size=13)
    wm["A2"] = "Black = live formula. Blue = value carried from a workstream CSV (band from A's delta-method fit, options probabilities from B, reverse-DCF growth from A). The solve identifies NTM growth (guide-proxy units, about 1pp above realised); FY27 is quoted as the range between the proportional and the chained mappings. Rows away from the price are JUDGEMENT (mapping-dependent)."; wm["A2"].font = GREY
    cols = ["Price ($)", "Label", "Market cap ($M)", "EV ($M)", "Implied NTM revenue growth (%)", "NTM growth, fitted-line band low (%)", "NTM growth, fitted-line band high (%)", "Implied EV/NTM EBITDA (x)",
            "FY27 growth, proportional (%)", "FY27 growth, chained through Street 2H26 (%)", "FY27 revenue, proportional ($M)", "FY27 adj. EBITDA ($M)", "FY27 GAAP EPS ($)", "Implied EV/FY27 EBITDA (x)",
            "FY27 nights growth, proportional (%)", "FY27 nights growth, chained (%)", "Fixed 16.5x: FY27 growth (%)", "Fixed 16.5x: nights (%)",
            "P(price above this in 12M, options RN)", "P(above at 20 Nov, options RN)", "Reverse DCF FY28 growth, reported FCF (%)", "Reverse DCF, SBC-adj FCF (%)"]
    hdr(wm, 4, cols)
    r0 = 5
    for i, row in mkt.iterrows():
        r = r0 + i
        wm.cell(row=r, column=1, value=float(row.price)).fill = YELLOW
        wm.cell(row=r, column=2, value=row.label)
        wm.cell(row=r, column=3, value=f"=A{r}*{IN['shares']}")
        wm.cell(row=r, column=4, value=f"=C{r}-{IN['netcash']}")
        # quadratic: c2 = b/100 ; c1 = a/100 + b ; c0 = a - EV/(base*m) ; g = (-c1 + sqrt(c1^2 - 4 c2 c0)) / (2 c2)
        def quad(a, b, ev, base, m):
            return f"=(-({a}/100+{b})+SQRT(({a}/100+{b})^2-4*({b}/100)*({a}-{ev}/({base}*{m}/100))))/(2*({b}/100))"
        wm.cell(row=r, column=5, value=quad(IN['reg_a'], IN['reg_b'], f"D{r}", IN['ltm_rev'], IN['ltm_margin']))
        if HAS_BAND:
            wm.cell(row=r, column=6, value=round(float(row.g_ntm_lo), 4)).font = BLUE
            wm.cell(row=r, column=7, value=round(float(row.g_ntm_hi), 4)).font = BLUE
        else:
            wm.cell(row=r, column=6, value=f"=MIN({quad(IN['reg_a_lo'], IN['reg_b_lo'], f'D{r}', IN['ltm_rev'], IN['ltm_margin'])[1:]},{quad(IN['reg_a_hi'], IN['reg_b_hi'], f'D{r}', IN['ltm_rev'], IN['ltm_margin'])[1:]})")
            wm.cell(row=r, column=7, value=f"=MAX({quad(IN['reg_a_lo'], IN['reg_b_lo'], f'D{r}', IN['ltm_rev'], IN['ltm_margin'])[1:]},{quad(IN['reg_a_hi'], IN['reg_b_hi'], f'D{r}', IN['ltm_rev'], IN['ltm_margin'])[1:]})")
        wm.cell(row=r, column=8, value=f"={IN['reg_a']}+{IN['reg_b']}*E{r}")
        wm.cell(row=r, column=9, value=f"=E{r}-{IN['spread']}")
        wm.cell(row=r, column=10, value=f"=(({IN['ltm_rev']}*(1+E{r}/100)-{STREET_2H26})/{H1_26_REV}-1)*100")
        wm.cell(row=r, column=11, value=f"={IN['fy26_base']}*(1+I{r}/100)")
        wm.cell(row=r, column=12, value=f"=K{r}*{IN['margin']}/100")
        wm.cell(row=r, column=13, value=f"=((L{r}-{IN['sbc27']}-{IN['da_pct']}/100*K{r})+{IN['netint27']})*(1-{IN['tax']}/100)/{IN['sh27']}")
        wm.cell(row=r, column=14, value=f"=D{r}/L{r}")
        nights = lambda gcell: f"=(EXP(LN(1+{gcell}/100)-LN(1+{IN['adr']}/100)-LN(1+{IN['fx']}/100)-LN(1+{IN['take']}/100))-1)*100"
        wm.cell(row=r, column=15, value=nights(f"I{r}"))
        wm.cell(row=r, column=16, value=nights(f"J{r}"))
        wm.cell(row=r, column=17, value=f"=(D{r}/{IN['mult_mid']}/({IN['margin']}/100)/{IN['fy26_base']}-1)*100")
        wm.cell(row=r, column=18, value=nights(f"Q{r}"))
        for j, k in [(19, "p_above_12m"), (20, "p_above_20nov"), (21, "rdcf_reported"), (22, "rdcf_sbc")]:
            c = wm.cell(row=r, column=j, value=(None if pd.isna(row[k]) else round(float(row[k]), 4))); c.font = BLUE
        for j in range(3, 23):
            wm.cell(row=r, column=j).number_format = "#,##0" if j in (3, 4, 11, 12) else ("0.00" if j in (13, 19, 20) else "0.0")
    wm.column_dimensions["A"].width = 10; wm.column_dimensions["B"].width = 34
    for j in range(3, 23):
        wm.column_dimensions[get_column_letter(j)].width = 14
    wm.row_dimensions[4].height = 60
    MROW = {round(p, 2): r0 + i for i, (p, _) in enumerate(PP)}
    # ---------------- Cases
    wc = wb.create_sheet("Cases")
    wc["A1"] = "What each case is worth on the market's own pricing rule, and the options-implied probability of getting there"; wc["A1"].font = Font(bold=True, size=13)
    wc["A2"] = "Joint-solve price = ((a + b g_ntm) x LTM revenue x (1 + g_ntm/100) x LTM margin + net cash) / shares with g_ntm = FY27 growth + spread. Fixed = 16.5x on the case's revenue at 36.2% (and on its own EBITDA)."; wc["A2"].font = GREY
    hdr(wc, 4, ["Case", "FY27 revenue growth on FY26 Delivered base (%)", "FY27 EBITDA, case's own ($M)", "Price on the joint solve ($)", "Upside vs price (%)", "Price at 16.5x, case revenue at 36.2% ($)", "Price at 16.5x, case's own EBITDA ($)", "Implied FY27 nights growth (%)", "P(above joint-solve price in 12M, options RN)"])
    for i, row in cases.iterrows():
        r = 5 + i
        wc.cell(row=r, column=1, value=row.case)
        wc.cell(row=r, column=2, value=round(float(row.fy27_growth), 4)).fill = YELLOW
        wc.cell(row=r, column=3, value=round(float(row.fy27_ebitda_own), 1)).fill = YELLOW
        g = f"(B{r}+{IN['spread']})"
        wc.cell(row=r, column=4, value=f"=(({IN['reg_a']}+{IN['reg_b']}*{g})*{IN['ltm_rev']}*(1+{g}/100)*{IN['ltm_margin']}/100+{IN['netcash']})/{IN['shares']}")
        wc.cell(row=r, column=5, value=f"=(D{r}/{IN['price']}-1)*100")
        wc.cell(row=r, column=6, value=f"=({IN['mult_mid']}*{IN['fy26_base']}*(1+B{r}/100)*{IN['margin']}/100+{IN['netcash']})/{IN['shares']}")
        wc.cell(row=r, column=7, value=f"=({IN['mult_mid']}*C{r}+{IN['netcash']})/{IN['shares']}")
        wc.cell(row=r, column=8, value=f"=(EXP(LN(1+B{r}/100)-LN(1+{IN['adr']}/100)-LN(1+{IN['fx']}/100)-LN(1+{IN['take']}/100))-1)*100")
        c = wc.cell(row=r, column=9, value=round(float(row.p_above_12m), 3)); c.font = BLUE
        for j in range(2, 10):
            wc.cell(row=r, column=j).number_format = "#,##0" if j == 3 else ("0.00" if j == 9 else "0.0")
    wc.column_dimensions["A"].width = 34
    for j in range(2, 10):
        wc.column_dimensions[get_column_letter(j)].width = 18
    wc.row_dimensions[4].height = 60
    # ---------------- Print_5Nov
    wp = wb.create_sheet("Print_5Nov")
    wp["A1"] = "5 Nov 2026 print: expected day-1 excess reaction by scenario (workstream C's function) and the options-implied dispersion (B)"; wp["A1"].font = Font(bold=True, size=13)
    wp["A2"] = "Headline = S1, the pre-stated printed-nights-acceleration sign rule (post-2022, n 14; QQQ-excess close-to-close; a base rate, not multiplicity-robust). S2 (two-variable, post-hoc, n 16) is illustrative and flips sign with the Zacks $3,200m comparator. Expectations are conditional on the print's acceleration sign; unconditional under the nowcast band is about -2 to -2.5%. Decelerating prints gap about -5% and recover about +1.7% intraday, so the move is close-to-close and captured only by holding through the print."; wp["A2"].font = GREY
    hdr(wp, 4, ["Scenario", "3Q26 nights growth (%)", "Acceleration sign", "4Q26 revenue guide midpoint ($M)", "Guide vs Street (%)", "E[day-1 excess return], S2 ex-reopening, illustrative (%)", "HEADLINE E[...], S1 post-2022 sign rule (%)", "E[...], S2 post-2022, illustrative (%)", "Options-implied event sd (%)", "Breakeven guide vs Street for zero E[r], S2 (%)", "Breakeven 4Q26 guide ($M)"])
    for i, row in prt.iterrows():
        r = 5 + i
        wp.cell(row=r, column=1, value=row.scenario)
        wp.cell(row=r, column=2, value=float(row.nights_3q26)).fill = YELLOW
        wp.cell(row=r, column=3, value=f"=IF(B{r}>{IN['accel_hi']},1,IF(B{r}<{IN['accel_lo']},-1,0))")
        wp.cell(row=r, column=4, value=float(row.rev_guide_4q26)).fill = YELLOW
        wp.cell(row=r, column=5, value=f"=(D{r}/{IN['street_q4']}-1)*100")
        wp.cell(row=r, column=6, value=f"={IN['c_S2']}+{IN['bs_S2']}*C{r}+{IN['bg_S2']}*E{r}")
        wp.cell(row=r, column=7, value=f"={IN['c_S1']}+{IN['bs_S1']}*C{r}")
        c2p, bs2p, bg2p = [float(C_COEF.loc["S2_post2022", k]) for k in ("c", "b_sign", "b_gvs")]
        wp.cell(row=r, column=8, value=f"={c2p}+{bs2p}*C{r}+{bg2p}*E{r}")
        wp.cell(row=r, column=9, value=f"={IN['event_sd']}")
        wp.cell(row=r, column=10, value=f"=-({IN['c_S2']}+{IN['bs_S2']}*C{r})/{IN['bg_S2']}")
        wp.cell(row=r, column=11, value=f"={IN['street_q4']}*(1+J{r}/100)")
        for j in range(2, 12):
            wp.cell(row=r, column=j).number_format = "#,##0" if j in (4, 11) else "0.0"
    wp.column_dimensions["A"].width = 52
    for j in range(2, 12):
        wp.column_dimensions[get_column_letter(j)].width = 16
    wp.row_dimensions[4].height = 75
    # ---------------- SellSide
    wsd = wb.create_sheet("SellSide")
    wsd["A1"] = "Sell-side tape (workstream D, 12 Sep 2026 pull, Goldman corrected to Neutral $165) and what each level requires at the fixed multiple"; wsd["A1"].font = Font(bold=True, size=13)
    d = D_PCT[D_PCT.tape.str.contains("Goldman corrected")].copy()
    d = d[d.stat.isin(["min", "p25", "median", "mean", "p75", "max"])]
    hdr(wsd, 3, ["Stat", "Target ($)", "Upside vs price (%)", "Implied EV / FY27 Delivered EBITDA (x)", "At 16.5x: required FY27 revenue ($M)", "At 16.5x: FY27 growth (%)", "At 16.5x: FY27 nights growth (%)", "Joint solve: FY27 growth, proportional (%)"])
    for i, row in enumerate(d.itertuples(index=False)):
        r = 4 + i
        wsd.cell(row=r, column=1, value=row.stat); wsd.cell(row=r, column=2, value=float(row.target)).font = BLUE
        wsd.cell(row=r, column=3, value=f"=(B{r}/{IN['price']}-1)*100")
        wsd.cell(row=r, column=4, value=f"=(B{r}*{IN['shares']}-{IN['netcash']})/{mg('Delivered','FY27','adj_ebitda_musd'):.3f}")
        wsd.cell(row=r, column=5, value=f"=(B{r}*{IN['shares']}-{IN['netcash']})/{IN['mult_mid']}/({IN['margin']}/100)")
        wsd.cell(row=r, column=6, value=f"=(E{r}/{IN['fy26_base']}-1)*100")
        wsd.cell(row=r, column=7, value=f"=(EXP(LN(1+F{r}/100)-LN(1+{IN['adr']}/100)-LN(1+{IN['fx']}/100)-LN(1+{IN['take']}/100))-1)*100")
        ev = f"(B{r}*{IN['shares']}-{IN['netcash']})"
        wsd.cell(row=r, column=8, value=f"=(-({IN['reg_a']}/100+{IN['reg_b']})+SQRT(({IN['reg_a']}/100+{IN['reg_b']})^2-4*({IN['reg_b']}/100)*({IN['reg_a']}-{ev}/({IN['ltm_rev']}*{IN['ltm_margin']}/100))))/(2*({IN['reg_b']}/100))-{IN['spread']}")
        for j in range(2, 9):
            wsd.cell(row=r, column=j).number_format = "#,##0" if j == 5 else "0.0"
    r = 4 + len(d) + 2
    wsd.cell(row=r, column=1, value="Estimate dispersion (Zacks FY27, 13 estimates), on the Delivered FY26 base").font = BOLD
    hdr(wsd, r + 1, ["Estimate", "FY27 revenue ($M)", "FY27 growth (%)", "Implied nights growth (%)", "Joint-solve price ($)"])
    e = D_EST[(D_EST.metric.str.startswith("FY27 revenue")) & (D_EST.base.str.contains("delivered"))]
    for i, row in enumerate(e.itertuples(index=False)):
        rr = r + 2 + i
        wsd.cell(row=rr, column=1, value=row.estimate); wsd.cell(row=rr, column=2, value=float(row.value)).font = BLUE
        wsd.cell(row=rr, column=3, value=f"=(B{rr}/{IN['fy26_base']}-1)*100")
        wsd.cell(row=rr, column=4, value=f"=(EXP(LN(1+C{rr}/100)-LN(1+{IN['adr']}/100)-LN(1+{IN['fx']}/100)-LN(1+{IN['take']}/100))-1)*100")
        g = f"(C{rr}+{IN['spread']})"
        wsd.cell(row=rr, column=5, value=f"=(({IN['reg_a']}+{IN['reg_b']}*{g})*{IN['ltm_rev']}*(1+{g}/100)*{IN['ltm_margin']}/100+{IN['netcash']})/{IN['shares']}")
        for j in range(2, 6):
            wsd.cell(row=rr, column=j).number_format = "#,##0" if j == 2 else "0.0"
    wsd.column_dimensions["A"].width = 16
    for j in range(2, 9):
        wsd.column_dimensions[get_column_letter(j)].width = 20
    wsd.row_dimensions[3].height = 60
    # ---------------- Options
    wo = wb.create_sheet("Options")
    wo["A1"] = "Options market (workstream B; live chain 11 Sep close, Bloomberg 4 Sep for history). Values carried from B's CSVs."; wo["A1"].font = Font(bold=True, size=13)
    hdr(wo, 3, ["Item", "Value", "Label", "Note"])
    bh = pd.read_csv(P("data", "processed", "reverse_dcf", "B", "B_headline.csv"))
    for i, row in enumerate(bh.itertuples(index=False)):
        r = 4 + i
        wo.cell(row=r, column=1, value=row.item); v = row.value
        try:
            v = float(v)
        except Exception:
            pass
        wo.cell(row=r, column=2, value=v).font = BLUE; wo.cell(row=r, column=3, value=row.label); wo.cell(row=r, column=4, value=row.note).font = GREY
    r = 4 + len(bh) + 2
    wo.cell(row=r, column=1, value="12-month price distribution (risk-neutral)").font = BOLD
    hdr(wo, r + 1, list(B_PCT.columns))
    for i, row in enumerate(B_PCT.itertuples(index=False)):
        for j, v in enumerate(row):
            wo.cell(row=r + 2 + i, column=1 + j, value=v).font = BLUE
    r = r + 2 + len(B_PCT) + 2
    wo.cell(row=r, column=1, value="Skew by expiry").font = BOLD
    sk = B_SKEW[[c for c in ["expiry", "days", "F", "atm_iv_pct", "rr25_call_minus_put_volpts", "skew_90_110_volpts", "call10_over_put10_model", "call10_over_put10_flat_smile_benchmark", "p_above_spot_rnd"] if c in B_SKEW.columns]]
    hdr(wo, r + 1, list(sk.columns))
    for i, row in enumerate(sk.itertuples(index=False)):
        for j, v in enumerate(row):
            wo.cell(row=r + 2 + i, column=1 + j, value=v).font = BLUE
    r = r + 2 + len(sk) + 2
    wo.cell(row=r, column=1, value="Print-day base rates (close before the print to close after; 23 prints 4Q20-2Q26)").font = BOLD
    bb = B_BASE[[c for c in B_BASE.columns if any(k in c for k in ("sample", "n", "mean_abs", "median_abs", "rms", "mean_signed", "share_abs_ge_7", "n_up", "n_down", "mean_up", "mean_down", "convention", "series"))]]
    hdr(wo, r + 1, list(bb.columns))
    for i, row in enumerate(bb.itertuples(index=False)):
        for j, v in enumerate(row):
            wo.cell(row=r + 2 + i, column=1 + j, value=v).font = BLUE
    wo.column_dimensions["A"].width = 44; wo.column_dimensions["B"].width = 16; wo.column_dimensions["C"].width = 12; wo.column_dimensions["D"].width = 90
    # ---------------- Comparison
    wq = wb.create_sheet("Comparison")
    wq["A1"] = "What is priced, by whom (FY27E, on the FY26 Delivered base; nights at ADR +3%, FX -0.6pp, take rate flat)"; wq["A1"].font = Font(bold=True, size=13)
    hdr(wq, 3, ["Who / what", "Price ($)", "FY27 revenue growth (%)", "FY27 revenue ($M)", "FY27 adj. EBITDA ($M)", "FY27 nights growth (%)", "Implied EV / FY27 EBITDA (x)", "P(price above this in 12M, options RN)", "Expected 5 Nov day-1 reaction, S1 sign rule, conditional (%)", "Source"])
    pr = MROW[round(PRICE, 2)]
    rows = []
    rows.append(("Market: current price (joint solve, proportional mapping)", f"=Market_Implied!A{pr}", f"=Market_Implied!I{pr}", f"=Market_Implied!K{pr}", f"=Market_Implied!L{pr}", f"=Market_Implied!O{pr}", f"=Market_Implied!N{pr}", f"=Market_Implied!S{pr}", None, "A"))
    rows.append(("Market: current price (joint solve, chained mapping)", f"=Market_Implied!A{pr}", f"=Market_Implied!J{pr}", f"={IN['fy26_base']}*(1+C5/100)", f"=D5*{IN['margin']}/100", f"=Market_Implied!P{pr}", f"=Market_Implied!D{pr}/E5", f"=Market_Implied!S{pr}", None, "A"))
    rows.append(("Market: current price (fixed 16.5x)", f"=Market_Implied!A{pr}", f"=Market_Implied!Q{pr}", f"={IN['fy26_base']}*(1+C6/100)", f"=D6*{IN['margin']}/100", f"=Market_Implied!R{pr}", f"={IN['mult_mid']}", f"=Market_Implied!S{pr}", None, "A fallback"))
    for lab, key in [("Options: 12M p25", "p25"), ("Options: 12M p50", "p50"), ("Options: 12M p75", "p75")]:
        pp_ = [p for p, l in PP if l.startswith("options-implied") and key in l]
        if pp_:
            rr = MROW[round(pp_[0], 2)]
            rows.append((lab + " (joint solve)", f"=Market_Implied!A{rr}", f"=Market_Implied!I{rr}", f"=Market_Implied!K{rr}", f"=Market_Implied!L{rr}", f"=Market_Implied!O{rr}", f"=Market_Implied!N{rr}", f"=Market_Implied!S{rr}", None, "B + A"))
    for lab, p in [("Sell-side: p25 target $165", 165.0), ("Sell-side: mean target $179.5", 179.5), ("Sell-side: p75 target $197.5", 197.5), ("Sell-side: top target $220", 220.0)]:
        rr = MROW[round(p, 2)]
        rows.append((lab + " (joint solve)", f"=Market_Implied!A{rr}", f"=Market_Implied!I{rr}", f"=Market_Implied!K{rr}", f"=Market_Implied!L{rr}", f"=Market_Implied!O{rr}", f"=Market_Implied!N{rr}", f"=Market_Implied!S{rr}", None, "D + A"))
    prt_map = {"Management literal": None, "Management delivered": "Management delivered", "Management ambition": None, "Street FY27 $15,745m": "Street (Bloomberg FA 4 Sep)", "Team base (WS29/30) $15,804m": "Team base (WS29/30)"}
    for i, (name, g27, eb) in enumerate(CASES):
        cr = 5 + i
        e_cell = None
        if prt_map.get(name):
            pri = 5 + [s_[0] for s_ in PRINT_SCEN].index(prt_map[name]); e_cell = f"=Print_5Nov!G{pri}"
        rows.append((name, f"=Cases!D{cr}", f"=Cases!B{cr}", f"={IN['fy26_base']}*(1+Cases!B{cr}/100)", f"=Cases!C{cr}", f"=Cases!H{cr}", f"=(Cases!D{cr}*{IN['shares']}-{IN['netcash']})/Cases!C{cr}", f"=Cases!I{cr}", e_cell, "management note / WS29 / A"))
    for i, row in enumerate(rows):
        r = 4 + i
        for j, v in enumerate(row):
            c = wq.cell(row=r, column=1 + j, value=v)
            if j in (1, 2, 5, 6, 8):
                c.number_format = "0.0"
            if j in (3, 4):
                c.number_format = "#,##0"
            if j == 7:
                c.number_format = "0.00"
    wq.column_dimensions["A"].width = 56
    for j in range(2, 11):
        wq.column_dimensions[get_column_letter(j)].width = 17
    wq.row_dimensions[3].height = 60
    wb.create_sheet("Recon")
    wb.save(OUT_XLSX)
    return MROW


def excel_recalc():
    import time, pythoncom
    import win32com.client as w
    for attempt in range(5):
        try:
            pythoncom.CoInitialize()
            app = w.DispatchEx("Excel.Application"); app.DisplayAlerts = False
            wbx = app.Workbooks.Open(os.path.abspath(OUT_XLSX)); app.CalculateFullRebuild(); wbx.Save(); wbx.Close(False); app.Quit()
            del wbx, app; pythoncom.CoUninitialize(); time.sleep(1.0); return
        except Exception as e:
            print("excel recalc retry", attempt, e); time.sleep(2.0)
    raise RuntimeError("Excel recalculation failed")


def recon(mkt, cases, prt, MROW):
    excel_recalc()
    wb = openpyxl.load_workbook(OUT_XLSX, data_only=True)
    rows = []
    wm = wb["Market_Implied"]
    colmap = {"g_ntm": 5, "m_ntm": 8, "g27_prop": 9, "g27_direct": 10, "rev27": 11, "ebitda27": 12, "eps27": 13, "ev_fy27_ebitda": 14, "nights27_prop": 15, "nights27_direct": 16, "g27_fixed": 17, "nights27_fixed": 18}
    for i, row in mkt.iterrows():
        r = MROW[round(float(row.price), 2)]
        for k, j in colmap.items():
            xv = wm.cell(row=r, column=j).value; rows.append(dict(sheet="Market_Implied", key=f"{row.price}:{k}", excel=xv, python=float(row[k]), diff=None if xv is None else xv - float(row[k])))
    wc = wb["Cases"]
    for i, row in cases.iterrows():
        r = 5 + i
        for k, j in [("price_joint", 4), ("price_fixed_16_5", 6), ("price_fixed_own_ebitda", 7), ("nights27", 8)]:
            xv = wc.cell(row=r, column=j).value; rows.append(dict(sheet="Cases", key=f"{row.case}:{k}", excel=xv, python=float(row[k]), diff=None if xv is None else xv - float(row[k])))
    wp = wb["Print_5Nov"]
    for i, row in prt.iterrows():
        r = 5 + i
        for k, j in [("E_S2_ex_reopening", 6), ("E_S1_post2022", 7), ("E_S2_post2022", 8)]:
            xv = wp.cell(row=r, column=j).value; rows.append(dict(sheet="Print_5Nov", key=f"{row.scenario}:{k}", excel=xv, python=float(row[k]), diff=None if xv is None else xv - float(row[k])))
    rec = pd.DataFrame(rows); rec.to_csv(os.path.join(OUT_DIR, "market_implied_recon.csv"), index=False)
    wb2 = openpyxl.load_workbook(OUT_XLSX); ws = wb2["Recon"]
    ws["A1"] = "Excel (recalculated) vs Python mirror; max abs diff:"; ws["B1"] = float(rec["diff"].abs().max())
    for j, h in enumerate(rec.columns):
        ws.cell(row=3, column=1 + j, value=h).font = BOLD
    for i, r in enumerate(rec.itertuples(index=False)):
        for j, v in enumerate(r):
            ws.cell(row=4 + i, column=1 + j, value=(float(v) if isinstance(v, (np.floating,)) else v))
    wb2.save(OUT_XLSX); excel_recalc()
    # read the Comparison sheet values for the note
    wq = openpyxl.load_workbook(OUT_XLSX, data_only=True)["Comparison"]
    comp = []
    for row in wq.iter_rows(min_row=4, max_row=40, max_col=10, values_only=True):
        if row[0]:
            comp.append(row)
    comp = pd.DataFrame(comp, columns=["who", "price", "fy27_growth_pct", "fy27_revenue_musd", "fy27_ebitda_musd", "fy27_nights_growth_pct", "ev_fy27_ebitda_x", "p_above_12m", "expected_5nov_reaction_pct", "source"])
    comp.to_csv(os.path.join(OUT_DIR, "market_implied_comparison.csv"), index=False)
    return rec, comp


def main():
    mkt = market_rows(); cases = case_rows(); prt = print_rows()
    mkt.round(4).to_csv(os.path.join(OUT_DIR, "market_implied_by_price.csv"), index=False)
    cases.round(4).to_csv(os.path.join(OUT_DIR, "market_implied_cases.csv"), index=False)
    prt.round(4).to_csv(os.path.join(OUT_DIR, "market_implied_print_scenarios.csv"), index=False)
    json.dump(dict(price=PRICE, shares=SHARES, net_cash=NET_CASH, ltm_rev=LTM_REV, ltm_margin=LTM_MARGIN, fy26_base=FY26_BASE, margin=MARGIN, reg_a=REG_A, reg_b=REG_B, spread=SPREAD, adr=ADR, fx=FX, take=TAKE, event_sd=EVENT_SD),
              open(os.path.join(OUT_DIR, "market_implied_params.json"), "w"), indent=2)
    MROW = build(mkt, cases, prt)
    rec, comp = recon(mkt, cases, prt, MROW)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print("recon max abs diff:", rec["diff"].abs().max())
    print(mkt[["price", "label", "g_ntm", "g27_prop", "g27_direct", "ebitda27", "eps27", "nights27_prop", "nights27_direct", "g27_fixed", "p_above_12m", "rdcf_reported"]].round(2).to_string())
    print(cases.round(2).to_string())
    print(prt.round(2).to_string())
    print(comp.round(2).to_string())


if __name__ == "__main__":
    main()
