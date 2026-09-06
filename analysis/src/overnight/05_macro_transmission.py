"""
05_macro_transmission.py  (overnight workstream 05, 6-7 Sep 2026)

Half A of the macro workstream: how macro variables have transmitted into ABNB nights,
ADR (ex-FX and FX), revenue and margin, and what that implies for 3Q26..4Q27.

Reads
  data/processed/abnb_driver_history_quarterly.csv          quarterly KPIs 1Q21..2Q26 (nights, GBV, ADR, revenue, EBITDA, cost lines)
  data/processed/predictive/03_quarterly_panel.csv          aligned macro panel 2019Q1..2026Q3 (ADR ex-FX and ADR FX effect from letters,
                                                            BEA travel lines, CPI, claims, FX). Only the target columns and the BEA columns are
                                                            reused; every FRED series is re-pulled here so the 3Q26 quarter-to-date values are fresh.
  theos-past-research/research/guidance/data/normalized/quarterly_actuals.csv   reported vs constant-currency revenue growth -> revenue FX points
  data/processed/eurostat_platform_nights_monthly.csv       EU27 platform nights (Eurostat tour_ce_*), monthly to 2026-03
  FRED keyless CSVs  https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES  (cached under data/processed/overnight/05_fred_cache/)

Writes (data/processed/overnight/)
  05_macro_quarterly_panel.csv   the quarterly panel used here (targets + macro transforms), 2019Q1..2026Q3 (3Q26 partial, flagged)
  05_macro_tests_all.csv         every pair tested (macro x lag x target x window), n, slope, r, p, Spearman, permutation p, LOO RMSE vs naive
  05_macro_sensitivities.csv     the deliverable: one row per macro variable x target with effect size, window, n, method, confidence
  05_fx_schedule.csv             fitted FX mechanism applied to three EUR/USD paths, 3Q25..4Q27: ADR FX effect and revenue FX points by quarter
  05_regional_growth.csv         regional nights growth buckets from the letters (3Q24..2Q26) with Eurostat EU27 platform nights and BEA travel
  05_crossborder_share.csv       cross-border share of gross nights as disclosed in letters (last disclosure 1Q24)
  05_shock_episodes.csv          the 2022 rate shock, 2024 US softness, spring-2025 tariff shock and 1Q26 Middle East conflict: guided vs printed vs stock
  05_reaction_by_accel.csv       day-1 / 20-day excess return split by the sign of nights acceleration in the reported quarter
  05_macro_scenarios.csv         Half B: three macro scenarios with probabilities, implied KPIs, likely guidance language and reaction analogues
Figures (analysis/figures/overnight/)
  05_fx_mechanism.png, 05_macro_vs_nights.png, 05_sensitivity_bars.png

Run:  py -3.13 analysis/src/overnight/05_macro_transmission.py
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
FIG = ROOT / "analysis" / "figures" / "overnight"
CACHE = OUT / "05_fred_cache"
for d in (OUT, FIG, CACHE):
    d.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
RNG = np.random.default_rng(20260906)

# ----------------------------------------------------------------------------------------------
# 1. FRED pulls (keyless CSV), quarterly aggregation and transforms
# ----------------------------------------------------------------------------------------------
# name -> (series id, transform). yoy = % change on 4-quarter lag of the quarterly mean; d4 = 4-quarter difference (pp)
FRED = {
    "usd_broad": ("DTWEXBGS", "yoy"),        # nominal broad trade-weighted USD (up = stronger USD)
    "eurusd": ("DEXUSEU", "yoy"),            # USD per EUR (up = weaker USD)
    "gbpusd": ("DEXUSUK", "yoy"),
    "usdcad": ("DEXCAUS", "yoy"),            # CAD per USD (up = weaker CAD)
    "usdmxn": ("DEXMXUS", "yoy"),
    "usdbrl": ("DEXBZUS", "yoy"),
    "usdjpy": ("DEXJPUS", "yoy"),
    "umcsent": ("UMCSENT", "d4"),            # Michigan sentiment, index points y/y
    "mich_infl_exp": ("MICH", "d4"),         # Michigan 1y inflation expectation, pp y/y
    "pce_services": ("PCES", "yoy"),         # nominal PCE services
    "real_pce": ("PCEC96", "yoy"),
    "real_dpi": ("DSPIC96", "yoy"),
    "cpi_all": ("CPIAUCSL", "yoy"),
    "cpi_lodging": ("CUSR0000SEHB", "yoy"),
    "cpi_airfare": ("CUSR0000SETG01", "yoy"),
    "unrate": ("UNRATE", "d4"),              # pp y/y
    "initial_claims": ("ICSA", "yoy"),
    "payrolls": ("PAYEMS", "yoy"),
    "emp_leisure_hosp": ("USLAH", "yoy"),
    "fed_funds": ("FEDFUNDS", "d4"),         # pp y/y
    "ust10y": ("DGS10", "d4"),
    "ust2y": ("DGS2", "d4"),
    "consumer_credit": ("TOTALSL", "yoy"),
    "saving_rate": ("PSAVERT", "d4"),
    "retail_sales_xauto": ("RSXFS", "yoy"),
    "air_rpm": ("AIRRPMTSID11", "yoy"),      # BTS air revenue passenger miles, ~3-month lag
    "wti": ("DCOILWTICO", "yoy"),
    "jet_fuel_gulf": ("WJFUELUSGULF", "yoy"),
}


def fetch_fred(sid: str) -> pd.Series:
    p = CACHE / f"{sid}.csv"
    if not p.exists() or p.stat().st_size < 200:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=60)
        r.raise_for_status()
        p.write_text(r.text)
        time.sleep(0.3)
    df = pd.read_csv(p)
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"].dropna()


def to_quarterly(s: pd.Series) -> pd.Series:
    q = s.resample("QE").mean()
    q.index = q.index.to_period("Q")
    return q


fred_q = {}
fred_last = {}
for name, (sid, tf) in FRED.items():
    s = fetch_fred(sid)
    fred_last[name] = (sid, s.index.max().date().isoformat(), float(s.iloc[-1]))
    q = to_quarterly(s)
    fred_q[name] = q.pct_change(4) * 100 if tf == "yoy" else q.diff(4)
    fred_q[name + "_level"] = q
macro = pd.DataFrame(fred_q)

# ----------------------------------------------------------------------------------------------
# 2. Targets: KPI history, ADR ex-FX / FX effect (letters, via the 03 panel), revenue FX points (Theo)
# ----------------------------------------------------------------------------------------------
dh = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
dh["q"] = pd.PeriodIndex([f"{r.year}Q{r.q}" for r in dh.itertuples()], freq="Q")
dh = dh.set_index("q").sort_index()
tgt = pd.DataFrame(index=dh.index)
tgt["nights_yoy"] = dh["nights_m"].pct_change(4) * 100
tgt["nights_accel"] = tgt["nights_yoy"].diff(1)
tgt["gbv_yoy"] = dh["gbv_musd"].pct_change(4) * 100
tgt["adr_yoy"] = dh["adr"].pct_change(4) * 100
tgt["rev_yoy"] = dh["revenue_musd"].pct_change(4) * 100
tgt["ebitda_margin"] = dh["adj_ebitda_margin_pct"]
tgt["ebitda_margin_chg"] = tgt["ebitda_margin"].diff(4)
tgt["sm_pct_rev"] = dh["sales_and_marketing_musd"] / dh["revenue_musd"] * 100
tgt["sm_pct_chg"] = tgt["sm_pct_rev"].diff(4)
tgt["ops_pct_rev"] = dh["operations_and_support_musd"] / dh["revenue_musd"] * 100
tgt["ops_pct_chg"] = tgt["ops_pct_rev"].diff(4)

panel03 = pd.read_csv(ROOT / "data/processed/predictive/03_quarterly_panel.csv")
panel03["q"] = pd.PeriodIndex(panel03["quarter"], freq="Q")
panel03 = panel03.set_index("q")
for c in ["adr_exfx_yoy", "adr_fx_effect", "bea_accom_nominal", "bea_accom_real", "bea_hotels_nominal",
          "bea_inbound_foreign_travel", "bea_outbound_us_travel", "vehicle_miles"]:
    tgt[c] = panel03[c]

theo = pd.read_csv(ROOT / "theos-past-research/research/guidance/data/normalized/quarterly_actuals.csv")
theo = theo[theo["metric_code"] == "revenue"].copy()
theo["q"] = pd.PeriodIndex(theo["fiscal_period"], freq="Q")
theo = theo.set_index("q")
tgt["rev_fx_pts"] = (theo["yoy_growth_reported"] - theo["yoy_growth_constant_currency"]) * 100
tgt["rev_cc_yoy"] = theo["yoy_growth_constant_currency"] * 100

# Eurostat EU27 platform nights, quarterly y/y (monthly sums)
eu = pd.read_csv(ROOT / "data/processed/eurostat_platform_nights_monthly.csv")
eu["month"] = pd.to_datetime(eu["month"])
eu_q = eu.set_index("month")[["eu27_nights", "eu27_domestic", "eu27_foreign"]].resample("QE").sum(min_count=3)
eu_q.index = eu_q.index.to_period("Q")
eu_yoy = eu_q.pct_change(4) * 100
eu_yoy.columns = ["eu27_platform_nights_yoy", "eu27_platform_domestic_yoy", "eu27_platform_foreign_yoy"]

panel = tgt.join(macro, how="outer").join(eu_yoy, how="left")
panel = panel[(panel.index >= pd.Period("2019Q1", "Q")) & (panel.index <= pd.Period("2026Q3", "Q"))]
panel["partial_quarter"] = panel.index == pd.Period("2026Q3", "Q")
panel.index.name = "quarter"
panel.round(3).to_csv(OUT / "05_macro_quarterly_panel.csv")

# ----------------------------------------------------------------------------------------------
# 3. Pair tests
# ----------------------------------------------------------------------------------------------
BEA_VARS = {
    "bea_accom_nominal": "BEA PCE accommodations nominal y/y",
    "bea_inbound_foreign_travel": "BEA foreign travel in the US (inbound) y/y",
    "bea_outbound_us_travel": "BEA US travel abroad (outbound) y/y",
}
LABELS = {
    "usd_broad": "USD broad trade-weighted y/y (%)", "eurusd": "EUR/USD y/y (%)", "gbpusd": "GBP/USD y/y (%)",
    "usdcad": "USD/CAD y/y (%)", "usdmxn": "USD/MXN y/y (%)", "usdbrl": "USD/BRL y/y (%)", "usdjpy": "USD/JPY y/y (%)",
    "umcsent": "Michigan sentiment, change y/y (pts)", "mich_infl_exp": "Michigan 1y inflation expectation, change y/y (pp)",
    "pce_services": "PCE services nominal y/y (%)", "real_pce": "Real PCE y/y (%)", "real_dpi": "Real disposable income y/y (%)",
    "cpi_all": "CPI all items y/y (%)", "cpi_lodging": "CPI lodging away from home y/y (%)", "cpi_airfare": "CPI airline fares y/y (%)",
    "unrate": "Unemployment rate, change y/y (pp)", "initial_claims": "Initial jobless claims y/y (%)", "payrolls": "Nonfarm payrolls y/y (%)",
    "emp_leisure_hosp": "Leisure & hospitality employment y/y (%)", "fed_funds": "Fed funds, change y/y (pp)", "ust10y": "10y Treasury, change y/y (pp)",
    "ust2y": "2y Treasury, change y/y (pp)", "consumer_credit": "Consumer credit outstanding y/y (%)", "saving_rate": "Personal saving rate, change y/y (pp)",
    "retail_sales_xauto": "Retail sales ex-auto y/y (%)", "air_rpm": "Air revenue passenger miles y/y (%)", "wti": "WTI crude y/y (%)",
    "jet_fuel_gulf": "Gulf Coast jet fuel y/y (%)", "eu27_platform_nights_yoy": "Eurostat EU27 platform nights y/y (%)",
}
LABELS.update(BEA_VARS)
MACROS = list(FRED.keys()) + list(BEA_VARS.keys()) + ["eu27_platform_nights_yoy"]
TARGETS = {
    "nights_yoy": "nights y/y (%)", "nights_accel": "nights acceleration (pp q/q)", "gbv_yoy": "GBV y/y (%)",
    "adr_yoy": "ADR y/y reported (%)", "adr_exfx_yoy": "ADR y/y ex-FX (%)", "adr_fx_effect": "FX effect on ADR (pp)",
    "rev_yoy": "revenue y/y (%)", "rev_cc_yoy": "revenue y/y constant currency (%)", "rev_fx_pts": "FX effect on revenue (pp)",
    "ebitda_margin_chg": "Adj. EBITDA margin change y/y (pp)", "sm_pct_chg": "S&M % revenue change y/y (pp)",
}
WINDOWS = {"post22": pd.Period("2023Q1", "Q"), "ex21": pd.Period("2022Q1", "Q")}
FROM24 = pd.Period("2024Q1", "Q")
END = pd.Period("2026Q2", "Q")


def pair_stats(x: pd.Series, y: pd.Series) -> dict | None:
    m = x.notna() & y.notna()
    x, y = x[m].values.astype(float), y[m].values.astype(float)
    n = len(x)
    if n < 7 or np.std(x) == 0 or np.std(y) == 0:
        return None
    lr = stats.linregress(x, y)
    rho = stats.spearmanr(x, y).correlation
    # permutation p on |r|
    xs = (x - x.mean()) / x.std()
    ys = (y - y.mean()) / y.std()
    perms = np.array([RNG.permutation(ys) for _ in range(N_PERM)])
    rperm = perms @ xs / n
    perm_p = (np.sum(np.abs(rperm) >= abs(lr.rvalue)) + 1) / (N_PERM + 1)
    # leave-one-out linear nowcast vs benchmarks
    preds = np.empty(n)
    mean_preds = np.empty(n)
    for i in range(n):
        mk = np.arange(n) != i
        b = np.polyfit(x[mk], y[mk], 1)
        preds[i] = np.polyval(b, x[i])
        mean_preds[i] = y[mk].mean()
    loo = float(np.sqrt(np.mean((y - preds) ** 2)))
    loo_mean = float(np.sqrt(np.mean((y - mean_preds) ** 2)))
    naive = float(np.sqrt(np.mean((y[1:] - y[:-1]) ** 2)))
    return dict(n=n, slope=lr.slope, intercept=lr.intercept, r=lr.rvalue, p=lr.pvalue, spearman=rho,
                perm_p=perm_p, loo_rmse=loo, naive_rmse=naive, loo_mean_rmse=loo_mean)


rows = []
for mvar in MACROS:
    for lag in (0, 1):
        x_full = panel[mvar].shift(lag)
        for tv in TARGETS:
            y_full = panel[tv]
            for wname, start in WINDOWS.items():
                sel = (panel.index >= start) & (panel.index <= END)
                st = pair_stats(x_full[sel], y_full[sel])
                if st is None:
                    continue
                sel24 = (panel.index >= FROM24) & (panel.index <= END)
                m24 = x_full[sel24].notna() & y_full[sel24].notna()
                r24 = float(np.corrcoef(x_full[sel24][m24], y_full[sel24][m24])[0, 1]) if m24.sum() >= 6 else np.nan
                # first-difference check: if the level relationship is a shared 2023-normalisation trend, the
                # quarter-on-quarter change relationship collapses. Real transmission survives differencing.
                xd, yd = x_full.diff(), y_full.diff()
                md = xd[sel].notna() & yd[sel].notna()
                rd = float(np.corrcoef(xd[sel][md], yd[sel][md])[0, 1]) if md.sum() >= 7 else np.nan
                rows.append(dict(macro=mvar, macro_label=LABELS.get(mvar, mvar), lag=lag, target=tv, target_label=TARGETS[tv],
                                 window=wname, r_from2024=r24, n_from2024=int(m24.sum()), r_diff=rd, n_diff=int(md.sum()), **st))
tests = pd.DataFrame(rows)
tests.round(4).to_csv(OUT / "05_macro_tests_all.csv", index=False)
n_tests = len(tests)
print(f"pairs tested: {n_tests}  (macros {len(MACROS)} x lags 2 x targets {len(TARGETS)} x windows 2, less missing)")

# ----------------------------------------------------------------------------------------------
# 4. Sensitivity table (deliverable)
# ----------------------------------------------------------------------------------------------
MECHANICAL = {("usd_broad", "adr_fx_effect"), ("eurusd", "adr_fx_effect"), ("gbpusd", "adr_fx_effect"),
              ("usd_broad", "adr_yoy"), ("eurusd", "adr_yoy"), ("usd_broad", "rev_fx_pts"), ("eurusd", "rev_fx_pts"),
              ("gbpusd", "rev_fx_pts"), ("usd_broad", "rev_yoy"), ("eurusd", "rev_yoy")}


def confidence(row_post, row_ex, mech: bool) -> tuple[str, str]:
    """Rule-based confidence; returns (confidence, reason)."""
    if row_post is None:
        return "none", "no post-2022 test (insufficient overlap)"
    r, pp = row_post["r"], row_post["perm_p"]
    r24 = row_post["r_from2024"]
    rd = row_post["r_diff"]
    beats_naive = row_post["loo_rmse"] < row_post["naive_rmse"]
    beats_mean = row_post["loo_rmse"] < row_post["loo_mean_rmse"]
    same_sign = (row_ex is not None) and np.sign(row_ex["r"]) == np.sign(r) and abs(row_ex["r"]) >= 0.3
    # Artefact guards. (a) sub-sample: does the relationship survive dropping the 2023 normalisation quarters?
    #                  (b) differencing: does the q/q change relationship survive? A shared downward trend
    #                      (disinflation, rate normalisation, travel re-opening) produces a high level r and a
    #                      near-zero difference r. Mechanical FX pairs pass both. See research/notes/predictive/
    #                      03_macro-altdata-nowcast.md finding 2 (CPI "nowcasts" nights as well as lodging spend does).
    sub_flag = np.isnan(r24) or abs(r24) < 0.40 or np.sign(r24) != np.sign(r)
    diff_flag = np.isnan(rd) or abs(rd) < 0.35 or np.sign(rd) != np.sign(r)
    trend_flag = (abs(r) >= 0.6) and (sub_flag or diff_flag)
    if abs(r) >= 0.8 and pp < 0.01 and beats_naive and beats_mean and same_sign and not trend_flag and mech:
        return "high", "|r|>=0.8, perm p<0.01, LOO beats both benchmarks, sign stable, survives from-2024 and first-difference checks, mechanical"
    if abs(r) >= 0.8 and pp < 0.01 and beats_naive and beats_mean and same_sign and not trend_flag:
        return "medium", "|r|>=0.8, passes all checks including differencing, but no mechanical story; treat as a hypothesis"
    if trend_flag:
        which = []
        if sub_flag:
            which.append(f"r from 2024 {r24:+.2f}")
        if diff_flag:
            which.append(f"r on q/q differences {rd:+.2f}")
        return "none", f"common-trend artefact: r post-2022 {r:+.2f} but " + " and ".join(which)
    if abs(r) >= 0.6 and pp < 0.05 and beats_mean and same_sign and not (sub_flag and diff_flag):
        return "medium", f"|r|>=0.6, perm p<0.05, LOO beats mean, sign stable; survives {'the from-2024' if not sub_flag else 'the differencing'} check"
    if abs(r) >= 0.4 and pp < 0.10:
        return "low", "|r|>=0.4, perm p<0.10; fails at least one stability or artefact check"
    return "none", f"|r| {abs(r):.2f}, perm p {pp:.2f}"


SENS_TARGETS = ["nights_yoy", "nights_accel", "adr_exfx_yoy", "adr_fx_effect", "rev_yoy", "rev_fx_pts", "ebitda_margin_chg", "sm_pct_chg"]
# margin chain constants from the margin bridge (research/notes/2026-09-05_margin-drivers.md, FY2026 base sensitivities)
CHAIN = {"nights": 0.35, "adr_exfx": 0.46, "fx": 0.47, "take": 0.64}  # margin points per +1 pt of growth (take: 10 bps take rate = 0.75% revenue = +0.48 pts)
sens_rows = []
for mvar in MACROS:
    sub = tests[tests["macro"] == mvar]
    per_target = {}
    for tv in SENS_TARGETS:
        cand = sub[(sub["target"] == tv) & (sub["window"] == "post22")]
        if cand.empty:
            per_target[tv] = None
            continue
        # pick the lag with the largest |r| among those that survive the first-difference check; if no lag
        # survives, take the largest |r| (it will be labelled an artefact below rather than silently promoted)
        clean = cand[(cand["r_diff"].abs() >= 0.35) & (np.sign(cand["r_diff"]) == np.sign(cand["r"]))]
        pool = clean if not clean.empty else cand
        best = pool.loc[pool["r"].abs().idxmax()]
        ex = sub[(sub["target"] == tv) & (sub["window"] == "ex21") & (sub["lag"] == best["lag"])]
        exrow = ex.iloc[0] if not ex.empty else None
        conf, reason = confidence(best, exrow, (mvar, tv) in MECHANICAL)
        per_target[tv] = (best, exrow, conf, reason)
    for tv in SENS_TARGETS:
        v = per_target[tv]
        if v is None:
            continue
        best, exrow, conf, reason = v
        sens_rows.append(dict(
            macro=mvar, macro_label=LABELS.get(mvar, mvar), target=tv, target_label=TARGETS[tv],
            effect_per_unit=best["slope"], effect_unit=f"{TARGETS[tv]} per +1 unit of macro",
            lag_quarters=int(best["lag"]), window="2023Q1-2026Q2", n=int(best["n"]), r=best["r"], spearman=best["spearman"],
            perm_p=best["perm_p"], loo_rmse=best["loo_rmse"], naive_rmse=best["naive_rmse"], loo_mean_rmse=best["loo_mean_rmse"],
            r_ex2021=(exrow["r"] if exrow is not None else np.nan), n_ex2021=(int(exrow["n"]) if exrow is not None else np.nan),
            r_from2024=best["r_from2024"], r_diff_qoq=best["r_diff"],
            method="OLS on quarterly y/y (or 4q change) vs KPI; LOO nowcast vs naive-last and LOO-mean; 1000-shuffle permutation p; two artefact guards (r from 2024Q1; r on q/q first differences)",
            confidence=conf, confidence_reason=reason))
sens = pd.DataFrame(sens_rows)
# chain-implied margin effect: macro -> (nights, ADR ex-FX, FX) -> margin, using the margin-bridge constants, only for medium/high rows
chain = {}
for mvar in MACROS:
    s = sens[sens["macro"] == mvar].set_index("target")
    tot, parts = 0.0, []
    for tv, key in (("nights_yoy", "nights"), ("adr_exfx_yoy", "adr_exfx"), ("adr_fx_effect", "fx")):
        if tv in s.index and s.loc[tv, "confidence"] in ("medium", "high"):
            tot += CHAIN[key] * s.loc[tv, "effect_per_unit"]
            parts.append(f"{key}:{CHAIN[key]}x{s.loc[tv, 'effect_per_unit']:+.2f}")
    chain[mvar] = (tot, "; ".join(parts) if parts else "no medium/high channel")
sens["margin_effect_via_chain_pp"] = sens["macro"].map(lambda m: chain[m][0])
sens["margin_chain_detail"] = sens["macro"].map(lambda m: chain[m][1])
sens.round(4).to_csv(OUT / "05_macro_sensitivities.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 5. FX mechanism and forward schedule
# ----------------------------------------------------------------------------------------------
def fit(xcol, ycol, start, lag=0):
    sel = (panel.index >= start) & (panel.index <= END)
    x = panel[xcol].shift(lag)[sel]
    y = panel[ycol][sel]
    st = pair_stats(x, y)
    return st


fx_fits = {}
for start_name, start in (("post22", WINDOWS["post22"]), ("ex21", WINDOWS["ex21"])):
    fx_fits[("adr_fx", "usd_broad", 0, start_name)] = fit("usd_broad", "adr_fx_effect", start)
    fx_fits[("adr_fx", "eurusd", 0, start_name)] = fit("eurusd", "adr_fx_effect", start)
    for lag in (0, 1, 2):
        fx_fits[("rev_fx", "usd_broad", lag, start_name)] = fit("usd_broad", "rev_fx_pts", start, lag)
        fx_fits[("rev_fx", "eurusd", lag, start_name)] = fit("eurusd", "rev_fx_pts", start, lag)
# 2-quarter average of USD y/y (current and prior quarter) for revenue FX, which is recognised at check-in on bookings made earlier
panel["usd_broad_avg01"] = (panel["usd_broad"] + panel["usd_broad"].shift(1)) / 2
panel["eurusd_avg01"] = (panel["eurusd"] + panel["eurusd"].shift(1)) / 2
panel["eurusd_avg12"] = (panel["eurusd"].shift(1) + panel["eurusd"].shift(2)) / 2
panel["eurusd_avg012"] = (panel["eurusd"] + panel["eurusd"].shift(1) + panel["eurusd"].shift(2)) / 3
panel["usd_broad_avg12"] = (panel["usd_broad"].shift(1) + panel["usd_broad"].shift(2)) / 2
for start_name, start in (("post22", WINDOWS["post22"]), ("ex21", WINDOWS["ex21"])):
    fx_fits[("rev_fx", "usd_broad_avg01", 0, start_name)] = fit("usd_broad_avg01", "rev_fx_pts", start)
    fx_fits[("rev_fx", "usd_broad_avg12", 0, start_name)] = fit("usd_broad_avg12", "rev_fx_pts", start)
    for drv_name in ("eurusd_avg01", "eurusd_avg12", "eurusd_avg012"):
        fx_fits[("rev_fx", drv_name, 0, start_name)] = fit(drv_name, "rev_fx_pts", start)
fxf = pd.DataFrame([dict(target=k[0], driver=k[1], lag=k[2], window=k[3], **v) for k, v in fx_fits.items() if v])
fxf.round(4).to_csv(OUT / "05_fx_fits.csv", index=False)
print("\nFX fits:")
print(fxf[["target", "driver", "lag", "window", "n", "slope", "intercept", "r", "loo_rmse", "naive_rmse"]].round(3).to_string(index=False))

# beta of broad USD y/y to EUR/USD y/y (2015Q1-2026Q2) so an EUR/USD path can be turned into a broad-dollar path
sel = (panel.index >= pd.Period("2015Q1", "Q")) & (panel.index <= END)
beta = stats.linregress(panel["eurusd"][sel].dropna(), panel["usd_broad"][sel].dropna())
print(f"\nusd_broad y/y = {beta.intercept:.2f} + {beta.slope:.2f} x eurusd y/y  (r {beta.rvalue:.2f}, n {sel.sum()})")

# chosen coefficients
a_adr = fx_fits[("adr_fx", "eurusd", 0, "ex21")]      # ADR FX effect from EUR/USD (r 0.99 in note 03; re-estimated here)
a_adr_usd = fx_fits[("adr_fx", "usd_broad", 0, "ex21")]
rev_candidates = fxf[(fxf["target"] == "rev_fx") & (fxf["window"] == "ex21")].sort_values("loo_rmse")
best_rev = rev_candidates.iloc[0]
# Out-of-sample check on the one forward observation we have: the 2Q26 letter (7 Aug 2026) guides Q3 2026
# revenue growth of 15-17% "inclusive of an approximate three percentage point FX tailwind after factoring in
# our hedging program". Score each candidate spec on its 3Q26 prediction against that +3.0 pp.
GUIDE_3Q26_REV_FX = 3.0
DRV = {"usd_broad": panel["usd_broad"], "eurusd": panel["eurusd"], "usd_broad_avg01": panel["usd_broad_avg01"],
       "usd_broad_avg12": panel["usd_broad_avg12"], "eurusd_avg01": panel["eurusd_avg01"],
       "eurusd_avg12": panel["eurusd_avg12"], "eurusd_avg012": panel["eurusd_avg012"]}
Q3P = pd.Period("2026Q3", "Q")
rc = rev_candidates.copy()
rc["pred_3q26"] = [row["intercept"] + row["slope"] * DRV[row["driver"]].shift(int(row["lag"])).loc[Q3P] for _, row in rc.iterrows()]
rc["err_vs_guide"] = (rc["pred_3q26"] - GUIDE_3Q26_REV_FX).abs()
print("")
print("revenue-FX specs scored against the 3Q26 guide (+3.0 pp FX after hedging, 2Q26 letter):")
print(rc[["driver", "lag", "n", "slope", "intercept", "r", "loo_rmse", "pred_3q26", "err_vs_guide"]].round(2).to_string(index=False))
# Forecasting spec: among specs within 1.0 pp of the guide, take the lowest LOO RMSE. Revenue is recognised at
# check-in on bookings made one to two quarters earlier and the hedging programme locks rates forward, so the
# lagged specs are the ones with a mechanism behind them; the contemporaneous spec fits the in-sample
# correlation better but predicts a negative FX effect for a quarter management has already called about +3 pp.
best_rev_insample = rev_candidates.iloc[0]
elig = rc[rc["err_vs_guide"] <= 1.0]
best_rev = (elig if not elig.empty else rc).sort_values("loo_rmse").iloc[0]
_contemp_pred = float(rc[(rc["driver"] == best_rev_insample["driver"]) & (rc["lag"] == best_rev_insample["lag"])]["pred_3q26"].iloc[0])
print("")
print(f"revenue FX forecasting spec: {best_rev['driver']} lag {int(best_rev['lag'])}: slope {best_rev['slope']:.3f}, intercept {best_rev['intercept']:.2f}, r {best_rev['r']:.2f}, LOO {best_rev['loo_rmse']:.2f} vs naive {best_rev['naive_rmse']:.2f}; 3Q26 prediction {best_rev['pred_3q26']:+.2f} pp vs guide +3.0")
print(f"   best in-sample spec {best_rev_insample['driver']} lag {int(best_rev_insample['lag'])} (r {best_rev_insample['r']:.2f}) predicts {_contemp_pred:+.2f} pp for 3Q26; carried in the schedule as revenue_fx_fit_contemp_pp")

# EUR/USD paths: actual quarterly means through 2Q26, 3Q26 quarter-to-date, then three paths
eur_lvl = panel["eurusd_level"].copy()
usd_lvl = panel["usd_broad_level"].copy()
qtd_eur = float(eur_lvl.loc[pd.Period("2026Q3", "Q")])
qtd_usd = float(usd_lvl.loc[pd.Period("2026Q3", "Q")])
future_q = [pd.Period(p, "Q") for p in ("2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4")]
PATHS = {
    # Reuters FX poll, 2 Sep 2026 (55-66 strategists, via Yahoo Finance syndication): EUR/USD median 1.16 at 3m,
    # 1.17 at 6m, 1.18 at 12m. Spot was 1.1614 on 4 Sep 2026. Interpolated across the five forward quarters.
    "consensus": [1.160, 1.165, 1.170, 1.175, 1.180],
    # The dollar-bull camp in the Exchange Rates UK bank survey (23 Aug 2026, ~25 banks): JPMorgan and HSBC 1.10,
    # Goldman 1.12, Citi 1.13-1.14, all for 2Q27. Consistent with the Fed hiking into the energy shock while
    # Hormuz stays contested and safe-haven flows persist (EUR/USD averaged 1.09 in 1Q25, so this is not a stretch).
    "strong_usd": [1.130, 1.100, 1.090, 1.090, 1.100],
    # The euro-bull camp in the same survey: Nomura 1.22 (1Q27) and 1.25 (4Q27), Scotiabank 1.20-1.21,
    # UBS 1.18-1.20. Consistent with the EIA STEO oil path (Brent to $69 in 2027) and a Fed that turns first.
    "weak_usd": [1.190, 1.210, 1.230, 1.240, 1.250],
}
def _realised(q: pd.Period) -> float:
    """Fraction of quarter q's EUR/USD quarterly average that is already observed at the quote date."""
    if q <= pd.Period("2026Q2", "Q"):
        return 1.0
    if q == pd.Period("2026Q3", "Q"):
        # daily quotes to 2026-08-28 cover roughly two of the three months of 3Q26
        return 0.67
    return 0.0


