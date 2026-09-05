"""Canonical schemas for tracked ABNB alternative-data research tables."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Sequence


SOURCE_REGISTRY_FIELDS = (
    "rank",
    "source_id",
    "dataset",
    "provider",
    "economic_mechanism",
    "source_url",
    "access_method",
    "license",
    "collection_restrictions",
    "geographic_coverage",
    "unit_of_observation",
    "frequency",
    "history_start",
    "history_end",
    "publication_schedule",
    "publication_lag",
    "revision_policy",
    "vintage_available",
    "cost",
    "collection_timestamp_utc",
    "pit_evidence",
    "leakage_risk",
    "leakage_mitigation",
    "status",
    "citations",
    "analyst_notes",
)

HYPOTHESIS_FIELDS = (
    "hypothesis_id",
    "version",
    "registered_at_utc",
    "target",
    "prediction_horizon",
    "signal",
    "transformation",
    "expected_direction",
    "economic_mechanism",
    "geographic_aggregation",
    "cutoff_rule",
    "availability_rule",
    "baseline",
    "evaluation_metric",
    "minimum_evidence",
    "confounders",
    "failure_conditions",
    "result_status",
    "result_path",
)

FREE_API_FIELDS = (
    "rank",
    "api_id",
    "provider",
    "api_name",
    "research_use",
    "economic_mechanism",
    "docs_url",
    "signup_url",
    "base_url",
    "authentication",
    "env_var_names",
    "free_tier",
    "rate_limit",
    "history_start",
    "history_end",
    "frequency",
    "geographic_coverage",
    "publication_lag",
    "revision_policy",
    "vintage_support",
    "license",
    "collection_restrictions",
    "cost",
    "terms_url",
    "last_reviewed_at_utc",
    "linked_source_ids",
    "status",
    "citations",
    "analyst_notes",
)

SCRAPING_AUDIT_FIELDS = (
    "audit_id",
    "source_id",
    "domain",
    "intended_paths",
    "collection_purpose",
    "terms_url",
    "robots_url",
    "reviewed_at_utc",
    "terms_status",
    "robots_status",
    "authenticated",
    "paywalled",
    "captcha_required",
    "access_control_bypass",
    "personal_data",
    "airbnb_controlled",
    "explicit_automation_permission",
    "rate_limit_per_minute",
    "cache_policy",
    "user_agent",
    "collection_allowed",
    "decision_reason",
    "selector_or_endpoint",
    "collected_at_utc",
    "artifact_path",
    "sha256",
    "status",
    "citations",
)

TRANSCRIPT_INDEX_FIELDS = (
    "transcript_id",
    "ticker",
    "fiscal_period",
    "event_date",
    "event_at",
    "corrected_transcript_created_at",
    "pdf_creation_at",
    "published_at",
    "retrieved_at_utc",
    "indexed_at_utc",
    "point_in_time_usable_after",
    "availability_status",
    "source_provider",
    "source_filename",
    "source_sha256",
    "transcript_status",
    "license_status",
    "page_count",
    "word_count",
    "markdown_path",
)

GUIDANCE_FIELDS = (
    "guidance_id",
    "issuing_fiscal_period",
    "call_event_at",
    "available_at",
    "guided_period",
    "metric",
    "guidance_type",
    "value_low",
    "value_high",
    "value_midpoint",
    "qualitative_direction",
    "unit",
    "currency",
    "constant_currency_basis",
    "source_markdown",
    "source_turn_id",
    "indiscernible_affects_record",
    "extraction_status",
    "confidence",
    "analyst_notes",
)

REPORTED_METRIC_FIELDS = (
    "fact_id",
    "fiscal_period",
    "available_at",
    "metric",
    "reference_period",
    "value",
    "unit",
    "currency",
    "constant_currency_basis",
    "source_markdown",
    "source_turn_id",
    "confidence",
)

MANAGEMENT_THEME_FIELDS = (
    "theme_id",
    "fiscal_period",
    "available_at",
    "theme",
    "direction",
    "geography",
    "source_markdown",
    "source_turn_id",
    "confidence",
    "analyst_notes",
)

CSV_SCHEMAS: dict[str, tuple[str, ...]] = {
    "research/source_registry.csv": SOURCE_REGISTRY_FIELDS,
    "research/hypothesis_ledger.csv": HYPOTHESIS_FIELDS,
    "research/free_api_registry.csv": FREE_API_FIELDS,
    "research/scraping_audit.csv": SCRAPING_AUDIT_FIELDS,
    "research/transcripts/transcript_index.csv": TRANSCRIPT_INDEX_FIELDS,
    "research/transcripts/guidance_facts.csv": GUIDANCE_FIELDS,
    "research/transcripts/reported_metrics.csv": REPORTED_METRIC_FIELDS,
    "research/transcripts/management_themes.csv": MANAGEMENT_THEME_FIELDS,
}


def validate_csv_header(path: Path, expected: Sequence[str]) -> None:
    """Raise when *path* does not begin with exactly *expected*."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        actual = next(csv.reader(handle), [])
    expected_list = list(expected)
    if actual != expected_list:
        raise ValueError(
            f"{path}: expected header {expected_list!r}; actual header {actual!r}"
        )


def write_empty_csv(path: Path, fields: Sequence[str]) -> None:
    """Create a header-only CSV without replacing an existing valid table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size:
        validate_csv_header(path, fields)
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerow(fields)
