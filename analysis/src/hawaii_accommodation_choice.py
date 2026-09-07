"""Who picks a rental over a hotel? Hawaii DBEDT 2024 Annual Visitor Research Report, by source market.

Hawaii is the one US destination whose government publishes accommodation choice (hotel / condo /
timeshare / rental home / friends-relatives) next to trip characteristics, by source market and by
island. Inputs are hand-transcribed from the report narrative (tables 15-35 and 57-63); see
data/processed/hawaii_dbedt_2024_accommodation_by_market.csv and ..._by_island.csv.

Outputs analysis/figures/10_hawaii_stay_length_vs_rental.png and prints rank correlations.
Run from repo root: python analysis/src/hawaii_accommodation_choice.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
S1, S2, GRID, INK2, MUTED, SURF = "#2a78d6", "#eb6834", "#e1e0d9", "#52514e", "#898781", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "font.size": 10})

d = pd.read_csv(ROOT / "data/processed/hawaii_dbedt_2024_accommodation_by_market.csv")
d["self_catering_pct"] = d[["condo_pct", "rental_home_pct"]].fillna(0).sum(axis=1)

print("Spearman rank correlations across 11 source markets (2024):")
for y in ["hotel_pct", "self_catering_pct"]:
    for x in ["avg_length_of_stay_days", "first_time_pct", "honeymoon_pct", "vfr_pct"]:
        s = d[[x, y]].dropna(); rs, p = stats.spearmanr(s[x], s[y])
        print(f"  {y:18s} vs {x:24s} n={len(s):2d} rho={rs:+.2f} p={p:.2f}")

fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(d["avg_length_of_stay_days"], d["self_catering_pct"], s=d["hotel_pct"] * 3, color=S1, alpha=0.85, edgecolor="white")
for r in d.itertuples():
    ax.annotate(r.market, (r.avg_length_of_stay_days, r.self_catering_pct), xytext=(6, 4), textcoords="offset points", fontsize=8.5, color=INK2)
m, b = np.polyfit(d["avg_length_of_stay_days"], d["self_catering_pct"], 1)
xs = np.linspace(d["avg_length_of_stay_days"].min(), d["avg_length_of_stay_days"].max(), 10)
ax.plot(xs, m * xs + b, color=S2, lw=1.4, ls="--")
rs, p = stats.spearmanr(d["avg_length_of_stay_days"], d["self_catering_pct"])
ax.set_xlabel("average length of stay (days)"); ax.set_ylabel("% staying in condo or rental home")
ax.set_title(f"Hawaii 2024: longer trips pick rentals over hotels (Spearman {rs:+.2f}, p={p:.2f}, n=11)")
fig.text(0.01, 0.01, "Source: Hawaii DBEDT 2024 Annual Visitor Research Report, visitor characteristics by source market (tables 15-35). Bubble size = hotel share.\n"
         "Japan rental-home share not reported; condo + rental home = self-catering.", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.06, 1, 1))
(ROOT / "analysis/figures").mkdir(parents=True, exist_ok=True)
fig.savefig(ROOT / "analysis/figures/10_hawaii_stay_length_vs_rental.png", dpi=160)
print("wrote figure")

# ---------------------------------------------------------------- figure 13: who stays where (DBEDT tables 43-46)
seg = pd.read_csv(ROOT / "data/processed/hawaii_dbedt_2024_characteristics_by_accommodation.csv")
seg = seg[seg.segment.isin(["Hotel only", "Condo only", "Timeshare only", "Rental house only"])].set_index("segment")
metrics = [("party_three_plus_pct", "party of 3+ (%)"), ("independent_pct", "no package / independent (%)"), ("avg_stay_days", "avg stay (days)"),
           ("honeymoon_pct", "honeymoon (%)"), ("mci_pct", "meetings & conventions (%)"), ("first_time_pct", "first-time visitor (%)")]
fig, axes = plt.subplots(2, 3, figsize=(12, 6.2))
cols = {"Hotel only": S1, "Condo only": "#7aa7e0", "Timeshare only": "#b9cdea", "Rental house only": S2}
for ax, (m, lab) in zip(axes.flat, metrics):
    vals = seg[m]
    ax.bar(range(len(vals)), vals, color=[cols[s] for s in vals.index])
    ax.set_xticks(range(len(vals))); ax.set_xticklabels(["Hotel", "Condo", "Timeshare", "Rental\nhouse"], fontsize=9)
    for i, v in enumerate(vals):
        ax.annotate(f"{v:.1f}", (i, v), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    ax.set_title(lab, fontsize=10.5); ax.set_ylim(0, vals.max() * 1.25)
fig.suptitle("Hawaii 2024: who stays in a rental house vs a hotel (visitors who used only that accommodation type)", fontweight="bold", x=0.01, ha="left")
fig.text(0.01, 0.01, "Source: Hawaii DBEDT 2024 Annual Visitor Research Report, Tables 43-46 (hotel-only 4.91M visitors, condo-only 1.08M, timeshare-only 0.68M, rental-house-only 0.76M).", fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 0.95))
fig.savefig(ROOT / "analysis/figures/13_hawaii_who_stays_where.png", dpi=160)
print("wrote figure 13")
