# WS01. Input census: everything in the repo that could move a cost line, an add-back or a below-EBITDA item

Margin build run, 13-14 Sep 2026. Slug `01_input_census`. Script `analysis/src/margin_build/01_input_census/run.py`
(`python`, exit 0). Outputs `data/processed/margin_build/01_input_census/01_input_census.csv` (123 rows),
`01_gaps.csv` (26 rows), `01_census_summary_by_line.csv`. Free parameters: 0 (this is a census, nothing is fitted).
Tests run: 0 statistical; 1 validation (every path exists, columns present, >= 10 concrete pulls) — passed.

**Pre-registered pass line (from the prompt):** census covers every `data/processed` folder and every research note;
every `file_path` exists; at least 10 candidate pulls with concrete sources for WS04. **Result: met** — 123 census rows
spanning all 39 `data/processed` sub-folders at package level, 123/123 paths exist (validated at run time), 25 of 26 gap
rows carry a URL pattern / LSEG field / EDGAR route. What I did not do is in "Skipped" at the end.

## Bottom line

1. **Margins have been modelled from the P&L alone, and the P&L work is thorough: 21 panels/notes already cover the six
   lines, with one promotable driver (cost of revenue on GBV, elasticity 1.01, n 14) and one pre-print predictor (prior-quarter
   S&M deleverage, r −0.62, n 14).** Every other elasticity fails; every macro/alt-data feature tested so far was tested against
   nights or revenue, never against a cost line or a below-EBITDA item. The census finds **56 series that bear on the revenue
   denominators, 44 on total margin, 31 on brand marketing, 26 on cost of revenue, 25 on ops & support, 17 on interest income and
   17 on tax** — but only ~8 of those have ever been paired with the line they could explain.

2. **The ten most promising inputs not yet used for margins, ranked by (size of the line × plausibility × reachability):**

   | # | Input | Line(s) | Why | Where / how | Method |
   |---|---|---|---|---|---|
   | 1 | **Interest-earning balances × short rates** | int_inc | Interest income is $705M (FY25, 5.8% of revenue) and falling; the repo has the balances (`rnpl_short_audit/qog_cash_reality_quarterly.csv`: cash, ST investments, funds held, implied annualised yield, 22 quarters) and FEDFUNDS/DGS2, but **the yield has never been regressed on a rate**; DTB3 is not cached | B05 + M02 + GAP04 (FRED DTB3/DGS3MO) | M7 |
   | 2 | **10-Q MD&A component deltas as a quarterly series** | cor, ops, pd, sm_brand, sm_field, ga | The only sub-line disclosure Airbnb makes (payroll, marketing activities, third-party providers, insurance, cloud, non-income taxes, $ per quarter); 07 has them **annually only**; 21 of 22 10-Qs are not in the tree | GAP06 (EDGAR submissions API, 22 filings) | M1 |
   | 3 | **Prior-quarter S&M deleverage** (known at the prior print) | margin_total | The one pre-print margin predictor: r −0.62 (perm p 0.017, n 14), LOO RMSE 2.61 vs guide 2.79 vs naive-last 3.03; exists in `predictive/04_print_features.csv` but is **not in any registered method** | G18/G19 | M2, M4 |
   | 4 | **Regional-mix ADR term as its own margin line** | margin_total, cor | −0.5 to −0.7 margin pt/yr (mix drag −0.5/−2.8/−1.1/−1.2/−1.6pp of ADR 2021-25); 31b has it, 07 and 30 fold it into "ADR ex-FX"; the regional panel and forecast exist | R04, R06, R07 | M1 |
   | 5 | **Nights per booking (ALOS) as the per-booking ↔ per-night converter** | ops, cor | Management's only quantified cost claims are **per booking** (support −10%/−16%); the line is modelled **per night**; ALOS (~4 nights, `airbnb_nights_per_booking.csv`, `adr/14b_los_bucket_shares.csv`) is the bridge and has never been used in a cost model | R21 | M1 |
   | 6 | **Unrecognised SBC, unvested RSUs, period-end shares, monthly buyback table** | sbc, shares | Forward SBC floor (12-month unrecognised expense in the 10-K), vest schedule and a period-end (not weighted) share count; all in XBRL/10-K but never extracted | GAP18, X01 | M7 |
   | 7 | **Headcount proxies: Wayback job-posting counts + tech-wage indices** | pd, ga, ops, sbc | PD is payroll (FY25 +$293M of +$298M was headcount); headcount is disclosed once a year; open-role counts lead hires; CES software-publisher wages deflate the plan into $ | GAP01, GAP03 | M4 |
   | 8 | **Hosting-commitment schedule (10-K Note 13)** | cor | $672M-through-2027 became $1.7B-through-2031 (≈$280M/yr vs ≈$220M run-rate); purchase obligations $719M → $1,749M; leads CoR-ex-payments by 4-8 quarters | P04, GAP11 | M1, M4 |
   | 9 | **Peer cost flex in downturns** (BKNG/EXPE/MAR/HLT marketing and margins) | sm_brand, margin_total | The cycle model needs episodes; ABNB has four shocks (M04) but BKNG/EXPE have 2009/2020/2022 marketing cuts in XBRL; peers also **print ~8 days before ABNB** (M11) | GAP07, M11, P11 | M6 |
   | 10 | **Tax-rate reconciliation and DTA run-down** | tax, fcf_timing | Cash taxes $232M vs $626M provision (FY25); as released DTAs are used, FCF loses 2-3pt of revenue; the 10-K tables are in the tree, never tabulated | GAP17, X02 | M7 |

   Honourable mentions: support-load proxies (Trustpilot/BBB/app-store counts via Wayback, GAP08) for the AI-deflection claim;
   a dated sponsorship/campaign calendar (IOC TOP partner 2021-28, Paris 2024, Milan-Cortina 1Q26; GAP16) for brand seasonality;
   Google Trends vs S&M spend (the repo has 12,454 weekly rows tested only against nights, M09/GAP15); Bloomberg `BEST_EBITDA`
   revision history (L01) for M5; the adj. EBITDA definition's **add-back of non-income-tax reserves** (see mechanisms, G&A).

