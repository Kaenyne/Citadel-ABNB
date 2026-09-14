"""
Workstream A, step 3: decompose the market-implied revenue growth into nights / ADR ex-FX / FX / take rate, reconcile the
Bloomberg FA quarterly consensus components for 3Q26 / 4Q26, and build the comparison table against the management cases,
the Street and the team base.

Identity (log-additive): ln(1+rev) = ln(1+nights) + ln(1+ADR ex-FX) + ln(1+FX) + ln(1+take-rate change) + residual.
Checked against 1Q23-2Q26 history (02_kpi_panel_quarterly.csv) two ways: the exact reported identity (nights x reported
ADR x reported take rate) and management's decomposition (ADR ex-FX + revenue FX with the take rate flat), whose residual
is the RNPL book-vs-stay timing gap the team calls the take-rate / timing residual.

Run from the repo root:  py -3.13 analysis/src/reverse_dcf/A_03_decomposition_comparison.py   (after A_02)
Outputs under data/processed/reverse_dcf/A/: A_decomposition_history_check.csv, A_quarterly_consensus_decomposition.csv,
A_quarterly_consensus_fy_reconciliation.csv, A_implied_nights.csv, A_implied_nights_sensitivity.csv, A_comparison_table.csv,
A_case_implied_prices.csv, A_headline.csv
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *  # noqa: F401,F403,E402

pd.set_option("display.width", 250)
js = pd.read_csv(os.path.join(OUT, "A_joint_solve.csv"))
hl = pd.read_csv(os.path.join(OUT, "A_simple_holds_long.csv"))
dcf = pd.read_csv(os.path.join(OUT, "A_reverse_dcf.csv"))
PRIMARY = "A. levels 2023-26, growth only (primary)"
# band = fitted-line 1 s.e. band (delta method on the Newey-West covariance, A_02), audit finding 1; the superseded slope-only rows stay in A_joint_solve.csv

# ---- 4a. history check of the identity ---------------------------------------------------------------------------------
k = pd.read_csv(os.path.join(OVN, "02_kpi_panel_quarterly.csv"))
k = k.set_index("quarter")
k["take_rate_yoy_pct"] = (k["take_rate_pct"] / k["take_rate_pct"].shift(4) - 1) * 100
h = k.loc["1Q23":"2Q26", ["nights_yoy_pct", "adr_yoy_pct", "adr_yoy_exfx_pct", "fx_pts_adr", "revenue_yoy_pct", "fx_pts_revenue", "take_rate_pct", "take_rate_yoy_pct", "gbv_yoy_pct", "unearned_fees_yoy_pct"]].copy()
L = lambda x: np.log(1 + x / 100)
# exact identity: revenue = nights x reported ADR x reported take rate
h["exact_identity_residual_pp"] = (L(h["revenue_yoy_pct"]) - L(h["nights_yoy_pct"]) - L(h["adr_yoy_pct"]) - L(h["take_rate_yoy_pct"])) * 100
# management decomposition: nights + ADR ex-FX + revenue FX, take rate flat -> residual = timing / take-rate residual
h["mgmt_decomp_sum_pct"] = (np.exp(L(h["nights_yoy_pct"]) + L(h["adr_yoy_exfx_pct"]) + L(h["fx_pts_revenue"])) - 1) * 100
h["timing_takerate_residual_pp"] = (L(h["revenue_yoy_pct"]) - L(h["nights_yoy_pct"]) - L(h["adr_yoy_exfx_pct"]) - L(h["fx_pts_revenue"])) * 100
h["arithmetic_vs_log_gap_pp"] = (h["nights_yoy_pct"] + h["adr_yoy_exfx_pct"] + h["fx_pts_revenue"]) - h["mgmt_decomp_sum_pct"]
h = h.round(2)
h.to_csv(os.path.join(OUT, "A_decomposition_history_check.csv"))
# annual-level residual (FY24, FY25, 1H26): nights and GBV summed, ADR ex-FX and revenue FX as revenue-weighted averages of the letters' quarterly figures
ann = []
for name, qs in [("FY24", ["1Q24", "2Q24", "3Q24", "4Q24"]), ("FY25", ["1Q25", "2Q25", "3Q25", "4Q25"]), ("1H26", ["1Q26", "2Q26"])]:
    py = [q.replace(q[-2:], str(int(q[-2:]) - 1)) for q in qs]
    rev_g = (k.loc[qs, "revenue_musd"].sum() / k.loc[py, "revenue_musd"].sum() - 1) * 100
    n_g = (k.loc[qs, "nights_m"].sum() / k.loc[py, "nights_m"].sum() - 1) * 100
    w = k.loc[qs, "revenue_musd"] / k.loc[qs, "revenue_musd"].sum()
    adr_x = (k.loc[qs, "adr_yoy_exfx_pct"] * w).sum()
    fx = (k.loc[qs, "fx_pts_revenue"] * w).sum()
    ann.append(dict(period=name, revenue_yoy_pct=round(rev_g, 2), nights_yoy_pct=round(n_g, 2), adr_exfx_rev_weighted_pct=round(adr_x, 2), fx_rev_weighted_pp=round(fx, 2),
                    timing_takerate_residual_pp=round((L(rev_g) - L(n_g) - L(adr_x) - L(fx)) * 100, 2)))
ann = pd.DataFrame(ann)
ann.to_csv(os.path.join(OUT, "A_decomposition_history_check_annual.csv"), index=False)
res = h["timing_takerate_residual_pp"]
res_stats = dict(mean_1q23_2q26=res.mean(), sd=res.std(), trailing_four_mean=res.iloc[-4:].mean(), trailing_eight_mean=res.iloc[-8:].mean(), min=res.min(), max=res.max(),
                 exact_identity_abs_mean=h["exact_identity_residual_pp"].abs().mean())

# ---- 4b. Bloomberg FA quarterly consensus decomposition (ANCHOR: BRIEF) ---------------------------------------------------------------------
ADR_FX_Q3, ADR_FX_Q4 = 0.3, -0.4          # management-model ADR FX points (mgmt_implied_inputs.csv, common to all cases)
REV_FX_Q3, REV_FX_Q4 = 3.0, -0.4          # revenue FX after hedging: 3Q26 guided ~3pp; 4Q26 WS29 fit
qrows = []
for qname, rev, nights, gbv, adr, adr_fx, rev_fx, py_rev, py_nights, py_gbv, py_take, ebitda, eps in [
        ("3Q26", STREET["q3_26_rev"], STREET["q3_26_nights"], STREET["q3_26_gbv"], STREET["q3_26_adr"], ADR_FX_Q3, REV_FX_Q3, Q3_25_REV, Q3_25_NIGHTS, 22892.0, Q3_25_TAKE, STREET["q3_26_ebitda"], STREET["q3_26_eps"]),
        ("4Q26", STREET["q4_26_rev"], STREET["q4_26_nights"], STREET["q4_26_gbv"], STREET["q4_26_adr"], ADR_FX_Q4, REV_FX_Q4, Q4_25_REV, Q4_25_NIGHTS, Q4_25_GBV, Q4_25_TAKE, STREET["q4_26_ebitda"], STREET["q4_26_eps"])]:
    n_g = (nights / py_nights - 1) * 100
    gbv_g = (gbv / py_gbv - 1) * 100
    adr_rep_g = (adr / (py_gbv / py_nights) - 1) * 100
    adr_exfx_g = ((1 + adr_rep_g / 100) / (1 + adr_fx / 100) - 1) * 100
    rev_g = (rev / py_rev - 1) * 100
    take = rev / gbv * 100
    take_g = (take / (py_take * 100) - 1) * 100
    gbv_check = nights * adr
    resid_mgmt = (L(rev_g) - L(n_g) - L(adr_exfx_g) - L(rev_fx)) * 100
    qrows.append(dict(quarter=qname, street_revenue_musd=rev, street_revenue_growth_pct=round(rev_g, 2), street_nights_m=nights, street_nights_growth_pct=round(n_g, 2), brief_nights_growth_pct=STREET[f"q{qname[0]}_26_nights_growth"],
                      street_gbv_musd=gbv, street_gbv_growth_pct=round(gbv_g, 2), brief_gbv_growth_pct=STREET[f"q{qname[0]}_26_gbv_growth"], nights_x_adr_musd=round(gbv_check, 0),
                      street_adr_usd=adr, street_adr_reported_growth_pct=round(adr_rep_g, 2), brief_adr_growth_pct=STREET[f"q{qname[0]}_26_adr_growth"], adr_fx_pp_assumed=adr_fx, street_adr_exfx_growth_pct=round(adr_exfx_g, 2),
                      revenue_fx_pp_assumed=rev_fx, street_implied_take_rate_pct=round(take, 3), prior_year_take_rate_pct=round(py_take * 100, 3), street_take_rate_change_rel_pct=round(take_g, 2), street_take_rate_change_bp=round((take - py_take * 100) * 100, 0),
                      exact_identity_check_nights_plus_adr_plus_take_pct=round((np.exp(L(n_g) + L(adr_rep_g) + L(take_g)) - 1) * 100, 2),
                      mgmt_decomp_nights_plus_adrexfx_plus_fx_pct=round((np.exp(L(n_g) + L(adr_exfx_g) + L(rev_fx)) - 1) * 100, 2), timing_takerate_residual_pp=round(resid_mgmt, 2),
                      street_ebitda_musd=ebitda, street_ebitda_margin_pct=round(ebitda / rev * 100, 1), street_eps_usd=eps,
                      revenue_at_flat_take_rate_musd=round(gbv * py_take, 0), street_revenue_minus_flat_take_rate_musd=round(rev - gbv * py_take, 0)))
qd = pd.DataFrame(qrows)
qd["case_stated_residual_pp"] = np.nan
qd["case_stated_residual_convention"] = ""
# comparison rows: management cases and team base, with each case's own nights / ADR ex-FX / FX and the log-identity residual its revenue implies.
# case_stated_residual_pp is the residual the case's builder quotes: the management model's multiplicative timing term (mgmt_implied_inputs.csv),
# WS29's arithmetic-sum residual for the team (29_q4_2026_bridge.csv: 3Q26 base about -0.5 at ADR ex-FX 3.5; 4Q26 base -0.5; the -1.5 in
# 29_bridge_assumptions.csv is the guide-implied residual at nights 11 / ADR 3, not the team base). Audit finding 10.
for case, q3n, q4n, q3a, q4a, q3r, q4r, q3s, q4s, conv in [
        ("Delivered (mgmt)", 11.5, 10.5, 3.5, 3.0, 4815.14, 3130.163, -1.108, -0.6, "management model multiplicative timing term"),
        ("Literal (mgmt)", 10.0, 8.5, 3.0, 2.5, 4730.0, 3061.15, -1.052, -0.517, "management model multiplicative timing term"),
        ("Ambition (mgmt)", 12.5, 12.0, 4.0, 3.5, 4882.182, 3188.055, -1.1, -0.6, "management model multiplicative timing term"),
        ("Team base (WS29)", 9.9, 8.9, 3.5, 3.0, 4771.0, 3111.0, -0.5, -0.5, "WS29 arithmetic sum (nights + ADR + FX + residual)")]:
    for qn, n_, a_, r_, fx_, py_, s_ in [("3Q26", q3n, q3a, q3r, REV_FX_Q3, Q3_25_REV, q3s), ("4Q26", q4n, q4a, q4r, REV_FX_Q4, Q4_25_REV, q4s)]:
        rg = (r_ / py_ - 1) * 100
        qd.loc[len(qd)] = {**{c: np.nan for c in qd.columns}, "quarter": f"{qn} {case}", "street_revenue_musd": r_, "street_revenue_growth_pct": round(rg, 2), "street_nights_growth_pct": n_,
                           "street_adr_exfx_growth_pct": a_, "revenue_fx_pp_assumed": fx_,
                           "mgmt_decomp_nights_plus_adrexfx_plus_fx_pct": round((np.exp(L(n_) + L(a_) + L(fx_)) - 1) * 100, 2),
                           "timing_takerate_residual_pp": round((L(rg) - L(n_) - L(a_) - L(fx_)) * 100, 2),
                           "case_stated_residual_pp": s_, "case_stated_residual_convention": conv}
qd.to_csv(os.path.join(OUT, "A_quarterly_consensus_decomposition.csv"), index=False)

# FY reconciliation: do the quarterly components add up to the FY consensus?
fy_rows = []
q_sum_rev = H1_26_REV + STREET["q3_26_rev"] + STREET["q4_26_rev"]
q_sum_rev_zacks = H1_26_REV + 4740.0 + 3200.0
fy26_nights = H1_26_NIGHTS_M + STREET["q3_26_nights"] + STREET["q4_26_nights"]
fy26_gbv = H1_26_GBV_MUSD + STREET["q3_26_gbv"] + STREET["q4_26_gbv"]
fy_rows.append(dict(item="FY26 revenue: 1H26 actual + Bloomberg FA 3Q26 + 4Q26 midpoint", value_musd=round(q_sum_rev, 0), growth_pct=round((q_sum_rev / FY25_REV - 1) * 100, 2), compare_to="FY26 consensus $14,100-14,160m (Zacks / S&P)", gap_musd=round(q_sum_rev - STREET["fy26_rev"], 0)))
fy_rows.append(dict(item="FY26 revenue: 1H26 actual + Zacks 3Q26 $4,740m + Zacks 4Q26 $3,200m", value_musd=round(q_sum_rev_zacks, 0), growth_pct=round((q_sum_rev_zacks / FY25_REV - 1) * 100, 2), compare_to="Zacks FY26 $14,100m", gap_musd=round(q_sum_rev_zacks - 14100.0, 0)))
fy_rows.append(dict(item="FY26 revenue: 1H26 actual + 3Q26 guide midpoint $4,730m + 4Q26 at the FY guide floor (at least mid teens = 15%)", value_musd=round(FY25_REV * 1.15, 0), growth_pct=15.0, compare_to="4Q26 implied $%.0fm" % (FY25_REV * 1.15 - H1_26_REV - 4730.0), gap_musd=round(FY25_REV * 1.15 - STREET["fy26_rev"], 0)))
fy_rows.append(dict(item="FY26 nights: 1H26 actual 304.5m + Bloomberg FA 3Q26 148.9m + 4Q26 134.2m", value_musd=round(fy26_nights, 1), growth_pct=round((fy26_nights / FY25_NIGHTS_M - 1) * 100, 2), compare_to="Delivered FY26 nights %.1fm (+%.1f%%)" % (FY26_NIGHTS_BASE, (FY26_NIGHTS_BASE / FY25_NIGHTS_M - 1) * 100), gap_musd=round(fy26_nights - FY26_NIGHTS_BASE, 1)))
fy_rows.append(dict(item="FY26 GBV: 1H26 actual $56.4bn + Bloomberg FA 3Q26 $26.35bn + 4Q26 $23.0bn", value_musd=round(fy26_gbv, 0), growth_pct=round((fy26_gbv / FY25_GBV_MUSD - 1) * 100, 2), compare_to="Delivered FY26 GBV $106,057m", gap_musd=round(fy26_gbv - 106056.581, 0)))
fy_rows.append(dict(item="FY26 ADR implied by the Street components (GBV / nights)", value_musd=round(fy26_gbv / fy26_nights, 2), growth_pct=round((fy26_gbv / fy26_nights / (FY25_GBV_MUSD / FY25_NIGHTS_M) - 1) * 100, 2), compare_to="Delivered FY26 ADR $180.32", gap_musd=np.nan))
fy_rows.append(dict(item="FY26 take rate implied by the Street components (revenue / GBV)", value_musd=round(q_sum_rev / fy26_gbv * 100, 3), growth_pct=round((q_sum_rev / fy26_gbv / (FY25_REV / FY25_GBV_MUSD) - 1) * 100, 2), compare_to="FY25 13.409%; management: relatively flat", gap_musd=np.nan))
fy_rows.append(dict(item="FY27 Street revenue growth on its own FY26 (mid $14,130m)", value_musd=STREET["fy27_rev"], growth_pct=round((STREET["fy27_rev"] / STREET["fy26_rev"] - 1) * 100, 2), compare_to="on the Delivered FY26 base $14,231m: %.2f%%" % ((STREET["fy27_rev"] / FY26_REV_BASE - 1) * 100), gap_musd=np.nan))
fy_rows.append(dict(item="FY27 Street EPS $6.08 translated to revenue at 36.2% margin (Delivered P&L mechanics)", value_musd=round(revenue_from_eps(STREET["fy27_eps"], MARGIN_BASE), 0), growth_pct=round((revenue_from_eps(STREET["fy27_eps"], MARGIN_BASE) / FY26_REV_BASE - 1) * 100, 2),
                    compare_to="Street revenue $15,745m; margin needed on $15,745m for $6.08: %.1f%%" % ((STREET["fy27_eps"] * DELIVERED_SHARES_FY27_AVG / (1 - TAX_RATE) - DELIVERED_NET_INTEREST_FY27 + DELIVERED_SBC_FY27 + DA_PCT_REV * STREET["fy27_rev"]) / STREET["fy27_rev"] * 100), gap_musd=np.nan))
fyr = pd.DataFrame(fy_rows)
fyr.to_csv(os.path.join(OUT, "A_quarterly_consensus_fy_reconciliation.csv"), index=False)

# ---- 4c. implied nights at each price point --------------------------------------------------------------------------------
prim = js[js.spec == PRIMARY].set_index("price_usd")
hold165 = hl[hl.lens == "EV/FY27 EBITDA 16.5x, margin 36.2%"].set_index("price_usd")
hold159 = hl[hl.lens.str.startswith("EV/FY27 EBITDA 15.86x")].set_index("price_usd")
FX_1H27 = -0.9   # WS29 consensus path: 1Q27 -1.0, 2Q27 -0.8
TAIL = {150.0, 220.0}
nrows = []
for price, label in PRICE_POINTS:
    g27 = prim.loc[price, "fy27_growth_proportional_pct"]
    g27_lo, g27_hi = prim.loc[price, "fy27_growth_proportional_lo_pct"], prim.loc[price, "fy27_growth_proportional_hi_pct"]     # fitted-line 1 s.e. band
    g27_chain, g27_bc = prim.loc[price, "fy27_growth_chained_street_2h26_pct"], prim.loc[price, "fy27_growth_base_consistent_pct"]
    g27_map_lo, g27_map_hi = min(g27, g27_chain), max(g27, g27_chain)
    g27_real = g27 - PROXY_BIAS_PP
    gntm = prim.loc[price, "implied_ntm_growth_pct"]
    ntm_rev = prim.loc[price, "implied_ntm_revenue_musd"]
    h1_27_rev = ntm_rev - STREET_2H26_REV
    g_1h27 = (h1_27_rev / H1_26_REV - 1) * 100
    n27 = implied_nights_growth(g27)
    row = dict(price_usd=price, label=label, label_measured_or_judgement="JUDGEMENT (tail: compound of slope, mapping and fixed-base convention)" if price in TAIL else "JUDGEMENT on a MEASURED NTM solve",
               implied_fy27_revenue_growth_pct=round(g27, 2), fy27_growth_band_low_pct=round(g27_lo, 2), fy27_growth_band_high_pct=round(g27_hi, 2),
               fy27_growth_chained_street_pct=round(g27_chain, 2), fy27_growth_base_consistent_pct=round(g27_bc, 2),
               fy27_growth_mapping_range_low_pct=round(g27_map_lo, 2), fy27_growth_mapping_range_high_pct=round(g27_map_hi, 2),
               fy27_growth_realised_units_pct=round(g27_real, 2),
               implied_fy27_nights_growth_pct=round(n27, 2), fy27_nights_band_low_pct=round(implied_nights_growth(g27_lo), 2), fy27_nights_band_high_pct=round(implied_nights_growth(g27_hi), 2),
               fy27_nights_chained_street_pct=round(implied_nights_growth(g27_chain), 2), fy27_nights_base_consistent_pct=round(implied_nights_growth(g27_bc), 2),
               fy27_nights_mapping_range_low_pct=round(implied_nights_growth(g27_map_lo), 2), fy27_nights_mapping_range_high_pct=round(implied_nights_growth(g27_map_hi), 2),
               fy27_nights_realised_units_pct=round(implied_nights_growth(g27_real), 2),
               implied_fy27_nights_m=round(FY26_NIGHTS_BASE * (1 + n27 / 100), 1), implied_fy27_gbv_musd=round(FY26_NIGHTS_BASE * (1 + n27 / 100) * 180.318 * (1 + ADR_EXFX_FY27 / 100) * (1 + 0.3 / 100), 0),
               adr_exfx_pct=ADR_EXFX_FY27, fx_pp=FX_FY27_PP, take_rate_change_pct=TAKE_RATE_CHANGE_FY27, residual_pp=RESIDUAL_FY27,
               implied_fy27_nights_growth_if_residual_at_trailing4_mean_pct=round(implied_nights_growth(g27, residual_pp=res_stats["trailing_four_mean"]), 2),
               implied_ntm_revenue_growth_pct=round(gntm, 2), implied_1h27_revenue_growth_given_street_2h26_pct=round(g_1h27, 2),
               implied_1h27_nights_growth_given_street_2h26_pct=round(implied_nights_growth(g_1h27, fx_pp=FX_1H27), 2),
               hold_16_5x_fy27_growth_pct=round(hold165.loc[price, "implied_fy27_growth_pct"], 2), hold_16_5x_fy27_nights_growth_pct=round(implied_nights_growth(hold165.loc[price, "implied_fy27_growth_pct"]), 2),
               hold_15_9x_fy27_growth_pct=round(hold159.loc[price, "implied_fy27_growth_pct"], 2), hold_15_9x_fy27_nights_growth_pct=round(implied_nights_growth(hold159.loc[price, "implied_fy27_growth_pct"]), 2))
    nrows.append(row)
nights = pd.DataFrame(nrows)
nights.to_csv(os.path.join(OUT, "A_implied_nights.csv"), index=False)

# ADR sensitivity grid
srows = []
for price, label in PRICE_POINTS:
    g27 = prim.loc[price, "fy27_growth_proportional_pct"]
    for adr in (2.0, 3.0, 4.0):
        for fx in (FX_FY27_PP,):
            for resid in (0.0, round(res_stats["trailing_four_mean"], 2)):
                srows.append(dict(price_usd=price, implied_fy27_revenue_growth_pct=round(g27, 2), adr_exfx_pct=adr, fx_pp=fx, take_rate_change_pct=0.0, residual_pp=resid,
                                  implied_fy27_nights_growth_pct=round(implied_nights_growth(g27, adr_exfx_pct=adr, fx_pp=fx, residual_pp=resid), 2)))
sens = pd.DataFrame(srows)
sens.to_csv(os.path.join(OUT, "A_implied_nights_sensitivity.csv"), index=False)
sens_grid = sens[sens.residual_pp == 0].pivot(index="adr_exfx_pct", columns="price_usd", values="implied_fy27_nights_growth_pct")

# ---- 5. comparison table -----------------------------------------------------------------------------------------------------------------
d10 = dcf[(dcf.wacc_pct == 10) & (dcf.terminal_growth_pct == 3)]
crows = []
for price, label in PRICE_POINTS:
    p = prim.loc[price]
    g27 = p["fy27_growth_proportional_pct"]
    g27c = p["fy27_growth_chained_street_2h26_pct"]
    gl, gh = min(g27, g27c), max(g27, g27c)
    rev27 = FY26_REV_BASE * (1 + g27 / 100)
    rev_l, rev_h = FY26_REV_BASE * (1 + gl / 100), FY26_REV_BASE * (1 + gh / 100)
    crows.append(dict(row=f"${price:.2f} {label}", kind="price point", price_usd=price, fy27_revenue_musd=round(rev27, 0), fy27_revenue_growth_pct=round(g27, 2),
                      fy27_growth_band_pct=f"{p['fy27_growth_proportional_lo_pct']:.1f} to {p['fy27_growth_proportional_hi_pct']:.1f}",
                      fy27_ebitda_musd=round(rev27 * MARGIN_BASE, 0), fy27_margin_pct=36.2, fy27_eps_usd=round(eps_from_revenue(rev27, MARGIN_BASE), 2),
                      fy27_nights_growth_pct=round(implied_nights_growth(g27), 2), ntm_revenue_growth_pct=round(p["implied_ntm_growth_pct"], 2),
                      ev_fy27_ebitda_x=round(ev_spot(price) / (rev27 * MARGIN_BASE), 2), ev_ntm_ebitda_x=round(p["implied_ev_ntm_ebitda_x"], 2),
                      reverse_dcf_fy28_growth_reported_pct=d10[(d10.price_usd == price) & (d10.fcf_basis == "Delivered reported FCF")]["implied_fy28_starting_fcf_growth_pct"].iloc[0],
                      reverse_dcf_fy28_growth_sbc_adj_pct=d10[(d10.price_usd == price) & (d10.fcf_basis == "Delivered SBC-adjusted FCF")]["implied_fy28_starting_fcf_growth_pct"].iloc[0],
                      hold_16_5x_fy27_growth_pct=round(hold165.loc[price, "implied_fy27_growth_pct"], 2),
                      # added after audit: the solve is MEASURED in NTM terms; FY27 is a range across the two legitimate mappings (proportional, chained through Street 2H26)
                      label_measured_or_judgement="JUDGEMENT (tail: compound of slope, mapping and fixed-base convention)" if price in TAIL else "JUDGEMENT on a MEASURED NTM solve",
                      ntm_growth_band_pct=f"{p['implied_ntm_growth_lo_pct']:.1f} to {p['implied_ntm_growth_hi_pct']:.1f}",
                      ntm_growth_realised_units_pct=round(p["implied_ntm_growth_realised_units_pct"], 2),
                      fy27_growth_chained_street_pct=round(g27c, 2), fy27_growth_base_consistent_pct=round(p["fy27_growth_base_consistent_pct"], 2),
                      fy27_growth_range_pct=f"{gl:.1f} to {gh:.1f}", fy27_revenue_range_musd=f"{rev_l:,.0f} to {rev_h:,.0f}",
                      fy27_ebitda_range_musd=f"{rev_l * MARGIN_BASE:,.0f} to {rev_h * MARGIN_BASE:,.0f}",
                      ev_fy27_ebitda_range_x=f"{ev_spot(price) / (rev_h * MARGIN_BASE):.1f} to {ev_spot(price) / (rev_l * MARGIN_BASE):.1f}",
                      fy27_nights_range_pct=f"{implied_nights_growth(gl):.1f} to {implied_nights_growth(gh):.1f}",
                      fy27_growth_realised_units_pct=round(g27 - PROXY_BIAS_PP, 2), fy27_growth_realised_units_range_pct=f"{gl - PROXY_BIAS_PP:.1f} to {gh - PROXY_BIAS_PP:.1f}",
                      fy27_nights_realised_units_pct=round(implied_nights_growth(g27 - PROXY_BIAS_PP), 2)))
for case in ["Literal", "Delivered", "Ambition"]:
    c = MGMT[case]
    crows.append(dict(row=f"Management {case}", kind="management case", price_usd=np.nan, fy27_revenue_musd=round(c["fy27_rev"], 0), fy27_revenue_growth_pct=round((c["fy27_rev"] / FY26_REV_BASE - 1) * 100, 2),
                      fy27_growth_band_pct=f"own-base growth {c['fy27_growth']:.1f}", fy27_ebitda_musd=round(c["fy27_ebitda"], 0), fy27_margin_pct=c["fy27_margin"], fy27_eps_usd=c["fy27_eps"],
                      fy27_nights_growth_pct=c["fy27_nights_growth"], ntm_revenue_growth_pct=round((c["ntm_rev"] / LTM_REV - 1) * 100, 2),
                      ev_fy27_ebitda_x=round(ev_spot(PRICE) / c["fy27_ebitda"], 2), ev_ntm_ebitda_x=round(ev_spot(PRICE) / c["ntm_ebitda"], 2),
                      reverse_dcf_fy28_growth_reported_pct=np.nan, reverse_dcf_fy28_growth_sbc_adj_pct=np.nan, hold_16_5x_fy27_growth_pct=np.nan))
crows.append(dict(row="Street (Bloomberg FA / Zacks / S&P, 3-4 Sep)", kind="street", price_usd=np.nan, fy27_revenue_musd=STREET["fy27_rev"], fy27_revenue_growth_pct=round((STREET["fy27_rev"] / FY26_REV_BASE - 1) * 100, 2),
                  fy27_growth_band_pct=f"own-base growth {(STREET['fy27_rev'] / STREET['fy26_rev'] - 1) * 100:.1f}; range 14,990-16,290", fy27_ebitda_musd=round(STREET["fy27_rev"] * MARGIN_BASE, 0), fy27_margin_pct="36.2 assumed", fy27_eps_usd=STREET["fy27_eps"],
                  fy27_nights_growth_pct=round(implied_nights_growth((STREET["fy27_rev"] / FY26_REV_BASE - 1) * 100), 2), ntm_revenue_growth_pct=np.nan,
                  ev_fy27_ebitda_x=round(ev_spot(PRICE) / (STREET["fy27_rev"] * MARGIN_BASE), 2), ev_ntm_ebitda_x=np.nan, reverse_dcf_fy28_growth_reported_pct=np.nan, reverse_dcf_fy28_growth_sbc_adj_pct=np.nan, hold_16_5x_fy27_growth_pct=np.nan))
crows.append(dict(row="Team base (WS29 / WS30)", kind="team", price_usd=np.nan, fy27_revenue_musd=round(TEAM["fy27_rev"], 0), fy27_revenue_growth_pct=round((TEAM["fy27_rev"] / FY26_REV_BASE - 1) * 100, 2),
                  fy27_growth_band_pct=f"own-base growth {TEAM['fy27_growth']:.1f}", fy27_ebitda_musd=round(TEAM["fy27_ebitda"], 0), fy27_margin_pct=TEAM["fy27_margin"], fy27_eps_usd=TEAM["fy27_eps"],
                  fy27_nights_growth_pct=TEAM["fy27_nights_growth"], ntm_revenue_growth_pct=np.nan, ev_fy27_ebitda_x=round(ev_spot(PRICE) / TEAM["fy27_ebitda"], 2), ev_ntm_ebitda_x=np.nan,
                  reverse_dcf_fy28_growth_reported_pct=np.nan, reverse_dcf_fy28_growth_sbc_adj_pct=np.nan, hold_16_5x_fy27_growth_pct=np.nan))
comp = pd.DataFrame(crows)
comp.to_csv(os.path.join(OUT, "A_comparison_table.csv"), index=False)

# which case is nearest to each price, and at what price the joint solve prices each case
a_p, b_p = float(js[js.spec == PRIMARY]["intercept"].iloc[0]), float(js[js.spec == PRIMARY]["slope_turns_per_pt"].iloc[0])
spread = (MGMT["Delivered"]["ntm_rev"] / LTM_REV - 1) * 100 - MGMT["Delivered"]["fy27_growth"]


def price_for_fy27_growth(g27):
    g_ntm = g27 + spread
    ev = (a_p + b_p * g_ntm) * LTM_REV * (1 + g_ntm / 100) * LTM_MARGIN
    return (ev + NET_CASH) / SHARES_M


cases = {"Management Literal": (MGMT["Literal"]["fy27_rev"] / FY26_REV_BASE - 1) * 100, "Management Delivered": MGMT["Delivered"]["fy27_growth"], "Management Ambition": (MGMT["Ambition"]["fy27_rev"] / FY26_REV_BASE - 1) * 100,
         "Street FY27 $15,745m": (STREET["fy27_rev"] / FY26_REV_BASE - 1) * 100, "Team base $15,804m": (TEAM["fy27_rev"] / FY26_REV_BASE - 1) * 100,
         "Team bear $14,318m (WS29)": (14318.33 / FY26_REV_BASE - 1) * 100, "Team bull $16,910m (WS29)": (16909.76 / FY26_REV_BASE - 1) * 100}
cp = pd.DataFrame([dict(case=k, fy27_revenue_growth_on_delivered_fy26_base_pct=round(v, 2), joint_solve_price_usd=round(price_for_fy27_growth(v), 2),
                        upside_vs_170_19_pct=round((price_for_fy27_growth(v) / PRICE - 1) * 100, 1),
                        fy27_ebitda_at_36_2_musd=round(FY26_REV_BASE * (1 + v / 100) * MARGIN_BASE, 0)) for k, v in cases.items()])
nearest = []
named = {k: v for k, v in cases.items() if k.startswith("Management") or k.startswith("Street") or k.startswith("Team base")}


def nearest_of(g):
    dist = {k: abs(v - g) for k, v in named.items()}
    k = min(dist, key=dist.get)
    return k, dist[k], "above" if g > named[k] else "below"


for price, label in PRICE_POINTS:
    p = prim.loc[price]
    g27 = p["fy27_growth_proportional_pct"]
    g27c = p["fy27_growth_chained_street_2h26_pct"]
    g27r = g27 - PROXY_BIAS_PP
    k0, d0, s0 = nearest_of(g27)
    kc, dc, sc = nearest_of(g27c)
    kr, dr, sr = nearest_of(g27r)
    lo_k, hi_k = (kc, k0) if g27c <= g27 else (k0, kc)
    nearest.append(dict(price_usd=price, implied_fy27_growth_pct=round(g27, 2), nearest_case=k0, gap_pp=round(d0, 2), gap_direction=s0,
                        nearest_case_chained_mapping=kc, gap_pp_chained=round(dc, 2),
                        nearest_case_range=(lo_k if lo_k == hi_k else f"{lo_k} to {hi_k}"),
                        nearest_case_realised_units=kr, gap_pp_realised_units=round(dr, 2), gap_direction_realised_units=sr,
                        cases_inside_mapping_range=", ".join(k for k, v in named.items() if min(g27, g27c) - 0.25 <= v <= max(g27, g27c) + 0.25) or "none"))
nearest = pd.DataFrame(nearest)
cp.to_csv(os.path.join(OUT, "A_case_implied_prices.csv"), index=False)
nearest.to_csv(os.path.join(OUT, "A_nearest_case_by_price.csv"), index=False)

# ---- headline ----------------------------------------------------------------------------------------------------------------------
head = comp[comp.kind == "price point"][["row", "price_usd", "fy27_revenue_growth_pct", "fy27_growth_band_pct", "fy27_revenue_musd", "fy27_ebitda_musd", "fy27_eps_usd", "fy27_nights_growth_pct", "ntm_revenue_growth_pct", "ev_fy27_ebitda_x", "ev_ntm_ebitda_x", "reverse_dcf_fy28_growth_reported_pct", "reverse_dcf_fy28_growth_sbc_adj_pct",
                                          "label_measured_or_judgement", "ntm_growth_band_pct", "ntm_growth_realised_units_pct", "fy27_growth_chained_street_pct", "fy27_growth_base_consistent_pct", "fy27_growth_range_pct", "fy27_revenue_range_musd", "fy27_ebitda_range_musd", "ev_fy27_ebitda_range_x", "fy27_nights_range_pct",
                                          "fy27_growth_realised_units_pct", "fy27_growth_realised_units_range_pct", "fy27_nights_realised_units_pct"]].copy()
head = head.merge(nearest[["price_usd", "nearest_case", "gap_pp", "nearest_case_range", "nearest_case_realised_units", "cases_inside_mapping_range"]], on="price_usd")
head.to_csv(os.path.join(OUT, "A_headline.csv"), index=False)

# ---- console ---------------------------------------------------------------------------------------------------------------------------
print("Identity check 1Q23-2Q26:\n", h.to_string())
print("\nResidual stats (mgmt decomposition, pp):", {k: round(v, 2) for k, v in res_stats.items()})
print("\nQuarterly consensus decomposition:\n", qd.T.to_string())
print("\nFY reconciliation:\n", fyr.to_string(index=False))
print("\nImplied nights:\n", nights.to_string(index=False))
print("\nADR sensitivity (FY27 nights growth, residual 0):\n", sens_grid.to_string())
print("\nComparison table:\n", comp.to_string(index=False))
print("\nCase implied prices:\n", cp.to_string(index=False))
print("\nNearest case by price:\n", nearest.to_string(index=False))
print("\nHeadline:\n", head.to_string(index=False))
