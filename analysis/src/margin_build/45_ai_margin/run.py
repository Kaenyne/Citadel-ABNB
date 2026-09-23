"""
45_ai_margin: does AI rescue the Street's FY27 margin? What AI already does in our cost build, what it has saved in the filings, a
generous AI bull case, the cost growth Airbnb would need to hold the Street's margin and EBITDA on our revenue, and a FY27 grid of
revenue paths x cost cases with the price on the 43b multiple convention.

Run:  py -3.13 analysis/src/margin_build/45_ai_margin/run.py   (exit 0; writes data/processed/margin_build/45_ai_margin/ only)

Reuses the 44_short_case_v2 copy of the 40_line_build engine (params, actuals, build()) unchanged, so COR and ops re-key to each revenue
path's GBV, nights and bookings. Cost cases are FY27 adjustments on top of the line build. Cost measure for Street comparisons:
revenue - adjusted EBITDA (as in 41). Street = LSEG 11 Sep 2026 (FY27 revenue $15,819M, EBITDA $5,766M; a 23 Sep re-pull gave
$15,818M / $5,763M). No fitted parameters.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
PAN = ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv"
PATH = ROOT / "data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv"
PATH_ANNUAL = ROOT / "data/processed/margin_build/06_fy27_path_v2/06_annual_fy26_fy28_v2b.csv"
M7 = ROOT / "data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv"
RUN23 = ROOT / "data/processed/margin_build/23_final_model/23_lines_quarterly.csv"
OUT = ROOT / "data/processed/margin_build/45_ai_margin"; OUT.mkdir(parents=True, exist_ok=True)
V40 = ROOT / "data/processed/margin_build/40_line_build"

Q_ORDER = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
PREV = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26", "3Q27": "3Q26", "4Q27": "4Q26"}
QN = {q: int(q[0]) for q in Q_ORDER}
# 2023-25 mean quarterly shares of each cash line's FY total (WS02 02_seasonality.csv, share_mean_2023_25)
SHARE = {"pd": {1: .2548, 2: .2466, 3: .2459, 4: .2527}, "sm": {1: .2397, 2: .2703, 3: .2370, 4: .2530}, "ga": {1: .2386, 2: .2600, 3: .2456, 4: .2558}}
H2 = {k: v[3] + v[4] for k, v in SHARE.items()}
# quarterly merchant-fee rate relative to the annual rate, mean of 2024 and 2025 (fees = cost of revenue less chargebacks, hosting, other/night)
FEE_FACTOR = {1: 0.90, 2: 1.045, 3: 1.035, 4: 1.033}

# ----------------------------------------------------------------------------------------------------------------------
# 1. Parameters (name, base, bear, bull, unit, source). bear/bull are the adverse/favourable COST values.
# ----------------------------------------------------------------------------------------------------------------------
P = []
def prm(line, name, base, unit, source, bear=None, bull=None):
    P.append(dict(line=line, name=name, base=base, bear=base if bear is None else bear, bull=base if bull is None else bull, unit=unit, source=source))

prm("volume", "nights_per_booking_fy26", 3.65, "nights per booking", "WS02 nights_per_booking_fy 3.9 (2023), 3.8 (2024), 3.7 (2025); trend continued")
prm("volume", "nights_per_booking_fy27", 3.60, "nights per booking", "same trend")
# cost of revenue = merchant fees (% GBV, seasonal) + chargebacks (per booking) + hosting (schedule) + other (per night)
prm("cor", "merchant_fee_pct_gbv", 1.70, "% of GBV, annual-equivalent rate", "FY24 1.69%, FY25 1.76% (cost of revenue less chargebacks, hosting, other per night; 07_cost_components payment processing $1,665M incl. $67M chargebacks); 1H26 fits 1.68% annual-equivalent after 'higher payment processor rebates and incentives' (1Q26 10-Q). Base 1.70 = rebates persist, do not widen.", bear=1.76, bull=1.64)
prm("cor", "chargeback_per_booking", 0.72, "USD per booking", "FY25 $67M / 144M bookings = $0.47; 1H26 +$12M and +$13M y/y (10-Q MD&A) implies ~$0.72 on 1H26 bookings; held flat", bear=0.85, bull=0.60)
prm("cor", "hosting_fy25", 224.0, "USD m per year", "Run-rate of the $672M hosting commitment through 2027 in the FY24 10-K (~$224M a year); FY25 10-K re-cut to $1.7bn through 2031 (~$283M a year)")
prm("cor", "hosting_step_2h26", 30.0, "USD m per half vs 2H25", "1H26 server costs +$12M y/y (2Q26 10-Q) and reserved-instance amortisation +$12-15M (WS05 H14); Mertz 2Q26 'a material increase in AI spend' ramping in 2H", bear=45.0, bull=20.0)
prm("cor", "hosting_fy27", 330.0, "USD m per year", "Between the old run-rate ($224M) and the new commitment ($283M a year) plus the unsized AI inference ramp; WS05 H03 total purchase obligations ~$465M a year in 2027-28", bear=400.0, bull=290.0)
prm("cor", "cor_other_per_night", 0.36, "USD per night", "FY25 residual: 2,086 - 1,598 fees - 67 chargebacks - 224 hosting = $197M on 533M nights (AirCover claims, payment operations)")
prm("cor", "xborder_fee_bp_per_pt", 1.0, "bp of GBV per +1pt non-NA revenue share", "Cross-border card volume carries higher interchange and FX cost; non-NA share of revenue 2Q26 55.8% vs 55.5% 2Q25 (WS02). Small at current drift.")
# operations & support: same quarter last year per booking, moved by a variable part (mgmt's support cost per booking) and a fixed part
prm("ops", "ops_variable_share", 0.215, "share of the line that behaves like mgmt's 'support cost per booking'", "Calibrated on 1H26 with the rule itself: ops 1H26/1H25 = 624/591 = 1.056 = v x (1 - 0.13) x 1.112 (bookings) + (1 - v) x 1.08 -> v = 0.215; mgmt's metric fell -10% (1Q26) and -16% (2Q26). Consistent with the metric being third-party contact cost (13,000 contingent workers, FY25 10-K), not the whole line.", bear=0.17, bull=0.27)
prm("ops", "ops_variable_decline_2h26", -14.0, "% y/y per booking, 2H26", "Support cost per booking -10% (1Q26 call), -16% (2Q26 call); >40% of issues resolved without an agent", bear=-8.0, bull=-18.0)
prm("ops", "ops_variable_decline_fy27", -10.0, "% y/y per booking, FY27", "Chesky 4Q25/2Q26: 'continue to decline' as AI moves to voice; no number (31a: medium confidence)", bear=-4.0, bull=-14.0)
prm("ops", "ops_fixed_growth", 8.0, "% y/y, the non-variable part", "1H26 10-Q: payroll +$14M/+$27M, customer relations +$3M/+$10M, insurance +$7M; headcount +12% in 2025 slowing", bear=11.0, bull=6.0)
# product development
prm("pd", "pd_growth_2h26", 9.0, "% y/y, 2H26", "1H26 +12% / +10%, all payroll from average headcount (10-Q); headcount growth below FY25's +12% (2Q26 call)", bear=11.0, bull=7.0)
prm("pd", "pd_growth_fy27", 8.0, "% y/y, FY27", "Headcount ~+5% plus ~3% comp; 31b took 9.5%", bear=10.0, bull=6.0)
prm("pd", "pd_ai_tooling_fy27", 30.0, "USD m, FY27 incremental", "The engineering-tools part of the unsized 'material increase in AI spend'; judgement", bear=60.0, bull=15.0)
# sales & marketing = brand + performance marketing (10-K split) + field operations & policy cash (incl. S&M payroll)
prm("sm", "marketing_fy25", 1595.0, "USD m", "FY25 10-K S&M split: brand and performance marketing $1,595M")
prm("sm", "marketing_1h_share", 0.51, "1H share of FY marketing", "2023-25 mean S&M quarterly shares Q1 24.0% + Q2 27.0% (02_seasonality)")
prm("sm", "marketing_growth_1h26", 32.0, "% y/y, 1H26 (reported)", "10-Q: marketing spend +$126M (1Q26) and +$132M (2Q26), 'paid growth initiatives in emerging markets and partnerships' = +$258M on ~$813M")
prm("sm", "marketing_growth_2h26", 25.0, "% y/y, 2H26", "2Q26 call: 'some incremental investment ... in sales and marketing' in 2H; Sep 2026 Goldman (WS05 V022-V026): marketing stays elevated into next year's launches. 1H26 ran +32%; 31b took +21% for 2H. Base 25 = partial deceleration.", bear=32.0, bull=18.0)
prm("sm", "marketing_growth_fy27", 15.0, "% y/y, FY27", "Expansion-market spend grows while core markets lever ('relative floor', 2Q26); 31b 15%", bear=22.0, bull=10.0)
prm("sm", "field_cash_fy25", 781.0, "USD m", "FY25 10-K field operations and policy $993M less S&M SBC $212M (WS02) = cash $781M; includes the ~$200M new-businesses launch spend")
prm("sm", "field_growth_fy26", 18.0, "% y/y", "1H26 S&M payroll +$42M/+$48M (10-Q) of which ~$26M SBC; 1H26 implied field cash +$88M (+21%); FY25 grew 43%; 31b 18%", bear=22.0, bull=14.0)
prm("sm", "field_growth_fy27", 11.0, "% y/y", "Services/Experiences launch spend laps (Chesky: each new business cheaper to launch); 31b 13%", bear=16.0, bull=8.0)
# reconciliation of 2H26 to management's 3Q26 margin sentence
prm("recon", "reconcile_to_sentence", 1.0, "1 = on, 0 = evidence-only build", "Management's quarterly margin sentence has not been sandbagged (WS22 group A: realised gap to the sentence mean -0.19pp, above in 4 of 10, W2), so the 2H26 cost budget is anchored to it; the un-reconciled build is kept as scenario evidence_only")
prm("recon", "guide_3q26_revenue_mid", 4730.0, "USD m", "6 Aug 2026 guide $4,690-4,770M (02_guidance_ledger)")
prm("recon", "sentence_3q26_margin_delta_pp", -0.5, "pp y/y", "'Adjusted EBITDA margin down slightly vs 3Q25' (6 Aug 2026); 'slightly' has meant 0.8-1.5pp in past quarters (M3), base -0.5", bear=-1.0, bull=0.0)
prm("recon", "recon_share_to_marketing", 0.70, "share of the cost gap assigned to 2H26 marketing", "Management named S&M ('some incremental investment') and AI spend ('material increase') as the 2H26 step-ups; the rest of the gap goes to hosting/AI in cost of revenue")
# G&A ex lodging-tax reserves
prm("ga", "ga_growth_2h26", 5.0, "% y/y, 2H26 (ex reserves)", "1H26 -5.4% because non-income taxes fell $38M; underlying payroll +$32M in 2Q26 alone (10-Q); 'extremely disciplined' (2Q26)", bear=8.0, bull=2.0)
prm("ga", "ga_growth_fy27", 5.0, "% y/y, FY27", "31b 5%; highest fixed share of any line", bear=8.0, bull=3.0)
prm("ga", "lodging_reserves_fwd", 0.0, "USD m per quarter (added back)", "None assumed; 4Q25's $81M was a one-off")
# RNPL / short-case overlays (0 in base; set by the short case)
prm("overlay", "rnpl_ops_uplift_pct", 0.0, "% uplift on ops & support per completed booking", "Cancellations raise contacts, refunds and make-goods per completed stay: 2Q26 10-Q customer relations +$10M on higher make-good payouts and related case reserves, 1Q26 +$3M refunds and credits; short case 4%")
prm("overlay", "chargeback_add_per_booking", 0.0, "USD per booking added", "1H26 chargebacks +$25M y/y (+37%) after two years of declines; short case +$0.15")
prm("overlay", "q4_marketing_cut_musd", 0.0, "USD m cut from 4Q26 marketing", "Management protected the FY floor in 4Q24 by phasing brand marketing down; the short case reports the cut needed")
# below EBITDA (M7 rules)
m7 = pd.read_csv(M7).set_index("name")["value"]
prm("below", "da_per_q", float(m7["da_musd_q"]), "USD m per quarter", "M7 parameter sheet")
prm("below", "sbc_growth", float(m7["sbc_yoy_growth"]) * 100, "% y/y on SBC[q-4]", "M7 (recency-weighted last-4 y/y); mgmt: SBC growth below FY25's")
prm("below", "interest_income_beta", float(m7["interest_income_beta"]), "x 3m T-bill x avg earning base / 4", "M7 / WS04 rule (r 0.83, n 18)")
prm("below", "tbill_3m", 3.76, "% (3Q26 QTD average, held)", "FRED DTB3 via M7")
prm("below", "cash_plus_sti", 12069.0, "USD m, held flat", "WS02 2Q26")
prm("below", "rnpl_share_shift_pts", 0.0, "pts of GBV paid at check-in rather than at booking, vs 2025", "No RNPL share series exists in the repo; sensitivity only: each 10 pts of GBV paid later cuts average funds held by ~10%", bear=10.0, bull=0.0)
prm("below", "interest_expense_per_q", 37.0, "USD m per quarter", "M7: $2.5bn notes (~$119M a year, WS05 H10)")
prm("below", "other_income_per_q", 3.7, "USD m per quarter", "M7 recency-weighted mean")
prm("below", "etr_2h26", 18.0, "% applied to 2H26 forecast quarters (1H26 printed 17.1%)", "M7; mgmt high teens (2Q26)")
prm("below", "etr_fy27", 17.5, "%", "M7; long-term mid-to-high teens under OBBBA (WS05 H09)")
prm("below", "diluted_shares_2q26", 597.0, "m", "WS02 2Q26")
prm("below", "diluted_shares_delta_per_q", float(m7["diluted_shares_delta_m_q"]), "m per quarter", "M7: -buyback/price + issuance; authorisation runs out ~1Q27 (WS05 H11)")
params = pd.DataFrame(P); params.to_csv(OUT / "45_params_inherited.csv", index=False)
PV = {s: params.set_index("name")[s].to_dict() for s in ("base", "bear", "bull")}

# ----------------------------------------------------------------------------------------------------------------------
# 2. Actuals and the revenue path
# ----------------------------------------------------------------------------------------------------------------------
pan = pd.read_csv(PAN).set_index("quarter")
path = pd.read_csv(PATH)
path = path[path.line.isin(["nights_mm", "gbv_busd", "revenue_musd"])].pivot_table(index=["scenario", "quarter"], columns="line", values="value")
ann_path = pd.read_csv(PATH_ANNUAL)
NPB_ACT = {"3Q25": 3.7, "4Q25": 3.7, "1Q26": 3.65, "2Q26": 3.65}
non_na = lambda q: 1 - pan.loc[q, "rev_na"] / pan.loc[q, "revenue"]

# ----------------------------------------------------------------------------------------------------------------------
# 3. The build
# ----------------------------------------------------------------------------------------------------------------------
def build(rev_scn: str = "base", cost_scn: str = "base", override: dict | None = None, path_override: pd.DataFrame | None = None) -> pd.DataFrame:
    p = dict(PV[cost_scn]); p.update(override or {})
    mkt_1h26 = p["marketing_fy25"] * p["marketing_1h_share"] * (1 + p["marketing_growth_1h26"] / 100)
    mkt_2h26 = p["marketing_fy25"] * (1 - p["marketing_1h_share"]) * (1 + p["marketing_growth_2h26"] / 100)
    mkt_fy27 = (mkt_1h26 + mkt_2h26) * (1 + p["marketing_growth_fy27"] / 100)
    sm_1h26 = float(pan.loc["1Q26", "sm_cash"] + pan.loc["2Q26", "sm_cash"])
    fld_1h26 = sm_1h26 - mkt_1h26
    fld_fy26 = p["field_cash_fy25"] * (1 + p["field_growth_fy26"] / 100); fld_2h26 = fld_fy26 - fld_1h26
    fld_fy27 = fld_fy26 * (1 + p["field_growth_fy27"] / 100)
    pd_2h26 = float(pan.loc["3Q25", "pd_cash"] + pan.loc["4Q25", "pd_cash"]) * (1 + p["pd_growth_2h26"] / 100)
    pd_fy27 = (float(pan.loc["1Q26", "pd_cash"] + pan.loc["2Q26", "pd_cash"]) + pd_2h26) * (1 + p["pd_growth_fy27"] / 100) + p["pd_ai_tooling_fy27"]
    ga_2h26 = float(pan.loc["3Q25", "ga_cash_ex_lodging"] + pan.loc["4Q25", "ga_cash_ex_lodging"]) * (1 + p["ga_growth_2h26"] / 100)
    ga_fy27 = (float(pan.loc["1Q26", "ga_cash_ex_lodging"] + pan.loc["2Q26", "ga_cash_ex_lodging"]) + ga_2h26) * (1 + p["ga_growth_fy27"] / 100)
    xb_drift_pts = (non_na("2Q26") - non_na("2Q25")) * 100
    hosting_step = p["hosting_step_2h26"]
    recon_gap = 0.0
    if p["reconcile_to_sentence"] >= 0.5:
        # evidence-only 3Q26 cash costs at the GUIDE revenue midpoint's drivers (use the path's 3Q26 nights/GBV, which sit inside the guide ranges)
        r3 = path.loc[("base", "3Q26")]; n3, g3 = float(r3["nights_mm"]), float(r3["gbv_busd"]); b3 = n3 / p["nights_per_booking_fy26"]
        fee3 = (p["merchant_fee_pct_gbv"] + p["xborder_fee_bp_per_pt"] * xb_drift_pts / 100) * FEE_FACTOR[3] / 100 * g3 * 1000
        cor3 = fee3 + p["chargeback_per_booking"] * b3 + (p["hosting_fy25"] / 2 + hosting_step) / 2 + p["cor_other_per_night"] * n3
        ops3 = float(pan.loc["3Q25", "ops_cash"]) * (p["ops_variable_share"] * (1 + p["ops_variable_decline_2h26"] / 100) * b3 / (float(pan.loc["3Q25", "nights_m"]) / 3.7) + (1 - p["ops_variable_share"]) * (1 + p["ops_fixed_growth"] / 100))
        pd3 = pd_2h26 * SHARE["pd"][3] / H2["pd"]; sm3 = (mkt_2h26 + fld_2h26) * SHARE["sm"][3] / H2["sm"]; ga3 = ga_2h26 * SHARE["ga"][3] / H2["ga"] + p["lodging_reserves_fwd"]
        evidence_costs3 = cor3 + ops3 + pd3 + sm3 + ga3
        target_margin = float(pan.loc["3Q25", "adj_ebitda_margin_pct"]) + p["sentence_3q26_margin_delta_pp"]
        budget3 = p["guide_3q26_revenue_mid"] * (1 - target_margin / 100) + p["da_per_q"] + p["lodging_reserves_fwd"]
        recon_gap = max(0.0, budget3 - evidence_costs3)
        # The marketing part is a 3Q26 timing step (campaign / launch spend named for the quarter); loading it into 4Q26 as well would put FY26
        # below the 35.5% floor at guide revenue, which management has never missed. The hosting/AI part is a run-rate step and stays in 4Q26 and FY27.
        mkt_q3_step = recon_gap * p["recon_share_to_marketing"]
        hosting_step += recon_gap * (1 - p["recon_share_to_marketing"]) * 2                     # per half; 3Q26 and 4Q26 each get their share
        mkt_fy27 = (mkt_1h26 + mkt_2h26 + mkt_q3_step) * (1 + p["marketing_growth_fy27"] / 100)
    else:
        mkt_q3_step = 0.0
    hist = {q: dict(ops=float(pan.loc[q, "ops_cash"]), bookings=float(pan.loc[q, "nights_m"]) / NPB_ACT[q], sbc=float(pan.loc[q, "sbc_total_is"]),
                    fh=float(pan.loc[q, "funds_held_on_behalf"]), gbv=float(pan.loc[q, "gbv_busd"])) for q in NPB_ACT}
    fh_last = hist["2Q26"]["fh"] * (1 - p["rnpl_share_shift_pts"] / 100)   # preceding quarter's (shifted) balance, for the average earning base
    shares = p["diluted_shares_2q26"]; rows = []
    for q in Q_ORDER:
        is27 = q.endswith("27"); qn = QN[q]; pq = PREV[q]
        r = path_override.loc[q] if path_override is not None else path.loc[(rev_scn, q)]; rev, nights, gbv = float(r["revenue_musd"]), float(r["nights_mm"]), float(r["gbv_busd"])
        bookings = nights / (p["nights_per_booking_fy27"] if is27 else p["nights_per_booking_fy26"])
        # cost of revenue
        fee_rate = (p["merchant_fee_pct_gbv"] + p["xborder_fee_bp_per_pt"] * xb_drift_pts / 100) * FEE_FACTOR[qn]
        fees = fee_rate / 100 * gbv * 1000
        chargebacks = (p["chargeback_per_booking"] + p["chargeback_add_per_booking"]) * bookings
        hosting = (p["hosting_fy27"] + max(0.0, 2 * (hosting_step - p["hosting_step_2h26"]))) / 4 if is27 else (p["hosting_fy25"] / 2 + hosting_step) / 2
        cor_other = p["cor_other_per_night"] * nights
        cor = fees + chargebacks + hosting + cor_other
        # operations & support
        d_var = p["ops_variable_decline_fy27"] if is27 else p["ops_variable_decline_2h26"]
        v = p["ops_variable_share"]
        ops_var = hist[pq]["ops"] * v * (1 + d_var / 100) * bookings / hist[pq]["bookings"]
        ops_fix = hist[pq]["ops"] * (1 - v) * (1 + p["ops_fixed_growth"] / 100)
        ops_pre = ops_var + ops_fix                                            # C-04: unoverlaid ops carried in the history
        ops = ops_pre * (1 + p["rnpl_ops_uplift_pct"] / 100)
        # product development, S&M, G&A: FY (or 2H) view spread on the 2023-25 quarterly shares
        pdv = pd_fy27 * SHARE["pd"][qn] if is27 else pd_2h26 * SHARE["pd"][qn] / H2["pd"]
        mkt = mkt_fy27 * SHARE["sm"][qn] if is27 else mkt_2h26 * SHARE["sm"][qn] / H2["sm"] + (mkt_q3_step if qn == 3 else 0.0) - (p["q4_marketing_cut_musd"] if q == "4Q26" else 0.0)
        fld = fld_fy27 * SHARE["sm"][qn] if is27 else fld_2h26 * SHARE["sm"][qn] / H2["sm"]
        sm = mkt + fld
        ga_ex = ga_fy27 * SHARE["ga"][qn] if is27 else ga_2h26 * SHARE["ga"][qn] / H2["ga"]
        lodging = p["lodging_reserves_fwd"]; ga = ga_ex + lodging
        da = p["da_per_q"]; cash_costs = cor + ops + pdv + sm + ga
        ebitda = rev - cash_costs + da + lodging; margin = ebitda / rev * 100
        # below EBITDA
        sbc = hist[pq]["sbc"] * (1 + p["sbc_growth"] / 100)
        op_inc = ebitda - da - sbc - lodging
        fh_unshifted = hist[pq]["fh"] * (gbv / hist[pq]["gbv"])                 # same quarter last year x GBV growth (M7 rule), unshifted path
        fh = fh_unshifted * (1 - p["rnpl_share_shift_pts"] / 100)               # RNPL level shift applied once, never compounded
        int_inc = p["interest_income_beta"] * p["tbill_3m"] / 100 * (p["cash_plus_sti"] + (fh + fh_last) / 2) / 4   # average of this and the preceding quarter (M7)
        fh_last = fh
        pretax = op_inc + int_inc - p["interest_expense_per_q"] + p["other_income_per_q"]
        etr = p["etr_fy27"] if is27 else p["etr_2h26"]; ni = pretax * (1 - etr / 100)
        shares += p["diluted_shares_delta_per_q"]; eps = ni / shares
        hist[q] = dict(ops=ops_pre, bookings=bookings, sbc=sbc, fh=fh_unshifted, gbv=gbv)
        rows.append(dict(quarter=q, rev_scenario=rev_scn, cost_scenario=cost_scn, revenue=rev, nights_m=nights, gbv_busd=gbv, bookings_m=bookings,
                         cor_fees=fees, cor_chargebacks=chargebacks, cor_hosting=hosting, cor_other=cor_other, cor_cash=cor, merchant_fee_rate_q_pct=fee_rate,
                         ops_variable=ops_var, ops_fixed=ops_fix, ops_cash=ops, ops_per_booking=ops / bookings,
                         pd_cash=pdv, sm_marketing=mkt, sm_field=fld, sm_cash=sm, ga_cash_ex_lodging=ga_ex, lodging_reserves=lodging, ga_cash=ga,
                         total_cash_costs=cash_costs, da=da, adj_ebitda=ebitda, adj_ebitda_margin_pct=margin, recon_gap_3q26_musd=recon_gap,
                         sbc=sbc, op_income=op_inc, interest_income=int_inc, interest_expense=p["interest_expense_per_q"], other_income=p["other_income_per_q"],
                         pretax=pretax, tax=pretax - ni, etr_pct=etr, net_income=ni, diluted_shares_m=shares, eps=eps))
    df = pd.DataFrame(rows).set_index("quarter")
    for line in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "total_cash_costs", "adj_ebitda", "eps"]:
        col = {"adj_ebitda": "adj_ebitda_reported", "eps": "eps_diluted"}.get(line, line)
        prev = [float(pan.loc[PREV[q], col]) if PREV[q] in pan.index else float(df.loc[PREV[q], line]) for q in df.index]
        df[line + "_yoy_pct"] = (df[line].values / np.array(prev) - 1) * 100
        if line != "eps":
            df[line + "_pct_rev"] = df[line] / df["revenue"] * 100
    return df.reset_index()



# ======================================================================================================================
# 45. AI and the FY27 margin
# ======================================================================================================================
from openpyxl import load_workbook

Q26H2 = ["3Q26", "4Q26"]; Q27 = ["1Q27", "2Q27", "3Q27", "4Q27"]; H1Q = ["1Q26", "2Q26"]
h1 = pan.loc[H1Q]
CASH = ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]
K_FLEX = 0.364                  # M6 cash-cost elasticity to revenue (t 6.58, n 18), used by 43b
SPOT, SHARES, NET_CASH, M_SPOT, SLOPE, G_STREET = 166.84, 597.0, 9593.0, 15.61, 0.486, 11.49   # 43b convention
SM_STREET_RESIDUAL = 3328.46   # C4 dossier / 43b: Street FY27 EBITDA implies this S&M on our other four lines

cur = pd.read_csv(ROOT / "data/processed/margin_build/03_consensus_pit/03_current_consensus.csv"); cur = cur[cur.vendor == "LSEG"].set_index("period")
ST = {p: dict(rev=float(cur.loc[p, "revenue_mean"]), ebitda=float(cur.loc[p, "ebitda_mean"]), cogs=float(cur.loc[p, "cogs_mean"])) for p in ["FY26", "FY27"]}
for p in ST: ST[p]["costs"] = ST[p]["rev"] - ST[p]["ebitda"]
ST_M27 = ST["FY27"]["ebitda"] / ST["FY27"]["rev"]

# ---- revenue paths --------------------------------------------------------------------------------------------------
def official_path() -> pd.DataFrame:
    ws = load_workbook(ROOT / "model/ABNB_official_model_complete.xlsx", read_only=True, data_only=True)["Income_Statement"]
    rows = {r: [ws.cell(r, c).value for c in range(1, 30)] for r in range(1, 40)}
    col = {h[:4]: i for i, h in enumerate(rows[4]) if isinstance(h, str) and h.endswith("E")}
    lab = {str(v[0]).strip(): r for r, v in rows.items() if v[0]}
    rn = next(r for k, r in lab.items() if k.startswith("Nights"))
    rg = next(r for k, r in lab.items() if k.startswith("Gross booking value"))   # already $bn
    rr = next(r for k, r in lab.items() if k.startswith("Revenue"))
    return pd.DataFrame({q: dict(revenue_musd=float(rows[rr][i]), nights_mm=float(rows[rn][i]), gbv_busd=float(rows[rg][i])) for q, i in col.items()}).T
short = pd.read_csv(ROOT / "data/processed/margin_build/44_short_case_v2/40_short_case_revenue_path.csv").set_index("quarter")[["revenue_musd", "nights_mm", "gbv_busd"]]
PATHS = {"line-build base (~Street revenue)": None, "official v2": official_path(), "short case v44": short}

def fy(d, qs, col): return float(d.loc[qs, col].sum())
res, ledger_rows = [], []
for pname, po in PATHS.items():
    d = build(path_override=po).set_index("quarter")
    rev26 = float(h1.revenue.sum()) + fy(d, Q26H2, "revenue"); rev27 = fy(d, Q27, "revenue")
    lines27 = {c: fy(d, Q27, c) for c in CASH}; da27 = fy(d, Q27, "da")
    pd26 = float(h1.pd_cash.sum()) + fy(d, Q26H2, "pd_cash"); ga26 = float(h1.ga_cash_ex_lodging.sum()) + fy(d, Q26H2, "ga_cash")
    costs26_ours = rev26 - (float(h1.adj_ebitda_reported.sum()) + fy(d, Q26H2, "adj_ebitda"))
    # AI bull pieces (FY27): whole ops & support line per booking -10% y/y; PD +5% (tooling kept); G&A +3%; hosting $340M (B08, DEC-0023)
    prev = {"1Q27": ("1Q26", True), "2Q27": ("2Q26", True), "3Q27": ("3Q26", False), "4Q27": ("4Q26", False)}
    ops_bull = 0.0
    for q in Q27:
        pq, act = prev[q]
        pops = float(pan.loc[pq, "ops_cash"]) if act else float(d.loc[pq, "ops_cash"])
        pbk = float(pan.loc[pq, "nights_m"]) / 3.65 if act else float(d.loc[pq, "bookings_m"])
        ops_bull += pops * float(d.loc[q, "bookings_m"]) / pbk * 0.90
    adj = {
        "d_ops_ai_bull": ops_bull - lines27["ops_cash"],
        "d_pd_ai_bull": pd26 * 1.05 + 30.0 - lines27["pd_cash"],
        "d_ga_ai_bull": ga26 * 1.03 - lines27["ga_cash"],
        "d_hosting_ai_bull": 340.0 - fy(d, Q27, "cor_hosting"),
        "d_sm_to_street_residual": SM_STREET_RESIDUAL - lines27["sm_cash"],
    }
    ai_bull = adj["d_ops_ai_bull"] + adj["d_pd_ai_bull"] + adj["d_ga_ai_bull"] + adj["d_hosting_ai_bull"]
    lb_costs27 = sum(lines27.values()) - da27            # EBITDA-cost basis (lodging reserves 0 in the forecast)
    gap = rev27 / ST["FY27"]["rev"] - 1
    cases = {
        "A. line build (our costs)": lb_costs27,
        "B. line build, S&M slows to the Street residual (+9.5%)": lb_costs27 + adj["d_sm_to_street_residual"],
        "C. line build + AI bull (ops -10%/booking, PD +5%, G&A +3%, hosting $340M)": lb_costs27 + ai_bull,
        "D. AI bull and S&M slows (C + B)": lb_costs27 + ai_bull + adj["d_sm_to_street_residual"],
        "E. Street's own cost path, flexed down with our revenue (k 0.364)": ST["FY27"]["costs"] * (1 + K_FLEX * gap),
        "F. Street's own cost path, no flex": ST["FY27"]["costs"],
    }
    g27 = (rev27 / rev26 - 1) * 100; mult = M_SPOT - SLOPE * (G_STREET - g27)
    for cname, c27 in cases.items():
        e27 = rev27 - c27
        res.append(dict(revenue_path=pname, cost_case=cname, fy27_revenue=rev27, fy27_growth_pct=g27, fy27_costs=c27,
                        fy27_cost_growth_vs_street_fy26_pct=(c27 / ST["FY26"]["costs"] - 1) * 100, fy27_ebitda=e27, fy27_margin_pct=e27 / rev27 * 100,
                        d_ebitda_vs_street=e27 - ST["FY27"]["ebitda"], d_ebitda_vs_street_pct=(e27 / ST["FY27"]["ebitda"] - 1) * 100,
                        d_margin_vs_street_bp=(e27 / rev27 - ST_M27) * 1e4, multiple=mult, price=(e27 * mult + NET_CASH) / SHARES,
                        price_at_spot_multiple=(e27 * M_SPOT + NET_CASH) / SHARES))
    # break-evens on this revenue path
    c_hold_margin = rev27 * (1 - ST_M27); c_hold_ebitda = rev27 - ST["FY27"]["ebitda"]
    ledger_rows.append(dict(revenue_path=pname, fy27_revenue=rev27, rev_gap_vs_street_pct=gap * 100,
                            costs_to_hold_street_margin=c_hold_margin, growth_to_hold_street_margin_pct=(c_hold_margin / ST["FY26"]["costs"] - 1) * 100,
                            cut_vs_street_path_to_hold_margin=ST["FY27"]["costs"] - c_hold_margin, cut_vs_line_build_to_hold_margin=lb_costs27 - c_hold_margin,
                            costs_to_hold_street_ebitda=c_hold_ebitda, growth_to_hold_street_ebitda_pct=(c_hold_ebitda / ST["FY26"]["costs"] - 1) * 100,
                            cut_vs_street_path_to_hold_ebitda=ST["FY27"]["costs"] - c_hold_ebitda, cut_vs_line_build_to_hold_ebitda=lb_costs27 - c_hold_ebitda,
                            ai_bull_saving_total=-ai_bull, **{k: -v for k, v in adj.items()}, line_build_costs=lb_costs27,
                            street_fy27_costs=ST["FY27"]["costs"], street_fy26_costs=ST["FY26"]["costs"], our_fy26_costs=costs26_ours))
grid = pd.DataFrame(res); grid.to_csv(OUT / "45_fy27_grid.csv", index=False)
be = pd.DataFrame(ledger_rows); be.to_csv(OUT / "45_breakeven.csv", index=False)

# ---- what AI already does in the line build (base path, FY27) -----------------------------------------------------
d = build().set_index("quarter")
V = PV["base"]["ops_variable_share"]; G_FIX = PV["base"]["ops_fixed_growth"] / 100
def ops_no_ai(q, cache={}):
    """Ops & support with support cost per booking held flat (no AI decline), same recursion as the build."""
    pq = PREV[q]
    if pq in ("1Q26", "2Q26", "3Q25", "4Q25"):
        pops, pbk = float(pan.loc[pq, "ops_cash"]), float(pan.loc[pq, "nights_m"]) / NPB_ACT[pq]
    else:
        pops, pbk = ops_no_ai(pq), float(d.loc[pq, "bookings_m"])
    val = pops * (V * float(d.loc[q, "bookings_m"]) / pbk + (1 - V) * (1 + G_FIX))
    return val
ops_lb27 = fy(d, Q27, "ops_cash"); ops_noai27 = sum(ops_no_ai(q) for q in Q27)
pd26 = float(h1.pd_cash.sum()) + fy(d, Q26H2, "pd_cash"); pd25g = float(pan.loc[["1Q25", "2Q25", "3Q25", "4Q25"], "pd_cash"].sum()) / float(pan.loc[["1Q24", "2Q24", "3Q24", "4Q24"], "pd_cash"].sum()) - 1
fy25 = pan.loc[["1Q25", "2Q25", "3Q25", "4Q25"]]; rev25 = float(fy25.revenue.sum())
rev27b = fy(d, Q27, "revenue")
shares = {c: (float(fy25[c if c != "ga_cash" else "ga_cash_ex_lodging"].sum()) / rev25 * 100, fy(d, Q27, c) / rev27b * 100) for c in CASH}
ledger = pd.DataFrame([
    dict(item="Support automation already credited in the line build: FY27 ops & support vs support cost per booking held flat", usd_m=ops_noai27 - ops_lb27, kind="AI saving (in our model)"),
    dict(item=f"Engineering productivity, generous: FY27 PD at +8% instead of FY25's growth ({pd25g * 100:.1f}%), all attributed to AI", usd_m=pd26 * (1 + pd25g) - pd26 * 1.08, kind="AI saving (in our model, if attributed)"),
    dict(item="AI tooling in PD (line build)", usd_m=-PV["base"]["pd_ai_tooling_fy27"], kind="AI cost (in our model)"),
    dict(item="Hosting above the FY25 run-rate ($224M): FY27 hosting in the line build", usd_m=-(fy(d, Q27, "cor_hosting") - PV["base"]["hosting_fy25"]), kind="AI/compute cost (in our model)"),
    dict(item="Filed: 2Q26 third-party support costs, 'lower agent contact volume resulting from increased use of AI' (10-Q)", usd_m=17.0, kind="realised AI saving, quarter"),
    dict(item="Filed: 1H26 third-party support costs, same cause (10-Q)", usd_m=15.0, kind="realised AI saving, six months"),
    dict(item="Filed: 1H26 ops & support payroll increase (10-Q)", usd_m=-41.0, kind="realised cost growth, six months"),
    dict(item="Filed: 1H26 product development payroll increase (10-Q)", usd_m=-132.0, kind="realised cost growth, six months"),
    dict(item="Filed: 1H26 S&M increase (10-Q)", usd_m=-372.0, kind="realised cost growth, six months"),
    dict(item="Filed: 1H26 server cost increase (10-Q)", usd_m=-15.0, kind="realised cost growth, six months"),
])
ledger.to_csv(OUT / "45_ai_ledger.csv", index=False)
sh = pd.DataFrame([dict(line=c, fy25_pct_rev=a, fy27_line_build_pct_rev=b, change_pp=b - a) for c, (a, b) in shares.items()])
sh.loc[len(sh)] = dict(line="ops+pd+ga (the AI-addressable opex)", fy25_pct_rev=sh[sh.line.isin(["ops_cash", "pd_cash", "ga_cash"])].fy25_pct_rev.sum(),
                       fy27_line_build_pct_rev=sh[sh.line.isin(["ops_cash", "pd_cash", "ga_cash"])].fy27_line_build_pct_rev.sum(), change_pp=np.nan)
sh.loc[sh.index[-1], "change_pp"] = sh.iloc[-1].fy27_line_build_pct_rev - sh.iloc[-1].fy25_pct_rev
sh.to_csv(OUT / "45_line_shares.csv", index=False)

# Street's implied split (LSEG COGS field) vs ours
split = pd.DataFrame([dict(period=p, street_costs=ST[p]["costs"], street_cogs=ST[p]["cogs"], street_opex=ST[p]["costs"] - ST[p]["cogs"],
                           street_opex_pct_rev=(ST[p]["costs"] - ST[p]["cogs"]) / ST[p]["rev"] * 100, street_cogs_pct_rev=ST[p]["cogs"] / ST[p]["rev"] * 100) for p in ST])
split.to_csv(OUT / "45_street_split.csv", index=False)

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 80)
print("=== line shares (base path) ===\n", sh.round(2).to_string(index=False))
print("\n=== AI ledger ===\n", ledger.round(1).to_string(index=False))
print("\n=== Street split ===\n", split.round(2).to_string(index=False))
print("\n=== break-evens ===\n", be.round(1).T.to_string())
print("\n=== grid ===\n", grid[["revenue_path", "cost_case", "fy27_revenue", "fy27_cost_growth_vs_street_fy26_pct", "fy27_ebitda", "fy27_margin_pct", "d_ebitda_vs_street", "d_margin_vs_street_bp", "multiple", "price"]].round(1).to_string(index=False))
print("\nwrote", OUT)

# ---- FY26 (the 5 Nov floor sentence): 1H26 actual + 2H26 on each revenue path, our costs vs the Street's 2H26 costs flexed -------------
cq = pd.read_csv(ROOT / "data/processed/margin_build/06_fy27_path_v2/06_consensus_quarterly_2027.csv").set_index("quarter")
st_h2_rev = float(cq.loc[Q26H2, "revenue_mean_musd"].sum()); st_h2_cost = st_h2_rev - float(cq.loc[Q26H2, "ebitda_mean_musd"].sum())
f26 = []
for pname, po in PATHS.items():
    d2 = build(path_override=po).set_index("quarter")
    r_h2 = fy(d2, Q26H2, "revenue"); e_h2_lb = fy(d2, Q26H2, "adj_ebitda")
    c_h2_st = st_h2_cost * (1 + K_FLEX * (r_h2 / st_h2_rev - 1))
    r26 = float(h1.revenue.sum()) + r_h2
    for cname, e_h2 in (("line build (our costs)", e_h2_lb), ("Street's 2H26 cost path, flexed (k 0.364)", r_h2 - c_h2_st)):
        e26 = float(h1.adj_ebitda_reported.sum()) + e_h2
        f26.append(dict(revenue_path=pname, cost_case=cname, fy26_revenue=r26, fy26_ebitda=e26, fy26_margin_pct=e26 / r26 * 100,
                        vs_floor_35_5_bp=(e26 / r26 * 100 - 35.5) * 100, vs_street_margin_bp=(e26 / r26 - ST["FY26"]["ebitda"] / ST["FY26"]["rev"]) * 1e4))
f26 = pd.DataFrame(f26); f26.to_csv(OUT / "45_fy26_floor.csv", index=False)
print("\n=== FY26 vs the 35.5% floor ===\n", f26.round(2).to_string(index=False))
