# RNPL: the full management statement ledger, and the cohort timing arithmetic for 3Q26 and 4Q26

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Workstream:** overnight run D. Branch `krish/overnight-2026-09-11`.
- **Scripts:** `analysis/src/overnight2/D0_rnpl_statement_ledger.py`, `analysis/src/overnight2/D1_rnpl_cohort_scenarios.py`.
- **Outputs:** `data/processed/overnight2/D/` (nine CSVs, listed at the end).
- **Reads, read-only:** the main tree at `C:\Users\krish\citadel-abnb` for transcripts, letters, filings, the newsroom archive and the KPI panel; `origin/krish/nights-quarterly` and `origin/jessie/backlog-conversion` for the parallel models.
- **Nothing here touches the live model, the workbook or any other workstream's paths.**

## 1. Bottom line

1. **There are two quantified bundle contributions on record, not one.** The RNPL handoff carries only the 1Q26 figure of approximately three points of nights growth and four points of GBV growth. The 4Q25 call carries an earlier one: "we estimate these three features delivered over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4" (ledger D014). The 2Q26 call gave an update on two of the three features and dropped the figure entirely. So the disclosed sequence is more than 2.0 points in 4Q25, about 3.0 points in 1Q26, and silence in 2Q26. Whether the figure returns on 5 November, and at what level, is the most direct read available on whether the lap is biting.

2. **The international rollout is now pinned, and it answers PR #32's top open question.** The worldwide announcement is dated 17 February 2026. The local newsroom archive holds the market-level posts: United Kingdom 18 February, Australia 23 February, Asia Pacific 23 February, Canada 4 March 2026. Eligibility is excluded by payment currency, not by country: Brazilian Real, Indian Rupee and Turkish Lira reservations are ineligible. Every go-live sits inside 1Q26, so the ex-North-America RNPL anniversary falls in 1Q27, not in 2026. Two consequences. First, Canada is in North America but only got RNPL in 1Q26, so PR #32's "NA only" 2025 cohort is really United States only. Second, the ex-NA go-lives landed in roughly the last five to six weeks of a thirteen-week quarter, so the 1Q27 lap is a partial-quarter lap and PR #32's flat minus 1.75 points from 1Q27 is too large in 1Q27 and about right from 2Q27.

3. **The cancellation redesign is dated, which closes PR #32's weakest input.** PR #32 lists the cancellation-redesign date as "not disclosed" and its caveat 2 says that if it landed later, more of the bundle laps in 2027. The 4Q25 letter dates it: "In October, we announced new cancellation policies to make it easier for guests to book a stay, even if their plans change. Hosts can now offer free cancellation up to 14 days before check-in under a new Limited policy" (D060). October 2025, global, the same window PR #32 assumed. The assumption is vindicated, but the geography is not: the redesign and the single fee are global in the letters, and PR #32 laps them in North America only.

4. **PR #32 and management agree, and the agreement survives an out-of-sample test.** PR #32 allocates 1.35 points of management's approximately 3.0 global points to North America at a 28.8 percent nights share, and 1.75 to ex-NA. That totals 3.1 against management's 3.0, which is agreement by construction because the ex-NA term was solved from the same disclosure. The 4Q25 figure is a genuine out-of-sample check, because PR #32 does not use it. In 4Q25 ex-NA RNPL was zero, so the ex-NA bundle then was the fee and cancellation legs alone. PR #32's parameters reproduce management's "over 200 basis points" only if those two legs are roughly 40 to 50 percent of the ex-NA bundle. That pins a parameter PR #32 leaves free, and the same parameter then sizes the gap in point 5.

5. **The ledger opens a 0.7 to 0.9 point hole in the 4Q26 baseline, which is the quarter the trade is on.** The cancellation redesign and single-fee tranche 1 were global from October to December 2025, so their year-over-year windows close everywhere from 4Q26. PR #32 laps them in North America and holds ex-NA at WS10, which carries no lap at all. At the 40 to 50 percent split pinned by the 4Q25 disclosure, the missing ex-NA lap is 0.70 to 0.88 points of total nights, putting 4Q26 at **8.0 to 8.2 percent (131.7 to 131.9mm)** rather than the team baseline of 8.9 percent (132.7mm). This is arithmetic on sourced dates plus one pinned split. It is not a model change and has not been applied anywhere.

