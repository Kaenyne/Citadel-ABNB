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
    assert p.loc["3Q26", "fx_pp_v1"] < p.loc["3Q26", "fx_pp_identity"] - 0.2      # fx_pp is the adopted leg since fix (j)


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
    X.CONSTRUCTION_FIX = X.LOS_NOWCAST = X.WC_CORE_ADJ = X.CORE_HORIZON_RULE = False
    try:
        assert abs(X.forward().loc["4Q26", "exfx_yoy"] - 2.784074164) < 1e-6
    finally:
        X.CONSTRUCTION_FIX = X.LOS_NOWCAST = X.WC_CORE_ADJ = X.CORE_HORIZON_RULE = True


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


# ---- fix (h): labels travel with the numbers -------------------------------------------------------------------------
def test_4q27_and_fy27_carry_the_artefact_label():
    p = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    assert "artefact" in p.loc["4Q27", "note"] and "artefact" in p.loc["FY27", "note"]
    assert p.loc["3Q26", "band_basis"].startswith("+/-1 sd")


# ---- fix (j): the card-method midpoint as the FX leg ------------------------------------------------------------------
def test_midpoint_beats_identity_and_euro_fit_in_every_promotion_cell():
    sc = pd.read_csv(C.OUT / "fx_scores.csv")
    cell = sc[sc.origin.isin(["O2", "O3"])].pivot_table(index=["window", "origin"], columns="variant", values="ratio_vs_naive")
    assert (cell.M_card_midpoint < cell.V0_translation).all() and (cell.M_card_midpoint < cell.V2_eur_ols).all()


def test_path_uses_the_midpoint_leg_and_keeps_the_identity_beside_it():
    from pitch_model_v2.adr_engine_v3 import assemble as A, exfx as X
    p = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    assert (p.loc[["3Q26", "4Q26"], "fx_leg"] == "midpoint").all()
    assert p.loc["3Q26", "adr_usd"] < p.loc["3Q26", "adr_usd_fx_v1"] < p.loc["3Q26", "adr_usd_fx_identity"]
    X.LOS_NOWCAST = X.WC_CORE_ADJ = False                        # fix (j)'s numbers, before fixes (k) and (l)
    try:
        q = A.build()
        assert abs(q.loc["3Q26", "adr_usd_fx_identity"] - 177.588) < 0.01 and abs(q.loc["4Q26", "adr_usd_fx_identity"] - 172.943) < 0.01
    finally:
        X.LOS_NOWCAST = X.WC_CORE_ADJ = True


def test_identity_switch_reproduces_the_previous_leg():
    from pitch_model_v2.adr_engine_v3 import assemble as A, exfx as X
    C.FX_LEG = "identity"; X.LOS_NOWCAST = X.WC_CORE_ADJ = False
    try:
        p = A.build()
        assert abs(p.loc["3Q26", "adr_usd"] - 177.588) < 0.01 and abs(p.loc["4Q26", "adr_usd"] - 172.943) < 0.01
    finally:
        C.FX_LEG = "midpoint"; X.LOS_NOWCAST = X.WC_CORE_ADJ = True


def test_falsifier_rarely_withdraws_a_correct_midpoint_leg():
    from pitch_model_v2.adr_engine_v3 import fx_falsifier as FF
    kw = dict(n=4000, candidates=FF.CANDIDATES_3Q26_J, leg="midpoint_refreshed", rule="withdraw_leg_ratio3")
    assert FF.false_withdrawal_rate(-0.406, **kw) < 0.10          # a correct midpoint is rarely withdrawn
    assert FF.false_withdrawal_rate(0.415, **kw) > 0.30           # and the rule has teeth if the identity is right


def test_midpoint_is_confined_to_the_tested_horizon():
    p = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    assert (p.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "fx_leg"] == "identity").all()
    assert (p.loc[["1Q27", "2Q27"], "fx_pp"] == p.loc[["1Q27", "2Q27"], "fx_pp_identity"]).all()


# ---- fix (k): LOS measured (2Q26 fill + measured 2Q26 -> 3Q26 change), 4Q26 carries the 3Q26 read ------------------------
def test_los_nowcast_enters_3q26_and_4q26_only():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    n = pd.read_csv(X.LOS_NOWCAST_FILE).set_index("quarter")
    f = pd.read_csv(C.OUT / "exfx_forward_base.csv", index_col=0)
    assert abs(f.loc["3Q26", "los_mix"] - n.loc["3Q26", "los_forward_pp"]) < 1e-9
    assert abs(f.loc["4Q26", "los_mix"] - f.loc["3Q26", "los_mix"]) < 1e-9
    X.CORE_HORIZON_RULE = False                                  # before fix (m), 2027 kept the in-core fill
    try:
        assert (X.forward().loc[["1Q27", "2Q27", "3Q27", "4Q27"], "los_mix"] == 0.30).all()
    finally:
        X.CORE_HORIZON_RULE = True
    assert abs(n.loc["3Q26", "los_forward_pp"] - (0.30 + n.loc["3Q26", "delta_pp"])) < 1e-9


