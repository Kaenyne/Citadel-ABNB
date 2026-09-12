"""fx_lag / fits.py -- Stage (b) ADR contemporaneous fits, and Objects A / B / C.

Scoring rule used everywhere: the disclosed revenue-FX series is a LETTER-ROUNDED
INTEGER.  Every observation is scored on [x-0.5, x+0.5].  A Gaussian point
likelihood on this target is not admissible and is never used here.
The disclosed ADR-FX series is letter-rounded to one decimal -> [x-0.05, x+0.05].
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from common import (OVN, OUT, interval_loglik, profile_sigma, fit_interval_linear,
                    write, to_period)

CHI2_95_3 = float(stats.chi2.ppf(0.95, 3))
NON_USD_SHARE = 0.56          # disclosed, 28_fx_hedge_disclosures.csv, 1Q25 onward


# ------------------------------------------------------------------ helpers
def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n = len(y); dof = n - 2
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r = float(np.corrcoef(x, y)[0, 1])
    return {"intercept": float(beta[0]), "slope": float(beta[1]),
            "se_slope": float(se[1]), "t_slope": float(beta[1] / se[1]),
            "p_slope": float(2 * (1 - stats.t.cdf(abs(beta[1] / se[1]), dof))),
            "r": r, "n": n, "rmse": float(np.sqrt(resid @ resid / n))}


def loo_rmse_ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    e = []
    for i in range(len(y)):
        m = np.ones(len(y), bool); m[i] = False
        b = np.polyfit(x[m], y[m], 1)
        e.append(y[i] - np.polyval(b, x[i]))
    return float(np.sqrt(np.mean(np.square(e))))


def interval_rmse(mu, y, half):
    """RMSE of the distance from mu to the scoring interval [y-half, y+half].
    Zero inside the band. This is the interval-scored analogue of RMSE."""
    mu = np.asarray(mu, float); y = np.asarray(y, float)
    d = np.maximum(np.maximum((y - half) - mu, mu - (y + half)), 0.0)
    return float(np.sqrt(np.mean(d ** 2)))


# ------------------------------------------------ (b) ADR contemporaneous fit
def stage_b(d: pd.DataFrame) -> pd.DataFrame:
    """Reproduce 05_fx_fits.csv, then refit with the interval likelihood."""
    post22 = d[(d["p"] >= to_period("1Q23")) & (d["p"] <= to_period("2Q26"))]
    ex21 = d[(d["p"] >= to_period("2Q22")) & (d["p"] <= to_period("2Q26"))]
    published = pd.read_csv(OVN / "05_fx_fits.csv")

    rows = []
    specs = [
        ("adr_fx", "eurusd", "fx_pts_adr", "eurusd_yoy_macro", "post22", post22),
        ("adr_fx", "usd_broad", "fx_pts_adr", "usd_broad_yoy_macro", "post22", post22),
        ("adr_fx", "eurusd", "fx_pts_adr", "eurusd_yoy_macro", "ex21", ex21),
        ("adr_fx", "usd_broad", "fx_pts_adr", "usd_broad_yoy_macro", "ex21", ex21),
        ("rev_fx", "usd_broad", "fx_pts_revenue", "usd_broad_yoy_macro", "post22", post22),
        ("rev_fx", "eurusd", "fx_pts_revenue", "eurusd_yoy_macro", "post22", post22),
        ("adr_fx", "basket_global", "fx_pts_adr", "b_lag0", "post22", post22),
        ("rev_fx", "basket_global", "fx_pts_revenue", "b_lag0", "post22", post22),
    ]
    for tgt, drv, ycol, xcol, win, sub in specs:
        s = sub.dropna(subset=[ycol, xcol])
        if len(s) < 5:
            continue
        o = ols(s[xcol], s[ycol])
        half = 0.05 if ycol == "fx_pts_adr" else 0.5
        f = fit_interval_linear(np.column_stack([np.ones(len(s)), s[xcol].values]),
                                s[ycol].values - half, s[ycol].values + half)
        mu = np.column_stack([np.ones(len(s)), s[xcol].values]) @ f["coef"]
        cal = ols(mu, s[ycol].values)["slope"]
        pub = published[(published.target == tgt) & (published.driver == drv)
                        & (published.lag == 0) & (published.window == win)]
        rows.append({
            "target": tgt, "driver": drv, "window": win, "n": o["n"],
            "ols_slope": round(o["slope"], 4), "ols_intercept": round(o["intercept"], 4),
            "ols_r": round(o["r"], 4), "ols_rmse": round(o["rmse"], 4),
            "loo_rmse": round(loo_rmse_ols(s[xcol], s[ycol]), 4),
            "iv_slope": round(float(f["coef"][1]), 4),
            "iv_intercept": round(float(f["coef"][0]), 4),
            "iv_sigma": round(f["sigma"], 4),
            "iv_calibration_slope": round(cal, 4),
            "iv_interval_rmse": round(interval_rmse(mu, s[ycol].values, half), 4),
            "published_slope": (round(float(pub.slope.iloc[0]), 4) if len(pub) else np.nan),
            "published_r": (round(float(pub.r.iloc[0]), 4) if len(pub) else np.nan),
            "published_n": (int(pub.n.iloc[0]) if len(pub) else -1),
            "published_loo_rmse": (round(float(pub.loo_rmse.iloc[0]), 4) if len(pub) else np.nan),
            "reproduces": (bool(len(pub)) and abs(o["slope"] - float(pub.slope.iloc[0])) < 0.002
                           and o["n"] == int(pub.n.iloc[0])),
        })
    out = pd.DataFrame(rows)
    write(out, "05_stage_b_adr_contemporaneous_fits.csv")
    return out


# -------------------------------------------------------------- OBJECT A
def object_a(d: pd.DataFrame, target: str, label: str, grid_step=0.025, amax=0.90):
    """Joint interval-likelihood regression of the disclosed revenue-FX series on
    lag-0 / lag-1 / lag-2 revenue-weighted baskets, non-negative coefficients.

    mu_q = a0 b_q + a1 b_{q-1} + a2 b_{q-2};   scale s = a0+a1+a2;   w = a/s.
    Reported as a 3-d confidence set, never as a point.
    H0: a = 0.56 * (0, 2/3, 1/3)  -- the architect's Phi kernel at the disclosed
    non-USD revenue share.  LR test, 3 restrictions, sigma profiled out.
    """
    s = d.dropna(subset=[target, "b_lag0", "b_lag1", "b_lag2"]).copy()
    y = s[target].values
    half = 0.5
    lo, hi = y - half, y + half
    X = s[["b_lag0", "b_lag1", "b_lag2"]].values

    # ---- unrestricted MLE
    f = fit_interval_linear(X, lo, hi, nonneg=True)
    a_hat = np.clip(f["coef"], 0, None)
    ll_max = f["loglik"]

    # ---- 3-d confidence set on a grid, sigma profiled
    ax = np.arange(0.0, amax + 1e-9, grid_step)
    A = np.array(np.meshgrid(ax, ax, ax, indexing="ij")).reshape(3, -1).T   # (G,3)
    MU = A @ X.T                                                            # (G,n)
    sig_grid = np.concatenate([np.arange(0.15, 3.0, 0.05), np.arange(3.0, 6.0, 0.25)])
    best = np.full(len(A), -np.inf)
    for sg in sig_grid:
        p = stats.norm.cdf((hi - MU) / sg) - stats.norm.cdf((lo - MU) / sg)
        ll = np.log(np.clip(p, 1e-300, None)).sum(axis=1)
        np.maximum(best, ll, out=best)
    ll_grid_max = float(best.max())
    ll_ref = max(ll_max, ll_grid_max)
    keep = best >= ll_ref - CHI2_95_3 / 2.0
    CS = A[keep]
    scale = CS.sum(axis=1)
    ok = scale > 1e-9
    W = CS[ok] / scale[ok][:, None]
    efflag = W[:, 1] + 2 * W[:, 2]

    # ---- H0 test
    a0 = NON_USD_SHARE * np.array([0.0, 2.0 / 3.0, 1.0 / 3.0])
    ll_h0, sig_h0 = profile_sigma(X @ a0, lo, hi)
    lr = 2.0 * (ll_ref - ll_h0)
    p_h0 = float(1 - stats.chi2.cdf(lr, 3))

    # ---- H0 variants worth naming
    variants = {
        "H0_architect_phi_x_0.56": a0,
        "H0b_theo_pure_lag2_x_0.56": NON_USD_SHARE * np.array([0.0, 0.0, 1.0]),
        "H0c_contemporaneous_x_0.56": NON_USD_SHARE * np.array([1.0, 0.0, 0.0]),
        "H0d_pure_lag1_x_0.56": NON_USD_SHARE * np.array([0.0, 1.0, 0.0]),
        "H0e_phi_free_scale": None,          # weights fixed at (0,2/3,1/3), scale free
    }
    vrows = []
    for name, av in variants.items():
        if av is None:
            wfix = np.array([0.0, 2.0 / 3.0, 1.0 / 3.0])
            z = (X @ wfix).reshape(-1, 1)
            ff = fit_interval_linear(z, lo, hi, nonneg=True)
            ll = ff["loglik"]; df = 2; sc = float(ff["coef"][0]); sg = ff["sigma"]
            av = sc * wfix
        else:
            ll, sg = profile_sigma(X @ av, lo, hi)
            df = 3; sc = float(av.sum())
        lrv = 2.0 * (ll_ref - ll)
        vrows.append({"hypothesis": name, "a0": round(float(av[0]), 4),
                      "a1": round(float(av[1]), 4), "a2": round(float(av[2]), 4),
                      "scale": round(sc, 4), "sigma_hat": round(sg, 3),
                      "loglik": round(ll, 4), "lr_vs_free": round(lrv, 3),
                      "df": df, "p_value": round(float(1 - stats.chi2.cdf(lrv, df)), 4),
                      "rejected_at_5pct": bool(1 - stats.chi2.cdf(lrv, df) < 0.05),
                      "in_95_confidence_set": bool(lrv <= CHI2_95_3)})

    mu_hat = X @ a_hat
    res = {
        "label": label, "target": target, "n": int(len(s)),
        "first_q": s["quarter"].iloc[0], "last_q": s["quarter"].iloc[-1],
        "a0_hat": round(float(a_hat[0]), 4), "a1_hat": round(float(a_hat[1]), 4),
        "a2_hat": round(float(a_hat[2]), 4),
        "scale_hat": round(float(a_hat.sum()), 4),
        "w0_hat": round(float(a_hat[0] / a_hat.sum()), 4),
        "w1_hat": round(float(a_hat[1] / a_hat.sum()), 4),
        "w2_hat": round(float(a_hat[2] / a_hat.sum()), 4),
        "eff_lag_hat_q": round(float((a_hat[1] + 2 * a_hat[2]) / a_hat.sum()), 4),
        "sigma_hat": round(f["sigma"], 4),
        "loglik_free": round(ll_ref, 4),
        "cs_points": int(keep.sum()), "cs_grid_points": int(len(A)),
        "cs_a0_lo": round(float(CS[:, 0].min()), 3), "cs_a0_hi": round(float(CS[:, 0].max()), 3),
        "cs_a1_lo": round(float(CS[:, 1].min()), 3), "cs_a1_hi": round(float(CS[:, 1].max()), 3),
        "cs_a2_lo": round(float(CS[:, 2].min()), 3), "cs_a2_hi": round(float(CS[:, 2].max()), 3),
        "cs_scale_lo": round(float(scale.min()), 3), "cs_scale_hi": round(float(scale.max()), 3),
        "cs_w0_lo": round(float(W[:, 0].min()), 3), "cs_w0_hi": round(float(W[:, 0].max()), 3),
        "cs_w1_lo": round(float(W[:, 1].min()), 3), "cs_w1_hi": round(float(W[:, 1].max()), 3),
        "cs_w2_lo": round(float(W[:, 2].min()), 3), "cs_w2_hi": round(float(W[:, 2].max()), 3),
        "cs_efflag_lo": round(float(efflag.min()), 3), "cs_efflag_hi": round(float(efflag.max()), 3),
        "scale_0.56_in_cs": bool((scale.min() <= NON_USD_SHARE <= scale.max())),
        "H0_lr": round(float(lr), 3), "H0_df": 3, "H0_p": round(p_h0, 4),
        "H0_rejected_at_5pct": bool(p_h0 < 0.05),
        "calibration_slope": round(ols(mu_hat, y)["slope"], 4),
        "interval_rmse": round(interval_rmse(mu_hat, y, half), 4),
        "point_rmse_vs_stated": round(float(np.sqrt(np.mean((mu_hat - y) ** 2))), 4),
        "n_params": 4,
    }
    return res, pd.DataFrame(vrows), (s, X, y, lo, hi, a_hat, f["sigma"])


# -------------------------------------------------------------- OBJECT B
def object_b(d: pd.DataFrame) -> pd.DataFrame:
    """The revenue-FX minus ADR-FX wedge on the basket lags.

    ADR-FX is contemporaneous-at-booking by construction.  If the revenue leg
    needs a lag and the ADR leg does not, then the wedge IS the recognition lag,
    and its loading should sit on lags 1-2, not lag 0.
    Interval half-width = 0.5 (revenue integer) + 0.05 (ADR one-decimal) = 0.55.
    """
    rows = []
    for tgt, name in [("stated_revenue_fx_pp", "stated"), ("gross_fx_ex_hedge_pp", "gross_ex_hedge")]:
        s = d.dropna(subset=[tgt, "fx_pts_adr", "b_lag0", "b_lag1", "b_lag2"]).copy()
        wedge = s[tgt].values - s["fx_pts_adr"].values
        half = 0.55
        X = np.column_stack([np.ones(len(s)), s[["b_lag0", "b_lag1", "b_lag2"]].values])
        f = fit_interval_linear(X, wedge - half, wedge + half)
        mu = X @ f["coef"]
        # univariate loadings, for the "where does the wedge live" read
        uni = {}
        for L in (0, 1, 2):
            o = ols(s[f"b_lag{L}"], wedge)
            uni[f"uni_lag{L}_slope"] = round(o["slope"], 4)
            uni[f"uni_lag{L}_t"] = round(o["t_slope"], 3)
            uni[f"uni_lag{L}_r"] = round(o["r"], 4)
        rows.append({"wedge_of": name, "n": len(s),
                     "first_q": s["quarter"].iloc[0], "last_q": s["quarter"].iloc[-1],
                     "wedge_mean_pp": round(float(np.mean(wedge)), 3),
                     "wedge_sd_pp": round(float(np.std(wedge, ddof=1)), 3),
                     "c_const": round(float(f["coef"][0]), 4),
                     "c_lag0": round(float(f["coef"][1]), 4),
                     "c_lag1": round(float(f["coef"][2]), 4),
                     "c_lag2": round(float(f["coef"][3]), 4),
                     "sigma": round(f["sigma"], 4),
                     "interval_rmse": round(interval_rmse(mu, wedge, half), 4),
                     "n_params": 5, **uni})
    out = pd.DataFrame(rows)
    write(out, "07_object_b_wedge.csv")
    return out


# -------------------------------------------------------------- OBJECT C
def object_c(d: pd.DataFrame):
    """Reproduce the architect's falsification: season-demeaned conversion lambda
    regressed on the booking-to-check-in FX remeasurement wedge.
    Target to reproduce: slope 0.158, se 0.275, t 0.57, n 12.
    Pre-registered: |t| stays under 2 when 4Q26 is added.
    """
    s = d.dropna(subset=["lambda_pct", "b_lag0", "b_lag1", "b_lag2"]).copy()
    s["season"] = [p.quarter for p in s["p"]]
    # booking-to-check-in remeasurement: contemporaneous basket minus the
    # Phi-weighted basket of the quarters in which the stays were booked
    s["remeas_wedge"] = s["b_lag0"] - ((2.0 / 3.0) * s["b_lag1"] + (1.0 / 3.0) * s["b_lag2"])
    s["remeas_wedge_adr"] = s["fx_pts_adr"] - ((2.0 / 3.0) * s["adrfx_lag1"] + (1.0 / 3.0) * s["adrfx_lag2"])

    rows = []
    for nlab, sub in [("n12_3Q23_2Q26", s[(s["p"] >= to_period("3Q23")) & (s["p"] <= to_period("2Q26"))]),
                      ("n14_1Q23_2Q26", s[(s["p"] >= to_period("1Q23")) & (s["p"] <= to_period("2Q26"))])]:
        for wcol in ["remeas_wedge", "remeas_wedge_adr"]:
            sub2 = sub.dropna(subset=[wcol, "lambda_pct"]).copy()
            if len(sub2) < 6:
                continue
            sub2["lam_dm"] = sub2["lambda_pct"] - sub2.groupby("season")["lambda_pct"].transform("mean")
            sub2["w_dm"] = sub2[wcol] - sub2.groupby("season")[wcol].transform("mean")
            # demeaning-convention grid: the architect's documents say
            # "season-demeaned conversion" but do not say whether the regressor is
            # also demeaned.  All four conventions are reported.
            for ylab, xlab in [("lam_season_demeaned", "wedge_season_demeaned"),
                               ("lam_season_demeaned", "wedge_raw"),
                               ("lam_raw", "wedge_season_demeaned"),
                               ("lam_raw", "wedge_raw")]:
                yv = sub2["lam_dm"] if ylab.endswith("demeaned") else sub2["lambda_pct"]
                xv = sub2["w_dm"] if xlab.endswith("demeaned") else sub2[wcol]
                oo = ols(xv, yv)
                rows.append({"sample": nlab, "wedge": wcol,
                             "convention": f"{ylab} ~ {xlab}", "n": oo["n"],
                             "slope": round(oo["slope"], 4), "se": round(oo["se_slope"], 4),
                             "t": round(oo["t_slope"], 4), "p": round(oo["p_slope"], 4),
                             "r": round(oo["r"], 4), "iv_slope": np.nan, "iv_sigma": np.nan,
                             "interval_half_width_pp": np.nan,
                             "abs_t_under_2": bool(abs(oo["t_slope"]) < 2)})
            o = ols(sub2["w_dm"], sub2["lam_dm"])
            # interval version: lambda is a ratio of two rounded disclosures;
            # revenue is exact ($m), GBV is rounded to $0.1bn -> ~+/-0.05bn on the base
            half = float(np.mean(100.0 * sub2["revenue_musd"] * 50.0
                                 / (sub2["kernel_base_musd"] ** 2)))
            Xi = np.column_stack([np.ones(len(sub2)), sub2["w_dm"].values])
            fi = fit_interval_linear(Xi, sub2["lam_dm"].values - half, sub2["lam_dm"].values + half)
            rows.append({"sample": nlab, "wedge": wcol,
                         "convention": "HEADLINE lam_season_demeaned ~ wedge_season_demeaned",
                         "n": o["n"],
                         "slope": round(o["slope"], 4), "se": round(o["se_slope"], 4),
                         "t": round(o["t_slope"], 4), "p": round(o["p_slope"], 4),
                         "r": round(o["r"], 4),
                         "iv_slope": round(float(fi["coef"][1]), 4),
                         "iv_sigma": round(fi["sigma"], 4),
                         "interval_half_width_pp": round(half, 4),
                         "abs_t_under_2": bool(abs(o["t_slope"]) < 2)})
    out = pd.DataFrame(rows)
    write(out, "08_object_c_falsification.csv")

    # regional pass-through extension
    pt = pd.read_csv(OVN / "10_regional_fx_passthrough.csv")
    write(pt.assign(used_in_object_c=pt["region"].isin(["emea", "latam", "apac"])),
          "08b_regional_passthrough_used.csv")
    return out, s
