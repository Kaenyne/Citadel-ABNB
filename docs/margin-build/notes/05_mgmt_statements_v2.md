# WS05. Management statements v2 (every reachable event) and the November guide-language pattern

Margin build, 14 Sep 2026. Script `analysis/src/margin_build/05_mgmt_statements_v2/run.py` (`py -3.13`, rebuilds every CSV
from raw text, exit 0; the command is in the README next to it). Outputs in `data/processed/margin_build/05_mgmt_statements_v2/`:
`05_statements.csv` (377 rows), `05_guide_language_pattern.csv` (20 prints 3Q21-2Q26), `05_guide_language_stats.csv`,
`05_nov2026_scenarios.csv` (45 rows), `05_fy27_hints.csv` (16), `05_reliability_by_line.csv` (19 lines), `05_reliability_by_event.csv`.
Raw pulls (gitignored) under `data/raw/margin_build/05_mgmt_statements_v2/`, manifest `data/manifests/margin_build/05_mgmt_statements_v2.csv`
(28 files: 17 10-Qs, 8 8-Ks, 3 stockanalysis pages, each with URL, UTC timestamp, sha256). Free parameters: 0 fitted; judgement calls
are the verdicts, the line mapping and the 3Q26 margin assumed in the scenario table (stated there).

**Pre-registered pass line (prompt):** >= 40 new dated statements beyond 31a's 194; >= 6 from non-earnings events; every November since
2021 has its full row in the pattern file with the implied Q4 margin computed and checked against the actual.
**Result: met.** 183 new statements (75 hand-verified sentences + 108 10-Q MD&A component rows), 155 of them from 31 non-earnings
events (6 conferences, 25 filings); 5 November rows (3Q21-3Q25), all with an implied Q4 margin and its error against the actual.
Every one of the 183 new verbatims is verified by the script as an exact substring of its source document; so are the 40 guide
sentences in the pattern table. Tests run: 0 statistical (this is a catalogue); 2 validations (substring check, id resolution) passed.

## Bottom line

1. **The operating profile management is describing for 2H26 and FY27, by line.** Ops & support keeps falling per booking (AI
   resolves "nearly half" of tickets, cost per booking -10% then -16% y/y; 100% kept, n 17), but the savings are being re-spent on
   premium support and payroll (+$27m payroll, +$10m make-goods in 2Q26 MD&A), so model -4 to -5%/yr per night, not -16%. Cost of
   revenue steps up: the hosting commitment doubled to $1.7bn through 2031 and reserved-instance amortisation is already +$12-15m
   in 1H26; merchant fees stay ~1.8% of GBV; the "material increase" in AI spend (S162) lands here and in product development, ramping
   through 2H26 so FY27 carries a full year of it. Product development headcount growth "lower than 2025" (FY25 +12.3%): +8-10% cash
   growth, discounted because the FY24 headcount guide (C017) missed by 7 pts. Sales & marketing is the line with no discipline in the
   record: +27-30% y/y in 1H26 ($132m of paid growth marketing in emerging markets and partnerships in 2Q26 alone), "major
   announcements next year" (V023) mean launch cost before revenue again in FY27, brand statements 68% kept (n 41). G&A underlying
   +8% (payroll) masked by a one-off non-income-tax release. Below EBITDA: ETR mid-to-high teens (OBBBA), first full year of cash
   interest (~$119m on the $2.5bn notes), buyback authorisation ($3.4bn) runs out ~1Q27 and has always been renewed.
   **Net: management is describing a flat-to-slightly-up FY27 margin held by the floor policy, with the mix of cost inflation moving
   from marketing to hosting/AI.** Confidence: high on ops, hosting, tax, interest; medium on PD and S&M; nothing quantified for FY27.

2. **The November sentence follows a mechanical rule, not the YTD result.** Since a numeric floor has existed (FY24, FY25) the
   November letter converted "at least X" into "approximately X + 50bp" both times, and the eventual actual beat that point by 90 and
   10bp. In 2023, with no numeric floor, it was "approximately 150bps higher than 2022" (actual +228). YTD over-delivery did not move
   the wording: 9M margin y/y was +0.13 pts (2024) and -0.89 (2025) and the rule was the same. The February floor was set 184-190bp
   below the prior-year actual (FY24, FY25); FY26 broke the pattern (Feb "stable", May "at least 35%", Aug "at least 35.5%": two
   mid-year raises, none in 2024-25).

