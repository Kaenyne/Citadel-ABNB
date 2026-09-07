"""
05_mechanism_and_tradeability.py - why Expedia and not Booking, and is any of it capturable?

Follow-ups to 02/03. Two questions, five tests.

WHY EXPEDIA
  M1  Is it just that Expedia moves more? EXPE's own mean |AR| on its print is 10.2% against BKNG's 4.0%,
      and a bigger signal is easier to detect. Re-run each name on its large prints only (|AR_peer| > 5%),
      where both have comparable signal, and compare.
  M2  Is Booking's earnings move industry news at all? On each peer's reaction day, measure the abnormal
      return of every OTHER travel name. If nobody moves with Booking, its prints are company-specific and
      there is nothing for Airbnb to read. Reported as a response matrix.
  M3  Does Airbnb respond to Booking's numbers even though it ignores Booking's stock? Regress ABNB's
      abnormal return on the peer's reported room-nights growth and acceleration (from 02_peer_prints.csv)
      rather than on the peer's stock move.
  M4  Ordinary-day co-movement. If Airbnb simply trades more like Expedia, its everyday beta to EXPE should
      exceed its beta to BKNG. (02 already reports the opposite; this restates it as the control.)

TRADEABILITY
  T1  Gap vs intraday. BKNG and EXPE release after the close, so Airbnb reacts the next session and opens
      with a gap. Split ABNB's reaction-day abnormal return into overnight (prior close -> open) and
      intraday (open -> close), both market-adjusted with QQQ's own gap and intraday leg. Whatever sits in
      the gap is only available in the thin after-hours session; whatever sits intraday is capturable at
      the open. Then regress the intraday leg alone on the peer's move: that slope is the tradeable one.
      A hit-rate and a naive P&L on the "buy/sell ABNB at the open in the direction of Expedia's move,
      exit at the close" rule is reported with a 10bp round-trip cost assumption.

Inputs   data/processed/peer_readthrough/02_event_days.csv, data/raw/prices/peer_event_closes.csv,
         data/raw/prices/peer_event_opens.csv, data/processed/predictive/02_peer_prints.csv
Outputs  data/processed/peer_readthrough/05_*.csv

Run: py -3.13 analysis/src/peer_readthrough/05_mechanism_and_tradeability.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data" / "processed" / "peer_readthrough"
EST_WIN, EST_GAP = 250, 6
COST_BPS = 10.0   # round-trip cost assumption for the naive P&L, in basis points


def market_model(ret, mkt, tickers):
    ar = pd.DataFrame(index=ret.index, columns=tickers, dtype=float)
    n = len(ret.index)
    for t in tickers:
        r, vals = ret[t], np.full(n, np.nan)
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


def main():
    ed = pd.read_csv(PROC / "02_event_days.csv", parse_dates=["reaction_date"])
    ed = ed[~ed.abnb_print_same_day]
    cl = pd.read_csv(ROOT / "data/raw/prices/peer_event_closes.csv", parse_dates=["date"]).set_index("date")
    op = pd.read_csv(ROOT / "data/raw/prices/peer_event_opens.csv", index_col=0, parse_dates=True)
    op.index.name = "date"
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 300)
    out = {}

    # ---------------- M1: large prints only, per name ----------------
    rows = []
    for tk in ["EXPE", "BKNG"]:
        for lab, sub in [("all prints", ed[ed.ticker == tk]),
                         ("|AR_peer| > 5%", ed[(ed.ticker == tk) & (ed.ar_peer.abs() > 5)]),
                         ("|AR_peer| > 8%", ed[(ed.ticker == tk) & (ed.ar_peer.abs() > 8)])]:
            if len(sub) < 4:
                continue
            x, y = sub.ar_peer.to_numpy(float), sub.ar_abnb.to_numpy(float)
            b = np.polyfit(x, y, 1)[0]
            rows.append(dict(ticker=tk, cut=lab, n=len(sub), mean_abs_ar_peer=round(np.abs(x).mean(), 2),
                             corr=round(float(np.corrcoef(x, y)[0, 1]), 3), slope=round(float(b), 3),
                             same_sign=round(float(np.mean(np.sign(x) == np.sign(y))), 2),
                             mean_abs_ar_abnb=round(float(np.abs(y).mean()), 2)))
    out["05_m1_large_prints"] = pd.DataFrame(rows)

    # ---------------- M2: cross-peer response matrix ----------------
    names = ["ABNB", "BKNG", "EXPE", "MAR", "HLT", "H", "WH", "CHH", "TRIP", "SABR", "DAL", "UAL", "RCL"]
    ret = cl.pct_change() * 100
    ar = market_model(ret, ret["QQQ"], names)
    rows = []
    for reporter in ["BKNG", "EXPE", "MAR", "HLT"]:
        days = ed.loc[ed.ticker == reporter, "reaction_date"]
        r = dict(reporter=reporter, n_days=len(days),
                 own_mean_abs_ar=round(float(ar.loc[days, reporter].abs().mean()), 2))
        for other in ["ABNB", "BKNG", "EXPE", "MAR", "HLT", "TRIP"]:
            if other == reporter:
                continue
            a = ar.loc[days, [reporter, other]].dropna()
            if len(a) >= 6:
                r[f"corr_{other}"] = round(float(np.corrcoef(a[reporter], a[other])[0, 1]), 2)
                r[f"beta_{other}"] = round(float(np.polyfit(a[reporter], a[other], 1)[0]), 3)
        rows.append(r)
    out["05_m2_response_matrix"] = pd.DataFrame(rows)

    # ---------------- M3: ABNB vs the peer's reported numbers ----------------
    pp = pd.read_csv(ROOT / "data/processed/predictive/02_peer_prints.csv")
    rows = []
    for tk, cols in [("bkng", ["bkng_room_nights_yoy", "bkng_room_nights_accel_pp", "bkng_gb_yoy"]),
                     ("expe", ["expe_room_nights_yoy", "expe_room_nights_accel_pp", "expe_gb_yoy"])]:
        d = pp[[f"{tk}_reaction_date"] + cols].rename(columns={f"{tk}_reaction_date": "reaction_date"})
        d["reaction_date"] = pd.to_datetime(d["reaction_date"])
        m = ed[ed.ticker == tk.upper()].merge(d, on="reaction_date", how="inner")
        for c in cols:
            s = m[[c, "ar_abnb", "ar_peer"]].dropna()
            if len(s) < 6:
                continue
            pr = stats.pearsonr(s[c], s.ar_abnb)
            pr2 = stats.pearsonr(s[c], s.ar_peer)
            rows.append(dict(signal=c, n=len(s), corr_with_abnb_ar=round(pr.statistic, 3), p_abnb=round(pr.pvalue, 4),
                             corr_with_own_ar=round(pr2.statistic, 3), p_own=round(pr2.pvalue, 4)))
    out["05_m3_fundamental_vs_stock"] = pd.DataFrame(rows)

    # ---------------- T1: gap vs intraday ----------------
    prev_close = cl.shift(1)
    gap = (op / prev_close - 1) * 100
    intra = (cl / op - 1) * 100
    rows = []
    ota = ed[ed.ticker.isin(["BKNG", "EXPE"])].copy()
    # market-adjust each leg with QQQ's own leg, using the same market-model beta as the daily AR
    # simple, transparent beta: rolling 250-day OLS of ABNB daily return on QQQ, lagged 6 days
    b_series = ret["ABNB"].rolling(EST_WIN).cov(ret["QQQ"]) / ret["QQQ"].rolling(EST_WIN).var()
    b_series = b_series.shift(EST_GAP)
    for _, r in ota.iterrows():
        d = r["reaction_date"]
        if d not in gap.index or not np.isfinite(b_series.get(d, np.nan)):
            continue
        b = float(b_series[d])
        g = float(gap.at[d, "ABNB"] - b * gap.at[d, "QQQ"])
        it = float(intra.at[d, "ABNB"] - b * intra.at[d, "QQQ"])
        rows.append(dict(reaction_date=d.date(), ticker=r["ticker"], ar_peer=r["ar_peer"], ar_abnb=r["ar_abnb"],
                         abnb_gap_adj=round(g, 3), abnb_intraday_adj=round(it, 3), beta_used=round(b, 2)))
    t1 = pd.DataFrame(rows)
    out["05_t1_gap_vs_intraday"] = t1

    summ = []
    for lab, sub in [("EXPE, all", t1[t1.ticker == "EXPE"]),
                     ("EXPE, |AR_peer|>5%", t1[(t1.ticker == "EXPE") & (t1.ar_peer.abs() > 5)]),
                     ("BKNG, all", t1[t1.ticker == "BKNG"]),
                     ("BKNG+EXPE, |AR_peer|>5%", t1[t1.ar_peer.abs() > 5])]:
        if len(sub) < 5:
            continue
        x = sub.ar_peer.to_numpy(float)
        row = dict(cut=lab, n=len(sub),
                   share_of_move_in_gap=round(float(sub.abnb_gap_adj.abs().mean() /
                                                    (sub.abnb_gap_adj.abs().mean() + sub.abnb_intraday_adj.abs().mean())), 2),
                   mean_abs_gap=round(float(sub.abnb_gap_adj.abs().mean()), 2),
                   mean_abs_intraday=round(float(sub.abnb_intraday_adj.abs().mean()), 2))
        for leg, col in [("gap", "abnb_gap_adj"), ("intraday", "abnb_intraday_adj")]:
            y = sub[col].to_numpy(float)
            pr = stats.pearsonr(x, y)
            row[f"corr_{leg}"] = round(pr.statistic, 3)
            row[f"p_{leg}"] = round(pr.pvalue, 4)
            row[f"slope_{leg}"] = round(float(np.polyfit(x, y, 1)[0]), 3)
        # naive rule: at the open, take ABNB in the sign of the peer's move; exit at the close
        pnl = np.sign(x) * sub.abnb_intraday_adj.to_numpy(float) - COST_BPS / 100
        row.update(hit_rate=round(float((pnl > 0).mean()), 2), mean_pnl_pct=round(float(pnl.mean()), 3),
                   sd_pnl_pct=round(float(pnl.std(ddof=1)), 3),
                   t_stat=round(float(pnl.mean() / (pnl.std(ddof=1) / np.sqrt(len(pnl)))), 2))
        summ.append(row)
    out["05_t1_summary"] = pd.DataFrame(summ)

    for name, df in out.items():
        df.to_csv(PROC / f"{name}.csv", index=False)
    print("M1  large prints only - does Expedia's edge survive matching on signal size?")
    print(out["05_m1_large_prints"].to_string(index=False))
    print("\n\nM2  who else moves on each reporter's day (corr / beta of the other name's AR on the reporter's)?")
    print(out["05_m2_response_matrix"].to_string(index=False))
    print("\n\nM3  ABNB's move vs the peer's REPORTED numbers, not its stock:")
    print(out["05_m3_fundamental_vs_stock"].to_string(index=False))
    print("\n\nT1  where in the day does ABNB's reaction happen?")
    print(out["05_t1_summary"].to_string(index=False))
    print("\n  event detail:")
    print(t1.sort_values(["ticker", "reaction_date"]).to_string(index=False))


if __name__ == "__main__":
    main()
