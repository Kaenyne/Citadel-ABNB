"""
Q3 2026 nowcast, workstream E, August-batch refresh, step 3: before/after comparison of the
committed E outputs (data/processed/q3nowcast/E, the 12 Sep run) and the refreshed E_aug outputs.

Writes data/processed/q3nowcast/E_aug/
  before_after.csv          long table: block, key, metric, before, after, delta
  big_markets_aug2026.csv   the named large markets' July, August-to-date and 3Q26-to-date reads,
                            within-vintage and vintage-matched, before and after

Run: py -3.13 analysis/src/q3nowcast/E_aug3_compare.py
"""
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
B = WT / "data/processed/q3nowcast/E"
A = WT / "data/processed/q3nowcast/E_aug"
BIG = {"united-states_ca_los-angeles": "Los Angeles", "united-states_ca_san-francisco": "San Francisco",
       "united-states_il_chicago": "Chicago", "united-kingdom_england_london": "London",
       "france_ile-de-france_paris": "Paris", "spain_catalonia_barcelona": "Barcelona",
       "australia_nsw_sydney": "Sydney", "canada_on_toronto": "Toronto", "united-states_ma_boston": "Boston",
       "singapore_sg_singapore": "Singapore", "united-states_ny_new-york-city": "New York City",
       "canada_qc_montreal": "Montreal", "japan_kanto_tokyo": "Tokyo"}
pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 300)

rows = []


def add(block, key, metric, b, a):
    b = np.nan if b is None else b
    a = np.nan if a is None else a
    rows.append(dict(block=block, key=key, metric=metric, before=b, after=a,
                     delta=(a - b) if (isinstance(a, (int, float, np.floating, np.integer)) and
                                      isinstance(b, (int, float, np.floating, np.integer))) else np.nan))


def rd(d, f):
    return pd.read_csv(d / f, encoding="utf-8")


# ---------------------------------------------------------------- 1. coverage
def coverage(d):
    mv = rd(d, "market_vintage_monthly.csv")
    lat = mv.sort_values("dump_date").groupby("market_key").dump_date.last()
    mv = mv.join(lat.rename("latest"), on="market_key")
    mv = mv[mv.dump_date == mv.latest]
    q3_25 = mv[mv.ym.isin(["2025-07", "2025-08", "2025-09"])].groupby("market_key").n_reviews.sum()
    mm = rd(d, "monthly_nowcast_2026_market.csv")
    jul = set(mm[mm.period == "2026-07"].market_key)
    aug = set(mm[mm.period == "2026-08_to_date"].market_key)
    both = jul & aug
    vm = rd(d, "vintage_matched_nowcast_market.csv")
    vm3 = vm[vm.period == "3q26_to_date"]
    geo = rd(d, "market_geo.csv").set_index("market_key").region
    out = dict(n_markets=int(lat.size),
               n_aug_dump=int((lat.str[:7] == "2026-08").sum()),
               n_jul_window=len(jul), n_aug_window=len(aug), n_jul_and_aug=len(both),
               share_3q25_base_jul_and_aug=float(q3_25.reindex(list(both)).sum() / q3_25.sum()),
               n_vmatch_3q26=int(vm3.market_key.nunique()),
               share_3q25_base_vmatch=float(q3_25.reindex(vm3.market_key.unique()).sum() / q3_25.sum()))
    for r in ["NAM", "EMEA", "LatAm", "APAC"]:
        ks = [k for k in both if geo.get(k) == r]
        out[f"n_jul_and_aug_{r}"] = len(ks)
        base = q3_25[q3_25.index.map(lambda k: geo.get(k) == r)]
        out[f"share_3q25_base_jul_and_aug_{r}"] = float(q3_25.reindex(ks).sum() / base.sum()) if base.sum() else np.nan
        out[f"n_vmatch_3q26_{r}"] = int(vm3[vm3.region == r].market_key.nunique())
    aug_m = mm[mm.period == "2026-08_to_date"]
    out["aug_window_days_median"] = float((pd.to_datetime(aug_m.win_end) - pd.to_datetime(aug_m.win_start)).dt.days.median() + 1)
    out["aug_window_days_min"] = float((pd.to_datetime(aug_m.win_end) - pd.to_datetime(aug_m.win_start)).dt.days.min() + 1)
    return out, q3_25


