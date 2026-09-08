"""
Historical time series of Airbnb average party size (guests per booking), 2018-2025.

Method: Airbnb discloses CUMULATIVE guest arrivals at milestones (400M Aug-2018, 500M Mar-2019,
825M Sep-2020, 1B Oct-2021, 2B Oct-2024, 2.5B+ Dec-2025) and nights booked / nights-per-booking
in the filings. Differencing consecutive milestones and dividing by bookings made in the same
window gives average people per booking for that window - a genuine, non-overlapping time series.

PROVENANCE (Airbnb IPO'd Dec-2020; the pre-IPO inputs are still primary sources):
  - Nights booked 2017/2018/2019 (185.8 / 250.3 / 326.9mm): the S-1 (Nov-2020), which discloses
    three years of pre-IPO history as any IPO filing must. SEC-filed.
  - Arrivals 400mm (Aug-2018) and 500mm (Mar-2019): Airbnb Newsroom press releases issued while
    private. NOT audited, NOT SEC-filed - marketing announcements.
  - 825mm (Sep-2020): S-1, quoted as "over 825 million" - a FLOOR.
  - 1bn (Oct-2021) and 2bn (Oct-2024): Newsroom. The 2-billionth arrival is the most precise point
    in the series - Airbnb identified the specific guests, so it is a dated event, not a rounding.
  - 2.5bn (Dec-2025): FY2025 10-K, "over 2.5 billion" - a FLOOR, and the weakest link below.

HEADLINE (7 Sep 2026, CORRECTED): the LEVEL is ~2.95 people per booking and is well supported.
The six long windows that do NOT depend on the 2025 figure - i.e. those anchored on the precise
2-billionth-arrival event - span 2.81-3.05 with a mean of 2.953.

There is NO RELIABLE TREND in this data, and an earlier draft of this script overclaimed one.
"Over 2.5 billion" is a floor: if the true cumulative figure is 2.55bn rather than 2.50bn, the
final window moves from 2.93 to 3.22 and every window ending Dec-2025 rises ~0.15. A ~4% error in
one rounded 10-K disclosure flips the conclusion from "party size falling ~4%" to "rising ~5%".
So: the level is ~2.95; the direction is NOT MEASURABLE with the milestones Airbnb publishes.

This matters because it contradicts the natural reading of the group-travel narrative. Reconciling
the two:
  - Bedroom Nights Booked +12% y/y vs Nights +10% (Q2-2026) => bedrooms per stay rising ~1.8%/yr
  - Guests per booking showing no measurable trend => guests per bedroom probably falling,
    but this rests on the level being stable rather than on a measured decline
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
    print(f"\nMarginal party size, Oct-2024 -> Dec-2025: {marg:.2f} AT EXACTLY 2.5bn cumulative.")
    print("  But the 10-K says 'over 2.5 billion'. Sensitivity to that floor:")
    dbk = w_new.bookings_mm - w_old.bookings_mm
    for cum in (2500, 2550, 2600):
        print(f"    cumulative {cum/1000:.2f}bn -> {(cum - 2000) / dbk:.2f} people/booking")
    print("  => the DIRECTION is not identified. Only the level (~2.95) is.")
    clean = df[(df.years >= MIN_INTERPRETABLE_YEARS) & (df.end != "2025-12-31")]
    print(f"\nWindows immune to the 2025 floor (long, ending Oct-2024 or earlier), n={len(clean)}: "
          f"mean {clean.guests_per_booking.mean():.3f}, range {clean.guests_per_booking.min():.2f}"
          f"-{clean.guests_per_booking.max():.2f}  <- the defensible result")

    bpn = BEDROOM_NIGHTS_TTM_Q2_26 / NIGHTS_TTM_Q2_26
    drift = (1 + BEDROOM_NIGHTS_GROWTH) / (1 + NIGHTS_GROWTH) - 1
    print(f"\nCross-check: bedrooms per night-stay ~{bpn:.2f} (Q2-2026 TTM), growing {drift * 100:+.1f}%/yr "
          f"while guests per booking is flat\n  => guests per bedroom falling ~{drift * 100:.1f}%/yr: "
          f"same group, more space. Group travel is showing up in ADR, not in people per booking.")

    ts.to_csv(OUT / "airbnb_party_size_time_series.csv", index=False)
    print("\nwrote", OUT / "airbnb_party_size_time_series.csv")


if __name__ == "__main__":
    main()
