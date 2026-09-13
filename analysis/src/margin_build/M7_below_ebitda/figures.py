"""M7 figures (py -3.13): interest-income rule vs actual, the 3Q26 EPS bridge, quarterly FCF backtest.
Writes analysis/figures/margin_build/M7_below_ebitda_{interest_income,eps_bridge_3q26,fcf_backtest}.png"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
OUT = REPO / "analysis" / "figures" / "margin_build"
OUT.mkdir(parents=True, exist_ok=True)
D = REPO / "data" / "processed" / "margin_build" / "M7_below_ebitda"
BLUE, RUST, GRAY, INK, MUTED, GRID = "#2563a8", "#c2410c", "#6b7280", "#1f2937", "#6b7280", "#e5e7eb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})


def style(ax, title, ylabel):
    ax.set_title(title, loc="left", color=INK, fontsize=10, pad=8)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def fig_interest_income():
    h = pd.read_csv(D / "M7_interest_income_fit_history.csv")
    h = h[h["quarter"] >= "2022Q1"]
    beta = float(pd.read_csv(D / "M7_parameter_sheet.csv").set_index("name").at["interest_income_beta", "value"])
    h["rule"] = beta * h["tbill_qmean"] / 100 * h["avg_base"] / 4
    live = pd.read_csv(D / "M7_live_waterfall_quarterly.csv")
    live = live[(live["scenario"].isin(["base", "rates_+100bp", "rates_-100bp"])) & (live["ebitda_source"] == live["ebitda_source"].iloc[0])]
    lb = live[live["scenario"] == "base"].set_index("quarter")["interest_income_musd"]
    lu = live[live["scenario"] == "rates_+100bp"].set_index("quarter")["interest_income_musd"]
    ld = live[live["scenario"] == "rates_-100bp"].set_index("quarter")["interest_income_musd"]
    qs = list(h["quarter"]) + list(lb.index[:6])
    x = np.arange(len(qs))
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    n = len(h)
    ax.plot(x[:n], h["interest_income"], color=BLUE, lw=2, marker="o", ms=4, label="Interest income, reported")
    ax.plot(x[:n], h["rule"], color=RUST, lw=2, ls="--", label=f"Rule: {beta:.2f} x 3m T-bill x avg(cash+STI+funds held)/4")
    ax.fill_between(x[n:], ld.values[:6], lu.values[:6], color=GRAY, alpha=0.18, lw=0, label="LIVE band, rates +/-100bp")
    ax.plot(x[n:], lb.values[:6], color=RUST, lw=2, ls="--")
    ax.axvline(n - 0.5, color=GRID, lw=1)
    ax.text(n - 0.3, ax.get_ylim()[1] * 0.97, "forecast", color=MUTED, va="top")
    ax.set_xticks(x); ax.set_xticklabels(qs, rotation=90)
    style(ax, "Interest income: the rate x balance rule fits to within ~$10M a quarter (2022Q1-2026Q2), then LIVE 3Q26-4Q27", "USD m per quarter")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "M7_below_ebitda_interest_income.png"); plt.close(fig)


def fig_eps_bridge():
    l = pd.read_csv(D / "M7_live_waterfall_quarterly.csv")
    r = l[(l["scenario"] == "base") & (l["quarter"] == "2026Q3") & (l["ebitda_source"] != "street") & (l["ebitda_source"] != "guide_implied")].iloc[0]
    steps = [("Adj. EBITDA", r["adj_ebitda_musd"]), ("D&A", -r["da_musd"]), ("SBC", -r["sbc_musd"]), ("Interest income", r["interest_income_musd"]),
             ("Interest expense", -r["interest_expense_musd"]), ("Other", r["other_income_musd"]), (f"Tax @ {r['tax_rate_pct']:.0f}%", -r["tax_provision_musd"])]
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    run = 0.0
    for i, (lab, v) in enumerate(steps):
        bottom = run if v >= 0 else run + v
        ax.bar(i, abs(v), bottom=bottom, color=BLUE if i == 0 else (GRAY if v >= 0 else RUST), width=0.6, edgecolor="white", linewidth=2)
        ax.text(i, run + v + (35 if v >= 0 else -35), f"{v:+,.0f}" if i else f"{v:,.0f}", ha="center", va="bottom" if v >= 0 else "top", color=INK, fontsize=8)
        run += v
    ax.bar(len(steps), run, color=BLUE, width=0.6, edgecolor="white", linewidth=2)
    ax.text(len(steps), run + 35, f"{run:,.0f}\n= ${r['eps_diluted']:.2f} / {r['diluted_shares_m']:.0f}M sh", ha="center", va="bottom", color=INK, fontsize=8)
    ax.set_xticks(range(len(steps) + 1)); ax.set_xticklabels([s[0] for s in steps] + ["Net income"], rotation=20, ha="right")
    style(ax, f"3Q26 EPS bridge on the {r['ebitda_source']} adj. EBITDA base: ${r['eps_diluted']:.2f} vs Street ${r['street_eps']:.2f} (LSEG, 11 Sep 2026)", "USD m")
    ax.set_ylim(0, r["adj_ebitda_musd"] * 1.15)
    fig.tight_layout(); fig.savefig(OUT / "M7_below_ebitda_eps_bridge_3q26.png"); plt.close(fig)


def fig_fcf_backtest():
    q = pd.read_csv(REPO / "data" / "processed" / "margin_build" / "10_harness_margin" / "scoreboard_by_quarter.csv")
    q = q[(q["method"] == "below-ebitda") & (q["target"] == "fcf_musd") & (q["window"] == "W1") & (q["horizon_q"] == 0) & (q["prior_basis"] == "PIT")]
    a = q[q["spec_id"] == "swing_x_gbv|rw"].set_index("quarter")
    b = q[q["spec_id"] == "swing_x_gbv_seasonal_other|rw"].set_index("quarter")
    qs = list(a.index); x = np.arange(len(qs))
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    ax.plot(x, a["actual"], color=INK, lw=2, marker="o", ms=4, label="FCF, reported")
    ax.plot(x, a["seasonal_naive_point"], color=GRAY, lw=1.5, ls=":", label="Seasonal naive (same quarter last year)")
    ax.plot(x, a["point"], color=RUST, lw=2, ls="--", label="M7 main: swing x GBV, trailing 'other' (h=0)")
    ax.plot(x, b["point"], color=BLUE, lw=2, ls="--", label="M7 variant: seasonal 'other' (h=0)")
    ax.set_xticks(x); ax.set_xticklabels(qs, rotation=90)
    style(ax, "Quarterly FCF at h=0, W1 (n 14): neither M7 spec beats the seasonal naive; the 'other' working-capital line is the swing", "USD m")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout(); fig.savefig(OUT / "M7_below_ebitda_fcf_backtest.png"); plt.close(fig)


if __name__ == "__main__":
    fig_interest_income(); fig_eps_bridge(); fig_fcf_backtest()
    print("figures written to", OUT)
