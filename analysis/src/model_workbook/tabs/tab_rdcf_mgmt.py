"""Tab 'Reverse DCF - Mgmt': the management-implied model (Literal / Delivered / Ambition cases).

Every number is read from data/processed/reverse_dcf/mgmt_implied_*.csv (built by
analysis/src/reverse_dcf/management_implied_model.py); the statements table is read from the
Mgmt_Statements sheet of model/ABNB_management_implied.xlsx. Blue = source value, black = formula.
Percent columns in the CSVs are stored as 11.5 meaning 11.5% and are divided by 100 here (style.pct).
"""
from __future__ import annotations
import math
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
import style as S

SHEET = "Reverse DCF - Mgmt"
REF_PRICE = 170.19
CASES = ["Literal", "Delivered", "Ambition"]
QTRS = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
NCOLS = 20

# (csv column, row label, number format, is_percent)
METRICS = [
    ("nights_m", "Nights & seats booked (m)", S.FMT_M1, False),
    ("gbv_musd", "Gross booking value ($m)", S.FMT_M, False),
    ("adr_usd", "ADR ($)", S.FMT_USD, False),
    ("revenue_musd", "Revenue ($m)", S.FMT_M, False),
    ("take_rate_pct", "Take rate (revenue / GBV)", S.FMT_PCT2, True),
    ("adj_ebitda_musd", "Adj. EBITDA ($m)", S.FMT_M, False),
    ("adj_ebitda_margin_pct", "Adj. EBITDA margin", S.FMT_PCT, True),
    ("sbc_musd", "Stock-based compensation ($m)", S.FMT_M, False),
    ("net_income_musd", "GAAP net income ($m)", S.FMT_M, False),
    ("diluted_shares_m", "Diluted shares (m)", S.FMT_M1, False),
    ("eps_gaap", "GAAP diluted EPS", S.FMT_EPS, False),
    ("fcf_musd", "Free cash flow ($m)", S.FMT_M, False),
    ("net_cash_musd", "Net cash ($m)", S.FMT_M, False),
]

# (csv column, row label, unit kind)
INPUTS = [
    ("nights", "Nights growth y/y", "pct"),
    ("adr", "ADR growth ex-FX y/y", "pct"),
    ("adr_fx", "ADR FX effect (pp)", "pp"),
    ("tr_rel", "Take-rate change vs prior year (pp)", "pp"),
    ("revfx", "Revenue FX after hedging (pp)", "pp"),
    ("timing", "Timing / RNPL residual (pp of revenue growth)", "pp"),
    ("sbc", "SBC growth y/y", "pct"),
    ("da_pct", "D&A (% of revenue)", "pct"),
    ("intinc", "Interest income ($m)", "m"),
    ("intexp", "Interest expense ($m)", "m"),
    ("tax", "Effective tax rate", "pct"),
    ("bb", "Buybacks ($m)", "m"),
    ("bb_price", "Buyback price ($)", "usd"),
    ("rsu_net", "Net RSU issuance (m shares)", "m1"),
    ("fcf_conv", "FCF / adj. EBITDA (x)", "x2"),
    ("margin_chg", "Adj. EBITDA margin change y/y (pp)", "pp"),
]
UNIT_FMT = {"pct": S.FMT_PCT, "pp": S.FMT_PP, "m": S.FMT_M, "usd": S.FMT_USD, "m1": S.FMT_M1, "x2": '0.00"x"'}

DCF_ROWS = [
    ("fcf27", "FY27E free cash flow, reported ($m)", S.FMT_M, False),
    ("sbc_adj_fcf27", "FY27E free cash flow less SBC ($m)", S.FMT_M, False),
    ("g_fy27", "FY27E FCF growth y/y", S.FMT_PCT, True),
    ("implied_g_reported", "Implied FCF growth FY28+ on reported FCF (price = $170.19)", S.FMT_PCT, True),
    ("implied_g_sbc_adj", "Implied FCF growth FY28+ on SBC-adjusted FCF", S.FMT_PCT, True),
    ("value_at_fy27_growth", "Value per share if FY27 FCF growth were sustained ($)", S.FMT_USD, False),
]


def _v(x):
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        pass
    return x.item() if hasattr(x, "item") else x


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    return df.astype(object).where(df.notna(), None)


def _h(text: str, chars: int = 175) -> float:
    return max(15.0, 13.5 * math.ceil(len(text) / chars))


