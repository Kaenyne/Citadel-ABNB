"""M2 (margin build, Sep 2026): time-series and ratio methods for adjusted EBITDA margin and the
cash cost lines. Method `margin-ts`, seven objects, registered through the margin harness (WS10).

Objects (see docs/margin-build/notes/M2_margin_ts.md for the pre-registration):
  yoy_margin_change     margin[q-4] + weighted mean of the last k y/y margin changes
  incremental_margin    EBITDA[q-4] + m (Rev_hat - Rev[q-4]), m from the last k y/y pairs
  pct_rev_seasonal      line % of revenue = last year's ratio + drift; six components; EBITDA = Rev - sum
  per_night_seasonal    line per night = last year's x (1 + growth) x nights leg; EBITDA = Rev - sum
  sarima_margin         small SARIMAX grid, AICc-selected on the training window (margin; log lines)
  ensemble_simple       equal / inverse-past-MAE mean of the main specs of the four above
  q_sentence_direction  margin[q-4] + k x sign(management's quarterly margin sentence), k fitted PIT

Everything is evaluated point-in-time: at each vintage only quarters printed on or before the
vintage are visible (harness `history_as_of`), revenue comes from the frozen-harness PIT leg and
nights from a naive rule; parameters are re-estimated at each vintage (`PIT`) or taken from the
full sample at TODAY and applied everywhere (`full_sample`).
"""
from __future__ import annotations

import datetime as _dt
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))

from harness_margin import (  # noqa: E402
    load_targets, history_as_of, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE, TODAY,
    windows_for, register, revenue_forecast_pit, q_guide_in_force, load_street, Q,
)
from harness_margin.baselines import (  # noqa: E402
    RELATIVE_METRICS, H_BACKTEST, H_LIVE, RESID_MAX_N, MIN_RESID, FALLBACK_SIGMA_REL, FALLBACK_SIGMA_PP,
)

METHOD = "margin-ts"
SLUG = "M2_margin_ts"
OUT = REPO / "data" / "processed" / "margin_build" / SLUG
FIG = REPO / "analysis" / "figures" / "margin_build"
WS06 = REPO / "data" / "processed" / "margin_build" / "06_fy27_path_v2"
WS03 = REPO / "data" / "processed" / "margin_build" / "03_consensus_pit"
HALF_LIFE = 4.0
LINES = ["cor", "ops", "pd", "sm", "ga"]
VINTAGES_ALL = list(GUIDE_DATES_ALL) + [TODAY]
LIVE_VINTAGES = [GUIDE_DATE_LIVE, TODAY]
LAST_REGISTERED_Q = "2027Q4"
LIVE_QUARTERS = [Q.shift("2026Q3", i) for i in range(10)]          # 3Q26 .. 4Q28 (FY28 for the annual file)
QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
ZS = dict(zip(QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817, 0.0,
                      0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))
MAIN_SPEC = {"yoy_margin_change": "k4_rw", "incremental_margin": "k4_rw", "pct_rev_seasonal": "drift_k4_rw",
             "per_night_seasonal": "g_k4_rw", "sarima_margin": "margin_aicc", "ensemble_simple": "invmae4",
             "q_sentence_direction": "k_fit_rw"}
LOG = []


def log(msg: str):
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------- state at a vintage
def _vd(x) -> _dt.date:
    return pd.to_datetime(x).date()


def build_state(vd, targets) -> dict:
    """Series (indexed by quarter) visible at vintage vd."""
    h = history_as_of(vd, None, targets).set_index("quarter")
    st = {"vd": _vd(vd), "n": len(h), "knowable_from": h["print_date"].max() if len(h) else None}
    st["margin"] = h["adj_ebitda_margin_pct"].astype(float)
    st["ebitda"] = h["adj_ebitda_musd"].astype(float)
    st["rev"] = h["revenue_musd"].astype(float)
    st["nights"] = h["nights_m"].astype(float)
    st["total"] = h["total_cash_costs_musd"].astype(float)
    lines = {}
    for ln in LINES:
        col = "ga_cash_ex_reserves_musd" if ln == "ga" else f"{ln}_cash_musd"
        lines[ln] = h[col].astype(float)
    st["lines"] = lines
    st["other"] = st["total"] - sum(lines.values())          # add-backs; about -0.5% of revenue
    st["ratio"] = {ln: 100.0 * s / st["rev"] for ln, s in lines.items()}
    st["ratio"]["other"] = 100.0 * st["other"] / st["rev"]
    st["pn"] = {ln: s / st["nights"] for ln, s in lines.items()}
    st["pn"]["other"] = st["other"] / st["nights"]
    st["T"] = h.index[-1] if len(h) else None
    return st


def rw_weights(quarters, T, mode) -> np.ndarray:
    n = len(quarters)
    if n == 0:
        return np.array([])
    if mode == "ew":
        return np.ones(n) / n
    w = np.array([0.5 ** ((Q.to_index(T) - Q.to_index(q)) / HALF_LIFE) for q in quarters], dtype=float)
    return w / w.sum()


def yoy(s: pd.Series) -> pd.Series:
    out = {}
    for q in s.index:
        lag = Q.shift(q, -4)
        if lag in s.index and np.isfinite(s[q]) and np.isfinite(s[lag]):
            out[q] = float(s[q] - s[lag])
    return pd.Series(out, dtype=float)


def yoy_growth(s: pd.Series) -> pd.Series:
    out = {}
    for q in s.index:
        lag = Q.shift(q, -4)
        if lag in s.index and s[lag] > 0 and s[q] > 0:
            out[q] = float(s[q] / s[lag] - 1.0)
    return pd.Series(out, dtype=float)


def last_k_stat(ch: pd.Series, k: int, mode: str, stat: str = "mean") -> float:
    if len(ch) == 0:
        return np.nan
    last = ch.iloc[-k:]
    if stat == "median":
        return float(np.median(last.to_numpy()))
    w = rw_weights(list(last.index), last.index[-1], mode)
    return float(np.sum(last.to_numpy() * w))


# ----------------------------------------------------------------------------- inputs (revenue, nights)
_ADOPTED = {}


