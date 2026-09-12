"""WS-D step 2: how targets and ratings move around prints (do targets chase the price, by how much, with what lag),
and positioning context (short interest, put/call, ratings mix, institutional snapshot).

Run:  py -3.13 analysis/src/reverse_dcf/D_02_revisions_positioning.py

Inputs
  data/processed/reverse_dcf/D/D_analyst_actions_2026-09-12.csv   469 actions Dec 2020 - 10 Sep 2026 (yfinance / Benzinga)
  data/processed/reverse_dcf/D/D_prices_daily_to_0911.csv         yfinance daily close
  data/processed/abnb_earnings_reactions.csv                      23 print reaction dates
  data/processed/overnight/09_positioning_short_interest.csv, 09_institutional_snapshot.csv, 04_current_consensus.csv
  data/processed/abnb_options_ledger.csv                          5-6 Sep 2026 Yahoo chains (put/call OI and volume, 25d skew)
  data/processed/reverse_dcf/D/D_yf_recommendations.csv           yfinance monthly recommendation counts

Outputs data/processed/reverse_dcf/D/
  D_target_panel_daily.csv        running live-target panel (latest target per firm within 365 days) and rating shares, by trading day
  D_print_revisions.csv           all 23 prints: mean target before / after at +1, +5, +20, +40 sessions, number and median size of
                                  target changes in [-5, +25] sessions (LOWER BOUNDS: the feed drops about a third of intermediate
                                  actions, audit finding 3), price move, chase ratio
  D_print_revisions_summary.csv   up prints (day-1 +5% or better) vs down prints (-5% or worse) vs the rest
  D_print_revision_actions.csv    every target change in [-5, +25] sessions around every print
  D_chase_regression.csv          21-session log change in mean target on contemporaneous and lagged price changes: overlapping daily
                                  Newey-West, and non-overlapping blocks at ALL 21 offsets (mean and range; audit finding 2)
  D_chase_asymmetry.csv           sign-split regressions (falls vs rises) and the mean-target response after non-print 21-session
                                  moves of 15%+ (audit finding 1)
  D_positioning_summary.csv       short interest, put/call, ratings mix (three conventions), institutional snapshot, tape vs price
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = os.path.join(ROOT, "data", "processed", "reverse_dcf", "D")
PR = os.path.join(ROOT, "data", "processed")
OV = os.path.join(PR, "overnight")
PRICE = 170.19

RB = {"Buy": "Buy", "Outperform": "Buy", "Overweight": "Buy", "Positive": "Buy", "Market Outperform": "Buy", "Strong Buy": "Buy",
      "Neutral": "Hold", "Hold": "Hold", "Equal-Weight": "Hold", "Market Perform": "Hold", "Sector Weight": "Hold", "In-Line": "Hold",
      "Perform": "Hold", "Sector Perform": "Hold", "Peer Perform": "Hold",
      "Sell": "Sell", "Underweight": "Sell", "Underperform": "Sell", "Reduce": "Sell"}

acts = pd.read_csv(os.path.join(D, "D_analyst_actions_2026-09-12.csv"), parse_dates=["grade_datetime"])
acts["d"] = acts.grade_datetime.dt.normalize()
acts["bucket"] = acts.ToGrade.map(RB).fillna("Other")
px = pd.read_csv(os.path.join(D, "D_prices_daily_to_0911.csv"), parse_dates=["date"]).set_index("date")["close"]
days = px.index

# ---------------- running panel: latest target per firm within 365 days ----------------
WIN = pd.Timedelta(days=365)
tgt_acts = acts[acts.currentPriceTarget > 0].sort_values("grade_datetime")
rows = []
firms = acts.Firm.unique()
for d in days:
    a = acts[acts.d <= d]
    a = a.groupby("Firm").tail(1)
    rated = a[a.d >= d - pd.Timedelta(days=730)]          # rating live for 24 months
    t = tgt_acts[tgt_acts.d <= d].groupby("Firm").tail(1)
    t = t[t.d >= d - WIN]
    rows.append(dict(date=d, close=px[d], n_targets=len(t), mean_target=t.currentPriceTarget.mean() if len(t) else np.nan,
                     median_target=t.currentPriceTarget.median() if len(t) else np.nan,
                     n_rated_24m=len(rated), share_buy_24m=(rated.bucket == "Buy").mean() if len(rated) else np.nan,
                     share_hold_or_worse_24m=(rated.bucket.isin(["Hold", "Sell"])).mean() if len(rated) else np.nan,
                     share_sell_24m=(rated.bucket == "Sell").mean() if len(rated) else np.nan))
PAN = pd.DataFrame(rows).set_index("date")
PAN["pt_premium_pct"] = 100 * (PAN.mean_target / PAN.close - 1)
PAN.to_csv(os.path.join(D, "D_target_panel_daily.csv"))
print(PAN.tail(12).round(3).to_string())

# ---------------- print-by-print revision pattern ----------------
ER = pd.read_csv(os.path.join(PR, "abnb_earnings_reactions.csv"), parse_dates=["reaction_date"])
ER = ER.sort_values("reaction_date")            # all 23 prints (audit finding 1)
out, detail = [], []
for _, r in ER.iterrows():
    rd = r.reaction_date
    i = days.get_indexer([rd])[0]
    if i < 0:
        i = days.searchsorted(rd)
    pos = {k: days[min(max(i + k, 0), len(days) - 1)] for k in [-1, 0, 1, 5, 20, 40]}
    m = {k: PAN.loc[v, "mean_target"] for k, v in pos.items()}
    p = {k: PAN.loc[v, "close"] for k, v in pos.items()}
    lo, hi = days[max(i - 5, 0)], days[min(i + 25, len(days) - 1)]
    w = acts[(acts.d >= lo) & (acts.d <= hi) & (acts.currentPriceTarget > 0) & (acts.priorPriceTarget > 0)
             & (acts.currentPriceTarget != acts.priorPriceTarget)].copy()
    w["chg_pct"] = 100 * (w.currentPriceTarget / w.priorPriceTarget - 1)
    w["sessions_after_print"] = [days.get_indexer([x])[0] - i if days.get_indexer([x])[0] >= 0 else days.searchsorted(x) - i for x in w.d]
    w["quarter"] = r.quarter
    detail.append(w)
    same_day = w[w.sessions_after_print == 0]
    within5 = w[(w.sessions_after_print >= 0) & (w.sessions_after_print <= 5)]
    rating_w = acts[(acts.d >= lo) & (acts.d <= hi)]
    ups = (rating_w.Action == "up").sum(); downs = (rating_w.Action == "down").sum()
    price_1d = 100 * (p[0] / p[-1] - 1)
    out.append(dict(quarter=r.quarter, reaction_date=rd.date(), price_day_before=p[-1], price_day1=p[0], price_move_day1_pct=price_1d,
                    price_move_to_plus20_pct=100 * (p[20] / p[-1] - 1),
                    price_runup_prior_21_sessions_pct=100 * (p[-1] / PAN.close.iloc[max(i - 22, 0)] - 1),
                    n_targets_day_before=int(PAN.loc[pos[-1], "n_targets"]),
                    mean_target_day_before=m[-1], mean_target_day1=m[0], mean_target_plus1=m[1], mean_target_plus5=m[5], mean_target_plus20=m[20],
                    mean_target_plus40=m[40],
                    d_mean_target_day1_pct=100 * (m[0] / m[-1] - 1), d_mean_target_plus5_pct=100 * (m[5] / m[-1] - 1),
                    d_mean_target_plus20_pct=100 * (m[20] / m[-1] - 1), d_mean_target_plus40_pct=100 * (m[40] / m[-1] - 1),
                    chase_ratio_plus5=(m[5] / m[-1] - 1) / (p[0] / p[-1] - 1) if abs(price_1d) > 1 else np.nan,
                    chase_ratio_plus20=(m[20] / m[-1] - 1) / (p[0] / p[-1] - 1) if abs(price_1d) > 1 else np.nan,
                    chase_ratio_plus40=(m[40] / m[-1] - 1) / (p[0] / p[-1] - 1) if abs(price_1d) > 1 else np.nan,
                    n_target_changes_m5_to_p25_lower_bound=len(w), n_raises_lower_bound=(w.chg_pct > 0).sum(), n_cuts_lower_bound=(w.chg_pct < 0).sum(),
                    median_change_pct=w.chg_pct.median(), mean_change_pct=w.chg_pct.mean(),
                    n_same_day=len(same_day), n_within_5_sessions=len(within5), share_within_5_sessions=len(within5) / len(w) if len(w) else np.nan,
                    rating_upgrades=ups, rating_downgrades=downs,
                    pt_premium_day_before_pct=100 * (m[-1] / p[-1] - 1), pt_premium_plus20_pct=100 * (m[20] / p[20] - 1)))
REV = pd.DataFrame(out)
REV["print_class"] = np.where(REV.price_move_day1_pct >= 5, "up 5%+", np.where(REV.price_move_day1_pct <= -5, "down 5%+", "small"))
REV.to_csv(os.path.join(D, "D_print_revisions.csv"), index=False)
RS = REV.groupby("print_class").agg(n_prints=("quarter", "count"), mean_price_move_day1_pct=("price_move_day1_pct", "mean"),
                                    mean_d_target_plus20_pct=("d_mean_target_plus20_pct", "mean"), mean_d_target_plus40_pct=("d_mean_target_plus40_pct", "mean"),
                                    median_d_target_plus20_pct=("d_mean_target_plus20_pct", "median"),
                                    prints_with_target_cut_at_plus20=("d_mean_target_plus20_pct", lambda x: int((x < 0).sum())),
                                    raises_lower_bound=("n_raises_lower_bound", "sum"), cuts_lower_bound=("n_cuts_lower_bound", "sum"),
                                    mean_pt_premium_day_before_pct=("pt_premium_day_before_pct", "mean")).reset_index()
RS["chase_ratio_plus20"] = RS.mean_d_target_plus20_pct / RS.mean_price_move_day1_pct
RS["chase_ratio_plus40"] = RS.mean_d_target_plus40_pct / RS.mean_price_move_day1_pct
RS.to_csv(os.path.join(D, "D_print_revisions_summary.csv"), index=False)
print(RS.round(2).to_string())
DET = pd.concat(detail)[["quarter", "d", "sessions_after_print", "Firm", "ToGrade", "Action", "priceTargetAction", "priorPriceTarget", "currentPriceTarget", "chg_pct"]]
DET.to_csv(os.path.join(D, "D_print_revision_actions.csv"), index=False)
print(REV[["quarter", "price_move_day1_pct", "price_runup_prior_21_sessions_pct", "d_mean_target_plus20_pct", "d_mean_target_plus40_pct", "chase_ratio_plus20", "n_raises_lower_bound", "n_cuts_lower_bound", "median_change_pct", "pt_premium_day_before_pct", "print_class"]].round(2).to_string())

# 2Q26 detail: mean target on 6 Aug, 7 Aug, 10 Aug, 4 Sep, 11 Sep
for dstr in ["2026-08-06", "2026-08-07", "2026-08-10", "2026-08-14", "2026-09-04", "2026-09-11"]:
    d = pd.Timestamp(dstr)
    print(dstr, "mean target", round(PAN.loc[d, "mean_target"], 2), "n", PAN.loc[d, "n_targets"], "close", round(PAN.loc[d, "close"], 2))

# ---------------- chase regression: 21-session change in log mean target on price changes ----------------
L = 21
S = PAN[PAN.n_targets >= 10].copy()
S["dlt"] = np.log(S.mean_target).diff(L)
S["dlp0"] = np.log(S.close).diff(L)
S["dlp1"] = S.dlp0.shift(L)
S["dlp2"] = S.dlp0.shift(2 * L)
S = S.dropna(subset=["dlt", "dlp0", "dlp1", "dlp2"])
reg = []
def fit(df, spec, hac):
    X = sm.add_constant(df[spec])
    return sm.OLS(df.dlt, X).fit(cov_type="HAC", cov_kwds={"maxlags": L}) if hac else sm.OLS(df.dlt, X).fit()
def rec(lab, spec, f, offset=np.nan):
    d = dict(sample=lab, block_offset=offset, spec="+".join(spec), n=int(f.nobs), r2=f.rsquared, const=f.params["const"])
    for k in ["dlp0", "dlp1", "dlp2"]:
        d[f"b_{k}"] = f.params.get(k, np.nan); d[f"t_{k}"] = f.tvalues.get(k, np.nan)
    d["sum_betas"] = sum(f.params[k] for k in spec)
    return d
for spec in [["dlp0"], ["dlp0", "dlp1"], ["dlp0", "dlp1", "dlp2"]]:
    reg.append(rec("overlapping daily (NW lags 21)", spec, fit(S, spec, True)))
reg.append(rec("overlapping daily (NW lags 21), from 2023", ["dlp0", "dlp1", "dlp2"], fit(S[S.index >= "2023-01-01"], ["dlp0", "dlp1", "dlp2"], True)))
# non-overlapping 21-session blocks at every one of the 21 possible offsets (audit finding 2: offset 0 alone is a selected draw)
per_offset = []
for off in range(L):
    S_no = S.iloc[off::L]
    per_offset.append(rec("non-overlapping 21-session blocks", ["dlp0", "dlp1", "dlp2"], fit(S_no, ["dlp0", "dlp1", "dlp2"], False), off))
PO = pd.DataFrame(per_offset)
for stat, fn in [("mean over 21 offsets", "mean"), ("min over 21 offsets", "min"), ("max over 21 offsets", "max")]:
    d = dict(sample="non-overlapping 21-session blocks, " + stat, block_offset=np.nan, spec="dlp0+dlp1+dlp2")
    for c in ["n", "r2", "const", "b_dlp0", "t_dlp0", "b_dlp1", "t_dlp1", "b_dlp2", "t_dlp2", "sum_betas"]:
        d[c] = getattr(PO[c], fn)()
    reg.append(d)
reg.append(dict(sample="non-overlapping 21-session blocks, offsets with contemporaneous t > 1.96", block_offset=np.nan, spec="dlp0+dlp1+dlp2",
                n=int((PO.t_dlp0 > 1.96).sum())))
reg += per_offset
REG = pd.DataFrame(reg)
REG.to_csv(os.path.join(D, "D_chase_regression.csv"), index=False)
print(REG[REG.block_offset.isna()].round(3).to_string())

# sign-split: falls and rises as separate regressors (audit finding 1)
asym = []
for k in ["dlp0", "dlp1", "dlp2"]:
    S[f"{k}_neg"] = S[k].clip(upper=0); S[f"{k}_pos"] = S[k].clip(lower=0)
split = [f"{k}_{sgn}" for k in ["dlp0", "dlp1", "dlp2"] for sgn in ["neg", "pos"]]
def rec_split(lab, f):
    d = dict(sample=lab, n=int(f.nobs), r2=f.rsquared)
    for c in split:
        d[f"b_{c}"] = f.params[c]; d[f"t_{c}"] = f.tvalues[c]
    d["sum_neg_betas"] = sum(f.params[c] for c in split if c.endswith("neg")); d["sum_pos_betas"] = sum(f.params[c] for c in split if c.endswith("pos"))
    return d
asym.append(rec_split("overlapping daily (NW lags 21)", sm.OLS(S.dlt, sm.add_constant(S[split])).fit(cov_type="HAC", cov_kwds={"maxlags": L})))
so = []
for off in range(L):
    S_no = S.iloc[off::L]
    so.append(rec_split(f"blocks offset {off}", sm.OLS(S_no.dlt, sm.add_constant(S_no[split])).fit()))
SO = pd.DataFrame(so)
for stat, fn in [("mean over 21 offsets", "mean"), ("min over 21 offsets", "min"), ("max over 21 offsets", "max")]:
    d = dict(sample="non-overlapping blocks, " + stat)
    for c in SO.columns[1:]:
        d[c] = getattr(SO[c], fn)()
    asym.append(d)
# non-print moves: mean-target change over the next 42 sessions after a 21-session move of 15%+
print_days = set(pd.to_datetime(ER.reaction_date))
PAN2 = PAN.copy(); PAN2["dlp21"] = np.log(PAN2.close).diff(L); PAN2["fwd42_target_pct"] = 100 * (PAN2.mean_target.shift(-2 * L) / PAN2.mean_target - 1)
idx = list(PAN2.index)
PAN2["has_print_in_window"] = [any((idx[j] in print_days) for j in range(max(k - L, 0), k + 1)) for k in range(len(idx))]
ALL = PAN2[PAN2.n_targets >= 10].dropna(subset=["dlp21", "fwd42_target_pct"])
NP = ALL[~ALL.has_print_in_window]
for lab, src, cond in [("21-session fall of 15%+ (no print in window)", NP, lambda x: x.dlp21 <= np.log(0.85)),
                       ("21-session rise of 15%+ (no print in window)", NP, lambda x: x.dlp21 >= np.log(1.15)),
                       ("21-session fall of 15%+ (any window)", ALL, lambda x: x.dlp21 <= np.log(0.85)),
                       ("21-session rise of 15%+ (any window)", ALL, lambda x: x.dlp21 >= np.log(1.15))]:
    sub = src[cond(src)]
    asym.append(dict(sample=lab, n=len(sub), r2=np.nan, mean_fwd42_target_change_pct=sub.fwd42_target_pct.mean(), median_fwd42_target_change_pct=sub.fwd42_target_pct.median(),
                     share_negative=(sub.fwd42_target_pct < 0).mean() if len(sub) else np.nan,
                     n_distinct_episodes=int((sub.index.to_series().diff() > pd.Timedelta(days=5)).sum() + 1) if len(sub) else 0))
ASY = pd.DataFrame(asym)
ASY.to_csv(os.path.join(D, "D_chase_asymmetry.csv"), index=False)
print(ASY.round(3).to_string())

# ---------------- positioning ----------------
SI = pd.read_csv(os.path.join(OV, "09_positioning_short_interest.csv"), parse_dates=["settlement_date"]).sort_values("settlement_date")
si_last = SI.iloc[-1]
INST = pd.read_csv(os.path.join(OV, "09_institutional_snapshot.csv"))
OPT = pd.read_csv(os.path.join(PR, "abnb_options_ledger.csv"))
OPT = OPT[(OPT.ticker == "ABNB") & (OPT.schema_version == 2)]
REC = pd.read_csv(os.path.join(D, "D_yf_recommendations.csv"))
r0 = REC[REC.period == "0m"].iloc[0]; r3 = REC[REC.period == "-3m"].iloc[0]
yf_n = r0[["strongBuy", "buy", "hold", "sell", "strongSell"]].sum()
last_row = PAN.iloc[-1]
recent = acts[acts.d >= pd.Timestamp("2026-09-12") - pd.Timedelta(days=365)].groupby("Firm").tail(1)
recent_mix = recent.bucket.value_counts()
pos = [
    dict(block="short interest", item="latest short interest, % of shares out", value=si_last.si_pct_shares, unit="%",
         detail=f"{si_last.short_interest_shares/1e6:.2f}m shares, settlement {si_last.settlement_date.date()}; series mean {SI.si_pct_shares.mean():.2f}%, "
                f"min {SI.si_pct_shares.min():.2f}%, max {SI.si_pct_shares.max():.2f}% over {len(SI)} settlements Feb 2023 - Aug 2026", label="MEASURED", source="09_positioning_short_interest.csv (MarketBeat/Nasdaq)"),
    dict(block="short interest", item="percentile of latest reading in its own history", value=100 * (SI.si_pct_shares < si_last.si_pct_shares).mean(), unit="pctile", detail="lower = less short interest than usual", label="MEASURED", source="same"),
    dict(block="short interest", item="days to cover (latest SI / 20d avg volume)", value=np.nan, unit="days", detail="not in the file; not computed", label="", source=""),
    dict(block="short interest", item="correlation of SI level with fwd 3m excess return", value=0.153, unit="r", detail="n 78, p 0.18; change in SI r -0.08 (1m), +0.04 (3m): none detectable in-sample at n 77-82", label="MEASURED", source="09_positioning_tests.csv"),
]
for _, o in OPT[OPT.expiry.isin(["2026-11-20", "2026-12-18", "2027-01-15"])].iterrows():
    pos.append(dict(block="options", item=f"put/call open interest, {o.expiry} expiry", value=o.put_call_oi, unit="ratio",
                    detail=f"put/call volume {o.put_call_vol:.2f}; 25-delta skew {o.skew25_pts:+.2f} vol pts (put IV minus call IV); ATM IV {o.raw_atm_iv_pct:.1f}%; straddle {o.raw_straddle_mid_pct_spot:.2f}% of spot; run {o.run_date}",
                    label="MEASURED", source="data/processed/abnb_options_ledger.csv (Yahoo chain 6 Sep 2026)"))
pos += [
    dict(block="ratings", item="Hold-or-worse share, S&P Global 46 analysts (3 Sep 2026)", value=100 * 21 / 46, unit="%",
         detail="21 Strong Buy / 4 Buy / 18 Hold / 1 Sell / 2 Strong Sell; stockanalysis.com 3 Sep 2026", label="ANCHOR", source="04_current_consensus.csv, 12 note s.5"),
    dict(block="ratings", item="Hold-or-worse share, yfinance recommendations current month", value=100 * (r0.hold + r0.sell + r0.strongSell) / yf_n, unit="%",
         detail=f"{r0.strongBuy} SB / {r0.buy} B / {r0.hold} H / {r0.sell} S / {r0.strongSell} SS = {yf_n}; three months ago {r3.strongBuy}/{r3.buy}/{r3.hold}/{r3.sell}/{r3.strongSell}", label="MEASURED", source="D_yf_recommendations.csv (pulled 12 Sep 2026)"),
    dict(block="ratings", item="Hold-or-worse share, feed firms with an action in 365 days (12 Sep 2026)", value=100 * (recent_mix.get("Hold", 0) + recent_mix.get("Sell", 0)) / recent_mix.sum(), unit="%",
         detail=f"{recent_mix.get('Buy',0)} Buy / {recent_mix.get('Hold',0)} Hold / {recent_mix.get('Sell',0)} Sell of {recent_mix.sum()} (Goldman counted as Sell per feed; 1 fewer Sell, 1 more Hold if corrected)", label="MEASURED", source="D_analyst_actions_2026-09-12.csv"),
    dict(block="ratings", item="Hold-or-worse share, the 32 firms with a live target (12 Sep 2026)", value=100 * 10 / 32, unit="%",
         detail="22 Buy / 8 Hold / 2 Sell (feed) or 22 / 9 / 1 (Goldman corrected); either way 10 of 32", label="MEASURED", source="D_live_targets_2026-09-12.csv"),
    dict(block="ratings", item="Buy share, 24-month rating panel (09 convention), 11 Sep 2026", value=100 * last_row.share_buy_24m, unit="%",
         detail=f"{int(last_row.n_rated_24m)} firms rated in the last 24 months; Hold-or-worse {100*last_row.share_hold_or_worse_24m:.1f}%; 4 Sep 2026 09 note: 49% Buy / 43% Hold / 8% Sell on 49 firms", label="MEASURED", source="D_target_panel_daily.csv"),
    dict(block="ratings", item="Buy share vs forward 3m excess return", value=0.128, unit="r", detail="n 66, p 0.30; 3m change in Buy share vs fwd 1m r -0.24 p 0.05, n 65 (contrarian-signed; in-sample, no out-of-sample test)", label="MEASURED", source="09_positioning_tests.csv"),
    dict(block="targets", item="mean live target vs $170.19 (premium), 11 Sep 2026", value=last_row.pt_premium_pct, unit="%",
         detail=f"mean ${last_row.mean_target:.2f} on {int(last_row.n_targets)} targets (365-day window); yfinance 12 Sep mean $182.13, median $185; S&P 3 Sep $178.96; MarketBeat 11 Sep $179.97", label="MEASURED", source="D_target_panel_daily.csv; D_yf_analyst_price_targets.csv"),
    dict(block="targets", item="PT premium vs forward 3m excess, quarterly non-overlapping from 2023", value=0.225, unit="r", detail="n 13, p 0.46; the full-sample r +0.51 is 2021-22 mean reversion in disguise (09 note s.9); in-sample only", label="MEASURED", source="09_positioning_tests.csv"),
    dict(block="institutional", item="institutional holders (13F, 30 Jun 2026)", value=float(INST[INST.metric == "institutional holders"].value.iloc[0]), unit="count", detail="single fintel.io snapshot; no quarterly history, so no change-in-ownership series exists in the files", label="MEASURED", source="09_institutional_snapshot.csv"),
    dict(block="institutional", item="institutions increasing / decreasing (2Q26 filings)", value=float(INST[INST.metric == "institutions increasing / decreasing"].value.iloc[0]), unit="ratio", detail="1,020 buyers vs 884 sellers; top-10 holders 33.2% of disclosed shares", label="MEASURED", source="same"),
    dict(block="institutional", item="shares reported long by institutions, % of basic shares (589.6m)", value=100 * float(INST[INST.metric == "institutional shares held (long)"].value.iloc[0]) / 589.6e6, unit="%", detail="468.9m / 589.6m basic (15 Jul 2026)", label="MEASURED", source="same; BRIEF share count"),
]
POS = pd.DataFrame(pos)
POS.to_csv(os.path.join(D, "D_positioning_summary.csv"), index=False)
print(POS[["block", "item", "value", "unit", "label"]].round(3).to_string())
