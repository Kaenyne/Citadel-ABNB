"""
WS-J step 1: would a listed-price panel have tracked the like-for-like pricing residual?

Inside Airbnb calendar dumps carry, per listing and forward stay date, the host's listed
nightly `price` (and `adjusted_price`, populated on <1% of rows). This script builds a
same-listing, same-forward-stay-date, same-lead listed-price y/y from every pair of
vintages one year apart that carries prices on BOTH ends, then aggregates by market,
region and global and writes the series the test in J3 consumes.

Coverage finding (11 Sep 2026, this script's `J1_price_coverage.csv`): Inside Airbnb
stopped populating calendar prices with the June 2025 dumps. Every vintage dated
2025-06 or later has an empty `price` column (or none at all). The BRIEF's statement
that "2024 and 2025 vintages carry price" holds only through May 2025. Year-apart
pairs with prices on both ends therefore exist only for the four markets that have
2024 vintages (austin, nashville, paris, rome) at two snapshot months, March 2025 and
May 2025: six pairs in total. The full 365-day forward window of each pair is used, so
the y/y is observed for stay quarters 1Q25 to 2Q26 as of March / May 2025.

Method per pair (V0 dated S0 in 2024, V1 dated S1 in 2025):
  - keep rows with a parsable price 1 <= p <= 10,000 in local listing currency (USD/EUR;
    same currency both ends so the y/y is constant-currency);
  - shift V0 stay dates by +364 days (same weekday) and match on (listing_id, stay date);
  - per matched listing-date, log ratio r = ln(p1/p0); lead = stay date - S1;
  - aggregate by lead bucket (0-30, 31-90, 91-180, 181-365 days, and 0-90) and by stay
    quarter, in two availability regimes ("all" matched dates; "open_both" = available
    at both snapshots, the closest thing to an unsold asking price);
  - statistics: median of r, 10% trimmed mean of r, the ratio of matched-listing
    arithmetic means (composition of the matched panel included, weights = nights),
    and the unmatched all-listings median (composition of the whole dump included).
Region = simple mean of markets (NA: austin, nashville; EMEA: paris, rome). Global =
NA 0.423, EMEA 0.577 (FY25 10-K nights shares 29.6 / 40.3 renormalised over the two
regions that have data; LatAm and APAC are absent from every price-bearing pair).

A second diagnostic uses consecutive vintages within 2024-25 (same market, ~1 month
apart, both priced) to measure how a listing's asking price for a FIXED stay date is
revised as the date approaches ("lead revision"). If hosts cut asking prices into the
stay date, a y/y taken at long lead is a statement about posted prices, not realised
ones, and that is part of why the panel can fail against ADR.

Run: py -3.13 analysis/src/adrq3/J1_calendar_price_yoy.py [--sample 0.2]
"""
from __future__ import annotations

import argparse
import gzip
import os
import re
import sys
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pcomp
import pyarrow.csv as pcsv

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MAIN = r"C:\Users\krish\citadel-abnb"
RAW = os.path.join(MAIN, "data", "raw", "inside_airbnb_calendar")
OUT = os.path.join(HERE, "data", "processed", "adrq3", "J")
os.makedirs(OUT, exist_ok=True)
FILE_RE = re.compile(r"^(?P<market>.+)_(?P<date>\d{4}-\d{2}-\d{2})_calendar\.csv\.gz$")
EPOCH = np.datetime64("2023-01-01")
REGION = {"austin": "na", "nashville": "na", "paris": "emea", "rome": "emea",
          "chicago": "na", "los-angeles": "na", "san-diego": "na", "bangkok": "apac",
          "hong-kong": "apac", "singapore": "apac", "taipei": "apac", "tokyo": "apac",
          "belize": "latam", "mexico-city": "latam", "rio-de-janeiro": "latam",
          "buenos-aires": "latam", "santiago": "latam", "barcelona": "emea", "london": "emea",
          "brisbane": "apac", "melbourne": "apac", "sydney": "apac", "tasmania": "apac",
          "western-australia": "apac", "sunshine-coast": "apac", "northern-rivers": "apac",
          "mid-north-coast": "apac", "mornington-peninsula": "apac",
          "barwon-south-west-vic": "apac", "barossa-valley": "apac", "new-orleans": "na",
          "new-york-city": "na", "bogota": "latam", "sao-paulo": "latam"}
