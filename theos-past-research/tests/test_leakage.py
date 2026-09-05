from decimal import Decimal

import pytest

from abnb_alt_data.leakage import (
    assert_feature_available_before_cutoff,
    eligible_features,
    guidance_midpoint,
    parse_utc,
    validate_guidance_row,
)


CUTOFF = "2026-08-06T20:00:00Z"
MARKDOWN = "data/licensed/earnings_transcripts/clean_md/ABNB-2026Q2.md"


def valid_guidance() -> dict[str, str]:
    return {
        "guidance_id": "G-2026Q2-REVENUE",
        "issuing_fiscal_period": "2026Q2",
        "call_event_at": CUTOFF,
        "available_at": CUTOFF,
        "guided_period": "2026Q3",
        "metric": "revenue",
        "guidance_type": "range",
        "value_low": "140",
        "value_high": "160",
        "value_midpoint": "150",
        "qualitative_direction": "",
        "unit": "USD millions",
        "currency": "USD",
        "constant_currency_basis": "reported",
        "source_markdown": MARKDOWN,
        "source_turn_id": "ABNB-2026Q2-MD-004",
        "indiscernible_affects_record": "false",
        "extraction_status": "verified",
        "confidence": "high",
        "analyst_notes": "",
    }


def verified_index() -> dict[str, dict[str, str]]:
    return {
        MARKDOWN: {
            "availability_status": "verified",
            "event_at": CUTOFF,
            "point_in_time_usable_after": CUTOFF,
        }
    }


def valid_turns() -> dict[str, set[str]]:
    return {MARKDOWN: {"ABNB-2026Q2-MD-004"}}


def test_feature_one_second_before_cutoff_is_allowed() -> None:
    assert_feature_available_before_cutoff("2026-08-06T19:59:59Z", CUTOFF)


@pytest.mark.parametrize(
    "available_at",
    [CUTOFF, "2026-08-06T20:00:01Z"],
)
def test_feature_at_or_after_cutoff_is_rejected(available_at: str) -> None:
    with pytest.raises(ValueError, match="strictly before"):
        assert_feature_available_before_cutoff(available_at, CUTOFF)


@pytest.mark.parametrize(
    ("feature_at", "cutoff"),
    [(None, CUTOFF), ("", CUTOFF), ("2026-08-06T19:59:59Z", None)],
)
def test_missing_timestamp_is_rejected(
    feature_at: str | None, cutoff: str | None
) -> None:
    with pytest.raises(ValueError, match="missing"):
        assert_feature_available_before_cutoff(feature_at, cutoff)


def test_timezone_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone"):
        parse_utc("2026-08-06T19:59:59", "available_at")


def test_eligible_features_filters_later_verified_releases() -> None:
    rows = [
        {"id": "early", "available_at": "2026-08-06T19:59:59Z", "availability_status": "verified"},
        {"id": "equal", "available_at": CUTOFF, "availability_status": "verified"},
        {"id": "late", "available_at": "2026-08-06T20:00:01Z", "availability_status": "verified"},
    ]

    assert [row["id"] for row in eligible_features(rows, CUTOFF)] == ["early"]


def test_eligible_features_rejects_unverified_release_time() -> None:
    rows = [
        {"id": "unknown", "available_at": "2026-08-06T19:00:00Z", "availability_status": "unverified"}
    ]

    with pytest.raises(ValueError, match="unverified"):
        eligible_features(rows, CUTOFF)


def test_guidance_midpoint_uses_exact_decimal_arithmetic() -> None:
    assert guidance_midpoint("140", "160") == Decimal("150")


def test_valid_numeric_range_passes() -> None:
    validate_guidance_row(valid_guidance(), verified_index(), valid_turns())


def test_wrong_numeric_midpoint_is_rejected() -> None:
    row = valid_guidance()
    row["value_midpoint"] = "151"

    with pytest.raises(ValueError, match="midpoint"):
        validate_guidance_row(row, verified_index(), valid_turns())


def test_qualitative_guidance_cannot_contain_numeric_values() -> None:
    row = valid_guidance()
    row.update(
        guidance_type="qualitative",
        qualitative_direction="decelerating",
        value_high="",
        value_midpoint="",
    )

    with pytest.raises(ValueError, match="qualitative.*numeric"):
        validate_guidance_row(row, verified_index(), valid_turns())


def test_guidance_requires_indexed_markdown_and_turn() -> None:
    with pytest.raises(ValueError, match="Markdown"):
        validate_guidance_row(valid_guidance(), {}, valid_turns())

    with pytest.raises(ValueError, match="turn"):
        validate_guidance_row(valid_guidance(), verified_index(), {MARKDOWN: set()})


def test_unverified_transcript_cannot_anchor_cutoff() -> None:
    index = verified_index()
    index[MARKDOWN]["availability_status"] = "unverified"

    with pytest.raises(ValueError, match="unverified"):
        validate_guidance_row(valid_guidance(), index, valid_turns())


def test_indiscernible_record_cannot_have_high_confidence() -> None:
    row = valid_guidance()
    row["indiscernible_affects_record"] = "true"

    with pytest.raises(ValueError, match="indiscernible.*high confidence"):
        validate_guidance_row(row, verified_index(), valid_turns())
