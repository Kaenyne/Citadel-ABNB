# WS02. The financial panel every margin method reads

Margin build run, 13-14 Sep 2026. Slug `02_financial_panel`. Script `analysis/src/margin_build/02_financial_panel/run.py`
(`python`, from the worktree root, exit 0, ~25 s; `panel_lib.py` holds the parsers, `figures.py` runs under `py -3.13`).
Outputs under `data/processed/margin_build/02_financial_panel/`: `02_panel_quarterly.csv` (34 quarters 1Q18-2Q26, 145 columns),
`02_panel_annual.csv` (FY2018-25, 125 columns incl. 24 `soq_minus_annual__*` checks), `02_panel_provenance.csv` (3,066 rows),
`02_seasonality.csv` (728 rows), `02_reconciliation.csv` (1,513 rows), `02_macro_cycle_episodes.csv` (29 rows),
`02_letter_vintages.csv` (3,288 rows), `02_build_log.txt`. Manifest `data/manifests/margin_build/02_financial_panel.csv`
(424B4 prospectus, 10-Q 1Q21, 10-Q 2Q21 pulled from EDGAR). Figures `analysis/figures/margin_build/02_financial_panel_{margin_seasonality,cost_lines_pct_rev,cost_per_night}.png`.
Free parameters: 0 (nothing is fitted). Tests: 3 pre-registered checks, run by `run.py` and printed in the build log.

**Pre-registered pass line (prompt):** Adjusted EBITDA rebuilt from lines within $2M of reported for every quarter 1Q21-2Q26 (n 22);
annual sums within $5M of the 10-K; every cell sourced; letter reconciliation wins for non-GAAP items, XBRL for GAAP lines.
**Result:** check 1 **PASS** (max |gap| $0.97M at 3Q21; 20 of 22 quarters within $0.5M; exact zero from 4Q22 on). Check 2 **PASS** for every
P&L line, SBC by function, D&A, each add-back, Adjusted EBITDA, tax, interest income and capex (max |gap| $1.0M, FY2018-25, n 8);
**FAIL as literally worded for CFO/FCF in FY2019 (+$10.7M) and FY2020 (-$110.9M)**, entirely the 1Q22 re-presentation of the cash-flow
statement (the quarterly series is the re-presented vintage; the FY2021 10-K's FCF table is the original; against the re-presented FY2020
CFO that XBRL carries from the FY2022 10-K the gap is $0.6M). Check 3 **PASS** (0 unsourced cells in either panel).

## Bottom line

1. **The panel reconciles.** Revenue minus the six GAAP lines plus D&A, SBC (reconciliation row), IPO stock-settlement, acquisition impacts,
   lodging/withholding/transactional-tax reserves and restructuring equals reported Adjusted EBITDA within $1M in all 22 quarters 1Q21-2Q26
   and within $0.6M in all 12 pre-IPO/2020 quarters (1Q18-4Q20). The residual is rounding: GAAP lines come from XBRL in thousands, the
   letters print in millions from 1Q22. Every one of the 3,066 sourced cells carries a file, table and vintage; 29 of 34 quarters have two or
   more letter vintages of the reconciliation, so restatements are visible rather than silently overwritten.
2. **Seasonality is mostly mechanical, and the discretionary part is Q1 marketing, not Q4 hiring.** Revenue is 18.7 / 25.0 / 33.8 / 22.5% of the
   year by quarter (2023-25 mean, range under 1 pt), while the costs Adjusted EBITDA bears are 24.2 / 26.2 / 25.3 / 24.3% (range 23.4-26.6).
   Spreading each year's costs flat across the quarters reproduces the Q2-Q4 margins within 4 pt; the only quarter where actual spending timing
   moves the margin by more is Q1 (+2 to +6 pt above the flat-cost margin in 2022-25: Q1 costs are the lightest quarter of the year, 23-25%,
   because Q1 S&M is only 22-26% of its FY and revenue per night is lowest). The five GAAP-less-SBC lines including the tax reserves in G&A
   show Q4 at 33% of the year in 2023 only because of the $931M Italian reserve, which is added back.
