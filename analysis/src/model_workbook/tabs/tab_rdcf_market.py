"""Tab 'Reverse DCF - Market': what the share price, the options market and the sell-side tape imply.

Reads the reverse-DCF run outputs under data/processed/reverse_dcf/ (market/, A-E/) built by
analysis/src/reverse_dcf/*.py on 12-13 Sep 2026. Blue = source value, black = formula.
Percent columns in the CSVs are stored as 11.5 meaning 11.5% and are divided by 100 here (style.pct);
probability columns are already fractions and are left as they are.
"""
from __future__ import annotations
import math
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
import style as S

SHEET = "Reverse DCF - Market"
NCOLS = 22
SPOT = 170.19


# ------------------------------------------------------------------ helpers
def _clean(df: pd.DataFrame) -> pd.DataFrame:
    return df.astype(object).where(df.notna(), None)


def _h(text: str, chars: int = 190) -> float:
    return max(15.0, 13.5 * math.ceil(len(text) / chars))


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _prep(df: pd.DataFrame, rename: dict, pct_cols: list | None = None) -> pd.DataFrame:
    """Keep the columns in `rename` (in order), divide percent columns by 100, rename to report labels."""
    keep = [c for c in rename if c in df.columns]
    out = df[keep].copy()
    for c in pct_cols or []:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce") / 100.0
    return _clean(out.rename(columns=rename))


def _table(ws, r: int, df: pd.DataFrame, fmts: dict, row_fill=None, wrap: list | None = None,
           first_col_chars: int = 46, first_col_wrap: bool = False) -> int:
    """style.table plus whole-row fills chosen by a function of the first column's value, and row heights for a
    wrapped first column."""
    r0 = r
    cols = list(df.columns)
    r = S.table(ws, r, df, first_col=1, fmts=fmts, wrap_text_cols=wrap, header_height=42)
    for i in range(len(df)):
        key = str(df.iloc[i, 0])
        fill = row_fill(key) if row_fill else None
        if fill is not None:
            for j in range(len(cols)):
                ws.cell(row=r0 + 1 + i, column=1 + j).fill = fill
        if first_col_wrap:
            ws.row_dimensions[r0 + 1 + i].height = max(15.0, 13.0 * math.ceil(len(key) / first_col_chars))
    return r


def _fill_team_street(key: str):
    k = key.lower()
    if k.startswith("team"):
        return S.FILL_KEY
    if k.startswith("street"):
        return S.FILL_STREET
    if "current price" in k or k.startswith("price"):
        return S.FILL_FORECAST
    return None


def _sign(x):
    v = _num(x)
    if v is None:
        return None
    return "accelerating" if v > 0 else ("decelerating" if v < 0 else "flat")


