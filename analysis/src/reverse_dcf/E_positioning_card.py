"""Workstream E: is the market positioned for an accelerating 3Q26 and a strong 4Q26 guide?

Krish with Claude Code, 13 Sep 2026; rebuilt after audit_E (pass with fixes).  py -3.13 analysis/src/reverse_dcf/E_positioning_card.py
Outputs data/processed/reverse_dcf/E/.

Three pieces of evidence, each a table:
  1. STREET SIGN HISTORY.  At every print with a nights consensus (16_consensus_at_print_merged.csv) the Street's bar
     implies a growth rate; compare it with the just-printed rate (0.25pt dead band) to get the sign the Street was
     positioned for, compare with what printed and the day-1 excess return, and compare with the direction of
     management's own next-quarter nights guide (02_guidance_ledger.csv).  Prints without a comparator are excluded.
  2. PRICE-IMPLIED 2H26 PATH.  The joint solve gives the NTM revenue the price pays for; shift the team's own bridge by
     a uniform nights uplift until NTM revenue matches, using the bridge's own ADDITIVE convention
     (rev y/y = nights + ADR ex-FX + FX + residual, as in 30_quarterly_pnl.csv), on two team baselines: the WS30 pnl
     bridge (3Q26 10.29 / 4Q26 9.94) and the 10 Sep pivot baseline (9.9 / 8.9).  Guide-proxy and realised units.
  3. REPRICING LADDER.  5 Nov outcomes: the fundamental repricing through the joint solve (NTM growth re-anchored to the
     printed path) shown BESIDE the sign-rule reaction (C), not summed: the sign rule is a total day-1 return that
     already contains whatever estimate effect there was.  Ex-NA lap row built one-for-one on 4Q26 (8.1%) with 1H27
     unchanged, and a variant with 1H27 also lapped.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("data", "processed", "reverse_dcf", "E"); os.makedirs(OUT, exist_ok=True)
prm = json.load(open(P("data", "processed", "reverse_dcf", "market", "market_implied_params.json")))
PRICE, SHARES, NET_CASH, LTM_REV, LTM_M = prm["price"], prm["shares"], prm["net_cash"], prm["ltm_rev"], prm["ltm_margin"]
A_, B_ = prm["reg_a"], prm["reg_b"]
PROXY_BIAS = 1.37   # A: the guide proxy overstates realised NTM growth by 1.37pp on average (unstable; sign flipped in 2025)
DB = 0.25           # dead band, pts

# ---------------------------------------------------------------- 1. Street sign history
c = pd.read_csv(P("data", "processed", "overnight", "16_consensus_at_print_merged.csv"))
k = pd.read_csv(P("data", "processed", "overnight", "02_kpi_panel_quarterly.csv"))[["quarter", "nights_m", "nights_yoy_pct"]]
g = pd.read_csv(P("data", "processed", "overnight", "02_guidance_ledger.csv"))
def q_to_label(q):
    y, n = q.split("Q"); return f"{n}Q{y[2:]}"
k["py"] = k.nights_m.shift(4); k["prev_growth"] = k.nights_yoy_pct.shift(1); k = k.set_index("quarter")
def sign(x, ref):
    return "acceleration" if x > ref + DB else ("deceleration" if x < ref - DB else "flat")
# management's next-quarter nights guide direction, from the ledger (directional rows carry direction + comparator; buckets carry a range)
def guide_dir(print_q, printed_rate):
    r = g[(g.print_quarter == print_q) & (g.metric == "nights_yoy_pct") & (g.horizon_quarters == 1)]
    if not len(r):
        return "no guide", np.nan
    r = r.iloc[0]
    if r.guide_type == "bucket":
        mid = (r.value_low + r.value_high) / 2; return sign(mid, printed_rate), mid
    d = str(r.direction)
    if d in ("above",): return "acceleration", np.nan
    if d in ("below", "below_revenue_growth"): return "deceleration", np.nan
    if d in ("stable", "approx"): return "flat", np.nan
    return d, np.nan
rows = []
for _, r in c.iterrows():
    if pd.isna(r.cons_nights_m):
        continue
    q = q_to_label(r.print_quarter)
    if q not in k.index or pd.isna(k.loc[q, "py"]) or pd.isna(k.loc[q, "prev_growth"]):
        continue
    py, prev, actual = k.loc[q, "py"], k.loc[q, "prev_growth"], k.loc[q, "nights_yoy_pct"]
    street_g = (r.cons_nights_m / py - 1) * 100
    gd, gmid = guide_dir(q, prev)   # the guide given at the PRIOR print for this quarter is in the ledger under print_quarter = prior quarter
    # ledger keys guides by the print at which they were given; the guide for quarter q was given at the previous print
    rows.append(dict(print=q, print_date=r.print_date, prior_quarter_growth_pct=prev, street_nights_m=r.cons_nights_m, street_implied_growth_pct=street_g,
                     street_positioned_for=sign(street_g, prev), street_accel_pts=street_g - prev, actual_growth_pct=actual, actual_accel_pts=actual - prev,
                     printed=sign(actual, prev), nights_vs_street_pct=r.nights_surprise_pct, day1_excess_pct=r.excess_1d_pct))
hist = pd.DataFrame(rows)
# guide direction: look up the guide GIVEN at the previous print for this quarter
order = list(k.index)
def prev_print(q):
    i = order.index(q); return order[i - 1] if i > 0 else None
gd_rows = []
for _, r in hist.iterrows():
    pq = prev_print(r["print"])
    d, mid = guide_dir(pq, r.prior_quarter_growth_pct) if pq else ("no guide", np.nan)
    gd_rows.append((d, mid))
hist["mgmt_guide_direction_for_this_quarter"] = [d for d, _ in gd_rows]; hist["mgmt_guide_bucket_mid_pct"] = [m for _, m in gd_rows]
hist["street_sign_matches_guide"] = np.where(hist.mgmt_guide_direction_for_this_quarter == "no guide", np.nan, hist.street_positioned_for == hist.mgmt_guide_direction_for_this_quarter)
hist["guide_downside_miss"] = np.where(hist.mgmt_guide_direction_for_this_quarter == "no guide", np.nan,
                                       (hist.mgmt_guide_direction_for_this_quarter == "acceleration") & (hist.printed != "acceleration")
                                       | (hist.mgmt_guide_direction_for_this_quarter == "flat") & (hist.printed == "deceleration"))
today = dict(print="3Q26E", print_date="2026-11-05", prior_quarter_growth_pct=10.34, street_nights_m=148.9, street_implied_growth_pct=(148.9 / 133.6 - 1) * 100,
             mgmt_guide_direction_for_this_quarter="acceleration (bucket 'low double-digit' 10-12, mid 11.0)", mgmt_guide_bucket_mid_pct=11.0)
today["street_accel_pts"] = today["street_implied_growth_pct"] - 10.34; today["street_positioned_for"] = "acceleration"
q4 = dict(print="4Q26E (guide read on 5 Nov)", print_date="2027-02", prior_quarter_growth_pct=11.45, street_nights_m=134.2, street_implied_growth_pct=(134.2 / 121.9 - 1) * 100,
          mgmt_guide_direction_for_this_quarter="not yet guided")
q4["street_accel_pts"] = q4["street_implied_growth_pct"] - 11.45; q4["street_positioned_for"] = "deceleration vs its own 3Q26E bar; acceleration vs 4Q25's 9.82%"
hist_out = pd.concat([hist, pd.DataFrame([today]), pd.DataFrame([q4])], ignore_index=True)
hist_out.round(3).to_csv(os.path.join(OUT, "E_street_sign_history.csv"), index=False)
summ = (hist.groupby("street_positioned_for").agg(n=("print", "size"), printed_accel=("printed", lambda s: (s == "acceleration").sum()),
        printed_decel=("printed", lambda s: (s == "deceleration").sum()), mean_day1_excess=("day1_excess_pct", "mean"), mean_nights_vs_street=("nights_vs_street_pct", "mean")).reset_index())
summ.round(2).to_csv(os.path.join(OUT, "E_street_sign_summary.csv"), index=False)
guided = hist[hist.mgmt_guide_direction_for_this_quarter != "no guide"]
guide_stats = dict(prints_with_guide=len(guided), street_sign_matches_guide=int(guided.street_sign_matches_guide.astype(bool).sum()),
                   guide_downside_misses=int(guided.guide_downside_miss.astype(bool).sum()),
                   accelerating_guides=int((guided.mgmt_guide_direction_for_this_quarter == "acceleration").sum()),
                   accelerating_guides_met=int(((guided.mgmt_guide_direction_for_this_quarter == "acceleration") & (guided.printed == "acceleration")).sum()))
pd.DataFrame([guide_stats]).to_csv(os.path.join(OUT, "E_guide_vs_street_sign.csv"), index=False)

# ---------------------------------------------------------------- 2. price-implied 2H26 path (additive bridge convention)
q = pd.read_csv(P("data", "processed", "overnight", "30_quarterly_pnl.csv")); q = q[q.scenario == "base"].set_index("quarter")
ntm_q = ["3Q26", "4Q26", "1Q27", "2Q27"]
py_rev = {"3Q26": 4095.0, "4Q26": 2778.0, "1Q27": 2678.0, "2Q27": 3608.0}
BASES = {
    "WS30 pnl bridge (3Q26 10.29 / 4Q26 9.94 / 1H27 7.95, 8.45)": {qq: dict(n=q.loc[qq, "nights_yoy"], other=q.loc[qq, "adr_exfx"] + q.loc[qq, "fx_pp"] + q.loc[qq, "resid_pp"]) for qq in ntm_q},
    "10 Sep pivot baseline (3Q26 9.9 / 4Q26 8.9 / 1H27 as pnl)": {"3Q26": dict(n=9.9, other=q.loc["3Q26", "adr_exfx"] + q.loc["3Q26", "fx_pp"] + q.loc["3Q26", "resid_pp"]),
                                                                    "4Q26": dict(n=8.9, other=q.loc["4Q26", "adr_exfx"] + q.loc["4Q26", "fx_pp"] + q.loc["4Q26", "resid_pp"]),
                                                                    "1Q27": dict(n=q.loc["1Q27", "nights_yoy"], other=q.loc["1Q27", "adr_exfx"] + q.loc["1Q27", "fx_pp"] + q.loc["1Q27", "resid_pp"]),
                                                                    "2Q27": dict(n=q.loc["2Q27", "nights_yoy"], other=q.loc["2Q27", "adr_exfx"] + q.loc["2Q27", "fx_pp"] + q.loc["2Q27", "resid_pp"])},
}
def ntm_rev(base, delta, quarters=ntm_q):
    return sum(py_rev[qq] * (1 + (base[qq]["n"] + (delta if qq in quarters else 0) + base[qq]["other"]) / 100) for qq in ntm_q)
def solve_delta(base, target, quarters=ntm_q):
    lo, hi = -15.0, 15.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if ntm_rev(base, mid, quarters) < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2
def quad(a, b, ev, base_rev, m):
    c2 = b / 100; c1 = a / 100 + b; c0 = a - ev / (base_rev * m)
    return (-c1 + np.sqrt(c1 * c1 - 4 * c2 * c0)) / (2 * c2)
ev = PRICE * SHARES - NET_CASH
g_proxy = quad(A_, B_, ev, LTM_REV, LTM_M); g_real = g_proxy - PROXY_BIAS
ntm_price_proxy, ntm_price_real = LTM_REV * (1 + g_proxy / 100), LTM_REV * (1 + g_real / 100)
street_ntm_deliv_base = 4744.0 + 3177.0 + 15745.0 * (6286.0 / 14231.3)
street_ntm_street_base = 4744.0 + 3177.0 + 15745.0 * (6286.0 / 14130.0)
deliv_ntm = 4815.14 + 3130.163 + 3003.832 + 4055.161
paths = []
for bname, base in BASES.items():
    team_ntm = ntm_rev(base, 0.0)
    for label, target in [("price-implied, guide-proxy units", ntm_price_proxy), ("price-implied, realised units (proxy bias 1.37pp removed; unstable)", ntm_price_real),
                          ("Street: Bloomberg 2H26 + 1H27 at Street FY27 x H1 share on the delivered FY26 base", street_ntm_deliv_base),
                          ("Street: same on the Street's own FY26 base ($14,130m)", street_ntm_street_base),
                          ("management delivered", deliv_ntm), ("team base (this bridge)", team_ntm)]:
        for scope, quarters in [("uniform across the four NTM quarters", ntm_q), ("2H26 only (1H27 held)", ["3Q26", "4Q26"])]:
            d = solve_delta(base, target, quarters)
            n3 = base["3Q26"]["n"] + d; n4 = base["4Q26"]["n"] + d
            paths.append(dict(team_bridge=bname, path=label, uplift_scope=scope, ntm_revenue_musd=target, ntm_growth_pct=(target / LTM_REV - 1) * 100, team_ntm_revenue_musd=team_ntm,
                              gap_vs_team_musd=target - team_ntm, nights_uplift_vs_team_pts=d, implied_3q26_nights_growth_pct=n3, implied_3q26_nights_m=133.6 * (1 + n3 / 100),
                              implied_3q26_sign_vs_2q26=sign(n3, 10.34), gap_to_street_bar_pts=n3 - 11.45, implied_4q26_nights_growth_pct=n4,
                              implied_4q26_revenue_musd=py_rev["4Q26"] * (1 + (n4 + base["4Q26"]["other"]) / 100)))
paths = pd.DataFrame(paths); paths.round(3).to_csv(os.path.join(OUT, "E_price_implied_2h26_path.csv"), index=False)

# ---------------------------------------------------------------- 3. repricing ladder (fundamental beside sign rule, not summed)
C = pd.read_csv(P("data", "processed", "reverse_dcf", "C", "C_coefficients_used.csv")).set_index("spec_id")
S1, S1b = C.loc["S1_post2022"], C.loc["S1_ex_reopening"]
EVENT_SD = prm["event_sd"]
def price_from_ntm(gg):
    return ((A_ + B_ * gg) * LTM_REV * (1 + gg / 100) * LTM_M + NET_CASH) / SHARES
pnl = BASES["WS30 pnl bridge (3Q26 10.29 / 4Q26 9.94 / 1H27 7.95, 8.45)"]; piv = BASES["10 Sep pivot baseline (3Q26 9.9 / 4Q26 8.9 / 1H27 as pnl)"]
def path_ntm(base, overrides):
    b = {qq: dict(base[qq]) for qq in ntm_q}
    for qq, n in overrides.items(): b[qq]["n"] = n
    return ntm_rev(b, 0.0)
ladder_in = [
    ("Street path prints (3Q26 +11.45%, 4Q26 at Street $3,177m; 1H27 at Street FY27, delivered FY26 base)", street_ntm_deliv_base, 1),
    ("Street path, 1H27 on the Street's own FY26 base", street_ntm_street_base, 1),
    ("Management delivered prints (3Q26 +11.5%, 4Q26 $3,130m)", deliv_ntm, 1),
    ("Team pnl bridge prints (3Q26 +10.3%, 4Q26 +9.9%, revenue $4,771m / $3,111m)", path_ntm(pnl, {}), -1),
    ("Team pivot baseline prints (3Q26 +9.9%, 4Q26 +8.9%, 1H27 as pnl)", path_ntm(piv, {}), -1),
    ("Team pivot baseline with the ex-NA lap: 4Q26 +8.1% one-for-one, 1H27 unchanged", path_ntm(piv, {"4Q26": 8.1}), -1),
    ("Team pivot baseline with the ex-NA lap also hitting 1H27 by 0.8pt", path_ntm(piv, {"4Q26": 8.1, "1Q27": piv["1Q27"]["n"] - 0.8, "2Q27": piv["2Q27"]["n"] - 0.8}), -1),
]
ladder = []
for label, ntm, sg in ladder_in:
    g_new = (ntm / LTM_REV - 1) * 100
    p_fund = price_from_ntm(g_new); p_fund_real = price_from_ntm(g_new + PROXY_BIAS)
    ladder.append(dict(outcome=label, ntm_revenue_musd=ntm, ntm_growth_pct=g_new, joint_solve_price_usd=p_fund, fundamental_repricing_pct=(p_fund / PRICE - 1) * 100,
                       joint_solve_price_if_path_is_realised_units_usd=p_fund_real, fundamental_repricing_realised_units_pct=(p_fund_real / PRICE - 1) * 100,
                       accel_sign=sg, sign_rule_reaction_post2022_pct=float(S1.c + S1.b_sign * sg), sign_rule_reaction_n16_pct=float(S1b.c + S1b.b_sign * sg),
                       note="sign rule is a total day-1 excess return (already contains any estimate effect); do not add to the fundamental column",
                       options_event_sd_pct=EVENT_SD))
ladder = pd.DataFrame(ladder); ladder.round(3).to_csv(os.path.join(OUT, "E_repricing_ladder.csv"), index=False)

# ---------------------------------------------------------------- 4. Street estimate DISTRIBUTION vs the team (Bloomberg MODL / EEG, 12 Sep 2026)
# Values read from Krish's Bloomberg MODL screenshots (12 Sep 2026); n = number of estimates; team values from docs/q3nowcast/SYNTHESIS.md,
# research/notes/adrv3 card v3 and the WS29 bridge.  ANCHOR: 3Q25 nights 133.6m, GBV $22,892m, ADR $171.29; 4Q25 nights 121.9m, GBV $20,400m, ADR $167.51.
MODL = [
    # quarter, metric, low, mean, high, n, prior-year actual, team value, team source
    ("3Q26", "nights_m", 147.0, 149.0, 151.0, 28, 133.6, 146.8, "team baseline +9.9% (docs/q3nowcast/SYNTHESIS.md; reviews index 9.5-10.0, band 8.5-11.0)"),
    ("3Q26", "gbv_musd", 25992.0, 26375.0, 26723.0, 28, 22892.0, 25900.0, "team: 146.8m x $176.8 (H note); WS-B FX schedule"),
    ("3Q26", "adr_usd", 173.71, 177.06, 179.12, 26, 171.29, 176.9, "ADR card v3 +3.3% (docs/adrv3); H note +3.2% $176.8"),
    ("3Q26", "take_rate_pct", 17.82, 18.00, 18.44, 28, 17.88, 18.4, "team 3Q26 revenue $4,771m / GBV ~$25.9bn"),
    ("4Q26", "nights_m", 130.0, 134.0, 136.0, 28, 121.9, 132.7, "team baseline +8.9% (8.0-8.2% if the ex-NA lap is adopted: 131.7-131.9m)"),
    ("4Q26", "gbv_musd", 22177.0, 23003.0, 23565.0, 28, 20400.0, 23100.0, "team: 132.7m x $174.1 (ADR card v2/v3 4Q26 +3.8-3.9%)"),
    ("4Q26", "adr_usd", 167.79, 171.33, 174.21, 25, 167.51, 174.1, "ADR card v3 4Q26 +3.8%"),
    ("4Q26", "take_rate_pct", 13.60, 13.76, 14.00, 28, 13.62, 13.5, "team 4Q26 revenue $3,111m / GBV ~$23.1bn"),
    ("4Q26", "revenue_musd", 3052.0, 3157.0, 3223.0, 37, 2778.0, 3111.0, "WS29 bridge base; ex-NA lap $3,055-3,102m"),
    ("4Q26", "eps_usd", 0.67, 0.87, 1.36, 29, 0.56, 0.81, "WS30 base"),
]
mrows = []
for qq, m, lo, mean, hi, n, py, team, src in MODL:
    growth = lambda v: (v / py - 1) * 100 if m not in ("take_rate_pct",) else v - py
    pos = "below the lowest estimate" if team < lo else ("above the highest estimate" if team > hi else "inside the range")
    pct = (team - lo) / (hi - lo) * 100 if hi > lo else np.nan
    mrows.append(dict(quarter=qq, metric=m, n_estimates=n, street_low=lo, street_mean=mean, street_high=hi, prior_year_actual=py,
                      street_low_growth=growth(lo), street_mean_growth=growth(mean), street_high_growth=growth(hi),
                      team_value=team, team_growth=growth(team), team_position=pos, team_position_pct_of_range=pct, team_source=src,
                      source="Bloomberg MODL, Standard Consensus, screenshot 12 Sep 2026 (Krish); values read off the image"))
modl = pd.DataFrame(mrows); modl.round(3).to_csv(os.path.join(OUT, "E_street_distribution_vs_team.csv"), index=False)
# EEG: consensus nights path over time (read off the Earnings Estimates Graph, 12 Sep 2026); pre/post the 6 Aug 2026 print
eeg = pd.DataFrame([
    dict(period="3Q26", date="2026-05 (post 1Q26 print)", cons_nights_m=145.5, note="EEG, read off the image, +/-0.3m"),
    dict(period="3Q26", date="2026-08-05 (pre 2Q26 print)", cons_nights_m=145.4, note="EEG"),
    dict(period="3Q26", date="2026-08-07 (post 2Q26 print)", cons_nights_m=148.5, note="EEG; jump of ~2.1% on the print; 2Q26 printed 148.3m vs a 145.44m bar (+2.0%)"),
    dict(period="3Q26", date="2026-09-12", cons_nights_m=148.96, note="EEG legend value"),
    dict(period="4Q26", date="2026-05 (post 1Q26 print)", cons_nights_m=132.4, note="EEG"),
    dict(period="4Q26", date="2026-08-05 (pre 2Q26 print)", cons_nights_m=132.4, note="EEG"),
    dict(period="4Q26", date="2026-08-07 (post 2Q26 print)", cons_nights_m=133.9, note="EEG; +1.1% on the print"),
    dict(period="4Q26", date="2026-09-12", cons_nights_m=134.22, note="EEG legend value"),
])
eeg["implied_growth_pct"] = np.where(eeg.period == "3Q26", (eeg.cons_nights_m / 133.6 - 1) * 100, (eeg.cons_nights_m / 121.9 - 1) * 100)
eeg.round(3).to_csv(os.path.join(OUT, "E_street_nights_estimate_path.csv"), index=False)
print(); print(modl[["quarter", "metric", "n_estimates", "street_low_growth", "street_mean_growth", "street_high_growth", "team_growth", "team_position"]].round(2).to_string())
print(); print(eeg.round(2).to_string())

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 70)
print(hist_out[["print", "prior_quarter_growth_pct", "street_implied_growth_pct", "street_positioned_for", "printed", "day1_excess_pct", "mgmt_guide_direction_for_this_quarter", "street_sign_matches_guide", "guide_downside_miss"]].round(2).to_string())
print(); print(summ.round(2).to_string()); print(guide_stats); print()
print(paths[["team_bridge", "path", "uplift_scope", "ntm_growth_pct", "gap_vs_team_musd", "nights_uplift_vs_team_pts", "implied_3q26_nights_growth_pct", "implied_3q26_sign_vs_2q26", "gap_to_street_bar_pts", "implied_4q26_revenue_musd"]].round(2).to_string())
print(); print(ladder[["outcome", "ntm_growth_pct", "joint_solve_price_usd", "fundamental_repricing_pct", "fundamental_repricing_realised_units_pct", "sign_rule_reaction_post2022_pct", "sign_rule_reaction_n16_pct"]].round(2).to_string())
