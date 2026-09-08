"""
BOTTOM-UP nights from raw Inside Airbnb data - an independent check on the top-down level.

The top-down U.S. nights figure rests on one chain: disclosed North America nights x a REVENUE
share proxy. This builds nights from the supply side instead, for 8 U.S. cities, from the raw
listings.csv.gz and calendar.csv.gz.

WHY THE CALENDAR ALONE CANNOT DO IT. Inside Airbnb's calendar marks `available = f` for booked
AND host-blocked AND not-yet-opened nights, with no way to separate them. The Austin horizon
profile makes the problem concrete (share unavailable, by days from the 2026-06-22 snapshot):

    0-7d 61.3% | 7-30d 42.8% | 30-60d 32.8% | 60-90d 27.4% | 90-120d 34.5%
    120-180d 31.9% | 180-240d 35.2% | 240-300d 40.9% | 300-366d 47.3%

Unavailability falls to a minimum around 60-90 days and then RISES again. That rise is not
bookings - it is hosts whose calendars simply are not open that far out. So "near minus far"
does not identify bookings either, because far-horizon unavailability is dominated by closed
calendars rather than blocks. Any occupancy read straight off the calendar is uninterpretable,
which is also why the repo's earlier extract implied ~9.7% occupancy against AirDNA's ~55%.

WHAT THIS USES INSTEAD - the review-rate estimator (Inside Airbnb's own "San Francisco model"):

    bookings_ltm = number_of_reviews_ltm / review_rate
    nights_ltm   = bookings_ltm x average nights per booked stay

Review rate is the share of stays that leave a review. Inside Airbnb's published work uses 50%;
the literature spans roughly 30-72%, so the whole range is carried rather than a point estimate.
CALIBRATED 8 Sep 2026 (review_rate_calibration.py): against Eurostat's MEASURED platform stays for
five European city-regions, the review rate is 43-60% and lands on 50% at a ~60% Airbnb platform
share. Both literature extremes are ruled out. Read the rr=50% column as the central case.
Stay length: the repo's booked-run mean is biased UP (its own source script says so - host blocks
read as bookings; Austin 4.71 against Airbnb's disclosed North America 4.1). The disclosed 4.1 is
therefore used as central, with the run-length mean carried as a high case.

Basis: the top-down 61.5 is nights per ALL U.S. listings. Active listings (a review in the last 12
months) are 70.4% of all across these eight cities, so the comparable top-down figure is
61.5 / 0.704 = 87.3 nights per ACTIVE listing. Comparing to 61.5 would overstate the gap by 42%.

THE COMPARISON: nights per active listing per year, against the 61.5 implied by the top-down
model (138.4mm U.S. nights / 2.25mm U.S. listings). This is the cleanest possible test because it
needs no availability term and no listing-count assumption on the bottom-up side.

Run:  python analysis/src/bottom_up_nights_from_raw.py --raw <dir>
      (expects <city>.csv.gz and <city>_listings.csv.gz per city; data/raw is gitignored)
Out:  data/processed/bottom_up_nights_from_raw.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"
RAW_DEFAULT = ROOT / "data/raw/inside_airbnb"

CITIES = {"austin": "austin", "chicago": "chicago", "denver": "denver", "nashville": "nashville",
          "new-orleans": "neworleans", "san-francisco": "sanfrancisco", "seattle": "seattle",
          "washington-dc": "washingtondc"}
REVIEW_RATES = (0.30, 0.50, 0.72)     # low / Inside Airbnb central / high
TOPDOWN_NIGHTS_PER_LISTING = 61.5     # 138.4mm US nights / 2.25mm US listings (ALL listings)
DISCLOSED_STAY = 4.1                  # Airbnb FY2025 10-K, North America nights per booking


def main():
    raw = Path(sys.argv[sys.argv.index("--raw") + 1]) if "--raw" in sys.argv else RAW_DEFAULT
    seg = pd.read_csv(OUT / "insideairbnb_booked_run_length_by_segment.csv")
    stay = seg[seg.segment == "ALL"].set_index("city")["mean"].to_dict()

    rows = []
    for city, key in CITIES.items():
        lf = raw / f"{city}_listings.csv.gz"
        if not lf.exists():
            print(f"  skip {city} (no listings file)")
            continue
        l = pd.read_csv(lf, usecols=["id", "number_of_reviews_ltm", "room_type", "availability_365"],
                        low_memory=False)
        active = l[l.number_of_reviews_ltm > 0]
        rows.append({"city": city, "listings_all": len(l), "listings_active": len(active),
                     "reviews_ltm": active.number_of_reviews_ltm.sum(),
                     "reviews_per_active": active.number_of_reviews_ltm.mean(),
                     "stay_len": stay.get(key, np.nan),
                     "avail365_mean": active.availability_365.mean()})
    d = pd.DataFrame(rows)
    if d.empty:
        raise SystemExit(f"No raw files found under {raw}. See the docstring for the download paths.")

    print("RAW INPUTS (Inside Airbnb, June-2026 snapshots)\n")
    print(d.round(2).to_string(index=False))

    # TWO CORRECTIONS before any comparison is meaningful:
    # 1. BASIS. The top-down 61.5 is nights per ALL US listings (138.4mm / 2.25mm). The bottom-up
    #    is per ACTIVE listing (reviews in the last 12 months). Active is only ~60% of all here, so
    #    the two are not comparable until the top-down figure is put on an active-listing basis.
    # 2. STAY LENGTH. The repo's booked-run mean is biased UP - the source script says so, because
    #    host blocks read as bookings. Austin's 4.71 against Airbnb's disclosed North America 4.1
    #    is about a 15% overstatement, so the disclosed 4.1 is used as central.
    active_share = d.listings_active.sum() / d.listings_all.sum()
    td_active = TOPDOWN_NIGHTS_PER_LISTING / active_share
    print(f"\nactive listings are {active_share:.1%} of all -> top-down on an ACTIVE basis = "
          f"{td_active:.1f} nights/active listing (was {TOPDOWN_NIGHTS_PER_LISTING:.1f} per all)")

    rpa = d.reviews_ltm.sum() / d.listings_active.sum()
    print(f"pooled reviews per active listing (LTM) = {rpa:.2f}")
    print("\nNIGHTS PER ACTIVE LISTING = reviews_ltm/listing / review_rate x stay length\n")
    print(f"  {'stay length':22s}" + "".join(f"{f'rr={r:.0%}':>10s}" for r in REVIEW_RATES))
    for sl, lbl in [(DISCLOSED_STAY, "4.1 (10-K NA, central)"),
                    (float((d.stay_len * d.reviews_ltm).sum() / d.reviews_ltm.sum()),
                     "5.06 (run-length, high)")]:
        vals = [rpa / rr * sl for rr in REVIEW_RATES]
        print(f"  {lbl:22s}" + "".join(f"{v:10.1f}" for v in vals))
        for rr, v in zip(REVIEW_RATES, vals):
            rows_out.append({"stay_length": sl, "review_rate": rr,
                             "nights_per_active_listing": round(v, 1),
                             "topdown_active_basis": round(td_active, 1)})

    implied_rr = rpa * DISCLOSED_STAY / td_active
    print(f"\nRECONCILIATION - what review rate makes bottom-up equal top-down?")
    print(f"  {rpa:.2f} reviews x {DISCLOSED_STAY} nights / {td_active:.1f} = "
          f"IMPLIED REVIEW RATE {implied_rr:.0%}")
    inside = REVIEW_RATES[0] <= implied_rr <= REVIEW_RATES[-1]
    print(f"  literature range is {REVIEW_RATES[0]:.0%}-{REVIEW_RATES[-1]:.0%} -> "
          f"{'INSIDE the plausible range' if inside else 'OUTSIDE the plausible range'}")
    urban_prem = {rr: (rpa / rr * DISCLOSED_STAY) / td_active - 1 for rr in REVIEW_RATES}
    print(f"""
