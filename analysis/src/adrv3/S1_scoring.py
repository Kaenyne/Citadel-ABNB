"""
WS-S (ADR v3, 11 Sep 2026): the shared scoring harness.

Importable, no side effects on import. Other workstreams (K, L, M, P) call `score()` with an
ex-FX ADR y/y path indexed by quarter ('1Q24' ... '2Q26') and get one row per
(target, window, fx_estimator). `preregistered_pass()` applies the BRIEF's v3 criterion.

Two pre-registered targets (docs/adrv3/BRIEF.md, section "Pre-registered pass criteria"):

  t1_exfx_integer_fair   Disclosed ex-FX ADR y/y is a whole number of points (1, 2, 3, 4). The
                         model's ex-FX output is rounded to the nearest whole point before scoring
                         (round half away from zero: 2.5 -> 3, -0.5 -> -1). Naive = last disclosed
                         ex-FX (already an integer). Prior year = disclosed ex-FX four quarters
                         earlier (integer). AR(1) = expanding fit on the disclosed integer series
                         strictly before t, prediction rounded the same way as the model so every
                         continuous forecast faces the same rounding. J3 scored unrounded model
                         output against the integer series, which charges the model rounding noise
                         the naive never pays (J note section 4).

  t2_reported_usd_yoy    Reported dollar ADR y/y, unrounded: adr_usd[t] / adr_usd[t-4] - 1 from
                         data/processed/q3nowcast/H/adr_history_components.csv (adr_usd carries two
                         decimals). Model = ex-FX model + FX estimator for quarter t; naive = last
                         disclosed ex-FX + the same FX estimator for quarter t. The FX estimator per
                         historical quarter is est_from_eur or est_from_regional_baskets from
                         data/processed/overnight2/B/B_adr_fx_estimator_backtest.csv, or their
                         midpoint (all three reported). The disclosed fx_effect_pp is never used as
                         the model's FX: it is only known at the print. Prior year = reported y/y
                         four quarters earlier. AR(1) = expanding fit on the reported series before t.

A third mode, `v2_original_exfx`, reproduces J3's scoring (unrounded model against the integer
disclosed ex-FX, naive = last disclosed) and exists only so this harness can be verified against the
v2 record (`reproduce_j3()`); it is not a v3 target.

Windows: 1Q24-2Q26 (n 10) and 2Q24-2Q26 (n 9). Per model, target, window and FX estimator: n,
RMSE, bias, MAE, ratio vs naive / prior year / AR(1), sign accuracy of the predicted change from
naive (over quarters where the actual change from naive is non-zero), jackknife drop-one min / max
of the ratio vs naive and the count of drop-one samples below 1, and the knowable-before-print flag
the caller supplies.

Benchmarks: naive, prior year, AR(1) expanding on the target series (fit strictly before t, at least
four training quarters, np.polyfit as J3). The AR(1) training history starts at 1Q23 for both
targets; for t2 the 2023 reported y/y values come from H's adr_yoy_reported_pp column (the same
quantity, on H's 2022 ADR base) because adr_usd is only carried from 1Q23.

v2 model paths: `v2_model_paths()` rebuilds the J3 walk-forward block (residual rules last_q,
persistence, trailing_4q, trailing_8q, ar1_residual, blend; measured mix and trailing-4q mix) from
the same inputs, so every J3 model can be rescored on the new targets. `reproduce_j3()` checks
the rebuild against data/processed/adrq3/J/card_v2_backtest.csv to 0.001.

Run `py -3.13 analysis/src/adrv3/S1_scoring.py` for a demo (reproduction check and the last_q rule
on both targets). Nothing is written by this module.
"""
from __future__ import annotations

import os
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
QORDER = [f"{q}Q{str(y)[-2:]}" for y in range(2017, 2030) for q in range(1, 5)]
QI = {q: i for i, q in enumerate(QORDER)}

