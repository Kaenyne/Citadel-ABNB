"""Rolling listing-ID disappearance, with dated fee-event diagnostics.

Rates reset the at-risk inventory at each interval. No fee-treatment flag exists in
Inside Airbnb: observed host portfolio size is descriptive, never a PMS classifier.
Failed/partial captures cannot supply negative observations. Persistence requires a
valid follow-up 90-135 days after the first absence, with no intervening positives.
"""
from collections import Counter, defaultdict
import csv
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path

from acquire_churn_archive import ROOT, inspect_capture
from measure_churn_archive import geographic_exclusions, load_compact
from execute_listing_churn import number, write_csv

EVENT = date(2025, 10, 27)
COHORTS = ("all_listings", "reviewed_str_homes")
PORTFOLIOS = ("all", "one", "two_to_four", "five_plus")
MONTHLY_MONTHS = tuple(f"2025-{m:02d}" for m in range(9, 13)) + tuple(f"2026-{m:02d}" for m in range(1, 8))
QUARTERS = ("2025-09", "2025-12", "2026-03", "2026-06")
HISTORY = ("2024-09", "2024-12", "2025-03", "2025-06", *QUARTERS)


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def cohort_ids(records, cohort, portfolio="all"):
    host_counts = Counter(row["host_id"] for row in records.values())
    if cohort not in COHORTS or portfolio not in PORTFOLIOS:
        raise ValueError("Unknown cohort or portfolio")
    ids = set()
    for key, row in records.items():
        size = host_counts[row["host_id"]]
        band = "one" if size == 1 else ("two_to_four" if size < 5 else "five_plus")
        if portfolio != "all" and portfolio != band:
            continue
        if cohort == "reviewed_str_homes":
            minimum = number(row["minimum_nights"])
            if row["room_type"] != "Entire home/apt" or (number(row["number_of_reviews_ltm"]) or 0) <= 0 or minimum is None or minimum >= 30:
                continue
        ids.add(key)
    return ids


def valid_negative(snapshot, policy):
    if policy not in ("coverage_screen", "exclude_feb_may_negatives"):
        raise ValueError("Unknown coverage policy")
    return not snapshot["flag"] and not (policy == "exclude_feb_may_negatives" and "2026-02" <= snapshot["month"] <= "2026-05")


def pair_measure(start, end, followups, members, positive_by_month, policy, positive_events):
    days = (end["complete"] - start["complete"]).days
    if days <= 0:
        raise ValueError("Observation dates must be strictly increasing")
    n = len(members)
    eligible = bool(n) and valid_negative(start, policy) and valid_negative(end, policy)
    missing = members - positive_by_month[end["month"]]
    row = dict(start_complete=start["complete"].isoformat(), end_complete=end["complete"].isoformat(),
               interval_days=days, eligible=eligible, baseline_ids=n,
               missing_ids=len(missing) if eligible else None,
               disappearance_rate=len(missing) / n if eligible else None,
               normalized_30d_rate=(1 - (1 - len(missing) / n) ** (30 / days)) if eligible else None,
               persistence_eligible=False, confirmation_date="", confirmation_lag_days="",
               persistent_90_ids=None, persistent_90_rate=None, reobserved_by_confirmation=None)
    candidates = [s for s in followups if valid_negative(s, policy) and 90 <= (s["complete"] - end["complete"]).days <= 135]
    if eligible and candidates:
        confirmation = min(candidates, key=lambda s: s["complete"])
        still_missing = set(missing)
        # All acquired positives in the intervening calendar months are retained,
        # including positives from partial captures and overlapping geographies.
        for month, positive in positive_by_month.items():
            if end["month"] <= month < confirmation["month"]:
                still_missing.difference_update(still_missing.intersection(positive))
        for s in positive_events:
            if s["month"] == confirmation["month"] and s["complete"] <= confirmation["complete"]:
                still_missing.difference_update(still_missing.intersection(s["ids"]))
        row.update(persistence_eligible=True, confirmation_date=confirmation["complete"].isoformat(),
                   confirmation_lag_days=(confirmation["complete"] - end["complete"]).days,
                   persistent_90_ids=len(still_missing), persistent_90_rate=len(still_missing) / n,
                   reobserved_by_confirmation=len(missing - still_missing))
    return row


