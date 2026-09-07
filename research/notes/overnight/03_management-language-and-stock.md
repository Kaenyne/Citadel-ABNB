# 03. What management says on the call, and how it moves the stock

**Date:** 2026-09-06 · **Author:** Krishang (compiled with Claude Code) · **Workstream 03 of the overnight run**

**Scope:** all 23 Airbnb earnings calls, Q4 2020 (25 Feb 2021) to Q2 2026 (6 Aug 2026), plus the 23 shareholder
letters. 1,677 speaker turns parsed with exact speaker attribution.

**Files written**

| What | Path |
|---|---|
| Per-print language features (132 columns) | `data/processed/overnight/03_call_features.csv` |
| Every speaker turn, auditable | `data/processed/overnight/03_call_turns.csv` |
| Theme regexes and lexicons | `data/processed/overnight/03_theme_lexicon.csv` |
| 83 forward-looking claims with outcomes and verdicts | `data/processed/overnight/03_forward_claims.csv` |
| Credibility scorecard by theme / executive / horizon | `data/processed/overnight/03_credibility_scorecard.csv` |
| 474 feature-vs-reaction tests | `data/processed/overnight/03_reaction_tests.csv` (+ `03_reaction_summary.csv`) |
| 237 detrended and numbers-controlled tests | `data/processed/overnight/03_reaction_controls.csv` |
| Incremental leave-one-out R² over a numbers-only model | `data/processed/overnight/03_reaction_incremental.csv` |
| Event study, 5 best and 5 worst reactions | `data/processed/overnight/03_event_study.csv` |
| Scripts | `analysis/src/overnight/03_call_features.py`, `03_reaction_tests.py`, `03_forward_claims.py`, `03_event_study.py` |
| Figures | `analysis/figures/overnight/03_theme_timeline.png`, `03_feature_vs_reaction.png`, `03_event_study.png` |

---

## Bottom line

1. **Call language explains reactions; it does not predict anything.** Every feature here is known only at
   ~17:30 ET on print day, after the letter at 16:05 ET and after the stock has already moved in the
   after-hours session. Nothing in this note is a pre-print signal. Treat it as a **reading guide for 5 Nov**,
   not as a factor.
2. **Classic text sentiment is worthless on this name.** Loughran-McDonald net tone in management Q&A has a
   detrended correlation of **+0.08** with the day-1 excess return (n = 23). Hedging share +0.09, the Q&A
   minus prepared tone gap −0.11, the change in macro-softness share −0.13. All null. Anyone pitching
   "management sounded cautious" as a signal is reading noise.
3. **What does line up is structural, not tonal.** The share of *prepared remarks* spent on long-term targets
   and full-year framing is the strongest single language feature: detrended r **+0.69** with the day-1
   excess (perm p = 0.0005), r **+0.72** after also controlling for the revenue beat, the guide acceleration
   and the change in nights growth. It is the only one of 79 features that turns a numbers-only day-1 model
   from LOO R² −2.31 into **+0.34**. The mirror image is international-expansion talk: detrended r **−0.62**.
   Read plainly: **calls where management leads with a number-bearing framework go up; calls where they lead
   with "we are investing in markets you cannot see yet" go down.**
4. **But nothing survives multiplicity.** 474 primary tests, 237 control tests, 237 incremental tests — 948
   in total. Benjamini-Hochberg q < 0.10 across either grid: **zero**. The best q is 0.12. With n = 23 the
   smallest detectable |r| at 5% is 0.41, so this is a hypothesis-generating exercise, not evidence.
5. **All ten of the biggest reactions turned on forward statements, none on the reported quarter.** Five best
   and five worst: 3 revenue guides, 2 nights guides, 1 nights beat, 2 macro warnings, 1 investment-spend
   disclosure, 1 long-term margin framework. Airbnb has beaten its own revenue guide in **19 of 19** quarters and the beat
   has never set the reaction (see `research/notes/2026-09-06_predictive-study.md`). The tape prices the
   forward sentence.