TARGETS = ("t1_exfx_integer_fair", "t2_reported_usd_yoy")
V2_ORIGINAL = "v2_original_exfx"
FX_ESTIMATORS = ("eur", "baskets", "midpoint")
WINDOWS = {"1Q24-2Q26": ("1Q24", "2Q26"), "2Q24-2Q26": ("2Q24", "2Q26")}
FIRST_SCORED = "1Q24"
MIN_AR1_TRAIN = 4          # training quarters strictly before t (J3 convention: 3 lag pairs at 1Q24)
RULES = ["last_q", "persistence", "trailing_4q", "trailing_8q", "ar1_residual", "blend"]
MIX_VARIANTS = ["measured", "trailing4q"]
V2_MODELS = [f"v2_{mv}_{r}" for mv in MIX_VARIANTS for r in RULES]
BENCHMARKS = ["naive_last_q", "prior_year_q", "ar1_expanding"]
V3_RULE_MODEL = "v2_measured_last_q"      # the pre-registered v3 rule (BRIEF, post-hoc promotion)
V2_RULE_MODEL = "v2_measured_persistence"  # J3's pre-registered v2 rule, for comparison
KNOWABLE_V2 = "no: the residual is only knowable after the print; the rule uses prior residuals only"
KNOWABLE_BENCH = "yes"
FX_LABEL = {"eur": "est_from_eur", "baskets": "est_from_regional_baskets", "midpoint": "mean of eur and baskets"}

_CACHE: dict = {}


# ----------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------
def round_half_away(x):
    """Round to the nearest whole point, halves away from zero (2.5 -> 3, -2.5 -> -3). NaN safe."""
    a = np.asarray(x, dtype=float)
    out = np.sign(a) * np.floor(np.abs(a) + 0.5)
    return out if a.ndim else float(out)


def b_to_h_quarter(q: str) -> str:
    """'2024Q1' (WS-B label) -> '1Q24' (H label)."""
    q = str(q).strip()
    if len(q) == 6 and q[4] == "Q":
        return f"{q[5]}Q{q[2:4]}"
    return q


def quarters_between(start: str, end: str) -> list[str]:
    return [q for q in QORDER if QI[start] <= QI[q] <= QI[end]]


def _prior(quarters: Iterable[str], t: str) -> list[str]:
    return [q for q in quarters if QI[q] < QI[t]]


def _rmse(e: pd.Series) -> float:
    e = e.dropna()
    return float(np.sqrt((e ** 2).mean())) if len(e) else np.nan


# ----------------------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------------------
def load_inputs(root: str | None = None) -> dict:
    """H components, disclosed series, the WS-B FX estimators (relabelled 1Q24 style), and the
    target series. Cached per root."""
    root = root or ROOT
    if root in _CACHE:
        return _CACHE[root]
    hdir = os.path.join(root, "data", "processed", "q3nowcast", "H")
    H = pd.read_csv(os.path.join(hdir, "adr_history_components.csv")).set_index("quarter")
    H = H.loc[sorted(H.index, key=lambda q: QI[q])]
    exfx = H["adr_exfx_yoy_pp"].astype(float)                 # disclosed, whole points
    fx_disc = H["fx_effect_pp"].astype(float)                 # disclosed, at the print only
    residual = H["residual_pricing_pp"].astype(float)
    adr = H["adr_usd"].astype(float)
    # target 2: reported dollar ADR y/y from adr_usd; H's own column where the prior-year ADR is
    # not in the file (2023 rows, H's 2022 base). Where both exist they agree to 1e-9.
    rep = pd.Series(index=H.index, dtype=float)
    for q in H.index:
        p = QORDER[QI[q] - 4]
        if p in adr.index:
            rep[q] = 100.0 * (adr[q] / adr[p] - 1.0)
        else:
            rep[q] = float(H.loc[q, "adr_yoy_reported_pp"])
    chk = (rep - H["adr_yoy_reported_pp"].astype(float)).abs().max()
    if chk > 1e-6:
        raise ValueError(f"adr_usd y/y disagrees with H adr_yoy_reported_pp by {chk:.4f}")
    B = pd.read_csv(os.path.join(root, "data", "processed", "overnight2", "B", "B_adr_fx_estimator_backtest.csv"))
    B["quarter"] = B["quarter"].map(b_to_h_quarter)
    B = B.set_index("quarter")
    fx_est = pd.DataFrame({"eur": B["est_from_eur"].astype(float),
                           "baskets": B["est_from_regional_baskets"].astype(float)})
    fx_est["midpoint"] = 0.5 * (fx_est["eur"] + fx_est["baskets"])
    fx_est["disclosed_B"] = B["adr_fx_disclosed_pp"].astype(float)
    out = {"root": root, "H": H, "exfx": exfx, "fx_disclosed": fx_disc, "residual": residual,
           "adr_usd": adr, "reported_yoy": rep, "fx_est": fx_est,
           "identity_gap": H["identity_check_pp"].astype(float)}
    _CACHE[root] = out
    return out


