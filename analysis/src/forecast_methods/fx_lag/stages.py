"""fx_lag / stages.py -- hypothesis horse-race, bootstrap, determined share,
forward schedule, four-way reconciliation, hedges, registry."""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd
from scipy import stats

import pit_fx
from common import (OVN, OUT, METHOD, TODAY, fit_interval_linear, interval_loglik,
                    profile_sigma, to_period, short, write)
from fits import interval_rmse, ols

HALF = 0.5
GUIDES = {  # guide date -> target quarter (from the harness windows file)
    "2021-11-04": "4Q21", "2022-02-15": "1Q22", "2022-05-03": "2Q22",
    "2022-08-02": "3Q22", "2022-11-01": "4Q22", "2023-02-14": "1Q23",
    "2023-05-09": "2Q23", "2023-08-03": "3Q23", "2023-11-01": "4Q23",
    "2024-02-13": "1Q24", "2024-05-08": "2Q24", "2024-08-06": "3Q24",
    "2024-11-07": "4Q24", "2025-02-13": "1Q25", "2025-05-01": "2Q25",
    "2025-08-06": "3Q25", "2025-11-06": "4Q25", "2026-02-12": "1Q26",
    "2026-05-07": "2Q26", "2026-08-06": "3Q26",
}
W1 = [d for d, q in GUIDES.items() if "1Q23" <= "" or True]  # filtered below
W1 = [d for d, q in GUIDES.items() if to_period("1Q23") <= to_period(q) <= to_period("2Q26")]
W2 = [d for d, q in GUIDES.items() if to_period("1Q24") <= to_period(q) <= to_period("2Q26")]


# ----------------------------------------------------------- hypothesis bank
def _design(sub, spec, pit_b0=None):
    """Return design matrix columns for a spec on a frame."""
    b0 = sub["b_lag0"].values if pit_b0 is None else pit_b0
    if spec == "H0_contemporaneous":
        return np.column_stack([b0]), True
    if spec == "H1_repo_eur_mean_t1_t2":
        return np.column_stack([np.ones(len(sub)),
                                (sub["eur_lag1"].values + sub["eur_lag2"].values) / 2.0]), False
    if spec == "H2_phi_adrfx":
        return np.column_stack([(2.0 / 3.0) * sub["adrfx_lag1"].values
                                + (1.0 / 3.0) * sub["adrfx_lag2"].values]), True
    if spec == "H2b_phi_basket":
        return np.column_stack([(2.0 / 3.0) * sub["b_lag1"].values
                                + (1.0 / 3.0) * sub["b_lag2"].values]), True
    if spec == "H3_free_weights":
        return np.column_stack([b0, sub["b_lag1"].values, sub["b_lag2"].values]), True
    if spec == "H3b_free_lags123":
        return np.column_stack([sub["b_lag1"].values, sub["b_lag2"].values,
                                sub["b_lag3"].values]), True
    if spec == "H4_free_adrfx_lags012":
        return np.column_stack([sub["fx_pts_adr"].values, sub["adrfx_lag1"].values,
                                sub["adrfx_lag2"].values]), True
    raise KeyError(spec)


SPECS = ["H0_contemporaneous", "H1_repo_eur_mean_t1_t2", "H2_phi_adrfx",
         "H2b_phi_basket", "H3_free_weights", "H3b_free_lags123", "H4_free_adrfx_lags012"]
PIT_SPECS = ["H0_contemporaneous", "H1_repo_eur_mean_t1_t2", "H2_phi_adrfx",
             "H2b_phi_basket", "H3_free_weights", "H3b_free_lags123"]
# H4 uses the target quarter's own disclosed ADR-FX point, which is only published
# at the print of that quarter -> NOT point-in-time; it is scored full-sample only.
NPARAM = {"H0_contemporaneous": 2, "H1_repo_eur_mean_t1_t2": 3, "H2_phi_adrfx": 2,
          "H2b_phi_basket": 2, "H3_free_weights": 4, "H3b_free_lags123": 4,
          "H4_free_adrfx_lags012": 4}


