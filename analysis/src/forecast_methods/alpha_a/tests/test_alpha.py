from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from alpha_a.run import consensus_candidates, executable_column, interval_sign, ridge_slope, statistics, wilson


def vintage(date="2026-08-05", **kwargs):
    row = dict(period="2026Q3", metric="revenue", unit="musd", pit_usable=True,
               vendor_attributed=True, vendor="LSEG", value=4610., as_of_timestamp=date,
               register_id="test", role="pre_guide")
    row.update(kwargs)
    return row


def test_strict_cutoff_rejects_same_day_intraday_and_future():
    f = pd.DataFrame([vintage("2026-08-05"), vintage("2026-08-05T08:00:00"), vintage("2026-08-06"),
                      vintage("2026-08-06T08:00:00"), vintage("2026-09-04")])
    # Mixed formats must not quietly misparse a valid intraday earlier stamp.
    assert len(consensus_candidates(f, "2026Q3", "2026-08-06")) == 2


@pytest.mark.parametrize("kw", [dict(vendor_attributed=False), dict(pit_usable=False),
                                      dict(vendor="vendor_not_recorded"), dict(value=np.nan),
                                      dict(value=-1), dict(unit="busd")])
def test_invalid_consensus_is_refused(kw):
    assert consensus_candidates(pd.DataFrame([vintage(**kw)]), "2026Q3", "2026-08-06").empty


def test_wilson_zero_is_unavailable_not_a_zero_percent_hit_rate():
    assert wilson(0, 0) == (None, None)
    lo, hi = wilson(7, 10)
    assert lo == pytest.approx(.3967781475)
    assert hi == pytest.approx(.8922087326)


def test_rounded_gap_zero_crossing_abstains():
    assert interval_sign(-.001, .001) == 0
    assert interval_sign(.001, .002) == 1
    assert interval_sign(-.002, -.001) == -1


def test_close_returns_are_never_selected():
    assert executable_column(pd.DataFrame(columns=["excess_20d_pct", "abnb_20d_pct"]), 20) is None
    assert executable_column(pd.DataFrame(columns=["open_excess_20d_pct"]), 20) == "open_excess_20d_pct"


def test_ridge_shrinks_toward_one():
    assert ridge_slope([1, 1, 1], [3, 3, 3]) == (2., 1.)
    _, slope = ridge_slope([0, 1, 2], [0, 2, 4])
    assert 1 < slope < 2


def test_no_data_stats_preserve_nulls_and_denominators():
    f = pd.DataFrame([dict(quarter="2024Q1", guide_date="2024-02-13", signal_pct=np.nan,
                           actual_sign=np.nan, actual_gap_pct=np.nan, consensus_musd=np.nan,
                           open_20d_pct=np.nan)])
    s = statistics(f)
    assert list(s.n_dates) == [1, 1]
    assert s.hit_rate.isna().all()
    assert s.wilson_lo.isna().all()
    assert list(s.verdict) == ["underpowered", "underpowered"]
