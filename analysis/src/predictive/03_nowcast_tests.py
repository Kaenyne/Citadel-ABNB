"""Predictive study 03: can any macro, category or alt-data series nowcast or lead Airbnb's quarterly KPIs?

Targets (quarterly, from the shareholder letters and our processed panels):
  nights_yoy      Nights and Seats Booked y/y %                 data/processed/abnb_kpi_vs_category_quarterly.csv
  nights_accel    change in nights y/y vs prior quarter (pp)    derived
  gbv_yoy         GBV y/y %                                     same panel
  adr_yoy         reported ADR y/y %                            same panel
  adr_exfx_yoy    ADR y/y ex-FX % (letters' global figure)      hardcoded below from data/raw/letters/*.htm, 2Q22-2Q26
  adr_fx_effect   reported ADR y/y minus ex-FX (pp)             derived; the FX contribution to ADR growth
  rev_beat_pct    revenue vs guide midpoint %                   data/external/abnb_revenue_guidance_vs_actual.csv
  excess_1d_pct   1-day excess return vs QQQ on the print       data/external/abnb_earnings_reactions.csv

Predictors: quarterly averages of monthly (or daily/weekly) macro series, as y/y % for indices and levels
for rates, at lag 0 (same quarter) and lag 1, both as levels and first differences; plus the share gap
(ABNB nights y/y minus BEA real accommodations y/y). Sources: data/raw/bea/*.csv, data/raw/fred/*.csv,
data/raw/macro/*.csv (keyless FRED CSVs, gitignored; re-download with
https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES).

Statistics per (series, transform, lag, target): n, Pearson r and p, Spearman rho and p, permutation p
(1,000 shuffles of the target, two-sided), leave-one-out OLS nowcast RMSE against naive last-quarter,
seasonal naive (t-4), LOO mean and (for the beat) zero, sign agreement across two halves, flag for |r|>0.5 and
perm p<0.05, Benjamini-Hochberg q and Bonferroni across all macro pairs. Every statistic is computed on three
windows: full sample (columns with no suffix), ex-2021 (suffix _ex2021, from 2022Q1) and post-2022 (suffix
_post2022, from 2023Q1); `survives_all_windows` marks pairs flagged with the same sign on all three. The COVID
rebound makes the full-sample columns leverage artefacts; read the post-2022 ones.

Alt data (section E): Inside Airbnb like-for-like price change and matched reviews_ltm change (year-ago pairs,
quarter of the later dump), city-snapshot reviews_ltm_sum y/y, Common Crawl review velocity by year, and a
descriptive ranking of the 2026 booking-curve snapshot.

Outputs: data/processed/predictive/03_nowcast_results.csv, 03_quarterly_panel.csv, 03_altdata_quarterly.csv,
03_booking_curve_ranking.csv, 03_cc_velocity_annual.csv.
Run: python analysis/src/predictive/03_nowcast_tests.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/predictive"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20260906)
N_PERM = 1000

# --------------------------------------------------------------------------------------------------
# A. Targets
# --------------------------------------------------------------------------------------------------
# ADR y/y excluding FX, global figure as stated in each shareholder letter ("Excluding the impact of FX, ADR in
# Qx increased N%"). 3Q23 and 4Q23 say "less than 1%", coded as 0.5. 1Q22 and earlier letters give no global
# ex-FX ADR figure. Source files: data/raw/letters/<Q>_*.htm.
ADR_EXFX = {"2022Q2": 7, "2022Q3": 12, "2022Q4": 5, "2023Q1": 3, "2023Q2": 2, "2023Q3": 0.5, "2023Q4": 0.5,
            "2024Q1": 2, "2024Q2": 3, "2024Q3": 2, "2024Q4": 2, "2025Q1": 1, "2025Q2": 1, "2025Q3": 2,
            "2025Q4": 3, "2026Q1": 4, "2026Q2": 4}


def load_targets() -> pd.DataFrame:
    k = pd.read_csv(ROOT / "data/processed/abnb_kpi_vs_category_quarterly.csv").set_index("quarter")
    t = pd.DataFrame(index=k.index)
    t["nights_yoy"] = k["nights_yoy_pct"]
    t["nights_accel"] = k["nights_yoy_pct"].diff()
    t["gbv_yoy"] = k["gbv_yoy_pct"]
    t["adr_yoy"] = k["adr_yoy_pct"]
    t["adr_exfx_yoy"] = pd.Series(ADR_EXFX)
    t["adr_fx_effect"] = t["adr_yoy"] - t["adr_exfx_yoy"]  # reported minus ex-FX: the FX contribution to ADR y/y (pp)
    g = pd.read_csv(ROOT / "data/external/abnb_revenue_guidance_vs_actual.csv").set_index("guided_quarter")
    t["rev_beat_pct"] = g["actual_vs_mid_pct"]
    r = pd.read_csv(ROOT / "data/external/abnb_earnings_reactions.csv").set_index("quarter")
    t["excess_1d_pct"] = r["excess_1d_pct"]
    t["share_gap"] = k["share_gap_nights_vs_bea_real_pct"]
    return t


# --------------------------------------------------------------------------------------------------
# B. Macro predictors: monthly -> quarterly mean -> y/y or level
# --------------------------------------------------------------------------------------------------
# (series_key, file, kind, availability-before-print note). kind: "yoy" = y/y % of the quarterly mean,
# "level" = quarterly mean of a rate/index used as is.
# Availability: ABNB prints 5 to 6 weeks after quarter end (earliest in our sample 2022-05-03, 33 days). CPI for
# the last month of the quarter is out about two weeks after month end; BEA personal income and outlays (PCE,
# saving rate) about four weeks after; retail sales advance about two weeks; sentiment final by month end;
# employment the first Friday; claims and FX daily/weekly. BTS air revenue passenger miles lag about three
# months and FHWA vehicle miles about two months, so the quarter's last month is NOT in hand at lag 0.
FRED_MONTHLY = [
    ("cpi_lodging_sa", "fred/CUSR0000SEHB.csv", "yoy", "yes: month-3 CPI out ~2 weeks after quarter end (4Q25 uses Nov-Dec only; Oct 2025 CPI not published)"),
    ("cpi_lodging_nsa", "macro/CUUR0000SEHB.csv", "yoy", "yes: same as CPI SA"),
    ("cpi_airfare", "fred/CUSR0000SETG01.csv", "yoy", "yes: same as CPI"),
    ("cpi_all", "fred/CPIAUCSL.csv", "yoy", "yes: same as CPI"),
    ("cpi_new_vehicles", "macro/CUSR0000SETA01.csv", "yoy", "yes: same as CPI (discretionary control)"),
    ("umcsent", "macro/UMCSENT.csv", "level", "yes: final reading by month end"),
    ("psavert", "macro/PSAVERT.csv", "level", "yes: BEA release ~4 weeks after month end; first vintage, revises"),
    ("unrate", "macro/UNRATE.csv", "level", "yes: first Friday of following month"),
    ("retail_sales_xauto", "macro/RSXFS.csv", "yoy", "yes: advance estimate ~2 weeks after month end; revises"),
    ("real_pce", "macro/PCEC96.csv", "yoy", "yes: BEA release ~4 weeks after month end; revises"),
    ("real_dpi", "macro/DSPIC96.csv", "yoy", "yes: BEA release ~4 weeks after month end; revises"),
    ("pce_services", "macro/PCES.csv", "yoy", "yes: BEA release ~4 weeks after month end; revises"),
    ("pce_durables", "macro/PCEDG.csv", "yoy", "yes: BEA release ~4 weeks after month end; revises"),
    ("emp_leisure_hosp", "macro/USLAH.csv", "yoy", "yes: first Friday of following month; revises"),
    ("air_rpm", "macro/AIRRPMTSID11.csv", "yoy", "NO at lag 0: BTS T-100 lags ~3 months; lag 1 mostly yes"),
    ("vehicle_miles", "macro/TRFVOLUSM227NFWA.csv", "yoy", "NO at lag 0: FHWA TVT lags ~2 months (month 3 missing); lag 1 yes"),
    ("initial_claims", "macro/ICSA.csv", "yoy", "yes: weekly, Thursday"),
    ("usd_tw_broad", "macro/DTWEXBGS.csv", "yoy", "yes: daily"),
    ("eurusd", "macro/DEXUSEU.csv", "yoy", "yes: daily"),
]
BEA_SERIES = [
    ("bea_accom_nominal", "accommodations", "nominal_saar_musd"),
    ("bea_accom_real", "accommodations", "real_chained_2017_musd"),
    ("bea_accom_price", "accommodations", "price_index_2017eq100"),
    ("bea_hotels_nominal", "hotels_motels", "nominal_saar_musd"),
    ("bea_hotels_real", "hotels_motels", "real_chained_2017_musd"),
    ("bea_hotels_price", "hotels_motels", "price_index_2017eq100"),
    ("bea_inbound_foreign_travel", "inbound_foreign_travel_in_us", "nominal_saar_musd"),
    ("bea_outbound_us_travel", "foreign_travel_by_us_residents", "nominal_saar_musd"),
]
BEA_NOTE = ("mostly yes: BEA monthly PCE for month 3 is out ~4 weeks after quarter end, before the print; "
            "our file is the current (revised) vintage, not what was printed at the time; US-resident spend only")


def quarterly_mean(s: pd.Series, min_months: int = 2) -> pd.Series:
    """Quarterly mean of a monthly/weekly/daily series. Monthly series need >=min_months months present;
    higher-frequency series need >= 8 (weekly) or >= 20 (daily) observations in the quarter."""
    s = s.dropna()
    freq_days = float(np.median(np.diff(s.index.values).astype("timedelta64[D]").astype(float))) if len(s) > 2 else 30.0
    q = s.groupby(s.index.to_period("Q"))
    m = q.mean()
    if freq_days > 20:  # monthly
        months = q.apply(lambda x: x.index.to_period("M").nunique())
        m = m[months >= min_months]
    else:
        m = m[q.count() >= (20 if freq_days < 3 else 8)]
    return m


def yoy(q: pd.Series) -> pd.Series:
    return (q / q.shift(4) - 1) * 100


def load_fred(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    df.columns = ["date", "value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")["value"]


def load_bea() -> dict:
    b = pd.read_csv(ROOT / "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv", parse_dates=["date"])
    out = {}
    for key, series, measure in BEA_SERIES:
        out[key] = b[(b.series == series) & (b.measure == measure)].set_index("date")["value"].astype(float)
    return out


def build_macro_panel():
    cols, notes = {}, {}
    for key, rel, kind, note in FRED_MONTHLY:
        q = quarterly_mean(load_fred(ROOT / "data/raw" / rel))
        cols[key] = yoy(q) if kind == "yoy" else q
        notes[key] = note
    for key, s in load_bea().items():
        cols[key] = yoy(quarterly_mean(s, min_months=3))
        notes[key] = BEA_NOTE
    panel = pd.DataFrame(cols)
    panel.index = panel.index.astype(str)
    return panel, notes


# --------------------------------------------------------------------------------------------------
# C. Statistics
# --------------------------------------------------------------------------------------------------
def loo_ols_rmse(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    err = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        b, a = np.polyfit(x[m], y[m], 1)
        err[i] = y[i] - (a + b * x[i])
    return float(np.sqrt(np.mean(err ** 2)))


def loo_mean_rmse(y: np.ndarray) -> float:
    n = len(y)
    err = np.array([y[i] - np.delete(y, i).mean() for i in range(n)])
    return float(np.sqrt(np.mean(err ** 2)))


def naive_rmse(target_full: pd.Series, quarters: list, shift: int):
    """RMSE of predicting y_t with y_{t-shift} over the given quarters, using the full target history."""
    tf = target_full.copy()
    tf.index = pd.PeriodIndex(tf.index, freq="Q")
    errs = []
    for q in quarters:
        p = pd.Period(q, freq="Q")
        prev = p - shift
        if prev in tf.index and pd.notna(tf[prev]):
            errs.append(tf[p] - tf[prev])
    return float(np.sqrt(np.mean(np.square(errs)))) if len(errs) >= 4 else None


def perm_p(x: np.ndarray, y: np.ndarray, r_obs: float) -> float:
    cnt = 0
    for _ in range(N_PERM):
        r = np.corrcoef(x, RNG.permutation(y))[0, 1]
        if abs(r) >= abs(r_obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (N_PERM + 1)


WINDOWS = [("", None), ("_ex2021", "2022Q1"), ("_post2022", "2023Q1")]  # suffix, first quarter kept


def block(d: pd.DataFrame, target_full: pd.Series, target: str, suffix: str) -> dict:
    """Full statistic set for one (x, y) sample. suffix is appended to every column name."""
    xa, ya = d["x"].to_numpy(float), d["y"].to_numpy(float)
    r, p = stats.pearsonr(xa, ya)
    rho, sp = stats.spearmanr(xa, ya)
    quarters = list(d.index)
    h = len(d) // 2
    r1 = stats.pearsonr(xa[:h], ya[:h])[0] if h >= 4 and len(set(xa[:h])) > 2 else np.nan
    r2 = stats.pearsonr(xa[h:], ya[h:])[0] if len(xa) - h >= 4 and len(set(xa[h:])) > 2 else np.nan
    out = {"n": len(d), "first_q": quarters[0], "last_q": quarters[-1], "pearson_r": r, "pearson_p": p,
           "spearman_rho": rho, "spearman_p": sp, "perm_p": perm_p(xa, ya, r), "rmse_loo_ols": loo_ols_rmse(xa, ya),
           "rmse_loo_mean": loo_mean_rmse(ya), "rmse_naive_last": naive_rmse(target_full, quarters, 1),
           "rmse_seasonal_naive": naive_rmse(target_full, quarters, 4),
           "rmse_zero": float(np.sqrt(np.mean(ya ** 2))) if target == "rev_beat_pct" else None,
           "r_half1": r1, "r_half2": r2,
           "sign_stable": bool(np.sign(r1) == np.sign(r2)) if not (np.isnan(r1) or np.isnan(r2)) else None}
    return {k + suffix: v for k, v in out.items()}


def pair_stats(x: pd.Series, y: pd.Series, target_full: pd.Series, target: str):
    """Statistics on three windows: full sample, ex-2021 (2022Q1 on) and post-2022 (2023Q1 on).
    The COVID rebound (nights +197% in 2Q21, +59% in 1Q22) gives every reopening series a leverage-driven
    correlation with the early quarters, so the sub-windows matter more than the full-sample r."""
    d = pd.concat([x, y], axis=1, keys=["x", "y"]).dropna()
    if len(d) < 8 or d["x"].nunique() < 3:
        return None
    out = {}
    for suffix, start in WINDOWS:
        dw = d if start is None else d[d.index >= start]
        if len(dw) >= 8 and dw["x"].nunique() > 2:
            out.update(block(dw, target_full, target, suffix))
        else:
            out["n" + suffix] = len(dw)
    return out


def bh_q(p: pd.Series) -> pd.Series:
    p = p.astype(float)
    order = p.dropna().sort_values()
    n = len(order)
    q = order.values * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    return pd.Series(np.minimum(q, 1.0), index=order.index).reindex(p.index)


# --------------------------------------------------------------------------------------------------
# D. Run the macro grid
# --------------------------------------------------------------------------------------------------
TARGETS = ["nights_yoy", "nights_accel", "gbv_yoy", "adr_yoy", "adr_exfx_yoy", "adr_fx_effect", "rev_beat_pct", "excess_1d_pct"]


def run_macro(targets: pd.DataFrame, panel: pd.DataFrame, notes: dict) -> pd.DataFrame:
    rows = []
    idx = sorted(set(targets.index) | set(panel.index))
    panel = panel.reindex(idx)
    tg = targets.reindex(idx)
    preds = {c: panel[c] for c in panel.columns}
    preds["share_gap"] = tg["share_gap"]
    notes = dict(notes)
    notes["share_gap"] = "no at lag 0 (needs the print's own nights figure); lag 1 yes"
    for key, s in preds.items():
        for transform in ("level", "diff1"):
            base = s if transform == "level" else s.diff()
            for lag in (0, 1):
                x = base.shift(lag)
                for target in TARGETS:
                    if key == "share_gap" and lag == 0 and target in ("nights_yoy", "nights_accel", "gbv_yoy"):
                        continue  # circular: the share gap contains the target
                    st = pair_stats(x, tg[target], targets[target].dropna(), target)
                    if st is None:
                        continue
                    avail = notes[key]
                    if lag == 1:
                        avail = "yes (prior quarter)" if not avail.startswith("NO") else avail
                    rows.append(dict(family="macro", series=key, transform=transform, lag=lag, target=target,
                                     available_before_print=avail, **st))
    res = pd.DataFrame(rows)
    for suffix, _ in WINDOWS:
        r, p, pp = res["pearson_r" + suffix], res["pearson_p" + suffix], res["perm_p" + suffix]
        res["flag_r_gt_0.5_perm_lt_0.05" + suffix] = (r.abs() > 0.5) & (pp < 0.05)
        res["bh_q" + suffix] = bh_q(p)
        res["bonferroni_sig" + suffix] = p < 0.05 / p.notna().sum()
        res["ols_beats_naive_last" + suffix] = res["rmse_loo_ols" + suffix] < res["rmse_naive_last" + suffix]
        res["ols_beats_seasonal" + suffix] = res["rmse_loo_ols" + suffix] < res["rmse_seasonal_naive" + suffix]
        res["ols_beats_loo_mean" + suffix] = res["rmse_loo_ols" + suffix] < res["rmse_loo_mean" + suffix]
    res["bh_q_within_target"] = res.groupby("target")["pearson_p"].transform(bh_q)
    # "survives": flagged on the full sample AND same-sign |r|>0.5 with perm p<0.05 on both sub-windows
    res["survives_all_windows"] = (res["flag_r_gt_0.5_perm_lt_0.05"] & res["flag_r_gt_0.5_perm_lt_0.05_ex2021"]
                                   & res["flag_r_gt_0.5_perm_lt_0.05_post2022"]
                                   & (np.sign(res.pearson_r) == np.sign(res.pearson_r_ex2021))
                                   & (np.sign(res.pearson_r) == np.sign(res.pearson_r_post2022)))
    return res


# --------------------------------------------------------------------------------------------------
# E. Alt data
# --------------------------------------------------------------------------------------------------
def altdata_quarterly() -> pd.DataFrame:
    lfl = pd.read_csv(ROOT / "data/external/inside_airbnb_like_for_like.csv", parse_dates=["date_a", "date_b"])
    ya = lfl[lfl.pair_type == "year_ago"].copy()
    ya["quarter"] = ya.date_b.dt.to_period("Q").astype(str)
    price = ya[(ya.price_comparable == True) & (ya.matched_priced_entire > 0)]  # noqa: E712
    pc = price.groupby(["quarter", "city"]).agg(chg=("lfl_price_chg_median", "mean"), w=("matched_priced_entire", "mean")).reset_index()
    pq = pc.groupby("quarter").apply(lambda g: pd.Series(dict(
        ia_lfl_price_yoy_simple=g.chg.mean() * 100,
        ia_lfl_price_yoy_weighted=np.average(g.chg, weights=g.w) * 100,
        ia_lfl_price_cities=len(g), ia_lfl_price_city_list=";".join(sorted(g.city)))), include_groups=False)
    rc = ya.groupby(["quarter", "city"]).agg(chg=("matched_reviews_ltm_chg", "mean"), ret=("retention", "mean")).reset_index()
    rq = rc.groupby("quarter").apply(lambda g: pd.Series(dict(
        ia_matched_reviews_ltm_yoy=g.chg.mean() * 100, ia_matched_retention=g.ret.mean(), ia_reviews_cities=len(g),
        ia_reviews_city_list=";".join(sorted(g.city)))), include_groups=False)
    snap = pd.read_csv(ROOT / "data/external/inside_airbnb_city_snapshots.csv", parse_dates=["dump_date"])
    recs = []
    for city, g in snap.sort_values("dump_date").groupby("city"):
        g = g.reset_index(drop=True)
        for _, row in g.iterrows():
            days = (row.dump_date - g.dump_date).dt.days
            cand = g[(days >= 330) & (days <= 400)]
            if len(cand):
                prev = cand.iloc[-1]
                recs.append(dict(city=city, quarter=str(row.dump_date.to_period("Q")),
                                 rev_ltm_yoy=(row.reviews_ltm_sum / prev.reviews_ltm_sum - 1) * 100,
                                 listings_yoy=(row.listings / prev.listings - 1) * 100))
    sn = pd.DataFrame(recs).groupby(["quarter", "city"]).mean(numeric_only=True).reset_index()
    sq = sn.groupby("quarter").apply(lambda g: pd.Series(dict(
        ia_snapshot_reviews_ltm_yoy=g.rev_ltm_yoy.mean(), ia_snapshot_listings_yoy=g.listings_yoy.mean(),
        ia_snapshot_cities=len(g), ia_snapshot_city_list=";".join(sorted(g.city)))), include_groups=False)
    out = pd.concat([pq, rq, sq], axis=1).sort_index()
    out.index.name = "quarter"
    return out


ALT_TESTS = [
    ("ia_lfl_price_yoy_simple", "adr_yoy", "Inside Airbnb like-for-like median listed-price change, year-ago matched listings, simple city mean"),
    ("ia_lfl_price_yoy_weighted", "adr_yoy", "same, weighted by matched priced entire-home listings"),
    ("ia_lfl_price_yoy_simple", "adr_exfx_yoy", "like-for-like price vs ADR ex-FX"),
    ("ia_lfl_price_yoy_weighted", "adr_exfx_yoy", "weighted like-for-like price vs ADR ex-FX"),
    ("ia_matched_reviews_ltm_yoy", "nights_yoy", "matched-listing trailing-12m reviews change (survivors only)"),
    ("ia_matched_reviews_ltm_yoy", "nights_accel", "matched reviews change vs nights acceleration"),
    ("ia_snapshot_reviews_ltm_yoy", "nights_yoy", "all-listing reviews_ltm_sum y/y from city snapshots ~12 months apart"),
    ("ia_snapshot_reviews_ltm_yoy", "gbv_yoy", "snapshot reviews y/y vs GBV y/y"),
    ("ia_snapshot_reviews_ltm_yoy", "rev_beat_pct", "snapshot reviews y/y vs revenue beat"),
    ("ia_snapshot_listings_yoy", "nights_yoy", "snapshot listing count y/y (supply) vs nights"),
]
ALT_AVAIL = "yes if dumps are captured (Inside Airbnb publishes ~quarterly with a 1 to 2 month lag)"


def run_altdata(targets: pd.DataFrame, alt: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, target, note in ALT_TESTS:
        d = pd.concat([alt[col], targets[target]], axis=1, keys=["x", "y"]).dropna()
        if len(d) < 5:
            rows.append(dict(family="altdata", series=col, transform="level", lag=0, target=target, n=len(d),
                             available_before_print=ALT_AVAIL, note=note + " -- n too small for any statistic"))
            continue
        xa, ya = d.x.to_numpy(float), d.y.to_numpy(float)
        r, p = stats.pearsonr(xa, ya)
        rho, sp = stats.spearmanr(xa, ya)
        rows.append(dict(family="altdata", series=col, transform="level", lag=0, target=target, n=len(d),
                         first_q=d.index[0], last_q=d.index[-1], pearson_r=r, pearson_p=p, spearman_rho=rho, spearman_p=sp,
                         perm_p=perm_p(xa, ya, r), rmse_loo_ols=loo_ols_rmse(xa, ya) if len(d) >= 6 else None,
                         rmse_loo_mean=loo_mean_rmse(ya), rmse_naive_last=naive_rmse(targets[target].dropna(), list(d.index), 1),
                         rmse_seasonal_naive=naive_rmse(targets[target].dropna(), list(d.index), 4),
                         available_before_print=ALT_AVAIL, note=note))
    return pd.DataFrame(rows)


def cc_velocity() -> pd.DataFrame:
    m = pd.read_csv(ROOT / "data/external/cc_matched_listings.csv")
    m = m[m.days_apart >= 90]
    v = m.groupby("year_b").agg(pairs=("listing_id", "count"), median_reviews_per_year=("reviews_per_year", "median"),
                                mean_reviews_per_year=("reviews_per_year", "mean"),
                                share_no_new_reviews=("review_delta", lambda s: (s <= 0).mean()))
    k = pd.read_csv(ROOT / "data/processed/abnb_kpi_vs_category_quarterly.csv")
    k["year"] = k.quarter.str[:4].astype(int)
    ann = k.groupby("year").agg(nights=("nights_m", "sum"), quarters=("quarter", "count"))
    ann["nights_yoy_pct"] = (ann.nights / ann.nights.shift(1) - 1) * 100
    h1 = k[k.quarter.str[-2:].isin(["Q1", "Q2"])].groupby("year").nights_m.sum()
    ann.loc[2026, "nights_yoy_pct"] = (h1[2026] / h1[2025] - 1) * 100  # 1H26 vs 1H25
    v = v.join(ann[["nights_yoy_pct", "quarters"]])
    v["velocity_yoy_pct"] = (v.median_reviews_per_year / v.median_reviews_per_year.shift(1) - 1) * 100
    v.index.name = "year"
    return v


def booking_curve_ranking() -> pd.DataFrame:
    b = pd.read_csv(ROOT / "data/external/booking_curves_by_market.csv")
    w = b.pivot_table(index=["country", "market", "snapshot_date"], columns="horizon", values="blocked_rate").reset_index()
    lst = b.groupby(["country", "market"]).listings.max().rename("listings").reset_index()
    w = w.merge(lst, on=["country", "market"])
    w["fwd_curve_slope_30_to_180"] = w["h000_030"] - w["h091_180"]
    return w.sort_values("h031_060", ascending=False)


# --------------------------------------------------------------------------------------------------
def main():
    targets = load_targets()
    panel, notes = build_macro_panel()
    full = targets.join(panel, how="outer").sort_index()
    full = full[full.index >= "2019Q1"]  # the FRED histories go back decades; keep the pre-COVID base and after
    full.index.name = "quarter"
    full.to_csv(OUT / "03_quarterly_panel.csv", float_format="%.3f")

    macro = run_macro(targets, panel, notes)
    alt = altdata_quarterly()
    alt.to_csv(OUT / "03_altdata_quarterly.csv", float_format="%.3f")
    altres = run_altdata(targets, alt)
    res = pd.concat([macro, altres], ignore_index=True)
    res.to_csv(OUT / "03_nowcast_results.csv", index=False, float_format="%.4f")

    cc = cc_velocity()
    cc.to_csv(OUT / "03_cc_velocity_annual.csv", float_format="%.3f")
    d = cc.dropna(subset=["velocity_yoy_pct", "nights_yoy_pct"])
    if len(d) >= 3:
        print("CC velocity y/y vs nights y/y: n=%d r=%.2f" % (len(d), stats.pearsonr(d.velocity_yoy_pct, d.nights_yoy_pct)[0]))
        print("CC median velocity level vs nights y/y: n=%d r=%.2f" % (len(d), stats.pearsonr(d.median_reviews_per_year, d.nights_yoy_pct)[0]))
    bc = booking_curve_ranking()
    bc.to_csv(OUT / "03_booking_curve_ranking.csv", index=False, float_format="%.4f")

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    for suffix, _ in WINDOWS:
        f = "flag_r_gt_0.5_perm_lt_0.05" + suffix
        print(f"window{suffix or '_full':10s}: pairs={int(macro['pearson_p' + suffix].notna().sum())} flagged={int(macro[f].sum())} "
              f"BH q<0.10={int((macro['bh_q' + suffix] < 0.10).sum())} Bonferroni={int(macro['bonferroni_sig' + suffix].sum())}")
    print("survive all three windows:", int(macro.survives_all_windows.sum()))
    macro["avail"] = macro.available_before_print.str.split(":").str[0].str.slice(0, 20)
    cols = ["series", "transform", "lag", "target", "n", "pearson_r", "perm_p", "pearson_r_ex2021", "perm_p_ex2021", "n_post2022",
            "pearson_r_post2022", "perm_p_post2022", "sign_stable_post2022", "rmse_loo_ols_post2022", "rmse_naive_last_post2022",
            "rmse_seasonal_naive_post2022", "rmse_loo_mean_post2022", "bh_q_post2022", "avail"]
    print("\nTOP 30 by |r| post-2022")
    top = macro.reindex(macro.pearson_r_post2022.abs().sort_values(ascending=False).index)
    print(top[cols].head(30).to_string())
    print("\nTOP 15 by |r| full sample")
    top = macro.reindex(macro.pearson_r.abs().sort_values(ascending=False).index)
    print(top[cols].head(15).to_string())
    print("\nsurvivors of all three windows")
    print(macro[macro.survives_all_windows][cols].to_string())
    print("\nper target, best |r| post-2022 pairs with availability yes:")
    ok = macro[macro.available_before_print.str.startswith(("yes", "mostly"))]
    for t, g in ok.groupby("target"):
        g = g.reindex(g.pearson_r_post2022.abs().sort_values(ascending=False).index)
        print(f"  == {t}")
        print(g[cols].head(8).to_string())
    print("\nalt data:")
    print(altres[["series", "target", "n", "first_q", "last_q", "pearson_r", "pearson_p", "perm_p", "rmse_loo_ols", "rmse_naive_last", "rmse_seasonal_naive"]].to_string())
    print("\n", alt.to_string())
    print("\n", cc.to_string())
    print("\nbooking curve: top 10 by 31-60d blocked rate")
    show = ["country", "market", "snapshot_date", "listings", "h000_030", "h031_060", "h061_090", "h091_180", "h181_372"]
    print(bc.head(10)[show].to_string())
    print("bottom 10")
    print(bc.tail(10)[show].to_string())
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