6. **Management's forward claims hit 62% of the time, and the hit rate collapses with horizon and vagueness.**
   Next-quarter claims 80% (n = 15); full-year 73% (n = 30); multi-year **26%** (n = 19). Quantified claims
   82% (n = 27); unquantified 49% (n = 39). Prepared remarks and the letter 100% / 75%; unscripted Q&A 52%.
   By person: Dave Stephenson 74%, Ellie Mertz 63%, **Brian Chesky 42%**.
7. **One theme is 0 for 7: pricing and affordability.** Every management claim that ADR would moderate, that
   supply growth would hold prices down, or that pricing tools would improve affordability, has been wrong.
   ADR rose in every calendar year since the claims began: $156.0 (2021) → $160.3 → $163.1 → $166.0 → $171.2
   → $185.3 (1H26). If the pitch has an ADR view, do not take it from the transcript.

---

## 1. The feature table

`03_call_features.csv`, one row per print, 132 columns: prepared and Q&A word counts, analyst count and
question count, CEO/CFO speaking share by section, Loughran-McDonald tone and hedging per 1,000 words,
numeric-quantification counts, forward-verb density, "won't quantify" counts, 13 theme sentence shares
(prepared / Q&A / total) and the change in each versus the prior call.

**Sources.** IR FactSet corrected transcripts for 4Q21 and 1Q23–2Q26 (15 calls, `data/raw/transcripts/ir/`);
Motley Fool web transcripts for 4Q20–3Q21 and 1Q22–4Q22 (8 calls, fetched 6 Sep 2026 into the scratchpad).
The Fool copies carry `<strong>Speaker</strong> -- Title` tags and explicit Prepared Remarks / Q&A headers,
so speaker attribution is exact — the stockanalysis.com copies used by
`research/notes/2026-09-05_transcript-analytics.md` do not have speaker tags. **Coverage is 23 of 23 prints**;
the earlier gap flagged in the resume note is closed.

### The call has changed shape twice

| | 4Q20–2Q25 (19 calls) | 3Q25–2Q26 (4 calls) |
|---|---|---|
| Prepared-remark words | 1,128 average | **2,430 average** |
| Numeric quantifications in prepared remarks | 25.0 average | **45.5 average** |
| Management Q&A words | 6,806 | 6,160 |
| Analyst questions | 32.4 | **23.5** |
| Distinct analysts on the call | 14.3 | **11.8** |

Since 3Q25 Airbnb has moved the substance out of Q&A and into a scripted, number-dense prepared section, and
sell side engagement has fallen with it. 2Q26 had **15 analyst questions and 12 analysts, both records lows**,
on a print that moved the stock +17.4%. The Street is asking less at exactly the moment the story is changing.

### Narrative rotation (share of management sentences; full series in the CSV, chart in `03_theme_timeline.png`)

| Theme | 2021 avg | 2023 avg | 2026 (1Q+2Q) |
|---|---|---|---|
| Supply / hosts | 19.8% | 14.8% | 9.1% |
| New businesses, Services, Experiences | 4.4% | 8.0% | 11.3% |
| AI | 0.0% | 3.2% | **9.4%** |
| Pricing / ADR / affordability | 3.7% | 9.7% | 5.7% |
| International expansion | 3.7% | 7.1% | 3.0% |
| Take rate / fees | 1.1% | 1.0% | 2.8% |
| Demand softness / macro | 1.6% | 1.7% | 2.2% |

Supply — the metric Chesky called "a long-term indication of growth in Airbnb" in 4Q23 — has been talked out
of the story. AI went from literally zero mentions before 4Q22 to the second-largest theme. Take-rate talk
has doubled in 2026, which matters because the single-fee migration is the live monetisation lever.

### Tone facts worth knowing

- Management's Q&A tone is **below** its prepared tone in **22 of 23 calls**
  (mean gap −12.2 per 1,000 words). The scripted section is systematically more upbeat. This is a constant, so it carries no information.
- The one exception is 1Q23 (+5.0), the print that fell 12.0% excess.
- "Declined to quantify" is rare and rising: 37 hand-verified instances across 23 calls, four of them in 2Q26.

---

## 2. Do the features explain the reaction?

Excess return = ABNB minus QQQ over 1, 5 and 20 sessions (`data/processed/abnb_earnings_reactions.csv`).
n = 23 (22 for the 20-day horizon, which is missing for 2Q26; 22 for change-vs-prior-call features).

