"""fx_lag / registry_out.py -- register forecast objects in the FROZEN v1.0 format."""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd
from scipy import stats

from common import METHOD, TODAY, to_period, short, write
from harness import register  # noqa: E402

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
        win = "W1" if r["in_W1"] else ("W2" if r["in_W2"] else None)
        if r["in_W2"]:
            win = "W2" if not r["in_W1"] else "W1"
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
        rows.append(dict(base))
        if r["in_W2"]:
            r2 = dict(base); r2["window"] = "W2"; rows.append(r2)
    return pd.DataFrame(rows)


def live_rows(a_hat, sigma, fwd: pd.DataFrame, n_train: int, n_params: int,
              object_name="live_fx_schedule") -> pd.DataFrame:
    rows = []
    # HARNESS LIMIT: windows.csv only admits 2026Q3 as LIVE, so 4Q26 and the FY27
    # quarters cannot be registered. They are written to the package data folder
    # (15_live_objects_not_registrable.csv) and a harness change request is filed.
    sub = fwd[fwd["path"] == "spot_held"]
    ok = sub[sub["quarter"] == "3Q26"]
    not_ok = sub[sub["quarter"] != "3Q26"].copy()
    not_ok["reason"] = "harness windows.csv admits only 2026Q3 as LIVE"
    not_ok["sd"] = round(float(sigma), 4)
    write(not_ok, "15_live_objects_not_registrable.csv")
    for _, r in ok.iterrows():
        tq = to_period(r["quarter"])
        q = _quantiles(float(r["revenue_fx_pp"]), sigma)
        row = {"method": METHOD, "object": object_name, "target": "fx_pts_revenue",
               "quarter": f"{tq.year}Q{tq.quarter}", "vintage_date": TODAY.isoformat(),
               "horizon_q": int((tq - to_period("3Q26")).n), "point": float(r["revenue_fx_pp"]),
               "window": "LIVE", "prior_basis": "PIT", "n_params": n_params,
               "n_train": n_train, "sd": round(float(sigma), 4),
               "knowable_from": "2026-08-28",
               "spec_id": "objectA_free_weights_spot_held",
               "notes": "FX pp is an OUTPUT of the kernel arithmetic; never added to revenue"}
        row.update({k: round(v, 4) for k, v in q.items()})
        rows.append(row)
        row2 = dict(row); row2["prior_basis"] = "full_sample"; rows.append(row2)
    return pd.DataFrame(rows)


def emit(pf: pd.DataFrame, pf_full: pd.DataFrame, a_hat, sigma, fwd, n_train, written: list):
    objs = []
    h2 = pd.concat([
        build_rows(pf, "H2_phi_adrfx", "fx_rev_next_q_h2", "PIT",
                   "H2_phi_2/3ADRFX(q-1)+1/3ADRFX(q-2)_scale_free",
                   "Phi-implied lag; interval likelihood on letter integers"),
        build_rows(pf_full, "H2_phi_adrfx", "fx_rev_next_q_h2", "full_sample",
                   "H2_phi_full_sample_weights", "full-sample-prior replay"),
    ], ignore_index=True)
    h3 = pd.concat([
        build_rows(pf, "H3_free_weights", "fx_rev_next_q_h3", "PIT",
                   "H3_free_nonneg_weights_on_basket_lags012",
                   "Object A; lag-0 basket is QTD actual plus spot held"),
        build_rows(pf_full, "H3_free_weights", "fx_rev_next_q_h3", "full_sample",
                   "H3_free_full_sample_weights", "full-sample-prior replay"),
    ], ignore_index=True)
    lv = live_rows(a_hat, sigma, fwd, n_train, 4)
    for df, name in [(h2, "fx_rev_next_q_h2"), (h3, "fx_rev_next_q_h3"),
                     (lv, "live_fx_schedule")]:
        if not len(df):
            print(f"  SKIP registry {name}: no rows")
            continue
        register(df, allow_single_replay=True)
        written.append(f"{METHOD}__{name}.csv")
        objs.append(name)
    return objs
