"""10. Audit the decomposition. Where does the unexplained line actually come from?

The unexplained line runs 19% to 131% of the ADR move, which is large enough that the
method should be suspected before the finding is believed. This script checks each term
against an independent source rather than re-deriving it the same way.

Checks
  A. FX. The decomposition (03) re-derives annual FX by averaging regional currency
     baskets. But the letters DISCLOSE the global FX effect quarterly, and 02 validated a
     reconstruction of it. Do the two agree? If not, the decomposition is carrying an FX
     error straight into the residual.
  B. Price. The measured price term is built from hotel benchmarks that were shown to have
     no relationship with ABNB ADR ex-FX post-2023. Subtracting an unrelated series does
     not explain variance -- it injects it. How much of the residual is that?
  C. Sub-regional mix. The decomposition removes mix at the 4-region level only. Airbnb's
     growth is concentrated in expansion markets WITHIN regions (Brazil inside LatAm, India
     inside APAC), which is a real mix effect that lands in the residual by construction.
     Size it.
  D. Rounding. ALOS is printed to 0.1 and nights to whole millions from 2022.

Output
  data/processed/adr/10_audit.csv
"""

import os
import numpy as np
import pandas as pd

OUT = "data/processed/adr"
REG = ["na", "emea", "latam", "apac"]


def qyear(q):
    return int(q[2:]) + 2000


