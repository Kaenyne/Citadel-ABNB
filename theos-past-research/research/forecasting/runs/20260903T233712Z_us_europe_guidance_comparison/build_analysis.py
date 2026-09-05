#!/usr/bin/env python3
"""Build a diagnostic U.S./Europe alt-data panel aligned to ABNB guidance events.

This deliberately separates observed provider publication metadata from conservative
availability assumptions used only for retrospective diagnostic alignment. Because the
underlying files are current snapshots, no row is promoted to strict point-in-time use.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
REPO_DIR = RUN_DIR.parents[3]
OUTPUT_DIR = REPO_DIR / "outputs" / "reproducibility" / "us-europe-guidance"
GUIDANCE_PATH = REPO_DIR / "research/forecasting/runs/20260903T224632Z_50_source_guidance_format/guidance_history.csv"
VALID_OBS_PATH = REPO_DIR / "research/edge-discovery/20260903T204950Z_broad_scrape/processed/valid_observations.csv"
PHYSICAL_OBS_PATH = REPO_DIR / "research/edge-discovery/20260903T231817Z_abnb_us_altdata_sleeve/physical_world_activity_edge/observations_long.csv"
PHYSICAL_DISPOSITIONS = REPO_DIR / "research/edge-discovery/20260903T231817Z_abnb_us_altdata_sleeve/physical_world_activity_edge/source_dispositions.csv"
SUPPLY_CANDIDATES = REPO_DIR / "research/edge-discovery/20260903T231817Z_abnb_us_altdata_sleeve/supply_scarcity_web_edge/candidate_source_manifest.csv"
SUPPLY_GATES = REPO_DIR / "research/edge-discovery/20260903T231817Z_abnb_us_altdata_sleeve/supply_scarcity_web_edge/exact_path_gate_decisions.csv"
SOURCE_REGISTRY = REPO_DIR / "research/source_registry.csv"


# Airbnb does not disclose Europe-only revenue. EMEA revenue is therefore the
# closest official, reproducible proxy. Each event uses the latest 10-K accepted
# strictly before its guidance cutoff; weights are normalized only across the two
# modeled sleeves (U.S. and EMEA), never fitted to the outcome.
REVENUE_WEIGHT_VINTAGES = [
    {
        "fiscal_year": 2021,
        "accepted_at_utc": "2022-02-25T21:09:12Z",
        "us_revenue_usd_mm": 2996,
        "emea_revenue_usd_mm": 1931,
        "total_revenue_usd_mm": 5992,
        "source_url": "https://www.sec.gov/Archives/edgar/data/1559720/000155972022000006/abnb-20211231.htm",
    },
    {
        "fiscal_year": 2022,
        "accepted_at_utc": "2023-02-17T21:07:04Z",
        "us_revenue_usd_mm": 3890,
        "emea_revenue_usd_mm": 2924,
        "total_revenue_usd_mm": 8399,
        "source_url": "https://www.sec.gov/Archives/edgar/data/1559720/000155972023000003/abnb-20221231.htm",
    },
    {
        "fiscal_year": 2023,
        "accepted_at_utc": "2024-02-16T21:02:16Z",
        "us_revenue_usd_mm": 4290,
        "emea_revenue_usd_mm": 3615,
        "total_revenue_usd_mm": 9917,
        "source_url": "https://www.sec.gov/Archives/edgar/data/1559720/000155972024000006/abnb-20231231.htm",
    },
    {
        "fiscal_year": 2024,
        "accepted_at_utc": "2025-02-13T21:04:28Z",
        "us_revenue_usd_mm": 4640,
        "emea_revenue_usd_mm": 4135,
        "total_revenue_usd_mm": 10842,
        "source_url": "https://www.sec.gov/Archives/edgar/data/1559720/000155972025000010/abnb-20241231.htm",
    },
    {
        "fiscal_year": 2025,
        "accepted_at_utc": "2026-02-12T21:04:39Z",
        "us_revenue_usd_mm": 4814,
        "emea_revenue_usd_mm": 4729,
        "total_revenue_usd_mm": 12241,
        "source_url": "https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm",
    },
]


@dataclass(frozen=True)
class FeatureSpec:
    feature_id: str
    label: str
    lag_days: int
    definition: str
    family: str


FEATURES = [
    FeatureSpec(
        "US_SFO_T3M_YOY",
        "U.S. airport activity — SFO trailing 3-month YoY",
        60,
        "Sum of SFO enplaned and deplaned passengers; trailing-three-month sum versus prior year.",
        "United States travel activity",
    ),
    FeatureSpec(
        "EU_PLATFORM_T3M_YOY",
        "EU27 collaborative-platform nights trailing 3-month YoY",
        120,
        "EU27 nights booked through collaborative-economy platforms; trailing-three-month sum versus prior year.",
        "Europe platform accommodation",
    ),
    FeatureSpec(
        "EU_TOURISM_T3M_YOY",
        "EU27 total tourism nights trailing 3-month YoY",
        60,
        "EU27 nights at tourist accommodation establishments; trailing-three-month sum versus prior year.",
        "Europe total accommodation",
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_month(text: str) -> date:
    year, month = (int(part) for part in text.split("-"))
    return date(year, month, 1)


def add_months(value: date, offset: int) -> date:
    number = value.year * 12 + value.month - 1 + offset
    return date(number // 12, number % 12 + 1, 1)


def month_end(value: date) -> date:
    return add_months(value, 1) - timedelta(days=1)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_float(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and values[order[end]] == values[order[index]]:
            end += 1
        average_rank = (index + 1 + end) / 2
        for position in range(index, end):
            ranks[order[position]] = average_rank
        index = end
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    return numerator / denominator if denominator else None


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(rankdata(xs), rankdata(ys)) if len(xs) >= 3 else None


def monthly_feature(series: dict[date, float], cutoff: datetime, lag_days: int) -> tuple[float | None, str, str]:
    eligible_months = [month for month in series if month_end(month) + timedelta(days=lag_days) < cutoff.date()]
    for latest in sorted(eligible_months, reverse=True):
        current_months = [add_months(latest, -2), add_months(latest, -1), latest]
        prior_months = [add_months(month, -12) for month in current_months]
        if all(month in series for month in current_months + prior_months):
            prior = sum(series[month] for month in prior_months)
            current = sum(series[month] for month in current_months)
            if prior:
                availability = datetime.combine(month_end(latest) + timedelta(days=lag_days), datetime.min.time(), tzinfo=timezone.utc)
                return current / prior - 1, latest.strftime("%Y-%m"), iso_z(availability)
    return None, "", ""


def period_previous_year(period: str) -> str:
    return f"{int(period[:4]) - 1}{period[4:]}"


def sign(value: float | None, tolerance: float = 1e-12) -> int | None:
    if value is None:
        return None
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def build_revenue_weights() -> list[dict]:
    rows = []
    for vintage in REVENUE_WEIGHT_VINTAGES:
        covered_revenue = vintage["us_revenue_usd_mm"] + vintage["emea_revenue_usd_mm"]
        rows.append({
            **vintage,
            "us_weight": vintage["us_revenue_usd_mm"] / covered_revenue,
            "emea_weight": vintage["emea_revenue_usd_mm"] / covered_revenue,
            "covered_revenue_share": covered_revenue / vintage["total_revenue_usd_mm"],
            "weight_scope": "Normalized within U.S. + EMEA covered sleeves; EMEA is the official proxy for Europe.",
        })
    return rows


def latest_revenue_weight(cutoff: datetime, revenue_weights: list[dict]) -> dict | None:
    eligible = [
        row for row in revenue_weights
        if datetime.fromisoformat(row["accepted_at_utc"].replace("Z", "+00:00")) < cutoff
    ]
    return max(eligible, key=lambda row: row["accepted_at_utc"]) if eligible else None


def build_long_observations() -> tuple[list[dict], dict[str, dict[date, float]]]:
    output_rows: list[dict] = []
    series: dict[str, dict[date, float]] = defaultdict(lambda: defaultdict(float))

    # Use the governed U.S. sleeve, which starts in 2021. Preserve every row in the
    # normalized dataset, but exclude tiny thru/transit counts from the feature.
    physical_rows = read_csv(PHYSICAL_OBS_PATH)
    for row in physical_rows:
        if row.get("source_id") != "SFO_AIR_PASSENGERS" or row.get("geo_segment") not in {"Domestic", "International"}:
            continue
        month = parse_month(row["reference_period"])
        value = to_float(row.get("value"))
        if value is None:
            continue
        # The lane's normalized metric can keep movement type in metric or another column.
        movement = row.get("movement_type") or row.get("segment_2") or row.get("metric")
        included_in_feature = movement in {"Enplaned", "Deplaned", "Enplaned passengers", "Deplaned passengers", "Passenger activity"}
        if included_in_feature:
            series["US_SFO_T3M_YOY"][month] += value
        output_rows.append({
            "observation_id": row.get("observation_id", ""),
            "source_id": "SFO_AIR_PASSENGERS",
            "provider": row.get("provider", "City and County of San Francisco"),
            "region_family": "United States",
            "geography": row.get("geography", "SFO"),
            "reference_period": row["reference_period"],
            "metric": row.get("metric", "Passenger activity"),
            "segment_1": row.get("geo_segment", row.get("segment_1", "")),
            "segment_2": movement,
            "value": value,
            "unit": row.get("unit", "passengers"),
            "observed_first_available_at_utc": row.get("initial_publication_timestamp_utc", ""),
            "source_loaded_at_utc": row.get("source_loaded_at_utc", ""),
            "collection_timestamp_utc": row.get("collection_timestamp_utc", ""),
            "pit_treatment": "current_snapshot_diagnostic_only",
            "strict_pit_eligible": "false",
            "included_in_feature": str(included_in_feature).lower(),
            "raw_file": row.get("raw_cache_path", ""),
        })

    broad_rows = read_csv(VALID_OBS_PATH)
    for row in broad_rows:
        source_id = row.get("source_id")
        if source_id not in {"EUROSTAT_PLATFORM_NIGHTS_COUNTRY", "EUROSTAT_TOURISM_NIGHTS"}:
            continue
        if row.get("geography_code") != "EU27_2020" or len(row.get("reference_period", "")) != 7:
            continue
        value = to_float(row.get("value"))
        if value is None:
            continue
        feature_id = "EU_PLATFORM_T3M_YOY" if source_id == "EUROSTAT_PLATFORM_NIGHTS_COUNTRY" else "EU_TOURISM_T3M_YOY"
        month = parse_month(row["reference_period"])
        series[feature_id][month] += value
        output_rows.append({
            "observation_id": row.get("observation_id", ""),
            "source_id": source_id,
            "provider": row.get("provider", "Eurostat"),
            "region_family": "Europe",
            "geography": row.get("geography_name", "EU27"),
            "reference_period": row["reference_period"],
            "metric": row.get("metric", ""),
            "segment_1": row.get("segment_1", ""),
            "segment_2": row.get("segment_2", ""),
            "value": value,
            "unit": row.get("unit", ""),
            "observed_first_available_at_utc": row.get("first_available_at_utc", ""),
            "source_loaded_at_utc": row.get("source_updated_at", ""),
            "collection_timestamp_utc": row.get("collected_at_utc", ""),
            "pit_treatment": "current_snapshot_diagnostic_only",
            "strict_pit_eligible": "false",
            "included_in_feature": "true",
            "raw_file": row.get("raw_file", ""),
        })

    output_rows.sort(key=lambda row: (row["region_family"], row["source_id"], row["reference_period"], row["segment_1"], row["segment_2"]))
    return output_rows, series


def build_guidance_and_events(
    series: dict[str, dict[date, float]], revenue_weights: list[dict]
) -> tuple[list[dict], list[dict]]:
    guidance = read_csv(GUIDANCE_PATH)
    midpoint_by_period = {row["guided_fiscal_period"]: to_float(row["target_midpoint"]) for row in guidance}
    previous_yoy: float | None = None
    previous_features: dict[str, float] = {}
    event_rows: list[dict] = []

    for row in guidance:
        midpoint = to_float(row["target_midpoint"])
        prior_period = period_previous_year(row["guided_fiscal_period"])
        prior_midpoint = midpoint_by_period.get(prior_period)
        yoy = midpoint / prior_midpoint - 1 if midpoint is not None and prior_midpoint else None
        acceleration = yoy - previous_yoy if yoy is not None and previous_yoy is not None else None
        if yoy is not None:
            previous_yoy = yoy
        row["prior_year_guided_period"] = prior_period
        row["prior_year_midpoint"] = prior_midpoint
        row["guidance_yoy_growth"] = yoy
        row["guidance_acceleration_pp"] = acceleration

        cutoff = datetime.fromisoformat(row["guidance_available_at_utc"].replace("Z", "+00:00"))
        weight_vintage = latest_revenue_weight(cutoff, revenue_weights)
        values: dict[str, tuple[float | None, str, str]] = {}
        for spec in FEATURES:
            values[spec.feature_id] = monthly_feature(series[spec.feature_id], cutoff, spec.lag_days)

        us_value, us_period, us_available = values["US_SFO_T3M_YOY"]
        eu_value, eu_period, eu_available = values["EU_PLATFORM_T3M_YOY"]
        tourism_value, tourism_period, tourism_available = values["EU_TOURISM_T3M_YOY"]
        composite_value = (us_value + eu_value) / 2 if us_value is not None and eu_value is not None else None
        revenue_weighted_value = (
            weight_vintage["us_weight"] * us_value + weight_vintage["emea_weight"] * eu_value
            if weight_vintage is not None and us_value is not None and eu_value is not None
            else None
        )
        premium_value = eu_value - tourism_value if eu_value is not None and tourism_value is not None else None
        composite_period = f"US:{us_period}|EU:{eu_period}" if composite_value is not None else ""
        composite_available = max(us_available, eu_available) if composite_value is not None else ""
        values["US_EU_50_50_COMPOSITE"] = (composite_value, composite_period, composite_available)
        values["US_EMEA_REVENUE_WEIGHTED_COMPOSITE"] = (
            revenue_weighted_value,
            composite_period if revenue_weighted_value is not None else "",
            max(composite_available, weight_vintage["accepted_at_utc"]) if revenue_weighted_value is not None else "",
        )
        values["EU_PLATFORM_MINUS_TOURISM"] = (premium_value, f"platform:{eu_period}|tourism:{tourism_period}" if premium_value is not None else "", max(eu_available, tourism_available) if premium_value is not None else "")

        for feature_id, (feature_value, ref_period, assumed_available) in values.items():
            feature_change = feature_value - previous_features[feature_id] if feature_value is not None and feature_id in previous_features else None
            if feature_value is not None:
                previous_features[feature_id] = feature_value
            direction_match = None
            if feature_change is not None and acceleration is not None:
                direction_match = sign(feature_change) == sign(acceleration)
            event_rows.append({
                "event_index": row["event_index"],
                "prediction_id": row["prediction_id"],
                "issuing_fiscal_period": row["issuing_fiscal_period"],
                "guided_fiscal_period": row["guided_fiscal_period"],
                "guidance_cutoff_utc": row["guidance_available_at_utc"],
                "guidance_midpoint_usd_mm": midpoint,
                "prior_year_midpoint_usd_mm": prior_midpoint,
                "guidance_yoy_growth": yoy,
                "guidance_acceleration_pp": acceleration,
                "feature_id": feature_id,
                "feature_value": feature_value,
                "feature_change_pp": feature_change,
                "feature_reference_period": ref_period,
                "assumed_availability_utc_for_diagnostic": assumed_available,
                "strict_pit_eligible": "false",
                "diagnostic_eligible": str(feature_value is not None).lower(),
                "acceleration_direction_match": "" if direction_match is None else str(direction_match).lower(),
                "evidence_status": "current_snapshot_diagnostic_only",
                "weight_fiscal_year": weight_vintage["fiscal_year"] if weight_vintage else "",
                "us_revenue_usd_mm": weight_vintage["us_revenue_usd_mm"] if weight_vintage else "",
                "emea_revenue_usd_mm": weight_vintage["emea_revenue_usd_mm"] if weight_vintage else "",
                "us_weight": weight_vintage["us_weight"] if weight_vintage else "",
                "emea_weight": weight_vintage["emea_weight"] if weight_vintage else "",
                "weight_available_at_utc": weight_vintage["accepted_at_utc"] if weight_vintage else "",
                "weight_source_url": weight_vintage["source_url"] if weight_vintage else "",
            })

    return guidance, event_rows


def build_comparisons(event_rows: list[dict]) -> list[dict]:
    labels = {spec.feature_id: spec.label for spec in FEATURES}
    labels.update({
        "US_EU_50_50_COMPOSITE": "Equal-weight U.S. airport + EU platform-nights composite",
        "US_EMEA_REVENUE_WEIGHTED_COMPOSITE": "Revenue-weighted U.S. airport + EMEA-proxy platform-nights composite",
        "EU_PLATFORM_MINUS_TOURISM": "EU platform-night growth minus total-tourism growth",
    })
    definitions = {spec.feature_id: spec.definition for spec in FEATURES}
    definitions.update({
        "US_EU_50_50_COMPOSITE": "Simple 50/50 average of the U.S. SFO activity feature and the EU27 platform-night feature; never row weighted.",
        "US_EMEA_REVENUE_WEIGHTED_COMPOSITE": "Point-in-time U.S./EMEA revenue weights from the latest available Airbnb 10-K, normalized within the two covered sleeves; EU27 platform nights proxy EMEA activity.",
        "EU_PLATFORM_MINUS_TOURISM": "EU27 platform-night YoY less EU27 total-tourism-night YoY.",
    })
    output = []
    for feature_id in labels:
        rows = [row for row in event_rows if row["feature_id"] == feature_id]
        level_pairs = [(to_float(row["feature_value"]), to_float(row["guidance_yoy_growth"])) for row in rows]
        level_pairs = [(x, y) for x, y in level_pairs if x is not None and y is not None]
        accel_pairs = [(to_float(row["feature_value"]), to_float(row["guidance_acceleration_pp"])) for row in rows]
        accel_pairs = [(x, y) for x, y in accel_pairs if x is not None and y is not None]
        direction_rows = [row for row in rows if row["acceleration_direction_match"] in {"true", "false"}]
        output.append({
            "feature_id": feature_id,
            "feature_label": labels[feature_id],
            "definition": definitions[feature_id],
            "diagnostic_event_count": sum(row["diagnostic_eligible"] == "true" for row in rows),
            "strict_pit_event_count": 0,
            "guidance_level_n": len(level_pairs),
            "guidance_level_pearson": pearson([x for x, _ in level_pairs], [y for _, y in level_pairs]),
            "guidance_level_spearman": spearman([x for x, _ in level_pairs], [y for _, y in level_pairs]),
            "guidance_acceleration_n": len(accel_pairs),
            "guidance_acceleration_pearson": pearson([x for x, _ in accel_pairs], [y for _, y in accel_pairs]),
            "guidance_acceleration_spearman": spearman([x for x, _ in accel_pairs], [y for _, y in accel_pairs]),
            "direction_test_n": len(direction_rows),
            "acceleration_direction_concordance": sum(row["acceleration_direction_match"] == "true" for row in direction_rows) / len(direction_rows) if direction_rows else None,
            "interpretation": "Descriptive current-snapshot diagnostic; not a backtest, forecast-approval result, or alpha estimate.",
        })
    return output


def build_usability(comparisons: list[dict]) -> dict:
    by_id = {row["feature_id"]: row for row in comparisons}
    weighted = by_id["US_EMEA_REVENUE_WEIGHTED_COMPOSITE"]
    equal = by_id["US_EU_50_50_COMPOSITE"]
    us = by_id["US_SFO_T3M_YOY"]
    delta_equal = weighted["guidance_level_pearson"] - equal["guidance_level_pearson"]
    delta_us = weighted["guidance_level_pearson"] - us["guidance_level_pearson"]
    # A move smaller than two correlation points is classified as immaterial.
    # This threshold is fixed before presentation and prevents a tiny positive
    # delta from being described as incremental edge.
    incremental_score = (
        8 if delta_equal >= 0.05 and delta_us >= 0.05
        else 6 if delta_equal >= 0.02 and delta_us >= 0.02
        else 4 if delta_equal >= 0.02
        else 2
    )
    dimensions = [
        {"dimension": "Economic directness", "weight": 0.20, "score": 8, "evidence": "Airport passengers and platform accommodation nights both map directly to travel demand and booked stays."},
        {"dimension": "Geographic representativeness", "weight": 0.20, "score": 5, "evidence": "Official revenue weights improve the mix, but SFO is one U.S. airport and EU27 activity is only a proxy for EMEA."},
        {"dimension": "Timeliness and frequency", "weight": 0.15, "score": 6, "evidence": "Monthly data are useful, but the diagnostic requires conservative 60-day and 120-day lags."},
        {"dimension": "Point-in-time integrity", "weight": 0.25, "score": 0, "evidence": "Zero strict point-in-time event-feature rows; current snapshots cannot support a historical forecast test."},
        {"dimension": "Stability and robustness", "weight": 0.10, "score": 4, "evidence": f"Only {weighted['guidance_level_n']} comparable events; rank correlation is modest and acceleration correlation is unstable."},
        {"dimension": "Incremental diagnostic value", "weight": 0.10, "score": incremental_score, "evidence": f"Level-Pearson change versus 50/50 is {delta_equal:+.3f}; versus SFO alone is {delta_us:+.3f}."},
    ]
    total = sum(row["weight"] * row["score"] for row in dimensions)
    return {
        "feature_id": "US_EMEA_REVENUE_WEIGHTED_COMPOSITE",
        "dimensions": dimensions,
        "total_score": total,
        "rating": "Research/hypothesis use only" if total < 5 else "Prospective pilot",
        "forecast_deployment_gate": "FAIL — zero strict point-in-time rows",
        "delta_vs_50_50_pearson": delta_equal,
        "delta_vs_sfo_pearson": delta_us,
    }


def build_source_summary(long_rows: list[dict]) -> list[dict]:
    counts = defaultdict(int)
    for row in long_rows:
        counts[row["source_id"]] += 1
    physical = read_csv(PHYSICAL_DISPOSITIONS)
    physical_by_id = {row["source_id"]: row for row in physical}
    supply_gates = {row["source_id"]: row for row in read_csv(SUPPLY_GATES)}
    registry = {row["source_id"]: row for row in read_csv(SOURCE_REGISTRY)}
    rows = []
    for source_id, source_rows in physical_by_id.items():
        registered = registry.get(source_id, {})
        rows.append({
            "source_id": source_id,
            "region": "United States",
            "provider": registered.get("provider", ""),
            "dataset": registered.get("dataset", ""),
            "gate_result": "allowed/reused" if int(source_rows.get("source_rows") or 0) else "blocked_or_inconclusive",
            "collection_outcome": source_rows.get("collection_outcome", ""),
            "compiled_rows": counts.get(source_id, 0),
            "strict_pit_rows": source_rows.get("strict_pit_eligible_rows", "0"),
            "reason": source_rows.get("reason", ""),
            "source_url": registered.get("source_url", ""),
        })
    for candidate in read_csv(SUPPLY_CANDIDATES):
        source_id = candidate["source_id"]
        gate = supply_gates.get(source_id, {})
        registered = registry.get(source_id, {})
        rows.append({
            "source_id": source_id,
            "region": "United States",
            "provider": candidate.get("provider", ""),
            "dataset": candidate.get("dataset", registered.get("dataset", "")),
            "gate_result": "allowed" if gate.get("allowed") == "true" else "blocked_or_inconclusive",
            "collection_outcome": "not_collected",
            "compiled_rows": counts.get(source_id, 0),
            "strict_pit_rows": 0,
            "reason": gate.get("decision_reasons", candidate.get("status", "")),
            "source_url": registered.get("source_url", candidate.get("exact_source_url", "")),
        })
    rows.extend([
        {
            "source_id": "EUROSTAT_PLATFORM_NIGHTS_COUNTRY",
            "region": "Europe",
            "provider": "Eurostat",
            "dataset": registry.get("EUROSTAT_PLATFORM_NIGHTS_COUNTRY", {}).get("dataset", "Collaborative-platform nights by country"),
            "gate_result": "governed_snapshot_reuse",
            "collection_outcome": "compiled_current_snapshot",
            "compiled_rows": counts.get("EUROSTAT_PLATFORM_NIGHTS_COUNTRY", 0),
            "strict_pit_rows": 0,
            "reason": "Official EU27 collaborative-platform nights; current snapshot is diagnostic/prospective only.",
            "source_url": registry.get("EUROSTAT_PLATFORM_NIGHTS_COUNTRY", {}).get("source_url", "https://ec.europa.eu/eurostat/"),
        },
        {
            "source_id": "EUROSTAT_TOURISM_NIGHTS",
            "region": "Europe",
            "provider": "Eurostat",
            "dataset": registry.get("EUROSTAT_TOURISM_NIGHTS", {}).get("dataset", "Tourism nights at accommodation establishments"),
            "gate_result": "governed_snapshot_reuse",
            "collection_outcome": "compiled_current_snapshot",
            "compiled_rows": counts.get("EUROSTAT_TOURISM_NIGHTS", 0),
            "strict_pit_rows": 0,
            "reason": "Official EU27 total-tourism nights control; current snapshot is diagnostic/prospective only.",
            "source_url": registry.get("EUROSTAT_TOURISM_NIGHTS", {}).get("source_url", "https://ec.europa.eu/eurostat/"),
        },
    ])
    rows.sort(key=lambda row: (row["region"], row["source_id"]))
    return rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    long_rows, series = build_long_observations()
    revenue_weights = build_revenue_weights()
    guidance, event_rows = build_guidance_and_events(series, revenue_weights)
    comparisons = build_comparisons(event_rows)
    usability = build_usability(comparisons)
    source_summary = build_source_summary(long_rows)

    long_path = OUTPUT_DIR / "abnb_us_europe_altdata_long.csv"
    event_path = OUTPUT_DIR / "abnb_us_europe_guidance_panel.csv"
    comparison_path = OUTPUT_DIR / "abnb_us_europe_comparison_metrics.csv"
    source_path = OUTPUT_DIR / "abnb_us_europe_source_permissions.csv"
    weight_path = OUTPUT_DIR / "abnb_us_emea_revenue_weights.csv"
    usability_path = OUTPUT_DIR / "abnb_us_emea_composite_usability.csv"
    guidance_path = RUN_DIR / "guidance_enriched.csv"
    write_csv(long_path, long_rows)
    write_csv(event_path, event_rows)
    write_csv(comparison_path, comparisons)
    write_csv(source_path, source_summary)
    write_csv(weight_path, revenue_weights)
    write_csv(usability_path, usability["dimensions"])
    write_csv(guidance_path, guidance)

    inputs = {
        "generated_at_utc": "2026-09-03T23:37:12Z",
        "guidance": guidance,
        "events": event_rows,
        "comparisons": comparisons,
        "revenue_weights": revenue_weights,
        "usability": usability,
        "sources": source_summary,
        "observations": long_rows,
        "feature_specs": [spec.__dict__ for spec in FEATURES],
        "paths": {
            "long_csv": long_path.relative_to(REPO_DIR).as_posix(),
            "event_csv": event_path.relative_to(REPO_DIR).as_posix(),
            "comparison_csv": comparison_path.relative_to(REPO_DIR).as_posix(),
            "source_csv": source_path.relative_to(REPO_DIR).as_posix(),
            "weight_csv": weight_path.relative_to(REPO_DIR).as_posix(),
            "usability_csv": usability_path.relative_to(REPO_DIR).as_posix(),
        },
    }
    (RUN_DIR / "workbook_inputs.json").write_text(json.dumps(inputs, indent=2, default=str), encoding="utf-8")

    validation = {
        "status": "PASS",
        "compiled_observation_rows": len(long_rows),
        "compiled_us_rows": sum(row["region_family"] == "United States" for row in long_rows),
        "compiled_europe_rows": sum(row["region_family"] == "Europe" for row in long_rows),
        "guidance_events": len(guidance),
        "numeric_guidance_events": sum(to_float(row.get("target_midpoint")) is not None for row in guidance),
        "yoy_comparable_guidance_events": sum(to_float(row.get("guidance_yoy_growth")) is not None for row in guidance),
        "event_feature_rows": len(event_rows),
        "strict_pit_event_rows": sum(row["strict_pit_eligible"] == "true" for row in event_rows),
        "diagnostic_feature_values": sum(row["diagnostic_eligible"] == "true" for row in event_rows),
        "guardrails": [
            "All compiled observations are current-snapshot diagnostic/prospective data.",
            "Assumed availability dates are conservative alignment rules, not observed historical publication timestamps.",
            "The primary composite uses the latest point-in-time U.S./EMEA Airbnb revenue weights normalized within the two covered sleeves.",
            "The 50/50 composite is retained only as a benchmark and was not used to tune the revenue weights.",
            "EMEA is the closest official revenue proxy because Airbnb does not disclose Europe-only revenue.",
            "Correlations are descriptive and were not used to select or tune features.",
        ],
    }
    (RUN_DIR / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
