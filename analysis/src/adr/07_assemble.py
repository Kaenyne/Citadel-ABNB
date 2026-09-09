"""07. Assemble the ADR decomposition.

REVISED 8 Sep 2026 after the audit in 10_audit_decomposition.py, which found the first
version's large "unexplained" line was mostly an artefact of two method errors:

  1. FX was RE-DERIVED by averaging regional currency baskets, when the letters disclose
     the global FX effect quarterly and 02 validated a reconstruction of it (r 0.988).
     The re-derivation was wrong by up to 1.33pp (2022), which was half that year's
     "unexplained".
  2. A hotel-benchmark price proxy was SUBTRACTED as a component. Those benchmarks have
     r ~ 0 with ABNB ADR ex-FX post-2023 (Bonferroni p = 1.000), so subtracting one does
     not explain variance, it injects it -- in 2022 it absorbed 6.73pp purely because
     hotel prices were inflating post-COVID.

Corrected structure:

  ADR y/y = geographic mix (4-region)
          + FX                       <- disclosed / validated, not re-derived
          + interaction
          + within-region ADR ex-FX

  within-region ADR ex-FX = unit-size mix
                          + length of stay
                          + [ within-region pricing + SUB-REGIONAL MIX ]   <- jointly
                                                                             unidentified

The last bracket is not "unexplained" in the sense of a mystery. It is a named quantity
that cannot be split further because **Airbnb discloses no country-level ADR**. It is not
noise either: expansion-market origin nights have grown ~2x core for ten consecutive
quarters and those markets are lower-ADR, so there is a real negative mix term inside each
region that a four-region decomposition cannot see.

Validation: the residual reconciles to the nights-weighted regional ADR ex-FX built
independently from the 10-K in 03, within ~0.1pp in every year 2023-2025. That is the
check the first version lacked.

The hotel price benchmark is retained as a COMPARATOR column, not a component.

Output
  data/processed/adr/07_full_decomposition.csv
"""

import os
import numpy as np
import pandas as pd

OUT = "data/processed/adr"
REG = ["na", "emea", "latam", "apac"]


def qyear(q):
    return int(q[2:]) + 2000


def disclosed_fx():
    """Annual FX effect on ADR, GBV-weighted from the disclosed/validated quarterly series."""
    h = pd.read_csv(f"{OUT}/02b_adr_history_extended.csv")
    h["year"] = h.quarter.map(qyear)
    h = h.dropna(subset=["fx_pts_adr_final", "gbv_busd"])
    return h.groupby("year").apply(
        lambda g: np.average(g.fx_pts_adr_final, weights=g.gbv_busd), include_groups=False)


def regional_exfx():
    """Nights-weighted regional ADR ex-FX growth -- the independent reconciliation target."""
    a = pd.read_csv(f"{OUT}/03_regional_annual_fx.csv")
    a = a[a.region.isin(REG)]
    out = {}
    for y, g in a.groupby("year"):
        g = g.dropna(subset=["adr_exfx_yoy", "nights_share_pct"])
        if len(g) == 4:
            out[y] = float(np.average(g.adr_exfx_yoy, weights=g.nights_share_pct))
    return pd.Series(out)


def size_by_year():
    s = pd.read_csv(f"{OUT}/05_size_mix_summary.csv")
    y = s[s.scope == "year"].copy()
    y["year"] = pd.to_datetime(y.date_b_min).dt.year
    return y.groupby("year", as_index=False).agg(
        size_mix_pp=("size_mix_pp_quote_basis", "mean"),
        size_n_pairs=("n_pairs", "max"), size_n_markets=("n_markets", "max"))


def build():
    d = pd.read_csv(f"{OUT}/03_annual_decomposition.csv")
    p = pd.read_csv(f"{OUT}/06_price_residual_annual.csv")
    s = size_by_year()
    fx = disclosed_fx()
    rex = regional_exfx()

    df = d[["year", "adr_yoy_pct", "geo_mix_pp", "interaction_pp", "of_which_los_pp"]].copy()
    df["fx_pp"] = df.year.map(fx)
    df = df.merge(s, on="year", how="left").merge(
        p[["year", "price_measured_pp", "worst_confidence"]], on="year", how="left")
    df = df.rename(columns={"price_measured_pp": "hotel_price_comparator_pp"})

    # Within-region ADR ex-FX, by subtraction from the identity.
    df["within_region_exfx_pp"] = (df.adr_yoy_pct - df.geo_mix_pp
                                   - df.interaction_pp - df.fx_pp)
    # Split what we can measure out of it.
    df["size_mix_pp"] = df.size_mix_pp.fillna(0.0)
    df["pricing_and_subregional_mix_pp"] = (df.within_region_exfx_pp
                                            - df.size_mix_pp - df.of_which_los_pp)

    # Reconciliation against the independently built regional panel.
    df["regional_exfx_independent_pp"] = df.year.map(rex)
    df["reconciliation_gap_pp"] = (df.within_region_exfx_pp
                                   - df.regional_exfx_independent_pp)

    df["identity_check_pp"] = (df.geo_mix_pp + df.fx_pp + df.interaction_pp
                               + df.within_region_exfx_pp - df.adr_yoy_pct)

    def conf(r):
        if abs(r.reconciliation_gap_pp) > 1.0 if pd.notna(r.reconciliation_gap_pp) else True:
            return "low -- does not reconcile to the independent regional panel"
        if r.size_n_markets != r.size_n_markets or r.size_n_markets < 3:
            return ("medium -- reconciles; size mix not separately measured "
                    "(folded into the pricing/sub-regional term)")
        return "medium -- reconciles; size mix measured"

    df["confidence"] = df.apply(conf, axis=1)

    os.makedirs(OUT, exist_ok=True)
    df.to_csv(f"{OUT}/07_full_decomposition.csv", index=False)
    return df


if __name__ == "__main__":
    df = build()
    pd.set_option("display.width", 240)
    cols = ["year", "adr_yoy_pct", "geo_mix_pp", "fx_pp", "interaction_pp",
            "within_region_exfx_pp", "of_which_los_pp", "size_mix_pp",
            "pricing_and_subregional_mix_pp", "identity_check_pp"]
    print("=== ADR decomposition, corrected (pp of ADR y/y) ===")
    print(df[cols].round(2).to_string(index=False))
    print("\n=== Reconciliation against the independent 10-K regional panel ===")
    print(df[["year", "within_region_exfx_pp", "regional_exfx_independent_pp",
              "reconciliation_gap_pp"]].round(2).to_string(index=False))
    print("\n=== Hotel price benchmark: COMPARATOR ONLY, not a component ===")
    print(df[["year", "hotel_price_comparator_pp", "pricing_and_subregional_mix_pp"]]
          .round(2).to_string(index=False))
    print("\n=== Confidence ===")
    for _, r in df.iterrows():
        print(f"  {int(r.year)}  {r.confidence}")