def load_adopted_path() -> pd.DataFrame:
    """Revenue and nights by quarter and scenario: WS06 (3Q26/4Q26 = bridge v3), FY28 base from the wide file."""
    if "p" in _ADOPTED:
        return _ADOPTED["p"]
    wide = pd.read_csv(WS06 / "06_revenue_path_wide.csv")
    wide["quarter"] = wide["quarter"].map(Q.canon)
    p = wide[["quarter", "scenario", "revenue_musd", "nights_mm"]].copy()
    v2b = WS06 / "06_revenue_path_3q26_4q27_v2b.csv"
    src = "06_revenue_path_wide.csv (+ 06_revenue_path_3q26_4q27.csv)"
    if v2b.exists():
        lo = pd.read_csv(v2b)
        lo["quarter"] = lo["quarter"].map(Q.canon)
        lo = lo[lo["line"].isin(["revenue_musd", "nights_mm"])]
        piv = lo.pivot_table(index=["quarter", "scenario"], columns="line", values="value").reset_index()
        p = p.merge(piv, on=["quarter", "scenario"], how="left", suffixes=("", "_v2b"))
        for c in ("revenue_musd", "nights_mm"):
            p[c] = p[f"{c}_v2b"].fillna(p[c])
        p = p[["quarter", "scenario", "revenue_musd", "nights_mm"]]
        src = "06_revenue_path_3q26_4q27_v2b.csv overriding 06_revenue_path_wide.csv"
    p["source"] = src
    _ADOPTED["p"] = p
    return p


def adopted(q: str, scenario: str, what: str) -> float:
    p = load_adopted_path()
    r = p[(p["quarter"] == q) & (p["scenario"] == scenario)]
    if len(r) == 0:
        return np.nan
    return float(r["revenue_musd" if what == "rev" else "nights_mm"].iloc[0])


def nights_naive(st: dict, q: str, cache: dict) -> float:
    """nights[q-4] x (1 + last observed y/y nights growth), chained when q-4 is itself a forecast."""
    N = st["nights"]
    if len(N) == 0:
        return np.nan
    T = N.index[-1]
    lagT = Q.shift(T, -4)
    g = N[T] / N[lagT] - 1.0 if lagT in N.index else np.nan
    lag = Q.shift(q, -4)
    if lag in N.index:
        base = N[lag]
    elif lag in cache:
        base = cache[lag]
    else:
        base = nights_naive(st, lag, cache)
    v = base * (1.0 + g)
    cache[q] = v
    return v


class Inputs:
    """Revenue and nights for a quarter at a vintage: PIT legs, actuals (diagnostic) or the adopted LIVE path."""

    def __init__(self, st, pb, scenario=None, rev_known=False, nights_known=False, targets=None):
        self.st, self.pb, self.scenario = st, pb, scenario
        self.rev_known, self.nights_known = rev_known, nights_known
        self.t = targets
        self._ncache = {}
        self.leg = {}

    def rev(self, q):
        if q in self.st["rev"].index:
            return float(self.st["rev"][q])
        if self.rev_known:
            a = self.t.loc[self.t["quarter"] == q, "revenue_musd"]
            return float(a.iloc[0]) if len(a) and pd.notna(a.iloc[0]) else np.nan
        if self.scenario is not None:
            v = adopted(q, self.scenario, "rev")
            self.leg[q] = f"adopted_{self.scenario}"
            return v
        v, leg = revenue_forecast_pit(self.st["vd"], q, self.pb)
        self.leg[q] = leg
        return float(v)

    def nights(self, q):
        if q in self.st["nights"].index:
            return float(self.st["nights"][q])
        if self.nights_known:
            a = self.t.loc[self.t["quarter"] == q, "nights_m"]
            return float(a.iloc[0]) if len(a) and pd.notna(a.iloc[0]) else np.nan
        if self.scenario is not None:
            return adopted(q, self.scenario, "nights")
        return nights_naive(self.st, q, self._ncache)


# ----------------------------------------------------------------------------- object 1: yoy_margin_change
SPECS_YOY = {"k4_rw": (4, "rw", 1.0), "k2_rw": (2, "rw", 1.0), "k4_ew": (4, "ew", 1.0), "k2_ew": (2, "ew", 1.0),
             "k4_rw_shrink50": (4, "rw", 0.5)}


def fit_yoy(st, spec):
    k, mode, shrink = SPECS_YOY[spec]
    return {"delta": shrink * last_k_stat(yoy(st["margin"]), k, mode), "n_params": 2 + (1 if shrink != 1.0 else 0)}


def fc_yoy(st, qs, params, inp):
    out = {}
    for q in qs:
        lag = Q.shift(q, -4)
        base = float(st["margin"][lag]) if lag in st["margin"].index else out.get(lag, {}).get("adj_ebitda_margin_pct", np.nan)
        m = base + params["delta"]
        rev = inp.rev(q)
        out[q] = {"adj_ebitda_margin_pct": m, "adj_ebitda_musd": m / 100.0 * rev,
                  "note": f"margin[{lag}]={base:.2f} + delta {params['delta']:+.2f}; rev={rev:.0f}"}
    return out


# ----------------------------------------------------------------------------- object 2: incremental_margin
SPECS_INCR = {"k4_rw": (4, "rw", "mean", False), "k8_rw": (8, "rw", "mean", False), "k4_ew": (4, "ew", "mean", False),
              "k8_ew": (8, "ew", "mean", False), "k8_median": (8, "ew", "median", False),
              "k4_rw_revknown": (4, "rw", "mean", True)}


def incr_series(st) -> pd.Series:
    E, R = st["ebitda"], st["rev"]
    out = {}
    for q in E.index:
        lag = Q.shift(q, -4)
        if lag in E.index and abs(R[q] - R[lag]) >= 0.10 * abs(R[lag]):
            out[q] = float((E[q] - E[lag]) / (R[q] - R[lag]))
    return pd.Series(out, dtype=float)


def fit_incr(st, spec):
    k, mode, stat, _ = SPECS_INCR[spec]
    return {"m": last_k_stat(incr_series(st), k, mode, stat), "n_params": 2}


