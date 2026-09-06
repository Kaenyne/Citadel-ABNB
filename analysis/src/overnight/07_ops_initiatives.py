"""Workstream 07 part 2: inventory of every operational / efficiency initiative Airbnb has run since 2022, with the
cost line it lands in, what management claimed, what the filings actually show, and a realised / in progress /
not evidenced score.

Method. The initiative list, dates and claimed effects are hand-curated from primary sources (each row carries its
source: shareholder letter quarter, 10-K / 10-Q MD&A, earnings-call speaker and quarter, or 8-K / press release).
Every "evidence" number is COMPUTED here from the workstream's own CSVs so nothing is typed twice: a row names a
metric key and the script fills the value. Rows whose evidence cannot be computed from a filed series say so.

Reads
  data/processed/overnight/07_cost_lines_per_night.csv      quarterly cost lines, per night, per $GBV, y/y, S&M split
  data/processed/overnight/07_cost_components_annual.csv    annual disclosed components (payments, marketing, headcount)
  data/processed/abnb_capital_return_quarterly.csv          SBC, buybacks, diluted share count
  data/processed/abnb_fcf_bridge.csv                        interest income, unearned fees, FCF

Writes
  data/processed/overnight/07_ops_initiatives.csv           one row per initiative

Run: py -3.13 analysis/src/overnight/07_ops_initiatives.py
"""
import csv, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("data", "processed", "overnight", "07_ops_initiatives.csv")


