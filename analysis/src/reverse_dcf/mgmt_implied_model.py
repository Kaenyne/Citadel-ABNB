"""Management-implied model for ABNB: what management is telling us, priced.

Krish with Claude Code, 11 Sep 2026.  Run with:  py -3.13 analysis/src/reverse_dcf/mgmt_implied_model.py

Builds model/ABNB_management_implied.xlsx (formula-driven; yellow cells are inputs), recalculates it
through Excel COM, reconciles every output against the Python mirror below, and writes
data/processed/reverse_dcf/mgmt_implied_summary.csv + mgmt_implied_recon.csv.

Three management cases, each a translation of what management has said (letters 4Q20-2Q26, calls,
the 8 Sep 2026 Communacopia fireside) into numbers:

  Literal    the guide taken at face value: range midpoints, floors as points, "low double digits" = 10,
             FY27 = the guide management would give in Feb 2027 on its own pattern (low double digits,
             margin floor carried forward)
  Delivered  the guide plus management's own historical cushion: quarterly revenue +1.8% above the
             midpoint (median of the last eight prints), nights one point above the top of the bucket
             (every bucket guide since 4Q25 printed above range), FY margin floor +70bp (FY24 +140,
             FY25 +60), FY27 = the FY26 exit rate carried forward with margin flat (the reinvestment rule)
  Ambition   the September 2026 CEO framing ("almost every market is accelerating", hotels 3x homes,
             India +60%, sponsored listings "a straight shot to $1bn"): nights 12-12.5%, take rate +20bp
             in FY27, margin drifting up to 37%

Every input cell carries its source in column P.  Management is silent on every FY27 line; the FY27
inputs are the analyst's reading of management's stated algorithm, and are labelled as such.
"""
from __future__ import annotations

import os
import sys
import json
import math
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT_XLSX = os.path.join(ROOT, "model", "ABNB_management_implied.xlsx")
OUT_DIR = os.path.join(ROOT, "data", "processed", "reverse_dcf")
os.makedirs(OUT_DIR, exist_ok=True)

PRICE = 170.19          # close 11 Sep 2026 (yfinance)
PRICE_DATE = "11 Sep 2026"
NET_CASH_2Q26 = 12069 - 2476   # cash + ST investments $12,069M less $2,476M senior notes (2Q26 10-Q); funds held for clients excluded
DILUTED_2Q26 = 597.0
RSU_WITHHOLD = 0.35     # FY25 withholding $561M / SBC $1,581M

# --------------------------------------------------------------------------------------------
# History (letters / 10-Q / Bloomberg FA page for interest and other income)
# --------------------------------------------------------------------------------------------
HQ = ["3Q25", "4Q25", "1Q26", "2Q26"]
FQ = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
PY = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}

HIST = {
    # nights (M), GBV ($M), revenue, adj EBITDA, SBC, D&A, op income, interest income, interest expense, other income,
    # tax, net income, diluted WA shares, FCF, buybacks, net cash ex float (cash+ST inv - debt)
    "3Q25": dict(nights=133.6, gbv=22892, rev=4095, ebitda=2051, sbc=399, da=22, opinc=1633, intinc=180, intexp=0, other=13, tax=418, ni=1374, sh=621, fcf=1349, bb=877, netcash=11684),
    "4Q25": dict(nights=121.9, gbv=20400, rev=2778, ebitda=786, sbc=400, da=23, opinc=479, intinc=162, intexp=0, other=38, tax=52, ni=341, sh=613, fcf=521, bb=1095, netcash=11014),
    "1Q26": dict(nights=156.2, gbv=29187, rev=2678, ebitda=519, sbc=410, da=22, opinc=161, intinc=155, intexp=0, other=-40, tax=121, ni=160, sh=608, fcf=1704, bb=1088, netcash=12005 - 2475),
    "2Q26": dict(nights=148.3, gbv=27247, rev=3608, ebitda=1261, sbc=487, da=17, opinc=846, intinc=183, intexp=37, other=7, tax=81, ni=816, sh=597, fcf=1253, bb=1051, netcash=NET_CASH_2Q26),
}
# 1Q25 / 2Q25 (for FY25 totals only)
H25 = {
    "1Q25": dict(nights=143.1, gbv=24500, rev=2272, ebitda=417, sbc=358, da=25, opinc=39, intinc=173, intexp=0, other=38, tax=19, ni=154, sh=632, fcf=1781, bb=807),
    "2Q25": dict(nights=134.4, gbv=23500, rev=3096, ebitda=1043, sbc=424, da=21, opinc=590, intinc=190, intexp=0, other=23, tax=137, ni=642, sh=626, fcf=962, bb=1010),
}
# op income check: pretax = opinc + intinc - intexp + other ; 3Q25: 1633+180+13 = 1826 vs Bloomberg 1792 (other adj); tolerated, hist only
# derive op income so that pretax ties to net income + tax exactly (letters), keeping interest/other as Bloomberg reports them
for q, d in list(HIST.items()) + list(H25.items()):
    d["pretax"] = d["ni"] + d["tax"]
    d["opinc"] = d["pretax"] - d["intinc"] + d["intexp"] - d["other"]

FY25 = {k: sum(d[k] for d in [H25["1Q25"], H25["2Q25"], HIST["3Q25"], HIST["4Q25"]])
        for k in ["nights", "gbv", "rev", "ebitda", "sbc", "da", "opinc", "intinc", "intexp", "other", "tax", "ni", "pretax", "fcf", "bb"]}
FY25["sh"] = np.mean([H25["1Q25"]["sh"], H25["2Q25"]["sh"], HIST["3Q25"]["sh"], HIST["4Q25"]["sh"]])
FY25["netcash"] = HIST["4Q25"]["netcash"]

# --------------------------------------------------------------------------------------------
# Management guide anchors (2Q26 letter, 6 Aug 2026) and cushions (02_guidance_ledger.csv)
# --------------------------------------------------------------------------------------------
GUIDE_3Q26_REV = (4690.0, 4770.0)       # $M, +15-17%, ~3pp FX after hedging
GUIDE_FY26_REV_GROWTH_FLOOR = 15.0      # "at least mid teens" -> 14-16 bucket with floor language; 15 = midpoint
GUIDE_FY26_MARGIN_FLOOR = 35.5
GUIDE_FY25_TAKE = 13.41                 # FY25 implied take rate; FY26 guided "relatively flat"
REV_BEAT_VS_MID = 1.8                   # median beat of the quarterly revenue midpoint, last 8 prints (2.5% all 19)
MARGIN_FLOOR_CUSHION = 0.7              # FY24 floor beaten by 140bp, FY25 by 60bp; midpoint 100, haircut to 70 for a twice-raised floor

# FX schedule (WS05 / WS29, consensus EUR path): revenue FX after hedging, ADR FX
REVFX = {"3Q26": 3.0, "4Q26": -0.4, "1Q27": -1.0, "2Q27": -0.8, "3Q27": -0.6, "4Q27": -0.1}
ADRFX = {"3Q26": 0.3, "4Q26": -0.4, "1Q27": -0.4, "2Q27": 0.0, "3Q27": 0.7, "4Q27": 0.0}

COMMON = dict(
    da_pct={q: 0.65 for q in FQ},                       # D&A 0.6-0.8% of revenue since 2023
    intinc={"3Q26": 170, "4Q26": 165, "1Q27": 160, "2Q27": 160, "3Q27": 160, "4Q27": 160},
    intexp={q: 31 for q in FQ},                         # $2.5bn notes at 4.40-5.25%
    tax={q: 18.0 for q in FQ},                          # "high teens" FY26; OBBBA long-term mid-to-high teens; 1H26 17.1%
    bb={q: 1050 for q in FQ},                           # 1H26 run rate $1.07bn/q; $3.4bn authorisation left after 2Q26 -> new authorisation needed by ~2Q27
    rsu_net={q: 1.6 for q in FQ},                       # net RSU issuance after withholding, M shares/q (37.8M RSUs outstanding)
    fcf_conv={"3Q26": 0.70, "4Q26": 0.70, "1Q27": 3.20, "2Q27": 1.00, "3Q27": 0.70, "4Q27": 0.70},  # seasonal: the float builds in H1 and unwinds in H2 (3Q25 0.66x, 4Q25 0.66x, 1Q26 3.28x, 2Q26 0.99x); annual FY24 1.14x, FY25 1.07x, LTM 1.05x -> FY26 ~1.03x, FY27 ~1.01x
)
BB_PRICE0 = PRICE
BB_PRICE_G = 1.2  # % per quarter drift in the repurchase price

