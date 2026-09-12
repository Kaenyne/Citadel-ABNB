"""Tests for the harness: validator, scorer, PIT rule, conformal arithmetic.

  /Users/theomachado/.venvs/citadel-abnb/bin/python -m pytest \
      analysis/src/forecast_methods/harness/tests -q
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from harness import metrics as M
from harness import quarters as Q
from harness import windows as W
from harness.registry import (RegistryError, StreetVintageError,
                              validate_registry_frame, REQUIRED_COLUMNS)
from harness.baselines import baseline_street
from harness.loaders import load_targets
from harness.score import score_registry


def _row(**kw):
    base = dict(method="toy", object="obj", target="revenue_musd", quarter="2025Q2",
                vintage_date=dt.date(2025, 5, 1), horizon_q=1, point=3000.0, q50=3000.0,
                window="W1", prior_basis="PIT", n_params=2, n_train=12)
    base.update(kw)
    return base


def _frame(*rows):
    return pd.DataFrame(list(rows) or [_row()])


# ------------------------------------------------------------------ windows
def test_window_counts_are_14_and_10():
    assert len(W.GUIDE_DATES_W1) == 14
    assert len(W.GUIDE_DATES_W2) == 10
    assert set(W.GUIDE_DATES_W2) <= set(W.GUIDE_DATES_W1)


def test_live_guide_is_2026_08_06_and_scores_nothing():
    assert W.GUIDE_DATE_LIVE == dt.date(2026, 8, 6)
    assert W.GUIDE_DATE_LIVE not in W.GUIDE_DATES_W1
    assert W.window_of_target("2026Q3") == ["LIVE"]


def test_hardcoded_windows_match_the_guidance_ledger():
    W.assert_matches_ledger()


def test_quarter_canonicalisation():
    assert Q.canon("3Q26") == "2026Q3"
    assert Q.canon("2026Q3") == "2026Q3"
    assert Q.short("2026Q3") == "3Q26"
    assert Q.shift("2026Q1", -4) == "2025Q1"


# ---------------------------------------------------------------- validator
def test_validator_accepts_a_good_frame():
    out = validate_registry_frame(_frame())
    assert len(out) == 1 and out["window"].iloc[0] == "W1"


def test_validator_rejects_missing_required_column():
    d = _frame().drop(columns=["n_params"])
    with pytest.raises(RegistryError, match="missing required columns"):
        validate_registry_frame(d)


def test_validator_rejects_unknown_column():
    d = _frame()
    d["my_special_column"] = 1
    with pytest.raises(RegistryError, match="unknown columns"):
        validate_registry_frame(d)


def test_validator_rejects_bad_window_and_bad_prior_basis():
    with pytest.raises(RegistryError, match="window must be one of"):
        validate_registry_frame(_frame(_row(window="W3")))
    with pytest.raises(RegistryError, match="prior_basis must be one of"):
        validate_registry_frame(_frame(_row(prior_basis="vibes")))


def test_validator_rejects_non_guide_vintage_date():
    with pytest.raises(RegistryError, match="must be a guide date"):
        validate_registry_frame(_frame(_row(vintage_date=dt.date(2025, 5, 2))))


def test_validator_rejects_two_objects_in_one_file():
    with pytest.raises(RegistryError, match="exactly one"):
        validate_registry_frame(_frame(_row(), _row(object="other")))


def test_validator_rejects_non_monotone_quantiles():
    with pytest.raises(RegistryError, match="non-decreasing"):
        validate_registry_frame(_frame(_row(q10=3100.0, q90=2900.0)))


def test_validator_rejects_window_inconsistent_with_quarter():
    # 2023Q2 is a W1 target only; it is not in W2.
    with pytest.raises(RegistryError, match="inconsistent with quarter"):
        validate_registry_frame(_frame(_row(quarter="2023Q2", window="W2",
                                            vintage_date=dt.date(2023, 5, 9))))


# ------------------------------------------------------------------ PIT rule
def test_pit_rule_rejects_forecast_made_after_the_target_printed():
    """2025Q2 printed 2025-08-06. A forecast for it stamped 2025-11-06 is look-ahead."""
    bad = _row(quarter="2025Q2", vintage_date=dt.date(2025, 11, 6), horizon_q=-2)
    with pytest.raises(RegistryError, match="POINT-IN-TIME VIOLATION"):
        validate_registry_frame(_frame(bad))


def test_pit_rule_rejects_forecast_made_on_the_print_date_itself():
    bad = _row(quarter="2025Q2", vintage_date=dt.date(2025, 8, 6), horizon_q=0)
    with pytest.raises(RegistryError, match="POINT-IN-TIME VIOLATION"):
        validate_registry_frame(_frame(bad))


def test_pit_rule_allows_a_live_quarter_that_has_not_printed():
    ok = _row(quarter="2026Q3", window="LIVE", vintage_date=dt.date(2026, 8, 6),
              horizon_q=1)
    assert len(validate_registry_frame(_frame(ok))) == 1


def test_validator_refuses_a_street_vintage_that_postdates_the_forecast():
    bad = _row(street_as_of=dt.date(2026, 9, 4), street_vendor="Zacks",
               quarter="2026Q3", window="LIVE", vintage_date=dt.date(2026, 8, 6))
    with pytest.raises(StreetVintageError, match="postdates"):
        validate_registry_frame(_frame(bad))


def test_street_baseline_refuses_a_later_vintage():
    """The kill-list rule: the 4-Sep Zacks number is not the 6-Aug pre-guide Street."""
    t = load_targets().copy()
    t.loc[t["quarter"] == "2026Q3", "street_pre_guide_musd"] = 4740.0
    t.loc[t["quarter"] == "2026Q3", "street_pre_guide_vendor"] = "Zacks"
    t.loc[t["quarter"] == "2026Q3", "street_pre_guide_as_of"] = dt.date(2026, 9, 4)
    with pytest.raises(StreetVintageError, match="POSTDATES"):
        baseline_street(dt.date(2026, 8, 6), "2026Q3", targets=t)


# ------------------------------------------------------------------- metrics
def test_crps_of_a_point_mass_is_absolute_error():
    assert M.crps_from_quantiles(10.0, [0.5], [7.0]) == pytest.approx(3.0)


def test_crps_is_minimised_at_the_truth_and_is_finite_outside_the_ladder():
    lv = [0.05, 0.25, 0.5, 0.75, 0.95]
    at_truth = M.crps_from_quantiles(100.0, lv, [90, 96, 100, 104, 110])
    off = M.crps_from_quantiles(140.0, lv, [90, 96, 100, 104, 110])
    assert np.isfinite(off) and off > at_truth > 0


def test_pit_is_a_half_at_the_median_and_flags_the_edges():
    lv = [0.05, 0.25, 0.5, 0.75, 0.95]
    vv = [90, 96, 100, 104, 110]
    pit, edge = M.pit_from_quantiles(100.0, lv, vv)
    assert pit == pytest.approx(0.5) and not edge
    _, edge_hi = M.pit_from_quantiles(999.0, lv, vv)
    assert edge_hi


def test_attainable_coverage_at_ncal6_alpha02_is_six_sevenths():
    k, lo, hi = M.attainable_coverage(6, 0.2)
    assert k == 6
    assert lo == pytest.approx(6 / 7)
    assert hi == pytest.approx(1.0)
    grid = {(r["n_cal"], r["alpha"]): r for r in M.attainable_coverage_grid()}
    row = grid[(6, 0.2)]
    assert row["uses_max_residual"] is True
    assert row["quantile_used"] == "max of 6 residuals"
    assert row["exact_nominal_attainable"] is False
    assert "NOT the nominal" in row["note"]


def test_conformal_covers_everything_when_residuals_are_constant():
    y = np.arange(12, dtype=float)
    p = y - 1.0
    cov, n_eval, width = M.rolling_split_conformal(y, p, n_cal=6, alpha=0.2)
    assert n_eval == 6 and cov == pytest.approx(1.0) and width == pytest.approx(2.0)


def test_exchangeability_caveat_string_is_non_empty():
    assert "EXCHANGEABILITY VIOLATED" in M.EXCHANGEABILITY_CAVEAT


# -------------------------------------------------------------------- scorer
def _toy_registry():
    """Two objects on a known series. Actuals for 2024Q1..2025Q2 come from targets.csv;
    the toy forecasts are built as actual + a fixed offset, so MAE/RMSE/bias are known."""
    t = load_targets()
    qs = [q for q in W.W2_TARGETS if q <= "2025Q2"]
    gd = {q: W.TARGET_TO_GUIDE_DATE[q] for q in qs}
    act = {r.quarter: r.revenue_musd for r in t.itertuples()}
    rows = []
    for name, offset in (("naive", 0.0), ("half", 0.0)):
        for q in qs:
            a = float(act[q])
            pt = a + (100.0 if name == "naive" else 50.0)
            rows.append(dict(method="baselines" if name == "naive" else "toy",
                             object=name, target="revenue_musd", quarter=q,
                             vintage_date=gd[q], horizon_q=1, point=pt, q50=pt,
                             q10=pt - 200, q90=pt + 200,
                             window="W2", prior_basis="PIT", n_params=1, n_train=10))
    return pd.DataFrame(rows)


def test_scorer_reproduces_known_mae_rmse_bias_and_naive_ratio():
    sb = score_registry(_toy_registry())
    naive = sb[(sb["object"] == "naive")].iloc[0]
    half = sb[(sb["object"] == "half")].iloc[0]
    assert naive["mae"] == pytest.approx(100.0)
    assert naive["rmse"] == pytest.approx(100.0)
    assert naive["bias"] == pytest.approx(100.0)
    assert naive["rmse_ratio_to_naive"] == pytest.approx(1.0)
    assert half["mae"] == pytest.approx(50.0)
    assert half["rmse_ratio_to_naive"] == pytest.approx(0.5)
    assert bool(half["beats_naive"])
    # every actual sits inside +/-200 of a forecast that is off by 50 or 100
    assert half["cov_empirical"] == pytest.approx(1.0)
    assert naive["cov_nominal"] == pytest.approx(0.80)
    assert naive["cov_interval"] == "q10-q90"
    assert M.EXCHANGEABILITY_CAVEAT in naive["coverage_caveat"]
    assert naive["param_obs_ratio"] == pytest.approx(1.0 / naive["n"])


def test_scorer_excludes_live_rows():
    d = _toy_registry()
    live = d.iloc[[0]].copy()
    live["quarter"] = "2026Q3"; live["window"] = "LIVE"
    live["vintage_date"] = W.GUIDE_DATE_LIVE
    sb = score_registry(pd.concat([d, live], ignore_index=True))
    assert (sb["window"] != "LIVE").all()


def test_scorer_handles_missing_quantiles_gracefully():
    d = _toy_registry().drop(columns=["q10", "q90"])
    sb = score_registry(d)
    assert len(sb) == 2
    assert sb["crps"].notna().all()          # degenerates to MAE
    assert sb["cov_empirical"].isna().all()  # no interval to score


def test_survives_both_windows_requires_both():
    d = _toy_registry()          # W2 only
    sb = score_registry(d)
    assert not sb["survives_both_windows"].any()
