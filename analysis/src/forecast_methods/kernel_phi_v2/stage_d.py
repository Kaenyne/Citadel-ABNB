"""Stage D — the carried part, the residual R, and the conditional 3Q26 / 4Q26 range.

carried_q = c_{s(q)} * [ phi_1 GBV_{q-1} + phi_2 GBV_{q-2} ]     (fully printed at the
                                                                  guide date for q)
R_q       = revenue_q - carried_q                                 (the "unknown third")

R is modelled on the scale k_q = R_q / carried_q, because carried_q is the only piece
of the identity that is known when the forecast is made.  revenue_q = carried_q (1+k_q).
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

from common import OUT, SEASON_NAME, GBV_2Q26, GBV_1Q26, usable

RNPL_SHARE = {"2025Q3": 5.0, "2025Q4": 12.0, "2026Q1": 20.0, "2026Q2": 22.0,
              "2026Q3": 23.0, "2026Q4": 23.0}
W1_START, W2_START = "2023Q1", "2024Q1"


def _rnpl(q):
    return RNPL_SHARE.get(q, 0.0)


def build(panel: pd.DataFrame, fit, kmax: int = 4, w=None, scale=None) -> pd.DataFrame:
    """carried_q = c_s * scale * [ w GBV_{q-1} + (1-w) GBV_{q-2} ].

    Only `w` matters for any forecast built on k = R/carried, because a positive
    rescaling of `carried` is absorbed one-for-one by k.  `w` defaults to the
    estimated split phi_1/(phi_1+phi_2); `scale` defaults to phi_1+phi_2 so that
    `carried` is on the same dollar scale as the fitted two-lag contribution.
    """
    phi = fit["phi"][0]
    if w is None:
        w = float(phi[1] / (phi[1] + phi[2]))
    if scale is None:
        scale = float(phi[1] + phi[2])
    d = usable(panel, kmax=kmax).copy()
    d["c_s"] = d["season"].map(fit["c"])
    d["carried_w"] = w
    d["carried_musd"] = d["c_s"] / 100.0 * scale * (w * d["gbv_l1"] +
                                                    (1 - w) * d["gbv_l2"])
    d["R_musd"] = d["revenue_musd"] - d["carried_musd"]
    d["R_share_of_revenue"] = d["R_musd"] / d["revenue_musd"]
    d["k"] = d["R_musd"] / d["carried_musd"]
    d["R_yoy_pct"] = 100.0 * (d["R_musd"] / d["R_musd"].shift(4) - 1.0)
    # the model-implied in-quarter piece (NOT point-in-time: needs GBV_q)
    d["phi0_inquarter_share"] = d["c_s"] / 100.0 * phi[0] * d["gbv_l0"] / d["revenue_musd"]
    # point-in-time observables: everything dated q-1 (printed in the letter that
    # carries the guide for q)
    d["x_gbv_yoy_l1"] = d["gbv_yoy_pct"].shift(1)
    d["x_nights_yoy_l1"] = d["nights_yoy_pct"].shift(1)
    d["x_paid_backlog_yoy_l1"] = d["paid_backlog_yoy_pct"].shift(1)
    d["x_fp_yoy_l1"] = d["funds_held_yoy_pct"].shift(1)
    d["x_uf_yoy_l1"] = d["unearned_fees_yoy_pct"].shift(1)
    d["x_summer"] = (d["season"] == 3).astype(float)
    d["x_gbv_accel_l1"] = d["gbv_yoy_pct"].shift(1) - d["gbv_yoy_pct"].shift(2)
    return d


# ------------------------------------------------------------------ descriptive
def describe_R(d: pd.DataFrame, lo="2022Q1") -> pd.DataFrame:
    w = d[d["q"] >= lo]
    rows = []
    for s, g in w.groupby("season"):
        rows.append(dict(season=SEASON_NAME[s], n=len(g),
                         R_share_mean=float(g["R_share_of_revenue"].mean()),
                         R_share_sd=float(g["R_share_of_revenue"].std(ddof=1)),
                         R_share_min=float(g["R_share_of_revenue"].min()),
                         R_share_max=float(g["R_share_of_revenue"].max()),
                         k_mean=float(g["k"].mean()), k_sd=float(g["k"].std(ddof=1)),
                         R_yoy_mean=float(g["R_yoy_pct"].mean()),
                         R_yoy_sd=float(g["R_yoy_pct"].std(ddof=1)),
                         revenue_yoy_mean=float(g["revenue_yoy_pct"].mean())))
    out = pd.DataFrame(rows)
    out["window"] = f"{lo}+"
    return out


def explain_R(d: pd.DataFrame, lo="2022Q1") -> pd.DataFrame:
    """In-sample season-demeaned correlations of k with each candidate observable."""
    w = d[(d["q"] >= lo)].copy()
    w["k_dm"] = w["k"] - w.groupby("season")["k"].transform("mean")
    rows = []
    cands = [("x_gbv_yoy_l1", "prior-quarter GBV y/y (PIT)", True),
             ("x_gbv_accel_l1", "prior-quarter GBV y/y acceleration (PIT)", True),
             ("x_paid_backlog_yoy_l1", "paid-backlog y/y at q-1 (PIT)", True),
             ("x_fp_yoy_l1", "funds payable y/y at q-1 (PIT)", True),
             ("x_uf_yoy_l1", "unearned fees y/y at q-1 (PIT)", True),
             ("x_nights_yoy_l1", "nights y/y at q-1 (PIT)", True),
             ("x_summer", "summer (Q3) dummy — absorbed by season means", True),
             ("phi0_inquarter_share", "phi_0 in-quarter share (NOT PIT)", False)]
    for col, lab, pit in cands:
        g = w.dropna(subset=["k_dm", col])
        if len(g) < 5:
            continue
        x = g[col].values.astype(float)
        y = g["k_dm"].values.astype(float)
        if x.std() == 0:
            rows.append(dict(regressor=col, label=lab, point_in_time=pit, n=len(g),
                             corr=np.nan, slope=np.nan, t=np.nan, r2=0.0))
            continue
        b = np.polyfit(x, y, 1)
        yh = np.polyval(b, x)
        ss = 1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        se = np.sqrt(((y - yh) ** 2).sum() / max(len(g) - 2, 1) /
                     ((x - x.mean()) ** 2).sum())
        rows.append(dict(regressor=col, label=lab, point_in_time=pit, n=len(g),
                         corr=float(np.corrcoef(x, y)[0, 1]), slope=float(b[0]),
                         t=float(b[0] / se) if se > 0 else np.nan, r2=float(ss)))
    return pd.DataFrame(rows)


# ------------------------------------------------------- expanding-window PIT
def _train_filter(train: pd.DataFrame, how: str) -> pd.DataFrame:
    """Estimation-window variants, mirroring kernel-lambda's ex_covid / last3."""
    if how == "all":
        return train
    if how == "ex_covid":
        t = train[train["nights_yoy_pct"].abs() <= 25.0]
        return t if (t["season"].nunique() == 4 and t["season"].value_counts().min() >= 2) else train
    if how == "last3_ex_covid":
        t = train[train["nights_yoy_pct"].abs() <= 25.0]
        if not (t["season"].nunique() == 4 and t["season"].value_counts().min() >= 2):
            t = train
        return t.groupby("season", group_keys=False).tail(3)
    raise ValueError(how)


