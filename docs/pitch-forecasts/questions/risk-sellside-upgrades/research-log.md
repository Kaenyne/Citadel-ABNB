# RESEARCH LOG

Revision 2 (2026-09-17, audit-response revision of the 2026-09-17 initial forecast, Fable 5.1, batch A13 with R13 and R14; responds to `docs/pitch-forecasts/audits/A13-research-audit.md`, response in `audits/A13-audit-response.md`). Reproduction: `datasets/upgrade_base_rates.py` (pandas, reads S04's feed pull; unchanged) then `datasets/r12_model_v2.py` (numpy, seed 20260917, 400,000 draws, ~2 min with sensitivities; outputs `r12_v2_summary.json`, `r12_v2_sensitivity.csv`, `r12_v2_stdout.txt`). Revision 1's `r12_model.py` and its outputs are left untouched as the audit trail. Revision 1 was built on the revision-1 S02/S04 parameter set; revision 2 rebuilds it on the run's current inputs (S02/S04 revision 2), adopts B11's feed-capture convention, and moves the post-print upgrade means toward the empirical print-window record (§10).

## 0. Metadata
- question_name: risk-sellside-upgrades
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R12)
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

## 0b. Question (verbatim)
### Title
Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating upgrades (to Buy/Outperform-equivalent) from firms in the tracked feed, or will the mean target rise to ≥$190?
### Resolution Criteria
Yes on either condition using the feed convention of `data/processed/reverse_dcf/D/`. Resolution 15 Dec 2026.
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted: (1) "tracked feed" = `Ticker('ABNB').upgrades_downgrades` (Yahoo Finance / Benzinga), pulled after 15 Dec; an upgrade is a row with `Action == "up"` and `ToGrade` in the Buy-equivalent set {Buy, Outperform, Overweight, Positive, Strong Buy, Market Outperform, Sector Outperform, Top Pick, Accumulate, Add}, dated 17 Sep–15 Dec inclusive (feed timestamp, US Eastern date); initiations at Buy (`init`), reiterations, and upgrades to Hold-equivalent (e.g., Morgan Stanley's 16 Sep Underweight → Equal-weight) do not count; two rows from one firm on one day count once; (2) "mean target" = the D convention: mean of `currentPriceTarget` over the latest action per firm within 365 days with a positive target (the S04 object; $181.81 on the 11–12 Sep feed, $183.22 once the feed carries Morgan Stanley $170); (3) "rise to ≥$190" is read as **any feed date in the window** (the mean is recomputable for every date from dated actions) — this is a live re-reading of the resolution sentence worth about 5 points (0.317 on the 15 Dec reading vs 0.364 any-day, revision-2 parameters), it is the reading that makes Yes easier, and both readings are published in `forecasts/2026-09-17-forecast.json` so the memo can state which it quotes (A13-24); (4) Weiss Ratings and Phillip Securities are not in the feed (0 and 1 rows in 469), so their August actions are outside the object; (5) if the feed is unavailable on 15 Dec, the fallback is MarketBeat's dated action list restricted to the same firms; (6) **feed capture**: the feed is documented to drop actions (96 chain breaks in 440 target actions, whole firms missing; `data/processed/reverse_dcf/D/D_feed_chain_breaks.csv`); R12 and B11 (the two questions on this feed in this run) both thin every modelled count by a capture rate of 0.85 — the same convention, stated once here and once in B11 (A13-06). Because the historical rates that set the means are themselves feed counts, the thinning is a conservatism toward No of ~2–3 points, not a measured correction; capture 1.0 is the sensitivity row.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Feed (469 rows, pulled 2026-09-17T03:12Z, unchanged since 12 Sep): upgrades with `Action == up` since 2021: 26 all / 21 to Buy-equivalent. To-Buy upgrades by year: 2021 5, 2022 1, 2023 1, 2024 2, 2025 4, 2026 YTD 8 (B. Riley 12 Jan, Citizens 4 Feb, Deutsche 13 Feb, Evercore 13 Feb, Wells 22 Apr, Oppenheimer 4 May, Wedbush 7 Aug, Raymond James 8 Sep). Trailing 12 months (17 Sep 2025–16 Sep 2026): 9 (RBC 17 Dec 2025 plus the eight); 4 of the 9 within 5 days of a print. 2026 "up" actions to Hold-equivalent (not counting): Cantor, Barclays, Wells (Jan), Truist (Mar) | `../sellside-mean-target-cut-by-15dec/sources/yfinance_upgrades_downgrades_20260917T031221Z.csv`; `datasets/feed_upgrades_all.csv` | 2026-09-16 | 2026-09-17 | yes |
| 2 | 90-day rolling window counts of to-Buy upgrades (daily start dates): 2021+ mean 0.86, P(≥3) 0.062, P(≥2) 0.23, max 5; 2023+ mean 0.94, P(≥3) 0.090; 2024+ mean 1.25, P(≥3) 0.127, P(≥2) 0.38. All-"up" (incl. to-Hold): 2024+ P(≥3) 0.257. Print-shaped windows (−49 to +39 calendar days around each reaction day, the 17 Sep → 15 Dec shape): to-Buy counts per print 2023+ (15 prints, 15 Feb 2023 → 7 Aug 2026): **1, 0, 0, 0, 0, 2, 0, 0, 2, 1, 0, 0, 4, 2, 2** (sum 14, mean 0.93; P(≥3) 1 of 15 = 0.067; by day-1 sign: up ≥5% 1.33, down ≤−5% 0.33, small 0.91). **Post-print counts alone (2023+): 8 in 15 windows, mean 0.53; by day-1 sign: up ≥5% 1.67 (n 3: 1, 2, 2), down ≤−5% 0.20 (n 5: 0, 1, 0, 0, 0), small 0.29 (n 7: 2 of the 7 in the Feb 2026 window).** Same calendar window 17 Sep–15 Dec: 2021 1, 2022–2025 0. Share of to-Buy upgrades within 5 / 10 days of a print: 0.38 / 0.48 | `datasets/upgrade_base_rates.json` (from `upgrade_base_rates.py`) | 2026-09-17 | 2026-09-17 | yes |
| 3 | Tape on **11–12 Sep** (panel last observation 11 Sep; live-target file dated 12 Sep): 32 live targets, mean $181.8125, median $182.5; Morgan Stanley re-initiated Equal-weight $170 on 16 Sep (from Underweight $125, which is the value in the 12 Sep file), not yet in the feed; with it the mean is $183.21875; $190 needs +3.70% (+4.5% on the feed-as-is base). yfinance `targetMeanPrice` $182.98 (40). Ratings: 22 Buy / 8 Hold / 2 Sell among the 32 live-target firms; 22 / 11 / 2 among the 35 firms with any action in 365 days; Buy share on the 24-month panel 59.5% (11 Sep), the series high; 09-note convention 49% Buy on 49 firms (4 Sep), also a high | S04 log claims 26, 31; `data/processed/reverse_dcf/D/D_positioning_summary.csv`, `D_live_targets_2026-09-12.csv`, `D_target_panel_daily.csv`; `sources/web_search_log.md` | 2026-09-11 to 2026-09-16 | 2026-09-17 | yes |
| 4 | Tape-lag regression (D §5): 21-session log change in the mean target on contemporaneous / lag-1 / lag-2 21-session price changes 0.075 / 0.13 / 0.10 (sum 0.30; 2023+ 0.44); print chase 0.40 at +20 sessions (up prints 0.47, 77 raises vs 10 cuts on six ≥+5% prints, mean target +6.3%); "Ratings move with prints, mostly in the direction of the print. Across the last four prints: 5 upgrades, 0 downgrades in the [−5, +25] session windows; across all 23 prints 21 upgrades, 15 downgrades." Off-print: after a 15%+ 21-session rise the mean target rose 5.9% over the next 42 sessions | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5; `data/processed/reverse_dcf/D/D_print_revisions_summary.csv`, `D_chase_regression.csv` | 2026-09-12 | 2026-09-17 | yes |
| 5 | D panel (n_targets ≥ 10, 1,429 rows 4 Jan 2021 – 11 Sep 2026), log mean target, threshold +3.70%: 35-session change with **no print inside the window**: n 577, P(≥ +3.7%) 0.019, P(≥ +2%) 0.12, mean −0.26%, sd 2.1% (2023+: n 367, 0.030 / 0.17 / +0.48% / 1.6%); **with a print inside: n 817, P(≥ +3.7%) 0.359** (all 35-session windows, prints or not: 0.218 all / 0.260 2023+ — revision 1 mislabelled these as the with-print figures, A13-12). 63-session windows (all, n 1,366): P(end ≥ +3.7%) **0.372**, P(running max ≥ +3.7%) **0.441**, ratio **1.185** (revision 1 had 0.353 / 0.429 / 1.22); 2023+ (n 863): 0.440 / 0.490, ratio 1.113. So the tape moves ≥3.7% almost only through prints (0.019 vs 0.359), and the any-day premium over the end-of-window reading is 11–19% | computed from `data/processed/reverse_dcf/D/D_target_panel_daily.csv` and `data/processed/abnb_earnings_reactions.csv` (query 6; recomputed by the audit's script `audits/A13-reproduce.py`, block "R12 feed, live targets, D panel") | 2026-09-17 | 2026-09-17 | yes |
| 6 | **S02 revision 2** (`../close-15dec-2026/datasets/abnb_path_mixture_v2.py` PARAMS, `../close-15dec-2026/forecasts/2026-09-17-forecast.json`): print-state weights accel 0.32 / flat 0.10 / decel-guide-ok 0.13 / decel-guide-below 0.45 with day-1 means +4.0 / −1.0 / −2.5 / −6.0, within-branch day-1 sd 8.45 solved from the variance identity so the unconditional sd is S01's 9.5%; post-print drifts to 15 Dec −1.5 / −0.5 / −0.5 / −1.0 over 26 sessions; 36 pre-print sessions; background vol 30%; total drift 6.97% a year; 15 Dec branch medians $172 / 165 / 163 / 156, unconditional median $166. **S04 revision 2** (`../sellside-mean-target-cut-by-15dec/forecasts/2026-09-17-forecast.json`, log claim 33): tape residual sd **5.0%** (exact hybrid equation on 21 print windows; revision 1 used 3.5%); 15 Dec mean-target distribution on the $183.22 base p5/25/50/75/95 $163 / 175 / 184 / 193 / 206; **P(≥ $190 on 15 Dec) 0.32** (revision 1: 0.25); P(≤ $176.8) 0.299 (this model reproduces 0.298) | as cited | 2026-09-17 (revision 2) | 2026-09-17 | yes |
| 7 | Positioning tests (09 note, D §7): Buy share vs forward 3-month excess return r 0.13 (n 66, p 0.30); 3-month change in Buy share vs forward 1-month r −0.24 (p 0.05, contrarian-signed, in-sample); "almost nothing outside the print moves the stock" — analyst actions, peer prints, buybacks and product launches produce abnormal returns indistinguishable from zero; the three exceptions are the S&P 500 inclusion announcement, the April 2025 tariff shock and the 3 Feb 2026 AI scare | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 item 6, item 9; `data/processed/reverse_dcf/D/D_positioning_summary.csv` | 2026-09-06 / 2026-09-12 | 2026-09-17 | yes |
| 8 | Web (17 Sep): no rating change 14–17 Sep other than Morgan Stanley EW $170; Weiss Ratings Hold → Buy (21 Aug) and Phillip Securities Hold → Reduce $158 (11 Aug; "an already expensive stock is made more expensive") are outside the feed; no cut since 7 Aug on the Cerbat Gem table; Rosenblatt initiated Buy $220 on 1 Sep (init, does not count) | `sources/web_search_log.md`; https://finance.yahoo.com/markets/stocks/articles/airbnb-just-hit-four-high-110129364.html ; https://www.thecerbatgem.com/2026/09/16/weekly-analysts-ratings-changes-for-airbnb-abnb.html | 2026-08-22 / 2026-09-16 | 2026-09-17 | no |
| 9 | Kalshi (KXABNB, 03:56Z) carries only Q3-2026 nights strikes; Polymarket (public-search "airbnb", 03:56Z) only weekly/September price-hit ladders; no market on ratings, targets or the December price | `sources/kalshi_KXABNB_20260917T035627Z.json`, `sources/polymarket_search_airbnb_20260917T035627Z.json` | 2026-09-17 | 2026-09-17 | no |
| 10 | B11 (`../bonus-sellside-downgrades/forecasts/2026-09-17-forecast.json`, log claim 7): the same feed, the same run, thins its downgrade counts by capture 0.85 ("counts are lower bounds"; sensitivity: 1.0 → 0.19, 0.70 → 0.11 on B11's 0.14). Adopted here as the shared convention (convention (6)) | as cited | 2026-09-17 | 2026-09-17 | yes |
| 11 | **Model, revision 2** (`datasets/r12_model_v2.py`, seed 20260917, n 400,000): P(Yes) **0.469**; upgrades leg 0.205 (mean count 1.45; P(≥1) 0.62, P(≥2) 0.36, P(≥4) 0.11); target leg 0.364 any-day (**0.317 on 15 Dec** = S04 revision 2's 0.32); both 0.10. By branch: accel 0.65 (up 0.38, T 0.49), flat 0.49, decel-ok 0.44, decel-below 0.34 (up 0.10, T 0.27). P(Yes | day-1 ≥ +5%) 0.78; inside (−5, +5) 0.50; ≤ −5% 0.24. P(branch | Yes): accel 0.45, flat 0.11, decel-ok 0.12, decel-below 0.33. E[15 Dec close | Yes] $179.9 (median $178.1) vs unconditional $165.5 ($163.1). Bridge from revision 1 (`r12_v2_sensitivity.csv`): revision-1 parameters 0.431 (file 0.4314) → S02/S04 revision-2 parameters 0.504 → + capture 0.85 0.478 → + post-print means 1.8/0.9/0.6/0.3 **0.469** (the auditor's construction with the empirical means 1.67/0.9/0.5/0.2: 0.459) | `datasets/r12_v2_summary.json`, `r12_v2_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 12 | A09 revision-2 adopted print states (`../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`): S01 states accel 0.261 / flat 0.104 / decel 0.636; with S01 revision 2's P(guide below \| decel) 0.761 → 0.26 / 0.10 / 0.15 / 0.48. S02 revision 2 still carries 0.32 / 0.10 / 0.13 / 0.45 and its rebasing note calls the change "immaterial" for S02; on this model the A09 states give **0.452** (sensitivity row) | as cited; `r12_v2_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the feed pull and the computed tables (16–17 Sep, zero to one day old against an 89-day window); the D note is 5 days old. Within the 7-day cap.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`; finished logs S04, S02, S03, S01, R01, F01 (and the F02/F03 JSONs)
2. [repo] `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5, §7, §8; `data/processed/reverse_dcf/D/` file list, `D_positioning_summary.csv`, `D_analyst_actions_2026-09-12.csv` (header), `D_target_panel_daily.csv` (tail)
3. [repo] `data/processed/overnight/09_positioning_ratings.csv` (Buy share 2023–2026, sampled every 60 sessions); `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 items 6 and 9
4. [repo, pandas] S04's feed pull `yfinance_upgrades_downgrades_20260917T031221Z.csv`: all 2026 rows by action type (55 main / 12 up / 4 reit / 2 init); grep for Weiss, Phillip, Rosenblatt, Morgan Stanley, Gordon Haskett
5. [computed] `datasets/upgrade_base_rates.py` (re-run 17 Sep; output identical to the earlier attempt's file)
6. [computed] D panel 35- and 63-session mean-target changes with and without a print inside the window; running-max vs end ratio (claim 5)
7. [repo] `../close-15dec-2026/datasets/abnb_path_mixture.py` (PARAMS and the S04 block, replicated in `r12_model.py`)
8. [Kalshi API] `markets?status=open&limit=100&series_ticker=KXABNB` — 2026-09-17T03:56:27Z, saved
9. [Polymarket public-search] airbnb — 03:56:27Z, saved
10. WebSearch: Airbnb ABNB analyst rating upgrade downgrade this week
11. WebFetch: finance.yahoo.com "Airbnb Just Hit a Four-Year High. The Downgrade Says That's the Problem." (Phillip Securities, 22 Aug)
12. [computed] `datasets/r12_model.py` (first version with a three-checkpoint any-day max: 0.487; rejected after query 6; final version with the measured any-day ratio: 0.431)
13. WebSearch: Airbnb news past 3 days (batch-level final 72-hour neutral recency check, charged to R14: fake-listing purge, $250M housing fund, World Cup host piece; nothing on ratings or targets; no change)
14. [revision 2, repo] `../close-15dec-2026/datasets/abnb_path_mixture_v2.py` (PARAMS), `../close-15dec-2026/forecasts/2026-09-17-forecast.json`, `../sellside-mean-target-cut-by-15dec/forecasts/2026-09-17-forecast.json` and log claim 33 / §6 (revision 2), `../bonus-sellside-downgrades/forecasts/2026-09-17-forecast.json` and log claim 7 (capture), `../day1-move-5nov/forecasts/2026-09-17-forecast.json` (revision 2), `../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`
15. [revision 2, computed] `audits/A13-reproduce.py` (the auditor's script, run from the repo root with `py -3.13 -B`; output in `audits/A13-reproduce.stdout.txt`): claims 1, 3, 5 re-verified; the 63-session all-history pair corrected to 0.372 / 0.441 / 1.185; the with-print 35-session figure 0.359 (n 817)
16. [revision 2, computed] `datasets/r12_model_v2.py` → `r12_v2_summary.json`, `r12_v2_sensitivity.csv` (claim 11, §7)

WebSearch calls charged to R12: 1 (query 10); batch total 3 of 15. No new web queries in revision 2.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, yfinance/Benzinga upgrades feed, Morgan Stanley, Raymond James, Wedbush, Oppenheimer, Wells Fargo, Deutsche Bank, Evercore, 5 Nov 2026 print, $190 mean target

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Any-day target leg built from three checkpoints (4 Nov, ~25 Nov, 15 Dec) with the S04 residual spread as a random walk (P(T leg) 0.35, total 0.487 on revision-1 parameters) | discarded | the D panel shows the mean target rose ≥3.7% in only 2–3% of print-free 35-session windows (claim 5); the checkpoint construction put ~15% on a pre-print crossing because the S04 residual is print-concentrated, not diffuse; replaced by the measured running-max ratio 1.15 (range 1.11–1.185) |
| Any-day ratio applied rank-preservingly (the paths that finish closest below $190 are the ones that touched it) | kept; assumption stated (A13-10) | the model has no path for the mean target inside the window, so the running-max premium is applied to the end-value distribution assuming perfect rank correlation between max and end; the premium also grows into the tail (tends to 2 in the driftless-diffusion limit) while the model's P(end) 0.32 sits below the 0.37–0.44 the ratio was measured on; the honest range of the leg is 0.317 (15 Dec only) to 0.364 (any-day) to ≈0.40 (three-checkpoint), carried in the interval |
| Count all `Action == up` rows (incl. to-Hold) | discarded | the question says "to Buy/Outperform-equivalent"; the all-up base rate (2024+ P(≥3) 0.26) is reported as a sensitivity only |
| Use the 2023–25 upgrade rate (4–5 per year) for the pre-print window | kept as a sensitivity (0.436) | the trailing-12-month rate is 9 per year and 8 of the 9 came in 2026; the regime-conditioned rate is the right base, tempered by the pool (13 non-Buy feed firms with a live action) |
| Post-print means at the revision-1 regime lift (2.0 / 1.0 / 0.7 / 0.35, 1.6–1.8× the empirical 2023+ print-window post counts 1.67 / 0.9 / 0.5 / 0.2) | replaced by the midpoint 1.8 / 0.9 / 0.6 / 0.3 (A13-07) | the 2026 regime (three prints: post counts 2, 0, 2 on day-1 moves +4.6 / +0.7 / +17.4) supports a lift on the up and small branches, but no 2026 print was a down print, so the lift on the decel branches has no evidence behind it; the midpoint carries the regime for the up branch and the record for the down branches; the empirical means are a sensitivity (0.459), ×1.5 / halved 0.506 / 0.430 |
| Feed capture 1.0 (revision 1) | replaced by 0.85 (A13-06, convention (6)) | one convention across R12 and B11; the thinning is a stated ~2–3-point conservatism because the means are feed-measured; capture 1.0 → 0.494 |
| Upgrades independent of the print branch | discarded | 38–48% of to-Buy upgrades fall within 5–10 days of a print and the last four prints drew 5 upgrades / 0 downgrades (claim 4); the model ties the post-print mean to the branch and to the day-1 draw |
| Mean target ≥$190 via a pre-print rally (price to $185+ by late October) | inside the model at low weight | needs a ~12% price rise (sum of betas 0.30) with a one-to-two-month lag; the pre-print block carries it through p1/p2pre |
| Feed never carries the Morgan Stanley $170 (base stays $181.81, $190 needs +4.5%) | sensitivity 0.434 | S04 flagged the same risk; check on the 19 Sep refresh |
| Goldman relabelled to $165 (D correction) | not applied | feed convention is the object; +$0.31 on the base either way |
| A09 revision-2 print states (accel 0.26) instead of S02 revision 2's 0.32 | sensitivity 0.452; S02 revision 2 kept as the base for coherence with S02/S03/S04/B11 | the orchestrator decides at X01 time which state vector the run carries; each −0.06 on P(accel) is worth about −0.017 here |

## 5. Independent Estimates
- base_rate_estimate: 0.50 — union of two regime-conditioned base rates: the upgrades leg at the trailing-12-month feed rate (9/yr → 90-day mean 2.2 → Poisson P(≥3) 0.38; the 2024+ empirical 90-day rate is 0.13 and the print-window rate 0.07; taken at 0.22, midway and thinned for capture) and the target leg at the 63-session rates P(end ≥ +3.7%) 0.372 (all) × 1.185 = 0.44, 0.440 × 1.113 = 0.49 (2023+, a bull-regime sample), or S04 revision 2's 15 Dec 0.32 × 1.15 = 0.37 → taken at 0.40; union with the print-driven intersection (≈0.10 in the model) ≈ 0.52; shaded to 0.50 because the all-history tape rates include the 2021 bull tape
- decomposition_estimate: 0.47 — joint simulation over the S02 revision-2 branches (claim 11): upgrades 0.205 + target 0.364 − both 0.10
- anchor_estimate: 0.32 — no tradable market (claim 9); the repo prior is S04 revision 2's P(mean target ≥ $190 on 15 Dec) = 0.32 (claim 6), which covers only the target leg on one date. **NOT_INDEPENDENTLY_DERIVED**: the anchor is the same tape block this model replicates (the model's own 15 Dec reading is 0.317), so it checks the arithmetic, not the forecast; S04 revision 2 flags its own anchor the same way
- anchor_value: 0.32 (S04 revision 2, 2026-09-17; target leg, 15 Dec reading only; not independent)
- final_estimate: **0.47** (credible interval 0.34–0.60)
- final_minus_anchor: +0.15. Justified by construction rather than by information the anchor lacks: the anchor omits the upgrades leg (0.205 on its own, correlated 0.10 with the target leg: +0.10) and the any-day reading (+0.05); the decomposition (0.47) and the base rate (0.50) agree; the final is the decomposition, not shaded further because the capture convention already carries the pool constraint (Buy share at a series high) and the one-year 2026 upgrade record on the No side

## 6. Final Numbers
P(≥3 to-Buy upgrades in the feed 17 Sep–15 Dec, or the feed-convention mean target ≥ $190 at any feed date in the window) = **0.47**, credible interval **0.34–0.60**.
On the 15 Dec-only reading of the target leg: **0.43** (published alongside so the memo can state which reading it quotes).
Legs: upgrades 0.20 (P(count = 0/1/2/3/4/5+) 0.38 / 0.26 / 0.16 / 0.09 / 0.05 / 0.06); target 0.36 any-day, 0.32 on 15 Dec only; both 0.10.
By 5 Nov branch: accelerating print 0.65; flat 0.49; decelerating with the guide at/above Street 0.44; decelerating with the guide below Street (the team's base case) 0.34. Conditional on a day-1 move ≥ +5%: 0.78; inside (−5, +5): 0.50; ≤ −5%: 0.24.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/r12_model_v2.py` (`r12_v2_sensitivity.csv`); base 0.469.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| S02/S04 revision-2 parameters | revision-1 parameter set (weights 0.24/0.14/0.10/0.52, drifts −2/−1/−1/−2.5, residual 3.5%, capture 1.0, rev-1 post means): 0.431; tape residual sd 3.5% alone: 0.44; 6.68% (Astra): 0.50; within-branch day-1 sd 7.5: 0.47 |
| Feed capture 0.85 | 1.0: 0.49; 0.70: 0.44 |
| Pre-print to-Buy mean 0.7 (trailing-12m off-print rate) | 0.35 (2023–25 rate): 0.44; 1.2 (no pool limit): 0.52 |
| Post-print means by branch 1.8 / 0.9 / 0.6 / 0.3 | empirical 1.67/0.9/0.5/0.2 (auditor): 0.46; halved: 0.43; ×1.5: 0.51; flat 0.93 (2023+ print-window mean): 0.48 |
| Any-day ratio 1.15 | 15 Dec only: 0.43; 1.185 (all history): 0.48; 1.11 (2023+): 0.46 |
| Base $183.22 (MS $170 in the feed) | feed as-is $181.81 (threshold effectively $192): 0.43 |
| P(accelerating print) 0.32 (S02 rev 2) | A09 rev-2 states 0.26/0.10/0.15/0.48: 0.45; 0.40 (Street-like): 0.49; 0.22 (R02 alt-data leg): 0.44 |
| Print chase 0.40 | 0.60: 0.47; 0.20: 0.48 (upgrade leg unchanged) |
| Day-1 means shrunk (S02) | unshrunk: 0.46; market-neutral (all 0): 0.51 |
| Negative-binomial overdispersion 1.6 | Poisson: 0.45; 2.5: 0.47 |
| Joint bull (accel 0.40, post ×1.5, pre 1.2, chase 0.6, capture 1.0) | 0.62 |
| Joint bear (accel 0.22, post halved, pre 0.35, chase 0.2, capture 0.7, 15 Dec only) | 0.34 |

Pre-mortem ("it is 15 Dec 2026 and I was wrong"): (1) **Yes at 0.47 and it resolved No on a decelerating print** — the base case; priced at 0.66 within the decel-guide-below branch. (2) **Resolved Yes on upgrades alone after a decelerating print** — the D note's "print-day cuts are rare" also means upgrades on a sell-off are rare (down ≤−5% windows: 0.2 post-print to-Buy upgrades), but a 9–10% print with a "high single digits" bucket could be read as de-risking (4Q22-style) and draw two or three catch-up upgrades from the 13 Hold/Sell firms; priced at 0.10 in that branch. (3) **Resolved Yes on the target leg before the print** — a rally to $185+ into late October plus Q3-preview raises; the panel says 2–3% for print-free 35-session windows; priced through p1/p2pre. (4) **The feed drops actions** (96 chain breaks, whole firms missing) so three real upgrades count as two — priced by capture 0.85 (convention (6)); the reverse error (the feed captures better than 0.85 and the thinning was a double count) is the capture-1.0 row, 0.49. (5) **Resolved Yes because the resolver reads a different vendor mean** (MarketBeat/S&P means differ by ~$3): fenced by convention (2). (6) **Resolved No on the 15 Dec reading after touching $190 in late November** — the any-day convention (3) resolves this Yes; if the memo quotes the 15 Dec reading it should quote 0.43. Asymmetry: the memo uses this as a risk to the short; overstating it costs little, understating it hides the thesis-breaker marker; the interval's top (0.60) is the joint-bull region, its bottom (0.34) the joint-bear-plus-15-Dec-only region.

## 8. Monitoring Calendar
Update procedure: recompute the live tape and the to-Buy count weekly from the feed (`datasets/upgrade_base_rates.py` on a fresh pull); re-run `r12_model_v2.py` with the branch weights of the day; the number is mechanical once two upgrades are in or the mean is within $3 of $190.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-19 | feed refresh | confirm Morgan Stanley $170 appears (base $183.22); if not, 0.43 |
| 2026-10-02 | prelim memo due | quote 0.47 (0.34–0.60) on the any-day reading, 0.43 on the 15 Dec reading; present as the thesis-breaker marker, not a standalone risk |
| 2026-10-14 | end of tape block 1 | price ≥ $180: 0.52 (lag-1 term positive); ≤ $155: 0.41 |
| 2026-10-15 to 11-04 | Q3 preview season | each to-Buy upgrade already in: 0 → 0.47, 1 → ≈0.52, 2 → ≈0.68 (hand-scaled from the count distribution; re-run for the live number); mean ≥ $187 before the print: 0.58 |
| 2026-11-05/06 | print and reaction | day-1 ≥ +5%: 0.78 (≈0.90 if the mean re-rates ≥ $188 same day); in (−5, +5): 0.50; ≤ −5%: 0.24 |
| 2026-11-25 | +13 sessions | 79% of print-driven revisions are in within 5 sessions; count upgrades and the mean; if 2 upgrades and mean ≥ $186 move to ≥ 0.7; if 0–1 and mean ≤ $180 move to ≤ 0.10 |
| 2026-12-15 | resolution | pull the feed after the close; count to-Buy upgrades 17 Sep–15 Dec; recompute the D-convention mean for every date in the window (any-day) and on 15 Dec (both readings recorded) |

## 9. Impact
If R12 resolves Yes (three to-Buy upgrades or a $190 mean target), deltas versus the memo's base case:

| Item | Delta if R12 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 (indirect: P(accelerating print \| Yes) 0.45 vs 0.32 unconditional) | claim 11; the event carries no operating content of its own |
| 4Q26 nights (pts) | 0 (indirect) | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 (indirect) | — |
| FY27 revenue ($M) | 0 (indirect) | — |
| FY26 / FY27 adj. EBITDA margin (pp) | 0 / 0 | — |
| FY27 EPS ($) | 0 | — |
| Stock ($/share) | **+$14.5 as a marker** (E[15 Dec close \| Yes] $179.9 vs $165.5 unconditional; median +$15.0) — this is the print branch the event labels, already counted in R01/R02/S02 and **not additive**; **direct effect of the upgrades themselves ≈ +$1.5** (judgement: three upgrade days at ~+0.3% abnormal each; 09 note: analyst actions outside prints produce no detectable abnormal return, Buy-share changes are contrarian-signed) | claim 11; claim 7 |
| **EV = P × impact** | marker: 0.47 × $14.5 = $6.8/share (not additive with R01/R02/S02); **direct: 0.47 × $1.5 ≈ $0.7/share** | |
| Materiality | **Immaterial as an independent line** (direct EV < $1/share); material only as a marker of the thesis-breaker branch. The memo can drop "sell-side upgrades" as a separate risk and mention it inside the accelerating-print scenario | |

## 10. Revision notes
| # | Change (revision 1 → revision 2) | Finding |
|---|---|---|
| 1 | Model rebuilt on the S02/S04 revision-2 parameter set (weights 0.32/0.10/0.13/0.45, within-branch day-1 sd 8.45, drifts −1.5/−0.5/−0.5/−1.0, 36/26 sessions, 30% vol, 6.97% drift, tape residual sd 5.0%): 0.431 → 0.504 on parameters alone; claim 6 rewritten; the model's 15 Dec target reading 0.317 reproduces S04 revision 2's 0.32 | A13-01 |
| 2 | Feed capture 0.85 on every modelled count (B11's convention), stated as convention (6) with the double-thin caveat: 0.504 → 0.478 | A13-06 |
| 3 | Post-print branch means 2.0/1.0/0.7/0.35 → 1.8/0.9/0.6/0.3 (midpoint of the regime lift and the empirical 2023+ print-window post counts 1.67/0.9/0.5/0.2, claim 2): 0.478 → 0.469; empirical means as a sensitivity (0.459) | A13-07 |
| 4 | Any-day construction kept; the rank-preserving assumption and the tail growth of the running-max premium stated in §4; all-history 63-session figures corrected to 0.372 / 0.441 / 1.185; the leg's range 0.317–0.40 carried in the interval, which widens to 0.34–0.60 | A13-10 |
| 5 | Claim 5: "with prints inside 0.22 / 0.26" corrected to "all windows 0.218 / 0.260; with a print inside 0.359 (n 817)" | A13-12 |
| 6 | Anchor 0.25 (S04 rev 1) → 0.32 (S04 rev 2), flagged NOT_INDEPENDENTLY_DERIVED; final − anchor +0.17 → +0.15 with the construction-based justification | A13-13 |
| 7 | Claim 2: the print-window series printed as 15 values (1,0,0,0,0,2,0,0,2,1,0,0,4,2,2); post-print counts by day-1 sign added | A13-14 |
| 8 | Claim 3: tape dated 11–12 Sep (panel last row 11 Sep, live-target file 12 Sep, Morgan Stanley in the file at $125) | A13-15 |
| 9 | §9 marker +$14.6 → +$14.5 (E[15 Dec \| Yes] $179.9 vs $165.5); EV-as-marker $6.1 → $6.8; direct effect and verdict unchanged | A13-22 |
| 10 | Convention (3): both readings of "rise to ≥ $190" published in `forecasts/2026-09-17-forecast.json` (`final.p` any-day 0.47; `final.p_dec15_only_reading` 0.43); pre-mortem item (6) added | A13-24 |
| 11 | Headline 0.42 (0.30–0.55) → **0.47 (0.34–0.60)**; base rate 0.45 → 0.50; decomposition 0.43 → 0.47; branch, day-1 and count conditionals updated; monitoring ladder re-based | A13-01/06/07 |
| 12 | Not in the audit: A09 revision-2 adopted print states (accel 0.26) recorded as claim 12 and a sensitivity row (0.452); S02 revision 2 kept as the base for coherence with S02/S03/S04/B11 | — |

## RESUME
The next agent (X01 or a further revision) should re-run `datasets/upgrade_base_rates.py` on a fresh feed pull and `datasets/r12_model_v2.py` (deterministic, ~2 min), and decide two things with the orchestrator: (1) which print-state vector the run carries — S02 revision 2 (0.32 accel; 0.47 here) or the A09 revision-2 adopted states (0.26 accel; 0.45 here); (2) which reading of "rise to ≥ $190" the memo quotes — any-day 0.47 or 15 Dec 0.43. The capture convention (0.85, stated conservatism) should be applied identically in B11's revision 2. On 19 Sep confirm the Morgan Stanley $170 row is in the feed.