6. **The cancellation drag itself is small relative to the level lap, in every scenario.** Across 2,025 parameter cells the incremental reported-nights effect of an RNPL cancellation-propensity assumption is **minus 0.10 to minus 1.37 growth points in 3Q26** and **minus 0.08 to minus 1.36 in 4Q26**, once both years are modelled. In the central cell the range is minus 0.15 points at a plus 1 point propensity, minus 0.62 at plus 4 points, and minus 0.93 at the management-implied plus 6.0 points. The level lap, by contrast, is 1.35 points of total nights by 4Q26 from the North American bundle alone, plus the 0.70 to 0.88 ex-NA piece above. **The anniversary is two to fifteen times the cancellation drag.** The original bridge's minus 1.5 to minus 2.5 point RNPL overlay is only reachable at the top of this grid, and then only by combining the management-implied propensity with zero rebooking and the shortest lead time.

7. **The reason the drag is small is the thing the hypothesis has to overcome: the cancellation drag laps too.** The 2025 base already contains United States RNPL from 3Q25. Modelling both years, as the handoff requires, means the prior-year denominator carries its own excess cancellations. What remains is the year-over-year increase in excess cancellations, driven by the increase in RNPL share. That increase was large into 1H26, when the share went from roughly nothing to 20 percent, and it is much smaller into 2H26, when it goes from an assumed 4 to 9 percent to an assumed 22 to 23 percent against a base that already had the product live.

8. **The sharpest sourced mechanism is the payment deadline, and it puts the cancellation in the stay quarter.** Airbnb states that RNPL payment falls due "shortly before the end of the listing's free cancellation period" (D002), and the free window is 24 hours before check-in for flexible, five days for moderate, and 14 days under the new Limited policy (D012, D060). So the moment at which an RNPL reservation can fail is days before check-in, not days after booking. With a mean booking-to-check-in lead time of about 2.2 months, derived below, **46 percent of the excess cancellations recognised in 3Q26 come from bookings made in earlier quarters, and 49 percent in 4Q26.** That is the cancellation tail, sized.

9. **Management's net-benefit claim is not a claim about reported nights.** The 4Q25 call says the product was tested "to ensure that by the time the cohorts opting into the product had reached their check-in date, that it was net beneficial to the business, meaning that the growth lift in bookings was larger than the net increase in cancellations before check-in" (D019). That is a stay-date test on a booking cohort. Reported Nights and Seats Booked is a transaction-period metric in which a cancellation reduces the quarter it occurs in, not the quarter of the booking (D054). A product can pass management's test and still move nights between reported quarters. This is the single cleanest statement of why the hypothesis is not closed by management's testing commentary, and equally why its magnitude is bounded.

10. **There is one dated, official, forward-testable prediction in the whole record, and it is about 3Q26.** The 1Q26 letter says RNPL "results in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3" (D038). Unearned fees ran plus 0.4 percent year over year in 1Q26 and minus 0.9 percent in 2Q26 against GBV growth of 19.2 and 15.7 percent. The FY2025 10-K says unearned fees normally fall sequentially in Q3 as check-ins peak (D055), so the test has to be year over year, not sequential. Pre-registered thresholds are in section 5.

## 2. Tables

### 2.1 The quantified record, in date order

Every figure below is verbatim in `rnpl_statement_ledger.csv`, with its basis and scope. The ledger holds 60 statements, 33 from official sources (shareholder letters, 10-K, 10-Q, Airbnb newsroom) and 27 from the stockanalysis.com call transcripts, which are mirrors rather than the official IR PDFs.

