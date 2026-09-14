"""
WS-P step 2: note-08 walk-forward tests of every collected official price series against the
Airbnb ADR targets, using the shared protocol in analysis/src/adrq3/I0_protocol.py (expanding
OLS refit strictly before each scored quarter from 1Q24; RMSE ratio vs naive last quarter, prior
year and AR(1); 1,000-shuffle permutation p), plus a leave-one-scored-quarter-out jackknife on
the naive ratio and a knowable-before-print flag. Bonferroni is over all tests on each target, as
J2 does. Both windows (2023Q1+ and 2022Q1+); the residual target only exists from 1Q23.

Targets
  residual_pricing_pp   H card reconstruction, 1Q23-2Q26 (data/processed/q3nowcast/H)
  adr_exfx_yoy_pp       disclosed blended ex-FX ADR (02b_adr_history_extended, adr_yoy_exfx_final)
  adr_reported_yoy_pp   reported blended ADR y/y
  adr_exfx_{na,emea,latam,apac}_pp  regional ex-FX ADR (04_regional_quarterly_wide); NA and EMEA are
                        disclosed-chained from 2Q23 (NA) / 1Q23 (EMEA), LatAm and APAC only from 4Q24,
                        modelled before that: the regional walk-forwards score partly against modelled values

Features: every series in P_series_tidy.csv converted to a calendar-quarter y/y percent (monthly
indexes: y/y then quarter mean; rates: quarter mean; quarterly indexes: y/y on the quarter), then
level and first difference at lags 0 and 1. The 3Q26 reading is the mean of the months in hand.

Run: py -3.13 analysis/src/govdata/P2_backtests.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(HERE, "analysis", "src", "adrq3"))
import I0_protocol as I0  # noqa: E402

OUT = os.path.join(HERE, "data", "processed", "govdata", "P")
QORDER = I0.QORDER
qi = {q: i for i, q in enumerate(QORDER)}
WF_START = "1Q24"


def to_q(period):
    """'2025-07' -> '3Q25'; '2025-Q3' -> '3Q25'."""
    if "-Q" in period:
        y, q = period.split("-Q")
        return f"{q}Q{y[2:]}"
    d = pd.Period(period, "M")
    return f"{(d.month - 1) // 3 + 1}Q{str(d.year)[2:]}"


# ----------------------------------------------------------------------------------------------
# 1. targets
# ----------------------------------------------------------------------------------------------
H = pd.read_csv(os.path.join(HERE, "data", "processed", "q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
hist = pd.read_csv(os.path.join(HERE, "data", "processed", "adr", "02b_adr_history_extended.csv")).set_index("quarter")
reg = pd.read_csv(os.path.join(HERE, "data", "processed", "adr", "04_regional_quarterly_wide.csv")).set_index("quarter")
targets = pd.DataFrame(index=QORDER)
targets["residual_pricing_pp"] = H["residual_pricing_pp"]
targets["adr_exfx_yoy_pp"] = hist["adr_yoy_exfx_final"]
targets["adr_reported_yoy_pp"] = hist["adr_yoy_reported_pct"]
for r in ("na", "emea", "latam", "apac"):
    targets[f"adr_exfx_{r}_pp"] = reg[f"adr_yoy_exfx_{r}_pct"]
targets = targets[(targets.index.map(qi) >= qi["1Q22"]) & (targets.index.map(qi) <= qi["2Q26"])]
TARGET_BASIS = {"adr_exfx_na_pp": "disclosed-chained from 2Q23, modelled 1Q22-1Q23",
                "adr_exfx_emea_pp": "disclosed-chained from 1Q23, modelled 2022",
                "adr_exfx_latam_pp": "disclosed-chained from 4Q24 only, modelled before",
                "adr_exfx_apac_pp": "disclosed-chained from 4Q24 only, modelled before"}

# ----------------------------------------------------------------------------------------------
# 2. features: series -> quarterly y/y
# ----------------------------------------------------------------------------------------------
ser = pd.read_csv(os.path.join(OUT, "P_series_tidy.csv"))

# which series to test, with metadata. (source_prefix or exact name) -> dict
HICP_GEOS = ["EA", "EU27_2020", "DE", "ES", "FR", "IT", "PT", "NL", "EL", "HR", "AT", "IE", "PL", "CH", "NO", "TR", "UK", "SE", "DK", "CZ", "HU", "BE"]
SPPI_GEOS = ["EA20", "EU27_2020", "DE", "ES", "FR", "IT", "PT", "NL", "AT", "SE", "DK", "PL", "UK", "NO", "IE", "HR", "EL"]

FEATURES = {}  # feature -> meta


def feat(name, kind, meta):
    FEATURES[name] = {"kind": kind, **meta}


# Eurostat HICP: RCH_A is already the annual rate
for cp, lab, ac in (("CP112", "accommodation services", "accommodation, all"), ("CP11201", "hotels, motels, inns", "hotel"),
                    ("CP11202", "holiday centres, camping, hostels", "other accommodation"), ("CP11209", "other accommodation services", "other accommodation, incl short-term lets")):
    for g in HICP_GEOS:
        feat(f"hicp_{cp}_{g}_RCH_A", "rate_M", {"source": "eurostat_hicp", "country": g, "region": "emea", "asset_class": ac,
                                              "label": f"HICP {lab}, {g}", "knowable": "yes: Sep flash ~1 Oct, final ~16 Oct"})
# Eurostat SPPI: PCH_SM is y/y on the quarter
for g in SPPI_GEOS:
    feat(f"sppi_I55_{g}_PCH_SM", "rate_Q", {"source": "eurostat_sppi", "country": g, "region": "emea", "asset_class": "accommodation (NACE I55, producer price)",
                                          "label": f"SPPI accommodation I55, {g}", "knowable": "no: 3Q26 publishes Dec 2026"})
# INE Spain: interannual variation rate rows
INE_PICK = {"ine_hdpi_holiday_dwellings_EOT8077": ("holiday dwellings / tourist apartments", "short-term rental (tourist apartments)"),
            "ine_rtapi_rural_EOT12767": ("rural tourism accommodation", "other accommodation (rural)"),
            "ine_hotel_adr_EOT16415": ("hotel ADR, national", "hotel"),
            "ine_hotel_revpar_EOT16471": ("hotel RevPAR, national", "hotel")}
for s in ser[ser.source == "ine_es"].series.unique():
    if s in INE_PICK:
        lab, ac = INE_PICK[s]
        feat(s, "rate_M", {"source": "ine_es", "country": "ES", "region": "emea", "asset_class": ac, "label": f"INE Spain {lab} y/y", "knowable": "yes: Sep release ~23 Oct"})
# campsite index: find the first interannual series code in table 1990
camp = [s for s in ser[ser.source == "ine_es"].series.unique() if s.startswith("ine_tcpi_campsite_")]
if camp:
    codes = sorted(camp, key=lambda x: int(x.split("EOT")[-1]))
    if len(codes) >= 2:
        feat(codes[1], "rate_M", {"source": "ine_es", "country": "ES", "region": "emea", "asset_class": "other accommodation (campsites)", "label": "INE Spain campsite price index y/y", "knowable": "yes"})
# BLS
for sid, lab, ac in (("PCU721110721110", "PPI hotels and motels 721110", "hotel"), ("PCU7211--7211--", "PPI traveler accommodation 7211", "hotel"),
                     ("CUUR0000SEHB02", "CPI other lodging away from home incl hotels, NSA", "hotel (CPI)"), ("CUSR0000SEHB02", "CPI other lodging away from home incl hotels, SA", "hotel (CPI)")):
    feat(f"bls_{sid}", "index_M", {"source": "bls", "country": "US", "region": "na", "asset_class": ac, "label": f"BLS {lab}", "knowable": "yes: Sep PPI/CPI mid-Oct"})
feat("statcan_cpi_traveller_accommodation", "index_M", {"source": "statcan", "country": "CA", "region": "na", "asset_class": "hotel (CPI traveller accommodation)", "label": "StatCan CPI traveller accommodation", "knowable": "yes: Sep CPI ~20 Oct"})
for idx, lab in (("30033", "holiday travel and accommodation"), ("40101", "domestic holiday travel and accommodation"), ("40102", "international holiday travel and accommodation")):
    feat(f"abs_cpi_{idx}_Q", "index_Q", {"source": "abs", "country": "AU", "region": "apac", "asset_class": "holiday travel and accommodation (CPI, bundles airfares)", "label": f"ABS CPI {lab}, quarterly", "knowable": "yes: Sep-quarter CPI 28 Oct"})
    feat(f"abs_cpi_{idx}_M", "abs_splice", {"source": "abs", "country": "AU", "region": "apac", "asset_class": "holiday travel and accommodation (monthly CPI)", "label": f"ABS monthly CPI {lab} (indicator to Sep 2025 spliced with complete monthly CPI)", "knowable": "yes: Aug ~30 Sep, Sep ~28 Oct"})
feat("ibge_ipca_hospedagem_yoy12m", "rate_M", {"source": "ibge", "country": "BR", "region": "latam", "asset_class": "hotel (IPCA hospedagem)", "label": "IBGE IPCA hospedagem 12-month rate", "knowable": "yes: Sep IPCA ~9 Oct"})
feat("bea_export_travel_price", "index_Q", {"source": "fred_bea", "country": "US", "region": "na", "asset_class": "travel exports deflator (inbound visitors' spend)", "label": "BEA exports of travel, price index", "knowable": "yes: 3Q advance 29 Oct"})
feat("bea_import_travel_price", "index_Q", {"source": "fred_bea", "country": "US", "region": "na", "asset_class": "travel imports deflator (US residents abroad)", "label": "BEA imports of travel, price index", "knowable": "yes: 3Q advance 29 Oct"})
feat("ons_cpi_112_accommodation_index", "index_M", {"source": "ons", "country": "UK", "region": "emea", "asset_class": "accommodation, all", "label": "ONS CPI 11.2 accommodation services", "knowable": "yes: Sep CPI ~22 Oct"})
feat("ons_cpi_11201_hotels_index", "index_M", {"source": "ons", "country": "UK", "region": "emea", "asset_class": "hotel", "label": "ONS CPI 11.2.0.1 hotels", "knowable": "yes"})
feat("ons_cpi_11203_other_establishments_index", "index_M", {"source": "ons", "country": "UK", "region": "emea", "asset_class": "other accommodation", "label": "ONS CPI 11.2.0.3 other establishments", "knowable": "yes"})
# Hawaii: the y/y is taken within each report vintage (current month vs the same month a year earlier on the same
# basis). A cross-vintage level series breaks in Aug 2025 when the data provider changed (Transparent -> Lighthouse)
feat("hawaii_vr_adr_state_yoy_reported_pct", "rate_M", {"source": "hawaii_dbedt", "country": "US-HI", "region": "na", "asset_class": "short-term rental (vacation rental ADR)", "label": "Hawaii DBEDT vacation rental ADR y/y, statewide", "knowable": "yes: Aug report ~25 Sep, Sep ~25 Oct"})
for k in ("maui", "oahu", "kauai", "island"):
    feat(f"hawaii_vr_adr_{k}_yoy_reported_pct", "rate_M", {"source": "hawaii_dbedt", "country": "US-HI", "region": "na", "asset_class": "short-term rental (vacation rental ADR)", "label": f"Hawaii vacation rental ADR y/y, {k}", "knowable": "yes"})
feat("japan_cpi_hotel_charges_index", "index_M", {"source": "japan_estat", "country": "JP", "region": "apac", "asset_class": "hotel (CPI hotel charges)", "label": "Japan CPI hotel charges", "knowable": "yes: Aug CPI 19 Sep, Sep 24 Oct"})
for s in ser[ser.source == "nz_statsnz"].series.unique():
    if "ccommodation" in s.lower() and s.endswith(("accommodation_services", "accommodation_services_nan")) or s.lower().endswith("accommodation_services"):
        feat(s, "index_Q", {"source": "nz_statsnz", "country": "NZ", "region": "apac", "asset_class": "accommodation services (CPI)", "label": f"Stats NZ CPI {s.split('_', 3)[-1]}", "knowable": "yes: Sep-quarter CPI ~20 Oct"})
# held BEA PCE price indexes not yet tested against ADR (accommodations, foreign travel)
bea = pd.read_csv(os.path.join(HERE, "data", "raw", "bea", "bea_pce_travel_monthly_2015_2026.csv"))
for sname, lab, ac in (("accommodations", "PCE accommodations price index (hotels plus housing at school)", "accommodation, all"),
                       ("foreign_travel_by_us_residents", "PCE foreign travel by US residents, price index", "travel deflator (outbound)"),
                       ("inbound_foreign_travel_in_us", "PCE inbound foreign travel in US, price index (negative PCE)", "travel deflator (inbound)")):
    b = bea[(bea.series == sname) & (bea.measure == "price_index_2017eq100")]
    for _, x in b.iterrows():
        ser.loc[len(ser)] = {"source": "bea_held", "series": f"bea_pce_{sname}_price", "freq": "M", "period": str(x["date"])[:7], "value": float(x["value"]), "unit": "index"}
    feat(f"bea_pce_{sname}_price", "index_M", {"source": "bea_held", "country": "US", "region": "na", "asset_class": ac, "label": f"BEA {lab}", "knowable": "yes: Aug PCE ~26 Sep"})

# build quarterly y/y panel and the 3Q26 readings
panel = pd.DataFrame(index=targets.index)
readings = []
monthly_yoy = {}
for name, m in FEATURES.items():
    s = ser[ser.series == name].copy()
    if not len(s):
        m["missing"] = True
        continue
    s = s.drop_duplicates("period").set_index("period")["value"].astype(float)
    if m["kind"] == "abs_splice":
        # y/y from the 2017-2025 indicator (suffix _M) and from the complete monthly CPI (suffix _Mc); the newer one wins where both exist
        parts = []
        for suf in ("M", "Mc"):
            z = ser[ser.series == name[:-1] + suf].drop_duplicates("period").set_index("period")["value"].astype(float)
            if not len(z):
                continue
            z.index = pd.PeriodIndex(z.index, freq="M"); z = z.sort_index().reindex(pd.period_range(z.index.min(), z.index.max(), freq="M"))
            parts.append(100 * (z / z.shift(12) - 1))
        if not parts:
            m["missing"] = True
            continue
        yoy = parts[-1].combine_first(parts[0]) if len(parts) == 2 else parts[0]
        m["kind"] = "index_M"
    elif m["kind"] == "index_M":
        s.index = pd.PeriodIndex(s.index, freq="M"); s = s.sort_index()
        full = pd.period_range(s.index.min(), s.index.max(), freq="M")
        s = s.reindex(full)
        yoy = 100 * (s / s.shift(12) - 1)
    elif m["kind"] == "rate_M":
        s.index = pd.PeriodIndex(s.index, freq="M"); s = s.sort_index(); yoy = s
    elif m["kind"] == "index_Q":
        s.index = pd.PeriodIndex([p.replace("-Q", "Q") for p in s.index], freq="Q"); s = s.sort_index()
        s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="Q"))
        yoy = 100 * (s / s.shift(4) - 1)
    else:  # rate_Q
        s.index = pd.PeriodIndex([p.replace("-Q", "Q") for p in s.index], freq="Q"); s = s.sort_index(); yoy = s
    yoy = yoy.dropna()
    if m["kind"].endswith("_M"):
        monthly_yoy[name] = yoy
        q = yoy.groupby(yoy.index.asfreq("Q")).mean()
        q3 = yoy[(yoy.index >= pd.Period("2026-07", "M")) & (yoy.index <= pd.Period("2026-09", "M"))]
        reading = float(q3.mean()) if len(q3) else np.nan
        months_in = ",".join(p.strftime("%b") for p in q3.index)
    else:
        q = yoy
        q3v = yoy.get(pd.Period("2026Q3"), np.nan)
        reading = float(q3v) if np.isfinite(q3v) else np.nan
        months_in = "3Q26 quarter value" if np.isfinite(q3v) else ""
    qlab = pd.Series(q.values, index=[f"{p.quarter}Q{str(p.year)[2:]}" for p in q.index])
    panel[name] = qlab.reindex(panel.index)
    m["first_q"] = qlab.index[0] if len(qlab) else ""
    m["last_period"] = str(yoy.index.max())
    m["hist_quarters_from_1q23"] = int(((qlab.index.map(lambda x: qi.get(x, -1)) >= qi["1Q23"]) & (qlab.index.map(lambda x: qi.get(x, 99)) <= qi["2Q26"])).sum())
    readings.append({"feature": name, "label": m["label"], "source": m["source"], "country": m["country"], "asset_class": m["asset_class"],
                     "reading_3q26_yoy_pct": reading, "months_in": months_in, "last_2q26_full_quarter": float(qlab.get("2Q26", np.nan)),
                     "last_1q26": float(qlab.get("1Q26", np.nan)), "change_2q26_to_3q26_pp": reading - float(qlab.get("2Q26", np.nan)) if np.isfinite(reading) else np.nan,
                     "last_period": m["last_period"], "knowable_before_5nov": m["knowable"]})
panel.to_csv(os.path.join(OUT, "P_feature_quarterly_panel.csv"))
pd.DataFrame(monthly_yoy).to_csv(os.path.join(OUT, "P_feature_monthly_yoy.csv"))
pd.DataFrame(readings).sort_values(["source", "feature"]).to_csv(os.path.join(OUT, "P_readings_3q26.csv"), index=False)

# ----------------------------------------------------------------------------------------------
# 3. tests
# ----------------------------------------------------------------------------------------------
def wf_errors(x, y, start, season_lag=4, min_fit=4):
    """Mirror of I0.walkforward returning per-quarter errors (model, naive) for the jackknife."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    ef, en, ts = [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < min_fit or not np.isfinite(x[t]) or not np.isfinite(y[t]) or not np.isfinite(y[t - 1]):
            continue
        b, a = I0.ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred):
            continue
        ef.append(pred - y[t]); en.append(y[t - 1] - y[t]); ts.append(t)
    return np.array(ef), np.array(en), ts


