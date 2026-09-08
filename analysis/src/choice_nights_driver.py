"""
Choice-probability nights driver for the ABNB revenue model.

Today:  Revenue = Nights x ADR x take rate x FX, with Nights a growth plug.
Here:   Nights_ABNB(t) = SUM_g [ N_g(t) + M_g(t) x P_g(t) ]
        N_g = "own-category" Airbnb nights that would NOT have gone to a hotel anyway
              (62% of Airbnb guests, Farronato & Fradkin survey) - grows with category adoption
        M_g = hotel-contestable lodging demand (party-nights) in segment g = hotel + contestable Airbnb
        P_g = probability a hotel-contestable party in segment g picks Airbnb (share of the pool)
        segments g = party size {solo, pair, 3-4, 5+}; solo carries the business-travel pool.

Base-year (2025, U.S.) calibration:
  Airbnb nights by segment  = U.S. nights x booking share_g x relative stay length_g
  Hotel party-nights by seg = room nights split business/leisure (AHLA), leisure parties by
                              size (Hawaii/Vegas), rooms per party, nights per stay (Kalibri)
  P_g(2025) = contestable Airbnb_g / (contestable Airbnb_g + Hotel_g); own-category = 62% of Airbnb_g

Projection:
  M_g(t)  = M_g(t-1) x (1 + market growth) x (1 + segment mix drift_g)
  logit P_g(t) = logit P_g(t-1) - SWITCH_RATE x dln(relative price_g) + product/regulation shift_g
      relative price_g = Airbnb all-in cost / hotel cost for a party of size g
      SWITCH_RATE = share sensitivity to relative price (central 5.0, grid 2.5-10.3; see note)
  Revenue = Nights x ADR x take rate x FX  (unchanged - plug Nights into the existing model)

Run:  python analysis/src/choice_nights_driver.py
Out:  data/processed/choice_driver_calibration_2025.csv
      data/processed/choice_driver_projection.csv
      data/processed/choice_driver_sensitivity.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
SEG = ["solo", "pair", "3-4", "5+"]

# ---------------- Inputs (every number sourced in research/notes/choice_nights_driver.md) ----------------
NA_NIGHTS_2025 = 158.0            # mm, Airbnb FY2025 10-K regional table
US_SHARE_OF_NA = 0.92             # U.S. = 39% of revenue ($4.76B) / NA revenue $5.196B, FY2025 10-K
NPB_NA = 4.1                      # nights per booking, North America, FY2025 10-K
BOOK_SHARE = {"solo": 0.16, "pair": 0.358, "3-4": 0.323, "5+": 0.159}   # fitted party-size distribution
REL_LEN = {"solo": 1.5, "pair": 0.95, "3-4": 0.9, "5+": 0.8}            # relative stay length (solo 24% nights / 16% bookings; Inside Airbnb by capacity)

US_HOTEL_ROOM_NIGHTS_2025 = 1300 * 1.01   # mm; 1.3B sold in 2024 (STR/CoStar) x ~+1% 2025
BUSINESS_SHARE = 439 / (439 + 605)        # AHLA 2024 SOTI, 2023 room nights
# KNOWN LIMITATION: Marriott's FY2025 mix is ~30% business transient / ~25% group-meetings / ~45%
# leisure. Group blocks are contracted demand with ~no Airbnb overlap, yet this model folds them
# into the leisure pool, where they land disproportionately in the 3-4/5+ segments (highest P_g).
# Base-year P_g self-corrects (contestable Airbnb is pinned), but market growth and mix drift are
# then applied to a pool ~25% of which cannot switch. Fix = a third, inert "group" bucket.
CORP_SOLO = 0.795                         # corporate bookings single-occupancy (Portuguese ledger)
HOTEL_ALOS = 2.1                          # Kalibri Labs
LEIS_PARTY = {"solo": 0.20, "pair": 0.54, "3-4": 0.20, "5+": 0.06}     # leisure hotel parties: mean of Hawaii hotel-only & Las Vegas 2024
LEIS_NIGHTS_REL = {"solo": 0.7, "pair": 1.0, "3-4": 1.0, "5+": 1.0}    # Portuguese ledger: solo 2.5 vs 3.6 nights
ROOMS_PER_PARTY = {"solo": 1.0, "pair": 1.0, "3-4": 1.5, "5+": 2.5}

# Descriptive only - carried into the calibration output for context; no equation reads it.
# Corrected 7 Sep 2026: the Jun-2026 Inside Airbnb `price` is already a fee-inclusive stay quote,
# so the old values had the 14% guest fee counted twice and were 12.3% too high
# (0.69 / 1.22 / 0.80 / 0.79). See analysis/src/party_size_crossover.py.
PRICE_RATIO_2025 = {"solo": 0.54, "pair": 1.03, "3-4": 0.69, "5+": 0.71}  # guest-quoted Airbnb / hotel rooms x ADR, party_size_cost_crossover.csv
CONTESTABLE = 0.38                # share of Airbnb guests who would have gone to a hotel absent Airbnb (F&F: 62% would not)

# SWITCH RATE (called beta in the econometrics literature - renamed 7 Sep 2026 because 'beta'
# collides with equity beta in a pitch context): the logit share sensitivity to ln(relative
# price) - how strongly a price gap pushes contestable travelers between Airbnb and hotels.
# Anchored on Farronato & Fradkin (AER 2022)
# online Appendix Table E9 ("Demand Cross-Price Elasticities by Accommodation Type", p.30), which gives
# the cross-price elasticity of Airbnb demand w.r.t. each of 6 hotel tiers. Summed across the hotel
# tiers, a uniform +1% move in all hotel prices raises Airbnb demand by 3.72-3.85% (avg 3.76).
# This model's analogue is  d ln(Nights_ABNB) / d ln(p_hotel) = CONTESTABLE * SWITCH_RATE * (1 - P),
# so reproducing F&F exactly would need SWITCH_RATE = 3.76 / (0.38 * 0.955) = 10.3.
# We discount that to a national annual figure for three reasons, all pushing the same way:
#   1. F&F's sample is 10 dense US cities (Austin, Boston, LA, Miami, NY, Oakland, Portland, SF,
#      San Jose, Seattle) - precisely where Airbnb/hotel overlap is highest.
#   2. Their elasticities are tier-level; category-level (all Airbnb vs all hotels) is always lower.
#   3. Their market is a city-night in 2014; annual national aggregates smooth much of the response.
# Central 5.0 sits roughly half way in log terms between the old unsupported 2.5 and the F&F-implied
# 10.3. The grid below spans 2.5 (bull floor) to 10.3 (F&F-matched ceiling).
SWITCH_RATE = 5.0
SWITCH_RATE_GRID = [2.5, 5.0, 7.0, 10.3]
FF_CROSS_PRICE_ELASTICITY = 3.76  # F&F Table E9, avg over the 4 Airbnb tiers, summed over 6 hotel tiers
# Own-category (N) growth - GROUNDED 7 Sep 2026 (data/processed/category_adoption_evidence.csv):
# inverting this model's identity on disclosed NA nights (146->154->158mm, FY23-25 10-Ks) gives
# implied own-category growth of 7.9% (2024) -> 4.5% (2025). The 4% entry below matches the
# observed 2025 exit rate; the fade to 3% extends the observed 2024->2025 deceleration.
# EMEA's implied rate is ~10% - see choice_nights_driver_global.py.
CATEGORY_GROWTH = {2026: 0.04, 2027: 0.04, 2028: 0.035, 2029: 0.035, 2030: 0.03}

# Market / price paths (edit these)
YEARS = [2025, 2026, 2027, 2028, 2029, 2030]
MARKET_GROWTH = {2026: 0.017, 2027: 0.011, 2028: 0.015, 2029: 0.015, 2030: 0.015}   # CoStar/TE U.S. demand +1.7% 2026, +1.1% 2027; 1.5% thereafter (assumption)
MIX_DRIFT = {"solo": -0.01, "pair": 0.0, "3-4": 0.02, "5+": 0.04}   # family nights +15% vs Airbnb +8-10%; bedroom nights +12% vs nights +10%
# Cohort support for MIX_DRIFT (Alchemer 2026, n=1,014): planned lodging next 12 months is
# "mostly rentals" 37% vs "mostly hotels" 29% for under-30s, but 11% vs 64% for 61+.
# Cohort replacement therefore pushes the contestable pool toward rental-leaning, larger parties;
# the same survey cautions the young cohort is fickle (39% "very likely" to rebook).
HOTEL_ADR_GROWTH = {2026: 0.031, 2027: 0.016, 2028: 0.025, 2029: 0.025, 2030: 0.025}  # CoStar/TE
# Airbnb ADR - WIRED TO THE TEAM MODEL 7 Sep 2026 (model/assumptions.md, overnight WS13 base case):
# ADR ex-FX +3.0% 2H26 (1H26 actual +4% -> FY26 blends ~+3.5%), FY27/FY28 +2.5%; held at +2.5%
# for 2029-30. Ex-FX is the right basis here: the share equation compares US price competitiveness,
# and FX moves reported ADR, not the relative price a US traveler faces. This replaces the +5%/+3%
# placeholder (which used FY25's FX-flattered print) and NARROWS the ADR gap vs hotels - the prior
# path overstated share loss. Bear/bull ADR paths in assumptions.md: +2.0% / +4.0% 2H26.
ABNB_ADR_GROWTH = {2026: 0.035, 2027: 0.025, 2028: 0.025, 2029: 0.025, 2030: 0.025}
PRODUCT_SHIFT = {"solo": 0.0, "pair": 0.0, "3-4": 0.0, "5+": 0.0}   # logit points per year for product / regulation (0 = none)
# Evidence this lever is real but two-sided (Upgraded Points Oct-25 n=2,193; Alchemer Jun-26 n=1,014):
#   up:   64% believe hotels are cheaper while Airbnb was cheaper in 71 of 100 largest US cities, and
#         76% think hotels are more price-transparent -> fixable perception gap; 55% of Airbnb hotel
#         bookers return to book a home within 365 days (Q1'26); rental-guest NPS 50.9 vs hotels 41.8.
#   down: 63% have abandoned an Airbnb booking over cleaning fees/checkout chores; 61-64% back city
#         caps on STRs (highest among the rental-leaning young cohort) -> regulation enters here too.
REST_OF_WORLD_NIGHTS_GROWTH = 0.10   # EMEA/LatAm/APAC nights: apply the team's own assumption; 10% placeholder


def logit(p):
    return np.log(p / (1 - p))


def inv_logit(x):
    return 1 / (1 + np.exp(-x))


def calibrate():
    us_nights = NA_NIGHTS_2025 * US_SHARE_OF_NA
    w = {g: BOOK_SHARE[g] * REL_LEN[g] for g in SEG}
    tot = sum(w.values())
    abnb = {g: us_nights * w[g] / tot for g in SEG}

    biz = US_HOTEL_ROOM_NIGHTS_2025 * BUSINESS_SHARE
    leis = US_HOTEL_ROOM_NIGHTS_2025 - biz
    # leisure: party-nights_g = N x share_g x nights_g ; room-nights = SUM party-nights_g x rooms_g
    unit = sum(LEIS_PARTY[g] * LEIS_NIGHTS_REL[g] * ROOMS_PER_PARTY[g] for g in SEG)
    N = leis / unit
    hotel = {g: N * LEIS_PARTY[g] * LEIS_NIGHTS_REL[g] for g in SEG}
    hotel["solo"] += biz * CORP_SOLO
    hotel["pair"] += biz * (1 - CORP_SOLO)
    rows = []
    for g in SEG:
        c = abnb[g] * CONTESTABLE
        rows.append({"segment": g, "airbnb_nights_mm": abnb[g], "airbnb_own_category_mm": abnb[g] - c,
                     "airbnb_contestable_mm": c, "hotel_party_nights_mm": hotel[g],
                     "contestable_pool_mm": c + hotel[g], "p_airbnb_in_pool": c / (c + hotel[g]),
                     "airbnb_share_all_lodging": abnb[g] / (abnb[g] + hotel[g]),
                     "price_ratio_airbnb_over_hotel": PRICE_RATIO_2025[g]})
    cal = pd.DataFrame(rows)
    t = cal.sum(numeric_only=True)
    cal.loc[len(cal)] = {"segment": "TOTAL", "airbnb_nights_mm": t.airbnb_nights_mm, "airbnb_own_category_mm": t.airbnb_own_category_mm,
                         "airbnb_contestable_mm": t.airbnb_contestable_mm, "hotel_party_nights_mm": t.hotel_party_nights_mm,
                         "contestable_pool_mm": t.contestable_pool_mm, "p_airbnb_in_pool": t.airbnb_contestable_mm / t.contestable_pool_mm,
                         "airbnb_share_all_lodging": t.airbnb_nights_mm / (t.airbnb_nights_mm + t.hotel_party_nights_mm),
                         "price_ratio_airbnb_over_hotel": np.nan}
    return cal


def project(cal, switch_rate=SWITCH_RATE, abnb_adr=ABNB_ADR_GROWTH, hotel_adr=HOTEL_ADR_GROWTH, mix=MIX_DRIFT,
            mkt=MARKET_GROWTH, shift=PRODUCT_SHIFT, cat=CATEGORY_GROWTH):
    base = cal[cal.segment != "TOTAL"].set_index("segment")
    M = base.contestable_pool_mm.to_dict()
    P = base.p_airbnb_in_pool.to_dict()
    N = base.airbnb_own_category_mm.to_dict()
    tot = lambda: sum(N[g] + M[g] * P[g] for g in SEG)
    rows = [{"year": 2025, **{f"M_{g}": M[g] for g in SEG}, **{f"P_{g}": P[g] for g in SEG},
             **{f"N_{g}": N[g] for g in SEG}, "us_nights_mm": tot()}]
    dec = []
    for y in YEARS[1:]:
        prev = tot()
        dln_price = np.log(1 + abnb_adr[y]) - np.log(1 + hotel_adr[y])
        # step 1: market growth on the contestable pool
        M1 = {g: M[g] * (1 + mkt[y]) for g in SEG}
        s_market = sum(N[g] + M1[g] * P[g] for g in SEG)
        # step 2: segment mix drift (both pools)
        M2 = {g: M1[g] * (1 + mix[g]) for g in SEG}
        N2 = {g: N[g] * (1 + mix[g]) for g in SEG}
        s_mix = sum(N2[g] + M2[g] * P[g] for g in SEG)
        # step 3: category adoption on own-category nights
        N3 = {g: N2[g] * (1 + cat[y]) for g in SEG}
        s_cat = sum(N3[g] + M2[g] * P[g] for g in SEG)
        # step 4: share shift from relative price + product
        # `shift` is either {segment: logit pts} applied EVERY year (a permanent annual share gain)
        # or {year: {segment: logit pts}} for one-off launches. A product launch is a level effect:
        # it lifts share in the year it lands and then laps, so it belongs in the second form. The
        # first form silently compounds a launch into perpetuity - see na_nights_reconciliation.py.
        shift_y = shift.get(y, {}) if set(shift) & set(YEARS) else shift
        P4 = {g: inv_logit(logit(P[g]) - switch_rate * dln_price + shift_y.get(g, 0.0)) for g in SEG}
        s_share = sum(N3[g] + M2[g] * P4[g] for g in SEG)
        M, N, P = M2, N3, P4
        rows.append({"year": y, **{f"M_{g}": M[g] for g in SEG}, **{f"P_{g}": P[g] for g in SEG},
                     **{f"N_{g}": N[g] for g in SEG}, "us_nights_mm": s_share})
        dec.append({"year": y, "market_pts": s_market / prev - 1, "mix_pts": (s_mix - s_market) / prev,
                    "category_pts": (s_cat - s_mix) / prev, "share_pts": (s_share - s_cat) / prev,
                    "total": s_share / prev - 1})
    df = pd.DataFrame(rows)
    df["us_nights_growth"] = df.us_nights_mm.pct_change()
    return df, pd.DataFrame(dec)


def main():
    cal = calibrate()
    print(cal.round(3).to_string(index=False))
    df, dec = project(cal)
    print("\n", df[["year", "us_nights_mm", "us_nights_growth"] + [f"P_{g}" for g in SEG]].round(3).to_string(index=False))
    print("\n", dec.round(4).to_string(index=False))
    cal.to_csv(OUT / "choice_driver_calibration_2025.csv", index=False)
    df.merge(dec, on="year", how="left").to_csv(OUT / "choice_driver_projection.csv", index=False)

    # sensitivity: 2030 U.S. nights vs beta and Airbnb ADR premium growth
    # Diagnostic: what cross-price elasticity does each beta imply, vs F&F Table E9's 3.76?
    p_pool = cal.loc[cal.segment == "TOTAL", "p_airbnb_in_pool"].iloc[0]
    print("\nswitch rate -> implied d ln(ABNB nights)/d ln(hotel price)   [F&F Table E9 = %.2f]" % FF_CROSS_PRICE_ELASTICITY)
    for b in SWITCH_RATE_GRID:
        print("  switch rate %5.2f -> %.2f" % (b, CONTESTABLE * b * (1 - p_pool)))

    sens = []
    for b in SWITCH_RATE_GRID:
        for prem in [-0.02, 0.0, 0.02, 0.04]:  # Airbnb ADR growth minus hotel ADR growth, per year
            adr = {y: HOTEL_ADR_GROWTH[y] + prem for y in YEARS[1:]}
            d, _ = project(cal, switch_rate=b, abnb_adr=adr)
            sens.append({"switch_rate": b, "abnb_adr_premium_growth": prem, "us_nights_2030_mm": d.us_nights_mm.iloc[-1],
                         "cagr_2025_30": (d.us_nights_mm.iloc[-1] / d.us_nights_mm.iloc[0]) ** (1 / 5) - 1,
                         "implied_cross_price_elasticity": CONTESTABLE * b * (1 - p_pool),
                         "airbnb_share_of_pool_2030": sum(d[f"M_{g}"].iloc[-1] * d[f"P_{g}"].iloc[-1] for g in SEG) / sum(d[f"M_{g}"].iloc[-1] for g in SEG)})
    sens = pd.DataFrame(sens)
    print("\n", sens.round(4).to_string(index=False))
    sens.to_csv(OUT / "choice_driver_sensitivity.csv", index=False)


if __name__ == "__main__":
    main()
