"""
Rental vs hotel party size: how far does the Hawaii finding generalise?

The nights model's split mix-drift (MIX_DRIFT_ABNB vs MIX_DRIFT_HOTEL) rests on one number:
Hawaii DBEDT's observation that rental-house parties grew +0.80%/yr while hotel parties grew
+0.34%/yr (2013-2024) - a 2.35x ratio from a SINGLE market. This script tests that against every
other source we have, and separates what is now well-supported from what still is not.

TWO CLAIMS, VERY DIFFERENT EVIDENCE:

  LEVEL GAP (rental parties are bigger than hotel parties)  -> STRONGLY VALIDATED
    Booking.com rectour24, 1.63m stays, 2023, 40 countries with >=500 reviews on both sides:
    whole-home analogues (Holiday home / Villa / Chalet / Country house / Apartment) vs Hotel.
    Rental > hotel in 39 of 40 countries, mean gap +0.35 people, mean ratio 1.131x, paired
    t = 10.2. The single exception is Thailand (0.93x).

  TREND DIVERGENCE (rental parties growing FASTER than hotel parties) -> STILL ONE MARKET
    Hawaii DBEDT remains the only source observing both accommodation types on the same
    instrument over a long horizon. Attempts to find a second:
      - Booking.com 515k (Europe hotels, 2015-08..2017-08): 25 months, ~2 summers, so month
        dummies and a trend are not jointly identified. It returns +3.9%/yr, which is not
        credible next to Hawaii's +0.34%/yr - treated as noise, not as a contradiction.
      - rectour24 is a single year (2023) - it can only speak to the level.
      - Tourism Research Australia, VisitBritain GBTS and Statistics Canada's NTS all collect
        party size AND accommodation type, but publish them as separate marginals; the cross-tab
        appears to live only in microdata (PUMF / data request). That is the next pull.

  A COUNTER-SIGNAL worth carrying: VisitBritain reports UK solo overnight trips at 28% in 2024,
  +3pp on 2023 and +4pp on 2022. Rising solo travel pushes mean party size DOWN and is a genuine
  offset to the family-mix story, in at least one large market.

THE CAVEAT THAT MATTERS MOST FOR THIS MODEL: the gap is weakest where we need it. The U.S. ranks
33rd of 40 at 1.051x against a 1.131x mean, and Hawaii (1.080x) is also below the mean. So the
party-size differentiation the thesis leans on is smaller in Airbnb's largest market than in
Europe. Two readings, both worth stating: (a) Booking's U.S. non-hotel inventory is thin
(2,165 whole-home reviews vs 134,537 hotel) and skews aparthotel/extended-stay rather than the
detached whole homes Airbnb sells, so the U.S. number is probably understated; (b) if it is not
understated, the U.S. mix tailwind is genuinely weaker than the global figure implies and
MIX_DRIFT_ABNB should be cut further.

Run:  python analysis/src/party_size_rental_vs_hotel.py
Out:  data/processed/party_size_rental_vs_hotel_by_country.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed"

# Same composition weights as the Airbnb review proxy, so the two are on one scale.
W = {"solo": 1.0, "couple": 2.0, "family": 3.9, "group": 4.7}
WHOLE_HOME = {"Holiday home", "Villa", "Chalet", "Country house", "Apartment"}
MIN_N = 500


def main():
    d = pd.read_csv(OUT / "booking_rectour24_guest_type_by_country_type.csv")
    d["implied"] = sum(d[k] * W[k] for k in W)

    rent = (d[d.accommodation_type.isin(WHOLE_HOME)]
            .groupby("accommodation_country")
            .apply(lambda x: pd.Series({"rental_implied": np.average(x.implied, weights=x.reviews),
                                        "rental_n": x.reviews.sum()}), include_groups=False))
    hot = (d[d.accommodation_type == "Hotel"].set_index("accommodation_country")
           [["implied", "reviews"]].rename(columns={"implied": "hotel_implied", "reviews": "hotel_n"}))
    m = rent.join(hot, how="inner")
    m = m[(m.rental_n >= MIN_N) & (m.hotel_n >= MIN_N)].copy()
    m["gap"] = m.rental_implied - m.hotel_implied
    m["ratio"] = m.rental_implied / m.hotel_implied
    m = m.sort_values("gap", ascending=False)

    g = m.gap
    t = g.mean() / (g.std() / np.sqrt(len(g)))
    print(f"LEVEL GAP - whole-home vs hotel, {len(m)} countries (Booking rectour24, 2023, 1.63m stays)")
    print(f"  rental > hotel in {(g > 0).sum()}/{len(m)}   mean gap {g.mean():+.3f} people "
          f"({m.ratio.mean():.3f}x)   paired t = {t:.1f}")
    print(f"  only exception: {m.index[-1]} ({m.ratio.iloc[-1]:.3f}x)")

    us = m.loc["United States of America"]
    rank = int((m.ratio > us.ratio).sum()) + 1
    print(f"\n  U.S.: {us.ratio:.3f}x, rank {rank}/{len(m)} - BELOW the {m.ratio.mean():.3f}x mean.")
    print(f"        (whole-home n={us.rental_n:.0f} vs hotel n={us.hotel_n:.0f}; thin and "
          f"aparthotel-skewed, so probably understated)")
    print(f"  Hawaii 2024 observed: 2.489 / 2.304 = 1.080x - also below the mean.")

    print("\nTREND DIVERGENCE - still Hawaii-only:")
    h = pd.read_csv(OUT / "hawaii_party_size_annual.csv")
    p = (h[h.segment.isin(["hotel", "rental_house"]) & h.avg_party_size.notna()]
         .pivot_table(index="year", columns="segment", values="avg_party_size").dropna())
    for seg in ("rental_house", "hotel"):
        r = (p[seg].loc[2024] / p[seg].loc[2013]) ** (1 / 11) - 1
        print(f"  Hawaii {seg:13s} {p[seg].loc[2013]:.2f} -> {p[seg].loc[2024]:.2f}  {r * 100:+.2f}%/yr")
    ratio = (((p.rental_house.loc[2024] / p.rental_house.loc[2013]) ** (1 / 11) - 1) /
             ((p.hotel.loc[2024] / p.hotel.loc[2013]) ** (1 / 11) - 1))
    print(f"  => rental drifts {ratio:.2f}x faster. THIS IS THE MODEL'S MIX-DRIFT RATIO, n=1 market.")
    print("  No second long-horizon source found; TRA / VisitBritain / StatCan hold the cross-tab")
    print("  only in microdata. Counter-signal: UK solo overnight trips 28% in 2024, +4pp vs 2022.")

    m.round(4).to_csv(OUT / "party_size_rental_vs_hotel_by_country.csv")
    print("\nwrote", OUT / "party_size_rental_vs_hotel_by_country.csv")
    print("\nNOTE: rectour24 is CC BY-SA 4.0, licensed NON-COMMERCIAL. Fine for internal validation;")
    print("it must not be reproduced in anything client-facing or published.")


if __name__ == "__main__":
    main()
