"""Two figures for M3. py -3.13 analysis/src/margin_build/M3_guide_policy_margin/make_figures.py"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DATA = REPO / "data" / "processed" / "margin_build" / "M3_guide_policy_margin"
FIG = REPO / "analysis" / "figures" / "margin_build"
FIG.mkdir(parents=True, exist_ok=True)

# ---- 1. the cushion history --------------------------------------------------
c = pd.read_csv(DATA / "M3_cushion_history.csv").dropna(subset=["cushion_pp"])
fig, ax = plt.subplots(figsize=(7.2, 4.0))
for b, m in (("FEB", "o"), ("MAY", "s"), ("AUG", "^"), ("NOV", "D")):
    s = c[c["bucket"] == b].sort_values("fy")
    ax.plot(s["fy"], s["cushion_pp"], marker=m, label=b)
ax.axhline(0, color="k", lw=0.8)
ax.set_title("Cushion: FY adj-EBITDA margin actual minus the guide in force (pp)")
ax.set_xlabel("fiscal year")
ax.set_ylabel("pp")
ax.set_xticks(sorted(c["fy"].unique()))
ax.legend(title="guide bucket", fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "M3_guide_policy_margin_cushion_history.png", dpi=150)
plt.close(fig)

# ---- 2. h = 0 MAE, M3 specs vs baselines -------------------------------------
s = pd.read_csv(REPO / "data" / "processed" / "margin_build" / "10_harness_margin" / "scoreboard_margin.csv")
s = s[(s["target"] == "adj_ebitda_margin_pct") & (s["prior_basis"] == "PIT") & (s["horizon_q"] == 0)]
m3 = s[(s["method"] == "guide-policy-margin") & (s["object"] == "actual_given_guide")]
bl = s[(s["method"] == "baselines-margin") &
       s["object"].isin(["seasonal_naive", "street", "guide_implied", "q_guide_implied"])]
rows = ([(f"M3 {r.spec_id}", r.window, r.mae, r.rw_mae) for r in m3.itertuples()] +
        [(r.object, r.window, r.mae, r.rw_mae) for r in bl.itertuples()])
d = pd.DataFrame(rows, columns=["label", "window", "mae", "rw_mae"])
p = d.pivot_table(index="label", columns="window", values="mae").sort_values("W1")
fig, ax = plt.subplots(figsize=(8.0, 4.4))
x = np.arange(len(p))
ax.barh(x - 0.2, p["W1"], height=0.38, label="W1 (n=14)")
ax.barh(x + 0.2, p["W2"], height=0.38, label="W2 (n=10)")
ax.set_yticks(x)
ax.set_yticklabels(p.index, fontsize=8)
ax.set_xlabel("MAE, adj EBITDA margin (pp), h = 0, PIT replay")
ax.set_title("M3 guidance-policy specs vs the margin baselines, h = 0")
ax.legend(fontsize=8)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "M3_guide_policy_margin_h0_mae.png", dpi=150)
plt.close(fig)
print("wrote", FIG / "M3_guide_policy_margin_cushion_history.png", "and", FIG / "M3_guide_policy_margin_h0_mae.png")
