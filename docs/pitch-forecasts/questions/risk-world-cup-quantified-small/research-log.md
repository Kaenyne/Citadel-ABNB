# RESEARCH LOG

Revision 2 (2026-09-17, audit response to `audits/A12-research-audit.md`, Fable 5.1; revision 1 of 2026-09-17 was the initial forecast, batch A12 with R10, R11, R16). Reproduction: [datasets/r15_model_v2.py](datasets/r15_model_v2.py) (`py -3.13`, pure arithmetic; writes `r15_v2_event_record.csv`, `r15_v2_base_rate.csv`, `r15_v2_tree.csv`, `r15_v2_sensitivity.csv`). Revision-1 `r15_model.py` and its CSVs are left in place as the audit trail. Verbatim event passages from every letter and call: [sources/event_passages_letters_transcripts_extract.txt](sources/event_passages_letters_transcripts_extract.txt).

## 0. Metadata
- question_name: risk-world-cup-quantified-small
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R15)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
By the Feb print, will management quantify the 2026 World Cup's contribution to nights or GBV at ≤1 point (or state it was not material)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if a letter or call gives a figure ≤1pt of nights or GBV, or says the contribution was immaterial/not meaningful to the growth rate. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted: (1) "letter or call" = the 3Q26 and 4Q26 shareholder letters, the two earnings calls (prepared remarks and Q&A), and the 10-Q/10-K text; investor-conference remarks do not count (priced in §7); (2) a figure counts whether stated as the 2Q26/3Q26 contribution ("roughly 1 point of Q2 nights") or as the 2027 lap ("about a 1-point headwind to Q2 2027"), in points or basis points of nights or GBV; a figure >1pt (e.g., "approximately 2 points") resolves No; a revenue-dollar figure resolves Yes only if it converts to ≤1pt of GBV at the trailing take rate; (3) "immaterial / not meaningful to the growth rate" requires a statement about the size of the World Cup's contribution to growth ("not a meaningful driver of Q2 growth", "not material to our growth rate", "relatively small compared to total nights", "insignificant to the total nights booked"); the 2Q26 line "bookings from any single event may be temporary" does not count (it is about duration, not size), nor does a qualitative "tougher comparison" for 2Q27 (a headwind mention is the opposite of immaterial); (4) letter governs where letter and call differ; if only the call carries the statement, the call resolves.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Paris 2024 record, verbatim: **1Q24 letter (EMEA) "with the upcoming Olympics, we have seen a strong backlog of nights this Summer. While the impact of a single city for a limited duration is insignificant to the total nights booked in a region, we believe Airbnb is crucial..."** (a second, stronger size-language line, in the run-up quarter; missed by revision 1 and by the audit's phrase list); 1Q24 letter "nights booked for stays during the dates of the Olympics are over five times higher ... Germany ... nearly double"; 2Q24 letter "nights booked in the Paris region for the dates of the event through Q2 were more than double ... Over the course of the Olympics, more than 400,000 guests"; 2Q24 letter (EMEA) "**While the impact of a single city for a limited duration is relatively small compared to the total nights booked in a region**, we believe Airbnb is crucial..."; 3Q24 letter "a slight acceleration in growth of Nights and Experiences booked in EMEA ... buoyed by the Summer Olympic and Paralympic Games ... almost 700,000 guests ... supply of approximately 35%"; 4Q24 call "700,000 guests in Paris". No points figure in any of the five | `data/raw/letters/1Q24_d813800dex991.htm`, `2Q24_d831385dex991.htm`, `3Q24_d886752dex991.htm`; `data/raw/transcripts/web/2Q24.html`, `3Q24.html`, `4Q24.html` | 2024-05-08 to 2025-02-13 | 2026-09-17 | yes |
| 2 | Paris lap, 3Q25 letter (EMEA): "we faced a **slightly unfavorable year-over-year comparison** within the region due to the Paris Summer Olympic and Paralympic Games in 2024" — qualitative, no points; a headwind framing, not an immateriality framing | `data/raw/letters/3Q25_d40503dex991.htm` | 2025-11-06 | 2026-09-17 | yes |
| 3 | Milan 2026 and World Cup preview, 1Q26 letter/call: "nearly 200,000 guests ... supply in host markets grew approximately 30% ... GBV more than tripling" (host markets); "we expect to host more guests than at any event in Airbnb's history ... over 100,000 homes ... listed for the first time"; Q&A (Nick Jones, BNP): Mertz answered on booking patterns ("a lot of the booking activity happens close to the actual games"), supply retention ("in excess of half" of Paris event listings six months later), no size of the contribution | `data/raw/letters/1Q26_d23351dex991.htm`; `data/raw/transcripts/web/1Q26.html` | 2026-05-07 | 2026-09-17 | yes |
| 4 | World Cup, 2Q26 letter/call (the event's own quarter): "Airbnb hosted millions of guest arrivals during the tournament, including many first-time users. More than 150,000 homes across host cities were listed on Airbnb for the first time"; call: "**While bookings from any single event may be temporary**, the brand awareness, the trust, and new hosts these partners create benefit our business long after the event ends"; "there was no single product, there's no single partnership or initiative that explains our results"; no analyst asked to size it. Newsroom 6 Aug: "millions of guests from 196 nations", one in seven first-time users, average <$250/night | `data/raw/letters/2Q26_d70413dex991.htm`; `data/raw/transcripts/web/2Q26.html`; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` row 24 | 2026-08-06 | 2026-09-17 | yes |
| 5 | 4Q25 call: Doug Anmuth asked for "any tailwinds from major events like the World Cup and Olympics" inside the FY26 acceleration; Mertz listed drivers without a number. **The phrase "Major events ... expected to provide incremental but not primary growth" occurs only inside a site-generated `<li>` summary block of the mirrored transcript; it is not management's words** (A12-23) and is excluded from the size-language count | `data/raw/transcripts/web/4Q25.html` | 2026-02-12 | 2026-09-17 | yes |
| 6 | Event record coded (this log, `r15_v2_event_record.csv`): 8 event discussions 1Q24–2Q26, 0 with a points figure (Laplace 0.10 per discussion); **qualifying size language 2 of 8** ("insignificant", 1Q24; "relatively small", 2Q24 — both about Paris, both in the run-up / own-quarter slots); "may be temporary" (2Q26) is duration, not size. **By slot: run-up / own-quarter discussions 2 of 5 with size language (Paris 1Q24, 2Q24 yes; World Cup 4Q25 preview, 1Q26, 2Q26 no); post-event / lap discussions 0 of 3 (3Q24, 4Q24, 3Q25).** The two remaining prints for this question (5 Nov, Feb) are both post-event slots | `datasets/r15_v2_event_record.csv` | 2026-09-17 | 2026-09-17 | yes |
| 7 | What management does quantify in points: calendar (Easter, Leap Day), FX (every guide), the Middle East conflict ("roughly 100bps headwind", 1Q26 guide; "approximately 10%" ex-conflict), and the product bundle twice (4Q25, 1Q26) before dropping it; product/driver attributions in points appear in 2 of 23 prints; 37 declines to quantify in 23 calls; "seats booked today are indeed immaterial" (2Q25, Trevor Young) and "hotels are only a single-digit percent of nights booked ... a relatively small segment" (2Q26) are the two size-language declines on record outside events | C05 log claims 5–8; R08 log claim 10; `data/processed/abnb_declined_to_quantify.csv` rows 25, 27, 34 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Team view of the World Cup: a bookings event in 1Q/2Q26 (helping 2Q26's 10.3%), a revenue event in 2Q/3Q26, a 2Q27/3Q27 comparison problem; bridge overlay +0.5pt in 2Q26; "Airbnb never sized its own benefit, which cuts both ways: nothing to lap on paper, and nothing to point to if 2Q27 nights decelerate"; the memo uses the unsized event as a bear point ("an unsized event is one you cannot lap on paper"). **The team's numeric path already carries only +0.5pt, so a confirming disclosure changes no line of the model** (A12-24) | `research/notes/overnight/10_regional-and-segment-decomposition.md` (World Cup section); `05_macro-outlook-and-transmission.md` §4.6; `deck/drafts/memo_v2_short_2026-09-16.md` (debate items 1–2) | 2026-09-06 to 2026-09-16 | 2026-09-17 | yes |
| 9 | Outside evidence the event was small: US international arrivals in the group stage +0.2% y/y; CoStar host-city hotel bookings +0.5%; Tourism Economics' World Cup lift +1.7% of US hotel RevPAR in June–July, +0.4% full-year; Marriott ~45bp of FY global RevPAR; STR June 2027 RevPAR −0.8% on the comp | `05_macro-outlook-and-transmission.md` §4.5–4.6; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` row 55; R11 log claim 2 | 2026-08-10 to 2026-09-09 | 2026-09-17 | no |
| 10 | Sibling disclosure objects (comparisons, not an anchor — they share this log's 23-print record: A12-22): **C05 revision 2 P(any bundle points figure at 5 Nov) 0.28, anchor null**; R08 P(a forward ≥1pt lever quantified by Feb) 0.15; R09 0.25; C05's metric-persistence base rate: a dropped metric returns 0.22–0.27 | `bundle-attribution-quantified/forecasts/2026-09-17-forecast.json` (rev 2); R08 log §6; R09 log §6 | 2026-09-17 | 2026-09-17 | no |
| 11 | Chesky at Goldman 8 Sep 2026 did not mention the World Cup (conference remarks would not count in any case, convention 1) | `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` V017–V026; R08 log claim 4 | 2026-09-08 | 2026-09-17 | no |
| 12 | No market prices any Airbnb disclosure (batch-shared Polymarket/Kalshi pulls) | C05 log claim 15; R16 log claim 10 | 2026-09-17 | 2026-09-17 | no |
| 13 | Final 72-hour recency check (batch-shared, R01/F01 "Airbnb news" passes of 17 Sep and R10's FOMC query): no Airbnb statement on the World Cup since the 6 Aug newsroom post | R01 log claim 23; F01 log claim 13 | 2026-09-17 | 2026-09-17 | no |
| 14 | The 5 Nov attribution ask is likelier than not: R01 revision 2 puts P(3Q26 print < 10.0%) at 0.61 and the team's base case is a decelerating Q3; sell-side previews naming a "World Cup air pocket" would make the ask near-certain (monitoring row 2) | `risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json` | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 2Q26 letter and call (6 Aug 2026, 42 days old) — the last management statement on the event; the next inputs are the 5 Nov and Feb prints.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs C05, R08, F01, R01
2. [repo, python] regex extraction of every event passage from `data/raw/letters/*.htm` and `data/raw/transcripts/web/*.html` (World Cup, Olympic, Euro Cup, eclipse, Super Bowl, Coachella, Taylor Swift) → `sources/event_passages_letters_transcripts_extract.txt`
3. [repo, python] targeted read of the 2Q26, 4Q25, 3Q25 transcripts for "World Cup" in prepared remarks and Q&A (analyst asks and answers)
4. [repo, python] scan of all letters and calls for "not material | immaterial | not meaningful | relatively small | may be temporary" within 300 characters of an event word (two hits: 2Q24 letter Paris, 2Q26 call World Cup)
5. [repo, pandas] `data/processed/abnb_declined_to_quantify.csv` (categories; size-language answers)
6. [repo] `research/notes/overnight/10_regional-and-segment-decomposition.md` World Cup section; `05_macro-outlook-and-transmission.md` §4.5–4.6; `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §4; `research/notes/2026-09-04_abnb-pitch-landscape.md` (debate items); `deck/drafts/memo_v2_short_2026-09-16.md` (World Cup lines)
7. [repo] grep "World Cup" in `05_mgmt_statements_v2/05_statements.csv`, `q3nowcast/G/intra_quarter_commentary.csv`, `overnight2/D/rnpl_statement_ledger.csv`, `research/notes/q3nowcast/G_external-sources-q3-read.md`
8. [computed] `datasets/r15_model.py` (revision 1)
9. (no WebSearch charged to R15; the batch's recency passes are cited in claim 13)
10. [revision 2, repo, python] re-scan of all 23 letters and 28 mirrored transcripts for the seven event words within 320 characters of {basis point, percentage point, points of, immaterial, not material, not meaningful, relatively small, may be temporary, **single city**}: hits = 1Q24 letter ("insignificant"), 2Q24 letter ("relatively small"), 2Q26 call ("may be temporary"); the 4Q25 "incremental but not primary growth" phrase located inside an escaped `<li>` block only
11. [revision 2, repo] `audits/A12-research-audit.md`; `audits/A12-reproduce.py` run; `bundle-attribution-quantified/forecasts/2026-09-17-forecast.json` (rev 2); `risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`
12. [revision 2, computed] `datasets/r15_model_v2.py`

## 3. Leading Hypothesis Entities
Airbnb, Brian Chesky, Ellie Mertz, FIFA World Cup 2026, Paris 2024 Olympics, 3Q26 shareholder letter, 4Q26 shareholder letter, February 2027 call

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Management never sizes events in points (0 of 8) and keeps the superlative framing for the World Cup; question resolves No | leading (≈0.82) | claims 1–6; the incentive on events is marketing (guests, listings, brand), and a small number would undercut "largest event in Airbnb's history" |
| **The slot argument (A12-09): the only precedents for size language are the run-up / own-quarter letters (Paris 1Q24, 2Q24); the World Cup's three equivalent slots have passed without it, and the one lap precedent (3Q25) chose "headwind" over "small"** | **the reason the record rate is cut** | post-event record 0 of 3 for Paris; the World Cup's pre/own record 0 of 3 says management's framing of this event is superlative-only; the highest-hazard print is spent |
| Management defuses the 2Q27 comp in February by calling the World Cup "not a meaningful driver" | kept, main Yes route (B_feb 0.08) | the incentive lines up (the Feb letter carries the FY27 outlook and the 2Q27 comp before the May guide) and the vocabulary exists (1Q24/2Q24); against it, 3Q25's lap sentence was a headwind, not nothing |
| A quantified ≤1pt lap headwind in the Feb FY27 framing ("about a point in Q2") | kept (A_feb 0.04) | management quantified the Middle East drag in a next-quarter guide but has never put a number on a lap (RNPL laps were "tougher comps", qualitative); the Q2 guide comes in May 2027, after resolution |
| A 5 Nov figure for the World Cup's 2Q/3Q26 contribution (≤1pt) | kept, small (A_nov 0.02) | the bundle figure was dropped in 2Q26 with "no single product"; a World Cup figure would re-open the attribution the company just closed |
| "Not a meaningful driver" said in 5 Nov Q&A when an analyst attributes the 3Q26 deceleration to the World Cup air pocket | kept (B_nov 0.06) | the ask is likelier than not (claim 14); management's size-language declines on record (seats "immaterial", hotels "relatively small", Paris "insignificant") show the phrase is in its vocabulary |
| A figure >1pt ("the World Cup added roughly 2 points to Q2") | priced as No (A routes 0 → 0.14) | would be a superlative-consistent number; equally unprecedented |
| "Bookings from any single event may be temporary" repeated, counted by a lenient resolver | priced in §7 (lenient: 0.28), not in the headline | convention 3: duration, not size |
| Apply the Paris pre/own-quarter rate (2 of 5) to the two remaining prints | discarded | the remaining prints are post-event slots, where the record is 0 of 3; it would give 0.66 (§7) and ignore the spent slot |

## 5. Independent Estimates
- base_rate_estimate: 0.23 — built from the coded record, not from a formula: size language 2 of 8 event discussions (raw 0.25 per discussion; over two prints 0.44 raw, 0.51 Laplace — the audit's A12-08 arithmetic, which is what the record says before any slot conditioning); conditioned on the slot the two remaining prints occupy (post-event: 0 of 3 for Paris, shrunk toward the pooled 2 of 8 with a prior weight of two discussions → 0.10 per print → 0.19 over two prints), plus a never-observed points route priced at 0.02 / 0.03 → 0.23 (claim 6, `r15_v2_base_rate.csv`). Revision 1's "1 − (0.95)² ≈ 0.10" is withdrawn: it used a per-print 0.05 that neither cited input produced
- decomposition_estimate: 0.19 — four routes in `r15_v2_tree.csv`: a ≤1pt figure at 5 Nov 0.02, at Feb 0.04; an immaterial/not-meaningful statement at 5 Nov 0.06 (ask likelier than not, claim 14), at Feb 0.08 (the FY27-outlook incentive); 1 − Π(1 − p) = 0.186; 5 Nov print 0.08, Feb print 0.12
- anchor_estimate: null — no market and no external forecast prices this disclosure (claim 12); NO_EXTERNAL_ANCHOR. Sibling comparisons, labelled as such (claim 10): C05 rev 2 0.28 (a backward points figure for an existing product at one print, where a figure had been given twice before), R09 0.25, R08 0.15 (a forward quantified lever by Feb). The World Cup has never had a figure, which cuts below C05; the "immaterial" route adds a second door, which lifts above R08
- anchor_value: null (NO_EXTERNAL_ANCHOR; three-estimate requirement unmet; |final − anchor| not reported)
- final_estimate: 0.18 (credible interval 0.10–0.30)
- final_minus_anchor: n/a. NOT_INDEPENDENTLY_DERIVED flag noted: the base rate and the tree are built from the same eight event discussions. The final sits between the tree (0.19) and the strict-resolver reading (0.12) rather than at the slot-conditioned base rate (0.23) because convention 3 is strict: a statement has to be about the size of the contribution to growth, and two of the three vocabulary precedents ("insignificant to the total nights booked in a region", "relatively small compared to the total nights booked in a region") are about a city's share of a region's nights, which a strict resolver could read as not being about the growth rate at all. Audit A12's independent number is 0.18 (0.10–0.30); this revision agrees with it and with its reasoning

## 6. Final Numbers
**Binary.** P(Yes) = **0.18**, credible interval **0.10–0.30**.
Split: 5 Nov print ≈ 0.08 (a ≤1pt figure 0.02, immaterial language 0.06); Feb print ≈ 0.12 (0.04 / 0.08), overlap removed. Under a lenient resolver (duration / "relatively small"-style language counts): 0.28; strict (explicit growth-rate immateriality only): 0.12.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Rows from `datasets/r15_v2_sensitivity.csv`.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 3 (size language about the growth contribution only) | lenient resolver counts "may be temporary" / "relatively small" repeats: 0.28; strict (explicit "not material/meaningful to growth" only): 0.12 |
| Management keeps laps qualitative (Feb points 0.04) | management turns numeric on the 2027 laps (0.10): 0.24 |
| 5 Nov ask likelier than not (Nov routes 0.02 / 0.06) | 3Q26 decelerates sharply and analysts press (Nov routes doubled): 0.25; 3Q26 accelerates, no pressure (halved): 0.15 |
| A World Cup figure, if given, is ≤1pt | any figure is >1pt (A routes 0): 0.14 |
| Post-event slot conditioning (0 of 3) | Paris pre/own-quarter rate (2 of 5 = 0.40 per print) applied to both prints: 0.66 — the number the slot argument rules out |
| Conference remarks excluded (convention 1) | included: +0.01 (Chesky did not mention the event at Goldman) |
| Joint bull (lenient, numeric, pressed) | 0.38 |
| Joint bear (strict, no numbers, no ask) | 0.09 |

Pre-mortem ("it is 11 Feb 2027 and the letter says the World Cup was 'not a meaningful contributor to our growth rate'"): (1) management wanted the 2Q27 comp defused before the May guide and used the 1Q24/2Q24 Paris vocabulary — the main priced route (B_feb); (2) the 3Q26 print decelerated, an analyst blamed the World Cup air pocket, and Mertz answered "the World Cup was never a meaningful driver of the quarter" — priced (B_nov); (3) the Feb letter's FY27 outlook carried "a roughly 50 basis point headwind in Q2 from the World Cup comparison" — priced (A_feb 0.04), and the memo would have to note that a quantified lap is more than the company has ever given for an event. ("It said nothing sized"): the modal case (0.82): superlatives, guests, listings, "tougher comps in Q2" without a number — exactly what the 3Q25 Paris-lap letter did. Asymmetry: the memo's use of the World Cup is the "unsized event" tell; a Yes would remove the tell but also confirm the memo's own view that the event was small, so the pitch is indifferent to the number and the question matters for the narrative, not the model.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.18 (0.10–0.30); keep the "management has never sized an event" sentence, with the caveat that it called Paris "insignificant" (1Q24) and "relatively small" (2Q24) before and during the event, and said nothing of the kind after it |
| 2026-10-26 to 2026-11-04 | Sell-side previews naming the World Cup air pocket as a Q3 factor | Two or more previews doing so: +0.03 (raises the odds of a 5 Nov ask) |
| 2026-11-05 | 3Q26 letter, call, 10-Q | Resolve if a ≤1pt figure or size language appears; a >1pt figure → move to 0.03 (Feb would have to contradict it); a "tougher comps in 2Q27 against the World Cup" line without size → 0.12 (the 3Q25 pattern, which lowers the Feb "small" route); silence → 0.12 |
| 2027-01-15 to 2027-02-10 | Sell-side FY27 previews; any Airbnb newsroom World Cup retrospective with numbers | A newsroom figure in points: +0.05 (letter/call repetition still needed) |
| ~2027-02-11 | 4Q26 letter, call, 10-K | Resolve per conventions 1–4; read the FY27 outlook paragraph and the EMEA/NA regional sections for the lap language |

## 9. Impact
If Yes (management states the World Cup was ≤1pt or not meaningful): the memo's "unsized event" tell disappears, and the 2Q27/3Q27 lap in the team's FY27 path is confirmed small. **The team's numeric path already carries only +0.5pt of World Cup in 2Q26, so a confirming disclosure moves no line of the model; the revenue and margin rows are zero (A12-24)** — revision 1's +$20M / +0.01pp (itself mis-multiplied) is withdrawn.

| Item | Delta if R15 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a disclosure, not a booking |
| 4Q26 nights (pts) | 0 | as above |
| ADR (pts) | 0 | |
| 4Q26 revenue ($M) | 0 | |
| FY27 revenue ($M) | **0** (the bridge already carries a +0.5pt 2Q26 event and a small 2Q27 lap; a confirming statement changes no line) | claim 8 |
| FY26 adj. EBITDA margin (pp) | 0 | |
| FY27 adj. EBITDA margin (pp) | 0 | |
| FY27 EPS ($) | 0 | |
| Stock ($/share) | **+1** (narrative only: removes one bear talking point about 2027 comps; an explicitly narrative entry, not a model line) | judgement |
| **EV = P × impact** | **0.18 × $1 ≈ $0.2/share** | |
| Materiality | **Immaterial.** Drop from the risks list; keep the "management has never sized an event" sentence in the thesis text with the 1Q24/2Q24 Paris caveat | |

## 10. Revision notes
| Change | Finding | Effect |
|---|---|---|
| Base rate rebuilt from the coded record: record-implied 0.44 raw / 0.51 Laplace published, then slot-conditioned (post-event 0 of 3, shrunk to the pooled rate) to 0.19 + a points route → 0.23; the "1 − (0.95)²" line withdrawn | A12-08 | base rate 0.10 → 0.23 |
| The slot argument promoted to §4, §5 and the pre-mortem: the run-up / own-quarter slots produced the only size language (Paris), the World Cup's equivalents have passed silently, the lap precedent was a headwind | A12-09 | the reason the record rate is cut; tree re-priced (B_nov 0.05 → 0.06, B_feb 0.05 → 0.08) |
| Claim 1 and the event record gain the 1Q24 "insignificant to the total nights booked in a region" line: size language 2 of 8, not 1 of 8; convention 3 lists it | missed by the audit (its phrase list lacked "insignificant" / "single city") | strengthens A12-09: both precedents sit in the spent slots |
| Claim 5 / event record: the 4Q25 "incremental but not primary growth" phrase marked as a site summary bullet, excluded from the count | A12-23 | none on the count (it was never coded as size language) |
| Anchor set to null (NO_EXTERNAL_ANCHOR); C05 quoted at its revision-2 0.28; C05/R08/R09 labelled sibling comparisons; \|final − anchor\| not reported | A12-22 | anchor 0.20 → null |
| §9 revenue and margin rows set to 0; stock +$1 kept as an explicitly narrative entry; EV $0.15 → $0.18 | A12-24 | immaterial verdict unchanged |
| Claim 14 added (R01 rev 2: P(Q3 < 10) 0.61 makes the 5 Nov ask likelier than not); monitoring row 3 gives the 3Q25-pattern update | — | — |
| Final 0.14 → 0.18 (0.07–0.25 → 0.10–0.30) | A12-08/09 | +0.04 |

RESUME: the next agent should re-read the two Paris size-language sentences (claim 1) against convention 3 before 5 Nov and decide, in writing, whether "insignificant / relatively small compared to the total nights booked in a region" would resolve Yes if repeated for the World Cup (it is about a city's share of a region's nights, not the growth rate; this log treats a repeat as Yes under the lenient reading and No under the strict one, and prices both in §7). After 5 Nov apply monitoring row 3; the Feb "immaterial" route (B_feb 0.08) is the judgement to attack.
