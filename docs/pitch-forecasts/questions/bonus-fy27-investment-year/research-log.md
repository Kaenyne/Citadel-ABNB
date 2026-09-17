# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A17 with B11 and B13). Companion: F03 `fy27-margin-guide` (this question is a re-cut of F03's option (d) under this question's own resolution text; the overlap is reconciled in §5–6). Reproduction: [datasets/b12_model.py](datasets/b12_model.py) (numpy only, seed 20260917, 400,000 draws, ~5 s; extends F03's `f03_model.py` with the two resolution readings; writes `b12_sensitivity.csv`). Letters read verbatim: 4Q21, 4Q22, 4Q23, 4Q24, 4Q25 (extract in [datasets/feb_fy_margin_sentences.csv](datasets/feb_fy_margin_sentences.csv)).

## 0. Metadata
- question_name: bonus-fy27-investment-year
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B12)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
At the Feb print, will management guide FY27 adjusted EBITDA margin down year over year versus FY26 actual, or explicitly frame 2027 as an investment year with margin below FY26?
### Resolution Criteria
Yes if the FY27 margin floor/point is below the FY26 reported margin, or the letter/call says margin will be down/lower in 2027. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry beyond the resolution sentence.)

Conventions adopted (stated here; the question is not changed): (1) **literal reading, which governs**: "floor/point below the FY26 reported margin" is read as written — any numeric FY27 floor ("at least X%") or point strictly below the FY26 adjusted EBITDA margin as the 4Q26 letter prints it (one decimal) resolves Yes, whatever the size of the gap; so "at least 35.5%" against a 35.7% print is Yes. (2) A qualitative flat sentence ("stable", "maintain", "in line", the Feb 2022/2023/2026 forms) has no floor/point below the print and no down/lower language → No. (3) Expansion language → No. (4) Explicit "down"/"lower"/"decline" for FY27, or an investment-year framing that says margin will be below FY26, → Yes with or without a number (the option text). (5) A range resolves on its midpoint; no FY27 margin sentence → No. (6) Letter governs; the call fills a silent letter. **Alternative "material" reading**, reported throughout as the sensitivity the memo may prefer: Yes only if the floor/point is ≥ 50bp below the print (the FY24/FY25 haircut form) or the down/investment-year language is explicit — because a 10–40bp gap between "at least 35.5%" and a 35.7% print is rounding, not a guide-down, and F03's implied B12 (0.35) was computed on a reading of that kind.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Every February letter since 4Q21 carried a full-year margin sentence (5 of 5), verbatim from the letters: **FY22** (4Q21 letter) "Assuming some ADR pressure due to mix shift, we would expect Adjusted EBITDA margin to be directionally in-line with 2021 as sales and marketing expense as a percent of revenue is expected to remain relatively flat and incremental variable cost improvements and fixed cost discipline is potentially offset by lower ADR" (prior actual 26.6 → delivered 34.6); **FY23** "For the full year 2023, we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022, as we offset the headwinds from lower ADR with incremental variable cost efficiencies and fixed cost discipline" (34.6 → 36.8); **FY24** "We remain committed to maintaining financial discipline and delivering strong profitability. We also believe we have meaningful growth opportunities ahead. For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year" (prior 36.84, floor 184bp below; 36.4); **FY25** "For the full year 2025, we intend to continue to deliver improving economics and strong FCF generation of our core business, while investing in growth opportunities. Specifically, we plan to invest $200 million to $250 million towards launching and scaling new businesses to be introduced later this year. Inclusive of these investments, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%—maintaining our strong track record of profitability without compromising our growth initiatives" (prior 36.40, 190bp below; 35.1); **FY26** "For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year as we reinvest top-line efficiencies to support growth across the business, primarily in marketing, product, and technology" (prior 35.10, 0). The words "down", "lower" or "decline" have never been used for a full-year margin; the FY25 sentence is the closest to an "investment year" framing and it paired a named investment with a floor below the print and the word "maintaining" | `data/raw/letters/4Q21_d251410dex991.htm`, `4Q22_d451233dex991.htm`, `4Q23_d646462dex991.htm`, `4Q24_d915198dex991.htm`, `4Q25_d58192dex991.htm` (Outlook sections, regex extract); [datasets/feb_fy_margin_sentences.csv](datasets/feb_fy_margin_sentences.csv) | 2022-02-15 to 2026-02-12 | 2026-09-17 | yes |
| 2 | Under this question's literal reading the five Februaries resolve: FY22 No (directional in-line), FY23 No (maintain), FY24 **Yes** (35 < 36.84), FY25 **Yes** (34.5 < 36.40), FY26 No (stable): 2 of 5; the last three 2 of 3. Under the material reading the same 2 of 5 (both haircuts were ≥ 184bp). Management described the FY24 floor as "the modest guide down in terms of, a modest amount of margin compression this year" (Mertz, Bernstein 30 May 2024) and "pulling back a bit on the margins ... to invest in short, medium, and long-term levers for growth" (Goldman 10 Sep 2024) — the haircut form is an investment-year framing in management's own words, even when the letter says "maintain" | claim 1; `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` V007, V011, V004 | 2024-05-30 / 2024-09-10 | 2026-09-17 | yes |
| 3 | The February floor is not mechanical: M3's February rule (prior actual minus the mean past haircut) has MAE 0.82pp, "blown by the two regime breaks (Feb 2024 no haircut history, Feb 2026 'stable' instead of a haircut)"; WS05: "February 2027 FY27 floor: FY26 actual minus 0–190bp (n 3: −184, −190, 0)"; H12: "The FY27 guide will be a floor at or slightly below the FY26 print, not a step down: four years of 35–37% and every floor beaten (60–140bp). A step-change in AI opex is the one stated risk to that" | `docs/margin-build/notes/M3_guide_policy_margin.md`; `docs/margin-build/notes/05_mgmt_statements_v2.md` §"For the 5 Nov card", pattern table; `05_fy27_hints.csv` H12 | 2026-09-14 | 2026-09-17 | yes |
| 4 | FY26 print distribution (F03 claim 12, reused unchanged): A ~ N(35.85, 0.55) with an 85% floor defence (A ≥ 35.5 + |N(0, 0.12)|) and a 15% miss branch N(35.4, 0.4) → mean 35.88, P(A < 35.5) 0.09, 35.5–35.9 0.57, 36.0–36.4 0.24, ≥ 36.5 0.10. Inputs: team margin build 35.73% / line build 35.7%, Street 35.62% (LSEG n 44, 11 Sep), floor "at least 35.5%", November point beaten by +10 / +90 / +77bp (n 3), no FY floor ever missed | `../fy27-margin-guide/research-log.md` claims 4, 12; `docs/margin-build/SYNTHESIS.md` §3; `data/processed/margin_build/23_final_model/23_vs_consensus.csv` | 2026-09-17 | 2026-09-17 | yes |
| 5 | F03 sentence regimes (reused unchanged): T1 numeric floor with a 100–200bp haircut 0.20; T2 numeric floor at the print rounded down to 0.5 (0–25bp haircut) 0.22; T3 qualitative flat 0.30; T4 expand 0.08; T5 explicit down / investment year 0.10; T6 none 0.10 → F03 vector a 0.08 / b 0.17 / c 0.27 / d 0.38 / e 0.10; F03's log implied P(B12) ≈ 0.35 "P(d) less the part of (d) that is a floor below 35.5 with an FY26 print also below 35.5" — a reading under which a T2 floor a few bp below the print does not count | `../fy27-margin-guide/research-log.md` §5–6; `../fy27-margin-guide/forecasts/2026-09-17-forecast.json` (`p_b12_implied` 0.35) | 2026-09-17 | 2026-09-17 | yes |
| 6 | Team FY27 margin views vs the Street: run 34.64% ($5,483M; bear 32.15 / bull 36.53), line build 35.7% ($5,644M), short case 31.9%; Street FY27 36.45% ($5,766M, n 44, sd $154M); FY27 incremental margin 24.7% (run) / 34.8% (line build) vs the Street's 43.7%; FY27 line-build cost lines: S&M $3,720M (+21%), cost of revenue $2,591M; "the company has given no FY27 margin guidance" | `docs/margin-build/SYNTHESIS.md` §3 (quarterly table 1Q27–4Q27: margins 19.5 / 34.0 / 48.3 / 27.9); `notes/40_line_build.md`; `23_vs_consensus.csv` | 2026-09-15 | 2026-09-17 | yes |
| 7 | What management is describing for FY27 (WS05 hints): AI/hosting ramp in 2H26 so FY27 carries a full year (H02; purchase obligations ~$465M/yr in 2027–28 vs $219M in 2026, H03); S&M +30% in 1H26 with $258M of emerging-market and partnership marketing, "FY27 S&M growth above revenue growth is the base case" (H08); "major announcements next year" (Chesky, Goldman 8 Sep 2026, V023) → launch cost before revenue, FY25's launch cost $200–250M (H07); ops per booking still falling (H05); "Net: management is describing a flat-to-slightly-up FY27 margin held by the floor policy, with the mix of cost inflation moving from marketing to hosting/AI". Mertz 6 Aug 2026: "I'm not going to give you a specific guide for 2027 and beyond, but I think looking at our track record, you can even see a couple of things" (S179); "there's a relative floor in our ability to continue to invest against that" (S164). Chesky 8 Sep: "We basically have remained pretty steady, 35% margins" (V017); "It's really actually hard to invest a lot of money in this business" (V018). No "elevated marketing" sentence exists in the Goldman 2026 transcript rows (V017–V026) or the G commentary file; the marketing ramp is a 10-Q fact (H08), not a conference remark | `05_fy27_hints.csv` H02, H03, H05, H07, H08, H12; `05_statements.csv` S164, S179, V017, V018, V023; `docs/margin-build/notes/05_mgmt_statements_v2.md` bottom line 1; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` (2026-09-08 rows) | 2026-08-06 to 2026-09-14 | 2026-09-17 | yes |
| 8 | F04 (this run): P(FY27 S&M ex-SBC ≥ 21.9% of revenue) 0.55 (CI 0.40–0.68); conditional on F03's (d) 0.70; FY27 S&M growth centred +14.5% ± 5.5 (revenue +10.9); Street-implied FY27 S&M share ~20.5%. The S&M ramp is the cost line that makes a floor below the FY26 print the natural sentence; F04's conditional says the ramp and the investment-year sentence go together | `../fy27-sm-share-above-219/forecasts/2026-09-17-forecast.json` | 2026-09-17 | 2026-09-17 | yes |
| 9 | Reaction context (not used in the number): both haircut Februaries were read differently by the market — 4Q23 print (floor 184bp below) day-1 −1.7%; 4Q24 (190bp below, with the $200–250M investment named) +14.4%, Wedbush/Oppenheimer reading "at least 34.5%" as 100–150bp above buyside fears; February Q4 prints up 6 of 6 | `data/processed/abnb_earnings_reactions.csv`; F03 log claim 10 | 2026-09-17 | 2026-09-17 | no |
| 10 | No market prices this item (Kalshi KXABNB/KXABNBA are nights ladders; Polymarket has weekly/September price ladders only; fetched 2026-09-17T08:27:05Z) | [sources/polymarket_search_airbnb_20260917T082705Z.json](sources/polymarket_search_airbnb_20260917T082705Z.json); B13's Kalshi snapshots | 2026-09-17 | 2026-09-17 | no |
| 11 | Monte Carlo (this log): literal reading P(Yes) **0.517** (T1 0.199 + T2-below-print 0.217 + T5 0.100; T2 counts in 0.217 of 0.220 because the rounded-down floor sits below the one-decimal print unless the print lands exactly on a 0.5 grid); material reading (≥ 50bp) **0.388** (T1 0.199 + T2 with gap ≥ 50bp 0.089 + T5 0.100); "T2 as flat" reading 0.299; gap between print and floor given a literal Yes: mean 1.04pp, p10 0.2, p50 0.7, p90 2.1; share of literal Yes with a gap < 50bp 0.25; P(Yes) is flat across FY26-print buckets (0.52 in every bucket — the regime, not the level, decides) | [datasets/b12_sensitivity.csv](datasets/b12_sensitivity.csv) (base row); script stdout | 2026-09-17 | 2026-09-17 | yes |
| 12 | Web (17 Sep, 1 WebSearch): no analyst note on an FY27 margin guide or a 2027 "investment year"; search returned Argus's FY27 EPS raise to $5.90, a Yahoo/Barchart piece on weakening margins from marketing and R&D, and the FY25 $200–250M investment language; the batch's neutral 72-hour check found nothing on 2027 guidance | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 14–15 Sep margin-build notes and the 17 Sep F03/F04/C04 logs; 2–3 days old against a 147-day window. The 5 Nov FY26 sentence and any 2027 investment language are the next real inputs.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs F03 (log, JSON, `f03_model.py`), F04 (JSON), F01, R16, S02, S01 (JSON)
2. [repo] Outlook sections of the 4Q21, 4Q22, 4Q23, 4Q24, 4Q25 letters (regex extract of every "Adjusted EBITDA margin ... [year/in-line/stable/maintain/at least]" sentence and every "invest(ment|ing) year" phrase — none of the latter exists)
3. [repo] `docs/margin-build/SYNTHESIS.md` §3; `docs/margin-build/notes/05_mgmt_statements_v2.md` (full); `data/processed/margin_build/05_mgmt_statements_v2/05_fy27_hints.csv` (all 16), `05_statements.csv` (V001–V026, grep "elevated": no hit)
4. [repo] `data/processed/q3nowcast/G/intra_quarter_commentary.csv` (rows dated 2026-09-08 to 09-11); `research/notes/q3nowcast/G_external-sources-q3-read.md` (grep marketing / announcement / 2027)
5. [Polymarket API] public-search "airbnb" (2026-09-17T08:27:05Z, saved); [Kalshi API] KXABNB, KXABNBA (B13 folder)
6. [computed] `datasets/b12_model.py` (base + 13 sensitivities)
7. WebSearch: Airbnb 2027 margin investment year outlook analysts
8. WebSearch: Airbnb news this week (batch final 72-hour neutral recency check, charged to B11 — nothing on 2027 guidance; no change)

