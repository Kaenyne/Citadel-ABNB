"""ADR v3, workstream M, step 6: the 3Q26-to-date value of the new-listing composition term with a band.

Point = primary specification (M4): quote-basis regional premium from the July and August 2026 dumps
times the review-weighted y/y change in the new-listing share of July 2026 reviews (vintage-matched
against July 2025 from the August 2025 dumps), FY25 nights weights.
Band = the range across the M4 specification variants (premium weighting, entire-home, full-scope,
share construction, global pooled premium) widened by the premium standard error (1 SE each way on the
primary), plus the 2Q26 value as the "full quarter" comparator. The band is a specification range, not
a statistical interval, and the share is one month of a three-month quarter.

Run: py -3.13 analysis/src/adrv3/M6_term_3q26.py
Output: data/processed/adrv3/M/M6_term_3q26.csv
"""
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "M")
WEIGHTS = {"NAM": 31.4, "EMEA": 36.8, "LatAm": 17.0, "APAC": 14.9}


def main():
    T = pd.read_csv(os.path.join(OUT, "M4_term_quarterly.csv"), keep_default_na=False, na_values=[""])
    prem = pd.read_csv(os.path.join(OUT, "M4_premium_by_region_quarter.csv"), keep_default_na=False, na_values=[""])
    rows = []
    q3 = T[T.quarter == "3Q26"]
    prim = q3[q3.variant == "primary"]
    for _, r in prim.iterrows():
        se = prem[(prem.variant == "primary") & (prem.quarter == "3Q26") & (prem.region == r.region)].premium_se
        se = float(se.iloc[0]) if len(se) and pd.notna(se.iloc[0]) else np.nan
        rows.append(dict(quarter="3Q26_to_date", region=r.region, variant="primary", premium_logpts=r.premium_logpts, premium_se=se,
                         premium_basis=r.premium_basis, premium_source=r.premium_source, d_share_pp=r.d_share_pp,
                         share_construction=r.share_construction, n_share_markets=r.n_share_markets, term_pp=r.term_pp,
                         label="descriptive: quote-basis premium (Jul-Aug 2026 dumps) x July 2026 share change, vintage-matched"))
    g = prim[prim.region == "GLOBAL_NW"].iloc[0]
    # SE band on the global term: premium +/- 1 SE per region, propagated with weights
    lo = hi = 0.0
    wsum = 0.0
    for _, r in prim[prim.region != "GLOBAL_NW"].iterrows():
        se = prem[(prem.variant == "primary") & (prem.quarter == "3Q26") & (prem.region == r.region)].premium_se
        se = float(se.iloc[0]) if len(se) and pd.notna(se.iloc[0]) else 0.0
        w = WEIGHTS[r.region]
        a, b = (r.premium_logpts - se) / 100 * r.d_share_pp, (r.premium_logpts + se) / 100 * r.d_share_pp
        lo += w * min(a, b)
        hi += w * max(a, b)
        wsum += w
    lo, hi = lo / wsum, hi / wsum
    variants = q3[q3.region == "GLOBAL_NW"].set_index("variant").term_pp
    q2 = T[(T.quarter == "2Q26") & (T.region == "GLOBAL_NW")].set_index("variant").term_pp
    band_lo = min(variants.min(), lo)
    band_hi = max(variants.max(), hi)
    rows.append(dict(quarter="3Q26_to_date", region="GLOBAL_NW", variant="band", premium_logpts=np.nan, premium_se=np.nan,
                     premium_basis="quote_per_night", premium_source="specification range + 1 SE on the primary premium",
                     d_share_pp=g.d_share_pp, share_construction=g.share_construction, n_share_markets=g.n_share_markets,
                     term_pp=g.term_pp, term_lo_pp=band_lo, term_hi_pp=band_hi,
                     variants=";".join(f"{k}={v:.3f}" for k, v in variants.items()),
                     term_2q26_primary_pp=float(q2.get("primary", np.nan)),
                     label="assumed band: min/max across M4 variants and +/- 1 SE of the primary regional premiums; July only"))
    rows.append(dict(quarter="4Q26", region="GLOBAL_NW", variant="carried", premium_basis="quote_per_night",
                     premium_source="3Q26 to date carried; no 4Q26 dump exists", term_pp=g.term_pp, term_lo_pp=band_lo, term_hi_pp=band_hi,
                     label="assumed: 4Q26 = 3Q26 to date (same premium; share change carried), band as 3Q26"))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "M6_term_3q26.csv"), index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 80)
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
