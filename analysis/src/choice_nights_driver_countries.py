"""
Choice-probability nights driver - EUROPEAN COUNTRIES (France, Spain, Italy, Germany).

Generalises the France calibration (supersedes choice_nights_driver_france.py) to the four
largest Eurostat-covered Airbnb markets. Unlike the U.S. model, BOTH sides are measured:
  - platform STR guest-nights reported by Airbnb/Booking/Expedia to Eurostat (tour_ce_omr)
  - hotel guest-nights from the same statistical system (NACE I551, "hotels and similar")

UNITS: Eurostat reports GUEST-nights (person-nights). Conversion to party-nights divides by
people-per-party - NOT the rooms-per-party conversion the U.S. model applies to room-nights.

Run:  python analysis/src/choice_nights_driver_countries.py
Out:  data/processed/choice_driver_countries_calibration_2025.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
SEG = ["solo", "pair", "3-4", "5+"]

# ---------------- Country inputs ----------------
# platform_nights: Eurostat guest-nights via 3 platforms, mm (DDN-20260401-1).
# hotel_nights: Eurostat I551 guest-nights, mm (via TradingEconomics mirrors); note period.
# abnb_share: Airbnb share of STR listings (myDataValue Jul/Aug-2026; France = AirDNA count).
#   Listing share proxies the nights share - flagged, not measured. VALIDATED 7 Sep 2026 by direct
#   fetch of each country page (exact counts, Airbnb snapshot 2026-07-07 / Booking 2026-06-17):
#     France  802,763 / 360,653 -> Airbnb 69.0%   (Airbnb stronghold)
#     Spain   234,413 / 238,087 -> Airbnb 49.6%   (Booking ahead by 3,674 - the ONLY one)
#     Italy   454,258 / 395,275 -> Airbnb 53.5%
#     Germany 241,989 / 228,579 -> Airbnb 51.4%
#   NOTE: Vrbo is NOT in this dataset, so all four shares are Airbnb-vs-Booking only and overstate
#   Airbnb's true share of ALL platform nights. Booking's STR supply also skews professionally
#   managed / higher occupancy, so its NIGHTS share likely exceeds its listing share - i.e. these
#   numbers are an UPPER bound on Airbnb's nights share. See emea_nowcast.py: Airbnb has undergrown
#   the EU platform aggregate two years running, which is consistent with that bias.
COUNTRIES = {
    "France":  {"platform_nights": 213.0, "hotel_nights": 220.2, "hotel_period": "2025", "abnb_share": 0.69},
    "Spain":   {"platform_nights": 189.0, "hotel_nights": 363.1, "hotel_period": "2024", "abnb_share": 0.50},
    "Italy":   {"platform_nights": 139.0, "hotel_nights": 288.2, "hotel_period": "2025", "abnb_share": 0.53},
    "Germany": {"platform_nights": 68.0,  "hotel_nights": 299.9, "hotel_period": "2024", "abnb_share": 0.51},
}

# ---------------- Shared assumptions (transplanted; see TODOs) ----------------
# Airbnb party mix: global fitted booking distribution x relative stay length ("Airbnb Party Size").
# Hotel party mix: must be a TRAVEL-PARTY distribution (per-room-booking data would put ~0.5% of
# hotel demand at 5+ and hand Airbnb ~90% of that segment). U.S. travel-party estimate used.
# TODO: country-specific party mixes; business/leisure splits; CONTESTABLE is F&F's U.S. figure.
BOOK_SHARE = {"solo": 0.16, "pair": 0.358, "3-4": 0.323, "5+": 0.159}
REL_LEN = {"solo": 1.5, "pair": 0.95, "3-4": 0.9, "5+": 0.8}
HOTEL_PARTY = {"solo": 0.452, "pair": 0.387, "3-4": 0.129, "5+": 0.037}
ABNB_SIZE = {"solo": 1.0, "pair": 2.0, "3-4": 3.4, "5+": 6.4}    # mean ~2.97/booking
HOTEL_SIZE = {"solo": 1.0, "pair": 2.0, "3-4": 3.43, "5+": 5.5}  # mean ~1.87/party
CONTESTABLE = 0.38
SWITCH_RATE = 5.0  # see choice_nights_driver.py for the F&F Table E9 derivation (formerly 'beta')


def calibrate(country, platform_nights, hotel_nights, abnb_share, hotel_period="2025"):
    abnb_guest_nights = platform_nights * abnb_share

    wp = {g: BOOK_SHARE[g] * REL_LEN[g] for g in SEG}
    wg = {g: wp[g] * ABNB_SIZE[g] for g in SEG}
    tot = sum(wg.values())
    abnb = {g: abnb_guest_nights * wg[g] / tot / ABNB_SIZE[g] for g in SEG}

    hg = {g: HOTEL_PARTY[g] * HOTEL_SIZE[g] for g in SEG}
    htot = sum(hg.values())
    hotel = {g: hotel_nights * hg[g] / htot / HOTEL_SIZE[g] for g in SEG}

    rows = []
    for g in SEG:
        c = abnb[g] * CONTESTABLE
        rows.append({"country": country, "segment": g,
                     "airbnb_party_nights_mm": abnb[g], "airbnb_contestable_mm": c,
                     "hotel_party_nights_mm": hotel[g],
                     "p_airbnb_in_pool": c / (c + hotel[g]),
                     "airbnb_share_all_lodging": abnb[g] / (abnb[g] + hotel[g])})
    a, h, c = sum(abnb.values()), sum(hotel.values()), sum(abnb.values()) * CONTESTABLE
    rows.append({"country": country, "segment": "TOTAL",
                 "airbnb_party_nights_mm": a, "airbnb_contestable_mm": c,
                 "hotel_party_nights_mm": h, "p_airbnb_in_pool": c / (c + h),
                 "airbnb_share_all_lodging": a / (a + h)})
    return rows


def main():
    rows = []
    for name, cc in COUNTRIES.items():
        rows += calibrate(name, cc["platform_nights"], cc["hotel_nights"], cc["abnb_share"], cc["hotel_period"])
    cal = pd.DataFrame(rows)
    print("EUROPE 2025 calibration (party-nights, mm; Airbnb-only at listing-share proxy)\n")
    print(cal.round(3).to_string(index=False))

    print("\nAirbnb share of all lodging party-nights by segment:")
    piv = cal[cal.segment != "TOTAL"].pivot(index="country", columns="segment", values="airbnb_share_all_lodging")
    tot = cal[cal.segment == "TOTAL"].set_index("country").airbnb_share_all_lodging
    piv = piv[SEG].assign(TOTAL=tot)
    print((piv * 100).round(1).to_string())

    OUT.mkdir(parents=True, exist_ok=True)
    cal.to_csv(OUT / "choice_driver_countries_calibration_2025.csv", index=False)
    print("\nwrote", OUT / "choice_driver_countries_calibration_2025.csv")
    print("""
OPEN ITEMS (inherited from the France build, now applying to all four)
  1. Airbnb nights share proxied by listing share (FR 69% / ES 50% / IT 53% / DE 51%).
  2. Eurostat platform vs establishment frameworks overlap ('cannot be combined' warning).
  3. Party-size mixes transplanted (Airbnb global fit / U.S. hotel travel-party estimate).
  4. Spain & Germany hotel nights are 2024 vintage vs 2025 platform nights (~2-3% drift).
  5. CONTESTABLE = 0.38 is Farronato & Fradkin's U.S. survey figure.
""")


if __name__ == "__main__":
    main()
