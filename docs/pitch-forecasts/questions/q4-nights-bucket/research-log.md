# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A02, question C02. Reproduction script: [datasets/decomposition.py](datasets/decomposition.py) (standard library only; prints every estimate and writes `datasets/decomposition_output.csv`).

## 0. Metadata
- question_name: q4-nights-bucket
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` §C02)
- type: multiple_choice
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a

## 0b. Question (verbatim)
### Title
What qualitative growth bucket will Airbnb give for 4Q26 Nights and Seats Booked at the 5 Nov print?
### Resolution Criteria
**Type.** Multiple choice. **Options.** (a) "low double digits" or any language implying ≥10% (e.g., "double-digit", "similar to Q3" when Q3 printed ≥10%); (b) "around 10%" / "high single digits to low double digits" / "similar to Q3" when Q3 printed <10%; (c) "high single digits"; (d) "mid single digits" or lower, or explicitly "moderate/decelerate" without a bucket; (e) no 4Q26 nights descriptor given.
### Fine Print
Letter governs; call clarifications count only if the letter is silent. Resolution date 5 Nov 2026.

Conventions adopted for this forecast (registry header: "Bucket language" is the letter's or call's qualitative growth descriptor for the next quarter; letter governs; where neither states an item, "not stated" resolves):
1. A directional-only sentence ("relatively stable compared to Q3", "similar to Q3") is read against the printed 3Q26 rate: ≥10.0% printed → (a); <10.0% printed → (b). A directional-down sentence with no bucket ("moderate", "decelerate", "lower than Q3", "a few points below") → (d) as the option text says, whatever the printed rate. A directional-up sentence ("higher than Q3") with Q3 printed <10% → (b) unless the letter also says "double-digit", in which case (a).
2. A GBV bucket "driven by growth in Nights and Seats Booked" with no qualifier on nights → (e). A GBV bucket "driven by high-single-digit growth in Nights and Seats Booked" → (c) (this is the 4Q25-letter construction and counts as a nights descriptor).
3. "Approximately 10%" or "roughly 10%" → (b). "High single to low double digits" → (b). "Low double digits" → (a). "Mid-to-high single digits" → (c) (midpoint 6.5–7 is high-single by their vocabulary; if the letter says "mid single digits" alone → (d)).
4. If the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | The guidance ledger holds 17 next-quarter Nights guides from the 2Q22 print to the 2Q26 print (16 resolved). Classified against the just-printed y/y rate: 9 "down" (3Q22 "moderate slightly", 1Q23 "lower than revenue growth", 3Q23 "moderate", 4Q23 "moderate", 2Q24 "sequential moderation", 1Q25 "moderate", 1Q26 "slightly decelerate", plus the two buckets set below the printed rate: 3Q25 mid-single vs 8.8% printed, 4Q25 high-single vs 9.8% printed), 5 "stable" (2Q22, 4Q22 "nearly as strong", 1Q24, 4Q24, 2Q25), 2 "up" (2Q23 "modest sequential increase", 3Q24 "higher than Q3"). down 0.56 / stable 0.31 / up 0.13 (n 16). Extract: [datasets/nights_descriptor_vs_printed_and_comp.csv](datasets/nights_descriptor_vs_printed_and_comp.csv), [datasets/ledger_next_quarter_nights_guides.csv](datasets/ledger_next_quarter_nights_guides.csv) | data/processed/overnight/02_guidance_ledger.csv (letters verified `verified=True`) | 2026-09-07 | 2026-09-17 | yes |
| 2 | Q3-print (November) next-quarter nights descriptors specifically: 3Q22 "will moderate slightly relative to Q3 2022" (down; 25.1 → 20.2), 3Q23 "to moderate relative to Q3 2023" (down; 13.5 → 12.0), 3Q24 "to be higher than Q3 2024" (up; 8.5 → 12.3), 3Q25 "in the mid-single-digit range due to the challenging Q4 2024 comparison" (bucket below printed; 8.8 printed, 9.8 delivered). 3 of 4 below the printed rate. Verbatim outlook paragraphs saved to [sources/letter_outlook_extracts_3Q22-2Q26.txt](sources/letter_outlook_extracts_3Q22-2Q26.txt) | data/raw/letters/3Q22_d408297dex991.htm; 3Q23_d481318dex991.htm; 3Q24_d886752dex991.htm; 3Q25_d40503dex991.htm | 2022-11-01 / 2023-11-01 / 2024-11-07 / 2025-11-06 | 2026-09-17 | yes |
| 3 | Bucket era (since the 3Q25 letter): three named buckets, all set with a comp in view. 3Q25→4Q25 "mid-single-digit" (mapped 4–6, mid 5) with 8.8% just printed and a 12.3% comp: mid − printed = −3.8. 4Q25→1Q26 "high-single-digit growth in Nights and Seats Booked" (7–9, mid 8) with 9.8% printed and a 7.9% comp: −1.8. 2Q26→3Q26 "low double-digit growth in Nights and Seats Booked" (10–12, mid 11) with 10.3% printed and an 8.8% comp: +0.7. The one directional guide in the era (1Q26→2Q26 "slightly decelerate … assuming an estimated roughly 100bps headwind related to the conflict in the Middle East") was missed in the company's favour (9.15 → 10.34) | data/processed/overnight/02_guidance_ledger.csv rows 158, 167, 177, 187; data/raw/letters/4Q25_d58192dex991.htm, 1Q26_d23351dex991.htm, 2Q26_d70413dex991.htm | 2025-11-06 to 2026-08-06 | 2026-09-17 | yes |
| 4 | Buckets are "the most beatable line in the letter": 5 of 5 nights/GBV buckets finished above the top of the range (0 met, 0 below); the two resolved nights buckets were beaten by 4.8 and 1.15 points at the midpoint (3.8 and 0.15 points above the top) | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §3.1–3.2; docs/revenue-forecast-strategy/05_backtests/guidance-policy.md | 2026-09-11 | 2026-09-17 | yes |
| 5 | 3Q25 call, Mertz (mirror transcript): "For Q4, we anticipate year-over-year growth of nights and seats booked in the mid-single digit range. Last year, we saw a meaningful acceleration of growth from Q3 to Q4. Our Q4 2025 guide takes this tougher comp into consideration. On a year-over-year basis, we do anticipate a sequential acceleration from Q3 to Q4." (the last sentence reads as a two-year-stack statement; mirror transcript, treated as tone). Also: "we're seeing strength in longer lead-time bookings, partly driven by our Reserve Now, Pay Later offering in the U.S." | data/raw/transcripts/web/3Q25.html | 2025-11-06 | 2026-09-17 | no |
| 6 | 3Q23 call, Stephenson, on why the Q4 nights guide was directional: "we're just seeing some variability in our nights demand here early in the quarter, and so we're just being cautious with that guide. And so we're not being specific on it, but anticipate nights growth to be a few points below" (precedent for a no-bucket "moderate" sentence when October is noisy → option (d) by the fine print) | data/raw/transcripts/web/3Q23.html | 2023-11-01 | 2026-09-17 | yes |
| 7 | 2Q26 letter 3Q26 guide, verbatim: "We expect year-over-year GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked and a moderate increase in ADR due to mix shift and price appreciation." 2Q26 call, Mertz: "Even against tougher comps in the back half of the year, we are raising our full year guidance." July was in hand when the guide was set | data/raw/letters/2Q26_d70413dex991.htm; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 8 | Team 3Q26 nights nowcast (the conditioning band, brief §Rules 6): +9.5% (146.3m), band 8.5–10.0; reviews stays index walk-forward RMSE 1.48pp vs naive 2.16 (ratio 0.68); external stack +9.2 (6.8–12.0); model path 9.9 at the top of the band; no read supports an acceleration from 2Q26's +10.34% | docs/q3nowcast/SYNTHESIS.md; research/notes/2026-09-10_nights-baseline-reconciliation.md | 2026-09-11 / 2026-09-10 | 2026-09-17 | yes |
| 9 | Team 4Q26 nights baseline: case B (WS-D global lap of the Oct–Dec 2025 cancellation-redesign and single-fee legs) +8.0 to +8.2%, point +8.1% (131.8m), adopted, with case A (PR #32 NA-only lap) +8.9% (132.7m) as the top of the band; bridge v3 carries 8.12 / band 8.0–8.86 | research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md Memo 2; docs/overnight2/SYNTHESIS.md §3.1; data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv | 2026-09-11 / 2026-09-12 | 2026-09-17 | yes |
| 10 | RNPL unified module: 4Q26 nights +7.61% (131.2m), band 6.6–8.4, from team 8.90 less uplift lap −0.59, pull-forward −0.16, deferral −0.10, propensity −0.45 | docs/rnpl-short-audit/00_SYNTHESIS.md §1.3 | 2026-09-11 | 2026-09-17 | yes |
| 11 | Comps: 4Q25 nights +9.82% (121.9m on 111.0m); 3Q25 +8.80% (133.6m on 122.8m); 4Q24 +12.35%. The 4Q26 comp is 1.0 point harder than the 3Q26 comp | data/processed/abnb_driver_history_quarterly.csv ([datasets/driver_history_nights_revenue.csv](datasets/driver_history_nights_revenue.csv)) | 2026-08-06 (last print) | 2026-09-17 | yes |
| 12 | Pre-registered 5 Nov thresholds for the 4Q26 nights guide: implies ≤7.5% supports the lap/drag hypothesis, ≥9.5% weakens it, 7.6–9.4% inconclusive; both team cases sit in the inconclusive band | data/processed/overnight2/D/D1_prereg_thresholds.csv | 2026-09-11 | 2026-09-17 | no |
| 13 | Street nights bars (Bloomberg MODL Standard Consensus, screenshot 12 Sep 2026, values read off the image, n 28): 3Q26 149.0m (+11.5%; range 147–151m, i.e. +10.0 to +13.0), 4Q26 134.0m (+9.9%; range 130–136m, +6.6 to +11.6). The team's 3Q26 146.8m sits below the lowest estimate; the 4Q26 team 132.7m sits inside the range at the 45th percentile | data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv | 2026-09-12 | 2026-09-17 | yes |
| 14 | Kalshi KXABNB "Will Airbnb Inc. report Above X nights & experiences booked in Q3 2026?", fetched 2026-09-17T02:50:36Z: >150m bid 0.32 / ask 0.36 (last 0.30); >148m 0.50/0.55 (0.53); >146m 0.63/0.66 (0.60); >144m 0.76/0.83 (0.83); >142m 0.84/0.92; >140m 0.89/0.96; >138m 0.94/0.97. Market detail (02:55:02Z): `liquidity_dollars` 0.0000, `volume` None, `open_interest` None. Quotes only, no trade: **zero weight as a price**; recorded because the ladder's implied median (~148m, +10.8%) coincides with the Bloomberg Street (149m) and disagrees with the team band. Saved [sources/kalshi_markets_KXABNB_open_20260917T025036Z.json](sources/kalshi_markets_KXABNB_open_20260917T025036Z.json), [sources/kalshi_market_KXABNB-26NOVNEB-148000000_20260917T025502Z.json](sources/kalshi_market_KXABNB-26NOVNEB-148000000_20260917T025502Z.json) | https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=100&series_ticker=KXABNB | 2026-09-17 | 2026-09-17 | no |
| 15 | Kalshi KXABNBA FY2026 nights ladder (02:50:36Z): >565m 0.79/0.88; >570m 0.63/0.71; >575m 0.37/0.41; >580m 0.19/0.28; >585m 0.10/0.15; >590m 0.08/0.12. Implied median ≈572m; with 1H26 304.5m and the Q3 ladder's ~148m this implies 4Q26 ≈120m (−1.6% y/y), i.e. the two Kalshi ladders are mutually inconsistent. Zero weight. Saved [sources/kalshi_markets_KXABNBA_open_20260917T025036Z.json](sources/kalshi_markets_KXABNBA_open_20260917T025036Z.json) | https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=100&series_ticker=KXABNBA | 2026-09-17 | 2026-09-17 | no |
| 16 | Polymarket public-search "Airbnb" and "ABNB earnings" (02:50:05Z): no market on Q3/Q4 2026 KPIs or guidance; only resolved "Will Airbnb (ABNB) beat quarterly earnings?" (Nov 2025 No, Feb 2026 No, May 2026 No, Aug 2026 Yes), resolved Q2 GBV brackets, and weekly/monthly price-hit markets. Saved [sources/polymarket_search_airbnb_20260917T025005Z.json](sources/polymarket_search_airbnb_20260917T025005Z.json), [sources/polymarket_search_abnb_earnings_20260917T025005Z.json](sources/polymarket_search_abnb_earnings_20260917T025005Z.json) | https://gamma-api.polymarket.com/public-search?q=Airbnb | 2026-09-17 | 2026-09-17 | no |
| 17 | Insider mechanics §5.5: a "good Q4 guide" has "nights guided 'low double digit' again"; a "bad one" has "nights dropped back to 'high-single digit'"; the base case there is a Q4 revenue midpoint near $3.05–3.10bn | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §5.5 | 2026-09-11 | 2026-09-17 | no |
| 18 | Reaction panel `nq_nights_dir` (next-quarter nights direction coded −1/0/+1): −1 in 9 prints, 0 in 6, +1 in 3, NaN for the three bucket prints (3Q25, 4Q25, 2Q26 carry `nq_nights_guide_pts` −3.79, −1.82, +0.66). Consistent with claim 1. Extract [datasets/reaction_panel_fy_actions.csv](datasets/reaction_panel_fy_actions.csv) | data/processed/abnb_guidance_reaction_panel.csv | 2026-09-07 | 2026-09-17 | no |
| 19 | Chesky, Goldman Communacopia 8 Sep 2026 (only company appearance 1 Aug–11 Sep; no CFO appearance, no 8-K, no mid-quarter update): "Almost every market is accelerating. Almost every country is accelerating," "India is growing 60% year-over-year." Tone, no quarter-to-date number | research/notes/q3nowcast/G_external-sources-q3-read.md §1.8 | 2026-09-11 | 2026-09-17 | no |
| 20 | Every letter from 2Q22 to 2Q26 (17 consecutive) carries a next-quarter nights sentence; the 4Q25 construction ("GBV … low teens … driven by high-single-digit growth in Nights and Seats Booked") embeds the descriptor inside the GBV sentence | data/processed/overnight/02_guidance_ledger.csv; data/raw/letters/*.htm | 2022-08-02 to 2026-08-06 | 2026-09-17 | yes |
| 21 | Web (search snippets, pages not fetched; the nasdaq.com Truist page timed out): Raymond James upgraded ABNB to Outperform, PT $200, 8 Sep 2026; Truist maintained Hold, PT $161, 15 Sep 2026; Bernstein reiterated Buy, PT $217 the same week. No analyst statement about the 4Q26 nights bucket found | https://www.dailypolitical.com/2026/09/15/airbnb-inc-nasdaqabnb-given-average-rating-of-moderate-buy-by-analysts.html | 2026-09-15 | 2026-09-17 | no |
| 22 | Airbnb IR events page lists no upcoming events (Q3 2026 call date not yet announced as of the fetch); ~5 Nov is MarketBeat's schedule-based estimate. 3Q25 print was 6 Nov 2025 | https://investors.airbnb.com/events-and-presentations/default.aspx; research/notes/catalyst_calendar.md | 2026-09-17 | 2026-09-17 | no |
| 23 | Final 72-hour recency checks (queries 12–13): nothing new on demand, guidance or the print date since the 8 Sep Communacopia remarks; search results were evergreen host-blog content and the 6 Aug guidance coverage | WebSearch (see §2) | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 12 Sep Bloomberg screenshot (claim 13) and the 11–12 Sep repo notes (claims 8–9); 5–6 days old against a 49-day window (≈11% of the window, ≈7 days cap). The last-72h pass (claim 23) found nothing newer that bears on the number; the September Inside Airbnb dumps (monitoring row 1) are the next real input.

## 2. Query Log
1. [repo] `02_guidance_ledger.csv` — all `nights_*` rows, all `3Q*` print rows, FY rows
2. [repo] `abnb_guidance_reaction_panel.csv` — full panel
3. [repo] letters 3Q22/3Q23/3Q24/3Q25/4Q25/1Q26/2Q26 outlook sections (regex extract, saved to sources/)
4. [repo] transcripts 3Q25, 3Q24, 3Q23, 2Q26 — "mid-single", "high single", "low double", "moderate", "decelerat", "tougher comp", "challenging" contexts
5. [repo] `03_insider_mechanics.md` §3, §5; nights-baseline reconciliation; overnight2 SYNTHESIS; ADR v3 N memo; RNPL 00_SYNTHESIS; q3nowcast SYNTHESIS and G note; D1_prereg_thresholds; E_street_distribution_vs_team; L0 vintage register (2026Q4 rows); catalyst calendar; B2 Q4 guide exhibit
6. [Polymarket public-search] Airbnb
7. [Polymarket public-search] ABNB earnings
8. [Kalshi API] events?status=open&limit=200 (grep airbnb/abnb/earnings); series?category=Companies (decode error, re-read utf-8); series?category=Financials → KXABNB, KXABNBA
9. [Kalshi API] markets?series_ticker=KXABNB (open, all); markets?series_ticker=KXABNBA; markets/KXABNB-26NOVNEB-148000000 (rules, liquidity)
10. Airbnb news
11. Airbnb third quarter 2026 earnings date
12. Airbnb fourth quarter 2026 nights growth outlook analysts
13. [fetch] investors.airbnb.com/events-and-presentations (no upcoming events listed)
14. Airbnb ABNB analyst note September 2026 (shared with C03)
15. [fetch] nasdaq.com/articles/truist-securities-upgrades-airbnb-abnb (timeout)
16. Airbnb bookings demand this week (final 72-hour neutral recency check — nothing new)
17. Airbnb guidance outlook latest (final recency check, shared with C03 — nothing newer than 6 Aug)

WebSearch calls charged to this question: 4 (queries 10, 11, 12, 16); query 14 and 17 are charged to C03.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Nights and Seats Booked, "high single digits", Reserve Now Pay Later, 4Q25 comparison, shareholder letter, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Management repeats "low double-digit" for 4Q26 (option a) | kept as minority, 0.21 | Requires either a 3Q26 print ≥10% with October running double digits, or a 3Q24-style re-acceleration call. The comp is 1.0 point harder than Q3's (claim 11), the global fee/cancellation lap lands in Q4 (claim 9), and every team read has Q4 at 7.6–8.9 (claims 9–10). Kept above the base rate for "up" (0.13) because management set the Q3 bucket at the printed rate with July in hand (claim 7), the Street bar is 9.9% (claim 13), and Chesky's September tone is bullish (claim 19) |
| "High single digits" (option c) is the modal descriptor | leading, 0.39 | Down-descriptors are 9 of 16 overall and 3 of 4 at November prints (claims 1–2); the bucket era sets the bucket midpoint 1–4 points below the printed rate when the comp hardens (claim 3); every repo model has 4Q26 at 7.6–8.9 (claims 9–10); the Street's 9.9 less the 1–3 point bucket cushion is 7–9 |
| Directional-only "moderate / decelerate" sentence (part of option d) | kept, ≈0.12 of the 0.17 | 12 of 16 pre-2025 nights guides were directional; 1Q26 was directional in the bucket era; the 3Q23 precedent (claim 6) shows management drops the bucket when October is volatile. The fine print maps a no-bucket "moderate" to (d) regardless of level, so (d) carries format risk, not just a mid-single-digit call |
| Explicit "mid single digits" (rest of option d) | kept, ≈0.05 | Needs management to expect ≤6–7% for Q4: the RNPL module's band floor (6.6) and the bridge's half-lap (8.1) do not get there; 3Q25's mid-single call was made against a 12.3% comp, not a 9.8% one |
| "Around 10%" / hyphenated "high single to low double digits" / "similar to Q3" with Q3 <10 (option b) | kept, 0.19 | Management has used hyphenated buckets for FY revenue ("low to mid teens") and "relatively stable" five times; a 3Q26 print of 9.5–9.9 followed by "similar to Q3" is a live path; the Street's 4Q26 bar (9.9%) is exactly this bucket |
| No 4Q26 nights descriptor (option e) | tail, 0.04 | 17 of 17 letters since 2Q22 carry one (claim 20); residual for a GBV-only sentence ("driven by continued growth in Nights and Seats Booked") — see the gate in §6 |
| Use the Kalshi Q3 ladder or the Bloomberg 149m as the 3Q26 conditioning distribution instead of the team band | discarded (kept as a sensitivity row) | Brief §Rules 6: the print is conditioned on the team band, not re-forecast from the web; the Kalshi ladder has zero liquidity and no volume (claim 14); the Bloomberg bar is a 12 Sep screenshot of a panel whose lowest estimate is above the team's number (claim 13) |
| Treat the guide number as separable from management's cushion | discarded | Buckets are floors with a 1–4 point cushion (claims 3–4); the descriptor is management's expectation minus a cushion, so the mapping is from expected Q4 growth of ~8–9 to a "high single digits" sentence, not from 8.1 to "approximately 8%" |

## 5. Independent Estimates
- base_rate_estimate: (a) 0.24, (b) 0.19, (c) 0.37, (d) 0.18, (e) 0.02 — descriptor-vs-printed classes on the 16 resolved next-quarter guides (down 0.56 / stable 0.31 / up 0.13, claim 1), mapped to options with "stable" split by P(3Q26 print ≥10.0) = 0.38 from the team band and "down" split 2:1 between a bucket (c) and a no-bucket or mid-single sentence (d); 0.02 reserved for (e)
- decomposition_estimate: (a) 0.21, (b) 0.19, (c) 0.40, (d) 0.17, (e) 0.03 — scenario tree on the 3Q26 print from the team band (≥10.0: 0.38; 9.0–9.99: 0.42; <9.0: 0.20; centre 9.5–9.6, walk-forward sd 1.48pp) × descriptor given the print (≥10: a .42 b .20 c .28 d .08 e .02; 9–10: a .10 b .22 c .50 d .15 e .03; <9: a .05 b .10 c .40 d .40 e .05), the conditionals set from claims 2–3, 6–7, 9–11; reproduced by `datasets/decomposition.py`
- anchor_estimate: (a) 0.12, (b) 0.25, (c) 0.45, (d) 0.15, (e) 0.03 — Street 4Q26 nights bar 134.0m (+9.9%, Bloomberg MODL 12 Sep, claim 13) less the 1–3 point bucket cushion (claim 4) → a management bucket centred on 7–9%, i.e. "high single digits"; no tradable market exists (claims 14–16)
- anchor_value: P(c) = 0.45 (Bloomberg MODL 4Q26 nights 134.0m, screenshot 2026-09-12, cushion-adjusted)
- final_estimate: (a) 0.21, (b) 0.19, (c) 0.39, (d) 0.17, (e) 0.04
- final_minus_anchor: −0.06 on the leading option (c). NOT_INDEPENDENTLY_DERIVED flag applies by the 10-point rule; the independence is partial: the base rate (claim 1) and the decomposition are built from the letters and the team's Q4 baselines without the Street number, and both land at 0.37–0.40 on their own; the anchor is the Street's Q4 bar passed through the same cushion logic, so the three agree because the mechanism (comp + lap + cushion) is common to all three, not because the anchor was copied. The two places the final differs from the anchor are deliberate: more weight on (a) (0.21 vs 0.12) because the team band still gives a 0.38 chance the Q3 print lands ≥10 and management set the Q3 bucket at the printed rate; less on (b) because a 4Q26 Street bar of 9.9 is itself above every repo model

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) "low double digits" / language implying ≥10% | 0.21 |
| (b) "around 10%" / "high single to low double digits" / "similar to Q3" with Q3 <10% | 0.19 |
| (c) "high single digits" | 0.39 |
| (d) "mid single digits" or lower, or "moderate/decelerate" without a bucket | 0.17 |
| (e) no 4Q26 nights descriptor | 0.04 |
Sum 1.00. Credible range on the leading option: 0.30–0.48 (moves with P(3Q26 ≥10) between 0.25 and 0.55, see §7).

Coherence notes for X01: P(bucket ≥ "around 10", a+b) = 0.40; P(descriptor at or below "high single digits", c+d) = 0.56. Joint structure used: the same 3Q26-print tree as R01/R02 (P(≥10.0) = 0.38 on the team band); (a) is 80% concentrated in the ≥10 branch, (d) is 47% concentrated in the <9 branch.

Extreme-probability gate (any option ≤2%): not triggered at the final vector; (e) sits at 0.04 after the audit below. Resolution-criteria audit for (e): (1) criteria re-read: letter governs, call counts only if the letter is silent, "not stated" resolves (e) when neither states an item; (2) edge cases: a GBV bucket "driven by continued growth in Nights and Seats Booked" with no qualifier (the 1Q26 letter used exactly "driven by growth in Nights and Seats Booked" inside the GBV sentence but added a separate deceleration sentence); a letter that guides GBV only and leaves nights to the call, where the call gives a bucket → still counts (call fills a silent letter); a print-date change → no effect; a dropped KPI (Airbnb has dropped listings growth, LTS share, cross-border) → nights is the headline KPI, not droppable; (3) residual: 0.03 for the qualifier-free GBV construction, 0.01 for a letter format change; (4) 0.04 confirmed. The 0.01 moved from (c) to (e) versus the decomposition is that residual.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| P(3Q26 print ≥10.0%) = 0.38 (team band centre 9.5–9.6, sd 1.48) | Street/Kalshi view, P(≥10) = 0.60 (9–10: 0.28, <9: 0.12): (a) 0.29, (b) 0.20, (c) 0.36, (d) 0.12, (e) 0.03. Team-low view, P(≥10) = 0.25 (9–10: 0.45, <9: 0.30): (a) 0.17, (b) 0.18, (c) 0.41, (d) 0.21, (e) 0.04 |
| Management keeps the bucket format (P(directional-only) ≈ 0.25) | Directional-only at 0.45 with "moderate" the default down-word: (d) 0.26, (c) 0.31, (b) 0.19, (a) 0.20, (e) 0.04 |
| 4Q26 team baseline 8.1 (case B) with 8.9 as the top | Case A (8.9) as the point and management guiding at the Street's 9.9 less a 1-point cushion: (b) 0.28, (c) 0.34, (a) 0.23, (d) 0.12, (e) 0.03 |
| Comp discipline: 1 point harder comp → ~1 point lower bucket (3Q25 template) | Management ignores the comp when October is strong (2Q26 template) and Q3 prints ≥10: (a | ≥10) 0.60 → (a) 0.28, (c) 0.34, (b) 0.19, (d) 0.16, (e) 0.03 |
| Bundle-contribution disclosure returns at ≥2.5 pts (lap not biting) | Would be inside the same letter; if the bundle is still adding, (a)+(b) rise to ≈0.50 jointly with a Q3 print ≥10 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-09-30 | September Inside Airbnb reviews/calendar dumps land; re-run the reviews stays index (q3nowcast E) for the full 3Q26 stay window | Re-set P(3Q26 ≥10): each 0.5pp move in the index centre moves P(≥10) by ≈0.13 and (a) by ≈±0.04, (c) by ∓0.03 (row 1 of §7) |
| 2026-10-02 | Team memo freeze | Carry this vector; note the (a)/(c) split as the memo's base-vs-breaker fork |
| ~2026-10-08 to 10-15 | Airbnb announces the Q3 call date (3–4 weeks ahead in prior years); confirm 5 Nov | No probability change; fix the resolution date |
| 2026-10-22 to 10-24 | Citadel finals | Hold |
| ~2026-10-28 to 10-30 | BKNG and EXPE Q3 prints (EXPE reads through to ABNB; BKNG does not, per the peer study) | If EXPE guides Q4 room nights ≥ Q3 rate: shift 0.03 from (c)/(d) to (a)/(b); if it guides a deceleration of ≥2 points: shift 0.03 the other way |
| 2026-11-05 (est.) | 3Q26 letter published after the close | Resolve by the conventions in §0b. If the letter is silent on nights, read the call before resolving (e) |
| 2026-11-05 | Same letter: bundle-contribution figure, RNPL GBV share, 3Q26 nights print | Feed X01 and C05/C06; the print settles the §7 row-1 sensitivity before the descriptor is read |
