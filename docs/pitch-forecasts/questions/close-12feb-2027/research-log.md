# RESEARCH LOG

## 0. Metadata
- question_name: close-12feb-2027
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § S03)
- type: continuous
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-02-12
- resolution_date: 2027-02-12
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A07 (shares the model with S02; master scripts in `../close-15dec-2026/datasets/`, wrapper `datasets/run.py` here)

## 0b. Question (verbatim)
### Title
What will ABNB's closing price be on the first trading session after the 4Q26 print (expected 12 Feb 2027)?
### Resolution Criteria
Continuous (USD). Percentile table plus P(≤ $150), P(≤ $143), P(≥ $180).
### Fine Print
If the print date moves, the first session after the actual 4Q26 release. Resolution date ~12 Feb 2027.

Conventions adopted: (1) the 4Q26 release is expected after the close on Thursday 11 Feb 2027 (Airbnb's Q4 releases: 25 Feb 2021, 15 Feb 2022, 14 Feb 2023, 13 Feb 2024, 13 Feb 2025, 12 Feb 2026, all after the close), so the resolving session is Friday 12 Feb 2027; no 2027 date has been announced (query 13); (2) if the release is on another date, the first full session after it; if it were before the open, that day's close; (3) "closing price" = the Nasdaq official close via yfinance `Close`; (4) unconditional: both the 5 Nov and the Feb print are inside the mixture; (5) the S01 forecast JSON did not exist at synthesis time; the 5 Nov day-1 mixture is the one built in the S02 log (S01 revision 1 landed during the run at mean −2.7%, sd 9.5%, P(≤ −8%) 0.29 — the same location, one point wider; see the S02 log fine print, no re-parameterisation); (6) the horizon is 103 sessions (16 Sep → 12 Feb), the model uses 35 + 27 + 39 + 1 = 102.

## 1. Claims Ledger
Claims 1–19 of `../close-15dec-2026/research-log.md` are reused unchanged (spot, session counts, reaction panel, sign rule, guide-vs-Street, post-print drift, options at the 16 Sep close, workstream B, realised vol, nowcast and C01/C02, repricing ladder, memo, seasonality, sell-side, Kalshi/Polymarket, web recency, the Monte Carlo). Additional and S03-specific claims:
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 20 | Q4 (February) print day-1 raw returns: 4Q20 +13.3, 4Q21 +3.6, 4Q22 +13.4, 4Q23 −1.7, 4Q24 +14.4, 4Q25 +4.6 — **5 of 6 positive**, mean +7.9%, median +9.0% (excess: +12.9, +3.7, +12.6, −2.8, +14.0, +4.4). The brief's "February Q4 prints positive 6 of 6" is the calendar-February excess return (09 note §5: Feb +7.7%, 6/6, p 0.005), not the day-1 count; the 4Q23 print (14 Feb 2024) closed −1.7% raw. 20-day returns after those prints: −3.2, −13.5, −6.0, +9.2, −12.9, +8.9 | `data/processed/abnb_earnings_reactions.csv`; `research/notes/overnight/09_stock-behaviour-and-alpha.md` §5 | 2026-09-06 | 2026-09-17 | yes |
| 21 | Options-implied distribution of the 12 Feb 2027 close (total-variance interpolation between the 15 Jan 2027 and 19 Mar 2027 expiries, T 0.408y, σ 37.7%, forward $170.25), risk-neutral: smile RND p5/10/25/50/75/90/95 = $106 / 119 / 141 / 167 / 196 / 224 / 241; P(≤143) 0.27, P(≤150) 0.33, P(≥180) 0.38 (lognormal 0.27 / 0.34 / 0.36). The 19 Mar expiry carries two prints (5 Nov, ~11 Feb); the 15 Jan expiry one; the interpolated variance therefore contains roughly 1.4 print events, close to the 2 the horizon actually holds — the anchor is if anything a touch narrow. Drift-shifted median $169.5 | `../close-15dec-2026/datasets/implied_dist_20260917T031221Z.json` (copied to `datasets/`); `datasets/final_blend.json` | 2026-09-16 | 2026-09-17 | yes |
| 22 | 103-session return windows: 2023+ (n 826) mean +4.7%, sd 15.3, p5 −19.9, p25 −4.7, p50 +3.2, p75 +13.2, p95 +32.5; P(< −10.5%) 0.13, P(< −14.6%) 0.07, P(> +7.5%) 0.38. All history (n 1,344): sd 18.0, p5 −30.7, p95 +29.8; 0.25 / 0.19 / 0.34. Same-calendar analogues 16 Sep → 12 Feb: 2021/22 +0.9%, 2022/23 −2.0%, 2023/24 +7.9%, 2024/25 +19.5%, 2025/26 −4.7% | computed from `../close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv` | 2026-09-16 | 2026-09-17 | yes |
| 23 | 1Q26 revenue $2,678M vs 1Q25 $2,272M = +17.9% (the comp the 1Q27 revenue guide is set against); 1Q26 nights +9.2%; F02's kernel range for the 1Q27 guide midpoint $2,930–2,990M (+9.4 to +11.6%); the Q4 print carries the FY margin sentence (F03) and the 1Q nights descriptor (F01); every Q4 print since 2022 has guided a decelerating Q1 on a hard comp (C note §5: "decelerating guide at a Q4 print: +7.1% mean, n 4") | `docs/pitch-forecasts/QUESTIONS.md` § F01–F03; `data/processed/overnight/02_guidance_ledger.csv`; `research/notes/reverse_dcf/C_reaction-function.md` §5 | 2026-09-16 | 2026-09-17 | yes |
| 24 | Jan/Feb seasonal: Jan +6.9% excess (4/6, p 0.23), Feb +7.7% (6/6, p 0.005); "the seasonal is the summer-booking-season expectations cycle, in which ABNB is bid into the February FY guide"; n 6, 54 tests run | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §5 | 2026-09-06 | 2026-09-17 | yes |
| 25 | Monte Carlo S03 block (`abnb_path_mixture.py`): 16 Dec → 11 Feb branch drifts accel +1.0 / flat −1.0 / decel-ok −1.0 / decel-below −3.0%, plus +2.0% Jan/Feb seasonal in every branch (75% shrink of the n-6 excess), 39-session diffusion at 29%; Feb day-1 mean +4.0 / +2.5 / +2.5 / +2.0% by 5 Nov branch (the +7.9% n-6 base rate shrunk ~65%), sd 8.0–8.5%. Outputs: Feb day-1 unconditional mean +2.6%, P(≥ +5%) 0.39, P(< 0) 0.38; decomposition percentiles $112 / 122 / 140 / 163 / 190 / 217 / 236, P(≤143) 0.28, P(≤150) 0.36, P(≥180) 0.33, log-sd 22.6%; branch medians accel $181, flat $168, decel-ok $166, decel-below $153. Final CDF mixture (0.65 / 0.35): $113 / 123 / 141 / 165 / 193 / 222 / 242; P(≤143) 0.27, P(≤150) 0.34, P(≥180) 0.35 | `datasets/mixture_base_run.json`, `sensitivity.csv`, `final_blend.json`, `S03_final_cdf.csv`, `S03_hist.csv` | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
Queries 1–18 of `../close-15dec-2026/research-log.md` § 2 were run once for the batch; the S03-specific items are query 13 ([WebSearch] Airbnb fourth quarter 2026 earnings date February 2027 — no 2027 date announced; the 4Q25 release was 12 Feb 2026 after the close), the Jan/Mar option-chain interpolation in `implied_dist.py`, the 103-session base rates, and query 17 (the final 72-hour recency check: nothing on the Feb print or FY27 guidance; no change to the number).

## 3. Leading Hypothesis Entities
Airbnb, ABNB, 4Q26 print, 1Q27 revenue guide, FY27 margin guide, 5 Nov 2026 print, February seasonal, options-implied distribution, Morgan Stanley

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Carry the "Q4 prints positive 6 of 6" base rate at full strength (+7.9% mean day-1) | discarded; shrunk to +2 to +4% by branch | the day-1 count is 5 of 6 (claim 20), n 6, and the Q4 print's positive history coincides with three reopening/first-profit years; conditional on a 5 Nov deceleration the Feb bar resets to the guide (E card: "the bar is the guide") so the surprise content is smaller |
| Feb print reaction is independent of the 5 Nov branch | discarded | the 4Q26 nights print and the 1Q27 guide are set against the 5 Nov guide; after a decel-guide-below November the Q4 nights bar is lower and a further deceleration guide is expected, so the Feb mean is lower (+2.0%) and the pre-print drift is negative (−3.0%: the memo's "estimate cuts and multiple compression" leg, carried at half strength) |
| Use the memo's 12-month scenario prices ($180–190 / $138–148 / $115–130) as the 12 Feb branch centres | discarded | they are 12-month joint-solve values (memo table); the model's branch medians at 12 Feb ($181 / $168 / $166 / $153) come from the same repricing ladder applied over five months, and the short-case $115–130 is the model's 10th percentile, not a branch centre |
| The January "bid into the February guide" seasonal at full strength (+14.6% Jan+Feb excess) | kept at +2% | n 6, 54 tests; a quarter of the raw excess is carried |
| Options interpolation between Jan and Mar expiries as the anchor | kept | the only listed expiries around 12 Feb; the interpolated variance holds ~1.4 print events against 2 in the horizon, so the anchor is slightly narrow; noted, not corrected |
| Corporate action / takeover before Feb | tail 0.7% | inside the tails |

## 5. Independent Estimates
- base_rate_estimate: median $167.8, P(≤150) 0.25, P(≤143) 0.19, P(≥180) 0.34 — all-history 103-session return distribution (claim 22) on $167.51; the 2023+ window (median +3.2%, sd 15.3) gives $172.9, 0.13 / 0.07 / 0.38 and is the bullish bound
- decomposition_estimate: median $162.8, P(≤150) 0.36, P(≤143) 0.28, P(≥180) 0.33, 5–95% $112–236 — the S02 mixture extended by the 16 Dec → 11 Feb block (branch drift + seasonal + 39-session diffusion) and the Feb day-1 event (claim 25); Feb day-1 unconditional mean +2.6%, sd ≈ 8.3%
- anchor_estimate: median $169.5 (risk-neutral $167.4 + 3% annual drift over 0.41y), P(≤150) 0.33, P(≤143) 0.27, P(≥180) 0.38 — Jan/Mar-interpolated smile RND at the 16 Sep close (claim 21), captured 2026-09-17T03:12Z
- anchor_value: median $167.4 (risk-neutral), P(≤ $150) 0.33, P(≤ $143) 0.27, P(≥ $180) 0.38
- final_estimate: CDF mixture 0.65 decomposition + 0.35 drift-shifted anchor: median $165; 5/10/25/50/75/90/95 = $113 / 123 / 141 / 165 / 193 / 222 / 242; P(≤150) 0.34, P(≤143) 0.27, P(≥180) 0.35
- final_minus_anchor: median −$4.4 (−2.6%); P(≤150) +0.01, P(≤143) 0.00, P(≥180) −0.03. NOT_INDEPENDENTLY_DERIVED by the 10-point rule on the thresholds; the independent decomposition is shown above and lands $6.7 below the anchor on the median, and the two agree on the thresholds because two opposite asymmetries roughly cancel by February: the team's negative 5 Nov view (median −$8 by 15 Dec) against the positive February print history and Jan/Feb seasonal (+$5 to +6 by 12 Feb). The market's distribution is symmetric on both and wider only because it is risk-neutral. The named asymmetry that survives is the sign of the 5 Nov print, worth about −3% on the median; the February print itself we do not claim to call

## 6. Final Numbers
| Percentile | USD |
|---|---|
| 5 | 113 |
| 10 | 123 |
| 25 | 141 |
| 50 | 165 |
| 75 | 193 |
| 90 | 222 |
| 95 | 242 |

Threshold probabilities: P(≤ $150) = **0.34**; P(≤ $143) = **0.27**; P(≥ $180) = **0.35**. Also P(≤ $125) 0.12, P(≥ $200) 0.20.
Mass below $100: 1.5% (a −40% move over 103 sessions has happened once in the series, Sep–Dec 2022 −24% plus the May 2023 leg); mass above $260: 2.5% (+55%; Nov 2024–Feb 2025 delivered +45% over a similar window).
Modes: unimodal at the $5 bin level (peak $150–170) with a fat left shoulder from the decel-guide-below branch (median $153) and a long right tail from the accel branch plus a positive Feb print (median $181).
Floor check: minimum density per $5 bin between $120 and $230 is 1.2%; nothing inside $100–$250 would shock us.
Mean $169; log-sd of the final ≈ 22%; median return −1.5% from $167.51.
Feb-print day-1 distribution (own event, all branches): mean +2.6%, P(≥ +5%) 0.39, P(< 0) 0.38 (feeds R14); conditional on the team's base 5 Nov branch: mean +2.0%.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Feb day-1 means +2 to +4% by branch (shrunk) | raw n-6 base rate +7.9% in every branch: decomposition median $171.3, P(≤150) 0.28, P(≥180) 0.41; zero in every branch: $158.7, 0.40, 0.29 |
| Jan/Feb seasonal +2% | none: median $159.6, P(≤150) 0.39, P(≥180) 0.30 |
| Post-print drifts (Nov branch to Feb) at half strength | none: median $168.9, P(≤150) 0.30, P(≥180) 0.39; doubled: $156.9, 0.43, 0.28 |
| P(accelerating 5 Nov print) 0.24 | 0.40: median $167.1, P(≤150) 0.32, P(≥180) 0.37; 0.13: $160.7, 0.38, 0.31 |
| 5 Nov day-1 means shrunk 30–40% | market-neutral: $167.3, 0.31, 0.37; unshrunk: $161.5, 0.38, 0.32 |
| Background vol 29% | 33%: P(≤150) 0.38, P(≥180) 0.34; 25%: 0.34 / 0.32 |
| Anchor weight 0.35 | 0: $163, 0.36 / 0.28 / 0.33; 1: $169.5, 0.33 / 0.27 / 0.38 |
| Print date 11 Feb after close | a release a week either side changes nothing material (< 0.3 on the log-sd) |

## 8. Monitoring Calendar
Update procedure: as S02 (re-centre, keep branch weights, collapse the 5 Nov mixture on 6 Nov), then re-run with the Feb block only after 15 Dec; after the 4Q26 date is announced, fix the resolution session.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-25 to 10-02 | 6 Nov weekly lists; September dumps refresh the nowcast | re-set P(accel) (each +0.5pp in the index centre ≈ +$2 on the 12 Feb median) |
| 2026-10-02 | prelim memo due | quote median $165, P(≤150) 0.34, P(≤143) 0.27, P(≥180) 0.35; the memo's $138–148 is the 20th–33rd percentile of the 12 Feb close |
| 2026-11-06 | 5 Nov reaction close | collapse the mixture: reference 6 Nov close $150 → 12 Feb median ≈ $150, P(≤150) ≈ 0.50, P(≥180) ≈ 0.14; $160 → $161, 0.38, 0.22; $175 → $178, 0.20, 0.46 (branch drifts and Feb event as realised branch) |
| 2026-12-15 | S02 resolves | re-run from the 15 Dec close with the Feb block only (39 sessions + event): P(≥180) from $160 ≈ 0.22 |
| mid-Jan 2027 | Airbnb announces the 4Q26 date; 15 Jan expiry rolls; Q4 print previews | fix the resolution session; re-pull the Feb weekly straddle for the Feb event sd (replace 8.0–8.5%) |
| 2027-01-25 | STR 4Q26 US RevPAR (R11/B15); NTTO December arrivals | if RevPAR ≤ +1%: shift 0.03 into the lower Feb branch means (−0.5% on the Feb day-1 mean) |
| ~2027-02-11/12 | 4Q26 print and reaction session | resolve on the close of the first session after the release |