WebSearch calls charged to B12: 1 (query 7). Batch total 4 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, 4Q26 shareholder letter, "at least 35%", "at least 34.5%", "stable year-over-year", sales and marketing, AI spend, 2027 launches, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| A numeric floor 100–200bp below the FY26 print with a named investment (the Feb 2024/2025 form) | leading component (T1 0.20) | 2 of the last 3 Februaries; the FY27 cost profile (full-year AI/hosting, S&M above revenue, launches before revenue, claim 7) is the Feb 2025 set-up; but Feb 2026 broke the form with "stable" and the FY26 floor was raised twice mid-year |
| A numeric floor at the print rounded down ("at least 35.5%" on a 35.7 print) | kept (T2 0.22); resolves Yes literally, No materially | the natural sentence when the print is 35.5–36.0 and management wants a numeric floor without a visible cut; this regime is the whole difference between the two readings (0.52 vs 0.39) |
| Explicit "down"/"lower"/"investment year" language | kept (T5 0.10) | never used for a full year (claim 1); the 2027 launches and the AI ramp are the mechanism; management's own gloss on the FY24 haircut ("modest guide down") shows they say it on calls, not in letters |
| Qualitative flat ("stable"/"maintain") → No | leading No regime (T3 0.30) | 3 of 5 Februaries; Chesky's "pretty steady, 35% margins" and Mertz's "relative floor" are the flat narrative |
| The Street's FY27 36.45% is management's number (expand) | kept as T4 0.08 | never guided a February expansion; the "relative floor" language makes it a live minority |
| Re-weight F03's regimes for B12 | not done | coherence with F03 matters more than a second opinion on the same five sentences; the regime weights are attacked in §7 instead |
| Treat any floor below the print as a guide-down (literal reading) vs ≥ 50bp (material) | both priced; literal governs | the resolution text says "below"; the memo's use ("investment year", "stock falls more") is closer to the material reading, so both numbers are given and the impact table mixes over the gap size |

