"""Conservation plus independent attacks on the actual pinned L4 interface."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

SPEC = importlib.util.spec_from_file_location("sc_c_consumption_runner", Path(__file__).with_name("run.py"))
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


@pytest.fixture(scope="module")
def source():
    return m.read_csv(m.BUNDLE / "l4_inputs.csv")


@pytest.fixture(scope="module")
def interface():
    snap, _ = m.load_inputs()
    return m.interface_namespace(snap)


def fixture_row():
    baseline = dict(quarter="2026Q4", scenario="fixture", revenue_musd=100,
                    fx_integration_status="pending_explicit_L3_bundle", cushion_decimal=.02,
                    information_date="2026-09-13", cohort_gbv_musd={"2026Q3": 100, "2026Q2": 100})
    cohorts = [dict(booking_quarter=q, currency="EUR", source_ref="synthetic fixture only",
                    evidence_status="assumed", reference_basis="test_reference", information_date="2026-09-13",
                    rate_direction="USD_per_currency", rnpl_share=.5,
                    share_denominator="surviving_recognized_revenue_reference_exposure", reference_gbv_musd=100,
                    booking_fx_ratio=1, rnpl_allocation=[dict(recognition_quarter="2026Q4", weight=1,
                                                            fx_ratio=1.1, information_date="2026-09-13")])
               for q in ["2026Q3", "2026Q2"]]
    row = dict(quarter="2026Q4", metric="revenue_timing_multiplier", scenario="synthetic_adjusted",
               value=1.05, lower=None, upper=None, units="ratio", information_date="2026-09-13",
               evidence_status="assumed", source_ref="synthetic fixture only",
               treatment="incremental_replacement_of_embedded_booking_fx", baseline_scenario="fixture",
               baseline_revenue_musd=100, reference_basis="test_reference",
               embedded_fx="booking_fx_already_in_USD_GBV",
               hedge_treatment="reconciled_baseline_hedges_held_unchanged", baseline_hedge_musd=10,
               hedge_source_ref="synthetic fixture only", hedge_evidence_status="verified_baseline_reconciliation",
               cohorts=cohorts)
    return baseline, row


def test_all_original_cells_and_rows_conserved(source):
    fields, original = source
    result = m.classify_all(fields, original)
    assert len(result) == 1187
    for i, (a, b) in enumerate(zip(original, result), 1):
        assert {k: b[k] for k in fields} == a
        assert b["original_row_number"] == str(i)
        assert b["original_row_sha256"] == m.sha(json.dumps(a, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
        assert b["consumption_status"] in m.STATUSES
        assert b["direct_l4_model_application"] == "blocked"
        for k in ["metric_definition", "bounds_meaning", "parent_baseline_contract", "dependency_contract", "exact_additional_inputs", "not_consume_reason", "l4_may_consume_now"]:
            assert b[k].strip()


def test_counts_and_missing_stay_missing(source):
    result = m.classify_all(*source)
    assert {s: sum(r["consumption_status"] == s for r in result) for s in m.STATUSES} == dict(zip(m.STATUSES, [0, 576, 603, 4, 4, 0]))
    assert all(r["value"] == "" for r in result if r["consumption_status"] == "unavailable")
    assert all(r["consumption_status"] == "unavailable" for r in result if r["value"] == "")


@pytest.mark.parametrize("field,value", [("information_date", "2027-01-01"), ("source_information_date", "nonsense"), ("units", "USD_millions"), ("source_information_date", "2026-09-13T01:00:00"), ("source_information_date", "2026-09-14")])
def test_source_metadata_attacks_rejected(source, field, value):
    fields, rows = source
    rows = copy.deepcopy(rows)
    rows[0][field] = value
    with pytest.raises(ValueError):
        m.classify_all(fields, rows)


def test_operating_multiplier_and_yoy_semantics_are_explicit(source):
    result = m.classify_all(*source)
    fx = next(r for r in result if r["metric"] == "rnpl_fx_replacement_multiplier")
    assert "compatible operating-only T/B" in fx["exact_additional_inputs"]
    assert "aggregate T/B is not certified" in m.GAP_LOOKUP["FX_HEDGE"]["prohibited_shortcut"]
    adr = next(r for r in result if r["metric"] == "adr_exfx_yoy")
    assert "growth in percent" in adr["metric_definition"]
    assert adr["units"] == "percentage_points"


@pytest.mark.parametrize("month,needed,other", [("sep", "September 14/16/18", "October 12/14/16"), ("oct", "October 12/14/16", "September 14/16/18")])
def test_fee_requirements_use_only_the_named_monthly_triplet(source, month, needed, other):
    row = next(r for r in m.classify_all(*source) if r["package"] == "fee_panel" and r["scenario"] == month)
    assert needed in row["exact_additional_inputs"] and other not in row["exact_additional_inputs"]
    assert needed in row["dependency_contract"] and other not in row["dependency_contract"]
    assert "no automatic pooling" in row["exact_additional_inputs"]
    assert row["consumption_status"] == "unavailable" and row["value"] == ""


def test_unknown_fee_month_rejected(source):
    row = next(r.copy() for r in source[1] if r["package"] == "fee_panel")
    row["scenario"] = "pooled"
    with pytest.raises(ValueError, match="Unknown fee month"):
        m.classify(row)


@pytest.mark.parametrize("mutation", ["drop", "duplicate", "unknown_metric", "status_promote", "missing_source", "infinity", "missing_value", "treatment_promote"])
def test_malformed_input_rejected(source, mutation):
    fields, rows = source
    rows = copy.deepcopy(rows)
    if mutation == "drop": rows.pop()
    elif mutation == "duplicate": rows[-1] = rows[0].copy()
    elif mutation == "unknown_metric": rows[0]["metric"] = "new_unreviewed_metric"
    elif mutation == "status_promote": rows[0]["evidence_status"] = "observed"
    elif mutation == "missing_source": rows[0]["source_reference"] = " "
    elif mutation == "infinity": rows[0]["value"] = "Infinity"
    elif mutation == "missing_value": rows[0]["value"] = ""
    elif mutation == "treatment_promote": rows[0]["treatment"] = "incremental"
    with pytest.raises(ValueError): m.classify_all(fields, rows)


def test_all_conditional_routes_have_explicit_gaps(source):
    for r in m.classify_all(*source):
        if r["package"] == "cohort_fx":
            assert {"FX_BASELINE", "FX_HEDGE", "FX_EXPOSURE", "FX_ROOT_QUOTES", "FX_ROUTE", "L4_FORMAT"} <= set(r["gap_ids"].split(";"))
            if r["metric"] in m.FX_DESCRIPTIVE:
                assert r["consumption_status"] == "descriptive_only"
        if r["metric"] in m.ADR_COMPONENTS:
            assert r["consumption_status"] == "descriptive_only"


def test_failed_research_and_coefficient_units_preserved(source):
    result = m.classify_all(*source)
    for r in result:
        if r["package"] in {"nclh", "conversion"}:
            assert r["consumption_status"] == "descriptive_only"
        if r["metric"].startswith("seasonal_conversion_"):
            assert "coefficient level in percent" in r["metric_definition"]
            assert "six year blocks" in r["bounds_meaning"]
        if r["metric"] == "free_to_fixed_PIT_RMSE_ratio":
            assert float(r["value"]) > 1
            assert "nested" in r["dependency_contract"]


def test_frozen_capture_inventory_has_no_material_new_content():
    _, inv = m.load_inputs()
    assert inv["as_of"] == "2026-09-14"
    assert len(inv["files"]) == 16
    assert not inv["actual_capture_wave_files"]
    assert not inv["material_new_content_files"]
    assert len(inv["changed_files"]) == 12
    assert all(r["content_equal_after_CRLF_to_LF"] for r in inv["files"])


def test_pinned_l4_actual_hedge_and_conservation_guards(interface):
    baseline, row = fixture_row()
    got = interface["apply_row"](baseline, row, "2026-09-14")
    assert got["revenue_musd"] == pytest.approx(104.5)
    assert got["revenue_musd"] != 105  # Hedge dollars are held unchanged.
    row2 = copy.deepcopy(row)
    row2["cohorts"][0]["rnpl_allocation"][0]["weight"] = .9
    with pytest.raises(ValueError, match="conserve"): interface["apply_row"](baseline, row2, "2026-09-14")
    row2 = copy.deepcopy(row); row2["baseline_hedge_musd"] = None
    with pytest.raises(ValueError): interface["apply_row"](baseline, row2, "2026-09-14")
    row2 = copy.deepcopy(row); row2["baseline_revenue_musd"] = 100.01
    with pytest.raises(ValueError, match="baseline revenue"): interface["apply_row"](baseline, row2, "2026-09-14")
    row2 = copy.deepcopy(row); row2["baseline_scenario"] = got["scenario"]
    with pytest.raises(ValueError, match="already applied"): interface["apply_row"](got, row2, "2026-09-14")


def test_pinned_l4_root_quote_metadata_is_not_required_or_validated(interface):
    baseline, row = fixture_row()
    accepted = interface["apply_row"](baseline, row, "2026-09-14")
    # This is an interface gap demonstration, not real rate evidence or model adoption.
    row["cohorts"][0].update(booking_quote_cutoff="2027-01-01", booking_rate_source="missing",
                              booking_observation_status="observed")
    assert interface["apply_row"](baseline, row, "2026-09-14")["revenue_musd"] == accepted["revenue_musd"]


def test_pinned_l4_manifest_commit_is_syntax_only(interface, tmp_path):
    _, row = fixture_row()
    data = json.dumps([row]).encode()
    (tmp_path / "adapter.json").write_bytes(data)
    manifest = dict(bundle_version="synthetic", commit="f"*40, information_date="2026-09-13",
                    files=[dict(path="adapter.json", sha256=m.sha(data), role="revenue_adapter")])
    file = tmp_path / "manifest.json"; file.write_text(json.dumps(manifest))
    got, result = interface["load_bundle"](file, "2026-09-14")
    assert got["commit"] == "f"*40 and len(result) == 1
    manifest["files"][0]["sha256"] = "0"*64; file.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="hash mismatch"): interface["load_bundle"](file, "2026-09-14")


def test_original_research_bundle_incompatible_with_existing_interface(interface, source):
    with pytest.raises(ValueError, match="Missing bundle commit"):
        interface["load_bundle"](m.BUNDLE / "bundle.json", "2026-09-14")
    baseline, _ = fixture_row()
    for r in source[1]:
        with pytest.raises(ValueError, match="Incomplete L3 adapter contract"):
            interface["apply_row"](baseline, r, "2026-09-14")


def test_rebuild_is_deterministic_and_refuses_overwrite(tmp_path):
    script = Path(__file__).with_name("run.py")
    outputs = [tmp_path / "a", tmp_path / "b"]
    for path in outputs:
        subprocess.run([sys.executable, "-B", str(script), "--out", str(path)], cwd=m.ROOT, check=True, capture_output=True)
    for path in outputs[0].iterdir():
        assert path.read_bytes() == (outputs[1] / path.name).read_bytes()
    result = subprocess.run([sys.executable, "-B", str(script), "--out", str(outputs[0])], cwd=m.ROOT, capture_output=True)
    assert result.returncode != 0 and b"Immutable output already exists" in result.stderr
    summary = json.loads((outputs[0] / "summary.json").read_text())
    assert summary["original_cells_preserved"] == 33236
    _, basis = m.read_csv(outputs[0] / "guide_basis_audit.csv")
    assert len(basis) == 1
    assert float(basis[0]["revenue_minus_revenue_consensus_musd"]) > 0
    assert float(basis[0]["gap_musd"]) < 0
    assert basis[0]["guide_expectation_consensus"] == "unavailable"
