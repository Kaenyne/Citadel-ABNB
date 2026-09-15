"""Strict application of an explicitly supplied L3 bundle; no RNPL estimation."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from adapter import dated, number, quarter, shift


def timing_identity(cohorts, target, as_of):
    """Generic unit-testable algebra on L3-supplied reference-currency exposures.

    This is an acceptance identity, not an independent empirical FX engine.
    Currency ratios must all be USD per foreign unit divided by same-currency
    reference rates. Rates are never averaged across unrelated currency levels.
    """
    quarter(target)
    if not cohorts:
        raise ValueError("Cohort mapping unavailable")
    result, keys = [], set()
    for c in cohorts:
        b = quarter(c["booking_quarter"])
        if b not in {shift(target, -1), shift(target, -2)}:
            raise ValueError("Cohort must be one of the two fixed kernel lags")
        key = (b, c["currency"])
        if key in keys:
            raise ValueError("Duplicate booking/currency cohort")
        keys.add(key)
        if not c.get("source_ref") or not c.get("evidence_status") or not c.get("reference_basis"):
            raise ValueError("Missing cohort provenance/reference basis")
        dated(c["information_date"], as_of)
        if c["rate_direction"] != "USD_per_currency":
            raise ValueError("Rates must be USD per currency")
        u = number(c["rnpl_share"], "rnpl_share")
        if not 0 <= u <= 1:
            raise ValueError("RNPL share must be on this revenue-producing cohort, in [0,1]")
        if c["share_denominator"] != "surviving_recognized_revenue_reference_exposure":
            raise ValueError("Stock and booking-flow shares are not cohort revenue weights")
        g = number(c["reference_gbv_musd"], "reference_gbv_musd", True)
        k = 2 / 3 if b == shift(target, -1) else 1 / 3
        booking = number(c["booking_fx_ratio"], "booking_fx_ratio", True)
        allocation = c["rnpl_allocation"]
        if not allocation:
            raise ValueError("Missing recognition allocation, even when RNPL share is zero")
        p_total, allocated, seen_periods = 0.0, 0.0, set()
        for a in allocation:
            rq = quarter(a["recognition_quarter"])
            if rq in seen_periods or rq != target:
                raise ValueError("This quarterly recognition hypothesis assigns target revenue only to target recognition quarter; other rate-fixing dates need a separately named contract")
            seen_periods.add(rq)
            dated(a["information_date"], as_of)
            p = number(a["weight"], "recognition weight")
            if not 0 <= p <= 1:
                raise ValueError("Recognition weight outside [0,1]")
            p_total += p
            allocated += p * number(a["fx_ratio"], "recognition_fx_ratio", True)
        if not math.isclose(p_total, 1, abs_tol=1e-10, rel_tol=0):
            raise ValueError("RNPL allocation must conserve exposure")
        result.append(dict(booking_quarter=b, currency=c["currency"],
                           weighted_reference_gbv_musd=k * g, booking_factor=booking,
                           retimed_factor=(1 - u) * booking + u * allocated))
    if {r["booking_quarter"] for r in result} != {shift(target, -1), shift(target, -2)}:
        raise ValueError("Both lag cohorts must be supplied")
    if len({c["reference_basis"] for c in cohorts}) != 1:
        raise ValueError("Reference bases do not match")
    denominator = sum(r["weighted_reference_gbv_musd"] for r in result)
    for r in result:
        r["reference_contribution_weight"] = r["weighted_reference_gbv_musd"] / denominator
    ordinary = sum(r["reference_contribution_weight"] * r["booking_factor"] for r in result)
    retimed = sum(r["reference_contribution_weight"] * r["retimed_factor"] for r in result)
    return dict(ordinary_booking_factor=ordinary, rnpl_retimed_factor=retimed,
                incremental_timing_multiplier=retimed / ordinary, cohort_rows=result)


def load_bundle(manifest_path, as_of):
    """Manifest references local JSON adapter rows by immutable SHA-256."""
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ["bundle_version", "commit", "information_date", "files"]:
        if not manifest.get(key):
            raise ValueError(f"Missing bundle {key}")
    if len(manifest["commit"]) != 40 or any(c not in "0123456789abcdef" for c in manifest["commit"]):
        raise ValueError("Bundle requires an explicit 40-character commit")
    dated(manifest["information_date"], as_of)
    rows = []
    for entry in manifest["files"]:
        path = (manifest_path.parent / entry["path"]).resolve()
        if not path.is_relative_to(manifest_path.parent):
            raise ValueError("Bundle path escapes manifest directory")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("L3 input hash mismatch")
        if entry["role"] == "revenue_adapter":
            rows.extend(json.loads(path.read_text(encoding="utf-8")))
    if not rows:
        raise ValueError("No revenue_adapter rows supplied")
    return manifest, rows


def apply_row(baseline, row, as_of):
    required = ["quarter", "metric", "scenario", "value", "lower", "upper", "units",
                "information_date", "evidence_status", "source_ref", "treatment",
                "baseline_scenario", "baseline_revenue_musd", "reference_basis",
                "embedded_fx", "hedge_treatment", "baseline_hedge_musd", "hedge_source_ref", "hedge_evidence_status", "cohorts"]
    if any(key not in row for key in required):
        raise ValueError("Incomplete L3 adapter contract")
    if any(not row[k] for k in ["scenario", "evidence_status", "source_ref", "reference_basis"]):
        raise ValueError("Missing L3 provenance")
    dated(row["information_date"], as_of)
    if row["quarter"] != baseline["quarter"] or row["baseline_scenario"] != baseline["scenario"]:
        raise ValueError("L3 baseline scenario/quarter mismatch")
    if baseline.get("fx_integration_status") != "pending_explicit_L3_bundle":
        raise ValueError("FX adjustment already applied")
    if row["metric"] != "revenue_timing_multiplier" or row["units"] != "ratio":
        raise ValueError("Only ratio-valued timing multipliers may be applied")
    if row["treatment"] != "incremental_replacement_of_embedded_booking_fx":
        raise ValueError("Full FX overlay on USD kernel is forbidden")
    if row["embedded_fx"] != "booking_fx_already_in_USD_GBV":
        raise ValueError("Embedded FX has not been reconciled")
    if row["hedge_treatment"] != "reconciled_baseline_hedges_held_unchanged":
        raise ValueError("Hedge bridge must be reconciled before adding hedge dollars")
    hedge = number(row["baseline_hedge_musd"], "baseline_hedge_musd")
    if not row["hedge_source_ref"] or row["hedge_evidence_status"] != "verified_baseline_reconciliation":
        raise ValueError("Missing verified baseline hedge reconciliation")
    pre_hedge = baseline["revenue_musd"] - hedge
    if pre_hedge <= 0:
        raise ValueError("Baseline pre-hedge revenue must be positive")
    if not math.isclose(number(row["baseline_revenue_musd"], "baseline revenue", True), baseline["revenue_musd"], abs_tol=1e-6, rel_tol=0):
        raise ValueError("L3 baseline revenue does not match")
    multiplier = number(row["value"], "multiplier", True)
    for key in ["lower", "upper"]:
        if row[key] is not None:
            bound = number(row[key], key, True)
            if (key == "lower" and bound > multiplier) or (key == "upper" and bound < multiplier):
                raise ValueError("Bounds exclude point")
    identity = timing_identity(row["cohorts"], row["quarter"], as_of)
    if any(c["reference_basis"] != row["reference_basis"] for c in row["cohorts"]):
        raise ValueError("Adapter and cohort reference bases differ")
    if not math.isclose(multiplier, identity["incremental_timing_multiplier"], abs_tol=1e-10, rel_tol=0):
        raise ValueError("L3 multiplier fails supplied cohort identity")
    # Prove reference-currency exposures reconstruct BOTH booking-USD kernel lags.
    for b in {c["booking_quarter"] for c in row["cohorts"]}:
        reconstructed = sum(float(c["reference_gbv_musd"]) * float(c["booking_fx_ratio"]) for c in row["cohorts"] if c["booking_quarter"] == b)
        expected = baseline["cohort_gbv_musd"][b]
        if not math.isclose(reconstructed, expected, abs_tol=1e-6, rel_tol=0):
            raise ValueError("Constant-reference exposure does not reconstruct USD GBV")
    result = dict(baseline)
    adjusted = pre_hedge * multiplier + hedge
    result.update(scenario=row["scenario"], revenue_musd=adjusted,
                  guide_musd=adjusted / (1 + baseline["cushion_decimal"]),
                  incremental_fx_musd=adjusted - baseline["revenue_musd"],
                  information_date=max(baseline.get("information_date", "1900-01-01"), row["information_date"]),
                  fx_integration_status="L3_applied_once_" + row["evidence_status"],
                  l3_source_ref=row["source_ref"], l3_reference_basis=row["reference_basis"],
                  l3_timing_multiplier=multiplier, baseline_hedge_musd=hedge,
                  l3_hedge_source_ref=row["hedge_source_ref"], hedge_treatment=row["hedge_treatment"])
    return result
