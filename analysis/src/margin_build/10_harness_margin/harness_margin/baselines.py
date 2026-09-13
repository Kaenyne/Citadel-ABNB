"""The margin baselines, registered as method `baselines-margin`, one object each.

Every rule is evaluated AT a vintage date with the point-in-time information set
(`panel.history_as_of`: quarters whose print date is <= the vintage date, same-day letter
included, the frozen-harness convention). Vintages: every guide date in the frozen calendar
(2021-11-04 .. 2026-08-06) plus TODAY = 2026-09-11 (the only non-guide date the frozen validator
accepts; the prompt's 2026-09-12 is therefore stamped 2026-09-11 and the WS03 row used is the
11 Sep LSEG row). Only W1 / W2 / LIVE rows are REGISTERED; the 2021-22 vintages exist so that the
PIT residual pools at the first W1 dates are not empty.

Objects (rule; free parameters excluding the residual sd, which adds 1 when fitted):
  seasonal_naive        y[q-4]                                                     0
  seasonal_naive_drift  y[q-4] + (y[last] - y[last-4])  (additive y/y change)     0
  trailing4             mean of the last 4 observed values (ratio-class metrics)  1
  pct_rev_last4         mean of last 4 (line / revenue) x revenue leg             2  (ratio + cushion)
  guide_implied         FY margin guide in force -> remaining-quarter EBITDA,
                        prorated by seasonal EBITDA shares                       3  (share vector)
  q_guide_implied       the quarterly margin sentence in force, as a level        0
  street                LSEG mean at the vintage date (WS03), pre-guide           0

Revenue leg (used by pct_rev_last4 and guide_implied; exposed as `revenue_forecast_pit`):
  frozen `baselines` guide-cushion (guide_mid x median trailing-8 actual/guide ratio) when the
  quarter has a revenue guide in force at the vintage; else the frozen `naive` rule
  y[q-4] x (1 + last observed y/y growth); else that rule chained from the nearest forecast
  (h >= 4 LIVE quarters). Written to revenue_leg_pit.csv.

Replays: PIT = residual sd (and guide_implied's seasonal shares) from information knowable at
the vintage; full_sample = the same rule with the residual sd (and shares) from the whole realised
sample through 2026Q2. Inputs are PIT in both; only parameter knowledge leaks in full_sample.

Quantiles: Gaussian on the walk-forward residual pool of the SAME object/target/horizon
(last 12 errors printed before the vintage for PIT; all errors for full_sample). Relative errors
(y/pt - 1) for level metrics whose pool is strictly positive (cost lines, revenue, nights, SBC,
D&A, shares, adj EBITDA); additive errors for everything else (ratios, pp, per-night, EPS, and
level metrics that cross zero such as operating income, net income, tax provision).
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd

from . import paths as P
from .frozen import (Q, W, TODAY, QUANTILE_LEVELS, frozen_revenue_guide_cushion,
                     frozen_revenue_naive, frozen_history_as_of)
from .panel import (load_targets, history_as_of, series_as_of, full_series, TARGET_METRICS, UNITS,
                    LINES)
from .guides import fy_guide_in_force, q_guide_in_force
from .street import load_street
from .registry import windows_for

_QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
_Z = dict(zip(_QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817, 0.0,
                       0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))

H_BACKTEST = 2          # h = 0, 1, 2 at W1 / W2 vintages
H_LIVE = 5              # h = 0 .. 5 at the LIVE vintages (3Q26 .. 4Q27)
RESID_MAX_N = 12
MIN_RESID = 3
FALLBACK_SIGMA_REL = 0.10
FALLBACK_SIGMA_PP = 3.0

RATIO_METRICS = [m for m in TARGET_METRICS if UNITS[m][0] in ("%", "pp", "USD/night")]
LEVEL_METRICS = [m for m in TARGET_METRICS if m not in RATIO_METRICS]     # USD m, m, USD/share
COST_LEVEL_METRICS = [f"{ln}_cash_musd" for ln in LINES] + \
    ["ga_cash_ex_reserves_musd", "total_cash_costs_musd", "sbc_musd", "da_musd", "adj_ebitda_musd"]

VINTAGES_ALL = list(W.GUIDE_DATES_ALL) + [TODAY]
VINTAGES_REGISTERED = list(W.GUIDE_DATES_W1) + [W.GUIDE_DATE_LIVE, TODAY]


# ----------------------------------------------------------------------------- helpers
def _vd(vintage_date) -> _dt.date:
    return pd.to_datetime(vintage_date).date()


def _horizon(vintage_date, quarter) -> int:
    return Q.to_index(Q.canon(quarter)) - Q.to_index(Q.quarter_of_date(_vd(vintage_date)))


def _print_date_map(targets=None) -> dict:
    t = load_targets() if targets is None else targets
    return {r.quarter: r.print_date for r in t.itertuples() if pd.notna(r.print_date)}


def _knowable_from(vintage_date, targets=None):
    h = history_as_of(vintage_date, None, targets)
    return h["print_date"].max() if len(h) else None


def _last_yoy_change(s: pd.Series):
    """(last quarter, y[last] - y[last-4]) or (None, nan)."""
    if len(s) == 0:
        return None, np.nan
    last = s.index[-1]
    lag = Q.shift(last, -4)
    if lag not in s.index:
        return last, np.nan
    return last, float(s[last] - s[lag])


def _last_yoy_growth_rev(vintage_date):
    h = frozen_history_as_of(vintage_date, "revenue_musd")
    s = pd.Series(h["revenue_musd"].to_numpy(dtype=float), index=h["quarter"].to_numpy())
    if len(s) == 0:
        return np.nan
    last = s.index[-1]
    lag = Q.shift(last, -4)
    if lag not in s.index or s[lag] == 0:
        return np.nan
    return float(s[last] / s[lag] - 1.0)


# ----------------------------------------------------------------------------- revenue leg
_REV_CACHE = {}


def revenue_forecast_pit(vintage_date, quarter, prior_basis: str = "PIT"):
    """(revenue_musd forecast, leg name) at a vintage. Frozen guide-cushion when the quarter has a
    revenue guide in force, else the frozen naive rule, else naive chained. PIT for both replays
    except the cushion median, which is full-sample under prior_basis='full_sample'."""
    vd = _vd(vintage_date)
    q = Q.canon(quarter)
    key = (vd, q, prior_basis)
    if key in _REV_CACHE:
        return _REV_CACHE[key]
    out = (np.nan, "none")
    try:
        r = frozen_revenue_guide_cushion(vd, q, metric="revenue_musd", prior_basis=prior_basis)
    except Exception:
        r = None
    # the cushion pool requires the guide to be in force at the vintage: guide_date <= vintage
    if r is not None:
        ft = _frozen_targets()
        row = ft[ft["quarter"] == q]
        gd = row["guide_date"].iloc[0] if len(row) else None
        if gd is None or pd.isna(gd) or gd > vd:
            r = None
    if r is not None:
        out = (float(r["point"]), "guide_cushion")
    else:
        r = frozen_revenue_naive(vd, q, metric="revenue_musd", prior_basis="PIT")
        if r is not None and np.isfinite(r["point"]):
            out = (float(r["point"]), "naive")
        else:
            base, leg = revenue_forecast_pit(vd, Q.shift(q, -4), prior_basis)
            g = _last_yoy_growth_rev(vd)
            if np.isfinite(base) and np.isfinite(g):
                out = (base * (1.0 + g), "naive_chained")
    _REV_CACHE[key] = out
    return out


_FT = {}


def _frozen_targets():
    if "t" not in _FT:
        from .frozen import load_frozen_targets
        _FT["t"] = load_frozen_targets()
    return _FT["t"]


def build_revenue_leg(write: bool = True) -> pd.DataFrame:
    rows = []
    for vd in VINTAGES_ALL:
        hmax = H_LIVE if vd in (W.GUIDE_DATE_LIVE, TODAY) else H_BACKTEST
        q0 = Q.quarter_of_date(vd)
        for h in range(hmax + 1):
            q = Q.shift(q0, h)
            for pb in ("PIT", "full_sample"):
                v, leg = revenue_forecast_pit(vd, q, pb)
                rows.append({"vintage_date": vd, "quarter": q, "horizon_q": h, "prior_basis": pb,
                             "revenue_musd_forecast": v, "leg": leg})
    out = pd.DataFrame(rows)
    if write:
        P.ensure_dirs()
        out.to_csv(P.OUT_REVENUE_LEG, index=False)
    return out


# ----------------------------------------------------------------------------- seasonal shares
def seasonal_ebitda_shares(vintage_date=None, prior_basis: str = "PIT", targets=None):
    """Average share of FY adjusted EBITDA by fiscal quarter. PIT: the last 3 complete fiscal years
    (FY2021 or later) knowable at the vintage, minimum 2; full_sample: FY2023-25 fixed.
    Returns (dict qn -> share, label) or (None, reason)."""
    t = load_targets() if targets is None else targets
    if prior_basis == "full_sample" or vintage_date is None:
        years = [2023, 2024, 2025]
        pool = t[t["has_actual"]]
    else:
        h = history_as_of(vintage_date, None, t)
        pool = h
        complete = []
        for y in sorted({int(q[:4]) for q in h["quarter"]}):
            if y >= 2021 and all(f"{y}Q{n}" in set(h["quarter"]) for n in (1, 2, 3, 4)):
                complete.append(y)
        years = complete[-3:]
        if len(years) < 2:
            return None, f"fewer than 2 complete fiscal years knowable at {vintage_date}"
    shares = {1: [], 2: [], 3: [], 4: []}
    for y in years:
        sub = pool[pool["quarter"].str.startswith(str(y))].set_index("quarter")["adj_ebitda_musd"]
        tot = float(sub.sum())
        if tot <= 0 or len(sub) < 4:
            continue
        for n in (1, 2, 3, 4):
            shares[n].append(float(sub[f"{y}Q{n}"]) / tot)
    if any(len(v) == 0 for v in shares.values()):
        return None, "no usable fiscal year"
    s = {n: float(np.mean(v)) for n, v in shares.items()}
    tot = sum(s.values())
    s = {n: v / tot for n, v in s.items()}
    return s, f"FY{years[0]}-{str(years[-1])[2:]}"


def build_seasonal_shares(write: bool = True) -> pd.DataFrame:
    rows = []
    for vd in VINTAGES_REGISTERED:
        s, lab = seasonal_ebitda_shares(vd, "PIT")
        rows.append({"vintage_date": vd, "prior_basis": "PIT", "years": lab,
                     **({f"share_q{n}": s[n] for n in (1, 2, 3, 4)} if s else {})})
    s, lab = seasonal_ebitda_shares(None, "full_sample")
    rows.append({"vintage_date": None, "prior_basis": "full_sample", "years": lab,
                 **{f"share_q{n}": s[n] for n in (1, 2, 3, 4)}})
    out = pd.DataFrame(rows)
    if write:
        out.to_csv(P.OUT_SEASONAL_SHARES, index=False)
    return out


# ----------------------------------------------------------------------------- point rules
def rule_seasonal_naive(vintage_date, quarter, metric, targets=None):
    s = series_as_of(vintage_date, metric, targets)
    lag = Q.shift(Q.canon(quarter), -4)
    if lag not in s.index:
        return np.nan, f"no {lag} in information set", len(s)
    return float(s[lag]), f"y[{lag}]", len(s)


def rule_seasonal_naive_drift(vintage_date, quarter, metric, targets=None):
    s = series_as_of(vintage_date, metric, targets)
    lag = Q.shift(Q.canon(quarter), -4)
    if lag not in s.index:
        return np.nan, f"no {lag} in information set", len(s)
    last, d = _last_yoy_change(s)
    if not np.isfinite(d):
        return np.nan, "no y/y change observable", len(s)
    return float(s[lag] + d), f"y[{lag}] + (y[{last}] - y[{Q.shift(last, -4)}] = {d:+.3f})", len(s)


def rule_trailing4(vintage_date, quarter, metric, targets=None):
    s = series_as_of(vintage_date, metric, targets)
    if len(s) < 4:
        return np.nan, "fewer than 4 observations", len(s)
    return float(s.iloc[-4:].mean()), f"mean({', '.join(s.index[-4:])})", len(s)


def rule_pct_rev_last4(vintage_date, quarter, metric, prior_basis="PIT", targets=None):
    """mean of last-4 (metric / revenue) x revenue leg. metric is a $ level."""
    t = load_targets() if targets is None else targets
    h = history_as_of(vintage_date, None, t)
    h = h.dropna(subset=[metric, "revenue_musd"])
    if len(h) < 4:
        return np.nan, "fewer than 4 observations", len(h), np.nan, "none"
    ratio = float((h[metric].iloc[-4:] / h["revenue_musd"].iloc[-4:]).mean())
    rev, leg = revenue_forecast_pit(vintage_date, quarter, prior_basis)
    if not np.isfinite(rev):
        return np.nan, "no revenue leg", len(h), np.nan, leg
    return ratio * rev, f"ratio4={100*ratio:.2f}% x rev[{leg}]={rev:.0f}", len(h), rev, leg


def rule_guide_implied(vintage_date, quarter, prior_basis="PIT", targets=None):
    """Returns dict(quarter -> (ebitda_musd, margin_pct, rev_hat, note)) for the remaining quarters
    of the fiscal year of `quarter`, or (None, reason)."""
    t = load_targets() if targets is None else targets
    vd = _vd(vintage_date)
    q = Q.canon(quarter)
    fy = int(q[:4])
    g = fy_guide_in_force(vd, fy, t)
    if g is None:
        return None, f"no FY{fy} margin guide in force at {vd}"
    h = history_as_of(vd, None, t)
    fyq = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
    ytd = h[h["quarter"].isin(fyq)]
    ytd_rev = float(ytd["revenue_musd"].sum())
    ytd_ebitda = float(ytd["adj_ebitda_musd"].sum())
    remaining = [x for x in fyq if x not in set(ytd["quarter"])]
    if q not in remaining:
        return None, f"{q} already printed at {vd}"
    shares, lab = seasonal_ebitda_shares(vd if prior_basis == "PIT" else None, prior_basis, t)
    if shares is None:
        return None, lab
    rev_hat = {}
    for r in remaining:
        v, leg = revenue_forecast_pit(vd, r, prior_basis)
        if not np.isfinite(v):
            return None, f"no revenue leg for {r}"
        rev_hat[r] = (v, leg)
    fy_rev = ytd_rev + sum(v for v, _ in rev_hat.values())
    rem_ebitda = g["level_pct"] / 100.0 * fy_rev - ytd_ebitda
    ssum = sum(shares[int(r[5])] for r in remaining)
    out = {}
    for r in remaining:
        e = rem_ebitda * shares[int(r[5])] / ssum
        m = 100.0 * e / rev_hat[r][0]
        out[r] = (e, m, rev_hat[r][0],
                  f"FY{fy} guide {g['guide_type']} {g['level_pct']:.2f}% ({g['form']}, {g['guide_date']}); "
                  f"YTD rev {ytd_rev:.0f} EBITDA {ytd_ebitda:.0f}; FY rev hat {fy_rev:.0f}; "
                  f"shares {lab}; rev[{rev_hat[r][1]}]={rev_hat[r][0]:.0f}")
    return out, "ok"


def rule_q_guide_implied(vintage_date, quarter, prior_basis="PIT", targets=None):
    """(margin_pct, ebitda_musd, note) from the quarterly margin sentence in force, or None."""
    t = load_targets() if targets is None else targets
    g = q_guide_in_force(vintage_date, quarter, t)
    if g is None:
        return None
    rev, leg = revenue_forecast_pit(vintage_date, quarter, prior_basis)
    m = g["level_pct"]
    e = np.nan
    if m is not None and np.isfinite(rev):
        e = m / 100.0 * rev
    if g["ebitda_floor_musd"] is not None:
        e = float(g["ebitda_floor_musd"]) if not np.isfinite(e) else e
        if m is None and np.isfinite(rev):
            m = 100.0 * e / rev
    return (m, e, f"{g['guide_type']} {g['form']} ({g['guide_id']}); rev[{leg}]={rev:.0f}")


# ----------------------------------------------------------------------------- grid
def _grid_rows_simple(obj, fn, metrics, targets):
    rows = []
    for vd in VINTAGES_ALL:
        hmax = H_LIVE if vd in (W.GUIDE_DATE_LIVE, TODAY) else H_BACKTEST
        q0 = Q.quarter_of_date(vd)
        kf = _knowable_from(vd, targets)
        for h in range(hmax + 1):
            q = Q.shift(q0, h)
            for m in metrics:
                pt, note, n_train = fn(vd, q, m, targets)
                if not np.isfinite(pt):
                    continue
                rows.append({"object": obj, "target": m, "quarter": q, "vintage_date": vd,
                             "horizon_q": h, "point": pt, "n_train": n_train, "notes": note,
                             "knowable_from": kf, "prior_basis": "both"})
    return rows


def _grid_rows_pct_rev(targets):
    rows = []
    for vd in VINTAGES_ALL:
        hmax = H_LIVE if vd in (W.GUIDE_DATE_LIVE, TODAY) else H_BACKTEST
        q0 = Q.quarter_of_date(vd)
        kf = _knowable_from(vd, targets)
        for h in range(hmax + 1):
            q = Q.shift(q0, h)
            for m in COST_LEVEL_METRICS:
                for pb in ("PIT", "full_sample"):
                    pt, note, n_train, rev, leg = rule_pct_rev_last4(vd, q, m, pb, targets)
                    if not np.isfinite(pt):
                        continue
                    rows.append({"object": "pct_rev_last4", "target": m, "quarter": q,
                                 "vintage_date": vd, "horizon_q": h, "point": pt, "n_train": n_train,
                                 "notes": note, "knowable_from": kf, "prior_basis": pb})
    return rows


def _grid_rows_guide_implied(targets):
    rows = []
    for vd in VINTAGES_ALL:
        hmax = H_LIVE if vd in (W.GUIDE_DATE_LIVE, TODAY) else H_BACKTEST
        q0 = Q.quarter_of_date(vd)
        kf = _knowable_from(vd, targets)
        n_train = len(history_as_of(vd, "adj_ebitda_margin_pct", targets))
        for pb in ("PIT", "full_sample"):
            done = set()
            for h in range(hmax + 1):
                q = Q.shift(q0, h)
                if q in done:
                    continue
                res, why = rule_guide_implied(vd, q, pb, targets)
                if res is None:
                    continue
                for r, (e, m, rev, note) in res.items():
                    hh = _horizon(vd, r)
                    if hh > hmax or hh < 0:
                        continue
                    done.add(r)
                    rows.append({"object": "guide_implied", "target": "adj_ebitda_margin_pct",
                                 "quarter": r, "vintage_date": vd, "horizon_q": hh, "point": m,
                                 "n_train": n_train, "notes": note, "knowable_from": kf,
                                 "prior_basis": pb})
                    rows.append({"object": "guide_implied", "target": "adj_ebitda_musd",
                                 "quarter": r, "vintage_date": vd, "horizon_q": hh, "point": e,
                                 "n_train": n_train, "notes": note, "knowable_from": kf,
                                 "prior_basis": pb})
    return rows


def _grid_rows_q_guide(targets):
    rows = []
    for vd in VINTAGES_ALL:
        hmax = H_LIVE if vd in (W.GUIDE_DATE_LIVE, TODAY) else H_BACKTEST
        q0 = Q.quarter_of_date(vd)
        kf = _knowable_from(vd, targets)
        n_train = len(history_as_of(vd, "adj_ebitda_margin_pct", targets))
        for h in range(hmax + 1):
            q = Q.shift(q0, h)
            for pb in ("PIT", "full_sample"):
                r = rule_q_guide_implied(vd, q, pb, targets)
                if r is None:
                    continue
                m, e, note = r
                if m is not None and np.isfinite(m):
                    rows.append({"object": "q_guide_implied", "target": "adj_ebitda_margin_pct",
                                 "quarter": q, "vintage_date": vd, "horizon_q": h, "point": float(m),
                                 "n_train": n_train, "notes": note, "knowable_from": kf,
                                 "prior_basis": pb})
                if e is not None and np.isfinite(e):
                    rows.append({"object": "q_guide_implied", "target": "adj_ebitda_musd",
                                 "quarter": q, "vintage_date": vd, "horizon_q": h, "point": float(e),
                                 "n_train": n_train, "notes": note, "knowable_from": kf,
                                 "prior_basis": pb})
    return rows


def _grid_rows_street(targets):
    s = load_street()
    rows = []
    if len(s) == 0:
        return rows
    for r in s.itertuples():
        vd = r.vintage_date
        if vd not in VINTAGES_ALL:
            continue
        if r.target not in TARGET_METRICS:
            continue
        h = _horizon(vd, r.quarter)
        n_train = len(history_as_of(vd, r.target, targets))
        rows.append({"object": "street", "target": r.target, "quarter": r.quarter, "vintage_date": vd,
                     "horizon_q": h, "point": float(r.value), "n_train": n_train,
                     "notes": f"LSEG {r.lseg_field} role={r.role} n_est={r.n_est} obs={r.obs_date}",
                     "knowable_from": r.as_of, "street_vendor": "LSEG", "street_as_of": r.as_of,
                     "prior_basis": "both"})
    return rows


N_PARAMS_RULE = {"seasonal_naive": 0, "seasonal_naive_drift": 0, "trailing4": 1, "pct_rev_last4": 2,
                 "guide_implied": 3, "q_guide_implied": 0, "street": 0}


def build_grid(targets=None) -> pd.DataFrame:
    """Every baseline point at every vintage (2021-11-04 .. TODAY) and horizon, before quantiles."""
    t = load_targets() if targets is None else targets
    rows = []
    rows += _grid_rows_simple("seasonal_naive", rule_seasonal_naive, TARGET_METRICS, t)
    rows += _grid_rows_simple("seasonal_naive_drift", rule_seasonal_naive_drift, TARGET_METRICS, t)
    rows += _grid_rows_simple("trailing4", rule_trailing4, RATIO_METRICS, t)
    rows += _grid_rows_pct_rev(t)
    rows += _grid_rows_guide_implied(t)
    rows += _grid_rows_q_guide(t)
    rows += _grid_rows_street(t)
    g = pd.DataFrame(rows)
    # expand "both" into the two replays (identical points; they differ in sigma only)
    both = g[g["prior_basis"] == "both"]
    rest = g[g["prior_basis"] != "both"]
    g = pd.concat([rest, both.assign(prior_basis="PIT"), both.assign(prior_basis="full_sample")],
                  ignore_index=True)
    act = t[t["has_actual"]].melt(id_vars=["quarter"], value_vars=TARGET_METRICS,
                                  var_name="target", value_name="actual")
    g = g.merge(act, on=["quarter", "target"], how="left")
    pdm = _print_date_map(t)
    g["target_print_date"] = g["quarter"].map(pdm)
    g["err"] = g["point"] - g["actual"]
    with np.errstate(divide="ignore", invalid="ignore"):
        g["rel_err"] = g["actual"] / g["point"] - 1.0
    return g.sort_values(["object", "target", "horizon_q", "vintage_date", "quarter"]).reset_index(drop=True)


# ----------------------------------------------------------------------------- quantiles
def _attach_quantiles(g: pd.DataFrame) -> pd.DataFrame:
    """Walk-forward residual sd per (object, target, horizon): PIT uses errors of quarters printed
    before the vintage (last 12); full_sample uses every realised error."""
    g = g.copy()
    for c in _QCOLS + ["sd", "sigma_n", "sigma_kind"]:
        g[c] = np.nan
    g["sigma_kind"] = ""
    for (obj, tgt, h), grp in g.groupby(["object", "target", "horizon_q"]):
        # the realised pool (PIT replay rows carry the same points as full_sample for most objects;
        # use the PIT rows as the error pool so that pct_rev/guide_implied pools are PIT too)
        pool = grp[(grp["prior_basis"] == "PIT") & grp["actual"].notna() & grp["target_print_date"].notna()]
        relative = (tgt in LEVEL_METRICS and len(pool) > 0
                    and (pool["point"] > 0).all() and (pool["actual"] > 0).all())
        errs = (pool["rel_err"] if relative else pool["err"]).to_numpy(dtype=float)
        pdates = pool["target_print_date"].to_numpy()
        pq = pool["quarter"].to_numpy()
        order = np.argsort(pq)
        errs, pdates, pq = errs[order], pdates[order], pq[order]
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
            kind = "relative" if relative else "additive"
            if not np.isfinite(sd) or sd <= 0:
                sd = FALLBACK_SIGMA_REL if relative else FALLBACK_SIGMA_PP
                kind += "_fallback"
            pt = g.at[i, "point"]
            for c in _QCOLS:
                g.at[i, c] = pt * (1.0 + _Z[c] * sd) if relative else pt + _Z[c] * sd
            g.at[i, "sd"] = abs(pt) * sd if relative else sd
            g.at[i, "sigma_n"] = n
            g.at[i, "sigma_kind"] = kind
    # relative quantiles on a negative point would invert the ladder; enforce monotone
    qm = g[_QCOLS].to_numpy(dtype=float)
    qm.sort(axis=1)
    g[_QCOLS] = qm
    return g


# ----------------------------------------------------------------------------- registry frames
def build_all_baselines(targets=None, verbose: bool = True):
    """Returns (frames by object, grid). Frames are FORMAT 1.0 registry frames."""
    t = load_targets() if targets is None else targets
    g = _attach_quantiles(build_grid(t))
    frames = {}
    for obj, grp in g.groupby("object"):
        rows = []
        for r in grp.itertuples():
            for win in windows_for(r.vintage_date, r.quarter):
                row = {"method": P.BASELINE_METHOD, "object": obj, "target": r.target,
                       "quarter": r.quarter, "vintage_date": r.vintage_date, "horizon_q": int(r.horizon_q),
                       "point": float(r.point), "window": win, "prior_basis": r.prior_basis,
                       "n_params": N_PARAMS_RULE[obj] + (0 if r.sigma_kind.endswith("fallback") else 1),
                       "n_train": int(r.n_train), "sd": r.sd, "knowable_from": r.knowable_from,
                       "spec_id": f"{obj}|{r.target}|h{int(r.horizon_q)}|{r.prior_basis}",
                       "notes": f"{r.notes}; sigma {r.sigma_kind} n={int(r.sigma_n)} ({r.prior_basis})"}
                for c in _QCOLS:
                    row[c] = float(getattr(r, c))
                if obj == "street":
                    row["street_vendor"] = r.street_vendor
                    row["street_as_of"] = r.street_as_of
                rows.append(row)
        if rows:
            frames[obj] = pd.DataFrame(rows)
            if verbose:
                f = frames[obj]
                print(f"  baseline {obj:22s}: {len(f):5d} rows, {f['target'].nunique():2d} target(s), "
                      f"windows {sorted(f['window'].unique())}")
    return frames, g