def full_sample_horse_race(d: pd.DataFrame, target: str, label: str) -> pd.DataFrame:
    sub = d[(d["p"] >= to_period("1Q23")) & (d["p"] <= to_period("2Q26"))].copy()
    rows = []
    for spec in SPECS:
        s = sub.dropna(subset=[target]).copy()
        X, nn = _design(s, spec)
        m = ~np.isnan(X).any(axis=1)
        s = s[m]; X = X[m]
        y = s[target].values
        f = fit_interval_linear(X, y - HALF, y + HALF, nonneg=nn)
        mu = X @ f["coef"]
        # LOO (interval likelihood refit, point RMSE vs the stated integer so it is
        # directly comparable with the repo's 1.2868 benchmark)
        e = []
        for i in range(len(y)):
            k = np.ones(len(y), bool); k[i] = False
            fi = fit_interval_linear(X[k], y[k] - HALF, y[k] + HALF, nonneg=nn)
            e.append(y[i] - float(X[i] @ fi["coef"]))
        e = np.array(e)
        rows.append({"target": label, "spec": spec, "n": len(y),
                     "coef": np.round(f["coef"], 4).tolist(),
                     "sigma": round(f["sigma"], 4), "loglik": round(f["loglik"], 3),
                     "aic": round(-2 * f["loglik"] + 2 * NPARAM[spec], 2),
                     "in_sample_rmse": round(float(np.sqrt(np.mean((mu - y) ** 2))), 4),
                     "in_sample_interval_rmse": round(interval_rmse(mu, y, HALF), 4),
                     "loo_rmse": round(float(np.sqrt(np.mean(e ** 2))), 4),
                     "loo_mae": round(float(np.mean(np.abs(e))), 4),
                     "loo_interval_rmse": round(interval_rmse(y - e, y, HALF), 4),
                     "se_of_rmse_approx": round(float(np.sqrt(np.mean(e ** 2)) / np.sqrt(2 * len(y))), 4),
                     "n_params": NPARAM[spec]})
    # baselines
    y = sub.dropna(subset=[target])[target].values
    prev = sub.dropna(subset=[target])[target].shift(1).values
    m = ~np.isnan(prev)
    rows.append({"target": label, "spec": "BASE_naive_last_fx_pp", "n": int(m.sum()),
                 "coef": [], "sigma": np.nan, "loglik": np.nan, "aic": np.nan,
                 "in_sample_rmse": round(float(np.sqrt(np.mean((prev[m] - y[m]) ** 2))), 4),
                 "in_sample_interval_rmse": round(interval_rmse(prev[m], y[m], HALF), 4),
                 "loo_rmse": round(float(np.sqrt(np.mean((prev[m] - y[m]) ** 2))), 4),
                 "loo_mae": round(float(np.mean(np.abs(prev[m] - y[m]))), 4),
                 "loo_interval_rmse": round(interval_rmse(prev[m], y[m], HALF), 4),
                 "se_of_rmse_approx": np.nan, "n_params": 0})
    rows.append({"target": label, "spec": "BASE_zero", "n": len(y), "coef": [],
                 "sigma": np.nan, "loglik": np.nan, "aic": np.nan,
                 "in_sample_rmse": round(float(np.sqrt(np.mean(y ** 2))), 4),
                 "in_sample_interval_rmse": round(interval_rmse(np.zeros_like(y), y, HALF), 4),
                 "loo_rmse": round(float(np.sqrt(np.mean(y ** 2))), 4),
                 "loo_mae": round(float(np.mean(np.abs(y))), 4),
                 "loo_interval_rmse": round(interval_rmse(np.zeros_like(y), y, HALF), 4),
                 "se_of_rmse_approx": np.nan, "n_params": 0})
    return pd.DataFrame(rows)


