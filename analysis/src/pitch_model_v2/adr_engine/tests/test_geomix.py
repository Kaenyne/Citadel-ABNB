"""Tests for the sub-regional (country-level) geographic-mix term — adr_v2_geomix_prereg.md, upgrade 6.

    PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/adr_engine/tests -q

Four groups: the mix arithmetic (sign, the zero it must return when nothing moves, invariance to the price unit),
the country aggregation's three-month rule, the market -> currency map, and a reproduction test that build_term on
the saved inputs still returns the saved term.
"""
import numpy as np
import pandas as pd
import pytest

from pitch_model_v2.adr_engine import config as C, geomix as GX, refresh_prices as RP, run as R


# ---------------------------------------------------------------------------------------------------------------- #
# helpers
# ---------------------------------------------------------------------------------------------------------------- #
def _growth(rows, quarter="1Q26", region="EMEA"):
    """rows: (country, base stays, y/y in per cent)."""
    return pd.DataFrame([{"country": c, "region": region, "quarter": quarter, "n_prior": float(n),
                          "stays_yoy_pct": float(g)} for c, n, g in rows])


def _prices(rows, region="EMEA"):
    return pd.DataFrame([{"country": c, "region": region, "usd_level": float(p), "n_markets_priced": 1.0}
                         for c, p in rows])


# ---------------------------------------------------------------------------------------------------------------- #
# 1. the mix arithmetic
# ---------------------------------------------------------------------------------------------------------------- #
def test_mix_is_negative_when_growth_tilts_to_the_cheaper_country():
    """The whole point of the term: inside a region, faster growth in a cheap country lowers the blended ADR."""
    g = _growth([("cheapland", 100, 20.0), ("dearland", 100, 0.0)])
    p = _prices([("cheapland", 80.0), ("dearland", 240.0)])
    mix, _ = GX.build_term(g, p)
    assert len(mix) == 1 and mix.mix_pp.iloc[0] < 0
    # and the sign flips when the dear country is the one growing
    g2 = _growth([("cheapland", 100, 0.0), ("dearland", 100, 20.0)])
    mix2, _ = GX.build_term(g2, p)
    assert mix2.mix_pp.iloc[0] > 0
    assert mix.mix_pp.iloc[0] == pytest.approx(-mix2.mix_pp.iloc[0], rel=0.15)


def test_mix_is_zero_when_every_country_grows_equally():
    """No reallocation of shares -> no mix effect, whatever the price dispersion or the common growth rate."""
    p = _prices([("a", 50.0), ("b", 175.0), ("c", 400.0)])
    for common in (-8.0, 0.0, 12.5):
        g = _growth([("a", 130, common), ("b", 70, common), ("c", 55, common)])
        mix, contrib = GX.build_term(g, p)
        assert mix.mix_pp.iloc[0] == pytest.approx(0.0, abs=1e-12)
        assert mix.region_growth_pct.iloc[0] == pytest.approx(common, abs=1e-12)
        assert contrib.contrib_pp.abs().max() == pytest.approx(0.0, abs=1e-12)


def test_mix_is_invariant_to_the_price_unit():
    """Price levels are a relative-level proxy (prereg §1), so the term must not move when the unit does."""
    g = _growth([("a", 90, 14.0), ("b", 60, -3.0), ("c", 30, 6.0)])
    base = [("a", 60.0), ("b", 210.0), ("c", 330.0)]
    ref = GX.build_term(g, _prices(base))[0].mix_pp.iloc[0]
    for k in (0.01, 7.3, 1000.0):
        scaled = GX.build_term(g, _prices([(c, p * k) for c, p in base]))[0].mix_pp.iloc[0]
        assert scaled == pytest.approx(ref, rel=1e-12, abs=1e-12)


def test_contributions_sum_to_the_region_mix():
    """contrib_pp = (s_new - s_base) * relative price: the country rows must add up to mix_pp."""
    g = _growth([("a", 90, 14.0), ("b", 60, -3.0), ("c", 30, 6.0)])
    mix, contrib = GX.build_term(g, _prices([("a", 60.0), ("b", 210.0), ("c", 330.0)]))
    assert contrib.contrib_pp.sum() == pytest.approx(mix.mix_pp.iloc[0], abs=1e-9)


def test_unpriced_country_is_imputed_at_the_region_median_and_contributes_nothing():
    """Stated imputation (prereg §1): a country with no price level takes the region median, so it cannot tilt."""
    g = _growth([("a", 100, 30.0), ("b", 100, 0.0), ("nopricehere", 100, 50.0)])
    mix, _ = GX.build_term(g, _prices([("a", 100.0), ("b", 300.0)]))
    assert mix.n_imputed.iloc[0] == 1
    assert mix.share_imputed.iloc[0] == pytest.approx(1 / 3, abs=1e-12)


