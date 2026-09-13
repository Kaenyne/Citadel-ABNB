"""M1: driver-based cost lines v2 (per-unit costs on the revenue drivers), point-in-time.

Rebuilds the whole package: PIT refits at every guide date, both replays, both weightings, quantiles,
registration through the margin harness (method `driver-lines`, objects `margin_v2` and `lines_v2`),
LIVE forecasts on the WS06 revenue path (base / bear / bull), annual FY26-28, figures, and the scoreboard.

    cd "C:\\Users\\krish\\citadel-abnb-margins"
    py -3.13 analysis/src/margin_build/M1_driver_lines/run.py

Model (see docs/margin-build/notes/M1_driver_lines.md section 0 for the pre-registration):
    d4 log L_q = g_L + b_L * d4 log D_q + sum_k c_Lk * d4 step_kq + e_q      (d4 x = x_q - x_{q-4})
for L in {cor, ops, pd, sm, ga ex lodging reserves}; D = GBV (cor), nights (ops), revenue (sm); pd, ga trend only.
adj EBITDA = revenue - sum(lines) + other_net (D&A + non-reserve add-backs, trailing-4 share of revenue).
"""
from __future__ import annotations

import datetime as _dt
import json
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
    load_targets, history_as_of, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATE_LIVE, TODAY,
    windows_for, register, revenue_forecast_pit, Q, recency_weights, load_registry,
)

warnings.filterwarnings("ignore", category=FutureWarning)

METHOD = "driver-lines"
OUT = REPO / "data" / "processed" / "margin_build" / "M1_driver_lines"
FIG = REPO / "analysis" / "figures" / "margin_build"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

MB = REPO / "data" / "processed" / "margin_build"
WS06_DIR = MB / "06_fy27_path_v2"
WS06_LONG_V2B = WS06_DIR / "06_revenue_path_3q26_4q27_v2b.csv"      # WS06v checker output (long format), preferred
WS06_WIDE = WS06_LONG_V2B if WS06_LONG_V2B.exists() else WS06_DIR / "06_revenue_path_wide.csv"
WS06_CONS27 = WS06_DIR / "06_consensus_quarterly_2027.csv"
WS03_CURRENT = MB / "03_consensus_pit" / "03_current_consensus.csv"
WS04_PANEL = MB / "04_alt_signals" / "04_signal_panel_quarterly.csv"
WS10_REGIONAL = REPO / "data" / "processed" / "overnight" / "10_regional_panel_quarterly.csv"
WS31B_PROFILE = REPO / "data" / "processed" / "overnight" / "31b_forward_margin_by_profile.csv"
WS30_FY = REPO / "data" / "processed" / "overnight" / "30_fy_summary.csv"
WS06_ASSUMP = WS06_DIR / "06_assumptions.csv"

LINES = ["cor", "ops", "pd", "sm", "ga"]
LINE_TARGET = {"cor": "cor_cash_musd", "ops": "ops_cash_musd", "pd": "pd_cash_musd", "sm": "sm_cash_musd",
               "ga": "ga_cash_ex_reserves_musd"}
DRIVER = {"cor": "gbv", "ops": "nights", "sm": "revenue", "pd": None, "ga": None}
STEPS = {"cor": ["event_E02_cor_cash", "event_E09_cor_cash"], "ops": ["event_E05_ops_cash"],
         "pd": ["event_E10_pd_cash"], "sm": [], "ga": []}
MIX_LINES = ["cor", "ops"]

HALF_LIFE = 4.0
MIN_OBS = 4
FIRST_YOY_MAIN = "2022Q1"      # levels from 1Q21: 2020 never in the base year
FIRST_YOY_2020 = "2021Q1"      # the "incl. 2020" variant
H_BACK, H_LIVE, H_ANNUAL = 2, 5, 9   # h=0..2 backtest; 0..5 LIVE (3Q26..4Q27); 6..9 for FY28 (base only)
RESID_MAX_N, MIN_RESID = 12, 3
FALLBACK_REL, FALLBACK_PP = 0.10, 3.0
QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
ZQ = dict(zip(QCOLS, [-1.6448536269514722, -1.2815515655446004, -0.6744897501960817, 0.0,
                      0.6744897501960817, 1.2815515655446004, 1.6448536269514722]))

# spec_id -> (family, weighting, first_yoy_quarter, sm_driver)
SPECS = {
    "a_unit_rw":      ("a", "rw", FIRST_YOY_MAIN, "revenue"),
    "a_unit_eq":      ("a", "eq", FIRST_YOY_MAIN, "revenue"),
    "b_elastic_rw":   ("b", "rw", FIRST_YOY_MAIN, "revenue"),
    "b_elastic_eq":   ("b", "eq", FIRST_YOY_MAIN, "revenue"),
    "c_mix_rw":       ("c", "rw", FIRST_YOY_MAIN, "revenue"),
    "d_steps_rw":     ("d", "rw", FIRST_YOY_MAIN, "revenue"),
    "e_revknown_rw":  ("e", "rw", FIRST_YOY_MAIN, "revenue"),
}
# grid-only variants (reported in the note, not registered)
GRID_EXTRA = {
    "b_smnights_rw":      ("b", "rw", FIRST_YOY_MAIN, "nights"),
    "a_unit_rw_incl2020": ("a", "rw", FIRST_YOY_2020, "revenue"),
    "b_elastic_rw_incl2020": ("b", "rw", FIRST_YOY_2020, "revenue"),
}
ALL_SPECS = {**SPECS, **GRID_EXTRA}
N_PARAMS = {"a": 7, "b": 10, "c": 12, "d": 14, "e": 10}
MAIN_SPEC = "b_elastic_rw"
MARGIN_TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd", "total_cash_costs_musd"]
RELATIVE_TARGETS = set(LINE_TARGET.values()) | {"adj_ebitda_musd", "total_cash_costs_musd"}


