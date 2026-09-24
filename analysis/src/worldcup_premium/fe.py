"""worldcup_premium / fe.py — OLS with several absorbed fixed effects (alternating projections) and cluster-robust
standard errors. No external FE library is installed on the build machine; this is the textbook estimator."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats


def demean(M: np.ndarray, groups: list[np.ndarray], tol: float = 1e-10, max_iter: int = 500) -> np.ndarray:
    """Project M off the span of the group dummies (method of alternating projections)."""
    X = M.astype(float).copy()
    codes = [pd.factorize(g)[0] for g in groups]
    counts = [np.bincount(c) for c in codes]
    for _ in range(max_iter):
        prev = X.copy()
        for c, n in zip(codes, counts):
            sums = np.zeros((n.size, X.shape[1]))
            np.add.at(sums, c, X)
            X -= (sums / n[:, None])[c]
        if np.max(np.abs(X - prev)) < tol:
            break
    return X


def ols_fe(df: pd.DataFrame, y: str, x: list[str], absorb: list[str], cluster: str, level: float = 0.90) -> pd.DataFrame:
    """y on x with the absorb columns as fixed effects; CR1 cluster-robust SEs; t(G-1) intervals."""
    d = df.dropna(subset=[y] + x + absorb + [cluster]).copy()
    # drop singletons of the first absorbed factor (they carry no within variation)
    first = absorb[0]
    d = d[d.groupby(first)[first].transform("size") > 1]
    M = demean(d[[y] + x].to_numpy(), [d[a].to_numpy() for a in absorb])
    Y, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ Y
    e = Y - X @ b
    g = pd.factorize(d[cluster])[0]; G = g.max() + 1
    S = np.zeros((X.shape[1], X.shape[1]))
    Xe = X * e[:, None]
    sums = np.zeros((G, X.shape[1])); np.add.at(sums, g, Xe)
    S = sums.T @ sums
    n, k = X.shape
    k_abs = sum(d[a].nunique() for a in absorb)
    c = (G / (G - 1)) * ((n - 1) / max(n - k - k_abs, 1))
    V = c * XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    tq = stats.t.ppf(0.5 + level / 2, G - 1)
    out = pd.DataFrame({"term": x, "coef": b, "se": se, "lo": b - tq * se, "hi": b + tq * se,
                        "p": 2 * (1 - stats.t.cdf(np.abs(b / np.where(se > 0, se, np.nan)), G - 1))})
    out.attrs.update({"n": n, "clusters": int(G), "vcov": V})
    return out


def lincomb(res: pd.DataFrame, weights: dict[str, float], level: float = 0.90) -> tuple[float, float, float]:
    """Point and interval of a linear combination of coefficients, using the stored vcov."""
    w = np.array([weights.get(t, 0.0) for t in res.term])
    est = float(w @ res.coef.to_numpy()); se = float(np.sqrt(w @ res.attrs["vcov"] @ w))
    tq = stats.t.ppf(0.5 + level / 2, res.attrs["clusters"] - 1)
    return est, est - tq * se, est + tq * se
