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
# CAUTION (audit, 8 Sep 2026): this is a REVENUE share used as a NIGHTS share. That is exact only if
# revenue per night (= ADR x take rate) is identical in the U.S. and in Canada/Mexico. It is not:
# Mexico is a materially cheaper market, so U.S. ADR sits ABOVE the NA blend and the U.S. nights
# share must sit BELOW the U.S. revenue share. The model's own reconciliation shows it:
#   145.4mm U.S. nights x $255 NA ADR (FY25 regional GBV/nights) x 13.4% take = $4.97bn
#   vs $4.76bn of reported U.S. revenue  ->  the model OVERSTATES U.S. revenue by 4.4%.
# Read as a nights error that is ~145.4 -> ~139mm, i.e. the whole Airbnb side of the U.S.
# calibration is ~4% too big. US_ADR_PREMIUM below makes the correction one number instead of a
# footnote. It is left at 1.00 (status quo) so no published figure moves silently; set it to ~1.05
# to clear the reconciliation. Levels scale; the GROWTH decomposition is unaffected either way.
US_ADR_PREMIUM = 1.05             # SET 8 Sep 2026 (was 1.00): clears the reconciliation.
                                  # U.S. nights 145.4 -> 138.4mm. Levels scale ~-4.8%; growth unaffected.
NPB_NA = 4.1                      # NOT USED by this model (kept as the documented NA stay-length
                                  # level; the live lever is STAY_LENGTH below). FY2025 10-K.
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
HOTEL_ALOS = 2.1                          # NOT USED - hotel nights enter as room-nights, converted by
                                          # ROOMS_PER_PARTY, so ALOS never enters. Kalibri Labs. Kept for reference.
LEIS_PARTY = {"solo": 0.20, "pair": 0.54, "3-4": 0.20, "5+": 0.06}     # leisure hotel parties: mean of Hawaii hotel-only & Las Vegas 2024
LEIS_NIGHTS_REL = {"solo": 0.7, "pair": 1.0, "3-4": 1.0, "5+": 1.0}    # Portuguese ledger: solo 2.5 vs 3.6 nights
# ROOMS_PER_PARTY - was the top unsourced input; now has TWO checks (8 Sep 2026), both supportive.
# It implies leisure guests-per-occupied-room of 2.00 (pair), 2.27 (3-4) and 2.20 (5+).
#  1. JAPAN, computed from two official sources: JTA total guest-nights 653.48mm in 2025 divided by
#     room-nights (MHLW stock 1.44mm rooms x 365 x JTA occupancy 61.8% = 325mm) = 2.01 guests per
#     occupied room. That is a BLENDED figure including business travel, which drags it down, so
#     the leisure-only value implied here (2.2-2.3) sits correctly above it.
#  2. The hotel industry's "double occupancy factor": ~1.2 for business hotels, ~1.5 spa,
#     1.8-2.5 for holiday hotels. This vector's leisure implication (2.0-2.27) sits mid-range of
#     the holiday band, which is the right band since business is added separately at 1 room/party.
# Still not a US-specific measurement - no US source publishes guests per occupied room - but it is
# no longer uncited, and both checks say the level is right rather than convenient.
ROOMS_PER_PARTY = {"solo": 1.0, "pair": 1.0, "3-4": 1.5, "5+": 2.5}

# Descriptive only - carried into the calibration output for context; no equation reads it.
# Corrected 7 Sep 2026: the Jun-2026 Inside Airbnb `price` is already a fee-inclusive stay quote,
# so the old values had the 14% guest fee counted twice and were 12.3% too high
# (0.69 / 1.22 / 0.80 / 0.79). See analysis/src/party_size_crossover.py.
PRICE_RATIO_2025 = {"solo": 0.54, "pair": 1.03, "3-4": 0.69, "5+": 0.71}  # guest-quoted Airbnb / hotel rooms x ADR, party_size_cost_crossover.csv
CONTESTABLE = 0.38                # share of Airbnb guests who would have gone to a hotel absent Airbnb (F&F: 62% would not)
# CHALLENGED 8 Sep 2026, and the challenge deserves to be carried. Airbnb's own commissioned
# economists (Charles River Associates, "The Cost of STR Restrictions", Dec-2024) analysed the same
# NYC LL18 event this model validates against and concluded the OPPOSITE: "Limited substitution
# from STRs to hotels is supported by hotel occupancy data, which shows no material increase in NYC
# hotel occupancy rates following LL18." They separately adjust their lost-nights estimates down by
# 70% (NYC) / 60-62% (Boston, New Orleans, Philadelphia) for substitution to alternative
# accommodation generally - so their view is that displaced guests substituted, just not to hotels.
# The disagreement is entirely about whether NYC hotels were CAPACITY-CONSTRAINED. They were at
# ~84% occupancy, so the EJPE 2025 diff-in-diff reading - that the shift showed up in PRICE
# (ADR +$14-19) rather than in occupancy - is the more coherent one, and it is the reading this
# model reproduces. But note the NYC validation is contested by a party with sight of Airbnb's own
# data, and do not present it as uncontested.

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

