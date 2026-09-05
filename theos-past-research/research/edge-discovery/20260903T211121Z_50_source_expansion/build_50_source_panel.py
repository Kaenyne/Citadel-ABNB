from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PROCESSED = ROOT / "processed"
BASELINE = ROOT.parent / "20260903T204950Z_broad_scrape"
TOC = ROOT / "metadata" / "eurostat_toc_20260903.txt"

DATASET_CODES = [
    "tour_ce_oarc",
    "tour_ce_oar",
    "tour_ce_oaw",
    "tour_ce_oam",
    "tour_ce_oasc",
    "tour_occ_arm",
    "tour_occ_mnor",
    "tour_occ_ninat",
    "tour_occ_ninraw",
    "tour_occ_ninats",
    "tour_occ_nin2m",
    "tour_occ_nin3",
    "tour_occ_ninc",
    "tour_occ_ninatdc",
    "tour_occ_nin2dc",
    "tour_occ_arnat",
    "tour_occ_arn2",
    "tour_occ_arnraw",
    "tour_occ_anor",
    "tour_occ_anor2",
    "tour_cap_nat",
    "tour_cap_nuts2",
    "tour_cap_nats",
    "tour_cap_natdc",
    "tour_cap_nuts2dc",
    "avia_tf_cm",
    "avia_tf_airpm",
    "avia_paoc",
    "avia_paoa",
    "avia_paocc",
    "avia_paoac",
    "avia_paodis",
    "avia_paexcc",
    "avia_paexac",
    "avia_par_ie",
    "avia_par_es",
    "avia_par_fr",
    "avia_par_it",
    "avia_par_pt",
    "avia_par_nl",
    "avia_par_el",
]

OBSERVATION_FIELDS = [
    "observation_id",
    "source_id",
    "provider",
    "dataset_code",
    "collected_at_utc",
    "source_updated_at",
    "reference_period",
    "geography_code",
    "geography_name",
    "metric",
    "unit",
    "value",
    "status",
    "first_available_at_utc",
    "pit_treatment",
    "dimensions_json",
    "raw_file",
    "raw_row_key",
]

