"""adr_engine / reconcile.py — upgrade 3: reconcile the ADR line's mix terms to the company's own numbers.

Two checks, both run end to end by this file (exit 0):

  A. ANNUAL (FY2023-25).  The repo's 10-K-based decomposition (`data/processed/adr/07_full_decomposition.csv`,
     built by `analysis/src/adr/07_assemble.py`) leaves one jointly unidentified line,
     `pricing_and_subregional_mix_pp` = within_region_exfx - size_mix - LOS.  This module puts our own
     sub-regional (country) mix term inside that plug and asks what price remainder is left:

         implied like-for-like price  =  plug  -  our sub-regional mix          (as briefed)
         implied price (rebased)      =  within_region_exfx - our size - our LOS - our sub-regional mix

     and compares the remainder with government accommodation price indices (HICP CP112 for the euro area,
     BLS lodging-away-from-home for the US, and a GBV-weighted four-region blend).  It also verifies the 07
     file's own identities and says which of them are definitional rather than tests.

  B. QUARTERLY, EMEA (4Q24-2Q26, n 7; extended 1Q24-2Q26, n 10).  The disclosed EMEA ex-FX ADR y/y should be

         disclosed EMEA ex-FX  =  within-EMEA country mix  +  within-country price growth  +  EMEA size/LOS

     so the implied within-country price growth is the disclosed number less our EMEA mix term (and, in a
     second column, less a size/LOS proxy, since no regional size/LOS is disclosed).  That implied price is
     scored against (i) euro-area HICP accommodation, (ii) a panel-share-weighted EMEA accommodation CPI
     built from the country HICP series and the ONS accommodation index, and (iii) the M2 quarterly median
     listed prices for Rome / Paris / Barcelona / London in local currency, on a like-for-like price basis.

Outputs
  data/processed/pitch_model_v2/adr_engine/reconcile_annual.csv
  data/processed/pitch_model_v2/adr_engine/reconcile_emea_quarterly.csv

Run
  cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.reconcile
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pitch_model_v2.adr_engine import config as C

ROOT = C.ROOT
OUT = C.OUT

DECOMP_07 = ROOT / "data/processed/adr/07_full_decomposition.csv"
REGIONAL_WIDE = ROOT / "data/processed/adr/04_regional_quarterly_wide.csv"
H_COMPONENTS = C.H_COMPONENTS
SUBGEO = OUT / "geomix_subregional_term.csv"
WITHIN = OUT / "geomix_within_region.csv"
CONTRIB = OUT / "geomix_country_contributions.csv"
EXFX_HIST = OUT / "exfx_history.csv"
GOVDATA = ROOT / "data/processed/govdata/P/P_feature_quarterly_panel.csv"
M2 = ROOT / "data/processed/adrv3/M/M2_new_listing_premium.csv"

YEARS = [2023, 2024, 2025]
# The seven quarters whose EMEA ex-FX ADR y/y is a whole disclosed point (4Q24 +6 ... 2Q26 +5).
EMEA_Q7 = ["4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
EMEA_Q10 = ["1Q24", "2Q24", "3Q24"] + EMEA_Q7

# Panel country -> government accommodation-price series in the govdata quarterly panel.
# HICP CP112 = "accommodation services", y/y %, quarter mean of the monthly rates.
HICP_MAP = {
    "italy": "hicp_CP112_IT_RCH_A", "spain": "hicp_CP112_ES_RCH_A", "france": "hicp_CP112_FR_RCH_A",
    "portugal": "hicp_CP112_PT_RCH_A", "greece": "hicp_CP112_EL_RCH_A", "ireland": "hicp_CP112_IE_RCH_A",
    "hungary": "hicp_CP112_HU_RCH_A", "czech-republic": "hicp_CP112_CZ_RCH_A",
    "germany": "hicp_CP112_DE_RCH_A", "belgium": "hicp_CP112_BE_RCH_A", "austria": "hicp_CP112_AT_RCH_A",
    "the-netherlands": "hicp_CP112_NL_RCH_A", "denmark": "hicp_CP112_DK_RCH_A",
    "norway": "hicp_CP112_NO_RCH_A", "switzerland": "hicp_CP112_CH_RCH_A",
    "sweden": "hicp_CP112_SE_RCH_A", "croatia": "hicp_CP112_HR_RCH_A", "poland": "hicp_CP112_PL_RCH_A",
    "united-kingdom": "ons_cpi_112_accommodation_index",   # ONS CPI 11.2 accommodation, y/y %
    "turkey": "hicp_CP112_TR_RCH_A",                        # excluded from the primary blend (hyperinflation)
}
TURKEY = "turkey"
# Four-region accommodation-price comparators for the annual blend.
REGION_CPI = {"na": "bls_CUUR0000SEHB02", "emea": "hicp_CP112_EA_RCH_A",
              "latam": "ibge_ipca_hospedagem_yoy12m", "apac": "abs_cpi_30033_Q"}


# ----------------------------------------------------------------------------- helpers
def qyear(q: str) -> int:
    return 2000 + int(q[2:])


def wmean(x: pd.Series, w: pd.Series) -> float:
    x = pd.to_numeric(x, errors="coerce"); w = pd.to_numeric(w, errors="coerce")
    m = x.notna() & w.notna()
    return float(np.average(x[m], weights=w[m])) if m.any() else float("nan")


def load_gbv() -> pd.Series:
    h = pd.read_csv(H_COMPONENTS)
    return h.set_index("quarter").gbv_busd


def load_gov() -> pd.DataFrame:
    g = pd.read_csv(GOVDATA, index_col=0)
    g.index.name = "quarter"
    return g


# ----------------------------------------------------------------------------- A. annual
def annual() -> tuple[pd.DataFrame, dict]:
    d07 = pd.read_csv(DECOMP_07).set_index("year")
    h = pd.read_csv(H_COMPONENTS)
    sub = pd.read_csv(SUBGEO)
    win = pd.read_csv(WITHIN)
    ex = pd.read_csv(EXFX_HIST)
    gov = load_gov()
    gbv = load_gbv()

    h["year"] = h.quarter.map(qyear)
    sub["year"] = sub.quarter.map(qyear)
    win["year"] = win.quarter.map(qyear)
    ex["year"] = ex.quarter.map(qyear)
    sub["gbv"] = sub.quarter.map(gbv)
    win["gbv"] = win.quarter.map(gbv)
    ex["gbv"] = ex.quarter.map(gbv)

    gov_y = gov.copy(); gov_y["year"] = [qyear(q) for q in gov_y.index]
    gov_ann = gov_y.groupby("year").mean(numeric_only=True)

    # GBV shares by fiscal year, for the four-region CPI blend.
    reg = pd.read_csv(ROOT / "data/processed/adr/01_regional_annual.csv")
    reg = reg[reg.region.isin(C.REGIONS)]
    shares = reg.pivot(index="year", columns="region", values="gbv_share_pct") / 100.0

    rows = []
    for y in YEARS:
        r07 = d07.loc[y]
        hy = h[h.year == y]
        sy = sub[sub.year == y]
        ey = ex[ex.year == y]
        wy = win[win.year == y]

        our_sub = wmean(sy.subgeo_pp, sy.gbv)
        our_size = wmean(hy.unit_size_pp, hy.gbv_busd)
        our_los = wmean(hy.los_mix_pp, hy.gbv_busd)
        our_geo4 = wmean(hy.geo_mix_pp, hy.gbv_busd)
        core = wmean(ey.core, ey.gbv)
        resid = wmean(ey.residual, ey.gbv)

        plug = float(r07.pricing_and_subregional_mix_pp)
        within = float(r07.within_region_exfx_pp)
        implied_task = plug - our_sub
        implied_rebased = within - our_size - our_los - our_sub

        row = {
            "year": y,
            # --- the company-side (10-K) decomposition, verbatim from 07 ---
            "adr_yoy_pct_10k": float(r07.adr_yoy_pct),
            "geo_mix_pp_10k": float(r07.geo_mix_pp),
            "fx_pp_10k": float(r07.fx_pp),
            "interaction_pp_10k": float(r07.interaction_pp),
            "within_region_exfx_pp_10k": within,
            "size_mix_pp_10k": float(r07.size_mix_pp),
            "los_pp_10k": float(r07.of_which_los_pp),
            "plug_pricing_and_subregional_pp": plug,
            # --- 07's identities ---
            "id_geo_fx_int_within_minus_total_pp": (float(r07.geo_mix_pp) + float(r07.fx_pp)
                                                    + float(r07.interaction_pp) + within
                                                    - float(r07.adr_yoy_pct)),
            "id_plug_plus_size_los_minus_within_pp": (plug + float(r07.size_mix_pp)
                                                      + float(r07.of_which_los_pp) - within),
            "recon_gap_vs_independent_panel_pp": float(r07.reconciliation_gap_pp),
            "regional_exfx_independent_pp": float(r07.regional_exfx_independent_pp),
            # --- our engine's terms, GBV-weighted annual averages of the quarters ---
            "our_subgeo_pp": our_sub,
            "our_subgeo_NAM_pp": wmean(sy.part_NAM, sy.gbv),
            "our_subgeo_EMEA_pp": wmean(sy.part_EMEA, sy.gbv),
            "our_subgeo_LatAm_pp": wmean(sy.part_LatAm, sy.gbv),
            "our_subgeo_APAC_pp": wmean(sy.part_APAC, sy.gbv),
            "our_size_pp": our_size, "our_los_pp": our_los, "our_geo4_pp": our_geo4,
            "our_core_pp": core, "our_residual_pp": resid,
            # --- the reconciliation ---
            "implied_price_pp": implied_task,
            "implied_price_rebased_pp": implied_rebased,
            "subgeo_share_of_plug_pct": 100.0 * our_sub / plug if plug else float("nan"),
        }
        # within-region rows (the region's own term, before the GBV weight)
        for rg in ["NAM", "EMEA", "LatAm", "APAC"]:
            x = wy[wy.region == rg]
            row[f"our_mix_{rg}_pp"] = wmean(x.mix_pp, x.gbv)

        # government accommodation price comparators
        gy = gov_ann.loc[y]
        row["hicp_ea_cp112_pct"] = float(gy["hicp_CP112_EA_RCH_A"])
        row["hicp_eu27_cp112_pct"] = float(gy["hicp_CP112_EU27_2020_RCH_A"])
        row["us_cpi_lodging_pct"] = float(gy["bls_CUUR0000SEHB02"])
        row["uk_ons_accom_pct"] = float(gy["ons_cpi_112_accommodation_index"])
        sh = shares.loc[y]
        blend = sum(float(sh[k]) * float(gy[v]) for k, v in REGION_CPI.items())
        row["gbv_wtd_accom_cpi_pct"] = blend
        row["price_minus_blend_pp"] = implied_task - blend
        rows.append(row)

    out = pd.DataFrame(rows)
    meta = {
        "note_identity": ("07's within_region_exfx is DEFINED as adr_yoy - geo - fx - interaction and the plug "
                          "as within - size - LOS, so both identities close to machine precision by "
                          "construction; the only non-trivial check in that file is recon_gap_vs_"
                          "independent_panel_pp, the nights-weighted regional ex-FX built from the 10-K in 03."),
    }
    return out, meta


# ----------------------------------------------------------------------------- B. EMEA quarterly
def emea_hicp_panel(gov: pd.DataFrame, contrib: pd.DataFrame, include_turkey: bool) -> pd.Series:
    """Panel-share-weighted EMEA accommodation CPI, y/y %, renormalised over covered countries."""
    out = {}
    for q, x in contrib[contrib.region == "EMEA"].groupby("quarter"):
        if q not in gov.index:
            continue
        num = den = 0.0
        for _, r in x.iterrows():
            c = r.country
            if c == TURKEY and not include_turkey:
                continue
            col = HICP_MAP.get(c)
            if col is None or col not in gov.columns:
                continue
            v = gov.loc[q, col]
            if pd.isna(v):
                continue
            num += float(r.share_base) * float(v); den += float(r.share_base)
        out[q] = num / den if den > 0 else float("nan")
    return pd.Series(out)


def emea_panel_coverage(gov: pd.DataFrame, contrib: pd.DataFrame, q: str) -> float:
    x = contrib[(contrib.region == "EMEA") & (contrib.quarter == q)]
    den = sum(float(r.share_base) for _, r in x.iterrows()
              if r.country != TURKEY and HICP_MAP.get(r.country) in gov.columns)
    return 100.0 * den / float(x.share_base.sum())


def m2_emea_price_yoy() -> pd.DataFrame:
    """Median listed/quoted nightly price of established listings, local currency, entire homes,
    y/y only where the SAME price basis exists in both quarters (listed_nightly vs listed_nightly)."""
    d = pd.read_csv(M2)
    d = d[(d.market.isin(["rome", "paris", "barcelona", "london"]))
          & (d.variant == "entire_home") & (d.age_field == "first_review")]
    # one observation per market-quarter-basis: the latest dump in the quarter
    d = d.sort_values("dump_date").groupby(["market", "quarter", "price_basis"], as_index=False).last()
    d["q"] = d.quarter.map(C.qlabel_to_period)
    rows = []
    for (mk, basis), x in d.groupby(["market", "price_basis"]):
        x = x.set_index("q").sort_index()
        for q, r in x.iterrows():
            prev = q - 4
            if prev in x.index:
                p0, p1 = float(x.loc[prev, "median_old"]), float(r.median_old)
                rows.append({"market": mk, "quarter": r.quarter, "price_basis": basis,
                             "median_old_prev": p0, "median_old": p1,
                             "yoy_pct": 100.0 * (p1 / p0 - 1.0),
                             "n_old_prev": int(x.loc[prev, "n_old"]), "n_old": int(r.n_old)})
    return pd.DataFrame(rows)


def emea_quarterly() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    wide = pd.read_csv(REGIONAL_WIDE).set_index("quarter")
    win = pd.read_csv(WITHIN)
    h = pd.read_csv(H_COMPONENTS).set_index("quarter")
    gov = load_gov()
    contrib = pd.read_csv(CONTRIB)

    mix = win[win.region == "EMEA"].set_index("quarter").mix_pp
    hicp_ea = gov["hicp_CP112_EA_RCH_A"]
    hicp_eu = gov["hicp_CP112_EU27_2020_RCH_A"]
    panel = emea_hicp_panel(gov, contrib, include_turkey=False)
    panel_tr = emea_hicp_panel(gov, contrib, include_turkey=True)

    m2 = m2_emea_price_yoy()
    m2_by_q = {}
    for q, x in m2.groupby("quarter"):
        m2_by_q[q] = x

    rows = []
    for q in EMEA_Q10:
        disc = float(wide.loc[q, "adr_yoy_exfx_emea_pct"])
        mx = float(mix.loc[q])
        size = float(h.loc[q, "unit_size_pp"]); los = float(h.loc[q, "los_mix_pp"])
        implied = disc - mx
        implied_ex = disc - mx - size - los
        mq = m2_by_q.get(q, pd.DataFrame())
        m2_rome = float(mq[mq.market == "rome"].yoy_pct.iloc[0]) if (len(mq) and (mq.market == "rome").any()) else np.nan
        m2_paris = float(mq[mq.market == "paris"].yoy_pct.iloc[0]) if (len(mq) and (mq.market == "paris").any()) else np.nan
        m2_med = float(np.nanmedian(mq.yoy_pct)) if len(mq) else np.nan
        rows.append({
            "quarter": q,
            "in_disclosed_7": q in EMEA_Q7,
            "disclosed_exfx_emea_pct": disc,
            "basis": ("disclosed whole point" if q in EMEA_Q7 else "constructed (reported less modelled FX)"),
            "our_emea_mix_pp": mx,
            "global_unit_size_pp": size, "global_los_pp": los,
            "implied_within_country_price_pp": implied,
            "implied_price_ex_sizelos_pp": implied_ex,
            "hicp_ea_cp112_pct": float(hicp_ea.loc[q]),
            "hicp_eu27_cp112_pct": float(hicp_eu.loc[q]),
            "hicp_emea_panelwtd_pct": float(panel.get(q, np.nan)),
            "hicp_emea_panelwtd_inclTR_pct": float(panel_tr.get(q, np.nan)),
            "panel_hicp_coverage_pct": emea_panel_coverage(gov, contrib, q),
            "m2_rome_yoy_pct": m2_rome, "m2_paris_yoy_pct": m2_paris, "m2_median_yoy_pct": m2_med,
        })
    out = pd.DataFrame(rows)
    out["resid_vs_hicp_ea_pp"] = out.implied_within_country_price_pp - out.hicp_ea_cp112_pct
    out["resid_vs_panel_pp"] = out.implied_within_country_price_pp - out.hicp_emea_panelwtd_pct
    out["resid_ex_sizelos_vs_panel_pp"] = out.implied_price_ex_sizelos_pp - out.hicp_emea_panelwtd_pct
    out["resid_vs_m2_pp"] = out.implied_within_country_price_pp - out.m2_median_yoy_pct
    # counterfactual: the same reconciliation with the mix term set to zero -- does our mix help or hurt?
    out["resid_zeromix_vs_panel_pp"] = out.disclosed_exfx_emea_pct - out.hicp_emea_panelwtd_pct
    out["resid_zeromix_ex_sizelos_vs_panel_pp"] = (out.disclosed_exfx_emea_pct - out.global_unit_size_pp
                                                   - out.global_los_pp - out.hicp_emea_panelwtd_pct)

    s7 = out[out.in_disclosed_7]
    stats = {}
    for col in ["resid_vs_hicp_ea_pp", "resid_vs_panel_pp", "resid_zeromix_vs_panel_pp",
                "resid_ex_sizelos_vs_panel_pp", "resid_zeromix_ex_sizelos_vs_panel_pp", "resid_vs_m2_pp"]:
        for lab, frame in (("n7", s7), ("n10", out)):
            v = frame[col].dropna()
            stats[f"{col}|{lab}"] = {"n": int(len(v)), "mean": float(v.mean()) if len(v) else np.nan,
                                     "sd": float(v.std(ddof=1)) if len(v) > 1 else np.nan,
                                     "mae": float(v.abs().mean()) if len(v) else np.nan}
    # does the mix track the part of EMEA ex-FX that accommodation CPI does not explain?
    for lab, frame in (("n7", s7), ("n10", out)):
        gap = frame.disclosed_exfx_emea_pct - frame.hicp_emea_panelwtd_pct
        x = frame.our_emea_mix_pp.to_numpy(float); yv = gap.to_numpy(float)
        slope = float(np.polyfit(x, yv, 1)[0])            # 1.0 is the scale the identity implies
        stats[f"corr_mix_vs_cpi_gap|{lab}"] = {"n": int(len(frame)),
                                               "mean": float(np.corrcoef(x, yv)[0, 1]),
                                               "sd": np.nan, "mae": np.nan}
        stats[f"slope_cpigap_on_mix|{lab}"] = {"n": int(len(frame)), "mean": slope,
                                               "sd": np.nan, "mae": np.nan}
    return out, m2, stats


# ----------------------------------------------------------------------------- main
def main() -> int:
    pd.set_option("display.width", 250)
    ann, meta = annual()
    emea, m2, stats = emea_quarterly()

    OUT.mkdir(parents=True, exist_ok=True)
    ann.to_csv(OUT / "reconcile_annual.csv", index=False)
    emea.to_csv(OUT / "reconcile_emea_quarterly.csv", index=False)

    print("=" * 118)
    print("A.  ANNUAL RECONCILIATION — our sub-regional mix inside the 10-K plug (pp of ADR y/y)")
    print("=" * 118)
    cols = ["year", "adr_yoy_pct_10k", "geo_mix_pp_10k", "fx_pp_10k", "interaction_pp_10k",
            "within_region_exfx_pp_10k", "size_mix_pp_10k", "los_pp_10k",
            "plug_pricing_and_subregional_pp"]
    print("\n-- the company-side decomposition (07_full_decomposition.csv) --")
    print(ann[cols].round(3).to_string(index=False))

    print("\n-- 07's identities --")
    print(ann[["year", "id_geo_fx_int_within_minus_total_pp", "id_plug_plus_size_los_minus_within_pp",
               "within_region_exfx_pp_10k", "regional_exfx_independent_pp",
               "recon_gap_vs_independent_panel_pp"]].round(4).to_string(index=False))
    print("   NOTE:", meta["note_identity"])

    print("\n-- our terms (GBV-weighted annual averages of the quarterly terms) --")
    print(ann[["year", "our_subgeo_pp", "our_subgeo_NAM_pp", "our_subgeo_EMEA_pp", "our_subgeo_LatAm_pp",
               "our_subgeo_APAC_pp", "our_mix_NAM_pp", "our_mix_EMEA_pp", "our_mix_LatAm_pp",
               "our_mix_APAC_pp"]].round(3).to_string(index=False))
    print(ann[["year", "our_size_pp", "our_los_pp", "our_geo4_pp", "our_residual_pp",
               "our_core_pp"]].round(3).to_string(index=False))

    print("\n-- the reconciliation: does the sub-regional term fit inside the plug? --")
    print(ann[["year", "plug_pricing_and_subregional_pp", "our_subgeo_pp", "implied_price_pp",
               "implied_price_rebased_pp", "our_core_pp", "subgeo_share_of_plug_pct"]]
          .round(3).to_string(index=False))

    print("\n-- price remainder vs government accommodation price indices (y/y %) --")
    print(ann[["year", "implied_price_pp", "hicp_ea_cp112_pct", "hicp_eu27_cp112_pct", "us_cpi_lodging_pct",
               "uk_ons_accom_pct", "gbv_wtd_accom_cpi_pct", "price_minus_blend_pp"]]
          .round(2).to_string(index=False))

    print()
    print("=" * 118)
    print("B.  EMEA QUARTERLY RECONCILIATION (disclosed ex-FX ADR y/y = country mix + within-country price + size/LOS)")
    print("=" * 118)
    print(emea[["quarter", "in_disclosed_7", "disclosed_exfx_emea_pct", "our_emea_mix_pp",
                "implied_within_country_price_pp", "global_unit_size_pp", "global_los_pp",
                "implied_price_ex_sizelos_pp"]].round(3).to_string(index=False))
    print("\n-- price proxies and residuals (pp) --")
    print(emea[["quarter", "implied_within_country_price_pp", "hicp_ea_cp112_pct", "hicp_emea_panelwtd_pct",
                "panel_hicp_coverage_pct", "m2_median_yoy_pct", "resid_vs_hicp_ea_pp", "resid_vs_panel_pp",
                "resid_ex_sizelos_vs_panel_pp", "resid_vs_m2_pp"]].round(2).to_string(index=False))

    print("\n-- residual summary (mean / sd / MAE; n small, stated) --")
    for k, v in stats.items():
        col, lab = k.split("|")
        if col.startswith("corr") or col.startswith("slope"):
            print(f"   {col:38s} {lab}: n {v['n']:2d}  {'r' if col[0] == 'c' else 'b'} {v['mean']:+5.2f}")
        else:
            print(f"   {col:38s} {lab}: n {v['n']:2d}  mean {v['mean']:+6.2f}pp  sd {v['sd']:5.2f}pp  "
                  f"MAE {v['mae']:5.2f}pp")

    print("\n-- M2 like-for-like price y/y, local currency, entire homes, same price basis both quarters --")
    print(m2.round(2).to_string(index=False))

    print(f"\nwrote {OUT / 'reconcile_annual.csv'}")
    print(f"wrote {OUT / 'reconcile_emea_quarterly.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
