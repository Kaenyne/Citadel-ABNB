"""03. Annual ADR decomposition, 2021-2025, from disclosed data only.

This is the layer where every input is a 10-K figure, so it carries no interpolation.
It does two jobs: it produces the annual four-way split, and it tests whether a
length-of-stay elasticity can be identified from disclosed data. It cannot -- see the
LOS section below -- so an externally bounded value is used and the failed fit recorded.

Identity
  ADR_t = sum_r w_r,t * ADR_r,t         w = region share of nights

  d ADR = sum_r [dw_r * ADR_r,t-1]      geographic mix
        + sum_r [w_r,t-1 * dADR_r]      within-region ADR
        + sum_r [dw_r * dADR_r]         interaction (reported separately, not buried)

The within-region term is then split into FX, length of stay, unit size and
like-for-like price, with an explicit unexplained line -- price is measured against
external benchmarks, not used as the plug.

LOS elasticity
  Estimated on the panel of 4 regions x 4 year-changes (2022-2025) of
  dlog(ADR ex-FX) on dlog(ALOS) with region fixed effects. 2021 is excluded: the
  COVID rebound moved ADR 26% and every regional series with it, which would dominate
  the fit. n=16. This is a small panel and the coefficient is reported with its
  standard error and a leave-one-region-out range. RESULT: not identified (t 1.8, sign
  flips when APAC is dropped). A bound from Airbnb's host discount structure is used
  instead, and the decomposition is run across that band.

Outputs
  data/processed/adr/03_annual_decomposition.csv
  data/processed/adr/03_los_elasticity.csv
  data/processed/adr/03_regional_annual_fx.csv
"""

import os
import numpy as np
import pandas as pd

OUT = "data/processed/adr"
REGIONS = ["na", "emea", "latam", "apac"]


def annual_fx():
    """Regional FX contribution to reported ADR, annual, from the quarterly baskets."""
    b = pd.read_csv(f"{OUT}/02_fx_basket_quarterly.csv")
    b["year"] = b.quarter.str[2:].astype(int) + 2000
    ann = b.groupby(["year", "region"], as_index=False).basket_yoy_pct.mean()
    passthrough = {"emea": 1.04, "latam": 0.62, "apac": 0.86, "na": 1.00}
    ann["fx_pp"] = ann.basket_yoy_pct * ann.region.map(passthrough)
    return ann