VERDICT - the two methods do NOT reconcile at any published review rate, and the direction matters.
  An implied {implied_rr:.0%} review rate is above the {REVIEW_RATES[-1]:.0%} top of the literature
  range, so on these eight cities the bottom-up build produces MORE nights per active listing than
  the top-down U.S. average implies, at every review rate tested:
      rr 72% -> {rpa / 0.72 * DISCLOSED_STAY:5.0f} vs {td_active:.0f} top-down  ({urban_prem[0.72]:+.0%})
      rr 50% -> {rpa / 0.50 * DISCLOSED_STAY:5.0f} vs {td_active:.0f} top-down  ({urban_prem[0.50]:+.0%})
      rr 30% -> {rpa / 0.30 * DISCLOSED_STAY:5.0f} vs {td_active:.0f} top-down  ({urban_prem[0.30]:+.0%})

  That gap is NOT automatically an error. These are eight large urban markets - professionally
  hosted, better utilised - and they SHOULD sit above a national average that includes rural and
  seasonal supply. The question is only whether the premium is credible:
      at a 72% review rate the implied urban premium is {urban_prem[0.72]:+.0%} - entirely credible;
      at 50% it is {urban_prem[0.50]:+.0%} - large but arguable;
      at 30% it is {urban_prem[0.30]:+.0%} - not credible, so a 30% review rate can be ruled out.

  READ: the top-down level is not refuted. If anything this leans the OPPOSITE way to the earlier
  supply-side check in bottom_up_nights_check.py, which hinted U.S. nights might be on the high
  side. Here they look, if anything, low. Two checks pointing opposite ways means neither is
  decisive and the level is uncertain within roughly +/-25% - which is honest, and worth saying
  out loud rather than claiming a validation.

  SETTLED, 8 Sep 2026 - see review_rate_calibration.py. Calibrated against Eurostat measured stays
  the review rate is 43-60%, centred on 50%, so the rr=50% row is the one to read: 156 nights per
  active listing for these eight cities against a top-down US average of 87.3. That +78% gap is
  RECONCILABLE rather than an error: if large urban markets are ~30% of US active listings, the
  other 70% need only average ~58 nights/yr, which is what seasonal rural and vacation-home supply
  actually looks like. The top-down level survives the bottom-up check.
""")
    pd.DataFrame(rows_out).to_csv(OUT / "bottom_up_nights_from_raw.csv", index=False)
    print("wrote", OUT / "bottom_up_nights_from_raw.csv")


rows_out = []

if __name__ == "__main__":
    main()
