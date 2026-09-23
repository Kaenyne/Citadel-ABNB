"""los_nowcast / seats_check.py — receipt for prereg section 4: does Inside Airbnb see Airbnb's hotel business?
Counts 'Hotel room' listings and their trailing-12-month reviews in every local listings dump for the cities the 2Q26
letter names as hotel-launch markets (plus LA, Mexico City, Barcelona). The letter reports thousands of hotels added
across 20+ destinations including New York, Paris, London, Madrid, Rome and Singapore."""
from __future__ import annotations
import re
import duckdb
import pandas as pd
from . import config as C

MARKETS = ["new-york-city", "paris", "london", "rome", "los-angeles", "mexico-city", "barcelona"]


def run() -> pd.DataFrame:
    con = duckdb.connect(); rows = []
    for m in MARKETS:
        for f in sorted(C.LST.glob(f"{m}_*_listings.parquet")):
            d = re.search(r"_(\d{4}-\d{2}-\d{2})_", f.name).group(1)
            if d < "2025-01-01":
                continue
            p = str(f).replace("\\", "/")
            n, nh, rh, rt = con.execute(
                "SELECT count(*), sum(CASE WHEN room_type='Hotel room' THEN 1 ELSE 0 END), "
                "sum(CASE WHEN room_type='Hotel room' THEN coalesce(try_cast(number_of_reviews_ltm AS INTEGER),0) ELSE 0 END), "
                f"sum(coalesce(try_cast(number_of_reviews_ltm AS INTEGER),0)) FROM read_parquet('{p}')").fetchone()
            rows.append(dict(market=m, dump=d, listings=n, hotel_room_listings=nh, hotel_room_reviews_ltm=rh, all_reviews_ltm=rt,
                             hotel_review_share=rh / rt if rt else None))
    return pd.DataFrame(rows)
