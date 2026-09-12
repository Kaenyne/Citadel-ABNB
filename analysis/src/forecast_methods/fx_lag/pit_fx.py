"""fx_lag / pit_fx.py -- point-in-time basket construction.

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

from common import OVN, L0, to_period

REGIONS = ["na", "emea", "latam", "apac"]


@functools.lru_cache(maxsize=1)
def _daily() -> pd.DataFrame:
    d = pd.read_csv(OVN / "10_fx_daily.csv", parse_dates=["date"])
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
    """Average of daily rate over quarter q: actuals to min(asof, q_end), then the
    last observed value (or `hold`) for the remaining business days."""
    start, end = q.start_time.date(), q.end_time.date()
    days = pd.bdate_range(start, end)
    obs = ccy_px[(ccy_px.index.date >= start) & (ccy_px.index.date <= min(asof, end))].dropna()
    if hold is None:
        prior = ccy_px[ccy_px.index.date <= asof].dropna()
        hold = float(prior.iloc[-1]) if len(prior) else np.nan
    vals = []
    obs_by_day = {d.date(): v for d, v in obs.items()}
    for d in days:
        vals.append(obs_by_day.get(d.date(), hold))
    return float(np.nanmean(vals)), len(obs), len(days)


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
