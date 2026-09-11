"""I0. Shared helpers for workstream I: the note-08 backtest protocol (expanding walk-forward
OLS refit strictly before each scored period, scored against naive last value, same period
prior year and AR(1); 1,000-shuffle permutation p on Pearson r), copied from
analysis/src/q3nowcast/E5_backtest.py so every term in this workstream is scored identically.
"""
import numpy as np, pandas as pd

RNG = np.random.default_rng(20260911)
QORDER = [f"{q}Q{y:02d}" for y in range(19, 28) for q in (1, 2, 3, 4)]


def qkey(q):
    return QORDER.index(q)


def q_from_period(p):  # '2025Q3' -> '3Q25'
    return f"{p[5]}Q{p[2:4]}"


def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0:
        return np.nan, np.nanmean(y)
    b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    return b, y.mean() - b * x.mean()


def perm_p(x, y, n=1000):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan, np.nan, int(len(x))
    r0 = np.corrcoef(x, y)[0, 1]
    idx = RNG.random((n, len(x))).argsort(axis=1)
    xp = x[idx]
    xm = xp - xp.mean(axis=1, keepdims=True)
    ym = y - y.mean()
    denom = np.sqrt((xm ** 2).sum(axis=1) * (ym ** 2).sum())
    r = (xm @ ym) / np.where(denom == 0, np.nan, denom)
    cnt = int(np.nansum(np.abs(r) >= abs(r0)))
    return float(r0), (cnt + 1) / (n + 1), int(len(x))


def walkforward(x, y, start, season_lag=4, min_fit=4):
    """x, y aligned arrays in time order; start = first index scored. Returns dict of RMSEs and ratios."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    e_f, e_n, e_p, e_a, sg, ts = [], [], [], [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < min_fit or not np.isfinite(x[t]) or not np.isfinite(y[t]) or not np.isfinite(y[t - 1]):
            continue
        b, a = ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred):
            continue
        e_f.append(pred - y[t]); e_n.append(y[t - 1] - y[t])
        e_p.append((y[t - season_lag] - y[t]) if t >= season_lag and np.isfinite(y[t - season_lag]) else np.nan)
        yl, yy = ys[:-1], ys[1:]
        m = np.isfinite(yl) & np.isfinite(yy)
        if m.sum() >= min_fit:
            b2, a2 = ols(yl[m], yy[m])
            e_a.append(a2 + b2 * y[t - 1] - y[t])
        else:
            e_a.append(np.nan)
        sg.append(np.sign(pred - y[t - 1]) == np.sign(y[t] - y[t - 1]))
        ts.append(t)
    if len(e_f) < 3:
        return None
    r = lambda e: float(np.sqrt(np.nanmean(np.asarray(e, float) ** 2))) if np.isfinite(np.asarray(e, float)).sum() else np.nan
    out = dict(wf_n=len(e_f), wf_rmse=r(e_f), wf_rmse_naive=r(e_n), wf_rmse_prior=r(e_p), wf_rmse_ar1=r(e_a))
    out["wf_ratio_vs_naive"] = out["wf_rmse"] / out["wf_rmse_naive"] if out["wf_rmse_naive"] else np.nan
    out["wf_ratio_vs_prior"] = out["wf_rmse"] / out["wf_rmse_prior"] if out["wf_rmse_prior"] else np.nan
    out["wf_ratio_vs_ar1"] = out["wf_rmse"] / out["wf_rmse_ar1"] if out["wf_rmse_ar1"] else np.nan
    out["sign_acc"] = float(np.mean(sg))
    out["wf_first_t"], out["wf_last_t"] = ts[0], ts[-1]
    return out


def score(feature_name, x, y, labels, start_label, knowable, season_lag=4):
    """One row of the note-08 scoreboard for feature x against target y (aligned lists, labels = quarters)."""
    r0, p, n = perm_p(x, y)
    start = labels.index(start_label) if start_label in labels else max(4, len(labels) // 2)
    wf = walkforward(x, y, start, season_lag) or {}
    row = dict(feature=feature_name, n=n, r=r0, perm_p=p, knowable_before_print=knowable,
               wf_start=labels[start] if start < len(labels) else None)
    row.update(wf)
    return row
