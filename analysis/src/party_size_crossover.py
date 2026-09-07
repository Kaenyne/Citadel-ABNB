"""
Party size: where hotels and Airbnb actually compete.

Hotel cost = rooms needed (2 people per room) x U.S. ADR $158.67 (CoStar/STR FY2024).
Airbnb cost = listing-weighted median nightly rate of entire homes whose `accommodates`
equals the party size (Inside Airbnb June-2026, 9 U.S. cities incl. LA), x 1.14 for the
guest service fee (Airbnb help centre: "typically under 14.2%"). Cleaning fees excluded
(they hurt Airbnb on 1-2 night stays - the small-party battleground).

Run:  python analysis/src/party_size_crossover.py
Out:  docs/figures/party_size_crossover.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data/processed/party_size_cost_crossover.csv"
FIG = ROOT / "docs/figures/party_size_crossover.png"
C_ABNB, C_HOTEL = "#2a78d6", "#eb6834"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"

# share of Airbnb booked runs by listing capacity (8-city calendar analysis)
RUN_SHARE = {"Private room": 12.6, "Entire, sleeps 1-2": 12.2, "Entire, sleeps 3-4": 22.8,
             "Entire, sleeps 5-6": 19.8, "Entire, sleeps 7+": 32.6}


def main():
    t = pd.read_csv(SRC)
    x = range(len(t))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160, gridspec_kw={"width_ratios": [5, 4]})
    fig.patch.set_facecolor(SURF)

    ax = axes[0]
    ax.set_facecolor(SURF)
    w = 0.38
    ax.bar([i - w / 2 for i in x], t.hotel_cost_night, w, color=C_HOTEL, label="Hotel rooms needed x $159 ADR")
    ax.bar([i + w / 2 for i in x], t.abnb_entire_incl_14pct_fee, w, color=C_ABNB, label="Airbnb entire home (median + 14% fee)")
    for i, r in t.iterrows():
        ax.text(i, max(r.hotel_cost_night, r.abnb_entire_incl_14pct_fee) + 12, f"{r.entire_vs_hotel_ratio:.2f}x",
                ha="center", color=INK2, fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(t.party_size.astype(str))
    ax.set_xlabel("Party size (people)", color=INK2, fontsize=9)
    ax.set_ylabel("$ per night", color=INK2, fontsize=9)
    ax.set_title("Airbnb is cheaper than hotels from 3 people up", loc="left", color=INK, fontsize=10.5, fontweight="bold", pad=10)
    ax.legend(frameon=False, fontsize=8, loc="upper left", labelcolor=INK2)

    ax = axes[1]
    ax.set_facecolor(SURF)
    labels, vals = list(RUN_SHARE), list(RUN_SHARE.values())
    colors = [MUTED, MUTED, C_ABNB, C_ABNB, C_ABNB]
    bars = ax.barh(labels, vals, color=colors, height=0.6)
    for b, v in zip(bars, vals):
        ax.text(v + 0.8, b.get_y() + b.get_height() / 2, f"{v:.0f}%", va="center", color=INK2, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 42)
    ax.set_xlabel("% of Airbnb booked stays (8 cities)", color=INK2, fontsize=9)
    ax.set_title("~75% of stays are in homes sleeping 3+", loc="left", color=INK, fontsize=10.5, fontweight="bold", pad=10)

    for ax in axes:
        ax.grid(axis="y" if ax is axes[0] else "x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=MUTED, labelsize=8.5)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color("#c3c2b7")
    fig.text(0.01, 0.01, "Sources: Inside Airbnb June-2026 (Austin, Chicago, Denver, LA, Nashville, New Orleans, SF, Seattle, DC) listing-weighted median rates;\n"
             "CoStar/STR FY2024 U.S. ADR $158.67; Airbnb guest fee ~14%. Hotel = 2 people/room. Cleaning fees and taxes excluded.",
             color=MUTED, fontsize=7)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, facecolor=SURF)
    print("wrote", FIG)


if __name__ == "__main__":
    main()
