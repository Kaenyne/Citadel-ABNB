"""adr_engine / forecast.py — the ex-ante FX-on-ADR forecast (pre-registration §7).
Point = translation identity (V0) with unobserved business days held at the last FRED print (spot held).
Band = moving-block bootstrap of the joint daily log-return vector of the nine currencies (demeaned, so the
median path is spot held = the martingale assumption), applied to the days that are still unobserved at each
as-of date; centred on today's spot-held path. Also the ±5% parallel USD shift (D5's one-sigma device)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C
from . import fx_data as F


def _grid(daily: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    days = pd.bdate_range(start, end)
    return daily[C.CCYS].reindex(daily.index.union(days)).ffill().reindex(days)


def simulate_paths(daily: pd.DataFrame, last_obs: pd.Timestamp, horizon_end: pd.Timestamp,
                   n_paths=C.BOOT_PATHS, block=C.BOOT_BLOCK, seed=21) -> np.ndarray:
    """Returns array (n_paths, n_future_days, n_ccy) of simulated USD-per-unit levels for business days after last_obs."""
    hist = daily.loc[C.BOOT_START:last_obs, C.CCYS].dropna()
    lr = np.log(hist).diff().dropna().values                      # (T, k)
    lr = lr - lr.mean(axis=0, keepdims=True)                        # demean: spot held is the median path
    fut = pd.bdate_range(last_obs + pd.Timedelta(days=1), horizon_end)
    n_days, T = len(fut), lr.shape[0]
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n_days / block))
    starts = rng.integers(0, T - block, size=(n_paths, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_paths, -1)[:, :n_days]
    cum = np.cumsum(lr[idx], axis=1)                                 # (n_paths, n_days, k)
    last = hist.iloc[-1].values[None, None, :]
    return fut, last * np.exp(cum)


def quarter_avg_paths(daily, fut_days, paths, q: str, spot_cut: pd.Timestamp | None):
    """Quarter-average rates per path. Days <= spot_cut (the as-of information set) are held at the last real print
    (the point of view of the as-of date); days after are simulated."""
    days = F.bdays(q)
    hist_grid = _grid(daily, days[0], days[-1])                     # realised where observed, ffilled (spot held)
    mask_future = days.isin(fut_days)
    n_paths = paths.shape[0]
    out = np.tile(hist_grid.values[None, :, :], (n_paths, 1, 1))     # (n_paths, n_days_q, k)
    if mask_future.any():
        pos = np.searchsorted(fut_days.values, days[mask_future].values)
        sim = paths[:, pos, :]
        if spot_cut is not None:
            keep_spot = np.asarray(days[mask_future] <= spot_cut)     # already observed by the as-of date: hold today's spot
            sim = np.where(keep_spot[None, :, None], hist_grid.values[mask_future][None, :, :], sim)
        out[:, mask_future, :] = sim
    return out.mean(axis=1)                                          # (n_paths, k)


def fx_pp_from_avgs(cur: np.ndarray, base: np.ndarray, g: pd.Series, beta: dict | None = None) -> np.ndarray:
    yoy = (cur / base - 1.0) * 100.0                                 # (n_paths, k)
    ci = {c: i for i, c in enumerate(C.CCYS)}
    total = np.zeros(cur.shape[0])
    for r in C.REGIONS:
        b = sum(w * yoy[:, ci[c]] for c, w in C.KAPPA[r].items() if c != "USD")
        total += float(g[r]) * (beta[r] if beta else 1.0) * b
    return total


def run(daily=None, shares=None, beta_v1: dict | None = None) -> pd.DataFrame:
    daily = F.load_daily() if daily is None else daily
    shares = F.gbv_shares() if shares is None else shares
    g, fy = F.shares_at(shares, None)
    last_obs = daily.index.max()
    horizon_end = F.bdays(C.FORWARD_QUARTERS[-1])[-1]
    fut_days, paths = simulate_paths(daily, last_obs, horizon_end)
    rows = []
    for asof, label in C.ASOF_DATES.items():
        d = pd.Timestamp(asof)
        spot_cut = last_obs if d <= pd.Timestamp.today().normalize() + pd.Timedelta(days=1) else d - pd.Timedelta(days=C.H10_LAG_DAYS)
        for q in C.FORWARD_QUARTERS:
            days = F.bdays(q)
            obs_frac_asof = float((days <= spot_cut).mean())
            cur = quarter_avg_paths(daily, fut_days, paths, q, spot_cut)
            base = quarter_avg_paths(daily, fut_days, paths, C.prior_quarter(q, 4), spot_cut)
            pp = fx_pp_from_avgs(cur, base, g)
            # spot-held point = every future day at the last print: the median path by construction; compute exactly
            cur_sh = _grid(daily, days[0], days[-1]).mean().values[None, :]
            bq = F.bdays(C.prior_quarter(q, 4)); base_sh = _grid(daily, bq[0], bq[-1]).mean().values[None, :]
            point = float(fx_pp_from_avgs(cur_sh, base_sh, g)[0])
            rec = {"asof": asof, "asof_label": label, "quarter": q, "fx_pp_point_spot_held": point,
                   "p10": float(np.percentile(pp, 10)), "p50": float(np.percentile(pp, 50)), "p90": float(np.percentile(pp, 90)),
                   "sd": float(pp.std()), "obs_frac_at_asof": obs_frac_asof, "shares_fy": fy, "last_fx_obs": last_obs.date().isoformat()}
            # parallel USD shift after the as-of date (D5 device): foreign units worth 5% more / less in USD
            for tag, mult in (("usd_weak_+5pct", 1 + C.USD_SHIFT), ("usd_strong_-5pct", 1 - C.USD_SHIFT)):
                shifted = _grid(daily, days[0], days[-1]).copy()
                shifted.loc[shifted.index > spot_cut] *= mult
                bgrid = _grid(daily, bq[0], bq[-1]).copy(); bgrid.loc[bgrid.index > spot_cut] *= mult
                rec[tag] = float(fx_pp_from_avgs(shifted.mean().values[None, :], bgrid.mean().values[None, :], g)[0])
            if beta_v1:
                rec["fx_pp_point_v1"] = float(fx_pp_from_avgs(cur_sh, base_sh, g, beta_v1)[0])
            rows.append(rec)
    return pd.DataFrame(rows)


def currency_table(daily=None) -> pd.DataFrame:
    """Per-currency y/y of the spot-held quarterly average for 3Q26..4Q27 and the contribution to FX pp (FY2025 GBV shares)."""
    daily = F.load_daily() if daily is None else daily
    shares = F.gbv_shares(); g, fy = F.shares_at(shares, None)
    rows = []
    for q in C.FORWARD_QUARTERS + ["2Q26", "1Q26"]:
        yoy, f = F.yoy_by_ccy(daily, q, None)
        for c in C.CCYS:
            w = sum(float(g[r]) * C.KAPPA[r].get(c, 0.0) for r in C.REGIONS)
            rows.append({"quarter": q, "ccy": c, "yoy_pct": float(yoy[c]), "gbv_weight": w, "contribution_pp": w * float(yoy[c]), "obs_frac": f})
    return pd.DataFrame(rows)