SCENARIOS = {
    "Literal": dict(
        label="Guide literal",
        blurb="Range midpoints, floors as points, buckets at their low end; FY27 = the guide management would give in Feb 2027 on its own pattern",
        nights={"3Q26": 10.0, "4Q26": 8.5, "1Q27": 9.0, "2Q27": 9.0, "3Q27": 9.0, "4Q27": 9.0},
        adr={"3Q26": 3.0, "4Q26": 2.5, "1Q27": 2.5, "2Q27": 2.5, "3Q27": 2.5, "4Q27": 2.5},
        tr_rel={q: 0.0 for q in FQ},
        timing={"3Q26": None, "4Q26": None, "1Q27": 0.0, "2Q27": 0.0, "3Q27": 0.0, "4Q27": 0.0},   # None = calibrated
        rev_3q26=(GUIDE_3Q26_REV[0] + GUIDE_3Q26_REV[1]) / 2,
        fy26_rev_growth=GUIDE_FY26_REV_GROWTH_FLOOR,
        margin_3q26_chg=-0.6,                     # "down slightly compared to Q3 2025" (50.1%)
        fy26_margin=GUIDE_FY26_MARGIN_FLOOR,
        fy27_margin=GUIDE_FY26_MARGIN_FLOOR,      # the floor carried forward (30_mgmt_language: Feb 2027 floor 'at least 35.5%')
        sbc={"3Q26": 10.0, "4Q26": 10.0, "1Q27": 9.0, "2Q27": 9.0, "3Q27": 9.0, "4Q27": 9.0},
    ),
    "Delivered": dict(
        label="Guide as delivered",
        blurb="Guide plus management's own cushion: revenue +1.8% vs midpoint, nights 1pt above the bucket top, FY margin floor +70bp; FY27 holds the FY26 exit rate with margin flat (reinvest-the-efficiencies rule)",
        nights={"3Q26": 11.5, "4Q26": 10.5, "1Q27": 10.0, "2Q27": 10.0, "3Q27": 10.0, "4Q27": 10.0},
        adr={"3Q26": 3.5, "4Q26": 3.0, "1Q27": 3.0, "2Q27": 3.0, "3Q27": 3.0, "4Q27": 3.0},
        tr_rel={q: 0.0 for q in FQ},
        timing={"3Q26": None, "4Q26": -0.6, "1Q27": 0.0, "2Q27": 0.0, "3Q27": 0.0, "4Q27": 0.0},
        rev_3q26=(GUIDE_3Q26_REV[0] + GUIDE_3Q26_REV[1]) / 2 * (1 + REV_BEAT_VS_MID / 100),
        fy26_rev_growth=None,
        margin_3q26_chg=-0.1,                     # 1Q26 guided flat printed +1.0; 2Q26 guided >=0 printed +1.3
        fy26_margin=GUIDE_FY26_MARGIN_FLOOR + MARGIN_FLOOR_CUSHION,
        fy27_margin=GUIDE_FY26_MARGIN_FLOOR + MARGIN_FLOOR_CUSHION,
        sbc={"3Q26": 10.0, "4Q26": 10.0, "1Q27": 9.0, "2Q27": 9.0, "3Q27": 9.0, "4Q27": 9.0},
    ),
    "Ambition": dict(
        label="Management ambition",
        blurb="The 8 Sep 2026 CEO framing: 'almost every market is accelerating', hotels 3x homes, India +60%, sponsored listings 'a straight shot to $1bn'; take rate +20bp in FY27, margin drifting to 37%",
        nights={"3Q26": 12.5, "4Q26": 12.0, "1Q27": 12.0, "2Q27": 12.0, "3Q27": 12.0, "4Q27": 12.0},
        adr={"3Q26": 4.0, "4Q26": 3.5, "1Q27": 3.0, "2Q27": 3.0, "3Q27": 3.0, "4Q27": 3.0},
        tr_rel={"3Q26": 0.0, "4Q26": 0.0, "1Q27": 1.5, "2Q27": 1.5, "3Q27": 1.5, "4Q27": 1.5},   # +20bp on a ~13.4% take rate
        timing={"3Q26": -1.1, "4Q26": -0.6, "1Q27": 0.5, "2Q27": 0.5, "3Q27": 0.5, "4Q27": 0.5},
        rev_3q26=None,
        fy26_rev_growth=None,
        margin_3q26_chg=0.3,
        fy26_margin=36.5,
        fy27_margin=37.0,
        sbc={"3Q26": 10.0, "4Q26": 10.0, "1Q27": 8.0, "2Q27": 8.0, "3Q27": 8.0, "4Q27": 8.0},
    ),
}

# --------------------------------------------------------------------------------------------
# Python mirror
# --------------------------------------------------------------------------------------------

def run(name: str) -> dict:
    s = SCENARIOS[name]
    o = {q: dict(HIST[q]) for q in HQ}
    for q in HQ:
        o[q]["adr"] = o[q]["gbv"] / o[q]["nights"]
        o[q]["take"] = o[q]["rev"] / o[q]["gbv"] * 100
        o[q]["margin"] = o[q]["ebitda"] / o[q]["rev"] * 100
        o[q]["eps"] = o[q]["ni"] / o[q]["sh"]
        o[q]["tax_rate"] = o[q]["tax"] / o[q]["pretax"] * 100
        o[q]["rsu_wh"] = None
    inputs = {q: {} for q in FQ}
    # calibrate 3Q26 timing so revenue = target
    timing = dict(s["timing"])
    prev_sh = HIST["2Q26"]["sh"]
    prev_nc = HIST["2Q26"]["netcash"]
    bb_price = BB_PRICE0
    for i, q in enumerate(FQ):
        p = o[PY[q]]
        n, a, afx, tr, rfx = s["nights"][q], s["adr"][q], ADRFX[q], s["tr_rel"][q], REVFX[q]
        core = (1 + n / 100) * (1 + a / 100) * (1 + tr / 100)
        if q == "3Q26" and timing[q] is None:
            timing[q] = ((s["rev_3q26"] / p["rev"]) / core - 1) * 100 - rfx
        if q == "4Q26" and timing[q] is None:
            fy_target = FY25["rev"] * (1 + s["fy26_rev_growth"] / 100)
            q4_target = fy_target - HIST["1Q26"]["rev"] - HIST["2Q26"]["rev"] - o["3Q26"]["rev"]
            timing[q] = ((q4_target / p["rev"]) / core - 1) * 100 - rfx
        t = timing[q]
        d = {}
        d["nights"] = p["nights"] * (1 + n / 100)
        d["gbv"] = p["gbv"] * (1 + n / 100) * (1 + a / 100) * (1 + afx / 100)
        d["adr"] = d["gbv"] / d["nights"]
        d["rev"] = p["rev"] * core * (1 + (rfx + t) / 100)
        d["take"] = d["rev"] / d["gbv"] * 100
        d["sbc"] = p["sbc"] * (1 + s["sbc"][q] / 100)
        d["da"] = d["rev"] * COMMON["da_pct"][q] / 100
        d["intinc"] = COMMON["intinc"][q]
        d["intexp"] = COMMON["intexp"][q]
        d["other"] = 0.0
        d["tax_rate"] = COMMON["tax"][q]
        d["bb"] = COMMON["bb"][q]
        bb_price = bb_price * (1 + BB_PRICE_G / 100) if i > 0 else BB_PRICE0
        d["bb_price"] = bb_price
        d["sh"] = prev_sh - d["bb"] / d["bb_price"] + COMMON["rsu_net"][q]
        prev_sh = d["sh"]
        o[q] = d
        inputs[q] = dict(nights=n, adr=a, adr_fx=afx, tr_rel=tr, revfx=rfx, timing=t, sbc=s["sbc"][q],
                         da_pct=COMMON["da_pct"][q], intinc=d["intinc"], intexp=d["intexp"], tax=d["tax_rate"],
                         bb=d["bb"], bb_price=bb_price, rsu_net=COMMON["rsu_net"][q], fcf_conv=COMMON["fcf_conv"][q])
    # margins: 3Q26 = prior + chg; 4Q26 solved for FY26 target; FY27 uniform delta solved for FY27 target
    mchg = {}
    mchg["3Q26"] = s["margin_3q26_chg"]
    o["3Q26"]["margin"] = o["3Q25"]["margin"] + mchg["3Q26"]
    o["3Q26"]["ebitda"] = o["3Q26"]["rev"] * o["3Q26"]["margin"] / 100
    fy26_rev = HIST["1Q26"]["rev"] + HIST["2Q26"]["rev"] + o["3Q26"]["rev"] + o["4Q26"]["rev"]
    q4_ebitda = s["fy26_margin"] / 100 * fy26_rev - HIST["1Q26"]["ebitda"] - HIST["2Q26"]["ebitda"] - o["3Q26"]["ebitda"]
    o["4Q26"]["margin"] = q4_ebitda / o["4Q26"]["rev"] * 100
    o["4Q26"]["ebitda"] = q4_ebitda
    mchg["4Q26"] = o["4Q26"]["margin"] - o["4Q25"]["margin"]
    fy27_q = ["1Q27", "2Q27", "3Q27", "4Q27"]
    w = sum(o[q]["rev"] * o[PY[q]]["margin"] for q in fy27_q) / sum(o[q]["rev"] for q in fy27_q)
    d27 = s["fy27_margin"] - w
    for q in fy27_q:
        mchg[q] = d27
        o[q]["margin"] = o[PY[q]]["margin"] + d27
        o[q]["ebitda"] = o[q]["rev"] * o[q]["margin"] / 100
    for q in FQ:
        d = o[q]
        d["opinc"] = d["ebitda"] - d["sbc"] - d["da"]
        d["pretax"] = d["opinc"] + d["intinc"] - d["intexp"] + d["other"]
        d["tax"] = d["pretax"] * d["tax_rate"] / 100
        d["ni"] = d["pretax"] - d["tax"]
        d["eps"] = d["ni"] / d["sh"]
        d["fcf"] = d["ebitda"] * COMMON["fcf_conv"][q]
        d["rsu_wh"] = RSU_WITHHOLD * d["sbc"]
        d["netcash"] = prev_nc + d["fcf"] - d["bb"] - d["rsu_wh"]
        prev_nc = d["netcash"]
        inputs[q]["margin_chg"] = mchg[q]
    # fiscal years
    def fy(qs, prior=None):
        f = {k: sum(o[q][k] for q in qs) for k in ["nights", "gbv", "rev", "ebitda", "sbc", "da", "opinc", "intinc", "intexp", "other", "pretax", "tax", "ni", "fcf", "bb"]}
        f["adr"] = f["gbv"] / f["nights"]
        f["take"] = f["rev"] / f["gbv"] * 100
        f["margin"] = f["ebitda"] / f["rev"] * 100
        f["sh"] = np.mean([o[q]["sh"] for q in qs])
        f["eps"] = f["ni"] / f["sh"]
        f["tax_rate"] = f["tax"] / f["pretax"] * 100
        f["netcash"] = o[qs[-1]]["netcash"]
        f["sh_end"] = o[qs[-1]]["sh"]
        return f
    o["FY25"] = dict(FY25)
    o["FY25"]["adr"] = FY25["gbv"] / FY25["nights"]; o["FY25"]["take"] = FY25["rev"] / FY25["gbv"] * 100
    o["FY25"]["margin"] = FY25["ebitda"] / FY25["rev"] * 100; o["FY25"]["eps"] = FY25["ni"] / FY25["sh"]
    o["FY25"]["tax_rate"] = FY25["tax"] / FY25["pretax"] * 100
    o["FY26"] = fy(["1Q26", "2Q26", "3Q26", "4Q26"])
    o["FY27"] = fy(fy27_q)
    return dict(out=o, inputs=inputs, mchg=mchg, timing=timing)