def fc_incr(st, qs, params, inp):
    out = {}
    for q in qs:
        lag = Q.shift(q, -4)
        if lag in st["ebitda"].index:
            e0, r0 = float(st["ebitda"][lag]), float(st["rev"][lag])
        else:
            e0, r0 = out.get(lag, {}).get("adj_ebitda_musd", np.nan), inp.rev(lag)
        rev = inp.rev(q)
        e = e0 + params["m"] * (rev - r0)
        out[q] = {"adj_ebitda_musd": e, "adj_ebitda_margin_pct": 100.0 * e / rev,
                  "note": f"E[{lag}]={e0:.0f} + m {params['m']:.3f} x (rev {rev:.0f} - {r0:.0f})"}
    return out


# ----------------------------------------------------------------------------- object 3: pct_rev_seasonal
SPECS_PCT = {"drift_k4_rw": (4, "rw", True, False), "drift_k4_ew": (4, "ew", True, False), "drift_k8_rw": (8, "rw", True, False),
             "nodrift": (4, "rw", False, False), "drift_k4_rw_revknown": (4, "rw", True, True)}


def fit_pct(st, spec):
    k, mode, drift, _ = SPECS_PCT[spec]
    d = {ln: (last_k_stat(yoy(st["ratio"][ln]), k, mode) if drift else 0.0) for ln in LINES}
    return {"drift": d, "n_params": 6 if drift else 1}


def fc_pct(st, qs, params, inp):
    out = {}
    comps = LINES + ["other"]
    for q in qs:
        lag = Q.shift(q, -4)
        rev = inp.rev(q)
        r_hat = {}
        for c in comps:
            if lag in st["ratio"][c].index:
                base = float(st["ratio"][c][lag])
            else:
                base = out.get(lag, {}).get(f"_ratio_{c}", np.nan)
            r_hat[c] = base + (params["drift"].get(c, 0.0) if c != "other" else 0.0)
        tot_ratio = sum(r_hat.values())
        row = {f"_ratio_{c}": r_hat[c] for c in comps}
        for ln in LINES:
            row[f"{ln}_cash_pct_rev"] = r_hat[ln]
            row[f"{ln}_cash_musd"] = r_hat[ln] / 100.0 * rev
        row["ga_cash_ex_reserves_musd"] = row["ga_cash_musd"]
        row["total_cash_costs_pct_rev"] = tot_ratio
        row["total_cash_costs_musd"] = tot_ratio / 100.0 * rev
        row["adj_ebitda_margin_pct"] = 100.0 - tot_ratio
        row["adj_ebitda_musd"] = rev - row["total_cash_costs_musd"]
        row["note"] = ("ratios[" + lag + "] + drift " + ", ".join(f"{ln} {params['drift'][ln]:+.2f}" for ln in LINES)
                       + f"; other {r_hat['other']:+.2f}; rev={rev:.0f}")
        out[q] = row
    return out


# ----------------------------------------------------------------------------- object 4: per_night_seasonal
SPECS_PN = {"g_k4_rw": (4, "rw", True, False), "g_k4_ew": (4, "ew", True, False), "g_k8_rw": (8, "rw", True, False),
            "nogrowth": (4, "rw", False, False), "g_k4_rw_nightsknown": (4, "rw", True, True)}


def fit_pn(st, spec):
    k, mode, growth, _ = SPECS_PN[spec]
    g = {ln: (last_k_stat(yoy_growth(st["pn"][ln]), k, mode) if growth else 0.0) for ln in LINES}
    return {"growth": g, "n_params": 6 if growth else 1}


def fc_pn(st, qs, params, inp):
    out = {}
    comps = LINES + ["other"]
    for q in qs:
        lag = Q.shift(q, -4)
        rev, nights = inp.rev(q), inp.nights(q)
        pn_hat = {}
        for c in comps:
            if lag in st["pn"][c].index:
                base = float(st["pn"][c][lag])
            else:
                base = out.get(lag, {}).get(f"_pn_{c}", np.nan)
            pn_hat[c] = base * (1.0 + (params["growth"].get(c, 0.0) if c != "other" else 0.0))
        row = {f"_pn_{c}": pn_hat[c] for c in comps}
        tot = 0.0
        for c in comps:
            usd = pn_hat[c] * nights
            tot += usd
            if c != "other":
                row[f"{c}_cash_per_night"] = pn_hat[c]
                row[f"{c}_cash_musd"] = usd
        row["ga_cash_ex_reserves_musd"] = row["ga_cash_musd"]
        row["total_cash_costs_musd"] = tot
        row["adj_ebitda_musd"] = rev - tot
        row["adj_ebitda_margin_pct"] = 100.0 * (rev - tot) / rev
        row["note"] = ("per-night[" + lag + "] x (1+g) " + ", ".join(f"{ln} {100*params['growth'][ln]:+.1f}%" for ln in LINES)
                       + f"; nights={nights:.1f}; rev={rev:.0f}")
        out[q] = row
    return out


# ----------------------------------------------------------------------------- object 5: sarima_margin
SARIMA_CANDIDATES = [  # (order, seasonal_order, trend, n_params)
    ((0, 0, 0), (0, 1, 0, 4), "c", 1),
    ((1, 0, 0), (0, 1, 0, 4), "c", 2),
    ((0, 0, 0), (0, 1, 1, 4), "c", 2),
    ((0, 1, 1), (0, 1, 1, 4), "n", 2),
]
SARIMA_START = "2021Q1"


def _sarima_fit(y: np.ndarray, cand):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    order, sorder, trend, _ = cand
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mod = SARIMAX(y, order=order, seasonal_order=sorder, trend=trend, enforce_stationarity=False,
                      enforce_invertibility=False)
        res = mod.fit(disp=False, maxiter=200)
    return mod, res


def sarima_select(y: np.ndarray):
    """AICc-selected candidate on the training window; returns (cand, params, aicc) or None."""
    best = None
    n_diff = len(y) - 4
    for cand in SARIMA_CANDIDATES:
        order, sorder, trend, npar = cand
        if n_diff - order[1] < npar + 3:
            continue
        try:
            mod, res = _sarima_fit(y, cand)
            aicc = float(res.aicc) if np.isfinite(res.aicc) else float(res.aic)
        except Exception:
            continue
        if best is None or aicc < best[2]:
            best = (cand, np.asarray(res.params, dtype=float), aicc)
    return best