3. **The G&A / add-back trap is handled: use `ga_cash_ex_lodging`.** Non-income-tax reserves and settlements sit inside GAAP G&A *and* are added
   back to Adjusted EBITDA (1Q23-2Q26 add-backs: 4, -2, 41, **931**, 8, 0, 58, -43, -4, -7, 4, **81**, 3, -2). `ga_cash` for 4Q23 is $1,142M;
   underlying `ga_cash_ex_lodging` is $211M. Any G&A driver model must be fit on the ex-lodging series (2023-25 Q share 24-26%, 6-10% of revenue),
   and the add-back must be forecast as a separate lumpy line whose expected value is small but whose FY2025 realisation was $74M.
4. **Nights per booking is now in the panel as the per-booking converter.** Global ALOS from the 10-K MD&A: 4.1 (2020-22), 3.9 (2023), 3.8 (2024),
   3.7 (2025; carried into 2026 and flagged). `bookings_est_m = nights_m / nights_per_booking_fy`; `ops_cash_per_booking_usd` was $10.74 in 3Q24, $9.50 in 3Q25
   (-11.5% y/y) and $8.06 in 2Q26 (-5.3%); per night the same quarters are -9.2% and -5.3%. The two differ by the ALOS change (3.8 to 3.7 in 2025)
   and agree by construction in 2026 until the FY2026 10-K discloses ALOS. Management's "-10%" and "-16% per booking" support-cost claims are to be
   scored on the per-booking series, which is where they were made.
5. **Three existing repo panels carry wrong Q4 SBC totals** (4Q23 $270M should be $290M; 4Q24 $400M should be $368M; 4Q25 $400M should be $411M):
   they derived Q4 as FY less 9M with a proxy-statement FY value rounded to $100M. Corrected here; details under "Corrections to existing work".
6. **Interest expense before 2026 is not debt interest.** The FY2024 10-K defines it as "primarily interest associated with various indirect tax
   reserves, amortization of debt issuance and debt discount costs"; the $71M in 4Q23 is interest on the Italian withholding-tax settlement.
   The 2026 senior notes ($2.5B, March 2026) make it a real line: $21M in 1Q26, $37M in 2Q26. 1Q24 is the one quarter with no separate figure
   (folded into other expense in the 1Q24 letter and 10-Q; the FY2024 10-K calls it "immaterial"; the 2Q26 letter re-presents 2Q24 onward).

## What ran (exact commands)

```
cd "C:\Users\krish\citadel-abnb-margins"
python "analysis/src/margin_build/02_financial_panel/run.py"        # everything; calls py -3.13 figures.py at the end (non-fatal)
```

Sources actually consumed (priority order per the prompt): `data/raw/xbrl/ABNB_companyfacts.json` (GAAP P&L 1Q20-2Q26 and FY2019-25, YTD cash-flow
lines de-cumulated with vintage pairing by filing fiscal year, balance-sheet instants, shares, EPS); the 23 shareholder letters 4Q20-2Q26 in
`data/raw/letters/` (Adjusted EBITDA and FCF reconciliation tables with 6-13 quarter columns each, statement of operations, SBC-by-function
footnote, cash-flow statement, KPI summary tables); the 424B4 prospectus (11 Dec 2020) for 1Q18-3Q20 quarterly lines, SBC and reconciliations;
10-Q 1Q21 and 2Q21 for the SBC footnote those two letters lack; 10-K FY2020-FY2025 text (`data/raw/filings/txt/`) for annual reconciliations,
SBC note, revenue by region, headcount, hosting commitment, FY2018; repo panels `overnight/02_kpi_panel_quarterly.csv` (nights/GBV/ADR 3Q20+),
`overnight/10_regional_revenue_xbrl.csv` (quarterly revenue by region 1Q22+), `airbnb_nights_per_booking.csv`, `overnight/31a_mgmt_margin_statements.csv`.
The 10-Q MD&A component deltas (WS01 GAP06) were not pulled: 21 of 22 10-Qs are not in the tree and WS04 owns that pull.

## Reconciliation

### Adjusted EBITDA rebuilt from lines minus reported ($M; n 22 in the window, 34 overall)

