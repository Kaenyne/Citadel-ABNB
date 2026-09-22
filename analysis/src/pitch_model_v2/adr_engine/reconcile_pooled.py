"""adr_engine / reconcile_pooled.py — mitigation C: raise n on the mix-term reconciliation.

Registered in docs/pitch-model-v2/lines/adr_v2_mitigation_C_pooled_reconciliation.md §1 BEFORE this file was
first run.  Nothing here is fitted; no window, weight, country or exclusion was chosen after seeing a result.

upgrade 3 §B reconciled our within-EMEA country-mix term to the disclosed EMEA ex-FX ADR and got a slope of
+1.09 against the identity's 1.0, r +0.48, on n 7 (p 0.27).  Right sign, right scale, no significance, and the
only thing wrong with it was n.  Two honest ways to raise n:

  (a) POOLED ACROSS REGIONS.  Stack all four regions' disclosed ex-FX ADR against our within-region mix:

          y_{r,t} = disclosed exfx_{r,t} - CPI proxy_{r,t} - global size_t - global LOS_t = a_r + b mix_{r,t} + e

      Region fixed effects, cluster-by-region (CRV1 = Arellano, i.e. HAC within region) as the primary SE, plus
      iid / HC1 / Newey-West(3) within region / a fully enumerated wild cluster bootstrap (2^4 = 16 draws).
      Two samples: cells whose ex-FX is a DISCLOSED whole point (the verdict sample) and all chained cells.
      Variants: no fixed effects, no CPI adjustment, neither, and a second CPI specification.

  (b) MONTHLY EMEA.  The same share-shift arithmetic at monthly frequency off Eurostat platform nights
      (2018-01..2026-03), checked against the published quarterly Eurostat-weighted EMEA mix and against the
      12-month change in the disclosed EMEA CPI gap.  n rises for the MIX OBJECT, not for the test of it: the
      target is published quarterly and only quarterly.

Outputs
  data/processed/pitch_model_v2/adr_engine/reconcile_pooled_cells.csv
  data/processed/pitch_model_v2/adr_engine/reconcile_pooled_cpi_proxy.csv
  data/processed/pitch_model_v2/adr_engine/reconcile_pooled_regressions.csv
  data/processed/pitch_model_v2/adr_engine/reconcile_pooled_emea_monthly.csv
  data/processed/pitch_model_v2/adr_engine/reconcile_pooled_emea_monthly_check.csv

Run
  cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.reconcile_pooled
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy import stats as sps

from pitch_model_v2.adr_engine import config as C
from pitch_model_v2.adr_engine.geomix_eurostat import ISO_TO_COUNTRY

ROOT, OUT = C.ROOT, C.OUT

WITHIN = OUT / "geomix_within_region.csv"
CONTRIB = OUT / "geomix_country_contributions.csv"
REGIONAL_WIDE = ROOT / "data/processed/adr/04_regional_quarterly_wide.csv"
LETTER_PANEL = ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv"
GOVDATA_Q = ROOT / "data/processed/govdata/P/P_feature_quarterly_panel.csv"
GOVDATA_M = ROOT / "data/processed/govdata/P/P_feature_monthly_yoy.csv"
EUROSTAT_MONTHLY = ROOT / "data/processed/eurostat_platform_nights_monthly.csv"
PRICES = OUT / "country_price_levels_usd.csv"
EUROSTAT_QMIX = OUT / "geomix_eurostat_emea_mix.csv"

REGION_KEY = {"NAM": "na", "EMEA": "emea", "LatAm": "latam", "APAC": "apac"}
REGIONS = ["NAM", "EMEA", "LatAm", "APAC"]

# --- registered §1.2 spec P1: one government accommodation-price series per PANEL country -------------------
COUNTRY_CPI = {
    # NAM
    "united-states": "bls_CUUR0000SEHB02",
    "canada": "statcan_cpi_traveller_accommodation",
    # EMEA (HICP CP112 by country; ONS CPI 11.2 for the UK)
    "italy": "hicp_CP112_IT_RCH_A", "spain": "hicp_CP112_ES_RCH_A", "france": "hicp_CP112_FR_RCH_A",
    "portugal": "hicp_CP112_PT_RCH_A", "greece": "hicp_CP112_EL_RCH_A", "ireland": "hicp_CP112_IE_RCH_A",
    "hungary": "hicp_CP112_HU_RCH_A", "czech-republic": "hicp_CP112_CZ_RCH_A",
    "germany": "hicp_CP112_DE_RCH_A", "belgium": "hicp_CP112_BE_RCH_A", "austria": "hicp_CP112_AT_RCH_A",
    "the-netherlands": "hicp_CP112_NL_RCH_A", "denmark": "hicp_CP112_DK_RCH_A",
    "norway": "hicp_CP112_NO_RCH_A", "switzerland": "hicp_CP112_CH_RCH_A",
    "sweden": "hicp_CP112_SE_RCH_A", "croatia": "hicp_CP112_HR_RCH_A", "poland": "hicp_CP112_PL_RCH_A",
    "united-kingdom": "ons_cpi_112_accommodation_index",
    "turkey": "hicp_CP112_TR_RCH_A",            # EXCLUDED from the blend (hyperinflation) - see EXCLUDE
    # LatAm
    "brazil": "ibge_ipca_hospedagem_yoy12m",
    # APAC
    "australia": "abs_cpi_30033_Q",
    "new-zealand": "nz_cpi_CPIQ.SE9096_accommodation_services_nan",
}
EXCLUDE = {"turkey"}
# --- registered §1.2 spec P2: the four frozen headline series (reconcile.REGION_CPI) ------------------------
REGION_CPI_P2 = {"NAM": "bls_CUUR0000SEHB02", "EMEA": "hicp_CP112_EA_RCH_A",
                 "LatAm": "ibge_ipca_hospedagem_yoy12m", "APAC": "abs_cpi_30033_Q"}

PASS_B_LO, PASS_B_HI, PASS_P = 0.5, 1.5, 0.10       # registered pass line (a)
PASS_MAE_MONTHLY = 0.15                              # registered pass line (b1), pp
NW_LAGS = 3


# ============================================================ regression machinery
def _bartlett(L: int, j: int) -> float:
    return 1.0 - j / (L + 1.0)


def ols(y: np.ndarray, X: np.ndarray, groups: np.ndarray, order: np.ndarray | None = None) -> dict:
    """OLS with the mix coefficient first in X.  Returns b and four SEs (iid, HC1, CRV1 by group, NW(3) within
    group), r2, and the machinery needed for the wild cluster bootstrap."""
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta
    dof = n - k
    s2 = float(u @ u) / dof
    V_iid = s2 * XtX_inv
    # HC1
    meat = (X * (u ** 2)[:, None]).T @ X
    V_hc1 = XtX_inv @ meat @ XtX_inv * n / dof
    # CRV1 (Arellano): arbitrary serial correlation and heteroskedasticity within region
    gs = np.unique(groups)
    G = len(gs)
    meat_c = np.zeros((k, k))
    for g in gs:
        m = groups == g
        sg = X[m].T @ u[m]
        meat_c += np.outer(sg, sg)
    c_small = (G / (G - 1.0)) * ((n - 1.0) / dof) if G > 1 else 1.0
    V_crv = XtX_inv @ meat_c @ XtX_inv * c_small
    # Newey-West (Bartlett, NW_LAGS) computed inside each group, summed
    meat_nw = np.zeros((k, k))
    for g in gs:
        m = groups == g
        Xg, ug = X[m], u[m]
        if order is not None:
            o = np.argsort(order[m]); Xg, ug = Xg[o], ug[o]
        hg = Xg * ug[:, None]
        meat_nw += hg.T @ hg
        for j in range(1, min(NW_LAGS, len(ug) - 1) + 1):
            Gj = hg[j:].T @ hg[:-j]
            meat_nw += _bartlett(NW_LAGS, j) * (Gj + Gj.T)
    V_nw = XtX_inv @ meat_nw @ XtX_inv * n / dof
    ybar = y.mean()
    r2 = 1.0 - float(u @ u) / float(((y - ybar) ** 2).sum())
    return {"beta": beta, "u": u, "XtX_inv": XtX_inv, "n": n, "k": k, "dof": dof, "G": G,
            "se_iid": float(np.sqrt(V_iid[0, 0])), "se_hc1": float(np.sqrt(V_hc1[0, 0])),
            "se_crv": float(np.sqrt(V_crv[0, 0])), "se_nw": float(np.sqrt(V_nw[0, 0])), "r2": r2}


def _crv_se(y, X, groups):
    return ols(y, X, groups)["se_crv"]


def wild_cluster_p(y: np.ndarray, X: np.ndarray, groups: np.ndarray, b0: float) -> tuple[float, int]:
    """Wild cluster bootstrap under the restricted null b = b0, Rademacher weights, ALL 2^G sign vectors
    enumerated (G = 4 -> 16 draws, smallest attainable p = 1/16 = 0.0625)."""
    fit = ols(y, X, groups)
    t_obs = (fit["beta"][0] - b0) / fit["se_crv"]
    # restricted fit: impose b = b0 by regressing (y - b0*mix) on the other columns
    y_r = y - b0 * X[:, 0]
    Z = X[:, 1:]
    bz = np.linalg.pinv(Z.T @ Z) @ (Z.T @ y_r)
    fitted_r = b0 * X[:, 0] + Z @ bz
    u_r = y - fitted_r
    gs = np.unique(groups)
    ts = []
    for signs in itertools.product([-1.0, 1.0], repeat=len(gs)):
        w = np.ones_like(y)
        for g, s in zip(gs, signs):
            w[groups == g] = s
        y_star = fitted_r + w * u_r
        f = ols(y_star, X, groups)
        ts.append(abs((f["beta"][0] - b0) / f["se_crv"]))
    ts = np.array(ts)
    return float((ts >= abs(t_obs) - 1e-12).mean()), len(ts)


def run_spec(df: pd.DataFrame, ycol: str, fe: bool, label: str, sample: str) -> dict:
    d = df.dropna(subset=[ycol, "mix_pp"]).copy()
    y = d[ycol].to_numpy(float)
    mix = d["mix_pp"].to_numpy(float)
    groups = d["region"].to_numpy()
    order = d["qi"].to_numpy(float)
    if fe:
        dummies = pd.get_dummies(d.region, dtype=float)
        X = np.column_stack([mix, dummies.to_numpy(float)])
        regs_with_var = int(sum(d[d.region == r].mix_pp.nunique() > 1 for r in d.region.unique()))
    else:
        X = np.column_stack([mix, np.ones(len(d))])
        regs_with_var = int(d.region.nunique())
    f = ols(y, X, groups, order)
    b = float(f["beta"][0])
    single = f["G"] < 2          # one region: clustering by region is undefined (the score sums to zero)
    if single:
        se = np.nan
        p0 = p1 = np.nan
        tcrit90 = tcrit95 = np.nan
        pw0, pw1, nboot = np.nan, np.nan, 0
    else:
        se = f["se_crv"]
        dof_c = max(f["G"] - 1, 1)
        p0 = 2 * (1 - sps.t.cdf(abs(b / se), dof_c))
        p1 = 2 * (1 - sps.t.cdf(abs((b - 1.0) / se), dof_c))
        tcrit90, tcrit95 = sps.t.ppf(0.95, dof_c), sps.t.ppf(0.975, dof_c)
        pw0, nboot = wild_cluster_p(y, X, groups, 0.0)
        pw1, _ = wild_cluster_p(y, X, groups, 1.0)
    # within-r2 (region-demeaned) for the FE specs
    if fe:
        yd = y - pd.Series(y).groupby(pd.Series(groups)).transform("mean").to_numpy()
        md = mix - pd.Series(mix).groupby(pd.Series(groups)).transform("mean").to_numpy()
        bw = float((md @ yd) / (md @ md))
        r2w = 1.0 - float(((yd - bw * md) ** 2).sum()) / float((yd ** 2).sum())
    else:
        r2w = np.nan
    # p on the other SE flavours, for the record
    p_iid = 2 * (1 - sps.t.cdf(abs(b / f["se_iid"]), f["dof"]))
    p_hc1 = 2 * (1 - sps.t.cdf(abs(b / f["se_hc1"]), f["dof"]))
    p_nw = 2 * (1 - sps.t.cdf(abs(b / f["se_nw"]), f["dof"]))
    # cluster by quarter (ADDED after registration; reported for completeness only)
    fq = ols(y, X, d["quarter"].to_numpy(), order)
    p_cq = 2 * (1 - sps.t.cdf(abs(b / fq["se_crv"]), max(fq["G"] - 1, 1)))
    return {"sample": sample, "spec": label, "fe": fe, "y": ycol, "n": int(f["n"]),
            "n_regions": int(f["G"]), "n_regions_with_variation": regs_with_var,
            "b": b, "se_cluster_region": se, "t_b0": b / se if not single else np.nan,
            "p_b0_cluster": p0, "p_b1_cluster": p1,
            "ci90_lo": b - tcrit90 * se, "ci90_hi": b + tcrit90 * se,
            "ci95_lo": b - tcrit95 * se, "ci95_hi": b + tcrit95 * se,
            "se_iid": f["se_iid"], "p_b0_iid": p_iid,
            "se_hc1": f["se_hc1"], "p_b0_hc1": p_hc1,
            "se_nw3": f["se_nw"], "p_b0_nw3": p_nw,
            "se_cluster_quarter": fq["se_crv"], "p_b0_cluster_quarter": p_cq,
            "p_b0_wildboot": pw0, "p_b1_wildboot": pw1, "n_wildboot": nboot,
            "r2": f["r2"], "r2_within": r2w,
            "pass_band": bool(PASS_B_LO <= b <= PASS_B_HI),
            "pass_p": bool(pd.notna(p0) and p0 <= PASS_P),
            "PASS": bool(PASS_B_LO <= b <= PASS_B_HI and pd.notna(p0) and p0 <= PASS_P)}


# ============================================================ (a) the pooled panel
def cpi_proxy(gov: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Spec P1: panel-share-weighted accommodation CPI by region-quarter, renormalised over covered countries."""
    c = pd.read_csv(CONTRIB)
    rows, wrows = [], []
    for (reg, q), x in c.groupby(["region", "quarter"]):
        if q not in gov.index:
            continue
        num = den = 0.0
        tot = float(x.share_base.sum())
        for _, r in x.iterrows():
            if r.country in EXCLUDE:
                continue
            col = COUNTRY_CPI.get(r.country)
            if col is None or col not in gov.columns:
                continue
            v = gov.loc[q, col]
            if pd.isna(v):
                continue
            num += float(r.share_base) * float(v)
            den += float(r.share_base)
            wrows.append({"region": reg, "quarter": q, "country": r.country, "series": col,
                          "share_base": float(r.share_base), "cpi_yoy_pct": float(v)})
        rows.append({"region": reg, "quarter": q, "cpi_p1_pct": num / den if den > 0 else np.nan,
                     "cpi_coverage_pct": 100.0 * den / tot if tot > 0 else np.nan,
                     "n_countries_covered": int((x.country.isin([k for k in COUNTRY_CPI if k not in EXCLUDE])).sum()),
                     "n_countries_panel": int(len(x))})
    return pd.DataFrame(rows), pd.DataFrame(wrows)


