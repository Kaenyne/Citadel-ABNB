"""live-block-v2 core: impose the printed-KPI identity on the live 3Q26 block.

COPY, NEVER OVERWRITE.  Nothing in this module imports or mutates optimal_mix,
fee_takerate or kernel_lambda.  The pieces it needs from them are reproduced here,
attributed line by line, so that the original packages stay exactly as they were.

The two identities being imposed are ABNB's own definitions, not modelling choices:

    (I1)  GBV            =  (Nights and Seats Booked) x ADR
          -- ABNB defines ADR as GBV divided by Nights and Seats Booked, so ADR
             is definitionally the residual of the other two.
    (I2)  printed take rate = Revenue / SAME-QUARTER GBV

The kernel object is a DIFFERENT ratio and is never mixed with (I2):

    (K)   lambda_s       =  Revenue_q / [ w.GBV_{q-1} + (1-w).GBV_{q-2} ],  w = 2/3
          -- reproduced from analysis/src/forecast_methods/kernel_lambda/kernel.py
             (lines 5-7, 45-52).  Its denominator is LAGGED GBV; converting it to a
             printed take rate requires multiplying by the lagged-to-same-quarter GBV
             base ratio.  See `kernel_wedge`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

W_KERNEL = 2.0 / 3.0          # kernel_lambda published prior
Z90 = 1.2815515655446004      # Phi^{-1}(0.90); optimal_mix/run.py uses the same constant


# ---------------------------------------------------------------------------
# (K) the kernel, reproduced from kernel_lambda/kernel.py
# ---------------------------------------------------------------------------
def kernel_base(gbv_l1: float, gbv_l2: float, w: float = W_KERNEL) -> float:
    """w.GBV_{q-1} + (1-w).GBV_{q-2}."""
    return w * gbv_l1 + (1.0 - w) * gbv_l2


def lambda_history(tg: pd.DataFrame, season: int, w: float = W_KERNEL) -> pd.DataFrame:
    """lambda_s in percent, per year, for one quarter-of-year, from the target panel."""
    d = tg.dropna(subset=["revenue_musd", "gbv_musd"])[
        ["quarter", "revenue_musd", "gbv_musd"]].copy()
    d = d.sort_values("quarter").reset_index(drop=True)
    d["gbv_l1"] = d["gbv_musd"].shift(1)
    d["gbv_l2"] = d["gbv_musd"].shift(2)
    d["season"] = d["quarter"].str[-1].astype(int)
    d = d[d["season"] == season].dropna(subset=["gbv_l1", "gbv_l2"])
    d["kernel_base_musd"] = kernel_base(d["gbv_l1"], d["gbv_l2"], w)
    d["lambda_pct"] = 100.0 * d["revenue_musd"] / d["kernel_base_musd"]
    d["printed_take_rate_pct"] = 100.0 * d["revenue_musd"] / d["gbv_musd"]
    d["base_ratio_lagged_over_same_q"] = d["kernel_base_musd"] / d["gbv_musd"]
    return d


def kernel_wedge(lambda_pct: float, kernel_base_musd: float, gbv_same_q_musd: float):
    """The structural gap between lambda (lagged-GBV ratio) and the printed take rate.

    printed = lambda x (kernel_base / same-quarter GBV).  Returns (printed, ratio).
    """
    ratio = kernel_base_musd / gbv_same_q_musd
    return lambda_pct * ratio, ratio


# ---------------------------------------------------------------------------
# walk-forward error correlation, from the registry backtests
# ---------------------------------------------------------------------------
def walkforward_errors(cw: pd.DataFrame, specs: dict, window: str,
                       prior_basis: str) -> pd.DataFrame:
    """Percent walk-forward errors (forecast - actual)/actual x 100, one column per
    target, indexed by target quarter.  `specs` maps target -> (pool, scheme): the
    SAME pool and scheme the live object was built from, so the correlation describes
    the actual objects being combined, not some other combination."""
    out = {}
    for t, (pool, scheme) in specs.items():
        d = cw[(cw["target"] == t) & (cw["pool"] == pool) & (cw["scheme"] == scheme)
               & (cw["window"] == window) & (cw["prior_basis"] == prior_basis)]
        if not len(d):
            continue
        e = 100.0 * (d["point"].to_numpy(float) - d["actual"].to_numpy(float)) \
            / d["actual"].to_numpy(float)
        out[t] = pd.Series(e, index=d["quarter"].to_numpy())
    return pd.DataFrame(out).dropna()


def nearest_psd(C: np.ndarray) -> np.ndarray:
    """Clip tiny negative eigenvalues so the Cholesky in `joint_draws` cannot fail.
    With 3 series and n >= 10 this is a no-op in practice; it is here so the run
    cannot silently produce garbage if a future pool changes."""
    v, Q = np.linalg.eigh((C + C.T) / 2.0)
    if (v > 1e-10).all():
        return C
    v = np.clip(v, 1e-10, None)
    A = Q @ np.diag(v) @ Q.T
    d = np.sqrt(np.diag(A))
    return A / np.outer(d, d)


# ---------------------------------------------------------------------------
# the joint draw, and the take rate derived ONCE from it
# ---------------------------------------------------------------------------
def joint_draws(points: dict, sds: dict, corr: np.ndarray, order: list,
                n: int = 500_000, seed: int = 20260911) -> dict:
    """Draw (revenue, gbv, nights) jointly as correlated Gaussians on the LEVELS.

    Gaussian on the level is not an extra assumption: every live object in
    combined_live_objects.json publishes q10 = point - 1.2816 sd and
    q90 = point + 1.2816 sd, i.e. its marginal already IS Gaussian on the level.
    This routine changes only the DEPENDENCE between them, which the published
    block never specified at all.

    Returns the draws plus the two identity outputs, ADR = GBV / Nights and
    take rate = 100 x Revenue / GBV.
    """
    rng = np.random.default_rng(seed)
    k = len(order)
    S = np.array([sds[o] for o in order], float)
    L = np.linalg.cholesky(nearest_psd(np.asarray(corr, float)) * np.outer(S, S))
    mu = np.array([points[o] for o in order], float)
    X = mu + rng.standard_normal((n, k)) @ L.T
    d = {o: X[:, i] for i, o in enumerate(order)}
    d["adr_usd"] = d["gbv_musd"] / d["nights_m"]
    d["take_rate_pct"] = 100.0 * d["revenue_musd"] / d["gbv_musd"]
    return d


QLEVELS = {"q05": 0.05, "q10": 0.10, "q25": 0.25, "q50": 0.50,
           "q75": 0.75, "q90": 0.90, "q95": 0.95}


def summarise(x: np.ndarray) -> dict:
    out = {"point": float(np.mean(x)), "sd": float(np.std(x, ddof=1))}
    for name, tau in QLEVELS.items():
        out[name] = float(np.quantile(x, tau))
    return out


def p_at_least(x: np.ndarray, thr: float) -> float:
    return float(np.mean(x >= thr))
