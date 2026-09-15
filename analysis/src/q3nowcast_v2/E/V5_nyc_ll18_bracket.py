"""
WP-K reviews index 2023 vintage, step 5: the NYC Local Law 18 bracket and the pre-registered test T3.

Inputs (all Inside Airbnb, CC BY 4.0, via the mirrors named in the manifest)
  2023-03-06 NYC reviews  C:/Users/krish/abnb_ia_capture/ia_reviews_vintage2023/united-states_ny_new-york-city_2023-03-06_reviews.csv.gz
  2025-09-01 NYC reviews  MAIN/data/raw/inside_airbnb_reviews/united-states_ny_new-york-city_2025-09-01_reviews.csv.gz (held)
  2026-08-10 NYC reviews and listings (held, same folder)
  2024-01-05 NYC listings (Kaggle re-upload, curated: zero-review listings dropped)
                          data/processed/github_altdata/samples/nyc-airbnb-listings-2024-01-05/new_york_listings_2024.csv

Writes data/processed/regulatory_v2/nyc_ll18_bracket.csv   (date, basis, listings_reviewed_ltm, min30_share,
                                                            entire_share, licensed_n, reviews_ltm_sum, review_flow_12m, source)
       data/processed/regulatory_v2/nyc_ll18_t3.csv         the T3 computation, every intermediate
       data/processed/regulatory_v2/nyc_monthly_reviews_by_vintage.csv

T3 as pre-registered: A (pre, Sep 2022 to Aug 2023) = 2023-vintage counts for the months complete at the 6 Mar 2023
dump (Sep 2022 to Jan 2023) plus 2025-vintage counts for Feb to Aug 2023 divided by r_pre (pooled 2025/2023 ratio
on Sep 2022 to Jan 2023); B (post, Sep 2023 to Aug 2024) = 2025-vintage counts divided by r_post = 0.86 (E table 2.2,
12 to 24 month old history). T3 = B / A - 1; pass band -40 to -70 percent.
Run: python analysis/src/q3nowcast_v2/E/V5_nyc_ll18_bracket.py
"""
import gzip, json, time
from pathlib import Path
import numpy as np, pandas as pd, pyarrow as pa
from pyarrow import csv as pacsv

WT = Path(__file__).resolve().parents[4]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
HELD = MAIN / "data/raw/inside_airbnb_reviews"
V23 = Path(r"C:\Users\krish\abnb_ia_capture\ia_reviews_vintage2023")
OUT = WT / "data/processed/regulatory_v2"
KAGGLE = WT / "data/processed/github_altdata/samples/nyc-airbnb-listings-2024-01-05/new_york_listings_2024.csv"
BENCH = WT / "research/regulatory/phase2/nyc_activity_benchmark.json"
R_POST = 0.86
BAND = (-70.0, -40.0)
FILES = {"2023-03-06": V23 / "united-states_ny_new-york-city_2023-03-06_reviews.csv.gz",
         "2025-09-01": HELD / "united-states_ny_new-york-city_2025-09-01_reviews.csv.gz",
         "2026-08-10": HELD / "united-states_ny_new-york-city_2026-08-10_reviews.csv.gz"}
LISTINGS_2026 = HELD / "united-states_ny_new-york-city_2026-08-10_listings.csv.gz"


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def read_reviews(path):
    co = pacsv.ConvertOptions(include_columns=["listing_id", "date"],
                              column_types={"listing_id": pa.int64(), "date": pa.string()})
    with gzip.open(path, "rb") as f:
        tb = pacsv.read_csv(f, read_options=pacsv.ReadOptions(use_threads=False),
                            parse_options=pacsv.ParseOptions(newlines_in_values=True), convert_options=co)
    df = tb.to_pandas()
    df["date"] = pd.to_datetime(df.date, errors="coerce")
    return df.dropna(subset=["date"])


def ymi(ts):
    return ts.dt.year * 12 + ts.dt.month - 1


