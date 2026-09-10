"""Matched calendar reopening pilot; availability transitions are not cancellations.

Local inputs only. Select 10% of listing IDs with a stable uint64 mixer, before outcomes.
Run: .venv/Scripts/python.exe analysis/src/rnpl_calendar_pilot.py
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/inside_airbnb_calendar"
OUT = ROOT / "outputs/rnpl-calendar-pilot-20260910"
MARKETS = {"austin": "united-states/tx/austin", "rome": "italy/lazio/rome", "sydney": "australia/nsw/sydney"}


def select_ids(ids):
    # SplitMix64 finalizer; stable across Python and pandas versions.
    x = np.asarray(ids, dtype=np.uint64)
    x = (x ^ (x >> np.uint64(30))) * np.uint64(0xbf58476d1ce4e5b9)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94d049bb133111eb)
    x = x ^ (x >> np.uint64(31))
    return np.asarray(ids)[x % np.uint64(10) == 0]


def add_runs(frame):
    frame = frame.sort_values(["listing_id", "date"]).reset_index(drop=True)
    boundary = (frame.listing_id.ne(frame.listing_id.shift()) |
                frame.u.ne(frame.u.shift()) | frame.date.diff().ne(pd.Timedelta(days=1)))
    run = boundary.cumsum()
    frame["run"] = frame.groupby(run).u.transform("size").astype("int16")
    group = frame.groupby("listing_id", sort=False)
    lo, hi = group.date.transform("min"), group.date.transform("max")
    frame["edge"] = (frame.groupby(run).date.transform("min").eq(lo) |
                     frame.groupby(run).date.transform("max").eq(hi))
    frame["blocked_share"] = group.u.transform("mean").astype("float32")
    return frame


def load_snapshot(path):
    snapshot = path.name.rsplit("_", 2)[1]
    chunks, total, all_ids = [], 0, set()
    for chunk in pd.read_csv(path, usecols=["listing_id", "date", "available", "minimum_nights"],
                             dtype={"listing_id": "int64", "available": "string", "minimum_nights": "float32"},
                             chunksize=300_000):
        total += len(chunk)
        ids = chunk.listing_id.unique()
        all_ids.update(ids.tolist())
        chunk = chunk[chunk.listing_id.isin(select_ids(ids))].copy()
        if not chunk.available.isin(["t", "f"]).all():
            raise ValueError(f"Unknown availability in {path}")
        chunk["date"] = pd.to_datetime(chunk.date, format="%Y-%m-%d", errors="raise")
        chunk["u"] = chunk.available.eq("f")
        chunks.append(chunk.drop(columns="available"))
    frame = pd.concat(chunks, ignore_index=True)
    duplicates = int(frame.duplicated(["listing_id", "date"]).sum())
    if duplicates:
        raise ValueError(f"{path}: {duplicates} duplicate sampled listing/date keys")
    frame = add_runs(frame)
    spans = frame.groupby("listing_id").size()
    meta = {"file": str(path.relative_to(ROOT)), "snapshot": snapshot,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "compressed_bytes": path.stat().st_size,
            "raw_rows": total, "raw_listings": len(all_ids), "sample_rows": len(frame),
            "sample_listings": int(frame.listing_id.nunique()), "duplicate_sample_keys": duplicates,
            "stay_date_min": str(frame.date.min().date()), "stay_date_max": str(frame.date.max().date()),
            "calendar_days_per_listing_min": int(spans.min()), "calendar_days_per_listing_max": int(spans.max()),
            "calendar_days_per_listing_median": float(spans.median()),
            "missing_minimum_nights": int(frame.minimum_nights.isna().sum())}
    return snapshot, frame, meta


def matched(a, b, date_b):
    # Identical dates only; elapsed nights cannot be construed as conversions.
    cut = pd.Timestamp(date_b)
    return a[a.date > cut].merge(b[b.date > cut], on=["listing_id", "date"], suffixes=("0", "1"), validate="one_to_one")


def window_masks(frame, last):
    days = (frame.date - pd.Timestamp(last)).dt.days
    return {"all_future": days > 0, "d001_030": days.between(1, 30),
            "d031_060": days.between(31, 60), "d061_090": days.between(61, 90),
            "d091_180": days.between(91, 180),
            "Q3_2026": frame.date.between("2026-07-01", "2026-09-30"),
            "Q4_2026": frame.date.between("2026-10-01", "2026-12-31")}


def regimes(frame, stable):
    persistent = frame.listing_id.isin(stable)
    screened = (persistent & frame.blocked_share0.lt(.95) & frame.blocked_share1.lt(.95) &
                frame.minimum_nights0.eq(frame.minimum_nights1) & frame.minimum_nights0.le(7))
    return {"all_matched": pd.Series(True, index=frame.index), "stable_all_five": persistent,
            "screened": screened,
            "screened_short_run": screened & frame.run0.between(1, 14) & ~frame.edge0}


def summarize_pair(frame):
    original_u = frame.u0
    reopened = original_u & ~frame.u1
    newly_u = ~original_u & frame.u1
    initial_n, reopened_n = int(original_u.sum()), int(reopened.sum())
    assert len(frame) == int((frame.u0 & frame.u1).sum() + reopened.sum() + newly_u.sum() + (~frame.u0 & ~frame.u1).sum())
    by_listing = frame[original_u].groupby("listing_id").u1.agg(["size", "sum"])
    if initial_n:
        counts = (by_listing["size"] - by_listing["sum"]).sort_values(ascending=False)
        listing_rate = counts / by_listing["size"]
        top10 = float(counts.head(10).sum() / reopened_n) if reopened_n else None
        broad = int(counts[listing_rate > .5].sum())
    else:
        top10, broad = None, 0
    return {"matched_nights": len(frame), "matched_listings": int(frame.listing_id.nunique()),
            "initial_unavailable_nights": initial_n, "reopened_nights": reopened_n,
            "reopening_rate_pct": reopened_n / initial_n * 100 if initial_n else None,
            "newly_unavailable_nights": int(newly_u.sum()),
            "net_unavailable_change_nights": int(frame.u1.sum() - frame.u0.sum()),
            "top10_listings_share_of_reopenings_pct": top10 * 100 if top10 is not None else None,
            "share_reopenings_from_listings_reopening_over_half_pct": broad / reopened_n * 100 if reopened_n else None}


def process_market(market):
    paths = sorted(RAW.glob(f"{market}_*_calendar.csv.gz"))
    if len(paths) != 5:
        raise ValueError(f"Expected five vintages for {market}")
    snapshots, provenance = [], []
    for path in paths:
        date, frame, meta = load_snapshot(path)
        meta["source_url"] = f"https://data.insideairbnb.com/{MARKETS[market]}/{date}/data/calendar.csv.gz"
        provenance.append(meta)
        snapshots.append((date, frame))
        print(f"{market} {date}: {len(frame):,} sampled nights; {meta['sample_listings']:,} listings", flush=True)
    stable = set.intersection(*(set(frame.listing_id.unique()) for _, frame in snapshots))
    coverage, pairs, triples = [], [], []
    for i in range(4):
        date0, a = snapshots[i]
        date1, b = snapshots[i + 1]
        joint = matched(a, b, date1)
        eligible = a[a.date > pd.Timestamp(date1)]
        coverage.append({"market": market, "snapshot0": date0, "snapshot1": date1,
                         "interval_days": (pd.Timestamp(date1) - pd.Timestamp(date0)).days,
                         "baseline_sample_listings": int(a.listing_id.nunique()),
                         "next_sample_listings": int(b.listing_id.nunique()),
                         "stable_all_five_listings": len(stable),
                         "baseline_future_rows": len(eligible), "matched_future_rows": len(joint),
                         "matched_future_row_retention_pct": len(joint) / len(eligible) * 100,
                         "baseline_future_unavailable": int(eligible.u.sum()),
                         "unavailable_row_retention_pct": float(joint.u0.sum() / eligible.u.sum() * 100)})
        for regime, regmask in regimes(joint, stable).items():
            for window, winmask in window_masks(joint, date1).items():
                subset = joint[regmask & winmask]
                if len(subset):
                    pairs.append({"market": market, "snapshot0": date0, "snapshot1": date1,
                                  "regime": regime, "window": window, **summarize_pair(subset)})
        if i < 3:
            date2, c = snapshots[i + 2]
            future = joint[joint.date > pd.Timestamp(date2)]
            third = c[["listing_id", "date", "u"]].rename(columns={"u": "u2"})
            follow = future.merge(third, on=["listing_id", "date"], validate="one_to_one")
            for regime, regmask in regimes(follow, stable).items():
                for window, winmask in window_masks(follow, date2).items():
                    subset = follow[regmask & winmask]
                    reopening = subset.u0 & ~subset.u1
                    n = int(reopening.sum())
                    prejoin_reopened = int((future.u0 & ~future.u1).sum()) if regime == "all_matched" and window == "all_future" else None
                    if len(subset):
                        triples.append({"market": market, "snapshot0": date0, "snapshot1": date1,
                                        "snapshot2": date2, "regime": regime, "window": window,
                                        "followable_reopened_before_join_all": prejoin_reopened,
                                        "reopened_followed_nights": n,
                                        "reclosed_nights": int((reopening & subset.u2).sum()),
                                        "still_available_nights": int((reopening & ~subset.u2).sum()),
                                        "reclosed_pct": float((reopening & subset.u2).sum() / n * 100) if n else None})
        print(f"{market} pair {date0} -> {date1}: {len(joint):,} matched future nights", flush=True)
    return {"market": market, "provenance": provenance, "coverage": coverage, "pairs": pairs, "triples": triples}


def self_test():
    # Four genuinely future keys plus an elapsed date and an unmatched listing.
    a = pd.DataFrame({"listing_id": [1, 1, 2, 2, 3, 4],
                      "date": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-01", "2026-07-02", "2026-06-01", "2026-07-01"]),
                      "u": [True, True, False, False, True, True]})
    b = a.iloc[:5].copy()
    b["u"] = [False, True, True, False, False]
    joint = matched(a, b, "2026-06-15")
    result = summarize_pair(joint)
    assert result["matched_nights"] == 4
    assert result["initial_unavailable_nights"] == 2
    assert result["reopened_nights"] == 1 and result["newly_unavailable_nights"] == 1
    assert result["reopening_rate_pct"] == 50 and result["net_unavailable_change_nights"] == 0
    runs = add_runs(a)
    assert runs[(runs.listing_id == 1)].run.tolist() == [2, 2]
    assert np.array_equal(select_ids(np.arange(1000)), select_ids(np.arange(1000)))
    print("Synthetic checks passed: elapsed/unmatched exclusion, transition identity, run boundaries, deterministic selection.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", choices=list(MARKETS))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    self_test()
    if args.self_test:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for market in [args.market] if args.market else MARKETS:
        result = process_market(market)
        result["method"] = {"sample": "SplitMix64(listing_id) mod 10 == 0; approximately 10% of listings, fixed over vintages",
                            "selection": "Austin, Rome, Sydney: five vintages, North America/Europe/APAC; selected before outcomes",
                            "license": "Inside Airbnb, CC BY 4.0; derived aggregate availability proxies",
                            "date_rule": "same listing and stay date at each capture; stay date strictly after last observation",
                            "warning": "Reopening is not cancellation; reclosure is not confirmed rebooking. No causal RNPL attribution.",
                            "python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__}
        path = OUT / f"{market}.json"
        path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
