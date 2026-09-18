# RESEARCH LOG

## 0. Metadata
- question_name: sellside-mean-target-cut-by-15dec
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § S04)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-12-15
- resolution_date: 2026-12-15
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A07 (price paths from the S02 revision-2 model, `../close-15dec-2026/datasets/abnb_path_mixture_v2.py`; tape base rates in `datasets/target_base_rates_v2.py`; wrapper `datasets/run_v2.py`; revision-1 files untouched)

## 0b. Question (verbatim)
### Title
Will the mean sell-side 12-month price target for ABNB on 15 Dec 2026 be at least $5 below its 12 Sep 2026 level ($181.8, 32 targets)?
### Resolution Criteria
Yes if the mean of live targets in the same feed convention (`data/processed/reverse_dcf/D/`, 365-day window; fallback yfinance `targetMeanPrice`) on 15 Dec 2026 ≤ $176.8. Resolution date 15 Dec 2026.
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted: (1) the resolving object is the mean of `currentPriceTarget` over the latest action per firm within 365 days of 15 Dec 2026 with a positive target, from `Ticker('ABNB').upgrades_downgrades` pulled on or after 15 Dec (the D convention; recomputed here for 16 Sep at $181.81, 32 firms, identical to the 12 Sep tape); (2) the threshold is fixed at $176.80 regardless of what the base does between now and then — in particular the Morgan Stanley re-initiation at $170 on 16 Sep (from $125) lifts the base to $183.22 once the feed carries it, so the cut required is 3.50% (log −3.566%), not 2.75%; (3) the yfinance `targetMeanPrice` fallback ($182.98, 40 analysts on 16 Sep) is a different universe and is used only if the feed is unavailable; (4) firms whose only action falls out of the 365-day window without a refresh drop from the mean — none of the 32 live targets is dated before 13 Feb 2026, so no drop-outs occur before 15 Dec; (5) **the comparison is inclusive as the registry writes it: a mean of exactly $176.80 resolves Yes** (revision 1's "ties resolve No" reversed the rule and is withdrawn, A07-01; the simulation always used `<=`).

## 1. Claims Ledger
Claims 1–19 and 34–35 of `../close-15dec-2026/research-log.md` (revision 2: price path model and its inputs, adopted print-state weights, Astra comparison) are reused; claim 16 there records the tape and the Morgan Stanley action. S04-specific claims:
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 26 | Live tape recomputed on the 16 Sep feed pull (469 rows, none added since 12 Sep): 32 firms, mean $181.8125, median $182.5; low Morgan Stanley $125 (30 Jul, Underweight), Barclays $150, Deutsche $154 (13 Feb, stale), Goldman $155 (feed label; Neutral $165 per D's correction), Cantor/TD Cowen $160, Truist $161 (10 Sep); high Rosenblatt/DA Davidson $220, Bernstein $217, B. Riley $210, six at $200. With Morgan Stanley at $170 (16 Sep, Equal-weight) the mean is $183.21875. yfinance `targetMeanPrice` $182.975 (40), median $185, high $220, low $125 | `sources/yfinance_upgrades_downgrades_20260917T031221Z.csv`, `yfinance_analyst_price_targets_20260917T031221Z.json`, `yfinance_info_subset_20260917T031221Z.json`; `datasets/target_base_rates_v2.json`; `sources/web_analyst_actions_capture_20260917.md` | 2026-09-16 | 2026-09-17 | yes |
| 27 | Tape-lag regression (D §5): 21-session log change in the mean target on the contemporaneous and two lagged 21-session log price changes: 0.075 / 0.13 / 0.10 (sum 0.30, R² 0.23, Newey-West t 2.1 / 5.5 / 4.1; reproduced by the auditor as 0.0740 / 0.1281 / 0.0953, n 1,366; 2023+ 0.14 / 0.19 / 0.10, sum 0.44); 21-block offsets range 0.26–0.36; "a 10% price move pulls the mean target 3–4% over three months, with the largest part in the second month". Sign-split: falls 0.34, rises 0.24 (inside noise). After a 21-session fall of 15%+ with no print, −5.6% over the next 42 sessions (16 episodes); after a 15%+ rise +5.9% | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5; `data/processed/reverse_dcf/D/D_chase_regression.csv`, `D_chase_asymmetry.csv`; `audits/A07-reproduce.py` §4 | 2026-09-12 | 2026-09-17 | yes |
| 28 | Print revisions (23 prints), **corrected class membership (A07-07)**: day-1 move ≤ −5% (n 6: 3Q22, 1Q23, 1Q24, 2Q24, 3Q24, 2Q25) → mean target −3.8% at +20 sessions, −3.9% at +40, chase 0.38; target changes at +20: **−7.6, −6.4, +1.7, −14.1, +3.5, −0.02%** — any net cut 4 of 6 (2Q25 at −0.02% is effectively unchanged, not a material cut), cut ≥ 3.8% (or ≥ the 3.5% gate) **3 of 6**; the exceptions 1Q24 (+1.7), 3Q24 (+3.5 after an 8.8% run-up) and 2Q25 (0.0 with a 9–11% pre-print discount). 2Q22 (day-1 −1.13%, targets −10.1%, 14 cuts) is a small-print window, not a member of this class (revision 1 listed it). Day-1 ≥ +5% (n 6) → +6.3%, chase 0.47, 1 of 6 with a cut; small prints (n 11) −0.3%, 5 of 11 with a cut, 1 of 11 ≥ 3.8%. 2Q26: +12.3% at +20 (24 raises, 0 cuts). Print-day cuts are rare; a down print after a run-up or a wide discount produces no net cut within 20 sessions | `data/processed/reverse_dcf/D/D_print_revisions.csv`, `D_print_revisions_summary.csv`; D §5; `datasets/target_base_rates_v2.json` "down_print_class" | 2026-09-12 / 2026-09-17 | 2026-09-17 | yes |
| 29 | Base rates from the daily panel (feed convention, n_targets ≥ 10), **exact thresholds (A07-16)**: 63-session log change in the mean target ≤ −3.566% (the MS-adjusted gate): **0.253 (all, 346/1,366 overlapping days, effective n ≈ 22), 0.174 (2023+, 150/863), 0.170 (2024+, 104/613)**; at the unadjusted-feed gate −2.80%: 0.294 / 0.218 / 0.181; revision 1's −0.035 cutoff gave 0.257 / 0.177 / 0.175. Print-centred windows on the revision-2 shape (−36 to +26 sessions around each reaction day, the 16 Sep → 15 Dec shape): **6 of 21 ≤ −3.50% simple (0.29); W1 3 of 13 (0.23); W2 2 of 9 (0.22)**; revision 1's −36/+27 windows 6 of 22 (0.27), 2023+ 3 of 13. Two-regressor regression across the −36/+27 windows (Δtarget% on Δprice% and day-1%): −0.08 + 0.097 × Δprice + 0.405 × day-1, R² 0.31, residual sd 6.68 (auditor's refit; W1 5.92, W2 6.86). Unconditional 63-session Δln T sd 7.2% (all), 5.8% (2023+). Same-calendar windows (mid-Sep → mid-Dec): 2021 +4.0, 2022 −11.9, 2023 −3.0, 2024 +5.0, 2025 +1.9 | `datasets/target_base_rates_v2.py` → `target_base_rates_v2.json`, `target_change_print_windows_v2.csv` (from `data/processed/reverse_dcf/D/D_target_panel_daily.csv`, `data/processed/abnb_earnings_reactions.csv`); `audits/A07-reproduce.py` §4 | 2026-09-17 | 2026-09-17 | yes |
| 30 | Known price lags for the regression (log): 17 Aug → 16 Sep −6.8% (p0); 17 Jul → 17 Aug +20.6% (p−1, contains the 2Q26 print); 17 Jun → 17 Jul +3.3%. Their contribution to the three blocks ending 15 Dec: (b1 + b2) × p0 + b2 × p−1 = −1.6% + 2.1% = +0.5%, plus 3 × the constant 0.05% | `datasets/target_base_rates.json` (revision 1, unchanged); `../close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv` | 2026-09-16 | 2026-09-17 | yes |
| 31 | D note JUDGEMENT (12 Sep): "the base case is a cut of roughly 3–4% in the mean target ($5–7, from $181.8 to about $175–177) over the next two to three months, most of it in October, unless the price recovers first"; what would change it: "a recovery to $180+ before mid-October" or "a run of cuts of more than 5% by mid-October". It gives no probability and rests on the same tape-lag history as this log — **a non-independent repo prior, not an external anchor (A07-09)**. Since then: no cuts; Morgan Stanley +$45 (16 Sep); the three raises of 8–10 Sep were already in the tape | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5 last paragraph | 2026-09-12 | 2026-09-17 | yes |
| 32 | Feed coverage: the yfinance/Benzinga feed drops whole firms (Gordon Haskett) and about a third of intermediate actions (96 chain breaks in 440 target actions); raise/cut counts are lower bounds; vendor means differ by ~$3 across universes (S&P $178.96 3 Sep, MarketBeat $179.97 11 Sep, yfinance $182.13 12 Sep, D file $181.81) | D §8 caveat 2; `data/processed/reverse_dcf/D/D_feed_chain_breaks.csv` | 2026-09-12 | 2026-09-17 | no |
| 33 | Monte Carlo S04 block, revision 2 (`abnb_path_mixture_v2.py`): Δln T = known lags (+0.65%) + 0.305 × p1 (16 Sep → 14 Oct, 21 sessions) + 0.205 × p2pre (14 Oct → 5 Nov, 15 sessions) + 0.40 × day-1 + 0.14 × post (6 Nov → 15 Dec, 26 sessions) + 0.5% stale-target refresh + N(0, **5.0%**); base $183.22. Outputs: mean Δln T +0.2%, sd 7.2%; T on 15 Dec p5/10/25/50/75/90/95 = $163 / 167 / 175 / 184 / 193 / 201 / 206; **P(T ≤ 176.8) 0.299** (0.337 on the feed-as-is base $181.81); P(T ≥ 190) 0.32 (feeds R12; revision 1 said 0.25); by 5 Nov branch: accel 0.19, flat 0.27, decel-guide-ok 0.30, decel-guide-below 0.38; conditional on the realised day-1 move: ≤ −8% **0.57**, ≤ −5% 0.51, inside (−5, +5) 0.23, ≥ +5% 0.08. Revision 1 (superseded): 0.295 with residual sd 3.5% | `datasets/mixture_base_run_v2.json`, `sensitivity_v2.csv` | 2026-09-17 | 2026-09-17 | yes |
| 36 | **Residual of the exact hybrid equation (A07-08)**: the model's Δln T equation (two known lags, p1, p2pre, day-1 × 0.40, post × 0.14, constants) evaluated on every historical print window with 78 sessions of history and 26 after (n 21): residual mean −0.7%, **sd 5.2% (rmse 5.1)**; W1 (n 13) mean +0.6, sd 4.3; W2 (n 9) mean +1.3, sd 4.7. A regression of the realised Δln T on the equation's prediction gives slope 1.25 (R² 0.55, residual sd 5.2): the equation under-predicts the size of target moves by about a quarter, in-sample. Revision 1's 3.5% was a judgment from the 21-session sd; revision 2 carries 5.0% (between the W1/W2 and all-sample values); the auditor's 6.68% is the residual of a two-regressor equation without the lag structure and is the sensitivity's upper case | `datasets/target_base_rates_v2.py` → `target_base_rates_v2.json` "print_windows_36_26", "hybrid_calibration"; `target_change_print_windows_v2.csv` | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
Queries 1–23 of `../close-15dec-2026/research-log.md` § 2 were run once for the batch. S04-specific: query 7 (the D panel files), query 8 (the fresh `upgrades_downgrades`, `analyst_price_targets`, `info`, `recommendations` pulls), query 14 ([WebSearch] Airbnb analyst price target cut September 2026 — surfaced the Morgan Stanley 16 Sep initiation, no cuts), queries 15–16 (WebFetch of the 247wallst and Cerbat Gem pages, verbatim in `sources/web_analyst_actions_capture_20260917.md`), the revision-1 base-rate computation (`datasets/target_base_rates.py`), query 17 (final 72-hour recency check: no target changes beyond Morgan Stanley; no change to the number), and in revision 2 the exact-threshold rates, the −36/+26 windows, the hybrid-equation residual and the corrected down-print class (`datasets/target_base_rates_v2.py`, query 23) plus the R12 read (query 21: R12 used this log's revision-1 P(T ≥ 190) 0.25 as its repo prior; revision 2 gives 0.32).

## 3. Leading Hypothesis Entities
Airbnb, ABNB, Morgan Stanley, Truist, Raymond James, Baird, Bernstein, Rosenblatt, DA Davidson, yfinance/Benzinga feed, 5 Nov 2026 print

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| D's JUDGEMENT "base case cut of 3–4% over two to three months" taken at face value (P ≈ 0.5) | discarded as the point; recorded as a non-independent repo prior, not an anchor | it applied the lag-1 term of the 8–10 Sep fall but not the lag-2 term of the August +20.6% print rally, which is larger (+2.1% vs −1.6%, claim 30); since 12 Sep the tape has moved the other way (Morgan Stanley +$45, no cuts); it supplies no probability and shares this log's evidence (A07-09) |
| The mean target cannot fall $6.4 without a down print | discarded | 5 of 11 small-print windows still had a net cut (claim 28) and the 2023Q3 window fell 3.0% on a −2.9% price move; the hybrid residual (5.0% per window) alone gives ~24% |
| Stale targets (Deutsche $154, TD Cowen $160, Mizuho $175, Tigress $185, CICC $165, set at prices $116–150) refresh upward after the print | kept as +0.5% drift, labelled judgment | four of the five sit below the current price and every post-print refresh in 2Q26 was a raise; a full refresh of the two lowest to $175 alone is +$1.1 on the mean; the "none" row (0.32) is inside the interval |
| Targets fall out of the 365-day window | discarded | no live target is dated before 13 Feb 2026 |
| Goldman relabelled to $165 (D's correction) | not applied | the feed convention is the resolving object and it carries $155; applying the correction would move the base by +$0.31 either way |
| A print-day cut wave like 2Q24 (−14.1% at +20, 19 cuts) | kept inside the decel-guide-below branch | that branch's median T is $180.5 with P(≤ 176.8) 0.38; a 2Q24-size day (−13%) produces a −5% chase in the model, which resolves Yes |
| Residual sd 3.5% (revision 1) | discarded (A07-08) | not established by any fitted object; the exact hybrid equation's historical residual is 4.3–5.2% (claim 36); 5.0% carried |
| Astra's independent construction (two-regressor window equation, propagated price/event uncertainty: mean −1.3%, sd 8.3%, model P 0.39; blended 2:1 with a 0.20 outside view → 0.33) | recorded; not adopted as the point | its equation omits the lag structure (the measured +2.1% August lag-2 term) and the stale-refresh term, and its 8.3% sd stacks the 6.68% residual on top of the price uncertainty the residual was estimated with; this log's decomposition with the 6.68% residual gives 0.33 and with no known-lag terms 0.33 — the two constructions differ by exactly those two named terms |

## 5. Independent Estimates
- base_rate_estimate: 0.22 — 63-session change in the mean target ≤ the exact gate: 0.17 (2023+, 2024+) to 0.25 (all); print-centred −36/+26 windows 0.22 (W2) / 0.23 (W1) / 0.29 (all) (claim 29); the figures average 0.23, rounded to 0.22 because the 2023+ regime (Buy share at a series high, targets chasing up) is the relevant one; all overlapping, effective n small
- decomposition_estimate: 0.30 — S02 revision-2 price paths pushed through the tape-lag regression with the print chase and the hybrid-equation residual (claim 33): 0.299 on the $183.22 base; the branch split (0.19 / 0.27 / 0.30 / 0.38) says the question is mostly "does 5 Nov decelerate and does the tape chase it down 3.5% within 26 sessions"; the realised-day-1 conditionals (≤ −8%: 0.57; ≥ +5%: 0.08) are the November update rule
- anchor_estimate: **no independent anchor exists.** No tradable market (Kalshi and Polymarket carry no ABNB target or price-level market for December, S02 claim 17); the yfinance `targetMeanPrice` $182.98 (2026-09-17T03:12Z) is a level, not P(target ≤ 176.8). The D note's published JUDGEMENT (claim 31, 12 Sep, "base case" cut of 3–4%) is a **non-independent repo prior** built on the same tape-lag history; it is recorded as 0.50 for the ledger's anchor field but is not a market consensus and the gap to it is not a disagreement with a crowd
- anchor_value: 0.50 (repo prior, 2026-09-12, non-independent; labelled as such per A07-09)
- final_estimate: **0.30** (credible interval 0.20–0.42)
- final_minus_anchor: −0.20 against the repo prior. The reasons the prior overstates it: (i) it omitted the +2.1% lag-2 contribution of the August rally, which offsets the −1.6% from the September fall; (ii) the base moved up $1.4 on 16 Sep (Morgan Stanley), raising the required cut from 2.75% to 3.50%; (iii) the tape has produced no cut since 7 Aug and three raises into the fall, the same-day catch-up pattern D itself documents; (iv) the two base-rate families sit at 0.17–0.29. The final leans on the decomposition (0.30) with the base rate (0.22) as the floor; Astra's independent 0.33 (0.20–0.45) differs by 0.03, inside the interval, and the difference is the two named terms in section 4

## 6. Final Numbers
P(mean live target on 15 Dec ≤ $176.80) = **0.30**, credible interval **0.20–0.42**.
Distribution of the 15 Dec mean target (model, $183.22 base): p5 $163, p10 $167, p25 $175, p50 $184, p75 $193, p90 $201, p95 $206; P(≥ $190) 0.32 (feeds R12; revision 1 said 0.25).
If the feed never carries the Morgan Stanley action (base stays $181.81): 0.34.
Conditional on the team's base 5 Nov branch (decel, guide below Street): 0.38; on an accelerating print: 0.19. Conditional on the realised day-1 move: ≤ −8% 0.57, ≤ −5% 0.51, inside ±5% 0.23, ≥ +5% 0.08.

## 7. Sensitivity
All rows from `datasets/sensitivity_v2.csv`.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Residual sd 5.0% (hybrid-equation residual 4.3–5.2) | 3.5% (revision 1): 0.27; 6.68% (Astra's two-regressor residual): 0.33 |
| Print chase 0.40 (D's +20-session ratio, both signs) | 0.60: 0.34; 0.20: 0.25 |
| Base $183.22 (Morgan Stanley $170 in the feed) | feed as-is $181.81: 0.34 |
| Known lag terms +0.65% (August rally, September fall) | zero: 0.33 |
| Stale-target refresh +0.5% | none: 0.32 |
| Print-state weights 0.32 / 0.10 / 0.13 / 0.45 | revision-1 weights (accel 0.24): 0.31; P(accel) 0.40: 0.28; 0.22: 0.32 |
| Day-1 conditional means shrunk | market-neutral print: 0.26; unshrunk: 0.31 |
| Post-print drifts | none: 0.29; revision-1 drifts: 0.31 |
| Total drift 6.97% | 3%: 0.31; 0: 0.32 |
| Regression betas 0.075 / 0.13 / 0.10 (full sample) | 2023+ betas 0.14 / 0.19 / 0.10 (sum 0.44): 0.32 |
| Background vol 30% | 33%: 0.31; 26%: 0.29 |

## 8. Monitoring Calendar
Update procedure: recompute the live tape (`datasets/target_base_rates_v2.py`) weekly; the answer is mechanical once the mean is within $2 of the threshold in December.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-19 | feed refresh | confirm Morgan Stanley $170 appears (base $183.22); if the feed carries it as a rating-only row with no target, base stays $181.81 → 0.34 |
| 2026-10-02 | prelim memo due | quote 0.30 (0.20–0.42); the memo should not say "the tape will cut into the print" |
| 2026-10-14 | end of block 1 | re-run with the realised p1: price ≤ $155 (p1 ≈ −8%) → ≈ 0.40; ≥ $180 → ≈ 0.20 |
| 2026-10-15 to 11-04 | Q3 preview season | each net cut of ≥ $10 by a live firm moves the mean −$0.3; three previews cutting to ≤ $165 would move P to ≈ 0.40 |
| 2026-11-05/06 | print and reaction | day-1 ≤ −8%: **≈ 0.57 (0.50–0.60)** — 3 of 6 down-5% prints cut ≥ 3.8% at +20 (3Q22, 1Q23, 2Q24), 4 of 6 any net cut; the 1Q24/3Q24/2Q25 exceptions had run-ups or discounts, absent here; day-1 in (−5, +5): ≈ 0.23; day-1 ≥ +5%: ≈ 0.08 |
| 2026-11-25 | +13 sessions | most print-driven revisions are in (79% within 5 sessions in 2Q26); if the mean is ≤ $179 move to ≥ 0.6, if ≥ $185 move to ≤ 0.1 |
| 2026-12-15 | resolution | recompute the D-convention mean from the feed pulled after the close; **≤ $176.80 inclusive resolves Yes**; fallback yfinance `targetMeanPrice` only if the feed is unavailable |

## 9. Model parameters
The S04 block has three judgment settings (print chase 0.40, stale refresh 0.5%, residual sd 5.0%) on top of the S02 path model (S02 log § 9); the three betas, the known-lag terms, the two bases and the gate are measured.

## 10. Revision notes
| # | Change (revision 1 → 2) | Finding |
|---|---|---|
| 1 | Convention (5): exactly $176.80 resolves Yes (inclusive, as the registry writes it); "ties resolve No" withdrawn | A07-01 |
| 2 | Down-print class corrected: 3Q22, 1Q23, 1Q24, 2Q24, 3Q24, 2Q25 (2Q22 removed, 1Q24 added); any net cut 4 of 6, cut ≥ 3.8% 3 of 6; monitoring rationale and the 6 Nov update rule rewritten (0.55–0.65 → ≈ 0.57, from the model's own conditional) | A07-07 |
| 3 | Residual sd 3.5% replaced by 5.0% from the exact hybrid equation's historical residual (sd 5.2 all, 4.3 W1, 4.7 W2; claim 36 new); the 3.5% and 6.68% cases shown as the sensitivity's bounds | A07-08 |
| 4 | The D note's "base case" relabelled a non-independent repo prior; "no independent anchor exists" stated; the 0.20 gap is no longer presented as disagreement with a consensus | A07-09 |
| 5 | Base rates at the exact log gate −3.566% (0.253 / 0.174 / 0.170) and the feed-as-is gate; print windows on the −36/+26 shape (6/21, 3/13, 2/9); overlapping-observation caveat | A07-15, A07-16 |
| 6 | Price paths from the S02 revision-2 model (adopted print-state weights, sessions 36/26, drift convention, rebased post-print drifts); tape blocks 21 + 15 + 26 sessions | A07-05/06/15/17, post-S01 inputs |
| 7 | Headline: P(Yes) 0.29 (0.20–0.40) → **0.30 (0.20–0.42)**; model 0.295 → 0.299 (the wider residual +0.03 offsets the accel-heavier weights −0.015 and the lighter drift −0.01); P(T ≥ 190) 0.25 → 0.32 (R12's repo prior should be refreshed) | — |
| 8 | Astra's independent 0.33 recorded in section 4 with the two named terms that separate it from 0.30 | A07 independent comparison |
