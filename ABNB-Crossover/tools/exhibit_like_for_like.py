"""Deck exhibit: like-for-like realized price and markdown breadth on identical products (built 2026-09-03).

Inputs: cc_matched_sku_q2_summary.csv (May-Jul 2025 vs May-Jul 2026) and cc_matched_sku_holiday_summary.csv
(Nov-Dec 2024 vs Nov-Dec 2025), bucket == "all" rows. Output: exhibit_like_for_like_price.png
Panel A: mean realized (current) price change on identical products, by banner, two windows.
Panel B: share of the same products carrying a markdown, before -> after, by banner and window.
Palette: dataviz reference slots 1-3 (validated 2026-09-01); before/after in Panel B use two steps of blue.
"""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
COL = {"kay.com": "#2a78d6", "zales.com": "#eb6834", "jared.com": "#1baf7a"}
NAME = {"kay.com": "Kay", "zales.com": "Zales", "jared.com": "Jared"}
BLUE_L, BLUE_D = "#86b6ef", "#1c5cab"   # sequential blue steps 250 / 550

q2 = pd.read_csv(os.path.join(HERE, "cc_matched_sku_q2_summary.csv")); q2 = q2[q2["bucket"] == "all"].set_index("domain")
hol = pd.read_csv(os.path.join(HERE, "cc_matched_sku_holiday_summary.csv")); hol = hol[hol["bucket"] == "all"].set_index("domain")
windows = [("Holiday FY26 vs FY25\n(Nov–Dec 2025 vs 2024)", hol), ("Q2 FY27 vs FY26\n(May–Jul 2026 vs 2025)", q2)]
banners = ["kay.com", "zales.com", "jared.com"]

fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.6), dpi=200, gridspec_kw={"wspace": 0.55, "width_ratios": [1, 1.1]})
fig.patch.set_facecolor(SURFACE)
for ax in axes:
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_alpha(0.4)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0); ax.tick_params(length=0, labelsize=9)

# ---------------- Panel A: realized price change on identical products ----------------
ax = axes[0]
w = 0.24
for k, dom in enumerate(banners):
    vals = [win[1].loc[dom, "mean_sale_chg_pct"] for win in windows]
    xs = [i + (k - 1) * w for i in range(len(windows))]
    ax.bar(xs, vals, width=w * 0.9, color=COL[dom], zorder=3, linewidth=0, label=NAME[dom])
    for x, v, win in zip(xs, vals, windows):
        n = int(win[1].loc[dom, "n"]); raised = win[1].loc[dom, "share_list_up"] * 100
        ax.text(x, v + (0.7 if v >= 0 else -0.7), f"{v:+.1f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, color=INK, fontweight="bold")
        ax.text(x, -6.2, f"n={n}\nlist raised\non {raised:.0f}%", ha="center", va="top", fontsize=7, color=INK2, linespacing=1.15)
ax.axhline(0, color=INK2, linewidth=0.8, alpha=0.6, zorder=2)
ax.set_xticks(range(len(windows))); ax.set_xticklabels([w_[0] for w_ in windows], fontsize=9)
ax.set_ylim(-14, 27)
ax.set_ylabel("mean change in realized price, identical products (%)", fontsize=8.5, color=INK2)
ax.legend(loc="upper left", fontsize=8.5, frameon=False, ncol=3)
ax.set_title("Same product, one year later: what it actually sells for\n(mean change in realized price; the median is 0% in every cell)", loc="left", fontsize=11, fontweight="bold", color=INK, pad=10)

# ---------------- Panel B: markdown breadth before -> after ----------------
ax = axes[1]
labels, y = [], 0
rows = []
for wi, (wname, tab) in enumerate(windows):
    for dom in banners:
        rows.append((f"{NAME[dom]} · {'Holiday' if wi == 0 else 'Q2'}", tab.loc[dom, "breadth_a"] * 100, tab.loc[dom, "breadth_b"] * 100, dom))
rows = rows[::-1]
for i, (lab, a, b, dom) in enumerate(rows):
    ax.plot([a, b], [i, i], color=GRID, linewidth=3, zorder=2)
    ax.plot([a], [i], marker="o", markersize=8, color=BLUE_L, markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=3)
    ax.plot([b], [i], marker="o", markersize=8, color=COL[dom], markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4)
    ax.text(min(a, b) - 2.5, i, f"{a:.0f}%", ha="right", va="center", fontsize=8, color=INK2)
    ax.text(max(a, b) + 2.5, i, f"{b:.0f}%  ({b - a:+.0f} pts)", ha="left", va="center", fontsize=8.5, color=INK, fontweight="bold")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
ax.set_xlim(0, 125); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0); ax.grid(axis="y", visible=False)
ax.set_title("Share of those same products carrying a markdown, before → after", loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=10)
ax.plot([], [], marker="o", color=BLUE_L, linestyle="none", markersize=7, label="year-ago window"); ax.plot([], [], marker="o", color=INK2, linestyle="none", markersize=7, label="latest window (banner colour)")
ax.legend(loc="upper left", fontsize=8, frameon=False)

fig.text(0.125, -0.06,
         "Source: Common Crawl product pages; product codes present in both windows were matched and both captures parsed (819 pairs May–Jul 2025 vs 2026; 825 pairs Nov–Dec 2024 vs 2025; 34–57% same calendar month). "
         "Realized price = listed current price on the product page; list = the page's compare-at (msrp). Matched items are the persistent core of each catalog, so new-collection pricing is excluded; sitewide promo codes applied at checkout are not visible.",
         fontsize=7.2, color=INK2, wrap=True)
out = os.path.join(HERE, "exhibit_like_for_like_price.png")
fig.savefig(out, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
print("saved", out)
