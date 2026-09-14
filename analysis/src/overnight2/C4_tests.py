"""
Workstream C, step 4. Does relative consumer strength explain the regional growth differential?

Target      diff_pp = regional nights y/y less TOTAL nights y/y, in percentage points.
Predictors  relative_z at lags 0, 1, 2 quarters; the 2-quarter change in relative_z at the same
            lags. Both are already relative to the global origin-weighted index, so a common
            global cycle is differenced out.
Spec        pooled with region fixed effects, i.e. both sides demeaned within region. A level
            regression without the fixed effect would only recover the structural fact that
            LatAm and APAC grow faster than NA, which is a penetration and expansion-strategy
            fact, not a consumer-cycle one.
Inference   permutation p, shuffling the predictor WITHIN region across quarters (20,000 draws),
            so the null keeps the region means and the predictor's own distribution.
Skill       leave-one-out RMSE against the naive model, which is the region mean differential.

Reads   data/processed/overnight2/C/regional_target_panel.csv
        data/processed/overnight2/C/regional_strength_quarterly.csv
        data/processed/overnight2/C/origin_country_panel.csv
        data/processed/overnight2/C/country_strength_monthly.csv
        C:/Users/krish/citadel-abnb/data/processed/overnight/02_kpi_panel_long.csv
Writes  data/processed/overnight2/C/C4_regression_panel.csv
        data/processed/overnight2/C/C4_fits.csv
        data/processed/overnight2/C/C4_origin_country_fits.csv
        data/processed/overnight2/C/C4_episode_checks.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

MAIN = Path(r"C:/Users/krish/citadel-abnb")
OUT = Path(__file__).resolve().parents[3] / "data/processed/overnight2/C"
RNG = np.random.default_rng(20260911)
NPERM = 20000

QORDER = [f"{q}Q{y}" for y in range(19, 27) for q in (1, 2, 3, 4)]
QIX = {q: i for i, q in enumerate(QORDER)}


def total_nights_yoy() -> pd.DataFrame:
    k = pd.read_csv(MAIN / "data/processed/overnight/02_kpi_panel_long.csv")
    n = k[k["metric"] == "nights_m"][["quarter", "value"]].copy()
    n["value"] = pd.to_numeric(n["value"], errors="coerce")
    n = n.dropna().drop_duplicates("quarter")
    n["ix"] = n["quarter"].map(QIX)
    n = n.dropna(subset=["ix"]).sort_values("ix").reset_index(drop=True)
    n["prior"] = n["value"].shift(4)
    n["total_yoy"] = (n["value"] / n["prior"] - 1.0) * 100.0
    return n[["quarter", "value", "total_yoy"]].rename(columns={"value": "nights_m"})


def build_panel() -> pd.DataFrame:
    tgt = pd.read_csv(OUT / "regional_target_panel.csv")
    tgt = tgt[tgt["metric"] == "nights_yoy_pct_destination"][["quarter", "region", "value", "halfwidth_pp"]]
    tot = total_nights_yoy()
    z = pd.read_csv(OUT / "regional_strength_quarterly.csv")
    z = z[["quarter", "region", "index_z", "global_z", "relative_z", "relative_z_chg1q", "relative_z_chg2q"]]

    # lagged predictors
    z["ix"] = z["quarter"].map(QIX)
    z = z.dropna(subset=["ix"]).sort_values(["region", "ix"])
    for lag in (1, 2):
        for col in ("relative_z", "relative_z_chg2q"):
            z[f"{col}_lag{lag}"] = z.groupby("region")[col].shift(lag)

    p = tgt.merge(tot[["quarter", "total_yoy", "nights_m"]], on="quarter", how="left").merge(
        z, on=["quarter", "region"], how="left")
    p["diff_pp"] = p["value"] - p["total_yoy"]
    p["ix"] = p["quarter"].map(QIX)
    return p.dropna(subset=["diff_pp", "relative_z"]).sort_values(["ix", "region"])


def demean(df: pd.DataFrame, cols: list[str], by: str) -> pd.DataFrame:
    d = df.copy()
    for c in cols:
        d[c + "_dm"] = d[c] - d.groupby(by)[c].transform("mean")
    return d


def ols(y: np.ndarray, x: np.ndarray) -> tuple[float, float, float]:
    """slope, t, r2 for a no-intercept fit on already demeaned data."""
    denom = float(x @ x)
    if denom <= 0:
        return np.nan, np.nan, np.nan
    b = float(x @ y) / denom
    resid = y - b * x
    dof = max(len(y) - 2, 1)           # -1 for the slope, -1 for the absorbed means (approx)
    s2 = float(resid @ resid) / dof
    se = np.sqrt(s2 / denom) if denom > 0 else np.nan
    t = b / se if se and se > 0 else np.nan
    ss_tot = float(y @ y)
    r2 = 1.0 - float(resid @ resid) / ss_tot if ss_tot > 0 else np.nan
    return b, t, r2


def perm_p(d: pd.DataFrame, ycol: str, xcol: str, by: str, nperm: int = NPERM) -> float:
    y = d[ycol].to_numpy(float)
    x = d[xcol].to_numpy(float)
    _, t0, _ = ols(y, x)
    if not np.isfinite(t0):
        return np.nan
    groups = [np.where(d[by].to_numpy() == g)[0] for g in d[by].unique()]
    hits = 0
    for _ in range(nperm):
        xs = x.copy()
        for g in groups:
            xs[g] = RNG.permutation(x[g])
        xs = xs - np.repeat([xs[g].mean() for g in groups],
                            [len(g) for g in groups])[np.argsort(np.concatenate(groups))]
        _, t, _ = ols(y, xs)
        if np.isfinite(t) and abs(t) >= abs(t0):
            hits += 1
    return (hits + 1) / (nperm + 1)


def loo(d: pd.DataFrame, ycol: str, xcol: str, by: str) -> tuple[float, float]:
    """LOO RMSE of the fixed-effect-plus-slope model vs the fixed-effect-only naive model."""
    errs_m, errs_n = [], []
    for i in d.index:
        tr = d.drop(index=i)
        te = d.loc[i]
        means_y = tr.groupby(by)[ycol].mean()
        means_x = tr.groupby(by)[xcol].mean()
        g = te[by]
        if g not in means_y.index:
            continue
        yd = tr[ycol] - tr[by].map(means_y)
        xd = tr[xcol] - tr[by].map(means_x)
        b, _, _ = ols(yd.to_numpy(float), xd.to_numpy(float))
        pred = means_y[g] + b * (te[xcol] - means_x[g])
        errs_m.append(te[ycol] - pred)
        errs_n.append(te[ycol] - means_y[g])
    rm = float(np.sqrt(np.mean(np.square(errs_m)))) if errs_m else np.nan
    rn = float(np.sqrt(np.mean(np.square(errs_n)))) if errs_n else np.nan
    return rm, rn


def run_fits(p: pd.DataFrame) -> pd.DataFrame:
    preds = ["relative_z", "relative_z_lag1", "relative_z_lag2",
             "relative_z_chg2q", "relative_z_chg2q_lag1", "relative_z_chg2q_lag2"]
    samples = {
        "all_disclosed_3Q22_2Q26": p,
        "from_1Q24": p[p["ix"] >= QIX["1Q24"]],
        "bucket_era_4Q24_2Q26": p[p["ix"] >= QIX["4Q24"]],
    }
    rows = []
    for sname, sub in samples.items():
        for pred in preds:
            d = sub.dropna(subset=[pred]).copy()
            if len(d) < 8 or d["region"].nunique() < 3:
                rows.append({"sample": sname, "predictor": pred, "n": len(d), "note": "too few observations"})
                continue
            d = demean(d, ["diff_pp", pred], "region")
            y = d["diff_pp_dm"].to_numpy(float)
            x = d[pred + "_dm"].to_numpy(float)
            b, t, r2 = ols(y, x)
            pp = perm_p(d, "diff_pp_dm", pred + "_dm", "region")
            rm, rn = loo(d.reset_index(drop=True), "diff_pp", pred, "region")
            rows.append({"sample": sname, "predictor": pred, "n": len(d),
                         "n_regions": d["region"].nunique(),
                         "slope_pp_per_z": round(b, 3), "t": round(t, 2), "r2_within": round(r2, 3),
                         "perm_p": round(pp, 4),
                         "loo_rmse_model": round(rm, 2), "loo_rmse_naive": round(rn, 2),
                         "loo_improvement_pct": round((rn - rm) / rn * 100.0, 1) if rn and np.isfinite(rn) else np.nan,
                         "note": ""})
    return pd.DataFrame(rows)


def ols2(y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """multivariate no-intercept fit on demeaned data: coefficients, t stats, within r2."""
    XtX = X.T @ X
    try:
        beta = np.linalg.solve(XtX, X.T @ y)
    except np.linalg.LinAlgError:
        return np.full(X.shape[1], np.nan), np.full(X.shape[1], np.nan), np.nan
    resid = y - X @ beta
    dof = max(len(y) - X.shape[1] - 1, 1)
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.pinv(XtX)
    se = np.sqrt(np.diag(cov))
    t = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)
    r2 = 1.0 - float(resid @ resid) / float(y @ y) if float(y @ y) > 0 else np.nan
    return beta, t, r2


def mean_reversion_controls(p: pd.DataFrame) -> pd.DataFrame:
    """Is the relative_z slope anything more than mean reversion in the differential?"""
    d = p.sort_values(["region", "ix"]).copy()
    d["diff_pp_lag1"] = d.groupby("region")["diff_pp"].shift(1)
    rows = []
    for sname, sub in {"all_disclosed_3Q22_2Q26": d, "bucket_era_4Q24_2Q26": d[d["ix"] >= QIX["4Q24"]]}.items():
        s = sub.dropna(subset=["diff_pp", "relative_z", "diff_pp_lag1"]).copy()
        if len(s) < 10:
            continue
        s = demean(s, ["diff_pp", "relative_z", "diff_pp_lag1"], "region")
        y = s["diff_pp_dm"].to_numpy(float)
        for label, cols in [("relative_z only", ["relative_z_dm"]),
                            ("lagged differential only", ["diff_pp_lag1_dm"]),
                            ("both", ["relative_z_dm", "diff_pp_lag1_dm"])]:
            X = s[cols].to_numpy(float)
            beta, t, r2 = ols2(y, X)
            rows.append({"sample": sname, "spec": label, "n": len(s),
                         "b_relative_z": round(beta[cols.index("relative_z_dm")], 3) if "relative_z_dm" in cols else np.nan,
                         "t_relative_z": round(t[cols.index("relative_z_dm")], 2) if "relative_z_dm" in cols else np.nan,
                         "b_diff_lag1": round(beta[cols.index("diff_pp_lag1_dm")], 3) if "diff_pp_lag1_dm" in cols else np.nan,
                         "t_diff_lag1": round(t[cols.index("diff_pp_lag1_dm")], 2) if "diff_pp_lag1_dm" in cols else np.nan,
                         "r2_within": round(r2, 3)})
    return pd.DataFrame(rows)


def leave_region_out(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sname, sub in {"all_disclosed_3Q22_2Q26": p, "bucket_era_4Q24_2Q26": p[p["ix"] >= QIX["4Q24"]]}.items():
        for drop in [None] + sorted(sub["region"].unique()):
            s = sub if drop is None else sub[sub["region"] != drop]
            s = s.dropna(subset=["diff_pp", "relative_z"]).copy()
            if s["region"].nunique() < 2 or len(s) < 8:
                continue
            s = demean(s, ["diff_pp", "relative_z"], "region")
            b, t, r2 = ols(s["diff_pp_dm"].to_numpy(float), s["relative_z_dm"].to_numpy(float))
            rows.append({"sample": sname, "dropped_region": drop or "none", "n": len(s),
                         "slope_pp_per_z": round(b, 3), "t": round(t, 2), "r2_within": round(r2, 3)})
    return pd.DataFrame(rows)


def accel_fits(p: pd.DataFrame) -> pd.DataFrame:
    """Same tests with the target changed to the CHANGE in the differential, which is the
    relative acceleration the 5 November print trades on."""
    d = p.sort_values(["region", "ix"]).copy()
    d["diff_accel_pp"] = d.groupby("region")["diff_pp"].diff()
    rows = []
    for sname, sub in {"all_disclosed_3Q22_2Q26": d, "bucket_era_4Q24_2Q26": d[d["ix"] >= QIX["4Q24"]]}.items():
        for pred in ["relative_z", "relative_z_chg2q", "relative_z_chg1q"]:
            s = sub.dropna(subset=["diff_accel_pp", pred]).copy()
            if len(s) < 10:
                rows.append({"sample": sname, "predictor": pred, "n": len(s), "note": "too few"})
                continue
            s = demean(s, ["diff_accel_pp", pred], "region")
            b, t, r2 = ols(s["diff_accel_pp_dm"].to_numpy(float), s[pred + "_dm"].to_numpy(float))
            pp = perm_p(s, "diff_accel_pp_dm", pred + "_dm", "region")
            rm, rn = loo(s.reset_index(drop=True), "diff_accel_pp", pred, "region")
            rows.append({"sample": sname, "predictor": pred, "n": len(s),
                         "slope_pp_per_z": round(b, 3), "t": round(t, 2), "r2_within": round(r2, 3),
                         "perm_p": round(pp, 4), "loo_rmse_model": round(rm, 2),
                         "loo_rmse_naive": round(rn, 2), "note": ""})
    return pd.DataFrame(rows)


def origin_fits() -> pd.DataFrame:
    org = pd.read_csv(OUT / "origin_country_panel.csv")
    org = org[org["value_kind"] != "domestic"].copy()   # domestic-only figure is a different basis
    cs = pd.read_csv(OUT / "country_strength_monthly.csv", parse_dates=["date"])
    cs["q"] = pd.PeriodIndex(cs["date"], freq="Q")
    cq = cs.groupby(["country", "q"], as_index=False)["z_mean"].mean()
    cq["quarter"] = cq["q"].apply(lambda x: f"{x.quarter}Q{str(x.year)[2:]}")
    cq = cq.sort_values(["country", "q"])
    cq["z_chg2q"] = cq.groupby("country")["z_mean"].transform(lambda s: s - s.shift(2))
    for lag in (1, 2):
        cq[f"z_mean_lag{lag}"] = cq.groupby("country")["z_mean"].shift(lag)

    tot = total_nights_yoy()
    d = org.merge(cq, left_on=["country_iso3", "quarter"], right_on=["country", "quarter"], how="left")
    d = d.merge(tot[["quarter", "total_yoy"]], on="quarter", how="left")
    d["diff_pp"] = d["value"] - d["total_yoy"]
    d.to_csv(OUT / "C4_origin_panel.csv", index=False)

    rows = []
    for pred in ["z_mean", "z_mean_lag1", "z_chg2q"]:
        sub = d.dropna(subset=["diff_pp", pred]).copy()
        # keep only countries with at least 2 observations, so a within-country slope exists
        keep = sub.groupby("country_iso3").size()
        sub = sub[sub["country_iso3"].isin(keep[keep >= 2].index)]
        if len(sub) < 6:
            rows.append({"predictor": pred, "n": len(sub), "note": "too few within-country observations"})
            continue
        sub = demean(sub, ["diff_pp", pred], "country_iso3")
        b, t, r2 = ols(sub["diff_pp_dm"].to_numpy(float), sub[pred + "_dm"].to_numpy(float))
        pp = perm_p(sub, "diff_pp_dm", pred + "_dm", "country_iso3", nperm=5000)
        rm, rn = loo(sub.reset_index(drop=True), "diff_pp", pred, "country_iso3")
        rows.append({"predictor": pred, "n": len(sub), "n_countries": sub["country_iso3"].nunique(),
                     "slope_pp_per_z": round(b, 2), "t": round(t, 2), "r2_within": round(r2, 3),
                     "perm_p": round(pp, 4), "loo_rmse_model": round(rm, 2), "loo_rmse_naive": round(rn, 2),
                     "note": ""})
    return pd.DataFrame(rows)


def episodes(p: pd.DataFrame) -> pd.DataFrame:
    """Would the index have called the 2025 NA slowdown and the 2025-26 LatAm / APAC strength?"""
    rows = []
    q = pd.read_csv(OUT / "regional_strength_quarterly.csv")
    q["ix"] = q["quarter"].map(QIX)
    for label, region, window in [
        ("2025 NA slowdown", "na", ["4Q24", "1Q25", "2Q25", "3Q25"]),
        ("2026 NA reacceleration", "na", ["4Q25", "1Q26", "2Q26"]),
        ("2025-26 LatAm strength", "latam", ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]),
        ("2025-26 APAC strength", "apac", ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]),
        ("2025-26 EMEA recovery", "emea", ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]),
    ]:
        sub = p[(p["region"] == region) & (p["quarter"].isin(window))]
        zz = q[(q["region"] == region) & (q["quarter"].isin(window))]
        if sub.empty:
            continue
        base = p[(p["region"] == region)]
        mean_diff = base["diff_pp"].mean()
        rows.append({
            "episode": label, "region": region, "quarters": " ".join(window),
            "mean_diff_pp_in_window": round(sub["diff_pp"].mean(), 2),
            "mean_diff_pp_full_sample": round(mean_diff, 2),
            "actual_direction_vs_own_mean": "above" if sub["diff_pp"].mean() > mean_diff else "below",
            "mean_relative_z_in_window": round(zz["relative_z"].mean(), 3),
            "mean_relative_z_chg2q_in_window": round(zz["relative_z_chg2q"].mean(), 3),
            "index_direction": "above" if zz["relative_z"].mean() > q[q["region"] == region]["relative_z"].mean() else "below",
        })
    r = pd.DataFrame(rows)
    r["index_called_it"] = r["actual_direction_vs_own_mean"] == r["index_direction"]
    return r


if __name__ == "__main__":
    p = build_panel()
    p.to_csv(OUT / "C4_regression_panel.csv", index=False)
    print("panel n =", len(p), "quarters", p["quarter"].min(), p["quarter"].max())
    print(p.pivot(index="quarter", columns="region", values="diff_pp").round(1).reindex(
        [q for q in QORDER if q in set(p["quarter"])]).to_string())
    print()

    fits = run_fits(p)
    fits.to_csv(OUT / "C4_fits.csv", index=False)
    print(fits.to_string(index=False))
    print()

    af = accel_fits(p)
    af.to_csv(OUT / "C4_acceleration_fits.csv", index=False)
    print("=== target = CHANGE in the differential (relative acceleration) ===")
    print(af.to_string(index=False))
    print()

    mr = mean_reversion_controls(p)
    mr.to_csv(OUT / "C4_mean_reversion.csv", index=False)
    print("=== is it just mean reversion in the differential? ===")
    print(mr.to_string(index=False))
    print()

    lro = leave_region_out(p)
    lro.to_csv(OUT / "C4_leave_region_out.csv", index=False)
    print("=== leave one region out ===")
    print(lro.to_string(index=False))
    print()

    of = origin_fits()
    of.to_csv(OUT / "C4_origin_country_fits.csv", index=False)
    print("=== origin-country tests ===")
    print(of.to_string(index=False))
    print()

    ep = episodes(p)
    ep.to_csv(OUT / "C4_episode_checks.csv", index=False)
    print("=== episode checks ===")
    print(ep.to_string(index=False))