def _fit_k(train: pd.DataFrame, col=None):
    """Season means of k, plus one optional shared slope on a season-demeaned x."""
    sm = train.groupby("season")["k"].mean().to_dict()
    if col is None:
        return sm, 0.0, np.nan
    t = train.dropna(subset=[col]).copy()
    if len(t) < 6:
        return sm, 0.0, np.nan
    t["k_dm"] = t["k"] - t["season"].map(sm)
    x = t[col].values.astype(float)
    xm = float(x.mean())
    if x.std() == 0:
        return sm, 0.0, xm
    b = float(np.polyfit(x - xm, t["k_dm"].values.astype(float), 1)[0])
    return sm, b, xm


def pit_replay(d: pd.DataFrame, col=None, start=W1_START, train_window="all"):
    rows = []
    for i in range(len(d)):
        q = d["q"].iloc[i]
        if q < start:
            continue
        train = d.iloc[:i]
        if train["season"].nunique() < 4 or train["season"].value_counts().min() < 2:
            continue
        train = _train_filter(train, train_window)
        sm, b, xm = _fit_k(train, col)
        s = int(d["season"].iloc[i])
        if s not in sm:
            continue
        kx = sm[s]
        if col is not None and np.isfinite(xm) and np.isfinite(d[col].iloc[i]):
            kx = kx + b * (float(d[col].iloc[i]) - xm)
        pred = float(d["carried_musd"].iloc[i]) * (1.0 + kx)
        act = float(d["revenue_musd"].iloc[i])
        rows.append(dict(target=d["label"].iloc[i], q=q, season=SEASON_NAME[s],
                         train_window=train_window, feature=col or "season_mean_only",
                         n_train=len(train), k_pred=kx, k_act=float(d["k"].iloc[i]),
                         pred_musd=pred, actual_musd=act,
                         err_pct=100.0 * (pred / act - 1.0)))
    return pd.DataFrame(rows)


