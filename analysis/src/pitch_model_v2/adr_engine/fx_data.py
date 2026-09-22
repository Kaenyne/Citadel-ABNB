"""adr_engine / fx_data.py — daily FX -> point-in-time quarterly averages -> regional baskets -> design matrix.
Information set at an origin date d: FRED prints dated <= d - H10_LAG_DAYS; unobserved business days of the target
quarter take the last observed rate (spot held); a business day with no print inside a completed quarter takes the
last rate on or before it (the fx_lag_v2 fix)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C


def load_daily() -> pd.DataFrame:
    """Wide daily table: index = date, columns = CCYS (USD per foreign unit) + USD_BROAD (index level)."""
    d = pd.read_csv(C.FX_DAILY, parse_dates=["date"])
    w = d.pivot(index="date", columns="ccy", values="usd_per_unit").sort_index()
    return w[C.CCYS + ["USD_BROAD"]]


def bdays(q: str) -> pd.DatetimeIndex:
    p = C.qlabel_to_period(q)
    return pd.bdate_range(p.start_time.normalize(), p.end_time.normalize())


def quarter_avg(daily: pd.DataFrame, q: str, info_date: pd.Timestamp | None = None) -> tuple[pd.Series, float]:
    """Mean over the quarter's business days of the rates knowable at info_date (spot held after the last print).
    Returns (mean per column, observed fraction of business days)."""
    days = bdays(q)
    cutoff = None if info_date is None else (pd.Timestamp(info_date) - pd.Timedelta(days=C.H10_LAG_DAYS))
    known = daily if cutoff is None else daily[daily.index <= cutoff]
    if known.empty:
        raise ValueError(f"no FX prints knowable at {info_date}")
    # forward-fill onto the quarter's business-day grid; days after the last print carry the last print
    grid = known.reindex(known.index.union(days)).ffill().reindex(days)
    obs_frac = float((days <= known.index.max()).mean())
    return grid.mean(), obs_frac


def yoy_by_ccy(daily: pd.DataFrame, q: str, info_date=None) -> tuple[pd.Series, float]:
    """Per-currency y/y of the quarterly average rate, in per cent. Base quarter q-4 always fully observed."""
    cur, f = quarter_avg(daily, q, info_date)
    base, _ = quarter_avg(daily, C.prior_quarter(q, 4), info_date)
    return (cur / base - 1.0) * 100.0, f


def regional_baskets(yoy: pd.Series) -> pd.Series:
    """Basket y/y per region = sum_c kappa_rc * yoy_c (USD legs contribute zero)."""
    out = {}
    for r in C.REGIONS:
        out[r] = sum(w * (0.0 if c == "USD" else float(yoy[c])) for c, w in C.KAPPA[r].items())
    return pd.Series(out)


def gbv_shares() -> pd.DataFrame:
    """Regional GBV shares by fiscal year from the 10-K Geographic Mix table, with the date each became knowable."""
    a = pd.read_csv(C.REGIONAL_ANNUAL)
    a = a[a.region.isin(C.REGIONS)].pivot(index="year", columns="region", values="gbv_share_pct") / 100.0
    led = pd.read_csv(C.LEDGER, parse_dates=["print_date"])
    prints = led.groupby("print_quarter").print_date.min()
    know = {}
    for y in a.index:
        pq = f"4Q{str(int(y))[2:]}"
        know[y] = prints[pq] + pd.Timedelta(days=C.TENK_LAG_DAYS) if pq in prints.index else pd.NaT
    a["knowable_from"] = pd.Series(know)
    return a


def shares_at(shares: pd.DataFrame, info_date) -> tuple[pd.Series, int]:
    """Latest fiscal-year shares knowable at info_date (None -> latest available)."""
    s = shares if info_date is None else shares[shares.knowable_from <= pd.Timestamp(info_date)]
    if s.empty:
        s = shares.iloc[[0]]          # before the first 10-K in the file: use FY2020 (stated fallback)
    row = s.iloc[-1]
    return row[C.REGIONS].astype(float), int(s.index[-1])


def print_dates() -> pd.Series:
    led = pd.read_csv(C.LEDGER, parse_dates=["print_date"])
    return led.groupby("print_quarter").print_date.min()


def disclosed_targets() -> pd.DataFrame:
    """The 17 disclosed ADR-FX points with print dates and interval half-widths."""
    k = pd.read_csv(C.KPI_PANEL)
    k = k[k.quarter.isin(C.TARGET_QUARTERS)][["quarter", "adr_usd", "adr_yoy_reported_pct", "adr_yoy_exfx_pct", "fx_pts_adr"]].copy()
    pdts = print_dates()
    k["print_date"] = k.quarter.map(pdts)
    k["half_width"] = np.where(k.quarter.isin(C.HALF_POINT_QUARTERS), 0.25, 0.5)
    k = k.set_index("quarter").loc[C.TARGET_QUARTERS]
    return k


def origin_dates(q: str, pdts: pd.Series) -> dict[str, pd.Timestamp]:
    p = C.qlabel_to_period(q)
    start = p.start_time.normalize()
    return {"O1": start - pd.Timedelta(days=1),
            "O2": start + pd.Timedelta(days=C.BDAY_60),
            "O3": (pdts[q] - pd.Timedelta(days=1)) if q in pdts.index else None}


def design_row(daily, shares, q: str, info_date):
    """One row of the design: X_r = 100 * g_r * basket_r (so FX_pp = sum_r beta_r X_r); also EUR / broad-USD y/y."""
    yoy, f = yoy_by_ccy(daily, q, info_date)
    b = regional_baskets(yoy)
    g, fy = shares_at(shares, info_date)
    X = {r: float(g[r] * b[r]) for r in C.REGIONS}
    X.update({"basket_" + r: float(b[r]) for r in C.REGIONS})
    X.update({"eur_yoy": float(yoy["EUR"]), "usd_broad_yoy": float(yoy["USD_BROAD"]), "obs_frac": f, "shares_fy": fy})
    return X
