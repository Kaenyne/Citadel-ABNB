"""
WP-K reviews index 2023 vintage, step 2: a copy of analysis/src/q3nowcast/E3_review_counts.py that reads
reviews files from TWO folders (the held MAIN store and the new 2023-vintage store) and writes to the
NEW folder data/processed/q3nowcast_v2/E/. The v1 per-file caches are copied from the q3nowcast worktree
so only the 2023 files are counted afresh. Counting logic is identical to E3 (pyarrow read of listing_id
and date, group listing x month, mature12 / mature24 / new-cohort splits, daily counts from 2021).

Writes data/processed/q3nowcast_v2/E/
  market_vintage_monthly.csv   held vintages (recomputed from the v1 caches) + 2023 vintages
  market_vintage_daily.csv     daily counts for every file
  v1_consistency_check.csv     held rows recomputed here vs the tracked v1 table (must be identical)

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC BY 4.0.
Run: python analysis/src/q3nowcast_v2/E/V2_review_counts_two_folders.py [--workers 3] [--only 2023-]
"""
import argparse, gzip, shutil, time
from pathlib import Path
import numpy as np, pandas as pd, pyarrow as pa
from pyarrow import csv as pacsv

WT = Path(__file__).resolve().parents[4]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
REV_DIRS = [MAIN / "data/raw/inside_airbnb_reviews",
            Path(r"C:\Users\krish\abnb_ia_capture\ia_reviews_vintage2023")]
V1_CACHE = Path(r"C:\Users\krish\citadel-abnb-q3nowcast\data\processed\q3nowcast\E\cache")
V1_OUT = WT / "data/processed/q3nowcast/E"
OUT = WT / "data/processed/q3nowcast_v2/E"
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


def seed_cache():
    """Copy the v1 per-file caches (parquet + daily csv) so the held files are not re-read."""
    CACHE.mkdir(parents=True, exist_ok=True)
    n = 0
    if V1_CACHE.exists():
        for p in V1_CACHE.iterdir():
            q = CACHE / p.name
            if not q.exists() or q.stat().st_size != p.stat().st_size:
                shutil.copy2(p, q)
                n += 1
    log(f"seeded {n} cache files from {V1_CACHE} ({len(list(CACHE.iterdir()))} now in cache)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--min-ym", type=int, default=2015 * 12)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    seed_cache()
    files = sorted(p for d in REV_DIRS for p in d.glob("*_reviews.csv.gz") if a.only in p.name)
    log(f"{len(files)} reviews files across {len(REV_DIRS)} folders")

    def flush(parts):
        mp = OUT / "market_vintage_monthly.csv"
        mv = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        if mp.exists():
            prev = pd.read_csv(mp)
            mv = (pd.concat([prev, mv], ignore_index=True) if len(mv) else prev)
            mv = mv.drop_duplicates(["market_key", "dump_date", "ymi"], keep="last")
        mv.sort_values(["market_key", "dump_date", "ymi"]).to_csv(mp, index=False, encoding="utf-8")
        return mv

    # files whose cache exists are cheap; do them in the parent. Uncached ones go to the pool.
    cached = [p for p in files if (CACHE / f"{parse_name(p.name)[0].replace('/', '_')}_{parse_name(p.name)[1]}_listing_month.parquet").exists()]
    fresh = [p for p in files if p not in cached]
    log(f"{len(cached)} cached, {len(fresh)} to count afresh")
    parts, failed = [], []
    for i, p in enumerate(cached, 1):
        o = one(p)
        parts.append(o[o.ymi >= a.min_ym])
        if i % 100 == 0:
            log(f"cached [{i}/{len(cached)}]")
    flush(parts); parts = []
    if fresh:
        import concurrent.futures as cf
        with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(one, p): p for p in fresh}
            for i, f in enumerate(cf.as_completed(futs), 1):
                p = futs[f]
                try:
                    o = f.result()
                    parts.append(o[o.ymi >= a.min_ym])
                    log(f"[{i}/{len(fresh)}] {p.name} rows {len(o)}")
                except Exception as e:
                    failed.append(p.name)
                    log(f"[{i}/{len(fresh)}] FAILED {p.name}: {e}")
                if i % 10 == 0:
                    flush(parts); parts = []
    mv = flush(parts)
    log(f"market_vintage_monthly.csv {len(mv)} rows, {mv.market_key.nunique()} markets, "
        f"{mv.groupby(['market_key', 'dump_date']).ngroups} market-vintages; failed {failed}")
    dl = pd.concat([pd.read_csv(p) for p in sorted(CACHE.glob("*_daily.csv"))], ignore_index=True)
    dl.to_csv(OUT / "market_vintage_daily.csv", index=False, encoding="utf-8")
    log(f"market_vintage_daily.csv {len(dl)} rows")
    # consistency: the held rows recomputed here must equal the tracked v1 table
    v1 = pd.read_csv(V1_OUT / "market_vintage_monthly.csv")
    k = ["market_key", "dump_date", "ymi"]
    held = mv[mv.dump_date >= "2025"]
    m = v1.merge(held, on=k, how="outer", suffixes=("_v1", "_v2"), indicator=True)
    cols = ["n_reviews", "n_listings", "n_reviews_mature12", "n_reviews_mature24", "n_new_listing_cohort"]
    diff = m[(m._merge != "both") | (m[[c + "_v1" for c in cols]].to_numpy() != m[[c + "_v2" for c in cols]].to_numpy()).any(axis=1)]
    pd.DataFrame(dict(v1_rows=[len(v1)], v2_held_rows=[len(held)], mismatched_rows=[len(diff)])).to_csv(
        OUT / "v1_consistency_check.csv", index=False)
    log(f"v1 consistency: v1 {len(v1)} rows, v2 held {len(held)} rows, mismatched {len(diff)}")
    if len(diff):
        diff.head(50).to_csv(OUT / "v1_consistency_mismatches.csv", index=False)
    if failed:
        raise SystemExit(1)
