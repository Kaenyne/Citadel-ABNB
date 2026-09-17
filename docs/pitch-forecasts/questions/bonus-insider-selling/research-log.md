# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A18 with B14 and B15). Reproduction: [datasets/pull_form4.py](datasets/pull_form4.py) (`py -3.13`, stdlib; re-pulls 563 Form 4 XMLs from EDGAR, about 4 min, or reuses `sources/form4_xml/`) then [datasets/b16_model.py](datasets/b16_model.py) (`py -3.13`, numpy/pandas, seed 20260917, 200,000 paths, under 10 s; writes `b16_summary.json`, `b16_window_history.csv`). Intermediate tables: `form4_transactions.csv`, `form4_sales_codeS.csv`, `sales_by_owner_and_plan.csv`.

## 0. Metadata
- question_name: bonus-insider-selling
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B16)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-01-31
- resolution_date: 2027-01-31
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A18

## 0b. Question (verbatim)
### Title
Between 17 Sep 2026 and 31 Jan 2027, will Airbnb insiders (Form 4 filers) sell >= $150M of stock in aggregate, or will a new 10b5-1 plan for the CEO be disclosed?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on either (SEC Form 4s; disclosure in a 10-Q/8-K). Resolution 31 Jan 2027.
### Fine Print
None beyond the resolution sentence. Conventions adopted:
1. Leg A (sales): the sum over Form 4 non-derivative transactions with transaction code S (open-market or private sale), transaction date 17 Sep 2026 to 31 Jan 2027 inclusive, of shares x reported price (weighted-average prices as reported), across all Airbnb Form 4 filers (officers, directors, 10% holders). Code F (tax withholding), G (gifts), C (Class B conversions), M/A (exercises, awards) and J are excluded. Filings made through about 4 Feb 2027 for late-January transactions count (two-business-day filing rule).
2. Leg B (new CEO plan): a Rule 10b5-1 trading arrangement for Brian Chesky adopted after his 26 Feb 2026 plan and disclosed between 17 Sep 2026 and 31 Jan 2027 in a 10-Q or 10-K Item 5/9B table, an 8-K, or a Form 4 footnote that names an adoption date after 26 Feb 2026. The 3Q26 10-Q (expected about 5-6 Nov 2026) discloses plans adopted 1 Jul-30 Sep 2026; a plan adopted in Q4 2026 would appear in the FY26 10-K (about 12 Feb 2027, outside the window) unless a Form 4 footnote reveals it first (cooling-off of at least 90 days makes that unlikely before late January). A plan adopted in Q3 2026 that was previewed in a Form 4 footnote before 17 Sep would still count when the 10-Q discloses it; no such footnote exists (claim 6).
3. Threshold: >= $150,000,000 on leg A; the window's two legs are OR.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | EDGAR pull: 563 Form 4/4A filings under CIK 1559720 since 1 Sep 2022, 1,122 code-S sales worth $4,487M: Gebbia $3,060M, Chesky $754M, Blecharczyk $465M, Balogh $106M, Mertz $30M, Jordan $24M, Stephenson $23M, Bernstein $15M, others under $4M each | `datasets/form4_sales_codeS.csv` (from `sources/form4_xml/`, https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1559720&type=4) | 2022-09 to 2026-09-16 | 2026-09-17 | yes |
| 2 | 137-day windows (17 Sep-31 Jan is 137 days), daily starts 2023-01-01 to 2026-05-03 (n 1,219): P(sales >= $150M) 0.95 all filers (median $334M); excluding Gebbia 0.40 (median $120M). The three same-calendar windows: 17 Sep 2023-31 Jan 2024 $464M (ex-Gebbia $310M: Chesky $203M under his May-2023 plan); 2024-25 $292M (ex-Gebbia $112M); 2025-26 $242M (ex-Gebbia $61M) | `datasets/b16_window_history.csv`; `b16_summary.json` history, seasonal_windows | 2026-09-17 | 2026-09-17 | yes |
| 3 | 10-Q Item 5 tables (mandatory since 2Q23): Chesky adopted plans on 31 May 2023 (2,060,000 shares, to 15 May 2024), 28 Feb 2024 (1,146,000, to 11 Nov 2024), 22 Aug 2024 (1,135,300, to 23 May 2025), 27 Feb 2025 (649,000, to 21 Nov 2025), 25 Aug 2025 (690,000, to 22 May 2026), 26 Feb 2026 (1,785,000, to 25 Nov 2026): five consecutive half-year slots (Feb/Aug) since Feb 2024, none in Aug 2023; no Q4 adoption in any year (10-K Item 9B: none in Q4 2023, 2024, 2025). Gebbia: 29 Feb 2024 (1,322,523), 20 Aug 2024 (3,086,102), 26 Feb 2025 (3,302,509), 29 Aug 2025 (1,752,860), 27 Feb 2026 (3,450,000, to 27 Nov 2026). Blecharczyk: 30 May 2023 (1,000,000), 31 May 2024 (869,042), 28 Aug 2025 (2,224,176, to 20 Nov 2026). Mertz: 31 May 2024 (146,533), 30 May 2025 (133,917, expired 5 Aug 2026). 2Q26 10-Q (6 Aug 2026): only Bernstein adopted (14,809 shares, 26 May 2026) | `sources/tenq_item5_10b51_tables.txt` (10-Qs 2Q23-2Q26, sec.gov); `data/raw/filings/abnb_10k_FY2023-2025.htm` Item 9B | 2023-08-03 to 2026-08-06 | 2026-09-17 | yes |
| 4 | Execution under current plans (Form 4 footnotes name the plan): Gebbia's 27 Feb 2026 plan sold exactly 3,450,000 shares ($511M) between 1 Jun and 28 Jul 2026 and is exhausted; Chesky's 26 Feb 2026 plan has sold 1,260,000 of 1,785,000 ($178M, 27 May-7 Aug; 525,000 remain, expiry 25 Nov); Blecharczyk's 28 Aug 2025 plan has sold 1,627,685 of 2,224,176 ($265M, 28 Nov 2025-14 Sep 2026; 596,491 remain, expiry 20 Nov), including 1,004,694 shares ($182M) in August 2026 at about $178 and 13,615 in September at $172-173 | `datasets/sales_by_owner_and_plan.csv`; `form4_sales_codeS.csv` | 2026-09-16 | 2026-09-17 | yes |
| 5 | Plans are not always executed: Chesky's Feb-2025 plan sold 24,500 of 649,000 and his Aug-2025 plan 60,000 of 690,000 (stock $115-135); his May-2023, Feb-2024 and Aug-2024 plans sold 80-93%. Gebbia's Aug-2025 plan sold 752,860 of 1,752,860. Under the August plans, December-January sales were: Gebbia $145M (Aug-2024 plan) and $38M (Aug-2025 plan); Chesky $21M and $8M. Cooling-off: first sales under the Aug-2025 plans came 28 Nov-12 Dec 2025 (about 90 days) | `datasets/sales_by_owner_and_plan.csv`; `b16_model.py` comments | 2026-09-17 | 2026-09-17 | yes |
| 6 | September 2026 Form 4s: Chesky 28 Aug gift of 76,500 shares (Form 4 on 1 Sep, 4/A on 2 Sep adding the Class B conversion); Gebbia 24 Aug conversion and gift of 960,000 shares (indirect); Bernstein 1 Sep sale 5,224 shares under his May-2026 plan; Blecharczyk sales 1 and 14 Sep under the Aug-2025 plan. No footnote names a plan adopted after 26 Feb 2026 (Chesky) or 27 Feb 2026 (Gebbia). Sales in September to date: $3.3M | `datasets/form4_transactions.csv` rows with filing_date >= 2026-08-26 | 2026-09-16 | 2026-09-17 | yes |
| 7 | Monthly code-S sales 2026: Jan $16M, Feb $15M, Mar $16M, Apr $21M, May $109M, Jun $193M, Jul $399M, Aug $223M, Sep $3M (to 16 Sep); YTD $995M; the last 137 days $926M | `datasets/form4_sales_codeS.csv` | 2026-09-16 | 2026-09-17 | yes |
| 8 | Monte Carlo (this log): remaining Blecharczyk 596,491 shares (P(fully sold by 20 Nov) 0.55, else Beta(1.5,2) fraction) and Chesky 525,000 (0.45, else Beta(1,3)) at $167.51 with a 12% price sd; a new Chesky plan adopted Jul-Sep with P 0.70 (Dec-Jan sales lognormal median $15M); a new Gebbia plan with P 0.75 (median $60M); others lognormal median $10M; a 5% tail of a non-plan block ($80M median). Results: P(leg A >= $150M) 0.78, P(leg B) 0.70, P(leg A given no new CEO plan) 0.72, P(Yes) 0.915; total-sales percentiles p5 $93M, p25 $157M, p50 $208M, p75 $267M, p95 $394M | `datasets/b16_summary.json` | 2026-09-17 | 2026-09-17 | yes |
| 9 | 16 Sep close $167.51; ABNB options 12-month distribution $126/$164/$214 (market-implied model) | `docs/pitch-forecasts/00_BRIEF.md`; `docs/reverse_dcf/SYNTHESIS.md` | 2026-09-16 | 2026-09-17 | no |
| 10 | Stock effect of insider selling: none of the 41 moves of 7%+ since listing is attributed to insider sales (causes are prints, index inclusion, macro); the 09 note's positioning work finds no insider-sale signal; the pitch catalogue lists "governance and insider selling" among live sell-side debates without a number | `data/processed/abnb_big_moves_7pct.csv`; `research/notes/2026-09-05_abnb-major-moves.md`; `research/notes/2026-09-04_abnb-pitch-catalogue.md` (line 318) | 2026-09-05 | 2026-09-17 | yes |
| 11 | Web recency (17 Sep): fool.com and SEC-indexed Form 4s for Jul-Aug 2026 (Gebbia 15-16 Jul at about $150, Blecharczyk 17 and 26 Aug at $182-191, Chesky 7 Aug); no report of a new plan or of a September sale beyond Blecharczyk's | `sources/web_search_log_2026-09-17.md` | 2026-08-26 | 2026-09-17 | no |