LEAD_BUCKETS = [("0-30", 0, 30), ("31-90", 31, 90), ("91-180", 91, 180), ("181-365", 181, 365),
                ("0-90", 0, 90)]


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def qlabel(day_idx):
    """Quarter label ('3Q25') for an int day index array relative to EPOCH, vectorised."""
    months = (EPOCH + np.asarray(day_idx, dtype="int64").astype("timedelta64[D]")).astype("datetime64[M]").astype("int64")
    y = months // 12 + 1970
    m = months % 12 + 1
    q = (m - 1) // 3 + 1
    return np.char.add(np.char.add(q.astype(str), "Q"), np.char.zfill((y % 100).astype(str), 2))


def select_ids(ids, frac):
    x = np.asarray(ids, dtype=np.uint64)
    x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    x = x ^ (x >> np.uint64(31))
    return np.asarray(ids)[(x % np.uint64(1000)) < np.uint64(int(frac * 1000))]


def sorted_unique(values):
    """Sort plus neighbour test: 10-20x faster than the library unique on large int64 arrays
    in this numpy build (F1 loader note)."""
    if not len(values):
        return values
    ordered = np.sort(values)
    return ordered[np.concatenate(([True], ordered[1:] != ordered[:-1]))]


def has_price(path):
    with gzip.open(path, "rt", encoding="utf-8") as h:
        hdr = h.readline().strip().split(",")
    if "price" not in hdr:
        return False, "no_price_column"
    t = pcsv.read_csv(path, read_options=pcsv.ReadOptions(block_size=1 << 22),
                      convert_options=pcsv.ConvertOptions(include_columns=["price"],
                                                          column_types={"price": pa.string()}))
    t = t.slice(0, 500_000)
    p = t["price"]
    ne = pcomp.sum(pcomp.and_(pcomp.is_valid(p), pcomp.not_equal(p, ""))).as_py() or 0
    share = ne / max(t.num_rows, 1)
    return share > 0.5, f"price_nonempty_share={share:.3f}"


def load(path, sample=None):
    t = pcsv.read_csv(path, convert_options=pcsv.ConvertOptions(
        include_columns=["listing_id", "date", "available", "price"],
        column_types={"listing_id": pa.int64(), "date": pa.date32(),
                      "available": pa.string(), "price": pa.string()}))
    p = pcomp.replace_substring(pcomp.replace_substring(t["price"], "$", ""), ",", "")
    p = pcomp.cast(pcomp.if_else(pcomp.equal(p, ""), None, p), pa.float64(), safe=False)
    price = p.to_numpy(zero_copy_only=False)
    lid = t["listing_id"].to_numpy(zero_copy_only=False).astype("int64")
    day = (t["date"].to_numpy(zero_copy_only=False) - EPOCH).astype("int32")
    avail = (t["available"].to_numpy(zero_copy_only=False) == "t")
    ok = np.isfinite(price) & (price >= 1) & (price <= 10_000)
    all_ids = sorted_unique(lid)
    if sample:
        ok &= np.isin(lid, select_ids(all_ids, sample))
    return lid[ok], day[ok], avail[ok], price[ok], int(t.num_rows), int(len(all_ids))


def match(l0, d0, a0, p0, l1, d1, a1, p1, shift):
    """Return matched arrays (day1, avail0, avail1, p0, p1, lid) on (listing, stay date)."""
    k0 = l0 * 4096 + (d0 + shift)
    k1 = l1 * 4096 + d1
    o0 = np.argsort(k0, kind="stable")
    k0s = k0[o0]
    pos = np.searchsorted(k0s, k1)
    pos[pos >= len(k0s)] = 0
    hit = k0s[pos] == k1
    i0 = o0[pos[hit]]
    return d1[hit], a0[i0], a1[hit], p0[i0], p1[hit], l1[hit]


