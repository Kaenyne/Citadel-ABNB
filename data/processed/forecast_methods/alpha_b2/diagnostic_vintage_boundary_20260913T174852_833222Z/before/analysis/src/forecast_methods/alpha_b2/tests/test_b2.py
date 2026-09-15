from pathlib import Path
import importlib.util
import sys

import numpy as np
import pandas as pd
import pytest

MODULE = Path(__file__).resolve().parents[1] / "run.py"
spec = importlib.util.spec_from_file_location("alpha_b2_run", MODULE)
B = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = B
spec.loader.exec_module(B)


def vintage(**updates):
    row = dict(register_id="test", vendor="LSEG", period="2024Q3", metric="revenue", value=100.,
               role="pre_guide", pit_usable=True, vendor_attributed=True, as_of_timestamp="2024-08-06")
    row.update(updates)
    return row


@pytest.mark.parametrize("changes", [dict(role="current"), dict(pit_usable=False),
    dict(vendor_attributed=False), dict(as_of_timestamp="2024-08-07"), dict(as_of_timestamp=None),
    dict(value=np.nan), dict(value=-1)])
def test_consensus_bad_or_future_rows_excluded(changes):
    rows = pd.DataFrame([vintage(**changes)])
    assert B.admissible_consensus(rows, "2024Q3", "2024-08-06", "pre_guide") is None


def test_same_day_morning_is_admissible():
    rows = pd.DataFrame([vintage(as_of_timestamp="2024-08-06T10:00:00")])
    assert B.admissible_consensus(rows, "2024Q3", "2024-08-06", "pre_guide")["value"] == 100


def test_gbv_formula_units_and_recursion():
    p = pd.DataFrame(dict(quarter=[str(q) for q in pd.period_range("2022Q1", periods=8, freq="Q")],
                          gbv_musd=[100, 200, 150, 80, 110, 220, 165, 88]))
    result, growth = B.extrapolated_gbv(p)
    assert growth == pytest.approx(.1)
    assert result["2024Q1"] == pytest.approx(96.8)
    assert result["2024Q2"] == pytest.approx(106.48)


def test_short_growth_history_refuses():
    p = pd.DataFrame(dict(quarter=["2022Q1", "2023Q1"], gbv_musd=[100, 110]))
    with pytest.raises(B.K.DataUnavailable):
        B.trailing_gbv_growth(p)


def test_zero_revision_is_not_a_directional_hit():
    frame = pd.DataFrame(dict(event_date=["2024-01-01", "2024-02-01", "2024-03-01"],
                              s1_pct=[1., -1., 1.], revision_pct=[0., -2., 3.]))
    result = B.pair_stats(frame)
    assert result["hits"] == 2
    assert result["n_strong"] == 3
    assert result["zero_revisions"] == 1


def test_empty_and_constant_statistics_are_unavailable():
    frame = pd.DataFrame(dict(event_date=["2024-01-01"] * 4, s1_pct=[1.] * 4, revision_pct=[0.] * 4))
    result = B.pair_stats(frame)
    assert np.isnan(result["corr"])
    assert result["hits"] == 0
    assert np.isnan(B.wilson(0, 0)[0])


def test_wilson_boundary_and_bootstrap_reproducible():
    lo, hi = B.wilson(0, 6)
    assert 0 <= lo < .001 and .3 < hi < .5
    x, y = np.arange(10.), np.arange(10.) ** 2
    assert B.corr_bootstrap(x, y, draws=200) == B.corr_bootstrap(x, y, draws=200)


def test_engine_same_letter_identity():
    term, _ = B.forecast_term("2026-05-07", max_steps=2)
    row = term[(term.horizon_from_print == 1) & np.isclose(term.weight, 2 / 3)].iloc[0]
    engine = B.K.kernel_guide("2026Q2", "2026-05-08")
    assert row.kernel_guide_musd == pytest.approx(engine["point"], rel=1e-12)
    assert row.knowable_from <= "2026-05-07"


def test_live_lseg_family_counted_once():
    sources = pd.DataFrame([vintage(period="2026Q4", role="current", vendor="Yahoo Finance", value=3160),
                            vintage(register_id="av", period="2026Q4", role="current", vendor="Alpha Vantage", value=3158)])
    live = pd.DataFrame([dict(quarter=q, weight=2 / 3, revenue_musd=3200., kernel_guide_musd=3150.)
                         for q in ("2026Q4", "2027Q1")])
    result = B.live_comparisons(sources, live, "2026-09-13")
    assert len(result[result.quarter == "2026Q4"]) == 1
    assert result.iloc[0].consensus_musd == 3158
    assert result[result.quarter == "2027Q1"].consensus_musd.isna().all()


def test_live_mixed_utc_date_stamps_and_future_rejection():
    now = pd.Timestamp.now(tz="UTC")
    today = str(now.date())
    past = now - pd.Timedelta(seconds=10)
    future = now + pd.Timedelta(days=1)
    sources = pd.DataFrame([
        vintage(register_id="old", period="2026Q4", role="current", as_of_timestamp="2026-09-11", value=3100),
        vintage(register_id="new", period="2026Q4", role="current", as_of_timestamp=past.isoformat(), value=3200),
        vintage(register_id="future", period="2026Q4", role="current", as_of_timestamp=future.isoformat(), value=9999)])
    assert B.admissible_consensus(sources, "2026Q4", today, "current")["register_id"] == "new"
    live = pd.DataFrame([dict(quarter=q, weight=2 / 3, revenue_musd=3200., kernel_guide_musd=3150.)
                         for q in ("2026Q4", "2027Q1")])
    result = B.live_comparisons(sources, live, today)
    assert result.iloc[0].consensus_musd == 3200


def test_registry_uses_harness_loaded_date_types():
    row = dict(horizon_from_print=2, weight=2 / 3, revenue_musd=2800., quarter="2024Q2",
               event_date="2024-02-13", known_panel_n=14, knowable_from="2024-02-13")
    hist = pd.DataFrame([dict(**row, prior_basis=b) for b in ("PIT", "full_sample")])
    empty_live = pd.DataFrame(columns=["quarter", "weight"])
    registry = B.make_registry(hist, empty_live, pd.DataFrame())
    assert len(registry) == 4
    assert registry.base_naive.iloc[0] == pytest.approx(2896.6940063091483)
    assert registry.horizon_q.eq(1).all()


def test_live_latest_selection_uses_instant_not_timezone_text():
    sources = pd.DataFrame([
        vintage(register_id="earlier", period="2026Q4", role="current", as_of_timestamp="2026-09-11T15:00:00+09:00", value=3100),
        vintage(register_id="later", period="2026Q4", role="current", as_of_timestamp="2026-09-11T10:00:00Z", value=3200)])
    live = pd.DataFrame([dict(quarter=q, weight=2 / 3, revenue_musd=3200., kernel_guide_musd=3150.)
                         for q in ("2026Q4", "2027Q1")])
    assert B.live_comparisons(sources, live, "2026-09-13").iloc[0].consensus_musd == 3200


@pytest.mark.parametrize("quarter,vintage,expected", [
    ("2024Q2", "2024-02-13", 1), ("2026Q4", "2026-09-13", 1),
    ("2027Q1", "2026-09-13", 2), ("2026Q3", "2026-09-13", 0)])
def test_registry_horizon_calendar_quarter_contract(quarter, vintage, expected):
    assert B.registry_horizon(quarter, vintage) == expected


def test_registry_negative_horizon_refused():
    with pytest.raises(ValueError, match="nonnegative"):
        B.registry_horizon("2024Q2", "2024-11-07")