sched_rows = []
for pname, lv in PATHS.items():
    e = eur_lvl.copy()
    for q, v in zip(future_q, lv):
        e.loc[q] = v
    e = e.sort_index()
    e_yoy = e.pct_change(4) * 100
    # implied broad USD y/y from the beta (3Q26 uses the actual quarter-to-date)
    u_yoy = beta.intercept + beta.slope * e_yoy
    u_yoy.loc[:pd.Period("2026Q3", "Q")] = panel["usd_broad"].loc[:pd.Period("2026Q3", "Q")]
    e_yoy_avg = (e_yoy + e_yoy.shift(1)) / 2
    u_yoy_avg = (u_yoy + u_yoy.shift(1)) / 2
    drv = {"usd_broad": u_yoy, "eurusd": e_yoy, "usd_broad_avg01": u_yoy_avg, "eurusd_avg01": e_yoy_avg,
           "usd_broad_avg12": (u_yoy.shift(1) + u_yoy.shift(2)) / 2,
           "eurusd_avg12": (e_yoy.shift(1) + e_yoy.shift(2)) / 2, "eurusd_avg012": (e_yoy + e_yoy.shift(1) + e_yoy.shift(2)) / 3}
    x_rev = drv[best_rev["driver"]].shift(int(best_rev["lag"]))
    alt = fx_fits[("rev_fx", best_rev_insample["driver"], int(best_rev_insample["lag"]), "ex21")]
    x_rev_alt = drv[best_rev_insample["driver"]].shift(int(best_rev_insample["lag"]))
    for q in [pd.Period(p, "Q") for p in ("2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3")] + future_q:
        actual_adr = panel["adr_fx_effect"].get(q, np.nan)
        actual_rev = panel["rev_fx_pts"].get(q, np.nan)
        sched_rows.append(dict(
            path=pname, quarter=str(q), eurusd_level=e.loc[q], eurusd_yoy_pct=e_yoy.loc[q], usd_broad_yoy_pct=u_yoy.loc[q],
            adr_fx_effect_fit_eur_pp=a_adr["intercept"] + a_adr["slope"] * e_yoy.loc[q],
            adr_fx_effect_fit_usd_pp=a_adr_usd["intercept"] + a_adr_usd["slope"] * u_yoy.loc[q],
            revenue_fx_fit_pp=best_rev["intercept"] + best_rev["slope"] * x_rev.loc[q],
            revenue_fx_fit_contemp_pp=alt["intercept"] + alt["slope"] * x_rev_alt.loc[q],
            adr_fx_effect_actual_pp=actual_adr, revenue_fx_actual_pp=actual_rev,
            # how much of the revenue-FX driver for this quarter is already observed rather than assumed:
            # the spec uses EUR/USD y/y in the two prior quarters, and FX through 2026Q3 is realised (3Q26
            # itself is about two thirds complete at the quote date), so the near quarters are close to locked
            driver_realised_share=round(np.clip(np.mean([_realised(q - 1), _realised(q - 2)]), 0, 1), 2),
            status=("actual" if q <= END else ("quarter-to-date to " + fred_last["eurusd"][1] if q == pd.Period("2026Q3", "Q") else "path")),
        ))
