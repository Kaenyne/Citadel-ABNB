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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A07 (shares the model with S02; master scripts in `../close-15dec-2026/datasets/` (`abnb_path_mixture_v2.py`, `implied_dist_v2.py`, `final_blend_v2.py`), wrapper `datasets/run_v2.py` here; the measured pre-release window is `datasets/dec_to_prerelease_window.py`; revision-1 files untouched)

## 0b. Question (verbatim)
### Title
What will ABNB's closing price be on the first trading session after the 4Q26 print (expected 12 Feb 2027)?
### Resolution Criteria
Continuous (USD). Percentile table plus P(≤ $150), P(≤ $143), P(≥ $180).
### Fine Print
If the print date moves, the first session after the actual 4Q26 release. Resolution date ~12 Feb 2027.

Conventions adopted: (1) the 4Q26 release is expected after the close on Thursday 11 Feb 2027 (Airbnb's Q4 releases: 25 Feb 2021, 15 Feb 2022, 14 Feb 2023, 13 Feb 2024, 13 Feb 2025, 12 Feb 2026, all after the close), so the resolving session is Friday 12 Feb 2027; no 2027 date has been announced (query 13); (2) if the release is on another date, the first full session after it; if it were before the open, that day's close; (3) "closing price" = the Nasdaq official close via yfinance `Close`; (4) unconditional: both the 5 Nov and the Feb print are inside the mixture; (5) the 5 Nov day-1 mixture is the S02 revision-2 mixture (adopted print-state weights 0.32 / 0.10 / 0.13 / 0.45, unconditional sd 9.5% matched to S01; see the S02 log conventions (5)); the February event is R14's distribution (P(≥ +5%) 0.30, mean ≈ +0.8%, sd 9.1) mapped onto the 5 Nov branches (section 5); (6) the horizon is 103 sessions (16 Sep → 12 Feb), and the model now uses 36 + 1 + 26 + 39 + 1 = 103 (A07-15; revision 1 had 35 + 27 and called itself one session short — the prose omitted the 5 Nov session, the total was already right); (7) a delisting before the resolution session is an undefined resolution case, not modelled (S02 convention (6)).

## 1. Claims Ledger
Claims 1–19 and 34–35 of `../close-15dec-2026/research-log.md` (revision 2) are reused (spot, session counts, reaction panel, sign rule, guide-vs-Street, rebased post-print drift, options at the 16 Sep close, the mixture-RND anchor method, workstream B, realised vol and corrected tails, nowcast provenance and adopted print-state weights, C01/C02, repricing ladder as a cross-check, memo, seasonality, sell-side, Kalshi/Polymarket, web recency, the Monte Carlo, R14/R16/F02/R12, the Astra comparison). Additional and S03-specific claims:
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 20 | Q4 (February) print day-1 raw returns: 4Q20 +13.3, 4Q21 +3.6, 4Q22 +13.4, 4Q23 −1.7, 4Q24 +14.4, 4Q25 +4.6 — **5 of 6 positive, 3 of 6 ≥ +5%**, mean +7.9%, median +9.0%, sd 6.7 (excess: +12.9, +3.7, +12.6, −2.8, +14.0, +4.4). The brief's "February Q4 prints positive 6 of 6" is the calendar-February excess return (09 note §5: Feb +7.7%, 6/6, p 0.005), not the day-1 count; the 4Q23 print (14 Feb 2024) closed −1.7% raw. 20-day returns after those prints: −3.2, −13.5, −6.0, +9.2, −12.9, +8.9. R14 conditions the February event on the 4Q26 print sign and the 1Q27 guide-vs-Street and lands at P(≥ +5%) 0.30, mean +0.8% (claim 34) | `data/processed/abnb_earnings_reactions.csv`; `research/notes/overnight/09_stock-behaviour-and-alpha.md` §5; `../risk-feb-print-up-day/forecasts/2026-09-17-forecast.json` | 2026-09-06 / 2026-09-17 | 2026-09-17 | yes |
| 21 | Options-implied distribution of the 12 Feb 2027 close, revision 2: two-lognormal mixture RNDs fitted per expiry (15 Jan: w 0.92, F₁ $168.0 σ₁ 38.3%, F₂ $193.2 σ₂ 5% (bound), rmse $0.31; 19 Mar: w 0.87, F₁ $168.7 σ₁ 40.9%, F₂ $190.9 σ₂ 10.4%, rmse $0.17), log-quantile interpolation at the calendar weight w = 28/63 = 0.444 (log-sd 24.3%), **plus the (1 − w) = 55.6% of a 9.5% February event that the interpolation omits** (A07-11: the 19 Mar expiry carries both prints and the 15 Jan expiry one, so total-variance interpolation prices only 44% of the February event although the 12 Feb close is after it; on the revision-1 lognormal the correction is log-sd 24.06% → 25.08%, equivalent annual IV 37.65% → 39.25%). Risk-neutral after the correction: p5/10/25/50/75/90/95 = $107 / 118 / 139 / 168 / 196 / 225 / 246, P(≤143) 0.279, P(≤150) 0.340, P(≥180) 0.389, log-sd 25.2%, P(<100) 2.8%. Real-world (× exp(3% × 0.408y)): median **$169.9**, P(≤143) 0.265, P(≤150) 0.324, P(≥180) 0.409. Revision 1 (superseded): smile RND $106 / 119 / 141 / 167 / 196 / 224 / 241, 0.27 / 0.33 / 0.38, with 0.47% negative density clipped and a lognormal substituted in the blend (A07-03/04) | `../close-15dec-2026/datasets/implied_dist_v2.py` → `datasets/implied_dist_v2.json`, `anchor_cdf_v2.csv`; `datasets/final_blend_v2.json` | 2026-09-16 | 2026-09-17 | yes |
| 22 | 103-session return windows: 2023+ (n 826) mean +4.7%, sd 15.3, p5 −19.9, p25 −4.7, p50 +3.2, p75 +13.2, p95 +32.5; P(< −10.5%) 0.13, P(< −14.6%) 0.07, P(> +7.5%) 0.38. All history (n 1,344): mean +0.5%, sd 18.0, median +0.19%, p1 −39.4, p5 −30.7, p95 +29.8; 0.25 / 0.19 / 0.34. **Tails corrected (A07-13):** worst 103-session return −47.7% (window starting 16 Feb 2022); **11 overlapping** windows ≤ −40% (9 at ≤ −40.3%), all starting 13 Jan–17 Feb 2022, one episode; 2023+ worst −31.7% (14 Mar 2024); one window ≥ +55% (+55.0%, starting 27 Mar 2026, the run into the 2Q26 print). Revision 1's "a −40% move has happened once, Sep–Dec 2022 plus the May 2023 leg" misidentified the episode. Same-calendar analogues 16 Sep → 12 Feb: 2021/22 +0.9%, 2022/23 −2.0%, 2023/24 +7.9%, 2024/25 +19.5%, 2025/26 −4.7% | computed from `../close-15dec-2026/datasets/abnb_close_merged_to_20260916.csv`; `audits/A07-reproduce.py` §1 | 2026-09-16 | 2026-09-17 | yes |
| 23 | 1Q26 revenue $2,678M vs 1Q25 $2,272M = +17.9% (the comp the 1Q27 revenue guide is set against); 1Q26 nights +9.2%; F02: 1Q27 revenue guide median +9.4% (p25 7.0, p75 12.0) vs LSEG +12.4%, gap-adjusted +11.0%, P(guide ≥ Street) 0.33 per R14; R16: 4Q26 nights print mean ~8.3%, P(≥ Street 9.93%) 0.27; the Q4 print carries the FY margin sentence (F03) and the 1Q nights descriptor (F01); every Q4 print since 2022 has guided a decelerating Q1 on a hard comp (C note §5: "decelerating guide at a Q4 print: +7.1% mean, n 4") | `docs/pitch-forecasts/QUESTIONS.md` § F01–F03; `../q1-27-revenue-guide-growth/forecasts/2026-09-17-forecast.json`; `../risk-q4-nights-print-meets-street/forecasts/2026-09-17-forecast.json`; `data/processed/overnight/02_guidance_ledger.csv`; `research/notes/reverse_dcf/C_reaction-function.md` §5 | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes |
| 24 | **Measured 15 Dec → pre-release window** (close on 15 Dec or the last session before it → close of the session before the Q4 reaction day, 39–48 sessions; A07-12 replaces the calendar Jan + Feb seasonal, which contained the reaction day and the post-release sessions): excess vs QQQ 2020/21 +43.9 (IPO window, excluded), 2021/22 +17.3, 2022/23 +22.3, 2023/24 −3.1, 2024/25 +6.5, 2025/26 −10.5; **ex-IPO mean +6.5% (raw +7.8%), median +6.5, sd 12.3, 3 of 5 positive**, t ≈ 1.2. Revision 1 carried +2% as "a quarter of Jan + Feb +14.6%" (it retained 13.8%, not 25%, and double-counted the reaction day); revision 2 carries **+1.5% = 25% of the measured ex-IPO excess**, judgment, with the "none" row as the alternative | `datasets/dec_to_prerelease_window.py` → `dec_to_prerelease_window.csv`, `.json` (from `data/processed/overnight/09_prices_daily.csv`, `abnb_earnings_reactions.csv`) | 2026-09-17 | 2026-09-17 | yes |
| 25 | Monte Carlo S03 block, revision 2 (`abnb_path_mixture_v2.py`): 15 Dec → 11 Feb branch drifts accel −0.5 / flat −0.5 / decel-ok −0.5 / decel-below −2.0% (the memo's estimate-cut leg at about half strength on the base branch; the rebased drift evidence in claim 6 does not support a persistent negative drift on the other branches), plus the +1.5% pre-release window in every branch (claim 24), 39-session diffusion at 30% and 6.97% total drift; Feb day-1 means +2.5 / +1.0 / +0.5 / −0.5% by 5 Nov branch (R14's +0.8% unconditional mean and its accel-vs-decel ordering), sd 9.0. Outputs: Feb day-1 unconditional mean +0.7%, sd 9.1, P(≥ +5%) 0.32, P(< 0) 0.47 (R14: 0.30 / 0.51); decomposition percentiles $111 / 121 / 140 / 165 / 193 / 222 / 242, P(≤143) 0.27, P(≤150) 0.35, P(≥180) 0.35, log-sd 23.6%; branch medians accel $178, flat $169, decel-ok $166, decel-below $154 (P(≤150) 0.45). Final CDF mixture (0.65 / 0.35 with the real-world mixture-RND anchor): **$110 / 121 / 141 / 166 / 195 / 224 / 244; P(≤143) 0.27, P(≤150) 0.34, P(≥180) 0.37**; mean $170, log-sd 24.1%; P(<100) 2.1%, P(>260) 2.9%. Revision 1 (superseded): decomposition $163, final $165, 0.27 / 0.34 / 0.35 | `datasets/mixture_base_run_v2.json`, `sensitivity_v2.csv`, `final_blend_v2.json`, `S03_final_cdf_v2.csv`, `S03_hist_v2.csv` | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
Queries 1–23 of `../close-15dec-2026/research-log.md` § 2 were run once for the batch; the S03-specific items are query 13 ([WebSearch] Airbnb fourth quarter 2026 earnings date February 2027 — no 2027 date announced; the 4Q25 release was 12 Feb 2026 after the close), the Jan/Mar option-chain fits and interpolation (`implied_dist_v2.py`), the 103-session base rates and tail counts, the measured 15 Dec → pre-release window (`datasets/dec_to_prerelease_window.py`, query 23), the R14/R16/F02 reads (query 21), and query 17 (the final 72-hour recency check: nothing on the Feb print or FY27 guidance; no change to the number).

## 3. Leading Hypothesis Entities
Airbnb, ABNB, 4Q26 print, 1Q27 revenue guide, FY27 margin guide, 5 Nov 2026 print, pre-release January window, options-implied distribution, Morgan Stanley

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Carry the "Q4 prints positive 6 of 6" base rate at full strength (+7.9% mean day-1) | discarded; the event is R14's | the day-1 count is 5 of 6 and 3 of 6 at ≥ +5% (claim 20), n 6, and the Q4 print's positive history coincides with three reopening/first-profit years; R14 conditions the February reaction on the 4Q26 sign (R16: mean ~8.3%, P(≥ Street) 0.27) and the 1Q27 guide (F02 median 9.4% vs Street 11–12.4%) and lands at mean +0.8%, P(≥ +5%) 0.30; revision 1's +2 to +4% by branch (unconditional +2.6%) was the shrunk base rate without those terms |
| Feb print reaction is independent of the 5 Nov branch | discarded | the 4Q26 nights print and the 1Q27 guide are set against the 5 Nov guide; after a decel-guide-below November the Q4 nights bar is lower and a further deceleration guide is expected, so the Feb mean is lower (−0.5%) and the pre-print drift is negative (−2.0%: the memo's "estimate cuts and multiple compression" leg, carried at about half strength, judgment) |
| Use the memo's 12-month scenario prices ($180–190 / $138–148 / $115–130) as the 12 Feb branch centres | discarded | they are 12-month joint-solve values (memo table); the model's branch medians at 12 Feb ($178 / $169 / $166 / $154) are outputs of the judgment drifts in section 9 of the S02 log, cross-checked against the ladder's ±2–3% fundamental range (A07-14), and the short-case $115–130 is the model's ~10th percentile, not a branch centre |
| The calendar January + February seasonal (+14.6% excess) as a pre-release drift | discarded (A07-12) | it contains the reaction day and the post-release sessions; replaced by the measured 15 Dec → pre-release window (+6.5% excess ex-IPO, n 5, sd 12.3), carried at 25% = +1.5% |
| Options interpolation between Jan and Mar expiries as the anchor, uncorrected | discarded (A07-11) | the interpolation prices 44% of the February event; the missing 56% of a 9.5% event is added as variance (log-sd 24.3% → 25.2%) |
| Corporate action / takeover before Feb as a component | not modelled | S02 convention (6) |

## 5. Independent Estimates
- base_rate_estimate: median $167.8, P(≤150) 0.25, P(≤143) 0.19, P(≥180) 0.34 — all-history 103-session return distribution (claim 22) on $167.51; the 2023+ window (median +3.2%, sd 15.3) gives $172.9, 0.13 / 0.07 / 0.38 and is the bullish bound; overlapping windows, effective n ≈ 13 (all) / 8 (2023+)
- decomposition_estimate: median $164.7, P(≤150) 0.35, P(≤143) 0.27, P(≥180) 0.35, 5–95% $111–242 — the S02 revision-2 mixture extended by the 15 Dec → 11 Feb block (branch drift + measured pre-release window + 39-session diffusion) and the R14-mapped Feb day-1 event (claim 25); Feb day-1 unconditional mean +0.7%, sd 9.1%
- anchor_estimate: median $169.9 (risk-neutral $167.8 + 3% premium over 0.41y), P(≤150) 0.32, P(≤143) 0.26, P(≥180) 0.41 — Jan/Mar mixture-RND interpolation with the February event variance restored (claim 21), captured 2026-09-17T03:12Z
- anchor_value: median $167.8 (risk-neutral), P(≤ $150) 0.34, P(≤ $143) 0.28, P(≥ $180) 0.39
- final_estimate: CDF mixture 0.65 decomposition + 0.35 real-world anchor (the anchor CDF used is the corrected mixture RND, `anchor_cdf_v2.csv`): median **$166**; 5/10/25/50/75/90/95 = $110 / 121 / 141 / 166 / 195 / 224 / 244; P(≤150) **0.34**, P(≤143) **0.27**, P(≥180) **0.37**
- final_minus_anchor: median −$3.5 (−2.1%); P(≤150) +0.01, P(≤143) +0.01, P(≥180) −0.04. NOT_INDEPENDENTLY_DERIVED by the 10-point rule on the thresholds; the independent decomposition is shown above and lands $5.2 below the anchor on the median. The two agree on the thresholds because two opposite effects roughly cancel by February, and revision 2 says which: the adopted 5 Nov print view (median −$7.5 on the decomposition by 15 Dec, S02 log) against the measured pre-release window carried at +1.5% and the R14 February event at +0.7% (together +$3.5 to +4 by 12 Feb), while the market's distribution is symmetric on both and wider only because it is risk-neutral. The named asymmetry that survives is the sign of the 5 Nov print, worth about −3% on the median; the February print itself we do not claim to call — R14's +0.8% mean is inside the options' symmetric event and we carry it because R14 conditions it on the 1Q27 guide (F02), which the market cannot see. Astra's construction (claim 35: two symmetric events, no drift, no seasonal) lands at $167.4, $1 above this final and $2.7 above the decomposition

## 6. Final Numbers
| Percentile | USD |
|---|---|
| 5 | 110 |
| 10 | 121 |
| 25 | 141 |
| 50 | 166 |
| 75 | 195 |
| 90 | 224 |
| 95 | 244 |

Threshold probabilities: P(≤ $150) = **0.34**; P(≤ $143) = **0.27**; P(≥ $180) = **0.37**. Also P(≤ $125) 0.13, P(≥ $200) 0.22.
Mass below $100: 2.1% (a −40.3% move over 103 sessions: 9 of 1,344 overlapping windows (0.7%), all one episode starting Jan–Feb 2022, none since 2023 where the worst is −31.7%; the model's mass comes from the decel-guide-below branch's tail plus a bad February, and from the corrected anchor's 2.5% — two prints of sd 9–9.5% and 101 diffusion sessions put a real weight there). Mass above $260: 2.9% (+55%; one window in the series reached it, the run into the 2Q26 print from 27 Mar 2026; the accel branch plus an up February is the model's route).
Modes: unimodal at the $5 bin level (peak $150–155) with a fat left shoulder from the decel-guide-below branch (median $154) and a long right tail from the accel branch plus a positive Feb print (median $178).
Floor check: minimum density per $5 bin between $120 and $230 is 1.3% (at $230); nothing inside $100–$250 would shock us.
Mean $170; log-sd of the final ≈ 24%; median return −0.7% from $167.51.
Feb-print day-1 distribution (own event, all branches): mean +0.7%, sd 9.1, P(≥ +5%) 0.32, P(< 0) 0.47 (R14's own numbers 0.30 / 0.51 are the reference; X01 should use R14); conditional on the team's base 5 Nov branch: mean −0.5%.

## 7. Sensitivity
All rows from `../close-15dec-2026/datasets/sensitivity_v2.csv` (decomposition level).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Feb day-1 means +2.5 / +1.0 / +0.5 / −0.5% (R14-mapped, unconditional +0.7%) | revision-1 means (+4.0 / +2.5 / +2.5 / +2.0, unconditional +2.6%): decomposition median $168.0, P(≤150) 0.31, P(≥180) 0.39; raw n-6 base rate +7.9% in every branch: $176.5, 0.24, 0.47; zero in every branch: $163.5, 0.36, 0.34 |
| Pre-release window +1.5% (25% of the measured +6.5%) | none: median $162.3, P(≤150) 0.37, P(≥180) 0.33; half the measured excess (+3.25%): $167.6, 0.32, 0.38 |
| Post-print drifts (Nov branch to Feb) −0.5 / −0.5 / −0.5 / −2.0% | none (Astra's construction): median $168.4, P(≤150) 0.31, P(≥180) 0.39; revision-1 drifts (+1 / −1 / −1 / −3): $163.0, 0.37, 0.34; doubled: $161.1, 0.38, 0.32 |
| Print-state weights 0.32 / 0.10 / 0.13 / 0.45 | revision-1 weights: $163.1, 0.36, 0.34; P(accel) 0.40: $166.4, 0.33, 0.37; P(accel) 0.22: $162.6, 0.37, 0.33 |
| 5 Nov day-1 means shrunk 30–40% | market-neutral: $167.8, 0.32, 0.38; unshrunk: $163.9, 0.36, 0.35 |
| Background vol 30% | 33%: P(≤150) 0.36, P(≥180) 0.36; 26%: 0.33 / 0.35 |
| Total drift 6.97% | 3% (revision 1): $162.1, 0.37, 0.33; 0: $160.2, 0.39, 0.31 |
| Anchor weight 0.35 | 0: $165, 0.35 / 0.27 / 0.35; 1 (real-world corrected RND): $169.9, 0.32 / 0.26 / 0.41 |
| February event sd 9.5% in the anchor correction | 8.5% (R14's low case): anchor log-sd 25.2% → 25.0%, thresholds move < 0.005 |
| Print date 11 Feb after close | a release a week either side changes nothing material (< 0.3 on the log-sd) |

## 8. Monitoring Calendar
Update procedure: as S02 (re-centre, keep branch weights, collapse the 5 Nov mixture on 6 Nov), then re-run with the Feb block only after 15 Dec; after the 4Q26 date is announced, fix the resolution session; R14 owns the February event — re-run it first, then map its branch means here.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-25 to 10-02 | 6 Nov weekly lists; September dumps refresh the nowcast | re-set the print-state weights from R01/R02 (each +0.5pp in the index centre ≈ +$1.5 on the 12 Feb median) |
| 2026-10-02 | prelim memo due | quote median $166, P(≤150) 0.34, P(≤143) 0.27, P(≥180) 0.37; the memo's $138–148 is the 24th–33rd percentile of the 12 Feb close |
| 2026-11-06 | 5 Nov reaction close | collapse the mixture: reference 6 Nov close (branch still weighted, before the realised branch is fixed) $150 → 12 Feb median ≈ $150.5, P(≤150) ≈ 0.49, P(≥180) ≈ 0.16; $160 → $160.6, 0.35, 0.26; $175 → $175.6, 0.19, 0.44 (v2 blocks from the 6 Nov close; rerun the script with `sessions_pre` = 0 and the realised branch fixed for the live numbers) |
| 2026-12-15 | S02 resolves; sell-side 1Q27 revisions (R14 trigger) | re-run from the 15 Dec close with the Feb block only (39 sessions + event): P(≥180) from $160 ≈ 0.23; Street 1Q27 ≤ $2,950M → Feb means +0.5 |
| mid-Jan 2027 | Airbnb announces the 4Q26 date; 15 Jan expiry rolls; Q4 print previews | fix the resolution session; re-pull the Feb weekly straddle for the Feb event sd (replace 9.0%) and rebuild the anchor from the expiry that straddles the actual release date |
| 2027-01-25 | STR 4Q26 US RevPAR (R11/B15); NTTO December arrivals | if RevPAR ≤ +1%: −0.5% on the Feb day-1 means (R14 rule) |
| ~2027-02-11/12 | 4Q26 print and reaction session | resolve on the close of the first session after the release |

## 9. Model parameters
See § 9 of the S02 log: 22 judgment settings across the batch, of which S03 owns the four mid drifts, the four Feb means and the pre-release window.

## 10. Revision notes
| # | Change (revision 1 → 2) | Finding |
|---|---|---|
| 1 | Anchor rebuilt from per-expiry two-lognormal mixture RNDs (arbitrage-free) with log-quantile interpolation, and the blend now uses that CDF; the revision-1 smile's 0.47% negative mass and the lognormal substitution recorded in claim 21 | A07-03, A07-04 |
| 2 | The 56% of the February event variance missing from the Jan/Mar interpolation restored (log-sd 24.3% → 25.2%); "1.4 events is close to 2" withdrawn | A07-11 |
| 3 | Calendar Jan + Feb seasonal (+2%, mis-stated as a quarter of +14.6%) replaced by the measured 15 Dec → pre-release window (+6.5% excess ex-IPO, n 5, 3 of 5 positive) carried at 25% = +1.5%, separated from the earnings day; claim 24 new | A07-12 |
| 4 | Tail evidence corrected (worst 103-session −47.7% from Feb 2022, 11 overlapping windows ≤ −40%, one episode; 2023+ worst −31.7%; one window ≥ +55%); bound masses re-justified (1.5% → 2.1% below $100; 2.5% → 2.9% above $260) | A07-13 |
| 5 | Branch medians relabelled as outputs of judgment drifts cross-checked against the ladder, not derived from it | A07-14 |
| 6 | Sessions 36 + 1 + 26 + 39 + 1 = 103; convention (6) corrected | A07-15 |
| 7 | Drift convention and within-branch event sd inherited from S02 revision 2 (total 6.97%; sd 8.45% within / 9.5% unconditional) | A07-17 |
| 8 | Post-print drifts revised on the rebased evidence: to 15 Dec −1.5 / −0.5 / −0.5 / −1.0; 15 Dec → 11 Feb −0.5 / −0.5 / −0.5 / −2.0 (revision 1 +1 / −1 / −1 / −3) | A07-05, A07-06 |
| 9 | Print-state weights from R01/R02/S01 (0.32 / 0.10 / 0.13 / 0.45); February event from R14 (means +2.5 / +1.0 / +0.5 / −0.5, sd 9.0 → unconditional +0.7%, P(≥ +5%) 0.32; revision 1 +2.6% / 0.39); "6 of 6" wording replaced by 5 of 6 positive, 3 of 6 ≥ +5% | post-S01 inputs (R01, R02, R14) |
| 10 | Headline: median $165 → **$166**; P(≤150) 0.34 → **0.34**; P(≤143) 0.27 → **0.27**; P(≥180) 0.35 → **0.37**; percentiles 113/123/141/165/193/222/242 → 110/121/141/166/195/224/244. The centre barely moved because the changes offset: R02 weights +$1.7, drift convention +$2.6, lighter post drifts +$1.7, anchor +$0.4 (median) and a wider anchor (event variance) against the R14 February event −$3.3 and the smaller pre-release term −$0.9 (decomposition-level sensitivity rows); the tails widened (5th 113 → 110, 95th 242 → 244) | — |
| 11 | Claims 23–25 rewritten; independence flag kept with the cancellation now itemised | A07 "what to keep" |
