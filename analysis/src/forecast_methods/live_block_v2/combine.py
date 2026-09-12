"""Combination schemes for the optimal-mix package.

Every scheme is a pure function of a TRAINING block (forecast matrix F_train [T x K],
actual vector y_train [T], predictive sd matrix S_train [T x K]) and returns a weight
vector w [K] on the simplex (non-negative, sums to one).

LEAVE-FUTURE-OUT is enforced by the CALLER: the training block handed to these
functions contains only target quarters whose print_date is strictly before the
vintage date of the forecast being combined. Nothing in this file has any notion of
time, which is deliberate -- it cannot leak on its own.
"""
from __future__ import annotations

import numpy as np

MIN_TRAIN = 4          # below this many training pairs every scheme falls back to equal
SHRINK_LAMBDA = 0.5    # fixed a priori; stack_shrunk = 0.5*stack + 0.5*equal
BMA_TEMPER = 1.0       # no tempering; declared


def _equal(K: int) -> np.ndarray:
    return np.full(K, 1.0 / K)


def w_equal(F, y, S) -> np.ndarray:
    return _equal(F.shape[1])


def w_inverse_mse(F, y, S) -> np.ndarray:
    T, K = F.shape
    if T < MIN_TRAIN:
        return _equal(K)
    mse = np.mean((y[:, None] - F) ** 2, axis=0)
    mse = np.where(np.isfinite(mse) & (mse > 0), mse, np.inf)
    inv = 1.0 / mse
    if not np.isfinite(inv).any() or inv.sum() <= 0:
        return _equal(K)
    inv = np.where(np.isfinite(inv), inv, 0.0)
    return inv / inv.sum()


def w_stack(F, y, S) -> np.ndarray:
    """Constrained least squares on the PIT errors: min ||y - F w||^2, w >= 0, sum w = 1.

    Solved by NNLS on a design augmented with a heavily weighted sum-to-one row, then
    polished with SLSQP; the better of the two objectives is kept. SLSQP alone stalls at
    its starting point when K is large relative to T, which silently returned the equal
    weights and made the stack look identical to the equal-weight scheme.
    """
    T, K = F.shape
    if T < MIN_TRAIN:
        return _equal(K)
    from scipy.optimize import minimize, nnls

    # Primary solve: NNLS on the design augmented with a heavily weighted sum-to-one
    # row. This is the standard simplex trick and, unlike SLSQP, does not stall at the
    # starting point when K is large relative to T (which it is here: K up to 14, T <= 13).
    M = 1e3 * (np.abs(F).max() + 1.0)
    F_aug = np.vstack([F, M * np.ones((1, K))])
    y_aug = np.concatenate([y, [M]])
    try:
        w0, _ = nnls(F_aug, y_aug)
        if np.isfinite(w0).all() and w0.sum() > 0:
            w0 = w0 / w0.sum()
        else:
            w0 = _equal(K)
    except Exception:
        w0 = _equal(K)

    def obj(w):
        r = y - F @ w
        return float(r @ r)

    def grad(w):
        r = y - F @ w
        return -2.0 * (F.T @ r)

    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1.0,
             "jac": lambda w: np.ones_like(w)}]
    # SLSQP polish from the NNLS solution; keep whichever has the lower objective.
    res = minimize(obj, w0, jac=grad, bounds=[(0.0, 1.0)] * K,
                   constraints=cons, method="SLSQP",
                   options={"maxiter": 400, "ftol": 1e-12})
    w = np.asarray(res.x, dtype=float)
    w = np.clip(w, 0.0, None)
    if not np.isfinite(w).all() or w.sum() <= 0:
        w = w0
    else:
        w = w / w.sum()
        if obj(w0) < obj(w):
            w = w0
    return w


def w_stack_shrunk(F, y, S) -> np.ndarray:
    K = F.shape[1]
    return SHRINK_LAMBDA * w_stack(F, y, S) + (1.0 - SHRINK_LAMBDA) * _equal(K)


