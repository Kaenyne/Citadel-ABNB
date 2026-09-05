from datetime import UTC, datetime

from abnb_guidance.extraction import excerpt_compliance_findings
from abnb_guidance.management_evidence import (
    build_management_evidence,
    build_other_guidance_items,
    build_transcript_evidence,
)
from abnb_guidance.official_history import build_official_history
from abnb_guidance.transcripts import build_transcript_manifest


def test_evidence_ledger_covers_requested_driver_families_and_negative_evidence():
    official = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC)
    )
    evidence = build_management_evidence(
        events=official["guidance_events"],
        official_documents=official["source_documents"],
    )
    codes = {row.driver_code for row in evidence["evidence_claims"]}

    assert {
        "nights_booked_yoy",
        "gbv_yoy",
        "adr_yoy",
        "take_rate",
        "regional_mix",
        "cross_border_growth",
        "booking_lead_time",
        "cancellation_rate",
        "active_listings_yoy",
        "marketing_expense",
        "fx_revenue_impact",
        "target_quarter",
        "easter_shift",
        "regulatory_pressure",
        "consumer_confidence_change",
    }.issubset(codes)
    assert any(row.evidence_stance == "contradictory" for row in evidence["evidence_claims"])
    assert any(row.evidence_stance == "negative_evidence" for row in evidence["evidence_claims"])


def test_management_observations_are_available_no_later_than_the_event():
    official = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC)
    )
    event_times = {row.guidance_event_id: row.published_at_utc for row in official["guidance_events"]}
    evidence = build_management_evidence(
        events=official["guidance_events"],
        official_documents=official["source_documents"],
    )

    assert all(
        row.known_to_management_by_utc <= event_times[row.guidance_event_id]
        for row in evidence["driver_observations"]
    )
    assert all(row.leakage_risk == "low" for row in evidence["driver_observations"])


def test_non_revenue_guidance_is_stored_separately_from_driver_observations():
    official = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC)
    )
    evidence = build_management_evidence(
        events=official["guidance_events"],
        official_documents=official["source_documents"],
    )

    guidance = build_other_guidance_items(
        events=official["guidance_events"],
        revenue_guidance=official["guidance_items"],
        driver_observations=evidence["driver_observations"],
    )

    assert {row.metric_code for row in guidance}.issuperset(
        {"nights_booked_yoy", "gbv_yoy", "adr_yoy", "take_rate"}
    )
    assert all(row.metric_code != "revenue" for row in guidance)
    assert all(row.measure_type == "qualitative_direction" for row in guidance)


def test_management_excerpts_respect_short_excerpt_policy():
    official = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC)
    )
    evidence = build_management_evidence(
        events=official["guidance_events"],
        official_documents=official["source_documents"],
    )

    assert all(row.excerpt_word_count <= 25 for row in evidence["source_excerpts"])
    assert excerpt_compliance_findings(
        evidence["source_excerpts"], official["source_documents"]
    ) == []


def test_transcript_evidence_is_minimal_and_includes_mixed_cancellation_evidence(tmp_path):
    filenames = {
        "2025Q3": "q3.pdf",
        "2026Q1": "q1.pdf",
    }
    for filename in filenames.values():
        (tmp_path / filename).write_bytes(b"fixture")
    documents = build_transcript_manifest(
        tmp_path,
        filenames,
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC),
    )
    official = build_official_history(
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC)
    )

    evidence = build_transcript_evidence(
        events=official["guidance_events"], transcript_documents=documents
    )

    assert len(evidence["source_excerpts"]) == 2
    assert all(row.excerpt_word_count <= 25 for row in evidence["source_excerpts"])
    assert any(
        row.driver_code == "cancellation_rate" and row.evidence_stance == "mixed"
        for row in evidence["evidence_claims"]
    )
    assert excerpt_compliance_findings(
        evidence["source_excerpts"], documents
    ) == []
