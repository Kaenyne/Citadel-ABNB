"""
Workstream 09: ABNB stock behaviour beyond the print.

Drift, seasonality, factor exposure, event reactions, options, simple-rule backtests
and positioning.

READS
  data/processed/overnight/09_prices_daily.csv   ABNB + 19 tickers, adjusted closes,
                                                 yfinance, 2020-12-01..2026-09-04
  data/processed/overnight/09_ff_factors_daily.csv  Ken French 5 factors + momentum
  data/processed/overnight/09_analyst_actions.csv   yfinance upgrades/downgrades feed
  data/processed/overnight/09_short_interest.csv    marketbeat / nasdaq semi-monthly SI
  data/processed/abnb_daily_close.csv                (cross-check only)
  data/processed/abnb_earnings_reactions.csv         23 prints, 1/5/20d vs QQQ
  data/processed/abnb_major_moves_events.csv         41 moves >= 7% with attribution
  data/processed/predictive/02_peer_prints.csv       peer print + reaction dates
  ../citadel-abnb/data/processed/abnb_options_ledger.csv   (optional) 5 Sep 2026 IV snapshot

WRITES  data/processed/overnight/09_*.csv, analysis/figures/overnight/09_*.png

Run:  py -3.13 analysis/src/overnight/09_stock_behaviour.py
"""
from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data" / "processed"
OUT = PROC / "overnight"
FIG = ROOT / "analysis" / "figures" / "overnight"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

TEST_LEDGER: list[dict] = []


def log_test(block: str, name: str, n, stat=None, p=None, note=""):
    TEST_LEDGER.append(
        dict(block=block, test=name, n=n, statistic=stat, p_value=p, note=note)
    )


def tstat(x):
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    if len(x) < 3:
        return np.nan, np.nan, len(x)
    t, p = stats.ttest_1samp(x, 0.0)
    return float(t), float(p), len(x)


# ---------------------------------------------------------------- data layer
def load_prices() -> pd.DataFrame:
    px = pd.read_csv(OUT / "09_prices_daily.csv", parse_dates=["Date"]).set_index("Date")
    px = px.sort_index()
    return px


def build_returns(px: pd.DataFrame) -> pd.DataFrame:
    lvl = [c for c in px.columns if c not in ("^TNX",)]
    r = px[lvl].pct_change() * 100.0
    # rates: change in the 10y yield in basis points; USD: UUP return already in lvl
    r["TNX_bp"] = px["^TNX"].diff() * 100.0
    r["VIX_chg"] = px["^VIX"].diff()
    r = r.rename(columns={"^VIX": "VIX_ret"})
    # baskets
    r["OTA"] = r[["BKNG", "EXPE"]].mean(axis=1)
    r["HOTELS"] = r[["MAR", "HLT", "H"]].mean(axis=1)
    r["TRAVEL"] = r[["BKNG", "EXPE", "MAR", "HLT", "H", "JETS"]].mean(axis=1)
    r["GIG"] = r[["UBER", "DASH"]].mean(axis=1)
    return r


def orthogonalise(y: pd.Series, X: pd.DataFrame) -> pd.Series:
    """Residual of y on X (with intercept), aligned on the common non-null index."""
    d = pd.concat([y, X], axis=1).dropna()
    A = np.column_stack([np.ones(len(d)), d[X.columns].values])
    beta, *_ = np.linalg.lstsq(A, d[y.name].values, rcond=None)
    resid = d[y.name].values - A @ beta
    return pd.Series(resid, index=d.index, name=f"{y.name}_orth")


# ============================================================ 1. FACTOR MODEL
FACTORS = ["QQQ", "XLY_orth", "TRAVEL_orth", "TNX_bp", "UUP"]


def factor_frame(r: pd.DataFrame) -> pd.DataFrame:
    """Sequentially orthogonalised factor set so betas are additive contributions."""
    f = pd.DataFrame(index=r.index)
    f["QQQ"] = r["QQQ"]
    f["XLY_orth"] = orthogonalise(r["XLY"], r[["QQQ"]])
    f["TRAVEL_orth"] = orthogonalise(r["TRAVEL"], f[["QQQ", "XLY_orth"]])
    f["TNX_bp"] = r["TNX_bp"]
    f["UUP"] = r["UUP"]
    f["ABNB"] = r["ABNB"]
    f["OTA"] = r["OTA"]
    f["HOTELS"] = r["HOTELS"]
    f["SPY"] = r["SPY"]
    return f.dropna(subset=["ABNB"])


def ols(y: np.ndarray, X: np.ndarray):
    """OLS with intercept. Returns coefs, se, t, r2, resid."""
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    dof = len(y) - A.shape[1]
    s2 = resid @ resid / dof if dof > 0 else np.nan
    try:
        cov = s2 * np.linalg.inv(A.T @ A)
        se = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        se = np.full(A.shape[1], np.nan)
    t = beta / se
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, t, r2, resid


def run_factor_model(f: pd.DataFrame):
    rows_year, rows_roll, rows_full = [], [], []

    d = f[["ABNB"] + FACTORS].dropna()

    # --- full sample and by-year multivariate ---
    def fit_block(dd, label):
        y = dd["ABNB"].values
        X = dd[FACTORS].values
        beta, se, t, r2, resid = ols(y, X)
        # variance shares: market only, +consumer, +travel
        _, _, _, r2_mkt, _ = ols(y, dd[["QQQ"]].values)
        _, _, _, r2_mkt_cd, _ = ols(y, dd[["QQQ", "XLY_orth"]].values)
        _, _, _, r2_sector, _ = ols(y, dd[["QQQ", "XLY_orth", "TRAVEL_orth"]].values)
        tot_var = float(np.var(y, ddof=1))
        rec = dict(
            sample=label, n=len(dd), alpha_bp_day=beta[0] * 100,
            alpha_t=t[0], r2=r2,
            var_share_market=r2_mkt, var_share_consumer=r2_mkt_cd - r2_mkt,
            var_share_travel=r2_sector - r2_mkt_cd,
            var_share_macro=r2 - r2_sector, var_share_idio=1 - r2,
            daily_vol_pct=float(np.std(y, ddof=1)),
            idio_vol_pct=float(np.std(resid, ddof=1)),
            ann_vol_pct=float(np.std(y, ddof=1)) * np.sqrt(252),
            ann_idio_vol_pct=float(np.std(resid, ddof=1)) * np.sqrt(252),
            total_var=tot_var,
        )
        for i, k in enumerate(FACTORS):
            rec[f"beta_{k}"] = beta[i + 1]
            rec[f"t_{k}"] = t[i + 1]
        # univariate betas to sub-baskets and SPY
        for k in ["OTA", "HOTELS", "SPY"]:
            sub = f.loc[dd.index, ["ABNB", k]].dropna()
            b, s, tt, rr, _ = ols(sub["ABNB"].values, sub[[k]].values)
            rec[f"uni_beta_{k}"] = b[1]
            rec[f"uni_r2_{k}"] = rr
        sub = f.loc[dd.index, ["ABNB", "QQQ"]].dropna()
        b, s, tt, rr, _ = ols(sub["ABNB"].values, sub[["QQQ"]].values)
        rec["uni_beta_QQQ"] = b[1]
        rec["uni_r2_QQQ"] = rr
        # annual return attribution (arithmetic, daily sums)
        contrib = {k: float(beta[i + 1] * dd[k].sum()) for i, k in enumerate(FACTORS)}
        rec.update({f"contrib_{k}_pct": v for k, v in contrib.items()})
        rec["contrib_alpha_pct"] = float(beta[0] * len(dd))
        rec["sum_daily_ret_pct"] = float(dd["ABNB"].sum())
        return rec

    rows_full.append(fit_block(d, "full_2020-12..2026-09"))
    rows_full.append(fit_block(d[d.index >= "2023-01-01"], "from_2023"))
    for yr, dd in d.groupby(d.index.year):
        if len(dd) < 60:
            continue
        rows_year.append(fit_block(dd, str(yr)))
    log_test("1 factor", "multivariate 5-factor OLS, full + from-2023 + 6 years", len(d),
             note="8 fits, 5 betas each = 40 coefficient t-tests")

    # --- rolling 126-session betas ---
    W = 126
    idx = d.index
    for i in range(W, len(d) + 1):
        w = d.iloc[i - W:i]
        y = w["ABNB"].values
        beta, se, t, r2, resid = ols(y, w[FACTORS].values)
        sub = f.loc[w.index, ["ABNB", "OTA", "HOTELS"]].dropna()
        b_ota = ols(sub["ABNB"].values, sub[["OTA"]].values)[0][1]
        b_hot = ols(sub["ABNB"].values, sub[["HOTELS"]].values)[0][1]
        rec = dict(date=idx[i - 1], n=W, r2=r2,
                   idio_vol_ann_pct=float(np.std(resid, ddof=1)) * np.sqrt(252),
                   total_vol_ann_pct=float(np.std(y, ddof=1)) * np.sqrt(252),
                   uni_beta_OTA=b_ota, uni_beta_HOTELS=b_hot,
                   alpha_bp_day=beta[0] * 100)
        for j, k in enumerate(FACTORS):
            rec[f"beta_{k}"] = beta[j + 1]
            rec[f"t_{k}"] = t[j + 1]
        rows_roll.append(rec)

    return (pd.DataFrame(rows_full + rows_year), pd.DataFrame(rows_roll))