def load_inventory():
    """One immutable raw identity per market/date; compact reuse is hash checked."""
    items = {}
    for folder in ("listing_churn_panel", "listing_churn_archive", "fee_churn_history"):
        for row in read(ROOT / f"data/raw/{folder}/download_manifest.csv"):
            key = (row["market"], row["snapshot_start"])
            if key in items and row["status"] == "ok" and items[key]["status"] == "ok" and row["sha256"] != items[key]["sha256"]:
                raise ValueError(f"Conflicting raw capture hashes: {key}")
            if key not in items or row.get("compact_path"):
                items[key] = row
    expected = json.loads((ROOT / "data/raw/fee_churn_history/selection.json").read_text(encoding="utf-8"))
    fee_rows = read(ROOT / "data/raw/fee_churn_history/download_manifest.csv")
    if len(fee_rows) != expected["selected_snapshots"]:
        raise ValueError("Acquisition has not finished")
    catalog = {(r["city"], r["dump_date"]): r for r in read(ROOT / "data/raw/listing_churn_panel/team_snapshot_catalog.csv")}
    compact_dir = ROOT / "data/raw/fee_churn_history/compact_cache"
    compact_dir.mkdir(exist_ok=True)
    snapshots, positives, quality = {}, defaultdict(set), []
    maximum = defaultdict(int)
    for (market, _), row in items.items():
        if row["status"] == "ok":
            maximum[market] = max(maximum[market], int(row["rows"]))
    for index, (key, original) in enumerate(sorted(items.items()), 1):
        market, start = key
        if original["status"] != "ok":
            quality.append(dict(market=market, start=start, complete="", status=original["status"], rows="", team_partial="", count_break="", negative_excluded=True, source_url=original["url"], sha256=""))
            continue
        item = dict(original)
        if not item.get("compact_path"):
            compact = compact_dir / f"{market}_{start}.csv.gz"
            metadata_path = compact.with_suffix(".json")
            if compact.exists() and metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                if metadata["sha256"] != item["sha256"]:
                    raise ValueError("Compact cache source changed")
            else:
                metadata = inspect_capture(ROOT / item["local_path"], compact, start)
                if metadata["sha256"] != item["sha256"]:
                    raise ValueError("Raw source changed")
                metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            item.update(metadata, compact_path=compact.relative_to(ROOT).as_posix())
        ids = load_compact(item, detailed=False)
        partial = catalog.get(key, {}).get("partial_scope", item.get("source_partial_scope", "")) == "True"
        count_break = len(ids) < .5 * maximum[market]
        snapshot = dict(market=market, start=start, month=start[:7], complete=date.fromisoformat(item["snapshot_complete"]),
                        ids=ids, item=item, flag=partial or count_break)
        snapshots[key] = snapshot
        positives[start[:7]].update(ids)
        quality.append(dict(market=market, start=start, complete=item["snapshot_complete"], status="ok", rows=len(ids),
                            team_partial=partial, count_break=count_break, negative_excluded=snapshot["flag"], source_url=item["url"], sha256=item["sha256"]))
        if index % 50 == 0:
            print(f"Loaded {index}/{len(items)} captures", flush=True)
    return snapshots, positives, quality, expected


def panel_pairs(name, selections, months, snapshots, positives):
    by_month = defaultdict(dict)
    for market, keys in selections.items():
        for key in keys:
            if key in snapshots:
                s = snapshots[key]
                if s["month"] in months and (market not in by_month[s["month"]] or s["start"] > by_month[s["month"]][market]["start"]):
                    by_month[s["month"]][market] = s
    owners, counts = defaultdict(list), {}
    for market, s in by_month[months[0]].items():
        counts[market] = len(s["ids"])
        for key in s["ids"]:
            owners[key].append(market)
    nested, _, _ = geographic_exclusions(owners, counts)
    output = []
    for left, right in zip(months, months[1:]):
        owners = defaultdict(list)
        for market, s in by_month[left].items():
            if market not in nested:
                for key in s["ids"]:
                    owners[key].append(market)
        duplicates = {key for key, markets in owners.items() if len(markets) > 1}
        for market in sorted(set(by_month[left]) & set(by_month[right]) - set(nested)):
            a, b = by_month[left][market], by_month[right][market]
            records = load_compact(a["item"], detailed=True, verify=False)
            following = [s for (m, _), s in snapshots.items() if m == market and s["complete"] > b["complete"]]
            for cohort in COHORTS:
                for portfolio in PORTFOLIOS:
                    members = cohort_ids(records, cohort, portfolio) - duplicates
                    if not members:
                        continue
                    review_total = sum(number(records[key]["number_of_reviews_ltm"]) or 0 for key in members)
                    missing = members - positives[right]
                    missing_reviews = sum(number(records[key]["number_of_reviews_ltm"]) or 0 for key in missing)
                    for policy in ("coverage_screen", "exclude_feb_may_negatives"):
                        result = pair_measure(a, b, following, members, positives, policy, snapshots.values())
                        result.update(panel=name, market=market, start_month=left, end_month=right, cohort=cohort,
                                      portfolio=portfolio, policy=policy, baseline_review_total=review_total,
                                      missing_baseline_reviews=missing_reviews if result["eligible"] else None,
                                      review_weighted_disappearance=missing_reviews/review_total if review_total and result["eligible"] else None,
                                      event_timing="before" if b["complete"] < EVENT else ("after" if a["complete"] >= EVENT else "straddles_rollout"))
                        output.append(result)
            del records
    return output