def score(rep: pd.DataFrame, start: str) -> dict:
    r = rep[rep["q"] >= start]
    e = r["err_pct"].values
    if len(e) == 0:
        return dict(n=0)
    return dict(n=len(e), rmse_pct=float(np.sqrt((e ** 2).mean())),
                mae_pct=float(np.abs(e).mean()), bias_pct=float(e.mean()))


# --------------------------------------------------------------- GBV forecast
def gbv_frame(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel.copy()
    d["gbv_l4"] = d["gbv_musd"].shift(4)
    d["y_gbv_yoy"] = d["gbv_yoy_pct"]
    d["x_gbv_yoy_l1"] = d["gbv_yoy_pct"].shift(1)
    d["x_nights_yoy_l1"] = d["nights_yoy_pct"].shift(1)
    d["x_fp_yoy_l1"] = d["funds_held_yoy_pct"].shift(1)
    d["x_paid_backlog_yoy_l1"] = d["paid_backlog_yoy_pct"].shift(1)
    d["x_uf_yoy_l1"] = d["unearned_fees_yoy_pct"].shift(1)
    # RNPL-confound-corrected unearned fees: add back the y/y CHANGE in the RNPL GBV
    # share, in points, times k.  PIT-safe (each share is same-day-letter admissible)
    # but 3Q25/4Q25 are researcher ramp values with NO disclosure behind them.
    for k in (0.5, 1.0):
        d[f"x_uf_yoy_corr_k{k}"] = d["x_uf_yoy_l1"] + k * np.array(
            [_rnpl(q4) - _rnpl(q8) for q4, q8 in
             zip(d["q"].shift(1).fillna(""), d["q"].shift(5).fillna(""))])
    return d


def gbv_replay(d: pd.DataFrame, col: str, start: str):
    rows = []
    for i in range(len(d)):
        q = d["q"].iloc[i]
        if q < start:
            continue
        if not np.isfinite(d["gbv_musd"].iloc[i]) or not np.isfinite(d["gbv_l4"].iloc[i]):
            continue
        train = d.iloc[:i].dropna(subset=["y_gbv_yoy", col])
        if len(train) < 6 or not np.isfinite(d[col].iloc[i]):
            continue
        x = train[col].values.astype(float)
        y = train["y_gbv_yoy"].values.astype(float)
        if x.std() == 0:
            continue
        b = np.polyfit(x, y, 1)
        yhat = float(np.polyval(b, float(d[col].iloc[i])))
        pred = float(d["gbv_l4"].iloc[i]) * (1 + yhat / 100.0)
        act = float(d["gbv_musd"].iloc[i])
        rows.append(dict(target=d["label"].iloc[i], q=q, feature=col, n_train=len(train),
                         yoy_pred=yhat, yoy_act=float(d["y_gbv_yoy"].iloc[i]),
                         pred_musd=pred, actual_musd=act,
                         err_pct=100.0 * (pred / act - 1.0)))
    return pd.DataFrame(rows)


def gbv_naive(d: pd.DataFrame, start: str):
    rows = []
    for i in range(len(d)):
        q = d["q"].iloc[i]
        if q < start:
            continue
        if not np.isfinite(d["gbv_l4"].iloc[i]) or not np.isfinite(d["x_gbv_yoy_l1"].iloc[i]):
            continue
        pred = float(d["gbv_l4"].iloc[i]) * (1 + float(d["x_gbv_yoy_l1"].iloc[i]) / 100.0)
        act = float(d["gbv_musd"].iloc[i])
        rows.append(dict(target=d["label"].iloc[i], q=q, feature="naive_yoy_persistence",
                         pred_musd=pred, actual_musd=act,
                         err_pct=100.0 * (pred / act - 1.0)))
    return pd.DataFrame(rows)
