"""Forward bookings by listing size, from Inside Airbnb calendar files.

Why: reviews count past bookings. The calendar shows the next 365 nights per listing as available (t)
or not (f). "Not available" = booked OR host-blocked, so the level is contaminated; the DIFFERENCE
between near-term unavailability (next 30 nights) and far-term unavailability (nights 181-365) is
mostly bookings, because host blocks are roughly flat across the horizon while bookings pile up near
the check-in date. That "pickup" is the closest thing to actual forward bookings in public data.

Per market x accommodates bucket, entire homes only:
  unavail_30   share of the next 30 nights marked unavailable
  unavail_90   same for next 90
  unavail_far  same for nights 181-365 (host-block baseline)
  pickup_30    unavail_30 - unavail_far     (forward-booking proxy)
  share of forward booked guest-nights = sum(pickup nights x accommodates) share by bucket vs listing share

Inputs  data/raw/insideairbnb/<mkt>_calendar.csv.gz + <mkt>_listings.csv.gz (gitignored)
Outputs data/processed/abnb_forward_bookings_by_size.csv, abnb_forward_bookings_pooled.csv,
        analysis/figures/14_forward_bookings_by_size.png
Run from repo root: python analysis/src/calendar_forward_bookings_by_size.py
"""
import glob, os
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/insideairbnb"; P = ROOT / "data/processed"; F = ROOT / "analysis/figures"
BINS = [0, 2, 4, 6, 99]; LABELS = ["1-2 guests", "3-4 guests", "5-6 guests", "7+ guests"]
S1, S2, GRID, INK2, MUTED, SURF = "#2a78d6", "#eb6834", "#e1e0d9", "#52514e", "#898781", "#fcfcfb"

rows = []
for cal in sorted(glob.glob(str(RAW / "*_calendar.csv.gz"))):
    m = os.path.basename(cal).replace("_calendar.csv.gz", "")
    lst = RAW / f"{m}_listings.csv.gz"
    if not lst.exists():
        continue
    L = pd.read_csv(lst, usecols=["id", "room_type", "accommodates", "number_of_reviews", "last_review", "last_scraped"], low_memory=False)
    L = L[(L.room_type == "Entire home/apt") & L.accommodates.between(1, 16)]
    snap = pd.to_datetime(L.last_scraped, errors="coerce").max()
    C = pd.read_csv(cal, usecols=["listing_id", "date", "available"])
    C = C[C.listing_id.isin(L.id)]
    C["d"] = (pd.to_datetime(C.date) - snap).dt.days
    C["unavail"] = (C.available == "f").astype(int)
    C = C[C.d.between(0, 365)]
    near = C[C.d < 30].groupby("listing_id").unavail.mean().rename("unavail_30")
    n90 = C[C.d < 90].groupby("listing_id").unavail.mean().rename("unavail_90")
    far = C[C.d.between(181, 365)].groupby("listing_id").unavail.mean().rename("unavail_far")
    D = L.set_index("id")[["accommodates", "number_of_reviews", "last_review"]].join([near, n90, far], how="inner").dropna()
    # active: at least one review in the last 12 months (drop dead listings whose calendars are all-blocked)
    D = D[pd.to_datetime(D.last_review, errors="coerce") >= snap - pd.Timedelta(days=365)]
    D["pickup_30"] = (D.unavail_30 - D.unavail_far).clip(lower=0)
    D["pickup_90"] = (D.unavail_90 - D.unavail_far).clip(lower=0)
    D["bucket"] = pd.cut(D.accommodates, BINS, labels=LABELS)
    g = D.groupby("bucket", observed=False)
    t = pd.DataFrame({"listings": g.size(), "unavail_30": g.unavail_30.mean(), "unavail_90": g.unavail_90.mean(), "unavail_far": g.unavail_far.mean(),
                      "pickup_30": g.pickup_30.mean(), "pickup_90": g.pickup_90.mean(),
                      "booked_guest_nights_30": g.apply(lambda x: (x.pickup_30 * 30 * x.accommodates).sum())}).reindex(LABELS)
    t["supply_share"] = t.listings / t.listings.sum()
    t["booked_nights_share_30"] = (t.pickup_30 * 30 * t.listings) / (t.pickup_30 * 30 * t.listings).sum()
    t["booked_guest_nights_share_30"] = t.booked_guest_nights_30 / t.booked_guest_nights_30.sum()
    t["nights_index"] = t.booked_nights_share_30 / t.supply_share
    t["guest_nights_index"] = t.booked_guest_nights_share_30 / t.supply_share
    t.insert(0, "market", m); t = t.reset_index().rename(columns={"index": "bucket"})
    rows.append(t)
    print(f"{m}: {len(D):,} active entire homes; pickup_30 by bucket:", t.pickup_30.round(3).tolist())

