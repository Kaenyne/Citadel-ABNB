"""X1 - what the two ADR-FX objects do to the committed ADR / GBV lines.

Reads committed cells only; writes only inside this receipt folder.
Base ex-FX is DEC-0008's v3_without_K card (3Q26 +3.69pp, 4Q26 +3.69pp).
Nights are DEC-0024 (3Q26 146.3m) and DEC-0019 (4Q26 131.8m).
"""
import pandas as pd
from pathlib import Path

OUT = Path("/Users/theomachado/Citadel-ABNB/data/processed/pitch_model_v2/receipts/X1")
PY_ADR = {"3Q26": 171.29, "4Q26": 167.51}     # 3Q25 / 4Q25 disclosed ADR, driver history
EXFX = {"3Q26": 3.69, "4Q26": 3.69}           # adr_card_v3 v3_without_K, DEC-0008
NIGHTS_M = {"3Q26": 146.3, "4Q26": 131.8}     # DEC-0024 / DEC-0019
CAND = {"D4 N midpoint (contemporaneous, disclosed-calibrated)": {"3Q26": -0.43, "4Q26": 0.15},
        "D5 point_phi_adrfx (Phi on LAGGED ADR-FX)": {"3Q26": 2.89, "4Q26": 0.93},
        "fx_lag_v2 contemporaneous basket fit": {"3Q26": 0.44, "4Q26": 1.10},
        "D4 low = euro fit": {"3Q26": -1.12, "4Q26": -0.66},
        "D4 high = regional baskets": {"3Q26": 0.26, "4Q26": 0.97}}

rows = []
for name, fx in CAND.items():
    for q in ("3Q26", "4Q26"):
        rep = EXFX[q] + fx[q]
        adr = PY_ADR[q] * (1 + rep / 100.0)
        rows.append({"object": name, "quarter": q, "adr_fx_pp": fx[q],
                     "adr_exfx_yoy_pp": EXFX[q], "adr_reported_yoy_pp": round(rep, 2),
                     "adr_usd": round(adr, 2), "nights_m": NIGHTS_M[q],
                     "gbv_musd": round(adr * NIGHTS_M[q], 0)})
t = pd.DataFrame(rows)
base = t[t.object.str.startswith("D4 N midpoint")].set_index("quarter")
t["delta_adr_usd_vs_D4"] = [round(r.adr_usd - base.loc[r.quarter, "adr_usd"], 2) for r in t.itertuples()]
t["delta_gbv_musd_vs_D4"] = [round(r.gbv_musd - base.loc[r.quarter, "gbv_musd"], 0) for r in t.itertuples()]
t.to_csv(OUT / "X1_model_impact.csv", index=False)
pd.set_option("display.width", 200)
print(t.to_string(index=False))
