"""
SHORT-PITCH nights module, 3Q26 and 4Q26 only. An OVERLAY on the team's unified RNPL module.

Replaces my nights_simple.py, which the 11 Sep audit (docs/rnpl-short-audit/01_*.md, point 8)
found double-counted the team's work in two places:
  - my C(t) cancellation drag and Krish's propensity tail are THE SAME OBJECT. Carrying both
    double counts. Mine also came out ~2x too large because I put the RNPL share of bookings at
    50% in 2026 against a disclosure-consistent 16.7-18% OF NIGHTS.
  - my L(t) product-bundle level and PR #32's fitted +2.40 / +2.29 are also the same object.
So this file adds NO mechanism the team already models. It takes their module as the base and
applies only the two things that are genuinely a variant view.

WHY THE SHARE CONVERTS DOWN. Krish's measured RNPL share is of GBV, not nights: ~20% (1Q26),
21% (2Q26), both measured; 21-27% assumed forward. RNPL bookings carry 1.33x the ADR of non-RNPL
ones, so the NIGHTS share is lower:
        p = s / (r(1-s) + s),  r = 1.33
        s = 21% GBV  ->  p = 16.7% of nights
That conversion is the whole reason my 50% was wrong, and it is worth stating in the pitch because
it also means RNPL is disproportionately a HIGH-ADR product - which is why it flatters ADR while
it is growing and why the lap hurts ADR as well as nights.

THE TWO VARIANT VIEWS THIS FILE ADDS

  V1. RNPL SHARE RUNS ABOVE CONSENSUS. Krish assumes 21-27% of GBV from 3Q26. The thesis is that
      adoption keeps compounding - it went ~0 -> 20% of GBV in four quarters - so a 30-38% path is
      not aggressive. Because the propensity drag scales with share, a higher share mechanically
      deepens the cancellation tail. This is a scaling of m4, not a new mechanism.

  V2. THE WORLD CUP SUPPRESSED THE CANCELLATION RATE, AND THAT REVERSES. FIFA 2026 ran 11 Jun -
      19 Jul across 16 US/Canada/Mexico host cities: "millions of guests", 150k+ new listings,
      ~14% first-time users. Event travel is high-commitment - tickets, flights, fixed dates - so
      those bookings cancel far less than the platform average. They were BOOKED 4Q25-2Q26, which
      is exactly the window the Street is extrapolating the cancellation rate from. As that cohort
      washes out, aggregate cancellations revert UP on mix alone, before any RNPL effect. No team
      model carries this. It is the newest thing in the short and the least contested.

WHAT THIS IS NOT. It is not a level call on 3Q26 revenue: the forecast harness found that once
Airbnb has guided, guide midpoint x (1 + trailing-8 cushion) beats every method the team built.
The short is a SHAPE call on nights, and the audit is explicit that it is a LAP thesis first -
the cancellation drag is -0.3 to -0.9 points of 3Q26 while the lap plus ex-NA correction is
1.4 to 2.6 points by 4Q26. Pitch the lap; the cancellation work is the supporting leg.

Run:  python analysis/src/nights_short_q3q4.py
Out:  data/processed/nights_short_q3q4.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
MODULE = OUT / "rnpl_short_audit/rnpl_nights_module.csv"

ADR_RATIO = 1.33                       # RNPL / non-RNPL ADR, derived by the team
KRISH_GBV_SHARE = {"3Q26": 0.24, "4Q26": 0.27}      # midpoint of the assumed 21-27%
THESIS_GBV_SHARE = {"3Q26": 0.30, "4Q26": 0.38}     # V1: adoption keeps compounding
# V2: World Cup cohort washout. Share of 3Q26/4Q26 booked nights that were WC-era in the prior
# year's comp, x the cancellation-rate gap between event and normal travel.
# BOTH PARAMETERS ARE UNSOURCED JUDGMENT. Airbnb has never disclosed a cancellation rate by trip
# type and no third party publishes one for event travel. The DIRECTION is solid - event bookings
# are date-locked against tickets and flights, so they cancel less - but the magnitude is a guess.
# Sized deliberately small. Do not present these two numbers as measured; present the mechanism.
WC_COMP_SHARE = {"3Q26": 0.08, "4Q26": 0.03}
WC_CANCEL_GAP = 0.06                   # event bookings cancel ~6pp less than platform average
GUIDE_LOW, GUIDE_HIGH = 10.0, 12.0     # 3Q26 nights guide, "low double-digit"


def nights_share(s):
    return s / (ADR_RATIO * (1 - s) + s)


def main():
    if not MODULE.exists():
        raise SystemExit(f"team module not found at {MODULE}")
    m = pd.read_csv(MODULE)
    m = m[m.quarter.isin(["3Q26", "4Q26"])]

    print("TEAM UNIFIED MODULE (the base this overlays, not a rebuild)\n")
    print(m[["scenario", "quarter", "reference_growth_pct", "m1_level_lap_pts",
             "m2_pull_forward_pts", "m4_propensity_drag_pts", "nights_yoy_pct"]]
          .round(2).to_string(index=False))

    print("\nSHARE CONVERSION - why 50% of bookings was wrong")
    for q in ("3Q26", "4Q26"):
        k, t = KRISH_GBV_SHARE[q], THESIS_GBV_SHARE[q]
        print(f"  {q}  Krish {k:.0%} of GBV -> {nights_share(k):.1%} of nights   |   "
              f"thesis {t:.0%} of GBV -> {nights_share(t):.1%} of nights")

    rows = []
    base = m[m.scenario == "base"].set_index("quarter")
    print("\nOVERLAY ON THE BASE CASE (points of nights growth)\n")
    print(f"  {'':22s} {'3Q26':>9s} {'4Q26':>9s}")
    team = {q: base.loc[q, "nights_yoy_pct"] for q in ("3Q26", "4Q26")}
    print(f"  {'team module base':22s} {team['3Q26']:8.2f}% {team['4Q26']:8.2f}%")

    v1, v2, tot = {}, {}, {}
    for q in ("3Q26", "4Q26"):
        # V1: the propensity drag scales with the nights share
        scale = nights_share(THESIS_GBV_SHARE[q]) / nights_share(KRISH_GBV_SHARE[q])
        v1[q] = base.loc[q, "m4_propensity_drag_pts"] * (scale - 1)
        # V2: World Cup cohort washout, in points of growth
        v2[q] = -100 * WC_COMP_SHARE[q] * WC_CANCEL_GAP
        tot[q] = team[q] + v1[q] + v2[q]
    print(f"  {'V1 share above cons.':22s} {v1['3Q26']:8.2f}  {v1['4Q26']:8.2f} ")
    print(f"  {'V2 World Cup washout':22s} {v2['3Q26']:8.2f}  {v2['4Q26']:8.2f} ")
    print(f"  {'SHORT CASE':22s} {tot['3Q26']:8.2f}% {tot['4Q26']:8.2f}%")

    for q in ("3Q26", "4Q26"):
        rows.append({"quarter": q, "team_base_yoy_pct": round(team[q], 2),
                     "v1_share_pts": round(v1[q], 2), "v2_worldcup_pts": round(v2[q], 2),
                     "short_case_yoy_pct": round(tot[q], 2),
                     "krish_gbv_share": KRISH_GBV_SHARE[q], "thesis_gbv_share": THESIS_GBV_SHARE[q],
                     "krish_nights_share": round(nights_share(KRISH_GBV_SHARE[q]), 4),
                     "thesis_nights_share": round(nights_share(THESIS_GBV_SHARE[q]), 4)})

    print(f"\nVS THE GUIDE. Airbnb guides 3Q26 nights at {GUIDE_LOW:.0f}-{GUIDE_HIGH:.0f}% "
          f"('low double-digit'), midpoint {(GUIDE_LOW + GUIDE_HIGH) / 2:.0f}%.")
    print(f"  short case 3Q26 {tot['3Q26']:.2f}% is {(GUIDE_LOW + GUIDE_HIGH) / 2 - tot['3Q26']:.2f} "
          f"points below the guide midpoint and {GUIDE_LOW - tot['3Q26']:.2f} below the bottom.")
    print(f"  short case 4Q26 {tot['4Q26']:.2f}% against a team base of {team['4Q26']:.2f}%.")
    print("""
  CAUTION, and it decides how this is pitched: Airbnb has BEATEN the top of its own nights range
  both times it gave one (4Q25 guided 4-6%, printed 9.82%; 1Q26 guided 7-9%, printed 9.15%). A
  short that needs them to miss a guide they habitually beat is the wrong trade. The team's own
  read is to short the FEBRUARY shape - the 1Q27 guide against a +17.9% comp - not the 5 Nov print.
  These Q3/Q4 numbers are the setup for that, not the trade itself.
""")
    pd.DataFrame(rows).to_csv(OUT / "nights_short_q3q4.csv", index=False)
    print("wrote", OUT / "nights_short_q3q4.csv")


if __name__ == "__main__":
    main()
