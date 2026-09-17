"""R05 revision 2 - P(3Q26 adj. EBITDA margin >= 51.5%). Response to audit A10 (A10-02 identity fix, A10-08, A10-09,
A10-18, A10-19, A10-20, A10-21). numpy/pandas only. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/risk-q3-margin-sandbagged/datasets/r05_model_v2.py
Revision-1 r05_model.py and r05_results.csv are left untouched as the audit trail."""
from pathlib import Path
import numpy as np, pandas as pd
from math import erf, sqrt
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
N = 400_000
Phi = lambda z: 0.5*(1+erf(z/sqrt(2)))
THR, CEIL, STREET = 51.5, 50.085, 49.7757
rows = []
# --- 1. sentence record (unchanged arithmetic; description corrected per A10-20)
led = pd.read_csv(HERE.parent.parent / "fy26-margin-sentence/datasets/quarterly_margin_sentence_ledger.csv")
led = led[led.guide_type.isin(["ceiling","point","floor"]) & led.actual.notna()].copy()
led = led[~led.target_period.isin(["3Q21","4Q21","2Q22","4Q22"])]
led.loc[led.target_period=="3Q22","actual"] = 50.52-49.22
led.loc[led.target_period=="3Q22","value_high"] = 49.0-49.22
c_all = led[led.guide_type=="ceiling"].copy()
rows.append(("ceiling rows before de-dup (4Q25 guided at both the 2Q25 h=2 and 3Q25 h=1 prints)", len(c_all)))
for keep, lab in [("first","keep h=2 (2Q25 print) sentence for 4Q25 [rev 1 choice]"),("last","keep h=1 (3Q25 print) sentence for 4Q25 [true analogue of 3Q26]")]:
    ceil = c_all.drop_duplicates("target_period", keep=keep).copy(); ceil["excess"] = ceil.actual - ceil.value_high
    n_c = len(ceil); k14 = int((ceil.excess >= 1.4).sum()); k0 = int((ceil.excess > 0).sum())
    rows.append((f"{lab}: n, >=1.4pp, >0, Laplace", f"{n_c}, {k14}, {k0}, {(k14+1)/(n_c+2):.4f}"))
# --- 2. line build identity (A10-02)
lb = pd.read_csv(ROOT/"data/processed/margin_build/40_line_build/40_lines_quarterly.csv")
b = lb[(lb.quarter=="3Q26") & (lb.scenario=="base")].iloc[0]
DA = float(b.da); REV0 = float(b.revenue); COST0 = float(b.total_cash_costs)
rows.append(("40_lines 3Q26 base: revenue, total_cash_costs, da, adj_ebitda, margin", f"{REV0:.3f}, {COST0:.3f}, {DA:.3f}, {b.adj_ebitda:.3f}, {b.adj_ebitda_margin_pct:.4f}"))
rows.append(("identity check revenue - cash + da == adj_ebitda", abs(REV0-COST0+DA-b.adj_ebitda) < 1e-6))
rows.append(("rev-1 MC centre (no add-back) vs line build", f"{100*(REV0-COST0)/REV0:.4f} vs {b.adj_ebitda_margin_pct:.4f}; D&A worth {100*DA/REV0:.4f} pp"))
# --- 3. Gaussian routes on the card (A10-18: gaussian_from_mae_80 is an 80% half-width; sd = /1.2816)
bands = pd.read_csv(ROOT/"data/processed/margin_build/23_final_model/23_bands.csv")
bm = bands[(bands.target=="adj_ebitda_margin_pct") & (bands.horizon_q==0)]
sd_w1 = float(bm[bm.calibration=="W1_all_n14"].gaussian_sd_from_qhat80.iloc[0]); sd_w2 = float(bm[bm.calibration=="recent_2024Q1plus"].gaussian_sd_from_qhat80.iloc[0])
hw_mae = float(bm[bm.calibration=="recent_2024Q1plus"].gaussian_from_mae_80.iloc[0]); b5 = float(bm.bias_last5.iloc[0])
MU = 49.9399
for label, mu, sd in [("card N(49.94, 1.72 W1 qhat80)",MU,sd_w1),("card N(49.94, 1.62 W2 qhat80)",MU,sd_w2),
                      ("card N(49.94, 1.01 = MAE-gaussian 80% half-width 1.297 / 1.2816) [rev 1 used 1.30 as sd]",MU,hw_mae/1.2816),
                      ("card bias-corrected last5 N(50.21, 1.62)",MU-b5,sd_w2),("M5 composite N(50.19, 1.356)",50.19,1.356),
                      ("Street + raw h0 bias N(50.9, 1.41)",50.91,1.41),("line build base N(50.37, 1.62)",50.367,sd_w2)]:
    rows.append((label+": P(>=51.5), P(>=50.085), P(>Street)", f"{1-Phi((THR-mu)/sd):.4f}, {1-Phi((CEIL-mu)/sd):.4f}, {1-Phi((STREET-mu)/sd):.4f}"))
