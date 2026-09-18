"""B11 base rates: rating downgrades to Hold/Sell-equivalent per 90-day window in the yfinance/Benzinga feed
(fresh pull 2026-09-17T08:21Z in ../sources, 469 rows, identical to S04's 16 Sep pull), clustering around prints and
around price falls, and the 17 Sep -> 15 Dec window analogues. Mirrors R12's upgrade_base_rates.py.
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/bonus-sellside-downgrades/datasets/downgrade_base_rates.py
"""
import json, pathlib, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[5]
HERE = pathlib.Path(__file__).resolve().parent
feed = HERE.parent / "sources/yfinance_upgrades_downgrades_20260917T082155Z.csv"
df = pd.read_csv(feed); df.columns = [c.strip() for c in df.columns]
dcol = [c for c in df.columns if "date" in c.lower()][0]
df["date"] = pd.to_datetime(df[dcol]).dt.tz_localize(None).dt.normalize()
BUY = {"buy","outperform","overweight","positive","strong buy","market outperform","sector outperform","top pick","conviction buy","accumulate","add"}
HOLD = {"neutral","hold","equal-weight","equal weight","market perform","sector perform","sector weight","in-line","perform","peer perform","mixed"}
SELL = {"sell","underweight","underperform","reduce","strong sell","negative"}
def bucket(g):
    g = str(g).strip().lower()
    return "Buy" if g in BUY else "Hold" if g in HOLD else "Sell" if g in SELL else "Other"
df["to_b"] = df["ToGrade"].map(bucket); df["from_b"] = df["FromGrade"].map(bucket)
downs = df[df["Action"].str.lower()=="down"].copy().sort_values("date")
downs["to_hold_or_sell"] = downs["to_b"].isin(["Hold","Sell"])
downs[["date","Firm","FromGrade","ToGrade","from_b","to_b","to_hold_or_sell","currentPriceTarget","priorPriceTarget"]].to_csv(HERE/"feed_downgrades_all.csv", index=False)
d = downs[downs.to_hold_or_sell]["date"]
rx = pd.read_csv(ROOT/"data/processed/abnb_earnings_reactions.csv"); rx["reaction_date"]=pd.to_datetime(rx["reaction_date"])
prints = rx["reaction_date"].tolist()
px = pd.read_csv(ROOT/"docs/pitch-forecasts/questions/close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv")
px["date"] = pd.to_datetime(px[px.columns[0]]); px = px.set_index("date")[px.columns[1]].astype(float)
res = {}
for start in ["2021-01-01","2023-01-01","2024-01-01"]:
    s = pd.Timestamp(start); e = pd.Timestamp("2026-09-16")
    days = pd.date_range(s, e - pd.Timedelta(days=89), freq="D")
    counts = np.array([((d>=t)&(d<t+pd.Timedelta(days=90))).sum() for t in days])
    res[start] = {"n_windows": int(len(days)), "mean": float(counts.mean()), "P(>=3)": float((counts>=3).mean()), "P(>=2)": float((counts>=2).mean()),
                  "P(>=1)": float((counts>=1).mean()), "max": int(counts.max()), "n_events": int(((d>=s)&(d<=e)).sum()),
                  "events_per_year": float(((d>=s)&(d<=e)).sum()/((e-s).days/365.25))}
# 90-day windows conditioned on the trailing 21-session price move at the window start (downgrades follow falls?)
rows = []
s = pd.Timestamp("2021-01-01"); e = pd.Timestamp("2026-09-16")
for t in pd.date_range(s, e - pd.Timedelta(days=89), freq="D"):
    p = px[:t]
    if len(p) < 22: continue
    r21 = p.iloc[-1]/p.iloc[-22]-1
    r90f = px[t:t+pd.Timedelta(days=90)]
    rows.append({"start": t, "r21_prior": r21, "r90_window": (r90f.iloc[-1]/r90f.iloc[0]-1) if len(r90f)>1 else np.nan,
                 "n": int(((d>=t)&(d<t+pd.Timedelta(days=90))).sum())})
w = pd.DataFrame(rows)
res["cond_on_window_price_move"] = {lab: {"n_windows": int(len(sub)), "mean": float(sub.n.mean()), "P(>=3)": float((sub.n>=3).mean())}
    for lab, sub in [("window return <= -15%", w[w.r90_window<=-0.15]), ("window return -15..0", w[(w.r90_window>-0.15)&(w.r90_window<=0)]),
                     ("window return > 0", w[w.r90_window>0]), ("window return <= -10% (2023+)", w[(w.r90_window<=-0.10)&(w.start>="2023")]),
                     ("window return > 0 (2023+)", w[(w.r90_window>0)&(w.start>="2023")])]}