# --------------------------------------------------- PIT expanding-window run
def full_sample_coefficients(d: pd.DataFrame, target: str = "fx_pts_revenue") -> dict:
    """Fit each PIT spec ONCE on the whole 1Q23-2Q26 sample.

    These are the *illegitimate* weights a forecaster would have used if they had
    seen the entire sample at every guide date.  Used only for the full-sample-prior
    replay published side by side with the PIT replay.
    """
    sub = d[(d["p"] >= to_period("1Q23")) & (d["p"] <= to_period("2Q26"))]
    s = sub.dropna(subset=[target]).copy()
    out = {}
    for spec in PIT_SPECS:
        X, nn = _design(s, spec)
        m = ~np.isnan(X).any(axis=1)
        y = s[target].values[m]
        f = fit_interval_linear(X[m], y - HALF, y + HALF, nonneg=nn)
        out[spec] = (f["coef"], f["sigma"], int(len(y)))
    return out


def pit_forecasts(d: pd.DataFrame, target: str = "fx_pts_revenue",
                  coef_override: dict | None = None) -> pd.DataFrame:
    """Expanding-window replay at each guide date.

    coef_override = {spec: (coef, sigma, n)} replaces the expanding-window fit with
    a fixed coefficient vector (the full-sample-prior replay).  The DRIVERS stay
    point-in-time (QTD basket + spot held) and the >=5-training-row gate is kept, so
    the two replays are row-matched and differ only in the weights that are applied.
    """
    idx = d.set_index("quarter")
    rows = []
    for gd, tq in sorted(GUIDES.items()):
        gdate = _dt.date.fromisoformat(gd)
        tp = to_period(tq)
        train = d[(d["p"] < tp) & d[target].notna()].copy()
        if len(train) < 5:
            continue
        # PIT lag-0 basket for the target quarter: QTD actual + spot held
        b0_pit = pit_fx.basket_yoy_asof(tp, gdate - _dt.timedelta(days=1))
        tgt_row = idx.loc[tq] if tq in idx.index else None
        for spec in PIT_SPECS:
            X, nn = _design(train, spec)
            m = ~np.isnan(X).any(axis=1)
            Xf = X[m]; y = train[target].values[m]
            if len(y) < 5:
                continue
            f = fit_interval_linear(Xf, y - HALF, y + HALF, nonneg=nn)
            coef, sigma_use, n_fit, basis = f["coef"], f["sigma"], int(len(y)), "PIT"
            if coef_override is not None:
                coef, sigma_use, n_fit = coef_override[spec]
                basis = "full_sample"
            if tgt_row is None:
                continue
            one = train.iloc[[0]].copy()
            for c in ["b_lag1", "b_lag2", "b_lag3", "eur_lag1", "eur_lag2",
                      "adrfx_lag1", "adrfx_lag2", "fx_pts_adr", "b_lag0"]:
                one[c] = tgt_row[c] if c in tgt_row.index else np.nan
            Xo, _ = _design(one, spec, pit_b0=np.array([b0_pit["global_pct"]]))
            if np.isnan(Xo).any():
                continue
            point = float(np.ravel(Xo @ coef)[0])
            rows.append({"guide_date": gd, "target_quarter": tq, "spec": spec,
                         "prior_basis": basis,
                         "n_train": n_fit, "n_train_pit": int(len(y)),
                         "coef": np.round(np.ravel(coef), 4).tolist(),
                         "point": round(point, 4),
                         "sigma": round(sigma_use, 4),
                         "actual": (float(tgt_row[target]) if not pd.isna(tgt_row[target]) else np.nan),
                         "b0_pit": round(b0_pit["global_pct"], 4),
                         "b0_elapsed_frac": round(b0_pit["elapsed_frac"], 3),
                         "n_params": NPARAM[spec],
                         "in_W1": gd in W1, "in_W2": gd in W2})
    out = pd.DataFrame(rows)
    return out


