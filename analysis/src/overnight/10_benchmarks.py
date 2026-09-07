"""Workstream 10, part 2: external regional benchmarks aligned to ABNB quarters, with publication lag and correlations.

Reads
  data/processed/overnight/10_regional_panel_quarterly.csv         regional nights growth (built by 10_regional_panel.py)
  data/processed/overnight/10_eurostat_platform_monthly_latest.csv EU27 + country platform nights (10_fetch_eurostat_latest.py)
  data/processed/overnight/10_bench_japan_arrivals_monthly.csv     JNTO (10_fetch_benchmarks.py)
  data/processed/overnight/10_bench_canada_travel_monthly.csv      StatCan 24-10-0053 (10_fetch_benchmarks.py)
  data/processed/overnight/10_fx_quarterly.csv                     FRED FX (10_fetch_fx.py)
  data/processed/overnight/10_fx_basket.csv                        regional FX baskets (10_regional_panel.py)
  data/processed/overnight/08_trends_weekly.csv                    Google Trends 'airbnb', US and worldwide (workstream 8)
  data/raw/bea/bea_pce_travel_monthly_2015_2026.csv                BEA monthly PCE travel lines
  data/processed/predictive/02_peer_prints.csv                     MAR / HLT RevPAR, BKNG / EXPE room nights
Writes
  data/processed/overnight/10_regional_benchmarks.csv              quarterly aligned benchmark panel (one row per quarter)
  data/processed/overnight/10_regional_benchmark_sources.csv       source and publication lag for each benchmark column
  data/processed/overnight/10_regional_benchmark_correlations.csv  r vs each region's nights growth at lag -1/0/+1, with n
Run: py -3.13 analysis/src/overnight/10_benchmarks.py

Point-in-time note: available_by_days_after_quarter_end on each series says when the full quarter of that benchmark is
public. ABNB reports about 37 days after quarter end (5 Nov 2026 for 3Q26), so anything above ~37 days is NOT usable to
nowcast the quarter being reported; Eurostat platform nights (about 150 days) runs a full quarter behind.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "overnight")


def qlab(ts):
    return f"{ts.quarter}Q{str(ts.year)[2:]}"


def qseries(monthly, how="sum", min_count=3):
    """monthly DatetimeIndex series -> quarterly y/y %, quarter-label index; incomplete quarters dropped"""
    if how == "sum":
        g = monthly.resample("QE").sum(min_count=min_count)
    else:
        g = monthly.resample("QE").apply(lambda s: s.mean() if s.notna().sum() >= min_count else np.nan)
    yoy = (g / g.shift(4) - 1) * 100
    yoy.index = [qlab(t) for t in yoy.index]
    return yoy


panel = pd.read_csv(os.path.join(OUT, "10_regional_panel_quarterly.csv")).set_index("quarter")
ORDER = list(panel.index)
b = pd.DataFrame(index=pd.Index(ORDER, name="quarter"))
LAG, WHO, REG = {}, {}, {}


def add(name, s, days, who, region):
    b[name] = pd.Series(s).reindex(b.index)
    LAG[name], WHO[name], REG[name] = days, who, region


# ---------------------------------------------------------------- ABNB actuals, kept in the file for reference
for c in ["total_nights_yoy_pct", "na_nights_yoy_mid", "emea_nights_yoy_mid", "latam_nights_yoy_mid",
          "apac_nights_yoy_mid", "na_nights_share_est_pct", "emea_nights_share_est_pct",
          "latam_nights_share_est_pct", "apac_nights_share_est_pct"]:
    b[c] = panel[c]

# ---------------------------------------------------------------- EMEA: Eurostat platform nights
eu = pd.read_csv(os.path.join(OUT, "10_eurostat_platform_monthly_latest.csv"), index_col=0)
eu.index = pd.to_datetime(eu.index)
for col, nm in [("eu27_nights", "eu27_platform_nights_yoy_pct"),
                ("eu27_domestic", "eu27_platform_domestic_yoy_pct"),
                ("eu27_foreign", "eu27_platform_foreign_yoy_pct")]:
    add(nm, qseries(eu[col]), 150, "Eurostat tour_ce_omr (NGT_SP, NR)", "emea")
for cc in ["ES", "FR", "IT", "DE", "PT", "EL", "NL"]:
    add(f"eurostat_{cc}_platform_nights_yoy_pct", qseries(eu[f"{cc}_nights"]), 150, "Eurostat tour_ce_omr", "emea")
big5 = eu[[f"{c}_nights" for c in ["ES", "FR", "IT", "DE", "PT"]]].sum(axis=1, min_count=5)
add("eurostat_big5_platform_nights_yoy_pct", qseries(big5), 150, "Eurostat tour_ce_omr, ES+FR+IT+DE+PT", "emea")

# ---------------------------------------------------------------- NA: BEA monthly PCE travel
bea = pd.read_csv(os.path.join(ROOT, "data", "raw", "bea", "bea_pce_travel_monthly_2015_2026.csv"))
bea["date"] = pd.to_datetime(bea.date)


def bea_s(series, measure):
    s = bea[(bea.series == series) & (bea.measure == measure)].set_index("date")["value"].sort_index()
    return qseries(s, how="mean")   # SAAR levels: average across the quarter


add("bea_inbound_foreign_travel_in_us_real_yoy_pct", bea_s("inbound_foreign_travel_in_us", "real_chained_2017_musd"), 30, "BEA PCE monthly line 339", "na")
add("bea_inbound_foreign_travel_in_us_nom_yoy_pct", bea_s("inbound_foreign_travel_in_us", "nominal_saar_musd"), 30, "BEA PCE monthly line 339", "na")
add("bea_outbound_us_travel_real_yoy_pct", bea_s("foreign_travel_by_us_residents", "real_chained_2017_musd"), 30, "BEA PCE monthly line 334", "na")
add("bea_accommodations_real_yoy_pct", bea_s("accommodations", "real_chained_2017_musd"), 30, "BEA PCE monthly line 249", "na")
add("bea_accommodations_nom_yoy_pct", bea_s("accommodations", "nominal_saar_musd"), 30, "BEA PCE monthly line 249", "na")
add("bea_accommodations_price_yoy_pct", bea_s("accommodations", "price_index_2017eq100"), 30, "BEA PCE monthly line 249 price index", "na")
add("bea_hotels_motels_real_yoy_pct", bea_s("hotels_motels", "real_chained_2017_musd"), 30, "BEA PCE monthly line 250", "na")
add("bea_air_transportation_real_yoy_pct", bea_s("air_transportation", "real_chained_2017_musd"), 30, "BEA PCE monthly line 207", "na")

# ---------------------------------------------------------------- NA: StatCan Canada <-> US
ca = pd.read_csv(os.path.join(OUT, "10_bench_canada_travel_monthly.csv"), index_col=0)
ca.index = pd.to_datetime(ca.index)
for col, nm in [("cdn_residents_returning_from_us", "statcan_cdn_returning_from_us_yoy_pct"),
                ("cdn_residents_returning_from_us_air", "statcan_cdn_returning_from_us_air_yoy_pct"),
                ("cdn_residents_returning_from_us_land", "statcan_cdn_returning_from_us_land_yoy_pct"),
                ("cdn_residents_returning_from_other", "statcan_cdn_returning_from_other_yoy_pct"),
                ("us_residents_entering_canada", "statcan_us_residents_entering_canada_yoy_pct")]:
    add(nm, qseries(ca[col]), 40, "Statistics Canada table 24-10-0053", "na")

# ---------------------------------------------------------------- hotel peers and OTAs
pp = pd.read_csv(os.path.join(ROOT, "data", "processed", "predictive", "02_peer_prints.csv"))
pp["q"] = pp.quarter.map(lambda s: f"{s[-1]}Q{s[2:4]}")
pp = pp.set_index("q")
add("mar_revpar_yoy_pct", pp["mar_revpar_yoy"], 33, "Marriott quarterly release, worldwide systemwide RevPAR", "na")
add("hlt_revpar_yoy_pct", pp["hlt_revpar_yoy"], 24, "Hilton quarterly release, systemwide comparable RevPAR", "na")
add("bkng_room_nights_yoy_pct", pp["bkng_room_nights_yoy"], 30, "Booking Holdings quarterly release", "global")
add("expe_room_nights_yoy_pct", pp["expe_room_nights_yoy"], 37, "Expedia quarterly release", "global")

# ---------------------------------------------------------------- APAC: JNTO
jp = pd.read_csv(os.path.join(OUT, "10_bench_japan_arrivals_monthly.csv"))
jp["month"] = pd.to_datetime(jp.month)
add("jnto_japan_inbound_arrivals_yoy_pct", qseries(jp.set_index("month")["visitors"]), 21, "JNTO monthly visitor arrivals", "apac")

# ---------------------------------------------------------------- Google Trends (no publication lag)
tr = pd.read_csv(os.path.join(OUT, "08_trends_weekly.csv"))
tr["date"] = pd.to_datetime(tr.date)
for geo, nm in [("US", "trends_airbnb_us_yoy_pct"), ("WW", "trends_airbnb_ww_yoy_pct")]:
    s = tr[(tr.term == "airbnb") & (tr.geo == geo)].groupby("date")["value_stitched"].mean().sort_index()
    add(nm, qseries(s, how="mean", min_count=10), 0, "Google Trends 'airbnb' weekly, stitched (workstream 8)", "na" if geo == "US" else "global")

# ---------------------------------------------------------------- FX
fxq = pd.read_csv(os.path.join(OUT, "10_fx_quarterly.csv"), header=[0, 1], index_col=0)["yoy_pct"]
for ccy in ["EUR", "GBP", "BRL", "MXN", "JPY", "AUD", "KRW", "CAD", "INR"]:
    add(f"fx_{ccy.lower()}_usd_per_unit_yoy_pct", fxq[ccy].round(2), 0, "FRED daily FX, quarterly average, USD per unit", "fx")
bk = pd.read_csv(os.path.join(OUT, "10_fx_basket.csv"))
bk = bk[bk.currency == "BASKET"].set_index("region")
for r in ["na", "emea", "latam", "apac", "global_revenue_weighted"]:
    vals = {q: bk.loc[r, f"usd_per_unit_yoy_{q}_pct"] for q in ["1Q26", "2Q26", "3Q26"]}
    nm = f"fx_basket_{r}_yoy_pct"
    b[nm] = pd.Series(vals).reindex(b.index)
    LAG[nm], WHO[nm], REG[nm] = 0, "FRED with the region weights in 10_fx_basket.csv", "fx"

# ---------------------------------------------------------------- write
meta = pd.DataFrame([dict(series=k, region=REG[k], source=WHO[k], available_by_days_after_quarter_end=LAG[k]) for k in LAG])
b = b.round(2)
b.reset_index().to_csv(os.path.join(OUT, "10_regional_benchmarks.csv"), index=False)
meta.to_csv(os.path.join(OUT, "10_regional_benchmark_sources.csv"), index=False)
show = [c for c in b.columns if c.startswith(("eu27_platform_nights", "bea_inbound_foreign_travel_in_us_real",
                                              "statcan_cdn_returning_from_us_yoy", "jnto", "mar_revpar", "trends_airbnb_us"))]
print(b.loc["4Q24":, ["total_nights_yoy_pct"] + show].to_string())

# ---------------------------------------------------------------- correlations
TARGETS = {"na": "na_nights_yoy_mid", "emea": "emea_nights_yoy_mid", "latam": "latam_nights_yoy_mid",
           "apac": "apac_nights_yoy_mid", "total": "total_nights_yoy_pct"}
# NA and EMEA nights are derived (not disclosed) for 4Q22..3Q24, so those correlations are partly circular;
# rerun them on the disclosed-only subset, which for NA/EMEA starts at 4Q24.
DISCLOSED_FROM = {"na": "4Q24", "emea": "4Q24", "latam": "3Q22", "apac": "3Q22", "total": "3Q22"}
POST2022 = [q for q in ORDER if ORDER.index(q) >= ORDER.index("4Q22")]
# Everything post-COVID trends down together, so a y/y-on-y/y correlation is mostly a shared normalisation trend
# (the same artefact flagged in research/notes/predictive). The honest test is on ACCELERATION: first differences of
# the y/y series. Both are computed; `basis` says which.
rows = []
for tname, tcol in TARGETS.items():
    for s in LAG:
        for basis in ["level (y/y)", "acceleration (d y/y)"]:
            xs_all = b[s].astype(float)
            ys_all = b[tcol].astype(float)
            if basis.startswith("acceleration"):
                xs_all = xs_all.diff()
                ys_all = ys_all.diff()
            for lag in (-1, 0, 1):   # lag +1: the benchmark's PRIOR quarter against this quarter's nights (benchmark leads)
                for sub in ["post-2022 all", "disclosed only", "post-4Q24 normalised"]:
                    if sub == "post-2022 all":
                        qs = POST2022
                    elif sub == "disclosed only":
                        qs = [q for q in POST2022 if ORDER.index(q) >= ORDER.index(DISCLOSED_FROM[tname])]
                    else:
                        qs = [q for q in POST2022 if ORDER.index(q) >= ORDER.index("4Q24")]
                    x = xs_all.shift(lag).reindex(qs)
                    y = ys_all.reindex(qs)
                    m = x.notna() & y.notna()
                    if m.sum() < 6:
                        continue
                    if x[m].std() == 0 or y[m].std() == 0:
                        continue
                    r = float(np.corrcoef(x[m], y[m])[0, 1])
                    rows.append(dict(target=tname, benchmark=s, benchmark_region=REG[s], basis=basis, lag_quarters=lag,
                                     subset=sub, n=int(m.sum()), r=round(r, 3), first_quarter=x[m].index[0],
                                     last_quarter=x[m].index[-1], available_by_days_after_quarter_end=LAG[s], source=WHO[s]))
corr = pd.DataFrame(rows).sort_values(["target", "basis", "subset", "lag_quarters", "r"], ascending=[True, True, True, True, False])
corr.to_csv(os.path.join(OUT, "10_regional_benchmark_correlations.csv"), index=False)
print("\ncorrelation tests run:", len(corr))
for basis in ["level (y/y)", "acceleration (d y/y)"]:
    for t in TARGETS:
        g = corr[(corr.target == t) & (corr.basis == basis) & (corr.subset == "post-4Q24 normalised") & (corr.lag_quarters == 0)]
        g = g.reindex(g.r.abs().sort_values(ascending=False).index).head(6)
        print(f"\n-- {t} | {basis} | lag 0 | post-2022")
        print(g[["benchmark", "n", "r"]].to_string(index=False))
