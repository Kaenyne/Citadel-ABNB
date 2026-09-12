#!/usr/bin/env python
"""Scorer: registry -> full metric block -> scoreboard.csv + scoreboard.md.

Run:
  /Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from harness import paths as P
    from harness import quarters as Q
    from harness import metrics as M
    from harness.registry import load_registry, QUANTILE_COLUMNS, QUANTILE_LEVELS
    from harness.loaders import load_targets
else:
    from . import paths as P
    from . import quarters as Q
    from . import metrics as M
    from .registry import load_registry, QUANTILE_COLUMNS, QUANTILE_LEVELS
    from .loaders import load_targets

GROUP_KEYS = ["method", "object", "target", "window", "prior_basis"]
NAIVE_METHOD, NAIVE_OBJECT = "baselines", "naive"


def _actuals() -> pd.DataFrame:
    t = load_targets()
    long = []
    for c in t.columns:
        if c in ("quarter", "print_date", "guide_date", "guide_issued_on",
                 "street_pre_guide_vendor", "street_pre_guide_as_of",
                 "cons_at_print_vendor", "has_actual"):
            continue
        v = pd.to_numeric(t[c], errors="coerce")
        for q, x, pdte in zip(t["quarter"], v, t["print_date"]):
            if pd.notna(x) and pd.notna(pdte):
                long.append({"quarter": q, "target": c, "actual": float(x)})
    return pd.DataFrame(long)


def _row_quantiles(row):
    levels, values = [], []
    for c in QUANTILE_COLUMNS:
        v = row.get(c)
        if v is not None and pd.notna(v):
            levels.append(QUANTILE_LEVELS[c]); values.append(float(v))
    return levels, values


def score_registry(reg: pd.DataFrame = None, n_cal: int = 6, alpha: float = 0.2) -> pd.DataFrame:
    reg = load_registry() if reg is None else reg
    if len(reg) == 0:
        return pd.DataFrame()
    act = _actuals()
    d = reg.merge(act, on=["quarter", "target"], how="left")
    d = d[d["window"].astype(str).str.upper() != "LIVE"].copy()
    d = d.dropna(subset=["actual"])
    if len(d) == 0:
        return pd.DataFrame()
    d = d.sort_values(GROUP_KEYS + ["quarter"]).reset_index(drop=True)

    # naive denominator, matched on (target, window, prior_basis, quarter)
    nai = d[(d["method"] == NAIVE_METHOD) & (d["object"] == NAIVE_OBJECT)]
    nai_map = {}
    for r in nai.itertuples():
        nai_map[(r.target, r.window, r.prior_basis, r.quarter)] = float(r.point)

    rows = []
    for keys, g in d.groupby(GROUP_KEYS, sort=True):
        method, obj, target, window, basis = keys
        g = g.sort_values("quarter")
        y = g["actual"].to_numpy(dtype=float)
        p = pd.to_numeric(g["point"], errors="coerce").to_numpy(dtype=float)
        err = p - y
        n = len(y)
        mae = float(np.mean(np.abs(err)))
        rmse = float(np.sqrt(np.mean(err ** 2)))
        bias = float(np.mean(err))
        with np.errstate(divide="ignore", invalid="ignore"):
            mape = float(np.mean(np.abs(err / np.where(y == 0, np.nan, y)))) * 100.0

        nd = np.array([nai_map.get((target, window, basis, q), np.nan)
                       for q in g["quarter"]], dtype=float)
        ok = np.isfinite(nd)
        rmse_naive = float(np.sqrt(np.mean((nd[ok] - y[ok]) ** 2))) if ok.sum() >= 2 else np.nan
        ratio = rmse / rmse_naive if (np.isfinite(rmse_naive) and rmse_naive > 0) else np.nan

        crps, pits, edges = [], [], 0
        lo_arr, hi_arr, cov_label, cov_nom = [], [], None, np.nan
        for _, r in g.iterrows():
            lv, vv = _row_quantiles(r)
            yy = float(r["actual"])
            crps.append(M.crps_from_quantiles(yy, lv, vv) if lv else abs(yy - float(r["point"])))
            pv, edge = M.pit_from_quantiles(yy, lv, vv)
            pits.append(pv); edges += int(edge)
            if pd.notna(r.get("q10")) and pd.notna(r.get("q90")):
                lo_arr.append(float(r["q10"])); hi_arr.append(float(r["q90"]))
                cov_label, cov_nom = "q10-q90", 0.80
            elif pd.notna(r.get("q05")) and pd.notna(r.get("q95")):
                lo_arr.append(float(r["q05"])); hi_arr.append(float(r["q95"]))
                cov_label, cov_nom = "q05-q95", 0.90
            else:
                lo_arr.append(np.nan); hi_arr.append(np.nan)
        lo_arr, hi_arr = np.asarray(lo_arr), np.asarray(hi_arr)
        m = np.isfinite(lo_arr) & np.isfinite(hi_arr)
        cov_emp = float(np.mean((y[m] >= lo_arr[m]) & (y[m] <= hi_arr[m]))) if m.any() else np.nan

        pinball = []
        for _, r in g.iterrows():
            lv, vv = _row_quantiles(r)
            if lv:
                pinball.append(np.mean([M.pinball_loss(float(r["actual"]), v, t)
                                        for v, t in zip(vv, lv)]))
        hist = M.pit_histogram(pits, 5)
        conf_cov, conf_n, conf_w = M.rolling_split_conformal(y, p, n_cal=n_cal, alpha=alpha)
        k, att_lo, att_hi = M.attainable_coverage(n_cal, alpha)
        n_params = int(pd.to_numeric(g["n_params"], errors="coerce").max())

        rows.append({
            "method": method, "object": obj, "target": target, "window": window,
            "prior_basis": basis, "n": n,
            "first_quarter": g["quarter"].iloc[0], "last_quarter": g["quarter"].iloc[-1],
            "mae": mae, "rmse": rmse, "bias": bias, "mape_pct": mape,
            "rmse_naive": rmse_naive, "rmse_ratio_to_naive": ratio,
            "beats_naive": bool(np.isfinite(ratio) and ratio < 1.0),
            "crps": float(np.mean(crps)) if crps else np.nan,
            "pinball_mean": float(np.mean(pinball)) if pinball else np.nan,
            "pit_mean": (float(np.nanmean(pits))
                         if any(np.isfinite(x) for x in pits) else np.nan),
            "pit_ks_p": M.pit_uniform_ks_p(pits),
            "pit_edge_frac": edges / n if n else np.nan,
            "pit_bin_1": hist[0], "pit_bin_2": hist[1], "pit_bin_3": hist[2],
            "pit_bin_4": hist[3], "pit_bin_5": hist[4],
            "cov_interval": cov_label, "cov_nominal": cov_nom, "cov_empirical": cov_emp,
            "conformal_n_cal": n_cal, "conformal_alpha": alpha, "conformal_k": k,
            "conformal_n_eval": conf_n, "conformal_cov_empirical": conf_cov,
            "conformal_mean_width": conf_w,
            "conformal_attainable_lo": att_lo, "conformal_attainable_hi": att_hi,
            "n_params": n_params, "n_obs": n,
            "param_obs_ratio": n_params / n if n else np.nan,
            "coverage_caveat": M.EXCHANGEABILITY_CAVEAT,
        })

    sb = pd.DataFrame(rows)
    if len(sb) == 0:
        return sb
    key = ["method", "object", "target", "prior_basis"]
    w1 = sb[sb["window"] == "W1"].set_index(key)["beats_naive"]
    w2 = sb[sb["window"] == "W2"].set_index(key)["beats_naive"]
    both = {}
    for k_ in set(w1.index) | set(w2.index):
        both[k_] = bool(w1.get(k_, False)) and bool(w2.get(k_, False))
    sb["survives_both_windows"] = [both.get(tuple(r[c] for c in key), False)
                                   for _, r in sb.iterrows()]
    rp = (sb.groupby(["method", "object", "target"])["prior_basis"]
            .nunique().rename("replays_present"))
    sb = sb.merge(rp, on=["method", "object", "target"], how="left")
    return sb.sort_values(["target", "window", "prior_basis", "rmse"]).reset_index(drop=True)


def _md(sb: pd.DataFrame) -> str:
    lines = ["# Harness scoreboard", "",
             f"Format v{P.FORMAT_VERSION}. Built {P.TODAY}. LIVE rows are excluded by "
             "construction: the 2026-08-06 guide enters no metric.", "",
             "`rmse_ratio_to_naive` < 1 beats the naive rule "
             "(`y[q-4] * (1 + last observed y/y growth)`) on the same series, same "
             "window, same replay. A result must have `survives_both_windows` = True "
             "to be quoted.", ""]
    lines.append("> " + M.EXCHANGEABILITY_CAVEAT)
    lines.append("")
    if len(sb) == 0:
        lines.append("_(registry empty)_")
        return "\n".join(lines)
    cols = ["method", "object", "window", "prior_basis", "n", "mae", "rmse", "bias",
            "rmse_ratio_to_naive", "crps", "cov_nominal", "cov_empirical",
            "conformal_cov_empirical", "n_params", "param_obs_ratio",
            "survives_both_windows"]
    for tgt, g in sb.groupby("target"):
        lines += [f"## target: `{tgt}`", ""]
        h = g[cols].copy()
        for c in ("mae", "rmse", "bias", "crps"):
            h[c] = h[c].map(lambda x: f"{x:,.1f}" if pd.notna(x) else "")
        for c in ("rmse_ratio_to_naive", "cov_empirical", "conformal_cov_empirical",
                  "param_obs_ratio", "cov_nominal"):
            h[c] = h[c].map(lambda x: f"{x:.3f}" if pd.notna(x) else "")
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("|" + "---|" * len(cols))
        for _, r in h.iterrows():
            lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        lines.append("")
    k, lo, hi = M.attainable_coverage(6, 0.2)
    lines += ["## Attainable conformal coverage", "",
              f"At `n_cal=6`, `alpha=0.2`: `k = ceil(7 x 0.8) = {k}`, so `qhat` is the "
              f"**maximum** of six residuals and attainable coverage lies in "
              f"[{lo:.3f}, {hi:.3f}] = [{lo*100:.1f}%, {hi*100:.1f}%]. "
              "There is no 80% guarantee at this sample size. Full grid: "
              "`conformal_attainable_grid.csv`.", ""]
    return "\n".join(lines)


def main() -> int:
    P.ensure_dirs()
    pd.DataFrame(M.attainable_coverage_grid()).to_csv(P.OUT_CONFORMAL_GRID, index=False)
    reg = load_registry()
    print(f"registry: {len(reg)} rows across "
          f"{reg[['method','object']].drop_duplicates().shape[0] if len(reg) else 0} objects")
    sb = score_registry(reg)
    sb.to_csv(P.OUT_SCOREBOARD, index=False)
    P.OUT_SCOREBOARD_MD.write_text(_md(sb))
    print(f"scoreboard: {len(sb)} rows -> {P.OUT_SCOREBOARD.name}, {P.OUT_SCOREBOARD_MD.name}")
    if len(sb):
        show = ["object", "target", "window", "prior_basis", "n", "rmse",
                "rmse_ratio_to_naive", "cov_empirical", "survives_both_windows"]
        print(sb[sb["target"] == "revenue_musd"][show].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
