"""
WS-L step 5: the 3Q26 and 4Q26 regional ex-FX forecasts and their aggregate.

Per region and variant (L_wf primary, plus L_wf_own, L_fixed_hicp, L_reg_lastq for the reader):
the pick at 3Q26 is the walk-forward pick on the out-of-sample record through 2Q26 (L2); 4Q26 has
the same information set, so the same pick. Proxy readings for 3Q26 are J2's quarter-to-date
readings (HICP July, INE July, CPI lodging July-August, BEA July). For 4Q26 a lag-0 proxy form
holds the 3Q26 reading (assumed), a lag-1 form uses the 3Q26 reading, and own-history rules chain
on the 3Q26 forecast (assumed). Aggregation uses 3Q25 (4Q25) nights shares and anchored regional
ADR as weights; the geo term is workstream I's measured 3Q26 split (-1.43, lo -1.57, hi -0.94)
and is carried to 4Q26 (assumed, J3's convention).

Bands: per region plus or minus the pick's out-of-sample RMSE on usable quarters before 3Q26
(descriptive). Aggregate central band = root sum of squares of the weighted regional bands, the
reconstruction-gap RMSE on 1Q24-2Q26 (0.39 pp) and the geo half-range; wide band = arithmetic sum.

Writes data/processed/adrv3/L/L4_regional_nowcast.csv and L4_aggregate_nowcast.csv.

py -3.13 analysis/src/adrv3/L4_regional_nowcast.py    (offline, seconds)
"""
import os

import numpy as np
import pandas as pd

import L0_common as L
from L0_common import S, REGIONS, QI

panel, wide = L.load_regional()
H = S.load_inputs()["H"]
proxies, readings = L.load_proxies()
prox_ext = L.proxy_series_with_readings(proxies, readings, hold_for_4q26=True)
sel = pd.read_csv(os.path.join(L.OUT, "L2_regional_selection.csv"))
seltab = pd.read_csv(os.path.join(L.OUT, "L2_selection_tables.csv"))
oosl = pd.read_csv(os.path.join(L.OUT, "L2_candidate_oos_paths.csv"))
chk = pd.read_csv(os.path.join(L.OUT, "L1_identity_check.csv"))
gap_rmse = L.rmse(chk[chk.quarter.map(QI) >= QI["1Q24"]].gap_reconstructed_minus_disclosed_pp)

imix = pd.read_csv(os.path.join(L.ROOT, "data", "processed", "adrq3", "I", "I_mix_terms_3q26.csv"))
geo_row = imix[(imix.term == "geo_mix") & (imix.quarter == "3Q26")].iloc[0]
GEO = {"3Q26": (float(geo_row.adr_contribution_pp), float(geo_row.lo), float(geo_row.hi), "measured: I3 3Q26 split (E_aug) x 07/H method"),
       "4Q26": (float(geo_row.adr_contribution_pp), float(geo_row.lo), float(geo_row.hi), "assumed: 3Q26 measured term carried (J3 convention)")}
size_row = imix[(imix.term == "unit_size") & (imix.quarter == "3Q26")].iloc[0]
los_row = imix[(imix.term == "los_mix") & (imix.quarter == "3Q26")].iloc[0]

# picks per variant at 3Q26 (same at 4Q26)
def pick_for(variant, region):
    s = sel[(sel.region == region) & (sel.quarter == "3Q26")].iloc[0]
    if variant == "L_wf":
        return s.pick
    if variant == "L_fixed_hicp":
        return "hicp_ea_accommodation|level|lag0" if region == "emea" else "last_q"
    if variant == "L_reg_lastq":
        return "last_q"
    if variant == "L_wf_own":
        d = oosl[(oosl.region == region)]
        tab = d.pivot(index="quarter", columns="candidate", values="pred_pp")
        tab["actual"] = d.groupby("quarter").actual_pp.first().reindex(tab.index)
        tab["usable"] = d.groupby("quarter").usable.first().reindex(tab.index).astype(bool)
        tab = tab.loc[sorted(tab.index, key=lambda q: QI[q])]
        return L.select(tab, [c for c in L.candidates_for(region) if c in L.OWN_RULES], "3Q26")["pick"]
    raise ValueError(variant)