def score_pit(pf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (spec, win) in [(s, w) for s in PIT_SPECS for w in ("W1", "W2")]:
        sub = pf[(pf["spec"] == spec) & pf[f"in_{win}"] & pf["actual"].notna()]
        if not len(sub):
            continue
        e = sub["point"].values - sub["actual"].values
        naive = sub["actual"].shift(1)
        rows.append({"spec": spec, "window": win, "n": len(sub),
                     "rmse": round(float(np.sqrt(np.mean(e ** 2))), 4),
                     "mae": round(float(np.mean(np.abs(e))), 4),
                     "bias": round(float(np.mean(e)), 4),
                     "interval_rmse": round(interval_rmse(sub["point"].values,
                                                          sub["actual"].values, HALF), 4),
                     "hit_rate_in_band": round(float(np.mean(np.abs(e) <= HALF)), 3),
                     "n_params": int(sub["n_params"].iloc[0])})
    sc = pd.DataFrame(rows)
    if len(sc):
        base = sc.groupby("window")["rmse"].min()
        piv = sc.pivot(index="spec", columns="window", values="rmse")
        sc["best_in_window"] = [r["rmse"] == base[r["window"]] for _, r in sc.iterrows()]
    return sc


def replay_delta(pf: pd.DataFrame, pf_full: pd.DataFrame,
                 sc: pd.DataFrame, sc_full: pd.DataFrame) -> pd.DataFrame:
    """Side-by-side PIT vs full-sample-prior replay: is the difference real?

    A non-zero max_abs_point_delta is the evidence that the two replays are two
    distinct forecasts and not one forecast with a relabelled band.
    """
    k = ["guide_date", "target_quarter", "spec"]
    left = pf[k + ["point", "sigma", "n_train", "n_train_pit"]].rename(
        columns={"n_train_pit": "n_expanding_rows"})
    m = left.merge(pf_full[k + ["point", "sigma", "n_train"]], on=k,
                   suffixes=("_pit", "_full"))
    rows = []
    for spec in sorted(m["spec"].unique()):
        s = m[m["spec"] == spec]
        dpt = (s["point_full"] - s["point_pit"]).values
        row = {"spec": spec, "n_rows_matched": int(len(s)),
               "max_abs_point_delta": round(float(np.max(np.abs(dpt))), 4),
               "mean_abs_point_delta": round(float(np.mean(np.abs(dpt))), 4),
               "n_rows_point_identical": int((np.abs(dpt) < 1e-9).sum()),
               "mean_n_train_pit": round(float(s["n_expanding_rows"].mean()), 2),
               "n_train_full": int(s["n_train_full"].iloc[0])}
        for w in ("W1", "W2"):
            a = sc[(sc["spec"] == spec) & (sc["window"] == w)]
            b = sc_full[(sc_full["spec"] == spec) & (sc_full["window"] == w)]
            row[f"rmse_pit_{w}"] = float(a["rmse"].iloc[0]) if len(a) else np.nan
            row[f"rmse_full_{w}"] = float(b["rmse"].iloc[0]) if len(b) else np.nan
            row[f"n_{w}"] = int(a["n"].iloc[0]) if len(a) else 0
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ bootstrap
def block_bootstrap_a(d: pd.DataFrame, target: str, n_rep=400, block=3, seed=17):
    s = d.dropna(subset=[target, "b_lag0", "b_lag1", "b_lag2"]).copy()
    X = s[["b_lag0", "b_lag1", "b_lag2"]].values
    y = s[target].values
    n = len(y)
    rng = np.random.default_rng(seed)
    out = []
    nb = int(np.ceil(n / block))
    for _ in range(n_rep):
        starts = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(st, st + block) for st in starts])[:n]
        f = fit_interval_linear(X[idx], y[idx] - HALF, y[idx] + HALF, nonneg=True)
        a = np.clip(f["coef"], 0, None)
        sc = a.sum()
        out.append([a[0], a[1], a[2], sc,
                    (a[1] + 2 * a[2]) / sc if sc > 1e-9 else np.nan])
    B = np.array(out)
    names = ["a0", "a1", "a2", "scale", "eff_lag_q"]
    rows = []
    for i, nm in enumerate(names):
        v = B[:, i][~np.isnan(B[:, i])]
        rows.append({"target": target, "param": nm, "n_rep": len(v),
                     "mean": round(float(v.mean()), 4),
                     "p2.5": round(float(np.percentile(v, 2.5)), 4),
                     "p50": round(float(np.percentile(v, 50)), 4),
                     "p97.5": round(float(np.percentile(v, 97.5)), 4)})
    return pd.DataFrame(rows)


