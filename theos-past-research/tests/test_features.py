import pytest

from abnb_guidance.features import derive_one_target


def test_guidance_target_sign_conventions():
    row = derive_one_target(guide_low=95, guide_high=105, consensus=110, actual=108)

    assert row.guide_mid == 100
    assert row.range_width_pct == 0.10
    assert row.guidance_surprise_pct == pytest.approx(-10 / 110)
    assert row.ex_ante_conservatism_pct == pytest.approx(10 / 110)
    assert row.realized_cushion_pct == 0.08
    assert row.actual_range_position == "above"


def test_target_without_consensus_retains_other_outputs():
    row = derive_one_target(guide_low=95, guide_high=105, consensus=None, actual=100)

    assert row.guidance_surprise_pct is None
    assert row.ex_ante_conservatism_pct is None
    assert row.actual_range_position == "within"


def test_zero_midpoint_is_rejected():
    with pytest.raises(ValueError, match="midpoint"):
        derive_one_target(guide_low=-1, guide_high=1, consensus=2, actual=1)
