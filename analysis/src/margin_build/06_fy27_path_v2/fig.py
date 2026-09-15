"""Figure for WS06: quarterly nights / ADR / revenue growth path 3Q26-4Q27 by scenario, with PR #32, WS29 and consensus.

Run with py -3.13 (matplotlib lives there); called by run.py after the CSVs are written. Reads only the 06 outputs.
    py -3.13 analysis/src/margin_build/06_fy27_path_v2/fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/margin_build/06_fy27_path_v2"
FIG = ROOT / "analysis/figures/margin_build"
FIG.mkdir(parents=True, exist_ok=True)

wide = pd.read_csv(OUT / "06_revenue_path_wide.csv")
comp = pd.read_csv(OUT / "06_comparison_quarterly.csv")
Q = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
wide = wide[wide.quarter.isin(Q)]
x = range(len(Q))
col = {"bear": "#b34a4a", "base": "#1f4e79", "bull": "#3a8a5a"}

fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
panels = [("nights_yoy_pct", "Nights and seats y/y, %", "pr32_base_nights_global_lap_pct", "ws29_base_nights_pct", None),
          ("adr_reported_yoy_pct", "Reported ADR y/y, %", None, None, None),
          ("revenue_yoy_pct", "Revenue y/y, %", None, "ws29_base_revenue_yoy_pct", "consensus_implied_revenue_yoy_pct")]
for ax, (line, title, p32col, w29col, ccol) in zip(axes, panels):
    for scen in ("bear", "base", "bull"):
        s = wide[wide.scenario == scen].set_index("quarter").reindex(Q)[line]
        ax.plot(list(x), s.values, marker="o", color=col[scen], lw=2 if scen == "base" else 1.2, label=f"06 v2 {scen}")
    c = comp.set_index("quarter").reindex(Q)
    if p32col and p32col in c:
        ax.plot(list(x), c[p32col].values, ls="--", color="grey", label="PR #32 base (global lap)")
        ax.plot(list(x), c["pr32_base_nights_na_only_lap_pct"].values, ls=":", color="grey", label="PR #32 base (NA-only lap)")
    if w29col and w29col in c:
        ax.plot(list(x), c[w29col].values, ls="-.", color="#c08a00", label="WS29 base")
    if ccol and ccol in c:
        ax.plot(list(x), c[ccol].values, marker="s", ls="none", color="black", label="LSEG consensus (comparison)")
    ax.set_xticks(list(x)); ax.set_xticklabels(Q); ax.set_title(title); ax.grid(alpha=0.3); ax.axhline(0, color="black", lw=0.5)
    ax.legend(fontsize=7)
fig.suptitle("WS06 FY27 revenue path v2: 3Q26-4Q26 from bridge v3, 1Q27-4Q27 rebuilt on the same decomposition (consensus is a comparison only)", fontsize=10)
fig.tight_layout()
fig.savefig(FIG / "06_fy27_path_v2_quarterly.png", dpi=130)
print("wrote", FIG / "06_fy27_path_v2_quarterly.png")