## 5. Independent Estimates
- base_rate_estimate: 0.45 — reference class "February FY margin sentence" (claim 2): numeric floor below the print 2 of 5 (0.40; Laplace 0.43), 2 of the last 3 (0.67); explicit down 0 of 5; taken at 0.45, between the all-sample rate and the recent-regime rate, because Feb 2026's "stable" is the most recent observation and it is the No form
- decomposition_estimate: 0.52 literal / 0.39 material — the regime × FY26-print Monte Carlo (claim 11)
- anchor_estimate: 0.65 — no market; the designated anchor is the repo's registered prior (WS05, 14 Sep: "February 2027 FY27 floor: FY26 actual minus 0–190bp (n 3: −184, −190, 0)"; H12: "a floor at or slightly below the FY26 print"), which under the literal reading resolves Yes in 2 of its 3 observations and in every "slightly below" case: P ≈ 0.65 (material reading: 2 of 3 → 0.6)
- anchor_value: 0.65 (repo prior WS05/H12, 2026-09-14, literal reading)
- final_estimate: **0.50** literal (credible interval 0.38–0.62); **0.38** under the material reading (0.27–0.50)
- final_minus_anchor: −0.15 (literal). Independently derived: the anchor assumes a numeric floor every February (n 3, no qualitative sentence in its sample) — the base rate weights the qualitative-flat form by its 3-of-5 frequency and the decomposition adds the expand and none regimes; the three estimates (0.45 / 0.52 / 0.65) agree in direction and disagree only on how often February brings a number at all; the final is the decomposition trimmed 2 points toward the base rate. **Reconciliation with F03**: F03's option (d) is 0.38 and its implied B12 is 0.35; this log's material reading (0.39) matches (d) almost exactly because both count the haircut floors and the explicit down/investment framing; the literal reading (0.50) is higher only because a T2 floor a few tenths below the print — F03's option (c) territory — resolves this question's text as written. If the memo wants "investment year" in the FY24/FY25 sense, quote 0.38; if it wants "guided below the print", quote 0.50

