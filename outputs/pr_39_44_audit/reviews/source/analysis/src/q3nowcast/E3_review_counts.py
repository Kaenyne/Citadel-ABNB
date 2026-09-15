"""
Q3 2026 nowcast, workstream E, step 3a: turn every Inside Airbnb reviews.csv.gz dump into monthly
review counts by market and dump vintage, with a listing-age split so survivorship can be handled.

Per reviews file (one market x one dump vintage) it writes:
  cache/<market>_<vintage>_listing_month.parquet   listing_id, ym (YYYYMM), n      (intermediate, not committed)
and appends to two committed tables:
  market_vintage_monthly.csv   market_key, cdn_path, dump_date, ym, n_reviews, n_listings,
                               n_reviews_mature12, n_reviews_mature24, n_new_listing_cohort
  market_vintage_daily.csv     daily counts for the 210 days before the dump date (truncation / posting lag)

"mature12" = reviews written by listings whose FIRST review in this dump is at least 12 months before the
review month. It is the within-vintage control for new-listing growth. Survivorship (a dump only holds
listings alive at dump time) is handled in E4 by comparing vintages.

Reviews carry a review date, not a stay date: the schema is listing_id, id, date, reviewer_id,
reviewer_name, comments. There is no stay date field, so the review date is used as a stay-date proxy.
Airbnb opens the review window at check-out and closes it 14 days later, so a review date is a
check-out date plus 0 to 14 days (assumed; the completeness curve measured in E4 is the evidence).

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC-BY 4.0.
Run: py -3.13 analysis/src/q3nowcast/E3_review_counts.py [--only 2026-08] [--workers 3]
"""
import argparse, gzip, time
from pathlib import Path
import numpy as np, pandas as pd, pyarrow as pa
from pyarrow import csv as pacsv

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
REV = MAIN / "data/raw/inside_airbnb_reviews"
OUT = WT / "data/processed/q3nowcast/E"
CACHE = OUT / "cache"


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def parse_name(fn):
    stem = fn[: -len("_reviews.csv.gz")]
    parts = stem.split("_")
    return "/".join(parts[:-1]), parts[-1]


def one(path: Path):
    cdn_path, vintage = parse_name(path.name)
    mkt = cdn_path.replace("/", "_")
    pq = CACHE / f"{mkt}_{vintage}_listing_month.parquet"
    dailyp = CACHE / f"{mkt}_{vintage}_daily.csv"
    if pq.exists() and dailyp.exists():
        lm = pd.read_parquet(pq)
    else:
        co = pacsv.ConvertOptions(include_columns=["listing_id", "date"],
                                  column_types={"listing_id": pa.int64(), "date": pa.string()})
        with gzip.open(path, "rb") as f:
            tb = pacsv.read_csv(f, read_options=pacsv.ReadOptions(use_threads=False),
                                parse_options=pacsv.ParseOptions(newlines_in_values=True),
                                convert_options=co)
        df = tb.to_pandas()
        d = pd.to_datetime(df["date"], errors="coerce")
        df = df.assign(ymi=(d.dt.year * 12 + d.dt.month - 1).astype("float")).dropna(subset=["ymi"])
        df["ymi"] = df["ymi"].astype("int32")
        df["listing_id"] = df["listing_id"].astype("int64")
        lm = df.groupby(["listing_id", "ymi"], sort=False).size().reset_index(name="n")
        lm["n"] = lm["n"].astype("int32")
        # daily counts from 2021-01-01 on: needed for the day-matched partial-month y/y and for the
        # review-posting completeness curve (how much of a date is posted k days later)
        vd = pd.Timestamp(vintage)
        dd = d[(d >= pd.Timestamp("2021-01-01")) & (d <= vd + pd.Timedelta(days=30))]
        dday = dd.dt.date.value_counts().sort_index().rename_axis("review_date").reset_index(name="n_reviews")
        dday.insert(0, "dump_date", vintage)
        dday.insert(0, "market_key", mkt)
        CACHE.mkdir(parents=True, exist_ok=True)
        dday.to_csv(dailyp, index=False)
        lm.to_parquet(pq, index=False)
    first = lm.groupby("listing_id", sort=False)["ymi"].min().rename("first_ymi")
    lm = lm.join(first, on="listing_id")
    age = lm["ymi"] - lm["first_ymi"]
    g = lm.groupby("ymi")
    out = pd.DataFrame({
        "n_reviews": g["n"].sum(),
        "n_listings": g["listing_id"].nunique(),
        "n_reviews_mature12": lm[age >= 12].groupby("ymi")["n"].sum(),
        "n_reviews_mature24": lm[age >= 24].groupby("ymi")["n"].sum(),
        "n_new_listing_cohort": lm[age == 0].groupby("ymi")["listing_id"].nunique(),
    }).fillna(0).reset_index()
    out.insert(0, "dump_date", vintage)
    out.insert(0, "cdn_path", cdn_path)
    out.insert(0, "market_key", mkt)
    out["ym"] = (out.ymi // 12).astype(str) + "-" + (out.ymi % 12 + 1).map(lambda m: f"{m:02d}")
    for c in ["n_reviews", "n_listings", "n_reviews_mature12", "n_reviews_mature24", "n_new_listing_cohort"]:
        out[c] = out[c].astype("int64")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="substring filter on the filename, e.g. 2026-08")
    ap.add_argument("--exclude", default="", help="substring to exclude from the filename")
    ap.add_argument("--min-ym", type=int, default=2015 * 12, help="drop months before this month index")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in REV.glob("*_reviews.csv.gz")
                   if a.only in p.name and not (a.exclude and a.exclude in p.name))
    log(f"{len(files)} reviews files to process")

    def flush(parts):
        mp = OUT / "market_vintage_monthly.csv"
        mv = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        if mp.exists():
            prev = pd.read_csv(mp)
            mv = (pd.concat([prev, mv], ignore_index=True) if len(mv) else prev)
            mv = mv.drop_duplicates(["market_key", "dump_date", "ymi"], keep="last")
        mv.sort_values(["market_key", "dump_date", "ymi"]).to_csv(mp, index=False, encoding="utf-8")
        return mv

    parts = []
    if a.workers > 1:
        import concurrent.futures as cf
        with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(one, p): p for p in files}
            for i, f in enumerate(cf.as_completed(futs), 1):
                p = futs[f]
                try:
                    o = f.result()
                    parts.append(o[o.ymi >= a.min_ym])
                    log(f"[{i}/{len(files)}] {p.name} rows {len(o)}")
                except Exception as e:
                    log(f"[{i}/{len(files)}] FAILED {p.name}: {e}")
                if i % 25 == 0:
                    flush(parts)
                    parts = []
    else:
        for i, p in enumerate(files, 1):
            try:
                o = one(p)
                parts.append(o[o.ymi >= a.min_ym])
                log(f"[{i}/{len(files)}] {p.name} rows {len(o)}")
            except Exception as e:
                log(f"[{i}/{len(files)}] FAILED {p.name}: {e}")
            if i % 25 == 0:                  # checkpoint, the job can be killed and resumed
                flush(parts)
                parts = []
    mv = flush(parts)
    log(f"market_vintage_monthly.csv {len(mv)} rows, {mv.market_key.nunique()} markets, "
        f"{mv.groupby(['market_key', 'dump_date']).ngroups} market-vintages")
    dl = pd.concat([pd.read_csv(p) for p in sorted(CACHE.glob("*_daily.csv"))], ignore_index=True)
    dl.to_csv(OUT / "market_vintage_daily.csv", index=False, encoding="utf-8")
    log(f"market_vintage_daily.csv {len(dl)} rows")

