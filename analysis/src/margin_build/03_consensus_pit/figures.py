"""WS03 figures (run with `py -3.13`, which has matplotlib). Reads the processed outputs plus the
licensed daily derived path in data/raw (only an index and margin ratios are drawn)."""
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
OUT = REPO / "data" / "processed" / "margin_build" / "03_consensus_pit"
RAW = REPO / "data" / "raw" / "margin_build" / "03_consensus_pit"
FIG = REPO / "analysis" / "figures" / "margin_build"
FIG.mkdir(parents=True, exist_ok=True)

INK, MUTED, GRID = "#1f2430", "#6b7280", "#e5e7eb"
C_MAIN, C_ALT, C_W2, C_ACT = "#2563eb", "#9ca3af", "#f59e0b", "#111827"


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK, labelsize=9)


def fig_margin_surprise():
    s = pd.read_csv(OUT / "03_surprise_history.csv")
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, gridspec_kw={"height_ratios": [1, 1.2]})
    ax = axes[0]
    x = np.arange(len(s))
    cols = [C_W2 if w2 else (C_MAIN if w1 else C_ALT) for w1, w2 in zip(s["in_W1"], s["in_W2"])]
    ax.bar(x, s["margin_surprise_pts"], color=cols, width=0.7)
    ax.axhline(0, color=INK, lw=0.8)
    for i, v in enumerate(s["margin_surprise_pts"]):
        ax.text(i, v + (0.6 if v >= 0 else -1.6), f"{v:+.1f}", ha="center", fontsize=7.5, color=INK)
    ax.set_ylabel("Adj. EBITDA margin surprise, pts\n(actual minus LSEG Street at print)", fontsize=9)
    ax.set_title("ABNB: the Street has under-called the margin at 21 of 22 prints; the beat shrank to under 1 pt in 2025-26",
                 fontsize=11, color=INK, loc="left")
    w1 = s[s.in_W1]["margin_surprise_pts"]; w2 = s[s.in_W2]["margin_surprise_pts"]
    ax.text(0.99, 0.95, f"W1 1Q23-2Q26 (n={len(w1)}): mean {w1.mean():+.2f}, sd {w1.std():.2f}\n"
                        f"W2 1Q24-2Q26 (n={len(w2)}): mean {w2.mean():+.2f}, sd {w2.std():.2f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color=INK,
            bbox=dict(boxstyle="round", fc="white", ec=GRID))
    ax.set_ylim(min(-3, s["margin_surprise_pts"].min() - 3), s["margin_surprise_pts"].max() + 6)
    style(ax)
    ax = axes[1]
    ax.plot(x, s["actual_margin_pct"], color=C_ACT, lw=1.8, marker="o", ms=3.5, label="Actual adj. EBITDA margin")
    ax.plot(x, s["street_margin_pct"], color=C_MAIN, lw=1.4, marker="s", ms=3, ls="--", label="LSEG Street at print (mean EBITDA / mean revenue)")
    g = s.dropna(subset=["guide_implied_margin_pct"])
    ax.scatter(g.index, g["guide_implied_margin_pct"], color=C_W2, marker="_", s=180, lw=2, label="Guide-implied margin (letter, floor/ceiling/point)", zorder=5)
    ax.set_xticks(x); ax.set_xticklabels(s["print_quarter"].str.replace("20", "", regex=False), rotation=0, fontsize=8)
    ax.set_ylabel("Margin, %", fontsize=9)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    style(ax)
    fig.text(0.01, 0.005, "Source: LSEG Workspace TR.EBITDAMean / TR.RevenueMean stamped one trading day before each print (WS03, pulled 13 Sep 2026); "
                          "actuals from shareholder letters (abnb_quarterly_cost_stack_exsbc.csv);
guide-implied from 02_guidance_ledger.csv. "
                          "Bars: grey = 2021-22, blue = W1 only, amber = W1 and W2.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(FIG / "03_consensus_pit_margin_surprise.png", dpi=160)
    plt.close(fig)


def fig_revision_paths():
    d = pd.read_csv(RAW / "derived_daily_revision_paths_LICENSED.csv", parse_dates=["calcdate"])
    q = d[d["path"] == "quarter"].copy()
    q = q[q["target_period"] >= "2023Q1"]
    fig, ax = plt.subplots(figsize=(11, 6))
    for tp, g in q.groupby("target_period"):
        g = g.sort_values("calcdate").reset_index(drop=True)
        col = C_W2 if tp >= "2024Q1" else C_MAIN
        if tp == "2026Q3":
            col = C_ACT
        ax.plot(np.arange(len(g)), g["ebitda_index"], color=col, lw=2.2 if tp == "2026Q3" else 1.1, alpha=0.95 if tp == "2026Q3" else 0.75)
        ax.text(len(g) - 1 + 0.6, g["ebitda_index"].iloc[-1], tp, fontsize=7.5, color=col, va="center")
    ax.axhline(100, color=INK, lw=0.8)
    ax.set_xlabel("Trading days since the guide (day 0 = last close before the letter)", fontsize=9)
    ax.set_ylabel("LSEG consensus adj. EBITDA for the guided quarter, index (pre-guide = 100)", fontsize=9)
    ax.set_title("Consensus EBITDA for the guided quarter: the guide sets the level in the first week; the drift to the print is small (median +0.1%)",
                 fontsize=11, color=INK, loc="left")
    ax.text(0.01, 0.96, "blue = targets 1Q23-4Q23; amber = 1Q24-2Q26 (W2); black = 3Q26 (live, to 11 Sep 2026)",
            transform=ax.transAxes, ha="left", va="top", fontsize=8, color=MUTED)
    style(ax)
    fig.text(0.01, 0.005, "Source: LSEG Workspace TR.EBITDAMean daily, period FQ1/FQ2 resolved by .fperiod (WS03 pull 13 Sep 2026). Index only; levels stay in data/raw.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(FIG / "03_consensus_pit_revision_paths.png", dpi=160)
    plt.close(fig)


def fig_fy_floor():
    d = pd.read_csv(RAW / "derived_daily_revision_paths_LICENSED.csv", parse_dates=["calcdate"])
    f = d[(d["path"] == "fy") & (d["target_period"].isin(["FY2024", "FY2025", "FY2026"]))].copy()
    f["margin"] = 100 * f["ebitdamean"] / f["revenuemean"]
    floors = {"FY2024": [("2024-02-13", 35.0), ("2024-11-07", 35.5)],
              "FY2025": [("2025-02-13", 34.5), ("2025-11-06", 35.0)],
              "FY2026": [("2026-02-12", 35.1), ("2026-05-07", 35.0), ("2026-08-06", 35.5)]}
    actual = {"FY2024": 36.4, "FY2025": 35.1}
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6), sharey=True)
    for ax, fy in zip(axes, ["FY2024", "FY2025", "FY2026"]):
        g = f[f.target_period == fy].sort_values("calcdate")
        ax.plot(g["calcdate"], g["margin"], color=C_MAIN, lw=1.6, label="LSEG consensus FY margin (mean/mean)")
        fl = floors[fy]
        for i, (dt_, v) in enumerate(fl):
            x0 = pd.Timestamp(dt_)
            x1 = pd.Timestamp(fl[i + 1][0]) if i + 1 < len(fl) else g["calcdate"].max()
            ax.hlines(v, x0, x1, color=C_W2, lw=2.2, label="Management FY floor / point" if i == 0 else None)
        if fy in actual:
            ax.axhline(actual[fy], color=C_ACT, lw=1.0, ls=":", label=f"Actual {actual[fy]:.1f}%")
        ax.set_title(fy, fontsize=10, color=INK)
        ax.tick_params(axis="x", rotation=30)
        style(ax)
        if fy == "FY2024":
            ax.legend(fontsize=7.5, frameon=False, loc="lower left")
    axes[0].set_ylabel("Adj. EBITDA margin, %", fontsize=9)
    fig.suptitle("The Street sits on the FY floor: consensus FY margin lands within 0.5 pt of the guided floor after 8 of 10 floor guides",
                 fontsize=11, color=INK, x=0.01, ha="left")
    fig.text(0.01, 0.005, "Source: LSEG TR.EBITDAMean / TR.RevenueMean FY1..FY3 daily resolved to the fiscal year (WS03); floors from 02_guidance_ledger.csv "
                          "(FY26 2/12 'stable y/y' drawn at the FY25 actual 35.1%). Actual FY margins from letters.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(FIG / "03_consensus_pit_fy_floor.png", dpi=160)
    plt.close(fig)


def main() -> int:
    fig_margin_surprise()
    fig_revision_paths()
    fig_fy_floor()
    print("figures ->", FIG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