def sarima_forecast(y: np.ndarray, steps: int, cand, params) -> np.ndarray:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    order, sorder, trend, _ = cand
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mod = SARIMAX(y, order=order, seasonal_order=sorder, trend=trend, enforce_stationarity=False,
                      enforce_invertibility=False)
        res = mod.filter(params)
        return np.asarray(res.forecast(steps=steps), dtype=float)


def _series_from(st, key, sub=None) -> pd.Series:
    s = st[key] if sub is None else st[key][sub]
    return s[[q for q in s.index if q >= SARIMA_START]]


def fit_sarima(st, spec):
    """Order selection and parameters on the training window (PIT) or full sample (full_sample)."""
    out = {"n_params": 0}
    if spec == "margin_aicc":
        y = _series_from(st, "margin").to_numpy()
        sel = sarima_select(y)
        out["margin"] = sel
        out["n_params"] = (sel[0][3] + 1) if sel else 0
    else:
        tot = 0
        for ln in LINES:
            y = np.log(_series_from(st, "lines", ln).clip(lower=1.0).to_numpy())
            sel = sarima_select(y)
            out[ln] = sel
            tot += (sel[0][3] + 1) if sel else 0
        out["n_params"] = tot
    return out


def fc_sarima(st, qs, params, inp, spec):
    out = {}
    T = st["T"]
    steps = max(Q.to_index(q) - Q.to_index(T) for q in qs)
    if spec == "margin_aicc":
        sel = params.get("margin")
        if sel is None:
            return out
        y = _series_from(st, "margin").to_numpy()
        f = sarima_forecast(y, steps, sel[0], sel[1])
        for q in qs:
            m = float(f[Q.to_index(q) - Q.to_index(T) - 1])
            rev = inp.rev(q)
            out[q] = {"adj_ebitda_margin_pct": m, "adj_ebitda_musd": m / 100.0 * rev,
                      "note": f"SARIMA{sel[0][0]}x{sel[0][1]} trend={sel[0][2]} aicc={sel[2]:.1f}; rev={rev:.0f}"}
        return out
    fcs = {}
    for ln in LINES:
        sel = params.get(ln)
        if sel is None:
            return out
        y = np.log(_series_from(st, "lines", ln).clip(lower=1.0).to_numpy())
        fcs[ln] = (np.exp(sarima_forecast(y, steps, sel[0], sel[1])), sel)
    for q in qs:
        i = Q.to_index(q) - Q.to_index(T) - 1
        rev = inp.rev(q)
        lag = Q.shift(q, -4)
        other_ratio = float(st["ratio"]["other"][lag]) if lag in st["ratio"]["other"].index else out.get(lag, {}).get("_ratio_other", np.nan)
        row = {"_ratio_other": other_ratio}
        tot = other_ratio / 100.0 * rev
        for ln in LINES:
            v = float(fcs[ln][0][i])
            row[f"{ln}_cash_musd"] = v
            row[f"{ln}_cash_pct_rev"] = 100.0 * v / rev
            tot += v
        row["ga_cash_ex_reserves_musd"] = row["ga_cash_musd"]
        row["total_cash_costs_musd"] = tot
        row["adj_ebitda_musd"] = rev - tot
        row["adj_ebitda_margin_pct"] = 100.0 * (rev - tot) / rev
        row["note"] = "log-line SARIMA " + ", ".join(f"{ln}:{fcs[ln][1][0][0]}x{fcs[ln][1][0][1]}" for ln in LINES) + f"; rev={rev:.0f}"
        out[q] = row
    return out


# ----------------------------------------------------------------------------- object 7: q_sentence_direction
DIR = {"ceiling": -1, "floor": 1, "point": 0}
SPECS_SENT = {"k_fit_rw": ("fit", "rw", "mean"), "k_fit_ew": ("fit", "ew", "mean"), "k_fit_median": ("fit", "ew", "median"),
              "k_abs_rw": ("abs", "rw", "mean")}


def sentence_dir(vd, q, targets):
    g = q_guide_in_force(vd, q, targets)
    if g is None or g.get("guide_type") is None:
        return None
    return DIR.get(g["guide_type"]), g


def fit_sentence(st, spec, targets):
    kind, mode, stat = SPECS_SENT[spec]
    ch = yoy(st["margin"])
    if kind == "abs":
        return {"k": last_k_stat(ch.abs(), 8, mode), "n_params": 1, "pool_n": min(8, len(ch))}
    pool = []
    for q in ch.index:
        r = sentence_dir(st["vd"], q, targets)
        if r is None or r[0] in (None, 0):
            continue
        pool.append((q, r[0], ch[q]))
    if len(pool) == 0:
        return {"k": np.nan, "n_params": 1, "pool_n": 0}
    qs = [p[0] for p in pool]
    d = np.array([p[1] for p in pool], dtype=float)
    dl = np.array([p[2] for p in pool], dtype=float)
    if stat == "median":
        k = float(np.median(d * dl))
    else:
        w = rw_weights(qs, qs[-1], mode)
        k = float(np.sum(w * d * dl) / np.sum(w * d * d))
    return {"k": k, "n_params": 1, "pool_n": len(pool)}


def fc_sentence(st, qs, params, inp, targets):
    out = {}
    for q in qs:
        r = sentence_dir(st["vd"], q, targets)
        if r is None or r[0] is None:
            continue
        d, g = r
        lag = Q.shift(q, -4)
        if lag not in st["margin"].index:
            continue
        m = float(st["margin"][lag]) + params["k"] * d
        rev = inp.rev(q)
        out[q] = {"adj_ebitda_margin_pct": m, "adj_ebitda_musd": m / 100.0 * rev,
                  "note": f"margin[{lag}]={st['margin'][lag]:.2f} {'+' if d >= 0 else '-'} k {abs(params['k']):.2f} "
                          f"(d={d:+d}, {g['guide_type']} {g['guide_id']}, pool n={params['pool_n']}); rev={rev:.0f}"}
    return out