def jackknife(ef, en):
    if len(ef) < 4:
        return np.nan, np.nan, np.nan
    rats = []
    for i in range(len(ef)):
        m = np.ones(len(ef), bool); m[i] = False
        rats.append(np.sqrt(np.mean(ef[m] ** 2)) / np.sqrt(np.mean(en[m] ** 2)))
    rats = np.array(rats)
    return float(rats.min()), float(rats.max()), int((rats < 1).sum())


tests = []
for name, m in FEATURES.items():
    if m.get("missing") or name not in panel.columns:
        continue
    tlist = ["residual_pricing_pp", "adr_exfx_yoy_pp", "adr_reported_yoy_pp"]
    if m["region"]:
        tlist.append(f"adr_exfx_{m['region']}_pp")
    for transform in ("level", "diff"):
        f = panel[name].astype(float)
        if transform == "diff":
            f = f.diff()
        for lag in (0, 1):
            fl = f.shift(lag)
            for tgt in tlist:
                for window in ("2023Q1+", "2022Q1+"):
                    if tgt == "residual_pricing_pp" and window == "2022Q1+":
                        continue
                    lo = "1Q23" if window == "2023Q1+" else "1Q22"
                    df = pd.DataFrame({"x": fl, "y": targets[tgt]})
                    df = df[df.index.map(qi) >= qi[lo]]
                    both = df.dropna()
                    if len(both) < 6:
                        continue
                    labels = list(df.index)
                    r0, pp, n = I0.perm_p(df.x.values, df.y.values)
                    pr = stats.pearsonr(both.x, both.y)
                    rs = stats.spearmanr(both.x, both.y).correlation
                    start = labels.index(WF_START)
                    wf = I0.walkforward(df.x.values, df.y.values, start) or {}
                    ef, en, ts = wf_errors(df.x.values, df.y.values, start)
                    jk_lo, jk_hi, jk_below = jackknife(ef, en)
                    row = {"feature": name, "label": m["label"], "source": m["source"], "country": m["country"], "asset_class": m["asset_class"],
                           "transform": transform, "lag": lag, "target": tgt, "window": window, "n": int(n),
                           "first_q": both.index[0], "last_q": both.index[-1], "pearson_r": float(pr[0]), "p": float(pr[1]), "spearman_r": float(rs),
                           "perm_p": pp, "knowable_before_print": m["knowable"], "target_basis": TARGET_BASIS.get(tgt, "disclosed")}
                    row.update({k: v for k, v in wf.items() if k not in ("wf_first_t", "wf_last_t")})
                    row["wf_first_q"] = labels[ts[0]] if ts else ""
                    row["wf_last_q"] = labels[ts[-1]] if ts else ""
                    row["jk_ratio_min"], row["jk_ratio_max"], row["jk_n_below_1"] = jk_lo, jk_hi, jk_below
                    tests.append(row)