sched = pd.DataFrame(sched_rows)
sched.round(2).to_csv(OUT / "05_fx_schedule.csv", index=False)
print("\nFX schedule (consensus path):")
print(sched[sched["path"] == "consensus"].round(2).to_string(index=False))

# ----------------------------------------------------------------------------------------------
# 6. Regional growth from the letters, cross-border share, Eurostat and BEA alignment
# ----------------------------------------------------------------------------------------------
# bucket -> midpoint used for plotting only: low-single 2, mid-single 5, high-single 8, low-double 11, mid-teens 15, high-teens 18, ~20 20, low-20s 22
REG = [
    # quarter, NA, EMEA, LatAm, APAC (text as written in the letter / call), source
    ("2024Q3", "growth, improved through the quarter (unquantified)", "slight acceleration q/q (unquantified)", "15%", "19%", "3Q24 letter"),
    ("2024Q4", "mid-single digits", "low-double digits", "low-20s", "low-20s", "4Q24 letter"),
    ("2025Q1", "low-single digits", "mid-single digits", "low-20s", "mid-teens", "1Q25 letter and call"),
    ("2025Q2", "low-single digits", "mid-single digits", "high-teens", "mid-teens", "2Q25 letter and call"),
    ("2025Q3", "mid-single digits", "mid-single digits", "low-20s", "mid-teens", "3Q25 call"),
    ("2025Q4", "mid-single digits", "high-single digits", "high-teens", "mid-teens", "4Q25 call"),
    ("2026Q1", "high-single digits", "mid-single digits (Middle East cancellations)", "high-teens", "high-teens", "1Q26 letter"),
    ("2026Q2", "high-single digits (highest in ~3 years)", "high-single digits", "approximately 20%", "high-teens", "2Q26 letter and call"),
]
MID = {"low-single": 2, "mid-single": 5, "high-single": 8, "low-double": 11, "mid-teens": 15, "high-teens": 18, "approximately 20%": 20, "low-20s": 22, "15%": 15, "19%": 19}


