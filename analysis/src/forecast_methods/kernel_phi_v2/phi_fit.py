"""kernel_phi_v2 — the lag-weight (phi) machinery.

Model:      Revenue_q = c_{s(q)} * SUM_{k=0..K} phi_{g(q),k} * GBV_{q-k}
            phi >= 0, sum_k phi_{g,k} = 1   (softmax -> simplex)

`g(q)` is the phi GROUP of quarter q:
    'pooled'  -> one shared phi for all quarters          (K free weights)
    'season'  -> one phi per fiscal quarter-of-year       (4K free weights)
    'summer'  -> one phi for Q3, one for the rest         (2K free weights)

c_s is always season-specific (4 conversions).  Fitted on RELATIVE errors so the
2021 COVID quarters cannot dominate a dollar objective.  Seeded from
`kernel_lambda/kernel.py::fit_lag_polynomial`, generalised to K=4 and to grouped phi.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize

from common import usable


def group_of(seasons: np.ndarray, mode: str, summer_set=(3,)) -> np.ndarray:
    if mode == "pooled":
        return np.zeros(len(seasons), dtype=int)
    if mode == "season":
        return seasons.astype(int)
    if mode == "summer":
        return np.isin(seasons, list(summer_set)).astype(int)
    raise ValueError(mode)


def _design(frame: pd.DataFrame, kmax: int):
    f = usable(frame, kmax=kmax)
    G = np.column_stack([f[f"gbv_l{k}"].values for k in range(0, kmax + 1)])
    return f, G, f["revenue_musd"].values.astype(float), f["season"].values.astype(int)


def fit_phi(frame: pd.DataFrame, kmax: int = 4, mode: str = "pooled",
            summer_set=(3,), fixed_phi=None, single_lag=False):
    """Least-squares fit on relative errors.  Returns a dict.

    fixed_phi : array of length kmax+1 -> phi is NOT fitted (used for the
                published 2/3-1/3 kernel baseline and for the lambda-only model).
    single_lag: shortcut for phi = (0,1,0,...)  (the 'seasonal lambda only' model).
    """
    f, G, rev, seas = _design(frame, kmax)
    if len(f) == 0:
        raise ValueError("empty design")
    uniq = sorted(set(seas.tolist()))
    smap = {s: i for i, s in enumerate(uniq)}

    if single_lag:
        fixed_phi = np.zeros(kmax + 1)
        fixed_phi[1] = 1.0

    if fixed_phi is not None:
        phi_full = np.asarray(fixed_phi, dtype=float)
        base = G @ phi_full
        c = np.array([float(np.mean(rev[seas == s] / base[seas == s])) for s in uniq])
        pred = np.array([c[smap[s]] for s in seas]) * base
        r = pred / rev - 1.0
        return {"phi": {0: phi_full}, "groups": np.zeros(len(f), dtype=int),
                "c": {s: float(c[smap[s]] * 100.0) for s in uniq},
                "rmse_pct": 100.0 * float(np.sqrt((r ** 2).mean())),
                "n": len(f), "n_params": len(uniq), "mode": "fixed",
                "resid_pct": 100.0 * r, "quarters": f["q"].tolist()}

    grp = group_of(seas, mode, summer_set)
    gids = sorted(set(grp.tolist()))
    gmap = {g: i for i, g in enumerate(gids)}
    nfree = kmax  # free logits per group (first logit pinned at 0)

    def unpack(p):
        phis = {}
        for g in gids:
            z = np.concatenate([[0.0], p[gmap[g] * nfree:(gmap[g] + 1) * nfree]])
            e = np.exp(z - z.max())
            phis[g] = e / e.sum()
        c = p[len(gids) * nfree:]
        return phis, c

    def resid(p):
        phis, c = unpack(p)
        b = np.array([G[i] @ phis[grp[i]] for i in range(len(rev))])
        pred = np.array([c[smap[s]] for s in seas]) * b
        return pred / rev - 1.0

    # start at the published kernel (0, 2/3, 1/3, 0, 0) and its implied c_s
    z0 = np.zeros(kmax + 1)
    z0[1] = np.log(2 / 3) - np.log(1e-3)
    z0[2] = np.log(1 / 3) - np.log(1e-3)
    z0 = z0[1:] - 0.0
    p0 = np.concatenate([np.tile(z0, len(gids)),
                         [float(np.mean(rev[seas == s] /
                                        (2 / 3 * G[seas == s, 1] + 1 / 3 * G[seas == s, 2])))
                          for s in uniq]])
    sol = optimize.least_squares(resid, p0, max_nfev=60000, xtol=1e-14, ftol=1e-14)
    phis, c = unpack(sol.x)
    r = resid(sol.x)
    return {"phi": phis, "groups": grp,
            "c": {s: float(c[smap[s]] * 100.0) for s in uniq},
            "rmse_pct": 100.0 * float(np.sqrt((r ** 2).mean())),
            "n": len(f), "n_params": len(gids) * nfree + len(uniq), "mode": mode,
            "resid_pct": 100.0 * r, "quarters": f["q"].tolist(),
            "summer_set": summer_set}


def phi_of(fit: dict, season: int) -> np.ndarray:
    """The phi vector this fit applies to a quarter of the given season."""
    if fit["mode"] == "fixed" or set(fit["phi"].keys()) == {0}:
        if fit["mode"] == "fixed":
            return fit["phi"][0]
    mode = fit["mode"]
    if mode == "pooled":
        return fit["phi"][0]
    if mode == "season":
        return fit["phi"][int(season)]
    if mode == "summer":
        g = int(season in fit.get("summer_set", (3,)))
        return fit["phi"][g]
    return fit["phi"][0]


def predict(fit: dict, gbv_lags: np.ndarray, season: int) -> float:
    phi = phi_of(fit, season)
    return fit["c"][season] / 100.0 * float(gbv_lags @ phi)


def loo_rmse(frame: pd.DataFrame, kmax: int = 4, mode: str = "pooled",
             summer_set=(3,), fixed_phi=None, single_lag=False, min_per_season=2):
    """Leave-one-quarter-out relative RMSE.  Refits everything without quarter t."""
    f, G, rev, seas = _design(frame, kmax)
    errs, kept = [], []
    for i in range(len(f)):
        tr = f.drop(index=i)
        if tr["season"].nunique() < 4 or tr["season"].value_counts().min() < min_per_season:
            continue
        try:
            fit = fit_phi(tr, kmax=kmax, mode=mode, summer_set=summer_set,
                          fixed_phi=fixed_phi, single_lag=single_lag)
        except Exception:
            continue
        if seas[i] not in fit["c"]:
            continue
        pred = predict(fit, G[i], int(seas[i]))
        errs.append(pred / rev[i] - 1.0)
        kept.append(f["q"].iloc[i])
    e = 100.0 * np.asarray(errs)
    if len(e) == 0:
        return np.nan, np.nan, np.nan, 0, []
    return (float(np.sqrt((e ** 2).mean())), float(np.abs(e).mean()),
            float(e.mean()), len(e), kept)


def block_bootstrap_phi(frame: pd.DataFrame, kmax: int = 4, mode: str = "pooled",
                        summer_set=(3,), n_boot: int = 400, block: int = 4,
                        seed: int = 20260911, min_per_season: int = 2):
    """Moving-block bootstrap over the quarter sequence.  Returns a (B, kmax+1)
    array of pooled/representative phi draws plus a dict of per-group draws and
    the c draws."""
    rng = np.random.default_rng(seed)
    f, G, rev, seas = _design(frame, kmax)
    n = len(f)
    nb = int(np.ceil(n / block))
    out_phi, out_c, out_group = [], [], []
    tries = 0
    while len(out_phi) < n_boot and tries < n_boot * 20:
        tries += 1
        starts = rng.integers(0, max(n - block + 1, 1), nb)
        idx = np.concatenate([np.arange(s, min(s + block, n)) for s in starts])[:n]
        bf = f.iloc[idx].reset_index(drop=True)
        if bf["season"].nunique() < 4 or bf["season"].value_counts().min() < min_per_season:
            continue
        try:
            fit = fit_phi(bf, kmax=kmax, mode=mode, summer_set=summer_set)
        except Exception:
            continue
        out_phi.append(phi_of(fit, 3) if mode != "season" else fit["phi"][3])
        out_c.append([fit["c"].get(s, np.nan) for s in (1, 2, 3, 4)])
        out_group.append({g: v.copy() for g, v in fit["phi"].items()})
    return np.array(out_phi), np.array(out_c), out_group


def ci(a, lo=2.5, hi=97.5):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return (np.nan, np.nan)
    return (float(np.percentile(a, lo)), float(np.percentile(a, hi)))