# ----------------------------------------------------------------------------------
# target frames: actual, naive, prior year, AR(1) per quarter
# ----------------------------------------------------------------------------------
def _ar1_expanding(series: pd.Series, t: str, min_train: int = MIN_AR1_TRAIN) -> float:
    prior = series[_prior(series.index, t)].dropna()
    if len(prior) < min_train:
        return np.nan
    v = prior.values
    b1, b0 = np.polyfit(v[:-1], v[1:], 1)
    return float(b0 + b1 * v[-1])


def target_frame(target: str, fx_estimator: str = "midpoint", root: str | None = None,
                 first: str = FIRST_SCORED, last: str = "2Q26") -> pd.DataFrame:
    """Per quarter: actual, naive, prior_year, ar1 (benchmark predictions, already in scored
    units), plus naive_exfx and the FX estimate used. Rows first..last."""
    d = load_inputs(root)
    exfx, rep, fx_est = d["exfx"], d["reported_yoy"], d["fx_est"]
    rows = []
    for t in quarters_between(first, last):
        if t not in exfx.index:
            continue
        prior = _prior(exfx.index, t)
        last_exfx = exfx[prior[-1]] if prior else np.nan
        py_q = QORDER[QI[t] - 4]
        r = {"quarter": t, "naive_exfx_pp": last_exfx}
        if target in ("t1_exfx_integer_fair", V2_ORIGINAL):
            r["fx_estimator"] = "none"
            r["fx_est_pp"] = np.nan
            r["actual"] = float(exfx[t])
            r["naive"] = float(last_exfx)
            r["prior_year"] = float(exfx.get(py_q, np.nan))
            a = _ar1_expanding(exfx, t)
            r["ar1"] = round_half_away(a) if (target == "t1_exfx_integer_fair" and np.isfinite(a)) else a
        elif target == "t2_reported_usd_yoy":
            fx = float(fx_est.loc[t, fx_estimator]) if t in fx_est.index else np.nan
            r["fx_estimator"] = fx_estimator
            r["fx_est_pp"] = fx
            r["actual"] = float(rep[t])
            r["naive"] = float(last_exfx + fx)
            r["prior_year"] = float(rep.get(py_q, np.nan))
            r["ar1"] = _ar1_expanding(rep, t)
        else:
            raise ValueError(f"unknown target {target}")
        rows.append(r)
    return pd.DataFrame(rows).set_index("quarter")


def scored_prediction(ex_fx_model: pd.Series, target: str, tf: pd.DataFrame) -> pd.Series:
    """Map an ex-FX model path onto the target's units: rounded for t1, plus the FX estimate for t2,
    unchanged for the v2 original mode."""
    m = pd.Series(ex_fx_model, dtype=float).reindex(tf.index)
    if target == "t1_exfx_integer_fair":
        return pd.Series(round_half_away(m.values), index=tf.index)
    if target == "t2_reported_usd_yoy":
        return m + tf["fx_est_pp"]
    return m


