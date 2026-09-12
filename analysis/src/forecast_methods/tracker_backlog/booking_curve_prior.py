"""(d) Booking curves -> a Dirichlet-style prior over the Phi kernel weights.

CRITICAL CAVEAT, stated once here and repeated everywhere this output is used:
`blocked_rate` in booking_curves_by_market.csv / booking_curve_daily.csv is the share
of a market's listing-nights that are UNAVAILABLE (booked OR host-blocked) within a
horizon window, in a SINGLE Jul-Aug 2026 snapshot across 120 markets. It is:
  - NOT occupancy (occupancy = nights actually stayed / nights available; this is a
    forward calendar-availability read taken today, of dates that have not happened).
  - NOT separable into "booked" vs "host blocked own calendar" -- both read as
    unavailable. Superhosts who block off personal-use dates, minimum-stay gaps, and
    manual holds are all counted as if they were bookings.
  - a single vintage: no y/y or q/q comparison is possible, so it cannot speak to
    whether the booking curve is lengthening or shortening (the one thing that
    actually moved reported KPIs twice -- 2Q24 shortening, 2025 RNPL lengthening,
    03_insider_mechanics.md sec 1.4).
  - measured in NIGHTS, not GBV or revenue-weighted GBV; a Phi kernel weight is a
    revenue-recognition-window share of DOLLARS, and nothing here carries a price.

Given that, this is a *plausibility prior*, not a measurement, over the SHAPE of the
lag distribution -- specifically, given a night that is currently blocked, how far out
is it, in quarter-buckets. It is offered to kernel-lambda as a soft check that the
Phi(2/3, 1/3, 0) mass concentrated in the first two quarters is not absurd on its face,
nothing more. It must NEVER be used to set point weights.

Mapping (horizon bands only reach 372 days = ~13.5 months in this data, so the 3rd
bucket is capped there and labelled accordingly):
  bucket 0-1Q ahead  <- h000_030 + h031_060 + h061_090  (0-90 days)
  bucket 1-2Q ahead  <- h091_180                          (91-180 days)
  bucket 2-4Q ahead  <- h181_372                          (181-372 days; NOT 2-3Q only
                        -- the data does not resolve a 270-day cutoff)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import ensure_out_dir, SRC_BOOKING_CURVES_MKT, OUT_DIR

BUCKET_MAP = {
    "h000_030": "b0_1Q", "h031_060": "b0_1Q", "h061_090": "b0_1Q",
    "h091_180": "b1_2Q",
    "h181_372": "b2_4Q_capped",
}


def run() -> pd.DataFrame:
    ensure_out_dir()
    b = pd.read_csv(SRC_BOOKING_CURVES_MKT)
    b["bucket"] = b["horizon"].map(BUCKET_MAP)

    # nights-weighted (listing-nights in the band) blocked-night counts, summed
    # across all 120 markets
    agg = (b.groupby("bucket")
            .agg(blocked_nights_sum=("blocked_nights", "sum"),
                 listing_nights_sum=("listing_nights", "sum"),
                 n_market_rows=("blocked_nights", "size"))
            .reset_index())
    agg["blocked_rate_pooled"] = agg["blocked_nights_sum"] / agg["listing_nights_sum"]

    # Dirichlet-style prior: alpha_i = blocked_nights_sum in bucket i (pseudo-counts).
    # This treats every currently-blocked listing-night in the snapshot as one "vote"
    # for its horizon bucket -- an informal but auditable way to turn a cross-sectional
    # calendar snapshot into concentration parameters.
    agg["alpha"] = agg["blocked_nights_sum"]
    total_alpha = agg["alpha"].sum()
    agg["dirichlet_mean_share"] = agg["alpha"] / total_alpha

    # region breakdown for transparency (does the shape hold across NA/EMEA/LatAm/APAC?)
    by_region = (b.groupby(["region", "bucket"])["blocked_nights"].sum()
                  .groupby(level=0, group_keys=False)
                  .apply(lambda s: s / s.sum())
                  .rename("share").reset_index())

    agg = agg.sort_values("bucket").reset_index(drop=True)
    agg.to_csv(OUT_DIR / "04_booking_curve_dirichlet_prior.csv", index=False)
    by_region.to_csv(OUT_DIR / "04b_booking_curve_prior_by_region.csv", index=False)

    caveat = (
        "PROXY, NOT A MEASUREMENT: nights not dollars; booked+host-blocked conflated; "
        "single Jul-Aug 2026 vintage, no history; blocked-rate is not occupancy. "
        "Provided as a soft plausibility check for kernel-lambda's Phi weights, never "
        "as a point input. See docstring."
    )
    with open(OUT_DIR / "04c_booking_curve_prior_caveat.txt", "w") as f:
        f.write(caveat + "\n")
    return agg, by_region, caveat


if __name__ == "__main__":
    agg, by_region, caveat = run()
    print(agg.to_string(index=False))
    print()
    print(by_region.pivot(index="region", columns="bucket", values="share").to_string())
    print()
    print(caveat)
