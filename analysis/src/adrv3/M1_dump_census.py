"""ADR v3, workstream M, step 1: schema and price-basis census of the Inside Airbnb listings dumps.

Reads every `<market>_<date>_listings.{parquet|csv.gz}` in the main-tree raw store (read-only), records
which vintages carry a usable price and on which basis, the listing-age fields, the scope regime, and
writes a slim per-dump cache (id, host_since, first_review, room_type, accommodates, bedrooms, price on
its basis, review counts) that M2 and M3 read. The cache is not committed (listed in the note).

Price basis rule (BRIEF): through Sep/Oct 2025 `price` is the host's listed nightly rate; Dec 2025 to
Feb 2026 no price; from Mar 2026 `price` (= `price_quote_price_per_night`) is a stay quote per night.
Parquet dumps carry `price_basis` already; csv.gz-only markets get the same rule applied here.

Run: py -3.13 analysis/src/adrv3/M1_dump_census.py [--refresh]
Outputs: data/processed/adrv3/M/M1_dump_census.csv, data/processed/adrv3/M/cache/<stem>.parquet
"""
import argparse
import glob
import os
import re
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = r"C:\Users\krish\citadel-abnb\data\raw\inside_airbnb"
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "M")
CACHE = os.path.join(OUT, "cache")
LOG = os.path.join(OUT, "M1_log.txt")

REGION = {
    "austin": "NA", "chicago": "NA", "los-angeles": "NA", "nashville": "NA", "new-orleans": "NA",
    "new-york-city": "NA", "san-diego": "NA",
    "barcelona": "EMEA", "london": "EMEA", "paris": "EMEA", "rome": "EMEA",
    "mexico-city": "LatAm", "belize": "LatAm", "bogota": "LatAm", "buenos-aires": "LatAm",
    "rio-de-janeiro": "LatAm", "santiago": "LatAm", "sao-paulo": "LatAm",
    "sydney": "APAC", "bangkok": "APAC", "barossa-valley": "APAC", "barwon-south-west-vic": "APAC",
    "brisbane": "APAC", "hong-kong": "APAC", "melbourne": "APAC", "mid-north-coast": "APAC",
    "mornington-peninsula": "APAC", "northern-rivers": "APAC", "singapore": "APAC", "sunshine-coast": "APAC",
    "taipei": "APAC", "tasmania": "APAC", "tokyo": "APAC", "western-australia": "APAC",
}
CORE13 = {"austin", "barcelona", "chicago", "london", "los-angeles", "mexico-city", "nashville", "new-orleans",
          "new-york-city", "paris", "rome", "san-diego", "sydney"}

KEEP = ["id", "host_id", "host_since", "first_review", "last_review", "room_type", "accommodates", "bedrooms",
        "price", "price_quote_price_per_night", "price_quote_checkin_date", "price_quote_checkout_date",
        "number_of_reviews", "number_of_reviews_ltm", "number_of_reviews_l30d", "estimated_occupancy_l365d",
        "availability_365", "has_availability"]


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def qlabel(date: str) -> str:
    y, m = int(date[:4]), int(date[5:7])
    return f"{(m - 1) // 3 + 1}Q{str(y)[2:]}"


def parse_price(s: pd.Series) -> pd.Series:
    if s.dtype.kind in "fi":
        return s.astype(float)
    s = s.astype("string")
    s = s.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(s, errors="coerce").astype(float)