def mid(txt):
    for k, v in MID.items():
        if txt.startswith(k):
            return v
    return np.nan


reg = pd.DataFrame(REG, columns=["quarter", "north_america", "emea", "latin_america", "asia_pacific", "source"])
for c in ["north_america", "emea", "latin_america", "asia_pacific"]:
    reg[c + "_mid_pct"] = reg[c].map(mid)
reg["q"] = pd.PeriodIndex(reg["quarter"], freq="Q")
reg = reg.set_index("q")
reg["global_nights_yoy_pct"] = tgt["nights_yoy"].reindex(reg.index).round(1)
reg["eu27_platform_nights_yoy_pct"] = eu_yoy["eu27_platform_nights_yoy"].reindex(reg.index).round(1)
reg["eu27_platform_foreign_yoy_pct"] = eu_yoy["eu27_platform_foreign_yoy"].reindex(reg.index).round(1)
reg["bea_inbound_foreign_travel_yoy_pct"] = tgt["bea_inbound_foreign_travel"].reindex(reg.index).round(1)
reg["bea_outbound_us_travel_yoy_pct"] = tgt["bea_outbound_us_travel"].reindex(reg.index).round(1)
reg["bea_accommodations_nominal_yoy_pct"] = tgt["bea_accom_nominal"].reindex(reg.index).round(1)
reg["usd_broad_yoy_pct"] = panel["usd_broad"].reindex(reg.index).round(1)
reg.reset_index(drop=True).to_csv(OUT / "05_regional_growth.csv", index=False)