# --------------------------------------------------------------------------------------------
# Valuation helpers (Python)
# --------------------------------------------------------------------------------------------
MULT = {
    "EV / FY27E adj. EBITDA": (13.5, 16.5, 18.5),   # WS12 recommendation (time series / cross-section / intrinsic)
    "P / FY27E GAAP EPS": (22.0, 27.0, 30.0),        # ABNB at $170 = 28x Street FY27; BKNG 16x, NFLX 21x, UBER 18x; ABNB 2023-26 LTM range 25-40x
    "EV / FY27E FCF": (14.0, 17.0, 20.0),            # WS12 0.75x haircut set 11.3/14.3/17.3, lifted for the FCF>EBITDA conversion
}
WACC, TG = 0.10, 0.03


def fade_dcf(fcf27, g0, wacc=WACC, tg=TG, years=10):
    """PV as of 30 Sep 2026 of FY27..FY36 FCF plus a Gordon terminal; FY28 growth g0 fades linearly to tg by FY36.
    Year-y cash flow is discounted from its mid-point (y - 0.25 years out); the terminal from end-FY36 (years - 0.25)."""
    pv = 0.0
    f = fcf27
    for y in range(1, years + 1):
        if y > 1:
            g = g0 + (tg - g0) * (y - 2) / (years - 2) if years > 2 else tg
            f = f * (1 + g)
        pv += f / (1 + wacc) ** (y - 0.25)
    tv = f * (1 + tg) / (wacc - tg)
    pv += tv / (1 + wacc) ** (years - 0.25)
    return pv


def implied_growth(ev_target, fcf27):
    lo, hi = -0.30, 0.60
    for _ in range(80):
        mid = (lo + hi) / 2
        if fade_dcf(fcf27, mid) < ev_target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# --------------------------------------------------------------------------------------------
# Excel builder
# --------------------------------------------------------------------------------------------
YELLOW = PatternFill("solid", fgColor="FFF2CC")
BLUE = Font(color="0000FF")
BOLD = Font(bold=True)
GREY = Font(color="808080", italic=True)
HDR = PatternFill("solid", fgColor="D9E1F2")
thin = Side(style="thin", color="BFBFBF")

COLS = {"3Q25": "C", "4Q25": "D", "1Q26": "E", "2Q26": "F", "3Q26": "G", "4Q26": "H", "1Q27": "I", "2Q27": "J", "3Q27": "K", "4Q27": "L", "FY25": "M", "FY26": "N", "FY27": "O"}
NOTE_COL = "P"

ROWS = []  # filled by layout()


def layout():
    """(key, label, unit, kind, note).  kind: input | hist | calc | growth | check | blank | section"""
    L = []
    L.append(("sec_in", "A. INPUTS (yellow = management-derived driver; column P = source)", "", "section", ""))
    L.append(("in_nights", "Nights & Seats Booked growth", "y/y %", "input", "2Q26 letter: 3Q26 'low double-digit'; 4Q26 not guided (FY 'at least mid teens' revenue implies it); FY27 silent"))
    L.append(("in_adr", "ADR ex-FX growth", "y/y %", "input", "2Q26 letter: 'moderate increase in ADR due to mix shift and price appreciation'; 1H26 ran +4%"))
    L.append(("in_adrfx", "ADR FX effect", "pp", "input", "WS05/WS29 EUR path fit; management does not guide ADR FX beyond 'significantly lower' (1Q26)"))
    L.append(("in_tr", "Implied take rate, relative change", "y/y %", "input", "2Q26: 'relatively flat compared to 2025' after customer incentives; +1.5% = +20bp (Ambition only)"))
    L.append(("in_revfx", "Revenue FX after hedging", "pp", "input", "2Q26 letter: 3Q26 'approximate three percentage point FX tailwind after factoring in our hedging program'; later quarters WS29 fit"))
    L.append(("in_timing", "Timing / other residual (revenue vs GBV x take rate)", "pp", "input", "calibrated so 3Q26 revenue hits the guide midpoint (Literal) or midpoint +1.8% (Delivered); RNPL book-vs-stay timing"))
    L.append(("in_mchg", "Adj. EBITDA margin change", "y/y pts", "input", "3Q26: 'down slightly compared to Q3 2025' (50.1%); 4Q26 solved so FY26 = floor (or floor + cushion); FY27 solved for the FY27 margin in row 1"))
    L.append(("in_sbc", "SBC growth", "y/y %", "input", "4Q25 letter: 'growth rate of SBC and headcount will be lower than 2025' (FY25 +13.1% letters basis); 1H26 +14.7% so H2 ~+10%"))
    L.append(("in_da", "D&A", "% revenue", "input", "0.6-0.8% of revenue since 2023"))
    L.append(("in_intinc", "Interest income", "$M", "input", "$12.1bn cash + ST investments; 2Q26 $183M; falling rates"))
    L.append(("in_intexp", "Interest expense", "$M", "input", "$2.5bn senior notes issued Mar 2026 at 4.40 / 4.65 / 5.25%"))
    L.append(("in_tax", "Effective tax rate", "%", "input", "2Q26 letter 'high teens' FY26; OBBBA long-term 'mid-to-high teens' (2Q26 call); 1H26 17.1%"))
    L.append(("in_bb", "Share repurchases", "$M", "input", "1H26 $2,139M; $3.4bn authorisation remaining after 2Q26 -> a new authorisation is needed by ~2Q27 for this path"))
    L.append(("in_bbpx", "Average repurchase price", "$", "input", f"{PRICE_DATE} close ${PRICE} drifting +{BB_PRICE_G}%/q"))
    L.append(("in_rsu", "Net RSU issuance after withholding", "M shares", "input", "37.8M RSUs outstanding at 30 Jun 2026; ~10M/yr vesting less 35% withheld"))
    L.append(("in_fcfconv", "FCF / adj. EBITDA (seasonal)", "x", "input", "prior-year quarter ratios 3Q25 0.66x, 4Q25 0.66x, 1Q26 3.28x, 2Q26 0.99x (the float builds in H1, unwinds in H2); annual FY24 1.14x, FY25 1.07x, LTM 1.05x; set so FY26 ~1.03x and FY27 ~1.01x as cash taxes rise, interest income falls and RNPL flattens unearned fees"))
    L.append(("blank1", "", "", "blank", ""))
    L.append(("sec_out", "B. OPERATING BUILD", "", "section", ""))
    L.append(("nights", "Nights & Seats Booked", "M", "hist", "letters"))
    L.append(("gbv", "Gross Booking Value", "$M", "hist", "letters / Bloomberg FA (unrounded 3Q25, 1Q26, 2Q26)"))
    L.append(("adr", "ADR (GBV / nights)", "$", "calc", ""))
    L.append(("rev", "Revenue", "$M", "hist", "letters"))
    L.append(("take", "Implied take rate", "%", "calc", "FY25 13.41%; guided 'relatively flat' for FY26"))
    L.append(("margin", "Adj. EBITDA margin", "%", "calc", ""))
    L.append(("ebitda", "Adj. EBITDA", "$M", "hist", "letters"))
    L.append(("sbc", "Stock-based compensation", "$M", "hist", "letters (adj. EBITDA reconciliation)"))
    L.append(("da", "D&A", "$M", "hist", "Bloomberg FA / 10-Q"))
    L.append(("opinc", "Operating income (GAAP; adj. EBITDA less SBC less D&A)", "$M", "hist", "history backed out of pretax income so the P&L ties to reported net income; other add-backs sit here"))
    L.append(("intinc", "Interest income", "$M", "hist", "Bloomberg FA"))
    L.append(("intexp", "Interest expense", "$M", "hist", "Bloomberg FA"))
    L.append(("other", "Other income (expense), net", "$M", "hist", "Bloomberg FA; zero forecast"))
    L.append(("pretax", "Pretax income", "$M", "calc", ""))
    L.append(("tax_rate", "Effective tax rate", "%", "calc", ""))
    L.append(("tax", "Income tax", "$M", "hist", "letters; 2Q26 includes a $77M prior-year benefit"))
    L.append(("ni", "Net income (GAAP)", "$M", "hist", "letters"))
    L.append(("sh", "Diluted weighted-average shares", "M", "hist", "10-Q; forecast = prior less buyback / price plus net RSU issuance"))
    L.append(("eps", "Diluted EPS (GAAP)", "$", "calc", "Street 'adjusted' EPS for ABNB is GAAP-basis (Bloomberg FA 2Q26 1.37 = GAAP)"))
    L.append(("fcf", "Free cash flow", "$M", "hist", "letters; forecast = adj. EBITDA x conversion (annual-grade; quarterly seasonality of the float is not modelled)"))
    L.append(("bb", "Share repurchases", "$M", "hist", "letters"))
    L.append(("rsu_wh", "RSU tax withholding (cash)", "$M", "calc", "35% of SBC (FY25 $561M / $1,581M)"))
    L.append(("netcash", "Net cash ex float (cash + ST investments less notes), period end", "$M", "hist", "10-Q; funds held for clients excluded; forecast = prior + FCF - buybacks - withholding"))
    L.append(("blank2", "", "", "blank", ""))
    L.append(("sec_g", "C. GROWTH AND CHECKS", "", "section", ""))
    L.append(("g_nights", "Nights growth", "y/y %", "growth", ""))
    L.append(("g_gbv", "GBV growth", "y/y %", "growth", ""))
    L.append(("g_adr", "ADR growth (reported)", "y/y %", "growth", ""))
    L.append(("g_rev", "Revenue growth", "y/y %", "growth", ""))
    L.append(("g_ebitda", "Adj. EBITDA growth", "y/y %", "growth", ""))
    L.append(("g_eps", "EPS growth", "y/y %", "growth", ""))
    L.append(("g_take", "Take rate change", "y/y pts", "growth", ""))
    L.append(("g_margin", "Margin change", "y/y pts", "growth", ""))
    L.append(("blank3", "", "", "blank", ""))
    L.append(("chk_q3", "3Q26 revenue vs guide $4,690-4,770M", "", "check", ""))
    L.append(("chk_fy26rev", "FY26 revenue growth vs 'at least mid teens' (>=15%)", "", "check", ""))
    L.append(("chk_fy26m", "FY26 adj. EBITDA margin vs 'at least 35.5%'", "", "check", ""))
    L.append(("chk_take", "FY26 take rate vs FY25 13.41% ('relatively flat')", "", "check", ""))
    L.append(("chk_q3m", "3Q26 margin vs 3Q25 50.1% ('down slightly')", "", "check", ""))
    L.append(("chk_auth", "Buybacks 3Q26-2Q27 vs $3.4bn remaining authorisation", "", "check", ""))
    return L


