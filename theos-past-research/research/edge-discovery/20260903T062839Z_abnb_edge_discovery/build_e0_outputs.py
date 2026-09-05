"""Build the governed Phase E0 reconciliation artifacts.

This script reads only lane-owned structured reconnaissance files. It does not
make network requests, inspect ABNB outcomes, or touch restricted transcripts.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_ID = "20260903T062839Z_abnb_edge_discovery"
RUN_DIR = ROOT / "research" / "edge_discovery" / RUN_ID
COLLECTED_AT = "2026-09-03T06:40:30Z"

PHYSICAL_DIR = RUN_DIR / "physical_world_activity_edge"
SUPPLY_DIR = RUN_DIR / "supply_scarcity_web_edge"

HIERARCHY = """1. ABNB Edge-Data Research Orchestrator — main Codex task; owns orchestration, user communication, and the final decision.
2. abnb_alt_data — permanent gpt-5.6-sol research lead; owns source governance, permission decisions, canonical registries, point-in-time methodology, hypothesis reconciliation, and the final ranked slate.
3. physical_world_activity_edge — searches physical sensors, mobility, transportation, remote sensing, environmental, and infrastructure data.
4. supply_scarcity_web_edge — searches STR supply, regulatory, public-calendar, capacity-scarcity, pricing, and permitted web-exhaust data.
"""

SELECTED_PHYSICAL = {
    "WSF_FERRY_RIDERSHIP",
    "NASA_BLACK_MARBLE_VNP46A2",
    "NOAA_HMS_SMOKE",
    "NPS_VISITOR_USE",
    "FTA_NTD_MONTHLY_RIDERSHIP",
    "MELB_PED_HOURLY",
    "NYC_311_TOURISM_STRESS",
    "MARINECADASTRE_AIS",
}

SELECTED_SUPPLY = {
    "SCW-002",
    "SCW-003",
    "SCW-004",
    "SCW-005",
    "SCW-006",
    "SCW-008",
    "SCW-010",
}

CANONICAL = {
    "SCW-002": "NOLA_STR_PERMIT_EVENTS",
    "SCW-003": "NOLA_STR_ENFORCEMENT_HEARINGS",
    "SCW-004": "VANCOUVER_STR_LICENSES",
    "SCW-005": "NYC_OSE_STR_SNAPSHOTS",
    "SCW-006": "ORANGE_FL_TDT_RELEASES",
    "SCW-008": "SAN_DIEGO_STRO_ACTIVE",
    "SCW-010": "NYC_OSE_ENFORCEMENT_REPORTS",
}

HISTORICAL_CLASS = {
    "NASA_BLACK_MARBLE_VNP46A2": "prospective_only",
    "WSF_FERRY_RIDERSHIP": "backtestable_now",
    "NOAA_HMS_SMOKE": "prospective_only",
    "NYC_OSE_STR_SNAPSHOTS": "backtestable_now",
    "ORANGE_FL_TDT_RELEASES": "backtestable_now",
    "VANCOUVER_STR_LICENSES": "prospective_only",
    "NPS_VISITOR_USE": "prospective_only",
    "NYC_OSE_ENFORCEMENT_REPORTS": "backtestable_now",
    "FTA_NTD_MONTHLY_RIDERSHIP": "prospective_only",
    "NOLA_STR_PERMIT_EVENTS": "prospective_only",
    "NOLA_STR_ENFORCEMENT_HEARINGS": "prospective_only",
    "SAN_DIEGO_STRO_ACTIVE": "prospective_only",
    "MARINECADASTRE_AIS": "prospective_only",
    "NYC_311_TOURISM_STRESS": "prospective_only",
    "MELB_PED_HOURLY": "prospective_only",
}

STATUS_OVERRIDE = {
    "NASA_BLACK_MARBLE_VNP46A2": "pending_sync",
    "WSF_FERRY_RIDERSHIP": "pending_permission",
    "NOAA_HMS_SMOKE": "pending_permission",
    "NYC_OSE_STR_SNAPSHOTS": "pending_permission",
    "ORANGE_FL_TDT_RELEASES": "pending_permission",
    "VANCOUVER_STR_LICENSES": "pending_permission",
    "NPS_VISITOR_USE": "pending_permission",
    "NYC_OSE_ENFORCEMENT_REPORTS": "pending_permission",
    "FTA_NTD_MONTHLY_RIDERSHIP": "pending_permission",
    "NOLA_STR_PERMIT_EVENTS": "pending_permission",
    "NOLA_STR_ENFORCEMENT_HEARINGS": "pending_permission",
    "SAN_DIEGO_STRO_ACTIVE": "prospective_only",
    "MARINECADASTRE_AIS": "prospective_only",
    "NYC_311_TOURISM_STRESS": "prospective_only",
    "MELB_PED_HOURLY": "pending_permission",
}

PILOTS = {
    "WSF_FERRY_RIDERSHIP": (
        "Latest dated report strictly before cutoff: YoY change in fixed leisure-route foot passengers minus YoY change in fixed Seattle/Bainbridge and Seattle/Bremerton commuter-control foot passengers.",
        "Use total riders instead of foot passengers with the same fixed route sets.",
    ),
    "ORANGE_FL_TDT_RELEASES": (
        "YoY percent change in the trailing three-month sum of Orange County TDT collections from PDFs released strictly before the cutoff.",
        "Use the latest single released collection month YoY instead of the trailing three-month sum.",
    ),
    "NYC_OSE_STR_SNAPSHOTS": (
        "Percent change in unique active registration numbers between consecutive dated OSE snapshots released strictly before the cutoff, aggregated citywide and never retaining addresses or listing identifiers.",
        "Use the grant-to-application ratio from the latest dated annual registration report strictly before the cutoff.",
    ),
}

MOONSHOTS = {
    "NASA_BLACK_MARBLE_VNP46A2": (
        "Median quality-screened radiance YoY change across fixed resort polygons minus matched resident-control polygons over the last 28 eligible days.",
        "Fraction of valid pixels with positive YoY radiance change under identical masks.",
    ),
    "MULTICITY_STR_PUBLIC_SNAPSHOT_MESH": (
        "Daily aggregate active-permit stock by city from approved official APIs; quarterly feature is net active-stock change divided by beginning active stock across a fixed equal-weight city panel.",
        "Renewal survival rate for the same fixed city panel.",
    ),
}

HISTORY_START = {
    "WSF_FERRY_RIDERSHIP": "2002-01-01",
    "NASA_BLACK_MARBLE_VNP46A2": "2012-01-01",
    "NOAA_HMS_SMOKE": "2005-01-01",
    "NPS_VISITOR_USE": "1979-01-01",
    "FTA_NTD_MONTHLY_RIDERSHIP": "2002-01-01",
    "MELB_PED_HOURLY": "2009-01-01",
    "NYC_311_TOURISM_STRESS": "2010-01-01",
    "MARINECADASTRE_AIS": "2009-01-01",
    "NOLA_STR_PERMIT_EVENTS": "2017-05-04",
    "NOLA_STR_ENFORCEMENT_HEARINGS": "2018-01-01",
    "VANCOUVER_STR_LICENSES": "",
    "NYC_OSE_STR_SNAPSHOTS": "2023-09-05",
    "ORANGE_FL_TDT_RELEASES": "2019-04-01",
    "SAN_DIEGO_STRO_ACTIVE": "2023-01-19",
    "NYC_OSE_ENFORCEMENT_REPORTS": "2016-01-01",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def pick(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name, "")
        if value:
            return value
    return ""


def normalize_candidate(row: dict[str, str], lane: str) -> dict[str, str]:
    lane_source_id = row["source_id"]
    source_id = CANONICAL.get(lane_source_id, lane_source_id)
    formula, sensitivity = PILOTS.get(source_id, ("", ""))
    if source_id == "NASA_BLACK_MARBLE_VNP46A2":
        formula, sensitivity = MOONSHOTS[source_id]
    normalized = {
        "source_id": source_id,
        "lane_source_id": lane_source_id,
        "research_lane": lane,
        "dataset": row["dataset"],
        "provider": row["provider"],
        "edge_family": pick(row, "edge_family") or pick(row, "measure_type"),
        "economic_mechanism": row["economic_mechanism"],
        "predicted_direction": row["predicted_direction"],
        "potential_abnb_target": row["potential_abnb_target"],
        "measurement_type": pick(row, "measurement_type", "measure_type"),
        "why_underused": row["why_underused"],
        "geographic_coverage": row["geographic_coverage"],
        "plausible_abnb_materiality": row["plausible_abnb_materiality"],
        "unit_of_observation": pick(row, "unit_of_observation", "unit"),
        "granularity": row["granularity"],
        "frequency": row["frequency"],
        "history": row["history"],
        "publication_schedule_and_lag": row["publication_schedule_and_lag"],
        "earliest_verifiable_public_availability": row["earliest_verifiable_public_availability"],
        "revision_or_snapshot_policy": pick(row, "revision_or_snapshot_policy", "record_behavior"),
        "true_vintage_support": pick(row, "true_vintage_support", "real_vintage_support"),
        "access_method": row["access_method"],
        "exact_source_urls": pick(row, "exact_source_urls", "exact_source_url"),
        "terms_url": pick(row, "terms_url"),
        "robots_url": pick(row, "robots_url"),
        "credential_requirement": row["credential_requirement"],
        "environment_variables": pick(row, "environment_variables", "required_environment_variables"),
        "cost": pick(row, "cost", "free_tier_and_cost"),
        "license_or_reuse": pick(row, "license_or_reuse", "license"),
        "collection_restrictions": pick(row, "collection_restrictions", "collection_and_redistribution_restrictions"),
        "sensor_methodology_survivorship_risks": pick(row, "sensor_methodology_survivorship_risks", "methodology_outage_survivorship_risks"),
        "point_in_time_leakage_risk": row["point_in_time_leakage_risk"],
        "leakage_mitigation": pick(row, "leakage_mitigation"),
        "historical_guidance_cutoff_coverage": pick(row, "historical_guidance_cutoff_coverage", "historical_cutoff_coverage"),
        "strict_cutoff_eligible_now": "false",
        "smallest_lawful_validation_sample": row["smallest_lawful_validation_sample"],
        "status": STATUS_OVERRIDE[source_id],
        "historical_class": HISTORICAL_CLASS[source_id],
        "selected_historical_pilot": str(source_id in PILOTS).lower(),
        "selected_moonshot": str(source_id in MOONSHOTS).lower(),
        "primary_feature_formula_if_selected": formula,
        "sensitivity_if_selected": sensitivity,
        "biggest_failure_reason": row["biggest_failure_reason"],
        "citations": row["citations"],
        "collection_timestamp_utc": pick(row, "collection_timestamp_utc") or COLLECTED_AT,
        "analyst_notes": pick(row, "analyst_notes"),
    }
    # Two physical-lane rows contained an unquoted comma in a prose field,
    # shifting the tail columns while remaining parseable CSV. Reconcile those
    # rows from their lane report and preflight records before canonical use.
    if source_id == "NOAA_HMS_SMOKE":
        normalized.update({
            "access_method": "Official KML/shapefile archive and product page; current regenerated annual bundles are not historical snapshots.",
            "exact_source_urls": "https://www.ospo.noaa.gov/products/land/hms.html; https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/Shapefile/",
            "credential_requirement": "None",
            "environment_variables": "",
            "cost": "Free",
            "license_or_reuse": "NOAA-produced data generally public domain/CC0 with attribution and no implied endorsement",
            "collection_restrictions": "No automated request until path-specific robots status is verified; cache daily files and metadata; no tactical safety inference.",
            "sensor_methodology_survivorship_risks": "Cloud cover; analyst subjectivity; satellite additions/removals; missing data not backfilled; 2022 classification/format change; regenerated archive timestamps.",
            "point_in_time_leakage_risk": "Treating regenerated annual bundles as original vintages or assigning end-of-day smoke information to an earlier cutoff.",
            "leakage_mitigation": "Use dated single-day operational files only; exclude annual regenerated-bundle timestamps; preserve a 2022 regime break.",
            "historical_guidance_cutoff_coverage": "Observation history spans 23/23 events, but 0/23 are strict-eligible until daily-file availability and vintage handling are locked.",
            "smallest_lawful_validation_sample": "One product metadata page and one single-day archive file; gate denied, so zero requests.",
            "primary_feature_formula_if_selected": "",
            "sensitivity_if_selected": "",
            "biggest_failure_reason": "Smoke is sparse, highly seasonal, and may proxy widely known wildfire news rather than incremental destination demand.",
            "citations": "https://www.ospo.noaa.gov/products/land/hms.html; https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/Shapefile/Annual_Bundles/; https://www.ospo.noaa.gov/data/messages/2022/05/MSG_20220527_1253.html",
            "analyst_notes": "Conditional only after permission and daily-file provenance audit; never use regenerated annual-bundle timestamps as historical availability.",
        })
    elif source_id == "NYC_311_TOURISM_STRESS":
        normalized.update({
            "access_method": "Socrata SODA/OData with server-side aggregation only; portal restore points are not yet verified as complete historical snapshots.",
            "exact_source_urls": "https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9; https://opendata.cityofnewyork.us/311-service-requests-from-2010-to-present-updates/",
            "credential_requirement": "None",
            "environment_variables": "",
            "cost": "Free",
            "license_or_reuse": "NYC Open Data terms allow public dataset use with source/version/modification identification",
            "collection_restrictions": "Query only aggregate counts; never select or retain addresses, BBL, coordinates, free text, or complainant data; robots evidence required.",
            "sensor_methodology_survivorship_risks": "Complaint-channel changes; enforcement campaigns; category renames; reporting propensity; duplicate complaints; COVID regime; mutable closure/status fields.",
            "point_in_time_leakage_risk": "Using later reclassification or deletion state at an earlier cutoff, or collecting household-level location fields.",
            "leakage_mitigation": "Use created-date aggregates only after a complete restore-point audit; predeclare complaint categories and tourist/control districts; retain channel and taxonomy-change controls.",
            "historical_guidance_cutoff_coverage": "History spans 23/23 events, but 0/23 are strict-eligible until complete restore-point coverage or contemporaneous aggregates are proven.",
            "smallest_lawful_validation_sample": "One metadata response plus one server-side aggregate count with no location microdata; gate denied, so zero requests.",
            "primary_feature_formula_if_selected": "",
            "sensitivity_if_selected": "",
            "biggest_failure_reason": "Complaints measure reporting and enforcement behavior, not tourist presence, and vintage reconstruction is unresolved.",
            "citations": "https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9; https://opendata.cityofnewyork.us/311-service-requests-from-2010-to-present-updates/; https://cityofnewyork.github.io/opendatatsm/publicpolicies.html",
            "analyst_notes": "Negative-control design is mandatory; community-created filtered views are not authoritative.",
        })
    return normalized


def score_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for lane, path, selected in (
        ("physical_world_activity_edge", PHYSICAL_DIR / "edge_scorecard.csv", SELECTED_PHYSICAL),
        ("supply_scarcity_web_edge", SUPPLY_DIR / "edge_scorecard.csv", SELECTED_SUPPLY),
    ):
        for row in read_csv(path):
            if row["source_id"] not in selected:
                continue
            sid = CANONICAL.get(row["source_id"], row["source_id"])
            normalized = {
                "source_id": sid,
                "lane_source_id": row["source_id"],
                "research_lane": lane,
                "causal_proximity_20": row["causal_proximity_20"],
                "pit_vintage_defensibility_20": pick(row, "pit_vintage_defensibility_20", "point_in_time_vintage_20"),
                "differentiation_underuse_15": row["differentiation_underuse_15"],
                "geographic_scalability_15": pick(row, "geographic_scalability_15", "geographic_relevance_scale_15"),
                "frequency_lead_time_10": row["frequency_lead_time_10"],
                "permission_license_clarity_10": row["permission_license_clarity_10"],
                "operational_reliability_5": row["operational_reliability_5"],
                "free_low_cost_5": row["free_low_cost_5"],
                "total_100": row["total_100"],
                "status": STATUS_OVERRIDE[sid],
                "historical_class": HISTORICAL_CLASS[sid],
                "score_rationale": pick(row, "scoring_note", "score_rationale"),
            }
            total = sum(int(normalized[key]) for key in (
                "causal_proximity_20", "pit_vintage_defensibility_20",
                "differentiation_underuse_15", "geographic_scalability_15",
                "frequency_lead_time_10", "permission_license_clarity_10",
                "operational_reliability_5", "free_low_cost_5",
            ))
            if total != int(normalized["total_100"]):
                raise ValueError(f"score mismatch for {sid}: {total}")
            rows.append(normalized)
    rows.sort(key=lambda item: (-int(item["total_100"]), item["source_id"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = str(index)
    return rows


def candidate_rows(scores: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for row in read_csv(PHYSICAL_DIR / "candidate_edge_registry.csv"):
        if row["source_id"] in SELECTED_PHYSICAL:
            item = normalize_candidate(row, "physical_world_activity_edge")
            by_id[item["source_id"]] = item
    for row in read_csv(SUPPLY_DIR / "candidate_edge_registry.csv"):
        if row["source_id"] in SELECTED_SUPPLY:
            item = normalize_candidate(row, "supply_scarcity_web_edge")
            by_id[item["source_id"]] = item
    ordered = []
    for score in scores:
        row = by_id[score["source_id"]]
        row["rank"] = score["rank"]
        row["ex_ante_score_100"] = score["total_100"]
        ordered.append(row)
    if len(ordered) != 15:
        raise ValueError(f"expected 15 retained candidates, got {len(ordered)}")
    return ordered


def permission_rows(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    by_lane = {row["lane_source_id"]: row for row in candidates}
    output: list[dict[str, str]] = []
    for row in read_csv(PHYSICAL_DIR / "permission_and_license_audit.csv"):
        if row["source_id"] not in SELECTED_PHYSICAL:
            continue
        candidate = by_lane[row["source_id"]]
        output.append({
            "source_id": candidate["source_id"], "lane_source_id": row["source_id"],
            "domain": row["domain"], "exact_source_url": candidate["exact_source_urls"],
            "intended_paths": row["intended_paths"], "terms_url": row["terms_url"],
            "terms_status": row["terms_status"], "robots_url": row["robots_url"],
            "robots_status": row["robots_status"], "license_or_reuse": row["license_or_reuse"],
            "authentication": row["authentication"], "personal_data_plan": row["personal_data_plan"],
            "rate_limit_per_minute": "1", "cache_policy": row["cache_plan"],
            "collection_allowed": row["gate_allowed"], "decision_reason": row["decision_reason"],
            "reviewed_at_utc": row["reviewed_at_utc"], "direct_requests_made": "0",
            "citations": row["citations"],
        })
    for row in read_csv(SUPPLY_DIR / "lane_preflight.csv"):
        if row["source_id"] not in SELECTED_SUPPLY:
            continue
        candidate = by_lane[row["source_id"]]
        output.append({
            "source_id": candidate["source_id"], "lane_source_id": row["source_id"],
            "domain": row["source_domain"], "exact_source_url": row["exact_source_url"],
            "intended_paths": row["proposed_paths"], "terms_url": row["terms_url"],
            "terms_status": row["terms_status"], "robots_url": row["robots_url"],
            "robots_status": row["robots_status"], "license_or_reuse": row["terms_evidence"],
            "authentication": "none" if row["authenticated"] == "false" else "required",
            "personal_data_plan": "Aggregate only; exclude all direct identifiers, addresses, free text, and contact fields.",
            "rate_limit_per_minute": row["requests_per_minute"], "cache_policy": "Cache exact response and checksum",
            "collection_allowed": "false", "decision_reason": row["decision_reasons"],
            "reviewed_at_utc": row["reviewed_at_utc"], "direct_requests_made": "0",
            "citations": candidate["citations"],
        })
    output.sort(key=lambda item: int(next(row["rank"] for row in candidates if row["source_id"] == item["source_id"])))
    return output


def archive_rows(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    supply_archive = {CANONICAL.get(row["source_id"], row["source_id"]): row for row in read_csv(SUPPLY_DIR / "historical_archive_matrix.csv")}
    output = []
    for candidate in candidates:
        sid = candidate["source_id"]
        if sid in supply_archive:
            row = supply_archive[sid]
            output.append({
                "source_id": sid, "history_claim": row["history_claim"],
                "earliest_verifiable_public_availability": row["earliest_verifiable_public_availability"],
                "archive_or_vintage_evidence": row["archive_or_vintage_evidence"],
                "record_behavior": row["record_behavior"], "real_vintage_support": row["real_vintage_support"],
                "historical_guidance_cutoff_coverage_estimate": row["historical_guidance_cutoff_coverage_estimate"],
                "strict_cutoff_eligible_now": row["strict_cutoff_eligible_now"], "reason": row["reason"],
            })
        else:
            output.append({
                "source_id": sid, "history_claim": candidate["history"],
                "earliest_verifiable_public_availability": candidate["earliest_verifiable_public_availability"],
                "archive_or_vintage_evidence": candidate["true_vintage_support"] + "; " + candidate["revision_or_snapshot_policy"],
                "record_behavior": candidate["revision_or_snapshot_policy"],
                "real_vintage_support": candidate["true_vintage_support"],
                "historical_guidance_cutoff_coverage_estimate": candidate["historical_guidance_cutoff_coverage"],
                "strict_cutoff_eligible_now": "false",
                "reason": candidate["point_in_time_leakage_risk"],
            })
    return output


def tiny_rows(candidates: list[dict[str, str]], permissions: list[dict[str, str]]) -> list[dict[str, str]]:
    permission_by_id = {row["source_id"]: row for row in permissions}
    rows = []
    for candidate in candidates:
        permission = permission_by_id[candidate["source_id"]]
        rows.append({
            "source_id": candidate["source_id"],
            "planned_endpoint_or_file": candidate["exact_source_urls"],
            "planned_request_count": "2",
            "actual_request_count": "0",
            "collection_utc": "", "http_status": "", "response_checksum": "", "cache_path": "",
            "selectors_or_fields": candidate["smallest_lawful_validation_sample"],
            "decision": "not_collected",
            "stop_reason": "Deterministic gate blocked: " + permission["decision_reason"],
        })
    return rows


def markdown_table(rows: list[dict[str, str]], fields: list[tuple[str, str]]) -> str:
    header = "| " + " | ".join(label for _, label in fields) + " |\n"
    divider = "| " + " | ".join("---" for _ in fields) + " |\n"
    body = ""
    for row in rows:
        values = []
        for key, _ in fields:
            value = row.get(key, "").replace("|", "/").replace("\n", " ")
            values.append(value)
        body += "| " + " | ".join(values) + " |\n"
    return header + divider + body


def write_reports(candidates: list[dict[str, str]], scores: list[dict[str, str]]) -> None:
    score_by_id = {row["source_id"]: row for row in scores}
    physical = [row for row in candidates if row["research_lane"] == "physical_world_activity_edge"]
    supply = [row for row in candidates if row["research_lane"] == "supply_scarcity_web_edge"]

    physical_text = HIERARCHY + "\n# Physical-world activity edge — Phase E0\n\n"
    physical_text += "The lane screened ten physical-world candidates and the lead retained eight. Every exact-path autonomous gate was blocked, principally because path-specific robots evidence was unavailable; NASA also requires unsynced Earthdata credentials. No direct request or tiny sample was made.\n\n"
    physical_text += markdown_table(
        [{**row, "score": score_by_id[row["source_id"]]["total_100"]} for row in physical],
        [("source_id", "Source"), ("score", "Score"), ("status", "Status"), ("historical_class", "History class"), ("biggest_failure_reason", "Largest failure risk")],
    )
    physical_text += "\nWSF has the cleanest dated report path. NPS is economically close but lacks preliminary monthly vintages. NOAA HMS has dated daily operations but regenerated bundles and a 2022 regime break. FTA, NYC 311, Melbourne, and AIS should not be treated as historical vintages from present extracts. NASA Black Marble is a credential-gated moonshot. Predictive alpha has not been tested.\n"
    (RUN_DIR / "physical_world_activity_edge_report.md").write_text(physical_text, encoding="utf-8")

    supply_text = HIERARCHY + "\n# Supply, scarcity, and permitted web edge — Phase E0\n\n"
    supply_text += "The lane screened ten candidates and the lead retained seven. No direct request or tiny sample was made because every retained exact-path gate failed on unresolved terms or robots evidence. The analysis never retained names, addresses, unit numbers, tax identifiers, listing URLs, free text, or contact fields.\n\n"
    supply_text += markdown_table(
        [{**row, "score": score_by_id[row["source_id"]]["total_100"]} for row in supply],
        [("source_id", "Source"), ("score", "Score"), ("status", "Status"), ("historical_class", "History class"), ("biggest_failure_reason", "Largest failure risk")],
    )
    supply_text += "\nOrange County TDT has the best publication-specific vintage evidence but is hotel-heavy and geographically narrow. NYC OSE annual reports and dated snapshots are real artifacts but cover a short regulatory regime. Vancouver and New Orleans event dates are not historical publication vintages. San Diego is an active-only snapshot. Predictive alpha has not been tested.\n"
    (RUN_DIR / "supply_scarcity_web_edge_report.md").write_text(supply_text, encoding="utf-8")

    memo = HIERARCHY + "\n# Source-selection memo — Phase E0\n\n"
    memo += "## Decision boundary\n\nPhase E0 is complete. This is an ex-ante source-governance ranking, not evidence of forecast improvement. **Predictive alpha has not been tested.** No ABNB outcome relationship was inspected, no hypothesis was added, no model or replay was run, and Phase E1 has not begun.\n\n"
    memo += "`historical_class=backtestable_now` below means only that dated source artifacts exist. It does not mean collectibility is cleared. Each such source has `status=pending_permission`, and every candidate currently has `strict_cutoff_eligible_now=false` until exact permission and event-level release timestamps are verified.\n\n"
    memo += markdown_table(
        [{**row, "score": score_by_id[row["source_id"]]["total_100"]} for row in candidates],
        [("rank", "Rank"), ("source_id", "Source"), ("score", "Score"), ("historical_class", "Class"), ("potential_abnb_target", "Potential target"), ("biggest_failure_reason", "Biggest failure reason")],
    )
    memo += "\n## Backtestable-now archive candidates\n\n"
    memo += "- `WSF_FERRY_RIDERSHIP`: archive proven through dated quarterly PDFs; permission pending; 0/23 event rows are currently strict-eligible. Estimated 23/23 guidance cutoffs have a prior report, subject to exact publication verification.\n- `ORANGE_FL_TDT_RELEASES`: archive proven through separate monthly PDFs with explicit release timestamps; permission pending; 0/23 event rows are currently strict-eligible. Estimated 23/23 coverage.\n- `NYC_OSE_STR_SNAPSHOTS`: archive proven for FY23-FY26 reports and a dated 2026 snapshot; permission pending; 0/23 event rows are currently strict-eligible. Roughly 11/23 cutoffs have regime context, with high-frequency history only in 2026.\n- `NYC_OSE_ENFORCEMENT_REPORTS`: archive proven through annual 2016-2024 PDFs; permission pending; 0/23 event rows are currently strict-eligible. Annual cadence is weak.\n\n"
    memo += "## Prospective-only candidates\n\n`VANCOUVER_STR_LICENSES`, `NOLA_STR_PERMIT_EVENTS`, `NOLA_STR_ENFORCEMENT_HEARINGS`, `SAN_DIEGO_STRO_ACTIVE`, `FTA_NTD_MONTHLY_RIDERSHIP`, `MARINECADASTRE_AIS`, `NYC_311_TOURISM_STRESS`, and `MELB_PED_HOURLY` have present extracts or operational histories but no defensible historical publication-state reconstruction. They must start with timestamped prospective snapshots if permissions clear.\n\n`NASA_BLACK_MARBLE_VNP46A2`, `NOAA_HMS_SMOKE`, and `NPS_VISITOR_USE` are also classified `prospective_only` for E0 despite their source archives: NASA is pending `EARTHDATA_TOKEN` sync and a granule-version audit; NOAA is pending path permission and daily-file provenance; NPS lacks a preliminary-vintage solution, so the current API cannot reconstruct what was visible at each cutoff.\n\n"
    memo += "## Best three historical pilots\n\n"
    for sid in ("WSF_FERRY_RIDERSHIP", "ORANGE_FL_TDT_RELEASES", "NYC_OSE_STR_SNAPSHOTS"):
        row = next(item for item in candidates if item["source_id"] == sid)
        memo += f"### {sid}\n\nMechanism: {row['economic_mechanism']}\n\nPrimary formula: {PILOTS[sid][0]}\n\nSingle sensitivity: {PILOTS[sid][1]}\n\nBiggest failure: {row['biggest_failure_reason']}\n\nCoverage: {row['historical_guidance_cutoff_coverage']}\n\n"
    memo += "## Moonshot prospective collectors\n\n"
    memo += f"- `NASA_BLACK_MARBLE_VNP46A2`: {MOONSHOTS['NASA_BLACK_MARBLE_VNP46A2'][0]} Sensitivity: {MOONSHOTS['NASA_BLACK_MARBLE_VNP46A2'][1]} Main risk: radiance is not occupancy.\n"
    memo += f"- `MULTICITY_STR_PUBLIC_SNAPSHOT_MESH`: {MOONSHOTS['MULTICITY_STR_PUBLIC_SNAPSHOT_MESH'][0]} Sensitivity: {MOONSHOTS['MULTICITY_STR_PUBLIC_SNAPSHOT_MESH'][1]} Main risk: non-comparable municipal regimes and unresolved automated-access permission.\n\n"
    memo += "## Informational advantage and replication difficulty\n\nThe differentiated sources are operational by-products: route/fare ferry counts, individual dated tax releases, jurisdiction-specific permit workflows, manual smoke polygons, and quality-screened satellite tiles. Replication requires stable geography mappings, release-time archives, sensor/regime change ledgers, and lawful collector maintenance. Their strangeness alone earned no score.\n\n"
    memo += "## Credential and cost boundary\n\nOnly `EARTHDATA_TOKEN` would be required, with no value stored in this run. No credential was accessed. No paid source, paid trial, Bloomberg request, commercial booking engine, OTA, Airbnb-controlled property, or authenticated API was accessed.\n\n"
    memo += "## Required stop\n\nStop after E0 and wait for the user's source-selection decision. Do not preregister a target relationship, run a backtest, fit a model, or start a prospective collector.\n"
    (RUN_DIR / "source_selection_memo.md").write_text(memo, encoding="utf-8")

    prospective = HIERARCHY + "\n# Prospective collection opportunities\n\nNo collector was started. Every opportunity below remains gated.\n\n"
    prospective += "## 1. NASA Black Marble resort-activity residual\n\nPending `EARTHDATA_TOKEN`, path-specific robots evidence, and a collection/version audit. Fix destination and control polygons before collection; retain observation date, granule production time, collection version, quality masks, retrieval UTC, and checksum. Primary and sensitivity formulas are frozen in the source-selection memo only as proposed E1 inputs—not hypotheses.\n\n"
    prospective += "## 2. Multi-city official STR permit snapshot mesh\n\nUse only approved official public APIs for Vancouver, New Orleans, New York City, and San Diego. Query server-side aggregates or immediately aggregate on ingest; never retain names, exact addresses, unit numbers, contact information, listing URLs, free text, or tax identifiers. Snapshot daily at a fixed UTC time and retain schema, extract timestamp, jurisdiction rule version, checksum, and outage log. Do not combine cities until status definitions and renewal regimes are mapped.\n\n"
    prospective += "## Other watch-list collectors\n\n- NYC 311 tourism-stress aggregates: complaint-channel and enforcement-campaign drift make this control-heavy.\n- Melbourne pedestrian mesh: potentially excellent tourist-versus-commuter design, but portal terms are undefined.\n- San Diego active STRO: active-only and address-rich payload requires server-side projection/aggregation and forward snapshots.\n\n"
    prospective += "Dynamic current calendars can never be backfilled. Predictive alpha has not been tested.\n"
    (RUN_DIR / "prospective_collection_opportunities.md").write_text(prospective, encoding="utf-8")

    rejected = HIERARCHY + "\n# Rejected and inconclusive sources\n\n"
    rejected += "| Source | Decision | Evidence and failure reason |\n| --- | --- | --- |\n"
    rejected += "| `HAWAII_TAT_DISTRICT` / lane `SCW-007` | Rejected | Excellent dated 1997-2026 archive, but State terms explicitly prohibit automated access and commercial use absent separate written permission. Public visibility does not cure the rights problem. |\n"
    rejected += "| Recreation.gov availability / lane `SCW-009` | Rejected for E0 collection | No documented public availability API, no genuine historical snapshots, and no affirmative terms/robots permission. The observed route is undocumented and was not requested. |\n"
    rejected += "| Austin Active STR / lane `SCW-001` | Inconclusive | The historical chart's underlying query may be broken, deleted, or unpublished; no stable source ID or vintage semantics were established. |\n"
    rejected += "| `CDOT_CONTINUOUS_COUNTS` | Inconclusive | Resort-ingress mechanism is coherent, but exact licence, outage history, and historical publication timing were not established. |\n"
    rejected += "| `TFL_CYCLE_HIRE_TRIPS` | Inconclusive | Official open-data messaging conflicts with general Santander Cycles website extraction restrictions; applicability to the bulk bucket is unresolved. |\n"
    rejected += "| WSF Save A Spot availability | Rejected for automation | WSDOT's reservation policy restricts automated processes on the reservation site. No availability collector was attempted. |\n"
    rejected += "| Paid STR/app intelligence | Not reconsidered | No paid approval or licensed export was supplied; AirDNA, CoStar STR, Sensor Tower, data.ai, and Similarweb were not accessed. |\n\n"
    rejected += "No negative source decision was replaced with search-index values or an undocumented substitute. Predictive alpha has not been tested.\n"
    (RUN_DIR / "rejected_and_inconclusive_sources.md").write_text(rejected, encoding="utf-8")


def append_unique_csv(path: Path, id_field: str, rows: list[dict[str, str]]) -> None:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        existing = {row[id_field] for row in reader}
    new_rows = [row for row in rows if row[id_field] not in existing]
    if not new_rows:
        return
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        for row in new_rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def refresh_current_run_rows(path: Path, id_field: str, rows: list[dict[str, str]]) -> None:
    """Refresh only rows owned by this still-open run; preserve all prior rows."""
    replacements = {row[id_field]: row for row in rows}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        current = list(reader)
    changed = False
    for index, existing in enumerate(current):
        replacement = replacements.get(existing.get(id_field, ""))
        if replacement is None or RUN_ID not in existing.get("analyst_notes", ""):
            continue
        current[index] = {field: replacement.get(field, "") for field in fields}
        changed = True
    if changed:
        write_csv(path, fields, current)


def refresh_rows_by_id(path: Path, id_field: str, rows: list[dict[str, str]]) -> None:
    """Refresh rows with run-unique IDs while preserving every other row."""
    replacements = {row[id_field]: row for row in rows}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        current = list(reader)
    changed = False
    for index, existing in enumerate(current):
        replacement = replacements.get(existing.get(id_field, ""))
        if replacement is None:
            continue
        current[index] = {field: replacement.get(field, "") for field in fields}
        changed = True
    if changed:
        write_csv(path, fields, current)


def update_canonical_registries(candidates: list[dict[str, str]], scores: list[dict[str, str]], permissions: list[dict[str, str]]) -> None:
    score_by_id = {row["source_id"]: row for row in scores}
    source_rows = []
    for candidate in candidates:
        sid = candidate["source_id"]
        source_rows.append({
            "rank": str(21 + int(candidate["rank"])),
            "source_id": sid,
            "dataset": candidate["dataset"], "provider": candidate["provider"],
            "economic_mechanism": candidate["economic_mechanism"], "source_url": candidate["exact_source_urls"],
            "access_method": candidate["access_method"], "license": candidate["license_or_reuse"],
            "collection_restrictions": candidate["collection_restrictions"], "geographic_coverage": candidate["geographic_coverage"],
            "unit_of_observation": candidate["unit_of_observation"], "frequency": candidate["frequency"],
            "history_start": HISTORY_START[sid], "history_end": "",
            "publication_schedule": candidate["publication_schedule_and_lag"], "publication_lag": candidate["publication_schedule_and_lag"],
            "revision_policy": candidate["revision_or_snapshot_policy"], "vintage_available": candidate["true_vintage_support"],
            "cost": candidate["cost"], "collection_timestamp_utc": candidate["collection_timestamp_utc"],
            "pit_evidence": candidate["earliest_verifiable_public_availability"] + "; " + candidate["historical_guidance_cutoff_coverage"],
            "leakage_risk": candidate["point_in_time_leakage_risk"], "leakage_mitigation": candidate["leakage_mitigation"],
            "status": candidate["status"], "citations": candidate["citations"],
            "analyst_notes": f"Phase E0 rank {candidate['rank']}; ex-ante score {score_by_id[sid]['total_100']}/100; historical class {candidate['historical_class']}; strict_cutoff_eligible_now=false; predictive alpha not tested; run {RUN_ID}.",
        })
    append_unique_csv(ROOT / "research" / "source_registry.csv", "source_id", source_rows)
    refresh_current_run_rows(ROOT / "research" / "source_registry.csv", "source_id", source_rows)

    api_rows = [
        {"rank": "19", "api_id": "NPS_VUSTATS_REST", "provider": "National Park Service", "api_name": "Visitor Use Statistics REST service", "research_use": "Park-level realized visitor presence", "economic_mechanism": "Monthly recreation visits and overnight categories proxy leisure presence near park gateways", "docs_url": "https://irmaservices.nps.gov/v3/rest/Stats/help", "signup_url": "", "base_url": "https://irmaservices.nps.gov/v3/rest/stats/", "authentication": "none", "env_var_names": "", "free_tier": "Public federal API", "rate_limit": "Unverified; autonomous plan capped at 1 request/minute", "history_start": "1979-01-01", "history_end": "", "frequency": "monthly", "geographic_coverage": "More than 400 U.S. national parks", "publication_lag": "Preliminary generally by 15th of following month; annual finalization in following Q1", "revision_policy": "Preliminary values revise until finalization", "vintage_support": "No public vintage endpoint found", "license": "U.S. federal public data", "collection_restrictions": "Robots path unresolved; no request made", "cost": "Free", "terms_url": "https://www.doi.gov/copyright", "last_reviewed_at_utc": COLLECTED_AT, "linked_source_ids": "NPS_VISITOR_USE", "status": "pending_permission", "citations": "https://irmaservices.nps.gov/v3/rest/Stats/help; https://home.nps.gov/subjects/socialscience/statistics-faq.htm", "analyst_notes": "Current finalized history is not a historical vintage."},
        {"rank": "20", "api_id": "NASA_LAADS_V2", "provider": "NASA LAADS DAAC", "api_name": "LAADS archive/content API", "research_use": "Black Marble granule metadata and files", "economic_mechanism": "Nighttime radiance residuals may proxy resort activity", "docs_url": "https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/", "signup_url": "https://urs.earthdata.nasa.gov/", "base_url": "https://ladsweb.modaps.eosdis.nasa.gov/api/v2/", "authentication": "Earthdata token", "env_var_names": "EARTHDATA_TOKEN", "free_tier": "Free Earthdata Login", "rate_limit": "Provider guidance; E0 proposed 1 request/minute", "history_start": "2012-01-01", "history_end": "", "frequency": "daily", "geographic_coverage": "Global land surface", "publication_lag": "Granule-specific; must be verified", "revision_policy": "Collections can be reprocessed", "vintage_support": "Granule production metadata may support version audit", "license": "NASA open-data policy", "collection_restrictions": "No access before user confirms credential sync; robots unresolved", "cost": "Free", "terms_url": "https://www.earthdata.nasa.gov/engage/open-data-services-and-software/data-and-information-policy", "last_reviewed_at_utc": COLLECTED_AT, "linked_source_ids": "NASA_BLACK_MARBLE_VNP46A2", "status": "pending_sync", "citations": "https://urs.earthdata.nasa.gov/documentation/what_do_i_need_to_know; https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5000/VNP46A2/", "analyst_notes": "Do not log token-bearing headers or URLs."},
        {"rank": "21", "api_id": "NOLA_SODA", "provider": "City of New Orleans", "api_name": "Socrata SODA API", "research_use": "STR permits and adjudication events", "economic_mechanism": "Permit and enforcement event flow may measure supply and regulatory friction", "docs_url": "https://dev.socrata.com/foundry/data.nola.gov/en36-xvxg", "signup_url": "", "base_url": "https://data.nola.gov/resource/", "authentication": "none for small public queries", "env_var_names": "", "free_tier": "Public API", "rate_limit": "Provider-dependent; E0 proposed 6 requests/minute", "history_start": "2017-05-04", "history_end": "", "frequency": "event-driven", "geographic_coverage": "New Orleans", "publication_lag": "Unverified", "revision_policy": "Current status can overwrite; event rows may backfill", "vintage_support": "No snapshot archive established", "license": "Portal public-data policy unresolved for exact paths", "collection_restrictions": "Terms and robots unresolved; no direct request; aggregate only", "cost": "Free", "terms_url": "https://data.nola.gov/stories/s/Data-Policy-Annual-Report-2017/6a26-q6dq/", "last_reviewed_at_utc": COLLECTED_AT, "linked_source_ids": "NOLA_STR_PERMIT_EVENTS; NOLA_STR_ENFORCEMENT_HEARINGS", "status": "pending_permission", "citations": "https://data.nola.gov/Housing-Land-Use-and-Blight/Map-of-Short-Term-Rental-License-Applications/j5u3-2ueh; https://data.nola.gov/Housing-Land-Use-and-Blight/Adjudication-Enforcement-Detailed-Hearings-Data-fo/uzyk-jrck", "analyst_notes": "Project only aggregate event dates and categories; no addresses or identifiers."},
        {"rank": "22", "api_id": "VANCOUVER_OPENDATASOFT", "provider": "City of Vancouver", "api_name": "OpenDataSoft Explore API v2.1", "research_use": "Short-term rental business licence events", "economic_mechanism": "Issue, expiry, revision, and status fields may measure legal supply", "docs_url": "https://opendata.vancouver.ca/explore/dataset/business-licences/api/", "signup_url": "", "base_url": "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/", "authentication": "none", "env_var_names": "", "free_tier": "Public API", "rate_limit": "Provider-dependent; E0 proposed 6 requests/minute", "history_start": "", "history_end": "", "frequency": "current extract", "geographic_coverage": "Vancouver", "publication_lag": "Extract-specific", "revision_policy": "Current extract with historical event dates and revisions", "vintage_support": "No historical extract archive established", "license": "Open Government Licence–Vancouver", "collection_restrictions": "Robots path unresolved; no direct request; exclude names/addresses", "cost": "Free", "terms_url": "https://vancouver.ca/your-government/terms-of-use.aspx", "last_reviewed_at_utc": COLLECTED_AT, "linked_source_ids": "VANCOUVER_STR_LICENSES", "status": "pending_permission", "citations": "https://opendata.vancouver.ca/explore/dataset/business-licences/api/; https://vancouver.ca/your-government/terms-of-use.aspx", "analyst_notes": "Present extract is not a historical vintage."},
        {"rank": "23", "api_id": "SAN_DIEGO_STRO_ARCGIS", "provider": "City of San Diego", "api_name": "STRO Active Licences ArcGIS REST service", "research_use": "Prospective legal STR supply snapshots", "economic_mechanism": "Tier and planning-area active licence counts measure permitted capacity", "docs_url": "https://webmaps.sandiego.gov/arcgis/rest/services/Treasurer/STRO_ACTIVE_LICENSES/MapServer", "signup_url": "", "base_url": "https://webmaps.sandiego.gov/arcgis/rest/services/Treasurer/STRO_ACTIVE_LICENSES/MapServer", "authentication": "none", "env_var_names": "", "free_tier": "Public service", "rate_limit": "Unverified; E0 proposed 6 requests/minute", "history_start": "2023-01-19", "history_end": "", "frequency": "current snapshot", "geographic_coverage": "San Diego", "publication_lag": "Unverified", "revision_policy": "Active-only overwritten state", "vintage_support": "None", "license": "City open-data terms allow use and redistribution", "collection_restrictions": "Robots unresolved; aggregate on ingest; exclude names, contacts, addresses, and tax IDs", "cost": "Free", "terms_url": "https://data.sandiego.gov/help/guides/terms/", "last_reviewed_at_utc": COLLECTED_AT, "linked_source_ids": "SAN_DIEGO_STRO_ACTIVE", "status": "prospective_only", "citations": "https://data.sandiego.gov/datasets/stro-licenses/; https://data.sandiego.gov/help/guides/terms/", "analyst_notes": "Never backfill historical active supply from the present snapshot."},
    ]
    append_unique_csv(ROOT / "research" / "free_api_registry.csv", "api_id", api_rows)

    audit_rows = []
    for index, permission in enumerate(permissions, start=1):
        audit_rows.append({
            "audit_id": f"SA-20260903-E{index:03d}", "source_id": permission["source_id"],
            "domain": permission["domain"], "intended_paths": permission["intended_paths"],
            "collection_purpose": "Phase E0 tiny schema/provenance validation only",
            "terms_url": permission["terms_url"], "robots_url": permission["robots_url"],
            "reviewed_at_utc": permission["reviewed_at_utc"], "terms_status": permission["terms_status"],
            "robots_status": permission["robots_status"], "authenticated": str(not permission["authentication"].lower().startswith("none")).lower(),
            "paywalled": "false", "captcha_required": "false", "access_control_bypass": "false",
            "personal_data": "false", "airbnb_controlled": "false", "explicit_automation_permission": "false",
            "rate_limit_per_minute": permission["rate_limit_per_minute"], "cache_policy": permission["cache_policy"],
            "user_agent": "ABNB-Edge-Research/1.0 (institutional research; contact: repository-owner)",
            "collection_allowed": "false", "decision_reason": permission["decision_reason"],
            "selector_or_endpoint": permission["intended_paths"], "collected_at_utc": "", "artifact_path": "", "sha256": "",
            "status": "blocked_preflight_no_request", "citations": permission["citations"],
        })
    append_unique_csv(ROOT / "research" / "scraping_audit.csv", "audit_id", audit_rows)
    refresh_rows_by_id(ROOT / "research" / "scraping_audit.csv", "audit_id", audit_rows)


def main() -> None:
    scores = score_rows()
    candidates = candidate_rows(scores)
    permissions = permission_rows(candidates)
    archives = archive_rows(candidates)
    tiny = tiny_rows(candidates, permissions)

    candidate_fields = [
        "rank", "source_id", "lane_source_id", "research_lane", "dataset", "provider", "edge_family",
        "economic_mechanism", "predicted_direction", "potential_abnb_target", "measurement_type", "why_underused",
        "geographic_coverage", "plausible_abnb_materiality", "unit_of_observation", "granularity", "frequency", "history",
        "publication_schedule_and_lag", "earliest_verifiable_public_availability", "revision_or_snapshot_policy",
        "true_vintage_support", "access_method", "exact_source_urls", "terms_url", "robots_url", "credential_requirement",
        "environment_variables", "cost", "license_or_reuse", "collection_restrictions",
        "sensor_methodology_survivorship_risks", "point_in_time_leakage_risk", "leakage_mitigation",
        "historical_guidance_cutoff_coverage", "strict_cutoff_eligible_now", "smallest_lawful_validation_sample", "status",
        "historical_class", "selected_historical_pilot", "selected_moonshot", "primary_feature_formula_if_selected",
        "sensitivity_if_selected", "biggest_failure_reason", "ex_ante_score_100", "citations", "collection_timestamp_utc", "analyst_notes",
    ]
    score_fields = [
        "rank", "source_id", "lane_source_id", "research_lane", "causal_proximity_20", "pit_vintage_defensibility_20",
        "differentiation_underuse_15", "geographic_scalability_15", "frequency_lead_time_10",
        "permission_license_clarity_10", "operational_reliability_5", "free_low_cost_5", "total_100", "status",
        "historical_class", "score_rationale",
    ]
    permission_fields = [
        "source_id", "lane_source_id", "domain", "exact_source_url", "intended_paths", "terms_url", "terms_status",
        "robots_url", "robots_status", "license_or_reuse", "authentication", "personal_data_plan", "rate_limit_per_minute",
        "cache_policy", "collection_allowed", "decision_reason", "reviewed_at_utc", "direct_requests_made", "citations",
    ]
    archive_fields = [
        "source_id", "history_claim", "earliest_verifiable_public_availability", "archive_or_vintage_evidence",
        "record_behavior", "real_vintage_support", "historical_guidance_cutoff_coverage_estimate",
        "strict_cutoff_eligible_now", "reason",
    ]
    tiny_fields = [
        "source_id", "planned_endpoint_or_file", "planned_request_count", "actual_request_count", "collection_utc",
        "http_status", "response_checksum", "cache_path", "selectors_or_fields", "decision", "stop_reason",
    ]

    write_csv(RUN_DIR / "candidate_edge_registry.csv", candidate_fields, candidates)
    write_csv(RUN_DIR / "edge_scorecard.csv", score_fields, scores)
    write_csv(RUN_DIR / "permission_and_license_audit.csv", permission_fields, permissions)
    write_csv(RUN_DIR / "historical_archive_matrix.csv", archive_fields, archives)
    write_csv(RUN_DIR / "tiny_sample_manifest.csv", tiny_fields, tiny)
    write_reports(candidates, scores)
    update_canonical_registries(candidates, scores, permissions)


if __name__ == "__main__":
    main()
