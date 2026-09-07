"""Measure the full team panel with transparent denominators and coverage limits.

Primary: fixed autumn-2025 cohort absent at the final summer-2026 observation.
Persistence: terminal observed absence >=90 actual days, with partial-file negatives
unknown and positives retained. These are not official annual or global churn rates.
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
import platform
import re

from acquire_churn_panel import ROOT, MARKETS
from audit_listing_churn_inputs import boolean
from execute_listing_churn import number, terminal_state, compatible, write_csv

POLICIES = ("team_flags", "exclude_feb_may_negatives")


def permit_key(value):
    """Full exact permit field only. No fuzzy match or assumption of legal validity."""
    cleaned = re.sub(r"\s+", " ", (value or "").strip().upper())
    if len(cleaned) < 6 or sum(c.isdigit() for c in cleaned) < 5:
        return ""
    if any(word in cleaned for word in ("EXEMPT", "EXEMPTION", "PENDING", "NOT REQUIRED", "APPLICATION", "000000")):
        return ""
    return cleaned


def endpoint_aliases(baseline, endpoint):
    """Candidate new Airbnb IDs; requires unique exact permit, room/bed/geo agreement.

    No existing baseline ID may be assigned as a new replacement. This does not dedup
    the whole baseline population or validate permit authenticity / physical identity.
    """
    a, b = defaultdict(list), defaultdict(list)
    for r in baseline.values():
        key = permit_key(r["license"])
        if key:
            a[key].append(r)
    for r in endpoint.values():
        key = permit_key(r["license"])
        if key:
            b[key].append(r)
    links = {}
    for key, old in a.items():
        new = b.get(key, [])
        if len(old) != 1 or len(new) != 1:
            continue
        old, new = old[0], new[0]
        if old["id"] in endpoint or new["id"] in baseline:
            continue
        beds_old, beds_new = number(old["bedrooms"]), number(new["bedrooms"])
        if beds_old is None or beds_new is None or beds_old != beds_new:
            continue
        if compatible(old, new):
            links[old["id"]] = new["id"]
    if len(set(links.values())) != len(links):
        raise ValueError("Many-to-one replacement link")
    return links


def valid_negative(snapshot, policy):
    if policy not in POLICIES:
        raise ValueError("Unknown policy")
    return not snapshot["partial"] and not (policy == POLICIES[1] and "2026-02" <= snapshot["start"][:7] <= "2026-05")


def load_snapshot(item, raw_dir, detailed=False):
    path = ROOT/item["local_path"]
    with path.open("rb") as h:
        if hashlib.file_digest(h,"sha256").hexdigest() != item["sha256"]:
            raise ValueError(f"Checksum changed: {path.name}")
    ids, records, source_counts, dates = set(), {}, Counter(), Counter()
    keep = ["id","host_id","room_type","minimum_nights","number_of_reviews_ltm",
            "license","latitude","longitude","bedrooms"]
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as h:
        for r in csv.DictReader(h):
            if not r["id"].isdigit() or r["id"] in ids:
                raise ValueError("Duplicate or invalid ID")
            ids.add(r["id"]); source_counts[r["source"]] += 1
            dates[date.fromisoformat(r["last_scraped"][:10])] += 1
            if detailed:
                records[r["id"]] = {k:r.get(k,"") for k in keep}
    if len(ids) != int(item["expected_rows"]):
        raise ValueError("Count does not reconcile")
    complete = max(dates)
    start = date.fromisoformat(item["snapshot_start"])
    if complete < start or (complete-start).days > 30:
        raise ValueError("Invalid scrape window")
    return dict(ids=ids, records=records, complete=complete, start=item["snapshot_start"],
                partial=boolean(item["source_partial_scope"]), sources=dict(source_counts),
                earliest_scraped=min(dates).isoformat(), url=item["url"], sha256=item["sha256"])


def measure_market(market, snapshots, cohort):
    baseline, endpoint = snapshots[0]["records"], snapshots[-1]["records"]
    aliases = endpoint_aliases(baseline, endpoint)
    members = baseline
    if cohort == "reviewed_str_homes":
        members = {k:r for k,r in baseline.items() if r["room_type"] == "Entire home/apt"
                   and (number(r["number_of_reviews_ltm"]) or 0) > 0
                   and number(r["minimum_nights"]) is not None and number(r["minimum_nights"]) < 30}
    elif cohort != "all_listings":
        raise ValueError("Unknown cohort")
    if not members:
        raise ValueError("Empty cohort")
    base_ids = set(members)
    retained = base_ids & snapshots[-1]["ids"]
    missing = base_ids - snapshots[-1]["ids"]
    common = dict(market=market, country=MARKETS[market][1], region=MARKETS[market][2], cohort=cohort,
                  baseline_start=snapshots[0]["start"], baseline_complete=snapshots[0]["complete"].isoformat(),
                  endpoint_start=snapshots[-1]["start"], endpoint_complete=snapshots[-1]["complete"].isoformat(),
                  interval_days=(snapshots[-1]["complete"]-snapshots[0]["complete"]).days,
                  snapshots=len(snapshots), baseline_ids=len(members), retained_ids=len(retained),
                  missing_ids=len(missing), id_attrition=len(missing)/len(members),
                  alternative_id_candidates=sum(k in aliases for k in missing),
                  baseline_review_total=sum(number(r["number_of_reviews_ltm"]) or 0 for r in members.values()),
                  baseline_hosts=len({r["host_id"] for r in members.values()}))
    if cohort == "all_listings":
        adds = len(snapshots[-1]["ids"]-base_ids)
        if len(snapshots[-1]["ids"]) != len(base_ids) + adds-len(missing):
            raise ValueError("Stock-flow identity failed")
        common.update(endpoint_ids=len(snapshots[-1]["ids"]), new_to_pair_ids=adds)
    else:
        common.update(endpoint_ids="",new_to_pair_ids="")
    output, case_rows = [], []
    for policy in POLICIES:
        valid = [valid_negative(s,policy) for s in snapshots]
        mature = [s for i,s in enumerate(snapshots) if i > 0 and valid[i]
                  and (snapshots[-1]["complete"]-s["complete"]).days >= 90]
        eligible = not snapshots[0]["partial"] and not snapshots[-1]["partial"]
        persistence_eligible = eligible and bool(mature) and valid[-1]
        status = Counter(); returned = 0; raw_persist_30 = raw_persist_180 = 0
        persistent_with_alias = 0; missing_reviews = persistent_reviews = 0
        for identifier, r in members.items():
            obs = [(s["complete"], True if identifier in s["ids"] else (False if valid[i] else None))
                   for i,s in enumerate(snapshots)]
            state = terminal_state(obs)
            status[state["status"]] += 1
            returned += state["ever_reobserved"]
            rv = number(r["number_of_reviews_ltm"]) or 0
            if identifier in missing:
                missing_reviews += rv
            if state["status"] == "persistent_absence":
                persistent_reviews += rv
                persistent_with_alias += identifier in aliases
            raw_persist_30 += terminal_state(obs,30)["status"] == "persistent_absence"
            raw_persist_180 += terminal_state(obs,180)["status"] == "persistent_absence"
            if cohort == "all_listings":
                case_rows.append(dict(market=market, policy=policy, listing_id=identifier,
                    baseline_host_id=r["host_id"], baseline_room_type=r["room_type"],
                    baseline_reviews_ltm=rv, baseline_minimum_nights=r["minimum_nights"],
                    candidate_replacement_id=aliases.get(identifier,""), **state))
        if sum(status.values()) != len(members):
            raise ValueError("State partition failed")
        gaps = [(b["complete"]-a["complete"]).days for a,b in zip(
            [s for i,s in enumerate(snapshots) if valid[i]], [s for i,s in enumerate(snapshots) if valid[i]][1:])]
        output.append(dict(**common, policy=policy, pair_eligible=eligible,
            pair_exclusion="" if eligible else "partial baseline or endpoint",
            persistence_eligible=persistence_eligible,
            persistence_exclusion="" if persistence_eligible else ("partial baseline or endpoint" if not eligible else "no valid post-baseline negative observation at least 90 days before endpoint"),
            valid_postbaseline_observations=sum(valid[1:]), mature_negative_opportunities=len(mature),
            longest_valid_observation_gap_days=max(gaps) if gaps else "",
            persistent_90=status["persistent_absence"], pending_90=status["pending_persistence"],
            endpoint_unknown=status["endpoint_unknown"], persistent_90_rate=status["persistent_absence"]/len(members) if persistence_eligible else None,
            persistent_90_with_alternative_id=persistent_with_alias,
            persistent_90_after_candidate_screen=status["persistent_absence"]-persistent_with_alias,
            persistent_30=raw_persist_30,persistent_180=raw_persist_180,
            ids_reobserved_after_gap=returned, missing_baseline_reviews=missing_reviews,
            persistent_baseline_reviews=persistent_reviews,
            review_weighted_id_attrition=missing_reviews/common["baseline_review_total"] if common["baseline_review_total"] else None))
    return output, case_rows, aliases


def pool_rates(rows, scope, cohort, policy, statistic):
    selected = [r for r in rows if r["cohort"]==cohort and r["policy"]==policy]
    if scope != "all_eligible_markets":
        selected = [r for r in selected if r["region"]==scope]
    eligibility = "pair_eligible" if statistic == "id_attrition" else "persistence_eligible"
    selected = [r for r in selected if r[eligibility]]
    if not selected:
        return None
    field = "missing_ids" if statistic == "id_attrition" else "persistent_90"
    n = sum(r["baseline_ids"] for r in selected); count = sum(r[field] for r in selected)
    city_rates = [r[field]/r["baseline_ids"] for r in selected]
    loo = [(count-r[field])/(n-r["baseline_ids"]) for r in selected if n > r["baseline_ids"]]
    return dict(scope=scope,cohort=cohort,policy=policy,statistic=statistic,
                markets=len(selected),countries=len({r["country"] for r in selected}),
                baseline_ids=n, event_ids=count, listing_weighted_rate=count/n,
                equal_market_weighted_rate=sum(city_rates)/len(city_rates),
                min_market_rate=min(city_rates),max_market_rate=max(city_rates),
                leave_one_market_out_min=min(loo) if loo else None,
                leave_one_market_out_max=max(loo) if loo else None,
                max_market_baseline_weight=max(r["baseline_ids"] for r in selected)/n,
                min_interval_days=min(r["interval_days"] for r in selected),
                max_interval_days=max(r["interval_days"] for r in selected),
                market_set=" | ".join(sorted(r["market"] for r in selected)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir",type=Path,default=ROOT/"data/raw/listing_churn_panel")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"data/processed/listing_churn_panel")
    args=parser.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    source=json.loads((args.raw_dir/"source.json").read_text(encoding="utf-8"))
    with (args.raw_dir/"download_manifest.csv").open(encoding="utf-8",newline="") as h:
        manifest=list(csv.DictReader(h))
    with (args.raw_dir/"team_snapshot_catalog.csv").open(encoding="utf-8-sig",newline="") as h:
        expected=[r for r in csv.DictReader(h) if r["dump_date"] >= source["start"]]
    expected_keys={(r["city"],r["dump_date"]) for r in expected}
    seen_keys=[(r["market"],r["snapshot_start"]) for r in manifest]
    if len(set(seen_keys)) != len(seen_keys) or set(seen_keys) != expected_keys:
        raise ValueError("Acquisition must finish; duplicate or incomplete manifest")
    groups=defaultdict(list)
    for r in manifest: groups[r["market"]].append(r)
    rates,qa,inventory,baseline_owners=[],[],[],{}
    for market in sorted(groups):
        items=sorted(groups[market],key=lambda r:r["snapshot_start"])
        failures=[r for r in items if r["status"]!="ok"]
        if failures:
            inventory.append(dict(market=market,country=MARKETS[market][1],catalogued_snapshots=len(items),
                acquired_snapshots=len(items)-len(failures),status="excluded_acquisition_gap",reason=" | ".join(r["snapshot_start"]+" "+r["error"] for r in failures)))
            continue
        snapshots=[load_snapshot(r,args.raw_dir,detailed=i in (0,len(items)-1)) for i,r in enumerate(items)]
        dates=[s["complete"] for s in snapshots]
        if dates!=sorted(set(dates)):
            raise ValueError(f"Overlapping / out-of-order completion dates: {market}")
        for identifier in snapshots[0]["ids"]:
            if identifier in baseline_owners:
                raise ValueError(f"Cross-market baseline duplication: {market} vs {baseline_owners[identifier]}")
            baseline_owners[identifier]=market
        eligible=not snapshots[0]["partial"] and not snapshots[-1]["partial"]
        inventory.append(dict(market=market,country=MARKETS[market][1],catalogued_snapshots=len(items),
            acquired_snapshots=len(items),status="pair_eligible" if eligible else "excluded_endpoint_coverage",
            reason="" if eligible else "Source-flagged baseline or endpoint; do not pool"))
        for s in snapshots:
            qa.append(dict(market=market,start=s["start"],complete=s["complete"].isoformat(),
                rows=len(s["ids"]),partial=s["partial"],city_scrape=s["sources"].get("city scrape",0),
                previous_scrape=s["sources"].get("previous scrape",0),
                source_url=s["url"],sha256=s["sha256"]))
        for cohort in ("all_listings","reviewed_str_homes"):
            result,cases,aliases=measure_market(market,snapshots,cohort)
            rates.extend(result)
            if cases:
                write_csv(args.raw_dir/f"{market}_listing_outcomes.csv",cases)
            if cohort=="all_listings" and aliases:
                write_csv(args.raw_dir/f"{market}_alternative_id_candidates.csv",
                    [dict(baseline_id=k,candidate_id=v,method="unique_exact_full_permit_same_room_bedrooms_within_300m_new_to_cohort") for k,v in sorted(aliases.items())])
        print(f"{market}: {len(snapshots[0]['ids']):,} baseline IDs; {len(snapshots)} snapshots; pair eligible={eligible}",flush=True)
    pools=[]
    for scope in ("all_eligible_markets", "North America", "Europe", "Latin America", "Asia Pacific"):
        for cohort in ("all_listings","reviewed_str_homes"):
            for policy in POLICIES:
                for statistic in ("id_attrition","persistent_90"):
                    r=pool_rates(rates,scope,cohort,policy,statistic)
                    if r: pools.append(r)
    write_csv(args.output_dir/"market_rates.csv",rates)
    write_csv(args.output_dir/"pooled_rates.csv",pools)
    write_csv(args.output_dir/"market_coverage.csv",inventory)
    write_csv(args.output_dir/"snapshot_quality.csv",qa)
    (args.output_dir/"execution_metadata.json").write_text(json.dumps(dict(source=source,
        python_version=platform.python_version(),acquired_snapshots=len(qa),
        cross_market_baseline_duplicate_ids=0,universe="team-selected historical Inside Airbnb city panel; not a probability sample of Airbnb",
        pooling="sum of event IDs divided by sum of baseline IDs; separate equal-market and leave-one-market-out sensitivity",
        persistence_days=90,annualized=False,
        candidate_identity="unique exact full permit; equal room type and nonmissing bedroom count; <=300m; replacement ID not in baseline; unvalidated linkage",
        policies={"team_flags":"Unknown negative evidence in source-flagged partial snapshots; retain all positives",
                  "exclude_feb_may_negatives":"Additional blanket February-May 2026 negative-evidence exclusion; sensitivity only, not validated collection-error classification"},
        limitations=["Unequal autumn-to-summer intervals; no annualization", "Nonflagged coverage is not guaranteed", "Repeated partial periods can make persistent exits unidentifiable; no zero-filled rates", "Replacement candidates are not verified property identities", "No population destination shares established"]),indent=2)+"\n",encoding="utf-8")
    for r in pools:
        if r["scope"]=="all_eligible_markets":
            print(f"{r['cohort']} {r['policy']} {r['statistic']}: {r['event_ids']:,}/{r['baseline_ids']:,} = {r['listing_weighted_rate']:.2%}, {r['markets']} markets",flush=True)


if __name__=="__main__":
    main()