3. **What is already tested, so nobody re-runs it:** prior-quarter ops-per-night y/y, take-rate change, SBC-ratio change, CPI
   lodging y/y, letter FX, guide width and prior beat all **fail LOO** against the guide bound for the margin surprise (n 14,
   `predictive/04_margin_predictability.csv`); 1,408 macro pairs and 598 alt-data features fail against nights/revenue (WS05, WS08);
   Google Trends 0 of 162 vs nights; unearned fees 1.85× AR(1) walk-forward (kill list); five of six cost-line elasticities are not
   identified on n 14 (31b). None of the macro or alt-data tests targeted a cost line.

4. **Consensus for EBITDA exists at only 8 of 23 prints** (`16_consensus_at_print_merged.csv`); the Bloomberg file is a revision
   history anchored on the pull date; WS03's LSEG pull is the only route to a point-in-time Street margin (GAP21).

## Census summary by target line

From `01_census_summary_by_line.csv` (a series can map to several lines).

| Target line | Series | Available | Needs refresh | Licensed local | Gaps (candidate pulls) | of which priority 1 |
|---|---|---|---|---|---|---|
| cost of revenue (cor) | 26 | 25 | 1 | 0 | 6 | 1 |
| operations & support (ops) | 25 | 23 | 2 | 0 | 8 | 2 |
| product development (pd) | 22 | 20 | 2 | 0 | 5 | 2 |
| brand + performance marketing (sm_brand) | 31 | 28 | 2 | 0 | 6 | 1 |
| field operations & policy (sm_field) | 28 | 27 | 1 | 0 | 1 | 1 |
| G&A (ga) | 23 | 20 | 2 | 1 | 7 | 2 |
| SBC | 29 | 27 | 1 | 1 | 4 | 2 |
| D&A | 10 | 10 | 0 | 0 | 1 | 0 |
| other add-backs | 2 | 2 | 0 | 0 | 1 | 0 |
| interest income | 17 | 16 | 1 | 0 | 3 | 2 |
| other income / expense | 7 | 7 | 0 | 0 | 1 | 1 |
| tax | 17 | 16 | 1 | 0 | 1 | 1 |
| share count | 13 | 12 | 1 | 0 | 2 | 2 |
| FCF timing (unearned fees, funds payable, WC) | 16 | 16 | 0 | 0 | 1 | 1 |
| capex | 8 | 8 | 0 | 0 | 0 | 0 |
| revenue drivers (nights, GBV, ADR, take, FX, mix) | 56 | 55 | 1 | 0 | 1 | 0 |
| total margin | 44 | 42 | 1 | 1 | 2 | 1 |
| guidance / consensus / language | 29 | 27 | 0 | 2 | 1 | 1 |

