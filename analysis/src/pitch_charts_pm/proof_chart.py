"""Graph 2 of the PM-feedback memo (v4): the reviews stays index against reported nights.

Out-of-sample (walk-forward, refit each quarter) predictions of the stays index for 1Q24-2Q26 (W2, n 10) against printed
Nights and Seats Booked y/y, then the 3Q26 read (frozen 1Q23-2Q25 mapping, +/-1 walk-forward RMSE band), the team model's
3Q26 (+9.2%, model v2) and the Street (Bloomberg MODL 12 Sep 2026: mean 149.0m = +11.5%, 28 estimates, 147.0-151.0m).

Inputs (read-only):
  data/processed/forecast_methods/reviews_index_v2/stage_b_paths.csv   measure yoy_vmatch_mix, window W2, subset full
  data/processed/forecast_methods/reviews_index_v2/stage_c3_3q26.json   implied_nights_yoy, band_pp
  data/processed/forecast_methods/reviews_index_v2/stage_e_view_vs_street.csv  Street mean / low / high (3Q26)
  data/processed/pitch_charts/n07_nights_caimanes.csv                   team model v2 3Q26 total (9.20)
Output: deck/Graphs/pm_feedback_v4/graph2_stays_index_proof.png (7.2 x 4.9 in, 300 dpi, STYLE.md canvas)
Run from the repo root: python analysis/src/pitch_charts_pm/proof_chart.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RI = ROOT / "data/processed/forecast_methods/reviews_index_v2"
OUT = ROOT / "deck/Graphs/pm_feedback_v4"
OUT.mkdir(parents=True, exist_ok=True)

# STYLE.md palette
TEAL, RED, INK, MUTED, GRIDC, LGRAY, BAND = "#00A3A1", "#D4145A", "#000000", "#7a7a7a", "#e4e4e4", "#cfcfcf", "#f0f0f0"
TITLE_GREY = "#4a4a4a"
BODY_FONT = "Carlito"  # metric-compatible with Calibri (STYLE.md's in-graph font)
TITLE_FONT = "Liberation Sans"  # Helvetica stand-in

paths = pd.read_csv(RI / "stage_b_paths.csv")
wf = paths[(paths.measure == "yoy_vmatch_mix") & (paths.window == "W2") & (paths.subset == "full")].copy()
wf["q"] = wf.t.map(lambda t: f"{t % 4 + 1}Q{str(t // 4)[2:]}")
c3 = json.loads((RI / "stage_c3_3q26.json").read_text())
vs = pd.read_csv(RI / "stage_e_view_vs_street.csv").set_index("quarter").loc["3Q26"]
nights_3q25 = 133.6
street_mean = float(vs.street_yoy)
street_lo = (float(vs.street_low_m) / nights_3q25 - 1) * 100
street_hi = (float(vs.street_high_m) / nights_3q25 - 1) * 100
n07 = pd.read_csv(ROOT / "data/processed/pitch_charts/n07_nights_caimanes.csv").set_index("quarter")
ours = float(n07.loc["3Q26", "total"])
read, band = float(c3["implied_nights_yoy"]), float(c3["band_pp"])

TS = 1.7
plt.rcParams.update({"font.family": BODY_FONT, "font.size": 8 * TS})
fig, ax = plt.subplots(figsize=(7.2, 4.9), dpi=300)
fig.subplots_adjust(left=0.075, right=0.985, top=0.80, bottom=0.10)

x = list(range(len(wf)))
xf = len(wf)  # 3Q26
labels = list(wf.q) + ["3Q26"]

ax.axvspan(xf - 0.5, xf + 2.2, color=BAND, zorder=0, lw=0)
ax.text(xf - 0.42, 13.75, "Next print (5 Nov)", color=MUTED, fontsize=7 * TS, va="top", linespacing=1.0)

ax.plot(x, wf.actual, color=INK, lw=1.4 * 1.5, zorder=3)
ax.scatter(x, wf.actual, color=INK, s=16 * 1.5, zorder=4)
ax.scatter(x, wf.pred, facecolor="white", edgecolor=TEAL, lw=1.4 * 1.5, s=34 * 1.5, zorder=5)

# 3Q26: stays-index read with its +/-1 RMSE band, our model, the Street range
ax.plot([xf, xf], [read - band, read + band], color=TEAL, lw=5 * 1.5, alpha=0.35, solid_capstyle="butt", zorder=2)
ax.scatter([xf], [read], facecolor="white", edgecolor=TEAL, lw=1.4 * 1.5, s=34 * 1.5, zorder=5)
ax.scatter([xf + 0.28], [ours], color=RED, marker="D", s=26 * 1.5, zorder=5)
ax.plot([xf + 0.1, xf + 1.0], [street_mean] * 2, color=INK, lw=1.2 * 1.5, ls=(0, (2, 1.5)), zorder=4)
ax.plot([xf + 1.62, xf + 1.62], [street_lo, street_hi], color=MUTED, lw=1.0 * 1.5, zorder=3)
for yv in (street_lo, street_hi):
    ax.plot([xf + 1.55, xf + 1.69], [yv, yv], color=MUTED, lw=1.0 * 1.5, zorder=3)

ax.text(xf, read - band - 0.12, f"Stays index\n{read:.1f} \u00b1 {band:.1f}", ha="center", va="top", fontsize=7.2 * TS, color=INK, linespacing=1.0)
ax.text(xf + 0.36, ours - 0.12, f"Ours {ours:.1f}", ha="left", va="top", fontsize=7.2 * TS, color=INK)
ax.text(xf + 0.1, street_mean + 0.15, f"Street {street_mean:.1f}", ha="left", va="bottom", fontsize=7.2 * TS, color=INK)
ax.text(xf + 1.62, street_lo - 0.12, "Range of\n28 est.", ha="center", va="top", fontsize=6.4 * TS, color=MUTED, linespacing=1.0)

ax.set_xticks(x + [xf])
ax.set_xticklabels(labels)
ax.set_xlim(-0.6, xf + 2.25)
ax.set_ylim(6, 14)
ax.set_yticks(range(6, 15, 2))
ax.set_yticklabels([f"{v}%" for v in range(6, 15, 2)])
ax.yaxis.grid(True, color=GRIDC, lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(INK)
ax.spines["bottom"].set_linewidth(1.4)
ax.tick_params(axis="both", length=0, colors=INK)

fig.text(0.012, 0.955, "Nights y/y: reported vs our stays index (out of sample), %", fontfamily=TITLE_FONT,
         fontweight="bold", fontsize=9.5 * TS * 0.92, color=TITLE_GREY, ha="left", va="top")
# key row
ky = 0.865
fig.lines.append(plt.Line2D([0.015, 0.045], [ky, ky], color=INK, lw=2.1, transform=fig.transFigure))
fig.text(0.052, ky, "Reported", va="center", fontsize=7.6 * TS)
fig.patches.append(matplotlib.patches.Circle((0.205, ky), 0.0085, transform=fig.transFigure, fc="white", ec=TEAL, lw=2.1))
fig.text(0.222, ky, "Stays index, predicted before the print", va="center", fontsize=7.6 * TS)
fig.lines.append(plt.Line2D([0.648], [ky], marker="D", color=RED, ms=6, transform=fig.transFigure))
fig.text(0.663, ky, "Team model", va="center", fontsize=7.6 * TS)
fig.lines.append(plt.Line2D([0.815, 0.855], [ky, ky], color=INK, lw=1.8, ls=(0, (2, 1.5)), transform=fig.transFigure))
fig.text(0.862, ky, "Street", va="center", fontsize=7.6 * TS)

fig.savefig(OUT / "graph2_stays_index_proof.png", dpi=300)
print("wrote", OUT / "graph2_stays_index_proof.png", f"read {read:.2f} band {band:.2f} ours {ours:.2f} street {street_mean:.2f} ({street_lo:.1f}-{street_hi:.1f})")