**Test count and multiplicity.** 79 features × 3 horizons × 2 samples (all prints; 2023Q1 onward, n = 14) =
474 primary tests. 64 clear nominal p < 0.05 against 23.7 expected by chance. **BH q < 0.10: zero.** A second
grid of 237 tests adds two controls — a linear time index, and the print's own numbers (revenue beat vs guide
midpoint, next-quarter guide acceleration, change in year-over-year nights growth, from
`abnb_reaction_inputs.csv`, n = 17 with all inputs present). BH q < 0.10 there: also zero; best q = 0.12.

### Headline features, day-1 excess

| Feature | raw r | r with time index | **detrended r** | perm p | r controlling for the print's numbers (n=17) |
|---|---|---|---|---|---|
| Long-term-target / full-year framing, share of prepared remarks | +0.43 | +0.68 | **+0.69** | 0.0005 | **+0.72** |
| International-expansion share, all management sentences | −0.62 | +0.01 | **−0.62** | 0.0035 | −0.63 |
| Change in long-term-target share vs prior call | +0.57 | +0.16 | +0.58 | 0.0035 | +0.72 |
| Analyst net tone (LM, per 1k) | +0.50 | −0.07 | +0.49 | 0.016 | +0.68 |
| Prepared-remark words | +0.32 | +0.60 | +0.49 | 0.018 | +0.44 |
| Numeric quantifications, prepared remarks | +0.07 | **+0.85** | +0.31 | 0.16 | +0.45 |
| Analyst question count | −0.24 | −0.55 | −0.36 | 0.093 | −0.37 |
| Change in macro-softness share vs prior call | −0.13 | −0.10 | −0.13 | 0.56 | −0.20 |
| Q&A minus prepared tone gap | −0.07 | −0.31 | −0.11 | 0.60 | −0.22 |
| Hedging, management Q&A | +0.08 | +0.06 | +0.09 | 0.68 | +0.27 |
| **LM net tone, management Q&A** | +0.12 | −0.46 | **+0.08** | 0.72 | +0.08 |

Read the "r with time index" column before the others. Quantification count correlates +0.85 with the calendar
and its apparent relationship with returns is almost entirely that trend — the same 2023-trend artefact the
predictive study found in the macro nowcasts. Long-term-target share also trends (+0.68) but **strengthens**
after detrending, which is the opposite pattern and the reason it is the one feature worth carrying forward.

**Change-in-theme-share tests.** Only the change in long-term-target share survives detrending (+0.58). The
intuitive ones — an increase in macro-softness talk, a jump in marketing talk, a drop in supply talk — are all
insignificant. Management do not telegraph a bad print by shifting the topic mix relative to last quarter.

**Q&A vs prepared tone gap.** Null on every horizon (day-1 detrended r −0.11). Because the gap is negative in
22 of 23 calls there is almost no cross-sectional variation to work with.

**Analyst question count and tone.** Question count is weakly negative (detrended −0.36, p 0.09): more
questions, worse reaction. Analyst *tone* is the second-strongest correlate (+0.49, +0.68 controlling for the
numbers) but it is endogenous — analysts congratulate a good print — and it is measured on the same call, so
it has no trading use whatsoever. Keep it as a reading cue, not a variable.

**Incremental value over the numbers.** A day-1 model on beat-vs-guide, guide acceleration and nights
acceleration has LOO R² of **−2.31** at n = 17: three predictors on seventeen points is unfittable out of
sample. Adding long-term-target share takes it to **+0.34**, the only specification of 79 that reaches
positive out-of-sample R². Adding pricing/ADR share or analyst-turn counts takes it to −5. This is a
one-variable finding on a tiny sample; do not put it in a model, put it in the pre-call checklist.

---

## 3. Event study: the five best and five worst reactions

`03_event_study.csv`, figure `03_event_study.png`. Quotes are verbatim from the letter or transcript and every
one is verified as a literal substring by the script (`quote_verified = yes` for all ten).

