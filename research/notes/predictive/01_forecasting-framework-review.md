# Forecasting frameworks, Airbnb print base rates, and the protocol for calling anything "predictive"

- **Sources:** `docs/forecast-skill/SKILL.md` and its `references/` (Metaculus-style forecasting skill); Theo's forecasting stream under `theos-past-research/` (`.codex/skills/abnb-forecasting/SKILL.md`, `docs/forecasting/agent-contract.md`, `docs/forecasting/prompting-and-running.md`, `docs/superpowers/specs/2026-09-03-abnb-forecasting-agent-design.md`, `docs/forecasting/abnb_ic_brief/brief.tex` and `generated/metrics.json`, `src/abnb_forecasting/{baselines,eligibility,packet}.py`, `research/forecasting/target_registry.csv`, the five run folders under `research/edge-discovery/`, the readiness run under `research/readiness/`, and `research/guidance/data/normalized/*.csv` with `AGENT_PLAYBOOK.md`); our own `data/processed/abnb_revenue_guidance_vs_actual.csv`, `data/external/abnb_earnings_reactions.csv`, `data/external/abnb_major_moves_events.csv`, `data/processed/abnb_quarterly_kpis_from_study.csv`, `data/processed/abnb_quarterly_cost_stack_exsbc.csv`, and `research/notes/2026-09-05_margin-drivers.md` sections 5, 5.1, 7 and 11.
- **Date:** 2026-09-05
- **Author:** Krishang Surapaneni (compiled with Claude Code, predictive-study agent 01 of 05).
- **Companion outputs:** `analysis/src/predictive/01_print_base_rates.py` writes `data/processed/predictive/01_print_base_rates.csv` (one row per print, 23 rows) and `data/processed/predictive/01_print_base_rates_summary.csv` (about 310 base-rate, bucket, baseline and diagnostic cells, each with its n).

---

## 0. Bottom line

1. **The Metaculus skill transfers almost whole.** Base rate first, decompose the question, price the boring gates before the story, write the pre-mortem, and update only when a named assumption moves. The parts that do not transfer are the crowd-relative scoring and the prediction-market anchor; for an earnings print the "crowd" is sell-side consensus and the options-implied move, and we do not yet have either as a point-in-time series.
2. **Theo built the plumbing and found no signal.** His own IC brief says it: "Process edge WORKS. Forecast edge UNPROVEN. Trading edge UNTESTED." The one strong number (activity composite vs guidance growth, Pearson 0.78, n=16) has zero strictly point-in-time rows and turns into r = -0.63 when you ask it about acceleration instead of level. Every alt-data hypothesis H-001 to H-012 ended INCONCLUSIVE, WATCH_PROSPECTIVELY, CONTROL_ONLY, INELIGIBLE or REJECT. Guidance direction to next-day excess return is r = 0.03 to 0.08.
3. **Our base rates are strong on management behaviour and weak on the stock.** Revenue beat the guide midpoint 19 of 19 times (mean +2.5%) and the top of the range 15 of 19. Quarterly margin has never come in worse than the direction guided (22 of 22). But the 1-day excess return versus QQQ is positive only 11 of 23 times (mean +0.5%, median 0.0%, standard deviation 8.7%), and the 20-day excess is negative in 16 of 22 prints. Beating the guide is the base case and is priced.
4. **The one print variable the stock reliably reacts to is nights acceleration.** When nights growth accelerated versus the prior quarter, the 1-day excess return was positive 7 of 8 times (Fisher p = 0.009); when it did not, 4 of 15. This is a reaction-function fact, not a forecast: nights are disclosed in the print. It becomes predictive only if one of agents 02 to 05 can forecast nights acceleration before 5 November with the protocol in section 4.
5. **Protocol in one line:** report n, Pearson and Spearman with p-values, a permutation p-value, leave-one-out or walk-forward error against both a seasonal-naive baseline and the management guide midpoint, a point-in-time check on every input, and a multiple-comparisons haircut. Nothing is called predictive until it passes all six.

---

## 1. What the Metaculus skill prescribes, and what transfers to an earnings print

`docs/forecast-skill/SKILL.md` is a superforecasting procedure written for Metaculus tournaments. The steps, in its order:

