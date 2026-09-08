"""Aggregate cc_pricing_products.csv into the UBS-style series and draw the exhibit (built 2026-09-02).

Per crawl x banner:
  n, breadth (share of products with price < msrp), depth (mean 1 - price/msrp among discounted),
  discount_factor = breadth x depth (UBS Evidence Lab definition), mean discount across all products,
  median current price, median msrp (list), and the same by product bucket (bridal / fashion / watch).
Bucket rule: product_type in ring-like types with engagement/bridal/wedding/anniversary in the breadcrumb
or title -> bridal; watch -> watch; everything else -> fashion. Lab-grown flag from title.
Outputs: cc_pricing_monthly.csv, exhibit_cc_discount_factor.png
"""
import re, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
COL = {"kay.com": "#2a78d6", "zales.com": "#eb6834", "jared.com": "#1baf7a"}

d = pd.read_csv(os.path.join(HERE, "cc_pricing_products.csv"))
d = d.dropna(subset=["price"]).copy()
d["msrp"] = d["msrp"].fillna(d["price"])
d = d[(d["price"] > 0) & (d["msrp"] > 0)]
d["disc"] = np.clip(1 - d["price"] / d["msrp"], 0, 0.95)
d["on_sale"] = d["disc"] > 0.005
txt = (d["title"].fillna("") + " " + d["breadcrumb1"].fillna("") + " " + d["product_category"].fillna("") + " " + d["url"].fillna("")).str.lower()
d["bucket"] = np.where(d["product_type"].fillna("").str.contains("watch"), "watch",
              np.where(txt.str.contains(r"engagement|bridal|wedding|anniversary band|bridal set"), "bridal", "fashion"))
d["lab_grown"] = txt.str.contains(r"lab[- ]?(?:grown|created)")
d["capture_month"] = pd.to_datetime(d["capture_ts"].astype(str).str[:6], format="%Y%m")

def agg(g):
    on = g[g["on_sale"]]
    return pd.Series({"n": len(g), "breadth": g["on_sale"].mean(), "depth": on["disc"].mean() if len(on) else 0.0,
                      "discount_factor": g["on_sale"].mean() * (on["disc"].mean() if len(on) else 0.0),
                      "mean_discount_all": g["disc"].mean(), "median_price": g["price"].median(),
                      "median_msrp": g["msrp"].median(), "mean_price": g["price"].mean(),
                      "share_bridal": (g["bucket"] == "bridal").mean(), "share_watch": (g["bucket"] == "watch").mean(),
                      "share_lab_grown": g["lab_grown"].mean(),
                      "median_price_fashion": g.loc[g["bucket"] == "fashion", "price"].median(),
                      "median_price_bridal": g.loc[g["bucket"] == "bridal", "price"].median(),
                      "discount_factor_fashion": (lambda h: h["on_sale"].mean() * (h.loc[h["on_sale"], "disc"].mean() if h["on_sale"].any() else 0))(g[g["bucket"] == "fashion"]) if (g["bucket"] == "fashion").any() else np.nan,
                      "discount_factor_bridal": (lambda h: h["on_sale"].mean() * (h.loc[h["on_sale"], "disc"].mean() if h["on_sale"].any() else 0))(g[g["bucket"] == "bridal"]) if (g["bucket"] == "bridal").any() else np.nan})

m = d.groupby(["crawl", "domain"])[[c for c in d.columns if c not in ("crawl","domain")]].apply(agg).reset_index()
m["capture_month"] = d.groupby(["crawl", "domain"])["capture_month"].min().values
m = m.sort_values(["domain", "capture_month"])
m.to_csv(os.path.join(HERE, "cc_pricing_monthly.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(m[["crawl", "domain", "capture_month", "n", "breadth", "depth", "discount_factor", "median_price", "median_msrp", "share_bridal", "share_lab_grown"]].round(3).to_string(index=False))

# ---------------- exhibit: discount factor and median list price by banner ----------------
fig, axes = plt.subplots(2, 1, figsize=(12.5, 8), dpi=200, sharex=True, gridspec_kw={"hspace": 0.28})
fig.patch.set_facecolor(SURFACE)
for ax, col, ylabel, title in [
    (axes[0], "discount_factor", "discount factor (breadth × depth)", "Catalog-level discount factor by banner (Common Crawl product-page samples)"),
    (axes[1], "median_msrp", "median list price, $", "Median list price by banner — the assortment re-tiering behind AUR")]:
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0); ax.tick_params(length=0, labelsize=9)
    for dom in ["kay.com", "zales.com", "jared.com"]:
        s = m[(m["domain"] == dom) & (m["n"] >= 20)]
        y = s[col] * (100 if col == "discount_factor" else 1)
        ax.plot(s["capture_month"], y, color=COL[dom], linewidth=2, marker="o", markersize=4.5, markeredgecolor=SURFACE, markeredgewidth=1.2, label=dom.split(".")[0].capitalize(), zorder=3)
        if len(s):
            ax.text(s["capture_month"].iloc[-1], y.iloc[-1], f"  {dom.split('.')[0].capitalize()} {y.iloc[-1]:.0f}{'%' if col=='discount_factor' else ''}", fontsize=8.5, color=INK, va="center")
    ax.set_ylabel(ylabel, fontsize=9, color=INK2)
    ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=8)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
