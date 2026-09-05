from pathlib import Path

import pytest

from abnb_alt_data.schemas import CSV_SCHEMAS, validate_csv_header, write_empty_csv


ROOT = Path(__file__).resolve().parents[1]


def test_declared_schema_fields_are_unique() -> None:
    for fields in CSV_SCHEMAS.values():
        assert len(fields) == len(set(fields))


def test_collection_governance_registries_are_declared() -> None:
    expected = {
        "research/free_api_registry.csv",
        "research/scraping_audit.csv",
    }

    assert expected.issubset(CSV_SCHEMAS)


def test_collection_governance_registries_capture_decision_inputs() -> None:
    api_fields = set(CSV_SCHEMAS["research/free_api_registry.csv"])
    scraping_fields = set(CSV_SCHEMAS["research/scraping_audit.csv"])

    assert {
        "api_id",
        "research_use",
        "docs_url",
        "signup_url",
        "authentication",
        "env_var_names",
        "free_tier",
        "rate_limit",
        "vintage_support",
        "terms_url",
        "last_reviewed_at_utc",
    }.issubset(api_fields)
    assert {
        "audit_id",
        "source_id",
        "domain",
        "intended_paths",
        "terms_url",
        "robots_url",
        "reviewed_at_utc",
        "terms_status",
        "robots_status",
        "airbnb_controlled",
        "explicit_automation_permission",
        "rate_limit_per_minute",
        "cache_policy",
        "user_agent",
        "collection_allowed",
        "decision_reason",
        "collected_at_utc",
        "sha256",
    }.issubset(scraping_fields)


def test_tracked_csv_headers_match_schema() -> None:
    for relative_path, fields in CSV_SCHEMAS.items():
        validate_csv_header(ROOT / relative_path, fields)


def test_header_validation_reports_expected_and_actual(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("wrong,header\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected.*actual"):
        validate_csv_header(path, ("right", "header"))


def test_write_empty_csv_does_not_overwrite_existing_rows(tmp_path: Path) -> None:
    path = tmp_path / "facts.csv"
    path.write_text("id,value\n1,2\n", encoding="utf-8")

    write_empty_csv(path, ("id", "value"))

    assert path.read_text(encoding="utf-8") == "id,value\n1,2\n"