cb, q3b = coverage(B)
ca, q3a = coverage(A)
for k in ca:
    add("coverage", "all", k, cb.get(k), ca.get(k))

# ---------------------------------------------------------------- 2. monthly reads, within vintage
for d, tag in [(B, "before"), (A, "after")]:
    pass
mb, ma = rd(B, "monthly_nowcast_2026.csv"), rd(A, "monthly_nowcast_2026.csv")
for per in ["2026-07", "2026-08_to_date"]:
    for reg in ["NAM", "EMEA", "LatAm", "APAC", "GLOBAL", "GLOBAL_NW"]:
        b = mb[(mb.period == per) & (mb.region == reg)]
        a = ma[(ma.period == per) & (ma.region == reg)]
        for w in ["w_equal", "w_reviews", "w_median", "n_markets"]:
            bv = float(b[w].iloc[0]) if len(b) and pd.notna(b[w].iloc[0]) else np.nan
            av = float(a[w].iloc[0]) if len(a) and pd.notna(a[w].iloc[0]) else np.nan
            add("within_vintage_daymatched", f"{per}|{reg}", w, bv * (100 if w != "n_markets" else 1), av * (100 if w != "n_markets" else 1))

# ---------------------------------------------------------------- 3. vintage-matched reads
vb, va = rd(B, "vintage_matched_nowcast.csv"), rd(A, "vintage_matched_nowcast.csv")
for per in ["2026-07", "2026-08_to_date", "3q26_to_date"]:
    for reg in ["NAM", "EMEA", "LatAm", "APAC", "GLOBAL", "GLOBAL_NW"]:
        b = vb[(vb.period == per) & (vb.region == reg)]
        a = va[(va.period == per) & (va.region == reg)]
        for w in ["vmatch_eq", "vmatch_cw", "within_eq", "within_cw", "wedge_eq_pp", "n_markets"]:
            sc = 100 if w in ("vmatch_eq", "vmatch_cw", "within_eq", "within_cw") else 1
            bv = float(b[w].iloc[0]) * sc if len(b) and pd.notna(b[w].iloc[0]) else np.nan
            av = float(a[w].iloc[0]) * sc if len(a) and pd.notna(a[w].iloc[0]) else np.nan
            add("vintage_matched_daymatched", f"{per}|{reg}", w, bv, av)

# ---------------------------------------------------------------- 4. partial-window index (3Q26 to date, all years)
pb, pa = rd(B, "partial_window_yoy_index.csv"), rd(A, "partial_window_yoy_index.csv")
for back in [0, 1, 2, 3]:
    for reg in ["NAM", "EMEA", "LatAm", "APAC", "GLOBAL", "GLOBAL_NW"]:
        b = pb[(pb.years_back == back) & (pb.region == reg)]
        a = pa[(pa.years_back == back) & (pa.region == reg)]
        for w in ["w_equal", "w_reviews", "w_median", "n_markets"]:
            sc = 1 if w == "n_markets" else 100
            bv = float(b[w].iloc[0]) * sc if len(b) and pd.notna(b[w].iloc[0]) else np.nan
            av = float(a[w].iloc[0]) * sc if len(a) and pd.notna(a[w].iloc[0]) else np.nan
            add("q3_to_date_window", f"years_back={back}|{reg}", w, bv, av)

# ---------------------------------------------------------------- 5. quarterly index (history should be near-identical)
qb, qa = rd(B, "index_quarterly.csv"), rd(A, "index_quarterly.csv")
for meas in ["yoy_all", "yoy_vmatch", "yoy_cohort", "yoy_stable"]:
    for reg in ["GLOBAL", "GLOBAL_NW", "APAC"]:
        for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
            b = qb[(qb.measure == meas) & (qb.region == reg) & (qb.quarter == q)]
            a = qa[(qa.measure == meas) & (qa.region == reg) & (qa.quarter == q)]
            for w in ["w_equal", "w_reviews", "n_markets"]:
                sc = 1 if w == "n_markets" else 100
                bv = float(b[w].iloc[0]) * sc if len(b) and pd.notna(b[w].iloc[0]) else np.nan
                av = float(a[w].iloc[0]) * sc if len(a) and pd.notna(a[w].iloc[0]) else np.nan
                add("quarterly_index", f"{meas}|{reg}|{q}", w, bv, av)

