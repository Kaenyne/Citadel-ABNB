"""Does listing size (accommodates, bedrooms) predict Airbnb demand?  Inside Airbnb, US + European markets.

Question behind it: the survey evidence says groups and families are the segment that picks a
rental over a hotel. If that is true, larger listings should capture a disproportionate share
of realised demand within every market. This script measures that with Inside Airbnb's
listing-level files and gives the team a size-vs-demand panel to join to hotel data.

Inputs   data/raw/insideairbnb/<state>_<city>_listings.csv.gz   (detailed listings files,
         CC BY 4.0, snapshots Jun-Aug 2026 per data/manifests/inside_airbnb_download_log.csv)
Outputs  data/processed/abnb_size_demand_by_market.csv      market x size bucket: supply share,
                                                            demand share, demand index, reviews/listing
         data/processed/abnb_size_demand_pooled.csv         all-US bucket table
         data/processed/abnb_size_regression.csv            OLS coefficients, pooled + per market
         data/processed/abnb_hawaii_islands_size.csv        Hawaii by island (joins to DBEDT survey)
         analysis/figures/08_size_demand_index.png, 09_size_demand_by_market.png

Demand proxy: number_of_reviews_ltm (reviews written in the trailing 12 months). Roughly half of
stays leave a review, so this is ~0.5 x completed stays. It is a flow (last 12 months), unlike
number_of_reviews which favours old listings. Only "active" listings are used: last_review within
the 12 months before the snapshot, or availability_365 > 0 with at least one review.

Run from repo root:  python analysis/src/listing_size_demand.py [--raw data/raw/insideairbnb]
Needs pandas, numpy, statsmodels, matplotlib.
"""
import argparse
import glob
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ACC_BINS = [0, 2, 4, 6, 99]
ACC_LABELS = ["1-2 guests", "3-4 guests", "5-6 guests", "7+ guests"]
BR_BINS = [-1, 1, 2, 3, 99]
BR_LABELS = ["0-1 br", "2 br", "3 br", "4+ br"]
COLS = ["id", "host_id", "neighbourhood_group_cleansed", "neighbourhood_cleansed", "property_type", "room_type",
        "accommodates", "bedrooms", "beds", "price", "minimum_nights", "number_of_reviews", "number_of_reviews_ltm",
        "number_of_reviews_l30d", "first_review", "last_review", "review_scores_rating", "availability_365",
        "calculated_host_listings_count", "estimated_occupancy_l365d", "estimated_revenue_l365d", "last_scraped"]


def load_market(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=lambda c: c in COLS, low_memory=False)
    name = os.path.basename(path).replace("_listings.csv.gz", "")
    df["market"] = name
    df["price_num"] = pd.to_numeric(df["price"].astype(str).str.replace(r"[\$,]", "", regex=True), errors="coerce") if "price" in df else np.nan
    snap = pd.to_datetime(df["last_scraped"], errors="coerce").max() if "last_scraped" in df else pd.Timestamp.today()
    df["snapshot"] = snap
    last = pd.to_datetime(df["last_review"], errors="coerce")
    df["active"] = (last >= snap - pd.Timedelta(days=365)) | ((df["availability_365"] > 0) & (df["number_of_reviews"] > 0))
    df["acc_bucket"] = pd.cut(df["accommodates"], ACC_BINS, labels=ACC_LABELS)
    df["br_bucket"] = pd.cut(df["bedrooms"].fillna(0), BR_BINS, labels=BR_LABELS)
    df["entire"] = df["room_type"].eq("Entire home/apt")
    df["multi_host"] = df["calculated_host_listings_count"].fillna(1) > 1
    return df


