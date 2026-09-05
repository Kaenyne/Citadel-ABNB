#!/usr/bin/env python3
"""Build the governed permission-resolution continuation artifacts.

This script is intentionally deterministic.  It only reconciles already-cached
lane evidence; it never performs a network request.  Canonical edits are
idempotent and preserve existing rows and schemas.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
OUT = RUN / "permission_resolution"
PW = RUN / "physical_world_activity_edge" / "permission_resolution"
SCW = RUN / "supply_scarcity_web_edge" / "permission_resolution"
RECONCILED_AT = "2026-09-03T17:15:18Z"
RUN_ID = "20260903T062839Z_abnb_edge_discovery"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


candidate_rows = read_csv(RUN / "candidate_edge_registry.csv")
rank = {row["source_id"]: row["rank"] for row in candidate_rows}
final_ids = [row["source_id"] for row in candidate_rows]
assert len(final_ids) == 15 and len(set(final_ids)) == 15

decision_rows = read_csv(RUN / "phase_e1" / "source_approval_and_disposition.csv")
decision_by_id = {row["source_id"]: row for row in decision_rows}

# Lead-level determinations.  Robots silence is always ``unclear`` in this run,
# even where the REP would ordinarily permit an unlisted path.
gates: dict[str, dict[str, object]] = {
    "NASA_BLACK_MARBLE_VNP46A2": dict(terms="unclear", robots="unclear", auth=True, captcha=False, personal=False, path="/archive/allData/5000/VNP46A2/ | /api/v2/content/details?products=VNP46A2", reason="Earthdata authentication remains separately blocked; robots redirected to login and the policy GET returned 403; no credential or payload access."),
    "NOAA_HMS_SMOKE": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=False, path="/products/land/hms.html | /pub/FIRE/web/HMS/Smoke_Polygons/Shapefile/Annual_Bundles/", reason="Robots gave no affirmative exact-path allowance; the shared NOAA policy GET returned 403; original daily-file vintages remain unresolved."),
    "WSF_FERRY_RIDERSHIP": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=False, path="/travel/washington-state-ferries/about-us/ferries-accountability-and-service-data/ridership-data | /sites/default/files/<dated-quarterly-report>.pdf", reason="WSDOT open-data language supports public access but not automated retrieval; robots does not explicitly allow the paths; exact initial-publication timing remains unverified."),
    "NYC_OSE_STR_SNAPSHOTS": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=True, path="/assets/specialenforcement/downloads/excel/<dated-registration-dataset>.xlsx", reason="Terms do not authorize automation, robots is silent, the workbook contains unit-level identifiers, and no historical snapshot panel is verified."),
    "ORANGE_FL_TDT_RELEASES": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=False, path="/Archive.aspx?AMID=56 | /DocumentCenter/View/<monthly-report-id>/<monthly-report>.pdf", reason="No affirmative automation terms or robots allowance; report-level first-publication timestamps remain unverified."),
    "VANCOUVER_STR_LICENSES": dict(terms="unclear", robots="disallowed", auth=False, captcha=True, personal=True, path="/api/explore/v2.1/catalog/datasets/business-licences/records", reason="Terms GET returned 403, robots explicitly disallows /api/, metadata triggered CAPTCHA, and the registered query could transport address-level fields."),
    "NPS_VISITOR_USE": dict(terms="allowed", robots="disallowed", auth=False, captcha=False, personal=False, path="/v3/rest/stats/visitation", reason="DOI reuse terms are permissive, but official robots says Disallow: /; the current API also lacks release vintages."),
    "NYC_OSE_ENFORCEMENT_REPORTS": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=False, path="/assets/specialenforcement/downloads/excel/<annual-enforcement-report>.xlsx", reason="Public/research-use language is not automation permission, robots is silent, and first-publication timestamps remain unverified."),
    "FTA_NTD_MONTHLY_RIDERSHIP": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=False, path="/ntd/monthly-ridership | /ntd/data-product/<raw-monthly-file>", reason="Robots GET returned 403 and the source stop prevented policy, metadata, calendar, and data requests; release vintages remain unverified."),
    "NOLA_STR_PERMIT_EVENTS": dict(terms="unclear", robots="unclear", auth=False, captcha=True, personal=False, path="/resource/en36-xvxg.json", reason="Policy page is not automation terms, robots is silent, metadata triggered CAPTCHA, the live UID differed, and publication timing is unverified."),
    "NOLA_STR_ENFORCEMENT_HEARINGS": dict(terms="unclear", robots="unclear", auth=False, captcha=True, personal=False, path="/resource/uzyk-jrck.json", reason="No automation terms or affirmative robots allowance; the NOLA host stop prevented metadata and payload access; PIT timing is unverified."),
    "SAN_DIEGO_STRO_ACTIVE": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=True, path="https://seshat.datasd.org/stro_licenses/stro_licenses_datasd.csv", reason="Terms permit data use but not automation, exact-host robots is unresolved, and the bulk file cannot exclude address, host-contact, and tax fields before transport."),
    "MARINECADASTRE_AIS": dict(terms="unclear", robots="unclear", auth=False, captcha=False, personal=False, path="/ais/ | /accessais/", reason="The shared NOAA policy GET returned 403 and the source stop prevented robots and metadata requests; release/vintage evidence remains unresolved."),
    "NYC_311_TOURISM_STRESS": dict(terms="allowed", robots="unclear", auth=False, captcha=False, personal=False, path="/resource/erm2-nwe9.json?$select=count(*) as request_count&$where=<one-day-window>", reason="Robots has no explicit Allow for /resource. One aggregate request occurred under a superseded lane interpretation; the payload is quarantined and excluded from all research use."),
    "MELB_PED_HOURLY": dict(terms="unclear", robots="disallowed", auth=False, captcha=True, personal=False, path="/api/explore/v2.1/catalog/datasets/pedestrian-counting-system-monthly-counts-per-hour/records", reason="Robots explicitly disallows /api/, terms are undefined, the terms response triggered a CAPTCHA marker, and current history is not a vintage archive."),
}
assert set(gates) == set(final_ids)


def normalize_manifest() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    manifest: list[dict[str, object]] = []
    results: list[dict[str, object]] = []

    pw_manifest = {r["recon_id"]: r for r in read_csv(PW / "permission_recon_manifest.csv")}
    pw_results: dict[str, dict[str, str]] = {}
    for source in (PW / "permission_recon_results.csv", PW / "permission_recon_retry_results.csv"):
        for r in read_csv(source):
            pw_results[r["recon_id"]] = r
    for request_id, r in pw_manifest.items():
        manifest.append({
            "request_id": request_id, "lane": "physical_world_activity_edge",
            "source_ids": r["source_ids"], "official_url": r["official_url"],
            "purpose": r["purpose"], "method": r["request_method"],
            "user_agent": r["user_agent"], "no_cookies": str(r["cookies"] == "none").lower(),
            "no_auth": str(r["authentication"] == "none").lower(),
            "no_personal_data": str(r["personal_data"].lower() == "false").lower(),
            "registered_at_utc": r["registered_at_utc"],
        })
        x = pw_results.get(request_id, {})
        results.append({
            "request_id": request_id, "lane": "physical_world_activity_edge", "source_ids": r["source_ids"],
            "requested_url": x.get("requested_url", r["official_url"]),
            "effective_safe_url": x.get("effective_safe_url", ""),
            "requested_at_utc": x.get("requested_at_utc", ""), "completed_at_utc": x.get("completed_at_utc", ""),
            "http_status": x.get("http_status", ""), "content_type": x.get("content_type", ""),
            "bytes": x.get("bytes", ""), "sha256": x.get("sha256", ""),
            "cache_path": x.get("cached_body_path", ""), "outcome": x.get("outcome", "not_executed"),
            "stop_reason": x.get("stop_reason", ""),
        })

    scw_manifest = {r["recon_id"]: r for r in read_csv(SCW / "permission_recon_manifest.csv")}
    scw_results = {r["recon_id"]: r for r in read_csv(SCW / "permission_recon_results.csv")}
    for request_id, r in scw_manifest.items():
        manifest.append({
            "request_id": request_id, "lane": "supply_scarcity_web_edge",
            "source_ids": r["source_ids"], "official_url": r["exact_official_url"],
            "purpose": r["purpose"], "method": r["method"], "user_agent": r["user_agent"],
            "no_cookies": r["no_cookies"], "no_auth": r["no_auth"],
            "no_personal_data": r["no_personal_data"], "registered_at_utc": r["registered_at_utc"],
        })
        x = scw_results.get(request_id, {})
        results.append({
            "request_id": request_id, "lane": "supply_scarcity_web_edge", "source_ids": r["source_ids"],
            "requested_url": x.get("requested_url", r["exact_official_url"]),
            "effective_safe_url": x.get("effective_url", ""), "requested_at_utc": x.get("requested_at_utc", ""),
            "completed_at_utc": x.get("requested_at_utc", ""), "http_status": x.get("http_status", ""),
            "content_type": x.get("content_type", ""), "bytes": x.get("response_bytes", ""),
            "sha256": x.get("sha256", ""), "cache_path": x.get("body_cache_path", ""),
            "outcome": x.get("stop_status", "not_executed"), "stop_reason": x.get("error", ""),
        })
    return manifest, results


permission_manifest, permission_results = normalize_manifest()
manifest_fields = ["request_id", "lane", "source_ids", "official_url", "purpose", "method", "user_agent", "no_cookies", "no_auth", "no_personal_data", "registered_at_utc"]
result_fields = ["request_id", "lane", "source_ids", "requested_url", "effective_safe_url", "requested_at_utc", "completed_at_utc", "http_status", "content_type", "bytes", "sha256", "cache_path", "outcome", "stop_reason"]
write_csv(OUT / "permission_recon_manifest.csv", manifest_fields, permission_manifest)
write_csv(OUT / "permission_recon_results.csv", result_fields, permission_results)

# Preserve the only data payload probe, while making the lead override explicit.
probe_manifest = read_csv(PW / "data_probe_manifest.csv")
probe_results = read_csv(PW / "data_probe_results.csv")
write_csv(OUT / "data_probe_manifest.csv", list(probe_manifest[0]), probe_manifest)
write_csv(OUT / "data_probe_results.csv", list(probe_results[0]), probe_results)

result_by_id = {r["request_id"]: r for r in permission_results}
manifest_by_id = {r["request_id"]: r for r in permission_manifest}

request_audit: list[dict[str, object]] = []
for request_id, m in manifest_by_id.items():
    r = result_by_id[request_id]
    requested = bool(r["requested_at_utc"])
    registered_before = (m["registered_at_utc"] < r["requested_at_utc"]) if requested else "not_applicable_not_sent"
    request_audit.append({
        "request_id": request_id, "lane": m["lane"], "request_class": "permission_only",
        "source_ids": m["source_ids"], "requested_url": r["requested_url"], "purpose": m["purpose"],
        "registered_at_utc": m["registered_at_utc"], "requested_at_utc": r["requested_at_utc"],
        "registration_precedes_request": str(registered_before).lower() if isinstance(registered_before, bool) else registered_before,
        "request_sent": str(requested).lower(), "provider_http_reached": str(bool(r["http_status"])).lower(),
        "http_status": r["http_status"], "content_type": r["content_type"], "bytes": r["bytes"],
        "sha256": r["sha256"], "cache_path": r["cache_path"], "outcome": r["outcome"],
        "stop_reason": r["stop_reason"], "exact_fields_or_selector": "permission/documentation page only; no data payload",
        "personal_data_scan": "not_applicable_permission_page", "gate_decision_at_request_time": "permission_recon_exception",
        "final_lead_gate_allowed": "not_applicable_permission_page", "payload_use": "permission_evidence_only",
        "strict_pit_eligible": "false", "eligibility_exclusion": "not a source observation or historical vintage",
    })

pm = probe_manifest[0]
pr = probe_results[0]
payload_path = PW / pr["cached_payload_path"]
payload = json.loads(payload_path.read_text(encoding="utf-8"))
assert isinstance(payload, list) and len(payload) == 1 and set(payload[0]) == {"request_count"}
request_audit.append({
    "request_id": pm["probe_id"], "lane": "physical_world_activity_edge", "request_class": "data_payload",
    "source_ids": pm["source_id"], "requested_url": pr["requested_safe_url"], "purpose": pm["purpose"],
    "registered_at_utc": pm["registered_at_utc"], "requested_at_utc": pr["requested_at_utc"],
    "registration_precedes_request": str(pm["registered_at_utc"] < pr["requested_at_utc"]).lower(),
    "request_sent": "true", "provider_http_reached": "true", "http_status": pr["http_status"],
    "content_type": pr["content_type"], "bytes": pr["bytes"], "sha256": pr["sha256"],
    "cache_path": "physical_world_activity_edge/permission_resolution/" + pr["cached_payload_path"],
    "outcome": "unauthorized_under_final_gate_then_quarantined", "stop_reason": "Lead audit overrode lane robots=allowed because path silence is not affirmative allowance.",
    "exact_fields_or_selector": pm["server_side_projection"],
    "personal_data_scan": "passed: parsed JSON has one row and only the request_count key; no row-level or personal fields",
    "gate_decision_at_request_time": "allowed=true under superseded lane interpretation",
    "final_lead_gate_allowed": "false", "payload_use": "quarantined; excluded from signal, replay, feature, and model use",
    "strict_pit_eligible": "false", "eligibility_exclusion": "permission exception and present-day aggregate response is not a historical publication vintage",
})

request_fields = ["request_id", "lane", "request_class", "source_ids", "requested_url", "purpose", "registered_at_utc", "requested_at_utc", "registration_precedes_request", "request_sent", "provider_http_reached", "http_status", "content_type", "bytes", "sha256", "cache_path", "outcome", "stop_reason", "exact_fields_or_selector", "personal_data_scan", "gate_decision_at_request_time", "final_lead_gate_allowed", "payload_use", "strict_pit_eligible", "eligibility_exclusion"]
write_csv(OUT / "request_level_audit.csv", request_fields, request_audit)

# Count unique permission requests by linked source.  Shared permission pages are
# intentionally counted once in totals but once for each linked source here.
def linked(source_id: str, row: dict[str, object]) -> bool:
    return source_id in str(row["source_ids"]).split("|")

source_rows: list[dict[str, object]] = []
gate_rows: list[dict[str, object]] = []
for source_id in final_ids:
    g = gates[source_id]
    linked_results = [r for r in permission_results if linked(source_id, r)]
    sent = [r for r in linked_results if r["requested_at_utc"]]
    provider = [r for r in sent if r["http_status"]]
    cached = [r for r in provider if r["cache_path"]]
    probe_count = 1 if source_id == "NYC_311_TOURISM_STRESS" else 0
    prior = decision_by_id[source_id]
    blockers = str(g["reason"])
    source_rows.append({
        "rank": rank[source_id], "source_id": source_id, "user_approved_for_lawful_review": "true",
        "permission_manifest_rows_linked": len([m for m in permission_manifest if linked(source_id, m)]),
        "permission_request_attempts_linked": len(sent), "provider_http_gets_linked": len(provider),
        "cached_permission_responses_linked": len(cached), "terms_status": g["terms"], "robots_status": g["robots"],
        "authentication_required_or_blocked": str(g["auth"]).lower(), "captcha_stop": str(g["captcha"]).lower(),
        "personal_data_transport_blocker": str(g["personal"]).lower(), "final_data_path_allowed": "false",
        "data_payload_request_count": probe_count,
        "data_payload_result": "unauthorized_under_final_gate_then_quarantined" if probe_count else "not_requested",
        "strict_pit_eligible_feature_count": 0, "frozen_hypothesis": {"WSF_FERRY_RIDERSHIP": "H-004", "ORANGE_FL_TDT_RELEASES": "H-005", "NYC_OSE_STR_SNAPSHOTS": "H-006"}.get(source_id, ""),
        "replay_rebuilt": "false", "prior_decision": prior["final_decision"], "updated_decision": prior["final_decision"],
        "unresolved_blockers": blockers,
    })
    gate_rows.append({
        "rank": rank[source_id], "source_id": source_id, "exact_data_path": g["path"],
        "terms_status": g["terms"], "robots_status": g["robots"], "authenticated": str(g["auth"]).lower(),
        "captcha_required_or_detected": str(g["captcha"]).lower(), "personal_data": str(g["personal"]).lower(),
        "assessed_at_utc": RECONCILED_AT, "assessment_allowed": "false",
        "assessment_reasons": blockers, "lead_override": "NYC311 robots silence corrected from allowed to unclear; payload quarantined" if source_id == "NYC_311_TOURISM_STRESS" else "",
    })

source_fields = ["rank", "source_id", "user_approved_for_lawful_review", "permission_manifest_rows_linked", "permission_request_attempts_linked", "provider_http_gets_linked", "cached_permission_responses_linked", "terms_status", "robots_status", "authentication_required_or_blocked", "captcha_stop", "personal_data_transport_blocker", "final_data_path_allowed", "data_payload_request_count", "data_payload_result", "strict_pit_eligible_feature_count", "frozen_hypothesis", "replay_rebuilt", "prior_decision", "updated_decision", "unresolved_blockers"]
gate_fields = ["rank", "source_id", "exact_data_path", "terms_status", "robots_status", "authenticated", "captcha_required_or_detected", "personal_data", "assessed_at_utc", "assessment_allowed", "assessment_reasons", "lead_override"]
write_csv(OUT / "source_permission_resolution.csv", source_fields, source_rows)
write_csv(OUT / "data_path_gate_results.csv", gate_fields, gate_rows)

# Update the E1 disposition record only for the disclosed data-request count and
# rationale.  Decisions, hypothesis scope, and eligibility remain frozen.
for row in decision_rows:
    if row["source_id"] == "NYC_311_TOURISM_STRESS":
        row["actual_request_count"] = "1"
        row["collection_allowed"] = "false"
        row["collection_outcome"] = "not_testable"
        row["decision_rationale"] = (
            "One server-side aggregate probe was made under a superseded robots-silence interpretation, then quarantined. "
            "The corrected gate is blocked; mutable classifications, no historical vintages, and weak causal specificity preserve REJECT."
        )
write_csv(RUN / "phase_e1" / "source_approval_and_disposition.csv", list(decision_rows[0]), decision_rows)

# Idempotently add the reconciliation note to the existing canonical source rows.
registry_path = ROOT / "research" / "source_registry.csv"
registry_rows = read_csv(registry_path)
marker = f"Permission resolution {RUN_ID}:"
source_resolution = {r["source_id"]: r for r in source_rows}
for row in registry_rows:
    if row["source_id"] not in source_resolution:
        continue
    sr = source_resolution[row["source_id"]]
    parts = [p.strip() for p in row["analyst_notes"].split(" || ") if p.strip() and not p.strip().startswith(marker)]
    note = (
        f"{marker} final exact-path gate allowed=false; terms={sr['terms_status']}; robots={sr['robots_status']}; "
        f"linked provider HTTP permission GETs={sr['provider_http_gets_linked']}; data payload requests={sr['data_payload_request_count']}; "
        f"strict PIT eligible features=0; E1 decision={sr['updated_decision']}. {sr['unresolved_blockers']}"
    )
    row["analyst_notes"] = " || ".join(parts + [note])
write_csv(registry_path, list(registry_rows[0]), registry_rows)

# Append or replace the fixed audit IDs without disturbing unrelated rows.
audit_path = ROOT / "research" / "scraping_audit.csv"
audit_rows = read_csv(audit_path)
old_e1 = {r["source_id"]: r for r in audit_rows if r["audit_id"].startswith("SA-20260903-E1-")}
new_ids = {f"SA-20260903-PR-{int(rank[s]):03d}" for s in final_ids}
audit_rows = [r for r in audit_rows if r["audit_id"] not in new_ids]
for source_id in final_ids:
    g = gates[source_id]
    old = old_e1[source_id]
    is_exception = source_id == "NYC_311_TOURISM_STRESS"
    audit_rows.append({
        "audit_id": f"SA-20260903-PR-{int(rank[source_id]):03d}", "source_id": source_id,
        "domain": old["domain"],
        "intended_paths": g["path"], "collection_purpose": "Permission-resolution continuation; exact-path lawful tiny probe only after deterministic gate",
        "terms_url": old["terms_url"], "robots_url": old["robots_url"], "reviewed_at_utc": RECONCILED_AT,
        "terms_status": g["terms"], "robots_status": g["robots"], "authenticated": str(g["auth"]).lower(),
        "paywalled": "false", "captcha_required": str(g["captcha"]).lower(), "access_control_bypass": "false",
        "personal_data": str(g["personal"]).lower(), "airbnb_controlled": "false", "explicit_automation_permission": "false",
        "rate_limit_per_minute": old["rate_limit_per_minute"] or "1", "cache_policy": "Cache exact response and SHA-256; no reuse of quarantined payload",
        "user_agent": old["user_agent"], "collection_allowed": "false", "decision_reason": g["reason"],
        "selector_or_endpoint": g["path"], "collected_at_utc": pr["requested_at_utc"] if is_exception else "",
        "artifact_path": "research/edge_discovery/20260903T062839Z_abnb_edge_discovery/physical_world_activity_edge/permission_resolution/cache/data_probe/DP-PW-001.json" if is_exception else "",
        "sha256": pr["sha256"] if is_exception else "",
        "status": "compliance_exception_payload_quarantined" if is_exception else "blocked_after_permission_resolution",
        "citations": " | ".join(x for x in [old["terms_url"], old["robots_url"], candidate_rows[int(rank[source_id]) - 1]["exact_source_urls"]] if x),
    })
write_csv(audit_path, list(audit_rows[0]), audit_rows)

# Bring the proposed non-executable handoff and claim ledger forward without
# admitting the quarantined payload into any feature or model table.
provenance_path = RUN / "phase_e1" / "proposed_quant_handoff" / "source_provenance.csv"
provenance_rows = read_csv(provenance_path)
for row in provenance_rows:
    if row["source_id"] == "NYC_311_TOURISM_STRESS":
        row["actual_request_count"] = "1"
        row["provider_gate_allowed"] = "false"
        row["collection_outcome"] = "not_testable_compliance_exception_quarantined"
        row["collection_timestamp_utc"] = pr["requested_at_utc"]
        row["artifact_sha256"] = pr["sha256"]
        row["notes"] = (
            "One one-row count(*) payload was requested under a superseded robots-silence interpretation. "
            "Lead gate=false; response quarantined and excluded from all features, replays, and models."
        )
write_csv(provenance_path, list(provenance_rows[0]), provenance_rows)

claim_path = RUN / "phase_e1" / "claim_source_ledger.csv"
claim_rows = read_csv(claim_path)
for row in claim_rows:
    if row["source_id"] == "NYC_311_TOURISM_STRESS":
        row["claim"] = "A single aggregate payload was requested under a superseded robots-silence interpretation, quarantined, and excluded; the source remains not testable."
        row["access_notes"] = "Exact request-level evidence is in permission_resolution/request_level_audit.csv; no further request is permitted."
        row["confidence"] = "high for request and exclusion outcome; source signal efficacy untested"
write_csv(claim_path, list(claim_rows[0]), claim_rows)

handoff_dir = RUN / "phase_e1" / "proposed_quant_handoff"
handoff_summary_path = handoff_dir / "handoff_summary.md"
handoff_summary = handoff_summary_path.read_text(encoding="utf-8")
handoff_summary = handoff_summary.replace(
    "No edge-source request or authenticated API call occurred, and all 138 primary/sensitivity feature rows are ineligible.",
    "One NYC 311 aggregate request occurred under a superseded robots-silence interpretation and is quarantined; no authenticated API call occurred, no lawful edge observation was admitted, and all 138 primary/sensitivity feature rows are ineligible.",
)
handoff_summary_path.write_text(handoff_summary, encoding="utf-8")

handoff_manifest_path = handoff_dir / "manifest.json"
handoff_manifest = json.loads(handoff_manifest_path.read_text(encoding="utf-8"))
handoff_manifest.update({
    "permission_resolution_continuation_at_utc": RECONCILED_AT,
    "data_payload_requests": 1,
    "quarantined_data_payloads": 1,
    "eligible_feature_rows": 0,
    "predictive_alpha_tested": False,
})
handoff_manifest_path.write_text(json.dumps(handoff_manifest, indent=2) + "\n", encoding="utf-8")
handoff_files = handoff_manifest["files"] + ["manifest.json"]
(handoff_dir / "checksums.sha256").write_text(
    "\n".join(f"{sha256(handoff_dir / name)}  {name}" for name in handoff_files) + "\n",
    encoding="utf-8",
)

# Amend the Phase E1 memo in place without duplicating the continuation section.
memo_path = RUN / "phase_e1" / "phase_e1_memo.md"
memo = memo_path.read_text(encoding="utf-8")
old_sentence = "Every deterministic gate remained blocked; no source request was made. Consequently, no lawful edge feature could be computed and no predictive relationship could be tested. **Predictive alpha remains untested.**"
new_sentence = "The permission-resolution continuation completed 35 provider-facing permission GETs and cached every response. Final lead review left all 15 exact data paths blocked. One privacy-safe NYC 311 aggregate GET occurred under a superseded lane interpretation of robots silence; it was immediately quarantined and excluded. Consequently, no lawful edge feature could be computed and no predictive relationship could be tested. **Predictive alpha remains untested.**"
if old_sentence in memo:
    memo = memo.replace(old_sentence, new_sentence)
start = "\n## Permission-resolution continuation\n"
if start in memo:
    memo = memo.split(start)[0].rstrip() + "\n"
memo += f"""