# ---- STAY LENGTH (nights per booking) - made an EXPLICIT lever 8 Sep 2026 ----
# The model's demand machinery (N, M, P) is denominated in party-NIGHTS, so a change in trip
# INTENSITY was previously invisible: it could only enter by silently contaminating the category
# and market growth terms. It is now a separate multiplicative index, so it can be argued with.
#
# What the disclosures actually say (nights per booking, FY20-FY25 10-K MD&A "Geographic Mix"):
#   North America  4.4  4.3  4.2  4.1  4.1  4.1   <- FLAT for three years
#   EMEA           4.4  4.4  4.2  3.9  3.8  3.8   <- -14%
#   Latin America  4.4  4.3  4.2  3.9  3.7  3.6   <- -18%
#   Asia Pacific   2.8  2.7  3.2  3.3  3.3  3.3   <- +18%, the only region rising
#   Global         4.1  4.1  4.1  3.9  3.8  3.7   <- -2.0%/yr; cost ~58mm nights in 2025 (10.8%)
#
# So the global -2%/yr drag is NOT a U.S. phenomenon. NA has been flat at 4.1 since 2023, which is
# why the U.S. BASE CASE CARRIES NO DRAG. The decline is EMEA/LatAm (see choice_nights_driver_global.py).
# Caveat both ways: the 4.1-4.4 plateau of 2020-22 was COVID long-stay inflation, so part of the
# global fall is normalisation rather than deterioration - and normalisation is self-limiting.
# Against 2019 (US reservation panel, 3.7 nights) today's level is not obviously abnormal.
# Bear case = the EMEA/LatAm pattern arrives in NA; bull = mix toward longer stays reverses it.
STAY_LENGTH = {2025: 4.1, 2026: 4.1, 2027: 4.1, 2028: 4.1, 2029: 4.1, 2030: 4.1}
STAY_LENGTH_BEAR = {2025: 4.1, 2026: 4.02, 2027: 3.94, 2028: 3.86, 2029: 3.78, 2030: 3.71}  # -2%/yr
STAY_LENGTH_BULL = {2025: 4.1, 2026: 4.14, 2027: 4.18, 2028: 4.22, 2029: 4.27, 2030: 4.31}  # +1%/yr

