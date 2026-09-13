import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("alpha_b_run", Path(__file__).resolve().parents[1] / "run.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def test_incomplete_fy_is_not_a_forecast():
    assert np.isnan(b.annual_sum({"2026Q1": 1, "2026Q2": 2, "2026Q3": 3}, 2026))
    assert b.annual_sum({f"2026Q{s}": s for s in range(1, 5)}, 2026) == 10


def test_null_and_small_gaps_cannot_pass():
    d = pd.DataFrame({"gap_pct": [np.nan, .5, -.5], "revision_pct": [1., 1., -1.]})
    r = b.revision_metrics(d)
    assert r["n"] == 0 and r["hit_rate"] is None and not r["pass_line_met"]


def test_zero_revision_is_not_missing_and_constant_correlation_is_undefined():
    r = b.revision_metrics(pd.DataFrame({"gap_pct": [1., 2., 3.], "revision_pct": [0., 0., 0.]}))
    assert r["n"] == 3 and r["hits"] == 0 and r["correlation"] is None


def test_known_predictive_sample():
    r = b.revision_metrics(pd.DataFrame({"gap_pct": [-2., -1., 1., 2.], "revision_pct": [-2., -1., 1., 2.]}))
    assert r["n"] == 4 and r["hits"] == 4 and r["pass_line_met"]
    assert 0 < r["wilson_low"] < r["wilson_high"] <= 1


def test_consensus_same_day_future_and_unattributed_are_excluded():
    d = pd.DataFrame(dict(register_id=list("abcde"), vendor=["Vendor"]*5,
                          period=["FY2026"]*5, metric=["revenue"]*5, unit=["musd"]*5,
                          pit_usable=[True]*5, vendor_attributed=[True, True, True, False, True],
                          value=[10., 11., 12., 13., 14.],
                          as_of_timestamp=["2026-08-01", "2026-09-12", "2026-09-13", "2026-09-11", "2026-08-02"]))
    got = b.stamped_consensus(d, "FY2026", "2026-09-12T23:59:59")
    assert got.register_id.tolist() == ["e"]
    assert got.stale_over_30_days.all()


def test_historical_window_uses_guide_target_and_excludes_august_live():
    dates = b.historical_dates(b.load_calendar())
    assert len(dates) == 14
    assert dates.iloc[0].fiscal_quarter == "2023Q1"
    assert str(dates.iloc[0].guide_date)[:10] == "2023-02-14"
    assert str(dates.iloc[-1].guide_date)[:10] == "2026-05-07"
    assert not dates.guide_date.astype(str).str.startswith("2026-08-06").any()
