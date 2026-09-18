"""C3 independent recompute: reproduce 40_line_build's product-development formula
(pd_2h26, pd_fy27, and the per-quarter pd_cash spread on the 2023-25 quarterly shares)
for every committed (quarter, scenario) cell in 40_lines_quarterly.csv, 40_annual.csv
and 40_short_case_quarterly.csv, using only 40_params.csv values and the committed
actual pd_cash inputs from the 02_financial_panel (3Q25, 4Q25, 1Q26, 2Q26) -- no
re-derivation of the revenue path or any other line, since product development has
no dependency on revenue, nights or GBV in this build.

Read-only: writes only inside this receipt folder (data/processed/pitch_model_v2/receipts/C3/).
Formula transcribed from analysis/src/margin_build/40_line_build/run.py lines 32-33
(SHARE, H2), 60-62 (params), 124-125 (pd_2h26, pd_fy27), 171 (quarterly spread).
"""
from pathlib import Path
import pandas as pd

ROOT = Path("/Users/theomachado/Citadel-ABNB")
LB = ROOT / "data/processed/margin_build/40_line_build"
PAN = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
OUT = ROOT / "data/processed/pitch_model_v2/receipts/C3"

SHARE_PD = {1: .2548, 2: .2466, 3: .2459, 4: .2527}
H2_PD = SHARE_PD[3] + SHARE_PD[4]
Q_ORDER = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
QN = {"3Q26": 3, "4Q26": 4, "1Q27": 1, "2Q27": 2, "3Q27": 3, "4Q27": 4}

params = pd.read_csv(LB / "40_params.csv").set_index("name")
def pv(name, scen):
    return float(params.loc[name, scen])

pan = pd.read_csv(PAN).set_index("quarter")

def recompute_pd(cost_scen: str) -> dict:
    """cost_scen in {'base','bear','bull'} -- the cost_scenario column of 40_params.csv."""
    g2h26 = pv("pd_growth_2h26", cost_scen)
    gfy27 = pv("pd_growth_fy27", cost_scen)
    ai_fy27 = pv("pd_ai_tooling_fy27", cost_scen)
    pd_2h26 = float(pan.loc["3Q25", "pd_cash"] + pan.loc["4Q25", "pd_cash"]) * (1 + g2h26 / 100)
    pd_fy27 = (float(pan.loc["1Q26", "pd_cash"] + pan.loc["2Q26", "pd_cash"]) + pd_2h26) * (1 + gfy27 / 100) + ai_fy27
    out = {}
    for q in Q_ORDER:
        qn = QN[q]
        is27 = q.endswith("27")
        out[q] = pd_fy27 * SHARE_PD[qn] if is27 else pd_2h26 * SHARE_PD[qn] / H2_PD
    out["pd_2h26_musd"] = pd_2h26
    out["pd_fy27_musd"] = pd_fy27
    out["FY26"] = float(pan.loc["1Q26", "pd_cash"] + pan.loc["2Q26", "pd_cash"]) + pd_2h26
    out["FY27"] = pd_fy27
    return out

rows = []
lq = pd.read_csv(LB / "40_lines_quarterly.csv")
ann = pd.read_csv(LB / "40_annual.csv")
sc = pd.read_csv(LB / "40_short_case_quarterly.csv").set_index("quarter")

for scen_label, cost_scen in [("base", "base"), ("cost_bull", "bull")]:
    committed_q = lq[lq.scenario == scen_label].set_index("quarter")["pd_cash"]
    committed_a = ann[ann.scenario == scen_label].set_index("period")["pd_cash"]
    recomputed = recompute_pd(cost_scen)
    for q in Q_ORDER:
        rows.append(dict(source="40_lines_quarterly.csv", scenario=scen_label, period=q,
                          committed=float(committed_q[q]), recomputed=recomputed[q],
                          diff=float(committed_q[q]) - recomputed[q]))
    for per in ["FY26", "FY27"]:
        rows.append(dict(source="40_annual.csv", scenario=scen_label, period=per,
                          committed=float(committed_a[per]), recomputed=recomputed[per],
                          diff=float(committed_a[per]) - recomputed[per]))

# short case: cost_scenario is "base" throughout (no PD-specific overlay in the short case;
# only the revenue path and three ops/chargeback/interest overlays change) -- pd_cash should
# equal the base-cost recompute exactly, quarter for quarter.
recomputed_base = recompute_pd("base")
for q in Q_ORDER:
    rows.append(dict(source="40_short_case_quarterly.csv", scenario="short", period=q,
                      committed=float(sc.loc[q, "pd_cash"]), recomputed=recomputed_base[q],
                      diff=float(sc.loc[q, "pd_cash"]) - recomputed_base[q]))

df = pd.DataFrame(rows)
df.to_csv(OUT / "c3_pd_recompute_check.csv", index=False)
maxdiff = df["diff"].abs().max()
print(df.to_string())
print("max abs diff (pd_cash, base/cost_bull/short vs 40_params.csv recompute):", maxdiff)
assert maxdiff < 1e-6, "recompute mismatch"
print("PASS: product-development pd_2h26 / pd_fy27 / quarterly spread reproduce exactly from 40_params.csv "
      "and the 02_financial_panel actuals, for base, cost_bull (breaker) and the short case.")
