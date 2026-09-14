"""ADR v3, workstream M, step 4: the new-listing composition term, quarterly 1Q23 to 3Q26 to date.

term_r(t) [pp of ex-FX ADR y/y] = premium_r(t) [log points / 100] x d_share_r(t) [pp]
    premium_r(t): M2 pooled hedonic premium (market FE) for region r, on the price basis observable in
                  quarter t (listed nightly rate through 3Q25; none in 4Q25, carried from 3Q25; stay quote
                  from 1Q26). Quarters before a region's first priced dump carry its earliest premium
                  (flag premium_source = carried_back). The 2026 quote-basis premium is a different object
                  from the 2025 listed-basis premium and the two are never differenced.
    d_share_r(t): M3 y/y change in the share of reviews (stays) from listings under 12 months old,
                  review-weighted across the region's E markets.
Elasticity assumption: one. With ADR = s P_new + (1 - s) P_old, d ln ADR / ds = (P_new - P_old) / ADR,
which is the premium in log points to first order, so a 1 pp rise in the new-listing share at a 10 log
point premium adds 0.10 pp to ADR y/y. This assumes the listed or quoted price gap between age groups
equals the realised price gap (assumed; new-listing promotions and discounts are not in the listed price).
Global term = FY25 nights-share weighted sum of regional terms (NA 31.4, EMEA 36.8, LatAm 17.0, APAC 14.9).

Primary specification (fixed before any score was seen): variant all_rooms, unweighted hedonic, region
pooling with market FE, all-scope dumps, review-weighted raw d_share. Sensitivities: l30d-weighted premium,
entire-home premium, wedge-corrected d_share, vintage-matched-only markets, global pooled premium.

Also: correlation of the term with H's residual and with disclosed ex-FX ADR y/y, and the note-08
walk-forward of the term as a feature (I0 protocol), levels and first differences, 1Q24 onward.

Run: py -3.13 analysis/src/adrv3/M4_term_quarterly.py
Outputs: data/processed/adrv3/M/M4_term_quarterly.csv (all variants, regional and global),
         M4_premium_by_region_quarter.csv (the premium path used, with source flags), M4_feature_tests.csv
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "M")
sys.path.insert(0, os.path.join(ROOT, "analysis", "src", "adrq3"))
import I0_protocol as I0  # noqa: E402

WEIGHTS = {"NAM": 31.4, "EMEA": 36.8, "LatAm": 17.0, "APAC": 14.9}
REGIONS = list(WEIGHTS)
QUARTERS = [f"{q}Q{y}" for y in range(23, 27) for q in range(1, 5)]
QUARTERS = [q for q in QUARTERS if q <= "4Q26"][: QUARTERS.index("3Q26") + 1]


def qorder(q):
    return (2000 + int(q[-2:])) * 4 + int(q[0]) - 1


def basis_for_quarter(q: str) -> str:
    o = qorder(q)
    if o <= qorder("3Q25"):
        return "listed_nightly"
    if o == qorder("4Q25"):
        return "none"
    return "quote_per_night"


def premium_path(pooled: pd.DataFrame, variant: str, weighted: bool, scope: str, region: str) -> pd.DataFrame:
    col = "hedonic_premium_l30d_weighted_logpts" if weighted else "hedonic_premium_logpts"
    secol = "hedonic_se_l30d_weighted" if weighted else "hedonic_se"
    p = pooled[(pooled.variant == variant) & (pooled.scope == scope) & (pooled.region == region)].copy()
    p = p.dropna(subset=[col])
    rows = []
    for q in QUARTERS:
        b = basis_for_quarter(q)
        if b == "none":
            # 4Q25: no price in any dump; carry the last listed-basis quarter
            src = p[(p.price_basis == "listed_nightly") & (p.quarter.map(qorder) <= qorder(q))].sort_values("quarter", key=lambda s: s.map(qorder))
            if src.empty:
                rows.append(dict(quarter=q, region=region, premium_logpts=np.nan, premium_se=np.nan, premium_basis="none", premium_source="missing"))
                continue
            r = src.iloc[-1]
            rows.append(dict(quarter=q, region=region, premium_logpts=r[col], premium_se=r[secol], premium_basis="listed_nightly",
                             premium_source=f"carried_from_{r.quarter}", n_new=r.n_new, n_old=r.n_old, n_markets=r.n_markets))
            continue
        same = p[(p.price_basis == b) & (p.quarter == q)]
        if not same.empty:
            r = same.iloc[0]
            rows.append(dict(quarter=q, region=region, premium_logpts=r[col], premium_se=r[secol], premium_basis=b,
                             premium_source="measured", n_new=r.n_new, n_old=r.n_old, n_markets=r.n_markets))
            continue
        onb = p[p.price_basis == b].copy()
        onb["dist"] = (onb.quarter.map(qorder) - qorder(q)).abs()
        if onb.empty:
            rows.append(dict(quarter=q, region=region, premium_logpts=np.nan, premium_se=np.nan, premium_basis=b, premium_source="missing"))
            continue
        r = onb.sort_values("dist").iloc[0]
        how = "carried_back" if qorder(r.quarter) > qorder(q) else "carried_forward"
        rows.append(dict(quarter=q, region=region, premium_logpts=r[col], premium_se=r[secol], premium_basis=b,
                         premium_source=f"{how}_from_{r.quarter}", n_new=r.n_new, n_old=r.n_old, n_markets=r.n_markets))
    return pd.DataFrame(rows)


def build_term(pooled, shares, variant, weighted, scope, share_subset, share_col, label):
    prem = pd.concat([premium_path(pooled, variant, weighted, scope, r) for r in REGIONS], ignore_index=True)
    prem["variant"] = label
    sh = shares[(shares.subset == share_subset) & (shares.region.isin(REGIONS))]
    rows = []
    for q in QUARTERS:
        tot, wsum, parts = 0.0, 0.0, {}
        for r in REGIONS:
            pr = prem[(prem.quarter == q) & (prem.region == r)]
            s = sh[(sh.quarter == q) & (sh.region == r)]
            if pr.empty or s.empty or pd.isna(pr.iloc[0].premium_logpts):
                continue
            prem_lp = float(pr.iloc[0].premium_logpts)
            ds = float(s.iloc[0][share_col])
            term = prem_lp / 100 * ds
            parts[r] = dict(premium=prem_lp, d_share=ds, term=term, source=pr.iloc[0].premium_source, basis=pr.iloc[0].premium_basis,
                            share_construction=s.iloc[0].construction, n_markets=int(s.iloc[0].n_markets))
            rows.append(dict(variant=label, quarter=q, region=r, premium_logpts=prem_lp, premium_basis=pr.iloc[0].premium_basis,
                             premium_source=pr.iloc[0].premium_source, d_share_pp=ds, share_construction=s.iloc[0].construction,
                             n_share_markets=int(s.iloc[0].n_markets), term_pp=term, weight=WEIGHTS[r]))
            tot += WEIGHTS[r] * term
            wsum += WEIGHTS[r]
        if wsum:
            rows.append(dict(variant=label, quarter=q, region="GLOBAL_NW", premium_logpts=np.nan, premium_basis=basis_for_quarter(q),
                             premium_source=";".join(sorted({v["source"].split("_from_")[0] for v in parts.values()})),
                             d_share_pp=sum(WEIGHTS[r] * parts[r]["d_share"] for r in parts) / wsum,
                             share_construction=";".join(sorted({c for v in parts.values() for c in v["share_construction"].split(";")})),
                             n_share_markets=sum(v["n_markets"] for v in parts.values()), term_pp=tot / wsum, weight=wsum,
                             regions_covered=len(parts)))
    return pd.DataFrame(rows), prem


def main():
    pooled = pd.read_csv(os.path.join(OUT, "M2_new_listing_premium_region.csv"), keep_default_na=False, na_values=[""])
    shares = pd.read_csv(os.path.join(OUT, "M3_new_listing_share_region.csv"), keep_default_na=False, na_values=[""])
    specs = [
        ("primary", "all_rooms", False, "all_scope", "all", "d_share_rw_pp"),
        ("l30d_weighted_premium", "all_rooms", True, "all_scope", "all", "d_share_rw_pp"),
        ("entire_home_premium", "entire_home", False, "all_scope", "all", "d_share_rw_pp"),
        ("full_scope_premium", "all_rooms", False, "full_scope_only", "all", "d_share_rw_pp"),
        ("wedge_corrected_share", "all_rooms", False, "all_scope", "all", "d_share_wedge_corrected_rw_pp"),
        ("equal_weighted_share", "all_rooms", False, "all_scope", "all", "d_share_eq_pp"),
        ("vintage_matched_only_share", "all_rooms", False, "all_scope", "vintage_matched_only", "d_share_rw_pp"),
    ]
    terms, prems = [], []
    for label, variant, weighted, scope, subset, col in specs:
        t, p = build_term(pooled, shares, variant, weighted, scope, subset, col, label)
        terms.append(t)
        prems.append(p)
    # global pooled premium x global share as a further variant
    gp = premium_path(pooled, "all_rooms", False, "all_scope", "GLOBAL")
    gs = shares[(shares.subset == "all") & (shares.region == "GLOBAL_NW")]
    grows = []
    for q in QUARTERS:
        pr, s = gp[gp.quarter == q], gs[gs.quarter == q]
        if pr.empty or s.empty or pd.isna(pr.iloc[0].premium_logpts):
            continue
        grows.append(dict(variant="global_pooled_premium", quarter=q, region="GLOBAL_NW", premium_logpts=pr.iloc[0].premium_logpts,
                          premium_basis=pr.iloc[0].premium_basis, premium_source=pr.iloc[0].premium_source, d_share_pp=s.iloc[0].d_share_rw_pp,
                          share_construction=s.iloc[0].construction, n_share_markets=int(s.iloc[0].n_markets),
                          term_pp=pr.iloc[0].premium_logpts / 100 * s.iloc[0].d_share_rw_pp, weight=100.0, regions_covered=4))
    terms.append(pd.DataFrame(grows))
    gp["variant"] = "global_pooled_premium"
    prems.append(gp)
    T = pd.concat(terms, ignore_index=True)
    T["qo"] = T.quarter.map(qorder)
    T = T.sort_values(["variant", "region", "qo"]).drop(columns="qo")
    T.to_csv(os.path.join(OUT, "M4_term_quarterly.csv"), index=False, encoding="utf-8")
    pd.concat(prems, ignore_index=True).to_csv(os.path.join(OUT, "M4_premium_by_region_quarter.csv"), index=False, encoding="utf-8")

    # correlations and note-08 walk-forward against the H residual and ex-FX ADR
    H = pd.read_csv(os.path.join(ROOT, "data", "processed", "q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
    labels = [q for q in QUARTERS if q in H.index]
    tests = []
    for label in T.variant.unique():
        g = T[(T.variant == label) & (T.region == "GLOBAL_NW")].set_index("quarter").term_pp
        x = np.array([g.get(q, np.nan) for q in labels], float)
        for tname, y in [("residual_pricing_pp", H.loc[labels, "residual_pricing_pp"].values.astype(float)),
                         ("adr_exfx_yoy_pp", H.loc[labels, "adr_exfx_yoy_pp"].values.astype(float))]:
            for form, xx, yy in [("level", x, y), ("first_difference", np.diff(x, prepend=np.nan), np.diff(y, prepend=np.nan))]:
                row = I0.score(f"{label} term ({form})", xx, yy, labels, "1Q24", "partial: premium is in-quarter, share is quarter-to-date")
                row.update(target=tname, variant=label, form=form)
                tests.append(row)
    F = pd.DataFrame(tests)
    F.to_csv(os.path.join(OUT, "M4_feature_tests.csv"), index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 500)
    print("global term by variant, pp of ex-FX ADR y/y:")
    print(T[T.region == "GLOBAL_NW"].pivot(index="quarter", columns="variant", values="term_pp").loc[QUARTERS].round(3).to_string())
    print("\nprimary variant by region:")
    P = T[T.variant == "primary"]
    print(P.pivot(index="quarter", columns="region", values="term_pp").loc[QUARTERS].round(3).to_string())
    print("\nprimary premium path (log pts) by region:")
    print(P[P.region != "GLOBAL_NW"].pivot(index="quarter", columns="region", values="premium_logpts").loc[QUARTERS].round(1).to_string())
    print(P[P.region != "GLOBAL_NW"].pivot(index="quarter", columns="region", values="premium_source").loc[QUARTERS].to_string())
    print("\nfeature tests:")
    print(F[["variant", "form", "target", "n", "r", "perm_p", "wf_n", "wf_rmse", "wf_rmse_naive", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "sign_acc"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