ROWS = layout()
ROWNUM = {}


def build_scenario_sheet(wb, name, res):
    s = SCENARIOS[name]
    ws = wb.create_sheet(f"Mgmt_{name}")
    ws["A1"] = f"ABNB management-implied model: {s['label']}"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = s["blurb"]
    ws["A2"].font = GREY
    ws["A3"] = f"Yellow = input. Blue = reported history. Black = formula. Price ${PRICE} ({PRICE_DATE}). Built by analysis/src/reverse_dcf/mgmt_implied_model.py"
    ws["A3"].font = GREY
    hdr = 5
    ws[f"A{hdr}"] = "Line"; ws[f"B{hdr}"] = "Unit"
    for p, c in COLS.items():
        ws[f"{c}{hdr}"] = p + ("A" if p in HQ or p == "FY25" else "E")
        ws[f"{c}{hdr}"].font = BOLD; ws[f"{c}{hdr}"].fill = HDR; ws[f"{c}{hdr}"].alignment = Alignment(horizontal="center")
    ws[f"{NOTE_COL}{hdr}"] = "Source / note"; ws[f"{NOTE_COL}{hdr}"].font = BOLD; ws[f"{NOTE_COL}{hdr}"].fill = HDR
    ws[f"A{hdr}"].font = BOLD; ws[f"A{hdr}"].fill = HDR; ws[f"B{hdr}"].fill = HDR
    r = hdr + 1
    rn = {}
    for key, label, unit, kind, note in ROWS:
        rn[key] = r
        ws[f"A{r}"] = label; ws[f"B{r}"] = unit
        if kind == "section":
            ws[f"A{r}"].font = BOLD
        if note:
            ws[f"{NOTE_COL}{r}"] = note; ws[f"{NOTE_COL}{r}"].font = GREY
        r += 1
    ROWNUM.update(rn)
    R = rn
    inp = res["inputs"]
    out = res["out"]
    inkey = {"in_nights": "nights", "in_adr": "adr", "in_adrfx": "adr_fx", "in_tr": "tr_rel", "in_revfx": "revfx", "in_timing": "timing",
             "in_mchg": "margin_chg", "in_sbc": "sbc", "in_da": "da_pct", "in_intinc": "intinc", "in_intexp": "intexp", "in_tax": "tax",
             "in_bb": "bb", "in_bbpx": "bb_price", "in_rsu": "rsu_net", "in_fcfconv": "fcf_conv"}
    # inputs
    for k, ik in inkey.items():
        for q in FQ:
            c = ws[f"{COLS[q]}{R[k]}"]
            c.value = round(float(inp[q][ik]), 4); c.fill = YELLOW
    # history values (blue)
    hist_keys = ["nights", "gbv", "rev", "ebitda", "sbc", "da", "opinc", "intinc", "intexp", "other", "tax", "ni", "sh", "fcf", "bb", "netcash"]
    for q in HQ:
        for k in hist_keys:
            c = ws[f"{COLS[q]}{R[k]}"]; c.value = HIST[q][k]; c.font = BLUE
    for k in hist_keys:
        if k == "netcash":
            ws[f"M{R[k]}"] = f"=D{R[k]}"
        elif k == "sh":
            ws[f"M{R[k]}"] = FY25["sh"]; ws[f"M{R[k]}"].font = BLUE
        else:
            ws[f"M{R[k]}"] = FY25[k]; ws[f"M{R[k]}"].font = BLUE
    # formulas, forecast quarters
    for q in FQ:
        c = COLS[q]; p = COLS[PY[q]]
        prev = COLS[HQ[-1]] if q == "3Q26" else COLS[FQ[FQ.index(q) - 1]]
        f = lambda key: f"{c}{R[key]}"
        pf = lambda key: f"{p}{R[key]}"
        ws[f("nights")] = f"={pf('nights')}*(1+{f('in_nights')}/100)"
        ws[f("gbv")] = f"={pf('gbv')}*(1+{f('in_nights')}/100)*(1+{f('in_adr')}/100)*(1+{f('in_adrfx')}/100)"
        ws[f("rev")] = f"={pf('rev')}*(1+{f('in_nights')}/100)*(1+{f('in_adr')}/100)*(1+{f('in_tr')}/100)*(1+({f('in_revfx')}+{f('in_timing')})/100)"
        ws[f("margin")] = f"={pf('margin')}+{f('in_mchg')}"
        ws[f("ebitda")] = f"={f('rev')}*{f('margin')}/100"
        ws[f("sbc")] = f"={pf('sbc')}*(1+{f('in_sbc')}/100)"
        ws[f("da")] = f"={f('rev')}*{f('in_da')}/100"
        ws[f("opinc")] = f"={f('ebitda')}-{f('sbc')}-{f('da')}"
        ws[f("intinc")] = f"={f('in_intinc')}"
        ws[f("intexp")] = f"={f('in_intexp')}"
        ws[f("other")] = 0
        ws[f("tax_rate")] = f"={f('in_tax')}"
        ws[f("tax")] = f"={f('pretax')}*{f('tax_rate')}/100"
        ws[f("sh")] = f"={prev}{R['sh']}-{f('in_bb')}/{f('in_bbpx')}+{f('in_rsu')}"
        ws[f("fcf")] = f"={f('ebitda')}*{f('in_fcfconv')}"
        ws[f("bb")] = f"={f('in_bb')}"
        ws[f("rsu_wh")] = f"={RSU_WITHHOLD}*{f('sbc')}"
        ws[f("netcash")] = f"={prev}{R['netcash']}+{f('fcf')}-{f('bb')}-{f('rsu_wh')}"
    # calc rows for all quarter columns (history + forecast)
    for q in HQ + FQ:
        c = COLS[q]
        f = lambda key: f"{c}{R[key]}"
        ws[f("adr")] = f"={f('gbv')}/{f('nights')}"
        ws[f("take")] = f"={f('rev')}/{f('gbv')}*100"
        if q in HQ:
            ws[f("margin")] = f"={f('ebitda')}/{f('rev')}*100"
            ws[f("tax_rate")] = f"={f('tax')}/{f('pretax')}*100"
            ws[f("rsu_wh")] = None
        ws[f("pretax")] = f"={f('opinc')}+{f('intinc')}-{f('intexp')}+{f('other')}"
        ws[f("ni")] = f"={f('pretax')}-{f('tax')}"
        ws[f("eps")] = f"={f('ni')}/{f('sh')}"
    # FY columns
    for fyc, qs in [("N", ["1Q26", "2Q26", "3Q26", "4Q26"]), ("O", ["1Q27", "2Q27", "3Q27", "4Q27"])]:
        cs = [COLS[q] for q in qs]
        for k in ["nights", "gbv", "rev", "ebitda", "sbc", "da", "opinc", "intinc", "intexp", "other", "pretax", "tax", "ni", "fcf", "bb"]:
            ws[f"{fyc}{R[k]}"] = "=" + "+".join(f"{c}{R[k]}" for c in cs)
        ws[f"{fyc}{R['rsu_wh']}"] = "=" + "+".join(f"{c}{R['rsu_wh']}" for c in cs if c in [COLS[q] for q in FQ])
        ws[f"{fyc}{R['sh']}"] = f"=AVERAGE({cs[0]}{R['sh']}:{cs[-1]}{R['sh']})"
        ws[f"{fyc}{R['netcash']}"] = f"={cs[-1]}{R['netcash']}"
    for fyc in ["M", "N", "O"]:
        f = lambda key: f"{fyc}{R[key]}"
        ws[f("adr")] = f"={f('gbv')}/{f('nights')}"
        ws[f("take")] = f"={f('rev')}/{f('gbv')}*100"
        ws[f("margin")] = f"={f('ebitda')}/{f('rev')}*100"
        ws[f("tax_rate")] = f"={f('tax')}/{f('pretax')}*100"
        ws[f("eps")] = f"={f('ni')}/{f('sh')}"
        if fyc == "M":
            ws[f("pretax")] = f"={f('opinc')}+{f('intinc')}-{f('intexp')}+{f('other')}"
            ws[f("ni")] = f"={f('pretax')}-{f('tax')}"
    # growth rows
    gmap = {"g_nights": "nights", "g_gbv": "gbv", "g_adr": "adr", "g_rev": "rev", "g_ebitda": "ebitda", "g_eps": "eps"}
    for q in FQ:
        c = COLS[q]; p = COLS[PY[q]]
        for gk, k in gmap.items():
            ws[f"{c}{R[gk]}"] = f"=({c}{R[k]}/{p}{R[k]}-1)*100"
        ws[f"{c}{R['g_take']}"] = f"={c}{R['take']}-{p}{R['take']}"
        ws[f"{c}{R['g_margin']}"] = f"={c}{R['margin']}-{p}{R['margin']}"
    for fyc, p in [("N", "M"), ("O", "N")]:
        for gk, k in gmap.items():
            ws[f"{fyc}{R[gk]}"] = f"=({fyc}{R[k]}/{p}{R[k]}-1)*100"
        ws[f"{fyc}{R['g_take']}"] = f"={fyc}{R['take']}-{p}{R['take']}"
        ws[f"{fyc}{R['g_margin']}"] = f"={fyc}{R['margin']}-{p}{R['margin']}"
    # checks (text in column C)
    ws[f"C{R['chk_q3']}"] = f'=IF(G{R["rev"]}<{GUIDE_3Q26_REV[0]},"BELOW guide",IF(G{R["rev"]}>{GUIDE_3Q26_REV[1]},"ABOVE guide top by "&TEXT(G{R["rev"]}/{GUIDE_3Q26_REV[1]}-1,"0.0%"),"within guide"))'
    ws[f"C{R['chk_fy26rev']}"] = f'=IF(N{R["g_rev"]}>={GUIDE_FY26_REV_GROWTH_FLOOR},"met: "&TEXT(N{R["g_rev"]},"0.0")&"%","BELOW: "&TEXT(N{R["g_rev"]},"0.0")&"%")'
    ws[f"C{R['chk_fy26m']}"] = f'=IF(N{R["margin"]}>={GUIDE_FY26_MARGIN_FLOOR},"met: "&TEXT(N{R["margin"]},"0.0")&"%","BELOW: "&TEXT(N{R["margin"]},"0.0")&"%")'
    ws[f"C{R['chk_take']}"] = f'=TEXT(N{R["take"]}-{GUIDE_FY25_TAKE},"+0.00;-0.00")&" pts vs FY25"'
    ws[f"C{R['chk_q3m']}"] = f'=TEXT(G{R["margin"]}-C{R["margin"]},"+0.0;-0.0")&" pts y/y"'
    ws[f"C{R['chk_auth']}"] = f'=IF(SUM(G{R["bb"]}:J{R["bb"]})>3400,"needs new authorisation: $"&TEXT(SUM(G{R["bb"]}:J{R["bb"]}),"#,##0")&"M planned vs $3,400M left","inside authorisation")'
    # formats
    for key, label, unit, kind, note in ROWS:
        rr = R[key]
        fmt = None
        if unit in ("$M", "M", "M shares"):
            fmt = "#,##0"
        elif unit in ("$",):
            fmt = "0.00"
        elif unit in ("%", "y/y %", "pp", "y/y pts", "% revenue", "x"):
            fmt = "0.0"
        if key == "adr":
            fmt = "0.0"
        if key in ("eps", "g_eps"):
            fmt = "0.00"
        if fmt:
            for col in list(COLS.values()):
                ws[f"{col}{rr}"].number_format = fmt
    ws.column_dimensions["A"].width = 58; ws.column_dimensions["B"].width = 10
    for col in COLS.values():
        ws.column_dimensions[col].width = 10
    ws.column_dimensions[NOTE_COL].width = 120
    ws.freeze_panes = "C6"
    return ws


