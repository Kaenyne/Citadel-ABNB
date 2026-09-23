"""adr_engine_v3 / run.py — the ADR line with the audit's corrections, rebuilt end to end (exit 0). Copy of adr_engine;
outputs go to data/processed/pitch_model_v2/adr_engine_v3/ and figures to docs/pitch-model-v2/lines/figures/v3/; the frozen
inputs are seeded read-only from adr_engine's outputs; the workbook stage is disabled (model/ is protected).
Original docstring follows.
adr_engine / run.py — rebuild the ADR line v1 end to end (exit 0). Offline once fx_daily_2026-09-21.csv exists;
`--fetch` refreshes FRED first (writes a new dated file; config.FX_DAILY must then be pointed at it).

    PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run [--fetch] [--no-posterior] [--no-workbook]
                                                                    [--no-refresh-prices]

Stages: FX walk-forward -> FX forecast (-> posterior) -> ex-FX mechanism -> **geomix** (the sub-regional country-mix
term of adr_v2_geomix_prereg.md, whose inputs refresh_prices.py rebuilds from the raw stores) -> ex-FX alternatives
(their composition scenarios read the geomix files) -> assembly -> figures -> workbook.
"""
from __future__ import annotations
import argparse, json, shutil, time, warnings
import numpy as np
import pandas as pd
from . import config as C, fx_data as F, walkforward as W, forecast as X, exfx as M, assemble as A, figures as G
from . import exposure as E
from . import geomix as GX

# ---- the geo-mix layer's frozen rules (adr_v2_geomix_prereg.md §2 H3; the four-region tilt of adr_v1_design.md) ----
TILT_PATTERNS = {
    "base pattern EMEA 8 / LatAm 20 / APAC 18": {"emea": 8.0, "latam": 20.0, "apac": 18.0},
    "tilt A: EMEA 6 / LatAm 25 / APAC 22": {"emea": 6.0, "latam": 25.0, "apac": 22.0},
    "tilt B: EMEA 5 / LatAm 30 / APAC 25 (India +60, Brazil +31 origin)": {"emea": 5.0, "latam": 30.0, "apac": 25.0},
    "tilt C: EMEA 10 / LatAm 15 / APAC 14 (Europe leads)": {"emea": 10.0, "latam": 15.0, "apac": 14.0},
}
TILT_QUARTERS = ["3Q26", "4Q26", "1Q27", "2Q27"]         # the quarters whose base-quarter regional shares are observed
H2_WINDOWS = {"W1": ["1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
              "W2": ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]}
DIFF_WINDOW_QUARTERS = 4                                 # H3: the growth differential averaged over 2H25-1H26


# ---------------------------------------------------------------------------------------------------------------- #
# the geomix stage
# ---------------------------------------------------------------------------------------------------------------- #
def last_full_quarter(cg: pd.DataFrame) -> str:
    """The most recent quarter whose country panel is complete (the QTD quarter carries only a handful of markets)."""
    n = cg.groupby("quarter").country.nunique()
    return [q for q in sorted(n.index, key=C.qlabel_to_period) if n[q] == n.max()][-1]


def growth_differentials(cg: pd.DataFrame, quarters: list[str]) -> pd.Series:
    """H3's carry rule: each country's mean stays-growth differential to its region over the stated window, in pp.
    The region rate is the panel's own share-weighted rate, identical to sum(n_cur)/sum(n_prior) - 1."""
    rows = []
    for q in quarters:
        for reg, y in cg[cg.quarter == q].groupby("region"):
            g_reg = (y.n_cur.sum() / y.n_prior.sum() - 1.0) * 100.0
            rows += [{"region": reg, "country": c, "d": g - g_reg} for c, g in zip(y.country, y.stays_yoy_pct)]
    return pd.DataFrame(rows).groupby(["region", "country"]).d.mean()