# ----------------------------------------------------------------------------- grid
OBJECTS = {
    "yoy_margin_change": (SPECS_YOY, fit_yoy, fc_yoy),
    "incremental_margin": (SPECS_INCR, fit_incr, fc_incr),
    "pct_rev_seasonal": (SPECS_PCT, fit_pct, fc_pct),
    "per_night_seasonal": (SPECS_PN, fit_pn, fc_pn),
}


def _known_flags(obj, spec):
    if obj == "incremental_margin":
        return SPECS_INCR[spec][3], False
    if obj == "pct_rev_seasonal":
        return SPECS_PCT[spec][3], False
    if obj == "per_night_seasonal":
        return False, SPECS_PN[spec][3]
    return False, False


def _rows_from(fc: dict, obj, spec, pb, st, h_of, extra: dict, scenario=None):
    rows = []
    for q, vals in fc.items():
        for tgt, v in vals.items():
            if tgt.startswith("_") or tgt == "note" or not np.isfinite(v):
                continue
            rows.append({"object": obj, "spec_id": spec, "prior_basis": pb, "target": tgt, "quarter": q,
                         "vintage_date": st["vd"], "horizon_q": h_of(q), "point": float(v), "n_train": st["n"],
                         "knowable_from": st["knowable_from"], "notes": vals.get("note", ""), "scenario": scenario or "",
                         **extra})
    return rows


