"""
Historical time series of Airbnb average party size (guests per booking), 2018-2025.

Method: Airbnb discloses CUMULATIVE guest arrivals at milestones (400M Aug-2018, 500M Mar-2019,
825M Sep-2020, 1B Oct-2021, 2B Oct-2024, 2.5B+ Dec-2025) and nights booked / nights-per-booking
in the filings. Differencing consecutive milestones and dividing by bookings made in the same
window gives average people per booking for that window - a genuine, non-overlapping time series.

HEADLINE (7 Sep 2026): average party size is FLAT at ~2.95-3.0 for seven years, and the most
recent window (Oct-2024 -> Dec-2025) is 2.92 - slightly BELOW the long-run mean. There is no
evidence in Airbnb's own disclosures that the average booking is carrying more people over time.

This matters because it contradicts the natural reading of the group-travel narrative. Reconciling
the two:
  - Bedroom Nights Booked +12% y/y vs Nights +10% (Q2-2026) => bedrooms per stay rising ~1.8%/yr
  - Guests per booking flat  => GUESTS PER BEDROOM IS FALLING ~1.8%/yr
  - i.e. the same size group is booking MORE SPACE, not more people per booking.
  - Consistent with Inside Airbnb: guests fill only ~half of listed capacity.
  - Also consistent with a POLARISING distribution at a constant mean: solo travel rising
    (Airbnb: ~25% of guests travel solo) AND multigenerational rising (47% of travellers in 2026,
    +17% vs 2024), hollowing the middle while the mean holds.
Implication: "group travel" shows up in ADR (bigger units) more than in nights. That is a
bearish-for-nights, bullish-for-ADR reading of the same trend the bulls cite.

CAVEAT - why short windows swing: guest arrivals are counted at CHECK-IN, bookings at RESERVATION,
so arrivals lag bookings by the booking lead time. Over <2.5-year windows that mismatch dominates
(the series shows 2.33 and 3.22 in adjacent short windows). Only windows of ~2.5yr+ are
interpretable; the long-window set spans 2.81-3.05 with a mean of 2.96.

Run:  python analysis/src/party_size_time_series.py
Out:  data/processed/airbnb_party_size_time_series.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

# Consecutive milestone chain - each window starts where the previous ended.
CHAIN = ["2018-08-26", "2019-03-27", "2020-09-30", "2021-10-15", "2024-10-15", "2025-12-31"]
MIN_INTERPRETABLE_YEARS = 2.5

# Q2-2026 disclosures for the bedrooms-per-stay cross-check
BEDROOM_NIGHTS_TTM_Q2_26 = 1000.0   # mm, ">1 billion" (Q2-2026 release)
NIGHTS_TTM_Q2_26 = 560.0            # mm, approx TTM nights at Q2-2026
BEDROOM_NIGHTS_GROWTH, NIGHTS_GROWTH = 0.12, 0.10


def main():
    df = pd.read_csv(OUT / "airbnb_guests_per_booking_windows.csv")
    df[["start", "end"]] = df.window.str.split(" -> ", expand=True)

    rows = []
    for a, b in zip(CHAIN, CHAIN[1:]):
        r = df[(df.start == a) & (df.end == b)]
        if len(r):
            r = r.iloc[0]
            rows.append({"start": a, "end": b, "years": r.years,
                         "guest_arrivals_mm": r.guest_arrivals_mm, "bookings_mm": r.bookings_mm,
                         "guests_per_booking": r.guests_per_booking,
                         "interpretable": r.years >= MIN_INTERPRETABLE_YEARS})
    ts = pd.DataFrame(rows)
    print("CONSECUTIVE-WINDOW TIME SERIES (non-overlapping)\n")
    print(ts.to_string(index=False))

    longw = df[df.years >= MIN_INTERPRETABLE_YEARS]
    print(f"\nLong-window anchors (>={MIN_INTERPRETABLE_YEARS}yr, n={len(longw)}): "
          f"mean {longw.guests_per_booking.mean():.3f}, range {longw.guests_per_booking.min():.2f}"
          f"-{longw.guests_per_booking.max():.2f}")

    # Marginal party size of the most recent period, inferred from two long windows sharing a start
    w_old = df[(df.start == "2021-10-15") & (df.end == "2024-10-15")].iloc[0]
    w_new = df[(df.start == "2021-10-15") & (df.end == "2025-12-31")].iloc[0]
    marg = ((w_new.guest_arrivals_mm - w_old.guest_arrivals_mm) /
            (w_new.bookings_mm - w_old.bookings_mm))
    print(f"\nMarginal party size, Oct-2024 -> Dec-2025 (differencing two long windows): {marg:.2f}")
    print(f"  vs the Oct-2021 -> Oct-2024 window at {w_old.guests_per_booking:.2f} "
          f"=> {(marg / w_old.guests_per_booking - 1) * 100:+.1f}% - flat to slightly DOWN, not up.")

    bpn = BEDROOM_NIGHTS_TTM_Q2_26 / NIGHTS_TTM_Q2_26
    drift = (1 + BEDROOM_NIGHTS_GROWTH) / (1 + NIGHTS_GROWTH) - 1
    print(f"\nCross-check: bedrooms per night-stay ~{bpn:.2f} (Q2-2026 TTM), growing {drift * 100:+.1f}%/yr "
          f"while guests per booking is flat\n  => guests per bedroom falling ~{drift * 100:.1f}%/yr: "
          f"same group, more space. Group travel is showing up in ADR, not in people per booking.")

    ts.to_csv(OUT / "airbnb_party_size_time_series.csv", index=False)
    print("\nwrote", OUT / "airbnb_party_size_time_series.csv")


if __name__ == "__main__":
    main()
