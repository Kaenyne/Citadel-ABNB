"""adr_engine / exfx.py — the ex-FX ADR mechanism (pre-registration §6).

    exFX_yoy(t) = core(t) + bundle(t) + geo_mix(t) + unit_size(t) + los_mix(t) + seats(t) + interaction(t) [+ fee_K(t)]

History 1Q23–2Q26 from the H decomposition (adr_history_components.csv); the like-for-like residual is split into
`bundle` (the product bundle's ADR contribution as management sized it, ~1pp, on the nights line's lap calendar)
and `core` (residual minus bundle). Forward: core carried at its last observed value (the same carry rule the card
applies to the whole residual), bundle legs lap on their filed anniversaries, geo mix computed from the nights
line's own regional path and the 10-K regional ADR levels, the other mix terms carried as the card does."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C

# ---- bundle sizing (points of ADR) -------------------------------------------------------------------------------
BUNDLE_ADR_PP = 1.0            # management: 4Q25 ">200bp nights / ~300bp GBV" (D014), 1Q26 "~3 pts nights / ~4 pts GBV" (D032) -> ~1pp ADR
BUNDLE_BAND = (0.5, 1.5)       # audit fix (f): the rounding permits 0-1.5 (4Q25) and 0-2.0 (1Q26); v2 used 0.8-1.2. The 1Q26
                               # figure also includes ~6 weeks of ex-NA RNPL (live 17 Feb 2026), so "did not rise" cannot size that leg
STEP_3Q25, STEP_4Q25 = 0.92, 0.88      # K4 residual steps on the filed dates (US RNPL live 3Q25; cancellation redesign + fee tranche 1 4Q25)
SPLIT_RNPL_NA = STEP_3Q25 / (STEP_3Q25 + STEP_4Q25)                     # 0.511 of the ~1pp is the NA RNPL (larger-home mix) leg
RNPL_EXNA_ADR_PP_BASE, RNPL_EXNA_ADR_PP_HIGH = 0.0, 0.68 + 0.47       # base: unsized by management (1Q26 "~1" did not rise); high: the 1H26 residual steps
PHASE_1Q26_EXNA = 0.5          # ex-NA RNPL live 17 Feb 2026: about half of 1Q26
PHASE_1Q27_LAP = 0.40          # nights line convention (phase_1q27)
CORE_MEAN_2023_25 = 2.398      # v2 value: the 2023-25 mean of the RESIDUAL, not the core. Superseded by core_mean_2023_25() (audit fix d)

# ---- the nights line's regional path (nights_v2_design.md §2.1 / §2a), used for the geo-mix term -----------------
NIGHTS_LINE = pd.DataFrame({
    "quarter": ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"],
    "total_yoy": [9.887, 8.157, 8.206, 5.934, 6.229, 6.045],
    "na_yoy":    [5.60, 3.31, 2.31, 2.31, 2.31, 2.31],
    "na_share":  [0.288, 0.282, 0.291, 0.291, 0.288, 0.282],
}).set_index("quarter")
EXNA_PATTERN = {"emea": 8.0, "latam": 20.0, "apac": 18.0}   # 2Q26 letter buckets (mid); scaled each quarter to the nights line's ex-NA rate

# ---- card terms (adrv3 P1, workstream I measured 3Q26 terms; J3 carry convention) ---------------------------------
CARD_TERMS = {"geo_mix": -1.428426, "unit_size": 0.796672, "los_mix": 0.056264, "seats_2026": -0.482570, "seats_2027": -0.565, "interaction": -0.10}
CARD_BANDS = {"geo_mix": (-1.5709, -0.9353), "unit_size": (0.5299, 0.9985), "los_mix": (-0.0811, 0.2887), "seats": (-0.7503, -0.2262), "interaction": (-0.15, -0.05)}


# ---- audit fix (c): forward terms measured on the same construction as the carried core ---------------------------
CONSTRUCTION_FIX = True        # False reproduces adr_engine (v2) exactly


def construction_offsets() -> dict:
    """The carried 2Q26 core is disclosed ex-FX minus the H decomposition's terms, but the forward adds geo mix from the
    bucket arithmetic (nights-linked) and unit size / LOS from workstream I. Put the forward on the core's footing:
    geo offset = bucket(2Q26) - H(2Q26) [positive in all 7 quarters 4Q24-2Q26]; unit offset = I's 2Q26 value on the
    identical construction as its forward 3Q26 value - H's 2Q26 value [the H 2Q26 capacity was measured on dumps in
    which 2Q26 was still partly reviewed; see docs/adr-card-v3_1/CARD_V3_1.md on branch krish/cc-search-price]; LOS
    has no same-construction 2Q26 value (H's 2026 LOS is an assumed fill), so case A carries the in-core 0.30 forward
    and case B (the measured blocked-run LOS drop is real) is reported as the bound (construction_cases())."""
    chk = geo_mix_history_check()
    i = pd.read_csv(C.I_MIX_3Q26); h = pd.read_csv(C.H_COMPONENTS).set_index("quarter")
    u_i = float(i[(i.term == "unit_size") & (i.quarter == "2Q26")].point_pp.iloc[0])
    return {"geo_off": float(chk.loc["2Q26", "geo_mix_buckets_pp"] - chk.loc["2Q26", "geo_mix_H_pp"]),
            "unit_off": u_i - float(h.loc["2Q26", "unit_size_pp"]),
            "los_in_core": float(h.loc["2Q26", "los_mix_pp"])}


def history() -> pd.DataFrame:
    h = pd.read_csv(C.H_COMPONENTS).set_index("quarter")
    out = pd.DataFrame(index=h.index)
    out["adr_usd"] = h.adr_usd; out["reported_yoy"] = h.adr_yoy_reported_pp; out["fx_pp"] = h.fx_effect_pp
    out["exfx_yoy"] = h.adr_exfx_yoy_pp; out["geo_mix"] = h.geo_mix_pp; out["unit_size"] = h.unit_size_pp
    out["los_mix"] = h.los_mix_pp; out["seats"] = h.new_business_pp.fillna(0.0); out["interaction"] = h.interaction_pp
    out["residual"] = h.residual_pricing_pp
    b = bundle_schedule()
    out["bundle"] = [b.loc[q, "bundle_total"] if q in b.index else 0.0 for q in out.index]
    out["core"] = out.residual - out.bundle
    out["basis"] = "history (H decomposition, disclosed letter figures)"
    return out


def bundle_schedule(bundle_total=BUNDLE_ADR_PP, split_na=SPLIT_RNPL_NA, exna_pp=RNPL_EXNA_ADR_PP_BASE) -> pd.DataFrame:
    """Live bundle legs by quarter (points of ADR). NA RNPL leg live 3Q25–2Q26 (laps 3Q26); fee/cancellation leg live
    4Q25–3Q26 (laps 4Q26); ex-NA RNPL leg live from 1Q26 (half), laps 1Q27 (0.40 phase) / 2Q27 (full)."""
    qs = ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"] + C.FORWARD_QUARTERS
    b1, b2 = bundle_total * split_na, bundle_total * (1 - split_na)
    rows = []
    for q in qs:
        i = C.qlabel_to_period(q)
        live_na = 1.0 if C.qlabel_to_period("3Q25") <= i <= C.qlabel_to_period("2Q26") else 0.0
        live_fee = 1.0 if C.qlabel_to_period("4Q25") <= i <= C.qlabel_to_period("3Q26") else 0.0
        if i == C.qlabel_to_period("1Q26"): live_ex = PHASE_1Q26_EXNA
        elif C.qlabel_to_period("2Q26") <= i <= C.qlabel_to_period("4Q26"): live_ex = 1.0
        elif i == C.qlabel_to_period("1Q27"): live_ex = 1.0 - PHASE_1Q27_LAP
        else: live_ex = 0.0
        rows.append({"quarter": q, "rnpl_na_leg": b1 * live_na, "fee_cancel_leg": b2 * live_fee, "rnpl_exna_leg": exna_pp * live_ex})
    d = pd.DataFrame(rows).set_index("quarter"); d["bundle_total"] = d.sum(axis=1)
    return d


def regional_base() -> pd.DataFrame:
    """Base-quarter regional nights shares and anchored regional ADR levels (04_regional_quarterly_wide, disclosed-chained)."""
    w = pd.read_csv(C.ROOT / "data/processed/adr/04_regional_quarterly_wide.csv").set_index("quarter")
    out = pd.DataFrame({r: w[f"nights_share_{r}_pct"] / 100.0 for r in C.REGIONS})
    for r in C.REGIONS:
        out[f"adr_{r}"] = w[f"adr_{r}_usd_anchored"]
    return out


def geo_mix_pp(shares_base: dict, adr_base: dict, growth: dict) -> float:
    """Pure mix effect on blended ADR, in pp: regional ADR levels held at the base quarter, shares shifted by growth."""
    s = np.array([shares_base[r] for r in C.REGIONS]); a = np.array([adr_base[r] for r in C.REGIONS]); g = np.array([growth[r] for r in C.REGIONS]) / 100.0
    s = s / s.sum()
    gt = float((s * g).sum())
    s_new = s * (1 + g) / (1 + gt)
    return float(((s_new * a).sum() / (s * a).sum() - 1.0) * 100.0)


def regional_growth_forward() -> pd.DataFrame:
    """Regional nights growth implied by the nights line: NA from the line; ex-NA split by the 2Q26 bucket pattern scaled to the
    line's ex-NA rate on the base-quarter within-ex-NA shares."""
    rb = regional_base(); rows = []
    for q, r in NIGHTS_LINE.iterrows():
        exna = (r.total_yoy - r.na_share * r.na_yoy) / (1 - r.na_share)
        bq = C.prior_quarter(q, 4)
        if bq in rb.index:
            sh = rb.loc[bq]
        else:                                    # 3Q26 / 4Q26 as base of 3Q27 / 4Q27: roll the year-earlier shares by the modelled growth
            prev = rows[-4] if len(rows) >= 4 else None
            sh = pd.Series({rr: prev[f"share_{rr}"] * (1 + prev[f"g_{rr}"] / 100) / (1 + prev["g_total"] / 100) for rr in C.REGIONS})
        w = np.array([sh[rr] for rr in ("emea", "latam", "apac")]); p = np.array([EXNA_PATTERN[rr] for rr in ("emea", "latam", "apac")])
        k = exna / float((w * p).sum() / w.sum())
        g = {"na": float(r.na_yoy), "emea": k * EXNA_PATTERN["emea"], "latam": k * EXNA_PATTERN["latam"], "apac": k * EXNA_PATTERN["apac"]}
        row = {"quarter": q, "base_quarter": bq, "exna_yoy": exna, "k_scale": k, "g_total": float(r.total_yoy)}
        row.update({f"g_{rr}": g[rr] for rr in C.REGIONS}); row.update({f"share_{rr}": float(sh[rr]) for rr in C.REGIONS})
        rows.append(row)
    return pd.DataFrame(rows).set_index("quarter")


def geo_mix_forward() -> pd.DataFrame:
    rb = regional_base(); rg = regional_growth_forward(); rows = []
    adr_levels = None
    for q, r in rg.iterrows():
        bq = r.base_quarter
        if bq in rb.index:
            adr_levels = {rr: float(rb.loc[bq, f"adr_{rr}"]) for rr in C.REGIONS}      # relative levels; held for rolled bases
        shares = {rr: float(r[f"share_{rr}"]) for rr in C.REGIONS}; growth = {rr: float(r[f"g_{rr}"]) for rr in C.REGIONS}
        rows.append({"quarter": q, "geo_mix_nights_linked_pp": geo_mix_pp(shares, adr_levels, growth), "geo_mix_card_pp": CARD_TERMS["geo_mix"]})
    return pd.DataFrame(rows).set_index("quarter")


def geo_mix_history_check() -> pd.DataFrame:
    """Same arithmetic on the disclosed regional bucket midpoints vs the H decomposition's geo-mix term (validation of the method)."""
    rb = regional_base(); p = pd.read_csv(C.ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv").set_index("quarter")
    h = pd.read_csv(C.H_COMPONENTS).set_index("quarter"); rows = []
    for q in h.index:
        bq = C.prior_quarter(q, 4)
        if q not in p.index or bq not in rb.index or pd.isna(p.loc[q, "na_nights_yoy_mid"]): continue
        growth = {rr: float(p.loc[q, f"{rr}_nights_yoy_mid"]) for rr in C.REGIONS}
        shares = {rr: float(rb.loc[bq, rr]) for rr in C.REGIONS}; adr = {rr: float(rb.loc[bq, f"adr_{rr}"]) for rr in C.REGIONS}
        rows.append({"quarter": q, "geo_mix_buckets_pp": geo_mix_pp(shares, adr, growth), "geo_mix_H_pp": float(h.loc[q, "geo_mix_pp"])})
    d = pd.DataFrame(rows).set_index("quarter"); d["diff_pp"] = d.geo_mix_buckets_pp - d.geo_mix_H_pp
    return d


def forward(core_rule="carry", geo_basis="nights_linked", bundle_total=BUNDLE_ADR_PP, split_na=SPLIT_RNPL_NA,
            exna_pp=RNPL_EXNA_ADR_PP_BASE, fee_k=False, terms=None) -> pd.DataFrame:
    """Forward ex-FX build 3Q26–4Q27. core_rule: 'carry' (last observed core), 'mean_reversion' (2023-25 mean), 'ar1'."""
    hist = history()
    b = bundle_schedule(bundle_total, split_na, exna_pp)
    hist["bundle"] = [b.loc[q, "bundle_total"] for q in hist.index]; hist["core"] = hist.residual - hist.bundle
    gm = geo_mix_forward(); terms = terms or CARD_TERMS
    core_last = float(hist.core.iloc[-1])
    const, rho = core_ar1()                       # audit fix (d): fitted on the core (v2: K4's residual AR(1) .750 / .747)
    core_mean = core_mean_2023_25()               # audit fix (d): the core's own 2023-25 mean (v2: the residual's 2.398)
    rows = []; prev_core = core_last
    for i, q in enumerate(C.FORWARD_QUARTERS):
        if core_rule == "carry": core = core_last
        elif core_rule == "mean_reversion": core = core_mean
        elif core_rule == "ar1": core = const + rho * prev_core; prev_core = core
        else: raise ValueError(core_rule)
        geo = float(gm.loc[q, "geo_mix_nights_linked_pp"]) if geo_basis == "nights_linked" else terms["geo_mix"]
        seats = terms["seats_2026"] if q.endswith("26") else terms["seats_2027"]
        kline = 0.0
        if fee_k:                                  # K4 central fee-migration mechanics line (labelled sensitivity, DEC-0008)
            sched = pd.read_csv(C.ROOT / "data/processed/adrv3/K/K4_fee_lap_schedule.csv"); sched = sched[sched.variant == "central"].set_index("quarter")
            base_share = float(sched.loc["2Q26", "yoy_change_pp"]); kline = 0.007 * (float(sched.loc[q, "yoy_change_pp"]) - base_share) if q in sched.index else 0.0
        bt = float(b.loc[q, "bundle_total"])
        los, basis_adj = terms["los_mix"], 0.0
        if CONSTRUCTION_FIX:                        # audit fix (c), case A
            off = construction_offsets()
            basis_adj = -off["unit_off"] - (off["geo_off"] if geo_basis == "nights_linked" else 0.0)
            los = off["los_in_core"]
        exfx = core + bt + geo + terms["unit_size"] + los + seats + terms["interaction"] + kline + basis_adj
        rows.append({"quarter": q, "core": core, "bundle": bt, "rnpl_na_leg": b.loc[q, "rnpl_na_leg"], "fee_cancel_leg": b.loc[q, "fee_cancel_leg"],
                     "rnpl_exna_leg": b.loc[q, "rnpl_exna_leg"], "residual": core + bt, "geo_mix": geo, "unit_size": terms["unit_size"],
                     "los_mix": los, "seats": seats, "interaction": terms["interaction"], "fee_k": kline, "basis_adj": basis_adj, "exfx_yoy": exfx,
                     "core_rule": core_rule, "geo_basis": geo_basis})
    return pd.DataFrame(rows).set_index("quarter")


def alternatives() -> pd.DataFrame:
    """The residual (core + bundle) and ex-FX under every rule carried beside the base."""
    k4 = pd.read_csv(C.K4_NOWCAST)
    base = forward()
    # K4 "lap only, residual steps": every residual change since 2Q25 is a dated product step that laps at its anniversary
    lap_only = base.copy(); steps = {"3Q26": 3.933, "4Q26": 3.056, "1Q27": 3.056 - 0.68, "2Q27": 3.056 - 0.68 - 0.47, "3Q27": 3.056 - 0.68 - 0.47, "4Q27": 3.056 - 0.68 - 0.47}
    for q in lap_only.index:
        lap_only.loc[q, "residual"] = steps[q]; lap_only.loc[q, "core"] = steps[q] - lap_only.loc[q, "bundle"]
        lap_only.loc[q, "exfx_yoy"] = steps[q] + lap_only.loc[q, ["geo_mix", "unit_size", "los_mix", "seats", "interaction", "fee_k", "basis_adj"]].sum()
    # composition scenarios (adr_v2_geomix_prereg.md): sub-regional term H3 (geomix_subregional_term_forward.csv) and the four-region tilt B
    subf = pd.read_csv(C.OUT / "geomix_subregional_term_forward.csv").set_index("quarter").subgeo_pp if (C.OUT / "geomix_subregional_term_forward.csv").exists() else None
    tilt = pd.read_csv(C.OUT / "geo_mix_tilt_sensitivity.csv") if (C.OUT / "geo_mix_tilt_sensitivity.csv").exists() else None
    comp = base.copy()
    # audit fix (e): the carried 2Q26 core already contains 2Q26's sub-regional term (the residual is ex-FX minus the
    # four-region terms only), so the scenario adds the CHANGE from 2Q26, not the level. Read by label, never by position
    # (geomix_subregional_term.csv carries a partial quarter-to-date row after 2Q26).
    sub_2q26 = 0.0
    if SUBGEO_NETTING and (C.OUT / "geomix_subregional_term.csv").exists():
        sub_2q26 = float(pd.read_csv(C.OUT / "geomix_subregional_term.csv").set_index("quarter").subgeo_pp.loc["2Q26"])
    if subf is not None:
        for q in comp.index:
            inc = float(subf.get(q, 0.0)) - sub_2q26
            comp.loc[q, "geo_mix"] = comp.loc[q, "geo_mix"] + inc; comp.loc[q, "exfx_yoy"] = comp.loc[q, "exfx_yoy"] + inc
    tiltb = comp.copy()
    if tilt is not None:
        tb = tilt[tilt.pattern.str.startswith("tilt B")].set_index("quarter").geo_mix_pp; tbase = tilt[tilt.pattern.str.startswith("base")].set_index("quarter").geo_mix_pp
        for q in tiltb.index:
            if q in tb.index:
                d = float(tb[q] - tbase[q]); tiltb.loc[q, "geo_mix"] += d; tiltb.loc[q, "exfx_yoy"] += d
    # measured origin-destination tilt (upgrade 2, od_layer.py): the tourism-board allocation of the named origins
    odm = comp.copy()
    if (C.OUT / "od_geo_mix_measured_tilt.csv").exists():
        od = pd.read_csv(C.OUT / "od_geo_mix_measured_tilt.csv"); odc = od[od.pattern.str.startswith("measured OD tilt (central)")].set_index("quarter")
        for q in odm.index:
            if q in odc.index:
                d = float(odc.loc[q, "delta_vs_base_pp"]); odm.loc[q, "geo_mix"] += d; odm.loc[q, "exfx_yoy"] += d
    alts = {
        "base: core carry + bundle laps (nights-linked geo)": base,
        "base + sub-regional country mix (v2 H3, Inside Airbnb panel)": comp,
        "base + sub-regional + measured origin-destination tilt (upgrade 2: EMEA 10.5 / LatAm 16.4 / APAC 14.9)": odm,
        "base + sub-regional + composition tilt B (EMEA 5 / LatAm 30 / APAC 25) — retired by upgrade 2": tiltb,
        "lap-only (K4 residual steps): every 2025-26 residual step laps at its anniversary": lap_only,
        "card v3: last_q residual carry, no lap (card geo)": forward(bundle_total=0.0, geo_basis="card"),
        "full lap: ex-NA RNPL sized at the 1H26 residual steps": forward(exna_pp=RNPL_EXNA_ADR_PP_HIGH),
        "core mean reversion to the 2023-25 mean": forward(core_rule="mean_reversion"),
        "AR(1) fitted on core": forward(core_rule="ar1"),
        "base + fee-migration K line (DEC-0008 sensitivity)": forward(fee_k=True),
    }
    rows = []
    for name, d in alts.items():
        for q, r in d.iterrows():
            rows.append({"rule": name, "quarter": q, "residual_pp": r.residual, "exfx_yoy_pct": r.exfx_yoy, "geo_mix_pp": r.geo_mix})
    out = pd.DataFrame(rows)
    # K4's own scenario rows for 3Q26 / 4Q26, for the record
    for _, r in k4.iterrows():
        rows.append({"rule": "K4: " + r.scenario, "quarter": r.quarter, "residual_pp": r.residual_pp, "exfx_yoy_pct": np.nan, "geo_mix_pp": np.nan})
    return pd.DataFrame(rows)


SUBGEO_NETTING = True          # audit fix (e); False reproduces v2's double count


# ---- audit fix (d): the downside rows on the core's own statistics ---------------------------------------------------
CORE_FIX = True                # False reproduces the v2 rows (residual mean 2.398; K4's residual AR(1) 0.750 / 0.747)
YEARS_2023_25 = ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25"]


def core_mean_2023_25() -> float:
    """The core's own 2023-25 mean (2.272), not the residual's (2.398): the residual includes the bundle in 3Q25-4Q25."""
    return float(history().core.loc[YEARS_2023_25].mean()) if CORE_FIX else CORE_MEAN_2023_25


def core_ar1() -> tuple[float, float]:
    """(const, rho) of an AR(1) fitted by OLS on the core itself, 1Q23-2Q26 (13 pairs). v2 used K4's residual AR(1)
    (const 0.750, rho 0.747), whose implied mean 2.96 is the residual's, not the core's."""
    if not CORE_FIX:
        return 0.750, 0.747
    c = history().core.to_numpy()
    rho, const = np.polyfit(c[:-1], c[1:], 1)
    return float(const), float(rho)


def construction_cases() -> pd.DataFrame:
    """Audit fix (c): the base ex-FX as filed (v2), under case A (the default: LOS switch treated as a basis offset)
    and under case B (the measured LOS drop is real: forward LOS stays at I's 0.056)."""
    global CONSTRUCTION_FIX
    keep = CONSTRUCTION_FIX
    try:
        CONSTRUCTION_FIX = False; v2 = forward().exfx_yoy
        CONSTRUCTION_FIX = True; a = forward().exfx_yoy
    finally:
        CONSTRUCTION_FIX = keep
    off = construction_offsets()
    b = a + (CARD_TERMS["los_mix"] - off["los_in_core"])
    return pd.DataFrame({"exfx_v2_as_filed": v2, "exfx_case_A": a, "exfx_case_B": b,
                         "d_case_A_pp": a - v2, "d_case_B_pp": b - v2}).assign(**{k: v for k, v in off.items()})


def core_carry_error_sd() -> dict:
    """Empirical h-step-ahead error of carrying core flat, from the 14-quarter core history (1Q23-2Q26): sd of the
    h-quarter change, h = 1..6 (pre-registration §6: 'core carry ± its own 2023-26 quarterly change sd')."""
    c = history().core.values
    return {h: float(np.std(c[h:] - c[:-h], ddof=1)) for h in range(1, 7)}


def envelope(fx_sd: pd.Series) -> pd.DataFrame:
    """Parameter envelope (RSS of half-ranges, J3 convention) on the base: bundle total BUNDLE_BAND (0.5-1.5; v2 0.8-1.2), ex-NA RNPL leg 0-1.15,
    geo (nights-linked vs card), unit, LOS, seats, interaction bands, the core carry's own h-step error; plus the FX
    predictive sd. Returns per-quarter half-band."""
    base = forward(); rows = []; cse = core_carry_error_sd()
    for h, (q, r) in enumerate(base.iterrows(), start=1):
        half = [cse[h]]
        half.append(abs(forward(bundle_total=BUNDLE_BAND[1]).loc[q, "exfx_yoy"] - forward(bundle_total=BUNDLE_BAND[0]).loc[q, "exfx_yoy"]) / 2)
        half.append(abs(forward(exna_pp=RNPL_EXNA_ADR_PP_HIGH).loc[q, "exfx_yoy"] - r.exfx_yoy) / 2)
        half.append(abs(r.geo_mix - CARD_TERMS["geo_mix"]) / 2)
        for k, key in (("unit_size", "unit_size"), ("los_mix", "los_mix"), ("seats", "seats"), ("interaction", "interaction")):
            lo, hi = CARD_BANDS[key]; half.append((hi - lo) / 2)
        rss = float(np.sqrt(np.sum(np.square(half))))
        fxsd = float(fx_sd.get(q, 0.0))
        rows.append({"quarter": q, "exfx_half_band_pp": rss, "core_carry_sd_pp": cse[h], "fx_sd_pp": fxsd, "reported_half_band_pp": float(np.sqrt(rss ** 2 + fxsd ** 2)),
                     "halfwidths": "core_carry|bundle|exna|geo|unit|los|seats|interaction=" + "|".join(f"{x:.3f}" for x in half)})
    return pd.DataFrame(rows).set_index("quarter")
