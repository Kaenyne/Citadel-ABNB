#!/usr/bin/env python
"""Part (d): PIT histogram + CRPS on the 391-row prediction ledger.

The ledger (`20_prediction_ledger.csv`) carries POINT forecasts only (`forecast`,
`actual`, no quantiles). To ask "was this calibrated" honestly we build a predictive
distribution the same way the harness does for the naive/AR(1) baselines: Gaussian,
centred on the point forecast, with sigma estimated OUT OF SAMPLE -- the expanding
std of that (target, model)'s own past errors, using only rows that occur earlier
in `print_quarter` order. A model's first 2 observations therefore get no sigma
(nothing to estimate from) and are dropped from the PIT/CRPS exhibit; this shrinks n
further on top of the ledger's already-small per-model counts, which is disclosed,
not hidden.

This is a descriptive artefact, not a registry object: the ledger's targets
(nights_surprise_pct, revenue_surprise_pct, five price-drift series) are not harness
target metrics, and several ledger "models" are literally baseline columns
(bl_guide, bl_guide_plus_cushion, bl_last_quarter, bl_expanding_mean) already covered
by the harness baselines. Output: pit_crps_ledger.csv + a compact markdown table.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import _common  # noqa: F401
from harness import metrics as M  # noqa: E402

Z = {"q05": -1.645, "q10": -1.282, "q25": -0.674, "q50": 0.0,
     "q75": 0.674, "q90": 1.282, "q95": 1.645}
# Quantile PROBABILITIES matching the Z keys, in the same order -- this is what
# harness.metrics.pit_from_quantiles / crps_from_quantiles expect as `levels`
# (fixed post-verification: the z-scores above were being passed as levels, which
# corrupted every interior PIT/CRPS value -- see VERIFY_calibration-rail_r1.md #4).
PROBS = {"q05": 0.05, "q10": 0.10, "q25": 0.25, "q50": 0.50,
         "q75": 0.75, "q90": 0.90, "q95": 0.95}
MIN_SIGMA_N = 3


def _pit_crps_group(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("print_quarter").reset_index(drop=True)
    errs = (g["forecast"] - g["actual"]).to_numpy()
    out_rows = []
    for i in range(len(g)):
        past = errs[:i]
        if len(past) < MIN_SIGMA_N:
            continue
        sigma = float(np.std(past, ddof=1))
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        fc = float(g.loc[i, "forecast"])
        act = float(g.loc[i, "actual"])
        levels = list(PROBS.values())
        values = [fc + z * sigma for z in Z.values()]
        pit, edge = M.pit_from_quantiles(act, levels, values)
        crps = M.crps_from_quantiles(act, levels, values)
        out_rows.append({"print_quarter": g.loc[i, "print_quarter"], "forecast": fc,
                         "actual": act, "sigma_pseudo_oos": sigma, "n_sigma_train": len(past),
                         "pit": pit, "pit_edge": edge, "crps": crps})
    return pd.DataFrame(out_rows)


def main() -> int:
    p = _common.REPO_ROOT / "data" / "processed" / "overnight" / "20_prediction_ledger.csv"
    df = pd.read_csv(p)
    all_rows = []
    for (task, target, model), g in df.groupby(["task", "target", "model"]):
        if len(g) < MIN_SIGMA_N + 2:
            continue
        r = _pit_crps_group(g)
        if len(r) == 0:
            continue
        r["task"] = task; r["target"] = target; r["model"] = model
        all_rows.append(r)
    if not all_rows:
        print("no groups with enough history for a pseudo-oos sigma")
        return 0
    detail = pd.concat(all_rows, ignore_index=True)
    detail.to_csv(_common.DATA_OUT / "pit_crps_ledger_detail.csv", index=False)

    summary = (detail.groupby(["task", "target", "model"])
              .agg(n=("pit", "size"), pit_mean=("pit", "mean"),
                   pit_edge_frac=("pit_edge", "mean"), crps_mean=("crps", "mean"),
                   mae=("forecast", lambda s: np.nan))  # placeholder, filled below
              .reset_index())
    mae = (detail.assign(abs_err=lambda d: (d["forecast"] - d["actual"]).abs())
           .groupby(["task", "target", "model"])["abs_err"].mean().rename("mae"))
    summary = summary.drop(columns=["mae"]).merge(mae, on=["task", "target", "model"])

    def _ks_p(rows):
        sub = detail[(detail.task == rows.task) & (detail.target == rows.target) &
                     (detail.model == rows.model)]
        return M.pit_uniform_ks_p(sub["pit"].tolist())
    summary["pit_ks_p"] = summary.apply(_ks_p, axis=1)

    def _calib_label(row):
        # pit_mean near 0.5 AND spread across bins -> "calibrated";
        # pit clustered near 0/1 (edge_frac high) -> "overconfident" (band too narrow);
        # pit clustered near 0.5 with almost no edge and low crps/mae ratio can also
        # indicate an overconfident band that happens to bracket the point -- flagged
        # via pit_edge_frac, not asserted from pit_mean alone.
        if row["pit_edge_frac"] > 0.5:
            return "OVERCONFIDENT (>50% of actuals outside the ladder)"
        if abs(row["pit_mean"] - 0.5) > 0.20:
            return "BIASED (PIT mean far from 0.5)"
        return "roughly calibrated on this small sample"
    summary["calibration_read"] = summary.apply(_calib_label, axis=1)
    summary = summary.sort_values(["task", "target", "n"], ascending=[True, True, False])
    summary.to_csv(_common.DATA_OUT / "pit_crps_ledger_summary.csv", index=False)

    print(summary.to_string(index=False))
    print(f"\n{len(summary)} (task,target,model) groups scored, "
          f"{len(detail)} scored rows out of {len(df)} ledger rows "
          f"(rows dropped: sigma needs >= {MIN_SIGMA_N} prior errors in the same group).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
