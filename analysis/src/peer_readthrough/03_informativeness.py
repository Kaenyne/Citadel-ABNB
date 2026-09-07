"""
03_informativeness.py - the follow-ups to 02: is the peer readthrough into ABNB actually informative?

02 established that ABNB's idiosyncratic move is ~35% larger than normal on a BKNG/EXPE print day and
~65% larger when the OTA's own print move is big, while hotel prints do nothing. Three questions left:

  1  BKNG vs EXPE. Pooled, ABNB's abnormal return correlates 0.54 with the OTA's. Split by name, EXPE is
     0.81 and BKNG is 0.01. With 14-18 events each that could be one or two days. Jackknife each
     correlation (drop one event at a time) and report the range, plus a bootstrap CI, before believing it.
  2  Does the move stick? For every ABNB print, sum ABNB's abnormal return over the peer prints in the 30
     calendar days before it ("the readthrough drift") and compare it to ABNB's own day-1 abnormal return
     and to its revenue beat vs the guide midpoint. Same sign = the readthrough was pointing the right way;
     opposite sign = ABNB's own print reverses what the peers implied.
  3  Hotels. 02 found the mean ABNB abnormal return is -0.98% (p=0.008) on days a hotel's own print move
     exceeds 5%, with no rise in |AR|. Check whether that is just an asymmetric sample of hotel prints.

Inputs
  data/processed/peer_readthrough/02_event_days.csv        (02_event_study.py)
  data/raw/peers/earnings_8k_dates.csv, data/raw/prices/peer_event_closes.csv
  data/processed/abnb_revenue_guidance_vs_actual.csv       ABNB revenue actual vs guide midpoint

Outputs (data/processed/peer_readthrough/)
  03_bkng_vs_expe.csv      per-event contributions and jackknife/bootstrap for question 1
  03_drift_vs_print.csv    one row per ABNB print for question 2
  03_hotel_asymmetry.csv   question 3
  03_ota_event_log.csv     every BKNG/EXPE print day with ABNB's move, newest first - the readable log

Run: py -3.13 analysis/src/peer_readthrough/03_informativeness.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "peer_readthrough"
N_BOOT, SEED = 5000, 0


def load():
    ed = pd.read_csv(OUT / "02_event_days.csv", parse_dates=["reaction_date"])
    ev = pd.read_csv(ROOT / "data/raw/peers/earnings_8k_dates.csv", parse_dates=["filing_date"])
    px = pd.read_csv(ROOT / "data/raw/prices/peer_event_closes.csv", parse_dates=["date"]).set_index("date")
    return ed, ev, px


def q1_bkng_vs_expe(ed):
    rows, sums = [], []
    rng = np.random.default_rng(SEED)
    for tk in ["BKNG", "EXPE"]:
        s = ed[(ed.ticker == tk) & (~ed.abnb_print_same_day)].copy()
        x, y = s.ar_peer.to_numpy(float), s.ar_abnb.to_numpy(float)
        n = len(x)
        r_full = float(np.corrcoef(x, y)[0, 1])
        jk = np.array([np.corrcoef(np.delete(x, i), np.delete(y, i))[0, 1] for i in range(n)])
        idx = rng.integers(0, n, (N_BOOT, n))
        boot = np.array([np.corrcoef(x[k], y[k])[0, 1] for k in idx])
        boot = boot[np.isfinite(boot)]
        sums.append(dict(ticker=tk, n=n, corr=round(r_full, 3),
                         jackknife_min=round(jk.min(), 3), jackknife_max=round(jk.max(), 3),
                         boot_ci_lo=round(float(np.percentile(boot, 2.5)), 3),
                         boot_ci_hi=round(float(np.percentile(boot, 97.5)), 3),
                         spearman=round(float(stats.spearmanr(x, y).statistic), 3),
                         sign_concord=round(float(np.mean(np.sign(x) == np.sign(y))), 2),
                         mean_abs_ar_peer=round(float(np.abs(x).mean()), 2),
                         mean_abs_ar_abnb=round(float(np.abs(y).mean()), 2)))
        s["drops_corr_to"] = jk.round(3)
        rows.append(s[["reaction_date", "ticker", "ar_peer", "ar_abnb", "drops_corr_to"]])
    detail = pd.concat(rows).sort_values(["ticker", "reaction_date"])
    return pd.DataFrame(sums), detail


def q2_drift(ed, ev):
    abnb = ev[ev.ticker == "ABNB"].copy()
    abnb["hour_et"] = abnb["acceptance_et"].str[11:13].astype(int)
    px = pd.read_csv(ROOT / "data/raw/prices/peer_event_closes.csv", parse_dates=["date"]).set_index("date")
    sessions = px.index
    ar_abnb_by_date = ed.drop_duplicates("reaction_date").set_index("reaction_date")["ar_abnb"]

    # ABNB's own reaction day and abnormal return, recomputed the same way as 02
    ret = px.pct_change() * 100
    mkt = ret["QQQ"]
    r = ret["ABNB"]
    ar = pd.Series(index=ret.index, dtype=float)
    for i in range(len(ret.index)):
        lo, hi = i - 256, i - 6
        if lo < 0:
            continue
        y, x = r.iloc[lo:hi], mkt.iloc[lo:hi]
        ok = y.notna() & x.notna()
        if ok.sum() < 120 or not np.isfinite(r.iloc[i]) or not np.isfinite(mkt.iloc[i]):
            continue
        b, a = np.polyfit(x[ok], y[ok], 1)
        ar.iloc[i] = r.iloc[i] - (a + b * mkt.iloc[i])

    guide = pd.read_csv(ROOT / "data/processed/abnb_revenue_guidance_vs_actual.csv", dtype={"guided_quarter": str})
    guide = guide.rename(columns={"guided_quarter": "quarter", "actual_vs_mid_pct": "rev_beat_pct"})

    rows = []
    clean = ed[~ed.abnb_print_same_day]
    for _, a in abnb.iterrows():
        d, h = a["filing_date"], a["hour_et"]
        cand = sessions[sessions >= d]
        if len(cand) == 0:
            continue
        rd = d if (cand[0] == d and h < 16) else (sessions[sessions > d][0] if len(sessions[sessions > d]) else None)
        if rd is None or not np.isfinite(ar.get(rd, np.nan)):
            continue
        win = clean[(clean.reaction_date < rd) & (clean.reaction_date >= rd - pd.Timedelta(days=30))]
        ota = win[win.ticker.isin(["BKNG", "EXPE"])]
        rows.append(dict(abnb_reaction_date=rd.date(), abnb_ar=round(float(ar[rd]), 2),
                         n_peer_prints_30d=len(win), n_ota_prints_30d=len(ota),
                         drift_all_peers=round(float(win.ar_abnb.sum()), 2),
                         drift_ota=round(float(ota.ar_abnb.sum()), 2),
                         drift_hotels=round(float(win[win.group == "Hotel"].ar_abnb.sum()), 2),
                         ota_peers=" ".join(f"{t}{v:+.1f}" for t, v in zip(ota.ticker, ota.ar_abnb))))
    df = pd.DataFrame(rows)
    df["quarter"] = pd.PeriodIndex(pd.to_datetime(df.abnb_reaction_date) - pd.Timedelta(days=45), freq="Q").astype(str)
    df = df.merge(guide[["quarter", "rev_beat_pct"]], on="quarter", how="left")

    tests = []
    for sig in ["drift_ota", "drift_all_peers", "drift_hotels"]:
        for tgt in ["abnb_ar", "rev_beat_pct"]:
            s = df[[sig, tgt]].dropna()
            s = s[s[sig] != 0]
            if len(s) < 6:
                continue
            x, y = s[sig].to_numpy(float), s[tgt].to_numpy(float)
            pr = stats.pearsonr(x, y)
            tests.append(dict(signal=sig, target=tgt, n=len(s), pearson_r=round(pr.statistic, 3),
                              p=round(pr.pvalue, 4),
                              spearman=round(float(stats.spearmanr(x, y).statistic), 3),
                              sign_concord=round(float(np.mean(np.sign(x) == np.sign(y))), 2)))
    return df, pd.DataFrame(tests)


def q3_hotels(ed):
    h = ed[(ed.group == "Hotel") & (~ed.abnb_print_same_day)].copy()
    big = h[h.ar_peer.abs() > 5]
    rows = [dict(cut="all hotel prints", n=len(h), mean_ar_peer=round(h.ar_peer.mean(), 2),
                 share_peer_neg=round(float((h.ar_peer < 0).mean()), 2), mean_ar_abnb=round(h.ar_abnb.mean(), 2)),
            dict(cut="hotel |AR|>5%", n=len(big), mean_ar_peer=round(big.ar_peer.mean(), 2),
                 share_peer_neg=round(float((big.ar_peer < 0).mean()), 2), mean_ar_abnb=round(big.ar_abnb.mean(), 2)),
            dict(cut="hotel AR < -5%", n=int((h.ar_peer < -5).sum()),
                 mean_ar_peer=round(h.loc[h.ar_peer < -5, "ar_peer"].mean(), 2), share_peer_neg=1.0,
                 mean_ar_abnb=round(h.loc[h.ar_peer < -5, "ar_abnb"].mean(), 2)),
            dict(cut="hotel AR > +5%", n=int((h.ar_peer > 5).sum()),
                 mean_ar_peer=round(h.loc[h.ar_peer > 5, "ar_peer"].mean(), 2), share_peer_neg=0.0,
                 mean_ar_abnb=round(h.loc[h.ar_peer > 5, "ar_abnb"].mean(), 2))]
    return pd.DataFrame(rows), big.sort_values("reaction_date")[["reaction_date", "ticker", "ar_peer", "ar_abnb"]]


def main():
    ed, ev, px = load()
    pd.set_option("display.width", 240)
    pd.set_option("display.max_rows", 200)

    s1, d1 = q1_bkng_vs_expe(ed)
    s1.to_csv(OUT / "03_bkng_vs_expe.csv", index=False)
    d1.to_csv(OUT / "03_bkng_vs_expe_events.csv", index=False)
    print("Q1  Is EXPE really the better readthrough than BKNG?")
    print(s1.to_string(index=False))
    print("\n  per-event detail (drops_corr_to = correlation if that day is removed):")
    print(d1.to_string(index=False))

    df2, t2 = q2_drift(ed, ev)
    df2.to_csv(OUT / "03_drift_vs_print.csv", index=False)
    t2.to_csv(OUT / "03_drift_tests.csv", index=False)
    print("\n\nQ2  Does the pre-print readthrough drift point the right way?")
    print(df2[["abnb_reaction_date", "quarter", "n_ota_prints_30d", "ota_peers", "drift_ota", "drift_all_peers",
               "abnb_ar", "rev_beat_pct"]].to_string(index=False))
    print("\n  tests:")
    print(t2.to_string(index=False))

    s3, big3 = q3_hotels(ed)
    s3.to_csv(OUT / "03_hotel_asymmetry.csv", index=False)
    print("\n\nQ3  The hotel result:")
    print(s3.to_string(index=False))
    print("\n  the 20 large hotel prints:")
    print(big3.to_string(index=False))

    log = ed[ed.ticker.isin(["BKNG", "EXPE"])].sort_values("reaction_date", ascending=False)
    log.to_csv(OUT / "03_ota_event_log.csv", index=False)
    print("\n\nEvery BKNG/EXPE print day and what ABNB did (newest first):")
    print(log[["reaction_date", "ticker", "ar_peer", "ar_abnb", "ret_abnb", "ret_qqq", "abnb_print_same_day"]].to_string(index=False))


if __name__ == "__main__":
    main()