Status totals: 115 available, 3 needs_refresh (FRED cache, Google Trends, 10-Qs), 4 licensed_local (Bloomberg ×2, FactSet,
LSEG bodies), 1 candidate_pull (Similarweb template). Gap rows: 26, 7 at priority 1 (GAP01 job postings, GAP04 T-bill, GAP05
funds-held yield split, GAP06 10-Qs, GAP17 tax reconciliation, GAP18 share/RSU path, GAP21 LSEG consensus).

Coverage by `data/processed` folder (all 39 sub-folders touched at package level): root panels (25 rows), `overnight` (44),
`predictive` (6), `adr` / `adrv3` / `adrq3` (6), `forecast_methods` (6: harness, L0, fx_lag_v2, fee_takerate, tracker_backlog,
regional_kernel_v1 via GAP10), `h2_bridge_v3`, `q3nowcast` E/G, `overnight2` B/D, `govdata` V/P, `reverse_dcf`,
`rnpl_short_audit`, `listing_churn_*`, `fee_churn_history`, `peer_readthrough` (via predictive/02), `hotel_*` (revenue-side only,
listed under R24's source inventory), raw stores (9 rows), licensed (4), Theo/Crossover (2), workbooks (2).

## 01_line_mechanisms

Definitions are quoted from the FY2025 10-K MD&A (`data/raw/filings/txt/abnb_10k_FY2025.txt`); dollar deltas are the 10-K
year-on-year explanations tabulated in `overnight/07_cost_components_annual.csv`; management statements are 31a IDs; WS31 assumptions
are `overnight/31b_overlay_parameters.csv` (historical trend / management / base, FY26-28).

**Cost of revenue (17.0% of revenue FY25, cash).** 10-K: "payment processing costs, including merchant fees and chargebacks, costs
associated with third-party data centers used to host our platform, and amortization of internally developed software and acquired
technology. As the merchant of record, we bear all payment processing costs." Economics: merchant fees + chargebacks 1.82% of GBV
(FY25, derived from MD&A deltas since the FY21 level; chargebacks alone $67M FY25); the non-payments remainder is ~$421M and
is hosting (+$27M/yr deltas; server costs +$15M 1H26 on reserved-instance amortisation) plus software amortisation. Drivers: GBV
dollars (× card-scheme rate × cross-border/FX share × alternative-payment mix), chargeback rate (RNPL and cancellation-policy
exposure), hosting commitment step, AI inference. Repo proxies: GBV and its FX (P05, R09-R12), cross-border share to 1Q24 and the
X-package O-D matrix (GAP10), hosting commitments (P04), fee timeline for the guest FX fee (R15). WS31: elasticity to GBV 1.01
(t 3.3, LOO 0.96-1.11, the only promoted line); per-$-GBV trend −1.3%/yr; base overlay **+1.0/+1.0/+0.5%** per $ GBV for the
hosting step; management "scale somewhat linearly" (S146). 55% of the line is treated as non-USD.

**Operations and support (10.1%).** 10-K: "personnel-related expenses and third-party service provider charges associated with
community support provided via phone, email, and chat to customers; customer relations costs, which include refunds and credits
related to customer satisfaction and expenses associated with our host protection programs; and allocated costs for facilities and
information technology." FY25 +$45M: payroll +$33M, insurance +$14M ("higher premiums as a result of higher nights booked"),
facilities +$11M; 13,000 third-party support workers. Economics: contacts = bookings × contact rate; cost = contacts × (1 −
AI deflection) × cost per human contact + insurance premium per night + refunds/credits (a function of cancellations, which RNPL
raised ~1pt) + host-protection payouts. Repo proxies: nights (P05), nights per booking (R21), AI-deflection statements 15% → 33% →
>40% → ~45% and per-booking cost −10%/−16% (G06, GAP26), insurance deltas (P04), quote-panel discounts/coupons (A07, contra-revenue
side), complaint counts (GAP08, not pulled). WS31: elasticity to nights 1.39 (LOO 0.41-1.66, **imposed 1.0**), per-night trend
−2.5%/yr, base **−4.0/−4.5/−4.5%** per night; 1H26 realised −3.8%; estimation risk ±1.1/−1.5pt at FY28. Contra-revenue: part of
support investment is booked against revenue (2Q24 letter), never sized.

**Product development (10.9% cash; 20.8% GAAP in 1H26).** 10-K: "personnel-related expenses and third-party service provider
expenditures incurred in connection with the development of our platform, and allocated costs for facilities and information
technology." FY25 +$298M of which **+$293M payroll on headcount**; SBC in PD $1,017M (64% of all SBC). Economics: engineering
headcount × cash comp per head (+ SBC per head $193k) − AI tooling productivity (claimed +30% since 1Q23, no filed evidence:
revenue per employee fell 1.8% in 2025). Repo proxies: annual headcount (P04), SBC by function (P02), statements S144/S163
(headcount growth below FY25's ~12%); nothing quarterly — hence GAP01 (job postings), GAP03 (wage index), GAP22 (WARN).
WS31: elasticity to revenue −0.69 (not admissible, imposed 0), cash growth trend +11.3%/yr, base **11/9.5/9%**; fixed share 32%.

**Sales and marketing — brand and performance (13.0%) and field operations and policy (6.4% cash).** 10-K: "brand and performance
marketing, personnel-related expenses, including those related to our field operations, policy and communications, portions of
referral incentives and coupons, and allocated costs." FY25: B&P $1,595M (+10%), field ops $993M (+43%); deltas +$163M marketing
activities, +$121M payroll, +$102M third-party providers. Economics, brand: fixed campaign flights (Q1 global campaign; Olympic
partnership 2021-28) + expansion-market budgets (count undisclosed) + performance CPC (bid intensity vs BKNG/EXPE; a future AI
referral fee, R20). Field: go-to-market headcount for new businesses (Services/Experiences launch May 2025, hotels), supply
acquisition, policy/communications, referral incentives to hosts. Repo proxies: Google Trends (M09; search per $ of brand spend
never computed), BKNG alt-accom competition (M12), peer marketing ratios (M11/P11), supply and churn panels as the replacement-supply
need (A01-A06), new-business revenue (R19), AI exposure (R20), quote-panel discounts (A07), call theme shares (G09), the
`marketing_commentary` column in the KPI panel; not in repo: ad trackers (GAP14), campaign calendar (GAP16), Similarweb paid share
(GAP23). WS31: brand elasticity 1.19 (LOO 0.42-1.89, imposed 0), trend +16.5%, base **27/15/12%**; field trend +24.3%, base
**18/13/11%**; brand fixed share −2% (the "fixed per market" model is unidentified). Reliability: brand statements 63% kept (n 35),
the FY24 "largely the same" guide missed by 157bp. The predictive study's one pre-print margin signal is this line's deleverage.

**General and administrative (8.7%).** 10-K: "personnel costs for management and administrative functions (finance, accounting,
legal, human resources), professional services fees, corporate and director and officer insurance, allocated costs for facilities
and information technology, and indirect taxes, including lodging tax reserves." Deltas: non-income taxes −$656M (FY24, lapping
the FY23 Italian reserve), +$74M (FY25), −$38M (1H26). Economics: corporate headcount + legal/regulatory (fines, settlements,
lodging-tax reserves, litigation) + insurance. **Important for WS02/M7:** the adj. EBITDA definition adds back "settlements and
reserves for lodging, withholding, transactional and other non-income taxes where significant uncertainty exists" — so these items
inflate GAAP G&A and `other_addbacks` together and are neutral to adjusted EBITDA; strip both to see underlying G&A. Repo proxies:
regulatory events and Monte Carlo (A08, X08), 10-K reserve sentences (GAP19), headcount (P04). WS31: elasticity to revenue 4.59
(R² 0.06, imposed 0), trend +9.6%, base **3/5/5%**; fixed share 61% (the most fixed line; the bear-case cushion).

