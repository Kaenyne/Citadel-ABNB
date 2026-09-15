"""Scoring primitives: CRPS from a quantile ladder, PIT, split conformal.

Nothing here knows about the registry; everything takes arrays.
"""
from __future__ import annotations

import math

import numpy as np

EXCHANGEABILITY_CAVEAT = (
    "EXCHANGEABILITY VIOLATED: residuals are a time-ordered non-exchangeable sequence "
    "(expanding-window refits, a trending target, and a regime change at the 2022 reopening); "
    "conformal coverage here is descriptive, not a guarantee."
)


def pinball_loss(y: float, q: float, tau: float) -> float:
    d = y - q
    return tau * d if d >= 0 else (tau - 1.0) * d


def crps_from_quantiles(y: float, levels, values) -> float:
    """CRPS via the quantile-score identity  CRPS = 2 * int_0^1 QS(tau) dtau.

    Trapezoid over the supplied tau ladder, with QS held constant outside the outermost
    supplied tau (so tails are bounded and CRPS is never inf, unlike integrating a
    piecewise-linear CDF with flat tails). With only a median supplied this returns |y-q50|,
    the exact CRPS of a point mass.
    """
    levels = np.asarray(levels, dtype=float)
    values = np.asarray(values, dtype=float)
    ok = np.isfinite(levels) & np.isfinite(values)
    levels, values = levels[ok], values[ok]
    if levels.size == 0:
        return float("nan")
    order = np.argsort(levels)
    levels, values = levels[order], values[order]
    qs = np.array([pinball_loss(y, v, t) for v, t in zip(values, levels)])
    if levels.size == 1:
        return float(2.0 * qs[0])
    integral = float(np.trapezoid(qs, levels)) if hasattr(np, "trapezoid") \
        else float(np.trapz(qs, levels))
    integral += qs[0] * (levels[0] - 0.0)          # flat extension to tau=0
    integral += qs[-1] * (1.0 - levels[-1])        # flat extension to tau=1
    return float(2.0 * integral)


def pit_from_quantiles(y: float, levels, values):
    """(pit, is_edge). Piecewise-linear CDF through the quantile ladder, clipped to [0,1]."""
    levels = np.asarray(levels, dtype=float)
    values = np.asarray(values, dtype=float)
    ok = np.isfinite(levels) & np.isfinite(values)
    levels, values = levels[ok], values[ok]
    if levels.size < 2:
        return float("nan"), True
    order = np.argsort(values)
    values, levels = values[order], levels[order]
    if y <= values[0]:
        return float(max(0.0, levels[0] * 0.5)), True
    if y >= values[-1]:
        return float(min(1.0, levels[-1] + (1.0 - levels[-1]) * 0.5)), True
    return float(np.interp(y, values, levels)), False


def pit_histogram(pits, nbins: int = 5):
    p = np.asarray([x for x in pits if np.isfinite(x)], dtype=float)
    if p.size == 0:
        return [0] * nbins
    edges = np.linspace(0, 1, nbins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1], right=False), 0, nbins - 1)
    return [int((idx == b).sum()) for b in range(nbins)]


def pit_uniform_ks_p(pits):
    """KS test of the PIT values against U(0,1). scipy if available, else NaN."""
    p = np.asarray([x for x in pits if np.isfinite(x)], dtype=float)
    if p.size < 4:
        return float("nan")
    try:
        from scipy import stats
        return float(stats.kstest(p, "uniform").pvalue)
    except Exception:
        return float("nan")


def conformal_k(n_cal: int, alpha: float) -> int:
    return int(math.ceil((n_cal + 1) * (1.0 - alpha)))


def attainable_coverage(n_cal: int, alpha: float):
    """(k, lo, hi). Attainable coverage of a split-conformal interval built on n_cal
    residuals. k = ceil((n+1)(1-alpha)); coverage lies in [k/(n+1), (k+1)/(n+1)].
    k > n means the interval is the MAXIMUM residual and no 1-alpha guarantee exists
    at that sample size -- the attainable floor is k/(n+1), not 1-alpha.
    """
    k = conformal_k(n_cal, alpha)
    lo = k / (n_cal + 1.0)
    hi = min(1.0, (k + 1.0) / (n_cal + 1.0))
    return k, lo, hi


def attainable_coverage_grid(n_cals=(4, 5, 6, 7, 8, 10, 12), alphas=(0.1, 0.2, 0.32)):
    rows = []
    for n in n_cals:
        for a in alphas:
            k, lo, hi = attainable_coverage(n, a)
            uses_max = k >= n
            exact = abs(lo - (1 - a)) < 1e-12
            rows.append({
                "n_cal": n, "alpha": a, "nominal_coverage": 1 - a, "k": k,
                "uses_max_residual": bool(uses_max),
                "quantile_used": (f"max of {n} residuals" if uses_max
                                  else f"{k}th smallest of {n}"),
                "attainable_lo": lo, "attainable_hi": hi,
                "exact_nominal_attainable": bool(exact),
                "note": ("qhat is the MAXIMUM of the calibration residuals; the coverage "
                         f"floor is k/(n+1) = {lo:.3f}, NOT the nominal "
                         f"{1-a:.2f}. Do not claim a {1-a:.0%} interval at this n_cal."
                         ) if uses_max else
                        ("" if exact else
                         f"coverage floor is k/(n+1) = {lo:.3f}, above nominal "
                         f"{1-a:.2f}; the interval is conservative, not exact."),
            })
    return rows


def rolling_split_conformal(y, point, n_cal: int = 6, alpha: float = 0.2):
    """Rolling split conformal on a time-ordered series.

    At each i >= n_cal, calibrate qhat on the previous n_cal absolute residuals
    (qhat = the k-th smallest, k = ceil((n_cal+1)(1-alpha)), capped at the max) and test
    whether |y_i - point_i| <= qhat. Returns (empirical_coverage, n_eval, mean_width).
    """
    y = np.asarray(y, dtype=float)
    p = np.asarray(point, dtype=float)
    res = np.abs(y - p)
    k, _, _ = attainable_coverage(n_cal, alpha)
    hits, widths = [], []
    for i in range(n_cal, len(res)):
        cal = np.sort(res[i - n_cal:i])
        qhat = cal[min(k, n_cal) - 1]
        hits.append(bool(res[i] <= qhat + 1e-12))
        widths.append(2.0 * qhat)
    if not hits:
        return float("nan"), 0, float("nan")
    return float(np.mean(hits)), len(hits), float(np.mean(widths))