# =============================================== 2. EARNINGS DRIFT AND RUN-UP
PRE, POST = 21, 60


def excess_path(px: pd.DataFrame, t0_idx: int, bench: str = "QQQ"):
    """Cumulative ABNB-minus-bench return path anchored PRE sessions before t0."""
    a = t0_idx - PRE
    if a < 0 or t0_idx + POST >= len(px):
        lo, hi = max(a, 0), min(t0_idx + POST, len(px) - 1)
    else:
        lo, hi = a, t0_idx + POST
    p = px["ABNB"].values
    q = px[bench].values
    out = {}
    for k in range(-PRE, POST + 1):
        j = t0_idx + k
        if j < 0 or j > len(px) - 1 or a < 0:
            out[k] = np.nan
        else:
            out[k] = (p[j] / p[a] - 1) * 100 - (q[j] / q[a] - 1) * 100
    return out


def earnings_drift(px: pd.DataFrame, prints: pd.DataFrame):
    dates = px.index
    paths, summ = [], []
    for _, row in prints.iterrows():
        d0 = row["reaction_date"]
        if d0 not in dates:
            continue
        i0 = dates.get_loc(d0)
        path = excess_path(px, i0)
        for k, v in path.items():
            paths.append(dict(quarter=row["quarter"], reaction_date=d0, k=k, cum_excess_pct=v))
        c = path
        day1 = c[0] - c[-1] if not np.isnan(c[-1]) else np.nan
        rec = dict(
            quarter=row["quarter"], reaction_date=d0,
            runup_20d_excess_pct=c[-1],
            day1_excess_pct=day1,
            drift_5d_excess_pct=c[5] - c[0] if not np.isnan(c[5]) else np.nan,
            drift_20d_excess_pct=c[20] - c[0] if not np.isnan(c[20]) else np.nan,
            drift_60d_excess_pct=c[60] - c[0] if not np.isnan(c[60]) else np.nan,
            cum_20d_incl_day1=c[20] - c[-1] if not np.isnan(c[20]) else np.nan,
            excess_20d_from_release=c[19] - c[-1] if not np.isnan(c[19]) else np.nan,
            year=d0.year,
        )
        summ.append(rec)
    paths = pd.DataFrame(paths)
    summ = pd.DataFrame(summ)
    summ["day1_sign"] = np.where(summ.day1_excess_pct >= 0, "up", "down")
    return paths, summ


def drift_stats(summ: pd.DataFrame):
    rows = []
    for col, lab in [("runup_20d_excess_pct", "run-up -20..-1"),
                     ("day1_excess_pct", "day 1"),
                     ("drift_5d_excess_pct", "drift +1..+5"),
                     ("drift_20d_excess_pct", "drift +1..+20"),
                     ("drift_60d_excess_pct", "drift +1..+60"),
                     ("cum_20d_incl_day1", "day1..+20 total")]:
        for grp, dd in [("all", summ)] + [(f"day1_{g}", summ[summ.day1_sign == g])
                                          for g in ["up", "down"]] + \
                       [("from_2023", summ[summ.year >= 2023])]:
            x = dd[col].dropna()
            t, p, n = tstat(x)
            # Wilcoxon signed rank
            try:
                w, pw = stats.wilcoxon(x) if n >= 6 else (np.nan, np.nan)
            except Exception:
                w, pw = np.nan, np.nan
            rows.append(dict(window=lab, group=grp, n=n, mean_pct=x.mean(),
                             median_pct=x.median(), sd_pct=x.std(),
                             share_positive=(x > 0).mean(), t_stat=t, p_value=p,
                             wilcoxon_p=pw))
            log_test("2 drift", f"{lab} | {grp} mean=0", n, t, p)
    return pd.DataFrame(rows)


def drift_robustness(summ: pd.DataFrame, col="drift_20d_excess_pct"):
    """Leave-one-year-out and leave-one-print-out on the drift mean."""
    rows = []
    x = summ.dropna(subset=[col])
    full = x[col].mean()
    t, p, n = tstat(x[col])
    rows.append(dict(scheme="full", dropped="-", n=n, mean_pct=full, t_stat=t, p_value=p))
    for yr in sorted(x.year.unique()):
        d = x[x.year != yr]
        t, p, n = tstat(d[col])
        rows.append(dict(scheme="leave-one-year-out", dropped=str(yr), n=n,
                         mean_pct=d[col].mean(), t_stat=t, p_value=p))
    # drop the single most negative and most positive print
    for lab, d in [("drop_min", x.drop(x[col].idxmin())),
                   ("drop_max", x.drop(x[col].idxmax())),
                   ("drop_both_tails", x.drop([x[col].idxmin(), x[col].idxmax()]))]:
        t, p, n = tstat(d[col])
        rows.append(dict(scheme="leave-one-print-out", dropped=lab, n=n,
                         mean_pct=d[col].mean(), t_stat=t, p_value=p))
    log_test("2 drift", "20-day drift leave-one-year-out and tail drops", len(x),
             note=f"{len(rows)} refits")
    return pd.DataFrame(rows)


# ================================================================ 3. SEASONALITY
def seasonality(px: pd.DataFrame):
    cols = ["ABNB", "QQQ", "BKNG", "EXPE", "TRAVEL_PX"]
    p = px.copy()
    p["TRAVEL_PX"] = np.nan  # placeholder, basket handled on returns below
    m = px[["ABNB", "QQQ", "BKNG", "EXPE", "MAR", "HLT", "SPY"]].resample("ME").last()
    mr = m.pct_change() * 100
    mr = mr[mr.index >= "2021-01-01"]
    mr["excess_QQQ"] = mr.ABNB - mr.QQQ
    mr["excess_BKNG"] = mr.ABNB - mr.BKNG
    mr["excess_EXPE"] = mr.ABNB - mr.EXPE
    mr["excess_OTA"] = mr.ABNB - mr[["BKNG", "EXPE"]].mean(axis=1)
    mr["month"] = mr.index.month
    mr["quarter"] = mr.index.quarter
    mr["year"] = mr.index.year

    rows = []
    for series in ["ABNB", "excess_QQQ", "excess_OTA"]:
        for mth, dd in mr.groupby("month"):
            x = dd[series].dropna()
            t, p_, n = tstat(x)
            rows.append(dict(grain="month", period=mth, series=series, n=n,
                             mean_pct=x.mean(), median_pct=x.median(),
                             share_positive=(x > 0).mean(), t_stat=t, p_value=p_))
            log_test("3 seasonality", f"{series} month {mth} mean=0", n, t, p_)
        for q, dd in mr.groupby("quarter"):
            x = dd[series].dropna()
            t, p_, n = tstat(x)
            rows.append(dict(grain="calendar_quarter", period=q, series=series, n=n,
                             mean_pct=x.mean(), median_pct=x.median(),
                             share_positive=(x > 0).mean(), t_stat=t, p_value=p_))
            log_test("3 seasonality", f"{series} calQ {q} mean=0", n, t, p_)
        # summer (May-Oct) vs winter
        for lab, mask in [("May-Oct", mr.month.isin([5, 6, 7, 8, 9, 10])),
                          ("Nov-Apr", ~mr.month.isin([5, 6, 7, 8, 9, 10]))]:
            x = mr.loc[mask, series].dropna()
            t, p_, n = tstat(x)
            rows.append(dict(grain="half_year", period=lab, series=series, n=n,
                             mean_pct=x.mean(), median_pct=x.median(),
                             share_positive=(x > 0).mean(), t_stat=t, p_value=p_))
            log_test("3 seasonality", f"{series} {lab} mean=0", n, t, p_)
    return pd.DataFrame(rows), mr


