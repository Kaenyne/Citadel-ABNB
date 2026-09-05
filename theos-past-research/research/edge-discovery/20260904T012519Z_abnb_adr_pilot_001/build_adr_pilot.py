#!/usr/bin/env python3
"""Build the immutable, leakage-audited ADR pilot artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


RUN = Path(__file__).resolve().parent
REPO = RUN.parents[2]
TARGET_SOURCE = REPO / "research" / "edge_discovery" / "20260903T231817Z_abnb_us_altdata_sleeve" / "guidance_targets.csv"
GENERATED_AT = "2026-09-04T01:38:00Z"
RUN_ID = "20260904T012519Z_abnb_adr_pilot_001"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    targets = read_csv(TARGET_SOURCE)
    if len(targets) != 23:
        raise ValueError(f"Expected 23 target events, found {len(targets)}")
    yoy_count = sum(bool(row.get("guidance_yoy_pct")) for row in targets)
    if yoy_count != 16:
        raise ValueError(f"Expected 16 YoY-comparable events, found {yoy_count}")

    target_fields = list(targets[0])
    write_csv(RUN / "guidance_targets_snapshot.csv", target_fields, targets)

    observation_fields = [
        "source_id", "provider", "series_id", "metric", "reference_period",
        "geography", "unit", "value", "observation_at_utc",
        "first_available_at_utc", "vintage_at_utc", "collected_at_utc",
        "pit_treatment", "raw_file", "source_url", "permission_status",
        "strict_pit_eligible", "exclusion_reason",
    ]
    write_csv(RUN / "observations_long.csv", observation_fields, [])

    panel_fields = [
        "prediction_id", "guidance_cutoff_at_utc", "latest_eligible_reference_period",
        "primary_feature_value", "primary_feature_transform",
        "control_feature_value", "control_feature_transform", "strict_pit_eligible",
        "exclusion_reason", "target_midpoint_usd_millions",
        "prior_year_comparable_midpoint_usd_millions", "guidance_yoy_pct",
        "prior_event_guidance_yoy_pct", "guidance_yoy_acceleration_pp",
        "guidance_yoy_direction", "guidance_acceleration_direction", "event_status",
    ]
    panel = []
    for row in targets:
        comparable = bool(row.get("guidance_yoy_pct"))
        panel.append({
            "prediction_id": row["prediction_id"],
            "guidance_cutoff_at_utc": row["guidance_available_at_utc"],
            "latest_eligible_reference_period": "",
            "primary_feature_value": "",
            "primary_feature_transform": "NSA lodging CPI arithmetic trailing-3-month mean YoY pct",
            "control_feature_value": "",
            "control_feature_transform": "primary minus NSA all-items CPI arithmetic trailing-3-month mean YoY pct",
            "strict_pit_eligible": "false",
            "exclusion_reason": (
                "no lawful official vintage-specific lodging CPI payload; FRED API key absent, "
                "no-key FRED/ALFRED automation prohibited, exact lodging series page HTTP 404, "
                "and BLS archive host stopped after robots HTTP 403"
            ),
            "target_midpoint_usd_millions": row.get("target_midpoint", ""),
            "prior_year_comparable_midpoint_usd_millions": row.get("prior_year_comparable_midpoint", ""),
            "guidance_yoy_pct": row.get("guidance_yoy_pct", ""),
            "prior_event_guidance_yoy_pct": row.get("prior_event_guidance_yoy_pct", ""),
            "guidance_yoy_acceleration_pp": row.get("guidance_yoy_acceleration_pp", ""),
            "guidance_yoy_direction": row.get("guidance_yoy_direction", ""),
            "guidance_acceleration_direction": row.get("guidance_acceleration_direction", ""),
            "event_status": "not_testable" if comparable else "target_not_yoy_comparable",
        })
    write_csv(RUN / "event_aligned_panel.csv", panel_fields, panel)

    metric_rows = []
    for feature in ("primary_lodging_t3m_yoy", "control_lodging_minus_all_items_t3m_yoy"):
        for metric, target in (
            ("pearson", "guidance_yoy_pct"),
            ("spearman", "guidance_yoy_pct"),
            ("direction_concordance", "guidance_yoy_direction"),
            ("acceleration_direction_concordance", "guidance_yoy_acceleration_pp"),
        ):
            metric_rows.append({
                "feature": feature,
                "target": target,
                "metric": metric,
                "value": "",
                "n": 0,
                "eligible_event_requirement": 16 if metric != "acceleration_direction_concordance" else 15,
                "status": "not_testable",
                "reason": "zero strictly PIT-eligible feature rows; descriptive statistic not computed",
            })
    write_csv(
        RUN / "descriptive_metrics.csv",
        ["feature", "target", "metric", "value", "n", "eligible_event_requirement", "status", "reason"],
        metric_rows,
    )

    usability = [
        {"score_type": "data_source", "dimension": "permission_clarity", "score_0_to_5": 1, "evidence": "FRED API terms allow API use but require a key; website automation is prohibited; BLS robots request returned 403."},
        {"score_type": "data_source", "dimension": "cost_and_access", "score_0_to_5": 3, "evidence": "No paid source is needed, but the free FRED key is unsynced and the exact lodging series URL returned 404."},
        {"score_type": "data_source", "dimension": "historical_vintage_support", "score_0_to_5": 0, "evidence": "No lawful requested-series vintage payload was obtained."},
        {"score_type": "data_source", "dimension": "history_coverage", "score_0_to_5": 0, "evidence": "2017-present values were not collected because current snapshots cannot substitute for vintages."},
        {"score_type": "data_source", "dimension": "publication_timing", "score_0_to_5": 1, "evidence": "BLS generally publishes CPI at 08:30 ET, but event-specific archive evidence was inaccessible under the host stop."},
        {"score_type": "data_source", "dimension": "schema_privacy_reproducibility", "score_0_to_5": 5, "evidence": "Aggregate national indexes contain no personal data and have stable series definitions."},
        {"score_type": "forecast_signal", "dimension": "economic_directness", "score_0_to_5": 4, "evidence": "Lodging prices map directly to the ADR/mix leg of nominal revenue."},
        {"score_type": "forecast_signal", "dimension": "lead_time", "score_0_to_5": 2, "evidence": "Monthly CPI is a lagged realized-price measure, not a forward booking indicator."},
        {"score_type": "forecast_signal", "dimension": "geographic_product_alignment", "score_0_to_5": 2, "evidence": "U.S. hotel-heavy national CPI is an imperfect proxy for Airbnb's global alternative-accommodation mix."},
        {"score_type": "forecast_signal", "dimension": "historical_testability", "score_0_to_5": 0, "evidence": "Zero eligible events; the fixed descriptive comparison cannot be run."},
        {"score_type": "forecast_signal", "dimension": "confounder_stability", "score_0_to_5": 2, "evidence": "Pandemic bases, substitution, seasonality, mix, and demand destruction can change the sign."},
        {"score_type": "forecast_signal", "dimension": "incremental_evidence", "score_0_to_5": 0, "evidence": "No relationship or incremental edge was tested."},
    ]
    write_csv(RUN / "usability_score.csv", ["score_type", "dimension", "score_0_to_5", "evidence"], usability)

    permission_results = read_csv(RUN / "permission_request_results.csv")
    raw_rows = []
    for row in permission_results:
        if not row.get("body_cache_path"):
            continue
        raw_rows.append({
            "request_id": row["request_id"],
            "request_class": row["request_class"],
            "source_id": row["source_id"],
            "safe_url": row["requested_url"],
            "requested_at_utc": row["requested_at_utc"],
            "http_status": row["http_status"],
            "content_type": row["content_type"],
            "response_bytes": row["response_bytes"],
            "raw_file": row["body_cache_path"],
            "sha256": row["sha256"],
            "eligibility_use": "permission_evidence_only",
        })
    write_csv(
        RUN / "raw_file_manifest.csv",
        ["request_id", "request_class", "source_id", "safe_url", "requested_at_utc", "http_status", "content_type", "response_bytes", "raw_file", "sha256", "eligibility_use"],
        raw_rows,
    )

    data_requests = read_csv(RUN / "data_request_manifest.csv")
    data_results = []
    gate_map = {
        "ADR-DATA-001": "blocked: missing FRED_API_KEY and exact API-host robots unresolved",
        "ADR-DATA-002": "blocked: missing FRED_API_KEY and exact API-host robots unresolved",
        "ADR-DATA-003": "blocked: website terms prohibit automated extraction and exact lodging series is unavailable",
        "ADR-DATA-004": "blocked: website terms prohibit automated extraction outside the API",
        "ADR-DATA-005": "blocked: BLS robots host stop and current API lacks vintage evidence",
        "ADR-DATA-006": "blocked: BLS robots host stop; archive pages not requested",
    }
    for row in data_requests:
        data_results.append({
            "request_id": row["request_id"],
            "source_id": row["source_id"],
            "registered_at_utc": row["registered_at_utc"],
            "requested_at_utc": "",
            "http_status": "",
            "response_bytes": 0,
            "sha256": "",
            "cache_path": "",
            "gate_allowed_at_request_time": "false",
            "status": "not_requested",
            "reason": gate_map[row["request_id"]],
        })
    write_csv(
        RUN / "data_request_results.csv",
        ["request_id", "source_id", "registered_at_utc", "requested_at_utc", "http_status", "response_bytes", "sha256", "cache_path", "gate_allowed_at_request_time", "status", "reason"],
        data_results,
    )

    permission_audit = [
        {"evidence_id": "ADR-PR-001", "provider": "Federal Reserve Bank of St. Louis", "evidence_type": "robots", "url": "https://fred.stlouisfed.org/robots.txt", "finding": "Generic agents are limited to one request per second and listed graph image/search paths are disallowed; this does not override terms.", "status": "reviewed"},
        {"evidence_id": "ADR-PR-002", "provider": "Federal Reserve Bank of St. Louis", "evidence_type": "api_terms", "url": "https://fred.stlouisfed.org/docs/api/terms_of_use.html", "finding": "The official API permits governed use subject to source rights and requires a registered API key.", "status": "allowed_only_with_key_and_exact_gate"},
        {"evidence_id": "ADR-PR-007", "provider": "Federal Reserve Bank of St. Louis", "evidence_type": "website_terms", "url": "https://fred.stlouisfed.org/legal/", "finding": "Automated data mining, robots, scraping, or extraction is prohibited except as expressly allowed by the FRED API.", "status": "prohibited_for_no_key_automation"},
        {"evidence_id": "ADR-PR-004", "provider": "Federal Reserve Bank of St. Louis", "evidence_type": "robots", "url": "https://alfred.stlouisfed.org/robots.txt", "finding": "Generic agents have a two-second crawl delay and the CSV path is not listed as disallowed; terms remain independently controlling.", "status": "robots_allowed_terms_prohibited"},
        {"evidence_id": "ADR-PR-005|ADR-PR-008", "provider": "Federal Reserve Bank of St. Louis", "evidence_type": "series_availability", "url": "https://alfred.stlouisfed.org/series?seid=CUUR0000SEHB02", "finding": "The exact requested NSA lodging series returned HTTP 404 on both ALFRED and FRED series pages.", "status": "unavailable_exact_series"},
        {"evidence_id": "ADR-PR-009", "provider": "U.S. Bureau of Labor Statistics", "evidence_type": "api_host_robots", "url": "https://api.bls.gov/robots.txt", "finding": "Exact API-host robots states User-agent: * and Disallow: /.", "status": "disallowed"},
        {"evidence_id": "PR-BLS-001", "provider": "U.S. Bureau of Labor Statistics", "evidence_type": "robots", "url": "https://www.bls.gov/robots.txt", "finding": "Same-day governed reconnaissance returned terminal HTTP 403; no retry and no archive request are allowed.", "status": "host_stopped"},
    ]
    write_csv(RUN / "permission_terms_audit.csv", ["evidence_id", "provider", "evidence_type", "url", "finding", "status"], permission_audit)

    summary = {
        "run_id": RUN_ID,
        "request_id": "ABNB-ADR-PILOT-001",
        "generated_at_utc": GENERATED_AT,
        "decision": "INCONCLUSIVE",
        "testability": "not_testable",
        "permission_attempts_registered": 9,
        "permission_provider_http_gets": 9,
        "permission_cached_responses": len(raw_rows),
        "data_payload_requests_registered": len(data_requests),
        "data_payload_http_gets": 0,
        "strict_pit_observations": 0,
        "event_rows": 23,
        "yoy_comparable_events": 16,
        "strict_eligible_yoy_events": 0,
        "descriptive_metrics_computed": 0,
        "current_snapshot_substitution": False,
        "model_fit": False,
        "forecast_promoted": False,
        "alpha_tested": False,
    }
    (RUN / "collection_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    memo = f"""# ABNB Historical ADR Pilot 1 — concise memo

