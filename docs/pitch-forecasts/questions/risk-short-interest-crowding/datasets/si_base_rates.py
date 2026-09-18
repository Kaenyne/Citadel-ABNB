"""R13 base rates: distribution of the maximum short interest (% of shares outstanding) over an 8-settlement window,
from the MarketBeat/Nasdaq series (84 settlements Feb 2023 - Aug 2026), unconditional and conditioned on the
starting level; the changes distribution; what a 5.0% reading needs.
Run: py -3.13 docs/pitch-forecasts/questions/risk-short-interest-crowding/datasets/si_base_rates.py
"""
import json, pathlib, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[5]; HERE = pathlib.Path(__file__).resolve().parent
s = pd.read_csv(ROOT/"data/processed/overnight/09_positioning_short_interest.csv")
s["settlement_date"] = pd.to_datetime(s["settlement_date"]); s = s.sort_values("settlement_date").reset_index(drop=True)
x = s["si_pct_shares"].values; n = len(x)
out = {"n_settlements": n, "first": s.settlement_date.min().date().isoformat(), "last": s.settlement_date.max().date().isoformat(),
       "latest_pct": float(x[-1]), "mean": float(x.mean()), "median": float(np.median(x)), "max": float(x.max()), "min": float(x.min()),
       "pctile_of_latest": float((x < x[-1]).mean()), "n_readings_ge_5": int((x>=5).sum()), "readings_ge_4.5": s[s.si_pct_shares>=4.5][["settlement_date","si_pct_shares"]].astype(str).values.tolist()}
# 8-settlement windows (30 Sep -> 15 Jan = 8 settlements: 9/30, 10/15, 10/31, 11/15, 11/30, 12/15, 12/31, 1/15)
W = 8
rows = []
for i in range(0, n - W + 1):
    w = x[i:i+W]; start = x[i-1] if i>0 else np.nan
    rows.append({"start_date": s.settlement_date[i].date().isoformat(), "start_level_prev": start, "first": w[0], "max": w.max(), "rise_from_prev": w.max()-start if i>0 else np.nan})
wdf = pd.DataFrame(rows); wdf.to_csv(HERE/"si_window_max.csv", index=False)
out["windows"] = {"n": int(len(wdf)), "P(max>=5.0)": float((wdf["max"]>=5.0).mean()), "P(max>=4.5)": float((wdf["max"]>=4.5).mean()), "P(max>=4.0)": float((wdf["max"]>=4.0).mean()),
                  "P(max>=3.5)": float((wdf["max"]>=3.5).mean()), "P(max>=3.0)": float((wdf["max"]>=3.0).mean()),
                  "n_windows_ge_5": int((wdf["max"]>=5.0).sum()), "windows_ge_5_dates": wdf[wdf["max"]>=5.0].start_date.tolist(),
                  "max_rise_from_prev": float(wdf.rise_from_prev.max()), "p90_rise": float(wdf.rise_from_prev.quantile(0.9)), "p95_rise": float(wdf.rise_from_prev.quantile(0.95)),
                  "P(rise>=2.83)": float((wdf.rise_from_prev>=2.83).mean())}
# conditional on starting level below 2.5 / below median
lo = wdf[wdf.start_level_prev<2.5]; med = wdf[wdf.start_level_prev<np.median(x)]
out["windows_start_below_2.5"] = {"n": int(len(lo)), "P(max>=5)": float((lo["max"]>=5).mean()), "P(max>=4)": float((lo["max"]>=4).mean()), "P(max>=3.5)": float((lo["max"]>=3.5).mean()), "max_of_max": float(lo["max"].max()), "mean_max": float(lo["max"].mean())}
out["windows_start_below_median"] = {"n": int(len(med)), "P(max>=5)": float((med["max"]>=5).mean()), "P(max>=4)": float((med["max"]>=4).mean()), "max_of_max": float(med["max"].max())}
# per-settlement change distribution and 4-settlement / 8-settlement changes
ch = np.diff(x)
out["changes"] = {"sd_1": float(ch.std(ddof=1)), "max_1": float(ch.max()), "p95_1": float(np.quantile(ch,0.95)), "P(ch>=1.0)": float((ch>=1.0).mean()),
                  "sd_4": float(np.std(x[4:]-x[:-4], ddof=1)), "max_4": float((x[4:]-x[:-4]).max()), "sd_8": float(np.std(x[8:]-x[:-8], ddof=1)), "max_8": float((x[8:]-x[:-8]).max()),
                  "ar1": float(np.corrcoef(x[1:], x[:-1])[0,1])}
# the Sep 2023 episode
ep = s[(s.settlement_date>="2023-08-01")&(s.settlement_date<="2023-12-31")][["settlement_date","short_interest_shares","si_pct_shares"]]
out["sep2023_episode"] = ep.astype(str).values.tolist()
# what 5.0% needs now: shares out 592m (latest file) -> 29.6m shares short; latest 12.86m -> +16.7m (x2.3)
so = float(s.shares_out_m.iloc[-1]); out["needs"] = {"shares_out_m_latest_file": so, "shares_short_for_5pct_m": 0.05*so, "latest_short_m": float(s.short_interest_shares.iloc[-1]/1e6), "multiple_needed": 0.05*so/(s.short_interest_shares.iloc[-1]/1e6)}
# simple AR(1) in levels fitted on the series, simulate 8 steps from the latest reading (bootstrap residuals) -> P(max>=5)
a = np.polyfit(x[:-1], x[1:], 1); resid = x[1:] - (a[0]*x[:-1]+a[1]); rng = np.random.default_rng(20260917)
sims = []
for _ in range(200000):
    v = x[-1]; m = 0
    # allow for the 31 Aug and 15 Sep settlements before 30 Sep: 2 unobserved steps then 8 in-window
    for k in range(10):
        v = a[0]*v + a[1] + rng.choice(resid); 
        if k>=2: m = max(m, v)
    sims.append(m)
sims = np.array(sims)
out["ar1_sim"] = {"slope": float(a[0]), "intercept": float(a[1]), "long_run_mean": float(a[1]/(1-a[0])), "resid_sd": float(resid.std(ddof=1)), "P(max>=5)": float((sims>=5).mean()), "P(max>=4)": float((sims>=4).mean()), "P(max>=3.5)": float((sims>=3.5).mean()), "p50_max": float(np.median(sims)), "p90_max": float(np.quantile(sims,0.9)), "p99_max": float(np.quantile(sims,0.99))}
json.dump(out, open(HERE/"si_base_rates.json","w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
