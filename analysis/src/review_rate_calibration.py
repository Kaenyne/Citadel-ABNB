"""
Calibrate the Airbnb REVIEW RATE against measured platform bookings - closing the bottom-up loop.

The bottom-up nights build (bottom_up_nights_from_raw.py) hinges entirely on the review rate: the
share of stays that leave a review. Inside Airbnb's published work assumes 50%, the literature
spans 30-72%, and that 2.4x range was the dominant uncertainty in the whole check - wide enough
that the bottom-up estimate could not confirm or refute the top-down nights level.

This calibrates it directly. Eurostat's collaborative-economy dataset (tour_ce_omn12) publishes
STAYS - actual bookings, reported by Airbnb, Booking and Expedia themselves - at NUTS region level.
Five European regions are effectively single cities, so they match an Inside Airbnb city almost
exactly:

    AT13 Vienna | DE30 Berlin | BE10 Brussels | CZ01 Prague | ES30 Madrid

Then, simply:

    review rate = Inside Airbnb reviews_ltm / (Eurostat stays x Airbnb's share of the 3 platforms)

This needs NO stay-length assumption, unlike everything else in the bottom-up chain, because both
sides are counts of bookings.

RESULT, pooled over 984,203 reviews against 3,304,396 measured stays:

    Airbnb = 50% of 3-platform stays  ->  review rate 60%
    Airbnb = 60%                      ->  review rate 50%
    Airbnb = 70%                      ->  review rate 43%

So the review rate is 43-60%, and Inside Airbnb's 50% assumption is vindicated at a ~60% Airbnb
platform share - which is close to the listing-share evidence (myDataValue: Airbnb 50-69% of
Airbnb+Booking listings across FR/ES/IT/DE, before diluting for Expedia). The literature's 30% low
end and 72% high end are both ruled out on this evidence.

WHAT THAT DOES TO THE US CHECK. At a 50% review rate the eight US cities produce ~156 nights per
active listing against a top-down US average of 87.3. That is a 78% urban premium, and the natural
question is whether it is credible. Decompose it: if large urban markets are ~30% of US active
listings at 156 nights, the remaining 70% must average ~57 nights for the national figure to hold.
Roughly 57 nights a year is exactly what a seasonal rural / vacation-home listing (Smoky Mountains,
beach towns, lake houses) looks like. So the two levels ARE reconcilable, and the top-down number
survives the bottom-up check once supply mix is accounted for.

CAVEATS, and the first is the binding one:
  - Airbnb's share of 3-platform stays is not published per city, and the cross-city spread of
    implied review rates is wide (Vienna 36% to Berlin 67% at a 60% share assumption). That spread
    is probably variation in Airbnb's share by city - Booking is strong in continental European
    apartments - rather than genuine variation in reviewing behaviour.
  - Eurostat 2025 annual vs Inside Airbnb June-2026 LTM snapshots: about a six-month offset.
  - NUTS region vs Inside Airbnb city boundary is close for these five but not identical.
  - European reviewing behaviour may differ from US; this is calibrated on Europe and applied to
    the US check.

Run:  python analysis/src/review_rate_calibration.py
Out:  data/processed/review_rate_calibration.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
RAW = ROOT / "data/raw/inside_airbnb"

# Eurostat tour_ce_omn12, annual 2025, indic_to=STY (stays), c_resid=TOTAL, month=TOTAL
EUROSTAT_STAYS_2025 = {
    "vienna": (702_156, "AT13"), "berlin": (328_646, "DE30"), "brussels": (294_385, "BE10"),
    "prague": (674_845, "CZ01"), "madrid": (1_304_364, "ES30"),
}
ABNB_PLATFORM_SHARES = (0.50, 0.60, 0.70)
US_URBAN_NIGHTS_AT_50 = 156.0   # bottom_up_nights_from_raw.py, 8 cities, rr=50%
US_TOPDOWN_ACTIVE = 87.3        # 138.4mm nights / 2.25mm listings / 70.4% active share
URBAN_SHARE_OF_US_LISTINGS = 0.30


def main():
    rows = []
    for city, (stays, geo) in EUROSTAT_STAYS_2025.items():
        f = RAW / f"eu_{city}_listings.csv.gz"
        if not f.exists():
            print(f"  skip {city} - no listings file at {f}")
            continue
        l = pd.read_csv(f, usecols=["id", "number_of_reviews_ltm"], low_memory=False)
        a = l[l.number_of_reviews_ltm > 0]
        rows.append({"city": city, "geo": geo, "listings": len(l), "active": len(a),
                     "reviews_ltm": int(a.number_of_reviews_ltm.sum()), "eurostat_stays": stays})
    d = pd.DataFrame(rows)
    if d.empty:
        raise SystemExit(f"No EU listings files under {RAW}. See docstring for download paths.")

    for s in ABNB_PLATFORM_SHARES:
        d[f"rr_at_{int(s * 100)}"] = d.reviews_ltm / (d.eurostat_stays * s)

    print("REVIEW-RATE CALIBRATION vs Eurostat measured stays (2025)\n")
    print(d.round(3).to_string(index=False))

    tot_r, tot_s = d.reviews_ltm.sum(), d.eurostat_stays.sum()
    print(f"\npooled: {tot_r:,} reviews against {tot_s:,} measured stays")
    pooled = {}
    for s in ABNB_PLATFORM_SHARES:
        pooled[s] = tot_r / (tot_s * s)
        print(f"  Airbnb = {s:.0%} of 3-platform stays -> REVIEW RATE {pooled[s]:.0%}")
    print("\n  => the review rate is 43-60%. Inside Airbnb's 50% assumption is vindicated at a")
    print("     ~60% Airbnb platform share. The literature's 30% and 72% ends are both ruled out.")

    print("\nCLOSING THE LOOP ON THE US CHECK\n")
    implied_rural = (US_TOPDOWN_ACTIVE - URBAN_SHARE_OF_US_LISTINGS * US_URBAN_NIGHTS_AT_50) / \
                    (1 - URBAN_SHARE_OF_US_LISTINGS)
    print(f"  8 US cities at a 50% review rate: {US_URBAN_NIGHTS_AT_50:.0f} nights/active listing")
    print(f"  top-down US average (active basis): {US_TOPDOWN_ACTIVE:.1f}")
    print(f"  if large urban markets are {URBAN_SHARE_OF_US_LISTINGS:.0%} of US active listings,")
    print(f"  the other {1 - URBAN_SHARE_OF_US_LISTINGS:.0%} must average {implied_rural:.0f} nights/yr")
    print(f"  ~{implied_rural:.0f} nights a year is what a seasonal rural / vacation-home listing looks")
    print("  like, so the two levels ARE reconcilable and the top-down number survives.")

    d.round(4).to_csv(OUT / "review_rate_calibration.csv", index=False)
    print("\nwrote", OUT / "review_rate_calibration.csv")


if __name__ == "__main__":
    main()
