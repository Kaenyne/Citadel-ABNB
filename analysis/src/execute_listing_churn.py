"""Measure snapshot-observed delisting persistence and license-linked continuation.

This estimates listing-cohort outcomes, not definitive global property churn.
Granular listing/unit records stay in gitignored raw storage. Positive observations
are retained even in a partial snapshot; partial snapshots cannot supply negatives.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import re
import platform
from research_integrity import atomic_write_csv

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ["id", "name", "description", "picture_url", "host_id", "license", "room_type",
          "bedrooms", "accommodates", "latitude", "longitude", "minimum_nights",
          "number_of_reviews_ltm", "availability_365", "source", "last_scraped"]


def license_id(value):
    tokens = set(re.findall(r"\bSTR[-\s]?(\d{5})L\b", value.upper()))
    return "STR-" + next(iter(tokens)) + "L" if len(tokens) == 1 else ""


def number(value):
    if value is None or value == "":
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def compatible(a, b):
    if a["room_type"] != b["room_type"]:
        return False
    coords = [number(r.get(k)) for r in (a, b) for k in ("latitude", "longitude")]
    if any(v is None for v in coords):
        return False
    lat_a, lon_a, lat_b, lon_b = coords
    distance = math.hypot((lat_b-lat_a)*111_320, (lon_b-lon_a)*111_320*math.cos(math.radians(lat_a)))
    return distance <= 300


def terminal_state(observations, persistence_days=90):
    """Each observation is (completed_date, True/False/None); None is unknown.

    The final observation must be classifiable. This is endpoint persistent absence,
    not cumulative first-exit incidence. A positive in a partial snapshot resets the clock.
    """
    if not observations or observations[0][1] is not True:
        raise ValueError("A cohort must start with an observed listing")
    dates = [d for d, _ in observations]
    if dates != sorted(set(dates)):
        raise ValueError("Observation dates must be unique and increasing")
    if isinstance(persistence_days, bool) or not isinstance(persistence_days, int) or persistence_days <= 0:
        raise ValueError("Persistence must be a positive integer number of days")
    last_present = 0
    ever_missing = False
    returned = False
    for j, (_, state) in enumerate(observations):
        if state is not True and state is not False and state is not None:
            raise ValueError("Invalid observation state")
        if state is False:
            ever_missing = True
        if state is True:
            if ever_missing:
                returned = True
            last_present = j
    final = observations[-1][1]
    absent = [(d, s) for d, s in observations[last_present+1:] if s is False]
    if final is True:
        status = "present"
    elif final is None:
        status = "endpoint_unknown"
    elif len(absent) >= 2 and (absent[-1][0] - absent[0][0]).days >= persistence_days:
        status = "persistent_absence"
    else:
        status = "pending_persistence"
    return {"status": status, "ever_reobserved": returned,
            "last_present": observations[last_present][0].isoformat(),
            "first_terminal_absence": absent[0][0].isoformat() if absent else "",
            "terminal_absence_days": (absent[-1][0] - absent[0][0]).days if absent else 0,
            "negative_observations": len(absent)}


def write_csv(path, rows):
    atomic_write_csv(path, rows)


def load_snapshots(raw_dir):
    with (raw_dir / "download_manifest.csv").open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    groups, qa = defaultdict(list), []
    for item in manifest:
        if item["status"] != "ok":
            raise ValueError("Incomplete acquisition manifest")
        path = raw_dir / f"{item['market']}_{item['snapshot_date']}_listings.csv.gz"
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Raw file checksum changed: {path.name}")
        with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
            records = [{key: r.get(key, "") for key in FIELDS} for r in csv.DictReader(handle)]
        rows = {r["id"]: r for r in records}
        if len(rows) != len(records) or len(records) != int(item["expected_rows"]):
            raise ValueError("Duplicate IDs or inconsistent row counts")
        complete = max(date.fromisoformat(r["last_scraped"][:10]) for r in records)
        start = date.fromisoformat(item["snapshot_date"])
        if complete < start or (complete-start).days > 30:
            raise ValueError("Implausible scrape window")
        licenses = defaultdict(list)
        for r in records:
            token = license_id(r["license"])
            if token:
                licenses[token].append(r)
        sources = Counter(r["source"] for r in records)
        groups[item["market"]].append({"start": start, "complete": complete, "rows": rows,
            "licenses": licenses, "source_partial": item["source_partial_scope"] == "True"})
        qa.append({"market": item["market"], "snapshot_start": start.isoformat(),
            "snapshot_complete": complete.isoformat(), "listing_ids": len(rows),
            "city_search_rows": sources["city scrape"], "previous_search_rows": sources["previous scrape"],
            "source_partial_scope": item["source_partial_scope"],
            "conservative_no_negative_evidence": item["source_partial_scope"] == "True" or "2026-02" <= item["snapshot_date"][:7] <= "2026-05",
            "sha256": item["sha256"], "source_url": item["url"]})
    for market in groups:
        groups[market].sort(key=lambda s: s["complete"])
    return groups, qa


def build_market(market, snapshots, policy):
    if policy not in ("source_flags", "conservative"):
        raise ValueError(f"Unknown coverage policy: {policy}")
    if not snapshots or snapshots[0]["source_partial"]:
        raise ValueError("A non-partial baseline snapshot is required")
    baseline = snapshots[0]["rows"]
    baseline_license_counts = Counter(license_id(r["license"]) for r in baseline.values())
    output, aliases = [], []
    for identifier, listing in sorted(baseline.items()):
        token = license_id(listing["license"]) if market == "san-diego" else ""
        unique_anchor = bool(token and baseline_license_counts[token] == 1)
        raw_observations, linked_observations = [], []
        final_alias = ""
        for snapshot in snapshots:
            negative_ok = not snapshot["source_partial"]
            if policy == "conservative" and "2026-02" <= snapshot["start"].strftime("%Y-%m") <= "2026-05":
                negative_ok = False
            own = snapshot["rows"].get(identifier)
            raw_state = True if own else (False if negative_ok else None)
            linked_state = raw_state
            match = None
            if own is None and unique_anchor:
                candidates = snapshot["licenses"].get(token, [])
                if len(candidates) == 1 and candidates[0]['id'] not in baseline and compatible(listing, candidates[0]):
                    match = candidates[0]
                    linked_state = True
                    aliases.append({"market": market, "baseline_id": identifier, "license_id": token,
                                    "replacement_id": match["id"], "snapshot_complete": snapshot["complete"].isoformat(),
                                    "method": "unique_license_same_room_type_within_300m"})
            raw_observations.append((snapshot["complete"], raw_state))
            linked_observations.append((snapshot["complete"], linked_state))
            if snapshot is snapshots[-1] and match:
                final_alias = match["id"]
        raw_result = terminal_state(raw_observations)
        linked_result = terminal_state(linked_observations)
        reviews = number(listing["number_of_reviews_ltm"])
        minimum = number(listing["minimum_nights"])
        active_home = listing["room_type"] == "Entire home/apt" and reviews is not None and reviews > 0 and minimum is not None and minimum < 30
        row = {"market": market, "policy": policy, "listing_id": identifier, "license_id": token,
               "unique_baseline_license": unique_anchor, "baseline_reviewed_str_home": active_home,
               "baseline_reviews_ltm": reviews, "baseline_room_type": listing["room_type"],
               "baseline_minimum_nights": minimum, "id_status": raw_result["status"],
               "linked_status": linked_result["status"], "id_reobserved_after_gap": raw_result["ever_reobserved"],
               "replacement_id_at_endpoint": final_alias,
               "last_present": linked_result["last_present"],
               "first_terminal_absence": linked_result["first_terminal_absence"],
               "terminal_absence_days": linked_result["terminal_absence_days"],
               "negative_observations": linked_result["negative_observations"],
               "id_persistent_30": terminal_state(raw_observations, 30)["status"] == "persistent_absence",
               "id_persistent_60": terminal_state(raw_observations, 60)["status"] == "persistent_absence",
               "id_persistent_180": terminal_state(raw_observations, 180)["status"] == "persistent_absence",
               "name": listing["name"], "description": listing["description"],
               "picture_url": listing["picture_url"], "host_id": listing["host_id"]}
        output.append(row)
    return output, aliases


def summarize(market, snapshots, rows, policy, cohort):
    if cohort == "reviewed_str_homes":
        rows = [r for r in rows if r["baseline_reviewed_str_home"]]
    n = len(rows)
    raw = Counter(r["id_status"] for r in rows)
    linked = Counter(r["linked_status"] for r in rows)
    if not n or sum(raw.values()) != n or sum(linked.values()) != n:
        raise ValueError("Invalid cohort reconciliation")
    review_base = sum(r["baseline_reviews_ltm"] or 0 for r in rows)
    review_gone = sum(r["baseline_reviews_ltm"] or 0 for r in rows if r["linked_status"] == "persistent_absence")
    return {"market": market, "coverage_policy": policy, "cohort": cohort,
            "baseline_snapshot_start": snapshots[0]["start"].isoformat(),
            "baseline_snapshot_complete": snapshots[0]["complete"].isoformat(),
            "endpoint_snapshot_start": snapshots[-1]["start"].isoformat(),
            "endpoint_snapshot_complete": snapshots[-1]["complete"].isoformat(),
            "followup_days": (snapshots[-1]["complete"]-snapshots[0]["complete"]).days,
            "baseline_ids": n, "endpoint_id_present": raw["present"],
            "endpoint_id_absent": n-raw["present"]-raw["endpoint_unknown"],
            "id_absence_fraction": (n-raw["present"]-raw["endpoint_unknown"])/n,
            "id_persistent_90": raw["persistent_absence"], "id_persistent_90_fraction": raw["persistent_absence"]/n,
            "id_pending_90": raw["pending_persistence"],
            "license_supported_replacement_present": sum(bool(r["replacement_id_at_endpoint"]) for r in rows),
            "linked_persistent_90": linked["persistent_absence"],
            "linked_persistent_90_fraction": linked["persistent_absence"]/n,
            "linked_pending_90": linked["pending_persistence"],
            "linked_endpoint_unknown": linked["endpoint_unknown"],
            "id_reobserved_after_gap": sum(r["id_reobserved_after_gap"] for r in rows),
            "id_persistent_30": sum(r["id_persistent_30"] for r in rows),
            "id_persistent_60": sum(r["id_persistent_60"] for r in rows),
            "id_persistent_180": sum(r["id_persistent_180"] for r in rows),
            "baseline_reviews_ltm": review_base, "linked_persistent_baseline_reviews_ltm": review_gone,
            "review_weighted_persistent_fraction": review_gone/review_base if review_base else None,
            "rate_definition": "endpoint observed absence lasting >=90 days; not annual first-exit or confirmed property churn"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT/"data/raw/listing_churn_execution")
    parser.add_argument("--output-dir", type=Path, default=ROOT/"data/processed/listing_churn_execution")
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260907)
    parser.add_argument("--registry-date", default="2026-09-07")
    args = parser.parse_args()
    groups, qa = load_snapshots(args.raw_dir)
    summary, granular, all_aliases = [], [], []
    for market, snapshots in sorted(groups.items()):
        for policy in ("source_flags", "conservative"):
            rows, aliases = build_market(market, snapshots, policy)
            for cohort in ("all_listings", "reviewed_str_homes"):
                summary.append(summarize(market, snapshots, rows, policy, cohort))
            granular.extend(rows)
            if policy == "conservative":
                all_aliases.extend(aliases)
    registry_path = args.raw_dir/f"san_diego_stro_licenses_{args.registry_date}.csv"
    registry_metadata = json.loads(registry_path.with_suffix(".json").read_text(encoding="utf-8"))
    if hashlib.sha256(registry_path.read_bytes()).hexdigest() != registry_metadata["sha256"]:
        raise ValueError("Municipal registry checksum changed")
    with registry_path.open(newline="", encoding="utf-8-sig") as handle:
        registry_rows = list(csv.DictReader(handle))
    registry = defaultdict(list)
    if len(registry_rows) != registry_metadata["rows"]:
        raise ValueError("Municipal registry row count changed")
    for row in registry_rows:
        registry[row["license_id"]].append(row)
    sample_population = [r for r in granular if r["market"] == "san-diego" and r["policy"] == "conservative"
                         and r["linked_status"] == "persistent_absence" and r["baseline_reviewed_str_home"] and r["unique_baseline_license"]]
    if not 0 < args.sample_size <= len(sample_population):
        raise ValueError("Sample size outside eligible cohort")
    sample = random.Random(args.seed).sample(sorted(sample_population, key=lambda r:r["listing_id"]), args.sample_size)
    for i, row in enumerate(sample, 1):
        matches = registry.get(row["license_id"], [])
        row = row.copy()
        row.update(case_id=f"SD-{i:02d}", registry_match_count=len(matches),
                   registry_address=matches[0]["address"] if len(matches) == 1 else "",
                   registry_expiration=matches[0]["date_expiration"] if len(matches) == 1 else "",
                   destination="unresolved", destination_evidence_url="")
        sample[i-1] = row
    sample_path = args.raw_dir/'destination_sample.csv'
    if sample_path.exists():
        from summarize_listing_destinations import sample_identity_hash
        with sample_path.open(encoding='utf-8-sig', newline='') as handle:
            existing_sample = list(csv.DictReader(handle))
        if sample_identity_hash(existing_sample) != sample_identity_hash(sample):
            raise ValueError('The frozen reviewed sample would change; use a separate raw/output directory and evidence ledger')
    # Validate registry and sample identity before replacing generated artifacts.
    write_csv(args.output_dir/'cohort_summary.csv', summary)
    write_csv(args.output_dir/'snapshot_quality.csv', qa)
    write_csv(args.raw_dir/'listing_outcomes.csv', granular)
    atomic_write_csv(args.raw_dir/'license_alias_evidence.csv', all_aliases,
                     ['market','baseline_id','license_id','replacement_id','snapshot_complete','method'])
    write_csv(sample_path, sample)
    registry_summary = {"eligible_sample_population": len(sample_population), "sample_size": len(sample),
        "sample_seed": args.seed, "sample_design": "simple random sample of conservative persistent, baseline reviewed STR entire-home IDs with unique baseline STRO license",
        "eligible_population_current_registry_match": sum(len(registry.get(r["license_id"], [])) == 1 for r in sample_population),
        "sample_current_registry_match": sum(r["registry_match_count"] == 1 for r in sample),
        "registry_interpretation": "Current licensing evidence only; does not prove operation, platform, sale or long-term rental"}
    args.output_dir.joinpath("execution_metadata.json").write_text(json.dumps({
        "source": json.loads((args.raw_dir/"team_source.json").read_text()),
        "python_version": platform.python_version(),
        "registry_capture": registry_metadata,
        "persistence_days":90, "geographic_match_radius_m":300,
        "conservative_policy": "No negative evidence from February-May 2026; keep all positive observations, including partial snapshots",
        "registry": registry_summary,
    },indent=2)+"\n",encoding="utf-8")
    for row in summary:
        print(f"{row['market']} {row['coverage_policy']} {row['cohort']}: N={row['baseline_ids']}, raw absence={row['id_absence_fraction']:.2%}, persistent90={row['id_persistent_90_fraction']:.2%}, license-linked={row['linked_persistent_90_fraction']:.2%}")
    print(json.dumps(registry_summary, indent=2))


if __name__ == "__main__":
    main()