Newest load-bearing source: the EDGAR filing index and XMLs of 16 Sep 2026 (one day old) against a 137-day window.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill and format references; example log; R11, R13, R16, B06 logs
2. [repo] `research/notes/2026-09-04_abnb-pitch-catalogue.md` grep `insider|form 4|10b5|sold`; `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` (title refers to revenue mechanics, not insiders; no Form 4 content); `data/raw/filings/` (10-Ks only, no Form 4s); 10-K FY2023-25 grep `10b5-1`
3. [repo] `data/processed/abnb_big_moves_7pct.csv`, `research/notes/2026-09-05_abnb-major-moves.md`, `research/notes/overnight/09_stock-behaviour-and-alpha.md` grep `insider|form 4|10b5` (no hits)
4. [EDGAR] data.sec.gov submissions JSON (recent + older file); all Form 4/4A XMLs since 2022-09-01 (`datasets/pull_form4.py`, 563 filings)
5. [EDGAR] 10-Q main documents 2Q23, 3Q23, 1Q24, 2Q24, 3Q24, 1Q25, 2Q25, 2Q26 (Item 5 tables extracted; 3Q25 and 1Q26 from the session scratchpad)
6. [computed] sales by owner, month, plan; 137-day rolling windows; `datasets/b16_model.py` Monte Carlo
7. WebSearch: Airbnb insider selling Chesky Gebbia Blecharczyk Form 4 September 2026 (also the final 72-hour recency check for this question: nothing beyond the EDGAR filings already pulled)

