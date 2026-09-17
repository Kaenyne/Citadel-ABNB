# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A16). Companion questions: B08 `bonus-ai-hosting-cost-step`, B09 `bonus-sbc-step-up`, B10 `bonus-interest-income-falls`. Finished logs reused as inputs (read-only): C11 `q3-take-rate-above-1810` (management's take-rate language record), R04 `risk-single-fee-take-rate-accretion-stated` (driver-attribution record; the mirror question), C12 `q3-unearned-fees-yoy` (RNPL timing). Reproduction: `datasets/b17_model.py` (numpy/pandas, seed 20260917, n 400,000, seconds) → `b17_results.csv`.

## 0. Metadata
- question_name: bonus-take-rate-guided-down
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B17)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-04
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
At the 5 Nov print, will management guide 4Q26 or FY27 take rate lower (any statement that take rate will be down y/y, or that incentives/new businesses will reduce it)?
### Resolution Criteria
Yes on any such forward statement. Resolution 5 Nov 2026.
### Fine Print
(none beyond the registry header conventions: letter governs where letter and call differ; "5 Nov print" = the 3Q26 release and call on its actual date.)

Conventions adopted (stated, priced in §5–7; they do not change the question): (1) the statement must be forward-looking at the 5 Nov print and its period must include 4Q26 or any part of FY27; an FY26 statement made on 5 Nov qualifies because its only unreported content is 4Q26; a statement about 3Q26 (realised) does not; (2) leg (a): the statement says the implied take rate will be "lower", "down", "decline" (or a synonym) year over year for that period — "relatively flat", "in-line", "stable" do not count on their own; (3) leg (b): the statement attributes a reduction of the forward take rate — relative to the prior year or to what it would otherwise be — to customer incentives, new businesses (Services, Experiences, hotels, partnerships) or the host-fee/direct-link pilot; the 2Q26 call form ("relatively flat … accounting for … higher customer incentives related to new businesses … Absent these incentives … slightly higher") counts under (b) if repeated for a qualifying period; RNPL booking-vs-stay timing named alone counts only under (a); (4) letter, prepared remarks and Q&A all count ("letter or call"); the letter-governs rule applies only to contradictions; (5) a statement that the take rate will be "roughly flat" with incentives named as an *offset to gains* counts under (b) because it states that incentives reduce the take rate; (6) if the print date moves, the same event on its actual date. The strict alternative — FY26 wording excluded, only statements naming 4Q26 or FY27 count — is reported as a sensitivity.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Letter take-rate outlook sentences, y/y form, 4Q22–2Q26 (13 prints): "similar" (1Q23), "above" (2Q23), "higher" (3Q23), "slightly higher" (4Q23), "notably higher" (1Q24), "higher" (3Q24 target), **"slightly lower on a year-over-year basis" (3Q24 letter for 4Q24; printed −22bp)**, "higher" (2Q25 target), "flat" (2Q25 letter for 3Q25; printed −69bp), "relatively flat" (3Q25 for 4Q25; printed −47bp), "up slightly" (4Q25 for 1Q26; printed −10bp), "up slightly" (1Q26 for 2Q26; printed +9bp), "relatively in-line" (2Q26 for 3Q26; pending). Direction "lower": 1 of 13; flat/similar/in-line: 4; higher: 8. Sequential-form sentences in 2021–22 ("will decrease from Q3") are seasonal and are excluded | `data/processed/overnight/02_guidance_ledger.csv` (metric take_rate_yoy_pts, 13 rows; take_rate_pct_seq, 5 rows); letters `data/raw/letters/*.htm` | 2023-02-14 to 2026-08-06 | 2026-09-17 | yes |
| 2 | 2Q26 call (6 Aug 2026), Mertz, verbatim (S165, S166): "For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026. Absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year, driven by our monetization initiatives and execution across our product roadmap." The 2Q26 letter carried only the Q3 sentence ("relatively in-line") and the realised-Q2 paragraph ("Factors impacting the Q2 2026 take rate included FX and the timing of when guests booked their travel and when guests stayed — a dynamic that reflects the growth of Reserve Now, Pay Later"). This is the first print in which incentives were named as reducing the take rate; under convention (3) a repeat of it on 5 Nov for FY26 resolves Yes | `data/raw/transcripts/web/2Q26.html`; `data/raw/letters/2Q26_d70413dex991.htm`; `05_statements.csv` S165, S166; `rnpl_statement_ledger.csv` D049 | 2026-08-06 | 2026-09-17 | yes |
| 3 | 1Q26 (7 May 2026): letter "improvements to monetization through a simplified fee structure and our insurance programs, which are expected to lift our full-year take rate"; call (Mertz) on the Delta partnership: "it is a rev share program. You shouldn't anticipate that it has a negative impact on our take rate this year … you should see modest upside to our take rate from both the migration to the single fee structure as well as our Insurance Program"; "a slightly higher implied take rate in the back half of the year". Between May and August the FY26 net guidance moved from "lift" to "relatively flat" with incentives as the named offset (claim 2) | `data/raw/letters/1Q26_d23351dex991.htm`; `data/raw/transcripts/web/1Q26.html`; `05_statements.csv` S154, S156 | 2026-05-07 | 2026-09-17 | yes |
| 4 | New-business spend: 4Q24 letter "$200 million to $250 million towards launching and scaling new businesses" (FY25), cut to "approximately $200 million towards services and experiences" (2Q25, 3Q25); 2Q25 call (Mertz): "a good portion of it is headcount … I'm not going to give a particular figure for next year, but what you should assume is that we will continue to invest in 2026 behind these businesses". Revenue is defined "net of incentives and refunds" (every letter), so customer incentives are contra-revenue and lower the printed take rate directly | `02_guidance_ledger.csv` rows 134, 144, 154, 163; `data/raw/transcripts/web/2Q25.html`; `data/raw/letters/2Q26_d70413dex991.htm` (definitions) | 2025-02-13 to 2026-08-06 | 2026-09-17 | yes |
| 5 | Direct-link host-fee pilot: Skift (29 Aug 2026) and Bloomberg (31 Aug 2026): Airbnb is piloting a host fee of "6% to 10%" (vs the standard 15.5%) on bookings arriving through a host's own direct link, "quietly piloting", "currently a limited test"; no company statement on revenue or take-rate effect, scale or timing (fetched); the repo's read: "the first explicit take-rate concession"; "Airbnb pricing its own disintermediation risk … caps the fee-migration tailwind"; a −0.8pt scaling has circulated but is unverified (paywalled) | https://skift.com/2026/08/29/airbnb-is-testing-lower-fees-for-hosts-who-bring-their-own-guests/ (WebFetch 2026-09-17); https://www.bloomberg.com/news/articles/2026-08-31/airbnb-rolls-out-pilot-program-in-us-to-lower-fees-paid-by-hosts-to-6-or-10 (snippet, not fetched); `research/blotnick_framework_abnb.md` §11; `research/notes/overnight/11_competition-supply-and-overlays.md` point 7 | 2026-08-29 / 2026-09-06 | 2026-09-17 | yes |
| 6 | 4Q26 take-rate arithmetic (4Q25 printed 13.62% = 2,778 / 20,400, down 47bp y/y "primarily due to FX and the timing of when guests booked their travel and when guests stayed"): team bridge v3 $3,178M / GBV $22,987M = 13.83% (+21bp); Street LSEG revenue $3,162M / MODL GBV $23,003M = 13.75% (+13bp); MODL take-rate mean 13.76 (13.60–14.00, n 28); team revenue on the Street-high GBV $23,565M = 13.49% (−13bp); an RNPL pull-forward adding +2% / +4% to GBV → 13.55% (−7bp) / 13.29% (−33bp). The short case scales revenue with nights and ADR and keeps the take rate on the team path. So the Q4 comp is easy (the 4Q25 base is depressed) but the timing effect that depressed it (lead times lengthening with RNPL, the July eligibility expansion) continues, and management's guided direction has been met or undershot in 5 of 6 pairs (C11 claim 4) | `datasets/b17_results.csv`; `data/processed/h2_bridge_v3/`; `40_lines_quarterly.csv` (gbv_busd 4Q26 22.99); `E_street_distribution_vs_team.csv`; `data/raw/letters/4Q25_d58192dex991.htm`; `../q3-take-rate-above-1810/research-log.md` claim 4 | 2026-09-15 / 2026-09-12 | 2026-09-17 | yes |
| 7 | R04 (this run, the mirror): P(management states fee-migration accretion to take rate/revenue at 5 Nov or Feb) 0.58 (0.42–0.72); the two questions are not exclusive (gross accretion and a net "flat/lower with incentives" can be said in one breath, as in 2Q26); R04's decomposition: P(a take-rate/fee question asked on the 5 Nov call) 0.70; 9 of 22 calls since 1Q21 carried a take-rate question, 3 of the last 3 | `../risk-single-fee-take-rate-accretion-stated/research-log.md` §5–6, claim 10 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Chesky, Goldman Communacopia (8 Sep 2026, V022): "a pretty easy straight shot to $1 billion incremental high margin revenue, based on what other brands have done" (monetisation of services/loyalty, FY27+) — the CEO's forward framing is take-rate up, not down; the CFO's is net-flat with named offsets (claim 2) | `05_statements.csv` V022 | 2026-09-08 | 2026-09-17 | yes |
| 9 | Base-rate objects: (i) a "lower" y/y sentence in 1 of 13 letters (Laplace 0.13); (ii) a qualifying statement of either leg in the new-business regime, 1 of 5 prints (2Q25 No, 3Q25 No, 4Q25 No, 1Q26 No, 2Q26 Yes; Laplace 0.29); (iii) Q3 letters with a y/y Q4 sentence, 3 (3Q23 higher, 3Q24 lower, 3Q25 relatively flat): 1 of 3 lower (Laplace 0.40); (iv) either leg across all 13 letters/calls: 2 of 13 (Laplace 0.20) | claims 1–2; `datasets/b17_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 10 | Monte Carlo (this log, `datasets/b17_model.py`, Gaussian copula ρ 0.5 across routes): route (a) letter Q4 sentence "lower" 0.12; route (b) incentives/new businesses/pilot named as reducing a qualifying period's take rate = P(take rate is a topic in prepared remarks or Q&A) 0.80 × P(the answer qualifies) 0.50 = 0.40; route (c) explicit FY27 lower 0.06; **union 0.48**; strict convention (FY26 wording excluded) 0.33; sensitivities: (a) 0.20 → 0.52, 0.06 → 0.46; topic 0.60 → 0.39; qualify 0.35 → 0.39, 0.65 → 0.58; ρ 0 → 0.50, 0.8 → 0.47; (c) 0.15 → 0.52 | computed; `datasets/b17_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 11 | No Kalshi or Polymarket market on management statements or take rate (2026-09-17T08:21:21Z) | `sources/kalshi_markets_KXABNB_open_20260917T082121Z.json`; `sources/polymarket_search_airbnb_20260917T082121Z.json` | 2026-09-17 | 2026-09-17 | no |
| 12 | Web pass (2 WebSearch calls attributable, one shared; 1 WebFetch): the pilot coverage (claim 5); nothing on 5 Nov take-rate previews; nothing in the last 72 hours | `sources/web_queries_2026-09-17.md` queries 1, 5, 6 | 2026-09-17 | 2026-09-17 | no |
| 13 | Impact inputs: 4Q26 GBV ≈ $23.0bn, FY27 GBV ≈ $114bn (R04 claim 12); 1pt of FY27 revenue growth ≈ $158M; +0.40–0.48 EV/EBITDA turns per point of forward growth, one turn ≈ $9–10/share; FY27 EPS ≈ $0.0014 per $M of EBITDA; team FY27 revenue $15,829M; take-rate revenue carries ~90% flow-through (R04 §9) | `docs/pitch-forecasts/00_BRIEF.md`; `../risk-single-fee-take-rate-accretion-stated/research-log.md` §9 | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes (impact only) |

