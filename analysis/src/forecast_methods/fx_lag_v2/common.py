"""fx_lag_v2 / common.py -- COPY of fx_lag/common.py.

CHANGES: OUT points at data/processed/forecast_methods/fx_lag_v2/, METHOD is
"fx-lag-v2", and FX_DAILY / FX_QUARTERLY point at the 2026-09-11 refresh written
by fetch_fx_v2.py.  Nothing under fx_lag/ or overnight/ is read for FX prices and
nothing there is ever written.

All paths resolve relative to this file so the package runs from anywhere.
"""
from __future__ import annotations

import datetime as _dt
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import optimize, stats

HERE = pathlib.Path(__file__).resolve().parent
FM = HERE.parent                      # analysis/src/forecast_methods
REPO = FM.parent.parent.parent        # repo root
OVN = REPO / "data" / "processed" / "overnight"
L0 = REPO / "data" / "processed" / "forecast_methods" / "L0"
OUT = REPO / "data" / "processed" / "forecast_methods" / "fx_lag_v2"
REG = REPO / "data" / "processed" / "forecast_methods" / "registry"
HARNESS_OUT = REPO / "data" / "processed" / "forecast_methods" / "harness"
OUT.mkdir(parents=True, exist_ok=True)
REG.mkdir(parents=True, exist_ok=True)

if str(FM) not in sys.path:
    sys.path.insert(0, str(FM))

TODAY = _dt.date(2026, 9, 11)
METHOD = "fx-lag-v2"

# the refreshed FX, written by fetch_fx_v2.py.  FRED H.10 publishes with a lag, so
# the last observation is 2026-09-04, not 2026-09-11.  Stated everywhere.
FX_DAILY = OUT / "fx_daily_2026-09-11.csv"
FX_QUARTERLY = OUT / "fx_quarterly_2026-09-11.csv"
FX_LAST_OBS = _dt.date(2026, 9, 4)

# ---------------------------------------------------------------- quarters
def to_period(s) -> pd.Period:
    """'1Q22' or '2022Q1' -> Period."""
    s = str(s).strip()
    if s[0].isdigit() and s[1].upper() == "Q":          # 1Q22
        return pd.Period(f"20{s[2:4]}Q{s[0]}", freq="Q")
    return pd.Period(s, freq="Q")


def short(p) -> str:
    p = p if isinstance(p, pd.Period) else to_period(p)
    return f"{p.quarter}Q{str(p.year)[2:]}"


def canon(p) -> str:
    p = p if isinstance(p, pd.Period) else to_period(p)
    return f"{p.year}Q{p.quarter}"


def write(df: pd.DataFrame, name: str) -> pathlib.Path:
    """Progressive write: every stage lands on disk as soon as it is computed."""
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"  wrote {name}  ({len(df)} rows)")
    return path


# ------------------------------------------------- interval log-likelihood
def interval_loglik(mu, lo, hi, sigma) -> float:
    """Sum log[ Phi((hi-mu)/s) - Phi((lo-mu)/s) ].

    This is the ONLY admissible likelihood for letter-rounded integers.
    A Gaussian point likelihood on a series with six exact zeros and a
    rounding half-width of 0.5pp against a residual sd near 1pp is not
    admissible and is never used in this package.
    """
    sigma = max(float(sigma), 1e-6)
    z_hi = (np.asarray(hi) - np.asarray(mu)) / sigma
    z_lo = (np.asarray(lo) - np.asarray(mu)) / sigma
    p = stats.norm.cdf(z_hi) - stats.norm.cdf(z_lo)
    p = np.clip(p, 1e-300, None)
    return float(np.sum(np.log(p)))


def profile_sigma(mu, lo, hi, s_grid=None) -> tuple[float, float]:
    """Profile out sigma on a grid; returns (loglik, sigma_hat)."""
    if s_grid is None:
        s_grid = np.concatenate([np.arange(0.05, 2.0, 0.01), np.arange(2.0, 8.0, 0.05)])
    lls = np.array([interval_loglik(mu, lo, hi, s) for s in s_grid])
    i = int(np.argmax(lls))
    return float(lls[i]), float(s_grid[i])


def fit_interval_linear(X, lo, hi, nonneg=False, x0=None):
    """Max interval-likelihood linear fit.  Returns dict with coef, sigma, loglik."""
    X = np.asarray(X, float)
    k = X.shape[1]

    def nll(theta):
        coef = theta[:k]
        sigma = np.exp(theta[k])
        return -interval_loglik(X @ coef, lo, hi, sigma)

    if x0 is None:
        mid = (np.asarray(lo) + np.asarray(hi)) / 2.0
        try:
            b0 = np.linalg.lstsq(X, mid, rcond=None)[0]
        except Exception:
            b0 = np.zeros(k)
        x0 = np.concatenate([b0, [np.log(1.0)]])
    bounds = [(0, None) if nonneg else (None, None) for _ in range(k)] + [(np.log(1e-3), np.log(20))]
    best = None
    for jitter in range(6):
        start = np.array(x0, float)
        if jitter:
            rng = np.random.default_rng(jitter)
            start = start + rng.normal(0, 0.25, size=start.shape)
            if nonneg:
                start[:k] = np.abs(start[:k])
        r = optimize.minimize(nll, start, method="L-BFGS-B", bounds=bounds)
        if best is None or r.fun < best.fun:
            best = r
    coef = best.x[:k]
    sigma = float(np.exp(best.x[k]))
    return {"coef": coef, "sigma": sigma, "loglik": -float(best.fun), "n": len(lo), "k": k}
