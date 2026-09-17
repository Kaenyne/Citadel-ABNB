# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A14). Companion questions: B01 `bonus-moderation-language`, B02 `bonus-adr-residual-reverts`. Reused as inputs (read-only): C04 `fy26-margin-sentence` (the hold-and-cut branch), C09 `q4-margin-direction-sentence` (P(Q4 margin sentence "up") 0.40), R05 `risk-q3-margin-sandbagged` (the S&M arithmetic), the margin build (`docs/margin-build/notes/05_mgmt_statements_v2.md`, `40_line_build.md`), the overnight language study. Datasets: `datasets/b03_marketing_statement_by_print.csv` (23 prints 4Q20–2Q26, every forward marketing statement in the letter or call, classified), `datasets/b03_sm_history.csv` (S&M line 3Q24–2Q26). No model script: the decomposition is a four-path union computed in §5 by hand from stated inputs (every number is in this log).

## 0. Metadata
- question_name: bonus-marketing-cut-signalled
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B03)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
At the 5 Nov print, will management state that 4Q26 or FY27 marketing/S&M spend will grow more slowly than revenue, be "moderated", "optimised" or reduced, or quantify a reduction?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on any such statement about S&M or marketing in the letter or call. Resolution 5 Nov 2026.
### Fine Print
(none beyond the registry header conventions.)