# ----------------------------------------------------------------------------------
# scoring
# ----------------------------------------------------------------------------------
def _score_block(pred: pd.Series, tf: pd.DataFrame, align_naive_to_model: bool = True) -> dict:
    """RMSE, bias, MAE, ratios, sign accuracy and jackknife for one prediction series against one
    target frame (already windowed)."""
    act, naive, prior, ar1 = tf["actual"], tf["naive"], tf["prior_year"], tf["ar1"]
    e = (pred - act)
    mask = e.notna()
    e_m = e[mask]
    nmask = mask if align_naive_to_model else act.notna()
    r_m = _rmse(e_m)
    r_n = _rmse((naive - act)[nmask])
    r_p = _rmse((prior - act)[nmask])
    r_a = _rmse((ar1 - act)[nmask])
    d_act = (act - naive)[mask]
    d_pred = (pred - naive)[mask]
    nz = d_act != 0
    sign_acc = float((np.sign(d_pred[nz]) == np.sign(d_act[nz])).mean()) if nz.any() else np.nan
    ratios = []
    for drop in tf.index:
        keep = [q for q in tf.index if q != drop]
        km = mask[keep] if align_naive_to_model else act.notna()[keep]
        e_mm = e[keep].dropna()
        e_nn = (naive - act)[keep][km].dropna()
        if len(e_mm) and len(e_nn):
            ratios.append(_rmse(e_mm) / _rmse(e_nn))
    return {"n": int(mask.sum()), "rmse_pp": r_m, "bias_pp": float(e_m.mean()) if len(e_m) else np.nan,
            "mae_pp": float(e_m.abs().mean()) if len(e_m) else np.nan,
            "rmse_naive_pp": r_n, "rmse_prior_year_pp": r_p, "rmse_ar1_pp": r_a,
            "ratio_vs_naive": r_m / r_n if r_n else np.nan,
            "ratio_vs_prior_year": r_m / r_p if r_p else np.nan,
            "ratio_vs_ar1": r_m / r_a if r_a else np.nan,
            "sign_accuracy_vs_naive": sign_acc,
            "jackknife_ratio_min": min(ratios) if ratios else np.nan,
            "jackknife_ratio_max": max(ratios) if ratios else np.nan,
            "jackknife_below_1": int(sum(r < 1 for r in ratios)), "jackknife_n": len(ratios)}


def score(ex_fx_model: pd.Series, name: str, knowable: str, root: str | None = None,
          targets: Iterable[str] = TARGETS, fx_estimators: Iterable[str] = FX_ESTIMATORS,
          windows: dict | None = None, align_naive_to_model: bool = True) -> pd.DataFrame:
    """Score one ex-FX ADR y/y model path.

    ex_fx_model : pd.Series of model ex-FX y/y in pp, indexed by quarter label ('1Q24' ... '2Q26').
                  Quarters missing from the series count as missing (n falls; jackknife shrinks).
    name        : model label written to the `model` column.
    knowable    : the knowable-before-print flag, written verbatim (e.g. 'yes', or
                  'no: uses the prior quarter residual, which is only known at the print').
    Returns one row per (target, window, fx_estimator): t1 has fx_estimator 'none'; t2 has one row
    per estimator in `fx_estimators`.
    """
    windows = windows or WINDOWS
    rows = []
    for target in targets:
        ests = ["none"] if target != "t2_reported_usd_yoy" else list(fx_estimators)
        for est in ests:
            tf_all = target_frame(target, est if est != "none" else "midpoint", root)
            pred_all = scored_prediction(ex_fx_model, target, tf_all)
            for wname, (w0, w1) in windows.items():
                idx = [q for q in tf_all.index if QI[w0] <= QI[q] <= QI[w1]]
                tf = tf_all.loc[idx]
                blk = _score_block(pred_all.loc[idx], tf, align_naive_to_model)
                row = {"model": name, "target": target, "window": wname, "fx_estimator": est,
                       "fx_estimator_source": FX_LABEL.get(est, "none")}
                row.update(blk)
                row["knowable_before_print"] = knowable
                row["scoring"] = _scoring_label(target)
                rows.append(row)
    return pd.DataFrame(rows)


def _scoring_label(target: str) -> str:
    return {"t1_exfx_integer_fair": "model ex-FX rounded half away from zero to whole points vs disclosed integer ex-FX; naive = last disclosed ex-FX",
            "t2_reported_usd_yoy": "model ex-FX + FX estimator vs unrounded adr_usd y/y; naive = last disclosed ex-FX + same FX estimator",
            V2_ORIGINAL: "J3 record: unrounded model ex-FX vs disclosed integer ex-FX; naive = last disclosed ex-FX"}[target]


