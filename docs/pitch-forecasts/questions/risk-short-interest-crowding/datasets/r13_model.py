"""R13: P(ABNB short interest >= 5.0% of shares outstanding at any Nasdaq settlement 30 Sep 2026 - 15 Jan 2027; 8 settlements:
30 Sep, 15 Oct, 30 Oct, 13 Nov, 30 Nov, 15 Dec, 31 Dec, 15 Jan).
Inputs: the repo series (84 settlements Feb 2023 - Aug 2026, % of basic shares outstanding), extended back to Sep 2021 from
MarketBeat's embedded dollar series (si_history_2022_2026.csv, built by marketbeat_history.py), plus the 31 Aug 2026 Nasdaq
reading pulled 17 Sep (sources/nasdaq_short_interest_20260917T035213Z.json: 14,228,547 shares).
Models: (1) empirical 8-settlement window maxima, unconditional and conditional on the starting level; (2) AR(1) in levels with
bootstrapped residuals, simulated from the latest reading with one unobserved step (15 Sep) before the window; (3) the same with
a jump component calibrated to the two observed one-step rises >= 0.9pt (15 Sep 2023 +0.94, 30 Sep 2023 +1.40, both the S&P 500
inclusion episode); (4) a down-print overlay (+0.7pt over two settlements after 5 Nov with P 0.41 = S01 P(day-1 <= -5%)).
Seed 20260917. Run: py -3.13 docs/pitch-forecasts/questions/risk-short-interest-crowding/datasets/r13_model.py
"""
import json, pathlib, csv, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[4]
rng = np.random.default_rng(20260917)
h = pd.read_csv(HERE / "si_history_2022_2026.csv"); h["date"] = pd.to_datetime(h["date"]); h = h.sort_values("date")
SHARES_OUT_M = 592.0            # latest basic count in the repo file (09_positioning_short_interest.csv, 14 Aug 2026 row)
latest_shares = 14_228_547      # Nasdaq settlement 31 Aug 2026
latest_pct = latest_shares / (SHARES_OUT_M * 1e6) * 100
x_hist = h["si_pct_used"].values
x = np.append(x_hist, latest_pct); dates = list(h["date"].dt.date.astype(str)) + ["2026-08-31"]
n = len(x)
out = {"n_settlements": n, "first": dates[0], "last": dates[-1], "latest_pct": float(latest_pct), "latest_shares": latest_shares,
       "shares_out_m": SHARES_OUT_M, "threshold_shares_m": 0.05 * SHARES_OUT_M, "multiple_needed": 0.05 * SHARES_OUT_M * 1e6 / latest_shares,
       "series_mean": float(x.mean()), "series_median": float(np.median(x)), "series_max": float(x.max()), "series_min": float(x.min()),
       "pctile_of_latest": float((x < latest_pct).mean()), "n_readings_ge_5": int((x >= 5).sum()), "n_readings_ge_4": int((x >= 4).sum()),
       "alt_basis_float_405.8m_latest_pct": latest_shares / 405.782e6 * 100, "alt_basis_threshold_shares_m": 0.05 * 405.782,
       "alt_basis_classA_419.5m_latest_pct": latest_shares / 419.53e6 * 100}
# (1) empirical windows
W = 8
rows = []
for i in range(1, n - W + 1):
    w = x[i:i + W]; rows.append({"start_date": dates[i], "prev_level": x[i - 1], "max": w.max(), "rise": w.max() - x[i - 1]})
wdf = pd.DataFrame(rows); wdf.to_csv(HERE / "si_window_max.csv", index=False)
def wstats(d):
    return {"n": int(len(d)), "P(max>=5.0)": float((d["max"] >= 5).mean()), "P(max>=4.5)": float((d["max"] >= 4.5).mean()),
            "P(max>=4.0)": float((d["max"] >= 4).mean()), "P(max>=3.5)": float((d["max"] >= 3.5).mean()), "P(max>=3.0)": float((d["max"] >= 3).mean()),
            "max_of_max": float(d["max"].max()), "p90_rise": float(d["rise"].quantile(0.9)), "max_rise": float(d["rise"].max()),
            "P(rise>=%.2f)" % (5 - latest_pct): float((d["rise"] >= 5 - latest_pct).mean())}
out["windows_all"] = wstats(wdf); out["windows_start_below_2.5"] = wstats(wdf[wdf.prev_level < 2.5]); out["windows_start_below_3.0"] = wstats(wdf[wdf.prev_level < 3.0])
out["windows_2023plus"] = wstats(wdf[wdf.start_date >= "2023-01-01"])
out["windows_ge5_start_dates"] = wdf[wdf["max"] >= 5].start_date.tolist()
# independent episodes: local maxima of the series above 3.3
peaks = []
for i in range(1, n - 1):
    if x[i] >= 3.3 and x[i] >= x[i - 1] and x[i] >= x[i + 1]: peaks.append((dates[i], round(float(x[i]), 2)))
out["local_peaks_ge_3.3"] = peaks
# per-step change distribution
ch = np.diff(x)
out["changes"] = {"sd_1": float(ch.std(ddof=1)), "max_1": float(ch.max()), "p95_1": float(np.quantile(ch, 0.95)), "n_steps": int(len(ch)),
                  "n_rise_ge_0.9": int((ch >= 0.9).sum()), "rises_ge_0.9": [(dates[i + 1], round(float(ch[i]), 2)) for i in np.where(ch >= 0.9)[0]],
                  "sd_8": float(np.std(x[8:] - x[:-8], ddof=1)), "max_8": float((x[8:] - x[:-8]).max()), "ar1": float(np.corrcoef(x[1:], x[:-1])[0, 1])}
