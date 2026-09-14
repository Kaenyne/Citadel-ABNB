"""kernel-lambda core: the recognition kernel lambda_s on lagged printed GBV.

Identity under test
-------------------
    Revenue_q  =  lambda_{s(q)} * [ w * GBV_{q-1} + (1-w) * GBV_{q-2} ]

with w = 2/3 the published prior.  lambda is an OUTPUT of printed revenue and
printed GBV; nothing here is fitted against anything unprinted.

Every function takes an explicit quarter-indexed frame so the point-in-time
replay can hand it a truncated panel.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize

# ---------------------------------------------------------------- panel

def canon(q: str) -> str:
    """'3Q26' -> '2026Q3'; passes '2026Q3' through."""
    s = str(q).strip().upper()
    if len(s) == 6 and s[4] == "Q":
        return s
    return f"20{s[2:4]}Q{s[0]}"


def build_panel(kpi_csv) -> pd.DataFrame:
    """Revenue / GBV panel with the two GBV lags and the quarter-of-year season."""
    d = pd.read_csv(kpi_csv)[["quarter", "revenue_musd", "gbv_musd",
                              "fx_pts_revenue", "fx_pts_adr"]].copy()
    d["q"] = d["quarter"].map(canon)
    d = d.sort_values("q").reset_index(drop=True)
    # contiguity: the lag shift is only valid on an unbroken quarterly index
    idx = [int(x[:4]) * 4 + int(x[-1]) for x in d["q"]]
    assert np.all(np.diff(idx) == 1), "panel is not a contiguous quarterly index"
    d["gbv_l1"] = d["gbv_musd"].shift(1)
    d["gbv_l2"] = d["gbv_musd"].shift(2)
    d["gbv_l3"] = d["gbv_musd"].shift(3)
    d["season"] = d["q"].str[-1].astype(int)
    return d


def base(frame: pd.DataFrame, w: float) -> pd.Series:
    return w * frame["gbv_l1"] + (1.0 - w) * frame["gbv_l2"]


def lam_pct(frame: pd.DataFrame, w: float) -> pd.Series:
    """lambda in PERCENT."""
    return 100.0 * frame["revenue_musd"] / base(frame, w)


def usable(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.dropna(subset=["revenue_musd", "gbv_l1", "gbv_l2"]).reset_index(drop=True)


# ---------------------------------------------------------------- objectives
# POOLING CONVENTION (one line, as required):
#   relative deviations of lambda_t(w) from the mean of its OWN quarter-of-year,
#   pooled across all four seasons on one fixed quarter set, RMS with denominator
#   (N - S) where S is the number of seasons present; reported in percent.

def pooled_dispersion(frame: pd.DataFrame, w: float) -> float:
    f = usable(frame)
    l = lam_pct(f, w)
    dev = np.concatenate([(g / g.mean() - 1.0).values for _, g in l.groupby(f["season"])])
    S = f["season"].nunique()
    return 100.0 * float(np.sqrt((dev ** 2).sum() / (len(dev) - S)))


def loo_criterion(frame: pd.DataFrame, w: float):
    """Leave-one-quarter-out: predict revenue_t with the season mean of lambda
    computed WITHOUT t.  Returns (RMSE %, MAE %, bias %, n)."""
    f = usable(frame)
    l = lam_pct(f, w).values
    s = f["season"].values
    rev = f["revenue_musd"].values
    b = base(f, w).values
    errs = []
    for i in range(len(l)):
        m = (s == s[i]).copy()
        m[i] = False
        if m.sum() < 1:
            continue
        errs.append((l[m].mean() / 100.0 * b[i]) / rev[i] - 1.0)
    e = 100.0 * np.array(errs)
    return float(np.sqrt((e ** 2).mean())), float(np.abs(e).mean()), float(e.mean()), len(e)


def weight_grid(frame: pd.DataFrame, ws=None) -> pd.DataFrame:
    ws = np.round(np.arange(0.0, 1.0001, 0.01), 2) if ws is None else ws
    rows = []
    for w in ws:
        r, m, bi, n = loo_criterion(frame, w)
        rows.append({"w": float(w), "pooled_rel_disp_pct": pooled_dispersion(frame, w),
                     "loo_rmse_pct": r, "loo_mae_pct": m, "loo_bias_pct": bi, "n": n})
    return pd.DataFrame(rows)


def argmin_w(frame: pd.DataFrame, col="loo_rmse_pct") -> float:
    g = weight_grid(frame)
    return float(g.loc[g[col].idxmin(), "w"])


# --- fast path used inside the bootstrap (same arithmetic, numpy only) ---------

def _arrays(frame: pd.DataFrame):
    f = usable(frame)
    return (f["revenue_musd"].values.astype(float), f["gbv_l1"].values.astype(float),
            f["gbv_l2"].values.astype(float), f["season"].values.astype(int))


def _loo_rmse_fast(rev, g1, g2, seas, w):
    b = w * g1 + (1.0 - w) * g2
    lam = rev / b
    errs = np.empty(len(rev))
    for i in range(len(rev)):
        m = seas == seas[i]
        k = m.sum()
        if k < 2:
            errs[i] = np.nan
            continue
        mu = (lam[m].sum() - lam[i]) / (k - 1)
        errs[i] = mu * b[i] / rev[i] - 1.0
    e = errs[np.isfinite(errs)]
    return 100.0 * float(np.sqrt((e ** 2).mean()))


def argmin_w_fast(frame: pd.DataFrame, ws=None) -> float:
    rev, g1, g2, seas = _arrays(frame)
    ws = np.round(np.arange(0.0, 1.0001, 0.02), 2) if ws is None else ws
    v = np.array([_loo_rmse_fast(rev, g1, g2, seas, w) for w in ws])
    return float(ws[int(np.nanargmin(v))])


def block_bootstrap_w(frame: pd.DataFrame, n_boot=400, block=4, seed=20261002,
                      col="loo_rmse_pct"):
    """Moving-block bootstrap over the quarter sequence -> distribution of argmin w.
    Uses the fast path on a 0.02 grid; identical objective to `weight_grid`."""
    rng = np.random.default_rng(seed)
    f = usable(frame)
    rev, g1, g2, seas = _arrays(f)
    n = len(f)
    nblocks = int(np.ceil(n / block))
    ws = np.round(np.arange(0.0, 1.0001, 0.02), 2)
    out = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - block + 1, nblocks)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        ss = seas[idx]
        if len(np.unique(ss)) < 4 or np.min(np.bincount(ss, minlength=5)[1:5]) < 2:
            continue
        v = np.array([_loo_rmse_fast(rev[idx], g1[idx], g2[idx], ss, w) for w in ws])
        out.append(float(ws[int(np.nanargmin(v))]))
    return np.array(out)


# ---------------------------------------------------------------- lag polynomial
# Revenue_q = lambda_{s(q)} * sum_{k=0..3} phi_k GBV_{q-k},  phi >= 0, sum phi = 1.
# 4 seasonal lambdas + 3 free phi = 7 parameters.  Fitted on RELATIVE errors so
# the 2021 COVID quarters do not dominate a dollar objective.

def fit_lag_polynomial(frame: pd.DataFrame, kmax=3, seed=None, restrict_phi0=False):
    f = frame.dropna(subset=["revenue_musd", "gbv_musd", "gbv_l1", "gbv_l2", "gbv_l3"])
    f = f.reset_index(drop=True)
    G = np.column_stack([f["gbv_musd"], f["gbv_l1"], f["gbv_l2"], f["gbv_l3"]])[:, :kmax + 1]
    rev = f["revenue_musd"].values
    seas = f["season"].values
    uniq = sorted(set(seas))

    nfree = kmax - 1 if restrict_phi0 else kmax

    def unpack(p):
        z = np.concatenate([[0.0], p[:nfree]])
        w_ = np.exp(z) / np.exp(z).sum()           # softmax -> simplex, phi >= 0
        phi = np.concatenate([[0.0], w_]) if restrict_phi0 else w_
        lam = p[nfree:]
        return phi, lam

    def resid(p):
        phi, lam = unpack(p)
        b = G @ phi
        lmap = {s: lam[i] for i, s in enumerate(uniq)}
        pred = np.array([lmap[s] for s in seas]) / 100.0 * b
        return pred / rev - 1.0

    p0 = np.concatenate([np.zeros(nfree), [float(lam_pct(f, 2 / 3)[f["season"] == s].mean())
                                           for s in uniq]])
    sol = optimize.least_squares(resid, p0, max_nfev=20000)
    phi, lam = unpack(sol.x)
    r = resid(sol.x)
    return {"phi": phi, "lam_pct": dict(zip(uniq, lam)),
            "rmse_pct": 100.0 * float(np.sqrt((r ** 2).mean())), "n": len(f),
            "n_params": nfree + len(uniq), "restrict_phi0": restrict_phi0}


def bootstrap_phi0(frame: pd.DataFrame, n_boot=300, block=4, seed=20261003, kmax=3):
    rng = np.random.default_rng(seed)
    f = frame.dropna(subset=["revenue_musd", "gbv_musd", "gbv_l1", "gbv_l2", "gbv_l3"])
    f = f.reset_index(drop=True)
    n = len(f)
    nb = int(np.ceil(n / block))
    out = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        bf = f.iloc[idx].reset_index(drop=True)
        if bf["season"].nunique() < 4 or bf["season"].value_counts().min() < 2:
            continue
        try:
            out.append(fit_lag_polynomial(bf, kmax=kmax)["phi"])
        except Exception:
            continue
    return np.array(out)


# ---------------------------------------------------------------- forecasting

def season_lambda(frame: pd.DataFrame, season: int, w: float, n_recent=None):
    """Mean lambda for a quarter-of-year over the supplied (already truncated) frame."""
    f = usable(frame)
    f = f[f["season"] == season]
    if n_recent is not None:
        f = f.tail(n_recent)
    if len(f) == 0:
        return np.nan, 0
    return float(lam_pct(f, w).mean()), len(f)


def relative_sigma(frame: pd.DataFrame, w: float, floor=0.010):
    """Pooled relative dispersion of lambda about its season mean, as a FRACTION.
    This is the predictive sd of the revenue level conditional on a known GBV base."""
    try:
        s = pooled_dispersion(frame, w) / 100.0
    except Exception:
        return floor
    if not np.isfinite(s) or s <= 0:
        return floor
    return max(s, floor)


_Z = {"q05": -1.6449, "q10": -1.2816, "q25": -0.6745, "q50": 0.0,
      "q75": 0.6745, "q90": 1.2816, "q95": 1.6449}


def quantiles_lognormal(point: float, rel_sd: float) -> dict:
    """Gaussian in logs -> strictly positive, non-decreasing ladder."""
    mu = np.log(point) - 0.0
    s = np.log1p(rel_sd)
    return {k: float(np.exp(mu + z * s)) for k, z in _Z.items()}


def loo_lag_polynomial(frame: pd.DataFrame, kmax=3, restrict_phi0=False):
    """Leave-one-quarter-out relative RMSE for the lag polynomial: refit without
    quarter t, predict t.  This is the only fair free-vs-restricted comparison,
    because the free fit spends one extra parameter."""
    f = frame.dropna(subset=["revenue_musd", "gbv_musd", "gbv_l1", "gbv_l2", "gbv_l3"])
    f = f.reset_index(drop=True)
    G = np.column_stack([f["gbv_musd"], f["gbv_l1"], f["gbv_l2"], f["gbv_l3"]])[:, :kmax + 1]
    rev = f["revenue_musd"].values
    seas = f["season"].values
    errs = []
    for i in range(len(f)):
        tr = f.drop(index=i)
        if tr["season"].nunique() < 4 or tr["season"].value_counts().min() < 2:
            continue
        fit = fit_lag_polynomial(tr, kmax=kmax, restrict_phi0=restrict_phi0)
        lam = fit["lam_pct"].get(seas[i])
        if lam is None:
            continue
        errs.append((lam / 100.0 * float(G[i] @ fit["phi"])) / rev[i] - 1.0)
    e = 100.0 * np.array(errs)
    return float(np.sqrt((e ** 2).mean())), len(e)