def build_valuation_sheet(wb, results):
    ws = wb.create_sheet("Valuation")
    ws["A1"] = "Management-implied target prices (12-month, FY27E exit)"; ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = "Target = (multiple x FY27E metric + end-FY27 net cash) / end-FY27 diluted shares; P/E lens uses FY27E GAAP EPS directly. Multiples are inputs (yellow)."; ws["A2"].font = GREY
    R = ROWNUM
    ws["A4"] = "Share price"; ws["B4"] = PRICE; ws["B4"].fill = YELLOW; ws["C4"] = f"{PRICE_DATE} close"
    ws["A5"] = "Diluted shares now (M)"; ws["B5"] = DILUTED_2Q26; ws["B5"].fill = YELLOW; ws["C5"] = "2Q26 diluted weighted average"
    ws["A6"] = "Net cash ex float now ($M)"; ws["B6"] = NET_CASH_2Q26; ws["B6"].fill = YELLOW; ws["C6"] = "30 Jun 2026: $12,069M cash + ST investments less $2,476M notes"
    ws["A7"] = "Market cap ($M)"; ws["B7"] = "=B4*B5"
    ws["A8"] = "Enterprise value ($M)"; ws["B8"] = "=B7-B6"
    # scenario metrics
    ws["A10"] = "FY27E metric"; ws["A10"].font = BOLD
    names = list(results.keys())
    for j, n in enumerate(names):
        ws.cell(row=10, column=2 + j, value=SCENARIOS[n]["label"]).font = BOLD
    ws.cell(row=10, column=5, value="Street (Zacks / S&P, 3-4 Sep 2026)").font = BOLD
    metrics = [("Revenue ($M)", "rev", "O"), ("Adj. EBITDA ($M)", "ebitda", "O"), ("Adj. EBITDA margin (%)", "margin", "O"), ("GAAP EPS ($)", "eps", "O"),
               ("FCF ($M)", "fcf", "O"), ("SBC ($M)", "sbc", "O"), ("Net cash, end-FY27 ($M)", "netcash", "O"), ("Diluted shares, 4Q27 (M)", "sh", "L"),
               ("FY26E revenue ($M)", "rev", "N"), ("FY26E adj. EBITDA ($M)", "ebitda", "N"), ("FY26E GAAP EPS ($)", "eps", "N")]
    mrow = {}
    for i, (lab, k, col) in enumerate(metrics):
        r = 11 + i; mrow[(k, col)] = r
        ws.cell(row=r, column=1, value=lab)
        for j, n in enumerate(names):
            ws.cell(row=r, column=2 + j, value=f"=Mgmt_{n}!{col}{R[k]}")
    street = {("rev", "O"): 15745, ("ebitda", "O"): None, ("eps", "O"): 6.08, ("rev", "N"): 14130, ("eps", "N"): 5.255, ("fcf", "O"): None, ("ebitda", "N"): None}
    for (k, col), v in street.items():
        if v is not None:
            ws.cell(row=mrow[(k, col)], column=5, value=v).font = BLUE
    ws.cell(row=mrow[("rev", "O")], column=6, value="Zacks $15,730M / S&P $15,760M").font = GREY
    ws.cell(row=mrow[("eps", "O")], column=6, value="Zacks $6.02 / S&P $6.14").font = GREY
    ws.cell(row=mrow[("rev", "N")], column=6, value="Zacks $14,100M / S&P $14,160M").font = GREY
    ws.cell(row=mrow[("eps", "N")], column=6, value="Zacks $5.23 / S&P $5.28").font = GREY
    # implied multiples today
    r0 = 11 + len(metrics) + 1
    ws.cell(row=r0, column=1, value="What $%.2f pays for each case today" % PRICE).font = BOLD
    rows_imp = [("EV / FY26E adj. EBITDA (x)", f"=$B$8/{{c}}{mrow[('ebitda','N')]}"),
                ("EV / FY27E adj. EBITDA (x)", f"=$B$8/{{c}}{mrow[('ebitda','O')]}"),
                ("P / FY26E EPS (x)", f"=$B$4/{{c}}{mrow[('eps','N')]}"),
                ("P / FY27E EPS (x)", f"=$B$4/{{c}}{mrow[('eps','O')]}"),
                ("EV / FY27E FCF (x)", f"=$B$8/{{c}}{mrow[('fcf','O')]}"),
                ("FY27E FCF yield on market cap (%)", f"={{c}}{mrow[('fcf','O')]}/$B$7*100")]
    for i, (lab, fml) in enumerate(rows_imp):
        r = r0 + 1 + i
        ws.cell(row=r, column=1, value=lab)
        for j, n in enumerate(names):
            c = get_column_letter(2 + j)
            ws.cell(row=r, column=2 + j, value=fml.format(c=c)).number_format = "0.0"
        if "EPS" in lab:
            ws.cell(row=r, column=5, value=fml.format(c="E")).number_format = "0.0"
    # multiples table
    r1 = r0 + len(rows_imp) + 3
    ws.cell(row=r1, column=1, value="Multiples (inputs)").font = BOLD
    ws.cell(row=r1, column=2, value="Low").font = BOLD; ws.cell(row=r1, column=3, value="Mid").font = BOLD; ws.cell(row=r1, column=4, value="High").font = BOLD
    ws.cell(row=r1, column=5, value="Rationale").font = BOLD
    rat = {"EV / FY27E adj. EBITDA": "WS12 recommendation: ABNB's own multiple vs growth 2023-26, 19-name cross-section, fade DCF all land 13.5-18.5x; today 16-18x",
           "P / FY27E GAAP EPS": "ABNB at $170 = 28x Street FY27 EPS; 2023-26 LTM GAAP P/E 25-40x; BKNG 16x, NFLX 21x, UBER 18x NTM",
           "EV / FY27E FCF": "WS12 haircut set 11.3/14.3/17.3x lifted for FCF running 2-7% above adj. EBITDA; today ~16x FY27E"}
    mult_row = {}
    for i, (lab, (lo, mi, hi)) in enumerate(MULT.items()):
        r = r1 + 1 + i; mult_row[lab] = r
        ws.cell(row=r, column=1, value=lab)
        for j, v in enumerate([lo, mi, hi]):
            cc = ws.cell(row=r, column=2 + j, value=v); cc.fill = YELLOW
        ws.cell(row=r, column=5, value=rat[lab]).font = GREY
    # target price grid
    r2 = r1 + len(MULT) + 3
    ws.cell(row=r2, column=1, value="Target price ($ / share, FY27E exit)").font = BOLD
    for j, n in enumerate(names):
        ws.cell(row=r2, column=2 + j, value=SCENARIOS[n]["label"]).font = BOLD
    ws.cell(row=r2, column=5, value="Street FY27 (P/E lens only)").font = BOLD
    ws.cell(row=r2, column=6, value="Upside vs price, Delivered case").font = BOLD
    r = r2 + 1
    tp_cells = {}
    for lab in MULT:
        for j2, lvl in enumerate(["Low", "Mid", "High"]):
            ws.cell(row=r, column=1, value=f"{lab} x {lvl}")
            mcell = f"${get_column_letter(2 + j2)}${mult_row[lab]}"
            for j, n in enumerate(names):
                c = get_column_letter(2 + j)
                if lab.startswith("P /"):
                    fml = f"={mcell}*{c}{mrow[('eps','O')]}"
                elif "EBITDA" in lab:
                    fml = f"=({mcell}*{c}{mrow[('ebitda','O')]}+{c}{mrow[('netcash','O')]})/{c}{mrow[('sh','L')]}"
                else:
                    fml = f"=({mcell}*{c}{mrow[('fcf','O')]}+{c}{mrow[('netcash','O')]})/{c}{mrow[('sh','L')]}"
                ws.cell(row=r, column=2 + j, value=fml).number_format = "0"
            if lab.startswith("P /"):
                ws.cell(row=r, column=5, value=f"={mcell}*E{mrow[('eps','O')]}").number_format = "0"
            ws.cell(row=r, column=6, value=f"=C{r}/$B$4-1").number_format = "0.0%"
            tp_cells[(lab, lvl)] = r
            r += 1
    ws.cell(row=r, column=1, value="Average of the three mid multiples").font = BOLD
    mids = [tp_cells[(lab, "Mid")] for lab in MULT]
    for j, n in enumerate(names):
        c = get_column_letter(2 + j)
        ws.cell(row=r, column=2 + j, value="=AVERAGE(" + ",".join(f"{c}{m}" for m in mids) + ")").number_format = "0"
    ws.cell(row=r, column=6, value=f"=C{r}/$B$4-1").number_format = "0.0%"
    avg_row = r
    r += 1
    ws.cell(row=r, column=1, value="Average of all nine cells").font = BOLD
    for j, n in enumerate(names):
        c = get_column_letter(2 + j)
        ws.cell(row=r, column=2 + j, value=f"=AVERAGE({c}{r2+1}:{c}{r2+9})").number_format = "0"
    ws.cell(row=r, column=6, value=f"=C{r}/$B$4-1").number_format = "0.0%"
    r += 2
    # DCF block (Python values)
    ws.cell(row=r, column=1, value="DCF on management FCF (Python-computed values, 10-year fade to 3%, WACC 10%; not live formulas)").font = BOLD
    r += 1
    hdrs = ["", *[SCENARIOS[n]["label"] for n in names]]
    for j, h in enumerate(hdrs):
        ws.cell(row=r, column=1 + j, value=h).font = BOLD
    r += 1
    dcf = {}
    for n in names:
        o = results[n]["out"]
        fcf27 = o["FY27"]["fcf"]; fcf26 = o["FY26"]["fcf"]
        g27 = fcf27 / fcf26 - 1
        sbc27 = o["FY27"]["sbc"]
        ev_today = PRICE * DILUTED_2Q26 - NET_CASH_2Q26
        dcf[n] = dict(
            fcf27=fcf27,
            g_fy27=g27 * 100,
            value_at_fy27_growth=(fade_dcf(fcf27, min(max(g27, 0.0), 0.2)) + NET_CASH_2Q26) / DILUTED_2Q26,
            implied_g_reported=implied_growth(ev_today, fcf27) * 100,
            implied_g_sbc_adj=implied_growth(ev_today, fcf27 - sbc27) * 100,
            sbc_adj_fcf27=fcf27 - sbc27,
        )
    lines = [("FY27E FCF ($M)", "fcf27", "#,##0"), ("FY27E FCF growth (%)", "g_fy27", "0.0"),
             ("DCF value/share today, FY28+ growth starting at the FY27 rate (capped 0-20%) fading to 3% ($)", "value_at_fy27_growth", "0"),
             ("Reverse DCF: FY28-36 starting growth the $%.2f EV requires, reported FCF (%%)" % PRICE, "implied_g_reported", "0.0"),
             ("FY27E SBC-adjusted FCF ($M)", "sbc_adj_fcf27", "#,##0"),
             ("Reverse DCF: starting growth required on SBC-adjusted FCF (%)", "implied_g_sbc_adj", "0.0")]
    for lab, k, fmt in lines:
        ws.cell(row=r, column=1, value=lab)
        for j, n in enumerate(names):
            ws.cell(row=r, column=2 + j, value=round(dcf[n][k], 3)).number_format = fmt
        r += 1
    ws.column_dimensions["A"].width = 78
    for c in "BCDE":
        ws.column_dimensions[c].width = 22
    ws.column_dimensions["F"].width = 30
    return dcf, avg_row


