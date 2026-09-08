"""
Party size (people per stay) on Airbnb: triangulated distribution.

Airbnb does not publish guests per booking. Three independent anchors pin it:
  1) MEAN  = cumulative guest arrivals / cumulative bookings (10-K / S-1 / newsroom milestones,
             bookings = nights booked / nights-per-booking)            -> ~2.9-3.0 guests per stay
  2) SOLO  = "more than 80% of bookings are group trips" (Airbnb 2024 Summer Release) -> P(1) < 20%;
             "almost a quarter of nights ... guests traveling on their own" (2022) -> solo nights 24%
  3) SHAPE = Hawaii DBEDT 2024 visitor survey: party-size buckets (1 / 2 / 3+) for rental-house-only
             vs hotel-only visitors; Inside Airbnb capacity of booked listings (upper bound on party)

Distribution = maximum-entropy fit: P(1) fixed at the solo anchor, remaining mass follows a
shifted geometric over 2..8+ chosen so the mean hits the guest-arrivals anchor. Sensitivity
band = mean 2.7-3.1, solo 13-19%.

Run:  python analysis/src/party_size_distribution.py
Out:  data/processed/airbnb_party_size_distribution.csv, docs/figures/party_size_distribution.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "data/processed/airbnb_party_size_distribution.csv"
FIG = ROOT / "docs/figures/party_size_distribution.png"
C1, C2, INK, INK2, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"

# ---- Anchor 1: guest arrivals / bookings -------------------------------------------------
# cumulative guest-arrival milestones (Airbnb newsroom / S-1 / 10-K)
MILESTONES = {  # date -> cumulative guest arrivals (millions)
    "2018-08-26": 400, "2019-03-27": 500, "2020-09-30": 825, "2021-10-15": 1000,
    "2024-10-15": 2000, "2025-12-31": 2500,
}
# annual bookings (millions) = nights & experiences booked / avg nights per booking (10-K)
NIGHTS = {2017: 185.8, 2018: 250.3, 2019: 326.9, 2020: 193.2, 2021: 300.6, 2022: 394.0,
          2023: 448.0, 2024: 491.5, 2025: 533.0}
NPB = {2017: 3.8, 2018: 3.8, 2019: 3.8, 2020: 4.1, 2021: 4.1, 2022: 4.1, 2023: 3.9, 2024: 3.8, 2025: 3.7}
# 2017-2019 nights-per-booking not disclosed; 3.8 = U.S. panel 2019 mean (arXiv 2507.21298) / 10-K 2024 level


def bookings_between(d0: str, d1: str) -> float:
    """Bookings (mm) between two dates, spreading each year's bookings evenly across the year."""
    t0, t1 = pd.Timestamp(d0), pd.Timestamp(d1)
    total = 0.0
    for y, n in NIGHTS.items():
        ys, ye = pd.Timestamp(f"{y}-01-01"), pd.Timestamp(f"{y}-12-31")
        lo, hi = max(t0, ys), min(t1, ye)
        if hi > lo:
            total += (n / NPB[y]) * ((hi - lo).days / 365.0)
    return total


def anchor_mean() -> pd.DataFrame:
    keys = list(MILESTONES)
    rows = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            d0, d1 = keys[i], keys[j]
            arr = MILESTONES[d1] - MILESTONES[d0]
            bk = bookings_between(d0, d1)
            rows.append({"window": f"{d0} -> {d1}", "guest_arrivals_mm": arr, "bookings_mm": round(bk, 1),
                         "guests_per_booking": round(arr / bk, 2), "years": round((pd.Timestamp(d1) - pd.Timestamp(d0)).days / 365, 1)})
    return pd.DataFrame(rows)


# ---- Fit --------------------------------------------------------------------------------
SIZES = [1, 2, 3, 4, 5, 6, 7, 8]  # 8 = "8+"
TAIL_EXTRA = 1.5  # mean of the 8+ bucket is ~8 + this (geometric tail)


def maxent(p1: float, mean: float) -> np.ndarray:
    """P(1)=p1; sizes>=2 follow a shifted geometric with success prob q so the overall mean = `mean`."""
    cond_mean = (mean - p1) / (1 - p1)          # mean of party size given >= 2
    q = 1 / (cond_mean - 1)                     # shifted geometric on {2,3,...}: mean = 2 + (1-q)/q
    p = np.array([p1] + [(1 - p1) * q * (1 - q) ** (k - 2) for k in range(2, 8)])
    p = np.append(p, 1 - p.sum())               # 8+ = remaining mass
    return p