**SBC (13.1% of revenue FY25; ops 90 / PD 1,017 / S&M 212 / G&A 273).** Drivers: headcount × grant value per head (share price at
grant, B08/B09) × vest schedule; unrecognised SBC and weighted remaining period in the 10-K equity note set a 12-month floor (GAP18).
Guided: growth below FY25's (S144); reliability 40% kept (n 5). Not projected by 31b; 07 uses +13/10/8%; capital-return note: ratio
flattens ~13%. Series: P02 (by line), B02, X01 tags.

**D&A and other add-backs (0.7% and 0.9% of revenue).** D&A: depreciation $17M + amortisation of capitalised software and acquired
intangibles (in CoR); capex $33M/yr ("not building data centers", S-series 4Q23/4Q25/2Q26). Other add-backs: acquisition-related
contingent consideration, non-income-tax settlements/reserves (above), IPO stock-settlement obligations (historic). Held at 0.9%
in 07/31b; WS02 should split D&A from the tax-reserve add-back because the latter is lumpy.

**Interest income ($705M FY25; $338M 1H26 vs $363M).** 10-K: "interest earned on our cash, cash equivalents, marketable securities,
and amounts held on behalf of customers." Economics: blended yield × (corporate cash + ST investments ≈ $12B + funds held ≈ $6-10B,
seasonal peak 1Q/2Q); RNPL shrinks the customer float; the split of income between corporate and customer balances is never
disclosed (GAP05). Repo: B05 implied annualised yield on interest-earning balances (22 quarters), M02 FEDFUNDS/DGS2/DGS10, B01/P03
interest income series; not in repo: DTB3/DGS3MO (GAP04). 07: $660/620/590M FY26-28; 30/13 model carries $170M/quarter.

