from pathlib import Path

import pytest

from abnb_forecasting.packet import audit_packet, build_packet, write_packet


def rehearsal_payload() -> dict[str, object]:
    manifest = {
        "manifest_id": "M-1",
        "dataset_id": "SYNTHETIC-MACRO",
        "dataset_version": "1",
        "producer": "test-fixture",
        "reviewer": "test-reviewer",
        "review_status": "approved_for_forecasting",
        "created_at_utc": "2026-09-03T10:00:00Z",
        "coverage_start": "2026-08-01",
        "coverage_end": "2026-09-03",
        "release_lag_rule": "synthetic fixture",
        "vintage_method": "synthetic fixture",
        "schema_version": "1",
        "row_count": 2,
        "content_checksum": "synthetic-not-a-real-checksum",
        "license_class": "synthetic_test_only",
        "permitted_uses": "software tests only",
        "source_registry_ids": ["S-1"],
        "evidence_locations": ["tests/fixtures"],
        "known_limitations": "Contains no real observations.",
    }

    def feature(feature_id: str, available_at: str) -> dict[str, object]:
        return {
            "feature_id": feature_id,
            "feature_definition_version": "1",
            "manifest_id": "M-1",
            "source_id": "S-1",
            "evidence_id": f"E-{feature_id}",
            "evidence_bucket": "outside",
            "metric": "synthetic_macro_index",
            "value": "100",
            "value_type": "decimal",
            "unit": "index",
            "currency": "",
            "geography": "global",
            "reference_start": "2026-08-01",
            "reference_end": "2026-08-31",
            "observed_at_utc": "2026-08-31T23:59:59Z",
            "first_available_at_utc": available_at,
            "vintage_at_utc": available_at,
            "collected_at_utc": "2026-09-03T12:05:00Z",
            "revision_status": "never_revised",
            "availability_status": "verified",
            "review_status": "approved",
            "license_class": "synthetic_test_only",
            "transformation_id": "level",
            "missing_reason": "",
        }

    return {
        "run": {
            "forecast_id": "ABNB-MVP-REHEARSAL-v1",
            "forecast_version": 1,
            "ticker": "ABNB",
            "issuing_fiscal_period": "2026Q2",
            "target_event": "Synthetic Q2 2026 earnings rehearsal",
            "target_event_at_utc": "2026-09-04T20:00:00Z",
            "as_of_utc": "2026-09-03T12:00:00Z",
            "generated_at_utc": "2026-09-03T12:01:00Z",
            "run_mode": "FORECAST",
            "status": "workflow_rehearsal",
            "agent_model": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "prompt_version": "1",
            "code_revision": "synthetic-test",
            "input_manifest_ids": ["M-1"],
            "parent_forecast_id": "",
            "analyst_owner": "test-fixture",
            "notes": "Synthetic values for software validation only.",
        },
        "target": {
            "target_id": "ABNB-NEXT-Q-REVENUE-GUIDANCE-MIDPOINT-v1",
            "model_stage": "guidance_policy",
            "metric": "revenue_guidance_midpoint",
            "guided_period": "2026Q3",
            "unit": "USD millions",
            "currency": "USD",
        },
        "manifests": [manifest],
        "features": [
            feature("before", "2026-09-03T11:59:59Z"),
            feature("equal", "2026-09-03T12:00:00Z"),
        ],
        "history": [
            {"guided_period": "2024Q3", "guidance_midpoint": "2700"},
            {"guided_period": "2025Q2", "guidance_midpoint": "2750"},
            {"guided_period": "2025Q3", "guidance_midpoint": "3000"},
        ],
        "operating_nowcast": {"p50": "3200", "provenance": "synthetic"},
        "policy_offsets": ["-100", "-50", "25"],
        "range_widths": ["80", "100", "120"],
        "residuals": ["-200", "-100", "0", "100", "200"],
        "agentic_adjustments": [
            {
                "label": "synthetic demand adjustment",
                "amount": "20",
                "evidence_ids": ["E-before"],
                "rationale": "Exercises a positive signed adjustment.",
                "falsification_condition": "The synthetic feature is withdrawn.",
            },
            {
                "label": "synthetic policy adjustment",
                "amount": "-10",
                "evidence_ids": ["E-before"],
                "rationale": "Exercises a negative signed adjustment.",
                "falsification_condition": "The policy assumption is removed.",
            },
        ],
        "alternative_data_requests": [],
        "research_evidence": False,
    }


def test_packet_exposes_baseline_adjustments_and_rejected_evidence() -> None:
    packet = build_packet(rehearsal_payload())
    forecast = packet["forecast_output"]

    assert forecast["seasonal_naive_p50"] == "3000"
    assert forecast["policy_baseline_p50"] == "3150"
    assert forecast["agentic_adjustment_total"] == "10"
    assert forecast["p50"] == "3160"
    assert forecast["p10"] == "3000.0"
    assert forecast["p90"] == "3320.0"
    assert forecast["guidance_range_width_p50"] == "100"
    assert forecast["agentic_weight"] == "1.0"
    assert forecast["local_llm_weight"] == "0.0"
    assert [row["feature_id"] for row in packet["eligible_features"]] == ["before"]
    assert packet["rejected_features"][0]["rejection_reason"] == (
        "not_available_strictly_before_cutoff"
    )
    assert packet["research_claim"] == "workflow_rehearsal_not_backtest"


def test_agentic_adjustment_cannot_cite_rejected_evidence() -> None:
    payload = rehearsal_payload()
    payload["agentic_adjustments"][0]["evidence_ids"] = ["E-equal"]

    with pytest.raises(ValueError, match="eligible evidence"):
        build_packet(payload)


def test_packet_directory_is_immutable_and_checksum_is_auditable(
    tmp_path: Path,
) -> None:
    packet = build_packet(rehearsal_payload())
    packet_dir = tmp_path / "ABNB-REHEARSAL-v1"

    write_packet(packet_dir, packet)

    assert audit_packet(packet_dir) == ()
    assert {path.name for path in packet_dir.iterdir()} == {
        "forecast_packet.json",
        "eligibility_audit.csv",
        "review_memo.md",
        "checksums.sha256",
    }
    with pytest.raises(FileExistsError):
        write_packet(packet_dir, packet)

    packet_path = packet_dir / "forecast_packet.json"
    packet_path.write_text("{}\n", encoding="utf-8")
    assert audit_packet(packet_dir) == ("forecast_packet.json checksum mismatch",)


def test_update_packet_requires_a_new_version_and_parent() -> None:
    payload = rehearsal_payload()
    run = payload["run"]
    assert isinstance(run, dict)
    run["run_mode"] = "UPDATE"
    run["forecast_version"] = 2
    run["parent_forecast_id"] = "ABNB-MVP-REHEARSAL-v1"
    run["forecast_id"] = "ABNB-MVP-REHEARSAL-v2"

    packet = build_packet(payload)

    assert packet["run"]["parent_forecast_id"] == "ABNB-MVP-REHEARSAL-v1"


def test_mvp_refuses_to_label_payload_as_research_evidence() -> None:
    payload = rehearsal_payload()
    payload["research_evidence"] = True

    with pytest.raises(ValueError, match="rehearsal"):
        build_packet(payload)
