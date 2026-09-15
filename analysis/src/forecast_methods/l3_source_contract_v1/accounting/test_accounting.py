"""Failure-mode tests of source/denominator gates; no empirical thesis tests."""
import copy
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("_l3_sc_b_accounting", Path(__file__).with_name("run.py"))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


@pytest.fixture(scope="module")
def rows():
    return r.enrich_rows(r.read_rows())


def request(row):
    return dict(use="conditional_exhibit_only", baseline_id=r.BASELINE, baseline_currency_basis="reported_USD",
                baseline_value_usd=row["baseline_value_usd"], u_denominator="reference_basis_recognized_revenue_flow",
                u_evidence="scenario", fixing_evidence="scenario_hypothesis", hedge_policy="inherited_hedges_unresolved_no_new_hedge_or_afterhedge_claim",
                cash_recognition_equivalence=False, rnpl_incremental_demand=0, extra_cancellation_haircut=0,
                new_hedge_amount=None, extra_fx_layer=False, origin=r.AS_OF, target_period=row["quarter"], scenario=row["scenario"])


def test_all_original_rows_cells_retained_with_unique_routes(rows):
    original = r.read_rows()
    assert len(rows) == len(original) == 1080
    assert sum(x["contract_allowed_route"].startswith("conditional_") for x in rows) == 540
    for src, out in zip(original, rows):
        assert all(out[k] == v for k, v in src.items())
        assert bool(out["contract_allowed_route"]) != bool(out["contract_unusable_reason"])
        assert out["contract_direct_L4_use"] == "unavailable"


def test_one_conditional_arithmetic_route_is_admitted_but_no_production(rows):
    row = next(x for x in rows if x["metric"] == "rnpl_fx_incremental_replacement")
    assert r.validate_conditional_use([row], request(row))["production_adoption"] is False


def test_reenriched_tampered_source_fails_hash_binding(tmp_path, monkeypatch):
    original = r.read_rows()
    edited = next(x for x in original if x["metric"] == "rnpl_fx_incremental_replacement")
    edited["value"] = "12345"
    file = tmp_path / "tampered_adapter.csv"
    r.write_csv(file, original)
    monkeypatch.setattr(r, "SOURCE", file)
    rebuilt = r.enrich_rows(r.read_rows())
    row = next(x for x in rebuilt if x["metric"] == "rnpl_fx_incremental_replacement")
    assert row["value"] == "12345"
    with pytest.raises(ValueError, match="frozen bundle FX input changed"):
        r.validate_conditional_use([row], request(row))


@pytest.mark.parametrize("field,value", [
    ("use", "production"), ("u_denominator", "unpaid_stock"), ("u_evidence", "measured"),
    ("fixing_evidence", "recognition_proves_fixing"), ("hedge_policy", "certified_prehedge"),
    ("hedge_policy", "hold_embedded_unchanged_no_new_hedge"),
    ("new_hedge_amount", -26000000), ("rnpl_incremental_demand", .1), ("extra_cancellation_haircut", .02),
    ("extra_fx_layer", True), ("cash_recognition_equivalence", True), ("origin", "2026-09-13"),
    ("origin", "2026-09-15"), ("baseline_currency_basis", "reference_USD"), ("target_period", "2026Q4"),
])
def test_rejects_wrong_economic_or_information_contract(rows, field, value):
    row = next(x for x in rows if x["metric"] == "rnpl_fx_incremental_replacement")
    req = request(row); req[field] = value
    with pytest.raises(ValueError):
        r.validate_conditional_use([row], req)


def test_no_stacking_equivalent_forms_or_gross_multiplier(rows):
    candidates = [x for x in rows[:6] if x["contract_allowed_route"].startswith("conditional_")]
    with pytest.raises(ValueError, match="exactly one"):
        r.validate_conditional_use(candidates, request(candidates[0]))
    diag = next(x for x in rows if x["metric"] == "rnpl_fx_level_multiplier")
    with pytest.raises(ValueError, match="diagnostic"):
        r.validate_conditional_use([diag], request(diag))