WebSearch calls charged to B16: 1 of 5.

## 3. Leading Hypothesis Entities
Brian Chesky, Joseph Gebbia, Nathan Blecharczyk, Rule 10b5-1, Form 4, EDGAR, 3Q26 10-Q, cooling-off period

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Unconditional window base rate (0.95) | discarded as the point | 68% of all sales since 2022 are Gebbia's and his current plan is exhausted (claim 4); ex-Gebbia the window rate is 0.40 and the last two Sep-Jan windows were $112M and $61M (claim 2) |
| Ex-Gebbia history (0.40) as the point | discarded | it ignores the 1.12m shares still open under the Chesky and Blecharczyk plans (about $190M at the current price) and the founders' half-yearly plan cadence, which makes an August 2026 Gebbia or Chesky plan likely (claim 3) |
| Leg B resolves through a Form 4 footnote before the 10-Q | discarded for Q3 plans (none previewed, claim 6); kept as a small route for a Q4 plan | a Q4 adoption would sell only after a 90-day cooling-off, i.e. after the window |
| Chesky's remaining 525,000 shares are abandoned (his Feb-2025 and Aug-2025 plans sold under 10%) | kept as the 55% branch of the Chesky leg | those plans coincided with $115-135 prices; the Feb-2026 plan sold 1.26m shares at $133-178, so it is not price-gated at today's $167 |
| Blecharczyk's remaining 596,491 shares are price-gated near $175 (1.0m sold in August at about $178, only 13,615 in September at $172) | kept as the 45% branch of the Blecharczyk leg | the September sales at $172-173 show sales continue below $175; his plan also gifts |
| Gebbia's 24 Aug gift of 960,000 shares is a disguised sale | discarded | code G, indirect holding; gifts to a trust or DAF are not Form 4 sales by an insider (the recipient is not a filer) |
| A 10% holder or a new director sells a block | tail (5%) | none has since 2022; Sequoia and Founders Fund exited long ago |

