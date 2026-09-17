"""R12 base rates: rating upgrades to Buy-equivalent per 90-day window in the yfinance/Benzinga feed
(S04's 16 Sep 2026 pull, 469 rows), clustering around prints, and the 17 Sep -> 15 Dec window analogues.
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/risk-sellside-upgrades/datasets/upgrade_base_rates.py
"""
import json, pathlib, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[5]
HERE = pathlib.Path(__file__).resolve().parent
feed = ROOT / "docs/pitch-forecasts/questions/sellside-mean-target-cut-by-15dec/sources/yfinance_upgrades_downgrades_20260917T031221Z.csv"
df = pd.read_csv(feed)
df.columns = [c.strip() for c in df.columns]
dcol = [c for c in df.columns if "Date" in c or "date" in c][0]
df["date"] = pd.to_datetime(df[dcol]).dt.tz_localize(None).dt.normalize()
BUY = {"buy","outperform","overweight","positive","strong buy","market outperform","sector outperform","top pick","conviction buy","accumulate","add"}
HOLD = {"neutral","hold","equal-weight","equal weight","market perform","sector perform","sector weight","in-line","perform","peer perform","mixed"}
def bucket(g):
    g = str(g).strip().lower()
    if g in BUY: return "Buy"
    if g in HOLD: return "Hold"
    if g in {"sell","underweight","underperform","reduce","strong sell","negative"}: return "Sell"
    return "Other"
df["to_b"] = df["ToGrade"].map(bucket); df["from_b"] = df["FromGrade"].map(bucket)
ups = df[(df["Action"].str.lower()=="up")].copy()
ups["to_buy"] = ups["to_b"]=="Buy"
ups = ups.sort_values("date")
ups[["date","Firm","FromGrade","ToGrade","from_b","to_b","to_buy","Action","priceTargetAction","currentPriceTarget","priorPriceTarget"]].to_csv(HERE/"feed_upgrades_all.csv", index=False)
downs = df[df["Action"].str.lower()=="down"].sort_values("date")
# print dates (reaction sessions)
rx = pd.read_csv(ROOT/"data/processed/abnb_earnings_reactions.csv"); rx["reaction_date"]=pd.to_datetime(rx["reaction_date"])
prints = rx["reaction_date"].tolist()
out = {}
for label, sub in [("all_upgrades", ups), ("upgrades_to_buy", ups[ups.to_buy])]:
    d = sub["date"]
    res = {}
    for start in ["2021-01-01","2023-01-01","2024-01-01"]:
        s = pd.Timestamp(start); e = pd.Timestamp("2026-09-16")
        days = pd.date_range(s, e - pd.Timedelta(days=89), freq="D")
        counts = np.array([((d>=t)&(d<t+pd.Timedelta(days=90))).sum() for t in days])
        res[start] = {"n_windows": int(len(days)), "mean": float(counts.mean()), "P(>=3)": float((counts>=3).mean()),
                      "P(>=2)": float((counts>=2).mean()), "P(>=1)": float((counts>=1).mean()), "max": int(counts.max()),
                      "n_events": int(((d>=s)&(d<=e)).sum()), "events_per_year": float(((d>=s)&(d<=e)).sum()/((e-s).days/365.25))}
    # windows shaped like 17 Sep -> 15 Dec around each print: reaction day -35 sessions ~ -49 cal days, +27 sessions ~ +39 cal days
    pw = []
    for p in prints:
        a = p - pd.Timedelta(days=49); b = p + pd.Timedelta(days=39)
        n = int(((d>=a)&(d<=b)).sum()); pre = int(((d>=a)&(d<p)).sum()); post = int(((d>=p)&(d<=b)).sum())
        pw.append({"print": p.date().isoformat(), "n": n, "pre": pre, "post": post, "day1_raw": float(rx.loc[rx.reaction_date==p,"abnb_1d_pct"].iloc[0])})
    pwdf = pd.DataFrame(pw)
    res["print_windows"] = pwdf.to_dict("records")
    res["print_windows_P(>=3)_all"] = float((pwdf.n>=3).mean()); res["print_windows_P(>=3)_2023plus"] = float((pwdf[pwdf["print"]>="2023"].n>=3).mean())
    res["print_windows_n_by_day1_sign"] = {"up>=5": float(pwdf[pwdf.day1_raw>=5].n.mean()), "down<=-5": float(pwdf[pwdf.day1_raw<=-5].n.mean()), "small": float(pwdf[(pwdf.day1_raw>-5)&(pwdf.day1_raw<5)].n.mean())}
    res["print_windows_P(>=3)_by_day1_sign"] = {"up>=5": float((pwdf[pwdf.day1_raw>=5].n>=3).mean()), "down<=-5": float((pwdf[pwdf.day1_raw<=-5].n>=3).mean()), "small": float((pwdf[(pwdf.day1_raw>-5)&(pwdf.day1_raw<5)].n>=3).mean())}
    # same calendar windows 17 Sep - 15 Dec
    cal = {}
    for y in range(2021, 2026):
        a = pd.Timestamp(f"{y}-09-17"); b = pd.Timestamp(f"{y}-12-15")
        cal[y] = int(((d>=a)&(d<=b)).sum())
    res["same_calendar_17sep_15dec"] = cal
    # distance of each upgrade to the nearest print (calendar days, signed: + after)
    if len(d):
        dist = [min(((x - p).days for p in prints), key=abs) for x in d]
        res["share_within_5d_of_print"] = float(np.mean([abs(z)<=5 for z in dist])); res["share_within_10d_of_print"] = float(np.mean([abs(z)<=10 for z in dist]))
    out[label] = res
out["downgrades_n_2023plus"] = int((downs.date>="2023-01-01").sum())
out["feed_rows"] = int(len(df))
json.dump(out, open(HERE/"upgrade_base_rates.json","w"), indent=1, default=str)
print(json.dumps({k:(v if not isinstance(v,dict) else {kk:vv for kk,vv in v.items() if kk!="print_windows"}) for k,v in out.items()}, indent=1, default=str))
print(pd.DataFrame(out["upgrades_to_buy"]["print_windows"]))