# ----------------------------------------------------------------------------- data
def build_panel() -> pd.DataFrame:
    """One row per quarter with actual lines, drivers, other_net, mix and steps (levels)."""
    t = load_targets().copy()
    t["quarter"] = t["quarter"].map(Q.canon)
    p = t[["quarter", "print_date", "has_actual", "revenue_musd", "nights_m", "gbv_musd", "adj_ebitda_musd",
           "adj_ebitda_margin_pct", "da_musd"] + list(LINE_TARGET.values())].copy()
    p = p.rename(columns={"revenue_musd": "revenue", "nights_m": "nights", "gbv_musd": "gbv"})
    for ln, col in LINE_TARGET.items():
        p[ln] = pd.to_numeric(p[col], errors="coerce")
    p["sum_lines"] = p[LINES].sum(axis=1, min_count=5)
    p["other_net"] = p["adj_ebitda_musd"] - p["revenue"] + p["sum_lines"]
    p["total_cash_costs_musd"] = p["revenue"] - p["adj_ebitda_musd"]
    # regional mix: ex-NA nights share (pp), WS10 estimate, 1Q22+
    r = pd.read_csv(WS10_REGIONAL)
    r["quarter"] = r["quarter"].map(Q.canon)
    r["exna_share"] = 100.0 - pd.to_numeric(r["na_nights_share_est_pct"], errors="coerce")
    p = p.merge(r[["quarter", "exna_share"]], on="quarter", how="left")
    # step dummies (levels) from WS04
    s = pd.read_csv(WS04_PANEL)
    s["quarter"] = s["quarter"].map(Q.canon)
    stepcols = sorted({c for v in STEPS.values() for c in v})
    p = p.merge(s[["quarter"] + stepcols], on="quarter", how="left")
    p = p.sort_values("quarter").reset_index(drop=True)
    for c in stepcols:
        p[c] = p[c].ffill().fillna(0.0)
    p = p.set_index("quarter")
    return p


PANEL = build_panel()
STEPCOLS = sorted({c for v in STEPS.values() for c in v})


def hist_as_of(vd) -> pd.DataFrame:
    h = history_as_of(vd)
    qs = set(h["quarter"].map(Q.canon))
    return PANEL[PANEL.index.isin(qs) & PANEL["has_actual"].astype(bool)]


# ----------------------------------------------------------------------------- fitting
def _d4(series: pd.Series, q: str):
    lag = Q.shift(q, -4)
    if q in series.index and lag in series.index and pd.notna(series[q]) and pd.notna(series[lag]):
        return series[q], series[lag]
    return None, None


def design_rows(h: pd.DataFrame, line: str, family: str, first_yoy: str, sm_driver: str):
    """(quarters, y, X columns dict) of the y/y observations available in history h for one line."""
    drv = DRIVER[line] if line != "sm" else sm_driver
    rows = []
    for q in h.index:
        if q < first_yoy:
            continue
        lq, llag = _d4(h[line], q)
        if lq is None or lq <= 0 or llag <= 0:
            continue
        rec = {"quarter": q, "y": np.log(lq / llag)}
        if drv is not None:
            dq, dlag = _d4(h[drv], q)
            if dq is None or dq <= 0 or dlag <= 0:
                continue
            rec["dlogD"] = np.log(dq / dlag)
        if family == "c" and line in MIX_LINES:
            mq, mlag = _d4(h["exna_share"], q)
            rec["mix"] = (mq - mlag) if mq is not None else np.nan
        if family == "d":
            for sc in STEPS[line]:
                sq, slag = _d4(h[sc], q)
                rec[sc] = (sq - slag) if sq is not None else 0.0
        rows.append(rec)
    return pd.DataFrame(rows)


def fit_line(h: pd.DataFrame, line: str, spec: str, anchor: str | None = None) -> dict:
    """Weighted least squares on y/y log changes. Returns the parameter dict for one line."""
    family, weighting, first_yoy, sm_driver = ALL_SPECS[spec]
    fam_for_design = family if family != "e" else "b"
    d = design_rows(h, line, fam_for_design, first_yoy, sm_driver)
    flags = []
    if len(d) < MIN_OBS and first_yoy != FIRST_YOY_2020:
        d = design_rows(h, line, fam_for_design, FIRST_YOY_2020, sm_driver)
        flags.append("added_2021_obs")
    out = {"line": line, "spec": spec, "n_obs": int(len(d)), "g": np.nan, "b": np.nan, "b_imposed": False,
           "c_mix": np.nan, "flags": ""}
    for sc in STEPS[line]:
        out[f"c_{sc}"] = np.nan
    if len(d) == 0:
        out["g"] = 0.0
        out["flags"] = "no_obs"
        return out
    T = anchor or h.index.max()
    w = recency_weights(list(d["quarter"]), T) if weighting == "rw" else np.ones(len(d)) / len(d)
    y = d["y"].to_numpy(dtype=float)
    cols = ["const"]
    X = [np.ones(len(d))]
    drv = DRIVER[line] if line != "sm" else sm_driver
    if family == "a":
        b_imp = 1.0 if line in ("cor", "ops") else 0.0
        if drv is not None and b_imp != 0.0:
            y = y - b_imp * d["dlogD"].to_numpy(dtype=float)
        out["b"] = b_imp if drv is not None else np.nan
        out["b_imposed"] = True
    else:
        if drv is not None and line in ("cor", "ops", "sm"):
            cols.append("dlogD"); X.append(d["dlogD"].to_numpy(dtype=float))
        if fam_for_design == "c" and line in MIX_LINES:
            m = d["mix"].to_numpy(dtype=float)
            ok = np.isfinite(m)
            if ok.sum() >= MIN_OBS:
                cols.append("mix"); X.append(np.where(ok, m, 0.0))
                if (~ok).any():
                    flags.append("mix_missing_zeroed")
            else:
                flags.append("mix_unidentified")
        if fam_for_design == "d":
            for sc in STEPS[line]:
                v = d[sc].to_numpy(dtype=float)
                if (v != 0).sum() >= 2:
                    cols.append(sc); X.append(v)
                else:
                    flags.append(f"{sc}_unidentified")
    X = np.column_stack(X)
    if len(d) < X.shape[1] + 1:      # too few observations for the columns: drop to trend only
        X = X[:, :1]; cols = cols[:1]
        flags.append("trend_only_small_n")
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    for c, bv in zip(cols, beta):
        if c == "const":
            out["g"] = float(bv)
        elif c == "dlogD":
            out["b"] = float(bv)
        elif c == "mix":
            out["c_mix"] = float(bv)
        else:
            out[f"c_{c}"] = float(bv)
    out["flags"] = ";".join(flags)
    return out