fig.text(0.125, 0.01, "Source: Common Crawl monthly crawls, random samples of product pages per banner (n per point in cc_pricing_monthly.csv); price = listed sale price, msrp = list price from the page's state JSON. "
         "Discount factor = share of sampled products on sale × average depth among those (UBS Evidence Lab definition). Sample composition shifts with the crawl; see share_bridal / share_watch columns.",
         fontsize=7.2, color=INK2, wrap=True)
fig.savefig(os.path.join(HERE, "exhibit_cc_discount_factor.png"), facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
print("saved exhibit_cc_discount_factor.png")

# ---------------- fiscal-quarter aggregation (n ~ 300 per banner per quarter) ----------------
dt = pd.to_datetime(d["capture_ts"].astype(str).str[:8], format="%Y%m%d")
def fq(x):
    m, y = x.month, x.year
    if m in (2, 3, 4): return f"FY{y+1}Q1"
    if m in (5, 6, 7): return f"FY{y+1}Q2"
    if m in (8, 9, 10): return f"FY{y+1}Q3"
    return f"FY{y+1 if m >= 11 else y}Q4"
d["fq"] = dt.map(fq)
def aggq(g):
    on = g[g["on_sale"]]; fa = g[g["bucket"] == "fashion"]; br = g[g["bucket"] == "bridal"]
    return pd.Series(dict(n=len(g), breadth=g["on_sale"].mean(), depth=on["disc"].mean() if len(on) else 0.0,
                          discount_factor=g["on_sale"].mean() * (on["disc"].mean() if len(on) else 0.0),
                          median_msrp=g["msrp"].median(), median_price=g["price"].median(),
                          median_msrp_fashion=fa["msrp"].median(), median_price_fashion=fa["price"].median(),
                          median_msrp_bridal=br["msrp"].median(), share_bridal=(g["bucket"] == "bridal").mean(),
                          share_lab_grown=g["lab_grown"].mean(),
                          discount_factor_fashion=fa["on_sale"].mean() * (fa.loc[fa["on_sale"], "disc"].mean() if fa["on_sale"].any() else 0) if len(fa) else np.nan))
q = d.groupby(["domain", "fq"])[[c for c in d.columns if c not in ("domain", "fq")]].apply(aggq).reset_index()
q["fy"] = q["fq"].str[2:6].astype(int); q["qn"] = q["fq"].str[-1].astype(int)
q = q.sort_values(["domain", "fy", "qn"])
prev = q.set_index(["domain", "fy", "qn"])
def yoy(row, col):
    key = (row["domain"], row["fy"] - 1, row["qn"])
    return (row[col] - prev.loc[key, col]) if key in prev.index else np.nan
q["discount_factor_yoy_bps"] = q.apply(lambda r: yoy(r, "discount_factor") * 1e4, axis=1)
q["median_msrp_yoy_pct"] = q.apply(lambda r: (r["median_msrp"] / prev.loc[(r["domain"], r["fy"] - 1, r["qn"]), "median_msrp"] - 1) * 100 if (r["domain"], r["fy"] - 1, r["qn"]) in prev.index else np.nan, axis=1)
q["median_price_yoy_pct"] = q.apply(lambda r: (r["median_price"] / prev.loc[(r["domain"], r["fy"] - 1, r["qn"]), "median_price"] - 1) * 100 if (r["domain"], r["fy"] - 1, r["qn"]) in prev.index else np.nan, axis=1)
q.to_csv(os.path.join(HERE, "cc_pricing_fiscal_quarter.csv"), index=False)
print("\nFISCAL QUARTERS:")
print(q[["domain", "fq", "n", "breadth", "depth", "discount_factor", "discount_factor_yoy_bps", "median_msrp", "median_msrp_yoy_pct", "median_price", "median_price_yoy_pct", "share_bridal"]].round(3).to_string(index=False))

# ---------------- quarterly exhibit: discount factor by banner + Kay breadth vs depth ----------------
qq = q[q["n"] >= 90]
fqs = sorted(qq["fq"].unique(), key=lambda s: (int(s[2:6]), int(s[-1])))
xi = {f: i for i, f in enumerate(fqs)}
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2), dpi=200, gridspec_kw={"wspace": 0.30})
fig.patch.set_facecolor(SURFACE)
ax = axes[0]; ax.set_facecolor(SURFACE)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0); ax.tick_params(length=0, labelsize=8.5)
w = 0.26
for k, dom in enumerate(["kay.com", "zales.com", "jared.com"]):
    s_ = qq[qq["domain"] == dom]
    ax.bar([xi[f] + (k - 1) * w for f in s_["fq"]], s_["discount_factor"] * 100, width=w * 0.92, color=COL[dom], label=dom.split(".")[0].capitalize(), zorder=3, linewidth=0)
    for f, v in zip(s_["fq"], s_["discount_factor"] * 100):
        ax.text(xi[f] + (k - 1) * w, v + 0.6, f"{v:.0f}", ha="center", fontsize=7, color=INK2)
