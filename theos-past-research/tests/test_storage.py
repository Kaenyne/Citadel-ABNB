from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from abnb_guidance.storage import (
    create_templates,
    export_json_schemas,
    load_table,
    validate_dataset,
    write_table,
)


def event_row(event_id: str = "E1") -> dict:
    return {
        "guidance_event_id": event_id,
        "issuer_id": "ABNB",
        "reported_period": "2024Q3",
        "event_type": "initial",
        "published_at_utc": datetime(2024, 11, 7, 21, 5, tzinfo=UTC),
        "published_at_precision": "minute",
        "release_timing": "after_close",
        "research_cutoff_at_utc": datetime(2026, 9, 3, 3, 59, 59, tzinfo=UTC),
        "is_initial_guide": True,
    }


def guidance_row(event_id: str = "E1") -> dict:
    return {
        "guidance_item_id": "G1",
        "guidance_event_id": event_id,
        "target_period": "2024Q4",
        "metric_code": "revenue",
        "measure_type": "absolute",
        "value_low": 2390.0,
        "value_high": 2440.0,
        "value_mid": 2415.0,
        "unit": "USD_millions",
        "currency": "USD",
        "accounting_basis": "GAAP",
        "is_company_stated": True,
        "extraction_confidence": "high",
        "value_status": "observed",
    }


def test_duplicate_primary_key_is_reported(tmp_path: Path):
    write_table("guidance_events", pd.DataFrame([event_row(), event_row()]), tmp_path)

    findings = validate_dataset(tmp_path)

    assert any(f.code == "duplicate_primary_key" for f in findings)


def test_missing_foreign_key_is_reported(tmp_path: Path):
    write_table("guidance_items", pd.DataFrame([guidance_row("MISSING")]), tmp_path)

    findings = validate_dataset(tmp_path)

    assert any(f.code == "missing_foreign_key" for f in findings)


def test_missing_excerpt_reference_on_guidance_is_reported(tmp_path: Path):
    row = guidance_row()
    row["source_excerpt_id"] = "MISSING-EXCERPT"
    write_table("guidance_events", pd.DataFrame([event_row()]), tmp_path)
    write_table("guidance_items", pd.DataFrame([row]), tmp_path)

    findings = validate_dataset(tmp_path)

    assert any(
        f.code == "missing_foreign_key" and f.table == "guidance_items"
        for f in findings
    )


def test_csv_and_parquet_round_trip_preserves_key(tmp_path: Path):
    write_table("guidance_events", pd.DataFrame([event_row()]), tmp_path)

    loaded = load_table("guidance_events", tmp_path)

    assert loaded.loc[0, "guidance_event_id"] == "E1"
    assert (tmp_path / "data/normalized/guidance_events.parquet").exists()


def test_template_and_json_schema_generation(tmp_path: Path):
    create_templates(tmp_path)
    export_json_schemas(tmp_path / "schemas/generated")

    assert (tmp_path / "data/manifests/source_documents.csv").exists()
    assert (tmp_path / "data/normalized/guidance_events.csv").exists()
    assert (tmp_path / "schemas/generated/guidance_events.schema.json").exists()