## 6. Final Numbers
**Binary.** P(Yes) = **0.50** (credible interval 0.38–0.62) under the literal reading that governs (§0b); **0.38** (0.27–0.50) under the material reading (floor ≥ 50bp below the print or explicit down/investment-year language).
Composition of the literal 0.52 (model): haircut floor (T1) 0.20; floor at the print rounded down and sitting below it (T2) 0.22; explicit down / investment year (T5) 0.10. Gap between the print and the floor given Yes: median 0.7pp, mean 1.0pp, p10 0.2 / p90 2.1; a quarter of the literal Yes cases have a gap under 50bp.
Conditional on the 5 Nov FY26 sentence (C04): the number is flat across FY26-print levels (0.52 in every bucket) because the regime, not the level, decides; it moves only through the regime weights (an explicit 2027 investment sentence on 5 Nov: T5 0.10 → 0.20, literal 0.57 / material 0.46).
Coherence: F03 (d) 0.38 ≈ material 0.39; F04 P(S&M ≥ 21.9% | Yes) ≈ 0.65 (between F03's (c) 0.52 and (d) 0.70 conditionals, weighted by the T2/T1 mix).
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/b12_model.py` (`b12_sensitivity.csv`); base literal 0.517 / material 0.388.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Regime weights T1 0.20 / T2 0.22 / T3 0.30 | haircut dominant (T1 0.40, T3 0.15): 0.72 / 0.60; flat dominant (T3 0.45, T1 0.10): 0.40 / 0.27; numeric floors 0.55 (T1 0.28, T2 0.27), flat 0.20: 0.65 / 0.49 |
| Explicit down / investment year 0.10 | 0.25: 0.63 / 0.52; 0.04 (never said for a full year): 0.50 / 0.36 |
| Expansion language 0.08 | 0.20 (bull): 0.45 / 0.32 |
| FY26 print centred 35.85 | 35.6: 0.52 / 0.40; 36.1: 0.52 / 0.38; 36.4: 0.52 / 0.38 (level-insensitive) |
| Floor defence 0.85 | 0.50: 0.52 / 0.38 |
| T2 haircut 0–25bp | 0–50bp (floor rounded down from a wider band): 0.52 / 0.44 |
| Material threshold 50bp | 100bp: material 0.30 (= T1 + T5) |
| Reading: literal | material: 0.39; T2-as-flat (F03's implied reading): 0.30 |

Pre-mortem ("it is 11 Feb 2027 and the letter said 'stable year-over-year' or 'at least 36%' on a 35.9 print", the No side, 0.50): (1) management repeated Feb 2026's form because the FY26 floor was raised twice and the "relative floor" narrative (S164, V017) is the one they want the Street to hear — the modal single No regime (T3 0.30); (2) the print came in ≥ 36.0 on a Q4 beat and the floor was set at the print (T2 with the print on the grid) or above (T4); (3) no FY27 margin sentence at all — Mertz's August refusal repeated with a long-term framework (T6 0.10). ("The letter said 'at least 34.5%' with a $300M launch budget", the Yes side): the Feb 2025 form on the 2027 launch programme (V023) — T1. Asymmetry: the memo's short case leans on an "investment year"; at 0.50 literal / 0.38 material it is a coin flip on the text and a modal-but-minority outcome on the substance, and the memo should say which it means.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | quote 0.50 (literal) with 0.38 (material) alongside; say which reading the "investment year" line uses |
| 2026-11-05 | 3Q26 letter and call: FY26 sentence (C04), any 2027 investment or launch-cost language, B03 marketing sentence | explicit 2027 investment sentence: T5 0.10 → 0.20 (literal 0.57 / material 0.46); "approximately 36%" FY26: no change (level-insensitive); a B03 marketing-moderation sentence: T4 0.08 → 0.15, T1 −0.05 (literal −0.05) |
| 2026-11-05 to 2026-12-15 | Sell-side FY27 margin revisions (LSEG mean, sd) | Street FY27 < 36.0: T1/T5 +0.05 jointly (+0.04); > 36.8: T4 +0.05 (−0.03) |
| 2027-01-15 to 2027-02-05 | 2027 product announcements (V023), any pre-announced launch budget; call date | a named 2027 launch programme with a dollar figure: T1/T5 +0.10 jointly (literal +0.08 / material +0.09) |
| ~2027-02-11 | 4Q26 letter: FY26 print, FY27 margin sentence | resolve per §0b on the letter's one-decimal FY26 margin and the FY27 floor/point; record the gap for the impact table; hand the sentence to F03/F04 |

## 9. Impact
If Yes: the FY27 floor sits below the FY26 print by a gap with median 0.7pp / mean 1.0pp (literal Yes), or ≥ 0.5pp (mean ≈ 1.4pp) under the material reading. Deltas versus the memo's base case (line build FY27 35.7%, Street 36.45%); the operating delta is against the team's own numbers, the stock delta comes through the Street's FY27 EBITDA, which the team's sensitivity (Street sits 60–140bp above every February floor) says falls toward floor + ~1pp:

| Item | Delta if B12 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | no operating content in the sentence |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 | — |
| FY27 revenue ($M) | 0 (the sentence reallocates cost; revenue effects of the spend are inside F01/F02) | — |
| FY26 adj. EBITDA margin (pp) | 0 (known at the print) | — |
| FY27 adj. EBITDA margin (pp) | **−0.3 vs the team's line build** (E[floor | Yes] ≈ 35.9 − 1.0 = 34.9; realised = floor + 60–140bp ≈ 35.5–36.3, centre 35.9 → the line build's 35.7 is roughly what a Yes delivers; the run's 34.6 is a step below); **−0.9 vs the Street** (36.45 → ≈ 35.5) | claims 3, 4, 6, 11 |
| FY27 EPS ($) | **−0.20** on the Street number (0.9pp × ~$15.8bn revenue ≈ $140M EBITDA × $0.0014); −0.07 on the team's line build | brief sensitivities |
| Stock ($/share) | **−$5** mean over the gap size: a Street FY27 EBITDA cut of ~2.5% at a constant multiple ≈ −$4.2 (2.5% × $167.5) plus a multiple effect from the "investment year" framing (−0.3 turn ≈ −$3) in the ≥ 1pp cases and ≈ −$2 in the < 50bp cases (a rounding floor, read as flat); by size: gap < 0.5pp −$2, 0.5–1.5pp −$5, > 1.5pp or explicit down −$9. Note the Feb 2025 precedent: a 190bp haircut with a named investment was read as a relief (+14.4% day-1) because it beat buyside fears — the sign of the day-1 reaction is not the sign of the estimate cut | claim 9; `research/notes/overnight/12_valuation-multiple-regime.md` (one turn ≈ $9–10/share) |
| **EV = P × impact** | literal: **0.50 × −$5 = −$2.5/share**; material: 0.38 × −$7 = −$2.7/share | |
| Materiality | **Material** (≥ $1/share) under either reading; the memo should carry it as "the February FY27 sentence is a coin flip to sit below the FY26 print, and roughly 4 in 10 to be a visible haircut of the FY24/FY25 kind" | |

RESUME: the next agent (audit response) should re-run `datasets/b12_model.py` (deterministic, ~5 s), verify claim 1 against the five letters (the CSV extract is in `datasets/`), and attack (1) the resolution reading — the audit can move the headline to the material 0.38 if it judges a sub-50bp rounding floor is not "guided down" in the question's sense; (2) the regime weights carried from F03 (haircut 0.20 vs flat 0.30 spans 0.40–0.72 literal); (3) the impact's Street-cut assumption (−0.9pp) and the −$5 mean. Keep the FY26-print distribution and regime weights identical to F03's revision 2 if that log changes them.