def pooled(rows, series, members=None):
    groups = defaultdict(list)
    for row in rows:
        if row["eligible"] and (members is None or row["market"] in members):
            groups[(row["panel"], row["cohort"], row["portfolio"], row["policy"], row["start_month"], row["end_month"])].append(row)
    result = []
    for key, group in sorted(groups.items()):
        n = sum(r["baseline_ids"] for r in group)
        missing = sum(r["missing_ids"] for r in group)
        reviews = sum(r["baseline_review_total"] for r in group)
        mature = [r for r in group if r["persistence_eligible"]]
        mature_n = sum(r["baseline_ids"] for r in mature)
        result.append(dict(series=series, panel=key[0], cohort=key[1], portfolio=key[2], policy=key[3], start_month=key[4], end_month=key[5],
            markets=len(group), baseline_ids=n, missing_ids=missing, disappearance_rate=missing/n,
            mean_30d_rate=sum(r["baseline_ids"]*r["normalized_30d_rate"] for r in group)/n,
            min_interval_days=min(r["interval_days"] for r in group), max_interval_days=max(r["interval_days"] for r in group),
            equal_market_mean=sum(r["disappearance_rate"] for r in group)/len(group),
            review_weighted_disappearance=sum(r["missing_baseline_reviews"] for r in group)/reviews if reviews else None,
            persistence_markets=len(mature), persistence_denominator=mature_n,
            persistent_90_ids=sum(r["persistent_90_ids"] for r in mature) if mature else None,
            persistent_90_rate=sum(r["persistent_90_ids"] for r in mature)/mature_n if mature_n else None,
            market_set=" | ".join(sorted(r["market"] for r in group))))
    return result


def balanced_markets(rows, panel, intervals, require_pre=False):
    groups = defaultdict(set)
    for row in rows:
        pair = (row["start_month"], row["end_month"])
        if row["panel"] == panel and row["cohort"] == "all_listings" and row["portfolio"] == "all" and row["policy"] == "coverage_screen" and row["eligible"] and pair in intervals:
            if require_pre and pair == intervals[0] and row["event_timing"] != "before":
                continue
            groups[pair].add(row["market"])
    return set.intersection(*(groups[pair] for pair in intervals)) if intervals else set()


def main():
    snapshots, positives, quality, selection = load_inventory()
    out = ROOT / "data/processed/fee_churn_history"
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "snapshot_quality.csv", quality)
    broad = defaultdict(list)
    for row in read(ROOT / "data/raw/listing_churn_archive/download_manifest.csv"):
        broad[row["market"]].append((row["market"], row["snapshot_start"]))
    monthly = defaultdict(list)
    for row in read(ROOT / "data/raw/fee_churn_history/download_manifest.csv"):
        if row["market"] in selection["monthly_markets"]:
            monthly[row["market"]].append((row["market"], row["snapshot_start"]))
    historical = defaultdict(list)
    team_markets = {r["city"] for r in read(ROOT / "data/raw/listing_churn_panel/team_snapshot_catalog.csv")}
    for market, start in snapshots:
        if market in team_markets:
            historical[market].append((market, start))
    rows = panel_pairs("broad_quarterly", broad, QUARTERS, snapshots, positives)
    rows += panel_pairs("monthly", monthly, MONTHLY_MONTHS, snapshots, positives)
    rows += panel_pairs("team_historical", historical, HISTORY, snapshots, positives)
    write_csv(out / "market_interval_rates.csv", rows)
    pools = pooled(rows, "available_markets")
    specs = [
        ("balanced_broad", "broad_quarterly", list(zip(QUARTERS, QUARTERS[1:])), False),
        ("balanced_event", "monthly", list(zip(MONTHLY_MONTHS[:5], MONTHLY_MONTHS[1:5])), True),
        ("balanced_pre_quarters", "team_historical", [("2025-03", "2025-06"), ("2025-06", "2025-09"), ("2025-09", "2025-12")], False),
        ("same_season", "team_historical", [("2024-09", "2024-12"), ("2025-09", "2025-12")], False),
    ]
    membership = {}
    for series, panel, intervals, require_pre in specs:
        markets = balanced_markets(rows, panel, intervals, require_pre)
        membership[series] = sorted(markets)
        selected = [r for r in rows if r["panel"] == panel and (r["start_month"], r["end_month"]) in intervals]
        pools += pooled(selected, series, markets)
        print(series, len(markets), sorted(markets), flush=True)
    write_csv(out / "pooled_interval_rates.csv", pools)
    (out / "execution_metadata.json").write_text(json.dumps(dict(
        source_commit=selection["source_commit"], market_sets=membership, captures_loaded=len(snapshots),
        failed_captures=sum(r["status"] != "ok" for r in quality), method="Rolling interval listing-ID disappearance; period-specific at-risk denominator; actual dates; 90-135-day confirmation when available",
        fee_treatment_observed=False, portfolio_definition="Listing count per host within starting market snapshot; not verified PMS usage",
        normalization="30-day equivalent assumes constant interval disappearance hazard; sensitivity, not an observed monthly count",
        positives="Any captured positive in the same calendar month prevents inferred absence; positive observations from partial files retained",
        persistence="No observed reappearance through first valid confirmation 90-135 days after endpoint; no later captures used to extend this horizon",
        caveats=["Availability-selected markets", "Snapshot absence is not verified property or global host churn", "Coverage screens cannot certify complete capture", "Changing fee cohorts and local regulations confound causal interpretation", "September/October 2026 broad rollout is outside observed post-period"]), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
