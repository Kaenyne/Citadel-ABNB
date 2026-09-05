#!/usr/bin/env python3
"""Independent integrity checks for the broad ABNB edge-data acquisition run."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / "processed"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    valid = read_csv(PROCESSED / "valid_observations.csv")
    rejected = read_csv(PROCESSED / "rejected_observations.csv")
    source_manifest = read_csv(ROOT / "source_manifest.csv")
    raw_manifest = read_csv(PROCESSED / "raw_file_manifest.csv")
    validation = json.loads((PROCESSED / "validation.json").read_text(encoding="utf-8"))

    source_ids = {row["source_id"] for row in valid}
    declared_source_ids = {row["source_id"] for row in source_manifest}
    observation_ids = [row["observation_id"] for row in valid]

    raw_integrity = []
    for row in raw_manifest:
        path = ROOT / "raw" / row["file"]
        raw_integrity.append(
            path.is_file()
            and path.stat().st_size == int(row["bytes"])
            and sha256(path) == row["sha256"]
        )

    finite_values = all(math.isfinite(float(row["value"])) for row in valid)
    required_identity = all(
        row["observation_id"]
        and row["source_id"]
        and row["reference_period"]
        and row["metric"]
        and row["first_available_at_utc"]
        for row in valid
    )

    checks = {
        "minimum_100_valid_observations": len(valid) >= 100,
        "validation_count_matches_csv": validation["valid_observations"] == len(valid),
        "rejection_count_matches_csv": validation["rejected_observations"] == len(rejected),
        "observation_ids_unique": len(observation_ids) == len(set(observation_ids)),
        "manifest_sources_equal_observed_sources": declared_source_ids == source_ids,
        "all_declared_sources_nonempty": all(
            any(row["source_id"] == source_id for row in valid)
            for source_id in declared_source_ids
        ),
        "all_values_numeric_and_finite": finite_values,
        "required_identity_fields_present": required_identity,
        "all_raw_files_match_bytes_and_sha256": len(raw_integrity) == 13 and all(raw_integrity),
        "all_sources_are_free": all(row["cost"] == "free" for row in source_manifest),
        "no_personal_data_retained": all(
            row["personal_data_retained"] == "false" for row in source_manifest
        ),
    }

    report = {
        "passed": all(checks.values()),
        "checks": checks,
        "valid_observations": len(valid),
        "rejected_observations": len(rejected),
        "distinct_sources": len(source_ids),
        "distinct_providers": len({row["provider"] for row in valid}),
        "raw_files_verified": sum(raw_integrity),
        "research_warning": (
            "Rows are correlated panel observations, not independent samples; current-snapshot "
            "history is prospective-only until immutable release vintages are archived."
        ),
    }
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