def build_street_sheet(wb):
    ws = wb.create_sheet("Street")
    ws["A1"] = "Consensus as pulled (comparison column, not an input)"; ws["A1"].font = Font(bold=True, size=13)
    rows = [
        ("3Q26E revenue ($M)", 4743.7, "Bloomberg FA consensus PDF (OneDrive, pulled 4 Sep 2026); Zacks $4,740M (7 est.)"),
        ("3Q26E nights (M)", 148.91, "Bloomberg FA; +11.1% y/y"),
        ("3Q26E GBV ($M)", 26352.9, "Bloomberg FA; +15.1%"),
        ("3Q26E ADR ($)", 177.02, "Bloomberg FA; +3.3%"),
        ("3Q26E take rate (%)", 18.0, "Bloomberg FA"),
        ("3Q26E adj. EBITDA ($M)", 2359.9, "Bloomberg FA; margin 49.7%"),
        ("3Q26E FCF ($M)", 1969.9, "Bloomberg FA"),
        ("3Q26E diluted EPS ($)", 2.88, "Bloomberg FA 2.86-2.88; Zacks 2.87 (11 est., 2.52-3.28)"),
        ("4Q26E revenue ($M)", 3154.0, "Bloomberg FA; Zacks $3,200M (10 est., 3,050-3,700)"),
        ("4Q26E nights (M)", 134.19, "Bloomberg FA; +10.1%"),
        ("4Q26E GBV ($M)", 22992.9, "Bloomberg FA; +12.7%"),
        ("4Q26E ADR ($)", 171.29, "Bloomberg FA; +2.3%"),
        ("4Q26E adj. EBITDA ($M)", 915.2, "Bloomberg FA; margin 29.0%"),
        ("4Q26E diluted EPS ($)", 0.85, "Bloomberg FA; Zacks 0.82"),
        ("FY26E revenue ($M)", 14130, "Zacks $14,100M (8 est.) / S&P Global $14,160M (43 analysts)"),
        ("FY26E EPS ($)", 5.255, "Zacks 5.23 / S&P 5.28"),
        ("FY26E FCF ($M)", 5350, "S&P Global via stockanalysis"),
        ("FY27E revenue ($M)", 15745, "Zacks $15,730M (13 est., 14,990-16,290) / S&P $15,760M"),
        ("FY27E EPS ($)", 6.08, "Zacks 6.02 (5.35-6.80) / S&P 6.14"),
        ("Mean price target ($)", 178.96, "46 analysts, S&P Global, 3 Sep 2026; range 125-220; yfinance 11 Sep mean 182.1, median 185"),
        ("Share price ($)", PRICE, PRICE_DATE),
    ]
    ws["A3"] = "Item"; ws["B3"] = "Value"; ws["C3"] = "Source"
    for c in "ABC":
        ws[f"{c}3"].font = BOLD; ws[f"{c}3"].fill = HDR
    for i, (a, b, c) in enumerate(rows):
        r = 4 + i
        ws[f"A{r}"] = a; ws[f"B{r}"] = b; ws[f"B{r}"].font = BLUE; ws[f"C{r}"] = c; ws[f"C{r}"].font = GREY
    ws.column_dimensions["A"].width = 30; ws.column_dimensions["B"].width = 12; ws.column_dimensions["C"].width = 110
    return ws