XB = [("2019Q1", 51), ("2019Q2", 50), ("2019Q3", 48), ("2019Q4", 47), ("2021Q3", 33), ("2021Q4", 34), ("2022Q1", 39), ("2022Q2", 43),
      ("2022Q3", 43), ("2022Q4", 44), ("2023Q1", 45), ("2023Q2", 45), ("2023Q3", 45), ("2023Q4", 44), ("2024Q1", 46)]
xb = pd.DataFrame(XB, columns=["quarter", "cross_border_share_of_gross_nights_pct"])
xb["source"] = "shareholder letters (Travel corridors section); 2019 values quoted as comparators in the 2022-23 letters; not disclosed after 1Q24"
xb.to_csv(OUT / "05_crossborder_share.csv", index=False)

# ----------------------------------------------------------------------------------------------
# 7. Shock episodes: what macro did, what management guided, what printed, what the stock did
# ----------------------------------------------------------------------------------------------
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
rx["q"] = pd.PeriodIndex(rx["quarter"], freq="Q")
rx = rx.set_index("q")


def mq(col, q):
    v = panel[col].get(pd.Period(q, "Q"), np.nan)
    return None if pd.isna(v) else round(float(v), 1)


EPIS = [
    dict(episode="2022 rate shock (Fed hikes, USD +9-10% y/y)", shock_quarters="2022Q2-2022Q4",
         macro="Fed funds +3.9 pp y/y by 4Q22; USD broad y/y " + str(mq("usd_broad", "2022Q3")) + "% (3Q22); Michigan sentiment " + str(mq("umcsent", "2022Q2")) + " pts y/y (2Q22); CPI " + str(mq("cpi_all", "2022Q2")) + "%",
         guided="3Q22 call (1 Nov 2022): 4Q nights growth to moderate to ~20% from 25%, ADR flat; revenue $1.80-1.88B (+17-23%)",
         printed="4Q22 nights +20.2%, revenue +24.2% ($1.90B), ADR -0.5% (ex-FX +5, FX -5.5)",
         stock=f"3Q22 print day-1 {rx.loc[pd.Period('2022Q3','Q'),'abnb_1d_pct']:+.1f}% (excess {rx.loc[pd.Period('2022Q3','Q'),'excess_1d_pct']:+.1f}), 20d excess {rx.loc[pd.Period('2022Q3','Q'),'excess_20d_pct']:+.1f}%",
         lesson="Macro hit ADR through FX (-5 to -7 pp) and the multiple, not nights; the guide-down in nights growth (25 -> 20) drove the -13% day",
         sources="3Q22, 4Q22 letters; data/processed/abnb_earnings_reactions.csv; 05_macro_quarterly_panel.csv"),
    dict(episode="2024 US softness / shorter lead times", shock_quarters="2024Q2-2024Q3",
         macro="Michigan sentiment " + str(mq("umcsent", "2024Q2")) + " pts y/y; real DPI " + str(mq("real_dpi", "2024Q2")) + "%; BEA accommodations nominal " + str(mq("bea_accom_nominal", "2024Q2")) + "%; US hotel RevPAR flat",
         guided="2Q24 call (6 Aug 2024): Q3 nights growth to moderate vs Q2 (+8.7%), shorter lead times, slowing US demand; Q3 revenue $3.67-3.73B (+8-10%)",
         printed="3Q24 nights +8.5%, revenue +9.9% ($3.73B), NA 'continued growth', then 4Q24 re-accelerated to +12.3% on product changes",
         stock=f"2Q24 print day-1 {rx.loc[pd.Period('2024Q2','Q'),'abnb_1d_pct']:+.1f}%, 20d excess {rx.loc[pd.Period('2024Q2','Q'),'excess_20d_pct']:+.1f}%; 3Q24 print day-1 {rx.loc[pd.Period('2024Q3','Q'),'abnb_1d_pct']:+.1f}%",
         lesson="A 1-pt nights deceleration with 'lead time' language cost 13%; the macro series moved little. The market prices the words, not the macro",
         sources="2Q24, 3Q24, 4Q24 letters; reactions file"),
    dict(episode="Spring-2025 tariff / consumer-sentiment shock", shock_quarters="2025Q2",
         macro="Michigan sentiment 52.2 (Apr-May 2025 lows), " + str(mq("umcsent", "2025Q2")) + " pts y/y; initial claims " + str(mq("initial_claims", "2025Q2")) + "% y/y; USD broad " + str(mq("usd_broad", "2025Q2")) + "% y/y; BEA inbound foreign travel " + str(mq("bea_inbound_foreign_travel", "2025Q2")) + "% y/y; Canada arrivals to the US -25.7% for 2025 (Oxford Economics, 29 Jan 2026)",
         guided="1Q25 call (1 May 2025): Q2 nights growth to moderate vs Q1 (+7.9%); US 'relatively softer', longer-lead-time bookings soft, lead times -7% y/y in April; ADR ~flat; revenue $2.99-3.05B (+9-11%); inbound to the US 2-3% of the business",
         printed="2Q25 nights +7.4% (NA low-single, LatAm high-teens), revenue +12.7% ($3.10B, +2.5% vs midpoint), ADR +2.9% (+1 ex-FX, FX +1.9); nights accelerated April -> July, lead times normalised by June",
         stock=f"Tariff days 3 Apr -7.2% / 9 Apr +14.8% (in line with BKNG, EXPE); 1Q25 print day-1 {rx.loc[pd.Period('2025Q1','Q'),'abnb_1d_pct']:+.1f}% (excess {rx.loc[pd.Period('2025Q1','Q'),'excess_1d_pct']:+.1f}), 20d excess {rx.loc[pd.Period('2025Q1','Q'),'excess_20d_pct']:+.1f}%; 2Q25 print day-1 {rx.loc[pd.Period('2025Q2','Q'),'abnb_1d_pct']:+.1f}% on H2 moderation and $200M new-business spend",
         lesson="A 20-point y/y sentiment collapse and a 25% drop in Canadian arrivals moved global nights by about half a point (7.9 -> 7.4). Corridor substitution (Canadians to Mexico +27%) and the 2-3% inbound share cap the exposure. What hurt the stock was the H2 moderation language in August, not the shock itself",
         sources="1Q25, 2Q25 letters and calls; major-moves note; Oxford Economics US inbound outlook (Jan 2026)"),
    dict(episode="1Q26 Middle East conflict (Hormuz closure, jet fuel +70%, airfares +25% y/y)", shock_quarters="2026Q1-2026Q2",
         macro="CPI airline fares " + str(mq("cpi_airfare", "2026Q2")) + "% y/y (2Q26); Gulf jet fuel " + str(mq("jet_fuel_gulf", "2026Q2")) + "% y/y; WTI " + str(mq("wti", "2026Q2")) + "% y/y; Michigan sentiment " + str(mq("umcsent", "2026Q2")) + " pts y/y; ECB hiked June 2026; IAG cut FY26 capacity to flat",
         guided="1Q26 call (7 May 2026): ~100 bp headwind to nights in Q1 (9% reported, ~10% ex-conflict) from EMEA/APAC cancellations; Q2 nights to 'decelerate slightly' with ~100 bp headwind; Q2 revenue $3.54-3.60B (+14-16%, ~3 pt FX)",
         printed="2Q26 nights +10.3% (accelerated; Europe recovered to high-single digits), revenue +16.5% ($3.61B, +1.1% vs midpoint), ADR +5.3% (+4 ex-FX); 'impact less than anticipated'; Q3 guide assumes no significant conflict impact",
         stock=f"1Q26 print day-1 {rx.loc[pd.Period('2026Q1','Q'),'abnb_1d_pct']:+.1f}% (20d excess {rx.loc[pd.Period('2026Q1','Q'),'excess_20d_pct']:+.1f}%); 2Q26 print day-1 {rx.loc[pd.Period('2026Q2','Q'),'abnb_1d_pct']:+.1f}% (excess {rx.loc[pd.Period('2026Q2','Q'),'excess_1d_pct']:+.1f}), 5d excess {rx.loc[pd.Period('2026Q2','Q'),'excess_5d_pct']:+.1f}%",
         lesson="The largest airfare shock since 2022 (+25% y/y) coincided with the fastest nights growth in two years and +4% ex-FX ADR. Expensive flights push demand toward domestic and drive-to stays where Airbnb is over-indexed (LatAm ~20%, NA high-single). Management guided the headwind conservatively and beat it",
         sources="1Q26, 2Q26 letters and calls; FRED CUSR0000SETG01, WJFUELUSGULF; IATA June 2026 outlook; IAG H1 2026 results (late Jul 2026)"),
]
pd.DataFrame(EPIS).to_csv(OUT / "05_shock_episodes.csv", index=False)

