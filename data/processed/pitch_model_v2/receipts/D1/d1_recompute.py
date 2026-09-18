"""D1 recompute: from the reviews-index backtest and nowcast to the committed
3Q26 nights level, and the scenario table in millions of nights.

Reads only files the two q3nowcast scripts just wrote (or that are committed):
  data/processed/q3nowcast/E/backtest_wf_paths.csv   walk-forward errors per quarter
  data/processed/q3nowcast/E/q3_2026_nowcast.csv     implied nights y/y per index row
  data/processed/abnb_driver_history_quarterly.csv   printed nights, the 3Q25 base
  data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv  external stack

Writes, under this receipt folder only:
  d1_scenarios.csv     scenario x period x point/low/high in millions and in pct
  d1_recompute.json    the chain, with the committed values it is checked against
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
E = ROOT / "data/processed/q3nowcast/E"
FEAT, TGT, LAG = "GLOBAL|yoy_all|w_reviews", "nights_yoy", 0

kpi = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
base_3q25 = float(kpi[(kpi.year == 2025) & (kpi.q == 3)].nights_m.iloc[0])
naive_2q26 = float(kpi[(kpi.year == 2026) & (kpi.q == 2)].nights_m_yoy_pct.iloc[0])

p = pd.read_csv(E / "backtest_wf_paths.csv")
p = p[(p.feature == FEAT) & (p.target == TGT) & (p.lag == LAG)]
bias = p.groupby("window").err_feature.agg(["count", "mean"])  # err = pred - actual

nc = pd.read_csv(E / "q3_2026_nowcast.csv")
hd = nc[(nc.measure == "yoy_all") & (nc.weighting == "w_reviews") & (nc.region == "GLOBAL")].iloc[0]
raw = float(hd.implied_nights_yoy)
w2_bias = float(bias.loc["2023Q1+", "mean"])
w1_bias = float(bias.loc["2022Q1+", "mean"])
corrected_w2 = raw - w2_bias
corrected_w1 = raw - w1_bias

# the seven index rows E6 writes (all-reviews and vintage-matched, four weightings)
seven = pd.DataFrame([dict(row=f"{r.region}|{r.measure}|{r.weighting}",
                           implied=float(r.implied_nights_yoy)) for _, r in nc.iterrows()])

def nights(g_pct: float) -> float:
    return round(base_3q25 * (1 + g_pct / 100.0), 2)

def yoy(n_m: float) -> float:
    return round((n_m / base_3q25 - 1) * 100.0, 2)

# Scenario cells.  The three points are the governing committed growth rates
# (memo v3, 17 Sep).  The outer low/high are the 10th and 90th percentiles of the
# adopted 3Q26 print object N(9.5, 1.70) (adopted_print_states_v2.json, A09 rev 2,
# 17 Sep), so the three scenarios partition one distribution instead of three.
# Every level below is recomputed here from the 3Q25 base; none is copied.
Z90 = 1.2815515655446004  # Phi^-1(0.90)
ADOPTED_CENTRE, ADOPTED_SD = 9.5, 1.70
p10 = ADOPTED_CENTRE - Z90 * ADOPTED_SD
p90 = ADOPTED_CENTRE + Z90 * ADOPTED_SD
cells = [
    ("base",    "point", 9.5),   ("base",    "low", 8.5),  ("base",    "high", 10.0),
    ("short",   "point", 8.5),   ("short",   "low", p10),  ("short",   "high", 9.5),
    ("breaker", "point", 10.0),  ("breaker", "low", 10.0), ("breaker", "high", p90),
]
sc = pd.DataFrame([dict(scenario=s, cell=c, yoy_pct=round(g, 4), nights_m=nights(g),
                        nights_m_1dp=round(nights(g), 1)) for s, c, g in cells])
sc.to_csv(HERE / "d1_scenarios.csv", index=False)

street = dict(mean_m=148.9, low_m=147.0, high_m=151.0, n_estimates=28,
              source="Bloomberg MODL aggregate, 12 Sep 2026 (quoted from memo v3; licensed, not in repo)",
              mean_yoy_pct=yoy(148.9), low_yoy_pct=yoy(147.0), high_yoy_pct=yoy(151.0))

g2 = pd.read_csv(ROOT / "data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv")
g2n = g2[g2.target == "nights_m_yoy_pct"]

out = dict(
    base_3q25_nights_m=base_3q25, naive_2q26_yoy_pct=naive_2q26,
    index_row=FEAT,
    index_raw_implied_yoy_pct=round(raw, 4),
    index_band_lo_hi=[round(float(hd.lo), 4), round(float(hd.hi), 4)],
    wf_ratio_vs_naive_W2=round(float(hd.wf_ratio_vs_naive), 6),
    wf_bias_pp={"W2_2023Q1+": round(w2_bias, 4), "W1_2022Q1+": round(w1_bias, 4)},
    wf_n={"W2_2023Q1+": int(bias.loc["2023Q1+", "count"]), "W1_2022Q1+": int(bias.loc["2022Q1+", "count"])},
    bias_corrected_yoy_pct={"W2": round(corrected_w2, 4), "W1": round(corrected_w1, 4)},
    bias_corrected_nights_m={"W2": nights(corrected_w2), "W1": nights(corrected_w1)},
    committed_base_nights_m=146.3, committed_base_yoy_pct=9.5,
    match_base_level_abs_diff=round(abs(nights(corrected_w2) - 146.3), 4),
    seven_rows_implied=[round(v, 4) for v in seven.implied.tolist()],
    external_stack={"n": int(len(g2n)), "median_yoy_pct": round(float(g2n.pred_3q26.median()), 4),
                    "min": round(float(g2n.pred_3q26.min()), 4), "max": round(float(g2n.pred_3q26.max()), 4)},
    street=street,
    adopted_print_object={"form": "N(9.5, 1.70) on latent 3Q26 nights y/y over the 133.6m base",
                          "p10_yoy_pct": round(p10, 4), "p10_nights_m": nights(p10),
                          "p90_yoy_pct": round(p90, 4), "p90_nights_m": nights(p90),
                          "source": "docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json (A09 rev 2, 17 Sep 2026); read only"},
    scenarios=sc.to_dict("records"),
)
(HERE / "d1_recompute.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