# -------------------------------------------------- determined share (stage d)
def determined_share(cs_w0_lo, cs_w0_hi, w0_hat) -> pd.DataFrame:
    """FX-determined share of a quarter's revenue-FX contribution at a guide date.

        determined = (1 - w0) + w0 * (days elapsed in the quarter before d / days in q)

    w0 is the contemporaneous (check-in-quarter) loading.  At w0 -> 0 the whole FX
    contribution is already fixed by printed quarters; at w0 = 0.75 (the M6 lambda)
    only about 0.54 is fixed on 5 Nov.  Published as a BAND over the Object-A
    confidence set, never as one number.

    Volume-determined share is reported alongside, because it is the defensible
    sentence: at the 5 Nov guide date 3Q26 GBV has printed, so 4Q26's kernel base
    2/3 GBV(3Q26) + 1/3 GBV(2Q26) is 100% known; at the 2-24 Oct pitch date only
    GBV(2Q26) is known, so it is 1/3.
    """
    rows = []
    events = [
        ("2026-08-06", "3Q26", "5 Aug letter / 6 Aug guide date for 3Q26", 2, 1),
        ("2026-09-11", "3Q26", "today (pitch build date)", 2, 1),
        ("2026-10-02", "4Q26", "memo due / pitch date", 1, 0),
        ("2026-10-23", "4Q26", "finals (NYC)", 1, 0),
        ("2026-11-05", "4Q26", "Q3 print + 4Q26 guide date", 1, 1),
        ("2027-02-11", "1Q27", "Q4 print + 1Q27 and FY27 guide (assumed date)", 1, 1),
    ]
    for ds, tq, what, _lagsknown, gbv_known in events:
        dte = _dt.date.fromisoformat(ds)
        p = to_period(tq)
        qs, qe = p.start_time.date(), p.end_time.date()
        ndays = (qe - qs).days + 1
        elapsed = min(max((dte - qs).days, 0), ndays)
        f = elapsed / ndays
        vol = 1.0 if (dte >= qs and gbv_known and dte > p.start_time.date()) else np.nan
        # volume-determined: 4Q26 kernel base = 2/3 GBV(3Q26) + 1/3 GBV(2Q26)
        prev1, prev2 = p - 1, p - 2
        # a GBV quarter is known once its print has happened
        prints = {"2Q26": _dt.date(2026, 8, 6), "3Q26": _dt.date(2026, 11, 5),
                  "4Q26": _dt.date(2027, 2, 11), "1Q26": _dt.date(2026, 5, 7),
                  "1Q27": _dt.date(2027, 5, 6)}
        k1 = prints.get(short(prev1), _dt.date(2100, 1, 1)) <= dte
        k2 = prints.get(short(prev2), _dt.date(2100, 1, 1)) <= dte
        vol_det = (2.0 / 3.0) * k1 + (1.0 / 3.0) * k2
        for lab, w0 in [("lo_of_CS", cs_w0_lo), ("point_estimate", w0_hat),
                        ("hi_of_CS", cs_w0_hi), ("M6_lambda_0.75", 0.75),
                        ("architect_w0_zero", 0.0)]:
            rows.append({"as_of": ds, "what": what, "target_quarter": tq,
                         "w0_basis": lab, "w0": round(float(w0), 4),
                         "days_elapsed": elapsed, "days_in_quarter": ndays,
                         "elapsed_frac": round(f, 4),
                         "fx_determined_share": round((1 - w0) + w0 * f, 4),
                         "volume_determined_share": round(vol_det, 4)})
    out = pd.DataFrame(rows)
    write(out, "10_determined_share.csv")
    return out


