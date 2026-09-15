"""Arithmetic/contract tests, including independently hand-computed examples."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapter import dated, forecast, shift
from l3_contract import apply_row, load_bundle, timing_identity

ASOF = "2026-09-13"
LAM = dict(lambda_pct=12, variant="test_fixture", n_train=3,
           training_quarters=["2023Q4", "2024Q4", "2025Q4"], knowable_from="2026-02-12")


def gbv(q, value, **extra):
    return dict(quarter=q, gbv_musd=value, kind="forecast", information_date="2026-09-11", source_ref="synthetic_test_only", **extra)


def cohorts():
    return [dict(booking_quarter=b, currency="EUR", reference_gbv_musd=g,
                 rnpl_share=.25, booking_fx_ratio=1.1, rate_direction="USD_per_currency",
                 share_denominator="surviving_recognized_revenue_reference_exposure",
                 information_date="2026-09-11", source_ref="synthetic_test_only", evidence_status="assumption",
                 reference_basis="fixed_test_reference",
                 rnpl_allocation=[dict(recognition_quarter="2026Q4", weight=1, fx_ratio=1.2, information_date="2026-09-11")])
            for b, g in [("2026Q3", 300), ("2026Q2", 600)]]


def bundle_row(hedge=10):
    baseline = dict(scenario="test_baseline", quarter="2026Q4", revenue_musd=100,
                    cushion_decimal=.04, fx_integration_status="pending_explicit_L3_bundle",
                    cohort_gbv_musd={"2026Q3": 330, "2026Q2": 660})
    row = dict(quarter="2026Q4", metric="revenue_timing_multiplier", scenario="test_retimed", value=1.125/1.1,
               lower=None, upper=None, units="ratio", information_date="2026-09-11", evidence_status="conditional_test_only",
               source_ref="synthetic_test_only", treatment="incremental_replacement_of_embedded_booking_fx",
               baseline_scenario="test_baseline", baseline_revenue_musd=100, reference_basis="fixed_test_reference",
               embedded_fx="booking_fx_already_in_USD_GBV", hedge_treatment="reconciled_baseline_hedges_held_unchanged",
               baseline_hedge_musd=hedge, hedge_source_ref="synthetic_test_only",
               multiplier_accounting_basis="certified_matching_pre_hedge_revenue", scenario_hedge_musd=hedge,
               scenario_hedge_source_ref="synthetic_test_only", scenario_hedge_evidence_status="explicit_unchanged_hedge_assumption",
               hedge_evidence_status="verified_baseline_reconciliation", cohorts=cohorts())
    return baseline, row


def test_independent_kernel_units_and_actual_contribution_weights():
    row, parts = forecast("2026Q4", ASOF, [gbv("2026Q3", 300), gbv("2026Q2", 600)], .04, LAM)
    assert row["revenue_musd"] == pytest.approx(48)
    assert row["guide_musd"] == pytest.approx(48/1.04)
    assert [p["usd_baseline_contribution_weight"] for p in parts] == pytest.approx([.5, .5])
    assert sum(p["revenue_contribution_musd"] for p in parts) == pytest.approx(48)


def test_quarter_rollover():
    assert shift("2027Q1", -1) == "2026Q4"


def test_q3_contemporaneous_and_q4_timing():
    inputs = [gbv("2026Q1", 100), gbv("2026Q2", 200), gbv("2026Q3", 300), gbv("2026Q4", 400)]
    original = {q: forecast(q, ASOF, inputs, .04, LAM)[0]["revenue_musd"] for q in ["2026Q3", "2026Q4", "2027Q1"]}
    changed = copy.deepcopy(inputs)
    changed[2]["gbv_musd"] += 30
    moved = {q: forecast(q, ASOF, changed, .04, LAM)[0]["revenue_musd"] for q in original}
    assert moved["2026Q3"] == original["2026Q3"]
    assert moved["2026Q4"]-original["2026Q4"] == pytest.approx(2.4)
    changed = copy.deepcopy(inputs)
    changed[3]["gbv_musd"] += 30
    assert forecast("2026Q4", ASOF, changed, .04, LAM)[0]["revenue_musd"] == original["2026Q4"]
    assert forecast("2027Q1", ASOF, changed, .04, LAM)[0]["revenue_musd"]-original["2027Q1"] == pytest.approx(2.4)


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), -1, 0, True])
def test_invalid_gbv_refused(bad):
    with pytest.raises(ValueError):
        forecast("2026Q4", ASOF, [gbv("2026Q3", bad), gbv("2026Q2", 600)], .04, LAM)


def test_identity_missing_and_duplicate_refused():
    with pytest.raises(ValueError, match="Missing required"):
        forecast("2026Q4", ASOF, [gbv("2026Q3", 300)], .04, LAM)
    with pytest.raises(ValueError, match="Duplicate"):
        forecast("2026Q4", ASOF, [gbv("2026Q3", 300)] * 2, .04, LAM)
    with pytest.raises(ValueError, match="Nights times ADR"):
        forecast("2026Q4", ASOF, [gbv("2026Q3", 300, nights_m=2, adr_usd=100), gbv("2026Q2", 600)], .04, LAM)


def test_future_input_refused():
    row = gbv("2026Q3", 300)
    row["information_date"] = "2026-09-14"
    with pytest.raises(ValueError, match="Future"):
        forecast("2026Q4", ASOF, [row, gbv("2026Q2", 600)], .04, LAM)
    with pytest.raises(ValueError):
        dated(None, ASOF)


def test_synthetic_cohort_conservation_and_independent_ratio():
    r = timing_identity(cohorts(), "2026Q4", ASOF)
    assert sum(c["reference_contribution_weight"] for c in r["cohort_rows"]) == pytest.approx(1)
    assert [c["reference_contribution_weight"] for c in r["cohort_rows"]] == pytest.approx([.5, .5])
    assert r["ordinary_booking_factor"] == pytest.approx(1.1)
    assert r["rnpl_retimed_factor"] == pytest.approx(1.125)
    assert r["incremental_timing_multiplier"] == pytest.approx(1.125/1.1)


@pytest.mark.parametrize("share,expected", [(0, 1), (1, 1.2/1.1)])
def test_zero_and_full_rnpl(share, expected):
    c = cohorts()
    for row in c:
        row["rnpl_share"] = share
    assert timing_identity(c, "2026Q4", ASOF)["incremental_timing_multiplier"] == pytest.approx(expected)


@pytest.mark.parametrize("rate", [1, 1.1, .8])
def test_equal_booking_recognition_rates(rate):
    c = cohorts()
    for row in c:
        row["booking_fx_ratio"] = rate
        row["rnpl_allocation"][0]["fx_ratio"] = rate
    assert timing_identity(c, "2026Q4", ASOF)["incremental_timing_multiplier"] == pytest.approx(1)


@pytest.mark.parametrize("field,value", [("booking_fx_ratio", None), ("rnpl_share", -1), ("rnpl_share", 1.1),
                                         ("share_denominator", "unpaid_stock"), ("rate_direction", "currency_per_USD"),
                                         ("information_date", "2026-09-14")])
def test_invalid_cohort_contract(field, value):
    c = cohorts()
    c[0][field] = value
    with pytest.raises(ValueError):
        timing_identity(c, "2026Q4", ASOF)


def test_missing_or_mistimed_recognition():
    for change in [dict(weight=.9), dict(fx_ratio=None), dict(information_date="2026-09-14"), dict(recognition_quarter="2027Q1")]:
        c = cohorts()
        c[0]["rnpl_allocation"][0].update(change)
        with pytest.raises(ValueError):
            timing_identity(c, "2026Q4", ASOF)


@pytest.mark.parametrize("hedge", [-10, 0, 10])
def test_hedges_held_unchanged_and_fx_applied_once(hedge):
    baseline, row = bundle_row(hedge)
    result = apply_row(baseline, row, ASOF)
    expected = (100-hedge)*(1.125/1.1)+hedge
    assert result["revenue_musd"] == pytest.approx(expected)
    assert result["guide_musd"] == pytest.approx(expected/1.04)
    assert result["incremental_fx_musd"] == pytest.approx((100-hedge)*(.025/1.1))
    row["baseline_scenario"] = result["scenario"]
    with pytest.raises(ValueError, match="already applied"):
        apply_row(result, row, ASOF)


@pytest.mark.parametrize("field,value", [("baseline_hedge_musd", None), ("hedge_evidence_status", "unidentified"),
                                        ("treatment", "full_fx_overlay"), ("baseline_revenue_musd", 99),
                                        ("lower", 2), ("value", 1.2), ("reference_basis", "wrong_reference")])
def test_invalid_application_refused(field, value):
    baseline, row = bundle_row()
    row[field] = value
    with pytest.raises(ValueError):
        apply_row(baseline, row, ASOF)


def test_cohort_reconstruction_required():
    baseline, row = bundle_row()
    baseline["cohort_gbv_musd"]["2026Q2"] = 661
    with pytest.raises(ValueError, match="reconstruct"):
        apply_row(baseline, row, ASOF)


def test_versioned_bundle_hash_and_path_controls(tmp_path):
    _, row = bundle_row()
    data = tmp_path / "adapter.json"
    data.write_text(json.dumps([row]), encoding="utf-8")
    manifest = dict(bundle_version="synthetic_test_v1", commit="a"*40, information_date="2026-09-11",
                    files=[dict(path="adapter.json", role="revenue_adapter", sha256=hashlib.sha256(data.read_bytes()).hexdigest())])
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert len(load_bundle(path, ASOF)[1]) == 1
    data.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_bundle(path, ASOF)
    manifest["files"][0]["path"] = "../outside.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        load_bundle(path, ASOF)


@pytest.mark.parametrize("old,new", [(-10, 15), (10, -15), (0, 0)])
def test_explicit_changed_hedge_preserves_accounting(old, new):
    baseline, row = bundle_row(old)
    row.update(scenario_hedge_musd=new, hedge_treatment="explicit_reconciled_scenario_hedge",
               scenario_hedge_evidence_status="verified_scenario_reconciliation")
    result = apply_row(baseline, row, ASOF)
    assert result["revenue_musd"] == pytest.approx((100-old)*(1.125/1.1)+new)
    assert result["incremental_hedge_musd"] == new-old


@pytest.mark.parametrize("field,value", [("scenario_hedge_musd",None), ("scenario_hedge_evidence_status",None),
                                         ("multiplier_accounting_basis","after_hedge"),
                                         ("multiplier_accounting_basis","unresolved")])
def test_missing_new_hedge_and_after_hedge_multiplier_refused(field,value):
    baseline,row=bundle_row()
    row[field]=value
    with pytest.raises(ValueError):
        apply_row(baseline,row,ASOF)