@pytest.mark.parametrize("field,value", [("contract_denominator", "R0"), ("value", "NaN"), ("units", "USD_millions")])
def test_mutated_bound_rows_rejected(rows, field, value):
    row = copy.deepcopy(next(x for x in rows if x["metric"] == "rnpl_fx_replacement_multiplier"))
    row[field] = value
    with pytest.raises(ValueError, match="immutable"):
        r.validate_conditional_use([row], request(row))


@pytest.mark.parametrize("attack", ["blank", "date", "hash", "two_routes", "unavailable_route", "wrong_denominator", "fact_date", "event_source"])
def test_definition_and_source_integrity(attack):
    s = r.load_spec()
    if attack == "blank": s["definitions"][0]["denominator"] = " "
    if attack == "date": s["definitions"][0]["admissible_origin"] = "2026-09-15"
    if attack == "hash": s["sources"][0]["sha256"] = "z" * 64
    if attack == "two_routes": s["definitions"][0]["unusable_reason"] = "also unusable"
    if attack == "unavailable_route": s["definitions"][0]["evidence_status"] = "unavailable"
    if attack == "wrong_denominator": next(x for x in s["definitions"] if x["id"] == "rnpl_fx_replacement_multiplier")["denominator"] = "R0"
    if attack == "fact_date": s["facts"][0]["source_date"] = "2026-09-15"
    if attack == "event_source": s["events"][0]["fact_ids"] = "missing_fact"
    with pytest.raises(ValueError): r.validate_spec(s)


def test_synthetic_denominator_counterexamples():
    # Fixed coefficient differs from arithmetic contribution; backward differs from forward.
    a1 = 2 / 3; g1, g2 = 20., 30.
    assert a1*g1/(a1*g1+(1-a1)*g2) != pytest.approx(a1)
    matrix = [[60., 40.], [40., 10.]]
    assert matrix[1][0]/sum(x[0] for x in matrix) == .4
    assert matrix[1][0]/sum(matrix[1]) == .8
    # All three correctly based replacement routes agree; gross factor on B does not.
    R0 = 100.; B = 60*1.2+40*.9; T = 60*(.5*1.2+.5*1.1)+40*(.5*.9+.5*1.1)
    assert B+(T-B) == pytest.approx(B*(T/B)) == pytest.approx(T)
    assert B*(T/R0) != pytest.approx(T)
    # Nonzero prior timing changes the full YoY contribution, even at same current delta.
    By, Ty, Bt, Tt = 80., 84., 100., 105.
    assert 100*(Tt/Ty-Bt/By) == 0
    assert 100*(Tt-Bt)/By == 6.25
    # No new hedge overlay does not certify preservation of unidentified embedded H.
    B, H, k = 100., 10., 1.05
    assert B*k == 105.
    assert (B-H)*k+H == 104.5
    assert B*k-((B-H)*k+H) == pytest.approx(H*(k-1))


def test_long_stay_and_observed_hedge_qualification_preserved():
    s = r.load_spec(); d = {x["id"]: x for x in s["definitions"]}
    assert any(x["id"] == "K02" and x["value"] == 28 for x in s["facts"])
    assert d["observed_Q2_revenue_hedge_component"]["value"] == -19
    assert d["observed_H1_revenue_hedge_component"]["value"] == -34
    assert d["future_quarter_hedge_component"]["evidence_status"] == "unavailable"


def test_existing_or_outside_output_refused(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="inside"):
        r.run(tmp_path / "outside")
    monkeypatch.setattr(Path, "exists", lambda self: True)
    with pytest.raises(FileExistsError, match="already exists"):
        r.run(r.ROOT / "data/processed/forecast_methods/l3_source_contract_v1/accounting/new_result")
