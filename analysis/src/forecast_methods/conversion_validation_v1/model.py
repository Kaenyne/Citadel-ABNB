"""Five-parameter seasonal conversion model; all currency arrays are USD millions."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

FIXED_W = 2 / 3
GRID = np.linspace(0, 1, 201)


def quarter(q):
    q = str(q)
    if len(q) == 4 and q[1] == "Q":
        q = "20" + q[2:] + "Q" + q[0]
    if len(q) != 6 or q[4] != "Q" or q[5] not in "1234":
        raise ValueError("invalid fiscal quarter")
    return str(pd.Period(q, freq="Q"))


def shift(q, n):
    return str(pd.Period(quarter(q), freq="Q") + n)


def to_musd(values, units):
    scale = {"USD_millions": 1., "USD_billions": 1000., "USD": .000001}
    if units not in scale:
        raise ValueError("explicit supported GBV/revenue units required")
    a = np.asarray(values, dtype=float) * scale[units]
    if not np.isfinite(a).all() or (a <= 0).any():
        raise ValueError("currency values must be finite and positive")
    return a


def validate_panel(panel, as_of=None):
    d = panel.copy()
    need = {"quarter", "print_date", "gbv_musd", "revenue_musd"}
    if need - set(d):
        raise ValueError("missing panel columns")
    d["quarter"] = d.quarter.map(quarter)
    if d.quarter.duplicated().any():
        raise ValueError("duplicate fiscal quarters")
    d["print_date"] = pd.to_datetime(d.print_date, errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()
    if d.print_date.isna().any():
        raise ValueError("missing publication date")
    if as_of is not None and (d.print_date > pd.Timestamp(as_of).normalize()).any():
        raise ValueError("future supplied observation")
    for c in ["gbv_musd", "revenue_musd"]:
        d[c] = to_musd(d[c], "USD_millions")
    return d.sort_values("quarter").reset_index(drop=True)


def lag_rows(panel):
    d = validate_panel(panel)
    lookup = d.set_index("quarter")
    for k in [1, 2]:
        d[f"gbv_l{k}"] = d.quarter.map(lambda q: lookup.gbv_musd.get(shift(q, -k), np.nan))
        d[f"gbv_l{k}_date"] = d.quarter.map(lambda q: lookup.print_date.get(shift(q, -k), pd.NaT))
    d = d.dropna(subset=["gbv_l1", "gbv_l2"]).copy()
    d["season"] = d.quarter.str[-1].astype(int)
    d["year"] = d.quarter.str[:4].astype(int)
    return d


def profile(d, weights, loss="usd"):
    w = np.atleast_1d(np.asarray(weights, dtype=float))
    if w.ndim != 1 or not np.isfinite(w).all() or ((w < 0) | (w > 1)).any():
        raise ValueError("weight must lie in [0,1]")
    if loss not in ["usd", "relative"]:
        raise ValueError("unknown loss")
    a, b, y = (to_musd(d[c], "USD_millions") for c in ["gbv_l1", "gbv_l2", "revenue_musd"])
    seasons = d.season.to_numpy()
    if set(seasons) != {1, 2, 3, 4}:
        raise ValueError("all four seasons required")
    x = w[:, None]*a[None, :] + (1-w[:, None])*b[None, :]
    lambdas = np.empty((len(w), 4)); predicted = np.empty_like(x)
    for s in range(1, 5):
        mask = seasons == s
        xx, yy = x[:, mask], y[mask]
        if loss == "usd":
            lam = (xx*yy).sum(axis=1) / np.square(xx).sum(axis=1)
        else:
            z = xx/yy
            lam = z.sum(axis=1) / np.square(z).sum(axis=1)
        lambdas[:, s-1] = lam
        predicted[:, mask] = lam[:, None]*xx
    error = predicted-y if loss == "usd" else predicted/y-1
    return np.square(error).sum(axis=1), lambdas


def fit(d, weight=None, loss="usd", min_per_season=2):
    counts = d.groupby("season").size()
    if len(d) < 4*min_per_season or set(counts.index) != {1,2,3,4} or counts.min() < min_per_season:
        raise ValueError("insufficient training season coverage")
    if weight is not None:
        if isinstance(weight, (bool, np.bool_)) or not np.isscalar(weight):
            raise ValueError("one scalar weight required")
        candidates = [float(weight)]
    else:
        losses, _ = profile(d, GRID, loss)
        candidates = [0., 1., float(GRID[np.argmin(losses)])]
        # A one-dimensional global grid plus refinement of EVERY local minimum.
        for i in range(1, len(GRID)-1):
            if losses[i] <= losses[i-1] and losses[i] <= losses[i+1]:
                opt = minimize_scalar(lambda w: float(profile(d, [w], loss)[0][0]),
                                      bounds=(GRID[i-1], GRID[i+1]), method="bounded", options={"xatol": 1e-10})
                candidates.append(float(opt.x))
    losses, lambdas = profile(d, candidates, loss)
    best = min(range(len(candidates)), key=lambda i: (losses[i], candidates[i]))
    return {"w": candidates[best], "lambdas": lambdas[best], "loss": loss, "sse": float(losses[best]),
            "n": len(d), "n_parameters": 5 if weight is None else 4}


def fitted_values(d, fitted):
    x = fitted["w"]*d.gbv_l1.to_numpy()+(1-fitted["w"])*d.gbv_l2.to_numpy()
    return fitted["lambdas"][d.season.to_numpy(dtype=int)-1]*x


def predict(panel_known, target, as_of, weight=None, loss="usd"):
    """Supplied observations must already be truncated. Target outcome is forbidden."""
    p = validate_panel(panel_known, as_of)
    target = quarter(target)
    if target in set(p.quarter):
        raise ValueError("target outcome already supplied/printed")
    needed = [shift(target, -1), shift(target, -2)]
    values = p.set_index("quarter")
    if not set(needed).issubset(values.index):
        raise ValueError("required lagged GBV unavailable")
    train = lag_rows(p)
    train = train[train.quarter >= "2021Q1"]
    fitted = fit(train, weight, loss)
    a, b = values.loc[needed, "gbv_musd"].to_numpy()
    point = fitted["lambdas"][int(target[-1])-1]*(fitted["w"]*a+(1-fitted["w"])*b)
    return {**fitted, "quarter": target, "point": float(point), "training_quarters": train.quarter.tolist(),
            "max_input_date": p.print_date.max().strftime("%Y-%m-%d"),
            "last_train_outcome_date": train.print_date.max().strftime("%Y-%m-%d"),
            "gbv_l1": float(a), "gbv_l2": float(b),
            "lag1_print_date": values.loc[needed[0], "print_date"].strftime("%Y-%m-%d"),
            "lag2_print_date": values.loc[needed[1], "print_date"].strftime("%Y-%m-%d")}


def sequential_band(point, past_relative_errors):
    e = np.abs(np.asarray(past_relative_errors, dtype=float))[-8:]
    if not np.isfinite(e).all():
        raise ValueError("past errors must be finite")
    if len(e) < 6:
        return np.nan, np.nan, len(e)
    rank = int(np.ceil((len(e)+1)*.8))
    width = float(np.sort(e)[rank-1])
    return point*(1-width), point*(1+width), len(e)


def calibration_error(actual, point):
    """Forecast-denominated residual consistent with symmetric point*(1 +/- q)."""
    if not np.isfinite([actual, point]).all() or actual <= 0 or point <= 0:
        raise ValueError("positive finite actual and prediction required")
    return (actual-point)/point
