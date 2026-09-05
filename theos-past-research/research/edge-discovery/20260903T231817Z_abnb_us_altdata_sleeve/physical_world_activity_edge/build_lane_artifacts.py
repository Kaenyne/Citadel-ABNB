"""Build governed source-side artifacts for the physical-activity lane."""

from __future__ import annotations

import csv
import hashlib
import json
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path

from abnb_alt_data.scraping_policy import ScrapeCandidate, assess_scrape_candidate


HERE = Path(__file__).resolve().parent
UA = "ABNB-US-altdata-research/0.1 (+https://github.com/theomachado05/airbnb-citadel-2026)"
ASSESSED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


specs = [
    dict(source_id="TSA_CHECKPOINT", exact_source_url="https://www.tsa.gov/travel/passenger-volumes", terms_url="https://www.tsa.gov/terms-and-conditions", terms_status="unclear", robots_url="https://www.tsa.gov/robots.txt", robots_status="unclear", intended_paths=("/travel/passenger-volumes?page=0",), evidence="PERM-US-001 returned provider HTTP 403; the terms request was not issued after the stop."),
    dict(source_id="FHWA_TVT_VMT", exact_source_url="https://www.fhwa.dot.gov/policyinformation/travel_monitoring/tvt.cfm", terms_url="https://www.transportation.gov/data", terms_status="unclear", robots_url="https://www.fhwa.dot.gov/robots.txt", robots_status="disallowed", intended_paths=("/policyinformation/travel_monitoring/26jultvt/26jultvt.xlsx",), evidence="PERM-US-009 explicitly Disallow: /policyinformation/travel_monitoring/ and Allow only tvt.cfm; it does not allow the workbook. No terms text explicitly authorizing automation was retrieved."),
    dict(source_id="BTS_T100", exact_source_url="https://www.bts.gov/browse-statistical-products-and-data/db20", terms_url="https://www.transportation.gov/data", terms_status="unclear", robots_url="https://www.bts.gov/robots.txt", robots_status="unclear", intended_paths=("/browse-statistical-products-and-data/db20", "/sites/bts.dot.gov/files/2026-08/DB20*.zip"), evidence="TranStats robots returned HTTP 404 and BTS robots returned provider HTTP 403; remaining terms/metadata requests were not issued after the stop."),
    dict(source_id="NPS_VISITOR_USE", exact_source_url="https://irmaservices.nps.gov/v3/rest/Stats/help", terms_url="https://www.doi.gov/copyright", terms_status="allowed", robots_url="https://irmaservices.nps.gov/robots.txt", robots_status="disallowed", intended_paths=("/v3/rest/stats/visitation?unitCodes=YELL&startMonth=1&startYear=2025&endMonth=1&endYear=2025",), evidence="REUSE-US-001 says User-agent: * and Disallow: /; DOI public-domain and API documentation evidence is otherwise affirmative."),
    dict(source_id="FTA_NTD_MONTHLY_RIDERSHIP", exact_source_url="https://www.transit.dot.gov/ntd/monthly-ridership", terms_url="https://www.transportation.gov/data", terms_status="unclear", robots_url="https://www.transit.dot.gov/robots.txt", robots_status="unclear", intended_paths=("/ntd/data-product/raw-monthly-ridership-no-adjustments-or-estimates",), evidence="REUSE-US-005 is provider HTTP 403; exact-path robots guidance and automation permission remain unresolved."),
    dict(source_id="SFO_AIR_PASSENGERS", exact_source_url="https://data.sfgov.org/Transportation/Air-Traffic-Passenger-Statistics/rkru-6vcg", terms_url="https://data.sfgov.org/terms-of-use", terms_status="allowed", robots_url="https://data.sfgov.org/robots.txt", robots_status="unclear", intended_paths=("/resource/rkru-6vcg.json?$select=activity_period,geo_summary,activity_type_code,sum(passenger_count)&$group=activity_period,geo_summary,activity_type_code",), evidence="No new request. Governed aggregate cache reuse was canonically authorized, but no same-day exact robots evidence affirmatively allows a new request; silence is not allowance."),
    dict(source_id="PANYNJ_AIRPORT_PARKING", exact_source_url="https://data.ny.gov/resource/h87k-kqb6.json", terms_url="https://data.ny.gov/api/views/77gx-ii52/files/ef0c1840-ad54-4240-92fd-6397c49fde46?filename=OPEN-NY_20Terms_20of_20Use.pdf", terms_status="unclear", robots_url="https://data.ny.gov/robots.txt", robots_status="unclear", intended_paths=("/resource/h87k-kqb6.json?$select=year,quarter,airport,count&$order=year,quarter,airport",), evidence="OPEN-NY invites lawful content download and reuse but does not clearly authorize this automated path; robots has Crawl-delay and unrelated disallows but no explicit Allow for /resource. Silence is not affirmative allowance."),
    dict(source_id="LAX_TERMINAL_PASSENGERS", exact_source_url="https://data.lacity.org/resource/g3qu-7q2u.json", terms_url="https://data.lacity.org/terms-of-use", terms_status="unclear", robots_url="https://data.lacity.org/robots.txt", robots_status="unclear", intended_paths=("/resource/g3qu-7q2u.json?$select=reportperiod,terminal,arrival_departure,sum(passenger_count)&$group=reportperiod,terminal,arrival_departure",), evidence="Robots has Crawl-delay and unrelated disallows but no explicit Allow for /resource; the official terms page triggered the conservative human-verification marker stop and metadata was not requested."),
]