def score_benchmarks(root: str | None = None, targets: Iterable[str] = TARGETS,
                     fx_estimators: Iterable[str] = FX_ESTIMATORS, windows: dict | None = None,
                     align_naive_to_model: bool = True) -> pd.DataFrame:
    """The three benchmarks scored as if they were models, so they sit in the same table."""
    windows = windows or WINDOWS
    rows = []
    for target in targets:
        ests = ["none"] if target != "t2_reported_usd_yoy" else list(fx_estimators)
        for est in ests:
            tf_all = target_frame(target, est if est != "none" else "midpoint", root)
            for bname, col in (("naive_last_q", "naive"), ("prior_year_q", "prior_year"), ("ar1_expanding", "ar1")):
                for wname, (w0, w1) in windows.items():
                    idx = [q for q in tf_all.index if QI[w0] <= QI[q] <= QI[w1]]
                    tf = tf_all.loc[idx]
                    blk = _score_block(tf[col], tf, align_naive_to_model)
                    row = {"model": bname, "target": target, "window": wname, "fx_estimator": est,
                           "fx_estimator_source": FX_LABEL.get(est, "none")}
                    row.update(blk)
                    row["knowable_before_print"] = KNOWABLE_BENCH
                    row["scoring"] = _scoring_label(target)
                    rows.append(row)
    return pd.DataFrame(rows)


def paths(models: dict, root: str | None = None, targets: Iterable[str] = TARGETS,
          fx_estimators: Iterable[str] = FX_ESTIMATORS, first: str = FIRST_SCORED, last: str = "2Q26") -> pd.DataFrame:
    """Per-quarter walk-forward paths in scored units. `models` maps name -> ex-FX pd.Series.
    One row per (target, fx_estimator, quarter); columns actual, naive, prior_year, ar1, then one
    column per model."""
    out = []
    for target in targets:
        ests = ["none"] if target != "t2_reported_usd_yoy" else list(fx_estimators)
        for est in ests:
            tf = target_frame(target, est if est != "none" else "midpoint", root, first, last)
            block = tf[["fx_estimator", "fx_est_pp", "naive_exfx_pp", "actual", "naive", "prior_year", "ar1"]].copy()
            block.insert(0, "target", target)
            for name, s in models.items():
                block[name] = scored_prediction(s, target, tf)
            out.append(block.reset_index())
    return pd.concat(out, ignore_index=True)


# ----------------------------------------------------------------------------------
# the v2 (J3) model paths, rebuilt from the same inputs
# ----------------------------------------------------------------------------------
def residual_rule_values(hist: pd.Series, t: str) -> dict:
    """J3's residual rules on residual history strictly before t (copied logic, not the module)."""
    prior = hist[_prior(hist.index, t)].dropna()
    v = prior.values
    out = {"last_q": v[-1] if len(v) >= 1 else np.nan,
           "persistence": v[-2:].mean() if len(v) >= 2 else np.nan,
           "trailing_4q": v[-4:].mean() if len(v) >= 4 else np.nan,
           "trailing_8q": v[-8:].mean() if len(v) >= 8 else v.mean() if len(v) >= 4 else np.nan}
    if len(v) >= 6:
        b1, b0 = np.polyfit(v[:-1], v[1:], 1)
        out["ar1_residual"] = b0 + b1 * v[-1]
    else:
        out["ar1_residual"] = np.nan
    out["blend"] = 0.5 * out["persistence"] + 0.5 * out["trailing_8q"]
    return out