| Date | Figure | Basis | Scope | Night weighted | Source | ID |
|---|---|---|---|---|---|---|
| 2025-08-14 | $0 upfront, payment due shortly before the free-cancellation window closes | payment schedule | US guests, US domestic, flexible or moderate policy | n/a | newsroom | D001, D002 |
| 2025-11-06 | about 70% | take-up among guests offered the product, headcount | US eligible subset | no | 3Q25 call | D005 |
| 2025-11-06 | 14 days / 24 hours / 7 days / 28 nights | cancellation-policy parameters | global | n/a | 3Q25 letter | D012 |
| 2025-08-06 | minus 7% | average lead time, y/y, April 2025, pre-RNPL | global | no | 2Q25 call | D011 |
| 2026-02-12 | over 200bp nights, roughly 300bp GBV | y/y growth contribution of the three features combined | global | yes (nights leg) | 4Q25 call | D014 |
| 2026-02-12 | about 1 point; 16% to 17% | platform aggregate cancellation rate, unit of account not stated | global platform | no | 4Q25 call | D017, D018 |
| 2026-02-12 | over 70% | adoption among eligible bookings, measured on global GBV in 4Q25 | global eligible subset | no | 4Q25 letter | D022 |
| 2026-02-12 | 15.5% | host service fee, PMS hosts from October, most non-PMS single-fee hosts from December | global | n/a | 4Q25 letter | D024 |
| 2026-02-12 | October 2025 | cancellation-redesign announcement date | global | n/a | 4Q25 letter | D060 |
| 2026-02-17 to 2026-03-04 | 3 excluded currencies (BRL, INR, TRY) | currency-level exclusion | global | n/a | newsroom | D025 to D029 |
| 2026-05-07 | roughly 20% | share of global GBV booked in the quarter | global | no | 1Q26 letter | D031 |
| 2026-05-07 | about 3 points nights, 4 points GBV | y/y growth contribution of the three features combined | global | yes (nights leg) | 1Q26 call | D032 |
| 2026-05-07 | over 25% | active listings on the single service fee | global supply | no | 1Q26 call | D041 |
| 2026-05-07 | about 1 growth point | reported nights growth lost to conflict cancellations | global KPI | yes | 1Q26 letter | D042 |
| 2026-05-07 | lower in Q1 and Q2, higher in Q3 | unearned fees, RNPL timing effect | global | no | 1Q26 letter | D038 |
| 2026-08-06 | over 20% | share of total GBV booked in the quarter | global | no | 2Q26 call | D043 |
| 2026-08-06 | July 2026 | expansion of eligible booking types, types unnamed | not specified | n/a | 2Q26 call | D044 |
| 2026-08-06 | about 50% | active listings on the single service fee | global supply | no | 2Q26 call | D047 |
| 2026-08-06 | 13.2% | implied take rate, moved by booking-versus-stay timing | global | no | 2Q26 letter | D049 |
| 2026-08-06 | low double digits | 3Q26 nights guide | global | yes | 2Q26 letter | D052 |

Four basis traps the ledger records explicitly.

- **The two 70 percent figures are different statistics.** The 3Q25 call's "about 70% of people that we offer" is headcount among United States guests offered the product. The 4Q25 letter's "over 70% adoption by eligible bookings" carries the footnote "Adoption percentage based on global GBV in Q4 2025". One is people and United States, the other is dollars and global. They cannot be chained into a series.
- **The 16 to 17 percent remark is hedged three ways in one sentence.** "An average of maybe 16% cancellation rate historically going to 17%" gives no base period, no denominator, and no statement of whether the rate is per booking, per night or per dollar. It is 4Q25 vintage. The approximately 20 percent GBV share is 1Q26 vintage. They are different periods and must not be combined into a same-period causal estimate.
- **Only eight of 60 statements have a night-weighted basis**, and six of those are growth-point contributions rather than levels. No night-weighted RNPL cancellation rate, eligibility share, take-up share or backlog share has ever been disclosed.
- **Two figures the main tree attributes to letters are call-only.** `data/processed/overnight/06_fee_timeline.csv` credits the 1Q26 and 2Q26 letters with the single-fee penetration figures of over a quarter and about half. Both are in the call transcripts; neither letter's fee paragraph carries a percentage. Worth fixing in the main tree.

### 2.2 The lap schedule, rebuilt from the ledger dates

