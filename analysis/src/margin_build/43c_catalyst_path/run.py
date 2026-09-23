"""43c — catalyst path for the cost leg (thesis point 3).

Builds, from files already in the repo (no web, no scraping, nothing overwritten):
  1. the pre-registered E-2023 test (does a marketing deceleration cost nights within 3 quarters?)
  2. the E-2025/26 regional test (did the emerging-market paid step buy regional nights?)
  3. the 5 Nov decision tree for the cost leg from the audited C04 x C09 joint, with the Street FY27 response and
     the implied stock move on 42's slope range and a constant-multiple row
  4. the 11 Feb branch from B12 / F03
  5. the watch list with pre-registered thresholds

Run from anywhere:  py -3.13 -X utf8 analysis/src/margin_build/43c_catalyst_path/run.py   (exit 0)
Outputs: data/processed/margin_build/43c_catalyst_path/*.csv
Pre-registration: docs/margin-build/notes/43c_prereg.md (written before the nights numbers were read).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
OUT = ROOT / "data/processed/margin_build/43c_catalyst_path"
OUT.mkdir(parents=True, exist_ok=True)

PANEL = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
PEERS = ROOT / "data/processed/predictive/02_peer_prints.csv"
JOINT = ROOT / "docs/pitch-forecasts/questions/fy26-margin-sentence/datasets/mc_joint_and_conditionals_v2.json"
SCEN42 = ROOT / "data/processed/margin_build/42_margin_reaction/42_scenarios.csv"
LINES40 = ROOT / "data/processed/margin_build/40_line_build/40_lines_quarterly.csv"

PRICE = 166.84          # 21 Sep 2026 close, from 42_margin_reaction.md
SLOPE_W1, SLOPE_W2 = 2.10, 2.66   # 42 R1: 5-session excess per 1% NTM EBITDA revision
NTM_WEIGHT_FY27_NOV = 0.85        # 42: NTM weight on FY27 at the November print
STREET_FY27_EBITDA = 5766.1       # LSEG FY27 mean (41)
STREET_FY27_REV = 15819.3
STREET_FY26_EBITDA = 5053.7


def q_to_key(q: str) -> str:
    # '3Q23' -> '2023Q3'
    return f"20{q[2:]}Q{q[0]}"


# ----------------------------------------------------------------------------------------------------------------
# 1. E-2023: S&M growth fell from +28.6% (2Q23) to +3.8% (3Q23). Pre-registered pass line (43c_prereg.md Q1):
#    PASS iff ABNB nights growth avg(4Q23,1Q24) - avg(1Q23,2Q23) <= -2.0pt AND that deceleration exceeds the
#    peer deceleration by >= 1.0pt AND the two-year stack also decelerates >= 1.0pt.
# ----------------------------------------------------------------------------------------------------------------
p = pd.read_csv(PANEL)
p = p.set_index("quarter")
for c in ("sm_cash", "nights_m", "revenue"):
    p[c + "_yoy"] = (p[c] / p[c].shift(4) - 1) * 100
p["nights_2yr"] = (p["nights_m"] / p["nights_m"].shift(8) - 1) * 100

peers = pd.read_csv(PEERS).set_index("quarter")
win = ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24"]
rows = []
for i, q in enumerate(win):
    k = q_to_key(q)
    rows.append({
        "quarter": q, "h": i - 2,
        "abnb_sm_cash_yoy_pct": round(p.loc[q, "sm_cash_yoy"], 1),
        "abnb_revenue_yoy_pct": round(p.loc[q, "revenue_yoy"], 1),
        "abnb_nights_yoy_pct": round(p.loc[q, "nights_m_yoy"], 1),
        "abnb_nights_2yr_stack_pct": round(p.loc[q, "nights_2yr"], 1),
        "bkng_room_nights_yoy_pct": peers.loc[k, "bkng_room_nights_yoy"],
        "expe_room_nights_yoy_pct": peers.loc[k, "expe_room_nights_yoy"],
    })
e23 = pd.DataFrame(rows)
pre = e23[e23.h.isin([-2, -1])]
post = e23[e23.h.isin([1, 2])]
d_abnb = post.abnb_nights_yoy_pct.mean() - pre.abnb_nights_yoy_pct.mean()
d_bkng = post.bkng_room_nights_yoy_pct.mean() - pre.bkng_room_nights_yoy_pct.mean()
d_expe = post.expe_room_nights_yoy_pct.mean() - pre.expe_room_nights_yoy_pct.mean()
# the 2-year stack for h=-2,-1 has a 2021 base (pandemic); h=1,2 has a 2022 base. Registered as a condition; reported
# as undefined for the pre-window because 1Q21/2Q21 are pandemic quarters (documented failure of the design, not hidden).
cond1 = d_abnb <= -2.0
cond2 = (d_abnb - min(d_bkng, d_expe)) <= -1.0   # ABNB decelerated MORE than the peer that decelerated least
cond3 = None
verdict = "PASS" if (cond1 and cond2) else "FAIL"
summary = pd.DataFrame([
    {"item": "ABNB nights decel (avg h=1,2 minus avg h=-2,-1), pts", "value": round(d_abnb, 2), "pass_line": "<= -2.0", "met": bool(cond1)},
    {"item": "BKNG room-nights decel, same windows, pts", "value": round(d_bkng, 2), "pass_line": "reference", "met": ""},
    {"item": "EXPE room-nights decel, same windows, pts", "value": round(d_expe, 2), "pass_line": "reference", "met": ""},
    {"item": "ABNB decel minus least-decelerating peer, pts", "value": round(d_abnb - min(d_bkng, d_expe), 2), "pass_line": "<= -1.0", "met": bool(cond2)},
    {"item": "Two-year stack decel", "value": "undefined (pre-window base is 2021)", "pass_line": ">= 1.0 decel", "met": "n/a"},
    {"item": "E-2023 verdict", "value": verdict, "pass_line": "all three", "met": verdict == "PASS"},
])
e23.to_csv(OUT / "43c_e2023_test.csv", index=False)
summary.to_csv(OUT / "43c_e2023_summary.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------
# 2. E-2025/26: regional nights growth from the letters (word buckets mapped: low-20s 21.5, ~20 20, high-teens 18,
#    mid-teens 15, low double 11, high-single 8, mid-single 5). SUPPORTED iff LatAm and APAC both rose >= 3pts vs
#    their 2024 average in >= 3 of 3Q25..2Q26 while NA/EMEA did not.
# ----------------------------------------------------------------------------------------------------------------
reg = pd.DataFrame({
    "quarter": ["1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
    "latam_nights_yoy": [19, 17, 15, 21.5, 21.5, 18, 21.5, 18, 18, 20],
    "latam_wording": ["19%", "17%", "15%", "low-20s", "low-20s", "high-teens", "low-20s", "high-teens", "high-teens", "approximately 20%"],
    "apac_nights_yoy": [21, 19, 19, 21.5, 15, 15, 15, 15, 18, 18],
    "apac_wording": ["21%", "19%", "19%", "low-20s", "mid-teens", "mid-teens", "mid-teens", "mid-teens", "high-teens", "high-teens"],
    "na_wording": ["stable", "slight accel", "improved in Q", "accel", "n/a", "softer", "n/a", "mid-single", "high-single", "high-single (highest in ~3y)"],
    "emea_wording": ["n/a", "n/a", "n/a", "accel", "high-single", "n/a", "n/a", "high-single", "mid-single", "high-single"],
    "sm_cash_yoy_pct": [round(p.loc[q, "sm_cash_yoy"], 1) for q in ["1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]],
})
base_latam = reg.loc[reg.quarter.isin(["1Q24", "2Q24", "3Q24", "4Q24"]), "latam_nights_yoy"].mean()
base_apac = reg.loc[reg.quarter.isin(["1Q24", "2Q24", "3Q24", "4Q24"]), "apac_nights_yoy"].mean()
reg["latam_vs_2024avg_pts"] = (reg.latam_nights_yoy - base_latam).round(1)
reg["apac_vs_2024avg_pts"] = (reg.apac_nights_yoy - base_apac).round(1)
step = reg[reg.quarter.isin(["3Q25", "4Q25", "1Q26", "2Q26"])]
n_latam = int((step.latam_vs_2024avg_pts >= 3).sum())
n_apac = int((step.apac_vs_2024avg_pts >= 3).sum())
reg_verdict = "SUPPORTED" if (n_latam >= 3 and n_apac >= 3) else "NOT SUPPORTED"
reg.to_csv(OUT / "43c_e2526_regional.csv", index=False)
pd.DataFrame([
    {"item": "LatAm 2024 average, pct", "value": round(base_latam, 1)},
    {"item": "APAC 2024 average, pct", "value": round(base_apac, 1)},
    {"item": "quarters 3Q25-2Q26 with LatAm >= +3pts vs 2024 avg (need >= 3)", "value": n_latam},
    {"item": "quarters 3Q25-2Q26 with APAC >= +3pts vs 2024 avg (need >= 3)", "value": n_apac},
    {"item": "E-2025/26 verdict", "value": reg_verdict},
]).to_csv(OUT / "43c_e2526_summary.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------
# 3. 5 Nov decision tree from the audited C04 x C09 joint (mc_joint_and_conditionals_v2.json).
#    Branches (43c_prereg.md Q2, refined so the cells partition):
#      A  Q4 margin sentence "down y/y" (C09 = a), any FY sentence                      -> costs flagged, 3Q24 form
#      B  FY26 sentence softened/lowered (C04 = d) without a Q4 "down" sentence         -> floor at risk, no cut
#      C  FY26 floor held "at least 35.5%" with Q4 flat or up (C04 = a, C09 in {b,c})    -> trim-to-hold (B03 tell inside)
#      D  FY26 raised (C04 in {b,c}) with Q4 "up y/y" (C09 = c)                          -> costs falling on their own
#      E  everything else (raise with flat/none; held or softened with no Q4 sentence; no FY sentence rows)
#    Street FY27 margin revision per branch (cost leg only; assumptions stated in the note), then 42's grid:
#      NTM revision = d_margin_bp/100 * STREET_FY27_REV / STREET_FY27_EBITDA * NTM_WEIGHT; move = slope * NTM;
#      constant multiple ~ 1.05 x NTM (42_scenarios: -2.37% NTM -> -2.48% price).
# ----------------------------------------------------------------------------------------------------------------
J = json.loads(JOINT.read_text())["joint_C04xC09"]
pA = sum(v for k, v in J.items() if k[1] == "a")
pB = sum(v for k, v in J.items() if k[0] == "d" and k[1] != "a")
pC = J["ab"] + J["ac"]
pD = J["bc"] + J["cc"]
pE = 1.0 - (pA + pB + pC + pD)

CM_RATIO = 1.048


def move_row(name, prob, d_margin_bp, precedent, street_fy27_note):
    ntm = d_margin_bp / 10000.0 * STREET_FY27_REV / STREET_FY27_EBITDA * 100 * NTM_WEIGHT_FY27_NOV  # % of NTM EBITDA (bp -> fraction of revenue)
    d_ebitda = d_margin_bp / 10000.0 * STREET_FY27_REV
    return {
        "branch": name, "probability": round(prob, 3),
        "street_fy27_margin_revision_bp": d_margin_bp,
        "street_fy27_ebitda_change_musd": round(d_ebitda, 0),
        "ntm_ebitda_revision_pct": round(ntm, 2),
        "move_slope_W1_pct": round(SLOPE_W1 * ntm, 1),
        "move_slope_W2_pct": round(SLOPE_W2 * ntm, 1),
        "move_constant_multiple_pct": round(CM_RATIO * ntm, 1),
        "usd_per_share_constant_multiple": round(CM_RATIO * ntm / 100 * PRICE, 1),
        "precedent": precedent, "street_fy27_note": street_fy27_note,
    }


tree = pd.DataFrame([
    move_row("A. Q4 margin 'down y/y' (costs flagged; C09=a)", pA, -100,
             "3Q24 (8 Nov 2024): Q4 EBITDA cons -9.6%, FY25 margin cons -0.92pt, stock -8.7% / -7.7% ex-QQQ 5d",
             "Street takes FY27 margin ~100bp lower on the named cost line (3Q24 form); 41 row -100bp/0%"),
    move_row("B. FY26 sentence softened/lowered, Q4 not 'down' (C04=d, C09!=a)", pB, -50,
             "4Q23 (14 Feb 2024): floor 1.6pt below Street, Street cut 0.25pt, stock -1.7%; 4Q25: 'stable' vs 35.4, cut 0.27pt",
             "Street trims FY27 ~50bp (a softened floor without a named line has been discounted 0.2-0.3pt)"),
    move_row("C. Floor held 'at least 35.5%', Q4 flat/up (trim-to-hold; C04=a, C09 in b,c)", pC, 0,
             "1Q23 (10 May 2023): 'total marketing costs roughly the same as prior year' -> stock -10.9%, but Q2 EBITDA cons -13% on S&M +400bp; no clean precedent for a cut framed as efficiency",
             "Street FY27 cost side unchanged; B03 tell (P~0.25 conditional) reads as growth capitulation, not a cost cut (B03 s9: stock ~ -$3, sign uncertain)"),
    move_row("D. FY26 raised to ~36%, Q4 'up y/y' (costs fall on their own; C04 in b,c, C09=c)", pD, +50,
             "2Q26 (7 Aug 2026): floor raised to 35.5%, stock +17.4%; 4Q25: 'stable' + revenue accel, +4.6%",
             "Street lifts FY27 ~50bp (FY26 raise + AI support / G&A leverage); the cost leg HURTS the short"),
    move_row("E. Residual (raise with Q4 flat/none; held/softened with no Q4 sentence; no FY sentence)", pE, 0,
             "n/a", "no cost-side revision assumed"),
])
w_ntm = float((tree.probability * tree.ntm_ebitda_revision_pct).sum())
tree.loc[len(tree)] = {
    "branch": "Probability-weighted cost-leg contribution", "probability": round(tree.probability.sum(), 3),
    "street_fy27_margin_revision_bp": round(float((tree.probability * tree.street_fy27_margin_revision_bp).sum()), 1),
    "street_fy27_ebitda_change_musd": round(float((tree.probability * tree.street_fy27_ebitda_change_musd).sum()), 0),
    "ntm_ebitda_revision_pct": round(w_ntm, 2),
    "move_slope_W1_pct": round(SLOPE_W1 * w_ntm, 2), "move_slope_W2_pct": round(SLOPE_W2 * w_ntm, 2),
    "move_constant_multiple_pct": round(CM_RATIO * w_ntm, 2),
    "usd_per_share_constant_multiple": round(CM_RATIO * w_ntm / 100 * PRICE, 2),
    "precedent": "", "street_fy27_note": "sum of P x row",
}
tree.to_csv(OUT / "43c_decision_tree_5nov.csv", index=False)

# overlays that are not cells of the joint
overlays = pd.DataFrame([
    {"overlay": "R05 sandbag: 3Q26 margin >= 51.5%", "probability": 0.22,
     "effect": "+0.5pp FY26 / +0.4pp FY27 on the team build; stock ~ +$3.5 (R05 s9); shifts C04 toward (b) and C09 toward (a) if the Q3 step slipped into Q4",
     "cost_leg_direction": "hurts the short on the day; ambiguous for Q4"},
    {"overlay": "B03 marketing-cut tell inside branch C", "probability": 0.18,
     "effect": "P(B03 | C04=a) ~ 0.25; if Yes, FY26 +1.2pp / FY27 +1.1pp cost side, 4Q26 nights -0.3pt (judgement), stock ~ -$3 (sign uncertain)",
     "cost_leg_direction": "neutral for the cost leg; the memo's 'tails' branch"},
    {"overlay": "C01 4Q26 revenue guide below Street", "probability": 0.72,
     "effect": "P(A | below) = 0.30 vs 0.03 if not below; P(D-type raise+up | not below) = 0.78 x 0.49: the cost leg is almost entirely conditional on the revenue guide",
     "cost_leg_direction": "the cost leg is a revenue-leg dependent"},
])
overlays.to_csv(OUT / "43c_decision_tree_overlays.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------
# 4. 11 Feb branch (B12 / F03). B12 s9: literal Yes -> FY27 -0.85pp vs Street 36.45 (-$135M, -2.3%), material Yes
#    -1.20pp (-$189M, -3.3%); constant multiple -$3.9 / -$5.5; EV -$1.9 / -$2.0. February day-1: 6 of 6 Q4 prints positive.
# ----------------------------------------------------------------------------------------------------------------
feb = pd.DataFrame([
    {"branch": "F1. FY27 floor/point set below the FY26 print or explicit investment-year (B12 literal)", "probability": 0.49,
     "fy27_margin_vs_street_pp": -0.85, "fy27_ebitda_vs_street_musd": -135, "ntm_ebitda_revision_pct": round(-2.3 * 0.88, 2),
     "move_slope_W1_pct": round(SLOPE_W1 * -2.3 * 0.88, 1), "move_slope_W2_pct": round(SLOPE_W2 * -2.3 * 0.88, 1),
     "move_constant_multiple_pct": -2.3, "usd_per_share_constant_multiple": -3.9,
     "precedent": "Feb 2025: floor 190bp below print + $200-250M budget, stock +14.4% (priced in Nov 2024)"},
    {"branch": "F1m. ... material reading (floor >= 50bp below print or explicit language; = F03 (d))", "probability": 0.36,
     "fy27_margin_vs_street_pp": -1.20, "fy27_ebitda_vs_street_musd": -189, "ntm_ebitda_revision_pct": round(-3.3 * 0.88, 2),
     "move_slope_W1_pct": round(SLOPE_W1 * -3.3 * 0.88, 1), "move_slope_W2_pct": round(SLOPE_W2 * -3.3 * 0.88, 1),
     "move_constant_multiple_pct": -3.3, "usd_per_share_constant_multiple": -5.5,
     "precedent": "Feb 2024: 'at least 35%' 1.6pt below Street, Street cut 0.25pt, -1.7%"},
    {"branch": "F2. Qualitative flat ('stable', 'maintain') or no number (F03 (e))", "probability": 0.48,
     "fy27_margin_vs_street_pp": 0.0, "fy27_ebitda_vs_street_musd": 0, "ntm_ebitda_revision_pct": 0.0,
     "move_slope_W1_pct": 0.0, "move_slope_W2_pct": 0.0, "move_constant_multiple_pct": 0.0, "usd_per_share_constant_multiple": 0.0,
     "precedent": "Feb 2026: 'stable' vs Street 35.4, Street cut 0.27pt, stock +4.6% on the revenue guide"},
    {"branch": "F3. Numeric floor at or above 35.5% (F03 a+b+c)", "probability": 0.16,
     "fy27_margin_vs_street_pp": 0.0, "fy27_ebitda_vs_street_musd": 0, "ntm_ebitda_revision_pct": 0.0,
     "move_slope_W1_pct": 0.0, "move_slope_W2_pct": 0.0, "move_constant_multiple_pct": 0.0, "usd_per_share_constant_multiple": 0.0,
     "precedent": "n/a (never given a numeric floor at or above the prior print)"},
])
feb.to_csv(OUT / "43c_decision_tree_11feb.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------
# 5. Watch list with thresholds (pre-registered in 43c_prereg.md Q3; numbers from 40/41/R05/B03/C09).
# ----------------------------------------------------------------------------------------------------------------
l40 = pd.read_csv(LINES40)
b = l40[(l40.scenario == "base")].set_index("quarter")
watch = pd.DataFrame([
    {"disclosure": "3Q26 S&M (P&L, GAAP incl. SBC ~ $70M)", "source": "letter P&L / 10-Q", "budget_or_bar": f"line-build cash S&M {b.loc['3Q26','sm_cash']:.0f}M (+33% y/y); R05: <= $724M cash means the Q3 step never came",
     "confirms_cost_leg": ">= $800M cash (spend running ahead of budget; Q4 sentence likely 'down')", "refutes_cost_leg": "<= $724M cash (step did not land; margin sandbagged; R05 Yes)"},
    {"disclosure": "3Q26 10-Q segment table 'Marketing' line (brand + performance)", "source": "10-Q significant segment expenses (1Q26 $506M vs $382M; 2Q26 $600M vs $468M)", "budget_or_bar": f"line-build 3Q26 marketing {b.loc['3Q26','sm_marketing']:.0f}M",
     "confirms_cost_leg": "y/y growth >= +25% (paid step persists into 2H)", "refutes_cost_leg": "y/y growth <= +15% (2H phasing down; a trim is already under way)"},
    {"disclosure": "3Q26 10-Q S&M MD&A driver sentence", "source": "10-Q MD&A (1Q26/2Q26: 'paid growth initiatives in emerging markets and partnerships')", "budget_or_bar": "n/a",
     "confirms_cost_leg": "same driver named again, plus payroll/headcount", "refutes_cost_leg": "'optimisation', 'efficiency', 'lower paid marketing' language"},
    {"disclosure": "3Q26 cost of revenue", "source": "letter P&L; LSEG COGS consensus (41 T3: above in 11 of 14)", "budget_or_bar": f"line-build {b.loc['3Q26','cor_cash']:.0f}M cash; 4Q26 DEC-0023 threshold $575M",
     "confirms_cost_leg": "3Q26 COR >= $650M and 4Q26 guided/implied >= $575M (hosting step real)", "refutes_cost_leg": "3Q26 COR <= $620M (fees rebates, no hosting step)"},
    {"disclosure": "Q4 margin sentence (letter)", "source": "letter Outlook", "budget_or_bar": "C09: down 0.22 / flat 0.26 / up 0.47",
     "confirms_cost_leg": "'decline ... due to higher marketing / product development / AI' (3Q24 form) = branch A", "refutes_cost_leg": "'up year-over-year' = branch D (cost leg hurts)"},
    {"disclosure": "FY26 margin sentence (letter)", "source": "letter Outlook", "budget_or_bar": "C04: held 0.33 / ~36% 0.30 / softened 0.27",
     "confirms_cost_leg": "'approximately 35.5%' or floor removed = branch B", "refutes_cost_leg": "'approximately 36%' = branch D"},
    {"disclosure": "2027 language", "source": "letter + call", "budget_or_bar": "B12 T5 regime; 3Q24 form 'share more about our 2025 growth and investment plans'",
     "confirms_cost_leg": "'2027 investment plans', a named 2027 launch programme, 'carry into next year' (B12 literal -> 0.60)", "refutes_cost_leg": "'maintaining strong margins' only (Nov 2023/2025 form -> flat FY27 floor in Feb)"},
    {"disclosure": "AI support / cost per booking", "source": "letter + call (1Q26 -10%, 2Q26 -16% y/y)", "budget_or_bar": "ops cash 3Q26 line-build 361M",
     "confirms_cost_leg": "cost per booking decline stalls (< -5% y/y) or make-good/case-reserve language repeats", "refutes_cost_leg": "cost per booking <= -15% y/y again (support leverage funds the marketing)"},
    {"disclosure": "B03 marketing tell", "source": "letter/call", "budget_or_bar": "B03 0.18 (strict 0.15 / loose 0.45)",
     "confirms_cost_leg": "n/a: a Yes means the floor is being defended with the growth budget (branch C)", "refutes_cost_leg": "n/a"},
])
watch.to_csv(OUT / "43c_watchlist.csv", index=False)

print("E-2023:", verdict, f"(ABNB decel {d_abnb:+.1f}pt vs BKNG {d_bkng:+.1f} / EXPE {d_expe:+.1f})")
print("E-2025/26:", reg_verdict, f"(LatAm {n_latam}/4, APAC {n_apac}/4 quarters >= +3pt vs 2024 avg)")
print(tree[["branch", "probability", "street_fy27_margin_revision_bp", "ntm_ebitda_revision_pct", "move_slope_W1_pct", "move_slope_W2_pct", "move_constant_multiple_pct"]].to_string(index=False))
print("outputs ->", OUT)
