"""M4: alt-data-augmented line model. Does any external signal add to M1's driver-line model?

Rebuilds the whole package: one-signal augmentations of M1's `b_elastic_rw` line model (strict knowable_from),
placebos (future shift, lead 0, random series), ridge "all candidates" spec, registration through the margin
harness (method `alt-augmented`, objects `lines_aug` and `margin_aug`), LIVE forecasts, annual CSV, figures, scoreboard.

    cd "C:\\Users\\krish\\citadel-abnb-margins"
    py -3.13 analysis/src/margin_build/M4_alt_augmented/run.py

Model (see docs/margin-build/notes/M4_alt_augmented.md section 0 for the pre-registration):
    d4 log L_q = g_L + b_L * d4 log D_q + c * x_{q-lead} + e_q      for ONE line L, signal x from WS04 (+ trends_qtd4 built here)
The other four lines and the drivers are M1's (imported, not copied). A signal term enters only when knowable at the vintage;
otherwise the quarter reverts to M1's forecast and is flagged.
"""
from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HARNESS = REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"
sys.path.insert(0, str(HARNESS))

from harness_margin import (  # noqa: E402
    load_targets, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATE_LIVE, TODAY, windows_for, register, Q, recency_weights,
)

warnings.filterwarnings("ignore", category=FutureWarning)