# day-1 reaction by sign of nights acceleration in the reported quarter (links to the predictive study's 17/21 finding)
acc = tgt["nights_accel"].reindex(rx.index)
rx2 = rx.assign(nights_accel=acc)
rx2 = rx2[rx2["nights_accel"].notna()]
grp = rx2.groupby(rx2["nights_accel"] >= 0)[["abnb_1d_pct", "excess_1d_pct", "excess_5d_pct", "excess_20d_pct"]].agg(["mean", "median", "count"])
grp.index = ["decelerating (accel<0)", "accelerating (accel>=0)"]
grp.columns = ["_".join(c) for c in grp.columns]
post = rx2[rx2.index >= pd.Period("2023Q1", "Q")]
grp_post = post.groupby(post["nights_accel"] >= 0)[["abnb_1d_pct", "excess_1d_pct", "excess_20d_pct"]].agg(["mean", "count"])
grp_post.index = ["decelerating (accel<0), post-2022", "accelerating (accel>=0), post-2022"]
grp_post.columns = ["_".join(c) for c in grp_post.columns]
react = pd.concat([grp, grp_post])
react.round(1).to_csv(OUT / "05_reaction_by_accel.csv")
print("\nreaction by nights-acceleration sign:")
print(react.round(1).to_string())

# ----------------------------------------------------------------------------------------------
# 8. Scenarios (Half B) built on the fitted FX mechanism and the margin-bridge chain constants
# ----------------------------------------------------------------------------------------------
def fx_avg(path, quarters, col):
    s = sched[(sched["path"] == path) & (sched["quarter"].isin(quarters))]
    return float(s[col].mean())


FY27 = ["2027Q1", "2027Q2", "2027Q3", "2027Q4"]
# claims -> ADR ex-FX slope (the one non-mechanical medium-confidence ADR pair from note 03), re-estimated here
cl = sens[(sens["macro"] == "initial_claims") & (sens["target"] == "adr_exfx_yoy")].iloc[0]
claims_slope = float(cl["effect_per_unit"])
af = sens[(sens["macro"] == "cpi_airfare") & (sens["target"] == "adr_exfx_yoy")].iloc[0]
airfare_slope = float(af["effect_per_unit"])
BASE = dict(nights_4q26=9.5, nights_fy27=8.5, adr_exfx_fy27=2.5, take_rate_pts_fy27=0.0, margin_fy26=36.0, margin_fy27=36.5)
# Scenario assumptions. Sources for every macro figure are in research/notes/overnight/05_macro-outlook-and-transmission.md
# section 4. Nights, ADR ex-FX and take rate are judgement anchored on the 2022-26 realised range (nights 7.4-12.3%
# outside 2021-22 base effects; ADR ex-FX 0.5-4%); FX comes from 05_fx_schedule.csv; margin comes from the
# margin-bridge chain constants plus a judgement cost-response share.
SCEN = {
    "A_energy_relief_soft_dollar": dict(
        probability=0.30, fx_path="weak_usd",
        macro=("EIA STEO (11 Aug 2026) base case delivers: Brent averages $86.81/b in 2026 and $69.39 in 2027, WTI $80.88 then "
               "$65.39, wholesale jet fuel $3.24/gal 2026 to $2.50 2027; Hormuz normalises from the partial reopening seen in "
               "early Sep 2026 (about 18m bbl/day of escorted transits against 20m pre-conflict and 4.9m in 2Q26), so "
               "Brent converges down from the $96.06 spot of 4 Sep 2026. Fed hikes "
               "once (Sep or Oct 2026) then holds and cuts from mid-2027; US real GDP 2.3% 2026 to 2.7% 2027 (STR/Tourism "
               "Economics assumption, 1 Sep 2026) vs the Fed SEP median 2.3%; unemployment 4.2-4.3%; PCE inflation to 2.3% "
               "in 2027 (Fed SEP, 17 Jun 2026); Michigan sentiment recovers from 55.2 (Jul 2026) toward 65; EUR/USD to "
               "1.21-1.25 as US rates converge down first (the Nomura 1.22/1.25 and Scotiabank 1.20-1.21 calls in the Exchange "
               "Rates UK bank survey of 23 Aug 2026); CPI airline fares turn negative y/y from 2Q27 as the 2026 fuel "
               "spike laps; airline capacity restored (American had cut 4Q26 to +6.5%, IAG to flat); TSA throughput "
               "recovers from -3.7% y/y (7-day avg to 23 Aug 2026); US inbound stabilises; Europe overnights +4-5% (ETC, "
               "10 Jul 2026: arrivals +5% YTD, Q2 nights +4.8%)"),
        nights_4q26=11.0, adr_exfx_4q26=3.5, nights_fy27=10.5, adr_exfx_fy27=3.0, claims_yoy_fy27=-5, take_rate_pts_fy27=0.0, margin_fy26=36.3,
        guide_5nov=("Q4 revenue +13-15% (FX about -0.4 pp vs +3 pp in Q3, nights ~11%, ADR ex-FX +3-4%, take rate +0.5); "
                    "FY26 revenue lifted from 'at least mid teens' toward 16-17%; FY26 margin raised above 'at least 35.5%'; "
                    "nights guided at or above the Q3 rate, which is what the reaction function reads"),
        guide_feb27=("FY27 revenue 'mid teens', Adjusted EBITDA margin guided up (a floor at or above 36.5%), FX described as "
                     "a tailwind in 2H27, buyback authorisation topped up"),
        analogue="4Q22 (15 Feb 2023, +13.4%), 4Q24 (14 Feb 2025, +14.4%), 2Q26 (7 Aug 2026, +17.4%): nights guided to accelerate",
    ),
    "B_muddle_through_stagflation_lite": dict(
        probability=0.50, fx_path="consensus",
        macro=("Brent holds $85-100 into 1H27 (spot $96.06 on 4 Sep 2026 against the Aug STEO forecast of $78 for 4Q26, so that "
               "STEO is already stale) then eases toward the EIA 2027 average of $69, in line with Capital Economics on "
               "4 Sep 2026 ($100 by end-2026, about $70 in 2027); the Fed delivers at most one hike (three July 2026 "
               "dissenters wanted one; "
               "market-implied hike odds about 60% on 4 Sep 2026 under new chair Kevin Warsh) and then holds, dots at 3.8% "
               "end-2026 and 3.6% end-2027 (SEP, "
               "17 Jun 2026); PCE inflation 3.6% 2026 to 2.3% 2027 (SEP) / core PCE 3.3% to 2.4% (Philadelphia Fed SPF Q3 "
               "2026); real GDP 2.1-2.2% (SPF); unemployment 4.3% through 2027 (SEP and SPF agree); Michigan sentiment "
               "50-58 and Conference Board expectations below the 80 recession threshold (68.2 in Aug 2026) but card "
               "delinquencies still improving (2.85% in 2Q26 from 3.04%); EUR/USD 1.16-1.18 (spot 1.16143 on 4 Sep 2026; "
               "Reuters poll of 55-66 strategists, 2 Sep 2026, median 1.16 at 3m, 1.17 at 6m, 1.18 at 12m) as the Fed and the ECB "
               "hike into each other, the ECB expected to raise 25 bp to 2.50% on 10 Sep 2026; CPI airline fares stay "
               "+15-20% y/y until they lap in 2Q27; US hotel RevPAR +4.4% 2026 and +2.1% 2027 (CoStar/STR + Tourism "
               "Economics, 7 Aug and 1 Sep 2026); US inbound flat to slightly better off a weak base; Europe overnights +3-4%"),
        nights_4q26=9.5, adr_exfx_4q26=3.0, nights_fy27=8.5, adr_exfx_fy27=2.5, claims_yoy_fy27=0, take_rate_pts_fy27=0.0, margin_fy26=36.0,
        guide_5nov=("Q4 revenue +11-13%. About 3 pp of the step-down from the Q3 guided 15-17% is the FX schedule, not demand. "
                    "Nights guided high-single to low-double digits against the Reserve Now Pay Later lap; FY26 'at least mid "
                    "teens' reiterated or nudged to ~16%; FY26 margin 'at least 35.5%' reiterated; take rate flat; no FY27 guide "
                    "(management has never given one in November)"),
        guide_feb27=("FY27 revenue 'low double digits' (10-12%), margin 'approximately stable' or a floor around 36%, FX called "
                     "out as a modest headwind in 1H27, continued reinvestment in AI, expansion markets and Services"),
        analogue=("4Q25 (13 Feb 2026, +4.6%) and 3Q25 (7 Nov 2025, +0.3%) if nights hold; 2Q25 (7 Aug 2025, -8.0%) if the "
                  "nights guide slips below the Q3 rate and 'moderation' or 'lead times' is said out loud"),
    ),
    "C_recession_or_renewed_shock": dict(
        probability=0.20, fx_path="strong_usd",
        macro=("Either Hormuz closes again and Brent goes above $110, or the Fed's hikes bite: unemployment to 5% by mid-2027, "
               "initial claims +20% y/y from 206k (w/e 29 Aug 2026), real disposable income flat, Michigan sentiment below 45, "
               "Conference Board expectations below 65. The dollar rallies on both safe-haven flows and a wider Fed-ECB "
               "differential, EUR/USD to 1.09-1.13 (the JPMorgan and HSBC 1.10, Goldman 1.12 and Citi 1.13-1.14 calls for 2Q27 in "
               "the Exchange Rates UK bank survey of 23 Aug 2026). Airline capacity cuts deepen from the 2H26 starting "
               "point (American already "
               "cut 4Q26 system capacity 110 bp to +6.5% and Pacific to -2.9% on TSA throughput -3.7% y/y; IAG cut FY26 to flat; "
               "Air France-KLM cut short/medium-haul to -1%). US inbound falls another 5% on top of the Canadian decline "
               "(StatCan: trips including a US visit -10.6% y/y in 1Q26, US spend -13.6%, while Canadian overseas trips rose "
               "6.2%); European long-haul outbound -10%; US hotel RevPAR turns negative"),
        nights_4q26=7.5, adr_exfx_4q26=2.0, nights_fy27=5.5, adr_exfx_fy27=0.5, claims_yoy_fy27=20, take_rate_pts_fy27=-0.3, margin_fy26=35.6,
        guide_5nov=("Q4 revenue +8-10% with 'moderation', 'shorter lead times' and 'macro uncertainty' in the letter; nights "
                    "guided below the Q3 rate; FY26 held at 'at least mid teens' only because 9M is already banked; Q4 margin "
                    "guided down y/y"),
        guide_feb27=("FY27 revenue 'mid-to-high single digits'; the margin floor guided down (the Feb 2025 pattern, when a "
                     "34.5% floor was set to protect reinvestment); named cost actions on marketing and headcount"),
        analogue=("3Q22 (2 Nov 2022, -13.4%), 1Q23 (10 May 2023, -10.9%), 2Q24 (7 Aug 2024, -13.4%), 3Q24 (8 Nov 2024, -8.7%), "
                  "2Q25 (7 Aug 2025, -8.0%): every one a decelerating nights guide, mean day-1 -5.4% post-2022 (n 9)"),
    ),
}
# change in airline-fare CPI y/y between 3Q26 (+21.1%) and the scenario's 2027 average, in percentage points
for _k, _v in SCEN.items():
    _v["airfare_yoy_chg_fy27"] = {"A_energy_relief_soft_dollar": -26.0, "B_muddle_through_stagflation_lite": -19.0,
                                  "C_recession_or_renewed_shock": -11.0}[_k]
