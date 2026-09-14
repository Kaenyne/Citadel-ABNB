#!/usr/bin/env python
"""Part (a): reference scoreboard rows + claim-confirmation exhibits.

The harness's own `build_all_baselines()` only covers 4 target metrics
(revenue_musd, revenue_yoy, gbv_musd, nights_m) because that is what
`baselines.BASELINE_SPECS` lists. calibration-rail needs the SAME five
baselines on nights_yoy, adr_yoy, gbv_yoy and take_rate_pct too, so every
other package has a denominator for those targets. The harness's baseline
functions (`baseline_naive`, `baseline_ar1`, `baseline_trailing4`) are
metric-agnostic -- they take `metric=` as an argument -- so this is a
legitimate re-use, not a re-implementation. See the harness change request
at the bottom of the package note.

Also reproduces, from data already on disk, the two ground-truth claims:
  1. guide + trailing-8 cushion prices revenue LEVEL to ~1.1% MAPE.
  2. guide (+cushion) is the WORST predictor of "surprise vs Street"
     (a target the ledger already carries as `revenue_surprise_pct`).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import _common  # noqa: F401  (sets sys.path)
from harness import (  # noqa: E402
    load_targets, load_registry, register, windows as W, quarters as Q,
    baseline_naive, baseline_ar1, baseline_trailing4,
)

EXTRA_METRICS = ["nights_yoy", "adr_yoy", "gbv_yoy", "take_rate_pct"]
FN_BY_OBJECT = {"ref_naive": baseline_naive, "ref_ar1": baseline_ar1,
                "ref_trailing4": baseline_trailing4}
N_PARAMS = {"ref_naive": 0, "ref_ar1": 2, "ref_trailing4": 1}


def build_extra_baselines(t: pd.DataFrame) -> dict:
    frames = {}
    for obj, fn in FN_BY_OBJECT.items():
        rows = []
        for gdate, tq in W.GUIDE_EVENTS_ALL:
            wins = W.window_of_target(tq)
            if not wins:
                continue
            for metric in EXTRA_METRICS:
                for basis in ("PIT", "full_sample"):
                    r = fn(gdate, tq, metric=metric, prior_basis=basis, targets=t)
                    if r is None:
                        continue
                    for win in wins:
                        row = {"method": "calibration-rail", "object": obj,
                               "target": metric, "quarter": tq, "vintage_date": gdate,
                               "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(gdate)),
                               "window": win, "prior_basis": basis,
                               "spec_id": f"{obj}|{metric}|{basis}|harness_fn_direct_call",
                               "notes": "reference row; extends harness baseline coverage "
                                        "to a target the harness's own BASELINE_SPECS omits"}
                        row.update(r)
                        rows.append(row)
        if rows:
            frames[obj] = pd.DataFrame(rows)
    return frames


def confirm_claim_level_mape(t: pd.DataFrame) -> dict:
    """Claim 1: guide + trailing-8 cushion prices revenue LEVEL to ~1.1% MAPE."""
    reg = load_registry(method="baselines", object_="guide_cushion")
    act = t[["quarter", "revenue_musd"]].rename(columns={"revenue_musd": "actual"})
    m = reg.merge(act, on="quarter").dropna(subset=["actual"])
    out = {}
    for basis in ("PIT", "full_sample"):
        d = m[m.prior_basis == basis]
        mape = float((np.abs(d["point"] - d["actual"]) / d["actual"]).mean() * 100)
        out[basis] = {"n": int(d["quarter"].nunique()), "mape_pct": mape}
    return out


def confirm_claim_worst_on_surprise() -> dict:
    """Claim 2: guide(+cushion) is the WORST predictor of surprise vs Street.

    Uses the existing 391-row prediction ledger's Task A, target
    `revenue_surprise_pct`, where `bl_guide` / `bl_guide_plus_cushion` are
    already-computed baseline columns alongside `bl_zero` (predict-no-surprise)
    and `bl_last_quarter`.
    """
    from _common import REPO_ROOT
    p = REPO_ROOT / "data" / "processed" / "overnight" / "20_prediction_ledger.csv"
    df = pd.read_csv(p)
    sub = df[(df.task == "A_pre_earnings_forecast") & (df.target == "revenue_surprise_pct")]
    out = {}
    for col in ("bl_zero", "bl_last_quarter", "bl_expanding_mean", "bl_guide",
                "bl_guide_plus_cushion"):
        d = sub.dropna(subset=[col, "actual"])
        if len(d) == 0:
            continue
        err = d[col] - d["actual"]
        out[col] = {"n": int(len(d)), "rmse": float(np.sqrt((err ** 2).mean())),
                     "mae": float(err.abs().mean())}
    return out


def main() -> int:
    t = load_targets()
    frames = build_extra_baselines(t)
    for obj, df in frames.items():
        register(df, allow_single_replay=False, quiet=False)

    claim1 = confirm_claim_level_mape(t)
    claim2 = confirm_claim_worst_on_surprise()

    rows = []
    for basis, d in claim1.items():
        rows.append({"claim": "guide+cushion revenue LEVEL ~1.1pct mean error",
                     "series": "guide_cushion", "prior_basis": basis, **d})
    for col, d in claim2.items():
        rows.append({"claim": "guide(+cushion) worst predictor of surprise vs Street",
                     "series": col, "prior_basis": "n/a (ledger, historical)", **d})
    out = pd.DataFrame(rows)
    out.to_csv(_common.DATA_OUT / "claims_confirmation.csv", index=False)
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
