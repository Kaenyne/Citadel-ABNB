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
- revision: 1
- agent: fable
- batch: A07 (price paths from the S02 model, `../close-15dec-2026/datasets/abnb_path_mixture.py`; tape base rates in `datasets/target_base_rates.py`)

## 0b. Question (verbatim)
### Title
Will the mean sell-side 12-month price target for ABNB on 15 Dec 2026 be at least $5 below its 12 Sep 2026 level ($181.8, 32 targets)?
### Resolution Criteria
Yes if the mean of live targets in the same feed convention (`data/processed/reverse_dcf/D/`, 365-day window; fallback yfinance `targetMeanPrice`) on 15 Dec 2026 ≤ $176.8. Resolution date 15 Dec 2026.
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted: (1) the resolving object is the mean of `currentPriceTarget` over the latest action per firm within 365 days of 15 Dec 2026 with a positive target, from `Ticker('ABNB').upgrades_downgrades` pulled on or after 15 Dec (the D convention; recomputed here for 16 Sep at $181.81, 32 firms, identical to the 12 Sep tape); (2) the threshold is fixed at $176.80 regardless of what the base does between now and then — in particular the Morgan Stanley re-initiation at $170 on 16 Sep (from $125) lifts the base to $183.22 once the feed carries it, so the cut required is 3.5%, not 2.75%; (3) the yfinance `targetMeanPrice` fallback ($182.98, 40 analysts on 16 Sep) is a different universe and is used only if the feed is unavailable; (4) firms whose only action falls out of the 365-day window without a refresh drop from the mean — none of the 32 live targets is dated before 13 Feb 2026, so no drop-outs occur before 15 Dec; (5) ties resolve No (≤ $176.80 exactly is measure-zero on a 32-firm mean).

