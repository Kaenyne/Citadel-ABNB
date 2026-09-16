"""'Cover' tab: what the workbook is, how to read it, the tab map, the headline numbers and provenance."""
import datetime as _dt
import style as S
import data as Dt


def build(wb):
    ws = wb.create_sheet("Cover")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 34
    for c in "CDEFGHIJ":
        ws.column_dimensions[c].width = 13
    ws.column_dimensions["K"].width = 40
    ws["B2"] = "Airbnb (ABNB): the team's forecasting model in one workbook"
    ws["B2"].font = S.f_title()
    ws["B3"] = f"2026 Citadel Intercollegiate Stock Pitch Competition. Built {_dt.date.today():%d %b %Y} from the repo's processed outputs (main at PR #56). Prelim memo due 2 Oct 2026; next print 5 Nov 2026 (3Q26)."
    ws["B3"].font = S.f_sub()
    row = 5
    row = S.section(ws, row, "What this is", ncols=11)
    row = S.bullets(ws, row, [
        "One place to see everything the team has built for the upcoming quarters: the revenue model (nights x ADR x FX x take rate), the cost stack line by line, a full income statement to FY27, "
        "the operating schedules behind them, the annotated stock history, the two reverse-DCF studies, and the Street/guidance comparison with its price implications.",
        "Nothing here is typed in by hand: every blue number is read from a CSV in data/processed (the path is beside it or in the Sources block at the foot of each tab); every black number is an Excel formula. "
        "Rebuild with:  py -3.13 analysis/src/model_workbook/build.py   (the script recalculates in Excel and saves the cached values).",
        "Two cases run through the workbook. BASE = the team model (bridge v3 revenue path, 40_line_build costs). SHORT = the pitch case added 15 Sep (the 4Q25-1Q26 bundle and the World Cup flattered 1H26 nights; "
        "RNPL eligibility expanding into a cohort that cancels more; costs at management's budget). STREET = LSEG/Bloomberg consensus, 11-12 Sep 2026.",
    ], col=2, wrap_cols=10, height=44)
    row += 1
    row = S.section(ws, row, "How to read it", ncols=11)
    conv = [("Blue font", "hard-coded source value from a repo CSV", S.f_input()), ("Black font", "formula in this sheet", S.f_formula()), ("Green font", "link to another tab", S.f_link()),
            ("Grey italic", "note, source, caveat", S.f_note())]
    for lab, desc, font in conv:
        ws.cell(row=row, column=2, value=lab).font = font
        ws.cell(row=row, column=3, value=desc).font = S.f_label(); row += 1
    for lab, desc, fill in [("Yellow fill", "forecast column (3Q26E onward)", S.FILL_FORECAST), ("Green fill", "team base case", S.FILL_KEY), ("Orange fill", "short (pitch) case", S.FILL_SHORT), ("Grey fill", "Street consensus", S.FILL_STREET), ("Pink fill", "bear / warning", S.FILL_WARN)]:
        c = ws.cell(row=row, column=2, value=lab); c.fill = fill; c.font = S.f_label()
        ws.cell(row=row, column=3, value=desc).font = S.f_label(); row += 1
    row = S.bullets(ws, row, [
        "The Income Statement tab has a scenario dropdown in cell B3, set to the Short case (the pitch) by default; the other options are Base (team model), the Short case with the 4Q26 marketing cut, evidence-only costs, and revenue/cost bear and bull. The forecast columns on the Income Statement, Margins and "
        "Operating Schedules tabs re-flow to the chosen scenario; the Revenue Model and 5 Nov & Street tabs always show Base, Short and Street side by side.",
        "Units are USD millions unless a row says otherwise; nights in millions; GBV in $bn; percentages are y/y unless labelled '% of revenue'. Quarters are labelled 1Q23A ... 4Q27E.",
        "Forecast vs scenario: 3Q26 is a tested forecast (the calibrated margin combination beat the Street 14/14 and 10/10 at h=0 in the two backtest windows; the revenue bridge and nights index were scored through the harness). "
        "4Q26 margin is quoted from the Street (no h=1 edge). FY27 is a labelled spending scenario. FY28 is a roll-forward, not a forecast. The short case is a mechanism-plus-current-data view, not a backtest.",
    ], col=2, wrap_cols=10, height=44)
    row += 1
    row = S.section(ws, row, "Tab map", ncols=11)
    tabs = [
        ("Income Statement", "Quarterly 1Q23A-4Q27E and FY23-FY27: KPIs, cash cost lines, adjusted EBITDA, GAAP bridge to EPS. Scenario dropdown. Street and Short comparison rows underneath."),
        ("Revenue Model", "Nights (with the regional and lap builds), ADR ex-FX and FX, GBV, take rate, the bridge conversion, revenue; bear/bull/short scenarios; Street on every KPI; the 3Q26 guide in force and the 4Q26 guide the model implies; guide history."),
        ("Margins", "Each cost line with its drivers, the 3Q26 'down slightly' reconciliation, the 5 Nov margin card (calibrated run), the FY26 sentence expectation and budget identity, FY27 scenario grid, sensitivities, the short case quarter by quarter, seasonality."),
        ("Operating Schedules", "Bookings and unit economics, revenue by region, the 2027 nights and ADR builds, FX paths, unit-cost drivers, below-EBITDA items, the full parameter sheet."),
        ("5 Nov & Street", "Key items side by side (Street / base / short / management delivered), the 5 Nov sequence the model expects, and what each path implies for the price (joint solve, fixed multiple, print reaction, repricing ladder)."),
        ("Stock Chart", "Annotated price history since the IPO: every earnings reaction, every 7%+ day and its driver, and the read-across to 5 Nov."),
        ("Reverse DCF - Mgmt", "What management's words are worth: Literal / Delivered / Ambition cases, inputs, implied prices by lens, reverse-DCF growth."),
        ("Reverse DCF - Market", "What the price, the options market and the sell-side tape are paying for; the reaction function; the positioning card."),
        ("Scenario Data", "The data block behind the dropdown (every scenario x line x quarter). Reference only."),
    ]
    for name, desc in tabs:
        c = ws.cell(row=row, column=2, value=name); c.font = S.f_link(bold=True)
        c.hyperlink = f"#'{name}'!A1"
        d = ws.cell(row=row, column=3, value=desc); d.font = S.f_label()
        d.alignment = S.Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=11)
        ws.row_dimensions[row].height = 30
        row += 1
    row += 1
    row = S.section(ws, row, "The numbers in one table", ncols=11)
    cons = Dt.consensus(); lseg = cons["lseg"]
    sq = Dt.scenario_quarterly()
    base = sq[sq.scenario == "base"].set_index("quarter"); short = sq[sq.scenario == "short_costs_at_budget"].set_index("quarter")
    ann = Dt.margin_build()["annual"].set_index(["period", "scenario"]); sca = Dt.short_case_annual()
    ss = Dt.margin_build()["short_summary"].set_index("case").loc["short_costs_at_budget"]
    S.header(ws, row, ["Street", "Team base", "Short (pitch)", "Base vs Street", "Short vs Street"], first_col=3, label="", height=18)
    ws.cell(row=row, column=2, value="Item").font = S.f_hdr(); ws.cell(row=row, column=2).fill = S.FILL_HEADER
    row += 1
    def line(lab, st, tb, sh, fmt, diff="pct"):
        nonlocal row
        d1 = f"=D{row}/C{row}-1" if diff == "pct" else f"=D{row}-C{row}"
        d2 = (f"=E{row}/C{row}-1" if diff == "pct" else f"=E{row}-C{row}") if sh is not None else None
        S.write_row(ws, row, "", [st, tb, sh, d1, d2], first_col=3, fmts=[fmt, fmt, fmt, S.FMT_PCT if diff == "pct" else S.FMT_PCT2, S.FMT_PCT if diff == "pct" else S.FMT_PCT2], kinds=["input", "input", "input", "formula", "formula"])
        ws.cell(row=row, column=2, value=lab).font = S.f_label()
        ws.cell(row=row, column=3).fill = S.FILL_STREET; ws.cell(row=row, column=4).fill = S.FILL_KEY
        if sh is not None:
            ws.cell(row=row, column=5).fill = S.FILL_SHORT
        row += 1
    line("3Q26 revenue ($m)", float(lseg.loc["3Q26", "revenue_mean"]), float(base.loc["3Q26", "revenue"]), float(short.loc["3Q26", "revenue"]), S.FMT_M)
    line("3Q26 nights y/y", S.pct(cons["bbg"].query("quarter=='3Q26' and metric=='nights_m'").street_mean_growth.iloc[0]), S.pct(Dt.revenue_path_wide("base").loc["nights_yoy_pct", "3Q26"]), S.pct(Dt.margin_build()["short_path"].set_index("quarter").loc["3Q26", "nights_yoy_pct"]), S.FMT_PCT, diff="pp")
    line("3Q26 adj. EBITDA ($m)", float(lseg.loc["3Q26", "ebitda_mean"]), float(base.loc["3Q26", "adj_ebitda"]), float(short.loc["3Q26", "adj_ebitda"]), S.FMT_M)
    line("3Q26 adj. EBITDA margin", S.pct(lseg.loc["3Q26", "implied_margin_pct"]), S.pct(base.loc["3Q26", "adj_ebitda_margin_pct"]), S.pct(short.loc["3Q26", "adj_ebitda_margin_pct"]), S.FMT_PCT, diff="pp")
    line("3Q26 EPS ($)", float(lseg.loc["3Q26", "eps_mean"]), float(base.loc["3Q26", "eps"]), float(short.loc["3Q26", "eps"]), S.FMT_EPS)
    line("4Q26 revenue ($m)", float(lseg.loc["4Q26", "revenue_mean"]), float(base.loc["4Q26", "revenue"]), float(short.loc["4Q26", "revenue"]), S.FMT_M)
    line("4Q26 adj. EBITDA ($m)", float(lseg.loc["4Q26", "ebitda_mean"]), float(base.loc["4Q26", "adj_ebitda"]), float(short.loc["4Q26", "adj_ebitda"]), S.FMT_M)
    line("FY26 revenue ($m)", float(lseg.loc["FY26", "revenue_mean"]), float(ann.loc[("FY26", "base"), "revenue"]), float(sca.loc[("short_costs_at_budget", "FY26"), "revenue"]), S.FMT_M)
    line("FY26 adj. EBITDA margin", S.pct(lseg.loc["FY26", "implied_margin_pct"]), S.pct(ann.loc[("FY26", "base"), "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda_margin_pct"]), S.FMT_PCT, diff="pp")
    line("FY26 EPS ($)", float(lseg.loc["FY26", "eps_mean"]), float(ann.loc[("FY26", "base"), "eps"]), None, S.FMT_EPS)
    line("FY27 revenue ($m)", float(lseg.loc["FY27", "revenue_mean"]), float(ann.loc[("FY27", "base"), "revenue"]), float(sca.loc[("short_costs_at_budget", "FY27"), "revenue"]), S.FMT_M)
    line("FY27 adj. EBITDA ($m)", float(lseg.loc["FY27", "ebitda_mean"]), float(ann.loc[("FY27", "base"), "adj_ebitda"]), float(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda"]), S.FMT_M)
    line("FY27 adj. EBITDA margin", S.pct(lseg.loc["FY27", "implied_margin_pct"]), S.pct(ann.loc[("FY27", "base"), "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda_margin_pct"]), S.FMT_PCT, diff="pp")
    line("FY27 EPS ($)", float(lseg.loc["FY27", "eps_mean"]), float(ann.loc[("FY27", "base"), "eps"]), float(ss["fy27_eps"]), S.FMT_EPS)
    row += 1
    row = S.section(ws, row, "The pitch in six lines (short; see 5 Nov & Street for the arithmetic)", ncols=11)
    row = S.bullets(ws, row, [
        "The market is positioned for an accelerating 3Q26 nights print (Street +11.5%, every estimate at or above 2Q26's +10.3%); the team's nowcast is a deceleration (+9.9% base, band 8.5-11.0; +8.5% short). "
        "On the only print reaction with statistical support (post-2022 sign rule, n 14) a decelerating print has averaged -5.6% day-1 excess against a 9.5% options-implied dispersion.",
        "1H26 nights were flattered by the 4Q25-1Q26 bundle and the June-July World Cup; the underlying rate is 6-7%, not 9-10%. RNPL eligibility is widening into a cohort that cancels more, with no volume offset in the alt data.",
        "On the short path the 4Q26 revenue guide lands 6-10% below the Street and FY26 needs a $177M marketing cut to hold the 35.5% floor; FY27 EBITDA is $4.8bn / 31.9% against the Street's $5.8bn / 36.5%.",
        "Even on the team's own base path, 5 Nov is 'a beat on dollars, not points' (3Q26 EBITDA $2,420m vs $2,362m) followed by a 4Q26 guide midpoint about 3% below the Street, because the Street prices the guide plus the cushion.",
        "The Street's FY27 margin needs the marketing ramp to stop (43.7% incremental margin); the line build's S&M path (19.4% -> 21.3% -> 21.9% of revenue) gives 35.7%, the calibrated run 34.6%.",
        "Price: $170 pays 16x for FY27 revenue of $15.7-15.9bn (the Street and the team base); the team bear is worth $121-137 and the short case about $140-148 on the same arithmetic (indicative).",
    ], col=2, wrap_cols=10, height=44)
    row += 1
    row = S.section(ws, row, "Provenance and what not to quote", ncols=11)
    row = S.bullets(ws, row, [
        "Revenue: bridge v3 (PR #52, 12 Sep) on the quarterly nights path (PR #32), ADR card v3 (PR #46), the FX-lag kernel (WS05) and the WS06 v2b 2027 path. Margins: the 13-15 Sep margin build (PR #56): calibrated combination "
        "(23_final_model, Codex-audited, 18 findings closed) and the line build (40_line_build, Codex read-only check, 7 findings fixed). Reverse DCF: PR #49 and the 12-13 Sep market-implied run. Stock history: the predictive study.",
        "Withdrawn numbers (do not quote): P(beat) 0.77 (now 0.779), the 3Q26 band $2,299-2,499m (now $2,337-2,462m), 'attained coverage 82-91%', 'Airbnb has no cost dial', S&M $790M/+35% (now $781M/+33.5%), FY27 S&M $3,740M/23.6% (run) or the WS31b 4Q26 margin profile of 24.7-25.9%. "
        "The full kill list is in docs/revenue-forecast-strategy/AGENT_BRIEF.md section 6 and docs/margin-build/SYNTHESIS.md section 9.",
        "Consensus is a comparison column, never an input. Every consensus value in this workbook carries its vendor and pull date. The Bloomberg KPI distribution is a 5-12 Sep pull, the LSEG means are 11 Sep.",
        "Open items for the team (from the margin build): the revenue_leg_live harness patch; reconcile or retire WS31b; a genuine h=1 object for 4Q26; the G&A residual allocation; the 5 Nov 10-Q S&M split will settle whether the ramp is a commitment or a dial.",
    ], col=2, wrap_cols=10, height=44)
    return ws