3. **What 5 Nov 2026 most likely looks like (prior for M3, not a forecast).** Sentence: *"For the full-year 2026, we now expect to
   deliver an Adjusted EBITDA Margin of approximately 36%"* (the floor + 50bp rule), with the Q4 sentence in the "decline / flat
   year-over-year" family and no FY27 number (none of the five Novembers gave one; the FY+1 line is qualitative: "maintaining strong
   margins while continuing to invest"). At the bridge-v3 implied Q4 revenue guide mid ($3,059m) and a 3Q26 margin of 49.5%
   ("down slightly" from 50.1%), "approximately 36%" implies a 4Q26 margin of 30.9% (+2.6 pts y/y); "at least 35.5%" unchanged
   implies 28.6% (+0.3). The FY sentence has under-called the Q4 actual by 0.7-4.3 pts (mean 2.9, n 3) every time.

4. **Reliability with the new rows:** total-margin statements 85% kept (n 55; 91% in 31a on n 43; the new partly/missed rows are
   Stephenson's conditional "ADR moderation" headwinds 2022-23 that never occurred and Mertz's 4Q24 "drag weighted to Q1-Q3" that was
   not). Conferences are the most reliable venue (91% kept, n 23) and filings the most (95%, n 20); the CEO on earnings calls the least
   (64%, n 22). Multi-year claims 65% kept (n 46); structural 91% (n 46); next-quarter 94% (n 16); full-year 72% (n 109).

## What was added (183 rows) and what was not reachable