| Quarter | 1Q21 | 2Q21 | 3Q21 | 4Q21 | 1Q22 | 2Q22 | 3Q22 | 4Q22 | 1Q23-2Q26 (14 q) |
|---|---|---|---|---|---|---|---|---|---|
| Gap | +0.06 | -0.28 | +0.97 | -0.75 | -0.13 | -0.18 | +0.48 | 0.00 | 0.00 every quarter |

Pre-window: 1Q18-4Q18 0.00 (424B4, thousands both sides); 1Q19-4Q19 -0.08 / -0.16 / +0.53 / +0.06; 1Q20-4Q20 +0.01 / -0.02 / +0.04 / -0.08.
Max |gap| 1Q21-2Q26 = $0.97M (3Q21). The non-zero 2021-3Q22 gaps are the letters' rounding to millions against XBRL in thousands; from 4Q22 the
FY2022 10-K itself is in millions and the identity is exact.

Identity used: `adj_ebitda_rebuilt = revenue - cor_gaap - ops_gaap - pd_gaap - sm_gaap - ga_gaap - restr_gaap + da + sbc_recon + ipo_settlement
+ acq_impacts + lodging_tax_reserves + restr_recon`. Restructuring cancels (GAAP charge and add-back) except for rounding. `sbc_recon` is the
reconciliation row (excludes restructuring SBC); `sbc_total_is` is the income-statement footnote total; they differ only in 2Q20-4Q20 (restructuring SBC).

### Annual sum-of-quarters minus 10-K ($M, |max| over FY2018-25)

| revenue | cor | ops | pd | sm | ga | restr | op inc | net inc | SBC total | SBC ops/pd/sm/ga | D&A | SBC recon | lodging | adj EBITDA | tax | int inc | capex | CFO | FCF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.45 | 0.17 | 0.82 | 0.16 | 0.38 | 1.01 | 0.05 | 0.32 | 0.34 | 0.39 | 0.56 / 0.29 / 0.23 / 0.34 | 0.30 | 0.50 | 0.43 | 0.40 | 0.41 | 0.55 | 0.80 | 10.3 (FY19) | 110.9 (FY20) |