## 5. Independent Estimates
- base_rate_estimate: 0.70 - the all-filer window rate 0.95 and the ex-Gebbia rate 0.40 (claim 2), weighted toward the lower figure because the dominant seller's plan is exhausted and no successor plan is disclosed, then lifted for leg B (a CEO plan in 5 of the last 6 half-year slots, Laplace 0.75)
- decomposition_estimate: 0.915 - the Monte Carlo of claim 8: remaining capacity under the two open plans (1.12m shares, about $190M) executed at historical rates, plus new August plans at the founders' cadence selling after cooling-off in December-January, OR a new CEO plan in the 3Q26 10-Q (0.70)
- anchor_estimate: 0.95 - the unconditional 137-day window rate (claim 2), the "Airbnb insiders always sell" crowd view; no tradable market
- anchor_value: 0.95 (historical window rate, computed 2026-09-17; no market)
- final_estimate: 0.87 (credible interval 0.75-0.95)
- final_minus_anchor: -8 points. NOT_INDEPENDENTLY_DERIVED flag noted for the magnitude of the gap; the divergence has a nameable cause: the seller who produced 68% of the record has no open plan, so the window depends on two partially executed plans and on plans not yet disclosed. The final sits below the Monte Carlo (0.915) because the model's execution fractions and the 0.70/0.75 new-plan probabilities are judgement and the pre-mortem's routes to No (both founders paused at $167 after selling at $178, no August plans) are correlated through one variable, the price

## 6. Final Numbers
**Binary.** P(Yes) = **0.87**, credible interval **0.75-0.95**.
Legs: P(sales >= $150M) about 0.75; P(new CEO plan disclosed in the window) about 0.70; P(Yes) = P(B) + P(not B) x P(A given not B) = 0.70 + 0.30 x 0.6 = 0.88, rounded to 0.87 with the model's 0.915 as the upper reference.
Extreme-probability gate: not triggered (0.87 < 0.95). Audit of the edge cases anyway: (1) a Form 4 price reported as a weighted average is used as reported; (2) a CEO plan "modification" of the Feb-2026 plan (not a new plan) would be argued as No; (3) Class B conversions and gifts are excluded by convention 1.

## 7. Sensitivity
Rows from `datasets/b16_summary.json` sensitivity (P(Yes); leg A in brackets).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| P(new Chesky plan in Q3 2026) 0.70 | 0.50: 0.86 [0.76]; 0.85: 0.96 [0.79] |
| P(new Gebbia plan in Q3 2026) 0.75 | 0.50: 0.89 [0.70]; 0.90: 0.93 [0.83] |
| Blecharczyk execution (55% full) | sells nothing more: 0.79 [0.40]; sells all 596k: 0.96 [0.90] |
| Chesky remaining 525k (45% full) | sells nothing more: 0.83 [0.52]; sells all: 0.97 [0.93] |
| New Gebbia plan Dec-Jan sales median $60M | $30M: 0.89 [0.70]; $120M: 0.94 [0.84] |
| Both founders paused (no Q3 plans, no further sales) | about 0.35 (Blecharczyk alone cannot reach $150M) |
| Stock at $130 through the window | leg A capacity falls to about $145M at full execution: about 0.78 |

