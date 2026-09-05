from datetime import UTC, datetime

from abnb_guidance.official_history import build_official_history


def test_history_covers_every_public_earnings_event_through_q2_2026():
    tables = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, 0, tzinfo=UTC)
    )

    assert len(tables["guidance_events"]) == 23
    assert len(tables["quarterly_actuals"]) == 23
    assert tables["guidance_events"][0].reported_period == "2020Q4"
    assert tables["guidance_events"][-1].reported_period == "2026Q2"


def test_numeric_guidance_starts_in_q3_2021_and_midpoints_are_derived():
    tables = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, 0, tzinfo=UTC)
    )
    guidance = tables["guidance_items"]
    numeric = [item for item in guidance if item.measure_type == "absolute_range"]
    qualitative = [item for item in guidance if item.measure_type == "qualitative"]

    assert len(numeric) == 20
    assert len(qualitative) == 3
    assert numeric[0].guidance_event_id == "ABNB-2021Q3-INITIAL"
    assert numeric[0].target_period == "2021Q4"
    assert numeric[0].value_low == 1390.0
    assert numeric[0].value_high == 1480.0
    assert numeric[0].value_mid == 1435.0
    assert all(item.value_mid == (item.value_low + item.value_high) / 2 for item in numeric)


def test_every_observation_has_a_pinned_official_excerpt_and_source():
    tables = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, 0, tzinfo=UTC)
    )
    document_ids = {record.document_id for record in tables["source_documents"]}
    excerpts = {record.source_excerpt_id: record for record in tables["source_excerpts"]}

    assert len(document_ids) == 23
    assert all(actual.source_excerpt_id in excerpts for actual in tables["quarterly_actuals"])
    assert all(item.source_excerpt_id in excerpts for item in tables["guidance_items"])
    assert all(excerpt.document_id in document_ids for excerpt in excerpts.values())
    assert all(excerpt.excerpt_word_count <= 25 for excerpt in excerpts.values())


def test_last_guidance_target_is_q3_2026_and_not_backfilled_with_future_actual():
    tables = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, 0, tzinfo=UTC)
    )
    last_guide = tables["guidance_items"][-1]

    assert last_guide.target_period == "2026Q3"
    assert last_guide.value_low == 4690.0
    assert last_guide.value_high == 4770.0
    assert all(actual.fiscal_period != "2026Q3" for actual in tables["quarterly_actuals"])
