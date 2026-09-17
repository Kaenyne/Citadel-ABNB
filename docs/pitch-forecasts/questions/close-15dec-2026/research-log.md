# RESEARCH LOG

## 0. Metadata
- question_name: close-15dec-2026
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § S02)
- type: continuous
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
- batch: A07 (S02, S03, S04 share the model in `datasets/abnb_path_mixture.py`; this folder holds the master copies)

## 0b. Question (verbatim)
### Title
What will ABNB's closing price be on 15 Dec 2026?
### Resolution Criteria
Continuous (USD). Percentile table plus P(≤ $150), P(≤ $143), P(≥ $180).
### Fine Print
Reference price $167.51 (16 Sep 2026 close). Build from S01, the 20-day drift base rates, sell-side lag behaviour, the multiple-growth line and the options 12M distribution. Resolution date 15 Dec 2026.

Conventions adopted: (1) "closing price" = the Nasdaq official close of ABNB on Tuesday 15 Dec 2026 as reported by yfinance `Close` (ABNB pays no dividend, so adjusted and unadjusted closes coincide); (2) if 15 Dec were not a trading session, the last close before it; (3) thresholds are inclusive as written (≤ $150.00, ≤ $143.00, ≥ $180.00); (4) the forecast is unconditional on the 5 Nov print — the print is inside the mixture, not a conditioning event; (5) the S01 forecast JSON did not exist when this log reached the synthesis step (the `day1-move-5nov` folder held only option-chain pulls), so the day-1 mixture is built here from the same panel and reported in section 5; S01 (revision 1, committed while this batch ran) landed at mean −2.7%, median −2.9%, sd 9.5%, P(≤ −8%) 0.29, P(≤ −5%) 0.41, P(≥ +5%) 0.20, P(≥ +10%) 0.10 against this log's −2.5 / −2.7 / 8.6 / 0.27 / 0.39 / 0.19 / 0.07 — the same location, S01 about one point wider; the "event sd 9.0% in every branch" sensitivity row reproduces S01's width and moves P(≤ $150) by +0.01 and the median by −$0.1, inside the run-to-run noise, so the mixture was not re-parameterised; (6) a corporate action (takeover, split) that makes the 15 Dec close incomparable is carried at 0.5% and treated as resolving on the last comparable close.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | ABNB closed $167.51 on 16 Sep 2026 (15 Sep 168.32, 14 Sep 170.65, 11 Sep 170.19, 4 Sep 181.94); yfinance calendar lists the next earnings date as 5 Nov 2026; 3-month T-bill (^IRX) 3.97% | `sources/yfinance_abnb_history_2y_20260917T031221Z.csv`, `yfinance_calendar_20260917T031221Z.json`, `yfinance_irx_20260917T031221Z.csv` (yfinance capture 2026-09-17T03:12Z) | 2026-09-16 | 2026-09-17 | yes |
| 2 | Session counts (NYSE calendar, Thanksgiving 26 Nov, Christmas, New Year, MLK excluded): 16 Sep close → 5 Nov close 36 sessions; 6 Nov → 15 Dec 27 sessions; 16 Dec → 11 Feb 39; 6 Nov → 11 Feb 66; 16 Sep → 15 Dec 63; 16 Sep → 12 Feb 103. The model uses 35 pre-print sessions (one fewer; sd effect < 1.5% of the pre-print sd) | computed (`datasets/abnb_path_mixture.py`, pandas bdate_range) | 2026-09-17 | 2026-09-17 | no |
| 3 | 23 prints 4Q20–2Q26, raw close-to-close day-1: rms 8.9%, mean abs 7.1%, 13 up / 10 down, 48% at 7%+, 35% at 10%+, mean +1.2%; QQQ-excess rms 8.5%, 11 up / 12 down. Last eight raw: −8.7, +14.5, +1.0, −8.0, +0.3, +4.6, +0.7, +17.4 | `data/processed/abnb_earnings_reactions.csv`; `research/notes/reverse_dcf/B_options-implied.md` §7; `data/processed/reverse_dcf/B/B_print_base_rates.csv` | 2026-09-12 | 2026-09-17 | yes |
| 4 | Nights-acceleration sign rule (0.25pt dead band): post-2022 (1Q23–2Q26, n 14) decelerating prints closed up 0 of 8 on QQQ-excess (2 of 8 raw), mean −5.6% (raw −5.0%); accelerating 4 of 5, +6.0% (raw +6.7%); Fisher p 0.007 excess / 0.103 raw. 3Q22–2Q26 (n 16): decel 1 of 9, −3.6%; accel 4 of 6, +3.4%; Fisher p 0.089. Nothing pre-stated clears Holm; residual sd 6.9–8.8 pts; decelerating prints have closed −12.3% to +12.6%. Whole conditional expectation is the overnight gap (decel gap −5.3%, intraday +1.7% 9 of 9) | `research/notes/reverse_dcf/C_reaction-function.md` §1, §4; `data/processed/reverse_dcf/C/C_sorted_portfolios.csv`, `C_deadband_sensitivity.csv` | 2026-09-13 | 2026-09-17 | yes |
| 5 | Next-quarter revenue guide vs Street: +1.9% day-1 excess per 1% (n 16, HC1 t 2.2, LOO R² +0.15, fragile: drops to ≈0 without 2Q24 or 4Q22). Q4-guide-below-Street AND nights direction lower: −8.0% mean, −10.9% median (n 5: 3Q22 −13.4, 1Q23 −10.9, 2Q24 −13.4, 3Q23 −3.3, 1Q25 +1.0). Team base conditional on a decelerating print: S1 −4.0% (n 16) to −6.1% (n 14); unconditional on the nowcast band −1.9% to −3.5% | `C_reaction-function.md` §1 item 3, §7; `docs/pitch-forecasts/00_BRIEF.md` "Reaction base rates"; `deck/drafts/memo_v2_short_2026-09-16.md` scenario table | 2026-09-13 / 2026-09-16 | 2026-09-17 | yes |
| 6 | Post-print drift (QQQ-excess, day 1 excluded): +1..+20 sessions all 23 prints −3.7% mean, −3.7% median, 35% positive, t −2.16 p 0.042; after a day-1 up −7.1% (n 11, p 0.027); after a day-1 down −0.7% (n 12, p 0.72); from 2023 −2.3% (n 15, p 0.27, "fails the regime check"); +1..+60 all −6.5% (p 0.077). By acceleration (post-2022): decelerating prints 20-day excess −8.0% including day 1 (−5.9% day 1, so ≈ −2.1% drift), accelerating +1.3% including day 1 (+6.0%, so ≈ −4.7% drift). RED_TEAM lists the drift rule as dead as a tradable rule | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §4; `data/processed/overnight/09_earnings_drift_stats.csv`; `data/processed/overnight/05_reaction_by_accel.csv`; `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md` | 2026-09-06 | 2026-09-17 | yes |
| 7 | Options at the 16 Sep close, own Black-76 IVs from bid/ask mids on a parity forward (r 3.97%, quadratic smile, OTM only, filters as workstream B): ATM IV 2 Oct 32.7%, 16 Oct 32.3%, 30 Oct 34.0%, 20 Nov 38.9%, 18 Dec 37.3%, 15 Jan 37.2%, 19 Mar 38.0%, 17 Jun 38.8%; $170 straddles 16 Oct 7.4%, 20 Nov 13.0%, 18 Dec 14.9%, 15 Jan 17.0%, 19 Mar 21.5% of spot; implied 5 Nov event sd 9.1% (16 Oct vs 20 Nov pair), 9.4% (vs 18 Dec). The concurrent S01 agent's independent pull the same night gives 9.12% (pair) and 8.23% (LS, LOO 7.85–8.51) | `datasets/implied_term_structure_20260917T031221Z.csv`, `datasets/implied_dist_20260917T031221Z.json` (chain `sources/yfinance_option_chain_20260917T031221Z.csv`, 513 contracts, 10 expiries); `../day1-move-5nov/datasets/options_event_sd.csv` | 2026-09-16 | 2026-09-17 | yes |
| 8 | Options-implied distribution of the 15 Dec close (18 Dec expiry smile, T 0.247y, σ 37.3%, forward $169.16), risk-neutral: smile RND p5/10/25/50/75/90/95 = $115 / 128 / 147 / 167 / 188 / 209 / 224; P(≤143) 0.21, P(≤150) 0.28, P(≥180) 0.34; lognormal p50 $166.3 (P 0.21 / 0.29 / 0.33). Shifted by a 3% real-world drift the anchor median is $168.6 | `datasets/implied_dist_20260917T031221Z.json`; `datasets/final_blend.json` | 2026-09-16 | 2026-09-17 | yes |
| 9 | Workstream B (11 Sep chain, spot $170.19): event sd 9.5% central (8.5–10.5), 12M lognormal p25/p50/p75 $126/164/214 at 39.5% IV; realised print rms / historical implied crush 0.85; 25-delta risk reversal −3.5 vol pts, "the usual ABNB premium"; risk-neutral probabilities are not forecasts | `research/notes/reverse_dcf/B_options-implied.md` §1, §5, §9; `data/processed/reverse_dcf/B/B_dist_12m_percentiles.csv` | 2026-09-12 | 2026-09-17 | yes |
| 10 | Realised vol (log returns, annualised): 2023+ 37.8% incl. print days, 33.6% ex-print days; 2024+ 36.1 / 31.5; trailing 1y 34.1 / 30.0; 2023 42.2, 2024 33.8, 2025 37.1, 2026 YTD 38.0. Overlapping 63-session return windows 2023+ (n 866): mean +3.5%, sd 13.8, p5 −18.3, p25 −7.2, p50 +2.5, p75 +13.1, p95 +26.9; P(< −10.5%) 0.16, P(< −14.6%) 0.08, P(> +7.5%) 0.38. All history (n 1,384): sd 17.1, p5 −25.9, p95 +28.7; 0.25 / 0.18 / 0.36. Same-calendar analogues 16 Sep → 15 Dec: 2021 0.0%, 2022 −23.7%, 2023 +2.8%, 2024 +12.5%, 2025 +8.3% | computed from `datasets/abnb_close_merged_to_20260916.csv` (`data/processed/abnb_daily_close.csv` to 4 Sep + yfinance after) | 2026-09-16 | 2026-09-17 | yes |
| 11 | Team 3Q26 nights nowcast +9.5% (band 8.5–10.0, model path 9.9), reviews-index walk-forward RMSE 1.48pp vs naive 2.16; the C note's band shapes give P(accelerate ≥ 10.6%) 0.13 (centre 9.75, sd 0.75) to 0.21 (centre 9.9, sd 0.85); C02 log: P(3Q26 print ≥ 10.0%) 0.38, 9–10% 0.42, < 9% 0.20; Bloomberg MODL 3Q26 nights: 28 estimates, low 147m (+10.0%), mean 149m (+11.5%); the team's 146.8m sits below the lowest | `docs/q3nowcast/SYNTHESIS.md`; `C_reaction-function.md` §7; `../q4-nights-bucket/forecasts/2026-09-17-forecast.json` (conditioning block); `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` | 2026-09-11 to 2026-09-17 | 2026-09-17 | yes |
| 12 | C01 (revision 1): P(4Q26 revenue guide midpoint below the LSEG-family mean) 0.75 (CI 0.62–0.85); guide median $3,100M vs Street $3,161M; joint bull print moves it to 0.49. C02: (c) high single digits 0.39, (a) low double digits 0.21, (b) 0.19, (d) 0.17 | `../q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json`; `../q4-nights-bucket/forecasts/2026-09-17-forecast.json` | 2026-09-17 | 2026-09-17 | yes |
| 13 | Repricing ladder (joint solve, NTM-growth units): Street path prints $170.7–172.6 (+0.3 to +1.4%), management delivered $175.5 (+3.1%), team pnl bridge $168.7 (−0.9%), team pivot baseline $167.0 (−1.9%), ex-NA lap $164.4–166.2 (−2.3 to −3.4%); 1pt of FY27 nights ≈ $4.90/share (joint) or $1.50 (fixed multiple); multiple slope +0.48 turns of EV/EBITDA per point of NTM revenue growth (t 8.3 levels, +0.49 t 5.6 in 12m changes), one turn ≈ $9–10/share | `data/processed/reverse_dcf/E/E_repricing_ladder.csv`; `research/notes/2026-09-13_market-implied-model.md` §3, §10; `research/notes/overnight/12_valuation-multiple-regime.md` | 2026-09-13 | 2026-09-17 | yes |
| 14 | Memo scenario table (12-month horizon): thesis breaker 25% $180–190, base 45% $138–148 ($143 at ~7.5% NTM growth), short case 30% $115–130; probability-weighted $146; "the base case is two legs: a one-sigma day on 5 Nov, then the estimate cuts and multiple compression that follow a FY27 growth reset" | `deck/drafts/memo_v2_short_2026-09-16.md` "Scenarios" | 2026-09-16 | 2026-09-17 | no |
| 15 | Calendar-month excess returns vs QQQ since 2021 (n 5–6): Sep +3.1% (4/6), Oct −2.7% (1/5), Nov −5.1% (0/5, p 0.027; the Novembers: −0.9, −10.0, −4.0, −4.4, −6.0), Dec +0.6% (2/5), Jan +6.9% (4/6), Feb +7.7% (6/6, p 0.005); "a base rate to put on the calendar, not a proven effect" (54 seasonality tests) | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §5 | 2026-09-06 | 2026-09-17 | no |
| 16 | Sell-side: 32 live targets (feed convention), mean $181.81, median $182.5 on 12 Sep, unchanged on the 16 Sep re-pull (469 feed rows, none new); yfinance `targetMeanPrice` $182.98 (40 analysts). Morgan Stanley assumed coverage at Equal-weight, $170 on 16 Sep (from Underweight $125, 30 Jul) — not yet in the feed; in the feed convention it lifts the mean to $183.22. Targets follow price with a one-to-two-month lag (21-session betas 0.075 / 0.13 / 0.10) | `sources/yfinance_upgrades_downgrades_20260917T031221Z.csv`, `yfinance_analyst_price_targets_20260917T031221Z.json`; `sources/web_analyst_actions_capture_20260917.md`; `research/notes/reverse_dcf/D_sell-side-dispersion.md` §5 | 2026-09-16 | 2026-09-17 | no |
| 17 | Kalshi KXABNB Q3 2026 nights strikes (yes bid/ask, 2026-09-17T03:10Z): >144m 0.76/0.83, >146m 0.63/0.66, >148m 0.50/0.55, >150m 0.32/0.36 (implied median ≈ 148.3m, +11.0%; volume field null); no Kalshi ABNB price-level series (Financials category: KXABNB, KXABNBA only). Polymarket: only weekly and September price-hit ladders ("hit $180 (high) in September" 0.275, "hit $164 (low) in September" 0.76, "$160 low" 0.64, "$152 low" 0.52; 17 Sep up-or-down 0.515); nothing dated December or February | `sources/kalshi_KXABNB_open_20260917T031018Z.json`, `kalshi_series_financials_20260917T031018Z.json`, `sources/polymarket_search_*_20260917T031018Z.json` | 2026-09-17 | 2026-09-17 | no |
| 18 | Web recency (16–17 Sep): Morgan Stanley EW $170 initiation; Truist Hold $161 (10 Sep); Raymond James upgrade $200 and Baird $200 (8 Sep); $250M Housing Accelerator fund (14 Sep); ~60k fake listings removed; NYC 30-day-minimum enforcement item; Washington Post "World Cup hosts still waiting" (3 days old). No 4Q26 guidance preview, no management quarter-to-date remark, no macro shock | WebSearch results 17 Sep (queries 12, 14, 17 in the query log); https://247wallst.com/investing/2026/09/16/here-are-wednesdays-top-wall-street-analyst-research-calls-airbnb-booking-holdings-credicorp-dutch-bros-expedia-hartford-financial-services-group-meritage-homes-patchex-yum-brands/ ; https://www.thecerbatgem.com/2026/09/16/weekly-analysts-ratings-changes-for-airbnb-abnb.html | 2026-09-16 | 2026-09-17 | no |
| 19 | Monte Carlo (this log; `datasets/abnb_path_mixture.py`, seed 20260917, n 400,000): day-1 mixture mean −2.5%, sd 8.6%, P(≤ −8%) 0.27, P(≤ −5%) 0.39, P(≥ +5%) 0.19, P(≥ +10%) 0.07; 15 Dec decomposition percentiles $120 / 128 / 142 / 159 / 178 / 197 / 210, P(≤143) 0.27, P(≤150) 0.37, P(≥180) 0.23, log-sd 17.0%; by branch: accel median $170, flat $163, decel-guide-ok $161, decel-guide-below $152 (P(≤150) 0.46). Final CDF mixture 0.65 decomposition + 0.35 drift-shifted smile RND: $121 / 129 / 144 / 162 / 183 / 204 / 217; P(≤143) 0.24, P(≤150) 0.33, P(≥180) 0.28 | `datasets/mixture_base_run.json`, `sensitivity.csv`, `final_blend.json`, `S02_final_cdf.csv`, `S02_hist.csv` | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `references/continuous-questions.md`, `examples/example-research-log.md`, finished logs C01, C02, C03, C04, C09 (forecast JSONs)
2. [repo] `data/processed/abnb_earnings_reactions.csv`, `data/processed/overnight/05_reaction_by_accel.csv`, `data/processed/overnight/20_executable_returns.csv`, `data/processed/abnb_daily_close.csv`
3. [repo] `research/notes/reverse_dcf/C_reaction-function.md` (full), `B_options-implied.md` (full), `D_sell-side-dispersion.md` (full)
4. [repo] `research/notes/2026-09-13_market-implied-model.md` §3, §4, §7, §10; `data/processed/reverse_dcf/market/market_implied_by_price.csv`, `market_implied_cases.csv`; `data/processed/reverse_dcf/E/E_repricing_ladder.csv`
5. [repo] `research/notes/overnight/09_stock-behaviour-and-alpha.md` §4, §5; `data/processed/overnight/09_earnings_drift_stats.csv`; `research/notes/overnight/12_valuation-multiple-regime.md` (slope rows)
6. [repo] `deck/drafts/memo_v2_short_2026-09-16.md` scenario table; `research/notes/catalyst_calendar.md` (grep Feb)
7. [repo] `data/processed/reverse_dcf/D/D_target_panel_daily.csv`, `D_print_revisions.csv`, `D_chase_regression.csv`, `D_chase_asymmetry.csv`, `D_tape_percentiles.csv`, `D_live_targets_2026-09-12.csv`, `D_yf_analyst_price_targets.csv`; `data/processed/reverse_dcf/B/B_dist_12m_percentiles.csv`, `B_term_structure.csv`
8. [yfinance] ABNB 2y history, QQQ 2y, ^IRX, option expiries and chains (Oct 2026 – Jun 2027), analyst_price_targets, upgrades_downgrades, calendar, recommendations, info subset — captured 2026-09-17T03:10Z and T03:12Z (`datasets/pull_yfinance.py`)
9. [Kalshi API] series?category=Financials (grep ABNB / Airbnb); markets?series_ticker=KXABNB&status=open
10. [Polymarket public-search] airbnb; ABNB; Airbnb price; Airbnb December
11. [repo] `../day1-move-5nov/` (S01 in progress: `datasets/options_event_sd.csv`, `options_term_structure.csv`; no forecast JSON yet)
12. [WebSearch] Airbnb stock news this week
13. [WebSearch] Airbnb fourth quarter 2026 earnings date February 2027 (for S03; no 2027 date announced)
14. [WebSearch] Airbnb analyst price target cut September 2026 (for S04; found the Morgan Stanley 16 Sep initiation)
15. [WebFetch] 247wallst.com 16 Sep analyst-calls page (Morgan Stanley EW $170, verbatim)
16. [WebFetch] thecerbatgem.com weekly ratings changes 16 Sep (full action table)
17. [WebSearch] Airbnb news past 3 days (final 72-hour neutral recency check — result: fake-listing purge, NYC enforcement, World Cup host piece; nothing on the print, guidance or the stock's drivers; no change to the number)
18. [computed] own Black-76 IVs, event sd, smile RND at 15 Dec and 12 Feb (`datasets/implied_dist.py`); realised-vol and horizon-return base rates; seeded mixture and sensitivities (`abnb_path_mixture.py`); CDF blend (`final_blend.py`)

## 3. Leading Hypothesis Entities
Airbnb, ABNB, 5 Nov 2026 print, 3Q26 Nights and Seats Booked, 4Q26 revenue guide, LSEG consensus, options-implied event move, QQQ, Morgan Stanley, Bloomberg MODL

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Quote the memo's $143 base-case price as the 15 Dec median | discarded | the memo's $143 is a 12-month joint-solve price for the decelerating branch (claim 14); on 15 Dec that branch's median in the mixture is $152 and $143 is its 32nd percentile; unconditionally $143 is the 24th percentile |
| Use the options-implied distribution as the forecast (defer to the market) | kept as the anchor with 0.35 weight | it is risk-neutral (claims 8, 9), prices the print at zero mean, and carries no view on the sign of the 3Q26 nights print; the team holds a nowcast that beats naive (claim 11) and sits below every Street estimate — a nameable asymmetry that justifies a median ~4% below the market's |
| Use the 2023+ realised 63-day distribution (mean +3.5%, sd 13.8) as the base rate and centre on spot | kept as the base-rate estimate, low weight | 3.7 years in which the stock roughly doubled; the all-history sd (17.1) and the implied sd (18.5) bracket it; the base-rate estimate is used to check the width, not the centre |
| The 8–10 Sep fall already priced a decelerating print | discarded as a reason to remove the print asymmetry | B §6: the fall added 1–2 vol points across the curve and left the event variance unchanged; E's positioning card: the price still carries a 3Q26 nights rate of 10.6–11.2% in the units it is priced in (claim 13) |
| Post-print drift rule (−3.7% over +1..+20) as a full-strength input | kept at roughly half strength | RED_TEAM lists it as dead as a tradable rule and it fails the 2023+ regime check (p 0.27); the mixture carries −1.0 to −2.5% by branch, not −3.7% |
| November seasonal (−5.1% excess, 0/5) as an additional drift | discarded | it is the print (five Novembers each contain a Q3 print); adding it would double-count the day-1 mixture |
| Sell-side target cuts as a driver of the 15 Dec price | discarded as a price driver | D §5: targets follow the price with a 1–2 month lag, not the reverse; used in S04 only |
| A 6 Nov weekly straddle to isolate the print | not available | weeklies list only to 30 Oct on 16 Sep; the 20 Nov expiry still carries 10 post-print sessions; re-pull in the last week of September (monitoring calendar) |
| Corporate action / takeover before 15 Dec | tail 0.5% | no reporting, $100bn market cap, founder control; carried inside the tails, not as a component |

## 5. Independent Estimates
- base_rate_estimate: median $168.7, P(≤150) 0.25, P(≤143) 0.18, P(≥180) 0.36 — all-history 63-session return distribution (claim 10: median +0.7%, sd 17.1) applied to $167.51; the 2023+ window gives median $171.7, 0.16 / 0.08 / 0.38 and is treated as the bullish bound
- decomposition_estimate: median $158.9, P(≤150) 0.37, P(≤143) 0.27, P(≥180) 0.23, 5–95% $120–210 — seeded mixture (claim 19): 35-session pre-print diffusion at 29% background vol and 3% annual drift; day-1 mixture over four print branches (accel 0.24 / flat 0.14 / decel-guide-ok 0.10 / decel-guide-below 0.52 with conditional means +4.0 / −1.0 / −2.5 / −6.0%, within-branch sd 7.5%, i.e. the sign-rule and guide-below means shrunk 30–40% toward zero); branch drifts to 15 Dec −2.0 / −1.0 / −1.0 / −2.5% (half-strength post-print drift, claim 6); 27-session post-print diffusion. Unconditional day-1 mean −2.5%, sd 8.6% (options: 9.1%); 15 Dec log-sd 17.0% (options 18.5%, realised 2023+ 13.8%)
- anchor_estimate: median $168.6 (risk-neutral $167.3 + 3% annual drift over 0.25y), P(≤150) 0.28, P(≤143) 0.21, P(≥180) 0.34 — 18 Dec expiry smile RND at the 16 Sep close (claim 8), captured 2026-09-17T03:12Z
- anchor_value: median $167.3 (risk-neutral), P(≤ $150) 0.28, P(≤ $143) 0.21, P(≥ $180) 0.34
- final_estimate: CDF mixture 0.65 decomposition + 0.35 drift-shifted anchor: median $162; 5/10/25/50/75/90/95 = $121 / 129 / 144 / 162 / 183 / 204 / 217; P(≤150) 0.33, P(≤143) 0.24, P(≥180) 0.28
- final_minus_anchor: median −$6.5 (−3.9% vs the drift-shifted anchor; −$5.3 vs the risk-neutral $167.3); P(≤150) +0.05, P(≤143) +0.03, P(≥180) −0.06. All inside 10 points, so the divergence is modest by construction; it is not a token haircut: the independent decomposition lands at $159 (−5% vs the anchor) and is pulled a third of the way back because (i) the sign rule is a 14-print base rate that fails Holm (claim 4), (ii) the team's nowcast has been below the Street at every quarter since 2Q25 and management has not yet missed a nights guide to the downside in the sample (E card), (iii) the options market's width is the better-identified quantity. Named asymmetry for the remaining −3%: the team's 3Q26 nights nowcast (RMSE 1.48pp) sits below all 28 Street estimates, the Street's bar itself implies acceleration for only the fourth time in 16 prints, and decelerating prints have been sold 8 of 9 times since 3Q22 on the excess convention; the option-implied print distribution is symmetric by construction. Why three estimates disagree by up to 10 points on P(≤150): the base rate is centred on spot with no print view; the decomposition carries the team's print view; the anchor is risk-neutral and symmetric — the disagreement is the print view, which the weights make explicit

## 6. Final Numbers
| Percentile | USD |
|---|---|
| 5 | 121 |
| 10 | 129 |
| 25 | 144 |
| 50 | 162 |
| 75 | 183 |
| 90 | 204 |
| 95 | 217 |

Threshold probabilities: P(≤ $150) = **0.33**; P(≤ $143) = **0.24**; P(≥ $180) = **0.28**. Also P(≤ $125) 0.07, P(≥ $200) 0.12.
Mass below $100: 0.3% (needs a −40% move in 63 sessions; ABNB's worst 63-session return since 2023 is −18%, all-history p1 ≈ −33% in 2022); mass above $260: 0.4% (needs +55%; the 2Q26 print plus a rally reached +33% over 63 sessions).
Modes: the mixture is unimodal at the $5 bin level (peak $155–165) with a heavier left shoulder from the decel-guide-below branch (median $152); the branch medians are $170 (accel), $163 (flat), $161 (decel, guide at Street), $152 (decel, guide below Street).
Floor check: minimum density per $5 bin between $120 and $230 is 0.6% (at $230); no region inside $110–$240 would shock us.
Mean $164; log-sd of the final ≈ 17%; median return −3.3% from $167.51.
Conditional day-1 distribution for the team's base case (decel, guide below Street): mean −6.0%, sd 7.5%, P(≤ −8%) 0.39, P(≤ −5%) 0.55, P(≥ +5%) 0.07 — reported separately, not the headline.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| P(accelerating print) 0.24 (team band) | 0.40 (Street/Kalshi-leaning): decomposition median $161.6, P(≤150) 0.33, P(≥180) 0.26; 0.13 (nowcast centre 9.75, sd 0.75): $157.6, 0.39, 0.22 |
| Day-1 conditional means shrunk 30–40% toward zero | unshrunk (accel +6, decel-below −8): median $157.6, P(≤150) 0.39; market-neutral print (all means 0): $163.2, P(≤150) 0.30, P(≥180) 0.27 |
| Post-print drift at half strength | none: median $162.2, P(≤150) 0.32; doubled: $155.6, P(≤150) 0.42 |
| Background vol 29% | 33% (Oct ATM IV): P(≤150) 0.39, P(≥180) 0.25; 25%: 0.35 / 0.21 (decomposition rows) |
| Event sd 7.5% within branch (8.6% unconditional) | 9.0% within branch: P(≤150) 0.38, P(≥180) 0.24 |
| Real-world drift 3% annual | 0: median $157.7, P(≤150) 0.38 |
| Anchor weight 0.35 | 0 (pure decomposition): median $159, 0.37 / 0.27 / 0.23; 1 (pure market): $168.6, 0.28 / 0.21 / 0.34 |
| Spot $167.51 | every $1 of spot moves the median ≈ $0.97 and P(≤150) by ≈ −0.011 before the print; re-centre on any move > 3% (monitoring calendar) |

## 8. Monitoring Calendar
Update procedure: (a) re-centre the pre-print diffusion on the latest close; (b) keep branch weights unless a listed trigger fires; (c) after 5 Nov collapse the day-1 mixture to the realised close and re-run with the post-print block only (27 sessions less elapsed).
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-25 to 10-02 | 6 Nov weekly options list; September Inside Airbnb dumps refresh the reviews index | re-pull chains (`datasets/pull_yfinance.py`, `implied_dist.py`) for a clean print straddle; re-set P(accel) from the nowcast: each +0.5pp in the index centre ≈ +0.06 on P(accel), ≈ +$1.5 on the median |
| 2026-10-02 | prelim memo due | quote median $162, P(≤150) 0.33, P(≤143) 0.24, P(≥180) 0.28; state that $143 is the 24th percentile on 15 Dec, not the base case |
| 2026-10-13 | EEA/CH single-fee migration deadline | no direct price action; feeds C01 (guide) — if C01 moves by > 0.05, re-weight the decel-guide-below branch one-for-one |
| 2026-10-30 | EXPE / BKNG 3Q prints (EXPE reads through) | EXPE guides Q4 room nights at or above its Q3 rate: shift 0.03 from decel-below to accel (median +$0.8); a ≥ 2pt deceleration guide: the reverse |
| 2026-11-04 | record the Street 4Q26 revenue mean and the 5 Nov close; re-pull the 6 Nov straddle | re-centre; if the implied event sd is outside 8–11%, rescale within-branch sd |
| 2026-11-05/06 | 3Q26 print and reaction session | replace the mixture with the realised close: reference values on 6 Nov close $150 → median ≈ $148, P(≤150) ≈ 0.55; $160 → $158, 0.34; $175 → $173, 0.15 (27 sessions at 29% vol, branch drift as realised) |
| 2026-11-20, 12-15 | 20 Nov expiry; resolution close | weekly re-centre in the last month; resolve on the 15 Dec Nasdaq close |
| any date | market shock (QQQ −8% in a week) or ABNB news moving the stock > 8% ex-print | re-centre; widen background vol to 35% for the remaining window |