# ------------------------------------------------------------------ build
def build(wb):
    ws = wb.create_sheet(SHEET)
    widths = {get_column_letter(i): 14 for i in range(2, NCOLS + 1)}
    r = S.setup(ws, "Reverse DCF - Market-implied: what the price, the options and the sell-side imply",
                "Joint solve (multiple endogenous to growth) at $170.19, the options-implied distribution and 5 Nov event "
                "move, the sell-side tape, the print reaction function and the positioning card. Run of 12-13 Sep 2026.",
                widths=widths, label_width=48)

    comp = S.read("reverse_dcf/market/market_implied_comparison.csv")
    cases = S.read("reverse_dcf/market/market_implied_cases.csv")
    ladder = S.read("reverse_dcf/market/market_implied_by_price.csv")
    bh = S.read("reverse_dcf/B/B_headline.csv").set_index("item")
    bpts = S.read("reverse_dcf/B/B_dist_12m_price_points.csv")
    brates = S.read("reverse_dcf/B/B_print_base_rates.csv")
    dtape = S.read("reverse_dcf/D/D_tape_percentiles.csv")
    dhead = S.read("reverse_dcf/D/D_headline.csv")
    dtargets = S.read("reverse_dcf/D/D_target_implied.csv")
    cscen = S.read("reverse_dcf/C/C_scenarios.csv")
    ccoef = S.read("reverse_dcf/C/C_coefficients_used.csv")
    cbase = S.read("reverse_dcf/C/C_base_rates.csv")
    edist = S.read("reverse_dcf/E/E_street_distribution_vs_team.csv")
    esign = S.read("reverse_dcf/E/E_street_sign_summary.csv")
    eladder = S.read("reverse_dcf/E/E_repricing_ladder.csv")
    eguide = S.read("reverse_dcf/E/E_guide_vs_street_sign.csv")

    # headline numbers for the framing bullets (all from the CSVs)
    prop, chained, fixed = comp.iloc[0], comp.iloc[1], comp.iloc[2]
    at_price = ladder.loc[ladder.price == SPOT].iloc[0]
    s1 = ccoef.set_index("spec_id").loc["S1_post2022"]
    accel, decel = float(s1.c) + float(s1.b_sign), float(s1.c) - float(s1.b_sign)
    tape12 = dtape[dtape.tape == "12 Sep pull (feed as-is)"].set_index("stat")
    n_targets = int(float(tape12.loc["mean", "n"]))
    bv = lambda k: str(bh.loc[k, "value"])  # noqa: E731

    # ---------------------------------------------------------------- a. framing
    r = S.section(ws, r, "What this tab says", ncols=NCOLS)
    lines = [
        f"At ${SPOT:.2f} (close 11 Sep 2026; EV ${float(at_price.ev)/1000:,.1f}bn) the joint solve, with the multiple "
        f"endogenous to growth (EV/NTM EBITDA = 12.53 + 0.40 x growth, about 16 independent observations), says the price "
        f"pays for NTM revenue growth of {float(at_price.g_ntm):.1f}% (band {float(at_price.g_ntm_lo):.1f} to "
        f"{float(at_price.g_ntm_hi):.1f}). Mapped to FY27: revenue ${float(chained.fy27_revenue_musd)/1000:,.1f} to "
        f"{float(prop.fy27_revenue_musd)/1000:,.1f}bn (+{float(chained.fy27_growth_pct):.1f} to "
        f"+{float(prop.fy27_growth_pct):.1f}%), nights +{float(chained.fy27_nights_growth_pct):.1f} to "
        f"+{float(prop.fy27_nights_growth_pct):.1f}%, adj. EBITDA ${float(prop.fy27_ebitda_musd)/1000:,.1f}bn at "
        f"{float(prop.ev_fy27_ebitda_x):.1f} to {float(chained.ev_fy27_ebitda_x):.1f}x FY27 EBITDA. That is the Street "
        f"and the team's base case, about $5 below management's delivered case.",
        f"Fixed-multiple cross-check (16.5x held): FY27 revenue ${float(fixed.fy27_revenue_musd)/1000:,.1f}bn "
        f"(+{float(fixed.fy27_growth_pct):.1f}%), nights +{float(fixed.fy27_nights_growth_pct):.1f}%. It agrees with "
        f"the joint solve at the price and goes absurd in the tails, so the joint solve is primary and the fixed "
        f"multiple is the cross-check only. A point of FY27 nights is worth about $4.90 on the joint solve, $1.50 on a "
        f"fixed multiple.",
        f"Options (11 Sep chain): 12-month lognormal p25 / p50 / p75 = ${bv('p12m_lognormal_p25')} / "
        f"${bv('p12m_lognormal_p50')} / ${bv('p12m_lognormal_p75')} (p10 ${bv('p12m_lognormal_p10')}, p90 "
        f"${bv('p12m_lognormal_p90')}); risk-neutral P(above the $179.5 mean target) {bv('p12m_above_179p5')}. The 5 Nov "
        f"print is priced at an event sd of {bv('event_sd_central_pct').split(' ', 1)[0]}% "
        f"({bv('event_sd_central_pct').split(' ', 1)[1].strip('()')}), expected absolute move "
        f"{bv('event_exp_abs_move_central_pct').split(' ', 1)[0]}% "
        f"({bv('event_exp_abs_move_central_pct').split(' ', 1)[1].strip('()')}), against a realised print rms of "
        f"{bv('hist_realised_raw_rms_pct')}% raw "
        f"/ {bv('hist_realised_excess_rms_pct')}% QQQ-excess. The 20 Nov straddle ({float(bv('straddle_20nov_170_mid_pct_spot')):.1f}% "
        f"of spot) is a 70-day upper bound, not the print.",
        f"The only print reaction with statistical support is the sign of printed nights acceleration (S1, post-2022, "
        f"n {int(s1.n)}, permutation p {float(s1.perm_p):.3f}): fitted day-1 excess return {accel:+.1f}% on an "
        f"accelerating print vs {decel:+.1f}% on a decelerating one (group means +6.0 / -5.6% in the synthesis; 0 of 8 "
        f"post-2022 decelerating prints positive on excess returns). The Street's 3Q26 nights bar (148.9m, +11.45%) is an "
        f"acceleration; the team's nowcast (+9.5 to 10.0%) is a deceleration, so the team's base case implies -4 to -6% "
        f"conditional and -2 to -3.5% unconditional against a 9.5% priced dispersion.",
        f"Sell-side tape, 12 Sep: {n_targets} live targets, mean ${float(tape12.loc['mean', 'target']):.0f} = "
        f"{float(tape12.loc['mean', 'implied_ev_fy27_ebitda_spot_x']):.1f}x delivered FY27 EBITDA; p25 "
        f"${float(tape12.loc['p25', 'target']):.0f} ({float(tape12.loc['p25', 'implied_ev_fy27_ebitda_spot_x']):.1f}x) / "
        f"p75 ${float(tape12.loc['p75', 'target']):.0f} ({float(tape12.loc['p75', 'implied_ev_fy27_ebitda_spot_x']):.1f}x). "
        f"Held at 16.5x, the mean target needs FY27 revenue growth of "
        f"+{float(tape12.loc['mean', 'req_fy27_rev_growth_pct_at_16_5x']):.1f}%, which nobody forecasts: the tape is the "
        f"delivered case at a higher multiple, not a higher revenue number.",
    ]
    for ln in lines:
        r = S.text_row(ws, r, "• " + ln, font=S.f_label(), wrap_cols=NCOLS, height=_h(ln))
    r += 1

    # ---------------------------------------------------------------- b. who is pricing what
    r = S.section(ws, r, "Who is pricing what: management vs market vs team (FY27E on the delivered FY26 base; nights at "
                         "ADR +3%, FX -0.6pp, take rate flat)", ncols=NCOLS,
                  note="green = team rows, grey = Street, yellow = the current price")
    df = _prep(comp, {
        "who": "Who", "price": "Price / target ($)", "fy27_growth_pct": "FY27 revenue growth",
        "fy27_revenue_musd": "FY27 revenue ($m)", "fy27_ebitda_musd": "FY27 adj. EBITDA ($m)",
        "fy27_nights_growth_pct": "FY27 nights growth", "ev_fy27_ebitda_x": "EV / FY27 EBITDA",
        "p_above_12m": "Options P(above) in 12M", "expected_5nov_reaction_pct": "Expected 5 Nov day-1 move (S1 post-2022, conditional)",
    }, pct_cols=["fy27_growth_pct", "fy27_nights_growth_pct", "expected_5nov_reaction_pct"])
    r = _table(ws, r, df, {
        "Price / target ($)": S.FMT_USD, "FY27 revenue growth": S.FMT_PCT, "FY27 revenue ($m)": S.FMT_M,
        "FY27 adj. EBITDA ($m)": S.FMT_M, "FY27 nights growth": S.FMT_PCT, "EV / FY27 EBITDA": S.FMT_X,
        "Options P(above) in 12M": S.FMT_PROB, "Expected 5 Nov day-1 move (S1 post-2022, conditional)": S.FMT_PCT,
    }, row_fill=_fill_team_street)
    r += 1

    # ---------------------------------------------------------------- c. cases and implied prices
    r = S.section(ws, r, "Cases and their implied prices: joint solve (primary) vs fixed 16.5x (cross-check)", ncols=NCOLS)
    df = _prep(cases, {
        "case": "Case", "fy27_growth": "FY27 revenue growth", "fy27_ebitda_own": "FY27 adj. EBITDA, own case ($m)",
        "nights27": "FY27 nights growth", "price_joint": "Joint-solve price ($)", "upside_joint": "Upside vs $170.19",
        "price_fixed_16_5": "Price at fixed 16.5x on price-implied EBITDA ($)",
        "price_fixed_own_ebitda": "Price at 16.5x on own EBITDA ($)", "p_above_12m": "Options P(above) in 12M",
    }, pct_cols=["fy27_growth", "nights27", "upside_joint"])
    r = _table(ws, r, df, {
        "FY27 revenue growth": S.FMT_PCT, "FY27 adj. EBITDA, own case ($m)": S.FMT_M, "FY27 nights growth": S.FMT_PCT,
        "Joint-solve price ($)": S.FMT_USD, "Upside vs $170.19": S.FMT_PCT,
        "Price at fixed 16.5x on price-implied EBITDA ($)": S.FMT_USD, "Price at 16.5x on own EBITDA ($)": S.FMT_USD,
        "Options P(above) in 12M": S.FMT_PROB,
    }, row_fill=_fill_team_street)
    r += 1

    # ---------------------------------------------------------------- d. price ladder
    r = S.section(ws, r, "Price ladder: what each price point implies (joint solve on the NTM basis, mapped to FY27)", ncols=NCOLS,
                  note="g NTM in the guide-proxy units the regression was fitted on (about 1pt above realised growth)")
    df = _prep(ladder, {
        "label": "Price point", "price": "Price ($)", "ev": "EV ($m)", "g_ntm": "Implied NTM revenue growth",
        "g_ntm_lo": "NTM growth, band low", "g_ntm_hi": "NTM growth, band high", "m_ntm": "EV / NTM EBITDA",
        "g27_prop": "FY27 revenue growth (proportional map)", "rev27": "FY27 revenue ($m)", "ebitda27": "FY27 adj. EBITDA ($m)",
        "eps27": "FY27 EPS", "ev_fy27_ebitda": "EV / FY27 EBITDA", "nights27_prop": "FY27 nights growth (proportional)",
        "nights27_direct": "FY27 nights growth (chained)", "g27_fixed": "FY27 revenue growth at fixed 16.5x",
        "p_above_12m": "P(above) in 12M", "p_above_20nov": "P(above) at 20 Nov",
        "rdcf_reported": "Reverse DCF growth, reported FCF", "rdcf_sbc": "Reverse DCF growth, SBC-adjusted",
    }, pct_cols=["g_ntm", "g_ntm_lo", "g_ntm_hi", "g27_prop", "nights27_prop", "nights27_direct", "g27_fixed",
                 "rdcf_reported", "rdcf_sbc"])
    pf = {c: S.FMT_PCT for c in df.columns if "growth" in c or c.startswith("NTM") or c.startswith("Reverse")}
    pf.update({"Price ($)": S.FMT_USD, "EV ($m)": S.FMT_M, "EV / NTM EBITDA": S.FMT_X, "FY27 revenue ($m)": S.FMT_M,
               "FY27 adj. EBITDA ($m)": S.FMT_M, "FY27 EPS": S.FMT_EPS, "EV / FY27 EBITDA": S.FMT_X,
               "P(above) in 12M": S.FMT_PROB, "P(above) at 20 Nov": S.FMT_PROB})
    r = _table(ws, r, df, pf, row_fill=lambda k: S.FILL_FORECAST if k.startswith("price") else None)
    r += 1

    # ---------------------------------------------------------------- e. options
    r = S.section(ws, r, "Options: the 5 Nov event move and the 12-month distribution (yfinance chain, 11 Sep 2026 close)", ncols=NCOLS)
    r = S.header(ws, r, ["Value", "Status", "Note"], label="Item", height=18)
    B_ITEMS = [
        ("spot", "Spot ($)", S.FMT_USD),
        ("first_post_print_expiry", "First post-print expiry", None),
        ("straddle_16oct_170_mid_pct_spot", "16 Oct 170 straddle, mid (% of spot; pre-print, 35 days)", "pct"),
        ("straddle_20nov_170_mid_pct_spot", "20 Nov 170 straddle, mid (% of spot; 70-day TOTAL move)", "pct"),
        ("atm_iv_16oct_pct", "ATM implied vol, 16 Oct", "pct"),
        ("atm_iv_20nov_pct", "ATM implied vol, 20 Nov", "pct"),
        ("atm_iv_12m_pct", "ATM implied vol, 12M (variance-interpolated)", "pct"),
        ("event_sd_pair_16oct_20nov_pct", "Event sd: 16 Oct / 20 Nov pair", "pct"),
        ("event_sd_ls_one_print_pct", "Event sd: least squares, one print, 5 maturities", "pct"),
        ("event_sd_ls_all_sloped_bg_pct", "Event sd: least squares, 11 maturities, sloped background", "pct"),
        ("event_sd_two_post_pct", "Event sd: two post-print maturities", "pct"),
        ("event_sd_4sep_bbg_chain_pair_pct", "Event sd: same method on the 4 Sep Bloomberg chain", "pct"),
        ("event_sd_central_pct", "Event sd, central (JUDGEMENT), %", None),
        ("event_exp_abs_move_central_pct", "Expected absolute 5 Nov move, central, %", None),
        ("hist_mean_implied_sd_iv_crush_pct", "History: mean implied sd from IV crush, 23 prints", "pct"),
        ("hist_realised_raw_rms_pct", "History: realised print move, rms, raw", "pct"),
        ("hist_realised_excess_rms_pct", "History: realised print move, rms, QQQ-excess", "pct"),
        ("hist_realised_raw_up_down", "History: up / down prints, raw", None),
        ("hist_realised_excess_up_down", "History: up / down prints, excess", None),
        ("nights_accel_split_raw", "Nights accelerating / decelerating prints, raw", None),
        ("nights_accel_split_excess", "Nights accelerating / decelerating prints, excess", None),
        ("rr25_20nov_volpts", "25-delta risk reversal, 20 Nov (vol pts; negative = puts richer)", "0.00"),
        ("skew_90_110_20nov_volpts", "90 / 110 skew, 20 Nov (vol pts)", "0.00"),
        ("call10_over_put10_20nov_relative_to_flat", "10%-OTM call / put ratio relative to a flat smile", "0.000"),
        ("p_above_spot_20nov_rnd", "P(above spot) at 20 Nov, risk-neutral", S.FMT_PROB),
        ("p12m_lognormal_p10", "12M lognormal p10 ($)", S.FMT_USD),
        ("p12m_lognormal_p25", "12M lognormal p25 ($)", S.FMT_USD),
        ("p12m_lognormal_p50", "12M lognormal p50 ($)", S.FMT_USD),
        ("p12m_lognormal_p75", "12M lognormal p75 ($)", S.FMT_USD),
        ("p12m_lognormal_p90", "12M lognormal p90 ($)", S.FMT_USD),
        ("p12m_skew_rnd_p25", "12M skew-adjusted RND p25 ($, sensitivity)", S.FMT_USD),
        ("p12m_skew_rnd_p50", "12M skew-adjusted RND p50 ($, sensitivity)", S.FMT_USD),
        ("p12m_skew_rnd_p75", "12M skew-adjusted RND p75 ($, sensitivity)", S.FMT_USD),
        ("p12m_above_179p5", "P(above $179.5 mean target) in 12M, risk-neutral", None),
        ("p12m_above_220", "P(above $220 top target) in 12M", None),
        ("p12m_below_150", "P(below $150 bear tape) in 12M", None),
        ("p12m_below_125", "P(below $125) in 12M", None),
    ]
    for key, lab, fmt in B_ITEMS:
        if key not in bh.index:
            continue
        raw, status, note = bh.loc[key, "value"], bh.loc[key, "label"], bh.loc[key, "note"]
        val = _num(raw)
        if fmt is None or val is None:
            v, f = str(raw), "@"
        elif fmt == "pct":
            v, f = S.pct(val), S.FMT_PCT
        else:
            v, f = val, fmt
        bold = key in ("event_sd_central_pct", "event_exp_abs_move_central_pct", "p12m_lognormal_p25",
                       "p12m_lognormal_p50", "p12m_lognormal_p75", "p12m_above_179p5")
        r = S.write_row(ws, r, lab, [v, str(status), None if pd.isna(note) else str(note)], fmts=[f, "@", "@"],
                        kinds=["input", "label", "label"], bold=bold)
        ws.cell(row=r - 1, column=4).font = S.f_note()
    r += 1

    r = S.text_row(ws, r, "12-month distribution: P(above) at each price point, by method (risk-neutral, not a forecast; "
                   "lognormal on the interpolated 12M ATM IV is the headline)", font=S.f_label(True))
    piv = bpts.pivot_table(index=["price_point", "label", "pct_vs_spot"], columns="method", values="p_above").reset_index()
    piv = piv.sort_values("price_point")
    piv["pct_vs_spot"] = piv["pct_vs_spot"] / 100.0
    meth = {"lognormal_atm_iv_12m_interp": "P(above): lognormal, 12M interpolated IV (headline)",
            "lognormal_atm_iv_sep27_direct": "P(above): lognormal, Sep-27 IV direct",
            "two_sided_lognormal_10pct_wings": "P(above): two-sided lognormal, 10% wings",
            "skew_adjusted_rnd_smile_interp": "P(above): skew-adjusted RND"}
    piv = piv.rename(columns={"price_point": "Price point ($)", "label": "Label", "pct_vs_spot": "vs spot", **meth})
    piv = piv[["Label", "Price point ($)", "vs spot"] + [m for m in meth.values() if m in piv.columns]]
    pf = {"Price point ($)": S.FMT_USD, "vs spot": S.FMT_PCT}
    pf.update({m: S.FMT_PROB for m in meth.values()})
    r = _table(ws, r, _clean(piv), pf, row_fill=lambda k: S.FILL_FORECAST if k == "price" else None)
    r += 1

    r = S.text_row(ws, r, "Realised print-day move base rates (close to close, 23 prints since listing; raw and "
                   "QQQ-excess series)", font=S.f_label(True))
    df = _prep(brates, {
        "sample": "Sample", "series": "Series", "n": "n", "mean_abs_pct": "Mean |move|", "median_abs_pct": "Median |move|",
        "rms_pct": "RMS", "mean_signed_pct": "Mean signed", "share_abs_ge_7pct": "Share |move| >= 7%",
        "share_abs_ge_10pct": "Share |move| >= 10%", "n_up": "Up", "n_down": "Down", "mean_up_pct": "Mean up",
        "mean_down_pct": "Mean down", "mean_abs_gap_pct": "Mean |gap|", "mean_abs_open_to_close_pct": "Mean |open-to-close|",
        "p10": "p10", "p25": "p25", "p75": "p75", "p90": "p90",
    }, pct_cols=["mean_abs_pct", "median_abs_pct", "rms_pct", "mean_signed_pct", "mean_up_pct", "mean_down_pct",
                 "mean_abs_gap_pct", "mean_abs_open_to_close_pct", "p10", "p25", "p75", "p90"])
    df["Sample"] = df["Sample"].astype(str).str.replace("_", " ")
    pf = {c: S.FMT_PCT for c in df.columns if c not in ("Sample", "Series", "n", "Up", "Down")}
    pf.update({"n": S.FMT_INT, "Up": S.FMT_INT, "Down": S.FMT_INT})
    r = _table(ws, r, df, pf, row_fill=lambda k: S.FILL_KEY if k.startswith("nights decel") else None)
    r += 1

    # ---------------------------------------------------------------- f. sell-side
    r = S.section(ws, r, "Sell-side tape: what the targets imply (EV = target x 597.0m shares - $9,593m net cash; FY27 "
                         "EBITDA at 16.5x, margin 36.2%, FY26 base $14,231m)", ncols=NCOLS)
    r = S.text_row(ws, r, "12 Sep 2026 tape, 32 live targets, with the $170.19 price for comparison", font=S.f_label(True))
    df = _prep(dhead, {
        "stat": "Statistic", "target": "Target ($)", "implied_ev_fy27_ebitda_spot_x": "Implied EV / FY27 EBITDA (spot basis)",
        "implied_ev_fy27_ebitda_fy27_basis_x": "Implied EV / FY27 EBITDA (FY27-end basis)",
        "req_fy27_revenue_musd_at_16_5x": "Required FY27 revenue at 16.5x ($m)",
        "req_fy27_rev_growth_pct_at_16_5x": "Required FY27 revenue growth at 16.5x",
        "req_fy27_ebitda_musd_at_16_5x": "Required FY27 EBITDA at 16.5x ($m)",
        "req_ebitda_vs_delivered_pct_at_16_5x": "Required EBITDA vs delivered case",
        "req_fy27_nights_growth_pct_at_16_5x": "Required FY27 nights growth at 16.5x",
        "req_fy27_eps_at_16_5x": "Required FY27 EPS at 16.5x",
        "req_fy27_nights_growth_pct_at_13_5x": "Required nights growth at 13.5x",
        "req_fy27_nights_growth_pct_at_18_5x": "Required nights growth at 18.5x",
    }, pct_cols=["req_fy27_rev_growth_pct_at_16_5x", "req_ebitda_vs_delivered_pct_at_16_5x",
                 "req_fy27_nights_growth_pct_at_16_5x", "req_fy27_nights_growth_pct_at_13_5x",
                 "req_fy27_nights_growth_pct_at_18_5x"])
    pf = {c: S.FMT_PCT for c in df.columns if "growth" in c or "vs delivered" in c}
    pf.update({"Target ($)": S.FMT_USD, "Implied EV / FY27 EBITDA (spot basis)": S.FMT_X,
               "Implied EV / FY27 EBITDA (FY27-end basis)": S.FMT_X, "Required FY27 revenue at 16.5x ($m)": S.FMT_M,
               "Required FY27 EBITDA at 16.5x ($m)": S.FMT_M, "Required FY27 EPS at 16.5x": S.FMT_EPS})
    r = _table(ws, r, df, pf, row_fill=lambda k: S.FILL_FORECAST if "170.19" in k else None)
    r += 1

    r = S.text_row(ws, r, "Target percentiles by pull: the tape moved up into the 8-10 Sep drawdown (three raises, no cuts)",
                   font=S.f_label(True))
    stats = ["min", "p25", "median", "mean", "p75", "max"]
    pulls = [t for t in dtape.tape.unique() if t != "brief price points"]
    tp = pd.DataFrame({"Pull": pulls})
    tp["n"] = [float(dtape[(dtape.tape == p) & (dtape.stat == "mean")].n.iloc[0]) for p in pulls]
    for s in stats:
        tp[f"{s} target ($)"] = [float(dtape[(dtape.tape == p) & (dtape.stat == s)].target.iloc[0]) for p in pulls]
    tp["Dispersion (sd / mean)"] = [float(dtape[(dtape.tape == p) & (dtape.stat == "sd / mean")].target.iloc[0]) for p in pulls]
    tp["Share of targets below $170.19"] = [float(dtape[(dtape.tape == p) & (dtape.stat == "share below $170.19")].target.iloc[0]) / 100
                                            for p in pulls]
    pf = {f"{s} target ($)": S.FMT_USD0 for s in stats}
    pf.update({"n": S.FMT_INT, "Dispersion (sd / mean)": "0.000", "Share of targets below $170.19": S.FMT_PCT})
    r = _table(ws, r, _clean(tp), pf)
    r += 1

    r = S.text_row(ws, r, "All live targets (12 Sep 2026 feed), sorted by target; required growth holds 16.5x EV/EBITDA "
                   "and a 36.2% margin", font=S.f_label(True))
    dt = dtargets.sort_values("target", ascending=False)
    df = _prep(dt, {
        "Firm": "Firm", "date": "Date", "rating": "Rating", "target": "Target ($)", "upside_vs_170_19_pct": "Upside vs $170.19",
        "implied_ev_fy27_ebitda_spot_basis_x": "Implied EV / FY27 EBITDA (spot basis)",
        "implied_ev_fy27_ebitda_fy27_basis_x": "Implied EV / FY27 EBITDA (FY27-end basis)",
        "implied_pe_fy27_delivered_x": "Implied P/E on delivered FY27 EPS",
        "req_fy27_rev_growth_pct_at_16.5x": "Required FY27 revenue growth at 16.5x",
        "req_fy27_nights_growth_pct_at_16.5x": "Required FY27 nights growth at 16.5x",
    }, pct_cols=["upside_vs_170_19_pct", "req_fy27_rev_growth_pct_at_16.5x", "req_fy27_nights_growth_pct_at_16.5x"])
    r = _table(ws, r, df, {
        "Target ($)": S.FMT_USD0, "Upside vs $170.19": S.FMT_PCT, "Implied EV / FY27 EBITDA (spot basis)": S.FMT_X,
        "Implied EV / FY27 EBITDA (FY27-end basis)": S.FMT_X, "Implied P/E on delivered FY27 EPS": S.FMT_X,
        "Required FY27 revenue growth at 16.5x": S.FMT_PCT, "Required FY27 nights growth at 16.5x": S.FMT_PCT,
    })
    r += 1

    # ---------------------------------------------------------------- g. reaction function
    r = S.section(ws, r, "Reaction function for 5 Nov: what moves the stock on the print (re-test of the predictive study; "
                         "S1 sign rule is the headline, S2 illustrative)", ncols=NCOLS)
    r = S.text_row(ws, r, "Coefficients used (day-1 QQQ-excess return, %, = c + b_sign x sign(nights acceleration) + "
                   "b_gvs x guide-vs-Street % + ...); fitted accelerating / decelerating values are formulas",
                   font=S.f_label(True))
    df = _prep(ccoef, {
        "spec_id": "Spec", "spec": "Specification", "status": "Status", "c": "c (intercept, %)", "b_sign": "b sign(accel), %",
        "b_gvs": "b guide vs Street (% per 1%)", "b_rev": "b revenue surprise", "b_gdir": "b guide direction", "n": "n",
        "r2": "R2", "loo_r2": "LOO R2", "perm_p": "Permutation p", "resid_sd": "Residual sd, %",
    })
    r0 = r
    r = _table(ws, r, df, {"c (intercept, %)": S.FMT_M2, "b sign(accel), %": S.FMT_M2, "b guide vs Street (% per 1%)": S.FMT_M2,
                           "b revenue surprise": S.FMT_M2, "b guide direction": S.FMT_M2, "n": S.FMT_INT, "R2": "0.00",
                           "LOO R2": "0.00", "Permutation p": "0.000", "Residual sd, %": S.FMT_M2},
               wrap=["Specification", "Status"])
    cols = list(df.columns)
    c_col, b_col = get_column_letter(1 + cols.index("c (intercept, %)")), get_column_letter(1 + cols.index("b sign(accel), %"))
    acc_col, dec_col = 1 + len(cols), 2 + len(cols)
    for lab, cc in (("Fitted: accelerating print (%)", acc_col), ("Fitted: decelerating print (%)", dec_col)):
        h = ws.cell(row=r0, column=cc, value=lab)
        h.font = S.f_hdr(); h.fill = S.FILL_HEADER
        h.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i in range(len(df)):
        rr = r0 + 1 + i
        for cc, op in ((acc_col, "+"), (dec_col, "-")):
            c = ws.cell(row=rr, column=cc, value=f"={c_col}{rr}{op}{b_col}{rr}")
            c.font = S.f_formula(); c.number_format = S.FMT_M2
    r += 1

    r = S.text_row(ws, r, "Scenarios for the 5 Nov print: nights, the 4Q26 guide vs the Street, and the expected day-1 "
                   "excess return under each spec (E = fitted mean; realised p10/p90 = spread of history in that state)",
                   font=S.f_label(True))
    cs = cscen.copy()
    cs["accel_sign"] = cs["accel_sign"].map(_sign)
    df = _prep(cs, {
        "scenario": "Scenario", "conditional_on": "Conditional on", "nights_3q26_pct": "3Q26 nights growth",
        "accel_pts_vs_2q26": "Acceleration vs 2Q26 (pts)", "accel_sign": "Sign", "revenue_3q26_musd": "3Q26 revenue ($m)",
        "revenue_surprise_vs_street_pct": "Revenue vs Street", "nights_guide_4q26_pct": "4Q26 nights guide",
        "rev_guide_4q26_musd": "4Q26 revenue guide ($m)", "guide_vs_street_bbg_pct": "Guide vs Street (Bloomberg)",
        "guide_vs_street_zacks_pct": "Guide vs Street (Zacks)", "E_S1_post2022_pct": "E[day-1] S1 post-2022 (headline)",
        "E_S1_ex_reopening_pct": "E[day-1] S1 ex-reopening (n 16)", "E_S2_post2022_bbg_pct": "E[day-1] S2 post-2022, Bloomberg",
        "E_S2_post2022_zacks_pct": "E[day-1] S2 post-2022, Zacks", "E_S2_ex_reopening_bbg_pct": "E[day-1] S2 ex-reopening, Bloomberg",
        "realised_move_p10_S1_post2022_pct": "Realised p10 in this state (S1 post-2022)",
        "realised_move_p90_S1_post2022_pct": "Realised p90 in this state (S1 post-2022)",
    }, pct_cols=["nights_3q26_pct", "revenue_surprise_vs_street_pct", "nights_guide_4q26_pct", "guide_vs_street_bbg_pct",
                 "guide_vs_street_zacks_pct", "E_S1_post2022_pct", "E_S1_ex_reopening_pct", "E_S2_post2022_bbg_pct",
                 "E_S2_post2022_zacks_pct", "E_S2_ex_reopening_bbg_pct", "realised_move_p10_S1_post2022_pct",
                 "realised_move_p90_S1_post2022_pct"])
    pf = {c: S.FMT_PCT for c in df.columns if c not in ("Scenario", "Conditional on", "Sign", "Acceleration vs 2Q26 (pts)",
                                                        "3Q26 revenue ($m)", "4Q26 revenue guide ($m)")}
    pf.update({"Acceleration vs 2Q26 (pts)": S.FMT_PP2, "3Q26 revenue ($m)": S.FMT_M, "4Q26 revenue guide ($m)": S.FMT_M})
    r = _table(ws, r, df, pf, row_fill=_fill_team_street, wrap=["Scenario"], first_col_wrap=True)
    r += 1

    r = S.text_row(ws, r, "Unconditional base rates of the print-day move (all 23 prints; ex-reopening n 16; post-2022 n 14)",
                   font=S.f_label(True))
    df = _prep(cbase, {"sample": "Sample", "target": "Series", "n": "n", "mean": "Mean", "median": "Median", "sd": "sd",
                       "mean_abs": "Mean |move|", "share_positive": "Share positive", "share_abs_ge_7": "Share |move| >= 7%"},
               pct_cols=["mean", "median", "sd", "mean_abs"])
    r = _table(ws, r, df, {"n": S.FMT_INT, "Mean": S.FMT_PCT2, "Median": S.FMT_PCT2, "sd": S.FMT_PCT2, "Mean |move|": S.FMT_PCT2,
                           "Share positive": S.FMT_PCT, "Share |move| >= 7%": S.FMT_PCT})
    r += 1

    # ---------------------------------------------------------------- h. positioning card
    r = S.section(ws, r, "Positioning card: is the market positioned for an accelerating 3Q26? (workstream E; Bloomberg MODL "
                         "standard consensus, 12 Sep 2026)", ncols=NCOLS)
    r = S.text_row(ws, r, "Street distribution vs the team, by quarter and metric", font=S.f_label(True))
    r = S.header(ws, r, ["n", "Street low", "Street mean", "Street high", "Prior-year actual", "Street low growth",
                         "Street mean growth", "Street high growth", "Team value", "Team growth", "Team position",
                         "Position (% of range)", "Team source"], label="Quarter / metric", height=42)
    MFMT = {"nights_m": ("Nights (m)", S.FMT_M1), "gbv_musd": ("GBV ($m)", S.FMT_M), "adr_usd": ("ADR ($)", S.FMT_USD),
            "take_rate_pct": ("Take rate", S.FMT_PCT2), "revenue_musd": ("Revenue ($m)", S.FMT_M), "eps_usd": ("EPS", S.FMT_EPS)}
    for _, e in edist.iterrows():
        name, f = MFMT.get(e.metric, (e.metric, S.FMT_M1))
        is_tr = e.metric == "take_rate_pct"
        lv = lambda x: S.pct(float(x)) if is_tr else float(x)  # noqa: E731
        vals = [int(e.n_estimates), lv(e.street_low), lv(e.street_mean), lv(e.street_high), lv(e.prior_year_actual),
                S.pct(e.street_low_growth), S.pct(e.street_mean_growth), S.pct(e.street_high_growth), lv(e.team_value),
                S.pct(e.team_growth), str(e.team_position), S.pct(e.team_position_pct_of_range), str(e.team_source)]
        fm = [S.FMT_INT, f, f, f, f, S.FMT_PCT, S.FMT_PCT, S.FMT_PCT, f, S.FMT_PCT, "@", S.FMT_PCT, "@"]
        kinds = ["input"] * 10 + ["label", "input", "label"]
        fill = S.FILL_KEY if "below" in str(e.team_position) else None
        r = S.write_row(ws, r, f"{e.quarter} {name}", vals, fmts=fm, kinds=kinds, fill=fill)
        ws.cell(row=r - 1, column=14).font = S.f_note()
    r = S.text_row(ws, r, "The team's 3Q26 nights (146.8m) sit below the lowest of 28 estimates while its ADR is on "
                   "consensus; the Street's 148.9m bar is +11.45% vs 2Q26's +10.34%, an acceleration.", wrap_cols=NCOLS)
    r += 1

    r = S.text_row(ws, r, "What the Street's nights bar was positioned for at each scored print, and what printed "
                   "(16 prints with a nights consensus; 0.25pt dead band)", font=S.f_label(True))
    df = _prep(esign, {"street_positioned_for": "Street bar positioned for", "n": "Prints", "printed_accel": "Printed acceleration",
                       "printed_decel": "Printed deceleration", "mean_day1_excess": "Mean day-1 excess return",
                       "mean_nights_vs_street": "Mean nights beat vs Street (%)"},
               pct_cols=["mean_day1_excess", "mean_nights_vs_street"])
    r = _table(ws, r, df, {"Prints": S.FMT_INT, "Printed acceleration": S.FMT_INT, "Printed deceleration": S.FMT_INT,
                           "Mean day-1 excess return": S.FMT_PCT, "Mean nights beat vs Street (%)": S.FMT_PCT})
    g = eguide.iloc[0]
    r = S.write_row(ws, r, "Prints where management gave a next-quarter nights guide", [int(g.prints_with_guide)], fmt=S.FMT_INT)
    r = S.write_row(ws, r, "... where the Street's bar carried the same sign as the guide", [int(g.street_sign_matches_guide)], fmt=S.FMT_INT)
    r = S.write_row(ws, r, "... downside misses of a nights guide (1Q25, 'stable' printed 0.4pt lower)", [int(g.guide_downside_misses)], fmt=S.FMT_INT)
    r = S.write_row(ws, r, "... accelerating guides / met", [int(g.accelerating_guides), int(g.accelerating_guides_met)], fmt=S.FMT_INT)
    r = S.text_row(ws, r, "The bar is the guide: the team's call is a bet on the first downside miss of a management nights "
                   "guide in the sample. Say so before the judge does.", wrap_cols=NCOLS)
    r += 1

    r = S.text_row(ws, r, "Repricing ladder for 5 Nov: fundamental = joint-solve repricing if the market re-anchors NTM growth "
                   "to the printed path; sign rule = total day-1 excess return in history (alternatives, not addends)",
                   font=S.f_label(True))
    el = eladder.copy()
    el["accel_sign"] = el["accel_sign"].map(_sign)
    df = _prep(el, {
        "outcome": "Outcome on 5 Nov", "ntm_revenue_musd": "NTM revenue ($m)", "ntm_growth_pct": "NTM growth",
        "joint_solve_price_usd": "Joint-solve price ($)", "fundamental_repricing_pct": "Fundamental repricing",
        "joint_solve_price_if_path_is_realised_units_usd": "Joint-solve price, realised units ($)",
        "fundamental_repricing_realised_units_pct": "Fundamental repricing, realised units", "accel_sign": "3Q26 nights sign",
        "sign_rule_reaction_post2022_pct": "Sign rule, post-2022 (n 14)", "sign_rule_reaction_n16_pct": "Sign rule, ex-reopening (n 16)",
        "options_event_sd_pct": "Options event sd",
    }, pct_cols=["ntm_growth_pct", "fundamental_repricing_pct", "fundamental_repricing_realised_units_pct",
                 "sign_rule_reaction_post2022_pct", "sign_rule_reaction_n16_pct", "options_event_sd_pct"])
    pf = {c: S.FMT_PCT for c in df.columns if c not in ("Outcome on 5 Nov", "NTM revenue ($m)", "Joint-solve price ($)",
                                                        "Joint-solve price, realised units ($)", "3Q26 nights sign")}
    pf.update({"NTM revenue ($m)": S.FMT_M, "Joint-solve price ($)": S.FMT_USD, "Joint-solve price, realised units ($)": S.FMT_USD})
    r = _table(ws, r, df, pf, row_fill=_fill_team_street, wrap=["Outcome on 5 Nov"], first_col_wrap=True)
    r += 1

    # ---------------------------------------------------------------- i. caveats
    r = S.section(ws, r, "Honest caveats (these belong on the slide)", ncols=NCOLS)
    cav = [
        "About 16 independent observations sit behind the multiple-growth slope (EV/NTM EBITDA on NTM growth, t 3.1, R2 0.23); "
        "the FY27 mapping from the NTM basis is a judgement, so FY27 is quoted as a range across mappings, never a point.",
        "14 post-2022 prints (16 ex-reopening) sit behind the nights-acceleration sign rule; it is a re-test of the predictive "
        "study, not multiplicity-robust (no pre-stated spec clears Holm), and no print in the sample pairs an accelerating "
        "Street bar with a decelerating print, so that reaction is unobserved. Its content is the sign, not the size.",
        "Options probabilities are risk-neutral, not forecasts; the 12M quartiles are a lognormal on the interpolated ATM IV "
        "(skew-adjusted RND shown as a sensitivity; tails beyond quoted strikes are not quoted).",
        "The joint solve is primary; the fixed-multiple hold is the cross-check at the price only and is absurd in the tails. "
        "Nights are a residual of revenue at ADR +3%, FX -0.6pp, take rate flat (one for one): a judgement.",
        "The sell-side tape moves with the price symmetrically with a 1-2 month lag; a $5-7 cut in the mean target is the "
        "base case after the drawdown, not evidence of a view. The 12 Sep feed has 96 chain breaks; Bernstein's 25.5x is a P/E.",
    ]
    for ln in cav:
        r = S.text_row(ws, r, "• " + ln, font=S.f_label(), wrap_cols=NCOLS, height=_h(ln))
    r += 1

    # ---------------------------------------------------------------- j. sources
    S.sources_block(ws, r, [
        ("Who is pricing what; cases; price ladder", "data/processed/reverse_dcf/market/market_implied_comparison.csv, "
                                                     "market_implied_cases.csv, market_implied_by_price.csv"),
        ("Joint solve (workstream A)", "data/processed/reverse_dcf/A/A_joint_solve.csv, A_price_points.csv, A_implied_nights.csv"),
        ("Options (workstream B)", "data/processed/reverse_dcf/B/B_headline.csv, B_dist_12m_price_points.csv, B_print_base_rates.csv"),
        ("Reaction function (workstream C)", "data/processed/reverse_dcf/C/C_scenarios.csv, C_coefficients_used.csv, C_base_rates.csv"),
        ("Sell-side tape (workstream D)", "data/processed/reverse_dcf/D/D_headline.csv, D_tape_percentiles.csv, D_target_implied.csv"),
        ("Positioning card (workstream E)", "data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv, E_street_sign_summary.csv, "
                                            "E_guide_vs_street_sign.csv, E_repricing_ladder.csv"),
        ("Builder and notes", "analysis/src/reverse_dcf/market_implied_model.py; research/notes/2026-09-13_market-implied-model.md; "
                              "research/notes/reverse_dcf/ (A-E notes and audits)"),
        ("Synthesis", "docs/reverse_dcf/SYNTHESIS.md"),
        ("Workbook", "model/ABNB_market_implied.xlsx"),
    ], ncols=NCOLS)
    S.freeze(ws, "B4")
    return ws
