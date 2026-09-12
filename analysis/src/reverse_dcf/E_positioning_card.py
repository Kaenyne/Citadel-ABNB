"""Workstream E: is the market positioned for an accelerating 3Q26 and a strong 4Q26 guide?

Krish with Claude Code, 13 Sep 2026.  py -3.13 analysis/src/reverse_dcf/E_positioning_card.py
Outputs data/processed/reverse_dcf/E/.

Three pieces of evidence, each a table:
  1. STREET SIGN HISTORY.  At every print with a nights consensus (16_consensus_at_print_merged.csv), the Street's
     nights bar implies a growth rate; compare it with the just-printed rate to get the sign the Street was positioned
     for; compare with what printed and the day-1 excess return.  Today: 148.9m = +11.45% vs 2Q26's +10.34%.
  2. PRICE-IMPLIED 2H26 PATH.  The joint solve gives the NTM revenue the price pays for; scale the team's own bridge
     (30_quarterly_pnl.csv base) by a uniform nights uplift until NTM revenue matches, and read off the implied 3Q26
     nights growth and 4Q26 revenue guide.  Done in guide-proxy units and realised units.
  3. REPRICING LADDER.  Two 5 Nov outcomes (team path; Street path): the fundamental repricing through the joint solve
     (NTM growth change -> multiple and EBITDA), plus the sign-rule reaction (C), against the options-implied sd (B).
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("data", "processed", "reverse_dcf", "E"); os.makedirs(OUT, exist_ok=True)
prm = json.load(open(P("data", "processed", "reverse_dcf", "market", "market_implied_params.json")))
PRICE, SHARES, NET_CASH, LTM_REV, LTM_M = prm["price"], prm["shares"], prm["net_cash"], prm["ltm_rev"], prm["ltm_margin"]
A_, B_, SPREAD = prm["reg_a"], prm["reg_b"], prm["spread"]
PROXY_BIAS = 1.37   # A: the guide proxy overstates realised NTM growth by 1.37pp on average

# ---------------------------------------------------------------- 1. Street sign history
c = pd.read_csv(P("data", "processed", "overnight", "16_consensus_at_print_merged.csv"))
k = pd.read_csv(P("data", "processed", "overnight", "02_kpi_panel_quarterly.csv"))[["quarter", "nights_m", "nights_yoy_pct"]]
def q_to_label(q):  # 2026Q2 -> 2Q26
    y, n = q.split("Q"); return f"{n}Q{y[2:]}"
k["py"] = k.nights_m.shift(4); k["prev_growth"] = k.nights_yoy_pct.shift(1)
k = k.set_index("quarter")
rows = []
for _, r in c.iterrows():
    if pd.isna(r.cons_nights_m):
        continue
    q = q_to_label(r.print_quarter)
    if q not in k.index or pd.isna(k.loc[q, "py"]):
        continue
    py, prev = k.loc[q, "py"], k.loc[q, "prev_growth"]
    street_g = (r.cons_nights_m / py - 1) * 100
    actual_g = k.loc[q, "nights_yoy_pct"]
    rows.append(dict(print=q, print_date=r.print_date, prior_quarter_growth_pct=prev, street_nights_m=r.cons_nights_m, street_implied_growth_pct=street_g,
                     street_positioned_for=("acceleration" if street_g > prev + 0.25 else ("deceleration" if street_g < prev - 0.25 else "flat")),
                     street_accel_pts=street_g - prev, actual_growth_pct=actual_g, actual_accel_pts=actual_g - prev,
                     printed=("acceleration" if actual_g > prev + 0.25 else ("deceleration" if actual_g < prev - 0.25 else "flat")),
                     nights_vs_street_pct=r.nights_surprise_pct, day1_excess_pct=r.excess_1d_pct))
hist = pd.DataFrame(rows)
# today
today = dict(print="3Q26E", print_date="2026-11-05", prior_quarter_growth_pct=10.34, street_nights_m=148.9, street_implied_growth_pct=(148.9 / 133.6 - 1) * 100)
today["street_accel_pts"] = today["street_implied_growth_pct"] - 10.34; today["street_positioned_for"] = "acceleration"
q4 = dict(print="4Q26E (guide read on 5 Nov)", print_date="2027-02", prior_quarter_growth_pct=11.45, street_nights_m=134.2, street_implied_growth_pct=(134.2 / 121.9 - 1) * 100)
q4["street_accel_pts"] = q4["street_implied_growth_pct"] - 11.45; q4["street_positioned_for"] = "deceleration vs its own 3Q26E bar; acceleration vs 4Q25's 9.82%"
hist_out = pd.concat([hist, pd.DataFrame([today]), pd.DataFrame([q4])], ignore_index=True)
hist_out.round(3).to_csv(os.path.join(OUT, "E_street_sign_history.csv"), index=False)
summ = (hist.groupby("street_positioned_for").agg(n=("print", "size"), printed_accel=("printed", lambda s: (s == "acceleration").sum()),
        printed_decel=("printed", lambda s: (s == "deceleration").sum()), mean_day1_excess=("day1_excess_pct", "mean"), mean_nights_vs_street=("nights_vs_street_pct", "mean")).reset_index())
summ.round(2).to_csv(os.path.join(OUT, "E_street_sign_summary.csv"), index=False)

# ---------------------------------------------------------------- 2. price-implied 2H26 path on the team's bridge
q = pd.read_csv(P("data", "processed", "overnight", "30_quarterly_pnl.csv")); q = q[q.scenario == "base"].set_index("quarter")
ntm_q = ["3Q26", "4Q26", "1Q27", "2Q27"]
base = q.loc[ntm_q, ["revenue_musd", "nights_m", "nights_yoy", "adr_exfx", "fx_pp", "resid_pp", "rev_yoy"]].copy()
py_rev = {"3Q26": 4095.0, "4Q26": 2778.0, "1Q27": 2678.0, "2Q27": 3608.0}
def ntm_rev(delta):
    tot = 0.0
    for qq in ntm_q:
        n = base.loc[qq, "nights_yoy"] + delta
        tot += py_rev[qq] * (1 + n / 100) * (1 + base.loc[qq, "adr_exfx"] / 100) * (1 + (base.loc[qq, "fx_pp"] + base.loc[qq, "resid_pp"]) / 100)
    return tot
def solve_delta(target):
    lo, hi = -15.0, 15.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if ntm_rev(mid) < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2
def quad(a, b, ev, base_rev, m):
    c2 = b / 100; c1 = a / 100 + b; c0 = a - ev / (base_rev * m)
    return (-c1 + np.sqrt(c1 * c1 - 4 * c2 * c0)) / (2 * c2)
ev = PRICE * SHARES - NET_CASH
g_proxy = quad(A_, B_, ev, LTM_REV, LTM_M); g_real = g_proxy - PROXY_BIAS
street_ntm = 4744.0 + 3177.0 + (15745.0 * (6286.0 / 14231.3))   # Street 2H26 + 1H27 at the Street FY27 x the H1 share
deliv_ntm = 4815.14 + 3130.163 + 3003.832 + 4055.161
team_ntm = ntm_rev(0.0)
paths = []
for label, target in [("price-implied, guide-proxy units", LTM_REV * (1 + g_proxy / 100)), ("price-implied, realised units (proxy bias 1.37pp removed)", LTM_REV * (1 + g_real / 100)),
                      ("Street (Bloomberg 3Q26 + 4Q26 midpoint + 1H27 at Street FY27)", street_ntm), ("management delivered", deliv_ntm), ("team base (WS29/30)", team_ntm)]:
    d = solve_delta(target)
    paths.append(dict(path=label, ntm_revenue_musd=target, ntm_growth_pct=(target / LTM_REV - 1) * 100, uniform_nights_uplift_vs_team_pts=d,
                      implied_3q26_nights_growth_pct=base.loc["3Q26", "nights_yoy"] + d, implied_3q26_nights_m=133.6 * (1 + (base.loc["3Q26", "nights_yoy"] + d) / 100),
                      implied_3q26_sign_vs_2q26=("acceleration" if base.loc["3Q26", "nights_yoy"] + d > 10.34 + 0.25 else ("deceleration" if base.loc["3Q26", "nights_yoy"] + d < 10.34 - 0.25 else "flat")),
                      implied_4q26_nights_growth_pct=base.loc["4Q26", "nights_yoy"] + d,
                      implied_4q26_revenue_musd=py_rev["4Q26"] * (1 + (base.loc["4Q26", "nights_yoy"] + d) / 100) * (1 + base.loc["4Q26", "adr_exfx"] / 100) * (1 + (base.loc["4Q26", "fx_pp"] + base.loc["4Q26", "resid_pp"]) / 100),
                      implied_1h27_nights_growth_pct=(base.loc["1Q27", "nights_yoy"] + base.loc["2Q27", "nights_yoy"]) / 2 + d))
paths = pd.DataFrame(paths); paths.round(3).to_csv(os.path.join(OUT, "E_price_implied_2h26_path.csv"), index=False)

# ---------------------------------------------------------------- 3. repricing ladder for 5 Nov
C = pd.read_csv(P("data", "processed", "reverse_dcf", "C", "C_coefficients_used.csv")).set_index("spec_id")
S1 = C.loc["S1_post2022"]; S1b = C.loc["S1_ex_reopening"]
EVENT_SD = prm["event_sd"]
def price_from_ntm(g):
    return ((A_ + B_ * g) * LTM_REV * (1 + g / 100) * LTM_M + NET_CASH) / SHARES
ladder = []
for label, ntm, sign in [("Street path prints (3Q26 +11.45%, 4Q26 guide at Street): market re-anchors to Street NTM", street_ntm, 1),
                         ("Management delivered prints (3Q26 +11.5%, 4Q26 $3,130m)", deliv_ntm, 1),
                         ("Team base prints (3Q26 +10.3% on the pnl bridge / +9.9% baseline, 4Q26 $3,111m)", team_ntm, -1),
                         ("Team base, 3Q26 nights 9.9% and 4Q26 8.1% (ex-NA lap)", None, -1)]:
    if ntm is None:
        d = 9.9 - base.loc["3Q26", "nights_yoy"]; ntm = ntm_rev(d) - py_rev["4Q26"] * 0  # approximate: uniform shift to 9.9 in 3Q26
    g_new = (ntm / LTM_REV - 1) * 100                # the market re-anchors NTM growth to the path's number, same units as it prices today
    p_fund = price_from_ntm(g_new)
    r_fund = (p_fund / PRICE - 1) * 100
    p_fund_realised = price_from_ntm(g_new + PROXY_BIAS)   # alternative: path is realised growth, line is in proxy units (+1.37pp)
    r_sign14 = float(S1.c + S1.b_sign * sign); r_sign16 = float(S1b.c + S1b.b_sign * sign)
    ladder.append(dict(outcome=label, ntm_revenue_musd=ntm, ntm_growth_pct=(ntm / LTM_REV - 1) * 100, joint_solve_price_usd=p_fund, fundamental_repricing_pct=r_fund,
                       joint_solve_price_if_path_is_realised_units_usd=p_fund_realised,
                       sign_rule_reaction_post2022_pct=r_sign14, sign_rule_reaction_n16_pct=r_sign16,
                       combined_low_pct=min(r_fund, 0) + min(r_sign14, r_sign16) if sign < 0 else max(r_fund, 0) + min(r_sign14, r_sign16),
                       combined_high_pct=min(r_fund, 0) + max(r_sign14, r_sign16) if sign < 0 else max(r_fund, 0) + max(r_sign14, r_sign16),
                       options_event_sd_pct=EVENT_SD))
ladder = pd.DataFrame(ladder); ladder.round(3).to_csv(os.path.join(OUT, "E_repricing_ladder.csv"), index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(hist_out.round(2).to_string()); print(); print(summ.round(2).to_string()); print()
print(paths.round(2).to_string()); print(); print(ladder.round(2).to_string())