def main():
    hist = pd.read_csv(f"{OUT}/02b_adr_history_extended.csv")
    dec = pd.read_csv(f"{OUT}/07_full_decomposition.csv")
    ann = pd.read_csv(f"{OUT}/03_regional_annual_fx.csv")
    rows = []

    # ---- A. FX: decomposition vs the validated/disclosed series ---------------
    hist["year"] = hist.quarter.map(qyear)
    # Weight quarters by GBV so the annual FX effect matches an annual ADR y/y.
    h = hist.dropna(subset=["fx_pts_adr_final", "gbv_busd"])
    fx_disc = (h.assign(w=h.gbv_busd)
                 .groupby("year")
                 .apply(lambda g: np.average(g.fx_pts_adr_final, weights=g.w),
                        include_groups=False))
    fx_simple = h.groupby("year").fx_pts_adr_final.mean()

    print("=== A. FX term: decomposition vs disclosed ===")
    print(f"{'year':6s}{'decomp':>10s}{'disclosed':>12s}{'(GBV-wtd)':>12s}{'gap pp':>10s}")
    for _, d in dec.iterrows():
        y = int(d.year)
        if y in fx_disc.index:
            gap = d.of_which_fx_pp - fx_disc[y]
            print(f"{y:<6d}{d.of_which_fx_pp:>10.2f}{fx_simple[y]:>12.2f}"
                  f"{fx_disc[y]:>12.2f}{gap:>10.2f}")
            rows.append(dict(check="A_fx", year=y, decomposition=d.of_which_fx_pp,
                             independent=fx_disc[y], gap_pp=gap,
                             note="03 re-derives FX from regional baskets; the letters "
                                  "disclose it and 02 validated a reconstruction"))

    # ---- B. Price: how much of the residual is the hotel proxy? --------------
    print("\n=== B. Price term: what happens if the hotel proxy is not subtracted ===")
    print(f"{'year':6s}{'size+price':>12s}{'price':>9s}{'size':>8s}"
          f"{'unexpl':>9s}{'unexpl if price=0':>19s}")
    for _, d in dec.iterrows():
        y = int(d.year)
        sp = d.of_which_size_and_price_pp
        pm = 0.0 if pd.isna(d.price_measured_pp) else d.price_measured_pp
        sz = 0.0 if pd.isna(d.size_mix_pp) else d.size_mix_pp
        alt = sp - sz
        print(f"{y:<6d}{sp:>12.2f}{pm:>9.2f}{sz:>8.2f}"
              f"{d.unexplained_pp if pd.notna(d.unexplained_pp) else float('nan'):>9.2f}"
              f"{alt:>19.2f}")
        rows.append(dict(check="B_price", year=y, decomposition=d.unexplained_pp,
                         independent=alt, gap_pp=pm,
                         note="unexplained if the hotel-proxy price term is dropped; the "
                              "proxy has r~0 with ABNB ADR ex-FX post-2023"))

    # ---- C. Sub-regional mix ------------------------------------------------
    # The decomposition removes mix across 4 regions. Within a region, nights are shifting
    # to lower-ADR countries (expansion markets grow ~2x core). Bound that effect: if the
    # within-region ADR dispersion is comparable to the cross-region dispersion, and
    # expansion markets take share at a similar rate, the missed term is of similar order.
    print("\n=== C. Sub-regional mix, the term the method cannot see ===")
    a24 = ann[ann.year == 2025].set_index("region")
    glob = (a24.nights_share_pct / 100 * a24.adr).sum()
    print(f"  2025 regional ADR: " + ", ".join(f"{r} ${a24.loc[r,'adr']:.0f}" for r in REG))
    print(f"  cross-region ADR dispersion (max/min): "
          f"{a24.adr.max()/a24.adr.min():.2f}x, and 4-region mix cost -1.58pp in 2025")
    print("  Airbnb discloses NO country-level ADR, so the within-region term is not")
    print("  measurable. It is not zero: expansion-market origin nights have grown ~2x core")
    print("  for ten consecutive quarters, and those markets are lower-ADR.")
    rows.append(dict(check="C_subregional_mix", year=2025, decomposition=np.nan,
                     independent=np.nan, gap_pp=np.nan,
                     note="within-region country mix is unmeasurable from disclosure and "
                          "lands entirely in the residual; sign is negative (expansion "
                          "markets are lower-ADR and grow ~2x core)"))

    # ---- D. Rounding --------------------------------------------------------
    print("\n=== D. Rounding headroom in the inputs ===")
    a = pd.read_csv(f"{OUT}/01_regional_annual.csv")
    a = a[a.region != "total"]
    worst = a.groupby("year").adr_round_err_pct.max()
    for y, v in worst.items():
        print(f"  {int(y)}  regional ADR rounding band up to +/-{v:.2f}%")
    alos_band = 0.05 / 3.8 * 100
    print(f"  ALOS printed to 0.1 on a ~3.8 base -> +/-{alos_band:.2f}% per year, and the "
          f"LOS term is small, so this is second-order")
    rows.append(dict(check="D_rounding", year=2025, decomposition=np.nan,
                     independent=np.nan, gap_pp=float(worst.get(2025, np.nan)),
                     note="whole-million nights rounding from 2022 puts a band on regional ADR"))

    df = pd.DataFrame(rows)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(f"{OUT}/10_audit.csv", index=False)

    # ---- Corrected decomposition --------------------------------------------
    print("\n=== Corrected: use disclosed FX, drop the hotel price proxy ===")
    print(f"{'year':6s}{'ADR y/y':>9s}{'geo':>8s}{'FX*':>8s}{'LOS':>7s}"
          f"{'size':>7s}{'within-region residual':>24s}")
    for _, d in dec.iterrows():
        y = int(d.year)
        if y not in fx_disc.index:
            continue
        fx = fx_disc[y]
        sz = 0.0 if pd.isna(d.size_mix_pp) else d.size_mix_pp
        # within-region residual after the corrected FX and the measured size term
        resid = d.adr_yoy_pct - d.geo_mix_pp - d.interaction_pp - fx - d.of_which_los_pp - sz
        print(f"{y:<6d}{d.adr_yoy_pct:>9.2f}{d.geo_mix_pp:>8.2f}{fx:>8.2f}"
              f"{d.of_which_los_pp:>7.2f}{sz:>7.2f}{resid:>24.2f}")


if __name__ == "__main__":
    main()
