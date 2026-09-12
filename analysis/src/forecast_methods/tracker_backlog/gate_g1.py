"""(c) Gate G1, redefined: does the RAW (non-circular) backlog series beat naive/AR(1)
for next-quarter revenue growth, on W1 and W2? Expect failure on revenue; the honest
claim is the backlog predicts VOLUME (nights), not dollars. RNPL correction is applied
as a disclosed-GBV-share SCENARIO (not fit to the target -- fitting it would recreate
exactly the circularity struck in circularity.py).

Predictor: OLS of y_{q} (metric y/y growth) on x_{q-1} (backlog-item y/y growth at the
LAST PRINTED quarter, i.e. what a forecaster standing at the guide date for q actually
has in hand), refit expanding-window at every vintage date using only realised pairs
known at that date (n_params=2: intercept + slope). Two features tested independently
(unearned fees y/y, funds held y/y) -- the decision doc asks for both. Two targets
(revenue_yoy, nights_yoy). PIT replay refits at each date; full_sample replay fixes the
slope/intercept to the final full-history fit (inputs are still point-in-time; only
parameter KNOWLEDGE leaks, per baselines.py's own convention).
"""
from __future__ import annotations

import sys
import numpy as np
import pandas as pd

from common import (ensure_out_dir, load_kpi_quarterly, RNPL_GBV_SHARE_SCENARIO_PCT,
                    OUT_DIR, GUIDE_EVENTS_ALL, W1_TARGETS, W2_TARGETS, window_of_target,
                    load_targets, history_as_of, register, validate_registry_frame, Q,
                    baseline_naive, baseline_ar1, SRC_08_BACKLOG_TESTS)

FEATURES = {
    "unearned": "unearned_fees_yoy_pct",
    "funds": "funds_held_yoy_pct",
}
TARGETS = {"revenue_yoy_next_q": "revenue_yoy", "nights_yoy_next_q": "nights_yoy"}
RNPL_K_SCENARIOS = {"k0.5": 0.5, "k1.0": 1.0, "k1.5": 1.5}


def _short(q):  # 'YYYYQn' -> '3Q26' spelling used by the KPI panel
    c = Q.canon(q)
    return f"{c[5]}Q{c[2:4]}"


def build_feature_frame() -> pd.DataFrame:
    """quarter (YYYYQn) -> feature y/y growths, keyed to the KPI panel's own 'quarter'
    spelling (e.g. '3Q26'), merged onto the harness's canonical 'YYYYQn' labels."""
    k = load_kpi_quarterly()[["quarter", "unearned_fees_yoy_pct", "funds_held_yoy_pct"]].copy()
    k["quarter"] = k["quarter"].map(Q.canon)
    return k


def rnpl_correction_pct(quarter: str, feature_key: str, k: float) -> float:
    """Scenario add-back to the RAW y/y feature growth for RNPL-era quarters, in
    points, = k * disclosed/scenario RNPL GBV share (NOT fit against the target)."""
    sq = _short(quarter)
    share = RNPL_GBV_SHARE_SCENARIO_PCT.get(sq, 0.0)
    return k * share


