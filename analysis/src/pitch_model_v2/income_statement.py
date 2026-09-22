"""pitch_model_v2 / income_statement.py — rows 12–36 of the official model's Income_Statement.

History (1Q23–2Q26) is PLUGGED from the reconciled financial panel: reported lines are reported, not
reconstructed. Forecast (3Q26–4Q27) is LIVE: the cost lines and the below-the-line parameters are plugged
from the finished 40_line_build stack (DEC-0022), and everything above and below them is an Excel formula,
so the margin is an OUTPUT of our own nights × ADR × take rate, not an assumption.

Nothing here forecasts a cost line or a margin. The only modelled object is the take rate:
  * 3Q26 and 4Q26   — Street-implied, per DEC-0018 (Street revenue ÷ Street nights × Street ADR).
  * 1Q27 onward     — the seasonal naive τ[q−4], the cyclical carry that D7 found beats every fitted
                      take-rate object on both windows, and which management's "relatively flat
                      year-over-year" guidance supports. No level drift is imposed.

Sources
  history   data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv  (USD m, costs positive)
  forecast  data/processed/margin_build/40_line_build/40_lines_quarterly.csv, scenario `base`
  Street    docs/pitch-model-v2/dossiers/V1_v1_street.md §2a; LSEG 06_consensus_quarterly_2027.csv;
            Bloomberg MODL 12 Sep 2026 via E_street_distribution_vs_team.csv (DEC-0005)

Called by adr_engine/workbook.py on the live Workbook, before save, so the nights and ADR charts survive.
"""
from __future__ import annotations
import pandas as pd
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L

ROOT_REL = "data/processed"
PANEL = "margin_build/02_financial_panel/02_panel_quarterly.csv"
ANNUAL = "margin_build/02_financial_panel/02_panel_annual.csv"
LINES = "margin_build/40_line_build/40_lines_quarterly.csv"

HIST = [f"{q}Q{y}" for y in range(23, 27) for q in range(1, 5)][:14]      # 1Q23..2Q26
FCST = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
ALLQ = HIST + FCST
COL = {lab: 3 + i for i, lab in enumerate(ALLQ)}                           # C..V
FY = {"FY23": (24, "1Q23", "4Q23"), "FY24": (25, "1Q24", "4Q24"), "FY25": (26, "1Q25", "4Q25"),
      "FY26": (27, "1Q26", "4Q26"), "FY27": (28, "1Q27", "4Q27")}

# Street inputs, DEC-0005 / DEC-0018. (revenue $m, nights m, ADR $)
STREET = {"3Q26": (4744.32, 149.0, 177.06), "4Q26": (3161.82, 134.0, 171.33)}
ETR = {"3Q26": 0.180, "4Q26": 0.180, "1Q27": 0.175, "2Q27": 0.175, "3Q27": 0.175, "4Q27": 0.175}

R = dict(REV=12, REVY=13, TAKE=14, COR=16, OPS=17, PD=18, SM=19, GA=20, TOT=21, TOTP=22, DA=23,
         EBITDA=24, MARGIN=25, ADDBK=26, SBC=27, OPINC=28, II=29, IE=30, OTH=31, PBT=32, TAX=33,
         NI=34, SH=35, EPS=36)

F_IN = Font(name="Arial", color="0000FF", size=10)      # plug, with a source
F_FX = Font(name="Arial", color="000000", size=10)      # formula
F_NOTE = Font(name="Arial", italic=True, color="666666", size=9)
FILL_NONE = PatternFill(fill_type=None)
USD, PCT, PCT1, NUM2, NUM1 = "#,##0", "0.00%", "0.0%", "0.00", "0.0"


def take_rate_path(panel: pd.DataFrame) -> tuple[dict, dict]:
    """Street-implied where the Street covers the quarter; seasonal naive tau[q-4] beyond it."""
    hist = panel.set_index("quarter").take_rate_pct
    t, how = {}, {}
    for q, (rev, nights, adr) in STREET.items():
        t[q] = rev / (nights * adr) * 100.0
        how[q] = "Street-implied (DEC-0018): Street revenue / (Street nights x Street ADR)"
    for q in ["1Q27", "2Q27", "3Q27", "4Q27"]:
        prior = f"{q[0]}Q{int(q[2:]) - 1}"
        t[q] = float(hist[prior]) if prior in hist.index else t[prior]
        src = "reported" if prior in hist.index else "Street-implied"
        how[q] = f"cyclical: seasonal naive, carries {prior} {src} ({t[q]:.3f}%), no drift imposed"
    return t, how


