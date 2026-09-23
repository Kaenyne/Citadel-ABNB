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
