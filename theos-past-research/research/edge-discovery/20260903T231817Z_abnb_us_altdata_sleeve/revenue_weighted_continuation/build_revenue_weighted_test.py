"""Build H-012 v2 using disclosure-derived fixed revenue weights.

No source weight is fitted to guidance outcomes. The script consumes the already
governed diagnostic event panel and preserves H-012 v1 separately.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


HERE = Path(__file__).resolve().parent
RUN_ROOT = HERE.parent
REPO = HERE.parents[3]
SEC_URL = "https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm"
SEC_ACCESSION = "0001559720-26-000004"
SEC_ACCEPTED = "2026-02-12T21:04:39Z"
SEC_SHA256 = "61bac47250511a2263631ebd99e92b1d42caf305d27ba9d9fbfa7b11aa199c02"
SEC_BYTES = 2_131_290
US_WEIGHT = 4814 / (4814 + 4729)
EMEA_WEIGHT = 4729 / (4814 + 4729)
BUILT_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt(value: float | None) -> str:
    return "" if value is None or not math.isfinite(value) else f"{value:.10f}".rstrip("0").rstrip(".")


def parse(value: str) -> float | None:
    return None if value == "" else float(value)


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def direction(value: float | None) -> str:
    if value is None:
        return ""
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    dx, dy = [x - mx for x in xs], [y - my for y in ys]
    denominator = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return None if denominator == 0 else sum(x * y for x, y in zip(dx, dy)) / denominator


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranked = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        rank = (cursor + 1 + end) / 2
        for position in range(cursor, end):
            ranked[order[position]] = rank
        cursor = end
    return ranked


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(ranks(xs), ranks(ys)) if len(xs) >= 2 else None


evidence = []
for year, us_revenue, emea_revenue, total_revenue in [
    (2023, 4290, 3615, 9917),
    (2024, 4640, 4135, 11102),
    (2025, 4814, 4729, 12241),
]:
    covered = us_revenue + emea_revenue
    evidence.append({
        "fiscal_year": year, "us_revenue_usd_millions": us_revenue,
        "emea_revenue_usd_millions": emea_revenue, "total_revenue_usd_millions": total_revenue,
        "us_weight_within_two_sleeves": fmt(us_revenue / covered),
        "emea_weight_within_two_sleeves": fmt(emea_revenue / covered),
        "two_sleeve_share_of_total_revenue": fmt(covered / total_revenue),
        "us_share_of_total_revenue": fmt(us_revenue / total_revenue),
        "emea_share_of_total_revenue": fmt(emea_revenue / total_revenue),
        "recommended_weight_year": str(year == 2025).lower(),
        "attribution_basis": "listing location",
        "source_accession": SEC_ACCESSION, "source_accepted_at_utc": SEC_ACCEPTED,
        "source_url": SEC_URL, "source_bytes": SEC_BYTES, "source_sha256": SEC_SHA256,
        "vintage_caveat": "Values are evidenced from the 2025 Form 10-K accepted in 2026; do not use this filing as pre-cutoff evidence for earlier events.",
    })
evidence_fields = ["fiscal_year", "us_revenue_usd_millions", "emea_revenue_usd_millions",
                   "total_revenue_usd_millions", "us_weight_within_two_sleeves",
                   "emea_weight_within_two_sleeves", "two_sleeve_share_of_total_revenue",
                   "us_share_of_total_revenue", "emea_share_of_total_revenue", "recommended_weight_year",
                   "attribution_basis", "source_accession", "source_accepted_at_utc", "source_url",
                   "source_bytes", "source_sha256", "vintage_caveat"]
write_csv(HERE / "weight_source_evidence.csv", evidence_fields, evidence)


score_rows = [
    ("official_authority_and_auditability", 15, 5, "Audited Form 10-K; tagged XBRL and exact SEC accession."),
    ("target_definition_match", 15, 5, "Both inputs are revenue attributed by host listing location."),
    ("us_geographic_match", 15, 5, "Exact United States revenue is disclosed."),
    ("europe_proxy_match", 15, 3, "EMEA is the closest disclosed regional proxy but is broader than EU27/Europe."),
    ("two_sleeve_coverage", 10, 4, "U.S. plus EMEA represent 77.96% of 2025 global revenue; other regions are excluded."),
    ("temporal_stability", 10, 3, "Normalized U.S. weight fell from 54.27% in 2023 to 50.45% in 2025."),
    ("frequency_and_recency", 10, 2, "Annual disclosure cannot capture quarterly mix shifts."),
    ("historical_point_in_time_usability", 10, 1, "2025 filing was accepted in February 2026 and is ex-post for earlier guidance events."),
]
usability = [{
    "dimension": dimension, "weight_pct": weight, "score_0_to_5": score,
    "weighted_points": fmt(weight * score / 5), "rationale": rationale,
} for dimension, weight, score, rationale in score_rows]
write_csv(HERE / "usability_scoring.csv",
          ["dimension", "weight_pct", "score_0_to_5", "weighted_points", "rationale"], usability)


base = read_csv(RUN_ROOT / "event_aligned_features.csv")
by_prediction: dict[str, dict[str, dict[str, str]]] = {}
for row in base:
    by_prediction.setdefault(row["prediction_id"], {})[row["feature_id"]] = row

weighted_rows = []
for prediction_id, features in by_prediction.items():
    us = features["US_ACTIVITY_AVAILABLE_PROVIDER"]
    eu = features["EU27_PLATFORM_NIGHTS_CONTROL"]
    old = features["US_EU_EQUAL_50_50_COMPOSITE"]
    us_value, eu_value = parse(us["feature_value"]), parse(eu["feature_value"])
    weighted_value = None if us_value is None or eu_value is None else US_WEIGHT * us_value + EMEA_WEIGHT * eu_value
    old_value = parse(old["feature_value"])
    weight_available = parse_utc(SEC_ACCEPTED) < parse_utc(us["guidance_cutoff_at_utc"])
    weighted_rows.append({
        "prediction_id": prediction_id, "guidance_cutoff_at_utc": us["guidance_cutoff_at_utc"],
        "guided_fiscal_period": us["guided_fiscal_period"], "hypothesis_id": "H-012",
        "hypothesis_version": 2, "us_feature_id": us["feature_id"], "us_feature_value": us["feature_value"],
        "europe_feature_id": eu["feature_id"], "europe_feature_value": eu["feature_value"],
        "us_revenue_weight": fmt(US_WEIGHT), "europe_proxy_revenue_weight": fmt(EMEA_WEIGHT),
        "revenue_weight_year": 2025, "weight_source_available_before_cutoff": str(weight_available).lower(),
        "weighted_composite_value": fmt(weighted_value), "prior_v1_equal_weight_value": old["feature_value"],
        "replacement_delta": fmt(None if weighted_value is None or old_value is None else weighted_value - old_value),
        "feature_transform": "0.5044535261 * U.S. activity growth + 0.4955464739 * EU27 platform-night growth",
        "strict_eligibility": "false", "pit_treatment": "current_snapshot_diagnostic",
        "exclusion_reason": (
            "Underlying SFO and Eurostat inputs lack original historical vintages. "
            + ("Weight disclosure is also after this event cutoff." if not weight_available else "Weight is public before cutoff, but signal-vintage failure remains.")
        ),
        "guidance_midpoint": us["guidance_midpoint"],
        "prior_year_comparable_midpoint": us["prior_year_comparable_midpoint"],
        "guidance_yoy_pct": us["guidance_yoy_pct"],
        "guidance_yoy_acceleration_pp": us["guidance_yoy_acceleration_pp"],
        "feature_direction": direction(weighted_value), "strict_evaluation_status": "not_testable",
    })

weighted_fields = ["prediction_id", "guidance_cutoff_at_utc", "guided_fiscal_period", "hypothesis_id",
                   "hypothesis_version", "us_feature_id", "us_feature_value", "europe_feature_id",
                   "europe_feature_value", "us_revenue_weight", "europe_proxy_revenue_weight",
                   "revenue_weight_year", "weight_source_available_before_cutoff", "weighted_composite_value",
                   "prior_v1_equal_weight_value", "replacement_delta", "feature_transform", "strict_eligibility",
                   "pit_treatment", "exclusion_reason", "guidance_midpoint", "prior_year_comparable_midpoint",
                   "guidance_yoy_pct", "guidance_yoy_acceleration_pp", "feature_direction",
                   "strict_evaluation_status"]
write_csv(HERE / "event_weighted_features.csv", weighted_fields, weighted_rows)


level_pairs = [(float(r["weighted_composite_value"]), float(r["guidance_yoy_pct"])) for r in weighted_rows
               if r["weighted_composite_value"] and r["guidance_yoy_pct"]]
acceleration_pairs = [(float(r["weighted_composite_value"]), float(r["guidance_yoy_acceleration_pp"])) for r in weighted_rows
                      if r["weighted_composite_value"] and r["guidance_yoy_acceleration_pp"]]
xs, ys = [x for x, _ in level_pairs], [y for _, y in level_pairs]
concordance = sum(direction(x) == direction(y) for x, y in acceleration_pairs) / len(acceleration_pairs)
comparison = [{
    "hypothesis_id": "H-012", "hypothesis_version": 2, "feature_id": "US_EU_REVENUE_WEIGHTED_COMPOSITE",
    "strict_pit_n": 0, "strict_pearson": "", "strict_spearman": "",
    "strict_acceleration_direction_concordance": "", "diagnostic_level_n": len(level_pairs),
    "diagnostic_pearson_guidance_yoy": fmt(pearson(xs, ys)),
    "diagnostic_spearman_guidance_yoy": fmt(spearman(xs, ys)),
    "diagnostic_acceleration_n": len(acceleration_pairs),
    "diagnostic_acceleration_direction_concordance": fmt(concordance),
    "decision": "WATCH_PROSPECTIVELY", "inference_status": "descriptive_current_snapshot_only",
    "notes": "Disclosure-derived fixed weights; no weight fitting or outcome optimization. Underlying signals remain non-PIT.",
}]
write_csv(HERE / "descriptive_comparison.csv",
          ["hypothesis_id", "hypothesis_version", "feature_id", "strict_pit_n", "strict_pearson",
           "strict_spearman", "strict_acceleration_direction_concordance", "diagnostic_level_n",
           "diagnostic_pearson_guidance_yoy", "diagnostic_spearman_guidance_yoy",
           "diagnostic_acceleration_n", "diagnostic_acceleration_direction_concordance", "decision",
           "inference_status", "notes"], comparison)


validation = {
    "status": "PASS", "built_at_utc": BUILT_AT, "hypothesis_id": "H-012", "hypothesis_version": 2,
    "recommended_us_weight": US_WEIGHT, "recommended_europe_proxy_weight": EMEA_WEIGHT,
    "weights_sum_to_one": abs(US_WEIGHT + EMEA_WEIGHT - 1) < 1e-12,
    "weight_source_accepted_at_utc": SEC_ACCEPTED,
    "event_rows": len(weighted_rows), "strict_pit_rows": sum(r["strict_eligibility"] == "true" for r in weighted_rows),
    "weight_public_before_cutoff_rows": sum(r["weight_source_available_before_cutoff"] == "true" for r in weighted_rows),
    "diagnostic_level_n": len(level_pairs), "diagnostic_acceleration_n": len(acceleration_pairs),
    "historical_usability_score_100": sum(float(r["weighted_points"]) for r in usability),
    "checks": {
        "event_count_23": len(weighted_rows) == 23,
        "strict_pit_zero": all(r["strict_eligibility"] == "false" for r in weighted_rows),
        "fixed_weights_each_row": all(r["us_revenue_weight"] == fmt(US_WEIGHT) and r["europe_proxy_revenue_weight"] == fmt(EMEA_WEIGHT) for r in weighted_rows),
        "prior_v1_preserved": (RUN_ROOT / "event_aligned_features.csv").exists(),
        "sec_arithmetic_reproduced": abs(US_WEIGHT - 0.5044535261448182) < 1e-12,
    },
    "limitations": [
        "EMEA is broader than Europe and EU27; it is the closest official Airbnb revenue proxy.",
        "The 2025 weight is ex-post for all cutoffs before 2026-02-12T21:04:39Z.",
        "Underlying SFO and Eurostat observations are current snapshots, so every composite row remains strict-PIT ineligible.",
        "The two sleeves cover 77.96% of 2025 global revenue and omit Latin America and Asia Pacific.",
    ],
}
assert all(validation["checks"].values())
(HERE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")


artifact_names = ["weight_source_evidence.csv", "usability_scoring.csv", "event_weighted_features.csv",
                  "descriptive_comparison.csv", "validation.json", "recommendation.md",
                  "build_revenue_weighted_test.py"]
manifest = []
for name in artifact_names:
    path = HERE / name
    manifest.append({"artifact": name, "bytes": path.stat().st_size, "sha256": sha256(path),
                     "generated_at_utc": BUILT_AT})
write_csv(HERE / "artifact_manifest.csv", ["artifact", "bytes", "sha256", "generated_at_utc"], manifest)
artifact_names.append("artifact_manifest.csv")
with (HERE / "checksums.sha256").open("w", encoding="utf-8") as handle:
    for name in artifact_names:
        handle.write(f"{sha256(HERE / name)}  {name}\n")