Pre-mortem ("it is 31 Jan 2027 and this resolved No"): (1) neither founder adopted an August 2026 plan (the 3Q26 10-Q table shows only officers), Chesky's remaining 525k lapsed on 25 Nov as his 2025 plans did, and Blecharczyk's remaining shares were price-gated above the post-print price; total sales $90-130M; (2) the stock fell 15% on 5 Nov and every plan's limit price bit; (3) a new CEO plan was adopted in December (after the print) and surfaced only in the 10-K on 12 Feb. ("Resolved Yes"): the modal outcome; the 3Q26 10-Q on about 5 Nov is the likely resolver. Asymmetry: the item has no operating content; a No costs only a line in the memo.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| twice weekly | EDGAR Form 4 feed for CIK 1559720 | running total of code-S sales from 17 Sep; each $25M: +0.01; a Chesky or Gebbia footnote naming a plan adopted after Feb 2026: resolve Yes |
| 2026-10-02 | Prelim memo freeze | quote 0.87 (0.75-0.95); immaterial for the stock |
| 2026-11-05 / 06 | 5 Nov print; 3Q26 10-Q Item 5 table | a Chesky adoption dated Jul-Sep 2026: resolve Yes; none: leg B dead, move to leg A only (about 0.6 if sales to date are under $75M, about 0.9 if over $120M) |
| 2026-11-20 / 25 | Blecharczyk and Chesky plan expiries | unsold remainder lapses; recompute leg A from the running total and any new plans |
| 2026-11-25 to 2026-12-15 | Cooling-off ends for late-August plans | first sales under new founder plans appear here in 2024 and 2025 |
| 2027-01-31 | Window end (filings through about 4 Feb count) | resolve on the EDGAR sum |
| 2027-02-12 (approx.) | FY26 10-K Item 9B | outside the window; record any Q4 adoption for the next question |

## 9. Impact
If Yes (modal Yes = $150-300M of programmatic 10b5-1 sales plus a routine CEO plan disclosure in the 3Q26 10-Q):

| Item | Delta if B16 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | insider sales do not touch bookings |
| 4Q26 nights (pts) | 0 | as above |
| ADR (pts) | 0 | as above |
| 4Q26 revenue ($M) | 0 | as above |
| FY27 revenue ($M) | 0 | as above |
| FY26 adj. EBITDA margin (pp) | 0 | as above |
| FY27 adj. EBITDA margin (pp) | 0 | as above |
| FY27 EPS ($) | 0.00 (sales are of existing shares; no dilution; buybacks absorb about 6m shares a quarter against about 1.5m of insider sales) | claim 1; `data/processed/abnb_capital_return_quarterly.csv` |
| Stock ($/share) | **-0.5** (a headline "$500M founder plan" or "CEO sells $80M" is worth at most a day of press; $4.5bn of insider sales since 2022 produced no attributable move in the big-moves file; the residual is the governance talking point the sell-side already carries) | claim 10 |
| **EV = P x impact** | **0.87 x -$0.5 = -$0.4/share** | |
| Materiality | **Immaterial** for the price target (EV under $1/share). Useful only as one sentence of colour: the founders have sold $4.3bn since Sep 2022 and run overlapping half-yearly 10b5-1 plans, so a new Chesky plan in the November 10-Q is the base case, not a signal. What would be a signal, and is not forecast here, is a founder plan being adopted with a price floor or an unusual size after the 5 Nov print | claims 3-5 |

RESUME: the next agent (audit response) should attack (1) the execution-fraction assumptions in `b16_model.py` (0.55 Blecharczyk, 0.45 Chesky) against the per-plan record in `sales_by_owner_and_plan.csv`; (2) the 0.70 / 0.75 new-plan probabilities (the cadence table in claim 3 is the evidence; the 2Q26 10-Q showing no founder adoption in Q2 is consistent with the Feb/Aug rhythm); (3) convention 2's treatment of a Form 4 footnote as a disclosure. Re-run after the 3Q26 10-Q (about 5-6 Nov) and every two weeks on the EDGAR running total; re-pull with `pull_form4.py`.
