# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A02, question C03. Reproduction script: [datasets/decomposition.py](datasets/decomposition.py) (standard library only; prints the arithmetic, every estimate, and writes `datasets/decomposition_output.csv`).

## 0. Metadata
- question_name: fy26-revenue-guide-language
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` §C03)
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
How will Airbnb's FY26 revenue growth guidance change at the 5 Nov print?
### Resolution Criteria
**Type.** Multiple choice. **Options.** (a) raised: a point estimate or a range whose midpoint exceeds the prior "at least mid-teens" (read as ≥15%) floor by ≥1pt, e.g., "approximately 16%" or "at least 16%"; (b) reiterated: "at least mid-teens" or equivalent unchanged; (c) narrowed to a point at ≈15% ("approximately 15%", "mid-teens"); (d) lowered or softened (any language implying <15% or removing the floor); (e) no FY26 revenue guidance.
### Fine Print
Prior guide from the 2Q26 letter (6 Aug 2026). Resolution date 5 Nov 2026.

Conventions adopted for this forecast:
1. A numeric point or range (growth % or dollars, converted on FY25 revenue $12,241M) resolves on its midpoint: ≥16.0% → (a); 15.0–15.99% → (c); <15.0% → (d). "Approximately 16%" → (a); "approximately 15%" and "15% to 16%" (midpoint 15.5) → (c); "approximately 15.5%" → (c) (below the ≥1pt bar).
2. Descriptive buckets: "high teens" or "mid-to-high teens" (midpoint ≥16.5) → (a); "at least mid teens" or "at least 15%" → (b); "mid teens" without the floor word → (c) as the option text says; "low-to-mid teens" or any <15 wording → (d).
3. An FY26 revenue statement in the letter's Outlook section, or a sentence of the form "this implies full-year growth of X" attached to the 4Q26 range, counts as FY26 revenue guidance. A statement only on the call with the letter silent counts (registry convention: the letter governs where they differ; where the letter is silent the call fills).
4. If the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | FY26 revenue-growth guide history (the first FY revenue guide Airbnb has ever given): 4Q25 letter (12 Feb 2026) "For 2026, we expect year-over-year revenue growth to accelerate to at least low double digits"; 1Q26 letter (7 May 2026) "For 2026, we are raising our guidance and now expect year-over-year revenue growth to accelerate to low to mid teens"; 2Q26 letter (6 Aug 2026) "For full-year 2026, we now expect year-over-year revenue growth to improve to at least mid teens, supported by the accelerated pace of Nights and Seats Booked we've observed, traction from product and growth initiatives, as well as continued strong travel demand." Preamble: "Given this strength, we are raising our full-year outlook for both revenue growth and Adjusted EBITDA Margin." Raised at both updates (+3 and +1 points on the ledger's bucket midpoints). Extract [datasets/ledger_fy_revenue_and_margin_guides.csv](datasets/ledger_fy_revenue_and_margin_guides.csv); verbatim [sources/letter_outlook_extracts_3Q22-2Q26.txt](sources/letter_outlook_extracts_3Q22-2Q26.txt) | data/processed/overnight/02_guidance_ledger.csv rows 172, 182, 192; data/raw/letters/4Q25_d58192dex991.htm, 1Q26_d23351dex991.htm, 2Q26_d70413dex991.htm | 2026-02-12 / 2026-05-07 / 2026-08-06 | 2026-09-17 | yes |
| 2 | How the FY margin guide (the only other FY line) has been handled at November prints: 3Q23 "approximately 150 bps higher than full-year 2022" (from 2Q23's "modestly higher"); 3Q24 "we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%" (from "at least 35%"); 3Q25 "we now expect to deliver an Adjusted EBITDA Margin of approximately 35%" (from "at least 34.5%"). 3 of 3 Novembers converted a floor or qualitative guide into an "approximately" point set above the floor (+50bp both times a numeric floor existed); the FY guide has never been cut. Non-November updates: reiterated 1Q24, 2Q24, 1Q25, 2Q25 ("consistent with our prior guidance"); raised 1Q26, 2Q26 | data/processed/margin_build/05_mgmt_statements_v2/05_guide_language_pattern.csv; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §3.2; ledger rows 89, 123, 162 | 2026-09-14 / 2026-09-11 | 2026-09-17 | yes |
| 3 | November points are conservative: beat vs the November point/approx sentence, FY23/FY24/FY25 = 77 / 90 / 10 bp (mean 59bp); the Q4 margin implied by the November FY sentence was beaten by 3.65 / 4.26 / 0.69 pts. FY24 "approximately 35.5%" delivered 36.4%; FY25 "approximately 35%" delivered 35.1% | data/processed/margin_build/05_mgmt_statements_v2/05_guide_language_stats.csv | 2026-09-14 | 2026-09-17 | yes |
| 4 | Reaction panel `fy_rev_action`: 4Q25 "first" (mid 11), 1Q26 "raised" (+3.0, mid 14), 2Q26 "raised" (+1.0, mid 15); `fy_margin_action` at Q3 prints: 3Q23 raised (+1.5), 3Q24 raised (+0.5), 3Q25 raised (+0.5). Extract [datasets/reaction_panel_fy_actions.csv](datasets/reaction_panel_fy_actions.csv) | data/processed/abnb_guidance_reaction_panel.csv | 2026-09-07 | 2026-09-17 | yes |
| 5 | Actuals: FY25 revenue $12,241M (2,272 + 3,096 + 4,095 + 2,778); 1Q26 $2,678M (+17.87%), 2Q26 $3,608M (+16.54%); 1H26 $6,286M (+17.1%); 9M25 $9,463M; 4Q25 $2,778M. Extract [datasets/driver_history_nights_revenue.csv](../q4-nights-bucket/datasets/driver_history_nights_revenue.csv) | data/processed/abnb_driver_history_quarterly.csv | 2026-08-06 | 2026-09-17 | yes |
| 6 | 3Q26 revenue guide $4,690–4,770M (+15–17%, ~3pt FX after hedging); LSEG 3Q26 consensus $4,744M (n 36, sd 24); team bridge v3 $4,804M (+17.3%); cushion-adjusted from the guide $4,820M. 19 of 19 quarterly revenue guides were beaten at the midpoint, trailing-8 cushion +1.86% (median 1.79%, sd 1.0pp) | data/processed/margin_build/23_final_model/23_vs_consensus.csv ([sources/consensus_23_vs_consensus_LSEG_2026-09-11_copied_2026-09-17.csv](sources/consensus_23_vs_consensus_LSEG_2026-09-11_copied_2026-09-17.csv)); data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv; docs/revenue-forecast-strategy/05_backtests/guidance-policy.md | 2026-09-11 to 2026-09-15 | 2026-09-17 | yes |
| 7 | 4Q26: bridge v3 revenue $3,178M (+14.4%; 80% band 3,156–3,201); implied guide midpoint if the Q4 cushion (3.88%) holds $3,059M; B2 exhibit's unconditional guide-midpoint distribution (kernel, trailing-8 cushion, GBV integrated) mean $3,161M, 80% interval $3,012–3,312M, sd $117M; LSEG 4Q26 consensus $3,162M (n 36, sd 49); Zacks $3,200M (n 10, high outlier) | data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv; docs/revenue-forecast-strategy/05_backtests/B2_Q4_GUIDE_EXHIBIT.md §5; 23_vs_consensus.csv; L0_vintage_register rows CU-2026Q4-* | 2026-09-12 / 2026-09-11 | 2026-09-17 | yes |
| 8 | Q4 revenue-guide cushions (actual ÷ midpoint − 1): 4Q21 6.76%, 4Q22 3.37%, 4Q23 3.16%, 4Q24 2.69%, 4Q25 3.27% → mean 3.85%, median 3.27%, last-3 mean 3.04%; all larger than the trailing-8 all-quarter cushion (1.86%). So the 4Q26 guide midpoint consistent with the team's $3,178M is $3,059–3,084M (Q4 conventions) to $3,120M (all-quarter convention). Computed in [datasets/quarterly_revenue_guide_cushions.csv](datasets/quarterly_revenue_guide_cushions.csv) | data/processed/overnight/02_guidance_ledger.csv (revenue_usd_m range rows) | 2026-09-07 | 2026-09-17 | yes |
| 9 | FY26 growth implied by 9M actual + 4Q26 guide midpoint ([datasets/fy26_guide_arithmetic_grid.csv](datasets/fy26_guide_arithmetic_grid.csv)): Q3 $4,804M with Q4 mid 3,059 / 3,083 / 3,120 / 3,160 → 15.59 / 15.78 / 16.09 / 16.41%; Q3 $4,740M (Street) → 15.06 / 15.26 / 15.56 / 15.89%; Q3 $4,820M → 15.72 / 15.91 / 16.22 / 16.54%. Q4 mid 2,980 (bear, +7.3%) → 14.42–15.07%. Distribution used: Q3 ~ N(4,795, 40), Q4 mid ~ N(3,085, 80) → FY $14,166M, +15.73%, sd 0.73pp; P(≥16.0) 0.35, P(15.0–16.0) 0.49, P(<15.0) 0.16; nearest-integer rounding P(≥16.5) 0.14, P(15.5–16.5) 0.48, P(14.5–15.5) 0.33, P(<14.5) 0.05 | computed from claims 5–8 (`datasets/decomposition.py`) | 2026-09-17 | 2026-09-17 | yes |
| 10 | FY26 revenue consensus: LSEG $14,189.6M (+15.9%, n 44, sd 59); S&P Global MI $14,160M (+15.6%, n 43, 3 Sep); Zacks $14,100M (+15.2%, n 8, 4 Sep; Zacks' own quarterly sum is $14,226M). κ (at-print consensus vs guide midpoint) +0.52–0.60%, sd 0.3pp (LSEG era) → a Street-implied guide of ≈$14,105M, +15.2% | 23_vs_consensus.csv; data/processed/forecast_methods/L0/L0_vintage_register.csv rows CU-FY2026-*; guidance-policy.md §(b) | 2026-09-03 to 2026-09-11 | 2026-09-17 | yes |
| 11 | Insider mechanics §5.5: a "good Q4 guide" includes "FY26 revenue growth raised a notch to 'high teens' or a point estimate"; a "bad one" includes "the FY26 revenue guide merely reiterated (the first non-raise since the guide existed)". §3.2: "The FY guide has only ever been raised, never cut, and the raise lands at the Q3 print" | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md | 2026-09-11 | 2026-09-17 | no |
| 12 | The 3Q25 letter's Outlook (Nov 2025) had a "Full-Year Adjusted EBITDA" bullet but no FY revenue sentence, because the FY revenue guide did not exist until Feb 2026; the 1Q26 and 2Q26 letters both carry a "Full-Year 2026" section with a revenue bullet first and a margin bullet second | data/raw/letters/3Q25_d40503dex991.htm, 1Q26_d23351dex991.htm, 2Q26_d70413dex991.htm | 2025-11-06 to 2026-08-06 | 2026-09-17 | yes |
| 13 | 4Q26 revenue FX: guide-anchored +3pt (Q3) steps to +0.15 to +1.0pt (adopted +1.0, kernel; dollar route +0.15) — the reported Q4 growth rate sheds ~2–3 points of FX tailwind versus Q3 regardless of demand, which is why a Q4 guide of +9–12% follows a Q3 guide of +15–17% | docs/revenue-forecast-strategy/05_backtests/FXSWAP_h2_bridge_kernel_fx.md §1, §4 | 2026-09-12 | 2026-09-17 | no |
| 14 | No tradable market on Airbnb guidance: Polymarket has only resolved "beat quarterly earnings" and price-hit markets; Kalshi has KPI ladders for Q3 and FY2026 nights (zero liquidity, no volume) and nothing on revenue or guidance. Snapshots in [sources/](sources/) (fetched 2026-09-17T02:50Z) | https://gamma-api.polymarket.com/public-search?q=Airbnb; https://api.elections.kalshi.com/trade-api/v2/series?category=Financials | 2026-09-17 | 2026-09-17 | no |
| 15 | Web: Bloomberg 6 Aug 2026 "Airbnb Lifts 2026 Outlook Again on Robust US, European Travel"; Yahoo/Quartz: "analysts had projected revenue of $3.58 billion" for 2Q26 and, per an August report, "analysts, on average, expected a 14% revenue growth jump for Airbnb's full-year 2026". No company statement on the FY guide since 6 Aug (only Chesky's Communacopia remarks, 8 Sep, with no numbers). Snippets, pages not fetched | https://www.bloomberg.com/news/articles/2026-08-06/airbnb-lifts-2026-outlook-again-on-robust-us-european-travel; https://qz.com/airbnb-earnings-q2-2026-full-year-forecast-080726 | 2026-08-06 | 2026-09-17 | no |
| 16 | Sell-side actions in the last ten days (snippets): Raymond James upgrade to Outperform, PT $200 (8 Sep); Truist Hold, PT $161 (15 Sep); Bernstein Buy, PT $217. Nothing on the FY guide wording | https://www.dailypolitical.com/2026/09/15/airbnb-inc-nasdaqabnb-given-average-rating-of-moderate-buy-by-analysts.html | 2026-09-15 | 2026-09-17 | no |
| 17 | Final 72-hour recency checks: no new guidance, no pre-announcement, no confirmed print date (IR events page empty on 2026-09-17) | WebSearch (see §2); https://investors.airbnb.com/events-and-presentations/default.aspx | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing sources: the 11–15 Sep consensus and repo objects (claims 6–7, 10), 2–6 days old against a 49-day window; the recency pass (claim 17) found nothing newer that bears on the number.

## 2. Query Log
1. [repo] `02_guidance_ledger.csv` — FY rows (revenue_yoy_pct, adj_ebitda_margin_*), all 3Q-print rows, revenue range rows for cushions
2. [repo] `abnb_guidance_reaction_panel.csv` — fy_rev_action, fy_margin_action, fy_numeric_present
3. [repo] letters 3Q23/3Q24/3Q25/4Q25/1Q26/2Q26 outlook sections (extract saved to sources/)
4. [repo] `05_mgmt_statements_v2/05_guide_language_pattern.csv`, `05_guide_language_stats.csv`, `05_nov2026_scenarios.csv`
5. [repo] `abnb_driver_history_quarterly.csv`; `23_vs_consensus.csv`; L0 register (FY2026 and 2026Q4 rows); `h2_bridge_v3/*`; B2_Q4_GUIDE_EXHIBIT.md; FXSWAP note; guidance-policy.md; insider mechanics §3, §5
6. [Polymarket public-search] Airbnb; ABNB earnings (shared with C02)
7. [Kalshi API] series?category=Financials → KXABNB, KXABNBA; markets for both (shared with C02)
8. Airbnb full-year 2026 revenue guidance "mid teens" analyst
9. Airbnb ABNB analyst note September 2026
10. [fetch] nasdaq.com Truist upgrade article (timeout)
11. [fetch] investors.airbnb.com/events-and-presentations (no upcoming events)
12. Airbnb guidance outlook latest (final 72-hour neutral recency check — nothing newer than the 6 Aug raise)

WebSearch calls charged to this question: 3 (queries 8, 9, 12).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, "approximately 16%", full-year 2026 revenue growth, "at least mid teens", shareholder letter, 5 November 2026, Q4 2026 revenue guidance

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| November conversion of the floor into an "approximately X" point, as with the margin guide 3 of 3 times (claim 2), with X = 16 → option (a) | leading, 0.37 | The arithmetic (claim 9) centres at 15.7% with P(≥16.0) 0.35 under round-down and P(15.5–16.5) 0.48 under nearest-integer rounding; management's own Q3 beat pattern (19/19) pushes 9M above $11.05bn; the "raised" tone has been used at both prior updates |
| Same conversion with X = 15 ("approximately 15%", "15% to 16%", or "mid teens" without the floor) → option (c) | strong second, 0.28 | November points are conservative (claim 3: FY24 35.5 vs 36.4 delivered); the Street-implied guide is 15.2% (claim 10); with the Street's Q3 ($4,744M) and a Q4 mid at the 5-year Q4 cushion ($3,059M) the arithmetic is 15.06% |
| Reiterate "at least mid teens" → option (b) | kept, 0.18 | Never done in a November letter for the FY line (0 of 3), but the revenue guide is new and a floor that the Q4 range already makes explicit costs nothing to repeat; insider §5.5 treats it as the "bad" outcome the memo watches for |
| Lowered / softened → option (d) | tail, 0.08 | Needs a Q4 guide midpoint below ≈$2,990M on the team's Q3 (+7.6% y/y) or "low-to-mid teens" wording; the Q4/FY27 bridge bear case is $2,961M; the FY guide has never been cut (claims 2, 4) |
| No FY26 revenue sentence → option (e) | tail, 0.09 | The FY section carried margin only in Nov 2025 because the revenue guide did not exist (claim 12); now that it exists, dropping it when the Q4 range fixes the year is possible (Airbnb drops metrics that stop being useful) but the two 2026 letters lead the FY section with it |
| "High teens" or "mid-to-high teens" descriptive raise → (a) | kept inside (a), ≈0.10 | Requires management to describe 15.7–16.4% as high teens; they described 17.1% 1H growth plus a 15–17% Q3 guide as "at least mid teens" in August, so a full bucket step is less likely than a numeric point |
| A dollar range for FY26 revenue (new format) | kept inside the numeric branch | Resolves on the midpoint by convention 1; the midpoint arithmetic is the same as for a growth point |
| Treat the Kalshi FY2026 nights ladder as evidence on the revenue guide | discarded | Zero liquidity and internally inconsistent with the Q3 ladder (C02 log claim 15) |

## 5. Independent Estimates
- base_rate_estimate: (a) 0.45, (b) 0.12, (c) 0.30, (d) 0.03, (e) 0.10 — FY-guide action at November prints is "convert to a point above the floor" 3 of 3 (margin; claim 2) and the revenue guide has been raised 2 of 2 times it was updated (claim 4); the +50bp margin step maps to (a) only when the revenue step is ≥1pt, so the raise mass is split (a) 0.45 / (c) 0.30 on the bucket-step size; (e) 0.10 for the new-line format risk
- decomposition_estimate: (a) 0.37, (b) 0.17, (c) 0.27, (d) 0.09, (e) 0.10 — P(numeric sentence) 0.55 × [(a) 0.48, (c) 0.40, (d) 0.10, (b) 0.02 from the claim-9 arithmetic averaged over round-down and nearest-integer rounding] + P(descriptive) 0.35 × [(a) 0.30, (b) 0.45, (c) 0.15, (d) 0.10] + P(none) 0.10; reproduced by `datasets/decomposition.py`
- anchor_estimate: (a) 0.30, (b) 0.18, (c) 0.35, (d) 0.07, (e) 0.10 — LSEG FY26 consensus $14,190M (+15.9%) and the Street-implied guide $14,105M (+15.2%, κ 0.6%) straddle the 15.5 rounding line, so the Street's number says "approximately 15 or 16" with (c) slightly ahead after the cushion; no market exists (claim 14)
- anchor_value: P(a) = 0.30 (LSEG FY26 revenue consensus $14,189.6M, n 44, 2026-09-11, cushion-adjusted)
- final_estimate: (a) 0.37, (b) 0.18, (c) 0.28, (d) 0.08, (e) 0.09
- final_minus_anchor: +0.07 on the leading option (a). NOT_INDEPENDENTLY_DERIVED by the 10-point rule; the divergence is nameable: the anchor uses the Street's Q3 ($4,744M) and a cushion-deflated guide, while the base rate (claim 2, November conversions above the floor) and the team's Q3 number ($4,804M, above the Street's highest estimate on 19/19 beat history) both push the implied point to 15.7–16.1%. The three estimates put (a) between 0.30 and 0.45 and (c) between 0.27 and 0.35; the final sits inside both ranges. The honest statement is that (a) versus (c) is a rounding question on a 15.5% line, and the vector says so

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) raised: point/range midpoint ≥16% ("approximately 16%", "at least 16%", "high teens") | 0.37 |
| (b) reiterated: "at least mid teens" or equivalent unchanged | 0.18 |
| (c) narrowed to ≈15% ("approximately 15%", "mid teens", "15% to 16%") | 0.28 |
| (d) lowered or softened (<15% implied, floor removed) | 0.08 |
| (e) no FY26 revenue guidance | 0.09 |
Sum 1.00. Credible range on the leading option: 0.25–0.49 (the span of the §7 rows: the Street-centred Q3 print is the low end, B2's kernel guide distribution the high end; in two of the six rows (c) overtakes (a)).

Coherence for X01: P(raised or point ≥15, a+c) = 0.65; P(not weakened, a+b+c) = 0.83; (d) is the only option that co-moves with the short case's "FY26 floor weakened" leg, and it is 0.08.

Extreme-probability gate: no option ≤2%; not triggered. Audit of the two tails anyway: (d) needs a Q4 guide midpoint ≤$2,990M on the team's Q3 or wording that removes the floor — the 4Q25 letter guided 4Q25 at +7–10% after a +10% Q3, so a low-single-digit-teens Q4 range is not unprecedented, which is why (d) is 0.08 and not 0.03. (e) needs the FY revenue bullet to vanish from a section that led with it in May and August; residual 0.09 for the redundancy argument (the Q4 range fixes the year) and for the call-only case where the letter is silent and the call also says nothing.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 guide midpoint ~ N(3,085, 80) (Q4-cushion convention on bridge v3) | B2's kernel distribution, mean 3,161, sd 117: implied FY 16.35% ± 1.01 → given-numeric (a) 0.70, (c) 0.22, (d) 0.06; final (a) 0.49, (b) 0.17, (c) 0.17, (d) 0.07, (e) 0.10 |
| Q3 print ~ N(4,795, 40) (team-centred) | Street-centred N(4,744, 30): implied FY 15.31% ± 0.70 → given-numeric (a) 0.27, (c) 0.49, (d) 0.22; final (a) 0.25, (b) 0.17, (c) 0.32, (d) 0.16, (e) 0.10 — (c) leads |
| P(numeric sentence) = 0.55 | 0.75 (November margin template applied to revenue; descriptive 0.15): (a) 0.40, (b) 0.08, (c) 0.32, (d) 0.09, (e) 0.10. 0.35 (descriptive 0.55): (a) 0.33, (b) 0.25, (c) 0.22, (d) 0.09, (e) 0.10 |
| Round-down convention weighted 50/50 with nearest-integer | Round-down only (conservative November points, claim 3): given-numeric (a) 0.35, (c) 0.48, (d) 0.16 → final (a) 0.30, (b) 0.17, (c) 0.32, (d) 0.12, (e) 0.10 — (c) leads by 2 points |
| FY revenue bullet is retained (P(e) 0.09) | Dropped as redundant with the Q4 range (P(e) 0.25; numeric 0.45, descriptive 0.30): (a) 0.31, (b) 0.14, (c) 0.23, (d) 0.08, (e) 0.25 |

All rows recomputed by the `sensitivities()` block in `datasets/decomposition.py`; the base row reproduces §5's decomposition (a) 0.368, (b) 0.168, (c) 0.273, (d) 0.091, (e) 0.10 before the small hand adjustments toward the base rate stated in §5.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 09-30 | September Inside Airbnb dumps and any FX move (FOMC 16 Sep passed; next 28 Oct) re-set the team's 3Q26 revenue and 4Q26 FX line | Re-run `datasets/decomposition.py` with the refreshed Q3 and Q4-mid centres; each $40M on the 9M+Q4-mid sum moves the implied FY by 0.33pp and (a) by ≈±0.05 |
| 2026-10-02 | Team memo freeze | Carry this vector; the memo's "reiterated = bad" line should quote (b) at 0.18, not as the base case |
| ~2026-10-08 to 10-15 | Airbnb announces the Q3 call date | Fix the resolution date; no change |
| 2026-10-22 to 10-24 | Citadel finals | Hold |
| ~2026-10-28 to 10-30 | EXPE/BKNG Q3 prints and Q4 guides | Demand read-through only; move (d) by ±0.02 if EXPE guides a Q4 deceleration of ≥3 points |
| 2026-11-04 | Register the LSEG FY26 and 4Q26 consensus (pre-print vintage) in `sources/` | Recompute the anchor on the 4 Nov vintage; no change to the final unless consensus moves ≥$60M |
| 2026-11-05 (est.) | 3Q26 letter: read the Full-Year 2026 bullet, then the 4Q26 range; convert dollars on $12,241M | Resolve by the §0b conventions; if the letter is silent, read the call transcript before resolving (e) |