def _band(ws, row: int, groups: list, first_col: int) -> int:
    """Merged navy band naming each scenario above its period columns. groups = [(name, ncols), ...]."""
    c = first_col
    for name, n in groups:
        cell = ws.cell(row=row, column=c, value=name)
        cell.font = S.f_hdr()
        cell.alignment = Alignment(horizontal="center")
        for k in range(c, c + n):
            ws.cell(row=row, column=k).fill = S.FILL_HEADER
        if n > 1:
            ws.merge_cells(start_row=row, start_column=c, end_row=row, end_column=c + n - 1)
        c += n
    return row + 1


def _load_statements() -> pd.DataFrame | None:
    """Mgmt_Statements sheet of the management workbook (values only): Area x near/mid term/number/track record."""
    path = S.REPO / "model" / "ABNB_management_implied.xlsx"
    if not path.exists():
        return None
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True, read_only=True)
    if "Mgmt_Statements" not in wb.sheetnames:
        return None
    rows = [r for r in wb["Mgmt_Statements"].iter_rows(values_only=True)]
    hdr_i = next((i for i, r in enumerate(rows) if r and r[0] == "Area"), None)
    if hdr_i is None:
        return None
    hdr = [h for h in rows[hdr_i] if h is not None]
    body = [list(r[: len(hdr)]) for r in rows[hdr_i + 1:] if r and r[0]]
    return pd.DataFrame(body, columns=hdr)