| Step | What the skill says | Transfers to a print forecast? |
|---|---|---|
| Triage | Classify the question as clocklike, Goldilocks, cloud-like or pending-decision. Pending-decision questions (one actor's discretionary act) get flat priors. | Yes. "Will the FY floor be raised" is a pending-decision question: Mertz decides. "Will revenue beat the top of the range" is Goldilocks. |
| 1b Fermi decomposition | Write P(outcome) = P(A) x P(B given A) x ... and say where the uncertainty concentrates. | Yes. Revenue = nights x ADR x take rate; margin = revenue minus a cost stack we already have by line. |
| 1c Threshold gates before merits | Enumerate every pass/fail gate and its calendar arithmetic. "The boring gate decides outcomes more often than the vivid narrative." | Yes. For Q3: the guide top is $4.77B; the cushion history says the actual lands at the top plus 0.0% on average for Q3 guides. That gate is the whole question. |
| 2 Outside view | Reference classes at several specificities; audit the event count; condition the base rate on the current regime numerically; source every point. | Yes, entirely. Section 3 of this note is that table. |
| 3 Inside view | Hypothesis-driven research, neutral queries first, a recency pass, a source recency ledger, "a flag is not a mitigation." | Yes, with one change: the recency pass for a print is the pre-announcement window (peer prints, card data, booking-curve snapshots), not news. |
| 4 Market cross-reference | Mandatory check of prediction markets; every price with a live timestamp; designate one external anchor. | Partly. There is no Metaculus question on ABNB Q3. The anchors are consensus revenue and the options-implied move. We have neither as a point-in-time history (Theo's open issue `ABNB-ISSUE-CONSENSUS-BLOOMBERG`). Until we do, the anchor row on the card is the guide midpoint and its cushion. |
| 5 Bayesian synthesis | Three independent estimates (base rate, decomposition, anchor); if they disagree by more than 15 points, find out why before blending. | Yes. Each card question below has a base-rate row, a decomposition row and an anchor row. |
| 6 Tail risk and pre-mortem | Classify thin- versus fat-tailed; write three failure scenarios dated to the resolution date; scenario table summing to 100%. | Yes. Print reactions are fat-tailed: 8 of 23 moves exceeded 10%. |
| 7 Self-audit | Bias checklist; adversarial test; extreme-probability gate for anything at or beyond 95/5. | Yes. Several of our base rates are 19/19 and 22/22. The gate says: re-read the resolution criteria and price the edge cases before writing 95%. |
| 8 Monitoring calendar | Dated catalysts, hazard-decay checkpoints, mechanical death dates. | Yes. The card has a calendar: BKNG and EXPE prints, Q3 consensus revisions, options-implied move on 4 November. |
| Update protocol | Six questions in order: already priced? which assumption moves? does it clear the noise floor (2 to 3 points)? calendar maintenance; crowd divergence needs a nameable asymmetry; which score does this earn. | Yes. This is how the team should handle every new datapoint between now and 5 November. |
| Scoring | Log score; peer score is zero-sum against the crowd; "matching the crowd earns about zero." | Only as discipline. We are not scored against peers. The equivalent statement is: a forecast that matches consensus and the implied move has no trading content. |
| Research log | Machine-parsed markdown: claims ledger with published and retrieved dates, verbatim query log, hypotheses discarded, three estimates, anchor, final minus anchor. | Yes. Keep one per card question in `research/notes/predictive/`. |

Two rules from the skill worth pinning on the wall for this study:

- "Numbers you don't compute with are numbers you don't use." Every regime adjustment to a base rate has to be a ratio, not an adjective.
- "Separate outcome accuracy from process quality." If the Q3 print lands where the card said, that does not validate the process on n = 1; if it does not, that does not falsify it either. The protocol in section 4 is judged on 23 prints, not on 5 November.

What does not transfer: the clamp to [0.1%, 99.9%], the Metaculus pdf floor mechanics in `references/continuous-questions.md`, and the peer-score strategy. Everything else in the skill is generic good practice.

---

## 2. What Theo built, and what he actually found

### 2.1 The architecture

Theo's design (`docs/superpowers/specs/2026-09-03-abnb-forecasting-agent-design.md`, approved 2026-09-03) is a four-stage chain with a separately scored output at each stage:

1. **Economic nowcast:** what operating results will Airbnb report.
2. **Guidance policy:** what management will guide, conditional on the operating state. This is the MVP centre.
3. **Expectations:** point-in-time consensus and bank estimates.
4. **Reaction:** the return distribution conditional on the actual-surprise and guide-surprise vector.

The contract (`docs/forecasting/agent-contract.md`) splits work into a control plane (the LLM, which frames, evaluates evidence and explains) and a quantitative plane (the `abnb_forecasting` package, which validates timestamps, computes baselines and writes immutable packets). The rule that matters: "An LLM-generated number never substitutes for a failed deterministic calculation. Every forecast number is a cited input, a computed result, a human assumption, or an explicitly labeled agentic adjustment." Four run modes: FORECAST, UPDATE, RESOLVE, AUDIT. Updates create a new packet with a parent link; nothing is overwritten.

The code is small and reusable:

- `baselines.py`: `seasonal_naive` (latest earlier same-quarter guide midpoint), `policy_adjusted_baseline` (operating P50 plus the median historical management offset), `median_range_width`, and `residual_interval` (empirical 10th/90th residual quantiles centred on the P50). Dependency-free, Decimal arithmetic.
- `eligibility.py`: `audit_features` partitions rows into eligible and rejected with a reason code: `availability_not_verified`, `manifest_not_approved_for_forecasting`, `feature_not_approved`, `availability_timestamp_invalid`, `not_available_strictly_before_cutoff`. Rejected rows are kept, not dropped.
- `packet.py`: builds the JSON packet, eligibility CSV, review memo and SHA-256 manifest; refuses to write into an existing run directory; refuses non-rehearsal data in the MVP.
- `research/forecasting/target_registry.csv` is a header row with no targets registered. The MVP was a "workflow rehearsal" on synthetic data, and Theo says so in every document.

### 2.2 What "eligibility" and "point-in-time" mean in his contract

A feature enters a forecast at cutoff `as_of_utc` only when all four hold:

1. `availability_status = verified`;
2. its evidence manifest is `approved_for_forecasting`;
3. `first_available_at_utc < as_of_utc`, strictly. Equality fails;
4. definition, unit, period and evidence ID are present.

Every observation carries six distinct times: reference period, observation time, first public availability, revision or vintage time, collection time, forecast cutoff. The leakage tests he names, and which we must run on our own inputs:

- same-call guidance used to predict itself;
- same-quarter letters or filings that disclose the target;
- latest-revised history standing in for the historical vintage ("a current snapshot represented as a historical vintage" is rejected, not discounted);
- transformations, imputation or feature selection fitted outside the training fold;
- "historical forecasts justified by an LLM's untraceable parametric memory."

Our datasets against that standard:

| Dataset | Point-in-time status | Note |
|---|---|---|
| `abnb_revenue_guidance_vs_actual.csv` | Pass | Guide known at the prior call (timestamps in Theo's `guidance_events.csv`, minute precision, webcast start); actual known at the print. Theo's own set, SEC-sourced. |
| `abnb_earnings_reactions.csv` | Pass as an outcome | Closing prices on dated sessions. Use as the target, never as a feature. |
| `abnb_quarterly_kpis_from_study.csv` | Pass at print date | Nights, GBV, ADR, revenue, EBITDA are disclosed in the letter. Eligible as features for the *next* print, not for the one they describe. |
| `abnb_quarterly_cost_stack_exsbc.csv` | Pass with a lag | Cash cost lines come from 10-Q/10-K XBRL, filed days after the letter. Same rule: features for the next print only. |
| Margin note section 5 guidance log | Pass | Transcripts are dated; the forward margin guide is on the call. |
| `inside_airbnb_city_snapshots.csv` | Pass if the dump date is used as first-availability | Inside Airbnb dumps are dated; the earliest is 2022-12-13, so there are at most 15 prints of overlap. Not "current snapshot" data, but revisions between dumps are not tracked. |
| `cc_listing_panel.csv`, `cc_listing_survival.csv` | Pass | Common Crawl crawls have capture dates (2021-01 to 2026-08). Coverage is thin per crawl. |
| `booking_curve_daily.csv`, `booking_curves_by_market.csv`, `market_summary_2026.csv` | Prospective only | Snapshots from 2026-06-14 to 2026-08-10. Zero prior prints. Can inform the Q3 card qualitatively; cannot be backtested. |
| `hotel_price_monitor_monthly.csv` | Pass for NSA CPI, check BEA vintages | This is the series Theo could not lawfully backfill (H-003). We have it from FRED; NSA CPI is final on release, so first availability is the BLS release date. BEA price indices revise; use the vintage rule. |
| Call roster, topics, declined-to-quantify | Pass | Derived from dated transcripts. |

### 2.3 What he found, with his numbers

From `docs/forecasting/abnb_ic_brief/generated/metrics.json` (evidence cutoff 2026-09-03):

| Diagnostic | Value | n | Theo's own reading |
|---|---|---|---|
| Revenue-weighted US/EU activity composite vs guidance y/y growth, Pearson | 0.784 | 16 | "Strong level association, but only 0.0075 Pearson above 50/50 and 0.0027 above SFO alone; 0 strict-PIT rows." |
| Same, Spearman | 0.388 | 16 | Rank correlation is half the Pearson. The level fit is driven by the 2021 to 2022 recovery. |
| Composite vs guidance acceleration, Pearson | -0.627 | 15 | "Negative relationship: the level fit does not transfer to changes in growth." |
| Acceleration direction concordance | 0.533 | 15 | Coin flip. |
| Guidance y/y vs next-day excess return (ABNB minus SPY), Pearson | 0.076 | 16 | "Weak direct mapping." |
| Guidance acceleration vs excess return | 0.082 | 15 | "Also weak." |
| Sequential guide % change vs excess return | 0.032 | 19 | Direction aligned 7 of 19. "Seasonal quarter mix dominates raw sequential changes." |
| Event returns, 23 prints | mean ABNB +1.16%, mean excess +0.71%, median excess -0.05%, sd 8.8% | 23 | "Visibly dominated by event dispersion." |
| H-001 (Fed H.10 broad dollar) directional hits | 9 of 16 overall; 3 of 4 early, 6 of 12 late | 16 | "Regime-stability warning, not statistical evidence." The only strict-PIT signal he had. |
| Strict-PIT rows in the composite | 0 | | All rows are current provider snapshots. |

The edge-discovery hypotheses and their verdicts (runs `20260903T053309Z_abnb_readiness`, `20260903T062839Z_abnb_edge_discovery`, `20260903T231817Z_abnb_us_altdata_sleeve`, `20260904T012519Z_abnb_adr_pilot_001`):

| ID | Signal | Verdict | Why |
|---|---|---|---|
| H-001 | Fed H.10 broad dollar, 28-day change, negative expected sign | WEAK / UNSTABLE | Only strict-PIT source. 9/16 hits; 75% early cohort, 50% late. No magnitude test. |
| H-002 | ECB EUR/USD | INELIGIBLE | API does not expose initial publication timestamps. Sensitivity (16:00 UTC assumption) 10/16, not promoted. |
| H-003 | BLS lodging CPI (v2: trailing 3-month NSA y/y) | INELIGIBLE / NOT TESTABLE | BLS robots disallow; FRED key absent; series ID 404. Zero rows. |
| H-004 | Washington State Ferries ridership | INCONCLUSIVE | Permission gate failed; no data collected. |
| H-005 | Orange County FL tourist development tax | INCONCLUSIVE | Not collected; one hotel-heavy county; publication lag likely too late. |
| H-006 | NYC OSE short-term-rental registrations | INCONCLUSIVE, CONTROL_ONLY | Regime identifier for Local Law 18, 4 events of coverage. |
| H-007 | SFO trailing-3-month passenger y/y | WATCH_PROSPECTIVELY | Diagnostic r = 0.816 vs guide y/y, Spearman 0.48, acceleration concordance 0.40. Current snapshot, 0 strict-PIT rows. |
| H-008 | FHWA vehicle-miles travelled | INCONCLUSIVE | Robots disallow the payload path. |
| H-009 | Census QSS accommodation revenue | INCONCLUSIVE | API robots rejection; metadata 404. |
| H-010 | Multi-airport breadth (SFO, PANYNJ, LAX) | INCONCLUSIVE | PANYNJ and LAX permission gates false. |
| H-011 | US activity, available provider (= SFO) | WATCH_PROSPECTIVELY | Same numbers as H-007. |
| H-012 | EU27 platform nights (Eurostat), 50/50 and v2 revenue-weighted composite with SFO | WATCH_PROSPECTIVELY | EU27 alone r = 0.725; 50/50 composite 0.778; v2 weights 50.4% US / 49.6% EMEA from the FY2025 10-K give 0.784. Weight not eligible before 2026-02-12. |

Fifteen other source candidates (NASA Black Marble night lights, NOAA smoke, NPS visits, FTA transit ridership, municipal STR licence files, Melbourne pedestrian counters, MarineCadastre AIS, NYC 311) were scored on an 100-point rubric and none was promoted. One NYC 311 aggregate request was made under a superseded robots interpretation and quarantined. The 50-source Eurostat expansion added 590,949 observations and, in Theo's words, "breadth increased, provider independence and vintage eligibility did not."

His guidance dataset (`research/guidance/data/normalized/`) is the cleanest thing he left: 23 events with minute-precision timestamps, 20 numeric revenue ranges and 3 qualitative ones, 23 revenue actuals with reported and constant-currency y/y, 69 market-return rows (ABNB vs QQQ at 1, 5 and 20 sessions), 33 qualitative direction items for nights, ADR, GBV and take rate, and an empty `model_results.csv`. The open issues are honest: no point-in-time consensus without Bloomberg (high severity), event times are webcast start rather than 8-K acceptance (medium), tone coding is single-coder (medium).

### 2.4 The three most useful things in Theo's work

1. **The four-error decomposition.** Being wrong about the print, wrong about the guide, wrong about what was expected, and wrong about how the stock maps a surprise are four different mistakes. Our card questions are grouped that way in section 5, and the protocol scores them separately.
2. **The eligibility rule, applied with its reason codes.** "Equality fails" and "a current snapshot is not a historical vintage" are the two rules most likely to catch us. Agents 02 to 05 should emit a rejected-rows table with those reason codes, not a footnote.
3. **The promotion ladder and its kill condition.** Hypothesis, then eligible data, then out-of-sample residual lift over a named baseline, then stability across regimes and leave-one-out, then a decision input net of what is already priced. His core falsifier: "If eligible features cannot produce stable out-of-sample residual improvement after matching seasons and regimes, the information-edge thesis fails even if in-sample level correlations remain high." The 0.78-then-minus-0.63 result is the worked example of why.

---

## 3. Base rates for Airbnb prints, 2020Q4 to 2026Q2

Source: `data/processed/predictive/01_print_base_rates.csv` and `01_print_base_rates_summary.csv`, built by `analysis/src/predictive/01_print_base_rates.py`. Hand-entered inputs are flagged in the `source_flags` column: 2020 quarterly nights (backed out of the 2021 letters' y/y figures) and Q4 2020 Adjusted EBITDA of -$21M. The margin-versus-guide and FY-floor codings come from section 5 of the margin note and are printed in full in the script.

### 3.1 Per print

| Print | Rev y/y | vs mid | vs top | Next-q guide implied y/y vs reported, pp (raw / cushion-adj.) | Nights y/y | Nights accel, pp | Adj. EBITDA margin | Margin vs guide | FY floor | ABNB 1d | Excess 1d | Excess 5d | Excess 20d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020Q4 | -22% | qual. | qual. | qual. | -39% | -11.0 | -2.4% | n/a | none | +13.3% | +12.9% | +1.8% | -2.8% |
| 2021Q1 | +5% | qual. | qual. | qual. | +13% | +52.2 | -6.7% | in line | none | +4.0% | +1.8% | -2.6% | +2.5% |
| 2021Q2 | +299% | qual. | qual. | qual. | +197% | +183.6 | 16.3% | above | none | +1.1% | +0.7% | -4.7% | +6.8% |
| 2021Q3 | +67% | qual. | qual. | +0.1 / n/a | +29% | -167.8 | 49.2% | in line | none | +13.0% | +12.9% | +9.3% | -2.8% |
| 2021Q4 | +78% | +6.8% | +3.5% | -15.1 / n/a | +59% | +29.5 | 21.7% | in line | introduced | +3.6% | +3.7% | -9.2% | -9.1% |
| 2022Q1 | +70% | +4.4% | +2.0% | -14.2 / n/a | +59% | 0.0 | 15.2% | above | raised | +7.7% | +4.3% | -14.2% | -15.5% |
| 2022Q2 | +58% | +1.2% | -1.2% | -31.5 / decel | +25% | -33.7 | 33.8% | above | held | -1.1% | -3.9% | -2.5% | +1.0% |
| 2022Q3 | +29% | +1.9% | +0.1% | -8.9 / decel | +25% | +0.3 | 50.5% | above | held | -13.4% | -10.0% | -7.3% | -13.0% |
| 2022Q4 | +24% | +3.4% | +1.2% | -5.7 / decel | +20% | -4.9 | 26.6% | above | introduced | +13.4% | +12.6% | +9.3% | -3.5% |
| 2023Q1 | +20% | +1.8% | -0.1% | -5.9 / decel | +19% | -1.6 | 14.4% | in line | held | -10.9% | -12.0% | -18.8% | -16.7% |
| 2023Q2 | +18% | +3.5% | +1.4% | -1.8 / accel | +11% | -7.6 | 33.0% | in line | raised | -0.5% | 0.0% | -2.1% | -7.7% |
| 2023Q3 | +18% | +1.4% | -0.1% | -5.0 / decel | +13% | +2.5 | 54.0% | in line | raised | -3.3% | -5.1% | -6.0% | -3.2% |
| 2023Q4 | +17% | +3.2% | +2.2% | -4.2 / decel | +12% | -1.5 | 33.3% | in line | introduced | -1.7% | -2.8% | -0.4% | +6.5% |
| 2024Q1 | +18% | +4.5% | +3.5% | -8.9 / decel | +9% | -2.5 | 19.8% | in line | held | -6.9% | -7.1% | -10.6% | -12.2% |
| 2024Q2 | +11% | +1.4% | +0.3% | -2.1 / accel | +9% | -0.8 | 32.5% | above | held | -13.4% | -12.3% | -15.6% | -16.5% |
| 2024Q3 | +10% | +0.9% | +0.1% | -1.1 / accel | +8% | -0.2 | 52.5% | in line | raised | -8.7% | -8.8% | -7.7% | -9.6% |
| 2024Q4 | +12% | +2.7% | +1.6% | -7.0 / decel | +12% | +3.8 | 30.8% | in line | introduced | +14.4% | +14.0% | +5.4% | -2.4% |
| 2025Q1 | +6% | +1.0% | +0.1% | +3.9 / accel | +8% | -4.4 | 18.4% | in line | held | +1.0% | -0.5% | +0.5% | -3.7% |
| 2025Q2 | +13% | +2.5% | +1.5% | -4.2 / decel | +7% | -0.5 | 33.7% | above | held | -8.0% | -8.4% | -6.9% | -5.3% |
| 2025Q3 | +10% | +0.9% | -0.1% | -1.5 / accel | +9% | +1.4 | 50.1% | in line | raised | +0.3% | +0.6% | +1.1% | +0.9% |
| 2025Q4 | +12% | +3.3% | +2.1% | +2.9 / accel | +10% | +1.0 | 28.3% | in line | introduced | +4.6% | +4.4% | +8.9% | +10.1% |
| 2026Q1 | +18% | +2.6% | +1.8% | -2.7 / flat | +9% | -0.6 | 19.4% | above | raised | +0.7% | -1.6% | -8.4% | -6.4% |
| 2026Q2 | +17% | +1.1% | +0.2% | -1.5 / accel | +10% | +1.1 | 35.0% | in line | raised | +17.4% | +16.3% | +19.6% | n/a |

Definitions. "vs mid" and "vs top" are revenue against the range issued on the prior call. "Next-q guide implied y/y" is the new midpoint over the year-ago actual for the guided quarter; "cushion-adj." adds the mean beat over guides already resolved at that date (point-in-time; first available from 2022Q2). Nights acceleration is the y/y growth change against the prior quarter in percentage points; 2021 values are COVID-lap artefacts. "Margin vs guide" codes the print against the direction the prior call gave: above, in line, or below. "FY floor" is what this call did to the full-year margin guide. Returns are close-to-close from the last close before the release; excess is minus QQQ.

### 3.2 Unconditional base rates

| Question | Rate | n | Comment |
|---|---|---|---|
| Revenue beats guide midpoint | 100% | 19 | Mean +2.55%, median +2.5%, minimum +0.9%. Last 8 guides: +1.88%. |
| Revenue beats top of range | 79% | 19 | 90% since 2024Q1 (n=10). Mean beat vs top +1.06%. |
| Revenue beats top of range, Q3 guides only | 50% | 4 | +0.1, -0.1, +0.1, -0.1. Q3 is the seasonally large quarter and the cushion is thinnest there. Mean 0.0%. |
| Quarterly margin at or better than guided direction | 100% | 22 | Above the guided direction 8 times (36%), in line 14, below 0. |
| Nights y/y accelerates vs prior quarter | 35% | 23 | 36% since 2023Q1 (n=14). |
| Next-q guide midpoint implies acceleration, raw | 10% | 20 | 85% imply deceleration. This is the cushion at work: the guide is set to be beaten. |
| Next-q guide implies acceleration after adding the trailing cushion | 41% | 17 | 53% imply deceleration. Closer to a fair question. |
| FY margin floor raised on this call | 30% | 23 | 7 raised, 7 held, 5 introduced (February calls), 4 none (2021). |
| FY floor raised, numeric-floor era (2023Q4 on) | 36% | 11 | 50% on the 8 non-February calls. |
| FY floor raised on a Q3 print, 2023 on | 100% | 3 | 2023Q3, 2024Q3, 2025Q3. n = 3; treat as "this is when it usually happens", not 100%. |
| 1-day excess return > 0 | 48% | 23 | 40% since 2024Q1 (n=10). |
| 5-day excess return > 0 | 35% | 23 | |
| 20-day excess return > 0 | 27% | 22 | Mean -4.7%, median -3.6%. The stock has tended to give back and then some. |
| ABNB 1-day move exceeds 7% in absolute value | 48% | 23 | 50% since 2024Q1. Up more than 7%: 26%. Down more than 7%: 22%. |
| ABNB 1-day move exceeds 10% in absolute value | 35% | 23 | |
| Mean / median absolute 1-day move | 7.1% / 6.9% | 23 | Fat-tailed: 17.4%, 14.4%, 13.4%, -13.4%, -13.4%. |
| Mean / median / sd of 1-day excess | +0.5% / 0.0% / 8.7% | 23 | Theo's version in `metrics.json`: +0.71% / -0.05% / 8.8%. Same story. |

### 3.3 Conditional base rates: excess return by print bucket

Each cell shows mean and median 1-day excess return, the share positive, and n. The p-values are two-sided permutation tests on the difference in means (20,000 shuffles) and Fisher exact tests on the share positive; they are in the summary CSV.

| Bucket | Mean 1d | Median 1d | P(1d > 0) | Mean 20d | n | Test |
|---|---|---|---|---|---|---|
| Revenue beat top of range | +0.3% | -0.5% | 40% | -6.3% | 15 | vs midpoint-only: perm p = 0.28, Fisher p = 1.0 |
| Revenue beat midpoint only | -5.1% | -4.5% | 25% | -4.5% | 4 | |
| Big beat (above median 2.5%) | +3.1% | +3.7% | 56% | -4.5% | 9 | vs small beat: perm p = 0.053, Fisher p = 0.17 |
| Small beat (at or below 2.5%) | -4.4% | -6.8% | 20% | -7.3% | 10 | |
| Next-q guide implies accel (cushion-adj.) | 0.0% | 0.0% | 43% | -4.4% | 7 | 3 buckets; not tested |
| Next-q guide implies decel (cushion-adj.) | -2.5% | -5.1% | 22% | -5.4% | 9 | |
| Nights accelerated | +4.6% | +2.8% | 88% | +0.8% | 8 | vs not: perm p = 0.10, Fisher p = 0.009 |
| Nights did not accelerate | -1.7% | -2.8% | 27% | -7.2% | 15 | |
| Nights accelerated, 2022Q2 on | +6.0% | +4.4% | 80% | +1.4% | 5 | vs not: perm p = 0.017, Fisher p = 0.010 |
| Nights did not accelerate, 2022Q2 on | -4.6% | -5.5% | 8% | -7.3% | 12 | |
| Margin above guided direction | -2.3% | -2.8% | 38% | -6.6% | 8 | vs in line: perm p = 0.36, Fisher p = 0.68 |
| Margin in line with guided direction | +1.2% | +0.3% | 50% | -3.7% | 14 | |
| FY floor raised | +0.8% | 0.0% | 43% | -6.9% | 7 | 4 buckets; not tested |
| FY floor held | -7.7% | -8.4% | 0% | -9.5% | 7 | |
| FY floor introduced (February) | +6.4% | +4.4% | 80% | +0.3% | 5 | |
| No FY guide (2021) | +7.1% | +7.4% | 100% | +0.9% | 4 | |

Diagnostic correlations with the 1-day excess return (all in the summary CSV with Pearson, Spearman, parametric and permutation p-values):

| Series | Pearson r | Spearman rho | n | Permutation p |
|---|---|---|---|---|
| Revenue beat vs midpoint, % | 0.24 | 0.29 | 19 | 0.33 |
| Revenue beat vs top, % | 0.22 | 0.32 | 19 | 0.36 |
| Next-q guide implied y/y minus reported y/y, pp | 0.11 | 0.18 | 20 | 0.68 |
| Nights acceleration, pp | -0.17 | 0.12 | 23 | 0.46 |
| Nights y/y, % | -0.02 | 0.20 | 23 | 0.94 |
| Margin y/y change, pp | 0.05 | -0.10 | 18 | 0.85 |
| Revenue y/y, % | 0.03 | 0.01 | 23 | 0.87 |
| Excess 1d vs excess 20d | 0.42 | 0.53 | 22 | 0.055 |
| Excess 1d vs excess 5d | 0.79 | 0.73 | 23 | <0.001 |

### 3.4 How to read this

- **Management behaviour is close to deterministic; the stock is not.** 19 of 19 midpoint beats and 22 of 22 margin directions met, against a coin-flip 1-day excess return. The beat is the base case, and the base case is priced. Theo's 0.03 to 0.08 correlations between guidance and return are reproduced here: beat size against return is r = 0.24, p = 0.33.
- **Small beats are punished more than big beats are rewarded.** The median-split difference (+3.1% vs -4.4%) is the largest continuous effect in the file and it is at p = 0.053 on n = 19, which is exactly what one spurious hit in a dozen cuts looks like. Hold it as a hypothesis for agent 04's reaction function, not as a result.
- **Nights acceleration is the print variable that matters.** 7 of 8 acceleration prints had a positive excess return, 4 of 15 non-acceleration prints did. The Pearson correlation with acceleration in percentage points is negative because the 2021 COVID-lap values (+184, -168) dominate; the sign test is the right statistic here. Fisher p = 0.009 does not survive a Bonferroni haircut at the 12 or so cuts in this file (0.05 / 12 = 0.004), and neither does the 2022Q2-on version (p = 0.010, n = 17). It is consistent with what the major-moves file says in words: four of the five worst prints (2022Q3 "Q4 nights guided to moderate", 2023Q1 "nights guided below revenue", 2024Q2 "shorter lead times and slowing US demand", 2025Q2 "H2 nights to moderate") were demand-guide events, the fifth (2024Q3) was an EPS miss on expense growth, and the three best (2022Q4, 2024Q4, 2026Q2) were guide or nights beats. This is a reaction-function fact. Nights are disclosed in the print, so it is tradable only if nights acceleration can be forecast before the print. That is the question for agents 02, 03 and 05.
- **The FY-floor buckets are seasonality in disguise.** "Introduced" is every February call; "held" clusters in Q1 and Q2 prints; "raised" is Q3 and mid-year. The 0 of 7 positive returns on "held" calls is real in the sample but says as much about Q1 and Q2 prints as about the floor. Do not put it on the card as a driver.
- **Post-print drift is negative.** Mean 20-day excess -4.7%, positive only 6 of 22 times, and the 1-day move carries into the 20-day (rho = 0.53). This is a feature of a stock that de-rated from 2021 to 2024; the 2024Q1-on sample is small (10 prints) and mixed. Do not build a strategy on it; do note it when the card asks about the 5-day and 20-day horizon.
- **Regime.** The 2024Q1-on sample has a lower beat (mean +2.09% vs midpoint, +1.11% vs top), a lower positive-return rate (40%), and the same frequency of 7%-plus moves (50%). The guide range narrowed from 6% of the midpoint (2021) to 1.7% (2026), and the cushion narrowed with it. When conditioning a base rate on the current regime, use the last 8 to 10 prints as the reference class and say so.
- **n.** Twenty-three prints, of which 19 have a numeric guide, 17 have a cushion-adjusted guide direction and 10 are in the current regime. The smallest detectable |r| at p < 0.05 is 0.41 at n = 23 and 0.46 at n = 19. Any correlation below that is indistinguishable from zero here, whatever its sign.

---

## 4. The evaluation protocol: what agents 02 to 05 must show before anything is called predictive

This is the bar. A result that clears it is labelled PREDICTIVE in the agent's note. A result that does not is labelled EXPLANATORY or DESCRIPTIVE, using Theo's section labels, and still gets written up because negative results are part of the record.

**4.1 Sample.** State n, the exact prints included, and why any were excluded. Twenty-three is the ceiling; 19 if the target needs a numeric guide; fewer if the feature starts late (Inside Airbnb: 15; booking curves: 0). Report the effective n after removing 2021 COVID-lap prints if the feature is a growth rate.

**4.2 Association, with all three p-values.** Pearson r and Spearman rho with parametric p-values, and a permutation p-value (at least 10,000 shuffles of the target) for whichever statistic is reported as the headline. Spearman and permutation are there because 23 points with a 2021 outlier will give a Pearson r that means nothing. If Pearson and Spearman disagree in sign, say which one you believe and why.

**4.3 Out-of-sample error against two baselines.** Either leave-one-out or expanding-window walk-forward (Theo's design: minimum 8 training events, one forecast per event, all transformations fitted inside the fold). Report MAE and RMSE of the candidate forecast and of both baselines on the same held-out prints:

- Baseline A, seasonal naive: same quarter one year earlier grown at the most recently reported y/y rate (for revenue, nights, take rate) or the same-quarter-prior-year value (for margin).
- Baseline B, management guide midpoint (for revenue), or the direction management guided (for margin), or the guide midpoint plus the trailing mean cushion (the stronger revenue baseline).

The summary CSV carries a worked example (block `baseline_demo_revenue_forecast`) on the 16 prints from 2022Q3 to 2026Q2 where at least three prior guides had resolved, forecast error as a percent of actual revenue:

| Revenue forecaster | MAE | RMSE | Max abs error | Mean signed error |
|---|---|---|---|---|
| Seasonal naive (year-ago revenue grown at last reported y/y) | 4.06% | 6.57% | 22.6% | +2.2% |
| Guide midpoint | 2.19% | 2.42% | 4.3% | -2.2% (always low) |
| Guide midpoint plus prior-print mean cushion | 1.12% | 1.38% | 2.2% | +0.8% |

So the bar for a revenue nowcast is an out-of-sample MAE below about 1.1%, not below the 4% a seasonal model gives. A feature that does not beat both baselines on MAE out of sample has not shown forecast value, however high its in-sample correlation. Report fold-level errors, not just the aggregate, and show whether the improvement is concentrated in one or two prints (Theo's promotion rule: no single event more than half the gain, improvement in at least 60% of folds).

**4.4 Point-in-time check.** For every input series, state the first-availability date rule and confirm it is strictly before the print date for every row used. Emit the rejected rows with a reason code from Theo's list (`availability_not_verified`, `availability_timestamp_invalid`, `not_available_strictly_before_cutoff`, plus `current_snapshot_not_vintage` for any series that has been revised or re-scraped). Same-print disclosures (nights, revenue, margin, the new guide) are targets or reaction-function inputs, never features for that print. If the input is a current snapshot with no vintage history, the result is DESCRIPTIVE, full stop.

**4.5 Multiple comparisons.** Count every series-target-window combination tested across the whole study and report it. We are testing dozens of series against a handful of targets on at most 23 prints, so expect about one spurious p < 0.05 hit for every 20 tests. Report the Bonferroni threshold (0.05 divided by the count) alongside each p-value, or a Benjamini-Hochberg q-value. A single p between 0.01 and 0.05 on n = 23 with no out-of-sample lift is not a finding. This note tested 9 correlations and 5 two-bucket splits; its own threshold is about 0.004.

**4.6 Stability.** Leave one print out and report the range of the statistic. Report it separately for 2022Q2 on (post COVID lap) and 2024Q1 on (current regime). If the sign flips in either sub-sample, say so.

**4.7 Separate the four errors.** Say which stage the result is about: nowcast (predicts the print), guidance policy (predicts the guide), expectations (predicts consensus or the implied move), or reaction (maps a known surprise to a return). A reaction-function result (section 3.3's nights finding) is not a nowcast result and does not by itself support a pre-print position.

**4.8 Labelling.** PREDICTIVE requires 4.1 to 4.7 all present, out-of-sample MAE below both baselines, and a permutation p below the multiple-comparisons threshold, or a pre-registered single test at p < 0.05. Anything else is EXPLANATORY. Anything with zero point-in-time rows is DESCRIPTIVE. Write the label in the first line of the note.

---

## 5. Prediction card template: Q3 2026 print, Thursday 5 November 2026 (after close; reaction session 6 November)

Format follows the skill's forecast output: base rate from section 3, Fermi decomposition, three estimates (base rate, decomposition, anchor), what would move it, the falsifier. **Probabilities are deliberately not final.** Each question carries the base-rate prior and a stated adjustment range; the team finalises the numbers in late October after the peer prints and the consensus/implied-move check. Resolution source for all questions: the Q3 2026 shareholder letter (8-K Exhibit 99.1) and the 6 November closing prices.

Shared context for the card:

- Guide issued 6 August 2026: revenue $4.69B to $4.77B (midpoint $4.73B, +14.5% to +16.5% y/y on $4,095M); Adjusted EBITDA up y/y with margin "down slightly" versus 50.1%; FY2026 margin at least 35.5%; take rate flat for 2026; "material increase" in AI spend; Q3 "GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked" (shareholder letter outlook, excerpt `ABNB-2026Q2-DRIVER-061` in Theo's `source_excerpts.csv`). Q2 nights were +10.3%, accelerating from +9.2%.
- Regime reference class: the 10 prints from 2024Q1. Cushion vs midpoint +2.09%, vs top +1.11%; P(1d excess > 0) 40%; P(|1d| > 7%) 50%.
- Q3 reference class: the 4 Q3 guides (2022 to 2025) beat the midpoint by +1.9, +1.4, +0.9, +0.9% and the top by +0.1, -0.1, +0.1, -0.1%.

### Q1. Will Q3 2026 revenue exceed $4,770M (top of the guided range)?

| Field | Entry |
|---|---|
| Type | Binary |
| Base-rate prior | 79% (15/19 all guides); 90% (9/10 since 2024Q1); 50% (2/4 Q3 guides). Weighted toward the Q3 class because the cushion is seasonal: **prior 60 to 70%**. |
| Decomposition | Revenue = nights x ADR x take rate. Top of range is +16.5% y/y. Q2 delivered +17% on nights +10.3%, ADR +5.3% (+4% ex-FX), take rate 13.3% vs 13.2%. Q3 needs nights at or above +10%, ADR at or above +4% including a fading FX tailwind, and take rate at or above 17.9% (Q3 2025). Each leg is roughly the Q2 run-rate; the question is whether the FX tailwind (about 1 point in H1) fades faster than ADR ex-FX holds. |
| Anchor | Guide midpoint plus trailing cushion (2.55% all-sample; 1.88% last 8) puts the point estimate at $4,819M to $4,851M, or 1.0% to 1.7% above the top. Consensus revenue: to be fetched in late October; if it sits at or above $4.78B the question is whether the beat is already the expectation. |
| What moves it | BKNG and EXPE Q3 prints (late October / early November): European and US room-night growth. Dollar index change July to September versus a year earlier. Any pre-announcement or conference commentary in September and October. Booking-curve snapshots (`booking_curves_by_market.csv`) if agent 03 can show them tracking nights. |
| Pre-mortem (it is 6 November and the answer was no) | FX tailwind turned to zero or negative on a stronger dollar in August to September; nights slowed to +8 to +9% as the RNPL lap and hotel/services incentives hit; take rate below 17.9% on customer incentives for new businesses, which management already flagged. |
| Falsifier for the prior | A second consecutive Q3 print at or below the top of the range would be the first time the regime cushion failed twice in the large quarter. |
| Adjustment range | Base rate 60 to 70%; decomposition pushes up; a Q3 seasonal class of 2/4 pulls down. Final to be set in late October; do not exceed 85% without passing the extreme-probability gate. |

### Q2. Will Q3 2026 Adjusted EBITDA margin be at or above 49.0%?

| Field | Entry |
|---|---|
| Type | Binary (49.0% is the margin note's base case and the midpoint of "down slightly" from 50.1%) |
| Base-rate prior | Margin has met or beaten the guided direction 22 of 22 times, and exceeded it 8 of 22 (36%). "Down slightly" from 50.1% resolves as met anywhere from about 48% to 50%. So P(margin at or above the guided direction) is very high; P(at or above 49.0%) is the coin-flip inside that band. **Prior 55 to 65%.** |
| Decomposition | Margin = 1 minus cost stack over revenue. Section 11 of the margin note: bear 48.3%, base 49.0%, bull 50.2%. Revenue at $4.82B (Q1 anchor) versus the $4.73B used in the scenarios adds about 0.5 to 0.9 points of margin if costs are fixed in dollars. S&M cash growth is the swing line: +25% y/y or less gets 49%; the 1H pace of +30% gets 48.3%. AI spend is the flagged unknown. |
| Anchor | Consensus adjusted EBITDA for Q3 (to fetch). The guided direction itself: "down slightly" implies 48.5 to 49.5%. |
| What moves it | Q2 support cost per booking (-16%) and headcount commentary; any disclosure on AI spend run-rate; S&M growth at BKNG and EXPE as a read on marketing intensity. |
| Pre-mortem | Revenue beat reinvested in the quarter (management's stated habit); AI spend larger than support savings; a one-off in G&A (lodging taxes, legal) as in Q3 2023's $49M. |
| Falsifier | A print below 48.0% would be the first quarterly margin worse than the guided direction in the record. |
| Adjustment range | 55 to 65%; the revenue beat is the upward pressure, the AI-spend language the downward. |

### Q3. Will Q3 2026 Nights and Experiences Booked grow at or above 10.0% y/y?

| Field | Entry |
|---|---|
| Type | Binary; Q3 2025 base 133.6M, so 10.0% means at or above 147.0M. |
| Base-rate prior | Nights accelerated 8 of 23 prints (35%); 5 of 14 since 2023Q1. Q2 was +10.3%, Q1 +9.2%, Q4 2025 +9.8%. Holding at or above 10% requires acceleration or a flat quarter at +10.3%; "flat" (within 0.5pp) has happened 4 of 23 times. **Prior 45 to 55%.** |
| Decomposition | Nights growth = core markets (US roughly flat to low single digits, Europe mid single digits) plus expansion markets (growing about twice the core) plus new offerings (services, experiences, hotels) plus the RNPL lap (US launch Q3 2025). Management guided "low double-digit growth in Nights and Seats Booked" for Q3, which brackets 10%; the RNPL lap is the named headwind. Note the metric is now "Nights and Seats Booked"; check that the Q3 letter's definition is comparable to the 133.6M base before resolving. |
| Anchor | Management's Q3 guide, "low double-digit" (Theo's `guidance_items.csv` row 55, excerpt `ABNB-2026Q2-DRIVER-061`); consensus nights (to fetch). |
| What moves it | This is the question the alt-data agents are working. Any PIT-passing series that forecast nights acceleration on past prints (protocol section 4) moves this number; nothing else should. BKNG room nights and EXPE lodging bookings as a demand read. |
| Pre-mortem | US demand soft (the 2024Q2 pattern); the RNPL lap subtracts 1 to 2 points; a September macro or weather disruption. |
| Falsifier | Nights below +9.0% would be a deceleration of more than a point and would flip Q6. |
| Adjustment range | 45 to 55% base; agents 02 to 05 supply the adjustment if and only if their series pass section 4. |

### Q4. Will the FY2026 Adjusted EBITDA margin floor be raised above 35.5%?

| Field | Entry |
|---|---|
| Type | Binary; "raised" means a numeric floor above 35.5% or a stated point estimate at or above 36.0%. "At least 35.5%" restated resolves no. |
| Base-rate prior | Raised on 7 of 23 calls (30%); 4 of 11 in the numeric-floor era; 3 of 3 Q3 prints since 2023 (2023Q3 +150 bps language, 2024Q3 to 35.5%, 2025Q3 to 35%). Pending-decision question: the skill says no option above about 45 to 50% on positioning alone. **Prior 40 to 50%.** |
| Decomposition | Floor gets raised when 9-month actuals plus the Q4 guide arithmetic make the old floor trivially safe. 1H 2026 margin was 28.3% on $6.29B ($1,780M EBITDA); at Q3 49% on $4.82B, 9-month margin is about 37.3%, and with Q4 revenue near $3.2B, Q4 needs only about 29% to hit 35.5% for the year (Q4 2025 was 28.3%). A 36% floor needs Q4 at about 31.5%. Management raised the floor in each of the last three Q3 calls under similar arithmetic. |
| Anchor | None external. Management's own words on 6 August: "there's a relative floor"; no 2027 view. |
| What moves it | Q3 margin (Q2 above): at or above 49.5% makes a raise the default; at or below 48.5% makes a hold the default. The size of the AI-spend language. |
| Pre-mortem | Management holds 35.5% and spends the upside ("we are not in profit maximization mode"); a raise to "about 36%" that the market treats as a hold. |
| Falsifier | A hold with a Q3 margin above 49.5% would break the three-for-three pattern. |
| Adjustment range | 40 to 50% pending the Q3 margin; cap at 60% before the print. |

### Q5. Will the implied Q3 2026 take rate (revenue / GBV) exceed 17.9%?

| Field | Entry |
|---|---|
| Type | Binary; Q3 2025 was 17.9% ($4,095M / $22.9B). |
| Base-rate prior | Same-quarter take rate y/y over the 18 comparable quarters (1Q22 to 2Q26): up 10, down 6, flat 2 (from `abnb_quarterly_kpis_from_study.csv`; flat means within 5 bps). Down 5 of the last 8. 2026 so far: Q1 9.2% vs 9.3% (down), Q2 13.3% vs 13.2% (up). Management guided take rate "flat for 2026" on RNPL timing and incentives. **Prior 40 to 50%.** |
| Decomposition | Take rate = revenue / GBV. RNPL shifts revenue recognition later (a Q3 headwind as it laps its US launch); FX fee (+20 bps in 2025) is in the base; customer incentives for hotels, services and experiences are a stated drag; higher ADR mechanically lifts it slightly through fixed-fee components. |
| Anchor | Management: "flat for 2026." Consensus GBV (to fetch) implies a consensus take rate. |
| What moves it | Q2 commentary on RNPL adoption; any change to host or guest fee structure; mix toward hotels (lower take rate). |
| Pre-mortem | Incentives for new offerings are larger than modelled; RNPL adoption rose faster in Q3 2026 than Q3 2025. |
| Falsifier | Take rate below 17.6% (30 bps down) with revenue still beating would mean ADR did the work; re-weight the nowcast toward GBV. |
| Adjustment range | 40 to 50%. |

### Q6. Will the 1-day excess return (ABNB minus QQQ, 5 November close to 6 November close) be positive?

| Field | Entry |
|---|---|
| Type | Binary |
| Base-rate prior | 48% (11/23); 40% since 2024Q1 (4/10). Conditional on nights acceleration: 88% (7/8); on no acceleration: 27% (4/15). Conditional on a big beat (above 2.5% vs midpoint): 56%; small beat: 20%. **Prior 40 to 50% unconditional; the conditional table is the update rule once the print is out, not before.** |
| Decomposition | P(up) = P(nights accel) x P(up given accel) + P(no accel) x P(up given no accel). With Q3's prior of 45 to 55% and the conditional rates above: 0.5 x 0.875 + 0.5 x 0.27 = 0.57. That is above the unconditional 48% because the record's acceleration prints are over-weighted in 2021; using the 2022Q2-on conditionals (80% and 8%) gives 0.44. The two decompositions bracket the base rate, which is the honest answer. |
| Anchor | Options-implied move on 4 November (to fetch); consensus revenue, EBITDA, nights and GBV. The skill's rule: if our number is within 10 points of what the implied move and consensus already say, say we are deferring to the market. |
| What moves it | Nothing before the print except a forecast of nights acceleration that passes section 4. After the print: nights y/y versus +10.3%, revenue versus consensus (not versus the guide), the Q4 guide midpoint versus consensus, and the FY floor. |
| Pre-mortem | Beat on every line and stock down: happened 2022Q3, 2024Q3, 2025Q2, each time on a nights or Q4 guide that "moderated." Miss and stock up: has not happened; the guide has never been missed. |
| Falsifier | This question resolves the reaction function; it does not test the nowcast. |
| Adjustment range | 40 to 50% pre-print. Do not move more than 5 points on any single input that has not passed the protocol. |

### Q7. Will the absolute 1-day ABNB move exceed 7%?

| Field | Entry |
|---|---|
| Type | Binary; |close-to-close return| > 7.0%. |
| Base-rate prior | 48% (11/23); 50% since 2024Q1. Up more than 7%: 26%; down more than 7%: 22%. Mean absolute move 7.1%, median 6.9%. **Prior 45 to 50%.** |
| Decomposition | The threshold sits at the median of the history, so the base rate is close to a coin flip by construction. Fat tails: 8 of 23 moves exceeded 10%. Big moves cluster on nights surprises and Q4-guide surprises, not on revenue beats (the beat is expected). |
| Anchor | Options-implied move on 4 November. Historically the implied move for ABNB prints has sat near 8 to 10%; if the implied is above 8% the market is already pricing a better-than-even chance of clearing 7%. Fetch and record with a timestamp. |
| What moves it | Implied volatility into the print; the size of the consensus dispersion on nights; whether the Q2 print's +17.4% reset positioning. |
| Pre-mortem | A print in line on every KPI with an in-line Q4 guide (the 2025Q3 pattern: +0.3%). |
| Falsifier | None; this is a calibration question. Score it. |
| Adjustment range | 45 to 55%; lean above 50% only if the implied move is above 8.5%. |

### Q8 (optional). Will the Q4 2026 revenue guide midpoint imply y/y growth at or above the just-reported Q3 growth, after adding the trailing cushion?

| Field | Entry |
|---|---|
| Type | Binary; cushion-adjusted implied y/y at or above reported Q3 y/y minus 0.5pp. |
| Base-rate prior | Raw: the guide midpoint implied acceleration 2 of 20 times (10%). Cushion-adjusted: 7 of 17 (41%), and 4 of the last 6. **Prior 40 to 50%.** |
| Decomposition | Q4 2025 was $2,778M, +12%. Management said "at least mid-teens" for FY2026; a Q4 guide midpoint of $3,180M (+14.5%) plus a 2% cushion implies about +17%, roughly flat against a Q3 print of +17 to +18%. Acceleration on this definition needs a Q4 midpoint above about $3.2B. |
| Anchor | Consensus Q4 revenue (to fetch). |
| What moves it | The FY revenue language on 5 November; the Q3 beat size (a big Q3 beat with a held FY implies a lower Q4). |
| Pre-mortem | Management guides Q4 conservatively into the lap of RNPL merchandising (launched Q4 2025). |
| Falsifier | A raw midpoint implying acceleration would be only the third in 21 guides; if it happens, the cushion assumption for 2027 needs revisiting. |
| Adjustment range | 40 to 50%. |

### Monitoring calendar for the card

| Date | Event | Expected action |
|---|---|---|
| Late September | Agents 02 to 05 deliver PIT-passing series with section-4 scorecards | Any series labelled PREDICTIVE for nights or revenue adjusts Q1, Q3 and Q6 by at most its out-of-sample lift. |
| Late October | BKNG and EXPE Q3 prints | Update Q1 and Q3 via the update protocol: which assumption moves, does it clear the 2 to 3 point noise floor. |
| 28 to 31 October | Fetch consensus revenue, EBITDA, nights, GBV, Q4 revenue for ABNB; record timestamp and source | Populate the anchor rows. If the card's numbers sit within 10 points of consensus-implied probabilities, say so. |
| 4 November, after close | Options-implied move for 6 November | Populate Q7's anchor; finalise all eight probabilities; freeze the card as `research/notes/predictive/01_card_2026Q3_frozen.md`. |
| 5 November, after close | Print | RESOLVE mode: attach outcomes to the frozen card; do not edit the forecast. Score each question with the log score and note which of the four error stages was wrong. |
| 6 November, close | Reaction | Resolve Q6 and Q7. |

---

## 6. Open items

1. Point-in-time consensus and the options-implied move are the two anchors the card lacks. Theo's `ABNB-ISSUE-CONSENSUS-BLOOMBERG` is still open; whoever has terminal access should pull a snapshot per print for revenue, EBITDA, nights and GBV and store only the derived aggregates, per CONTRIBUTING.md.
2. The hand-entered 2020 nights and Q4 2020 EBITDA should be replaced with letter-sourced values and the source IDs added to `research/sources/README.md` by whoever owns that file.
3. The nights-acceleration reaction finding (section 3.3) is the one result in this note that agent 04 should try to break: leave-one-out, 2022Q2-on, and against the raw ABNB return rather than the excess.
4. The FY-floor and guide-direction buckets are confounded with fiscal quarter. Any use of them should be within-quarter (Q3 prints only) or should include a quarter dummy.