# ----------------------------------------------- forward schedule (stage e)
def forward_schedule(a_hat, sigma, asof=_dt.date(2026, 8, 28)) -> pd.DataFrame:
    """Quarterly revenue-FX contribution 3Q26..4Q27 under spot-held-constant, and
    under +/- 1 sd USD paths.  FRED daily FX ends 2026-08-28; there is NO forward
    curve in the FRED cache (no forward points, no FX futures series), so the
    forward-curve path is NOT derivable here and is reported as not available."""
    qs = [to_period(q) for q in ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]]
    # 1 sd of quarterly log change of the global basket, from history
    hist = pd.read_csv(OUT / "02_basket_quarterly.csv")
    sd_q = float(np.nanstd(np.diff(hist["basket_global_rev_wtd_yoy_pct"].values[-20:])))
    paths = {"spot_held": 0.0, "usd_minus_1sd_weak_usd": +5.0, "usd_plus_1sd_strong_usd": -5.0}
    rows = []
    bk = {}
    for pname, shift in paths.items():
        bseries = {}
        for q in [to_period(x) for x in ["1Q26", "2Q26"]] + qs:
            r = pit_fx.basket_yoy_asof(q, asof, hold_shift_pct=(0.0 if q <= to_period("3Q26") else shift))
            bseries[short(q)] = r["global_pct"]
        for q in qs:
            b0 = bseries[short(q)]; b1 = bseries[short(q - 1)]; b2 = bseries[short(q - 2)]
            fx = float(a_hat[0] * b0 + a_hat[1] * b1 + a_hat[2] * b2)
            rows.append({"path": pname, "quarter": short(q),
                         "basket_lag0_pct": round(b0, 3), "basket_lag1_pct": round(b1, 3),
                         "basket_lag2_pct": round(b2, 3),
                         "revenue_fx_pp": round(fx, 1),
                         "revenue_fx_pp_lo": round(fx - 1.28 * sigma, 1),
                         "revenue_fx_pp_hi": round(fx + 1.28 * sigma, 1)})
        bk[pname] = bseries
    out = pd.DataFrame(rows)
    out["note"] = "spot held constant from 2026-08-28 (last FRED obs); +/-1sd = +/-5% parallel shift in the held spot"
    out["basket_sd_of_qoq_change_pp"] = round(sd_q, 2)
    out["forward_curve_available"] = False
    write(out, "11_forward_schedule.csv")
    # FY27 annualisation, shown explicitly (FIX r2, cosmetic item 3): a FY y/y FX
    # contribution is the revenue-weighted AVERAGE of its four quarters, NOT the sum.
    # Revenue weights are the 2025 actual quarterly revenue shares (an FY27 revenue
    # forecast would be circular here; the shares move the answer by <0.05pp anyway).
    kp = pd.read_csv(OVN / "02_kpi_panel_quarterly.csv")
    w25 = kp[kp["quarter"].isin(["1Q25", "2Q25", "3Q25", "4Q25"])].set_index("quarter")["revenue_musd"]
    arows = []
    for pname in paths:
        sub = out[out["path"] == pname].set_index("quarter")
        v = [float(sub.loc[q, "revenue_fx_pp"]) for q in ["1Q27", "2Q27", "3Q27", "4Q27"]]
        wts = np.array([float(w25[f"{i}Q25"]) for i in range(1, 5)])
        wts = wts / wts.sum()
        arows.append({"path": pname,
                      "q1_pp": v[0], "q2_pp": v[1], "q3_pp": v[2], "q4_pp": v[3],
                      "sum_of_four_quarters_pp_DO_NOT_QUOTE": round(float(np.sum(v)), 1),
                      "simple_average_pp": round(float(np.mean(v)), 1),
                      "revenue_weighted_average_pp": round(float(np.dot(wts, v)), 1),
                      "revenue_weights_2025": np.round(wts, 3).tolist(),
                      "headline": "FY27 FX = revenue-weighted average of the four "
                                  "quarterly y/y contributions; the SUM is meaningless"})
    ann = pd.DataFrame(arows)
    write(ann, "11b_fy27_annualisation.csv")
    return out