tests = pd.DataFrame(tests)
for tgt, gg in tests.groupby("target"):
    tests.loc[gg.index, "n_tests_on_target"] = len(gg)
    tests.loc[gg.index, "p_bonferroni"] = np.minimum(1.0, gg.p * len(gg))
tests["flagged_r"] = (tests.pearson_r.abs() > 0.5) & (tests.perm_p < 0.05)
tests["beats_naive"] = (tests.wf_ratio_vs_naive < 1) & (tests.wf_n >= 6)
tests["beats_naive_and_ar1"] = tests.beats_naive & (tests.wf_ratio_vs_ar1 < 1)
tests["survivor_j2"] = tests.flagged_r & tests.beats_naive_and_ar1
# BRIEF verdict at the (feature, transform, lag, target) level: beats naive on both windows
key = ["feature", "transform", "lag", "target"]
bw = tests.groupby(key).apply(lambda g: pd.Series({"beats_short": bool(g[(g.window == "2023Q1+")].beats_naive.any()),
                                                    "beats_long": bool(g[(g.window == "2022Q1+")].beats_naive.any()),
                                                    "has_long": bool((g.window == "2022Q1+").any())}), include_groups=False).reset_index()
tests = tests.merge(bw, on=key, how="left")
tests["beats_both_windows"] = tests.beats_short & tests.beats_long
tests = tests.sort_values(["target", "wf_ratio_vs_naive"])
tests.to_csv(os.path.join(OUT, "P_backtests.csv"), index=False)

