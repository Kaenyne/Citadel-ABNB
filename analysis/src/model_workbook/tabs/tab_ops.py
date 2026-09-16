"""'Operating Schedules' tab: volume and unit economics, regional revenue, the 2027 nights and ADR builds, FX paths,
unit-cost drivers, below-EBITDA items and the full parameter sheet of the line build."""
import style as S
import data as Dt

SHEET = "Operating Schedules"
HDR_ROW = 5
C0 = 2
NH = len(Dt.HIST_Q)
NF = len(Dt.FC_Q)
NOTE_COL = C0 + NH + NF + 1


def qcol(i):
    return S.col(C0 + i)


def build(wb):
    ws = wb.create_sheet(SHEET)
    rng = wb._scen_ranges
    S.setup(ws, "Operating schedules: volume, unit economics, regional mix, the 2027 nights and ADR builds, FX, below-EBITDA items, parameters",
            "Forecast columns follow the scenario dropdown on the Income Statement tab where the line exists per scenario (green links); "
            "builds that exist only for the base path are shown as blue source values.", label_width=48)
    for i in range(NH + NF):
        ws.column_dimensions[qcol(i)].width = 9.5
    ws.column_dimensions[S.col(NOTE_COL)].width = 70
    KEY = "'Income Statement'!$G$3"
    labels = [q + "A" for q in Dt.HIST_Q] + [q + "E" for q in Dt.FC_Q]
    S.header(ws, HDR_ROW, labels, first_col=C0, label="Quarter")
    for i, q in enumerate(Dt.ALL_Q):
        ws.cell(row=4, column=C0 + i, value=q).font = S.f_note()
    ncols = C0 + NH + NF
    hq = Dt.history_quarterly()
    rows = {}
    row = HDR_ROW + 1

    def fc(line_key, i):
        return f'=INDEX({rng["data"]},MATCH({KEY}&"|{line_key}",{rng["keys"]},0),MATCH({qcol(NH+i)}$4,{rng["qhdr"]},0))'

    def put(key, label, hist=None, line_key=None, fc_vals=None, fmt=S.FMT_M, bold=False, indent=0, note=""):
        nonlocal row
        vals = list(hist) if hist is not None else [None] * NH
        kinds = ["formula" if isinstance(v, str) else "input" for v in vals]
        for i in range(NF):
            if fc_vals is not None:
                vals.append(fc_vals[i]); kinds.append("formula" if isinstance(fc_vals[i], str) else "input")
            elif line_key:
                vals.append(fc(line_key, i)); kinds.append("link")
            else:
                vals.append(None); kinds.append("input")
        S.write_row(ws, row, label, vals, fmt=fmt, kinds=kinds, bold=bold, indent=indent, forecast_from=NH, note=note, note_col=NOTE_COL)
        rows[key] = row; row += 1

    # ---- A. volume
    row = S.section(ws, row, "A. Volume and unit economics", ncols=ncols)
    put("nights", "Nights & seats booked (m)", [float(hq.loc[q, "nights_m"]) for q in Dt.HIST_Q], "nights_m", fmt=S.FMT_M1, bold=True)
    put("bookings", "Bookings (m)", None, "bookings_m", fmt=S.FMT_M1, note="nights / nights per booking (3.65 in 2026, 3.60 in 2027, continuing 3.9 / 3.8 / 3.7)")
    put("npb", "Nights per booking", None, None, fc_vals=[f"=IFERROR({qcol(NH+i)}{rows['nights']}/{qcol(NH+i)}{rows['bookings']},\"\")" for i in range(NF)], fmt=S.FMT_M2, indent=1)
    put("gbv", "Gross booking value ($bn)", [float(hq.loc[q, "gbv_busd"]) for q in Dt.HIST_Q], "gbv_busd", fmt=S.FMT_M1, bold=True)
    put("adr", "ADR ($)", [float(hq.loc[q, "adr_usd"]) for q in Dt.HIST_Q], None, fc_vals=[f"=IFERROR({qcol(NH+i)}{rows['gbv']}*1000/{qcol(NH+i)}{rows['nights']},\"\")" for i in range(NF)], fmt=S.FMT_USD)
    put("rev", "Revenue ($m)", [float(hq.loc[q, "revenue"]) for q in Dt.HIST_Q], "revenue", bold=True)
    put("rpn", "Revenue per night ($)", [f"={qcol(i)}{rows['rev']}/{qcol(i)}{rows['nights']}" for i in range(NH)], None, fc_vals=[f"={qcol(NH+i)}{rows['rev']}/{qcol(NH+i)}{rows['nights']}" for i in range(NF)], fmt=S.FMT_USD, indent=1)
    put("take", "Take rate (revenue / GBV)", [f"={qcol(i)}{rows['rev']}/({qcol(i)}{rows['gbv']}*1000)" for i in range(NH)], None, fc_vals=[f"={qcol(NH+i)}{rows['rev']}/({qcol(NH+i)}{rows['gbv']}*1000)" for i in range(NF)], fmt=S.FMT_PCT2, indent=1)
    put("ccpn", "Cash cost per night ($)", [f"={float(hq.loc[q, 'total_cash_costs'])}/{qcol(i)}{rows['nights']}" for i, q in enumerate(Dt.HIST_Q)], None,
        fc_vals=[f"=INDEX({rng['data']},MATCH({KEY}&\"|total_cash_costs\",{rng['keys']},0),MATCH({qcol(NH+i)}$4,{rng['qhdr']},0))/{qcol(NH+i)}{rows['nights']}" for i in range(NF)], fmt=S.FMT_USD, indent=1)
    row += 1

    # ---- B. regional revenue
    row = S.section(ws, row, "B. Revenue by region (10-Q geographic split; Q4 derived from the 10-K)", ncols=ncols)
    reg = Dt.read("airbnb_regional_revenue_quarterly.csv").set_index("quarter")
    qm = {q: f"20{q[2:]}Q{q[0]}" for q in Dt.HIST_Q}
    for col_, lab in [("north_america_usd_m", "North America"), ("emea_usd_m", "EMEA"), ("latam_usd_m", "Latin America"), ("apac_usd_m", "Asia Pacific")]:
        put(f"reg_{col_}", f"{lab} ($m)", [float(reg.loc[qm[q], col_]) if qm[q] in reg.index else None for q in Dt.HIST_Q], None, indent=1)
    for col_, lab in [("north_america_usd_m", "North America"), ("emea_usd_m", "EMEA"), ("latam_usd_m", "Latin America"), ("apac_usd_m", "Asia Pacific")]:
        r_ = rows[f"reg_{col_}"]
        put(f"sh_{col_}", f"{lab} share of revenue", [f"=IFERROR({qcol(i)}{r_}/{qcol(i)}{rows['rev']},\"\")" for i in range(NH)], None, fmt=S.FMT_PCT, indent=1)
    for col_, lab in [("north_america_usd_m", "North America"), ("emea_usd_m", "EMEA"), ("latam_usd_m", "Latin America"), ("apac_usd_m", "Asia Pacific")]:
        r_ = rows[f"reg_{col_}"]
        put(f"yy_{col_}", f"{lab} revenue y/y", [None] * 4 + [f"=IFERROR({qcol(i)}{r_}/{qcol(i-4)}{r_}-1,\"\")" for i in range(4, NH)], None, fmt=S.FMT_PCT, indent=1)
    row = S.text_row(ws, row, "Regional nights growth used by the 2026 build (WS10, re-based): NA +8% in 1H26 and +11% in 2H26; EMEA +5/+8/+6.5/+9.5%; LatAm +18-20%; APAC +14-18%. The pitch's lap thesis is NA-centred: "
                     "the 4Q25-1Q26 bundle and the June-July World Cup flattered 1H26 NA nights. Revenue Model tab section 1 has the quarterly rows.", wrap_cols=12, height=32)
    row += 1

    # ---- C. 2027 nights build
    row = S.section(ws, row, "C. The 2027 nights build (WS06 v2b, base): NA plus ex-NA less the laps", ncols=ncols)
    nb = Dt.read("margin_build/06_fy27_path_v2/06_nights_build.csv")
    nbb = nb[nb.scenario == "base"].set_index("quarter")
    q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]
    off = NH + 2  # 1Q27 column index
    def nrow(key, label, col_, fmt=S.FMT_PCT, scale=100.0, note=""):
        put(key, label, None, None, fc_vals=[None, None] + [float(nbb.loc[q, col_]) / scale for q in q27], fmt=fmt, indent=1, note=note)
    nrow("na_sh", "NA share of prior-year nights", "na_share_prior_year", scale=1.0)
    nrow("na_yoy", "NA nights y/y", "na_yoy_pct", note="PR #32 three-feature lap: NA +2.3% base (bear +1.3%, bull +4.7%)")
    nrow("exna", "Ex-NA nights y/y, pre-lap (WS10)", "exna_ws10_prelap_yoy_pct")
    nrow("na_c", "NA contribution (pts)", "na_contribution_pts", fmt=S.FMT_PCT2)
    nrow("exna_c", "Ex-NA contribution pre-lap (pts)", "exna_contribution_prelap_pts", fmt=S.FMT_PCT2)
    nrow("lap_fee", "Ex-NA fee-cancellation lap (pts)", "exna_lap_fee_cancel_pts", fmt=S.FMT_PCT2)
    nrow("lap_rnpl", "Ex-NA RNPL lap (pts)", "exna_lap_rnpl_pts", fmt=S.FMT_PCT2)
    nrow("event", "Events (World Cup lap etc., pts)", "event_pts", fmt=S.FMT_PCT2)
    nrow("tot", "Total nights y/y (base)", "total_nights_yoy_pct", note="= NA contribution + ex-NA contribution + laps + events")
    for cc in range(C0 + off, C0 + NH + NF):
        ws.cell(row=rows["tot"], column=cc).fill = S.FILL_KEY
    row += 1

    # ---- D. 2027 ADR build
    row = S.section(ws, row, "D. The 2027 ADR build (WS06 v2b, base): ex-FX terms then FX", ncols=ncols)
    ab = Dt.read("margin_build/06_fy27_path_v2/06_adr_build.csv")
    abb = ab[ab.scenario == "base"].set_index("quarter")
    def arow(key, label, col_, fmt=S.FMT_PCT2, note=""):
        put(key, label, None, None, fc_vals=[None, None] + [float(abb.loc[q, col_]) / 100 for q in q27], fmt=fmt, indent=1, note=note)
    arow("res", "Pricing residual (pts)", "residual_pp", note="the unobserved same-listing price term; ADR v3 rule = last quarter's residual, decaying")
    arow("k", "K mechanics line (pts)", "k_line_pp", note="fee-structure mechanics from ADR v3 workstream K")
    arow("geo", "Geographic mix (pts)", "geo_mix_pp", note="faster growth in lower-ADR regions (LatAm/APAC) dilutes ADR")
    arow("party", "Party size (pts)", "party_size_pp")
    arow("los", "Length of stay (pts)", "los_pp")
    arow("seats", "New-business seats dilution (pts)", "new_business_seats_pp", note="Services/Experiences seats are counted in 'nights & seats' at a lower price")
    arow("inter", "Interaction (pts)", "interaction_pp")
    arow("exfx", "ADR y/y ex-FX", "adr_exfx_yoy_pct", fmt=S.FMT_PCT)
    arow("fx", "FX on ADR (pts, kernel)", "fx_pts_adr", fmt=S.FMT_PCT2)
    arow("rep", "ADR y/y reported", "adr_reported_yoy_pct", fmt=S.FMT_PCT)
    for cc in range(C0 + off, C0 + NH + NF):
        ws.cell(row=rows["rep"], column=cc).fill = S.FILL_KEY
    row += 1

    # ---- E. FX paths
    row = S.section(ws, row, "E. FX: EUR/USD paths and the fitted effects on ADR and revenue (WS05 kernel; three USD paths)", ncols=ncols)
    fx = Dt.fx_schedule()
    qmap = {q: f"20{q[2:]}Q{q[0]}" for q in Dt.ALL_Q}
    for path, lab in [("consensus", "Consensus FX path"), ("strong_usd", "Strong-USD path"), ("weak_usd", "Weak-USD path")]:
        f = fx[fx.path == path].set_index("quarter")
        def g(q, c):
            k = qmap[q]
            return float(f.loc[k, c]) if k in f.index and f.loc[k, c] == f.loc[k, c] else None
        put(f"{path}_eur", f"{lab}: EUR/USD average", [g(q, "eurusd_level") for q in Dt.HIST_Q], None, fc_vals=[g(q, "eurusd_level") for q in Dt.FC_Q], fmt=S.FMT_M2, indent=1, bold=True)
        put(f"{path}_eury", "  EUR/USD y/y", [S.pct(g(q, "eurusd_yoy_pct")) for q in Dt.HIST_Q], None, fc_vals=[S.pct(g(q, "eurusd_yoy_pct")) for q in Dt.FC_Q], fmt=S.FMT_PCT, indent=2)
        put(f"{path}_adr", "  FX effect on ADR (pts): fit (EUR) / actual where disclosed", [S.pct(g(q, "adr_fx_effect_actual_pp")) for q in Dt.HIST_Q], None, fc_vals=[S.pct(g(q, "adr_fx_effect_fit_eur_pp")) for q in Dt.FC_Q], fmt=S.FMT_PCT2, indent=2)
        put(f"{path}_rev", "  FX effect on revenue (pts): lagged fit / actual where disclosed", [S.pct(g(q, "revenue_fx_actual_pp")) for q in Dt.HIST_Q], None, fc_vals=[S.pct(g(q, "revenue_fx_fit_pp")) for q in Dt.FC_Q], fmt=S.FMT_PCT2, indent=2)
    row = S.text_row(ws, row, "Revenue FX lags ADR FX because revenue is recognised at check-in on bookings made one to two quarters earlier (fit: -0.64 + 0.41 x mean EUR/USD y/y at t-1, t-2; n 17, r 0.80). "
                     "The base path in the Revenue Model uses management's ~3pt for 3Q26 and the kernel thereafter (+1.0, +0.9, +0.6, +0.3, +0.4pt); ADR FX uses the ADR v3 midpoint (EUR fit and regional baskets).", wrap_cols=12, height=32)
    row += 1

    # ---- F. unit-cost drivers
    row = S.section(ws, row, "F. Unit-cost drivers (follow the scenario dropdown)", ncols=ncols)
    put("fee_rate", "Merchant fee rate (% of GBV, quarterly)", None, "merchant_fee_rate_q_pct", fmt=S.FMT_PCT2, indent=1, note="annual-equivalent 1.70% x seasonal factor; +1bp per point of non-NA revenue share")
    put("fees", "Merchant / payment fees ($m)", None, "cor_fees", indent=1)
    put("cb", "Chargebacks ($m)", None, "cor_chargebacks", indent=1)
    put("cbpb", "Chargebacks per booking ($)", None, None, fc_vals=[f"=IFERROR({qcol(NH+i)}{rows['cb']}/{qcol(NH+i)}{rows['bookings']},\"\")" for i in range(NF)], fmt=S.FMT_M2, indent=2)
    put("host", "Hosting ($m)", None, "cor_hosting", indent=1, note="$1.7bn of cloud commitments through 2031 (10-K); 'material increase in AI spend' (Mertz)")
    put("ops_pb", "Ops & support per booking ($)", None, "ops_per_booking", fmt=S.FMT_M2, indent=1, note="management: support cost per booking -10% (1Q26) and -16% (2Q26) y/y with AI; applies to ~22% of the line")
    put("mkt", "Brand + performance marketing ($m)", None, "sm_marketing", indent=1)
    put("mkt_pn", "  Marketing per night ($)", None, None, fc_vals=[f"=IFERROR({qcol(NH+i)}{rows['mkt']}/{qcol(NH+i)}{rows['nights']},\"\")" for i in range(NF)], fmt=S.FMT_M2, indent=2)
    put("fld", "Field operations & policy ($m)", None, "sm_field", indent=1)
    row += 1

    # ---- G. below EBITDA
    row = S.section(ws, row, "G. Below adjusted EBITDA (M7 bridge conventions)", ncols=ncols)
    put("sbc", "Stock-based compensation ($m)", [float(hq.loc[q, "sbc"]) for q in Dt.HIST_Q], "sbc", indent=1, note="+13.2% y/y on the year-ago quarter")
    put("da", "D&A ($m)", [float(hq.loc[q, "da"]) for q in Dt.HIST_Q], "da", indent=1, note="$20.6M per quarter")
    put("ii", "Interest income ($m)", [float(hq.loc[q, "interest_income"]) for q in Dt.HIST_Q], "interest_income", indent=1,
        note="rule: 0.876 x 3m T-bill (3.76% held) x average earning base (cash + STI $12.1bn + funds held, previous quarter) / 4; reproduces 2Q26 $183M. Short case: funds held -10%")
    put("ie", "Interest expense ($m)", [float(hq.loc[q, "interest_expense"]) for q in Dt.HIST_Q], "interest_expense", indent=1, note="$37M per quarter on the $2.5bn 2026 senior notes")
    put("etr", "Effective tax rate", [f"=IFERROR({hq.loc[q, 'tax']}/{hq.loc[q, 'pretax']},\"\")" for q in Dt.HIST_Q], "etr_pct", fmt=S.FMT_PCT, indent=1, note="18.0% for 2H26 (1H26 printed 17.1%), 17.5% for FY27; management guides 'high teens'")
    put("sh", "Diluted shares (m)", [float(hq.loc[q, "diluted_shares_m"]) for q in Dt.HIST_Q], "diluted_shares_m", fmt=S.FMT_M1, indent=1, note="-5.3M per quarter (the 2023-26 run rate of buybacks net of RSU issuance)")
    put("bb", "Share repurchases ($m, history)", [float(hq.loc[q, "buybacks"]) for q in Dt.HIST_Q], None, indent=1, note="FY24 $3.4bn, FY25 $3.8bn, 1H26 $2.1bn; $3.4bn authorisation left (Aug 2026)")
    put("fcf", "Free cash flow ($m, history)", [float(hq.loc[q, "fcf"]) for q in Dt.HIST_Q], None, indent=1, note="conversion above 100% of EBITDA is guest-float growth and interest income")
    row += 1

    # ---- H. parameters
    row = S.section(ws, row, "H. The line build's parameter sheet (40_params.csv): change a value there and re-run to regenerate", ncols=ncols)
    P = Dt.margin_build()["params"].copy()
    P = P[["line", "name", "base", "bear", "bull", "unit", "source"]]
    P.columns = ["Line", "Parameter", "Base", "Bear", "Bull", "Unit", "Source"]
    row = S.table(ws, row, P, first_col=1, default_fmt=S.FMT_M2, header_height=18, wrap_text_cols=["Source", "Unit"])
    ws.column_dimensions["G"].width = 12
    row += 1
    row = S.sources_block(ws, row, [
        ("Volume, unit costs, below-EBITDA forecast lines", "data/processed/margin_build/40_line_build/40_lines_quarterly.csv, 40_short_case_quarterly.csv, 40_params.csv"),
        ("Regional revenue", "data/processed/airbnb_regional_revenue_quarterly.csv (10-Q / 10-K)"),
        ("2027 nights and ADR builds", "data/processed/margin_build/06_fy27_path_v2/06_nights_build.csv, 06_adr_build.csv"),
        ("FX schedule", "data/processed/overnight/05_fx_schedule.csv (WS05 kernel, three USD paths)"),
        ("History", "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv; abnb_driver_history_quarterly.csv"),
    ], ncols=ncols)
    S.freeze(ws, f"B{HDR_ROW+1}")
    return ws