# ============================================================== 4. EVENT STUDY
EST_START, EST_END = -140, -21


def market_model_car(px: pd.DataFrame, event_dates, windows, bench="QQQ", label=""):
    """Estimate a+b*bench on [-140,-21], report abnormal returns over `windows`."""
    dates = px.index
    ra = px["ABNB"].pct_change() * 100
    rb = px[bench].pct_change() * 100
    out = []
    for d in event_dates:
        d = pd.Timestamp(d)
        # snap forward to the next trading session if the event fell on a holiday
        pos = dates.searchsorted(d)
        if pos >= len(dates):
            continue
        i0 = pos
        if i0 + EST_START < 1 or i0 + max(w[1] for w in windows) >= len(dates):
            continue
        est = slice(i0 + EST_START, i0 + EST_END)
        y = ra.iloc[est].values
        x = rb.iloc[est].values
        ok = ~(np.isnan(y) | np.isnan(x))
        if ok.sum() < 60:
            continue
        b, se, t, r2, resid = ols(y[ok], x[ok].reshape(-1, 1))
        sd = float(np.std(resid, ddof=2))
        rec = dict(event_date=dates[i0], label=label, beta=b[1], est_sd_pct=sd)
        for (lo, hi) in windows:
            sl = slice(i0 + lo, i0 + hi + 1)
            ar = ra.iloc[sl].values - (b[0] + b[1] * rb.iloc[sl].values)
            car = np.nansum(ar)
            k = hi - lo + 1
            rec[f"car_{lo}_{hi}"] = car
            rec[f"t_{lo}_{hi}"] = car / (sd * np.sqrt(k)) if sd > 0 else np.nan
        out.append(rec)
    return pd.DataFrame(out)


def event_group_stats(df: pd.DataFrame, group: str, windows):
    rows = []
    if df.empty:
        return pd.DataFrame(rows)
    for lab, dd in df.groupby(group):
        for (lo, hi) in windows:
            c = f"car_{lo}_{hi}"
            if c not in dd:
                continue
            x = dd[c].dropna()
            t, p, n = tstat(x)
            rows.append(dict(group=lab, window=f"[{lo},{hi}]", n=n,
                             mean_car_pct=x.mean(), median_car_pct=x.median(),
                             share_positive=(x > 0).mean(), t_stat=t, p_value=p))
            log_test("4 events", f"{lab} CAR[{lo},{hi}] mean=0", n, t, p)
    return pd.DataFrame(rows)


# ---- macro release dates (BLS schedule archives, fetched 2026-09-06 from
# https://www.bls.gov/schedule/<year>/home.htm and /schedule/news_release/cpi.htm).
# BLS blocks scripted requests, so the dates are inlined rather than re-fetched.
CPI_DATES = """2021-01-13 2021-02-10 2021-03-10 2021-04-13 2021-05-12 2021-06-10 2021-07-13
2021-08-11 2021-09-14 2021-10-13 2021-11-10 2021-12-10
2022-01-12 2022-02-10 2022-03-10 2022-04-12 2022-05-11 2022-06-10 2022-07-13 2022-08-10
2022-09-13 2022-10-13 2022-11-10 2022-12-13
2023-01-12 2023-02-14 2023-03-14 2023-04-12 2023-05-10 2023-06-13 2023-07-12 2023-08-10
2023-09-13 2023-10-12 2023-11-14 2023-12-12
2024-01-11 2024-02-13 2024-03-12 2024-04-10 2024-05-15 2024-06-12 2024-07-11 2024-08-14
2024-09-11 2024-10-10 2024-11-13 2024-12-11
2025-01-15 2025-02-12 2025-03-12 2025-04-10 2025-05-13 2025-06-11 2025-07-15 2025-08-12
2025-09-11 2025-10-24 2025-12-18
2026-01-13 2026-02-13 2026-03-11 2026-04-10 2026-05-12 2026-06-10 2026-07-14 2026-08-12""".split()

JOBS_DATES = """2021-01-08 2021-02-05 2021-03-05 2021-04-02 2021-05-07 2021-06-04 2021-07-02
2021-08-06 2021-09-03 2021-10-08 2021-11-05 2021-12-03
2022-01-07 2022-02-04 2022-03-04 2022-04-01 2022-05-06 2022-06-03 2022-07-08 2022-08-05
2022-09-02 2022-10-07 2022-11-04 2022-12-02
2023-01-06 2023-02-03 2023-03-10 2023-04-07 2023-05-05 2023-06-02 2023-07-07 2023-08-04
2023-09-01 2023-10-06 2023-11-03 2023-12-08
2024-01-05 2024-02-02 2024-03-08 2024-04-05 2024-05-03 2024-06-07 2024-07-05 2024-08-02
2024-09-06 2024-10-04 2024-11-01 2024-12-06
2025-01-10 2025-02-07 2025-03-07 2025-04-04 2025-05-02 2025-06-06 2025-07-03 2025-08-01
2025-09-05 2025-11-20 2025-12-16
2026-01-09 2026-02-11 2026-03-06 2026-04-03 2026-05-08 2026-06-05 2026-07-02 2026-08-07""".split()

# ---- named single events. Source column carries the provenance for each row.
NAMED_EVENTS = [
    ("2023-09-01", "SP500_announcement", "S&P DJI announces ABNB joins the S&P 500 (after the close, Fri); "
     "first session 2023-09-05. Source: research/notes/2026-09-05_abnb-major-moves.md event 33"),
    ("2023-09-18", "SP500_effective", "Index inclusion effective. Same source"),
    ("2023-09-05", "NYC_LL18_enforcement", "NYC Local Law 18 platform enforcement begins. Source: "
     "citadel-abnb/research/regulatory/factors.json REG-01. NOTE: same session as the S&P pop"),
    ("2024-06-21", "Barcelona_2028_phaseout", "Barcelona announces non-renewal of all tourist-apartment "
     "licences by 2028 (announced June 2024; exact session approximate). factors.json REG-22"),
    ("2025-05-19", "Spain_removal_order", "Spanish consumer ministry orders removal of listings. factors.json REG-02"),
    ("2025-12-01", "Spain_fine", "EUR64.1m Airbnb fine, December 2025 (month only). factors.json REG-02"),
    ("2026-05-19", "Spain_partial_annulment", "Court annuls material provisions of the Spanish registry. REG-03"),
    ("2026-05-20", "EU_STR_data_regulation", "EU short-term rental data-sharing regulation applies. REG-17"),
    ("2026-09-04", "EU_housing_act_draft", "Reuters: proposed EU rules would curb Airbnb. REG-25 / "
     "citadel-abnb/data/raw/regulatory/lseg/regulatory_news_headlines.json"),
    ("2025-05-13", "SummerRelease_2025", "2025 Summer Release: Airbnb Services + reimagined Experiences. "
     "Source: 1Q25 and 2Q25 shareholder letters ('since May 13, 2025')"),
    ("2026-05-20", "SummerRelease_2026", "2026 Summer Release. Source: 1Q26 shareholder letter"),
    ("2022-08-02", "Buyback_2.0bn", "$2bn authorisation, announced in the 2Q22 letter (same day as the print)"),
    ("2023-05-09", "Buyback_2.5bn", "$2.5bn authorisation, 1Q23 letter (same day as the print)"),
    ("2024-02-13", "Buyback_6.0bn", "$6bn authorisation, 4Q23 letter (same day as the print)"),
    ("2025-08-06", "Buyback_6.0bn_2", "$6bn authorisation, 2Q25 letter (same day as the print)"),
    ("2026-02-03", "AI_disintermediation_scare", "Hotel chains sign Google/Anthropic/OpenAI booking deals. "
     "major-moves event 40"),
    ("2025-04-03", "Tariffs_liberation_day", "major-moves event 36"),
    ("2025-04-09", "Tariffs_pause", "major-moves event 37"),
]