def _fit_ols(xs, ys):
    if len(xs) < 4:
        return None
    X = np.column_stack([np.ones(len(xs)), np.asarray(xs, float)])
    y = np.asarray(ys, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = max(len(xs) - 2, 1)
    sigma = float(np.sqrt((resid ** 2).sum() / dof))
    return {"a": float(beta[0]), "b": float(beta[1]), "sigma": sigma, "n": len(xs)}


def build_pairs(feat: pd.DataFrame, feature_col: str, target_metric: str,
                targets: pd.DataFrame, rnpl_k: float | None) -> pd.DataFrame:
    """(quarter q, x = feature at q-1, y = target metric y/y at q) for every quarter
    with both observed, x optionally RNPL-corrected."""
    t = targets[["quarter", target_metric, "print_date"]].dropna(subset=[target_metric]).copy()
    rows = []
    for _, r in t.iterrows():
        q = r["quarter"]
        qprev = Q.shift(q, -1)
        fx = feat.loc[feat.quarter == qprev, feature_col]
        if len(fx) == 0 or pd.isna(fx.iloc[0]):
            continue
        x = float(fx.iloc[0])
        if rnpl_k is not None:
            x = x + rnpl_correction_pct(qprev, feature_col, rnpl_k)
        rows.append({"quarter": q, "x": x, "y": float(r[target_metric])})
    return pd.DataFrame(rows).sort_values("quarter").reset_index(drop=True)


def walk_forward(pairs: pd.DataFrame, guide_dates_targets, targets_df) -> pd.DataFrame:
    """Expanding-window fit/predict at each (vintage_date, target_quarter). Returns one
    row per date with PIT-fit prediction; full-sample fit added by caller."""
    out = []
    for gdate, tq in guide_dates_targets:
        train = pairs[pairs.quarter < tq]
        if len(train) < 4:
            continue
        fit = _fit_ols(train["x"].to_numpy(), train["y"].to_numpy())
        if fit is None:
            continue
        row_x = pairs.loc[pairs.quarter == tq, "x"]
        if len(row_x) == 0:
            continue
        x_at_vintage = float(row_x.iloc[0])
        point = fit["a"] + fit["b"] * x_at_vintage
        actual_row = pairs.loc[pairs.quarter == tq, "y"]
        actual = float(actual_row.iloc[0]) if len(actual_row) else np.nan
        out.append({"vintage_date": gdate, "quarter": tq, "x": x_at_vintage,
                    "point_pit": point, "a_pit": fit["a"], "b_pit": fit["b"],
                    "sigma_pit": fit["sigma"], "n_train_pit": fit["n"], "actual": actual})
    return pd.DataFrame(out)


def add_full_sample(wf: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    fit = _fit_ols(pairs["x"].to_numpy(), pairs["y"].to_numpy())
    wf = wf.copy()
    if fit is None:
        wf["point_fs"] = np.nan
        wf["sigma_fs"] = np.nan
        wf["n_train_fs"] = 0
        return wf
    wf["point_fs"] = fit["a"] + fit["b"] * wf["x"]
    wf["sigma_fs"] = fit["sigma"]
    wf["n_train_fs"] = fit["n"]
    return wf


_Z90 = 1.2815515655446004


def to_registry_rows(wf: pd.DataFrame, method, object_, target_metric, spec_id, notes):
    rows = []
    for _, r in wf.iterrows():
        tq = r["quarter"]
        wins = window_of_target(tq)
        for win in wins:
            for basis, pcol, scol, ncol in (
                ("PIT", "point_pit", "sigma_pit", "n_train_pit"),
                ("full_sample", "point_fs", "sigma_fs", "n_train_fs"),
            ):
                pt = r[pcol]
                if not np.isfinite(pt):
                    continue
                sd = r[scol] if np.isfinite(r[scol]) and r[scol] > 0 else abs(pt) * 0.05 + 1.0
                rows.append({
                    "method": method, "object": object_, "target": target_metric,
                    "quarter": tq, "vintage_date": r["vintage_date"],
                    "horizon_q": 1, "point": float(pt), "q50": float(pt),
                    "q10": float(pt - _Z90 * sd), "q90": float(pt + _Z90 * sd),
                    "sd": float(sd), "window": win, "prior_basis": basis,
                    "n_params": 2, "n_train": int(r[ncol]),
                    "spec_id": spec_id, "notes": notes,
                })
    return pd.DataFrame(rows)


def score_wf(wf: pd.DataFrame, label: str) -> dict:
    d = wf.dropna(subset=["actual"]).copy()
    if len(d) == 0:
        return {"label": label, "n": 0}
    err = d["point_pit"] - d["actual"]
    return {
        "label": label, "n": len(d),
        "mae": float(err.abs().mean()), "rmse": float(np.sqrt((err ** 2).mean())),
        "bias": float(err.mean()),
        "sign_acc": float(np.mean(np.sign(d["point_pit"]) == np.sign(d["actual"]))),
    }


def run():
    ensure_out_dir()
    feat = build_feature_frame()
    targets = load_targets()

    all_reg = []
    summary_rows = []
    for obj_name, target_metric in TARGETS.items():
        for feat_key, feat_col in FEATURES.items():
            # RAW (no RNPL correction)
            pairs = build_pairs(feat, feat_col, target_metric, targets, rnpl_k=None)
            w1_events = [(d, q) for d, q in GUIDE_EVENTS_ALL if q in W1_TARGETS]
            wf1 = walk_forward(pairs, w1_events, targets)
            wf1 = add_full_sample(wf1, pairs)
            spec_id = f"{feat_key}_raw"
            reg = to_registry_rows(wf1, "tracker-backlog", obj_name, target_metric,
                                   spec_id, f"raw {feat_key} y/y feature, no RNPL correction")
            all_reg.append(reg)
            s_w1 = score_wf(wf1[wf1.quarter.isin(W1_TARGETS)], f"{obj_name}|{feat_key}_raw|W1")
            s_w2 = score_wf(wf1[wf1.quarter.isin(W2_TARGETS)], f"{obj_name}|{feat_key}_raw|W2")
            summary_rows += [s_w1, s_w2]

            # RNPL-corrected SCENARIOS (only meaningful where correction != 0, i.e. all
            # dates, since it changes both training features for RNPL-era pairs and the
            # prediction input)
            for k_name, k in RNPL_K_SCENARIOS.items():
                pairs_k = build_pairs(feat, feat_col, target_metric, targets, rnpl_k=k)
                wfk = walk_forward(pairs_k, w1_events, targets)
                wfk = add_full_sample(wfk, pairs_k)
                spec_id_k = f"{feat_key}_rnpl_scenario_{k_name}"
                reg_k = to_registry_rows(wfk, "tracker-backlog", obj_name, target_metric,
                                         spec_id_k,
                                         f"{feat_key} y/y feature + RNPL GBV-share scenario "
                                         f"add-back, k={k} (scenario, not fit to target)")
                all_reg.append(reg_k)
                s_w1k = score_wf(wfk[wfk.quarter.isin(W1_TARGETS)], f"{obj_name}|{feat_key}_rnpl_{k_name}|W1")
                s_w2k = score_wf(wfk[wfk.quarter.isin(W2_TARGETS)], f"{obj_name}|{feat_key}_rnpl_{k_name}|W2")
                summary_rows += [s_w1k, s_w2k]

    reg_all = pd.concat(all_reg, ignore_index=True)
    # one file per (method, object) pair (harness format): split, validate, register
    for obj_name in TARGETS:
        sub = reg_all[reg_all.object == obj_name]
        _ = validate_registry_frame(sub)  # raise early on any format violation
        register(sub)

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_DIR / "03_gate_g1_walkforward_summary.csv", index=False)
    reg_all.to_csv(OUT_DIR / "03b_gate_g1_all_registry_rows.csv", index=False)

    ratios = _ratio_vs_baselines_by_spec(reg_all, targets)
    ratios.to_csv(OUT_DIR / "03c_gate_g1_ratios_by_spec.csv", index=False)

    # VERIFICATION FIX (priority 1): reconcile funds_raw/revenue_yoy/W2 against the
    # previously-published 02_model_audit.md line 438 "survivor" claim. Written
    # unconditionally (not gated on the ratio looking surprising) so it is always
    # available as evidence before the funds feature or its RNPL variants are used.
    recon = reconcile_funds_w2(feat, targets)
    print("\nfunds_raw / revenue_yoy / W2 legacy-convention reconciliation "
          "(03d_funds_w2_legacy_reconciliation.csv):")
    print(recon.to_string(index=False))

    return summary, reg_all, ratios


def _ratio_vs_baselines_by_spec(reg_all: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    """RMSE ratio to naive/AR(1) PER spec_id.

    Two reasons this is computed locally rather than read off the harness scoreboard:
    (1) harness score.py's GROUP_KEYS has no spec_id column, so multiple spec_id
        variants registered under one object (the README's own suggested pattern, "a
        grid of variants can live in one object file") get POOLED into one blended
        scoreboard row -- which hides exactly the raw-vs-RNPL-scenario,
        unearned-vs-funds comparison this package exists to make.
        HARNESS CHANGE REQUEST: add spec_id to score.py's GROUP_KEYS, or document
        that multi-spec objects must not be scored as a single row.
    (2) the "baselines" package's BASELINE_SPECS list (baselines.py) hard-codes its
        metric coverage to ["revenue_musd","revenue_yoy","gbv_musd","nights_m"] and
        does NOT include "nights_yoy" -- even though it is a valid target metric in
        targets.csv and baseline_naive/baseline_ar1 are metric-agnostic. There is
        therefore no baselines__naive/ar1 row for nights_yoy to join against.
        HARNESS CHANGE REQUEST: add nights_yoy (and adr_yoy, gbv_yoy) to
        BASELINE_SPECS's metric list so every package targeting those metrics gets a
        registered denominator instead of each having to call the functions directly.
    Both baseline functions are metric-agnostic, so they are called DIRECTLY here
    (not read from the registry) -- this is robust to either gap and exactly
    reproduces what the harness would compute if the gaps were fixed.
    """
    rows = []
    key_cols = ["target", "object", "spec_id", "window", "prior_basis"]
    for keys, g in reg_all.groupby(key_cols):
        tgt, obj, spec, win, basis = keys
        actual_col = "revenue_yoy" if tgt == "revenue_yoy" else "nights_yoy"
        gm = g.merge(targets[["quarter", actual_col]], on="quarter", how="left")
        err = (gm["point"] - gm[actual_col]).dropna()
        if len(err) == 0:
            continue
        rmse = float(np.sqrt((err ** 2).mean()))
        mae = float(err.abs().mean())
        bias = float(err.mean())
        out_ratio = {}
        for bname, bfn in (("naive", baseline_naive), ("ar1", baseline_ar1)):
            berrs = []
            for _, r in g.iterrows():
                bd = bfn(r["vintage_date"], r["quarter"], metric=tgt,
                        prior_basis=basis, targets=targets)
                if bd is None:
                    continue
                a = targets.loc[targets.quarter == r["quarter"], actual_col]
                if len(a) and pd.notna(a.iloc[0]):
                    berrs.append(bd["point"] - float(a.iloc[0]))
            brmse = float(np.sqrt(np.mean(np.square(berrs)))) if berrs else np.nan
            out_ratio[f"rmse_{bname}"] = brmse
            out_ratio[f"ratio_vs_{bname}"] = rmse / brmse if brmse else np.nan
        rows.append({"target": tgt, "object": obj, "spec_id": spec, "window": win,
                     "prior_basis": basis, "n": len(err), "rmse": rmse, "mae": mae,
                     "bias": bias, **out_ratio,
                     "beats_naive": (out_ratio["ratio_vs_naive"] < 1.0) if pd.notna(out_ratio["ratio_vs_naive"]) else None,
                     "beats_ar1": (out_ratio["ratio_vs_ar1"] < 1.0) if pd.notna(out_ratio["ratio_vs_ar1"]) else None})
    return pd.DataFrame(rows).sort_values(key_cols).reset_index(drop=True)


def reconcile_funds_w2(feat: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    """VERIFICATION FIX (priority 1, round 1): 02_model_audit.md line 438 quotes a
    previously-published "survivor" for the funds_held feature -- bl_funds_yoy_lag1 ->
    rev_yoy, ratio_vs_naive 0.600, sourced from 08_backlog_tests.csv -- for the IDENTICAL
    feature/target/window this package's own funds_raw/revenue_yoy/W2/PIT row scores at
    0.985 (a narrow pass, not a survivor). This function reproduces both training
    CONVENTIONS side by side to diagnose, not just disclose, the gap.

    Root cause (confirmed here numerically): 08_backlog_tests.csv's own "window" column
    shows its W2 walk-forward TRAINS on "2023Q1..2026Q2, WF from 2024Q1" -- i.e. it drops
    2022 entirely from the training sample. This package's walk_forward() instead trains
    on full history from 2022Q1 for both W1 and W2 (differing only in which dates are
    SCORED), which is what the standing instruction specifies ("expanding window ...
    W1 origin 1Q23 ... W2 origin 1Q24"): the window origin governs the scored dates, not
    a second, shorter training-sample cutoff. funds_held_yoy_pct has a sharp 2022
    reopening outlier (70.3% -> 52.1% -> 18.5% y/y in 4Q21-2Q22, per the KPI panel) that
    swings the OLS fit far more than it swings the unearned-fees feature, which is why
    dropping 2022 from training flips this one feature/window cell from a narrow pass
    to a much stronger one -- an artefact of training-sample choice, not evidence the
    funds feature is a stronger predictor than this package's headline numbers say.
    """
    feat_col = FEATURES["funds"]
    target_metric = "revenue_yoy"
    pairs = build_pairs(feat, feat_col, target_metric, targets, rnpl_k=None)
    w2_events = [(d, q) for d, q in GUIDE_EVENTS_ALL if q in W2_TARGETS]

    rows = []
    for convention, min_train_q in (
        ("this_package_full_history_from_2022Q1", None),
        ("legacy_08backlogtests_truncated_2023Q1plus", "2023Q1"),
    ):
        tr_pairs = pairs if min_train_q is None else pairs[pairs.quarter >= min_train_q].reset_index(drop=True)
        wf = walk_forward(tr_pairs, w2_events, targets)
        d = wf.dropna(subset=["actual"]).copy()
        if len(d) == 0:
            rows.append({"convention": convention, "n": 0})
            continue
        err = d["point_pit"] - d["actual"]
        rmse = float(np.sqrt((err ** 2).mean()))
        berrs_naive, berrs_ar1 = [], []
        for _, r in d.iterrows():
            bn = baseline_naive(r["vintage_date"], r["quarter"], metric=target_metric,
                                prior_basis="PIT", targets=targets)
            ba = baseline_ar1(r["vintage_date"], r["quarter"], metric=target_metric,
                              prior_basis="PIT", targets=targets)
            if bn is not None:
                berrs_naive.append(bn["point"] - r["actual"])
            if ba is not None:
                berrs_ar1.append(ba["point"] - r["actual"])
        rmse_naive = float(np.sqrt(np.mean(np.square(berrs_naive)))) if berrs_naive else np.nan
        rmse_ar1 = float(np.sqrt(np.mean(np.square(berrs_ar1)))) if berrs_ar1 else np.nan
        rows.append({
            "convention": convention, "n": len(d),
            "n_train_at_first_scored_date": int(d["n_train_pit"].iloc[0]) if "n_train_pit" in d else None,
            "rmse": rmse, "rmse_naive": rmse_naive, "rmse_ar1": rmse_ar1,
            "ratio_vs_naive": rmse / rmse_naive if rmse_naive else np.nan,
            "ratio_vs_ar1": rmse / rmse_ar1 if rmse_ar1 else np.nan,
        })

    out = pd.DataFrame(rows)

    # cross-check against the legacy CSV's own quoted row, read directly (not
    # hand-transcribed), for the exact feature/target/window cited in the audit.
    legacy_ratio = np.nan
    try:
        lg = pd.read_csv(SRC_08_BACKLOG_TESTS)
        lgm = lg[(lg.feature == "bl_funds_yoy_lag1") & (lg.target == "rev_yoy") &
                 (lg.window == "2023Q1..2026Q2, WF from 2024Q1")]
        if len(lgm):
            legacy_ratio = float(lgm.iloc[0]["wf_ratio_vs_naive"])
    except Exception:
        pass
    out["legacy_08backlogtests_quoted_ratio_vs_naive"] = legacy_ratio
    out["audit_line438_survivor_ratio_quoted"] = 0.600
    out.to_csv(OUT_DIR / "03d_funds_w2_legacy_reconciliation.csv", index=False)
    return out


if __name__ == "__main__":
    summary, reg_all, ratios = run()
    pd.set_option("display.width", 200)
    print(ratios[ratios.prior_basis == "PIT"].to_string(index=False))
    print(f"\n{len(reg_all)} registry rows written across {reg_all.object.nunique()} objects")
