"""07. Assemble the full ADR decomposition with an explicit unexplained line.

Pulls together the four measured terms and reports what is left over:

  ADR y/y = geographic mix          (03, from 10-K annual regional anchors)
          + interaction             (03)
          + FX                      (02/02b, validated basket reconstruction)
          + length of stay          (03, externally bounded elasticity -- NOT fitted)
          + unit-size mix           (05, Inside Airbnb booking-weighted + hedonics)
          + like-for-like price     (06, external benchmarks, GBV-weighted)
          + UNEXPLAINED             (the residual, shown rather than hidden in price)

Every term carries a confidence flag. The point of this script is the last column: the
team asked for price to be measured rather than used as the plug, which means the
decomposition does not sum to zero by construction and the gap is the finding.

Output
  data/processed/adr/07_full_decomposition.csv
"""

import os
import numpy as np
import pandas as pd

OUT = "data/processed/adr"


def size_by_year():
    """Unit-size ADR contribution by year, with the sample behind it."""
    s = pd.read_csv(f"{OUT}/05_size_mix_summary.csv")
    y = s[s.scope == "year"].copy()
    # The year rows carry date_b_min; use it to label the year.
    y["year"] = pd.to_datetime(y.date_b_min).dt.year
    y = y.groupby("year", as_index=False).agg(
        size_mix_pp=("size_mix_pp_quote_basis", "mean"),
        size_n_pairs=("n_pairs", "max"), size_n_markets=("n_markets", "max"))
    return y


def build():
    d = pd.read_csv(f"{OUT}/03_annual_decomposition.csv")
    p = pd.read_csv(f"{OUT}/06_price_residual_annual.csv")
    s = size_by_year()

    keep = ["year", "adr_yoy_pct", "geo_mix_pp", "interaction_pp", "of_which_fx_pp",
            "of_which_los_pp", "of_which_size_and_price_pp"]
    df = d[keep].merge(
        p[["year", "price_measured_pp", "price_measured_lo_pp", "price_measured_hi_pp",
           "worst_confidence"]], on="year", how="left").merge(s, on="year", how="left")

    df["unexplained_pp"] = (df.of_which_size_and_price_pp
                            - df.size_mix_pp.fillna(0) - df.price_measured_pp)
    df["explained_pp"] = df.adr_yoy_pct - df.unexplained_pp
    df["pct_of_move_unexplained"] = 100 * df.unexplained_pp.abs() / df.adr_yoy_pct.abs()

    def conf(r):
        if pd.isna(r.price_measured_pp):
            return "not estimable -- no usable price benchmark"
        if pd.isna(r.size_mix_pp):
            return f"low -- no size-mix measurement this year; price {r.worst_confidence}"
        if r.size_n_markets < 3:
            return (f"low -- size mix rests on {int(r.size_n_markets)} city/cities "
                    f"({int(r.size_n_pairs)} pairs); price {r.worst_confidence}")
        return f"medium -- size mix {int(r.size_n_markets)} cities; price {r.worst_confidence}"

    df["confidence"] = df.apply(conf, axis=1)

    # Sum check on the terms that are definitionally exhaustive (03's identity).
    df["identity_check_pp"] = (df.geo_mix_pp + df.interaction_pp + df.of_which_fx_pp
                               + df.of_which_los_pp + df.of_which_size_and_price_pp
                               - df.adr_yoy_pct)

    os.makedirs(OUT, exist_ok=True)
    df.to_csv(f"{OUT}/07_full_decomposition.csv", index=False)
    return df


if __name__ == "__main__":
    df = build()
    pd.set_option("display.width", 240)
    cols = ["year", "adr_yoy_pct", "geo_mix_pp", "of_which_fx_pp", "of_which_los_pp",
            "size_mix_pp", "price_measured_pp", "interaction_pp", "unexplained_pp",
            "pct_of_move_unexplained", "identity_check_pp"]
    print("=== Full ADR decomposition (pp of ADR y/y) ===")
    print(df[cols].round(2).to_string(index=False))
    print("\n=== Confidence ===")
    for _, r in df.iterrows():
        print(f"  {int(r.year)}  {r.confidence}")
