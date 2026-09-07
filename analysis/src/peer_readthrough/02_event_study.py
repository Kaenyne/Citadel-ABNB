"""
02_event_study.py - does ABNB's stock trade on other travel companies' earnings days?

Question: analysts get BKNG/EXPE room nights and MAR/HLT RevPAR days before Airbnb prints. Is that
information the market puts into ABNB, and how much?

Inputs
  data/raw/prices/peer_event_closes.csv    daily adjusted closes (01_fetch.py)
  data/raw/peers/earnings_8k_dates.csv     8-K Item 2.02 filing dates + Eastern acceptance times (01_fetch.py)

Method
  Reaction day  = the filing date when the 8-K was accepted before 16:00 ET, otherwise the next trading day.
  Abnormal return (AR) = residual of a market model r_i = a + b*r_QQQ fitted on the 250 trading days ending
  6 sessions before the event (so the estimation window never contains the event). Days without a full
  window are dropped. The same model is applied to ABNB and to every peer.
  ABNB's own volatility regime fell a lot between 2021 and 2026, so every |AR| test is run twice: on raw AR
  and on AR/sigma, where sigma is the standard deviation of ABNB's AR over the 120 sessions ending 6 days
  before (the same lag as the beta window). The permutation baseline is also era-matched - draws are taken
  from ordinary days in the same calendar years, in the same proportions as the event set.

Tests
  A  Unconditional: mean AR_ABNB and mean |AR_ABNB| on each peer's reaction days vs the baseline of ordinary
     days (no ABNB print, no peer print). t-tests are two-sided; a permutation test (2,000 era-matched draws
     of date sets the same size, seed 0) gives an exact-ish p on |AR|, which is fat-tailed.
  B  Conditional readthrough beta: AR_ABNB = a + b*AR_peer, fitted on the peer's reaction days and, for
     comparison, on ordinary days. b_event - b_ordinary is the extra co-movement bought by the print itself.
     Newey-West (lag 1) standard errors.
  C  Does it stick? Post-event cumulative AR_ABNB over t+1..t+5 conditional on the sign of the day-0 AR.

Outputs (data/processed/peer_readthrough/)
  02_event_days.csv        one row per peer reaction day with AR_ABNB, AR_peer and post-event windows
  02_peer_summary.csv      tests A + B + C per peer, per group, and by era
  02_baseline.csv          the ordinary-day distribution the tests compare against
  02_abnb_top_moves.csv    ABNB's largest abnormal days tagged with any industry print on the same day

Run: py -3.13 analysis/src/peer_readthrough/02_event_study.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "peer_readthrough"
OUT.mkdir(parents=True, exist_ok=True)
EST_WIN, EST_GAP, N_PERM, SEED = 250, 6, 2000, 0

GROUP = {"BKNG": "OTA", "EXPE": "OTA", "TRIP": "OTA", "SABR": "Distribution",
         "MAR": "Hotel", "HLT": "Hotel", "H": "Hotel", "WH": "Hotel", "CHH": "Hotel",
         "HGV": "Timeshare", "TNL": "Timeshare", "VAC": "Timeshare",
         "DAL": "Airline", "UAL": "Airline", "LUV": "Airline", "RCL": "Cruise", "CCL": "Cruise"}


def load():
    px = pd.read_csv(ROOT / "data/raw/prices/peer_event_closes.csv", parse_dates=["date"]).set_index("date")
    px = px.dropna(axis=1, how="all")
    ret = px.pct_change() * 100
    ev = pd.read_csv(ROOT / "data/raw/peers/earnings_8k_dates.csv", parse_dates=["filing_date"])
    ev["hour_et"] = ev["acceptance_et"].str[11:13].astype(int)
    sessions = ret.index

    def reaction(row):
        d, h = row["filing_date"], row["hour_et"]
        on_or_after = sessions[sessions >= d]
        if len(on_or_after) == 0:
            return pd.NaT
        if on_or_after[0] == d and h < 16:
            return d
        after = sessions[sessions > d]
        return after[0] if len(after) else pd.NaT

    ev["reaction_date"] = ev.apply(reaction, axis=1)
    ev["premarket"] = ev["hour_et"] < 16
    return ret, ev.dropna(subset=["reaction_date"])


def abnormal(ret, tickers):
    """Market-model residuals vs QQQ; betas from the 250 sessions ending EST_GAP days before each date."""
    mkt = ret["QQQ"]
    ar = pd.DataFrame(index=ret.index, columns=tickers, dtype=float)
    n = len(ret.index)
    for t in tickers:
        r = ret[t]
        vals = np.full(n, np.nan)
        for i in range(n):
            lo, hi = i - EST_GAP - EST_WIN, i - EST_GAP
            if lo < 0:
                continue
            y, x = r.iloc[lo:hi], mkt.iloc[lo:hi]
            ok = y.notna() & x.notna()
            if ok.sum() < 120 or not np.isfinite(r.iloc[i]) or not np.isfinite(mkt.iloc[i]):
                continue
            b, a = np.polyfit(x[ok], y[ok], 1)
            vals[i] = r.iloc[i] - (a + b * mkt.iloc[i])
        ar[t] = vals
    return ar


def nw_ols(y, X, lag=1):
    """OLS with Newey-West standard errors. X passed without an intercept column."""
    n = len(y)
    X1 = np.column_stack([np.ones(n), X])
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    e = y - X1 @ b
    XtXi = np.linalg.pinv(X1.T @ X1)
    Z = X1 * e[:, None]
    S = Z.T @ Z
    for L in range(1, lag + 1):
        w = 1 - L / (lag + 1)
        G = Z[L:].T @ Z[:-L]
        S += w * (G + G.T)
    se = np.sqrt(np.diag(XtXi @ S @ XtXi))
    return b, se


def main():
    ret, ev = load()
    tickers = [t for t in GROUP if t in ret.columns] + ["ABNB"]
    ar = abnormal(ret, tickers)

    abnb_days = set(ev.loc[ev.ticker == "ABNB", "reaction_date"])
    peer_ev = ev[(ev.ticker != "ABNB") & ev.ticker.isin(GROUP)].copy()
    peer_ev["group"] = peer_ev.ticker.map(GROUP)
    all_peer_days = set(peer_ev["reaction_date"])

    # trailing volatility of ABNB's own abnormal return, lagged like the beta window
    sigma = ar["ABNB"].rolling(120, min_periods=60).std().shift(EST_GAP)
    arz = ar["ABNB"] / sigma

    idx = ar.index
    pos = {d: i for i, d in enumerate(idx)}
    rows = []
    for _, r in peer_ev.iterrows():
        d, tk = r["reaction_date"], r["ticker"]
        i = pos.get(d)
        if i is None or not np.isfinite(ar.at[d, "ABNB"]) or not np.isfinite(ar.at[d, tk]):
            continue
        post = ar["ABNB"].iloc[i + 1:i + 6]
        rows.append(dict(reaction_date=d, ticker=tk, group=r["group"], filing_date=r["filing_date"].date(),
                         premarket=r["premarket"], ar_peer=round(ar.at[d, tk], 3), ar_abnb=round(ar.at[d, "ABNB"], 3),
                         z_abnb=round(arz.at[d], 3) if np.isfinite(arz.at[d]) else np.nan,
                         ret_abnb=round(ret.at[d, "ABNB"], 3), ret_peer=round(ret.at[d, tk], 3),
                         ret_qqq=round(ret.at[d, "QQQ"], 3), year=d.year,
                         car_abnb_1_5=round(post.sum(), 3) if post.notna().all() else np.nan,
                         abnb_print_same_day=d in abnb_days))
    ed = pd.DataFrame(rows).sort_values("reaction_date").reset_index(drop=True)
    ed.to_csv(OUT / "02_event_days.csv", index=False)

    base_mask = (~idx.isin(abnb_days)) & (~idx.isin(all_peer_days)) & ar["ABNB"].notna()
    base = ar.loc[base_mask, "ABNB"]
    base_z = arz.loc[base_mask].dropna()
    own = ar.loc[idx.isin(abnb_days) & ar["ABNB"].notna(), "ABNB"]
    pd.DataFrame({"date": base.index, "ar_abnb": base.round(3),
                  "z_abnb": arz.loc[base_mask].round(3)}).to_csv(OUT / "02_baseline.csv", index=False)
    rng = np.random.default_rng(SEED)
    base_abs = np.abs(base.values)
    # ordinary-day pools split by calendar year, so a permutation draw can match the event set's era mix
    by_year = {y: g.values for y, g in base.groupby(base.index.year)}
    by_year_z = {y: g.values for y, g in base_z.groupby(base_z.index.year)}

    def perm_p_absmean(year_counts, obs, pools):
        """Era-matched: draw the same number of ordinary days from each calendar year as the event set has."""
        draws = np.empty(N_PERM)
        for j in range(N_PERM):
            parts = [rng.choice(pools[y], min(k, len(pools[y])), replace=False) for y, k in year_counts.items() if y in pools]
            draws[j] = np.abs(np.concatenate(parts)).mean() if parts else np.nan
        return float((np.sum(draws >= obs) + 1) / (N_PERM + 1))

    clean = ed[~ed["abnb_print_same_day"]]

    def block(sub, label, kind):
        n = len(sub)
        if n < 6:
            return None
        a, p = sub["ar_abnb"].to_numpy(float), sub["ar_peer"].to_numpy(float)
        z = sub["z_abnb"].dropna().to_numpy(float)
        yc = sub["year"].value_counts().to_dict()
        t_mean = stats.ttest_1samp(a, 0)
        t_abs = stats.ttest_ind(np.abs(a), base_abs, equal_var=False)
        b_ev, se_ev = nw_ols(a, p[:, None])
        row = dict(scope=kind, name=label, n_events=n,
                   mean_ar_abnb=round(a.mean(), 3), t_mean=round(t_mean.statistic, 2), p_mean=round(t_mean.pvalue, 4),
                   mean_abs_ar_abnb=round(np.abs(a).mean(), 3), baseline_abs=round(base_abs.mean(), 3),
                   abs_ratio=round(np.abs(a).mean() / base_abs.mean(), 2),
                   p_abs_welch=round(t_abs.pvalue, 4),
                   p_abs_perm_eramatched=round(perm_p_absmean(yc, np.abs(a).mean(), by_year), 4),
                   mean_abs_z=round(np.abs(z).mean(), 3) if len(z) else np.nan,
                   baseline_abs_z=round(np.abs(base_z.values).mean(), 3),
                   z_ratio=round(np.abs(z).mean() / np.abs(base_z.values).mean(), 2) if len(z) else np.nan,
                   p_absz_perm_eramatched=round(perm_p_absmean(yc, np.abs(z).mean(), by_year_z), 4) if len(z) >= 6 else np.nan,
                   share_abs_gt2=round(float((np.abs(a) > 2).mean()), 2),
                   baseline_share_gt2=round(float((base_abs > 2).mean()), 2),
                   beta_event=round(b_ev[1], 3), beta_event_se=round(se_ev[1], 3),
                   beta_event_t=round(b_ev[1] / se_ev[1], 2) if se_ev[1] else np.nan,
                   sign_concord=round(float(np.mean(np.sign(a) == np.sign(p))), 2),
                   corr_ar=round(float(np.corrcoef(a, p)[0, 1]), 3))
        if kind == "ticker":
            q = ar.loc[base_mask, ["ABNB", label]].dropna()
            b0, se0 = nw_ols(q["ABNB"].to_numpy(float), q[label].to_numpy(float)[:, None])
            row["beta_ordinary"] = round(b0[1], 3)
            row["beta_lift"] = round(b_ev[1] - b0[1], 3)
            row["beta_lift_t"] = round((b_ev[1] - b0[1]) / np.sqrt(se_ev[1] ** 2 + se0[1] ** 2), 2)
        s = sub.dropna(subset=["car_abnb_1_5"])
        if len(s) >= 6:
            row["car1_5_given_pos"] = round(s.loc[s.ar_abnb > 0, "car_abnb_1_5"].mean(), 3)
            row["car1_5_given_neg"] = round(s.loc[s.ar_abnb < 0, "car_abnb_1_5"].mean(), 3)
        return row

    res = []
    for tk in sorted(clean.ticker.unique()):
        r = block(clean[clean.ticker == tk], tk, "ticker")
        if r:
            res.append(r)
    for g in sorted(clean.group.unique()):
        r = block(clean[clean.group == g], g, "group")
        if r:
            res.append(r)
    oe = clean[clean.ticker.isin(["BKNG", "EXPE"])]
    big = clean[clean.ar_peer.abs() > 5]
    pooled = [("ALL peer prints", clean),
              ("BKNG+EXPE only", oe),
              ("Hotels only", clean[clean.group == "Hotel"]),
              ("2021-2023", clean[clean.reaction_date < "2024-01-01"]),
              ("2024-2026", clean[clean.reaction_date >= "2024-01-01"]),
              ("BKNG+EXPE 2021-2023", oe[oe.reaction_date < "2024-01-01"]),
              ("BKNG+EXPE 2024-2026", oe[oe.reaction_date >= "2024-01-01"]),
              ("Peer AR >5% (any peer)", big),
              ("Peer AR >5%, BKNG/EXPE", big[big.ticker.isin(["BKNG", "EXPE"])]),
              ("Peer AR >5%, hotels", big[big.group == "Hotel"]),
              ("Peer AR <=5% (any peer)", clean[clean.ar_peer.abs() <= 5])]
    for lbl, sub in pooled:
        r = block(sub, lbl, "pooled")
        if r:
            res.append(r)
    summary = pd.DataFrame(res)
    summary.to_csv(OUT / "02_peer_summary.csv", index=False)

    tag = peer_ev.groupby("reaction_date")["ticker"].apply(lambda s: " ".join(sorted(s)))
    top = ar["ABNB"].dropna().rename("ar_abnb").to_frame()
    top["ret_abnb"] = ret["ABNB"]
    top["ret_qqq"] = ret["QQQ"]
    top["abnb_print"] = top.index.isin(abnb_days)
    top["peers_reporting"] = top.index.map(tag).fillna("")
    top = top.reindex(top["ar_abnb"].abs().sort_values(ascending=False).index).head(60).round(2)
    top.index.name = "date"
    top.to_csv(OUT / "02_abnb_top_moves.csv")

    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 300)
    print(f"ABNB ordinary day:  mean|AR| = {base_abs.mean():.2f}%, n={len(base)}")
    print(f"ABNB own print day: mean|AR| = {np.abs(own.values).mean():.2f}%, n={len(own)}")
    print(f"peer reaction days: {len(ed)} ({len(clean)} after dropping days ABNB also printed)\n")
    cols = ["scope", "name", "n_events", "mean_ar_abnb", "p_mean", "mean_abs_ar_abnb", "abs_ratio",
            "p_abs_perm_eramatched", "z_ratio", "p_absz_perm_eramatched", "share_abs_gt2",
            "beta_event", "beta_event_t", "beta_ordinary", "beta_lift", "beta_lift_t", "corr_ar", "sign_concord"]
    print(summary[cols].to_string(index=False))
    print("\nPost-event drift (mean CAR t+1..t+5 given the sign of day 0):")
    print(summary[["scope", "name", "n_events", "car1_5_given_pos", "car1_5_given_neg"]].dropna().to_string(index=False))
    print("\nABNB's 35 largest abnormal days:")
    print(top.head(35).to_string())


if __name__ == "__main__":
    main()