# ================================================== 5. IMPLIED VS REALISED MOVE
def atm_iv(tk, expiry, spot):
    ch = tk.option_chain(expiry)
    out = {}
    for side, df in (("call", ch.calls), ("put", ch.puts)):
        d = df.dropna(subset=["impliedVolatility"])
        d = d[(d.impliedVolatility > 0.01) & (d.impliedVolatility < 3)]
        if d.empty:
            continue
        d = d.assign(dist=(d.strike - spot).abs()).nsmallest(2, "dist")
        out[side] = float(np.average(d.impliedVolatility, weights=1 / (d.dist + 1e-6)))
    if not out:
        return np.nan
    return float(np.mean(list(out.values())))


def implied_vs_realised(px, prints):
    """Realised absolute day-1 move for every print, plus the one implied move we can
    actually observe today (two-expiry variance decomposition around the 5 Nov print)."""
    rows = []
    p = px["ABNB"]
    dates = px.index
    for _, r in prints.iterrows():
        d0 = r["reaction_date"]
        if d0 not in dates:
            continue
        i = dates.get_loc(d0)
        realised = (p.iloc[i] / p.iloc[i - 1] - 1) * 100
        hist = p.pct_change().iloc[i - 61:i - 1] * 100
        rv = float(hist.std(ddof=1))
        rows.append(dict(quarter=r["quarter"], reaction_date=d0,
                         realised_day1_pct=realised, abs_realised_day1_pct=abs(realised),
                         trailing_60d_daily_vol_pct=rv,
                         vol_multiple=abs(realised) / rv if rv else np.nan,
                         implied_move_pct=np.nan, implied_source=""))
    df = pd.DataFrame(rows)
    df["naive_implied_prior4_pct"] = df["abs_realised_day1_pct"].rolling(4).mean().shift(1)
    df["surprise_vs_naive_pct"] = df["abs_realised_day1_pct"] - df["naive_implied_prior4_pct"]

    live = {}
    try:
        import yfinance as yf
        tk = yf.Ticker("ABNB")
        spot = float(px["ABNB"].iloc[-1])
        exps = list(tk.options)
        pre = [e for e in exps if pd.Timestamp(e) < pd.Timestamp("2026-11-05")]
        post = [e for e in exps if pd.Timestamp(e) >= pd.Timestamp("2026-11-06")]
        e1, e2 = pre[-1], post[0]
        asof = pd.Timestamp("2026-09-06")
        t1 = (pd.Timestamp(e1) - asof).days / 365.25
        t2 = (pd.Timestamp(e2) - asof).days / 365.25
        iv1, iv2 = atm_iv(tk, e1, spot), atm_iv(tk, e2, spot)
        # Two estimators bracket the earnings jump.
        # (a) flat non-event vol: iv1 is the clean 47-day vol, so the jump is the only
        #     extra variance in the post-print expiry -> J = t2 * (iv2^2 - iv1^2)
        # (b) upper bound: attribute ALL the incremental total variance to the jump,
        #     i.e. treat the 28 extra calendar days as carrying no ordinary vol.
        jv_flat = t2 * (iv2 ** 2 - iv1 ** 2)
        jv_upper = iv2 ** 2 * t2 - iv1 ** 2 * t1
        sd_flat = float(np.sqrt(jv_flat)) * 100 if jv_flat > 0 else float("nan")
        sd_upper = float(np.sqrt(jv_upper)) * 100 if jv_upper > 0 else float("nan")
        live = dict(spot=spot, expiry_pre=e1, t1_years=round(t1, 4),
                    atm_iv_pre_pct=iv1 * 100, expiry_post=e2, t2_years=round(t2, 4),
                    atm_iv_post_pct=iv2 * 100,
                    jump_sd_flatvol_pct=sd_flat,
                    jump_sd_upper_bound_pct=sd_upper,
                    exp_abs_move_flatvol_pct=sd_flat * np.sqrt(2 / np.pi),
                    exp_abs_move_upper_pct=sd_upper * np.sqrt(2 / np.pi),
                    note="IVs are a single yfinance snapshot on strikes that are thin "
                         "60 days out; the two estimators bracket the truth. The event "
                         "premium normally only appears in the last 1-2 weeks.")
        # cross-check against the 5 Sep 2026 straddle ledger: if the Nov and Dec
        # straddles scale as sqrt(time) there is no distinct event premium yet.
        led = ROOT.parent / "citadel-abnb" / "data" / "processed" / "abnb_options_ledger.csv"
        if led.exists():
            L = pd.read_csv(led)
            a_ = L[(L.ticker == "ABNB")].sort_values("dte")
            if len(a_) >= 2:
                r1, r2 = a_.iloc[0], a_.iloc[1]
                live["ledger_straddle_near_pct"] = float(r1.straddle_pct_spot)
                live["ledger_straddle_far_pct"] = float(r2.straddle_pct_spot)
                live["ledger_sqrt_time_implied_far_pct"] = float(
                    r1.straddle_pct_spot * np.sqrt(r2.dte / r1.dte))
                live["ledger_event_premium_pts"] = float(
                    r1.straddle_pct_spot - r2.straddle_pct_spot * np.sqrt(r1.dte / r2.dte))
    except Exception as exc:
        live = dict(error=str(exc))
    return df, live


# ================================================ 6. SIMPLE-RULE BACKTESTS
COST_BP = 10.0  # round-trip transaction cost assumption, basis points


def fwd_excess(px, i0, h, bench="QQQ", short=False):
    if i0 + h >= len(px) or i0 < 0:
        return float("nan")
    a = (px["ABNB"].iloc[i0 + h] / px["ABNB"].iloc[i0] - 1) * 100
    b = (px[bench].iloc[i0 + h] / px[bench].iloc[i0] - 1) * 100
    x = a - b
    return (-x if short else x) - COST_BP / 100.0


def summarise_rule(name, trades, horizon, note=""):
    x = pd.Series([t["excess"] for t in trades]).dropna()
    yrs = pd.Series([t["year"] for t in trades]).loc[x.index]
    t, p, n = tstat(x)
    rec = dict(rule=name, horizon_sessions=horizon, n=n, hit_rate=(x > 0).mean(),
               mean_excess_pct=x.mean(), median_excess_pct=x.median(),
               sd_pct=x.std(), t_stat=t, p_value=p,
               cost_bp_per_trade=COST_BP, note=note)
    means, ts = [], []
    for yr in sorted(yrs.unique()):
        keep = x[yrs != yr]
        if len(keep) >= 3:
            tt, pp, nn = tstat(keep)
            means.append(keep.mean())
            ts.append(tt)
    rec["loyo_min_mean_pct"] = min(means) if means else float("nan")
    rec["loyo_max_mean_pct"] = max(means) if means else float("nan")
    rec["loyo_min_abs_t"] = min(abs(np.array(ts))) if ts else float("nan")
    rec["loyo_sign_stable"] = bool(means) and (np.sign(min(means)) == np.sign(max(means)))
    log_test("6 rules", f"{name} h={horizon}", n, t, p)
    return rec