STATEMENTS = [
    # area, near-term (3Q26 / FY26) what they said, mid-term (FY27+) what they said, number in the Delivered case, reliability, source
    ("Nights & Seats Booked", "3Q26 'low double-digit growth'; FY26 'accelerated pace of Nights and Seats Booked we've observed'; 2Q26 +10.3% with every region up, expansion markets ~2x core, first-time bookers +11% (highest in four years), app nights +23% = 64% of total", "No number. 8 Sep: 'almost every market is accelerating', 'four of the five countries [70% of the business] are accelerating', India +60%; core business 'could probably be double the size'", "3Q26 +11.5%, 4Q26 +10.5%, FY27 +10.0%", "Bucket guides: 3 of 3 since 4Q25 printed ABOVE the range (+1 to +5pts). Directional guides 92% met (n=13)", "2Q26 letter p.6; 2Q26 call; Communacopia 8 Sep 2026"),
    ("ADR", "3Q26 'moderate increase in ADR due to mix shift and price appreciation'; 2Q26 +5% (+4% ex-FX), 'noticeable strength in North America and Europe'; bedroom nights +12% vs nights +10% (larger homes keep growing fastest)", "AI pricing model 'one of the biggest single levers for growth', 'many multiples bigger than RNPL' -> aimed at affordability, i.e. it argues for LOWER host prices over time, not higher; ADR ex-FX above ~3% is mix, not price", "ex-FX +3.5% 3Q26, +3.0% thereafter; FX +0.3 / -0.4 / -0.4 / 0 / +0.7 / 0 pp", "ADR floors/points 16 of 18 met or beaten", "2Q26 letter p.10; 2Q26 call (pricing answer)"),
    ("GBV", "3Q26 'mid teens' (nights low double digits + moderate ADR); 2Q26 +16% (+15% ex-FX); RNPL >20% of GBV, eligibility expanded in July", "'approaching $100 billion in GBV' (8 Sep); FY25 was $91.3bn, FY26 lands ~$106bn in the Delivered case", "3Q26 +15.4%, 4Q26 +13.4%, FY27 +13.3%", "Bucket guides beaten by 4-6pts in all three cases since 4Q25", "2Q26 letter; Communacopia"),
    ("Take rate / monetisation", "FY26 'relatively flat compared to 2025' (13.41%) after RNPL timing and 'higher customer incentives related to new businesses'; 'absent these incentives... slightly higher'; 3Q26 'relatively in-line'; single fee to be completed by year-end (half of listings already)", "Sponsored listings 'a pretty easy straight shot to $1 billion incremental high margin revenue' (8 Sep, undated); travel insurance 'very high margin... does quite well'; advertising deferred behind AI search", "flat in Literal/Delivered; +20bp FY27 in Ambition", "The weak line: 59% kept (n=17). FY25 promised +20bp, printed -16bp. 1Q26 'lift full-year take rate' withdrawn at 2Q26", "2Q26 call prepared remarks; 31a S165/S166/S110"),
    ("Cancellations / RNPL", "Not disclosed. Nights and GBV are reported net of cancellations. RNPL defers payment to near check-in; 2Q26: 'absent RNPL... unearned fees would have grown y/y'; 1Q26 letter predicted unearned fees higher y/y in 3Q26 (forward-testable on 5 Nov). 1Q26: Middle East cancellations cost ~1pt of nights", "Nothing. The team's own RNPL ledger (overnight2 D) models a -0.1 to -1.4pt cancellation drag on 3Q26/4Q26 nights; management has never sized it", "Inside the -0.6 to -1.1pp timing residual", "n/a (never guided)", "2Q26 call CFO; 1Q26 letter; docs/overnight2/SYNTHESIS.md"),
    ("Revenue", "3Q26 $4.69-4.77bn (+15-17%) incl. ~3pp FX after hedging; FY26 'at least mid teens' (raised from 'low double digits' in Feb and 'low-to-mid teens' in May)", "No FY27 number ('I'm not going to give you a specific guide for 2027 and beyond'). Pattern: Feb guide is a floor, raised twice, printed 1-3pp above", "3Q26 $4,815M (+17.6%), 4Q26 $3,131M (+12.7%), FY26 $14.23bn (+16.3%), FY27 $15.99bn (+12.4%)", "19 of 19 quarterly ranges beaten at the midpoint (median +2.5%, last eight +1.8%); 15 of 19 above the top", "2Q26 letter p.6; 02_guidance_ledger.csv"),
    ("FX", "~3pp tailwind to 3Q26 revenue after hedging (was 0 / +3 / +4 in 4Q25-2Q26); ADR FX 'significantly lower in Q2 than Q1'", "Silent; hedging programme unchanged. Consensus EUR path turns FX to a -0.4 to -1.0pp headwind from 4Q26", "WS29 schedule", "FX statements 100% kept but they only ever guide one quarter", "2Q26 letter; 28_fx-hedge-disclosures.md"),
    ("Adj. EBITDA margin", "FY26 'at least 35.5%' (raised from 'stable' -> '>=35%' -> '>=35.5%'); 3Q26 'down slightly compared to Q3 2025' (50.1%) 'due to timing of investments'; 2Q26 printed 35.0% (+1.3pts) on ops & support and product-dev efficiency, offset by S&M", "'There's a relative floor in our ability to continue to invest against that' (2Q26); 'we basically have remained pretty steady, 35% margins' (8 Sep); rule: find variable-cost efficiencies every year and reinvest most of them", "3Q26 50.0%, 4Q26 30.8%, FY26 36.2%, FY27 36.2%", "Total-margin statements 91% kept (n=43). Floors beaten by +140bp (FY24), +60bp (FY25). Floor becomes a point ('approximately X') at the Q3 print", "2Q26 letter; 31a note"),
    ("Cost lines", "Cost of revenue 'scale somewhat linearly'; ops & support cost per booking -16% y/y (AI resolves ~45% of tickets); product dev: 'we don't need to grow our head count at levels that we did in the past'; S&M: 'where you will see some incremental investment'; AI spend: guidance 'assumes a material increase' (unsized)", "No FY27 line has a number. Brand marketing is fixed per market ('surgical topper' for performance); hotels build-out unbudgeted; services are partnerships ('we do not see a big incurring of cost')", "Not modelled line by line here (margin is the policy variable per 31a); WS30/31 hold the line build", "Ops & support 100% kept (n=13); brand marketing 63% (n=35); product dev 60%; SBC 40%", "31a_mgmt-margin-statements.md"),
    ("SBC / share count", "FY26 SBC growth 'lower than 2025'; 1H26 +14.7%; 37.8M RSUs + 5.7M options outstanding; diluted WA 597M in 2Q26 (-4.6% y/y)", "Silent; the SBC-equals-headcount promise was withdrawn at 4Q25", "SBC +10% H2-26, +9% FY27; shares -4.5M/q net", "SBC guides 40% kept (n=5)", "4Q25 letter; 2Q26 10-Q"),
    ("Capital return", "$1.1bn repurchased in 2Q26, $2.1bn in 1H26; $3.4bn authorisation remaining (2Q26 call); 'returning capital to shareholders remains a core component'", "Nothing beyond the authorisation; at the current pace it is exhausted by ~2Q27, so a new programme is the likely 4Q26/1Q27 announcement", "$1,050M/q through FY27 ($4.2bn/yr)", "FY24 $3.4bn, FY25 $3.8bn delivered; never guided", "2Q26 call CFO; 10-Q"),
    ("Tax", "FY26 effective tax rate 'high teens' (FY25 20.0%; 1H26 17.1% incl. a $77M prior-year benefit)", "OBBBA long-term effective rate 'mid-to-high teens' (2Q26 call)", "18% throughout", "Tax statements 33% kept (n=3) but the FY26 direction is landing", "1Q26 / 2Q26 letters; 2Q26 call"),
    ("New businesses: hotels", "'Single-digit percentage of nights', growing ~3x faster than homes; 35% of first-time hotel guests come back to book a home; supply outreach expanded to top-20 cities; 'we are absolutely going to be stepping on the gas'", "'This other business that's, like, 10x larger' (8 Sep); 'international expansion of hotels... $ billions incremental revenue... nearly adjacent' (2Q26 horizon 2)", "Inside the nights growth (no separate line: management gives no hotel nights or revenue figure)", "New-business cost claims: 'not cost very much' (2Q24) missed by ~$200m in FY25", "2Q26 call; Communacopia"),
    ("New businesses: services, experiences, cars", "Services expanded May 2026 (groceries, car rental, airport pickup, luggage); Resort Passes; experiences supply +80%, bookings accelerating on a small base; car rentals 'one of the biggest sellers... at one point'", "Horizon 3, 'multi-year', 'not this year' for the 1-10-many industrialisation; 'every month you'll see an acceleration in new verticals launching'", "Zero incremental revenue in Literal/Delivered; the +20bp FY27 take rate in Ambition is the only place it enters", "Multi-year claims 48% kept (n=31); Chesky 57% (n=21)", "2Q26 call; Communacopia"),
    ("AI", "Customer service: ~45% of tickets AI-resolved in 50+ languages, cost per booking -16%; AI search in test on a small share of traffic, expanding through the year; 'ship 80% more features than a year ago'; guidance assumes a 'material increase' in AI spend; 'we are not buying up a whole bunch of GPUs'", "'The next 18 months to 24 months... a massive shift from enterprise to consumer' AI; full trip-planning agent within ~18 months; sponsored listings gated behind AI search", "In the margin floor; no separate line", "Support-cost claim landed; engineering-productivity claim (+30%, since 1Q23) has never shown in a filed number", "2Q26 call; 31a section (d); Communacopia"),
    ("Regulation", "Not in guidance. 2Q26 letter: usual risk-factor language only", "Nothing", "Zero; the team's regulatory Monte Carlo (PR #15) is the only quantification", "n/a", "regulatory package, PR #19"),
]