def _load_m1():
    spec = importlib.util.spec_from_file_location("m1_driver_lines", REPO / "analysis/src/margin_build/M1_driver_lines/run.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


m1 = _load_m1()

METHOD = "alt-augmented"
MB = REPO / "data" / "processed" / "margin_build"
OUT = MB / "M4_alt_augmented"
FIG = REPO / "analysis" / "figures" / "margin_build"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
WS04 = MB / "04_alt_signals"
TRENDS_WEEKLY = REPO / "data" / "processed" / "overnight" / "08_trends_weekly.csv"
M1_LIVE = MB / "M1_driver_lines" / "M1_driver_lines_live_quarterly.csv"
M1_ANNUAL = MB / "M1_driver_lines" / "M1_driver_lines_annual_forecasts.csv"

LINES = m1.LINES
LINE_TARGET = m1.LINE_TARGET
DRIVER = m1.DRIVER
MARGIN_TARGETS = m1.MARGIN_TARGETS
MIN_FIT = m1.MIN_OBS + 1          # one-signal fit needs at least 5 observations with the signal present
ANCHOR_FULL = "2026Q2"
FIRST_VINTAGE = _dt.date(2022, 2, 15)
IV_PASS = 0.9
N_RANDOM = 200
SEED = 20260914
BASE_SPEC = {"rw": "b_elastic_rw", "eq": "b_elastic_eq"}
N_PARAMS = {"none": 10, "best1": 15, "ridge_all": 37, "surv": 11}
DEFAULT_LEAD = {"dlog": 1, "yoy_pct": 1, "dstep": 0, "qtd": 0}
LEADS = {"dlog": [1, 2], "yoy_pct": [1, 2], "dstep": [0, 1], "qtd": [0]}
PLACEBO_LEADS = {"dlog": [0, -4], "yoy_pct": [0, -4], "dstep": [-4], "qtd": [-4]}
FAR_PAST = _dt.date(1900, 1, 1)

# (line, signal, expected sign of c, transform)
SIGNALS = [
    ("cor", "funds_held_musd", "+", "dlog"), ("cor", "fx_usd_per_eur", "-", "dlog"), ("cor", "fx_broad_dollar", "+", "dlog"),
    ("cor", "ppi_data_hosting", "+", "dlog"), ("cor", "event_E02_cor_cash", "+", "dstep"),
    ("ops", "event_E05_ops_cash", "-", "dstep"), ("ops", "appstore_new_ratings_per_day", "+", "dlog"),
    ("ops", "playstore_ratings_new_per_day", "+", "dlog"), ("ops", "emp_business_support_services", "+", "dlog"),
    ("ops", "ppi_insurance_brokerage", "+", "dlog"),
    ("pd", "careers_open_roles", "+", "dlog"), ("pd", "emp_software_publishers", "+", "dlog"),
    ("pd", "emp_computer_systems_design", "+", "dlog"), ("pd", "ahe_information", "+", "dlog"),
    ("pd", "eci_wages_private", "+", "dlog"), ("pd", "event_E10_pd_cash", "-", "dstep"),
    ("sm", "trends_airbnb_share_us", "-", "dlog"), ("sm", "trends_airbnb_share_ww", "-", "dlog"),
    ("sm", "trends_airbnb_us", "either", "dlog"), ("sm", "peer_bkng_advertising_yoy", "+", "yoy_pct"),
    ("sm", "peer_expe_sga_yoy", "+", "yoy_pct"), ("sm", "trends_qtd4_share_us", "-", "qtd"), ("sm", "trends_qtd4_share_ww", "-", "qtd"),
    ("ga", "careers_open_roles", "+", "dlog"), ("ga", "cpi_sf_bay", "+", "dlog"), ("ga", "emp_computer_systems_design", "+", "dlog"),
]
ALL_Q = [f"{y}Q{i}" for y in range(2019, 2029) for i in range(1, 5)]


# ----------------------------------------------------------------------------- signals
def _read_ws04():
    p = pd.read_csv(WS04 / "04_signal_panel_quarterly.csv")
    p["quarter"] = p["quarter"].map(Q.canon)
    p = p.set_index("quarter").reindex(ALL_Q)
    k = pd.read_csv(WS04 / "04_signal_knowable_from.csv")
    k["quarter"] = k["quarter"].map(Q.canon)
    k = k.set_index("quarter").reindex(ALL_Q)
    for c in k.columns:
        k[c] = pd.to_datetime(k[c], errors="coerce").dt.date
    return p, k


PANEL_SIG, KNOW_SIG = _read_ws04()


def build_qtd(geo: str):
    """Airbnb share of category search over the weeks starting in the first 21 days of the quarter (3-4 weeks),
    knowable_from = last included week start + 8 days (the week is complete after 7 days)."""
    w = pd.read_csv(TRENDS_WEEKLY, parse_dates=["date"])
    w = w[(w["payload"] == "P1_peers") & (w["geo"] == geo)]
    g = w.pivot_table(index="date", columns="term", values="value_stitched", aggfunc="mean").sort_index()
    share = 100.0 * g["airbnb"] / (g["airbnb"] + g["booking.com"] + g["expedia"] + g["vrbo"])
    df = share.rename("share").reset_index()
    df["quarter"] = df["date"].map(lambda d: f"{d.year}Q{(d.month - 1) // 3 + 1}")
    df["qstart"] = df["quarter"].map(lambda q: pd.Timestamp(int(q[:4]), 3 * (int(q[-1]) - 1) + 1, 1))
    df = df[(df["date"] - df["qstart"]).dt.days <= 21]
    agg = df.groupby("quarter").agg(share=("share", "mean"), n=("share", "size"), last=("date", "max"))
    agg = agg[agg["n"] >= 3]
    lvl = agg["share"].reindex(ALL_Q)
    know = pd.Series([(d + pd.Timedelta(days=8)).date() if pd.notna(d) else pd.NaT for d in agg["last"].reindex(ALL_Q)], index=ALL_Q)
    return lvl, know, agg


QTD = {}
for _geo in ("US", "WW"):
    _lvl, _know, _agg = build_qtd(_geo)
    QTD[f"trends_qtd4_share_{_geo.lower()}"] = (_lvl, _know)
    PANEL_SIG[f"trends_qtd4_share_{_geo.lower()}"] = _lvl
    KNOW_SIG[f"trends_qtd4_share_{_geo.lower()}"] = _know
    _agg.to_csv(OUT / f"M4_alt_augmented_trends_qtd_{_geo.lower()}.csv")

_SIG_CACHE = {}


def signal_change(sig: str, transform: str):
    """(x, k): the signal's change series and its knowable_from date, both indexed by quarter (ALL_Q)."""
    if sig in _SIG_CACHE:
        return _SIG_CACHE[sig]
    s = pd.to_numeric(PANEL_SIG[sig], errors="coerce")
    k = KNOW_SIG[sig]
    x = pd.Series(np.nan, index=ALL_Q, dtype=float)
    kk = pd.Series([pd.NaT] * len(ALL_Q), index=ALL_Q, dtype=object)
    if transform == "dstep":
        s = s.ffill().fillna(0.0)
        ev = min([d for d in k if pd.notna(d)] or [FAR_PAST])
        for q in ALL_Q:
            lag = Q.shift(q, -4)
            if lag not in s.index:
                continue
            x[q] = float(s[q] - s[lag])
            kk[q] = ev if (s[q] != 0 or s[lag] != 0) else FAR_PAST
    elif transform == "yoy_pct":
        for q in ALL_Q:
            if pd.notna(s[q]):
                x[q] = float(s[q]) / 100.0
                kk[q] = k[q]
    else:  # dlog and qtd
        for q in ALL_Q:
            lag = Q.shift(q, -4)
            if lag in s.index and pd.notna(s[q]) and pd.notna(s[lag]) and s[q] > 0 and s[lag] > 0:
                x[q] = float(np.log(s[q] / s[lag]))
                d1, d0 = k[q], k[lag]
                kk[q] = max([d for d in (d1, d0) if pd.notna(d)] or [pd.NaT])
    _SIG_CACHE[sig] = (x, kk)
    return x, kk


def shifted(x: pd.Series, k: pd.Series, lead: int):
    """xs[q] = x[q - lead] (lead -4 = the +4-quarter future-shift placebo)."""
    xs = pd.Series(np.nan, index=ALL_Q, dtype=float)
    ks = pd.Series([pd.NaT] * len(ALL_Q), index=ALL_Q, dtype=object)
    for q in ALL_Q:
        src = Q.shift(q, -lead)
        if src in x.index:
            xs[q] = x[src]
            ks[q] = k[src]
    return xs, ks


def known(kdate, vd) -> bool:
    return pd.notna(kdate) and kdate <= vd


# ----------------------------------------------------------------------------- base (M1) cache
VINTAGES = [d for d in GUIDE_DATES_ALL if d >= FIRST_VINTAGE]
LIVE_VINTAGES = [GUIDE_DATE_LIVE, TODAY]
_HIST = {}


def hist(vd):
    if vd not in _HIST:
        _HIST[vd] = m1.hist_as_of(vd)
    return _HIST[vd]


FULL_H = hist(TODAY)
FULL_PARAMS = {w: m1.fit_all(FULL_H, BASE_SPEC[w], anchor=ANCHOR_FULL) for w in ("rw", "eq")}
_BASE = {}
_BASE_PARAMS = {}


def base_rows(vd, weighting, replay, live=False, scenario="base", h_max=None):
    """M1 forecasts (list of dicts, horizon order) and M1 params at one vintage."""
    key = (vd, weighting, replay, live, scenario, h_max)
    if key not in _BASE:
        rows, params = m1.run_vintage(vd, BASE_SPEC[weighting], replay, FULL_PARAMS[weighting], live=live,
                                      scenario=scenario, h_max=h_max)
        _BASE[key] = rows
        _BASE_PARAMS[(vd, weighting, replay)] = params
    return _BASE[key], _BASE_PARAMS[(vd, weighting, replay)]


# ----------------------------------------------------------------------------- augmented fit
def fit_aug(h: pd.DataFrame, line: str, sigs: list, vd, weighting: str, anchor=None, ridge: bool = False) -> dict:
    """WLS of d4 log L on [1, d4 log D, x_1..x_k]. `sigs` = [(name, xs, ks)] already lead-shifted.
    One-signal: rows without a knowable signal are dropped; ridge: missing -> 0 in standardised units, penalty n_obs."""
    d = m1.design_rows(h, line, "b", m1.FIRST_YOY_MAIN, "revenue")
    flags = []
    if len(d) < m1.MIN_OBS:
        d = m1.design_rows(h, line, "b", m1.FIRST_YOY_2020, "revenue")
        flags.append("added_2021_obs")
    d = d.copy()
    names = [s[0] for s in sigs]
    for name, xs, ks in sigs:
        v = d["quarter"].map(xs).astype(float)
        ok = d["quarter"].map(lambda q: known(ks[q], vd))
        d[name] = np.where(ok, v, np.nan)
    out = {"line": line, "n_obs": 0, "g": np.nan, "b": np.nan, "c": {}, "c_se": {}, "t": {}, "mu": {}, "sd": {},
           "flags": "", "fitted": False}
    if not ridge:
        d = d[d[names].notna().all(axis=1)]
        if len(d) < MIN_FIT:
            out["flags"] = ";".join(flags + ["insufficient_n_revert_m1"])
            return out
    else:
        for name in names:
            if d[name].notna().sum() < MIN_FIT:
                flags.append(f"{name}_dropped_n")
        names = [n for n in names if d[n].notna().sum() >= MIN_FIT]
        if not names:
            out["flags"] = ";".join(flags + ["no_signal_revert_m1"])
            return out
    T = anchor or h.index.max()
    w = recency_weights(list(d["quarter"]), T) if weighting == "rw" else np.ones(len(d)) / len(d)
    y = d["y"].to_numpy(dtype=float)
    cols, X = ["const"], [np.ones(len(d))]
    drv = DRIVER[line] if line != "sm" else "revenue"
    if drv is not None and line in ("cor", "ops", "sm"):
        cols.append("dlogD"); X.append(d["dlogD"].to_numpy(dtype=float))
    mu, sd = {}, {}
    for name in names:
        v = d[name].to_numpy(dtype=float)
        if ridge:
            m = np.isfinite(v)
            mu[name] = float(np.sum(w[m] * v[m]) / np.sum(w[m]))
            sd[name] = float(np.sqrt(np.sum(w[m] * (v[m] - mu[name]) ** 2) / np.sum(w[m])))
            if not np.isfinite(sd[name]) or sd[name] <= 0:
                sd[name] = 1.0
            v = np.where(m, (v - mu[name]) / sd[name], 0.0)
        cols.append(name); X.append(v)
    X = np.column_stack(X)
    n, p = X.shape
    if n < p + 1:
        out["flags"] = ";".join(flags + ["too_few_obs_revert_m1"])
        return out
    sw = np.sqrt(w)
    Xw, yw = X * sw[:, None], y * sw
    if ridge:
        lam = np.zeros(p)
        lam[len(cols) - len(names):] = float(n)
        A = Xw.T @ Xw + np.diag(lam)
        beta = np.linalg.solve(A, Xw.T @ yw)
        cov = np.linalg.inv(A)
    else:
        beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
        A = Xw.T @ Xw
        cov = np.linalg.pinv(A)
    resid = yw - Xw @ beta
    dof = max(n - p, 1)
    s2 = float(resid @ resid) / dof * n   # weights are normalised to sum 1; rescale to per-obs variance
    se = np.sqrt(np.maximum(np.diag(cov) * s2 / n, 0.0))
    for c, bv, sv in zip(cols, beta, se):
        if c == "const":
            out["g"] = float(bv)
        elif c == "dlogD":
            out["b"] = float(bv)
        else:
            out["c"][c] = float(bv); out["c_se"][c] = float(sv)
            out["t"][c] = float(bv / sv) if sv > 0 else np.nan
    out.update({"n_obs": int(n), "mu": mu, "sd": sd, "flags": ";".join(flags), "fitted": True, "ridge": ridge})
    return out


# ----------------------------------------------------------------------------- augmented forecast
def forecast_aug(vd, line: str, sigs: list, p: dict, brows: list, h: pd.DataFrame, spec_id: str) -> list:
    """Re-forecast one line on top of M1's rows `brows` (same drivers, same other lines)."""
    bq = {r["quarter"]: r for r in brows}
    prev, rows = {}, []
    drv = DRIVER[line] if line != "sm" else "revenue"
    for f0 in brows:
        q = f0["quarter"]
        lag = Q.shift(q, -4)
        f = dict(f0)
        fl = [x for x in str(f0.get("flags", "")).split(";") if x]
        use = p["fitted"]
        xs_vals = {}
        if use:
            for name, xs, ks in sigs:
                if known(ks[q], vd) and np.isfinite(xs[q]):
                    xs_vals[name] = float(xs[q])
                elif p.get("ridge"):
                    xs_vals[name] = None          # -> 0 in standardised units
                    fl.append(f"{name}_unknowable_mean")
                else:
                    use = False
                    fl.append(f"{name}_unknowable_revert_m1")
        if use:
            base_ln = float(h.loc[lag, line]) if lag in h.index else prev[lag][line]
            x = p["g"]
            if drv is not None and np.isfinite(p.get("b", np.nan)):
                dq = f0[drv]
                dl = float(h.loc[lag, drv]) if lag in h.index else bq[lag][drv]
                if dq > 0 and dl > 0:
                    x += p["b"] * np.log(dq / dl)
            for name, cval in p["c"].items():
                v = xs_vals.get(name)
                if p.get("ridge"):
                    z = 0.0 if v is None else (v - p["mu"][name]) / p["sd"][name]
                    x += cval * z
                else:
                    x += cval * v
            f[line] = base_ln * np.exp(x)
            f["sum_lines"] = sum(f[ln] for ln in LINES)
            f["adj_ebitda_musd"] = f["revenue"] - f["sum_lines"] + f["other_net"]
            f["adj_ebitda_margin_pct"] = 100.0 * f["adj_ebitda_musd"] / f["revenue"]
            f["total_cash_costs_musd"] = f["revenue"] - f["adj_ebitda_musd"]
        else:
            fl.append("m1_values")
        f["spec_id"] = spec_id
        f["flags"] = ";".join(sorted(set(fl)))
        f["signal_x"] = json.dumps({k: (None if v is None else round(v, 5)) for k, v in xs_vals.items()}) if xs_vals else ""
        prev[q] = f
        rows.append(f)
    return rows


def run_spec(spec_id: str, line: str | None, sigdefs: list, weighting: str, ridge: bool = False, replays=("PIT", "full_sample"),
             vintages=None, live: bool = True, h_back: int | None = None, assume_known: bool = False) -> tuple[list, list]:
    """All forecast rows (backtest at every vintage, LIVE base/bear/bull) for one spec. `sigdefs` = [(name, transform, lead)].
    line None = the `none` spec (M1 rows relabelled).
    `assume_known=True` switches OFF the knowable_from gate. It is used ONLY for the leakage placebos: with the gate on,
    an unknowable alignment simply reverts to M1 and every placebo IV is exactly 1.000, which demonstrates nothing.
    Disabling the gate is what a careless analyst would do, and that is the thing the placebo is meant to price."""
    sigs = [(f"{name}@{lead}", *shifted(*signal_change(name, tr), lead)) for name, tr, lead in sigdefs]
    if assume_known:
        sigs = [(nm, xs, pd.Series([FAR_PAST] * len(ALL_Q), index=ALL_Q, dtype=object)) for nm, xs, ks in sigs]
    rows, prow = [], []
    vints = vintages or VINTAGES
    full_p = None
    if line is not None:
        full_p = fit_aug(FULL_H, line, sigs, TODAY, weighting, anchor=ANCHOR_FULL, ridge=ridge)
        prow.append({"vintage_date": "full_sample", "spec_id": spec_id, **_flat(full_p)})
    for vd in vints:
        for replay in replays:
            brows, _ = base_rows(vd, weighting, replay, live=False, h_max=h_back)
            if line is None:
                out = [dict(r, spec_id=spec_id) for r in brows]
            else:
                p = full_p if replay == "full_sample" else fit_aug(hist(vd), line, sigs, vd, weighting, ridge=ridge)
                if replay == "PIT":
                    prow.append({"vintage_date": vd, "spec_id": spec_id, **_flat(p)})
                out = forecast_aug(vd, line, sigs, p, brows, hist(vd), spec_id)
            rows += out
    if live:
        for vd in LIVE_VINTAGES:
            p_pit = None if line is None else fit_aug(hist(vd), line, sigs, vd, weighting, ridge=ridge)
            for scen in ("base", "bear", "bull"):
                hm = m1.H_ANNUAL if scen == "base" else m1.H_LIVE
                for replay in replays:
                    brows, _ = base_rows(vd, weighting, replay, live=True, scenario=scen, h_max=hm)
                    if line is None:
                        out = [dict(r, spec_id=spec_id) for r in brows]
                    else:
                        p = full_p if replay == "full_sample" else p_pit
                        out = forecast_aug(vd, line, sigs, p, brows, hist(vd), spec_id)
                    rows += out
    return rows, prow


def _flat(p: dict) -> dict:
    d = {"line": p["line"], "n_obs": p["n_obs"], "g": p["g"], "b": p["b"], "flags": p["flags"], "fitted": p["fitted"]}
    for k, v in p["c"].items():
        d[f"c[{k}]"] = v; d[f"se[{k}]"] = p["c_se"].get(k); d[f"t[{k}]"] = p["t"].get(k)
    return d


# ----------------------------------------------------------------------------- incremental value
ACT = m1.PANEL[m1.PANEL["has_actual"].astype(bool)]


def iv_table(aug_rows: list, none_rows: list, line: str, spec_id: str, extra: dict | None = None) -> list:
    """MAE ratios (aug / none) per window, horizon, weighting on the line ($, relative) and the margin (pp)."""
    a = pd.DataFrame(aug_rows); n = pd.DataFrame(none_rows)
    a = a[(a["scenario"] == "backtest") & (a["prior_basis"] == "PIT")]
    n = n[(n["scenario"] == "backtest") & (n["prior_basis"] == "PIT")]
    n = n.set_index(["vintage_date", "quarter"])
    out = []
    for win in ("W1", "W2"):
        for hz in (0, 1, 2):
            ea, en, ma, mn, qq, nk = [], [], [], [], [], 0
            for r in a[a["horizon_q"] == hz].itertuples():
                if win not in windows_for(r.vintage_date, r.quarter) or r.quarter not in ACT.index:
                    continue
                b = n.loc[(r.vintage_date, r.quarter)]
                act = float(ACT.loc[r.quarter, line]); am = float(ACT.loc[r.quarter, "adj_ebitda_margin_pct"])
                ea.append(abs(getattr(r, line) / act - 1)); en.append(abs(b[line] / act - 1))
                ma.append(abs(r.adj_ebitda_margin_pct - am)); mn.append(abs(b["adj_ebitda_margin_pct"] - am))
                qq.append(r.quarter); nk += int("m1_values" not in str(r.flags))
            if not qq:
                continue
            w = recency_weights(qq, ANCHOR_FULL)
            ea, en, ma, mn = map(np.array, (ea, en, ma, mn))
            out.append(dict(spec_id=spec_id, line=line, window=win, horizon_q=hz, n=len(qq), n_signal_used=nk,
                            mape_aug=ea.mean(), mape_none=en.mean(), iv_eq=ea.mean() / en.mean(),
                            iv_rw=float(np.sum(w * ea) / np.sum(w * en)),
                            margin_mae_aug=ma.mean(), margin_mae_none=mn.mean(), iv_margin_eq=ma.mean() / mn.mean(),
                            iv_margin_rw=float(np.sum(w * ma) / np.sum(w * mn)), **(extra or {})))
    return out


def passes(ivs: pd.DataFrame, spec_id: str) -> tuple[bool, dict]:
    s = ivs[(ivs["spec_id"] == spec_id) & (ivs["horizon_q"] == 0)]
    vals = {}
    for r in s.itertuples():
        vals[f"{r.window}_eq"] = r.iv_eq; vals[f"{r.window}_rw"] = r.iv_rw
    ok = all(k in vals and vals[k] < IV_PASS for k in ("W1_eq", "W1_rw", "W2_eq", "W2_rw"))
    return ok, vals


# ----------------------------------------------------------------------------- main
def main() -> int:
    t0 = _dt.datetime.now()
    print(f"M4 alt-augmented: start {t0:%Y-%m-%d %H:%M:%S}")
    all_rows, all_params, ivs, tests = [], [], [], []

    # ---- none (= M1) --------------------------------------------------------------------------
    none = {}
    for wgt in ("rw", "eq"):
        rows, _ = run_spec(f"none_{wgt}", None, [], wgt)
        none[wgt] = rows
        all_rows += rows
    print(f"  none: {len(none['rw'])} rows per weighting")

    # ---- one-signal grid + placebos (rw fit) ----------------------------------------------------
    grid_specs = []
    for line, sig, sign, tr in SIGNALS:
        for lead in LEADS[tr]:
            grid_specs.append((line, sig, sign, tr, lead, "test"))
        for lead in PLACEBO_LEADS[tr]:
            grid_specs.append((line, sig, sign, tr, lead, "placebo_future" if lead < 0 else "placebo_lead0"))
    spec_rows = {}
    for line, sig, sign, tr, lead, kind in grid_specs:
        sid = f"{line}|{sig}@{lead}"
        rows, prow = run_spec(sid, line, [(sig, tr, lead)], "rw", live=False, h_back=2, replays=("PIT",),
                              assume_known=(kind != "test"))
        spec_rows[sid] = rows
        for p in prow:
            all_params.append({**p, "kind": kind, "signal": sig, "lead": lead, "expected_sign": sign})
        c_live = next((p for p in prow if p["vintage_date"] == GUIDE_DATE_LIVE), None)
        c_full = next((p for p in prow if p["vintage_date"] == "full_sample"), None)
        cv = c_live.get(f"c[{sig}@{lead}]") if c_live else np.nan
        cf = c_full.get(f"c[{sig}@{lead}]") if c_full else np.nan
        tf = c_full.get(f"t[{sig}@{lead}]") if c_full else np.nan
        sign_ok = (sign == "either") or (pd.notna(cv) and ((cv > 0) == (sign == "+")))
        extra = dict(kind=kind, signal=sig, lead=lead, expected_sign=sign, c_live=cv, c_full=cf, t_full=tf,
                     n_obs_live=c_live["n_obs"] if c_live else 0, sign_ok=sign_ok)
        ivs += iv_table(rows, none["rw"], line, sid, extra)
    ivs = pd.DataFrame(ivs)
    for line, sig, sign, tr, lead, kind in grid_specs:
        sid = f"{line}|{sig}@{lead}"
        ok, vals = passes(ivs, sid)
        r0 = ivs[(ivs["spec_id"] == sid)].iloc[0]
        h1 = ivs[(ivs["spec_id"] == sid) & (ivs["horizon_q"] == 1)]
        tests.append(dict(spec_id=sid, line=line, signal=sig, lead=lead, kind=kind, expected_sign=sign, c_live=r0["c_live"],
                          c_full=r0["c_full"], t_full=r0["t_full"], n_obs_live=r0["n_obs_live"], sign_ok=bool(r0["sign_ok"]),
                          **{f"iv_h0_{k}": v for k, v in vals.items()},
                          **{f"iv_h1_{r.window}_{w}": getattr(r, f"iv_{w}") for r in h1.itertuples() for w in ("eq", "rw")},
                          **{f"n_signal_used_h0_{r.window}": int(r.n_signal_used) for r in
                             ivs[(ivs["spec_id"] == sid) & (ivs["horizon_q"] == 0)].itertuples()},
                          iv_margin_h0_W1_rw=float(ivs[(ivs["spec_id"] == sid) & (ivs["horizon_q"] == 0) & (ivs["window"] == "W1")]["iv_margin_rw"].iloc[0]),
                          iv_margin_h0_W2_rw=float(ivs[(ivs["spec_id"] == sid) & (ivs["horizon_q"] == 0) & (ivs["window"] == "W2")]["iv_margin_rw"].iloc[0]),
                          iv_pass=ok, survives=bool(ok and r0["sign_ok"] and kind == "test")))
    tests = pd.DataFrame(tests)
    tests.to_csv(OUT / "M4_alt_augmented_signal_tests.csv", index=False)
    ivs.to_csv(OUT / "M4_alt_augmented_iv_grid.csv", index=False)
    survivors = tests[tests["survives"]]
    print(f"  grid: {len(grid_specs)} specs ({(tests['kind']=='test').sum()} tests, {(tests['kind']!='test').sum()} placebos); "
          f"survivors: {list(survivors['spec_id'])}")

    # ---- random-series placebo ------------------------------------------------------------------
    rng = np.random.default_rng(SEED)
    rand_rows = []
    w1_vints = list(GUIDE_DATES_W1)
    for line in LINES:
        for i in range(N_RANDOM):
            name = f"rand_{line}_{i}"
            x = pd.Series(rng.standard_normal(len(ALL_Q)), index=ALL_Q)
            k = pd.Series([FAR_PAST] * len(ALL_Q), index=ALL_Q, dtype=object)
            _SIG_CACHE[name] = (x, k)
            rows, _ = run_spec(f"{line}|{name}", line, [(name, "dlog", 1)], "rw", replays=("PIT",), vintages=w1_vints,
                               live=False, h_back=1)
            t = pd.DataFrame(iv_table(rows, none["rw"], line, f"{line}|{name}"))
            rec = {"line": line, "i": i}
            for r in t.itertuples():
                rec[f"iv_h{r.horizon_q}_{r.window}_eq"] = r.iv_eq; rec[f"iv_h{r.horizon_q}_{r.window}_rw"] = r.iv_rw
                rec[f"ivm_h{r.horizon_q}_{r.window}_rw"] = r.iv_margin_rw
            rec["pass_h0"] = all(rec.get(f"iv_h0_{w}_{g}", 9) < IV_PASS for w in ("W1", "W2") for g in ("eq", "rw"))
            rec["sel_score"] = np.mean([rec.get("iv_h0_W1_rw", 9), rec.get("iv_h0_W2_rw", 9)])
            rand_rows.append(rec)
            del _SIG_CACHE[name]
    rand = pd.DataFrame(rand_rows)
    rand.to_csv(OUT / "M4_alt_augmented_placebo_random.csv", index=False)
    summ = []
    for line, g in rand.groupby("line"):
        g = g.sort_values("i")
        best5 = [g.iloc[j:j + 5].sort_values("sel_score").iloc[0] for j in range(0, len(g), 5)]
        b5 = pd.DataFrame(best5)
        summ.append(dict(line=line, n=len(g), fp_rate_single=g["pass_h0"].mean(), fp_rate_best_of_5=b5["pass_h0"].mean(),
                         iv_h0_W1_rw_p05=g["iv_h0_W1_rw"].quantile(.05), iv_h0_W1_rw_p50=g["iv_h0_W1_rw"].median(),
                         iv_h0_W2_rw_p05=g["iv_h0_W2_rw"].quantile(.05), iv_h0_W2_rw_p50=g["iv_h0_W2_rw"].median(),
                         iv_h0_W1_eq_p50=g["iv_h0_W1_eq"].median(), iv_h0_W2_eq_p50=g["iv_h0_W2_eq"].median(),
                         best5_sel_score_p50=b5["sel_score"].median(), best5_sel_score_p05=b5["sel_score"].quantile(.05),
                         best5_iv_h0_W1_rw_p50=b5["iv_h0_W1_rw"].median(), best5_iv_h0_W2_rw_p50=b5["iv_h0_W2_rw"].median(),
                         ivm_h0_W1_rw_p50=g["ivm_h0_W1_rw"].median(), ivm_h0_W2_rw_p50=g["ivm_h0_W2_rw"].median()))
    summ = pd.DataFrame(summ)
    summ.to_csv(OUT / "M4_alt_augmented_placebo_summary.csv", index=False)
    print("  random placebo:\n" + summ[["line", "fp_rate_single", "fp_rate_best_of_5", "iv_h0_W1_rw_p50", "iv_h0_W2_rw_p50"]].to_string(index=False))

    # ---- best1 (in-sample selection by mean h=0 rw IV over W1/W2 among `test` specs) ---------------
    cand = tests[tests["kind"] == "test"].copy()
    cand["sel_score"] = cand[["iv_h0_W1_rw", "iv_h0_W2_rw"]].mean(axis=1)
    best = cand.sort_values("sel_score").groupby("line").head(1).set_index("line")
    best_sigdefs = {ln: [(best.loc[ln, "signal"], next(t for l, s, _, t in SIGNALS if l == ln and s == best.loc[ln, "signal"]),
                          int(best.loc[ln, "lead"]))] for ln in LINES if ln in best.index}
    for ln in LINES:
        best_sigdefs.setdefault(ln, [])          # a line with no usable candidate stays pure M1
    best.to_csv(OUT / "M4_alt_augmented_best1_selection.csv")
    print("  best1 per line: " + "; ".join(f"{ln}: {v[0][0]}@{v[0][2]} (score {best.loc[ln,'sel_score']:.3f})" for ln, v in best_sigdefs.items()))

    # ---- registered specs: best1, ridge_all, survivors; both weightings; LIVE --------------------------
    reg_specs = {}
    ridge_sigdefs = {ln: [(s, t, DEFAULT_LEAD[t]) for l, s, _, t in SIGNALS if l == ln] for ln in LINES}
    for wgt in ("rw", "eq"):
        for fam, sdmap, ridge in (("best1", best_sigdefs, False), ("ridge_all", ridge_sigdefs, True)):
            sid = f"{fam}_{wgt}"
            rows = None
            # apply the per-line augmentation sequentially: each line's rows built on M1 rows, then merged
            merged = None
            for ln in LINES:
                r_ln, prow = run_spec(sid, ln, sdmap[ln], wgt, ridge=ridge)
                for p in prow:
                    all_params.append({**p, "kind": fam, "signal": "|".join(s for s, _, _ in sdmap[ln]), "lead": "", "expected_sign": ""})
                df = pd.DataFrame(r_ln)
                if merged is None:
                    merged = df.copy()
                    merged["flags"] = merged["flags"].astype(str)
                else:
                    merged[ln] = df[ln].to_numpy()
                    merged["flags"] = [";".join(sorted(set(a.split(";")) | set(str(b).split(";")))) for a, b in zip(merged["flags"], df["flags"])]
                    merged["signal_x"] = [(a or "") + (b or "") for a, b in zip(merged["signal_x"].fillna(""), df["signal_x"].fillna(""))]
            merged["sum_lines"] = merged[LINES].sum(axis=1)
            merged["adj_ebitda_musd"] = merged["revenue"] - merged["sum_lines"] + merged["other_net"]
            merged["adj_ebitda_margin_pct"] = 100 * merged["adj_ebitda_musd"] / merged["revenue"]
            merged["total_cash_costs_musd"] = merged["revenue"] - merged["adj_ebitda_musd"]
            reg_specs[sid] = (merged.to_dict("records"), fam)
            all_rows += reg_specs[sid][0]
    for r in survivors.itertuples():
        tr = next(t for l, s, _, t in SIGNALS if l == r.line and s == r.signal)
        sid = f"surv_{r.signal}_rw"
        rows, prow = run_spec(sid, r.line, [(r.signal, tr, int(r.lead))], "rw")
        for p in prow:
            all_params.append({**p, "kind": "surv", "signal": r.signal, "lead": r.lead, "expected_sign": r.expected_sign})
        reg_specs[sid] = (rows, "surv")
        all_rows += rows
    # IV of the registered composite specs vs none (same weighting)
    comp_iv = []
    for sid, (rows, fam) in reg_specs.items():
        wgt = sid.split("_")[-1]
        for ln in LINES:
            comp_iv += iv_table(rows, none[wgt], ln, sid, {"kind": fam})
    comp_iv = pd.DataFrame(comp_iv)
    comp_iv.to_csv(OUT / "M4_alt_augmented_iv_registered.csv", index=False)

    wide = pd.DataFrame(all_rows)
    wide["vintage_date"] = pd.to_datetime(wide["vintage_date"]).dt.date
    wide.to_csv(OUT / "M4_alt_augmented_forecasts_wide.csv", index=False)
    pd.DataFrame(all_params).to_csv(OUT / "M4_alt_augmented_coefs_by_vintage.csv", index=False)

    # ---- registry -------------------------------------------------------------------------------
    reg_ids = ["none_rw", "none_eq"] + list(reg_specs)
    pd_map = {Q.canon(r.quarter): r.print_date for r in load_targets().itertuples() if pd.notna(r.print_date)}
    target_cols = {**{v: k for k, v in LINE_TARGET.items()}, **{t: t for t in MARGIN_TARGETS}}
    fam_of = lambda sid: "none" if sid.startswith("none") else ("surv" if sid.startswith("surv") else sid.rsplit("_", 1)[0])  # noqa: E731
    long_rows, pool_rows = [], []
    reg = wide[wide["spec_id"].isin(reg_ids)]
    for r in reg[(reg["scenario"] == "backtest") | (reg["scenario"] == "base")].itertuples():
        wins = windows_for(r.vintage_date, r.quarter)
        for tg, col in target_cols.items():
            actual = float(ACT.loc[r.quarter, tg]) if r.quarter in ACT.index else np.nan
            pt = float(getattr(r, col))
            if r.scenario == "backtest":
                pool_rows.append(dict(spec_id=r.spec_id, target=tg, horizon_q=int(r.horizon_q), prior_basis=r.prior_basis,
                                      quarter=r.quarter, vintage_date=r.vintage_date, point=pt, actual=actual,
                                      target_print_date=pd_map.get(r.quarter)))
            for w in wins:
                if (w == "LIVE") != (r.scenario == "base"):
                    continue
                obj = "lines_aug" if tg in LINE_TARGET.values() else "margin_aug"
                long_rows.append(dict(method=METHOD, object=obj, target=tg, quarter=r.quarter, vintage_date=r.vintage_date,
                                      horizon_q=int(r.horizon_q), point=pt, window=w, prior_basis=r.prior_basis,
                                      spec_id=r.spec_id, n_params=N_PARAMS[fam_of(r.spec_id)], n_train=int(r.n_train),
                                      knowable_from=r.knowable_from, actual=actual, target_print_date=pd_map.get(r.quarter),
                                      notes=f"rev_leg={r.rev_leg};scenario={r.scenario};{r.flags}"[:240]))
    long = pd.DataFrame(long_rows); pool = pd.DataFrame(pool_rows)
    long["_reg"] = True; pool["_reg"] = False
    both = m1.attach_quantiles(pd.concat([long, pool], ignore_index=True, sort=False))
    long = both[both["_reg"] == True].drop(columns=["_reg"]).copy()   # noqa: E712
    long["q50"] = long["point"]
    long.to_csv(OUT / "M4_alt_augmented_registry_long.csv", index=False)
    reg_cols = ["method", "object", "target", "quarter", "vintage_date", "horizon_q", "point", "q50", "window", "prior_basis",
                "n_params", "n_train", "q05", "q10", "q25", "q75", "q90", "q95", "sd", "knowable_from", "spec_id", "notes"]
    for obj in ("lines_aug", "margin_aug"):
        register(long[long["object"] == obj][reg_cols].reset_index(drop=True), quiet=False)
    print(f"  registered {len(long)} rows in 2 objects, specs {reg_ids}")

    # ---- LIVE tables ------------------------------------------------------------------------------
    live = wide[(wide["scenario"] != "backtest") & (wide["vintage_date"] == TODAY) & (wide["spec_id"].isin(reg_ids))].copy()
    m1live = pd.read_csv(M1_LIVE)
    cmp_cols = ["quarter", "scenario", "cons_revenue_musd", "cons_ebitda_musd", "cons_margin_pct", "ws31b_base_margin_pct",
                "ws30_margin_pct", "mgmt_3q26_ceiling_margin_pct"]
    cmp = m1live[(m1live["spec_id"] == "b_elastic_rw") & (m1live["prior_basis"] == "PIT")][cmp_cols].drop_duplicates(["quarter", "scenario"])
    lq = live[live["quarter"] <= "2027Q4"].merge(cmp, on=["quarter", "scenario"], how="left")
    keep = ["quarter", "scenario", "spec_id", "prior_basis", "horizon_q", "revenue", "nights", "gbv"] + LINES + \
           ["other_net", "adj_ebitda_musd", "adj_ebitda_margin_pct", "total_cash_costs_musd", "flags", "signal_x"] + cmp_cols[2:]
    lq[keep].to_csv(OUT / "M4_alt_augmented_live_quarterly.csv", index=False)
    # delta vs none per quarter
    piv = lq[lq["prior_basis"] == "PIT"].pivot_table(index=["quarter", "scenario"], columns="spec_id", values="adj_ebitda_margin_pct")
    piv.to_csv(OUT / "M4_alt_augmented_live_margin_by_spec.csv")

    h1 = ACT.loc[["2026Q1", "2026Q2"]]
    ann = []
    for (spec, scen, replay), g in live.groupby(["spec_id", "scenario", "prior_basis"]):
        g = g.set_index("quarter")
        for fy, qs in (("FY26", ["2026Q3", "2026Q4"]), ("FY27", [f"2027Q{i}" for i in range(1, 5)]), ("FY28", [f"2028Q{i}" for i in range(1, 5)])):
            if not all(q in g.index for q in qs):
                continue
            rec = {"fy": fy, "scenario": scen, "spec_id": spec, "prior_basis": replay}
            for c in ["revenue", "nights", "gbv"] + LINES + ["other_net", "adj_ebitda_musd"]:
                v = g.loc[qs, c].sum() + (h1[c].sum() if fy == "FY26" and c in h1.columns else 0.0)
                rec[c] = float(v)
            rec["adj_ebitda_margin_pct"] = 100 * rec["adj_ebitda_musd"] / rec["revenue"]
            ann.append(rec)
    ann = pd.DataFrame(ann)
    m1ann = pd.read_csv(M1_ANNUAL)
    m1ann = m1ann[(m1ann["spec_id"] == "b_elastic_rw") & (m1ann["prior_basis"] == "PIT")][
        ["fy", "scenario", "cons_ebitda_musd", "cons_margin_pct", "ws31b_base_margin_pct", "ws30_margin_pct", "mgmt_fy26_floor_pct"]]
    ann = ann.merge(m1ann, on=["fy", "scenario"], how="left")
    ann.to_csv(OUT / "M4_alt_augmented_annual_forecasts.csv", index=False)

    # ---- figures ----------------------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        tt = tests.copy()
        tt["label"] = tt["line"] + " | " + tt["signal"].str.replace("_cash", "").str[:26] + "@" + tt["lead"].astype(str)
        fig, ax = plt.subplots(figsize=(11, 12))
        colors = {"test": "#1f77b4", "placebo_lead0": "#ff7f0e", "placebo_future": "#7f7f7f"}
        tt = tt.sort_values(["line", "kind", "signal", "lead"]).reset_index(drop=True)
        y = np.arange(len(tt))
        ax.scatter(tt["iv_h0_W1_rw"], y, c=tt["kind"].map(colors), marker="o", label="W1 (n 14)")
        ax.scatter(tt["iv_h0_W2_rw"], y, c=tt["kind"].map(colors), marker="s", label="W2 (n 10)")
        for k, c in colors.items():
            ax.scatter([], [], c=c, label=k)
        ax.axvline(1.0, color="k", lw=.8); ax.axvline(IV_PASS, color="r", ls="--", lw=.8, label="pass line 0.9")
        for ln, g in summ.set_index("line").iterrows():
            pass
        ax.set_yticks(y); ax.set_yticklabels(tt["label"], fontsize=7)
        ax.set_xlabel("incremental value = MAE(M1 + signal) / MAE(M1), line $, h=0, recency-weighted")
        ax.set_title("M4: one-signal augmentations of M1 (blue = knowable; orange = lead 0, unknowable at h=0; grey = +4q future shift)")
        ax.legend(fontsize=7, loc="lower right"); ax.grid(alpha=.3); ax.set_xlim(0.4, 1.8); fig.tight_layout()
        fig.savefig(FIG / "M4_alt_augmented_iv_grid.png", dpi=130); plt.close(fig)

        fig, axes = plt.subplots(1, 5, figsize=(15, 3.6), sharey=True)
        for ax, ln in zip(axes, LINES):
            g = rand[rand["line"] == ln]
            ax.hist(g["sel_score"], bins=30, color="#bbbbbb", label="random (200)")
            c = cand[cand["line"] == ln]
            for r in c.itertuples():
                ax.axvline(r.sel_score, color="#1f77b4", lw=1)
            ax.axvline(IV_PASS, color="r", ls="--", lw=.8)
            ax.set_title(ln); ax.set_xlabel("mean h=0 rw IV (W1, W2)")
        axes[0].legend(fontsize=7); fig.suptitle("M4: real signals (blue lines) against the random-series null"); fig.tight_layout()
        fig.savefig(FIG / "M4_alt_augmented_placebo.png", dpi=130); plt.close(fig)
    except Exception as e:  # pragma: no cover
        print(f"  figure skipped: {e}")

    # ---- scoreboard --------------------------------------------------------------------------------
    # WS22 discussion round: three agents re-run their packages concurrently, so score.py is run ONCE by
    # the orchestrator afterwards. MARGIN_SKIP_SCORE=1 skips it here; the scoreboard copy below is then
    # the previous scoring and is stale until the orchestrator re-scores.
    if os.environ.get("MARGIN_SKIP_SCORE") == "1":
        print("  MARGIN_SKIP_SCORE=1: skipping score.py (orchestrator re-scores once)")
    else:
        print("  running score.py ...")
        rc = subprocess.run([sys.executable, str(HARNESS / "score.py")], cwd=str(REPO), capture_output=True, text=True)
        print(rc.stdout[-1500:])
        if rc.returncode != 0:
            print(rc.stderr[-3000:])
            return rc.returncode
    sbp = MB / "10_harness_margin" / "scoreboard_margin.csv"
    if sbp.exists():
        sb = pd.read_csv(sbp)
        sb[sb["method"] == METHOD].to_csv(OUT / "M4_alt_augmented_scoreboard_rows.csv", index=False)
    else:
        print("  scoreboard_margin.csv absent (harness mid-rebuild); keeping the previous scoreboard rows")
    json.dump({"built": f"{t0:%Y-%m-%d %H:%M:%S}", "n_forecast_rows": int(len(wide)), "n_registry_rows": int(len(long)),
               "specs_registered": reg_ids, "n_tests": int((tests["kind"] == "test").sum()),
               "n_placebo_specs": int((tests["kind"] != "test").sum()), "n_random": N_RANDOM * len(LINES),
               "survivors": list(survivors["spec_id"]), "best1": {ln: f"{v[0][0]}@{v[0][2]}" for ln, v in best_sigdefs.items()}},
              open(OUT / "M4_alt_augmented_build.json", "w"), indent=2)
    print(f"done in {(_dt.datetime.now() - t0).total_seconds():.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