def fit_all(h: pd.DataFrame, spec: str, anchor: str | None = None) -> dict:
    return {ln: fit_line(h, ln, spec, anchor) for ln in LINES}


# ----------------------------------------------------------------------------- drivers
def last_ratio_yoy(h: pd.DataFrame, num: str, den: str) -> float:
    last = h.index.max()
    lag = Q.shift(last, -4)
    if lag not in h.index:
        return 0.0
    r1 = h.loc[last, num] / h.loc[last, den]
    r0 = h.loc[lag, num] / h.loc[lag, den]
    return float(r1 / r0 - 1.0)


def pit_drivers(vd, q: str, h: pd.DataFrame, prev: dict) -> dict:
    """PIT driver levels for quarter q: revenue from the frozen harness leg; nights and GBV from the
    y/y revenue growth adjusted by the last printed revenue-per-night and take-rate changes."""
    rev, leg = revenue_forecast_pit(vd, q, "PIT")
    lag = Q.shift(q, -4)
    base = h.loc[lag] if lag in h.index else prev.get(lag)
    if base is None or not np.isfinite(rev):
        return {"revenue": np.nan, "nights": np.nan, "gbv": np.nan, "leg": leg}
    growth = rev / base["revenue"]
    rpn = last_ratio_yoy(h, "revenue", "nights")
    tr = last_ratio_yoy(h, "revenue", "gbv")
    return {"revenue": rev, "nights": base["nights"] * growth / (1.0 + rpn),
            "gbv": base["gbv"] * growth / (1.0 + tr), "leg": leg}


def oracle_drivers(q: str) -> dict | None:
    if q in PANEL.index and bool(PANEL.loc[q, "has_actual"]):
        r = PANEL.loc[q]
        return {"revenue": float(r["revenue"]), "nights": float(r["nights"]), "gbv": float(r["gbv"]), "leg": "actual"}
    return None


def load_ws06() -> pd.DataFrame:
    w = pd.read_csv(WS06_WIDE)
    if "line" in w.columns:      # the long v2b file: pivot to wide
        w = w.pivot_table(index=["quarter", "scenario"], columns="line", values="value").reset_index()
    w["quarter"] = w["quarter"].map(Q.canon)
    w["gbv"] = w["gbv_busd"] * 1000.0
    w = w.rename(columns={"revenue_musd": "revenue", "nights_mm": "nights"})
    return w.set_index(["quarter", "scenario"])[["revenue", "nights", "gbv", "nights_yoy_pct", "adr_exfx_yoy_pct"]]


WS06 = load_ws06()


def live_drivers(q: str, scenario: str) -> dict | None:
    key = (q, scenario)
    if key in WS06.index:
        r = WS06.loc[key]
        return {"revenue": float(r["revenue"]), "nights": float(r["nights"]), "gbv": float(r["gbv"]),
                "leg": f"ws06_{scenario}"}
    return None


def live_mix_d4(q: str, h: pd.DataFrame) -> float:
    """d4 of the ex-NA nights share for a LIVE quarter: WS06 na_share for 3Q26/4Q26, then held at the 4Q26 change."""
    a = pd.read_csv(WS06_ASSUMP).set_index("name")["value"]
    na = {"2026Q3": float(a["na_share_3Q26"]) * 100, "2026Q4": float(a["na_share_4Q26"]) * 100}
    lag = Q.shift(q, -4)
    if q in na and lag in h.index and pd.notna(h.loc[lag, "exna_share"]):
        return (100 - na[q]) - h.loc[lag, "exna_share"]
    # beyond 4Q26: hold the last printed d4 change
    last = h.index.max()
    l4 = Q.shift(last, -4)
    if l4 in h.index and pd.notna(h.loc[last, "exna_share"]) and pd.notna(h.loc[l4, "exna_share"]):
        return float(h.loc[last, "exna_share"] - h.loc[l4, "exna_share"])
    return 0.0


