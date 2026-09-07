"""
GLOBAL nights build - replaces the 10% rest-of-world plug.

Regions (FY2025 10-K nights, mm): NA 158 (US 145.4 via the 92% revenue proxy), EMEA 215,
LatAm 90, APAC 70; total 533.

  US      - the full segment-level choice model (choice_nights_driver.py, switch rate 5.0, team ADR line).
  EMEA    - the measured 4-country calibration (choice_nights_driver_countries.py: FR/ES/IT/DE =
            128.2mm Airbnb party-nights, 60% of EMEA's 215mm) scaled to EMEA and run through the
            same M/P/N machinery in aggregate. Implied EMEA own-category growth is ~10%
            (category_adoption_evidence.csv); 7% fading to 5% is used - a deliberate haircut.
  NA x US - Canada + Mexico (12.6mm) grown at the US model's growth rate.
  LatAm / APAC - still growth paths, not choice models (no hotel-side data pulled yet), but now
            EXPLICIT fades from disclosed 2025 growth (+18% / +15%) instead of one 10% plug.

Run:  python analysis/src/choice_nights_driver_global.py
Out:  data/processed/choice_driver_global_projection.csv
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

# ---------------- Regional anchors (FY2025 10-K) ----------------
NA_NIGHTS, EMEA_NIGHTS, LATAM_NIGHTS, APAC_NIGHTS = 158.0, 215.0, 90.0, 70.0

# ---------------- EMEA choice-model inputs ----------------
EMEA_MARKET_GROWTH = 0.020        # EU tourism nights +2.2% in 2025 (Eurostat DDN-20260304-1)
EMEA_HOTEL_ADR_GROWTH = 0.025     # assumption; European hotel ADR ran +3-5% 2024-25, cooling
EMEA_CATEGORY_GROWTH = {2026: 0.07, 2027: 0.065, 2028: 0.06, 2029: 0.055, 2030: 0.05}
# implied ~10% from 2024-25 EMEA history; haircut for regulation (WS11 drag) and maturity
EMEA_MIX_UPLIFT = 0.009           # same blended mix-drift contribution the US model produces
CONTESTABLE, SWITCH_RATE = us_model.CONTESTABLE, us_model.SWITCH_RATE

# ---------------- LatAm / APAC growth fades (from disclosed +18% / +15% in 2025) ----------------
LATAM_GROWTH = {2026: 0.16, 2027: 0.14, 2028: 0.12, 2029: 0.11, 2030: 0.10}
APAC_GROWTH = {2026: 0.13, 2027: 0.12, 2028: 0.11, 2029: 0.10, 2030: 0.09}


def emea_path():
    """Aggregate M/P/N projection for EMEA, seeded from the measured 4-country calibration."""
    ctry = pd.read_csv(OUT / "choice_driver_countries_calibration_2025.csv")
    tot = ctry[ctry.segment == "TOTAL"]
    a4 = tot.airbnb_party_nights_mm.sum()          # 128.2 - 4-country Airbnb party-nights
    h4 = tot.hotel_party_nights_mm.sum()           # 4-country hotel party-nights
    scale = EMEA_NIGHTS / a4                       # rest of EMEA assumed to look like the 4
    N = 0.62 * EMEA_NIGHTS
    M = CONTESTABLE * EMEA_NIGHTS + h4 * scale
    P = (CONTESTABLE * EMEA_NIGHTS) / M
    out = {2025: EMEA_NIGHTS}
    for y in YEARS[1:]:
        dln = np.log(1 + us_model.ABNB_ADR_GROWTH[y]) - np.log(1 + EMEA_HOTEL_ADR_GROWTH)
        M *= (1 + EMEA_MARKET_GROWTH + EMEA_MIX_UPLIFT)
        N *= (1 + EMEA_CATEGORY_GROWTH[y] + EMEA_MIX_UPLIFT)
        P = 1 / (1 + np.exp(-(np.log(P / (1 - P)) - SWITCH_RATE * dln)))
        out[y] = N + M * P
    return out


def main():
    cal = us_model.calibrate()
    us_df, _ = us_model.project(cal)
    us = dict(zip(us_df.year, us_df.us_nights_mm))

    na_ex_us = {2025: NA_NIGHTS - us[2025]}
    for y in YEARS[1:]:
        na_ex_us[y] = na_ex_us[y - 1] * (us[y] / us[y - 1])

    emea = emea_path()
    latam, apac = {2025: LATAM_NIGHTS}, {2025: APAC_NIGHTS}
    for y in YEARS[1:]:
        latam[y] = latam[y - 1] * (1 + LATAM_GROWTH[y])
        apac[y] = apac[y - 1] * (1 + APAC_GROWTH[y])

    rows = []
    for y in YEARS:
        total = us[y] + na_ex_us[y] + emea[y] + latam[y] + apac[y]
        rows.append({"year": y, "us": us[y], "na_ex_us": na_ex_us[y], "emea": emea[y],
                     "latam": latam[y], "apac": apac[y], "global_nights_mm": total})
    df = pd.DataFrame(rows).round(1)
    df["global_growth"] = pd.Series([np.nan] + list(np.diff(df.global_nights_mm) / df.global_nights_mm[:-1].values)).round(4)
    print(df.to_string(index=False))
    print("\nTeam model (assumptions.md WS13 base): total nights FY26 +9.9%, FY27 +8.9%, FY28 +7.4%")
    print("This build:                              FY26 %+.1f%%, FY27 %+.1f%%, FY28 %+.1f%%"
          % tuple(df.global_growth.iloc[1:4] * 100))
    df.to_csv(OUT / "choice_driver_global_projection.csv", index=False)
    print("\nwrote", OUT / "choice_driver_global_projection.csv")


if __name__ == "__main__":
    main()
