"""
Q3 2026 nowcast, workstream E, step 7: print every table the note needs, from the CSVs E1-E6 wrote.
Nothing is computed here that is not already in a committed CSV.
Run: py -3.13 analysis/src/q3nowcast/E7_report.py
"""
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path(__file__).resolve().parents[3] / "data/processed/q3nowcast/E"
MAIN = Path(r"C:\Users\krish\citadel-abnb")
pd.set_option("display.width", 260)
pd.set_option("display.max_rows", 200)


def head(t):
    print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)


head("1. inventory")
inv = pd.read_csv(OUT / "inventory.csv")
print(inv.groupby(["store", "kind"]).agg(n=("file", "size"), gb=("bytes", lambda s: round(s.sum() / 1e9, 2))).to_string())
print("\nTheo artifacts:")
print(inv[inv.kind == "theo_artifact"][["store", "file", "present", "bytes", "note"]].to_string(index=False))
rv = inv[inv.kind == "reviews"]
print("\nreviews dumps held, by vintage month:")
print(rv.dump_date.str[:7].value_counts().sort_index().to_string())
print(f"markets {rv.market_key.nunique()}, files {len(rv)}, "
      f"{rv.bytes.sum() / 1e9:.1f} GB; vintages per market: "
      f"{rv.groupby('market_key').size().value_counts().to_dict()}")

head("2. downloads added this run")
man = pd.read_csv(OUT / "download_manifest.csv")
print(man.groupby(["mode", "status"]).agg(n=("file", "size"), gb=("bytes", lambda s: round(s.sum() / 1e9, 2))).to_string())
gaps = pd.read_csv(OUT / "download_gaps.csv")
print(f"failures: {len(gaps)}")
pl = pd.read_csv(OUT / "download_plan.csv")
print("\nCDN availability found by the probe (live dumps we did not already hold):")
print(pl.groupby("why").agg(markets=("market_key", "nunique"), files=("url", "size"),
                            gb=("bytes", lambda s: round(s.sum() / 1e9, 2))).to_string())

head("3. survivorship wedge: the same review month measured in two vintages")
w = pd.read_csv(OUT / "survivorship_wedge.csv")
if len(w):
    w = w[w.gap_days.between(330, 400)]
    g = (w[w.months_before_early_dump.between(0, 60)]
         .groupby("months_before_early_dump")
         .agg(n=("market_key", "size"), late=("n_reviews_late", "sum"), early=("n_reviews_early", "sum")))
    g["ratio_late_over_early"] = (g.late / g.early).round(4)
    g["annual_attrition_pct"] = ((1 - g.late / g.early) * 100).round(2)
    print("vintage pairs about 12 months apart, pooled over markets:")
    print(g[["n", "ratio_late_over_early", "annual_attrition_pct"]].head(40).to_string())

head("4. review posting completeness, k days after the review date")
c = pd.read_csv(OUT / "posting_completeness_curve.csv")
print(c[c.k_days <= 45][["k_days", "n_pairs", "completeness"]].round(4).to_string(index=False))

head("5. global monthly index, last 30 months")
gm = pd.read_csv(OUT / "global_monthly_index.csv")
for meas in ["yoy_all", "yoy_cohort", "yoy_vmatch"]:
    a = gm[gm.measure == meas].sort_values("ymi").tail(30)
    if a.empty:
        continue
    print(f"\n-- {meas}")
    print((a[["ym", "n_markets", "w_equal", "w_reviews", "w_median", "w_nights", "reviews"]]
           .assign(**{k: (a[k] * 100).round(2) for k in ["w_equal", "w_reviews", "w_median", "w_nights"]})
           .to_string(index=False)))

head("6. quarterly index vs disclosed KPIs")
kpi = pd.read_csv(MAIN / "data/processed/abnb_driver_history_quarterly.csv")
kpi["qi"] = kpi.year * 4 + kpi.q - 1
qq = pd.read_csv(OUT / "index_quarterly.csv")
qq["qi"] = qq.year * 4 + qq.q - 1
for meas in ["yoy_all", "yoy_cohort", "yoy_vmatch"]:
    g = qq[(qq.region == "GLOBAL") & (qq.measure == meas)][["qi", "quarter", "n_markets", "w_equal", "w_reviews", "w_median"]]
    nw = qq[(qq.region == "GLOBAL_NW") & (qq.measure == meas)][["qi", "w_equal"]].rename(columns={"w_equal": "w_nights"})
    t = g.merge(nw, on="qi", how="left").merge(
        kpi[["qi", "nights_m_yoy_pct", "gbv_musd_yoy_pct", "revenue_musd_yoy_pct"]], on="qi", how="left")
    if t.empty:
        continue
    for k in ["w_equal", "w_reviews", "w_median", "w_nights"]:
        t[k] = (t[k] * 100).round(2)
    print(f"\n-- {meas}")
    print(t[t.qi >= 2022 * 4].to_string(index=False))

