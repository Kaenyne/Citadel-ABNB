"""'Income Statement' tab: quarterly 1Q23-4Q27 and annual FY23-FY27, forecast columns driven by a scenario dropdown."""
import style as S
import data as Dt
from openpyxl.styles import Alignment, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

SHEET = "Income Statement"
HDR_ROW = 5
C0 = 2  # first quarter column (B)
NH = len(Dt.HIST_Q)  # 14 actual quarters
NF = len(Dt.FC_Q)    # 6 forecast quarters
GAP = C0 + NH + NF   # blank column between quarterly and annual
A0 = GAP + 1         # first annual column
ANNUAL = ["FY23", "FY24", "FY25", "FY26E", "FY27E"]


def qcol(i):
    return S.col(C0 + i)


def acol(i):
    return S.col(A0 + i)


def build(wb):
    ws = wb.create_sheet(SHEET)
    rng = wb._scen_ranges
    S.setup(ws, "Airbnb income statement: actuals 1Q23-2Q26, forecast 3Q26-4Q27, FY23-FY27",
            "USD millions unless stated. Blue = source value (10-Q/10-K panel, 40_line_build), black = formula. Forecast columns "
            "(yellow) follow the scenario chosen in B3 and pull from the 'Scenario Data' tab. Adjusted EBITDA = revenue less cash "
            "costs plus D&A (cash cost lines are GAAP less SBC and other add-backs, as management defines them).", label_width=40)
    for i in range(NH + NF):
        ws.column_dimensions[qcol(i)].width = 9.5
    ws.column_dimensions[S.col(GAP)].width = 2
    for i in range(len(ANNUAL)):
        ws.column_dimensions[acol(i)].width = 11
    ws.column_dimensions[S.col(A0 + len(ANNUAL))].width = 3
    ws.column_dimensions[S.col(A0 + len(ANNUAL) + 1)].width = 60

    # scenario selector
    ws["A3"] = "Scenario shown in the forecast columns  →"
    ws["A3"].font = S.f_label(bold=True)
    ws["B3"] = "Base (team model)"
    ws["B3"].font = S.f_input(bold=True)
    ws["B3"].fill = S.FILL_KEY
    ws.merge_cells("B3:F3")
    dv = DataValidation(type="list", formula1=rng["names"], allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B3")
    ws["G3"] = f'=INDEX({rng["namekeys"]},MATCH($B$3,{rng["names"]},0))'
    ws["G3"].font = S.f_note()
    ws["H3"] = "← scenario key (used by the lookups). Pick from the dropdown in B3: Base, the two Short (pitch) cases, evidence-only costs, or the bear/bull revenue and cost cases."
    ws["H3"].font = S.f_note()

    labels = [q + "A" for q in Dt.HIST_Q] + [q + "E" for q in Dt.FC_Q]
    S.header(ws, HDR_ROW, labels, first_col=C0, label="Quarter", height=18)
    S.header(ws, HDR_ROW, ANNUAL, first_col=A0)
    # helper: quarter names without the A/E suffix in a hidden-ish row 4 for MATCH
    for i, q in enumerate(Dt.ALL_Q):
        c = ws.cell(row=4, column=C0 + i, value=q); c.font = S.f_note(); c.alignment = Alignment(horizontal="center")
    for i, y in enumerate(ANNUAL):
        c = ws.cell(row=4, column=A0 + i, value=y.replace("E", "")); c.font = S.f_note()

    hq = Dt.history_quarterly()
    ha = Dt.history_annual()
    row = HDR_ROW + 1
    rows = {}  # key -> row number

    def fc_formula(line_key, i):
        qc = f"{qcol(NH + i)}$4"
        return (f'=INDEX({rng["data"]},MATCH($G$3&"|{line_key}",{rng["keys"]},0),MATCH({qc},{rng["qhdr"]},0))')

    def put(key, label, hist_col=None, line_key=None, fmt=S.FMT_M, bold=False, indent=0, fc_override=None,
            hist_override=None, annual=None, annual_hist_col=None, note=""):
        """Write a row: history from hq[hist_col] (or hist_override formulas), forecast via INDEX/MATCH on line_key
        (or fc_override formulas), annual via `annual` spec: 'sum' | 'avg' | list of formulas | None."""
        nonlocal row
        vals = []
        kinds = []
        for i, q in enumerate(Dt.HIST_Q):
            if hist_override is not None:
                vals.append(hist_override(i)); kinds.append("formula")
            elif hist_col is not None:
                v = hq.loc[q, hist_col]
                vals.append(None if v != v else float(v)); kinds.append("input")
            else:
                vals.append(None); kinds.append("input")
        for i in range(NF):
            if fc_override is not None:
                vals.append(fc_override(i)); kinds.append("formula")
            elif line_key is not None:
                vals.append(fc_formula(line_key, i)); kinds.append("link")
            else:
                vals.append(None); kinds.append("input")
        S.write_row(ws, row, label, vals, fmt=fmt, kinds=kinds, bold=bold, indent=indent, forecast_from=NH, note=note,
                    note_col=A0 + len(ANNUAL) + 1)
        # annual
        avals, akinds = [], []
        for j, y in enumerate(ANNUAL):
            if annual is None:
                avals.append(None); akinds.append("input"); continue
            if isinstance(annual, list):
                avals.append(annual[j]); akinds.append("formula"); continue
            if y in ("FY23", "FY24", "FY25"):
                col_ = annual_hist_col or hist_col
                if annual == "sum" and col_ is not None and col_ in ha.columns:
                    v = ha.loc[y, col_]; avals.append(None if v != v else float(v)); akinds.append("input")
                elif annual == "avg":
                    qs = [i for i, q in enumerate(Dt.HIST_Q) if q.endswith(y[-2:])]
                    avals.append(f"=AVERAGE({qcol(qs[0])}{row}:{qcol(qs[-1])}{row})"); akinds.append("formula")
                else:
                    avals.append(None); akinds.append("input")
            elif y == "FY26E":
                h1 = f"{qcol(NH-2)}{row}:{qcol(NH-1)}{row}"; h2 = f"{qcol(NH)}{row}:{qcol(NH+1)}{row}"
                avals.append(f"=SUM({h1},{h2})" if annual == "sum" else f"=AVERAGE({h1},{h2})"); akinds.append("formula")
            elif y == "FY27E":
                r_ = f"{qcol(NH+2)}{row}:{qcol(NH+5)}{row}"
                avals.append(f"=SUM({r_})" if annual == "sum" else f"=AVERAGE({r_})"); akinds.append("formula")
        S.write_row(ws, row, "", avals, fmt=fmt, kinds=akinds, bold=bold, first_col=A0, forecast_from=3)
        ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row
        row += 1
        return row - 1

    def ratio_row(key, label, num_key, den_key, fmt=S.FMT_PCT, scale="", indent=1, bold=False, annual=True):
        nonlocal row
        nr, dr = rows[num_key], rows[den_key]
        vals = [f"=IFERROR({qcol(i)}{nr}/{qcol(i)}{dr}{scale},\"\")" for i in range(NH + NF)]
        S.write_row(ws, row, label, vals, fmt=fmt, kind="formula", indent=indent, bold=bold, forecast_from=NH)
        if annual:
            av = [f"=IFERROR({acol(j)}{nr}/{acol(j)}{dr}{scale},\"\")" for j in range(len(ANNUAL))]
            S.write_row(ws, row, "", av, fmt=fmt, kind="formula", first_col=A0, bold=bold, forecast_from=3)
            ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row
        row += 1

    def yoy_row(key, label, base_key, indent=1):
        nonlocal row
        br = rows[base_key]
        vals = [None] * 4 + [f"=IFERROR({qcol(i)}{br}/{qcol(i-4)}{br}-1,\"\")" for i in range(4, NH + NF)]
        S.write_row(ws, row, label, vals, fmt=S.FMT_PCT, kind="formula", indent=indent, forecast_from=NH)
        av = [None] + [f"=IFERROR({acol(j)}{br}/{acol(j-1)}{br}-1,\"\")" for j in range(1, len(ANNUAL))]
        S.write_row(ws, row, "", av, fmt=S.FMT_PCT, kind="formula", first_col=A0, forecast_from=3)
        ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row
        row += 1

    ncols = A0 + len(ANNUAL)
    # ---------- KPIs
    row = S.section(ws, row, "Operating KPIs", ncols=ncols)
    put("nights", "Nights & seats booked (m)", "nights_m", "nights_m", fmt=S.FMT_M1, bold=True, annual="sum")
    yoy_row("nights_yoy", "y/y", "nights")
    put("gbv", "Gross booking value ($bn)", "gbv_busd", "gbv_busd", fmt=S.FMT_M1, bold=True, annual="sum")
    yoy_row("gbv_yoy", "y/y", "gbv")
    ratio_row("adr", "ADR ($, = GBV / nights)", "gbv", "nights", fmt=S.FMT_USD, scale="*1000", indent=0)
    yoy_row("adr_yoy", "y/y", "adr")
    row += 1
    # ---------- IS
    row = S.section(ws, row, "Income statement (adjusted EBITDA build, then GAAP bridge)", ncols=ncols)
    put("rev", "Revenue", "revenue", "revenue", bold=True, annual="sum")
    yoy_row("rev_yoy", "y/y", "rev")
    ratio_row("take", "Take rate (revenue / GBV)", "rev", "gbv", scale="/1000", fmt=S.FMT_PCT2)
    row += 1
    put("cor", "Cost of revenue (cash)", "cor_cash", "cor_cash", indent=1, annual="sum")
    put("ops", "Operations & support (cash)", "ops_cash", "ops_cash", indent=1, annual="sum")
    put("pd", "Product development (cash)", "pd_cash", "pd_cash", indent=1, annual="sum")
    put("sm", "Sales & marketing (cash)", "sm_cash", "sm_cash", indent=1, annual="sum")
    put("ga", "General & administrative (cash, ex lodging-tax reserves)", "ga_cash", "ga_cash", indent=1, annual="sum")
    # total cash costs as a formula
    def tot_fc(i):
        c = qcol(NH + i); return f"=SUM({c}{rows['cor']}:{c}{rows['ga']})"
    def tot_h(i):
        c = qcol(i); return f"=SUM({c}{rows['cor']}:{c}{rows['ga']})"
    put("tcc", "Total cash costs", hist_override=tot_h, fc_override=tot_fc, bold=True,
        annual=[f"=SUM({acol(j)}{rows['cor']}:{acol(j)}{rows['ga']})" for j in range(len(ANNUAL))])
    ratio_row("tcc_pct", "% of revenue", "tcc", "rev")
    put("da", "Depreciation & amortisation (inside the cash lines)", "da", "da", indent=1, annual="sum")
    put("oth_addb", "Other add-backs / reconciling items (history only)", "other_addbacks", None, indent=1, annual="sum",
        note="History: reported adjusted EBITDA less (revenue - cash costs + D&A); lodging-tax reserves, restructuring and rounding. Forecast: nil by construction.")
    def ebitda_h(i):
        c = qcol(i); return f"={c}{rows['rev']}-{c}{rows['tcc']}+{c}{rows['da']}+{c}{rows['oth_addb']}"
    def ebitda_f(i):
        c = qcol(NH + i); return f"={c}{rows['rev']}-{c}{rows['tcc']}+{c}{rows['da']}"
    put("ebitda", "Adjusted EBITDA", hist_override=ebitda_h, fc_override=ebitda_f, bold=True,
        annual=[f"={acol(j)}{rows['rev']}-{acol(j)}{rows['tcc']}+{acol(j)}{rows['da']}+IF(ISNUMBER({acol(j)}{rows['oth_addb']}),{acol(j)}{rows['oth_addb']},0)" for j in range(len(ANNUAL))])
    ratio_row("ebitda_m", "Adjusted EBITDA margin", "ebitda", "rev", indent=1, bold=True)
    yoy_row("ebitda_yoy", "y/y", "ebitda")
    row += 1
    put("sbc", "Stock-based compensation", "sbc", "sbc", indent=1, annual="sum")
    ratio_row("sbc_pct", "% of revenue", "sbc", "rev", indent=2)
    put("gaap_oth", "Other GAAP items vs the adjusted stack (history only)", "gaap_other", None, indent=1, annual="sum",
        note="History: reported operating income less (adjusted EBITDA - D&A - SBC): restructuring, lodging-tax reserves, acquisition items. Forecast: nil.")
    def opi_h(i):
        c = qcol(i); return f"={c}{rows['ebitda']}-{c}{rows['da']}-{c}{rows['sbc']}+{c}{rows['gaap_oth']}"
    def opi_f(i):
        c = qcol(NH + i); return f"={c}{rows['ebitda']}-{c}{rows['da']}-{c}{rows['sbc']}"
    put("opi", "Operating income (GAAP)", hist_override=opi_h, fc_override=opi_f, bold=True,
        annual=[f"={acol(j)}{rows['ebitda']}-{acol(j)}{rows['da']}-{acol(j)}{rows['sbc']}+IF(ISNUMBER({acol(j)}{rows['gaap_oth']}),{acol(j)}{rows['gaap_oth']},0)" for j in range(len(ANNUAL))])
    ratio_row("opm", "Operating margin", "opi", "rev", indent=1)
    put("ii", "Interest income", "interest_income", "interest_income", indent=1, annual="sum")
    put("ie", "Interest expense", "interest_expense", "interest_expense", indent=1, annual="sum")
    put("oi", "Other income / (expense), net", "other_income", "other_income", indent=1, annual="sum")
    def ptx(c):
        return f"={c}{rows['opi']}+{c}{rows['ii']}-{c}{rows['ie']}+{c}{rows['oi']}"
    put("pretax", "Pre-tax income", hist_override=lambda i: ptx(qcol(i)), fc_override=lambda i: ptx(qcol(NH + i)), bold=True,
        annual=[ptx(acol(j)) for j in range(len(ANNUAL))])
    put("tax", "Income tax provision / (benefit)", "tax", "tax", indent=1, annual="sum",
        note="4Q23 carries the $2.7bn valuation-allowance release; FY23 GAAP net income is not comparable.")
    ratio_row("etr", "Effective tax rate", "tax", "pretax", indent=2)
    def ni(c):
        return f"={c}{rows['pretax']}-{c}{rows['tax']}"
    put("ni", "Net income", hist_override=lambda i: ni(qcol(i)), fc_override=lambda i: ni(qcol(NH + i)), bold=True,
        annual=[ni(acol(j)) for j in range(len(ANNUAL))])
    ratio_row("nim", "Net margin", "ni", "rev", indent=1)
    put("shares", "Diluted weighted-average shares (m)", "diluted_shares_m", "diluted_shares_m", fmt=S.FMT_M1, indent=1, annual="avg")
    def eps(c):
        return f"=IFERROR({c}{rows['ni']}/{c}{rows['shares']},\"\")"
    put("eps", "Diluted EPS ($)", hist_override=lambda i: eps(qcol(i)), fc_override=lambda i: eps(qcol(NH + i)), fmt=S.FMT_EPS, bold=True,
        annual=[eps(acol(j)) for j in range(len(ANNUAL))],
        note="History EPS is net income / diluted shares from the panel; it can differ from the reported figure by a cent. Forecast: 40_line_build M7 bridge.")
    put("eps_rep", "Diluted EPS as reported ($)", "eps", None, fmt=S.FMT_EPS, indent=1, annual=None)
    row += 1
    row = S.section(ws, row, "Memo: cash and capital return (history)", ncols=ncols)
    put("fcf", "Free cash flow", "fcf", None, indent=1, annual="sum", annual_hist_col="fcf_reported")
    ratio_row("fcf_m", "FCF margin", "fcf", "rev", indent=2)
    put("bb", "Share repurchases", "buybacks", None, indent=1, annual="sum")
    row += 1
    # ---------- comparisons under the IS: Street and the short case for the key lines
    row = S.section(ws, row, "Comparison rows (do not move with the dropdown)", ncols=ncols,
                    note="Street = LSEG mean 11 Sep 2026 (quarters 1Q27-4Q27 n 17-19); Short = pitch case with costs at budget")
    cons = Dt.consensus()
    vs = cons["vs"]
    sq = Dt.scenario_quarterly()
    base = sq[sq.scenario == "base"].set_index("quarter")
    short = sq[sq.scenario == "short_costs_at_budget"].set_index("quarter")
    sca = Dt.short_case_annual()
    lseg = cons["lseg"]
    per_map = {"3Q26": "2026Q3", "4Q26": "2026Q4", "1Q27": "2027Q1", "2Q27": "2027Q2", "3Q27": "2027Q3", "4Q27": "2027Q4"}

    def cmp_row(label, fc_vals, ann_vals, fmt=S.FMT_M, fill=None):
        nonlocal row
        vals = [None] * NH + fc_vals
        S.write_row(ws, row, label, vals, fmt=fmt, kind="input", indent=1, fill=fill)
        S.write_row(ws, row, "", ann_vals, fmt=fmt, kind="input", first_col=A0, fill=fill)
        ws.cell(row=row, column=1).value = "    " + label
        row += 1

    cmp_row("Revenue: Street (LSEG)", [float(vs.loc[per_map[q], "lseg_revenue_musd"]) for q in Dt.FC_Q],
            [None, None, None, float(lseg.loc["FY26", "revenue_mean"]), float(lseg.loc["FY27", "revenue_mean"])], fill=S.FILL_STREET)
    cmp_row("Revenue: Base (team)", [float(base.loc[q, "revenue"]) for q in Dt.FC_Q],
            [None, None, None, float(Dt.margin_build()["annual"].query("period=='FY26' and scenario=='base'").revenue.iloc[0]),
             float(Dt.margin_build()["annual"].query("period=='FY27' and scenario=='base'").revenue.iloc[0])], fill=S.FILL_KEY)
    cmp_row("Revenue: Short case (pitch)", [float(short.loc[q, "revenue"]) for q in Dt.FC_Q],
            [None, None, None, float(sca.loc[("short_costs_at_budget", "FY26"), "revenue"]), float(sca.loc[("short_costs_at_budget", "FY27"), "revenue"])], fill=S.FILL_SHORT)
    cmp_row("Adj. EBITDA: Street (LSEG)", [float(vs.loc[per_map[q], "lseg_ebitda_musd"]) for q in Dt.FC_Q],
            [None, None, None, float(lseg.loc["FY26", "ebitda_mean"]), float(lseg.loc["FY27", "ebitda_mean"])], fill=S.FILL_STREET)
    cmp_row("Adj. EBITDA: Base (team)", [float(base.loc[q, "adj_ebitda"]) for q in Dt.FC_Q],
            [None, None, None, float(Dt.margin_build()["annual"].query("period=='FY26' and scenario=='base'").adj_ebitda.iloc[0]),
             float(Dt.margin_build()["annual"].query("period=='FY27' and scenario=='base'").adj_ebitda.iloc[0])], fill=S.FILL_KEY)
    cmp_row("Adj. EBITDA: Short case (pitch)", [float(short.loc[q, "adj_ebitda"]) for q in Dt.FC_Q],
            [None, None, None, float(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda"]), float(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda"])], fill=S.FILL_SHORT)
    cmp_row("Adj. EBITDA margin: Street (LSEG)", [S.pct(vs.loc[per_map[q], "lseg_margin_pct"]) for q in Dt.FC_Q],
            [None, None, None, S.pct(lseg.loc["FY26", "implied_margin_pct"]), S.pct(lseg.loc["FY27", "implied_margin_pct"])], fmt=S.FMT_PCT, fill=S.FILL_STREET)
    cmp_row("Adj. EBITDA margin: Base (team)", [S.pct(base.loc[q, "adj_ebitda_margin_pct"]) for q in Dt.FC_Q],
            [None, None, None, S.pct(Dt.margin_build()["annual"].query("period=='FY26' and scenario=='base'").adj_ebitda_margin_pct.iloc[0]),
             S.pct(Dt.margin_build()["annual"].query("period=='FY27' and scenario=='base'").adj_ebitda_margin_pct.iloc[0])], fmt=S.FMT_PCT, fill=S.FILL_KEY)
    cmp_row("Adj. EBITDA margin: Short case (pitch)", [S.pct(short.loc[q, "adj_ebitda_margin_pct"]) for q in Dt.FC_Q],
            [None, None, None, S.pct(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda_margin_pct"])], fmt=S.FMT_PCT, fill=S.FILL_SHORT)
    eps_street_q = {"3Q26": float(lseg.loc["3Q26", "eps_mean"]), "4Q26": float(lseg.loc["4Q26", "eps_mean"])}
    cmp_row("Diluted EPS: Street (LSEG)", [eps_street_q.get(q) for q in Dt.FC_Q],
            [None, None, None, float(lseg.loc["FY26", "eps_mean"]), float(lseg.loc["FY27", "eps_mean"])], fmt=S.FMT_EPS, fill=S.FILL_STREET)
    cmp_row("Diluted EPS: Base (team)", [float(base.loc[q, "eps"]) for q in Dt.FC_Q],
            [None, None, None, float(Dt.margin_build()["annual"].query("period=='FY26' and scenario=='base'").eps.iloc[0]),
             float(Dt.margin_build()["annual"].query("period=='FY27' and scenario=='base'").eps.iloc[0])], fmt=S.FMT_EPS, fill=S.FILL_KEY)
    ss = Dt.margin_build()["short_summary"].set_index("case").loc["short_costs_at_budget"]
    cmp_row("Diluted EPS: Short case (pitch)", [float(short.loc[q, "eps"]) for q in Dt.FC_Q],
            [None, None, None, None, float(ss["fy27_eps"])], fmt=S.FMT_EPS, fill=S.FILL_SHORT)
    row += 1
    row = S.sources_block(ws, row, [
        ("Quarterly and annual GAAP lines, cash cost lines, SBC, D&A, shares", "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv, 02_panel_annual.csv"),
        ("Nights, GBV, ADR, reported adjusted EBITDA, FCF, buybacks", "data/processed/abnb_driver_history_quarterly.csv"),
        ("Forecast lines by scenario (base, bear/bull, evidence-only)", "data/processed/margin_build/40_line_build/40_lines_quarterly.csv; note docs/margin-build/notes/40_line_build.md"),
        ("Short case (pitch) quarterly lines", "data/processed/margin_build/40_line_build/40_short_case_quarterly.csv, 40_short_case_summary.csv"),
        ("Street consensus", "data/processed/margin_build/03_consensus_pit/03_current_consensus.csv (LSEG 11 Sep 2026); 23_final_model/23_vs_consensus.csv"),
    ], ncols=ncols)
    S.freeze(ws, f"B{HDR_ROW+1}")
    wb._is_rows = rows
    return ws
