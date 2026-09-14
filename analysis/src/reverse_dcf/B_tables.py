"""Workstream B: headline and synthesis tables built from the B_*.csv outputs.

Writes B_headline.csv, B_price_points_for_synthesis.csv, B_implied_vs_realised_print.csv,
B_reconcile_reaction_files.csv.  Run after B_options_implied.py and B_bloomberg_summary.py, from this directory:
    py -3.13 B_tables.py

Audit (12 Sep 2026) changes: the realised print series is reported twice (raw close-to-close, and the QQQ-excess
`legacy_1d_pct` that earlier notes used); the headline 12-month quartiles are the lognormal ones, the skew-adjusted
RND is carried as a sensitivity; the reconciliation with abnb_earnings_reactions.csv adds QQQ back.
"""
from __future__ import annotations
import math
import numpy as np, pandas as pd
from scipy.stats import norm
import B_options_implied as B

OUT = B.OUT
ch = pd.read_csv(OUT / "B_chain_clean.csv")
ts = pd.read_csv(OUT / "B_term_structure.csv")
ev = pd.read_csv(OUT / "B_event_variance.csv").set_index("spec")
sk = pd.read_csv(OUT / "B_skew.csv").set_index("expiry")
d12 = pd.read_csv(OUT / "B_dist_12m_percentiles.csv").set_index("method")
p12 = pd.read_csv(OUT / "B_dist_12m_price_points.csv")
br = pd.read_csv(OUT / "B_print_base_rates.csv")
br_raw = br[br.series == "raw"].set_index("sample"); br_exc = br[br.series == "excess"].set_index("sample")
mv = pd.read_csv(OUT / "B_print_moves.csv")
bbg_pp = pd.read_csv(OUT / "B_bbg_print_implied_vs_realised_summary.csv").set_index("stat").value
bbg_ms = pd.read_csv(OUT / "B_bbg_monthly_straddles_summary.csv").set_index("sample")
bbg_f4 = pd.read_csv(OUT / "B_bbg_event_fit_4sep_chain.csv").set_index("spec")
leg = pd.read_csv(OUT / "B_event_sd_leg_sensitivity.csv")
LOGN, SKEW = "lognormal_atm_iv_12m_interp", "skew_adjusted_rnd_smile_interp"

# ---- 20 Nov risk-neutral distribution for the price points (the print expiry)
g = ch[ch.expiry == "2026-11-20"]; sm = B.fit_smile(g); T = g["T"].iloc[0]; F = g.F.iloc[0]
K, f, cdf, neg = B.rnd_from_smile(sm, F, T, B.R)
rows = []
for x in B.PRICE_POINTS + [125.0]:
    r12 = p12[(p12.method == SKEW) & (p12.price_point == x)].iloc[0]
    l12 = p12[(p12.method == LOGN) & (p12.price_point == x)].iloc[0]
    rows.append(dict(price_point=x, label=B.BRIEF_LABELS.get(x, "below $125 (MS-style bear)"), pct_vs_spot=round((x / B.SPOT - 1) * 100, 1),
                     p_above_20nov_rnd=round(B.prob_above(K, cdf, x), 3), p_below_20nov_rnd=round(1 - B.prob_above(K, cdf, x), 3),
                     p_above_12m_lognormal=l12.p_above, p_below_12m_lognormal=l12.p_below,
                     p_above_12m_skew_rnd=r12.p_above, p_below_12m_skew_rnd=r12.p_below))
pp = pd.DataFrame(rows)
# options-implied 12M quartiles as price points: lognormal is the headline, skew-adjusted RND the sensitivity
lo, sa = d12.loc[LOGN], d12.loc[SKEW]
def _logn_above(x):
    s, F12, T12 = lo.atm_iv_pct / 100, lo.forward, 1.0
    return 1 - norm.cdf((math.log(x / F12) + 0.5 * s * s * T12) / (s * math.sqrt(T12)))
grid = pd.read_csv(OUT / "B_rnd_12m_grid.csv")
def _skew_above(x):
    return float(1 - np.interp(x, grid.K, grid.cdf))