def subregional_forward(cg: pd.DataFrame, cp: pd.DataFrame, rg: pd.DataFrame) -> pd.DataFrame:
    """H3 forward within-region mix, 3Q26-4Q27: every country grows at its region's modelled rate (the nights line's
    regional path, regional_growth_forward.csv) plus its frozen 2H25-1H26 differential; base shares start at the last
    full panel quarter's stays and are rolled by the modelled growth. Same mix arithmetic as geomix.build_term."""
    last = last_full_quarter(cg)
    order = sorted(cg.quarter.unique(), key=C.qlabel_to_period)
    i = order.index(last)
    d = growth_differentials(cg, order[i - DIFF_WINDOW_QUARTERS + 1: i + 1])
    price = cp.set_index("country").usd_level
    reg_med = cp.groupby("region").usd_level.median()
    share = {}
    for reg, y in cg[cg.quarter == last].groupby("region"):
        share.update({(reg, c): float(v) for c, v in zip(y.country, y.n_cur / y.n_cur.sum())})
    rows = []
    for q in C.FORWARD_QUARTERS:
        for reg in sorted(GX.REGION_KEY):
            cs = sorted(c for (r, c) in share if r == reg)
            if not cs:
                continue
            g_mod = float(rg.loc[q, f"g_{GX.REGION_KEY[reg]}"])
            s0 = np.array([share[(reg, c)] for c in cs])
            gr = np.array([g_mod + float(d.loc[(reg, c)]) for c in cs]) / 100.0
            imp = np.array([c not in price.index for c in cs])
            P = np.array([float(price[c]) if c in price.index else float(reg_med[reg]) for c in cs])
            g_reg = float((s0 * gr).sum())
            mix = (float((s0 * (1 + gr) * P).sum()) / ((1 + g_reg) * float((s0 * P).sum())) - 1.0) * 100.0
            rows.append({"region": reg, "quarter": q, "q": str(C.qlabel_to_period(q)), "mix_pp": mix,
                         "region_growth_pct": g_reg * 100.0, "n_countries": len(cs), "n_imputed": int(imp.sum()),
                         "share_imputed": float(s0[imp].sum())})
            for c, v in zip(cs, s0 * (1 + gr) / (1 + g_reg)):
                share[(reg, c)] = float(v)
    out = pd.DataFrame(rows)
    out["_o"] = out.quarter.map(C.qlabel_to_period)
    return out.sort_values(["region", "_o"]).drop(columns="_o").reset_index(drop=True)


def tilt_table() -> pd.DataFrame:
    """The four-region (disclosed-bucket) geo-mix term under the pre-registered ex-NA growth patterns. The arithmetic
    is exfx's own — only the ex-NA bucket pattern is swapped, and it is restored afterwards."""
    keep, rows = M.EXNA_PATTERN, []
    try:
        for q in TILT_QUARTERS:
            for name, pat in TILT_PATTERNS.items():
                M.EXNA_PATTERN = pat
                rg, gm = M.regional_growth_forward(), M.geo_mix_forward()
                rows.append({"quarter": q, "pattern": name, "g_emea": float(rg.loc[q, "g_emea"]),
                             "g_latam": float(rg.loc[q, "g_latam"]), "g_apac": float(rg.loc[q, "g_apac"]),
                             "geo_mix_pp": float(gm.loc[q, "geo_mix_nights_linked_pp"])})
    finally:
        M.EXNA_PATTERN = keep
    return pd.DataFrame(rows)


def h2_scores(term: pd.Series) -> pd.DataFrame:
    """H2: does the sub-regional term add forecast content to the residual? The term is knowable only one quarter late,
    so `core2(t-1) + bundle(t) + subgeo(t-1)` collapses to v1's `core(t-1) + bundle(t)` — reported, not assumed."""
    h = M.history()
    rows = []
    for w, qs in H2_WINDOWS.items():
        e2, e1, ec = [], [], []
        for q in qs:
            p = C.prior_quarter(q)
            res, bun = float(h.loc[q, "residual"]), float(h.loc[q, "bundle"])
            res_p, bun_p, sg_p = float(h.loc[p, "residual"]), float(h.loc[p, "bundle"]), float(term.get(p, 0.0))
            e2.append(res - ((res_p - bun_p - sg_p) + bun + sg_p))
            e1.append(res - (float(h.loc[p, "core"]) + bun))
            ec.append(res - res_p)
        rmse = lambda e: float(np.sqrt(np.mean(np.square(e))))
        rows.append({"window": w, "n": len(qs), "rmse_v2_subgeo": rmse(e2), "rmse_v1_core": rmse(e1),
                     "rmse_carry": rmse(ec), "ratio_v2_vs_carry": rmse(e2) / rmse(ec),
                     "ratio_v1_vs_carry": rmse(e1) / rmse(ec)})
    return pd.DataFrame(rows)


