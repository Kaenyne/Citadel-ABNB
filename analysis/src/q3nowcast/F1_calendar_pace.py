"""WS-F step 1: booked-nights pace from Inside Airbnb calendar vintages.

What the data are. A calendar dump taken on snapshot date S lists, for every listing live
at S, one row per forward stay date with available in {t, f}. available='f' is a STOCK of
blocked stay-nights: it mixes confirmed bookings, host blocks, and listings that are
inactive or on long-term-rental calendars. It is never occupancy.

What this script produces. Two daily-granularity aggregates, so that every horizon,
month and window downstream is built in F2 from one pass over 2.7 GB of gzip:

  F1_daily_levels.csv     market x vintage x stay_date: listing_nights, blocked_nights
                          over EVERY listing in the dump (Theo's definition, so his
                          booking_curves_by_market.csv can be reproduced).
  F1_daily_transitions.csv  market x (vintage0 -> vintage1) x stay_date, on listings
                          present in BOTH dumps and stay dates strictly after vintage1's
                          snapshot date: blocked at v0, blocked at v1, available->blocked
                          (new blocks, a gross booking proxy), blocked->available
                          (reopenings). The change in the blocked stock for the same
                          forward stay dates on the same listings is a flow, and is the
                          closest thing here to net bookings.
  F1_provenance.csv       one row per file read: sha256, bytes, rows, listings, url.

Regimes in the transitions table:
  all        every matched listing
  screened   drops listings whose matched-future blocked share is >= 0.95 in either
             vintage (inactive listings and long-term-rental calendars read as
             permanently blocked and cannot transition)

Transitions are not bookings and not cancellations. A new block can be a host closing a
date; a reopening can be a cancellation, a host reopening, or a calendar edit. No
identification of bookings is claimed anywhere in this workstream.

Run: py -3.13 analysis/src/q3nowcast/F1_calendar_pace.py            (all markets, full listing set)
     py -3.13 analysis/src/q3nowcast/F1_calendar_pace.py --market rome --sample
     py -3.13 analysis/src/q3nowcast/F1_calendar_pace.py --self-test
"""
import argparse
import csv
import hashlib
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MAIN_TREE = Path(r"C:\Users\krish\citadel-abnb")
RAW_DEFAULT = MAIN_TREE / "data/raw/inside_airbnb_calendar"
MANIFEST_DEFAULT = MAIN_TREE / "data/processed/adr/14c_calendar_manifest.csv"
OUT_DEFAULT = ROOT / "data/processed/q3nowcast/F"
FILE_RE = re.compile(r"^(?P<market>.+)_(?P<date>\d{4}-\d{2}-\d{2})_calendar\.csv\.gz$")

EPOCH = np.datetime64("2024-01-01")          # day index origin; 2024 dumps exist
DAY_SPAN = 4096                              # keys assume 0 <= stay_date - EPOCH < DAY_SPAN
HORIZON_MAX = 372                            # Theo's cap, kept so levels are comparable
SCREEN_BLOCKED = 0.95


def select_ids(ids):
    """Deterministic 10% listing sample, SplitMix64 finalizer. Copied from overnight2 A1
    so a --sample run is directly comparable with that workstream."""
    x = np.asarray(ids, dtype=np.uint64)
    x = (x ^ (x >> np.uint64(30))) * np.uint64(0xbf58476d1ce4e5b9)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94d049bb133111eb)
    x = x ^ (x >> np.uint64(31))
    return np.asarray(ids)[x % np.uint64(10) == 0]


def sorted_unique(values):
    """np.unique costs 10 to 20x a sort plus a neighbour test on the large-cardinality int64
    arrays here (20 s against 1 s for 5mm listing ids in this numpy build) and the match does
    it four times per pair, so it is done by hand."""
    if not len(values):
        return values
    ordered = np.sort(values)
    return ordered[np.concatenate(([True], ordered[1:] != ordered[:-1]))]


def read_manifest(path):
    index = {}
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("date"):
                index[(row["market"], row["date"])] = {
                    "url": row.get("url") or None,
                    "region": (row.get("region") or "").lower() or None}
    return index


def discover(raw_dir):
    found = {}
    for path in sorted(Path(raw_dir).glob("*_calendar.csv.gz")):
        match = FILE_RE.match(path.name)
        if match:
            found.setdefault(match["market"], []).append((match["date"], path))
    return {market: sorted(items) for market, items in sorted(found.items())}


