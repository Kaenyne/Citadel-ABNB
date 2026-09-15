"""Paired-loss significance for the margin scoreboard (added in the WS22 discussion round).

Why this exists. WS21 (`docs/margin-build/notes/21_red_team.md`, R01/R02/R08) showed that the
scoreboard's headline flag -- `survives_both_windows` AND `rw_survives_both_windows` -- is close to
free at this n: W2's 10 target quarters are a SUBSET of W1's 14 and the two weightings are highly
correlated, so a sign-flip null over the 74 margin h=0 PIT cells produces 22.1 survivors on average
against 25 observed (P = 0.39). A MAE ratio below 1 is therefore not evidence of skill on its own.
This module adds the missing number: a paired test of the loss differential

    d_q = |e_method(q)| - |e_baseline(q)|     on matched quarters

against `seasonal_naive` (the scorer's primary baseline) and `street` (the hardest margin baseline),
reported two ways:

  * `t_nw1_<baseline>` / `p_nw1_<baseline>` -- mean(d) over a Newey-West(1) standard error, two-sided
    normal p. NW(1) because consecutive quarters of the same rule share a fitted parameter; at n 10-14
    the t is indicative, not exact, and the p should be read as "is this bigger than the noise", not as
    a 5% decision rule.
  * `k_better_<baseline>` / `p_sign_<baseline>` -- the quarters-better count and the one-sided exact
    binomial sign test (ties dropped). Distribution-free and the honest statistic at this n.

Nothing here changes an existing scoreboard column: every column this module contributes is new.
The convention matches WS21 check_02 / check_10 exactly, so the discussion numbers and the scoreboard
numbers are the same numbers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

SIG_BASELINES = ("seasonal_naive", "street")
MIN_N_FOR_FLAG = 8          # R08: `beats_seasonal_naive` is asserted on as few as 2 matched quarters
# WS21 R03 / WS20 question 13: specs that condition on a realised driver are diagnostics, not forecasts.
# They were labelled by a naming convention only, and they top several rankings; this makes it a column.
ORACLE_MARKERS = ("revknown", "nightsknown", "ebitda_known")


def mark_oracle(sb: pd.DataFrame) -> pd.DataFrame:
    """Adds `is_oracle`: the spec conditions on a realised driver (revenue, nights or actual EBITDA)."""
    sb = sb.copy()
    txt = (sb.get("object", pd.Series("", index=sb.index)).astype(str) + "|"
           + sb.get("spec_id", pd.Series("", index=sb.index)).astype(str)).str.lower()
    sb["is_oracle"] = txt.apply(lambda s: any(m in s for m in ORACLE_MARKERS))
    return sb


def nw_se(d: np.ndarray, lag: int = 1) -> float:
    """Newey-West standard error of the mean of `d` with Bartlett weights (lag 1 by default)."""
    d = np.asarray(d, dtype=float)
    n = len(d)
    if n < 2:
        return float("nan")
    x = d - d.mean()
    v = float(x @ x) / n
    for l in range(1, lag + 1):
        if l < n:
            v += 2 * (1 - l / (lag + 1)) * float(x[l:] @ x[:-l]) / n
    return float(np.sqrt(max(v, 1e-12) / n))


def paired_loss_test(own_abs, base_abs) -> dict:
    """Paired test of |e_method| - |e_baseline| on matched quarters. Negative d = method better."""
    own = np.asarray(own_abs, dtype=float)
    base = np.asarray(base_abs, dtype=float)
    m = np.isfinite(own) & np.isfinite(base)
    own, base = own[m], base[m]
    n = len(own)
    out = {"n_cmp": n, "d_mean": np.nan, "t_nw1": np.nan, "p_nw1": np.nan,
           "k_better": np.nan, "p_sign": np.nan}
    if n < 3:
        return out
    d = own - base
    se = nw_se(d)
    t = d.mean() / se if se and np.isfinite(se) and se > 0 else np.nan
    k = int((d < 0).sum())
    n_eff = n - int((d == 0).sum())
    out.update({
        "d_mean": float(d.mean()),
        "t_nw1": float(t) if np.isfinite(t) else np.nan,
        "p_nw1": float(2 * (1 - stats.norm.cdf(abs(t)))) if np.isfinite(t) else np.nan,
        "k_better": k,
        "p_sign": (float(stats.binomtest(k, n_eff, 0.5, alternative="greater").pvalue)
                   if n_eff > 0 else np.nan),
    })
    return out


def significance_columns(own_abs_by_quarter: dict, bmaps: dict, target: str, window: str,
                         horizon: int, baselines=SIG_BASELINES) -> dict:
    """Columns for one scoreboard group.

    own_abs_by_quarter: {quarter: |error|} for the group's rows.
    bmaps: {baseline_object: {(target, window, horizon, quarter): (point, abs_err)}} -- the PIT replay
           of `baselines-margin`, exactly as `score._baseline_maps` builds it.
    """
    rec = {}
    qs = list(own_abs_by_quarter.keys())
    own = np.array([own_abs_by_quarter[q] for q in qs], dtype=float)
    for b in baselines:
        bm = bmaps.get(b, {})
        base = np.array([bm.get((target, window, int(horizon), q), (np.nan, np.nan))[1] for q in qs],
                        dtype=float)
        r = paired_loss_test(own, base)
        for k, v in r.items():
            rec[f"{k}_{b}"] = v
    return rec


def add_window_flags(sb: pd.DataFrame, key=("method", "object", "target", "horizon_q",
                                            "prior_basis", "spec_id")) -> pd.DataFrame:
    """Adds `n_min_both_windows` and the n-gated / significance-gated survivor flags (all new columns).

    `survives_both_windows_n8`  -- the existing flag AND at least MIN_N_FOR_FLAG matched quarters in
                                   BOTH windows (R08: the raw flag is asserted on as few as 2).
    `survives_both_windows_sig` -- that, AND the W1 sign test against seasonal_naive at p < 0.10.
                                   W1 is the longer sample and W2 is a subset of it, so W1 is where a
                                   claim has to show up; 0.10 because n 14 gives 11/14 a p of 0.029 and
                                   10/14 a p of 0.090, and nothing in this run is a 5% decision.
    """
    key = list(key)
    sb = sb.copy()
    n_by = {}
    p_by = {}
    for k_, g in sb.groupby(key, sort=False):
        w1 = g[g["window"] == "W1"]
        w2 = g[g["window"] == "W2"]
        ns = [int(x["n"]) for _, x in pd.concat([w1, w2]).iterrows()] or [0]
        n_by[tuple(k_)] = min(ns) if (len(w1) and len(w2)) else 0
        p_by[tuple(k_)] = float(w1["p_sign_seasonal_naive"].iloc[0]) if len(w1) and \
            "p_sign_seasonal_naive" in w1.columns and pd.notna(w1["p_sign_seasonal_naive"].iloc[0]) else np.nan
    tup = [tuple(r[c] for c in key) for _, r in sb.iterrows()]
    sb["n_min_both_windows"] = [n_by.get(t, 0) for t in tup]
    w1_sign = [p_by.get(t, np.nan) for t in tup]
    sb["w1_p_sign_seasonal_naive"] = w1_sign
    base = sb["survives_both_windows"] & sb["rw_survives_both_windows"] \
        if "rw_survives_both_windows" in sb.columns else sb["survives_both_windows"]
    sb["survives_both_windows_n8"] = base & (sb["n_min_both_windows"] >= MIN_N_FOR_FLAG)
    sb["survives_both_windows_sig"] = sb["survives_both_windows_n8"] & \
        pd.Series(w1_sign, index=sb.index).lt(0.10).fillna(False)
    return sb


def from_by_quarter(bq: pd.DataFrame, baseline_method: str = "baselines-margin",
                    group_keys=("method", "object", "target", "window", "horizon_q",
                                "prior_basis", "spec_id")) -> pd.DataFrame:
    """Recompute the significance columns straight from `scoreboard_by_quarter.csv`.

    Used by `significance_check.py` so the numbers are available without re-running the scorer; the
    per-group arithmetic is the same function the scorer calls.
    """
    gk = list(group_keys)
    d = bq.copy()
    d["spec_id"] = d["spec_id"].fillna("").astype(str)
    b = d[(d["method"] == baseline_method) & (d["prior_basis"] == "PIT")]
    bmaps = {}
    for obj, g in b.groupby("object"):
        g = g.drop_duplicates(["target", "window", "horizon_q", "quarter"])
        bmaps[obj] = {(r.target, r.window, int(r.horizon_q), r.quarter): (float(r.point), float(r.abs_err))
                      for r in g.itertuples()}
    rows = []
    for keys, g in d.groupby(gk, sort=True):
        rec = dict(zip(gk, keys))
        rec["n"] = len(g)
        own = {r.quarter: float(r.abs_err) for r in g.itertuples()}
        rec.update(significance_columns(own, bmaps, rec["target"], rec["window"], rec["horizon_q"]))
        rows.append(rec)
    return pd.DataFrame(rows)
