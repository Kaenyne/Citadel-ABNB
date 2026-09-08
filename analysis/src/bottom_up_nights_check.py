"""
BOTTOM-UP fact-check of the top-down nights level.

The nights model is top-down throughout: STR/CoStar national room nights, AHLA national splits,
and - critically - U.S. Airbnb nights taken as the disclosed North America total x a REVENUE-share
proxy. That last step is a single unvalidated chain, and the audit already found it ~4% too high
(the model reproduced $4.97bn of U.S. revenue against $4.76bn reported, which is why
US_ADR_PREMIUM is now 1.05 and U.S. nights are 138.4mm rather than 145.4mm).

This script tests that level from the supply side instead, using the identity

    nights = listings x 365 x availability x occupancy

WHY A NAIVE VERSION OF THIS IS WRONG, and it is worth stating because it is an easy trap:
AirDNA's occupancy is booked nights / AVAILABLE nights, NOT booked / 365. Multiplying
2.25mm U.S. listings x 365 x 55% gives 452mm nights - more than Airbnb's entire global total of
533mm. The availability term (what share of the year a host actually offers) is doing most of the
work and is the term nobody publishes cleanly.

TEST 1 - what availability does the top-down number imply, and is it plausible?
  2.25mm U.S. listings x 365 = 821mm listing-days. Top-down 138.4mm nights = 16.9% of all
  calendar days. At AirDNA occupancy of 50/55/60%, implied availability is 33.7 / 30.6 / 28.1%,
  i.e. the average U.S. listing is offered 103-123 nights a year.
  VERDICT: plausible. A mix of professional hosts (near year-round) and casual hosts (a few weeks)
  lands in exactly that band. The top-down level is NOT contradicted by the supply base.

TEST 2 - nights per listing, which needs no availability term and is the cleaner check.
  Global: 533mm / 8.0mm listings   = 66.6 nights/listing/yr
          533mm / 9.5mm listings   = 56.1
  U.S.:   138.4mm / 2.25mm         = 61.5
  The U.S. sits 8% BELOW an 8.0mm global base and 10% above a 9.5mm base - i.e. squarely inside
  the range, but at the low end of it. That is mildly uncomfortable: U.S. supply skews whole-home
  and professional, which should be MORE utilised than a global mix heavy in private rooms and
  casual hosts, so the U.S. ought to sit ABOVE the global average rather than at or below it.
  Reading it the other way, holding U.S. nights fixed, 67-85 nights/listing would imply
  1.63-2.07mm U.S. listings rather than 2.25mm.

CONCLUSION: the bottom-up check does NOT overturn the top-down level - both tests place it inside
a plausible band - but it does NOT independently confirm it either, because every input carries
wide uncertainty (listing counts vary 8.0-9.5mm globally by source; availability is unpublished).
It is a sanity check that the level is not absurd, not a validation of the specific number. The
residual tension in Test 2 leans the same way as the revenue reconciliation did: if anything, U.S.
nights are on the high side relative to the supply base, or the 2.25mm listing count is too high.

WHY THIS ISN'T THE STRONGER VERSION, and what would be:
Inside Airbnb calendars would give a genuinely independent build, but the repo's extract cannot
support it as it stands:
  - a "booked run" there is a contiguous UNAVAILABLE block CAPPED AT 30 NIGHTS to strip host
    blocks. That makes mean run length usable but total booked nights systematically UNDERCOUNTED,
    because every run over 30 nights is dropped entirely.
  - the calendars are 365-day FORWARD snapshots, so far-dated months are unbooked simply because
    the bookings have not happened yet. Averaging occupancy across the forward year understates
    realised occupancy badly.
  Together these produce ~9.7% implied occupancy across the eight cities against AirDNA's ~55% -
  about one eighth. The fix is to recompute from the raw calendar.csv.gz using only a near window
  (say 0-30 days out, where booking is largely complete) and no 30-night cap, then correct for the
  remaining pickup. data/raw is gitignored and the gz files are not on this machine, so that is a
  follow-up, not something this script can do.

Run:  python analysis/src/bottom_up_nights_check.py
Out:  data/processed/bottom_up_nights_check.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

US_NIGHTS_TOPDOWN = 138.4      # choice_nights_driver.py, US_ADR_PREMIUM = 1.05
GLOBAL_NIGHTS = 533.0          # FY2025 10-K
US_LISTINGS = 2.25             # mm, active US properties 2025 (industry compilations)
GLOBAL_LISTINGS = (8.0, 9.5)   # mm - sources disagree, so both are carried
AIRDNA_OCC = (0.50, 0.55, 0.60)


def main():
    rows = []
    ld = US_LISTINGS * 365
    print("TEST 1 - implied availability\n")
    print(f"  {US_LISTINGS}mm US listings x 365 = {ld:.0f}mm listing-days")
    print(f"  top-down {US_NIGHTS_TOPDOWN}mm nights = {US_NIGHTS_TOPDOWN / ld * 100:.1f}% of calendar days")
    for occ in AIRDNA_OCC:
        av = US_NIGHTS_TOPDOWN / ld / occ
        print(f"    occupancy {occ:.0%} -> availability {av * 100:.1f}% ({av * 365:.0f} nights offered/listing)")
        rows.append({"test": "implied_availability", "occupancy": occ, "availability": round(av, 4),
                     "nights_offered_per_listing": round(av * 365, 1)})
    print("  VERDICT: plausible - professional hosts near year-round, casual hosts a few weeks.")

    print("\nTEST 2 - nights per listing (no availability term needed)\n")
    us_npl = US_NIGHTS_TOPDOWN / US_LISTINGS
    print(f"  US: {us_npl:.1f} nights/listing/yr")
    for gl in GLOBAL_LISTINGS:
        g = GLOBAL_NIGHTS / gl
        print(f"  global at {gl}mm listings: {g:.1f}  -> US is {us_npl / g - 1:+.0%}")
        rows.append({"test": "nights_per_listing", "global_listings_mm": gl,
                     "global_nights_per_listing": round(g, 1), "us_nights_per_listing": round(us_npl, 1),
                     "us_vs_global": round(us_npl / g - 1, 4)})
    print("  US supply skews whole-home/professional and should be MORE utilised than the global")
    print("  mix, so sitting at the low end of the range leans the same way as the revenue")
    print("  reconciliation: US nights high relative to supply, or the listing count too high.")
    for npl in (67, 75, 85):
        print(f"    at {npl} nights/listing, {US_NIGHTS_TOPDOWN}mm nights implies "
              f"{US_NIGHTS_TOPDOWN / npl * 1000:.0f}k US listings")

    print("\nCONCLUSION: not contradicted, not confirmed. Both tests place the top-down level")
    print("inside a plausible band, but every input has wide uncertainty, so this is a sanity")
    print("check rather than a validation. See the docstring for the stronger version and why")
    print("the repo's Inside Airbnb extract cannot support it yet.")

    pd.DataFrame(rows).to_csv(OUT / "bottom_up_nights_check.csv", index=False)
    print("\nwrote", OUT / "bottom_up_nights_check.csv")


if __name__ == "__main__":
    main()
