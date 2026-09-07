"""
Hotel party size: guests per stay, built two ways.

A) Per room-booking (the transactions lens - comparable to Airbnb's "per booking"):
   Hotel Booking Demand dataset (Antonio, de Almeida & Nunes 2019, Data in Brief 22:41-49):
   119k real reservations at a city hotel and a resort hotel in Portugal, 2015-2017, with
   adults/children/babies per booking. Completed stays only. Corporate vs leisure segments
   give the business/leisure shapes; the U.S. mix weights them by AHLA's 2023 room-night split
   (business 439M / leisure 605M).

B) Per travel party (who is choosing hotel vs Airbnb): U.S. leisure-market surveys -
   Hawaii DBEDT 2024 hotel-only visitors (1 / 2 / 3+ = 29 / 43 / 29%, avg 2.30) and the
   Las Vegas Visitor Profile 2024 (1 / 2 / 3 / 4 / 5+ = 12 / 64 / 11 / 9 / 6%), blended with
   the corporate booking shape at the AHLA business share.

Run:  python analysis/src/hotel_party_size.py
Out:  data/processed/hotel_party_size_distribution.csv
"""
import io
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed/hotel_party_size_distribution.csv"
RAW = ROOT / "data/raw/hotel_bookings_portugal.csv"  # data/raw is gitignored
URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv"

BUSINESS_SHARE = 439 / (439 + 605)  # AHLA 2024 State of the Industry: 2023 U.S. room nights
SIZES = [1, 2, 3, 4, 5]             # 5 = "5+"
TAIL = np.array([1, 2, 3, 4, 5.5])


def dist(series: pd.Series) -> np.ndarray:
    return series.clip(upper=5).value_counts(normalize=True).reindex(SIZES).fillna(0).values


def main():
    if RAW.exists():
        df = pd.read_csv(RAW)
    else:
        df = pd.read_csv(io.BytesIO(urlopen(URL).read()))
        RAW.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(RAW, index=False)
    d = df[df.is_canceled == 0].copy()
    d["party"] = (d.adults + d.children.fillna(0) + d.babies).astype(int)
    d = d[(d.party >= 1) & (d.party <= 12)]
    d["nights"] = d.stays_in_weekend_nights + d.stays_in_week_nights

    all_ = dist(d.party)
    corp = dist(d[d.market_segment == "Corporate"].party)
    leis = dist(d[d.market_segment.isin(["Online TA", "Direct", "Offline TA/TO"])].party)
    us_room = BUSINESS_SHARE * corp + (1 - BUSINESS_SHARE) * leis

    # B) travel party: leisure shape = mean of Hawaii hotel-only and Las Vegas 2024 (3+ split by Vegas ratio)
    hawaii = np.array([0.288, 0.425, 0.287 * 11 / 26, 0.287 * 9 / 26, 0.287 * 6 / 26])
    vegas = np.array([0.12, 0.64, 0.11, 0.09, 0.06])
    leisure_party = (hawaii + vegas) / 2
    us_party = BUSINESS_SHARE * corp + (1 - BUSINESS_SHARE) * leisure_party

    out = pd.DataFrame({
        "party_size": ["1", "2", "3", "4", "5+"],
        "portugal_all_bookings": all_.round(3),
        "portugal_corporate": corp.round(3),
        "portugal_leisure": leis.round(3),
        "us_per_room_booking_est": us_room.round(3),
        "hawaii_hotel_only_2024": hawaii.round(3),
        "las_vegas_2024": vegas.round(3),
        "us_travel_party_est": us_party.round(3),
    })
    print(out.to_string(index=False))
    for c in out.columns[1:]:
        print(f"{c:28s} mean {float(np.dot(out[c], TAIL)):.2f}  P(3+) {out[c][2:].sum():.2f}")
    print("\nPortugal nights by party:", d.groupby(d.party.clip(upper=5)).nights.mean().round(2).to_dict())
    print("Portugal stays:", len(d), " corporate mean party", round(d[d.market_segment == 'Corporate'].party.mean(), 2))
    out.to_csv(OUT, index=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
