"""C4 audit — does the pooled mix-term reconciliation rest on one region?

Reads the frozen engine output reconcile_pooled_cells.csv (never re-runs the engine), reproduces the primary
specification and the leave-one-region-out slopes, then does what the note did not:
  (a) a fully enumerated Webb six-point wild cluster bootstrap (6^4 = 1296 draws) for H0: b = 0 and H0: b = 1,
      alongside the Rademacher 2^4 = 16 the note registered;
  (b) plain OLS and HC1 p-values, restated;
  (c) leave-one-quarter-out and leave-two-out inside Latin America, and a decomposition of the LatAm within-region
      slope into its ex-FX, CPI and size/LOS pieces;
  (d) the pooled slope with Latin America's comparator replaced by zero and by the same-quarter median of the
      other regions' comparators;
  (e) randomisation inference: permute the mix series within each region (the regressor is ours, the target is
      Airbnb's) and ask how often a pooled |b| >= the observed one appears.

Run (from the audit worktree root):
  py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/C4_audit.py
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ENG = ROOT / "data/processed/pitch_model_v2/adr_engine"
CELLS = ENG / "reconcile_pooled_cells.csv"
REGS = ENG / "reconcile_pooled_regressions.csv"
REGIONS = ["NAM", "EMEA", "LatAm", "APAC"]
BAND = (0.5, 1.5)
WEBB = [-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)]


# ------------------------------------------------------------------ machinery (independent re-implementation)
def design(d: pd.DataFrame, ycol: str, fe: bool = True):
    y = d[ycol].to_numpy(float)
    mix = d["mix_pp"].to_numpy(float)
    g = d["region"].to_numpy()
    if fe:
        X = np.column_stack([mix, pd.get_dummies(d.region, dtype=float).to_numpy(float)])
    else:
        X = np.column_stack([mix, np.ones(len(d))])
    return y, X, g


def fit(y, X, g):
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    dof = n - k
    s2 = u @ u / dof
    se_iid = np.sqrt(s2 * XtX_inv[0, 0])
    meat = (X * (u ** 2)[:, None]).T @ X
    se_hc1 = np.sqrt((XtX_inv @ meat @ XtX_inv)[0, 0] * n / dof)
    gs = np.unique(g)
    G = len(gs)
    meat_c = np.zeros((k, k))
    for gg in gs:
        m = g == gg
        s = X[m].T @ u[m]
        meat_c += np.outer(s, s)
    c = (G / (G - 1)) * ((n - 1) / dof) if G > 1 else np.nan
    se_crv = np.sqrt((XtX_inv @ meat_c @ XtX_inv)[0, 0] * c) if G > 1 else np.nan
    return dict(b=beta[0], beta=beta, u=u, n=n, k=k, dof=dof, G=G, se_iid=se_iid, se_hc1=se_hc1, se_crv=se_crv)


def crv_summary(d, ycol, fe=True, b0s=(0.0, 1.0)):
    y, X, g = design(d, ycol, fe)
    f = fit(y, X, g)
    G = f["G"]
    out = dict(n=f["n"], G=G, b=f["b"], se_crv=f["se_crv"], se_iid=f["se_iid"], se_hc1=f["se_hc1"])
    if G > 1:
        dfc = G - 1
        for b0 in b0s:
            t = (f["b"] - b0) / f["se_crv"]
            out[f"p_b{int(b0)}_crv"] = 2 * (1 - sps.t.cdf(abs(t), dfc))
        tc = sps.t.ppf(0.95, dfc)
        out["ci90_lo"], out["ci90_hi"] = f["b"] - tc * f["se_crv"], f["b"] + tc * f["se_crv"]
    out["p_b0_iid"] = 2 * (1 - sps.t.cdf(abs(f["b"] / f["se_iid"]), f["dof"]))
    out["p_b0_hc1"] = 2 * (1 - sps.t.cdf(abs(f["b"] / f["se_hc1"]), f["dof"]))
    out["p_b1_iid"] = 2 * (1 - sps.t.cdf(abs((f["b"] - 1) / f["se_iid"]), f["dof"]))
    out["p_b1_hc1"] = 2 * (1 - sps.t.cdf(abs((f["b"] - 1) / f["se_hc1"]), f["dof"]))
    return out


def wild_cluster(d, ycol, b0, weights, fe=True, restricted=True):
    """Wild cluster bootstrap-t. restricted=True imposes b=b0 when generating (WCR); False uses the unrestricted
    residuals (WCU). All len(weights)^G draws enumerated. Returns p, n_draws, and the |t*| distribution."""
    y, X, g = design(d, ycol, fe)
    f = fit(y, X, g)
    t_obs = (f["b"] - b0) / f["se_crv"]
    if restricted:
        y_r = y - b0 * X[:, 0]
        Z = X[:, 1:]
        bz = np.linalg.pinv(Z.T @ Z) @ Z.T @ y_r
        fitted = b0 * X[:, 0] + Z @ bz
        u = y - fitted
    else:
        fitted = X @ f["beta"]
        u = f["u"]
    gs = np.unique(g)
    ts = []
    for w in itertools.product(weights, repeat=len(gs)):
        wv = np.empty(len(y))
        for gg, s in zip(gs, w):
            wv[g == gg] = s
        y_star = fitted + wv * u
        fs = fit(y_star, X, g)
        ts.append(abs((fs["b"] - b0) / fs["se_crv"]))
    ts = np.array(ts)
    p = float((ts >= abs(t_obs) - 1e-12).mean())
    return p, len(ts), t_obs, ts


def within_slope(x: pd.DataFrame, ycol: str):
    if len(x) < 3 or x.mix_pp.nunique() < 2:
        return np.nan, np.nan
    b = np.polyfit(x.mix_pp, x[ycol], 1)[0]
    r = np.corrcoef(x.mix_pp, x[ycol])[0, 1]
    return float(b), float(r)


def loro(d, ycol="y_full_p1"):
    rows = []
    for r in REGIONS:
        sub = d[d.region != r]
        s = crv_summary(sub, ycol)
        rows.append(dict(dropped=r, **{k: s.get(k) for k in ("n", "G", "b", "se_crv", "p_b0_crv", "p_b1_crv")}))
    return pd.DataFrame(rows)


def main():
    pd.set_option("display.width", 220)
    d_all = pd.read_csv(CELLS)
    disc = d_all[d_all.is_disclosed].copy().sort_values(["region", "qi"]).reset_index(drop=True)
    reg = pd.read_csv(REGS)
    prim = reg[(reg["sample"] == "disclosed_only") & (reg.spec.str.startswith("primary: FE"))].iloc[0]
    lines = []
    P = lambda s="": (print(s), lines.append(s))

    # ------------------------------------------------------------ 1. reproduction
    P("=" * 100); P("1. REPRODUCTION of the primary spec and the leave-one-region-out slopes"); P("=" * 100)
    s = crv_summary(disc, "y_full_p1")
    rep = pd.DataFrame([
        dict(stat="b", note_value=prim.b, audit_value=s["b"]),
        dict(stat="se_cluster_region", note_value=prim.se_cluster_region, audit_value=s["se_crv"]),
        dict(stat="p_b0_cluster (t3)", note_value=prim.p_b0_cluster, audit_value=s["p_b0_crv"]),
        dict(stat="p_b1_cluster (t3)", note_value=prim.p_b1_cluster, audit_value=s["p_b1_crv"]),
        dict(stat="ci90_lo", note_value=prim.ci90_lo, audit_value=s["ci90_lo"]),
        dict(stat="ci90_hi", note_value=prim.ci90_hi, audit_value=s["ci90_hi"]),
        dict(stat="n", note_value=prim.n, audit_value=s["n"]),
        dict(stat="p_b0_iid", note_value=prim.p_b0_iid, audit_value=s["p_b0_iid"]),
        dict(stat="p_b0_hc1", note_value=prim.p_b0_hc1, audit_value=s["p_b0_hc1"]),
    ])
    rep["diff"] = rep.audit_value - rep.note_value
    P(rep.round(6).to_string(index=False))
    lo = loro(disc)
    note_lo = {r: reg[(reg["sample"] == "disclosed_only") & (reg.spec == f"primary, drop {r}")].b.iloc[0] for r in REGIONS}
    lo["note_b"] = lo.dropped.map(note_lo)
    lo["diff"] = lo.b - lo.note_b
    P(""); P("leave-one-region-out (audit vs note):"); P(lo.round(4).to_string(index=False))
    rep.to_csv(HERE / "C4_reproduction.csv", index=False)
    lo.to_csv(HERE / "C4_loro.csv", index=False)
    P(""); P("within-region slopes (primary y on mix):")
    wr = []
    for r in REGIONS:
        x = disc[disc.region == r]
        b, rr = within_slope(x, "y_full_p1")
        wr.append(dict(region=r, n=len(x), b_within=b, r_within=rr))
    P(pd.DataFrame(wr).round(3).to_string(index=False))

    # ------------------------------------------------------------ 2. inference with four clusters
    P(""); P("=" * 100); P("2. INFERENCE WITH G = 4: wild cluster bootstrap, enumerated"); P("=" * 100)
    wb = []
    specs = [("primary (disclosed, FE)", disc, "y_full_p1", True),
             ("drop LatAm (disclosed, FE)", disc[disc.region != "LatAm"], "y_full_p1", True),
             ("no FE (disclosed)", disc, "y_full_p1", False),
             ("CPI P2 (disclosed, FE)", disc, "y_full_p2", True)]
    for lab, dd, ycol, fe in specs:
        for b0 in (0.0, 1.0):
            for wname, w in (("rademacher", [-1.0, 1.0]), ("webb6", WEBB)):
                for restricted in (True, False):
                    p, nd, t_obs, ts = wild_cluster(dd, ycol, b0, w, fe, restricted)
                    wb.append(dict(spec=lab, H0_b=b0, weights=wname, restricted=restricted, n_draws=nd,
                                   t_obs=t_obs, p_boot=p, min_attainable_p=1 / nd,
                                   frac_t_star_above_2=float((ts > 2).mean()), t_star_median=float(np.median(ts))))
    wb = pd.DataFrame(wb)
    P(wb.round(4).to_string(index=False))
    wb.to_csv(HERE / "C4_wildboot.csv", index=False)

    # why the FE + WCR bootstrap is degenerate: show the 16 Rademacher draws' b* and t* for the primary spec
    y, X, g = design(disc, "y_full_p1", True)
    f0 = fit(y, X, g)
    yr = y - 0.0 * X[:, 0]; Z = X[:, 1:]; fitted = Z @ (np.linalg.pinv(Z.T @ Z) @ Z.T @ yr); u = y - fitted
    gs = np.unique(g)
    P(""); P("Rademacher WCR draws on the primary spec, H0 b=0 (t_obs %.3f):" % (f0["b"] / f0["se_crv"]))
    rows = []
    for w in itertools.product([-1.0, 1.0], repeat=4):
        wv = np.empty(len(y))
        for gg, sgn in zip(gs, w):
            wv[g == gg] = sgn
        fs = fit(fitted + wv * u, X, g)
        rows.append(dict(signs=" ".join(f"{gg}:{int(sgn):+d}" for gg, sgn in zip(gs, w)), b_star=fs["b"],
                         se_star=fs["se_crv"], t_star=fs["b"] / fs["se_crv"]))
    P(pd.DataFrame(rows).round(3).to_string(index=False))

    # ------------------------------------------------------------ 3. which LatAm prints carry it
    P(""); P("=" * 100); P("3. LEAVE-ONE-QUARTER-OUT AND LEAVE-TWO-OUT INSIDE LATIN AMERICA"); P("=" * 100)
    la = disc[disc.region == "LatAm"]
    b_full, r_full = within_slope(la, "y_full_p1")
    rows = []
    for q in la.quarter:
        sub = disc[~((disc.region == "LatAm") & (disc.quarter == q))]
        s = crv_summary(sub, "y_full_p1")
        bl, rl = within_slope(la[la.quarter != q], "y_full_p1")
        rows.append(dict(dropped_latam_quarter=q, pooled_b=s["b"], pooled_p_b0=s["p_b0_crv"],
                         pooled_p_b1=s["p_b1_crv"], latam_b=bl, latam_r=rl, latam_n=len(la) - 1,
                         in_band=BAND[0] <= s["b"] <= BAND[1]))
    lq = pd.DataFrame(rows)
    P(f"LatAm within slope, all 7: b {b_full:+.3f}  r {r_full:+.3f}")
    P(lq.round(3).to_string(index=False))
    lq.to_csv(HERE / "C4_latam_loqo.csv", index=False)
    rows = []
    for q1, q2 in itertools.combinations(list(la.quarter), 2):
        sub = disc[~((disc.region == "LatAm") & (disc.quarter.isin([q1, q2])))]
        s = crv_summary(sub, "y_full_p1")
        bl, rl = within_slope(la[~la.quarter.isin([q1, q2])], "y_full_p1")
        rows.append(dict(dropped=f"{q1}+{q2}", pooled_b=s["b"], pooled_p_b0=s["p_b0_crv"], latam_b=bl, latam_r=rl,
                         in_band=BAND[0] <= s["b"] <= BAND[1]))
    l2 = pd.DataFrame(rows).sort_values("pooled_b")
    P(""); P("leave-two-out inside LatAm (21 pairs), sorted by pooled b:")
    P(l2.round(3).to_string(index=False))
    P(f"pairs whose removal leaves the band: {int((~l2.in_band).sum())} of {len(l2)}")
    l2.to_csv(HERE / "C4_latam_l2o.csv", index=False)

    # decomposition of the LatAm slope: y = exfx - cpi - size - los, so b_y = b_exfx - b_cpi - b_size - b_los
    P(""); P("decomposition of the LatAm within-region slope (each component regressed on mix, n 7):")
    dec = []
    for col, sign in (("disclosed_exfx_pct", 1), ("cpi_p1_pct", -1), ("global_unit_size_pp", -1),
                      ("global_los_pp", -1), ("y_full_p1", 1)):
        b, r = within_slope(la, col)
        dec.append(dict(component=col, sign_in_y=sign, slope_on_mix=b, r=r, contribution_to_b_y=sign * b))
    dec = pd.DataFrame(dec)
    P(dec.round(3).to_string(index=False))
    dec.to_csv(HERE / "C4_latam_decomposition.csv", index=False)
    P(""); P("the LatAm panel, for the eye:")
    P(la[["quarter", "disclosed_exfx_pct", "mix_pp", "cpi_p1_pct", "cpi_coverage_pct", "y_full_p1"]].round(3).to_string(index=False))

    # ------------------------------------------------------------ 4. neutral LatAm comparator
    P(""); P("=" * 100); P("4. THE POOLED SLOPE WITH A NEUTRAL LATIN-AMERICAN COMPARATOR"); P("=" * 100)
    # median of the OTHER regions' P1 comparators in the same quarter (all cells, not just disclosed: the proxy
    # exists for every region-quarter regardless of whether the ex-FX print is disclosed)
    other_med = (d_all[d_all.region != "LatAm"].groupby("quarter").cpi_p1_pct.median())
    other_mean = (d_all[d_all.region != "LatAm"].groupby("quarter").cpi_p1_pct.mean())
    variants = {
        "as published (Brazil IBGE, ~27% coverage)": disc.cpi_p1_pct,
        "LatAm comparator = 0": np.where(disc.region == "LatAm", 0.0, disc.cpi_p1_pct),
        "LatAm comparator = same-quarter median of other regions": np.where(
            disc.region == "LatAm", disc.quarter.map(other_med), disc.cpi_p1_pct),
        "LatAm comparator = same-quarter mean of other regions": np.where(
            disc.region == "LatAm", disc.quarter.map(other_mean), disc.cpi_p1_pct),
        "LatAm comparator = its own 7-quarter mean (constant)": np.where(
            disc.region == "LatAm", la.cpi_p1_pct.mean(), disc.cpi_p1_pct),
    }
    rows, loro_rows = [], []
    for lab, cpi in variants.items():
        dd = disc.copy()
        dd["cpi_alt"] = np.asarray(cpi, float)
        dd["y_alt"] = dd.disclosed_exfx_pct - dd.cpi_alt - dd.global_unit_size_pp - dd.global_los_pp
        s = crv_summary(dd, "y_alt")
        pW, _, _, _ = wild_cluster(dd, "y_alt", 0.0, WEBB, True, True)
        pW1, _, _, _ = wild_cluster(dd, "y_alt", 1.0, WEBB, True, True)
        bl, rl = within_slope(dd[dd.region == "LatAm"], "y_alt")
        rows.append(dict(variant=lab, n=s["n"], b=s["b"], se_crv=s["se_crv"], p_b0_crv=s["p_b0_crv"],
                         p_b1_crv=s["p_b1_crv"], ci90_lo=s["ci90_lo"], ci90_hi=s["ci90_hi"],
                         p_b0_webb=pW, p_b1_webb=pW1, latam_b=bl, latam_r=rl,
                         in_band=BAND[0] <= s["b"] <= BAND[1]))
        lo_v = loro(dd, "y_alt"); lo_v.insert(0, "variant", lab); loro_rows.append(lo_v)
    nv = pd.DataFrame(rows)
    P(nv.round(3).to_string(index=False))
    nv.to_csv(HERE / "C4_neutral_comparator.csv", index=False)
    lov = pd.concat(loro_rows)
    P(""); P("leave-one-region-out under each comparator:"); P(lov.round(3).to_string(index=False))
    lov.to_csv(HERE / "C4_neutral_comparator_loro.csv", index=False)
    P(""); P("other regions' P1 comparator by quarter (median / mean used above):")
    P(pd.DataFrame({"median_other": other_med, "mean_other": other_mean}).loc[la.quarter].round(3).to_string())

    # ------------------------------------------------------------ 5. randomisation inference
    P(""); P("=" * 100); P("5. RANDOMISATION INFERENCE: permute the mix series within each region"); P("=" * 100)
    rng = np.random.default_rng(20260922)
    y, X, g = design(disc, "y_full_p1", True)
    b_obs = fit(y, X, g)["b"]
    idx = {r: np.where(g == r)[0] for r in REGIONS}
    B = 20000
    bs = np.empty(B)
    for i in range(B):
        Xp = X.copy()
        for r, ii in idx.items():
            if len(ii) > 1:
                Xp[ii, 0] = X[rng.permutation(ii), 0]
        bs[i] = fit(y, Xp, g)["b"]
    p_two = float((np.abs(bs) >= abs(b_obs) - 1e-12).mean())
    p_one = float((bs >= b_obs - 1e-12).mean())
    P(f"observed b {b_obs:+.3f}; permutation null (within-region shuffles of mix, {B} draws): "
      f"mean {bs.mean():+.3f} sd {bs.std():.3f}; p(|b*|>=|b|) {p_two:.4f}, p(b*>=b) {p_one:.4f}")
    # and the same with LatAm's mix held fixed (only the other regions shuffled) -> how much do the others add
    bs2 = np.empty(B)
    for i in range(B):
        Xp = X.copy()
        for r, ii in idx.items():
            if r != "LatAm" and len(ii) > 1:
                Xp[ii, 0] = X[rng.permutation(ii), 0]
        bs2[i] = fit(y, Xp, g)["b"]
    P(f"LatAm mix held fixed, EMEA/APAC shuffled: b* mean {bs2.mean():+.3f} sd {bs2.std():.3f} "
      f"range [{bs2.min():+.3f}, {bs2.max():+.3f}]")
    # LatAm alone: exact enumeration of 7! permutations of its mix against its y
    la_y = la.y_full_p1.to_numpy(); la_m = la.mix_pp.to_numpy()
    b_la = np.polyfit(la_m, la_y, 1)[0]
    perm_b = np.array([np.polyfit(la_m[list(pm)], la_y, 1)[0] for pm in itertools.permutations(range(len(la)))])
    P(f"LatAm alone, exact permutation test (7! = {len(perm_b)}): b {b_la:+.3f}, "
      f"p(|b*|>=|b|) {float((np.abs(perm_b) >= abs(b_la) - 1e-12).mean()):.4f}")
    pd.DataFrame(dict(b_perm=bs, b_perm_latam_fixed=bs2)).describe().to_csv(HERE / "C4_permutation_summary.csv")

    (HERE / "C4_audit_output.txt").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