**Interest expense (~$120-125M/yr from 2026).** $2.5B IG notes issued Mar 2026 at 4.40-5.25% ($37M in 2Q26); folded into other
income in the 1Q24-4Q25 letters (B01 `source_letter` handling). Below adjusted EBITDA; hits FCF and EPS.

**Other income (expense), net (−$112M FY25).** FX remeasurement on net monetary assets (10% adverse move ≈ $38M, Item 7A),
non-designated hedge gains/losses (B07: notional and AOCI 1Q23-2Q26), investment marks. Repo: B01, B07, R09 FX; XBRL
`OtherNonoperatingIncomeExpense` (X01, unpulled).

**Tax (provision $626M FY25, ETR 20%; cash taxes $232M).** Guided high teens FY26, mid-to-high teens long term under OBBBA (S157,
S179); the 3Q23 $2.7B valuation-allowance release created DTAs whose use keeps cash taxes below the provision until they run
down (the residual in B01). Repo: B01, P03, P04 (current/deferred split annual), 07 cash-tax path 2.6/3.4/4.0% of revenue;
not tabulated: the rate reconciliation and DTA schedule (GAP17).

**Share count (diluted 597M 2Q26, −4.6% y/y).** Buybacks ~$1.0-1.1B/quarter ($3.4B authorisation left Aug 2026), RSU withholding
~$130-165M/quarter, SBC issuance; $1.4B per 1% of count. Repo: B02, B03, B08 (price), B10 (reverse-DCF buyback assumptions);
not extracted: period-end shares (dei tag), monthly repurchase table, unvested RSUs (GAP18).

