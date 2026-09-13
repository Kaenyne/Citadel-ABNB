"""Figures for the WS02 financial panel. Run with py -3.13 (matplotlib); called by run.py (non-fatal if unavailable).
Writes analysis/figures/margin_build/02_financial_panel_*.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/margin_build/02_financial_panel"
FIG = ROOT / "analysis/figures/margin_build"
FIG.mkdir(parents=True, exist_ok=True)

P = pd.read_csv(OUT / "02_panel_quarterly.csv")
S = pd.read_csv(OUT / "02_seasonality.csv")

# 1. Adjusted EBITDA margin by quarter, one line per year (seasonal profile)
fig, ax = plt.subplots(figsize=(8, 4.5))
for y, g in P.groupby("year"):
    if g["adj_ebitda_margin_pct"].notna().sum() < 2 or y < 2019:
        continue
    ax.plot(g["qn"], g["adj_ebitda_margin_pct"], marker="o", label=str(y), alpha=0.5 if y < 2023 else 1.0, lw=1 if y < 2023 else 2)
ax.set_xticks([1, 2, 3, 4]); ax.set_xticklabels(["Q1", "Q2", "Q3", "Q4"])
ax.set_ylabel("Adjusted EBITDA margin, %"); ax.set_title("ABNB Adjusted EBITDA margin by quarter (2020 omitted below -40%)")
ax.set_ylim(-45, 60); ax.axhline(0, color="k", lw=0.5); ax.legend(ncol=4, fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(FIG / "02_financial_panel_margin_seasonality.png", dpi=150); plt.close(fig)

# 2. Cash cost lines as % of revenue, 1Q19-2Q26
fig, ax = plt.subplots(figsize=(10, 4.5))
x = range(len(P))
for line, lab in (("cor_cash_pct_rev", "Cost of revenue"), ("ops_cash_pct_rev", "Ops & support (cash)"), ("pd_cash_pct_rev", "Product dev (cash)"),
                  ("sm_cash_pct_rev", "Sales & marketing (cash)"), ("ga_cash_pct_rev", "G&A (cash)")):
    ax.plot(list(x), P[line], marker=".", label=lab)
ax.set_xticks(list(x)[::2]); ax.set_xticklabels(P["quarter"][::2], rotation=60, fontsize=7)
ax.set_ylim(0, 60); ax.set_ylabel("% of revenue"); ax.set_title("ABNB cash (ex-SBC) cost lines as % of revenue, 1Q18-2Q26 (2Q20 clipped)")
ax.legend(fontsize=8, ncol=3); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(FIG / "02_financial_panel_cost_lines_pct_rev.png", dpi=150); plt.close(fig)

# 3. Cash cost per night by quarter, 2022-2026
fig, ax = plt.subplots(figsize=(10, 4.5))
Q = P[P["year"] >= 2021].reset_index(drop=True)
for line, lab in (("cor_cash_per_night_usd", "Cost of revenue"), ("ops_cash_per_night_usd", "Ops & support"), ("pd_cash_per_night_usd", "Product dev"),
                  ("sm_cash_per_night_usd", "Sales & marketing"), ("ga_cash_per_night_usd", "G&A")):
    ax.plot(range(len(Q)), Q[line], marker=".", label=lab)
ax.set_xticks(range(len(Q))); ax.set_xticklabels(Q["quarter"], rotation=60, fontsize=7)
ax.set_ylabel("USD per night booked"); ax.set_title("ABNB cash cost per night booked, 1Q21-2Q26"); ax.legend(fontsize=8, ncol=3); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(FIG / "02_financial_panel_cost_per_night.png", dpi=150); plt.close(fig)
print("figures written")
sys.exit(0)
