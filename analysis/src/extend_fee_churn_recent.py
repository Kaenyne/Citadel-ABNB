"""Latest team-panel intervals and diagnostics of the winter disappearance spike.

Uses hash-checked cached captures only. No fee treatment is inferred from a host's
portfolio or a listing's country. Short-lag reappearance is not 90-day churn.
"""
from collections import Counter, defaultdict
from datetime import date
import csv
import gzip
import hashlib
import json
from statistics import median

from acquire_churn_archive import ROOT
from execute_listing_churn import number, write_csv
from measure_churn_archive import load_compact
from measure_fee_churn_history import read, cohort_ids

MONTHS = ("2026-06", "2026-07", "2026-08")
SPIKE_MARKETS = ("toronto", "vaud", "new-zealand")
OUT = ROOT / "data/processed/fee_churn_recent"


def cached_inventory():
    items = {}
    for folder in ("listing_churn_panel", "listing_churn_archive", "fee_churn_history"):
        for r in read(ROOT / f"data/raw/{folder}/download_manifest.csv"):
            if r["status"] != "ok":
                continue
            key = r["market"], r["snapshot_start"]
            if key in items and items[key]["sha256"] != r["sha256"]:
                raise ValueError(f"Conflicting source hashes: {key}")
            if key not in items or r.get("compact_path"):
                items[key] = r
    quality = {(r["market"], r["start"]): r for r in read(ROOT / "data/processed/fee_churn_history/snapshot_quality.csv")}
    for key, r in items.items():
        q = quality[key]
        if r["sha256"] != q["sha256"]:
            raise ValueError("Quality audit source changed")
        if not r.get("compact_path"):
            path = ROOT / f"data/raw/fee_churn_history/compact_cache/{key[0]}_{key[1]}.csv.gz"
            meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
            if meta["sha256"] != r["sha256"]:
                raise ValueError("Compact source hash changed")
            r.update(meta, compact_path=path.relative_to(ROOT).as_posix())
        r["negative_excluded"] = q["negative_excluded"] == "True"
    return items


def interval_counts(members, endpoint_positives, later_positives=None):
    if not members:
        raise ValueError("Empty at-risk cohort")
    missing = members - endpoint_positives
    returned = None if later_positives is None else len(missing & later_positives)
    return dict(baseline_ids=len(members), missing_ids=len(missing),
                disappearance_rate=len(missing)/len(members),
                reobserved_next_vintage=returned,
                still_missing_next_vintage=None if returned is None else len(missing)-returned)


