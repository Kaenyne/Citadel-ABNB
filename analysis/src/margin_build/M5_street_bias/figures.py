"""M5 figures. Interpreter: py -3.13."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import TODAY  # noqa: E402

OUT = REPO / "data" / "processed" / "margin_build" / "M5_street_bias"
FIG = REPO / "analysis" / "figures" / "margin_build"
FIG.mkdir(parents=True, exist_ok=True)


def f1_bias():
    sp = pd.read_csv(OUT / "M5_surprise_panel.csv")
    sp = sp[(sp["horizon_q"] == 0) & sp["s_pt"].notna()].sort_values("quarter")
    d = pd.read_csv(OUT / "M5_parameters_by_vintage.csv")
    d = d[(d["horizon_q"] == 0) & (d["spec_id"] == "rw_hl4")].sort_values("vintage_date")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(sp["quarter"], sp["s_pt"], color="#7aa6c2", label="realised margin surprise (actual - Street), pt")
    ax.plot(d["vintage_date"].map(lambda x: str(x)[:4] + "Q" + str(((int(str(x)[5:7]) - 1) // 3) + 1)),
            d["b_pt"], "o-", color="#c0392b", lw=2,
            label="PIT shrunk recency-weighted bias b(vintage, h=0)")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("margin points")
    ax.set_title("ABNB: the Street's adjusted-EBITDA margin surprise and the point-in-time bias estimate\n"
                 "(h = 0, pre-guide LSEG mean vs the letter; pool from 2022Q1, half-life 4 q, shrunk)")
    ax.tick_params(axis="x", rotation=70, labelsize=8)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "M5_street_bias_surprise_and_bias.png", dpi=140)
    plt.close(fig)


def f2_scoreboard():
    t = pd.read_csv(OUT / "M5_backtest_vs_street.csv")
    t = t[(t["object"] != "street(raw baseline)") & (t["spec_id"] == "rw_hl4")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, tgt, lab in zip(axes, ["adj_ebitda_margin_pct", "adj_ebitda_musd"],
                            ["adj EBITDA margin (pt)", "adj EBITDA ($M)"]):
        s = t[t["target"] == tgt]
        labels, vals, cols = [], [], []
        for (win, h), gg in s.groupby(["window", "horizon_q"]):
            for r in gg.itertuples():
                labels.append(f"{r.object.replace('street_plus_', '+').replace('dispersion_conditioned', 'disp')}\n{win} h={h}")
                vals.append(r.mae_ratio_street)
                cols.append("#2e7d32" if r.mae_ratio_street < 1 else "#c0392b")
        ax.bar(range(len(vals)), vals, color=cols)
        ax.axhline(1.0, color="k", lw=1, ls="--")
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(labels, rotation=90, fontsize=6)
        ax.set_title(lab)
    axes[0].set_ylabel("MAE / raw-Street MAE  (<1 = better)")
    fig.suptitle("M5 street-bias: MAE relative to the raw Street baseline, spec rw_hl4, PIT replay", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "M5_street_bias_mae_ratio.png", dpi=140)
    plt.close(fig)


def f3_dispersion():
    sp = pd.read_csv(OUT / "M5_surprise_panel.csv")
    sp = sp[(sp["horizon_q"] == 0) & sp["s_pt"].notna()]
    d = pd.read_csv(OUT / "M5_parameters_by_vintage.csv")
    d = d[(d["horizon_q"] == 0) & (d["spec_id"] == "rw_hl4")][["vintage_date", "disp"]]
    m = sp.merge(d, left_on="vintage_date", right_on="vintage_date", how="inner")
    m = m[m["disp"].notna()]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    recent = m["quarter"] >= "2024Q1"
    ax.scatter(m.loc[~recent, "disp"], m.loc[~recent, "s_pt"], c="#9aa7b0", label="2021-23")
    ax.scatter(m.loc[recent, "disp"], m.loc[recent, "s_pt"], c="#1f4e79", label="2024Q1-2026Q2 (W2)")
    for r in m.itertuples():
        ax.annotate(r.quarter, (r.disp, r.s_pt), fontsize=6, alpha=0.7)
    x = m["disp"].to_numpy(float)
    y = m["s_pt"].to_numpy(float)
    b, a = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a + b * xs, "r-", lw=1.2, label=f"OLS slope {b:+.1f} pt per unit sd/mean (n={len(x)})")
    dl = pd.read_csv(OUT / "M5_parameters_by_vintage.csv")
    live = dl[(dl["vintage_date"].astype(str) == str(TODAY)) & (dl["horizon_q"] == 0) &
              (dl["spec_id"] == "rw_hl4")]
    if len(live):
        ax.axvline(float(live["disp"].iloc[0]), color="#c0392b", ls="--", lw=1,
                   label=f"3Q26 today: sd/mean {float(live['disp'].iloc[0]):.4f}")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("analyst dispersion at the vintage:  EBITDA sd / mean")
    ax.set_ylabel("realised margin surprise, pt")
    ax.set_title("Dispersion and the size of the beat (h = 0)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "M5_street_bias_dispersion.png", dpi=140)
    plt.close(fig)


def main():
    f1_bias()
    f2_scoreboard()
    f3_dispersion()
    print("figures ->", FIG)


if __name__ == "__main__":
    main()