def _reproduces(name: str, new: pd.DataFrame, keys: list[str], cols: list[str], tol: float = 1e-6) -> str:
    """Compare a rebuilt table against the file already on disk, before overwriting it. One-line verdict."""
    path = C.OUT / name
    if not path.exists():
        return f"    {name:38s} no saved file (first build)"
    m = pd.read_csv(path).merge(new, on=keys, how="outer", suffixes=("_s", "_n"), indicator=True)
    if (m._merge != "both").any():
        return f"    {name:38s} KEY SET CHANGED ({int((m._merge != 'both').sum())} rows)"
    d = max(float((m[c + "_s"] - m[c + "_n"]).abs().max()) for c in cols)
    return f"    {name:38s} max |diff| {d:.3e}  -> {'reproduced (<1e-6)' if d < tol else 'CHANGED'}"


def geomix_stage(refresh: bool = True) -> dict:
    """The sub-regional (country-level) geographic-mix term: rebuild the inputs, build the history, the H3 forward,
    the four-region tilt table and the H2 scores; verify each against the saved outputs before overwriting."""
    print("geomix stage (adr_v2_geomix_prereg.md):")
    if refresh:
        from . import refresh_prices as RP
        RP.main(["--quiet"])
    else:
        print("  --no-refresh-prices: reusing the saved stays panel and price levels")

    cg = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv")
    cp = pd.read_csv(C.OUT / "country_price_levels_usd.csv")
    mix, contrib = GX.build_term(cg, cp)
    term = GX.subregional_term(mix)
    mixf = subregional_forward(cg, cp, M.regional_growth_forward())
    termf = GX.subregional_term(mixf)
    tilt = tilt_table()
    scores = h2_scores(term.set_index("quarter").subgeo_pp)

    parts = ["subgeo_pp", "part_NAM", "part_EMEA", "part_LatAm", "part_APAC"]
    print("  reproduction checks (against the outputs on disk, before overwriting):")
    for line in (_reproduces("geomix_subregional_term.csv", term, ["quarter"], parts),
                 _reproduces("geomix_subregional_term_forward.csv", termf, ["quarter"], parts),
                 _reproduces("geo_mix_tilt_sensitivity.csv", tilt, ["quarter", "pattern"],
                             ["g_emea", "g_latam", "g_apac", "geo_mix_pp"]),
                 _reproduces("geomix_within_region.csv", mix, ["region", "quarter"], ["mix_pp", "region_growth_pct"]),
                 _reproduces("geomix_within_region_forward.csv", mixf, ["region", "quarter"],
                             ["mix_pp", "region_growth_pct", "share_imputed"]),
                 _reproduces("geomix_h2_scores.csv", scores, ["window"],
                             ["rmse_v2_subgeo", "rmse_v1_core", "rmse_carry"])):
        print(line)

    mix.to_csv(C.OUT / "geomix_within_region.csv", index=False)
    contrib.to_csv(C.OUT / "geomix_country_contributions.csv", index=False)
    term.to_csv(C.OUT / "geomix_subregional_term.csv", index=False)
    mixf.to_csv(C.OUT / "geomix_within_region_forward.csv", index=False)
    termf.to_csv(C.OUT / "geomix_subregional_term_forward.csv", index=False)
    tilt.to_csv(C.OUT / "geo_mix_tilt_sensitivity.csv", index=False)
    scores.to_csv(C.OUT / "geomix_h2_scores.csv", index=False)

    # upgrade 1: geomix_eurostat  — widen the EMEA/APAC country panel with official nights statistics
    # upgrade 2: od_layer         — the origin/destination layer (reviewer-language origin proxy)
    # upgrade 3: reconcile        — reconcile the sub-regional term with the four disclosed regional buckets
    th = term.set_index("quarter").subgeo_pp
    tf = termf.set_index("quarter").subgeo_pp
    tb = tilt[tilt.pattern.str.startswith("tilt B")].set_index("quarter").geo_mix_pp
    hist = [q for q in th.index if C.qlabel_to_period("1Q23") <= C.qlabel_to_period(q) <= C.qlabel_to_period("2Q26")]
    out = {"subgeo_3q26_pp": float(tf["3Q26"]), "subgeo_4q26_pp": float(tf["4Q26"]),
           "subgeo_hist_mean_1q23_2q26_pp": float(th[hist].mean()),
           "geo_mix_tiltB_3q26_pp": float(tb["3Q26"]), "geo_mix_tiltB_4q26_pp": float(tb["4Q26"]),
           "h2_ratio_W1": float(scores.set_index("window").loc["W1", "ratio_v2_vs_carry"]),
           "h2_ratio_W2": float(scores.set_index("window").loc["W2", "ratio_v2_vs_carry"])}
    print("  sub-regional term 3Q26 {subgeo_3q26_pp:+.3f}pp / 4Q26 {subgeo_4q26_pp:+.3f}pp; 1Q23-2Q26 mean "
          "{subgeo_hist_mean_1q23_2q26_pp:+.3f}pp; tilt-B four-region geo mix 4Q26 {geo_mix_tiltB_4q26_pp:+.3f}pp"
          .format(**out))
    return out