**FCF timing (unearned fees, funds payable, working capital).** CFO = adj. EBITDA + interest − tax − other + Δ unearned fees +
residual; the residual is −1.1% of revenue in FY24 and FY25 (07); Δ unearned fees fell from +$278M (FY22) to −$26M TTM as RNPL moved
collection toward check-in. Repo: B01, B04, B05, B06, R26, R27. Kill list: restated unearned fees (`reported/(1−d)`) is circular.

**Capex (0.3% of revenue).** $25-47M/yr 2021-25; P04, B01. No AI capex ("not buying GPUs", 2Q26).

## Corrections to existing work

1. `research/notes/predictive/04_margin-and-reaction.md` §6 still says FY floors are "beaten by 60 to 180 bps every year"; 31a
   established 60-140bp (FY24 +140, FY25 +60). Carry 60-140bp.
2. `data/README.md` lists `raw/xbrl/ABNB.json, BKNG.json, EXPE.json`; in this worktree only `data/raw/xbrl/ABNB_companyfacts.json`
   is junctioned. BKNG/EXPE companyfacts must be re-pulled for the peer cycle work (GAP07).
3. The brief says the repo venv `python` has openpyxl; in the bash tool `python` resolves to `C:/Users/krish/citadel-abnb/.venv`
   (3.11) which does not have it. Use `py -3.13` for any `.xlsx` read; `run.py` here needs only pandas.
4. Not an error but a modelling trap for WS02/M1: non-income-tax settlements and reserves sit in GAAP G&A **and** in adj. EBITDA
   add-backs (definition above), so a cash-G&A series that keeps the FY23 Italian reserve without the matching add-back double-counts;
   the 22-quarter identity in `abnb_quarterly_cost_stack_exsbc.csv` holds, so the existing stack is consistent, but the FY23 G&A
   "+1,160bp distortion" quoted in 31a is a GAAP-line statement, not an adjusted-EBITDA one.
5. `07_cost_components_annual.csv` `payment_processing_cost` from FY22 on is accumulated MD&A deltas (the CSV's `source` column says
   so); 31b and this note quote 1.82% of GBV as ±10bp. Keep that caveat attached wherever the rate is used.

## For the model

WS01 supplies no parameters. It supplies the routing table below (series → line → method) and the point-in-time lag convention
to be used by WS10 when it stamps features at guide dates: letter/print series 40 days after quarter end; 10-Q detail 42-45;
10-K detail 50-60; FRED monthly 1-15; daily rates/FX 0-1; Inside Airbnb dumps 35; Eurostat 150; management statements and consensus
at the event date; peer prints −8 (before ABNB).

| Line | Read history from | Per-unit basis | Driver series | Overlay / statement source | Method owner |
|---|---|---|---|---|---|
| cor | P02 `cor_cash`, P03 `cor_cash_per_100gbv` | $ per $100 GBV | P05 GBV; R09-R12 FX; GAP10 cross-border; P04 hosting commitment | S146; 31b base +1.0%/yr | M1 (+M4 hosting/payments steps) |
| ops | P02 `ops_cash`, P03 `ops_cash_per_night` | $ per night (convert per booking via R21 ALOS) | P05 nights; GAP26 AI step series; P04 insurance delta | S151/S152/S160; 31b base −4.0/−4.5 | M1 (+M4 support proxies GAP08) |
| pd | P02 `pd_cash` | $ per employee, cash growth | P04 headcount; GAP01/GAP03 | S144/S163; 31b base 11/9.5/9 | M1 (+M4 headcount) |
| sm_brand | P03 `sm_brand_perf_musd` | cash growth; $ per night | M09 Trends; M11/GAP07 peers; GAP14/16 | S147/S153/S108; 31b base 27/15/12 | M1/M4/M6 |
| sm_field | P03 `sm_field_ops_musd` (GAAP less all S&M SBC) | cash growth | R19 new business; A01-A03 supply need | S127/S135; 31b base 18/13/11 | M1/M6 |
| ga | P02 `ga_cash` | cash growth; strip reserves (GAP19) | P04 headcount; A08/X08 regulatory | S157/S148; 31b base 3/5/5 | M1 |
| margin_total | P01/P02 `adj_ebitda_margin_pct` | % revenue | G18 lagged S&M deleverage; R04 mix; R10/R11 FX | G01/G03/G06 floors; G13/L01/GAP21 Street | M2, M3, M5, M6 |
| sbc | P02 SBC by line; B02 | % revenue; per employee | B09 price; GAP18 unrecognised SBC | S144 | M7 |
| int_inc | B01/B05 | yield × avg balances | GAP04 DTB3; M02 FEDFUNDS; B04 funds held | 07 levers | M7 |
| tax | B01; P04 current/deferred | ETR; cash tax % revenue | GAP17 reconciliation; R08 geography | S157/S179 | M7 |
| shares | B02; B08 | count path | B09 price; GAP18 | capital-return note | M7 |
| fcf_timing | B01/B04/B05/B06 | % revenue | R26 RNPL share | 07 residual −1.1% | M7 |

