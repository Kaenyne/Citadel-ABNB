"""Build the frozen-H-004 WSF replay shell without accessing WSF or transcripts.

The only event inputs are the approved target panel and the two existing H-001
Phase-A replay tables.  WSF source fields remain missing because the collection
gate denied every request.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
READINESS = REPO / "research/readiness/20260903T053309Z_abnb_readiness"
TARGET_PANEL = READINESS / "target_panel.csv"
H001_REPLAYS = (
    READINESS / "cohort_2020q4_2023q2_replay.csv",
    READINESS / "cohort_2023q3_2026q2_replay.csv",
)
OUTPUT = HERE / "wsf_h004_event_replay.csv"

HYPOTHESIS_ID = "H-004"
SOURCE_ID = "WSF_FERRY_RIDERSHIP"
EXPECTED_DIRECTION = "positive"
PRIMARY_FORMULA = (
    "From the latest dated WSF report proven published strictly before cutoff, "
    "subtract the fixed commuter-control-route year-over-year percentage change "
    "in foot passengers from the fixed leisure-route year-over-year percentage "
    "change in foot passengers. Fixed leisure routes: Anacortes/San Juan and "
    "Fauntleroy/Vashon/Southworth. Fixed commuter controls: Seattle/Bainbridge "
    "and Seattle/Bremerton."
)
SENSITIVITY_FORMULA = (
    "Use total riders instead of foot passengers with identical fixed route sets."
)
AVAILABILITY_RULE = (
    "Use the target-panel guidance_available_at_utc as cutoff; include only a dated "
    "WSF report with exact initial publication timestamp strictly before cutoff. "
    "Equality and later releases are excluded."
)
EXCLUSION_REASON = (
    "WSF permission gate denied collection; no lawful source request or WSF data "
    "exists in this run; exact historical publication timing and route-vintage "
    "values are unavailable."
)
MISSINGNESS = (
    "wsf_report_reference_period;wsf_initial_publication_utc;"
    "wsf_route_values;wsf_primary_feature_value;wsf_sensitivity_feature_value"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def prior_year_period(period: str) -> str:
    return f"{int(period[:4]) - 1}{period[4:]}"


def prior_quarter_period(period: str) -> str:
    year = int(period[:4])
    quarter = int(period[-1])
    return f"{year - 1}Q4" if quarter == 1 else f"{year}Q{quarter - 1}"


def comparable(target: dict[str, str], baseline: dict[str, str] | None) -> bool:
    if baseline is None:
        return False
    if target["target_type"] != "numeric_range" or baseline["target_type"] != "numeric_range":
        return False
    if not target["target_midpoint"] or not baseline["target_midpoint"]:
        return False
    return all(
        target[field] == baseline[field]
        for field in ("target_unit", "currency", "constant_currency_basis")
    )


def baseline_fields(
    target: dict[str, str], baseline: dict[str, str] | None
) -> tuple[str, str, str, str, str, str]:
    if not comparable(target, baseline):
        if target["target_type"] != "numeric_range" or not target["target_midpoint"]:
            reason = "target midpoint is missing because guidance is qualitative"
        elif baseline is None:
            reason = "named prior-period target is absent from the approved panel"
        else:
            reason = "named prior-period target is nonnumeric or noncomparable"
        return "false", "missing", "", "", "", reason
    assert baseline is not None
    change = Decimal(target["target_midpoint"]) - Decimal(baseline["target_midpoint"])
    direction = "up" if change > 0 else "down" if change < 0 else "neutral"
    return (
        "true",
        "available",
        baseline["prediction_id"],
        baseline["target_midpoint"],
        format(change, "f"),
        direction,
    )


def main() -> None:
    targets = read_rows(TARGET_PANEL)
    assert len(targets) == 23
    assert len({row["prediction_id"] for row in targets}) == 23

    by_guided = {row["guided_fiscal_period"]: row for row in targets}
    by_issuing = {row["issuing_fiscal_period"]: row for row in targets}

    h001: dict[str, dict[str, str]] = {}
    for replay_path in H001_REPLAYS:
        for row in read_rows(replay_path):
            if row["signal_id"] != "H-001":
                continue
            assert row["prediction_id"] not in h001
            h001[row["prediction_id"]] = row
    assert set(h001) == {row["prediction_id"] for row in targets}

    completed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    output_rows: list[dict[str, str]] = []
    for target in targets:
        seasonal = baseline_fields(
            target, by_guided.get(prior_year_period(target["guided_fiscal_period"]))
        )
        prior = baseline_fields(
            target, by_issuing.get(prior_quarter_period(target["issuing_fiscal_period"]))
        )
        control = h001[target["prediction_id"]]
        control_classification = control.get("replay_classification") or control.get("classification", "")
        control_comparable = (
            control.get("eligible") == "true"
            and control_classification in {"hit", "miss", "neutral"}
            and bool(control.get("baseline_value"))
        )

        output_rows.append(
            {
                "prediction_id": target["prediction_id"],
                "cohort": target["cohort"],
                "issuing_fiscal_period": target["issuing_fiscal_period"],
                "guided_fiscal_period": target["guided_fiscal_period"],
                "cutoff_utc": target["guidance_available_at_utc"],
                "target_type": target["target_type"],
                "target_low": target["target_low"],
                "target_high": target["target_high"],
                "target_midpoint": target["target_midpoint"],
                "target_unit": target["target_unit"],
                "currency": target["currency"],
                "constant_currency_basis": target["constant_currency_basis"],
                "target_source_id": target["target_source_id"],
                "target_citation": target["target_citation"],
                "hypothesis_id": HYPOTHESIS_ID,
                "source_id": SOURCE_ID,
                "frozen_primary_formula": PRIMARY_FORMULA,
                "frozen_sensitivity_formula": SENSITIVITY_FORMULA,
                "expected_direction": EXPECTED_DIRECTION,
                "availability_rule": AVAILABILITY_RULE,
                "wsf_report_reference_period": "",
                "wsf_initial_publication_utc": "",
                "wsf_primary_feature_value": "",
                "wsf_sensitivity_feature_value": "",
                "signal_unit": "percentage_points",
                "source_eligible": "false",
                "replay_status": "not_testable",
                "missingness": MISSINGNESS,
                "exclusion_reason": EXCLUSION_REASON,
                "seasonal_baseline_comparable": seasonal[0],
                "seasonal_baseline_status": seasonal[1],
                "seasonal_baseline_source_prediction_id": seasonal[2],
                "seasonal_baseline_value": seasonal[3],
                "target_change_vs_seasonal": seasonal[4],
                "actual_direction_vs_seasonal": seasonal[5] if seasonal[1] == "available" else "",
                "wsf_classification_vs_seasonal": "not_testable" if seasonal[0] == "true" else "missing",
                "seasonal_missing_reason": "" if seasonal[1] == "available" else seasonal[5],
                "prior_quarter_baseline_comparable": prior[0],
                "prior_quarter_baseline_status": prior[1],
                "prior_quarter_baseline_source_prediction_id": prior[2],
                "prior_quarter_baseline_value": prior[3],
                "target_change_vs_prior_quarter": prior[4],
                "actual_direction_vs_prior_quarter": prior[5] if prior[1] == "available" else "",
                "wsf_classification_vs_prior_quarter": "not_testable" if prior[0] == "true" else "missing",
                "prior_quarter_missing_reason": "" if prior[1] == "available" else prior[5],
                "wsf_signal_implication": "not_testable",
                "h001_comparable": str(control_comparable).lower(),
                "h001_signal_implication": control.get("signal_implication", "") if control_comparable else "",
                "h001_classification": control_classification if control_comparable else "",
                "h001_baseline_value": control.get("baseline_value", "") if control_comparable else "",
                "h001_target_change_vs_baseline": control.get("target_change_vs_baseline", "") if control_comparable else "",
                "h001_join_status": "joined" if control_comparable else "not_comparable",
                "leakage_warning": (
                    "Do not backfill WSF observations from current reports or infer publication timing; "
                    "target values and H-001 classifications are audit context, never WSF features."
                ),
                "completed_at_utc": completed_at,
            }
        )

    fieldnames = list(output_rows[0])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    assert len(output_rows) == 23
    assert all(row["source_id"] == SOURCE_ID for row in output_rows)
    assert all(row["hypothesis_id"] == HYPOTHESIS_ID for row in output_rows)
    assert all(row["source_eligible"] == "false" for row in output_rows)
    assert all(row["replay_status"] == "not_testable" for row in output_rows)
    assert all(not row["wsf_primary_feature_value"] for row in output_rows)
    assert sum(row["seasonal_baseline_comparable"] == "true" for row in output_rows) == 16
    assert sum(row["prior_quarter_baseline_comparable"] == "true" for row in output_rows) == 19
    assert sum(row["h001_comparable"] == "true" for row in output_rows) == 16
    assert sum(row["h001_classification"] == "hit" for row in output_rows) == 9
    assert sum(row["h001_classification"] == "miss" for row in output_rows) == 7

    print(f"wrote {len(output_rows)} rows to {OUTPUT}")
    print(f"columns={len(fieldnames)}")
    print("seasonal_comparable=16 prior_quarter_comparable=19 h001_comparable=16")
    print("wsf_eligible=0 wsf_not_testable=23 h001_hits=9 h001_misses=7")


if __name__ == "__main__":
    main()
