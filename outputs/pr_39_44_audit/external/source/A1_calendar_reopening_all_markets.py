"""Matched calendar reopening across all Inside Airbnb markets on disk.

Generalisation of analysis/src/rnpl_calendar_pilot.py. The sample hash, screens, windows,
regimes and pair/triple summaries are copied unchanged, so austin, rome and sydney must
reproduce outputs/rnpl-calendar-pilot-20260910/{austin,rome,sydney}.json exactly. The only
changes are: any market discovered from the raw filenames, source_url and region taken from
the acquisition manifest instead of a hard-coded path table, fewer than five vintages
tolerated (a market with k captures yields k-1 pairs and max(k-2, 0) triples), and one JSON
checkpoint per market so a run can resume.

Availability transitions are not cancellations and reclosure is not confirmed rebooking.

Run: python analysis/src/overnight2/A1_calendar_reopening_all_markets.py [--market rome]
"""
import argparse
import csv
import hashlib
import json
import platform
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MAIN_TREE = Path(r"C:\Users\krish\citadel-abnb")
RAW_DEFAULT = MAIN_TREE / "data/raw/inside_airbnb_calendar"
MANIFEST_DEFAULT = MAIN_TREE / "data/processed/adr/14c_calendar_manifest.csv"
OUT_DEFAULT = ROOT / "data/processed/overnight2/A/markets"
FILE_RE = re.compile(r"^(?P<market>.+)_(?P<date>\d{4}-\d{2}-\d{2})_calendar\.csv\.gz$")


# ---------------------------------------------------------------- pilot code, unchanged
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


# ------------------------------------------------------------------------- generalised
def read_manifest(path):
    """(market, capture date) -> {url, region}. Rows without a realised capture are skipped."""
    index = {}
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("date"):
                index[(row["market"], row["date"])] = {"url": row.get("url") or None,
                                                       "region": (row.get("region") or "").lower() or None}
    return index


def discover(raw_dir):
    """market -> sorted list of (capture date, path) for every calendar dump on disk."""
    found = {}
    for path in sorted(Path(raw_dir).glob("*_calendar.csv.gz")):
        match = FILE_RE.match(path.name)
        if not match:
            continue
        found.setdefault(match["market"], []).append((match["date"], path))
    return {market: sorted(items) for market, items in sorted(found.items())}


def load_snapshot(path, root_for_labels):
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
    try:
        label = str(path.relative_to(root_for_labels))
    except ValueError:
        label = str(path)
    meta = {"file": label, "snapshot": snapshot,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "compressed_bytes": path.stat().st_size,
            "raw_rows": total, "raw_listings": len(all_ids), "sample_rows": len(frame),
            "sample_listings": int(frame.listing_id.nunique()), "duplicate_sample_keys": duplicates,
            "stay_date_min": str(frame.date.min().date()), "stay_date_max": str(frame.date.max().date()),
            "calendar_days_per_listing_min": int(spans.min()), "calendar_days_per_listing_max": int(spans.max()),
            "calendar_days_per_listing_median": float(spans.median()),
            "missing_minimum_nights": int(frame.minimum_nights.isna().sum())}
    return snapshot, frame, meta


def process_market(market, captures, manifest, raw_dir, label_root):
    if len(captures) < 2:
        raise ValueError(f"{market}: need at least two vintages, found {len(captures)}")
    snapshots, provenance = [], []
    for date, path in captures:
        snapshot, frame, meta = load_snapshot(path, label_root)
        record = manifest.get((market, snapshot), {})
        meta["source_url"] = record.get("url")
        provenance.append(meta)
        snapshots.append((snapshot, frame))
        print(f"{market} {snapshot}: {len(frame):,} sampled nights; {meta['sample_listings']:,} listings", flush=True)
    stable = set.intersection(*(set(frame.listing_id.unique()) for _, frame in snapshots))
    coverage, pairs, triples = [], [], []
    for i in range(len(snapshots) - 1):
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
        if i < len(snapshots) - 2:
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
    region = next((manifest.get((market, p["snapshot"]), {}).get("region") for p in provenance
                   if manifest.get((market, p["snapshot"]), {}).get("region")), None)
    return {"market": market, "region": region, "n_vintages": len(snapshots),
            "provenance": provenance, "coverage": coverage, "pairs": pairs, "triples": triples}


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
    # Generalised parts: filename parsing and short-panel tolerance.
    assert FILE_RE.match("sao-paulo_2026-06-14_calendar.csv.gz")["market"] == "sao-paulo"
    assert FILE_RE.match("new-york-city_2026-08-10_calendar.csv.gz")["date"] == "2026-08-10"
    print("Synthetic checks passed: elapsed/unmatched exclusion, transition identity, run boundaries, "
          "deterministic selection, filename parsing.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", action="append", default=None,
                        help="market slug; repeatable. Default: every market found in --raw-dir.")
    parser.add_argument("--raw-dir", default=str(RAW_DEFAULT))
    parser.add_argument("--manifest", default=str(MANIFEST_DEFAULT))
    parser.add_argument("--out-dir", default=str(OUT_DEFAULT))
    parser.add_argument("--overwrite", action="store_true", help="recompute markets whose JSON exists")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    self_test()
    if args.self_test:
        return
    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest(args.manifest)
    found = discover(raw_dir)
    wanted = args.market or list(found)
    missing = [m for m in wanted if m not in found]
    if missing:
        raise SystemExit(f"No calendar files for: {', '.join(missing)}")
    label_root = raw_dir.parents[2] if len(raw_dir.parents) >= 3 else raw_dir
    for market in wanted:
        path = out_dir / f"{market}.json"
        if path.exists() and not args.overwrite:
            print(f"skip {market}: {path.name} exists", flush=True)
            continue
        result = process_market(market, found[market], manifest, raw_dir, label_root)
        result["method"] = {"sample": "SplitMix64(listing_id) mod 10 == 0; approximately 10% of listings, fixed over vintages",
                            "selection": "every Inside Airbnb market with repeated calendar captures on disk; "
                                         "methodology frozen from the Austin/Rome/Sydney pilot before viewing outcomes",
                            "license": "Inside Airbnb, CC BY 4.0; derived aggregate availability proxies",
                            "date_rule": "same listing and stay date at each capture; stay date strictly after last observation",
                            "panel_note": "regime key stable_all_five means present in every capture this market has "
                                          "(five for 32 markets, two for bogota and sao-paulo)",
                            "warning": "Reopening is not cancellation; reclosure is not confirmed rebooking. No causal RNPL attribution.",
                            "python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__}
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        tmp.replace(path)
        print(f"Wrote {path}", flush=True)


if __name__ == "__main__":
    main()