gate_rows: list[dict[str, object]] = []
for spec in specs:
    candidate = ScrapeCandidate(
        source_id=spec["source_id"], public_access=True,
        terms_url=spec["terms_url"], terms_status=spec["terms_status"],
        robots_url=spec["robots_url"], robots_status=spec["robots_status"],
        intended_paths=spec["intended_paths"], authenticated=False, paywalled=False,
        captcha_required=False, access_control_bypass=False, personal_data=False,
        airbnb_controlled=False, explicit_airbnb_automation_permission=False,
        requests_per_minute=9, cache_responses=True, user_agent=UA,
    )
    decision = assess_scrape_candidate(candidate)
    gate_rows.append({
        "source_id": spec["source_id"], "exact_source_url": spec["exact_source_url"],
        "terms_url": spec["terms_url"], "terms_status": spec["terms_status"],
        "robots_url": spec["robots_url"], "robots_status": spec["robots_status"],
        "intended_paths": "|".join(spec["intended_paths"]), "public_access": "true",
        "authenticated": "false", "paywalled": "false", "captcha_required": "false",
        "access_control_bypass": "false", "personal_data": "false",
        "requests_per_minute": 9, "cache_responses": "true", "user_agent": UA,
        "assessment_allowed": str(decision.allowed).lower(),
        "assessment_reasons": " | ".join(decision.reasons), "assessed_at_utc": ASSESSED_AT,
        "evidence_note": spec["evidence"],
    })

gate_fields = ["source_id", "exact_source_url", "terms_url", "terms_status", "robots_url", "robots_status", "intended_paths", "public_access", "authenticated", "paywalled", "captcha_required", "access_control_bypass", "personal_data", "requests_per_minute", "cache_responses", "user_agent", "assessment_allowed", "assessment_reasons", "assessed_at_utc", "evidence_note"]
write_csv(HERE / "exact_path_gate_decisions.csv", gate_fields, gate_rows)

# No candidate passed, so canonical scraping-audit approval and new data requests were unnecessary.
write_csv(HERE / "proposed_scraping_audit.csv", ["source_id", "exact_source_url", "intended_paths", "terms_url", "robots_url", "assessment_allowed", "proposed_status", "notes"], [])
write_csv(HERE / "data_probe_manifest.csv", ["probe_id", "source_id", "exact_url", "purpose", "registered_at_utc", "canonical_scraping_audit_confirmed"], [])
write_csv(HERE / "data_probe_results.csv", ["probe_id", "source_id", "requested_at_utc", "http_status", "content_type", "bytes", "sha256", "cached_path", "outcome"], [])

