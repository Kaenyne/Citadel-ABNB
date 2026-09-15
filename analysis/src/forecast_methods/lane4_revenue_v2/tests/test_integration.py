"""Decision-relevant basis, joint dependence, timing and application checks."""
from pathlib import Path
import sys
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integration import expectation_row, tuple_revenue, main_joint_rows, verify_accepted_source, BUNDLE


def test_same_basis_sign_and_hypothetical_identity():
    r=expectation_row(3179.3436542864088,3123.4191151733926,.017904910308494282,3161.021490)
    assert r["revenue_gap_musd"]==pytest.approx(18.3221642864088)
    assert r["revenue_gap_pct"]==pytest.approx(.5796279571136)
    assert r["guide_minus_revenue_diagnostic_musd"]==pytest.approx(-37.6023748266074)
    assert r["hypothetical_street_guide_musd"]==pytest.approx(3105.4192373811)
    assert r["hypothetical_like_basis_guide_gap_musd"]==pytest.approx(r["revenue_gap_musd"]/(1+r["cushion_decimal"]))
    assert r["guide_expectations_status"]=="explicit_dated_guide_expectations_unavailable"


def test_street_cushion_independent_assumption_changes_comparison():
    r=expectation_row(3200,3200/1.02,.02,3180,0)
    assert r["revenue_gap_musd"]>0
    assert r["hypothetical_like_basis_guide_gap_musd"]<0
    with pytest.raises(ValueError):
        expectation_row(3200,3100,.02,3180)


def test_joint_tuple_manual_revenue_and_missing_season_refused():
    p={"w":.8,"lambda_Q1_pct":10,"lambda_Q2_pct":11,"lambda_Q3_pct":12,"lambda_Q4_pct":13}
    assert tuple_revenue(p,"2026Q4",200,100)==pytest.approx(23.4)
    del p["lambda_Q2_pct"]
    with pytest.raises(KeyError):
        tuple_revenue(p,"2026Q4",200,100)


def test_main_stress_keeps_fixed_weight_no_net_overlay_and_conserves_bridge():
    forecasts=[]
    weights=[]
    for scenario in ["review_with_k","adr_mean_reversion","nights_case_a"]:
        for q in ["2026Q3","2026Q4","2027Q1"]:
            forecasts.append(dict(scenario=scenario,quarter=q,lambda_pct=12,lambda_n_train=5,
                                  revenue_musd=24,guide_musd=24/1.02,cushion_decimal=.02,
                                  guide_status="diagnostic" if q=="2026Q3" else "future"))
            for lag in [1,2]:
                weights.append(dict(scenario=scenario,target_quarter=q,lag=lag,gbv_musd=200))
    rows,bridge=main_joint_rows(forecasts,weights,{"mean":{"cushion":.025}})
    assert len(rows)==9
    assert all(r["kernel_weight"]==2/3 and r["net_revenue_factor"]==1 for r in rows)
    soft=next(r for r in rows if r["scenario"]=="joint_soft" and r["quarter"]=="2026Q4")
    assert soft["revenue_musd"]==pytest.approx(23.8)
    assert soft["guide_musd"]==pytest.approx(23.8/1.0388)
    steps=[r for r in bridge if r["scenario"]=="joint_soft" and r["quarter"]=="2026Q4"]
    assert sum(r["delta_revenue_musd"] for r in steps)==pytest.approx(soft["revenue_musd"]-24)
    assert sum(r["delta_guide_musd"] for r in steps)==pytest.approx(soft["guide_musd"]-24/1.02)


def test_accepted_source_manifest_and_joint_inventory():
    assert verify_accepted_source("2026-09-13")["verified_bundle_files"]==108
    d=pd.read_csv(BUNDLE/"payload/conversion/parameter_bootstrap.csv")
    assert len(d)==1000 and d.draw.nunique()==1000
    # Selection changes an entire five-parameter row, never independent bounds.
    p=d.iloc[706].to_dict()
    assert p["draw"]==706
    assert tuple_revenue(p,"2026Q4",26008.556,27200)==pytest.approx(3135.13298874878)


def test_precision_sensitivity_lag_arithmetic():
    q3base=(2*27247+29187)/3-(2*27200+29200)/3
    q4base=(2*26008.556+27247)/3-(2*26008.556+27200)/3
    assert q3base==pytest.approx(27)
    assert q4base==pytest.approx(47/3)