# ---------------------------------------------------------------- 6. backtest
sb, sa = rd(B, "backtest_scoreboard.csv"), rd(A, "backtest_scoreboard.csv")
for fam in sb.family:
    for c in ["tests", "flagged", "beat_naive", "beat_naive_and_ar1", "beat_by_20pct", "best_ratio"]:
        add("backtest_scoreboard", fam, c, float(sb[sb.family == fam][c].iloc[0]),
            float(sa[sa.family == fam][c].iloc[0]) if (sa.family == fam).any() else np.nan)
bb, ba = rd(B, "backtest_abnb_quarterly.csv"), rd(A, "backtest_abnb_quarterly.csv")
feats = ["GLOBAL|yoy_all|w_reviews", "GLOBAL|yoy_all|w_equal", "GLOBAL|yoy_all|w_median",
         "GLOBAL_NW|yoy_all|w_equal", "GLOBAL|yoy_vmatch|w_reviews", "GLOBAL|yoy_vmatch|w_equal",
         "GLOBAL_NW|yoy_vmatch|w_equal", "GLOBAL|yoy_cohort|w_equal", "APAC|yoy_all|w_reviews",
         "APAC|yoy_vmatch|w_reviews"]
for f in feats:
    for lag in [0, 1]:
        sel = lambda t: t[(t.feature == f) & (t.lag == lag) & (t["transform"] == "level") & (t.target == "nights_yoy") & (t.window == "2023Q1+")]
        b, a = sel(bb), sel(ba)
        for c in ["r", "r_2024q1plus", "perm_p", "wf_n", "wf_rmse", "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1", "sign_acc"]:
            add("backtest_nights_2023Q1plus_level", f"{f}|lag{lag}", c,
                float(b[c].iloc[0]) if len(b) else np.nan, float(a[c].iloc[0]) if len(a) else np.nan)
eb, ea = rd(B, "backtest_eurostat_monthly.csv"), rd(A, "backtest_eurostat_monthly.csv")
for fam, geo, win in [("eurostat_eu27", "EU27", "2023M1+"), ("eurostat_eu27", "EU27", "2022M1+")]:
    b = eb[(eb.family == fam) & (eb.geo == geo) & (eb.window == win)]
    a = ea[(ea.family == fam) & (ea.geo == geo) & (ea.window == win)]
    for c in ["r", "wf_ratio_vs_naive", "wf_ratio_vs_prior", "wf_ratio_vs_ar1"]:
        add("backtest_eurostat", f"{geo}|{win}", c, float(b[c].iloc[0]) if len(b) else np.nan,
            float(a[c].iloc[0]) if len(a) else np.nan)

# ---------------------------------------------------------------- 7. the 3Q26 nowcast
nb, na_ = rd(B, "q3_2026_nowcast.csv"), rd(A, "q3_2026_nowcast.csv")
for _, r in nb.iterrows():
    k = f"{r.measure}|{r.weighting}|{r.region}"
    a = na_[(na_.measure == r.measure) & (na_.weighting == r.weighting) & (na_.region == r.region)]
    for c in ["slope", "partial_index_3q26_pct", "gap_mean_pp", "full_index_3q26_pct", "index_2q26_pct",
              "implied_nights_yoy", "implied_nights_yoy_anchored_2q26", "band_pp", "lo", "hi", "wf_rmse_pp", "wf_ratio_vs_naive"]:
        add("q3_2026_nowcast", k, c, float(r[c]), float(a[c].iloc[0]) if len(a) else np.nan)
# summary point: mean of the seven implied rows and of the anchored rows, and the min lo / max hi
for tag, t in [("before", nb), ("after", na_)]:
    pass
add("q3_2026_nowcast", "summary", "mean_implied_7rows", float(nb.implied_nights_yoy.mean()), float(na_.implied_nights_yoy.mean()))
add("q3_2026_nowcast", "summary", "mean_anchored_7rows", float(nb.implied_nights_yoy_anchored_2q26.mean()), float(na_.implied_nights_yoy_anchored_2q26.mean()))
add("q3_2026_nowcast", "summary", "min_lo", float(nb.lo.min()), float(na_.lo.min()))
add("q3_2026_nowcast", "summary", "max_hi", float(nb.hi.max()), float(na_.hi.max()))
add("q3_2026_nowcast", "summary", "mean_band_pp", float(nb.band_pp.mean()), float(na_.band_pp.mean()))

