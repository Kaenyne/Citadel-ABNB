# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A14). Companion questions: B02 `bonus-adr-residual-reverts`, B03 `bonus-marketing-cut-signalled`. Reused as inputs (read-only): C02 `q4-nights-bucket` revision 2 (the 4Q26 descriptor tree and its joint table with the 3Q26 print branches), R01 `risk-q3-nights-meets-guide` (the print distribution N(9.67, 1.70)), S01 `day1-move-5nov` (reaction cells), the overnight language study (`research/notes/overnight/03_management-language-and-stock.md`), the major-moves note. Reproduction: `datasets/b01_decomposition.py` (standard library; prints every estimate, the branch conditionals, the sensitivities and the impact arithmetic; writes `datasets/b01_decomposition_output.csv`). Letter classification: `datasets/b01_letter_language_by_print.csv` (16 letters, 3Q22 to 2Q26, each with the verbatim phrase or "none").

## 0. Metadata
- question_name: bonus-moderation-language
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B01)
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
At the 5 Nov print, will management use demand-softening language of the kind that preceded 8–13% declines ("moderation"/"moderate" applied to nights or demand, "shorter lead times", "softening", "macro uncertainty affecting bookings", or "deceleration" for 4Q26)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if the letter or prepared remarks contain any such phrase applied to forward demand or bookings (not to ADR, costs or FX). Resolution 5 Nov 2026.
### Fine Print
(none beyond the registry header conventions: "5 Nov print" = the 3Q26 release and call on its actual date; letter governs where the letter and call differ.)