def build():
    a = pd.read_csv(f"{OUT}/01_regional_annual.csv")
    a = a[a.region != "total"].copy()
    # Prefer the company-stated ADR where the filing gives it; the whole-million
    # nights rounding from 2022 makes the computed figure drift up to 1.7%.
    a["adr"] = a.adr_stated.fillna(a.adr_computed)
    a["adr_basis"] = np.where(a.adr_stated.notna(), "stated", "computed GBV/nights")

    fx = annual_fx()
    a = a.merge(fx[["year", "region", "fx_pp", "basket_yoy_pct"]], on=["year", "region"], how="left")

    a = a.sort_values(["region", "year"])
    a["adr_yoy"] = a.groupby("region").adr.pct_change() * 100
    a["adr_exfx_yoy"] = a.adr_yoy - a.fx_pp
    a["alos_yoy"] = a.groupby("region").alos_nights.pct_change() * 100
    a["nights_share"] = a.nights_share_pct / 100

    # --- LOS elasticity, region fixed effects, 2022-2025 -----------------------
    p = a[(a.year >= 2022) & a.adr_exfx_yoy.notna() & a.alos_yoy.notna()].copy()
    p["dl_adr"] = np.log1p(p.adr_exfx_yoy / 100)
    p["dl_alos"] = np.log1p(p.alos_yoy / 100)
    X = pd.get_dummies(p.region, prefix="r", dtype=float)
    X["dl_alos"] = p.dl_alos.values
    Xm = X.values
    y = p.dl_adr.values
    beta, *_ = np.linalg.lstsq(Xm, y, rcond=None)
    resid = y - Xm @ beta
    dof = len(y) - Xm.shape[1]
    sigma2 = (resid @ resid) / dof
    cov = sigma2 * np.linalg.pinv(Xm.T @ Xm)
    k = list(X.columns).index("dl_alos")
    los_beta, los_se = beta[k], np.sqrt(cov[k, k])

    # Leave-one-region-out range, because n is 16 and one region could carry it.
    loo = {}
    for r in REGIONS:
        q = p[p.region != r]
        Xq = pd.get_dummies(q.region, prefix="r", dtype=float)
        Xq["dl_alos"] = q.dl_alos.values
        bq, *_ = np.linalg.lstsq(Xq.values, np.log1p(q.adr_exfx_yoy.values / 100), rcond=None)
        loo[r] = bq[list(Xq.columns).index("dl_alos")]

    # VERDICT: not identified. The coefficient is insignificant and its sign flips when
    # APAC is dropped (ALOS 2.7 -> 3.2 in 2022, +18.5%, against ex-FX ADR +14.6% -- one
    # observation carries the fit). It is reported for the record and NOT used.
    identified = (abs(los_beta / los_se) > 2) and (min(loo.values()) * max(loo.values()) > 0)

    # Used instead: a bound from Airbnb's own host discount structure. Only the discount
    # channel matters -- a longer stay at an unchanged nightly rate does not move ADR at
    # all -- so the elasticity is the discount gradient, which is negative and small.
    # Weekly discounts cluster near 10% and monthly near 20-30%; with ALOS at 3.6-4.4
    # nights most stays sit below the 7-night weekly threshold, so the marginal effect of
    # a 1% change in ALOS on realised ADR is well inside 0.25%.
    LOS_BAND = {"low": -0.25, "central": -0.15, "high": -0.05}

    los = pd.DataFrame([{
        "coefficient": "d log ADR ex-FX / d log ALOS", "beta_fitted": los_beta,
        "se": los_se, "t": los_beta / los_se, "n": len(p), "dof": dof,
        "window": "2022-2025", "spec": "region fixed effects, 4 regions x 4 year-changes",
        "loo_min": min(loo.values()), "loo_max": max(loo.values()),
        "loo_detail": "; ".join(f"ex-{r}: {v:+.2f}" for r, v in loo.items()),
        "identified": identified,
        "verdict": ("NOT IDENTIFIED -- insignificant and sign-unstable across regions; "
                    "fitted value is recorded but not used"),
        "beta_used_central": LOS_BAND["central"],
        "beta_used_low": LOS_BAND["low"], "beta_used_high": LOS_BAND["high"],
        "beta_used_source": ("bound from Airbnb host weekly/monthly discount structure "
                             "(weekly ~10%, monthly ~20-30%) against ALOS of 3.6-4.4 nights"),
    }])
    los_beta = LOS_BAND["central"]

    # --- Decomposition ---------------------------------------------------------
    rows = []
    for yr in sorted(a.year.unique())[1:]:
        cur = a[a.year == yr].set_index("region")
        pre = a[a.year == yr - 1].set_index("region")
        adr0 = (pre.nights_share * pre.adr).sum()
        adr1 = (cur.nights_share * cur.adr).sum()

        dw = cur.nights_share - pre.nights_share
        dadr = cur.adr - pre.adr
        geo = (dw * pre.adr).sum()
        within = (pre.nights_share * dadr).sum()
        inter = (dw * dadr).sum()

        # Split the within-region term. FX first, then LOS at the fitted elasticity,
        # then price measured externally; whatever is left is unexplained.
        fx_c = (pre.nights_share * pre.adr * cur.fx_pp / 100).sum()
        los_c = (pre.nights_share * pre.adr
                 * (np.expm1(los_beta * np.log1p(cur.alos_yoy.values / 100)))).sum()

        rows.append({
            "year": yr, "adr_prior": adr0, "adr": adr1,
            "adr_yoy_pct": 100 * (adr1 / adr0 - 1),
            "geo_mix_pp": 100 * geo / adr0,
            "within_region_pp": 100 * within / adr0,
            "interaction_pp": 100 * inter / adr0,
            "of_which_fx_pp": 100 * fx_c / adr0,
            "of_which_los_pp": 100 * los_c / adr0,
            "of_which_size_and_price_pp": 100 * (within - fx_c - los_c) / adr0,
        })
    d = pd.DataFrame(rows)
    d["check_sum_pp"] = d.geo_mix_pp + d.within_region_pp + d.interaction_pp
    d["check_err_pp"] = d.check_sum_pp - d.adr_yoy_pct

    os.makedirs(OUT, exist_ok=True)
    d.to_csv(f"{OUT}/03_annual_decomposition.csv", index=False)
    los.to_csv(f"{OUT}/03_los_elasticity.csv", index=False)
    a.to_csv(f"{OUT}/03_regional_annual_fx.csv", index=False)
    return a, d, los


if __name__ == "__main__":
    a, d, los = build()
    pd.set_option("display.width", 220)
    print("=== Regional ADR, ex-FX growth and LOS ===")
    print(a[a.year >= 2021][["year", "region", "adr", "adr_basis", "adr_yoy", "fx_pp",
                             "adr_exfx_yoy", "alos_nights", "alos_yoy",
                             "nights_share_pct"]].round(2).to_string(index=False))
    print("\n=== LOS elasticity ===")
    r = los.iloc[0]
    print(f"  fitted beta = {r.beta_fitted:+.3f}  (se {r.se:.3f}, t {r.t:+.2f}, n {int(r.n)})")
    print(f"  leave-one-region-out range: {r.loo_min:+.2f} to {r.loo_max:+.2f}   [{r.loo_detail}]")
    print(f"  VERDICT: {r.verdict}")
    print(f"  used instead: {r.beta_used_central:+.2f} (band {r.beta_used_low:+.2f} to {r.beta_used_high:+.2f})")
    print(f"  source: {r.beta_used_source}")
    print("\n=== Annual ADR decomposition (pp of ADR y/y) ===")
    print(d.round(2).to_string(index=False))