## Permission-resolution continuation

At {RECONCILED_AT}, both fixed lanes had completed the authorized official-page reconnaissance. The combined append-only manifest contains 83 permission rows. There were 68 sent permission attempts: 33 sandbox attempts that ended before HTTP because DNS was unavailable and 35 one-time provider-facing GETs after preregistered retries. Provider responses were 29 HTTP 200, five HTTP 403, and one HTTP 404; all 35 bodies were cached and checksummed. Stop rows prevented 14 further planned requests. No refusal was retried.

No final exact data path passed the lead gate. Terms and robots were evaluated separately, and silence was not treated as affirmative robots permission. The sole data-payload request, DP-PW-001, was a one-row NYC 311 `count(*)` response made after the physical lane had treated an unlisted `/resource/` path as allowed. Lead review superseded that interpretation: the request is the run's sole unauthorized-under-final-gate compliance exception, robots status is `unclear`, the final gate is false, the payload is quarantined, and no further NYC 311 request is permitted. A parsed-field audit found only `request_count`; no row-level or personal field was transported. It is also a current response rather than a historical publication vintage, so it is excluded from H-004/H-005/H-006, all features, and any model.

H-004, H-005, and H-006 therefore remain unreplayed: each still has zero strict-cutoff-eligible edge observations and remains `INCONCLUSIVE` under its frozen failure rule. All other source decisions are unchanged. No source is promoted, no outcome was inspected, and no regression, machine learning, threshold tuning, or quant phase began. The complete request-level evidence is in `permission_resolution/request_level_audit.csv`.
"""
memo_path.write_text(memo, encoding="utf-8")

# Human-readable lead memo.
lines = [
    "1. ABNB Edge-Data Research Orchestrator — owns orchestration, user communication, and the final decision.",
    "2. abnb_alt_data — owns governance, canonical registries, PIT methodology, reconciliation, and the final slate.",
    "3. physical_world_activity_edge — eight retained physical-world sources.",
    "4. supply_scarcity_web_edge — seven retained supply/scarcity sources.",
    "", "# Permission-resolution and lawful-extraction continuation", "",
    "## Decision", "",
    "All 15 approved retained IDs were reviewed. Final exact-path result: **0 allowed, 15 blocked**. Exactly one unauthorized-under-final-gate data probe occurred: the NYC 311 aggregate request made under a superseded robots-silence interpretation. It is quarantined, unused, and ineligible. No other data payload was requested. Predictive alpha remains untested.",
    "", "## Request accounting", "",
    "- Permission manifest rows: 83.",
    "- Sent permission attempts: 68 (33 sandbox DNS failures; 35 provider-facing GETs).",
    "- Provider responses: 29×200, 5×403, 1×404; 35 cached bodies.",
    "- Planned rows not sent after stop: 14; one supply manifest row had no execution row and is retained as not executed.",
    "- Data payload requests: 1; HTTP 200; one row/one field; quarantined and excluded.",
    "", "## Source resolutions", "",
    "| Rank | Source | Terms | Robots | Payloads | Eligible features | Decision |", "|---:|---|---|---|---:|---:|---|",
]
for row in source_rows:
    lines.append(f"| {row['rank']} | {row['source_id']} | {row['terms_status']} | {row['robots_status']} | {row['data_payload_request_count']} | 0 | {row['updated_decision']} |")
lines += [
    "", "## Frozen pilots", "",
    "H-004 WSF, H-005 Orange TDT, and H-006 NYC OSE each remain `INCONCLUSIVE`: zero strict-cutoff-eligible feature observations, no replay rebuild, and no outcome inspection. Archive promise is not permission clearance, and neither is event-level eligibility.",
    "", "## Compliance exception", "",
    "DP-PW-001 was preregistered before request and used server-side projection `count(*) as request_count`; the cached JSON contains only `request_count`. The physical lane treated robots silence as ordinary REP allowance. The lead applied the user's stricter rule, changed final robots status to `unclear`, set gate=false, quarantined the response, excluded it from every downstream artifact, and stopped further NYC 311 requests.",
    "", "## Stop", "",
    "This continuation ends inside Phase E1. No later quant phase was started.",
]
(OUT / "permission_resolution_memo.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# Artifact inventory and checksums.  The checksum file excludes itself.
artifact_paths = [
    OUT / "permission_recon_manifest.csv", OUT / "permission_recon_results.csv",
    OUT / "data_probe_manifest.csv", OUT / "data_probe_results.csv",
    OUT / "request_level_audit.csv", OUT / "source_permission_resolution.csv",
    OUT / "data_path_gate_results.csv", OUT / "permission_resolution_memo.md",
]
manifest_rows = []
for path in artifact_paths:
    manifest_rows.append({"artifact": str(path.relative_to(RUN)), "sha256": sha256(path), "bytes": path.stat().st_size})
write_csv(OUT / "artifact_manifest.csv", ["artifact", "sha256", "bytes"], manifest_rows)
with (OUT / "checksums.sha256").open("w", encoding="utf-8") as handle:
    for path in artifact_paths + [OUT / "artifact_manifest.csv"]:
        handle.write(f"{sha256(path)}  {path.name}\n")

print("BUILT_PERMISSION_RESOLUTION")
