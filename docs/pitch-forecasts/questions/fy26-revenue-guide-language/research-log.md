# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A02, Fable). Revision 1 was the initial forecast of 2026-09-17. Batch A02, question C03. Reproduction script: [datasets/decomposition_v2.py](datasets/decomposition_v2.py) (standard library only; prints the arithmetic, every estimate and the sensitivity rows, and writes `datasets/decomposition_v2_output.csv`). The revision-1 script `decomposition.py` is kept unchanged for the record. Changes are listed in §10.

## 0. Metadata
- question_name: fy26-revenue-guide-language
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` §C03)
- type: multiple_choice
- run_mode: initial
- run_date: 2026-09-17
- revision: 2
- revised: 2026-09-17
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
| 1 | FY26 revenue-growth guide history (the first FY revenue guide Airbnb has ever given): 4Q25 letter (12 Feb 2026) "For 2026, we expect year-over-year revenue growth to accelerate to at least low double digits"; 1Q26 letter (7 May 2026) "For 2026, we are raising our guidance and now expect year-over-year revenue growth to accelerate to low to mid teens"; 2Q26 letter (6 Aug 2026) "For full-year 2026, we now expect year-over-year revenue growth to improve to at least mid teens, supported by the accelerated pace of Nights and Seats Booked we've observed, traction from product and growth initiatives, as well as continued strong travel demand." Preamble: "Given this strength, we are raising our full-year outlook for both revenue growth and Adjusted EBITDA Margin." Raised at both updates (+3 and +1 points on the ledger's bucket midpoints; 2 of 2 updates, both at non-November prints — there is no prior November update of this line, A02-04). Extract [datasets/ledger_fy_revenue_and_margin_guides.csv](datasets/ledger_fy_revenue_and_margin_guides.csv); verbatim [sources/letter_outlook_extracts_3Q22-2Q26.txt](sources/letter_outlook_extracts_3Q22-2Q26.txt) | data/processed/overnight/02_guidance_ledger.csv rows 172, 182, 192; data/raw/letters/4Q25_d58192dex991.htm, 1Q26_d23351dex991.htm, 2Q26_d70413dex991.htm | 2026-02-12 / 2026-05-07 / 2026-08-06 | 2026-09-17 | yes |
| 2 | How the FY margin guide (the only other FY line) has been handled at November prints **when a same-year FY guide existed at the prior print (4 cases, A02-04)**: **3Q22 — the 2Q22 letter's "we continue to forecast delivering Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021" does not appear in the 3Q22 letter (omitted; `fy_sentence_type` none)**; 3Q23 "approximately 150 bps higher than full-year 2022" (from 2Q23's "modestly higher"); 3Q24 "we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%" (from "at least 35%"); 3Q25 "we now expect to deliver an Adjusted EBITDA Margin of approximately 35%" (from "at least 34.5%"). So 3 of 4 Novembers converted the FY sentence into an "approximately" point above it, 1 of 4 dropped it, 0 of 4 reiterated; both numeric-floor years converted, by **+50bp** each (not +1pt). 3Q21 also had no FY sentence, but no FY21 guide existed. The FY guide has never been cut. Non-November updates: reiterated 1Q24, 2Q24, 1Q25, 2Q25 ("consistent with our prior guidance"); raised 1Q26, 2Q26 | data/processed/margin_build/05_mgmt_statements_v2/05_guide_language_pattern.csv (rows 2Q22, 3Q22, 3Q23, 3Q24, 3Q25); data/raw/letters/2Q22_d353427dex991.htm, 3Q22_d408297dex991.htm; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §3.2; ledger rows 89, 123, 162 | 2026-09-14 / 2022-08-02 / 2022-11-01 / 2026-09-11 | 2026-09-17 | yes |
| 3 | November points are conservative: beat vs the November point/approx sentence, FY23/FY24/FY25 = 77 / 90 / 10 bp (mean 59bp, n 3); the Q4 margin implied by the November FY sentence was beaten by 3.65 / 4.26 / 0.69 pts. FY24 "approximately 35.5%" delivered 36.4%; FY25 "approximately 35%" delivered 35.1%. These are margin analogies; no revenue-line observation exists | data/processed/margin_build/05_mgmt_statements_v2/05_guide_language_stats.csv | 2026-09-14 | 2026-09-17 | yes |
| 4 | Reaction panel `fy_rev_action`: 4Q25 "first" (mid 11), 1Q26 "raised" (+3.0, mid 14), 2Q26 "raised" (+1.0, mid 15); `fy_margin_action` at Q3 prints: 3Q23 raised (+1.5), 3Q24 raised (+0.5), 3Q25 raised (+0.5). Extract [datasets/reaction_panel_fy_actions.csv](datasets/reaction_panel_fy_actions.csv) | data/processed/abnb_guidance_reaction_panel.csv | 2026-09-07 | 2026-09-17 | yes |
| 5 | Actuals: FY25 revenue $12,241M (2,272 + 3,096 + 4,095 + 2,778); 1Q26 $2,678M (+17.87%), 2Q26 $3,608M (+16.54%); 1H26 $6,286M (+17.1%); 9M25 $9,463M; 4Q25 $2,778M. Extract [datasets/driver_history_nights_revenue.csv](../q4-nights-bucket/datasets/driver_history_nights_revenue.csv) | data/processed/abnb_driver_history_quarterly.csv | 2026-08-06 | 2026-09-17 | yes |
| 6 | 3Q26 revenue guide $4,690–4,770M (+15–17%, ~3pt FX after hedging); LSEG 3Q26 consensus $4,744.3M (**revenue n 37**, sd 24.3; revenue observation date **2026-09-07**, row date 2026-09-11 — A02-14); team bridge v3 $4,804M (+17.3%); cushion-adjusted from the guide $4,820M. 19 of 19 quarterly revenue guides were beaten at the midpoint (14/14 W1, 10/10 W2; 15/19 above the top), trailing-8 cushion +1.86% (median 1.79%, sd 1.0pp) | data/processed/margin_build/03_consensus_pit/03_current_consensus.csv (provenance); data/processed/margin_build/23_final_model/23_vs_consensus.csv ([sources/consensus_23_vs_consensus_LSEG_2026-09-11_copied_2026-09-17.csv](sources/consensus_23_vs_consensus_LSEG_2026-09-11_copied_2026-09-17.csv)); data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv; docs/revenue-forecast-strategy/05_backtests/guidance-policy.md | 2026-09-07 (obs) / 2026-09-11 (row) / 2026-09-15 | 2026-09-17 | yes |
| 7 | 4Q26: bridge v3 revenue $3,178M (+14.4%); the bridge's $3,156–3,201M is the **historical min/max GBV-to-revenue conversion envelope with lagged GBV held fixed** (`analysis/src/h1_to_h2_bridge_v3.py` lines 436–437), not an 80% predictive interval (A02-07); implied guide midpoint if the Q4 cushion (3.88%) holds $3,059M; B2 exhibit's unconditional guide-midpoint distribution (kernel, trailing-8 cushion, GBV integrated) mean $3,161M, 80% interval $3,012–3,312M, sd $117M; LSEG 4Q26 consensus $3,161.8M (revenue n 37, sd 48.6, obs 2026-09-07); Zacks $3,200M (n 10, high outlier) | data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv; analysis/src/h1_to_h2_bridge_v3.py; docs/revenue-forecast-strategy/05_backtests/B2_Q4_GUIDE_EXHIBIT.md §5; 03_current_consensus.csv; L0_vintage_register rows CU-2026Q4-* | 2026-09-12 / 2026-09-11 | 2026-09-17 | yes |
| 8 | Q4 revenue-guide cushions (actual ÷ midpoint − 1): 4Q21 6.76%, 4Q22 3.37%, 4Q23 3.16%, 4Q24 2.69%, 4Q25 3.27% → mean 3.85%, median 3.27%, last-3 mean 3.04%; all larger than the trailing-8 all-quarter cushion (1.86%). So the 4Q26 guide midpoint consistent with the team's $3,178M is $3,059–3,084M (Q4 conventions) to $3,120M (all-quarter convention). Computed in [datasets/quarterly_revenue_guide_cushions.csv](datasets/quarterly_revenue_guide_cushions.csv) | data/processed/overnight/02_guidance_ledger.csv (revenue_usd_m range rows) | 2026-09-07 | 2026-09-17 | yes |
| 9 | FY26 growth implied by 9M actual + 4Q26 guide midpoint ([datasets/fy26_guide_arithmetic_grid.csv](datasets/fy26_guide_arithmetic_grid.csv)): Q3 $4,804M with Q4 mid 3,059 / 3,083 / 3,120 / 3,160 → 15.59 / 15.78 / 16.09 / 16.41%; Q3 $4,740M (Street) → 15.06 / 15.26 / 15.56 / 15.89%; Q3 $4,820M → 15.72 / 15.91 / 16.22 / 16.54%. Q4 mid 2,980 (bear, +7.3%) → 14.42–15.07%. Distribution used: Q3 ~ N(4,795, 40), Q4 mid ~ N(3,085, 80) — **both sds are assumptions**, and revision 2 adds a shared-demand correlation ρ = 0.5 between the Q3 print and the Q4 guide (A02-07) → FY $14,166M, +15.73%, **sd 0.86pp** (0.73 at ρ 0, 0.94 at ρ 0.8); P(≥16.0) 0.38, P(15.0–16.0) 0.42, P(<15.0) 0.20; nearest-integer rounding P(≥15.5) 0.60, P(14.5–15.5) 0.32, P(<14.5) 0.08. Seeded Monte-Carlo check (seed 20260917, 2×10⁵ draws) matches to ±0.002 | computed from claims 5–8 (`datasets/decomposition_v2.py`) | 2026-09-17 | 2026-09-17 | yes |
| 10 | FY26 revenue consensus: LSEG $14,189.6M (+15.9%, n 44, sd 59, obs 2026-09-07); S&P Global MI $14,160M (+15.6%, n 43, 3 Sep); Zacks $14,100M (+15.2%, n 8, 4 Sep; Zacks' own quarterly sum is $14,226M). κ (at-print consensus vs the quarterly guide midpoint) mean **+0.60%, n 12, sd 0.30pp; trailing-8 +0.52%** (L0 AP- rows matched to quarterly guides). **Corrected (A02-01):** κ is a quarterly quantity and applies only to the not-yet-guided quarter. Street-implied FY guide = 1H26 actual $6,286M + LSEG 3Q26 $4,744.3M + LSEG 4Q26 $3,161.8M / 1.006 = **$14,173.3M, +15.79%** (deflating only the Q4 leg of the annual figure gives $14,170.7M, +15.76%). Revision 1 deflated the whole FY consensus ($14,105M, +15.23%), which wrongly discounted revenue already reported; the correction crosses the 15.5% rounding line | 23_vs_consensus.csv; 03_current_consensus.csv; data/processed/forecast_methods/L0/L0_vintage_register.csv rows CU-FY2026-*, AP-*-revenue; guidance-policy.md §(b); recomputed by audits/A02-reproduce.py | 2026-09-03 to 2026-09-11 | 2026-09-17 | yes |
| 11 | Insider mechanics §5.5: a "good Q4 guide" includes "FY26 revenue growth raised a notch to 'high teens' or a point estimate"; a "bad one" includes "the FY26 revenue guide merely reiterated (the first non-raise since the guide existed)". §3.2: "The FY guide has only ever been raised, never cut, and the raise lands at the Q3 print" | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md | 2026-09-11 | 2026-09-17 | no |
| 12 | The 3Q25 letter's Outlook (Nov 2025) had a "Full-Year Adjusted EBITDA" bullet but no FY revenue sentence, because the FY revenue guide did not exist until Feb 2026; the 1Q26 and 2Q26 letters both carry a "Full-Year 2026" section with a revenue bullet first and a margin bullet second. The one precedent for an existing FY line vanishing in November (3Q22, claim 2) was a qualitative y/y margin sentence, not a headline numeric line | data/raw/letters/3Q25_d40503dex991.htm, 1Q26_d23351dex991.htm, 2Q26_d70413dex991.htm, 3Q22_d408297dex991.htm | 2025-11-06 to 2026-08-06; 2022-11-01 | 2026-09-17 | yes |
| 13 | 4Q26 revenue FX: guide-anchored +3pt (Q3) steps to +0.15 to +1.0pt (adopted +1.0, kernel; dollar route +0.15) — the reported Q4 growth rate sheds ~2–3 points of FX tailwind versus Q3 regardless of demand, which is why a Q4 guide of +9–12% follows a Q3 guide of +15–17% | docs/revenue-forecast-strategy/05_backtests/FXSWAP_h2_bridge_kernel_fx.md §1, §4 | 2026-09-12 | 2026-09-17 | no |
| 14 | No tradable market on Airbnb guidance: Polymarket has only resolved "beat quarterly earnings" and price-hit markets; Kalshi has KPI ladders for Q3 and FY2026 nights (thin — a few hundred contracts per rung traded around the August guide, `volume_24h` 0, `liquidity_dollars` 0; corrected from "zero liquidity, no volume", A02-05) and nothing on revenue or guidance. Snapshots in [sources/](sources/) (fetched 2026-09-17T02:50Z) | https://gamma-api.polymarket.com/public-search?q=Airbnb; https://api.elections.kalshi.com/trade-api/v2/series?category=Financials | 2026-09-17 | 2026-09-17 | no |
| 15 | Web: Bloomberg 6 Aug 2026 "Airbnb Lifts 2026 Outlook Again on Robust US, European Travel"; Yahoo/Quartz: "analysts had projected revenue of $3.58 billion" for 2Q26 and, per an August report, "analysts, on average, expected a 14% revenue growth jump for Airbnb's full-year 2026". No company statement on the FY guide since 6 Aug (only Chesky's Communacopia remarks, 8 Sep, with no numbers). Snippets, pages not fetched; zero weight in the number | https://www.bloomberg.com/news/articles/2026-08-06/airbnb-lifts-2026-outlook-again-on-robust-us-european-travel; https://qz.com/airbnb-earnings-q2-2026-full-year-forecast-080726 | 2026-08-06 | 2026-09-17 | no |
| 16 | Sell-side actions in the last ten days (snippets): Raymond James upgrade to Outperform, PT $200 (8 Sep); Truist Hold, PT $161 (15 Sep); Bernstein Buy, PT $217. Nothing on the FY guide wording; zero weight | https://www.dailypolitical.com/2026/09/15/airbnb-inc-nasdaqabnb-given-average-rating-of-moderate-buy-by-analysts.html | 2026-09-15 | 2026-09-17 | no |
| 17 | Final 72-hour recency checks: no new guidance, no pre-announcement, no confirmed print date (IR events page rendered empty on 2026-09-17; dynamically loaded, so not conclusive) | WebSearch (see §2); https://investors.airbnb.com/events-and-presentations/default.aspx | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing sources: the 7–11 Sep consensus vintage and the 11–15 Sep repo objects (claims 6–7, 10), 2–10 days old against a 49-day window; the consensus observation date (7 Sep) is 10 days old, above the 7-day cap, so monitoring row 6 re-registers it before the print. The recency pass (claim 17) found nothing newer that bears on the number.

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
13. [repo, revision 2] data/raw/letters/2Q22_d353427dex991.htm and 3Q22_d408297dex991.htm — FY2022 margin sentences (A02-04); 05_guide_language_pattern.csv rows 3Q21–3Q25 `fy_sentence_type`
14. [repo, revision 2] data/processed/margin_build/03_consensus_pit/03_current_consensus.csv — revenue_n, revenue_obs_date, as_of_row_date (A02-14)
15. [repo, revision 2] analysis/src/h1_to_h2_bridge_v3.py lines 425–445 — `revenue_low/high` construction (A02-07)
16. [repo, revision 2] L0_vintage_register.csv AP-*-revenue rows matched to quarterly revenue guides — κ n 12, mean 0.604%, sd 0.30pp, trailing-8 0.516% (A02-01, via audits/A02-reproduce.py under `py -3.13`)
17. [repo, revision 2] QUESTIONS.md X01 block — short-case leg is "FY26 margin floor weakened" (A02-10)

WebSearch calls charged to this question: 3 (queries 8, 9, 12). No WebSearch in revision 2.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, "approximately 16%", full-year 2026 revenue growth, "at least mid teens", shareholder letter, 5 November 2026, Q4 2026 revenue guidance

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| November conversion of the floor into an "approximately X" point, as with the margin guide 3 of 4 times an FY guide existed (claim 2), with X = 16 → option (a) | leading, 0.36 | The arithmetic (claim 9) centres at 15.7% with P(≥16.0) 0.38 under round-down and P(≥15.5) 0.60 under nearest-integer rounding; the corrected Street-implied guide is 15.8% (claim 10), on the same side of the 15.5 line; management's own Q3 beat pattern (19/19) pushes 9M above $11.05bn; the "raised" tone has been used at both prior updates |
| Same conversion with X = 15 ("approximately 15%", "15% to 16%", "approximately 15.5%", or "mid teens" without the floor) → option (c) | strong second, 0.28 | November points are conservative (claim 3: FY24 35.5 vs 36.4 delivered); the two numeric-floor conversions stepped +0.5, which for revenue is "approximately 15.5%" → (c) by convention 1; with the Street's Q3 ($4,744M) and a Q4 mid at the 5-year Q4 cushion ($3,059M) the arithmetic is 15.06% |
| Reiterate "at least mid teens" → option (b) | kept, 0.16 | Never done in a November letter for an existing FY line (0 of 4), but the revenue guide is new and a floor that the Q4 range already makes explicit costs nothing to repeat; insider §5.5 treats it as the "bad" outcome the memo watches for |
| Lowered / softened → option (d) | tail, 0.08 | Needs a Q4 guide midpoint below ≈$2,990M on the team's Q3 (+7.6% y/y) or "low-to-mid teens" wording; the Q4/FY27 bridge bear case is $2,961M; the FY guide has never been cut (claims 2, 4). ρ 0.5 raises the numeric-branch (d) from 0.10 to 0.14 (claim 9) |
| No FY26 revenue sentence → option (e) | tail, 0.12 (was 0.09) | **Revised up (A02-04):** an existing FY sentence was dropped in November once in four cases (3Q22, claim 2), when the Q4 guide had made a qualitative y/y sentence redundant. The 2026 revenue line is a headline numeric line that the two 2026 letters lead with (claim 12), and the numeric margin floor was retained and converted 2/2, so the omission share is shaded well below the raw 1/4 |
| "High teens" or "mid-to-high teens" descriptive raise → (a) | kept inside (a), ≈0.10 | Requires management to describe 15.7–16.4% as high teens; they described 17.1% 1H growth plus a 15–17% Q3 guide as "at least mid teens" in August, so a full bucket step is less likely than a numeric point |
| A dollar range for FY26 revenue (new format) | kept inside the numeric branch | Resolves on the midpoint by convention 1; the midpoint arithmetic is the same as for a growth point |
| Treat the Kalshi FY2026 nights ladder as evidence on the revenue guide | discarded | Thin and not a revenue or guidance market (claim 14) |
| Deflate the whole FY consensus by the quarterly κ (revision-1 anchor) | discarded (A02-01) | κ is measured on quarterly guides; 1H26 is reported and 3Q26 is already guided. Replaced by the quarter-sum construction in claim 10 |
| Read the bridge's $3,156–3,201M as an 80% interval for 4Q26 revenue | discarded (A02-07) | It is the min/max conversion envelope with lagged GBV fixed (claim 7); the Q4-mid sd of $80M is an assumption, stated as such |

## 5. Independent Estimates
- base_rate_estimate: (a) 0.33, (b) 0.15, (c) 0.33, (d) 0.04, (e) 0.15 — the November reference class with an existing same-year FY guide (n 4, margin line): convert to a point 3, omit 1, reiterate 0; raw Laplace over the three actions 0.57 / 0.29 / 0.14; regime-conditioned to convert 0.70 / omit 0.15 / reiterate 0.15 because both numeric-floor years converted (2/2) and the 2026 letters lead with the revenue line (claim 12). The analogy carries no level — the +0.5pp margin steps map to "approximately 15.5%" (c) as readily as to a rounded "approximately 16%" (a) — so the conversion mass is split 0.47 / 0.47 / 0.06 (a / c / d). **This is an analogical judgment on a margin line with n 4, not an empirical MC frequency for the revenue line, which has never been updated in November** (A02-04)
- decomposition_estimate: (a) 0.36, (b) 0.16, (c) 0.25, (d) 0.11, (e) 0.12 — P(numeric sentence) 0.55 × [(a) 0.48, (c) 0.36, (d) 0.14, (b) 0.02 from the claim-9 arithmetic with ρ 0.5, averaged over round-down and nearest-integer wording] + P(descriptive) 0.33 × [(a) 0.30, (b) 0.45, (c) 0.15, (d) 0.10] + P(none) 0.12; reproduced by `datasets/decomposition_v2.py`
- anchor_estimate: (a) 0.38, (b) 0.16, (c) 0.28, (d) 0.06, (e) 0.12 — the corrected Street-implied FY guide $14,173.3M (+15.79%, claim 10; sd 0.57pp from a $50M Q3 print error, κ's 0.3pp and the Q4 consensus dispersion $49M) passed through the same format and rounding mapping as the decomposition. **Dependent construction (A02-06):** the level is the Street's, the vector is ours; the only independent content is the level, 15.79% vs the team's 15.73%, which agree within 0.06pp. No market exists (claim 14)
- anchor_value: P(a) = 0.38 (LSEG FY26 revenue consensus components, obs 2026-09-07 / row 2026-09-11, Q4 leg deflated by κ 0.6%, mapped as above)
- final_estimate: (a) 0.36, (b) 0.16, (c) 0.28, (d) 0.08, (e) 0.12 — stated blend 0.5 × decomposition + 0.3 × base rate + 0.2 × anchor = (0.356, 0.156, 0.280, 0.079, 0.129), rounded to sum 1
- final_minus_anchor: −0.02 on the leading option (a). NOT_INDEPENDENTLY_DERIVED: all three vectors share the arithmetic centre (team 15.73 / Street 15.79) and the same language mapping; revision 1's +0.07 "divergence" was an artefact of the mis-constructed anchor (A02-01) and is withdrawn. The honest statement is that (a) versus (c) is a rounding question on a 15.5% line whose centre sits 0.2–0.3pp above it, and the vector says so; the residual weight on (b) and (e) is the format question (does the sentence become a number, stay a floor, or vanish), which no level can settle

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) raised: point/range midpoint ≥16% ("approximately 16%", "at least 16%", "high teens") | 0.36 |
| (b) reiterated: "at least mid teens" or equivalent unchanged | 0.16 |
| (c) narrowed to ≈15% ("approximately 15%", "approximately 15.5%", "mid teens", "15% to 16%") | 0.28 |
| (d) lowered or softened (<15% implied, floor removed) | 0.08 |
| (e) no FY26 revenue guidance | 0.12 |
Sum 1.00. Sensitivity range on the leading option (a): 0.26–0.47 (the span of the §7 decomposition rows: the Street-centred Q3 print is the low end, B2's kernel guide distribution or the Street-implied Q4 guide the high end; in two rows (c) overtakes (a)). This is a range over stated assumption reversals, not a posterior interval with a coverage level (A02-15).

Coherence for X01: P(raised or point ≥15, a+c) = 0.64; P(not weakened, a+b+c) = 0.80. **X01's short-case leg is "FY26 margin floor weakened" (C04), not revenue language; C03(d) does not satisfy it** (A02-10, revision 1's mapping withdrawn). C03(d) and C04(d) are positively correlated through the Q4 revenue guide (a Q4 midpoint below ≈$2,990M lowers both the implied FY revenue and the achievable FY margin); X01 should assume P(C04 = d | C03 = d) ≈ 0.5 versus the C04 marginal, stated as a joint assumption, not a substitution.

Extreme-probability gate: no option ≤2%; not triggered. Audit of the two tails anyway: (d) needs a Q4 guide midpoint ≤$2,990M on the team's Q3 or wording that removes the floor — the 4Q25 letter guided 4Q25 at +7–10% after a +10% Q3, so a low-single-digit-teens Q4 range is not unprecedented, which is why (d) is 0.08 and not 0.03. (e) needs the FY revenue bullet to vanish from a section that led with it in May and August; 0.12 for the redundancy argument (the Q4 range fixes the year; the 3Q22 precedent) and for the call-only case where the letter is silent and the call also says nothing.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 guide midpoint ~ N(3,085, 80) (Q4-cushion convention on bridge v3) | B2's kernel distribution, mean 3,161, sd 117: implied FY 16.35% ± 1.15 → given-numeric (a) 0.68, (c) 0.21, (d) 0.09; decomposition (a) 0.47, (b) 0.16, (c) 0.17, (d) 0.08, (e) 0.12. Street-implied Q4 guide mid 3,143 (κ on Q4): FY 16.20% → (a) 0.47, (c) 0.19, (d) 0.06 |
| Q3 print ~ N(4,795, 40) (team-centred) | Street-centred N(4,744, 30): implied FY 15.31% ± 0.80 → given-numeric (a) 0.30, (c) 0.44, (d) 0.25; decomposition (a) 0.26, (b) 0.16, (c) 0.29, (d) 0.17, (e) 0.12 — (c) leads |
| ρ(Q3 print, Q4 guide) = 0.5 | ρ 0 (independent errors, revision 1): sd 0.73pp → (a) 0.36, (c) 0.27, (d) 0.09. ρ 0.8: sd 0.94pp → (a) 0.36, (c) 0.24, (d) 0.12. ρ moves (c)/(d), not (a) |
| P(numeric sentence) = 0.55 | 0.75 (November margin template applied to revenue; descriptive 0.13): (a) 0.40, (b) 0.07, (c) 0.29, (d) 0.12, (e) 0.12. 0.35 (descriptive 0.53): (a) 0.33, (b) 0.25, (c) 0.21, (d) 0.10, (e) 0.12 |
| Round-down convention weighted 50/50 with nearest-integer | Round-down only (conservative November points, claim 3): given-numeric (a) 0.37, (c) 0.42, (d) 0.20 → (a) 0.30, (b) 0.16, (c) 0.28, (d) 0.14, (e) 0.12 — tie. Nearest-integer only: (a) 0.42, (c) 0.22, (d) 0.08 |
| FY revenue bullet is retained (P(e) 0.12) | Dropped as redundant with the Q4 range (P(e) 0.25; numeric 0.45, descriptive 0.30): (a) 0.31, (b) 0.14, (c) 0.21, (d) 0.09, (e) 0.25 |

All rows recomputed by the `sens()` block in `datasets/decomposition_v2.py` on the decomposition alone; the base row reproduces §5's decomposition (a) 0.363, (b) 0.159, (c) 0.250, (d) 0.108, (e) 0.120.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 09-30 | September Inside Airbnb dumps and any FX move (FOMC 16 Sep passed; next 28 Oct) re-set the team's 3Q26 revenue and 4Q26 FX line | Re-run `datasets/decomposition_v2.py` with the refreshed Q3 and Q4-mid centres; each $40M on the 9M+Q4-mid sum moves the implied FY by 0.33pp and (a) by ≈±0.05 |
| 2026-10-02 | Team memo freeze | Carry this vector; the memo's "reiterated = bad" line should quote (b) at 0.16, not as the base case; quote (e) 0.12 as the format risk |
| ~2026-10-08 to 10-15 | Airbnb announces the Q3 call date | Fix the resolution date; no change |
| 2026-10-22 to 10-24 | Citadel finals | Hold |
| ~2026-10-28 to 10-30 | EXPE/BKNG Q3 prints and Q4 guides | Demand read-through only; move (d) by ±0.02 if EXPE guides a Q4 deceleration of ≥3 points |
| 2026-11-04 | Register the LSEG FY26, 3Q26 and 4Q26 consensus (pre-print vintage) in `sources/` with vendor, observation date and row date | Recompute the anchor by the claim-10 construction (deflate the Q4 leg only); no change to the final unless the Street-implied FY guide moves ≥ $60M (≈0.5pp) |
| 2026-11-05 (est.) | 3Q26 letter: read the Full-Year 2026 bullet, then the 4Q26 range; convert dollars on $12,241M | Resolve by the §0b conventions; if the letter is silent, read the call transcript before resolving (e) |

## 9. Impact
Not applicable (core question, not R/B).

## 10. Revision notes
Revision 2 (2026-09-17) responds to `audits/A02-research-audit.md`; the finding-by-finding rulings are in `audits/A02-audit-response.md`. Vector (a–e): revision 1 (0.37, 0.18, 0.28, 0.08, 0.09) → revision 2 **(0.36, 0.16, 0.28, 0.08, 0.12)**; Astra's comparison (0.35, 0.19, 0.21, 0.10, 0.15).
- A02-01 (accepted): the anchor now deflates only the 4Q26 consensus by κ (claim 10: $14,173.3M, +15.79%, vs the wrong $14,105M, +15.23%); κ re-measured (n 12, 0.60%, sd 0.30pp, trailing-8 0.52%). The anchor vector moves from (a) 0.30 to (a) 0.38, and the revision-1 "+0.07 divergence" is withdrawn.
- A02-04 (accepted): claim 2 now reports 3/4 November conversions with 1/4 omission (3Q22); the numeric-floor steps are +50bp; the base rate is rebuilt on {convert, omit, reiterate} with raw and regime-conditioned versions and labelled analogical; P(none) raised from 0.10 to 0.12.
- A02-05 (accepted): Kalshi description corrected (claim 14).
- A02-06 (accepted): all three estimates labelled dependent constructions with the mapping shown; blend weights stated.
- A02-07 (accepted): the bridge band is named a conversion envelope (claim 7); the $40M/$80M sds are labelled assumptions; ρ 0.5 adopted with ρ 0 and 0.8 as sensitivities (claim 9, §7).
- A02-10 (accepted): the X01 mapping of C03(d) onto the margin-floor leg removed; a joint assumption with C04(d) stated instead (§6).
- A02-14 (accepted): revenue n 37 and observation date 7 Sep / row date 11 Sep recorded (claims 6, 7, 10); provenance file cited; freshness note updated.
- A02-15 (accepted): "credible range" renamed sensitivity range (§6).
- A02-02, -03, -08, -09, -11, -12, -13, -16 concern C02 only.
- Monitoring row 6 now specifies the corrected anchor construction and a $60M trigger.
- The JSON `forecasts/2026-09-17-forecast.json` is rewritten with `"revision": 2`.
