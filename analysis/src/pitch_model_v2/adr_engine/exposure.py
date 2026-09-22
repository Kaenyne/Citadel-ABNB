"""adr_engine / exposure.py — the pass-through model. V0 = pure translation (beta = 1). V1 = beta_r fitted by MAP
under Normal(1, 0.25^2) priors with the interval (rounding-aware) Gaussian likelihood; sigma ~ HalfNormal(1pp).
V2/V3 = OLS on a single proxy (euro, broad dollar). Full posterior for the in-sample estimate via PyMC (optional)."""
from __future__ import annotations
import numpy as np
from scipy import optimize, stats
from . import config as C


def interval_loglik(mu, y, h, sigma):
    """log P(y - h <= y* <= y + h) under y* ~ N(mu, sigma^2); clipped for numerical safety."""
    p = stats.norm.cdf((y + h - mu) / sigma) - stats.norm.cdf((y - h - mu) / sigma)
    return np.log(np.clip(p, 1e-12, None))


def neg_log_post(theta, X, y, h):
    beta, log_sigma = theta[:-1], theta[-1]
    sigma = np.exp(log_sigma)
    mu = X @ beta
    ll = interval_loglik(mu, y, h, sigma).sum()
    lp = stats.norm.logpdf(beta, C.BETA_PRIOR_MEAN, C.BETA_PRIOR_SD).sum()
    lp += stats.halfnorm.logpdf(sigma, scale=C.SIGMA_PRIOR_SD) + log_sigma   # Jacobian of log transform
    return -(ll + lp)


def fit_v1_map(X: np.ndarray, y: np.ndarray, h: np.ndarray) -> dict:
    k = X.shape[1]
    x0 = np.r_[np.ones(k), np.log(0.5)]
    best = None
    for s0 in (np.log(0.3), np.log(0.6), np.log(1.2)):
        x0[-1] = s0
        r = optimize.minimize(neg_log_post, x0, args=(X, y, h), method="L-BFGS-B",
                              bounds=[(0.0, 2.5)] * k + [(np.log(0.05), np.log(5.0))])
        if best is None or r.fun < best.fun:
            best = r
    return {"beta": best.x[:-1], "sigma": float(np.exp(best.x[-1])), "nlp": float(best.fun), "ok": bool(best.success)}


def predict_v0(Xrow: np.ndarray) -> float:
    return float(Xrow.sum())


def predict_v1(Xrow: np.ndarray, beta: np.ndarray) -> float:
    return float(Xrow @ beta)


def fit_ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    A = np.c_[np.ones_like(x), x]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0]), float(coef[1])


def fit_v1_nuts(X, y, h, draws=1500, tune=1500, chains=4, seed=21):
    """Full posterior with PyMC. Returns a dict of draws or None if PyMC is unavailable."""
    try:
        import pymc as pm
        import pytensor.tensor as pt
    except Exception as e:      # pragma: no cover
        return None
    with pm.Model():
        beta = pm.Normal("beta", mu=C.BETA_PRIOR_MEAN, sigma=C.BETA_PRIOR_SD, shape=X.shape[1])
        sigma = pm.HalfNormal("sigma", sigma=C.SIGMA_PRIOR_SD)
        mu = pt.dot(X, beta)
        z_hi = (y + h - mu) / sigma
        z_lo = (y - h - mu) / sigma
        Phi = lambda z: 0.5 * (1 + pt.erf(z / np.sqrt(2.0)))
        p = pt.clip(Phi(z_hi) - Phi(z_lo), 1e-12, 1.0)
        pm.Potential("interval_lik", pt.log(p).sum())
        idata = pm.sample(draws=draws, tune=tune, chains=chains, random_seed=seed, progressbar=False,
                          target_accept=0.9, cores=1)
    post = idata.posterior
    b = post["beta"].stack(s=("chain", "draw")).values.T          # (n_draws, k)
    s = post["sigma"].stack(s=("chain", "draw")).values
    import arviz as az
    summ = az.summary(idata, var_names=["beta", "sigma"])
    return {"beta_draws": b, "sigma_draws": s, "summary": summ}
