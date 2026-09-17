# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A15 (B04, B05, B06, B07). Reproduction: the base rate is the count in `datasets/letter_geopolitical_base_rate_4Q20-2Q26.csv`; the decomposition is the two-line mixture in section 5.

## 0. Metadata
- question_name: bonus-geopolitical-headwind-cited
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B06)
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
- batch: A15

## 0b. Question (verbatim)
### Title
At the 5 Nov print, will management cite the Middle East conflict or another geopolitical event as a headwind to 3Q26 or 4Q26 nights of ≥0.5 point, or as a named reason for the 4Q26 guide?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on a quantified drag ≥0.5pt or an explicit attribution in the guide paragraph. Resolution 5 Nov 2026.
### Fine Print
None beyond the resolution sentence. Conventions adopted (each priced in section 5 and section 7):
1. Leg 1 (quantified drag) requires a number or a number-word for the effect on 3Q26 or 4Q26 nights (or Nights and Seats Booked): "approximately 100 basis points", "roughly half a point", "about one point of growth". "Slightly", "modestly" or "some cancellations" without a magnitude do not satisfy leg 1.
2. Leg 2 (named reason for the 4Q26 guide) requires the conflict or another geopolitical event to appear in the letter's Q4 2026 outlook paragraph (or, if the letter is silent, in the CFO's prepared Q4 outlook remarks) as a factor in or assumption behind the guide: e.g. "assuming a continued headwind from the conflict in the Middle East", "given geopolitical uncertainty we expect nights growth to moderate", "closely monitoring geopolitical conflicts that may impact travel demand" tied to the Q4 expectation (the 3Q23 construction counts). A generic risk-factor sentence elsewhere in the letter, the forward-looking-statements boilerplate, and the 10-Q's "macroeconomic and geopolitical conditions" paragraph do not count.
3. A negation ("we are not assuming any significant impact from the conflict", the 2Q26 call construction) names the conflict but does not attribute a headwind to it and resolves No. This is the most likely resolver dispute and is priced at 0.05.
4. "Another geopolitical event" includes a new war, a terror attack with travel effects, sanctions or airspace closures; it excludes tariffs, visa policy and macro conditions.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 1Q26 letter (7 May 2026): "Nights and Seats Booked grew over 9% year-over-year, despite increased cancellations from the Middle East conflict. Absent the impact of the conflict, we estimate growth ... would have been approximately 10%"; Q2 guide: "we expect Nights and Seats booked growth to slightly decelerate ... assuming an estimated roughly 100bps headwind related to the conflict in the Middle East"; FY paragraph: "even as we face ... current headwinds from the Middle East conflict" | sources/letters_calls_geopolitical_passages_4Q20-2Q26.txt; data/raw/letters/1Q26_d23351dex991.htm | 2026-05-07 | 2026-09-17 | yes |
| 2 | 2Q26 letter (6 Aug 2026): the Outlook section (verbatim in sources) contains no geopolitical reference; EMEA paragraph: "Following the headwinds we saw last quarter related to the ongoing conflict in the Middle East, we've observed a steady recovery of demand trends within the region"; call (Mertz): "the impact to our business from the conflict was less than we had anticipated" and "In Q3, we are not assuming any significant impact related to the conflict in the Middle East" | sources/letters_calls_geopolitical_passages_4Q20-2Q26.txt; data/raw/letters/2Q26_d70413dex991.htm; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 3 | Base rate across 23 letters (4Q20-2Q26): 8 prints had a major conflict active in the quarter (1Q22-4Q22 Ukraine, 3Q23-4Q23 Israel, 1Q26-2Q26 Iran); the outlook paragraph named it as a headwind or risk in 3 of 8 (1Q22 risk list; 3Q23 "closely monitoring ... geopolitical conflicts ... we currently expect our nights booked growth in Q4 2023 to moderate"; 1Q26 quantified); quantified ≥0.5pt in 1 of 8; unconditional 3 of 23 | datasets/letter_geopolitical_base_rate_4Q20-2Q26.csv; sources/letters_calls_geopolitical_passages_4Q20-2Q26.txt | 2026-08-06 | 2026-09-17 | yes |
| 4 | Ledger D042: the 1Q26 conflict headwind is the only cancellation shock Airbnb has ever sized in growth points; the 2Q26 letter dropped it once the effect faded | data/processed/overnight2/D/rnpl_statement_ledger.csv (D042); docs/pitch-forecasts/questions/rnpl-negative-effect-acknowledged/research-log.md claim 5 | 2026-05-07 | 2026-09-17 | yes |
| 5 | Conflict state, 16 Sep 2026: war since 28 Feb 2026; ceasefire 8 Apr-8 Jul; attacks resumed 28 Aug; US strikes on IRGC targets and tankers 1-9 Sep; 20 Iranian missiles at Jordan 8-9 Sep; seven days without Iranian launches through 16 Sep; Hormuz largely closed (4 commodity transits 15 Sep vs 18 average; 103 vessels redirected); Oman-hosted Gulf-Iran meeting postponed; Iran: "No talks until Iran's conditions are met"; Brent $108.75, dated Brent > $130 | sources/web_fetch_notes_2026-09-17.md (globalsecurity.org, updated 2026-09-16) | 2026-09-16 | 2026-09-17 | yes |
| 6 | Aviation: EASA conflict-zone warnings over Bahrain, Kuwait, Qatar, UAE extended to 30 Sep 2026; BA suspended London-Dubai/Abu Dhabi to 25 Oct; KLM suspended Riyadh, Dammam, Dubai to 24 Oct; Virgin London-Dubai through winter; 490 delays / 70 cancellations at Gulf hubs on 14 Sep; Middle Eastern carriers −14% passenger demand; Europe-Asia traffic +11% | sources/web_fetch_notes_2026-09-17.md (search snippets; Al Jazeera 2026-08-06) | 2026-09-14 | 2026-09-17 | yes |
| 7 | Demand redistribution rather than destruction: European travellers substituting Italy, Spain, Greece, Norway for long-haul via the Gulf (TUI, Trailfinders); Sri Lanka bookings −20-30% | sources/web_fetch_notes_2026-09-17.md (Al Jazeera 2026-08-06) | 2026-08-06 | 2026-09-17 | no |
| 8 | Peers: Booking's Q3 assumptions include "softer long-haul international travel demand persisting" and "pressure on inbound travel to the Middle East" (4 Aug); Booking CFO 9 Sep: direct impact "starting to normalize"; Marriott Middle East RevPAR −43% in Q2, −12% in July; Hyatt: the conflict cost ~110bp of total RevPAR growth in Q2 | data/processed/q3nowcast/G/intra_quarter_commentary.csv; research/notes/overnight/05_macro-outlook-and-transmission.md §4.5 | 2026-09-09 | 2026-09-17 | yes |
| 9 | Macro-transmission finding: "the largest airfare shock since 2022 coincided with the fastest nights growth in two years" (2Q26 +10.3%); Airbnb's nights have absorbed every macro and geopolitical shock since 2022 within a 7-12% band; the risk is in the wording, not the KPI | research/notes/overnight/05_macro-outlook-and-transmission.md (composite lesson) | 2026-09-05 | 2026-09-17 | yes |
| 10 | Consumer-strength split: 3Q26 to date EMEA +0.16 z (strongest region), NA −0.30; the C workstream flags EMEA as the relative loser only through a fitted sign it does not trust | research/notes/overnight2/C_consumer-relative-strength-regional-split.md §1 | 2026-09-11 | 2026-09-17 | no |
| 11 | Team 3Q26 nights nowcast +9.5% (band 8.5-10.0) against a "low double-digit" guide; P(4Q26 bucket ≤ "high single digits") = 0.61 (C02 rev 2); a deceleration guide raises the value to management of an external, quantifiable cause | docs/pitch-forecasts/00_BRIEF.md rule 6; docs/pitch-forecasts/questions/q4-nights-bucket/forecasts/2026-09-17-forecast.json | 2026-09-17 | 2026-09-17 | yes |
| 12 | Polymarket (2026-09-17T08:21:26Z): P(no US-Iran diplomatic meeting by 30 Sep) 0.9355; P(final nuclear deal by 31 Dec) 0.105, by 30 Nov 0.055; the conflict is priced as still unresolved at the 5 Nov print with ≈ 0.85-0.90 | sources/polymarket_search_Iran_ceasefire_20260917T082126Z.json; sources/web_fetch_notes_2026-09-17.md | 2026-09-17 | 2026-09-17 | yes |
| 13 | The 2Q26 10-Q MD&A already carries "The conflict in the Middle East has had and may continue to have an impact on booking trends. To date, these conditions have not had a material impact" — boilerplate that does not count under convention 2 | data/raw/regulatory/quantification/abnb_2026q2_10q.html | 2026-08-06 | 2026-09-17 | no |
| 14 | Final 72-hour name-free check (17 Sep): Iran PGSA vessel blacklist; US-escorted transits rising; drone shot down over Hormuz; Oman meeting postponed; no ceasefire; nothing that changes the number | sources/web_fetch_notes_2026-09-17.md (query 3) | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] regex extraction of "Middle East|geopolit|conflict|war|Ukraine|Israel|Iran" from all 23 letters and 22 call mirrors, saved to sources/letters_calls_geopolitical_passages_4Q20-2Q26.txt (with the 1Q22, 3Q23, 1Q26 and 2Q26 outlook paragraphs verbatim)
2. [repo] data/processed/overnight2/D/rnpl_statement_ledger.csv row D042
3. [repo] data/processed/overnight/02_guidance_tells.csv and 02_guidance_ledger.csv grep "Middle East|conflict|geopolit" (no rows)
4. [repo] data/processed/q3nowcast/G/intra_quarter_commentary.csv grep "Middle East|conflict|geopolit|inbound"
5. [repo] research/notes/overnight/05_macro-outlook-and-transmission.md (episode table, §4.4-4.6); research/notes/overnight2/C_consumer-relative-strength-regional-split.md §1
6. [repo] abnb_2026q2_10q.html grep "geopolit|Middle East|conflict"
7. [Polymarket API] public-search?q=Iran%20ceasefire; ?q=Iran%20US (2026-09-17T08:21:26Z)
8. WebSearch: Iran war news September 2026
9. WebFetch: globalsecurity.org/military/ops/iran-war-oprep.htm (updated 2026-09-16)
10. WebSearch: airlines cancel flights Gulf airspace travel demand Europe Asia September 2026
11. WebFetch: aljazeera.com 2026-08-06 "how the Middle East conflict is upending European travel"
12. WebSearch: Gulf Hormuz news today (final 72-hour name-free recency check; nothing new)
13. [computed] datasets/letter_geopolitical_base_rate_4Q20-2Q26.csv

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Middle East conflict, Iran, Strait of Hormuz, EMEA cancellations, Q4 2026 outlook paragraph, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The late-August/September escalation re-creates the March pattern (cancellations across EMEA and APAC) and management quantifies a ≥0.5pt drag on Q3 or Q4 | kept as the main Yes route (P(material effect) 0.30 × P(cited given effect) 0.75 = 0.225) | The March shock came from the war's outbreak and Gulf airspace closures; September's disruptions are real (claim 6) but smaller and demand is substituting within Europe (claim 7); Q2's impact was "less than anticipated" (claim 2) |
| A Q4 deceleration guide uses the conflict or "geopolitical uncertainty" as a named reason without a number (the 3Q23 construction) | kept (P 0.15 given no material effect, includes 0.05 resolver risk on negation language) | Management guided "moderate" in 3Q23 with a geopolitical clause; the team's base case is a deceleration bucket (claim 11) |
| Management repeats "not assuming any significant impact" and the resolver counts it | priced as resolver risk (0.05, inside the 0.15 above) | Convention 3 says No |
| A new geopolitical event (not the Middle East) is cited | kept inside the 0.30 | Convention 4; no such event on 17 Sep |
| Ceasefire or deal before 5 Nov removes the topic | kept as the main No route | Polymarket prices no meeting by 30 Sep at 0.94 and a deal by 31 Dec at 0.105 (claim 12); even a ceasefire leaves the Q3 cancellation history to describe |
| Nothing cited: strong Q3, EMEA "recovery" language repeated, Outlook silent as in 2Q26 | base case (about 0.65) | claims 2, 9 |

