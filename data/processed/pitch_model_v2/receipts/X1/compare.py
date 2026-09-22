"""X1 - ADR FX object reconciliation: D4 (adrv3 N midpoint) vs D5 (fx_lag_v2 point_phi_adrfx_pp).

Reads only committed CSVs; fits nothing; writes only inside this receipt folder.

Objects compared, all in pp:
  disclosed_adr_fx   = reported ADR y/y  -  ex-FX ADR y/y   (Airbnb's own definition;
                       analysis/src/predictive/03_nowcast_tests.py line 66)
  disclosed_rev_fx   = reported revenue y/y - ex-FX revenue y/y (letter integers)
  d4_midpoint        = mean(est_from_eur, est_from_regional_baskets), both CONTEMPORANEOUS
  d5_phi_adrfx       = (2/3) f(basket_{q-1}) + (1/3) f(basket_{q-2}),
                       f(x) = adr_intercept + adr_slope * x   (fx_lag_v2 exhibit.py L283-289)
  fxlagv2_contemp    = f(basket_q)  - fx_lag_v2's OWN contemporaneous ADR-FX estimator
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/Users/theomachado/Citadel-ABNB")
OUT = ROOT / "data/processed/pitch_model_v2/receipts/X1"

SLOPE, INTERCEPT = 0.872, -0.076          # run.py stdout, fx_lag_v2, n=14 1Q23-2Q26, r 0.962
f = lambda x: INTERCEPT + SLOPE * x

# ---- disclosed series + fx_lag_v2 baskets -----------------------------------
p = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/04_analysis_panel.csv")
p = p[["quarter", "fx_pts_adr", "fx_pts_revenue", "b_lag0", "b_lag1", "b_lag2"]]

# ---- D4's estimator, per quarter --------------------------------------------
b = pd.read_csv(ROOT / "data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv")
b = b[["quarter_h", "adr_fx_disclosed_pp", "est_from_eur",
       "est_from_regional_baskets", "est_from_midpoint"]]
b = b.rename(columns={"quarter_h": "quarter"})

d = p.merge(b, on="quarter", how="left")
d["d4_midpoint"] = d["est_from_midpoint"]
d["d5_phi_adrfx"] = (2.0 / 3.0) * f(d["b_lag1"]) + (1.0 / 3.0) * f(d["b_lag2"])
d["fxlagv2_contemp"] = f(d["b_lag0"])

hist = d[d["fx_pts_adr"].notna()].copy()          # 2Q22-2Q26, 17 quarters
hist["err_d4_vs_adr"] = hist["d4_midpoint"] - hist["fx_pts_adr"]
hist["err_d5_vs_adr"] = hist["d5_phi_adrfx"] - hist["fx_pts_adr"]
hist["err_contemp_vs_adr"] = hist["fxlagv2_contemp"] - hist["fx_pts_adr"]
hist["err_d5_vs_rev"] = hist["d5_phi_adrfx"] - hist["fx_pts_revenue"]
hist["err_d4_vs_rev"] = hist["d4_midpoint"] - hist["fx_pts_revenue"]

def rmse(s):
    s = s.dropna()
    return (float(np.sqrt(np.mean(s ** 2))), len(s))

rows = []
for lab, col in [("D4 midpoint (eur+baskets)/2, contemporaneous", "err_d4_vs_adr"),
                 ("D5 point_phi_adrfx (Phi on lagged fitted ADR-FX)", "err_d5_vs_adr"),
                 ("fx_lag_v2 contemporaneous basket fit f(basket_q)", "err_contemp_vs_adr")]:
    for wname, sub in [("full 2Q22-2Q26", hist),
                       ("W1-like 1Q23-2Q26", hist[hist["quarter"].isin(
                           ["1Q23","2Q23","3Q23","4Q23","1Q24","2Q24","3Q24","4Q24",
                            "1Q25","2Q25","3Q25","4Q25","1Q26","2Q26"])]),
                       ("scored 1Q24-2Q26", hist[hist["quarter"].isin(
                           ["1Q24","2Q24","3Q24","4Q24","1Q25","2Q25","3Q25","4Q25",
                            "1Q26","2Q26"])])]:
        r, n = rmse(sub[col])
        rows.append({"estimator": lab, "target": "DISCLOSED ADR FX", "window": wname,
                     "n": n, "rmse_pp": round(r, 3),
                     "bias_pp": round(float(sub[col].dropna().mean()), 3)})
for lab, col in [("D5 point_phi_adrfx (Phi on lagged fitted ADR-FX)", "err_d5_vs_rev"),
                 ("D4 midpoint (eur+baskets)/2, contemporaneous", "err_d4_vs_rev")]:
    sub = hist[hist["fx_pts_revenue"].notna()]
    r, n = rmse(sub[col])
    rows.append({"estimator": lab, "target": "DISCLOSED REVENUE FX", "window": "2Q22-2Q26",
                 "n": n, "rmse_pp": round(r, 3),
                 "bias_pp": round(float(sub[col].dropna().mean()), 3)})
score = pd.DataFrame(rows)

# ---- forward cells, read not derived ----------------------------------------
fc = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/23_forecast_4q26_v2.csv")
fc = fc[fc.path == "spot_held"].set_index("quarter")
card = pd.read_csv(ROOT / "data/processed/adrv3/N/N1_fx_choice_card.csv")
card = card[card.fx_estimator == "midpoint"].set_index("quarter")
k27 = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/27_kernel_carried_fx_v2.csv")

fwd = pd.DataFrame([
    {"quarter": q,
     "d4_midpoint_adr_fx_pp": float(card.loc[q, "fx_effect_pp"]),
     "d5_adr_fx_pp_as_published": float(fc.loc[q, "point_phi_adrfx_pp"]),
     "d5_revenue_fx_pp_phi_0851": float(fc.loc[q, "point_phi_basket_scale_0.851_pp"]),
     "fxlagv2_contemporaneous_adr_fx_pp": round(f(float(fc.loc[q, "basket_lag0_pct"])), 2),
     "basket_lag0_pct": float(fc.loc[q, "basket_lag0_pct"])}
    for q in ["3Q26", "4Q26"]])

hist_out = hist[["quarter", "fx_pts_adr", "fx_pts_revenue", "est_from_eur",
                 "est_from_regional_baskets", "d4_midpoint", "d5_phi_adrfx",
                 "fxlagv2_contemp", "b_lag0", "b_lag1", "b_lag2",
                 "err_d4_vs_adr", "err_d5_vs_adr", "err_contemp_vs_adr",
                 "err_d5_vs_rev"]].round(3)
hist_out.to_csv(OUT / "X1_disclosed_vs_objects.csv", index=False)
score.to_csv(OUT / "X1_estimator_scores.csv", index=False)
fwd.round(3).to_csv(OUT / "X1_forward_cells.csv", index=False)

pd.set_option("display.width", 220)
print("=== per-quarter, disclosed vs the two objects (pp) ===")
print(hist_out.to_string(index=False))
print("\n=== RMSE / bias by target and window ===")
print(score.to_string(index=False))
print("\n=== forward cells (spot held, FX through 2026-09-04) ===")
print(fwd.round(3).to_string(index=False))
print("\n=== 27_kernel_carried_fx_v2 adr_fx_3Q26_fitted_pp ===")
print(float(k27["adr_fx_3Q26_fitted_pp"].iloc[0]))
print("\n=== identity check: does disclosed ADR FX = reported - exFX? ===")
h = pd.read_csv(ROOT / "data/processed/q3nowcast/H/adr_history_components.csv")
h["recon"] = (h["adr_yoy_reported_pp"] - h["adr_exfx_yoy_pp"]).round(3)
print(h[["quarter", "adr_yoy_reported_pp", "adr_exfx_yoy_pp", "fx_effect_pp",
         "recon"]].assign(gap=lambda x: (x["recon"] - x["fx_effect_pp"]).round(4)).to_string(index=False))
json.dump({"slope": SLOPE, "intercept": INTERCEPT,
           "d4_3q26": float(card.loc["3Q26", "fx_effect_pp"]),
           "d4_4q26": float(card.loc["4Q26", "fx_effect_pp"]),
           "d5_3q26": float(fc.loc["3Q26", "point_phi_adrfx_pp"]),
           "d5_4q26": float(fc.loc["4Q26", "point_phi_adrfx_pp"]),
           "contemp_3q26": round(f(float(fc.loc["3Q26", "basket_lag0_pct"])), 2),
           "contemp_4q26": round(f(float(fc.loc["4Q26", "basket_lag0_pct"])), 2)},
          open(OUT / "X1_cells.json", "w"), indent=2)
