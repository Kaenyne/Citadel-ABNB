from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PROCESSED = ROOT / "processed"
TARGET_MINIMUM = 100
COLLECTION_MONTH = "2026-09"

FIELDS = [
    "observation_id",
    "source_id",
    "provider",
    "collected_at_utc",
    "source_updated_at",
    "reference_period",
    "geography_code",
    "geography_name",
    "metric",
    "segment_1",
    "segment_2",
    "unit",
    "value",
    "status",
    "first_available_at_utc",
    "pit_treatment",
    "raw_file",
    "raw_row_key",
]

SOURCE_PROVIDERS = {
    "EUROSTAT_PLATFORM_NIGHTS_COUNTRY": "Eurostat",
    "EUROSTAT_PLATFORM_NIGHTS_REGION": "Eurostat",
    "EUROSTAT_PLATFORM_NIGHTS_NUTS3": "Eurostat",
    "EUROSTAT_TOURISM_NIGHTS": "Eurostat",
    "TORONTO_STR_PROGRAM": "City of Toronto",
    "SFO_AIR_PASSENGERS": "City and County of San Francisco",
    "STATCAN_ACCOM_PRICE": "Statistics Canada",
    "STATCAN_TRAVELLERS": "Statistics Canada",
    "UK_CAA_AIRPORT_PASSENGERS": "UK Civil Aviation Authority",
}


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(source_id: str, *parts: object) -> str:
    text = "|".join([source_id, *(str(part) for part in parts)])
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def dimension_codes(payload: dict, dim: str) -> list[str]:
    index = payload["dimension"][dim]["category"]["index"]
    if isinstance(index, list):
        return list(index)
    result = [""] * len(index)
    for code, position in index.items():
        result[int(position)] = code
    return result


def flatten_jsonstat(path: Path, source_id: str, platform: bool) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    dims = payload["id"]
    sizes = payload["size"]
    codes = {dim: dimension_codes(payload, dim) for dim in dims}
    labels = {
        dim: payload["dimension"][dim]["category"].get("label", {})
        for dim in dims
    }
    values = payload.get("value", {})
    if isinstance(values, list):
        items = ((str(i), value) for i, value in enumerate(values) if value is not None)
    else:
        items = values.items()
    collected = iso_mtime(path)
    updated = payload.get("updated", "")
    status_map = payload.get("status", {})
    rows: list[dict[str, str]] = []
    for flat_key, raw_value in items:
        if raw_value is None:
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(value):
            continue
        rem = int(flat_key)
        positions = [0] * len(sizes)
        for index in range(len(sizes) - 1, -1, -1):
            positions[index] = rem % sizes[index]
            rem //= sizes[index]
        coord = {dim: codes[dim][positions[i]] for i, dim in enumerate(dims)}
        time_code = coord.get("time", "")
        month_code = coord.get("month", "")
        if month_code.startswith("M") and len(month_code) == 3:
            reference_period = f"{time_code}-{month_code[1:]}"
        else:
            reference_period = time_code
        geo_code = coord.get("geo", "")
        geo_name = labels.get("geo", {}).get(geo_code, geo_code)
        indicator = coord.get("indic_to", "")
        if platform:
            metric = labels.get("indic_to", {}).get(indicator, indicator)
            segment_1 = labels.get("c_resid", {}).get(coord.get("c_resid", ""), coord.get("c_resid", ""))
            segment_2 = labels.get("month", {}).get(month_code, month_code)
        else:
            metric = "Nights spent at tourist accommodation establishments"
            segment_1 = labels.get("c_resid", {}).get(coord.get("c_resid", ""), coord.get("c_resid", ""))
            segment_2 = labels.get("nace_r2", {}).get(coord.get("nace_r2", ""), coord.get("nace_r2", ""))
        unit_code = coord.get("unit", "")
        unit = labels.get("unit", {}).get(unit_code, unit_code)
        row_key = ";".join(f"{dim}={coord.get(dim, '')}" for dim in dims)
        rows.append(
            {
                "observation_id": stable_id(source_id, row_key),
                "source_id": source_id,
                "provider": SOURCE_PROVIDERS[source_id],
                "collected_at_utc": collected,
                "source_updated_at": updated,
                "reference_period": reference_period,
                "geography_code": geo_code,
                "geography_name": geo_name,
                "metric": metric,
                "segment_1": segment_1,
                "segment_2": segment_2,
                "unit": unit,
                "value": format(value, ".15g"),
                "status": str(status_map.get(str(flat_key), "")),
                "first_available_at_utc": collected,
                "pit_treatment": "current_snapshot_prospective_only",
                "raw_file": path.name,
                "raw_row_key": str(flat_key),
            }
        )
    return rows


