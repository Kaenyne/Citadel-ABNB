# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A12 with R10, R11, R16). Reproduction: [datasets/r15_model.py](datasets/r15_model.py) (`py -3.13`, pure arithmetic; writes `r15_event_record.csv`, `r15_tree.csv`, `r15_sensitivity.csv`). Verbatim event passages from every letter and call: [sources/event_passages_letters_transcripts_extract.txt](sources/event_passages_letters_transcripts_extract.txt) (regex extract of "World Cup | Olympic | Euro Cup | eclipse | Super Bowl | Coachella | Taylor Swift" from `data/raw/letters/*.htm` and `data/raw/transcripts/web/*.html`).

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
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
By the Feb print, will management quantify the 2026 World Cup's contribution to nights or GBV at ≤1 point (or state it was not material)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if a letter or call gives a figure ≤1pt of nights or GBV, or says the contribution was immaterial/not meaningful to the growth rate. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted: (1) "letter or call" = the 3Q26 and 4Q26 shareholder letters, the two earnings calls (prepared remarks and Q&A), and the 10-Q/10-K text; investor-conference remarks do not count (priced in §7); (2) a figure counts whether stated as the 2Q26/3Q26 contribution ("roughly 1 point of Q2 nights") or as the 2027 lap ("about a 1-point headwind to Q2 2027"), in points or basis points of nights or GBV; a figure >1pt (e.g., "approximately 2 points") resolves No; a revenue-dollar figure resolves Yes only if it converts to ≤1pt of GBV at the trailing take rate; (3) "immaterial / not meaningful to the growth rate" requires a statement about the size of the World Cup's contribution to growth ("not a meaningful driver of Q2 growth", "not material to our growth rate", "relatively small compared to total nights"); the 2Q26 line "bookings from any single event may be temporary" does not count (it is about duration, not size), nor does a qualitative "tougher comparison" for 2Q27 (a headwind mention is the opposite of immaterial); (4) letter governs where letter and call differ; if only the call carries the statement, the call resolves.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Paris 2024 record, verbatim: 1Q24 letter "nights booked for stays during the dates of the Olympics are over five times higher ... Germany ... nearly double"; 2Q24 letter "nights booked in the Paris region for the dates of the event through Q2 were more than double ... Over the course of the Olympics, more than 400,000 guests"; 2Q24 letter (EMEA section) "**While the impact of a single city for a limited duration is relatively small compared to the total nights booked in a region**, we believe Airbnb is crucial..."; 3Q24 letter "a slight acceleration in growth of Nights and Experiences booked in EMEA ... buoyed by the Summer Olympic and Paralympic Games ... almost 700,000 guests ... supply of approximately 35%"; 4Q24 call "700,000 guests in Paris". No points figure in any of the four | `data/raw/letters/1Q24_d813800dex991.htm`, `2Q24_d831385dex991.htm`, `3Q24_d886752dex991.htm`; `data/raw/transcripts/web/2Q24.html`, `3Q24.html`, `4Q24.html` | 2024-05-08 to 2025-02-13 | 2026-09-17 | yes |
| 2 | Paris lap, 3Q25 letter (EMEA): "we faced a **slightly unfavorable year-over-year comparison** within the region due to the Paris Summer Olympic and Paralympic Games in 2024" — qualitative, no points | `data/raw/letters/3Q25_d40503dex991.htm` | 2025-11-06 | 2026-09-17 | yes |
| 3 | Milan 2026 and World Cup preview, 1Q26 letter/call: "nearly 200,000 guests ... supply in host markets grew approximately 30% ... GBV more than tripling" (host markets); "we expect to host more guests than at any event in Airbnb's history ... over 100,000 homes ... listed for the first time"; Q&A (Nick Jones, BNP): Mertz answered on booking patterns ("a lot of the booking activity happens close to the actual games"), supply retention ("in excess of half" of Paris event listings six months later), no size of the contribution | `data/raw/letters/1Q26_d23351dex991.htm`; `data/raw/transcripts/web/1Q26.html` | 2026-05-07 | 2026-09-17 | yes |
| 4 | World Cup, 2Q26 letter/call: "Airbnb hosted millions of guest arrivals during the tournament, including many first-time users. More than 150,000 homes across host cities were listed on Airbnb for the first time"; call: "**While bookings from any single event may be temporary**, the brand awareness, the trust, and new hosts these partners create benefit our business long after the event ends"; "there was no single product, there's no single partnership or initiative that explains our results"; no analyst asked to size it (World Cup appears only in prepared remarks and the summary). Newsroom 6 Aug: "millions of guests from 196 nations", one in seven first-time users, average <$250/night | `data/raw/letters/2Q26_d70413dex991.htm`; `data/raw/transcripts/web/2Q26.html`; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` row 24 | 2026-08-06 | 2026-09-17 | yes |
| 5 | 4Q25 call: Doug Anmuth asked for "any tailwinds from major events like the World Cup and Olympics" inside the FY26 acceleration; Mertz listed drivers without a number; the call summary reads "Major events ... expected to provide incremental but not primary growth" | `data/raw/transcripts/web/4Q25.html` | 2026-02-12 | 2026-09-17 | yes |
| 6 | Event record coded (this log): 8 event discussions 1Q24–2Q26, 0 with a points figure (Laplace 0.10 per discussion); size language twice: "relatively small compared to the total nights booked in a region" (2Q24, Paris) and "may be temporary" (2Q26, World Cup) | `datasets/r15_event_record.csv` | 2026-09-17 | 2026-09-17 | yes |
| 7 | What management does quantify in points: calendar (Easter, Leap Day), FX (every guide), the Middle East conflict ("roughly 100bps headwind", 1Q26 guide; "approximately 10%" ex-conflict), and the product bundle twice (4Q25, 1Q26) before dropping it; product/driver attributions in points appear in 2 of 23 prints; 37 declines to quantify in 23 calls; "seats booked today are indeed immaterial" (2Q25, Trevor Young) and "hotels are only a single-digit percent of nights booked ... a relatively small segment" (2Q26) are the two size-language declines on record | C05 log claims 5–8; R08 log claim 10; `data/processed/abnb_declined_to_quantify.csv` rows 25, 27, 34 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Team view of the World Cup: a bookings event in 1Q/2Q26 (helping 2Q26's 10.3%), a revenue event in 2Q/3Q26, a 2Q27/3Q27 comparison problem; bridge overlay +0.5pt in 2Q26; "Airbnb never sized its own benefit, which cuts both ways: nothing to lap on paper, and nothing to point to if 2Q27 nights decelerate"; the memo uses the unsized event as a bear point ("an unsized event is one you cannot lap on paper") | `research/notes/overnight/10_regional-and-segment-decomposition.md` (World Cup section); `05_macro-outlook-and-transmission.md` §4.6; `deck/drafts/memo_v2_short_2026-09-16.md` (debate items 1–2) | 2026-09-06 to 2026-09-16 | 2026-09-17 | yes |
| 9 | Outside evidence the event was small: US international arrivals in the group stage +0.2% y/y; CoStar host-city hotel bookings +0.5%; Tourism Economics' World Cup lift +1.7% of US hotel RevPAR in June–July, +0.4% full-year; Marriott ~45bp of FY global RevPAR; STR June 2027 RevPAR −0.8% on the comp | `05_macro-outlook-and-transmission.md` §4.5–4.6; `data/processed/q3nowcast/G/intra_quarter_commentary.csv` row 55; R11 log claim 2 | 2026-08-10 to 2026-09-09 | 2026-09-17 | no |
| 10 | Sibling disclosure objects: C05 P(any points figure for the bundle at 5 Nov) 0.27; R08 P(a forward ≥1pt lever quantified by Feb) 0.15; C05's metric-persistence base rate: a dropped metric returns 5/19 | C05 log §6; R08 log §6 | 2026-09-17 | 2026-09-17 | yes |
| 11 | Chesky at Goldman 8 Sep 2026 did not mention the World Cup (conference remarks would not count in any case, convention 1) | `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` V017–V026; R08 log claim 4 | 2026-09-08 | 2026-09-17 | no |
| 12 | No market prices any Airbnb disclosure (batch-shared Polymarket/Kalshi pulls) | C05 log claim 15; R16 log claim 10 | 2026-09-17 | 2026-09-17 | no |
| 13 | Final 72-hour recency check (batch-shared, R01/F01 "Airbnb news" passes of 17 Sep and R10's FOMC query): no Airbnb statement on the World Cup since the 6 Aug newsroom post | R01 log claim 23; F01 log claim 13 | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 2Q26 letter and call (6 Aug 2026, 42 days old) — the last management statement on the event; the next inputs are the 5 Nov and Feb prints.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs C05, R08, F01, R01
2. [repo, python] regex extraction of every event passage from `data/raw/letters/*.htm` and `data/raw/transcripts/web/*.html` (World Cup, Olympic, Euro Cup, eclipse, Super Bowl, Coachella, Taylor Swift) → `sources/event_passages_letters_transcripts_extract.txt`
3. [repo, python] targeted read of the 2Q26, 4Q25, 3Q25 transcripts for "World Cup" in prepared remarks and Q&A (analyst asks and answers)
4. [repo, python] scan of all letters and calls for "not material | immaterial | not meaningful | relatively small | may be temporary" within 300 characters of an event word (two hits: 2Q24 letter Paris, 2Q26 call World Cup)
5. [repo, pandas] `data/processed/abnb_declined_to_quantify.csv` (categories; size-language answers)
6. [repo] `research/notes/overnight/10_regional-and-segment-decomposition.md` World Cup section; `05_macro-outlook-and-transmission.md` §4.5–4.6; `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §4; `research/notes/2026-09-04_abnb-pitch-landscape.md` (debate items); `deck/drafts/memo_v2_short_2026-09-16.md` (World Cup lines)
7. [repo] grep "World Cup" in `05_mgmt_statements_v2/05_statements.csv`, `q3nowcast/G/intra_quarter_commentary.csv`, `overnight2/D/rnpl_statement_ledger.csv`, `research/notes/q3nowcast/G_external-sources-q3-read.md`
8. [computed] `datasets/r15_model.py`
9. (no WebSearch charged to R15; the batch's recency passes are cited in claim 13)

## 3. Leading Hypothesis Entities
Airbnb, Brian Chesky, Ellie Mertz, FIFA World Cup 2026, Paris 2024 Olympics, 3Q26 shareholder letter, 4Q26 shareholder letter, February 2027 call

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Management never sizes events in points (0 of 8) and keeps the superlative framing; question resolves No | leading (≈0.85) | claims 1–6; the incentive on events is marketing (guests, listings, brand), and a small number would undercut "largest event in Airbnb's history" |
| Management defuses the 2Q27 comp in February by calling the World Cup "not a meaningful driver" | kept, main Yes route (B_feb 0.05) | precedent: 2Q24's "relatively small compared to the total nights booked in a region" for Paris; but the 3Q25 lap was framed as a "slightly unfavorable comparison", i.e. as a headwind, not as nothing |
| A quantified ≤1pt lap headwind in the Feb FY27 framing ("about a point in Q2") | kept (A_feb 0.04) | management quantified the Middle East drag in a next-quarter guide but has never put a number on a lap (RNPL laps were "tougher comps", qualitative); the Q2 guide comes in May 2027, after resolution |
| A 5 Nov figure for the World Cup's 2Q/3Q26 contribution (≤1pt) | kept, small (A_nov 0.02) | the bundle figure was dropped in 2Q26 with "no single product"; a World Cup figure would re-open the attribution the company just closed |
| "Not a meaningful driver" said in 5 Nov Q&A when an analyst attributes the 3Q26 deceleration to the World Cup air pocket | kept (B_nov 0.05) | plausible if Q3 decelerates and the question is asked; management's two size-language declines on record (seats "immaterial", hotels "relatively small") show the phrase exists in its vocabulary |
| A figure >1pt ("the World Cup added roughly 2 points to Q2") | priced as No (A routes 0 → 0.10) | would be a superlative-consistent number; equally unprecedented |
| "Bookings from any single event may be temporary" repeated, counted by a lenient resolver | priced in §7 (lenient: 0.24), not in the headline | convention 3: duration, not size |

## 5. Independent Estimates
- base_rate_estimate: 0.10 — event discussions with a points figure 0 of 8 (Laplace 0.10 per discussion, claim 6); size-language statements about an event's growth contribution 1 of 8 (2Q24); two prints in the window with at most one World Cup discussion each → P(points ≤1pt or size language) ≈ 1 − (0.95)² ≈ 0.10, no regime adjustment (the 2026 numeric turn was about the bundle, and was reversed in 2Q26)
- decomposition_estimate: 0.15 — four routes in `r15_tree.csv`: a ≤1pt figure at 5 Nov 0.02, at Feb 0.04; an immaterial/not-meaningful statement at 5 Nov 0.05, at Feb 0.05; 1 − Π(1 − p) = 0.151
- anchor_estimate: 0.20 — no market (claim 12); the sibling objects are C05's 0.27 (a backward points figure for an existing product at one print, where a figure had been given twice before) and R08's 0.15 (a forward quantified lever by Feb); the World Cup has never had a figure, which cuts below C05, and the "immaterial" route adds a second door, which lifts above R08
- anchor_value: 0.20 (sibling-object construction; NO external anchor)
- final_estimate: 0.14 (credible interval 0.07–0.25)
- final_minus_anchor: −6 points. NOT_INDEPENDENTLY_DERIVED flag noted: the anchor is a construction from sibling logs, not a market; the base rate and the tree are built from the same eight event discussions. The final sits between the record (0.10) and the tree (0.15) because the tree's Feb "immaterial" route is the one place the incentive (defusing the 2Q27 comp) and the vocabulary (2Q24's "relatively small") line up, and the record has only one such instance in eight

## 6. Final Numbers
**Binary.** P(Yes) = **0.14**, credible interval **0.07–0.25**.
Split: 5 Nov print ≈ 0.07 (a ≤1pt figure 0.02, immaterial language 0.05); Feb print ≈ 0.08 (0.04 / 0.05), overlap removed. Under a lenient resolver (duration/"relatively small"-style language counts): 0.24; strict (explicit growth-rate immateriality only): 0.11.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Rows from `datasets/r15_sensitivity.csv`.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 3 (size language only) | lenient resolver counts "may be temporary" / "relatively small" repeats: 0.24; strict (explicit "not material/meaningful to growth" only): 0.11 |
| Management keeps laps qualitative (Feb points 0.04) | management turns numeric on the 2027 laps (0.10): 0.20 |
| 3Q26 in line; no attribution pressure on 5 Nov | 3Q26 decelerates sharply and analysts press (Nov routes doubled): 0.21 |
| A World Cup figure, if given, is ≤1pt | any figure is >1pt (A routes 0): 0.10 |
| Conference remarks excluded (convention 1) | included: +0.01 (Chesky did not mention the event at Goldman) |
| Joint bull (lenient, numeric, pressed) | 0.33 |
| Joint bear (strict, no numbers) | 0.07 |

Pre-mortem ("it is 11 Feb 2027 and the letter says the World Cup was 'not a meaningful contributor to our growth rate'"): (1) management wanted the 2Q27 comp defused before the May guide and used the 2Q24 Paris vocabulary — the main priced route (B_feb); (2) the 3Q26 print decelerated, an analyst blamed the World Cup air pocket, and Mertz answered "the World Cup was never a meaningful driver of the quarter" — priced (B_nov); (3) the Feb letter's FY27 outlook carried "a roughly 50 basis point headwind in Q2 from the World Cup comparison" — priced (A_feb 0.04), and the memo would have to note that a quantified lap is more than the company has ever given for an event. ("It said nothing sized"): the modal case (0.86): superlatives, guests, listings, "tougher comps in Q2" without a number. Asymmetry: the memo's use of the World Cup is the "unsized event" tell; a Yes would remove the tell but also confirm the memo's own view that the event was small, so the pitch is indifferent to the number and the question matters for the narrative, not the model.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.14 (0.07–0.25); keep the "unsized event" line, with the caveat that management called Paris "relatively small" in 2024 |
| 2026-10-26 to 2026-11-04 | Sell-side previews naming the World Cup air pocket as a Q3 factor | Two or more previews doing so: +0.03 (raises the odds of a 5 Nov ask) |
| 2026-11-05 | 3Q26 letter, call, 10-Q | Resolve if a ≤1pt figure or size language appears; a >1pt figure → move to 0.03 (Feb would have to contradict it); a "tougher comps in 2Q27 against the World Cup" line without size → 0.10; silence → 0.09 |
| 2027-01-15 to 2027-02-10 | Sell-side FY27 previews; any Airbnb newsroom World Cup retrospective with numbers | A newsroom figure in points: +0.05 (letter/call repetition still needed) |
| ~2027-02-11 | 4Q26 letter, call, 10-K | Resolve per conventions 1–4; read the FY27 outlook paragraph and the EMEA/NA regional sections for the lap language |

## 9. Impact
If Yes (management states the World Cup was ≤1pt or not meaningful): the memo's "unsized event" tell disappears, and the 2Q27/3Q27 lap in the team's FY27 path is confirmed small (the bridge already carries only +0.5pt in 2Q26).

| Item | Delta if R15 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a disclosure, not a booking |
| 4Q26 nights (pts) | 0 | as above |
| ADR (pts) | 0 | |
| 4Q26 revenue ($M) | 0 | |
| FY27 revenue ($M) | **+20** (a confirmed ≤1pt lap vs the memo's rhetorical "World Cup laps in 2Q27": +0.1–0.15pt of FY27 nights × $158M; the team's numeric path barely moves because it already carries +0.5pt in one quarter) | claim 8; brief |
| FY26 adj. EBITDA margin (pp) | 0 | |
| FY27 adj. EBITDA margin (pp) | +0.01 | 0.66 × 0.13 |
| FY27 EPS ($) | +0.00 | |
| Stock ($/share) | **+1** (narrative only: removes one bear talking point about 2027 comps; 0.13pt × $4.90 = $0.6 on the joint solve, rounded up for the narrative) | brief; judgement |
| **EV = P × impact** | **0.14 × $1 ≈ $0.15/share** | |
| Materiality | **Immaterial.** Drop from the risks list; keep the "management has never sized an event" sentence in the thesis text with the 2Q24 "relatively small" caveat | |

RESUME: the next agent (audit response) should check claim 1's four Paris quotes and claim 4's 2Q26 quotes against the raw letters/transcripts (the extract file has them), re-run `datasets/r15_model.py`, and attack the two judgement routes: B_feb 0.05 (the incentive-to-defuse route) and the convention-3 line between "relatively small" (counts) and "may be temporary" (does not), which moves the number between 0.11 and 0.24.
