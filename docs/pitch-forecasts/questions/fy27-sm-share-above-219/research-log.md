# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A08, Fable 5.1). Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion question: F03 `fy27-margin-guide` — this question is now simulated JOINTLY with F03 in one script so the conditional table aggregates to the unconditional by construction. Reproduction: `../fy27-margin-guide/datasets/f03_f04_joint_v2.py` (numpy only, seed 20260917, 400,000 draws, ~30 s; writes [datasets/f04_v2_summary.csv](datasets/f04_v2_summary.csv), [datasets/f04_v2_conditionals.csv](datasets/f04_v2_conditionals.csv), [datasets/f04_v2_sensitivity.csv](datasets/f04_v2_sensitivity.csv) here). Revision-1 `f04_model.py` and its CSVs are left untouched as the audit trail. Audit: `docs/pitch-forecasts/audits/A08-research-audit.md`; response: `audits/A08-audit-response.md`.

## 0. Metadata
- question_name: fy27-sm-share-above-219
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` F04)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2028-02-15
- resolution_date: 2028-02-15
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will Airbnb's FY27 sales and marketing expense (GAAP, ex-SBC, as reported in the FY27 10-K) be ≥ 21.9% of FY27 revenue?
### Resolution Criteria
Yes if FY27 S&M ex-SBC ÷ FY27 revenue ≥ 0.219 in the 10-K filed ~Feb 2028. Resolution date ~Feb 2028.
### Fine Print
Far out; the log should also give P(≥21.9%) conditional on the Feb 2027 FY27 margin guide buckets in F03.

Conventions adopted (stated, not changing the question): (1) "S&M ex-SBC" = the income-statement sales and marketing line less the stock-based compensation attributed to sales and marketing in the 10-K's SBC-by-line table (the `sm_cash` construction of `data/processed/margin_build/02_financial_panel/02_panel_annual.csv`: FY25 2,588 − 212 = $2,376M, 19.41% of $12,241M); (2) ratio computed on the 10-K's own FY27 figures, unrounded, so 21.86% resolves No and 21.90% resolves Yes; (3) if Airbnb re-segments the line (e.g. moves field operations out of S&M), the 10-K's "sales and marketing" caption as filed governs; (4) resolution on the 10-K filing (expected mid-to-late February 2028), not on the 4Q27 letter; (5) [rev 2] the F03 buckets in the conditional table are F03's **literal** buckets (revision 2): (a)–(c) numeric floors only, (d) numeric < 35.5 or explicit down/investment-year, (e) any qualitative or absent sentence.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | S&M ex-SBC as % of revenue by year (10-K GAAP line less S&M SBC): 2019 33.25, 2020 21.91, 2021 18.13, 2022 16.69, 2023 16.47, 2024 17.82, 2025 19.41 (GAAP incl. SBC: 17.78 / 19.35 / 21.14 for 2023–25). Year-over-year change in the ex-SBC share: 2022 −1.44, 2023 −0.23, 2024 +1.35, 2025 +1.59. [rev 2] **Completed-year reference class: increases ≥ 0.6pp in 2 of 4 (2022–25), 2 of 3 (2023–25), 2 of 2 (2024–25)**; FY26 is a forecast (line build 21.31%, +1.9pp) and is not a completed observation. Extract: [datasets/sm_share_history_annual.csv](datasets/sm_share_history_annual.csv) | `data/processed/margin_build/02_financial_panel/02_panel_annual.csv` (from the 10-Ks); recomputed in `audits/A08-reproduce.py` | 2026-09-14 | 2026-09-17 | yes |
| 2 | Quarterly S&M ex-SBC: 1Q25 519 (22.8% of revenue), 2Q25 639 (20.6), 3Q25 585 (14.3), 4Q25 633 (22.8); 1Q26 696 (26.0, +34% y/y), 2Q26 808 (22.4, +26%); 1H26 1,504 on $6,286M = 23.93% vs 1H25 1,158 on $5,368M = 21.57% (+2.35pp). Extract: [datasets/sm_share_history_quarterly.csv](datasets/sm_share_history_quarterly.csv) | `02_panel_quarterly.csv`; 10-Q MD&A: 1Q26 marketing +$126M, 2Q26 +$132M "driven by higher paid growth marketing initiatives in emerging markets and partnerships" plus payroll +$42M/+$48M (F1Q26_sm_total, F2Q26_sm_total) | 2026-08-06 | 2026-09-17 | yes |
| 3 | Line build (the pitch's margin line view): FY26 S&M ex-SBC $3,040M = 21.31% (marketing $2,119M: 1H26 +32%, 2H26 +25% plus the $67M 3Q26 reconciliation step; field $922M +18%); FY27 $3,459.6M = **21.857%** of $15,828.6M (marketing +15% to $2,437M; field +11% to $1,023M — **the team's spending interpretation, not a management budget**, A08-08); FY27 evidence-only build 21.36%; scenario columns: cost bear 23.33%, cost bull 20.76%, revenue bear 23.14%, revenue bull 20.88%, both bear 24.70%, both bull 19.83%. Sensitivity: +5pts of FY27 marketing growth = −0.67pp of FY27 margin (≈ +0.65pp of S&M share) | `data/processed/margin_build/40_line_build/40_annual.csv`, `40_params.csv`, `40_sensitivities.csv`; `docs/margin-build/notes/40_line_build.md` | 2026-09-15 | 2026-09-17 | yes |
| 4 | The run's allocated FY27 S&M is $3,721M = 23.5% of revenue (carrying the 1H26 marketing growth rate forward in the residual allocation); "the two builds agree on 2026 and disagree on 2027 by one point, entirely in S&M"; the Street's FY27 EBITDA $5,766M (36.45%, n 44, sd $154M) implies an incremental margin of 43.7% that "requires the ramp to stop" | `docs/margin-build/SYNTHESIS.md` §3; `data/processed/margin_build/23_final_model/23_lines_quarterly.csv`, `23_vs_consensus.csv`; `notes/40_line_build.md` | 2026-09-15 | 2026-09-17 | yes |
| 5 | [rev 2, corrected per A08-04/05] Street-implied FY27 S&M: adjusted EBITDA = revenue − five cash-cost lines **+ D&A** in this line build, so S&M = revenue − EBITDA + D&A − other four lines = 15,819.3 − 5,766.0 + 82.5 − 6,807.3 = **$3,328.5M = 21.04%** (rev 1 omitted D&A: $3,246M = 20.52%). The other four lines ($2,760 + 1,378 + 1,625 + 1,045) remain team assumptions. The Street's sd ($154M) is analyst **dispersion**, not a forecast-error scale: the dispersion-only tail P(≥21.9%) is 0.19, an illustration; with an explicit uncertainty model (EBITDA sd = √(154² + 175²) adding a one-year-ahead realisation error of ~3% [judgment], other lines sd $200M) the share sd is 1.9pp and **P(≥21.9%) = 0.33** | computed from claims 3–4 and `23_vs_consensus.csv` FY27 (`lseg_revenue_musd`, `lseg_ebitda_musd`, `lseg_ebitda_sd_musd`); `40_annual.csv` FY27/base `da`; `f03_f04_joint_v2.py` `street_anchor()` | 2026-09-17 | 2026-09-17 | yes |
| 6 | Short case (team pitch): FY27 revenue $14,914M (+4.5%) with costs at budget → S&M 25–29% of revenue in 4Q26 and 1Q27, FY27 S&M share ≈ 23–24% (FY27 margin 31.9%); revenue scenarios in the line build do not flex the discretionary lines ("the M6 finding that Airbnb's discretionary lines have not responded to revenue within a year"; k = 0.364 on total cash costs, k_down < k_up) | `40_short_case_summary.csv`, `40_short_case_stress.csv`; `docs/margin-build/notes/M6_cycle_flex.md` via SYNTHESIS §9 | 2026-09-15 | 2026-09-17 | yes |
| 7 | [rev 2, re-attributed per A08-08] Management on S&M into 2027 — what was actually said: 2Q26 call "some incremental investment ... in sales and marketing" in 2H26; Goldman 8 Sep 2026 (V021–V026): "Nearly 90% of our traffic is direct or organic" (V021), "We're going to have some major announcements next year" (V023), seller/host services as the high-margin pool (V022, V026). What is the team's reading: H08 "FY27 S&M growth above revenue growth is the base case" and H07 "launches before revenue in FY27" are WS05's *implications* (H07/H08 `confidence = medium`), not management budget statements; **no management statement gives an FY27 marketing growth rate**. Brand-marketing statements 63–68% kept (n 35–41), the least reliable line after SBC. The Goldman HTML (`GS26.html`) is absent from this checkout; the ledger rows are quote-verified against the recorded stockanalysis.com URL | `05_fy27_hints.csv` H07, H08; `05_statements.csv` V021–V026; `docs/margin-build/notes/05_mgmt_statements_v2.md` | 2026-09-14 | 2026-09-17 | yes |
| 8 | [rev 2, corrected per A08-20] Historical S&M-share guidance and outcomes (ledger basis: **GAAP incl. SBC**; ex-SBC outcomes recomputed alongside): FY22 "sales and marketing expense as a percent of revenue is expected to remain relatively flat" (GAAP −174.7bp; ex-SBC −143.8bp); FY23 "flat as a percent of revenue for the full year" (GAAP −27.2bp; ex-SBC −22.6bp); 1Q23 "approximately 150 basis points higher" (GAAP +190bp, a miss); Chesky 2021: "We don't intend to ever again spend the amount of money as a percentage of revenue on marketing ... as we did in 2019" (still true); 10-Q boilerplate: S&M "will vary from period to period as a percentage of revenue ... over the long term, we expect it will decline as a percentage of revenue relative to 2019". The two bases are not interchangeable calibration observations for this ex-SBC question | `02_guidance_ledger.csv` rows ABNB-4Q21-sm_pct_rev_yoy_bps-FY2022-034, ABNB-4Q22-sm_pct_rev_yoy_bps-**FY2023-065**, ABNB-4Q22-sm_pct_rev_yoy_bps-**1Q23-063**; `02_panel_annual.csv`; `05_statements.csv` S003, Q002 | 2023-02-14 | 2026-09-17 | yes |
| 9 | FY27 revenue: WS06 v2 base $15,829M (+10.94%), bear $14,948M (+5.2%), bull $16,571M (+15.7%); LSEG $15,819M (n 44); B3 band +9.18 to +11.52%; RNPL-aware +8.4 to +10.2% | `docs/margin-build/notes/06_fy27_path_v2.md`; `data/processed/rnpl_short_audit/turns_vs_street_and_w_band.csv` | 2026-09-14 | 2026-09-17 | yes |
| 10 | [rev 2, corrected per A08-09] There is **no observed precedent** of a marketing cut to protect an FY floor: the 3Q24 letter guided Q4 2024 margin "to decline relative to the same time period last year due to **higher** marketing and product development expenses" while raising the FY point, i.e. the opposite of a cut. The $176.7M 4Q26 marketing cut is a **modelled** future action in the line build's short case (`short_with_q4_marketing_cut`), and C04 rev 2 prices a Q4 cost cut at 0.50 when the FY26 floor is at risk. A discretionary spending response remains plausible; it is a judgment, not evidence. B03 (marketing cut signalled at 5 Nov) is a separate question | `data/raw/letters/3Q24_d886752dex991.htm` (Outlook); `40_short_case_summary.csv`; C04 rev 2 log claim 24 | 2026-09-17 | 2026-09-17 | no |
| 11 | [rev 2] F03 vector (revision 2, literal convention): (a) 0.02, (b) 0.04, (c) 0.10, (d) 0.36, (e) 0.48; FY26 print from C04 rev 2 (mean 35.82, P<35.5 0.18) | `docs/pitch-forecasts/questions/fy27-margin-guide/research-log.md` §6 (rev 2) | 2026-09-17 | 2026-09-17 | yes |
| 12 | No market prices this item; web returned only historical marketing pieces (Marketing Week: CEO on keeping marketing % of revenue consistent; S&M +18.7% in the quarter to June 2025) and no 2027 S&M preview | [sources/web_search_log.md](sources/web_search_log.md); [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 13 | [rev 2] Joint Monte Carlo (`f03_f04_joint_v2.py`): FY27 revenue 0.75 × N(15,829, 450) + 0.25 × N(15,100, 500); FY26 S&M ex-SBC N(3,040, 60) less $40M per sd of FY26 print surprise (a stronger FY26 print came with a lower 2H26 S&M base); FY27 S&M growth = 14.5 + 3.0 z + 0.30 × (revenue growth − 10.94) + N(0, 4.5) where z is the reinvestment-intensity latent shared with F03's regime draw (total growth sd ≈ 5.4, mean 14.5); ratio median 22.16%, 5–95% 20.1–24.4%, **P(≥21.9%) 0.581**; conditionals **from the joint** a 0.40 / b 0.46 / c 0.56 / d 0.67 / e 0.53, Σ P(F03) × P(F04 | F03) = 0.581 exactly (rev 1's conditionals were separate reruns that aggregated to 0.614 against its own 0.581, A08-06) | [datasets/f04_v2_summary.csv](datasets/f04_v2_summary.csv), [datasets/f04_v2_conditionals.csv](datasets/f04_v2_conditionals.csv), [datasets/f04_v2_sensitivity.csv](datasets/f04_v2_sensitivity.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 15 Sep line build and the 17 Sep F03 rev 2 / C04 rev 2 objects; 2 days old against a ~17-month window. The next real inputs are the 5 Nov 10-Q (2H26 marketing run-rate, any B03 sentence) and the Feb 2027 FY27 margin sentence.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs C01, C02, C04/C09, C05–C07
2. [repo] `docs/margin-build/SYNTHESIS.md` §3, §9; `notes/40_line_build.md`; `notes/05_mgmt_statements_v2.md`; `notes/M3_guide_policy_margin.md`; `05_fy27_hints.csv`; `05_statements.csv` (S&M / marketing rows, V015–V026)
3. [repo, pandas] `data/processed/abnb_quarterly_costlines.csv`, `abnb_driver_history_quarterly.csv`; `02_financial_panel/02_panel_annual.csv`, `02_panel_quarterly.csv` (sm_gaap, sm_cash); `abnb_quarterly_cost_stack_exsbc.csv` header
4. [repo] `40_line_build/40_annual.csv`, `40_params.csv`, `40_sensitivities.csv`, `40_short_case_*.csv`; `23_final_model/23_lines_quarterly.csv`, `23_vs_consensus.csv`
5. [repo, pandas] `02_guidance_ledger.csv` S&M rows (sm_pct_rev_yoy_bps)
6. [Kalshi API] KXABNBA, KXABNB; [Polymarket API] "Airbnb 2027", "Airbnb guidance" (2026-09-17T03:18:45Z) — nothing
7. WebSearch: Airbnb marketing spend 2027 margin investment analysts
8. WebSearch: Airbnb news; Airbnb 2027 revenue growth outlook analyst expectations; Airbnb fourth quarter 2026 results date February 2027 (batch-shared)
9. [computed] `datasets/f04_model.py` (rev 1: base, 11 sensitivities, 5 F03 conditionals)
10. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)
11. [rev 2, repo] `docs/pitch-forecasts/audits/A08-research-audit.md`; `audits/A08-reproduce.py` (run from the repo root, `py -3.13 -B`)
12. [rev 2, repo] `data/raw/letters/3Q24_d886752dex991.htm` Outlook and S&M paragraphs (claim 10); `40_annual.csv` FY27/base `da`, `cor_cash`, `ops_cash`, `pd_cash`, `ga_cash` (claim 5); `02_panel_annual.csv` `sbc_sm` (claims 1, 8); ledger IDs …-FY2023-065 / …-1Q23-063 (claim 8); `05_fy27_hints.csv` H07/H08 `confidence`, `05_statements.csv` V021–V026 `source_path_or_url`, `quote_verified` (claim 7)
13. [rev 2, repo] `questions/fy26-margin-sentence/` rev 2 (FY26 print object, Q4 cost-cut rule); `questions/bonus-marketing-cut-signalled/` (B03, cross-reference only)
14. [rev 2, computed] `../fy27-margin-guide/datasets/f03_f04_joint_v2.py` (joint model, `street_anchor()`, 22 F04 sensitivities)

WebSearch calls charged to this batch: 5 across F01–F04 (none added in revision 2).

## 3. Leading Hypothesis Entities
Airbnb, sales and marketing, Brian Chesky, Ellie Mertz, emerging-market marketing, 2027 launches, FY27 10-K, line build

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The S&M share keeps rising a third year (+0.6pp or more over FY26's ~21.3%) | leading, 0.55 | 1H26 +2.35pp y/y; the line build's central case (21.86%) sits a hair under the bar, so anything above its +15%/+11% growth pair (the team's assumption, claim 3), or any revenue shortfall with costs at budget (claim 6), clears it. [rev 2] No management statement establishes the FY27 growth rate; the case rests on the run-rate and the launch pattern |
| The ramp stops: marketing grows below revenue in 2027 (the Street's implied 21.0%, claim 5) | kept as the main No route (~0.35) | Chesky's "90% direct or organic" and the 2021–23 record of S&M share falling; the F03 (a)/(b) branches carry this. [rev 2] The rev-1 "FY24 floor protected by phasing brand marketing down" precedent is withdrawn (claim 10) |
| A revenue shortfall (short case) raises the ratio mechanically | kept, 0.25 tail | Discretionary lines have not flexed within a year (claim 6); the short case gives 23–24% |
| Airbnb re-captions the line (field operations out of S&M) | discarded as a route (convention 3) | No precedent; the 10-K caption has been stable since the IPO |
| The line build's 21.86% is exactly the median and the question is a coin toss | discarded as the headline, kept as the floor of the interval | The run's allocation (23.5%) and the 1H26 run-rate argue the centre is above 21.9; the Street's implied 21.0% argues below; the model's median is 22.2 |
| Use the Street's FY27 EBITDA as management's plan | discarded | The Street's FY27 incremental margin 43.7% has no support in any management statement (claim 4) |

## 5. Independent Estimates
[rev 2] Independence label (A08-03): **partially dependent** — the decomposition and the anchor share the line build's other four cost lines; the base rate is the only estimate that does not use the team's FY26/FY27 builds.
- base_rate_estimate: 0.50 — reference class "year-over-year change in the ex-SBC S&M share ≥ +0.6pp" (claim 1): **2 of 4 completed years** (2022–25); regime sensitivity 2/3 (2023–25) and 2/2 (2024–25); the threshold needs only +0.6pp on the FY26 line-build share and the regime since 2024 is a rising share, so the class is read at 0.50–0.60 with 0.50 as the broad number (rev 1: 0.55 on 3/5 including FY26E — withdrawn, A08-07)
- decomposition_estimate: 0.58 — joint Monte Carlo (claim 13); ratio median 22.2%
- anchor_estimate: 0.33 — no market; the Street's FY27 EBITDA implies S&M = 21.04% (claim 5, D&A-corrected), 0.86pp below the bar; with the explicit uncertainty model (EBITDA dispersion + realisation error, other-line uncertainty) P ≈ 0.33 (the dispersion-only 0.19 is an illustration, not a probability). The Street's S&M is a residual of an EBITDA panel, not a modelled line
- anchor_value: 0.33 (Street-implied FY27 S&M share 21.04%, LSEG FY27 EBITDA $5,766M n 44 sd $154M, 11 Sep 2026; uncertainty model in `street_anchor()`)
- final_estimate: 0.55 (credible interval 0.40–0.68)
- final_minus_anchor: +22 points. Named asymmetry: the anchor is the Street's FY27 margin, which the team's entire margin build disputes on this one line (claim 4); the decomposition (line build run-rate + the 1H26 step) gives 0.58 and the completed-year base rate 0.50–0.60 without reference to the Street. The final is trimmed 3 points below the decomposition **as a judgment** toward the base rate and the anchor, replacing rev 1's trim that cited a marketing-cut precedent which does not exist (claim 10). Astra's independent estimate is 0.55 (three states 25/50/25 with 20/55/90); this revision coincides with it

## 6. Final Numbers
**Binary.** P(FY27 S&M ex-SBC ÷ FY27 revenue ≥ 21.9%, FY27 10-K) = **0.55**, credible interval **0.40–0.68**.
Ratio distribution (joint model): 5/10/25/50/75/90/95 = 20.1 / 20.5 / 21.3 / 22.2 / 23.0 / 23.9 / 24.4%.
**Conditional on the F03 (Feb 2027 FY27 margin guide, literal) bucket.** The joint model's conditionals aggregate to its unconditional 0.581 by construction; the final table subtracts the same 3-point judgment trim from every row, so it aggregates to the final: Σ P(F03 rev 2) × P(F04 | F03) = 0.02×0.37 + 0.04×0.43 + 0.10×0.53 + 0.36×0.64 + 0.48×0.50 = **0.548**.
| F03 bucket | P(S&M ≥ 21.9%) — joint model | final (trimmed −0.03) |
|---|---|---|
| (a) ≥36.5% floor or point | 0.40 | 0.37 |
| (b) 36.0–36.4% | 0.46 | 0.43 |
| (c) 35.5–35.9% | 0.56 | 0.53 |
| (d) <35.5%, down y/y, or investment year | 0.67 | 0.64 |
| (e) no numeric FY27 margin guidance | 0.53 | 0.50 |
Reading: the spread between (a) and (d) comes from two modelled links — a numeric floor ≥ 36% needs an FY26 print that came with a lower 2H26 S&M base, and a haircut/investment-year sentence goes with higher reinvestment intensity (z), which also drives FY27 S&M growth (+3pts per sd). Removing either link flattens the table (§7). Under the literal F03 convention, (e) is the modal bucket and carries an unconditional-like 0.50, because a qualitative sentence says little about the S&M plan. Astra's elicited conditionals (a .25 / b .35 / c .50 / d .70 / e .50) are steeper at the top; the joint model is flatter because (a)/(b) are now rare numeric-floor cases driven mostly by the FY26 print level rather than by discipline.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of the joint model from the base (0.581); the final carries the same deltas.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| FY27 S&M growth centred +14.5% (line build's +15% marketing / +11% field, the team's assumption) | +10% (cost bull): 0.32; +12%: 0.43; +17%: 0.72; +20% (cost bear): 0.85; +22% (run allocation 23.5%): 0.91 |
| FY26 S&M ex-SBC $3,040M (2H26 marketing +25%) | $2,980M (2H26 +20%): 0.45; $3,100M (2H26 +30%): 0.70 |
| 25% short-case revenue tail | none: 0.53; 50%: 0.63; FY27 revenue base $15,500M (RNPL-aware): 0.66; $16,100M (bull): 0.52 |
| Total growth sd ≈ 5.4pp | ≈ 3: 0.61; ≈ 8: 0.56 |
| Cost flex to revenue β 0.30 | 0 (no flex): 0.59; 0.6: 0.56 |
| Joint links (z → S&M growth 3.0/sd; FY26 print → S&M base −$40M/sd; z → haircut +0.4/sd) | no z → S&M link: 0.58, conditionals a 0.40 / b 0.48 / c 0.58 / d 0.60 / e 0.58; no FY26-print → base link: conditionals flatten by ~0.06 at (a)/(b); stronger links (4.0 / 70 / 0.6): (a) 0.33, (d) 0.70 |
| F03 outcome (joint model) | (a) 0.40 / (b) 0.46 / (c) 0.56 / (d) 0.67 / (e) 0.53 |

Pre-mortem ("it is February 2028 and the 10-K shows S&M ex-SBC at 20.8%"): (1) management declared 2027 a leverage year in February 2027 and grew marketing ~8% — the F03 (a)/(b) branch plus the low-z half of (e), priced at ~0.25 jointly; (2) the 3Q26 $67M reconciliation step was a one-off and the FY26 base is $2,980M not $3,040M — priced at 0.45 in that row; (3) FY27 revenue printed +14% on a weak dollar while S&M grew +12% — inside the revenue draw (bull) with β; (4) a re-caption moved field operations out of S&M — not priced (convention 3). The opposite miss (24%+): the short case with costs at budget — 0.25 tail. Asymmetry: the memo's short case leans on rising S&M; at 0.55 it is "more likely than not, not a foundation", and the memo should lean on the F03-conditional reading instead — a haircut or investment-year February sentence takes it to 0.64.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.55 (0.40–0.68) and the F03-conditional table (final column) |
| 2026-11-05 | 3Q26 10-Q: S&M line and MD&A marketing/payroll split; any B03 sentence (marketing to grow below revenue / moderated) | 3Q26 S&M ex-SBC ≥ $800M (+37%): FY26 base → $3,100M, P +0.10; ≤ $740M: base → $2,980M, P −0.10; a B03 "moderation" sentence: −0.08 |
| 2027-02-11 | 4Q26 letter and 10-K: FY26 S&M ex-SBC and share; FY27 margin sentence (F03) | Re-base S26 to the print; apply the conditional row for the F03 outcome (final column); re-run the joint script with the FY26 print fixed |
| 2027-05 / 2027-08 / 2027-11 | 1Q27, 2Q27, 3Q27 10-Qs: S&M y/y and MD&A drivers | Each quarter with S&M growth ≥ revenue growth + 3pts: +0.06; ≤ revenue growth: −0.08; by 3Q27 the 9M ratio pins the FY within ~0.4pp |
| 2028-02 (est.) | FY27 10-K | Resolve on the S&M line less S&M SBC ÷ revenue, unrounded |

## 10. Revision notes
| Change | Finding |
|---|---|
| Street residual corrected for D&A: 20.52% → 21.04% ($3,328M); anchor rebuilt with an explicit uncertainty model (0.33; dispersion-only 0.19 kept as an illustration); rev-1 "~0.10 on the Street's own sd" withdrawn | A08-04, A08-05 (accepted) |
| F03/F04 rebuilt as one joint simulation (shared latent z; FY26 print → S&M base link); conditionals now aggregate to the unconditional exactly (0.581); final table subtracts a uniform 3-point trim so it aggregates to 0.55 | A08-06 (accepted) |
| Base rate: 2 of 4 completed years (regime 2/3, 2/2); FY26E removed from the class and kept as a conditioning input; base-rate estimate 0.55 → 0.50 | A08-07 (accepted) |
| Claim 7 re-attributed: H07/H08 are WS05 implications, no management FY27 marketing growth statement exists; +15%/+11% labelled the team's assumption | A08-08 (accepted) |
| Claim 10 rewritten: the 3Q24 letter cites *higher* marketing; no observed marketing-cut precedent; the $177M cut is a modelled short-case action; the 3-point trim is now a labelled judgment toward the base rate and anchor | A08-09 (accepted) |
| Claim 8: GAAP basis labelled, ex-SBC outcomes added (−143.8 / −22.6bp), guide IDs corrected to …-FY2023-065 and …-1Q23-063 | A08-20 (accepted) |
| §5 relabelled partially dependent; Astra's 0.55 recorded | A08-03 (accepted) |
| Conditional table re-keyed to F03's literal buckets (revision 2) | consequence of A08-01 |

RESUME: the next agent (X01 / synthesis) should read F04 as 0.55 with the final-column conditional table and note the number did not move: the audit's corrections changed the anchor (0.30 → 0.33), the base rate (0.55 → 0.50) and the justification for the trim, not the centre. Re-run `../fy27-margin-guide/datasets/f03_f04_joint_v2.py` after the 5 Nov 10-Q with `S26_mu` re-based; the two load-bearing judgments remain the FY27 S&M growth centre (+14.5%, ±0.13 per ±2.5pts) and the FY26 base ($3,040M, ±0.13 per ±$60M).