# feature metadata for P3
meta = pd.DataFrame([{"feature": k, **{kk: vv for kk, vv in v.items() if kk != "kind"}, "kind": v["kind"]} for k, v in FEATURES.items()])
meta.to_csv(os.path.join(OUT, "P_feature_meta.csv"), index=False)

pd.set_option("display.width", 250)
print("features", len(FEATURES), "missing", sum(1 for v in FEATURES.values() if v.get("missing")), "tests", len(tests))
print(tests.groupby("target").agg(tests=("feature", "size"), flagged=("flagged_r", "sum"), beat_naive=("beats_naive", "sum"),
                                  beat_naive_ar1=("beats_naive_and_ar1", "sum"), best=("wf_ratio_vs_naive", "min")).round(3).to_string())
cols = ["feature", "transform", "lag", "target", "window", "n", "pearson_r", "perm_p", "p_bonferroni", "wf_n", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "jk_ratio_min", "jk_ratio_max", "beats_both_windows"]
print("\nbest 40 by naive ratio (wf_n>=6)\n", tests[tests.wf_n >= 6].sort_values("wf_ratio_vs_naive").head(40)[cols].round(3).to_string())
print("\nreadings\n", pd.DataFrame(readings)[["feature", "reading_3q26_yoy_pct", "months_in", "last_2q26_full_quarter", "last_period"]].round(2).to_string())