# (2) AR(1) with bootstrapped residuals (fit on the full series, and on 2024+ as a regime check)
def ar_sim(xfit, start, n_unobs=1, n_win=8, nsim=300_000, jump_q=0.0, jump_lo=0.9, jump_hi=1.5, overlay_p=0.0, overlay_pts=0.7, overlay_steps=(3, 4)):
    a, b = np.polyfit(xfit[:-1], xfit[1:], 1); resid = xfit[1:] - (a * xfit[:-1] + b)
    v = np.full(nsim, start); m = np.full(nsim, -np.inf)
    ov = rng.random(nsim) < overlay_p
    for k in range(n_unobs + n_win):
        v = a * v + b + rng.choice(resid, nsim)
        if jump_q > 0:
            j = rng.random(nsim) < jump_q; v = v + j * rng.uniform(jump_lo, jump_hi, nsim)
        if overlay_p > 0 and (k - n_unobs) in overlay_steps: v = v + ov * overlay_pts / len(overlay_steps)
        if k >= n_unobs: m = np.maximum(m, v)
    return {"slope": float(a), "intercept": float(b), "long_run_mean": float(b / (1 - a)), "resid_sd": float(resid.std(ddof=1)),
            "P(max>=5)": float((m >= 5).mean()), "P(max>=4.5)": float((m >= 4.5).mean()), "P(max>=4)": float((m >= 4).mean()), "P(max>=3.5)": float((m >= 3.5).mean()),
            "P(max>=3.43_float_basis_equiv)": float((m >= 3.43).mean()),
            "p50_max": float(np.median(m)), "p90_max": float(np.quantile(m, 0.9)), "p99_max": float(np.quantile(m, 0.99)), "p999_max": float(np.quantile(m, 0.999))}
out["ar1_full"] = ar_sim(x, latest_pct)
out["ar1_2024plus"] = ar_sim(x[[d >= "2024-01-01" for d in dates]], latest_pct)
out["ar1_2023plus"] = ar_sim(x[[d >= "2023-01-01" for d in dates]], latest_pct)
# (3) jump component: 2 one-step rises >= 0.9 in 98 steps -> q = 2/98 per step; size U(0.9, 1.5)
q = out["changes"]["n_rise_ge_0.9"] / out["changes"]["n_steps"]
out["ar1_full_jump"] = dict(jump_q=q, **ar_sim(x, latest_pct, jump_q=q))
out["ar1_full_jump_x2"] = dict(jump_q=2 * q, **ar_sim(x, latest_pct, jump_q=2 * q))
out["ar1_full_jump_bigger"] = dict(jump_q=q, size="U(1.5,2.5)", **ar_sim(x, latest_pct, jump_q=q, jump_lo=1.5, jump_hi=2.5))
# (4) down-print overlay: P 0.41 of a +0.7pt rise over the two settlements after 5 Nov (13 Nov, 30 Nov = steps 3-4 of the window)
out["ar1_full_jump_downprint"] = dict(jump_q=q, overlay="P 0.41, +0.7pt over 13 Nov & 30 Nov", **ar_sim(x, latest_pct, jump_q=q, overlay_p=0.41))
out["ar1_full_jump_downprint_big"] = dict(jump_q=q, overlay="P 0.41, +1.5pt", **ar_sim(x, latest_pct, jump_q=q, overlay_p=0.41, overlay_pts=1.5))
# what the post-print history says: SI change over the two settlements after each down-5% print (from the repo series where available)
hist = pd.read_csv(ROOT / "data/processed/overnight/09_positioning_short_interest.csv"); hist["settlement_date"] = pd.to_datetime(hist.settlement_date)
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv"); rx["reaction_date"] = pd.to_datetime(rx.reaction_date)
full = pd.DataFrame({"date": pd.to_datetime(dates), "pct": x}).sort_values("date")
post = []
for _, r in rx.iterrows():
    d = r.reaction_date
    before = full[full.date < d]; after = full[full.date >= d]
    if len(before) and len(after) >= 3:
        post.append({"print": r.quarter, "day1": r.abnb_1d_pct, "si_before": round(float(before.pct.iloc[-1]), 2), "si_+1": round(float(after.pct.iloc[0]), 2), "si_+2": round(float(after.pct.iloc[1]), 2), "si_+3": round(float(after.pct.iloc[2]), 2),
                     "rise_max3": round(float(after.pct.iloc[:3].max() - before.pct.iloc[-1]), 2)})
pdf = pd.DataFrame(post); pdf.to_csv(HERE / "si_after_prints.csv", index=False)
out["si_after_prints"] = {"down5_mean_rise_max3": float(pdf[pdf.day1 <= -5].rise_max3.mean()), "down5_max_rise": float(pdf[pdf.day1 <= -5].rise_max3.max()), "down5_n": int((pdf.day1 <= -5).sum()),
                          "up5_mean_rise_max3": float(pdf[pdf.day1 >= 5].rise_max3.mean()), "other_mean": float(pdf[(pdf.day1 > -5) & (pdf.day1 < 5)].rise_max3.mean())}
json.dump(out, open(HERE / "r13_summary.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
print(pdf.to_string())