# Normalize the already-governed SFO aggregate cache. These are current-snapshot rows,
# never historical vintages; all retrospective PIT eligibility is therefore false.
raw_path = HERE / "raw_cache" / "source_reused" / "sfo_air_passengers_aggregate.json"
raw = json.loads(raw_path.read_text(encoding="utf-8"))
obs: list[dict[str, object]] = []
for row in raw:
    period = row["activity_period"]
    if not ("202101" <= period <= "202606"):
        continue
    year, month = int(period[:4]), int(period[4:])
    reference = f"{year:04d}-{month:02d}"
    obs_date = f"{reference}-{monthrange(year, month)[1]:02d}"
    key = "|".join(("SFO_AIR_PASSENGERS", period, row["geo_summary"], row["activity_type_code"]))
    obs.append({
        "observation_id": hashlib.sha256(key.encode()).hexdigest()[:20],
        "source_id": "SFO_AIR_PASSENGERS", "provider": "City and County of San Francisco",
        "dataset": "Air Traffic Passenger Statistics", "observation_date": obs_date,
        "reference_period": reference, "geography": "San Francisco International Airport",
        "geo_segment": row["geo_summary"], "metric": row["activity_type_code"],
        "value": int(row["passenger_count"]), "unit": "passengers", "frequency": "monthly",
        "initial_publication_timestamp_utc": "", "revision_timestamp_utc": row["data_as_of"] + "Z",
        "vintage": "current_snapshot_data_as_of_2026-08-20",
        "source_loaded_at_utc": row["data_loaded_at"] + "Z",
        "collection_timestamp_utc": "2026-09-03T20:50:50Z",
        "strict_pit_eligible": "false",
        "pit_ineligibility_reason": "Initial historical publication timestamp and original vintage were not recovered; cached payload is an August 2026 current snapshot.",
        "raw_cache_path": "raw_cache/source_reused/sfo_air_passengers_aggregate.json",
        "raw_sha256": "5f10170b56cdb5b963478dc5347584a3194b477f3bd79ef5380d83fe00f591b4",
    })

obs_fields = ["observation_id", "source_id", "provider", "dataset", "observation_date", "reference_period", "geography", "geo_segment", "metric", "value", "unit", "frequency", "initial_publication_timestamp_utc", "revision_timestamp_utc", "vintage", "source_loaded_at_utc", "collection_timestamp_utc", "strict_pit_eligible", "pit_ineligibility_reason", "raw_cache_path", "raw_sha256"]
write_csv(HERE / "observations_long.csv", obs_fields, obs)

vintage_rows = [
    {"source_id":"TSA_CHECKPOINT","publication_schedule":"Updated Monday-Friday by 09:00 ET; holidays may delay","publication_lag":"Usually next morning","revision_policy":"Mutable table may be corrected or repaginated","vintage_evidence":"No immutable historical publication timestamps established","pit_status":"not_collected_permission_blocked","eligible_observations":0,"limitation":"TSA robots request returned provider HTTP 403."},
    {"source_id":"FHWA_TVT_VMT","publication_schedule":"Monthly; official FAQ says available within 60 days after month close","publication_lag":"<=60 days per official FAQ","revision_policy":"Continuously updated with additional state data and annually re-adjusted to HPMS","vintage_evidence":"Dated monthly files exist, but workbook path is robots-disallowed and exact first-publication timestamps were not collected","pit_status":"not_collected_permission_blocked","eligible_observations":0,"limitation":"Robots permits only tvt.cfm inside the disallowed directory, not XLS/XLSX payloads."},
    {"source_id":"BTS_T100","publication_schedule":"Monthly","publication_lag":"Typically 2-3 months","revision_policy":"Carrier submissions and prior months may be revised","vintage_evidence":"No true vintage API established; dated DB20 artifacts were not reached after provider stop","pit_status":"not_collected_permission_blocked","eligible_observations":0,"limitation":"TranStats robots 404 and BTS robots 403 leave exact-path permission unresolved."},
    {"source_id":"NPS_VISITOR_USE","publication_schedule":"Preliminary monthly data generally by the 15th of next month","publication_lag":"About 15 days","revision_policy":"Editable until calendar-year finalization in following Q1","vintage_evidence":"No public API vintage endpoint identified","pit_status":"not_collected_permission_blocked","eligible_observations":0,"limitation":"Robots explicitly Disallow: /."},
    {"source_id":"FTA_NTD_MONTHLY_RIDERSHIP","publication_schedule":"First full week, normally 4th-7th","publication_lag":"About two months","revision_policy":"Current raw file can overwrite corrected history","vintage_evidence":"No dated release-vintage archive identified","pit_status":"not_collected_permission_blocked","eligible_observations":0,"limitation":"Provider robots request returned HTTP 403."},
    {"source_id":"SFO_AIR_PASSENGERS","publication_schedule":"Mutable SODA dataset; cadence not independently reconstructed","publication_lag":"Unknown historically","revision_policy":"Current snapshot may revise historical rows","vintage_evidence":"Cached rows share data_as_of 2026-08-20 and data_loaded_at 2026-08-22; no original monthly vintages","pit_status":"prospective_only_current_snapshot","eligible_observations":0,"limitation":"384 normalized 2021-2026 rows are explicitly strict_pit_eligible=false."},
    {"source_id":"PANYNJ_AIRPORT_PARKING","publication_schedule":"Quarterly; metadata updated 2026-04-15","publication_lag":"Exact lag not established","revision_policy":"Current SODA dataset may revise history","vintage_evidence":"Metadata dates the dataset and latest update, not original row-level vintages","pit_status":"not_collected_permission_unclear","eligible_observations":0,"limitation":"Terms and exact /resource robots permission are not affirmative."},
    {"source_id":"LAX_TERMINAL_PASSENGERS","publication_schedule":"Not recovered after terms-page stop","publication_lag":"Unknown","revision_policy":"City terms state older versions are not retained and data can be updated, corrected, overwritten, or refreshed","vintage_evidence":"No row-level historical publication vintages recovered","pit_status":"not_collected_permission_unclear","eligible_observations":0,"limitation":"Terms stop and robots silence for /resource; metadata request not made."},
]
write_csv(HERE / "publication_vintage_audit.csv", ["source_id","publication_schedule","publication_lag","revision_policy","vintage_evidence","pit_status","eligible_observations","limitation"], vintage_rows)