def test_subregional_term_is_the_gbv_weighted_sum_of_the_region_mixes():
    mix = pd.read_csv(C.OUT / "geomix_within_region.csv")
    term = GX.subregional_term(mix).set_index("quarter")
    parts = [f"part_{r}" for r in GX.REGION_KEY]
    assert np.allclose(term[parts].sum(axis=1).values, term.subgeo_pp.values, atol=1e-12)


# ---------------------------------------------------------------------------------------------------------------- #
# 2. the country aggregation — the three-month rule
# ---------------------------------------------------------------------------------------------------------------- #
def _e_rows(rows):
    """rows: (market_key, country, ym, n_vm_cur, n_vm_prior) -> a frame shaped like q3nowcast/E/market_monthly_yoy."""
    return pd.DataFrame([{"market_key": m, "country": c, "region": "EMEA", "ym": ym,
                          "n_vm_cur": cur, "n_vm_prior": pri} for m, c, ym, cur, pri in rows])


def test_country_aggregation_requires_all_three_months_of_a_quarter(tmp_path):
    """A market with only two of the quarter's months is dropped from that quarter entirely — it does not get to
    contribute two thirds of a quarter to its country's stays."""
    f = tmp_path / "e.csv"
    _e_rows([("full_a", "atlantis", "2026-01", 110, 100), ("full_a", "atlantis", "2026-02", 110, 100),
             ("full_a", "atlantis", "2026-03", 110, 100),
             ("part_b", "atlantis", "2026-01", 900, 100), ("part_b", "atlantis", "2026-02", 900, 100)]).to_csv(f, index=False)
    out = RP.country_stays(f)
    assert len(out) == 1
    r = out.iloc[0]
    assert r.quarter == "1Q26" and r.n_mkts == 1
    assert r.n_cur == 330 and r.n_prior == 300                 # the two-month market contributed nothing
    assert r.stays_yoy_pct == pytest.approx(10.0)


def test_country_aggregation_sums_markets_and_every_vintage_pair(tmp_path):
    """Two complete markets add; a second vintage pair for the same months multiplies both legs, so the y/y is
    unchanged (this is why the raw counts in the file are a multiple of a single vintage's counts)."""
    f = tmp_path / "e.csv"
    base = [("m1", "atlantis", ym, 120, 100) for ym in ("2026-01", "2026-02", "2026-03")]
    base += [("m2", "atlantis", ym, 200, 100) for ym in ("2026-01", "2026-02", "2026-03")]
    _e_rows(base).to_csv(f, index=False)
    one = RP.country_stays(f).iloc[0]
    _e_rows(base + base).to_csv(f, index=False)
    two = RP.country_stays(f).iloc[0]
    assert one.n_mkts == 2 and two.n_mkts == 2
    assert two.n_cur == 2 * one.n_cur and two.n_prior == 2 * one.n_prior
    assert two.stays_yoy_pct == pytest.approx(one.stays_yoy_pct) == pytest.approx(60.0)


def test_saved_country_panel_has_no_partial_quarters_except_the_qtd_tail():
    """The panel on disk: 34 countries in every complete quarter, and only the quarter-to-date tail is thin."""
    cg = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv")
    n = cg.groupby("quarter").country.nunique()
    last_full = R.last_full_quarter(cg)
    assert last_full == "2Q26"
    assert n[last_full] == n.max() == 34
    assert (cg.n_prior > 0).all() and cg.stays_yoy_pct.notna().all()


# ---------------------------------------------------------------------------------------------------------------- #
# 3. the market -> currency map
# ---------------------------------------------------------------------------------------------------------------- #
def test_every_panel_market_is_mapped_to_a_currency():
    cm = RP.currency_map()
    saved = pd.read_csv(C.OUT / "market_currency_map.csv")
    assert len(cm) == len(saved) == 123
    assert cm.currency.notna().all() and (cm.currency.str.len() == 3).all()
    assert set(cm.market_key) == set(saved.market_key)
    assert cm.market_key.is_unique


def test_hong_kong_prices_in_hkd_and_the_us_in_usd():
    cm = RP.currency_map().set_index("market_key")
    assert cm.loc[RP.HONG_KONG_MARKET, "currency"] == "HKD"          # the `china` folder is the Hong Kong market
    assert cm.loc[RP.HONG_KONG_MARKET, "region"] == "APAC"
    assert (cm[cm.country == "united-states"].currency == "USD").all()
    assert (cm[cm.country == "the-netherlands"].currency == "EUR").all()