MANIFEST_FIELDS = [
    "source_id",
    "provider",
    "dataset_name",
    "dataset_url",
    "terms_url",
    "reuse_status",
    "access_method",
    "cost",
    "personal_data_retained",
    "retained_granularity",
    "pit_treatment",
    "forecast_linkage",
    "caveat",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def iso_mtime(path: Path) -> str:
    value = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def source_id(code: str) -> str:
    return "EUROSTAT_" + code.upper()


def stable_id(source: str, row_key: str) -> str:
    return hashlib.sha256(f"{source}|{row_key}".encode("utf-8")).hexdigest()[:20]


def dimension_codes(payload: dict, dim: str) -> list[str]:
    index = payload["dimension"][dim]["category"]["index"]
    if isinstance(index, list):
        return list(index)
    result = [""] * len(index)
    for code, position in index.items():
        result[int(position)] = code
    return result


def toc_metadata() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    with TOC.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if len(row) < 8 or row[1] not in DATASET_CODES or row[2] != "dataset":
                continue
            result.setdefault(
                row[1],
                {
                    "title": row[0].strip(),
                    "catalogue_last_update": row[3],
                    "catalogue_structure_update": row[4],
                    "catalogue_data_start": row[5],
                    "catalogue_data_end": row[6],
                    "catalogue_values": row[7],
                },
            )
    missing = sorted(set(DATASET_CODES) - set(result))
    if missing:
        raise ValueError(f"Codes missing from official catalogue snapshot: {missing}")
    return result


def family_and_linkage(code: str) -> tuple[str, str]:
    if code.startswith("tour_ce_"):
        return "platform-activity", "Collaborative-platform demand, mix, geographic breadth, or accommodation structure"
    if code.startswith("tour_cap_"):
        return "accommodation-capacity", "Accommodation supply, market capacity, and possible STR substitution control"
    if code.startswith("tour_occ_"):
        return "tourism-occupancy", "Accommodation demand, pricing pressure, occupancy, and destination breadth control"
    if code.startswith("avia_tf_"):
        return "commercial-flights", "High-frequency physical travel-activity and destination-breadth proxy"
    if code.startswith("avia_par_"):
        return "airport-routes", "Country-specific international route depth and travel-connectivity proxy"
    return "air-passengers", "Passenger demand, origin mix, and cross-border travel-volume proxy"


def flatten(path: Path, metadata: dict[str, str]) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    dims = payload["id"]
    sizes = payload["size"]
    codes = {dim: dimension_codes(payload, dim) for dim in dims}
    labels = {
        dim: payload["dimension"][dim]["category"].get("label", {})
        for dim in dims
    }
    values = payload.get("value", {})
    items = (
        ((str(index), value) for index, value in enumerate(values) if value is not None)
        if isinstance(values, list)
        else values.items()
    )
    statuses = payload.get("status", {})
    collected = iso_mtime(path)
    source = source_id(path.stem)
    rows: list[dict[str, object]] = []

    for flat_key, raw_value in items:
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(value):
            continue

        remainder = int(flat_key)
        positions = [0] * len(sizes)
        for index in range(len(sizes) - 1, -1, -1):
            positions[index] = remainder % sizes[index]
            remainder //= sizes[index]
        coordinate = {dim: codes[dim][positions[i]] for i, dim in enumerate(dims)}
        labelled = {
            dim: labels[dim].get(code, code)
            for dim, code in coordinate.items()
        }

        period = coordinate.get("time", "")
        month = coordinate.get("month", "")
        if len(period) == 4 and month.startswith("M") and len(month) == 3:
            period = f"{period}-{month[1:]}"

        geography_dimension = next(
            (dim for dim in ("geo", "cities", "rep_airp", "airp_pr", "partner") if coordinate.get(dim)),
            "",
        )
        geography_code = coordinate.get(geography_dimension, "")
        geography_name = labelled.get(geography_dimension, geography_code)
        row_key = ";".join(f"{dim}={coordinate[dim]}" for dim in dims)
        status = statuses.get(str(flat_key), "") if isinstance(statuses, dict) else ""

        rows.append(
            {
                "observation_id": stable_id(source, row_key),
                "source_id": source,
                "provider": "Eurostat",
                "dataset_code": path.stem,
                "collected_at_utc": collected,
                "source_updated_at": payload.get("updated", metadata["catalogue_last_update"]),
                "reference_period": period,
                "geography_code": geography_code,
                "geography_name": geography_name,
                "metric": metadata["title"],
                "unit": labelled.get("unit", coordinate.get("unit", "")),
                "value": format(value, ".15g"),
                "status": status,
                "first_available_at_utc": collected,
                "pit_treatment": "current_snapshot_prospective_only",
                "dimensions_json": json.dumps(labelled, ensure_ascii=False, sort_keys=True),
                "raw_file": path.name,
                "raw_row_key": str(flat_key),
            }
        )
    return rows


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    metadata = toc_metadata()
    observations: list[dict[str, object]] = []
    new_manifest: list[dict[str, object]] = []
    raw_manifest: list[dict[str, object]] = []

    for code in DATASET_CODES:
        path = RAW / f"{code}.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        family, linkage = family_and_linkage(code)
        rows = flatten(path, metadata[code])
        if not rows:
            raise ValueError(f"No numeric observations in {path.name}")
        observations.extend(rows)

        suffix = "&partner=US" if code == "avia_paexac" else ""
        new_manifest.append(
            {
                "source_id": source_id(code),
                "provider": "Eurostat",
                "dataset_name": metadata[code]["title"],
                "dataset_url": f"https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table",
                "terms_url": "https://ec.europa.eu/eurostat/help/copyright-notice",
                "reuse_status": "allowed_with_attribution",
                "access_method": f"Official Statistics API lastTimePeriod=1{suffix}",
                "cost": "free",
                "personal_data_retained": "false",
                "retained_granularity": f"{family}-latest-provider-snapshot",
                "pit_treatment": "current_snapshot_prospective_only",
                "forecast_linkage": linkage,
                "caveat": "Latest provider snapshot; revisions and cross-source dependence require prospective point-in-time testing",
            }
        )
        raw_manifest.append(
            {
                "file": path.name,
                "query_url": (
                    f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{code}"
                    f"?lang=en&lastTimePeriod=1{suffix}"
                ),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "captured_at_utc": iso_mtime(path),
                "numeric_observations": len(rows),
            }
        )

    write_csv(PROCESSED / "new_observations.csv", observations, OBSERVATION_FIELDS)
    write_csv(PROCESSED / "new_source_manifest.csv", new_manifest, MANIFEST_FIELDS)
    write_csv(
        PROCESSED / "raw_file_manifest.csv",
        raw_manifest,
        ["file", "query_url", "bytes", "sha256", "captured_at_utc", "numeric_observations"],
    )

    baseline_manifest = read_csv(BASELINE / "source_manifest.csv")
    consolidated_manifest = baseline_manifest + new_manifest
    write_csv(ROOT / "source_manifest_50.csv", consolidated_manifest, MANIFEST_FIELDS)

    counts = Counter(str(row["source_id"]) for row in observations)
    new_summary = []
    for row in new_manifest:
        sid = str(row["source_id"])
        source_rows = [item for item in observations if item["source_id"] == sid]
        periods = [str(item["reference_period"]) for item in source_rows if item["reference_period"]]
        new_summary.append(
            {
                "source_id": sid,
                "provider": "Eurostat",
                "valid_observations": counts[sid],
                "min_reference_period": min(periods) if periods else "",
                "max_reference_period": max(periods) if periods else "",
                "distinct_geographies": len({item["geography_code"] for item in source_rows}),
                "distinct_metrics": 1,
                "pit_treatment": "current_snapshot_prospective_only",
            }
        )
    baseline_summary = read_csv(BASELINE / "processed" / "source_summary.csv")
    summary_fields = list(baseline_summary[0])
    write_csv(ROOT / "source_summary_50.csv", baseline_summary + new_summary, summary_fields)

    baseline_validation = json.loads(
        (BASELINE / "processed" / "validation.json").read_text(encoding="utf-8")
    )
    ids = [str(row["observation_id"]) for row in observations]
    source_ids = [str(row["source_id"]) for row in consolidated_manifest]
    report = {
        "requested_total_sources": 50,
        "baseline_sources": len(baseline_manifest),
        "new_sources": len(new_manifest),
        "consolidated_sources": len(consolidated_manifest),
        "new_valid_observations": len(observations),
        "baseline_valid_observations": baseline_validation["valid_observations"],
        "total_referenced_observations": len(observations) + baseline_validation["valid_observations"],
        "new_raw_files": len(raw_manifest),
        "nonempty_new_sources": len(counts),
        "duplicate_new_observation_ids": len(ids) - len(set(ids)),
        "duplicate_source_ids": len(source_ids) - len(set(source_ids)),
        "all_sources_free": all(str(row["cost"]) == "free" for row in consolidated_manifest),
        "no_personal_data_retained": all(
            str(row["personal_data_retained"]).lower() == "false"
            for row in consolidated_manifest
        ),
        "passed_50_source_gate": (
            len(consolidated_manifest) == 50
            and len(counts) == 41
            and len(ids) == len(set(ids))
            and len(source_ids) == len(set(source_ids))
        ),
        "provider_concentration_warning": "The 41 added datasets are distinct Eurostat products but share one provider and licence regime.",
        "pit_warning": "The expansion contains latest provider snapshots and is eligible only for prospective forecasting from collection time.",
    }
    (PROCESSED / "validation_50.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