def bucket_table(df: pd.DataFrame, by: str, labels) -> pd.DataFrame:
    """Supply share, demand share (reviews_ltm), demand index = demand share / supply share, reviews per listing."""
    g = df.groupby(by, observed=False)
    t = pd.DataFrame({
        "listings": g.size(),
        "reviews_ltm": g["number_of_reviews_ltm"].sum(),
        "reviews_per_listing": g["number_of_reviews_ltm"].mean(),
        "median_price": g["price_num"].median(),
    }).reindex(labels)
    t["supply_share"] = t["listings"] / t["listings"].sum()
    t["demand_share"] = t["reviews_ltm"] / t["reviews_ltm"].sum()
    t["demand_index"] = t["demand_share"] / t["supply_share"]
    # guest-weighted (reviews x capacity = upper bound on guest-stays) and revenue-weighted (Inside Airbnb estimate) shares
    gs = df.assign(gs=df["number_of_reviews_ltm"] * df["accommodates"]).groupby(by, observed=False)["gs"].sum().reindex(labels)
    rv = df.groupby(by, observed=False)["estimated_revenue_l365d"].sum().reindex(labels) if "estimated_revenue_l365d" in df else pd.Series(np.nan, index=labels)
    t["guest_stay_share"] = gs / gs.sum(); t["guest_stay_index"] = t["guest_stay_share"] / t["supply_share"]
    t["revenue_share"] = rv / rv.sum(); t["revenue_index"] = t["revenue_share"] / t["supply_share"]
    t["median_price_per_guest"] = (df.assign(ppg=df["price_num"] / df["accommodates"]).groupby(by, observed=False)["ppg"].median()).reindex(labels)
    return t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(ROOT / "data/raw/insideairbnb"))
    ap.add_argument("--out", default=str(ROOT / "data/processed"))
    ap.add_argument("--fig", default=str(ROOT / "analysis/figures"))
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.raw, "*_listings.csv.gz")))
    if not files:
        print("no *_listings.csv.gz under", a.raw, file=sys.stderr)
        return 1
    Path(a.out).mkdir(parents=True, exist_ok=True); Path(a.fig).mkdir(parents=True, exist_ok=True)

    frames = [load_market(f) for f in files]
    allx = pd.concat(frames, ignore_index=True)
    act = allx[allx["active"] & allx["entire"] & allx["accommodates"].between(1, 16)].copy()
    print(f"{len(files)} markets, {len(allx):,} listings, {len(act):,} active entire-home listings")

    # ---------- per-market bucket tables
    rows = []
    for m, d in act.groupby("market"):
        for by, labels in (("acc_bucket", ACC_LABELS), ("br_bucket", BR_LABELS)):
            t = bucket_table(d, by, labels).reset_index().rename(columns={by: "bucket"})
            t.insert(0, "dimension", "accommodates" if by == "acc_bucket" else "bedrooms")
            t.insert(0, "market", m)
            rows.append(t)
    by_market = pd.concat(rows, ignore_index=True)
    by_market.to_csv(Path(a.out) / "abnb_size_demand_by_market.csv", index=False)

    pooled = []
    for by, labels, dim in (("acc_bucket", ACC_LABELS, "accommodates"), ("br_bucket", BR_LABELS, "bedrooms")):
        t = bucket_table(act, by, labels).reset_index().rename(columns={by: "bucket"}); t.insert(0, "dimension", dim); pooled.append(t)
    pooled = pd.concat(pooled, ignore_index=True)
    pooled.to_csv(Path(a.out) / "abnb_size_demand_pooled.csv", index=False)
    print("\nPooled (all markets, active entire homes):")
    print(pooled[["dimension", "bucket", "listings", "supply_share", "demand_share", "demand_index", "guest_stay_index", "revenue_index", "reviews_per_listing", "median_price", "median_price_per_guest"]].round(3).to_string(index=False))
    us = act[act["market"].str.match(r"^[a-z]{2}_") & act["market"].str[:2].isin(["tx", "mn", "mt", "ca", "ny", "fl", "hi", "nv", "il", "wa", "la", "dc", "tn", "co", "ma", "or", "oh", "nc", "nj", "ri", "mt"])]
    if len(us):
        tus = bucket_table(us, "acc_bucket", ACC_LABELS).reset_index().rename(columns={"acc_bucket": "bucket"}); tus.insert(0, "dimension", "accommodates_US_only")
        tus.to_csv(Path(a.out) / "abnb_size_demand_pooled_us_only.csv", index=False)
        print("\nUS-only markets:"); print(tus[["bucket", "listings", "supply_share", "demand_index", "guest_stay_index", "revenue_index", "median_price_per_guest"]].round(3).to_string(index=False))

    # ---------- regression: log(1+reviews_ltm) on size, price, min nights, host type, market FE
    try:
        import statsmodels.formula.api as smf
        reg = act.dropna(subset=["price_num"]).copy()
        reg = reg[(reg["price_num"] > 10) & (reg["price_num"] < 5000) & (reg["minimum_nights"] <= 30)]
        reg["y"] = np.log1p(reg["number_of_reviews_ltm"])
        reg["lprice"] = np.log(reg["price_num"])
        reg["bedrooms"] = reg["bedrooms"].fillna(0)
        f = "y ~ accommodates + bedrooms + lprice + np.log1p(minimum_nights) + multi_host + C(market)"
        fit = smf.ols(f, data=reg).fit(cov_type="HC1")
        keep = ["accommodates", "bedrooms", "lprice", "np.log1p(minimum_nights)", "multi_host[T.True]"]
        out = pd.DataFrame({"term": keep, "coef": fit.params[keep].values, "se": fit.bse[keep].values, "p": fit.pvalues[keep].values})
        out.insert(0, "scope", "pooled_market_FE"); out["n"] = int(fit.nobs); out["r2"] = fit.rsquared
        per = []
        for m, d in reg.groupby("market"):
            if len(d) < 300:
                continue
            fm = smf.ols("y ~ accommodates + bedrooms + lprice + np.log1p(minimum_nights) + multi_host", data=d).fit(cov_type="HC1")
            per.append({"scope": m, "term": "accommodates", "coef": fm.params["accommodates"], "se": fm.bse["accommodates"], "p": fm.pvalues["accommodates"], "n": int(fm.nobs), "r2": fm.rsquared})
        res = pd.concat([out, pd.DataFrame(per)], ignore_index=True)
        res.to_csv(Path(a.out) / "abnb_size_regression.csv", index=False)
        print("\nPooled OLS, log(1+reviews_ltm), market fixed effects, HC1 SEs:")
        print(out.round(4).to_string(index=False))
        pos = sum(1 for r in per if r["coef"] > 0 and r["p"] < 0.05)
        print(f"accommodates coefficient positive and significant in {pos} of {len(per)} markets")
    except ImportError:
        print("statsmodels missing: pip install statsmodels", file=sys.stderr)

    # ---------- Hawaii by island (joins to DBEDT accommodation survey)
    hi = act[act["market"].str.contains("hawaii")]
    if len(hi):
        g = hi.groupby("neighbourhood_group_cleansed")
        isl = pd.DataFrame({"active_entire_listings": g.size(), "reviews_ltm": g["number_of_reviews_ltm"].sum(),
                            "reviews_per_listing": g["number_of_reviews_ltm"].mean(), "mean_accommodates": g["accommodates"].mean(),
                            "share_5plus_guests": g.apply(lambda d: (d["accommodates"] >= 5).mean()), "median_price": g["price_num"].median()})
        isl.to_csv(Path(a.out) / "abnb_hawaii_islands_size.csv")
        print("\nHawaii by island:\n", isl.round(2).to_string())

    # ---------- figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    S1, S2, GRID, INK2, MUTED, SURF = "#2a78d6", "#eb6834", "#e1e0d9", "#52514e", "#898781", "#fcfcfb"
    plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlelocation": "left",
                         "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "font.size": 10})
    p = pooled[pooled["dimension"] == "accommodates"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(len(p))
    w = 0.2
    ax.bar(x - 1.5 * w, p["supply_share"] * 100, w, color=GRID, edgecolor=MUTED, label="share of listings")
    ax.bar(x - 0.5 * w, p["demand_share"] * 100, w, color=S1, label="share of bookings (reviews, 12 mo)")
    ax.bar(x + 0.5 * w, p["guest_stay_share"] * 100, w, color="#1baf7a", label="share of guest-stays (reviews x capacity)")
    ax.bar(x + 1.5 * w, p["revenue_share"] * 100, w, color=S2, label="share of est. revenue (Inside Airbnb)")
    for i, r in enumerate(p.itertuples()):
        ax.annotate(f"{r.revenue_index:.2f}x", (x[i] + 1.5 * w, r.revenue_share * 100), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9,
                    color=S2 if r.revenue_index > 1 else INK2, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(p["bucket"]); ax.set_ylabel("%"); ax.legend(frameon=False)
    ax.set_title("Bigger homes: fewer bookings per listing, far more guests and revenue (label = revenue index)")
    fig.text(0.01, 0.01, f"Inside Airbnb, {len(files)} markets (US, UK, Italy, Spain, Sweden), active entire-home listings, snapshots Jun-Aug 2026. Demand = reviews in trailing 12 months (~0.5 x stays).", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(Path(a.fig) / "08_size_demand_index.png", dpi=160)

    bm = by_market[(by_market["dimension"] == "accommodates") & (by_market["bucket"].isin(["5-6 guests", "7+ guests"]))]
    big = bm.groupby("market")[["listings", "reviews_ltm"]].sum()
    tot = by_market[by_market["dimension"] == "accommodates"].groupby("market")[["listings", "reviews_ltm"]].sum()
    bmr = by_market[(by_market["dimension"] == "accommodates")]
    rev_big = bmr[bmr["bucket"].isin(["5-6 guests", "7+ guests"])].groupby("market")["revenue_share"].sum()
    share = pd.DataFrame({"supply_share_5plus": big["listings"] / tot["listings"], "demand_share_5plus": big["reviews_ltm"] / tot["reviews_ltm"], "revenue_share_5plus": rev_big})
    share["demand_index_5plus"] = share["demand_share_5plus"] / share["supply_share_5plus"]
    share["revenue_index_5plus"] = share["revenue_share_5plus"] / share["supply_share_5plus"]
    share = share.sort_values("revenue_index_5plus")
    share.to_csv(Path(a.out) / "abnb_size_demand_5plus_by_market.csv")
    fig, ax = plt.subplots(figsize=(9, 6))
    yy = np.arange(len(share)); h = 0.38
    ax.barh(yy - h / 2, share["demand_index_5plus"], h, color=S1, label="bookings index (reviews share / listing share)")
    ax.barh(yy + h / 2, share["revenue_index_5plus"], h, color=S2, label="revenue index (est. revenue share / listing share)")
    ax.set_yticks(yy); ax.set_yticklabels(share.index)
    ax.axvline(1, color=MUTED, lw=1, ls="--"); ax.set_xlabel("index for 5+ guest homes (1 = proportional to listing count)"); ax.legend(frameon=False, loc="lower right")
    ax.set_title("5+ guest homes: share of bookings vs share of revenue, by market")
    fig.tight_layout(); fig.savefig(Path(a.fig) / "09_size_demand_by_market.png", dpi=160)
    print("\nwrote", a.out, "and", a.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