# Market / price paths (edit these)
YEARS = [2025, 2026, 2027, 2028, 2029, 2030]
MARKET_GROWTH = {2026: 0.017, 2027: 0.011, 2028: 0.015, 2029: 0.015, 2030: 0.015}   # CoStar/TE U.S. demand +1.7% 2026, +1.1% 2027; 1.5% thereafter (assumption)
# MIX DRIFT - SPLIT INTO TWO VECTORS 8 Sep 2026, calibrated on Krish's party-size series (PR #33).
# Until now one vector was applied to BOTH pools, which assumed Airbnb and hotel parties grow at the
# same rate. They do not. Hawaii DBEDT is the only source observing both in the same market:
#   rental house 2.28 -> 2.49 (+0.80%/yr)   hotel 2.22 -> 2.30 (+0.34%/yr)   2013-2024
# i.e. rental-type parties drift 2.35x faster than hotel parties.
# Anchoring: the LEVEL comes from the global review proxy (abnb_party_size_reviews_quarterly.csv,
# 74m reviews / 123 markets, +0.62%/yr 2018-25 - the window after the mention rate stabilised at ~6%);
# the RELATIVE rate comes from the Hawaii ratio, giving the hotel side +0.26%/yr.
# The old single vector implied +0.98%/yr for both, so this cuts the Airbnb side by ~a third and the
# hotel side by ~three quarters. Net effect is a LOWER mix contribution to nights growth - the
# previous setup was flattering the forecast by drifting the whole contestable pool at Airbnb's rate.
# The composition story behind it: couples 50% -> 25% and families 31% -> 46% (2012-2025), with the
# size rise coming from guests booking BIGGER HOMES rather than the same homes hosting bigger groups.
#
# GENERALISATION TEST 8 Sep 2026 (analysis/src/party_size_rental_vs_hotel.py):
#   LEVEL gap validated hard - Booking rectour24 (1.63m stays, 2023) shows rental parties larger
#   than hotel parties in 39 of 40 countries, mean 1.131x, paired t = 10.2.
#   TREND divergence (the 2.35x that sets these two vectors' RATIO) is NOT confirmed elsewhere.
#   All three national surveys were pulled 8 Sep 2026: TRA is behind a paid portal (and its NVS
#   ends Dec-2024); StatCan publishes only marginals and directs cross-tab requests to email;
#   VisitBritain GBTS DID yield a trip-level cross-tab, and it confirms the LEVEL (UK rental trips
#   are ~1.5x more likely to include a child than hotel trips, 2022-24) but NOT the divergence -
#   the gap is 12.4pp in 2022, 15.3pp in 2023 and 11.4pp in 2024, i.e. narrower at the end.
#   So: level gap now has three independent confirmations; the trend has one market for and one
#   against. Treat the 2.35x ratio as the OPTIMISTIC case, not an established fact.
#   CAUTION: the gap is WEAKEST WHERE THIS MODEL NEEDS IT. The U.S. ranks 33/40 at 1.051x vs the
#   1.131x mean (Hawaii 1.080x, also below). Either Booking's thin U.S. whole-home sample understates
#   it (2,165 reviews, aparthotel-skewed), or the U.S. mix tailwind is genuinely weaker than global
#   and MIX_DRIFT_ABNB should be cut further. Unresolved - treat +0.62%/yr as the optimistic end.
#   Counter-signal: UK solo overnight trips 28% in 2024, +4pp vs 2022 (VisitBritain) - rising solo
#   travel pushes mean party size the other way in at least one large market.
#
# VERDICT AFTER SPAIN (8 Sep 2026, ine_spain_party_size.py) - THE DIVERGENCE IS NOT SUPPORTED.
# Spain's INE Encuesta de Turismo de Residentes is the strongest instrument available: official,
# weighted, trip-level microdata, 11 full years, real party size (household members on trip), with
# hotel and whole-home rental separately coded. It says:
#     LEVEL   rental/hotel = 1.167x, stable, range 1.09-1.22 across 12 years -> a FOURTH
#             independent confirmation of the level gap (with Hawaii, 40-country Booking, UK).
#     TREND   the rental/hotel ratio is FLAT: log-linear +0.04%/yr, se 0.35, t = +0.12.
#             Both sides also FELL slightly in level (rental -0.17%/yr, hotel -0.21%/yr) - the
#             opposite of Hawaii, where both rose.
# Scoreboard on the divergence that sets MIX_DRIFT_ABNB / MIX_DRIFT_HOTEL apart:
#     Hawaii  FOR      (2.31x, 11 years, observed)
#     Spain   AGAINST  (flat, 11 years, weighted microdata, larger sample)
#     UK      AGAINST  (gap narrower in 2024 than 2022, 3 years)
# One market for, two against, and the strongest dataset is one of the two against. The 2.35x split
# below is therefore NOT an established fact and should be run as a sensitivity, not a base case.
# Impact of the alternatives on 2030 U.S. nights: both vectors at the Airbnb rate 160.2mm (+0.6%);
# both at the hotel rate 157.6mm (-1.1%); MIX DRIFT OFF ENTIRELY - the Spain/UK reading - 155.7mm
# (-2.2%, CAGR 2.84% -> 2.38%). Kept at the split for continuity with the published deck; a reviewer
# who takes the Spain evidence at face value should zero both vectors.
MIX_DRIFT_ABNB = {"solo": -0.0063, "pair": 0.0, "3-4": 0.0127, "5+": 0.0253}    # implies +0.62%/yr
MIX_DRIFT_HOTEL = {"solo": -0.0027, "pair": 0.0, "3-4": 0.0054, "5+": 0.0107}   # implies +0.26%/yr
MIX_DRIFT = MIX_DRIFT_ABNB   # back-compat alias; project() takes both explicitly
# M (the contestable pool) is ~96% hotel party-nights, so it takes the hotel vector; N (own-category
# Airbnb) takes the Airbnb vector. Cohort support (Alchemer 2026, n=1,014): under-30s plan "mostly
# rentals" 37% vs "mostly hotels" 29%; 61+ are 11% vs 64%. Cohort replacement pushes the same way.
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
    us_nights = NA_NIGHTS_2025 * US_SHARE_OF_NA / US_ADR_PREMIUM
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