scen_rows = []
for name, s in SCEN.items():
    adr_fx_4q26 = fx_avg(s["fx_path"], ["2026Q4"], "adr_fx_effect_fit_eur_pp")
    rev_fx_4q26 = fx_avg(s["fx_path"], ["2026Q4"], "revenue_fx_fit_pp")
    adr_fx_fy27 = fx_avg(s["fx_path"], FY27, "adr_fx_effect_fit_eur_pp")
    rev_fx_fy27 = fx_avg(s["fx_path"], FY27, "revenue_fx_fit_pp")
    adr_exfx_4q26 = s["adr_exfx_4q26"]
    take_4q26 = 0.5  # RNPL booking-vs-check-in timing laps (4Q25 take-rate contribution was -3.6 pp); judgement
    rev_4q26 = ((1 + s["nights_4q26"] / 100) * (1 + adr_exfx_4q26 / 100) * (1 + rev_fx_4q26 / 100) * (1 + take_4q26 / 100) - 1) * 100
    rev_fy27 = ((1 + s["nights_fy27"] / 100) * (1 + s["adr_exfx_fy27"] / 100) * (1 + rev_fx_fy27 / 100) * (1 + s["take_rate_pts_fy27"] / 100) - 1) * 100
    # margin FY27: model base 36.5 moved by the margin-bridge chain constants relative to the base scenario
    d_margin = (CHAIN["nights"] * (s["nights_fy27"] - BASE["nights_fy27"]) + CHAIN["adr_exfx"] * (s["adr_exfx_fy27"] - BASE["adr_exfx_fy27"])
                + CHAIN["fx"] * (rev_fx_fy27 - fx_avg("consensus", FY27, "revenue_fx_fit_pp")) + CHAIN["take"] * (s["take_rate_pts_fy27"] - BASE["take_rate_pts_fy27"]))
    margin_fy27_mech = BASE["margin_fy27"] + d_margin
    # cost response (judgement): in A management reinvests half the mechanical upside (Feb 2025 and Aug 2026 pattern: "reinvest most efficiencies");
    # in C S&M growth is cut to recover 40% of the mechanical shortfall (2022-23 pattern; the margin note's FY27 bear cuts S&M growth to +9% and lands at 33.8%)
    resp = {"A_energy_relief_soft_dollar": 0.5, "B_muddle_through_stagflation_lite": 0.0, "C_recession_or_renewed_shock": 0.4}[name]
    margin_fy27 = BASE["margin_fy27"] + d_margin * (1 - resp)
    scen_rows.append(dict(
        scenario=name, probability=s["probability"], macro_assumptions=s["macro"], fx_path=s["fx_path"],
        nights_growth_4q26_pct=s["nights_4q26"], adr_exfx_4q26_pct=adr_exfx_4q26, adr_fx_4q26_pp=round(adr_fx_4q26, 1), revenue_fx_4q26_pp=round(rev_fx_4q26, 1),
        take_rate_4q26_pp=take_4q26, revenue_growth_4q26_pct=round(rev_4q26, 1), ebitda_margin_fy26_pct=s["margin_fy26"],
        nights_growth_fy27_pct=s["nights_fy27"], adr_exfx_fy27_pct=s["adr_exfx_fy27"], adr_fx_fy27_pp=round(adr_fx_fy27, 1), revenue_fx_fy27_pp=round(rev_fx_fy27, 1),
        take_rate_fy27_pp=s["take_rate_pts_fy27"], revenue_growth_fy27_pct=round(rev_fy27, 1), ebitda_margin_fy27_mechanical_pct=round(margin_fy27_mech, 1),
        ebitda_margin_fy27_pct=round(margin_fy27, 1), cost_response_share=resp,
        adr_exfx_check_from_claims_pp=round(claims_slope * s["claims_yoy_fy27"], 1),
        adr_exfx_check_from_airfare_pp=round(airfare_slope * s["airfare_yoy_chg_fy27"], 1),
        guidance_5nov_2026=s["guide_5nov"], guidance_feb_2027=s["guide_feb27"], reaction_analogue=s["analogue"],
        method="nights and ADR ex-FX are judgement anchored on the 2022-26 range (nights 7-12 outside shocks); FX from 05_fx_schedule.csv; revenue multiplicative; FY27 margin = model base 36.5 +0.35/pt nights, +0.46/pt ADR ex-FX, +0.47/pt FX, +0.64/pt take-rate revenue (margin-drivers note sensitivities), then a cost-response share (A reinvests 50% of upside, C recovers 40% of downside)",
    ))
