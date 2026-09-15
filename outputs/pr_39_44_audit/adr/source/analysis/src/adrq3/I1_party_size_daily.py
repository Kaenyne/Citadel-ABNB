"""I1. Party-size review-text proxies, per market x dump x review DATE, from the refreshed
Inside Airbnb reviews dumps (Aug 2026 vintage for 123 markets, plus each market's own
Aug/Sep 2025 vintage where the CDN still had one).

Why daily: the 3Q26-to-date read has to be built on the same day-matched, vintage-matched
windows as the nights index (E6): 2026 dump, review dates 1 Jul to (dump date - 14 days),
against the 2025 dump's identical window 364 days earlier. Daily sums let any window be
assembled afterwards without re-reading 16 GB of gzip.

Classifier: exactly the regexes and head-count parser of analysis/src/abnb_party_size_reviews.py
(imported, not copied), so the series is on the pipeline's basis. Booked capacity = the
`accommodates` of the reviewed listing from the market's 2026 listings dump (the only listings
vintage in the reviews store), joined to BOTH dumps' reviews; a review on a listing delisted
by mid-2026 therefore has no capacity on either side (survivor basis, noted in the note).

Output (checkpointed per dump file, never overwrites the main outputs):
  data/processed/adrq3/I/cache/<market>_<dump>.parquet   columns:
     market_key, dump_date, date, n, n_any, n_solo, n_couple, n_family, n_group,
     hc_n, hc_sum, hc_ge4, acc_n, acc_sum, acc_ge5, entire_n, len_sum
  Rows are kept for review dates >= 2022-07-01 (late dump) / >= 2024-01-01 (old dump).
  A per-year count of ALL reviews in the dump is written alongside as
  data/processed/adrq3/I/cache/<market>_<dump>_years.parquet (for the fixed-2019 weights).

Run (one shard of n): py -3.13 analysis/src/adrq3/I1_party_size_daily.py --shard i n
"""
import sys, os, re, glob, time, importlib.util
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
RAW = MAIN / "data/raw/inside_airbnb_reviews"
OUT = WT / "data/processed/adrq3/I"
CACHE = OUT / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

# import the pipeline's classifier verbatim
spec = importlib.util.spec_from_file_location("psr", WT / "analysis/src/abnb_party_size_reviews.py")
psr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(psr)
RX, headcount = psr.RX, psr.headcount


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def inventory():
    geo = pd.read_csv(WT / "data/processed/q3nowcast/E_aug/market_geo.csv")
    rows = []
    for mk in geo.market_key:
        # exact market match: "ireland_*" must not pick up "ireland_leinster_dublin_*"
        fs = [f for f in glob.glob(str(RAW / f"{mk}_*_reviews.csv.gz"))
              if re.fullmatch(re.escape(mk) + r"_\d{4}-\d{2}-\d{2}_reviews\.csv\.gz", os.path.basename(f))]
        ds = sorted(re.search(r"_(\d{4}-\d{2}-\d{2})_reviews", f).group(1) for f in fs)
        if not ds:
            continue
        late = ds[-1]
        lt = pd.Timestamp(late)
        olds = [d for d in ds if 300 <= (lt - pd.Timestamp(d)).days <= 430]
        old = olds[-1] if olds else ""
        ls = sorted(f for f in glob.glob(str(RAW / f"{mk}_*_listings.csv.gz"))
                    if re.fullmatch(re.escape(mk) + r"_\d{4}-\d{2}-\d{2}_listings\.csv\.gz", os.path.basename(f)))
        rows.append(dict(market_key=mk, region=geo.set_index("market_key").region[mk],
                         vintage_late=late, vintage_old=old, listings_file=ls[-1] if ls else ""))
    inv = pd.DataFrame(rows)
    inv.to_csv(OUT / "I1_inventory.csv", index=False, encoding="utf-8")
    return inv


def load_acc(lp):
    if not lp or not os.path.exists(lp):
        return None
    L = pd.read_csv(lp, usecols=lambda c: c in ("id", "accommodates", "room_type"), low_memory=False)
    L = L.drop_duplicates("id").set_index("id")
    return L


