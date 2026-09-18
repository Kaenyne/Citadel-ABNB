"""R07 - P(3Q26 reported ADR y/y >= +4.4%). numpy/pandas only. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/risk-adr-residual-persists/datasets/r07_model.py"""
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]
rng = np.random.default_rng(20260917); N = 400_000
Phi = lambda z: 0.5*(1+erf(z/sqrt(2)))
THR = 4.4; rows = []
# 1. history: reported ADR y/y, FX, ex-FX (H reconstruction)
h = pd.read_csv(ROOT/"data/processed/q3nowcast/H/adr_history_components.csv")
h["needed_exfx_at_fx"] = np.nan
hist = h[["quarter","adr_yoy_reported_pp","fx_effect_pp","adr_exfx_yoy_pp","residual_pricing_pp"]].copy()
hist["reported_ge_4.4"] = hist.adr_yoy_reported_pp >= THR
hist["fx_adjusted_to_3q26(-0.43)"] = hist.adr_exfx_yoy_pp - 0.43
hist["fxadj_ge_4.4"] = hist["fx_adjusted_to_3q26(-0.43)"] >= THR
hist.to_csv(HERE/"r07_history.csv", index=False)
rows.append(("quarters 1Q23-2Q26 n", len(hist))); rows.append(("reported >= 4.4", int(hist["reported_ge_4.4"].sum())))
rows.append(("reported >= 4.4 with FX <= 0", int((hist["reported_ge_4.4"] & (hist.fx_effect_pp<=0)).sum())))
rows.append(("ex-FX (disclosed integer) - 0.43 >= 4.4", int(hist["fxadj_ge_4.4"].sum())))
rows.append(("max residual", float(hist.residual_pricing_pp.max())))
# 2. v3 card walk-forward errors (P1 paths, midpoint FX, with K line)
p = pd.read_csv(ROOT/"data/processed/adrv3/P/P1_card_v3_backtest_paths.csv")
p2 = p[(p.target=="t2_reported_usd_yoy")]
err = {}
for fx in ["midpoint","eur","baskets"]:
    q = p2[p2.fx_estimator==fx]; e = q.v3_point_last_q_plus_K_line_measured_mix - q.actual
    err[fx] = (float(np.sqrt((e**2).mean())), float(e.mean()))
    rows.append((f"v3+K walk-forward {fx}: RMSE, bias (model-actual)", f"{err[fx][0]:.3f}, {err[fx][1]:+.3f}"))
pd.DataFrame({"quarter":p2[p2.fx_estimator=="midpoint"].quarter.values,
              "err_midpoint":(p2[p2.fx_estimator=="midpoint"].v3_point_last_q_plus_K_line_measured_mix-p2[p2.fx_estimator=="midpoint"].actual).values}).to_csv(HERE/"r07_v3_errors.csv", index=False)
# 3. gaussian on the card point under each FX estimator
card = {"midpoint":3.43,"eur":2.74,"baskets":4.12}
for fx,pt in card.items():
    sd, b = err[fx]
    rows.append((f"P(>=4.4) N(card {fx} {pt}, sd {sd:.2f})", 1-Phi((THR-pt)/sd)))
    rows.append((f"P(>=4.4) N(card {fx} bias-corrected {pt-b:.2f}, sd {sd:.2f})", 1-Phi((THR-(pt-b))/sd)))
# 4. structural Monte Carlo: reported = mix terms + residual + FX
mix = rng.normal(-1.15, 0.35, N)           # geo -1.43, party +0.80, LOS +0.06, new-business -0.48, interaction -0.10, K line +0.17 => -0.98; centre -1.15 uses J3 fills
u = rng.random(N)
resid = np.where(u<0.55, rng.normal(4.85,0.55,N), np.where(u<0.75, rng.normal(5.35,0.55,N), rng.normal(3.6,0.7,N)))  # persistence 55 / momentum 20 / partial mean reversion 25
v = rng.random(N)
fx = np.where(v<0.5, rng.normal(-0.43,0.33,N), np.where(v<0.75, rng.normal(0.26,0.42,N), rng.normal(-1.12,0.46,N)))
rep = mix + resid + fx
rows.append(("structural MC P(>=4.4)", float((rep>=THR).mean()))); rows.append(("structural MC median", float(np.median(rep))))
rows.append(("structural MC P(<=2.0) [B02]", float((rep<=2.0).mean())))
for lab, w in [("residual all persistence 4.85",(1.0,0.0)),("residual all momentum 5.35",(0.0,1.0)),("residual all mean-rev 3.6",(0.0,0.0))]:
    if lab.endswith("4.85"): r2 = rng.normal(4.85,0.55,N)
    elif lab.endswith("5.35"): r2 = rng.normal(5.35,0.55,N)
    else: r2 = rng.normal(3.6,0.7,N)
    rows.append((f"MC {lab}", float(((mix+r2+fx)>=THR).mean())))
for lab, f2 in [("FX all midpoint", rng.normal(-0.43,0.33,N)),("FX all baskets", rng.normal(0.26,0.42,N)),("FX all eur", rng.normal(-1.12,0.46,N))]:
    rows.append((f"MC {lab}", float(((mix+resid+f2)>=THR).mean())))
rows.append(("MC mix centre -0.98 (H fills)", float(((mix+0.17+resid+fx)>=THR).mean())))
rows.append(("MC mix centre -1.45 (geo drag at band low)", float(((mix-0.30+resid+fx)>=THR).mean())))
out = pd.DataFrame(rows, columns=["item","value"]); out.to_csv(HERE/"r07_results.csv", index=False); print(out.to_string())