Newest load-bearing source: the direct-link pilot coverage (29–31 Aug 2026, 17 days old against a 49-day window) and the 8 Sep Chesky remark (9 days); the mechanism sources are the 6 Aug call and letter (42 days).

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; finished logs C11, R04, C12, R05, R01, F03, F04 (read-only)
2. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` rows metric ∈ {take_rate_yoy_pts, take_rate_pct_seq, new_business_investment_usd_m} (quotes, outcomes)
3. [repo, python] letters 4Q23, 4Q24, 3Q25, 4Q25, 1Q26, 2Q26: every "take rate" paragraph (outlook and realised); call mirrors 2Q25, 3Q25, 4Q25, 1Q26, 2Q26: "take rate", "incentive", "headcount" passages
4. [repo, pandas] `05_statements.csv` rows on take rate / incentives (S131, S154, S156, S165, S166, S171, S177, V006, V022); `rnpl_statement_ledger.csv` D049 via C11/R04
5. [repo] `data/processed/h2_bridge_v3/`, `40_lines_quarterly.csv` (4Q26 revenue and GBV), `E_street_distribution_vs_team.csv` (4Q26 take-rate consensus)
6. [repo, grep] "direct link|direct-link|direct booking" across `research/` and `docs/` (blotnick framework, overnight/11 note)
7. [Kalshi API] KXABNB open; [Polymarket public-search] airbnb (2026-09-17T08:21:21Z)
8. [WebSearch] Airbnb news (neutral recency pass, shared)
9. [WebSearch] Airbnb direct booking link host service fee pilot 6% 10% take rate
10. [WebFetch] skift.com/2026/08/29/airbnb-is-testing-lower-fees-for-hosts-who-bring-their-own-guests/ (dates, fee levels, company statements)
11. [python] `datasets/b17_model.py` → `b17_results.csv`
12. [WebSearch, final 72-hour neutral recency check = query 8, 2026-09-17: nothing new on take rate, incentives or the pilot] — no change

WebSearch calls used by this question: 2 of 5 (one shared); WebFetch 1.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, implied take rate, customer incentives, new businesses, Services, Experiences, Reserve Now Pay Later, direct booking link pilot, 3Q26 shareholder letter

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The 5 Nov letter's Q4 sentence reads "relatively flat" or "up slightly" (the easy comp) and no offset is named — No | leading No path (~0.45) | claim 6: the 4Q25 base is 47bp depressed and both the team and the Street have 4Q26 up 13–21bp; management's 3Q25 form for Q4 was "relatively flat" |
| The CFO repeats the 2Q26 FY26 form on 5 Nov ("relatively flat … accounting for … incentives related to new businesses") — Yes under convention (3) | leading Yes path (route (b), 0.40) | claim 2: it is the current FY26 guidance and Q3 calls restate FY guidance; the direct-link pilot (claim 5) and the migration deadlines make a take-rate question near-certain (R04: 3 of the last 3 calls) |
| The letter guides 4Q26 take rate "lower" y/y (RNPL timing and incentives) | kept (route (a), 0.12) | claim 1: 1 of 13 letters; the Q4 comp argues against; an RNPL pull-forward of +4% of GBV would put the print at −33bp and management has undershot its own direction in 5 of 6 pairs |
| Management frames incentives as "investment in growth" without linking them to the take rate | kept inside route (b)'s 0.50 qualify probability | the 2Q26 form linked them explicitly; the 1Q26 form (Delta) said "no negative impact" — a coin toss on the wording |
| An explicit FY27 take-rate-down statement | tail (route (c), 0.06) | FY+1 take-rate statements have come only in February (the 4Q24 +20bp form); Chesky's 8 Sep framing is take-rate up (claim 8) |
| Strict convention: FY26 wording excluded | sensitivity, 0.33 | convention (1) adopted because an FY26 statement on 5 Nov is a statement about 4Q26 in substance |
| The pilot is sized and described as dilutive | inside route (b) | "currently a limited test"; no company quantification (claim 5) |

## 5. Independent Estimates
- base_rate_estimate: 0.29 — a qualifying statement of either leg in the new-business regime, 1 of 5 prints (2Q26 only), Laplace (1+1)/(5+2) = 0.29; the all-letters class gives 0.20 (2 of 13) and the Q3-letter "lower" class 0.40 (1 of 3, n too small to carry weight)
- decomposition_estimate: 0.48 — `datasets/b17_model.py` union of the letter-lower route (0.12), the incentives-named route (0.80 × 0.50 = 0.40) and the FY27 route (0.06) with ρ 0.5 (claim 10); 0.33 under the strict convention
- anchor_estimate: 0.50 — no market or consensus prices the statement (claim 11); the anchor is the skill's pending-decision flat prior for a discretionary management statement (no option above ~45–50% on positioning alone), the number a peer without the letters would hold
- anchor_value: 0.50 (flat prior; Kalshi/Polymarket scans 2026-09-17T08:21:21Z)
- final_estimate: 0.42 (credible interval 0.28–0.56)
- final_minus_anchor: −8 points. NOT_INDEPENDENTLY_DERIVED flag raised by the arithmetic and answered: the final is 0.5 × 0.48 + 0.3 × 0.29 + 0.2 × 0.50 = 0.43, rounded to 0.42; it is built from the letter record and the 2Q26 call form, not from the prior; the base rate and the decomposition disagree by 19 points because the base rate cannot see that the incentives sentence is now the standing FY26 guidance and that the pilot has put take rate on every analyst's list — the decomposition carries that and gets the larger weight.

## 6. Final Numbers
**Binary.** P(a qualifying take-rate-lower statement at the 5 Nov print) = **0.42**, credible interval **0.28–0.56**.
Route split of the Yes mass (from the model): incentives/new-business/pilot named as reducing a qualifying period's take rate ≈ 0.80; the letter's Q4 sentence reading "lower" ≈ 0.25 (overlapping); an explicit FY27 lower statement ≈ 0.12. Under the strict convention (only statements naming 4Q26 or FY27) the number is **0.33**.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention (1): FY26 statements on 5 Nov qualify | strict (4Q26/FY27 only): 0.33 |
| Convention (5): "flat, with incentives offsetting gains" counts | net-only reading (take rate must be said to fall): ~0.22 |
| P(letter Q4 sentence "lower") 0.12 | 0.06: 0.40; 0.20: 0.45 |
| P(take rate is a topic on the call) 0.80 | 0.60: 0.37 |
| P(the answer qualifies \| topic) 0.50 | 0.35: 0.37; 0.65: 0.50 |
| Route correlation ρ 0.5 | 0: 0.44; 0.8: 0.41 |
| Blend weights 0.5 / 0.3 / 0.2 (decomposition / base rate / prior) | all decomposition: 0.48; all base rate: 0.29 |

Pre-mortem ("it is 5 Nov and this resolved No"): (1) the letter said "relatively flat" for Q4 and the CFO's FY sentence dropped the incentives clause now that the take rate is tracking (the leading No path, ~0.45); (2) the take-rate question on the call was answered with the R04 form only ("modest upside from the single fee") and the pilot was called "too small to matter" without an incentives reference — inside route (b)'s 0.50; (3) a resolver reads "flat, accounting for incentives" as not a "lower" statement (convention (5), −0.20). "It resolved Yes and the memo was hurt": it cannot — this is a bonus for the short; the damaging form for the *long* is a quantified 2027 take-rate decline, which is the 0.06 route. Asymmetry: a confident Yes that resolves No would be read as the memo over-reaching on a language call; the log keeps 0.42 and the strict-convention 0.33 in front.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-02 | Press or host-forum coverage of the direct-link pilot (scale, US-wide roll-out); any management conference remark on take rate or incentives | pilot expanded nationally → +0.05; a management remark of the 2Q26 form at a conference → +0.08; a remark of the 1Q26 "no negative impact" form → −0.05 |
| 2026-10-02 | Prelim memo due | Quote 0.42 (0.28–0.56) with the strict-convention 0.33; state that the 2Q26 call already made the statement for FY26 |
| 2026-10-13 | EEA/CH single-fee deadline | no direct effect; raises the odds of a fee/take-rate question on the call (+0.02) |
| 2026-10-15 to 2026-11-03 | Sell-side previews (take-rate expectations for Q4; MODL 13.76) | previews centring Q4 take rate below 13.62 → +0.05 |
| 2026-11-05 (after close) | 3Q26 letter: Q4 take-rate sentence and any FY26/FY27 take-rate sentence; call prepared remarks and Q&A | letter "lower" → resolve Yes; letter "flat/up" → read the call for the incentives clause; none → resolve No |

## 9. Impact
If the event happens (a stated lower / incentive-reduced forward take rate), the market re-marks 4Q26 and FY27 take rate down and removes the fee-migration tailwind the bull case carries; taken at −13bp on 4Q26 (the Street's +13bp becomes flat) and −15bp on FY27 (net of the fee lift, the mirror of R04's +20bp):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a monetisation statement does not move the print |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | incentives are contra-revenue, not ADR |
| 4Q26 revenue ($M) | −30 | −13bp × $23.0bn GBV (claim 13) |
| FY27 revenue ($M) | −170 | −15bp × $114bn FY27 GBV ≈ −1.1pt of FY27 revenue growth |
| FY26 adj. EBITDA margin (pp) | −0.2 | −$30M × 0.9 flow-through on $14,268M |
| FY27 adj. EBITDA margin (pp) | −1.0 | −$170M × 0.9 = −$153M on $15,829M |
| FY27 EPS ($) | −0.21 | $0.0014 per $M × $153M |
| Stock ($/share) | −6 | −1.1pt of forward growth × 0.40–0.48 turns × $9–10 ≈ −$4.6 plus the FY27 EBITDA level effect (−$153M × ~16x / 620m ≈ −$4), haircut to −$6 because the modal form (the 2Q26 "flat, with incentives" sentence, ~0.8 of the Yes mass) would be marked at less than the full −15bp |
| **EV = P × stock** | **0.42 × −$6 ≈ −$2.5/share** | **Material** (≥ $1/share): carry as a named bonus line; pre-write the reply to R04 (gross fee accretion and a net-flat/lower take rate are the same sentence) |

RESUME: the next agent (audit response) should re-run `datasets/b17_model.py` (seconds), re-read the six conventions in §0b (the number moves 0.22–0.48 across (1) and (5); confirm with Krish whether the 2Q26 FY26 form repeated on 5 Nov is meant to count), check claim 1's 13-letter direction table against the ledger, and challenge the two judgement inputs of route (b) (topic 0.80, qualify 0.50); the impact table's −15bp FY27 mark mirrors R04's +20bp and should be re-derived from the fee-takerate primitives if a range is wanted.