*Press caveat:* this session's WebSearch budget (200 calls) was exhausted by other overnight workstreams
before this step, and Reuters/CNBC are not fetchable from this environment. The "what the press led with"
column is taken from `research/notes/2026-09-05_abnb-major-moves.md` and
`data/processed/abnb_major_moves_events.csv`, which were compiled from same-day CNBC / Reuters / Skift /
Seeking Alpha coverage on 5 Sep 2026, rather than re-fetched. The quotes themselves are primary-source.

| Quarter | Day-1 excess | Driver | What management said (verbatim, ≤30 words) |
|---|---|---|---|
| 2Q26 | **+16.3%** | guide | *"we now expect year-over-year revenue growth to improve to at least mid teens, supported by the accelerated pace of Nights and Seats Booked we've observed"* — letter |
| 4Q24 | **+14.0%** | KPI | *"Q4 was our highest nights and bookings growth quarter of 2024 and we are excited by the continued strong demand we are seeing in 2025."* — letter |
| 3Q21 | **+12.9%** | guide | *"looking forward to a strong Q4 with accelerating GBV growth, continued revenue strength, and further Adjusted EBITDA margin expansion, compared to Q3 2021"* — letter |
| 4Q20 | **+12.9%** | margin | *"And what we would expect to achieve over time is 30% EBITDA margins or greater."* — Dave Stephenson, Q&A |
| 4Q22 | **+12.6%** | guide | *"We expect revenue of $1.75 billion to $1.82 billion in Q1 2023. This represents year-over-year growth of between 16% and 21%"* — letter |
| 2Q24 | **−12.3%** | macro | *"However, we are seeing shorter booking lead times globally and some signs of slowing demand from U.S. guests."* — letter |
| 1Q23 | **−12.0%** | KPI | *"We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth during the quarter."* — letter |
| 3Q22 | **−10.0%** | KPI | *"On a year-over-year basis, we expect Nights and Experiences Booked growth will moderate slightly relative to Q3 2022"* — letter |
| 3Q24 | **−8.8%** | investment spend | *"Obviously, the guide does imply several point margin compression relative to last Q4. You should see that most specifically in terms of both the product development line item as well as marketing."* — Ellie Mertz, Q&A |
| 2Q25 | **−8.4%** | macro | *"we expect a tougher year-over-year comparison toward the end of the quarter. This dynamic will continue into Q4, putting pressure on growth rates later in the year."* — letter |

**Three things fall out of the table.**

- **Eight of ten quotes are from the letter or a scripted guide paragraph, not from spontaneous Q&A.** The
  sentence that moves the stock is written in advance. Two exceptions (4Q20, 3Q24) are both CFO answers about
  the cost/margin structure.
- **Nine of ten are about the next period, not the reported one.** 4Q22's first profitable year is the only
  case where the reported quarter carried the day, and even there the Q1 guide beat was the cited cause.
- **The language features separate the two groups cleanly**, which is where the section-2 correlations come
  from:

| Feature (mean) | 5 best | 5 worst |
|---|---|---|
| Long-term-target share of prepared remarks | 4.1% | **0.8%** |
| International-expansion share | 3.5% | **6.6%** |
| Demand-softness / macro share | 1.4% | **3.4%** |
| Prepared-remark words | 1,412 | 1,047 |
| Analyst net tone (LM per 1k) | +7.9 | +1.2 |
| Analyst questions | 27.8 | 32.2 |
| **LM net tone, management Q&A** | 12.1 | 10.2 |

Note the last row. Management's own measured tone is essentially identical on the best and the worst days.

**Two of the five worst were management being wrong in the cautious direction.** After the 2Q24 warning about
shorter lead times, Q3 2024 nights grew 8.5% against Q2's 8.7% — a 0.2-point moderation for a 12.3% drawdown.
After the 2Q25 warning that comps would pressure 2H growth, nights *accelerated*: 7.4% → 8.8% → 9.8%. On both
occasions the market took the caution at face value and the caution was wrong. That is a repeatable setup: an
8–12% de-rating on a hedged forward sentence that does not verify.

---

## 4. Management credibility scorecard

83 curated forward-looking claims from the 23 calls and letters, each verified verbatim against its source,
each with the later outcome and a verdict (`03_forward_claims.csv`, scorecard in
`03_credibility_scorecard.csv`). 66 have closed; 11 are too early; 6 are unverifiable because Airbnb never
disclosed the metric needed to score them.

