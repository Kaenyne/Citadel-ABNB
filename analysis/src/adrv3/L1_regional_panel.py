"""
WS-L step 1: the regional ex-FX ADR panel and the identity check against H.

Writes data/processed/adrv3/L/L1_regional_panel.csv (quarter x region, 1Q21-2Q26: ex-FX y/y,
reported y/y, FX pp, nights share, anchored ADR, basis class disclosed / solved / modelled, usable
flag, workstream I regional size term) and L1_identity_check.csv (per quarter 1Q23-2Q26: this
script's within-region ex-FX, geo mix and reconstructed blended ex-FX from the regional panel,
H's own columns, the disclosed blended ex-FX, the reconstruction gap, and a plain nights-share
weighted mean of regional ex-FX for comparison).

py -3.13 analysis/src/adrv3/L1_regional_panel.py    (offline, seconds)
"""
import os

import numpy as np
import pandas as pd

import L0_common as L
from L0_common import S, REGIONS, QI

panel, wide = L.load_regional()
H = S.load_inputs()["H"]

panel.to_csv(os.path.join(L.OUT, "L1_regional_panel.csv"), index=False)

rows = []
for q in wide.index:
    if QI[q] - 4 < 0 or L.qprev(q, 4) not in wide.index:
        continue
    g = {r: float(wide.at[q, f"adr_yoy_exfx_{r}_pct"]) for r in REGIONS}
    if any(pd.isna(v) for v in g.values()):
        continue
    s0, s1, a0 = L.weights_for(wide, q)
    within = L.aggregate_within(g, s0, a0)
    total = L.aggregate_total(g, s0, s1, a0)
    ns_mean = sum(s0[r] * g[r] for r in REGIONS) / sum(s0.values())
    disc = float(H.at[q, "adr_exfx_yoy_pp"]) if q in H.index else np.nan
    r = {"quarter": q, "within_region_exfx_L_pp": within, "geo_mix_L_pp": total - within,
         "blended_reconstructed_L_pp": total, "nights_share_mean_exfx_pp": ns_mean,
         "within_region_exfx_H_pp": H.at[q, "within_region_exfx_pp"] if q in H.index else np.nan,
         "geo_mix_H_pp": H.at[q, "geo_mix_pp"] if q in H.index else np.nan,
         "blended_reconstructed_H_pp": H.at[q, "blended_exfx_reconstructed_pp"] if q in H.index else np.nan,
         "disclosed_blended_exfx_pp": disc,
         "gap_reconstructed_minus_disclosed_pp": total - disc if pd.notna(disc) else np.nan,
         "gap_H_pp": H.at[q, "geo_recon_gap_pp"] if q in H.index else np.nan,
         "n_regions_usable": int(sum(panel[(panel.quarter == q) & (panel.region == rr)].usable.iloc[0] for rr in REGIONS)),
         "regions_modelled": ",".join(rr for rr in REGIONS if not panel[(panel.quarter == q) & (panel.region == rr)].usable.iloc[0])}
    for rr in REGIONS:
        r[f"dollar_weight_{rr}"] = s0[rr] * a0[rr] / sum(s0[x] * a0[x] for x in REGIONS)
    rows.append(r)
chk = pd.DataFrame(rows)
chk["abs_diff_within_vs_H"] = (chk.within_region_exfx_L_pp - chk.within_region_exfx_H_pp).abs()
chk["abs_diff_geo_vs_H"] = (chk.geo_mix_L_pp - chk.geo_mix_H_pp).abs()
chk.to_csv(os.path.join(L.OUT, "L1_identity_check.csv"), index=False)

pd.set_option("display.width", 250)
print("usable quarters per region (disclosed or solved):")
for r in REGIONS:
    u = panel[(panel.region == r) & panel.usable].quarter.tolist()
    b = panel[(panel.region == r) & panel.usable].exfx_basis.value_counts().to_dict()
    print(f"  {r:6s} {u[0]}..{u[-1]} n={len(u)} {b}")
print("\nidentity check vs H (1Q24-2Q26 rows):")
c = chk[chk.quarter.map(QI) >= QI["1Q24"]]
print(c[["quarter", "within_region_exfx_L_pp", "within_region_exfx_H_pp", "geo_mix_L_pp", "geo_mix_H_pp",
         "blended_reconstructed_L_pp", "disclosed_blended_exfx_pp", "gap_reconstructed_minus_disclosed_pp", "gap_H_pp",
         "nights_share_mean_exfx_pp", "regions_modelled"]].round(3).to_string(index=False))
print("\nmax abs diff within vs H: %.6f  geo vs H: %.6f" % (chk.abs_diff_within_vs_H.max(), chk.abs_diff_geo_vs_H.max()))
gap = chk[chk.quarter.map(QI) >= QI["1Q24"]].gap_reconstructed_minus_disclosed_pp
print("gap 1Q24-2Q26: RMSE %.3f mean %.3f min %.3f max %.3f; lag-1 autocorr %.2f" % (
    L.rmse(gap), gap.mean(), gap.min(), gap.max(), gap.autocorr(1)))
print("dollar weights (year-ago share x anchored ADR) at 2Q26:", {r: round(v, 3) for r, v in L.dollar_weights(wide, "2Q26").items()})