Conventions adopted (stated here, not changing the question): (1) the object is a *forward* statement about the marketing or S&M line for 4Q26, FY27 or "next year", in the letter, the prepared remarks or the Q&A; (2) it resolves Yes if it says the line will grow more slowly than revenue (incl. "leverage on marketing", "marketing as a percent of revenue will decline"), will be moderated, optimised or reduced as a level or a growth rate, or gives a number for a reduction; (3) a statement that Q4 margin will rise "due to timing of marketing spend" or "as marketing spend normalises after Q3" resolves Yes only if it says or implies that 4Q26 marketing grows more slowly than revenue or is lower than planned — a bare "timing of investments" with no line named is No; (4) generic descriptors of *how* they spend ("efficient marketing spend", "ROI-driven", "we review channels monthly") applied to a budget that is growing are No; "flat as a percent of revenue" is No (in line, not slower); a core-markets-only leverage statement with total marketing growing faster than revenue (the 4Q24 form) is No; (5) a seasonal sequential decline (Q4 below Q3 in dollars) is No unless framed as a cut or slower-than-revenue growth; (6) if the print date moves, the same event on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Statement ledger, 23 prints 4Q20–2Q26 (letter + call): a forward statement that marketing/S&M would grow more slowly than revenue or be reduced appears in **4 of 23** — 4Q20, 1Q21, 2Q21 ("S&M as a percentage of revenue in the second half of 2021 will be lower than that of the first half"; FY21 below 2019) and 1Q23 (Stephenson on the call: "for the full year, total marketing costs will be roughly the same as they were in the prior year", against +18% revenue; the letter said "flat as a percent of revenue"). **Since 1Q22: 1 of 18; since 1Q24: 0 of 10; November prints: 0 of 5.** Borderline Nos: 3Q22 (dollars flat for the *current* year), 4Q23 (Stephenson: "we probably could see additional leverage on marketing, but ... we're actually expanding to 20 countries"). Every 2024–26 forward marketing statement is up or flat: 2Q24 and 1Q25 letters "Marketing expense is expected to grow faster than revenue"; 3Q24 letter "Q4 2024 Adjusted EBITDA Margin is expected to decline ... due to higher marketing and product development expenses"; 4Q24 "$200 million to $250 million" new-business investment; 4Q25 letter "reinvest top-line efficiencies ... primarily in marketing, product, and technology"; 1Q26 "efficient marketing spend" (on a budget growing +33%); 2Q26 "some incremental investment", margin "partially offset by continued investment in sales and marketing" | `datasets/b03_marketing_statement_by_print.csv`; `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` (sm_* rows); `data/raw/letters/*.htm`, `data/raw/transcripts/web/*.html` (regex extract "marketing", "efficien", "optimi", "disciplin") | 2021-02-25 to 2026-08-06 | 2026-09-17 | yes |
| 2 | Guidance ledger `sm_pct_rev_yoy_bps` (7 rows) and `sm_growth_minus_rev_growth_pts` (2): the only "lower" statements are the 2021 seasonal ones (4Q20, 1Q21, 2Q21, not scoreable); 4Q21/1Q22 "relatively flat" FY22 (beat: −175bp); 4Q22 "+150bp in Q1 2023, flat for the full year" (Q1 miss +190, FY beat −27); 1Q23 "+400bp in Q2 2023" (beat, +160); 2Q24 and 1Q25 "grow faster than revenue" (met, +17.7 and +7.9pts). Tell 5: "The guides that actually miss are the expense and monetisation lines"; the FY24 "marketing % of revenue largely the same" missed by 150bp | `data/processed/overnight/02_guidance_ledger.csv` rows 6, 15, 34, 41, 62, 66, 72, 112, 141; `02_guidance_tells.csv` row 5; `research/notes/overnight/03_management-language-and-stock.md` §4 ("Marketing as a percent of revenue ... 19.3% → 21.1% → 25.9% in 1H26") | 2026-09-07 / 2026-09-06 | 2026-09-17 | yes |
| 3 | S&M line: 3Q25 $639M (15.6% of revenue, +24.3% y/y vs revenue +9.7%); 4Q25 $695M (25.0%, +27.1% vs +12.0%); 1Q26 $751M (28.0%, +33.4% vs +17.9%); 2Q26 $875M (24.3%, +26.6% vs +16.5%); FY25 S&M 19.4% of revenue; 10-Q: 1Q26 "+$126 million increase in marketing activities driven by paid growth initiatives in emerging markets and partnerships", 2Q26 "+$132 million ... higher paid growth marketing initiatives in emerging markets and partnerships" — eight consecutive quarters of S&M growing faster than revenue | `datasets/b03_sm_history.csv` (from `data/processed/abnb_quarterly_costlines.csv`); `05_statements.csv` F1Q26_sm_total, F2Q26_sm_total | 2026-08-06 | 2026-09-17 | yes |
| 4 | WS05 (14 Sep): "Sales & marketing is the line with no discipline in the record: +27-30% y/y in 1H26 ..., 'major announcements next year' (V023) mean launch cost before revenue again in FY27, brand statements 68% kept (n 41)"; reliability by line: sm_field 80% kept (n 15), sm_brand 68% (n 41); Chesky at Goldman (8 Sep 2026): "We're going to have some major announcements next year" (V023), "Nearly 90% of our traffic is direct or organic" (S371), "It's really actually hard to invest a lot of money in this business" (V018). The line build reads the Goldman remarks as "marketing stays elevated into next year's launches" and models FY27 marketing +15% (S&M 21.9% of revenue) after FY26 +28% | `docs/margin-build/notes/05_mgmt_statements_v2.md` bottom line 1, reliability table; `05_statements.csv` V018, V023, S371; `docs/margin-build/notes/40_line_build.md` line table | 2026-09-14 / 2026-09-15 / 2026-09-08 | 2026-09-17 | yes |
| 5 | Line build (15 Sep): the 3Q26 "down slightly" sentence needs ~$97M more Q3 cost than the evidence supports, 70% booked as a marketing timing step; "the Q3 marketing step does not recur in Q4 because carrying it into Q4 would put FY26 below the 35.5% floor at guide revenue, which management has never missed"; short case: FY26 34.2% at budget, 35.5% with a **$177M 4Q26 marketing cut (~35% of Q4 marketing)**; "the 5 Nov sequence this implies: ... either an FY sentence held at 'at least 35.5%' with a visible marketing cut or the floor at risk"; FY27 sensitivity: marketing growth +5pts → −0.67pp of FY27 margin, −$0.15 EPS | `docs/margin-build/notes/40_line_build.md` reconciliation, short case, sensitivities; `data/processed/margin_build/40_line_build/40_short_case_summary.csv`, `40_sensitivities.csv` | 2026-09-15 | 2026-09-17 | yes |
| 6 | C04 (this run): FY26 margin sentence (a) held "at least 35.5%" 0.26 (the hold-and-cut branch: "management ... holds the cut lever, so 'hold and cut' beats 'soften' when the floor is at risk"), (b) "approximately 36%" 0.42, (d) softer 0.24; floor break-even: a 2H26 revenue shortfall of 0.63% ($50M) with costs held; the 2Q26 call: Mertz "I'm not going to give you a specific guide for 2027 and beyond"; "there's a relative floor in our ability to continue to invest" | `../fy26-margin-sentence/research-log.md` §4–6, claims 10, 16 | 2026-09-17 | 2026-09-17 | yes |
| 7 | C09 (this run): 4Q26 margin sentence (a) down 0.28, (b) flat 0.27, **(c) up 0.40**, (d) none 0.05; conditional on the C01 guide midpoint below the Street: c 0.32; the 3Q24 form ("decline due to higher marketing and product development") is the named-line precedent; WS05: the 2026 sentences dropped the line names ("timing of investments") | `../q4-margin-direction-sentence/research-log.md` §5–6 | 2026-09-17 | 2026-09-17 | yes |
| 8 | R05: a 51.5% 3Q26 print needs S&M ≤ $706M (+20.7% y/y) vs the budget's $778–781M (+33.5%); $48M of S&M = 1.0pp of 3Q26 margin; the sentence has not been sandbagged (above it in 4 of 10 quarters) | `../risk-q3-margin-sandbagged/research-log.md` claims 6–7 | 2026-09-17 | 2026-09-17 | no |
| 9 | Language study §4: marketing claims 7 of 8 kept (the miss is the FY24 "% of revenue largely the same"); "marketing" theme share of management sentences 2Q26 0.4% (record low; prepared 1.4%, Q&A 0.0%), 1Q26 1.6%, 4Q25 0.8%: the topic has almost left the call; declined-to-quantify instances rising (four in 2Q26) | `research/notes/overnight/03_management-language-and-stock.md` §1, §4; `data/processed/overnight/03_call_features.csv` (theme_marketing_share_*) | 2026-09-06 | 2026-09-17 | yes |
| 10 | Historical form of a Yes at a November print: none in 5 Novembers; the closest analogues are 4Q23's "could see additional leverage" (negated in the same answer, Feb 2024) and 1Q23's "total marketing costs roughly the same as the prior year" (May 2023, a year in which S&M % of revenue fell 27bp); the 2023 pattern was a front-loaded campaign followed by a 2H that grew slower than revenue (3Q23 S&M +5% y/y, 10-Q), which management described in advance | claim 1 dataset; `05_statements.csv` rows 109, 118, 147, 161 | 2023-05-09 to 2024-02-13 | 2026-09-17 | yes |
| 11 | Web (search snippets, pages not fetched, zero weight): Marketing Week coverage of the brand-over-performance shift (Chesky: "pretty consistent marketing spend as a percent of revenue over time"); no sell-side or press item on 2027 marketing plans; no Polymarket or Kalshi market on the guide's cost language (scans 2026-09-17T08:03:45Z) | https://www.marketingweek.com/airbnb-brand-strength-marketing-spend-consistent/ ; `sources/polymarket_search_Airbnb_20260917T080345Z.json`; `sources/kalshi_markets_KXABNB_open_20260917T080345Z.json` | 2026-09-17 | 2026-09-17 | no |
| 12 | Sensitivities for the impact table: $48M of S&M = 1.0pp of 3Q26 margin; a $177M 4Q26 cut = +1.24pp of FY26 margin ($14,268M revenue); FY27 marketing growth −10pts (15 → 5) = +1.34pp of FY27 margin, +$0.30 EPS (claim 5); the reaction function carries no cost term; the 3Q24 print (spend up, margin down) fell −8.8% excess; the M6 asymmetry k_down < k_up (discretionary lines have not responded to revenue within a year) | `docs/pitch-forecasts/00_BRIEF.md`; `40_sensitivities.csv`; `research/notes/reverse_dcf/C_reaction-function.md`; `docs/margin-build/notes/M6_cycle_flex.md` (via C04 claim 10) | 2026-09-16 / 2026-09-15 | 2026-09-17 | yes (impact only) |
| 13 | Final 72-hour check (query 10): ABNB −7.4% w/w to $170.65 (15 Sep), Housing Accelerator, ratings; nothing on spending plans | WebSearch (see §2) | 2026-09-15 | 2026-09-17 | no |

