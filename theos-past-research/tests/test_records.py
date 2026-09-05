from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from abnb_guidance.records import DriverObservation, GuidanceEvent, GuidanceItem


def valid_event(**overrides):
    values = {
        "guidance_event_id": "ABNB_2024Q3_RESULTS_2024-11-07",
        "issuer_id": "ABNB",
        "reported_period": "2024Q3",
        "event_type": "initial",
        "published_at_utc": datetime(2024, 11, 7, 21, 5, tzinfo=UTC),
        "published_at_precision": "minute",
        "release_timing": "after_close",
        "research_cutoff_at_utc": datetime(2026, 9, 3, 3, 59, 59, tzinfo=UTC),
        "is_initial_guide": True,
    }
    values.update(overrides)
    return values


def valid_guidance_item(**overrides):
    values = {
        "guidance_item_id": "ABNB_2024Q3_RESULTS_2024-11-07_REVENUE_2024Q4",
        "guidance_event_id": "ABNB_2024Q3_RESULTS_2024-11-07",
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
        "source_excerpt_id": "EX_2024Q3_OUTLOOK_REVENUE",
        "extraction_confidence": "high",
    }
    values.update(overrides)
    return values


def valid_driver(**overrides):
    values = {
        "driver_observation_id": "ABNB_2024Q3_TAKE_RATE",
        "guidance_event_id": "ABNB_2024Q3_RESULTS_2024-11-07",
        "driver_family": "booking_economics",
        "driver_code": "take_rate",
        "value_numeric": 0.154,
        "unit": "ratio",
        "period_start": "2024-07-01",
        "period_end": "2024-09-30",
        "scope_code": "global",
        "availability_class": "contemporaneous_management_known",
        "is_derived": False,
        "quality_grade": "A",
        "leakage_risk": "low",
    }
    values.update(overrides)
    return values


def test_guidance_range_rejects_reversed_bounds():
    with pytest.raises(ValidationError, match="value_low cannot exceed value_high"):
        GuidanceItem.model_validate(valid_guidance_item(value_low=2450.0))


def test_derived_driver_requires_formula():
    with pytest.raises(ValidationError, match="derivation_formula"):
        DriverObservation.model_validate(valid_driver(is_derived=True))


def test_missing_value_requires_reason():
    with pytest.raises(ValidationError, match="missing_reason"):
        GuidanceItem.model_validate(valid_guidance_item(value_status="missing"))


def test_invalid_fiscal_period_is_rejected():
    with pytest.raises(ValidationError):
        GuidanceEvent.model_validate(valid_event(reported_period="2024-Q3"))


def test_timestamp_must_be_timezone_aware():
    with pytest.raises(ValidationError, match="timezone-aware"):
        GuidanceEvent.model_validate(
            valid_event(published_at_utc=datetime(2024, 11, 7, 21, 5))
        )


def test_valid_guidance_midpoint_is_accepted():
    item = GuidanceItem.model_validate(valid_guidance_item())

    assert item.value_mid == 2415.0
    assert item.value_status.value == "observed"