## For the 5 Nov card

Inputs that will update before the print, in order of when they land: FRED rates and FX daily (R09/M02; the 4Q26 FX line from R11
re-stamps weekly); Google Trends weekly with a stamped pull date (GAP15); Similarweb/app-store captures (GAP23/GAP14) monthly;
Inside Airbnb September dump (~mid-Oct, A02); peer prints HLT 21 Oct, BKNG ~28 Oct, MAR ~3 Nov (M11: BKNG marketing and margin are
the same-quarter cost-cycle read); LSEG consensus daily (GAP21/WS03); the 3Q26 10-Q on 5 Nov itself (brand vs field split, S&M
deleverage, support commentary, interest income vs $180M, CoR per $100 GBV vs $2.40 — the items 07 §8 lists). The lagged S&M signal
for 3Q26 is already fixed (2Q26 deleverage +9.9pt → 49.8% vs the 50.1% ceiling, sd 2.6pt).

## Skipped (breadth over depth, per the prompt)

- The 69 registry files under `forecast_methods/registry/` and the `*_prev*` folders are covered at package level (G15, R11, R16,
  B06), not row by row; none carries a margin object.
- `research/notes/overnight/14_master-synthesis.md` (124 KB) was read through the 6 Sep inventory, not in full.
- Model workbooks (`model/*.xlsx`) are listed with sheet-level descriptions from the inventory; not opened (no openpyxl in `python`).
- Theo's OneDrive `processed/` and `metadata/` folders and the Third Bridge digests were not enumerated (revenue-side content;
  the licensed items are listed as L01-L04).
- Hotel workstream folders (`hotel_13_market_panel`, `hotel_funnel_audit`, `hotel_rollout_economics`, `hotel_expanded_research`)
  are revenue/optionality inputs and are represented only through R19 and R24's source inventory.
- `docs/q3nowcast`, `docs/overnight2`, `docs/govdata`, `docs/adrv3`, `docs/reverse_dcf` SYNTHESIS files were used for the series
  descriptions, not re-read for margin content (they have none beyond what 07/31 already carry).

## RESUME

WS01 is complete: `01_input_census.csv` (123 rows), `01_gaps.csv` (26 rows, 7 priority-1), `01_census_summary_by_line.csv`, this
note and the validating `run.py` (exit 0). The next agent should not extend the census; it should consume it. WS04 takes `01_gaps.csv`
as its pull list in priority order (GAP04 T-bill, GAP06 10-Qs, GAP17 tax tables, GAP18 share/RSU path, GAP01 job postings, GAP05
funds-held split, then GAP07-GAP08-GAP16), writing raw to `data/raw/margin_build/04_alt_signals/` with a manifest. WS02 should
read the "01_line_mechanisms" section for the G&A/add-back double-count trap and the ALOS converter, and pull the 10-Q component
deltas quarterly (GAP06) into its provenance file. M1 should start from the routing table in "For the model" and register the
regional-mix and ALOS terms as explicit lines; M7 should build interest income as yield × balances (B05 + GAP04) before anything
else, because it is the largest unmodelled below-EBITDA item. If the census must be re-run after new files land, add rows to the
`REG` list in `run.py` (one `R(...)` call each) and re-run; the script validates paths and rewrites all three CSVs.