| Source | Rows | Ids | Event dates | Notes |
|---|---|---|---|---|
| 10-Q MD&A three-month cost explanations, 17 filings 1Q21-2Q26 | 108 | `F<q>_<line>` | 2021-05-14 .. 2026-08-06 | one row per line (cor, ops, pd, sm_total, ga, interest, other): $ y/y change, %, drivers; backward-looking, so `verdict` n/a; the only sub-line disclosure Airbnb makes (census gap GAP06 closed) |
| Investor conferences: MS TMT 2023/2024, Bernstein 2024, GS Communacopia 2024/2025/**2026 (8 Sep 2026, new pull)** | 26 | V001-V026 | 2023-03-07 .. 2026-09-08 | Chesky and Mertz; GS26 gives 10 rows incl. "nearly half" of tickets on AI, "$1bn straight shot" seller services, "major announcements next year" |
| Earnings-call sentences 31a left out (4Q20-4Q25) | 28 | C001-C028 | 2021-02-25 .. 2026-02-12 | e.g. the FY24 PD "not above revenue growth" guide (missed by 7 pts), the 4Q24 investment-phasing miss |
| 10-K FY2023/24/25: headcount, hosting commitments, unrecognised SBC, ops mechanics | 10 | K001-K010 | | hosting $672m-through-2027 -> $1.7bn-through-2031 |
| 10-Q outlook/risk sentences (1Q21, 2Q25) | 7 | Q001-Q007 | | Q004 the FY21 capex guide missed |
| Non-earnings 8-Ks: 2021 converts, Italian tax settlement (Dec 2023), Mar 2026 notes | 4 | E001-E004 | | coupon ~$119m/yr on $2.5bn; EUR 576m settlement |

Not reachable or empty, logged per the brief: **LSEG** (`ld.news.get_headlines`, StreetEvents): the Workspace desktop session was
closed when tried at 04:15 (proxy on :9000/:9060 refused; "Check if Desktop is running"), so no conference transcripts or headlines
came from LSEG; the stockanalysis pages cover every conference on its list. **Interviews** with quantified cost claims: none pulled
(fool.com rate-limited, no sanctioned interview archive; nothing on airbnb.com may be fetched live). **Investor Day 2023**: Airbnb held
none; the two 2021 product-event transcripts (Summer/Winter Release, pulled) contain no cost or margin statement and yield 0 rows.
**pre-2023 FactSet transcripts** (Theo's OneDrive): read locally where 31a had not, nothing copied; the 2021-22 calls are covered by the
stockanalysis pages already in the tree. EDGAR full-text search for 8-K Items 7.01/8.01 returned the eight 8-Ks pulled; only three
carry cost content.

## The guide-language pattern (from `05_guide_language_pattern.csv`)

November prints. Implied Q4 margin = (FY sentence level x (9M revenue + Q4 revenue guide mid) - 9M adj. EBITDA) / Q4 guide mid; for
3Q21 and 3Q22 no FY number was given and the Q4 sentence itself is the floor.

| Print | FY sentence (type) | 9M margin, y/y pts | Q4 rev guide mid | Implied Q4 margin | Q4 actual | Q4 - implied | FY actual | FY - guide | FY+1 statement at that print |
|---|---|---|---|---|---|---|---|---|---|
| 3Q21 | none; Q4: "greater y/y and 2-yr margin expansion in Q4 than in Q3" (floor_yoy, Q3 was +11.9) | 28.23, +37.4 | 1,435 | 9.5 | 21.7 | +12.3 | 26.57 | n/a | none; ADR moderation flagged for 2022 |
| 3Q22 | none; Q4: "in-line to modestly higher than last year's 22%" (floor) | 36.89, +8.7 | 1,840 | 22.0 | 26.6 | +4.6 | 34.56 | n/a | marketing % of revenue similar in 2023; ADR moderation a headwind |
| 3Q23 | "approximately 150 bps higher than full-year 2022" (approx_yoy -> 36.06) | 37.86, +1.0 | 2,150 | 29.6 | 33.3 | +3.7 | 36.84 | +77bp | SBC growth similar in 2024; no margin number |
| 3Q24 | "now expect ... approximately 35.5%" (approx; Feb floor 35) | 38.00, +0.1 | 2,415 | 26.6 | 30.9 | +4.3 | 36.40 | +90bp | "share more about our 2025 growth and investment plans early next year" |
| 3Q25 | "now expect ... approximately 35%" (approx; Feb floor 34.5) | 37.10, -0.9 | 2,690 | 27.6 | 28.3 | +0.7 | 35.10 | +10bp | "maintaining strong margins while continuing to invest"; OBBBA ETR |

February / May / August (FY floor vs eventual beat):

| FY | Feb sentence | Floor vs prior FY actual | May | Aug | Nov | FY actual | Beat vs Feb floor |
|---|---|---|---|---|---|---|---|
| 2022 | "directionally in-line with 2021" (26.57) | 0 | "modest expansion" | "expansion" | none | 34.56 | +799bp |
| 2023 | "maintain the strong margin we delivered in 2022" (34.56) | 0 | "broadly in-line" | "modestly higher" | approx +150bp | 36.84 | +228bp |
| 2024 | "at least 35%" | -184bp | unchanged | unchanged | approx 35.5% | 36.40 | +140bp |
| 2025 | "at least 34.5%" | -190bp | unchanged | unchanged | approx 35% | 35.10 | +60bp |
| 2026 | "stable year-over-year" (35.10) | 0 | "at least 35%" | "at least 35.5%" | ? | ? | ? |

Distributions (`05_guide_language_stats.csv`): beat vs numeric Feb floor n 2, mean +100bp (60-140); beat vs November point n 3, mean
+59bp (10-90); beat vs qualitative Feb y/y guide n 2, mean +513bp; Q4 actual minus FY-sentence-implied Q4 n 3, mean +2.9 pts (0.7-4.3);
all five Novembers incl. the Q4-sentence floors n 5, mean +5.1 pts. The relation to YTD over-delivery: none visible on n 3 -- the
November level was the standing floor + 50bp in both years that had one, at 9M y/y of +0.1 and -0.9 pts.

The Q4 margin sentence: "decline relative to last year" at 3Q24 and 3Q25, both right (-2.4, -2.6 pts). The 2Q26 letter already says
3Q26 margin "down slightly ... due to timing of investments", which is the same construction.

## 5 Nov 2026 scenarios (`05_nov2026_scenarios.csv`)

1H26 actual: revenue $6,286m, adj. EBITDA $1,780m (28.32%, +1.12 y/y). 3Q26 revenue at the guide mid $4,730m; 3Q26 margin assumed
49.0 / 49.5 / 50.1 (down slightly, the guide; 49.5 is the stated centre). Q4 revenue guide mid: $3,059m (bridge v3 implied guide),
$2,980m (+7.3%), $3,178m (bridge v3 forecast).

| 5 Nov FY sentence | 9M margin (Q3 49.5) | Implied 4Q26 margin at $3,059m guide mid | y/y vs 28.29 |
|---|---|---|---|
| "at least 35.5%" unchanged | 37.41 (+0.31) | 28.6 | +0.3 |
| "approximately 35.5%" | 37.41 | 28.6 | +0.3 |
| **"approximately 36%"** (floor + 50bp rule) | 37.41 | **30.9** | **+2.6** |
| "at least 36%" | 37.41 | 30.9 | +2.6 |
| "approximately 36.5%" | 37.41 | 33.2 | +4.9 |

Range across the Q3 assumption: "approximately 36%" implies 30.0-31.7; "35.5%" implies 27.7-29.4. The historical under-call of the
November sentence (Q4 actual 0.7-4.3 pts above implied) means "approximately 36%" is consistent with a 4Q26 print anywhere from
31.6 to 35 and an FY26 print of 36.1-36.9.

Prior handed to M3 (weights are judgement, n 3): "approximately 36%" 0.45; "approximately 35.5%" or floor held at 35.5% 0.35 (the two
mid-year raises already spent the cushion; 9M y/y only +0.3); "at least 36%" 0.15; other 0.05. Q4 sentence: "flat to down / decline
year-over-year" 0.6, "expand" 0.4 (the 4Q25 base is the low one at 28.3). FY27 number on 5 Nov: 0.05; expect a qualitative line.
February 2027 FY27 floor: FY26 actual minus 0-190bp (n 3: -184, -190, 0).

## Corrections to existing work

- 31a rows are carried unchanged, but ten are re-filed under the finer v2 taxonomy (S140/S155/S162/S168 -> `ai`, S167/S181 -> `capex`,
  S103/S134/S148/S157 -> `tax`); `line_31a` keeps the original. Not an error in 31a.
- 31a's total-margin kept rate (91%, n 43) falls to 85% (n 55) once Stephenson's conditional ADR-headwind statements (C004, C007, C011)
  and Mertz's 4Q24 investment-phasing claim (C019) are added. 31a's per-line hit rates otherwise reproduce.
- The 3Q25 letter's Q4 sentence reads "flat- to-down slightly" in the PDF-derived HTML; kept verbatim (hyphenation artefact, not a typo of ours).
- `02_guidance_ledger.csv` has no row for the 3Q21 and 3Q22 Q4 margin sentences used here; both are quoted from the letters directly.

## For the model

| Name | Value | Unit | Source |
|---|---|---|---|
| nov_sentence_rule | floor + 0.5 | pts, "approximately" | pattern rows 3Q24, 3Q25 (n 2) |
| nov_point_beat | +10 / +90 / +77 (mean 59) | bp, FY actual - November point | 3Q25, 3Q24, 3Q23 |
| feb_floor_beat | +140, +60 (mean 100) | bp | FY24, FY25 |
| feb_floor_vs_prior_actual | -184, -190, 0 (FY26 "stable") | bp | 4Q23, 4Q24, 4Q25 |
| q4_actual_minus_implied | +3.7, +4.3, +0.7 (mean 2.9) | pts | 3Q23-3Q25 |
| ops_cost_per_booking_yoy | -10 (1Q26), -16 (2Q26) | % | S160, S188; V019 (~half of tickets on AI) |
| hosting_commitment | 1,700 through 2031 (~283/yr) vs 672 through 2027 (~224/yr) | usd_m | K004-K007 |
| purchase_obligations_2027_28 | 930 / 2 = 465 per year vs 219 in 2026 | usd_m | H03 (10-K FY2025) |
| server_costs_1h26 | +15 (reserved-instance amortisation) | usd_m y/y | F1Q26_cor, F2Q26_cor |
| sm_1h26_growth | +30 (1H), +27 (2Q); $258m emerging-market and partnership marketing in 1H26 | % y/y, usd_m | F1Q26/F2Q26_sm_total |
| pd_growth_guide_fy26 | headcount growth below FY25's 12.3% | qualitative | S163, S144, K003 |
| etr_long_term | 17-19 | % | S148, S157, S134 |
| interest_expense_fy27 | ~119 | usd_m/yr | E003 (4.40/4.65/5.25% on $2.5bn) |
| buyback_authorisation | 3,400 remaining at 30 Jun 2026; ~1,000-1,100/quarter pace | usd_m | 2Q26 letter (H11) |
| reliability_by_line | ops 100 (n 17), cor 100 (8), hosting 100 (5), sm_field 80 (15), margin_total 85 (55), sm_brand 68 (41), take_rate 63 (19), pd 61 (18), sbc 50 (6) | % kept | `05_reliability_by_line.csv` |

## For the 5 Nov card

- Modal sentence: "approximately 36%" for FY26 (floor + 50bp); watch for "at least 36%" as the bullish tell (never used in November).
- Implied 4Q26 margin at the guide-mid revenue: ~31% for "approximately 36%", ~28.6% for an unchanged 35.5%; the print has beaten
  the implied Q4 by 0.7-4.3 pts every year.
- No FY27 margin number on 5 Nov; the February floor will sit 0-190bp below the FY26 print.
- Lines to listen for: AI spend size (never given), hosting/reserved-instance amortisation, "major announcements next year" cost,
  emerging-market marketing run-rate, support cost per booking (the only kept quantified series).

## RESUME

WS05 is complete: the script rebuilds all seven CSVs with exit 0 and every verbatim verifies; the pass line is met (183 new rows,
155 from 31 non-earnings events, five November rows with implied Q4 margins checked against actuals). The next agent (M3) should read
`05_guide_language_pattern.csv`, `05_guide_language_stats.csv` and `05_nov2026_scenarios.csv` and treat the sentence weights above as
a prior on n 3, not a fitted model; `05_fy27_hints.csv` feeds M1/M6/M7 (hosting step, AI ramp, interest, tax, buyback). If the LSEG
desktop is reopened, `ld.news.get_headlines("Airbnb AND conference")` was never run successfully and could add Citi/JPMorgan/Deutsche
Bank appearances not on stockanalysis.com; the 10-Q MD&A rows (`origin = 10q_mda`) are the quarterly component series WS01 asked for
(GAP06) and can be pivoted into a panel by M1 without re-parsing.