def w_bma(F, y, S) -> np.ndarray:
    """Bayesian model averaging with log-predictive-score weights.

    The registered predictive distribution of each candidate is summarised as a Gaussian
    with mean q50 and sd taken from the registered `sd` column (or (q90-q10)/2.5631 when
    sd is absent). Weight_i proportional to prior_i * exp(sum_t log N(y_t | f_it, s_it)).
    Prior is uniform over the pool. Computed with a log-sum-exp normalisation.
    """
    T, K = F.shape
    if T < MIN_TRAIN:
        return _equal(K)
    s = np.where(np.isfinite(S) & (S > 1e-9), S, np.nan)
    # a candidate with no usable sd anywhere gets the pool-median sd at that date
    row_med = np.nanmedian(s, axis=1, keepdims=True)
    row_med = np.where(np.isfinite(row_med), row_med, 1.0)
    s = np.where(np.isfinite(s), s, np.repeat(row_med, K, axis=1))
    ll = -0.5 * np.log(2.0 * np.pi * s ** 2) - 0.5 * ((y[:, None] - F) / s) ** 2
    tot = BMA_TEMPER * np.nansum(ll, axis=0)
    if not np.isfinite(tot).any():
        return _equal(K)
    tot = np.where(np.isfinite(tot), tot, -np.inf)
    m = np.max(tot)
    w = np.exp(tot - m)
    if w.sum() <= 0 or not np.isfinite(w.sum()):
        return _equal(K)
    return w / w.sum()


def w_top3_inv_mse(F, y, S) -> np.ndarray:
    """Selection + combination: keep the 3 lowest-trailing-MSE candidates, inverse-MSE
    weight them, zero the rest. Selection is itself leave-future-out."""
    T, K = F.shape
    if T < MIN_TRAIN:
        return _equal(K)
    mse = np.mean((y[:, None] - F) ** 2, axis=0)
    keep = np.argsort(mse)[: min(3, K)]
    w = np.zeros(K)
    inv = 1.0 / np.maximum(mse[keep], 1e-12)
    w[keep] = inv / inv.sum()
    return w


def w_top1_trailing(F, y, S) -> np.ndarray:
    """Pick the single lowest-trailing-MSE candidate. Not a combination -- it is the
    IMPLEMENTABLE version of "use the best single method", and it is the fair comparator
    for the mix, because the ex-post best single is an oracle nobody could have chosen
    in advance."""
    T, K = F.shape
    if T < MIN_TRAIN:
        return _equal(K)
    mse = np.mean((y[:, None] - F) ** 2, axis=0)
    w = np.zeros(K)
    w[int(np.argmin(mse))] = 1.0
    return w


SCHEMES = {
    "equal": w_equal,
    "inv_mse": w_inverse_mse,
    "stack_ls": w_stack,
    "stack_shrunk": w_stack_shrunk,
    "bma_logscore": w_bma,
    "top3_inv_mse": w_top3_inv_mse,
    "top1_trailing": w_top1_trailing,
}

# free parameters each scheme spends, over and above the candidates themselves
SCHEME_NPARAMS = {
    "equal": 0,
    "inv_mse": 0,          # weights are a deterministic function of trailing MSE
    "stack_ls": None,      # K-1, filled at call site
    "stack_shrunk": None,  # K-1
    "bma_logscore": 0,     # weights are a deterministic function of the log score
    "top3_inv_mse": 0,
    "top1_trailing": 0,
}


def mixture_moments(w, mu, sd):
    """Mean and sd of the finite Gaussian mixture sum_i w_i N(mu_i, sd_i^2).

    The mixture sd -- not sqrt(sum w_i^2 sd_i^2) -- is the right width: disagreement
    between candidates is genuine predictive uncertainty and must widen the interval.
    """
    w = np.asarray(w, float)
    mu = np.asarray(mu, float)
    sd = np.asarray(sd, float)
    ok = np.isfinite(mu)
    if not ok.any():
        return np.nan, np.nan
    w = np.where(ok, w, 0.0)
    if w.sum() <= 0:
        return np.nan, np.nan
    w = w / w.sum()
    mu = np.where(ok, mu, 0.0)
    sd = np.where(ok & np.isfinite(sd), sd, 0.0)
    m = float(w @ mu)
    v = float(w @ (sd ** 2 + (mu - m) ** 2))
    return m, float(np.sqrt(max(v, 0.0)))