def trimmed_mean(x, frac=0.10):
    if len(x) == 0:
        return np.nan
    lo, hi = np.quantile(x, [frac, 1 - frac])
    m = (x >= lo) & (x <= hi)
    return float(x[m].mean()) if m.any() else np.nan


def summarise(rows, market, s0, s1, lead1, a0, a1, p0, p1, lid, regime_mask, regime, extra):
    r = np.log(p1 / p0)
    q = qlabel(pd.Series(lead1 + (np.datetime64(s1) - EPOCH).astype(int))).values \
        if False else None
    stay_day = lead1 + int((np.datetime64(s1) - EPOCH).astype(int))
    stay_q = qlabel(stay_day)
    uids = sorted_unique(lid)
    codes = np.searchsorted(uids, lid)
    groups = [("lead", name, (lead1 >= lo) & (lead1 <= hi)) for name, lo, hi in LEAD_BUCKETS]
    groups += [("stay_quarter", qq, stay_q == qq) for qq in sorted(set(stay_q))]
    for gtype, gname, gm in groups:
        m = gm & regime_mask
        n = int(m.sum())
        if n < 200:
            continue
        rr = r[m]
        rows.append({
            "market": market, "region": REGION.get(market, ""), "snapshot0": s0, "snapshot1": s1,
            "snapshot1_quarter": str(qlabel([int((np.datetime64(s1) - EPOCH).astype(int))])[0]),
            "group_type": gtype, "group": gname, "regime": regime,
            "n_listing_dates": n, "n_listings": int(np.count_nonzero(np.bincount(codes[m], minlength=len(uids)))),
            "median_yoy_pct": 100 * (np.exp(np.median(rr)) - 1),
            "trimmed_mean_yoy_pct": 100 * (np.exp(trimmed_mean(rr)) - 1),
            "mean_ratio_yoy_pct": 100 * (p1[m].mean() / p0[m].mean() - 1),
            "share_dates_up": float((rr > 0.005).mean()),
            "share_dates_down": float((rr < -0.005).mean()),
            **extra,
        })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=float, default=None, help="deterministic listing sample fraction")
    ap.add_argument("--skip-revision", action="store_true")
    args = ap.parse_args()

    # ---- 1. coverage census of every pre-2026 vintage ------------------------------------
    files = {}
    for fn in sorted(os.listdir(RAW)):
        m = FILE_RE.match(fn)
        if m and m["date"] < "2026-01-01":
            files.setdefault(m["market"], []).append((m["date"], os.path.join(RAW, fn)))
    cov_path = os.path.join(OUT, "J1_price_coverage.csv")
    cached = pd.read_csv(cov_path) if os.path.exists(cov_path) else None
    cov = []
    priced = {}
    for mk, lst in files.items():
        for d, path in lst:
            hit = None if cached is None else cached[(cached.market == mk) & (cached.snapshot == d)]
            if hit is not None and len(hit):
                ok, note = bool(hit.priced.iloc[0]), str(hit.note.iloc[0])
            else:
                ok, note = has_price(path)
            cov.append({"market": mk, "snapshot": d, "priced": ok, "note": note, "file": os.path.basename(path)})
            if ok:
                priced.setdefault(mk, []).append((d, path))
    cov = pd.DataFrame(cov)
    cov.to_csv(cov_path, index=False)
    last = cov[cov.priced].groupby("market").snapshot.max()
    log(f"priced vintages: {int(cov.priced.sum())} of {len(cov)}; last priced snapshot per market:\n{last.to_string()}")

    # ---- 2. year-apart pairs, both priced ----------------------------------------------
    pairs = []
    for mk, lst in priced.items():
        for d1, f1 in lst:
            for d0, f0 in lst:
                gap = (np.datetime64(d1) - np.datetime64(d0)).astype(int)
                if 340 <= gap <= 380:
                    pairs.append((mk, d0, f0, d1, f1, int(gap)))
    log(f"year-apart priced pairs: {len(pairs)}: " + ", ".join(f"{p[0]} {p[1]}->{p[3]}" for p in pairs))

    rows, prov = [], []
    for mk, d0, f0, d1, f1, gap in pairs:
        t0 = time.time()
        l0, dd0, a0, p0, n0, u0 = load(f0, args.sample)
        l1, dd1, a1, p1, n1, u1 = load(f1, args.sample)
        s1_day = int((np.datetime64(d1) - EPOCH).astype(int))
        s0_day = int((np.datetime64(d0) - EPOCH).astype(int))
        # align V0 stay dates by +364 days (same weekday); keep leads 0..365 in V1
        dm, am0, am1, pm0, pm1, lm = match(l0, dd0, a0, p0, l1, dd1, a1, p1, 364)
        lead1 = dm - s1_day
        keep = (lead1 >= 0) & (lead1 <= 365)
        dm, am0, am1, pm0, pm1, lm, lead1 = dm[keep], am0[keep], am1[keep], pm0[keep], pm1[keep], lm[keep], lead1[keep]
        n_matched_listings = int(len(sorted_unique(lm)))
        extra = {"gap_days": gap, "listings_v0": u0, "listings_v1": u1,
                 "matched_listings": n_matched_listings,
                 "matched_share_of_v1": float(n_matched_listings / max(u1, 1))}
        summarise(rows, mk, d0, d1, lead1, am0, am1, pm0, pm1, lm, np.ones(len(dm), bool), "all", extra)
        summarise(rows, mk, d0, d1, lead1, am0, am1, pm0, pm1, lm, am0 & am1, "open_both", extra)
        # unmatched all-listings median (composition of the whole dump included), by stay quarter
        for regime, mask0, mask1 in (("all", np.ones(len(dd0), bool), np.ones(len(dd1), bool)),
                                     ("open", a0, a1)):
            q0 = qlabel(dd0 + 364)
            q1 = qlabel(dd1)
            for qq in sorted(set(q1)):
                m1 = (q1 == qq) & mask1 & ((dd1 - s1_day) >= 0) & ((dd1 - s1_day) <= 365)
                m0 = (q0 == qq) & mask0 & ((dd0 - s0_day) >= 0) & ((dd0 - s0_day) <= 365)
                if m1.sum() < 200 or m0.sum() < 200:
                    continue
                rows.append({"market": mk, "region": REGION.get(mk, ""), "snapshot0": d0, "snapshot1": d1,
                             "snapshot1_quarter": str(qlabel([s1_day])[0]),
                             "group_type": "stay_quarter", "group": qq, "regime": f"unmatched_{regime}",
                             "n_listing_dates": int(m1.sum()), "n_listings": int(len(sorted_unique(l1[m1]))),
                             "median_yoy_pct": 100 * (np.median(p1[m1]) / np.median(p0[m0]) - 1),
                             "trimmed_mean_yoy_pct": 100 * (np.exp(trimmed_mean(np.log(p1[m1])) - trimmed_mean(np.log(p0[m0]))) - 1),
                             "mean_ratio_yoy_pct": 100 * (p1[m1].mean() / p0[m0].mean() - 1),
                             "share_dates_up": np.nan, "share_dates_down": np.nan, **extra})
        prov.append({"market": mk, "snapshot0": d0, "snapshot1": d1, "rows_v0": n0, "rows_v1": n1,
                     "priced_rows_v0": int(len(l0)), "priced_rows_v1": int(len(l1)),
                     "listings_v0": u0, "listings_v1": u1, "matched_listing_dates": int(len(dm)),
                     "matched_listings": extra["matched_listings"], "seconds": round(time.time() - t0, 1)})
        log(f"{mk} {d0}->{d1}: matched {len(dm):,} listing-dates on {extra['matched_listings']:,} listings "
            f"({extra['matched_share_of_v1']:.0%} of V1) in {time.time()-t0:.0f}s")
        del l0, dd0, a0, p0, l1, dd1, a1, p1
    pairs_df = pd.DataFrame(rows)
    pairs_df.to_csv(os.path.join(OUT, "J1_calendar_pairs.csv"), index=False)
    pd.DataFrame(prov).to_csv(os.path.join(OUT, "J1_provenance.csv"), index=False)

    # ---- 3. aggregate: market -> region (mean) -> global (FY25 nights shares, renormalised)
    W = {"na": 29.6, "emea": 40.3, "latam": 16.9, "apac": 13.1}
    stats = ["median_yoy_pct", "trimmed_mean_yoy_pct", "mean_ratio_yoy_pct"]
    keys = ["snapshot1_quarter", "group_type", "group", "regime"]
    # a market can appear twice in one snapshot quarter only if two pairs share it: not the case here
    reg = (pairs_df.groupby(keys + ["region"])[stats].mean().reset_index())
    reg["n_markets"] = pairs_df.groupby(keys + ["region"]).market.nunique().values
    glob_rows = []
    for k, g in reg.groupby(keys):
        w = np.array([W[r] for r in g.region])
        w = w / w.sum()
        row = dict(zip(keys, k))
        row["region"] = "global"
        for s in stats:
            row[s] = float((g[s].values * w).sum())
        row["n_markets"] = int(g.n_markets.sum())
        row["regions_present"] = "+".join(sorted(g.region))
        glob_rows.append(row)
    agg = pd.concat([reg.assign(regions_present=reg.region), pd.DataFrame(glob_rows)], ignore_index=True)
    agg.to_csv(os.path.join(OUT, "calendar_price_yoy.csv"), index=False)
    log("aggregate written")

    # ---- 4. lead-revision diagnostic on consecutive priced vintages ----------------------
    if not args.skip_revision:
        rev = []
        for mk, lst in priced.items():
            if mk not in ("austin", "nashville", "paris", "rome"):
                continue
            lst = sorted(lst)
            for (da, fa), (db, fb) in zip(lst[:-1], lst[1:]):
                gap = int((np.datetime64(db) - np.datetime64(da)).astype(int))
                if not 20 <= gap <= 70:
                    continue
                frac = args.sample or (0.2 if mk == "paris" else 0.5)
                la, dda, aa, pa_, _, _ = load(fa, frac)
                lb, ddb, ab, pb, _, _ = load(fb, frac)
                sb = int((np.datetime64(db) - EPOCH).astype(int))
                dm, am0, am1, pm0, pm1, lm = match(la, dda, aa, pa_, lb, ddb, ab, pb, 0)
                lead = dm - sb
                r = np.log(pm1 / pm0)
                for name, lo, hi in LEAD_BUCKETS[:4]:
                    for regime, mask in (("all", np.ones(len(r), bool)), ("open_both", am0 & am1)):
                        m = (lead >= lo) & (lead <= hi) & mask
                        if m.sum() < 200:
                            continue
                        rev.append({"market": mk, "snapshot_a": da, "snapshot_b": db, "gap_days": gap,
                                    "lead_bucket_at_b": name, "regime": regime, "n": int(m.sum()),
                                    "median_revision_pct": 100 * (np.exp(np.median(r[m])) - 1),
                                    "trimmed_mean_revision_pct": 100 * (np.exp(trimmed_mean(r[m])) - 1),
                                    "share_cut": float((r[m] < -0.005).mean()),
                                    "share_raised": float((r[m] > 0.005).mean())})
                log(f"revision {mk} {da}->{db}: {len(dm):,} matched")
                del la, dda, aa, pa_, lb, ddb, ab, pb
        pd.DataFrame(rev).to_csv(os.path.join(OUT, "J1_lead_revision.csv"), index=False)
    log("done")


if __name__ == "__main__":
    main()