def read_dump(stem: str) -> tuple[pd.DataFrame, str]:
    pq = os.path.join(RAW, stem + ".parquet")
    gz = os.path.join(RAW, stem + ".csv.gz")
    if os.path.exists(pq):
        import pyarrow.parquet as pqt
        sch = pqt.read_schema(pq).names
        cols = [c for c in KEEP + ["price_basis"] if c in sch]
        df = pqt.read_table(pq, columns=cols).to_pandas()
        fmt = "parquet"
    else:
        head = pd.read_csv(gz, nrows=5, low_memory=False)
        cols = [c for c in KEEP if c in head.columns]
        df = pd.read_csv(gz, usecols=cols, low_memory=False)
        fmt = "csv.gz"
    for c in KEEP:
        if c not in df.columns:
            df[c] = np.nan
    df["price"] = parse_price(df["price"])
    df["price_quote_price_per_night"] = parse_price(df["price_quote_price_per_night"])
    for c in ["accommodates", "bedrooms", "number_of_reviews", "number_of_reviews_ltm", "number_of_reviews_l30d",
              "estimated_occupancy_l365d", "availability_365"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["host_since", "first_review", "last_review", "price_quote_checkin_date", "price_quote_checkout_date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    return df, fmt


def infer_basis(df: pd.DataFrame, date: str) -> str:
    """Parquet dumps carry price_basis (listed_nightly / quote_per_night / none). csv.gz dumps: apply the
    BRIEF rule on the data actually present."""
    if "price_basis" in df.columns and df["price_basis"].notna().any():
        return str(df["price_basis"].mode().iloc[0])
    p_share = df["price"].notna().mean()
    q_share = df["price_quote_price_per_night"].notna().mean()
    if q_share > 0.3:
        return "quote_per_night"
    if p_share > 0.3 and date >= "2026-03-01":
        return "quote_per_night"
    if p_share > 0.3 and date < "2025-11-01":
        return "listed_nightly"
    return "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="rebuild cache files that already exist")
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    stems = sorted({re.sub(r"\.(parquet|csv\.gz)$", "", os.path.basename(p))
                    for p in glob.glob(os.path.join(RAW, "*_listings.*"))})
    log(f"M1 start: {len(stems)} dump stems")
    rows = []
    for i, stem in enumerate(stems):
        m = re.match(r"(.+)_(\d{4}-\d{2}-\d{2})_listings$", stem)
        market, date = m.group(1), m.group(2)
        cpath = os.path.join(CACHE, stem + ".parquet")
        t0 = time.time()
        try:
            if os.path.exists(cpath) and not a.refresh:
                df = pd.read_parquet(cpath)
                fmt = df.attrs.get("source_format", "cache")
                basis = df["price_basis"].iloc[0] if len(df) else "none"
            else:
                df, fmt = read_dump(stem)
                basis = infer_basis(df, date)
                df["price_basis"] = basis
                # one price column on the vintage's basis
                if basis == "quote_per_night":
                    df["price_on_basis"] = df["price_quote_price_per_night"].where(
                        df["price_quote_price_per_night"].notna(), df["price"])
                elif basis == "listed_nightly":
                    df["price_on_basis"] = df["price"]
                else:
                    df["price_on_basis"] = np.nan
                keep = [c for c in KEEP if c != "price"] + ["price_basis", "price_on_basis"]
                slim = df[keep].copy()
                slim["market"] = market
                slim["dump_date"] = date
                slim.attrs["source_format"] = fmt
                slim.to_parquet(cpath, index=False)
                df = slim
        except Exception as e:  # noqa: BLE001
            log(f"FAIL {stem}: {e!r}")
            rows.append(dict(market=market, region=REGION.get(market, "?"), dump_date=date, quarter=qlabel(date),
                             source_format="error", error=repr(e)))
            continue
        dd = pd.Timestamp(date)
        age_fr = (dd - df["first_review"]).dt.days
        age_hs = (dd - df["host_since"]).dt.days
        has_p = df["price_on_basis"].notna() & (df["price_on_basis"] > 0)
        new_fr = age_fr < 365
        l30 = df["number_of_reviews_l30d"].fillna(0)
        ltm = df["number_of_reviews_ltm"].fillna(0)
        rows.append(dict(
            market=market, region=REGION.get(market, "?"), core13=market in CORE13, dump_date=date, quarter=qlabel(date),
            source_format=fmt, n_listings=int(len(df)), price_basis=basis,
            price_nonnull_share=round(float(has_p.mean()), 4),
            quote_col_present=bool(df["price_quote_price_per_night"].notna().any()),
            quote_checkin_median=(df["price_quote_checkin_date"].dropna().median().date().isoformat()
                                  if df["price_quote_checkin_date"].notna().any() else ""),
            quote_stay_nights_median=(float((df["price_quote_checkout_date"] - df["price_quote_checkin_date"]).dt.days.median())
                                      if df["price_quote_checkin_date"].notna().any() else np.nan),
            first_review_nonnull_share=round(float(df["first_review"].notna().mean()), 4),
            host_since_nonnull_share=round(float(df["host_since"].notna().mean()), 4),
            reviews_l30d_present=bool(df["number_of_reviews_l30d"].notna().any()),
            n_reviewed=int(df["first_review"].notna().sum()),
            n_new_first_review_lt12m=int(new_fr.sum()),
            share_listings_new_by_first_review=round(float(new_fr.sum() / max(df["first_review"].notna().sum(), 1)), 4),
            share_listings_new_by_host_since=round(float((age_hs < 365).sum() / max(df["host_since"].notna().sum(), 1)), 4),
            share_l30d_reviews_from_new=round(float(l30[new_fr].sum() / l30.sum()), 4) if l30.sum() else np.nan,
            share_ltm_reviews_from_new=round(float(ltm[new_fr].sum() / ltm.sum()), 4) if ltm.sum() else np.nan,
            n_priced_new=int((has_p & new_fr).sum()), n_priced_old=int((has_p & (age_fr >= 365)).sum()),
            n_priced_entire_new=int((has_p & new_fr & df["room_type"].eq("Entire home/apt")).sum()),
            n_priced_entire_old=int((has_p & (age_fr >= 365) & df["room_type"].eq("Entire home/apt")).sum()),
            seconds=round(time.time() - t0, 1)))
        log(f"[{i + 1}/{len(stems)}] {stem} {fmt} n={len(df)} basis={basis} price={has_p.mean():.2f} "
            f"new_share_l30d={rows[-1]['share_l30d_reviews_from_new']} ({time.time() - t0:.1f}s)")
    c = pd.DataFrame(rows)
    # scope regime: Dec 2025 to May 2026 monthlies are partial-scope releases (memory); also flag any vintage
    # whose listing count is under 80% of the market's median full-scope count within +/- 12 months.
    c["partial_scope_regime"] = (c.dump_date >= "2025-12-01") & (c.dump_date <= "2026-05-31")
    ratios = []
    for _, r in c.iterrows():
        if r.get("source_format") == "error":
            ratios.append(np.nan)
            continue
        w = c[(c.market == r.market) & (~c.partial_scope_regime) & (c.source_format != "error")
              & ((pd.to_datetime(c.dump_date) - pd.Timestamp(r.dump_date)).dt.days.abs() <= 400)]
        ratios.append(r.n_listings / w.n_listings.median() if len(w) else np.nan)
    c["n_ratio_to_full_scope"] = np.round(ratios, 3)
    c["scope_flag"] = np.where(c.partial_scope_regime | (c.n_ratio_to_full_scope < 0.8), "partial", "full")
    c["usable_for_premium"] = (c.price_basis.isin(["listed_nightly", "quote_per_night"])) & (c.price_nonnull_share >= 0.5) \
        & (c.n_priced_new.fillna(0) >= 100) & (c.n_priced_old.fillna(0) >= 300)
    c = c.sort_values(["market", "dump_date"])
    c.to_csv(os.path.join(OUT, "M1_dump_census.csv"), index=False, encoding="utf-8")
    log(f"M1 done: {len(c)} rows, bases {c.price_basis.value_counts().to_dict()}, "
        f"usable {int(c.usable_for_premium.sum())}, errors {(c.source_format == 'error').sum()}")


if __name__ == "__main__":
    main()
