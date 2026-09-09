"""09. Build the ADR decomposition workbook.

Turns the workstream outputs into model/ADR_decomposition.xlsx: the history, the
decomposition, the regional panel, a forecastability scorecard, and a live forecast
scaffold whose cells are real formulas so the team can drive it.

The workbook is organised around one identity, which is what the study established:

    blended ADR y/y = FX
                    + geographic mix
                    + nights-weighted regional ADR ex-FX
                    + interaction

and the finding that makes it useful: regional ADR ex-FX has CONVERGED. The cross-regional
spread went 19.1pp (2022) -> 9.9 -> 3.7 -> 1.5pp (2025), with all four regions printing
2.6-4.1% in 2025. So the hard term is now a single number plus a band, and the forecastable
work sits in FX and mix.

Rebuild: py -3.13 analysis/src/adr/09_workbook.py
"""

import os
import pandas as pd
import xlsxwriter

OUT = "data/processed/adr"
XLSX = "model/ADR_decomposition.xlsx"
REG = ["na", "emea", "latam", "apac"]
REGN = {"na": "North America", "emea": "EMEA", "latam": "Latin America", "apac": "Asia Pacific"}


def qkey(q):
    return (int(q[2:]) + 2000, int(q[0]))


def load():
    hist = pd.read_csv(f"{OUT}/02b_adr_history_extended.csv")
    hist = hist.sort_values("quarter", key=lambda s: s.map(qkey))
    dec = pd.read_csv(f"{OUT}/07_full_decomposition.csv")
    ann = pd.read_csv(f"{OUT}/03_regional_annual_fx.csv")
    size_fc = pd.read_csv(f"{OUT}/13_party_size_adr_forecast.csv")
    size_fc = size_fc[size_fc.region.eq("global_nights_weighted")]
    return hist, dec, ann, size_fc