Newest load-bearing sources: C04/C09 (17 Sep, same day), the line build (15 Sep) and WS05 (14 Sep) with the 8 Sep Goldman remarks (9 days against a 49-day window; the only management datum since 6 Aug). The last-72h pass found nothing newer that bears on the number.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; C04, C09, R05, R01, C02, R07 logs and JSONs (read-only)
2. [repo] `docs/margin-build/notes/05_mgmt_statements_v2.md` (all); `docs/margin-build/notes/40_line_build.md` (all)
3. [repo, pandas] `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` — every row with line sm_* or "marketing" in the verbatim (96 rows)
4. [repo, python] regex sentence extract from `data/raw/letters/*.htm` and `data/raw/transcripts/web/*.html` for marketing / efficien / optimi / disciplin (letters ~180 sentences, transcripts 542); forward-looking rows read by hand for every print → `datasets/b03_marketing_statement_by_print.csv`
5. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` sm_pct_rev_yoy_bps and sm_growth_minus_rev_growth_pts rows; `02_guidance_tells.csv`; `data/processed/abnb_quarterly_costlines.csv` (S&M 3Q24–2Q26) → `datasets/b03_sm_history.csv`
6. [repo] `data/processed/q3nowcast/G/intra_quarter_commentary.csv` (Goldman 8 Sep rows); `data/processed/overnight/03_call_features.csv` (theme_marketing_*); `research/notes/overnight/03_management-language-and-stock.md` §4
7. [Polymarket public-search] Airbnb; [Kalshi API] KXABNB open (2026-09-17T08:03:45Z, saved)
8. WebSearch: Airbnb news (neutral, shared)
9. WebSearch: Airbnb sales and marketing expense 2027 leverage analysts Chesky Mertz marketing spend next year launches — Marketing Week brand-vs-performance coverage; nothing on 2027 plans
10. WebSearch: Airbnb ABNB this week (final 72-hour neutral recency check, shared) — nothing that changes the number

WebSearch calls charged to this question: 2 (query 9 and a share of the shared queries); batch total 5 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, sales and marketing, "timing of investments", "at least 35.5%", 4Q26 margin sentence, 2027 launches, "major announcements next year", Goldman Communacopia

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Path A: the letter or prepared remarks guide 4Q26 margin up y/y and attribute it to marketing spend growing more slowly / normalising after the Q3 step | leading Yes path, 0.12 | C09 P(up) 0.40 (claim 7) × P(marketing named as the reason and framed as slower/lower) 0.30: the 2026 letters dropped line names ("timing of investments", claims 7, 1) but the 3Q24 letter named marketing for a decline and the Q3 step is management's own flagged timing item (claim 5) |
| Path B: a Q&A answer on 2027 says marketing will grow slower than revenue / show leverage | kept, 0.08 | Mertz declines 2027 guides (claim 6); the one "leverage" remark in the record (4Q23) was negated in the same breath (claim 10); "major announcements next year" points to launch marketing (claim 4) |
| Path C: the FY26 floor is held by a visible Q4 marketing cut *and* management says so ("we have moderated Q4 marketing") | kept, 0.05 (inside the C04 hold branch 0.26 × P(stated) ~0.2) | the line build's short case (claim 5) makes the cut the mechanism, but the 2024–25 precedent when margins were squeezed was to name *higher* marketing, not a cut; a cut would more likely be shown, not said |
| Path D: a generic "efficient/optimised marketing" phrase that a resolver counts | kept as resolver risk, 0.04 | convention 4 excludes it; the phrase appears in most calls (1Q26 letter), so the residual is the chance the memo's resolver reads it loosely |
| Management states marketing will grow *faster* than revenue again (2Q24/1Q25 form) or "reinvest efficiencies in marketing" (4Q25 form) | the modal No path (~0.5) | eight quarters of S&M > revenue growth (claim 3), the 2027 launch narrative (claim 4), sm_brand statements 68% kept |
| "Flat as a percent of revenue" for FY27 | No under convention 4 (in line, not slower); ~0.15 of the mass | the 2022–23 form (claims 1–2); a February statement more than a November one (FY+1 was qualitative in all five Novembers, WS05) |
| The 3Q26 margin prints ≥ 51.5% (R05, 0.17) and the Q3 step "slipped into Q4" → Q4 marketing *up* | lowers Path A | R05's slip component is 25%; on that branch the Q4 sentence names higher marketing (C09 §7 last row) |

## 5. Independent Estimates
- base_rate_estimate: 0.09 — reference class "a forward slower-than-revenue / reduction statement about marketing in the letter or call": 4 of 23 prints (0.17) but 1 of 18 since 1Q22 (0.06, Laplace 2/20 = 0.10) and 0 of 10 since 1Q24 (Laplace 1/12 = 0.08); 0 of 5 Novembers; regime-conditioned up from 0.08 for the tight FY26 floor (break-even $50–75M, claim 6) and the Q3 timing step that must not recur (claim 5), down for the 2027 launch narrative (claim 4) → 0.09
- decomposition_estimate: 0.26 — union of the four paths in §4 treated as independent given the print state: 1 − (1 − 0.12)(1 − 0.08)(1 − 0.05)(1 − 0.04) = 0.26; Path A is 0.40 × 0.30 (C09 up × marketing named as slower); the paths share the "floor at risk / Q4 guide below Street" state (C01 0.80), so the union overstates by a few points → 0.22–0.26
- anchor_estimate: 0.20 — no external market (claim 11); the designated internal anchor is the line build's own 5 Nov sequence read through C04: the hold-and-cut branch (a) 0.26 with a visible cut, plus the (b) 0.42 branch's implied Q4 margin of ~31% (which needs the Q3 step not to recur, i.e. Q4 marketing flat-to-down y/y in growth terms) × a 0.25 chance the letter says so → 0.26 × 0.5 + 0.42 × 0.25 ≈ 0.24, shaded to 0.20 for the 2026 habit of not naming lines
- anchor_value: 0.20 (repo prior: line build short case + C04/C09 branches, 2026-09-15/17; dependent construction, not a price)
- final_estimate: 0.18 (credible interval 0.10–0.30)
- final_minus_anchor: −2 points. NOT_INDEPENDENTLY_DERIVED flag: raised by the arithmetic and answered: the anchor and the decomposition are both built on C04/C09 and the line build, so their agreement is common-mechanism; the base rate (0.09) is the independent leg and it is the reason the final sits below both — management has not made such a statement in ten prints, has spent two years saying the opposite, and the 2026 letters stopped naming cost lines at all. The final lands two-thirds of the way from the base rate to the decomposition because the print state (floor tight, Q4 guide likely below Street, a Q3 step management itself labelled timing) is genuinely unlike the 2024–25 prints in the base-rate window
- overlap statement: a Yes here is most likely inside C09 (c) "up" and C01 Yes; X01 should not add it to the base case

## 6. Final Numbers
**Binary.** P(management states at the 5 Nov print that 4Q26 or FY27 marketing/S&M will grow more slowly than revenue, be moderated/optimised/reduced, or quantifies a reduction) = **0.18**, credible interval **0.10–0.30**.
Path split of the 0.18: Q4-margin-up attributed to slower marketing (letter/prepared remarks) ≈ 0.09; 2027 leverage statement (Q&A) ≈ 0.05; stated Q4 cut to hold the floor ≈ 0.02; resolver-loose reading of "efficient" ≈ 0.02. Conditional on C09 = (c) "up": ≈ 0.30; on C09 = (a) "down": ≈ 0.07. Conditional on C04 = (a) hold: ≈ 0.25; on (b) "approximately 36%": ≈ 0.20; on (d) softer: ≈ 0.10.
Strict reading (conventions 3–5 applied hard, Path D at 0): 0.15. Loose reading (any "efficient/optimise marketing" phrase counts): 0.45.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| P(marketing named as the slower line \| Q4 sentence "up") 0.30 | 0.15 (2026 no-line-names habit holds): 0.13; 0.50 (3Q24 naming form returns): 0.25 |
| C09 P(up) 0.40 | 0.25 (guide at C01 p10): 0.14; 0.55 (M3 path): 0.22 |
| P(2027 leverage remark in Q&A) 0.08 | 0.03: 0.14; 0.15: 0.24 |
| Resolver reads "efficient marketing spend" as Yes (convention 4 off) | 0.45 |
| Base-rate window: since 1Q24 (0/10) vs all 23 (4/23) | base rate 0.08 → final 0.16; 0.17 → final 0.21 |
| 3Q26 margin prints ≥ 51.5% (R05 Yes: the Q3 step slipped into Q4) | 0.10 (Q4 sentence names higher marketing) |
| Management pre-announces a 2027 launch slate before 5 Nov | 0.12 (launch marketing framed as investment) |

Pre-mortem ("it is 5 Nov and management said marketing would be moderated / grow slower"): (1) the FY26 sentence was held at "at least 35.5%" with a weak Q4 guide, and Mertz explained the implied Q4 margin expansion by "moderating our marketing spend in Q4 after the Q3 campaigns" — Path A/C, the memo's own short-case sequence, priced at 0.11 jointly; (2) an analyst asked about 2027 margins and Mertz said "we'd expect to see leverage in sales and marketing next year as the emerging-market campaigns mature" — Path B at 0.08; the 4Q24 core-markets construction shows she has the vocabulary; (3) the letter said "efficient marketing" and the team's resolver counted it — convention 4 exists to stop this, but the residual is real. ("It is 5 Nov and nothing of the kind was said, 0.18 was too high"): the modal outcome; the 2027-launch narrative and "reinvest efficiencies in marketing" repeated. Asymmetry: for the short memo a Yes is a tell (the floor is being defended with the growth budget), not a stock line; the cost of over-stating it is a memo bullet that does not land, the cost of under-stating it is missing the one sentence that would confirm the short case's mechanism on the day.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-02 | Any Airbnb conference appearance or 8-K (none scheduled; CFO absent since 6 Aug) | A Mertz remark on 2H26 marketing "front-loaded into Q3" → 0.25; on 2027 launch spend → 0.12 |
| 2026-10-02 | Prelim memo due | Quote 0.18 (0.10–0.30) as a tell inside the short case, not as a stock line; state the strict/loose readings (0.15 / 0.45) |
| 2026-10-20 to 2026-10-30 | LSEG 4Q26 margin consensus refresh; BKNG/EXPE Q3 prints (marketing intensity read-across) | Street 4Q26 margin ≥ 29.5% (Q4 "up" more likely) → +0.02; a peer marketing pull-back framed as efficiency → +0.02 |
| 2026-11-05 (after close) | 3Q26 letter, prepared remarks, Q&A (~16:05–17:30 ET); 10-Q S&M line | Resolve by conventions 1–5; record the sentence; note whether the 3Q26 S&M print landed at the budget ($778–781M) — a print ≤ $710M means the Q3 step never came and the Q4 sentence will name higher marketing (→ No more likely) |
| 2027-02-11 (est.) | 4Q26 letter (FY27 guide) | Out of scope for B03 (5 Nov only); F03/F04 carry the FY27 marketing question |

## 9. Impact
If the event happens (management signals 4Q26/FY27 marketing growth below revenue growth or a reduction), the direct cost-side deltas are taken at the line build's short-case cut ($177M of 4Q26 marketing, ~35% of Q4 marketing) and a FY27 marketing growth of +5% instead of +15%; the demand-side delta is a judgement (the repo has no marketing-to-nights elasticity; M6 found discretionary lines do not respond to revenue within a year, and the reverse is unmodelled):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a forward statement; the reported quarter is unaffected |
| 4Q26 nights (pts) | **−0.3** | judgement: a Q4 marketing cut of ~35% removes emerging-market paid growth (the 1H26 driver, claim 3); no repo elasticity, so this is the smallest non-zero value the mechanism supports |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | **−9** | −0.3pt × $30M |
| FY27 revenue ($M) | **−50** | ≈ −0.3pt of FY27 growth × $158M (paid-growth markets are the marginal nights) |
| FY26 adj. EBITDA margin (pp) | **+1.2** direct (the $177M cut on $14,268M revenue, claim 12); **≈ −0.2 vs the memo base case** (the signal arrives with the short-case revenue path: 35.5% held vs the base 35.7%) | `40_short_case_summary.csv`; claim 5 |
| FY27 adj. EBITDA margin (pp) | **+1.3** direct (marketing +5% instead of +15%: +1.34pp, claim 12) less ≈ −0.2 from the revenue line → **+1.1** | `40_sensitivities.csv` |
| FY27 EPS ($) | **+0.27** (+$0.30 from the marketing line, −$0.03 from revenue × 0.66 × $0.0014) | claim 12 |
| Stock ($/share) | **−3** (range −8 to +5) | the reaction function has no cost term and keys on nights and the guide; a signalled cut is read with the weak Q4 guide it accompanies as growth capitulation (the 3Q24 analogue: spend *up* cost −8.8%; a spend *down* framed as efficiency has no precedent on this name); EPS +$0.27 at ~27x is +$7 on the level, the growth read −0.3pt × 0.44 turns × $9.5 ≈ −$1.3 plus a sentiment term; net set at −$3 with the sign uncertain |
| **EV = P × stock** | **0.18 × −$3 ≈ −$0.5/share** | **Immaterial** as a stock line (< $1/share); the memo should carry it as the *tell* that the FY26 floor is being defended with the growth budget (the line build's 5 Nov sequence), with the margin arithmetic (+1.2pp FY26 / +1.1pp FY27 if it happens) as the reply to "the floor is safe" |

RESUME: the next agent (audit response) should attack (1) Path A's 0.30 (marketing named as the slower line given a Q4 "up" sentence) — the 2026 letters have not named a cost line, and a resolver could go either way on "timing of marketing"; (2) convention 4 (generic "efficient" excluded), which is worth 0.15 vs 0.45; (3) the base-rate classification of 1Q23 and 3Q22/4Q23 (borderlines) in `datasets/b03_marketing_statement_by_print.csv`; (4) the −$3 stock sign, which is a judgement. No script to re-run; every number in §5 is a stated product. If Mertz appears anywhere before 5 Nov, read the transcript for 2H26 marketing phasing first.