def cells() -> pd.DataFrame:
    w = pd.read_csv(WITHIN)[["region", "quarter", "mix_pp"]]
    wide = pd.read_csv(REGIONAL_WIDE).set_index("quarter")
    letter = pd.read_csv(LETTER_PANEL).set_index("quarter")
    h = pd.read_csv(ROOT / "data/processed/q3nowcast/H/adr_history_components.csv").set_index("quarter")
    gov = pd.read_csv(GOVDATA_Q, index_col=0)
    gov.index.name = "quarter"
    p1, weights = cpi_proxy(gov)

    rows = []
    for _, r in w.iterrows():
        reg, q = r.region, r.quarter
        key = REGION_KEY[reg]
        if q not in wide.index or q not in h.index or q not in gov.index:
            continue
        exfx = wide.loc[q, f"adr_yoy_exfx_{key}_pct"]
        basis = wide.loc[q, f"basis_adr_{key}"]
        if pd.isna(exfx):
            continue
        lv = letter.loc[q, f"{key}_adr_yoy_exfx_pct"] if q in letter.index else np.nan
        whole = abs(float(exfx) - round(float(exfx))) < 1e-6
        matches = pd.notna(lv) and abs(float(lv) - float(exfx)) < 1e-6
        disclosed = bool(basis == "disclosed-chained" and whole and matches)
        rows.append({
            "region": reg, "quarter": q, "qi": float(C.qlabel_to_period(q).ordinal),
            "mix_pp": float(r.mix_pp), "disclosed_exfx_pct": float(exfx), "basis_04": basis,
            "letter_exfx_pct": float(lv) if pd.notna(lv) else np.nan,
            "is_whole_point": whole, "matches_letter": bool(matches), "is_disclosed": disclosed,
            "in_chained_sample": bool(basis == "disclosed-chained"),
            "global_unit_size_pp": float(h.loc[q, "unit_size_pp"]),
            "global_los_pp": float(h.loc[q, "los_mix_pp"]),
            "cpi_p2_pct": float(gov.loc[q, REGION_CPI_P2[reg]]),
        })
    d = pd.DataFrame(rows).merge(p1, on=["region", "quarter"], how="left")
    d["y_full_p1"] = d.disclosed_exfx_pct - d.cpi_p1_pct - d.global_unit_size_pp - d.global_los_pp
    d["y_full_p2"] = d.disclosed_exfx_pct - d.cpi_p2_pct - d.global_unit_size_pp - d.global_los_pp
    d["y_nocpi"] = d.disclosed_exfx_pct - d.global_unit_size_pp - d.global_los_pp
    d["y_raw"] = d.disclosed_exfx_pct
    d["implied_within_country_price_pp"] = d.disclosed_exfx_pct - d.mix_pp
    d["resid_vs_cpi_p1_pp"] = d.implied_within_country_price_pp - d.cpi_p1_pct
    d["cpi_gap_p1_pp"] = d.disclosed_exfx_pct - d.cpi_p1_pct
    return d.sort_values(["region", "qi"]).reset_index(drop=True), weights


