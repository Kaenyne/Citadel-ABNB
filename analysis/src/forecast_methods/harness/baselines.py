"""The five mandatory baselines, as functions, so no package re-implements them.

Every baseline is evaluated AT a guide date using only information knowable then:
quarters whose PRINT DATE is strictly before the guide date, plus the guide itself
(which is issued that evening) and a consensus value whose vintage precedes the date.

Replays
-------
PIT          : every parameter (AR(1) coefficients, cushion median, residual sd,
               street calibration ratio) estimated from the information set at the
               vintage date.
full_sample  : the same rule, but its PARAMETERS are estimated once on the full
               realised sample through 2026Q2. Inputs stay point-in-time; only
               parameter knowledge leaks. For `naive` and `naive_seasonal` the only
               parameter is the residual sd, so the two replays differ in interval
               width alone -- which is itself the honest statement.
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd

from . import paths as P
from . import quarters as Q
from . import windows as W
from .loaders import load_targets, history_as_of
from .registry import StreetVintageError, QUANTILE_LEVELS
from .spine import LEVEL_TARGETS, FLOW_PCT_TARGETS

_QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
_QTAUS = [QUANTILE_LEVELS[c] for c in _QCOLS]
_Z = dict(zip(_QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817,
                       0.0, 0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))


def _is_growth_like(metric: str) -> bool:
    return metric not in LEVEL_TARGETS or metric in FLOW_PCT_TARGETS


def _series(vintage_date, metric, targets=None) -> pd.Series:
    h = history_as_of(vintage_date, metric, targets)
    return pd.Series(h[metric].to_numpy(), index=h["quarter"].to_numpy())


def _full_series(metric, targets=None) -> pd.Series:
    t = load_targets() if targets is None else targets
    t = t[t["print_date"].notna()].sort_values("quarter")
    s = pd.Series(pd.to_numeric(t[metric], errors="coerce").to_numpy(),
                  index=t["quarter"].to_numpy()).dropna()
    return s


def _yoy_growth(s: pd.Series) -> pd.Series:
    idx = list(s.index)
    out = {}
    for q in idx:
        lag = Q.shift(q, -4)
        if lag in s.index and pd.notna(s[lag]) and s[lag] != 0:
            out[q] = 100.0 * (s[q] / s[lag] - 1.0)
    return pd.Series(out).sort_index()


# ---------------------------------------------------------------- point rules
def _rule_naive(s: pd.Series, q_target: str, metric: str):
    if _is_growth_like(metric):
        return (float(s.iloc[-1]), "last observed value") if len(s) else (np.nan, "no data")
    lag4 = Q.shift(q_target, -4)
    if lag4 not in s.index:
        return np.nan, f"no {lag4} in information set"
    g = _yoy_growth(s)
    if len(g) == 0:
        return float(s[lag4]), "y[q-4], no growth observable"
    return float(s[lag4] * (1.0 + g.iloc[-1] / 100.0)), \
        f"y[{lag4}] * (1 + g_last={g.iloc[-1]:.2f}%)"


def _rule_naive_seasonal(s: pd.Series, q_target: str, metric: str):
    if _is_growth_like(metric):
        return (0.0, "zero") if len(s) else (np.nan, "no data")
    lag4 = Q.shift(q_target, -4)
    if lag4 not in s.index:
        return np.nan, f"no {lag4} in information set"
    return float(s[lag4]), f"y[{lag4}] (zero y/y growth)"


def _rule_trailing4(s: pd.Series, q_target: str, metric: str):
    if _is_growth_like(metric):
        if len(s) < 4:
            return np.nan, "fewer than 4 observations"
        return float(s.iloc[-4:].mean()), "mean of last 4 observed values"
    lag4 = Q.shift(q_target, -4)
    if lag4 not in s.index:
        return np.nan, f"no {lag4} in information set"
    g = _yoy_growth(s)
    if len(g) < 4:
        return np.nan, "fewer than 4 y/y growths"
    gbar = float(g.iloc[-4:].mean())
    return float(s[lag4] * (1.0 + gbar / 100.0)), f"y[{lag4}] * (1 + mean4 g={gbar:.2f}%)"


def _fit_ar1(g: pd.Series):
    """OLS  g_t = a + b g_{t-1} + e.  Returns (a, b, sigma, n)."""
    x, y = [], []
    idx = list(g.index)
    for i in range(1, len(idx)):
        if Q.shift(idx[i], -1) == idx[i - 1]:
            x.append(g.iloc[i - 1]); y.append(g.iloc[i])
    if len(x) < 4:
        return np.nan, np.nan, np.nan, len(x)
    X = np.column_stack([np.ones(len(x)), np.asarray(x)])
    yv = np.asarray(y)
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    resid = yv - X @ beta
    dof = max(len(x) - 2, 1)
    return float(beta[0]), float(beta[1]), float(np.sqrt((resid ** 2).sum() / dof)), len(x)


def _rule_ar1(s: pd.Series, q_target: str, metric: str, params=None):
    g = s if _is_growth_like(metric) else _yoy_growth(s)
    if len(g) < 5:
        return np.nan, "fewer than 5 growth observations"
    a, b, _sig, _n = params if params is not None else _fit_ar1(g)
    if not np.isfinite(a):
        return np.nan, "AR(1) not estimable"
    last_q = g.index[-1]
    h = Q.to_index(q_target) - Q.to_index(last_q)
    if h < 1:
        return np.nan, "target already in information set"
    gh = float(g.iloc[-1])
    for _ in range(h):
        gh = a + b * gh
    if _is_growth_like(metric):
        return gh, f"AR(1) g a={a:.3f} b={b:.3f} h={h}"
    lag4 = Q.shift(q_target, -4)
    if lag4 not in s.index:
        return np.nan, f"no {lag4} in information set"
    return float(s[lag4] * (1.0 + gh / 100.0)), \
        f"y[{lag4}] * (1 + AR1 g={gh:.2f}%), a={a:.3f} b={b:.3f} h={h}"


_RULES = {
    "naive": _rule_naive,
    "naive_seasonal": _rule_naive_seasonal,
    "trailing4": _rule_trailing4,
    "ar1": _rule_ar1,
}


def _pseudo_oos_residuals(s_full_pit: pd.Series, metric: str, rule_name: str,
                          params=None, max_n: int = 12):
    """Relative errors of the same rule applied inside the information set."""
    idx = list(s_full_pit.index)
    errs = []
    for i in range(len(idx)):
        q = idx[i]
        hist = s_full_pit.iloc[:i]
        if len(hist) < 6:
            continue
        fn = _RULES[rule_name]
        pt, _ = fn(hist, q, metric, params) if rule_name == "ar1" else fn(hist, q, metric)
        if not np.isfinite(pt):
            continue
        y = float(s_full_pit.iloc[i])
        if _is_growth_like(metric):
            errs.append(y - pt)
        elif pt != 0:
            errs.append(y / pt - 1.0)
    return np.asarray(errs[-max_n:], dtype=float)


def _quantiles_from_sigma(point, sigma_rel, relative: bool):
    out = {}
    for c in _QCOLS:
        out[c] = point * (1.0 + _Z[c] * sigma_rel) if relative else point + _Z[c] * sigma_rel
    return out


def _wrap(point, sigma, relative, n_train, n_params, note, extra=None):
    if not np.isfinite(point):
        return None
    if not np.isfinite(sigma) or sigma <= 0:
        sigma = 0.02 if relative else 1.0
    d = {"point": float(point), "n_train": int(n_train), "n_params": int(n_params),
         "notes": note}
    d.update(_quantiles_from_sigma(point, sigma, relative))
    d["sd"] = abs(point) * sigma if relative else sigma
    if extra:
        d.update(extra)
    return d


# ------------------------------------------------------------- public baselines
def _generic(rule_name, vintage_date, target_quarter, metric, prior_basis, targets=None,
             n_params=0):
    q = Q.canon(target_quarter)
    s = _series(vintage_date, metric, targets)
    if len(s) == 0:
        return None
    params = None
    if rule_name == "ar1":
        g_pit = s if _is_growth_like(metric) else _yoy_growth(s)
        if prior_basis == "full_sample":
            sf = _full_series(metric, targets)
            g_fs = sf if _is_growth_like(metric) else _yoy_growth(sf)
            params = _fit_ar1(g_fs)
        else:
            params = _fit_ar1(g_pit)
    fn = _RULES[rule_name]
    pt, note = fn(s, q, metric, params) if rule_name == "ar1" else fn(s, q, metric)
    if prior_basis == "full_sample":
        s_for_res = _full_series(metric, targets)
    else:
        s_for_res = s
    res = _pseudo_oos_residuals(s_for_res, metric, rule_name, params)
    sigma = float(np.std(res, ddof=1)) if len(res) >= 3 else np.nan
    relative = not _is_growth_like(metric)
    extra_params = 1 if len(res) >= 3 else 0     # the residual sd is a fitted parameter
    return _wrap(pt, sigma, relative, len(s), n_params + extra_params,
                 f"{rule_name}: {note}; sigma from {len(res)} pseudo-oos errors "
                 f"({prior_basis})")


def baseline_naive(vintage_date, target_quarter, metric="revenue_musd",
                   prior_basis="PIT", targets=None):
    """y[q-4] * (1 + last observed y/y growth). Canonical RMSE-ratio denominator."""
    return _generic("naive", vintage_date, target_quarter, metric, prior_basis, targets, 0)


def baseline_naive_seasonal(vintage_date, target_quarter, metric="revenue_musd",
                            prior_basis="PIT", targets=None):
    """y[q-4]: zero y/y growth. Transparency object, NOT the ratio denominator."""
    return _generic("naive_seasonal", vintage_date, target_quarter, metric, prior_basis,
                    targets, 0)


def baseline_ar1(vintage_date, target_quarter, metric="revenue_musd",
                 prior_basis="PIT", targets=None):
    """OLS AR(1) on y/y growth, refit expanding, mapped back to the level via y[q-4]."""
    return _generic("ar1", vintage_date, target_quarter, metric, prior_basis, targets, 2)


def baseline_trailing4(vintage_date, target_quarter, metric="revenue_musd",
                       prior_basis="PIT", targets=None):
    """Mean of the last four observed y/y growths, applied to y[q-4]."""
    return _generic("trailing4", vintage_date, target_quarter, metric, prior_basis,
                    targets, 1)


def baseline_guide_cushion(vintage_date, target_quarter, metric="revenue_musd",
                           prior_basis="PIT", targets=None, n_cushion: int = 8):
    """guide_mid * (1 + c), c = MEDIAN trailing-8 actual/guide_mid - 1.

    The cushion pool contains only guides whose target quarter printed strictly before
    the vintage date. Revenue only.
    """
    if metric != "revenue_musd":
        return None
    t = load_targets() if targets is None else targets
    q = Q.canon(target_quarter)
    vd = pd.to_datetime(vintage_date).date() if isinstance(vintage_date, str) else vintage_date
    row = t[t["quarter"] == q]
    if len(row) == 0 or pd.isna(row["guide_mid"].iloc[0]):
        return None
    gmid = float(row["guide_mid"].iloc[0])
    pool = t[t["actual_over_guide_mid"].notna() & t["print_date"].notna()]
    if prior_basis == "PIT":
        pool = pool[pool["print_date"].map(lambda d: pd.notna(d) and d <= vd)]
    pool = pool.sort_values("quarter")
    ratios = pool["actual_over_guide_mid"].to_numpy(dtype=float)
    if prior_basis == "PIT":
        ratios = ratios[-n_cushion:]
    if len(ratios) < 3:
        return None
    c_med = float(np.median(ratios))
    pt = gmid * c_med
    qs = {c: gmid * float(np.quantile(ratios, tau)) for c, tau in zip(_QCOLS, _QTAUS)}
    d = {"point": pt, "n_train": int(len(ratios)), "n_params": 1,
         "sd": float(gmid * np.std(ratios, ddof=1)),
         "notes": (f"guide_mid={gmid:.0f} * median trailing-{len(ratios)} cushion "
                   f"{100*(c_med-1):+.2f}%; quantiles are the EMPIRICAL cushion "
                   f"quantiles ({prior_basis})")}
    d.update(qs)
    # np.quantile(ratios, 0.5) is the median, so q50 == point by construction.
    d["q50"] = pt
    return d


def baseline_street(vintage_date, target_quarter, metric="revenue_musd",
                    prior_basis="PIT", targets=None, n_cal: int = 8):
    """The vintage-stamped PRE-GUIDE Street consensus.

    Raises StreetVintageError if the only available consensus row postdates the vintage
    date -- which is exactly the kill-list rule "do not use the September vendor as the
    6-Aug pre-guide Street". ABNB reports after the close, so the print-morning
    consensus carried in `16_consensus_at_print_merged.next_q_cons_revenue_musd`
    precedes the letter and the guide on the same calendar day; as_of == vintage_date
    is therefore admissible, as_of > vintage_date is not.
    """
    if metric != "revenue_musd":
        return None
    t = load_targets() if targets is None else targets
    q = Q.canon(target_quarter)
    vd = pd.to_datetime(vintage_date).date() if isinstance(vintage_date, str) else vintage_date
    row = t[t["quarter"] == q]
    if len(row) == 0 or pd.isna(row["street_pre_guide_musd"].iloc[0]):
        return None
    val = float(row["street_pre_guide_musd"].iloc[0])
    vendor = row["street_pre_guide_vendor"].iloc[0]
    as_of = row["street_pre_guide_as_of"].iloc[0]
    if isinstance(as_of, str):
        as_of = pd.to_datetime(as_of).date()
    if as_of is not None and not pd.isna(as_of) and as_of > vd:
        raise StreetVintageError(
            f"pre-guide Street for {q} is stamped {as_of}, which POSTDATES the vintage "
            f"date {vd}. Refusing. (vendor={vendor}, value={val})")
    hist = t[t["street_pre_guide_musd"].notna() & t["revenue_musd"].notna()
             & t["print_date"].notna()]
    if prior_basis == "PIT":
        hist = hist[hist["print_date"].map(lambda d: pd.notna(d) and d <= vd)]
    ratios = (hist["revenue_musd"] / hist["street_pre_guide_musd"]).to_numpy(dtype=float)
    if prior_basis == "PIT":
        ratios = ratios[-n_cal:]
    sigma = float(np.std(ratios, ddof=1)) if len(ratios) >= 3 else 0.03
    d = _wrap(val, sigma, True, int(len(ratios)), 0,
              f"pre-guide Street vendor={vendor} as_of={as_of}; sigma from "
              f"{len(ratios)} actual/street ratios ({prior_basis})")
    if d is not None:
        d["street_vendor"] = str(vendor)
        d["street_as_of"] = as_of
        d["knowable_from"] = as_of
    return d


BASELINE_SPECS = [
    ("naive", baseline_naive, ["revenue_musd", "revenue_yoy", "gbv_musd", "nights_m"]),
    ("naive_seasonal", baseline_naive_seasonal,
     ["revenue_musd", "revenue_yoy", "gbv_musd", "nights_m"]),
    ("ar1", baseline_ar1, ["revenue_musd", "revenue_yoy", "gbv_musd", "nights_m"]),
    ("trailing4", baseline_trailing4,
     ["revenue_musd", "revenue_yoy", "gbv_musd", "nights_m"]),
    ("guide_cushion", baseline_guide_cushion, ["revenue_musd"]),
    ("street", baseline_street, ["revenue_musd"]),
]


def build_all_baselines(verbose: bool = True):
    """Build registry frames for every baseline object, both windows, both replays."""
    t = load_targets()
    frames = {}
    refusals = []
    for obj, fn, metrics in BASELINE_SPECS:
        rows = []
        for gdate, tq in W.GUIDE_EVENTS_ALL:
            wins = W.window_of_target(tq)
            if not wins:
                continue
            for metric in metrics:
                for basis in ("PIT", "full_sample"):
                    try:
                        r = fn(gdate, tq, metric=metric, prior_basis=basis, targets=t)
                    except StreetVintageError as e:
                        refusals.append(str(e))
                        r = None
                    if r is None:
                        continue
                    for win in wins:
                        row = {"method": "baselines", "object": obj, "target": metric,
                               "quarter": tq, "vintage_date": gdate,
                               "horizon_q": Q.to_index(tq) - Q.to_index(
                                   Q.quarter_of_date(gdate)),
                               "window": win, "prior_basis": basis,
                               "spec_id": f"{obj}|{metric}|{basis}"}
                        row.update(r)
                        rows.append(row)
        if rows:
            frames[obj] = pd.DataFrame(rows)
            if verbose:
                print(f"  baseline {obj:16s}: {len(rows):4d} rows, "
                      f"{frames[obj]['target'].nunique()} target(s)")
    if verbose and refusals:
        print(f"  street baseline refused {len(refusals)} vintage violation(s) "
              "(this is the rule working)")
    return frames, refusals
