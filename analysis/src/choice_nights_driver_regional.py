"""
REGIONAL nights model - one calibration per Airbnb reporting segment, on that region's own data.

Supersedes the aggregate treatment in choice_nights_driver_global.py. The four regions are not
variants of one market: 2025 ADR runs $255 in North America against $95 in LatAm, stay length is
FLAT in NA and FALLING 2.7%/yr in LatAm, and disclosed nights growth spans +2.6% to +18.4%. Since
the team forecasts ADR regionally, nights are now built the same way, so the two can be multiplied
region by region without a mix error.

EVIDENCE AVAILABLE PER REGION - the confidence gradient runs BACKWARDS to the growth:

  NORTH AMERICA   full segment choice model. Hotel side: STR/CoStar 1.3bn room nights, AHLA
                  business split, Hawaii+Vegas leisure party mix, CoStar demand and ADR forecasts.
                  Airbnb side: disclosed nights, revenue-share proxy for the U.S., 10-K stay length.
                  -> the only region where P(Airbnb | contestable) is actually calibrated.

  EMEA            hotel side MEASURED: Eurostat platform guest-nights (tour_ce_omr) and hotel
                  guest-nights (I551) for FR/ES/IT/DE, scaled to EMEA. Party size by accommodation
                  now also measured, from Spain's INE ETR microdata (11 years). Airbnb side:
                  disclosed nights, 10-K stay length (4.4 -> 3.8, the steepest decline of any region).

  LATIN AMERICA   Hotel side now PARTLY evidenced (latam_apac_hotel_evidence.py): Mexico's DATATUR
                  publishes average occupied rooms and occupancy, giving 170.4mm room-nights in
                  2025, +6.5%. Still no party-size-by-accommodation anywhere in the region, so no
                  P(Airbnb | contestable) can be calibrated - a market-growth anchor, not a model. What IS region-specific: disclosed nights
                  (+18.4% in 2025), ADR $94.91 (+1.7%, the weakest of the four), and stay length
                  falling fastest (-2.7%/yr, 4.4 -> 3.6 since 2020).

  ASIA PACIFIC    Hotel side now PARTLY evidenced: Japan's JTA Overnight Travel Statistics give
                  653.48mm guest-nights in 2025, -0.8% y/y (domestic -3.8%, international +8.2%).
                  Same limit as LatAm - a market-growth anchor, not a calibrated share. Japan is
                  not APAC though: Korea (+15.2% inbound), India (occupancy rising) and Australia
                  (flat) all point higher, and China barely matters since Airbnb exited domestic
                  China in 2022. Region-specific: disclosed nights (+14.8%),
                  ADR $118.20 (+1.2%), and the ONLY region where stay length is RISING (2.8 -> 3.3,
                  +18% since 2020). Japan's minpaku law caps a property at 180 nights/yr and lets
                  municipalities zero it out, so APAC supply has a legal ceiling the others lack.

  => LatAm + APAC are 30% of 2025 nights and ~62% of 2025-30 growth. They now have a hotel-side
     market anchor each (Mexico, Japan) but still no calibrated share. Brazil, China, India, Korea
     and Australia remain unpulled; Brazil matters most, being LatAm's largest Airbnb market.

ADR: regional ADR = regional GBV / regional nights from the FY2025 10-K regional table. This
INCLUDES FX, whereas the share equation wants an ex-FX comparison. Regional ex-FX paths should
replace ADR_GROWTH below as soon as the team's regional ADR line lands - flagged, not silently
assumed. Only NA and EMEA have a hotel ADR comparator, so only they run a price-driven share term.

Run:  python analysis/src/choice_nights_driver_regional.py
Out:  data/processed/choice_driver_regional_detail.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
sys.path.insert(0, str(ROOT / "analysis/src"))

import choice_nights_driver as us_model  # noqa: E402

YEARS = [2025, 2026, 2027, 2028, 2029, 2030]

# ---- 2025 anchors, all from the FY2025 10-K regional table (nights, GBV -> ADR) and MD&A stay length
ANCHOR = {
    "north_america": {"nights": 158.0, "adr": 255.03, "stay": 4.1, "nights_g25": 0.026},
    "emea":          {"nights": 215.0, "adr": 158.89, "stay": 3.8, "nights_g25": 0.070},
    "latam":         {"nights":  90.0, "adr":  94.91, "stay": 3.6, "nights_g25": 0.184},
    "apac":          {"nights":  70.0, "adr": 118.20, "stay": 3.3, "nights_g25": 0.148},
}

# ---- Own-category growth: implied by inverting the model identity on disclosed 2025 nights growth,
#      then faded. g_cat = (g_total - CONTESTABLE * g_contestable) / (1 - CONTESTABLE).
CATEGORY = {
    "north_america": {2026: 0.033, 2027: 0.032, 2028: 0.030, 2029: 0.029, 2030: 0.028},
    "emea":          {2026: 0.085, 2027: 0.078, 2028: 0.070, 2029: 0.063, 2030: 0.057},
    "latam":         {2026: 0.230, 2027: 0.200, 2028: 0.175, 2029: 0.155, 2030: 0.138},
    "apac":          {2026: 0.185, 2027: 0.165, 2028: 0.148, 2029: 0.133, 2030: 0.120},
}
# EMEA implied +10.3% is haircut to 8.5% for the WS11 regulatory drag; LatAm 27.3% and APAC 21.3%
# are haircut hard because a first-year implied rate off one year of data is not a trend.

# ---- Lodging-market growth for the contestable pool.
# NA and EMEA come from measured pools (CoStar/STR; Eurostat). LatAm and APAC were pure guesses
# until 8 Sep 2026, when latam_apac_hotel_evidence.py found the first hotel-side observations:
#   Mexico hotel room-nights +6.5% in 2025 (DATATUR: 438,624 -> 466,958 avg occupied rooms)
#   Japan  hotel guest-nights -0.8% in 2025 (JTA: 653.48mm, domestic -3.8%, international +8.2%)
# The two point in OPPOSITE directions and both away from the old guesses (3.0% / 3.5%):
#   LatAm  raised 3.0% -> 5.0%. Mexico says 6.5%, haircut because Mexico is not LatAm and one
#          year is not a trend. More market growth makes the LatAm path MORE robust: less of its
#          +18.4% has to be share gain.
#   APAC   cut 3.5% -> 2.0%. Japan's hotel nights fell 0.8%, but five-market evidence says Japan
#          is NOT representative: Korea inbound +15.2%, India occupancy rising, Australia roughly
#          flat, and China's falling star-rated occupancy is nearly irrelevant because Airbnb
#          exited domestic China in 2022. APAC growth is still mostly share gain - just not
#          entirely, as a Japan-only read implied.
MARKET = {"north_america": 0.015, "emea": 0.020, "latam": 0.050, "apac": 0.020}

# ---- ADR paths. NA/EMEA hotel comparators are real forecasts; LatAm/APAC have none.
ABNB_ADR = {  # PROVISIONAL - replace with the team's regional ex-FX line when it lands
    "north_america": 0.030, "emea": 0.028, "latam": 0.020, "apac": 0.018,
}
HOTEL_ADR = {"north_america": 0.025, "emea": 0.025, "latam": None, "apac": None}

# ---- Stay length: 10-K regional nights-per-booking. NA flat since 2023; EMEA and LatAm falling;
#      APAC the only riser. Paths fade each region's recent rate toward zero.
STAY_DRIFT = {"north_america": 0.000, "emea": -0.008, "latam": -0.015, "apac": +0.006}

CONTESTABLE = us_model.CONTESTABLE
SWITCH_RATE = us_model.SWITCH_RATE

# ---- NA CYCLICAL INBOUND RECOVERY, added 8 Sep 2026 to close a real gap against Krish's WS10.
# My structural drivers (category adoption, price, market growth) contain NO inbound-travel term,
# so the model produced US 2026 +2.9% against disclosed NA ACTUALS of +5% (4Q25) and +8% (1Q26,
# 2Q26) and Krish's base of +7%. Being below realised history is not a defensible forecast.
# What is actually happening (WS10, sourced): BEA inbound foreign travel in the US went -9.9% y/y
# in 3Q25 to -0.6% in Jul-2026; StatCan Canadian returns from the US went -31% mid-2025 to +1.8 /
# +9.9 / +5.0% in Apr/May/Jun-2026. Management called 2Q26 NA "the highest growth we've seen in
# almost three years". That is a CYCLICAL normalisation, not a new structural rate, so it is added
# as a fading term rather than folded into category growth - it must not compound past the recovery.
NA_INBOUND_RECOVERY = {2026: 0.035, 2027: 0.015, 2028: 0.005, 2029: 0.0, 2030: 0.0}

# ---- EMEA leisure party mix, from SPAIN INE ETR microdata (leisure trips only, n=7,633 weighted,
# 2022-26): solo 20 / pair 34 / 3-4 42 / 5+ 4, mean 2.57. Deliberately NOT used in the US model -
# transplanting a European mix into a US calibration is the error the Portuguese ledger already
# commits there - but for EMEA it is the right-continent source and beats Hawaii+Vegas outright.
EMEA_LEIS_PARTY = {"solo": 0.20, "pair": 0.34, "3-4": 0.42, "5+": 0.04}

# ---- SEASONALITY of NIGHTS BOOKED, from disclosed quarterly nights 2023-2025.
# NOTE THE DIRECTION, because the intuition runs the other way: Airbnb reports nights BOOKED at
# RESERVATION, not nights stayed. Q1 is when summer travel gets booked, so the booked metric peaks
# in Q1 and troughs in Q4 - every year, without exception - even though OCCUPANCY peaks in Q3.
# Index = quarter / that year's mean: 1Q 1.078, 2Q 1.018, 3Q 1.004, 4Q 0.900.
SEASONAL_INDEX = {"1Q": 1.078, "2Q": 1.018, "3Q": 1.004, "4Q": 0.900}

# ---- Revenue shares, FY2025 10-K. Used ONLY to show the revenue read-through: nights AGGREGATE by
# summing, so the total nights line is nights-weighted by construction. Revenue weights matter
# because LatAm+APAC are 31% of nights but only 18.9% of revenue - fast growth there is
# ADR-dilutive. (US is 39.3% of revenue, NA 42.4% - not 57%.)
REVENUE_SHARE = {"north_america": 0.424, "emea": 0.387, "latam": 0.094, "apac": 0.095}


def region_path(name):
    a = ANCHOR[name]
    N = (1 - CONTESTABLE) * a["nights"]
    M_pool = CONTESTABLE * a["nights"]
    P = 1.0  # contestable Airbnb / itself; the pool below carries the hotel side where known
    hotel_adr = HOTEL_ADR[name]
    out, sl = {2025: a["nights"]}, 1.0
    contestable = M_pool
    for y in YEARS[1:]:
        N *= (1 + CATEGORY[name][y])
        contestable *= (1 + MARKET[name])
        if name == "north_america":
            cyc = 1 + NA_INBOUND_RECOVERY[y]
            N *= cyc
            contestable *= cyc
        if hotel_adr is not None:
            dln = np.log(1 + ABNB_ADR[name]) - np.log(1 + hotel_adr)
            contestable *= np.exp(-SWITCH_RATE * dln * CONTESTABLE)  # share response, pool-scaled
        sl *= (1 + STAY_DRIFT[name])
        out[y] = (N + contestable) * sl
    return out


def main():
    paths = {r: region_path(r) for r in ANCHOR}
    df = pd.DataFrame({"year": YEARS, **{r: [paths[r][y] for y in YEARS] for r in ANCHOR}})
    df["total"] = df[list(ANCHOR)].sum(axis=1)

    print("REGIONAL NIGHTS (mm) - each region on its own data\n")
    print(df.round(1).to_string(index=False))
    g = df.set_index("year").pct_change() * 100
    print("\nGROWTH (%)")
    print(g.round(1).to_string())

    print("\nCAGR 2025-30, share of nights, and what each region is built on")
    basis = {"north_america": "full choice model (STR/AHLA/CoStar hotel side)",
             "emea": "measured Eurostat platform+hotel, Spain INE party size",
             "latam": "growth model + Mexico DATATUR market anchor (+6.5%)",
             "apac": "growth model + Japan JTA market anchor (-0.8%)"}
    rows = []
    for r in list(ANCHOR) + ["total"]:
        s = df.set_index("year")[r]
        c = (s.loc[2030] / s.loc[2025]) ** 0.2 - 1
        sh0, sh1 = s.loc[2025] / df.total.iloc[0], s.loc[2030] / df.total.iloc[-1]
        print(f"  {r:14s} {c * 100:+6.2f}%/yr  share {sh0 * 100:4.1f}% -> {sh1 * 100:4.1f}%   "
              f"{basis.get(r, 'sum')}")
        rows.append({"region": r, "nights_2025": s.loc[2025], "nights_2030": s.loc[2030],
                     "cagr": c, "share_2025": sh0, "share_2030": sh1,
                     "adr_2025": ANCHOR.get(r, {}).get("adr"), "basis": basis.get(r, "sum")})

    tot0, tot1 = df.total.iloc[0], df.total.iloc[-1]
    print(f"\nSHARE OF THE {(tot1 / tot0 - 1) * 100:.1f}% FIVE-YEAR GROWTH")
    evid = 0.0
    for r in ANCHOR:
        s = df.set_index("year")[r]
        part = (s.loc[2030] - s.loc[2025]) / (tot1 - tot0)
        print(f"  {r:14s} {part * 100:5.1f}%")
        if r in ("latam", "apac"):
            evid += part
    print(f"  => {evid * 100:.0f}% of all growth comes from the two regions with a market anchor")
    print("     but no calibrated share. Brazil is the highest-value remaining pull.")

    print("\nGBV CROSS-CHECK (nights x ADR, 2025) - ties to the disclosed regional table")
    for r in ANCHOR:
        print(f"  {r:14s} {ANCHOR[r]['nights'] * ANCHOR[r]['adr'] / 1000:6.2f}bn")

    # ---- Revenue read-through and guidance comparison
    print("\nREVENUE-WEIGHTED vs NIGHTS-WEIGHTED growth")
    print("  (nights aggregate by SUMMING, so the total nights line is nights-weighted by")
    print("   construction. Revenue weights show the read-through, and they differ a lot.)")
    g26 = {r: df.set_index("year")[r].loc[2026] / df.set_index("year")[r].loc[2025] - 1 for r in ANCHOR}
    nights_w = sum(g26[r] * (ANCHOR[r]["nights"] / 533.0) for r in ANCHOR)
    rev_w = sum(g26[r] * REVENUE_SHARE[r] for r in ANCHOR)
    print(f"    2026 nights-weighted  {nights_w * 100:+.1f}%   (= the total nights line)")
    print(f"    2026 revenue-weighted {rev_w * 100:+.1f}%   ({(rev_w - nights_w) * 100:+.1f}pp)")
    print("    Lower on revenue weights because LatAm+APAC are 31% of nights but 18.9% of revenue")
    print("    - the fast-growing regions are the low-ADR ones, so nights mix is ADR-dilutive.")

    print("\nSEASONALITY of NIGHTS BOOKED (2023-25 disclosed; index = quarter / year mean)")
    for q, v in SEASONAL_INDEX.items():
        print(f"    {q} {v:.3f}", end="")
    print("\n    Q1 is the BIGGEST quarter every year, Q4 the smallest. Airbnb books nights at")
    print("    RESERVATION, so the metric peaks when summer is booked (Q1), not when it is")
    print("    stayed (Q3). Occupancy peaks in Q3; the reported metric does not.")

    print("\nVS AIRBNB GUIDANCE AND VS KRISH (WS10/WS13)")
    print("  Airbnb does NOT guide a nights number. The 2Q26 letter (6 Aug 2026) guides 3Q26")
    print("  REVENUE $4.69-4.77bn (+15-17%) and describes nights only as 'low double-digit'.")
    print(f"    Airbnb guidance, 3Q26 nights   ~10-12% (qualitative)")
    print(f"    Krish WS10 base, 3Q26 nights   +10.3%   FY26 +9.9%, FY27 +8.9%")
    print(f"    this model, FY26               {nights_w * 100:+.1f}%   FY27 "
          f"{(df.set_index('year').total.loc[2027] / df.set_index('year').total.loc[2026] - 1) * 100:+.1f}%")
    print("  Still below both, and the residual is almost entirely North America: this model has")
    print("  a structural view (category adoption, price, mix) while Krish adds a cyclical inbound")
    print("  recovery that is measurably happening. The NA_INBOUND_RECOVERY term closes part of it")
    print("  (US 2026 +2.9% -> +5.8%) but deliberately not all: it fades to zero by 2029 because a")
    print("  normalisation cannot compound, whereas Krish's horizon stops before that matters.")

    pd.DataFrame(rows).to_csv(OUT / "choice_driver_regional_detail.csv", index=False)
    print("\nwrote", OUT / "choice_driver_regional_detail.csv")


if __name__ == "__main__":
    main()
