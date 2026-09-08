"""
Party size: where hotels and Airbnb actually compete.

Hotel cost = rooms needed (2 people per room) x U.S. ADR $158.67 (CoStar/STR FY2024).
Airbnb cost = listing-weighted average of city medians of the nightly rate for active
entire homes whose `accommodates` equals the party size, U.S. Inside Airbnb dumps.

PRICE BASIS - the thing this script got wrong until 7 Sep 2026
-------------------------------------------------------------
Inside Airbnb changed what `price` means. Through the Sep-2025 dumps it is the host's
listed nightly rate, which excludes the guest service fee, so the guest's price is
`price x 1.14` ("typically under 14.2%", Airbnb Help Centre 1857) and cleaning is excluded.
From the Mar-2026 dumps `price` IS `price_quote_price_per_night` - a real stay quote
divided by nights, already inclusive of the service fee and of cleaning amortised over
the stay. Verified here: in `austin_2026-06-22` the two columns are identical to floating
point across 10,321 entire homes.

The previous version of this script read the Jun-2026 dumps and multiplied by 1.14 anyway,
double-counting the guest fee and inflating every Airbnb price by exactly 14%. Every ratio
it published was 12.3% too high (= 1 - 1/1.14). This version detects the basis per dump and
applies the fee only on the listed basis.

A useful side effect: the quote basis is immune to the host-only fee migration
(`research/notes/host_only_fee_history_and_elasticity.md`). As hosts move to the single
15.5% fee they gross up their listed rate ~14.8% and the guest fee disappears, so the
LISTED series contains a 12-18% step that has nothing to do with pricing power - but the
QUOTED all-in price a guest pays is roughly unchanged, which is what this exhibit wants.
Mixing the two bases is what produced the contaminated ratios.

Run:  py -3.13 analysis/src/party_size_crossover.py
Out:  data/processed/party_size_cost_crossover.csv
      docs/figures/party_size_crossover.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DUMPS = ROOT / "data/raw/inside_airbnb"
OUT = ROOT / "data/processed/party_size_cost_crossover.csv"
FIG = ROOT / "docs/figures/party_size_crossover.png"

US_CITIES = ["austin", "chicago", "los-angeles", "nashville", "new-orleans", "new-york-city", "san-diego"]
HEADLINE_WINDOW = "2026-0"      # latest dump in the first half of 2026 (quote basis)
COMPARATOR_WINDOW = "2025-09"   # last full listed-basis dump before the price-basis change
HOTEL_ADR = 158.67              # CoStar/STR FY2024 U.S. ADR
ROOMS_NEEDED = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}
GUEST_FEE = 1.14                # applied ONLY on the listed basis

C_ABNB, C_HOTEL, C_OLD = "#2a78d6", "#eb6834", "#b9b7ad"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"

# share of Airbnb booked runs by listing capacity (8-city calendar analysis)
RUN_SHARE = {"Private room": 12.6, "Entire, sleeps 1-2": 12.2, "Entire, sleeps 3-4": 22.8,
             "Entire, sleeps 5-6": 19.8, "Entire, sleeps 7+": 32.6}


def latest_dump(city: str, window: str):
    hits = sorted(DUMPS.glob(f"{city}_{window}*_listings.parquet"))
    return hits[-1] if hits else None


def read_dump(path: Path) -> pd.DataFrame:
    """Return active entire homes with a numeric price and a flag for the price basis."""
    cols = pd.read_parquet(path).columns  # cheap: parquet keeps the schema in the footer
    want = ["price", "accommodates", "room_type", "number_of_reviews_ltm"]
    quote_basis = "price_quote_price_per_night" in cols
    d = pd.read_parquet(path, columns=[c for c in want if c in cols])
    d = d[d.room_type == "Entire home/apt"]
    if "number_of_reviews_ltm" in d.columns:
        d = d[d.number_of_reviews_ltm.fillna(0) >= 1]
    p = d["price"]
    if p.dtype == object:
        p = p.astype(str).str.replace(r"[\$,]", "", regex=True).replace("nan", np.nan).astype(float)
    d = d.assign(price_num=p).dropna(subset=["price_num"])
    d = d[(d.price_num > 10) & (d.price_num < 5000)]
    d["quote_basis"] = quote_basis
    return d


def city_medians(window: str) -> pd.DataFrame:
    """Listing-weighted average of city medians, per `accommodates`, plus the basis used."""
    rows = []
    for city in US_CITIES:
        path = latest_dump(city, window)
        if path is None:
            continue
        d = read_dump(path)
        d["acc"] = d.accommodates.clip(upper=8)
        for acc, grp in d.groupby("acc"):
            if acc < 1:
                continue
            rows.append({"city": city, "dump": path.name.split("_listings")[0],
                         "acc": int(acc), "median": grp.price_num.median(),
                         "n": len(grp), "quote_basis": bool(d.quote_basis.iloc[0])})
    t = pd.DataFrame(rows)
    agg = (t.assign(w=lambda x: x["median"] * x["n"])
             .groupby("acc").agg(listed_or_quote=("w", "sum"), n=("n", "sum"),
                                 quote_basis=("quote_basis", "first"), cities=("city", "nunique")))
    agg["listed_or_quote"] = agg.listed_or_quote / agg.n
    # the guest fee is already inside a stay quote; it is not inside a listed rate
    agg["guest_price"] = np.where(agg.quote_basis, agg.listed_or_quote, agg.listed_or_quote * GUEST_FEE)
    return agg


def main():
    now = city_medians(HEADLINE_WINDOW)
    then = city_medians(COMPARATOR_WINDOW)

    t = pd.DataFrame({"party_size": now.index})
    t["hotel_rooms_needed"] = t.party_size.map(ROOMS_NEEDED)
    t["hotel_cost_night"] = (t.hotel_rooms_needed * HOTEL_ADR).round(0)
    t["price_basis"] = np.where(now.quote_basis.values, "stay quote (fee + cleaning incl.)", "listed rate")
    t["abnb_quoted_night"] = now.listed_or_quote.round(0).values
    t["abnb_guest_price_night"] = now.guest_price.round(0).values
    t["entire_vs_hotel_ratio"] = (now.guest_price.values / t.hotel_cost_night).round(2)
    # what the previous version published, for the correction record
    t["superseded_ratio_double_counted_fee"] = (now.guest_price.values * GUEST_FEE / t.hotel_cost_night).round(2)
    t["n_entire_listings"] = now.n.values
    t["n_cities"] = now.cities.values
    # listed-basis comparator: NOT comparable (different year, cleaning excluded)
    t["comparator_2025_listed_night"] = [round(then.listed_or_quote.get(a, np.nan), 0) for a in t.party_size]
    t["comparator_2025_ratio_not_comparable"] = [
        round(then.guest_price.get(a, np.nan) / h, 2) for a, h in zip(t.party_size, t.hotel_cost_night)]
    t["hotel_per_person"] = (t.hotel_cost_night / t.party_size).round(0)
    t["abnb_per_person"] = (now.guest_price.values / t.party_size).round(0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT, index=False)
    print(t[["party_size", "hotel_cost_night", "abnb_guest_price_night", "entire_vs_hotel_ratio",
             "superseded_ratio_double_counted_fee", "n_entire_listings"]].to_string(index=False))

    seg_map = {"solo": [1], "pair": [2], "3-4": [3, 4], "5+": [5, 6, 7, 8]}
    print("\nSegment ratios for PRICE_RATIO_2025 (listing-weighted within segment):")
    for seg, accs in seg_map.items():
        sub = t[t.party_size.isin(accs)]
        w = sub.n_entire_listings
        abnb = (sub.abnb_guest_price_night * w).sum() / w.sum()
        hotel = (sub.hotel_cost_night * w).sum() / w.sum()
        print(f"  {seg:5} {abnb / hotel:.2f}   (was {abnb * GUEST_FEE / hotel:.2f})")

    # ------------------------------------------------------------------ figure
    x = range(len(t))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160, gridspec_kw={"width_ratios": [5, 4]})
    fig.patch.set_facecolor(SURF)

    ax = axes[0]
    ax.set_facecolor(SURF)
    w = 0.38
    ax.bar([i - w / 2 for i in x], t.hotel_cost_night, w, color=C_HOTEL, label=f"Hotel rooms needed x ${HOTEL_ADR:.0f} ADR")
    ax.bar([i + w / 2 for i in x], t.abnb_guest_price_night, w, color=C_ABNB, label="Airbnb entire home, price a guest is quoted")
    ax.bar([i + w / 2 for i in x], t.abnb_guest_price_night * (GUEST_FEE - 1), w,
           bottom=t.abnb_guest_price_night, color=C_OLD, hatch="///", edgecolor="white", linewidth=0,
           label="superseded: fee counted twice")
    for i, r in t.iterrows():
        ax.text(i, max(r.hotel_cost_night, r.abnb_guest_price_night * GUEST_FEE) + 12,
                f"{r.entire_vs_hotel_ratio:.2f}x", ha="center", color=INK2, fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(t.party_size.astype(str))
    ax.set_xlabel("Party size (people)", color=INK2, fontsize=9)
    ax.set_ylabel("$ per night", color=INK2, fontsize=9)
    ax.set_title("Airbnb undercuts hotels at every party size except couples", loc="left", color=INK, fontsize=10.5, fontweight="bold", pad=10)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left", labelcolor=INK2)

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
    fig.text(0.01, 0.01,
             f"Sources: Inside Airbnb {HEADLINE_WINDOW.rstrip('-0')} dumps, {t.n_cities.iloc[0]} U.S. cities, active entire homes; `price` on these dumps is a stay quote already\n"
             f"inclusive of the guest service fee and amortised cleaning, so no fee is added. CoStar/STR FY2024 U.S. ADR ${HOTEL_ADR:.2f}; hotel = 2 people/room.\n"
             "Hotel taxes and resort fees excluded on the hotel side; hotel ADR is a FY2024 vintage against 2026 Airbnb prices (both open items).",
             color=MUTED, fontsize=6.5)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, facecolor=SURF)
    print("\nwrote", OUT)
    print("wrote", FIG)


if __name__ == "__main__":
    main()