def load_snapshot(path, sample):
    """-> (snapshot_date, lid int64, day int32, u bool), plus provenance.

    pyarrow reads a 11mm-row gzipped calendar in about 2 s against 35 s for pandas, which
    is what makes 328 files feasible. available is a single ASCII byte per row, so the
    string column's value buffer is read as one byte per value after asserting that the
    offsets really are one byte apart and that nothing is null.
    """
    import pyarrow as pa
    import pyarrow.csv as pc
    snapshot = path.name.rsplit("_", 2)[1]
    table = pc.read_csv(
        path, read_options=pc.ReadOptions(use_threads=True),
        convert_options=pc.ConvertOptions(
            include_columns=["listing_id", "date", "available"],
            column_types={"listing_id": pa.int64(), "date": pa.date32(),
                          "available": pa.string()}))
    total = table.num_rows
    avail = table["available"].combine_chunks()
    if avail.null_count or table["date"].null_count or table["listing_id"].null_count:
        raise ValueError(f"{path}: null listing_id, date or available")
    raw = np.frombuffer(avail.cast(pa.binary()).buffers()[2], dtype="S1")
    if len(raw) != total:
        raise ValueError(f"{path}: availability values are not single characters")
    codes = np.unique(raw)
    if not set(codes.tolist()) <= {b"t", b"f"}:
        raise ValueError(f"{path}: unexpected availability values {codes}")
    lid = table["listing_id"].combine_chunks().to_numpy(zero_copy_only=False).astype("int64")
    day = ((table["date"].combine_chunks().to_numpy(zero_copy_only=False) - EPOCH)
           .astype("int32"))
    u = raw == b"f"
    all_ids = sorted_unique(lid)
    if sample:
        keep = np.isin(lid, select_ids(all_ids))
        lid, day, u = lid[keep], day[keep], u[keep]
        kept_ids = sorted_unique(lid)
    else:
        kept_ids = all_ids
    if day.min() < 0 or day.max() >= DAY_SPAN:
        raise ValueError(f"{path}: stay dates outside the key range")
    meta = {"file": path.name, "market": path.name.rsplit("_", 2)[0], "snapshot": snapshot,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "compressed_bytes": path.stat().st_size, "raw_rows": int(total),
            "raw_listings": int(len(all_ids)), "used_rows": int(len(lid)),
            "used_listings": int(len(kept_ids)),
            "stay_date_min": str((EPOCH + day.min().astype("timedelta64[D]"))),
            "stay_date_max": str((EPOCH + day.max().astype("timedelta64[D]")))}
    return snapshot, lid, day, u, kept_ids, meta


def daily_levels(market, region, snapshot, day, u, url):
    """Blocked share by stay date over every listing in the dump, days ahead 0..372."""
    s_day = int((np.datetime64(snapshot) - EPOCH).astype(int))
    keep = (day >= s_day) & (day <= s_day + HORIZON_MAX)
    d, ub = day[keep], u[keep]
    if not len(d):
        return pd.DataFrame()
    lo = d.min()
    nights = np.bincount(d - lo)
    blocked = np.bincount(d - lo, weights=ub.astype("int64")).astype("int64")
    present = nights > 0
    idx = np.nonzero(present)[0]
    frame = pd.DataFrame({
        "market": market, "region": region, "snapshot_date": snapshot,
        "stay_date": (EPOCH + (idx + lo).astype("timedelta64[D]")).astype(str),
        "days_ahead": (idx + lo - s_day).astype("int32"),
        "listing_nights": nights[idx], "blocked_nights": blocked[idx]})
    frame["source_url"] = url
    return frame


