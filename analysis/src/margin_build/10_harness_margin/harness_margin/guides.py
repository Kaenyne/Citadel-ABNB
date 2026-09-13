"""Management margin guidance in force at a vintage date.

Source: data/processed/overnight/02_guidance_ledger.csv (metric adj_ebitda_margin_pct,
adj_ebitda_margin_yoy_pts, adj_ebitda_usd_m; guide_type floor / ceiling / point).
Writes guides_margin.csv (one row per guide, canonical periods and dates).

Two look-ups:
  fy_guide_in_force(vintage_date, fy)   -> latest FY-margin guide for fiscal year `fy` issued on
                                           or before vintage_date, converted to a LEVEL (%). A y/y
                                           guide is converted with the prior-FY actual margin, which
                                           must itself be knowable at vintage_date.
  q_guide_in_force(vintage_date, quarter) -> latest quarterly margin guide for `quarter` issued on
                                           or before vintage_date, converted to a level with the
                                           same-quarter-last-year actual margin.
Floors are read at the floor, ceilings at the ceiling, points at the point (that is what
"guide-implied" means; the Street does the same, WS03 note).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import paths as P
from .frozen import Q
from .panel import load_targets, history_as_of

MARGIN_METRICS = {"adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts", "adj_ebitda_usd_m"}
NUMERIC_TYPES = {"floor", "ceiling", "point"}


def _canon_period(p: str):
    s = str(p).strip().upper()
    if s.startswith("FY"):
        return s
    try:
        return Q.canon(s)
    except ValueError:
        return None


def build_guides(write: bool = True) -> pd.DataFrame:
    g = pd.read_csv(P.SRC_GUIDANCE_LEDGER)
    g = g[g["metric"].isin(MARGIN_METRICS) & g["guide_type"].isin(NUMERIC_TYPES)].copy()
    g["guide_date"] = pd.to_datetime(g["print_date"]).dt.date
    g["print_quarter"] = g["print_quarter"].map(Q.canon)
    g["target_period"] = g["target_period"].map(_canon_period)
    g = g[g["target_period"].notna()].copy()

    def _val(r):
        if r["guide_type"] == "floor":
            return r["value_low"]
        if r["guide_type"] == "ceiling":
            return r["value_high"]
        return r["value_mid"]

    g["value"] = g.apply(_val, axis=1)
    g["is_fy"] = g["target_period"].str.startswith("FY")
    g["fy"] = np.where(g["is_fy"], g["target_period"].str[2:], g["target_period"].str[:4])
    g = g.sort_values(["guide_date", "target_period"]).reset_index(drop=True)
    out = g[["guide_id", "guide_date", "print_quarter", "target_period", "is_fy", "fy", "metric",
             "guide_type", "value", "unit", "quote", "note"]].copy()
    if write:
        P.ensure_dirs()
        out.to_csv(P.OUT_GUIDES, index=False)
    return out


_CACHE = {}


def load_guides() -> pd.DataFrame:
    if "g" in _CACHE:
        return _CACHE["g"]
    if not P.OUT_GUIDES.exists():
        build_guides()
    g = pd.read_csv(P.OUT_GUIDES)
    g["guide_date"] = pd.to_datetime(g["guide_date"]).dt.date
    _CACHE["g"] = g
    return g


def fy_actual_margin_as_of(vintage_date, fy: int, targets=None):
    """FY adjusted-EBITDA margin from the four quarters, only if all four printed <= vintage."""
    h = history_as_of(vintage_date, None, targets)
    qs = [f"{fy}Q{n}" for n in (1, 2, 3, 4)]
    sub = h[h["quarter"].isin(qs)]
    if len(sub) < 4:
        return None
    return float(100.0 * sub["adj_ebitda_musd"].sum() / sub["revenue_musd"].sum())


def fy_guide_in_force(vintage_date, fy: int, targets=None):
    """dict(level_pct, guide_type, guide_date, form, guide_id, quote) or None."""
    vd = pd.to_datetime(vintage_date).date()
    g = load_guides()
    rows = g[g["is_fy"] & (g["fy"].astype(int) == int(fy)) & (g["guide_date"] <= vd)
             & g["metric"].isin(["adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts"])]
    if len(rows) == 0:
        return None
    r = rows.sort_values("guide_date").iloc[-1]
    if r["metric"] == "adj_ebitda_margin_pct":
        level = float(r["value"])
        form = "level"
    else:
        prior = fy_actual_margin_as_of(vd, int(fy) - 1, targets)
        if prior is None:
            return None
        level = prior + float(r["value"])
        form = f"yoy_pts({r['value']:+.1f}) on FY{int(fy)-1} actual {prior:.2f}"
    return {"level_pct": level, "guide_type": r["guide_type"], "guide_date": r["guide_date"],
            "form": form, "guide_id": r["guide_id"], "quote": r.get("quote", "")}


def q_guide_in_force(vintage_date, quarter: str, targets=None):
    """Quarterly margin guide for `quarter` (level %, plus an optional $ floor) or None."""
    vd = pd.to_datetime(vintage_date).date()
    q = Q.canon(quarter)
    g = load_guides()
    rows = g[(~g["is_fy"]) & (g["target_period"] == q) & (g["guide_date"] <= vd)]
    if len(rows) == 0:
        return None
    out = {"guide_date": None, "level_pct": None, "ebitda_floor_musd": None, "guide_type": None,
           "form": None, "guide_id": None}
    m = rows[rows["metric"].isin(["adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts"])]
    if len(m):
        r = m.sort_values("guide_date").iloc[-1]
        if r["metric"] == "adj_ebitda_margin_pct":
            out["level_pct"] = float(r["value"])
            out["form"] = "level"
        else:
            s = history_as_of(vd, "adj_ebitda_margin_pct", targets)
            lag = Q.shift(q, -4)
            base = s.loc[s["quarter"] == lag, "adj_ebitda_margin_pct"]
            if len(base) == 0:
                return None
            out["level_pct"] = float(base.iloc[0]) + float(r["value"])
            out["form"] = f"yoy_pts({r['value']:+.1f}) on {lag} actual {float(base.iloc[0]):.2f}"
        out["guide_type"] = r["guide_type"]
        out["guide_date"] = r["guide_date"]
        out["guide_id"] = r["guide_id"]
    d = rows[rows["metric"] == "adj_ebitda_usd_m"]
    if len(d):
        r = d.sort_values("guide_date").iloc[-1]
        out["ebitda_floor_musd"] = float(r["value"])
        out["guide_date"] = out["guide_date"] or r["guide_date"]
        out["guide_id"] = out["guide_id"] or r["guide_id"]
        out["guide_type"] = out["guide_type"] or r["guide_type"]
    if out["level_pct"] is None and out["ebitda_floor_musd"] is None:
        return None
    return out
