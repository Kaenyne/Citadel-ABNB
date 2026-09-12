"""fx_lag_v2 / pit_fx.py -- COPY of fx_lag/pit_fx.py, re-pointed at the
2026-09-11 FX refresh.  Point-in-time basket construction.

At a guide date d the information set is FRED FX through d-1.  The target quarter
is only partly elapsed, so its basket y/y is completed by holding the last observed
spot constant to quarter end ("QTD actual + spot held").  Regional revenue weights
use only L0 cells whose knowable_from <= d.
"""
from __future__ import annotations

import datetime as _dt
import functools

import numpy as np
import pandas as pd

from common import OVN, L0, FX_DAILY, to_period

REGIONS = ["na", "emea", "latam", "apac"]


@functools.lru_cache(maxsize=1)
def _daily() -> pd.DataFrame:
    d = pd.read_csv(FX_DAILY, parse_dates=["date"])
    d = d[d["unit"] == "usd_per_foreign_unit"]
    return d.pivot_table(index="date", columns="ccy", values="usd_per_unit")


@functools.lru_cache(maxsize=1)
def _weights() -> pd.DataFrame:
    b = pd.read_csv(OVN / "10_fx_basket.csv")
    w = b[(b["currency"] != "BASKET") & (b["region"].isin(REGIONS))].copy()
    w["ccy_used"] = np.where(w["proxy_series"].notna(), w["proxy_series"], w["currency"])
    return w[["region", "ccy_used", "weight"]]


@functools.lru_cache(maxsize=1)
def _l0() -> pd.DataFrame:
    l = pd.read_csv(L0 / "L0_exact_regional_revenue.csv")
    l["p"] = [to_period(q) for q in l["quarter"]]
    l["knowable_from"] = pd.to_datetime(l["knowable_from"]).dt.date
    return l


def regional_shares_asof(asof: _dt.date) -> pd.Series:
    l = _l0()
    l = l[l["knowable_from"] <= asof]
    piv = l.pivot_table(index="p", columns="region", values="revenue_musd", aggfunc="sum")
    piv = piv.reindex(columns=REGIONS)
    piv = piv.dropna()
    if len(piv) < 4:
        return pd.Series({r: v for r, v in zip(REGIONS, [0.42, 0.39, 0.10, 0.09])})
    t4 = piv.tail(4).sum()
    return t4 / t4.sum()


def _q_avg_spot_held(ccy_px: pd.Series, q: pd.Period, asof: _dt.date, hold: float | None = None):
    """Average of the daily rate over quarter q: actuals to min(asof, q_end), then
    the last observed value (or `hold`) for the remaining business days.

    v2 FIX (changed from fx_lag/pit_fx.py).  The original filled EVERY business day
    with no FRED print -- bank holidays inside a long-past quarter included -- with
    `hold`, the CURRENT spot.  On a completed base quarter that puts a 2026 rate
    into a 2025 average on two or three days out of about sixty-four.  Here a day
    with no print takes the last rate observed ON OR BEFORE it (the standard
    as-of convention), and `hold` is used only for days AFTER the last observation,
    which is the genuine spot-held-constant region.  `n_obs` counts days with a
    real print, so it is the honest observed-share numerator.
    """
    start, end = q.start_time.date(), q.end_time.date()
    days = pd.bdate_range(start, end)
    s = ccy_px.dropna()
    s = s[s.index.date <= min(asof, end)]
    if hold is None:
        prior = ccy_px[ccy_px.index.date <= asof].dropna()
        hold = float(prior.iloc[-1]) if len(prior) else np.nan
    if len(s) == 0:
        return float(hold), 0, len(days)
    ff = s.reindex(s.index.union(days)).ffill().reindex(days)
    vals = ff.values.astype(float).copy()
    last_obs = s.index.max()
    post = np.array([d > last_obs for d in days])
    vals[post] = hold
    in_q = set(d.date() for d in s.index if start <= d.date() <= end)
    n_obs = int(sum(1 for d in days if d.date() in in_q))
    return float(np.nanmean(vals)), n_obs, len(days)


def basket_yoy_asof(q, asof: _dt.date, hold_shift_pct: float = 0.0) -> dict:
    """Global revenue-weighted basket y/y for quarter q, using FX through `asof`
    and spot-held-constant thereafter.  `hold_shift_pct` shifts the held spot for
    scenario paths (+x% = weaker dollar)."""
    q = q if isinstance(q, pd.Period) else to_period(q)
    px = _daily()
    w = _weights()
    sh = regional_shares_asof(asof)
    qm4 = q - 4
    reg = {}
    elapsed_frac = None
    for region, g in w.groupby("region"):
        tot = g["weight"].sum()
        acc = 0.0
        for _, r in g.iterrows():
            if r["ccy_used"] == "USD":
                continue
            s = px[r["ccy_used"]]
            prior = s[s.index.date <= asof].dropna()
            hold = float(prior.iloc[-1]) * (1 + hold_shift_pct / 100.0) if len(prior) else np.nan
            cur, nobs, ndays = _q_avg_spot_held(s, q, asof, hold=hold)
            base, _, _ = _q_avg_spot_held(s, qm4, asof, hold=hold)
            acc += r["weight"] * ((cur / base - 1.0) * 100.0)
            elapsed_frac = nobs / ndays
        reg[region] = acc / tot
    glob = sum(reg[r] * float(sh[r]) for r in REGIONS)
    return {"quarter": f"{q.quarter}Q{str(q.year)[2:]}", "global_pct": glob,
            "elapsed_frac": elapsed_frac if elapsed_frac is not None else 0.0, **reg}
