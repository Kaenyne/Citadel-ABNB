"""B09 bonus-sbc-step-up: P(4Q26 SBC >= $500M). numpy/pandas only, seed 20260917.
  py -3.13 docs/pitch-forecasts/questions/bonus-sbc-step-up/datasets/b09_model.py
"""
import pathlib
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260917)
N = 400_000
here = pathlib.Path(__file__).resolve().parent

# history: the letters' adjusted-EBITDA reconciliation tables (4Q = FY less 9M; 4Q24 $368M and 4Q25 $411M per the 4Q24/4Q25 letters and the 1Q26/2Q26 nine-quarter tables)
q = ["1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
s = [195, 247, 234, 254, 240, 304, 286, 290, 295, 382, 362, 368, 358, 424, 399, 411, 410, 487]
h = pd.DataFrame({"quarter": q, "sbc": s})
h["yoy_pct"] = h["sbc"].pct_change(4) * 100
h["q4_over_q2"] = np.nan
for i, qq in enumerate(q):
    if qq.startswith("4Q"):
        h.loc[i, "q4_over_q2"] = h.loc[i, "sbc"] / h.loc[i - 2, "sbc"]
h.to_csv(here / "b09_history.csv", index=False)
rows = []
ratios = h["q4_over_q2"].dropna()
rows += [("q4_over_q2_mean_all4", ratios.mean()), ("q4_over_q2_sd_all4", ratios.std(ddof=1)),
         ("q4_over_q2_mean_2023_25", ratios.iloc[1:].mean()), ("q4_over_q2_sd_2023_25", ratios.iloc[1:].std(ddof=1))]

# Route A: Q4/Q2 seasonal ratio applied to 2Q26 $487M
for lab, mu, sd in [("A_all4", ratios.mean(), ratios.std(ddof=1)),
                    ("A_2023_25_sd0.035", ratios.iloc[1:].mean(), 0.035),
                    ("A_2023_25_sd0.02", ratios.iloc[1:].mean(), 0.02)]:
    x = 487 * rng.normal(mu, sd, N) + rng.normal(0, 8, N)
    rows += [(f"route_{lab}_p_ge_500", (x >= 500).mean()), (f"route_{lab}_median", np.median(x))]

# Route B: y/y rule on 4Q25 $411M with the recent growth regime
yy = h["yoy_pct"].dropna().iloc[-8:]
rows += [("yoy_last8_mean", yy.mean()), ("yoy_last8_sd", yy.std(ddof=1)), ("yoy_last4_mean", yy.iloc[-4:].mean())]
for lab, mu, sd in [("B_m7_13.2_sd6", 13.18, 6.0), ("B_last4_sd5", yy.iloc[-4:].mean(), 5.0),
                    ("B_last8_own_sd", yy.mean(), yy.std(ddof=1)), ("B_1H26_14.7_sd4", 14.7, 4.0)]:
    x = 411 * (1 + rng.normal(mu, sd, N) / 100)
    rows += [(f"route_{lab}_p_ge_500", (x >= 500).mean()), (f"route_{lab}_median", np.median(x))]
rows += [("needed_yoy_on_411_pct", (500 / 411 - 1) * 100), ("needed_yoy_on_400_pct", 25.0), ("needed_q4_over_q2", 500 / 487)]

# Route C: the 4Q25 letter's FY26 sentence (SBC growth lower than 2025's +13.1%)
fy_cap = 1592 * 1.131
q3 = 399 * 1.132
rows += [("C_fy26_cap", fy_cap), ("C_3q26_rule", q3), ("C_4q26_at_cap", fy_cap - 897 - q3),
         ("C_fy26_growth_needed_for_500_pct", ((897 + q3 + 500) / 1592 - 1) * 100)]
# FY SBC guide record: 2023 ~20% -> 18.3 (beat); 2024 ~20%, then ~25% -> 30.8 (miss by 10.8 / 5.8); 2025 'approximate headcount' -> 13.1 vs 12.3 (met)
miss = rng.random(N) < 0.20
g = np.where(miss, rng.normal(6, 3, N), rng.normal(-1.5, 2.5, N))
fy = 1592 * (1 + (13.1 + g) / 100)
q4 = fy - 897 - q3 + rng.normal(0, 10, N)
rows += [("route_C_p_ge_500", (q4 >= 500).mean()), ("route_C_median", np.median(q4))]
for lab, pm in [("C_miss_0.10", 0.10), ("C_miss_0.35", 0.35)]:
    miss = rng.random(N) < pm
    g = np.where(miss, rng.normal(6, 3, N), rng.normal(-1.5, 2.5, N))
    q4 = 1592 * (1 + (13.1 + g) / 100) - 897 - q3 + rng.normal(0, 10, N)
    rows.append((f"route_{lab}_p_ge_500", (q4 >= 500).mean()))

d = dict(rows)
rows.append(("blend_0.4A_0.4B_0.2C", 0.4 * d["route_A_2023_25_sd0.035_p_ge_500"] + 0.4 * d["route_B_m7_13.2_sd6_p_ge_500"] + 0.2 * d["route_C_p_ge_500"]))
out = pd.DataFrame(rows, columns=["item", "value"])
out.to_csv(here / "b09_results.csv", index=False)
print(out.to_string())
