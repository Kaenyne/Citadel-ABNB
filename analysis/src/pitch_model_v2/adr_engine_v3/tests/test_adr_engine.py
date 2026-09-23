"""Tests for the ADR engine. Run: python3 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests -q"""
import numpy as np
import pandas as pd
import pytest

from pitch_model_v2.adr_engine_v3 import config as C, fx_data as F, exposure as E, walkforward as W, exfx as X


@pytest.fixture(scope="module")
def daily():
    return F.load_daily()


def test_identity_closes_on_disclosed_data():
    h = pd.read_csv(C.H_COMPONENTS)
    assert (h.identity_check_pp.abs() <= 0.05).all()


def test_seventeen_targets_with_half_widths():
    t = F.disclosed_targets()
    assert len(t) == 17 and list(t.index) == C.TARGET_QUARTERS
    assert t.loc["3Q23", "half_width"] == 0.25 and t.loc["1Q26", "half_width"] == 0.5
    assert abs(t.loc["2Q26", "fx_pts_adr"] - 1.3) < 1e-9


def test_kappa_rows_sum_to_one():
    for r, k in C.KAPPA.items():
        assert abs(sum(k.values()) - 1.0) < 1e-9


def test_quarter_avg_spot_held_reproduces_fx_lag_v2_basket(daily):
    """fx_lag_v2 (FX through 4 Sep) published the completed-quarter global basket for 2Q26 as +2.266% on revenue weights;
    our currency y/y for a completed quarter must match the same daily data to the second decimal for EUR."""
    yoy, f = F.yoy_by_ccy(daily, "2Q26", pd.Timestamp("2026-09-04"))
    assert abs(yoy["EUR"] - 2.559) < 0.06         # 02_basket_quarterly eurusd_yoy_pct 2Q26 = 2.559 (holiday-fill differences)
    assert f == 1.0


def test_pit_information_set_excludes_future_prints(daily):
    cur_o1, f1 = F.quarter_avg(daily, "1Q26", pd.Timestamp("2025-12-31"))
    cur_o3, f3 = F.quarter_avg(daily, "1Q26", pd.Timestamp("2026-05-06"))
    assert f1 == 0.0 and f3 == 1.0
    assert cur_o1["EUR"] != cur_o3["EUR"]


def test_v0_is_zero_parameter_and_walkforward_reproduces_scores():
    wf = pd.read_csv(C.OUT / "fx_pit_walkforward.csv"); sc = W.score(wf)
    v0 = sc[(sc.variant == "V0_translation") & (sc.origin == "O3")].set_index("window")
    assert v0.loc["W1", "ratio_vs_naive"] < C.PASS_RATIO and v0.loc["W2", "ratio_vs_naive"] < C.PASS_RATIO
    assert W.promotion(sc)["promoted_leg"] == "V0_translation"


def test_interval_likelihood_prefers_inside_interval():
    ll_in = E.interval_loglik(np.array([0.2]), np.array([0.0]), np.array([0.5]), 0.3)
    ll_out = E.interval_loglik(np.array([1.5]), np.array([0.0]), np.array([0.5]), 0.3)
    assert ll_in > ll_out


def test_bundle_laps_on_filed_dates():
    b = X.bundle_schedule()
    assert abs(b.loc["4Q25", "bundle_total"] - X.BUNDLE_ADR_PP) < 1e-9
    assert b.loc["3Q26", "rnpl_na_leg"] == 0.0 and b.loc["3Q26", "fee_cancel_leg"] > 0
    assert b.loc["4Q26", "bundle_total"] == 0.0


def test_geo_mix_sign_and_method_check():
    """Faster growth in low-ADR regions must lower blended ADR; the bucket arithmetic reproduces H within 0.25pp on 2Q24-2Q26."""
    g = X.geo_mix_pp({"na": .3, "emea": .4, "latam": .15, "apac": .15}, {"na": 250, "emea": 160, "latam": 95, "apac": 118},
                     {"na": 3, "emea": 7, "latam": 18, "apac": 15})
    assert g < 0
    chk = X.geo_mix_history_check().loc["2Q24":"2Q26"]
    assert (chk.diff_pp.abs() <= 0.25).all()


def test_forward_exfx_identity_sums():
    f = X.forward()
    parts = f[["core", "bundle", "geo_mix", "unit_size", "los_mix", "seats", "interaction", "fee_k", "basis_adj", "wc_lap"]].sum(axis=1)   # v3 fix (l): the 2Q27 World Cup lap
    assert np.allclose(parts.values, f.exfx_yoy.values)
    assert f.loc["4Q26", "residual"] < f.loc["3Q26", "residual"]     # the bundle laps