def process(mk, dump, acc, cutoff):
    rp = RAW / f"{mk}_{dump}_reviews.csv.gz"
    dest = CACHE / f"{mk}_{dump}.parquet"
    ydest = CACHE / f"{mk}_{dump}_years.parquet"
    if dest.exists() and ydest.exists():
        return "cached"
    t0 = time.time()
    parts, years = [], {}
    for chunk in pd.read_csv(rp, usecols=["listing_id", "date", "comments"], chunksize=200_000,
                             dtype={"comments": str}, low_memory=False):
        dt = pd.to_datetime(chunk.date, errors="coerce")
        yc = dt.dt.year.value_counts()
        for y, n in yc.items():
            years[int(y)] = years.get(int(y), 0) + int(n)
        m = (dt >= cutoff).to_numpy()
        if not m.any():
            continue
        c = chunk.comments[m].fillna("").astype(str)
        d = pd.DataFrame({"date": dt[m].dt.normalize().values, "listing_id": chunk.listing_id[m].values})
        for k, rx in RX.items():
            d[k] = c.str.contains(rx).values
        d["any"] = d[list(RX)].any(axis=1)
        hc = c.map(headcount).values
        d["hc"] = hc
        d["len"] = c.str.len().values
        if acc is not None:
            j = acc.reindex(d.listing_id)
            d["acc"] = pd.to_numeric(j.accommodates.values, errors="coerce")
            d["entire"] = (j.room_type.values == "Entire home/apt")
        else:
            d["acc"] = np.nan
            d["entire"] = False
        g = d.groupby("date")
        a = pd.DataFrame({
            "n": g.size(), "n_any": g["any"].sum(),
            "n_solo": g["solo"].sum(), "n_couple": g["couple"].sum(),
            "n_family": g["family"].sum(), "n_group": g["group"].sum(),
            "hc_n": g["hc"].count(), "hc_sum": g["hc"].sum(min_count=1).fillna(0),
            "hc_ge4": g["hc"].apply(lambda s: int((s.dropna() >= 4).sum())),
            "acc_n": g["acc"].count(), "acc_sum": g["acc"].sum(min_count=1).fillna(0),
            "acc_ge5": g["acc"].apply(lambda s: int((s.dropna() >= 5).sum())),
            "entire_n": g["entire"].sum(), "len_sum": g["len"].sum(),
        })
        parts.append(a)
    if parts:
        a = pd.concat(parts).groupby(level=0).sum().reset_index()
    else:
        a = pd.DataFrame(columns=["date", "n"])
    a.insert(0, "dump_date", dump)
    a.insert(0, "market_key", mk)
    a.to_parquet(dest, index=False)
    pd.DataFrame({"market_key": mk, "dump_date": dump, "year": list(years.keys()),
                  "n_all": list(years.values())}).to_parquet(ydest, index=False)
    return f"{len(a)} days, {sum(years.values())} reviews, {time.time() - t0:.0f}s"


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", message="This pattern is interpreted")
    args = sys.argv[1:]
    shard = (int(args[1]), int(args[2])) if args[:1] == ["--shard"] else (0, 1)
    inv = inventory()
    jobs = []
    for r in inv.itertuples():
        jobs.append((r.market_key, r.vintage_late, r.listings_file, pd.Timestamp("2022-07-01")))
        if r.vintage_old:
            jobs.append((r.market_key, r.vintage_old, r.listings_file, pd.Timestamp("2024-01-01")))
    jobs = [j for i, j in enumerate(jobs) if i % shard[1] == shard[0]]
    log(f"shard {shard}: {len(jobs)} dump files")
    acc_cache = {}
    for mk, dump, lp, cutoff in jobs:
        if mk not in acc_cache:
            acc_cache = {mk: load_acc(lp)}
        try:
            log(f"{mk} {dump}: {process(mk, dump, acc_cache[mk], cutoff)}")
        except Exception as e:
            log(f"{mk} {dump}: ERR {e!r}")
    log("done")