res["cond_on_prior_21s_move"] = {lab: {"n_windows": int(len(sub)), "mean": float(sub.n.mean()), "P(>=3)": float((sub.n>=3).mean())}
    for lab, sub in [("prior 21s <= -10%", w[w.r21_prior<=-0.10]), ("prior 21s -10..0", w[(w.r21_prior>-0.10)&(w.r21_prior<=0)]), ("prior 21s > 0", w[w.r21_prior>0])]}
# print-shaped windows (-49 / +39 calendar days around each reaction day = 17 Sep -> 15 Dec shape)
pw = []
for p in prints:
    a = p - pd.Timedelta(days=49); b = p + pd.Timedelta(days=39)
    n = int(((d>=a)&(d<=b)).sum()); pre = int(((d>=a)&(d<p)).sum()); post = int(((d>=p)&(d<=b)).sum())
    pp = px[p:p+pd.Timedelta(days=39)]; move20 = float(pp.iloc[-1]/px[:p].iloc[-2]-1) if len(pp)>1 else np.nan
    pw.append({"print": p.date().isoformat(), "n": n, "pre": pre, "post": post, "day1_raw": float(rx.loc[rx.reaction_date==p,"abnb_1d_pct"].iloc[0]), "post39d_move": move20})
pwdf = pd.DataFrame(pw); res["print_windows"] = pwdf.to_dict("records")
res["print_windows_P(>=3)_all"] = float((pwdf.n>=3).mean()); res["print_windows_P(>=3)_2023plus"] = float((pwdf[pwdf["print"]>="2023"].n>=3).mean())
res["print_windows_mean_all"] = float(pwdf.n.mean()); res["print_windows_mean_2023plus"] = float(pwdf[pwdf["print"]>="2023"].n.mean())
res["print_windows_n_by_day1_sign"] = {"up>=5": float(pwdf[pwdf.day1_raw>=5].n.mean()), "down<=-5": float(pwdf[pwdf.day1_raw<=-5].n.mean()), "small": float(pwdf[(pwdf.day1_raw>-5)&(pwdf.day1_raw<5)].n.mean())}
res["print_windows_post_by_day1_sign"] = {"up>=5": float(pwdf[pwdf.day1_raw>=5].post.mean()), "down<=-5": float(pwdf[pwdf.day1_raw<=-5].post.mean()), "small": float(pwdf[(pwdf.day1_raw>-5)&(pwdf.day1_raw<5)].post.mean())}
res["print_windows_P(>=3)_by_day1_sign"] = {"up>=5": float((pwdf[pwdf.day1_raw>=5].n>=3).mean()), "down<=-5": float((pwdf[pwdf.day1_raw<=-5].n>=3).mean()), "small": float((pwdf[(pwdf.day1_raw>-5)&(pwdf.day1_raw<5)].n>=3).mean())}
res["print_windows_post_by_post39d_move"] = {"post move <= -8%": float(pwdf[pwdf.post39d_move<=-0.08].post.mean()), "-8..0": float(pwdf[(pwdf.post39d_move>-0.08)&(pwdf.post39d_move<=0)].post.mean()), "> 0": float(pwdf[pwdf.post39d_move>0].post.mean()),
                                              "n": {"<=-8": int((pwdf.post39d_move<=-0.08).sum()), "-8..0": int(((pwdf.post39d_move>-0.08)&(pwdf.post39d_move<=0)).sum()), ">0": int((pwdf.post39d_move>0).sum())}}
res["same_calendar_17sep_15dec"] = {y: int(((d>=pd.Timestamp(f"{y}-09-17"))&(d<=pd.Timestamp(f"{y}-12-15"))).sum()) for y in range(2021, 2026)}
dist = [min(((x - p).days for p in prints), key=abs) for x in d]
res["share_within_5d_of_print"] = float(np.mean([abs(z)<=5 for z in dist])); res["share_within_10d_of_print"] = float(np.mean([abs(z)<=10 for z in dist])); res["share_within_30d_after_print"] = float(np.mean([0<=z<=30 for z in dist]))
res["days_since_last_downgrade_on_2026-09-16"] = int((pd.Timestamp("2026-09-16")-d.max()).days)
res["n_downgrades_to_hold_sell"] = int(len(d)); res["n_down_rows_all"] = int(len(downs)); res["feed_rows"] = int(len(df))
live = df[df.date>=pd.Timestamp("2025-09-17")].sort_values("date").groupby("Firm").tail(1)
res["pool_live_365d"] = {"n_firms": int(len(live)), "buy": int((live.to_b=="Buy").sum()), "hold": int((live.to_b=="Hold").sum()), "sell": int((live.to_b=="Sell").sum()), "other": int((live.to_b=="Other").sum())}
json.dump(res, open(HERE/"downgrade_base_rates.json","w"), indent=1, default=str)
print(json.dumps({k:v for k,v in res.items() if k!="print_windows"}, indent=1, default=str)); print(pwdf.to_string())
