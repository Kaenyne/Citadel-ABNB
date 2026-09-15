"""Independent adversarial calls to the actual quant implementation."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

from economic_contract import matrix_views, joint_variance

FILE = Path(__file__).resolve().parents[1] / "quant_v1/run.py"
SPEC = importlib.util.spec_from_file_location("reviewed_joint_quant", FILE)
quant = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quant)
sys.modules["run"] = quant
DIAG_SPEC = importlib.util.spec_from_file_location("reviewed_joint_diagnostics", FILE.with_name("diagnostics.py"))
diagnostics = importlib.util.module_from_spec(DIAG_SPEC)
DIAG_SPEC.loader.exec_module(diagnostics)


@pytest.fixture(scope="module")
def data():
    return quant.load_inputs()


def test_actual_allocation_normalizations_and_tail_agree_with_independent_dollars():
    rows = pd.DataFrame([dict(quarter="2024Q1", season=1, year=2024,
                             g0=100., g1=300., g2=200., g3=80., g4=120., gtail=100.,
                             revenue_musd=35.)])
    fit = {"phi": np.array([.4, .3, .2, .1]), "lambda": np.array([.2]*4)}
    a = quant.allocation(rows, fit, [3, 4])
    expected = np.array([8., 18., 8., .8, 1.2])
    np.testing.assert_allclose(a.allocated_revenue_musd, expected)
    independent = matrix_views(expected[:, None], [100, 300, 200, 80, 120], [35])
    np.testing.assert_allclose(a.backward_share, independent["conditional_allocated_shares"][:, 0])
    np.testing.assert_allclose(a.actual_revenue_attribution_share, independent["corporate_revenue_shares"][:, 0])
    np.testing.assert_allclose(a.effective_forward_fee_per_net_gbv, independent["effective_forward_rates"][:, 0])
    np.testing.assert_allclose(a.unallocated_residual_share, independent["residual_revenue_share"][0])
    assert a.loc[a.lag.ge(3), "allocated_revenue_musd"].sum() == pytest.approx(2)
    assert a.column_residual_musd.iloc[0] == pytest.approx(-1)  # discrepancy remains visible, not renormalized away
    realized = quant.allocation(rows, fit, [3, 4], observed_scale=True)
    np.testing.assert_allclose(realized.allocated_revenue_musd.sum(), 35)
    assert set(realized.basis) == {"realized_total_conditional_allocation"}


def test_missing_tail_history_is_not_silently_averaged(data):
    panel, _ = data
    full = quant.features(panel, [3, 4])
    incomplete = panel.loc[panel.quarter.ne("2022Q1")]
    after = quant.features(incomplete, [3, 4])
    assert "2023Q1" in full.quarter.values
    assert "2023Q1" not in after.quarter.values


def test_full_replay_poison_future_actuals_and_guides(monkeypatch, data):
    panel, calendar = data
    panel = panel.loc[panel.quarter.le("2025Q4")].copy()
    cutoff = pd.Timestamp(calendar.set_index("print_quarter").loc["2025Q2", "print_date"])
    monkeypatch.setattr(quant, "TAILS", {"tail34": [3, 4]})
    base, skipped = quant.pit_replay(panel, calendar)
    poison = panel.copy()
    future = poison.print_date.gt(cutoff)
    poison.loc[future, "gbv_musd"] *= 17
    poison.loc[future, "revenue_musd"] *= 31
    altered_calendar = calendar.copy()
    later_guides = pd.to_datetime(altered_calendar.print_date).gt(cutoff)
    altered_calendar.loc[later_guides, "guide_mid"] *= 41
    changed, changed_skipped = quant.pit_replay(poison, altered_calendar)
    fields = ["quarter", "origin", "candidate_revenue_musd", "baseline_revenue_musd",
              "candidate_guide_musd", "baseline_guide_musd", "cushion_pct",
              "gbv_forecast_musd", "lag1_gbv_forecast_musd", "weight_0", "weight_1", "weight_2", "weight_3"]
    pd.testing.assert_frame_equal(base[fields], changed[fields], check_exact=True)
    pd.testing.assert_frame_equal(skipped, changed_skipped)
    assert pd.to_datetime(base.origin).le(cutoff).all()
    assert (pd.to_datetime(base.guide_event_date) > pd.to_datetime(base.origin)).all()
    assert not np.allclose(base.oracle_revenue_musd, changed.oracle_revenue_musd)
    # Poison includes same-event lag1 and target GBV; oracle changes but pre-event forecasts do not.


def test_known_gbv_positive_control_changes_forecast(data):
    panel, calendar = data
    cutoff = pd.Timestamp(calendar.set_index("print_quarter").loc["2025Q2", "print_date"])
    baseline = quant.forecast_gbv(panel, "2025Q4", cutoff)[0]
    altered = panel.copy()
    altered.loc[altered.quarter.eq("2025Q2"), "gbv_musd"] *= 1.1
    assert not np.isclose(baseline, quant.forecast_gbv(altered, "2025Q4", cutoff)[0])


def test_forecast_rejects_already_published_target(data):
    panel, calendar = data
    cutoff = calendar.set_index("print_quarter").loc["2025Q2", "print_date"]
    with pytest.raises(ValueError, match="unprinted"):
        quant.forecast_gbv(panel, "2025Q2", cutoff)


def test_fractional_bounds_normalize_column_not_beta():
    z = np.array([[2., 8.]])
    upper = np.vstack([z, -z])
    bound = np.array([1.01, -.99])
    low, high = quant.ratio_bounds(z, upper, bound, 0, np.array([1, 0]))
    np.testing.assert_allclose([low[0], high[0]], [0, 1], atol=1e-10)
    for value, beta in [low, high]:
        assert .99 - 1e-10 <= float(z[0] @ beta) <= 1.01 + 1e-10
        np.testing.assert_allclose(value, z[0, 0]*beta[0]/float(z[0]@beta))


def test_stale_k2_restriction_operates_on_backward_share():
    rows = pd.DataFrame([dict(g0=100., g1=200., g2=300., g3=400., revenue_musd=50.)])
    prior = [(0.1, .2), (.2, .3), (.3, .4), (.2, .3)]
    z, upper, bound = quant.lp_problem(rows, [0, 1, 2, 3], .01, prior)
    low, high = quant.ratio_bounds(z, upper, bound, 0, np.array([1, 0, 0, 0]))
    np.testing.assert_allclose([low[0], high[0]], [.1, .2], atol=1e-10)
    for _, beta in [low, high]:
        share = z[0]*beta/(z[0]@beta)
        for actual, (lo, hi) in zip(share, prior):
            assert lo-1e-10 <= actual <= hi+1e-10


def test_quant_covariance_preserves_offsetting_components():
    rows = []
    for year, x in zip([2023, 2024, 2025], [1., 2., 3.]):
        for season in range(1, 5):
            for group, value in zip(quant.GROUPS, [x, 5-x, 2*x, 10-2*x]):
                rows.append(dict(quarter=f"{year}Q{season}", season=season, year=year, group=group,
                                 allocated_revenue_musd=value, backward_share=value/15,
                                 effective_forward_fee_per_net_gbv=value/100))
    _, covariance, identities = quant.temporal_stats(pd.DataFrame(rows))
    independent = joint_variance([[1, 4, 2, 8], [2, 3, 4, 6], [3, 2, 6, 4]])
    np.testing.assert_allclose(identities.total_variance_musd2, independent["direct_total_variance"])
    np.testing.assert_allclose(identities.diagonal_sum_musd2, independent["diagonal"])
    np.testing.assert_allclose(identities.offdiagonal_sum_musd2, independent["off_diagonal"])
    assert (identities.diagonal_sum_musd2 > 0).all()
    assert np.max(np.abs(identities.reconciliation_error_musd2)) < 1e-12


def test_pr60_explicit_future_same_day_commit_is_rejected():
    f = pd.DataFrame([
        dict(quarter="2024Q1", commit_date=pd.Timestamp("2024-03-20"), committed_utc=pd.Timestamp("2024-03-20T10:00:00Z"), days_cur_present=75, eu40_flt_da_yoy=4.),
        dict(quarter="2024Q2", commit_date=pd.Timestamp("2024-08-08"), committed_utc=pd.Timestamp("2024-08-08T23:59:59Z"), days_cur_present=75, eu40_flt_da_yoy=999.),
    ])
    selected = diagnostics.eligible_flight(f, "2024-08-08", "2024Q2")
    assert selected.quarter == "2024Q1"
    assert selected.eu40_flt_da_yoy == 4


def test_pr60_incomplete_and_stale_rows_do_not_fill_a_feature():
    f = pd.DataFrame([dict(quarter="2024Q2", commit_date=pd.Timestamp("2024-07-01"),
                          committed_utc=pd.Timestamp("2024-07-01T12:00:00Z"), days_cur_present=74, eu40_flt_da_yoy=4.)])
    with pytest.raises(ValueError, match="eligible"):
        diagnostics.eligible_flight(f, "2024-08-08", "2024Q2")
    f.loc[0, "days_cur_present"] = 75
    f.loc[0, "quarter"] = "2023Q1"
    with pytest.raises(ValueError, match="stale"):
        diagnostics.eligible_flight(f, "2024-08-08", "2024Q2")


def test_pr60_training_never_uses_later_company_outcomes_or_commits(data):
    panel, calendar = data
    flights = diagnostics.flight_source()
    origin = pd.Timestamp("2025-08-06")
    before = diagnostics.flight_training(panel, calendar, flights, origin)
    poison = panel.copy()
    poison.loc[poison.print_date.gt(origin), ["gbv_musd", "revenue_musd"]] *= 23
    flights.loc[flights.committed_utc.gt(origin.tz_localize("UTC")), "eu40_flt_da_yoy"] *= 10000
    after = diagnostics.flight_training(poison, calendar, flights, origin)
    pd.testing.assert_frame_equal(before, after, check_exact=True)
    assert (pd.to_datetime(before.outcome_available) <= origin).all()
