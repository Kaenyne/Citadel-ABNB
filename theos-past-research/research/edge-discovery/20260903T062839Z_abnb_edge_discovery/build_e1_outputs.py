from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_ID = "20260903T062839Z_abnb_edge_discovery"
RUN_DIR = ROOT / "research" / "edge_discovery" / RUN_ID
E1_DIR = RUN_DIR / "phase_e1"
HANDOFF_DIR = E1_DIR / "proposed_quant_handoff"
TARGET_PANEL = ROOT / "research" / "readiness" / "20260903T053309Z_abnb_readiness" / "target_panel.csv"
PHASE_A_FEATURES = ROOT / "research" / "readiness" / "20260903T053309Z_abnb_readiness" / "point_in_time_feature_panel.csv"
SOURCE_REGISTRY = ROOT / "research" / "source_registry.csv"
SCRAPING_AUDIT = ROOT / "research" / "scraping_audit.csv"
CREATED_AT = "2026-09-03T16:00:35Z"

HIERARCHY = """1. ABNB Edge-Data Research Orchestrator — main Codex task; owns orchestration, user communication, and the final decision.
2. abnb_alt_data — permanent gpt-5.6-sol research lead; owns source governance, permission decisions, canonical registries, point-in-time methodology, hypothesis reconciliation, and the final ranked slate.
3. physical_world_activity_edge — searches physical sensors, mobility, transportation, remote sensing, environmental, and infrastructure data.
4. supply_scarcity_web_edge — searches STR supply, regulatory, public-calendar, capacity-scarcity, pricing, and permitted web-exhaust data.
"""

APPROVED_IDS = [
    "NASA_BLACK_MARBLE_VNP46A2",
    "NOAA_HMS_SMOKE",
    "WSF_FERRY_RIDERSHIP",
    "NYC_OSE_STR_SNAPSHOTS",
    "ORANGE_FL_TDT_RELEASES",
    "VANCOUVER_STR_LICENSES",
    "NPS_VISITOR_USE",
    "NYC_OSE_ENFORCEMENT_REPORTS",
    "FTA_NTD_MONTHLY_RIDERSHIP",
    "NOLA_STR_PERMIT_EVENTS",
    "NOLA_STR_ENFORCEMENT_HEARINGS",
    "SAN_DIEGO_STRO_ACTIVE",
    "MARINECADASTRE_AIS",
    "NYC_311_TOURISM_STRESS",
    "MELB_PED_HOURLY",
]

PILOTS = {
    "H-004": {
        "source_id": "WSF_FERRY_RIDERSHIP",
        "expected_direction": "positive",
        "geography": "Washington_State_fixed_leisure_minus_commuter_route_panel",
        "primary": "yoy_pct_change_fixed_leisure_route_foot_passengers_minus_yoy_pct_change_fixed_commuter_control_foot_passengers_latest_report_strictly_before_cutoff",
        "sensitivity": "same_fixed_routes_using_total_riders_instead_of_foot_passengers",
        "unit": "percentage_points",
        "minimum": "12 strictly eligible numeric events spanning at least eight guided quarters and both sides of material reporting breaks",
        "missing_reason": "Exact-path terms and robots permission remain unclear; no WSF report was requested. No source value, initial publication timestamp, or released vintage is available for an eligible feature.",
        "regime": "WSF_route_and_reporting_regime_unverified",
        "decision": "INCONCLUSIVE",
    },
    "H-005": {
        "source_id": "ORANGE_FL_TDT_RELEASES",
        "expected_direction": "positive",
        "geography": "Orange_County_Florida_aggregate",
        "primary": "yoy_pct_change_trailing_three_month_sum_TDT_collections_from_PDFs_strictly_before_cutoff",
        "sensitivity": "latest_single_released_collection_month_yoy_pct_change",
        "unit": "percent",
        "minimum": "12 strictly eligible numeric events spanning at least eight guided quarters including pre- and post-COVID observations",
        "missing_reason": "The exact source has no verified terms URL and its robots guidance is unclear; no monthly PDF was requested. No collection amount, initial publication timestamp, or released vintage is available for an eligible feature.",
        "regime": "Orange_County_TDT_definition_and_release_regime_unverified",
        "decision": "INCONCLUSIVE",
    },
    "H-006": {
        "source_id": "NYC_OSE_STR_SNAPSHOTS",
        "expected_direction": "positive",
        "geography": "New_York_City_aggregate",
        "primary": "pct_change_unique_active_registration_numbers_between_consecutive_dated_snapshots_strictly_before_cutoff",
        "sensitivity": "grant_to_application_ratio_latest_dated_annual_report_strictly_before_cutoff",
        "unit": "percent",
        "minimum": "8 strictly eligible post-regime numeric events spanning at least two calendar years and four consecutive snapshot transitions",
        "missing_reason": "NYC terms and robots do not clearly permit the exact automated paths; no snapshot or report was requested. Current records cannot be backfilled and no released vintage is available for an eligible feature.",
        "regime": "NYC_Local_Law_18_post_2023_09_05",
        "decision": "INCONCLUSIVE",
    },
}

