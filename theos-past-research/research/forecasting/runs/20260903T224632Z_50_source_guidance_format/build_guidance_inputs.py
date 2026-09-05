from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
SOURCE_RUN = REPO / "research" / "edge-discovery" / "20260903T211121Z_50_source_expansion"
BASELINE_RUN = REPO / "research" / "edge-discovery" / "20260903T204950Z_broad_scrape"
GUIDANCE_PATH = REPO / "research" / "readiness" / "20260903T053309Z_abnb_readiness" / "target_panel.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def family(source_id: str) -> str:
    if "PLATFORM_NIGHTS" in source_id or "TOUR_CE_" in source_id:
        return "Collaborative-platform activity"
    if "TOUR_CAP_" in source_id:
        return "Accommodation capacity"
    if "TOURISM_NIGHTS" in source_id or "TOUR_OCC_" in source_id:
        if "MNOR" in source_id or "ANOR" in source_id:
            return "Hotel occupancy / pricing"
        return "Tourism demand / occupancy"
    if source_id == "TORONTO_STR_PROGRAM":
        return "STR regulatory supply"
    if source_id == "STATCAN_ACCOM_PRICE":
        return "Accommodation pricing"
    if source_id == "STATCAN_TRAVELLERS":
        return "Traveller flows"
    return "Aviation / physical travel"


def mapping(source_id: str) -> dict[str, object]:
    source_family = family(source_id)
    pit_score = 2 if source_id == "UK_CAA_AIRPORT_PASSENGERS" else 1

    if source_family == "Collaborative-platform activity":
        frequency = 5 if source_id == "EUROSTAT_PLATFORM_NIGHTS_COUNTRY" else (4 if source_id == "EUROSTAT_PLATFORM_NIGHTS_REGION" else 2)
        timeliness = 3 if source_id == "EUROSTAT_PLATFORM_NIGHTS_COUNTRY" else 2
        return {
            "family": source_family,
            "operating_bridge": "Platform guest nights → ABNB Nights & Experiences Booked → GBV → revenue",
            "abnb_kpi": "Nights & Experiences Booked",
            "proposed_transformation": "YoY guest-night growth; positive-growth geography breadth; international mix; platform share versus total lodging",
            "expected_sign": "positive",
            "cadence": "monthly" if frequency >= 4 else "annual",
            "directness_score": 5,
            "timeliness_score": timeliness,
            "frequency_score": frequency,
            "geography_score": 4,
            "pit_score": pit_score,
        }
    if source_family == "Tourism demand / occupancy":
        monthly = source_id in {
            "EUROSTAT_TOURISM_NIGHTS",
            "EUROSTAT_TOUR_OCC_ARM",
            "EUROSTAT_TOUR_OCC_NIN2M",
        }
        return {
            "family": source_family,
            "operating_bridge": "Destination lodging demand → ABNB trip volume → nights → revenue",
            "abnb_kpi": "Nights & Experiences Booked",
            "proposed_transformation": "YoY nights/arrivals growth; regional breadth; short-stay growth minus all-accommodation growth",
            "expected_sign": "positive",
            "cadence": "monthly" if monthly else "annual",
            "directness_score": 4,
            "timeliness_score": 5 if source_id in {"EUROSTAT_TOURISM_NIGHTS", "EUROSTAT_TOUR_OCC_ARM"} else 3,
            "frequency_score": 5 if monthly else 2,
            "geography_score": 4,
            "pit_score": pit_score,
        }
    if source_family == "Hotel occupancy / pricing":
        monthly = source_id == "EUROSTAT_TOUR_OCC_MNOR"
        return {
            "family": source_family,
            "operating_bridge": "Hotel occupancy pressure → lodging pricing/availability → ABNB ADR and GBV → revenue",
            "abnb_kpi": "GBV / implied ADR",
            "proposed_transformation": "YoY percentage-point change in bed/room occupancy; regional occupancy breadth",
            "expected_sign": "positive",
            "cadence": "monthly" if monthly else "annual",
            "directness_score": 3,
            "timeliness_score": 5 if monthly else 3,
            "frequency_score": 5 if monthly else 2,
            "geography_score": 4,
            "pit_score": pit_score,
        }
    if source_family == "Accommodation capacity":
        return {
            "family": source_family,
            "operating_bridge": "Lodging capacity → supply availability and substitution → ABNB nights/ADR → revenue",
            "abnb_kpi": "Active listings / nights / implied ADR",
            "proposed_transformation": "YoY change in establishments, bedrooms and bed places; holiday-accommodation share; regional supply breadth",
            "expected_sign": "ambiguous",
            "cadence": "annual",
            "directness_score": 2,
            "timeliness_score": 4,
            "frequency_score": 2,
            "geography_score": 4,
            "pit_score": pit_score,
        }
    if source_family == "STR regulatory supply":
        return {
            "family": source_family,
            "operating_bridge": "Registrations/approvals/enforcement → legal STR capacity → ABNB nights and ADR → revenue",
            "abnb_kpi": "Active listings / Nights & Experiences Booked",
            "proposed_transformation": "TTM net approvals less denials/revocations; enforcement intensity; complaint rate",
            "expected_sign": "net supply positive; enforcement negative",
            "cadence": "monthly",
            "directness_score": 4,
            "timeliness_score": 5,
            "frequency_score": 5,
            "geography_score": 2,
            "pit_score": pit_score,
        }
    if source_family == "Accommodation pricing":
        return {
            "family": source_family,
            "operating_bridge": "Accommodation price inflation → ABNB ADR/GBV → revenue",
            "abnb_kpi": "GBV / implied ADR",
            "proposed_transformation": "YoY traveller-accommodation price-index growth and acceleration",
            "expected_sign": "positive",
            "cadence": "monthly; stale after 2019",
            "directness_score": 3,
            "timeliness_score": 1,
            "frequency_score": 5,
            "geography_score": 2,
            "pit_score": pit_score,
        }
    if source_family == "Traveller flows":
        return {
            "family": source_family,
            "operating_bridge": "International overnight travellers → Canadian destination nights → ABNB revenue",
            "abnb_kpi": "Nights & Experiences Booked",
            "proposed_transformation": "YoY overnight non-resident visitors by entry province; positive-growth province breadth",
            "expected_sign": "positive",
            "cadence": "monthly",
            "directness_score": 3,
            "timeliness_score": 5,
            "frequency_score": 5,
            "geography_score": 2,
            "pit_score": pit_score,
        }

    if source_id in {"SFO_AIR_PASSENGERS", "UK_CAA_AIRPORT_PASSENGERS"} or "AVIA_TF_" in source_id:
        timeliness = 5
        frequency = 5
    elif "AVIA_PAR_" in source_id:
        timeliness = 1
        frequency = 4
    else:
        timeliness = 4
        frequency = 4
    geography = 2 if source_id == "SFO_AIR_PASSENGERS" else (3 if source_id == "UK_CAA_AIRPORT_PASSENGERS" else 4)
    return {
        "family": source_family,
        "operating_bridge": "Passenger/flight activity → trip formation and destination demand → ABNB nights → revenue",
        "abnb_kpi": "Nights & Experiences Booked",
        "proposed_transformation": "YoY passenger/flight growth; positive-growth airport breadth; international mix; route breadth",
        "expected_sign": "positive",
        "cadence": "monthly/quarterly",
        "directness_score": 3,
        "timeliness_score": timeliness,
        "frequency_score": frequency,
        "geography_score": geography,
        "pit_score": pit_score,
    }


