from pathlib import Path

import pytest

from abnb_forecasting.contracts import validate_record, validate_run


ROOT = Path(__file__).resolve().parents[1]


def valid_run(**changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "forecast_id": "ABNB-2026Q3-20260903T120000Z",
        "forecast_version": 1,
        "ticker": "ABNB",
        "issuing_fiscal_period": "2026Q3",
        "target_event": "Q3 2026 earnings",
        "target_event_at_utc": "",
        "as_of_utc": "2026-09-03T12:00:00Z",
        "generated_at_utc": "2026-09-03T12:01:00Z",
        "run_mode": "FORECAST",
        "status": "workflow_rehearsal",
        "agent_model": "gpt-5.6-sol",
        "reasoning_effort": "xhigh",
        "prompt_version": "1",
        "code_revision": "test",
        "input_manifest_ids": [],
        "parent_forecast_id": "",
        "analyst_owner": "test",
        "notes": "synthetic",
    }
    row.update(changes)
    return row


def test_forecast_run_requires_an_offset_aware_cutoff() -> None:
    row = valid_run(as_of_utc="2026-09-03T12:00:00")

    with pytest.raises(ValueError, match="timezone"):
        validate_run(row)


def test_update_requires_a_parent_forecast() -> None:
    row = valid_run(run_mode="UPDATE", forecast_version=2)

    with pytest.raises(ValueError, match="parent_forecast_id"):
        validate_run(row)


def test_manifest_validation_reports_missing_review_status() -> None:
    with pytest.raises(ValueError, match="review_status"):
        validate_record("EvidenceManifest", {"manifest_id": "M-1"})


def test_target_registry_has_the_canonical_header() -> None:
    header = (ROOT / "research/forecasting/target_registry.csv").read_text(
        encoding="utf-8"
    ).splitlines()[0]

    assert header == (
        "target_id,model_stage,metric,target_definition,target_version,"
        "issuing_fiscal_period,reference_period,guidance_type,unit,currency,"
        "constant_currency_basis,available_at_utc,source_evidence_id,"
        "comparability_status,notes"
    )
