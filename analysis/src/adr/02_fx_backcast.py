"""02. Reconstruct the FX contribution to reported ADR before 2Q22.

Airbnb's letters give ex-FX ADR growth only from 2Q22. Reported ADR y/y is computable
from 3Q21 (the KPI panel starts 3Q20, so 3Q21 is the first quarter with a year-ago
base). That leaves 3Q21, 4Q21 and 1Q22 with a reported ADR and no ex-FX counterpart.

Method
  1. Build a regional currency basket y/y per quarter from 10_fx_basket.csv weights
     (judgement, anchored on the 10-K country split) and 10_fx_quarterly.csv levels,
     which run from 1Q18 -- far enough back to cover the whole reconstruction.
  2. Weight regions by their share of GBV, interpolated from the 10-K annual tables
     built in 01_annual_anchors.py. FX baskets move an order of magnitude faster than
     the mix does, so mix precision is second-order here.
  3. Apply WS10's estimated pass-through of a basket move into reported regional ADR
     (EMEA 1.04, LatAm 0.62, APAC 0.86). NA was not identified by WS10 -- its basket
     moves under 1.5pp across the whole sample -- so it is carried at 1.0 and the
     sensitivity to that choice is reported.
  4. Validate on 2Q22-2Q26, where the letters give the answer (n=17), against two
     benchmarks: the broad-USD fit used by WS08/WS13 (0.52 - 0.72 x USD y/y) and a
     naive zero.
  5. Backcast 3Q21, 4Q21, 1Q22.

Outputs
  data/processed/adr/02_fx_basket_quarterly.csv   regional and global basket y/y by quarter
  data/processed/adr/02_fx_backcast.csv           predicted vs disclosed FX effect, all quarters
  data/processed/adr/02_adr_exfx_reconstructed.csv  the ADR ex-FX series, disclosed + backcast
"""

import os
import numpy as np
import pandas as pd

OUT = "data/processed/adr"
PASSTHROUGH = {"emea": 1.04, "latam": 0.62, "apac": 0.86, "na": 1.00}
PASSTHROUGH_SRC = {
    "emea": "WS10 fit, r 0.987, n=10", "latam": "WS10 fit, r 0.996, n=7",
    "apac": "WS10 fit, r 0.972, n=5",
    "na": "ASSUMED 1.0 -- WS10 could not identify it (basket range <1.5pp)",
}


def qkey(q):
    """'3Q21' -> (2021, 3) for sorting."""
    return (int(q[2:]) + 2000, int(q[0]))


def load_baskets():
    """Regional basket y/y per quarter, in USD-per-unit terms (positive = weaker USD)."""
    w = pd.read_csv("data/processed/overnight/10_fx_basket.csv")
    # The file carries a summary row per region (currency == "BASKET", weight 1.00)
    # alongside the component legs. Including it double-counts every basket and halves
    # the result, so drop it; only the legs are used here.
    w = w[(w.currency != "BASKET") & (w.region != "global_revenue_weighted")].copy()
    fx = pd.read_csv("data/processed/overnight/10_fx_quarterly.csv", header=[0, 1])
    fx.columns = ["quarter"] + [f"{a}_{b}" for a, b in fx.columns[1:]]
    fx = fx[fx.quarter.notna() & fx.quarter.str.match(r"^\dQ\d\d$")].copy()

    # Each basket leg maps to a currency column; USD legs are 0 y/y by construction.
    rows = []
    for _, r in w.iterrows():
        ccy = r.currency if pd.isna(r.proxy_series) else r.proxy_series
        col = f"yoy_pct_{ccy}"
        for _, f in fx.iterrows():
            val = 0.0 if ccy == "USD" else pd.to_numeric(f.get(col), errors="coerce")
            rows.append({"quarter": f.quarter, "region": r.region,
                         "currency": ccy, "weight": r.weight, "ccy_yoy_pct": val})
    leg = pd.DataFrame(rows)
    leg["contrib"] = leg.weight * leg.ccy_yoy_pct

    b = leg.groupby(["quarter", "region"], as_index=False).agg(
        basket_yoy_pct=("contrib", "sum"), weight_sum=("weight", "sum"),
        n_missing=("ccy_yoy_pct", lambda s: int(s.isna().sum())))
    b["basket_yoy_pct"] = b.basket_yoy_pct / b.weight_sum
    return b


def gbv_shares_quarterly(quarters):
    """Regional GBV shares interpolated from the 10-K annual tables.

    Annual shares are placed at the mid-point of each year (Q2/Q3 boundary) and
    linearly interpolated; ends are held flat. GBV shares are mildly seasonal, which
    this ignores -- flagged in the note.
    """
    ann = pd.read_csv(f"{OUT}/01_regional_annual.csv")
    ann = ann[ann.region != "total"]
    piv = ann.pivot(index="year", columns="region", values="gbv_share_pct") / 100.0

    # Quarter -> continuous time in years, with the annual anchor at year + 0.5.
    idx = pd.DataFrame({"quarter": quarters})
    idx["y"] = [qkey(q)[0] + (qkey(q)[1] - 0.5) / 4 for q in idx.quarter]

    out = {"quarter": idx.quarter}
    for reg in ["na", "emea", "latam", "apac"]:
        out[f"gbv_share_{reg}"] = np.interp(
            idx.y, piv.index + 0.5, piv[reg].values,
            left=piv[reg].iloc[0], right=piv[reg].iloc[-1])
    s = pd.DataFrame(out)
    tot = s[[c for c in s.columns if c.startswith("gbv_share_")]].sum(axis=1)
    for c in s.columns:
        if c.startswith("gbv_share_"):
            s[c] = s[c] / tot
    return s