def build(wb, root):
    """Fill Income_Statement rows 12-36. `root` is the repo root Path."""
    panel = pd.read_csv(root / ROOT_REL / PANEL)
    ph = panel[panel.quarter.isin(HIST)].set_index("quarter")
    lines = pd.read_csv(root / ROOT_REL / LINES)
    fb = lines[lines.scenario == "base"].set_index("quarter")
    ann = pd.read_csv(root / ROOT_REL / ANNUAL).set_index("year")
    take, how = take_rate_path(panel)
    ws = wb["Income_Statement"]

    def put(r, c, v, font=F_FX, fmt=None):
        cell = ws.cell(r, c, v); cell.font = font; cell.fill = FILL_NONE
        if fmt: cell.number_format = fmt
        return cell

    def note(r, text):
        ws.cell(r, 2, text).font = F_NOTE

    # ---------------- history: reported lines are plugged, ratios are formulas ----------------
    plug = {R["REV"]: "revenue", R["COR"]: "cor_cash", R["OPS"]: "ops_cash", R["PD"]: "pd_cash",
            R["SM"]: "sm_cash", R["GA"]: "ga_cash_ex_lodging", R["DA"]: "da",
            R["SBC"]: "sbc_total_is", R["OPINC"]: "op_income", R["II"]: "interest_income",
            R["IE"]: "interest_expense", R["OTH"]: "other_income_expense", R["PBT"]: "pretax_income",
            R["TAX"]: "tax_provision", R["NI"]: "net_income", R["SH"]: "shares_diluted_m",
            R["EPS"]: "eps_diluted", R["EBITDA"]: "adj_ebitda_reported"}
    for q in HIST:
        c = COL[q]
        for r, col in plug.items():
            v = ph.loc[q, col]
            fmt = NUM2 if r == R["EPS"] else (NUM1 if r == R["SH"] else USD)
            put(r, c, None if pd.isna(v) else float(v), F_IN, fmt)
        put(R["ADDBK"], c, float(ph.loc[q, "other_addbacks_total"] - ph.loc[q, "lodging_tax_reserves"]), F_IN, USD)
        put(R["TOT"], c, f"=SUM({L(c)}{R['COR']}:{L(c)}{R['GA']})", F_FX, USD)
    put(R["IE"], COL["1Q24"], 0.0, F_IN, USD)     # not separately disclosed; sits in other income/(expense)

    # ---------------- forecast: costs and below-the-line plugged, the rest live ----------------
    for q in FCST:
        c, C = COL[q], L(COL[q])
        put(R["TAKE"], c, float(take[q]) / 100.0, F_IN, "0.000%")
        put(R["REV"], c, f"={C}8*1000*{C}{R['TAKE']}", F_FX, USD)      # GBV ($bn) x take rate
        for r, col in ((R["COR"], "cor_cash"), (R["OPS"], "ops_cash"), (R["PD"], "pd_cash"),
                       (R["SM"], "sm_cash"), (R["GA"], "ga_cash_ex_lodging"), (R["DA"], "da"),
                       (R["SBC"], "sbc"), (R["II"], "interest_income"), (R["IE"], "interest_expense"),
                       (R["OTH"], "other_income"), (R["SH"], "diluted_shares_m")):
            put(r, c, float(fb.loc[q, col]), F_IN, NUM1 if r == R["SH"] else USD)
        put(R["ADDBK"], c, float(fb.loc[q, "lodging_reserves"]), F_IN, USD)
        put(R["TOT"], c, f"=SUM({C}{R['COR']}:{C}{R['GA']})", F_FX, USD)
        put(R["EBITDA"], c, f"={C}{R['REV']}-{C}{R['TOT']}+{C}{R['DA']}+{C}{R['ADDBK']}", F_FX, USD)
        put(R["OPINC"], c, f"={C}{R['EBITDA']}-{C}{R['DA']}-{C}{R['SBC']}", F_FX, USD)
        put(R["PBT"], c, f"={C}{R['OPINC']}+{C}{R['II']}-{C}{R['IE']}+{C}{R['OTH']}", F_FX, USD)
        put(R["TAX"], c, f"={C}{R['PBT']}*{ETR[q]}", F_FX, USD)
        put(R["NI"], c, f"={C}{R['PBT']}-{C}{R['TAX']}", F_FX, USD)
        put(R["EPS"], c, f"={C}{R['NI']}/{C}{R['SH']}", F_FX, NUM2)

    # ---------------- ratios and y/y, both halves ----------------
    for q in ALLQ:
        c, C = COL[q], L(COL[q])
        put(R["TOTP"], c, f"={C}{R['TOT']}/{C}{R['REV']}", F_FX, PCT)
        put(R["MARGIN"], c, f"={C}{R['EBITDA']}/{C}{R['REV']}", F_FX, PCT)
        if q in HIST:                                  # forecast take rate is the input, history derives it
            put(R["TAKE"], c, f"={C}{R['REV']}/({C}8*1000)", F_FX, "0.000%")
        i = ALLQ.index(q)
        if i >= 4:
            p = L(COL[ALLQ[i - 4]])
            put(R["REVY"], c, f"={C}{R['REV']}/{p}{R['REV']}-1", F_FX, PCT1)

    # ---------------- FY columns ----------------
    flows = [R["REV"], R["COR"], R["OPS"], R["PD"], R["SM"], R["GA"], R["TOT"], R["DA"], R["EBITDA"],
             R["ADDBK"], R["SBC"], R["OPINC"], R["II"], R["IE"], R["OTH"], R["PBT"], R["TAX"], R["NI"]]
    for name, (c, q0, q1) in FY.items():
        a, b, C = L(COL[q0]), L(COL[q1]), L(c)
        for r in flows:
            put(r, c, f"=SUM({a}{r}:{b}{r})", F_FX, USD)
        put(R["TOTP"], c, f"={C}{R['TOT']}/{C}{R['REV']}", F_FX, PCT)
        put(R["MARGIN"], c, f"={C}{R['EBITDA']}/{C}{R['REV']}", F_FX, PCT)
        put(R["TAKE"], c, f"={C}{R['REV']}/(SUM({a}8:{b}8)*1000)", F_FX, "0.000%")
        # fully-historical years take the reported annual share count and EPS: the company weights shares
        # across the year, which a mean of four quarterly counts does not reproduce (FY23 off by $0.03).
        yr = 2000 + int(name[2:])
        if name in ("FY23", "FY24", "FY25") and yr in ann.index:
            put(R["SH"], c, float(ann.loc[yr, "shares_diluted_m"]), F_IN, NUM1)
            put(R["EPS"], c, float(ann.loc[yr, "eps_diluted"]), F_IN, NUM2)
        else:
            put(R["SH"], c, f"=AVERAGE({a}{R['SH']}:{b}{R['SH']})", F_FX, NUM1)
            put(R["EPS"], c, f"={C}{R['NI']}/{C}{R['SH']}", F_FX, NUM2)
        if name in ("FY24", "FY25", "FY26", "FY27"):
            put(R["REVY"], c, f"={C}{R['REV']}/{L(c-1)}{R['REV']}-1", F_FX, PCT1)

    # ---------------- notes ----------------
    note(R["REV"], "A: reported. E: = GBV x take rate (DEC-0018), so revenue is an output of lines 1-2")
    note(R["TAKE"], "A: = revenue / GBV. E: 3Q26-4Q26 Street-implied; 1Q27+ seasonal naive tau[q-4], no drift")
    note(R["COR"], "cash = GAAP less SBC. A: 02_panel_quarterly. E: 40_line_build base, carried in dollars (DEC-0022)")
    note(R["GA"], "ex lodging/withholding-tax reserves (4Q23 carried $931m); reserves sit in the add-back row")
    note(R["EBITDA"], "A: as reported. E: = revenue - cash costs + D&A + add-backs; margin is therefore an OUTPUT")
    note(R["ADDBK"], "memo, feeds Adj. EBITDA: lodging-tax reserves and other add-backs (acquisition, IPO, restructuring)")
    note(R["SBC"], "A: income-statement footnote total. E: 40_line_build (SBC[q-4] x 1.1318, M7 parameter sheet)")
    note(R["OPINC"], "A: reported GAAP. E: = Adj. EBITDA - D&A - SBC (holds exactly in the line build)")
    note(R["TAX"], "E: effective rate 18.0% FY26 / 17.5% FY27 (M7 parameter sheet), applied to our own pre-tax")
    note(R["EPS"], "E: = net income / diluted shares; shares -5.324m per quarter (M7)")
    ws.cell(7, 2, "history 1Q23-2Q26 plugged from 02_panel_quarterly.csv (reported); forecast cost lines and "
                  "below-the-line plugged from 40_line_build base (DEC-0022); blue = plug, black = formula").font = F_NOTE

    # ---------------- cross-checks and the open choices this line does NOT settle ----------------
    F_SEC = Font(name="Arial", bold=True, color="FFFFFF", size=10)
    r0 = 38
    for c in range(1, 29):
        ws.cell(r0, c).fill = PatternFill("solid", fgColor="222222"); ws.cell(r0, c).font = F_SEC
    ws.cell(r0, 1, "Cross-checks against the Street, and the open choices this line does not settle "
                   "(memo rows - none of these feed the statement above)")
    lab = lambda r, s, n=None: (ws.cell(r, 1, s).__setattr__("font", Font(name="Arial", size=10)),
                                n and ws.cell(r, 2, n).__setattr__("font", F_NOTE))
    lab(r0 + 1, "Street revenue ($m)", "LSEG 06_consensus_quarterly_2027.csv, 13 Sep 2026 pull")
    lab(r0 + 2, "    ours vs Street", "negative = our nights/ADR lines sit below consensus")
    lab(r0 + 3, "Street adj. EBITDA ($m)", "LSEG; n 36-37 for 3Q26/4Q26, n 17-19 for 2027")
    lab(r0 + 4, "    ours vs Street", "wider than the revenue gap because cost dollars are carried flat")
    lab(r0 + 5, "memo: adj. EBITDA if costs flexed to hold the line build's own margin",
        "DEC-0022 carries dollars flat; C4 asks whether management's margin sentence is a budget (costs flex) or a floor")
    lab(r0 + 6, "    difference vs the statement above", "the cost of the flat-dollar assumption, in EBITDA $m")
    lab(r0 + 7, "memo: DEC-0023 hosting step, B08 alternative ($85.0m/q vs the $100.21m/$111.71m plugged)",
        "NOT CHOSEN - both sides on record; positive = EBITDA if the lower B08 hosting number is right")
    st_rev = {"3Q26": 4744.32, "4Q26": 3161.82, "1Q27": 3010.32, "2Q27": 4036.94, "3Q27": 5269.97, "4Q27": 3528.92}
    st_eb = {"3Q26": 2361.52, "4Q26": 913.68, "1Q27": 610.73, "2Q27": 1451.71, "3Q27": 2695.55, "4Q27": 1068.40}
    for q in FCST:
        c, C = COL[q], L(COL[q])
        lb_margin = float(fb.loc[q, "adj_ebitda_margin_pct"]) / 100.0
        hosting_alt = float(fb.loc[q, "cor_hosting"]) - 85.0
        put(r0 + 1, c, st_rev[q], F_IN, USD)
        put(r0 + 2, c, f"={C}{R['REV']}/{C}{r0+1}-1", F_FX, PCT1)
        put(r0 + 3, c, st_eb[q], F_IN, USD)
        put(r0 + 4, c, f"={C}{R['EBITDA']}/{C}{r0+3}-1", F_FX, PCT1)
        put(r0 + 5, c, f"={C}{R['REV']}*{lb_margin}", F_FX, USD)
        put(r0 + 6, c, f"={C}{r0+5}-{C}{R['EBITDA']}", F_FX, USD)
        put(r0 + 7, c, hosting_alt, F_IN, USD)
    return take, how