def main() -> None:
    source_manifest = read_csv(SOURCE_RUN / "source_manifest_50.csv")
    source_summary = {row["source_id"]: row for row in read_csv(SOURCE_RUN / "source_summary_50.csv")}
    guidance = read_csv(GUIDANCE_PATH)

    first_available: dict[str, str] = {}
    for row in read_csv(BASELINE_RUN / "processed" / "valid_observations.csv"):
        sid = row["source_id"]
        stamp = row["first_available_at_utc"]
        if stamp and (sid not in first_available or stamp < first_available[sid]):
            first_available[sid] = stamp
    for row in read_csv(SOURCE_RUN / "processed" / "raw_file_manifest.csv"):
        sid = "EUROSTAT_" + Path(row["file"]).stem.upper()
        first_available[sid] = row["captured_at_utc"]

    weights = {
        "directness_score": 0.30,
        "timeliness_score": 0.20,
        "frequency_score": 0.20,
        "geography_score": 0.15,
        "pit_score": 0.15,
    }
    crosswalk: list[dict[str, object]] = []
    for source in source_manifest:
        sid = source["source_id"]
        spec = mapping(sid)
        score = sum(float(spec[key]) * weight for key, weight in weights.items())
        summary = source_summary[sid]
        crosswalk.append(
            {
                "source_id": sid,
                "provider": source["provider"],
                "dataset_name": source["dataset_name"],
                **spec,
                "guidance_target": "Revenue-guidance midpoint YoY residual vs same guided quarter prior year",
                "coverage_start": summary["min_reference_period"],
                "coverage_end": summary["max_reference_period"],
                "valid_observations": int(summary["valid_observations"]),
                "weighted_score": round(score, 2),
                "forecast_approval": "discovery_only_not_approved",
                "historical_eligibility": False,
                "first_available_at_utc": first_available[sid],
                "earliest_prospective_use": "First ABNB guidance cutoff strictly after collection, only after manifest approval",
                "caveat": source["caveat"],
                "source_url": source["dataset_url"],
            }
        )
    crosswalk.sort(key=lambda row: (-float(row["weighted_score"]), str(row["source_id"])))
    for rank, row in enumerate(crosswalk, start=1):
        row["priority_rank"] = rank

    crosswalk_fields = [
        "priority_rank", "source_id", "provider", "dataset_name", "family", "operating_bridge",
        "abnb_kpi", "guidance_target", "proposed_transformation", "expected_sign", "cadence",
        "coverage_start", "coverage_end", "valid_observations", "directness_score", "timeliness_score",
        "frequency_score", "geography_score", "pit_score", "weighted_score", "forecast_approval",
        "historical_eligibility", "first_available_at_utc", "earliest_prospective_use", "caveat", "source_url",
    ]
    write_csv(ROOT / "source_guidance_crosswalk.csv", crosswalk, crosswalk_fields)

    guidance_rows: list[dict[str, object]] = []
    for index, row in enumerate(guidance, start=1):
        guidance_rows.append(
            {
                "event_index": index,
                "prediction_id": row["prediction_id"],
                "issuing_fiscal_period": row["issuing_fiscal_period"],
                "guided_fiscal_period": row["guided_fiscal_period"],
                "guidance_available_at_utc": row["guidance_available_at_utc"],
                "target_metric": row["target_metric"],
                "target_type": row["target_type"],
                "target_low": row["target_low"],
                "target_high": row["target_high"],
                "target_midpoint": row["target_midpoint"],
                "target_unit": row["target_unit"],
                "currency": row["currency"],
                "target_source_id": row["target_source_id"],
                "target_citation": row["target_citation"],
                "target_confidence": row["target_confidence"],
                "notes": row["discrepancy_notes"],
            }
        )
    guidance_fields = list(guidance_rows[0])
    write_csv(ROOT / "guidance_history.csv", guidance_rows, guidance_fields)

    eligibility: list[dict[str, object]] = []
    for event in guidance_rows:
        cutoff = datetime.fromisoformat(str(event["guidance_available_at_utc"]).replace("Z", "+00:00"))
        for source in crosswalk:
            available = datetime.fromisoformat(str(source["first_available_at_utc"]).replace("Z", "+00:00"))
            timing_pass = available < cutoff
            approval_pass = source["forecast_approval"] == "approved_for_forecasting"
            reasons = []
            if not timing_pass:
                reasons.append("first availability is not strictly before the guidance cutoff")
            if not approval_pass:
                reasons.append("evidence manifest is discovery-only, not approved_for_forecasting")
            eligibility.append(
                {
                    "prediction_id": event["prediction_id"],
                    "issuing_fiscal_period": event["issuing_fiscal_period"],
                    "guided_fiscal_period": event["guided_fiscal_period"],
                    "guidance_cutoff_at_utc": event["guidance_available_at_utc"],
                    "target_type": event["target_type"],
                    "target_midpoint": event["target_midpoint"],
                    "source_rank": source["priority_rank"],
                    "source_id": source["source_id"],
                    "first_available_at_utc": source["first_available_at_utc"],
                    "forecast_approval": source["forecast_approval"],
                    "timing_pass": timing_pass,
                    "approval_pass": approval_pass,
                    "strictly_eligible": timing_pass and approval_pass,
                    "exclusion_reason": "; ".join(reasons),
                    "guidance_comparison_target": source["guidance_target"],
                    "expected_sign": source["expected_sign"],
                }
            )
    eligibility_fields = list(eligibility[0])
    write_csv(ROOT / "historical_eligibility_matrix.csv", eligibility, eligibility_fields)

    report = {
        "sources": len(crosswalk),
        "guidance_events": len(guidance_rows),
        "numeric_guidance_events": sum(row["target_type"] == "numeric_range" for row in guidance_rows),
        "source_event_pairs": len(eligibility),
        "strictly_eligible_historical_pairs": sum(bool(row["strictly_eligible"]) for row in eligibility),
        "comparison_target": "Revenue-guidance midpoint residual versus same guided quarter one year earlier",
        "forecast_status": "FORMAT_READY_NOT_APPROVED_FOR_FORECASTING",
    }
    workbook_inputs = {
        "crosswalk": crosswalk,
        "guidance": guidance_rows,
        "eligibility": eligibility,
        "weights": weights,
        "validation": report,
    }
    (ROOT / "workbook_inputs.json").write_text(
        json.dumps(workbook_inputs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (ROOT / "format_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