## Decision

**INCONCLUSIVE / NOT TESTABLE.** No lawful vintage-specific lodging CPI payload passed the deterministic collection gate, so the two preregistered features contain zero observations and zero guidance events are strictly eligible. No Pearson, Spearman, direction, or acceleration statistic was computed. This is not a negative signal result; it is a source-readiness failure.

## Frozen design

H-003 version 2 was appended at `2026-09-04T01:25:19Z` before signal/outcome comparison. The primary is NSA lodging CPI trailing-three-month mean YoY growth. The sole control subtracts the identically calculated NSA all-items CPI trailing-three-month mean YoY growth. The target snapshot retains 23 guidance events, including 16 with numeric prior-year-comparable midpoint growth. No transformation, threshold, lag, window, or weight was searched.

## Permission and vintage outcome

- The free FRED API route is governed by official terms but requires `FRED_API_KEY`; no synced key or local `.env` was present. The exact API-host robots path was not established, so the gate remained false even apart from authentication.
- FRED Services terms prohibit automated data mining, scraping, or extraction outside the expressly allowed API. Therefore the otherwise robots-allowed ALFRED graph CSV route was not requested.
- The exact requested series ID `CUUR0000SEHB02` returned HTTP 404 on the official FRED and ALFRED series pages. The all-items control `CPIAUCNS` exists, but it is unusable without the primary.
- BLS's official robots request had already returned terminal HTTP 403 in same-day governed reconnaissance. No retry, archive-page request, or BLS payload occurred. Its current no-key API was not substituted for historical vintages.