def v2_components(root: str | None = None, first: str = FIRST_SCORED, last: str = "2Q26") -> pd.DataFrame:
    """Per quarter: measured and trailing-4q mix, prior-calendar-year new business and interaction
    fills, the actual new business and interaction, the actual residual, and every residual rule.
    These are the building blocks of every v2 path (J3 section 4)."""
    d = load_inputs(root)
    H, res = d["H"], d["residual"]
    root = d["root"]
    adr_dir = os.path.join(root, "data", "processed", "adr")
    sd = pd.read_csv(os.path.join(adr_dir, "15_seats_dilution_annual.csv"))
    sd_base = sd[sd.case_business == "base"].set_index("year")["dilution_drag_pp"].to_dict()
    inter = pd.read_csv(os.path.join(adr_dir, "07_full_decomposition.csv")).set_index("year")["interaction_pp"].to_dict()
    mixc = ["geo_mix_pp", "unit_size_pp", "los_mix_pp"]
    rows = []
    for t in quarters_between(first, last):
        if t not in H.index:
            continue
        prior = _prior(H.index, t)
        yprev = 2000 + int(t[-2:]) - 1
        nb = 0.0 if pd.isna(sd_base.get(yprev, np.nan)) else float(sd_base[yprev])
        it = 0.0 if pd.isna(inter.get(yprev, np.nan)) else float(inter[yprev])
        r = {"quarter": t, "actual_exfx_pp": float(H.loc[t, "adr_exfx_yoy_pp"]), "actual_residual_pp": float(res[t]),
             "mix_measured_pp": float(H.loc[t, mixc].sum()),
             "mix_trailing4q_pp": float(H.loc[prior[-4:], mixc].sum(axis=1).mean()),
             "new_business_prior_year_pp": nb, "interaction_prior_year_pp": it,
             "new_business_actual_pp": float(0.0 if pd.isna(H.loc[t, "new_business_pp"]) else H.loc[t, "new_business_pp"]),
             "interaction_actual_pp": float(0.0 if pd.isna(H.loc[t, "interaction_pp"]) else H.loc[t, "interaction_pp"])}
        rv = residual_rule_values(res, t)
        for rule in RULES:
            r[f"residual_{rule}_pp"] = rv[rule]
        rows.append(r)
    return pd.DataFrame(rows).set_index("quarter")


def v2_model_paths(root: str | None = None) -> pd.DataFrame:
    """Ex-FX paths for every J3 model variant (columns V2_MODELS) plus H's route a if the H backtest
    file exists (column h_route_a). Indexed by quarter 1Q24..2Q26."""
    c = v2_components(root)
    out = pd.DataFrame(index=c.index)
    for rule in RULES:
        out[f"v2_measured_{rule}"] = c["mix_measured_pp"] + c["new_business_prior_year_pp"] + c["interaction_prior_year_pp"] + c[f"residual_{rule}_pp"]
        out[f"v2_trailing4q_{rule}"] = c["mix_trailing4q_pp"] + c["new_business_prior_year_pp"] + c["interaction_prior_year_pp"] + c[f"residual_{rule}_pp"]
    hb = os.path.join(root or ROOT, "data", "processed", "q3nowcast", "H", "adr_exfx_backtest.csv")
    if os.path.exists(hb):
        Hbt = pd.read_csv(hb).set_index("quarter")["component_build_pp"].astype(float)
        out["h_route_a"] = Hbt.reindex(out.index)
    return out


def exfx_from_residual(residual_pred: pd.Series, mix_variant: str = "measured", extra_pp: pd.Series | None = None,
                       root: str | None = None) -> pd.Series:
    """Build an ex-FX path from a residual model: mix (measured or trailing-4q, as J3) + prior-year
    new business + prior-year interaction + residual_pred (+ extra_pp, e.g. a fifth mix term from
    WS-M). Quarters absent from residual_pred come out NaN. This is what K and L should call."""
    c = v2_components(root)
    mixcol = {"measured": "mix_measured_pp", "trailing4q": "mix_trailing4q_pp"}[mix_variant]
    base = c[mixcol] + c["new_business_prior_year_pp"] + c["interaction_prior_year_pp"]
    r = pd.Series(residual_pred, dtype=float).reindex(c.index)
    out = base + r
    if extra_pp is not None:
        out = out + pd.Series(extra_pp, dtype=float).reindex(c.index).fillna(0.0)
    return out


def knowable_flag_v2(model: str) -> str:
    return KNOWABLE_V2 if model.startswith("v2_") else KNOWABLE_BENCH