ax.set_xticks(range(len(fqs))); ax.set_xticklabels([f.replace("FY20", "FY").replace("Q", " Q") for f in fqs], fontsize=8, rotation=45, ha="right")
ax.set_ylabel("discount factor, % (breadth × depth)", fontsize=9, color=INK2)
ax.legend(loc="upper left", fontsize=8.5, frameon=False, ncol=3)
ax.set_title("Discount factor by banner, breadth × depth (%)", loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=8)
ax = axes[1]; ax.set_facecolor(SURFACE)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0); ax.tick_params(length=0, labelsize=8.5)
kq = qq[qq["domain"] == "kay.com"]
ax.plot([xi[f] for f in kq["fq"]], kq["breadth"] * 100, color=COL["kay.com"], linewidth=2, marker="o", markersize=5.5, markeredgecolor=SURFACE, markeredgewidth=1.3, label="breadth: % of sampled Kay products marked down", zorder=3)
ax.plot([xi[f] for f in kq["fq"]], kq["depth"] * 100, color="#e34948", linewidth=2, marker="s", markersize=5.5, markeredgecolor=SURFACE, markeredgewidth=1.3, label="depth: average markdown on those products", zorder=3)
for f, b, dp in zip(kq["fq"], kq["breadth"] * 100, kq["depth"] * 100):
    ax.text(xi[f], b + 2, f"{b:.0f}", ha="center", fontsize=7.5, color=INK); ax.text(xi[f], dp - 4.5, f"{dp:.0f}", ha="center", fontsize=7.5, color=INK)
ax.set_xticks(range(len(fqs))); ax.set_xticklabels([f.replace("FY20", "FY").replace("Q", " Q") for f in fqs], fontsize=8, rotation=45, ha="right")
ax.set_ylim(0, 100); ax.set_ylabel("%", fontsize=9, color=INK2)
ax.legend(loc="lower left", fontsize=8, frameon=False)
ax.set_title("Kay: broader, not deeper — breadth doubled y/y in Q2 FY27, depth fell", loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=8)
fig.text(0.125, -0.02, "Source: Common Crawl product-page samples aggregated to Signet fiscal quarters (n ≈ 250–300 products per banner per quarter; Q3 FY27 = August crawl only). Discount factor = share of products with a listed price below list (msrp) × average markdown among those. "
         "Product samples are random within each crawl, so composition shifts (see share_bridal); use for direction and y/y, not levels.", fontsize=7.2, color=INK2, wrap=True)
fig.savefig(os.path.join(HERE, "exhibit_cc_pricing_quarterly.png"), facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
print("saved exhibit_cc_pricing_quarterly.png")