## 5. Independent Estimates
- base_rate_estimate: 0.40 — conditional on an active conflict at the print, the outlook paragraph named it or quantified it in 3 of 8 letters (claim 3); Laplace (3+1)/(8+2) = 0.40; the unconditional rate is 3/23 = 0.13 and the quantified-only rate is 1/8 = 0.125
- decomposition_estimate: 0.33 — P(a ≥0.5pt cancellation or booking effect in Sep-Oct from the renewed hostilities, Gulf route suspensions to late October and $108 oil) 0.30 × P(management cites it given the effect) 0.75 = 0.225; plus P(no material effect) 0.70 × P(named in the Q4 guide paragraph as cover for a moderation guide, or resolver reads a negation as attribution) 0.15 = 0.105; total 0.33
- anchor_estimate: none — no market on management language; Polymarket's adjacent prices (claim 12) only establish that the conflict will most likely still be live on 5 Nov (≈ 0.85-0.90), which is an input to P(material effect), not an anchor for the citation
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.35 (credible interval 0.22–0.48)
- final_minus_anchor: n/a. The base rate and decomposition are within 7 points and are partly independent (the base rate uses only the letter history; the decomposition uses the conflict state, peers and the team's guide-bucket view)

## 6. Final Numbers
P(Yes) = 0.35; credible interval 0.22–0.48.
Extreme-probability gate: not triggered.
Coherence: if B01 (moderation language) resolves Yes, B06 rises to about 0.45 (management pairs moderation with a cause); if C02 resolves (a), B06 falls to about 0.20. For X01 treat B06 as positively correlated with the deceleration branch.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 3 (a negation does not count) | If "not assuming any significant impact" in the Q4 paragraph resolves Yes: 0.55 (the 2Q26 construction is the modal wording if the conflict is still live) |
| P(material Sep-Oct effect) = 0.30 | Ceasefire or Hormuz reopening by mid-October: 0.10 → final 0.20; a new escalation with Gulf airspace closures (as in March): 0.60 → final 0.55 |
| P(cited given effect) = 0.75 | If management absorbs it silently as in 2Q26 (0.50): 0.26 |
| P(cover language given no effect) = 0.15 | If the Q4 guide is "low double digits" (no moderation to explain): 0.05 → final 0.26; if "mid single digits"/"moderate": 0.25 → final 0.40 |
| Base rate reference class (8 active-conflict prints) | If all 23 prints are the class (0.13): final 0.28 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-30 | EASA conflict-zone bulletin renewal; Polymarket "no meeting by 30 Sep" resolves | Bulletin extended into November: +0.03; a US-Iran meeting held: −0.05 |
| 2026-10-13 to 2026-10-31 | Hilton (21 Oct), Marriott, Booking and Expedia Q3 calls | A peer quantifying a Q3 conflict drag or citing it for Q4: +0.05 each (max +0.10); peers saying normalised: −0.05 |
| 2026-10-24 / 2026-10-25 | KLM and BA Gulf-route resumption dates | Routes resumed on schedule: −0.03; suspensions extended into December: +0.05 |
| any date | Ceasefire, Hormuz reopening agreement, or a new escalation with Gulf airspace closures | Apply the section-7 rows (0.20 / 0.55) within a day |
| 2026-11-04 | Freeze: nowcast band vs guide; C02 leading bucket | Bucket (c)/(d) leading: hold 0.35-0.40; (a) leading: 0.25 |
| 2026-11-05 after close | Letter Outlook paragraph, then the call's prepared Q4 remarks | Resolve per conventions 1-4; quote the sentence in the resolution note |

## 9. Impact
If B06 resolves Yes, the cited drag is taken at 0.7pt (the conditional mean of a ≥0.5pt disclosure given the 1Q26 template of "approximately 100bps"), applied to both 3Q26 and 4Q26 nights. Deltas versus the memo's base case:

| Item | Delta if B06 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **−0.7** | E[drag | ≥0.5] from the 1Q26 template |
| 4Q26 nights (pts) | **−0.7** (the guide carries the assumption, as in the 1Q26 Q2 guide) | claim 1 |
| ADR (pts) | 0.0 | cancellations are region-mixed; no ADR channel in the 1Q26 disclosure |
| 4Q26 revenue ($M) | **−21** (0.7 × $30M) | brief sensitivity |
| FY27 revenue ($M) | **−40** (0.25pt of FY27 growth × $158M; the effect fades) | judgement |
| FY26 adj. EBITDA margin (pp) | **−0.15** (0.7pt × 0.59pp × ¼ FY weight, both halves) | brief sensitivity (held costs) |
| FY27 adj. EBITDA margin (pp) | **−0.15** (0.66 × 0.25) | brief sensitivity |
| FY27 EPS ($) | **−0.04** ($40M × 0.66 × $0.0014) | brief sensitivity |
| Stock ($/share) | **−1.5** net: −$1.0 to −$3.4 fundamental (0.7pt × $1.50 fixed multiple to $4.90 joint solve) offset by the reaction-softening effect of an external, quantified cause (1Q26: +0.7% day-1 with a 100bp conflict headwind disclosed; decelerating prints post-2022 average −5.6%) | brief sensitivity; data/processed/abnb_earnings_reactions.csv |
| **EV = P × impact** | **0.35 × −$1.5 = −$0.5/share** | |
| Materiality | **Immaterial** as a standalone bonus line (< $1/share). Worse for the short than for the long: a named external headwind is the excuse that turns "deceleration" into "one-off", so the memo should list it under risks to the short's narrative, not under bonus items. Drop the number from the memo | |

## RESUME
The next agent (audit response) should attack: (1) the 8-print reference class in `datasets/letter_geopolitical_base_rate_4Q20-2Q26.csv` (whether 1Q22's risk list and 3Q23's monitoring clause are "attribution in the guide paragraph"); (2) the 0.30 for a material Sep-Oct effect, which should be re-read against the October Inside Airbnb review counts for EMEA and APAC markets and against Hilton/Booking Q3 commentary; (3) the sign of the stock impact, which this log argues is a risk to the short rather than a bonus. Re-run the Polymarket fetch and the globalsecurity daily page before quoting.
