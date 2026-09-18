"""'Margins' tab: cost lines by quarter (history + scenario-driven forecast), the 3Q26 sentence reconciliation, the
5 Nov margin card, what the FY26 margin sentence should look like, FY27 scenario grid and sensitivities, the short case."""
import style as S
import data as Dt
import pandas as pd

SHEET = "Margins"
HDR_ROW = 5
C0 = 2
NH = len(Dt.HIST_Q)
NF = len(Dt.FC_Q)
GAP = C0 + NH + NF
A0 = GAP + 1
ANNUAL = ["FY23", "FY24", "FY25", "FY26E", "FY27E"]


def qcol(i):
    return S.col(C0 + i)


def acol(i):
    return S.col(A0 + i)


def build(wb):
    ws = wb.create_sheet(SHEET)
    rng = wb._scen_ranges
    S.setup(ws, "Margins: the cost stack line by line, the 3Q26 sentence, the 5 Nov card and the FY26/FY27 margin view",
            "Cash cost lines = GAAP less SBC and add-backs (management's adjusted EBITDA definition). Forecast columns follow the "
            "scenario dropdown on the Income Statement tab (B3). Blue = source value, black = formula, green = link.", label_width=46)
    for i in range(NH + NF):
        ws.column_dimensions[qcol(i)].width = 9.5
    ws.column_dimensions[S.col(GAP)].width = 2
    for i in range(len(ANNUAL)):
        ws.column_dimensions[acol(i)].width = 11
    ws.column_dimensions[S.col(A0 + len(ANNUAL))].width = 3
    ws.column_dimensions[S.col(A0 + len(ANNUAL) + 1)].width = 70
    NOTE_COL = A0 + len(ANNUAL) + 1
    ncols = A0 + len(ANNUAL)
    KEY = "'Income Statement'!$G$3"

    labels = [q + "A" for q in Dt.HIST_Q] + [q + "E" for q in Dt.FC_Q]
    S.header(ws, HDR_ROW, labels, first_col=C0, label="Quarter")
    S.header(ws, HDR_ROW, ANNUAL, first_col=A0)
    for i, q in enumerate(Dt.ALL_Q):
        c = ws.cell(row=4, column=C0 + i, value=q); c.font = S.f_note()
    ws["A3"] = "Scenario in the forecast columns:"; ws["A3"].font = S.f_label(bold=True)
    ws["B3"] = "='Income Statement'!B3"; ws["B3"].font = S.f_link(bold=True); ws["B3"].fill = S.FILL_KEY
    ws.merge_cells("B3:F3")

    hq = Dt.history_quarterly()
    ha = Dt.history_annual()
    rows = {}
    row = HDR_ROW + 1

    def fc(line_key, i):
        return f'=INDEX({rng["data"]},MATCH({KEY}&"|{line_key}",{rng["keys"]},0),MATCH({qcol(NH+i)}$4,{rng["qhdr"]},0))'

    def put(key, label, hist_col=None, line_key=None, fmt=S.FMT_M, bold=False, indent=0, note="", annual="sum",
            hist_vals=None, fc_vals=None, annual_vals=None):
        nonlocal row
        vals, kinds = [], []
        for i, q in enumerate(Dt.HIST_Q):
            if hist_vals is not None:
                v = hist_vals[i]
            elif hist_col is not None and hist_col in hq.columns:
                v = hq.loc[q, hist_col]; v = None if v != v else float(v)
            else:
                v = None
            vals.append(v); kinds.append("formula" if isinstance(v, str) else "input")
        for i in range(NF):
            v = fc_vals[i] if fc_vals is not None else (fc(line_key, i) if line_key else None)
            vals.append(v); kinds.append("link" if (line_key and fc_vals is None) else "formula")
        S.write_row(ws, row, label, vals, fmt=fmt, kinds=kinds, bold=bold, indent=indent, forecast_from=NH, note=note, note_col=NOTE_COL)
        if annual_vals is not None:
            av = annual_vals
        elif annual == "sum":
            h1 = f"{qcol(NH-2)}{row}:{qcol(NH-1)}{row}"; h2 = f"{qcol(NH)}{row}:{qcol(NH+1)}{row}"
            av = []
            for j, y in enumerate(ANNUAL[:3]):
                col_ = hist_col
                v = ha.loc[y, col_] if (col_ and col_ in ha.columns) else None
                av.append(None if (v is None or v != v) else float(v))
            av += [f"=SUM({h1},{h2})", f"=SUM({qcol(NH+2)}{row}:{qcol(NH+5)}{row})"]
        else:
            av = None
        if av is not None:
            ak = ["formula" if isinstance(v, str) else "input" for v in av]
            S.write_row(ws, row, "", av, fmt=fmt, kinds=ak, bold=bold, first_col=A0, forecast_from=3)
            ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row
        row += 1

    def ratio(key, label, num, den, fmt=S.FMT_PCT, indent=1, bold=False, scale=""):
        nonlocal row
        nr, dr = rows[num], rows[den]
        vals = [f"=IFERROR({qcol(i)}{nr}/{qcol(i)}{dr}{scale},\"\")" for i in range(NH + NF)]
        S.write_row(ws, row, label, vals, fmt=fmt, kind="formula", indent=indent, bold=bold, forecast_from=NH)
        av = [f"=IFERROR({acol(j)}{nr}/{acol(j)}{dr}{scale},\"\")" for j in range(len(ANNUAL))]
        S.write_row(ws, row, "", av, fmt=fmt, kind="formula", first_col=A0, bold=bold, forecast_from=3)
        ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row; row += 1

    def yoy(key, label, base, indent=1):
        nonlocal row
        br = rows[base]
        vals = [None] * 4 + [f"=IFERROR({qcol(i)}{br}/{qcol(i-4)}{br}-1,\"\")" for i in range(4, NH + NF)]
        S.write_row(ws, row, label, vals, fmt=S.FMT_PCT, kind="formula", indent=indent, forecast_from=NH)
        av = [None] + [f"=IFERROR({acol(j)}{br}/{acol(j-1)}{br}-1,\"\")" for j in range(1, len(ANNUAL))]
        S.write_row(ws, row, "", av, fmt=S.FMT_PCT, kind="formula", first_col=A0, forecast_from=3)
        ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row; row += 1

    # ------------- Section 1: cost stack
    row = S.section(ws, row, "1. The cost stack, cash basis (what adjusted EBITDA is made of)", ncols=ncols)
    put("rev", "Revenue", "revenue", "revenue", bold=True)
    put("cor", "Cost of revenue", "cor_cash", "cor_cash", bold=True)
    ratio("cor_pct", "% of revenue", "cor", "rev"); yoy("cor_yoy", "y/y", "cor")
    put("cor_fees", "Merchant / payment fees", None, "cor_fees", indent=1, annual=None, note="1.70% of GBV annual-equivalent, seasonal factors 0.90/1.045/1.035/1.033; 1H26 rate 1.68% after processor rebates")
    put("cor_cb", "Chargebacks", None, "cor_chargebacks", indent=1, annual=None, note="$0.72 per booking (1H26 +$25M y/y); short case adds $0.15 per booking")
    put("cor_host", "Hosting", None, "cor_hosting", indent=1, annual=None, note="$224M/yr FY25 + $30M per half step in 2H26 + AI reconciliation step; $330M/yr FY27. The least-sourced number in the build.")
    put("cor_oth", "Other cost of revenue", None, "cor_other", indent=1, annual=None, note="$0.36 per night")
    put("ops", "Operations & support", "ops_cash", "ops_cash", bold=True)
    ratio("ops_pct", "% of revenue", "ops", "rev"); yoy("ops_yoy", "y/y", "ops")
    put("ops_var", "Variable part (AI-addressable, 21.5% of the line)", None, "ops_variable", indent=1, annual=None, note="per booking -14% y/y in 2H26, -10% in FY27 (management: support cost per booking -10% and -16% in 1H26)")
    put("ops_fix", "Fixed part (payroll, customer relations, insurance)", None, "ops_fixed", indent=1, annual=None, note="+8% y/y")
    put("opb", "Ops & support per booking ($)", None, "ops_per_booking", fmt=S.FMT_M2, indent=1, annual=None)
    put("pd", "Product development", "pd_cash", "pd_cash", bold=True, note="2H26 +9% y/y, FY27 +8% + $30M AI tooling; 1H26 ran +12%/+10%, all payroll")
    ratio("pd_pct", "% of revenue", "pd", "rev"); yoy("pd_yoy", "y/y", "pd")
    put("sm", "Sales & marketing", "sm_cash", "sm_cash", bold=True, note="THE line that carries the margin call: FY25 19.4% of revenue, FY26 21.3%, FY27 21.9% (line build) / 23.5% (run allocation)")
    ratio("sm_pct", "% of revenue", "sm", "rev"); yoy("sm_yoy", "y/y", "sm")
    put("sm_mkt", "Brand + performance marketing", None, "sm_marketing", indent=1, annual=None, note="FY25 $1,595M (10-K split); 1H26 +32% reported; 2H26 +25% plus the $67M 3Q26 reconciliation step; FY27 +15%")
    put("sm_fld", "Field operations & policy", None, "sm_field", indent=1, annual=None, note="FY25 $781M incl. ~$200M of Services/Experiences launch spend; +18% FY26, +11% FY27")
    put("ga", "General & administrative (ex lodging-tax reserves)", "ga_cash", "ga_cash", bold=True, note="4Q23 excludes the ~$1bn lodging-tax reserve, which management adds back; 2H26 +5%, FY27 +5% (1H26 ran -5.4% on a $38M drop in non-income taxes)")
    ratio("ga_pct", "% of revenue", "ga", "rev"); yoy("ga_yoy", "y/y", "ga")
    def tot(c):
        return f"={c}{rows['cor']}+{c}{rows['ops']}+{c}{rows['pd']}+{c}{rows['sm']}+{c}{rows['ga']}"
    put("tcc", "Total cash costs", hist_vals=[tot(qcol(i)) for i in range(NH)], fc_vals=[tot(qcol(NH+i)) for i in range(NF)], bold=True,
        annual_vals=[tot(acol(j)) for j in range(len(ANNUAL))])
    ratio("tcc_pct", "% of revenue", "tcc", "rev", bold=True); yoy("tcc_yoy", "y/y", "tcc")
    put("da", "D&A (inside the lines, added back)", "da", "da", indent=1)
    put("oth", "Other add-backs (history)", "other_addbacks", None, indent=1, note="reported adjusted EBITDA less the stack identity; nil in the forecast")
    def eb(c, hist):
        return f"={c}{rows['rev']}-{c}{rows['tcc']}+{c}{rows['da']}" + (f"+{c}{rows['oth']}" if hist else "")
    put("ebitda", "Adjusted EBITDA", hist_vals=[eb(qcol(i), True) for i in range(NH)], fc_vals=[eb(qcol(NH+i), False) for i in range(NF)], bold=True,
        annual_vals=[eb(acol(j), True).replace(f"+{acol(j)}{rows['oth']}", f"+IF(ISNUMBER({acol(j)}{rows['oth']}),{acol(j)}{rows['oth']},0)") for j in range(len(ANNUAL))])
    ratio("margin", "Adjusted EBITDA margin", "ebitda", "rev", bold=True, indent=0)
    for cc in range(C0, C0 + NH + NF):
        ws.cell(row=rows["margin"], column=cc).fill = S.FILL_KEY
    for j in range(len(ANNUAL)):
        ws.cell(row=rows["margin"], column=A0 + j).fill = S.FILL_KEY
    yoy("ebitda_yoy", "Adjusted EBITDA y/y", "ebitda")
    # incremental margin
    vals = [None] * 4 + [f"=IFERROR(({qcol(i)}{rows['ebitda']}-{qcol(i-4)}{rows['ebitda']})/({qcol(i)}{rows['rev']}-{qcol(i-4)}{rows['rev']}),\"\")" for i in range(4, NH + NF)]
    S.write_row(ws, row, "Incremental margin y/y (d EBITDA / d revenue)", vals, fmt=S.FMT_PCT, kind="formula", indent=1, forecast_from=NH,
                note="Street-implied FY27 incremental margin is 43.7%; the line build's is 34.8%, the run's 24.7%", note_col=NOTE_COL)
    av = [None] + [f"=IFERROR(({acol(j)}{rows['ebitda']}-{acol(j-1)}{rows['ebitda']})/({acol(j)}{rows['rev']}-{acol(j-1)}{rows['rev']}),\"\")" for j in range(1, len(ANNUAL))]
    S.write_row(ws, row, "", av, fmt=S.FMT_PCT, kind="formula", first_col=A0, forecast_from=3)
    ws.cell(row=row, column=1).value = "    Incremental margin y/y (d EBITDA / d revenue)"
    rows["incr"] = row; row += 1
    put("sbc", "Stock-based compensation (below adjusted EBITDA)", "sbc", "sbc", indent=1, note="+13.2% y/y on the year-ago quarter (M7); management: SBC growth below FY25's +13%")
    ratio("sbc_pct", "% of revenue", "sbc", "rev", indent=2)
    row += 1

    # ------------- Section 2: Street / run / line build comparison
    row = S.section(ws, row, "2. Adjusted EBITDA and margin: line build vs the calibrated run vs Street vs the short case", ncols=ncols,
                    note="LSEG 11 Sep 2026; run = 23_final_model (backtested combination); line build = 40_line_build (composition); short = pitch")
    mb = Dt.margin_build()
    ann = mb["annual"].set_index(["period", "scenario"])
    sq = Dt.scenario_quarterly()
    base = sq[sq.scenario == "base"].set_index("quarter")
    short = sq[sq.scenario == "short_costs_at_budget"].set_index("quarter")
    cons = Dt.consensus(); vs = cons["vs"]; lseg = cons["lseg"]
    sca = Dt.short_case_annual()
    run_q = Dt.read("margin_build/23_final_model/23_forecast_quarterly.csv")
    run_q = run_q[run_q.scenario == "base"].set_index("quarter") if "scenario" in run_q.columns else run_q.set_index("quarter")
    fa = mb["fc_annual_run"]; fa = fa[(fa.scenario == "base")].set_index("period")
    S.header(ws, row, ["3Q26", "4Q26", "FY26", "FY27", "FY28 (roll)"], first_col=2, label="Adj. EBITDA ($m) / margin", height=18); row += 1
    def qv(df, q, c):
        try:
            v = df.loc[q, c]; return None if v != v else float(v)
        except KeyError:
            return None
    cmp = [
        ("EBITDA: Street (LSEG mean)", [float(lseg.loc["3Q26", "ebitda_mean"]), float(lseg.loc["4Q26", "ebitda_mean"]), float(lseg.loc["FY26", "ebitda_mean"]), float(lseg.loc["FY27", "ebitda_mean"]), float(lseg.loc["FY28", "ebitda_mean"])], S.FMT_M, S.FILL_STREET),
        ("EBITDA: line build base (this workbook's IS)", [float(base.loc["3Q26", "adj_ebitda"]), float(base.loc["4Q26", "adj_ebitda"]), float(ann.loc[("FY26", "base"), "adj_ebitda"]), float(ann.loc[("FY27", "base"), "adj_ebitda"]), float(ann.loc[("FY28 roll-forward (flagged)", "base"), "adj_ebitda"])], S.FMT_M, S.FILL_KEY),
        ("EBITDA: calibrated run (backtested; the 5 Nov card object)", [qv(run_q, "2026Q3", "adj_ebitda_musd"), qv(run_q, "2026Q4", "adj_ebitda_musd"), float(fa.loc["FY26", "adj_ebitda_musd"]), float(fa.loc["FY27", "adj_ebitda_musd"]), float(fa.loc["FY28", "adj_ebitda_musd"])], S.FMT_M, None),
        ("EBITDA: short case (pitch, costs at budget)", [float(short.loc["3Q26", "adj_ebitda"]), float(short.loc["4Q26", "adj_ebitda"]), float(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda"]), float(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda"]), None], S.FMT_M, S.FILL_SHORT),
        ("Margin: Street", [S.pct(lseg.loc["3Q26", "implied_margin_pct"]), S.pct(lseg.loc["4Q26", "implied_margin_pct"]), S.pct(lseg.loc["FY26", "implied_margin_pct"]), S.pct(lseg.loc["FY27", "implied_margin_pct"]), S.pct(lseg.loc["FY28", "implied_margin_pct"])], S.FMT_PCT, S.FILL_STREET),
        ("Margin: line build base", [S.pct(base.loc["3Q26", "adj_ebitda_margin_pct"]), S.pct(base.loc["4Q26", "adj_ebitda_margin_pct"]), S.pct(ann.loc[("FY26", "base"), "adj_ebitda_margin_pct"]), S.pct(ann.loc[("FY27", "base"), "adj_ebitda_margin_pct"]), S.pct(ann.loc[("FY28 roll-forward (flagged)", "base"), "adj_ebitda_margin_pct"])], S.FMT_PCT, S.FILL_KEY),
        ("Margin: calibrated run", [S.pct(qv(run_q, "2026Q3", "adj_ebitda_margin_pct")), S.pct(qv(run_q, "2026Q4", "adj_ebitda_margin_pct")), S.pct(fa.loc["FY26", "adj_ebitda_margin_pct"]), S.pct(fa.loc["FY27", "adj_ebitda_margin_pct"]), S.pct(fa.loc["FY28", "adj_ebitda_margin_pct"])], S.FMT_PCT, None),
        ("Margin: short case", [S.pct(short.loc["3Q26", "adj_ebitda_margin_pct"]), S.pct(short.loc["4Q26", "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda_margin_pct"]), None], S.FMT_PCT, S.FILL_SHORT),
        ("EPS: Street", [float(lseg.loc["3Q26", "eps_mean"]), float(lseg.loc["4Q26", "eps_mean"]), float(lseg.loc["FY26", "eps_mean"]), float(lseg.loc["FY27", "eps_mean"]), float(lseg.loc["FY28", "eps_mean"])], S.FMT_EPS, S.FILL_STREET),
        ("EPS: line build base", [float(base.loc["3Q26", "eps"]), float(base.loc["4Q26", "eps"]), float(ann.loc[("FY26", "base"), "eps"]), float(ann.loc[("FY27", "base"), "eps"]), float(ann.loc[("FY28 roll-forward (flagged)", "base"), "eps"])], S.FMT_EPS, S.FILL_KEY),
        ("EPS: calibrated run", [qv(run_q, "2026Q3", "eps_diluted"), qv(run_q, "2026Q4", "eps_diluted"), float(fa.loc["FY26", "eps_diluted"]), float(fa.loc["FY27", "eps_diluted"]), float(fa.loc["FY28", "eps_diluted"])], S.FMT_EPS, None),
        ("EPS: short case", [float(short.loc["3Q26", "eps"]), float(short.loc["4Q26", "eps"]), None, float(mb["short_summary"].set_index("case").loc["short_costs_at_budget", "fy27_eps"]), None], S.FMT_EPS, S.FILL_SHORT),
    ]
    first_cmp = row
    for lab, vals, fmt, fill in cmp:
        S.write_row(ws, row, lab, vals, fmt=fmt, fill=fill, indent=1); row += 1
    # gaps
    S.write_row(ws, row, "Line build base vs Street, EBITDA ($m)", [f"={S.col(2+j)}{first_cmp+1}-{S.col(2+j)}{first_cmp}" for j in range(5)], fmt=S.FMT_M, kind="formula", bold=True, indent=1); row += 1
    S.write_row(ws, row, "Short case vs Street, EBITDA ($m)", [f"=IF(ISNUMBER({S.col(2+j)}{first_cmp+3}),{S.col(2+j)}{first_cmp+3}-{S.col(2+j)}{first_cmp},\"\")" for j in range(5)], fmt=S.FMT_M, kind="formula", bold=True, indent=1); row += 1
    row = S.text_row(ws, row, "FY28 in the line build is the FY27 margin rolled flat, not a forecast. The run's FY27 (34.6%) and the line build's FY27 (35.7%) differ by one point, all in S&M: "
                     "the run carried the 1H26 marketing growth rate forward, the line build applies management's stated deceleration to a base that already includes the 3Q26 step. "
                     "Both sit below the Street's 36.5%, which needs the marketing ramp to stop (43.7% incremental margin).", wrap_cols=12, height=44)
    row += 1

    # ------------- Section 3: 3Q26 reconciliation
    row = S.section(ws, row, "3. 3Q26: management's 'margin down slightly' sentence used as the cost budget", ncols=ncols)
    sent = mb["sentence"].copy()
    fm = {}
    for i, r in sent.iterrows():
        v = float(r["value"])
        isp = ("margin" in r["item"] or "%" in r["item"]) and v < 100
        S.write_row(ws, row, r["item"], [v / 100 if isp else v], fmt=S.FMT_PCT if isp else S.FMT_M, indent=1); row += 1
    row = S.text_row(ws, row, "Built from the evidence alone, 3Q26 costs grow 11.5% against revenue +17% and the margin would be 52.4%, contradicting the sentence. The base takes management at its word and adds "
                     "$97M of cost to 3Q26 (70% marketing as a timing step, 30% hosting as a run-rate step). The quarterly sentence has not been sandbagged: the realised gap averaged -0.19pp, above the sentence in 4 of 10 quarters. "
                     "The 5 Nov 10-Q S&M split (brand vs performance) is what settles whether the ramp is a fixed commitment or a dial.", wrap_cols=12, height=44)
    row += 1

    # ------------- Section 4: the 5 Nov card
    row = S.section(ws, row, "4. The 5 November margin card (calibrated run, audited; the object with the backtest record)", ncols=ncols)
    card = mb["card"].copy()
    S.header(ws, row, ["Value", "Unit", "80% band", "Versus", "Note"], first_col=2, label="Item", height=18); row += 1
    for _, r in card.iterrows():
        v = float(r["value"]); unit = str(r["unit"])
        fmt = S.FMT_PCT if unit == "%" else (S.FMT_PROB if unit == "probability" else (S.FMT_EPS if unit == "USD" else S.FMT_M))
        vv = v / 100 if unit == "%" else v
        ws.cell(row=row, column=1, value=str(r["item"])).font = S.f_label(bold=True)
        c = ws.cell(row=row, column=2, value=vv); c.font = S.f_input(bold=True); c.number_format = fmt
        ws.cell(row=row, column=3, value=unit).font = S.f_note()
        ws.cell(row=row, column=4, value=None if r["band80"] != r["band80"] else str(r["band80"])).font = S.f_label()
        ws.cell(row=row, column=5, value=None if r["vs"] != r["vs"] else str(r["vs"])).font = S.f_label()
        ws.cell(row=row, column=6, value=None if r["note"] != r["note"] else str(r["note"])[:180]).font = S.f_note()
        row += 1
    row = S.text_row(ws, row, "The beat is dollars, not points: the team's revenue is $60M above the Street's; at the Street's own revenue the margin view is worth about $8M (P(margin beats) 0.54). "
                     "Backtest: at h=0 the combination's MAE is 0.50x/0.40x the seasonal naive and 0.71x/0.60x the Street (W1 n 14 / W2 n 10); at h=1 it loses to the raw Street, so 4Q26 is quoted from the Street. "
                     "The pool was chosen after seeing the scoreboard; 5 Nov is the first true out-of-sample observation.", wrap_cols=12, height=44)
    row += 1

    # ------------- Section 5: FY26 sentence / guide expectation
    row = S.section(ws, row, "5. What the FY26 margin sentence should look like on 5 Nov, and what it forces on 4Q26", ncols=ncols)
    cush = mb["cushion"].copy()
    cush = cush[["fy", "bucket", "guide_date", "guide_type", "guide_level_pct", "fy_actual_margin_pct", "cushion_pp", "quote"]].copy()
    cush["guide_level_pct"] = cush["guide_level_pct"] / 100; cush["fy_actual_margin_pct"] = cush["fy_actual_margin_pct"] / 100; cush["cushion_pp"] = cush["cushion_pp"] / 100
    cush = cush.sort_values(["fy", "guide_date"])
    cush.columns = ["FY", "Call", "Guide date", "Type", "Guide level", "FY actual margin", "Cushion (actual - guide)", "Quote"]
    row = S.table(ws, row, cush, first_col=1, fmts={"Guide level": S.FMT_PCT, "FY actual margin": S.FMT_PCT, "Cushion (actual - guide)": S.FMT_PCT, "FY": S.FMT_INT}, header_height=30, wrap_text_cols=["Quote"])
    ws.column_dimensions["I"].width = 9.5
    row = S.text_row(ws, row, "Pattern (M3): the November sentence has been the August floor + 50bp, exactly, in both years it was numeric (FY24: 35% -> 'approximately 35.5%'; FY25: 34.5% -> 'approximately 35%'). "
                     "Forecast for 5 Nov 2026: 'approximately 36%' (p about 0.45-0.50). Every FY floor since 2023 has been beaten by 60-230bp.", wrap_cols=12, height=32)
    row += 1
    S.header(ws, row, ["FY26 sentence", "3Q26 margin", "FY26 EBITDA ($m)", "3Q26 EBITDA ($m)", "4Q26 EBITDA implied ($m)", "4Q26 margin implied", "Reading"], first_col=2, label="Budget identity (bridge v3 revenue: FY26 $14,268m, 4Q26 $3,178m)", height=32); row += 1
    ident = mb["identity"].copy()
    for _, r in ident.iterrows():
        vals = [float(r["fy26_sentence_pct"]) / 100, float(r["q3_margin_pct"]) / 100, float(r["fy26_ebitda_musd"]), float(r["q3_ebitda_musd"]), float(r["q4_ebitda_musd"]), float(r["q4_margin_pct"]) / 100, str(r["q4_margin_reading"])[:60]]
        S.write_row(ws, row, "", vals, fmts=[S.FMT_PCT, S.FMT_PCT, S.FMT_M, S.FMT_M, S.FMT_M, S.FMT_PCT, "@"], kinds=["input"] * 6 + ["label"])
        if abs(float(r["fy26_sentence_pct"]) - 36.0) < 0.01 and abs(float(r["q3_margin_pct"]) - 49.94) < 0.01:
            for cc in range(2, 9):
                ws.cell(row=row, column=cc).fill = S.FILL_KEY
        row += 1
    S.write_row(ws, row, "1pp of the FY26 sentence = pp of 4Q26 margin", [float(ident["pp_of_q4_per_1pp_of_fy"].iloc[0])], fmt=S.FMT_M2, bold=True); row += 1
    S.write_row(ws, row, "1pp of 3Q26 margin = pp of 4Q26 margin", [float(ident["pp_of_q4_per_1pp_of_q3"].iloc[0])], fmt=S.FMT_M2, bold=True); row += 1
    row = S.text_row(ws, row, "Highlighted row: 'approximately 36%' at the run's 3Q26 (49.94%) implies 4Q26 at 30.1% vs the Street's 28.9%, the contestable number. An unchanged 'at least 35.5%' is only an inequality "
                     "(4Q26 >= ~27.6%), i.e. the absence of a raise, not a guide-down. The short case needs a $177M 4Q26 marketing cut to hold the 35.5% floor at its revenue.", wrap_cols=12, height=32)
    row += 1
    fl = mb["floor"].copy()
    fl["floor_pct"] = fl["floor_pct"] / 100; fl["fy26_margin_base_pct"] = fl["fy26_margin_base_pct"] / 100; fl["cushion_pp"] = fl["cushion_pp"] / 100; fl["breakeven_2h26_shortfall_pct"] = fl["breakeven_2h26_shortfall_pct"] / 100
    fl.columns = ["Cost response", "k (cost elasticity)", "Floor", "FY26 margin (run base)", "Cushion", "2H26 revenue shortfall that breaks the floor (%)", "... in $m"]
    row = S.table(ws, row, fl, first_col=1, fmts={"Floor": S.FMT_PCT, "FY26 margin (run base)": S.FMT_PCT, "Cushion": S.FMT_PCT2, "2H26 revenue shortfall that breaks the floor (%)": S.FMT_PCT2, "... in $m": S.FMT_M, "k (cost elasticity)": S.FMT_M2}, header_height=32)
    row += 1

    # ------------- Section 6: FY27 scenario grid and sensitivities
    row = S.section(ws, row, "6. FY27 margin scenarios (line build) and sensitivities", ncols=ncols)
    S.header(ws, row, ["Cost bull", "Cost base", "Cost bear"], first_col=2, label="FY27 adj. EBITDA margin: revenue case x cost case", height=18); row += 1
    grid = {("rev_bull", "cost_bull"): "both_bull", ("rev_bull", "cost_base"): "rev_bull", ("rev_base", "cost_bull"): "cost_bull", ("rev_base", "cost_base"): "base",
            ("rev_base", "cost_bear"): "cost_bear", ("rev_bear", "cost_base"): "rev_bear", ("rev_bear", "cost_bear"): "both_bear"}
    for rc, rlab in [("rev_bull", "Revenue bull (FY27 +15.1%)"), ("rev_base", "Revenue base (FY27 +10.9%)"), ("rev_bear", "Revenue bear (FY27 +5.5%)")]:
        vals = []
        for cc in ["cost_bull", "cost_base", "cost_bear"]:
            k = grid.get((rc, cc)); vals.append(S.pct(ann.loc[("FY27", k), "adj_ebitda_margin_pct"]) if k else None)
        S.write_row(ws, row, rlab, vals, fmt=S.FMT_PCT, indent=1, fill=None); row += 1
    S.header(ws, row, ["Cost bull", "Cost base", "Cost bear"], first_col=2, label="FY26 adj. EBITDA margin: same grid", height=18); row += 1
    for rc, rlab in [("rev_bull", "Revenue bull"), ("rev_base", "Revenue base"), ("rev_bear", "Revenue bear")]:
        vals = []
        for cc in ["cost_bull", "cost_base", "cost_bear"]:
            k = grid.get((rc, cc)); vals.append(S.pct(ann.loc[("FY26", k), "adj_ebitda_margin_pct"]) if k else None)
        S.write_row(ws, row, rlab, vals, fmt=S.FMT_PCT, indent=1); row += 1
    row = S.text_row(ws, row, "Costs do not flex with revenue in the revenue cases except through the drivers (GBV, bookings, nights): the M6 finding is that Airbnb's discretionary lines have not responded to revenue within a year "
                     "(cash-cost elasticity 0.364, t 6.6, n 18; asymmetric, it cuts less readily than it spends). Rule of thumb: 0.35-0.6pp of FY27 margin per 1pt of revenue.", wrap_cols=12, height=32)
    row += 1
    sens = mb["sens"].copy()
    sens = sens[["parameter", "shock", "d_3q26_ebitda_musd", "d_fy27_margin_pp", "d_fy27_eps_usd"]]
    sens["d_fy27_margin_pp"] = sens["d_fy27_margin_pp"] / 100
    sens.columns = ["Parameter", "Shock", "d 3Q26 EBITDA ($m)", "d FY27 margin", "d FY27 EPS ($)"]
    row = S.table(ws, row, sens, first_col=1, fmts={"d 3Q26 EBITDA ($m)": S.FMT_M1, "d FY27 margin": S.FMT_PCT2, "d FY27 EPS ($)": S.FMT_EPS}, header_height=30)
    row += 1
    mac = mb["macro"].copy()
    mac = mac[mac.revenue_shock_pct.isin([-3, -1, 1]) & mac.cost_response.isin(["held", "flex"])][["period", "cost_response", "k", "revenue_shock_pct", "margin_base_pct", "margin_shocked_pct", "margin_delta_pp", "pp_per_1pct_revenue"]].copy()
    for c in ["revenue_shock_pct", "margin_base_pct", "margin_shocked_pct", "margin_delta_pp", "pp_per_1pct_revenue"]:
        mac[c] = mac[c] / 100
    mac.columns = ["Period", "Cost response", "k", "Revenue shock", "Margin base (run)", "Margin shocked", "Margin delta", "pp per 1% of revenue"]
    row = S.table(ws, row, mac, first_col=1, fmts={"Revenue shock": S.FMT_PCT, "Margin base (run)": S.FMT_PCT, "Margin shocked": S.FMT_PCT, "Margin delta": S.FMT_PCT2, "pp per 1% of revenue": S.FMT_PCT2, "k": S.FMT_M2}, header_height=30)
    row += 1

    # ------------- Section 7: short case
    row = S.section(ws, row, "7. The short case, quarter by quarter: the lap plus RNPL cancellations on a budgeted cost base", ncols=ncols)
    st = mb["short_stress"].copy()
    for c in ["revenue_vs_team_path_pct", "nights_yoy", "sm_pct_rev", "total_cash_costs_pct_rev", "margin", "margin_vs_base_pp"]:
        st[c] = st[c] / 100
    st.columns = ["Quarter", "Revenue ($m)", "Revenue vs team path", "Nights y/y", "Ops & support ($m)", "Ops per booking ($)", "Chargebacks ($m)", "Interest income ($m)", "S&M % revenue", "Total cash costs % revenue", "Margin", "Margin vs base (pp)"]
    row = S.table(ws, row, st, first_col=1, fmts={"Revenue vs team path": S.FMT_PCT, "Nights y/y": S.FMT_PCT, "S&M % revenue": S.FMT_PCT, "Total cash costs % revenue": S.FMT_PCT, "Margin": S.FMT_PCT, "Margin vs base (pp)": S.FMT_PCT2, "Revenue ($m)": S.FMT_M, "Ops & support ($m)": S.FMT_M, "Chargebacks ($m)": S.FMT_M1, "Interest income ($m)": S.FMT_M, "Ops per booking ($)": S.FMT_M2}, header_height=32)
    ssum = mb["short_summary"].copy()
    ssum = ssum[["case", "q3_revenue", "q3_ebitda", "q3_margin", "q3_eps", "q4_revenue", "q4_ebitda", "q4_margin", "q4_marketing_cut_musd", "fy26_revenue", "fy26_ebitda", "fy26_margin", "fy27_revenue", "fy27_ebitda", "fy27_margin", "fy27_eps"]]
    for c in ["q3_margin", "q4_margin", "fy26_margin", "fy27_margin"]:
        ssum[c] = ssum[c] / 100
    ssum.columns = ["Case", "3Q26 revenue", "3Q26 EBITDA", "3Q26 margin", "3Q26 EPS", "4Q26 revenue", "4Q26 EBITDA", "4Q26 margin", "4Q26 marketing cut ($m)", "FY26 revenue", "FY26 EBITDA", "FY26 margin", "FY27 revenue", "FY27 EBITDA", "FY27 margin", "FY27 EPS"]
    row = S.table(ws, row, ssum, first_col=1, fmts={"3Q26 margin": S.FMT_PCT, "4Q26 margin": S.FMT_PCT, "FY26 margin": S.FMT_PCT, "FY27 margin": S.FMT_PCT, "3Q26 EPS": S.FMT_EPS, "FY27 EPS": S.FMT_EPS}, default_fmt=S.FMT_M, header_height=32)
    row = S.text_row(ws, row, "Assumptions: nights +8.5% in 3Q26 then +5/+4/+2/+3/+4% through 4Q27; ADR ex-FX +2.5% then flat; FX on the kernel; take rate on the team path. RNPL overlays: ops & support +4% per completed booking, "
                     "chargebacks +$0.15 per booking, funds held -10% (interest income). Costs at management's budget. Almost all of the margin gap is revenue on fixed cost: total cash costs go from 77% to 88% of revenue in the low quarters. "
                     "Evidence standard = disclosed mechanism plus current data, not a backtest; not re-audited by Codex.", wrap_cols=12, height=44)
    row += 1

    # ------------- Section 8: seasonality
    row = S.section(ws, row, "8. Seasonality: the margin is a revenue phenomenon, not a cost one", ncols=ncols)
    se = mb["seasonality"].copy()
    se = se[se.quarter >= "2024Q1"][["quarter", "revenue_musd", "margin_pct", "mechanical_cost_pct_rev", "discretionary_cost_pct_rev", "hist_margin_mean_2022_26", "hist_margin_sd"]]
    for c in ["margin_pct", "mechanical_cost_pct_rev", "discretionary_cost_pct_rev", "hist_margin_mean_2022_26", "hist_margin_sd"]:
        se[c] = se[c] / 100
    se.columns = ["Quarter", "Revenue ($m, run base)", "Margin", "Mechanical cost % rev (CoR + ops)", "Discretionary cost % rev (PD + S&M + G&A)", "Same-quarter margin mean 2022-26", "sd"]
    row = S.table(ws, row, se, first_col=1, fmts={"Margin": S.FMT_PCT, "Mechanical cost % rev (CoR + ops)": S.FMT_PCT, "Discretionary cost % rev (PD + S&M + G&A)": S.FMT_PCT, "Same-quarter margin mean 2022-26": S.FMT_PCT, "sd": S.FMT_PCT2, "Revenue ($m, run base)": S.FMT_M}, header_height=32)
    row = S.text_row(ws, row, "Product development, S&M and G&A run $1.4-1.7bn every quarter regardless of season; that is why 1Q27 is a 19-20% margin quarter. 3Q26 at 49.9% is 1.0 sd below its own 2022-26 seasonal mean (51.8%), and that gap is the marketing ramp.", wrap_cols=12, height=30)
    row += 1
    row = S.sources_block(ws, row, [
        ("Cost lines, history", "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv, 02_panel_annual.csv"),
        ("Cost lines, forecast by scenario", "data/processed/margin_build/40_line_build/40_lines_quarterly.csv, 40_annual.csv, 40_params.csv, 40_sentence_implied.csv, 40_sensitivities.csv; docs/margin-build/notes/40_line_build.md"),
        ("Calibrated run and the 5 Nov card", "data/processed/margin_build/23_final_model/23_card_5nov.csv, 23_forecast_quarterly.csv, 23_forecast_annual.csv, 23_card_budget_identity.csv, 23_fy26_floor_breakeven.csv, 23_macro_sensitivity.csv, 23_seasonality.csv; docs/margin-build/MORNING_REPORT.md, SYNTHESIS.md"),
        ("FY sentence history", "data/processed/margin_build/M3_guide_policy_margin/M3_cushion_history.csv, M3_q4_implied_live_5nov.csv"),
        ("Short case", "data/processed/margin_build/40_line_build/40_short_case_*.csv"),
        ("Street", "data/processed/margin_build/03_consensus_pit/03_current_consensus.csv (LSEG, 11 Sep 2026)"),
    ], ncols=ncols)
    S.freeze(ws, f"B{HDR_ROW+1}")
    wb._margin_rows = rows
    return ws