def main():
    am = anchor_mean()
    print(am.to_string(index=False))
    long = am[am.years >= 2.5]
    mean_c = round(float(np.average(long.guests_per_booking, weights=long.guest_arrivals_mm)), 2)
    print(f"\nLong-window weighted mean guests/booking: {mean_c}")

    central = maxent(0.16, mean_c)
    lo = maxent(0.19, 2.7)
    hi = maxent(0.13, 3.1)
    df = pd.DataFrame({"party_size": ["1", "2", "3", "4", "5", "6", "7", "8+"],
                       "airbnb_central": central.round(3), "airbnb_low": lo.round(3), "airbnb_high": hi.round(3)})
    # Hawaii DBEDT 2024: visitors by party bucket -> parties (visitors / size; 3+ size solved from avg party size)
    hi_rows = {"Rental house-only": (88969, 227102, 441830, 2.49, 9.46), "Hotel-only": (614076, 1815690, 2482500, 2.30, 7.31),
               "Condo-only": (100712, 404208, 576768, 2.44, 10.23)}
    hw = []
    for k, (one, two, three, avg, los) in hi_rows.items():
        parties = (one + two + three) / avg
        p1, p2 = one / parties, (two / 2) / parties
        hw.append({"segment": k, "share_1": round(p1, 3), "share_2": round(p2, 3), "share_3plus": round(1 - p1 - p2, 3),
                   "avg_party": avg, "avg_3plus_party": round(three / (parties - one - two / 2), 2), "los_days": los})
    hw = pd.DataFrame(hw)
    print("\n", hw.to_string(index=False))
    print("\nAirbnb central:", dict(zip(df.party_size, df.airbnb_central)))
    print("P(>=3) =", round(central[2:].sum(), 3), " P(>=5) =", round(central[4:].sum(), 3), " implied mean =",
          round(float(np.dot(central, [1, 2, 3, 4, 5, 6, 7, 8 + TAIL_EXTRA])), 2))
    df.to_csv(OUT_CSV, index=False)
    am.to_csv(ROOT / "data/processed/airbnb_guests_per_booking_windows.csv", index=False)
    hw.to_csv(ROOT / "data/processed/hawaii_party_size_by_accommodation_2024.csv", index=False)

    # ---- chart ---------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), dpi=160, gridspec_kw={"width_ratios": [5, 4]})
    fig.patch.set_facecolor(SURF)
    ax = axes[0]
    ax.set_facecolor(SURF)
    x = np.arange(len(SIZES))
    ax.bar(x, central * 100, color=C1, width=0.62)
    ax.errorbar(x, central * 100, yerr=[np.maximum(central - np.minimum(lo, hi), 0) * 100,
                                        np.maximum(np.maximum(lo, hi) - central, 0) * 100],
                fmt="none", ecolor=INK2, elinewidth=1, capsize=3)
    for i, v in enumerate(central):
        ax.text(i, v * 100 + 2.6, f"{v * 100:.0f}%", ha="center", color=INK2, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(df.party_size)
    ax.set_xlabel("People per stay", color=INK2, fontsize=9)
    ax.set_ylabel("% of Airbnb bookings", color=INK2, fontsize=9)
    ax.set_ylim(0, 45)
    ax.set_title(f"Airbnb party size: mean ~{mean_c}, 84% are groups", loc="left", color=INK, fontsize=10.5, fontweight="bold", pad=10)

    ax = axes[1]
    ax.set_facecolor(SURF)
    cats = ["1", "2", "3+"]
    a = [central[0], central[1], central[2:].sum()]
    r = hw.set_index("segment").loc["Rental house-only", ["share_1", "share_2", "share_3plus"]].values
    h = hw.set_index("segment").loc["Hotel-only", ["share_1", "share_2", "share_3plus"]].values
    w = 0.26
    xx = np.arange(3)
    ax.bar(xx - w, np.array(a) * 100, w, color=C1, label="Airbnb (fitted, global)")
    ax.bar(xx, r * 100, w, color=C2, label="Hawaii rental-house visitors")
    ax.bar(xx + w, h * 100, w, color=MUTED, label="Hawaii hotel visitors")
    ax.set_xticks(xx)
    ax.set_xticklabels(cats)
    ax.set_xlabel("People in party", color=INK2, fontsize=9)
    ax.set_ylim(0, 60)
    ax.set_title("Rental parties skew bigger than hotel parties", loc="left", color=INK, fontsize=10.5, fontweight="bold", pad=10)
    ax.legend(frameon=False, fontsize=8, loc="upper left", labelcolor=INK2)
    for ax in axes:
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=MUTED, labelsize=8.5)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color("#c3c2b7")
    fig.text(0.01, 0.01, "Left: max-entropy fit to Airbnb anchors (guest arrivals / bookings = 2.9-3.0 per stay; >80% of bookings are group trips). "
             "Whiskers = mean 2.7-3.1, solo 13-19%.\nRight: Hawaii DBEDT 2024 Annual Visitor Research Report, Tables 43 & 46 "
             "(parties = visitors / party size). Sources in research/notes/party_size_distribution.md.",
             color=MUTED, fontsize=7)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, facecolor=SURF)
    print("wrote", FIG)


if __name__ == "__main__":
    main()