# ----------------------------------------------------------------------------------
# reproduction of the J3 record
# ----------------------------------------------------------------------------------
def reproduce_j3(root: str | None = None, tol: float = 1e-3) -> tuple[pd.DataFrame, bool]:
    """Rescore every J3 model and benchmark in J3's own mode (unrounded model vs integer disclosed,
    naive over all window quarters as J3) and compare rmse, ratio vs naive and jackknife min / max
    with data/processed/adrq3/J/card_v2_backtest.csv. Returns (comparison table, all within tol)."""
    root = root or ROOT
    rec = pd.read_csv(os.path.join(root, "data", "processed", "adrq3", "J", "card_v2_backtest.csv"))
    pth = v2_model_paths(root)
    models = {m: pth[m] for m in V2_MODELS}
    if "h_route_a" in pth:
        models["h_route_a"] = pth["h_route_a"]
    parts = [score_benchmarks(root, targets=(V2_ORIGINAL,), align_naive_to_model=False)]
    for m, s in models.items():
        parts.append(score(s, m, knowable_flag_v2(m), root, targets=(V2_ORIGINAL,), align_naive_to_model=False))
    new = pd.concat(parts, ignore_index=True)
    cols = ["rmse_pp", "ratio_vs_naive", "ratio_vs_prior_year", "ratio_vs_ar1", "jackknife_ratio_min", "jackknife_ratio_max"]
    rec = rec.rename(columns={"jackknife_ratio_min": "jackknife_ratio_min", "jackknife_ratio_max": "jackknife_ratio_max"})
    cmp = new[["model", "window", "n"] + cols].merge(rec[["model", "window", "n"] + cols], on=["model", "window"],
                                                       suffixes=("_S1", "_J3"), how="inner")
    for c in cols:
        cmp[f"diff_{c}"] = (cmp[f"{c}_S1"] - cmp[f"{c}_J3"]).abs()
    cmp["max_abs_diff"] = cmp[[f"diff_{c}" for c in cols]].max(axis=1)
    ok = bool(len(cmp) == len(rec) and (cmp["max_abs_diff"] < tol).all() and (cmp["n_S1"] == cmp["n_J3"]).all())
    return cmp, ok


