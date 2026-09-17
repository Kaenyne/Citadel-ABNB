# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A13 with R13 and R14). Reproduction: `datasets/upgrade_base_rates.py` (pandas, reads S04's feed pull) then `datasets/r12_model.py` (numpy, seed 20260917, 400,000 draws, ~90 s with sensitivities). A previous attempt at this batch was cut off before writing; its scripts were re-run and checked, and the R12 model was rebuilt (the any-day construction changed, §4).

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
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating upgrades (to Buy/Outperform-equivalent) from firms in the tracked feed, or will the mean target rise to ≥$190?
### Resolution Criteria
Yes on either condition using the feed convention of `data/processed/reverse_dcf/D/`. Resolution 15 Dec 2026.
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted: (1) "tracked feed" = `Ticker('ABNB').upgrades_downgrades` (Yahoo Finance / Benzinga), pulled after 15 Dec; an upgrade is a row with `Action == "up"` and `ToGrade` in the Buy-equivalent set {Buy, Outperform, Overweight, Positive, Strong Buy, Market Outperform, Sector Outperform, Top Pick, Accumulate, Add}, dated 17 Sep–15 Dec inclusive (feed timestamp, US Eastern date); initiations at Buy (`init`), reiterations, and upgrades to Hold-equivalent (e.g., Morgan Stanley's 16 Sep Underweight → Equal-weight) do not count; two rows from one firm on one day count once; (2) "mean target" = the D convention: mean of `currentPriceTarget` over the latest action per firm within 365 days with a positive target (the S04 object; $181.81 on the 16 Sep feed, $183.22 once the feed carries Morgan Stanley $170); (3) "rise to ≥$190" is read as any feed date in the window (the mean is recomputable for every date from dated actions), and the 15 Dec-only reading is reported alongside; (4) Weiss Ratings and Phillip Securities are not in the feed (0 and 1 rows in 469), so their August actions are outside the object; (5) if the feed is unavailable on 15 Dec, the fallback is MarketBeat's dated action list restricted to the same firms.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Feed (469 rows, pulled 2026-09-17T03:12Z, unchanged since 12 Sep): upgrades with `Action == up` since 2021: 26 all / 21 to Buy-equivalent. To-Buy upgrades by year: 2021 5, 2022 1, 2023 1, 2024 2, 2025 4, 2026 YTD 8 (B. Riley 12 Jan, Citizens 4 Feb, Deutsche 13 Feb, Evercore 13 Feb, Wells 22 Apr, Oppenheimer 4 May, Wedbush 7 Aug, Raymond James 8 Sep). Trailing 12 months (17 Sep 2025–16 Sep 2026): 9 (RBC 17 Dec 2025 plus the eight); 4 of the 9 within 5 days of a print. 2026 "up" actions to Hold-equivalent (not counting): Cantor, Barclays, Wells (Jan), Truist (Mar) | `../sellside-mean-target-cut-by-15dec/sources/yfinance_upgrades_downgrades_20260917T031221Z.csv`; `datasets/feed_upgrades_all.csv` | 2026-09-16 | 2026-09-17 | yes |
| 2 | 90-day rolling window counts of to-Buy upgrades (daily start dates): 2021+ mean 0.86, P(≥3) 0.062, P(≥2) 0.23, max 5; 2023+ mean 0.94, P(≥3) 0.090; 2024+ mean 1.25, P(≥3) 0.127, P(≥2) 0.38. All-"up" (incl. to-Hold): 2024+ P(≥3) 0.257. Print-shaped windows (−49 to +39 calendar days around each reaction day, the 17 Sep → 15 Dec shape): to-Buy counts per print 2023+: 0,0,0,0,2,0,0,2,1,0,0,4,2,2 (mean 0.93; P(≥3) 1 of 15 = 0.067; by day-1 sign: up ≥5% 1.33, down ≤−5% 0.33, small 0.91). Same calendar window 17 Sep–15 Dec: 2021 1, 2022–2025 0. Share of to-Buy upgrades within 5 / 10 days of a print: 0.38 / 0.48 | `datasets/upgrade_base_rates.json` (from `upgrade_base_rates.py`) | 2026-09-17 | 2026-09-17 | yes |
| 3 | Tape on 16 Sep: 32 live targets, mean $181.81, median $182.5; Morgan Stanley re-initiated Equal-weight $170 on 16 Sep (from Underweight $125), not yet in the feed; with it the mean is $183.22; $190 needs +3.7% (+4.5% on the feed-as-is base). yfinance `targetMeanPrice` $182.98 (40). Ratings: 22 Buy / 8 Hold / 2 Sell among the 32 live-target firms; 22 / 11 / 2 among the 35 firms with any action in 365 days; Buy share on the 24-month panel 59.5% (11 Sep), the series high; 09-note convention 49% Buy on 49 firms (4 Sep), also a high | S04 log claims 26, 31; `data/processed/reverse_dcf/D/D_positioning_summary.csv`, `D_live_targets_2026-09-12.csv`, `D_target_panel_daily.csv`; `sources/web_search_log.md` | 2026-09-12 to 2026-09-16 | 2026-09-17 | yes |
| 4 | Tape-lag regression (D §5): 21-session log change in the mean target on contemporaneous / lag-1 / lag-2 21-session price changes 0.075 / 0.13 / 0.10 (sum 0.30; 2023+ 0.44); print chase 0.40 at +20 sessions (up prints 0.47, 77 raises vs 10 cuts on six ≥+5% prints, mean target +6.3%); "Ratings move with prints, mostly in the direction of the print. Across the last four prints: 5 upgrades, 0 downgrades in the [−5, +25] session windows; across all 23 prints 21 upgrades, 15 downgrades." Off-print: after a 15%+ 21-session rise the mean target rose 5.9% over the next 42 sessions | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5; `data/processed/reverse_dcf/D/D_print_revisions_summary.csv`, `D_chase_regression.csv` | 2026-09-12 | 2026-09-17 | yes |
| 5 | D panel (n_targets ≥ 10), measured here: 35-session log change in the mean target with no print inside the window: n 577, P(≥ +3.7%) 0.019, P(≥ +2%) 0.12, mean −0.26%, sd 2.1% (2023+: n 367, 0.030 / 0.17 / +0.48% / 1.6%); with prints inside (all): P(≥ +3.7%) 0.22 / 0.26 (2023+). 63-session windows (all): P(end ≥ +3.7%) 0.353, P(running max ≥ +3.7%) 0.429, ratio 1.22; 2023+: 0.438 / 0.49, ratio 1.12. So the tape moves ≥3.7% almost only through prints, and the any-day premium over the end-of-window reading is 12–22% | computed from `data/processed/reverse_dcf/D/D_target_panel_daily.csv` and `data/processed/abnb_earnings_reactions.csv` (query 6; numbers in this row) | 2026-09-17 | 2026-09-17 | yes |
| 6 | S04 (revision 1): 15 Dec mean-target distribution on the $183.22 base p5/25/50/75/95 $165 / 175 / 183 / 190 / 201; P(≥ $190) 0.25; P(≤ $176.8) 0.295 (replicated here 0.294); by 5 Nov branch P(≤176.8) accel 0.15 … decel-below 0.38. S02 branch weights accel 0.24 / flat 0.14 / decel-guide-ok 0.10 / decel-guide-below 0.52 with day-1 means +4.0 / −1.0 / −2.5 / −6.0 (sd 7.5) and drifts to 15 Dec −2.0 / −1.0 / −1.0 / −2.5; 15 Dec branch medians $170 / 163 / 161 / 152 | `../sellside-mean-target-cut-by-15dec/research-log.md` §5–6; `../close-15dec-2026/datasets/abnb_path_mixture.py` PARAMS | 2026-09-17 | 2026-09-17 | yes |
| 7 | Positioning tests (09 note, D §7): Buy share vs forward 3-month excess return r 0.13 (n 66, p 0.30); 3-month change in Buy share vs forward 1-month r −0.24 (p 0.05, contrarian-signed, in-sample); "almost nothing outside the print moves the stock" — analyst actions, peer prints, buybacks and product launches produce abnormal returns indistinguishable from zero; the three exceptions are the S&P 500 inclusion announcement, the April 2025 tariff shock and the 3 Feb 2026 AI scare | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 item 6, item 9; `data/processed/reverse_dcf/D/D_positioning_summary.csv` | 2026-09-06 / 2026-09-12 | 2026-09-17 | yes |
| 8 | Web (17 Sep): no rating change 14–17 Sep other than Morgan Stanley EW $170; Weiss Ratings Hold → Buy (21 Aug) and Phillip Securities Hold → Reduce $158 (11 Aug; "an already expensive stock is made more expensive") are outside the feed; no cut since 7 Aug on the Cerbat Gem table; Rosenblatt initiated Buy $220 on 1 Sep (init, does not count) | `sources/web_search_log.md`; https://finance.yahoo.com/markets/stocks/articles/airbnb-just-hit-four-high-110129364.html ; https://www.thecerbatgem.com/2026/09/16/weekly-analysts-ratings-changes-for-airbnb-abnb.html | 2026-08-22 / 2026-09-16 | 2026-09-17 | no |
| 9 | Kalshi (KXABNB, 03:56Z) carries only Q3-2026 nights strikes; Polymarket (public-search "airbnb", 03:56Z) only weekly/September price-hit ladders; no market on ratings, targets or the December price | `sources/kalshi_KXABNB_20260917T035627Z.json`, `sources/polymarket_search_airbnb_20260917T035627Z.json` | 2026-09-17 | 2026-09-17 | no |
| 10 | Model (this log, `datasets/r12_model.py`, seed 20260917, n 400,000): P(Yes) **0.431**; upgrades leg 0.245 (mean count 1.67; P(≥1) 0.68, P(≥2) 0.41, P(≥4) 0.14); target leg 0.286 any-day (0.249 on 15 Dec; the three-checkpoint construction 0.351 is reported and rejected, §4); both 0.10. By branch: accel 0.68 (up 0.49, T 0.45), flat 0.50, decel-ok 0.43, decel-below 0.30 (up 0.13, T 0.20). P(Yes | day-1 ≥ +5%) 0.80; P(Yes | day-1 ≤ −5%) 0.21. P(branch | Yes): accel 0.38, flat 0.16, decel-ok 0.10, decel-below 0.36. E[15 Dec close | Yes] $175.7 (median $174.6) vs unconditional $161.1 ($158.9) | `datasets/r12_summary.json`, `r12_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |

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

WebSearch calls charged to R12: 1 (query 10); batch total 3 of 15.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, yfinance/Benzinga upgrades feed, Morgan Stanley, Raymond James, Wedbush, Oppenheimer, Wells Fargo, Deutsche Bank, Evercore, 5 Nov 2026 print, $190 mean target

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Any-day target leg built from three checkpoints (4 Nov, ~25 Nov, 15 Dec) with the S04 residual spread as a random walk (P(T leg) 0.35, total 0.487) | discarded | the D panel shows the mean target rose ≥3.7% in only 2–3% of print-free 35-session windows (claim 5); the checkpoint construction put ~15% on a pre-print crossing because the S04 residual (3.5% over 63 sessions) is print-concentrated, not diffuse; replaced by the measured running-max ratio 1.15 (range 1.12–1.22) applied monotonically |
| Count all `Action == up` rows (incl. to-Hold) | discarded | the question says "to Buy/Outperform-equivalent"; the all-up base rate (2024+ P(≥3) 0.26) is reported as a sensitivity only |
| Use the 2023–25 upgrade rate (4–5 per year) for the pre-print window | kept as a sensitivity (0.386) | the trailing-12-month rate is 9 per year and 8 of the 9 came in 2026; the regime-conditioned rate is the right base, tempered by the pool (13 non-Buy feed firms with a live action) |
| Upgrades independent of the print branch | discarded | 38–48% of to-Buy upgrades fall within 5–10 days of a print and the last four prints drew 5 upgrades / 0 downgrades (claim 4); the model ties the post-print mean to the branch and to the day-1 draw |
| Mean target ≥$190 via a pre-print rally (price to $185+ by late October) | inside the model at low weight | needs a ~12% price rise (sum of betas 0.30) with a one-to-two-month lag; the pre-print block carries it through p1/p2pre |
| Feed never carries the Morgan Stanley $170 (base stays $181.81, $190 needs +4.5%) | sensitivity 0.399 | S04 flagged the same risk; check on the 19 Sep refresh |
| Goldman relabelled to $165 (D correction) | not applied | feed convention is the object; +$0.31 on the base either way |

## 5. Independent Estimates
- base_rate_estimate: 0.45 — union of two regime-conditioned base rates: the upgrades leg at the trailing-12-month rate (9/yr → 90-day mean 2.2 → Poisson P(≥3) 0.38; the 2024+ empirical 90-day rate is 0.13 and the print-window rate 0.07, so the leg is taken at 0.25, midway, for the shrinking pool) and the target leg at the all-history 63-session rate P(end ≥ +3.7%) 0.35 × 1.15 any-day = 0.40 (2023+ 0.44 × 1.12 = 0.49, a bull-regime sample); union with the observed print-driven correlation ≈ 0.45
- decomposition_estimate: 0.43 — joint simulation over the S02 branches (claim 10): upgrades 0.245 + target 0.286 − both 0.10
- anchor_estimate: 0.25 — no tradable market (claim 9); the repo prior is S04's P(mean target ≥ $190 on 15 Dec) = 0.25 (revision 1, 17 Sep, "feeds R12"), which covers only the target leg on one date
- anchor_value: 0.25 (S04 revision 1, 2026-09-17; target leg, 15 Dec reading only)
- final_estimate: **0.42** (credible interval 0.30–0.55)
- final_minus_anchor: +0.17. Justified: the anchor omits the upgrades leg (0.25 on its own, correlated 0.10 with the target leg) and the any-day reading (+0.04); the decomposition and the base rate agree at 0.43–0.45; the final is shaded to 0.42 for the pool constraint (Buy share at a series high) and because the 2026 upgrade rate is one year of data

## 6. Final Numbers
P(≥3 to-Buy upgrades in the feed 17 Sep–15 Dec, or the feed-convention mean target ≥ $190 at any feed date in the window) = **0.42**, credible interval **0.30–0.55**.
Legs: upgrades 0.25 (P(count = 0/1/2/3/4/5+) 0.32 / 0.26 / 0.17 / 0.10 / 0.06 / 0.08); target 0.29 any-day, 0.25 on 15 Dec only; both 0.10.
By 5 Nov branch: accelerating print 0.68; flat 0.50; decelerating with the guide at/above Street 0.43; decelerating with the guide below Street (the team's base case) 0.30. Conditional on a day-1 move ≥ +5%: 0.80; ≤ −5%: 0.21.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/r12_model.py` (`r12_sensitivity.csv`); base 0.431.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Pre-print to-Buy mean 0.7 (trailing-12m off-print rate) | 0.35 (2023–25 rate): 0.39; 1.2 (no pool limit): 0.50 |
| Post-print means by branch 2.0 / 1.0 / 0.7 / 0.35 | halved: 0.38; ×1.5: 0.48; flat 0.93 (2023+ print-window mean): 0.45 |
| Any-day ratio 1.15 | 15 Dec only: 0.405; 1.22 (all history): 0.44; 1.12 (2023+): 0.43 |
| Base $183.22 (MS $170 in the feed) | feed as-is $181.81 (threshold effectively $192): 0.40 |
| P(accelerating print) 0.24 | 0.40 (Street-like): 0.49; 0.13: 0.39 |
| Print chase 0.40 | 0.60: 0.43; 0.20: 0.44 (upgrade leg unchanged) |
| Tape residual sd 3.5% | 5%: 0.46 |
| Day-1 means shrunk (S02) | unshrunk: 0.42; market-neutral (all 0): 0.49 |
| Negative-binomial overdispersion 1.6 | Poisson: 0.42; 2.5: 0.43 |
| Joint bull (accel 0.40, post ×1.5, pre 1.2, chase 0.6) | 0.61 |
| Joint bear (accel 0.13, post halved, pre 0.35, chase 0.2, 15 Dec only) | 0.29 |

Pre-mortem ("it is 15 Dec 2026 and I was wrong"): (1) **Yes at 0.42 and it resolved No on a decelerating print** — the base case; priced at 0.70 within the decel-guide-below branch. (2) **Resolved Yes on upgrades alone after a decelerating print** — the D note's "print-day cuts are rare" also means upgrades on a sell-off are rare (down ≤−5% windows: 0.33 to-Buy upgrades), but a 9–10% print with a "high single digits" bucket could be read as de-risking (4Q22-style) and draw two or three catch-up upgrades from the 13 Hold/Sell firms; priced at 0.13 in that branch. (3) **Resolved Yes on the target leg before the print** — a rally to $185+ into late October plus Q3-preview raises; the panel says 2–3% for print-free 35-session windows; priced through p1/p2pre. (4) **The feed drops actions** (96 chain breaks, whole firms missing) so three real upgrades count as two — a resolution-source risk on the Yes side, which is why the upgrades leg is not carried at the raw 2026 rate. (5) **Resolved Yes because the resolver reads a different vendor mean** (MarketBeat/S&P means differ by ~$3): fenced by convention (2). Asymmetry: the memo uses this as a risk to the short; overstating it costs little, understating it hides the thesis-breaker marker; the interval's top (0.55) is the joint-bull region.

## 8. Monitoring Calendar
Update procedure: recompute the live tape and the to-Buy count weekly from the feed (`datasets/upgrade_base_rates.py` on a fresh pull); the number is mechanical once two upgrades are in or the mean is within $3 of $190.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-19 | feed refresh | confirm Morgan Stanley $170 appears (base $183.22); if not, 0.40 |
| 2026-10-02 | prelim memo due | quote 0.42 (0.30–0.55); present as the thesis-breaker marker, not a standalone risk |
| 2026-10-14 | end of tape block 1 | price ≥ $180: 0.47 (lag-1 term positive); ≤ $155: 0.36 |
| 2026-10-15 to 11-04 | Q3 preview season | each to-Buy upgrade already in: 0 → 0.42, 1 → 0.50, 2 → 0.66 (P(≥1 more) rises with the print inside the remaining window); mean ≥ $187 before the print: 0.55 |
| 2026-11-05/06 | print and reaction | day-1 ≥ +5%: 0.80 (0.90 if the mean re-rates ≥ $188 same day); in (−5, +5): 0.40; ≤ −5%: 0.21 |
| 2026-11-25 | +13 sessions | 79% of print-driven revisions are in within 5 sessions; count upgrades and the mean; if 2 upgrades and mean ≥ $186 move to ≥ 0.7; if 0–1 and mean ≤ $180 move to ≤ 0.10 |
| 2026-12-15 | resolution | pull the feed after the close; count to-Buy upgrades 17 Sep–15 Dec; recompute the D-convention mean for every date in the window |

## 9. Impact
If R12 resolves Yes (three to-Buy upgrades or a $190 mean target), deltas versus the memo's base case:

| Item | Delta if R12 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 (indirect: P(accelerating print | Yes) 0.38 vs 0.24 unconditional) | claim 10; the event carries no operating content of its own |
| 4Q26 nights (pts) | 0 (indirect) | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 (indirect) | — |
| FY27 revenue ($M) | 0 (indirect) | — |
| FY26 / FY27 adj. EBITDA margin (pp) | 0 / 0 | — |
| FY27 EPS ($) | 0 | — |
| Stock ($/share) | **+$14.6 as a marker** (E[15 Dec close | Yes] $175.7 vs $161.1 unconditional; median +$15.7) — this is the print branch the event labels, already counted in R01/R02/S02; **direct effect of the upgrades themselves ≈ +$1.5** (judgement: three upgrade days at ~+0.3% abnormal each; 09 note: analyst actions outside prints produce no detectable abnormal return, Buy-share changes are contrarian-signed) | claim 10; claim 7 |
| **EV = P × impact** | marker: 0.42 × $14.6 = $6.1/share (not additive with R01/R02); **direct: 0.42 × $1.5 ≈ $0.6/share** | |
| Materiality | **Immaterial as an independent line** (direct EV < $1/share); material only as a marker of the thesis-breaker branch. The memo can drop "sell-side upgrades" as a separate risk and mention it inside the accelerating-print scenario | |

## RESUME
The next agent (audit response) should re-run `datasets/upgrade_base_rates.py` then `datasets/r12_model.py` (deterministic, ~2 min) and attack three choices: (1) the any-day ratio 1.15 measured on the D panel's running max vs end (claim 5) — check the computation in query 6 by hand on `D_target_panel_daily.csv` (n_targets ≥ 10, log mean_target, 63-session windows); (2) the pre-print to-Buy mean 0.7 and the post-print branch means (2.0 / 1.0 / 0.7 / 0.35), which rest on nine upgrades in twelve months and 15 print windows — an auditor may prefer the 2024+ empirical rate (0.386); (3) the S02 branch weights carried unchanged (P(accel) 0.24) — if R01/R02 revision 2 moves P(accel), rescale (each +0.10 on P(accel) ≈ +0.04 on P). On 19 Sep confirm the Morgan Stanley $170 row is in the feed.
