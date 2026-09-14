"""
40_line_build: a bottom-up margin build by cost item for ABNB, 3Q26-4Q27 (+FY26-FY28).

Run:  py -3.13 analysis/src/margin_build/40_line_build/run.py     (exit 0; writes data/processed/margin_build/40_line_build/ and model/ABNB_margin_line_build.xlsx)

Reads:  02_financial_panel (actuals), 06_fy27_path_v2 (_v2b revenue path, base/bear/bull), M7 parameter sheet (below-EBITDA rules),
        the 10-K S&M split and payment-processing facts (07_cost_components_annual) and the 1H26 10-Q MD&A component deltas (both quoted in PARAMS).
Writes: 40_params.csv, 40_lines_quarterly.csv, 40_annual.csv, 40_backcast.csv, 40_sensitivities.csv, 40_sentence_implied.csv, 40_vs_run.csv, workbook.

Conventions. Cash lines = GAAP less SBC (they still contain D&A). Adjusted EBITDA = revenue - sum(cash lines) + D&A + lodging-tax reserves
(the WS02 identity). Scenarios: `rev_*` = bear/bull revenue path at base costs; `cost_*` = base revenue at adverse/favourable cost parameters;
`both_*` = the two together. Every parameter has a source in 40_params.csv.
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
OUT = ROOT / "data/processed/margin_build/40_line_build"; OUT.mkdir(parents=True, exist_ok=True)
XLSX = ROOT / "model/ABNB_margin_line_build.xlsx"

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
params = pd.DataFrame(P); params.to_csv(OUT / "40_params.csv", index=False)
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
def build(rev_scn: str = "base", cost_scn: str = "base", override: dict | None = None) -> pd.DataFrame:
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
        r = path.loc[(rev_scn, q)]; rev, nights, gbv = float(r["revenue_musd"]), float(r["nights_mm"]), float(r["gbv_busd"])
        bookings = nights / (p["nights_per_booking_fy27"] if is27 else p["nights_per_booking_fy26"])
        # cost of revenue
        fee_rate = (p["merchant_fee_pct_gbv"] + p["xborder_fee_bp_per_pt"] * xb_drift_pts / 100) * FEE_FACTOR[qn]
        fees = fee_rate / 100 * gbv * 1000
        chargebacks = p["chargeback_per_booking"] * bookings
        hosting = (p["hosting_fy27"] + max(0.0, 2 * (hosting_step - p["hosting_step_2h26"]))) / 4 if is27 else (p["hosting_fy25"] / 2 + hosting_step) / 2
        cor_other = p["cor_other_per_night"] * nights
        cor = fees + chargebacks + hosting + cor_other
        # operations & support
        d_var = p["ops_variable_decline_fy27"] if is27 else p["ops_variable_decline_2h26"]
        v = p["ops_variable_share"]
        ops_var = hist[pq]["ops"] * v * (1 + d_var / 100) * bookings / hist[pq]["bookings"]
        ops_fix = hist[pq]["ops"] * (1 - v) * (1 + p["ops_fixed_growth"] / 100)
        ops = ops_var + ops_fix
        # product development, S&M, G&A: FY (or 2H) view spread on the 2023-25 quarterly shares
        pdv = pd_fy27 * SHARE["pd"][qn] if is27 else pd_2h26 * SHARE["pd"][qn] / H2["pd"]
        mkt = mkt_fy27 * SHARE["sm"][qn] if is27 else mkt_2h26 * SHARE["sm"][qn] / H2["sm"] + (mkt_q3_step if qn == 3 else 0.0)
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
        hist[q] = dict(ops=ops, bookings=bookings, sbc=sbc, fh=fh_unshifted, gbv=gbv)
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

SCN = {"base": ("base", "base"), "evidence_only": ("base", "base"), "rev_bear": ("bear", "base"), "rev_bull": ("bull", "base"), "cost_bear": ("base", "bear"), "cost_bull": ("base", "bull"),
       "both_bear": ("bear", "bear"), "both_bull": ("bull", "bull")}
lines = pd.concat([build(*v, override=({"reconcile_to_sentence": 0.0} if k == "evidence_only" else None)).assign(scenario=k) for k, v in SCN.items()], ignore_index=True)
lines.to_csv(OUT / "40_lines_quarterly.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 4. Annual: FY26 = 1H26 actual + 2H26 build; FY27 = four quarters; FY28 = FY27 margin on the FY28 base revenue path (flagged)
# ----------------------------------------------------------------------------------------------------------------------
h1 = pan.loc[["1Q26", "2Q26"]]; h1_op_inc = float((h1["adj_ebitda_reported"] - h1["da"] - h1["sbc_total_is"] - h1["other_addbacks_total"]).sum())
mkt_1h26_base = PV["base"]["marketing_fy25"] * PV["base"]["marketing_1h_share"] * (1 + PV["base"]["marketing_growth_1h26"] / 100)
LINES = ["revenue", "nights_m", "gbv_busd", "cor_cash", "ops_cash", "pd_cash", "sm_cash", "sm_marketing", "sm_field", "ga_cash", "total_cash_costs", "da", "adj_ebitda", "sbc", "op_income", "interest_income", "net_income"]
H1MAP = {"adj_ebitda": "adj_ebitda_reported", "sbc": "sbc_total_is", "total_cash_costs": None, "sm_marketing": None, "sm_field": None, "op_income": None}
ann_rows = []
for scn, (rs, cs) in SCN.items():
    d = lines[lines.scenario == scn].set_index("quarter")
    for fy, qs in (("FY26", ["3Q26", "4Q26"]), ("FY27", Q_ORDER[2:])):
        s = d.loc[qs].sum(numeric_only=True); row = dict(period=fy, scenario=scn)
        for c in LINES:
            add = 0.0
            if fy == "FY26":
                col = H1MAP.get(c, c)
                if col is not None: add = float(h1[col].sum())
                elif c == "total_cash_costs": add = float((h1.cor_cash + h1.ops_cash + h1.pd_cash + h1.sm_cash + h1.ga_cash).sum())
                elif c == "sm_marketing": add = mkt_1h26_base
                elif c == "sm_field": add = float(h1.sm_cash.sum()) - mkt_1h26_base
                elif c == "op_income": add = h1_op_inc
            row[c] = float(s[c]) + add
        row["adj_ebitda_margin_pct"] = row["adj_ebitda"] / row["revenue"] * 100
        sh = float(d.loc[qs, "diluted_shares_m"].mean()) if fy == "FY27" else (float(h1.shares_diluted_m.mean()) + float(d.loc[qs, "diluted_shares_m"].mean())) / 2
        row["eps"] = row["net_income"] / sh
        for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "sm_marketing", "ga_cash", "total_cash_costs", "sbc"]:
            row[c + "_pct_rev"] = row[c] / row["revenue"] * 100
        ann_rows.append(row)
annual = pd.DataFrame(ann_rows)
fy27b = annual[(annual.period == "FY27") & (annual.scenario == "base")].iloc[0]
rev28 = float(ann_path.loc[(ann_path.period == "FY28") & (ann_path.scenario == "base"), "revenue_musd"].iloc[0]); g = rev28 / fy27b["revenue"]
r28 = {k: (v * g if isinstance(v, float) and not k.endswith("_pct") and k != "eps" else v) for k, v in fy27b.items()}
r28.update(period="FY28 roll-forward (flagged)", scenario="base", eps=fy27b["eps"] * g)
for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "sm_marketing", "ga_cash", "total_cash_costs", "sbc"]:
    r28[c + "_pct_rev"] = r28[c] / r28["revenue"] * 100
r28["adj_ebitda_margin_pct"] = r28["adj_ebitda"] / r28["revenue"] * 100
annual = pd.concat([annual, pd.DataFrame([r28])], ignore_index=True)
for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "total_cash_costs"]:
    fy25 = float(pan.loc[["1Q25", "2Q25", "3Q25", "4Q25"], c].sum())
    annual[c + "_yoy_pct"] = np.where(annual.period == "FY26", annual[c] / fy25 * 100 - 100, np.nan)
annual.to_csv(OUT / "40_annual.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 5. What management's "down slightly" sentence implies for 2H26 marketing (solve on the base build)
# ----------------------------------------------------------------------------------------------------------------------
target = float(pan.loc["3Q25", "adj_ebitda_margin_pct"]) - 0.5
def m3q(g): return float(build(override={"marketing_growth_2h26": g, "reconcile_to_sentence": 0.0}).set_index("quarter").loc["3Q26", "adj_ebitda_margin_pct"])
lo, hi = -50.0, 150.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if m3q(mid) > target else (lo, mid)
implied = build(override={"marketing_growth_2h26": mid, "reconcile_to_sentence": 0.0}).set_index("quarter")
evid_q = lines[lines.scenario == "evidence_only"].set_index("quarter")
base_q = lines[lines.scenario == "base"].set_index("quarter")
sent = pd.DataFrame([dict(item="3Q25 actual margin", value=float(pan.loc["3Q25", "adj_ebitda_margin_pct"])),
                     dict(item="'down slightly' target used (3Q25 - 0.5pt)", value=target),
                     dict(item="evidence-only build: 3Q26 margin", value=float(evid_q.loc["3Q26", "adj_ebitda_margin_pct"])),
                     dict(item="evidence-only build: 3Q26 total cash cost growth y/y %", value=float(evid_q.loc["3Q26", "total_cash_costs_yoy_pct"])),
                     dict(item="reconciled base: 3Q26 margin at the GUIDE midpoint revenue (by construction = target)", value=target),
                     dict(item="reconciled base: 3Q26 margin at OUR revenue ($4,804M; the forecast)", value=float(base_q.loc["3Q26", "adj_ebitda_margin_pct"])),
                     dict(item="reconciled base: 3Q26 total cash cost growth y/y %", value=float(base_q.loc["3Q26", "total_cash_costs_yoy_pct"])),
                     dict(item="reconciled base: cost gap assigned in 3Q26, USD m", value=float(base_q.loc["3Q26", "recon_gap_3q26_musd"])),
                     dict(item="2H26 marketing growth % that lands the sentence AT OUR revenue with no hosting step (evidence build)", value=mid),
                     dict(item="3Q26 S&M at that growth, USD m", value=float(implied.loc["3Q26", "sm_cash"])),
                     dict(item="3Q26 S&M y/y % at that growth", value=float(implied.loc["3Q26", "sm_cash_yoy_pct"])),
                     dict(item="3Q26 total cash cost growth y/y % at that growth", value=float(implied.loc["3Q26", "total_cash_costs_yoy_pct"])),
                     dict(item="FY26 margin at that growth", value=float(implied.loc[["3Q26", "4Q26"], "adj_ebitda"].sum() + h1.adj_ebitda_reported.sum()) / float(implied.loc[["3Q26", "4Q26"], "revenue"].sum() + h1.revenue.sum()) * 100)])
sent.to_csv(OUT / "40_sentence_implied.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 6. Backcast (cost of revenue and ops from FY24-knowable rates onto FY25 drivers) and in-sample checks
# ----------------------------------------------------------------------------------------------------------------------
fy24 = pan.loc[["1Q24", "2Q24", "3Q24", "4Q24"]]; fy25 = pan.loc[["1Q25", "2Q25", "3Q25", "4Q25"]]
fee24 = (float(fy24.cor_cash.sum()) - 96 - 224 - 0.36 * float(fy24.nights_m.sum())) / (float(fy24.gbv_busd.sum()) * 1000) * 100
cor25_hat = fee24 / 100 * float(fy25.gbv_busd.sum()) * 1000 + 96 / (float(fy24.nights_m.sum()) / 3.8) * (float(fy25.nights_m.sum()) / 3.7) + 224 + 0.36 * float(fy25.nights_m.sum())
ops25_hat = float(fy24.ops_cash.sum()) / (float(fy24.nights_m.sum()) / 3.8) * 0.975 * (float(fy25.nights_m.sum()) / 3.7)
cor_1h26_hat = PV["base"]["merchant_fee_pct_gbv"] / 100 * (FEE_FACTOR[1] * float(pan.loc["1Q26", "gbv_busd"]) + FEE_FACTOR[2] * float(pan.loc["2Q26", "gbv_busd"])) * 1000 \
    + PV["base"]["chargeback_per_booking"] * float(h1.nights_m.sum()) / 3.65 + 224 / 2 + 12 + 0.36 * float(h1.nights_m.sum())
backcast = pd.DataFrame([
    dict(test="FY25 cost of revenue from FY24-knowable rates (fee % GBV, chargebacks/booking, hosting run-rate, other/night)", predicted=cor25_hat, actual=float(fy25.cor_cash.sum()), note=f"FY24 fee rate {fee24:.2f}% of GBV; out of sample"),
    dict(test="FY25 ops & support from FY24 cost per booking x FY25 bookings x the pre-AI -2.5%/yr per-unit trend", predicted=ops25_hat, actual=float(fy25.ops_cash.sum()), note="out of sample; the -10/-16% AI statements came in 2026"),
    dict(test="1H26 cost of revenue with the base rates (1.70% x seasonal factors) and 1H26 drivers", predicted=cor_1h26_hat, actual=float(h1.cor_cash.sum()), note="in sample; the 1H26 fit itself is 1.68% annual-equivalent, FY25 1.76%"),
    dict(test="1H26 ops & support from the rule with v = 0.215 (exact calibration)", predicted=float(pan.loc[["1Q25", "2Q25"], "ops_cash"].sum()) * (0.215 * 0.87 * (float(h1.nights_m.sum()) / 3.65) / (float(pan.loc[["1Q25", "2Q25"], "nights_m"].sum()) / 3.7) + 0.785 * 1.08), actual=float(h1.ops_cash.sum()), note="calibration identity, not a test"),
])
backcast["error_pct"] = (backcast.predicted / backcast.actual - 1) * 100
backcast.to_csv(OUT / "40_backcast.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 7. Sensitivities on the base build
# ----------------------------------------------------------------------------------------------------------------------
def summ(df):
    d = df.set_index("quarter"); f = d.loc[Q_ORDER[2:]]
    return float(d.loc["3Q26", "adj_ebitda"]), float(f.adj_ebitda.sum()) / float(f.revenue.sum()) * 100, float(f.net_income.sum()) / float(f.diluted_shares_m.mean())
b3, b27, be = summ(build()); ev3, ev27, _ = summ(build(override={"reconcile_to_sentence": 0.0}))
sens = []
for name, step, unit in [("merchant_fee_pct_gbv", 0.10, "+10bp of GBV"), ("chargeback_per_booking", 0.20, "+$0.20 per booking"), ("hosting_fy27", 50, "+$50M a year"), ("hosting_step_2h26", 15, "+$15M per half"),
                         ("ops_variable_decline_fy27", 4, "+4pts (slower decline)"), ("ops_variable_decline_2h26", 4, "+4pts"), ("ops_fixed_growth", 3, "+3pts"), ("ops_variable_share", 0.10, "+0.10"),
                         ("pd_growth_fy27", 2, "+2pts"), ("pd_growth_2h26", 2, "+2pts"), ("pd_ai_tooling_fy27", 30, "+$30M"),
                         ("marketing_growth_2h26", 5, "+5pts"), ("marketing_growth_fy27", 5, "+5pts"), ("field_growth_fy26", 4, "+4pts"), ("field_growth_fy27", 4, "+4pts"),
                         ("ga_growth_fy27", 3, "+3pts"), ("ga_growth_2h26", 3, "+3pts"), ("rnpl_share_shift_pts", 10, "+10pts of GBV paid later"), ("tbill_3m", 1.0, "+100bp"), ("etr_fy27", 2.0, "+2pts"), ("sentence_3q26_margin_delta_pp", -0.5, "-0.5pp (a bigger 'slightly')"), ("guide_3q26_revenue_mid", 40, "+$40M guide midpoint"), ("recon_share_to_marketing", 0.30, "+0.30 to marketing")]:
    s3, s27, se = summ(build(override={name: PV["base"][name] + step}))
    e3, e27, ee = summ(build(override={name: PV["base"][name] + step, "reconcile_to_sentence": 0.0}))
    sens.append(dict(parameter=name, shock=unit, d_3q26_ebitda_musd=s3 - b3, d_fy27_margin_pp=s27 - b27, d_fy27_eps_usd=se - be,
                     evidence_only_d_3q26_ebitda_musd=e3 - ev3, evidence_only_d_fy27_margin_pp=e27 - ev27))
sens = pd.DataFrame(sens).sort_values("d_fy27_margin_pp", key=lambda s: -s.abs()); sens.to_csv(OUT / "40_sensitivities.csv", index=False)

# ----------------------------------------------------------------------------------------------------------------------
# 8. Comparison with the run's allocated lines (23_final_model, base) and identities
# ----------------------------------------------------------------------------------------------------------------------
run = pd.read_csv(RUN23); run = run[run.scenario == "base"].set_index("quarter")
qmap = {"3Q26": "2026Q3", "4Q26": "2026Q4", "1Q27": "2027Q1", "2Q27": "2027Q2", "3Q27": "2027Q3", "4Q27": "2027Q4"}
rl = {"cor_cash": "cor_cash_musd", "ops_cash": "ops_cash_musd", "pd_cash": "pd_cash_musd", "sm_cash": "sm_cash_musd", "ga_cash": "ga_cash_musd", "adj_ebitda": "adj_ebitda_musd", "adj_ebitda_margin_pct": "adj_ebitda_margin_pct"}
cmp = pd.DataFrame([dict(quarter=q, line=l, line_build=float(base_q.loc[q, l]), run23_allocated=float(run.loc[qmap[q], rl[l]]) if qmap[q] in run.index else np.nan) for q in Q_ORDER for l in rl])
cmp["diff"] = cmp.line_build - cmp.run23_allocated; cmp.to_csv(OUT / "40_vs_run.csv", index=False)
assert (lines.revenue - lines.total_cash_costs + lines.da + lines.lodging_reserves - lines.adj_ebitda).abs().max() < 1e-6
assert (lines.cor_cash - (lines.cor_fees + lines.cor_chargebacks + lines.cor_hosting + lines.cor_other)).abs().max() < 1e-6
assert (lines.sm_cash - (lines.sm_marketing + lines.sm_field)).abs().max() < 1e-6
assert (lines.ops_cash - (lines.ops_variable + lines.ops_fixed)).abs().max() < 1e-6

# ----------------------------------------------------------------------------------------------------------------------
# 9. Workbook (frozen report of the CSVs)
# ----------------------------------------------------------------------------------------------------------------------
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
wb = Workbook(); ws = wb.active; ws.title = "README"
for i, t in enumerate([
    "ABNB margin line build (40_line_build), 15 Sep 2026. Built directly, no subagents.",
    "Each cost line is a formula on named parameters (sheet Params; every parameter has a source). Cash lines = GAAP less SBC and still contain D&A.",
    "Adjusted EBITDA = revenue - sum(cash lines) + D&A + lodging-tax reserves (WS02 identity). Revenue: bridge v3 (3Q26/4Q26) and WS06 v2b (2027).",
    "Scenarios: rev_bear/rev_bull = revenue path at base costs; cost_bear/cost_bull = base revenue at adverse/favourable cost parameters; both_* = combined.",
    "FY26 = 1H26 actual + 2H26 build. FY28 = FY27 margin on the FY28 revenue path, flagged, not a forecast.",
    "Sentence_implied: the 2H26 marketing growth at which 3Q26 lands on management's 'down slightly' (3Q25 - 0.5pt). Backcast: what the structure gets right out of sample.",
    "Rebuild: py -3.13 analysis/src/margin_build/40_line_build/run.py. This workbook is a frozen report of data/processed/margin_build/40_line_build/."], 1):
    ws.cell(i, 1, t)
ws.column_dimensions["A"].width = 170
def sheet(name, df):
    w = wb.create_sheet(name)
    for j, c in enumerate(df.columns, 1):
        cell = w.cell(1, j, str(c)); cell.font = Font(bold=True); cell.fill = PatternFill("solid", fgColor="DDE5EE")
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            w.cell(i, j, float(v) if isinstance(v, (float, np.floating)) else v)
    for j, c in enumerate(df.columns, 1):
        w.column_dimensions[get_column_letter(j)].width = max(12, min(70, int(df[c].astype(str).str.len().max()) + 2))
sheet("Params", params); sheet("Lines_quarterly", lines.round(3)); sheet("Annual", annual.round(3)); sheet("Sentence_implied", sent.round(2))
sheet("Backcast", backcast.round(2)); sheet("Sensitivities", sens.round(3)); sheet("Vs_run23", cmp.round(2))
hist_cols = ["revenue", "nights_m", "gbv_busd", "cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "ga_cash_ex_lodging", "lodging_tax_reserves", "da", "sbc_total_is", "adj_ebitda_reported", "adj_ebitda_margin_pct", "interest_income", "net_income", "eps_diluted", "shares_diluted_m", "funds_held_on_behalf"]
sheet("Actuals_1Q23_2Q26", pan.loc[[q for q in pan.index if q[-2:] in ("23", "24", "25", "26")], hist_cols].reset_index().round(2))
wb.save(XLSX)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print("=== quarterly, base ===")
print(base_q[["revenue", "cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "adj_ebitda", "adj_ebitda_margin_pct", "total_cash_costs_yoy_pct", "sm_cash_yoy_pct", "eps"]].round(1).to_string())
print("\n=== annual ===")
print(annual[["period", "scenario", "revenue", "cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "adj_ebitda", "adj_ebitda_margin_pct", "sm_cash_pct_rev", "eps"]].round(2).to_string(index=False))
print("\n=== sentence implied ===\n", sent.round(2).to_string(index=False))
print("\n=== backcast ===\n", backcast.round(1).to_string(index=False))
print("\n=== sensitivities ===\n", sens.round(2).to_string(index=False))
print("\nwrote", OUT, "and", XLSX)