def build(wb):
    ws = wb.create_sheet(SHEET)
    widths = {get_column_letter(i): 13 for i in range(2, NCOLS + 1)}
    r = S.setup(ws, "Reverse DCF - Management-implied: what management's words are worth",
                "Three readings of the guide (Literal / Delivered / Ambition), FY26E-FY27E by quarter, implied prices at "
                "the team's multiples, and a reverse DCF on management's own FCF. Source: management-implied model, 12 Sep 2026.",
                widths=widths, label_width=46)

    summ = S.read("reverse_dcf/mgmt_implied_summary.csv")
    inputs = S.read("reverse_dcf/mgmt_implied_inputs.csv")
    targets = S.read("reverse_dcf/mgmt_implied_targets.csv")
    dcf = S.read("reverse_dcf/mgmt_implied_dcf.csv", index_col=0)
    try:
        comp = S.read("reverse_dcf/market/market_implied_comparison.csv")
        street_rev = float(comp.loc[comp["who"].str.startswith("Street"), "fy27_revenue_musd"].iloc[0])
    except Exception:
        street_rev = None

    def cell(case, period, colname):
        return float(summ.loc[(summ.scenario == case) & (summ.period == period), colname].iloc[0])

    # ---------------------------------------------------------------- a. framing
    r = S.section(ws, r, "What this tab says", ncols=NCOLS)
    d27, d26 = ({m: cell("Delivered", p, m) for m, *_ in METRICS} for p in ("FY27", "FY26"))
    mid = targets.set_index("lens").loc["Average of the three mid multiples"]
    lit_mid, del_mid, amb_mid = (float(mid[c]) for c in CASES)
    dcf_del = dcf.loc["Delivered"]
    street_txt = f" (${street_rev:,.0f}m)" if street_rev else ""
    lines = [
        "LITERAL = the guide taken at its word: range midpoints, floors as points, buckets ('low double digits') at the "
        "low end; FY27 is the guide management would give in Feb 2027 on its own pattern (floor carried).",
        "DELIVERED = the guide plus management's own cushion: quarterly revenue +1.8% vs the midpoint (median of the last "
        "eight prints; 19 of 19 ranges beaten), nights one point above the bucket top (3 of 3 bucket guides since 4Q25 "
        "printed above range), FY margin floor +70bp (FY24 +140, FY25 +60); FY27 holds the FY26 exit rate with margin flat.",
        "AMBITION = the 8 Sep 2026 CEO framing ('almost every market is accelerating', hotels 3x homes, India +60%, "
        "sponsored listings 'a straight shot to $1bn'): take rate +20bp in FY27, margin drifting to 37%.",
        f"Headline (Delivered, FY27E): revenue ${d27['revenue_musd']:,.0f}m (+{d27['revenue_musd']/d26['revenue_musd']-1:.1%}), "
        f"nights {d27['nights_m']:,.1f}m (+{d27['nights_m']/d26['nights_m']-1:.1%}), adj. EBITDA ${d27['adj_ebitda_musd']:,.0f}m "
        f"at a {d27['adj_ebitda_margin_pct']:.1f}% margin, GAAP EPS ${d27['eps_gaap']:.2f}, FCF ${d27['fcf_musd']:,.0f}m. "
        f"The Street's FY27 revenue{street_txt} is the Delivered case; the sell-side mean target (~$182) is the Delivered "
        f"case at 16-17x EBITDA.",
        f"At the team's mid multiples (16.5x EV/EBITDA, 27x P/E, 17x EV/FCF) the three cases are worth ${lit_mid:,.0f} / "
        f"${del_mid:,.0f} / ${amb_mid:,.0f} (Literal / Delivered / Ambition) against ${REF_PRICE:.2f}, i.e. "
        f"{lit_mid/REF_PRICE-1:+.0%} / {del_mid/REF_PRICE-1:+.0%} / {amb_mid/REF_PRICE-1:+.0%}. The multiple matters more "
        f"than the case: 13.5x to 18.5x moves the Delivered case by about $51, the three cases at a fixed 16.5x span about $30.",
        f"Reverse DCF on the Delivered FCF (${float(dcf_del['fcf27']):,.0f}m, WACC 10%, ten-year fade to 3%): at "
        f"${REF_PRICE:.2f} (EV $92.0bn) the price needs FY28+ FCF growth of {float(dcf_del['implied_g_reported']):.1f}% on reported "
        f"FCF and {float(dcf_del['implied_g_sbc_adj']):.1f}% on SBC-adjusted FCF (${float(dcf_del['sbc_adj_fcf27']):,.0f}m): the SBC debate.",
    ]
    for ln in lines:
        r = S.text_row(ws, r, "• " + ln, font=S.f_label(), wrap_cols=NCOLS, height=_h(ln))
    r += 1

    # ---------------------------------------------------------------- b. three cases, annual
    r = S.section(ws, r, "The three cases side by side: annual (FY25A actual, FY26E-FY27E by case)", ncols=NCOLS,
                  note="USD millions unless stated; blue = model output from the CSV, black = growth formulas")
    r = _band(ws, r, [("Actual", 1)] + [(c, 2) for c in CASES], first_col=2)
    r = S.header(ws, r, ["FY25A"] + ["FY26E", "FY27E"] * 3, label="Metric")
    annual_cols = [("Literal", "FY25")] + [(c, p) for c in CASES for p in ("FY26", "FY27")]
    row_of = {}
    for m, lab, fmt, is_pct in METRICS:
        vals = [cell(c, p, m) for c, p in annual_cols]
        if is_pct:
            vals = [S.pct(v) for v in vals]
        row_of[m] = r
        r = S.write_row(ws, r, lab, vals, fmt=fmt, forecast_from=1, bold=(m in ("revenue_musd", "eps_gaap")))
    for m, lab in (("revenue_musd", "Revenue growth y/y"), ("nights_m", "Nights growth y/y"),
                   ("adj_ebitda_musd", "Adj. EBITDA growth y/y"), ("eps_gaap", "EPS growth y/y")):
        base = row_of[m]
        vals = [None]
        for k in range(3):
            c26, c27 = 3 + 2 * k, 4 + 2 * k
            vals.append(f"={get_column_letter(c26)}{base}/$B${base}-1")
            vals.append(f"={get_column_letter(c27)}{base}/{get_column_letter(c26)}{base}-1")
        r = S.write_row(ws, r, lab, vals, fmt=S.FMT_PCT, kind="formula", forecast_from=1, indent=1)
    r += 1

    # ---------------------------------------------------------------- b'. three cases, quarterly
    r = S.section(ws, r, "The three cases side by side: quarterly, 3Q26E-4Q27E", ncols=NCOLS)
    r = _band(ws, r, [(c, len(QTRS)) for c in CASES], first_col=2)
    r = S.header(ws, r, QTRS * 3, label="Metric")
    q_cols = [(c, q) for c in CASES for q in QTRS]
    for m, lab, fmt, is_pct in METRICS:
        vals = [cell(c, q, m) for c, q in q_cols]
        if is_pct:
            vals = [S.pct(v) for v in vals]
        r = S.write_row(ws, r, lab, vals, fmt=fmt, forecast_from=0, bold=(m in ("revenue_musd", "eps_gaap")))
    r += 1

    # ---------------------------------------------------------------- c. inputs by case
    r = S.section(ws, r, "Inputs by case and quarter (the assumptions behind each case)", ncols=NCOLS,
                  note="pp rows are percentage points; FX and timing rows are common across cases (WS29 consensus-EUR schedule)")
    r = _band(ws, r, [(c, len(QTRS)) for c in CASES], first_col=2)
    r = S.header(ws, r, QTRS * 3, label="Input")
    for m, lab, unit in INPUTS:
        vals = []
        for c, q in q_cols:
            v = _v(inputs.loc[(inputs.scenario == c) & (inputs.quarter == q), m].iloc[0])
            vals.append(S.pct(v) if unit == "pct" else v)
        r = S.write_row(ws, r, lab, vals, fmt=UNIT_FMT[unit], forecast_from=0)
    r += 1

    # ---------------------------------------------------------------- d. implied price targets
    r = S.section(ws, r, "Implied share price by lens and case (team multiples: EV/EBITDA 13.5 / 16.5 / 18.5x; "
                         "P/E 22 / 27 / 30x; EV/FCF 14 / 17 / 20x)", ncols=NCOLS)
    ref_row = r
    r = S.write_row(ws, r, "Reference share price ($, close 11 Sep 2026)", [REF_PRICE], fmt=S.FMT_USD, kind="input",
                    bold=True, note="input: the upside columns reference this cell")
    ref = f"$B${ref_row}"
    r = S.header(ws, r, CASES + [f"{c} upside" for c in CASES], label="Lens (multiple)", height=30)
    for _, t in targets.iterrows():
        prices = [float(t[c]) for c in CASES]
        ups = [f"={get_column_letter(2 + k)}{r}/{ref}-1" for k in range(3)]
        is_avg = str(t["lens"]).startswith("Average")
        r = S.write_row(ws, r, str(t["lens"]), prices + ups, fmts=[S.FMT_USD0] * 3 + [S.FMT_PCT] * 3,
                        kinds=["input"] * 3 + ["formula"] * 3, bold=is_avg, fill=S.FILL_KEY if is_avg else None)
    r += 1

    # ---------------------------------------------------------------- e. reverse DCF
    r = S.section(ws, r, "Reverse DCF on management's own FCF (EV $92.0bn at $170.19; WACC 10%; growth fades to 3% "
                         "over ten years)", ncols=NCOLS)
    r = S.header(ws, r, CASES, label="Item")
    for m, lab, fmt, is_pct in DCF_ROWS:
        vals = [float(dcf.loc[c, m]) for c in CASES]
        if is_pct:
            vals = [S.pct(v) for v in vals]
        r = S.write_row(ws, r, lab, vals, fmt=fmt, bold=m.startswith("implied"))
    r = S.text_row(ws, r, "The seven-turn gap between the reported and SBC-adjusted readings is the SBC debate: on "
                   "reported FCF the market asks for little; on FCF after SBC it asks for mid-teens growth.",
                   wrap_cols=NCOLS, height=15)
    r += 1

    # ---------------------------------------------------------------- f. management statements
    r = S.section(ws, r, "What management is looking at, by area: near term, mid term, the number used in the Delivered "
                         "case, and the line's track record", ncols=NCOLS)
    st = _load_statements()
    if st is None:
        r = S.text_row(ws, r, "Mgmt_Statements sheet not found in model/ABNB_management_implied.xlsx; see "
                       "research/notes/2026-09-12_management-implied-model.md section 3.", wrap_cols=NCOLS)
    else:
        cols = list(st.columns)
        r0 = r
        r = S.table(ws, r, _clean(st), first_col=1, wrap_text_cols=cols, header_height=30)
        for i in range(len(st)):
            longest = max(len(str(x or "")) for x in st.iloc[i].tolist())
            ws.row_dimensions[r0 + 1 + i].height = min(220, max(30, 13.0 * math.ceil(longest / 60)))
        for j in range(1, len(cols)):
            ws.column_dimensions[get_column_letter(1 + j)].width = 48 if j < 4 else (38 if j == 4 else 30)
    r += 1

    # ---------------------------------------------------------------- g. sources
    S.sources_block(ws, r, [
        ("Three cases, quarterly and annual", "data/processed/reverse_dcf/mgmt_implied_summary.csv"),
        ("Inputs by case", "data/processed/reverse_dcf/mgmt_implied_inputs.csv"),
        ("Implied prices by lens", "data/processed/reverse_dcf/mgmt_implied_targets.csv"),
        ("Reverse DCF", "data/processed/reverse_dcf/mgmt_implied_dcf.csv"),
        ("Management statements table", "model/ABNB_management_implied.xlsx (Mgmt_Statements sheet); "
                                        "data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv (377 statements)"),
        ("Street FY27 revenue", "data/processed/reverse_dcf/market/market_implied_comparison.csv"),
        ("Builder and note", "analysis/src/reverse_dcf/management_implied_model.py; "
                             "research/notes/2026-09-12_management-implied-model.md"),
        ("Synthesis", "docs/reverse_dcf/SYNTHESIS.md"),
    ], ncols=NCOLS)
    S.freeze(ws, "B4")
    return ws
