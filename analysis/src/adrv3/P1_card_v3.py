"""
WS-P (ADR v3, 11 Sep 2026), step 1: card v3 for 3Q26 and 4Q26 on the S harness.

Point (BRIEF, P): the pre-registered v3 result first, then any K, L, M term that passed its
criterion. Only K passed (on the letter, by 0.003 to 0.007 of ratio; K note point 1), so:

  ex-FX v3 (without K) = last_q residual (2Q26 value, 4.85; 4Q26 carries the same because no
                         3Q26 residual exists)
                       + workstream I's measured 3Q26 mix terms (geo, size, LOS; 4Q26 carries them)
                       + new business and interaction as J3 carries them (H fills)
  ex-FX v3 (with K)    = the same + K's mechanics line, 0.007 x change in y/y migrated nights
                         share (+0.17 pp in 3Q26; 4Q26 chained as K4: +0.17 + 0.20 = +0.37 over
                         the flat last_q carry, so the 4Q26 residual with K is K4's 5.22)
  reported             = ex-FX + N's midpoint FX (euro fit and baskets alongside)

L (FAIL 0 of 4) and M (FAIL 2 of 4) are memo lines, never in the point. The H card's fee
increment, card v2, the H card and consensus are memo lines too.

Bands: central = point +/- root-sum-square of the term half-ranges (J3 convention); wide = the
arithmetic sum of lo / hi plus the min / max of the two single FX estimators. Residual band from
K's scenario table: 3Q26 mean reversion 2.40 to last_q 4.85; 4Q26 lap-only 3.06 to K rule 5.22
(without K) or 3.06 to 4.85 (with K, where the K rule's 5.22 is the K line itself, so it is not
counted twice). K line band = the mechanics coefficient range 0.000 to 0.038 on the same share
changes (K2 pre-stated range).

Dollar ADR on 3Q25 $171.29 and 4Q25 $167.51. GBV and revenue (comparison columns, not inputs)
at 146.8mm nights for 3Q26 and at BOTH 4Q26 nights cases, N's case B 131.8mm (baseline) and case
A 132.7mm (top of the band), with J3's same-quarter-prior-year take-rate convention.

Walk-forward: the exact v3 point specification (last_q + measured mix + K line) is re-run on the
S harness (K's K_mech_central residual path, central cohort variant, through S.exfx_from_residual
with measured mix and S's prior-calendar-year fills, exactly as S and K scored it), with the plain
last_q rule alongside, and S.preregistered_pass printed for both.

Outputs (data/processed/adrv3/P/): adr_card_v3.csv, P1_card_v3_terms.csv, P1_card_v3_backtest.csv,
P1_card_v3_backtest_paths.csv, P1_card_v3_pass_table.csv.

Run: py -3.13 analysis/src/adrv3/P1_card_v3.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import S1_scoring as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "P")
os.makedirs(OUT, exist_ok=True)
P = lambda *a: os.path.join(ROOT, "data", "processed", *a)  # noqa: E731

# ----------------------------------------------------------------------------------
# 0. inputs (all read from files committed by H, I, J, S, K, L, M, N)
# ----------------------------------------------------------------------------------
H = pd.read_csv(P("q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
res = H["residual_pricing_pp"].astype(float)
I = pd.read_csv(P("adrq3", "I", "I_mix_terms_3q26.csv"))
J3_terms = pd.read_csv(P("adrq3", "J", "J3_card_v2_terms.csv"))
card_v2 = pd.read_csv(P("adrq3", "J", "adr_card_v2.csv"))
Hcard = pd.read_csv(P("q3nowcast", "H", "adr_forecast_card.csv"))
K4 = pd.read_csv(P("adrv3", "K", "K4_residual_nowcast.csv"))
Klap = pd.read_csv(P("adrv3", "K", "K4_fee_lap_schedule.csv"))
Kpaths = pd.read_csv(P("adrv3", "K", "K3_rule_residual_paths.csv"))
Kscores = pd.read_csv(P("adrv3", "K", "K3_residual_rule_scores.csv"))
K2pre = pd.read_csv(P("adrv3", "K", "K2_expected_effect_prestated.csv"))
L4 = pd.read_csv(P("adrv3", "L", "L4_aggregate_nowcast.csv"))
L3pass = pd.read_csv(P("adrv3", "L", "L3_pass.csv"))
M6 = pd.read_csv(P("adrv3", "M", "M6_term_3q26.csv"))
M5crit = pd.read_csv(P("adrv3", "M", "M5_criterion.csv"))
N1 = pd.read_csv(P("adrv3", "N", "N1_fx_choice_card.csv"))
N2 = pd.read_csv(P("adrv3", "N", "N2_q4_lap_cases.csv"))
S_v3 = pd.read_csv(P("adrv3", "S", "v3_preregistered_result.csv"))
sd_q = pd.read_csv(P("adr", "15_seats_dilution_quarterly.csv")).set_index(["case_business", "quarter"])["dilution_drag_pp"]
cons_file = P("q3nowcast", "H", "adr_consensus_implied.csv")
cons = pd.read_csv(cons_file) if os.path.exists(cons_file) else None

QUARTERS = ("3Q26", "4Q26")
BASE_Q = {"3Q26": "3Q25", "4Q26": "4Q25"}
BASE_ADR = {q: float(H.at[BASE_Q[q], "adr_usd"]) for q in QUARTERS}          # 171.29, 167.51 (sourced)
BASE_NIGHTS = {q: float(H.at[BASE_Q[q], "nights_m"]) for q in QUARTERS}      # 133.6, 121.9 (sourced)
TAKE = {"3Q26": 0.1788, "4Q26": 0.1362}                                      # J3 same-quarter-prior-year take rate
REV_BASE = {"3Q26": 4095.0, "4Q26": 2778.0}                                  # J3 prior-year revenue, $mm
NIGHTS_CASES = {
    "3Q26": [("team_baseline", 146.8, "team nights baseline (Q3 nowcast synthesis; reviews index band 8.5 to 11.0)")],
    "4Q26": [("N_case_B_global_lap_baseline", 131.8, "N memo 2 case B, WS-D global lap at the 45% ex-NA split, adopted as baseline"),
             ("N_case_A_team_baseline_top_of_band", 132.7, "N memo 2 case A, PR #32 NA-only lap, kept as the top of the band")],
}
assert abs(BASE_ADR["3Q26"] - 171.29) < 1e-6 and abs(BASE_ADR["4Q26"] - 167.51) < 1e-6

# FX: N's recommended midpoint, with the two single estimators alongside (N1 card = H card values)
FX = {}
for q in QUARTERS:
    n = N1[N1.quarter == q].set_index("fx_estimator")["fx_effect_pp"]
    FX[q] = {"eur_fit": float(n["eur_fit"]), "baskets": float(n["baskets"]), "midpoint": float(n["midpoint"])}
    assert abs(FX[q]["midpoint"] - 0.5 * (FX[q]["eur_fit"] + FX[q]["baskets"])) < 0.01
    assert bool(N1[(N1.quarter == q) & (N1.fx_estimator == "midpoint")]["recommended"].iloc[0])

# I's measured 3Q26 mix terms (point, lo, hi); 4Q26 carries them (J3 convention)
def i_term(term: str):
    r = I[(I.term == term) & (I.quarter == "3Q26")].iloc[0]
    return float(r.lo), float(r.point_pp), float(r.hi)

MIX = {"geographic_mix": i_term("geo_mix"), "unit_size_party": i_term("unit_size"), "length_of_stay_mix": i_term("los_mix")}
assert abs(MIX["geographic_mix"][1] + 1.43) < 0.01 and abs(MIX["unit_size_party"][1] - 0.80) < 0.01 and abs(MIX["length_of_stay_mix"][1] - 0.06) < 0.01

# residual: v3 last_q rule = the 2Q26 value, carried to 4Q26
R_LASTQ = float(res["2Q26"])
assert abs(R_LASTQ - 4.85) < 0.005
k4 = lambda scen, q: float(K4[(K4.scenario == scen) & (K4.quarter == q)]["residual_pp"].iloc[0])  # noqa: E731
R_MEANREV = k4("mean reversion", "3Q26")                       # 2.40, 2023-25 mean
R_LAP_ONLY_4Q = k4("lap only, residual steps", "4Q26")         # 3.06
R_K_RULE_3Q = k4("cohort mechanics, central (last_q + 0.007 * change in y/y share)", "3Q26")   # 5.02
R_K_RULE_4Q = k4("cohort mechanics, central (last_q + 0.007 * change in y/y share)", "4Q26")   # 5.22, chained
R_K_HIGH_3Q = k4("cohort mechanics, high (last_q + 0.038 * change in y/y share)", "3Q26")      # 5.78
R_K_HIGH_4Q = k4("cohort mechanics, high (last_q + 0.038 * change in y/y share)", "4Q26")      # 6.88
assert abs(k4("last_q (v3 rule)", "3Q26") - R_LASTQ) < 1e-3

# K line: 0.007 x change in the y/y migrated nights share (central path), chained for 4Q26
kl = Klap[Klap.variant == "central"].set_index("quarter")["yoy_change_pp"]
K_COEF_CENTRAL, K_COEF_HIGH = 0.007, 0.038
dd_3q = float(kl["3Q26"] - kl["2Q26"])          # +24.5 pp
dd_4q = float(kl["4Q26"] - kl["3Q26"])          # +29.0 pp
K_LINE = {"3Q26": (0.0, K_COEF_CENTRAL * dd_3q, K_COEF_HIGH * dd_3q),
          "4Q26": (0.0, K_COEF_CENTRAL * (dd_3q + dd_4q), K_COEF_HIGH * (dd_3q + dd_4q))}
assert abs(R_LASTQ + K_LINE["3Q26"][1] - R_K_RULE_3Q) < 0.01
assert abs(R_LASTQ + K_LINE["4Q26"][1] - R_K_RULE_4Q) < 0.01
assert abs(R_LASTQ + K_LINE["4Q26"][2] - R_K_HIGH_4Q) < 0.01
K_INCR = {"3Q26": K_COEF_CENTRAL * dd_3q, "4Q26": K_COEF_CENTRAL * dd_4q}    # the per-quarter K increment (+0.17, +0.20)

# new business and interaction as J3 carries them (H fills)
NB = {q: (float(sd_q.loc[("bull", q)]), float(sd_q.loc[("base", q)]), float(sd_q.loc[("bear", q)])) for q in QUARTERS}
INTER = (-0.15, -0.10, -0.05)
for q in QUARTERS:   # must match J3's terms file exactly
    j = J3_terms[(J3_terms.quarter == q) & (J3_terms.term == "new_business_seats")].iloc[0]
    assert abs(j.point_pp - NB[q][1]) < 1e-9 and abs(j.lo_pp - NB[q][0]) < 1e-9 and abs(j.hi_pp - NB[q][2]) < 1e-9

# memo inputs
FEE_MEMO_H = {q: tuple(J3_terms[(J3_terms.quarter == q) & (J3_terms.term == "memo_fee_migration_increment_H")].iloc[0][["lo_pp", "point_pp", "hi_pp"]].astype(float)) for q in QUARTERS}
M_TERM = {"3Q26": M6[(M6.quarter == "3Q26_to_date") & (M6.variant == "band")].iloc[0], "4Q26": M6[(M6.quarter == "4Q26")].iloc[0]}
L_MEMO = {v: {q: L4[(L4.variant == v) & (L4.quarter == q)].iloc[0] for q in QUARTERS} for v in ("L_reg_lastq", "L_wf", "L_fixed_hicp")}

# ----------------------------------------------------------------------------------
# 1. term table and card, two variants (without K = the pre-registered v3 result; with K)
# ----------------------------------------------------------------------------------
def terms_for(q: str, with_k: bool) -> dict:
    """term -> (lo, point, hi, source, label). Order is the walk order on the slide."""
    if q == "3Q26":
        r_band = (R_MEANREV, R_LASTQ, R_LASTQ)
        r_src = "H residual history; v3 last_q rule = 2Q26 value; band K4 scenario table: mean reversion (2023-25 mean) to last_q"
    elif with_k:
        r_band = (R_LAP_ONLY_4Q, R_LASTQ, R_LASTQ)
        r_src = "H residual history; last_q carried (no 3Q26 residual exists); band K4 scenario table: lap only (3.06) to last_q; the K rule's 5.22 is the K line below, not counted here"
    else:
        r_band = (R_LAP_ONLY_4Q, R_LASTQ, R_K_RULE_4Q)
        r_src = "H residual history; last_q carried (no 3Q26 residual exists); band K4 scenario table: lap only (3.06) to the K rule chained (5.22)"
    t = {
        "like_for_like_pricing_residual": (*r_band, r_src, "assumed rule, anchored on measured residuals; the one unobserved line"),
        "geographic_mix": (*MIX["geographic_mix"], "workstream I I_mix_terms_3q26.csv (E_aug regional split x 07/H method)" + ("" if q == "3Q26" else "; 4Q26 carries the 3Q26 term (J3 convention)"), "measured (unvalidated mapping)"),
        "unit_size_party": (*MIX["unit_size_party"], "workstream I I_mix_terms_3q26.csv (booked capacity, 119 markets, x 0.592)" + ("" if q == "3Q26" else "; 4Q26 carries the 3Q26 term"), "measured (level term)"),
        "length_of_stay_mix": (*MIX["length_of_stay_mix"], "workstream I I_mix_terms_3q26.csv (28+ share of blocked runs)" + ("" if q == "3Q26" else "; 4Q26 carries the 3Q26 term"), "measured, unvalidated"),
        "new_business_seats": (*NB[q], "H, 15_seats_dilution_quarterly (bull / base / bear), as J3", "assumed"),
        "interaction": (*INTER, "H, 07 interaction, as J3", "descriptive"),
    }
    if with_k:
        if q == "3Q26":
            src = f"K primary rule: 0.007 x change in y/y migrated nights share (+{dd_3q:.1f} pp, central path); band = K2 pre-stated coefficient range 0.000 to 0.038; met the K criterion by 0.003 to 0.007 of ratio"
        else:
            src = f"K primary rule chained as K4: +{K_INCR['3Q26']:.2f} (3Q26 share change +{dd_3q:.1f} pp) + {K_INCR['4Q26']:.2f} (4Q26 share change +{dd_4q:.1f} pp) over the flat last_q carry; band = coefficient 0.000 to 0.038"
        t["fee_migration_mechanics_K"] = (*K_LINE[q], src, "assumed mechanics line (coefficient imposed, not estimated); K note: a nudge, not evidence")
    return t


term_rows, card_rows = [], []
for q in QUARTERS:
    for with_k in (False, True):
        variant = "v3_with_K" if with_k else "v3_without_K"
        terms = terms_for(q, with_k)
        for k, (lo, pt, hi, src, lab) in terms.items():
            term_rows.append({"quarter": q, "variant": variant, "term": k, "lo_pp": lo, "point_pp": pt, "hi_pp": hi, "in_point": True, "source": src, "label": lab})
        pt = sum(v[1] for v in terms.values())
        half = float(np.sqrt(sum(((v[2] - v[0]) / 2) ** 2 for v in terms.values())))
        arith_lo = sum(v[0] for v in terms.values())
        arith_hi = sum(v[2] for v in terms.values())
        r_pt = terms["like_for_like_pricing_residual"][1] + (terms["fee_migration_mechanics_K"][1] if with_k else 0.0)
        for fxname, fx in FX[q].items():
            rep = pt + fx
            c_lo, c_hi = pt - half + fx, pt + half + fx
            w_lo = arith_lo + min(FX[q]["eur_fit"], FX[q]["baskets"])
            w_hi = arith_hi + max(FX[q]["eur_fit"], FX[q]["baskets"])
            adr = BASE_ADR[q] * (1 + rep / 100)
            v2 = card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == fxname)].iloc[0]
            hc = Hcard[(Hcard.quarter == q) & (Hcard.route == "headline_mean_of_routes") & (Hcard.fx_estimator == fxname)].iloc[0]
            for case_name, nights, case_src in NIGHTS_CASES[q]:
                gbv = adr * nights
                nights_yoy = 100 * (nights / BASE_NIGHTS[q] - 1)
                card_rows.append({
                    "quarter": q, "variant": variant, "base_quarter": BASE_Q[q], "base_adr_usd": BASE_ADR[q],
                    "fx_estimator": fxname, "fx_recommended_N": fxname == "midpoint", "fx_effect_pp": round(fx, 2),
                    "residual_rule": "last_q (v3, pre-registered)" + (" + K mechanics line" if with_k else ""),
                    "residual_pp": round(r_pt, 2), "residual_band_lo_pp": round(terms["like_for_like_pricing_residual"][0], 2),
                    "residual_band_hi_pp": round(terms["like_for_like_pricing_residual"][2] + (terms["fee_migration_mechanics_K"][2] if with_k else 0.0), 2),
                    "k_line_pp": round(terms["fee_migration_mechanics_K"][1], 2) if with_k else 0.0,
                    "mix_source": "workstream I measured 3Q26 terms" + ("" if q == "3Q26" else " carried to 4Q26"),
                    "adr_exfx_yoy_pp": round(pt, 2), "adr_exfx_central_lo_pp": round(pt - half, 2), "adr_exfx_central_hi_pp": round(pt + half, 2),
                    "adr_exfx_arith_lo_pp": round(arith_lo, 2), "adr_exfx_arith_hi_pp": round(arith_hi, 2),
                    "adr_reported_yoy_pp": round(rep, 2), "adr_reported_central_lo_pp": round(c_lo, 2), "adr_reported_central_hi_pp": round(c_hi, 2),
                    "adr_reported_wide_lo_pp": round(w_lo, 2), "adr_reported_wide_hi_pp": round(w_hi, 2),
                    "adr_usd_point": round(adr, 2), "adr_usd_central_lo": round(BASE_ADR[q] * (1 + c_lo / 100), 2), "adr_usd_central_hi": round(BASE_ADR[q] * (1 + c_hi / 100), 2),
                    "adr_usd_wide_lo": round(BASE_ADR[q] * (1 + w_lo / 100), 2), "adr_usd_wide_hi": round(BASE_ADR[q] * (1 + w_hi / 100), 2),
                    "nights_case": case_name, "nights_m": nights, "nights_yoy_pp": round(nights_yoy, 2), "nights_case_source": case_src,
                    "gbv_busd_point": round(gbv / 1000, 2), "gbv_yoy_pp_point": round(100 * ((1 + rep / 100) * (1 + nights_yoy / 100) - 1), 2),
                    "take_rate_same_q_prior_year": TAKE[q], "revenue_musd_same_q_take": round(gbv * TAKE[q], 0),
                    "revenue_yoy_pp_same_q_take": round(100 * (gbv * TAKE[q] / REV_BASE[q] - 1), 2),
                    "card_v2_reported_yoy_pp": float(v2.adr_reported_yoy_pp), "card_v2_adr_usd": float(v2.adr_usd_point),
                    "card_v2_exfx_pp": float(v2.adr_exfx_yoy_pp), "card_v2_residual_pp": float(v2.residual_pp),
                    "h_card_reported_yoy_pp": float(hc.adr_reported_yoy_pp), "h_card_adr_usd": float(hc.adr_usd_point), "h_card_exfx_pp": float(hc.adr_exfx_yoy_pp),
                    "band_basis": "central = point +/- RSS of term half-ranges (J3); wide = arithmetic lo/hi + min/max of eur and baskets FX",
                    "label": "point: sourced residual history + measured mix + assumed fills" + (" + assumed K mechanics line" if with_k else "") + "; GBV and revenue are comparison columns, not inputs",
                })
    # memo lines (not in the point), one row each per quarter
    memo = [
        ("memo_L_regional_lastq_carry_exfx", L_MEMO["L_reg_lastq"][q].blended_exfx_pp, L_MEMO["L_reg_lastq"][q].lo_central_pp, L_MEMO["L_reg_lastq"][q].hi_central_pp,
         "L4 regional last_q aggregate (NA 6.75, EMEA 5.0, LatAm 2.0, APAC -1.35 carried; geo -1.43): ex-FX ADR y/y, L FAILED its criterion (2 of 4 vs last_q for this variant; primary L_wf 0 of 4)", "descriptive, memo only"),
        ("memo_L_primary_wf_exfx_failed", L_MEMO["L_wf"][q].blended_exfx_pp, L_MEMO["L_wf"][q].lo_central_pp, L_MEMO["L_wf"][q].hi_central_pp,
         "L4 primary walk-forward model (NA on BEA lag 1): the failed model's number, should not be used", "descriptive, memo only (FAIL 0 of 4)"),
        ("memo_L_emea_hicp_read", 4.6, np.nan, np.nan, "July euro-area HICP accommodation 4.6 implies EMEA ex-FX about 4.6 for 3Q26 (L note); regional read for the letter, nothing more", "descriptive, memo only"),
        ("memo_M_new_listing_premium_term", float(M_TERM[q].term_pp), float(M_TERM[q].term_lo_pp), float(M_TERM[q].term_hi_pp),
         "M6: quote-basis premium x July 2026 share change, 120 markets; M FAILED its criterion (RMSE lower on 2 of 4 checks)" + ("" if q == "3Q26" else "; 4Q26 carried"), "descriptive, memo only (FAIL 2 of 4)"),
        ("memo_H_fee_migration_increment", FEE_MEMO_H[q][1], FEE_MEMO_H[q][0], FEE_MEMO_H[q][2],
         "H card table 2.3 increment; superseded by the K line (same mechanics, dated cohort); not added", "assumed, memo only"),
        ("memo_card_v2_exfx", float(card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == "midpoint")].adr_exfx_yoy_pp.iloc[0]),
         float(card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == "midpoint")].adr_exfx_central_lo_pp.iloc[0]),
         float(card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == "midpoint")].adr_exfx_central_hi_pp.iloc[0]),
         "J3 card v2 ex-FX (persistence residual 4.61 + same mix and fills); comparison column", "descriptive, comparison"),
        ("memo_card_v2_reported_midpoint", float(card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == "midpoint")].adr_reported_yoy_pp.iloc[0]),
         float(card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == "midpoint")].adr_reported_central_lo_pp.iloc[0]),
         float(card_v2[(card_v2.quarter == q) & (card_v2.fx_estimator == "midpoint")].adr_reported_central_hi_pp.iloc[0]),
         "J3 card v2 reported y/y at midpoint FX; comparison column", "descriptive, comparison"),
        ("memo_H_card_reported_midpoint", float(Hcard[(Hcard.quarter == q) & (Hcard.route == "headline_mean_of_routes") & (Hcard.fx_estimator == "midpoint")].adr_reported_yoy_pp.iloc[0]),
         float(Hcard[(Hcard.quarter == q) & (Hcard.route == "headline_mean_of_routes") & (Hcard.fx_estimator == "midpoint")].adr_reported_central_lo_pp.iloc[0]),
         float(Hcard[(Hcard.quarter == q) & (Hcard.route == "headline_mean_of_routes") & (Hcard.fx_estimator == "midpoint")].adr_reported_central_hi_pp.iloc[0]),
         "H card headline (mean of routes) at midpoint FX; comparison column", "descriptive, comparison"),
        ("memo_naive_last_disclosed_exfx", 4.0, np.nan, np.nan, "last disclosed ex-FX ADR y/y (2Q26 letter, whole points): the naive the harness scores against", "sourced, comparison"),
    ]
    if cons is not None:
        for _, c in cons[cons.quarter == q].iterrows():
            memo.append((f"memo_consensus_implied_adr_yoy_{c.vendor}_{c.nights_assumption}", float(c.implied_adr_yoy_pp), np.nan, np.nan,
                         f"{c.vendor} revenue ${c.consensus_revenue_musd:,.0f}mm at take {c.take_rate_assumed} and {c.nights_m}mm nights implies ADR ${c.implied_adr_usd} ({c.implied_adr_yoy_pp:+.2f}% y/y); comparison only, never an input", "descriptive, comparison"))
    for name, pt_, lo_, hi_, src, lab in memo:
        term_rows.append({"quarter": q, "variant": "memo", "term": name, "lo_pp": lo_, "point_pp": pt_, "hi_pp": hi_, "in_point": False, "source": src, "label": lab})

card = pd.DataFrame(card_rows)
terms_df = pd.DataFrame(term_rows)
card.to_csv(os.path.join(OUT, "adr_card_v3.csv"), index=False)
terms_df.to_csv(os.path.join(OUT, "P1_card_v3_terms.csv"), index=False)

# ----------------------------------------------------------------------------------
# 2. the card's own walk-forward on the S harness: exact v3 point specification
#    (last_q + measured mix + K line), plain last_q alongside, S.preregistered_pass on both
# ----------------------------------------------------------------------------------
kp = Kpaths[Kpaths.variant == "central"].set_index("quarter")
r_k = kp["K_mech_central"].astype(float)
r_lq = kp["last_q"].astype(float)
# sanity: K's path is last_q plus 0.007 x the change in the y/y share, on residual history strictly before t
chk = (r_k - (r_lq + K_COEF_CENTRAL * kp["dd4share_pp"].astype(float))).abs().max()
assert chk < 1e-9, chk
v2p = S.v2_model_paths()
path_lastq = v2p[S.V3_RULE_MODEL]
path_k = S.exfx_from_residual(r_k, mix_variant="measured")
assert (S.exfx_from_residual(r_lq, "measured") - path_lastq).abs().max() < 1e-9
KNOW_K = ("no: the residual rule uses the prior-quarter residual, known only at that print; the K share path is dated from disclosures "
          "before each print (tranche dates), its level calibration from the 1Q26 and 2Q26 calls")
sc = pd.concat([
    S.score_benchmarks(),
    S.score(path_lastq, "v3_last_q_measured_mix", S.KNOWABLE_V2),
    S.score(path_k, "v3_point_last_q_plus_K_line_measured_mix", KNOW_K),
], ignore_index=True)
pass_lq = S.preregistered_pass(sc, "v3_last_q_measured_mix")
pass_k = S.preregistered_pass(sc, "v3_point_last_q_plus_K_line_measured_mix")
pt_lq = S.pass_table(pass_lq)
pt_k = S.pass_table(pass_k)
# K criterion (beats last_q on all four target-2 checks, ratio and jackknife max)
m = pt_k[pt_k.in_pass_criterion].merge(pt_lq[pt_lq.in_pass_criterion][["fx_estimator", "window", "ratio_vs_naive", "jackknife_ratio_max"]],
                                       on=["fx_estimator", "window"], suffixes=("", "_last_q"))
m["beats_last_q_ratio"] = m.ratio_vs_naive < m.ratio_vs_naive_last_q
m["beats_last_q_jackknife_max"] = m.jackknife_ratio_max < m.jackknife_ratio_max_last_q
m["margin_ratio"] = m.ratio_vs_naive_last_q - m.ratio_vs_naive
k_met = bool(m.beats_last_q_ratio.all() and m.beats_last_q_jackknife_max.all())
# reproduction against S's and K's committed results
s_chk = S_v3[S_v3.in_pass_criterion].merge(pt_lq[pt_lq.in_pass_criterion][["fx_estimator", "window", "ratio_vs_naive", "jackknife_ratio_max"]],
                                           on=["fx_estimator", "window"], suffixes=("_S", "_P"))
assert (s_chk.ratio_vs_naive_S - s_chk.ratio_vs_naive_P).abs().max() < 1e-9
assert (s_chk.jackknife_ratio_max_S - s_chk.jackknife_ratio_max_P).abs().max() < 1e-9
kk = Kscores[(Kscores.model == "K_mech_central__central") & (Kscores.target == "t2_reported_usd_yoy")] if "model" in Kscores.columns else None
if kk is not None and len(kk):
    k_chk = kk.merge(pt_k[pt_k.target == "t2_reported_usd_yoy"][["fx_estimator", "window", "ratio_vs_naive"]], on=["fx_estimator", "window"], suffixes=("_K", "_P"))
    k_repro = float((k_chk.ratio_vs_naive_K - k_chk.ratio_vs_naive_P).abs().max()) if len(k_chk) else np.nan
else:
    k_repro = np.nan

sc["S_preregistered_pass"] = sc.model.map({"v3_last_q_measured_mix": pass_lq["verdict"], "v3_point_last_q_plus_K_line_measured_mix": pass_k["verdict"]})
sc["K_criterion_beats_last_q_all_4"] = sc.model.map({"v3_point_last_q_plus_K_line_measured_mix": k_met})
sc["fills_convention"] = "walk-forward uses S's prior-calendar-year new-business and interaction fills (as J3, S, K); the card uses J3's H fills for 2026 (-0.48, -0.10)"
sc.to_csv(os.path.join(OUT, "P1_card_v3_backtest.csv"), index=False)
pd.concat([pt_lq, pt_k], ignore_index=True).to_csv(os.path.join(OUT, "P1_card_v3_pass_table.csv"), index=False)
S.paths({"v3_last_q_measured_mix": path_lastq, "v3_point_last_q_plus_K_line_measured_mix": path_k}).to_csv(os.path.join(OUT, "P1_card_v3_backtest_paths.csv"), index=False)

# ----------------------------------------------------------------------------------
# 3. print
# ----------------------------------------------------------------------------------
pd.set_option("display.width", 260)
print("\ncard v3 (midpoint FX, N's recommendation), both variants, all nights cases\n")
cols = ["quarter", "variant", "fx_estimator", "fx_effect_pp", "residual_pp", "k_line_pp", "adr_exfx_yoy_pp", "adr_reported_yoy_pp",
        "adr_reported_central_lo_pp", "adr_reported_central_hi_pp", "adr_reported_wide_lo_pp", "adr_reported_wide_hi_pp",
        "adr_usd_point", "adr_usd_central_lo", "adr_usd_central_hi", "nights_case", "nights_m", "nights_yoy_pp", "gbv_busd_point", "revenue_musd_same_q_take", "revenue_yoy_pp_same_q_take",
        "card_v2_reported_yoy_pp", "h_card_reported_yoy_pp"]
print(card[card.fx_estimator == "midpoint"][cols].to_string())
print("\nall FX estimators, baseline nights case\n")
print(card[card.nights_case.isin(["team_baseline", "N_case_B_global_lap_baseline"])][["quarter", "variant", "fx_estimator", "fx_effect_pp", "adr_exfx_yoy_pp", "adr_reported_yoy_pp", "adr_usd_point", "card_v2_reported_yoy_pp", "h_card_reported_yoy_pp"]].to_string())
print("\nterms\n", terms_df.round(3).to_string())
print("\nwalk-forward on the S harness (target 2 checks + alongside)\n")
show = ["model", "target", "fx_estimator", "window", "n", "rmse_pp", "rmse_naive_pp", "ratio_vs_naive", "jackknife_ratio_min", "jackknife_ratio_max", "jackknife_below_1", "sign_accuracy_vs_naive"]
print(sc[sc.model.str.startswith("v3")][show].round(3).to_string())
print(f"\nS.preregistered_pass, v3 last_q (measured mix)                : {pass_lq['verdict']} ({pass_lq['n_checks_met']} of {pass_lq['n_checks']} checks)")
print(f"S.preregistered_pass, v3 point = last_q + K line (measured mix): {pass_k['verdict']} ({pass_k['n_checks_met']} of {pass_k['n_checks']} checks)")
print(f"K criterion (beats last_q on all 4 target-2 checks, ratio and jackknife max): {'met' if k_met else 'not met'}; margins of ratio {m.margin_ratio.min():.3f} to {m.margin_ratio.max():.3f}")
print(f"reproduction: S v3_preregistered_result.csv matched to 1e-9; K K3_residual_rule_scores max abs ratio diff {k_repro}")
print(f"binding case: eur, 2Q24-2Q26 jackknife max last_q {pt_lq[(pt_lq.fx_estimator=='eur')&(pt_lq.window=='2Q24-2Q26')].jackknife_ratio_max.iloc[0]:.3f} (margin {1-pt_lq[(pt_lq.fx_estimator=='eur')&(pt_lq.window=='2Q24-2Q26')].jackknife_ratio_max.iloc[0]:.3f}); with K {pt_k[(pt_k.fx_estimator=='eur')&(pt_k.window=='2Q24-2Q26')].jackknife_ratio_max.iloc[0]:.3f}")
print("\nwritten:", OUT)