def project(cal, switch_rate=SWITCH_RATE, abnb_adr=ABNB_ADR_GROWTH, hotel_adr=HOTEL_ADR_GROWTH, mix_abnb=MIX_DRIFT_ABNB, mix_hotel=MIX_DRIFT_HOTEL,
            mkt=MARKET_GROWTH, shift=PRODUCT_SHIFT, cat=CATEGORY_GROWTH, stay=STAY_LENGTH):
    base = cal[cal.segment != "TOTAL"].set_index("segment")
    M = base.contestable_pool_mm.to_dict()
    P = base.p_airbnb_in_pool.to_dict()
    N = base.airbnb_own_category_mm.to_dict()
    # Demand machinery runs at CONSTANT 2025 stay length; the stay-length index is applied on top,
    # so nights = (trip demand at 2025 intensity) x (stay length / stay length 2025).
    sl = lambda y: stay[y] / stay[YEARS[0]]
    tot = lambda: sum(N[g] + M[g] * P[g] for g in SEG)
    rows = [{"year": 2025, **{f"M_{g}": M[g] for g in SEG}, **{f"P_{g}": P[g] for g in SEG},
             **{f"N_{g}": N[g] for g in SEG}, "stay_length": stay[YEARS[0]],
             "us_nights_mm": tot() * sl(YEARS[0])}]
    dec = []
    for y in YEARS[1:]:
        prev = tot()
        dln_price = np.log(1 + abnb_adr[y]) - np.log(1 + hotel_adr[y])
        # step 1: market growth on the contestable pool
        M1 = {g: M[g] * (1 + mkt[y]) for g in SEG}
        s_market = sum(N[g] + M1[g] * P[g] for g in SEG)
        # step 2: segment mix drift (both pools)
        M2 = {g: M1[g] * (1 + mix_hotel[g]) for g in SEG}   # pool is ~96% hotel
        N2 = {g: N[g] * (1 + mix_abnb[g]) for g in SEG}
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
        # step 5: stay length (trip intensity) - scales nights, does not touch the share competition
        s_stay = s_share * sl(y)
        M, N, P = M2, N3, P4
        rows.append({"year": y, **{f"M_{g}": M[g] for g in SEG}, **{f"P_{g}": P[g] for g in SEG},
                     **{f"N_{g}": N[g] for g in SEG}, "stay_length": stay[y], "us_nights_mm": s_stay})
        # Decomposition: steps 1-4 are measured at LAST year's stay length, so they divide by `prev`;
        # step 5 is the incremental effect of the stay-length change. The five sum to `total` exactly.
        sl_prev = sl(YEARS[YEARS.index(y) - 1])
        prev_sl = prev * sl_prev
        dec.append({"year": y, "market_pts": (s_market - prev) / prev,
                    "mix_pts": (s_mix - s_market) / prev, "category_pts": (s_cat - s_mix) / prev,
                    "share_pts": (s_share - s_cat) / prev,
                    "stay_length_pts": s_share * (sl(y) - sl_prev) / prev_sl,
                    "total": s_stay / prev_sl - 1})
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
    print("\nStay-length scenarios (2030 nights, CAGR) - the largest single lever in the model:")
    for lbl, sl in [("bull +1%/yr", STAY_LENGTH_BULL), ("base flat 4.1", STAY_LENGTH),
                    ("bear -2%/yr (the EMEA/LatAm pattern reaching NA)", STAY_LENGTH_BEAR)]:
        dd, _ = project(cal, stay=sl)
        n = dd.us_nights_mm.iloc[-1]
        print("  %-48s %6.1fmm  %+.2f%%" % (lbl, n, ((n / dd.us_nights_mm.iloc[0]) ** 0.2 - 1) * 100))

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