def rd(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


Q = {r["quarter"]: r for r in rd(P("data", "processed", "overnight", "07_cost_lines_per_night.csv"))}
A = {r["component"]: r for r in rd(P("data", "processed", "overnight", "07_cost_components_annual.csv"))}
CAP = {r["quarter"]: r for r in rd(P("data", "processed", "abnb_capital_return_quarterly.csv"))}
FCF = {r["period"]: r for r in rd(P("data", "processed", "abnb_fcf_bridge.csv"))}


def q(quarter, col):
    return f(Q[quarter].get(col))


def ann(component, year):
    return f(A[component].get(f"fy{year}"))


def h(year, col, agg="sum"):
    """1H aggregate of a quarterly $ column."""
    vals = [f(Q[f"{i}Q{str(year)[2:]}"][col]) for i in (1, 2)]
    return sum(vals) if agg == "sum" else vals


def h_per_night(year, col):
    return sum(f(Q[f"{i}Q{str(year)[2:]}"][col]) for i in (1, 2)) / sum(f(Q[f"{i}Q{str(year)[2:]}"]["nights_m"]) for i in (1, 2))


# ---------------------------------------------------------------------------------------------------------
# Evidence builders. Each returns (evidence_string, quantified_effect_string). Everything numeric comes from the CSVs.
def ev_marketing_reset():
    y = {yr: ann("brand_perf_marketing_pct_rev", yr) for yr in (2021, 2022, 2023, 2024, 2025)}
    h25, h26 = h(2025, "sm_brand_perf_musd"), h(2026, "sm_brand_perf_musd")
    r25, r26 = h(2025, "revenue_musd"), h(2026, "revenue_musd")
    return (f"Brand and performance marketing was 23.7% of revenue in 2019 ($1,140M / $4,805M) and has been "
            f"{min(y.values()):.1f}-{max(y.values()):.1f}% every year 2021-2025 ({y[2025]:.1f}% in 2025). "
            f"But 1H26 it is {100*h26/r26:.1f}% of revenue against {100*h25/r25:.1f}% in 1H25, ${h26:,.0f}M vs ${h25:,.0f}M, +{100*(h26/h25-1):.0f}% y/y.",
            f"Worth about {23.7 - y[2025]:.0f} points of margin against the 2019 cost structure; but brand and performance marketing is "
            f"{100*h26/r26 - 100*h25/r25:+.1f} points of revenue higher in 1H26 than in 1H25, so the reset is being spent back.")


def ev_headcount():
    rpe = {yr: ann("revenue_per_employee_kusd", yr) for yr in (2021, 2022, 2023, 2024, 2025)}
    emp = {yr: ann("employees_dec31", yr) for yr in (2022, 2024, 2025)}
    return (f"Revenue per employee ${rpe[2021]:,.0f}k (2021) -> ${rpe[2024]:,.0f}k (2024) -> ${rpe[2025]:,.0f}k (2025), the first decline. "
            f"Headcount {emp[2022]:,.0f} (2022) -> {emp[2024]:,.0f} -> {emp[2025]:,.0f}, +{100*(emp[2025]/emp[2024]-1):.0f}% in 2025. "
            f"1H26 10-Q attributes the increase in every people line (ops +$41M, product dev +$132M, S&M payroll, G&A +$38M) to higher average headcount.",
            f"Productivity gain stalled: revenue per employee {100*(rpe[2025]/rpe[2024]-1):+.1f}% in 2025 after +{100*(rpe[2024]/rpe[2021]-1):.0f}% 2021-24.")


def ev_payments():
    pg = {yr: ann("payment_processing_pct_gbv", yr) for yr in (2020, 2021, 2022, 2023, 2024, 2025)}
    return (f"Merchant fees plus chargebacks as a percent of GBV: {pg[2020]:.2f}% (2020), {pg[2021]:.2f}% (2021), then "
            f"{pg[2022]:.2f}% / {pg[2023]:.2f}% / {pg[2024]:.2f}% / {pg[2025]:.2f}%. Levels after 2021 are derived from the MD&A deltas, not disclosed. "
            f"Cost of revenue per $100 of GBV was ${q('2Q22','cor_cash_per_100gbv'):.2f} in 2Q22 and ${q('2Q26','cor_cash_per_100gbv'):.2f} in 2Q26.",
            f"{100*(pg[2021]-pg[2020]):.0f} bps of GBV taken out in 2021 (~1.5 points of margin); flat +-4 bps since. Not a forward lever.")


def ev_payment_incentive():
    return ("2Q23 cost of revenue carried a payment-processor incentive; Mertz on the 2Q24 call flagged 'the one-time benefit that we had "
            "in payment processing a year ago that will not recur this year'. Cost of revenue per $100 GBV was "
            f"${q('2Q23','cor_cash_per_100gbv'):.2f} in 2Q23 vs ${q('2Q24','cor_cash_per_100gbv'):.2f} in 2Q24 and ${q('2Q22','cor_cash_per_100gbv'):.2f} in 2Q22.",
            "One quarter, not a run-rate lever. Never sized by the company.")


def ev_outsourcing():
    w = {yr: ann("third_party_support_workers", yr) for yr in (2022, 2023, 2024, 2025)}
    return (f"Third-party (contingent) community-support workers: {w[2022]:,.0f} in 2022-2024, {w[2025]:,.0f} in 2025 (10-K Item 1). "
            f"Operations and support cash cost per night ${q('2Q22','ops_cash_per_night'):.2f} (2Q22) -> ${q('2Q25','ops_cash_per_night'):.2f} (2Q25) -> ${q('2Q26','ops_cash_per_night'):.2f} (2Q26).",
            f"Ops and support cash per night {100*(q('2Q26','ops_cash_per_night')/q('2Q22','ops_cash_per_night')-1):+.0f}% over four years while ADR rose; ~0.8 points of margin 2022-2025 (abnb_margin_bridge.csv).")


def ev_ai_support():
    o25, o26 = h_per_night(2025, "ops_cash_musd"), h_per_night(2026, "ops_cash_musd")
    return ("Disclosed: AI assistant resolves ~1/3 of issues without an agent (4Q25 letter), over 40% (1Q26 letter), nearly 45% in 50+ languages (2Q26 letter). "
            "Customer-support cost per booking -10% y/y (1Q26 call) and -16% y/y (2Q26 letter and call). 2Q26 10-Q: third-party service-provider costs "
            "-$17M in the quarter and -$15M in 1H26 'due to lower agent contact volume resulting from increased use of artificial intelligence'. "
            f"Independently: ops and support cash per night ${o25:.2f} (1H25) -> ${o26:.2f} (1H26), {100*(o26/o25-1):+.1f}%.",
            f"Ops and support cash per night {100*(o26/o25-1):+.1f}% y/y in 1H26 = about {100*(o25-o26)*sum(f(Q[f'{i}Q26']['nights_m']) for i in (1,2))/h(2026,'revenue_musd'):+.2f} points of margin. "
            "Partly offset inside the same line by payroll +$41M, customer relations +$14M and insurance +$9M, so the reported line still grew 8%.")


def ev_ai_engineering():
    p25, p26 = h(2025, "pd_cash_musd"), h(2026, "pd_cash_musd")
    return ("Claims: 60% of code AI-authored (1Q26 call), 80% more features shipped y/y and concept-to-launch time down as much as 60% (2Q26 call). "
            f"Product development cash cost 1H25 ${p25:,.0f}M -> 1H26 ${p26:,.0f}M, +{100*(p26/p25-1):.0f}%; the 10-Q says the whole increase is payroll on higher average headcount. "
            f"Cash product development was {q('2Q22','pd_cash_pct_rev'):.1f}% of revenue in 2Q22 and {q('2Q26','pd_cash_pct_rev'):.1f}% in 2Q26.",
            "Zero measurable P&L saving so far. It shows up as output (features shipped), not cost. Treat as a growth option, not a margin lever.")


def ev_cloud():
    d = {yr: ann("cloud_hosting_cost_delta", yr) for yr in (2022, 2023, 2024, 2025)}
    return (f"10-K MD&A gives only the increase in cloud / data-hosting cost: +${d[2022]:.0f}M, +${d[2023]:.0f}M, +${d[2024]:.0f}M, +${d[2025]:.0f}M. "
            "1H26 10-Q: server costs +$15M 'driven by higher amortization related to reserved instance purchases and increased infrastructure spend'. "
            f"Non-cancelable purchase obligations at year end: ${ann('purchase_obligations_dec31',2022):,.0f}M (2022), ${ann('purchase_obligations_dec31',2023):,.0f}M, "
            f"${ann('purchase_obligations_dec31',2024):,.0f}M, ${ann('purchase_obligations_dec31',2025):,.0f}M. The data-hosting commitment went from "
            f"'at least ${ann('data_hosting_commitment_total',2024):,.0f} million... through 2027' (FY2024 10-K) to 'at least $1.7 billion... through 2031' (FY2025 10-K).",
            "No disclosed saving, and the direction has reversed: committed compute is 2.4x higher at end-2025 than end-2024 and now runs to 2031. "
            "Reserved instances convert a variable cost into a fixed one. This is where the AI build is visible before it reaches the P&L.")


def ev_ga():
    return (f"G&A cash cost {q('2Q22','ga_cash_pct_rev'):.1f}% of revenue in 2Q22 -> {q('2Q26','ga_cash_pct_rev'):.1f}% in 2Q26. "
            "1H26 10-Q: G&A up $4M, or 1%, with payroll +$38M offset by non-income taxes -$38M. FY2024 carried a -$656M non-income-tax swing "
            "as the 2023 Italy withholding settlement reversed.",
            "The cleanest line in the P&L: roughly 2.7 points of revenue taken out since 2022, but ~1 point of it is lapping tax reserves, not operating discipline.")


def ev_cohost():
    return ("Co-Host Network launched Oct 2024 (3Q24 letter). Almost 100,000 listings four months in (4Q24 letter); over 100,000 listings and "
            "10 million cumulative nights by 2Q25. Listings on the network 'earn approximately twice as much as Airbnb listings in comparable countries' (4Q24 letter).",
            "A supply-acquisition and quality program, not a cost program. No cost effect has ever been disclosed and none is visible in field operations and policy.")


def ev_new_business():
    fo = {yr: ann("field_ops_policy_pct_rev", yr) for yr in (2023, 2024, 2025)}
    fo25, fo26 = h(2025, "sm_field_ops_musd"), h(2026, "sm_field_ops_musd")
    return (f"Guided $200-250M in 2025 to launch and scale Services and Experiences (4Q24 letter and call), refined to about $200M on the 2Q25 call. "
            f"Field operations and policy went from ${ann('field_operations_and_policy',2024):,.0f}M (2024) to ${ann('field_operations_and_policy',2025):,.0f}M (2025), +43%, "
            f"i.e. {fo[2024]:.1f}% -> {fo[2025]:.1f}% of revenue; S&M third-party service-provider costs rose $102M in 2025 for 'product launch and supply acquisition'. "
            f"In 1H26 field ops is ${fo26:,.0f}M vs ${fo25:,.0f}M, +{100*(fo26/fo25-1):.0f}%, decelerating from +43%.",
            f"The $200-250M was spent and then some (field ops alone +${ann('field_operations_and_policy',2025)-ann('field_operations_and_policy',2024):,.0f}M): "
            f"about {fo[2025]-fo[2024]:.1f} points of revenue. Return not evidenced: no contribution margin, revenue or booking figure for Services or Experiences has ever been given.")


def ev_take_rate():
    return (f"Implied take rate (revenue / GBV): {q('2Q24','take_rate_pct'):.2f}% (2Q24), {q('2Q25','take_rate_pct'):.2f}% (2Q25), {q('2Q26','take_rate_pct'):.2f}% (2Q26). "
            "'Project Hawaii', a single 15.5% host-paid fee replacing the split fee for property-manager listings, started rolling out in 4Q25 (revealed 12 Feb 2026). "
            "Management guides the 2026 take rate flat, held down by customer incentives on new businesses.",
            "Not yet visible. FY2025 take rate fell 16 bps (-0.8 points of margin, abnb_margin_bridge.csv). +10 bps is worth about +0.48 points of margin.")


def ev_rnpl():
    fy = {y: f(FCF[f"FY{y}"]["change_unearned_fees"]) for y in (2022, 2023, 2024, 2025)}
    return (f"Reserve Now, Pay Later launched in the US in 3Q25 with ~70% adoption among eligible bookings; merchandised from 4Q25. "
            f"Change in unearned fees: +${fy[2022]:,.0f}M (2022), +${fy[2023]:,.0f}M, +${fy[2024]:,.0f}M, +${fy[2025]:,.0f}M, and negative in 2Q26.",
            f"Revenue-positive, cash-flow-negative: the float added {100*fy[2022]/f(FCF['FY2022']['revenue']):.1f} points of revenue to cash flow in 2022 and about nothing now. "
            "Roughly 2.8 points of the FCF-margin decline since 2023.")


def ev_hedging():
    return ("FX hedging of forecast revenue began in 2025; every 2026 guide quotes the FX effect 'after factoring in our hedging program' "
            "(2Q26 letter: about a 3-point FX tailwind to revenue growth).",
            "Dampens, does not remove: ~0.26 points of margin per 1% dollar move unhedged (margin-drivers note section 14), less and lagged after hedges.")


def ev_capital_structure():
    return ("Inaugural investment-grade ratings (S&P A-, Moody's Baa1) 12-19 Mar 2026; $2.5B senior notes at 4.40-5.25%; $2.0B used to repay the 2026 converts. "
            "2Q26 10-Q: interest expense $37M in the quarter and $58M in 1H26, against $6M and $11M a year earlier; interest income $183M vs $190M.",
            "Removes the convert dilution overhang and costs about $124M a year of interest, roughly 0.9% of revenue, below the EBITDA line. Net interest 1H26 $280M vs $352M in 1H25.")


def ev_buybacks():
    return (f"Buybacks ${f(CAP['1Q26']['buybacks_musd'])+f(CAP['2Q26']['buybacks_musd']):,.0f}M in 1H26 against SBC of "
            f"${f(CAP['1Q26']['sbc_musd'])+f(CAP['2Q26']['sbc_musd']):,.0f}M; diluted share count {f(CAP['2Q26']['diluted_wa_shares_m']):,.0f}M, "
            f"{f(CAP['2Q26']['diluted_shares_yoy_pct']):+.1f}% y/y, after {f(CAP['4Q25']['diluted_shares_yoy_pct']):+.1f}% in 4Q25.",
            f"SBC is {f(CAP['2Q26']['sbc_pct_rev']):.1f}% of revenue in 2Q26. Buybacks are running ahead of SBC (share count -4.6% y/y), so the dilution offset is now a real return, not just a mop-up.")


def ev_insurance():
    d = {yr: ann("insurance_cost_delta", yr) for yr in (2021, 2022, 2023, 2024, 2025)}
    return (f"Increase in insurance cost inside operations and support: +${d[2021]:.0f}M (2021), +${d[2022]:.0f}M, +${d[2023]:.0f}M, +${d[2024]:.0f}M, +${d[2025]:.0f}M; "
            "+$9M in 1H26 (2Q26 10-Q, host liability premiums). AirCover / Host Liability Insurance scales with nights.",
            f"Growth in the insurance add has fallen from ${d[2021]:.0f}M a year to about $18M a year while nights roughly doubled: contained, but it is a cost that only goes up.")


def ev_marketing_efficiency():
    b25, b26 = h(2025, "sm_brand_perf_musd"), h(2026, "sm_brand_perf_musd")
    return ("Management line, repeated on five calls: '90% of our traffic remains direct or unpaid'. Performance marketing described as running at "
            "'really great efficiencies' (3Q24 call). 1H26 10-Q: marketing spend +$258M 'driven by higher paid growth marketing initiatives in emerging markets and partnerships'.",
            f"Reversed in 2026: brand and performance marketing ${b25:,.0f}M (1H25) -> ${b26:,.0f}M (1H26), +{100*(b26/b25-1):.0f}%, against revenue +{100*(h(2026,'revenue_musd')/h(2025,'revenue_musd')-1):.0f}%. "
            "The 90%-direct claim and a 30%+ paid-marketing ramp cannot both be efficiency.")


def ev_expansion_markets():
    return ("Mertz, 4Q24 call: 'Brand marketing is effectively a fixed amount of spend for each market... the marketing budget is allowed to expand and be "
            "more heavily dedicated to expansion markets.' 1H26 10-Q names 'emerging markets and partnerships' as the driver of the marketing increase.",
            "A redeployment policy, not a saving. It means core-market leverage is real but is being spent, which is exactly why the margin guide is a floor.")


def ev_ai_spend():
    return ("Chesky, 4Q25 call: 'Our investment in AI will not affect the P&L. I don't think you'll see it in the P&L.' Mertz, 2Q26 call: "
            "'the updated guidance that we've provided obviously does assume a material increase in terms of the AI spend over the course of the year.' "
            "New CTO (Ahmad Al-Dahle, ex-Meta Llama) hired Jan 2026.",
            "Contradiction on the record. The 2026 guide contains an unquantified AI cost increase; it is the main reason to treat the 35.5% floor as a floor and not a base.")


def ev_hotels_org():
    return ("Hotels org built out through 2026: VP Hotels (Andrea D'Amico, ex-Booking) Jun 2026, Chief Business Officer (Pepijn Rijvers, ex-Booking) Sep 2026, "
            "Global Head of Operations (Gus Fuldner, ex-Uber, owns safety, support, payments, insurance) Mar 2026, hotels live in 20 cities (May 2026 release), Lark Hotels partnership Aug 2026.",
            "Cost now, revenue later. Lands in field operations and policy and in operations and support payroll. No disclosed budget.")


def ev_restructuring():
    return ("May 2020 workforce reduction (~1,900 roles) and the move to a functional organisation. Headcount at end-2022 (6,811) was still about 5% below 2019 "
            "on 75% more revenue (Stephenson, 4Q22 call).",
            "The single largest lever in the record and it predates the window: it is the base on which every later percentage sits, not a repeatable one.")


# ---------------------------------------------------------------------------------------------------------
INITIATIVES = [
    # id, initiative, category, first announced, source, cost line, claimed effect, verdict, builder
    ("OPS-01", "Permanent marketing reset: brand-led, ~90% direct or unpaid traffic", "Marketing", "2020-Q4 (policy), ongoing",
     "Chesky, 4Q20 call: 'We don't intend to ever again spend the amount of money as a percentage of revenue on marketing... as we did in 2019'; 10-K S&M split table",
     "Sales & marketing", "Marketing stays a far smaller share of revenue than 2019 forever", "Realised 2021-2025, eroding in 2026", ev_marketing_reset),
    ("OPS-02", "2020 workforce reduction and functional reorganisation", "Organisation", "2020-05",
     "FY2020 10-K; Stephenson, 4Q22 call", "All people lines", "Fixed-cost base reset; grow revenue without growing headcount",
     "Realised (pre-window base effect)", ev_restructuring),
    ("OPS-03", "Headcount discipline / revenue per employee", "Organisation", "2022 onward",
     "10-K Item 1 Human Capital counts; 4Q25 call ('headcount growth lower than 2025' for 2026)", "Ops & support, product dev, G&A",
     "Headcount grows slower than revenue", "Realised 2021-2024, lapsed 2025, unproven 2026", ev_headcount),
    ("OPS-04", "Payments: in-house platform, processor mix, chargeback controls", "Payments", "2020-2021",
     "FY2021 10-K MD&A (merchant fees 3% of GBV in 2020, 2% in 2021); Chesky on the payments platform", "Cost of revenue",
     "Lower merchant fees and chargebacks per dollar of GBV", "Realised once (2021), flat since", ev_payments),
    ("OPS-05", "Payment-processor incentive", "Payments", "2023-Q2",
     "2Q23 letter cost-of-revenue commentary; Mertz, 2Q24 call ('will not recur')", "Cost of revenue",
     "Lower cost of revenue", "Realised but one-off (explicitly non-recurring)", ev_payment_incentive),
    ("OPS-06", "Third-party (contingent) community-support network", "Customer support", "2021 onward",
     "10-K Item 1 (11,000 workers 2022-2024, 13,000 in 2025)", "Operations & support",
     "Variable, lower-cost support capacity", "Realised", ev_outsourcing),
    ("OPS-07", "AI customer-service assistant", "Customer support / AI", "2025-Q2 (US launch), scaled 2025-Q4 to 2026-Q2",
     "3Q25 letter (US, -15% need for a human agent); 4Q25 letter (~1/3 resolved); 1Q26 letter (>40%); 2Q26 letter (~45%, 50+ languages, cost per booking -16%); 2Q26 10-Q (third-party -$17M)",
     "Operations & support", "Support cost per booking falls, keeps falling as languages and voice roll out", "Realised", ev_ai_support),
    ("OPS-08", "AI engineering productivity (60% of code AI-authored)", "Product / AI", "2026-Q1",
     "1Q26 call (60% of code); 2Q26 call (80% more features shipped, concept-to-launch -60%)", "Product development",
     "More output per engineer; implied product-dev leverage", "Not evidenced in the P&L", ev_ai_engineering),
    ("OPS-09", "Cloud and hosting optimisation, reserved-instance purchases", "Infrastructure", "2022 onward",
     "10-K MD&A cost-of-revenue deltas; 2Q26 10-Q (server costs +$15M, reserved-instance amortisation); 10-K purchase obligations",
     "Cost of revenue", "Contain hosting cost growth below volume growth", "Not evidenced (cost is rising)", ev_cloud),
    ("OPS-10", "G&A discipline and lapping of non-income tax reserves", "G&A", "2024 onward",
     "10-K / 10-Q MD&A G&A commentary; FY2024 non-income taxes -$656M; 1H26 -$38M", "G&A",
     "G&A grows near zero while revenue compounds", "Realised", ev_ga),
    ("OPS-11", "Co-Host Network", "Supply", "2024-10",
     "3Q24 and 4Q24 letters; 2Q25 letter (100k listings, 10M nights)", "S&M field operations",
     "Cheaper supply growth and better listing quality without Airbnb-employed support", "Realised as a program, no cost effect disclosed", ev_cohost),
    ("OPS-12", "Services and Experiences launch investment ($200-250M)", "New business", "2025-02 (4Q24 letter)",
     "4Q24 letter and call; Mertz, 2Q25 call ('about $200M... field operations, go-to-market and supply acquisition'); FY2025 10-K S&M split",
     "S&M field operations and policy; product development", "Upfront investment, 'optimize the margins over time'",
     "Spend realised, return not evidenced", ev_new_business),
    ("OPS-13", "Host fee simplification: single 15.5% fee ('Project Hawaii')", "Monetisation", "2025-Q4 rollout, revealed 2026-02-12",
     "4Q25 print coverage; 2026 guide of a flat take rate", "Revenue / take rate", "Simpler pricing, no take-rate headwind",
     "In progress, not yet visible", ev_take_rate),
    ("OPS-14", "Reserve Now, Pay Later", "Monetisation / working capital", "2025-Q3 (US), merchandised 2025-Q4",
     "3Q25 and 4Q25 letters; FCF bridge unearned fees", "Revenue timing; free cash flow", "Higher conversion and booking volume",
     "Realised, with a cash-flow cost", ev_rnpl),
    ("OPS-15", "FX hedging of forecast revenue", "Financial", "2025",
     "Every 2025-2026 guide: 'after factoring in our hedging program'", "Revenue / margin volatility", "Smoother reported revenue and margin",
     "Realised", ev_hedging),
    ("OPS-16", "Investment-grade debt: $2.5B senior notes, converts repaid", "Capital structure", "2026-03",
     "8-K Mar 2026; 2Q26 10-Q debt note and income statement", "Below EBITDA (interest)", "Cheaper permanent capital, no convert dilution",
     "Realised", ev_capital_structure),
    ("OPS-17", "Buyback program against SBC dilution", "Capital return", "2022-08 onward",
     "abnb_capital_return_quarterly.csv from the letters", "Share count (not margin)", "Offset SBC dilution and shrink the count",
     "Realised", ev_buybacks),
    ("OPS-18", "Trust, safety and insurance cost containment", "Trust & safety", "2021 onward",
     "10-K MD&A operations-and-support insurance deltas; 2Q26 10-Q +$9M", "Operations & support",
     "Insurance grows slower than nights", "Realised (contained, not reduced)", ev_insurance),
    ("OPS-19", "Performance-marketing efficiency", "Marketing", "2023-2024",
     "3Q24 call ('really great efficiencies'); 1Q25 call ('relative efficiencies by channel, by market')", "Sales & marketing",
     "Paid channels stay a small, high-ROI top-up", "Reversed in 2026", ev_marketing_efficiency),
    ("OPS-20", "Redeploy fixed core-market brand budget into expansion markets", "Marketing", "2025-02 (4Q24 call)",
     "Mertz, 4Q24 call; 1H26 10-Q ('emerging markets and partnerships')", "Sales & marketing",
     "Core-market leverage funds expansion at no net margin cost", "Realised as a policy; it is why margin does not expand", ev_expansion_markets),
    ("OPS-21", "AI spend inside the 2026 guide", "AI", "2026-Q2",
     "Chesky, 4Q25 call vs Mertz, 2Q26 call; CTO hire Jan 2026", "Product development, cost of revenue",
     "First: no P&L effect. Then: a 'material increase' inside the guide", "In progress, unquantified, contradictory", ev_ai_spend),
    ("OPS-22", "Hotels, enterprise and global-markets organisation build-out", "New business", "2026-01 to 2026-09",
     "8-Ks and press: Stein (Jan), Fuldner (Mar), D'Amico (Jun), Rijvers (Sep); May 2026 Summer Release; Lark Hotels (Aug 2026)",
     "S&M field operations; operations & support", "Hotel supply at portfolio scale", "In progress, cost only so far", ev_hotels_org),
]

SCORE = {"Realised": 3, "Realised 2021-2025, eroding in 2026": 2, "Realised (pre-window base effect)": 3,
         "Realised 2021-2024, lapsed 2025, unproven 2026": 2, "Realised once (2021), flat since": 2,
         "Realised but one-off (explicitly non-recurring)": 2, "Not evidenced in the P&L": 0, "Not evidenced (cost is rising)": 0,
         "Realised as a program, no cost effect disclosed": 1, "Spend realised, return not evidenced": 1,
         "In progress, not yet visible": 1, "Realised, with a cash-flow cost": 2, "Realised (contained, not reduced)": 2,
         "Reversed in 2026": 0, "Realised as a policy; it is why margin does not expand": 2,
         "In progress, unquantified, contradictory": 0, "In progress, cost only so far": 0}

BUCKET = {3: "realised", 2: "realised", 1: "in progress", 0: "not evidenced"}


def main():
    rows = []
    for iid, name, cat, date, src, line, claim, verdict, builder in INITIATIVES:
        ev, quant = builder()
        rows.append({"id": iid, "initiative": name, "category": cat, "first_announced": date, "cost_line": line,
                     "claimed_effect": claim, "claim_source": src, "evidence_of_realisation": ev,
                     "quantified_effect": quant, "verdict": verdict, "score": BUCKET[SCORE[verdict]]})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    n = {}
    for r in rows:
        n[r["score"]] = n.get(r["score"], 0) + 1
    print(f"{len(rows)} initiatives ->", OUT)
    print("scores:", n)
    for r in rows:
        print(f"  {r['id']:7s} {r['score']:13s} {r['cost_line']:28s} {r['initiative'][:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