for method, src, tag in ((LOGN, lo, "lognormal, HEADLINE"), (SKEW, sa, "skew-adjusted RND, sensitivity")):
    for q, v in [("p25", src.p25), ("p50", src.p50), ("p75", src.p75)]:
        pp.loc[len(pp)] = dict(price_point=v, label=f"options-implied 12M {q} ({tag})", pct_vs_spot=round((v / B.SPOT - 1) * 100, 1),
                               p_above_20nov_rnd=round(B.prob_above(K, cdf, v), 3), p_below_20nov_rnd=round(1 - B.prob_above(K, cdf, v), 3),
                               p_above_12m_lognormal=round(_logn_above(v), 3), p_below_12m_lognormal=round(1 - _logn_above(v), 3),
                               p_above_12m_skew_rnd=round(_skew_above(v), 3), p_below_12m_skew_rnd=round(1 - _skew_above(v), 3))
pp["note"] = "risk-neutral probabilities, not real-world; RN median below spot is the drift (carry less half the variance), not a view"
pp.to_csv(OUT / "B_price_points_for_synthesis.csv", index=False)

# ---- implied event distribution vs realised print distribution (raw is the like-for-like series)
rows = []
for label, sd in [("live pair 16Oct/20Nov", ev.loc["pair_2026-10-16_vs_20Nov", "event_sd_pct"]),
                  ("live LS one-print expiries", ev.loc["LS_to_Jan27_one_print_max", "event_sd_pct"]),
                  ("live LS all maturities, sloped background", ev.loc["LS_all_maturities_multi_print_slope_bg", "event_sd_pct"]),
                  ("live two post-event expiries (20Nov/18Dec)", ev.loc["pair_20Nov_vs_18Dec_both_post", "event_sd_pct"]),
                  ("central reading (JUDGEMENT)", 9.5),
                  ("BBG history: mean IV-crush implied sd, 23 prints", bbg_pp["mean_implied_event_sd_crush_pct"]),
                  ("BBG history: mean 30D/60D kink implied sd at print-45d, 23 prints", bbg_pp["mean_implied_event_sd_kink45_pct"]),
                  ("realised rms, raw close-to-close, 23 prints", br_raw.loc["all_23_prints", "rms_pct"]),
                  ("realised rms, QQQ-excess close-to-close, 23 prints", br_exc.loc["all_23_prints", "rms_pct"])]:
    rows.append(dict(source=label, event_sd_pct=sd, exp_abs_move_pct=round(sd * math.sqrt(2 / math.pi), 2),
                     **{f"p_abs_ge_{th}": round(2 * (1 - norm.cdf(th / sd)), 3) for th in (3, 5, 7, 10, 15)}))
for col, lab in (("raw_cc_1d_pct", "raw"), ("excess_cc_1d_pct", "QQQ-excess")):
    x = mv[col]
    rows.append(dict(source=f"REALISED share of 23 prints ({lab} close-to-close)", event_sd_pct=np.nan, exp_abs_move_pct=round(x.abs().mean(), 2),
                     **{f"p_abs_ge_{th}": round(float((x.abs() >= th).mean()), 3) for th in (3, 5, 7, 10, 15)}))
pd.DataFrame(rows).to_csv(OUT / "B_implied_vs_realised_print.csv", index=False)

# ---- reconcile the two reaction files: 20_executable_returns legacy_1d_pct is abnb_earnings_reactions excess_1d_pct;
#      raw close-to-close equals abnb_1d_pct.  The difference between the two series is QQQ on the reaction day.
er = pd.read_csv(B.ROOT / "data" / "processed" / "abnb_earnings_reactions.csv").rename(columns={"quarter": "print_quarter"})
rec = mv[["print_quarter", "raw_cc_1d_pct", "excess_cc_1d_pct"]].merge(er[["print_quarter", "abnb_1d_pct", "qqq_1d_pct", "excess_1d_pct"]], on="print_quarter", how="left")
rec["raw_minus_abnb_1d"] = (rec.raw_cc_1d_pct - rec.abnb_1d_pct).round(2)
rec["excess_minus_excess_1d"] = (rec.excess_cc_1d_pct - rec.excess_1d_pct).round(2)
rec["raw_minus_excess_minus_qqq"] = (rec.raw_cc_1d_pct - rec.excess_cc_1d_pct - rec.qqq_1d_pct).round(2)
rec.loc[len(rec)] = dict(print_quarter="MAX_ABS", raw_cc_1d_pct=np.nan, excess_cc_1d_pct=np.nan, abnb_1d_pct=np.nan, qqq_1d_pct=np.nan, excess_1d_pct=np.nan,
                         raw_minus_abnb_1d=rec.raw_minus_abnb_1d.abs().max(), excess_minus_excess_1d=rec.excess_minus_excess_1d.abs().max(),
                         raw_minus_excess_minus_qqq=rec.raw_minus_excess_minus_qqq.abs().max())