All P&L/EBITDA lines are within $1.01M (the 2021-22 gaps are XBRL-thousands vs 10-K-millions rounding; 2023-25 exact). CFO/FCF: FY2019 +10.3/+10.7,
FY2020 -0.7/-110.9, FY2021 -0.6/+0.2, then exact. The FY2020 figure is the vintage difference between the FY2021 10-K (CFO -$629.7M, FCF -$667.1M,
original presentation) and the re-presented cash-flow statement from the 1Q22 10-Q onward (FY2020 CFO -$740.0M, which is what XBRL now carries
from the FY2022 10-K, and which the 2Q22 letter's quarterly table sums to within $0.6M: `soq_minus_annual__fcf_latest_vintage`). FY2019 has no
re-presented annual filing; the quarterly 2019 CFO comes from the 4Q23 letter's history table on the new basis.

### Versus the three existing repo panels (plus `abnb_fcf_bridge.csv`)

1,479 cell comparisons; 64 differ by more than $1M; every one carries an explanation in `02_reconciliation.csv`. By cause:

| Cause | Rows | Where |
|---|---|---|
| Vintage: 2020-22 CFO/FCF re-presented (up to $125M at 4Q20/1Q21) | 12 | `abnb_fcf_bridge.csv`, `02_kpi_panel_quarterly.csv` |
| **CORRECTION: Q4 SBC total from a DEF 14A FY value rounded to $100M** (4Q23 +20, 4Q24 -32, 4Q25 +11) | 9 | `abnb_quarterly_costlines.csv`, `abnb_quarterly_cost_stack_exsbc.csv`, `02_kpi_panel_quarterly.csv` |
| Definition: restructuring folded into other add-backs there, separate here | 9 | `abnb_quarterly_cost_stack_exsbc.csv`, `abnb_fcf_bridge.csv` |
| Vintage/definition: change in unearned fees (XBRL latest vs letter YTD first-reported) | 8 | `abnb_fcf_bridge.csv` |
| Definition: buybacks retired (XBRL accrual) vs letter cash | 7 | `02_kpi_panel_quarterly.csv` |
| Vintage: interest expense folded into other in 2024-25 filings, re-separated in the 2Q26 letter | 7 | `abnb_fcf_bridge.csv` (carries 0) |
| Definition: other income (expense) with/without interest expense | 7 | `abnb_fcf_bridge.csv` |
| Q4 weighted-average shares from the 4Q letter (not FY-less-9M) | 3 | `02_kpi_panel_quarterly.csv` |
| Precision / later-letter re-presentation of small add-backs | 2 | `abnb_quarterly_costlines.csv`, `abnb_fcf_bridge.csv` |

Everything else (1,415 cells: revenue, the six lines, SBC by function, D&A, Adjusted EBITDA, KPIs, balance-sheet items) agrees within $1M.

## Seasonality (2023-2025 mean; min-max in brackets; n 3 years, 12 quarters)

Quarter's share of the FY total (%):

| Line | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| Revenue | 18.7 [18.3-19.3] | 25.0 [24.8-25.3] | 33.8 [33.4-34.2] | 22.5 [22.3-22.7] |
| Nights booked | 27.0 [26.8-27.0] | 25.4 [25.2-25.7] | 25.1 [25.0-25.3] | 22.5 [22.0-22.9] |
| Adjusted EBITDA | 9.1 [7.2-10.5] | 22.9 [22.1-24.3] | 48.8 [47.7-50.2] | 19.1 [18.3-20.2] |
| Costs Adjusted EBITDA bears (rev - adj EBITDA) | 24.2 [23.4-24.8] | 26.2 [25.8-26.6] | 25.3 [25.0-25.7] | 24.3 [23.6-25.1] |
| Five cash lines incl. tax reserves in G&A | 23.1 [21.8-24.4] | 24.8 [22.8-26.2] | 24.5 [22.2-25.8] | 27.6 [23.6-33.3] |
| Cost of revenue | 25.0 | 26.1 | 26.0 | 22.9 |
| Ops & support (cash) | 23.0 | 26.0 | 27.9 | 23.1 |
| Product development (cash) | 25.5 | 24.7 | 24.6 | 25.3 |
| Sales & marketing (cash) | 24.0 [21.8-25.8] | 27.0 | 23.7 | 25.3 |
| G&A cash ex lodging | 23.9 | 26.0 | 24.6 | 25.6 |
| SBC | 21.6 | 27.0 | 25.4 | 26.0 |
| Interest income | 23.2 | 27.0 | 25.8 | 24.0 |

Mechanical vs discretionary (adjusted EBITDA margin, %): `margin_if_costs_flat` spreads the year's Adjusted-EBITDA cost base evenly over four quarters;
the difference to the actual margin is what spending timing did.

| Year | Q1 actual / flat / timing | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2022 | 15.2 / 8.9 / +6.2 | 33.8 / 34.7 / -0.9 | 50.5 / 52.4 / -1.8 | 26.6 / 27.8 / -1.2 |
| 2023 | 14.4 / 13.9 / +0.6 | 33.0 / 37.0 / -4.0 | 54.0 / 53.9 / +0.1 | 33.3 / 29.4 / +3.9 |
| 2024 | 19.8 / 17.6 / +2.2 | 32.5 / 35.8 / -3.2 | 52.5 / 52.7 / -0.2 | 30.8 / 28.8 / +2.0 |
| 2025 | 18.4 / 12.6 / +5.8 | 33.7 / 35.8 / -2.2 | 50.1 / 51.5 / -1.4 | 28.3 / 28.5 / -0.2 |

Cost per night vs cost as % of revenue, side by side (2023-25 mean): CoR $3.6 / 3.9 / 4.0 / 3.9 per night = 22.7 / 17.8 / 13.1 / 17.4% of revenue;
ops $2.1 / 2.5 / 2.7 / 2.5 = 13.2 / 11.1 / 8.8 / 11.0%; PD $2.3 / 2.3 / 2.3 / 2.7 = 14.4 / 10.5 / 7.7 / 11.9%; S&M $3.6 / 4.3 / 3.8 / 4.6 = 22.8 / 19.3 / 12.6 / 20.2%;
G&A ex lodging $1.6 / 1.9 / 1.8 / 2.1 = 10.4 / 8.5 / 6.0 / 9.3%. Per-night costs rise 10-30% from Q1 to Q3/Q4 (nights are booked earliest in Q1); % of revenue
swings 2x because revenue per night is $15.7 / 22.2 / 30.4 / 22.5 (check-in timing). The Q3 margin peak is revenue recognition, not cost discipline. The full year-by-year tables
(2018-2025) are in `02_seasonality.csv`.

## Line definitions (FY2025 10-K, `data/raw/filings/txt/abnb_10k_FY2025.txt`; panel column names in code)

- `revenue`: service fees net of incentives and refunds, recognised at check-in (XBRL `RevenueFromContractWithCustomerExcludingAssessedTax`).
- `cor_gaap` (no SBC): "payment processing costs, including merchant fees and chargebacks, costs associated with third-party data centers used to
  host our platform, and amortization of internally developed software and acquired technology. As the merchant of record, we bear all payment
  processing costs." `cor_cash_pct_gbv` is the % of GBV form (2.0-2.5% by quarter in 2023-26; Q1 low, Q3 high).
- `ops_gaap` / `ops_cash`: "personnel-related expenses and third-party service provider charges associated with community support ...; customer
  relations costs, which include refunds and credits related to customer satisfaction and expenses associated with our host protection programs;
  and allocated costs for facilities and information technology." No us-gaap element: derived as `CostsAndExpenses` less the other five lines
  (annual check within $0.82M; the 424B4/letters print it directly and agree).
- `pd_gaap` / `pd_cash`: "personnel-related expenses and third-party service provider expenditures incurred in connection with the development of
  our platform, and allocated costs." XBRL `ResearchAndDevelopmentExpense`. Carries 64% of all SBC.
- `sm_gaap` / `sm_cash`: "brand and performance marketing, personnel-related expenses, including those related to our field operations, policy and
  communications, portions of referral incentives and coupons, and allocated costs." The brand/field split is annual only (10-K MD&A; FY2025
  $1,595M / $993M) and is not in this panel (WS01 P03 holds it).