# --- 4. cost-stack Monte Carlo, corrected identity: margin = (rev - cash costs + D&A) / rev
def mc(p_slip=0.25, sd_cost=60.0, rev_mu=4804.0, da=DA, seed=20260917):
    g = np.random.default_rng(seed)
    rev = g.normal(rev_mu, 50, N); slip = g.random(N) < p_slip
    cost = COST0 + g.normal(0, sd_cost, N) - np.where(slip, g.uniform(30, 97, N), 0.0) + 0.20*(rev-4804)
    return 100*(rev - cost + da)/rev
for lab, kw in [("as published (no add-back) [rev 1]", dict(da=0.0)), ("corrected (+D&A 20.634)", dict()),
                ("corrected, cost sd 72 (total sd ~ conformal 1.62) [A10-19]", dict(sd_cost=72.0))]:
    m = mc(**kw)
    rows.append((f"MC {lab}: P(>=51.5), median, sd, P(>=50.085), P(>=51.0), P(>=52.0), P(<=49.0)",
                 f"{(m>=THR).mean():.4f}, {np.median(m):.3f}, {m.std():.3f}, {(m>=CEIL).mean():.4f}, {(m>=51.0).mean():.4f}, {(m>=52.0).mean():.4f}, {(m<=49.0).mean():.4f}"))
for lab, kw in [("slip 0", dict(p_slip=0.0)), ("slip 0.5", dict(p_slip=0.5)), ("cost sd 40", dict(sd_cost=40.0)), ("cost sd 80", dict(sd_cost=80.0)),
                ("revenue 4744", dict(rev_mu=4744.0)), ("revenue 4770", dict(rev_mu=4770.0)), ("revenue 4850", dict(rev_mu=4850.0)), ("D&A 27 (3Q25 implied add-back)", dict(da=27.0))]:
    m = mc(**kw); rows.append((f"MC corrected, {lab}: P(>=51.5)", f"{(m>=THR).mean():.4f}"))
# --- 5. revenue-leg arithmetic on the corrected identity (A10-21): cash costs <= rev*(1-0.515) + D&A
SM_BUDGET, SM_3Q25 = float(b.sm_cash), float(b.sm_cash/(1+b.sm_cash_yoy_pct/100))
for rv in [4744.3, 4770.0, 4804.0, 4850.0]:
    c = rv*(1-THR/100) + DA; sm = SM_BUDGET - (COST0 - c)
    rows.append((f"51.5% at revenue {rv:.1f}: cash costs allowed, gap vs budget, S&M if whole gap is S&M, y/y", f"{c:.1f}, {c-COST0:+.1f}, {sm:.0f}, {100*(sm/SM_3Q25-1):+.1f}%"))
rows.append(("S&M budget (line build sm_cash), 3Q25 cash S&M base, budget y/y", f"{SM_BUDGET:.1f}, {SM_3Q25:.1f}, {100*(SM_BUDGET/SM_3Q25-1):+.1f}%"))
rows.append(("1H26 printed S&M y/y: 1Q26, 2Q26", f"{100*(751/563-1):.1f}%, {100*(875/691-1):.1f}%"))
# --- 6. revision-2 blend
routes = {"card bias-corrected N(50.21,1.62)": (0.35, 1-Phi((THR-(MU-b5))/sd_w2)),
          "corrected cost stack, sd 72": (0.25, float((mc(sd_cost=72.0)>=THR).mean())),
          "M5 composite (anchor)": (0.20, 1-Phi((THR-50.19)/1.356)),
          "ceiling base rate Laplace": (0.20, 1/6)}
blend = sum(w*p for w,p in routes.values())
for k,(w,p) in routes.items(): rows.append((f"route {k}: weight, P", f"{w:.2f}, {p:.4f}"))
rows.append(("revision-2 blend P(>=51.5)", round(blend,4)))
rows.append(("auditor blend 0.40/0.25/0.20/0.15 on 0.2136/0.2806/0.167/0.167", round(0.40*0.2136+0.25*0.2806+0.20*0.167+0.15*0.167,4)))
out = pd.DataFrame(rows, columns=["item","value"]); out.to_csv(HERE/"r05_results_v2.csv", index=False)
pd.set_option("display.max_colwidth", 200); print(out.to_string())
