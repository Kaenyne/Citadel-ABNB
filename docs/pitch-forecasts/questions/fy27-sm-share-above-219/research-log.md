# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion question: F03 `fy27-margin-guide` (this log gives P conditional on each F03 bucket). Reproduction: [datasets/f04_model.py](datasets/f04_model.py) (numpy only, seed 20260917, 400,000 draws, ~5 s; writes `f04_summary.csv`, `f04_sensitivity.csv`).

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
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will Airbnb's FY27 sales and marketing expense (GAAP, ex-SBC, as reported in the FY27 10-K) be ≥ 21.9% of FY27 revenue?
### Resolution Criteria
Yes if FY27 S&M ex-SBC ÷ FY27 revenue ≥ 0.219 in the 10-K filed ~Feb 2028. Resolution date ~Feb 2028.
### Fine Print
Far out; the log should also give P(≥21.9%) conditional on the Feb 2027 FY27 margin guide buckets in F03.

Conventions adopted (stated, not changing the question): (1) "S&M ex-SBC" = the income-statement sales and marketing line less the stock-based compensation attributed to sales and marketing in the 10-K's SBC-by-line table (the `sm_cash` construction of `data/processed/margin_build/02_financial_panel/02_panel_annual.csv`: FY25 2,588 − 212 = $2,376M, 19.41% of $12,241M); (2) ratio computed on the 10-K's own FY27 figures, unrounded, so 21.86% resolves No and 21.90% resolves Yes; (3) if Airbnb re-segments the line (e.g. moves field operations out of S&M), the 10-K's "sales and marketing" caption as filed governs; (4) resolution on the 10-K filing (expected mid-to-late February 2028), not on the 4Q27 letter.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | S&M ex-SBC as % of revenue by year: 2019 33.25, 2020 21.91, 2021 18.13, 2022 16.69, 2023 16.47, 2024 17.82, 2025 19.41 (GAAP incl. SBC: 17.78 / 19.35 / 21.14 for 2023–25). Year-over-year change in the ex-SBC share: 2022 −1.44, 2023 −0.22, 2024 +1.35, 2025 +1.59. Extract: [datasets/sm_share_history_annual.csv](datasets/sm_share_history_annual.csv) | `data/processed/margin_build/02_financial_panel/02_panel_annual.csv` (from the 10-Ks) | 2026-09-14 | 2026-09-17 | yes |
| 2 | Quarterly S&M ex-SBC: 1Q25 519 (22.8% of revenue), 2Q25 639 (20.6), 3Q25 585 (14.3), 4Q25 633 (22.8); 1Q26 696 (26.0, +34% y/y), 2Q26 808 (22.4, +26%); 1H26 1,504 on $6,286M = 23.9% vs 1H25 1,158 on $5,368M = 21.6% (+2.4pp). Extract: [datasets/sm_share_history_quarterly.csv](datasets/sm_share_history_quarterly.csv) | `02_panel_quarterly.csv`; 10-Q MD&A: 1Q26 marketing +$126M, 2Q26 +$132M "driven by higher paid growth marketing initiatives in emerging markets and partnerships" plus payroll +$42M/+$48M (F1Q26_sm_total, F2Q26_sm_total) | 2026-08-06 | 2026-09-17 | yes |
| 3 | Line build (the pitch's margin line view): FY26 S&M ex-SBC $3,040M = 21.31% (marketing $2,119M: 1H26 +32%, 2H26 +25% plus the $67M 3Q26 reconciliation step; field $922M +18%); FY27 $3,460M = **21.86%** of $15,829M (marketing +15% to $2,437M; field +11% to $1,023M); FY27 evidence-only build 21.36%; scenario columns: cost bear 23.33%, cost bull 20.76%, revenue bear 23.14%, revenue bull 20.88%, both bear 24.70%, both bull 19.83%. Sensitivity: +5pts of FY27 marketing growth = −0.67pp of FY27 margin (≈ +0.65pp of S&M share) | `data/processed/margin_build/40_line_build/40_annual.csv`, `40_params.csv`, `40_sensitivities.csv`; `docs/margin-build/notes/40_line_build.md` | 2026-09-15 | 2026-09-17 | yes |
| 4 | The run's allocated FY27 S&M is $3,721M = 23.5% of revenue (carrying the 1H26 marketing growth rate forward in the residual allocation); "the two builds agree on 2026 and disagree on 2027 by one point, entirely in S&M"; the Street's FY27 EBITDA $5,766M (36.45%, n 44, sd $154M) implies an incremental margin of 43.7% that "requires the ramp to stop" | `docs/margin-build/SYNTHESIS.md` §3; `data/processed/margin_build/23_final_model/23_lines_quarterly.csv`, `23_vs_consensus.csv`; `notes/40_line_build.md` | 2026-09-15 | 2026-09-17 | yes |
| 5 | Street-implied FY27 S&M: with the Street's EBITDA ($5,766M on $15,819M → cash costs ≈ $10,053M) and the line build's other four lines ($2,760 + 1,378 + 1,625 + 1,045 = $6,808M), S&M ≈ $3,245M = 20.5% (No); one Street sd on EBITDA ($154M) ≈ 1.0pp of S&M share | computed from claims 3–4 | 2026-09-17 | 2026-09-17 | yes |
| 6 | Short case (team pitch): FY27 revenue $14,914M (+4.5%) with costs at budget → S&M 25–29% of revenue in 4Q26 and 1Q27, FY27 S&M share ≈ 23–24% (FY27 margin 31.9%); revenue scenarios in the line build do not flex the discretionary lines ("the M6 finding that Airbnb's discretionary lines have not responded to revenue within a year"; k = 0.364 on total cash costs, k_down < k_up) | `40_short_case_summary.csv`, `40_short_case_stress.csv`; `docs/margin-build/notes/M6_cycle_flex.md` via SYNTHESIS §9 | 2026-09-15 | 2026-09-17 | yes |
| 7 | Management on S&M into 2027: 2Q26 call "some incremental investment ... in sales and marketing" in 2H26; Goldman 8 Sep 2026: marketing stays elevated into next year's launches (WS05 V022–V026), "We're going to have some major announcements next year" (V023), "Nearly 90% of our traffic is direct or organic" (V021); WS05 H08: "FY27 S&M growth above revenue growth is the base case"; H07: launches before revenue in FY27 (FY25's launch cost $200–250M); brand-marketing statements 68% kept (n 41), the least reliable line after SBC | `05_fy27_hints.csv` H07, H08; `05_statements.csv` V021–V026; `docs/margin-build/notes/05_mgmt_statements_v2.md` | 2026-09-14 | 2026-09-17 | yes |
| 8 | Historical S&M-share guidance and outcomes: FY22 "sales and marketing expense as a percent of revenue is expected to remain relatively flat" (delivered −175bp); FY23 "flat as a percent of revenue for the full year" (−27bp); 1Q23 "approximately 150 basis points higher" (+190bp, a miss); Chesky 2021: "We don't intend to ever again spend the amount of money as a percentage of revenue on marketing ... as we did in 2019" (still true); 10-Q boilerplate: S&M "will vary from period to period as a percentage of revenue ... over the long term, we expect it will decline as a percentage of revenue relative to 2019" | `02_guidance_ledger.csv` rows ABNB-4Q21-sm_pct_rev_yoy_bps-FY2022-034, -4Q22-...-FY2023-066, -4Q22-...-1Q23-062; `05_statements.csv` S003, Q002 | 2023-02-14 | 2026-09-17 | yes |
| 9 | FY27 revenue: WS06 v2 base $15,829M (+10.94%), bear $14,948M (+5.2%), bull $16,571M (+15.7%); LSEG $15,819M (n 44); B3 band +9.18 to +11.52%; RNPL-aware +8.4 to +10.2% | `docs/margin-build/notes/06_fy27_path_v2.md`; `data/processed/rnpl_short_audit/turns_vs_street_and_w_band.csv` | 2026-09-14 | 2026-09-17 | yes |
| 10 | Precedent for a marketing cut to protect the floor: 3Q24 letter guided Q4 margin "to decline ... due to higher marketing and product development expenses" while raising the FY point; the line build's short case protects the FY26 floor with a $177M 4Q26 marketing cut (~35% of Q4 marketing); C04 puts "hold and cut" at 0.26; B03 (marketing cut signalled at 5 Nov) is a separate question | `data/raw/letters/3Q24_d886752dex991.htm`; `40_short_case_summary.csv`; C04 log | 2026-09-17 | 2026-09-17 | no |
| 11 | F03 vector (this batch): (a) 0.08, (b) 0.17, (c) 0.27, (d) 0.38, (e) 0.10 | `docs/pitch-forecasts/questions/fy27-margin-guide/research-log.md` §6 | 2026-09-17 | 2026-09-17 | yes |
| 12 | No market prices this item; web returned only historical marketing pieces (Marketing Week: CEO on keeping marketing % of revenue consistent; S&M +18.7% in the quarter to June 2025) and no 2027 S&M preview | [sources/web_search_log.md](sources/web_search_log.md); [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 13 | Monte Carlo (this log): FY27 revenue 0.75 × N(15,829, 450) + 0.25 × N(15,100, 500); FY26 S&M ex-SBC N(3,040, 60); FY27 S&M growth N(14.5%, 5.5) + 0.30 × (revenue growth − 10.94); ratio median 22.16%, 5–95% 20.1–24.4%, P(≥21.9%) 0.581; conditionals by F03 bucket (growth shift −4.5 / −2.0 / 0 / +3.5 / +0.5 and short-tail weight 0.10 / 0.15 / 0.25 / 0.35 / 0.30): a 0.28, b 0.44, c 0.58, d 0.78, e 0.62 | [datasets/f04_summary.csv](datasets/f04_summary.csv), [datasets/f04_sensitivity.csv](datasets/f04_sensitivity.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 15 Sep line build and the 17 Sep F03 vector; 2 days old against a ~17-month window. The next real inputs are the 5 Nov 10-Q (2H26 marketing run-rate, any B03 sentence) and the Feb 2027 FY27 margin sentence.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs C01, C02, C04/C09, C05–C07
2. [repo] `docs/margin-build/SYNTHESIS.md` §3, §9; `notes/40_line_build.md`; `notes/05_mgmt_statements_v2.md`; `notes/M3_guide_policy_margin.md`; `05_fy27_hints.csv`; `05_statements.csv` (S&M / marketing rows, V015–V026)
3. [repo, pandas] `data/processed/abnb_quarterly_costlines.csv`, `abnb_driver_history_quarterly.csv`; `02_financial_panel/02_panel_annual.csv`, `02_panel_quarterly.csv` (sm_gaap, sm_cash); `abnb_quarterly_cost_stack_exsbc.csv` header
4. [repo] `40_line_build/40_annual.csv`, `40_params.csv`, `40_sensitivities.csv`, `40_short_case_*.csv`; `23_final_model/23_lines_quarterly.csv`, `23_vs_consensus.csv`
5. [repo, pandas] `02_guidance_ledger.csv` S&M rows (sm_pct_rev_yoy_bps)
6. [Kalshi API] KXABNBA, KXABNB; [Polymarket API] "Airbnb 2027", "Airbnb guidance" (2026-09-17T03:18:45Z) — nothing
7. WebSearch: Airbnb marketing spend 2027 margin investment analysts
8. WebSearch: Airbnb news; Airbnb 2027 revenue growth outlook analyst expectations; Airbnb fourth quarter 2026 results date February 2027 (batch-shared)
9. [computed] `datasets/f04_model.py` (base, 11 sensitivities, 5 F03 conditionals)
10. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)

WebSearch calls charged to this batch: 5 across F01–F04.

## 3. Leading Hypothesis Entities
Airbnb, sales and marketing, Brian Chesky, Ellie Mertz, emerging-market marketing, 2027 launches, FY27 10-K, line build

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The S&M share keeps rising a third year (+0.6pp or more over FY26's ~21.3%) | leading, 0.55 | 1H26 +2.4pp y/y; management's own language says marketing stays elevated into 2027 launches (claim 7); the line build's central case (21.86%) sits a hair under the bar, so anything above its +15%/+11% growth pair, or any revenue shortfall with costs at budget (claim 6), clears it |
| The ramp stops: marketing grows below revenue in 2027 (the Street's implied 20.5%, claim 5) | kept as the main No route (~0.35) | Management protected the FY24 floor by phasing brand marketing down (claim 10); Chesky's "90% direct or organic" and the 2021–23 record of S&M share falling; the F03 (a)/(b) branches carry this |
| A revenue shortfall (short case) raises the ratio mechanically | kept, 0.25 tail | Discretionary lines have not flexed within a year (claim 6); the short case gives 23–24% |
| Airbnb re-captions the line (field operations out of S&M) | discarded as a route (convention 3) | No precedent; the 10-K caption has been stable since the IPO |
| The line build's 21.86% is exactly the median and the question is a coin toss | discarded as the headline, kept as the floor of the interval | The line build's growth pair is management's stated deceleration taken at face value; the run's allocation (23.5%) and the 1H26 run-rate argue the centre is above 21.9 |
| Use the Street's FY27 EBITDA as management's plan | discarded | The Street's FY27 incremental margin 43.7% has no support in any management statement (claim 4) |

## 5. Independent Estimates
- base_rate_estimate: 0.55 — reference class "year-over-year change in the ex-SBC S&M share" (claim 1): rose ≥ +0.6pp in 2 of the last 4 years (2024, 2025) and is on course for +1.9pp in 2026 (claim 3); 3 of 5 including FY26E; the regime since 2024 is a rising share and the threshold needs only +0.6pp on FY26
- decomposition_estimate: 0.58 — Monte Carlo (claim 13): FY26 S&M $3,040M × (1 + N(14.5%, 5.5) + 0.3 × revenue-growth deviation) over FY27 revenue with a 25% short-case tail; ratio median 22.2%
- anchor_estimate: 0.30 — no market; the Street's FY27 EBITDA implies S&M ≈ 20.5% (claim 5), 1.4pp below the bar, i.e. P ≈ 0.10 on the Street's own sd; raised to 0.30 because the Street's S&M is a residual of an EBITDA panel, not a modelled line, and the Street's FY margin has sat above every February floor
- anchor_value: 0.30 (Street-implied FY27 S&M share 20.5%, LSEG FY27 EBITDA $5,766M n 44, 11 Sep 2026)
- final_estimate: 0.55 (credible interval 0.40–0.68)
- final_minus_anchor: +25 points. Justified independently: the anchor is the Street's FY27 margin, which the team's entire margin build disputes on this one line (claim 4); the base rate (share trend) and the decomposition (line build + management's language) agree at 0.55–0.58 without reference to the Street. The final is trimmed 3 points below the decomposition for the marketing-cut precedent (claim 10) and management's 68% kept rate on brand statements (claim 7)

## 6. Final Numbers
**Binary.** P(FY27 S&M ex-SBC ÷ FY27 revenue ≥ 21.9%, FY27 10-K) = **0.55**, credible interval **0.40–0.68**.
Ratio distribution (model): 5/10/25/50/75/90/95 = 20.1 / 20.6 / 21.3 / 22.2 / 23.0 / 23.9 / 24.4%.
**Conditional on the F03 (Feb 2027 FY27 margin guide) bucket** (model values shrunk 3 points toward the unconditional, coherent with the F03 vector: Σ P(F03) × P(F04 | F03) = 0.549):
| F03 bucket | P(S&M ≥ 21.9%) |
|---|---|
| (a) ≥36.5% floor or point | 0.25 |
| (b) 36.0–36.4% | 0.40 |
| (c) 35.5–35.9% | 0.52 |
| (d) <35.5%, down y/y, or investment year | 0.70 |
| (e) no numeric FY27 margin guidance | 0.55 |
Reading: a Feb 2027 floor at or above 36% is the signal that the marketing ramp is being reined in; a haircut floor or an investment-year framing is the signal that it is not.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/f04_model.py` from the base (0.581).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| FY27 S&M growth centred +14.5% (line build's +15% marketing / +11% field) | +10% (cost bull): 0.32; +20% (cost bear): 0.85; +22% (run allocation 23.5%): 0.91 |
| FY26 S&M ex-SBC $3,040M (2H26 marketing +25%) | $2,980M (2H26 +20%): 0.44; $3,100M (2H26 +30%): 0.71 |
| 25% short-case revenue tail | none: 0.53; 50%: 0.64 |
| Growth sd 5.5pp | 3: 0.61; 8: 0.56 |
| Cost flex to revenue β 0.30 | 0 (no flex): 0.59; 0.6: 0.56 |
| F03 outcome | (a) 0.28 / (b) 0.44 / (c) 0.58 / (d) 0.78 / (e) 0.62 (model, before the 3-point shrink) |

Pre-mortem ("it is February 2028 and the 10-K shows S&M ex-SBC at 20.8%"): (1) management declared 2027 a leverage year in February 2027 and grew marketing ~8% — the F03 (a)/(b) branch, priced at 0.25 jointly; (2) the 3Q26 $67M reconciliation step was a one-off and the FY26 base is $2,980M not $3,040M — priced at 0.44 in that row; (3) FY27 revenue printed +14% on a weak dollar while S&M grew +12% — inside the revenue draw (bull) with β; (4) a re-caption moved field operations out of S&M — not priced (convention 3). The opposite miss (24%+): the short case with costs at budget — 0.25 tail. Asymmetry: the memo's short case leans on rising S&M; at 0.55 it is "more likely than not, not a foundation", and the memo should lean on the F03-conditional reading instead.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.55 (0.40–0.68) and the F03-conditional table |
| 2026-11-05 | 3Q26 10-Q: S&M line and MD&A marketing/payroll split; any B03 sentence (marketing to grow below revenue / moderated) | 3Q26 S&M ex-SBC ≥ $800M (+37%): FY26 base → $3,100M, P +0.10; ≤ $740M: base → $2,980M, P −0.10; a B03 "moderation" sentence: −0.08 |
| 2027-02-11 | 4Q26 letter and 10-K: FY26 S&M ex-SBC and share; FY27 margin sentence (F03) | Re-base S26 to the print; apply the conditional row for the F03 outcome |
| 2027-05 / 2027-08 / 2027-11 | 1Q27, 2Q27, 3Q27 10-Qs: S&M y/y and MD&A drivers | Each quarter with S&M growth ≥ revenue growth + 3pts: +0.06; ≤ revenue growth: −0.08; by 3Q27 the 9M ratio pins the FY within ~0.4pp |
| 2028-02 (est.) | FY27 10-K | Resolve on the S&M line less S&M SBC ÷ revenue, unrounded |

RESUME: the next agent (audit response) should re-run `datasets/f04_model.py` (deterministic, ~5 s), verify claim 1–2 (the `sm_cash` construction) against the 10-K SBC-by-line table, and attack the two load-bearing choices: the FY27 S&M growth centre (+14.5%; the cost-bull +10% gives 0.32, the run's +22% gives 0.91) and the FY26 base ($3,040M). The F03 conditionals should be re-derived if the F03 vector changes after its audit.