def build_statements_sheet(wb):
    ws = wb.create_sheet("Mgmt_Statements")
    ws["A1"] = "What management is looking at, by area: near term (3Q26 / FY26), mid term (FY27+), how it enters the Delivered case, and how reliable that line has been"; ws["A1"].font = Font(bold=True, size=13)
    hdr = ["Area", "Near term: what they said (3Q26 / FY26)", "Mid term: what they said (FY27 and beyond)", "Number used (Delivered case)", "Track record of this line", "Source"]
    for j, h in enumerate(hdr):
        c = ws.cell(row=3, column=1 + j, value=h); c.font = BOLD; c.fill = HDR
    for i, row in enumerate(STATEMENTS):
        for j, v in enumerate(row):
            c = ws.cell(row=4 + i, column=1 + j, value=v); c.alignment = Alignment(wrap_text=True, vertical="top")
    widths = [24, 70, 60, 34, 40, 34]
    for j, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(1 + j)].width = w
    return ws


def build_workbook(results):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    cover = wb.create_sheet("Cover")
    cover["A1"] = "ABNB: the management-implied model"; cover["A1"].font = Font(bold=True, size=14)
    txt = [
        f"Built {PRICE_DATE} by analysis/src/reverse_dcf/mgmt_implied_model.py. Rebuild with: py -3.13 analysis/src/reverse_dcf/mgmt_implied_model.py",
        "Question: if what management says is true, what is the stock worth? Three translations of the words into numbers, each on its own sheet:",
        "  Mgmt_Literal    - the guide at face value (range midpoints, floors as points, buckets at the low end; FY27 = the Feb-2027 guide on management's pattern)",
        "  Mgmt_Delivered  - the guide plus management's own cushion (revenue +1.8% vs midpoint, nights 1pt above the bucket, FY margin floor +70bp); FY27 = FY26 exit rate, margin flat",
        "  Mgmt_Ambition   - the 8 Sep 2026 CEO framing (accelerating everywhere, hotels 3x, take rate +20bp in FY27, margin 37%)",
        "Valuation      - FY27E exit multiples (EV/EBITDA, P/E, EV/FCF; inputs) and a DCF / reverse DCF on management FCF",
        "Street         - consensus as pulled (Bloomberg FA 4 Sep, Zacks 4 Sep, S&P Global 3 Sep) for comparison only",
        "Mgmt_Statements- what management is looking at by area, near and mid term, with the hit rate of each line",
        "Recon          - Excel recalculated values vs the Python mirror (must be all zeros)",
        "Conventions: yellow = input, blue = reported history, black = formula. Every input carries its source in column P. Management is silent on all FY27 lines: FY27 inputs are the analyst's reading of the stated algorithm.",
        "Not in this workbook: line-by-line cost build (WS30/31), regional nights (WS10), the team's own forecasts (WS29 bridge), any market-implied case (next step).",
    ]
    for i, t in enumerate(txt):
        cover[f"A{3+i}"] = t
    cover.column_dimensions["A"].width = 160
    for n in results:
        build_scenario_sheet(wb, n, results[n])
    dcf, avg_row = build_valuation_sheet(wb, results)
    build_street_sheet(wb)
    build_statements_sheet(wb)
    wb.create_sheet("Recon")
    wb.save(OUT_XLSX)
    return dcf


def excel_recalc():
    """Open the workbook in Excel, force a full recalculation and save, so cached values exist for openpyxl."""
    import time
    import pythoncom
    import win32com.client as w
    for attempt in range(5):
        try:
            pythoncom.CoInitialize()
            app = w.DispatchEx("Excel.Application")
            app.DisplayAlerts = False
            wbx = app.Workbooks.Open(os.path.abspath(OUT_XLSX))
            app.CalculateFullRebuild()
            wbx.Save(); wbx.Close(False); app.Quit()
            del wbx, app
            pythoncom.CoUninitialize()
            time.sleep(1.0)
            return
        except Exception as e:  # COM is flaky right after a previous Quit
            print("excel recalc retry", attempt, e)
            time.sleep(2.0)
    raise RuntimeError("Excel recalculation failed")


def excel_recalc_and_recon(results):
    excel_recalc()
    wb = openpyxl.load_workbook(OUT_XLSX, data_only=True)
    rows = []
    keys = ["nights", "gbv", "adr", "rev", "take", "margin", "ebitda", "sbc", "da", "opinc", "pretax", "tax", "ni", "sh", "eps", "fcf", "netcash"]
    for n, res in results.items():
        ws = wb[f"Mgmt_{n}"]
        for per in FQ + ["FY26", "FY27"]:
            for k in keys:
                xv = ws[f"{COLS[per]}{ROWNUM[k]}"].value
                pv = res["out"][per][k]
                rows.append(dict(scenario=n, period=per, line=k, excel=xv, python=pv, diff=(None if xv is None else xv - pv)))
    rec = pd.DataFrame(rows)
    rec.to_csv(os.path.join(OUT_DIR, "mgmt_implied_recon.csv"), index=False)
    # write recon sheet
    wb2 = openpyxl.load_workbook(OUT_XLSX)
    ws = wb2["Recon"]
    ws["A1"] = "Excel (recalculated) vs Python mirror; max abs diff:"; ws["B1"] = float(rec["diff"].abs().max())
    for j, h in enumerate(rec.columns):
        ws.cell(row=3, column=1 + j, value=h).font = BOLD
    for i, r in enumerate(rec.itertuples(index=False)):
        for j, v in enumerate(r):
            ws.cell(row=4 + i, column=1 + j, value=(float(v) if isinstance(v, (np.floating,)) else v))
    wb2.save(OUT_XLSX)
    # openpyxl drops cached values on save: recalculate through Excel again so the file opens with values and can be read back
    excel_recalc()
    # read target-price grid values for the summary
    wbv = openpyxl.load_workbook(OUT_XLSX, data_only=True)["Valuation"]
    grid = {}
    for row in wbv.iter_rows(min_row=1, max_row=80, max_col=6, values_only=True):
        if (row[0] and isinstance(row[0], str) and " x " in row[0] and any(row[0].startswith(m) for m in MULT)) or (row[0] in ("Average of the three mid multiples", "Average of all nine cells")):
            grid[row[0]] = row[1:4]
    return rec, grid


def main():
    results = {n: run(n) for n in SCENARIOS}
    dcf = build_workbook(results)
    rec, grid = excel_recalc_and_recon(results)
    print("recon max abs diff:", rec["diff"].abs().max())
    # summary csv
    rows = []
    for n, res in results.items():
        for per in FQ + ["FY25", "FY26", "FY27"]:
            o = res["out"][per]
            rows.append(dict(scenario=n, period=per, nights_m=o["nights"], gbv_musd=o["gbv"], adr_usd=o["adr"], revenue_musd=o["rev"], take_rate_pct=o["take"],
                             adj_ebitda_musd=o["ebitda"], adj_ebitda_margin_pct=o["margin"], sbc_musd=o["sbc"], net_income_musd=o["ni"], diluted_shares_m=o["sh"],
                             eps_gaap=o["eps"], fcf_musd=o["fcf"], net_cash_musd=o["netcash"]))
    pd.DataFrame(rows).round(3).to_csv(os.path.join(OUT_DIR, "mgmt_implied_summary.csv"), index=False)
    # inputs csv
    irows = []
    for n, res in results.items():
        for q, d in res["inputs"].items():
            irows.append(dict(scenario=n, quarter=q, **d))
    pd.DataFrame(irows).round(4).to_csv(os.path.join(OUT_DIR, "mgmt_implied_inputs.csv"), index=False)
    # target grid csv
    g = pd.DataFrame([(k, *v) for k, v in grid.items()], columns=["lens", *SCENARIOS.keys()])
    g.to_csv(os.path.join(OUT_DIR, "mgmt_implied_targets.csv"), index=False)
    pd.DataFrame(dcf).T.round(3).to_csv(os.path.join(OUT_DIR, "mgmt_implied_dcf.csv"))
    # console summary
    pd.set_option("display.width", 200)
    for n, res in results.items():
        o = res["out"]
        print(f"\n== {n}: timing 3Q26 {res['timing']['3Q26']:.2f}pp, 4Q26 {res['timing']['4Q26']:.2f}pp; margin chg 4Q26 {res['mchg']['4Q26']:+.2f}, FY27 {res['mchg']['1Q27']:+.2f}")
        for per in ["3Q26", "4Q26", "FY26", "FY27"]:
            d = o[per]
            print(f"  {per}: nights {d['nights']:.1f} rev {d['rev']:,.0f} ({(d['rev']/o[PY.get(per,'FY25' if per=='FY26' else 'FY26')]['rev']-1)*100 if per in PY else (d['rev']/o['FY25' if per=='FY26' else 'FY26']['rev']-1)*100:+.1f}%) take {d['take']:.2f} ebitda {d['ebitda']:,.0f} margin {d['margin']:.1f} eps {d['eps']:.2f} fcf {d['fcf']:,.0f} netcash {d['netcash']:,.0f} sh {d['sh']:.0f}")
    print("\nTarget grid:\n", g.to_string())
    print("\nDCF:\n", pd.DataFrame(dcf).T.round(2).to_string())


if __name__ == "__main__":
    main()