rec.round(3).to_csv(OUT / "B_reconcile_reaction_files.csv", index=False)

# ---- headline
nov = ts.set_index("expiry").loc["2026-11-20"]; oct16 = ts.set_index("expiry").loc["2026-10-16"]
leg_rng = f"{leg.event_sd_pct.min():.1f}..{leg.event_sd_pct.max():.1f}"
H = [
    ("pull_time_utc", B.META["pull_utc"], "MEASURED", "yfinance, Friday 11 Sep 2026 close quotes"),
    ("spot", B.SPOT, "ANCHOR", "close 11 Sep 2026"),
    ("risk_free_used_pct", B.R * 100, "JUDGEMENT", "^IRX 3.91% on 11 Sep; brief 4.0-4.2%"),
    ("first_post_print_expiry", "2026-11-20", "MEASURED", "no 6 Nov weekly listed; 15 days after the 5 Nov print"),
    ("straddle_20nov_170_mid_pct_spot", nov.straddle_mid_pct_spot, "MEASURED", f"mid of a {nov.straddle_bid_pct_spot:.1f}-{nov.straddle_ask_pct_spot:.1f} market (170 put quoted 8.85/12.30); TOTAL 70-day move, not the print"),
    ("straddle_20nov_model_atm_pct_spot", nov.model_atm_fwd_straddle_pct_spot, "MEASURED", "smile-model ATM straddle at the forward"),
    ("straddle_20nov_0p85_rule_pct", round(nov.straddle_mid_pct_spot * 0.85, 2), "MEASURED", "rule-of-thumb applied to a 70-day straddle: upper bound only, NOT the print move"),
    ("straddle_16oct_170_mid_pct_spot", oct16.straddle_mid_pct_spot, "MEASURED", "pre-print 35-day straddle"),
    ("atm_iv_16oct_pct", oct16.atm_iv_smile_pct, "MEASURED", "own Black-76 IV from mids, smile at forward"),
    ("atm_iv_20nov_pct", nov.atm_iv_smile_pct, "MEASURED", "own"),
    ("atm_iv_12m_pct", round(float(pd.read_json(OUT / "B_dist_12m_meta.json", typ="series")["atm_iv_12m_interp_pct"]), 2), "MEASURED", "variance-interpolated Jun27/Dec27"),
    ("event_sd_pair_16oct_20nov_pct", ev.loc["pair_2026-10-16_vs_20Nov", "event_sd_pct"], "MEASURED", f"E = T_post (sig_post^2 - sig_pre^2); flat background; +/-1 vol pt on either leg gives {leg_rng}"),
    ("event_sd_ls_one_print_pct", ev.loc["LS_to_Jan27_one_print_max", "event_sd_pct"], "MEASURED", f"5 maturities, LOO {ev.loc['LS_to_Jan27_one_print_max', 'loo_range']}"),
    ("event_sd_ls_all_sloped_bg_pct", ev.loc["LS_all_maturities_multi_print_slope_bg", "event_sd_pct"], "MEASURED", "11 maturities, 5 prints, background allowed to slope"),
    ("event_sd_two_post_pct", ev.loc["pair_20Nov_vs_18Dec_both_post", "event_sd_pct"], "MEASURED", "20 Nov vs 18 Dec, both contain the print"),
    ("event_sd_central_pct", "9.5 (range 8.5-10.5; identified specs 8.3-11.0)", "JUDGEMENT", "about 0.7 pt of sd per vol pt of either leg; smile fit RMSE 0.5-0.7 pt"),
    ("event_exp_abs_move_central_pct", "7.6 (range 6.8-8.4)", "JUDGEMENT", "0.80 x sd"),
    ("event_sd_4sep_bbg_chain_pair_pct", bbg_f4.loc["pair 16 Oct (pre) vs 20 Nov (post), 4 Sep chain", "event_sd_pct"], "MEASURED", "same method on the 4 Sep Bloomberg chain; within noise of the 11 Sep reading"),
    ("hist_mean_implied_sd_iv_crush_pct", bbg_pp["mean_implied_event_sd_crush_pct"], "MEASURED", "Bloomberg 30D ATM IV, print close vs reaction close, 23 prints; upper-bound style measure"),
    ("hist_mean_implied_sd_kink45_pct", bbg_pp["mean_implied_event_sd_kink45_pct"], "MEASURED", "Bloomberg 30D vs 60D IV 45 days before each print"),
    ("hist_realised_raw_rms_pct", br_raw.loc["all_23_prints", "rms_pct"], "MEASURED", "raw close-to-close, 20_executable_returns entry_postclose_px / pre_close"),
    ("hist_realised_raw_mean_abs_pct", br_raw.loc["all_23_prints", "mean_abs_pct"], "MEASURED", "same"),
    ("hist_realised_raw_median_abs_pct", br_raw.loc["all_23_prints", "median_abs_pct"], "MEASURED", "same"),
    ("hist_realised_raw_share_abs_ge_7pct", br_raw.loc["all_23_prints", "share_abs_ge_7pct"], "MEASURED", "same"),
    ("hist_realised_raw_share_abs_ge_10pct", br_raw.loc["all_23_prints", "share_abs_ge_10pct"], "MEASURED", "same"),
    ("hist_realised_raw_up_down", f"{int(br_raw.loc['all_23_prints', 'n_up'])} up / {int(br_raw.loc['all_23_prints', 'n_down'])} down", "MEASURED", "same"),
    ("hist_realised_raw_rms_over_implied_crush", bbg_pp["rms_realised_raw_over_mean_implied_sd_crush"], "MEASURED", "8.92 / 10.47"),
    ("hist_realised_excess_rms_pct", br_exc.loc["all_23_prints", "rms_pct"], "MEASURED", "QQQ-excess close-to-close (legacy_1d_pct); the series earlier notes used"),
    ("hist_realised_excess_mean_abs_pct", br_exc.loc["all_23_prints", "mean_abs_pct"], "MEASURED", "same"),
    ("hist_realised_excess_median_abs_pct", br_exc.loc["all_23_prints", "median_abs_pct"], "MEASURED", "same"),
    ("hist_realised_excess_up_down", f"{int(br_exc.loc['all_23_prints', 'n_up'])} up / {int(br_exc.loc['all_23_prints', 'n_down'])} down", "MEASURED", "same"),
    ("hist_realised_excess_rms_over_implied_crush", bbg_pp["rms_realised_excess_over_mean_implied_sd_crush"], "MEASURED", "8.48 / 10.47"),
    ("nights_accel_split_raw", f"{int(br_raw.loc['nights_accelerated_yoy_in_reported_q_(gt_0)', 'n_up'])} up / {int(br_raw.loc['nights_accelerated_yoy_in_reported_q_(gt_0)', 'n_down'])} down accel; {int(br_raw.loc['nights_decelerated_yoy_in_reported_q_(le_0)', 'n_up'])} up / {int(br_raw.loc['nights_decelerated_yoy_in_reported_q_(le_0)', 'n_down'])} down decel", "MEASURED", "threshold 0, n 8 / 11; base rate not model"),
    ("nights_accel_split_excess", f"{int(br_exc.loc['nights_accelerated_yoy_in_reported_q_(gt_0)', 'n_up'])} up / {int(br_exc.loc['nights_accelerated_yoy_in_reported_q_(gt_0)', 'n_down'])} down accel; {int(br_exc.loc['nights_decelerated_yoy_in_reported_q_(le_0)', 'n_up'])} up / {int(br_exc.loc['nights_decelerated_yoy_in_reported_q_(le_0)', 'n_down'])} down decel", "MEASURED", "1Q25 and 1Q26 flip sign once QQQ is subtracted; C's +/-0.25pt dead band moves 1Q22 and 3Q24 to flat"),
    ("rr25_20nov_volpts", sk.loc["2026-11-20", "rr25_call_minus_put_volpts"], "MEASURED", "25d call IV minus 25d put IV; negative = puts richer"),
    ("skew_90_110_20nov_volpts", sk.loc["2026-11-20", "skew_90_110_volpts"], "MEASURED", "own method, 70d; cross-method vs BBG 30D history (median 4.4) is approximate, own method reads ~1 pt below BBG"),
    ("call10_over_put10_20nov_relative_to_flat", sk.loc["2026-11-20", "call10_over_put10_relative_to_flat"], "MEASURED", "market call/put ratio is 15.5% below the flat-smile ratio, i.e. the put is 1/0.845 = 1.18x richer relative to the call than under a flat smile"),
    ("p_above_spot_20nov_rnd", sk.loc["2026-11-20", "p_above_spot_rnd"], "MEASURED", "risk-neutral"),
    ("p12m_lognormal_p10", lo.p10, "MEASURED", "HEADLINE 12M distribution: lognormal, ATM IV 39.5%, forward 177.1, risk-neutral"),
    ("p12m_lognormal_p25", lo.p25, "MEASURED", ""), ("p12m_lognormal_p50", lo.p50, "MEASURED", "below spot mechanically: RN drift = carry less half the variance"),
    ("p12m_lognormal_p75", lo.p75, "MEASURED", ""), ("p12m_lognormal_p90", lo.p90, "MEASURED", ""),
    ("p12m_skew_rnd_p25", sa.p25, "MEASURED", "sensitivity: skew-adjusted RND; mean 0.8% below forward from clipping"),
    ("p12m_skew_rnd_p50", sa.p50, "MEASURED", "sensitivity"), ("p12m_skew_rnd_p75", sa.p75, "MEASURED", "sensitivity"),
    ("p12m_skew_rnd_p10_p90", f"{sa.p10} / {sa.p90}", "JUDGEMENT", "extrapolated beyond quoted strikes; do not quote"),
    ("p12m_above_179p5", f"{pp[pp.price_point == 179.5].p_above_12m_lognormal.iloc[0]:.2f}-{pp[pp.price_point == 179.5].p_above_12m_skew_rnd.iloc[0]:.2f}", "MEASURED", "mean target; lognormal-skew RND range; risk-neutral"),
    ("p12m_above_220", f"{pp[pp.price_point == 220.0].p_above_12m_lognormal.iloc[0]:.2f}-{pp[pp.price_point == 220.0].p_above_12m_skew_rnd.iloc[0]:.2f}", "MEASURED", "top target"),
    ("p12m_below_150", f"{pp[pp.price_point == 150.0].p_below_12m_skew_rnd.iloc[0]:.2f}-{pp[pp.price_point == 150.0].p_below_12m_lognormal.iloc[0]:.2f}", "MEASURED", "bear tape"),
    ("p12m_below_125", f"{pp[pp.price_point == 125.0].p_below_12m_lognormal.iloc[0]:.2f}-{pp[pp.price_point == 125.0].p_below_12m_skew_rnd.iloc[0]:.2f}", "MEASURED", "MS target"),
    ("bbg_monthly_straddles_print_months_implied_vs_realised", f"{bbg_ms.loc['print_months', 'avg_implied_move_pct']} vs {bbg_ms.loc['print_months', 'avg_realised_move_pct']}", "MEASURED", "23 print months, 30-day straddles, realised to expiry not day 1"),
    ("bbg_monthly_straddles_nonprint_implied_vs_realised", f"{bbg_ms.loc['non_print_months', 'avg_implied_move_pct']} vs {bbg_ms.loc['non_print_months', 'avg_realised_move_pct']}", "MEASURED", "42 non-print months"),
]
pd.DataFrame(H, columns=["item", "value", "label", "note"]).to_csv(OUT / "B_headline.csv", index=False)
pd.set_option("display.width", 250)
print(pp.drop(columns=["note"]).to_string(index=False)); print(pd.read_csv(OUT / "B_implied_vs_realised_print.csv").to_string(index=False)); print(rec.tail(2).to_string(index=False))
print(pd.DataFrame(H, columns=["item", "value", "label", "note"]).to_string(index=False))
