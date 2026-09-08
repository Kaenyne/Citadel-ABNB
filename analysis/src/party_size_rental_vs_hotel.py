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
      - PULLED 8 Sep 2026, all three:
        * Tourism Research Australia - the party-size x accommodation cross-tab is only in
          TRA Online, a PAID SUBSCRIBER portal. Not accessible. (Also note the National Visitor
          Survey ended Dec-2024 and is replaced by Domestic Tourism Statistics from Jan-2025,
          so any TRA series breaks there anyway.)
        * Statistics Canada NTS - public tables carry party size and accommodation type as
          separate marginals; StatCan's own guidance is to email tourism@statcan.gc.ca for the
          cross-tab. Not obtainable without a data request.
        * VisitBritain GBTS - SUCCESS, partially. The 2022-24 pivot workbook has trip-level
          records with "Main Accommodation Type" x "Children on trip", weighted. No party-size
          field, but children-on-trip is the sharper family measure and the thesis is about
          families. Results in gbts_children_by_accommodation.csv and below.

  WHAT THE UK DATA SAYS (share of overnight trips including a child, weighted, GB):
        year   commercial property rental   serviced accommodation   gap      ratio
        2022              37.7%                    25.3%            12.4pp    1.49x
        2023              39.2%                    23.9%            15.3pp    1.64x
        2024              33.7%                    22.3%            11.4pp    1.51x
    LEVEL: confirmed, and more sharply than rectour24 - UK rental trips are ~1.5x more likely to
    include children than hotel trips, in a second market on a single instrument.
    TREND: NOT confirmed. The gap widened then narrowed and is 1.0pp LOWER in 2024 than 2022.
    Both categories' family share FELL in 2024, consistent with VisitBritain's separate finding
    that solo trips rose to 28% (+4pp vs 2022). Three years, one of them a COVID-recovery year,
    so this cannot refute Hawaii - but it does not support the divergence either.

  A COUNTER-SIGNAL worth carrying: VisitBritain reports UK solo overnight trips at 28% in 2024,
  +3pp on 2023 and +4pp on 2022 (GB Tourist 2024 report, p41; full distribution 28 / 35 / 24 / 9 / 3%
  for solo / 2 / 3-4 / 5-9 / 10+). Rising solo travel pushes mean party size DOWN and is a genuine
  offset to the family-mix story, in a large market, from a primary source.

  NET READ AFTER THE THREE PULLS: the LEVEL gap now has three independent confirmations (Hawaii,
  40-country Booking cross-section, UK trip survey). The TREND divergence still has exactly one
  supporting market (Hawaii) and one market that does not support it (UK). The model's 2.35x
  mix-drift ratio should be treated as the optimistic case, not as an established fact.

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

    uk = pd.read_csv(OUT / "gbts_children_by_accommodation.csv")
    uk = uk[uk.acc.isin(["Commercial property rental", "Serviced accomodation"])]
    up = uk.pivot(index="Year", columns="acc", values="share_with_children")
    up["gap_pp"] = (up["Commercial property rental"] - up["Serviced accomodation"]) * 100
    up["ratio"] = up["Commercial property rental"] / up["Serviced accomodation"]
    print("\nUK GBTS - share of overnight trips including a child, by accommodation type:")
    print((up[["Commercial property rental", "Serviced accomodation"]] * 100).round(1).to_string())
    print(up[["gap_pp", "ratio"]].round(3).to_string())
    print(f"  LEVEL confirmed ({up.ratio.mean():.2f}x mean). TREND not confirmed: gap "
          f"{up.gap_pp.loc[2022]:.1f}pp (2022) -> {up.gap_pp.loc[2024]:.1f}pp (2024).")

    m.round(4).to_csv(OUT / "party_size_rental_vs_hotel_by_country.csv")
    print("\nwrote", OUT / "party_size_rental_vs_hotel_by_country.csv")
    print("\nNOTE: rectour24 is CC BY-SA 4.0, licensed NON-COMMERCIAL. Fine for internal validation;")
    print("it must not be reproduced in anything client-facing or published.")


if __name__ == "__main__":
    main()
