"""
Average length of stay: Airbnb vs. U.S. hotels.

Method ("reported nights / consumer transactions"):
  avg nights per stay = reported nights booked / number of bookings (transactions)

Airbnb: the 10-K reports Nights & Experiences (Seats) Booked and, in the MD&A
"Geographic Mix" section, "average nights per booking, excluding experiences".
Implied bookings = nights / nights-per-booking. (Nights include experiences,
so implied bookings are slightly overstated - experiences are a small share.)

Hotels: U.S. room nights sold (STR/CoStar) / Kalibri Labs average length of stay
(check-in based). Implied stays = room nights / ALOS.

Swap in a card-panel transaction count (Consumer Edge / Second Measure / Earnest)
for `implied_bookings_mm` if the team obtains one - the chart code is unchanged.

Run:  python analysis/src/stay_length_airbnb_vs_hotels.py
Out:  docs/figures/stay_length_airbnb_vs_hotels.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ABNB = ROOT / "data/processed/airbnb_nights_per_booking.csv"
HOTEL = ROOT / "data/processed/hotel_avg_length_of_stay.csv"
OUT = ROOT / "docs/figures/stay_length_airbnb_vs_hotels.png"

# dataviz reference palette (light mode)
C_ABNB, C_HOTEL = "#2a78d6", "#eb6834"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"


def main() -> None:
    ab = pd.read_csv(ABNB)
    ho = pd.read_csv(HOTEL)

    g = ab[ab.region == "Global"].dropna(subset=["avg_nights_per_booking"])
    g = g.sort_values("year")

    # Hotel series: Kalibri ALOS, all U.S. hotels (pre-pandemic ~1.9, 2020+ ~2.1)
    hotel_years = {2019: 1.9, 2020: 2.1, 2021: 2.1, 2022: 2.1, 2023: 2.1, 2024: 2.1, 2025: 2.1}

    print("Airbnb (global, 10-K):")
    print(g[["year", "avg_nights_per_booking", "nights_booked_mm", "implied_bookings_mm"]].to_string(index=False))
    print("\nU.S. hotels (Kalibri ALOS):", hotel_years)
    print("\nRatio 2025: Airbnb / hotel =", round(g[g.year == 2025].avg_nights_per_booking.iloc[0] / 2.1, 2), "x")

    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)

    ax.plot(g.year, g.avg_nights_per_booking, color=C_ABNB, lw=2, marker="o", ms=6, label="Airbnb (global, 10-K)")
    hy = sorted(hotel_years)
    ax.plot(hy, [hotel_years[y] for y in hy], color=C_HOTEL, lw=2, marker="o", ms=6, label="U.S. hotels (Kalibri Labs ALOS)")

    # selective direct labels: first and last point of each series
    for x, y in [(g.year.iloc[0], g.avg_nights_per_booking.iloc[0]), (g.year.iloc[-1], g.avg_nights_per_booking.iloc[-1])]:
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", color=INK2, fontsize=9)
    for x in (hy[0], hy[-1]):
        ax.annotate(f"{hotel_years[x]:.1f}", (x, hotel_years[x]), textcoords="offset points", xytext=(0, -14), ha="center", color=INK2, fontsize=9)

    ax.set_ylim(0, 5)
    ax.set_xticks(hy)
    ax.set_ylabel("Avg nights per stay", color=INK2, fontsize=9)
    ax.set_title("Average length of stay: Airbnb runs ~1.8x U.S. hotels", loc="left", color=INK, fontsize=12, fontweight="bold")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.tick_params(colors=MUTED, labelsize=9)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.legend(frameon=False, fontsize=9, loc="upper right", labelcolor=INK2)
    fig.text(0.01, 0.01, "Sources: Airbnb 10-Ks FY2020-FY2025 (avg nights per booking, excl. experiences);\n"
             "Kalibri Labs via HotelBusiness / HotelsMag (U.S. hotel ALOS ~1.9 pre-2020, ~2.1 since; 2023-25 carried at 2.1).",
             color=MUTED, fontsize=7)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT, facecolor=SURF)
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
