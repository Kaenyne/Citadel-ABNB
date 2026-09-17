# RESEARCH LOG

Revision 2 (2026-09-17, revised after audit A16 `docs/pitch-forecasts/audits/A16-research-audit.md` and the response `A16-audit-response.md`; revision 1 was the initial forecast, Fable 5.1, batch A16). Companion questions: B08 `bonus-ai-hosting-cost-step`, B10 `bonus-interest-income-falls`, B17 `bonus-take-rate-guided-down`. Reused inputs: M7 below-EBITDA bridge (`docs/margin-build/notes/M7_below_ebitda.md`). Reproduction: `datasets/b09_model.py` (revision 1, numpy/pandas, seed 20260917, n 400,000) → `b09_results.csv`, `b09_history.csv`, left untouched as the audit trail; the revision-2 route calibration, the §7 blend loop and the companion quantiles are re-run in `../../audits/A16-reproduce.py` (audit script, saved verbatim) and in the response's recomputation block. Revision-2 headline **0.08** (rev 1: 0.10).

## 0. Metadata
- question_name: bonus-sbc-step-up
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B09)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
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
Will 4Q26 stock-based compensation be ≥ $500M?
### Resolution Criteria
Yes if 4Q26 SBC per the 4Q26 release ≥ $500M (4Q25 $400M; team path $465M). Resolution ~11 Feb 2027.
### Fine Print
(none beyond the registry header conventions.)