def test_los_band_is_the_nowcasts_own():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    n = pd.read_csv(X.LOS_NOWCAST_FILE).set_index("quarter")
    e = pd.read_csv(C.OUT / "exfx_envelope.csv", index_col=0)
    los_half = float(e.loc["3Q26", "halfwidths"].split("=")[1].split("|")[5])
    assert abs(los_half - (n.loc["3Q26", "band_hi_pp"] - n.loc["3Q26", "band_lo_pp"]) / 2) < 1e-3


# ---- fix (l): the World Cup premium out of the carried core --------------------------------------------------------------
def test_world_cup_premium_is_removed_from_the_carry_and_lapped_in_2q27():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    f = pd.read_csv(C.OUT / "exfx_forward_base.csv", index_col=0); h = X.history()
    assert np.allclose(f.loc[["3Q26", "4Q26"], "core"], float(h.core.iloc[-1]) - X.WC_CORE_PP)
    assert f.loc["2Q27", "wc_lap"] == -X.WC_CORE_PP and (f.drop(index="2Q27").wc_lap == 0).all()


def test_ladder_starts_at_fix_j_and_each_step_is_recorded():
    d = pd.read_csv(C.OUT / "los_wc_ladder.csv")
    assert len(d) == 4
    assert abs(d.adr_identity_3Q26.iloc[0] - 177.588) < 0.01 and abs(d.adr_identity_4Q26.iloc[0] - 172.943) < 0.01
    p = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    assert abs(d.adr_4Q26.iloc[-1] - p.loc["4Q26", "adr_usd"]) < 1e-9


# ---- fix (m): the 2027 core rule -----------------------------------------------------------------------------------------
def test_core_horizon_reproduces_the_audits_h1_to_h4_scores():
    s = pd.read_csv(C.OUT / "core_horizon_scores.csv")
    a = pd.read_csv(C.ROOT / "data/processed/pitch_model_v2/receipts/ADR_AUDIT/C1_core_pit_scores.csv")
    m = s.merge(a, on=["h", "window"], suffixes=("", "_audit"))
    assert len(m) == 8 and np.allclose(m.mean_vs_carry, m.mean_vs_carry_audit) and (m.n == m.n_audit).all()


def test_rule_is_carry_to_h2_and_mean_where_it_wins_after():
    r = pd.read_csv(C.OUT / "core_horizon_rule.csv", index_col=0)
    s = pd.read_csv(C.OUT / "core_horizon_scores.csv")
    assert (r.loc[["3Q26", "4Q26"], "core_rule"] == "carry").all() and (r.loc[["1Q27", "2Q27"], "core_rule"] == "mean").all()
    for q, h in (("3Q27", 5), ("4Q27", 6)):                     # read from the registered test, never typed in
        wins = bool((s[s.h == h].mean_vs_carry < 1).all())
        assert r.loc[q, "core_rule"] == ("mean" if wins else "carry")


def test_2027_core_is_the_expanding_mean_net_of_the_world_cup_and_los_its_own_mean():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    f = pd.read_csv(C.OUT / "exfx_forward_base.csv", index_col=0); r = pd.read_csv(C.OUT / "core_horizon_rule.csv", index_col=0)
    cv = X.history().core.to_numpy(dtype=float).copy(); cv[-1] -= X.WC_CORE_PP
    n = pd.read_csv(X.LOS_NOWCAST_FILE).set_index("quarter")
    los_mean = np.mean(list(X.history().los_mix) + [n.loc["3Q26", "los_forward_pp"]])
    for q in [q for q in r.index if r.loc[q, "core_rule"] == "mean"]:
        assert abs(f.loc[q, "core"] - cv.mean()) < 1e-9 and abs(f.loc[q, "los_mix"] - los_mean) < 1e-9
    assert 2.40 < cv.mean() < 2.50


def test_switching_m_off_restores_the_carry_in_2027():
    from pitch_model_v2.adr_engine_v3 import exfx as X
    X.CORE_HORIZON_RULE = False
    try:
        f = X.forward()
        assert np.allclose(f.core, float(X.history().core.iloc[-1]) - X.WC_CORE_PP)
    finally:
        X.CORE_HORIZON_RULE = True