**Selection note.** The raw pool is ~800 forward-looking sentences; most are unfalsifiable product talk. What
is curated is every claim that names a metric or a checkable state of the world and whose horizon has passed,
plus the open claims that matter for 5 Nov. Read the hit rate as "hit rate among checkable claims".

| Cut | n closed | kept | partly | missed | hit rate |
|---|---|---|---|---|---|
| **All claims** | 66 | 41 | 7 | 18 | **62%** |
| Dave Stephenson (CFO to Feb 2024) | 23 | 17 | 2 | 4 | **74%** |
| Ellie Mertz (CFO from Mar 2024) | 16 | 10 | 1 | 5 | **63%** |
| Brian Chesky (CEO) | 19 | 8 | 3 | 8 | **42%** |
| Shareholder letter | 8 | 6 | 1 | 1 | 75% |
| Next-quarter horizon | 15 | 12 | 2 | 1 | **80%** |
| Full-year horizon | 30 | 22 | 1 | 7 | 73% |
| Multi-year horizon | 19 | 5 | 4 | 10 | **26%** |
| Quantified | 27 | 22 | 1 | 4 | **82%** |
| Not quantified | 39 | 19 | 6 | 14 | **49%** |
| Prepared remarks | 10 | 10 | 0 | 0 | 100% |
| Unscripted Q&A | 48 | 25 | 6 | 17 | **52%** |

**By theme** (closed claims): buybacks/SBC 5/5, marketing 7/8, margins 13/17, demand-macro 7/10, take
rate/fees 3/6, new businesses 3/6, **pricing/ADR 0/7**, international 0/2.

### The claims that were quietly dropped

- **"Every year now, for the coming years, we will launch one to two new businesses that will generate
  $1 billion or more of revenue incrementally a year"** — Chesky, 3Q24 call. Twelve months later, on the 3Q25
  call, the same person said *"it's going to take three to five years, I think, for services, experiences to
  become a material part of our business"*, and the 2Q25 letter says *"we don't expect meaningful revenue from
  our new businesses in the near term"*. The $1bn-a-year cadence was never repeated and never withdrawn. This
  is the most important dropped claim in the file: it is the number the bull case for Services/Experiences was
  built on.
- **"Most of these new services and offerings are going to not cost very much"** — Chesky, 2Q24. Two quarters
  later Airbnb guided $200–250m of 2025 new-business spend and cut the FY25 margin floor to 34.5%.
- **The FY2025 take-rate guide.** *"For full year 2025, you should assume that the implied take rate gets the
  full benefit of 20 basis points increase on a year-over-year basis as compared to 2024"* — Mertz, 4Q24 call.
  Actual: 13.41% vs 13.57%, **down 16bp against a guided +20bp — a 36bp miss** on the most model-relevant
  number management gave in 2025. It was never revisited on a later call.
- **The 1Q26 take-rate guide was walked back within one quarter.** 1Q26: *"you should see modest upside to our
  take rate"*. 2Q26 letter: implied take rate *"relatively flat compared to 2025"*. Take-rate guidance from
  this company has a one-quarter half-life.
- **Marketing as a percent of revenue.** Held flat as promised in 2021, 2022 and 2023; then 4Q23's *"we're
  going to keep marketing costs as a percentage of revenue largely the same as what it was in 2023"* missed by
  150bp (19.3% vs 17.8%) and the line has risen every year since: 19.3% → 21.1% → **25.9% in 1H26**.
- **Free cash flow margin expansion** (3Q22): 40.5% (2022) → 38.7% → 40.4% → 37.7% (2025). No expansion.
- **The $200–250m new-business investment for 2025 was never reported as an actual.** Nor has any Services or
  Experiences revenue figure been given, twelve months after launch.

### What this implies for how to read the 5 Nov guide

The company's *quantified, next-quarter and full-year* guidance is genuinely reliable — 80% and 73%, and
Airbnb has beaten its own revenue guide in 19 of 19 quarters. Take the Q3 revenue guide of $4.69–4.77bn and
the FY26 "at least mid-teens / at least 35.5%" as high-confidence. Everything the CEO says about ADR,
affordability, market penetration or the size of a new business should be discounted to roughly a coin flip.

