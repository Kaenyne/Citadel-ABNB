# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A10). Companion questions in the batch: R05 `risk-q3-margin-sandbagged`, R07 `risk-adr-residual-persists`. Related finished logs reused as inputs: C11 `q3-take-rate-above-1810` (management's take-rate language record), C01 (fee step in the 4Q26 guide model).

## 0. Metadata
- question_name: risk-single-fee-take-rate-accretion-stated
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R04)
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
Will management state at the 5 Nov or Feb print that the single-fee migration is (or will be) accretive to take rate or revenue in 4Q26 or FY27, with a number or a direction ("higher take rate")?
### Resolution Criteria
Yes if either print's letter or call attributes a higher take rate, higher revenue per GBV, or a quantified revenue uplift to the fee migration for 4Q26 or FY27. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry beyond the header conventions: letter governs where letter and call differ; "5 Nov print" = the 3Q26 release and call on its actual date; "Feb print" = the 4Q26 release and call, ~11 Feb 2027.)

Conventions adopted for ambiguities (stated, not changing the question): (1) the attribution must name the fee migration ("single service fee", "simplified fee structure", "single fee", "host-only fee", "fee migration") in the same print, either in the accretion sentence itself or as an enumerated member of the "monetization initiatives" the sentence credits (the 1Q26 letter form); a bare "monetization initiatives" with the fee unnamed anywhere in that print resolves No; (2) a gross or conditional attribution counts ("absent incentives, take rate would be higher, driven by the single fee") because the question asks whether accretion is *stated*, not whether the net printed take rate rises; a statement that the fee is offset to flat still resolves Yes if the fee's own contribution is described as positive; (3) "4Q26 or FY27" includes any period inside FY27 (1Q27 guidance at the Feb print counts) and the FY26 full-year sentence given at the 5 Nov print counts only if it explicitly covers Q4; (4) the call counts whether or not the letter is silent, because the resolution text says "letter or call" (the header's letter-governs rule applies only to contradictions, and an attribution cannot be contradicted by silence); (5) a statement about revenue "per GBV" or "implied take rate" are the same object; a statement about host pricing competitiveness, guest conversion or nights (the 2Q26 "helped hosts price more competitively" form) does not count; (6) if either print date moves, the same event on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 1Q26 letter (7 May 2026), verbatim: "The upward revision to our revenue outlook reflects meaningful progress across our growth initiatives and improvements to monetization through a simplified fee structure and our insurance programs, which are expected to lift our full-year take rate." Call (Mertz): "you should see modest upside to our take rate from both the migration to the single fee structure as well as our Insurance Program"; "you should see a slightly higher implied take rate in the back half of the year". This is an explicit, direction-stated attribution of take-rate accretion to the fee migration, i.e. the exact form the question asks about, given once already for FY26 | `data/raw/letters/1Q26_d23351dex991.htm`; `data/raw/transcripts/web/1Q26.html` | 2026-05-07 | 2026-09-17 | yes |
| 2 | 2Q26 letter (6 Aug 2026): "We expect our implied take rate to remain relatively in-line year-over-year" (Q3); call (Mertz): "For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026. Absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year, driven by our monetization initiatives and execution across our product roadmap." Same call, on the fee: "the single service fee ... in aggregate, has a kind of downward pressure on pricing"; "We anticipate by year-end, our entire supply base will be on that single service fee"; "Approximately half of our active listings are now subject to the single service fee." The 2Q26 print therefore reversed the 1Q26 net guidance to flat while keeping a conditional gross attribution to monetization (fee unnamed in that sentence, named elsewhere in the call) | `data/raw/letters/2Q26_d70413dex991.htm`; `data/raw/transcripts/web/2Q26.html`; `data/processed/overnight2/D/rnpl_statement_ledger.csv` D047, D049, D050 | 2026-08-06 | 2026-09-17 | yes |
| 3 | Take-rate forward sentences and the driver named, 4Q22–2Q26 letters (13 prints): a driver is named in 9 of 13; a positive monetization driver (cross-currency fee 4Q23/2Q24/1Q25, FX service fee quantified "+20 basis points" on the 4Q24 call, fee migration + insurance 1Q26) in 5 of 13; the fee migration specifically in 1 (1Q26) plus the 2Q26 conditional. Since the migration began (four prints 3Q25–2Q26): 3Q25 No (Q4 "relatively flat", Q3 decline attributed to FX and timing), 4Q25 No (Q1 "up slightly ... mostly due to some timing consideration"), 1Q26 Yes, 2Q26 marginal Yes under convention (2) | `datasets/r04_driver_attribution_history.csv`, `datasets/r04_statement_record.csv` (extracted this run from `data/raw/letters/*.htm` and `data/raw/transcripts/web/*.html`); `data/processed/overnight/02_guidance_ledger.csv` metric take_rate_yoy_pts | 2023-02-14 to 2026-08-06 | 2026-09-17 | yes |
| 4 | 4Q24 call (13 Feb 2025), Mertz, verbatim: "We introduced an FX service fee mid-2024. That service fee is approximately 100 basis points applied to 20% of our GBV. On an annualized basis, you would assume that it would lift the implied take rate by about 20 basis points ... for full year 2025, you should assume that the implied take rate gets the full benefit of 20 basis points increase on a year-over-year basis." Precedent for a quantified, forward, driver-attributed take-rate accretion statement at a February print | `data/raw/transcripts/web/4Q24.html` | 2025-02-13 | 2026-09-17 | yes |
| 5 | Fee mechanics: single fee 15.50% of the host price vs split 14.99% of the guest total, so the migrated cohort's take rate on guest spend rises ~+51–58bp mechanically regardless of host repricing (θ); migrated-cohort revenue +1.1% to +1.8% (θ 0.83), +4.05% only at the θ = 1 upper bound; on the printed quarterly take rate the effect is small (~+7bp at a 40% migrated revenue share) because revenue lags GBV and the seasonal conversion dominates; no fee effect detectable in printed take rates through 2Q26 (n 20, permutation p 0.73). Host-only note §3: "worth ~+3–4% revenue at the central case (ε −1, full pass-through), i.e. roughly +50–60 bp of take rate — consistent with the CFO saying take rate would be 'slightly higher' in 2026 absent new-business incentives" | `docs/revenue-forecast-strategy/05_backtests/fee-takerate.md` §1, §3; `research/notes/host_only_fee_history_and_elasticity.md` §3–4 | 2026-09-11 / 2026-09-06 | 2026-09-17 | yes |
| 6 | Migrated share path (listing-weighted → GBV-weighted → kernel revenue-quarter share, central): 3Q26 0.394, 4Q26 0.625, 1Q27 0.873, 2Q27+ 0.98; the y/y migrated nights share is +46pp in 3Q26, +75pp in 4Q26, +71pp in 1Q27, +66pp in 2Q27, +41pp in 3Q27, zero in 4Q27 — the mechanical take-rate effect of the migration is at its largest in 4Q26–1H27, exactly the periods the question covers; tranche-2 deadlines 15 Sep (non-EEA) and 13 Oct (EEA/CH) sourced to Airbnb's Resource Center article 771 ("The deadline to adjust your prices is September 15 if you live outside the European Economic Area and October 13 if you live within it or in Switzerland") | `fee-takerate.md` §2; `research/notes/adrv3/K_residual-decomposition-fee-migration.md` §1 point 5; `docs/revenue-forecast-strategy/05_backtests/A3_fee_panels.md` §1.1 (https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-on-airbnb-771) | 2026-09-11 / 2026-07-07 | 2026-09-17 | yes |
| 7 | 4Q25 printed take rate 13.62% vs 14.09% in 4Q24 (−47bp, "primarily due to FX and the timing of when guests booked their travel and when guests stayed"); 3Q25 17.88 vs 18.57 (−69bp, same attribution). The 4Q26 y/y comparison is therefore against a depressed base, which raises the chance the 5 Nov letter's Q4 take-rate sentence reads "up"; management's habit is to name the driver of any stated direction (claim 3) | `data/raw/letters/4Q25_d58192dex991.htm`, `3Q25_d40503dex991.htm`; `data/processed/abnb_driver_history_quarterly.csv` take_rate_calc_pct | 2026-02-12 | 2026-09-17 | yes |
| 8 | Fee-churn evidence: "a plausible risk to monitor, but the current evidence does not establish a significant fee-driven bearish catalyst"; the January 2026 disappearance spike did not validate a permanent exit (65–90% of missing IDs reappeared by July); the broader Sep/Oct 2026 deadlines were still ahead at the note date. Bearing on R04: no host-attrition datum that would make management avoid the subject; the host-facing framing ("price more competitively") remains available as the alternative to a take-rate framing | `research/notes/2026-09-07_fee-churn-catalyst.md`; `2026-09-07_fee-churn-recent-followup.md` | 2026-09-07 | 2026-09-17 | no |
| 9 | Chesky, 2Q26 call (ledger D053): "On pricing, I think this is one of the biggest single levers for growth that we have. I think it's significantly greater than Reserve Now, Pay Later ... many multiples bigger than RNPL." Management frames the fee/pricing roadmap as a growth (nights, conversion) lever, not primarily a take-rate lever; the 2Q26 call describes the single fee as "downward pressure on pricing" for guests. This is the main mechanism for a No: the accretion is real but management chooses the host/guest framing | `data/processed/overnight2/D/rnpl_statement_ledger.csv` D053, D047; `data/raw/transcripts/web/2Q26.html` | 2026-08-06 | 2026-09-17 | yes |
| 10 | Analysts asked about take rate / the fee on the last three calls (4Q25: "could you just talk about the take rate dynamics in Q1"; 1Q26: "I guess you talked about expanding take rate ... Is it just small enough that it doesn't affect your take rate trajectory?"; 2Q26: fee-migration question answered with the "downward pressure on pricing" framing) and on 9 of the 22 quarterly calls since 1Q21; with the migration completing in 4Q26 a take-rate/fee question on 5 Nov or in February is close to certain, so the call route dominates the letter route | `data/raw/transcripts/web/4Q25.html`, `1Q26.html`, `2Q26.html` (grep "take rate", "service fee", "single fee") | 2026-02-12 to 2026-08-06 | 2026-09-17 | yes |
| 11 | B17 (bonus-take-rate-guided-down) is the mirror question; the two are not exclusive (management can say the fee is accretive and that incentives/RNPL timing take the net lower). C11 log: management's guided take-rate direction has been met or undershot in 5 of 6 pairs; "in-line" for 3Q26 centres 17.9% | `docs/pitch-forecasts/questions/q3-take-rate-above-1810/research-log.md` claim 4 | 2026-09-17 | 2026-09-17 | no |
| 12 | C01 model carries the 4Q26 fee step at 45/40/15 over 0 / +0.55% / +1.11% of 4Q26 revenue (half step +$17M, full +$35M on $3,178M); bridge v3 4Q26 revenue $3,178M; team FY27 revenue $15,829M (line build), FY27 GBV ≈ $114bn (FY26 GBV ≈ $105bn on the card: 29.2 + 27.2 + 25.9 + 23.1, grown ~8%) | `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json`; `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv`; `docs/margin-build/notes/40_line_build.md` | 2026-09-17 / 2026-09-15 | 2026-09-17 | yes (impact only) |
| 13 | No Polymarket or Kalshi market exists on management statements, take rate or fees (Kalshi KXABNB/KXABNBA are nights ladders; Polymarket has price-hit ladders and a closed Q2 GBV ladder), fetched 2026-09-17T03:34:27Z | `sources/kalshi_markets_KXABNB_open_20260917T033427Z.json`; `sources/polymarket_search_airbnb_20260917T033427Z.json` | 2026-09-17 | 2026-09-17 | no |
| 14 | Web pass (3 WebSearch calls attributable to this question, all shared or specific): host-facing fee explainers only; no sell-side or press item on the 2027 take-rate effect; no management remark since 8 Sep (Goldman) on take rate | `sources/web_queries_2026-09-17.md` | 2026-09-17 | 2026-09-17 | no |
| 15 | Decomposition arithmetic (this log): letter route at 5 Nov = P(4Q26 take-rate sentence reads up) 0.45 × P(fee named as the driver | up) 0.50 = 0.225; call route = P(take-rate/fee question asked) 0.70 × P(answer states a positive fee effect) 0.45 = 0.315; union with overlap ρ 0.5 → P(Yes at 5 Nov) 0.39; P(Yes in Feb | No in Nov) 0.30 → total 0.57. Per-print base rate since the migration began 1.5/4 = 0.375; two-print base 1 − 0.625² = 0.61 | `datasets/r04_decomposition.csv` | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md` (conventions, Risks preamble, R04/R05/R07), skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`; finished logs C01, C11, C04, C09, S01 (read-only)
2. [repo] `research/notes/2026-09-07_fee-churn-catalyst.md`; `research/notes/host_only_fee_history_and_elasticity.md` §1–4; `research/notes/adrv3/K_residual-decomposition-fee-migration.md` §1; `docs/revenue-forecast-strategy/05_backtests/fee-takerate.md` §0–4; `A3_fee_panels.md` §1–2
3. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` rows metric ∈ {take_rate_yoy_pts, take_rate_pct_seq} (13 + 5 rows, quotes and outcomes)
4. [repo, pandas] `data/processed/overnight2/D/rnpl_statement_ledger.csv` rows matching take rate / service fee / single fee / simplified / pricing (D013, D014, D024, D041, D047, D049, D050, D053, D060)
5. [repo, python] sentence extraction from every letter `data/raw/letters/*.htm` and every call mirror `data/raw/transcripts/web/*.html` for "take rate", "service fee", "single fee", "host-only", "simplified", "fee structure" → `datasets/r04_driver_attribution_history.csv`, `r04_statement_record.csv`
6. [Kalshi API] markets?series_ticker=KXABNB (open) — nights ladder only; [Polymarket public-search] airbnb, Airbnb Q3, Airbnb margin, Airbnb ADR — no relevant market (2026-09-17T03:34:27Z)
7. [WebSearch] Airbnb news (neutral, shared)
8. [WebSearch] Airbnb single service fee 15.5% take rate analyst revenue impact 2027 (host explainers only)
9. [python] `datasets/r04_decomposition.csv` (route arithmetic, claim 15)
10. [WebSearch] Airbnb ABNB this week (final 72-hour neutral recency check, shared, 2026-09-17: stock −7.4% w/w, Housing Accelerator, ratings; nothing on take rate) — no change

WebSearch calls used by this question: 3 of 5 (two shared).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, single service fee, simplified fee structure, implied take rate, 3Q26 shareholder letter, 4Q26 shareholder letter, monetization initiatives, customer incentives, Reserve Now Pay Later

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Management repeats the 1Q26 form at 5 Nov or in February: fee migration named as lifting the take rate for 4Q26/1Q27/FY27 | leading (~0.45 of the Yes mass via the letter, more via the call) | claims 1, 6, 7: the mechanical effect peaks in 4Q26–1H27, the 4Q25 comp is depressed by −47bp, and management names a driver for every stated take-rate direction (9 of 13) |
| Management keeps the 2Q26 "relatively flat, absent incentives slightly higher, driven by monetization initiatives" form without naming the fee | kept as the main No path (~0.30) | claim 2; under convention (1) this resolves No unless the fee is named in the same print, and the fee was named on the 2Q26 call (so that print would have been a marginal Yes); repeating that exact pattern is a coin toss on the naming |
| Management frames the fee only as pricing competitiveness / guest conversion / nights (the D053 and D047 framing) and declines to attribute take rate | kept as the second No path (~0.25) | claim 9; this is the CEO's preferred framing and the host-relations reason to avoid "we take more" language |
| A quantified FY27 take-rate figure at the Feb print (the 4Q24 "+20bp" form) | inside Yes (~0.10 of total) | claim 4 precedent; the fee's ~+50bp gross is larger than the FX fee's +20bp, but management has never quantified the fee's effect |
| B17-style "take rate down" guidance for 4Q26/FY27 without any positive fee attribution | kept (~0.20) | RNPL timing and new-business incentives are the named offsets (D050); a "down" sentence usually names only the negative drivers (3Q24, 3Q25 forms) |
| No take-rate sentence at all in either print | tail (~0.03) | 13 of 13 letters since 4Q22 carried one |
| The migration is delayed past year-end so nothing is said | discarded | Airbnb-primary deadlines 15 Sep / 13 Oct (claim 6); even a delay leaves the FY27 statement route open |

## 5. Independent Estimates
- base_rate_estimate: 0.61 — per-print rate of a qualifying attribution since the migration began, 1.5 of 4 prints (1Q26 explicit; 2Q26 conditional counted at half; 3Q25 and 4Q25 No) = 0.375, compounded over the two prints in the window: 1 − 0.625² = 0.61; the wider class (a positive monetization driver named for the take rate, 5 of 13 letters since 4Q22) gives 0.385 per print → 0.62 over two prints
- decomposition_estimate: 0.57 — claim 15: 5 Nov letter route 0.225 + call route 0.315 with overlap → 0.39; Feb conditional 0.30 → 0.57
- anchor_estimate: 0.50 — no market or consensus prices the statement (claim 13); the anchor is the skill's pending-decision flat prior for a discretionary management statement (§1a: no option above ~45–50% on positioning alone), which is the number a peer with no repo access would hold
- anchor_value: 0.50 (flat prior, no external market; Kalshi/Polymarket scans 2026-09-17T03:34:27Z)
- final_estimate: 0.58 (credible interval 0.42–0.72)
- final_minus_anchor: +8 points. NOT_INDEPENDENTLY_DERIVED flag is raised by the arithmetic and answered here: the number is not a haircut off the anchor; the base rate (0.61) and the decomposition (0.57) are built from the letters and calls and happen to land 7–11 points above a flat prior. Pending-decision caution keeps the final below the two-print base rate; the two estimates agree within 4 points, so no missing consideration is indicated.

## 6. Final Numbers
**Binary.** P(management states, at the 5 Nov or Feb print, that the single-fee migration is or will be accretive to take rate or revenue in 4Q26 or FY27) = **0.58**, credible interval **0.42–0.72**.
Split: P(Yes at the 5 Nov print) ≈ 0.39; P(Yes first at the Feb print) ≈ 0.19. Route split of the Yes mass: call Q&A ≈ 0.55, letter outlook sentence ≈ 0.35, prepared remarks ≈ 0.10. P(a quantified figure, not just a direction) ≈ 0.10.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention (2): a conditional/gross attribution ("absent incentives ... driven by the single fee") counts | net-only reading (fee must be credited with a higher *printed* take rate): 0.42 |
| Convention (1): "monetization initiatives" counts only if the fee is named in the same print | any "monetization initiatives" language counts: 0.68; the fee must be named in the accretion sentence itself: 0.48 |
| P(4Q26 take-rate sentence reads up) 0.45 | 0.30 (RNPL timing repeats the 4Q25 −47bp): 0.53; 0.60 (easy comp dominates): 0.62 |
| P(call answer names a positive fee effect | asked) 0.45 | 0.30 (pricing-competitiveness framing holds): 0.50; 0.60 (1Q26 form): 0.65 |
| Feb conditional 0.30 | 0.15: 0.48; 0.45: 0.66 |
| Per-print base rate 0.375 (2Q26 counted at half) | 2Q26 counted as No (0.25): base 0.44, final 0.52; 2Q26 counted as full Yes (0.50): base 0.75, final 0.63 |

Pre-mortem ("it is 12 Feb 2027 and this resolved No"): (1) management kept the 2Q26 framing exactly — "relatively flat" net, offsets named, the fee credited only with host pricing competitiveness — through both prints (the leading No path, priced at ~0.30); (2) the 4Q26 take rate printed down y/y again on RNPL timing and the take-rate paragraph named only FX and timing, and analysts asked about RNPL cancellations instead of the fee (priced through the 0.45/0.70 inputs); (3) the fee became a host-relations issue (attrition, press) after the 15 Sep/13 Oct deadlines and management avoided any "we take more" language (partly priced, claim 8); (4) a resolver reads "driven by our monetization initiatives" as not naming the fee (convention (1) sensitivity, −0.10). "It resolved Yes and the memo was hurt": the most likely form is a call answer of the 1Q26 kind ("modest upside from the single fee, offset by incentives"), which is a gross statement the short can absorb; the damaging form is a quantified FY27 figure (~0.10).

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-15 / 2026-10-13 | Non-EEA and EEA/CH price-adjustment deadlines; any Airbnb Resource Center or press statement on completion | Completion confirmed → hold; a delay past year-end → −0.05 (the 4Q26 statement route weakens, the FY27 route stays) |
| 2026-09-17 to 2026-11-04 | Host-forum / press coverage of the migration (attrition, backlash); any management conference remark on take rate or fees | A public host backlash → −0.05 (pricing framing more likely); a management remark of the 1Q26 kind at a conference → +0.10 |
| 2026-10-02 | Prelim memo due | Quote 0.58 (0.42–0.72); state that the 1Q26 letter already made this statement for FY26 and 2Q26 walked it to flat |
| 2026-11-05 (after close) | 3Q26 letter Outlook take-rate sentence; call Q&A | Letter names the fee as lifting Q4/FY take rate → resolve Yes; letter "relatively flat/in-line" with no fee mention → read the call transcript for a fee attribution; if none, move to 0.30 (Feb route only) |
| 2026-11-06 to 2027-02-10 | 10-Q MD&A revenue discussion (a "monetization" or fee reference to revenue per GBV); sell-side FY27 take-rate notes | A 10-Q attribution does not resolve (letter/call only) but raises P(Feb statement) by +0.05 |
| ~2027-02-11 | 4Q26 letter and call: 1Q27 / FY27 take-rate sentence | Resolve; audit read: pre-print P should be ~0.30 if 5 Nov was a No |

## 9. Impact
If the event happens (a stated accretion, direction or number), the market re-marks the fee leg from the bridge's half step to a full step and adds a FY27 take-rate lift; the memo's revenue path carries the fee only as the bridge's half step (+0.55% of 4Q26 revenue) and take rate on the team path thereafter.

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a statement about take rate does not move the 3Q26 print |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | the fee reprice's ADR mechanics (+0.17pp 3Q26, +0.37pp 4Q26) are already in card v3 (K line); a take-rate statement adds no ADR information |
| 4Q26 revenue ($M) | +30 | half-step → full-step on the bridge (+0.55% × $3,178M = +$17M, claim 12) plus the market's mark-up of the 4Q26 take rate by ~+5bp on ~$23bn GBV (+$12M) |
| FY27 revenue ($M) | +230 | ~+20bp of net take rate (the FX-fee precedent's magnitude, claim 4; gross +50–60bp less incentives, claim 5) on FY27 GBV ≈ $114bn (claim 12) ≈ +1.5pt of FY27 revenue growth |
| FY26 adj. EBITDA margin (pp) | +0.1 | +$30M of 4Q26 revenue at ~90% flow-through on $14,268M |
| FY27 adj. EBITDA margin (pp) | +1.3 | +$230M × 0.9 = +$205M of EBITDA on $15,829M (take-rate revenue carries almost no cost, host-only note §4) |
| FY27 EPS ($) | +0.29 | $0.0014 per $M of EBITDA × $205M (brief sensitivities) |
| Stock ($/share) | +7 | +1.5pt of forward revenue growth × 0.40–0.48 turns × $9–10/turn ≈ +$6 (multiple) plus the FY27 EBITDA level effect (~$205M × ~16x / 620m shares ≈ +$5), haircut to +$7 because a direction-only statement (0.90 of the Yes mass) would be marked at less than the full +20bp |
| **EV = P × stock** | **0.58 × $7 ≈ +$4.1/share** | **Material** (≥ $1/share): the memo should carry this as a named risk and pre-write the reply (gross accretion is consistent with a flat net take rate, per the 2Q26 call) |

RESUME: the next agent (audit response) should re-read the six convention choices in §0b (the number is most sensitive to (1) and (2), ±0.10–0.16), check the 13-letter driver table in `datasets/r04_driver_attribution_history.csv` against the letters, and challenge the three judgement inputs in `datasets/r04_decomposition.csv` (0.45 / 0.50 / 0.45); the impact table's +20bp net take-rate mark is the one number in §9 not sourced to a repo sensitivity and should be re-derived from the fee-takerate primitives if the audit wants a range.
