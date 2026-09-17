"""S04 base rates from the daily mean-target panel (feed convention, D_target_panel_daily.csv):
63-session log changes in the mean live target; print-centred windows (-36 to +27 sessions around each
reaction day, the shape of 16 Sep -> 15 Dec around 5 Nov); a regression of the window change on the price
change and the day-1 move; the live tape recomputed from the fresh feed pull; the known price lags.
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/sellside-mean-target-cut-by-15dec/datasets/target_base_rates.py"""
import glob, json, pathlib
import numpy as np, pandas as pd, statsmodels.api as sm
here = pathlib.Path(__file__).resolve().parent
root = here.parents[4]
p = pd.read_csv(root / "data/processed/reverse_dcf/D/D_target_panel_daily.csv", parse_dates=["date"]).dropna(subset=["mean_target"])
p = p[p.n_targets >= 10].set_index("date")
t = np.log(p.mean_target)
out = {}
d = (t.shift(-63) - t).dropna()
for lab, dd in (("all", d), ("2023+", d[d.index >= "2023-01-01"]), ("2024+", d[d.index >= "2024-01-01"])):
    out[f"63s_{lab}"] = dict(n=int(len(dd)), mean_pct=dd.mean() * 100, sd_pct=dd.std() * 100, P_le_m3_5=float((dd <= -0.035).mean()),
                            P_le_m2=float((dd <= -0.02).mean()), P_lt_0=float((dd < 0).mean()),
                            p10=dd.quantile(.1) * 100, p25=dd.quantile(.25) * 100, p50=dd.quantile(.5) * 100, p75=dd.quantile(.75) * 100)
rx = pd.read_csv(root / "data/processed/abnb_earnings_reactions.csv", parse_dates=["reaction_date"])
rows = []
for _, r in rx.iterrows():
    rd = r.reaction_date
    if rd not in p.index:
        continue
    i = p.index.get_loc(rd)
    if i - 36 < 0 or i + 27 >= len(p):
        continue
    a, b = p.mean_target.iloc[i - 36], p.mean_target.iloc[i + 27]
    pa, pb = p.close.iloc[i - 36], p.close.iloc[i + 27]
    rows.append(dict(q=r.quarter, start=p.index[i - 36].date(), end=p.index[i + 27].date(), d_target_pct=(b / a - 1) * 100,
                     d_price_pct=(pb / pa - 1) * 100, day1=r.abnb_1d_pct))
w = pd.DataFrame(rows)
w.to_csv(here / "target_change_print_windows.csv", index=False)
out["print_windows"] = dict(n=int(len(w)), share_le_m3_5=float((w.d_target_pct <= -3.5).mean()),
                            share_le_m3_5_2023plus=float((w[w.q >= "2023Q1"].d_target_pct <= -3.5).mean()), n_2023plus=int((w.q >= "2023Q1").sum()),
                            corr_price=float(w.d_target_pct.corr(w.d_price_pct)), corr_day1=float(w.d_target_pct.corr(w.day1)))
m = sm.OLS(w.d_target_pct, sm.add_constant(w[["d_price_pct", "day1"]])).fit()
out["regression_price_day1"] = dict(params=m.params.round(4).to_dict(), r2=float(m.rsquared), resid_sd=float(np.sqrt(m.mse_resid)))
d21 = (t.shift(-21) - t).dropna()
out["dlogT_21s_sd_pct"] = dict(all=d21.std() * 100, from_2023=d21[d21.index >= "2023-01-01"].std() * 100)
# live tape from the fresh feed pull (D convention: latest action per firm within 365 days, target > 0)
f = sorted(glob.glob(str(here / "sources" / "yfinance_upgrades_downgrades_*.csv")) + glob.glob(str(here.parent / "sources" / "yfinance_upgrades_downgrades_*.csv")))[-1]
ud = pd.read_csv(f, parse_dates=["GradeDate"])
asof = pd.Timestamp("2026-09-16")
u = ud[(ud.GradeDate >= asof - pd.Timedelta(days=365)) & (ud.GradeDate <= asof + pd.Timedelta(days=1)) & (ud.currentPriceTarget > 0)]
live = u.sort_values("GradeDate").groupby("Firm").tail(1)
ms_adj = live.currentPriceTarget.where(live.Firm != "Morgan Stanley", 170.0)
out["live_tape_16sep"] = dict(n=int(len(live)), mean=float(live.currentPriceTarget.mean()), median=float(live.currentPriceTarget.median()),
                              mean_with_MS_170=float(ms_adj.mean()), feed_rows=int(len(ud)), oldest_live_action=str(live.GradeDate.min().date()))
s = pd.read_csv(here.parent.parent / "close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv", parse_dates=["Date"]).set_index("Date")["Close"]
i = len(s) - 1
out["known_price_lags_log_pct"] = dict(p0_17aug_16sep=float(np.log(s.iloc[i] / s.iloc[i - 21]) * 100), pm1_17jul_17aug=float(np.log(s.iloc[i - 21] / s.iloc[i - 42]) * 100),
                                       pm2=float(np.log(s.iloc[i - 42] / s.iloc[i - 63]) * 100))
json.dump(out, open(here / "target_base_rates.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