def latest_panel(items):
    team = {r["city"] for r in read(ROOT / "data/raw/listing_churn_panel/team_snapshot_catalog.csv")}
    selected = {}
    positives = defaultdict(set)
    positive_sources = []
    for (market, start), r in sorted(items.items()):
        month = start[:7]
        if month not in MONTHS:
            continue
        ids = load_compact(r)
        positives[month].update(ids)  # Partial files still supply positive evidence.
        positive_sources.append(dict(market=market, start=start, complete=r["snapshot_complete"],
            rows=len(ids), sha256=r["sha256"], compact_sha256=r["compact_sha256"], url=r["url"],
            negative_excluded=r["negative_excluded"], city_scrape=r.get("city_scrape"),
            previous_scrape=r.get("previous_scrape"), unknown_source_rows=r.get("unknown_source_rows")))
        if market in team and not r["negative_excluded"]:
            key = market, month
            if key not in selected or start > selected[key]["snapshot_start"]:
                selected[key] = r
    balanced = sorted(m for m in team if all((m, month) in selected for month in MONTHS))
    if len(balanced) != len(team):
        raise ValueError(f"Latest balanced team panel incomplete: {set(team)-set(balanced)}")
    rows, summaries = [], []
    for left, right in zip(MONTHS, MONTHS[1:]):
        baselines = {m: load_compact(selected[m, left], detailed=True) for m in balanced}
        frequency = Counter(key for records in baselines.values() for key in records)
        duplicates = {key for key, n in frequency.items() if n > 1}
        for market, records in baselines.items():
            a, b = selected[market, left], selected[market, right]
            days = (date.fromisoformat(b["snapshot_complete"])-date.fromisoformat(a["snapshot_complete"])).days
            if days <= 0:
                raise ValueError("Non-increasing observation completion dates")
            for cohort in ("all_listings", "reviewed_str_homes"):
                members = cohort_ids(records, cohort) - duplicates
                counts = interval_counts(members, positives[right], positives["2026-08"] if right == "2026-07" else None)
                missing = members - positives[right]
                reviews = sum(number(records[key]["number_of_reviews_ltm"]) or 0 for key in members)
                missing_reviews = sum(number(records[key]["number_of_reviews_ltm"]) or 0 for key in missing)
                rows.append(dict(market=market, cohort=cohort, start_month=left, end_month=right,
                    start_vintage=a["snapshot_start"], end_vintage=b["snapshot_start"],
                    start_complete=a["snapshot_complete"], end_complete=b["snapshot_complete"], interval_days=days,
                    vintage_gap_days=(date.fromisoformat(b["snapshot_start"])-date.fromisoformat(a["snapshot_start"])).days,
                    cross_market_duplicate_ids_excluded=len(set(records) & duplicates), **counts,
                    baseline_reviews=reviews, missing_baseline_reviews=missing_reviews))
        for cohort in ("all_listings", "reviewed_str_homes"):
            group = [r for r in rows if r["start_month"] == left and r["cohort"] == cohort]
            n, d = sum(r["baseline_ids"] for r in group), sum(r["missing_ids"] for r in group)
            returned = None if right == "2026-08" else sum(r["reobserved_next_vintage"] for r in group)
            reviews = sum(r["baseline_reviews"] for r in group)
            summaries.append(dict(start_month=left, end_month=right, cohort=cohort, markets=len(group),
                baseline_ids=n, missing_ids=d, disappearance_rate=d/n,
                review_weighted_disappearance=sum(r["missing_baseline_reviews"] for r in group)/reviews if reviews else None,
                equal_market_mean=sum(r["disappearance_rate"] for r in group)/len(group),
                min_interval_days=min(r["interval_days"] for r in group), max_interval_days=max(r["interval_days"] for r in group),
                min_vintage_gap_days=min(r["vintage_gap_days"] for r in group), max_vintage_gap_days=max(r["vintage_gap_days"] for r in group),
                reobserved_next_vintage=returned, still_missing_next_vintage=None if returned is None else d-returned,
                persistent_90_rate=None, market_set=" | ".join(balanced)))
    write_csv(OUT / "market_rates.csv", rows)
    write_csv(OUT / "pooled_rates.csv", summaries)
    write_csv(OUT / "positive_source_manifest.csv", positive_sources)
    return summaries


def raw_profile(item, missing):
    path = ROOT / item["local_path"]
    with path.open("rb") as h:
        if hashlib.file_digest(h, "sha256").hexdigest() != item["sha256"]:
            raise ValueError("Raw file changed")
    groups = defaultdict(list)
    dates = Counter()
    with gzip.open(path, "rt", encoding="utf-8", newline="") as h:
        for r in csv.DictReader(h):
            groups["missing" if r["id"] in missing else "retained"].append(r)
            dates[r["last_scraped"]] += 1
    results = []
    for group, records in groups.items():
        n = len(records)
        reviews = [number(r.get("number_of_reviews_ltm")) or 0 for r in records]
        ratings = [v for r in records if (v := number(r.get("review_scores_rating"))) is not None]
        sources = Counter(r.get("source", "unknown") for r in records)
        results.append(dict(market=item["market"], baseline_vintage=item["snapshot_start"], group=group, listings=n,
            zero_reviews_ltm=sum(v == 0 for v in reviews), median_reviews_ltm=median(reviews),
            reviews_ltm=sum(reviews), rated_listings=len(ratings), median_rating=median(ratings) if ratings else None,
            source_counts=json.dumps(dict(sources), sort_keys=True), raw_sha256=item["sha256"]))
    return results, dates


