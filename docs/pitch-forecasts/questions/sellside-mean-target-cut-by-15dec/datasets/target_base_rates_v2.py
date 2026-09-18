"""Revision-2 S04 base rates (audit A07 findings 07, 08, 15, 16). Revision 1 (target_base_rates.py) is untouched.
(a) 63-session daily rates at the EXACT log threshold ln(176.8 / 183.21875) = -0.03566 (and the unadjusted-feed
    threshold ln(176.8 / 181.8125)), with the -0.035 cutoff of revision 1 beside them; overlapping days disclosed.
(b) print-centred windows on the revision-2 session shape (-36 to +26 sessions around each reaction day).
(c) the residual of the EXACT hybrid tape equation used by the Monte Carlo, evaluated on every historical print
    window with enough history (blocks: two known lags of 21 sessions before the window, p1 21 sessions, p2pre 15,
    day-1, post 26; coefficients as in the model), all / W1 / W2.
(d) the corrected down-print class (day-1 <= -5%: 3Q22, 1Q23, 1Q24, 2Q24, 3Q24, 2Q25; 2Q22 at -1.13% is not in it).
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/sellside-mean-target-cut-by-15dec/datasets/target_base_rates_v2.py
"""
import glob, json, math, pathlib
import numpy as np, pandas as pd
here = pathlib.Path(__file__).resolve().parent
root = here.parents[4]
p = pd.read_csv(root / "data/processed/reverse_dcf/D/D_target_panel_daily.csv", parse_dates=["date"]).dropna(subset=["mean_target"])
p = p[p.n_targets >= 10].set_index("date").sort_index()
lt = np.log(p.mean_target); lp = np.log(p.close)
rx = pd.read_csv(root / "data/processed/abnb_earnings_reactions.csv", parse_dates=["reaction_date"])
out = {}
# (a) exact thresholds
f = sorted(glob.glob(str(here.parent / "sources" / "yfinance_upgrades_downgrades_*.csv")))[-1]
ud = pd.read_csv(f, parse_dates=["GradeDate"]); asof = pd.Timestamp("2026-09-16")
u = ud[(ud.GradeDate >= asof - pd.Timedelta(days=365)) & (ud.GradeDate <= asof + pd.Timedelta(days=1)) & (ud.currentPriceTarget > 0)]
live = u.sort_values("GradeDate").groupby("Firm").tail(1)
base_feed = float(live.currentPriceTarget.mean()); base_ms = float(live.currentPriceTarget.where(live.Firm != "Morgan Stanley", 170.0).mean())
out["live_tape_16sep"] = dict(n=int(len(live)), mean=base_feed, mean_with_MS_170=base_ms)
d63 = (lt.shift(-63) - lt).dropna()
out["thresholds_log"] = {"rev1_cutoff": -0.035, "exact_MS_adjusted": math.log(176.8 / base_ms), "exact_feed_asis": math.log(176.8 / base_feed)}
out["63s_rates"] = {}
for lab, dd in (("all", d63), ("2023+", d63[d63.index >= "2023-01-01"]), ("2024+", d63[d63.index >= "2024-01-01"])):
    out["63s_rates"][lab] = {k: dict(n=int(len(dd)), hits=int((dd <= t).sum()), p=float((dd <= t).mean()))
                             for k, t in out["thresholds_log"].items()}
    out["63s_rates"][lab]["note"] = "overlapping daily windows; effective independent observations ~ n/63"
# (b) print windows -36/+26 and (c) hybrid residual
b0, b1, b2, chase = 0.075, 0.13, 0.10, 0.40
rows = []
for _, e in rx.iterrows():
    if e.reaction_date not in p.index: continue
    i = p.index.get_loc(e.reaction_date)
    if i - 78 < 0 or i + 26 >= len(p): continue
    plag2 = lp.iloc[i - 57] - lp.iloc[i - 78]; plag1 = lp.iloc[i - 36] - lp.iloc[i - 57]
    p1 = lp.iloc[i - 15] - lp.iloc[i - 36]; p2 = lp.iloc[i - 1] - lp.iloc[i - 15]; d1 = lp.iloc[i] - lp.iloc[i - 1]; post = lp.iloc[i + 26] - lp.iloc[i]
    dT = lt.iloc[i + 26] - lt.iloc[i - 36]
    pred = (b1 + b2) * plag1 + b2 * plag2 + (b0 + b1 + b2) * p1 + (b0 + b1) * p2 + chase * d1 + (b0 + 0.5 * b1) * post + 3 * 0.0005
    rows.append(dict(q=e.quarter, start=p.index[i - 36].date(), end=p.index[i + 26].date(), d_target_log_pct=dT * 100, d_target_simple_pct=(math.exp(dT) - 1) * 100,
                     pred_log_pct=pred * 100, resid_pct=(dT - pred) * 100, day1_pct=d1 * 100, p1_pct=p1 * 100, p2pre_pct=p2 * 100, post_pct=post * 100,
                     plag1_pct=plag1 * 100, plag2_pct=plag2 * 100))
w = pd.DataFrame(rows); w.to_csv(here / "target_change_print_windows_v2.csv", index=False)
gate_simple = (176.8 / base_ms - 1) * 100
out["print_windows_36_26"] = {}
for lab, g in (("all", w), ("W1", w[w.q >= "2023Q1"]), ("W2", w[w.q >= "2024Q1"])):
    out["print_windows_36_26"][lab] = dict(n=int(len(g)), hits_le_gate=int((g.d_target_simple_pct <= gate_simple).sum()),
                                           share_le_gate=float((g.d_target_simple_pct <= gate_simple).mean()),
                                           hybrid_resid_mean=float(g.resid_pct.mean()), hybrid_resid_sd=float(g.resid_pct.std()),
                                           hybrid_resid_rmse=float(np.sqrt((g.resid_pct ** 2).mean())))
out["print_windows_36_26"]["gate_simple_pct"] = gate_simple
import statsmodels.api as sm
m = sm.OLS(w.d_target_log_pct, sm.add_constant(w.pred_log_pct)).fit()
out["hybrid_calibration"] = dict(const=float(m.params.iloc[0]), slope=float(m.params.iloc[1]), r2=float(m.rsquared), resid_sd=float(np.sqrt(m.mse_resid)), n=int(len(w)))
# (d) corrected down-print class
rev = pd.read_csv(root / "data/processed/reverse_dcf/D/D_print_revisions.csv")
down = rev[rev.price_move_day1_pct <= -5].sort_values("quarter")
out["down_print_class"] = dict(quarters=down.quarter.tolist(), d_mean_target_plus20_pct=[round(float(x), 2) for x in down.d_mean_target_plus20_pct],
                               any_net_cut=int((down.d_mean_target_plus20_pct < 0).sum()), cut_ge_3_8=int((down.d_mean_target_plus20_pct <= -3.8).sum()),
                               cut_ge_gate=int((down.d_mean_target_plus20_pct <= gate_simple).sum()), n=int(len(down)),
                               note="2Q22 (day-1 -1.13%, targets -10.1%) is a small-print window, not a down-5% print")
json.dump(out, open(here / "target_base_rates_v2.json", "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
