"""v2.1 geographic mix: quarterly stay-quarter regional weights instead of one annual snapshot.
w_{r,t} = regional revenue_{r,t} (check-in basis, 10-Q, overnight/10_regional_panel_quarterly.csv) / regional ADR index
(NA 1.42, EMEA 0.97, LatAm 0.68, APAC 0.59 — research/notes/overnight/10_regional-and-segment-decomposition.md), renormalised.
Forward (3Q26-4Q27): same quarter of the prior year, rolled by the record's share-drift rule (NA -0.55 pp/qtr, EMEA +0.10,
LatAm +0.33, APAC +0.10 per quarter of elapsed time), renormalised. Nothing fitted."""
import numpy as np, pandas as pd
import config as C

ADR_INDEX = {"NAM": 1.42, "EMEA": 0.97, "LatAm": 0.68, "APAC": 0.59}
COL = {"NAM": "na", "EMEA": "emea", "LatAm": "latam", "APAC": "apac"}
DRIFT_PP_PER_Q = {"NAM": -0.55, "EMEA": 0.10, "LatAm": 0.33, "APAC": 0.10}
PANEL = C.ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv"


def _qi(label):
    return C.qi(2000 + int(label[2:]), int(label[0]))


def seasonal_weights(through_qi=C.qi(2027, 4)):
    p = pd.read_csv(PANEL); p["qi"] = p.quarter.map(_qi); p = p.set_index("qi").sort_index()
    rev = pd.DataFrame({R: p[f"{COL[R]}_revenue_musd"] for R in ADR_INDEX}).dropna()
    proxy = rev.div(pd.Series(ADR_INDEX)); w = proxy.div(proxy.sum(axis=1), axis=0)
    last = int(w.index.max()); out = w.copy()
    for q in range(last + 1, through_qi + 1):
        base = out.loc[q - 4]; k = (q - last + 3) // 4            # quarters of elapsed drift, in years-of-4
        rolled = base + pd.Series(DRIFT_PP_PER_Q) / 100 * 4 * ((q - (last - 3)) / 4)   # drift accrues with elapsed quarters
        rolled = rolled.clip(lower=0.01); out.loc[q] = rolled / rolled.sum()
    out = out.sort_index(); out.index.name = "qi"; return out


def global_from_regional(reg_pct, weights):
    """reg_pct: DataFrame index qi, columns regions, regional y/y in percent. weights: from seasonal_weights()."""
    w = weights.reindex(reg_pct.index).reindex(columns=reg_pct.columns)
    ok = reg_pct.notna() & w.notna(); ws = (w * ok).sum(axis=1)
    g = (reg_pct.fillna(0) * w.fillna(0)).sum(axis=1) / ws
    g[ws < 0.5] = np.nan
    return g
