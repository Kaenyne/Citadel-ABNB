"""guidance-policy: shared primitives.

The guidance POLICY FUNCTION, in one place:

    guide_mid_q   = E[Revenue_q] / (1 + c)          c = trailing-8 cushion (mean)
    print_q       = guide_mid_q * (1 + c)           (the inverse; they are one object)
    cons_at_print = guide_mid_q * (1 + kappa)       kappa = at-print Street over guide mid
    E[Revenue_q]  = lambda_season(q) * [w*GBV_{q-1} + (1-w)*GBV_{q-2}]     w = 2/3

Free parameters of the POLICY layer: c and kappa -> 2.
The kernel (4 seasonal lambdas + 1 lag weight) is owned by package kernel-lambda; it is
recomputed here locally so this package does not block on it, and its parameters are
counted separately wherever an object consumes it.

CUSHION DEFINITION (binding): actual / guide_midpoint - 1.  Directly observed and
kernel-free.  NEVER guide/model, which absorbs kernel bias one-for-one.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PKG_DIR = Path(__file__).resolve().parent
FM_DIR = PKG_DIR.parent                      # analysis/src/forecast_methods
REPO = FM_DIR.parents[2]                     # Citadel-ABNB
OUT = REPO / "data" / "processed" / "forecast_methods" / "guidance_policy"
OVN = REPO / "data" / "processed" / "overnight"
PROC = REPO / "data" / "processed"
L0 = REPO / "data" / "processed" / "forecast_methods" / "L0"

if str(FM_DIR) not in sys.path:
    sys.path.insert(0, str(FM_DIR))

METHOD = "guidance-policy"
SEASON_W = 2.0 / 3.0          # published kernel weight (sensitivity 0.33..0.667)
LAMBDA_K = 3                  # same-season observations used for lambda_s
TODAY = pd.Timestamp("2026-09-11").date()

# Nights / GBV bucket vocabulary, read off the letters in 02_guidance_ledger.csv.
BUCKET_WORDS = {
    "mid-single-digit": (4.0, 6.0),
    "high-single-digit": (7.0, 9.0),
    "low-double-digit": (10.0, 12.0),
    "low-teens": (12.0, 14.0),
    "mid-teens": (14.0, 16.0),
}


def out(name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    return OUT / name


def write(df: pd.DataFrame, name: str) -> Path:
    p = out(name)
    df.to_csv(p, index=False)
    print(f"  wrote {name:44s} rows={len(df):4d}")
    return p


# ------------------------------------------------------------------ bootstrap
def moving_block_bootstrap(x, stat=np.mean, block: int = 4, B: int = 5000, seed: int = 20261005):
    """Moving-block bootstrap CI for a statistic of a short, serially-dependent series."""
    x = np.asarray([v for v in x if np.isfinite(v)], dtype=float)
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    b = int(min(block, n))
    nb = int(np.ceil(n / b))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n - b + 1, size=(B, nb))
    reps = np.empty(B)
    for i in range(B):
        samp = np.concatenate([x[s:s + b] for s in starts[i]])[:n]
        reps[i] = stat(samp)
    return float(stat(x)), float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5)), n


# ------------------------------------------------------------------ kernel
def lambda_table(tg: pd.DataFrame, w: float = SEASON_W) -> pd.DataFrame:
    """lambda_q = Revenue_q / [w*GBV_{q-1} + (1-w)*GBV_{q-2}], in percent, for every quarter."""
    t = tg.sort_values("quarter").reset_index(drop=True)
    rev = dict(zip(t["quarter"], pd.to_numeric(t["revenue_musd"], errors="coerce")))
    gbv = dict(zip(t["quarter"], pd.to_numeric(t["gbv_musd"], errors="coerce")))
    from harness import quarters as Q
    rows = []
    for q in t["quarter"]:
        q1, q2 = Q.shift(q, -1), Q.shift(q, -2)
        if q1 in gbv and q2 in gbv and np.isfinite(gbv.get(q1, np.nan)) \
                and np.isfinite(gbv.get(q2, np.nan)) and np.isfinite(rev.get(q, np.nan)):
            base = w * gbv[q1] + (1 - w) * gbv[q2]
            rows.append({"quarter": q, "season": int(q[-1]), "revenue_musd": rev[q],
                         "gbv_lag1": gbv[q1], "gbv_lag2": gbv[q2], "base_musd": base,
                         "lambda_pct": 100.0 * rev[q] / base, "weight_w": w})
    return pd.DataFrame(rows)


def lambda_hat(lam: pd.DataFrame, season: int, k: int = LAMBDA_K) -> tuple[float, int]:
    """Mean of the most recent k same-season lambdas available in the given table."""
    s = lam[lam["season"] == season].sort_values("quarter")
    if len(s) == 0:
        return np.nan, 0
    use = s.tail(k)
    return float(use["lambda_pct"].mean()), int(len(use))


# ------------------------------------------------------------------ cushion
def cushion_window(hist: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    """Trailing-n realised cushions available in a point-in-time history slice."""
    h = hist[hist["actual_over_guide_mid"].notna()].sort_values("quarter")
    return h.tail(n)


def cushion_stats(hist: pd.DataFrame, n: int = 8) -> dict:
    w = cushion_window(hist, n)
    c = 100.0 * (pd.to_numeric(w["actual_over_guide_mid"], errors="coerce") - 1.0)
    c = c.dropna().to_numpy(dtype=float)
    if len(c) == 0:
        return {"c_mean_pct": np.nan, "c_median_pct": np.nan, "c_sd_pp": np.nan, "n_cushion": 0}
    return {"c_mean_pct": float(np.mean(c)),
            "c_median_pct": float(np.median(c)),
            "c_sd_pp": float(np.std(c, ddof=1)) if len(c) > 1 else np.nan,
            "n_cushion": int(len(c))}


# ------------------------------------------------------------------ quantiles
_Z = {"q05": -1.6448536269514722, "q10": -1.2815515655446004, "q25": -0.6744897501960817,
      "q50": 0.0, "q75": 0.6744897501960817, "q90": 1.2815515655446004,
      "q95": 1.6448536269514722}


def gauss_quantiles(point: float, sd: float) -> dict:
    return {k: point + z * sd for k, z in _Z.items()}