by = pd.concat(rows, ignore_index=True)
by.to_csv(P / "abnb_forward_bookings_by_size.csv", index=False)
pool = by.groupby("bucket", observed=False).agg(listings=("listings", "sum"), booked_nights_30=("pickup_30", lambda s: np.nan),
                                                 booked_guest_nights_30=("booked_guest_nights_30", "sum")).reindex(LABELS)
pool["booked_nights_30"] = by.assign(bn=by.pickup_30 * 30 * by.listings).groupby("bucket", observed=False).bn.sum().reindex(LABELS)
pool["supply_share"] = pool.listings / pool.listings.sum()
pool["booked_nights_share_30"] = pool.booked_nights_30 / pool.booked_nights_30.sum()
pool["booked_guest_nights_share_30"] = pool.booked_guest_nights_30 / pool.booked_guest_nights_30.sum()
pool["nights_index"] = pool.booked_nights_share_30 / pool.supply_share
pool["guest_nights_index"] = pool.booked_guest_nights_share_30 / pool.supply_share
pool["pickup_30_weighted"] = pool.booked_nights_30 / (pool.listings * 30)
pool.to_csv(P / "abnb_forward_bookings_pooled.csv")
print("\nPooled (7 markets):"); print(pool.round(3).to_string())
wins = by[by.bucket.isin(["5-6 guests", "7+ guests"])].groupby("market").apply(lambda d: d.booked_guest_nights_30.sum()) / by.groupby("market").booked_guest_nights_30.sum()
sup = by[by.bucket.isin(["5-6 guests", "7+ guests"])].groupby("market").listings.sum() / by.groupby("market").listings.sum()
print("\n5+ guest homes: share of forward booked guest-nights vs share of listings, by market")
print(pd.DataFrame({"guest_nights_share": wins, "supply_share": sup, "index": wins / sup}).round(3).to_string())

plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "font.size": 10})
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
ax = axes[0]; x = np.arange(len(LABELS)); w = 0.26
ax.bar(x - w, pool.supply_share * 100, w, color=GRID, edgecolor=MUTED, label="share of listings")
ax.bar(x, pool.booked_nights_share_30 * 100, w, color=S1, label="share of forward-booked nights (next 30)")
ax.bar(x + w, pool.booked_guest_nights_share_30 * 100, w, color=S2, label="share of forward-booked guest-nights")
for i, r in enumerate(pool.itertuples()):
    ax.annotate(f"{r.guest_nights_index:.2f}x", (x[i] + w, r.booked_guest_nights_share_30 * 100), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9, fontweight="bold", color=S2 if r.guest_nights_index > 1 else INK2)
ax.set_xticks(x); ax.set_xticklabels(LABELS); ax.set_ylabel("%"); ax.legend(frameon=False, fontsize=8.5)
ax.set_title("Forward bookings by listing size, 7 markets")
ax = axes[1]
ax.bar(x, pool.pickup_30_weighted * 100, 0.5, color=S1)
for i, v in enumerate(pool.pickup_30_weighted * 100):
    ax.annotate(f"{v:.1f}%", (x[i], v), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(LABELS); ax.set_ylabel("% of next 30 nights booked, net of block baseline")
ax.set_title("Pickup per listing, next 30 nights")
fig.text(0.01, 0.01, "Inside Airbnb calendar + listings, snapshots Jun-Jul 2026: London, Manchester, Bristol, Edinburgh, Bergamo, Stockholm, Bozeman. Active entire homes (review in last 12 months).\n"
         "Pickup = unavailable share of next 30 nights minus unavailable share of nights 181-365 (host-block baseline); blocked-not-booked nights cannot be fully removed.", fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(F / "14_forward_bookings_by_size.png", dpi=160)
print("wrote figure 14")