def oos_rmse(region, cand):
    r = seltab[(seltab.region == region) & (seltab.quarter == "3Q26") & (seltab.candidate == cand)]
    return (float(r.rmse_prior_oos.iloc[0]), int(r.n_oos_prior.iloc[0])) if len(r) else (np.nan, 0)


VARIANTS = ["L_wf", "L_wf_own", "L_fixed_hicp", "L_reg_lastq"]
rows, agg = [], []
for v in VARIANTS:
    fc = {r: {} for r in REGIONS}
    for r in REGIONS:
        rd = L.RegionData(r, panel, prox_ext)
        cand = pick_for(v, r)
        band, n_oos = oos_rmse(r, cand)
        # 3Q26
        p3, note3 = L.predict(rd, cand, "3Q26")
        used = cand
        if pd.isna(p3):
            p3, note3 = L.predict(rd, "last_q", "3Q26")
            used, note3 = "last_q", f"{cand} unavailable at 3Q26 ({note3}); last_q used"
            band, n_oos = oos_rmse(r, "last_q")
        fc[r]["3Q26"] = p3
        x3 = ""
        if "|" in used:
            proxy, tr, lag = used.split("|")
            x3 = f"{proxy} {tr} {lag} = {rd.proxy_x(proxy, tr, int(lag[3:])).get('3Q26', np.nan):.2f}"
        rows.append({"variant": v, "region": r, "quarter": "3Q26", "pick": used, "pick_basis": note3, "proxy_input": x3,
                     "forecast_exfx_pp": p3, "band_pp": band, "band_basis": f"OOS RMSE of the pick on {n_oos} usable quarters before 3Q26",
                     "last_disclosed_exfx_pp": float(rd.y["2Q26"]), "last_basis": panel[(panel.region == r) & (panel.quarter == "2Q26")].exfx_basis.iloc[0],
                     "weight_share_pct": float(wide.at["3Q25", f"nights_share_{r}_pct"]), "weight_adr_anchored_usd": float(wide.at["3Q25", f"adr_{r}_usd_anchored"])})
        # 4Q26: own rules chain on the 3Q26 forecast; lag-0 proxies hold the 3Q26 reading (assumed)
        extra = pd.Series({"3Q26": p3})
        p4, note4 = L.predict(rd, used, "4Q26", extra_y=extra)
        used4 = used
        if pd.isna(p4):
            p4, note4 = L.predict(rd, "last_q", "4Q26", extra_y=extra)
            used4, note4 = "last_q", f"{used} unavailable at 4Q26 ({note4}); last_q on the 3Q26 forecast"
        if used4 in L.OWN_RULES:
            note4 += "; assumed: chains on the 3Q26 forecast"
        elif used4.endswith("lag0"):
            note4 += "; assumed: 3Q26 proxy reading held for 4Q26"
        else:
            note4 += "; proxy at lag 1 = the 3Q26 reading"
        fc[r]["4Q26"] = p4
        x4 = ""
        if "|" in used4:
            proxy, tr, lag = used4.split("|")
            x4 = f"{proxy} {tr} {lag} = {rd.proxy_x(proxy, tr, int(lag[3:])).get('4Q26', np.nan):.2f}"
        rows.append({"variant": v, "region": r, "quarter": "4Q26", "pick": used4, "pick_basis": note4, "proxy_input": x4,
                     "forecast_exfx_pp": p4, "band_pp": band, "band_basis": "same OOS RMSE as 3Q26 (no 4Q26 record exists)",
                     "last_disclosed_exfx_pp": float(rd.y["2Q26"]), "last_basis": panel[(panel.region == r) & (panel.quarter == "2Q26")].exfx_basis.iloc[0],
                     "weight_share_pct": float(wide.at["4Q25", f"nights_share_{r}_pct"]), "weight_adr_anchored_usd": float(wide.at["4Q25", f"adr_{r}_usd_anchored"])})
    for q in L.NOWCAST_QUARTERS:
        s0, _, a0 = L.weights_for(wide, q)
        w = L.dollar_weights(wide, q)
        g = {r: fc[r][q] for r in REGIONS}
        within = L.aggregate_within(g, s0, a0)
        geo, glo, ghi, gbasis = GEO[q]
        bands = {r: [x for x in rows if x["variant"] == v and x["region"] == r and x["quarter"] == q][0]["band_pp"] for r in REGIONS}
        reg_band = {r: w[r] * bands[r] for r in REGIONS}
        geo_half = 0.5 * (ghi - glo)
        central = float(np.sqrt(sum(b ** 2 for b in reg_band.values()) + gap_rmse ** 2 + geo_half ** 2))
        wideb = float(sum(reg_band.values()) + gap_rmse + geo_half)
        agg.append({"variant": v, "quarter": q, "within_region_exfx_pp": within, "geo_mix_pp": geo, "geo_basis": gbasis,
                    "blended_exfx_pp": within + geo, "band_central_pp": central, "lo_central_pp": within + geo - central, "hi_central_pp": within + geo + central,
                    "band_wide_pp": wideb, "lo_wide_pp": within + geo - wideb, "hi_wide_pp": within + geo + wideb,
                    "gap_rmse_pp": gap_rmse, "geo_half_range_pp": geo_half,
                    **{f"g_{r}": g[r] for r in REGIONS}, **{f"w_{r}": w[r] for r in REGIONS}, **{f"band_{r}": bands[r] for r in REGIONS},
                    "band_basis": "central = RSS(weighted regional OOS RMSE, gap RMSE 1Q24-2Q26, geo half-range); wide = arithmetic sum"})

