"""Adversarial economic examples, independent of quant's implementation.

These validate the review arithmetic, not predictive or identification claims.
"""
import numpy as np
import pytest

from economic_contract import joint_variance, matrix_views


def test_backward_shares_are_not_normalized_forward_coefficients():
    result = matrix_views([[10, 20], [0, 20]], [100, 400], [10, 40])
    np.testing.assert_allclose(result["conditional_allocated_shares"][:, 1], [.5, .5])
    np.testing.assert_allclose(result["effective_forward_rates"][:, 1], [.2, .05])
    normalized_coefficients = np.array([.2, .05]) / .25
    assert not np.allclose(normalized_coefficients, [.5, .5])


def test_residual_dollars_cannot_be_normalized_away():
    result = matrix_views([[20], [20]], [100, 400], [50])
    assert result["conditional_allocated_shares"].sum() == 1
    assert result["corporate_revenue_shares"].sum() == .8
    assert result["residual_revenue_share"][0] == .2
    assert result["residual_dollars"][0] == 10


def test_identical_totals_allow_incompatible_cohort_allocations():
    left = matrix_views([[90, 0], [10, 100]], [200, 400], [100, 100])
    right = matrix_views([[10, 90], [90, 10]], [200, 400], [100, 100])
    np.testing.assert_allclose(left["allocated_revenue"], right["allocated_revenue"])
    assert np.max(np.abs(left["conditional_allocated_shares"] -
                         right["conditional_allocated_shares"])) == .9


def test_three_plus_tail_stays_in_composition_denominator():
    result = matrix_views([[4], [6], [8], [2]], [100, 100, 100, 100], [20])
    np.testing.assert_allclose(result["corporate_revenue_shares"][:, 0], [.2, .3, .4, .1])
    assert result["corporate_revenue_shares"][:3].sum() == .9


def test_right_censored_row_sum_changes_when_future_recognition_arrives():
    observed = matrix_views([[10]], [100], [10])
    mature = matrix_views([[10, 5]], [100], [10, 5])
    assert observed["observed_row_rate_sum"][0] == .1
    assert mature["observed_row_rate_sum"][0] == .15
    # No 'survival_probability' output: neither row sum counts reservations.
    assert "survival_probability" not in observed


def test_reported_net_gbv_does_not_identify_gross_cohort_or_cancellation():
    # Two accounting histories have identical net reporting-period GBV.
    new_bookings = np.array([100., 120.])
    cancellations_of_old_bookings = np.array([10., 30.])
    np.testing.assert_allclose(new_bookings - cancellations_of_old_bookings, [90., 90.])
    revenue = 9.
    assert revenue / 90 == .1
    assert not np.isclose(revenue / new_bookings[0], revenue / new_bookings[1])
    assert not np.isclose(revenue, revenue * .9)  # second haircut loses another dollar flow


def test_offsetting_components_have_zero_total_variance():
    result = joint_variance([[1, 9], [3, 7], [5, 5], [7, 3]])
    assert result["diagonal"] > 0
    assert result["off_diagonal"] < 0
    assert result["direct_total_variance"] == 0
    assert abs(result["identity_error"]) < 1e-12


def test_positive_covariance_cannot_be_omitted():
    result = joint_variance([[1, 2], [2, 4], [3, 6]])
    assert result["diagonal"] == 5
    assert result["off_diagonal"] == 4
    assert result["direct_total_variance"] == 9


@pytest.mark.parametrize("a,b,r", [([[-1]], [100], [10]), ([[np.nan]], [100], [10]),
                                      ([[10]], [0], [10]), ([[10]], [100], [0]),
                                      ([[10, 20]], [100, 200], [10, 20])])
def test_invalid_denominators_and_dimensions_are_rejected(a, b, r):
    with pytest.raises(ValueError):
        matrix_views(a, b, r)