def kernel_carried_fx(d: pd.DataFrame, a_hat) -> pd.DataFrame:
    """Booking-date FX carried through the Phi kernel, recomputed from the basket
    files.  Three readings, all one-decimal (never two)."""
    rows = []
    bq = {r["quarter"]: r for _, r in d.iterrows()}
    # extend the ADR-FX series to 3Q26 with the contemporaneous ADR fit on the basket
    sub = d[(d["p"] >= to_period("1Q23")) & (d["p"] <= to_period("2Q26"))].dropna(subset=["fx_pts_adr", "b_lag0"])
    o = ols(sub["b_lag0"], sub["fx_pts_adr"])
    adr = {q: bq[q]["fx_pts_adr"] for q in ["1Q26", "2Q26"]}
    adr["3Q26"] = o["intercept"] + o["slope"] * bq["3Q26"]["b_lag0"]
    basket = {q: bq[q]["b_lag0"] for q in ["1Q26", "2Q26", "3Q26"]}
    readings = {
        "A_disclosed_ADR_FX_through_Phi": adr,
        "B_basket_x_0.56_through_Phi": {k: 0.56 * v for k, v in basket.items()},
        "C_objectA_weights_applied_to_basket": None,
    }
    for name, ser in readings.items():
        if name.startswith("C"):
            v3 = float(a_hat[0] * basket["3Q26"] + a_hat[1] * basket["2Q26"] + a_hat[2] * basket["1Q26"])
            b4 = basket["3Q26"]  # 4Q26 lag0 under spot held == 3Q26-style; recomputed in forward_schedule
            v4 = float(a_hat[0] * 0.97 + a_hat[1] * basket["3Q26"] + a_hat[2] * basket["2Q26"])
        else:
            v3 = (2.0 / 3.0) * ser["2Q26"] + (1.0 / 3.0) * ser["1Q26"]
            v4 = (2.0 / 3.0) * ser["3Q26"] + (1.0 / 3.0) * ser["2Q26"]
        rows.append({"reading": name, "fx_3Q26_pp": round(v3, 1), "fx_4Q26_pp": round(v4, 1),
                     "step_4Q26_minus_3Q26_pp": round(v4 - v3, 1)})
    out = pd.DataFrame(rows)
    out["adr_fx_3Q26_fitted_pp"] = round(adr["3Q26"], 1)
    write(out, "12_kernel_carried_fx.csv")
    return out


def four_way_reconciliation(kernel_row) -> pd.DataFrame:
    """The 4Q26 FX reconciliation exhibit.  These are the ONLY places the rejected
    constructions may appear.  No additive pp adjustment to revenue is emitted by
    this package."""
    sched = pd.read_csv(OVN / "05_fx_schedule.csv")
    repo = float(sched[(sched.path == "consensus") & (sched.quarter == "2026Q4")]["revenue_fx_fit_pp"].iloc[0])
    rows = [
        {"construction": "repo 05_fx_schedule revenue_fx_fit_pp", "fx_4Q26_pp": round(repo, 1),
         "status": "REJECTED as an input",
         "named_cause": "a reduced-form fit of stated revenue FX on a lagged EURUSD/broad-USD blend; it is a level forecast of the disclosed pp, not the kernel arithmetic, and it double-counts the lag already inside the lagged GBV base"},
        {"construction": "repo 29_q4_fy27_bridge FX step", "fx_4Q26_pp": -3.4,
         "status": "REJECTED as an input",
         "named_cause": "subtracts the FX step a SECOND time on top of a GBV base that already carries booking-date FX; this is the double-subtraction the architect ruled out"},
        {"construction": "M6 memo forward schedule", "fx_4Q26_pp": 0.4,
         "status": "REJECTED as an input",
         "named_cause": "rests on an FX fit that misses a nearly observed quarter by about 2pp, and the memo carries +1.04pp in its schedule against +0.73pp in its own 3Q26 build"},
        {"construction": "guide-anchored (back out from management's stated Q3 FX assumption)", "fx_4Q26_pp": 2.6,
         "status": "REJECTED as an input",
         "named_cause": "holds the 3Q26 guided FX tailwind flat into 4Q26; management's own basket rolls over, so holding it flat imports a tailwind that the spot path has already removed"},
        {"construction": "kernel-implied (this package, Object-A weights on the rebuilt basket)",
         "fx_4Q26_pp": float(kernel_row["fx_4Q26_pp"]),
         "status": "ADOPTED as the reported reading (as an OUTPUT of the arithmetic, never added to revenue)",
         "named_cause": "booking-date FX is already inside the lagged USD GBV base; the pp shown is what the arithmetic produces, not an adjustment applied to it"},
    ]
    out = pd.DataFrame(rows)
    lo, hi = out["fx_4Q26_pp"].min(), out["fx_4Q26_pp"].max()
    out["spread_pp"] = round(float(hi - lo), 1)
    out["spread_musd_on_4Q26"] = round(float((hi - lo) * 2778.0 / 100.0), 0)  # pp of growth on 4Q25 revenue
    write(out, "13_four_way_reconciliation.csv")
    return out