| Feature | Live from | Geography | Y/Y window | Laps from | PR #32 fitted, NA points | Points of total nights |
|---|---|---|---|---|---|---|
| RNPL, United States | 3Q25 (call: beginning of Q3; letter: August) | US guests, US domestic, flexible or moderate policy | 3Q25 to 2Q26 | 3Q26 | 2.40 | 0.69 |
| Updated cancellation policies | October 2025 | global | 4Q25 to 3Q26 | 4Q26 | jointly 2.29 | jointly 0.66 |
| Single fee, tranche 1 | October 2025 PMS, December 2025 most remaining single-fee hosts | global | 4Q25 to 3Q26 | 4Q26 | jointly 2.29 | jointly 0.66 |
| RNPL, rest of world | 17 Feb 2026 worldwide; UK 18 Feb, AU 23 Feb, CA 4 Mar | global ex BRL, INR, TRY payers | 1Q26 to 4Q26, partial in 1Q26 | 1Q27 partially, 2Q27 fully | n/a | 0.87 to 1.05 |
| Cancellation redesign and fee tranche 1, ex-NA | October to December 2025 | global | 4Q25 to 3Q26 | 4Q26 | not modelled | 0.70 to 0.88 |
| Single fee, tranche 2 | announced July 2026, completing during 2026 | global | from migration | not before 3Q27 | 0.0 | 0.0 |
| RNPL, expanded booking types | July 2026 | not specified | 3Q26 onward | 3Q27 | not modelled | unknown |

The decomposition closes on management's disclosure. North America 1.35, plus ex-NA fee and cancellation 0.70 to 0.88, plus ex-NA RNPL 0.87 to 1.05, totals 2.9 to 3.3 points against the approximately 3.0 points management attributed to the bundle in 1Q26. Every row's date is sourced; only the split between the two ex-NA legs is inferred, and it is pinned by the 4Q25 disclosure.

### 2.3 The cancellation scenario grid

Incremental reported-nights effect, in growth points, against the team baseline of 3Q26 plus 9.89 percent and 4Q26 plus 8.90 percent. Central cell: central share path, RNPL ADR 25 percent above non-RNPL, 2.2-month mean lead time, 7 percent RNPL lead-time uplift, 25 percent same-quarter rebooking offset.

| Incremental RNPL cancellation propensity | 3Q26 points | 3Q26 nights, mm | 3Q26 growth | 4Q26 points | 4Q26 nights, mm | 4Q26 growth |
|---|---|---|---|---|---|---|
| 0 points | 0.00 | 0.00 | 9.89% | 0.00 | 0.00 | 8.90% |
| plus 1 point | -0.15 | -0.23 | 9.74% | -0.14 | -0.23 | 8.76% |
| plus 2 points | -0.31 | -0.46 | 9.58% | -0.28 | -0.46 | 8.62% |
| plus 4 points | -0.62 | -0.91 | 9.27% | -0.57 | -0.93 | 8.33% |
| management-implied, plus 6.0 points | -0.93 | -1.37 | 8.96% | -0.85 | -1.39 | 8.05% |

Full grid across all 2,025 cells: 3Q26 minus 1.37 to minus 0.10 points excluding the zero-propensity cells, 4Q26 minus 1.36 to minus 0.08. The worst cell combines the high 2H26 share path, the management-implied propensity, a 1.8-month lead time and zero rebooking, and gives 3Q26 at 8.52 percent and 4Q26 at 7.56 percent. The management-implied propensity of 6.0 points is the excess needed for RNPL alone to explain the whole one-point rise in the platform cancellation rate, evaluated at the 1Q26 nights share of 16.7 percent.

### 2.4 The booking-quarter by cancellation-quarter matrix

Excess RNPL cancellations in millions of nights, central cell, management-implied propensity. Rows are booking cohorts, columns are recognition quarters. This is the handoff's next-steps item 4 made concrete.

| Booking cohort | 3Q25 | 4Q25 | 1Q26 | 2Q26 | 3Q26 | 4Q26 | Cohort total |
|---|---|---|---|---|---|---|---|
| 3Q25 | 0.158 | 0.099 | 0.034 | 0.012 | 0.004 | 0.001 | 0.308 |
| 4Q25 | | 0.328 | 0.207 | 0.071 | 0.025 | 0.008 | 0.640 |
| 1Q26 | | | 0.944 | 0.595 | 0.206 | 0.071 | 1.816 |
| 2Q26 | | | | 0.952 | 0.599 | 0.207 | 1.758 |
| 3Q26 | | | | | 0.989 | 0.623 | 1.612 |
| 4Q26 | | | | | | 0.941 | 0.941 |
| **Recognised in quarter** | **0.158** | **0.427** | **1.185** | **1.630** | **1.823** | **1.851** | |
| of which from earlier cohorts | 0% | 23% | 20% | 42% | **46%** | **49%** | |