head("7. regional quarterly index, review-count weighted")
for meas in ["yoy_all"]:
    p = qq[(qq.measure == meas) & qq.region.isin(["NAM", "EMEA", "LatAm", "APAC"])]
    piv = p.pivot_table(index="quarter", columns="region", values="w_reviews") * 100
    piv["qi"] = p.groupby("quarter").qi.first()
    print(piv.sort_values("qi").round(2).to_string())

head("8. backtest scoreboard")
print(pd.read_csv(OUT / "backtest_scoreboard.csv").to_string(index=False))

head("9. ABNB quarterly backtest, nights target, level features, 2023Q1+ window")
a = pd.read_csv(OUT / "backtest_abnb_quarterly.csv")
cols = ["feature", "lag", "transform", "n", "r", "r_2024q1plus", "perm_p", "wf_n",
        "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1", "sign_acc", "available_before_print"]
cols = [c for c in cols if c in a.columns]
sub = a[(a.target == "nights_yoy") & (a.window == "2023Q1+")].sort_values("wf_ratio_vs_naive")
print(sub.head(20)[cols].round(3).to_string(index=False))
print("\nsame, other targets, best 10 each")
for tgt in ["gbv_yoy", "revenue_yoy", "bkng_room_nights_yoy", "expe_room_nights_yoy"]:
    print(f"\n-- {tgt}")
    print(a[(a.target == tgt) & (a.window == "2023Q1+")].sort_values("wf_ratio_vs_naive").head(10)[cols].round(3).to_string(index=False))

head("10. jackknife of the walk-forward ratio")
rb = pd.read_csv(OUT / "backtest_survivor_robustness.csv")
print(rb[rb.target == "nights_yoy"].head(25).round(3).to_string(index=False))
print(f"\nfeatures beating naive on nights whose jackknife never crosses 1: "
      f"{int((~rb[(rb.target == 'nights_yoy')].jk_max_above_1).sum())} of {len(rb[rb.target == 'nights_yoy'])}")

head("11. Eurostat monthly test")
e = pd.read_csv(OUT / "backtest_eurostat_monthly.csv")
ec = ["family", "build", "geo", "window", "n_markets", "n", "r", "perm_p", "wf_n",
      "wf_rmse", "wf_rmse_naive", "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1", "sign_acc"]
ec = [c for c in ec if c in e.columns]
print(e[ec].round(3).to_string(index=False))

head("12. July and August 2026, within-vintage day-matched")
m = pd.read_csv(OUT / "monthly_nowcast_2026.csv")
m2 = m.copy()
for k in ["w_equal", "w_reviews", "w_median"]:
    m2[k] = (m2[k] * 100).round(2)
print(m2.to_string(index=False))

head("13. July and August 2026, vintage-matched vs within-vintage")
v = pd.read_csv(OUT / "vintage_matched_nowcast.csv")
for k in ["vmatch_eq", "vmatch_cw", "within_eq", "within_cw"]:
    if k in v:
        v[k] = (v[k] * 100).round(2)
print(v.round(2).to_string(index=False))

head("13b. per-market wedge distribution, 3q26-to-date window (scope-change screen)")
vm = pd.read_csv(OUT / "vintage_matched_nowcast_market.csv")
q = vm[vm.period == "3q26_to_date"]
if len(q):
    print(q.wedge_pp.describe(percentiles=[.05, .25, .5, .75, .95]).round(2).to_string())
    print("\nten largest wedges (candidate scope changes):")
    print(q.reindex(q.wedge_pp.abs().sort_values(ascending=False).index)
          .head(10)[["market_key", "vintage_late", "vintage_old", "n_cur", "n_prior_oldvintage",
                     "n_prior_samevintage", "yoy_vmatch", "yoy_within", "wedge_pp"]].round(3).to_string(index=False))

head("14. partial quarter to whole quarter")
p = pd.read_csv(OUT / "partial_vs_full_quarter.csv")
for k in ["partial_eq", "partial_cw", "full_eq", "full_cw"]:
    p[k] = (p[k] * 100).round(2)
print(p.round(2).to_string(index=False))

head("15. 3Q26 nowcast")
n = pd.read_csv(OUT / "q3_2026_nowcast.csv")
print(n.round(3).to_string(index=False))

head("16. coverage of the August reading")
cv = pd.read_csv(OUT / "q3_2026_coverage.csv")
print(f"markets with an August 2026 dump: {cv.vintage.astype(str).str[:7].value_counts().to_dict()}")
mm = pd.read_csv(OUT / "monthly_nowcast_2026_market.csv")
aug = mm[mm.period == "2026-08_to_date"]
print(f"markets in the August-to-date reading: {aug.market_key.nunique()}, "
      f"reviews in window {aug.n_cur.sum():,}")
jul = mm[mm.period == "2026-07"]
print(f"markets in the July reading: {jul.market_key.nunique()}, reviews {jul.n_cur.sum():,}")
print("\nby region:")
print(aug.groupby("region").agg(markets=("market_key", "nunique"), reviews=("n_cur", "sum")).to_string())
print("\nwindow end dates in the August reading:")
print(aug.win_end.value_counts().sort_index().to_string())