---

## 5. What to listen for on 5 November 2026

Ranked by how much the past nine years of transcript actually justify.

1. **Whether the full-year framework appears in the prepared remarks, and how numeric it is.** This is the one
   language feature that survives both controls. Twelve of the 23 calls spent *zero* prepared sentences on
   long-term or full-year framing and averaged **−2.7%** day-1 excess; the eleven that spent some averaged
   **+4.0%**. Be honest about the strength: the sign hit rate is 6/11 versus 5/12, a coin flip. It is the mean
   that separates, driven by the tails (2024Q4 +14.0% at a 10.2% share, 2026Q2 +16.3% at 6.4%; 2024Q2 −12.3%,
   2023Q1 −12.0%, 2022Q3 −10.0%, 2024Q3 −8.8% all at zero). If Mertz raises or reiterates FY26 with a number,
   that is the bullish tell. If the prepared section drifts into expansion-market and Experiences narrative
   without a full-year figure, that is the 2Q24/1Q23 pattern.
2. **The nights and seats guide for Q4, in relation to the revenue guide.** Three of the five worst reactions
   were a nights guide, and the 1Q23 crash was specifically nights guided *below* revenue. Q3 2026 is guided
   to low-double-digit nights growth on 15–17% revenue growth; a Q4 nights guide that drops to mid-single
   digits while revenue stays mid-teens re-runs 1Q23.
3. **Any hedged 2H/2027 macro sentence.** The 2Q24 and 2Q25 warnings cost 12.3% and 8.4% of excess return and
   both proved wrong within two quarters. If the same construction appears — "tougher comparisons",
   "shorter lead times", "pressure on growth rates later in the year" — expect the drawdown, and expect the
   caution not to verify. That is where the 5–20 session reversal trade lives, not the day-1 trade.
4. **Whether the single service fee finishes on time and what it does to the take rate.** Mertz said on 6 Aug
   2026 *"we anticipate by year end, our entire supply base will be on that single service fee"* and guided
   FY26 implied take rate flat. Take-rate guidance from this management has been walked back twice in eighteen
   months. A slip on either is the highest-probability negative surprise on the card.
5. **The first quantification of hotels.** Chesky said hotels are *"going significantly better than I
   expected"* and Mertz said Airbnb intends to *"exit 2026 with hotels being a meaningfully larger percent of
   the overall business"*. There is still no hotels GBV or nights disclosure. 5 Nov is the natural place for
   one; a first number, in either direction, is a new fact for the model.
6. **Whether Services/Experiences gets a revenue figure or a fourth timeline.** The claim has already slipped
   from "$1bn a year, every year" (3Q24) to "three to five years to material" (3Q25). Another slip is a
   credibility event, not a modelling one.
7. **2027 margin framing.** FY26 is guided to at least 35.5% versus a 36.8% peak in 2023. The first mention of
   a 2027 margin number, and whether it is above or below 36%, sets the terminal-margin debate for the pitch.
8. **Question count.** 2Q26 had 15 analyst questions from 12 analysts, both record lows, and question count is
   the one *negatively* signed engagement feature (detrended r −0.36). Falling engagement has coincided with
   better reactions, probably because there is less to push back on. Watch it, do not trade it.

---

## 6. Negative results, stated plainly

Run and rejected: management LM sentiment (prepared, Q&A, total, and change vs prior call); hedging density;
the Q&A-minus-prepared tone gap; the hedging gap; uncertainty-word density; forward-verb density; the change
in every one of the 13 theme shares except long-term targets; numeric-quantification count once detrended;
"won't quantify" phrase counts; CEO vs CFO speaking share (day-1); all of the above on the 5- and 20-session
horizons and on the post-2022 subsample. 948 tests, zero BH-significant results at q < 0.10 on either grid.

Point-in-time discipline: every feature in `03_call_features.csv` becomes knowable at the end of the call
(~17:30 ET on print day). The letter lands at 16:05 ET, the after-hours move has already happened, and the
day-1 excess return is measured from that day's close to the next close. **Call features are therefore
explanatory only.** There is no version of this work that becomes a forecast.

