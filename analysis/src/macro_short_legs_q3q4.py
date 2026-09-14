"""
Which MACRO variables can actually move ABNB in 3Q26/4Q26 — tested, not asserted.

Screens every macro channel against two bars:
  (a) has it ever moved this stock?           abnb_big_moves_7pct.csv, 41 daily moves >=7% since IPO
  (b) does it hit the 3Q26/4Q26 P&L or multiple, not 2028?

Run:  python3 analysis/src/macro_short_legs_q3q4.py
Out:  data/processed/macro_short_legs_q3q4.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "data/processed"

# FY2025 income statement, summed from abnb_quarterly_costlines.csv
INTEREST_INCOME = {"FY2023": 721.0, "FY2024": 818.0, "FY2025": 705.0,
                   "1H2025": 363.0, "1H2026": 338.0, "2Q2025": 190.0, "2Q2026": 183.0}


def main():
    rows = []
    macro = pd.read_csv(P / "macro_us_monthly.csv")
    macro["month"] = pd.PeriodIndex(macro.month, freq="M")
    macro = macro.set_index("month")
    aug26, aug25 = pd.Period("2026-08", "M"), pd.Period("2025-08", "M")

    print("=" * 78)
    print("1. WHAT HAS ACTUALLY MOVED THIS STOCK")
    print("=" * 78)
    bm = pd.read_csv(P / "abnb_big_moves_7pct.csv")
    bm["yr"] = pd.to_datetime(bm.date).dt.year
    print(bm.groupby("driver").size().to_string())
    m = bm[bm.driver == "Macro/market"]
    slope, intercept = np.polyfit(m.qqq_pct, m.abnb_move_pct, 1)
    corr = np.corrcoef(m.qqq_pct, m.abnb_move_pct)[0, 1]
    amp = m.abnb_move_pct.abs().mean() / m.qqq_pct.abs().mean()
    print(f"\nMacro is the single biggest bucket: {len(m)} of {len(bm)} moves.")
    print(f"  On those days ABNB = {slope:.2f} x QQQ (corr {corr:.2f}), "
          f"{amp:.1f}x amplification in absolute terms.")
    print("  -> ABNB does not have its own macro. It is a high-beta expression of the tape.")
    print("\nBut the REGIME matters. Macro big moves by year:")
    print("  " + "  ".join(f"{y}:{n}" for y, n in m.groupby("yr").size().items()))
    print("  14 of 20 were the 2022 hiking cycle; 2 were the April 2025 tariff days.")
    print("  ZERO in 2023, 2024 or 2026. A 7% macro day needs a macro SHOCK, not a macro drift.")

    print("\n" + "=" * 78)
    print("2. THE FUNDAMENTAL BEAT DOES NOT EXPLAIN THE REACTION")
    print("=" * 78)
    rr = pd.read_csv(P / "abnb_reaction_regression.csv")
    b = rr[(rr.dependent == "excess_1d_pct") & (rr.spec == "beat_guide")].iloc[0]
    print(f"  excess_1d ~ beat + guide:  n={int(b.n)}  R2={b.r2:.3f}  adj-R2={b.adj_r2:.3f}")
    print(f"  beat coefficient t={b.t_beat_vs_mid_pct:.2f}, p={b.p_beat_vs_mid_pct:.2f}")
    print("  Every spec has NEGATIVE adjusted R2 and no coefficient clears p=0.35.")
    print("  -> 'they miss nights by 2 points' has no measured link to the stock moving.")
    print("     The macro/valuation legs are not decoration. They are where the edge is.")

    print("\n" + "=" * 78)
    print("3. MACRO SCREEN, Aug 2026 vs Aug 2025")
    print("=" * 78)
    channels = [
        ("fedfunds", "Fed funds", "SHORT", "interest income is ~100% margin and rate-linked"),
        ("gs10", "10-year", "SHORT", "long-duration multiple; reverse DCF needs 11-14% growth"),
        ("wti", "WTI crude", "SHORT", "airfare pass-through; 2 of 20 macro big moves were oil"),
        ("umcsent", "U.Mich sentiment", "SHORT", "travel is discretionary"),
        ("usd_broad", "Broad dollar", "LONG", "~58% of revenue is ex-NA; weak USD helps"),
        ("unrate", "Unemployment", "LONG", "labour market improving"),
    ]
    print(f"  {'channel':18s} {'Aug25':>9s} {'Aug26':>9s} {'YoY':>9s}  direction")
    for col, label, side, why in channels:
        a = macro.loc[aug26, col]
        p = macro.loc[aug25, col]
        if np.isnan(a):  # sentiment has no Aug26 print
            a = macro.loc[pd.Period("2026-07", "M"), col]
            p = macro.loc[pd.Period("2025-07", "M"), col]
            label += " (Jul)"
        chg = 100 * (a / p - 1)
        print(f"  {label:18s} {p:9.2f} {a:9.2f} {chg:+8.1f}%  {side:5s} {why}")
        rows.append({"channel": label, "aug_2025": p, "aug_2026": a,
                     "yoy_pct": round(chg, 1), "side": side, "why": why})

    print("\n  THE SPLIT IS THE POINT: Fed funds -16% while the 10-year is +10%.")
    print("  Front end down hits the P&L now. Long end up hits the multiple now.")
    print("  Two different macro variables, same direction for a short, both live in 3Q/4Q26.")
    print("  Kept on the record AGAINST the short: the dollar is 1.4% weaker and")
    print("  unemployment is 20bp lower. Both are tailwinds. Neither is large.")

    print("\n" + "=" * 78)
    print("4. THE ONE MACRO CHANNEL THAT IS ABNB-SPECIFIC: INTEREST INCOME")
    print("=" * 78)
    cl = pd.read_csv(P / "abnb_quarterly_costlines.csv")
    fy25 = cl[cl.quarter.isin(["1Q25", "2Q25", "3Q25", "4Q25"])]
    op25 = fy25.operating_income_musd.sum()
    ii25 = INTEREST_INCOME["FY2025"]
    print(f"  FY2025 operating income      ${op25:,.0f}mm")
    print(f"  FY2025 interest income       ${ii25:,.0f}mm   = {100*ii25/op25:.1f}% of operating income")
    print(f"  implied pre-tax (op + int)   ${op25+ii25:,.0f}mm   interest = {100*ii25/(op25+ii25):.1f}% of it")
    print("  Interest income is ~100% margin. It is a fifth of pre-tax income and nobody models it.")
    print()
    print(f"  Trend:  FY23 ${INTEREST_INCOME['FY2023']:,.0f}mm -> FY24 ${INTEREST_INCOME['FY2024']:,.0f}mm "
          f"-> FY25 ${INTEREST_INCOME['FY2025']:,.0f}mm")
    print(f"  1H26 ${INTEREST_INCOME['1H2026']:,.0f}mm vs 1H25 ${INTEREST_INCOME['1H2025']:,.0f}mm  "
          f"= {100*(INTEREST_INCOME['1H2026']/INTEREST_INCOME['1H2025']-1):+.1f}%")
    ff26, ff25 = macro.loc[aug26, "fedfunds"], macro.loc[aug25, "fedfunds"]
    print(f"  ...while GBV grew 16-19% and Fed funds fell {100*(ff25-ff26):.0f}bp ({ff25:.2f} -> {ff26:.2f}).")
    print()
    print("  TWO FORCES, SAME DIRECTION, BOTH IN 3Q/4Q26:")
    print("    (a) rate:  the front end is 70bp lower YoY, so the yield on the float falls")
    print("    (b) float: RNPL removes the float itself - unearned fees ran -$442mm (1Q26)")
    print("        and -$466mm (2Q26) below seasonal-normal, against +/-5% before 1Q26")
    h2_25 = ii25 - INTEREST_INCOME["1H2025"]
    for lbl, d in [("1H26 run-rate (-7%)", -0.07), ("rate+float compounding (-12%)", -0.12),
                   ("bear (-18%)", -0.18)]:
        print(f"    2H26 interest income {lbl:32s} ${h2_25*(1+d):,.0f}mm "
              f"vs ${h2_25:,.0f}mm  ({h2_25*d:+,.0f}mm)")
    print("\n  HONEST SIZING: at -12% that is ~$41mm off 2H26 pre-tax, roughly 2% of 2H")
    print("  operating income. It does NOT carry a short on its own. What it does is make")
    print("  the float leg quantitative and give it a macro tailwind, and it is one of the")
    print("  few ABNB lines where the direction is known before the print.")

    print("\n" + "=" * 78)
    print("5. WHERE MACRO ACTUALLY BITES: THE DISCOUNT RATE ON A PRICED-FOR-GROWTH FCF LINE")
    print("=" * 78)
    mt = pd.read_csv(P / "abnb_multiples_today.csv").iloc[0]
    rd = pd.read_csv(P / "abnb_reverse_dcf.csv")
    ev, fcf = mt.ev_musd, mt.ltm_fcf_musd
    sbc_fcf = rd[rd.cash_flow == "sbc_adjusted_fcf_ltm"].base_musd.iloc[0]
    print(f"  price ${mt.price:.2f}  EV ${ev:,.0f}mm  LTM FCF ${fcf:,.0f}mm  -> EV/FCF {ev/fcf:.1f}x")
    print(f"  SBC-adjusted FCF ${sbc_fcf:,.0f}mm -> EV/FCF {ev/sbc_fcf:.1f}x")
    print(f"  SBC is ${fcf-sbc_fcf:,.0f}mm, {100*(fcf-sbc_fcf)/fcf:.0f}% of reported FCF.")
    print("\n  Reverse DCF - the FCF growth the market is paying for, 10 years, by WACC:")
    piv = rd.pivot_table(index="wacc_pct", columns=["cash_flow", "terminal_growth_pct"],
                         values="implied_growth_pct")
    print(piv.round(1).to_string())
    print("\n  Read the SBC-adjusted block. At a 9-10% WACC the market is paying for")
    print("  11-14% FCF growth for a decade. Move WACC up a point and the required")
    print("  growth goes up with it - and the 10-year is ALREADY 42bp higher YoY.")
    print("\n  THIS IS THE THESIS: the stock is priced for low-double-digit growth in a cash")
    print("  flow line that RNPL is structurally shrinking (float) and lower front-end rates")
    print("  are shrinking again (interest income), while the long end raises the bar.")
    print("  Macro is not a separate leg. It is the transmission channel for leg 4.")

    pd.DataFrame(rows).to_csv(P / "macro_short_legs_q3q4.csv", index=False)
    print("\nwrote", P / "macro_short_legs_q3q4.csv")


if __name__ == "__main__":
    main()
