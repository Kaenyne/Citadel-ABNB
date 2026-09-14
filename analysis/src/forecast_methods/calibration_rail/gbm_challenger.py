#!/usr/bin/env python
"""Part (b): monotone-constrained GBM challenger.

Two objects, same 4 PIT features, nested expanding-window CV:
  gbm_revenue        -- predicts revenue_yoy (mapped back to revenue_musd via y[q-4])
  gbm_surprise_guide -- predicts (actual/guide_mid - 1)*100 ("surprise vs the guide
                         midpoint"; mapped back the same way)

Features (<=4, all strictly point-in-time at the guide date):
  f1  lag1_revenue_yoy  -- revenue_yoy of quarter q-1 (already printed by the guide
                            date for q, since the guide for q is issued alongside the
                            q-1 print)
  f2  lag1_gbv_yoy       -- gbv_yoy of quarter q-1
  f3  guide_growth_pct   -- (guide_mid(q) / y[q-4] - 1) * 100; knowable at the guide
                            date because the guide for q IS issued at that date
  f4  fx_adr_lag2        -- fx_pts_adr of quarter q-2, the ADR-FX channel at the
                            2-quarter booking-to-recognition lead the standing orders
                            ask to test. Full-sample sign check (n=15, lag2):
                            r=-0.436, p=0.104 (permutation, one-sided direction only,
                            NOT the sign-prior survivor -- that lives on the ADR-FX
                            target itself per the addendum, r=-0.95 p=0.001; this is a
                            weaker, separate relationship on revenue_yoy). Monotonic
                            constraint = DECREASING is applied to this feature ONLY.
                            f1-f3 carry NO constraint.

This is the ONLY feature in the model with a monotone constraint, per the addendum:
"apply the monotone constraint on the USD-to-ADR-FX channel only (the audit shows
USD-to-nights has the wrong sign and p 0.27)." No nights feature is used at all here,
so there is nothing to mis-constrain.

Hyperparameters are chosen by a small inner grid (nested, nothing outside the training
window at that origin) over (max_depth, min_samples_leaf), scored by one-step-ahead
expanding MAE strictly inside the training set.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

import _common  # noqa: F401
from harness import (  # noqa: E402
    load_targets, register, windows as W, quarters as Q, history_as_of,
)

FEATURES = ["lag1_revenue_yoy", "lag1_gbv_yoy", "guide_growth_pct", "fx_adr_lag2"]
MONO_CST = [0, 0, 0, -1]          # decreasing on fx_adr_lag2 only
GRID = [(1, 2), (1, 3), (2, 2), (2, 3)]   # (max_depth, min_samples_leaf)
N_PARAMS_NOMINAL = 4              # 4 features; effective dof reported separately


def _row_features(hist: pd.DataFrame, q: str, t_full: pd.DataFrame):
    """Feature vector for target quarter q.

    f1/f2/f4 (lag1/lag1/lag2 of already-printed quarters) come from `hist`, a table
    already cut to the point-in-time information set (print_date <= vintage_date) --
    this is what enforces PIT correctness for the lagged-actuals features.

    guide_mid(q) and y[q-4] come from `t_full` (unfiltered): guide_mid(q) is knowable
    at the guide date because it IS the guide being issued that date (the row for q
    itself has no print_date yet, which is exactly why it is absent from `hist` --
    that is not a PIT violation, it is why we read it from the unfiltered table
    instead). y[q-4] is always safely printed long before q's guide date.
    """
    idx = hist.set_index("quarter")
    full = t_full.set_index("quarter")
    q1, q2, q4 = Q.shift(q, -1), Q.shift(q, -2), Q.shift(q, -4)
    try:
        f1 = float(idx.loc[q1, "revenue_yoy"]) if q1 in idx.index else np.nan
        f2 = float(idx.loc[q1, "gbv_yoy"]) if q1 in idx.index else np.nan
        f4 = float(idx.loc[q2, "fx_pts_adr"]) if q2 in idx.index else np.nan
        gmid = float(full.loc[q, "guide_mid"]) if q in full.index and pd.notna(
            full.loc[q, "guide_mid"]) else np.nan
        y4 = float(full.loc[q4, "revenue_musd"]) if q4 in full.index and pd.notna(
            full.loc[q4, "revenue_musd"]) else np.nan
        f3 = (gmid / y4 - 1.0) * 100.0 if np.isfinite(gmid) and np.isfinite(y4) and y4 else np.nan
    except KeyError:
        return None
    v = [f1, f2, f3, f4]
    if any((x is None) or (isinstance(x, float) and not np.isfinite(x)) for x in v):
        return None
    return v


def _target_value(t: pd.DataFrame, q: str, mode: str):
    idx = t.set_index("quarter")
    if q not in idx.index or pd.isna(idx.loc[q, "revenue_musd"]):
        return None
    if mode == "revenue_yoy":
        return float(idx.loc[q, "revenue_yoy"]) if pd.notna(idx.loc[q, "revenue_yoy"]) else None
    if mode == "surprise_guide":
        gmid = idx.loc[q, "guide_mid"] if "guide_mid" in idx.columns else np.nan
        if pd.isna(gmid) or gmid == 0:
            return None
        return float(idx.loc[q, "revenue_musd"] / gmid - 1.0) * 100.0
    raise ValueError(mode)


def _map_to_level(t: pd.DataFrame, q: str, mode: str, pred: float):
    idx = t.set_index("quarter")
    if mode == "revenue_yoy":
        q4 = Q.shift(q, -4)
        if q4 not in idx.index or pd.isna(idx.loc[q4, "revenue_musd"]):
            return np.nan
        return float(idx.loc[q4, "revenue_musd"]) * (1.0 + pred / 100.0)
    if mode == "surprise_guide":
        if q not in idx.index or pd.isna(idx.loc[q, "guide_mid"]):
            return np.nan
        return float(idx.loc[q, "guide_mid"]) * (1.0 + pred / 100.0)
    raise ValueError(mode)


def _build_training_table(hist: pd.DataFrame, mode: str, t_full: pd.DataFrame,
                          exclude_quarter: str | None = None):
    """All (features, y) pairs buildable strictly inside `hist` (a PIT-cut frame).

    `exclude_quarter` is a leave-one-out guard for the full_sample replay: the
    harness's own "full_sample" convention (baselines.py) lets PARAMETERS leak (fit
    once on the whole realised series) while inputs stay point-in-time. For a
    non-parametric model with n~15-20 and features that can isolate a single row,
    literally including the target quarter's own (features, actual) pair as a
    training example is a materially worse leak than a 2-coefficient AR(1) fit, so it
    is excluded even in the full_sample replay. This is a deliberate, documented
    deviation from the letter of the AR(1) convention, not an oversight.
    """
    quarters = sorted(hist["quarter"].unique())
    if exclude_quarter is not None:
        quarters = [q for q in quarters if q != exclude_quarter]
    X, y, qs = [], [], []
    for q in quarters:
        feats = _row_features(hist, q, t_full)
        yv = _target_value(hist, q, mode)
        if feats is None or yv is None:
            continue
        X.append(feats); y.append(yv); qs.append(q)
    return np.array(X, dtype=float), np.array(y, dtype=float), qs


def _inner_select_hparams(X, y, qs):
    """One-step-ahead expanding MAE inside the training set. Returns best (depth, leaf)."""
    n = len(y)
    if n < 8:
        return GRID[0]           # too small to tune; use the mildest setting
    best, best_mae = GRID[0], np.inf
    for depth, leaf in GRID:
        errs = []
        start = max(5, n - 6)    # evaluate on the last few points only (n is tiny)
        for i in range(start, n):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = HistGradientBoostingRegressor(
                    max_depth=depth, min_samples_leaf=leaf, max_iter=40,
                    learning_rate=0.15, l2_regularization=1.0,
                    monotonic_cst=MONO_CST, random_state=0)
                m.fit(X[:i], y[:i])
            errs.append(abs(float(m.predict(X[i:i + 1])[0]) - y[i]))
        if errs:
            mae = float(np.mean(errs))
            if mae < best_mae:
                best_mae, best = mae, (depth, leaf)
    return best


def _fit_predict(X_train, y_train, x_target, depth, leaf):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = HistGradientBoostingRegressor(
            max_depth=depth, min_samples_leaf=leaf, max_iter=40, learning_rate=0.15,
            l2_regularization=1.0, monotonic_cst=MONO_CST, random_state=0)
        m.fit(X_train, y_train)
    pred = float(m.predict(np.array([x_target]))[0])
    resid = y_train - m.predict(X_train)
    sigma = float(np.std(resid, ddof=1)) if len(resid) >= 3 else float(np.std(y_train)) or 5.0
    n_leaves_used = getattr(m, "n_iter_", 40)
    return pred, sigma, n_leaves_used


_Z = {"q05": -1.645, "q10": -1.282, "q25": -0.674, "q50": 0.0,
      "q75": 0.674, "q90": 1.282, "q95": 1.645}


def build_object(obj_name: str, mode: str, t_full: pd.DataFrame, verbose=True):
    rows = []
    for gdate, tq in W.GUIDE_EVENTS_ALL:
        wins = W.window_of_target(tq)
        if not wins:
            continue
        for basis in ("PIT", "full_sample"):
            if basis == "PIT":
                hist = history_as_of(gdate, targets=t_full)
            else:
                # full_sample replay: PARAMETERS estimated once on the realised
                # sample through 2026Q2 (same convention as harness baselines.py);
                # inputs at the target quarter itself are still the PIT ones.
                hist = t_full[t_full["print_date"].notna()].copy()
            X, y, qs = _build_training_table(hist, mode, t_full, exclude_quarter=tq)
            if len(y) < 5:
                continue
            depth, leaf = _inner_select_hparams(X, y, qs)
            hist_for_target = hist if basis == "full_sample" else history_as_of(gdate, targets=t_full)
            x_target = _row_features(hist_for_target, tq, t_full)
            if x_target is None:
                continue
            pred, sigma, n_iter_used = _fit_predict(X, y, x_target, depth, leaf)
            # map to level with t_full (unfiltered): guide_mid(tq) and y[tq-4] are both
            # knowable at the guide date (see _row_features docstring); tq itself is
            # never used as a lookup KEY for its own actual here, only guide_mid/y[q-4].
            point = _map_to_level(t_full, tq, mode, pred)
            if not np.isfinite(point):
                continue
            # quantiles: Gaussian in the growth/surprise space, mapped to level
            qvals = {}
            for k, z in _Z.items():
                qvals[k] = _map_to_level(t_full, tq, mode, pred + z * sigma)
            for win in wins:
                rows.append({
                    "method": "calibration-rail", "object": obj_name,
                    "target": "revenue_musd", "quarter": tq, "vintage_date": gdate,
                    "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(gdate)),
                    "point": point, "window": win, "prior_basis": basis,
                    "n_params": N_PARAMS_NOMINAL, "n_train": int(len(y)),
                    "sd": abs(qvals["q95"] - qvals["q05"]) / (2 * 1.645) if np.isfinite(
                        qvals["q95"]) else np.nan,
                    "spec_id": f"{obj_name}|depth={depth},leaf={leaf},iter={n_iter_used}|"
                               f"mono=fx_adr_lag2(-1)|{basis}",
                    "notes": f"GBM({mode}); nested-CV depth={depth} leaf={leaf}",
                    **qvals,
                })
    df = pd.DataFrame(rows)
    if len(df) == 0:
        if verbose:
            print(f"  {obj_name}: NO ROWS BUILT (insufficient training data)")
        return None
    register(df, allow_single_replay=False, quiet=False)
    return df


def main() -> int:
    t = load_targets()
    print("[gbm] building gbm_revenue (target = revenue_yoy)")
    build_object("gbm_revenue", "revenue_yoy", t)
    print("[gbm] building gbm_surprise_guide (target = surprise vs guide midpoint)")
    build_object("gbm_surprise_guide", "surprise_guide", t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
