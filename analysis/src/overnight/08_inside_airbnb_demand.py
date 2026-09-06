"""08_inside_airbnb_demand.py -- Inside Airbnb demand proxies on a fixed 13-city panel.

Reads:  data/raw/inside_airbnb/*_listings.parquet (168 dumps, 13 cities, Dec 2022 to Aug 2026),
        data/raw/inside_airbnb/manifest.csv, data/processed/inside_airbnb_city_snapshots.csv (partial_scope flag).
Writes: data/processed/overnight/08_ia_dump_metrics.csv   one row per dump: listings, reviews_ltm, reviews_l30d,
            blocked share at 30/90 days (1 - availability/days, listings with has_availability), like-for-like
            reviews on ids matched to the year-ago dump of the same city.
        data/processed/overnight/08_ia_city_yoy.csv       per city x dump: y/y of reviews_ltm (all and matched ids),
            reviews_l30d, blocked_30, blocked_90, listings, vs the year-ago dump (270-460 days back).
Notes:  reviews_l30d and availability are point-in-time on the scrape date, so y/y needs a dump ~365 days earlier.
        availability 'f' conflates booked, host-blocked and inactive (Theo's caveat) - blocked share is a proxy.
"""
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/inside_airbnb"
OUT = ROOT / "data/processed/overnight"
COLS = ["id", "room_type", "has_availability", "availability_30", "availability_90",
        "number_of_reviews_ltm", "number_of_reviews_l30d", "minimum_nights"]

def load(p):
    t = pq.read_table(p, columns=[c for c in COLS if c in pq.read_schema(p).names]).to_pandas()
    for c in ["availability_30", "availability_90", "number_of_reviews_ltm", "number_of_reviews_l30d"]:
        if c in t: t[c] = pd.to_numeric(t[c], errors="coerce")
    t["id"] = t["id"].astype(str)
    return t

def main():
    snaps = pd.read_csv(ROOT / "data/processed/inside_airbnb_city_snapshots.csv")
    snaps["dump_date"] = pd.to_datetime(snaps["dump_date"])
    scope = snaps.set_index(["city", "dump_date"])["partial_scope"].to_dict()
    files = sorted(RAW.glob("*_listings.parquet"))
    data = {}
    rows = []
    for p in files:
        city, date = p.name.rsplit("_listings.parquet", 1)[0].rsplit("_", 1)
        d = pd.Timestamp(date)
        t = load(p)
        data[(city, d)] = t
        av = t[t["has_availability"].astype(str).str.lower().isin(["t", "true", "1"])] if "has_availability" in t else t
        rows.append(dict(city=city, dump_date=d, listings=len(t),
                         reviews_ltm=t["number_of_reviews_ltm"].sum(), reviews_l30d=t["number_of_reviews_l30d"].sum(),
                         n_avail=len(av),
                         blocked_30=1 - av["availability_30"].mean() / 30, blocked_90=1 - av["availability_90"].mean() / 90,
                         entire_share=(t["room_type"] == "Entire home/apt").mean(),
                         partial_scope=bool(scope.get((city, d), False))))
        print(city, date, len(t), flush=True)
    m = pd.DataFrame(rows).sort_values(["city", "dump_date"])
    # year-ago pairs
    yy = []
    for (city, d), t in data.items():
        cand = [(c, dd) for (c, dd) in data if c == city and 270 <= (d - dd).days <= 460]
        if not cand: continue
        c0, d0 = min(cand, key=lambda k: abs((d - k[1]).days - 365))
        t0 = data[(c0, d0)]
        j = t[["id", "number_of_reviews_ltm", "number_of_reviews_l30d", "availability_30", "availability_90"]].merge(
            t0[["id", "number_of_reviews_ltm", "number_of_reviews_l30d", "availability_30", "availability_90"]], on="id", suffixes=("_b", "_a"))
        a_row = m[(m.city == city) & (m.dump_date == d0)].iloc[0]; b_row = m[(m.city == city) & (m.dump_date == d)].iloc[0]
        yy.append(dict(city=city, dump_date=d, yearago_date=d0, days_apart=(d - d0).days, matched=len(j),
                       partial_scope=b_row.partial_scope or a_row.partial_scope,
                       listings_yoy=b_row.listings / a_row.listings - 1,
                       reviews_ltm_all_yoy=b_row.reviews_ltm / a_row.reviews_ltm - 1,
                       reviews_l30d_all_yoy=b_row.reviews_l30d / a_row.reviews_l30d - 1 if a_row.reviews_l30d else np.nan,
                       reviews_ltm_matched_yoy=j["number_of_reviews_ltm_b"].sum() / j["number_of_reviews_ltm_a"].sum() - 1,
                       reviews_l30d_matched_yoy=j["number_of_reviews_l30d_b"].sum() / j["number_of_reviews_l30d_a"].sum() - 1 if j["number_of_reviews_l30d_a"].sum() else np.nan,
                       blocked_30_yoy_pts=b_row.blocked_30 - a_row.blocked_30, blocked_90_yoy_pts=b_row.blocked_90 - a_row.blocked_90,
                       blocked_30_matched_yoy_pts=(1 - j["availability_30_b"].mean() / 30) - (1 - j["availability_30_a"].mean() / 30)))
    y = pd.DataFrame(yy).sort_values(["city", "dump_date"])
    OUT.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT / "08_ia_dump_metrics.csv", index=False)
    y.to_csv(OUT / "08_ia_city_yoy.csv", index=False)
    print("wrote", len(m), len(y))

if __name__ == "__main__":
    main()