Conventions adopted: (1) the object is the "Stock-based compensation expense" line in the 4Q26 release's adjusted-EBITDA reconciliation (three months ended 31 Dec 2026), in $ millions as printed; (2) the registry's "4Q25 $400M" is the driver-history figure; the releases print **4Q25 $411M** (4Q25 letter: "$368 $411 $1,407 $1,592"; the 2Q26 letter's nine-quarter table: 382 362 368 358 424 399 411 410 487) and FY25 $1,592M = 358 + 424 + 399 + 411. The threshold is fixed at $500M and is unaffected; the needed y/y is +21.7% on $411M (+25.0% on $400M); the log uses the printed $411M; (3) a restatement of prior quarters does not move the threshold; (4) if the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | SBC by quarter ($M, release reconciliation tables): 1Q22 195, 2Q22 247, 3Q22 234, 4Q22 254; 1Q23 240, 2Q23 304, 3Q23 286, 4Q23 290; 1Q24 295, 2Q24 382, 3Q24 362, 4Q24 368; 1Q25 358, 2Q25 424, 3Q25 399, 4Q25 411; 1Q26 410, 2Q26 487. FY: 2022 930, 2023 1,120 (+20%), 2024 1,407 (+26%), 2025 1,592 (+13%). Y/y: 4Q24 +26.9%, 1Q25 +21.4%, 2Q25 +11.0%, 3Q25 +10.2%, 4Q25 +11.7%, 1Q26 +14.5%, 2Q26 +14.9% | `data/raw/letters/4Q25_d58192dex991.htm`, `4Q24_d915198dex991.htm`, `2Q26_d70413dex991.htm` (reconciliation tables); `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (sbc_total_is); `datasets/b09_history.csv` | 2026-08-06 (last print) | 2026-09-17 | yes |
| 2 | Q4 seasonality: SBC steps up in Q2 (the annual grant cycle: 2Q24 +29% q/q, 2Q25 +18%, 2Q26 +19%) and Q4 prints below Q2: Q4/Q2 = 2022 1.028, 2023 0.954, 2024 0.963, 2025 0.969 (mean 0.979 all four, 0.962 for 2023–25, sd 0.008). On 2Q26's $487M the 2023–25 ratio gives $469M; $500M needs Q4/Q2 ≥ 1.027, seen once (2022, the post-IPO double-trigger regime) | claim 1; `datasets/b09_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 3 | Management's SBC statements: 4Q23 letter (Feb 2024): FY23 SBC +20% "as anticipated"; "We anticipate a similar year-over-year growth rate for SBC expense in 2024. Beyond 2024, after the last of the double-trigger RSUs … have vested or expired, we anticipate that SBC expense will grow largely in-line with headcount growth." 4Q24 letter (Feb 2025): FY24 +26% "driven by headcount growth and the accounting for our RSU awards"; "the remaining portion of the double trigger RSUs … fully vested in 2024. In 2025, we anticipate that the growth rate of SBC will approximate headcount growth." 4Q25 letter (Feb 2026): "For full-year 2025, SBC expense increased 13%, driven by headcount growth. **In 2026, we anticipate that the year-over-year growth rate of SBC and headcount will be lower than 2025.**" Guide record — **corrected in revision 2 (A16-04)**: revision 1 took the outcomes from `02_guidance_ledger.csv`'s `sbc_yoy_pct` rows, whose `actual` column reproduces **only from the erroneous `abnb_driver_history_quarterly.csv`** (4Q23 270, 4Q24 400) that convention (2) has already declared wrong. On the **printed releases** (1,120 / 1,407 / 1,592 against 930 / 1,120 / 1,407) FY23 was **+20.43%**, FY24 **+25.63%**, FY25 **+13.15%**, against the ledger's 18.28 / 30.82 / 9.87. So: FY23 "~20%" → **met** (not beaten); FY24 "~20%" (1Q24) → **missed by 5.6 points**, not 10.8; FY24 "~25%" (3Q24) → **met**, not missed by 5.8; FY25 "approximate headcount growth" → +13.15 vs headcount +12.3 (met). The record behind "management misses its own SBC sentence" is **1 of 4, and the single miss is half the stated size**. **This is a repo data defect, not only a B09 error: `02_guidance_ledger.csv` is a point-in-time-clean ledger carrying a wrong actual, and anything else in the run that uses `sbc_yoy_pct` inherits it** (flagged to the synthesis) | `data/raw/letters/4Q23_…`, `4Q24_…`, `4Q25_…`; `data/processed/overnight/02_guidance_ledger.csv` (sbc_yoy_pct rows 90, 106, 125); `05_statements.csv` S106, S144 | 2024-02-13 to 2026-02-12 | 2026-09-17 | yes |
| 4 | Headcount: 6,907 (Dec 2023), ~7,300 (Dec 2024, +5.7%), ~8,200 (Dec 2025, +12.3%); 2Q26 call (Mertz, S163): "we don't need to grow our head count at levels that we did in the past because we're getting so much more output and speed from our existing workforce"; 2Q26 10-Q: product development +$62M in Q2 "resulting from an increase in average headcount"; ~13,000 third-party support workers (not on the SBC line) | `data/raw/filings/abnb_10k_FY2025.htm` (Human Capital); `05_statements.csv` K001–K003, S163; `abnb_2026q2_10q.html` | 2026-02-12 / 2026-08-06 | 2026-09-17 | yes |
| 5 | FY26 arithmetic under the letter's sentence: FY25 $1,592M × 1.131 = $1,801M cap; 1H26 $897M; 3Q26 on the M7 rule $452M → 4Q26 at the cap $452M; a $500M 4Q26 needs FY26 ≥ $1,849M (+16.1%), i.e. the sentence missed by ≥ 3 points (FY24's miss was 10.8 points against "~20%") | computed; `datasets/b09_results.csv` (route C) | 2026-09-17 | 2026-09-17 | yes |
| 6 | M7 SBC rule: SBC[q] = SBC[q−4] × (1 + g), g = recency-weighted mean of the last four y/y rates = 13.18% (1Q26 +14.5, 2Q26 +14.9, 4Q25 +11.7, 3Q25 +10.2) → 4Q26 $465M (the "team path"); backtest MAE h=0 $10.8M (W1) / $10.9M (W2), h=1 $19.2 / $21.9, h=2 $25.3 / $30.9 (0.45–0.55× the seasonal naive); LIVE 3Q26 SBC q10–q90 433–483; `yoy_last` spec preferred by the scoreboard; SBC by line TTM: product development 62.6%, G&A 17.0%, S&M 13.9%, ops 6.4%; FY27 SBC $2,053M | `docs/margin-build/notes/M7_below_ebitda.md`; `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv`; `40_lines_quarterly.csv` (sbc 4Q26 465.2) | 2026-09-14 / 2026-09-15 | 2026-09-17 | yes |
| 7 | Unrecognised compensation: the FY25 10-K discloses $114M for stock options (weighted-average 2.9 years) and no RSU figure (checked: every "unrecognized" sentence is options or tax); RSUs "vest over four years with a 25% one-year cliff, then quarterly" (third-party); so the grant cadence cannot be read from the filings beyond the Q2 step | `data/raw/filings/abnb_10k_FY2025.htm` Note 12; `sources/web_queries_2026-09-17.md` query 3 | 2026-02-12 | 2026-09-17 | no |
| 8 | **Revision-2 routes (A16-04, A16-15; re-run in `../../audits/A16-reproduce.py` block B09/3 and the response's recomputation):** Route A (Q4/Q2 ratio on $487M, 2023–25 mean 0.9622 at sd 0.035 = 4.5× the observed 0.0078) = **0.048**; Route B (y/y on the printed $411M, M7 13.2 ± 6) = **0.078**; Route C (the FY26-sentence overlay) **recalibrated to P(miss) 0.15 × N(+4, 3)** on the corrected guide record = **0.127** (rev 1: 0.20 at P(miss) 0.20 × N(+6, 3)) and **re-weighted 0.20 → 0.10** because it re-expresses route B's y/y information as an FY constraint and loads the whole FY residual onto Q4, so it is an overlay, not a third estimate. Blend **0.45 / 0.45 / 0.10 = 0.069**, plus **0.012** for the unmodelled discrete-grant tail = **0.081**. Companion from a weighted draw of the same blend: median **$466M**, P(≥ $480M) **0.27**, P(≤ $450M) **0.26**, p10–p90 **$432–495M**. **Superseded revision-1 values** (retained for the audit trail): A 0.05, B 0.08, C 0.20, blend 0.09, headline 0.10, companion median $468M / 0.30 / 0.25 | computed; `datasets/b09_results.csv` (rev-1 route grid) | 2026-09-17 | 2026-09-17 | yes |
| 8b | Revision-1 Monte Carlo (superseded, retained): Route A (Q4/Q2 ratio on $487M): all four years N(0.979, 0.034) → 0.10, 2023–25 mean 0.962 at sd 0.035 → 0.05, at sd 0.02 → 0.006; Route B (y/y on $411M): M7 13.2 ± 6 → 0.08, last-4 12.8 ± 5 → 0.04, last-8 17.1 ± 6.9 (includes the 2024 step regime) → 0.26, 1H26 14.7 ± 4 → 0.04; Route C (FY26 sentence with a 20% miss branch of +6 ± 3 pts) → 0.20 (miss 0.10 → 0.12, 0.35 → 0.32); blend 0.4A/0.4B/0.2C → 0.09 | computed; `datasets/b09_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 9 | No Kalshi or Polymarket market on SBC or any Airbnb cost line (2026-09-17T08:21:21Z); the Street does not publish an SBC consensus in the register (LSEG EPS actual = GAAP diluted EPS, so SBC is inside the EPS estimate) | `sources/kalshi_markets_KXABNB_open_20260917T082121Z.json`; `sources/polymarket_search_airbnb_20260917T082121Z.json`; M7 note ("What LSEG's EPS field measures") | 2026-09-17 | 2026-09-17 | no |
| 10 | Web pass (2 WebSearch calls attributable, one shared): confirms the 4Q25 letter sentence; Form 4 grants to the CFO and CAO (not fetched, zero weight); nothing else | `sources/web_queries_2026-09-17.md` queries 1, 3 | 2026-09-17 | 2026-09-17 | no |
| 11 | Impact inputs: SBC sits below adjusted EBITDA (no margin effect); M7 FY27 waterfall: SBC $2,053M, ETR 17.5%, diluted shares 573m; Street FY27 EPS $6.23 at $167.51 (16 Sep close) = 26.9× | `M7_below_ebitda_annual_forecasts.csv`; `23_vs_consensus.csv`; `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-14 / 2026-09-16 | 2026-09-17 | yes (impact only) |

Newest load-bearing source: the 2Q26 release (6 Aug 2026, 42 days against a 147-day window); the next information is the 3Q26 SBC line on 5 Nov.

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; finished logs R05, C11, R04, C12, R01, F03, F04
2. [repo, pandas] `data/processed/abnb_driver_history_quarterly.csv` (stock_based_comp_total_musd), `abnb_quarterly_costlines.csv`, `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (sbc_total_is, sbc by line), `02_panel_annual.csv`
3. [repo] `docs/margin-build/notes/M7_below_ebitda.md` (pre-registration, backtest table, LIVE waterfall); `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv`, `M7_below_ebitda_annual_forecasts.csv`; `40_lines_quarterly.csv` (sbc column)
4. [repo, python] letters 4Q23, 4Q24, 4Q25, 3Q25, 1Q26, 2Q26: "Stock-based compensation expense" reconciliation rows and "SBC" paragraphs (claims 1, 3); 4Q25 vs driver-history discrepancy resolved (convention 2)
5. [repo, python] FY2025 10-K: "unrecognized", "employees as of December 31", "Stock-based compensation expense was"; 2Q26 10-Q: Note 8, headcount sentences
6. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` (sbc_yoy_pct rows); `05_statements.csv` (S106, S144, S163, K001–K003, K010)
7. [Kalshi API] KXABNB open; [Polymarket public-search] airbnb (2026-09-17T08:21:21Z)
8. [WebSearch] Airbnb news (neutral recency pass, shared)
9. [WebSearch] Airbnb stock-based compensation 2026 headcount growth RSU grants
10. [python] `datasets/b09_model.py` → `b09_results.csv`, `b09_history.csv`
11. [WebSearch, final 72-hour neutral recency check = query 8, 2026-09-17: nothing on SBC or headcount] — no change

12. [rev 2, pandas] `02_guidance_ledger.csv` `sbc_yoy_pct` rows re-derived from both bases: printed releases give FY23 20.43 / FY24 25.63 / FY25 13.15; `abnb_driver_history_quarterly.csv` gives 18.28 / 30.82 / 9.87 — the ledger carries the driver-history numbers (A16-04)
13. [rev 2, python] `../../audits/A16-reproduce.py` (the audit's script, saved verbatim) run from the repo root with `py -3.13 -B`, clean, no path fix needed
14. [rev 2, python] §7 rewritten as a computed blend loop (every row 0.45A + 0.45B + 0.10C + 0.012 under the stated reversal) rather than typed route values; companion quantiles sampled from the blend

WebSearch calls used by this question: 2 of 5 (one shared); revision 2 added no web queries (repo-only findings).

## 3. Leading Hypothesis Entities
Airbnb, stock-based compensation, RSUs, 4Q26 shareholder letter, Ellie Mertz, headcount, M7 below-EBITDA bridge

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The 2025–26 regime holds: SBC grows +12–15% y/y, Q4 prints ~0.96 × Q2, 4Q26 ≈ $460–475M | leading (~0.85 of the mass) | claims 1–3: three consecutive years of Q4/Q2 at 0.954–0.969; FY26 guided "lower than 2025" (+13%); headcount growth slowing (claim 4) |
| A 2024-style step (new grant accounting, larger refresh cycle) lifts y/y to +22%+ | **rev 2: cut to ~0.05** | the 2024 step was the last of the double-trigger RSUs plus grant-accounting changes, now vested (claim 3); the Q2 2026 step (+19% q/q) was ordinary; and the correction in claim 3 removes the argument revision 1 leaned on — the FY24 guide was missed by **5.6** points, not 10.8, and the 3Q24 "~25%" guide was **met**, so a miss of the size this question needs (+21.7% against a 13.2% path, i.e. ≈8.5 points) has **never** happened in the printed record (A16-04) |
| A discrete Q4 grant event (executive performance awards, acquisition retention) adds $30M+ in one quarter | kept in the tail (~0.03) | no disclosed programme; Form 4 grants to the CFO/CAO are routine (claim 10); unrecognised RSU cost is not disclosed (claim 7) |
| The registry's 4Q25 base of $400M is right and the needed y/y is +25% | discarded as the base, threshold unaffected | claim 1 / convention (2): the releases print $411M; FY25 $1,592M reconciles only with $411M |
| Q4 seasonality flips (Q4 ≥ Q2) as in 2022 | inside Route A all-four (0.10) | 2022 was the post-IPO regime; 2023–25 are tight at 0.96 |
| A revenue or margin event changes SBC | discarded | SBC is grant-driven, not revenue-driven (M7: forecasting SBC as % of revenue fails, dollars pass) |
| Route C is a third independent estimate | **rev 2: discarded as a third estimate, kept as an overlay at 0.10 weight** (A16-15) | route C re-expresses route B's y/y information as an FY constraint and fixes 3Q26 at 399 × 1.132 with zero error, loading the entire FY residual onto Q4; it is therefore neither independent of B nor a correct decomposition of the FY uncertainty (a high-SBC regime raises Q3 and Q4 together, while the residual construction makes them offset — adding independent Q3 noise of $25M *raises* the route to 0.216, the wrong sign for the correlation that actually holds) |

## 5. Independent Estimates
- base_rate_estimate: 0.08 — Q4/Q2 seasonal route on 2Q26's $487M: the 2023–25 regime (0.9622, sd widened to 0.035 = 4.5× the observed 0.0078) gives **0.048**, the four-year ratio N(0.979, 0.034) **0.105**; a Q4/Q2 ≥ 1.027 has occurred in 1 of 4 years (2022, the post-IPO double-trigger regime, now spent)
- decomposition_estimate: 0.08 (rev 1: 0.11) — claim 8: route A **0.048**, route B **0.078**, route C **0.127** after the corrected guide record (A16-04), blended **0.45 / 0.45 / 0.10** (route C cut from 0.20 because it is an overlay on route B, not a third estimate — A16-15) = 0.069, plus **0.012** for the unmodelled discrete-grant tail = **0.081**
- anchor_estimate: **null — NO_EXTERNAL_ANCHOR** (rev 1 reported 0.16). A16-13 accepted: no market or consensus prices SBC (claim 9; LSEG's EPS field is GAAP, so SBC sits inside the EPS estimate and is not separately forecast), and the object revision 1 called the anchor — the repo's own M7 rule — is the same y/y rule route B uses, at the error scale of a residual pool that includes the 2024 step regime. It is a **labelled internal comparison**, not an anchor.
- internal_comparison: **0.16** — M7 `below-ebitda` LIVE rule, vintage 2026-09-11, 4Q26 point $465M and its h=2 residual pool (MAE $25–31M, Gaussian sd ≈ $35M) → P(≥ $500M) ≈ 0.16. Gap to the final: **−8 points** (rev 1: −6), and the gap is the error pool: M7's h=2 residuals are drawn from a window containing the double-trigger step, which this question's threshold specifically requires to repeat.
- final_estimate: **0.08** (credible interval **0.04–0.14**) (rev 1: 0.10, 0.05–0.20)
- NOT_INDEPENDENTLY_DERIVED flag: **true**. Raised and answered: route B and the internal comparison are the same y/y rule at different error scales; routes A and C are separate objects and land at 0.048 and 0.127, so the final sits below the comparison on evidence, not deference.
- The audit's independent comparison is **0.08**, the same number, built from the same corrected route C at a 0.10 weight and a +0.010 tail against this log's +0.012.

## 6. Final Numbers
**Binary.** P(4Q26 SBC ≥ $500M) = **0.08**, credible interval **0.04–0.14**. (Revision 1: 0.10, 0.05–0.20.)
Companion (sampled from the published blend, not from one route — A16-16): 4Q26 SBC median **$466M**, p10–p90 **$432–495M**; P(≥ $480M) **0.27**; P(≤ $450M) **0.26**. (Revision 1 published $468M / 0.30 / 0.25, which were the seasonal route's, not the blend's.) Implied FY26 SBC at the median ≈ $1,815M (+14.0%) if 3Q26 prints on the M7 rule — about one point above the letter's "lower than 2025", which on the **corrected** FY25 growth of +13.15% is the bar (the ledger's 9.87% would have made it a four-point overshoot).
The question needs **+21.65% y/y** on the printed $411M base, or a Q4/Q2 ratio of **1.027** in a regime that has printed 0.954 / 0.963 / 0.969 three years running. Neither has happened in the printed record.
Extreme-probability gate: not triggered (0.08 > 0.05).

## 7. Sensitivity
Every row is the **blend** 0.45A + 0.45B + 0.10C + 0.012 recomputed under the stated reversal (A16-05; revision 1 reported three route-level values as if they were final numbers — sd 0.02 was route A alone, 1H26 was route B alone, and the 0.22 "last-8" row was neither route nor blend).

| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4/Q2 ratio regime 2023–25 (0.9622, sd 0.035) | all four years incl. 2022 (0.979, 0.034): **0.105**; sd 0.02: **0.063** |
| Y/y growth regime 13.2 ± 6 (M7) | last-8 quarters incl. the 2024 step (17.1 ± 6.9): **0.161**; 1H26 rate 14.7 ± 4: **0.065** |
| P(FY26 sentence missed) 0.15 × N(+4, 3) | 0.25: **0.087**; 0.08: **0.077** |
| Route C weight 0.10 | 0.20 (revision-1 weight, corrected calibration): **0.088**; 0.15: **0.085** |
| Base = registry $400M (needed +25.0%) | no change to the threshold; the y/y routes fall and the blend goes to ~0.05 |
| Discrete Q4 grant event (unmodelled) | +$30M one-off certain: ~0.25 |

Honest width across §7: **0.06–0.16**, narrower than revision 1's published 0.05–0.25 and consistent with the 0.04–0.14 credible interval.

Pre-mortem ("it is 11 Feb 2027 and 4Q26 SBC printed $500M+"): (1) the 3Q26 print already showed the step (≥ $475M, +19% y/y) and the pre-print P should have been ~0.30 — the monitoring row below; (2) a 2026 refresh cycle at a lower share price (grants sized in dollars at ~$120–170 vs ~$130–150 a year earlier) raised unit counts and the Q4 expense — partly inside the y/y sd; (3) a Q4 executive award or acquisition retention grant (the +0.012 tail); (4) the FY26 "lower than 2025" sentence was simply missed (route C, now 0.10 weight at P(miss) 0.15). "It printed $465M": the modal outcome. Asymmetry: an over-stated bonus item on a below-EBITDA line would cost the memo credibility for little gain (EV under $1/share), so the log keeps the number at the seasonal evidence — and revision 2 moves it *down*, because the guidance-miss record revision 1 leaned on dissolves under this log's own SBC correction.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo due | Quote 0.08 (0.04–0.14); **immaterial, drop from the memo body**. What the memo should carry from this log is the **$411M / $368M correction**, not the probability |
| 2026-11-05 (after close) | 3Q26 release: SBC line (M7 rule $452M; q10–q90 433–483) | ≥ $475M → 0.26; $455–475M → 0.12; ≤ $455M → 0.05 |
| 2026-11-06 | 3Q26 10-Q Note 8 (SBC by line; any new award programme) | a disclosed executive/performance award programme → +0.10 |
| 2026-11-06 to 2027-02-10 | Form 4 filings (large one-off grants); any conference remark on headcount | a stated headcount re-acceleration → +0.03 |
| ~2027-02-11 | 4Q26 release reconciliation table | resolve; audit read: a 3Q26 line ≥ $475M implies the pre-print P should have been ~0.26 |
| any date | **Repo hygiene** — `abnb_driver_history_quarterly.csv` (4Q23 270, 4Q24 400, 4Q25 400) and the `sbc_yoy_pct` actuals in `02_guidance_ledger.csv` derived from it | not this log's to fix (CLAUDE.md rule 1), but flagged to the synthesis: any other question using `sbc_yoy_pct` as a base rate inherits FY23 18.28 / FY24 30.82 instead of 20.43 / 25.63 |

## 9. Impact
If the event happens (4Q26 SBC ≥ $500M, taken at $500M against the team path's $465M, +$35M; FY27 run-rate +$140M against M7's $2,053M):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a compensation line |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 | — |
| FY27 revenue ($M) | 0 | — |
| FY26 adj. EBITDA margin (pp) | 0 | SBC is excluded from adjusted EBITDA |
| FY27 adj. EBITDA margin (pp) | 0 | — |
| FY27 EPS ($) | −0.20 | GAAP EPS (= the Street's basis, M7): +$140M × (1 − 0.175) / **573m** shares (run convention for FY27 rows) = −$0.202; 4Q26 EPS −$0.05. The audit replays this row exactly |
| Stock ($/share) | −3 | a full P/E mark on −$0.20 at 26.9× is −$5.4; SBC-driven EPS misses are discounted by EBITDA/FCF-based holders, so half-weight ≈ −$3 |
| **EV = P × stock** | **0.08 × −$3 ≈ −$0.24/share** | **Immaterial** (< $1/share, and further below it than at revision 1's −$0.30): drop from the memo; keep the arithmetic as a footnote on GAAP EPS quality |

## 10. Revision notes
| Finding | Ruling | Change made |
|---|---|---|
| A16-04 (major) | **accepted** | Claim 3's guide record re-derived from the printed releases: FY23 +20.43 (met), FY24 +25.63 (the 1Q24 "~20%" guide missed by **5.6**, not 10.8; the 3Q24 "~25%" guide **met**, not missed by 5.8), FY25 +13.15. Route C recalibrated to P(miss) **0.15** × N(**+4**, 3): 0.197 → **0.127**. The ledger defect is stated in claim 3 and in the monitoring calendar and flagged to the synthesis |
| A16-05 (major) | **accepted** | §7 rewritten as a computed blend loop; the three rows that did not replay (0.05, 0.22, 0.06) are replaced by 0.063, 0.161, 0.065 at the revision-2 weights. Honest §7 width 0.06–0.16 |
| A16-15 (minor) | **accepted** | Route C's weight 0.20 → **0.10** and it is described in §4 and claim 8 as a guidance-miss overlay on route B, not a third estimate |
| A16-16 (minor) | **accepted** | Companion quantiles sampled from the published blend: median **$466M**, P(≥480) **0.27**, P(≤450) **0.26** (rev 1 published the seasonal route's $468M / 0.30 / 0.25) |
| A16-13 (major) | **accepted** | `anchor: null`, `NO_EXTERNAL_ANCHOR`; M7 relabelled `internal_comparison` 0.16; `final_minus_anchor` no longer reported |
| **not in the audit** | — | The corrected record removes the *only* historical precedent for a miss of the size this question needs. The question requires ≈8.5 points of overshoot against the M7 path; the largest printed miss of an SBC sentence is 5.6 points (FY24 against the 1Q24 "~20%" guide), and the 2024 regime that produced it — the last of the double-trigger RSUs — is spent. §4 row 2 is cut from ~0.08 to ~0.05 on this |
| **not in the audit** | — | The letter's FY26 bar is "lower than 2025" and 2025 on the corrected basis is **+13.15%**, not the ledger's 9.87%. 1H26 at +14.7% is therefore a **1.5-point** overshoot of the sentence, not a 4.8-point one — a smaller tell than the ledger implies, and the reason route C's miss branch is 0.15 rather than 0.20 |

RESUME: the revision-2 number is **0.08 (0.04–0.14)** and the item is immaterial at every value in the interval — it should be dropped from the memo body. The thing worth carrying forward is not the forecast but the data correction: `abnb_driver_history_quarterly.csv` prints 4Q23 $270M, 4Q24 $400M and 4Q25 $400M where the releases print **$290M, $368M and $411M**, and `02_guidance_ledger.csv`'s `sbc_yoy_pct` actuals (FY23 18.28, FY24 30.82) are computed from the erroneous series. Neither file may be edited from this run (CLAUDE.md rule 1); the next agent should (a) hand the correction to whoever owns the driver history, with the FY25 $1,592M reconciliation as the proof, and (b) check every other question in this run that used `sbc_yoy_pct` as a base rate — B08 claim 8 cites the same metric for its February-letter record. The forecast itself needs no more work: the only live input is the 3Q26 SBC line on 5 November, and the monitoring table gives the three cut points.