Sample: n = 23 prints overall, n = 14 post-2022, n = 17 with the fundamentals controls attached, n = 66 closed
forward claims. Smallest detectable |r| at n = 23, two-sided 5%: 0.41.

---

## Corrections to existing work

None. `research/notes/2026-09-05_transcript-analytics.md` (analyst roster, topic frequency, declined-to-quantify
list) and `research/notes/2026-09-05_abnb-major-moves.md` (41 attributed moves) both reconcile with what is
here; the 37 hand-verified declines in `data/processed/abnb_declined_to_quantify.csv` are carried through as a
feature column. The earlier transcript work used stockanalysis.com copies without speaker tags for pre-2023
calls; this workstream re-sourced those eight calls from Motley Fool to get exact speaker attribution, which
is why CEO/CFO shares are available for the whole 2020–2026 history here and were not before.

---

## For the model

| Name | Value | Unit | Source |
|---|---|---|---|
| `mgmt_guide_hit_rate_next_q` | 80 | % of 15 closed next-quarter claims | `03_credibility_scorecard.csv` |
| `mgmt_guide_hit_rate_full_year` | 73 | % of 30 closed full-year claims | `03_credibility_scorecard.csv` |
| `mgmt_guide_hit_rate_multi_year` | 26 | % of 19 closed multi-year claims | `03_credibility_scorecard.csv` |
| `mgmt_hit_rate_quantified` | 82 | % of 27 closed quantified claims | `03_credibility_scorecard.csv` |
| `mgmt_hit_rate_unquantified` | 49 | % of 39 closed unquantified claims | `03_credibility_scorecard.csv` |
| `ceo_claim_hit_rate` | 42 | % of 19 closed Chesky claims | `03_credibility_scorecard.csv` |
| `cfo_claim_hit_rate` | 69 | % of 39 closed CFO claims | `03_credibility_scorecard.csv` |
| `pricing_adr_claim_hit_rate` | 0 | % of 7 closed ADR/affordability claims | `03_forward_claims.csv` |
| `fy25_take_rate_guide_error` | −36 | bp (actual 13.41% vs guided ≈13.77%) | C057, `abnb_driver_history_quarterly.csv` |
| `fy24_marketing_guide_error` | +150 | bp of revenue (19.3% actual vs 17.8% guided-flat) | C042, `abnb_quarterly_costlines.csv` |
| `services_experiences_materiality_date` | 2028–2030 | management's own current horizon | C067, 3Q25 call |
| `long_term_target_share_prepared` | 0.0643 | share of prepared sentences, 2Q26 | `03_call_features.csv` |
| `reaction_beta_long_term_target_share` | +0.69 | detrended corr. with day-1 excess, n=23 | `03_reaction_controls.csv` |

**How to use these.** Apply a haircut to any multi-year or unquantified management assertion carried into the
DCF: the empirical realisation rate is 26% and 49% respectively. Treat next-quarter and full-year quantified
guidance as ~80% reliable and directionally conservative (19 of 19 revenue beats). Do **not** put any language
feature into a return model.

## For the 5 Nov card

- Q3 2026 guide to check against: revenue **$4.69–4.77bn (+15–17%)**, GBV mid-teens, nights and seats
  low-double-digit, adj. EBITDA up year over year with margin down slightly vs Q3 2025's 50.1%.
- Full-year 2026 guide to check: revenue **at least mid-teens**, adj. EBITDA margin **at least 35.5%**,
  implied take rate **relatively flat vs 2025's 13.41%**.
- Open claims whose verdicts land on or after 5 Nov, from `03_forward_claims.csv`: C078 (FY26 revenue),
  C079 (FY26 margin), C080 (FY26 take rate), C081 (entire supply base on the single fee by year end),
  C082 (hotels), C071 (>30% of support tickets handled by AI, due Feb 2027), C073 (hotels a meaningfully
  larger percent of the business by end-2026).
- Base rate for the day: 23 prints, 11 moves of 7% or more, 6 of them negative despite a revenue beat. The
  reaction will be set by the Q4 nights guide and the FY26 wording, not by the Q3 beat.