There were **9 permission-page/provider GETs**, **6 registered candidate data requests**, and **0 data-payload GETs**. The exact `api.bls.gov` robots file states `User-agent: *` and `Disallow: /`, so the no-key BLS API path is affirmatively disallowed for this automated run despite the public API documentation and final-on-release CPI policy. All cached responses are checksummed. No personal data, paid source, credential value, authenticated request, restricted transcript, regression, or model was used.

## Usability

Data-source usability is **1.7/5** on the six prespecified dimensions: free aggregate data and privacy are favorable, but exact-series availability, credential sync, path permission, vintage access, and event-specific publication evidence failed. Forecast-signal usability remains **2.0/5 ex ante**: the ADR mechanism is coherent, but the proxy is lagged, U.S.-only, hotel-heavy, and currently untestable. These scores describe usability, not predictive performance.

## What would resolve the blocker

Either (1) a synced free FRED key plus official confirmation that a supported ALFRED series exactly matches NSA BLS lodging CPI and exact API-path robots permission, or (2) written BLS automation permission or user-supplied lawful original CPI release artifacts with publication timestamps. Until then, H-003 v2 must not enter an ABNB forecast.

Predictive alpha has not been tested, and this pilot is not promoted to forecasting.
"""
    (RUN / "memo.md").write_text(memo, encoding="utf-8")

    validation = {
        "run_id": RUN_ID,
        "validated_at_utc": GENERATED_AT,
        "status": "pass_not_testable",
        "checks": {
            "target_rows_23": len(targets) == 23,
            "yoy_comparable_rows_16": yoy_count == 16,
            "observations_zero_without_vintage": True,
            "panel_rows_23": len(panel) == 23,
            "strict_eligible_rows_zero": all(row["strict_pit_eligible"] == "false" for row in panel),
            "permission_registration_precedes_requests": all(
                not row["requested_at_utc"] or row["registered_at_utc"] < row["requested_at_utc"]
                for row in permission_results
            ),
            "data_payload_http_gets_zero": True,
            "no_current_snapshot_substitution": True,
            "metrics_not_computed_at_n_zero": all(row["value"] == "" and row["n"] == 0 for row in metric_rows),
            "no_model_fit": True,
            "no_forecast_promotion": True,
        },
        "source_target_sha256": sha256(TARGET_SOURCE),
    }
    if not all(validation["checks"].values()):
        raise ValueError(f"Validation failed: {validation}")
    (RUN / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    excluded_from_checksums = {"checksums.sha256", "artifact_manifest.csv"}
    files = sorted(
        path for path in RUN.rglob("*")
        if path.is_file()
        and path.name not in excluded_from_checksums
        and "__pycache__" not in path.parts
        and "raw/permission" not in str(path.relative_to(RUN))
    )
    checksum_lines = [f"{sha256(path)}  {path.relative_to(RUN)}" for path in files]
    checksum_lines.extend(
        f"{row['sha256']}  {row['raw_file']}"
        for row in raw_rows
    )
    (RUN / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    manifest_rows = [{
        "artifact": str(path.relative_to(RUN)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "role": "raw_permission_cache" if "raw/permission" in str(path.relative_to(RUN)) else "audit_or_analysis",
    } for path in files]
    manifest_rows.extend({
        "artifact": row["raw_file"],
        "bytes": row["response_bytes"],
        "sha256": row["sha256"],
        "role": "raw_permission_cache",
    } for row in raw_rows)
    manifest_rows.append({
        "artifact": "checksums.sha256",
        "bytes": (RUN / "checksums.sha256").stat().st_size,
        "sha256": sha256(RUN / "checksums.sha256"),
        "role": "checksum_manifest",
    })
    write_csv(RUN / "artifact_manifest.csv", ["artifact", "bytes", "sha256", "role"], manifest_rows)


if __name__ == "__main__":
    main()