# comparison columns (not inputs): v3 last_q rule on the same I terms, and card v2
c = S.v2_components()
nb, it = float(c.at["2Q26", "new_business_prior_year_pp"]), float(c.at["2Q26", "interaction_prior_year_pp"])
res_last = float(H.at["2Q26", "residual_pricing_pp"])
v3_3q26 = float(GEO["3Q26"][0]) + float(size_row.adr_contribution_pp) + float(los_row.adr_contribution_pp) + nb + it + res_last
for q in L.NOWCAST_QUARTERS:
    agg.append({"variant": "comparison: v3 last_q rule (measured I terms + prior-year fills + 2Q26 residual)", "quarter": q,
                "within_region_exfx_pp": np.nan, "geo_mix_pp": GEO[q][0], "geo_basis": GEO[q][3], "blended_exfx_pp": v3_3q26,
                "band_basis": f"geo {GEO[q][0]:.2f} + size {float(size_row.adr_contribution_pp):.2f} + LOS {float(los_row.adr_contribution_pp):.2f} + nb {nb:.2f} + interaction {it:.2f} + residual last_q {res_last:.2f}; 4Q26 carries the 3Q26 terms"})
    agg.append({"variant": "comparison: card v2 (J3)", "quarter": q, "blended_exfx_pp": 3.46 if q == "3Q26" else np.nan,
                "band_basis": "docs/adrq3/SYNTHESIS.md: 3Q26 ex-FX +3.46 (residual 4.61 + geo -1.43 + size +0.80 + LOS +0.06 + nb -0.48 + interaction -0.10)"})

rows = pd.DataFrame(rows)
agg = pd.DataFrame(agg)
rows.to_csv(os.path.join(L.OUT, "L4_regional_nowcast.csv"), index=False)
agg.to_csv(os.path.join(L.OUT, "L4_aggregate_nowcast.csv"), index=False)

pd.set_option("display.width", 250)
print(rows[["variant", "region", "quarter", "pick", "proxy_input", "forecast_exfx_pp", "band_pp", "last_disclosed_exfx_pp", "pick_basis"]].round(2).to_string(index=False))
print()
print(agg[["variant", "quarter", "within_region_exfx_pp", "geo_mix_pp", "blended_exfx_pp", "band_central_pp", "lo_central_pp", "hi_central_pp", "lo_wide_pp", "hi_wide_pp"]].round(2).to_string(index=False))