def rules_backtest(px, summ, moves, prints):
    dates = px.index
    out, trade_rows = [], []
    print_idx = {d: dates.get_loc(d) for d in prints["reaction_date"] if d in dates}
    near_print = set()
    for d, i in print_idx.items():
        for k in range(-3, 4):
            if 0 <= i + k < len(dates):
                near_print.add(dates[i + k])

    def add(name, entries, horizons, short=False, note=""):
        for h in horizons:
            trades = []
            for d in entries:
                if d not in dates:
                    continue
                i = dates.get_loc(d)
                e = fwd_excess(px, i, h, short=short)
                if e == e:
                    trades.append(dict(date=d, year=d.year, excess=e))
                    trade_rows.append(dict(rule=name, horizon=h, entry_date=d,
                                           excess_pct=e))
            if trades:
                out.append(summarise_rule(name, trades, h, note))

    down = summ[summ.day1_excess_pct < 0]["reaction_date"].tolist()
    add("R1 buy close of day-1 after a down print", down, [20, 60],
        note="entry = reaction-day close; excess vs QQQ, 10bp cost")
    up = summ[summ.day1_excess_pct >= 0]["reaction_date"].tolist()
    add("R2 short close of day-1 after an up print", up, [20, 60], short=True,
        note="short ABNB vs long QQQ")
    add("R2b buy close of day-1 after an up print", up, [20, 60])

    trades3 = []
    for d in summ["reaction_date"]:
        if d not in dates:
            continue
        i = dates.get_loc(d)
        if i - 21 < 0:
            continue
        e = fwd_excess(px, i - 21, 20)
        if e == e:
            trades3.append(dict(date=dates[i - 21], year=d.year, excess=e))
            trade_rows.append(dict(rule="R3 buy -20d, sell at the release close",
                                   horizon=20, entry_date=dates[i - 21], excess_pct=e))
    if trades3:
        out.append(summarise_rule("R3 buy -20d, sell at the release close", trades3, 20,
                                  "exits at the release-day close; carries no event risk"))

    mv = moves.copy()
    mv["date"] = pd.to_datetime(mv["date"])
    big_down = [d for d in mv.loc[mv.move_pct <= -7, "date"] if d not in near_print]
    add("R4 buy a -7% non-earnings day", big_down, [5, 20, 60],
        note=str(len(big_down)) + " of " + str(int((mv.move_pct <= -7).sum())) +
             " >=7% down days are not within 3 sessions of a print")

    r = px["ABNB"].pct_change()
    three = (r < 0) & (r.shift(1) < 0) & (r.shift(2) < 0)
    ent5 = [d for d in dates[three.values] if d not in near_print]
    add("R5 buy after 3 consecutive down days", ent5, [5, 10, 20],
        note="overlapping windows; t-stats are optimistic")

    m = px[["ABNB", "QQQ"]].resample("ME").last()
    sig = (m["ABNB"].shift(1) / m["ABNB"].shift(12) - 1) - \
          (m["QQQ"].shift(1) / m["QQQ"].shift(12) - 1)
    nxt = m.pct_change().shift(-1) * 100
    mom = pd.DataFrame(dict(sig=sig, ex=nxt["ABNB"] - nxt["QQQ"])).dropna()
    mom["abs_sig"] = (m["ABNB"].shift(1) / m["ABNB"].shift(12) - 1).reindex(mom.index)
    for lab, mask in [("R6 12-1 momentum: long when relative 12-1 > 0", mom.sig > 0),
                      ("R6b 12-1 momentum: long when relative 12-1 < 0", mom.sig <= 0),
                      ("R6c 12-1 momentum: long when absolute 12-1 > 0", mom.abs_sig > 0),
                      ("R6d 12-1 momentum: long when absolute 12-1 < 0", mom.abs_sig <= 0)]:
        d = mom[mask]
        trades = [dict(date=i, year=i.year, excess=v - COST_BP / 100)
                  for i, v in d["ex"].items()]
        if trades:
            out.append(summarise_rule(lab, trades, 21, "calendar-month holding periods"))
            for t_ in trades:
                trade_rows.append(dict(rule=lab, horizon=21, entry_date=t_["date"],
                                       excess_pct=t_["excess"]))

    # R7 calendar rules that fell out of the seasonality block (in-sample by
    # construction; they are here so they face the same LOYO and cost treatment)
    mall = px[["ABNB", "QQQ"]].resample("ME").last().pct_change() * 100
    mall = mall[mall.index >= "2021-01-01"]
    mall["ex"] = mall.ABNB - mall.QQQ
    for lab, mth, short in [("R7 short ABNB vs QQQ through May", 5, True),
                            ("R7b long ABNB vs QQQ through February", 2, False),
                            ("R7c short ABNB vs QQQ through November", 11, True)]:
        d = mall[mall.index.month == mth]
        trades = [dict(date=i, year=i.year,
                       excess=(-v if short else v) - COST_BP / 100)
                  for i, v in d["ex"].items()]
        if trades:
            out.append(summarise_rule(lab, trades, 21,
                                      "calendar month; selected after looking at the "
                                      "seasonality table, so in-sample"))
            for t_ in trades:
                trade_rows.append(dict(rule=lab, horizon=21, entry_date=t_["date"],
                                       excess_pct=t_["excess"]))

    allm = mom["ex"]
    t, p, n = tstat(allm)
    out.append(dict(rule="B0 always long ABNB vs QQQ (monthly)", horizon_sessions=21,
                    n=n, hit_rate=float((allm > 0).mean()), mean_excess_pct=allm.mean(),
                    median_excess_pct=allm.median(), sd_pct=allm.std(), t_stat=t,
                    p_value=p, cost_bp_per_trade=0.0,
                    note="buy-and-hold benchmark that every rule has to beat"))
    log_test("6 rules", "B0 buy-and-hold monthly excess", n, t, p)
    return pd.DataFrame(out), pd.DataFrame(trade_rows)


# ==================================================== 7. POSITIONING
BUY_WORDS = {"buy", "outperform", "overweight", "strong buy", "positive", "add",
             "accumulate", "market outperform", "sector outperform", "conviction buy",
             "top pick", "outperformer"}
HOLD_WORDS = {"hold", "neutral", "market perform", "equal-weight", "equalweight",
              "sector perform", "peer perform", "in-line", "perform", "sector weight",
              "equal weight", "market weight", "mixed"}
SELL_WORDS = {"sell", "underperform", "underweight", "negative", "reduce",
              "sector underperform"}


def bucket(grade):
    g = str(grade).strip().lower()
    if g in BUY_WORDS:
        return "buy"
    if g in HOLD_WORDS:
        return "hold"
    if g in SELL_WORDS:
        return "sell"
    return "other"


