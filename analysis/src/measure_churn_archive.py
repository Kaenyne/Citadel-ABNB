"""Measure a broad, common-month listing cohort, with explicit coverage exclusions.

Pooled IDs are unique: drop nested geographies (>=90% overlap with a larger file),
then exclude remaining cross-market duplicate baseline IDs. Presence anywhere in the selected public panel is
positive evidence. A blank persistence rate means no eligible observation window.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform

from acquire_churn_archive import ROOT, MONTHS, select_snapshots
from execute_listing_churn import number, write_csv
from measure_churn_panel import endpoint_aliases, pool_rates

REGIONS = {
    "North America": {"United States", "Canada"},
    "Latin America": {"Argentina", "Belize", "Brazil", "Chile", "Mexico"},
    "Asia Pacific": {"Australia", "China", "Japan", "New Zealand", "Singapore", "Taiwan", "Thailand"},
    "Africa": {"South Africa"},
    "Europe": {"Austria", "Belgium", "Czech Republic", "Denmark", "France", "Germany", "Greece",
        "Hungary", "Ireland", "Italy", "Latvia", "Malta", "Norway", "Portugal", "Spain", "Sweden",
        "Switzerland", "The Netherlands", "Turkey", "United Kingdom"},
}
POLICIES = ("coverage_screen", "exclude_march_negatives")


def region(country):
    matches=[k for k,v in REGIONS.items() if country in v]
    if len(matches)!=1: raise ValueError(f"Review region mapping for {country}")
    return matches[0]


def geographic_exclusions(owners, counts):
    overlap=Counter()
    for markets in owners.values():
        for a,b in itertools.combinations(sorted(markets),2): overlap[(a,b)]+=1
    nested={}
    for (a,b),count in sorted(overlap.items()):
        small,large=sorted((a,b),key=lambda k:(counts[k],k))
        if count/counts[small]>=.9:
            nested[small]=large
    duplicates={k for k,v in owners.items() if len([m for m in v if m not in nested])>1}
    return nested,duplicates,overlap


def load_compact(item, detailed=False, verify=True):
    path=ROOT/item["compact_path"]
    if verify:
        with path.open("rb") as h:
            if hashlib.file_digest(h,"sha256").hexdigest()!=item["compact_sha256"]:
                raise ValueError(f"Compact capture changed: {path.name}")
    with gzip.open(path,"rt",encoding="utf-8",newline="") as h:
        rows={r["id"]:r if detailed else None for r in csv.DictReader(h)}
    if len(rows)!=int(item["rows"]): raise ValueError("Compact row count mismatch")
    return rows if detailed else set(rows)


def persistent_ids(members, snapshots, global_positive, valid, days=90):
    """Set implementation of terminal observed absence; retain partial positives.

    Any positive within the first-negative calendar month conservatively prevents
    starting the clock in that month, even if another market captured it earlier.
    No inference about continuous unobserved dates between snapshots is made.
    """
    if days<=0: raise ValueError("Persistence days must be positive")
    if not valid[-1]: return set(),False
    end=snapshots[-1]["complete"]
    candidates=set(); mature=False
    for i,s in enumerate(snapshots):
        if i==0 or not valid[i] or (end-s["complete"]).days<days: continue
        mature=True
        absent=set(members)
        # All available positives, including months missing from this market's index.
        for month in MONTHS:
            if month>=s["month"]: absent.difference_update(global_positive[month])
        candidates.update(absent)
    return candidates,mature


def measure(market, snapshots, global_positive, duplicate_ids, global_baseline):
    baseline,endpoint=snapshots[0]["records"],snapshots[-1]["records"]
    unique=set(baseline)-duplicate_ids
    present=global_positive[MONTHS[-1]]
    aliases=endpoint_aliases(baseline,endpoint)
    aliases={k:v for k,v in aliases.items() if k in unique and k not in present and v not in global_baseline}
    valid_base=[not s["coverage_flag"] for s in snapshots]
    pair_eligible=valid_base[0] and valid_base[-1]
    country=snapshots[0]["country"]
    output=[]
    for cohort in ("all_listings","reviewed_str_homes"):
        members=unique
        if cohort=="reviewed_str_homes":
            members={k for k in unique if baseline[k]["room_type"]=="Entire home/apt"
                and (number(baseline[k]["number_of_reviews_ltm"]) or 0)>0
                and number(baseline[k]["minimum_nights"]) is not None
                and number(baseline[k]["minimum_nights"])<30}
        if not members: continue
        missing=members-present
        total_reviews=sum(number(baseline[k]["number_of_reviews_ltm"]) or 0 for k in members)
        missing_reviews=sum(number(baseline[k]["number_of_reviews_ltm"]) or 0 for k in missing)
        common=dict(market=market,country=country,region=region(country),cohort=cohort,
            baseline_start=snapshots[0]["start"],baseline_complete=snapshots[0]["complete"].isoformat(),
            endpoint_start=snapshots[-1]["start"],endpoint_complete=snapshots[-1]["complete"].isoformat(),
            interval_days=(snapshots[-1]["complete"]-snapshots[0]["complete"]).days,
            snapshots=len(snapshots),baseline_file_ids=len(baseline),
            overlapping_baseline_ids_excluded=len(set(baseline)&duplicate_ids),
            baseline_ids=len(members),retained_ids=len(members&present),missing_ids=len(missing),
            id_attrition=len(missing)/len(members),
            same_id_observed_elsewhere_at_endpoint=len((members-set(endpoint))&present),
            alternative_id_candidates=len(missing&set(aliases)),
            baseline_review_total=total_reviews,missing_baseline_reviews=missing_reviews,
            review_weighted_id_attrition=missing_reviews/total_reviews if total_reviews else None,
            pair_eligible=pair_eligible,
            pair_exclusion="" if pair_eligible else "Baseline or endpoint flagged by team or below 50% of maximum selected snapshot count")
        for policy in POLICIES:
            valid=[v and not (policy==POLICIES[1] and s["month"]=="2026-03") for v,s in zip(valid_base,snapshots)]
            persistent,mature=persistent_ids(members,snapshots,global_positive,valid)
            eligible=pair_eligible and mature
            persist_alias=persistent&set(aliases)
            if not persistent.issubset(missing): raise ValueError("Persistently absent ID observed at endpoint")
            output.append(dict(**common,policy=policy,persistence_eligible=eligible,
                persistence_exclusion="" if eligible else (common["pair_exclusion"] or "No valid post-baseline negative at least 90 days before endpoint"),
                persistent_90=len(persistent),persistent_90_rate=len(persistent)/len(members) if eligible else None,
                pending_90=len(missing-persistent),persistent_90_with_alternative_id=len(persist_alias),
                persistent_90_after_candidate_screen=len(persistent-persist_alias),
                baseline_hosts=len({baseline[k]["host_id"] for k in members}),
                valid_postbaseline_observations=sum(valid[1:])))
    return output,aliases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir",type=Path,default=ROOT/"data/raw/listing_churn_archive")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"data/processed/listing_churn_archive")
    args=parser.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    source=json.loads((args.raw_dir/"source.json").read_text(encoding="utf-8"))
    metadata=json.loads((args.raw_dir/"public_archive_metadata.json").read_text(encoding="utf-8"))
    selected,selection=select_snapshots(metadata["data"]["allData"]["datasets"])
    with (args.raw_dir/"download_manifest.csv").open(encoding="utf-8",newline="") as h: manifest=list(csv.DictReader(h))
    expected={(r["link"],r["publishDate"]) for r in selected}
    actual=[(r["market"],r["snapshot_start"]) for r in manifest]
    if len(actual)!=len(set(actual)) or set(actual)!=expected:
        raise ValueError("Acquisition has not finished or manifest has duplicate keys")
    groups=defaultdict(list)
    for r in manifest: groups[r["market"]].append(r)
    failures={k for k,items in groups.items() if any(r["status"]!="ok" for r in items)}
    global_positive={m:set() for m in MONTHS}; baseline_owners=defaultdict(list);baseline_counts={}
    for market in sorted(groups):
        items=sorted(groups[market],key=lambda r:r["snapshot_start"])
        for i,item in enumerate(items):
            if item["status"]!="ok": continue
            ids=load_compact(item)
            global_positive[item["snapshot_start"][:7]].update(ids)
            if i==0 and market not in failures:
                baseline_counts[market]=len(ids)
                for identifier in ids: baseline_owners[identifier].append(market)
    nested,duplicates,overlap=geographic_exclusions(baseline_owners,baseline_counts)
    global_baseline=global_positive[MONTHS[0]]
    del baseline_owners
    if overlap:
        write_csv(args.output_dir/"geographic_overlap.csv",[dict(market_a=a,market_b=b,shared_baseline_ids=n) for (a,b),n in sorted(overlap.items())])
    print(f"{len(global_baseline):,} unique starting IDs; {len(duplicates):,} overlap IDs excluded",flush=True)
    rates,qa,coverage=[],[],[]
    for r in selection:
        if not r["acquisition_eligible"]:
            coverage.append(dict(market=r["market"],country=r["country"],status="excluded_no_history",reason=r["reason"],snapshots=0))
    for market in sorted(groups):
        items=sorted(groups[market],key=lambda r:r["snapshot_start"])
        if market in failures:
            coverage.append(dict(market=market,country=items[0]["country"],status="excluded_acquisition_failure",
                reason=" | ".join(r["error"] for r in items if r["status"]!="ok"),snapshots=len(items)))
            continue
        max_count=max(int(r["rows"]) for r in items)
        snapshots=[]
        for i,item in enumerate(items):
            team_flag=item["source_partial_scope"]=="True"
            count_flag=int(item["rows"])<.5*max_count
            detailed=i in (0,len(items)-1)
            rows=load_compact(item,detailed=detailed,verify=False)
            snapshot=dict(start=item["snapshot_start"],month=item["snapshot_start"][:7],
                complete=date.fromisoformat(item["snapshot_complete"]),country=item["country"],
                ids=set(rows),records=rows if detailed else {},coverage_flag=team_flag or count_flag)
            snapshots.append(snapshot)
            qa.append(dict(market=market,country=item["country"],start=item["snapshot_start"],complete=item["snapshot_complete"],
                rows=int(item["rows"]),team_partial_scope=item["source_partial_scope"],count_below_half_max=count_flag,
                negative_evidence_excluded=team_flag or count_flag,city_scrape=item["city_scrape"],previous_scrape=item["previous_scrape"],
                team_historical_count_verified=bool(item["team_historical_count"]),team_current_hash_verified=bool(item["team_current_sha256"]),
                source_url=item["url"],sha256=item["sha256"]))
        dates=[s["complete"] for s in snapshots]
        if dates!=sorted(set(dates)): raise ValueError("Invalid completion-date order")
        if market in nested:
            coverage.append(dict(market=market,country=items[0]["country"],status="excluded_nested_geography",
                reason=f"At least 90% of baseline IDs overlap the larger {nested[market]} file",snapshots=len(items)))
            continue
        result,aliases=measure(market,snapshots,global_positive,duplicates,global_baseline)
        if not result:
            coverage.append(dict(market=market,country=items[0]["country"],status="excluded_empty_unique_cohort",
                reason="No unique baseline IDs remain after geographic exclusions",snapshots=len(items)))
            continue
        rates.extend(result)
        eligible=result[0]["pair_eligible"]
        coverage.append(dict(market=market,country=items[0]["country"],status="pair_eligible" if eligible else "excluded_coverage",
            reason=result[0]["pair_exclusion"],snapshots=len(items)))
        if aliases:
            write_csv(args.raw_dir/f"{market}_alternative_id_candidates.csv",[dict(baseline_id=k,candidate_id=v,
                method="unique_exact_full_permit_same_room_bedrooms_within_300m_new_to_global_baseline") for k,v in sorted(aliases.items())])
        print(f"{market}: N={result[0]['baseline_ids']:,}, missing={result[0]['id_attrition']:.2%}, eligible={eligible}",flush=True)
    pools=[]
    for scope in ("all_eligible_markets",*REGIONS):
        for cohort in ("all_listings","reviewed_str_homes"):
            for policy in POLICIES:
                for stat in ("id_attrition","persistent_90"):
                    p=pool_rates(rates,scope,cohort,policy,stat)
                    if p: pools.append(p)
    write_csv(args.output_dir/"market_rates.csv",rates)
    write_csv(args.output_dir/"pooled_rates.csv",pools)
    write_csv(args.output_dir/"market_coverage.csv",coverage)
    write_csv(args.output_dir/"snapshot_quality.csv",qa)
    evidence=dict(source=source,python_version=platform.python_version(),
        successful_snapshots=len(qa),failed_markets=sorted(failures),
        baseline_unique_ids_before_coverage_screen=len(global_baseline),overlapping_unique_baseline_ids_excluded=len(duplicates),
        nested_geography_exclusions=nested,
        duplicate_rule="Exclude smaller geographies with >=90% baseline-ID overlap with a larger acquired geography. Exclude residual baseline IDs present in multiple remaining geographies from all denominators.",
        positive_rule="Presence anywhere in the acquired panel during the corresponding snapshot month. All positive observations retained, even partial files.",
        coverage_rule="Inherited team partial flags, plus any selected snapshot below 50% of that market's largest selected snapshot. This is a diagnostic, not proof of completeness.",
        persistence_rule="At least two usable negative snapshots spanning >=90 actual completion-date days; no positive in any selected month from first negative onward",
        sensitivity="Exclude all March 2026 negative evidence; still retain March positives",
        annualized=False,geographic_sampling="Availability-selected public Inside Airbnb markets; cities, regions, and some countries; no Airbnb-wide weighting",
        limitations=["September-to-June observation dates vary by market; seasonal exposure is about nine months, not one year",
            "Nonflagged public files are not independently verified complete", "Quarterly observations miss intervening pauses and returns",
            "90-day persistence is snapshot-observed absence, not proven permanent property exit",
            "Review-weighted results use review counts, not revenue or nights", "Exact permit links are unvalidated replacement candidates",
            "No population sale, rental, or competitor-migration share identified"])
    evidence["team_historical_source"]=json.loads((ROOT/"data/raw/listing_churn_panel/source.json").read_text(encoding="utf-8"))
    evidence["team_current_manifest_sha256"]=hashlib.sha256((ROOT/"data/manifests/inside_airbnb_download_log.csv").read_bytes()).hexdigest()
    (args.output_dir/"execution_metadata.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    for p in pools:
        if p["scope"]=="all_eligible_markets":
            print(f"{p['cohort']} {p['policy']} {p['statistic']}: {p['event_ids']:,}/{p['baseline_ids']:,} = {p['listing_weighted_rate']:.2%}, {p['markets']} markets",flush=True)


if __name__=="__main__": main()