scen = pd.DataFrame(scen_rows)
scen.to_csv(OUT / "05_macro_scenarios.csv", index=False)
pw = scen.set_index("scenario")
print("\nscenarios:")
print(pw[["probability", "nights_growth_4q26_pct", "revenue_growth_4q26_pct", "nights_growth_fy27_pct", "adr_exfx_fy27_pct", "adr_fx_fy27_pp", "revenue_fx_fy27_pp", "revenue_growth_fy27_pct", "ebitda_margin_fy27_mechanical_pct", "ebitda_margin_fy27_pct"]].to_string())
print("probability-weighted FY27: nights %.1f, revenue %.1f, margin %.1f" % tuple(
    (pw["probability"] * pw[c]).sum() for c in ["nights_growth_fy27_pct", "revenue_growth_fy27_pct", "ebitda_margin_fy27_pct"]))

# ----------------------------------------------------------------------------------------------
# 9. Figures
# ----------------------------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # categorical slots 1-4 (reference palette, fixed order)
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": AXIS, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9, "text.color": INK,
                     "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlecolor": INK, "legend.frameon": False})

# 9a FX mechanism: scatter + schedule
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axes[0]
sel = (panel.index >= WINDOWS["ex21"]) & (panel.index <= END)
d = panel.loc[sel, ["eurusd", "adr_fx_effect"]].dropna()
ax.scatter(d["eurusd"], d["adr_fx_effect"], s=34, color=C[0], edgecolor=SURF, linewidth=1, zorder=3)
xx = np.linspace(d["eurusd"].min() - 1, d["eurusd"].max() + 1, 50)
ax.plot(xx, a_adr["intercept"] + a_adr["slope"] * xx, color=C[0], lw=2)
for q, r_ in d.iterrows():
    if str(q) in ("2022Q3", "2026Q1", "2025Q1", "2026Q2"):
        ax.annotate(str(q), (r_["eurusd"], r_["adr_fx_effect"]), xytext=(4, 4), textcoords="offset points", fontsize=8, color=INK2)
ax.axhline(0, color=AXIS, lw=0.8)
ax.set_xlabel("EUR/USD y/y, quarter average (%)")
ax.set_ylabel("FX effect on ADR growth (pp, letters)")
ax.set_title(f"FX to ADR is mechanical: r {a_adr['r']:.2f}, n {a_adr['n']} (1Q22-2Q26)\nADR FX pp = {a_adr['intercept']:.2f} + {a_adr['slope']:.2f} x EUR/USD y/y", loc="left", fontsize=9.5)
ax = axes[1]
qs = [pd.Period(p, "Q") for p in ("2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3")] + future_q
xl = [str(q) for q in qs]
for i, (pname, lab) in enumerate((("consensus", "Reuters-poll path (1.16-1.18)"), ("strong_usd", "strong USD (1.09-1.13)"), ("weak_usd", "weak USD (1.19-1.25)"))):
    s = sched[sched["path"] == pname].set_index("quarter").reindex(xl)
    ax.plot(xl, s["revenue_fx_fit_pp"], color=C[i], lw=2, marker="o", ms=4, label=lab)
act = sched[sched["path"] == "consensus"].set_index("quarter").reindex(xl)["revenue_fx_actual_pp"]
ax.scatter(xl, act, color=INK, s=40, zorder=4, marker="D", label="actual revenue FX (reported minus constant currency)")
ax.axhline(0, color=AXIS, lw=0.8)
ax.axvline(4.5, color=AXIS, lw=0.8, ls="--")
ax.set_ylabel("FX contribution to revenue growth (pp)")
ax.set_title("Revenue FX schedule under three EUR/USD paths\n(fit: " + f"{best_rev['driver']} lag {int(best_rev['lag'])}, r {best_rev['r']:.2f}; 3Q26 guide says ~3 pp)", loc="left", fontsize=9.5)
ax.tick_params(axis="x", rotation=45)
ax.legend(fontsize=7.5, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "05_fx_mechanism.png", dpi=160)
plt.close(fig)

# 9b macro vs nights, post-2022 (the null result, shown)
pairs = [("umcsent", "Michigan sentiment, y/y change (pts)"), ("real_dpi", "real disposable income y/y (%)"),
         ("initial_claims", "initial claims y/y (%)"), ("cpi_airfare", "CPI airline fares y/y (%)"),
         ("fed_funds", "Fed funds, y/y change (pp)"), ("usd_broad", "USD broad y/y (%)")]
fig, axes = plt.subplots(2, 3, figsize=(11, 6.2))
selp = (panel.index >= WINDOWS["post22"]) & (panel.index <= END)
for ax, (mv, lab) in zip(axes.ravel(), pairs):
    d = panel.loc[selp, [mv, "nights_yoy"]].dropna()
    ax.scatter(d[mv], d["nights_yoy"], s=30, color=C[0], edgecolor=SURF, linewidth=1, zorder=3)
    for q, r_ in d.iterrows():
        if q.year == 2023 and q.quarter == 1 or str(q) in ("2025Q2", "2026Q2"):
            ax.annotate(str(q), (r_[mv], r_["nights_yoy"]), xytext=(3, 3), textcoords="offset points", fontsize=7, color=INK2)
    r_ = np.corrcoef(d[mv], d["nights_yoy"])[0, 1]
    d24 = d[d.index >= FROM24]
    r24 = np.corrcoef(d24[mv], d24["nights_yoy"])[0, 1]
    ax.set_title(f"{lab}\nr {r_:+.2f} (n {len(d)}); from 2024 r {r24:+.2f} (n {len(d24)})", loc="left", fontsize=8.5)
    ax.set_ylabel("nights y/y (%)")
fig.suptitle("Nights growth vs macro, 1Q23-2Q26: nothing survives once 1Q23 (the 19% quarter) is set aside", x=0.01, ha="left", fontsize=10)
fig.tight_layout()
fig.savefig(FIG / "05_macro_vs_nights.png", dpi=160)
plt.close(fig)

# 9c sensitivity bars: |r| post-2022 by macro for four targets, bars single hue, confidence in label
fig, axes = plt.subplots(1, 4, figsize=(14, 6.5), sharey=False)
for ax, tv in zip(axes, ["nights_yoy", "adr_exfx_yoy", "adr_fx_effect", "ebitda_margin_chg"]):
    s = sens[sens["target"] == tv].copy()
    s = s.assign(absr=s["r"].abs()).sort_values("absr").tail(14)
    cols = [C[0] if c in ("high", "medium") else GRID for c in s["confidence"]]
    ax.barh(s["macro_label"].str.replace(r" \(.*\)", "", regex=True), s["absr"], color=cols, height=0.62)
    for i, (v, c, r_) in enumerate(zip(s["absr"], s["confidence"], s["r"])):
        ax.text(v + 0.01, i, f"{r_:+.2f} {c}", va="center", fontsize=7, color=INK2)
    ax.set_xlim(0, 1.25)
    ax.set_title(TARGETS[tv], loc="left", fontsize=9)
    ax.set_xlabel("|r|, 1Q23-2Q26, best lag")
    ax.tick_params(axis="y", labelsize=7.5)
fig.suptitle("Which macro variables relate to ABNB KPIs post-2022 (blue = medium/high confidence after the artefact and stability checks; grey = low/none)", x=0.01, ha="left", fontsize=10)
fig.tight_layout()
fig.savefig(FIG / "05_sensitivity_bars.png", dpi=160)
plt.close(fig)

# ----------------------------------------------------------------------------------------------
# 10. Console summary for the note
# ----------------------------------------------------------------------------------------------
print("\nlatest FRED observations used:")
for k, v in fred_last.items():
    print(f"  {k:20s} {v[0]:16s} {v[1]}  {v[2]:,.3f}")
print("\n3Q26 quarter-to-date macro (y/y or 4q change):")
print(pd.to_numeric(panel.loc[pd.Period("2026Q3", "Q"), MACROS], errors="coerce").dropna().round(2).to_string())
print("\nsensitivities with medium/high confidence:")
print(sens[sens["confidence"].isin(["medium", "high"])][["macro", "target", "lag_quarters", "n", "effect_per_unit", "r", "perm_p", "loo_rmse", "naive_rmse", "r_ex2021", "r_from2024", "confidence"]].round(3).to_string(index=False))
print("\ncounts by confidence:")
print(sens["confidence"].value_counts().to_string())
print("\nregional table:")
print(reg[["north_america_mid_pct", "emea_mid_pct", "latin_america_mid_pct", "asia_pacific_mid_pct", "global_nights_yoy_pct", "eu27_platform_nights_yoy_pct", "bea_inbound_foreign_travel_yoy_pct", "usd_broad_yoy_pct"]].to_string())
print("\nEurostat EU27 platform nights y/y (quarterly):")
print(eu_yoy.dropna().tail(10).round(1).to_string())