def test_fx_available_flags_exactly_the_fred_currencies():
    cm = RP.currency_map()
    fred = RP.fred_currencies()
    assert (cm.fx_available == cm.currency.isin(fred)).all()
    # the five FRED cannot carry, and which therefore either come from the ECB/peg file or are imputed
    assert set(cm.loc[~cm.fx_available, "currency"]) == {"ARS", "CLP", "COP", "KES", "CZK", "HUF", "TRY", "BZD"}


def test_country_price_levels_are_n_listed_weighted_with_a_floor():
    mp = pd.read_csv(C.OUT / "market_price_levels_capture_2026.csv")
    cp = RP.country_prices(mp).set_index("country")
    us = mp[(mp.country == "united-states") & mp.median_listed_usd.notna()]
    assert cp.loc["united-states", "usd_level"] == pytest.approx(
        float(np.average(us.median_listed_usd, weights=us.n_listed)))
    assert cp.loc["united-states", "n_markets_priced"] == len(us)
    assert "switzerland" not in cp.index                   # the Swiss dumps carry 0.16-0.18 CHF a night
    assert (cp.usd_level >= RP.MIN_USD_LEVEL).all()


# ---------------------------------------------------------------------------------------------------------------- #
# 4. reproduction
# ---------------------------------------------------------------------------------------------------------------- #
def test_build_term_on_the_saved_inputs_reproduces_the_saved_term():
    """The pre-registered term, rebuilt from the two saved inputs, must match the filed outputs to 1e-6."""
    cg = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv")
    cp = pd.read_csv(C.OUT / "country_price_levels_usd.csv")
    mix, contrib = GX.build_term(cg, cp)
    saved_mix = pd.read_csv(C.OUT / "geomix_within_region.csv")
    m = saved_mix.merge(mix, on=["region", "quarter"], how="outer", suffixes=("_s", "_n"), indicator=True)
    assert (m._merge == "both").all()
    assert (m.mix_pp_s - m.mix_pp_n).abs().max() < 1e-6

    term = GX.subregional_term(mix)
    saved = pd.read_csv(C.OUT / "geomix_subregional_term.csv")
    t = saved.merge(term, on="quarter", how="outer", suffixes=("_s", "_n"), indicator=True)
    assert (t._merge == "both").all()
    for col in ["subgeo_pp"] + [f"part_{r}" for r in GX.REGION_KEY]:
        assert (t[col + "_s"] - t[col + "_n"]).abs().max() < 1e-6


def test_forward_term_reproduces_the_filed_h3_scenario():
    from pitch_model_v2.adr_engine import exfx as M
    cg = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv")
    cp = pd.read_csv(C.OUT / "country_price_levels_usd.csv")
    mixf = R.subregional_forward(cg, cp, M.regional_growth_forward())
    termf = GX.subregional_term(mixf).set_index("quarter")
    saved = pd.read_csv(C.OUT / "geomix_subregional_term_forward.csv").set_index("quarter")
    assert list(termf.index) == list(saved.index) == C.FORWARD_QUARTERS
    assert (termf.subgeo_pp - saved.subgeo_pp).abs().max() < 1e-6
    assert termf.subgeo_pp.max() < 0                     # H3: the carried differential is a drag in every quarter


def test_tilt_table_reproduces_and_orders_the_patterns():
    tilt = R.tilt_table()
    saved = pd.read_csv(C.OUT / "geo_mix_tilt_sensitivity.csv")
    m = saved.merge(tilt, on=["quarter", "pattern"], how="outer", suffixes=("_s", "_n"), indicator=True)
    assert (m._merge == "both").all() and len(m) == 16
    assert (m.geo_mix_pp_s - m.geo_mix_pp_n).abs().max() < 1e-6
    # a bigger tilt into LatAm/APAC is a bigger ADR drag; Europe leading is a smaller one
    for q, x in tilt.set_index("pattern").groupby("quarter"):
        b = float(x.loc[[p for p in x.index if p.startswith("base")][0], "geo_mix_pp"])
        tb = float(x.loc[[p for p in x.index if p.startswith("tilt B")][0], "geo_mix_pp"])
        tc = float(x.loc[[p for p in x.index if p.startswith("tilt C")][0], "geo_mix_pp"])
        assert tb < b < tc, q


def test_exfx_pattern_is_restored_after_the_tilt_table():
    from pitch_model_v2.adr_engine import exfx as M
    before = dict(M.EXNA_PATTERN)
    R.tilt_table()
    assert M.EXNA_PATTERN == before