# ============================================================ (b) monthly EMEA
def monthly_mix() -> tuple[pd.DataFrame, pd.DataFrame]:
    m = pd.read_csv(EUROSTAT_MONTHLY, parse_dates=["month"])
    cols = [c for c in m.columns if c.endswith("_nights") and not c.startswith("eu27")]
    n = m.set_index("month")[cols].rename(columns=lambda c: c[:-7])
    iso = [i for i in ISO_TO_COUNTRY if i in n.columns]
    n = n[iso].rename(columns=ISO_TO_COUNTRY)

    pr = pd.read_csv(PRICES)
    lvl = pr.set_index("country").usd_level
    emea_med = float(pr[pr.region == "EMEA"].usd_level.median())
    P = pd.Series({c: float(lvl.get(c, emea_med)) for c in n.columns})
    imputed = [c for c in n.columns if c not in lvl.index]

    rows = []
    idx = n.index
    for i, t in enumerate(idx):
        if i < 12:
            continue
        base = idx[i - 12]
        if (t.to_period("M") - 12) != base.to_period("M"):
            continue
        n0, n1 = n.loc[base], n.loc[t]
        ok = n0.notna() & n1.notna() & (n0 > 0)
        n0, n1, p = n0[ok], n1[ok], P[ok.index[ok]]
        s0 = n0 / n0.sum()
        gr = n1 / n0 - 1.0
        g_reg = float((s0 * gr).sum())
        num = float((s0 * (1 + gr) * p).sum())
        den = (1 + g_reg) * float((s0 * p).sum())
        rows.append({"month": t.strftime("%Y-%m"), "q": str(t.to_period("Q")),
                     "mix_pp": (num / den - 1) * 100, "region_growth_pct": g_reg * 100,
                     "n_countries": int(ok.sum()),
                     "share_imputed_price": float(s0[[c for c in s0.index if c in imputed]].sum())})
    mm = pd.DataFrame(rows)
    mm["mix_pp_d12"] = mm.mix_pp - mm.mix_pp.shift(12)
    mm.loc[mm.index[:12], "mix_pp_d12"] = np.nan

    # like-for-like control: same 18 countries, same data, QUARTERLY arithmetic with a 4-quarter lag
    nq = n.copy()
    nq["q"] = nq.index.to_period("Q")
    full = nq.groupby("q").size() == 3
    qn = nq.groupby("q").sum(numeric_only=True).loc[full[full].index]
    qrows = []
    for i, q in enumerate(qn.index):
        if i < 4 or (qn.index[i - 4] != q - 4):
            continue
        n0, n1 = qn.loc[q - 4], qn.loc[q]
        ok = n0.notna() & n1.notna() & (n0 > 0)
        n0, n1, p = n0[ok], n1[ok], P[ok.index[ok]]
        s0 = n0 / n0.sum(); gr = n1 / n0 - 1.0
        g_reg = float((s0 * gr).sum())
        num = float((s0 * (1 + gr) * p).sum()); den = (1 + g_reg) * float((s0 * p).sum())
        qrows.append({"q": str(q), "quarter": C.period_to_qlabel(q), "mix_pp_q18": (num / den - 1) * 100,
                      "region_growth_pct": g_reg * 100})
    return mm, pd.DataFrame(qrows)


