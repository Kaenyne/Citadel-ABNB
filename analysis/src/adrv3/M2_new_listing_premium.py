"""ADR v3, workstream M, step 2: the new-listing price premium, per market x vintage and pooled by
region x quarter, on each price basis separately (2025 listed nightly rate; 2026 stay quote per night).

Listing age = dump date minus `first_review` (the age of the listing as a trading unit: the first stay
that left a review). `host_since` is the host's account age, not the listing's, and is reported as a
sensitivity only. Listings with no first_review (never reviewed) have not traded and are excluded from
the premium (they contribute no nights); their count is in M1.

Premium = coefficient on new (< 12 months) in
    log(price) = a_market + b_new * new + room_type dummies + c * log(accommodates) + d * bedrooms + e
fitted per market x vintage (descriptive, one market FE), and pooled per region x quarter x basis with
market fixed effects. Unweighted (listing-weighted) primary; weighted by number_of_reviews_l30d as the
stay-weighted variant (closer to what enters ADR). Entire home/apt only as a further variant.
Prices trimmed to the 1st to 99th percentile of the market x vintage and to > 0.

Run: py -3.13 analysis/src/adrv3/M2_new_listing_premium.py
Outputs: data/processed/adrv3/M/M2_new_listing_premium.csv (market x vintage cells),
         M2_new_listing_premium_region.csv (region x quarter x basis pooled with market FE)
"""
import glob
import os
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "M")
CACHE = os.path.join(OUT, "cache")
REG_CODE = {"NA": "NAM", "EMEA": "EMEA", "LatAm": "LatAm", "APAC": "APAC"}


def prep(df: pd.DataFrame, age_field: str = "first_review") -> pd.DataFrame:
    d = df[df.price_on_basis.notna() & (df.price_on_basis > 0) & df[age_field].notna()].copy()
    dd = pd.Timestamp(d.dump_date.iloc[0]) if len(d) else None
    if d.empty:
        return d
    lo, hi = d.price_on_basis.quantile([0.01, 0.99])
    d = d[(d.price_on_basis >= lo) & (d.price_on_basis <= hi)]
    d["age_days"] = (dd - d[age_field]).dt.days
    d = d[d.age_days >= 0]
    d["new"] = (d.age_days < 365).astype(float)
    d["lp"] = np.log(d.price_on_basis)
    d["acc"] = pd.to_numeric(d.accommodates, errors="coerce").clip(lower=1)
    d["lacc"] = np.log(d.acc)
    d["bed"] = pd.to_numeric(d.bedrooms, errors="coerce")
    d["bed"] = d.bed.fillna(d.bed.median() if d.bed.notna().any() else 1).clip(0, 10)
    d["rt"] = d.room_type.fillna("Entire home/apt").astype(str)
    d["w_l30"] = pd.to_numeric(d.number_of_reviews_l30d, errors="coerce").fillna(0).clip(lower=0)
    return d


def wls_coef(X: np.ndarray, y: np.ndarray, w: np.ndarray | None = None) -> tuple[float, float]:
    """coefficient and HC0-style standard error of the first column of X (X includes an intercept)."""
    if w is None:
        w = np.ones(len(y))
    sw = np.sqrt(w)
    Xw, yw = X * sw[:, None], y * sw
    XtX = Xw.T @ Xw
    try:
        beta = np.linalg.solve(XtX, Xw.T @ yw)
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        return np.nan, np.nan
    e = yw - Xw @ beta
    meat = (Xw * e[:, None]).T @ (Xw * e[:, None])
    V = XtX_inv @ meat @ XtX_inv
    return float(beta[0]), float(np.sqrt(max(V[0, 0], 0)))


def design(d: pd.DataFrame, fe: str | None = None) -> np.ndarray:
    cols = [d.new.values, d.lacc.values, d.bed.values]
    rts = sorted(d.rt.unique())
    for r in rts[1:]:
        cols.append((d.rt == r).astype(float).values)
    if fe is not None:
        levels = sorted(d[fe].unique())
        for l in levels[1:]:
            cols.append((d[fe] == l).astype(float).values)
    cols.append(np.ones(len(d)))
    X = np.column_stack(cols)
    # drop any regressor without variation (a constant bedrooms column made Paris 4Q23 singular); keep new and intercept
    keep = [0] + [j for j in range(1, X.shape[1] - 1) if np.nanstd(X[:, j]) > 0] + [X.shape[1] - 1]
    return X[:, keep]