The corresponding booking-quarter by stay-quarter matrix is in `D1_cohort_matrix_stay.csv`. At a 2.2-month mean lead time, about 55 percent of a cohort's nights are stayed in the booking quarter and 37 percent in the next, which is the timing bridge between the booked KPI and revenue.

### 2.5 The 4Q26 gap

| Ex-NA fee and cancellation share of the ex-NA bundle | Points missing from 4Q26 | Adjusted 4Q26 | Consistent with the 4Q25 disclosure |
|---|---|---|---|
| 40% | 0.70 | 8.20%, 131.9mm | yes |
| 50% | 0.88 | 8.03%, 131.7mm | yes |
| 70% | 1.22 | 7.68%, 131.3mm | no, implies a 4Q25 bundle of 2.6 points |
| 100% | 1.75 | 7.15%, 130.6mm | no, implies 3.1 points |

## 3. Method

**Ledger.** `D0_rnpl_statement_ledger.py` converts the source HTML to text, normalises typographic variants, and asserts that every quote appears verbatim in its source file before writing the CSV. All 57 file-sourced quotes pass. Three rows are recovered from the live Airbnb newsroom on 2026-09-11, for the 14 August 2025 United States announcement and the 17 February 2026 worldwide announcement, and are flagged `quote_verified = web_2026-09-11` because they cannot be machine-checked against a local file. Sources are the stockanalysis.com call transcripts for 2Q25, 3Q25, 4Q25, 1Q26 and 2Q26; the SEC-filed shareholder letters for 3Q25, 4Q25, 1Q26 and 2Q26; the FY2025 Form 10-K; the 2Q26 Form 10-Q; and the local newsroom archive for the United Kingdom, Australia, Asia Pacific and Canada posts. Call dates are taken from the main tree's guidance ledger print dates. The format follows WS31a's management-statements file at `data/processed/overnight/31a_mgmt_margin_statements.csv`, with five columns added for the basis, scope, night-weighting flag and official-versus-mirror provenance the task specifies.

**Cohort engine.** `D1_rnpl_cohort_scenarios.py` runs a monthly booking-cohort model from January 2024 to June 2027 and reports only 3Q26 and 4Q26. Two runs. Run A sets the incremental RNPL cancellation propensity to zero and solves monthly gross booked nights so that reported nights reproduce every disclosed quarter from 1Q24 to 2Q26 and the team baseline in 3Q26 and 4Q26; the solve is a forward sweep because a cohort's cancellations can land in its own month or later but never earlier. Run B holds that gross booking path fixed and turns on an RNPL share path and a cancellation propensity. The reported effect is growth under B minus growth under A, so the 2025 denominator carries its own RNPL cancellations. That is the handoff's requirement to model both years, and it is why the answers are small.

Within the engine, baseline cancellations run at the 16 percent platform average, with 25 percent recognised in the booking month (the 24-hour grace period) and the rest spread uniformly from the booking month to the stay month. Excess RNPL cancellations are recognised at the payment deadline: 85 percent in the stay month and 15 percent in the month before. The lead-time distribution is a shifted geometric in whole months with its mean varied over 1.8, 2.2 and 3.0 months and an RNPL-specific uplift of 0, 7 or 15 percent. The rebooking offset applies to excess cancellations only, in the same month.

**The lead-time mean is derived from disclosure, not assumed.** Little's Law on the unearned-fee pool: opening unearned fees divided by the quarter's revenue was 0.71 times in Q1, 0.88 in Q2, 0.70 in Q3 and 0.66 in Q4 through 2025, from Jessie's backlog table on `origin/jessie/backlog-conversion`. Revenue is recognised at check-in, so the mean residence time of a booked-but-unstayed fee is 0.66 to 0.88 quarters, that is 2.0 to 2.6 months of booking-to-check-in lead time. Only the pre-RNPL 2022 to 2025 seasonal constants are used, because from 3Q25 RNPL itself corrupts the ratio, and that corruption is exactly Jessie's finding of a 4.0-point break in both 1Q26 and 2Q26.

