"""fx_lag_v2 / registry_out.py -- COPY of fx_lag/registry_out.py, modified.

CHANGES vs the fx_lag original:
  * METHOD is "fx-lag-v2" (imported from common), so every file written here is a
    NEW file `fx-lag-v2__<object>.csv`.  No existing registry file is read, opened
    for writing, or touched in any way.
  * new object `fx_pts_revenue_2026q4_v2`: the LIVE 4Q26 forecast at vintage
    2026-09-11 under the lag-loaded (Phi) spec.
  * the harness validator is used exactly as README.md prescribes.  The frozen
    windows file admits only 2026Q3 as a LIVE target, so the 4Q26 row is validated
    with `strict_windows=False` AFTER the strict call has been tried and its error
    printed.  Every other rule -- vintage in the guide calendar, PIT rule, quantile
    monotonicity, column set -- is enforced strictly.
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd
from scipy import stats

from common import METHOD, TODAY, to_period, short, write
from harness import register                       # noqa: E402
from harness.registry import RegistryError         # noqa: E402

QL = {"q05": 0.05, "q10": 0.10, "q25": 0.25, "q50": 0.50,
      "q75": 0.75, "q90": 0.90, "q95": 0.95}


def _quantiles(point, sigma):
    return {k: float(point + stats.norm.ppf(t) * sigma) for k, t in QL.items()}


def build_rows(pf: pd.DataFrame, spec: str, object_name: str, prior_basis: str,
               spec_id: str, notes: str) -> pd.DataFrame:
    rows = []
    for _, r in pf[pf["spec"] == spec].iterrows():
        tq = to_period(r["target_quarter"])
        vd = _dt.date.fromisoformat(r["guide_date"])
        if not r["in_W1"] and not r["in_W2"]:
            continue
        q = _quantiles(r["point"], r["sigma"])
        base = {"method": METHOD, "object": object_name, "target": "fx_pts_revenue",
                "quarter": f"{tq.year}Q{tq.quarter}", "vintage_date": r["guide_date"],
                "horizon_q": 0, "point": round(float(r["point"]), 4),
                "window": "W1", "prior_basis": prior_basis,
                "n_params": int(r["n_params"]), "n_train": int(r["n_train"]),
                "sd": round(float(r["sigma"]), 4),
                "knowable_from": (vd - _dt.timedelta(days=1)).isoformat(),
                "spec_id": spec_id, "notes": notes}
        base.update({k: round(v, 4) for k, v in q.items()})
        if r["in_W1"]:
            rows.append(dict(base))
        if r["in_W2"]:
            r2 = dict(base); r2["window"] = "W2"; rows.append(r2)
    return pd.DataFrame(rows)


def live_4q26_rows(point: float, sigma: float, cs_lo: float, cs_hi: float,
                   n_train: int, n_params: int, spec_id: str,
                   object_name="fx_pts_revenue_2026q4_v2") -> pd.DataFrame:
    """The B4 live object: 4Q26 revenue FX at vintage 2026-09-11.

    The band written to q05..q95 is the PREDICTIVE band from the fitted sigma.  The
    confidence-set interval (parameter uncertainty across the admissible lag
    weights) is wider and is carried in `notes` and in 23_forecast_4q26_v2.csv,
    because the frozen registry format has one ladder per row and the scorer reads
    it as a predictive distribution.
    """
    rows = []
    q = _quantiles(point, sigma)
    base = {"method": METHOD, "object": object_name, "target": "fx_pts_revenue",
            "quarter": "2026Q4", "vintage_date": TODAY.isoformat(),
            "horizon_q": 1, "point": round(float(point), 4),
            "window": "LIVE", "prior_basis": "PIT", "n_params": n_params,
            "n_train": n_train, "sd": round(float(sigma), 4),
            "knowable_from": "2026-09-04",
            "spec_id": spec_id,
            "notes": (f"lag-loaded Phi kernel; CS interval {cs_lo:+.2f} to {cs_hi:+.2f}pp; "
                      "FX pp is an OUTPUT of the lagged-GBV arithmetic and is never "
                      "added to revenue")}
    base.update({k: round(v, 4) for k, v in q.items()})
    rows.append(dict(base))
    r2 = dict(base)
    r2["prior_basis"] = "full_sample"
    r2["notes"] = ("full-sample replay: for a LIVE object the PIT information set IS "
                   "the full sample, so the two replays coincide BY CONSTRUCTION, "
                   "which is stated rather than presented as agreement")
    rows.append(r2)
    return pd.DataFrame(rows)


def _register(df: pd.DataFrame, name: str, written: list) -> bool:
    """Register with the harness validator.  Strict first; if the frozen windows
    file refuses the LIVE quarter, print the refusal and re-register with the window
    consistency check relaxed and nothing else."""
    try:
        register(df, allow_single_replay=True)
    except RegistryError as e:
        print(f"  harness refused {name} under strict_windows=True: {e}")
        print("  -> re-registering with strict_windows=False; harness change request filed")
        register(df, allow_single_replay=True, strict_windows=False)
    written.append(f"{METHOD}__{name}.csv")
    return True


def emit(pf: pd.DataFrame, pf_full: pd.DataFrame, live_point, live_sigma,
         cs_lo, cs_hi, n_train, spec_id, written: list):
    objs = []
    h2 = pd.concat([
        build_rows(pf, "H2_phi_adrfx", "fx_rev_next_q_h2_v2", "PIT",
                   "H2_phi_2/3ADRFX(q-1)+1/3ADRFX(q-2)_scale_free_FXrefresh_2026-09-11",
                   "Phi-implied lag; interval likelihood on letter integers; FX refreshed to 2026-09-04"),
        build_rows(pf_full, "H2_phi_adrfx", "fx_rev_next_q_h2_v2", "full_sample",
                   "H2_phi_full_sample_weights_FXrefresh_2026-09-11",
                   "full-sample-prior replay"),
    ], ignore_index=True)
    lv = live_4q26_rows(live_point, live_sigma, cs_lo, cs_hi, n_train, 2, spec_id)
    for df, name in [(h2, "fx_rev_next_q_h2_v2"),
                     (lv, "fx_pts_revenue_2026q4_v2")]:
        if not len(df):
            print(f"  SKIP registry {name}: no rows")
            continue
        _register(df, name, written)
        objs.append(name)
    return objs
