# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A17 with B12 and B13). Reproduction: `datasets/downgrade_base_rates.py` (pandas, reads the fresh feed pull in `sources/`) then `datasets/b11_model.py` (numpy, seed 20260917, 400,000 draws, ~60 s with sensitivities). The model is the downgrade mirror of R12's `r12_model.py`: the same S02 print branches, day-1 draw and price blocks, with the count rates taken from the downgrade tape instead of the upgrade tape.

## 0. Metadata
- question_name: bonus-sellside-downgrades
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B11)
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
Between 17 Sep and 15 Dec 2026, will ABNB receive ≥3 rating downgrades from firms in the tracked feed?
### Resolution Criteria
Yes if ≥3 downgrades (to Hold/Sell-equivalent) in the feed convention of `data/processed/reverse_dcf/D/`. Resolution 15 Dec 2026.
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted (the mirror of R12's): (1) "tracked feed" = `Ticker('ABNB').upgrades_downgrades` (Yahoo Finance / Benzinga), pulled after 15 Dec; a downgrade is a row with `Action == "down"` and `ToGrade` in the Hold-equivalent set {Neutral, Hold, Equal-Weight, Market Perform, Sector Perform, Sector Weight, In-Line, Perform, Peer Perform, Mixed} or the Sell-equivalent set {Sell, Underweight, Underperform, Reduce, Strong Sell, Negative}, dated 17 Sep–15 Dec inclusive (feed timestamp, US Eastern date); every one of the feed's 20 historical `down` rows is to Hold or Sell, so the qualifier changes nothing historically; (2) a `down` row to a Buy-equivalent grade (e.g., Strong Buy → Buy), initiations at Hold/Sell (`init`), reiterations, and target cuts without a rating change (`main`) do not count; (3) two rows from one firm on one day count once; three downgrades from three firms are needed — one firm downgrading twice (Buy → Hold, then Hold → Sell) counts as two; (4) firms outside the feed (Weiss Ratings; Phillip Securities, whose 11 Aug 2026 Neutral → Reduce never appeared) are outside the object; (5) if the feed is unavailable on 15 Dec, the fallback is MarketBeat's dated action list restricted to the feed's firms.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Fresh feed pull 2026-09-17T08:21:55Z: 469 rows, identical to S04's 16 Sep pull (no row added 12–17 Sep; Morgan Stanley's 16 Sep Equal-weight $170 still absent); action mix main 350 / init 38 / reit 35 / up 26 / down 20. yfinance `analyst_price_targets`: mean $182.98, median $185, high $220, low $125, current $167.51 | [sources/yfinance_upgrades_downgrades_20260917T082155Z.csv](sources/yfinance_upgrades_downgrades_20260917T082155Z.csv), [sources/yfinance_analyst_price_targets_20260917T082155Z.json](sources/yfinance_analyst_price_targets_20260917T082155Z.json) | 2026-09-16 | 2026-09-17 | yes |
| 2 | The 20 downgrades in the feed, all to Hold/Sell (by year 2021 2, 2022 5, 2023 6, 2024 5, 2025 2, 2026 0): Atlantic Equities 5 Jan 2021; RBC 16 Dec 2021; Piper 10 Jan 2022, Gordon Haskett 18 Jan, BTIG 8 Feb, Baird 22 Nov, Morgan Stanley 7 Dec (EW → UW); Gordon Haskett 25 Jan 2023 (Hold → Underperform), Keybanc 3 Oct, Evercore 17 Nov, Jefferies 29 Nov, DBS 8 Dec, Barclays 12 Dec (EW → UW); DA Davidson 14 Feb 2024, Needham 11 Apr, HSBC 9 May, Argus 4 Sep, Phillip 12 Nov (Neutral → Reduce); Wedbush 2 May 2025, Truist 30 May 2025 (Hold → Sell). Last downgrade 30 May 2025: **474 days** to 16 Sep 2026, the longest gap in the series | [datasets/feed_downgrades_all.csv](datasets/feed_downgrades_all.csv) | 2026-09-16 | 2026-09-17 | yes |
| 3 | 90-day rolling window counts of downgrades (daily start dates): 2021+ mean 0.86, P(≥3) 0.106, P(≥2) 0.24, max 5; 2023+ mean 0.87, P(≥3) 0.082; 2024+ mean 0.65, P(≥3) 0.006 (max 3, once), P(≥2) 0.19. Rate 3.5 per year (2021+ and 2023+), 2.6 (2024+), 0 trailing twelve months. Same calendar window 17 Sep–15 Dec: 2021 0, 2022 2, 2023 **5**, 2024 1, 2025 0 (1 of 5 years ≥3) | [datasets/downgrade_base_rates.json](datasets/downgrade_base_rates.json) (from `downgrade_base_rates.py`) | 2026-09-17 | 2026-09-17 | yes |
| 4 | Downgrades follow price falls, not prints: share within 5 / 10 days of a print 0.20 / 0.25 (upgrades: 0.38 / 0.48), within 30 days after a print 0.45; 90-day windows starting after a 21-session fall ≤ −10%: mean 1.18, P(≥3) 0.164 (n 354) vs 0.65 / 0.079 after a 21-session move in (−10, 0] and 0.88 / 0.105 after a rise; post-print counts (reaction day to +39 calendar days) by the 39-day price move: ≤ −8% mean 1.00 (n 4), (−8, 0] 0.17 (n 6), > 0 0.46 (n 13); by day-1 sign: down ≤ −5% 0.83 post (n 6), small 0.55 (n 11), up ≥ +5% 0.00 (n 6). Print-shaped windows (−49 / +39 calendar days, the 17 Sep → 15 Dec shape): counts 0,0,0,0,3,0,0,2,1,0,0,4,1,2,1,1,0,2,0,0,0,0,0 (mean 0.74; P(≥3) 2 of 23 = 0.087, 2023+ 1 of 15 = 0.067); the two ≥3 windows were Feb 2022 (three pre-print cuts in the January 2022 growth sell-off) and Nov 2023 (Keybanc, Evercore, Jefferies, DBS after a "moderate" Q4 guide and a −20% October) | [datasets/downgrade_base_rates.json](datasets/downgrade_base_rates.json); `data/processed/abnb_earnings_reactions.csv`; `../close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv` | 2026-09-17 | 2026-09-17 | yes |
| 5 | Pool: 35 firms with a feed action in the last 365 days — 22 Buy, 11 Hold, 2 Sell (the R12 log's 22 / 11 / 2); Buy share on the 24-month panel 59.5% on 11 Sep, the series high; 22 Buy-rated firms are the downgrade pool (in Oct–Dec 2023, when five downgraded, the Buy share was ~45%) | R12 log claim 3; `data/processed/reverse_dcf/D/D_positioning_summary.csv`; [datasets/downgrade_base_rates.json](datasets/downgrade_base_rates.json) `pool_live_365d` | 2026-09-12 to 2026-09-17 | 2026-09-17 | yes |
| 6 | D note: "Ratings move with prints, mostly in the direction of the print. Across the last four prints: 5 upgrades, 0 downgrades in the [−5, +25] session windows; across all 23 prints 21 upgrades, 15 downgrades"; "print-day cuts are rare; a down print after a run-up or a wide discount produces no net cut within 20 sessions"; day-1 ≤ −5% prints (n 6) → mean target −3.8% at +20 sessions, 4 of 6 with a net cut; after a 21-session fall of 15%+ with no print, −5.6% over the next 42 sessions (16 episodes). D's print-revision file lists the rating-and-target cuts near prints: Baird +14 and Morgan Stanley +24 sessions after 3Q22 (−13.4%), Jefferies +18 after 3Q23 (−3.3%), Wedbush day 0 and Truist +19 after 1Q25 (+1.0%) | `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5; `data/processed/reverse_dcf/D/D_print_revision_actions.csv`, `D_print_revisions_summary.csv`, `D_chase_asymmetry.csv` | 2026-09-12 | 2026-09-17 | yes |
| 7 | Feed coverage: the yfinance/Benzinga feed drops whole firms and about a third of intermediate actions (96 chain breaks in 440 target actions); Phillip Securities' 11 Aug 2026 downgrade to Reduce ($158 from $136, analyst Paul Chew: the stock "trades at 30.9 times price-to-earnings versus its two-year historical plus-one standard deviation of 29.6 times") is not in the feed (Phillip has one row, Nov 2024); Weiss Ratings' 21 Aug Hold → Buy is not in the feed. Counts are lower bounds; the model thins counts by a capture rate of 0.85 | D §8 caveat 2; `data/processed/reverse_dcf/D/D_feed_chain_breaks.csv`; https://www.investing.com/news/analyst-ratings/phillip-securities-downgrades-airbnb-stock-rating-on-valuation-93CH-4851031 (WebFetch, verbatim in [sources/web_search_log.md](sources/web_search_log.md)) | 2026-08-11 / 2026-09-12 | 2026-09-17 | yes |
| 8 | S02 (revision 1): print branches accel 0.24 / flat 0.14 / decel-guide-ok 0.10 / decel-guide-below 0.52 with day-1 means +4.0 / −1.0 / −2.5 / −6.0 (sd 7.5) and drifts to 15 Dec −2.0 / −1.0 / −1.0 / −2.5; 15 Dec branch medians $170 / 163 / 161 / 152; unconditional median $162, P(≤150) 0.33. S01: P(day-1 ≤ −8%) 0.29, ≤ −5% 0.41 | `../close-15dec-2026/research-log.md` §5–6; `../day1-move-5nov/forecasts/2026-09-17-forecast.json`; `../close-15dec-2026/datasets/abnb_path_mixture.py` PARAMS | 2026-09-17 | 2026-09-17 | yes |
| 9 | Positioning tests (09 note, D §7): analyst actions outside prints produce abnormal returns indistinguishable from zero; Buy share vs forward 3-month excess return r 0.13 (p 0.30); 3-month change in Buy share vs forward 1-month return r −0.24 (contrarian-signed). The one memorable exception: the Morgan Stanley 7 Dec 2022 downgrade to Underweight, −5% on the day (InvestorPlace) | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 items 6, 9; R12 log claim 7; https://investorplace.com/2022/12/airbnb-abnb-stock-falls-5-percent-on-analyst-downgrade/ (search snippet) | 2026-09-06 / 2022-12-07 | 2026-09-17 | yes |
| 10 | Web (17 Sep, 1 WebSearch + 1 WebFetch): no rating change since Phillip (11 Aug, outside the feed) other than Morgan Stanley's 16 Sep re-initiation at Equal-weight (an upgrade to Hold, not a downgrade); Wedbush, Susquehanna, BMO, UBS raised targets after the 2Q26 print; the batch's neutral 72-hour check carried nothing on ratings | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 11 | Kalshi (KXABNB, 2026-09-17T08:27:05Z) carries Q3-2026 nights strikes only (>146m last 0.60, >148m 0.53); Polymarket (public-search "airbnb") only weekly / September price-hit ladders ("hit $164 low in September" 0.695, "$160 low" 0.42, "$156 low" 0.60 — internally inconsistent, thin); no market on ratings, targets or the December price | [sources/kalshi_KXABNB_open_20260917T082705Z.json](sources/kalshi_KXABNB_open_20260917T082705Z.json), [sources/polymarket_search_airbnb_20260917T082705Z.json](sources/polymarket_search_airbnb_20260917T082705Z.json) | 2026-09-17 | 2026-09-17 | no |
| 12 | Model (this log, `datasets/b11_model.py`, seed 20260917, n 400,000): P(≥3) **0.154**; mean count 1.17 (pre-print 0.33, post-print 0.84); P(count = 0/1/2/3/4/5+) 0.44 / 0.26 / 0.15 / 0.08 / 0.04 / 0.04; by branch: accel 0.04, flat 0.09, decel-guide-ok 0.13, decel-guide-below 0.23; P(branch | Yes): decel-below 0.77, accel 0.06; P(Yes | day-1 ≤ −8%) 0.30, ≤ −5% 0.26, in (−5, +5) 0.10, ≥ +5% 0.05; P(Yes | 15 Dec close ≤ $150) 0.24, ≥ $180 0.07; E[15 Dec close | Yes] $148.0 (median $145.7) vs unconditional $161.1 ($158.9); E[day-1 | Yes] −8.2% vs −2.5% | [datasets/b11_summary.json](datasets/b11_summary.json), [datasets/b11_sensitivity.csv](datasets/b11_sensitivity.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the feed pull and the computed tables (16–17 Sep, zero to one day old against an 89-day window); the D note is 5 days old. Within the 7-day cap.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`; finished logs R12 (log, JSON, `upgrade_base_rates.py`, `r12_model.py`, base-rate JSON), S04, S02, S01 (JSON), F03, R16, F01
2. [repo] `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5, §7, §8 (grep "downgrade"); `data/processed/reverse_dcf/D/` file list, `D_analyst_actions_2026-09-12.csv` (header, row count), `D_target_panel_daily.csv` (header), `D_print_revision_actions.csv` (down rows)
3. [yfinance, py -3.13] `Ticker('ABNB').upgrades_downgrades`, `.analyst_price_targets`, 5-day history — 2026-09-17T08:21:55Z, saved to `sources/`
4. [repo, pandas] every `Action == down` row in the feed with grade buckets (query 3's file)
5. [computed] `datasets/downgrade_base_rates.py` (90-day windows, price-conditioned windows, print-shaped windows, same-calendar windows, pool)
6. [repo] `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 (via R12 claim 7); `data/processed/q3nowcast/G/intra_quarter_commentary.csv` (8–11 Sep rows)
7. [Kalshi API] `markets?status=open&limit=100&series_ticker=KXABNB` — 2026-09-17T08:27:05Z, saved
8. [Polymarket public-search] airbnb — 2026-09-17T08:27:05Z, saved
9. [computed] `datasets/b11_model.py` (base + 21 sensitivities)
10. WebSearch: Airbnb ABNB analyst downgrade
11. WebFetch: investing.com "Phillip Securities downgrades Airbnb stock rating on valuation" (11 Aug 2026; verbatim in `sources/web_search_log.md`)
12. WebSearch: Airbnb news this week (batch final 72-hour neutral recency check — Icons collection, $250M Housing Accelerator, fake-listing purge; nothing on ratings or the stock's drivers; no change)

WebSearch calls charged to B11: 2 (queries 10, 12); batch total 4 of 15.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, yfinance/Benzinga upgrades-downgrades feed, 5 Nov 2026 print, Morgan Stanley, Phillip Securities, Keybanc, Evercore, Jefferies, Barclays, Truist, Wedbush

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Downgrades cluster on prints like upgrades do, so the R12 print-window rate transfers | discarded | only 20–25% of downgrades fall within 5–10 days of a print (upgrades 38–48%); downgrades follow the price with a lag (45% within 30 days after a print; 90-day windows after a 21-session fall ≤ −10% run at 1.18 vs 0.65) — the model puts the post-print count on the day-1 draw and the post-print price path, not on the print alone (claim 4) |
| Trailing-12-month rate (zero downgrades, 474 days) is the regime and P ≈ 0.02 | kept as the pre-print rate's lower sensitivity (0.13 overall) | the zero was earned on a stock that rose ~70% from the April 2025 low with four up prints; the question's window contains a print the team expects to decelerate, which is the regime in which the 2022–24 downgrades happened |
| 2023-style wave (five downgrades in Oct–Dec 2023 after a "moderate" Q4 guide and a −20% October) is the base case | kept inside the decel-guide-below branch (0.23) and the overdispersion (1.6; 2.5 as a sensitivity) | it is 1 of 5 same-calendar windows and 1 of 15 print-shaped windows since 2023; the 2023 wave needed a −3% day and a −20% month, which the S02 decel-below branch gives a median of −6% and −9% respectively |
| The Buy-share high (22 Buys, 59.5%) means more firms can downgrade | kept as a sensitivity (pool ×1.25 → 0.21), not in the base | the 2023 wave came from a 45% Buy-share tape; the pool is larger now, but the D note also shows the tape chasing the price up with no cut since 7 Aug, and a larger pool of Buys cut targets before they cut ratings (S04) |
| Feed misses real downgrades (Phillip Aug 2026) so the count should be inflated | reversed: the feed is the resolving object, so capture < 1 lowers P | the question resolves on the feed; a downgrade the feed drops does not count (capture 0.85 base; 0.70 → 0.11; 1.0 → 0.19) |
| Count `main` rows with target cuts as downgrades | discarded | the question says rating downgrades; target cuts are S04's object |
| Morgan Stanley re-initiation (UW → EW, 16 Sep) is a downgrade | discarded | it is an upgrade to Hold; not in the feed anyway |

## 5. Independent Estimates
- base_rate_estimate: 0.10 — regime-conditioned reference classes: 90-day P(≥3) 0.106 (2021+) / 0.082 (2023+) / 0.006 (2024+); print-shaped windows 0.087 (2 of 23) / 0.067 (2023+); same-calendar windows 0.20 (1 of 5); windows after a 21-session fall ≤ −10% 0.16; the trailing-12-month rate is zero. The four families span 0.01–0.20; taken at 0.10 because the window contains a print the team expects to decelerate (the 0.16 family) but the recent regime (0.006 since 2024, zero for 474 days) pulls the other way
- decomposition_estimate: 0.15 — joint simulation over the S02 branches (claim 12): pre-print NB(0.35 × exp(−3 × p1⁻)) + post-print NB(branch mean 0.15 / 0.5 / 0.7 / 1.1 × exp(−0.06 × day-1 surprise) × exp(−3 × r_post⁻)), overdispersion 1.6, capture 0.85; P(≥3) 0.154, P(≥2) 0.30
- anchor_estimate: 0.09 — no tradable market (claim 11); the repo's registered tape statistic is the D note's print-window record (claim 6: 15 downgrades across 23 print windows; "print-day cuts are rare"), which as a print-shaped window rate is 0.087 (claim 4)
- anchor_value: 0.09 (D note / feed print-window rate P(≥3), 2026-09-12 tape, recomputed 2026-09-17)
- final_estimate: **0.14** (credible interval 0.07–0.25)
- final_minus_anchor: +0.05. Inside 10 points, so flagged: the number is near the repo's own tape statistic, but it is not a haircut off it — the decomposition (0.15) conditions on the S02 branches (P(Yes | decel-guide-below) 0.23 vs 0.04 on an accelerating print) and on the price-fall mechanism the base rates show (claim 4), and the base rate (0.10) is the regime-conditioned average of four reference classes; the final sits between them, shaded below the decomposition for the 474-day drought and the feed's capture risk

## 6. Final Numbers
P(≥3 rating downgrades to Hold/Sell-equivalent in the feed, 17 Sep–15 Dec 2026) = **0.14**, credible interval **0.07–0.25**.
Count distribution (model): P(0) 0.44, P(1) 0.26, P(2) 0.15, P(3) 0.08, P(4) 0.04, P(5+) 0.04; mean 1.2. P(≥1) 0.56, P(≥2) 0.30.
By 5 Nov branch: accelerating print 0.04; flat 0.09; decelerating with the guide at/above Street 0.13; decelerating with the guide below Street (the team's base case) 0.23. Conditional on a day-1 move ≤ −8%: 0.30; ≤ −5%: 0.26; in (−5, +5): 0.10; ≥ +5%: 0.05. Conditional on a 15 Dec close ≤ $150: 0.24.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/b11_model.py` (`b11_sensitivity.csv`); base 0.154.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Pre-print mean 0.35 (2023+ off-print rate) | 0.20 (trailing-12m drought): 0.13; 0.55 (2021+ all-window rate): 0.19 |
| Post-print means by branch 0.15 / 0.5 / 0.7 / 1.1 | halved: 0.08; ×1.5: 0.24; flat 0.74 (all-print mean, no branch): 0.15 |
| Day-1 modulation 0.06 per point | none: 0.14; 0.12: 0.20 |
| Price-path modulation (k 3.0 pre and post) | none: 0.12; doubled: 0.20 |
| Overdispersion 1.6 | Poisson: 0.14; 2.5 (Nov-2023 clustering): 0.16 |
| Feed capture 0.85 | 1.0: 0.19; 0.70: 0.11 |
| Pool scale 1.0 | 1.25 (22 Buys at a series-high Buy share): 0.21 |
| P(accelerating print) 0.24 | 0.40 (Street-like): 0.13; 0.13 (nowcast centre 9.75): 0.17 |
| Day-1 branch means shrunk (S02) | unshrunk or market-neutral: 0.15 (the modulation is on the surprise, so the branch means cancel) |
| Joint bear-for-stock (accel 0.13, post ×1.5, pool 1.25, capture 1.0, overdispersion 2.5) | 0.38 |
| Joint bull-for-stock (accel 0.40, post halved, pre 0.20, capture 0.70) | 0.03 |

Pre-mortem ("it is 15 Dec 2026 and I was wrong"): (1) **Resolved Yes on a 2023-style wave** — a decelerating print, a "high single digits" or "moderate" bucket, a −10% day and a −15% month; four or five Buy-rated firms (the 22-firm pool) move to Hold within three weeks; priced at 0.23 in that branch and 0.30 conditional on a −8% day, with the joint-bear row at 0.38 — the memo's own base case is the case in which this resolves, so the unconditional 0.14 understates what the memo should expect if its print call is right. (2) **Resolved Yes before the print** — a further slide into October (the stock is already −8% over 21 sessions) draws valuation downgrades of the Phillip kind from feed firms; the price-conditioned base rate (0.16 after a ≤ −10% fall) is inside the pre-print term. (3) **Resolved No on a decelerating print because the tape cut targets, not ratings** — the 2Q24 precedent (−13.4% day-1, 19 target cuts, one rating downgrade): the S04 object moved, this one did not; this is why the decel-below branch is 0.23 and not 0.5. (4) **The feed dropped the actions** — three real downgrades, two captured; priced by capture 0.85. (5) **Resolved on a different vendor's list** (MarketBeat shows more firms): fenced by convention (1). Asymmetry: this is a bonus item; overstating it inflates the short case with a marker that carries no operating content, so the interval's top (0.25) is the joint-bear region and the memo should not lean on it.

## 8. Monitoring Calendar
Update procedure: recompute the downgrade count weekly from a fresh feed pull (`datasets/downgrade_base_rates.py` on the new file); the number is mechanical once two downgrades are in.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-19 | feed refresh | confirm no new `down` rows; if Morgan Stanley's 16 Sep row appears as `up` (UW → EW) it does not count |
| 2026-10-02 | prelim memo due | quote 0.14 (0.07–0.25); present as a marker of the decel-guide-below branch (P(branch | Yes) 0.77), not a standalone bonus |
| 2026-10-14 | end of price block 1 | close ≤ $155 (−8% from here): 0.19; ≥ $180: 0.11; any downgrade already in: 1 → 0.25, 2 → 0.45 |
| 2026-10-15 to 11-04 | Q3 preview season | valuation downgrades are the pre-print risk (Phillip form); each feed downgrade in raises P by ~0.10–0.20 |
| 2026-11-05/06 | print and reaction | day-1 ≤ −8%: 0.30 (0.45 if the bucket is "moderate"/mid-single); in (−5, +5): 0.10; ≥ +5%: 0.05 |
| 2026-11-25 | +13 sessions | downgrades lag the price by 2–5 weeks (Nov 2023: +11 to +28 sessions); if the close is ≤ $150 and 0–1 downgrades are in, hold ≈ 0.20; if 2 are in, ≥ 0.6 |
| 2026-12-15 | resolution | pull the feed after the close; count `down` rows to Hold/Sell dated 17 Sep–15 Dec, one per firm per day |

## 9. Impact
If B11 resolves Yes (three rating downgrades in the feed), deltas versus the memo's base case:

| Item | Delta if B11 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 (indirect: P(decel-guide-below | Yes) 0.77 vs 0.52 unconditional) | claim 12; the event carries no operating content of its own |
| 4Q26 nights (pts) | 0 (indirect) | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 (indirect) | — |
| FY27 revenue ($M) | 0 (indirect) | — |
| FY26 / FY27 adj. EBITDA margin (pp) | 0 / 0 | — |
| FY27 EPS ($) | 0 | — |
| Stock ($/share) | **−$13.1 as a marker** (E[15 Dec close | Yes] $148.0 vs $161.1 unconditional; median −$13.2) — this is the print branch the event labels, already counted in S01/S02/C01 and not additive; **direct effect of the downgrades themselves ≈ −$1.5** (judgement: three downgrade days at ~−0.3% abnormal each, per the 09 note's finding that analyst actions outside prints move the stock by nothing detectable; the Dec 2022 Morgan Stanley −5% day is the one exception in the record) | claim 12; claim 9 |
| **EV = P × impact** | marker: 0.14 × −$13.1 = −$1.8/share (not additive with S01/S02); **direct: 0.14 × −$1.5 ≈ −$0.2/share** | |
| Materiality | **Immaterial as an independent line** (direct EV under $1/share); a marker of the base-case branch only. The memo can drop "sell-side downgrades" as a separate bonus and mention it inside the base-case narrative ("a 2023-style wave of downgrades followed the last 'moderate' Q4 guide") | |

RESUME: the next agent (audit response) should re-run `datasets/downgrade_base_rates.py` then `datasets/b11_model.py` (deterministic, ~1 min) and attack three choices: (1) the post-print branch means (0.15 / 0.5 / 0.7 / 1.1), which rest on 20 downgrades in 23 print windows — an auditor may prefer the flat all-print mean (0.15 overall, unchanged) or the 2024+ regime (P(≥3) 0.006, which would take the number toward 0.08); (2) the capture rate 0.85 (the feed missed Phillip's Aug 2026 action; 1.0 gives 0.19); (3) the price-path modulation k = 3 (none gives 0.12, doubled 0.20). If S02 revision 2 moves P(accel) or the decel-below day-1 mean, rescale (each +0.10 on P(accel) ≈ −0.02 here). On 19 Sep confirm the feed carries no new `down` row.
