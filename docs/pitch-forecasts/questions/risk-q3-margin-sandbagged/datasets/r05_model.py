"""R05 - P(3Q26 adj. EBITDA margin >= 51.5%). numpy/pandas only. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/risk-q3-margin-sandbagged/datasets/r05_model.py"""
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
rng = np.random.default_rng(20260917)
N = 400_000
Phi = lambda z: 0.5*(1+erf(z/sqrt(2)))
THR = 51.5
rows = []
# --- 1. sentence record: realised y/y margin change vs the quarterly ceiling/point sentences
led = pd.read_csv(HERE.parent.parent / "fy26-margin-sentence/datasets/quarterly_margin_sentence_ledger.csv")
led = led[led.guide_type.isin(["ceiling","point","floor"]) & led.actual.notna()].copy()
led = led[~led.target_period.isin(["3Q21","4Q21","2Q22","4Q22"])]  # 2021-22 reopening levels, not y/y pts on a stable base? keep 3Q22 (ceiling 49) as level->y/y
# 3Q22: ceiling was a level 49.0 vs 3Q21 49.2, actual 50.5 -> y/y +1.3; recompute y/y pts for it
led.loc[led.target_period=="3Q22","actual"] = 50.52-49.22
led.loc[led.target_period=="3Q22","value_high"] = 49.0-49.22
ceil = led[led.guide_type=="ceiling"].drop_duplicates("target_period")
ceil = ceil.assign(excess=ceil.actual - ceil.value_high)
ceil.to_csv(HERE/"r05_ceiling_record.csv", index=False)
n_c = len(ceil); k14 = int((ceil.excess >= 1.4).sum()); k0 = int((ceil.excess > 0).sum())
rows.append(("ceiling sentences n", n_c)); rows.append(("exceeded ceiling by >=1.4pp", k14)); rows.append(("exceeded ceiling at all", k0))
rows.append(("base rate Laplace (k14+1)/(n+2)", (k14+1)/(n_c+2)))
# --- 2. combination object: 49.94, conformal qhat80 2.20 (W1) / 2.08 (2024Q1+), MAE-gaussian 1.30, bias-corrected 50.21
for label, mu, sd in [("combination N(49.94, 1.72 from qhat80 W1)",49.94,2.204/1.2816),("combination N(49.94, 1.62 from qhat80 2024Q1+)",49.94,2.080/1.2816),
                      ("combination N(49.94, 1.30 gaussian-from-MAE)",49.94,1.30),("bias-corrected N(50.21, 1.62)",50.21,1.623),
                      ("M5 composite N(50.19, 1.34)",50.19,1.34),("Street+h0 bias N(50.9, 1.41)",50.91,1.41),("line build base N(50.4, 1.5)",50.4,1.5)]:
    rows.append((label+" P(>=51.5)", 1-Phi((THR-mu)/sd)))
# --- 3. cost-stack Monte Carlo: revenue x cost budget with a 'spend slipped' component
rev = rng.normal(4804, 50, N)                      # bridge v3 revenue, sd ~ Q3 cushion 0.5% + kernel
cost_budget = 2405.0                               # cash costs implied by the sentence at the guide midpoint (40 note)
slip = rng.random(N) < 0.25                        # 25%: part of the flagged Q3 step (marketing timing / hosting) does not land in Q3
cost = cost_budget + rng.normal(0, 60, N) - np.where(slip, rng.uniform(30, 97, N), 0.0)
cost += 0.20*(rev-4804)                            # variable cost on revenue (merchant fees, support) ~20%
ebitda = rev - cost; margin = 100*ebitda/rev
p_mc = float((margin >= THR).mean())
rows.append(("cost-stack MC P(>=51.5)", p_mc)); rows.append(("cost-stack MC median margin", float(np.median(margin))))
rows.append(("cost-stack MC P(>=50.09, i.e. sentence missed to the upside)", float((margin >= 50.085).mean())))
for p_slip in [0.0, 0.5]:
    slip2 = rng.random(N) < p_slip
    cost2 = cost_budget + rng.normal(0, 60, N) - np.where(slip2, rng.uniform(30, 97, N), 0.0) + 0.20*(rev-4804)
    rows.append((f"MC P(slip)={p_slip}", float((100*(rev-cost2)/rev >= THR).mean())))
for sdc in [40, 80]:
    cost3 = cost_budget + rng.normal(0, sdc, N) - np.where(slip, rng.uniform(30, 97, N), 0.0) + 0.20*(rev-4804)
    rows.append((f"MC cost sd={sdc}", float((100*(rev-cost3)/rev >= THR).mean())))
for rv in [4744, 4770, 4850]:
    rev4 = rng.normal(rv, 50, N); cost4 = cost_budget + rng.normal(0, 60, N) - np.where(slip, rng.uniform(30, 97, N), 0.0) + 0.20*(rev4-4804)
    rows.append((f"MC revenue centre {rv}", float((100*(rev4-cost4)/rev4 >= THR).mean())))
# --- 4. revenue-leg arithmetic: cash costs allowed at 51.5%
for rv in [4744.3, 4770, 4804, 4850]:
    c = rv*(1-THR/100); sm = 781 - (cost_budget - c)
    rows.append((f"costs allowed at 51.5% on revenue {rv}", round(c,1)))
    rows.append((f"  implied S&M if the whole gap is S&M (3Q25 585)", f"{sm:.0f}M, {100*(sm/585-1):+.1f}% y/y vs budget +33.5%"))
out = pd.DataFrame(rows, columns=["item","value"]); out.to_csv(HERE/"r05_results.csv", index=False)
print(out.to_string())
