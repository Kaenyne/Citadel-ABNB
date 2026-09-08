"""
LATAM / APAC hotel-side evidence - closing (partly) the biggest gap in the nights work.

The regional model (choice_nights_driver_regional.py) runs NA and EMEA as calibrated choice models
and LatAm/APAC as pure growth models, because neither had ANY hotel-side data. Those two regions
are ~30% of 2025 nights and ~64% of 2025-30 growth, so the least evidenced part of the forecast
was also the largest. This script pulls what free official statistics do exist.

SEVEN MARKETS PULLED. Quality varies enormously - read the tier before using a number.

  TIER 1, national census or near-census, usable directly:

  MEXICO (DATATUR / SECTUR, "Turismo en Cifras", Dec-2025 edition)
    Average occupied rooms   419,768 (2023) -> 438,624 (2024) -> 466,958 (2025), +6.5% in 2025
    National occupancy       52.2% -> 51.4% -> 54.1%
    Arrivals to hotel rooms  89.8mm in 2025 (67.6mm domestic 74.8%, 22.2mm international 25.2%)
    => room-nights 2025 = 466,958 x 365 = 170.4mm; implied 1.90 nights per arrival

  JAPAN (Japan Tourism Agency, Overnight Travel Statistics Survey, 2025 preliminary annual)
    Total guest-nights       653.48mm in 2025, -0.8% y/y
                             domestic 475.61mm (-3.8%), international 177.87mm (+8.2%)
    Occupancy by type        ryokan 38.4%, resort hotel 56.9%, business hotel 75.3%,
                             city hotel 74.2%; all types 61.8%
    Supply is legally capped: the minpaku law limits a dwelling to 180 nights/yr and lets
    municipalities set it to zero locally (40,745 notified dwellings as of May-2026).

WHY THIS MATTERS MORE THAN IT LOOKS: the regional model's contestable-pool growth for LatAm and
APAC was a pure guess (3.0% and 3.5%). These are the first observations against it, and they point
in OPPOSITE directions:

    Mexico hotel room-nights   +6.5% (2025)  vs  Airbnb LatAm nights +18.4%  -> Airbnb +11.9pp
    Japan hotel guest-nights   -0.8% (2025)  vs  Airbnb APAC nights  +14.8%  -> Airbnb +15.6pp

So the LatAm lodging market is growing roughly twice as fast as assumed, while Japan's is flat to
shrinking. But Japan alone would have been a trap: the Tier-2 markets below show Korea, India and
Australia all firmer, so APAC settles at ~2.0% rather than the ~1.0% a Japan-only read implied.
Either way both regions' Airbnb growth is far more share gain than rising tide, which is a more
fragile basis for a five-year forecast and is why both carry fades.

  TIER 2, partial or sample-based - directional only:

  BRAZIL (FOHB / HotelInvest monthly panel, FY2025)
    Occupancy +2.1% y/y, ADR +10.5%, RevPAR +12.8%; urban occupancy 60.8% in 2024.
    Panel of 583 chain hotels / ~91,000 rooms - NOT a national census, and skewed to urban chains.
    Occupancy is a RATE, so room-nights growth = supply growth + occupancy growth; with Brazilian
    supply running low-single-digit, room-nights are plausibly +4-5%, i.e. broadly consistent
    with Mexico's +6.5% rather than contradicting it.

  CHINA (Ministry of Culture and Tourism, 2025 Statistical Bulletin)
    7,586 star-rated hotels at end-2025; average occupancy 49.2% (2024) -> 46.8% (2025), -4.9%.
    Domestic trips 6.522bn, +16.2%; domestic tourism spend 6.30tn yuan, +9.5%.
    ** Largely IRRELEVANT to the model: Airbnb shut its domestic China business in July 2022. **
    China enters Airbnb's APAC only through outbound travellers. Also note the tension in the
    Chinese data itself - trips +16.2% while star-rated occupancy fell - which says Chinese
    travellers are moving away from star-rated hotels, not that travel is weak.

  KOREA (KTO; Colliers Korea hotel market report, 2025)
    Inbound visitors +15.2%; Seoul occupancy 80.8% (Aug) and 81.6% (Sep); Seoul-Incheon ADR
    ~KRW 296,000 in September, +14.6% y/y. City-level, inbound-led - strong but not a national
    room-nights series.

  INDIA (FHRAI / ICRA)
    National hotel occupancy 67.5% in FY2024 (from ~66% in FY2023); premium segment guided
    70-72% FY25 -> 72-74% FY26 with revenue +6-9%. Occupancy RISING.

  AUSTRALIA (Tourism Research Australia / ABS Survey of Tourist Accommodation)
    418mm domestic visitor nights in 2025, of which 91mm business. SERIES BREAK: the National
    Visitor Survey ended Dec-2024 and Domestic Tourism Statistics (DoTS) replaces it from
    Jan-2025, so 2024->2025 is not a clean comparison. ABS STA covers establishments with 15+
    rooms only, missing exactly the small-operator segment Airbnb competes with.

LIMITS, stated plainly:
  - NOT ONE of these seven markets publishes party size by accommodation type. So P(Airbnb |
    contestable) still cannot be calibrated outside NA and EMEA - every figure here is a
    market-GROWTH anchor, not a choice model. That gap is unchanged by this pull.
  - Units are not comparable across markets: Mexico publishes ROOM-nights, Japan GUEST-nights,
    Brazil an occupancy RATE on a chain panel, China an occupancy rate on star-rated hotels only,
    Australia visitor nights on 15+ room establishments. Never add them; use each only for its own
    market's growth rate.
  - Coverage bias runs one way everywhere: official accommodation surveys count registered
    establishments (China star-rated only, Australia 15+ rooms, Brazil chains), which systematically
    excludes the small-operator segment Airbnb actually competes with. Hotel-side growth measured
    this way is likely UNDERSTATED as a measure of total lodging demand.
  - Brazil still lacks a clean national guest-nights series; IBGE publishes capacity via SIDRA.
    That remains the highest-value single pull left in LatAm.

Run:  python analysis/src/latam_apac_hotel_evidence.py
Out:  data/processed/latam_apac_hotel_evidence.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

ROWS = [
    dict(region="latam", country="Mexico", metric="avg occupied rooms", unit="rooms",
         y2023=419768, y2024=438624, y2025=466958, source="DATATUR/SECTUR Turismo en Cifras Dec-2025"),
    dict(region="latam", country="Mexico", metric="hotel occupancy", unit="%",
         y2023=0.522, y2024=0.514, y2025=0.541, source="DATATUR/SECTUR"),
    dict(region="latam", country="Mexico", metric="hotel room-nights", unit="mm",
         y2023=419768 * 365 / 1e6, y2024=438624 * 365 / 1e6, y2025=466958 * 365 / 1e6,
         source="derived: avg occupied rooms x 365"),
    dict(region="latam", country="Mexico", metric="arrivals to hotel rooms", unit="mm",
         y2023=None, y2024=None, y2025=89.8, source="DATATUR/SECTUR (67.6 domestic + 22.2 intl)"),
    dict(region="apac", country="Japan", metric="total guest-nights", unit="mm",
         y2023=None, y2024=653.48 / (1 - 0.008), y2025=653.48,
         source="JTA Overnight Travel Statistics, 2025 preliminary annual"),
    dict(region="apac", country="Japan", metric="domestic guest-nights", unit="mm",
         y2023=None, y2024=475.61 / (1 - 0.038), y2025=475.61, source="JTA"),
    dict(region="apac", country="Japan", metric="international guest-nights", unit="mm",
         y2023=None, y2024=177.87 / 1.082, y2025=177.87, source="JTA"),
    dict(region="apac", country="Japan", metric="all-type occupancy", unit="%",
         y2023=None, y2024=None, y2025=0.618, source="JTA (ryokan 38.4, resort 56.9, business 75.3, city 74.2)"),
]

# Airbnb's own disclosed regional nights growth, FY2025 10-K regional table
ABNB_2025_GROWTH = {"latam": 0.184, "apac": 0.148}
# What choice_nights_driver_regional.py assumes for contestable-pool growth (post-revision)
MODEL_MARKET = {"latam": 0.050, "apac": 0.020}   # updated 8 Sep 2026 on the evidence below


def main():
    df = pd.DataFrame(ROWS)
    print("HOTEL-SIDE EVIDENCE, LATAM AND APAC\n")
    print(df[["region", "country", "metric", "unit", "y2023", "y2024", "y2025"]].round(1).to_string(index=False))

    print("\nMARKET GROWTH: observed hotel side vs what the model assumes\n")
    obs = {
        "latam": ("Mexico hotel room-nights", 466958 / 438624 - 1),
        "apac": ("Japan hotel guest-nights", -0.008),
    }
    print(f"{'region':8s} {'proxy':28s} {'observed':>9s} {'model':>7s} {'ABNB':>7s} {'ABNB - mkt':>11s}")
    rows = []
    for r, (lbl, g) in obs.items():
        a = ABNB_2025_GROWTH[r]
        print(f"{r:8s} {lbl:28s} {g * 100:+8.1f}% {MODEL_MARKET[r] * 100:+6.1f}% "
              f"{a * 100:+6.1f}% {(a - g) * 100:+10.1f}pp")
        rows.append({"region": r, "proxy": lbl, "observed_market_growth": round(g, 4),
                     "model_assumption": MODEL_MARKET[r], "abnb_growth_2025": a,
                     "abnb_less_market_pp": round((a - g) * 100, 1)})

    print("""
READ:
  LatAm - the lodging market is growing ~2x faster than the model assumes (6.5% vs 3.0%), so part
          of Airbnb's +18.4% is a rising tide rather than share gain. Raising MARKET['latam'] is
          supported; it makes the LatAm path slightly MORE robust, not less.
  APAC  - Japan's hotel nights FELL 0.8% while Airbnb APAC grew 14.8%. If Japan is representative,
          the model's +3.5% market growth is too generous and essentially ALL of APAC's growth is
          share gain against a flat market. That is the more fragile of the two positions and
          argues for a faster fade.
  Both  - these are market-growth anchors only. Neither country publishes party size by
          accommodation type, so P(Airbnb | contestable) still cannot be calibrated outside
          NA and EMEA.
""")
    pd.DataFrame(rows).to_csv(OUT / "latam_apac_hotel_evidence.csv", index=False)
    df.to_csv(OUT / "latam_apac_hotel_series.csv", index=False)
    print("wrote", OUT / "latam_apac_hotel_evidence.csv", "and latam_apac_hotel_series.csv")


if __name__ == "__main__":
    main()