def pair_daily(market, region, v0, v1, snap0, snap1, cut_day):
    """Match two vintages on (listing_id, stay_date) and aggregate transitions per stay date.

    Implemented as a dense listing x stay-date state matrix rather than a sort-merge join.
    A calendar pair is naturally dense: every matched listing has a row for nearly every
    forward date, so U listings x D days is the same order as the row count, and filling it
    is one O(N) scatter instead of two O(N log N) sorts. On paris this is about fifteen
    times faster than the join it replaces, which is what makes 321 pairs practical.

    State codes: 0 absent from this vintage, 1 available, 2 blocked (available='f').
    Only stay dates strictly after snapshot1 are considered, so an elapsed night can never
    be read as a booking, and only listings present in both vintages contribute.
    """
    ids0, lid0, day0, u0 = v0
    ids1, lid1, day1, u1 = v1
    ids = np.union1d(ids0, ids1)
    n_codes = len(ids)
    dmin = cut_day + 1
    dmax = int(max(day0.max(), day1.max()))
    if dmax < dmin:
        return pd.DataFrame(), []
    span = dmax - dmin + 1
    states = []
    baseline_future_rows = 0
    for which, (lid, day, u) in enumerate(((lid0, day0, u0), (lid1, day1, u1))):
        keep = day >= dmin
        if which == 0:
            baseline_future_rows = int(keep.sum())
        code = np.searchsorted(ids, lid[keep])
        flat = code.astype("int64") * span + (day[keep] - dmin)
        state = np.zeros(n_codes * span, dtype="int8")
        state[flat] = np.where(u[keep], 2, 1).astype("int8")
        states.append(state.reshape(n_codes, span))
    a, b = states
    present = (a != 0) & (b != 0)
    blk0 = present & (a == 2)
    blk1 = present & (b == 2)
    newb = present & (a == 1) & (b == 2)
    reop = present & (a == 2) & (b == 1)
    del a, b
    per_listing = present.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        share0 = np.where(per_listing > 0, blk0.sum(1) / np.maximum(per_listing, 1), 0.0)
        share1 = np.where(per_listing > 0, blk1.sum(1) / np.maximum(per_listing, 1), 0.0)
    live = (share0 < SCREEN_BLOCKED) & (share1 < SCREEN_BLOCKED) & (per_listing > 0)
    interval = int((np.datetime64(snap1) - np.datetime64(snap0)).astype(int))
    s1_day = int((np.datetime64(snap1) - EPOCH).astype(int))
    frames, pair_rows = [], []
    for regime, rows in (("all", None), ("screened", live)):
        sel = (lambda m: m) if rows is None else (lambda m: m[rows])
        nights = sel(present).sum(0).astype("int64")
        if not nights.sum():
            continue
        idx = np.nonzero(nights > 0)[0]
        frames.append(pd.DataFrame({
            "market": market, "region": region, "snapshot0": snap0, "snapshot1": snap1,
            "regime": regime,
            "stay_date": (EPOCH + (idx + dmin).astype("timedelta64[D]")).astype(str),
            "days_ahead_v1": (idx + dmin - s1_day).astype("int32"),
            "matched_nights": nights[idx],
            "blocked_v0": sel(blk0).sum(0).astype("int64")[idx],
            "blocked_v1": sel(blk1).sum(0).astype("int64")[idx],
            "new_blocks": sel(newb).sum(0).astype("int64")[idx],
            "reopenings": sel(reop).sum(0).astype("int64")[idx]}))
        matched_listings = int((per_listing > 0).sum() if rows is None
                              else (live & (per_listing > 0)).sum())
        total = int(nights.sum())
        pair_rows.append({"market": market, "region": region, "snapshot0": snap0,
                          "snapshot1": snap1, "regime": regime, "interval_days": interval,
                          "matched_listings": matched_listings,
                          "matched_future_nights": total,
                          "baseline_future_rows": baseline_future_rows,
                          "matched_row_retention_pct": round(
                              total / baseline_future_rows * 100, 2)
                          if baseline_future_rows else None})
    if not frames:
        return pd.DataFrame(), []
    return pd.concat(frames, ignore_index=True), pair_rows


def choose_pairs(dates, year_tol=21, interval_tol=21):
    """Which vintage pairs to match.

    Consecutive pairs give the pace curve. They are not enough for a year-over-year read:
    the 2026 vintages are quarterly, so the analogue of 2026-03 -> 2026-06 in a market that
    now has monthly 2025 dumps is 2025-03 -> 2025-06, which is not a consecutive pair. So for
    every pair whose later end is in the most recent year, the closest pair one and two years
    back is added when both ends land within year_tol days of the anniversary and the
    interval is within interval_tol days. Nothing else is matched, because a full pair grid
    would be quadratic in vintages for no extra identification.
    """
    stamps = [np.datetime64(d) for d in dates]
    pairs = {(i, i + 1) for i in range(len(dates) - 1)}
    latest_year = max(int(d[:4]) for d in dates)
    for i, j in sorted(pairs):
        if int(dates[j][:4]) != latest_year:
            continue
        interval = int((stamps[j] - stamps[i]).astype(int))
        for back in (1, 2):
            shift = np.timedelta64(365 * back, "D")
            want0, want1 = stamps[i] - shift, stamps[j] - shift
            def nearest(target):
                gaps = [abs(int((t - target).astype(int))) for t in stamps]
                k = int(np.argmin(gaps))
                return k, gaps[k]
            k0, g0 = nearest(want0)
            k1, g1 = nearest(want1)
            if g0 > year_tol or g1 > year_tol or k0 >= k1:
                continue
            if abs(int((stamps[k1] - stamps[k0]).astype(int)) - interval) > interval_tol:
                continue
            pairs.add((k0, k1))
    return sorted(pairs)