- `ga_gaap` / `ga_cash` / `ga_cash_ex_lodging`: "personnel costs for management and administrative functions ..., professional services fees,
  corporate and director and officer insurance, allocated costs ..., and indirect taxes, including lodging tax reserves." The last item is the trap.
- `restr_gaap`: 2Q20-4Q21 RIF and lease charges, 2Q22 $89M lease impairment; zero since. `restr_recon` is the matching add-back.
- Add-backs (letter reconciliation, latest vintage): `da` (D&A incl. capitalised-software amortisation that sits in CoR), `sbc_recon`, `ipo_settlement`
  (4Q20 $103M; a -$5M reversal in 2Q25), `acq_impacts` (contingent consideration marks, -$22M to +$12M), `lodging_tax_reserves` (label history:
  "Net changes in lodging tax reserves" to FY2022; "... and reserves for host withholding taxes" FY2023; "Lodging taxes, host withholding taxes,
  and transactional taxes, net" from the 4Q24 letter / FY2024 10-K), `other_addbacks_total` = the last three. `adj_cost_total` = revenue - adj EBITDA.
- Below EBITDA: `interest_income` (XBRL `InvestmentIncomeNonoperating`: cash, investments and funds held on behalf of customers), `interest_expense`
  (positive; XBRL to 4Q23, letter 2Q24 on, NaN 1Q24), `other_income_expense` (signed as income; derived as pretax - operating income - interest income
  + interest expense so that it excludes interest expense wherever that is disclosed; `other_includes_interest_expense` flags 1Q24), `pretax_income`,
  `tax_provision`, `net_income`, `eps_basic/diluted` (GAAP; Airbnb publishes no non-GAAP EPS), `shares_basic_m/diluted_m` (Q4 from the 4Q letter,
  since weighted averages are not additive), `effective_tax_rate_pct`.
- Cash flow: `cfo` (letter FCF table, latest vintage; `cfo_xbrl` keeps the companyfacts derivation), `capex` (positive), `fcf_reported`, `fcf_check_gap`
  (= 0 everywhere), `change_unearned_fees` (XBRL de-cumulated) and `change_unearned_fees_letter`, `change_funds_payable` (letter cash-flow
  statements, de-cumulated; 4Q20-2Q26), `change_funds_receivable_xbrl`, `buybacks` (XBRL retired, accrual) and `buybacks_cash`, `rsu_tax_withholding`,
  `income_taxes_paid`, `da_cashflow`, `sbc_cashflow`.
- Balance sheet (quarter-end): `cash_and_equivalents`, `short_term_investments`, `restricted_cash`, `cash_and_investments_total`, `funds_held_on_behalf`,
  `unearned_fees_balance`, `long_term_debt_noncurrent/current/total` ($2.0B 2026 converts to 1Q26; $2.5B notes from 1Q26).
- KPIs: `nights_m`, `gbv_busd`, `adr_usd` (1Q19+; 2019-20 from the 1Q21/4Q21 letter history tables, 3Q20+ from the repo KPI panel), `take_rate_pct`,
  `revenue_per_night_usd`, `nights_per_booking_fy`, `bookings_est_m`, `revenue_per_booking_usd`, `*_cash_per_night_usd`, `cor/ops_cash_per_booking_usd`.
- Regional revenue: `rev_na/emea/latam/apac/us/non_us` quarterly 1Q22-2Q26 from `overnight/10_regional_revenue_xbrl.csv`; annual FY2020-25 from the 10-Ks.
- Annual extras: `headcount_dec31` (5,597 / 6,132 / 6,811 / 6,907 / 7,300 / 8,200 for FY2020-25), `hosting_commitment_remaining` ($1.7B through 2031 at FY2025),
  `advertising_expense` (XBRL `AdvertisingExpense` as tagged: $713M FY2019, $953M FY2023, $1,100M FY2024, $843M FY2025; the FY2025 value is
  inconsistent with brand and performance marketing +10% in the same 10-K, so verify the note's scope before using it), `nights_per_booking_{na,emea,latam,apac}`.

## Caveats

1. **Vintages.** `02_letter_vintages.csv` holds every reconciliation value by letter. Material restatements: CFO/FCF 4Q20 and 1Q21 (+/-$125M, the 1Q22
   re-presentation of funds-related flows), 3Q21 (+$12M); "other (income) expense" 1Q23-4Q25 (the 1Q24-4Q25 letters fold interest expense into it,
   the 2Q26 letter separates it again from 2Q24; the panel's `other_income_expense` is derived from XBRL and unaffected except 1Q24); D&A 4Q21 30.8 to 30;
   small lodging/acquisition re-presentations in 2022. Adjusted EBITDA itself was restated once by more than $0.6M: 2Q21 217.4 to 218.0 (rounding).
   First-reported values are kept as `letter_first_vintage` / `xbrl_first_vintage` rows in the provenance file for point-in-time work.
2. **Pre-IPO rows (1Q18-3Q20, `pre_ipo = True`)** come from the 424B4 (thousands) and later letters; 2018 has no nights/GBV; 2019 KPIs are from letter
   history tables (validated against the repo panel where they overlap).
3. **XBRL rounding.** The FY2024/FY2025 10-Ks tag total SBC only as $1.4B/$1.6B, so `sbc_total_xbrl` is unreliable for Q4 2024-25; `sbc_total_is` uses the
   footnote. That rounding is the root cause of the Q4 SBC errors in the existing panels.
4. **3Q23 tax:** -$2,695M valuation-allowance release (net income $4,374M, EPS $6.63); FY2023 provision -$2,690M. Cash taxes paid are the `income_taxes_paid`
   line (XBRL `IncomeTaxesPaid`, YTD de-cumulated; FY2025 provision $626M against cash taxes of $232M per WS01's 10-K read; the FY2025 annual
   and 4Q25 values are not tagged in companyfacts, so both are NaN here and 9M25 is $180M).
5. **The 2023 Italian reserve:** $931M in 4Q23 G&A (FY2023 add-back $974M) and a $71M 4Q23 interest expense; both neutral to Adjusted EBITDA. The FY2024 10-K
   reports a $770M withholding-tax settlement in 2024 (cash, not P&L).
6. **2025-26 changes to the reconciliation:** label of the tax add-back widened to transactional taxes (4Q24 letter); IPO stock-settlement reversal -$5M in 2Q25;
   interest expense shown separately again from the 2Q26 letter (2026 notes). No change to the SBC definition was found in any 2025-26 letter or the FY2025 10-K;
   the footnote total equals the reconciliation row in every quarter since 1Q23.
7. **Parser drops.** The 2Q24 and 4Q24 letters' reconciliation tables and the 2Q24/2Q22/3Q22 FCF columns for 4Q21/1Q22 failed the identity check and were dropped;
   every affected quarter is covered by other vintages (build log lists all 7 warnings). 2Q26 has a single vintage by construction.
8. **Not in the panel:** brand vs field S&M (annual only), 10-Q MD&A component deltas (GAP06, WS04), non-GAAP EPS (does not exist), quarterly headcount
   (not disclosed), the split of interest income between corporate cash and customer funds (never disclosed).

## Corrections to existing work

1. `data/processed/abnb_quarterly_costlines.csv`, `abnb_quarterly_cost_stack_exsbc.csv`, `overnight/02_kpi_panel_quarterly.csv`: total SBC for 4Q23 is $290M
   (they carry $270M), 4Q24 $368M ($400M), 4Q25 $411M ($400M): derived as FY (proxy-statement value rounded to $100M) less 9M. Their SBC-by-function rows are
   right, so their cash lines are right; anything using the Q4 total (SBC % of revenue, SBC y/y, FCF-less-SBC) is off by up to $32M (1.3% of 4Q24 revenue).
   `abnb_fcf_bridge.csv` has the correct values.
2. `abnb_fcf_bridge.csv` carries `interest_expense = 0` for 1Q24-4Q25 and puts it inside `other_income_expense`; the 2Q26 letter now discloses $9/2/10/5/6/6/26M
   for 2Q24-4Q25. Use this panel's `interest_expense` from 2Q24 (1Q24 remains unknown).
3. `abnb_fcf_bridge.csv` and `02_kpi_panel_quarterly.csv` hold first-reported CFO/FCF for 2020-22 (4Q20 CFO -$139M vs -$259M re-presented; 1Q21 $494M vs $606M).
   Not errors at the time; the re-presented series is the one later letters and XBRL carry.
4. WS01 note item 4 confirmed and extended: the FY2023 "+1,160bp G&A distortion" quoted in 31a is a GAAP statement; on `ga_cash_ex_lodging` FY2023 G&A was
   8.3% of revenue vs 8.7% in FY2022 and 8.1% in FY2024. `research/notes/overnight/31_margin-model.md` and 31b fit G&A on the GAAP-less-SBC line; refitting on
   the ex-lodging series would remove the 2023 outlier (not done here; M1's call).
5. `abnb_quarterly_cost_stack_exsbc.csv` `other_addbacks` includes restructuring; `07`/`31b`'s "other add-backs 0.9% of revenue" therefore mixes a lumpy tax
   item with a discontinued restructuring item. Split as here: D&A (0.6-0.8%), tax reserves (lumpy, FY2025 $74M = 0.6%), acquisition marks (~0), restructuring (0).

## For the model

Series (all in `02_panel_quarterly.csv`, USD millions, 1Q18-2Q26 unless stated; annual twins in `02_panel_annual.csv`):

| Object | Column(s) | Note |
|---|---|---|
| Six cost lines GAAP | `cor_gaap ops_gaap pd_gaap sm_gaap ga_gaap restr_gaap` | XBRL (thousands to 3Q22, millions after) |
| Six cost lines cash | `cor_cash ops_cash pd_cash sm_cash ga_cash` (+ `ga_cash_ex_lodging`) | GAAP less that line's SBC; fit G&A on ex-lodging |
| SBC by line | `sbc_ops sbc_pd sbc_sm sbc_ga sbc_restr sbc_total_is sbc_recon` | footnote; recon row excludes restructuring SBC |
| Add-backs | `da ipo_settlement acq_impacts lodging_tax_reserves restr_recon other_addbacks_total` | forecast `lodging_tax_reserves` as its own lumpy line |
| Target | `adj_ebitda_reported adj_ebitda_margin_pct` (+ `adj_ebitda_rebuilt rebuild_gap`) | reported, latest vintage; first vintage in provenance |
| Below EBITDA | `interest_income interest_expense other_income_expense pretax_income tax_provision net_income eps_diluted shares_diluted_m effective_tax_rate_pct` | `interest_expense` NaN 1Q24 |
| Cash flow | `cfo capex fcf_reported change_unearned_fees change_funds_payable buybacks buybacks_cash rsu_tax_withholding income_taxes_paid` | FCF identity holds every quarter |
| Balance sheet | `cash_and_investments_total funds_held_on_behalf unearned_fees_balance long_term_debt_total` | quarter-end |
| Denominators | `nights_m gbv_busd adr_usd revenue_per_night_usd take_rate_pct nights_per_booking_fy bookings_est_m` | ALOS annual, applied to quarters |
| Per-unit | `*_cash_per_night_usd`, `cor_cash_pct_gbv`, `cor/ops_cash_per_booking_usd`, `*_cash_pct_rev` | |
| Seasonal profile | `02_seasonality.csv` (`q_share_of_fy_pct`, `pct_of_revenue`, `per_night_usd`, `margin_if_costs_flat_pct`, `margin_discretionary_timing_pp`, 2023-25 mean/min/max) | M2's seasonal-share method should use the 2023-25 shares above |
| Episodes | `02_macro_cycle_episodes.csv`: E0 2019 investment year, E1 2020 COVID, E2 2H22 deceleration/FX, E3 2023 ADR normalisation, E4 2025 NA slowdown, E5 2026 reacceleration; revenue/nights/GBV/ADR y/y, each line's cash and GAAP y/y and % of revenue, restructuring, 31a statement IDs and quotes | for M6 |
| Point-in-time | `02_panel_provenance.csv` rows with `source in (letter_first_vintage, xbrl_first_vintage)`; `02_letter_vintages.csv` by letter | for the harness (WS10) |

Parameters supplied: none fitted. Constants worth quoting: 2023-25 revenue shares 18.7 / 25.0 / 33.8 / 22.5%; Adjusted EBITDA shares 9.1 / 22.9 / 48.8 / 19.1%;
Q1 discretionary timing +0.6 to +5.8 pt (2023-25), Q2 -2.2 to -4.0, Q3 -1.4 to +0.1, Q4 -0.2 to +3.9; ALOS 3.7 (FY2025); ops cash per booking $8.6 FY2025
(-7% y/y), per night $2.32 (-4%).

## For the 5 Nov card

Read on the print, in this order: the 3Q26 reconciliation (does the tax add-back carry a reserve? 3Q24 was +$58M; 3Q25 +$4M); `sbc_total_is` vs the footnote;
`interest_expense` (run-rate $37M/quarter on the notes, vs $6M a year ago; hits EPS/FCF, not EBITDA); `interest_income` vs $180M (funds held at 2Q26 $12.2B,
+10% y/y); ops cash per booking (3Q25 $9.50; management's -16% claim implies $8.0); S&M cash % of revenue in Q3 (2023-25 range 10.9-14.3%; 3Q25 14.3% was the
high); the Q4-implied margin from the FY floor once the 4Q guide is given, using the 18.3-20.2% Q4 share of FY EBITDA.

## RESUME

WS02 is complete and reproducible (`python analysis/src/margin_build/02_financial_panel/run.py`, exit 0, pass-line block printed at the end of
`02_build_log.txt`). The next agent should consume, not extend: WS10 builds the margin targets from `adj_ebitda_reported`, `adj_ebitda_margin_pct` and the
six `*_cash` lines (first-vintage values for the point-in-time columns are in `02_panel_provenance.csv`); M1 fits G&A on `ga_cash_ex_lodging` and ops on
`ops_cash_per_booking_usd` as well as per night; M2 takes the 2023-25 quarter shares from `02_seasonality.csv`; M6 takes `02_macro_cycle_episodes.csv`;
M7 takes the below-EBITDA and cash-flow columns (1Q24 interest expense is the one hole; the FY2024 10-K calls it immaterial, so carry $5M with a flag if a
value is needed). If a new letter lands (3Q26 on 5 Nov), drop it in `data/raw/letters/` with the `3Q26_` prefix and re-run; the parser validates every column
with the NI-to-EBITDA identity and the build log reports any drop. If 10-Qs arrive (WS04 GAP06), add the MD&A component deltas as new columns in a `_v2`
folder rather than editing this one.
