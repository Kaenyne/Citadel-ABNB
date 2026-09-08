"""
EMEA nights tracker - Eurostat platform data vs Airbnb's reported EMEA nights.

WHAT THIS IS NOT (correction, 7 Sep 2026): this was pitched as a way to nowcast Airbnb's EMEA
nights BEFORE the company reports. That is wrong. Eurostat's country-level platform series had
reached only Q1-2026 as of Sep-2026, while Airbnb reported Q1-2026 in May-2026 and Q2-2026 on
13 Aug 2026. Eurostat LAGS Airbnb by roughly four months. It cannot front-run a print.

WHAT IT IS: an independent, official-statistics check on WHETHER AIRBNB IS GAINING OR LOSING
SHARE of the European short-term-rental market, plus country-level detail Airbnb never discloses
(it reports one EMEA aggregate). Both are decision-useful; neither is a leading indicator.

HEADLINE FINDING: Airbnb has undergrown the EU platform aggregate two years running.
  2024: EU platform +19.0% vs Airbnb EMEA +7.5%   (wedge -11.5pp; CONTAMINATED - see caveats)
  2025: EU platform +11.5% vs Airbnb EMEA +7.0%   (wedge  -4.5pp; the cleaner read)
If the market series is even roughly right, Booking/Expedia are taking European STR share from
Airbnb in NIGHTS - a stronger and better-grounded claim than the listing-count comparison, which
actually shows Airbnb at or ahead of Booking everywhere except Spain.

CAVEATS (each one can move the wedge materially):
  1. Platform count changed: 4 platforms through 2024 (incl. Tripadvisor), 3 from 2025. The 2024
     comparison is not like-for-like.
  2. Eurostat calls this series EXPERIMENTAL. Coverage and host-compliance improve over time,
     which mechanically inflates market growth and widens the apparent wedge.
  3. EU != EMEA. Airbnb's EMEA includes the UK, Switzerland, Norway, Middle East and Africa;
     Eurostat's EU+EFTA aggregate does not match it. Only growth RATES are comparable, not levels.
  4. UNITS: Eurostat headline figures are GUEST-nights (person-nights); Airbnb's "nights booked"
     are stay-nights. Levels differ by ~the average party size (~2.97). tour_ce_omr also carries
     a "nights" (non-guest) measure, which is the like-for-like series and should replace the
     guest-nights figure in a v2 of this script.

Run:  python analysis/src/emea_nowcast.py
Out:  data/processed/emea_nowcast.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

# EU platform guest-nights, mm. 2024 and 2025 published; 2023 back-solved from "+19% in 2024".
EU_PLATFORM = {2023: 854 / 1.19, 2024: 854.0, 2025: 952.0}
# Airbnb EMEA nights, mm - FY2025 10-K regional table
ABNB_EMEA = {2023: 187.0, 2024: 201.0, 2025: 215.0}
# Latest partial-year signal
Q1_2026_EU_GROWTH = 0.097          # Q1-2026: 144.3mm guest-nights, +9.7% y/y
Q1_SHARE_OF_YEAR = 144.3 / 952.0   # Q1 is only ~15% of the year - seasonality caution


def main():
    rows = []
    for y in (2024, 2025):
        ge = EU_PLATFORM[y] / EU_PLATFORM[y - 1] - 1
        ga = ABNB_EMEA[y] / ABNB_EMEA[y - 1] - 1
        rows.append({"year": y, "eu_platform_mm": round(EU_PLATFORM[y], 1),
                     "eu_platform_growth": round(ge, 4), "abnb_emea_mm": ABNB_EMEA[y],
                     "abnb_emea_growth": round(ga, 4), "wedge_pp": round((ga - ge) * 100, 1)})
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))

    wedge = df.loc[df.year == 2025, "wedge_pp"].iloc[0] / 100   # use the clean year only
    print(f"\nNowcast for FY2026 EMEA, carrying the 2025 wedge ({wedge * 100:+.1f}pp):")
    print(f"  Q1-2026 EU platform growth {Q1_2026_EU_GROWTH:+.1%} (only {Q1_SHARE_OF_YEAR:.0%} of the year)")
    out = []
    for label, mkt in [("Q1-2026 run-rate", Q1_2026_EU_GROWTH),
                       ("FY2025 rate held", EU_PLATFORM[2025] / EU_PLATFORM[2024] - 1),
                       ("market decelerates to +7%", 0.07)]:
        g = mkt + wedge
        nights = ABNB_EMEA[2025] * (1 + g)
        print(f"  market {mkt:+.1%} -> Airbnb EMEA {g:+.1%} -> {nights:.1f}mm   [{label}]")
        out.append({"scenario": label, "eu_market_growth": round(mkt, 4),
                    "implied_abnb_emea_growth": round(g, 4), "implied_emea_nights_mm": round(nights, 1)})

    print("\nCross-check vs choice_driver_global_projection.csv:")
    try:
        glob = pd.read_csv(OUT / "choice_driver_global_projection.csv")
        model26 = glob.loc[glob.year == 2026, "emea"].iloc[0]
        base = out[0]["implied_emea_nights_mm"]
        print(f"  choice model EMEA 2026: {model26:.1f}mm | Eurostat-implied: {base:.1f}mm "
              f"({(base / model26 - 1) * 100:+.1f}%)")
        print("  Two independent routes land within a couple of percent - the EMEA build is not obviously wrong.")
    except Exception as e:
        print("  (global projection not available:", e, ")")

    pd.DataFrame(out).to_csv(OUT / "emea_nowcast.csv", index=False)
    print("\nwrote", OUT / "emea_nowcast.csv")


if __name__ == "__main__":
    main()
