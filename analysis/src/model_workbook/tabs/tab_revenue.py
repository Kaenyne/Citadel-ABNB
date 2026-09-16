"""'Revenue Model' tab: nights x ADR x FX x take rate -> revenue, history and the team's base path, with bear/bull/short
comparison rows, Street consensus on each KPI, and what the model implies for management's next guide."""
import style as S
import data as Dt

SHEET = "Revenue Model"
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
    S.setup(ws, "Revenue model: nights x ADR (ex-FX + FX) = GBV; GBV x take rate = revenue",
            "Base path = bridge v3 for 3Q26-4Q26 (team nights baseline PR #32, ADR card v3, FX kernel) and the WS06 v2b path for "
            "2027. Blue = source value, black = formula. Percent changes are y/y. FX shown in percentage points of y/y growth.",
            label_width=46)
    for i in range(NH + NF):
        ws.column_dimensions[qcol(i)].width = 9.5
    ws.column_dimensions[S.col(GAP)].width = 2
    for i in range(len(ANNUAL)):
        ws.column_dimensions[acol(i)].width = 11
    ws.column_dimensions[S.col(A0 + len(ANNUAL))].width = 3
    ws.column_dimensions[S.col(A0 + len(ANNUAL) + 1)].width = 70
    NOTE_COL = A0 + len(ANNUAL) + 1
    ncols = A0 + len(ANNUAL)

    labels = [q + "A" for q in Dt.HIST_Q] + [q + "E" for q in Dt.FC_Q]
    S.header(ws, HDR_ROW, labels, first_col=C0, label="Quarter")
    S.header(ws, HDR_ROW, ANNUAL, first_col=A0)

    hq = Dt.history_quarterly()
    ha = Dt.history_annual()
    base = Dt.revenue_path_wide("base")
    bear = Dt.revenue_path_wide("bear")
    bull = Dt.revenue_path_wide("bull")
    ann = Dt.read("margin_build/06_fy27_path_v2/06_annual_fy26_fy28_v2b.csv").set_index(["scenario", "period"])
    drv = Dt.read("abnb_driver_history_quarterly.csv").set_index("quarter")
    fx = Dt.fx_schedule()
    fxc = fx[fx.path == "consensus"].set_index("quarter")
    proj = Dt.bridge()["proj"]
    short_path = Dt.margin_build()["short_path"].set_index("quarter")
    sca = Dt.short_case_annual()
    rows = {}
    row = HDR_ROW + 1

    def qmap(q):  # '3Q26' -> '2026Q3'
        return f"20{q[2:]}Q{q[0]}"

    def put(key, label, hist=None, fc=None, annual=None, fmt=S.FMT_M, bold=False, indent=0, note="", kinds_fc="input"):
        nonlocal row
        vals = list(hist) if hist is not None else [None] * NH
        vals += list(fc) if fc is not None else [None] * NF
        kinds = ["input" if not (isinstance(v, str) and str(v).startswith("=")) else "formula" for v in vals]
        S.write_row(ws, row, label, vals, fmt=fmt, kinds=kinds, bold=bold, indent=indent, forecast_from=NH, note=note, note_col=NOTE_COL)
        if annual is not None:
            ak = ["input" if not (isinstance(v, str) and str(v).startswith("=")) else "formula" for v in annual]
            S.write_row(ws, row, "", annual, fmt=fmt, kinds=ak, bold=bold, first_col=A0, forecast_from=3)
            ws.cell(row=row, column=1).value = ("    " * indent) + label
        rows[key] = row
        row += 1

    def yoy(key, label, base_key, indent=1, annual=True):
        nonlocal row
        br = rows[base_key]
        vals = [None] * 4 + [f"=IFERROR({qcol(i)}{br}/{qcol(i-4)}{br}-1,\"\")" for i in range(4, NH + NF)]
        av = ([None] + [f"=IFERROR({acol(j)}{br}/{acol(j-1)}{br}-1,\"\")" for j in range(1, len(ANNUAL))]) if annual else None
        put(key, label, vals[:NH], vals[NH:], av, fmt=S.FMT_PCT, indent=indent)

    def annual_sum(r):
        h1 = f"{qcol(NH-2)}{r}:{qcol(NH-1)}{r}"; h2 = f"{qcol(NH)}{r}:{qcol(NH+1)}{r}"
        return [f"=SUM({qcol(4*j)}{r}:{qcol(4*j+3)}{r})" for j in range(3)] + [f"=SUM({h1},{h2})", f"=SUM({qcol(NH+2)}{r}:{qcol(NH+5)}{r})"]

    # ---------------- Section 1: the base build
    row = S.section(ws, row, "1. Base path: volume, price, FX and take rate", ncols=ncols,
                    note="team baseline; comparison scenarios are in section 2")
    put("nights", "Nights & seats booked (m)", [float(hq.loc[q, "nights_m"]) for q in Dt.HIST_Q],
        [float(base.loc["nights_mm", q]) for q in Dt.FC_Q], fmt=S.FMT_M1, bold=True)
    S.write_row(ws, rows["nights"], "", annual_sum(rows["nights"]), fmt=S.FMT_M1, kind="formula", first_col=A0, forecast_from=3, bold=True)
    yoy("nights_yoy", "y/y", "nights")
    # regional nights y/y (2026 only, from the bridge projection)
    reg = {"NA": "nights_yoy_na_pct", "EMEA": "nights_yoy_emea_pct", "LatAm": "nights_yoy_latam_pct", "APAC": "nights_yoy_apac_pct"}
    for name, m in reg.items():
        h = [None] * (NH - 2) + [S.pct(proj.loc[m, "q1_2026"]), S.pct(proj.loc[m, "q2_2026"])]
        f = [S.pct(proj.loc[m, "q3_adjusted"]), S.pct(proj.loc[m, "q4_adjusted"])] + [None] * 4
        put(f"reg_{name}", f"{name} nights y/y (regional build)", h, f, fmt=S.FMT_PCT, indent=2,
            note="1H26 from letters/10-Q commentary; 2H26 = WS10 regional build re-based (h2_bridge_2026_projection.csv). No regional 2027 build." if name == "NA" else "")
    row += 1
    put("adr", "ADR ($, GBV / nights)", [float(hq.loc[q, "adr_usd"]) for q in Dt.HIST_Q],
        [float(base.loc["adr_usd", q]) for q in Dt.FC_Q], fmt=S.FMT_USD, bold=True)
    S.write_row(ws, rows["adr"], "", [None, None, None, None, None], first_col=A0)
    yoy("adr_yoy", "ADR y/y reported", "adr")
    put("adr_exfx", "ADR y/y ex-FX", [None] * (NH - 4) + [S.pct(fxc.loc[qmap(q), "adr_fx_effect_actual_pp"]) and None for q in Dt.HIST_Q[-4:]],
        [S.pct(base.loc["adr_exfx_yoy_pct", q]) for q in Dt.FC_Q], fmt=S.FMT_PCT, indent=1,
        note="Forecast: ADR card v3 (3Q26 +3.9%, 4Q26 +4.1%) then the WS06 ADR build (residual + K line + geo mix + party size + LOS + seats).")
    # history ex-FX = reported - FX pts where disclosed (3Q25-2Q26)
    for i, q in enumerate(Dt.HIST_Q[-4:]):
        idx = NH - 4 + i
        ws.cell(row=rows["adr_exfx"], column=C0 + idx, value=f"={qcol(idx)}{rows['adr_yoy']}-{qcol(idx)}{rows['adr_fx']+0 if 'adr_fx' in rows else row}")
    put("adr_fx", "FX contribution to ADR y/y (pts)", [None] * (NH - 4) + [S.pct(fxc.loc[qmap(q), "adr_fx_effect_actual_pp"]) for q in Dt.HIST_Q[-4:]],
        [S.pct(base.loc["fx_pts_adr", q]) for q in Dt.FC_Q], fmt=S.FMT_PCT, indent=1,
        note="History: disclosed in the letters (3Q25-2Q26). Forecast: ADR v3 midpoint of the EUR fit and regional baskets (3Q26 -0.4pt, 4Q26 +0.2pt), then the FX kernel.")
    # fix the ex-FX history formulas now that adr_fx row is known
    for i, q in enumerate(Dt.HIST_Q[-4:]):
        idx = NH - 4 + i
        c = ws.cell(row=rows["adr_exfx"], column=C0 + idx, value=f"={qcol(idx)}{rows['adr_yoy']}-{qcol(idx)}{rows['adr_fx']}")
        c.font = S.f_formula(); c.number_format = S.FMT_PCT
    row += 1
    put("gbv", "Gross booking value ($bn)", [float(hq.loc[q, "gbv_busd"]) for q in Dt.HIST_Q],
        [f"={qcol(NH+i)}{rows['nights']}*{qcol(NH+i)}{rows['adr']}/1000" for i in range(NF)], fmt=S.FMT_M1, bold=True,
        note="Forecast GBV = nights x ADR (the 06 path carries a <0.2% identity gap to its own GBV line).")
    S.write_row(ws, rows["gbv"], "", annual_sum(rows["gbv"]), fmt=S.FMT_M1, kind="formula", first_col=A0, forecast_from=3, bold=True)
    yoy("gbv_yoy", "y/y", "gbv")
    row += 1
    put("take_py", "Take rate, prior-year quarter (%)", [None] * NH, [S.pct(base.loc["take_rate_prior_year_pct", q]) for q in Dt.FC_Q], fmt=S.FMT_PCT2, indent=1)
    put("take_chg", "Take rate change y/y (pts)", [None] * NH, [S.pct(base.loc["take_rate_change_pts", q]) for q in Dt.FC_Q], fmt=S.FMT_PCT2, indent=1,
        note="3Q26 +0.58pt: FX timing (revenue recognised at check-in on bookings made when the dollar was weaker) and the fee changes; 2027 +0.1-0.3pt.")
    put("lag_gbv", "Lagged GBV used by the bridge ($bn)", [None] * NH, [float(base.loc["lagged_gbv_busd", q]) for q in Dt.FC_Q], fmt=S.FMT_M1, indent=1,
        note="Revenue converts from bookings made earlier: the bridge kernel maps a lagged GBV mix to revenue at a seasonal conversion rate.")
    put("conv", "Conversion: revenue / lagged GBV", [None] * NH, [f"=IFERROR({qcol(NH+i)}{{REV}}/({qcol(NH+i)}{rows['lag_gbv']}*1000),\"\")" for i in range(NF)], fmt=S.FMT_PCT2, indent=1)
    put("rev", "Revenue ($m)", [float(hq.loc[q, "revenue"]) for q in Dt.HIST_Q], [float(base.loc["revenue_musd", q]) for q in Dt.FC_Q], bold=True)
    S.write_row(ws, rows["rev"], "", annual_sum(rows["rev"]), fmt=S.FMT_M, kind="formula", first_col=A0, forecast_from=3, bold=True)
    for i in range(NF):  # patch the conversion formula with the revenue row
        c = ws.cell(row=rows["conv"], column=C0 + NH + i)
        c.value = c.value.replace("{REV}", str(rows["rev"]))
    yoy("rev_yoy", "Revenue y/y reported", "rev")
    put("rev_fx", "FX contribution to revenue y/y (pts)",
        [S.pct((drv.loc[q, "yoy_growth_reported"] - drv.loc[q, "yoy_growth_constant_currency"]) * 100) if drv.loc[q, "yoy_growth_constant_currency"] == drv.loc[q, "yoy_growth_constant_currency"] else None for q in Dt.HIST_Q],
        [S.pct(base.loc["fx_pts_revenue_memo", q]) for q in Dt.FC_Q], fmt=S.FMT_PCT, indent=1,
        note="History: reported less constant-currency growth from the letters. 3Q26 = management's ~3pt after hedging; 4Q26+ = FX-lag kernel (0.98, 0.93, 0.62, 0.31, 0.38pt).")
    put("rev_exfx", "Revenue y/y ex-FX", [f"=IFERROR({qcol(i)}{rows['rev_yoy']}-{qcol(i)}{rows['rev_fx']},\"\")" for i in range(NH)],
        [f"={qcol(NH+i)}{rows['rev_yoy']}-{qcol(NH+i)}{rows['rev_fx']}" for i in range(NF)], fmt=S.FMT_PCT, indent=1)
    put("take", "Take rate printed (revenue / GBV)", [f"=IFERROR({qcol(i)}{rows['rev']}/({qcol(i)}{rows['gbv']}*1000),\"\")" for i in range(NH)],
        [f"=IFERROR({qcol(NH+i)}{rows['rev']}/({qcol(NH+i)}{rows['gbv']}*1000),\"\")" for i in range(NF)],
        [f"=IFERROR({acol(j)}{rows['rev']}/({acol(j)}{rows['gbv']}*1000),\"\")" for j in range(len(ANNUAL))], fmt=S.FMT_PCT2, indent=1, bold=True)
    put("rev_lo", "Revenue band low (conversion band)", [None] * NH, [float(base.loc["revenue_conversion_lo_musd", q]) if base.loc["revenue_conversion_lo_musd", q] == base.loc["revenue_conversion_lo_musd", q] else None for q in Dt.FC_Q], indent=1)
    put("rev_hi", "Revenue band high (conversion band)", [None] * NH, [float(base.loc["revenue_conversion_hi_musd", q]) if base.loc["revenue_conversion_hi_musd", q] == base.loc["revenue_conversion_hi_musd", q] else None for q in Dt.FC_Q], indent=1,
        note="Conversion min/max over the fitted years; it is not the nights band (section 2 has that).")
    row += 1

    # ---------------- Section 2: scenarios
    row = S.section(ws, row, "2. Revenue scenarios: nights, ADR and revenue by case", ncols=ncols,
                    note="bear/bull = WS06 v2b on the bridge v3 bands; Short = the pitch case (lap + RNPL cancellations)")
    fills = {"Bear": S.FILL_WARN, "Base": S.FILL_KEY, "Bull": None, "Short (pitch)": S.FILL_SHORT}
    cases = {"Bear": bear, "Base": base, "Bull": bull}
    for metric, line, fmt, lab in [("nights_yoy", "nights_yoy_pct", S.FMT_PCT, "Nights y/y"), ("adr_rep", "adr_reported_yoy_pct", S.FMT_PCT, "ADR y/y reported"),
                                   ("rev", "revenue_musd", S.FMT_M, "Revenue ($m)"), ("rev_yoy", "revenue_yoy_pct", S.FMT_PCT, "Revenue y/y")]:
        for cname, w in cases.items():
            conv = S.pct if fmt == S.FMT_PCT else float
            fc = [conv(w.loc[line, q]) for q in Dt.FC_Q]
            a = None
            sc = {"Bear": "bear", "Base": "base", "Bull": "bull"}[cname]
            if metric == "rev":
                a = [None, None, None, float(ann.loc[(sc, "FY26"), "revenue_musd"]), float(ann.loc[(sc, "FY27"), "revenue_musd"])]
            elif metric == "rev_yoy":
                a = [None, None, None, S.pct(ann.loc[(sc, "FY26"), "revenue_musd_yoy_pct"]), S.pct(ann.loc[(sc, "FY27"), "revenue_musd_yoy_pct"])]
            elif metric == "nights_yoy":
                a = [None, None, None, S.pct(ann.loc[(sc, "FY26"), "nights_mm_yoy_pct"]), S.pct(ann.loc[(sc, "FY27"), "nights_mm_yoy_pct"])]
            elif metric == "adr_rep":
                a = [None, None, None, S.pct(ann.loc[(sc, "FY26"), "adr_usd_yoy_pct"]), S.pct(ann.loc[(sc, "FY27"), "adr_usd_yoy_pct"])]
            put(f"{metric}_{cname}", f"{lab}: {cname}", [None] * NH, fc, a, fmt=fmt, indent=1)
            if fills[cname] is not None:
                for cc in range(C0 + NH, C0 + NH + NF):
                    ws.cell(row=rows[f"{metric}_{cname}"], column=cc).fill = fills[cname]
        # short
        if metric == "nights_yoy":
            fc = [S.pct(short_path.loc[q, "nights_yoy_pct"]) for q in Dt.FC_Q]; a = None
        elif metric == "adr_rep":
            fc = [S.pct(short_path.loc[q, "adr_reported_yoy_pct"]) for q in Dt.FC_Q]; a = None
        elif metric == "rev":
            fc = [float(short_path.loc[q, "revenue_musd"]) for q in Dt.FC_Q]
            a = [None, None, None, float(sca.loc[("short_costs_at_budget", "FY26"), "revenue"]), float(sca.loc[("short_costs_at_budget", "FY27"), "revenue"])]
        else:
            fc = [f"=IFERROR({qcol(NH+i)}{rows['rev_Short (pitch)']}/{qcol(NH+i-4)}{rows['rev']}-1,\"\")" for i in range(NF)]
            a = [None, None, None, f"={acol(3)}{rows['rev_Short (pitch)']}/{acol(2)}{rows['rev']}-1", f"={acol(4)}{rows['rev_Short (pitch)']}/{acol(3)}{rows['rev_Short (pitch)']}-1"]
        put(f"{metric}_Short (pitch)", f"{lab}: Short (pitch)", [None] * NH, fc, a, fmt=fmt, indent=1,
            note=("Short: nights +8.5% in 3Q26 (guide low; July still has the World Cup) then +5/+4/+2/+3/+4% as the 4Q25-1Q26 bundle and World Cup lap and RNPL cancellations land; ADR ex-FX +2.5% then flat." if metric == "nights_yoy" else ""))
        for cc in range(C0 + NH, C0 + NH + NF):
            ws.cell(row=rows[f"{metric}_Short (pitch)"], column=cc).fill = S.FILL_SHORT
        row += 1
    # nights lap scenarios table (bridge)
    row = S.section(ws, row, "2b. Nights lap arithmetic for 2H26 (bridge v3 scenarios)", ncols=ncols)
    nl = Dt.bridge()["nights"][["scenario", "nights_q3", "nights_q4", "gbv_q3", "gbv_q4", "q3_vs_guide", "q3_accel_vs_2q26", "q4_accel_vs_q3"]].copy()
    for c in ["nights_q3", "nights_q4", "gbv_q3", "gbv_q4"]:
        nl[c] = nl[c] / 100
    nl.columns = ["Scenario", "3Q26 nights y/y", "4Q26 nights y/y", "3Q26 GBV y/y", "4Q26 GBV y/y", "3Q26 vs guide (10-12%)", "3Q26 accel vs 2Q26 (pts)", "4Q26 accel vs 3Q26 (pts)"]
    row = S.table(ws, row, nl, first_col=1, fmts={"3Q26 nights y/y": S.FMT_PCT, "4Q26 nights y/y": S.FMT_PCT, "3Q26 GBV y/y": S.FMT_PCT, "4Q26 GBV y/y": S.FMT_PCT,
                                                 "3Q26 accel vs 2Q26 (pts)": S.FMT_M2, "4Q26 accel vs 3Q26 (pts)": S.FMT_M2}, header_height=32)
    row = S.text_row(ws, row, "2Q26 printed nights +10.3%; management guided 3Q26 'low double digits'. The team baseline (+9.9%) sits below the guide and decelerates; "
                     "the 4Q26 case B applies the RNPL/bundle lap to ex-NA nights at a 45% split. The 2027 nights build (06_nights_build.csv) carries NA +2.3% and ex-NA +10-11% "
                     "pre-lap, less 0.74pt fee-cancellation lap and 0.36-0.91pt RNPL lap, for +6.0-8.2% total.", wrap_cols=12, height=42)
    row += 1

    # ---------------- Section 3: Street on the KPIs
    row = S.section(ws, row, "3. Street consensus on the KPIs, and where the team sits", ncols=ncols,
                    note="Bloomberg estimate distribution (pull 5-12 Sep 2026) for 3Q26/4Q26; LSEG revenue means 11 Sep 2026 for 3Q26-FY28")
    bbg = Dt.consensus()["bbg"].copy()
    lab = {"nights_m": "Nights (m)", "gbv_musd": "GBV ($m)", "adr_usd": "ADR ($)", "take_rate_pct": "Take rate (%)", "revenue_musd": "Revenue ($m)", "eps_usd": "EPS ($)"}
    t = bbg[["quarter", "metric", "n_estimates", "street_low", "street_mean", "street_high", "prior_year_actual", "street_mean_growth", "team_value", "team_growth", "team_position"]].copy()
    t["metric"] = t["metric"].map(lab)
    t["street_mean_growth"] = t["street_mean_growth"] / 100
    t["team_growth"] = t["team_growth"] / 100
    t.columns = ["Quarter", "Metric", "n", "Street low", "Street mean", "Street high", "Prior-year actual", "Street mean y/y", "Team value", "Team y/y", "Team position in the range"]
    row = S.table(ws, row, t, first_col=1, fmts={"Street mean y/y": S.FMT_PCT, "Team y/y": S.FMT_PCT, "n": S.FMT_INT}, header_height=32,
                  row_fill_col="Team position in the range", row_fills={"below the lowest estimate": S.FILL_WARN})
    row = S.text_row(ws, row, "Team values in this Bloomberg comparison are the reverse-DCF run's snapshot (12 Sep): 3Q26 nights 146.8m / +9.9% and revenue $4,771m; the live bridge v3 "
                     "revenue is $4,804m (section 1). The point that matters: every one of the 28 Street nights estimates for 3Q26 is at or above 2Q26's growth rate; the team's is below the lowest.",
                     wrap_cols=12, height=36)
    row += 1
    cons = Dt.consensus()
    vs = cons["vs"]; lseg = cons["lseg"]
    per_map = {q: f"20{q[2:]}Q{q[0]}" for q in Dt.FC_Q}
    put("street_rev", "Revenue: Street (LSEG mean)", [None] * NH, [float(vs.loc[per_map[q], "lseg_revenue_musd"]) for q in Dt.FC_Q],
        [None, None, None, float(lseg.loc["FY26", "revenue_mean"]), float(lseg.loc["FY27", "revenue_mean"])], bold=True)
    for cc in list(range(C0 + NH, C0 + NH + NF)) + [A0 + 3, A0 + 4]:
        ws.cell(row=rows["street_rev"], column=cc).fill = S.FILL_STREET
    put("street_n", "  n estimates", [None] * NH, [float(vs.loc[per_map[q], "lseg_n"]) for q in Dt.FC_Q], [None, None, None, float(lseg.loc["FY26", "revenue_n"]), float(lseg.loc["FY27", "revenue_n"])], fmt=S.FMT_INT, indent=1)
    put("street_sd", "  sd of estimates ($m)", [None] * NH, [float(vs.loc[per_map[q], "lseg_revenue_sd_musd"]) for q in Dt.FC_Q], [None, None, None, float(lseg.loc["FY26", "revenue_sd"]), float(lseg.loc["FY27", "revenue_sd"])], fmt=S.FMT_M1, indent=1)
    put("gap_base", "Team base vs Street (%)", [None] * NH, [f"={qcol(NH+i)}{rows['rev']}/{qcol(NH+i)}{rows['street_rev']}-1" for i in range(NF)],
        [None, None, None, f"={acol(3)}{rows['rev']}/{acol(3)}{rows['street_rev']}-1", f"={acol(4)}{rows['rev']}/{acol(4)}{rows['street_rev']}-1"], fmt=S.FMT_PCT, indent=1)
    put("gap_short", "Short case vs Street (%)", [None] * NH, [f"={qcol(NH+i)}{rows['rev_Short (pitch)']}/{qcol(NH+i)}{rows['street_rev']}-1" for i in range(NF)],
        [None, None, None, f"={acol(3)}{rows['rev_Short (pitch)']}/{acol(3)}{rows['street_rev']}-1", f"={acol(4)}{rows['rev_Short (pitch)']}/{acol(4)}{rows['street_rev']}-1"], fmt=S.FMT_PCT, indent=1)
    put("gap_sd", "Team base gap in Street sd's", [None] * NH, [f"=IFERROR(({qcol(NH+i)}{rows['rev']}-{qcol(NH+i)}{rows['street_rev']})/{qcol(NH+i)}{rows['street_sd']},\"\")" for i in range(NF)],
        [None, None, None, f"=({acol(3)}{rows['rev']}-{acol(3)}{rows['street_rev']})/{acol(3)}{rows['street_sd']}", f"=({acol(4)}{rows['rev']}-{acol(4)}{rows['street_rev']})/{acol(4)}{rows['street_sd']}"], fmt=S.FMT_M2, indent=1)
    row += 1

    # ---------------- Section 4: management guidance
    row = S.section(ws, row, "4. Management guidance: the 3Q26 guide in force, and what the model implies for the 5 Nov 4Q26 guide", ncols=ncols)
    S.header(ws, row, ["Guide text (6 Aug 2026 letter)", "Guide low", "Guide high", "Guide mid", "Team base", "Base vs mid", "Short case", "Short vs mid", "Street"], first_col=2, label="3Q26 item", height=30)
    row += 1
    g = proj
    rev3 = Dt.bridge()["rev"].loc["3Q26"]
    items = [
        ("Revenue ($m)", "$4.69-4.77bn, +15-17% incl. ~3pt FX", float(rev3["guide_low"]), float(rev3["guide_high"]), float(base.loc["revenue_musd", "3Q26"]), float(short_path.loc["3Q26", "revenue_musd"]), float(lseg.loc["3Q26", "revenue_mean"]), S.FMT_M),
        ("Nights & seats y/y", str(g.loc["nights_yoy_pct", "q3_guide_text"]), S.pct(g.loc["nights_yoy_pct", "q3_guide_low"]), S.pct(g.loc["nights_yoy_pct", "q3_guide_high"]), S.pct(base.loc["nights_yoy_pct", "3Q26"]), S.pct(short_path.loc["3Q26", "nights_yoy_pct"]), S.pct(bbg.query("quarter=='3Q26' and metric=='nights_m'").street_mean_growth.iloc[0]), S.FMT_PCT),
        ("GBV y/y", str(g.loc["gbv_yoy_reported_pct", "q3_guide_text"]), S.pct(g.loc["gbv_yoy_reported_pct", "q3_guide_low"]), S.pct(g.loc["gbv_yoy_reported_pct", "q3_guide_high"]), S.pct(base.loc["gbv_yoy_pct", "3Q26"]), None, S.pct(bbg.query("quarter=='3Q26' and metric=='gbv_musd'").street_mean_growth.iloc[0]), S.FMT_PCT),
        ("FX pts on revenue", str(g.loc["fx_pts_revenue", "q3_guide_text"]), S.pct(g.loc["fx_pts_revenue", "q3_guide_low"]), S.pct(g.loc["fx_pts_revenue", "q3_guide_high"]), S.pct(base.loc["fx_pts_revenue_memo", "3Q26"]), S.pct(base.loc["fx_pts_revenue_memo", "3Q26"]), None, S.FMT_PCT),
        ("Take rate", str(g.loc["take_rate_pct", "q3_guide_text"]), S.pct(g.loc["take_rate_pct", "q3_guide_low"]), S.pct(g.loc["take_rate_pct", "q3_guide_high"]), S.pct(base.loc["take_rate_printed_pct", "3Q26"]), None, S.pct(bbg.query("quarter=='3Q26' and metric=='take_rate_pct'").street_mean.iloc[0]), S.FMT_PCT2),
        ("Adj. EBITDA margin", str(g.loc["adj_ebitda_margin_pct", "q3_guide_text"]), S.pct(g.loc["adj_ebitda_margin_pct", "q3_guide_low"]), S.pct(g.loc["adj_ebitda_margin_pct", "q3_guide_high"]), None, None, S.pct(lseg.loc["3Q26", "implied_margin_pct"]), S.FMT_PCT),
    ]
    for lab_, text, lo, hi, tb, sh, st, fmt in items:
        ws.cell(row=row, column=1, value=lab_).font = S.f_label()
        ws.cell(row=row, column=2, value=text).font = S.f_note()
        vals = [lo, hi, f"=AVERAGE(C{row}:D{row})" if lo is not None else None, tb, (f"=F{row}/E{row}-1" if (tb is not None and lo is not None and fmt == S.FMT_M) else (f"=F{row}-E{row}" if (tb is not None and lo is not None) else None)),
                sh, (f"=H{row}/E{row}-1" if (sh is not None and lo is not None and fmt == S.FMT_M) else (f"=H{row}-E{row}" if (sh is not None and lo is not None) else None)), st]
        fm = [fmt, fmt, fmt, fmt, S.FMT_PCT if fmt == S.FMT_M else S.FMT_PCT2, fmt, S.FMT_PCT if fmt == S.FMT_M else S.FMT_PCT2, fmt]
        S.write_row(ws, row, lab_, vals, first_col=3, fmts=fm)
        ws.cell(row=row, column=2, value=text).font = S.f_note()
        row += 1
    row = S.text_row(ws, row, "Margin margin-sentence rows are on the Margins tab (3Q26 'down slightly' vs 3Q25's 50.1%; FY26 'at least 35.5%'). "
                     "The team base sits above the 3Q26 revenue guide's top end (as the last 19 prints did, mean +2.5% vs the midpoint), and below its nights guide.", wrap_cols=12, height=30)
    row += 1
    # what we expect the 4Q26 guide to look like
    S.header(ws, row, ["4Q26", "How it is derived"], first_col=2, label="Expected 4Q26 guide (given 5 Nov)", height=18)
    ws.column_dimensions["C"].width = 9.5
    row += 1
    gh = Dt.bridge()["guide_hist"]
    q4h = gh[gh.guided_quarter.str.endswith("Q4") & gh.actual_musd.notna()]
    cushion_q4 = float(q4h.actual_vs_mid_pct.mean()) / 100
    cushion_all = float(gh.actual_vs_mid_pct.dropna().mean()) / 100
    width = float(gh.range_width_pct_of_mid.tail(6).mean()) / 100
    r0 = row
    S.write_row(ws, row, "Historical Q4 actual vs guide midpoint (mean, 4 Q4 guides)", [cushion_q4], fmt=S.FMT_PCT, note="abnb_revenue_guidance_vs_actual.csv: 4Q22 +3.4%, 4Q23 +3.2%, 4Q24 +2.7%, 4Q25 +3.3%", note_col=3); row += 1
    S.write_row(ws, row, "Historical actual vs midpoint, all 19 guided quarters (mean)", [cushion_all], fmt=S.FMT_PCT, note="every print since 4Q21 landed above the midpoint; 15 of 19 above the top end", note_col=3); row += 1
    S.write_row(ws, row, "Guide range width, % of midpoint (mean of the last 6)", [width], fmt=S.FMT_PCT, note_col=3); row += 1
    S.write_row(ws, row, "Team base 4Q26 revenue ($m)", [f"={qcol(NH+1)}{rows['rev']}"], kind="link", note="bridge v3", note_col=3); row += 1
    S.write_row(ws, row, "Implied 4Q26 guide midpoint if the Q4 cushion holds ($m)", [f"=B{row-1}/(1+B{r0})"], bold=True, note="team base / (1 + historical Q4 cushion). Bridge v3 quotes $3,059m on the same arithmetic.", note_col=3); row += 1
    S.write_row(ws, row, "  Implied guide range ($m, low / high)", [f"=B{row-1}*(1-B{r0+2}/2)", f"=B{row-1}*(1+B{r0+2}/2)"], note_col=4); row += 1
    S.write_row(ws, row, "  Implied guide midpoint y/y", [f"=B{row-2}/{qcol(NH-3)}{rows['rev']}-1"], fmt=S.FMT_PCT, note="vs 4Q25 actual $2,778m", note_col=3); row += 1
    S.write_row(ws, row, "Street 4Q26 revenue (LSEG mean)", [f"={qcol(NH+1)}{rows['street_rev']}"], kind="link", note_col=3); row += 1
    S.write_row(ws, row, "  Implied guide midpoint vs Street (%)", [f"=B{row-4}/B{row-1}-1"], fmt=S.FMT_PCT, bold=True, note="a guide midpoint below the Street is the base case even on the team's own path: the market prices the guide plus the cushion", note_col=3); row += 1
    rs = row
    S.write_row(ws, row, "Short case 4Q26 revenue ($m)", [f"={qcol(NH+1)}{rows['rev_Short (pitch)']}"], kind="link", note_col=3); row += 1
    S.write_row(ws, row, "  Short case implied guide midpoint ($m)", [f"=B{rs}/(1+B{r0})"], bold=True, note_col=3); row += 1
    S.write_row(ws, row, "  Short case implied guide midpoint vs Street (%)", [f"=B{row-1}/B{rs-2}-1"], fmt=S.FMT_PCT, bold=True, note="the pitch's 5 Nov sequence: a Q3 print near the sentence, a Q4 guide well below the Street", note_col=3); row += 1
    S.write_row(ws, row, "Nights guide direction for 4Q26 (expected wording)", ["decelerating vs 3Q26 print; 'high single digits' on the base path, 'mid single digits' on the short path"], kind="label", note_col=3); row += 1
    S.write_row(ws, row, "FX in the 4Q26 revenue guide (pts)", [S.pct(base.loc["fx_pts_revenue_memo", "4Q26"])], fmt=S.FMT_PCT, note="kernel: about +1pt; management's own sentence has been the hedged number", note_col=3); row += 1
    S.write_row(ws, row, "Take rate wording", ["'in line' y/y (4Q25 13.6%); team 13.8%"], kind="label", note_col=3); row += 1
    row += 1
    # guide history table
    row = S.section(ws, row, "4b. Revenue guide history: every quarterly guide since 4Q21 and how the print landed", ncols=ncols)
    ghd = gh.copy()
    for c in ["range_width_pct_of_mid", "actual_vs_mid_pct", "actual_vs_high_pct"]:
        ghd[c] = ghd[c] / 100
    ghd.columns = ["Guided quarter", "Issued on call", "Guide low", "Guide high", "Guide mid", "Range width % of mid", "Actual", "Actual vs mid", "Actual vs high"]
    row = S.table(ws, row, ghd, first_col=1, fmts={"Range width % of mid": S.FMT_PCT, "Actual vs mid": S.FMT_PCT, "Actual vs high": S.FMT_PCT, "Guide low": S.FMT_M, "Guide high": S.FMT_M, "Guide mid": S.FMT_M, "Actual": S.FMT_M}, header_height=30)
    row += 1
    row = S.sources_block(ws, row, [
        ("History KPIs and revenue", "data/processed/abnb_driver_history_quarterly.csv; margin_build/02_financial_panel/02_panel_quarterly.csv"),
        ("Base / bear / bull path 3Q26-4Q28 (nights, ADR, FX, take rate, revenue)", "data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv, 06_annual_fy26_fy28_v2b.csv, 06_nights_build.csv, 06_adr_build.csv"),
        ("Bridge v3 (2H26 lines, FX, nights scenarios, revenue dollars, 3Q26 guide)", "data/processed/h2_bridge_v3/*.csv; docs/thesis-kernel-topdown; PR #52"),
        ("Regional nights 2026", "data/processed/h2_bridge_v3/h2_bridge_2026_projection.csv (WS10 regional build)"),
        ("FX history and kernel", "data/processed/overnight/05_fx_schedule.csv; h2_bridge_v3/h2_bridge_v3_fx_line.csv"),
        ("Short case path", "data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv; docs/margin-build/notes/40_line_build.md"),
        ("Street KPIs", "data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv (Bloomberg); margin_build/03_consensus_pit/03_current_consensus.csv and 23_final_model/23_vs_consensus.csv (LSEG)"),
        ("Guide history", "data/processed/abnb_revenue_guidance_vs_actual.csv"),
    ], ncols=ncols)
    S.freeze(ws, f"B{HDR_ROW+1}")
    wb._rev_rows = rows
    return ws
