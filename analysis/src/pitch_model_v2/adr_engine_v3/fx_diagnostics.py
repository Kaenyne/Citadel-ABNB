"""adr_engine_v3 / fx_diagnostics.py — audit fix (a): the registered V1 variant beside the V0 identity, and the
diagnostic that motivates showing it.

The pre-registered promotion rule keeps V0 (the translation identity) as the leg; this module does not change that.
It (1) fits V1 (regional pass-through, MAP, the registration's own prior and interval likelihood) on all 17 disclosed
quarters so its forward point can be shown beside V0's, and (2) records how V0's point-in-time error depends on V0's
own Latin-American component (audit finding F1: slope +0.55 to +0.69, p 0.002-0.012 in all four promotion cells).
Mechanism evidence gathered since the audit (docs/cc-search-price/I6*.md): Airbnb converts a host's price at spot with
no margin or lag, and Brazilian hosts price in BRL, so the V0 miss is a weighting problem, not a pass-through one."""
from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from . import config as C, exposure as E, walkforward as W


def fit_v1_all(full: pd.DataFrame) -> dict[str, float]:
    """V1 MAP on every disclosed quarter (the in-sample fit whose forward point is shown beside V0)."""
    m = E.fit_v1_map(full[C.REGIONS].values, full.y.values, full.h.values)
    return {r: float(b) for r, b in zip(C.REGIONS, m["beta"])} | {"sigma": float(m["sigma"])}


def v0_error_on_latam(wf: pd.DataFrame, full: pd.DataFrame, fwd_latam: dict[str, float]) -> pd.DataFrame:
    """OLS of V0's point-in-time error on V0's own LatAm component, per window x promotion origin, with the implied
    V0 error at the forward quarters (descriptive; not a forecast adjustment)."""
    rows = []
    for w, qs in C.WINDOWS.items():
        for o in ("O2", "O3"):
            e = wf[(wf.variant == "V0_translation") & (wf.origin == o) & wf.quarter.isin(qs)].set_index("quarter").err_pp
            x = full.loc[e.index, "latam"]
            m = sm.OLS(e.values, sm.add_constant(x.values)).fit()
            row = {"window": w, "origin": o, "n": len(e), "intercept_pp": m.params[0], "slope": m.params[1],
                   "p_slope": m.pvalues[1], "r": float(np.corrcoef(x, e)[0, 1])}
            for q, xl in fwd_latam.items():
                row[f"implied_v0_error_{q}_pp"] = m.params[0] + m.params[1] * xl
            rows.append(row)
    return pd.DataFrame(rows)


def latam_strong_quarters(full: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Full-information V0 misses in the quarters whose LatAm component exceeds the threshold (pp)."""
    d = full.assign(v0=full[C.REGIONS].sum(axis=1)); d["v0_err"] = d.v0 - d.y
    return d.loc[d.latam > threshold, ["y", "v0", "v0_err", "latam", "emea", "apac"]]
