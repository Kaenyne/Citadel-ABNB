#!/usr/bin/env python3
"""Independent integrity verification for the consolidated 50-source panel."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
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
    manifest = read_csv(ROOT / "source_manifest_50.csv")
    summary = read_csv(ROOT / "source_summary_50.csv")
    raw_manifest = read_csv(PROCESSED / "raw_file_manifest.csv")
    declared_validation = json.loads(
        (PROCESSED / "validation_50.json").read_text(encoding="utf-8")
    )

    observation_ids: set[str] = set()
    source_counts: Counter[str] = Counter()
    duplicate_observations = 0
    invalid_numeric_values = 0
    missing_identity_fields = 0
    observation_count = 0
    with (PROCESSED / "new_observations.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            observation_count += 1
            source_counts[row["source_id"]] += 1
            observation_id = row["observation_id"]
            if observation_id in observation_ids:
                duplicate_observations += 1
            observation_ids.add(observation_id)
            try:
                if not math.isfinite(float(row["value"])):
                    invalid_numeric_values += 1
            except (TypeError, ValueError):
                invalid_numeric_values += 1
            if not all(
                row[field]
                for field in (
                    "observation_id",
                    "source_id",
                    "dataset_code",
                    "reference_period",
                    "metric",
                    "first_available_at_utc",
                    "raw_file",
                )
            ):
                missing_identity_fields += 1

    raw_failures: list[str] = []
    for row in raw_manifest:
        path = ROOT / "raw" / row["file"]
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256(path) != row["sha256"]
        ):
            raw_failures.append(row["file"])

    manifest_ids = [row["source_id"] for row in manifest]
    summary_ids = [row["source_id"] for row in summary]
    new_manifest_ids = {
        row["source_id"] for row in read_csv(PROCESSED / "new_source_manifest.csv")
    }
    checks = {
        "exactly_50_manifest_sources": len(manifest) == 50,
        "exactly_50_summary_sources": len(summary) == 50,
        "manifest_source_ids_unique": len(manifest_ids) == len(set(manifest_ids)),
        "summary_source_ids_unique": len(summary_ids) == len(set(summary_ids)),
        "manifest_and_summary_sources_match": set(manifest_ids) == set(summary_ids),
        "exactly_41_new_sources": len(new_manifest_ids) == 41,
        "all_41_new_sources_nonempty": set(source_counts) == new_manifest_ids,
        "observation_count_matches_declared": (
            observation_count == declared_validation["new_valid_observations"]
        ),
        "new_observation_ids_unique": duplicate_observations == 0,
        "all_values_numeric_and_finite": invalid_numeric_values == 0,
        "all_required_identity_fields_present": missing_identity_fields == 0,
        "all_41_raw_files_match_bytes_and_sha256": (
            len(raw_manifest) == 41 and not raw_failures
        ),
        "all_50_sources_free": all(row["cost"] == "free" for row in manifest),
        "no_personal_data_retained": all(
            row["personal_data_retained"].lower() == "false" for row in manifest
        ),
        "declared_50_source_gate_passed": declared_validation["passed_50_source_gate"] is True,
    }
    report = {
        "passed": all(checks.values()),
        "checks": checks,
        "consolidated_sources": len(manifest),
        "new_sources": len(new_manifest_ids),
        "new_valid_observations": observation_count,
        "total_referenced_observations": declared_validation["total_referenced_observations"],
        "verified_raw_files": len(raw_manifest) - len(raw_failures),
        "raw_integrity_failures": raw_failures,
        "provider_warning": "The 41 additions are distinct datasets from one provider, Eurostat; they are not independent source families.",
        "research_warning": "Current snapshots are prospective-only and do not establish historical forecasting edge.",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
