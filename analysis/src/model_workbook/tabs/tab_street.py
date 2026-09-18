"""'5 Nov & Street' tab: the key items side by side (Street / team base / short case / management delivered), the 5 Nov
sequence the model expects (print, 4Q26 guide, FY26 sentence), and what each path implies for the share price."""
import json
import style as S
import data as Dt

SHEET = "5 Nov & Street"


def build(wb):
    ws = wb.create_sheet(SHEET)
    S.setup(ws, "5 November and the Street: where the team sits on every key item, the guide we expect, and what it implies for the stock",
            "Street = LSEG mean 11 Sep 2026 (revenue/EBITDA/EPS) and Bloomberg estimate distribution 5-12 Sep (nights/GBV/ADR). Team base = "
            "this workbook's base scenario. Short = the pitch case. Blue = source value, black = formula.", label_width=50)
    widths = {"B": 16, "C": 16, "D": 16, "E": 13, "F": 12, "G": 14, "H": 12, "I": 60}
    for k, v in widths.items():
        ws.column_dimensions[k].width = v
    cons = Dt.consensus(); lseg = cons["lseg"]; vs = cons["vs"]; bbg = cons["bbg"]
    sq = Dt.scenario_quarterly()
    base = sq[sq.scenario == "base"].set_index("quarter")
    short = sq[sq.scenario == "short_costs_at_budget"].set_index("quarter")
    sca = Dt.short_case_annual()
    ann = Dt.margin_build()["annual"].set_index(["period", "scenario"])
    rp = Dt.revenue_path_wide("base")
    rann = Dt.read("margin_build/06_fy27_path_v2/06_annual_fy26_fy28_v2b.csv").set_index(["scenario", "period"])
    sp = Dt.margin_build()["short_path"].set_index("quarter")
    mg = Dt.read("reverse_dcf/mgmt_implied_summary.csv"); mg = mg[mg.scenario == "Delivered"].set_index("period")
    ss = Dt.margin_build()["short_summary"].set_index("case").loc["short_costs_at_budget"]
    hq = Dt.history_quarterly()
    row = 4

    def bq(q, m, c):
        d = bbg[(bbg.quarter == q) & (bbg.metric == m)]
        return None if d.empty else float(d[c].iloc[0])

    # ---------------- Section 1
    row = S.section(ws, row, "1. Key items: Street, team base, short case, management delivered", ncols=9)
    S.header(ws, row, ["Street", "n", "Team base", "Base vs Street", "Short (pitch)", "Short vs Street", "Mgmt delivered", "Notes"], first_col=2, label="Item", height=18); row += 1

    def item(label, street, n, tb, sh, mgmt, fmt, note="", diff="pct"):
        nonlocal row
        d1 = (f"=IFERROR(D{row}/B{row}-1,\"\")" if diff == "pct" else f"=IFERROR(D{row}-B{row},\"\")") if (tb is not None and street is not None) else None
        d2 = (f"=IFERROR(F{row}/B{row}-1,\"\")" if diff == "pct" else f"=IFERROR(F{row}-B{row},\"\")") if (sh is not None and street is not None) else None
        dfmt = S.FMT_PCT if diff == "pct" else S.FMT_PCT2
        S.write_row(ws, row, label, [street, n, tb, d1, sh, d2, mgmt, note], fmts=[fmt, S.FMT_INT, fmt, dfmt, fmt, dfmt, fmt, "@"],
                    kinds=["input", "input", "input", "formula", "input", "formula", "input", "label"])
        ws.cell(row=row, column=2).fill = S.FILL_STREET
        ws.cell(row=row, column=4).fill = S.FILL_KEY
        ws.cell(row=row, column=6).fill = S.FILL_SHORT
        ws.cell(row=row, column=9).font = S.f_note()
        row += 1

    def sub(t):
        nonlocal row
        ws.cell(row=row, column=1, value=t).font = S.f_label(bold=True); row += 1

    sub("3Q26 (prints 5 Nov)")
    item("Revenue ($m)", float(lseg.loc["3Q26", "revenue_mean"]), int(lseg.loc["3Q26", "revenue_n"]), float(base.loc["3Q26", "revenue"]), float(sp.loc["3Q26", "revenue_musd"]), None, S.FMT_M, "guide $4,690-4,770m; the base sits above the top end, as 15 of the last 19 prints did")
    item("Nights & seats y/y", S.pct(bq("3Q26", "nights_m", "street_mean_growth")), int(bq("3Q26", "nights_m", "n_estimates")), S.pct(rp.loc["nights_yoy_pct", "3Q26"]), S.pct(sp.loc["3Q26", "nights_yoy_pct"]), 0.115, S.FMT_PCT, "guide 'low double digits'; 2Q26 printed +10.3%. Every Street estimate is at or above 2Q26's rate; the team is below the lowest", diff="pp")
    item("ADR y/y reported", S.pct(bq("3Q26", "adr_usd", "street_mean_growth")), int(bq("3Q26", "adr_usd", "n_estimates")), S.pct(rp.loc["adr_reported_yoy_pct", "3Q26"]), S.pct(sp.loc["3Q26", "adr_reported_yoy_pct"]), None, S.FMT_PCT, "ADR card v3 +3.9% ex-FX, FX -0.4pt", diff="pp")
    item("GBV y/y", S.pct(bq("3Q26", "gbv_musd", "street_mean_growth")), int(bq("3Q26", "gbv_musd", "n_estimates")), S.pct(rp.loc["gbv_yoy_pct", "3Q26"]), None, None, S.FMT_PCT, "guide 'mid teens'", diff="pp")
    item("Adj. EBITDA ($m)", float(lseg.loc["3Q26", "ebitda_mean"]), int(lseg.loc["3Q26", "ebitda_n"]), float(base.loc["3Q26", "adj_ebitda"]), float(short.loc["3Q26", "adj_ebitda"]), None, S.FMT_M, "calibrated run $2,399m, 80% band $2,337-2,462m, P(beat) 0.78; line build $2,420m")
    item("Adj. EBITDA margin", S.pct(lseg.loc["3Q26", "implied_margin_pct"]), int(lseg.loc["3Q26", "ebitda_n"]), S.pct(base.loc["3Q26", "adj_ebitda_margin_pct"]), S.pct(short.loc["3Q26", "adj_ebitda_margin_pct"]), None, S.FMT_PCT, "sentence 'down slightly' vs 50.1%; ceiling 50.085%; P(margin beats) 0.54", diff="pp")
    item("Diluted EPS ($)", float(lseg.loc["3Q26", "eps_mean"]), int(lseg.loc["3Q26", "eps_n"]), float(base.loc["3Q26", "eps"]), float(short.loc["3Q26", "eps"]), None, S.FMT_EPS, "run $2.88 (band $2.70-3.05)")
    sub("4Q26 (guided 5 Nov, prints Feb 2027)")
    item("Revenue ($m)", float(lseg.loc["4Q26", "revenue_mean"]), int(lseg.loc["4Q26", "revenue_n"]), float(base.loc["4Q26", "revenue"]), float(sp.loc["4Q26", "revenue_musd"]), None, S.FMT_M, "the guide will sit below the print by the cushion (about 3.9% in Q4s): see section 2")
    item("Nights & seats y/y", S.pct(bq("4Q26", "nights_m", "street_mean_growth")), int(bq("4Q26", "nights_m", "n_estimates")), S.pct(rp.loc["nights_yoy_pct", "4Q26"]), S.pct(sp.loc["4Q26", "nights_yoy_pct"]), None, S.FMT_PCT, "ex-NA lap adopted (case B); NA-only lap would be +8.9%", diff="pp")
    item("ADR y/y reported", S.pct(bq("4Q26", "adr_usd", "street_mean_growth")), int(bq("4Q26", "adr_usd", "n_estimates")), S.pct(rp.loc["adr_reported_yoy_pct", "4Q26"]), S.pct(sp.loc["4Q26", "adr_reported_yoy_pct"]), None, S.FMT_PCT, "", diff="pp")
    item("Adj. EBITDA ($m)", float(lseg.loc["4Q26", "ebitda_mean"]), int(lseg.loc["4Q26", "ebitda_n"]), float(base.loc["4Q26", "adj_ebitda"]), float(short.loc["4Q26", "adj_ebitda"]), None, S.FMT_M, "no h=1 edge: the run quotes the Street ($918m); line build $899m; short $700m at budget / $876m with the marketing cut")
    item("Adj. EBITDA margin", S.pct(lseg.loc["4Q26", "implied_margin_pct"]), int(lseg.loc["4Q26", "ebitda_n"]), S.pct(base.loc["4Q26", "adj_ebitda_margin_pct"]), S.pct(short.loc["4Q26", "adj_ebitda_margin_pct"]), None, S.FMT_PCT, "'approximately 36%' FY sentence at the run's 3Q26 implies 30.1%", diff="pp")
    item("Diluted EPS ($)", float(lseg.loc["4Q26", "eps_mean"]), int(lseg.loc["4Q26", "eps_n"]), float(base.loc["4Q26", "eps"]), float(short.loc["4Q26", "eps"]), None, S.FMT_EPS, "")
    sub("FY26")
    item("Revenue ($m)", float(lseg.loc["FY26", "revenue_mean"]), int(lseg.loc["FY26", "revenue_n"]), float(ann.loc[("FY26", "base"), "revenue"]), float(sca.loc[("short_costs_at_budget", "FY26"), "revenue"]), float(mg.loc["FY26", "revenue_musd"]), S.FMT_M, "")
    item("Adj. EBITDA ($m)", float(lseg.loc["FY26", "ebitda_mean"]), int(lseg.loc["FY26", "ebitda_n"]), float(ann.loc[("FY26", "base"), "adj_ebitda"]), float(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda"]), float(mg.loc["FY26", "adj_ebitda_musd"]), S.FMT_M, "floor 'at least 35.5%' breaks on a 2H26 revenue miss of $50m held / $75m flexed")
    item("Adj. EBITDA margin", S.pct(lseg.loc["FY26", "implied_margin_pct"]), int(lseg.loc["FY26", "ebitda_n"]), S.pct(ann.loc[("FY26", "base"), "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY26"), "adj_ebitda_margin_pct"]), S.pct(mg.loc["FY26", "adj_ebitda_margin_pct"]), S.FMT_PCT, "short case: 34.2% at budget (floor broken) or 35.5% with a $177m Q4 marketing cut", diff="pp")
    item("Diluted EPS ($)", float(lseg.loc["FY26", "eps_mean"]), int(lseg.loc["FY26", "eps_n"]), float(ann.loc[("FY26", "base"), "eps"]), None, float(mg.loc["FY26", "eps_gaap"]), S.FMT_EPS, "")
    sub("FY27 (the trade)")
    item("Revenue ($m)", float(lseg.loc["FY27", "revenue_mean"]), int(lseg.loc["FY27", "revenue_n"]), float(ann.loc[("FY27", "base"), "revenue"]), float(sca.loc[("short_costs_at_budget", "FY27"), "revenue"]), float(mg.loc["FY27", "revenue_musd"]), S.FMT_M, "Street FY27 = management's delivered case; the price pays for $15.7-15.9bn")
    item("Revenue growth", S.pct((lseg.loc["FY27", "revenue_mean"] / lseg.loc["FY26", "revenue_mean"] - 1) * 100), int(lseg.loc["FY27", "revenue_n"]), S.pct(rann.loc[("base", "FY27"), "revenue_musd_yoy_pct"]), float(sca.loc[("short_costs_at_budget", "FY27"), "revenue"]) / float(sca.loc[("short_costs_at_budget", "FY26"), "revenue"]) - 1, float(mg.loc["FY27", "revenue_musd"]) / float(mg.loc["FY26", "revenue_musd"]) - 1, S.FMT_PCT, "", diff="pp")
    item("Nights growth", None, None, S.pct(rann.loc[("base", "FY27"), "nights_mm_yoy_pct"]), float(sca.loc[("short_costs_at_budget", "FY27"), "nights_m"]) / float(sca.loc[("short_costs_at_budget", "FY26"), "nights_m"]) - 1, float(mg.loc["FY27", "nights_m"]) / float(mg.loc["FY26", "nights_m"]) - 1, S.FMT_PCT, "no direct Street nights consensus for FY27; the joint solve backs out +8 to +9% at the price", diff="pp")
    item("Adj. EBITDA ($m)", float(lseg.loc["FY27", "ebitda_mean"]), int(lseg.loc["FY27", "ebitda_n"]), float(ann.loc[("FY27", "base"), "adj_ebitda"]), float(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda"]), float(mg.loc["FY27", "adj_ebitda_musd"]), S.FMT_M, "calibrated run $5,483m (34.6%, a spending scenario); Street needs a 43.7% incremental margin")
    item("Adj. EBITDA margin", S.pct(lseg.loc["FY27", "implied_margin_pct"]), int(lseg.loc["FY27", "ebitda_n"]), S.pct(ann.loc[("FY27", "base"), "adj_ebitda_margin_pct"]), S.pct(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda_margin_pct"]), S.pct(mg.loc["FY27", "adj_ebitda_margin_pct"]), S.FMT_PCT, "S&M 19.4% (FY25) -> 21.3% (FY26) -> 21.9% (FY27) of revenue", diff="pp")
    item("Diluted EPS ($)", float(lseg.loc["FY27", "eps_mean"]), int(lseg.loc["FY27", "eps_n"]), float(ann.loc[("FY27", "base"), "eps"]), float(ss["fy27_eps"]), float(mg.loc["FY27", "eps_gaap"]), S.FMT_EPS, "")
    row += 1

    # ---------------- Section 2: the 5 Nov sequence
    row = S.section(ws, row, "2. The 5 November sequence the model expects (links to the Revenue Model and Margins tabs)", ncols=9)
    rr = wb._rev_rows
    S.header(ws, row, ["Base path", "Short path", "Street / prior", "Comment"], first_col=2, label="Item", height=18); row += 1
    seq = [
        ("3Q26 revenue print vs guide midpoint ($4,730m)", f"='Revenue Model'!P{rr['rev']}/4730-1", f"='Revenue Model'!P{rr['rev_Short (pitch)']}/4730-1", 0.0125, S.FMT_PCT, "prior: Q3 prints landed +1.3% above the midpoint on average"),
        ("3Q26 nights y/y print", f"='Revenue Model'!P{rr['nights_yoy']}", f"='Revenue Model'!P{rr['nights_yoy_Short (pitch)']}", S.pct(bq("3Q26", "nights_m", "street_mean_growth")), S.FMT_PCT, "Street bar +11.5%; a decelerating print vs 2Q26's +10.3% is the differentiated call"),
        ("3Q26 adj. EBITDA margin", "='Margins'!P{}".format(wb._margin_rows["margin"]), S.pct(short.loc["3Q26", "adj_ebitda_margin_pct"]), S.pct(lseg.loc["3Q26", "implied_margin_pct"]), S.FMT_PCT, "at or just under the 'down slightly' ceiling; the beat is dollars"),
        ("4Q26 revenue guide midpoint we expect ($m)", "='Revenue Model'!B{}".format(_find_row(wb, "Implied 4Q26 guide midpoint if the Q4 cushion holds ($m)")), "='Revenue Model'!B{}".format(_find_row(wb, "  Short case implied guide midpoint ($m)")), float(lseg.loc["4Q26", "revenue_mean"]), S.FMT_M, "team revenue / (1 + historical Q4 cushion); Street column = LSEG 4Q26 revenue mean"),
        ("  ... vs Street 4Q26 revenue", "=B{}/D{}-1".format(row + 3, row + 3), "=C{}/D{}-1".format(row + 3, row + 3), None, S.FMT_PCT, "the market prices the guide plus the cushion; a guide below the Street is the base case even on the team path"),
        ("4Q26 nights guide direction", "decelerating ('high single digits')", "decelerating ('mid single digits')", "Street 4Q26 +9.9%", "@", "management's bar has matched the Street's sign in 12 of 13 guided prints; this is a bet on the first downside miss of a nights guide"),
        ("FY26 margin sentence we expect", "approximately 36%", "at least 35.5% held (or floor at risk)", "in force: at least 35.5%", "@", "M3: November sentence = August floor + 50bp, 2 of 2; p about 0.45-0.50"),
        ("4Q26 margin that sentence implies at the run's 3Q26", 0.30125, S.pct(short.loc["4Q26", "adj_ebitda_margin_pct"]), S.pct(lseg.loc["4Q26", "implied_margin_pct"]), S.FMT_PCT, "1pp of the FY sentence = 4.49pp of 4Q26; an unchanged floor only says 4Q26 >= ~27.6%"),
    ]
    for lab, b_, c_, d_, fmt, cm in seq:
        S.write_row(ws, row, lab, [b_, c_, d_, cm], fmts=[fmt, fmt, fmt, "@"], kinds=["link" if isinstance(b_, str) and b_.startswith("=") else ("label" if fmt == "@" else "input"),
                    "link" if isinstance(c_, str) and c_.startswith("=") else ("label" if fmt == "@" else "input"), "label" if fmt == "@" else "input", "label"],
                    wrap_text=(fmt == "@"), height=(40 if fmt == "@" else None))
        ws.cell(row=row, column=5).font = S.f_note()
        ws.cell(row=row, column=5).alignment = S.Alignment(horizontal="left", vertical="top", wrap_text=False)
        for cc, fill in [(2, S.FILL_KEY), (3, S.FILL_SHORT), (4, S.FILL_STREET)]:
            ws.cell(row=row, column=cc).fill = fill
        row += 1
    row += 1

    # ---------------- Section 3: price implications
    row = S.section(ws, row, "3. What each path implies for the share price (reverse DCF run, 12-13 Sep 2026; details on the two Reverse DCF tabs)", ncols=9)
    prm = json.load(open(S.D / "reverse_dcf" / "market" / "market_implied_params.json"))
    S.write_row(ws, row, "Reference price (12 Sep 2026)", [float(prm["price"])], fmt=S.FMT_USD, bold=True); pr_row = row; row += 1
    S.write_row(ws, row, "Diluted shares (m)", [float(prm["shares"])], fmt=S.FMT_M1); sh_row = row; row += 1
    S.write_row(ws, row, "Net cash ex float ($m, 30 Jun 2026)", [float(prm["net_cash"])], fmt=S.FMT_M); nc_row = row; row += 1
    S.write_row(ws, row, "Fixed EV / FY27 EBITDA multiple used for the cross-check", [16.5], fmt=S.FMT_X); mx_row = row; row += 1
    S.write_row(ws, row, "Joint-solve multiple rule: EV / NTM EBITDA = a + b x NTM growth (%)", [float(prm["reg_a"]), float(prm["reg_b"])], fmt=S.FMT_M2, note="t 3.1, R2 0.23, about 16 independent observations; the price pays 16x for 12.9% NTM growth", note_col=4); row += 1
    row += 1
    S.header(ws, row, ["FY27 revenue ($m)", "FY27 growth", "FY27 EBITDA ($m)", "Joint-solve price", "Upside vs ref", "Price at 16.5x own EBITDA", "Upside vs ref", "P(above in 12M, options)"], first_col=2, label="Case", height=30); row += 1
    mc = Dt.read("reverse_dcf/market/market_implied_cases.csv")
    mcmp = Dt.read("reverse_dcf/market/market_implied_comparison.csv").set_index("who")
    fills = {"Street": S.FILL_STREET, "Team base": S.FILL_KEY, "Team bear": S.FILL_WARN, "Management": None}
    for _, r in mc.iterrows():
        who = [w for w in mcmp.index if w.startswith(str(r["case"])[:14])]
        rev27 = float(mcmp.loc[who[0], "fy27_revenue_musd"]) if who else None
        vals = [rev27, S.pct(r["fy27_growth"]), float(r["fy27_ebitda_own"]), float(r["price_joint"]), f"=E{row}/$B${pr_row}-1", float(r["price_fixed_own_ebitda"]), f"=G{row}/$B${pr_row}-1", float(r["p_above_12m"])]
        S.write_row(ws, row, str(r["case"]), vals, fmts=[S.FMT_M, S.FMT_PCT, S.FMT_M, S.FMT_USD, S.FMT_PCT, S.FMT_USD, S.FMT_PCT, S.FMT_PROB])
        for k, f in fills.items():
            if str(r["case"]).startswith(k) and f is not None:
                for cc in range(1, 10):
                    ws.cell(row=row, column=cc).fill = f
        row += 1
    # short case, derived
    sc_rev = float(sca.loc[("short_costs_at_budget", "FY27"), "revenue"]); sc_eb = float(sca.loc[("short_costs_at_budget", "FY27"), "adj_ebitda"])
    bear_row = row - 2; street_row = row - 4
    S.write_row(ws, row, "Short case (pitch): 15 Sep, not in the run; derived here", [sc_rev, f"=B{row}/{float(sca.loc[('short_costs_at_budget', 'FY26'), 'revenue'])}-1", sc_eb,
                f"=E{bear_row}+(B{row}-B{bear_row})/(B{street_row}-B{bear_row})*(E{street_row}-E{bear_row})", f"=E{row}/$B${pr_row}-1",
                f"=($B${mx_row}*D{row}+$B${nc_row})/$B${sh_row}", f"=G{row}/$B${pr_row}-1", None],
                fmts=[S.FMT_M, S.FMT_PCT, S.FMT_M, S.FMT_USD, S.FMT_PCT, S.FMT_USD, S.FMT_PCT, S.FMT_PROB], kinds=["input", "formula", "input", "formula", "formula", "formula", "formula", "input"])
    for cc in range(1, 10):
        ws.cell(row=row, column=cc).fill = S.FILL_SHORT
    row += 1
    row = S.text_row(ws, row, "Short-case joint-solve price is a linear interpolation between the team bear and Street rows on FY27 revenue (indicative, JUDGEMENT); the 16.5x column is the arithmetic "
                     "(multiple x own FY27 EBITDA + net cash) / shares, the same convention as the run's fixed-multiple cross-check. The joint solve is the primary lens in the run; the fixed multiple is the cross-check.",
                     wrap_cols=9, height=32)
    row += 1
    # print reaction
    S.header(ws, row, ["3Q26 nights y/y", "Accel sign vs 2Q26", "3Q26 revenue ($m)", "4Q26 revenue guide ($m)", "Guide vs Street", "Expected day-1 excess (sign rule, post-2022)", "Expected (S2 with guide term)"], first_col=2, label="Print scenario (reaction function C)", height=30); row += 1
    cs = Dt.read("reverse_dcf/C/C_scenarios.csv")
    keep = cs[cs.scenario.str.startswith(("Team base (WS", "Team base, ex-NA", "Street (Bloomberg", "Management delivered", "Q3 nowcast central", "Flat print", "Accelerating print, 4Q26 guide at Street", "Team base, UNCONDITIONAL over the nowcast band (nowcast centre 9.9"))]
    for _, r in keep.iterrows():
        nm = str(r["scenario"])
        if len(nm) > 70:
            nm = nm[:67] + "..."
        vals = [S.pct(r["nights_3q26_pct"]), None if r["accel_sign"] != r["accel_sign"] else float(r["accel_sign"]), float(r["revenue_3q26_musd"]), float(r["rev_guide_4q26_musd"]), S.pct(r["guide_vs_street_bbg_pct"]), S.pct(r["E_S1_post2022_pct"]), S.pct(r["E_S2_post2022_bbg_pct"])]
        S.write_row(ws, row, nm, vals, fmts=[S.FMT_PCT, S.FMT_M, S.FMT_M, S.FMT_M, S.FMT_PCT, S.FMT_PCT, S.FMT_PCT])
        if nm.startswith("Team base"):
            for cc in range(1, 9):
                ws.cell(row=row, column=cc).fill = S.FILL_KEY
        if nm.startswith("Street"):
            for cc in range(1, 9):
                ws.cell(row=row, column=cc).fill = S.FILL_STREET
        row += 1
    bh = Dt.read("reverse_dcf/B/B_headline.csv").set_index("item")
    S.write_row(ws, row, "Options-implied 5 Nov event standard deviation", [str(bh.loc["event_sd_central_pct", "value"]) + "%"], kind="label", note="expected absolute move " + str(bh.loc["event_exp_abs_move_central_pct", "value"]) + "%; realised print rms " + str(bh.loc["hist_realised_raw_rms_pct", "value"]) + "% raw / " + str(bh.loc["hist_realised_excess_rms_pct", "value"]) + "% excess", note_col=3); row += 1
    S.write_row(ws, row, "Nights-acceleration sign rule, post-2022 (n 14)", ["accelerating +6.0%, decelerating -5.6% day-1 excess; 0 of 8 decelerating prints positive on excess, 2 of 8 raw; Fisher p 0.007"], kind="label"); row += 1
    S.write_row(ws, row, "12-month options distribution (lognormal p25 / p50 / p75)", [float(bh.loc["p12m_lognormal_p25", "value"]), float(bh.loc["p12m_lognormal_p50", "value"]), float(bh.loc["p12m_lognormal_p75", "value"])], fmt=S.FMT_USD, note="P(above $179.5) " + str(bh.loc["p12m_above_179p5", "value"]) + "; P(below $150) " + str(bh.loc["p12m_below_150", "value"]), note_col=5); row += 1
    row += 1
    el = Dt.read("reverse_dcf/E/E_repricing_ladder.csv")
    el = el[["outcome", "ntm_revenue_musd", "ntm_growth_pct", "joint_solve_price_usd", "fundamental_repricing_pct", "accel_sign", "sign_rule_reaction_post2022_pct"]].copy()
    for c in ["ntm_growth_pct", "fundamental_repricing_pct", "sign_rule_reaction_post2022_pct"]:
        el[c] = el[c] / 100
    el.columns = ["Outcome on 5 Nov (positioning card E)", "NTM revenue ($m)", "NTM growth", "Joint-solve price", "Fundamental repricing", "Accel sign", "Sign-rule reaction"]
    row = S.table(ws, row, el, first_col=1, fmts={"NTM growth": S.FMT_PCT, "Fundamental repricing": S.FMT_PCT, "Sign-rule reaction": S.FMT_PCT, "Joint-solve price": S.FMT_USD, "NTM revenue ($m)": S.FMT_M, "Accel sign": S.FMT_INT}, header_height=30, wrap_text_cols=["Outcome on 5 Nov (positioning card E)"])
    row = S.text_row(ws, row, "Reading: the differentiated claim is the 3Q26 nights print, not FY27. The price is within 1-3% of the team's own revenue path (fundamental repricing -1 to -3%); the reaction is the sign rule "
                     "(-4 to -6% conditional on deceleration, -2 to -3.5% probability-weighted over the nowcast band) against a 9.5% options-implied dispersion. The short case adds a second leg: a 4Q26 guide "
                     "6-10% below the Street and FY27 EBITDA about $1.0bn below, which on the multiple arithmetic above is worth $20-30 a share.", wrap_cols=9, height=56)
    row += 1
    row = S.sources_block(ws, row, [
        ("Street", "data/processed/margin_build/03_consensus_pit/03_current_consensus.csv (LSEG 11 Sep 2026); reverse_dcf/E/E_street_distribution_vs_team.csv (Bloomberg)"),
        ("Team base / short", "this workbook's Income Statement, Revenue Model and Margins tabs; 40_line_build outputs"),
        ("Management delivered", "data/processed/reverse_dcf/mgmt_implied_summary.csv"),
        ("Price implications", "data/processed/reverse_dcf/market/market_implied_cases.csv, market_implied_comparison.csv, market_implied_params.json; C/C_scenarios.csv; B/B_headline.csv; E/E_repricing_ladder.csv; docs/reverse_dcf/SYNTHESIS.md"),
    ], ncols=9)
    S.freeze(ws, "B4")
    return ws


def _find_row(wb, label):
    ws = wb["Revenue Model"]
    for r in range(1, ws.max_row + 1):
        v = ws.cell(row=r, column=1).value
        if v == label:
            return r
    raise KeyError(label)
