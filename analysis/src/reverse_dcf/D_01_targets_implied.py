"""WS-D step 1: what each live sell-side price target implies for FY27 (multiple, EBITDA, revenue, nights).

Run:  py -3.13 analysis/src/reverse_dcf/D_01_targets_implied.py

Anchors (docs/reverse_dcf/BRIEF.md, do not re-derive):
  diluted shares 597.0m, net cash ex float $9,593m (2Q26 10-Q)            -> "spot basis" EV = target x 597.0 - 9,593
  FY27-end basis: 570.7m diluted, net cash $10,609m (management delivered) -> sensitivity column
  management delivered FY27: revenue $16,025m, adj EBITDA $5,801m, margin 36.2%, EPS $6.08; FY26 revenue $14,231m
  exit multiples the team supports: 13.5 / 16.5 / 18.5x EV/FY27 EBITDA
  decomposition (JUDGEMENT, task-set, not in the brief): revenue growth = nights + ADR ex-FX + FX + take-rate change (log-additive); ADR +3%, FX -0.6pp, take rate flat

Outputs data/processed/reverse_dcf/D/
  D_live_targets_2026-09-12.csv       the live tape (latest action per firm in the last 365 days, target > 0), 6 Sep vs 12 Sep
  D_target_implied.csv                per target: implied multiple (both bases) and the FY27 revenue / EBITDA / nights each
                                      target needs at 13.5 / 16.5 / 18.5x
  D_tape_percentiles.csv              p25 / median / mean / p75 / min / max of the tape translated into operating numbers,
                                      plus the seven brief price points
  D_estimate_dispersion.csv           Zacks FY27 revenue and EPS low / mean / high mapped to nights and EBITDA
  D_analyst_own_multiples.csv         Truist, Bernstein, Raymond James at their own published multiples / assumptions
  D_feed_chain_breaks.csv             every target action with the feed's previous target for the firm and a chain-break flag (audit finding 3)
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = os.path.join(ROOT, "data", "processed", "reverse_dcf", "D")
OV = os.path.join(ROOT, "data", "processed", "overnight")

# ---------------- anchors (BRIEF) ----------------
PRICE = 170.19
SH_SPOT, NC_SPOT = 597.0, 9593.0           # 2Q26 diluted WA, net cash ex float
SH_FY27, NC_FY27 = 570.7, 10608.664        # 4Q27 diluted, end-FY27 net cash (delivered case)
EB27_DEL, REV27_DEL, MGN_DEL, EPS27_DEL = 5800.957, 16024.742, 0.362, 6.078
REV26_DEL = 14231.303
REV26_ZACKS = 14100.0
NIGHTS26_DEL = 588.164
MULTS = [13.5, 16.5, 18.5]
ADR_G, FX_G, TR_G = 0.03, -0.006, 0.0
# EPS <-> EBITDA map from the three management cases (literal / delivered / ambition): linear fit, JUDGEMENT
_cases = np.array([[5548.792, 5.723], [5800.957, 6.078], [6212.536, 6.681]])
EPS_B, EPS_A = np.polyfit(_cases[:, 0], _cases[:, 1], 1)
print(f"EPS = {EPS_A:.3f} + {EPS_B*1000:.3f} per $bn EBITDA (fit on mgmt cases; delivered check {EPS_A + EPS_B*EB27_DEL:.3f} vs 6.078)")


def nights_from_rev(g_rev):
    """log-additive: (1+rev) = (1+nights)(1+adr)(1+fx)(1+tr)"""
    return (1 + g_rev) / ((1 + ADR_G) * (1 + FX_G) * (1 + TR_G)) - 1


def implied(target, sh=SH_SPOT, nc=NC_SPOT, eb=EB27_DEL):
    return (target * sh - nc) / eb


def required(target, mult, sh=SH_SPOT, nc=NC_SPOT):
    ev = target * sh - nc
    eb = ev / mult
    rev = eb / MGN_DEL
    g = rev / REV26_DEL - 1
    return dict(ev_musd=ev, ebitda_musd=eb, revenue_musd=rev, rev_growth_pct=100 * g,
                nights_growth_pct=100 * nights_from_rev(g), eps=EPS_A + EPS_B * eb,
                ebitda_vs_delivered_pct=100 * (eb / EB27_DEL - 1))


# ---------------- tape ----------------
RB = {"Buy": "Buy", "Outperform": "Buy", "Overweight": "Buy", "Positive": "Buy", "Market Outperform": "Buy", "Strong Buy": "Buy",
      "Neutral": "Hold", "Hold": "Hold", "Equal-Weight": "Hold", "Market Perform": "Hold", "Sector Weight": "Hold", "In-Line": "Hold",
      "Perform": "Hold", "Sector Perform": "Hold", "Peer Perform": "Hold",
      "Sell": "Sell", "Underweight": "Sell", "Underperform": "Sell", "Reduce": "Sell"}
acts = pd.read_csv(os.path.join(D, "D_analyst_actions_2026-09-12.csv"), parse_dates=["grade_datetime"])
asof = pd.Timestamp("2026-09-12")
recent = acts[acts.grade_datetime >= asof - pd.Timedelta(days=365)].sort_values("grade_datetime")
last = recent.groupby("Firm").tail(1).copy()
last["rating_bucket"] = last.ToGrade.map(RB).fillna("Other")
live = last[last.currentPriceTarget > 0].copy()
# feed chain-break flag: the stated prior target differs from the feed's own previous target for the firm (audit finding 3)
_t = acts[acts.currentPriceTarget > 0].sort_values("grade_datetime").copy()
_t["prev_feed_target"] = _t.groupby("Firm").currentPriceTarget.shift(1)
_t["chain_break"] = (_t.priorPriceTarget > 0) & _t.prev_feed_target.notna() & (_t.priorPriceTarget != _t.prev_feed_target)
_t["chain_break"].sum()
_cb = _t.groupby("Firm").agg(chain_breaks_total=("chain_break", "sum"),
                             chain_breaks_since_sep2025=("chain_break", lambda x: int(x[_t.loc[x.index, "grade_datetime"] >= "2025-09-01"].sum())))
_last_cb = _t.groupby("Firm").tail(1).set_index("Firm")[["chain_break", "prev_feed_target"]].rename(columns={"chain_break": "last_action_chain_break"})
live = live.merge(_cb, left_on="Firm", right_index=True, how="left").merge(_last_cb, left_on="Firm", right_index=True, how="left")
_t[["grade_datetime", "Firm", "ToGrade", "priorPriceTarget", "prev_feed_target", "currentPriceTarget", "chain_break"]].to_csv(os.path.join(D, "D_feed_chain_breaks.csv"), index=False)
print(f"feed chain breaks: {int(_t.chain_break.sum())} of {len(_t)} target actions; since Sep 2025 on live-tape firms: "
      f"{int(_t[(_t.grade_datetime >= '2025-09-01') & _t.Firm.isin(live.Firm) & _t.chain_break].shape[0])}")
old = pd.read_csv(os.path.join(OV, "12_analyst_targets.csv"))
old = old[old.target > 0][["Firm", "target", "date"]].rename(columns={"target": "target_0906", "date": "date_0906"})
live = live.merge(old, on="Firm", how="left")
live = live.rename(columns={"currentPriceTarget": "target", "priorPriceTarget": "prior_target"})
live["date"] = live.grade_datetime.dt.date.astype(str)
live["changed_since_0906"] = np.where(live.target_0906.isna(), "new firm", np.where(live.target != live.target_0906, "changed", ""))
live = live.sort_values("target", ascending=False)
# Goldman correction (JUDGEMENT, documented): feed shows Sell $155 (20 Jul 2026) but MarketScreener/MT Newswires shows
# Neutral $155 from $157 on 20 Jul 2026 and $165 from $155 on 7 Aug 2026; feed itself carries the 14 Feb 2025 Sell->Neutral upgrade.
live["target_corrected"] = np.where(live.Firm == "Goldman Sachs", 165.0, live.target)
live["rating_corrected"] = np.where(live.Firm == "Goldman Sachs", "Hold", live.rating_bucket)
live["correction_note"] = np.where(
    live.Firm == "Goldman Sachs",
    "feed label Sell/$155 contradicted by MarketScreener (MT Newswires) 20 Jul 2026 Neutral $155 from $157 and 7 Aug 2026 $165 from $155 (7 Aug headline carries no rating; Neutral by continuity); "
    "feed also omits the 8 May 2026 $157 from $150 raise (Investing.com); feed's own 14 Feb 2025 row is an upgrade to Neutral", "")
cols = ["Firm", "date", "ToGrade", "rating_bucket", "Action", "priceTargetAction", "target", "prior_target", "target_0906", "date_0906",
        "changed_since_0906", "target_corrected", "rating_corrected", "correction_note", "last_action_chain_break", "prev_feed_target",
        "chain_breaks_total", "chain_breaks_since_sep2025", "source"]
live[cols].to_csv(os.path.join(D, "D_live_targets_2026-09-12.csv"), index=False)
print(f"live targets 12 Sep: {len(live)} (6 Sep file: {len(old)}); firms with a rating but no target: {len(last) - len(live)}")
print(live[["Firm", "date", "ToGrade", "target", "target_0906", "changed_since_0906"]].to_string())
print("rating mix (12 Sep, firms with an action in 365d):", last.rating_bucket.value_counts().to_dict())

# ---------------- per-target implied ----------------
rows = []
for _, r in live.iterrows():
    t = r.target
    d = dict(Firm=r.Firm, date=r.date, rating=r.ToGrade, rating_bucket=r.rating_bucket, target=t,
             upside_vs_170_19_pct=100 * (t / PRICE - 1),
             implied_ev_fy27_ebitda_spot_basis_x=implied(t),
             implied_ev_fy27_ebitda_fy27_basis_x=implied(t, SH_FY27, NC_FY27),
             implied_pe_fy27_delivered_x=t / EPS27_DEL)
    for m in MULTS:
        q = required(t, m)
        d[f"req_fy27_ebitda_musd_at_{m}x"] = q["ebitda_musd"]
        d[f"req_fy27_revenue_musd_at_{m}x"] = q["revenue_musd"]
        d[f"req_fy27_rev_growth_pct_at_{m}x"] = q["rev_growth_pct"]
        d[f"req_fy27_nights_growth_pct_at_{m}x"] = q["nights_growth_pct"]
        d[f"req_fy27_eps_at_{m}x"] = q["eps"]
        d[f"req_ebitda_vs_delivered_pct_at_{m}x"] = q["ebitda_vs_delivered_pct"]
    rows.append(d)
TI = pd.DataFrame(rows)
TI.to_csv(os.path.join(D, "D_target_implied.csv"), index=False)


# ---------------- percentiles ----------------
def row_for(label, stat, v, n=np.nan):
    q = required(v, 16.5)
    return dict(tape=label, n=n, stat=stat, target=v, upside_vs_170_19_pct=100 * (v / PRICE - 1),
                implied_ev_fy27_ebitda_spot_x=implied(v), implied_ev_fy27_ebitda_fy27_basis_x=implied(v, SH_FY27, NC_FY27),
                implied_pe_fy27_delivered_x=v / EPS27_DEL,
                req_fy27_ebitda_musd_at_16_5x=q["ebitda_musd"], req_fy27_revenue_musd_at_16_5x=q["revenue_musd"],
                req_fy27_rev_growth_pct_at_16_5x=q["rev_growth_pct"], req_fy27_nights_growth_pct_at_16_5x=q["nights_growth_pct"],
                req_fy27_eps_at_16_5x=q["eps"], req_ebitda_vs_delivered_pct_at_16_5x=q["ebitda_vs_delivered_pct"],
                req_fy27_ebitda_musd_at_13_5x=required(v, 13.5)["ebitda_musd"], req_fy27_ebitda_musd_at_18_5x=required(v, 18.5)["ebitda_musd"],
                req_fy27_nights_growth_pct_at_13_5x=required(v, 13.5)["nights_growth_pct"],
                req_fy27_nights_growth_pct_at_18_5x=required(v, 18.5)["nights_growth_pct"])


def pct_table(targets, label):
    s = pd.Series(targets, dtype=float)
    stats = {"min": s.min(), "p25": s.quantile(0.25), "median": s.median(), "mean": s.mean(), "p75": s.quantile(0.75), "max": s.max(),
             "sd": s.std()}
    out = [row_for(label, k, v, len(s)) for k, v in stats.items() if k != "sd"]
    out.append(dict(tape=label, n=len(s), stat="sd / mean", target=s.std() / s.mean()))
    out.append(dict(tape=label, n=len(s), stat="share below $170.19", target=100 * (s < PRICE).mean()))
    return pd.DataFrame(out)


P = pd.concat([pct_table(old.target_0906, "6 Sep pull (31 targets)"),
               pct_table(live.target, "12 Sep pull (feed as-is)"),
               pct_table(live.target_corrected, "12 Sep pull (Goldman corrected to $165)")])
bp = [row_for("brief price points", lab, v) for lab, v in
      [("$150 bear tape", 150.0), ("$165 p25 target (brief)", 165.0), ("$170.19 price", PRICE), ("$179.5 mean target (brief)", 179.5),
       ("$185 median yfinance", 185.0), ("$197.5 p75 target (brief)", 197.5), ("$220 top target", 220.0)]]
P = pd.concat([P, pd.DataFrame(bp)])
P.to_csv(os.path.join(D, "D_tape_percentiles.csv"), index=False)
print(P[["tape", "stat", "target", "implied_ev_fy27_ebitda_spot_x", "req_fy27_revenue_musd_at_16_5x", "req_fy27_rev_growth_pct_at_16_5x",
         "req_fy27_ebitda_musd_at_16_5x", "req_fy27_nights_growth_pct_at_16_5x", "req_fy27_eps_at_16_5x"]].round(2).to_string())

# ---------------- estimate dispersion (Zacks 4 Sep 2026, 13 estimates) ----------------
disp = []
for k, rev in [("low", 14990.0), ("consensus", 15730.0), ("high", 16290.0)]:
    for base_lab, base in [("Zacks FY26 consensus $14,100m", REV26_ZACKS), ("mgmt delivered FY26 $14,231m", REV26_DEL)]:
        g = rev / base - 1
        disp.append(dict(metric="FY27 revenue (Zacks, 13 est.)", estimate=k, value=rev, base=base_lab, fy27_growth_pct=100 * g,
                         implied_nights_growth_pct=100 * nights_from_rev(g),
                         implied_fy27_nights_m=NIGHTS26_DEL * (1 + nights_from_rev(g)),
                         implied_ebitda_at_36_2_pct_musd=rev * MGN_DEL,
                         implied_price_at_16_5x_spot_basis=(16.5 * rev * MGN_DEL + NC_SPOT) / SH_SPOT,
                         decomposition="ADR +3.0%, FX -0.6pp, take rate flat, log-additive (JUDGEMENT: task-set assumptions, not in the brief)"))
for k, eps in [("low", 5.35), ("consensus", 6.02), ("high", 6.80)]:
    eb = (eps - EPS_A) / EPS_B
    disp.append(dict(metric="FY27 EPS adj (Zacks, 13 est.)", estimate=k, value=eps, base="mgmt-case EPS to EBITDA map", fy27_growth_pct=np.nan,
                     implied_nights_growth_pct=100 * nights_from_rev(eb / MGN_DEL / REV26_DEL - 1),
                     implied_fy27_nights_m=np.nan, implied_ebitda_at_36_2_pct_musd=eb,
                     implied_price_at_16_5x_spot_basis=(16.5 * eb + NC_SPOT) / SH_SPOT,
                     decomposition=f"EBITDA = (EPS - {EPS_A:.3f}) / {EPS_B:.6f}; revenue = EBITDA / 36.2% "
                                   "(JUDGEMENT: margin held at 36.2%, the split between margin and growth is not identified from EPS alone; decomposition terms task-set)"))
DI = pd.DataFrame(disp)
DI.to_csv(os.path.join(D, "D_estimate_dispersion.csv"), index=False)
print(DI.round(2).to_string())

# ---------------- analysts' own multiples / estimates where published ----------------
own = []
for t, lab in [(134.0, "Truist $134 (12 Jun 2026)"), (161.0, "Truist $161 (10 Sep 2026)")]:
    own.append(dict(firm_target=lab,
                    published_item="2027E adj EBITDA $5.37bn, EPS $5.96, 20x 2027E EBITDA blended (26 Mar 2026 note, via research/notes/2026-09-04_abnb-pitch-landscape.md)",
                    implied_ev_fy27_ebitda_on_own_estimate_spot_x=(t * SH_SPOT - NC_SPOT) / 5370.0,
                    implied_ev_fy27_ebitda_on_delivered_x=implied(t),
                    implied_pe_on_own_eps_x=t / 5.96,
                    ebitda_required_at_own_multiple_musd=(t * SH_SPOT - NC_SPOT) / 20.0,
                    note="Truist's March 2027E EBITDA is 7.4% below management delivered; at our EV basis its stated 20x does not reproduce "
                         "either target, so its blended multiple is on another EV or share basis (not reconstructable from public reporting); "
                         "the 10 Sep raise to $161 carried no published reasoning (TheFly via TipRanks)"))
own.append(dict(firm_target="Bernstein $217 (24 Aug 2026)",
                published_item="25.5x core earnings (a P/E), 12% annual revenue growth, ~20% EPS growth, market prices 10.5-11% medium-term growth (TipRanks 24 Aug 2026)",
                implied_ev_fy27_ebitda_on_own_estimate_spot_x=np.nan,
                implied_ev_fy27_ebitda_on_delivered_x=implied(217.0),
                implied_pe_on_own_eps_x=25.5,
                ebitda_required_at_own_multiple_musd=np.nan,
                note=f"25.5x is a P/E: $217 / 25.5 = ${217/25.5:.2f} of core EPS, {100*(217/25.5/EPS27_DEL-1):.0f}% above management delivered FY27 EPS $6.08 "
                     f"and {100*(217/25.5/6.681-1):.0f}% above the ambition case $6.68, so Bernstein carries out-year and/or ex-SBC earnings well above "
                     f"management's FY27 case (audit finding 4); its 12% revenue growth on FY26 delivered = ${REV26_DEL*1.12:,.0f}m FY27 revenue = "
                     f"nights +{100*nights_from_rev(0.12):.1f}% on the decomposition (JUDGEMENT terms), consensus-like"))
own.append(dict(firm_target="Raymond James $200 (8 Sep 2026)",
                published_item="low-double-digit night growth with a bull case pointing to low-teens (Investing.com 8 Sep 2026)",
                implied_ev_fy27_ebitda_on_own_estimate_spot_x=np.nan, implied_ev_fy27_ebitda_on_delivered_x=implied(200.0),
                implied_pe_on_own_eps_x=np.nan, ebitda_required_at_own_multiple_musd=np.nan,
                note=f"nights +10% to +12% => revenue +{100*((1.10)*(1.03)*(0.994)-1):.1f}% to +{100*((1.12)*(1.03)*(0.994)-1):.1f}% on the decomposition "
                     f"(JUDGEMENT terms) = FY27 revenue ${REV26_DEL*1.10*1.03*0.994:,.0f}m to ${REV26_DEL*1.12*1.03*0.994:,.0f}m, worth "
                     f"${(16.5*REV26_DEL*1.10*1.03*0.994*MGN_DEL+NC_SPOT)/SH_SPOT:.1f} to ${(16.5*REV26_DEL*1.12*1.03*0.994*MGN_DEL+NC_SPOT)/SH_SPOT:.1f} "
                     f"at 16.5x and 36.2%; the $200 target at 16.5x needs revenue +{required(200,16.5)['rev_growth_pct']:.1f}%, so the target needs a multiple "
                     "above 16.5x or margin above 36.2% even on its own bull nights"))
pd.DataFrame(own).to_csv(os.path.join(D, "D_analyst_own_multiples.csv"), index=False)
print(pd.DataFrame(own).round(2).to_string())