dispositions = [
    {"source_id":"TSA_CHECKPOINT","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_provider_stop","source_rows":0,"strict_pit_eligible_rows":0,"reason":"HTTP 403 on robots; no exact-path permission."},
    {"source_id":"FHWA_TVT_VMT","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_robots_disallowed","source_rows":0,"strict_pit_eligible_rows":0,"reason":"Workbook directory explicitly disallowed; index-only Allow does not extend to payloads."},
    {"source_id":"BTS_T100","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_provider_stop","source_rows":0,"strict_pit_eligible_rows":0,"reason":"Robots unresolved after 404/403; no payload."},
    {"source_id":"NPS_VISITOR_USE","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_robots_disallowed","source_rows":0,"strict_pit_eligible_rows":0,"reason":"Exact robots says Disallow: /."},
    {"source_id":"FTA_NTD_MONTHLY_RIDERSHIP","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_provider_stop","source_rows":0,"strict_pit_eligible_rows":0,"reason":"Robots request 403; permission unresolved."},
    {"source_id":"SFO_AIR_PASSENGERS","disposition":"WATCH_PROSPECTIVELY","collection_outcome":"reused_governed_current_snapshot","source_rows":len(obs),"strict_pit_eligible_rows":0,"reason":"Useful aggregate monthly history, but all rows are current-snapshot observations unavailable for retrospective PIT testing."},
    {"source_id":"PANYNJ_AIRPORT_PARKING","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_permission_unclear","source_rows":0,"strict_pit_eligible_rows":0,"reason":"Neither terms nor robots affirmatively authorizes the exact automated /resource request."},
    {"source_id":"LAX_TERMINAL_PASSENGERS","disposition":"INCONCLUSIVE","collection_outcome":"not_collected_provider_stop","source_rows":0,"strict_pit_eligible_rows":0,"reason":"Terms page triggered conservative stop; robots does not explicitly Allow /resource."},
]
write_csv(HERE / "source_dispositions.csv", ["source_id","disposition","collection_outcome","source_rows","strict_pit_eligible_rows","reason"], dispositions)

assert len(obs) == 384
assert len({r["observation_id"] for r in obs}) == len(obs)
assert all(r["strict_pit_eligible"] == "false" for r in obs)
assert sum(r["assessment_allowed"] == "true" for r in gate_rows) == 0

validation = {
    "run_id": "20260903T231817Z_abnb_us_altdata_sleeve",
    "lane": "physical_world_activity_edge", "validated_at_utc": ASSESSED_AT,
    "candidate_count": 8, "permission_manifest_rows": 17, "permission_provider_gets": 11,
    "permission_completed": 7, "permission_provider_stops": 3, "permission_other_http_error": 1,
    "permission_not_requested_after_stop": 6, "reused_permission_evidence_rows": 5,
    "exact_path_gate_count": len(gate_rows), "exact_path_allowed_count": 0,
    "new_data_probe_manifest_rows": 0, "new_data_provider_gets": 0,
    "sfo_reused_raw_files": 2, "observation_rows": len(obs), "strict_pit_eligible_rows": 0,
    "checks": {"sfo_row_count_384": True, "unique_observation_ids": True, "all_sfo_rows_prospective_only": True, "no_allowed_data_path": True, "no_abnb_outcomes_opened": True},
    "status": "PASS",
}
(HERE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