**Parameter labelling.** `D1_rnpl_parameters.csv` labels all 19 parameters as sourced, derived, direction-sourced with an assumed magnitude, or assumed, each with its provenance. Sourced: the disclosed nights series, the team baseline, the 1Q26 and 2Q26 GBV shares, the 16 percent base cancellation rate with its unit of account flagged as unstated, the North American nights share, and the PR #32 fitted terms. Derived: the GBV-share to nights-share identity, and the lead-time mean. Direction sourced with the magnitude assumed: the RNPL ADR ratio, the lead-time uplift, the rebooking offset, the stay-month split of excess cancellations. Assumed outright: the 2025 and 2H26 GBV share paths, the distributional shape, and the equal-thirds within-quarter booking split.

**Self-checks.** The lead-time weights sum to one and their truncated mean stays within 0.3 months of the target. The reference run reproduces every disclosed quarter within 0.2 percent. A zero-propensity scenario run is bit-identical to the reference.

## 4. What this can and cannot identify

**What it can.** It can size what an assumed RNPL cancellation propensity is worth in reported-nights growth points once the timing is handled correctly and both years are modelled. It can show how much of a quarter's excess cancellations arrive from earlier booking cohorts, which is the tail the hypothesis rests on. It can separate the product level anniversary from the cancellation drag, which the original bridge's minus 1.5 and minus 2.5 point overlays conflated. It can date the rollout and the policy changes precisely enough to say which quarter each feature laps in, and in which geography. It can check PR #32's fitted parameters against a disclosure PR #32 did not use.

**What it cannot.** It cannot measure the RNPL cancellation propensity. The propensity is a scenario input in every cell, and the management-implied value of 6.0 points rests on attributing the whole one-point rise in the platform cancellation rate to RNPL, which the 2Q26 letter's Strict-to-Firm policy migration (D048) alone makes unsafe. It cannot measure the live RNPL exposure. The FY2025 10-K confirms Airbnb measures and hedges an unbilled balance for confirmed RNPL bookings (D056), but never discloses it, so the exposure here is inferred from an assumed GBV share path and an assumed ADR ratio. It cannot separate a payment-timing shift from a cancellation in the unearned-fee line; a weak 3Q26 print there is consistent with deferral, with cancellation, or with a smaller live base. It cannot establish causality: the October 2025 cancellation redesign, the two single-fee tranches, the 2Q26 Strict-to-Firm migration, the Middle East conflict and the World Cup all overlap the rollout window, and the currency-level exclusion of Brazilian Real, Indian Rupee and Turkish Lira means country is not treatment assignment. It cannot error-bound PR #32's two product parameters, which are fitted on four WS10 North American estimates rather than disclosure.

**Evidence that weakens the hypothesis, kept on the record.** Management says realised cancellation curves have been "very close to what we saw from a tested perspective" (D020). It says the elevated cancellations are "already absorbing" into reported results (D021). It describes RNPL as driving "a meaningful lift to all booking metrics, net of cancellation" (D033). The Chief Executive says the pricing roadmap is "many multiples bigger than RNPL" (D053), which puts the product well down the list of 2027 drivers. And the arithmetic itself weakens the hypothesis: once both years are modelled, no cell in the grid reaches the original bridge's minus 1.5 to minus 2.5 point overlay at a plausible propensity with any rebooking offset at all.

**The one asymmetry that keeps the hypothesis alive.** The gross booking uplift scales with the flow of new RNPL bookings in the quarter, and that flow's year-over-year growth is flattening as the share approaches its ceiling. Excess cancellations scale with the stock of live RNPL bookings reaching their payment deadline, and that stock is still growing, because lead times lengthened and the installed base is larger. A flattening share with a still-growing stock is the configuration in which the net turns negative, and it is the configuration 2H26 is in.

## 5. Next evidence: pre-registered thresholds for 5 November

Full version with the reasoning and the identification limits in `D1_prereg_thresholds.csv`. Scored on the 3Q26 print.