DECISIONS = {
    "NASA_BLACK_MARBLE_VNP46A2": ("WATCH_PROSPECTIVELY", "Authenticated Earthdata access was not authorized or attempted; granule versioning and environmental controls require a prospective protocol."),
    "NOAA_HMS_SMOKE": ("CONTROL_ONLY", "Smoke is a sparse disruption control with regenerated-archive and 2022 methodology risks, not a stand-alone demand signal."),
    "WSF_FERRY_RIDERSHIP": ("INCONCLUSIVE", "The dated archive is promising, but permission and report-level initial-publication evidence remain unresolved, so no lawful replay ran."),
    "NYC_OSE_STR_SNAPSHOTS": ("INCONCLUSIVE", "Zero eligible post-regime observations fail H-006's frozen minimum evidence; no readiness promotion or signal/control inference is permitted."),
    "ORANGE_FL_TDT_RELEASES": ("INCONCLUSIVE", "Zero eligible observations fail H-005's frozen minimum evidence; no readiness promotion or signal/control inference is permitted."),
    "VANCOUVER_STR_LICENSES": ("WATCH_PROSPECTIVELY", "The current extract can overwrite status and cannot reconstruct historical state; begin aggregate snapshots only if exact-path permission clears."),
    "NPS_VISITOR_USE": ("WATCH_PROSPECTIVELY", "The finalized API lacks preliminary vintages, so prospective capture is required despite long observation history."),
    "NYC_OSE_ENFORCEMENT_REPORTS": ("CONTROL_ONLY", "Annual enforcement counts measure policy effort more than timely consolidated supply and remain permission-blocked."),
    "FTA_NTD_MONTHLY_RIDERSHIP": ("CONTROL_ONLY", "Publication lag and broad agency-level aggregation make this more suitable as a mobility control than an edge signal."),
    "NOLA_STR_PERMIT_EVENTS": ("INCONCLUSIVE", "Event dates are coherent, but current status can overwrite history and neither path permission nor historical public-state timing is established."),
    "NOLA_STR_ENFORCEMENT_HEARINGS": ("CONTROL_ONLY", "Hearings measure regulatory effort and may be backfilled; use only as a control after immutable publication timing is proven."),
    "SAN_DIEGO_STRO_ACTIVE": ("WATCH_PROSPECTIVELY", "The active-only snapshot cannot be backfilled and contains avoidable personal fields; only aggregate prospective capture is defensible."),
    "MARINECADASTRE_AIS": ("WATCH_PROSPECTIVELY", "Bulk annual timing is too late for same-quarter forecasting and the subset service is unavailable; prospective disruption design remains possible."),
    "NYC_311_TOURISM_STRESS": ("REJECT", "Complaint propensity, enforcement campaigns, mutable classifications, privacy risk, and unresolved vintages overwhelm the tourist-presence mechanism."),
    "MELB_PED_HOURLY": ("WATCH_PROSPECTIVELY", "Undefined portal permission and absent publication vintages block history; a fixed sensor/control panel could begin only prospectively."),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def previous_year(period: str) -> str:
    return f"{int(period[:4]) - 1}{period[4:]}"


def direction(value: str, baseline: str) -> str:
    if not value or not baseline:
        return "not_testable"
    delta = float(value) - float(baseline)
    return "up" if delta > 0 else "down" if delta < 0 else "neutral"


def delta(value: str, baseline: str) -> str:
    if not value or not baseline:
        return ""
    return f"{float(value) - float(baseline):.8f}".rstrip("0").rstrip(".")


def h001_implication(row: dict[str, str]) -> str:
    if row.get("eligible") != "true" or not row.get("feature_value"):
        return "not_testable"
    value = float(row["feature_value"])
    return "down" if value > 0 else "up" if value < 0 else "neutral"


def compare(implication: str, actual: str) -> str:
    if implication == "not_testable" or actual == "not_testable":
        return "not_testable"
    if implication == "neutral" or actual == "neutral":
        return "neutral"
    return "hit" if implication == actual else "miss"


def update_source_approval_notes() -> None:
    rows = read_csv(SOURCE_REGISTRY)
    marker = f"User approved lawful Phase E1 collection/testability review for {RUN_ID}; provider terms, robots, authentication, privacy, rate limits, and PIT vintage gates remain controlling."
    seen: set[str] = set()
    for row in rows:
        if row["source_id"] in APPROVED_IDS and RUN_ID in row.get("analyst_notes", ""):
            seen.add(row["source_id"])
            if marker not in row["analyst_notes"]:
                row["analyst_notes"] = row["analyst_notes"].rstrip(" .") + ". " + marker
    if seen != set(APPROVED_IDS):
        raise ValueError(f"Cannot record approval; missing current-run source rows: {sorted(set(APPROVED_IDS) - seen)}")
    write_csv(SOURCE_REGISTRY, list(rows[0]), rows)


def append_scrape_audit(permission_rows: list[dict[str, str]]) -> None:
    rows = read_csv(SCRAPING_AUDIT)
    fields = list(rows[0])
    prefix = "SA-20260903-E1-"
    rows = [row for row in rows if not row["audit_id"].startswith(prefix)]
    for index, source_id in enumerate(APPROVED_IDS, start=1):
        evidence = next(row for row in permission_rows if row["source_id"] == source_id)
        rows.append({
            "audit_id": f"{prefix}{index:03d}",
            "source_id": source_id,
            "domain": evidence["domain"],
            "intended_paths": evidence["intended_paths"],
            "collection_purpose": "Phase E1 user-approved lawful collection/testability review; smallest source probe only if the deterministic gate allows",
            "terms_url": evidence["terms_url"],
            "robots_url": evidence["robots_url"],
            "reviewed_at_utc": CREATED_AT,
            "terms_status": evidence["terms_status"],
            "robots_status": evidence["robots_status"],
            "authenticated": "true" if source_id == "NASA_BLACK_MARBLE_VNP46A2" else "false",
            "paywalled": "false",
            "captcha_required": "false",
            "access_control_bypass": "false",
            "personal_data": "false",
            "airbnb_controlled": "false",
            "explicit_automation_permission": "false",
            "rate_limit_per_minute": evidence["rate_limit_per_minute"],
            "cache_policy": evidence["cache_policy"],
            "user_agent": "ABNB-Edge-Research/1.0 (institutional research; contact: repository-owner)",
            "collection_allowed": "false",
            "decision_reason": "User source approval recorded but does not override provider gate. " + evidence["decision_reason"],
            "selector_or_endpoint": evidence["intended_paths"],
            "collected_at_utc": "",
            "artifact_path": "",
            "sha256": "",
            "status": "blocked_preflight_no_request",
            "citations": evidence["citations"],
        })
    write_csv(SCRAPING_AUDIT, fields, rows)


def main() -> None:
    E1_DIR.mkdir(parents=True, exist_ok=True)
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    candidates = read_csv(RUN_DIR / "candidate_edge_registry.csv")
    candidate_by_id = {row["source_id"]: row for row in candidates}
    permission_rows = read_csv(RUN_DIR / "permission_and_license_audit.csv")
    permission_by_id = {row["source_id"]: row for row in permission_rows}
    targets = read_csv(TARGET_PANEL)
    h001_rows = [row for row in read_csv(PHASE_A_FEATURES) if row["signal_id"] == "H-001"]
    h001_by_prediction = {row["prediction_id"]: row for row in h001_rows}
    target_by_guided = {row["guided_fiscal_period"]: row for row in targets}
    target_index = {row["prediction_id"]: index for index, row in enumerate(targets)}

    approval_fields = [
        "rank", "source_id", "user_approved_for_lawful_e1_review", "approval_scope", "provider_gate_overridden",
        "collection_allowed", "actual_request_count", "collection_outcome", "historical_class", "strict_cutoff_eligible_now",
        "abnb_outcome_test_scope", "abnb_outcome_test_executed", "final_decision", "decision_rationale", "unblock_condition",
    ]
    approval_rows: list[dict[str, object]] = []
    for rank, source_id in enumerate(APPROVED_IDS, start=1):
        candidate = candidate_by_id[source_id]
        decision, rationale = DECISIONS[source_id]
        is_pilot = source_id in {value["source_id"] for value in PILOTS.values()}
        approval_rows.append({
            "rank": rank,
            "source_id": source_id,
            "user_approved_for_lawful_e1_review": "true",
            "approval_scope": "lawful_collection_and_testability_review_only",
            "provider_gate_overridden": "false",
            "collection_allowed": "false",
            "actual_request_count": 0,
            "collection_outcome": "not_testable",
            "historical_class": candidate["historical_class"],
            "strict_cutoff_eligible_now": "false",
            "abnb_outcome_test_scope": "frozen_pilot_only" if is_pilot else "not_authorized_for_outcome_test",
            "abnb_outcome_test_executed": "false",
            "final_decision": decision,
            "decision_rationale": rationale,
            "unblock_condition": candidate["biggest_failure_reason"] + " Resolve exact provider permission and PIT evidence before any collection or retest.",
        })
    write_csv(E1_DIR / "source_approval_and_disposition.csv", approval_fields, approval_rows)

    collection_fields = [
        "source_id", "exact_source_url", "intended_paths", "terms_url", "terms_status", "robots_url", "robots_status",
        "authentication", "user_approval_recorded", "deterministic_gate_allowed", "gate_reason", "assessed_at_utc",
        "planned_request_count", "actual_request_count", "response_url", "http_status", "cached_artifact_path", "response_sha256",
        "collection_outcome", "historical_testability", "vintage_pit_limitation", "citations",
    ]
    collection_rows: list[dict[str, object]] = []
    for source_id in APPROVED_IDS:
        p = permission_by_id[source_id]
        c = candidate_by_id[source_id]
        collection_rows.append({
            "source_id": source_id,
            "exact_source_url": p["exact_source_url"],
            "intended_paths": p["intended_paths"],
            "terms_url": p["terms_url"],
            "terms_status": p["terms_status"],
            "robots_url": p["robots_url"],
            "robots_status": p["robots_status"],
            "authentication": p["authentication"],
            "user_approval_recorded": "true",
            "deterministic_gate_allowed": "false",
            "gate_reason": "User approval does not override the gate. " + p["decision_reason"],
            "assessed_at_utc": CREATED_AT,
            "planned_request_count": 1,
            "actual_request_count": 0,
            "response_url": "",
            "http_status": "",
            "cached_artifact_path": "",
            "response_sha256": "",
            "collection_outcome": "not_testable",
            "historical_testability": c["historical_class"],
            "vintage_pit_limitation": c["point_in_time_leakage_risk"],
            "citations": p["citations"],
        })
    write_csv(E1_DIR / "collection_testability_audit.csv", collection_fields, collection_rows)

    baseline_fields = [
        "prediction_id", "issuing_fiscal_period", "guided_fiscal_period", "cutoff_utc", "target_midpoint", "target_unit",
        "seasonal_baseline_prediction_id", "seasonal_baseline_value", "target_change_vs_seasonal", "actual_direction_vs_seasonal",
        "prior_quarter_baseline_prediction_id", "prior_quarter_baseline_value", "target_change_vs_prior_quarter", "actual_direction_vs_prior_quarter",
        "h001_eligible", "h001_feature_value", "h001_unit", "h001_signal_implication", "h001_vs_seasonal_classification", "h001_vs_prior_quarter_classification",
        "baseline_comparability_notes",
    ]
    baseline_rows: list[dict[str, object]] = []
    for target in targets:
        seasonal_target = target_by_guided.get(previous_year(target["guided_fiscal_period"]), {})
        index = target_index[target["prediction_id"]]
        prior_target = targets[index - 1] if index else {}
        h001 = h001_by_prediction[target["prediction_id"]]
        seasonal_value = seasonal_target.get("target_midpoint", "")
        prior_value = prior_target.get("target_midpoint", "")
        actual_seasonal = direction(target["target_midpoint"], seasonal_value)
        actual_prior = direction(target["target_midpoint"], prior_value)
        h001_direction = h001_implication(h001)
        baseline_rows.append({
            "prediction_id": target["prediction_id"],
            "issuing_fiscal_period": target["issuing_fiscal_period"],
            "guided_fiscal_period": target["guided_fiscal_period"],
            "cutoff_utc": target["guidance_available_at_utc"],
            "target_midpoint": target["target_midpoint"],
            "target_unit": target["target_unit"],
            "seasonal_baseline_prediction_id": seasonal_target.get("prediction_id", ""),
            "seasonal_baseline_value": seasonal_value,
            "target_change_vs_seasonal": delta(target["target_midpoint"], seasonal_value),
            "actual_direction_vs_seasonal": actual_seasonal,
            "prior_quarter_baseline_prediction_id": prior_target.get("prediction_id", ""),
            "prior_quarter_baseline_value": prior_value,
            "target_change_vs_prior_quarter": delta(target["target_midpoint"], prior_value),
            "actual_direction_vs_prior_quarter": actual_prior,
            "h001_eligible": h001["eligible"],
            "h001_feature_value": h001["feature_value"],
            "h001_unit": h001["unit"],
            "h001_signal_implication": h001_direction,
            "h001_vs_seasonal_classification": compare(h001_direction, actual_seasonal),
            "h001_vs_prior_quarter_classification": compare(h001_direction, actual_prior),
            "baseline_comparability_notes": "Blank target or baseline remains not_testable; H-001 is a control comparator, never fitted jointly in E1.",
        })
    write_csv(E1_DIR / "baseline_audit.csv", baseline_fields, baseline_rows)
    baseline_by_prediction = {row["prediction_id"]: row for row in baseline_rows}

    feature_fields = [
        "feature_row_id", "prediction_id", "issuing_fiscal_period", "guided_fiscal_period", "prediction_cutoff_at_utc",
        "hypothesis_id", "source_id", "feature_variant", "fixed_formula", "expected_direction", "geography",
        "observation_date", "reference_period_start", "reference_period_end", "initial_publication_at_utc", "revision_at_utc",
        "vintage_id", "collected_at_utc", "raw_value_1", "raw_value_2", "feature_value", "unit", "eligible",
        "exclusion_reason", "missingness", "availability_evidence_url", "source_artifact_sha256", "regime", "leakage_warning",
    ]
    replay_fields = [
        "replay_id", "feature_row_id", "prediction_id", "issuing_fiscal_period", "guided_fiscal_period", "cutoff_utc",
        "target_midpoint", "target_unit", "hypothesis_id", "source_id", "feature_variant", "expected_direction", "feature_value",
        "signal_implication", "seasonal_baseline_value", "target_change_vs_seasonal", "actual_direction_vs_seasonal", "replay_vs_seasonal",
        "prior_quarter_baseline_value", "target_change_vs_prior_quarter", "actual_direction_vs_prior_quarter", "replay_vs_prior_quarter",
        "h001_eligible", "h001_feature_value", "h001_signal_implication", "h001_vs_seasonal_classification", "h001_vs_prior_quarter_classification",
        "eligible", "classification", "exclusion_reason", "missingness", "regime", "discrepancies", "leakage_warning",
    ]
    feature_rows: list[dict[str, object]] = []
    replay_rows: list[dict[str, object]] = []
    for hypothesis_id, spec in PILOTS.items():
        source_id = str(spec["source_id"])
        for target in targets:
            baseline = baseline_by_prediction[target["prediction_id"]]
            pre_regime = source_id == "NYC_OSE_STR_SNAPSHOTS" and target["guidance_available_at_utc"] < "2023-09-05T00:00:00Z"
            classification = "excluded" if pre_regime else "not_testable"
            exclusion = "Structural exclusion: prediction cutoff precedes the NYC Local Law 18 registration regime." if pre_regime else str(spec["missing_reason"])
            for variant in ("primary", "sensitivity"):
                feature_id = f"{hypothesis_id}-{target['prediction_id']}-{variant.upper()}"
                replay_missing = ["observation_date", "reference_period", "initial_publication_at_utc", "vintage_id", "collected_at_utc", "raw_values", "feature_value"]
                if not target["target_midpoint"]:
                    replay_missing.append("target_midpoint")
                if not baseline["seasonal_baseline_value"]:
                    replay_missing.append("seasonal_baseline_value")
                if not baseline["prior_quarter_baseline_value"]:
                    replay_missing.append("prior_quarter_baseline_value")
                feature = {
                    "feature_row_id": feature_id,
                    "prediction_id": target["prediction_id"],
                    "issuing_fiscal_period": target["issuing_fiscal_period"],
                    "guided_fiscal_period": target["guided_fiscal_period"],
                    "prediction_cutoff_at_utc": target["guidance_available_at_utc"],
                    "hypothesis_id": hypothesis_id,
                    "source_id": source_id,
                    "feature_variant": variant,
                    "fixed_formula": spec[variant],
                    "expected_direction": spec["expected_direction"],
                    "geography": spec["geography"],
                    "observation_date": "",
                    "reference_period_start": "",
                    "reference_period_end": "",
                    "initial_publication_at_utc": "",
                    "revision_at_utc": "",
                    "vintage_id": "",
                    "collected_at_utc": "",
                    "raw_value_1": "",
                    "raw_value_2": "",
                    "feature_value": "",
                    "unit": spec["unit"],
                    "eligible": "false",
                    "exclusion_reason": exclusion,
                    "missingness": "observation_date; reference_period; initial_publication_at_utc; vintage_id; collected_at_utc; raw_values; feature_value",
                    "availability_evidence_url": "",
                    "source_artifact_sha256": "",
                    "regime": "pre_Local_Law_18" if pre_regime else spec["regime"],
                    "leakage_warning": "A dated archive or present snapshot is not proof that this value was visible strictly before the cutoff; no current value was backfilled.",
                }
                feature_rows.append(feature)
                replay_rows.append({
                    "replay_id": f"REPLAY-{feature_id}",
                    "feature_row_id": feature_id,
                    "prediction_id": target["prediction_id"],
                    "issuing_fiscal_period": target["issuing_fiscal_period"],
                    "guided_fiscal_period": target["guided_fiscal_period"],
                    "cutoff_utc": target["guidance_available_at_utc"],
                    "target_midpoint": target["target_midpoint"],
                    "target_unit": target["target_unit"],
                    "hypothesis_id": hypothesis_id,
                    "source_id": source_id,
                    "feature_variant": variant,
                    "expected_direction": spec["expected_direction"],
                    "feature_value": "",
                    "signal_implication": "not_testable",
                    "seasonal_baseline_value": baseline["seasonal_baseline_value"],
                    "target_change_vs_seasonal": baseline["target_change_vs_seasonal"],
                    "actual_direction_vs_seasonal": baseline["actual_direction_vs_seasonal"],
                    "replay_vs_seasonal": "not_testable",
                    "prior_quarter_baseline_value": baseline["prior_quarter_baseline_value"],
                    "target_change_vs_prior_quarter": baseline["target_change_vs_prior_quarter"],
                    "actual_direction_vs_prior_quarter": baseline["actual_direction_vs_prior_quarter"],
                    "replay_vs_prior_quarter": "not_testable",
                    "h001_eligible": baseline["h001_eligible"],
                    "h001_feature_value": baseline["h001_feature_value"],
                    "h001_signal_implication": baseline["h001_signal_implication"],
                    "h001_vs_seasonal_classification": baseline["h001_vs_seasonal_classification"],
                    "h001_vs_prior_quarter_classification": baseline["h001_vs_prior_quarter_classification"],
                    "eligible": "false",
                    "classification": classification,
                    "exclusion_reason": exclusion,
                    "missingness": "; ".join(replay_missing),
                    "regime": feature["regime"],
                    "discrepancies": target["discrepancy_notes"],
                    "leakage_warning": feature["leakage_warning"],
                })
    write_csv(E1_DIR / "features_long.csv", feature_fields, feature_rows)
    write_csv(E1_DIR / "event_level_replay.csv", replay_fields, replay_rows)

    source_claim_fields = ["claim_id", "source_id", "claim", "source_title", "publisher", "publication_or_update_date", "url", "access_notes", "confidence", "contradictions_or_gaps"]
    claim_rows: list[dict[str, object]] = []
    for index, source_id in enumerate(APPROVED_IDS, start=1):
        candidate = candidate_by_id[source_id]
        claim_rows.append({
            "claim_id": f"E1-CLAIM-{index:03d}",
            "source_id": source_id,
            "claim": "The source remains uncollected and not testable in E1 because the exact deterministic gate did not allow a request or PIT evidence remained unavailable.",
            "source_title": candidate["dataset"],
            "publisher": candidate["provider"],
            "publication_or_update_date": "",
            "url": candidate["exact_source_urls"],
            "access_notes": "Official source and permission evidence were reviewed in E0/E1; no direct request was executed in E1.",
            "confidence": "high for collection outcome; source signal efficacy untested",
            "contradictions_or_gaps": candidate["biggest_failure_reason"],
        })
    claim_rows.extend([
        {"claim_id": "E1-CLAIM-TARGET", "source_id": "ABNB_GUIDANCE_TARGET_PANEL", "claim": "The compact approved target panel contains 23 quarterly guidance events and is used only after H-004 through H-006 were frozen.", "source_title": "Phase-A target panel", "publisher": "ABNB research workspace", "publication_or_update_date": "2026-09-03", "url": str(TARGET_PANEL.relative_to(ROOT)), "access_notes": "Compact table only; no restricted transcript Markdown opened.", "confidence": "high", "contradictions_or_gaps": "Three early targets are qualitative and remain numerically missing."},
        {"claim_id": "E1-CLAIM-H001", "source_id": "FED_H10_DTWEXBGS", "claim": "H-001 is carried only as the previously preregistered point-in-time control comparator.", "source_title": "Phase-A point-in-time feature panel", "publisher": "ABNB research workspace / Federal Reserve Board", "publication_or_update_date": "2026-09-03", "url": str(PHASE_A_FEATURES.relative_to(ROOT)), "access_notes": "No new Federal Reserve request was made in E1.", "confidence": "high", "contradictions_or_gaps": "H-001 itself was inconclusive in Phase A and is not evidence of alpha."},
    ])
    write_csv(E1_DIR / "claim_source_ledger.csv", source_claim_fields, claim_rows)

    # Proposed, deliberately non-executable quant package.
    target_fields = [
        "prediction_id", "cohort", "issuing_fiscal_period", "guided_fiscal_period", "guidance_available_at_utc", "target_metric",
        "target_type", "target_low", "target_high", "target_midpoint", "target_unit", "currency", "constant_currency_basis",
        "target_source_id", "target_citation", "source_turn_id", "target_confidence", "indiscernible_affects_record", "discrepancy_notes",
    ]
    write_csv(HANDOFF_DIR / "targets.csv", target_fields, targets)
    write_csv(HANDOFF_DIR / "features_long.csv", feature_fields, feature_rows)
    write_csv(HANDOFF_DIR / "pre_model_replay.csv", replay_fields, replay_rows)
    cutoff_fields = ["feature_row_id", "prediction_id", "source_id", "observation_date", "initial_publication_at_utc", "revision_at_utc", "collected_at_utc", "prediction_cutoff_at_utc", "strictly_before_cutoff", "eligible", "exclusion_reason", "availability_evidence_url", "source_artifact_sha256"]
    cutoff_rows = [{field: row.get(field, "") for field in cutoff_fields} | {"strictly_before_cutoff": "false"} for row in feature_rows]
    write_csv(HANDOFF_DIR / "cutoff_audit.csv", cutoff_fields, cutoff_rows)
    provenance_fields = ["source_id", "user_approved", "provider_gate_allowed", "actual_request_count", "collection_outcome", "final_decision", "source_url", "terms_url", "robots_url", "license", "collection_timestamp_utc", "artifact_sha256", "notes"]
    provenance_rows = []
    approval_by_id = {row["source_id"]: row for row in approval_rows}
    for source_id in APPROVED_IDS:
        candidate = candidate_by_id[source_id]
        permission = permission_by_id[source_id]
        approval = approval_by_id[source_id]
        provenance_rows.append({
            "source_id": source_id, "user_approved": "true", "provider_gate_allowed": "false", "actual_request_count": 0,
            "collection_outcome": "not_testable", "final_decision": approval["final_decision"], "source_url": permission["exact_source_url"],
            "terms_url": permission["terms_url"], "robots_url": permission["robots_url"], "license": candidate["license_or_reuse"],
            "collection_timestamp_utc": "", "artifact_sha256": "", "notes": approval["decision_rationale"],
        })
    write_csv(HANDOFF_DIR / "source_provenance.csv", provenance_fields, provenance_rows)
    model_matrix_fields = ["prediction_id", "target_midpoint", "seasonal_baseline_value", "prior_quarter_baseline_value", "h001_feature_value", "h004_primary", "h005_primary", "h006_primary"]
    write_csv(HANDOFF_DIR / "model_matrix.csv", model_matrix_fields, [])
    folds_fields = ["fold_id", "prediction_id", "role", "train_start", "train_end", "test_start", "test_end", "embargo_days", "eligible"]
    write_csv(HANDOFF_DIR / "folds.csv", folds_fields, [])
    dictionary_rows = []
    for table, fields in [("features_long.csv", feature_fields), ("pre_model_replay.csv", replay_fields), ("cutoff_audit.csv", cutoff_fields), ("model_matrix.csv", model_matrix_fields), ("folds.csv", folds_fields)]:
        for field in fields:
            dictionary_rows.append({"table": table, "field": field, "type": "boolean" if field in {"eligible", "strictly_before_cutoff"} else "number" if field.endswith("_value") or field in {"target_midpoint", "embargo_days"} else "string", "unit": "field-specific or blank", "nullable": "true", "definition": "Exact field retained for audit; missing values are blank and never imputed in E1."})
    write_csv(HANDOFF_DIR / "data_dictionary.csv", ["table", "field", "type", "unit", "nullable", "definition"], dictionary_rows)

    model_spec = HIERARCHY + """
# Proposed model specification — not authorized for execution

This package contains no eligible edge features and no model-ready rows. Regression, machine learning, coefficient fitting, threshold selection, feature selection, imputation, and fold construction are prohibited in Phase E1.

If a later quant phase is separately authorized after lawful point-in-time evidence is supplied, the target is the next-quarter ABNB revenue-guidance midpoint in USD millions. H-004, H-005, and H-006 must retain their version-1 formulas and directions. Baselines are seasonal-naive same guided quarter one year earlier, prior-quarter guidance midpoint, and H-001 as a control comparator where comparable. An expanding-window design would require at least the hypothesis-specific minimum evidence, an embargo through each prediction cutoff, transformations fit inside training folds, blank missing values, and exclusion of every ineligible row. The only allowed sensitivity for each source is the one frozen in the ledger.

The quant may not infer predictive alpha, direction stability, MAE/RMSE improvement, geographic scalability, or transaction-cost viability from this schema-only handoff.
"""
    (HANDOFF_DIR / "model_spec.md").write_text(model_spec, encoding="utf-8")
    handoff_summary = HIERARCHY + """
# Proposed quant handoff summary

Status: `PROPOSED_NON_EXECUTABLE`.

All 15 sources were user-approved for lawful testability review, but all exact-path collection gates remained blocked. No edge-source request or authenticated API call occurred, and all 138 primary/sensitivity feature rows are ineligible. The 138 replay rows preserve the 23 events, three pilot hypotheses, two fixed variants, target/baseline context, exclusions, missingness, and regime flags. `model_matrix.csv` and `folds.csv` are intentionally header-only.

Signal evidence: none. H-004 and H-005 have 46 `not_testable` rows each. H-006 has 22 structural pre-regime exclusions and 24 post-regime `not_testable` rows across primary and sensitivity variants. H-001 is carried only as the already-governed control comparator. No result may be interpreted as alpha or a failed economic relationship because the edge features were never lawfully observed.
"""
    (HANDOFF_DIR / "handoff_summary.md").write_text(handoff_summary, encoding="utf-8")

    memo = HIERARCHY + """
# Phase E1 source testability and fixed-rule replay memo

## Executive decision

All 15 E0 source IDs are recorded as user-approved for lawful collection and testability review. That approval did not override provider terms, robots rules, authentication, privacy, rate limits, or point-in-time evidence. Every deterministic gate remained blocked; no source request was made. Consequently, no lawful edge feature could be computed and no predictive relationship could be tested. **Predictive alpha remains untested.**

The three frozen pilot hypotheses received an event-level replay with explicit missing and not-testable rows, seasonal and prior-quarter guidance baselines, and H-001 as a control comparator where comparable. No regression, machine learning, threshold search, geography selection, imputation, or post-hoc feature change occurred.

## Pilot decisions

### H-004 — WSF Ferry Ridership: INCONCLUSIVE

- Information versus seasonality: not testable; no WSF feature was lawfully collected.
- Timing: archive cadence appears potentially early enough, but exact report-level first-publication evidence is unverified.
- Consolidated breadth: a Washington route panel is unlikely to be broad enough alone.
- Costs: direct data cost may be low, but permission, route mapping, service-capacity controls, and vintage maintenance are unresolved.
- Stability: not testable across time or geography.
- Falsification: reject usefulness if a permission-cleared 12-event panel fails the fixed direction across reporting regimes or adds no descriptive information versus the named baselines.

### H-005 — Orange County TDT: INCONCLUSIVE

- Information versus seasonality: not testable; no monthly PDF was lawfully collected. The all-lodging series is likely to contain known Orlando seasonality.
- Timing: the collection and publication lag may be too late for guidance even if exact release timestamps are established.
- Consolidated breadth: one hotel-heavy county is not broad enough for consolidated ABNB.
- Costs: data cost may be low, but PDF/vintage maintenance and tax-definition auditing are non-trivial.
- Stability: not testable across time or geography.
- Falsification: reject as an edge signal if a 12-event lawful panel only mirrors the seasonal baseline or changes implication across the COVID/tax regimes.

### H-006 — NYC OSE STR Snapshots: INCONCLUSIVE

- Information versus seasonality: not testable; no snapshot was lawfully collected. The series may primarily identify the Local Law 18 regime.
- Timing: exact snapshot publication timing is unresolved; current records cannot be backfilled.
- Consolidated breadth: NYC's compliant home-share segment is too narrow to establish consolidated materiality alone.
- Costs: aggregate prospective capture may be inexpensive, but regime-definition and snapshot preservation are operationally demanding.
- Stability: no two-year post-regime history or four-transition chain is available.
- Falsification: reject predictive use if a lawful eight-event post-regime panel is dominated by implementation ramp or has unstable direction; retain only as a regulatory control.

## Remaining source decisions

`WATCH_PROSPECTIVELY`: NASA Black Marble, Vancouver STR Licenses, NPS Visitor Use, San Diego STRO Active, MarineCadastre AIS, and Melbourne Pedestrian Counts.

`CONTROL_ONLY`: NOAA HMS Smoke, NYC OSE Enforcement Reports, FTA NTD Monthly Ridership, and New Orleans STR Enforcement Hearings.

`INCONCLUSIVE`: WSF Ferry Ridership, Orange County TDT, NYC OSE STR Snapshots, and New Orleans STR Permit Events.

`REJECT`: NYC 311 Tourism Stress.

No source is promoted. A decision reflects E1 readiness, not the sign or size of an outcome relationship.

The lane-local E1 appendices also preserve five E0 lane candidates that were not retained in the final combined 15: TfL Cycle Hire, CDOT Continuous Counts, Austin Active STR, Hawaii TAT district archives, and Recreation.gov availability. They were not user-approved as part of the final 15, were not included in the combined disposition table, and were not tested against ABNB outcomes.

## Leakage and collection conclusion

Observation date, reference period, initial publication, revision, local collection, and prediction cutoff remain separate fields. Blank timestamps remain blank. No present snapshot was treated as a historical vintage, no equality-at-cutoff row was admitted, and no ineligible edge row entered the proposed model matrix. NASA remains blocked pending separate credential-sync confirmation and an exact-path version audit; no credential value was accessed.

## Stop

Phase E1 stops here. The proposed handoff is schema-complete but deliberately non-executable. A later quant phase requires separate authorization plus lawful point-in-time source artifacts meeting the frozen minimum-evidence rules.
"""
    (E1_DIR / "phase_e1_memo.md").write_text(memo, encoding="utf-8")

    update_source_approval_notes()
    append_scrape_audit(permission_rows)

    handoff_files = [
        "targets.csv", "features_long.csv", "model_matrix.csv", "folds.csv", "cutoff_audit.csv", "source_provenance.csv",
        "data_dictionary.csv", "pre_model_replay.csv", "model_spec.md", "handoff_summary.md",
    ]
    manifest = {
        "run_id": RUN_ID,
        "phase": "E1",
        "status": "PROPOSED_NON_EXECUTABLE",
        "created_at_utc": CREATED_AT,
        "files": handoff_files,
        "target_rows": len(targets),
        "feature_rows": len(feature_rows),
        "eligible_feature_rows": 0,
        "replay_rows": len(replay_rows),
        "model_matrix_rows": 0,
        "fold_rows": 0,
        "predictive_alpha_tested": False,
    }
    (HANDOFF_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    checksum_files = handoff_files + ["manifest.json"]
    checksum_lines = [f"{hashlib.sha256((HANDOFF_DIR / name).read_bytes()).hexdigest()}  {name}" for name in checksum_files]
    (HANDOFF_DIR / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
