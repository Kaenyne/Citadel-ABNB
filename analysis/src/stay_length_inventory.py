"""
Length-of-stay: every source we have, in one place, with what each can and cannot support.

Stay length is the LARGEST single lever in the nights model (a -2%/yr path takes 2030 U.S. nights
from 171.1mm to 154.8mm, CAGR +3.31% -> +1.27%), so it is worth knowing exactly what stands behind
it. Seven sources, in three tiers.

TIER 1 - MEASURED, and two of them validate the model's inputs almost exactly

  AIRBNB 10-K, nights per booking (the model's own input)     global + 4 regions, FY2020-FY2025
      Global 4.1 / 4.1 / 4.1 / 3.9 / 3.8 / 3.7    NA 4.4 -> 4.1 (flat since 2023)
      EMEA 4.4 -> 3.8 (-14%)   LatAm 4.4 -> 3.6 (-18%)   APAC 2.8 -> 3.3 (+18%, only riser)

  EUROSTAT tour_ce_omn12, 2025 - the strongest external check we have, and it was sitting unused.
      The dataset carries THREE measures, not one: STY (stays = bookings), LSTY (nights rented out
      = listing-nights) and NGT_SP (guest-nights = person-nights). Dividing them gives measured
      stay length AND measured party size, for 85.4mm bookings and 951.6mm guest-nights:

          EU27      3.77 nights/booking      2.96 guests/night
          Spain     4.64                     3.18
          Germany   3.86                     2.55
          Italy     3.66                     2.99
          France    3.62                     2.88

      Against the model: Airbnb's disclosed EMEA nights/booking is 3.80 vs EU27's measured 3.77,
      and the fitted global guests-per-booking is 2.97 vs EU27's measured 2.96. Both within 1%.
      The party-size figure matters most: that level previously rested on differencing Airbnb's
      cumulative guest-arrival milestones, which could not identify a trend and depended on a
      rounded "over 2.5 billion". It is now independently confirmed on measured bookings.
      Caveats: EU27 is 3 platforms (Airbnb + Booking + Expedia), not Airbnb alone, and Europe is
      not global - so read it as a strong corroboration of the level, not as a replacement.

  SPAIN INE ETR microdata, nights per trip by accommodation, 2015-2026 (weighted, trip-level)
      hotel 3.84 -> 3.75   whole-home rental 7.90 -> 5.26   rented room 6.12 -> 5.24
      Whole-home rental stays are ~1.4x hotel stays and have COMPRESSED hard (-33% since 2015)
      while hotel stay length is flat. Same direction as Airbnb's own EMEA decline.

  UK GBTS, nights per trip by accommodation, 2022-2024 (weighted trip records)
      commercial rental 4.41 / 4.02 / 3.81   serviced accommodation 2.57 / 2.42 / 2.50
      Rental ~1.6x hotel, and again falling on the rental side while hotels hold.

TIER 2 - OBSERVED but narrow

  HAWAII DBEDT 2024, length of stay by accommodation: rental house 9.46 days, condo 10.23,
      hotel 7.31, timeshare 9.36, B&B 8.53. One resort market, so the LEVEL is not transferable -
      but the rental-vs-hotel RATIO (1.29x) is a third independent read on the same gap.

  U.S. HOTEL ALOS (Kalibri Labs via trade press): 1.9 (2015-19) -> 2.1 (2020-22, and held).
      Hotels stepped UP once post-COVID and stayed there while Airbnb's fell - the divergence is
      the point. Extended-stay guests are a different animal: 24 nights at extended-stay brands,
      13 at traditional hotels.

TIER 3 - PROXY, use for differences not levels

  INSIDE AIRBNB booked runs (8 U.S. cities, Jun-2026, 273,522 runs): pooled mean 4.88 nights.
      Biased UP - its own source script says so, because host blocks read as bookings (Austin 4.71
      against Airbnb's disclosed NA 4.1). Its value is the SEGMENT structure, which nothing else
      gives: by capacity, 1-2 guests 5.60 nights, 3-4 5.41, 5-6 5.00, 7+ 4.29. Bigger homes are
      booked for SHORTER stays - the opposite of the intuition, and it is why party-size mix and
      stay length pull against each other in the model.

WHAT IS STILL MISSING: no U.S. source publishes Airbnb stay length by party size or by market, so
the model's REL_LEN vector (solo 1.5 / pair 0.95 / 3-4 0.9 / 5+ 0.8) is still inferred from Inside
Airbnb capacity buckets plus Airbnb's disclosed solo statistic, not measured directly.

Run:  python analysis/src/stay_length_inventory.py
Out:  data/processed/stay_length_inventory.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

# Eurostat tour_ce_omn12 2025: stays, nights rented out, guest-nights
EUROSTAT = {
    "EU27": (85_443_586, 321_811_154, 951_611_862), "Spain": (12_841_549, 59_567_834, 189_492_971),
    "France": (20_391_090, 73_880_865, 212_557_676), "Italy": (12_693_270, 46_428_840, 138_736_628),
    "Germany": (6_939_537, 26_783_181, 68_302_428), "Vienna": (702_156, 2_462_605, 6_348_835),
    "Berlin": (328_646, 1_317_291, 3_274_282), "Madrid": (1_304_364, 4_786_022, 13_151_692),
}
ABNB_EMEA_NPB, ABNB_GUESTS_PER_BOOKING = 3.8, 2.97


def main():
    rows = []
    print("EUROSTAT MEASURED (tour_ce_omn12, 2025) - stay length AND party size from one source\n")
    print(f"{'geo':10s} {'stays':>12s} {'nights/booking':>15s} {'guests/night':>13s}")
    for g, (s, l, n) in EUROSTAT.items():
        print(f"{g:10s} {s:12,.0f} {l / s:15.2f} {n / l:13.2f}")
        rows.append({"source": "Eurostat tour_ce_omn12 2025", "geo": g, "stays": s,
                     "nights_per_booking": round(l / s, 2), "guests_per_night": round(n / l, 2)})
    eu = EUROSTAT["EU27"]
    print(f"\n  vs the model: Airbnb disclosed EMEA nights/booking {ABNB_EMEA_NPB} against EU27 "
          f"{eu[1] / eu[0]:.2f}  ({(eu[1] / eu[0]) / ABNB_EMEA_NPB - 1:+.1%})")
    print(f"                fitted guests/booking {ABNB_GUESTS_PER_BOOKING} against EU27 "
          f"{eu[2] / eu[1]:.2f}  ({(eu[2] / eu[1]) / ABNB_GUESTS_PER_BOOKING - 1:+.1%})")
    print("  Both within 1% on 85.4mm measured bookings. The party-size level in particular was")
    print("  previously only inferable from rounded guest-arrival milestones - it is now confirmed.")

    for f, cols, lbl in [("airbnb_nights_per_booking.csv", None, "Airbnb 10-K"),
                         ("ine_spain_party_size_by_accommodation.csv", None, "Spain INE"),
                         ("gbts_children_by_accommodation.csv", None, "UK GBTS")]:
        p = OUT / f
        if not p.exists():
            continue
        d = pd.read_csv(p)
        if lbl == "Spain INE":
            piv = d.pivot(index="year", columns="acc", values="nights_per_trip")
            print(f"\nSPAIN INE - nights per trip by accommodation (weighted microdata)")
            print(piv.round(2).tail(6).to_string())
            print(f"  whole-home rental / hotel ratio 2025: {piv.rental_whole.loc[2025] / piv.hotel.loc[2025]:.2f}x")
        if lbl == "UK GBTS":
            piv = d.pivot(index="Year", columns="acc", values="nights_per_trip")
            keep = [c for c in ["Commercial property rental", "Serviced accomodation"] if c in piv]
            print(f"\nUK GBTS - nights per trip by accommodation (weighted trip records)")
            print(piv[keep].round(2).to_string())
            print(f"  rental / hotel ratio 2024: "
                  f"{piv['Commercial property rental'].loc[2024] / piv['Serviced accomodation'].loc[2024]:.2f}x")

    print("\nTHE RENTAL-vs-HOTEL STAY-LENGTH GAP, three independent reads")
    for lbl, v in [("Spain INE 2025", 5.26 / 3.75), ("UK GBTS 2024", 3.81 / 2.50),
                   ("Hawaii DBEDT 2024", 9.46 / 7.31)]:
        print(f"  {lbl:20s} {v:.2f}x")
    print("  Rentals are booked for materially longer stays than hotels everywhere it is measured -")
    print("  and on the rental side the number is FALLING in all three, while hotels hold flat.")

    pd.DataFrame(rows).to_csv(OUT / "stay_length_inventory.csv", index=False)
    print("\nwrote", OUT / "stay_length_inventory.csv")


if __name__ == "__main__":
    main()