| Metric | Supports the drag hypothesis | Weakens it | Inconclusive |
|---|---|---|---|
| 3Q26 nights growth, y/y | at or below 8.5% (144.9mm or less) | at or above 10.3% (147.3mm or more) | 8.6% to 10.2% |
| 3Q26 GBV growth minus nights growth | widens above 7 points with nights at or below 9% | narrows below 4.5 points with nights at or above 10% | 4.5 to 7 points |
| 3Q26 quarter-end unearned fees, y/y | at or below minus 3% (below about $1,765mm) | at or above plus 6% (about $1,930mm or more) | minus 3% to plus 6% |
| Backlog conversion, revenue over revenue plus closing unearned fees, 3Q26 | at or above 74% | 70% to 71%, back on the pre-RNPL constant | 71% to 74% |
| 4Q26 nights guide | implies 7.5% or below | implies 9.5% or above | 7.6% to 9.4% |
| An RNPL GBV share disclosed for 3Q26 | flat or down versus 2Q26 while nights decelerate | at or above 25% with nights at or above 10% | 21% to 24% |
| A quantified bundle contribution for 3Q26 | none given, or at or below 1.5 points | at or above 2.5 points | qualitative update only |

The unearned-fee threshold is the one that carries the most information per unit of ambiguity, because it scores a specific dated prediction management made itself, and because the 10-K gives the counterfactual seasonal path (D055). Note the direction carefully: management predicted unearned fees would be **higher** in Q3, so a weak print contradicts management, and a strong print is evidence the deferred fees are arriving on schedule rather than being cancelled.

### Other next evidence, in order of value per unit of effort

1. **Ask IR for the unbilled confirmed-bookings balance for RNPL.** The 10-K says Airbnb hedges it (D056), so it exists as a reported internal number. It is the live exposure the materiality arithmetic needs, and it would collapse the widest assumption in this grid.
2. **Ask for the RNPL GBV share and the RNPL nights share for the same quarter.** The ratio of the two is the ADR ratio, which is currently the second-widest assumption.
3. **Ask what the "types of bookings" expanded in July 2026 are** (D044). It is the largest unquantified offset to the 3Q26 lap and it is the only thing in the ledger that is fresh treatment inside the quarter being printed.
4. **Pin the 2Q26 Strict-to-Firm migration's scope** (D048). It is a 2026 cancellation-policy change that no team model carries, and it raises the platform refundable share independently of RNPL, which is a direct confound for the 16-to-17 remark.
5. **Relabel PR #32's "+10.2% consensus" as the team frozen card**, per the reconciliation note's action list. It is unrelated to this workstream but it is the line most likely to mislead a reader of the PR.

## 6. Files

Scripts, in this worktree:

- `analysis/src/overnight2/D0_rnpl_statement_ledger.py` builds and verbatim-verifies the ledger.
- `analysis/src/overnight2/D1_rnpl_cohort_scenarios.py` builds the cohort engine, the scenario grid, the matrices, the lap table, the cross-check, the 4Q26 gap and the thresholds.

Outputs, in `data/processed/overnight2/D/`:

- `rnpl_statement_ledger.csv`, 60 statements, 22 columns, every file-sourced quote verified verbatim.
- `D1_rnpl_cohort_scenarios.csv`, 2,025 parameter cells.
- `D1_rnpl_parameters.csv`, 19 parameters each labelled sourced, derived or assumed, with provenance.
- `D1_cohort_matrix_cancellation.csv`, booking quarter by cancellation-recognition quarter.
- `D1_cohort_matrix_stay.csv`, booking quarter by stay quarter.
- `D1_lap_anniversary.csv`, the level and anniversary schedule with ledger IDs.
- `D1_bundle_crosscheck.csv`, PR #32's parameters against the 4Q25 disclosure, out of sample.
- `D1_exna_4q26_gap.csv`, the ex-NA 4Q26 lap PR #32 omits, sized.
- `D1_prereg_thresholds.csv`, the seven 5 November scoring rules in full.

Reproduce with `py -3.13 analysis/src/overnight2/D0_rnpl_statement_ledger.py` then `py -3.13 analysis/src/overnight2/D1_rnpl_cohort_scenarios.py`. Both read the main tree read-only and need no network.