def parse_toronto(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata = json.loads((RAW / "toronto_str_package.json").read_text(encoding="utf-8"))["result"]
    updated = metadata.get("metadata_modified", "")
    collected = iso_mtime(path)
    rows = []
    month_numbers = {
        month: index
        for index, month in enumerate(
            ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            start=1,
        )
    }
    for item in payload:
        try:
            year = int(item["Year"])
            month = month_numbers[item["Month Name"]]
            value = float(item["Data Count"])
        except (KeyError, TypeError, ValueError):
            continue
        raw_key = str(item.get("_id", ""))
        rows.append(
            {
                "observation_id": stable_id("TORONTO_STR_PROGRAM", raw_key),
                "source_id": "TORONTO_STR_PROGRAM",
                "provider": SOURCE_PROVIDERS["TORONTO_STR_PROGRAM"],
                "collected_at_utc": collected,
                "source_updated_at": updated,
                "reference_period": f"{year:04d}-{month:02d}",
                "geography_code": "TORONTO",
                "geography_name": "Toronto",
                "metric": str(item["Data Name"]),
                "segment_1": str(item["Data Type"]),
                "segment_2": "",
                "unit": "count",
                "value": format(value, ".15g"),
                "status": "",
                "first_available_at_utc": collected,
                "pit_treatment": "current_snapshot_prospective_only",
                "raw_file": path.name,
                "raw_row_key": raw_key,
            }
        )
    return rows


def parse_sfo(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    collected = iso_mtime(path)
    rows = []
    for index, item in enumerate(payload, start=1):
        period = str(item.get("activity_period", ""))
        if len(period) != 6:
            continue
        try:
            value = float(item["passenger_count"])
        except (KeyError, TypeError, ValueError):
            continue
        reference_period = f"{period[:4]}-{period[4:]}"
        data_loaded = str(item.get("data_loaded_at", ""))
        raw_key = f"{period}|{item.get('geo_summary', '')}|{item.get('activity_type_code', '')}"
        rows.append(
            {
                "observation_id": stable_id("SFO_AIR_PASSENGERS", raw_key),
                "source_id": "SFO_AIR_PASSENGERS",
                "provider": SOURCE_PROVIDERS["SFO_AIR_PASSENGERS"],
                "collected_at_utc": collected,
                "source_updated_at": data_loaded,
                "reference_period": reference_period,
                "geography_code": "SFO",
                "geography_name": "San Francisco International Airport",
                "metric": "Passenger activity",
                "segment_1": str(item.get("geo_summary", "")),
                "segment_2": str(item.get("activity_type_code", "")),
                "unit": "passengers",
                "value": format(value, ".15g"),
                "status": "",
                "first_available_at_utc": collected,
                "pit_treatment": "current_snapshot_prospective_only",
                "raw_file": path.name,
                "raw_row_key": str(index),
            }
        )
    return rows


def zip_csv_rows(path: Path, member: str):
    with zipfile.ZipFile(path) as archive:
        with archive.open(member) as handle:
            wrapper = io.TextIOWrapper(handle, encoding="utf-8-sig", newline="")
            yield from csv.DictReader(wrapper)


def parse_statcan_price(path: Path) -> list[dict[str, str]]:
    collected = iso_mtime(path)
    source_updated = "2026-08-18"
    rows = []
    for item in zip_csv_rows(path, "18100249.csv"):
        period = item.get("REF_DATE", "")
        if period < "2018-01" or not item.get("VALUE"):
            continue
        try:
            value = float(item["VALUE"])
        except ValueError:
            continue
        raw_key = item.get("VECTOR", "") + "|" + period
        rows.append(
            {
                "observation_id": stable_id("STATCAN_ACCOM_PRICE", raw_key),
                "source_id": "STATCAN_ACCOM_PRICE",
                "provider": SOURCE_PROVIDERS["STATCAN_ACCOM_PRICE"],
                "collected_at_utc": collected,
                "source_updated_at": source_updated,
                "reference_period": period,
                "geography_code": item.get("DGUID", ""),
                "geography_name": item.get("GEO", ""),
                "metric": "Traveller accommodation services price index",
                "segment_1": item.get("Client groups", ""),
                "segment_2": "",
                "unit": item.get("UOM", ""),
                "value": format(value, ".15g"),
                "status": item.get("STATUS", ""),
                "first_available_at_utc": collected,
                "pit_treatment": "current_snapshot_prospective_only",
                "raw_file": path.name,
                "raw_row_key": raw_key,
            }
        )
    return rows


def parse_statcan_travellers(path: Path) -> list[dict[str, str]]:
    collected = iso_mtime(path)
    source_updated = "2026-08-20"
    accepted_geographies = {"Canada", "Ontario", "Quebec", "British Columbia"}
    accepted_types = {"Travellers", "Tourists (overnight)"}
    rows = []
    for item in zip_csv_rows(path, "24100054.csv"):
        period = item.get("REF_DATE", "")
        if period < "2018-01" or item.get("GEO") not in accepted_geographies or item.get("Traveller type") not in accepted_types or not item.get("VALUE"):
            continue
        try:
            value = float(item["VALUE"])
        except ValueError:
            continue
        raw_key = item.get("VECTOR", "") + "|" + period
        rows.append(
            {
                "observation_id": stable_id("STATCAN_TRAVELLERS", raw_key),
                "source_id": "STATCAN_TRAVELLERS",
                "provider": SOURCE_PROVIDERS["STATCAN_TRAVELLERS"],
                "collected_at_utc": collected,
                "source_updated_at": source_updated,
                "reference_period": period,
                "geography_code": item.get("DGUID", ""),
                "geography_name": item.get("GEO", ""),
                "metric": item.get("Traveller characteristics", ""),
                "segment_1": item.get("Traveller type", ""),
                "segment_2": "Seasonally adjusted",
                "unit": item.get("UOM", ""),
                "value": format(value, ".15g"),
                "status": item.get("STATUS", ""),
                "first_available_at_utc": collected,
                "pit_treatment": "current_snapshot_prospective_only",
                "raw_file": path.name,
                "raw_row_key": raw_key,
            }
        )
    return rows


def parse_caa(path: Path) -> list[dict[str, str]]:
    collected = iso_mtime(path)
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for index, item in enumerate(csv.DictReader(handle), start=1):
            period = item.get("this_period", "")
            if len(period) != 6:
                continue
            try:
                value = float(item["terminal_pax_this_period"])
            except (KeyError, TypeError, ValueError):
                continue
            reference_period = f"{period[:4]}-{period[4:]}"
            updated = item.get("rundate", "")
            airport = item.get("reporting_airport_name", "")
            raw_key = f"{period}|{airport}"
            rows.append(
                {
                    "observation_id": stable_id("UK_CAA_AIRPORT_PASSENGERS", raw_key),
                    "source_id": "UK_CAA_AIRPORT_PASSENGERS",
                    "provider": SOURCE_PROVIDERS["UK_CAA_AIRPORT_PASSENGERS"],
                    "collected_at_utc": collected,
                    "source_updated_at": updated,
                    "reference_period": reference_period,
                    "geography_code": airport,
                    "geography_name": airport,
                    "metric": "Terminal passengers",
                    "segment_1": item.get("reporting_airport_group_name", ""),
                    "segment_2": "",
                    "unit": "passengers",
                    "value": format(value, ".15g"),
                    "status": "",
                    "first_available_at_utc": collected,
                    "pit_treatment": "current_release",
                    "raw_file": path.name,
                    "raw_row_key": str(index),
                }
            )
    return rows


def raw_manifest() -> list[dict[str, object]]:
    records = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(
            {
                "file": path.name,
                "bytes": path.stat().st_size,
                "sha256": digest,
                "captured_at_utc": iso_mtime(path),
            }
        )
    return records


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    rows.extend(flatten_jsonstat(RAW / "eurostat_tour_ce_omr.json", "EUROSTAT_PLATFORM_NIGHTS_COUNTRY", platform=True))
    rows.extend(flatten_jsonstat(RAW / "eurostat_tour_ce_omn12.json", "EUROSTAT_PLATFORM_NIGHTS_REGION", platform=True))
    rows.extend(flatten_jsonstat(RAW / "eurostat_tour_ce_oan3.json", "EUROSTAT_PLATFORM_NIGHTS_NUTS3", platform=True))
    rows.extend(flatten_jsonstat(RAW / "eurostat_tour_occ_nim.json", "EUROSTAT_TOURISM_NIGHTS", platform=False))
    rows.extend(parse_toronto(RAW / "toronto_str_program_data.json"))
    rows.extend(parse_sfo(RAW / "sfo_air_passengers_aggregate.json"))
    rows.extend(parse_statcan_price(RAW / "statcan_18100249-eng.zip"))
    rows.extend(parse_statcan_travellers(RAW / "statcan_24100054-eng.zip"))
    rows.extend(parse_caa(RAW / "uk_caa_2026_05_table09.csv"))

    valid = []
    rejected = []
    seen: set[str] = set()
    duplicate_count = 0
    for row in rows:
        reason = ""
        if not row["reference_period"]:
            reason = "missing_reference_period"
        elif len(row["reference_period"]) == 7 and row["reference_period"] > COLLECTION_MONTH:
            reason = "future_reference_period"
        elif not row["source_id"] or not row["metric"]:
            reason = "missing_identity"
        else:
            try:
                value = float(row["value"])
                if not math.isfinite(value):
                    reason = "nonfinite_value"
            except ValueError:
                reason = "nonnumeric_value"
        if row["observation_id"] in seen:
            duplicate_count += 1
            reason = "duplicate_observation_id"
        if reason:
            rejected.append({**row, "rejection_reason": reason})
            continue
        seen.add(row["observation_id"])
        valid.append(row)

    valid.sort(key=lambda row: (row["source_id"], row["reference_period"], row["geography_code"], row["metric"], row["segment_1"], row["segment_2"]))
    with (PROCESSED / "valid_observations.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(valid)

    with (PROCESSED / "rejected_observations.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*FIELDS, "rejection_reason"])
        writer.writeheader()
        writer.writerows(rejected)

    counts = Counter(row["source_id"] for row in valid)
    summary_fields = ["source_id", "provider", "valid_observations", "min_reference_period", "max_reference_period", "distinct_geographies", "distinct_metrics", "pit_treatment"]
    summaries = []
    for source_id in sorted(counts):
        subset = [row for row in valid if row["source_id"] == source_id]
        summaries.append(
            {
                "source_id": source_id,
                "provider": SOURCE_PROVIDERS[source_id],
                "valid_observations": len(subset),
                "min_reference_period": min(row["reference_period"] for row in subset),
                "max_reference_period": max(row["reference_period"] for row in subset),
                "distinct_geographies": len({row["geography_code"] for row in subset}),
                "distinct_metrics": len({row["metric"] for row in subset}),
                "pit_treatment": ";".join(sorted({row["pit_treatment"] for row in subset})),
            }
        )
    with (PROCESSED / "source_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summaries)

    raw_files = raw_manifest()
    with (PROCESSED / "raw_file_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "bytes", "sha256", "captured_at_utc"])
        writer.writeheader()
        writer.writerows(raw_files)

    validation = {
        "target_minimum_valid_observations": TARGET_MINIMUM,
        "valid_observations": len(valid),
        "rejected_observations": len(rejected),
        "duplicate_observation_ids": duplicate_count,
        "distinct_sources": len(counts),
        "distinct_providers": len({SOURCE_PROVIDERS[source_id] for source_id in counts}),
        "source_counts": dict(sorted(counts.items())),
        "raw_files": len(raw_files),
        "passed_minimum": len(valid) >= TARGET_MINIMUM,
        "all_sources_nonempty": all(counts.get(source_id, 0) > 0 for source_id in SOURCE_PROVIDERS),
        "pit_warning": "Except for the current UK CAA release, rows represent current provider snapshots. Historical observation dates must not be treated as original first-availability vintages.",
    }
    (PROCESSED / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