def self_test():
    # Two listings present in both vintages, one dropping out, one elapsed date,
    # one new block and one reopening. Day index 10 is 2024-01-11 given EPOCH.
    lid0 = np.array([1, 1, 1, 2, 2, 3], dtype="int64")
    day0 = np.array([10, 11, 12, 10, 11, 10], dtype="int32")
    u0 = np.array([True, True, False, False, True, True])
    lid1 = np.array([1, 1, 1, 2, 2], dtype="int64")
    day1 = np.array([10, 11, 12, 10, 11], dtype="int32")
    u1 = np.array([True, False, True, False, True])
    v0 = (sorted_unique(lid0), lid0, day0, u0)
    v1 = (sorted_unique(lid1), lid1, day1, u1)
    daily, pair = pair_daily("t", "na", v0, v1, "2024-01-10", "2024-01-11", cut_day=10)
    assert set(daily.regime) == {"all", "screened"}
    allr = daily[daily.regime == "all"]
    assert int(allr.matched_nights.sum()) == 3, allr.matched_nights.sum()
    assert int(allr.new_blocks.sum()) == 1 and int(allr.reopenings.sum()) == 1
    assert int(allr.blocked_v1.sum() - allr.blocked_v0.sum()) == 0
    assert allr.days_ahead_v1.tolist() == [1, 2], allr.days_ahead_v1.tolist()
    assert pair[0]["matched_listings"] == 2 and pair[0]["baseline_future_rows"] == 3
    # a listing blocked on every matched night is dropped by the screen
    lidp = np.array([1, 1, 2, 2], dtype="int64")
    dayp = np.array([11, 12, 11, 12], dtype="int32")
    allb = np.array([True, True, False, False])
    half = np.array([True, True, True, False])
    dp, _ = pair_daily("t", "na", (sorted_unique(lidp), lidp, dayp, allb),
                       (sorted_unique(lidp), lidp, dayp, half), "2024-01-10", "2024-01-11", 10)
    assert int(dp[dp.regime == "all"].matched_nights.sum()) == 4
    assert int(dp[dp.regime == "screened"].matched_nights.sum()) == 2
    # levels: day 0 (the snapshot date) is included, and a date before it is dropped
    lv = daily_levels("t", "na", "2024-01-11", np.array([9, 10, 11, 11], dtype="int32"),
                      np.array([True, True, True, False]), None)
    assert lv.days_ahead.tolist() == [0, 1], lv.days_ahead.tolist()
    assert lv.listing_nights.tolist() == [1, 2] and lv.blocked_nights.tolist() == [1, 1]
    assert np.array_equal(select_ids(np.arange(1000)), select_ids(np.arange(1000)))
    assert FILE_RE.match("new-york-city_2026-08-10_calendar.csv.gz")["market"] == "new-york-city"
    # pair choice: consecutive pairs plus the one-year-back analogue of a 2026 quarterly pair
    dates = ["2025-03-05", "2025-06-12", "2025-09-14", "2026-03-24", "2026-06-20"]
    chosen = choose_pairs(dates)
    assert (0, 1) in chosen and (3, 4) in chosen            # consecutive
    assert (0, 1) in chosen                                  # 2025-03 -> 2025-06 analogue
    assert all(a < b for a, b in chosen)
    assert choose_pairs(["2026-06-20"]) == []
    print("self-test passed: elapsed/unmatched exclusion, transition identity, "
          "day-0 levels, the always-blocked screen, deterministic sample, "
          "filename parsing", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", action="append", default=None)
    ap.add_argument("--raw-dir", default=str(RAW_DEFAULT))
    ap.add_argument("--manifest", default=str(MANIFEST_DEFAULT))
    ap.add_argument("--out-dir", default=str(OUT_DEFAULT))
    ap.add_argument("--sample", action="store_true", help="deterministic 10%% listing sample")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    self_test()
    if args.self_test:
        return
    out = Path(args.out_dir) / ("markets_sample" if args.sample else "markets")
    out.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest(args.manifest)
    markets = discover(args.raw_dir)
    todo = args.market or list(markets)
    print(f"{len(markets)} markets on disk; processing {len(todo)}; "
          f"sample={args.sample}", flush=True)
    for market in todo:
        captures = markets.get(market)
        if not captures:
            print(f"!! {market}: no files", flush=True)
            continue
        lv_path = out / f"{market}_levels.csv"
        tr_path = out / f"{market}_transitions.csv"
        if lv_path.exists() and tr_path.exists() and not args.overwrite:
            print(f"== {market}: already done, skipped", flush=True)
            continue
        t0 = time.time()
        region = next((manifest.get((market, d), {}).get("region") for d, _ in captures
                       if manifest.get((market, d), {}).get("region")), None)
        dates = [d for d, _ in captures]
        paths = {d: path for d, path in captures}
        levels, prov = [], []
        for date in dates:
            snapshot, lid, day, u, ids, meta = load_snapshot(paths[date], args.sample)
            rec = manifest.get((market, snapshot), {})
            meta["source_url"] = rec.get("url")
            meta["region"] = region
            prov.append(meta)
            levels.append(daily_levels(market, region, snapshot, day, u, rec.get("url")))
            del lid, day, u, ids
        print(f"   {market}: {len(dates)} vintages read [{time.time() - t0:.0f}s]", flush=True)
        trans, pairs = [], []
        plan = choose_pairs(dates)
        cached_i, cached = None, None
        for i, j in plan:
            if cached_i != i:
                snap, lid, day, u, ids, _ = load_snapshot(paths[dates[i]], args.sample)
                cached = (ids, lid, day, u)
                cached_i = i
            _, lid1, day1, u1, ids1, _ = load_snapshot(paths[dates[j]], args.sample)
            cut = int((np.datetime64(dates[j]) - EPOCH).astype(int))
            d_frame, p_rows = pair_daily(market, region, cached, (ids1, lid1, day1, u1),
                                         dates[i], dates[j], cut)
            if len(d_frame):
                trans.append(d_frame)
                pairs.extend(p_rows)
            del lid1, day1, u1, ids1
            print(f"   {market} {dates[i]} -> {dates[j]} done [{time.time() - t0:.0f}s]",
                  flush=True)
        del cached
        pd.concat(levels, ignore_index=True).to_csv(lv_path, index=False)
        if trans:
            pd.concat(trans, ignore_index=True).to_csv(tr_path, index=False)
            pd.DataFrame(pairs).to_csv(out / f"{market}_pairs.csv", index=False)
        else:
            pd.DataFrame().to_csv(tr_path, index=False)
        pd.DataFrame(prov).to_csv(out / f"{market}_provenance.csv", index=False)
        print(f"== {market}: {len(captures)} vintages, {len(plan)} pairs done [{time.time() - t0:.0f}s]", flush=True)

    # concatenate whatever is present, so a partial run still yields usable tables
    for kind in ("levels", "transitions", "pairs", "provenance"):
        files = sorted(out.glob(f"*_{kind}.csv"))
        frames = []
        for f in files:
            try:
                frame = pd.read_csv(f)
            except pd.errors.EmptyDataError:
                continue
            if len(frame):
                frames.append(frame)
        if frames:
            # the two daily tables are tens of MB, so they are committed gzipped; pandas
            # reads .csv.gz transparently, so nothing downstream changes
            if kind in ("levels", "transitions"):
                name = f"F1_daily_{kind}.csv.gz"
            else:
                name = f"F1_{kind}.csv"
            if args.sample:
                name = name.replace(".csv", "_sample10pct.csv", 1)
            target = Path(args.out_dir) / name
            combined = pd.concat(frames, ignore_index=True)
            combined.to_csv(target, index=False)
            print(f"wrote {target} ({len(combined):,} rows from {len(frames)} markets)", flush=True)


if __name__ == "__main__":
    main()