def build_grid(targets, include_sarima=True, verbose=True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Every object x spec x replay at every vintage and horizon (backtest + LIVE base), plus a
    LIVE scenario frame (base / bear / bull at TODAY, 3Q26-4Q28)."""
    st_full = build_state(TODAY, targets)
    full_params = {}
    for obj, (specs, fit, _) in OBJECTS.items():
        for spec in specs:
            full_params[(obj, spec)] = fit(st_full, spec)
    for spec in SPECS_SENT:
        full_params[("q_sentence_direction", spec)] = fit_sentence(st_full, spec, targets)
    if include_sarima:
        for spec in ("margin_aicc", "lines_aicc"):
            full_params[("sarima_margin", spec)] = fit_sarima(st_full, spec)
    rows, live_rows, param_rows = [], [], []
    for vd in VINTAGES_ALL:
        st = build_state(vd, targets)
        is_live = vd in LIVE_VINTAGES
        q0 = Q.quarter_of_date(_vd(vd))
        hmax = H_LIVE if is_live else H_BACKTEST
        qs = [Q.shift(q0, h) for h in range(hmax + 1)]
        if vd == TODAY:
            qs = LIVE_QUARTERS                                     # 3Q26 .. 4Q28 (FY28 for the annual file)
        h_of = lambda q, q0=q0: Q.to_index(q) - Q.to_index(q0)   # noqa: E731
        if verbose:
            print(f"  vintage {vd}  q0={q0}  n_train={st['n']}")
        for obj, (specs, fit, fc) in OBJECTS.items():
            for spec in specs:
                rev_known, nights_known = _known_flags(obj, spec)
                for pb in ("PIT", "full_sample"):
                    params = fit(st, spec) if pb == "PIT" else full_params[(obj, spec)]
                    param_rows.append({"vintage_date": st["vd"], "object": obj, "spec_id": spec, "prior_basis": pb,
                                       "params": _fmt_params(params)})
                    if vd == TODAY and not (rev_known or nights_known):
                        for scen in ("base", "bear", "bull"):
                            inp = Inputs(st, pb, scenario=scen, targets=targets)
                            f = fc(st, qs, params, inp)
                            r = _rows_from(f, obj, spec, pb, st, h_of, {"n_params": params["n_params"]}, scen)
                            live_rows += r
                            if scen == "base":
                                rows += [dict(x, knowable_from=TODAY) for x in r]
                    else:
                        if vd == TODAY:
                            continue                                # known-input specs have no LIVE meaning
                        inp = Inputs(st, pb, rev_known=rev_known, nights_known=nights_known, targets=targets)
                        f = fc(st, qs, params, inp)
                        rows += _rows_from(f, obj, spec, pb, st, h_of, {"n_params": params["n_params"]})
        for spec in SPECS_SENT:
            for pb in ("PIT", "full_sample"):
                params = fit_sentence(st, spec, targets) if pb == "PIT" else full_params[("q_sentence_direction", spec)]
                param_rows.append({"vintage_date": st["vd"], "object": "q_sentence_direction", "spec_id": spec,
                                   "prior_basis": pb, "params": _fmt_params(params)})
                if not np.isfinite(params["k"]):
                    continue
                if vd == TODAY:
                    for scen in ("base", "bear", "bull"):
                        inp = Inputs(st, pb, scenario=scen, targets=targets)
                        f = fc_sentence(st, qs, params, inp, targets)
                        r = _rows_from(f, "q_sentence_direction", spec, pb, st, h_of, {"n_params": 1}, scen)
                        live_rows += r
                        if scen == "base":
                            rows += [dict(x, knowable_from=TODAY) for x in r]
                else:
                    inp = Inputs(st, pb, targets=targets)
                    f = fc_sentence(st, qs, params, inp, targets)
                    rows += _rows_from(f, "q_sentence_direction", spec, pb, st, h_of, {"n_params": 1})
        if include_sarima and st["n"] >= 8:
            for spec in ("margin_aicc", "lines_aicc"):
                for pb in ("PIT", "full_sample"):
                    params = fit_sarima(st, spec) if pb == "PIT" else full_params[("sarima_margin", spec)]
                    param_rows.append({"vintage_date": st["vd"], "object": "sarima_margin", "spec_id": spec,
                                       "prior_basis": pb, "params": _fmt_params(params)})
                    if params["n_params"] == 0:
                        continue
                    try:
                        if vd == TODAY:
                            for scen in ("base", "bear", "bull"):
                                inp = Inputs(st, pb, scenario=scen, targets=targets)
                                f = fc_sarima(st, qs, params, inp, spec)
                                r = _rows_from(f, "sarima_margin", spec, pb, st, h_of, {"n_params": params["n_params"]}, scen)
                                live_rows += r
                                if scen == "base":
                                    rows += [dict(x, knowable_from=TODAY) for x in r]
                        else:
                            inp = Inputs(st, pb, targets=targets)
                            f = fc_sarima(st, qs, params, inp, spec)
                            rows += _rows_from(f, "sarima_margin", spec, pb, st, h_of, {"n_params": params["n_params"]})
                    except Exception as e:  # a failed fit is logged, not hidden
                        log(f"  sarima {spec} {pb} failed at {vd}: {e}")
    g = pd.DataFrame(rows)
    g = _attach_actuals(g, targets)
    g = add_ensemble(g, targets)
    pd.DataFrame(param_rows).to_csv(OUT / f"{SLUG}_params_by_vintage.csv", index=False)
    live = pd.DataFrame(live_rows)
    return g, live


def _fmt_params(p: dict) -> str:
    parts = []
    for k, v in p.items():
        if k == "n_params":
            continue
        if isinstance(v, dict):
            parts.append(k + "{" + ", ".join(f"{a}:{b:.4g}" for a, b in v.items()) + "}")
        elif isinstance(v, tuple):
            parts.append(f"{k}=SARIMA{v[0][0]}x{v[0][1]}{v[0][2]} aicc={v[2]:.1f}")
        elif isinstance(v, float):
            parts.append(f"{k}={v:.4g}")
        else:
            parts.append(f"{k}={v}")
    return "; ".join(parts) + f"; n_params={p.get('n_params')}"


def _attach_actuals(g: pd.DataFrame, targets) -> pd.DataFrame:
    t = targets[targets["has_actual"]]
    tg = sorted(set(g["target"]))
    act = t.melt(id_vars=["quarter", "print_date"], value_vars=[c for c in tg if c in t.columns],
                 var_name="target", value_name="actual").rename(columns={"print_date": "target_print_date"})
    g = g.merge(act, on=["quarter", "target"], how="left")
    g["err"] = g["point"] - g["actual"]
    with np.errstate(divide="ignore", invalid="ignore"):
        g["rel_err"] = g["actual"] / g["point"] - 1.0
    return g


# ----------------------------------------------------------------------------- object 6: ensemble_simple
ENS_MEMBERS = [("yoy_margin_change", "k4_rw"), ("incremental_margin", "k4_rw"), ("pct_rev_seasonal", "drift_k4_rw"),
               ("per_night_seasonal", "g_k4_rw")]
ENS_TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd"]
ENS_ERR_N = 8


def ensemble_weights(pit_err: pd.DataFrame, tgt: str, h: int, vd, pb: str):
    """Inverse-MAE weights over the members from past PIT errors at the same horizon whose target
    quarters printed on/before the vintage (last ENS_ERR_N; full_sample: all). None -> equal weights."""
    maes = {}
    for obj, _ in ENS_MEMBERS:
        e = pit_err[(pit_err["object"] == obj) & (pit_err["target"] == tgt) & (pit_err["horizon_q"] == h)]
        if pb == "PIT":
            e = e[e["target_print_date"] <= vd]
        e = e.sort_values("quarter")
        errs = (e["rel_err"].abs() if tgt in RELATIVE_METRICS else e["err"].abs()).to_numpy()
        if pb == "PIT":
            errs = errs[-ENS_ERR_N:]
        maes[obj] = float(np.mean(errs)) if len(errs) >= 3 else np.nan
    if all(np.isfinite(v) and v > 0 for v in maes.values()):
        w = {o: 1.0 / v for o, v in maes.items()}
        s = sum(w.values())
        return {o: v / s for o, v in w.items()}
    return None


def add_ensemble(g: pd.DataFrame, targets) -> pd.DataFrame:
    mem = g[g["target"].isin(ENS_TARGETS) & g[["object", "spec_id"]].apply(tuple, axis=1).isin(ENS_MEMBERS)]
    rows = []
    key = ["target", "vintage_date", "quarter", "horizon_q", "prior_basis"]
    pit_err = mem[(mem["prior_basis"] == "PIT") & mem["actual"].notna()]
    for (tgt, vd, q, h, pb), grp in mem.groupby(key):
        if len(grp) < len(ENS_MEMBERS):
            continue
        pts = grp.set_index("object")["point"]
        eq = float(pts.mean())
        w = ensemble_weights(pit_err, tgt, h, vd, pb)
        if w is not None:
            inv = float(sum(w[o] * pts[o] for o in w))
            wnote = "w " + ", ".join(f"{o[:6]} {w[o]:.2f}" for o in w)
        else:
            inv, wnote = eq, "equal (fewer than 3 past errors for a member)"
        base = {"target": tgt, "quarter": q, "vintage_date": vd, "horizon_q": h, "prior_basis": pb,
                "n_train": int(grp["n_train"].max()), "knowable_from": grp["knowable_from"].max(),
                "scenario": grp["scenario"].iloc[0], "actual": grp["actual"].iloc[0],
                "target_print_date": grp["target_print_date"].iloc[0]}
        rows.append(dict(base, object="ensemble_simple", spec_id="eq4", point=eq, n_params=0,
                         notes="mean of " + ", ".join(f"{o[:6]} {pts[o]:.2f}" for o in pts.index)))
        rows.append(dict(base, object="ensemble_simple", spec_id="invmae4", point=inv, n_params=4, notes=wnote))
    e = pd.DataFrame(rows)
    e["err"] = e["point"] - e["actual"]
    with np.errstate(divide="ignore", invalid="ignore"):
        e["rel_err"] = e["actual"] / e["point"] - 1.0
    return pd.concat([g, e], ignore_index=True)


# ----------------------------------------------------------------------------- quantiles
def attach_quantiles(g: pd.DataFrame) -> pd.DataFrame:
    """Walk-forward residual pools per (object, spec, target, horizon); PIT = last 12 errors of quarters
    printed on/before the vintage; full_sample = all realised errors. Same convention as the WS10 baselines."""
    g = g.copy()
    for c in QCOLS + ["sd", "sigma_n"]:
        g[c] = np.nan
    g["sigma_kind"] = ""
    pools = {}
    for (obj, spec, tgt, h), grp in g.groupby(["object", "spec_id", "target", "horizon_q"]):
        rel = tgt in RELATIVE_METRICS
        pool = grp[(grp["prior_basis"] == "PIT") & grp["actual"].notna() & grp["target_print_date"].notna()]
        if rel:
            pool = pool[(pool["point"] > 0) & (pool["actual"] > 0)]
        pool = pool.sort_values("quarter")
        errs = (pool["rel_err"] if rel else pool["err"]).to_numpy(dtype=float)
        pools[(obj, spec, tgt, h)] = (errs, pool["target_print_date"].to_numpy())
    for (obj, spec, tgt, h), grp in g.groupby(["object", "spec_id", "target", "horizon_q"]):
        rel = tgt in RELATIVE_METRICS
        errs, pdates = pools[(obj, spec, tgt, h)]
        borrowed = ""
        if len(errs) < MIN_RESID:
            for hb in range(int(h) - 1, -1, -1):
                e2, p2 = pools.get((obj, spec, tgt, hb), (np.array([]), np.array([])))
                if len(e2) >= MIN_RESID:
                    errs, pdates, borrowed = e2, p2, f"_borrowed_h{hb}"
                    break
        full_sd = float(np.std(errs, ddof=1)) if len(errs) >= MIN_RESID else np.nan
        for i in grp.index:
            vd = g.at[i, "vintage_date"]
            pb = g.at[i, "prior_basis"]
            if pb == "full_sample":
                sd, n = full_sd, len(errs)
            else:
                m = np.array([d <= vd for d in pdates], dtype=bool)
                e = errs[m][-RESID_MAX_N:]
                sd = float(np.std(e, ddof=1)) if len(e) >= MIN_RESID else np.nan
                n = int(len(e))
            kind = ("relative" if rel else "additive") + borrowed
            if not np.isfinite(sd) or sd <= 0:
                sd = FALLBACK_SIGMA_REL if rel else FALLBACK_SIGMA_PP
                kind += "_fallback"
            pt = g.at[i, "point"]
            for c in QCOLS:
                g.at[i, c] = pt * (1.0 + ZS[c] * sd) if rel else pt + ZS[c] * sd
            g.at[i, "sd"] = abs(pt) * sd if rel else sd
            g.at[i, "sigma_n"] = n
            g.at[i, "sigma_kind"] = kind
    qm = g[QCOLS].to_numpy(dtype=float)
    qm.sort(axis=1)
    g[QCOLS] = qm
    return g


# ----------------------------------------------------------------------------- registry
def registry_frames(g: pd.DataFrame) -> dict:
    frames = {}
    for obj, grp in g.groupby("object"):
        rows = []
        for r in grp.itertuples():
            if r.quarter > LAST_REGISTERED_Q:
                continue
            for win in windows_for(r.vintage_date, r.quarter):
                row = {"method": METHOD, "object": obj, "target": r.target, "quarter": r.quarter,
                       "vintage_date": r.vintage_date, "horizon_q": int(r.horizon_q), "point": float(r.point),
                       "window": win, "prior_basis": r.prior_basis,
                       "n_params": int(r.n_params) + (0 if str(r.sigma_kind).endswith("fallback") else 1),
                       "n_train": int(r.n_train), "sd": r.sd, "knowable_from": r.knowable_from,
                       "spec_id": r.spec_id, "notes": f"{r.notes}; sigma {r.sigma_kind} n={int(r.sigma_n)} ({r.prior_basis})"}
                for c in QCOLS:
                    row[c] = float(getattr(r, c))
                rows.append(row)
        if rows:
            frames[obj] = pd.DataFrame(rows)
    return frames


# ----------------------------------------------------------------------------- LIVE and annual tables
def live_table(g: pd.DataFrame, live: pd.DataFrame, targets) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Quarterly LIVE forecasts (3Q26-4Q28, base/bear/bull, with the TODAY-vintage quantiles from the
    registered base rows) and FY26-28 annuals."""
    qb = g[(g["vintage_date"] == TODAY) & (g["prior_basis"] == "PIT")]
    qcols = qb.set_index(["object", "spec_id", "target", "quarter"])[QCOLS + ["sd", "sigma_kind"]]
    lv = live[live["prior_basis"] == "PIT"].copy()
    # ensemble rows per scenario, with the TODAY PIT weights (same rule and error pool as add_ensemble)
    memg = g[g["target"].isin(ENS_TARGETS) & g[["object", "spec_id"]].apply(tuple, axis=1).isin(ENS_MEMBERS)]
    pit_err = memg[(memg["prior_basis"] == "PIT") & memg["actual"].notna()]
    ens = []
    mem = lv[lv["target"].isin(ENS_TARGETS) & lv[["object", "spec_id"]].apply(tuple, axis=1).isin(ENS_MEMBERS)]
    for (tgt, scen, q, h), grp in mem.groupby(["target", "scenario", "quarter", "horizon_q"]):
        if len(grp) < len(ENS_MEMBERS):
            continue
        pts = grp.set_index("object")["point"]
        w = ensemble_weights(pit_err, tgt, int(h), _vd(TODAY), "PIT") if pit_err is not None else None
        base = {"target": tgt, "scenario": scen, "quarter": q, "horizon_q": int(h), "prior_basis": "PIT",
                "vintage_date": _vd(TODAY), "n_train": int(grp["n_train"].max()), "knowable_from": TODAY}
        ens.append(dict(base, object="ensemble_simple", spec_id="eq4", point=float(pts.mean()), n_params=0,
                        notes="mean of " + ", ".join(f"{o[:6]} {pts[o]:.2f}" for o in pts.index)))
        inv = float(sum(w[o] * pts[o] for o in w)) if w else float(pts.mean())
        ens.append(dict(base, object="ensemble_simple", spec_id="invmae4", point=inv, n_params=4,
                        notes=("w " + ", ".join(f"{o[:6]} {w[o]:.2f}" for o in w)) if w else "equal"))
    if ens:
        lv = pd.concat([lv, pd.DataFrame(ens)], ignore_index=True)
    lv = lv.merge(qcols, left_on=["object", "spec_id", "target", "quarter"], right_index=True, how="left")
    for c in QCOLS + ["sd"]:
        lv.loc[lv["scenario"] != "base", c] = np.nan            # intervals are built on the base path only
    lv["vintage_date"] = TODAY
    # consensus (WS03 / WS06 LSEG 11-13 Sep) and management comparison columns
    cons = pd.read_csv(WS06 / "06_consensus_quarterly_2027.csv")
    cons["quarter"] = cons["quarter"].map(lambda x: Q.canon(x) if not str(x).startswith("FY") else x)
    cmap_e = cons.set_index("quarter")["ebitda_mean_musd"].to_dict()
    cmap_r = cons.set_index("quarter")["revenue_mean_musd"].to_dict()
    lv["street_ebitda_musd"] = lv["quarter"].map(cmap_e)
    lv["street_revenue_musd"] = lv["quarter"].map(cmap_r)
    lv["street_margin_pct"] = 100.0 * lv["street_ebitda_musd"] / lv["street_revenue_musd"]
    lv["street_vendor"] = "LSEG mean, 06_consensus_quarterly_2027.csv (pull 2026-09-13; obs dates in that file)"
    sn = {}
    t = targets.set_index("quarter")
    for q in LIVE_QUARTERS:
        lag = Q.shift(q, -4)
        sn[q] = float(t.loc[lag, "adj_ebitda_margin_pct"]) if lag in t.index and pd.notna(t.loc[lag, "adj_ebitda_margin_pct"]) else np.nan
    lv["seasonal_naive_margin_pct"] = lv["quarter"].map(sn)
    lv = lv.sort_values(["target", "object", "spec_id", "scenario", "quarter"]).reset_index(drop=True)
    # annuals
    rows = []
    act = targets[targets["has_actual"]].set_index("quarter")
    for (obj, spec, scen), grp in lv[lv["target"].isin(["adj_ebitda_musd"])].groupby(["object", "spec_id", "scenario"]):
        e = grp.set_index("quarter")["point"]
        rv = grp.set_index("quarter")["notes"]  # noqa: F841
        for fy in (2026, 2027, 2028):
            qs = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
            E = R = 0.0
            ok = True
            src = []
            for q in qs:
                if q in act.index:
                    E += float(act.loc[q, "adj_ebitda_musd"]); R += float(act.loc[q, "revenue_musd"]); src.append("actual")
                elif q in e.index:
                    rq = adopted(q, scen, "rev")
                    if not np.isfinite(rq):
                        ok = False; break
                    E += float(e[q]); R += rq; src.append("fc")
                else:
                    ok = False; break
            if not ok:
                continue
            rows.append({"object": obj, "spec_id": spec, "scenario": scen, "period": f"FY{fy}", "adj_ebitda_musd": E,
                         "revenue_musd": R, "adj_ebitda_margin_pct": 100.0 * E / R,
                         "quarters": "+".join(src), "vintage_date": TODAY})
    ann = pd.DataFrame(rows)
    fy_cons = cons[cons["quarter"].astype(str).str.startswith("FY")].copy()
    fy_cons["period"] = fy_cons["quarter"].map(lambda s: "FY20" + s[2:])
    ann = ann.merge(fy_cons[["period", "ebitda_mean_musd", "revenue_mean_musd"]].rename(
        columns={"ebitda_mean_musd": "street_ebitda_musd", "revenue_mean_musd": "street_revenue_musd"}), on="period", how="left")
    ann["street_margin_pct"] = 100.0 * ann["street_ebitda_musd"] / ann["street_revenue_musd"]
    ann["mgmt_fy26_guide"] = np.where(ann["period"] == "FY2026", "at least 35.5% (2Q26 letter, 2026-08-06)", "")
    return lv, ann


# ----------------------------------------------------------------------------- figures
def make_figures(sb: pd.DataFrame, by_q: pd.DataFrame, lv: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    # 1. h=0 margin errors by quarter, main specs vs seasonal naive and street (W1)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    sel = by_q[(by_q["target"] == "adj_ebitda_margin_pct") & (by_q["window"] == "W1") & (by_q["horizon_q"] == 0)
               & (by_q["prior_basis"] == "PIT")]
    series = [("baselines-margin", "seasonal_naive", ""), ("baselines-margin", "street", "")]
    series += [(METHOD, o, s) for o, s in MAIN_SPEC.items()]
    for meth, obj, spec in series:
        x = sel[(sel["method"] == meth) & (sel["object"] == obj)]
        if meth == METHOD:
            x = x[x["spec_id"] == spec]
        else:
            x = x.drop_duplicates("quarter")
        if len(x) == 0:
            continue
        x = x.sort_values("quarter")
        ax.plot(x["quarter"], x["err"], marker="o", lw=1, label=f"{obj}" + (f" ({spec})" if spec else ""))
    ax.axhline(0, color="k", lw=0.6)
    ax.set_ylabel("forecast - actual, pp")
    ax.set_title("Adj EBITDA margin, h=0, W1 (n=14), PIT replay: error by quarter")
    ax.tick_params(axis="x", rotation=60)
    ax.legend(fontsize=7, ncol=3)
    fig.tight_layout()
    fig.savefig(FIG / f"{SLUG}_h0_errors_w1.png", dpi=130)
    plt.close(fig)
    # 2. LIVE margin path 3Q26-4Q27 by object (base), with Street and seasonal naive
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = lv[(lv["target"] == "adj_ebitda_margin_pct") & (lv["scenario"] == "base") & (lv["quarter"] <= LAST_REGISTERED_Q)]
    for obj, spec in MAIN_SPEC.items():
        y = x[(x["object"] == obj) & (x["spec_id"] == spec)].sort_values("quarter")
        if len(y):
            ax.plot(y["quarter"], y["point"], marker="o", lw=1, label=f"{obj} ({spec})")
    y = x.drop_duplicates("quarter").sort_values("quarter")
    ax.plot(y["quarter"], y["street_margin_pct"], "k--", lw=1.2, label="Street (LSEG)")
    ax.plot(y["quarter"], y["seasonal_naive_margin_pct"], "k:", lw=1.2, label="seasonal naive")
    ax.set_ylabel("adj EBITDA margin, %")
    ax.set_title("LIVE (vintage 2026-09-11), base revenue path: margin by object")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / f"{SLUG}_live_margin_path.png", dpi=130)
    plt.close(fig)
