"""B3: does relative currency strength explain ABNB's geographic travel mix?

Four escalating tests, from the best-measured proxy to the actual sparse target:

  T1  US inbound and outbound travel spending (BEA, real, quarterly, long history)
      against the NA inbound purchasing-power index and NA outbound affordability.
      This is the mechanism test: good n, independent of Airbnb.
  T2  Eurostat EU27 platform nights by residence of guest (foreign share and the
      foreign-minus-domestic growth differential) against the EMEA inbound index.
      Destination-side mix inside Europe, monthly source aggregated to quarters.
  T3  Airbnb regional nights growth differential (region minus total) against the
      region's inbound purchasing-power index. This is the target; n is small and
      most observations are qualitative buckets mapped to midpoints.
  T4  Airbnb cross-border share of gross nights against cross-border affordability.

Every fit reports OLS slope, r, Pearson p, Spearman, a 1,000-shuffle permutation p,
and leave-one-out RMSE against naive-last-value and LOO-mean benchmarks, the same
shape as data/processed/overnight/05_fx_fits.csv.

Run: py -3.13 analysis/src/overnight2/B3_mix_tests.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(r"C:\Users\krish\citadel-abnb-overnight2")
MAIN = Path(r"C:\Users\krish\citadel-abnb")
MP = MAIN / "data" / "processed" / "overnight"
OUT = ROOT / "data" / "processed" / "overnight2" / "B"
RNG = np.random.default_rng(20260911)
REGIONS = ["na", "emea", "latam", "apac"]


def qkey(q: str) -> int:
    return (2000 + int(q[3:])) * 4 + int(q[0]) - 1


def fit(target: str, driver: str, window: str, x: pd.Series, y: pd.Series,
        nperm: int = 1000) -> dict | None:
    d = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    n = len(d)
    if n < 6:
        return None
    xv, yv = d["x"].to_numpy(float), d["y"].to_numpy(float)
    lr = stats.linregress(xv, yv)
    sp = stats.spearmanr(xv, yv)
    # permutation p on |r|
    obs = abs(lr.rvalue)
    cnt = sum(1 for _ in range(nperm)
              if abs(np.corrcoef(xv, RNG.permutation(yv))[0, 1]) >= obs)
    perm_p = (cnt + 1) / (nperm + 1)
    # leave-one-out
    loo, naive, loom = [], [], []
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        f = stats.linregress(xv[m], yv[m])
        loo.append(f.intercept + f.slope * xv[i] - yv[i])
        loom.append(yv[m].mean() - yv[i])
        if i > 0:
            naive.append(yv[i - 1] - yv[i])
    rmse = lambda a: float(np.sqrt(np.mean(np.square(a)))) if len(a) else np.nan
    return {"target": target, "driver": driver, "window": window, "n": n,
            "slope": round(lr.slope, 4), "intercept": round(lr.intercept, 4),
            "r": round(lr.rvalue, 4), "p": round(lr.pvalue, 4),
            "spearman": round(sp.statistic, 4), "perm_p": round(perm_p, 4),
            "loo_rmse": round(rmse(loo), 4), "naive_rmse": round(rmse(naive), 4),
            "loo_mean_rmse": round(rmse(loom), 4),
            "beats_naive": bool(rmse(loo) < rmse(naive)),
            "beats_loo_mean": bool(rmse(loo) < rmse(loom))}


# ------------------------------------------------------------------ inputs
IDX = pd.read_csv(OUT / "B_relative_strength_quarterly.csv", index_col=0)
IDX["k"] = [qkey(q) for q in IDX.index]
panel = pd.read_csv(OUT / "regional_target_panel.csv")
panel = panel[~panel.quarter.str.startswith("FY")].copy()
panel["k"] = panel["quarter"].map(qkey)


def series(metric, region):
    s = (panel[(panel.metric == metric) & (panel.region == region)]
         .dropna(subset=["value"]).set_index("k")["value"].astype(float))
    return s[~s.index.duplicated()].sort_index()


def basis_of(metric, region):
    return (panel[(panel.metric == metric) & (panel.region == region)]
            .dropna(subset=["value"]).set_index("k")["basis"])


def idx_series(col, lag=0):
    s = IDX.set_index("k")[col].astype(float).sort_index()
    return s.shift(lag) if lag else s


COVID = set(range(qkey("2Q20"), qkey("4Q21") + 1))
# Reopening base effects run to end-2023 in the BEA travel series (+200% to +20% y/y)
# and in Eurostat foreign nights. They are excluded from the primary windows.
REOPEN = set(range(qkey("1Q20"), qkey("4Q23") + 1))
WINDOWS = {
    "full": lambda k: True,
    "ex_covid": lambda k: k not in COVID,
    "post22": lambda k: k >= qkey("1Q22"),
    "ex_reopening_2019_plus_from_1Q24": lambda k: k not in REOPEN,
    "from_1Q24": lambda k: k >= qkey("1Q24"),
    "from_4Q24_disclosed_era": lambda k: k >= qkey("4Q24"),
}
PRIMARY = ("ex_reopening_2019_plus_from_1Q24", "from_1Q24", "post22", "full")
fits: list[dict] = []


def run(target_name, y, driver_name, col, lags=(0, 1, 2), windows=PRIMARY,
        diff_guard=True):
    for lag in lags:
        x = idx_series(col, lag)
        for w in windows:
            keep = [k for k in y.index if WINDOWS[w](k)]
            r = fit(target_name, f"{driver_name}_lag{lag}", w,
                    x.reindex(keep), y.reindex(keep))
            if r:
                fits.append(r)
            if diff_guard and lag == 0:
                # first-difference guard: q/q changes on both sides. A level
                # relationship that is only a shared trend fails this.
                ks = sorted(keep)
                contig = [k for k in ks if (k - 1) in ks]
                dy = pd.Series({k: y.get(k, np.nan) - y.get(k - 1, np.nan) for k in contig})
                dx = pd.Series({k: x.get(k, np.nan) - x.get(k - 1, np.nan) for k in contig})
                rd = fit(f"{target_name}__qoq_diff", f"{driver_name}_qoq_diff", w, dx, dy)
                if rd:
                    fits.append(rd)


# ------------------------------------------------------ T1 BEA in / outbound
bea_in = series("bea_inbound_foreign_travel_in_us_yoy_pct", "na")
bea_out = series("bea_outbound_us_travel_abroad_yoy_pct", "na")
run("bea_us_inbound_spend_yoy", bea_in, "ipp_xb_na", "ipp_xb_na")
run("bea_us_inbound_spend_yoy", bea_in, "ipp_na", "ipp_na")
run("bea_us_outbound_spend_yoy", bea_out, "oa_xb_na", "oa_xb_na")
run("bea_us_outbound_spend_yoy", bea_out, "oa_na", "oa_na")
# the inbound-minus-outbound gap is the cleanest corridor-direction target
gap = (bea_in - bea_out).dropna()
run("bea_inbound_minus_outbound_pp", gap, "ipp_xb_na", "ipp_xb_na")
run("bea_inbound_minus_outbound_pp", gap, "usd_vs_rest_yoy", "usd_vs_rest_yoy")

# ------------------------------------------------------------ T2 Eurostat EU27
eu_share_chg = series("eurostat_eu27_platform_foreign_share_chg_pp", "emea")
eu_for = series("eurostat_eu27_platform_foreign_yoy_pct", "emea")
eu_dom = series("eurostat_eu27_platform_domestic_yoy_pct", "emea")
eu_diff = (eu_for - eu_dom).dropna()
run("eurostat_eu27_foreign_share_chg_pp", eu_share_chg, "ipp_xb_emea", "ipp_xb_emea")
run("eurostat_eu27_foreign_minus_domestic_pp", eu_diff, "ipp_xb_emea", "ipp_xb_emea")
run("eurostat_eu27_foreign_nights_yoy", eu_for, "ipp_xb_emea", "ipp_xb_emea")

# --------------------------------------------- T3 ABNB regional differential
diff_rows = []
for reg in REGIONS:
    y = series("nights_yoy_differential_pp", reg)
    b = basis_of("nights_yoy_differential_pp", reg)
    run(f"abnb_{reg}_nights_differential_pp", y, f"ipp_xb_{reg}", f"ipp_xb_{reg}",
        lags=(0, 1), windows=("ex_reopening_2019_plus_from_1Q24", "post22", "from_4Q24_disclosed_era"))
    run(f"abnb_{reg}_nights_differential_pp", y, f"ipp_{reg}", f"ipp_{reg}",
        lags=(0, 1), windows=("ex_reopening_2019_plus_from_1Q24", "post22", "from_4Q24_disclosed_era"))
    # disclosed-only subset (drop the WS10 derived residual rows)
    disc = y[[k for k in y.index if "derived" not in str(b.get(k, ""))]]
    run(f"abnb_{reg}_nights_differential_pp_disclosed_only", disc,
        f"ipp_xb_{reg}", f"ipp_xb_{reg}", lags=(0, 1), windows=("post22", "from_1Q24"))
    for k, v in y.items():
        diff_rows.append({"k": k, "region": reg, "diff_pp": v,
                          "basis": b.get(k, ""),
                          "ipp_xb": idx_series(f"ipp_xb_{reg}").get(k, np.nan),
                          "ipp": idx_series(f"ipp_{reg}").get(k, np.nan)})
POOL = pd.DataFrame(diff_rows).dropna()
# pooled with region demeaning (region fixed effects)
for w, name in [(lambda k: k not in REOPEN, "ex_reopening_2019_plus_from_1Q24"),
                (lambda k: k >= qkey("1Q22"), "post22"),
                (lambda k: k >= qkey("1Q24"), "from_1Q24"),
                (lambda k: k >= qkey("4Q24"), "from_4Q24_disclosed_era")]:
    sub = POOL[POOL.k.map(w)].copy()
    if len(sub) < 8:
        continue
    for xcol in ["ipp_xb", "ipp"]:
        s = sub.copy()
        s["yd"] = s["diff_pp"] - s.groupby("region")["diff_pp"].transform("mean")
        s["xd"] = s[xcol] - s.groupby("region")[xcol].transform("mean")
        r = fit("abnb_pooled_regional_differential_pp_demeaned",
                f"{xcol}_demeaned_lag0", name,
                s.set_index(s.index)["xd"], s.set_index(s.index)["yd"])
        if r:
            r["note"] = "pooled across four regions, both sides demeaned by region"
            fits.append(r)
POOL.to_csv(OUT / "B_pooled_regional_differential_inputs.csv", index=False)

# ------------------------------------------------------- T4 cross-border share
cbs = series("cross_border_share_of_gross_nights_pct", "total")
cbs_chg = (cbs - cbs.shift(4)).dropna()
IDXk = IDX.set_index("k")
xb_global = sum(0.25 * IDXk[f"ipp_xb_{r}"] for r in REGIONS)
IDX2 = IDX.copy()
IDX2["ipp_xb_global_equal"] = xb_global.reindex(IDX2["k"]).to_numpy()
IDX2.to_csv(OUT / "B_relative_strength_quarterly.csv")
for lag in (0, 1):
    x = xb_global.shift(lag)
    for w in ("full", "ex_covid"):
        keep = [k for k in cbs.index if WINDOWS[w](k)]
        for tgt, yy in [("abnb_cross_border_share_pct", cbs),
                        ("abnb_cross_border_share_chg_pp", cbs_chg)]:
            r = fit(tgt, f"ipp_xb_global_equal_lag{lag}", w,
                    x.reindex([k for k in yy.index if WINDOWS[w](k)]),
                    yy.reindex([k for k in yy.index if WINDOWS[w](k)]))
            if r:
                fits.append(r)
cbg = series("cross_border_nights_growth_pct", "total")
for lag in (0, 1):
    r = fit("abnb_cross_border_nights_growth_pct",
            f"ipp_xb_global_equal_lag{lag}", "full",
            xb_global.shift(lag).reindex(cbg.index), cbg)
    if r:
        fits.append(r)
# cross-border growth to a named region
for reg in ["na", "emea", "apac"]:
    y = series("cross_border_nights_growth_to_region_pct", reg)
    r = fit(f"abnb_cross_border_nights_growth_to_{reg}_pct", f"ipp_xb_{reg}_lag0",
            "full", idx_series(f"ipp_xb_{reg}").reindex(y.index), y)
    if r:
        fits.append(r)

FITS = pd.DataFrame(fits)
FITS.to_csv(OUT / "B_mix_fits.csv", index=False)

# ------------------------------------------------- descriptive alignment table
klab = {qkey(q): q for q in IDX.index}
align = pd.DataFrame({"ipp_xb_na": IDXk["ipp_xb_na"], "ipp_xb_emea": IDXk["ipp_xb_emea"],
                      "ipp_xb_latam": IDXk["ipp_xb_latam"], "ipp_xb_apac": IDXk["ipp_xb_apac"],
                      "oa_xb_na": IDXk["oa_xb_na"], "usd_vs_rest_yoy": IDXk["usd_vs_rest_yoy"]})
align["bea_us_inbound_yoy"] = bea_in
align["bea_us_outbound_yoy"] = bea_out
align["eu27_foreign_share_chg_pp"] = eu_share_chg
align["eu27_foreign_minus_domestic_pp"] = eu_diff
for reg in REGIONS:
    align[f"abnb_{reg}_diff_pp"] = series("nights_yoy_differential_pp", reg)
align["abnb_total_nights_yoy"] = series("nights_yoy_pct", "total")
align["abnb_cross_border_share_pct"] = cbs
align.index = [klab.get(k, k) for k in align.index]
align.index.name = "quarter"
align.round(3).to_csv(OUT / "B_alignment_table.csv")

print("=== fits that clear |r| >= 0.55 with perm p <= 0.10 ===")
good = FITS[(FITS.r.abs() >= 0.55) & (FITS.perm_p <= 0.10)].sort_values(
    "r", key=lambda s: s.abs(), ascending=False)
print(good.to_string(index=False))
print(f"\n{len(FITS)} fits total, {len(good)} clear the bar")
print("\n=== alignment, 2024Q2 onward ===")
cols = ["ipp_xb_na", "bea_us_inbound_yoy", "oa_xb_na", "bea_us_outbound_yoy",
        "ipp_xb_emea", "eu27_foreign_minus_domestic_pp",
        "abnb_na_diff_pp", "abnb_emea_diff_pp", "abnb_latam_diff_pp", "abnb_apac_diff_pp"]
print(align.loc["2Q24":, cols].to_string())