# ---------------------------------------------------------------------------------------------------------------- #
def seed_inputs() -> list[str]:
    """Copy the frozen inputs v3 does not rebuild from adr_engine's outputs, once, if absent (never overwrites)."""
    C.OUT.mkdir(parents=True, exist_ok=True); copied = []
    for f in C.SEED_FILES:
        if not (C.OUT / f).exists() and (C.SEED_FROM / f).exists():
            shutil.copy2(C.SEED_FROM / f, C.OUT / f); copied.append(f)
    return copied


def main(argv=None):
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(); ap.add_argument("--fetch", action="store_true"); ap.add_argument("--no-posterior", action="store_true"); ap.add_argument("--no-workbook", action="store_true")
    ap.add_argument("--no-refresh-prices", action="store_true", help="geomix stage: skip the raw-store rebuild")
    ap.add_argument("--no-figures", action="store_true", help="skip the seven figures")
    a = ap.parse_args(argv); t0 = time.time(); C.OUT.mkdir(parents=True, exist_ok=True)
    seeded = seed_inputs()
    if seeded: print("seeded read-only inputs from adr_engine:", ", ".join(seeded))
    if a.fetch:
        from . import fetch_fx; fetch_fx.main()
    daily = F.load_daily(); shares = F.gbv_shares(); tg = F.disclosed_targets()
    wf, full = W.run(daily, shares, tg); sc = W.score(wf); promo = W.promotion(sc)
    wf.to_csv(C.OUT / "fx_pit_walkforward.csv", index=False); sc.to_csv(C.OUT / "fx_scores.csv", index=False); full.to_csv(C.OUT / "fx_design_full.csv")
    print("walk-forward:", promo)
    # audit fix (a): the registered V1 variant beside V0 (V0 stays the leg), and V0's LatAm-conditional error
    from . import fx_diagnostics as D
    beta_v1 = D.fit_v1_all(full); pd.DataFrame([beta_v1]).to_csv(C.OUT / "fx_v1_map_beta_all17.csv", index=False)
    a2, b2 = E.fit_ols(full.eur_yoy.values, full.y.values)                  # audit fix (j): V2 on every disclosed quarter
    pd.DataFrame([{"intercept_pp": a2, "slope_per_eur_pct": b2, "n": len(full)}]).to_csv(C.OUT / "fx_v2_fit_all17.csv", index=False)
    fc = X.run(daily, shares, beta_v1={r: beta_v1[r] for r in C.REGIONS}, v2_coef=(a2, b2)); fc.to_csv(C.OUT / "fx_forecast_asof.csv", index=False)
    fwd_latam = {q: F.design_row(daily, shares, q, None)["latam"] for q in ("3Q26", "4Q26")}
    D.v0_error_on_latam(wf, full, fwd_latam).to_csv(C.OUT / "fx_v0_error_on_latam.csv", index=False)
    D.latam_strong_quarters(full).to_csv(C.OUT / "fx_v0_latam_strong_quarters.csv")
    X.currency_table(daily).to_csv(C.OUT / "fx_currency_contributions.csv", index=False)
    if not a.no_posterior:
        from . import posterior; posterior.main()
    _f = fc[fc["asof"] == "2026-09-21"].set_index("quarter")                  # the leg's own FX band, per quarter (fix j)
    sd = pd.Series({q: float(_f.loc[q, "sd_mid" if (C.FX_LEG == "midpoint" and q in C.FX_MIDPOINT_QUARTERS) else "sd"]) for q in C.FORWARD_QUARTERS})
    M.history().to_csv(C.OUT / "exfx_history.csv"); M.forward().to_csv(C.OUT / "exfx_forward_base.csv")
    M.geo_mix_history_check().to_csv(C.OUT / "geo_mix_method_check.csv")
    M.regional_growth_forward().to_csv(C.OUT / "regional_growth_forward.csv"); M.geo_mix_forward().to_csv(C.OUT / "geo_mix_forward.csv")
    M.bundle_schedule().to_csv(C.OUT / "bundle_schedule.csv"); M.envelope(sd).to_csv(C.OUT / "exfx_envelope.csv")
    M.construction_cases().to_csv(C.OUT / "exfx_construction_cases.csv")          # audit fix (c)
    gm = geomix_stage(refresh=not a.no_refresh_prices)
    M.alternatives().to_csv(C.OUT / "exfx_alternatives.csv", index=False)    # composition rows read the geomix files
    path = A.build(); path.to_csv(C.OUT / "adr_path.csv"); A.scenario_table().to_csv(C.OUT / "adr_scenarios.csv", index=False)
    if not a.no_figures:
        G.main()
    if not a.no_workbook:
        print("workbook stage disabled in v3: model/ is protected (CLAUDE.md rule 1); use --no-workbook")
    meta = {"run_at": pd.Timestamp.now().isoformat(timespec="seconds"), "fx_last_obs": str(daily.index.max().date()), "promotion": promo,
            "adr_3q26": float(path.loc["3Q26", "adr_usd"]), "adr_4q26": float(path.loc["4Q26", "adr_usd"]),
            "fx_leg": C.FX_LEG,
            "adr_3q26_fx_v1": float(path.loc["3Q26", "adr_usd_fx_v1"]), "adr_4q26_fx_v1": float(path.loc["4Q26", "adr_usd_fx_v1"]),
            "adr_3q26_fx_identity": float(path.loc["3Q26", "adr_usd_fx_identity"]), "adr_4q26_fx_identity": float(path.loc["4Q26", "adr_usd_fx_identity"]),
            "fx_v1_beta_all17": beta_v1, "fx_3q26_pp": float(path.loc["3Q26", "fx_pp"]),
            "fx_4q26_pp": float(path.loc["4Q26", "fx_pp"]), "subgeo_4q26_pp": gm["subgeo_4q26_pp"],
            "geo_mix_tiltB_4q26_pp": gm["geo_mix_tiltB_4q26_pp"], "geomix": gm, "seconds": round(time.time() - t0, 1)}
    (C.OUT / "00_summary.json").write_text(json.dumps(meta, indent=2)); print(json.dumps(meta, indent=2))
    from . import compare_v2; compare_v2.main()                                   # v3 against adr_engine (v2) as filed


if __name__ == "__main__":
    main()