def build():
    hist, dec, ann, size_fc = load()
    os.makedirs("model", exist_ok=True)
    wb = xlsxwriter.Workbook(XLSX)

    # ---- formats -------------------------------------------------------------
    F = dict(
        h1=wb.add_format({"bold": True, "font_size": 15, "font_color": "#1a1a1a"}),
        h2=wb.add_format({"bold": True, "font_size": 11, "bg_color": "#EDF2F7",
                          "border": 1, "border_color": "#CBD5E0"}),
        hdr=wb.add_format({"bold": True, "bg_color": "#2D3748", "font_color": "white",
                           "border": 1, "text_wrap": True, "valign": "vcenter"}),
        txt=wb.add_format({"text_wrap": True, "valign": "top"}),
        body=wb.add_format({"border": 1, "border_color": "#E2E8F0"}),
        num=wb.add_format({"num_format": "0.00", "border": 1, "border_color": "#E2E8F0"}),
        num1=wb.add_format({"num_format": "0.0", "border": 1, "border_color": "#E2E8F0"}),
        usd=wb.add_format({"num_format": "$#,##0.00", "border": 1, "border_color": "#E2E8F0"}),
        pct=wb.add_format({"num_format": "0.0", "border": 1, "border_color": "#E2E8F0"}),
        bold=wb.add_format({"bold": True, "border": 1, "border_color": "#E2E8F0"}),
        boldn=wb.add_format({"bold": True, "num_format": "0.00", "border": 1,
                             "bg_color": "#F7FAFC", "border_color": "#E2E8F0"}),
        inp=wb.add_format({"num_format": "0.00", "border": 1, "bg_color": "#FEF3C7",
                           "border_color": "#D97706"}),
        out=wb.add_format({"num_format": "0.00", "border": 1, "bg_color": "#DBEAFE",
                           "bold": True, "border_color": "#2563EB"}),
        note=wb.add_format({"italic": True, "font_color": "#4A5568", "text_wrap": True,
                            "valign": "top"}),
        good=wb.add_format({"bg_color": "#D1FAE5", "border": 1, "text_wrap": True,
                            "valign": "top"}),
        mid=wb.add_format({"bg_color": "#FEF3C7", "border": 1, "text_wrap": True,
                           "valign": "top"}),
        bad=wb.add_format({"bg_color": "#FEE2E2", "border": 1, "text_wrap": True,
                           "valign": "top"}),
    )

    # ======================= 0. README ========================================
    ws = wb.add_worksheet("0_README")
    ws.set_column("A:A", 3); ws.set_column("B:B", 30); ws.set_column("C:C", 95)
    ws.write("B2", "ABNB ADR decomposition", F["h1"])
    r = 3
    for k, v in [
        ("Owner", "Krish. Built 7-8 Sep 2026 with Claude Code."),
        ("Source note", "research/notes/2026-09-07_adr-decomposition.md"),
        ("Scripts", "analysis/src/adr/01-14; data in data/processed/adr/. 10 is the audit, 11-12 the quote tests, 13 party size, 14a-c length of stay."),
        ("Rebuild", "py -3.13 analysis/src/adr/09_workbook.py"),
    ]:
        ws.write(r, 1, k, F["h2"]); ws.write(r, 2, v, F["txt"]); r += 1

    r += 1
    ws.write(r, 1, "The identity", F["h1"]); r += 1
    ws.write(r, 2, "blended ADR y/y  =  FX  +  geographic mix  +  nights-weighted regional "
                   "ADR ex-FX  +  interaction", F["h2"]); r += 2

    ws.write(r, 1, "Why it matters", F["h2"])
    ws.write(r, 2, "Blended ex-FX ADR is NOT a pricing signal. In 2025 it was +1.95% while "
                   "every single region priced at 2.6-4.1% (nights-weighted +3.54%). The "
                   "-1.58pp gap is geographic mix. Anyone reading blended ex-FX ADR as "
                   "'what Airbnb did on price' is under-reading it by roughly 1.6pp.", F["txt"])
    ws.set_row(r, 46); r += 2

    ws.write(r, 1, "The forecasting finding", F["h2"])
    ws.write(r, 2, "Regional ADR ex-FX has converged. Cross-regional spread: 19.1pp (2022) "
                   "-> 9.9 -> 3.7 -> 1.5pp (2025), with all four regions in a 2.6-4.1% band. "
                   "So the term that used to need four separate forecasts is now one number "
                   "plus a band, and the real forecasting work moves to FX and mix - both of "
                   "which are far more tractable. See sheet 4 and 5.", F["txt"])
    ws.set_row(r, 60); r += 2

    ws.write(r, 1, "Sheets", F["h1"]); r += 1
    for k, v in [
        ("1_History", "Quarterly ADR 1Q19-2Q26: level, reported y/y, FX contribution, ex-FX. "
                      "Ex-FX is disclosed from 2Q22 and reconstructed before that (validated "
                      "r 0.988, raw RMSE 0.68pp). 1Q20-2Q21 are flagged do-not-calibrate."),
        ("2_Decomposition", "Annual split into geographic mix, FX, interaction and "
                            "within-region ADR ex-FX, with the last broken down as far as "
                            "disclosure allows. REVISED 8 Sep after an audit; it now "
                            "reconciles to the independent 10-K regional panel within 0.3pp."),
        ("3_Regional", "Regional ADR levels and ex-FX growth from the 10-K, plus nights shares "
                       "and the convergence table."),
        ("4_Drivers", "Forecastability scorecard: for each term, how it behaves, whether it can "
                      "be forecast, and how."),
        ("5_Forecast", "Live scaffold. Yellow cells are inputs, blue cells are formulas. Drive "
                       "FY27 ADR from a USD path, a regional nights mix and a regional pricing "
                       "assumption."),
    ]:
        ws.write(r, 1, k, F["h2"]); ws.write(r, 2, v, F["txt"]); ws.set_row(r, 40); r += 1

    r += 1
    ws.write(r, 1, "Health warning", F["h2"])
    ws.write(r, 2, "Within-region pricing cannot be separated from SUB-REGIONAL (country) "
                   "mix, because Airbnb discloses no country-level ADR. The two are carried "
                   "as one jointly-unidentified term of ~+2.5 to +3.6pp. It is not noise: "
                   "expansion markets grow ~2x core and are lower-ADR, so it contains a real "
                   "negative mix component. Separately: every external price benchmark (CPI "
                   "lodging, BEA hotels, MAR/HLT RevPAR) has Bonferroni p=1.000 against ABNB "
                   "ADR ex-FX on 2023Q1+, so do NOT build a price forecast on a hotel index.",
             F["txt"])
    ws.set_row(r, 72)

    # ======================= 1. HISTORY =======================================
    ws = wb.add_worksheet("1_History")
    ws.freeze_panes(4, 1)
    ws.set_column("A:A", 10); ws.set_column("B:E", 13); ws.set_column("F:F", 34)
    ws.set_column("G:G", 15)
    ws.write("A1", "Quarterly ADR history and the ex-FX reconstruction", F["h1"])
    ws.write("A2", "ADR level from 1Q19 (1Q21 letter Quarterly Summary); ex-FX disclosed from "
                   "2Q22, reconstructed before that.", F["note"])
    cols = ["Quarter", "ADR $", "Reported y/y %", "FX contribution pp", "ADR ex-FX y/y %",
            "Basis", "Use for calibration?"]
    for c, h in enumerate(cols):
        ws.write(3, c, h, F["hdr"])
    ws.set_row(3, 30)
    row = 4
    for _, x in hist.iterrows():
        ws.write(row, 0, x.quarter, F["body"])
        ws.write(row, 1, x.adr_usd, F["usd"])
        for c, v in [(2, x.adr_yoy_reported_pct), (3, x.fx_pts_adr_final),
                     (4, x.adr_yoy_exfx_final)]:
            ws.write(row, c, None if pd.isna(v) else v, F["num"])
        ws.write(row, 5, x.basis if isinstance(x.basis, str) else "", F["body"])
        ws.write(row, 6, "" if pd.isna(x.adr_yoy_reported_pct)
                 else ("yes" if x.usable_for_calibration else "NO - COVID distortion"),
                 F["body"])
        row += 1
    ws.conditional_format(4, 4, row - 1, 4, {"type": "3_color_scale",
                                             "min_color": "#FEE2E2", "mid_color": "#FEF3C7",
                                             "max_color": "#D1FAE5"})

    # ======================= 2. DECOMPOSITION =================================
    ws = wb.add_worksheet("2_Decomposition")
    ws.set_column("A:A", 42); ws.set_column("B:E", 12); ws.set_column("F:F", 60)
    ws.write("A1", "Annual ADR decomposition (pp of ADR y/y)", F["h1"])
    ws.write("A2", "REVISED 8 Sep after an audit. The first version carried a large "
                   "'unexplained' line that was mostly two method errors: FX was re-derived "
                   "instead of taken from the letters (wrong by 1.33pp in 2022), and a hotel "
                   "price proxy with r~0 against ABNB ADR was subtracted as a component. "
                   "Corrected, the decomposition reconciles to the independent regional "
                   "panel within 0.3pp.", F["note"])
    ws.set_row(1, 46)
    years = dec.year.tolist()
    ws.write(3, 0, "Term", F["hdr"])
    for i, y in enumerate(years):
        ws.write(3, 1 + i, int(y), F["hdr"])
    ws.write(3, 1 + len(years), "How to read it", F["hdr"])
    ws.set_row(3, 30)

    rows = [
        ("ADR y/y, reported", "adr_yoy_pct", True,
         "What actually printed."),
        ("Geographic mix (4-region)", "geo_mix_pp", False,
         "Nights shifting to lower-ADR regions. Negative every year and getting worse."),
        ("FX", "fx_pp", False,
         "DISCLOSED in the letters, GBV-weighted - not re-derived. Forecast with "
         "0.52 - 0.72 x broad USD y/y, r 0.96."),
        ("Interaction", "interaction_pp", False,
         "Mix x rate cross-term. Small."),
        ("Within Region ADR ex-FX", "within_region_exfx_pp", True,
         "The residual of the identity. RECONCILES to the independent 10-K regional panel "
         "within 0.3pp in 2023-25 - see the check below."),
        ("   of which length of stay", "of_which_los_pp", False,
         "Bounded, not fitted - the panel could not identify an elasticity."),
        ("   of which unit-size mix", "size_mix_pp", False,
         "Bedrooms and capacity per booked night, 29 markets. NA/EMEA only."),
        ("   of which pricing + SUB-REGIONAL MIX", "pricing_and_subregional_mix_pp", True,
         "JOINTLY UNIDENTIFIED. Airbnb discloses no country-level ADR, so within-region "
         "pricing cannot be separated from country mix. Not noise: expansion markets grow "
         "~2x core and are lower-ADR, so this carries a real negative mix term."),
        ("", None, False, ""),
        ("Memo: independent regional ex-FX", "regional_exfx_independent_pp", False,
         "Nights-weighted regional ADR ex-FX built separately from the 10-K."),
        ("Memo: reconciliation gap", "reconciliation_gap_pp", False,
         "Within-region term less the independent build. 2023-25: +0.03, +0.30, -0.13pp."),
        ("Memo: hotel price comparator", "hotel_price_comparator_pp", False,
         "COMPARATOR ONLY, never a component. Hotel benchmarks have r~0 with ABNB ADR "
         "ex-FX post-2023, so subtracting one would inject variance, not explain it."),
    ]
    r = 4
    for label, col, bold, how in rows:
        ws.write(r, 0, label, F["bold"] if bold else F["body"])
        for i, y in enumerate(years):
            if col is None:
                continue
            v = dec.loc[dec.year == y, col]
            v = None if v.empty or pd.isna(v.values[0]) else float(v.values[0])
            ws.write(r, 1 + i, v, F["boldn"] if bold else F["num"])
        ws.write(r, 1 + len(years), how, F["txt"])
        r += 1
    r += 1
    ws.write(r, 0, "Confidence", F["h2"])
    for i, y in enumerate(years):
        c = dec.loc[dec.year == y, "confidence"].values[0]
        ws.write(r, 1 + i, str(c)[:14], F["body"])

    # ======================= 3. REGIONAL ======================================
    ws = wb.add_worksheet("3_Regional")
    ws.set_column("A:A", 24); ws.set_column("B:G", 12)
    ws.write("A1", "Regional ADR, from the 10-K Geographic Mix tables", F["h1"])
    ws.write("A2", "Non-circular anchor: the filings give regional nights, GBV and revenue, and "
                   "name regional ADR outright through FY2022.", F["note"])
    yrs = sorted(ann.year.unique())

    def block(title, values, start, fmt, note=""):
        ws.write(start, 0, title, F["h2"])
        for i, y in enumerate(yrs):
            ws.write(start, 1 + i, int(y), F["hdr"])
        s = start + 1
        for rg in REG:
            ws.write(s, 0, REGN[rg], F["body"])
            for i, y in enumerate(yrs):
                v = values(rg, y)
                ws.write(s, 1 + i, v, fmt)
            s += 1
        if note:
            ws.write(s, 0, note, F["note"]); s += 1
        return s + 1

    idx = ann.set_index(["region", "year"])

    def g(col):
        def f(rg, y):
            try:
                v = idx.loc[(rg, y), col]
                return None if pd.isna(v) else float(v)
            except KeyError:
                return None
        return f

    r = 3
    r = block("ADR level, $", g("adr"), r, F["usd"])
    r = block("ADR ex-FX y/y, %", g("adr_exfx_yoy"), r, F["num1"])
    r = block("Nights share of total, %", g("nights_share_pct"), r, F["num1"])

    ws.write(r, 0, "Cross-regional spread in ADR ex-FX growth (max - min, pp)", F["h2"])
    for i, y in enumerate(yrs):
        ws.write(r, 1 + i, int(y), F["hdr"])
    r += 1
    ws.write(r, 0, "Spread", F["bold"])
    for i, y in enumerate(yrs):
        s = ann[ann.year == y].adr_exfx_yoy
        ws.write(r, 1 + i, None if s.isna().all() else float(s.max() - s.min()), F["boldn"])
    r += 2
    ws.write(r, 0, "THE CONVERGENCE: regional pricing has collapsed into a 1.5pp band. That is "
                   "what makes the forecast on sheet 5 tractable - one pricing number plus a "
                   "band, instead of four independent regional forecasts.", F["note"])
    ws.set_row(r, 30)

    # ======================= 4. DRIVERS =======================================
    ws = wb.add_worksheet("4_Drivers")
    ws.set_column("A:A", 26); ws.set_column("B:B", 11); ws.set_column("C:C", 46)
    ws.set_column("D:D", 52)
    ws.write("A1", "Forecastability scorecard", F["h1"])
    ws.write("A2", "Ordered by how much of the ADR move they explain AND how forecastable they "
                   "are. Forecast the top of this list properly; do not pretend to forecast the "
                   "bottom.", F["note"])
    for c, h in enumerate(["Term", "Forecast-\nability", "How it behaves",
                           "How to forecast it"]):
        ws.write(3, c, h, F["hdr"])
    ws.set_row(3, 34)
    drivers = [
        ("FX", "HIGH", F["good"],
         "Mechanical and knowable daily. Fitted ADR FX = 0.52 - 0.72 x broad USD y/y; "
         "r 0.96, walk-forward 0.44x naive. Ranged +5.0pp (1Q26) to -7.1pp (3Q22).",
         "Take the USD path off the forward curve or a consensus track and apply the fit. "
         "This is the only ADR term with demonstrated predictive power. Already in the "
         "driver model."),
        ("Geographic mix", "HIGH", F["good"],
         "Slow, monotonic, and negative every year since 2021: -0.5, -2.8, -1.1, -1.2, "
         "-1.6pp. NA nights share fell 39.1% -> 29.6% over five years, roughly 1.5-2pp a year.",
         "Sum of (change in regional nights share) x (regional ADR level). Both inputs are "
         "disclosed annually in the 10-K. Drive it off the regional nights forecast. NOTE: "
         "WS10's shares are wrong for LatAm/APAC - use the 10-K."),
        ("Regional ADR ex-FX", "MEDIUM", F["mid"],
         "Converged. Spread across regions fell 19.1pp (2022) -> 1.5pp (2025); all four "
         "regions printed 2.6-4.1% in 2025, nights-weighted +3.54%.",
         "Carry ONE number with a band (base ~3.0-3.5%, bear ~2%, bull ~4%) rather than four "
         "regional forecasts. Revisit if the spread re-widens - that would be the signal that "
         "a region has decoupled."),
        ("Unit-size mix (party size)", "MEDIUM", F["mid"],
         "Steady and structural: booked capacity per stay +1.2-1.6% a year globally since "
         "2022 (NA +2.5-3%, EMEA +0.5-1%, APAC +1-1.5%, LatAm ~0), worth +0.7-0.9pp of ADR "
         "at elasticity 0.59. Does not explain quarter-to-quarter ADR variance (r ~0 vs "
         "ex-FX); it is a level term, not a timing signal.",
         "13_party_size_adr.py: capacity of the reviewed listing, 123 markets, 15 years, by "
         "region. Drive it off the team's people-per-booking forecast at constant fill "
         "(d ln capacity = d ln party size), regionally. Bear = mix shift matured (the "
         "sleeps-5+ share stalled at 25-27% in 2025-26)."),
        ("Length-of-stay mix", "MEDIUM", F["mid"],
         "Bucket mix term, replaces the rejected elasticity. Per-night price at 7-27 nights "
         "is 0.97x and at 28+ is 0.85x an under-7 stay (host + platform discounts, 139 quote "
         "dumps, stable across regions). The 28+ share of nights fell 21% (2021) -> ~13-15% "
         "(2025-26), about -2pp a year, corroborated by two sources (ALOS identity; "
         "calendar runs Sep-25 -> Aug-26). Worth +0.16, +0.33, +0.34, +0.35pp in 2022-25.",
         "14a/b/c_los_*.py. Term = sum over buckets of d(nights share) x (price ratio - 1). "
         "Base: 28+ share keeps falling ~2pp a year -> +0.3pp. Bear: shares stabilise -> 0. "
         "Bull: LatAm-style -3pp -> +0.45pp. The same bucket shares give ALOS for the nights "
         "model; do not forecast ALOS separately."),
        ("Like-for-like price", "NOT\nFORECASTABLE", F["bad"],
         "No external series tracks it post-reopening. CPI lodging r=+0.05, BEA r=+0.01, "
         "MAR/HLT r=+0.13 on 2023Q1+, all Bonferroni p=1.000.",
         "Do NOT build a price forecast off a hotel index - it has no demonstrated power. "
         "Price is inside the regional pricing number above, as an assumption. Say so out "
         "loud rather than dressing it as a forecast."),
    ]
    r = 4
    for name, score, fmt, behav, how in drivers:
        ws.write(r, 0, name, F["bold"])
        ws.write(r, 1, score, fmt)
        ws.write(r, 2, behav, F["txt"])
        ws.write(r, 3, how, F["txt"])
        ws.set_row(r, 62)
        r += 1

    # ======================= 5. FORECAST ======================================
    ws = wb.add_worksheet("5_Forecast")
    ws.set_column("A:A", 40); ws.set_column("B:D", 14); ws.set_column("E:E", 58)
    ws.write("A1", "ADR forecast scaffold", F["h1"])
    ws.write("A2", "Yellow = input, blue = formula. Change the yellow cells.", F["note"])

    ws.write(3, 0, "Driver", F["hdr"])
    for i, c in enumerate(["Bear", "Base", "Bull"]):
        ws.write(3, 1 + i, c, F["hdr"])
    ws.write(3, 4, "Basis", F["hdr"])

    # inputs
    sz = {c: float(size_fc[size_fc.case.eq(c)].size_term_pp.iloc[0]) for c in ("bear", "base", "bull")}
    inputs = [
        ("Broad USD y/y, % (FY27 avg)", [3.0, 0.0, -3.0],
         "Consensus / forward curve. 3Q26 QTD was -0.4%."),
        ("Regional pricing + sub-regional mix, % (ex unit size, ex LOS)", [1.5, 2.2, 2.55],
         "2025 within-region ex-FX was +3.5% nights-weighted, of which ~0.7pp was unit-size "
         "mix and ~0.35pp length-of-stay mix (rows below). Not measurable externally: a rate "
         "with a band, not a forecast."),
        ("Length-of-stay mix, pp", [0.0, 0.3, 0.45],
         "14a/b/c_los_*: 28+ nights share falling ~2pp a year into shorter stays, at per-night "
         "ratios 0.97 (7-27n) and 0.85 (28+). Ran +0.16, +0.33, +0.34, +0.35pp in 2022-25. "
         "Bear = bucket shares stabilise; bull = LatAm-style -3pp a year."),
        ("Unit-size mix via party size, pp", [round(sz["bear"], 2), round(sz["base"], 2), round(sz["bull"], 2)],
         "13_party_size_adr: booked-capacity growth by region (Inside Airbnb reviews, 123 "
         "markets, fixed 2019 weights) x price elasticity 0.59, nights-weighted on 10-K 2025 "
         "shares. Base = trailing 8-quarter capacity growth; bear = mix shift matured; bull = "
         "recent peak. To drive off a people-per-booking forecast: d ln capacity = d ln party "
         "size at constant fill."),
        ("Fee migration reprice, pp", [-0.5, 0.5, 1.5],
         "ADR is gross of the guest fee, so the single-fee move is +0.7% on the migrated cohort "
         "if hosts hold payout, -12.3% if they do not, +3.8% if they over-reprice. Prints reject "
         "no-reprice (1H26 NA accelerated). Applies to 4Q26-3Q27 y/y."),
        ("Geographic mix drag, pp", [-2.0, -1.7, -1.2],
         "Ran -1.1, -1.2, -1.6pp in 2023-25. Drive off the regional nights build."),
        ("Interaction, pp", [-0.15, -0.10, -0.05],
         "Has been -0.05 to -0.11pp since 2023."),
    ]
    r = 4
    for label, vals, basis in inputs:
        ws.write(r, 0, label, F["body"])
        for i, v in enumerate(vals):
            ws.write_number(r, 1 + i, v, F["inp"])
        ws.write(r, 4, basis, F["txt"])
        ws.set_row(r, 40)
        r += 1

    usd_r, price_r, los_r, size_r, fee_r, mix_r, int_r = 5, 6, 7, 8, 9, 10, 11  # 1-indexed Excel rows

    r += 1
    ws.write(r, 0, "FX contribution, pp  = 0.52 - 0.72 x USD y/y", F["bold"])
    for i, col in enumerate("BCD"):
        ws.write_formula(r, 1 + i, f"=0.52-0.72*{col}{usd_r}", F["out"])
    ws.write(r, 4, "Fitted on 17 disclosed quarters, r 0.96, walk-forward 0.44x naive.",
             F["txt"])
    fx_r = r + 1
    r += 2

    ws.write(r, 0, "ADR ex-FX y/y, %  = pricing + LOS mix + unit size + fee + geo mix + interaction", F["bold"])
    for i, col in enumerate("BCD"):
        ws.write_formula(r, 1 + i, f"={col}{price_r}+{col}{los_r}+{col}{size_r}+{col}{fee_r}+{col}{mix_r}+{col}{int_r}", F["out"])
    ws.write(r, 4, "This is what the letters would report as ex-FX ADR. Note it is 1.5-1.8pp "
                   "BELOW the regional pricing number - that gap is geographic mix.", F["txt"])
    ws.set_row(r, 30)
    exfx_r = r + 1
    r += 1

    ws.write(r, 0, "ADR y/y reported, %", F["bold"])
    for i, col in enumerate("BCD"):
        ws.write_formula(r, 1 + i, f"={col}{exfx_r}+{col}{fx_r}", F["out"])
    ws.write(r, 4, "The printed number.", F["txt"])
    rep_r = r + 1
    r += 1

    last_adr = float(hist.adr_usd.dropna().iloc[-1])
    ws.write(r, 0, "Implied ADR level, $ (off 2Q26 $%.2f)" % last_adr, F["bold"])
    for i, col in enumerate("BCD"):
        ws.write_formula(r, 1 + i, f"={last_adr}*(1+{col}{rep_r}/100)", F["usd"])
    ws.write(r, 4, "Illustrative level only - ADR is strongly seasonal (Q1 high, Q3 low), so "
                   "compare like quarters.", F["txt"])
    r += 3

    ws.write(r, 0, "How to use this", F["h1"]); r += 1
    for line in [
        "1. FX is the only term with demonstrated predictive power. Get the USD path right and "
        "you have removed the single largest source of ADR variance - it swung +5.0pp to -7.1pp.",
        "2. Geographic mix is the most reliably WRONG term in other people's models. It is "
        "disclosed in the 10-K and is negative every year. Do not leave it at zero.",
        "3. Regional pricing is one number now, not four. That is the convergence finding. If "
        "the regional spread re-widens above ~3pp, this simplification breaks and you go back "
        "to forecasting regions.",
        "4. Do not add a separate 'price' line driven off hotel CPI or RevPAR. It has no "
        "demonstrated relationship with Airbnb's ADR since the reopening.",
        "5. Sanity check: at base this scaffold gives ex-FX ADR around +1.5%, against the "
        "driver model's FY27 assumption of +2.5%. If the mix drag is real and regional pricing "
        "stays near 3.25%, the model's ADR is roughly 1pp too high.",
    ]:
        ws.write(r, 0, line, F["txt"])
        ws.merge_range(r, 0, r, 4, line, F["txt"])
        ws.set_row(r, 30)
        r += 1

    wb.close()
    return XLSX


if __name__ == "__main__":
    p = build()
    print(f"wrote {p}")