# ----------------------------------------------------------------------------- forecasting
def forecast_quarter(params: dict, spec: str, h: pd.DataFrame, q: str, drv: dict, prev: dict,
                     mix_d4: float | None) -> dict | None:
    """Levels for quarter q given fitted params, PIT history h, driver levels drv and the chain `prev`
    (quarter -> dict of forecast levels for quarters not yet printed)."""
    family, _, _, sm_driver = ALL_SPECS[spec]
    lag = Q.shift(q, -4)
    base = h.loc[lag] if lag in h.index else prev.get(lag)
    if base is None or not np.isfinite(drv["revenue"]):
        return None
    out = {"quarter": q, "revenue": drv["revenue"], "nights": drv["nights"], "gbv": drv["gbv"]}
    for ln in LINES:
        p = params[ln]
        dname = DRIVER[ln] if ln != "sm" else sm_driver
        x = p["g"]
        if dname is not None and np.isfinite(p.get("b", np.nan)) and p["b"] != 0.0:
            dq, dl = drv[dname], base[dname]
            if dq > 0 and dl > 0:
                x += p["b"] * np.log(dq / dl)
        if family == "c" and ln in MIX_LINES and np.isfinite(p.get("c_mix", np.nan)) and mix_d4 is not None:
            x += p["c_mix"] * mix_d4
        if family == "d":
            for sc in STEPS[ln]:
                c = p.get(f"c_{sc}", np.nan)
                if np.isfinite(c):
                    # step level for a future quarter: persists at the last known level
                    lvl_q = PANEL.loc[q, sc] if q in PANEL.index else PANEL[sc].iloc[-1]
                    lvl_l = PANEL.loc[lag, sc] if lag in PANEL.index else 0.0
                    x += c * (lvl_q - lvl_l)
        out[ln] = float(base[ln] * np.exp(x))
    last4 = h.tail(4)
    on_share = float((last4["other_net"] / last4["revenue"]).mean())
    out["other_net"] = on_share * out["revenue"]
    out["sum_lines"] = sum(out[ln] for ln in LINES)
    out["adj_ebitda_musd"] = out["revenue"] - out["sum_lines"] + out["other_net"]
    out["adj_ebitda_margin_pct"] = 100.0 * out["adj_ebitda_musd"] / out["revenue"]
    out["total_cash_costs_musd"] = out["revenue"] - out["adj_ebitda_musd"]
    return out


def run_vintage(vd, spec: str, replay: str, full_params: dict, live: bool, scenario: str = "base",
                h_max: int | None = None) -> tuple[list, dict]:
    """Forecasts at one vintage for one spec and replay. Returns (rows, params)."""
    h = hist_as_of(vd)
    params = full_params if replay == "full_sample" else fit_all(h, spec)
    q0 = Q.quarter_of_date(pd.to_datetime(vd).date())
    hmax = h_max if h_max is not None else (H_LIVE if live else H_BACK)
    prev, rows = {}, []
    family = ALL_SPECS[spec][0]
    for hz in range(0, hmax + 1):
        q = Q.shift(q0, hz)
        if live:
            drv = live_drivers(q, scenario)
            if drv is None:
                continue
            mix = live_mix_d4(q, h) if family == "c" else None
        elif family == "e":
            drv = oracle_drivers(q)
            if drv is None:
                drv = pit_drivers(vd, q, h, prev)
                drv["leg"] = drv["leg"] + "_no_actual"
            mix = None
            if family == "c":
                pass
        else:
            drv = pit_drivers(vd, q, h, prev)
            mix = None
            if family == "c":
                last = h.index.max(); l4 = Q.shift(last, -4)
                mix = float(h.loc[last, "exna_share"] - h.loc[l4, "exna_share"]) \
                    if (l4 in h.index and pd.notna(h.loc[last, "exna_share"]) and pd.notna(h.loc[l4, "exna_share"])) else 0.0
        f = forecast_quarter(params, spec, h, q, drv, prev, mix)
        if f is None:
            continue
        prev[q] = f
        f.update({"vintage_date": pd.to_datetime(vd).date(), "horizon_q": hz, "spec_id": spec, "prior_basis": replay,
                  "rev_leg": drv["leg"], "scenario": scenario if live else "backtest", "n_train": int(len(h)),
                  "knowable_from": h["print_date"].max(),
                  "flags": ";".join(sorted({x for ln in LINES for x in params[ln]["flags"].split(";") if x}))})
        rows.append(f)
    return rows, params


# ----------------------------------------------------------------------------- quantiles
def attach_quantiles(long: pd.DataFrame) -> pd.DataFrame:
    """Walk-forward residual sd per (spec, target, horizon, replay-own errors); PIT restricted to quarters printed
    before the vintage (last 12); full_sample uses all realised errors; LIVE h>=3 borrow the h=2 pool."""
    long = long.copy()
    for c in QCOLS + ["sd", "sigma_n"]:
        long[c] = np.nan
    long["sigma_kind"] = ""
    real = long[long["actual"].notna()]
    pools = {}
    for (sp, tg, hz, pb), g in real.groupby(["spec_id", "target", "horizon_q", "prior_basis"]):
        rel = tg in RELATIVE_TARGETS
        g = g[(g["point"] > 0) & (g["actual"] > 0)] if rel else g
        errs = ((g["point"] / g["actual"] - 1.0) if rel else (g["point"] - g["actual"])).to_numpy(dtype=float)
        pools[(sp, tg, int(hz), pb)] = (errs, g["target_print_date"].to_numpy(), g["quarter"].to_numpy())
    for i, r in long.iterrows():
        rel = r["target"] in RELATIVE_TARGETS
        hz = int(r["horizon_q"])
        key = (r["spec_id"], r["target"], hz, r["prior_basis"])
        borrowed = ""
        errs, pdates, _ = pools.get(key, (np.array([]), np.array([]), np.array([])))
        if len(errs) < MIN_RESID:
            for hb in range(hz - 1, -1, -1):
                e2, p2, _ = pools.get((r["spec_id"], r["target"], hb, r["prior_basis"]), (np.array([]), np.array([]), None))
                if len(e2) >= MIN_RESID:
                    errs, pdates, borrowed = e2, p2, f"_borrowed_h{hb}"
                    break
        if r["prior_basis"] == "full_sample":
            e = errs
        else:
            m = np.array([pd.notna(d) and d <= r["vintage_date"] for d in pdates], dtype=bool)
            e = errs[m][-RESID_MAX_N:]
        sd = float(np.std(e, ddof=1)) if len(e) >= MIN_RESID else np.nan
        kind = ("relative" if rel else "additive") + borrowed
        if not np.isfinite(sd) or sd <= 0:
            sd = FALLBACK_REL if rel else FALLBACK_PP
            kind += "_fallback"
        pt = float(r["point"])
        for c in QCOLS:
            long.at[i, c] = pt * (1.0 + ZQ[c] * sd) if rel else pt + ZQ[c] * sd
        long.at[i, "sd"] = abs(pt) * sd if rel else sd
        long.at[i, "sigma_n"] = int(len(e))
        long.at[i, "sigma_kind"] = kind
    qm = long[QCOLS].to_numpy(dtype=float)
    qm.sort(axis=1)
    long[QCOLS] = qm
    return long


