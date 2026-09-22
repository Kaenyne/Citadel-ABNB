"""Walk-forward scorer. ols() and walkforward() are E5_backtest.py's functions, unchanged, so that v2 is scored on
exactly the record's yardstick (test_scoring.py reproduces E5's 0.683209). Added: score_window(), a moving-block
bootstrap interval for the RMSE ratio, and a Diebold-Mariano test with the Harvey-Leybourne-Newbold correction."""
import numpy as np, pandas as pd
from scipy import stats


def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0:
        return np.nan, np.nanmean(y)
    b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    return b, y.mean() - b * x.mean()


def walkforward(x, y, start, season_lag):
    """x, y aligned arrays indexed 0..n-1 in time order. start = first index scored. (E5, verbatim, plus preds.)"""
    e_f, e_n, e_p, e_a, sg, ts, pr = [], [], [], [], [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < 4 or not np.isfinite(x[t]) or not np.isfinite(y[t]):
            continue
        b, a = ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred) or not np.isfinite(y[t - 1]):
            continue
        e_f.append(pred - y[t]); e_n.append(y[t - 1] - y[t]); pr.append(pred)
        e_p.append((y[t - season_lag] - y[t]) if t >= season_lag and np.isfinite(y[t - season_lag]) else np.nan)
        yl, yy = ys[:-1], ys[1:]
        m = np.isfinite(yl) & np.isfinite(yy)
        if m.sum() >= 4:
            b2, a2 = ols(yl[m], yy[m]); e_a.append(a2 + b2 * y[t - 1] - y[t])
        else:
            e_a.append(np.nan)
        sg.append(np.sign(pred - y[t - 1]) == np.sign(y[t] - y[t - 1]))
        ts.append(t)
    if len(e_f) < 4:
        return None
    r = lambda e: float(np.sqrt(np.nanmean(np.asarray(e, float) ** 2))) if np.isfinite(np.asarray(e, float)).sum() else np.nan
    return dict(wf_n=len(e_f), wf_rmse=r(e_f), wf_rmse_naive=r(e_n), wf_rmse_prior=r(e_p), wf_rmse_ar1=r(e_a),
                wf_ratio_vs_naive=r(e_f) / r(e_n) if r(e_n) else np.nan,
                wf_ratio_vs_prior=r(e_f) / r(e_p) if r(e_p) else np.nan,
                wf_ratio_vs_ar1=r(e_f) / r(e_a) if r(e_a) else np.nan,
                sign_acc=float(np.mean(sg)), mean_err=float(np.mean(e_f)), _path=(ts, e_f, e_n, pr))


def score_window(x, y, window_start, score_start, season_lag=4, score_end=None):
    """x, y: Series indexed by the same integer period key (qi or ymi). Contiguous index is rebuilt so lag
    baselines are honest (E5 convention). score_end (inclusive) truncates the series before scoring."""
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    df = df[(df.index >= window_start) & ((df.index <= score_end) if score_end is not None else True)].sort_index()
    if len(df) < 7:
        return None
    full = pd.DataFrame(index=range(int(df.index.min()), int(df.index.max()) + 1)).join(df)
    xa, ya = full.x.to_numpy(float), full.y.to_numpy(float)
    start = max(4, int(np.searchsorted(full.index.to_numpy(), score_start)))
    res = walkforward(xa, ya, start, season_lag)
    if res is None:
        return None
    ts, ef, en, pr = res.pop("_path")
    res["path"] = pd.DataFrame({"t": [int(full.index[t]) for t in ts], "pred": pr,
                                "actual": [ya[t] for t in ts], "err_feature": ef, "err_naive": en})
    return res


def ratio_interval(ef, en, B=2000, block=2, seed=20260918, q=(0.05, 0.95)):
    """Moving-block bootstrap (block = 2 periods) of the RMSE ratio over the scored periods."""
    rng = np.random.default_rng(seed); ef = np.asarray(ef, float); en = np.asarray(en, float); n = len(ef)
    out = []
    for _ in range(B):
        starts = rng.integers(0, n - block + 1, size=int(np.ceil(n / block)))
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        out.append(np.sqrt(np.mean(ef[idx] ** 2)) / np.sqrt(np.mean(en[idx] ** 2)))
    return float(np.quantile(out, q[0])), float(np.quantile(out, q[1]))


def dm_test(ef, en):
    """Diebold-Mariano on squared loss, h = 1, HLN small-sample factor sqrt((n-1)/n), two-sided p on t(n-1).
    Negative statistic = feature loss below naive loss."""
    d = np.asarray(ef, float) ** 2 - np.asarray(en, float) ** 2
    n = len(d); v = d.var(ddof=1) / n
    if n < 3 or v == 0:
        return np.nan, np.nan
    dm = d.mean() / np.sqrt(v) * np.sqrt((n - 1) / n)
    return float(dm), float(2 * (1 - stats.t.cdf(abs(dm), df=n - 1)))