def winter_diagnostics(items):
    rows, profiles, sources = [], [], []
    for market in SPIKE_MARKETS:
        by_month = {}
        for (m, start), item in sorted(items.items()):
            if m == market and start >= "2025-12-01":
                by_month[start[:7]] = item
        a, b = by_month["2025-12"], by_month["2026-01"]
        baseline = load_compact(a, detailed=True)
        missing = set(baseline)-load_compact(b)
        # Same-market reappearances are independently sufficient positive evidence;
        # reported return counts are a lower bound across all geographies.
        returned = set()
        for month, item in sorted(by_month.items()):
            if month <= "2026-01":
                continue
            current = load_compact(item)
            newly_returned = (missing & current)-returned
            returned.update(missing & current)
            for cohort in ("all_listings", "reviewed_str_homes"):
                members = cohort_ids(baseline, cohort)
                lost = members & missing
                rows.append(dict(market=market, cohort=cohort, baseline_vintage=a["snapshot_start"],
                    first_missing_vintage=b["snapshot_start"], first_missing_complete=b["snapshot_complete"],
                    followup_vintage=item["snapshot_start"], followup_complete=item["snapshot_complete"],
                    negative_excluded=item["negative_excluded"], baseline_ids=len(members), january_missing=len(lost),
                    cumulative_reobserved=len(lost & returned), newly_reobserved=len(lost & newly_returned),
                    return_share=len(lost & returned)/len(lost) if lost else None,
                    never_reobserved_yet=len(lost-returned)))
        profile, dates = raw_profile(a, missing)
        profiles.extend(profile)
        with gzip.open(ROOT / b["local_path"], "rt", encoding="utf-8", newline="") as h:
            end_sources = Counter(r.get("source", "unknown") for r in csv.DictReader(h))
        with (ROOT / b["local_path"]).open("rb") as h:
            if hashlib.file_digest(h, "sha256").hexdigest() != b["sha256"]:
                raise ValueError("Winter endpoint raw changed")
        sources.append(dict(market=market, baseline_sha256=a["sha256"], baseline_url=a["url"],
            baseline_scrape_date_counts=dict(dates), first_missing_sha256=b["sha256"], first_missing_url=b["url"],
            first_missing_source_counts=dict(end_sources),
            followups=[dict(vintage=r["snapshot_start"], sha256=r["sha256"], url=r["url"]) for month,r in sorted(by_month.items()) if month > "2026-01"]))
    write_csv(OUT / "winter_reappearances.csv", rows)
    write_csv(OUT / "winter_baseline_profiles.csv", profiles)
    (OUT / "winter_sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    return rows


def figure(summaries, winter):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for cohort, label, color in (("all_listings", "All listing IDs", "#375f8c"), ("reviewed_str_homes", "Reviewed short-stay homes", "#b36728")):
        values = [100*r["disappearance_rate"] for r in summaries if r["cohort"] == cohort]
        offset = -.18 if cohort == "all_listings" else .18
        positions = [offset, 1+offset]
        axes[0].bar(positions, values, width=.32, label=label, color=color)
        for x,y in enumerate(values):
            axes[0].annotate(f"{y:.2f}%", (positions[x],y), xytext=(0,7), textcoords="offset points", ha="center", color=color)
    intervals = [r for r in summaries if r["cohort"] == "all_listings"]
    labels = [f"{r['start_month']} → {r['end_month']}\n{r['min_vintage_gap_days']}–{r['max_vintage_gap_days']} days between vintages" for r in intervals]
    axes[0].set(xticks=[0,1], xticklabels=labels, ylabel="Missing at next snapshot (%)", title="Latest: same 13 team markets", ylim=(0, max(r["disappearance_rate"] for r in summaries)*140))
    axes[0].legend(loc="lower left", fontsize=9)
    for market in SPIKE_MARKETS:
        group = [r for r in winter if r["market"] == market and r["cohort"] == "all_listings"]
        axes[1].plot([r["followup_vintage"][5:7] for r in group], [100*r["return_share"] for r in group], "o-", label=market.replace("-", " ").title())
    axes[1].set(ylabel="January-missing IDs reobserved (%)", xlabel="Follow-up snapshot month, 2026", title="Winter spike: same IDs returning", ylim=(0,105))
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.grid(axis="y", alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Recent Airbnb disappearance and evidence of temporary absence", fontsize=15)
    fig.text(.04,.02,"Source: hash-checked Inside Airbnb / team captures. Unequal collection intervals; no annualization. Disappearance is not fee-attributable exit.",fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.93))
    fig.savefig(ROOT / "analysis/figures/fee_churn_recent.png", dpi=180)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = cached_inventory()
    recent = latest_panel(items)
    print(json.dumps(recent, indent=2), flush=True)
    winter = winter_diagnostics(items)
    figure(recent, winter)
    print("Latest panel and winter diagnostics written.", flush=True)


if __name__ == "__main__":
    main()