def cell_stats(d: pd.DataFrame, label: str, fe: str | None = None) -> dict:
    new, old = d[d.new == 1], d[d.new == 0]
    r = dict(variant=label, n_new=int(len(new)), n_old=int(len(old)),
             median_new=float(new.price_on_basis.median()) if len(new) else np.nan,
             median_old=float(old.price_on_basis.median()) if len(old) else np.nan,
             mean_new=float(new.price_on_basis.mean()) if len(new) else np.nan,
             mean_old=float(old.price_on_basis.mean()) if len(old) else np.nan)
    r["raw_median_premium_pct"] = 100 * (r["median_new"] / r["median_old"] - 1) if r["median_old"] else np.nan
    r["raw_mean_premium_pct"] = 100 * (r["mean_new"] / r["mean_old"] - 1) if r["mean_old"] else np.nan
    r["raw_logmean_premium_pct"] = 100 * (new.lp.mean() - old.lp.mean()) if len(new) and len(old) else np.nan
    if len(new) >= 30 and len(old) >= 100:
        X = design(d, fe)
        b, se = wls_coef(X, d.lp.values)
        r["hedonic_premium_logpts"], r["hedonic_se"] = 100 * b, 100 * se
        w = d.w_l30.values
        if (w > 0).sum() >= 200 and new.w_l30.sum() > 0:
            m = w > 0
            bw, sew = wls_coef(design(d[m], fe), d.lp.values[m], w[m])
            r["hedonic_premium_l30d_weighted_logpts"], r["hedonic_se_l30d_weighted"] = 100 * bw, 100 * sew
            r["n_weighted_new"], r["n_weighted_old"] = int((m & (d.new == 1)).sum()), int((m & (d.new == 0)).sum())
        else:
            r["hedonic_premium_l30d_weighted_logpts"] = r["hedonic_se_l30d_weighted"] = np.nan
            r["n_weighted_new"] = r["n_weighted_old"] = 0
    else:
        for k in ["hedonic_premium_logpts", "hedonic_se", "hedonic_premium_l30d_weighted_logpts", "hedonic_se_l30d_weighted"]:
            r[k] = np.nan
        r["n_weighted_new"] = r["n_weighted_old"] = 0
    return r


def main():
    t0 = time.time()
    cen = pd.read_csv(os.path.join(OUT, "M1_dump_census.csv"), keep_default_na=False)
    cen = cen[(cen.source_format != "error") & (cen.price_basis.isin(["listed_nightly", "quote_per_night"]))]
    rows, pooled_frames = [], []
    for i, r in cen.reset_index(drop=True).iterrows():
        stem = f"{r.market}_{r.dump_date}_listings"
        df = pd.read_parquet(os.path.join(CACHE, stem + ".parquet"))
        base = dict(market=r.market, region=REG_CODE.get(r.region, r.region), dump_date=r.dump_date, quarter=r.quarter,
                    price_basis=r.price_basis, scope_flag=r.scope_flag, usable_for_premium=r.usable_for_premium)
        d = prep(df, "first_review")
        if d.empty:
            continue
        rows.append({**base, "age_field": "first_review", **cell_stats(d, "all_rooms")})
        de = d[d.rt == "Entire home/apt"]
        if len(de):
            rows.append({**base, "age_field": "first_review", **cell_stats(de, "entire_home")})
        dh = prep(df, "host_since")
        if len(dh):
            rows.append({**base, "age_field": "host_since", **cell_stats(dh, "all_rooms")})
        if str(r.usable_for_premium) == "True":
            keep = d[["new", "lp", "lacc", "bed", "rt", "w_l30", "price_on_basis"]].copy()
            keep["market"] = r.market
            keep["region"] = base["region"]
            keep["quarter"] = r.quarter
            keep["price_basis"] = r.price_basis
            keep["scope_flag"] = r.scope_flag
            pooled_frames.append(keep)
        if (i + 1) % 25 == 0:
            print(f"[{i + 1}/{len(cen)}] {stem} {time.time() - t0:.0f}s", flush=True)
    cells = pd.DataFrame(rows)
    cells.to_csv(os.path.join(OUT, "M2_new_listing_premium.csv"), index=False, encoding="utf-8")
    print(f"cells: {len(cells)} rows")
    # pooled by region x quarter x basis with market FE (and global on all markets with market FE)
    P = pd.concat(pooled_frames, ignore_index=True)
    prow = []
    groups = [("region", g) for g in P.region.unique()] + [("global", None)]
    for scope, reg in groups:
        sub = P if reg is None else P[P.region == reg]
        for (q, basis), d in sub.groupby(["quarter", "price_basis"]):
            for label, dd in [("all_rooms", d), ("entire_home", d[d.rt == "Entire home/apt"])]:
                for sf, ddd in [("all_scope", dd), ("full_scope_only", dd[dd.scope_flag == "full"])]:
                    if ddd.new.sum() < 100 or (ddd.new == 0).sum() < 300:
                        continue
                    st = cell_stats(ddd, label, fe="market")
                    prow.append(dict(region=reg or "GLOBAL", quarter=q, price_basis=basis, scope=sf,
                                     n_markets=int(ddd.market.nunique()), markets=";".join(sorted(ddd.market.unique())), **st))
    pooled = pd.DataFrame(prow)
    pooled.to_csv(os.path.join(OUT, "M2_new_listing_premium_region.csv"), index=False, encoding="utf-8")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 500)
    show = pooled[(pooled.variant == "all_rooms") & (pooled.scope == "all_scope")]
    print("\npooled hedonic premium (log points, market FE), all rooms, unweighted:")
    print(show.pivot_table(index=["price_basis", "quarter"], columns="region", values="hedonic_premium_logpts").round(1).to_string())
    print("\npooled hedonic premium, l30d-review weighted:")
    print(show.pivot_table(index=["price_basis", "quarter"], columns="region", values="hedonic_premium_l30d_weighted_logpts").round(1).to_string())
    print("\nn_new by region/quarter/basis:")
    print(show.pivot_table(index=["price_basis", "quarter"], columns="region", values="n_new").fillna(0).astype(int).to_string())
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
