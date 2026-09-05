from decimal import Decimal

import pytest

from abnb_forecasting.baselines import (
    median_range_width,
    policy_adjusted_baseline,
    residual_interval,
    seasonal_naive,
)


def test_seasonal_naive_uses_latest_prior_same_quarter() -> None:
    history = [
        {"guided_period": "2024Q3", "guidance_midpoint": "2700"},
        {"guided_period": "2025Q2", "guidance_midpoint": "2750"},
        {"guided_period": "2025Q3", "guidance_midpoint": "3000"},
    ]

    assert seasonal_naive(history, "2026Q3") == Decimal("3000")


def test_seasonal_naive_fails_when_comparator_is_absent() -> None:
    with pytest.raises(ValueError, match="same-quarter"):
        seasonal_naive([], "2026Q3")


def test_policy_baseline_uses_median_signed_management_offset() -> None:
    assert policy_adjusted_baseline("3200", ["-100", "-50", "25"]) == Decimal(
        "3150"
    )


def test_policy_baseline_requires_historical_offsets() -> None:
    with pytest.raises(ValueError, match="policy offset"):
        policy_adjusted_baseline("3200", [])


def test_range_width_and_residual_interval_are_deterministic() -> None:
    assert median_range_width(["80", "100", "120"]) == Decimal("100")
    assert residual_interval("3150", ["-200", "-100", "0", "100", "200"]) == (
        Decimal("2990.0"),
        Decimal("3310.0"),
    )


def test_negative_guidance_range_width_is_rejected() -> None:
    with pytest.raises(ValueError, match="negative"):
        median_range_width(["80", "-1", "120"])