def positioning(px, shares_out_m):
    dates = px.index
    px_ = px.copy()

    # ---- consensus rating panel from the action feed
    a = pd.read_csv(OUT / "09_analyst_actions.csv", parse_dates=["date"])
    a = a.sort_values("date")
    a["b"] = a["ToGrade"].map(bucket)
    a = a[a.b != "other"]
    latest = {}
    panel = []
    pt = {}
    for d, grp in a.groupby("date"):
        for _, r in grp.iterrows():
            latest[r["Firm"]] = r["b"]
            if r.get("currentPriceTarget", 0) and float(r["currentPriceTarget"]) > 0:
                pt[r["Firm"]] = (float(r["currentPriceTarget"]), d)
        n = len(latest)
        # only price targets set in the last 400 days count
        live_pt = [v for v, dd in pt.values() if (d - dd).days <= 400]
        panel.append(dict(date=d, n_firms=n,
                          share_buy=sum(v == "buy" for v in latest.values()) / n,
                          share_hold=sum(v == "hold" for v in latest.values()) / n,
                          share_sell=sum(v == "sell" for v in latest.values()) / n,
                          mean_price_target=np.mean(live_pt) if live_pt else np.nan,
                          n_price_targets=len(live_pt)))
    panel = pd.DataFrame(panel).set_index("date")
    panel = panel.reindex(dates).ffill()
    panel["close"] = px_["ABNB"]
    panel["pt_premium_pct"] = (panel.mean_price_target / panel.close - 1) * 100

    # ---- short interest
    si = pd.read_csv(OUT / "09_short_interest.csv", parse_dates=["settlement_date"])
    si = si.sort_values("settlement_date")
    si["shares_out_m"] = si["settlement_date"].map(
        lambda d: shares_out_m.asof(d) if len(shares_out_m) else np.nan)
    si["si_pct_shares"] = si.short_interest_shares / (si.shares_out_m * 1e6) * 100
    si["si_chg_pct_shares"] = si.si_pct_shares.diff()

    # publication lag: FINRA publishes ~8 calendar days after settlement
    si["knowable_date"] = si.settlement_date + pd.Timedelta(days=9)

    def fwd(d, h):
        pos = dates.searchsorted(pd.Timestamp(d))
        if pos + h >= len(dates) or pos >= len(dates):
            return np.nan
        return ((px_["ABNB"].iloc[pos + h] / px_["ABNB"].iloc[pos] - 1) -
                (px_["QQQ"].iloc[pos + h] / px_["QQQ"].iloc[pos] - 1)) * 100

    for h, lab in [(21, "fwd_1m_excess_pct"), (63, "fwd_3m_excess_pct")]:
        si[lab] = si.knowable_date.map(lambda d: fwd(d, h))

    tests = []
    for xcol in ["si_pct_shares", "si_chg_pct_shares"]:
        for ycol in ["fwd_1m_excess_pct", "fwd_3m_excess_pct"]:
            d = si[[xcol, ycol]].dropna()
            if len(d) < 8:
                continue
            r, p = stats.pearsonr(d[xcol], d[ycol])
            rs, ps = stats.spearmanr(d[xcol], d[ycol])
            tests.append(dict(block="short interest", x=xcol, y=ycol, n=len(d),
                              pearson_r=r, p_value=p, spearman_r=rs, spearman_p=ps))
            log_test("7 positioning", f"{xcol} vs {ycol}", len(d), r, p)

    # ratings vs forward return, sampled monthly to limit overlap
    pm = panel.resample("ME").last()
    pm["fwd_3m_excess_pct"] = pm.index.map(lambda d: fwd(d, 63))
    pm["fwd_1m_excess_pct"] = pm.index.map(lambda d: fwd(d, 21))
    pm["d_share_buy_3m"] = pm.share_buy.diff(3)
    for xcol in ["share_buy", "d_share_buy_3m", "pt_premium_pct"]:
        for ycol in ["fwd_1m_excess_pct", "fwd_3m_excess_pct"]:
            d = pm[[xcol, ycol]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(d) < 12:
                continue
            r, p = stats.pearsonr(d[xcol], d[ycol])
            rs, ps = stats.spearmanr(d[xcol], d[ycol])
            tests.append(dict(block="ratings", x=xcol, y=ycol, n=len(d),
                              pearson_r=r, p_value=p, spearman_r=rs, spearman_p=ps))
            log_test("7 positioning", f"{xcol} vs {ycol}", len(d), r, p)

    # price-target premium: overlapping monthly samples overstate significance, so
    # re-test on non-overlapping quarterly points and control for the trailing 3m move
    pq = panel.resample("QE").last()
    pq["fwd_3m_excess_pct"] = pq.index.map(lambda d: fwd(d, 63))
    pq["trail_3m_excess_pct"] = pq.index.map(lambda d: fwd(d, -63) if False else np.nan)
    close = panel["close"]
    qq = close.reindex(pq.index)
    bq = px_["QQQ"].resample("QE").last()
    pq["trail_3m_excess_pct"] = (qq.pct_change() - bq.pct_change()) * 100
    d = pq[["pt_premium_pct", "fwd_3m_excess_pct"]].dropna()
    if len(d) >= 8:
        r, p = stats.pearsonr(d.pt_premium_pct, d.fwd_3m_excess_pct)
        tests.append(dict(block="ratings", x="pt_premium_pct",
                          y="fwd_3m_excess_pct (non-overlapping quarterly)", n=len(d),
                          pearson_r=r, p_value=p, spearman_r=np.nan, spearman_p=np.nan))
        log_test("7 positioning", "pt_premium vs fwd 3m, non-overlapping quarterly",
                 len(d), r, p)
    d2 = pq[["pt_premium_pct", "fwd_3m_excess_pct", "trail_3m_excess_pct"]].dropna()
    if len(d2) >= 8:
        # partial correlation of the premium with the forward return, controlling for
        # the trailing 3-month excess move (price targets are sticky, so the premium is
        # mostly 'the stock just fell')
        def resid(y, x):
            A = np.column_stack([np.ones(len(x)), x])
            b, *_ = np.linalg.lstsq(A, y, rcond=None)
            return y - A @ b
        ry = resid(d2.fwd_3m_excess_pct.values, d2.trail_3m_excess_pct.values)
        rx = resid(d2.pt_premium_pct.values, d2.trail_3m_excess_pct.values)
        r, p = stats.pearsonr(rx, ry)
        tests.append(dict(block="ratings",
                          x="pt_premium_pct | trailing 3m excess",
                          y="fwd_3m_excess_pct (non-overlapping quarterly)", n=len(d2),
                          pearson_r=r, p_value=p, spearman_r=np.nan, spearman_p=np.nan))
        log_test("7 positioning", "pt_premium partial, controlling trailing 3m",
                 len(d2), r, p)
        r0, p0 = stats.pearsonr(d2.trail_3m_excess_pct, d2.fwd_3m_excess_pct)
        tests.append(dict(block="ratings", x="trail_3m_excess_pct",
                          y="fwd_3m_excess_pct (non-overlapping quarterly)", n=len(d2),
                          pearson_r=r0, p_value=p0, spearman_r=np.nan, spearman_p=np.nan))
        log_test("7 positioning", "trailing 3m excess vs forward 3m excess", len(d2), r0, p0)
        for lab, dsub in [("all", d2), ("from 2023", d2[d2.index >= "2023-01-01"])]:
            if len(dsub) < 8:
                continue
            rr, pp = stats.pearsonr(dsub.trail_3m_excess_pct, dsub.fwd_3m_excess_pct)
            r2_, p2_ = stats.pearsonr(dsub.pt_premium_pct, dsub.fwd_3m_excess_pct)
            tests.append(dict(block="ratings", x=f"trail_3m_excess_pct [{lab}]",
                              y="fwd_3m_excess_pct (non-overlapping quarterly)",
                              n=len(dsub), pearson_r=rr, p_value=pp,
                              spearman_r=np.nan, spearman_p=np.nan))
            tests.append(dict(block="ratings", x=f"pt_premium_pct [{lab}]",
                              y="fwd_3m_excess_pct (non-overlapping quarterly)",
                              n=len(dsub), pearson_r=r2_, p_value=p2_,
                              spearman_r=np.nan, spearman_p=np.nan))
            log_test("7 positioning", f"trailing vs forward 3m [{lab}]", len(dsub), rr, pp)
            log_test("7 positioning", f"pt premium vs forward 3m [{lab}]", len(dsub), r2_, p2_)
    # analyst action event study is done in the event-study block
    return panel, si, pm, pd.DataFrame(tests)


# ==================================================== FIGURES
def make_figures(roll, paths, summ, seas_mr, rules, si, panel, byper):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 130, "font.size": 8,
                         "axes.grid": True, "grid.alpha": 0.25,
                         "axes.spines.top": False, "axes.spines.right": False})

    # 1. rolling betas
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    r = roll.set_index("date")
    ax[0].plot(r.index, r.beta_QQQ, label="beta to QQQ", lw=1.2)
    ax[0].plot(r.index, r.beta_TRAVEL_orth, label="beta to travel basket (orth.)", lw=1.2)
    ax[0].plot(r.index, r.beta_XLY_orth, label="beta to XLY (orth.)", lw=1.0, alpha=.8)
    ax[0].axhline(1, color="k", lw=.6, ls=":")
    ax[0].legend(fontsize=7, ncol=3)
    ax[0].set_title("ABNB rolling 126-session factor betas (daily returns)")
    ax[1].plot(r.index, r.uni_beta_OTA, label="univariate beta to OTAs (BKNG/EXPE)", lw=1.2)
    ax[1].plot(r.index, r.uni_beta_HOTELS, label="univariate beta to hotels (MAR/HLT/H)", lw=1.2)
    ax[1].axhline(1, color="k", lw=.6, ls=":")
    ax[1].legend(fontsize=7)
    ax[1].set_title("Beta to OTAs vs hotels")
    fig.tight_layout()
    fig.savefig(FIG / "09_rolling_betas.png")
    plt.close(fig)

    # 2. variance decomposition by year
    yrs = byper[byper["sample"].str.fullmatch(r"\d{4}")].set_index("sample")
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    cols = ["var_share_market", "var_share_consumer", "var_share_travel",
            "var_share_macro", "var_share_idio"]
    labs = ["QQQ", "XLY (orth.)", "travel (orth.)", "rates+USD", "idiosyncratic"]
    bottom = np.zeros(len(yrs))
    for c, l in zip(cols, labs):
        ax[0].bar(yrs.index, yrs[c] * 100, bottom=bottom, label=l)
        bottom += yrs[c].values * 100
    ax[0].set_ylabel("% of daily return variance")
    ax[0].set_title("Where ABNB's daily variance comes from")
    ax[0].legend(fontsize=6.5, ncol=2)
    ax[1].plot(yrs.index, yrs.ann_vol_pct, marker="o", label="total vol (ann.)")
    ax[1].plot(yrs.index, yrs.ann_idio_vol_pct, marker="o", label="idiosyncratic vol (ann.)")
    ax[1].set_ylabel("%")
    ax[1].set_title("Annualised volatility")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "09_variance_decomposition.png")
    plt.close(fig)

    # 3. earnings drift
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
    piv = paths.pivot_table(index="k", columns="quarter", values="cum_excess_pct")
    for q in piv.columns:
        ax[0].plot(piv.index, piv[q], color="0.75", lw=.6)
    ax[0].plot(piv.index, piv.mean(axis=1), color="C3", lw=2, label="mean, all prints")
    ax[0].axvline(0, color="k", lw=.8)
    ax[0].axhline(0, color="k", lw=.5)
    ax[0].set_xlabel("sessions relative to the reaction day")
    ax[0].set_ylabel("cumulative excess vs QQQ, %")
    ax[0].set_title("Excess return path around 23 prints")
    ax[0].legend(fontsize=7)
    for sign, col in [("up", "C0"), ("down", "C1")]:
        qs = summ[summ.day1_sign == sign].quarter
        sub = piv[[q for q in piv.columns if q in set(qs)]]
        # re-anchor at day 0 to show post-print drift only
        post = sub.loc[0:].sub(sub.loc[0])
        ax[1].plot(post.index, post.mean(axis=1), color=col, lw=2,
                   label=f"day-1 move was {sign} (n={sub.shape[1]})")
    ax[1].axhline(0, color="k", lw=.5)
    ax[1].set_xlabel("sessions after the reaction day")
    ax[1].set_ylabel("mean excess vs QQQ from day 0 close, %")
    ax[1].set_title("Post-print drift by sign of the day-1 move")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "09_earnings_drift.png")
    plt.close(fig)

    # 4. seasonality
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    g = seas_mr.groupby("month")[["ABNB", "excess_QQQ", "excess_OTA"]].mean()
    ax[0].bar(g.index - 0.2, g.ABNB, width=.4, label="ABNB total")
    ax[0].bar(g.index + 0.2, g.excess_QQQ, width=.4, label="excess vs QQQ")
    ax[0].axhline(0, color="k", lw=.6)
    ax[0].set_xticks(range(1, 13))
    ax[0].set_title("Mean monthly return by calendar month, 2021-26")
    ax[0].set_ylabel("%")
    ax[0].legend(fontsize=7)
    ax[1].bar(g.index, g.excess_OTA, color="C4")
    ax[1].axhline(0, color="k", lw=.6)
    ax[1].set_xticks(range(1, 13))
    ax[1].set_title("ABNB minus the BKNG/EXPE average")
    ax[1].set_ylabel("%")
    fig.tight_layout()
    fig.savefig(FIG / "09_seasonality.png")
    plt.close(fig)

    # 5. rules
    fig, ax = plt.subplots(figsize=(8, 4.6))
    d = rules.dropna(subset=["mean_excess_pct"]).copy()
    d["lab"] = d.rule.str.slice(0, 46) + " (h=" + d.horizon_sessions.astype(str) + ", n=" + d.n.astype(str) + ")"
    d = d.sort_values("mean_excess_pct")
    colors = ["C2" if v > 0 else "C3" for v in d.mean_excess_pct]
    ax.barh(d.lab, d.mean_excess_pct, color=colors)
    for y, (m, t) in enumerate(zip(d.mean_excess_pct, d.t_stat)):
        ax.text(m + (0.3 if m > 0 else -0.3), y, f"t={t:.1f}", va="center",
                ha="left" if m > 0 else "right", fontsize=6.5)
    ax.axvline(0, color="k", lw=.6)
    ax.set_xlabel("mean excess return vs QQQ per trade, % (after 10bp cost)")
    ax.set_title("Simple rules: mean excess return and t-stat")
    fig.tight_layout()
    fig.savefig(FIG / "09_rules_backtest.png")
    plt.close(fig)

    # 6. positioning
    fig, ax = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    ax[0].plot(si.settlement_date, si.si_pct_shares, marker=".", lw=1)
    ax[0].set_ylabel("short interest, % of shares out")
    ax[0].set_title("Short interest and sell-side rating mix")
    ax2 = ax[1]
    ax2.plot(panel.index, panel.share_buy * 100, label="% Buy", lw=1.2)
    ax2.plot(panel.index, panel.share_hold * 100, label="% Hold", lw=1.2)
    ax2.plot(panel.index, panel.share_sell * 100, label="% Sell", lw=1.2)
    ax2.set_ylabel("% of covering firms")
    ax2.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "09_positioning.png")
    plt.close(fig)


