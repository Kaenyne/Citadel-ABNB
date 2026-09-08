"""
Kitchen / whole-home effect on Airbnb stay length (Inside Airbnb).

Stay-length proxy: a "booked run" = a contiguous block of nights marked
unavailable (available == 'f') in Inside Airbnb calendar.csv.gz, capped at 30
nights to strip host blocks. Runs are booking-weighted, so mean run length is
the same construct as Airbnb's "nights per booking" (nights / bookings).
Level is biased UP (host blocks look like bookings); use the DIFFERENCES between
segments, not the level.

Segments: room_type x kitchen amenity; bedrooms; accommodates (entire homes only).
Only listings active in the last 12 months (number_of_reviews_ltm > 0).

Two modes:
  1) --raw  <city>=<dir> ...  : recompute from Inside Airbnb listings.csv.gz + calendar.csv.gz
                                (data/raw is gitignored - keep the gz files there)
  2) default                  : read data/processed/insideairbnb_booked_run_length_by_segment.csv
                                (aggregates computed 2026-09-06 from the June-2026 scrapes of
                                 Austin, Chicago, Denver, Nashville, New Orleans, SF, Seattle, DC)
Both modes write the pooled table and the chart.

Run:  python analysis/src/kitchen_wholehome_stay_length.py
      python analysis/src/kitchen_wholehome_stay_length.py --raw austin=data/raw/austin chicago=data/raw/chicago
Out:  data/processed/kitchen_wholehome_pooled.csv, docs/figures/kitchen_wholehome_stay_length.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SEG_CSV = ROOT / "data/processed/insideairbnb_booked_run_length_by_segment.csv"
POOL_CSV = ROOT / "data/processed/kitchen_wholehome_pooled.csv"
FIG = ROOT / "docs/figures/kitchen_wholehome_stay_length.png"
CAP = 30

C1, C2, INK, INK2, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"


def runs_from_calendar(cal_path: Path) -> dict:
    """listing_id -> list of contiguous unavailable-run lengths (nights)."""
    cal = pd.read_csv(cal_path, usecols=["listing_id", "date", "available"])
    cal = cal.sort_values(["listing_id", "date"])
    cal["unav"] = (cal.available == "f").astype(int)
    grp = cal.groupby("listing_id")["unav"]
    # new run starts when unav flips or listing changes
    cal["run_id"] = (cal.unav.ne(grp.shift())).cumsum()
    runs = cal[cal.unav == 1].groupby(["listing_id", "run_id"]).size().reset_index(name="len")
    return runs.groupby("listing_id")["len"].apply(list).to_dict()


def segments_for_city(city: str, d: Path) -> pd.DataFrame:
    lst = pd.read_csv(d / "listings.csv.gz", usecols=["id", "room_type", "accommodates", "bedrooms",
                                                        "amenities", "number_of_reviews_ltm"])
    lst["kitchen"] = lst.amenities.fillna("").str.lower().str.contains("kitchen")
    lst = lst[lst.number_of_reviews_ltm > 0]
    runs = runs_from_calendar(d / "calendar.csv.gz")
    rows = []
    for r in lst.itertuples():
        rr = [x for x in runs.get(r.id, []) if x <= CAP]
        if not rr:
            continue
        entire = r.room_type == "Entire home/apt"
        segs = ["ALL", ("Entire" if entire else "Room") + "|" + ("K" if r.kitchen else "noK")]
        if entire:
            b = r.bedrooms if pd.notna(r.bedrooms) else 0
            segs.append("bed" + ("4+" if b >= 4 else str(int(b))))
            a = r.accommodates
            segs.append("acc" + ("1-2" if a <= 2 else "3-4" if a <= 4 else "5-6" if a <= 6 else "7+"))
        for s in segs:
            rows += [(s, x) for x in rr]
    df = pd.DataFrame(rows, columns=["segment", "len"])
    out = df.groupby("segment")["len"].agg(runs="size", mean="mean", median="median",
                                           share_ge7=lambda x: (x >= 7).mean(),
                                           share_ge3=lambda x: (x >= 3).mean()).reset_index()
    out.insert(0, "city", city)
    return out


def pooled(seg_df: pd.DataFrame) -> pd.DataFrame:
    w = seg_df.runs
    g = seg_df.assign(m=seg_df["mean"] * w, s7=seg_df.share_ge7 * w, s3=seg_df.share_ge3 * w).groupby("segment")
    out = g[["runs", "m", "s7", "s3"]].sum()
    out["mean_nights_per_booked_run"] = out.m / out.runs
    out["share_ge7"] = out.s7 / out.runs
    out["share_ge3"] = out.s3 / out.runs
    return out[["runs", "mean_nights_per_booked_run", "share_ge7", "share_ge3"]].round(3)


def chart(pool: pd.DataFrame) -> None:
    left = [("Room, no kitchen", "Room|noK"), ("Room + kitchen", "Room|K"),
            ("Entire home, no kitchen", "Entire|noK"), ("Entire home + kitchen", "Entire|K")]
    right = [("Studio", "bed0"), ("1 bed", "bed1"), ("2 bed", "bed2"), ("3 bed", "bed3"), ("4+ bed", "bed4+")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160, gridspec_kw={"width_ratios": [4, 5]})
    fig.patch.set_facecolor(SURF)
    for ax, items, color, title in [(axes[0], left, C1, "Kitchen + whole home: +1.2-1.5 nights"),
                                    (axes[1], right, C2, "Bigger homes book shorter stays")]:
        ax.set_facecolor(SURF)
        labels = [l for l, _ in items]
        vals = [pool.loc[k, "mean_nights_per_booked_run"] for _, k in items]
        bars = ax.bar(labels, vals, color=color, width=0.62)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.1f}", ha="center", va="bottom", color=INK2, fontsize=9)
        ax.set_ylim(0, 6.5)
        ax.set_title(title, loc="left", color=INK, fontsize=10.5, fontweight="bold", pad=10)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=MUTED, labelsize=8.5)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color("#c3c2b7")
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    axes[0].set_ylabel("Mean nights per booked run", color=INK2, fontsize=9)
    fig.text(0.01, 0.01, "Inside Airbnb June-2026 scrapes, 8 U.S. cities (Austin, Chicago, Denver, Nashville, New Orleans, SF, Seattle, DC), "
             "273k booked runs <=30 nights,\nactive listings only. Right panel = entire homes. Levels biased up by host blocks; read the differences.",
             color=MUTED, fontsize=7)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, facecolor=SURF)


def main(argv):
    if len(argv) > 1 and argv[1] == "--raw":
        parts = [segments_for_city(a.split("=", 1)[0], Path(a.split("=", 1)[1])) for a in argv[2:]]
        seg = pd.concat(parts, ignore_index=True)
        seg.to_csv(SEG_CSV, index=False)
    else:
        seg = pd.read_csv(SEG_CSV)
    pool = pooled(seg)
    pool.to_csv(POOL_CSV)
    print(pool)
    e, r = pool.loc["Entire|K", "mean_nights_per_booked_run"], pool.loc["Room|noK", "mean_nights_per_booked_run"]
    print(f"\nEntire+kitchen vs room w/o kitchen: +{e - r:.2f} nights ({(e / r - 1) * 100:.0f}%)")
    print(f"Room kitchen effect: +{pool.loc['Room|K', 'mean_nights_per_booked_run'] - r:.2f} nights")
    print(f"1-bed vs 4+ bed: {pool.loc['bed1', 'mean_nights_per_booked_run'] - pool.loc['bed4+', 'mean_nights_per_booked_run']:+.2f} nights")
    chart(pool)
    print("wrote", FIG)


if __name__ == "__main__":
    main(sys.argv)