def monthly_check(mm: pd.DataFrame, q18: pd.DataFrame, cellsdf: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    pub = pd.read_csv(EUROSTAT_QMIX)
    pub = pub[(pub.share_src == "eurostat") & (pub.growth_src == "eurostat") & (pub.price_basis == "median")]
    pub = pub[["quarter", "q", "mix_pp"]].rename(columns={"mix_pp": "mix_pp_published_q"})

    qm = mm.groupby("q").agg(mix_pp_monthly_qavg=("mix_pp", "mean"),
                             mix_d12_monthly_qavg=("mix_pp_d12", "mean"),
                             n_months=("mix_pp", "size")).reset_index()
    qm = qm[qm.n_months == 3]
    qm["quarter"] = [C.period_to_qlabel(pd.Period(x, freq="Q")) for x in qm.q]
    chk = qm.merge(pub, on=["quarter", "q"], how="left").merge(q18, on=["q", "quarter"], how="left")

    gov = pd.read_csv(GOVDATA_Q, index_col=0)
    e = cellsdf[cellsdf.region == "EMEA"].set_index("quarter")
    chk["disclosed_exfx_emea_pct"] = chk.quarter.map(e.disclosed_exfx_pct)
    chk["is_disclosed"] = chk.quarter.map(e.is_disclosed).fillna(False)
    chk["in_chained_sample"] = chk.quarter.map(e.in_chained_sample).fillna(False)
    chk["hicp_ea_cp112_pct"] = chk.quarter.map(gov["hicp_CP112_EA_RCH_A"])
    chk["cpi_gap_pp"] = chk.disclosed_exfx_emea_pct - chk.hicp_ea_cp112_pct
    chk = chk.sort_values("q").reset_index(drop=True)
    chk["cpi_gap_d4_pp"] = chk.cpi_gap_pp - chk.cpi_gap_pp.shift(4)
    chk["d_quarter_lag4_ok"] = [
        (i >= 4) and (pd.Period(chk.q[i], "Q") - 4 == pd.Period(chk.q[i - 4], "Q")) if i >= 4 else False
        for i in range(len(chk))]
    chk.loc[~chk.d_quarter_lag4_ok, "cpi_gap_d4_pp"] = np.nan

    chk["diff_vs_published_pp"] = chk.mix_pp_monthly_qavg - chk.mix_pp_published_q
    chk["diff_vs_q18_pp"] = chk.mix_pp_monthly_qavg - chk.mix_pp_q18
    pan = cellsdf[cellsdf.region == "EMEA"].set_index("quarter").mix_pp
    chk["mix_pp_panel_q"] = chk.quarter.map(pan)
    chk["diff_vs_panel_pp"] = chk.mix_pp_monthly_qavg - chk.mix_pp_panel_q

    res = {}
    for lab, col in (("published_eurostat_eurostat", "diff_vs_published_pp"), ("like_for_like_q18", "diff_vs_q18_pp")):
        v = chk[col].dropna()
        res[f"b1|{lab}"] = {"n": int(len(v)), "mae": float(v.abs().mean()) if len(v) else np.nan,
                            "mean": float(v.mean()) if len(v) else np.nan,
                            "max_abs": float(v.abs().max()) if len(v) else np.nan,
                            "corr": float(np.corrcoef(chk.dropna(subset=[col, "mix_pp_monthly_qavg"]).mix_pp_monthly_qavg,
                                                      chk.dropna(subset=[col]).mix_pp_monthly_qavg - chk.dropna(subset=[col])[col])[0, 1])
                            if len(v) > 2 else np.nan}
    # DIAGNOSTICS, not part of the registered lines: the b1 gap split at the COVID break, and whether the
    # monthly-derived mix agrees with the panel-derived EMEA mix the pooled leg actually uses.
    post = chk[chk.q >= "2023Q1"]
    v = post.diff_vs_published_pp.dropna()
    res["b1_diag|published_2023Q1_on"] = {"n": int(len(v)), "mae": float(v.abs().mean()),
                                          "mean": float(v.mean()), "max_abs": float(v.abs().max()), "corr": np.nan}
    v = chk[chk.q < "2023Q1"].diff_vs_published_pp.dropna()
    res["b1_diag|published_pre2023"] = {"n": int(len(v)), "mae": float(v.abs().mean()),
                                        "mean": float(v.mean()), "max_abs": float(v.abs().max()), "corr": np.nan}
    v = chk.dropna(subset=["mix_pp_monthly_qavg", "mix_pp_panel_q"])
    res["b1_diag|vs_panel_mix"] = {"n": int(len(v)), "mae": float((v.diff_vs_panel_pp).abs().mean()),
                                   "mean": float(v.diff_vs_panel_pp.mean()),
                                   "max_abs": float(v.diff_vs_panel_pp.abs().max()),
                                   "corr": float(np.corrcoef(v.mix_pp_monthly_qavg, v.mix_pp_panel_q)[0, 1])}
    for lab, sub in (("all_chained", chk[chk.in_chained_sample]), ("disclosed_only", chk[chk.is_disclosed])):
        v = sub.dropna(subset=["mix_d12_monthly_qavg", "cpi_gap_d4_pp"])
        if len(v) > 2:
            r = float(np.corrcoef(v.mix_d12_monthly_qavg, v.cpi_gap_d4_pp)[0, 1])
            b = float(np.polyfit(v.mix_d12_monthly_qavg, v.cpi_gap_d4_pp, 1)[0])
        else:
            r = b = np.nan
        res[f"b2|{lab}"] = {"n": int(len(v)), "corr": r, "slope": b}
        v2 = sub.dropna(subset=["mix_pp_monthly_qavg", "cpi_gap_pp"])
        res[f"b2_levels|{lab}"] = {"n": int(len(v2)),
                                   "corr": float(np.corrcoef(v2.mix_pp_monthly_qavg, v2.cpi_gap_pp)[0, 1]) if len(v2) > 2 else np.nan,
                                   "slope": float(np.polyfit(v2.mix_pp_monthly_qavg, v2.cpi_gap_pp, 1)[0]) if len(v2) > 2 else np.nan}
    return chk, res


# ============================================================ main
def main() -> int:
    pd.set_option("display.width", 250)
    OUT.mkdir(parents=True, exist_ok=True)

    d, weights = cells()
    d.to_csv(OUT / "reconcile_pooled_cells.csv", index=False)
    weights.to_csv(OUT / "reconcile_pooled_cpi_proxy.csv", index=False)

    disc = d[d.is_disclosed]
    chained = d[d.in_chained_sample]

    specs = [("primary: FE + CPI P1 + size/LOS", "y_full_p1", True),
             ("no FE: CPI P1 + size/LOS", "y_full_p1", False),
             ("no CPI: FE + size/LOS", "y_nocpi", True),
             ("neither: no FE, no CPI, no size/LOS", "y_raw", False),
             ("CPI P2 (headline series): FE + size/LOS", "y_full_p2", True),
             ("CPI P2, no FE", "y_full_p2", False),
             ("FE + CPI P1, size/LOS NOT removed", "cpi_gap_p1_pp", True)]
    seen, rows = set(), []
    for lab, ycol, fe in specs:
        if (lab, ycol, fe) in seen:
            continue
        seen.add((lab, ycol, fe))
        for sname, frame in (("disclosed_only", disc), ("all_chained", chained)):
            if frame.mix_pp.notna().sum() < 5:
                continue
            rows.append(run_spec(frame, ycol, fe, lab, sname))
    # leave-one-region-out and window robustness on the PRIMARY spec, disclosed sample
    for r in REGIONS:
        sub = disc[disc.region != r]
        if sub.region.nunique() >= 2 and len(sub) >= 6:
            rows.append(run_spec(sub, "y_full_p1", True, f"primary, drop {r}", "disclosed_only"))
    w = disc[disc.qi >= float(C.qlabel_to_period("4Q24").ordinal)]
    rows.append(run_spec(w, "y_full_p1", True, "primary, 4Q24+ only (common window)", "disclosed_only"))
    e = disc[disc.region == "EMEA"]
    rows.append(run_spec(e, "y_full_p1", False, "EMEA alone, primary y (no FE possible)", "disclosed_only"))
    rows.append(run_spec(e, "cpi_gap_p1_pp", False, "EMEA alone, upgrade-3 y (gap on mix), all 9",
                         "disclosed_only"))
    rows.append(run_spec(e[e.qi >= float(C.qlabel_to_period("4Q24").ordinal)], "cpi_gap_p1_pp", False,
                         "EMEA alone, upgrade-3 y and window (n 7 replication)", "disclosed_only"))
    reg = pd.DataFrame(rows)
    reg.to_csv(OUT / "reconcile_pooled_regressions.csv", index=False)

    mm, q18 = monthly_mix()
    mm.to_csv(OUT / "reconcile_pooled_emea_monthly.csv", index=False)
    chk, mres = monthly_check(mm, q18, d)
    chk.to_csv(OUT / "reconcile_pooled_emea_monthly_check.csv", index=False)

    # -------------------------------------------------------- printing
    print("=" * 126)
    print("A.  POOLED ACROSS REGIONS — cell inventory (which ex-FX prints are disclosed whole points?)")
    print("=" * 126)
    inv = d.pivot(index="quarter", columns="region", values="is_disclosed")
    inv = inv.reindex(sorted(inv.index, key=lambda q: C.qlabel_to_period(q).ordinal))
    flag = d.copy()
    flag["f"] = np.where(flag.is_disclosed, "DISC", np.where(flag.in_chained_sample, "chain", "modl"))
    fv = flag.pivot(index="quarter", columns="region", values="f")
    fv = fv.reindex(sorted(fv.index, key=lambda q: C.qlabel_to_period(q).ordinal))
    print(fv.to_string())
    print(f"\n   cells with a disclosed whole point : n {int(d.is_disclosed.sum()):3d}"
          f"   by region: {d[d.is_disclosed].region.value_counts().to_dict()}")
    print(f"   cells on the chained basis         : n {int(d.in_chained_sample.sum()):3d}"
          f"   by region: {d[d.in_chained_sample].region.value_counts().to_dict()}")

    print("\n-- the panel (disclosed cells) --")
    cols = ["region", "quarter", "disclosed_exfx_pct", "mix_pp", "cpi_p1_pct", "cpi_coverage_pct",
            "global_unit_size_pp", "global_los_pp", "y_full_p1", "implied_within_country_price_pp",
            "resid_vs_cpi_p1_pp"]
    print(disc[cols].round(3).to_string(index=False))

    print("\n-- CPI proxy P1 coverage by region (share of panel stays with a government accommodation series) --")
    cov = d.groupby("region").cpi_coverage_pct.agg(["min", "mean", "max"]).round(1)
    print(cov.to_string())

    print("\n" + "=" * 126)
    print("A.  REGRESSIONS   y = a_r + b*mix + e   (identity implies b = 1; pass line b in [0.5,1.5] and p<=0.10)")
    print("=" * 126)
    show = ["sample", "spec", "n", "b", "se_cluster_region", "p_b0_cluster", "p_b1_cluster",
            "ci90_lo", "ci90_hi", "r2", "r2_within", "PASS"]
    print(reg[show].round(3).to_string(index=False))
    print("\n-- where the slope comes from: within-region OLS of the primary y on mix, disclosed cells --")
    wr = []
    for r in REGIONS:
        x = disc[disc.region == r]
        if len(x) >= 3 and x.mix_pp.nunique() > 1:
            bb, aa = np.polyfit(x.mix_pp, x.y_full_p1, 1)
            rr = float(np.corrcoef(x.mix_pp, x.y_full_p1)[0, 1])
        else:
            bb = rr = np.nan
        wr.append({"region": r, "n": len(x), "mix_min": x.mix_pp.min(), "mix_max": x.mix_pp.max(),
                   "mix_sd": x.mix_pp.std(), "y_sd": x.y_full_p1.std(), "b_region": bb, "r_region": rr,
                   "cpi_coverage_mean_pct": x.cpi_coverage_pct.mean()})
    print(pd.DataFrame(wr).round(3).to_string(index=False))

    print("\n-- influence: leave-one-CELL-out jackknife on the primary spec (disclosed cells, 23 refits) --")
    jb = []
    for i in range(len(disc)):
        sub = disc.drop(disc.index[i])
        f = run_spec(sub, "y_full_p1", True, "jk", "disclosed_only")
        jb.append({"dropped": f"{disc.iloc[i].region} {disc.iloc[i].quarter}", "b": f["b"],
                   "p": f["p_b0_cluster"]})
    jk = pd.DataFrame(jb).sort_values("b")
    print(f"   b range {jk.b.min():+.3f} .. {jk.b.max():+.3f}   median {jk.b.median():+.3f}   "
          f"cells whose removal breaks the pass line: "
          f"{int(((jk.b < PASS_B_LO) | (jk.b > PASS_B_HI) | (jk.p > PASS_P)).sum())} of {len(jk)}")
    print(jk.head(4).round(3).to_string(index=False))
    print(jk.tail(3).round(3).to_string(index=False))

    print("\n-- the same b under every SE flavour (p on H0: b = 0) --")
    show2 = ["sample", "spec", "n", "b", "se_iid", "p_b0_iid", "se_hc1", "p_b0_hc1", "se_nw3", "p_b0_nw3",
             "se_cluster_region", "p_b0_cluster", "se_cluster_quarter", "p_b0_cluster_quarter",
             "p_b0_wildboot", "p_b1_wildboot"]
    print(reg[show2].round(3).to_string(index=False))

    print("\n" + "=" * 126)
    print("B.  MONTHLY EMEA MIX (Eurostat platform nights, 18 countries, 12-month share-shift)")
    print("=" * 126)
    print(f"   months built: {len(mm)}  ({mm.month.iloc[0]} .. {mm.month.iloc[-1]}), "
          f"12-month changes: {int(mm.mix_pp_d12.notna().sum())}")
    print(f"   mix_pp: mean {mm.mix_pp.mean():+.3f}  sd {mm.mix_pp.std():.3f}  "
          f"min {mm.mix_pp.min():+.3f}  max {mm.mix_pp.max():+.3f}  "
          f"share imputed price {mm.share_imputed_price.mean():.4f}")
    print("\n-- b1: does the quarter mean of the monthly mix reproduce the published quarterly term? --")
    print(chk[["quarter", "mix_pp_monthly_qavg", "mix_pp_published_q", "diff_vs_published_pp",
               "mix_pp_q18", "diff_vs_q18_pp"]].round(3).to_string(index=False))
    for k, v in mres.items():
        if k.startswith("b1_diag|"):
            print(f"   [diag] {k.split('|')[1]:26s} n {v['n']:3d}  MAE {v['mae']:.3f}pp  mean {v['mean']:+.3f}pp  "
                  f"max|diff| {v['max_abs']:.3f}pp" + (f"  r {v['corr']:+.3f}" if pd.notna(v['corr']) else ""))
    for k, v in mres.items():
        if k.startswith("b1|"):
            print(f"   {k.split('|')[1]:32s} n {v['n']:3d}  MAE {v['mae']:.3f}pp  mean {v['mean']:+.3f}pp  "
                  f"max|diff| {v['max_abs']:.3f}pp   "
                  f"{'PASS' if v['mae'] <= PASS_MAE_MONTHLY else 'FAIL'} (line {PASS_MAE_MONTHLY}pp)")
    print("\n-- b2: 12-month change in the monthly mix vs the 4-quarter change in the EMEA CPI gap --")
    print(chk[["quarter", "mix_pp_monthly_qavg", "mix_d12_monthly_qavg", "disclosed_exfx_emea_pct",
               "hicp_ea_cp112_pct", "cpi_gap_pp", "cpi_gap_d4_pp", "is_disclosed",
               "in_chained_sample"]].round(3).to_string(index=False))
    for k, v in mres.items():
        if k.startswith("b2"):
            kind, lab = k.split("|")
            print(f"   {kind:12s} {lab:16s} n {v['n']:3d}  r {v['corr']:+.3f}  slope {v['slope']:+.3f}  "
                  f"{'right sign' if v['corr'] > 0 else 'WRONG SIGN'}")

    for f in ["reconcile_pooled_cells.csv", "reconcile_pooled_cpi_proxy.csv", "reconcile_pooled_regressions.csv",
              "reconcile_pooled_emea_monthly.csv", "reconcile_pooled_emea_monthly_check.csv"]:
        print(f"wrote {OUT / f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