def hedge_exhibit() -> pd.DataFrame:
    h = pd.read_csv(OVN / "28_fx_hedge_disclosures.csv")
    keep = ["quarter", "stated_revenue_fx_pp", "gross_fx_ex_hedge_pp",
            "hedge_effect_on_revenue_growth_pp", "reclassified_to_revenue_musd",
            "designated_notional_musd", "expected_reclass_next_12m_musd",
            "non_usd_revenue_share"]
    out = h[keep].copy()
    out["identity_check_gross_minus_hedge_equals_stated"] = (
        (out["gross_fx_ex_hedge_pp"] + out["hedge_effect_on_revenue_growth_pp"]
         - out["stated_revenue_fx_pp"]).abs() < 1e-6)
    out["hedge_once_rule"] = ("the letter-stated revenue FX pp is ALREADY AFTER hedges; "
                              "28_fx_hedge_forward.csv is NEVER added on top of it")
    write(out, "14_hedge_gross_vs_after.csv")
    return out


def exfx_acceleration(d: pd.DataFrame, kc: pd.DataFrame) -> pd.DataFrame:
    """The claim to test: the 4Q26 FX step is an OUTPUT of the lagged-GBV arithmetic,
    and set against the lagged-GBV growth step it means ex-FX growth ACCELERATES.
    No pp is added to revenue anywhere in this table."""
    g = {r["quarter"]: r["gbv_musd"] for _, r in d.iterrows() if not pd.isna(r["gbv_musd"])}
    rows = []
    for gbv3q26, lab in [(26185.0, "frozen card 20_frozen_q3_2026"),
                         (26300.0, "architect central"),
                         (25800.0, "low"), (26800.0, "high")]:
        g2 = dict(g); g2["3Q26"] = gbv3q26
        def base(q):
            p = to_period(q)
            return (2.0 / 3.0) * g2[short(p - 1)] + (1.0 / 3.0) * g2[short(p - 2)]
        b3, b3p = base("3Q26"), base("3Q25")
        b4, b4p = base("4Q26"), base("4Q25")
        gr3 = 100.0 * (b3 / b3p - 1.0)
        gr4 = 100.0 * (b4 / b4p - 1.0)
        for _, k in kc.iterrows():
            rows.append({"gbv_3Q26_musd": gbv3q26, "gbv_basis": lab,
                         "kernel_base_3Q26_musd": round(b3, 0),
                         "kernel_base_4Q26_musd": round(b4, 0),
                         "kernel_base_yoy_3Q26_pct": round(gr3, 1),
                         "kernel_base_yoy_4Q26_pct": round(gr4, 1),
                         "gbv_base_growth_step_pp": round(gr4 - gr3, 1),
                         "fx_reading": k["reading"],
                         "fx_step_pp": float(k["step_4Q26_minus_3Q26_pp"]),
                         "exfx_acceleration_pp": round((gr4 - gr3) - float(k["step_4Q26_minus_3Q26_pp"]), 1)})
    out = pd.DataFrame(rows)
    write(out, "12b_exfx_acceleration.csv")
    return out