## 1. Claims Ledger
Claims 1–19 of `../close-15dec-2026/research-log.md` (price path model and its inputs) are reused; claim 16 there records the tape and the Morgan Stanley action. S04-specific claims:
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 26 | Live tape recomputed on the 16 Sep feed pull (469 rows, none added since 12 Sep): 32 firms, mean $181.81, median $182.5; low Morgan Stanley $125 (30 Jul, Underweight), Barclays $150, Deutsche $154 (13 Feb, stale), Goldman $155 (feed label; Neutral $165 per D's correction), Cantor/TD Cowen $160, Truist $161 (10 Sep); high Rosenblatt/DA Davidson $220, Bernstein $217, B. Riley $210, six at $200. With Morgan Stanley at $170 (16 Sep, Equal-weight) the mean is $183.22. yfinance `targetMeanPrice` $182.98 (40), median $185, high $220, low $125 | `sources/yfinance_upgrades_downgrades_20260917T031221Z.csv`, `yfinance_analyst_price_targets_20260917T031221Z.json`, `yfinance_info_subset_20260917T031221Z.json`; `datasets/target_base_rates.json`; `sources/web_analyst_actions_capture_20260917.md` | 2026-09-16 | 2026-09-17 | yes |
| 27 | Tape-lag regression (D §5): 21-session log change in the mean target on the contemporaneous and two lagged 21-session log price changes: 0.075 / 0.13 / 0.10 (sum 0.30, R² 0.23, Newey-West t 2.1 / 5.5 / 4.1; 2023+ 0.14 / 0.19 / 0.10, sum 0.44); 21-block offsets range 0.26–0.36; "a 10% price move pulls the mean target 3–4% over three months, with the largest part in the second month". Sign-split: falls 0.34, rises 0.24 (inside noise). After a 21-session fall of 15%+ with no print, −5.6% over the next 42 sessions (16 episodes); after a 15%+ rise +5.9% | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5; `data/processed/reverse_dcf/D/D_chase_regression.csv`, `D_chase_asymmetry.csv` | 2026-09-12 | 2026-09-17 | yes |
| 28 | Print revisions (23 prints): day-1 move ≤ −5% (n 6) → mean target −3.8% at +20 sessions, −4.0% at +40, chase 0.38, 4 of 6 with a net cut (3Q22 −7.6, 1Q23 −6.5, 2Q24 −14.1, 2Q22 −10.1; exceptions 3Q24 +3.5 after an 8.8% run-up, 2Q25 0.0 with a 9–11% pre-print discount); day-1 ≥ +5% (n 6) → +6.3%, chase 0.47, 1 of 6 with a cut; small prints (n 11) −0.2%, 5 of 11 with a cut. 2Q26: +12.3% at +20 (24 raises, 0 cuts). Print-day cuts are rare; a down print after a run-up or a wide discount produces no net cut within 20 sessions | `data/processed/reverse_dcf/D/D_print_revisions.csv`, `D_print_revisions_summary.csv`; D §5 | 2026-09-12 | 2026-09-17 | yes |
| 29 | Base rates from the daily panel (feed convention, n_targets ≥ 10): 63-session log change in the mean target ≤ −3.5%: 0.26 (all, n 1,366 overlapping days), 0.18 (2023+, n 863), 0.17 (2024+); P(< 0) 0.40 / 0.31 / 0.24; 2023+ mean +1.5%, sd 5.8, p10 −6.4, p25 −1.1. Print-centred windows (−36 to +27 sessions around each reaction day, the 16 Sep → 15 Dec shape): 6 of 22 ≤ −3.5% (0.27; 2021Q1 −1.8, 2022Q1 −4.1, 2022Q2 −17.4, 2022Q3 −11.9, 2023Q1 −6.6, 2023Q3 −3.0, 2024Q2 −13.9, 2025Q1 −6.1 are the negative ones), 2023+ 3 of 13 (0.23). Regression across the 22 windows: Δtarget% = −0.09 + 0.097 × Δprice% + 0.405 × day-1% (R² 0.31, residual sd 6.7); corr with the day-1 move 0.52, with the window price move 0.37. 21-session Δlog target sd 3.8% (2023+ 3.4%). Same-calendar windows (mid-Sep → mid-Dec): 2021 +4.0, 2022 −11.9, 2023 −3.0, 2024 +5.0, 2025 +1.9 | `datasets/target_base_rates.py` → `target_base_rates.json`, `target_change_print_windows.csv` (from `data/processed/reverse_dcf/D/D_target_panel_daily.csv`, `data/processed/abnb_earnings_reactions.csv`) | 2026-09-17 | 2026-09-17 | yes |
| 30 | Known price lags for the regression (log): 17 Aug → 16 Sep −6.8% (p0); 17 Jul → 17 Aug +20.6% (p−1, contains the 2Q26 print); 17 Jun → 17 Jul +3.3%. Their contribution to the three blocks ending 15 Dec: (b1 + b2) × p0 + b2 × p−1 = −1.6% + 2.1% = +0.5%, plus 3 × the constant 0.05% | `datasets/target_base_rates.json`; `../close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv` | 2026-09-16 | 2026-09-17 | yes |
| 31 | D note JUDGEMENT (12 Sep): "the base case is a cut of roughly 3–4% in the mean target ($5–7, from $181.8 to about $175–177) over the next two to three months, most of it in October, unless the price recovers first"; what would change it: "a recovery to $180+ before mid-October" or "a run of cuts of more than 5% by mid-October". Since then: no cuts; Morgan Stanley +$45 (16 Sep); the three raises of 8–10 Sep were already in the tape | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5 last paragraph | 2026-09-12 | 2026-09-17 | yes |
| 32 | Feed coverage: the yfinance/Benzinga feed drops whole firms (Gordon Haskett) and about a third of intermediate actions (96 chain breaks in 440 target actions); raise/cut counts are lower bounds; vendor means differ by ~$3 across universes (S&P $178.96 3 Sep, MarketBeat $179.97 11 Sep, yfinance $182.13 12 Sep, D file $181.81) | D §8 caveat 2; `data/processed/reverse_dcf/D/D_feed_chain_breaks.csv` | 2026-09-12 | 2026-09-17 | no |
| 33 | Monte Carlo S04 block (`abnb_path_mixture.py`): Δln T = known lags (+0.65%) + 0.305 × p1 (16 Sep → 14 Oct) + 0.205 × p2pre (14 Oct → 5 Nov) + 0.40 × day-1 + 0.14 × post-print (6 Nov → 15 Dec) + 0.5% stale-target refresh + N(0, 3.5%); base $183.22. Outputs: mean Δln T −0.4%, sd 5.9%; T on 15 Dec p5/25/50/75/95 = $165 / 175 / 183 / 190 / 201; P(T ≤ 176.8) **0.295** (0.34 on the feed-as-is base $181.81); P(T ≥ 190) 0.25; by 5 Nov branch: accel 0.15, flat 0.24, decel-guide-ok 0.27, decel-guide-below 0.38 | `datasets/mixture_base_run.json`, `sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
Queries 1–18 of `../close-15dec-2026/research-log.md` § 2 were run once for the batch. S04-specific: query 7 (the D panel files), query 8 (the fresh `upgrades_downgrades`, `analyst_price_targets`, `info`, `recommendations` pulls), query 14 ([WebSearch] Airbnb analyst price target cut September 2026 — surfaced the Morgan Stanley 16 Sep initiation, no cuts), queries 15–16 (WebFetch of the 247wallst and Cerbat Gem pages, verbatim in `sources/web_analyst_actions_capture_20260917.md`), the base-rate computation (`datasets/target_base_rates.py`), and query 17 (final 72-hour recency check: no target changes beyond Morgan Stanley; no change to the number).

## 3. Leading Hypothesis Entities
Airbnb, ABNB, Morgan Stanley, Truist, Raymond James, Baird, Bernstein, Rosenblatt, DA Davidson, yfinance/Benzinga feed, 5 Nov 2026 print

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| D's JUDGEMENT "base case cut of 3–4% over two to three months" taken at face value (P ≈ 0.5) | discarded as the point; kept as the anchor | it applied the lag-1 term of the 8–10 Sep fall but not the lag-2 term of the August +20.6% print rally, which is larger (+2.1% vs −1.6%, claim 30); since 12 Sep the tape has moved the other way (Morgan Stanley +$45, no cuts) |
| The mean target cannot fall $6.4 without a down print | discarded | 5 of 11 small-print windows still had a net cut (claim 28) and the 2023Q3 window fell 3.0% on a −2.9% price move; the residual sd (3.5% per three months) alone gives ~15% |
| Stale targets (Deutsche $154, TD Cowen $160, Mizuho $175, Tigress $185, CICC $165, set at prices $116–150) refresh upward after the print | kept as +0.5% drift | four of the five sit below the current price and every post-print refresh in 2Q26 was a raise; a full refresh of the two lowest to $175 alone is +$1.1 on the mean |
| Targets fall out of the 365-day window | discarded | no live target is dated before 13 Feb 2026 |
| Goldman relabelled to $165 (D's correction) | not applied | the feed convention is the resolving object and it carries $155; applying the correction would move the base by +$0.31 either way |
| A print-day cut wave like 2Q24 (−14.1% at +20, 19 cuts) | kept inside the decel-guide-below branch | that branch's median T is $180 with P(≤ 176.8) 0.38; a 2Q24-size day (−13%) produces a −5% chase in the model, which resolves Yes |

## 5. Independent Estimates
- base_rate_estimate: 0.22 — 63-session change in the mean target ≤ −3.5%: 0.18 (2023+) to 0.26 (all); print-centred windows 0.23 (2023+) to 0.27 (all) (claim 29); the four figures average 0.235, rounded to 0.22 because the 2023+ regime (Buy share at a series high, targets chasing up) is the relevant one
- decomposition_estimate: 0.30 — S02 price paths pushed through the tape-lag regression with the print chase (claim 33): 0.295 on the $183.22 base; the branch split (0.15 / 0.24 / 0.27 / 0.38) says the question is mostly "does 5 Nov decelerate and does the tape chase it down 3.5% within 27 sessions"
- anchor_estimate: 0.50 — the D note's published JUDGEMENT (claim 31) read as "the base case", dated 12 Sep, before the Morgan Stanley action and without the August lag-2 term; no tradable market exists (Kalshi and Polymarket carry no ABNB target or price-level market for December, S02 claim 17)
- anchor_value: 0.50 (repo prior, 2026-09-12)
- final_estimate: **0.29** (credible interval 0.20–0.40)
- final_minus_anchor: −0.21. Justified: (i) the anchor omitted the +2.1% lag-2 contribution of the August rally, which offsets the −1.6% from the September fall; (ii) the base moved up $1.4 on 16 Sep (Morgan Stanley), raising the required cut from 2.75% to 3.5%; (iii) the tape has produced no cut since 7 Aug and three raises into the fall, the same-day catch-up pattern D itself documents; (iv) the two base-rate families sit at 0.18–0.27. The final leans on the decomposition (0.30) with a small pull toward the base rate

## 6. Final Numbers
P(mean live target on 15 Dec ≤ $176.80) = **0.29**, credible interval **0.20–0.40**.
Distribution of the 15 Dec mean target (model, $183.22 base): p5 $165, p10 $169, p25 $175, p50 $183, p75 $190, p95 $201; P(≥ $190) 0.25 (feeds R12).
If the feed never carries the Morgan Stanley action (base stays $181.81): 0.34.
Conditional on the team's base 5 Nov branch (decel, guide below Street): 0.38; on an accelerating print: 0.15.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Print chase 0.40 (D's +20-session ratio, both signs) | 0.60: 0.36; 0.20: 0.23 |
| Base $183.22 (Morgan Stanley $170 in the feed) | feed as-is $181.81: 0.34 |
| Known lag terms +0.65% (August rally, September fall) | zero: 0.33 |
| Stale-target refresh +0.5% | none: 0.33 |
| Residual sd 3.5% over the window | 5%: 0.32 |
| P(accelerating 5 Nov print) 0.24 | 0.40: 0.26; 0.13: 0.31 |
| Day-1 conditional means shrunk | market-neutral print: 0.23; unshrunk: 0.32 |
| Regression betas 0.075 / 0.13 / 0.10 (full sample) | 2023+ betas (sum 0.44): ≈ 0.33 (scaling the price terms by 1.45) |

## 8. Monitoring Calendar
Update procedure: recompute the live tape (`datasets/target_base_rates.py`) weekly; the answer is mechanical once the mean is within $2 of the threshold in December.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-19 | feed refresh | confirm Morgan Stanley $170 appears (base $183.22); if the feed carries it as a rating-only row with no target, base stays $181.81 → 0.34 |
| 2026-10-02 | prelim memo due | quote 0.29 (0.20–0.40); the memo should not say "the tape will cut into the print" |
| 2026-10-14 | end of block 1 | re-run with the realised p1: price ≤ $155 (p1 ≈ −8%) → ≈ 0.40; ≥ $180 → ≈ 0.20 |
| 2026-10-15 to 11-04 | Q3 preview season | each net cut of ≥ $10 by a live firm moves the mean −$0.3; three previews cutting to ≤ $165 would move P to ≈ 0.40 |
| 2026-11-05/06 | print and reaction | day-1 ≤ −8%: 0.55–0.65 (4 of 6 down-5% prints cut ≥ 3.8% at +20; the 2Q25/3Q24 exceptions had run-ups or discounts, absent here); day-1 in (−5, +5): ≈ 0.20; day-1 ≥ +5%: ≈ 0.05 |
| 2026-11-25 | +13 sessions | most print-driven revisions are in (79% within 5 sessions in 2Q26); if the mean is ≤ $179 move to ≥ 0.6, if ≥ $185 move to ≤ 0.1 |
| 2026-12-15 | resolution | recompute the D-convention mean from the feed pulled after the close; fallback yfinance `targetMeanPrice` only if the feed is unavailable |