# ----------------------------------------------------------------------------------
# the pre-registered v3 criterion
# ----------------------------------------------------------------------------------
def preregistered_pass(df: pd.DataFrame, model: str = V3_RULE_MODEL, windows: Iterable[str] = tuple(WINDOWS),
                       fx_estimators: Iterable[str] = ("eur", "baskets")) -> dict:
    """BRIEF v3 criterion: on target 2, under BOTH the eur and baskets FX estimators, on BOTH windows,
    ratio vs naive < 1.0 AND jackknife maximum < 1.0. Target 1 is reported alongside, not part of
    the pass. `df` is a frame from score() (any number of models; `model` selects one)."""
    d = df[df.model == model]
    if d.empty:
        raise ValueError(f"model {model!r} not in the frame")
    checks = []
    for est in fx_estimators:
        for w in windows:
            r = d[(d.target == "t2_reported_usd_yoy") & (d.fx_estimator == est) & (d.window == w)]
            if r.empty:
                raise ValueError(f"no target-2 row for {model} {est} {w}")
            r = r.iloc[0]
            checks.append({"model": model, "target": "t2_reported_usd_yoy", "fx_estimator": est, "window": w, "n": int(r.n),
                           "rmse_pp": float(r.rmse_pp), "rmse_naive_pp": float(r.rmse_naive_pp),
                           "ratio_vs_naive": float(r.ratio_vs_naive), "jackknife_ratio_min": float(r.jackknife_ratio_min),
                           "jackknife_ratio_max": float(r.jackknife_ratio_max), "jackknife_below_1": int(r.jackknife_below_1),
                           "ratio_below_1": bool(r.ratio_vs_naive < 1.0), "jackknife_max_below_1": bool(r.jackknife_ratio_max < 1.0),
                           "criterion_met": bool(r.ratio_vs_naive < 1.0 and r.jackknife_ratio_max < 1.0), "in_pass_criterion": True})
    alongside = []
    for w in windows:
        r = d[(d.target == "t1_exfx_integer_fair") & (d.window == w)]
        if not r.empty:
            r = r.iloc[0]
            alongside.append({"model": model, "target": "t1_exfx_integer_fair", "fx_estimator": "none", "window": w, "n": int(r.n),
                              "rmse_pp": float(r.rmse_pp), "rmse_naive_pp": float(r.rmse_naive_pp),
                              "ratio_vs_naive": float(r.ratio_vs_naive), "jackknife_ratio_min": float(r.jackknife_ratio_min),
                              "jackknife_ratio_max": float(r.jackknife_ratio_max), "jackknife_below_1": int(r.jackknife_below_1),
                              "ratio_below_1": bool(r.ratio_vs_naive < 1.0), "jackknife_max_below_1": bool(r.jackknife_ratio_max < 1.0),
                              "criterion_met": bool(r.ratio_vs_naive < 1.0 and r.jackknife_ratio_max < 1.0), "in_pass_criterion": False})
        r = d[(d.target == "t2_reported_usd_yoy") & (d.fx_estimator == "midpoint") & (d.window == w)]
        if not r.empty:
            r = r.iloc[0]
            alongside.append({"model": model, "target": "t2_reported_usd_yoy", "fx_estimator": "midpoint", "window": w, "n": int(r.n),
                              "rmse_pp": float(r.rmse_pp), "rmse_naive_pp": float(r.rmse_naive_pp),
                              "ratio_vs_naive": float(r.ratio_vs_naive), "jackknife_ratio_min": float(r.jackknife_ratio_min),
                              "jackknife_ratio_max": float(r.jackknife_ratio_max), "jackknife_below_1": int(r.jackknife_below_1),
                              "ratio_below_1": bool(r.ratio_vs_naive < 1.0), "jackknife_max_below_1": bool(r.jackknife_ratio_max < 1.0),
                              "criterion_met": bool(r.ratio_vs_naive < 1.0 and r.jackknife_ratio_max < 1.0), "in_pass_criterion": False})
    passed = all(c["criterion_met"] for c in checks)
    return {"model": model, "pass": passed, "verdict": "PASS" if passed else "FAIL",
            "criterion": "target 2 (reported dollar ADR y/y, unrounded): ratio vs naive < 1.0 on both windows AND jackknife max < 1.0, under both the eur and baskets FX estimators",
            "checks": checks, "alongside": alongside,
            "n_checks": len(checks), "n_checks_met": int(sum(c["criterion_met"] for c in checks))}


def pass_table(result: dict) -> pd.DataFrame:
    rows = [dict(r, verdict=result["verdict"]) for r in result["checks"]] + [dict(r, verdict=result["verdict"]) for r in result["alongside"]]
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------
# demo
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    pd.set_option("display.width", 250)
    cmp, ok = reproduce_j3()
    print("reproduction of J3 card_v2_backtest.csv: max abs diff %.6f over %d rows -> %s" % (cmp.max_abs_diff.max(), len(cmp), "OK" if ok else "MISMATCH"))
    print(cmp[cmp.model.isin([V2_RULE_MODEL, V3_RULE_MODEL, "naive_last_q"])][["model", "window", "rmse_pp_S1", "rmse_pp_J3", "ratio_vs_naive_S1", "ratio_vs_naive_J3", "max_abs_diff"]].round(4).to_string())
    p = v2_model_paths()
    df = score(p[V3_RULE_MODEL], V3_RULE_MODEL, KNOWABLE_V2)
    print(df[["model", "target", "window", "fx_estimator", "n", "rmse_pp", "rmse_naive_pp", "ratio_vs_naive", "jackknife_ratio_min", "jackknife_ratio_max", "jackknife_below_1", "sign_accuracy_vs_naive"]].round(3).to_string())
    res = preregistered_pass(df)
    print("v3 pre-registered verdict for", res["model"], "->", res["verdict"], f"({res['n_checks_met']} of {res['n_checks']} checks met)")
