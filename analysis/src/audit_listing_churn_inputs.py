"""Audit existing aggregate retention data; this does not estimate property churn.

Reads pinned Git blobs without checking out or merging another contributor's branch.
Standard library only. All rates are fractions and retain their actual date interval.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess


PAIR_PATH = "data/processed/inside_airbnb_like_for_like.csv"
SNAPSHOT_PATH = "data/processed/inside_airbnb_city_snapshots.csv"


def boolean(value: str) -> bool:
    if value not in ("True", "False"):
        raise ValueError(f"Expected True/False scope flag, received {value!r}")
    return value == "True"


def nonnegative_integer(value: str) -> int:
    result = int(value)
    if result < 0:
        raise ValueError("Counts cannot be negative")
    return result


def reconciles(value: str, expected: float) -> bool:
    number = float(value)
    return math.isfinite(number) and abs(number - expected) <= 0.000051


def audit(snapshots: list[dict], pairs: list[dict]) -> tuple[list[dict], dict]:
    if not snapshots or not pairs:
        raise ValueError("Both snapshot and pair tables must be nonempty")
    snapshot_index = {}
    for row in snapshots:
        key = row["city"], date.fromisoformat(row["dump_date"])
        if key in snapshot_index:
            raise ValueError(f"Duplicate snapshot: {key}")
        snapshot_index[key] = (
            nonnegative_integer(row["listings"]), boolean(row["partial_scope"])
        )

    seen = set()
    validated = []
    for row in pairs:
        start, end = date.fromisoformat(row["date_a"]), date.fromisoformat(row["date_b"])
        days = (end - start).days
        key = row["city"], row["pair_type"], start, end
        if key in seen:
            raise ValueError(f"Duplicate pair: {key}")
        seen.add(key)
        if days <= 0 or days != int(row["days_apart"]):
            raise ValueError(f"Invalid interval: {key}")
        a, b, matched, exits, adds = (
            nonnegative_integer(row[name])
            for name in ("ids_a", "ids_b", "matched", "exits", "gross_adds")
        )
        if matched > min(a, b) or a - matched != exits or b - matched != adds:
            raise ValueError(f"Stock-flow identity fails: {key}")
        # The source stores fractions rounded to four decimal places.
        if a and not reconciles(row["retention"], matched / a):
            raise ValueError(f"Retention does not reconcile to counts: {key}")
        if b and not reconciles(row["new_share_b"], adds / b):
            raise ValueError(f"New share does not reconcile to counts: {key}")
        snap_a = snapshot_index[(row["city"], start)]
        snap_b = snapshot_index[(row["city"], end)]
        if (a, b) != (snap_a[0], snap_b[0]):
            raise ValueError(f"Pair and snapshot counts disagree: {key}")
        if not a:
            screen = "undefined_zero_baseline"
        elif snap_a[1] or snap_b[1]:
            screen = "reject_flagged_scope"
        else:
            screen = "review_required_no_endpoint_flag"
        validated.append({
            "market": row["city"], "pair_type": row["pair_type"],
            "date_a": start.isoformat(), "date_b": end.isoformat(), "days_apart": days,
            "baseline_listing_ids": a, "endpoint_listing_ids": b,
            "matched_listing_ids": matched, "missing_listing_ids": exits,
            "new_to_pair_listing_ids": adds,
            "interval_id_absence_rate": exits / a if a else None,
            "new_share_of_endpoint": adds / b if b else None,
            "net_listing_change_rate": (b - a) / a if a else None,
            "source_partial_scope_a": snap_a[1], "source_partial_scope_b": snap_b[1],
            "coverage_screen": screen,
            "property_churn_rate": None, "sale_share": None, "other_platform_share": None,
            "interpretation": "ID absence only; property identity and destination unobserved",
        })

    # Use the latest source-designated year-ago pair, not the most convenient rate.
    # Source pairs span unequal intervals and were selected partly for price comparability.
    latest = {}
    for row in validated:
        if row["pair_type"] != "year_ago":
            continue
        previous = latest.get(row["market"])
        if previous and row["date_b"] == previous["date_b"]:
            raise ValueError(f"Ambiguous latest year-ago pair for {row['market']}")
        if previous is None or row["date_b"] > previous["date_b"]:
            latest[row["market"]] = row
    if not latest:
        raise ValueError("No year-ago pairs to audit")
    rows = [latest[key] for key in sorted(latest)]
    summary = {
        "snapshot_rows": len(snapshots),
        "snapshot_markets": len({row["city"] for row in snapshots}),
        "source_flagged_partial_snapshots": sum(flag for _, flag in snapshot_index.values()),
        "validated_pair_rows": len(validated),
        "year_ago_pair_rows": sum(row["pair_type"] == "year_ago" for row in validated),
        "latest_year_ago_pairs": len(rows),
        "latest_pairs_with_endpoint_scope_flag": sum(
            row["source_partial_scope_a"] or row["source_partial_scope_b"] for row in rows
        ),
        "interval_days_min": min(row["days_apart"] for row in rows),
        "interval_days_max": max(row["days_apart"] for row in rows),
        "measured_property_churn_rate": None,
        "destination_classification": "not_identifiable_from_aggregate_inputs",
        "limitations": [
            "No raw listing IDs or property crosswalk in these aggregate inputs.",
            "No endpoint scope flag is not proof of complete or comparable coverage.",
            "Source scope heuristic uses future snapshots; it is retrospective, not point-in-time.",
            "Year-ago pairs are not exactly annual; no annualization or global pooling is performed.",
            "New to this pair does not establish a property's first-ever Airbnb entry.",
            "Rates use all observed IDs, not a verified economically active property denominator.",
        ],
    }
    return rows, summary


def git_bytes(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, timeout=60
    ).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rev", required=True, help="Commit or branch containing both input tables")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    revision = git_bytes(root, "rev-parse", "--verify", f"{args.source_rev}^{{commit}}").decode().strip()
    tables, provenance = {}, []
    for path in (PAIR_PATH, SNAPSHOT_PATH):
        raw = git_bytes(root, "show", f"{revision}:{path}")
        tables[path] = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        provenance.append({"commit": revision, "path": path, "sha256": hashlib.sha256(raw).hexdigest()})
    rows, summary = audit(tables[SNAPSHOT_PATH], tables[PAIR_PATH])
    summary["inputs"] = provenance
    summary["method"] = "latest_source_year_ago_pair_per_city_with_endpoint_scope_screen"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "listing_churn_existing_data_audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_commit", *rows[0]])
        writer.writeheader()
        writer.writerows({"source_commit": revision, **row} for row in rows)
    (args.output_dir / "listing_churn_existing_data_audit.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