# ---------------------------------------------------------------- 8. posting completeness and partial-to-full gap
cb_, ca_ = rd(B, "posting_completeness_curve.csv"), rd(A, "posting_completeness_curve.csv")
for k in [7, 10, 14, 21]:
    add("posting_completeness", f"k={k}", "completeness",
        float(cb_[cb_.k_days == k].completeness.iloc[0]), float(ca_[ca_.k_days == k].completeness.iloc[0]))
gb_, ga_ = rd(B, "partial_vs_full_quarter.csv"), rd(A, "partial_vs_full_quarter.csv")
for y in [2023, 2024, 2025]:
    for c in ["gap_cw_pp", "gap_eq_pp"]:
        b = gb_[(gb_.year == y) & (gb_.region == "GLOBAL")]
        a = ga_[(ga_.year == y) & (ga_.region == "GLOBAL")]
        add("partial_to_full_gap", f"GLOBAL|{y}", c, float(b[c].iloc[0]) if len(b) else np.nan, float(a[c].iloc[0]) if len(a) else np.nan)

out = pd.DataFrame(rows)
out.to_csv(A / "before_after.csv", index=False, encoding="utf-8")
print(f"before_after.csv {len(out)} rows")

# ---------------------------------------------------------------- 9. big markets
def big(d, tag):
    mm = rd(d, "monthly_nowcast_2026_market.csv")
    vm = rd(d, "vintage_matched_nowcast_market.csv")
    mm = mm[mm.market_key.isin(BIG)].rename(columns={"yoy": "yoy_within", "vintage": "vintage_late"})
    mm["construction"] = "within_vintage"
    vm = vm[vm.market_key.isin(BIG)]
    vm["construction"] = "vintage_matched"
    cols = ["market_key", "region", "period", "construction", "vintage_late", "vintage_old", "win_start", "win_end",
            "n_cur", "n_prior", "n_prior_oldvintage", "yoy_within", "yoy_vmatch", "wedge_pp"]
    t = pd.concat([mm, vm], ignore_index=True)
    for c in cols:
        if c not in t.columns:
            t[c] = np.nan
    t = t[cols]
    t.insert(0, "run", tag)
    t.insert(1, "market", t.market_key.map(BIG))
    return t


bg = pd.concat([big(B, "before"), big(A, "after")], ignore_index=True)
bg.to_csv(A / "big_markets_aug2026.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------- print
def show(block, keys=None):
    t = out[out.block == block]
    if keys:
        t = t[t.key.isin(keys)]
    print("\n== " + block)
    print(t.drop(columns="block").round(3).to_string(index=False))


show("coverage")
show("vintage_matched_daymatched")
show("within_vintage_daymatched")
show("q3_to_date_window", [f"years_back=0|{r}" for r in ["NAM", "EMEA", "LatAm", "APAC", "GLOBAL", "GLOBAL_NW"]])
show("backtest_scoreboard")
show("backtest_nights_2023Q1plus_level")
show("backtest_eurostat")
show("q3_2026_nowcast")
show("posting_completeness")
show("partial_to_full_gap")
print("\n== quarterly index rows that moved by more than 0.05 pp")
qm = out[(out.block == "quarterly_index") & (out.metric != "n_markets") & (out.delta.abs() > 0.05)]
print(qm.drop(columns="block").round(3).to_string(index=False) if len(qm) else "none")
print("\n== big markets, after run")
t = bg[bg.run == "after"].copy()
for c in ["yoy_within", "yoy_vmatch"]:
    t[c] = (t[c] * 100).round(1)
print(t[["market", "period", "construction", "vintage_late", "vintage_old", "win_end", "n_cur", "yoy_within", "yoy_vmatch", "wedge_pp"]]
      .sort_values(["market", "construction", "period"]).round(1).to_string(index=False))
print("\n== big markets, before vs after (vintage-matched 3q26_to_date and within-vintage Aug)")
piv = bg[bg.period.isin(["3q26_to_date", "2026-08_to_date", "2026-07"])].pivot_table(
    index=["market", "period", "construction"], columns="run", values=["yoy_within", "yoy_vmatch"], aggfunc="first")
print((piv * 100).round(1).to_string())