# ----------------------------------------------------------------------------- main build
def main() -> int:
    t0 = _dt.datetime.now()
    print(f"M1 driver lines: start {t0:%Y-%m-%d %H:%M:%S}; WS06 wide file = {WS06_WIDE.name}")
    full_h = hist_as_of(TODAY)
    vintages = [d for d in GUIDE_DATES_ALL if d >= _dt.date(2022, 2, 15)]
    live_vintages = [GUIDE_DATE_LIVE, TODAY]

    wide_rows, param_rows = [], []
    full_params_by_spec = {}
    for spec in ALL_SPECS:
        full_params_by_spec[spec] = fit_all(full_h, spec, anchor="2026Q2")
        for ln, p in full_params_by_spec[spec].items():
            param_rows.append({"vintage_date": "full_sample", **p})
        for vd in vintages:
            for replay in ("PIT", "full_sample"):
                rows, params = run_vintage(vd, spec, replay, full_params_by_spec[spec], live=False)
                wide_rows += rows
                if replay == "PIT":
                    for ln, p in params.items():
                        param_rows.append({"vintage_date": vd, **p})
        # LIVE: base registered; bear/bull to CSV; FY28 needs h up to 9 (base only, WS06 has 2028 base rows)
        for vd in live_vintages:
            for scen in ("base", "bear", "bull"):
                for replay in ("PIT", "full_sample"):
                    rows, _ = run_vintage(vd, spec, replay, full_params_by_spec[spec], live=True, scenario=scen,
                                          h_max=H_ANNUAL if scen == "base" else H_LIVE)
                    wide_rows += rows
    wide = pd.DataFrame(wide_rows)
    wide["vintage_date"] = pd.to_datetime(wide["vintage_date"]).dt.date
    wide.to_csv(OUT / "M1_driver_lines_forecasts_wide.csv", index=False)
    pr = pd.DataFrame(param_rows)
    pr.to_csv(OUT / "M1_driver_lines_params_by_vintage.csv", index=False)
    print(f"  forecasts: {len(wide)} quarter-rows; params: {len(pr)} rows")

    # ---- long registry frame (backtest + LIVE base) --------------------------------------
    pd_map = {Q.canon(r.quarter): r.print_date for r in load_targets().itertuples() if pd.notna(r.print_date)}
    act = PANEL[PANEL["has_actual"].astype(bool)]
    target_cols = {**{v: k for k, v in LINE_TARGET.items()}, **{t: t for t in MARGIN_TARGETS}}
    long_rows = []
    bt = wide[(wide["scenario"] == "backtest") | (wide["scenario"] == "base")]
    for r in bt.itertuples():
        wins = windows_for(r.vintage_date, r.quarter)
        if not wins:
            continue
        for tg, col in target_cols.items():
            pt = getattr(r, col)
            obj = "lines_v2" if tg in LINE_TARGET.values() else "margin_v2"
            actual = float(act.loc[r.quarter, tg]) if r.quarter in act.index else np.nan
            for w in wins:
                if w == "LIVE" and r.scenario != "base":
                    continue
                if w != "LIVE" and r.scenario != "backtest":
                    continue
                long_rows.append(dict(method=METHOD, object=obj, target=tg, quarter=r.quarter,
                                      vintage_date=r.vintage_date, horizon_q=int(r.horizon_q), point=float(pt),
                                      window=w, prior_basis=r.prior_basis, spec_id=r.spec_id,
                                      n_params=N_PARAMS[ALL_SPECS[r.spec_id][0]], n_train=int(r.n_train),
                                      knowable_from=r.knowable_from, actual=actual,
                                      target_print_date=pd_map.get(r.quarter),
                                      notes=f"rev_leg={r.rev_leg};scenario={r.scenario};{r.flags}"))
    long = pd.DataFrame(long_rows)
    long = long[long["spec_id"].isin(SPECS)]
    # quantile pools use the W1-vintage rows (all vintages from 2022-02-15 give the pool via `wide`, but the
    # registry only carries W1/W2/LIVE rows; build the pool from every backtest vintage for depth)
    pool_rows = []
    for r in wide[(wide["scenario"] == "backtest") & (wide["spec_id"].isin(SPECS))].itertuples():
        for tg, col in target_cols.items():
            actual = float(act.loc[r.quarter, tg]) if r.quarter in act.index else np.nan
            pool_rows.append(dict(spec_id=r.spec_id, target=tg, horizon_q=int(r.horizon_q), prior_basis=r.prior_basis,
                                  quarter=r.quarter, vintage_date=r.vintage_date, point=float(getattr(r, col)),
                                  actual=actual, target_print_date=pd_map.get(r.quarter)))
    pool = pd.DataFrame(pool_rows)
    # attach quantiles using the deep pool: temporarily concat, compute, then keep registry rows
    long["_reg"] = True
    pool["_reg"] = False
    both = pd.concat([long, pool], ignore_index=True, sort=False)
    both = attach_quantiles(both)
    long = both[both["_reg"] == True].drop(columns=["_reg"]).copy()   # noqa: E712
    long["q50"] = long["point"]
    long.to_csv(OUT / "M1_driver_lines_registry_long.csv", index=False)

    reg_cols = ["method", "object", "target", "quarter", "vintage_date", "horizon_q", "point", "q50", "window",
                "prior_basis", "n_params", "n_train", "q05", "q10", "q25", "q75", "q90", "q95", "sd", "knowable_from",
                "spec_id", "notes"]
    for obj in ("margin_v2", "lines_v2"):
        d = long[long["object"] == obj][reg_cols].reset_index(drop=True)
        register(d, quiet=False)

    # ---- in-script grid: margin MAE by spec (incl. grid-only variants), both windows, both weightings ----
    grid = []
    sn = {}
    for q in act.index:
        lag = Q.shift(q, -4)
        if lag in act.index:
            sn[q] = float(act.loc[lag, "adj_ebitda_margin_pct"])
    bg = pd.read_csv(HARNESS.parent.parent.parent.parent / "data" / "processed" / "margin_build" / "10_harness_margin"
                     / "baseline_grid_all_vintages.csv")
    bg["vintage_date"] = pd.to_datetime(bg["vintage_date"]).dt.date
    street = bg[(bg["object"] == "street") & (bg["target"] == "adj_ebitda_margin_pct") & (bg["prior_basis"] == "PIT")]
    street = street.set_index(["vintage_date", "quarter"])["point"].to_dict()
    for spec in ALL_SPECS:
        for replay in ("PIT", "full_sample"):
            sub = wide[(wide["spec_id"] == spec) & (wide["prior_basis"] == replay) & (wide["scenario"] == "backtest")]
            for win in ("W1", "W2"):
                for hz in (0, 1, 2):
                    rows = []
                    for r in sub[sub["horizon_q"] == hz].itertuples():
                        if win not in windows_for(r.vintage_date, r.quarter) or r.quarter not in act.index:
                            continue
                        a = float(act.loc[r.quarter, "adj_ebitda_margin_pct"])
                        rows.append((r.quarter, r.adj_ebitda_margin_pct - a, sn.get(r.quarter, np.nan) - a,
                                     street.get((r.vintage_date, r.quarter), np.nan) - a))
                    if not rows:
                        continue
                    qq = [x[0] for x in rows]
                    e = np.array([x[1] for x in rows]); es = np.array([x[2] for x in rows]); est = np.array([x[3] for x in rows])
                    w = recency_weights(qq, "2026Q2")
                    ok_st = np.isfinite(est)
                    grid.append(dict(spec_id=spec, prior_basis=replay, window=win, horizon_q=hz, n=len(rows),
                                     mae=np.mean(np.abs(e)), rw_mae=float(np.sum(w * np.abs(e))),
                                     bias=np.mean(e), rw_bias=float(np.sum(w * e)),
                                     mae_sn=np.mean(np.abs(es)), rw_mae_sn=float(np.sum(w * np.abs(es))),
                                     ratio_sn=np.mean(np.abs(e)) / np.mean(np.abs(es)),
                                     rw_ratio_sn=float(np.sum(w * np.abs(e)) / np.sum(w * np.abs(es))),
                                     mae_street=np.mean(np.abs(est[ok_st])) if ok_st.any() else np.nan,
                                     ratio_street=(np.mean(np.abs(e[ok_st])) / np.mean(np.abs(est[ok_st]))) if ok_st.any() else np.nan,
                                     rw_ratio_street=(float(np.sum(w[ok_st] * np.abs(e[ok_st])) / np.sum(w[ok_st] * np.abs(est[ok_st])))) if ok_st.any() else np.nan))
    grid = pd.DataFrame(grid)
    grid.to_csv(OUT / "M1_driver_lines_grid_margin.csv", index=False)

    # ---- per-line MAE (in-script), PIT, vs seasonal naive and pct_rev_last4 with the same PIT revenue leg ----
    pl = []
    for spec in SPECS:
        sub = wide[(wide["spec_id"] == spec) & (wide["prior_basis"] == "PIT") & (wide["scenario"] == "backtest")]
        for ln in LINES + ["other_net"]:
            for win in ("W1", "W2"):
                for hz in (0, 1):
                    e, es, ep, qq = [], [], [], []
                    for r in sub[sub["horizon_q"] == hz].itertuples():
                        if win not in windows_for(r.vintage_date, r.quarter) or r.quarter not in act.index:
                            continue
                        a = float(act.loc[r.quarter, ln]); lag = Q.shift(r.quarter, -4)
                        h = hist_as_of(r.vintage_date)
                        share = float((h.tail(4)[ln] / h.tail(4)["revenue"]).mean())
                        e.append(getattr(r, ln) / a - 1.0); es.append(act.loc[lag, ln] / a - 1.0)
                        ep.append(share * r.revenue / a - 1.0); qq.append(r.quarter)
                    if not e:
                        continue
                    e, es, ep = np.abs(np.array(e)), np.abs(np.array(es)), np.abs(np.array(ep))
                    w = recency_weights(qq, "2026Q2")
                    pl.append(dict(spec_id=spec, line=ln, window=win, horizon_q=hz, n=len(e), mape=e.mean(),
                                   rw_mape=float(np.sum(w * e)), ratio_sn=e.mean() / es.mean(),
                                   rw_ratio_sn=float(np.sum(w * e) / np.sum(w * es)), ratio_pct_rev=e.mean() / ep.mean(),
                                   rw_ratio_pct_rev=float(np.sum(w * e) / np.sum(w * ep))))
    pl = pd.DataFrame(pl)
    pl.to_csv(OUT / "M1_driver_lines_per_line_mape.csv", index=False)

    # ---- leave-one-year-out stability of b_L (spec b, full sample) --------------------------------
    loyo = []
    for spec in ("b_elastic_rw", "b_elastic_eq"):
        base = full_params_by_spec[spec]
        for yr in ["none", 2022, 2023, 2024, 2025, 2026]:
            h = full_h if yr == "none" else full_h[~full_h.index.str.startswith(str(yr))]
            pp = fit_all(h, spec, anchor="2026Q2")
            for ln in ("cor", "ops", "sm"):
                loyo.append(dict(spec_id=spec, drop_year=yr, line=ln, b=pp[ln]["b"], g=pp[ln]["g"], n_obs=pp[ln]["n_obs"],
                                 b_full=base[ln]["b"]))
    loyo = pd.DataFrame(loyo)
    loyo.to_csv(OUT / "M1_driver_lines_loyo_elasticities.csv", index=False)

    # ---- LIVE tables -----------------------------------------------------------------------
    live = wide[(wide["scenario"] != "backtest") & (wide["vintage_date"] == TODAY)].copy()
    cons = pd.read_csv(WS06_CONS27)
    cons["quarter"] = cons["quarter"].map(Q.canon)
    cons_q = cons.set_index("quarter")[["revenue_mean_musd", "ebitda_mean_musd"]]
    p31 = pd.read_csv(WS31B_PROFILE)
    p31 = p31[(p31["line"] == "adj_ebitda") & (p31["scenario"] == "base")]
    p31q = {(Q.canon(r.period) if not r.period.startswith("FY") else r.period, r.profile): (r.value_musd, r.pct_of_revenue)
            for r in p31.itertuples()}
    ws30 = pd.read_csv(WS30_FY).set_index("scenario")
    live_q = live[live["quarter"] <= "2027Q4"].copy()
    live_q["cons_ebitda_musd"] = live_q["quarter"].map(cons_q["ebitda_mean_musd"])
    live_q["cons_revenue_musd"] = live_q["quarter"].map(cons_q["revenue_mean_musd"])
    live_q["cons_margin_pct"] = 100 * live_q["cons_ebitda_musd"] / live_q["cons_revenue_musd"]
    for prof in ("historical", "management", "base"):
        live_q[f"ws31b_{prof}_margin_pct"] = live_q["quarter"].map(lambda q: p31q.get((q, prof), (np.nan, np.nan))[1])
    live_q["ws30_margin_pct"] = np.nan
    for scen in ("bear", "base", "bull"):
        m = live_q["scenario"] == scen
        live_q.loc[m & (live_q["quarter"] == "2026Q3"), "ws30_margin_pct"] = float(ws30.loc[scen, "q3_margin_pct"])
        live_q.loc[m & (live_q["quarter"] == "2026Q4"), "ws30_margin_pct"] = float(ws30.loc[scen, "q4_margin_pct"])
    live_q["mgmt_3q26_ceiling_margin_pct"] = np.where(live_q["quarter"] == "2026Q3", float(act.loc["2025Q3", "adj_ebitda_margin_pct"]), np.nan)
    keep = ["quarter", "scenario", "spec_id", "prior_basis", "horizon_q", "revenue", "nights", "gbv"] + LINES + \
           ["other_net", "sum_lines", "adj_ebitda_musd", "adj_ebitda_margin_pct", "total_cash_costs_musd", "rev_leg",
            "cons_revenue_musd", "cons_ebitda_musd", "cons_margin_pct", "ws31b_historical_margin_pct",
            "ws31b_management_margin_pct", "ws31b_base_margin_pct", "ws30_margin_pct", "mgmt_3q26_ceiling_margin_pct"]
    live_q[keep].to_csv(OUT / "M1_driver_lines_live_quarterly.csv", index=False)

    # annual: FY26 = 1H26 actual + 3Q/4Q forecast; FY27, FY28 sums (FY28 base only)
    cur = pd.read_csv(WS03_CURRENT)
    cons_fy = {r.period: (r.revenue_mean, r.ebitda_mean) for r in cur[cur["vendor"] == "LSEG"].itertuples()}
    ann = []
    h1 = act.loc[["2026Q1", "2026Q2"]]
    for (spec, scen, replay), g in live.groupby(["spec_id", "scenario", "prior_basis"]):
        g = g.set_index("quarter")
        for fy, qs in (("FY26", ["2026Q3", "2026Q4"]), ("FY27", [f"2027Q{i}" for i in range(1, 5)]),
                       ("FY28", [f"2028Q{i}" for i in range(1, 5)])):
            if not all(q in g.index for q in qs):
                continue
            rec = {"fy": fy, "scenario": scen, "spec_id": spec, "prior_basis": replay}
            for c in ["revenue", "nights", "gbv"] + LINES + ["other_net", "adj_ebitda_musd"]:
                v = g.loc[qs, c].sum()
                if fy == "FY26":
                    v += h1[c].sum() if c in h1.columns else 0.0
                rec[c] = float(v)
            rec["adj_ebitda_margin_pct"] = 100 * rec["adj_ebitda_musd"] / rec["revenue"]
            for ln in LINES:
                rec[f"{ln}_pct_rev"] = 100 * rec[ln] / rec["revenue"]
            cr = cons_fy.get(fy)
            rec["cons_revenue_musd"] = cr[0] if cr else np.nan
            rec["cons_ebitda_musd"] = cr[1] if cr else np.nan
            rec["cons_margin_pct"] = 100 * cr[1] / cr[0] if cr else np.nan
            fyl = f"FY20{fy[2:]}E"
            for prof in ("historical", "management", "base"):
                rec[f"ws31b_{prof}_margin_pct"] = p31q.get((fyl, prof), (np.nan, np.nan))[1]
            rec["ws30_margin_pct"] = float(ws30.loc[scen, "fy26_margin_pct"]) if fy == "FY26" else \
                (float(ws30.loc[scen, "fy27_margin_pct"]) if fy == "FY27" else np.nan)
            rec["mgmt_fy26_floor_pct"] = 35.5 if fy == "FY26" else np.nan
            ann.append(rec)
    ann = pd.DataFrame(ann)
    fy25 = act.loc[[f"2025Q{i}" for i in range(1, 5)]]
    fy25_margin = 100 * fy25["adj_ebitda_musd"].sum() / fy25["revenue"].sum()
    ann["fy25_actual_margin_pct"] = fy25_margin
    piv = ann.pivot_table(index=["scenario", "spec_id", "prior_basis"], columns="fy", values="adj_ebitda_margin_pct")
    inc = {}
    for k, r in piv.iterrows():
        inc[k] = (r.get("FY27", np.nan) - r.get("FY26", np.nan), r.get("FY28", np.nan) - r.get("FY27", np.nan))
    ann["margin_chg_fy27_vs_fy26_pp"] = [inc[(r.scenario, r.spec_id, r.prior_basis)][0] if r.fy == "FY27" else np.nan for r in ann.itertuples()]
    ann["margin_chg_fy28_vs_fy27_pp"] = [inc[(r.scenario, r.spec_id, r.prior_basis)][1] if r.fy == "FY28" else np.nan for r in ann.itertuples()]
    ann["margin_chg_fy26_vs_fy25_pp"] = np.where(ann["fy"] == "FY26", ann["adj_ebitda_margin_pct"] - fy25_margin, np.nan)
    ann.to_csv(OUT / "M1_driver_lines_annual_forecasts.csv", index=False)

    # ---- figures ---------------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sub = wide[(wide["spec_id"] == MAIN_SPEC) & (wide["prior_basis"] == "PIT") & (wide["scenario"] == "backtest")
                   & (wide["horizon_q"] == 0)]
        sub = sub[sub["vintage_date"].isin(GUIDE_DATES_W1)].sort_values("quarter")
        fig, ax = plt.subplots(figsize=(10, 4.5))
        qs = list(sub["quarter"])
        ax.plot(qs, [act.loc[q, "adj_ebitda_margin_pct"] for q in qs], "k-o", label="actual")
        ax.plot(qs, sub["adj_ebitda_margin_pct"], "-s", color="#1f77b4", label=f"M1 {MAIN_SPEC} PIT h=0")
        ax.plot(qs, [sn.get(q, np.nan) for q in qs], "--", color="#7f7f7f", label="seasonal naive y[q-4]")
        ax.plot(qs, [street.get((v, q), np.nan) for v, q in zip(sub["vintage_date"], qs)], ":", color="#d62728", label="Street (LSEG pre-guide)")
        ax.set_ylabel("adj EBITDA margin, %"); ax.set_title("M1 driver lines: h=0 backtest at the 14 W1 guide dates (PIT)")
        ax.legend(); ax.grid(alpha=.3); plt.xticks(rotation=45); fig.tight_layout()
        fig.savefig(FIG / "M1_driver_lines_backtest_margin.png", dpi=130); plt.close(fig)

        fig, ax = plt.subplots(figsize=(10, 4.5))
        lq = live_q[(live_q["spec_id"] == MAIN_SPEC) & (live_q["prior_basis"] == "PIT")]
        for scen, col in (("bear", "#d62728"), ("base", "#1f77b4"), ("bull", "#2ca02c")):
            s = lq[lq["scenario"] == scen].sort_values("quarter")
            ax.plot(s["quarter"], s["adj_ebitda_margin_pct"], "-o", color=col, label=f"M1 {scen}")
        s = lq[lq["scenario"] == "base"].sort_values("quarter")
        ax.plot(s["quarter"], s["cons_margin_pct"], "k--", label="LSEG consensus (11-13 Sep)")
        ax.plot(s["quarter"], s["ws31b_base_margin_pct"], ":", color="#9467bd", label="WS31b base profile")
        ax.set_ylabel("adj EBITDA margin, %"); ax.set_title("M1 driver lines: LIVE 3Q26-4Q27 on the WS06 revenue path")
        ax.legend(); ax.grid(alpha=.3); fig.tight_layout()
        fig.savefig(FIG / "M1_driver_lines_live_margin.png", dpi=130); plt.close(fig)
    except Exception as e:  # pragma: no cover
        print(f"  figure skipped: {e}")

    # ---- scoreboard -----------------------------------------------------------------------
    print("  running score.py ...")
    rc = subprocess.run([sys.executable, str(HARNESS / "score.py")], cwd=str(REPO), capture_output=True, text=True)
    print(rc.stdout[-2000:])
    if rc.returncode != 0:
        print(rc.stderr[-3000:])
        return rc.returncode
    sb = pd.read_csv(MB / "10_harness_margin" / "scoreboard_margin.csv")
    mine = sb[sb["method"] == METHOD]
    mine.to_csv(OUT / "M1_driver_lines_scoreboard_rows.csv", index=False)
    json.dump({"built": f"{t0:%Y-%m-%d %H:%M:%S}", "ws06_wide": WS06_WIDE.name, "n_forecast_rows": int(len(wide)),
               "n_registry_rows": int(len(long)), "specs": list(SPECS), "main_spec": MAIN_SPEC},
              open(OUT / "M1_driver_lines_build.json", "w"), indent=2)
    print(f"done in {(_dt.datetime.now() - t0).total_seconds():.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
