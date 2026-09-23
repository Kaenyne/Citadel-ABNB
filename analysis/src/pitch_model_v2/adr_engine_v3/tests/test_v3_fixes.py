"""Tests for the audit's corrections in adr_engine_v3 (docs/pitch-model-v2/lines/adr_v3_corrections.md).
Run after the engine: PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests -q"""
import numpy as np
import pandas as pd

from pitch_model_v2.adr_engine_v3 import config as C


# ---- fix (a): the registered V1 variant beside V0 --------------------------------------------------------------------
def test_v0_stays_the_leg_and_v1_is_carried_beside_it():
    s = pd.read_json(C.OUT / "00_summary.json", typ="series")
    assert s["promotion"]["promoted_leg"] == "V0_translation"
    p = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    assert {"fx_pp_v1", "adr_usd_fx_v1", "p_print_ge_street_fx_v1"} <= set(p.columns)
    assert np.isfinite(p.loc[["3Q26", "4Q26"], "adr_usd_fx_v1"]).all()


def test_v1_fits_latam_below_one_and_emea_above():
    b = pd.read_csv(C.OUT / "fx_v1_map_beta_all17.csv").iloc[0]
    assert b["latam"] < 0.6 and b["emea"] > 1.1


def test_v1_puts_3q26_fx_below_the_identity():
    p = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    assert p.loc["3Q26", "fx_pp_v1"] < p.loc["3Q26", "fx_pp"] - 0.2


def test_v0_error_rises_with_its_latam_component_in_every_promotion_cell():
    d = pd.read_csv(C.OUT / "fx_v0_error_on_latam.csv")
    assert len(d) == 4 and (d.slope > 0.4).all() and (d.p_slope < 0.05).all()


# ---- fix (b): the re-specified FX falsifier ----------------------------------------------------------------------------
def test_amended_falsifier_rarely_withdraws_a_correct_identity():
    from pitch_model_v2.adr_engine_v3 import fx_falsifier as FF
    assert FF.false_withdrawal_rate(true_fx=0.415, n=4000) < 0.05


def test_amended_falsifier_can_withdraw_the_identity_when_the_euro_fit_is_right():
    from pitch_model_v2.adr_engine_v3 import fx_falsifier as FF
    assert FF.false_withdrawal_rate(true_fx=-1.12, n=4000) > 0.8


def test_old_band_falsifier_failed_a_correct_identity_most_of_the_time():
    rng = np.random.default_rng(7); ex = rng.uniform(2, 5, 20000)
    printed = (ex + 0.415) - np.round(ex)
    assert np.mean((printed >= 0.355) & (printed <= 0.481)) < 0.2


# ---- fix (c): forward terms on the carried core's construction -------------------------------------------------------
def test_construction_offsets_match_the_audit():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    off = X.construction_offsets()
    assert abs(off["geo_off"] - 0.132) < 0.005 and abs(off["unit_off"] - 0.166) < 0.005 and abs(off["los_in_core"] - 0.30) < 1e-9


def test_case_a_lowers_the_base_by_about_five_hundredths_and_case_b_bounds_it():
    d = pd.read_csv(C.OUT / "exfx_construction_cases.csv", index_col=0)
    assert np.allclose(d.d_case_A_pp, d.d_case_A_pp.iloc[0]) and -0.07 < d.d_case_A_pp.iloc[0] < -0.04
    assert -0.32 < d.loc["4Q26", "d_case_B_pp"] < -0.28


def test_switch_off_reproduces_v2():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    X.CONSTRUCTION_FIX = False
    try:
        assert abs(X.forward().loc["4Q26", "exfx_yoy"] - 2.784074164) < 1e-6
    finally:
        X.CONSTRUCTION_FIX = True


# ---- fix (d): the downside rows on the core's own statistics ---------------------------------------------------------
def test_mean_reversion_uses_the_cores_own_mean():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    assert abs(X.core_mean_2023_25() - 2.272) < 0.001


def test_ar1_is_fitted_on_the_core():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    const, rho = X.core_ar1()
    assert abs(rho - 0.465) < 0.005 and abs(const / (1 - rho) - 2.411) < 0.01


def test_downside_rows_moved_down_and_ar1_now_below_the_street():
    s = pd.read_csv(C.OUT / "adr_scenarios.csv")
    q = s[s.quarter == "4Q26"].set_index("rule").adr_usd
    assert q["core mean reversion to the 2023-25 mean"] < 170.45
    assert q["AR(1) fitted on core"] < C.STREET_ADR["4Q26"][0]


# ---- fix (e): the sub-regional scenario adds the change from 2Q26 ----------------------------------------------------
def test_subregional_row_adds_only_the_change_from_2q26():
    s = pd.read_csv(C.OUT / "adr_scenarios.csv")
    q = s[s.quarter == "4Q26"].set_index("rule")
    base = q.loc["base: core carry + bundle laps (nights-linked geo)", "exfx_pct"]
    sub = q.loc["base + sub-regional country mix (v2 H3, Inside Airbnb panel)", "exfx_pct"]
    term = pd.read_csv(C.OUT / "geomix_subregional_term.csv").set_index("quarter").subgeo_pp
    fwd = pd.read_csv(C.OUT / "geomix_subregional_term_forward.csv").set_index("quarter").subgeo_pp
    assert abs((sub - base) - (fwd["4Q26"] - term["2Q26"])) < 1e-9 and -0.06 < sub - base < -0.03


# ---- fix (f): bundle band from management's rounding -----------------------------------------------------------------
def test_bundle_band_is_half_a_point_either_side_in_4q26():
    e = pd.read_csv(C.OUT / "exfx_envelope.csv", index_col=0)
    bundle_half = float(e.loc["4Q26", "halfwidths"].split("=")[1].split("|")[1])
    assert abs(bundle_half - 0.5) < 1e-6
