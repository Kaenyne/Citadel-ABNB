"""Margin scorer: registry -> scoreboard_margin.csv / .md + scoreboard_by_quarter.csv.

Per (method, object, target, window, horizon_q, prior_basis, spec_id):
  n, mae, rmse, bias, crps, pinball_mean, cov80 (q10-q90), cov90 (q05-q95), pit_mean,
  mae_ratio_<baseline> for every `baselines-margin` object (PIT replay, matched quarters),
  beats_seasonal_naive, survives_both_windows, n_params, n_obs, param_obs_ratio, replays_present,
  and every accuracy statistic again RECENCY-WEIGHTED (prefix rw_): exponential weights
  w = 0.5 ** ((T - t) / 4) in quarters, anchored at T = the latest quarter of the window (2026Q2),
  normalised to sum to 1 over the scored rows of the group.
Rolling split conformal (frozen metrics, n_cal=6, alpha=0.2) is reported with the frozen caveat.
spec_id is part of the key so a grid of variants can live in one object file.
LIVE rows are excluded (no actual). Rows whose quarter has no actual are dropped.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import paths as P
from . import significance as SIG
from .frozen import Q, W, M, QUANTILE_COLUMNS, QUANTILE_LEVELS, TODAY, FORMAT_VERSION
from .panel import load_targets, TARGET_METRICS
from .registry import load_registry

GROUP_KEYS = ["method", "object", "target", "window", "horizon_q", "prior_basis", "spec_id"]
HALF_LIFE_Q = 4.0
BASELINE_OBJECTS = ["seasonal_naive", "seasonal_naive_drift", "trailing4", "pct_rev_last4",
                    "guide_implied", "q_guide_implied", "street"]
PRIMARY_BASELINE = "seasonal_naive"
WINDOW_ANCHOR = {"W1": W.W1_TARGETS[-1], "W2": W.W2_TARGETS[-1]}


def _actuals(targets=None) -> pd.DataFrame:
    t = load_targets() if targets is None else targets
    t = t[t["has_actual"]]
    long = t.melt(id_vars=["quarter"], value_vars=[c for c in TARGET_METRICS if c in t.columns],
                  var_name="target", value_name="actual").dropna(subset=["actual"])
    return long


def recency_weights(quarters, anchor: str) -> np.ndarray:
    ai = Q.to_index(anchor)
    w = np.array([0.5 ** ((ai - Q.to_index(q)) / HALF_LIFE_Q) for q in quarters], dtype=float)
    return w / w.sum() if w.sum() > 0 else w


def _row_quantiles(row):
    levels, values = [], []
    for c in QUANTILE_COLUMNS:
        v = row.get(c)
        if v is not None and pd.notna(v):
            levels.append(QUANTILE_LEVELS[c]); values.append(float(v))
    return levels, values


def _wmean(x, w):
    x = np.asarray(x, dtype=float); w = np.asarray(w, dtype=float)
    m = np.isfinite(x)
    if not m.any():
        return np.nan
    return float(np.sum(x[m] * w[m]) / np.sum(w[m]))


def _stats(y, p, w, crps, pinball, in80, in90, pits):
    err = p - y
    return {
        "mae": _wmean(np.abs(err), w),
        "rmse": float(np.sqrt(_wmean(err ** 2, w))),
        "bias": _wmean(err, w),
        "crps": _wmean(crps, w),
        "pinball_mean": _wmean(pinball, w),
        "cov80": _wmean(in80, w),
        "cov90": _wmean(in90, w),
        "pit_mean": _wmean(pits, w),
    }


def _prep(reg: pd.DataFrame, targets=None) -> pd.DataFrame:
    d = reg.copy()
    d["window"] = d["window"].astype(str).str.upper()
    d = d[d["window"] != "LIVE"]
    if "spec_id" not in d.columns:
        d["spec_id"] = ""
    d["spec_id"] = d["spec_id"].fillna("").astype(str)
    d["quarter"] = d["quarter"].map(Q.canon)
    d = d.merge(_actuals(targets), on=["quarter", "target"], how="left").dropna(subset=["actual"])
    d["horizon_q"] = d["horizon_q"].astype(int)
    d["point"] = pd.to_numeric(d["point"], errors="coerce")
    return d.sort_values(GROUP_KEYS + ["quarter"]).reset_index(drop=True)


def _per_row(d: pd.DataFrame) -> pd.DataFrame:
    """Row-level errors, CRPS, coverage flags and recency weights (the by_quarter file)."""
    out = d.copy()
    crps, pinball, in80, in90, pits, edge = [], [], [], [], [], []
    for _, r in out.iterrows():
        lv, vv = _row_quantiles(r)
        y = float(r["actual"]); pt = float(r["point"])
        crps.append(M.crps_from_quantiles(y, lv, vv) if lv else abs(y - pt))
        pinball.append(np.mean([M.pinball_loss(y, v, t) for v, t in zip(vv, lv)]) if lv else np.nan)
        pv, ed = M.pit_from_quantiles(y, lv, vv)
        pits.append(pv); edge.append(ed)
        q10, q90 = r.get("q10"), r.get("q90")
        q05, q95 = r.get("q05"), r.get("q95")
        in80.append(float(q10 <= y <= q90) if pd.notna(q10) and pd.notna(q90) else np.nan)
        in90.append(float(q05 <= y <= q95) if pd.notna(q05) and pd.notna(q95) else np.nan)
    out["err"] = out["point"] - out["actual"]
    out["abs_err"] = out["err"].abs()
    out["crps"] = crps
    out["pinball"] = pinball
    out["in80"] = in80
    out["in90"] = in90
    out["pit"] = pits
    out["pit_edge"] = edge
    out["weight_rw"] = np.nan
    for keys, g in out.groupby(GROUP_KEYS, sort=False):
        anchor = WINDOW_ANCHOR.get(keys[3], W.W1_TARGETS[-1])
        out.loc[g.index, "weight_rw"] = recency_weights(g["quarter"].tolist(), anchor)
    return out


def _baseline_maps(rows: pd.DataFrame) -> dict:
    """{baseline_object: {(target, window, h, quarter): (point, abs_err)}} from the PIT replay."""
    maps = {}
    b = rows[(rows["method"] == P.BASELINE_METHOD) & (rows["prior_basis"] == "PIT")]
    for obj, g in b.groupby("object"):
        g = g.drop_duplicates(["target", "window", "horizon_q", "quarter"])
        maps[obj] = {(r.target, r.window, int(r.horizon_q), r.quarter): (float(r.point), float(r.abs_err))
                     for r in g.itertuples()}
    return maps


def score_registry(reg: pd.DataFrame | None = None, targets=None, n_cal: int = 6, alpha: float = 0.2):
    """Returns (scoreboard, by_quarter). `reg` defaults to the whole margin registry."""
    reg = load_registry() if reg is None else reg
    if len(reg) == 0:
        return pd.DataFrame(), pd.DataFrame()
    d = _prep(reg, targets)
    if len(d) == 0:
        return pd.DataFrame(), pd.DataFrame()
    rows = _per_row(d)
    bmaps = _baseline_maps(rows)
    # seasonal-naive point / error carried on every by_quarter row for diffing
    sn = bmaps.get(PRIMARY_BASELINE, {})
    rows["seasonal_naive_point"] = [sn.get((r.target, r.window, int(r.horizon_q), r.quarter), (np.nan, np.nan))[0]
                                    for r in rows.itertuples()]
    rows["seasonal_naive_abs_err"] = [sn.get((r.target, r.window, int(r.horizon_q), r.quarter), (np.nan, np.nan))[1]
                                      for r in rows.itertuples()]

    out = []
    for keys, g in rows.groupby(GROUP_KEYS, sort=True):
        method, obj, target, window, h, basis, spec = keys
        g = g.sort_values("quarter")
        y = g["actual"].to_numpy(dtype=float)
        p = g["point"].to_numpy(dtype=float)
        n = len(y)
        w_eq = np.ones(n) / n
        w_rw = g["weight_rw"].to_numpy(dtype=float)
        ew = _stats(y, p, w_eq, g["crps"], g["pinball"], g["in80"], g["in90"], g["pit"])
        rw = _stats(y, p, w_rw, g["crps"], g["pinball"], g["in80"], g["in90"], g["pit"])
        rec = {"method": method, "object": obj, "target": target, "window": window, "horizon_q": int(h),
               "prior_basis": basis, "spec_id": spec, "n": n,
               "first_quarter": g["quarter"].iloc[0], "last_quarter": g["quarter"].iloc[-1]}
        rec.update(ew)
        rec.update({f"rw_{k}": v for k, v in rw.items()})
        # ratios to every baseline on matched quarters
        for bobj in BASELINE_OBJECTS:
            bm = bmaps.get(bobj, {})
            be = np.array([bm.get((target, window, int(h), q), (np.nan, np.nan))[1] for q in g["quarter"]])
            m = np.isfinite(be)
            if m.sum() >= 2:
                own = np.abs(p - y)
                mae_b = float(np.mean(be[m])); mae_o = float(np.mean(own[m]))
                wr = w_rw[m] / w_rw[m].sum()
                rmae_b = float(np.sum(be[m] * wr)); rmae_o = float(np.sum(own[m] * wr))
                rec[f"mae_ratio_{bobj}"] = mae_o / mae_b if mae_b > 0 else np.nan
                rec[f"rw_mae_ratio_{bobj}"] = rmae_o / rmae_b if rmae_b > 0 else np.nan
                rec[f"n_match_{bobj}"] = int(m.sum())
            else:
                rec[f"mae_ratio_{bobj}"] = np.nan
                rec[f"rw_mae_ratio_{bobj}"] = np.nan
                rec[f"n_match_{bobj}"] = int(m.sum())
        # WS22 (R01/R02/R08): paired-loss significance next to every ratio. New columns only.
        rec.update(SIG.significance_columns({q: abs(pp - yy) for q, pp, yy in zip(g["quarter"], p, y)},
                                            bmaps, target, window, int(h)))
        r_ew = rec[f"mae_ratio_{PRIMARY_BASELINE}"]
        r_rw = rec[f"rw_mae_ratio_{PRIMARY_BASELINE}"]
        rec["beats_seasonal_naive"] = bool(np.isfinite(r_ew) and r_ew < 1.0)
        rec["rw_beats_seasonal_naive"] = bool(np.isfinite(r_rw) and r_rw < 1.0)
        conf_cov, conf_n, conf_w = M.rolling_split_conformal(y, p, n_cal=n_cal, alpha=alpha)
        k, att_lo, att_hi = M.attainable_coverage(n_cal, alpha)
        rec.update({"pit_edge_frac": float(g["pit_edge"].mean()),
                    "conformal_n_cal": n_cal, "conformal_alpha": alpha, "conformal_n_eval": conf_n,
                    "conformal_cov_empirical": conf_cov, "conformal_mean_width": conf_w,
                    "conformal_attainable_lo": att_lo, "conformal_attainable_hi": att_hi,
                    "n_params": int(pd.to_numeric(g["n_params"], errors="coerce").max()),
                    "n_obs": n})
        rec["param_obs_ratio"] = rec["n_params"] / n if n else np.nan
        rec["coverage_caveat"] = M.EXCHANGEABILITY_CAVEAT
        out.append(rec)
    sb = pd.DataFrame(out)
    if len(sb) == 0:
        return sb, rows
    key = ["method", "object", "target", "horizon_q", "prior_basis", "spec_id"]
    for col, flag in (("survives_both_windows", "beats_seasonal_naive"),
                      ("rw_survives_both_windows", "rw_beats_seasonal_naive")):
        w1 = sb[sb["window"] == "W1"].set_index(key)[flag]
        w2 = sb[sb["window"] == "W2"].set_index(key)[flag]
        both = {k_: bool(w1.get(k_, False)) and bool(w2.get(k_, False)) for k_ in set(w1.index) | set(w2.index)}
        sb[col] = [both.get(tuple(r[c] for c in key), False) for _, r in sb.iterrows()]
    rp = sb.groupby(["method", "object", "target", "horizon_q", "spec_id"])["prior_basis"].nunique().rename("replays_present")
    sb = sb.merge(rp, on=["method", "object", "target", "horizon_q", "spec_id"], how="left")
    # WS22 (R09): the baselines put prior_basis INSIDE spec_id, so the group key above splits their two
    # replays and `replays_present` reads 1 for every baseline row. Recomputed here with that suffix
    # stripped, as a NEW column; `replays_present` itself is left exactly as it was.
    sb["_spec_base"] = sb["spec_id"].astype(str).str.replace(r"\|(PIT|full_sample)$", "", regex=True)
    rp2 = (sb.groupby(["method", "object", "target", "horizon_q", "_spec_base"])["prior_basis"]
             .nunique().rename("replays_present_fixed"))
    sb = sb.merge(rp2, on=["method", "object", "target", "horizon_q", "_spec_base"], how="left").drop(columns="_spec_base")
    sb = SIG.add_window_flags(sb)
    sb = SIG.mark_oracle(sb)
    sb = sb.sort_values(["target", "window", "horizon_q", "prior_basis", "mae"]).reset_index(drop=True)
    by_q_cols = GROUP_KEYS + ["quarter", "vintage_date", "point", "actual", "err", "abs_err", "crps", "pinball",
                              "in80", "in90", "pit", "weight_rw", "seasonal_naive_point", "seasonal_naive_abs_err",
                              "n_params", "_source_file"]
    by_q = rows[[c for c in by_q_cols if c in rows.columns]].sort_values(GROUP_KEYS + ["quarter"]).reset_index(drop=True)
    return sb, by_q


# ----------------------------------------------------------------------------- markdown
_MD_TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd", "cor_cash_pct_rev", "ops_cash_pct_rev",
               "pd_cash_pct_rev", "sm_cash_pct_rev", "ga_cash_pct_rev", "sbc_pct_rev", "op_margin_pct",
               "eps_diluted", "fcf_margin_pct"]


def _fmt(x, nd=2):
    return "" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:,.{nd}f}"


def scoreboard_md(sb: pd.DataFrame, title="Margin harness scoreboard") -> str:
    lines = [f"# {title}", "",
             f"Registry FORMAT v{FORMAT_VERSION}; margin harness `10_harness_margin`. Built {TODAY} (validator TODAY). "
             "LIVE rows enter no metric. `mae_ratio_seasonal_naive` < 1 beats y[q-4] on the same target, window, "
             "horizon and replay; a claim must have `survives_both_windows` (equal-weighted) AND "
             "`rw_survives_both_windows` (recency-weighted, half-life 4 quarters) to be quoted.", "",
             "**WS22 amendment (WS21 R01/R02/R08).** Those two flags are NOT evidence of skill on their "
             "own: W2's 10 quarters are a subset of W1's 14, the two weightings are highly correlated, and "
             "a sign-flip null over the 74 margin h=0 PIT cells gives 22.1 survivors on average against 25 "
             "observed (P 0.39). They are also asserted on as few as 2 matched quarters. Quote a result as "
             "`beats <baseline> by d, better in k of n quarters, sign-test p` using the new columns "
             "`d_mean_*`, `k_better_*`, `p_sign_*`, `t_nw1_*`, `p_nw1_*` (vs `seasonal_naive` and vs "
             "`street`), and filter on `survives_both_windows_n8` / `survives_both_windows_sig` rather than "
             "on the raw flags. `p_sn` below is `p_sign_seasonal_naive`, `k/n` the quarters-better count.", "",
             "> " + M.EXCHANGEABILITY_CAVEAT, ""]
    if len(sb) == 0:
        lines.append("_(registry empty)_")
        return "\n".join(lines)
    cols = ["method", "object", "window", "h", "replay", "n", "mae", "rw_mae", "rmse", "bias", "rw_bias",
            "r_sn", "rw_r_sn", "r_street", "k/n", "p_sn", "p_street", "crps", "cov80", "n_params",
            "both", "rw_both"]
    for tgt in [t for t in _MD_TARGETS if t in set(sb["target"])] + \
            sorted(set(sb["target"]) - set(_MD_TARGETS)):
        g = sb[sb["target"] == tgt]
        lines += [f"## target: `{tgt}`", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        for _, r in g.iterrows():
            vals = [r["method"], r["object"], r["window"], str(r["horizon_q"]), r["prior_basis"], str(r["n"]),
                    _fmt(r["mae"]), _fmt(r["rw_mae"]), _fmt(r["rmse"]), _fmt(r["bias"]), _fmt(r["rw_bias"]),
                    _fmt(r.get("mae_ratio_seasonal_naive"), 3), _fmt(r.get("rw_mae_ratio_seasonal_naive"), 3),
                    _fmt(r.get("mae_ratio_street"), 3),
                    (f"{int(r['k_better_seasonal_naive'])}/{int(r['n_cmp_seasonal_naive'])}"
                     if pd.notna(r.get("k_better_seasonal_naive")) else ""),
                    _fmt(r.get("p_sign_seasonal_naive"), 3), _fmt(r.get("p_sign_street"), 3),
                    _fmt(r["crps"]), _fmt(r["cov80"], 2),
                    str(r["n_params"]), str(r["survives_both_windows"]), str(r["rw_survives_both_windows"])]
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
    return "\n".join(lines)


_SUMMARY_TARGETS = ["adj_ebitda_margin_pct", "adj_ebitda_musd", "cor_cash_musd", "ops_cash_musd", "pd_cash_musd",
                    "sm_cash_musd", "ga_cash_musd", "cor_cash_pct_rev", "ops_cash_pct_rev", "pd_cash_pct_rev",
                    "sm_cash_pct_rev", "ga_cash_pct_rev", "cor_cash_per_night", "ops_cash_per_night",
                    "pd_cash_per_night", "sm_cash_per_night", "ga_cash_per_night", "sbc_musd", "sbc_pct_rev",
                    "da_musd", "op_income_musd", "op_margin_pct", "net_income_musd", "eps_diluted", "fcf_musd",
                    "fcf_margin_pct", "interest_income_musd", "tax_rate_pct", "diluted_shares_m"]


def hardest_baseline_table(sb: pd.DataFrame) -> pd.DataFrame:
    """Per (target, window, horizon): the baseline object with the lowest MAE, equal- and
    recency-weighted, from the PIT replay of `baselines-margin`; the seasonal-naive MAE alongside."""
    b = sb[(sb["method"] == P.BASELINE_METHOD) & (sb["prior_basis"] == "PIT")]
    rows = []
    for (t, w, h), g in b[b["target"].isin(_SUMMARY_TARGETS)].groupby(["target", "window", "horizon_q"]):
        ew = g.sort_values("mae").iloc[0]
        rw = g.sort_values("rw_mae").iloc[0]
        sn = g[g["object"] == PRIMARY_BASELINE]
        rows.append({"target": t, "window": w, "horizon_q": int(h), "n": int(ew["n"]),
                     "hardest_ew": ew["object"], "mae_ew": ew["mae"],
                     "hardest_rw": rw["object"], "rw_mae": rw["rw_mae"],
                     "seasonal_naive_mae_ew": float(sn["mae"].iloc[0]) if len(sn) else np.nan,
                     "seasonal_naive_mae_rw": float(sn["rw_mae"].iloc[0]) if len(sn) else np.nan,
                     "weightings_agree": ew["object"] == rw["object"]})
    out = pd.DataFrame(rows)
    out["target"] = pd.Categorical(out["target"], _SUMMARY_TARGETS)
    return out.sort_values(["target", "window", "horizon_q"]).reset_index(drop=True)


def hardest_baseline_md(hb: pd.DataFrame) -> str:
    lines = ["# Which baseline is hardest to beat (method `baselines-margin`, PIT replay)", "",
             "Lowest MAE per target / window / horizon, equal-weighted (ew) and recency-weighted "
             "(rw, half-life 4 quarters anchored at 2026Q2). `seasonal_naive` MAE shown for scale. "
             "Units: the target's own (pp for %, USD m for _musd, USD/night for _per_night).", "",
             "| target | window | h | n | hardest (ew) | MAE ew | hardest (rw) | MAE rw | naive ew | naive rw | agree |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in hb.iterrows():
        lines.append(f"| {r['target']} | {r['window']} | {r['horizon_q']} | {r['n']} | {r['hardest_ew']} | "
                     f"{_fmt(r['mae_ew'], 3)} | {r['hardest_rw']} | {_fmt(r['rw_mae'], 3)} | "
                     f"{_fmt(r['seasonal_naive_mae_ew'], 3)} | {_fmt(r['seasonal_naive_mae_rw'], 3)} | "
                     f"{'yes' if r['weightings_agree'] else 'NO'} |")
    return "\n".join(lines) + "\n"


def main(verbose: bool = True) -> int:
    P.ensure_dirs()
    reg = load_registry()
    n_obj = reg[["method", "object"]].drop_duplicates().shape[0] if len(reg) else 0
    print(f"margin registry: {len(reg)} rows across {n_obj} objects in {P.REGISTRY_DIR.relative_to(P.REPO_ROOT)}")
    sb, by_q = score_registry(reg)
    sb.to_csv(P.OUT_SCOREBOARD, index=False)
    by_q.to_csv(P.OUT_BY_QUARTER, index=False)
    P.OUT_SCOREBOARD_MD.write_text(scoreboard_md(sb), encoding="utf-8")
    if len(sb):
        hb = hardest_baseline_table(sb)
        hb.to_csv(P.OUT_HARDEST, index=False)
        P.OUT_BASELINE_TABLE.write_text(hardest_baseline_md(hb), encoding="utf-8")
    print(f"scoreboard: {len(sb)} rows -> {P.OUT_SCOREBOARD.name}, {P.OUT_SCOREBOARD_MD.name}; "
          f"by_quarter: {len(by_q)} rows -> {P.OUT_BY_QUARTER.name}")
    if verbose and len(sb):
        show = ["method", "object", "window", "horizon_q", "prior_basis", "n", "mae", "rw_mae",
                "mae_ratio_seasonal_naive", "rw_mae_ratio_seasonal_naive", "cov80", "survives_both_windows"]
        x = sb[(sb["target"] == "adj_ebitda_margin_pct") & (sb["horizon_q"] == 0) & (sb["prior_basis"] == "PIT")]
        with pd.option_context("display.width", 250, "display.max_columns", 30):
            print(x[show].to_string(index=False))
    return 0