# ==================================================== MAIN
def main():
    px = load_prices()
    r = build_returns(px)
    f = factor_frame(r)

    byper, roll = run_factor_model(f)
    byper.to_csv(OUT / "09_factor_model_by_period.csv", index=False)
    roll.to_csv(OUT / "09_factor_betas_rolling.csv", index=False)

    # Fama-French 5 + momentum, so the style exposure is on the record too
    ff = pd.read_csv(OUT / "09_ff_factors_daily.csv", parse_dates=["date"]).set_index("date")
    ffc = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
    dff = pd.concat([r["ABNB"].rename("abnb"), ff[ffc + ["rf"]]], axis=1).dropna()
    dff["exret"] = dff["abnb"] - dff["rf"]
    ffrows = []
    for lab, dd in [("full", dff), ("from_2023", dff[dff.index >= "2023-01-01"])] +                    [(str(y), g) for y, g in dff.groupby(dff.index.year) if len(g) > 60]:
        b, se, t, r2, res = ols(dd["exret"].values, dd[ffc].values)
        rec = dict(sample=lab, n=len(dd), r2=r2, alpha_bp_day=b[0] * 100, alpha_t=t[0])
        for i, k in enumerate(ffc):
            rec[f"beta_{k}"] = b[i + 1]
            rec[f"t_{k}"] = t[i + 1]
        ffrows.append(rec)
    pd.DataFrame(ffrows).to_csv(OUT / "09_ff_factor_model.csv", index=False)
    log_test("1 factor", "Fama-French 5 + momentum, 8 samples x 6 betas", len(dff),
             note="48 coefficient t-tests")

    prints = pd.read_csv(PROC / "abnb_earnings_reactions.csv",
                         parse_dates=["reaction_date"])
    pxi = px.dropna(subset=["ABNB"]).copy()

    paths, summ = earnings_drift(pxi, prints)
    paths.to_csv(OUT / "09_earnings_drift_paths.csv", index=False)
    summ.to_csv(OUT / "09_earnings_drift_by_print.csv", index=False)
    stats_df = drift_stats(summ)
    stats_df.to_csv(OUT / "09_earnings_drift_stats.csv", index=False)
    rob = drift_robustness(summ)
    rob.to_csv(OUT / "09_earnings_drift_robustness.csv", index=False)

    # run-up vs day 1
    d = summ[["runup_20d_excess_pct", "day1_excess_pct", "drift_20d_excess_pct"]].dropna()
    extra = []
    for a, b in [("runup_20d_excess_pct", "day1_excess_pct"),
                 ("runup_20d_excess_pct", "drift_20d_excess_pct"),
                 ("day1_excess_pct", "drift_20d_excess_pct")]:
        dd = summ[[a, b]].dropna()
        rr, pp = stats.pearsonr(dd[a], dd[b])
        rs, ps = stats.spearmanr(dd[a], dd[b])
        extra.append(dict(x=a, y=b, n=len(dd), pearson_r=rr, p_value=pp,
                          spearman_r=rs, spearman_p=ps))
        log_test("2 drift", f"{a} vs {b}", len(dd), rr, pp)
    pd.DataFrame(extra).to_csv(OUT / "09_runup_vs_reaction.csv", index=False)

    seas, mr = seasonality(pxi)
    seas.to_csv(OUT / "09_seasonality.csv", index=False)
    mr.to_csv(OUT / "09_monthly_returns.csv")

    # ---------------- event studies ----------------
    W = [(0, 0), (0, 1), (0, 5), (0, 20), (-1, 1), (-5, -1)]
    ev_frames = []

    peers = pd.read_csv(PROC / "predictive" / "02_peer_prints.csv")
    own = set(pd.to_datetime(prints.reaction_date))
    own_window = set()
    for dt0 in own:
        for k in range(-2, 3):
            own_window.add(dt0 + pd.Timedelta(days=k))
    for tk, col in [("BKNG", "bkng_reaction_date"), ("EXPE", "expe_reaction_date"),
                    ("MAR", "mar_reaction_date"), ("HLT", "hlt_reaction_date")]:
        ds = pd.to_datetime(peers[col].dropna())
        ds = [x for x in ds if x not in own_window]
        e = market_model_car(pxi, ds, W, label=f"peer print {tk}")
        ev_frames.append(e)

    ev_frames.append(market_model_car(pxi, pd.to_datetime(CPI_DATES), W, label="CPI release"))
    ev_frames.append(market_model_car(pxi, pd.to_datetime(JOBS_DATES), W, label="jobs report"))

    a = pd.read_csv(OUT / "09_analyst_actions.csv", parse_dates=["date"])
    a["b_to"] = a.ToGrade.map(bucket)
    a["b_from"] = a.FromGrade.map(bucket)
    rank = {"sell": 0, "hold": 1, "buy": 2}
    a["upgrade"] = a.apply(lambda x: rank.get(x.b_to, np.nan) > rank.get(x.b_from, np.nan)
                           if x.b_to in rank and x.b_from in rank else False, axis=1)
    a["downgrade"] = a.apply(lambda x: rank.get(x.b_to, np.nan) < rank.get(x.b_from, np.nan)
                             if x.b_to in rank and x.b_from in rank else False, axis=1)
    groups = {
        "analyst upgrade": a.loc[a.upgrade, "date"],
        "analyst downgrade": a.loc[a.downgrade, "date"],
        "analyst initiation": a.loc[a.Action == "init", "date"],
        "PT raise": a.loc[a.priceTargetAction == "Raises", "date"],
        "PT cut": a.loc[a.priceTargetAction == "Lowers", "date"],
    }
    for lab, ds in groups.items():
        ds = pd.to_datetime(ds)
        keep = [x for x in ds if x not in own_window]
        ev_frames.append(market_model_car(pxi, keep, W, label=f"{lab} (ex-print week)"))
        ev_frames.append(market_model_car(pxi, list(ds), W, label=f"{lab} (all)"))

    named = market_model_car(pxi, [d for d, _, _ in NAMED_EVENTS], W, label="named")
    nm = pd.DataFrame(NAMED_EVENTS, columns=["date", "name", "source"])
    nm["date"] = pd.to_datetime(nm["date"])
    named = named.merge(nm.rename(columns={"date": "raw_date"}),
                        left_on="event_date", right_on="raw_date", how="left")
    if named["name"].isna().any():  # dates snapped forward to the next session
        for i, row in named[named["name"].isna()].iterrows():
            cand = nm[(nm.raw_date <= row.event_date) &
                      (nm.raw_date > row.event_date - pd.Timedelta(days=5))]
            if len(cand):
                named.loc[i, "name"] = cand.iloc[-1]["name"]
                named.loc[i, "source"] = cand.iloc[-1]["source"]
    named = named.drop_duplicates(subset=["event_date", "name"])
    named["label"] = "named: " + named["name"].astype(str)
    ev_frames.append(named)

    events = pd.concat(ev_frames, ignore_index=True)
    events.to_csv(OUT / "09_event_study_events.csv", index=False)
    esum = event_group_stats(events[~events.label.str.startswith("named")], "label", W)
    esum.to_csv(OUT / "09_event_study_summary.csv", index=False)

    # ---------------- options ----------------
    ivr, live = implied_vs_realised(pxi, prints)
    for k, v in live.items():
        ivr[f"live_{k}"] = v
    ivr.to_csv(OUT / "09_implied_vs_realised.csv", index=False)
    (OUT / "09_implied_move_live.json").write_text(json.dumps(live, indent=2, default=str))

    # ---------------- rules ----------------
    moves = pd.read_csv(PROC / "abnb_major_moves_events.csv")
    rules, trades = rules_backtest(pxi, summ, moves, prints)
    rules.to_csv(OUT / "09_rules_backtest.csv", index=False)
    trades.to_csv(OUT / "09_rules_trades.csv", index=False)

    # ---------------- positioning ----------------
    cap = pd.read_csv(PROC / "abnb_capital_return_quarterly.csv")

    def qend(q):
        n, y = q[0], q[2:]
        return pd.Period(f"20{y}Q{n}", freq="Q").end_time.normalize()

    cap["date"] = cap["quarter"].map(qend)
    shares = cap.set_index("date")["basic_wa_shares_m"].sort_index()
    panel, si, pm, ptests = positioning(pxi, shares)
    panel.to_csv(OUT / "09_positioning_ratings.csv")
    si.to_csv(OUT / "09_positioning_short_interest.csv", index=False)
    pm.to_csv(OUT / "09_positioning_ratings_monthly.csv")
    ptests.to_csv(OUT / "09_positioning_tests.csv", index=False)

    # ---- 13F concentration: only a single public snapshot is free, so no time series
    inst = pd.DataFrame([
        dict(as_of="2026-06-30", metric="institutional holders", value=2210,
             unit="count", source="fintel.io/so/us/abnb, fetched 2026-09-06"),
        dict(as_of="2026-06-30", metric="institutional shares held (long)",
             value=468934053, unit="shares", source="fintel.io/so/us/abnb"),
        dict(as_of="2026-06-30", metric="top-5 holders share of disclosed shares",
             value=22.43, unit="%", source="fintel.io/so/us/abnb"),
        dict(as_of="2026-06-30", metric="top-10 holders share of disclosed shares",
             value=33.15, unit="%", source="fintel.io/so/us/abnb"),
        dict(as_of="2026-06-30", metric="institutions increasing / decreasing",
             value=1020 / 884, unit="ratio", source="fintel.io/so/us/abnb"),
    ])
    inst.to_csv(OUT / "09_institutional_snapshot.csv", index=False)

    # ---- reconcile our post-print excess with the file the team already uses
    theo = prints.rename(columns={"excess_20d_pct": "theo_excess_20d_pct"})
    rec = summ.merge(theo[["quarter", "theo_excess_20d_pct", "excess_1d_pct"]],
                     on="quarter", how="left")
    rec["diff_20d"] = rec.excess_20d_from_release - rec.theo_excess_20d_pct
    rec["diff_1d"] = rec.day1_excess_pct - rec.excess_1d_pct
    rec[["quarter", "reaction_date", "day1_excess_pct", "excess_1d_pct", "diff_1d",
         "excess_20d_from_release", "theo_excess_20d_pct", "diff_20d"]].to_csv(
        OUT / "09_reconciliation_vs_existing.csv", index=False)

    pd.DataFrame(TEST_LEDGER).to_csv(OUT / "09_test_ledger.csv", index=False)

    make_figures(roll, paths, summ, mr, rules, si, panel, byper)

    print("tests run:", len(TEST_LEDGER))
    print(byper[["sample", "n", "beta_QQQ", "beta_TRAVEL_orth", "var_share_idio",
                 "ann_vol_pct", "ann_idio_vol_pct"]].to_string(index=False))
    print(stats_df[stats_df.group == "all"].to_string(index=False))
    print(rules[["rule", "horizon_sessions", "n", "hit_rate", "mean_excess_pct",
                 "t_stat", "p_value", "loyo_sign_stable"]].to_string(index=False))
    print("live implied:", live)


if __name__ == "__main__":
    main()
