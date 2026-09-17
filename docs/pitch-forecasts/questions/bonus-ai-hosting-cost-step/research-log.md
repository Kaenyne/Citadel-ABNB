# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A16). Companion questions in the batch: B09 `bonus-sbc-step-up`, B10 `bonus-interest-income-falls`, B17 `bonus-take-rate-guided-down`. Finished logs reused as inputs (read-only): R05 (cost stack), F03 (FY27 margin guide and February-letter record), C04/C09 (margin sentences). Reproduction: `datasets/b08_model.py` (numpy/pandas, seed 20260917, n 400,000, seconds) → `b08_results.csv`, `b08_history.csv`.

## 0. Metadata
- question_name: bonus-ai-hosting-cost-step
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B08)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
By the Feb print, will management quantify incremental AI/hosting/infrastructure spend for FY27 of ≥$50M, or will 4Q26 cost of revenue grow ≥ +18% y/y?
### Resolution Criteria
Yes on either (4Q25 cost of revenue $487M; threshold $575M). Resolution ~11 Feb 2027.
### Fine Print
(none beyond the registry header conventions: "Feb print" = the 4Q26 release and call, ~11 Feb 2027; letter governs where letter and call differ.)

Conventions adopted (stated, not changing the question): (1) leg 2 resolves on the income-statement line "Cost of revenue" in the 4Q26 press release / FY26 10-K, computed as FY26 less nine months where the release gives only the FY column, against the 4Q25 line of $487M (FY25 $2,086M less 9M25 $1,599M); a restated 4Q25 does not move the $575M threshold; (2) leg 1 requires a management statement — letter, prepared remarks, Q&A, or 10-K MD&A — that puts a dollar figure (or a percentage convertible to dollars on a stated base) of ≥ $50M on *incremental* FY27 (or "next year", "2027") spend on AI, hosting, cloud, infrastructure, compute or server costs; a statement given at the 5 Nov print counts ("by the Feb print" includes it); the 10-K commitments table (purchase obligations by year) is not a management quantification of incremental spend and does not count on its own; a figure for total FY27 AI spend counts only if the incremental over FY26 is stated or arithmetically implied ≥ $50M; a figure given as a range counts on its midpoint; (3) a quantified *saving* from AI (support cost per booking) does not count; (4) if either print date moves, the same event on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Reported cost of revenue by quarter ($M): 1Q25 506, 2Q25 544, 3Q25 549, 4Q25 487, 1Q26 581, 2Q26 633; y/y: 1Q25 +5.4, 2Q25 +7.5, 3Q25 +18.1, 4Q25 +14.1, 1Q26 +14.8, 2Q26 +16.4; FY25 $2,086M. GBV y/y over the same quarters: 7.0, 10.8, 13.9, 15.9, 19.2, 15.7. Cost of revenue / GBV (%): 3Q24 2.313, 4Q24 2.426, 1Q25 2.065, 2Q25 2.315, 3Q25 2.397, 4Q25 2.387, 1Q26 1.990, 2Q26 2.327; y/y change in the ratio over the last 10 quarters mean −1.0%, sd 3.7% (max +5.5% in 2Q24, +3.6% in 3Q25) | `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (cor_cash, cor_cash_pct_gbv); `data/processed/abnb_quarterly_costlines.csv`; `datasets/b08_history.csv` | 2026-08-06 (last print) | 2026-09-17 | yes |
| 2 | Threshold arithmetic: $575M = +18.1% on $487M; at the team's 4Q26 GBV +12.7% the cost-of-revenue/GBV ratio must rise +4.7% y/y (2.387% → 2.50%); at GBV +15.5% (Street high) +2.2%; the ratio has risen ≥ +4.7% y/y in 1 of the last 10 quarters (2Q24, +5.5%, the cross-currency fee and chargeback step) | computed from claim 1; `datasets/b08_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 3 | Line build (15 Sep) cost-of-revenue formula: merchant fees 1.70% of GBV annual-equivalent × quarterly factors (0.90/1.045/1.035/1.033; 4Q factor gives 1.756–1.759%) + chargebacks $0.72 per booking + hosting ($224M/yr FY25 base = $56M/q, +$30M per half step in 2H26, plus the "AI reconciliation step") + other $0.36 per night; FY25 backcast error −1.0%, 1H26 +0.8%. 4Q26 base path (reconciled): fees $404M, chargebacks $26M, hosting $100M (56 + 15 + 29), other $47M = **$578M, +18.7% y/y**; evidence-only path (no reconciliation step): hosting $71M, **$549M, +12.7%**; cost-bear $582M (+19.5%), cost-bull $575M (+18.1%), revenue-bear $572M (+17.4%), revenue-bull $587M (+20.5%). FY27 hosting $330M (bear $400M, bull $290M) vs FY25 $224M; sensitivity: FY27 hosting +$50M = −0.32pp of FY27 margin, −$0.07 EPS | `docs/margin-build/notes/40_line_build.md`; `data/processed/margin_build/40_line_build/40_params.csv`, `40_lines_quarterly.csv` (rows 1, 7, 13, 19, 25, 31), `40_sensitivities.csv` | 2026-09-15 | 2026-09-17 | yes |
| 4 | The reconciliation step is an inference, not evidence: "the evidence-only build … contradicts management's 'margin down slightly' sentence"; landing the sentence needs ~$97M more 3Q26 cost, "70% to 3Q26 marketing as a timing step, 30% to hosting as a run-rate step"; "the hosting run-rate step ($116M a year into FY27) is the least-sourced number in the build"; R05 (this run) prices a 25% chance the flagged Q3 step slips out of the quarter | `docs/margin-build/notes/40_line_build.md` §"The reconciliation" and Caveats; `../risk-q3-margin-sandbagged/research-log.md` claim 12 | 2026-09-15 / 2026-09-17 | 2026-09-17 | yes |
| 5 | 2Q26 10-Q MD&A, verbatim: Q2 "Cost of revenue increased $89 million, or 16%, primarily due to a $68 million increase in merchant fees, a $13 million increase in chargebacks, and a $12 million increase in server costs … The increase in server costs was primarily driven by higher amortization related to reserved instance purchases and increased infrastructure spend. These increases were partially offset by a decrease in amortization expenses related to capitalized internal-use software projects"; six months: +$164M (+16%): fees +$131M, chargebacks +$25M, server +$15M. Commitments note: "no material changes outside the ordinary course of business to the Company's commitments, as disclosed in its 2025 Annual Report" | `data/raw/regulatory/quantification/abnb_2026q2_10q.html` | 2026-08-06 | 2026-09-17 | yes |
| 6 | Hosting commitments: FY23 10-K "at least $842 million for vendor services through 2027" (K004); FY24 10-K "at least $672 million … through 2027" (K005; ~$224M/yr); FY25 10-K "at least $1.7 billion … through 2031" (K006), purchase obligations table $1,749M: less than 1 year $219M, 1–3 years $930M (~$465M/yr in 2027–28), 3–5 years $600M. The contracted step is in 2027, not 2026: the committed run-rate roughly doubles from $219M (2026) to ~$465M (2027) | `data/raw/filings/abnb_10k_FY2025.htm` Note 13; `abnb_10k_FY2024.htm`; `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` K004–K007 | 2026-02-12 | 2026-09-17 | yes |
| 7 | Management on AI spend, verbatim: Chesky 4Q25 call (12 Feb 2026, S140): "we're not building models. We do not have a huge CapEx cost base. So our investment in AI will not affect the P&L. I don't think you'll see it in the P&L"; (S181) "we're not building data centers". Mertz 1Q26 call (7 May 2026, S155): AI "is an expense that will ramp over the course of the year … we've the ability to absorb that in the strong margin". Mertz 2Q26 call (6 Aug 2026, S162): "the updated guidance … obviously does assume a material increase in terms of the AI spend over the course of the year … we are expanding margins while absorbing that increased cost." WS05: "AI spend size (never given)"; 2Q26 letter: support cost per booking −16% y/y "driven in part by improvements to our AI assistant" | `05_statements.csv` S140, S155, S162, S181; `docs/margin-build/notes/05_mgmt_statements_v2.md` (lines to listen for); `data/raw/letters/2Q26_d70413dex991.htm` | 2026-02-12 to 2026-08-06 | 2026-09-17 | yes |
| 8 | February-letter record of quantified cost items (4Q21–4Q25 letters, 5 prints): Feb 2022 S&M % of revenue "relatively flat" (qualitative); Feb 2023 Q1 S&M "approximately 150 basis points higher" and FY "flat" (quantified, bp); Feb 2024 SBC "similar year-over-year growth rate" (~20%, quantified %); Feb 2025 "$200 million to $250 million towards launching and scaling new businesses" (quantified $); Feb 2026 SBC/headcount growth "lower than 2025" (qualitative) plus the tax rate each year. A dollar or percentage on a named cost item in 3 of 5 February letters; on AI/hosting specifically 0 of 5; the 4Q24 call also quantified the FX fee (+20bp of take rate). The FY25 investment figure was later cut to "approximately $200 million" (2Q25, 3Q25) and Mertz declined to size 2026 ("I'm not going to give a particular figure for next year", 2Q25 call) | `data/processed/overnight/02_guidance_ledger.csv` (metrics sm_pct_rev_yoy_bps, sbc_yoy_pct, new_business_investment_usd_m, tax_rate_pct); `data/raw/transcripts/web/2Q25.html`; `../fy27-margin-guide/research-log.md` claim 1 | 2022-02-15 to 2026-02-12 | 2026-09-17 | yes |
| 9 | F03 (this run): FY27 margin guide vector (a) 0.08 / (b) 0.17 / (c) 0.27 / (d) 0.38 / (e) 0.10; within (d) an explicit investment-year framing ≈ 0.10; WS05 H12: "A step-change in AI opex is the one stated risk"; H02/H03: the 2H26 AI/hosting ramp means FY27 carries a full year of it; Feb 2025 precedent named the investment with a dollar figure when it cut the floor | `../fy27-margin-guide/research-log.md` §6, claims 3, 8, 9; `05_fy27_hints.csv` | 2026-09-17 / 2026-09-14 | 2026-09-17 | yes |
| 10 | 4Q26 GBV: team (bridge v3 / line build) $22,987M (+12.7%); Bloomberg MODL mean $23,003M (+12.8%), low $22,177M, high $23,565M (n 28, 12 Sep); LSEG 4Q26 revenue $3,162M; team 4Q26 nights 132.7m, nights per booking 3.65. Merchant-fee rate: FY24 1.69%, FY25 1.76%, 1H26 1.68% annual-equivalent "after higher payment processor rebates and incentives" (1Q26 10-Q) | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `40_params.csv` (merchant_fee_pct_gbv) | 2026-09-12 / 2026-09-15 | 2026-09-17 | yes |
| 11 | Monte Carlo (this log, `datasets/b08_model.py`): leg 2 = fees (GBV N(22,990, 650) × rate N(1.756, 0.04)) + chargebacks N(26, 4) + hosting (56 + step, step a 0.45/0.35/0.20 mixture of N(15, 5) / N(30, 8) / N(45, 10)) + other N(47.8, 3) + N(0, 12): median $559M, p10–p90 $530–591M, **P(≥ $575M) 0.26**. Sensitivities: hosting evidence-only 0.10, line-build reconciliation mix 0.57, 40/40/20 0.27; GBV at the Street high 0.41, at $22.4bn 0.15; fee rate 1.735 (rebates persist) 0.20, 1.818 (FY25 rate) 0.48; residual sd 20 → 0.30, 6 → 0.24. Ratio base rate: N(−1.0, 3.7) vs the needed +4.7% → 0.06 unshifted, 0.20 with a +2.5pt hosting shift, 0.17 at GBV +15%. Leg 1: P(quantify | leg 2 Yes) 0.40, P(quantify | leg 2 No) 0.18 → unconditional leg 1 0.24; **P(Yes) 0.39**; P(leg 1 | No) 0.10 / 0.12 / 0.25 / 0.30 → 0.33 / 0.35 / 0.44 / 0.48 | computed; `datasets/b08_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 12 | No Kalshi or Polymarket market on Airbnb costs, AI spend or guidance (Kalshi KXABNB is a Q3 nights ladder; Polymarket has price ladders and a closed Q2 GBV ladder), fetched 2026-09-17T08:21:21Z | `sources/kalshi_markets_KXABNB_open_20260917T082121Z.json`; `sources/polymarket_search_airbnb_20260917T082121Z.json` | 2026-09-17 | 2026-09-17 | no |
| 13 | Web pass (2 WebSearch calls attributable, one shared): no company or sell-side sizing of Airbnb's AI/hosting spend; only the 6 Aug call language repeated by trade press; nothing in the last 72 hours | `sources/web_queries_2026-09-17.md` queries 1–2 | 2026-09-17 | 2026-09-17 | no |
| 14 | Impact sensitivities: FY27 hosting +$50M = −0.32pp FY27 margin / −$0.07 EPS (claim 3); FY27 EPS ≈ $0.0014 per $M of EBITDA; one EV/EBITDA turn ≈ $9–10/share; Street FY27 adj. EBITDA $5,766M / 36.45% (n 44) carries no hosting step (Street incremental margin 43.7%); 16 Sep close $167.51; ~620m diluted shares (M7 FY27 573m weighted) | `docs/pitch-forecasts/00_BRIEF.md`; `40_sensitivities.csv`; `data/processed/margin_build/23_final_model/23_vs_consensus.csv` | 2026-09-16 / 2026-09-15 | 2026-09-17 | yes (impact only) |

Newest load-bearing source: the 2Q26 10-Q and call (6 Aug 2026, 42 days old against a 147-day window) for the mechanism; the line build (15 Sep) and the 17 Sep market/FRED pulls for the path. Nothing newer exists on the object; the next information is the 3Q26 cost-of-revenue line on 5 Nov.

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md` (conventions, Bonus preamble, B08–B10, B17), skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`; finished logs R05, C11, R04, C12, R01, F03, F04 (read-only)
2. [repo] `docs/margin-build/notes/40_line_build.md` (all); `data/processed/margin_build/40_line_build/40_params.csv`, `40_lines_quarterly.csv` (all 48 scenario rows), `40_sensitivities.csv`
3. [repo, pandas] `data/processed/abnb_driver_history_quarterly.csv`, `abnb_quarterly_costlines.csv`, `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (cost of revenue, GBV, ratio by quarter)
4. [repo, python] 2Q26 10-Q text: "server", "infrastructure", "hosting", "artificial intelligence", "headcount" passages; FY2025 and FY2024 10-K: "web-hosting", "Purchase commitments include", "artificial intelligence"
5. [repo, python] every letter 4Q20–2Q26 for "hosting", "infrastructure", " AI ", "cloud", "compute", "headcount"; call mirrors 2Q25–2Q26 for "AI spend", "infrastructure", "compute", "investment in AI"
6. [repo, pandas] `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` (S140, S155, S162, S181, K004–K007), `05_fy27_hints.csv`; `docs/margin-build/notes/05_mgmt_statements_v2.md` grep "hosting|AI|infrastructure"
7. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` (February-print metrics; quantified cost items)
8. [Kalshi API] series KXABNB open markets; [Polymarket public-search] airbnb (2026-09-17T08:21:21Z)
9. [WebSearch] Airbnb news (neutral recency pass, shared by the batch)
10. [WebSearch] Airbnb AI infrastructure spending 2027 Mertz "material increase" hosting costs
11. [python] `datasets/b08_model.py` → `b08_results.csv`, `b08_history.csv`
12. [WebSearch, final 72-hour neutral recency check = query 9, 2026-09-17: nothing new on hosting, AI spend or cost of revenue] — no change

WebSearch calls used by this question: 2 of 5 (one shared).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, cost of revenue, merchant fees, hosting, reserved instances, AI spend, data hosting services provider ($1.7 billion through 2031), 4Q26 shareholder letter, FY2026 10-K

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Leg 2 via the line build's reconciled path ($578M, +18.7%): the "down slightly" sentence implies a hosting run-rate step of ~$29M/q that persists into Q4 | kept at 0.20 weight in the hosting mixture (P(leg 2) 0.57 if it were the whole story) | claim 4: the 30% hosting share of the reconciliation gap is a judgement and "the least-sourced number in the build"; the 10-K commitments (claim 6) put the contracted step in 2027, not 2026 |
| Leg 2 via the evidence-only path ($549M, +12.7%): fees track GBV +12.7%, server costs +$7–8M/q as in 1H26 | kept at 0.45 weight (P(leg 2) 0.10 on its own) | claim 5: 1H26 server costs +$15M on the half; 1H26 cost of revenue grew slower than GBV (rebates); the ratio has risen ≥ 4.7% y/y in 1 of 10 quarters (claim 2) |
| GBV prints at the Street high (+15.5%) and carries fees over the line | inside the GBV N(22,990, 650) (sensitivity 0.41 at the high) | the team's 4Q26 nights +8.9% and ADR +3.9% sit inside the MODL range; the bundle lap argues for the low half |
| Merchant-fee rate reverts to the FY25 1.76% annual-equivalent (rebates fade) | inside rate N(1.756, 0.04); sensitivity 0.48 at 1.818 | the 1Q26 10-Q attributed the lower 1H26 rate to "higher payment processor rebates and incentives"; no sign of reversal in 2Q26 (+$68M fees on +15.7% GBV) |
| Leg 1: management sizes the FY27 AI/hosting step in the February letter, in the Feb 2025 form ("$200–250M towards new businesses") | leading component of leg 1 (~0.15 of total) | claim 8: a named dollar figure on a cost item in 3 of 5 February letters, but never on AI/hosting, and the CEO's framing is that AI "will not affect the P&L" (claim 7) |
| Leg 1: Q&A on 5 Nov or in February elicits a figure ("how much is the AI spend?") | kept (~0.10 of total) | Mertz has twice described the ramp without a number (S155, S162) and declined to size new-business spend for 2026 (claim 8) |
| Leg 1 via the 10-K purchase-obligations table alone | discarded by convention (2) | the table is a contractual schedule, not a statement of incremental spend; it already implies ~+$246M for 2027 and would resolve the question trivially if it counted — the strict reading is adopted and its alternative reported in §7 |
| A capitalised-software or D&A reclassification lifts the reported line | inside the residual N(0, 12) | 2Q26 notes an *offset* from fully amortised internal-use software (claim 5) |
| Print date moves / restatement | no effect | conventions (1), (4) |

## 5. Independent Estimates
- base_rate_estimate: 0.31 — leg 2: the cost-of-revenue/GBV ratio has risen ≥ +4.7% y/y in 1 of 10 quarters; N(−1.0, 3.7) with a +2.5pt shift for the disclosed hosting ramp gives 0.20 (0.06 unshifted, 0.17 at GBV +15%); leg 1: a dollar or percentage on a named cost item in 3 of 5 February letters, on AI/hosting in 0 of 5 and 0 of the 6 prints since the AI theme began (Laplace 1/8 ≈ 0.13); union 1 − 0.80 × 0.87 = 0.31
- decomposition_estimate: 0.39 — `datasets/b08_model.py`: leg 2 from the line-build formula with a hosting-step mixture (0.26), leg 1 conditional on leg 2 (0.40 / 0.18) → 0.39 (claim 11)
- anchor_estimate: 0.63 — no market prices the object (claim 12); the designated anchor is the repo's own adopted path: the line build's reconciled 4Q26 cost of revenue of $578M (+18.7%) sits above the threshold, i.e. P(leg 2) ≈ 0.57 under its reconciliation mix, plus leg 1 at 0.18 given leg 2 No → 0.63
- anchor_value: 0.63 (line build 15 Sep 2026, reconciled base path; a repo prior, not a market)
- final_estimate: 0.38 (credible interval 0.25–0.52)
- final_minus_anchor: −25 points. Independence: the anchor takes the reconciliation step as fact; this log weights it at 0.20 because the step is an inference from the Q3 sentence with a judgement split (claim 4) and the contracted hosting step is a 2027 event (claim 6). The base rate (0.31) and the decomposition (0.39) agree within 8 points; the final sits between them, nearer the decomposition because the disclosed server-cost trend and the AI ramp are real and the ratio base rate does not carry them.

## 6. Final Numbers
**Binary.** P(Yes) = **0.38**, credible interval **0.25–0.52**.
Split: P(leg 2, 4Q26 cost of revenue ≥ $575M) ≈ 0.26; P(leg 1, a quantified ≥ $50M FY27 AI/hosting step, unconditional) ≈ 0.24; P(both) ≈ 0.10; P(leg 1 only) ≈ 0.13. Leg-2 distribution: median $559M (+14.8% y/y), p10–p90 $530–591M.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Hosting-step mixture 0.45 / 0.35 / 0.20 (evidence-only / partial AI / full reconciliation) | evidence-only: 0.26; full reconciliation: 0.65; 40/40/20: 0.39 |
| 4Q26 GBV centre $22,990M (team = Street mean) | Street high $23,565M: 0.52; $22,400M: 0.30 |
| Merchant-fee rate 1.756% (4Q factor on 1.70) | 1.735 (rebates persist): 0.34; 1.818 (FY25 rate): 0.57 |
| P(quantify \| leg 2 No) 0.18 | 0.10: 0.33; 0.12: 0.35; 0.25: 0.44; 0.30: 0.48 |
| Convention (2): the 10-K commitments table does not count | if it counts as a quantification: ~0.85 (the FY25 10-K already implies ~+$246M for 2027 and the FY26 10-K will restate the schedule) |
| Residual cost noise sd $12M | $6M: 0.37; $20M: 0.42 |

Pre-mortem ("it is 11 Feb 2027 and this resolved Yes"): (1) 4Q26 cost of revenue printed ~$580M because the reserved-instance amortisation and inference spend Mertz called "material" landed as a ~$25–30M/quarter run-rate step in 2H26 — the line build's reconciliation read, priced at 0.20 plus the partial branch; (2) management pre-announced the 2027 cost step in February with a number ("approximately $150 million of incremental infrastructure and AI investment") alongside a haircut FY27 margin floor, the Feb 2025 form (F03 (d) 0.38), priced at ~0.15; (3) GBV printed +15% on a stronger Q4 and fees alone carried the line (0.41 route); (4) a resolver counts the 10-K commitments schedule (convention (2), the largest single risk to the number). "It resolved No": the modal outcome — fees tracked GBV, server costs grew +$8M/q, the letter described AI as "efficient" and never sized it. Asymmetry: this item is a bonus for the short; over-stating it would put a coin-flip cost item next to the memo's demand thesis, so the log keeps the number below 0.40 and the interval wide.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo due | Quote 0.38 (0.25–0.52); state that leg 2 is a $559M-median line against a $575M threshold and that the team's own reconciled path sits above it |
| 2026-11-05 (after close) | 3Q26 release: cost of revenue line (vs the line build's $641M reconciled / $612M evidence-only); call Q&A on AI spend | 3Q26 ≥ $635M (hosting step visible) → 0.55; ≤ $615M → 0.25; any dollar figure on 2027 AI/hosting ≥ $50M → resolve Yes |
| 2026-11-06 | 3Q26 10-Q MD&A: server-cost increase (the 2Q26 form "+$12M") | server costs +$20M or more y/y in Q3 → +0.08; +$10M or less → −0.05 |
| 2026-11-06 to 2027-02-10 | Sell-side FY27 model notes on cost of revenue / hosting; any management conference remark sizing AI spend | a sized remark ≥ $50M → resolve Yes; a repeated "efficient, not in the P&L" framing → −0.03 |
| ~2027-02-11 | 4Q26 release and call; FY26 10-K commitments schedule and MD&A | resolve: 4Q26 cost of revenue ≥ $575M or a quantified FY27 step; audit read: a 3Q26 line ≥ $635M should have put the pre-print P near 0.6 |

## 9. Impact
If the event happens (taken at its conditional mean: 4Q26 cost of revenue ≈ $590M, +$12M above the line build's $578M; FY27 hosting/AI ≈ +$100M above the line build's $330M, i.e. roughly the contracted 2027 step net of what the build already carries):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a cost item |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 | — |
| FY27 revenue ($M) | 0 | — |
| FY26 adj. EBITDA margin (pp) | −0.1 | +$12M of 4Q26 cost on $14,268M (−0.4pp of the 4Q26 margin) |
| FY27 adj. EBITDA margin (pp) | −0.6 | +$100M of FY27 hosting/AI × (−0.32pp per $50M, claim 3); against the Street, which carries no step, the gap is larger (~−0.9pp on the Street's $15.8bn) |
| FY27 EPS ($) | −0.14 | $0.0014 per $M × $100M |
| Stock ($/share) | −4 | level effect −$100M × ~16x / 620m ≈ −$2.6, plus the read that FY27 is an investment year (F03 (d) rises), ≈ −$1.5; no revenue-growth channel |
| **EV = P × stock** | **0.38 × −$4 ≈ −$1.5/share** | **Material at the margin** (≥ $1/share): carry as a bonus line with the 5 Nov cost-of-revenue read as the trigger; drop if 3Q26 cost of revenue prints ≤ $615M |

RESUME: the next agent (audit response) should re-run `datasets/b08_model.py` (seconds), check claim 1's cost-of-revenue and GBV series against the panel and the 4Q25 line ($487M = FY25 $2,086M − 9M $1,599M), and challenge two inputs: the hosting-step mixture weights (0.45/0.35/0.20 — the single largest lever, 0.26 → 0.65 across its range) and the leg-1 conditionals (0.40 / 0.18). Convention (2) on the 10-K commitments table should be confirmed with Krish before 2 Oct because it flips the number.