Conventions adopted (stated here, not changing the question): (1) the object is the 3Q26 shareholder letter plus the scripted prepared remarks of the call (CEO and CFO), not the Q&A; (2) the phrase must be applied to forward demand, bookings or nights (the 4Q26 outlook, quarter-to-date trends, or the second half); the same words applied to ADR ("moderate increase in ADR"), to costs, to FX, or to the reported quarter only ("growth decelerated in March") do not resolve Yes; (3) the listed words resolve on their stems ("moderate", "moderation", "moderating"; "decelerate", "deceleration"; "soften", "softer", "softness"; "shorter lead times"/"lead times shortened"; "macro/macroeconomic uncertainty" when tied to demand or bookings); (4) close synonyms that convey the same forward softening ("pressure on growth rates", "slowing demand", "tougher comparison" *with* a softening verb) are counted as Yes because the title says "of the kind"; a bare comp statement ("challenging comparison") or a bucket alone ("high single digits") is No; the strict-list and with-synonym base rates are both reported; (5) "despite macro uncertainty, demand grew" (uncertainty as a foil for strength) is No; (6) if the print date moves, the same event on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Letter classification 3Q22–2Q26 (16 letters): the strict listed phrases applied to forward demand appear in **6 of 16** (3Q22 "moderate slightly"; 3Q23 "volatility early in Q4 ... monitoring macroeconomic trends and geopolitical conflicts that may impact travel demand" + "moderate"; 4Q23 "moderate"; 2Q24 "sequential moderation" + "shorter booking lead times globally and some signs of slowing demand from U.S. guests"; 1Q25 "moderate" + "relatively softer results ... broader economic uncertainties" + "broad macro uncertainty"; 1Q26 "slightly decelerate ... roughly 100bps headwind related to the conflict in the Middle East" + "navigating a period of macroeconomic and geopolitical uncertainty"); with close synonyms **8 of 16** (adds 1Q23 "nights growth lower than our revenue growth"; 2Q25 "putting pressure on growth rates later in the year"). W1 (1Q23+) 5/14 strict, 7/14 with synonyms; W2 (1Q24+) 3/10, 4/10; November letters 2/4 (3Q22, 3Q23 yes; 3Q24, 3Q25 no); bucket era (3Q25+) 1/4 (1Q26). Every strict hit sits on a directional-down nights descriptor: P(strict word \| down-class descriptor) = 6/8; P(strict word \| non-down descriptor) = 0/8 (1/8 with synonyms, 2Q25). The two down-class descriptors without the word are 1Q23 ("lower than revenue growth") and 4Q24 (the indirect "relatively stable compared to Q1 2024 ex Leap Day") | `datasets/b01_letter_language_by_print.csv` (regex extract of every letter sentence containing moderat/lead time/soft/macro/decelerat/uncertain/slow/pressure, `data/raw/letters/*.htm`, classified by hand) | 2022-11-01 to 2026-08-06 | 2026-09-17 | yes |
| 2 | Day-1 QQQ-excess returns by language state (claim 1's classes): strict-word letters mean **−5.4%** (n 6: −10.0, −5.1, −2.8, −12.3, −0.5, −1.6); with synonyms mean −6.6% (n 8, adds −12.0, −8.4); letters without such language mean +1.2% strict / +4.0% synonym-class (n 10 / 8). P(day-1 excess ≤ −8% \| language, synonym class) = 4/8; without = 1/8 (3Q24, the spend print). The four 8–13% declines named in the brief (3Q22, 1Q23, 2Q24, 2Q25) are all in the language class; the other four language prints fell 0.5–5.1%, two of them (1Q25, 1Q26) with an FY guide raised or reiterated in the same letter | `data/processed/abnb_earnings_reactions.csv`; `research/notes/2026-09-05_abnb-major-moves.md` §2, §2b; `research/notes/overnight/03_management-language-and-stock.md` §3 | 2026-09-05 / 2026-09-06 | 2026-09-17 | yes |
| 3 | Language study: "Two of the five worst [reactions] were management being wrong in the cautious direction" (2Q24 lead-time warning → Q3 nights 8.5 vs 8.7; 2Q25 comp warning → nights accelerated 7.4 → 8.8 → 9.8); demand-softness/macro share of management sentences: 5 best reactions 1.4%, 5 worst 3.4%; the change in macro-softness share vs the prior call has detrended r −0.13 with day-1 excess (null); the feature is explanatory, not predictive; §5 item 3: "If the same construction appears — 'tougher comparisons', 'shorter lead times', 'pressure on growth rates later in the year' — expect the drawdown" | `research/notes/overnight/03_management-language-and-stock.md` §2–3, §5 | 2026-09-06 | 2026-09-17 | yes |
| 4 | Macro note §5 point (b): watch for "any use of 'moderation', 'shorter lead times' or 'macro uncertainty', which cost 8-13% in 2022, 2023, 2024 and 2025"; point 6: "None of Airbnb's 2026 growth is coming from the macro cycle" | `research/notes/overnight/05_macro-outlook-and-transmission.md` §5 | 2026-09-07 | 2026-09-17 | no |
| 5 | Prepared-remark demand/macro sentence counts (call features, 23 calls): 2025Q4 8, 2026Q1 12, 2026Q2 4 prepared sentences on the demand-softness/macro theme (2024Q2 4, 2025Q1 5); the theme's prepared share was 9.6% in 1Q26 (the Middle East headwind quarter) and 2.9% in 2Q26. The 1Q26 prepared remarks reprised the letter's "decelerate slightly" and "macroeconomic and geopolitical uncertainty"; the 2Q26 prepared remarks contained no forward softening phrase ("moderate" appears only for ADR) | `data/processed/overnight/03_call_features.csv` (theme_demand_macro_n_prepared); `data/raw/transcripts/web/1Q26.html`, `2Q26.html` (regex extract) | 2026-09-06 / 2026-08-06 | 2026-09-17 | yes |
| 6 | Call transcripts add to the letter in the bucket era only through Q&A, not prepared remarks: 3Q25 prepared remarks used "mid-single digit range ... tougher comp" and "strength in longer lead time bookings" (no softening word); 4Q25 prepared remarks: "high single-digit growth ... moderate increase in ADR" (ADR only), "slightly better macroeconomic environment than anticipated"; the one "did moderate" in 4Q25 is Q&A about a region's reported growth. No prepared-remark forward softening phrase in 3Q24, 3Q25, 4Q25 or 2Q26 | `data/raw/transcripts/web/3Q25.html`, `4Q25.html`, `3Q24.html`, `2Q26.html` (regex extract, scratchpad `transcripts_demand.csv`) | 2024-11-07 to 2026-08-06 | 2026-09-17 | yes |
| 7 | C02 revision 2 (4Q26 nights descriptor): (a) 0.18, (b) 0.17, (c) 0.30, (d) 0.31 (directional "moderate/decelerate" ≈ 0.19 + explicit mid-single ≈ 0.12), (e) 0.04; tree parameters by 3Q26 print branch (≥10 / 9–10 / <9, masses 0.423 / 0.230 / 0.347 from R01's N(9.67, 1.70)): P(directional) 0.25 / 0.28 / 0.35, P("moderate" \| directional) 0.55 / 0.60 / 0.75, bucket content (a/b/c/d) .45/.20/.30/.05, .08/.22/.57/.13, .02/.07/.50/.41, P(none) 0.03; joint table (branch × option) published in C02 §6; P(Q3 <9 \| d) = 0.57 | `../q4-nights-bucket/research-log.md` §5–6; `../q4-nights-bucket/datasets/decomposition_v2.py` | 2026-09-17 | 2026-09-17 | yes |
| 8 | R01: P(3Q26 nights ≥ 10.0%) = 0.42, implied N(9.67, 1.70); team nowcast +9.5 (band 8.5–10.0 per the brief; the source's band is 8.5–11.0); every external series the team measures (hotels, TSA, lodging CPI, EMEA stays, the external stack at 9.2) decelerated through August; the 4Q26 comp is 1.0pt harder than 3Q26's; team 4Q26 baseline +8.1% (case B) | `../risk-q3-nights-meets-guide/research-log.md` §5–6; `docs/q3nowcast/SYNTHESIS.md`; C02 claims 9, 11 | 2026-09-17 / 2026-09-11 | 2026-09-17 | yes |
| 9 | Management's current tone is the opposite of softening: Chesky at Goldman Communacopia (8 Sep 2026): "Almost every market is accelerating. Almost every country is accelerating"; "Four of the five countries are accelerating"; no quarter-to-date number, no guide update; CFO made no public appearance after 6 Aug; 2Q26 call: "It's given us so much confidence in the second half of this year, that that's why we're raising our guidance" | `data/processed/q3nowcast/G/intra_quarter_commentary.csv` rows 7, 25–34; `research/notes/q3nowcast/G_external-sources-q3-read.md` §1.8 | 2026-09-08 / 2026-08-06 | 2026-09-17 | yes |
| 10 | Macro backdrop for a "macro uncertainty" sentence: NerdWallet travel price tracker (11 Sep 2026, August CPI): US travel costs +9% y/y, airfares +23.4% ("sustained high jet fuel prices and geopolitical risks"), hotel and motel rates +2.9%; search snippets (pages not fetched, zero weight): U.S. Travel dashboard "fourth quarter room nights [on the books] 1.2% behind the same time last year"; "hotel prices dip this fall". The 1Q26 letter's macro sentence was tied to a named shock (Middle East conflict, ~100bps); no comparable named shock is in the repo's September read | https://www.nerdwallet.com/travel/learn/travel-price-tracker ; https://www.ustravel.org/research/travel-recovery-insights-dashboard (403 via WebFetch; curl returned a JS dashboard, no text) | 2026-09-11 / 2026-09-02 | 2026-09-17 | no |
| 11 | Reaction panel `nq_nights_dir` (next-quarter nights direction): −1 in 8 prints, 0 in 6, +1 in 3 of the 17 coded (C02 claim 18: a derived encoding of the same letters); the 2023–24 regime was entirely directional (11 of 11 pre-2025 guides), the bucket era has 3 buckets in 4 guides | `data/processed/abnb_guidance_reaction_panel.csv`; C02 claims 3, 18 | 2026-09-07 | 2026-09-17 | no |
| 12 | Decomposition (this log, `datasets/b01_decomposition.py`): P(Yes) = 0.325 on C02's tree (0.331 on C02's final marginals); by 3Q26 branch: ≥10 → 0.24, 9–10 → 0.32, <9 → 0.43; by descriptor: P(Yes \| d) 0.67, (c) 0.25, (b) 0.13, (a) 0.06, (e) 0.30; P(Yes ∧ C02 = d) = 0.21, P(Yes ∧ C02 ≠ d) = 0.12; P(branch \| Yes) = 0.32 / 0.23 / 0.46; E[3Q26 nights \| Yes] = 9.31 vs 9.67 unconditional. Sensitivities: P(word \| directional-moderate) 0.70 → 0.30, 0.95 → 0.34; P(word \| high-single bucket) 0.10 → 0.28, 0.40 → 0.37; Street/Kalshi branch masses → 0.28; external-stack masses → 0.34 | `datasets/b01_decomposition_output.csv` | 2026-09-17 | 2026-09-17 | yes |
| 13 | No Polymarket or Kalshi market on the letter's language or the 4Q26 descriptor (Polymarket public-search "Airbnb": weekly/monthly price ladders and resolved Q2 GBV brackets only; Kalshi KXABNB: Q3 nights ladder, >146m 0.01/0.66 last 0.60, >148m 0.49/0.78 last 0.53, >150m 0.31/0.53 last 0.30, volume_fp 50–999 per rung, unchanged since the 6 Aug guide) | `sources/polymarket_search_Airbnb_20260917T080345Z.json`; `sources/kalshi_markets_KXABNB_open_20260917T080345Z.json` | 2026-09-17 | 2026-09-17 | no |
| 14 | Sensitivities for the impact table: 1pt of 3Q26 nights ≈ 1.34m ≈ $48M revenue; 1pt of 4Q26 ≈ $30M; kernel carry ⅔ × GBV × 12.03%; 1pt of FY27 growth ≈ $158M; margin 0.59pp per 1pt of 2H26 revenue held / 0.66 FY27; FY27 EPS $0.0014 per $M EBITDA; S01 unconditional day-1 median −2.9%, base-case median −8.6% (P(≤ −8) 0.53), ABNB $167.51 (16 Sep close) | `docs/pitch-forecasts/00_BRIEF.md`; `../day1-move-5nov/research-log.md` §6 | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes (impact only) |
| 15 | Final 72-hour checks (queries 12, 14): ABNB $170.65 on 15 Sep (−7.4% w/w), $250M Housing Accelerator, EU plans to let cities curb short-term rentals, Raymond James upgrade / Truist Hold; nothing on quarter-to-date demand or the letter | WebSearch (see §2) | 2026-09-15 | 2026-09-17 | no |

Newest load-bearing sources: C02/R01 (17 Sep, same day) and the 8 Sep Communacopia remarks (9 days against a 49-day window, 18%, above the 7-day cap; the only newer management datum is the absence of any appearance, claim 9). The last-72h pass found nothing newer that bears on the number.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md` (conventions, Bonus preamble, B01–B03), skill and schema, example log; C02 rev 2, R07, C04, R05, R01, C09, S01 logs and JSONs (read-only)
2. [repo, python] regex sentence extract from `data/raw/letters/*.htm` for moderat / lead time / soft / macro / decelerat / uncertain / slow / pressure (173 sentences), classified by print into forward-demand vs ADR/cost/FX/backward → `datasets/b01_letter_language_by_print.csv`
3. [repo, python] same extract from `data/raw/transcripts/web/*.html` (392 sentences; prepared remarks vs Q&A read by hand for 1Q23, 3Q23, 4Q23, 2Q24, 3Q24, 1Q25, 2Q25, 3Q25, 4Q25, 1Q26, 2Q26)
4. [repo] `research/notes/overnight/03_management-language-and-stock.md` (all); `research/notes/2026-09-05_abnb-major-moves.md` (all); `research/notes/overnight/05_macro-outlook-and-transmission.md` §5
5. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` nights_yoy_pct rows (17); `data/processed/overnight/03_call_features.csv` theme_demand_macro_* and theme_marketing_* columns; `data/processed/abnb_guidance_reaction_panel.csv` (nq_nights_dir, fy_* columns); `02_guidance_tells.csv`
6. [repo] `data/processed/q3nowcast/G/intra_quarter_commentary.csv` (Airbnb rows), `str_weekly_us_3q26.csv`
7. [Polymarket public-search] Airbnb (2026-09-17T08:03:45Z, saved); [Kalshi API] KXABNB open markets (same timestamp, saved)
8. WebSearch: Airbnb news (neutral pass, shared with B02/B03) — Housing Accelerator, Summer Release; nothing on demand language
9. WebSearch: Airbnb Q3 2026 earnings preview analysts expectations November — 5 Nov date, EPS $2.85; no preview content
10. WebSearch: US travel demand consumer September 2026 hotels airlines bookings softening — NerdWallet tracker (fetched, claim 10), U.S. Travel dashboard (snippet only), "hotel prices dip this fall" (snippet only)
11. WebFetch: nerdwallet.com travel-price-tracker (11 Sep 2026; August CPI: hotels +2.9%, airfares +23.4%); ustravel.org dashboard (403; curl → JS shell, unusable)
12. WebSearch: Airbnb ABNB this week (final 72-hour neutral recency check, shared) — price, ratings, Housing Accelerator, EU STR plans; nothing that changes the number
13. [python] `datasets/b01_decomposition.py` → `b01_decomposition_output.csv`
14. (B03's search "Airbnb sales and marketing expense 2027 leverage ..." also scanned for demand commentary: none)

WebSearch calls charged to this question: 2 (queries 10 and a half-share of the three shared neutral/recency queries 8, 9, 12); batch total 5 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, "moderate", "decelerate", "shorter lead times", "macro uncertainty", Nights and Seats Booked, 3Q26 shareholder letter, 5 November 2026, Reserve Now Pay Later

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The letter gives a directional "moderate/decelerate" sentence for 4Q26 (C02's (d)-directional, 0.19) and the word resolves Yes | leading path, ≈0.16 of the 0.34 | 6 of 8 down-class descriptors used a listed word (claim 1); the sentence is the word |
| A bucket ("high single digits" or "mid single digits") with a softening phrase in the narrative or prepared remarks | second path, ≈0.12 | the bucket era has used comp language ("challenging comparison", "tougher comps") rather than softening words (claims 6, 1: 0 of 3 bucket letters); kept at 0.25–0.40 per bucket because a decelerating print is where the narrative would carry "moderate"/"shorter lead times" |
| A "macro/geopolitical uncertainty affecting bookings" sentence independent of the descriptor (1Q25, 1Q26 pattern) | kept inside the conditionals (≈0.03) | both precedents were tied to named shocks (tariffs, Middle East); the September read has airfares +23% and Q4 hotel room nights on the books −1.2% (snippets), no named shock; management's public tone is "accelerating" (claim 9) |
| Management repeats "low double digits" and no softening word appears (C02 (a), 0.18) | the main No path with (c) | P(Yes \| a) 0.06; the Communacopia tone and the 6 Aug "confidence in the second half" (claim 9) |
| Count "moderate increase in ADR" as Yes | discarded | the resolution excludes ADR; the phrase has appeared in 4 of the last 5 letters and would otherwise make the question trivial |
| Count Q&A answers ("we're seeing a bit of softness") as Yes | discarded | resolution names the letter or prepared remarks; Q&A is where the 3Q23 and 2Q24 softness detail lived, but each of those letters already carried the word |
| Use the reaction-panel −1 share (8/17 = 0.47) as the base rate | discarded as the base rate, kept as the upper bound | it is the down-descriptor rate, not the word rate; 2 of the 8 down descriptors had no listed word |
| The bucket format has retired the word ("moderate" 0 of 3 bucket letters) → P ≈ 0.15 | kept as the lower sensitivity | the one bucket-era directional guide (1Q26) used "decelerate"; C02 gives the directional format 0.25–0.35 by branch, which is where the word lives |

## 5. Independent Estimates
- base_rate_estimate: 0.35 — strict listed phrases in 6 of 16 letters since 3Q22 (0.375; W1 5/14 = 0.36; W2 3/10 = 0.30; November letters 2/4; bucket era 1/4 = 0.25, Laplace 0.33); with synonyms 8/16 = 0.50 (W2 0.40); regime-conditioned between the bucket-era rate and the W2 rate because the format shift removes the word from ~70% of guides (C02 P(bucket) ≈ 0.70) while the print state (P(decel) ≈ 0.58, a 1pt harder Q4 comp, every external series slowing through August, claim 8) raises the chance of a directional-down sentence above its 2024–26 average
- decomposition_estimate: 0.33 — C02's tree × P(language \| sentence type): directional "moderate/decelerate" 0.85, directional stable/higher 0.10, buckets a/b/c/d 0.05/0.15/0.25/0.40, no descriptor 0.30 (claim 12); by branch 0.24 / 0.32 / 0.43; range 0.28–0.37 across the stated parameter reversals
- anchor_estimate: 0.31 — no external market (claim 13); the designated internal anchor is C02's option (d) = 0.31 (revision 2, 17 Sep), the language block this question overlaps; the reaction panel's down-descriptor share 0.47 is the upper bound, the bucket-era word rate 0.25 the lower
- anchor_value: 0.31 (C02 revision 2 option (d), 2026-09-17; dependent internal construction, not a price)
- final_estimate: 0.34 (credible interval 0.24–0.46)
- final_minus_anchor: +3 points. NOT_INDEPENDENTLY_DERIVED flag: raised by the arithmetic and answered: the anchor is the team's own C02 vector and the decomposition is built on the same tree, so their agreement is common-mechanism, not corroboration; the base rate (0.35) is the one independent leg and it is built from the 16 letters directly (claim 1). The three legs agree within 4 points; the disagreement they hide is about format (bucket vs directional), which is C02's own coin flip (its (c) 0.30 vs (d) 0.31)

## 6. Final Numbers
**Binary.** P(the 3Q26 letter or prepared remarks apply "moderate/moderation", "decelerate", "softening/softer", "shorter lead times" or "macro uncertainty" to forward demand or bookings) = **0.34**, credible interval **0.24–0.46** (the span of the §7 rows plus the strict/synonym reading of the resolution).

Overlap with C02 (stated for X01): the tree gives P(Yes ∧ C02 = d) ≈ 0.21 and P(Yes ∧ C02 ≠ d) ≈ 0.12, i.e. two-thirds of a Yes is the directional "moderate" sentence C02 already prices inside (d) (its directional-moderate sub-block 0.19), and the rest is a softening phrase around a bucket. P(Yes \| C02 = d) ≈ 0.67, P(Yes \| c) ≈ 0.25, P(Yes \| a or b) ≈ 0.10. Joint with the print: P(Yes \| 3Q26 ≥ 10) 0.24, (9–10) 0.32, (<9) 0.43; P(3Q26 < 9 \| Yes) 0.46. X01 should treat B01 as the language marker of the base-case scenario, not as an independent event.

Strict-list reading only (convention 4 reversed, synonyms excluded): 0.30. Synonyms counted generously (any forward "tougher comps"/"pressure" sentence): 0.40.

Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| P(word \| directional "moderate/decelerate" sentence) 0.85 | 0.70 (Laplace on 6/8): 0.30; 0.95: 0.34 |
| P(softening phrase \| "high single digits" bucket) 0.25 | 0.10 (bucket-era literalism, 0 of 3): 0.28; 0.40: 0.37 |
| P(softening phrase \| "mid single digits" bucket) 0.40 | 0.20: 0.30; 0.60: 0.35 |
| 3Q26 print branches from R01's N(9.67, 1.70) | Street/Kalshi N(11.0, 1.7): 0.28; external stack N(9.2, 1.7): 0.34; team baseline N(9.9, 1.48): 0.31 |
| C02's P(directional) 0.25–0.35 by branch | 0.20 everywhere (bucket format entrenched): ≈ 0.29; 0.40 everywhere: ≈ 0.38 (from C02 §7 row 2 scaled by P(word \| directional)) |
| Resolution read strictly on the listed stems (convention 4 off) | 0.30 |
| A named macro/geopolitical shock emerges before 5 Nov (1Q26 template) | +0.10 (the "macro uncertainty" channel becomes near-certain in the letter's narrative) |

Pre-mortem ("it is 5 Nov and the letter contained the word / did not"): (1) Yes at 0.34 too low: the print decelerated to 8–9%, October was noisy, and management wrote the 3Q23 sentence ("moderate ... we are seeing some variability") instead of a bucket — priced in the <9 branch at 0.43, and the reason the interval reaches 0.46; (2) Yes because the word attached to a *bucket* ("we expect growth to moderate to high single digits in Q4") — the bucket_c/d conditionals carry this at 0.25/0.40 and it is the least-evidenced parameter (0 of 3 bucket letters used it); (3) Yes through "shorter lead times" as RNPL's lead-time lengthening laps (the 1Q26 letter credited RNPL for longer lead times; a lap would read as "lead times normalised", which is not softening unless written as "shorter") — small; (4) No at 0.34 too high: management kept the bucket format and wrote "high single digits ... against tougher comps" with the Communacopia "accelerating" tone — the (c)-without-word path is the largest single No path (0.22) and is why the number sits below C02's (c)+(d). Asymmetry: this is a bonus item for a short memo; a confident Yes that resolves No costs little in the memo (the base case does not depend on the word), a confident No that resolves Yes would have dropped the memo's most legible historical pattern (claim 2). The interval is kept wide on the format question.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-09-30 | September Inside Airbnb dumps; R01 re-centres; C02 re-runs its tree | Re-run `b01_decomposition.py` with the new branch masses: each 0.1 of mass moved from ≥10 to <9 adds ≈ +0.02 |
| 2026-10-02 | Prelim memo due | Quote 0.34 (0.24–0.46) as the language marker of the base case; do not add it to the base case's probability |
| 2026-10-13 | September CPI (lodging away from home); NTTO September arrivals ~15 Oct | A named demand shock (arrivals ≤ −10%, a geopolitical event, a US shutdown affecting travel) → +0.10 via the "macro uncertainty" channel |
| 2026-10-28 to 2026-10-30 | BKNG / EXPE Q3 prints (EXPE reads through) | EXPE guiding a Q4 room-night deceleration ≥ 2pts with softening language of its own → +0.03; EXPE accelerating → −0.03 |
| 2026-11-05 (after close) | 3Q26 letter (16:05 ET) then prepared remarks (~16:30 ET) | Resolve by conventions 1–5: search the letter's outlook and regional paragraphs for the stems, then the prepared remarks; ADR uses excluded; record which sentence resolved it for the audit |
| 2026-11-06 | Day-1 close | Feed S01/X01: if Yes, the historical conditional day-1 mean is −5.4% (strict, n 6) — read against the S01 base-case cell, not as an addition to it |

## 9. Impact
If the event happens (the language appears), the print state it implies is E[3Q26 nights \| Yes] = 9.31% (vs 9.67 unconditional, 9.9 team baseline) and a 4Q26 descriptor in the (c)/(d) block with probability 0.83. Deltas versus the memo base case (team baseline path), from `datasets/b01_decomposition_output.csv`:

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **−0.6** | E[nights \| Yes] 9.31 − 9.90 (claims 8, 12) |
| 4Q26 nights (pts) | **−0.4** | 0.6 persistence of the Q3 shortfall into the Q4 booking rate (R01 convention) |
| ADR (pts) | 0 | language question; ADR uses of the words are excluded and the ADR line is B02's |
| 4Q26 revenue ($M) | **−22** | kernel carry ⅔ × (−0.59 × 1.34m × $176.8 = −$141M GBV) × 12.03% ≈ −$11M, plus −0.36pt × $30M ≈ −$11M |
| FY27 revenue ($M) | **−38** | 0.4 persistence × 0.59pt × $158M |
| FY26 adj. EBITDA margin (pp) | **−0.2** | 0.59pp per 1pt of 2H26 revenue held (3Q26 −$28M, 4Q26 −$22M on $7.98bn), half-year weight |
| FY27 adj. EBITDA margin (pp) | **−0.15** | 0.66 × (−$38M / $15,829M) |
| FY27 EPS ($) | **−0.04** | −$38M × 0.66 flow-through × $0.0014 |
| Stock ($/share) | **−4 vs the S01 unconditional** (−5.4% conditional day-1 mean, strict n 6, vs −2.9% median: −2.5pt × $167.51); **≈ 0 vs the memo base case** (the base-case cell's −8.6% median already conditions on the deceleration and the guide the word accompanies; the language prints' mean sits inside that cell's range, claim 2) | `abnb_earnings_reactions.csv`; S01 §6 |
| **EV = P × stock** | **0.34 × −$4 ≈ −$1.4/share vs the unconditional; ≈ $0 incremental to the base case** | **Material only as the language marker of the base case, not as a separate bonus line**: the memo should cite it as the tell that the deceleration scenario has arrived (P 0.34; historical day-1 mean −5.4%, 4 of 8 such prints fell ≥ 8%) and must not add its EV to the base case's, because P(Yes ∧ C02 = d) = 0.21 of its 0.34 is the same event |

RESUME: the next agent (audit response) should re-run `datasets/b01_decomposition.py` (instant) and attack (1) the P(language \| sentence type) vector, especially the bucket conditionals 0.25/0.40, which have 0 of 3 bucket-era observations behind them; (2) convention 4 (synonyms), which is worth 0.30 vs 0.40 on its own; (3) whether prepared remarks ever add a softening phrase that the letter lacks (claim 6 says not since 3Q24 — verify against the IR FactSet transcripts in `data/raw/transcripts/ir/` if present, which have exact prepared/Q&A tags). If the September dumps move R01's centre, re-run before anything else.