def build():
    kpi = pd.read_csv("data/processed/overnight/02_kpi_panel_quarterly.csv")
    kpi = kpi[["quarter", "adr_usd", "adr_yoy_reported_pct", "adr_yoy_exfx_pct",
               "fx_pts_adr"]].copy()

    b = load_baskets()
    piv = b.pivot(index="quarter", columns="region", values="basket_yoy_pct").reset_index()
    piv.columns.name = None
    piv = piv.rename(columns={r: f"basket_{r}" for r in ["na", "emea", "latam", "apac"]})

    df = kpi.merge(piv, on="quarter", how="left")
    df = df.merge(gbv_shares_quarterly(df.quarter.tolist()), on="quarter", how="left")
    df = df.sort_values("quarter", key=lambda s: s.map(qkey)).reset_index(drop=True)

    # Predicted FX contribution to reported ADR, in percentage points.
    df["fx_pred_pp"] = sum(
        df[f"gbv_share_{r}"] * PASSTHROUGH[r] * df[f"basket_{r}"]
        for r in ["na", "emea", "latam", "apac"])
    # Sensitivity: NA pass-through at 0 instead of 1.
    df["fx_pred_pp_na0"] = sum(
        df[f"gbv_share_{r}"] * (0.0 if r == "na" else PASSTHROUGH[r]) * df[f"basket_{r}"]
        for r in ["na", "emea", "latam", "apac"])

    # Benchmark: the broad-USD fit WS08/WS13 use. DTWEXBGS y/y is not in this file,
    # so it is reconstructed from the disclosed FX effect only where available.
    fit = df.dropna(subset=["fx_pts_adr"])
    if len(fit) > 2:
        sl, ic = np.polyfit(fit.fx_pred_pp, fit.fx_pts_adr, 1)
        df["fx_pred_calibrated_pp"] = ic + sl * df.fx_pred_pp
    else:
        sl = ic = np.nan
        df["fx_pred_calibrated_pp"] = np.nan

    v = df.dropna(subset=["fx_pts_adr", "fx_pred_pp"]).copy()
    stats = {
        "n_validation": len(v),
        "window": f"{v.quarter.iloc[0]}-{v.quarter.iloc[-1]}",
        "r_raw": v.fx_pred_pp.corr(v.fx_pts_adr),
        "rmse_raw_pp": float(np.sqrt(((v.fx_pred_pp - v.fx_pts_adr) ** 2).mean())),
        "rmse_calibrated_pp": float(np.sqrt(((v.fx_pred_calibrated_pp - v.fx_pts_adr) ** 2).mean())),
        "rmse_zero_pp": float(np.sqrt((v.fx_pts_adr ** 2).mean())),
        "calib_slope": sl, "calib_intercept": ic,
        "r_na0": v.fx_pred_pp_na0.corr(v.fx_pts_adr),
    }

    # Leave-one-out on the calibration, so the reported error is out of sample.
    loo = []
    for i in v.index:
        tr = v.drop(i)
        s2, i2 = np.polyfit(tr.fx_pred_pp, tr.fx_pts_adr, 1)
        loo.append(i2 + s2 * v.loc[i, "fx_pred_pp"])
    v["loo_pred"] = loo
    stats["rmse_loo_pp"] = float(np.sqrt(((v.loo_pred - v.fx_pts_adr) ** 2).mean()))

    # Final series: disclosed where the letters give it, backcast where they do not.
    df["fx_pts_adr_final"] = df.fx_pts_adr.where(
        df.fx_pts_adr.notna(), df.fx_pred_calibrated_pp)
    df["fx_basis"] = np.where(df.fx_pts_adr.notna(), "disclosed (letter)",
                              np.where(df.fx_pred_calibrated_pp.notna(),
                                       "backcast (basket, calibrated)", "n/a"))
    df["adr_yoy_exfx_final"] = df.adr_yoy_exfx_pct.where(
        df.adr_yoy_exfx_pct.notna(), df.adr_yoy_reported_pct - df.fx_pts_adr_final)
    df["adr_exfx_basis"] = np.where(df.adr_yoy_exfx_pct.notna(), "disclosed (letter)",
                                    np.where(df.adr_yoy_exfx_final.notna(),
                                             "reconstructed", "n/a"))

    os.makedirs(OUT, exist_ok=True)
    b.to_csv(f"{OUT}/02_fx_basket_quarterly.csv", index=False)
    df.to_csv(f"{OUT}/02_fx_backcast.csv", index=False)
    df[["quarter", "adr_usd", "adr_yoy_reported_pct", "fx_pts_adr_final", "fx_basis",
        "adr_yoy_exfx_final", "adr_exfx_basis"]].to_csv(
        f"{OUT}/02_adr_exfx_reconstructed.csv", index=False)
    return df, stats, v


if __name__ == "__main__":
    df, stats, v = build()
    pd.set_option("display.width", 220)
    print("=== Validation on the disclosed window ===")
    for k, val in stats.items():
        print(f"  {k:24s} {val if isinstance(val, (str, int)) else round(val, 3)}")
    print("\n  pass-through used:")
    for r, p in PASSTHROUGH.items():
        print(f"    {r:6s} {p:4.2f}   {PASSTHROUGH_SRC[r]}")

    print("\n=== Predicted vs disclosed FX effect on ADR (pp) ===")
    print(v[["quarter", "basket_na", "basket_emea", "basket_latam", "basket_apac",
             "fx_pred_pp", "fx_pred_calibrated_pp", "fx_pts_adr"]].round(2).to_string(index=False))

    print("\n=== Reconstructed ADR ex-FX ===")
    out = df[["quarter", "adr_usd", "adr_yoy_reported_pct", "fx_pts_adr_final",
              "adr_yoy_exfx_final", "adr_exfx_basis"]]
    print(out[out.adr_yoy_reported_pct.notna()].round(2).to_string(index=False))