def span(y0, m0, y1, m1):
    return list(range(y0 * 12 + m0 - 1, y1 * 12 + m1))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rv = {k: read_reviews(p) for k, p in FILES.items()}
    for k, d in rv.items():
        log(f"{k}: {len(d):,} reviews, {d.listing_id.nunique():,} listings, dates {d.date.min().date()} to {d.date.max().date()}")
    monthly = pd.DataFrame({k: ymi(d.date).value_counts().sort_index() for k, d in rv.items()}).fillna(0).astype(int)
    monthly.index.name = "ymi"
    monthly = monthly[monthly.index >= 2019 * 12].reset_index()
    monthly["ym"] = monthly.ymi.map(lambda i: f"{i // 12}-{i % 12 + 1:02d}")
    monthly.to_csv(OUT / "nyc_monthly_reviews_by_vintage.csv", index=False, encoding="utf-8")
    c = monthly.set_index("ymi")

    # ---- T3
    pre_complete = span(2022, 9, 2023, 1)         # complete at the 6 Mar 2023 dump (month end + 14 days <= dump)
    pre_rest = span(2023, 2, 2023, 8)
    post = span(2023, 9, 2024, 8)
    r_pre = c.loc[pre_complete, "2025-09-01"].sum() / c.loc[pre_complete, "2023-03-06"].sum()
    r_post_nyc = c.loc[post, "2026-08-10"].sum() / c.loc[post, "2025-09-01"].sum()
    A = c.loc[pre_complete, "2023-03-06"].sum() + c.loc[pre_rest, "2025-09-01"].sum() / r_pre
    A_raw25 = c.loc[pre_complete + pre_rest, "2025-09-01"].sum()
    B_raw = c.loc[post, "2025-09-01"].sum()
    B = B_raw / R_POST
    B_nyc = B_raw / r_post_nyc
    t3 = 100 * (B / A - 1)
    t3_nyc = 100 * (B_nyc / A - 1)
    t3_uncorrected = 100 * (B_raw / A_raw25 - 1)
    # cross-check against the Jan 2024 Kaggle file (reviews_ltm un-attrited as of 5 Jan 2024)
    kg = pd.read_csv(KAGGLE)
    kg_ltm = int(kg.number_of_reviews_ltm.sum())
    d25 = rv["2025-09-01"]
    win = (d25.date > "2023-01-05") & (d25.date <= "2024-01-05")
    ltm_in_2025 = int(win.sum())
    bench = json.load(open(BENCH, encoding="utf-8"))
    cra = [b for b in bench if b["metric"].startswith("Airbnb guest-nights")]
    cra_pct = 100 * (cra[1]["value"] / cra[0]["value"] - 1)
    rows = [
        ("r_pre: pooled 2025/2023 ratio, Sep 2022 to Jan 2023 (NYC pre-LL18 history attrition as of Sep 2025)", r_pre),
        ("n pre months in 2023 vintage (complete)", len(pre_complete)),
        ("reviews Sep 2022 to Jan 2023, 2023 vintage", int(c.loc[pre_complete, "2023-03-06"].sum())),
        ("reviews Sep 2022 to Jan 2023, 2025 vintage", int(c.loc[pre_complete, "2025-09-01"].sum())),
        ("reviews Feb to Aug 2023, 2025 vintage (raw)", int(c.loc[pre_rest, "2025-09-01"].sum())),
        ("A: pre-LL18 flow Sep 2022 to Aug 2023, attrition-corrected", A),
        ("A raw in the 2025 vintage (uncorrected)", int(A_raw25)),
        ("B raw: post flow Sep 2023 to Aug 2024 in the 2025 vintage", int(B_raw)),
        ("r_post used (E table 2.2, 12-24 month history)", R_POST),
        ("r_post NYC-specific sensitivity (2026-08 / 2025-09 on Sep 2023 to Aug 2024)", r_post_nyc),
        ("B: post flow corrected by r_post 0.86", B),
        ("B: post flow corrected by NYC-specific r_post", B_nyc),
        ("T3 = B/A - 1, percent (primary)", t3),
        ("T3 sensitivity with NYC-specific r_post, percent", t3_nyc),
        ("T3 uncorrected (both windows raw in the 2025 vintage), percent", t3_uncorrected),
        ("pass band lo, percent", BAND[0]), ("pass band hi, percent", BAND[1]),
        ("T3 PASS (primary inside band)", bool(BAND[0] <= t3 <= BAND[1])),
        ("CRA guest-nights benchmark, percent (Sep 2023-Aug 2024 vs prior year)", cra_pct),
        ("cross-check: Kaggle Jan 2024 file reviews_ltm sum (Jan 2023 to Jan 2024, as of 5 Jan 2024)", kg_ltm),
        ("cross-check: same window counted in the 2025-09-01 dump", ltm_in_2025),
        ("cross-check: ratio 2025 dump / Jan 2024 file", ltm_in_2025 / kg_ltm),
    ]
    t = pd.DataFrame(rows, columns=["item", "value"])
    t.to_csv(OUT / "nyc_ll18_t3.csv", index=False, encoding="utf-8")
    print(t.to_string(index=False))

    # ---- bracket: listings with >= 1 review in the trailing 365 days, as of each cross-section
    def ltm(d, dump):
        e = pd.Timestamp(dump); s = e - pd.Timedelta(days=365)
        w = d[(d.date > s) & (d.date <= e)]
        return w.listing_id.nunique(), len(w)
    br = []
    for k, d in rv.items():
        n_l, n_r = ltm(d, k)
        br.append(dict(date=k, basis="reviews dump; listings with >=1 review in the 365 days to the dump date",
                       listings_reviewed_ltm=n_l, min30_share=np.nan, entire_share=np.nan, licensed_n=np.nan,
                       reviews_ltm_sum=n_r, review_flow_12m=n_r,
                       source=("Inside Airbnb NYC reviews dump " + k + (" via HF mirror alujjdnd/Airbnb-Mar-2022-2023" if k < "2024" else " (held)"))))
    kg_active = kg[kg.number_of_reviews_ltm > 0]
    br.append(dict(date="2024-01-05", basis="listings file (curated Kaggle subset, zero-review listings dropped); number_of_reviews_ltm > 0",
                   listings_reviewed_ltm=int((kg.number_of_reviews_ltm > 0).sum()),
                   min30_share=float((kg.minimum_nights >= 30).mean()),
                   entire_share=float((kg.room_type == "Entire home/apt").mean()),
                   licensed_n=int(kg.license.fillna("").str.upper().str.startswith("OSE-STRREG").sum()),
                   reviews_ltm_sum=kg_ltm, review_flow_12m=kg_ltm,
                   source="Tracey-Sneed/New-York-Airbnb-Listings-2024 (Inside Airbnb 2024-01-05 dump, curated)"))
    l26 = pd.read_csv(LISTINGS_2026, usecols=["id", "room_type", "minimum_nights", "license", "number_of_reviews_ltm"])
    i26 = [i for i, r in enumerate(br) if r["date"] == "2026-08-10"][0]
    br[i26].update(min30_share=float((l26.minimum_nights >= 30).mean()),
                   entire_share=float((l26.room_type == "Entire home/apt").mean()),
                   licensed_n=int(l26.license.fillna("").str.upper().str.startswith("OSE-STRREG").sum()),
                   basis=br[i26]["basis"] + "; shares and licence count from the same-date listings dump (all listings)")
    br.append(dict(date="2023-08-31", basis="T3 window A: Sep 2022 to Aug 2023 review flow, attrition-corrected (2023 vintage + 2025 vintage / r_pre)",
                   listings_reviewed_ltm=np.nan, min30_share=np.nan, entire_share=np.nan, licensed_n=np.nan,
                   reviews_ltm_sum=int(A_raw25), review_flow_12m=A, source="this script, nyc_ll18_t3.csv"))
    br.append(dict(date="2024-08-31", basis="T3 window B: Sep 2023 to Aug 2024 review flow, attrition-corrected (2025 vintage / 0.86)",
                   listings_reviewed_ltm=np.nan, min30_share=np.nan, entire_share=np.nan, licensed_n=np.nan,
                   reviews_ltm_sum=int(B_raw), review_flow_12m=B, source="this script, nyc_ll18_t3.csv"))
    b = pd.DataFrame(br).sort_values("date")
    b.to_csv(OUT / "nyc_ll18_bracket.csv", index=False, encoding="utf-8")
    print(b[["date", "listings_reviewed_ltm", "min30_share", "entire_share", "licensed_n", "reviews_ltm_sum", "review_flow_12m"]].round(3).to_string(index=False))
