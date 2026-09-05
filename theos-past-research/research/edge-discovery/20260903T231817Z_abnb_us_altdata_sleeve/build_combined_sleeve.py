"""Build the governed combined U.S. alt-data sleeve and descriptive event panel.

This script performs no network access. It only reconciles governed lane outputs and
previously cached aggregate public-source payloads. All retrospective features remain
strictly PIT-ineligible when original publication vintages are unavailable.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from calendar import monthrange
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean


RUN_ID = "20260903T231817Z_abnb_us_altdata_sleeve"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PHYSICAL = HERE / "physical_world_activity_edge"
SUPPLY = HERE / "supply_scarcity_web_edge"
PRIOR_BROAD = REPO / "research/edge_discovery/20260903T204950Z_broad_scrape"
GUIDANCE = REPO / "research/forecasting/runs/20260903T224632Z_50_source_guidance_format/guidance_history.csv"
BUILT_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def fmt(value: float | None) -> str:
    return "" if value is None or not math.isfinite(value) else f"{value:.8f}".rstrip("0").rstrip(".")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def month_end(period: str) -> datetime:
    year, month = map(int, period.split("-"))
    return datetime(year, month, monthrange(year, month)[1], 23, 59, 59, tzinfo=timezone.utc)


def shift_month(period: str, delta: int) -> str:
    year, month = map(int, period.split("-"))
    idx = year * 12 + month - 1 + delta
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def latest_period(series: dict[str, float], cutoff: datetime, lag_days: int) -> str | None:
    eligible = [p for p in series if month_end(p) + timedelta(days=lag_days) < cutoff]
    return max(eligible) if eligible else None


def trailing_three_yoy(series: dict[str, float], period: str | None) -> float | None:
    if period is None:
        return None
    current = [shift_month(period, offset) for offset in (-2, -1, 0)]
    prior = [shift_month(p, -12) for p in current]
    if any(p not in series for p in current + prior):
        return None
    current_sum = sum(series[p] for p in current)
    prior_sum = sum(series[p] for p in prior)
    return None if prior_sum == 0 else (current_sum / prior_sum - 1.0) * 100.0


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return None if denom == 0 else sum(x * y for x, y in zip(dx, dy)) / denom


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        average_rank = (cursor + 1 + end) / 2.0
        for pos in range(cursor, end):
            out[order[pos]] = average_rank
        cursor = end
    return out


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(ranks(xs), ranks(ys)) if len(xs) >= 2 else None


def direction(value: float | None) -> str:
    if value is None:
        return ""
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


# Canonical source manifest.
run_source_ids = [
    "TSA_CHECKPOINT", "FHWA_TVT_VMT", "BTS_T100", "NPS_VISITOR_USE",
    "FTA_NTD_MONTHLY_RIDERSHIP", "SFO_AIR_PASSENGERS", "PANYNJ_AIRPORT_PARKING",
    "LAX_TERMINAL_PASSENGERS", "BLS_CPI_LODGING", "CENSUS_QSS_ACCOMMODATION",
    "NYC_OSE_STR_SNAPSHOTS", "NOLA_STR_PERMIT_EVENTS", "SAN_DIEGO_STRO_ACTIVE",
    "EUROSTAT_PLATFORM_NIGHTS",
]
registry = {row["source_id"]: row for row in read_csv(REPO / "research/source_registry.csv")}
source_rows: list[dict[str, object]] = []
for source_id in run_source_ids:
    row = dict(registry[source_id])
    row["run_id"] = RUN_ID
    row["run_role"] = (
        "current_snapshot_diagnostic_control" if source_id == "EUROSTAT_PLATFORM_NIGHTS"
        else "governed_cache_diagnostic" if source_id == "SFO_AIR_PASSENGERS"
        else "permission_and_testability_review"
    )
    source_rows.append(row)
source_fields = list(read_csv(REPO / "research/source_registry.csv")[0].keys()) + ["run_id", "run_role"]
write_csv(HERE / "source_manifest.csv", source_fields, source_rows)


# Request-level permission audit. Permission reconnaissance is separated from data reuse.
permission_rows: list[dict[str, object]] = []


def add_request_set(manifest_path: Path, results_path: Path, lane: str, id_field: str,
                    url_field: str, registered_field: str) -> None:
    manifests = {row[id_field]: row for row in read_csv(manifest_path)}
    results = {row[id_field]: row for row in read_csv(results_path)}
    for request_id, manifest in manifests.items():
        result = results.get(request_id, {})
        requested_at = result.get("requested_at_utc", "")
        registered_at = manifest.get(registered_field, "")
        made = bool(requested_at)
        timing_ok = "not_applicable"
        if made:
            timing_ok = str(parse_utc(registered_at) < parse_utc(requested_at)).lower()
        cache_rel = result.get("cached_path", result.get("body_cache_path", ""))
        cache_path = str((manifest_path.parent / cache_rel).relative_to(REPO)) if cache_rel else ""
        permission_rows.append({
            "audit_row_id": f"{lane}:{request_id}", "lane": lane, "request_id": request_id,
            "source_id": manifest["source_id"], "request_class": "permission_only",
            "permission_attempt": "true", "provider_http_get_made": str(made).lower(),
            "data_payload_request": "false", "registered_at_utc": registered_at,
            "requested_at_utc": requested_at, "manifest_precedes_request": timing_ok,
            "requested_url": result.get("requested_url", manifest.get(url_field, "")),
            "effective_safe_url": result.get("effective_safe_url", result.get("effective_url", "")),
            "http_status": result.get("http_status", ""), "content_type": result.get("content_type", ""),
            "response_bytes": result.get("bytes", result.get("response_bytes", "")),
            "sha256": result.get("sha256", ""), "cache_path": cache_path,
            "outcome": result.get("outcome", result.get("stop_status", "")),
            "exact_fields": "permission/robots/terms/metadata only; no observation fields",
            "personal_data_scan": "not_applicable_no_data_payload",
            "gate_decision_at_request_time": "permission_reconnaissance_exception_only",
            "eligibility_exclusion": "permission evidence only; never an observation",
            "notes": result.get("stop_reason", result.get("error", "")),
        })


add_request_set(PHYSICAL / "permission_request_manifest.csv", PHYSICAL / "permission_request_results.csv",
                "physical", "request_id", "official_url", "registered_at_utc")
add_request_set(PHYSICAL / "airport_permission_manifest.csv", PHYSICAL / "airport_permission_results.csv",
                "physical", "request_id", "official_url", "registered_at_utc")
add_request_set(SUPPLY / "permission_request_manifest.csv", SUPPLY / "permission_request_results.csv",
                "supply", "recon_id", "exact_official_url", "registered_at_utc")

for reuse in read_csv(PHYSICAL / "permission_reuse_manifest.csv"):
    permission_rows.append({
        "audit_row_id": f"physical:{reuse['reuse_id']}", "lane": "physical",
        "request_id": reuse["reuse_id"], "source_id": reuse["source_id"],
        "request_class": "permission_reuse_no_get", "permission_attempt": "false",
        "provider_http_get_made": "false", "data_payload_request": "false",
        "registered_at_utc": "", "requested_at_utc": reuse["prior_requested_at_utc"],
        "manifest_precedes_request": "not_applicable_reuse", "requested_url": reuse["official_url"],
        "effective_safe_url": reuse["official_url"], "http_status": reuse["http_status"],
        "content_type": reuse["content_type"], "response_bytes": reuse["bytes"],
        "sha256": reuse["sha256"],
        "cache_path": str((PHYSICAL / reuse["reused_cache_path"]).relative_to(REPO)),
        "outcome": "reused_same_day", "exact_fields": "permission evidence only",
        "personal_data_scan": "not_applicable_no_data_payload",
        "gate_decision_at_request_time": "same-day exact evidence reuse",
        "eligibility_exclusion": "permission evidence only; never an observation",
        "notes": reuse["reuse_basis"],
    })

for idx, reuse in enumerate(read_csv(SUPPLY / "permission_evidence_reuse.csv"), start=1):
    permission_rows.append({
        "audit_row_id": f"supply:REUSE-{idx:03d}", "lane": "supply",
        "request_id": f"REUSE-SUP-{idx:03d}", "source_id": reuse["source_id"],
        "request_class": "permission_reuse_no_get", "permission_attempt": "false",
        "provider_http_get_made": "false", "data_payload_request": "false",
        "registered_at_utc": reuse["reused_at_utc"], "requested_at_utc": "",
        "manifest_precedes_request": "not_applicable_reuse", "requested_url": reuse["exact_urls"],
        "effective_safe_url": "", "http_status": "", "content_type": "", "response_bytes": "",
        "sha256": reuse["sha256_or_row_reference"], "cache_path": reuse["evidence_path"],
        "outcome": "reused_same_day", "exact_fields": "permission evidence only",
        "personal_data_scan": "not_applicable_no_data_payload",
        "gate_decision_at_request_time": "same-day exact evidence reuse",
        "eligibility_exclusion": "permission evidence only; never an observation",
        "notes": reuse["interpretation"],
    })

permission_rows.extend([
    {
        "audit_row_id": "combined:REUSE-DATA-SFO", "lane": "combined", "request_id": "REUSE-DATA-SFO",
        "source_id": "SFO_AIR_PASSENGERS", "request_class": "data_reuse_no_get",
        "permission_attempt": "false", "provider_http_get_made": "false", "data_payload_request": "false",
        "registered_at_utc": "2026-09-03T23:20:45Z", "requested_at_utc": "2026-09-03T20:50:50Z",
        "manifest_precedes_request": "not_applicable_prior_governed_run", "requested_url": registry["SFO_AIR_PASSENGERS"]["source_url"],
        "effective_safe_url": registry["SFO_AIR_PASSENGERS"]["source_url"], "http_status": "200", "content_type": "application/json",
        "response_bytes": (PRIOR_BROAD / "raw/sfo_air_passengers_aggregate.json").stat().st_size,
        "sha256": sha256(PRIOR_BROAD / "raw/sfo_air_passengers_aggregate.json"),
        "cache_path": str((PRIOR_BROAD / "raw/sfo_air_passengers_aggregate.json").relative_to(REPO)),
        "outcome": "prior_governed_cache_reused", "exact_fields": "activity_period, geo_summary, activity_type_code, aggregate passenger_count, data_as_of, data_loaded_at",
        "personal_data_scan": "aggregate airport-month fields only; no personal fields",
        "gate_decision_at_request_time": "no new request; prior governed aggregate cache only",
        "eligibility_exclusion": "current snapshot; original monthly publication timestamps unavailable",
        "notes": "No provider request in this run.",
    },
    {
        "audit_row_id": "combined:REUSE-DATA-EUROSTAT", "lane": "combined", "request_id": "REUSE-DATA-EUROSTAT",
        "source_id": "EUROSTAT_PLATFORM_NIGHTS", "request_class": "data_reuse_no_get",
        "permission_attempt": "false", "provider_http_get_made": "false", "data_payload_request": "false",
        "registered_at_utc": "", "requested_at_utc": "2026-09-03T20:50:17Z",
        "manifest_precedes_request": "not_applicable_prior_governed_run", "requested_url": registry["EUROSTAT_PLATFORM_NIGHTS"]["source_url"],
        "effective_safe_url": registry["EUROSTAT_PLATFORM_NIGHTS"]["source_url"], "http_status": "200", "content_type": "application/json",
        "response_bytes": (PRIOR_BROAD / "raw/eurostat_tour_ce_omr.json").stat().st_size,
        "sha256": sha256(PRIOR_BROAD / "raw/eurostat_tour_ce_omr.json"),
        "cache_path": str((PRIOR_BROAD / "raw/eurostat_tour_ce_omr.json").relative_to(REPO)),
        "outcome": "prior_governed_cache_reused", "exact_fields": "EU27_2020, monthly, nights spent, total residence, aggregate value",
        "personal_data_scan": "aggregate EU27-month fields only; no personal fields",
        "gate_decision_at_request_time": "no new request; prior governed aggregate cache only",
        "eligibility_exclusion": "current snapshot; API has no vintage support",
        "notes": "No provider request in this run; fixed 120-day lag is diagnostic only.",
    },
])
permission_fields = ["audit_row_id", "lane", "request_id", "source_id", "request_class", "permission_attempt",
                     "provider_http_get_made", "data_payload_request", "registered_at_utc", "requested_at_utc",
                     "manifest_precedes_request", "requested_url", "effective_safe_url", "http_status", "content_type",
                     "response_bytes", "sha256", "cache_path", "outcome", "exact_fields", "personal_data_scan",
                     "gate_decision_at_request_time", "eligibility_exclusion", "notes"]
write_csv(HERE / "permission_audit.csv", permission_fields, permission_rows)


# Normalized observations: governed SFO cache, governed EU27 cache, and explicit not-collected rows.
observation_fields = ["observation_id", "source_id", "provider", "series_id", "metric", "reference_period",
                      "geography", "unit", "value", "observation_at_utc", "first_available_at_utc",
                      "vintage_at_utc", "collected_at_utc", "pit_treatment", "raw_file", "raw_sha256",
                      "source_url", "permission_status", "strict_pit_eligible", "exclusion_reason"]
observations: list[dict[str, object]] = []

for row in read_csv(PHYSICAL / "observations_long.csv"):
    observations.append({
        "observation_id": row["observation_id"], "source_id": row["source_id"], "provider": row["provider"],
        "series_id": f"rkru-6vcg.{row['geo_segment']}.{row['metric']}", "metric": row["metric"],
        "reference_period": row["reference_period"], "geography": f"{row['geography']} | {row['geo_segment']}",
        "unit": row["unit"], "value": row["value"],
        "observation_at_utc": f"{row['observation_date']}T23:59:59Z",
        "first_available_at_utc": row["initial_publication_timestamp_utc"],
        "vintage_at_utc": row["revision_timestamp_utc"], "collected_at_utc": row["collection_timestamp_utc"],
        "pit_treatment": "current_snapshot_prospective_only", "raw_file": str((PHYSICAL / row["raw_cache_path"]).relative_to(REPO)),
        "raw_sha256": row["raw_sha256"], "source_url": registry[row["source_id"]]["source_url"],
        "permission_status": "prior_governed_cache_reuse_no_new_request", "strict_pit_eligible": "false",
        "exclusion_reason": row["pit_ineligibility_reason"],
    })

prior_observations = PRIOR_BROAD / "processed/valid_observations.csv"
for row in read_csv(prior_observations):
    if row["source_id"] != "EUROSTAT_PLATFORM_NIGHTS_COUNTRY" or row["geography_code"] != "EU27_2020":
        continue
    if len(row["reference_period"]) != 7 or row["reference_period"][4] != "-":
        continue
    raw_path = PRIOR_BROAD / "raw/eurostat_tour_ce_omr.json"
    observations.append({
        "observation_id": f"EU27-{row['reference_period']}", "source_id": "EUROSTAT_PLATFORM_NIGHTS",
        "provider": "Eurostat", "series_id": "tour_ce_omr.EU27_2020.NGT_SP.TOTAL",
        "metric": "collaborative-platform nights spent", "reference_period": row["reference_period"],
        "geography": "European Union - 27 countries (from 2020)", "unit": "nights", "value": row["value"],
        "observation_at_utc": month_end(row["reference_period"]).isoformat().replace("+00:00", "Z"),
        "first_available_at_utc": "", "vintage_at_utc": row["source_updated_at"],
        "collected_at_utc": row["collected_at_utc"], "pit_treatment": "current_snapshot_prospective_only",
        "raw_file": str(raw_path.relative_to(REPO)), "raw_sha256": sha256(raw_path),
        "source_url": registry["EUROSTAT_PLATFORM_NIGHTS"]["source_url"],
        "permission_status": "prior_governed_cache_reuse_no_new_request", "strict_pit_eligible": "false",
        "exclusion_reason": "Eurostat dissemination API provides latest values without historical versions; fixed 120-day lag is only a diagnostic convention.",
    })

for row in read_csv(SUPPLY / "observations_long.csv"):
    observations.append({
        "observation_id": row["observation_id"], "source_id": row["source_id"],
        "provider": registry[row["source_id"]]["provider"], "series_id": "not_collected",
        "metric": row["metric"], "reference_period": "", "geography": row["geography"], "unit": row["unit"],
        "value": "", "observation_at_utc": "", "first_available_at_utc": "", "vintage_at_utc": "",
        "collected_at_utc": row["collected_at_utc"], "pit_treatment": row["eligibility_status"],
        "raw_file": str((SUPPLY / row["cache_path"]).relative_to(REPO)) if row["cache_path"] else "",
        "raw_sha256": row["sha256"], "source_url": row["source_url"], "permission_status": row["eligibility_status"],
        "strict_pit_eligible": "false", "exclusion_reason": row["exclusion_reason"],
    })

physical_dispositions = read_csv(PHYSICAL / "source_dispositions.csv")
for row in physical_dispositions:
    if row["source_id"] == "SFO_AIR_PASSENGERS":
        continue
    observations.append({
        "observation_id": f"{row['source_id']}-NOT-COLLECTED", "source_id": row["source_id"],
        "provider": registry[row["source_id"]]["provider"], "series_id": "not_collected",
        "metric": "", "reference_period": "", "geography": registry[row["source_id"]]["geographic_coverage"],
        "unit": "", "value": "", "observation_at_utc": "", "first_available_at_utc": "",
        "vintage_at_utc": "", "collected_at_utc": BUILT_AT, "pit_treatment": row["collection_outcome"],
        "raw_file": "", "raw_sha256": "", "source_url": registry[row["source_id"]]["source_url"],
        "permission_status": row["collection_outcome"], "strict_pit_eligible": "false",
        "exclusion_reason": row["reason"],
    })

write_csv(HERE / "observations_long.csv", observation_fields, observations)


# Feature inputs from current snapshots. Transit passengers are excluded by preregistration.
sfo: dict[str, float] = {}
for row in observations:
    if row["source_id"] == "SFO_AIR_PASSENGERS" and row["metric"] in {"Enplaned", "Deplaned"}:
        sfo[str(row["reference_period"])] = sfo.get(str(row["reference_period"]), 0.0) + float(row["value"])
europe = {str(row["reference_period"]): float(row["value"]) for row in observations
          if row["source_id"] == "EUROSTAT_PLATFORM_NIGHTS" and row["value"] != ""}


# Targets and fixed event alignment.
guidance_rows = read_csv(GUIDANCE)
midpoint_by_guided_period = {row["guided_fiscal_period"]: safe_float(row["target_midpoint"]) for row in guidance_rows}
targets: list[dict[str, object]] = []
previous_yoy: float | None = None
for row in guidance_rows:
    year, quarter = int(row["guided_fiscal_period"][:4]), row["guided_fiscal_period"][4:]
    prior_period = f"{year - 1}{quarter}"
    midpoint = safe_float(row["target_midpoint"])
    prior_midpoint = midpoint_by_guided_period.get(prior_period)
    yoy = None if midpoint is None or prior_midpoint in (None, 0) else (midpoint / prior_midpoint - 1.0) * 100.0
    acceleration = None if yoy is None or previous_yoy is None else yoy - previous_yoy
    targets.append({
        **row, "prior_year_comparable_guided_fiscal_period": prior_period,
        "prior_year_comparable_midpoint": fmt(prior_midpoint), "guidance_yoy_pct": fmt(yoy),
        "prior_event_guidance_yoy_pct": fmt(previous_yoy), "guidance_yoy_acceleration_pp": fmt(acceleration),
        "guidance_yoy_direction": direction(yoy), "guidance_acceleration_direction": direction(acceleration),
    })
    previous_yoy = yoy
target_fields = list(guidance_rows[0].keys()) + ["prior_year_comparable_guided_fiscal_period",
                "prior_year_comparable_midpoint", "guidance_yoy_pct", "prior_event_guidance_yoy_pct",
                "guidance_yoy_acceleration_pp", "guidance_yoy_direction", "guidance_acceleration_direction"]
write_csv(HERE / "guidance_targets.csv", target_fields, targets)

feature_rows: list[dict[str, object]] = []
for target in targets:
    cutoff = parse_utc(target["guidance_available_at_utc"])
    sfo_period = latest_period(sfo, cutoff, 0)
    sfo_value = trailing_three_yoy(sfo, sfo_period)
    eu_period = latest_period(europe, cutoff, 120)
    eu_value = trailing_three_yoy(europe, eu_period)
    composite = None if sfo_value is None or eu_value is None else 0.5 * sfo_value + 0.5 * eu_value
    common = {
        "prediction_id": target["prediction_id"], "guidance_cutoff_at_utc": target["guidance_available_at_utc"],
        "guided_fiscal_period": target["guided_fiscal_period"], "guidance_midpoint": target["target_midpoint"],
        "prior_year_comparable_midpoint": target["prior_year_comparable_midpoint"],
        "guidance_yoy_pct": target["guidance_yoy_pct"],
        "guidance_yoy_acceleration_pp": target["guidance_yoy_acceleration_pp"],
    }

    def add(hypothesis_id: str, feature_id: str, period: str | None, value: float | None,
            transform: str, pit_treatment: str, exclusion: str, source_ids: str) -> None:
        feature_rows.append({
            **common, "hypothesis_id": hypothesis_id, "feature_id": feature_id,
            "source_ids": source_ids, "latest_eligible_reference_period": "",
            "diagnostic_reference_period": period or "", "feature_value": fmt(value),
            "feature_transform": transform, "strict_eligibility": "false", "pit_treatment": pit_treatment,
            "exclusion_reason": exclusion,
            "feature_direction": direction(value),
            "strict_evaluation_status": "not_testable",
        })

    snapshot_reason = "Current snapshot lacks original historical publication/vintage timestamps; reference-period alignment is diagnostic only."
    add("H-007", "SFO_TRAILING_3M_PASSENGER_YOY", sfo_period, sfo_value,
        "Trailing three complete reference months total enplaned+deplaned passengers YoY; reference-month-end-only diagnostic alignment",
        "current_snapshot_diagnostic", snapshot_reason, "SFO_AIR_PASSENGERS")
    add("H-008", "FHWA_TRAILING_3M_VMT_YOY", None, None,
        "Trailing three complete months national VMT YoY", "not_collected_permission_blocked",
        "FHWA dated workbook directory is explicitly robots-disallowed; no payload or feature.", "FHWA_TVT_VMT")
    add("H-009", "CENSUS_QSS_ACCOMMODATION_YOY", None, None,
        "Latest contemporaneous NAICS 721 quarterly revenue YoY", "not_collected_permission_blocked",
        "Exact API path and release vintages were not lawfully established; no payload or feature.", "CENSUS_QSS_ACCOMMODATION")
    add("H-010", "MUNICIPAL_AIRPORT_BREADTH", None, None,
        "Equal-weight mean of provider-level fixed YoY changes; requires at least two providers", "not_testable_one_provider",
        "Only SFO cache was usable; PANYNJ and LAX exact data paths did not pass the gate.",
        "SFO_AIR_PASSENGERS|PANYNJ_AIRPORT_PARKING|LAX_TERMINAL_PASSENGERS")
    add("H-011", "US_ACTIVITY_AVAILABLE_PROVIDER", sfo_period, sfo_value,
        "Trailing three complete months YoY; SFO is the sole available official provider and is not a breadth composite",
        "current_snapshot_diagnostic", snapshot_reason + " Fewer than two providers means H-011 minimum evidence fails.",
        "SFO_AIR_PASSENGERS")
    add("H-012", "EU27_PLATFORM_NIGHTS_CONTROL", eu_period, eu_value,
        "Trailing three complete months EU27 collaborative-platform nights YoY with fixed 120-day conservative diagnostic lag",
        "current_snapshot_diagnostic", "Eurostat API history is a current snapshot with no versioning; 120-day lag is not vintage evidence.",
        "EUROSTAT_PLATFORM_NIGHTS")
    add("H-012", "US_EU_EQUAL_50_50_COMPOSITE", min(filter(None, [sfo_period, eu_period]), default=None), composite,
        "Exactly 50% available U.S. activity growth plus 50% EU27 platform-night growth; never row-weighted",
        "current_snapshot_diagnostic", "Both inputs are non-PIT current-snapshot diagnostics; composite cannot be strict.",
        "SFO_AIR_PASSENGERS|EUROSTAT_PLATFORM_NIGHTS")

feature_fields = ["prediction_id", "guidance_cutoff_at_utc", "guided_fiscal_period", "hypothesis_id", "feature_id",
                  "source_ids", "latest_eligible_reference_period", "diagnostic_reference_period", "feature_value",
                  "feature_transform", "strict_eligibility", "pit_treatment", "exclusion_reason", "feature_direction",
                  "guidance_midpoint", "prior_year_comparable_midpoint", "guidance_yoy_pct",
                  "guidance_yoy_acceleration_pp", "strict_evaluation_status"]
write_csv(HERE / "event_aligned_features.csv", feature_fields, feature_rows)


# Fixed, descriptive metrics only. These are not historical backtests because strict n is zero.
summary_rows: list[dict[str, object]] = []
for feature_id in sorted({row["feature_id"] for row in feature_rows}):
    rows = [row for row in feature_rows if row["feature_id"] == feature_id]
    level_pairs = [(float(r["feature_value"]), float(r["guidance_yoy_pct"])) for r in rows
                   if r["feature_value"] != "" and r["guidance_yoy_pct"] != ""]
    accel_pairs = [(float(r["feature_value"]), float(r["guidance_yoy_acceleration_pp"])) for r in rows
                   if r["feature_value"] != "" and r["guidance_yoy_acceleration_pp"] != ""]
    xs = [p[0] for p in level_pairs]
    ys = [p[1] for p in level_pairs]
    concordant = sum(direction(x) == direction(y) for x, y in accel_pairs)
    summary_rows.append({
        "feature_id": feature_id, "strict_pit_n": 0, "strict_pearson": "", "strict_spearman": "",
        "strict_acceleration_concordance": "", "diagnostic_level_n": len(level_pairs),
        "diagnostic_pearson_guidance_yoy": fmt(pearson(xs, ys)),
        "diagnostic_spearman_guidance_yoy": fmt(spearman(xs, ys)),
        "diagnostic_acceleration_n": len(accel_pairs),
        "diagnostic_acceleration_direction_concordance": fmt(concordant / len(accel_pairs) if accel_pairs else None),
        "inference_status": "descriptive_current_snapshot_only" if level_pairs else "not_testable_no_feature",
        "decision": "WATCH_PROSPECTIVELY" if level_pairs else "INCONCLUSIVE",
        "notes": "Fixed metrics from preregistered transformations; no threshold or feature search; no alpha or predictive-power claim.",
    })
summary_fields = ["feature_id", "strict_pit_n", "strict_pearson", "strict_spearman",
                  "strict_acceleration_concordance", "diagnostic_level_n", "diagnostic_pearson_guidance_yoy",
                  "diagnostic_spearman_guidance_yoy", "diagnostic_acceleration_n",
                  "diagnostic_acceleration_direction_concordance", "inference_status", "decision", "notes"]
write_csv(HERE / "descriptive_comparison.csv", summary_fields, summary_rows)


vintage_rows = []
for row in read_csv(PHYSICAL / "publication_vintage_audit.csv") + read_csv(SUPPLY / "publication_vintage_audit.csv"):
    vintage_rows.append(row)
vintage_rows.append({
    "source_id": "EUROSTAT_PLATFORM_NIGHTS", "publication_schedule": "Current dissemination snapshot updated 2026-07-02",
    "publication_lag": "Fixed 120-day diagnostic lag only", "revision_policy": "Latest values revise; dissemination API has no versioning",
    "vintage_evidence": "No historical API versions; original monthly release timestamps unavailable",
    "pit_status": "prospective_only_current_snapshot", "eligible_observations": 0,
    "limitation": "Reference-period plus lag is not proof of historical availability.",
})
vintage_fields = ["source_id", "publication_schedule", "publication_lag", "revision_policy", "vintage_evidence",
                  "pit_status", "eligible_observations", "limitation"]
write_csv(HERE / "publication_vintage_audit.csv", vintage_fields, vintage_rows)


raw_files = [
    ("SFO_AIR_PASSENGERS", PRIOR_BROAD / "raw/sfo_air_passengers_aggregate.json", "data_payload", "2026-09-03T20:50:50Z"),
    ("SFO_AIR_PASSENGERS", PRIOR_BROAD / "raw/sfo_air_passengers_metadata.json", "dataset_metadata", "2026-09-03T20:50:50Z"),
    ("EUROSTAT_PLATFORM_NIGHTS", PRIOR_BROAD / "raw/eurostat_tour_ce_omr.json", "data_payload", "2026-09-03T20:50:17Z"),
]
raw_rows = [{
    "source_id": sid, "artifact_role": role, "raw_file": str(path.relative_to(REPO)),
    "bytes": path.stat().st_size, "sha256": sha256(path), "retrieved_at_utc": retrieved,
    "source_url": registry[sid]["source_url"], "reuse_status": "prior_governed_cache_reused_no_new_request",
} for sid, path, role, retrieved in raw_files]
write_csv(HERE / "raw_file_manifest.csv",
          ["source_id", "artifact_role", "raw_file", "bytes", "sha256", "retrieved_at_utc", "source_url", "reuse_status"],
          raw_rows)


request_gets = sum(row["provider_http_get_made"] == "true" for row in permission_rows)
data_gets = sum(row["data_payload_request"] == "true" and row["provider_http_get_made"] == "true" for row in permission_rows)
timing_violations = sum(row["manifest_precedes_request"] == "false" for row in permission_rows)
strict_observations = sum(row["strict_pit_eligible"] == "true" for row in observations)
strict_features = sum(row["strict_eligibility"] == "true" for row in feature_rows)

validation = {
    "run_id": RUN_ID, "built_at_utc": BUILT_AT, "status": "PASS_WITH_DISCLOSED_PERMISSION_MANIFEST_TIMING_EXCEPTION",
    "source_manifest_rows": len(source_rows), "permission_audit_rows": len(permission_rows),
    "permission_attempt_rows": sum(row["permission_attempt"] == "true" for row in permission_rows),
    "provider_permission_gets": request_gets, "new_data_payload_gets": data_gets,
    "permission_manifest_timing_violations": timing_violations,
    "observation_rows": len(observations), "sfo_rows": sum(r["source_id"] == "SFO_AIR_PASSENGERS" for r in observations),
    "eu27_rows": sum(r["source_id"] == "EUROSTAT_PLATFORM_NIGHTS" for r in observations),
    "strict_pit_observation_rows": strict_observations, "guidance_events": len(targets),
    "event_feature_rows": len(feature_rows), "strict_pit_feature_rows": strict_features,
    "hypotheses": ["H-007", "H-008", "H-009", "H-010", "H-011", "H-012"],
    "checks": {
        "all_required_source_ids_registered": all(sid in registry for sid in run_source_ids),
        "unique_observation_ids": len({str(r["observation_id"]) for r in observations}) == len(observations),
        "zero_new_data_payload_gets": data_gets == 0,
        "zero_strict_pit_observations": strict_observations == 0,
        "zero_strict_pit_features": strict_features == 0,
        "guidance_event_count_23": len(targets) == 23,
        "fixed_feature_rows_7_per_event": len(feature_rows) == 23 * 7,
        "no_pii_fields_in_observation_schema": not any(x in observation_fields for x in ["name", "address", "latitude", "longitude", "email", "phone"]),
        "permission_manifest_timing_exceptions_disclosed": timing_violations == 8,
    },
    "limitations": [
        "All normalized values are current-snapshot or prospective-only; strict PIT n is zero.",
        "Eight executed physical-lane permission-page GETs have manifest registered_at_utc later than requested_at_utc in the final lane artifacts (three FHWA and five airport rows). No data payload followed; these rows are retained and flagged, not rewritten.",
        "PANYNJ and LAX data paths did not pass the exact gate; no airport fallback payload was requested.",
        "Descriptive metrics are not a historical backtest and do not establish alpha or predictive power.",
    ],
}
assert all(validation["checks"].values())
(HERE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")


# Combined artifact inventory and checksums are written last.
artifact_names = [
    "run_plan.md", "source_manifest.csv", "permission_audit.csv", "observations_long.csv",
    "guidance_targets.csv", "event_aligned_features.csv", "descriptive_comparison.csv",
    "publication_vintage_audit.csv", "raw_file_manifest.csv", "validation.json", "lead_memo.md",
    "build_combined_sleeve.py",
]
artifact_rows = []
for name in artifact_names:
    path = HERE / name
    row_count = ""
    if path.suffix == ".csv":
        row_count = max(0, len(path.read_text(encoding="utf-8").splitlines()) - 1)
    artifact_rows.append({
        "artifact": name, "bytes": path.stat().st_size, "sha256": sha256(path),
        "row_count_if_csv": row_count, "generated_at_utc": BUILT_AT,
    })
write_csv(HERE / "artifact_manifest.csv",
          ["artifact", "bytes", "sha256", "row_count_if_csv", "generated_at_utc"], artifact_rows)
artifact_names.append("artifact_manifest.csv")
with (HERE / "checksums.sha256").open("w", encoding="utf-8") as handle:
    for name in artifact_names:
        handle.write(f"{sha256(HERE / name)}  {name}\n")
