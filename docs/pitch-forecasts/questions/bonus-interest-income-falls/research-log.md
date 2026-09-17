# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A16). Companion questions: B08 `bonus-ai-hosting-cost-step`, B09 `bonus-sbc-step-up`, B17 `bonus-take-rate-guided-down`. Reused inputs: M7 below-EBITDA bridge (interest-income rule), C12 `q3-unearned-fees-yoy` (RNPL cash timing), R10 `risk-dollar-weakens` (the 16 Sep FOMC), R06 `risk-buyback-upsize` (cash draw). Reproduction: `datasets/b10_model.py` (numpy/pandas, seed 20260917, n 400,000, seconds) → `b10_results.csv`, `b10_history.csv`.

## 0. Metadata
- question_name: bonus-interest-income-falls
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B10)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will 4Q26 interest income be ≤ 90% of 4Q25's?
### Resolution Criteria
Yes if 4Q26 interest income ≤ 0.90 × 4Q25 interest income (4Q26 release / 10-K). Resolution ~11 Feb 2027.
### Fine Print
Mechanism: RNPL reduces funds held for clients; rates. Use M7's interest-income rule (0.876 × 3m T-bill × earning base) and the RNPL funds-held overlay.

Conventions adopted: (1) the object is the income-statement line "Interest income" for the three months ended 31 Dec 2026 as printed in the 4Q26 release (the reconciliation table prints it by quarter) or, failing that, FY26 10-K less nine months; the 4Q25 base is **$162M** as printed (FY25 $705M less 9M25 $543M; the 2Q26 letter's nine-quarter table: 226 207 183 173 190 180 162 155 183), so the threshold is **$145.8M**; (2) a restatement of 4Q25 in the 4Q26 release governs the base only if the release itself presents the comparative; (3) interest income is gross (interest expense, $37M/q on the March 2026 notes, is a separate line and does not enter); (4) if the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Interest income by quarter ($M): 1Q24 202, 2Q24 226, 3Q24 207, 4Q24 183, 1Q25 173, 2Q25 190, 3Q25 180, 4Q25 162, 1Q26 155, 2Q26 183; FY24 $818M, FY25 $705M (−14%, "due to lower interest rates, partially offset by higher investment balances"); 1H26 $338M vs $363M (−7%). Y/y: 4Q25 −11.5%, 1Q26 −10.4%, 2Q26 −3.7% — every ≥ 10% y/y decline since 2023 coincided with a y/y fall in the 3m T-bill of 15% or more | `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (interest_income); `data/raw/filings/abnb_10k_FY2025.htm` (MD&A Interest Income); `data/raw/letters/2Q26_d70413dex991.htm`; `datasets/b10_history.csv` | 2026-08-06 (last print) | 2026-09-17 | yes |
| 2 | Earning base: cash + short-term investments + restricted cash ($M) 3Q25 11,719, 4Q25 11,049, 1Q26 12,065, 2Q26 12,136; funds held on behalf of customers 3Q25 7,209, 4Q25 6,959, 1Q26 10,550, 2Q26 12,224 (y/y +9.7%, +17.3%, +15.0%, +10.5% against GBV +13.9%, +15.9%, +19.2%, +15.7% — the gap to GBV widened from −4 to −5 points as RNPL scaled, but the balance still grew double digits); the $2.5bn March 2026 notes lifted cash; buybacks $1,088M (1Q26) and $1,051M (2Q26); $3.4bn authorisation left at 30 Jun 2026 | `02_panel_quarterly.csv` (cash_and_investments_total, funds_held_on_behalf, buybacks_cash); `data/processed/overnight/02_kpi_panel_quarterly.csv` (funds_held_yoy_pct); `M7_parameter_sheet.csv` | 2026-08-06 | 2026-09-17 | yes |
| 3 | M7 rule: II = β × r × avg(cash + STI + restricted + funds held)/4 with β = 0.876 (recency-weighted realised ratio over the last 8 non-ZIRP quarters), r = 3m T-bill (FRED DTB3) quarter average; backtest MAE h=0 $17.9M (W1, n 14) / $10.5M (W2, n 10), h=1 $20.4 / $7.8, h=2 $25.3 / $11.9 (0.32–0.64× the seasonal naive; passes both windows); rate sensitivity ±100bp ≈ ±$49–55M a quarter; LIVE (vintage 11 Sep, T-bill 3.86 held flat): 3Q26 $184M (q10–q90 161–206), 4Q26 $170M (q10–q90 144–196); the line build's 4Q26 is $165M | `docs/margin-build/notes/M7_below_ebitda.md` (pre-registration, backtest, LIVE waterfall); `M7_parameter_sheet.csv`; `40_lines_quarterly.csv` (interest_income 4Q26 165.5) | 2026-09-14 / 2026-09-15 | 2026-09-17 | yes |
| 4 | Rule residuals (this log, `datasets/b10_history.csv`): realised β by quarter 2Q24 0.831, 3Q24 0.839, 4Q24 0.966, 1Q25 0.882, 2Q25 0.832, 3Q25 0.849, 4Q25 0.942, 1Q26 0.849, 2Q26 0.860; residual vs the 0.876 rule mean −0.4%, sd 5.6%; both Q4 residuals positive (+10.3%, +7.5%), i.e. the rule under-calls Q4 (the quarter-end funds-held balance understates the intra-quarter average after the Q3 peak) | computed from claims 1–3 | 2026-09-17 | 2026-09-17 | yes |
| 5 | Rates: FRED DTB3 quarter means 4Q25 3.726, 1Q26 3.594, 2Q26 3.624, 3Q26-to-date 3.749; daily 10 Sep 3.86, 11 Sep 3.92, 14 Sep 3.97, 15 Sep 3.97; DGS1 15 Sep 4.39; fed funds upper bound 3.75 through 16 Sep (DFEDTARU). FOMC 16 Sep 2026: unanimous +25bp to 3.75–4.00%, the first hike since 2023; "traders price three hikes through June 2027" (R10 claim 10) | `sources/fred_DTB3_20260917T082052Z.csv`, `fred_DGS1_…`, `fred_DFEDTARU_…` (https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3 etc.); `../risk-dollar-weakens/research-log.md` claim 10 | 2026-09-16 | 2026-09-17 | yes |
| 6 | Kalshi Fed markets (2026-09-17T08:21:21Z, yes bid/ask): KXFEDDECISION Oct 2026 hike 25bp 0.45/0.46, hold 0.55/0.57, cut ≤ 0.02; Dec 2026 hike 25bp 0.69/0.70, hold 0.29/0.30, cut ≤ 0.02; Jan 2027 hike 25bp 0.22/0.57, cut 25bp 0.09/0.10; KXFED Dec 2026 upper bound > 4.00% 0.82/0.83, > 4.25% 0.27/0.31, > 3.75% 0.98/0.99. Polymarket "Fed rate cut by October 2026" 0.0145, by January 2027 0.14, by March 2027 0.30 (volume fields mostly None; thin). Implied 4Q26 DTB3 average ≈ 4.05–4.20% (+9 to +13% y/y on 3.726) | `sources/kalshi_KXFEDDECISION_open_20260917T082121Z.json`; `sources/kalshi_KXFED_open_20260917T082121Z.json`; `sources/polymarket_search_fed_dec2026_20260917T082121Z.json` | 2026-09-17 | 2026-09-17 | yes |
| 7 | RNPL and the earning base: RNPL shifts guest payment closer to check-in, so funds held and unearned fees grow slower than GBV (C12: unpaid share u ≈ 15% at 2Q26 rising toward ~18% at 3Q26; the −3% unearned-fees row is a payment-timing read); the line build's short-case overlay is funds held −10% (`rnpl_share_shift_pts` 10, interest-income hit "$10–19M a quarter … below EBITDA"); 2Q26 10-Q: "Funds held on behalf of customers and amounts payable to customers do not impact FCF, except for interest earned on those funds" | `../q3-unearned-fees-yoy/research-log.md` §5–6; `40_params.csv`; `docs/margin-build/notes/40_line_build.md` (short case); `abnb_2026q2_10q.html` | 2026-09-17 / 2026-09-15 | 2026-09-17 | yes |
| 8 | Cash path: FY26 FCF $4.9–5.1bn (M7), seasonally 3Q ≈ $1.1–1.5bn and 4Q ≈ $0.7–0.9bn against buybacks ≈ $1.05bn/q, so 2H26 cash is roughly flat at ~$12bn absent an upsize; an extra $1.5bn / $3bn of buybacks in 2H26 would cut the average base by the same amount (−$14M / −$27M of quarterly interest at 4.1%); R06 (this run) prices the upsize | `M7_below_ebitda.md` LIVE waterfall (CFO/FCF rows); `M7_parameter_sheet.csv` (buyback_musd_q 1,027.75; authorisation $3.4bn) | 2026-09-14 | 2026-09-17 | yes |
| 9 | Monte Carlo (this log, `datasets/b10_model.py`): r N(4.10, 0.15), β N(0.88, 0.045), 3Q26/4Q26 cash N(12,100/12,000, 500), funds held = same quarter last year × (1 + N(12.7%, 3%)) × (1 − U(0, 10%)) RNPL overlay, residual 5%: 4Q26 interest income median **$177M** (+9% y/y), p10–p90 $158–196M, **P(≤ $145.8M) 0.014**. Sensitivities: rate 3.97 held (no more hikes) 0.023, 4.30 0.003, 3.25 (emergency cuts) 0.67; β 0.83 0.064, 0.94 (4Q25 realised) 0.001; funds held flat y/y 0.044; RNPL overlay 20% 0.027, 0 0.007; cash −$1.5bn 0.096, −$3bn 0.38, −$3bn and 3.97 0.53; residual 10% 0.066; all-bear joint 0.93. Mixture (base 0.88 / upsize $1.5bn 0.07 / upsize $3bn 0.03 / emergency cuts 0.02) → **0.043**. The average base needed at 4.10% and β 0.88 is $16.2bn (vs ~$19.7bn expected); the rate needed at the expected base is 3.37% | computed; `datasets/b10_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 10 | No market on Airbnb's interest income; the Fed markets above are the adjacent markets (2026-09-17T08:21:21Z) | `sources/` | 2026-09-17 | 2026-09-17 | no |
| 11 | Web pass (2 WebSearch calls attributable, one shared): CME FedWatch snippets (63.7% December hike; undated aggregator, zero weight — the Kalshi fetch is used instead); nothing on Airbnb cash or funds held | `sources/web_queries_2026-09-17.md` queries 1, 4 | 2026-09-17 | 2026-09-17 | no |
| 12 | Impact inputs: M7 FY27 interest income $765M, ETR 17.5%, 573m diluted shares; line-build sensitivity "3m T-bill +100bp → FY27 EPS +$0.28"; Street FY27 EPS $6.23 at 26.9× | `M7_below_ebitda_annual_forecasts.csv`; `40_sensitivities.csv`; `23_vs_consensus.csv` | 2026-09-14 / 2026-09-15 | 2026-09-17 | yes (impact only) |

Newest load-bearing source: the 16 Sep FOMC and the 17 Sep FRED/Kalshi pulls (0–1 days old against a 147-day window); the balance-sheet inputs are from the 2Q26 10-Q (42 days).

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; finished logs R05, C11, R04, C12, R01, F03, F04, R10 (grep "Fed|hike|FOMC")
2. [repo] `docs/margin-build/notes/M7_below_ebitda.md`; `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv`, `M7_interest_income_fit_history.csv`, `M7_below_ebitda_annual_forecasts.csv`; `40_params.csv` (below-EBITDA rows, rnpl_share_shift_pts), `40_lines_quarterly.csv` (interest_income)
3. [repo, pandas] `02_financial_panel/02_panel_quarterly.csv` (interest_income, cash_and_investments_total, funds_held_on_behalf, buybacks_cash); `02_kpi_panel_quarterly.csv` (funds_held_yoy_pct, cash_plus_st_investments_musd)
4. [repo, python] FY2025 10-K "Interest income" MD&A and "funds held on behalf"; 2Q26 10-Q "interest income", "funds held"; 4Q25 and 2Q26 letters' reconciliation rows (Interest income by quarter)
5. [FRED CSV] DTB3, DGS1, DFEDTARU → `sources/` (2026-09-17T08:20:52Z); quarter means computed
6. [Kalshi API] series KXFEDDECISION and KXFED open markets; [Polymarket public-search] "fed rate december 2026", "airbnb" → `sources/` (2026-09-17T08:21:21Z)
7. [WebSearch] Airbnb news (neutral recency pass, shared)
8. [WebSearch] fed funds futures December 2026 meeting probability after September hike CME FedWatch
9. [python] `datasets/b10_model.py` → `b10_results.csv`, `b10_history.csv`
10. [WebSearch, final 72-hour neutral recency check = query 7, 2026-09-17: nothing on cash, funds held or rates beyond the 16 Sep hike] — no change

WebSearch calls used by this question: 2 of 5 (one shared).

## 3. Leading Hypothesis Entities
Airbnb, interest income, funds held on behalf of customers, Reserve Now Pay Later, 3-month Treasury bill, Federal Reserve, Kevin Warsh, M7 below-EBITDA bridge, share repurchase

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Base regime: rates +9–13% y/y after the 16 Sep hike, earning base +6% y/y, interest income ≈ $175–180M (+9%) | leading (≈ 0.88 weight; P(Yes) 0.014 inside it) | claims 3–6: the rule is the best-validated line in the margin build, the T-bill is above its 4Q25 average and the base is larger |
| RNPL drains funds held enough to offset the rate | discarded as sufficient (overlay 20% → 0.027) | claim 2: funds held still +10.5% y/y at 2Q26 with RNPL at 20%+ of GBV; a −20% overlay is worth ≈ −$1.5bn of base ≈ −$14M, a fifth of the needed miss |
| A buyback upsize draws $1.5–3bn of cash in 2H26 | kept as the main tail (0.07 / 0.03 weights; 0.10 / 0.38 conditional) | claim 8: the $3.4bn authorisation is exhausted ~1Q27 at the current pace; an upsize is priced in R06; a $3bn extra draw alone gets the line to ~$150M and needs a second miss to cross |
| An emergency cutting cycle takes the T-bill to ~3.25% by Q4 | kept at 0.02 (Kalshi Oct/Dec cut ≤ 0.02; 0.67 conditional) | claim 6; the Fed hiked on 16 Sep and three more hikes are priced |
| The realised yield β falls (mix into non-USD funds held, EUR rates 2.5%) | inside β N(0.88, 0.045); 0.83 → 0.064 | β has ranged 0.83–0.97 over nine quarters and both Q4 readings were high (claim 4) |
| A presentation change (interest on funds held moved out of the line) | tail, unmodelled (~0.005) | no signal in the 2Q26 10-Q; adjusted EBITDA definition unchanged |
| Print date moves / restatement | no effect | conventions (1), (2), (4) |

## 5. Independent Estimates
- base_rate_estimate: 0.10 — reference class "quarters since 2023 with the 3m T-bill flat or up y/y" (2Q23–2Q24, n 6): interest income fell ≥ 10% y/y in 0 of 6 (Laplace 1/8 = 0.125); every ≥ 10% decline since 2023 (4Q24–1Q26, n 5) came with a ≥ 15% y/y fall in the T-bill (claim 1); 4Q26's T-bill is +9–13% y/y; trimmed to 0.10 for the small n
- decomposition_estimate: 0.04 — `datasets/b10_model.py` mixture (claim 9): base regime 0.014, plus the buyback-upsize and emergency-cut tails → 0.043
- anchor_estimate: 0.11 — no market prices the line; the designated anchor is the repo's registered M7 LIVE quantile for 4Q26 (vintage 2026-09-11: point $170M, q10 $144M), which puts P(≤ $145.8M) ≈ 0.11; the adjacent Fed markets (claim 6) price a cut by December at ≤ 0.02
- anchor_value: 0.11 (M7 `below-ebitda` LIVE 4Q26 q10–q90 144–196, vintage 2026-09-11, T-bill 3.86 held flat, before the 16 Sep hike)
- final_estimate: 0.05 (credible interval 0.02–0.10)
- final_minus_anchor: −6 points. NOT_INDEPENDENTLY_DERIVED flag raised by the arithmetic and answered: M7's band is built on the h=2 Gaussian pool with cov80 = 1.00 ("honest but conservative") and pre-dates the hike (+25bp ≈ +$11M on the point); the decomposition re-centres on the post-hike path and lands at 0.04; the final is the decomposition rounded up for the unmodelled presentation and joint-tail risks.

## 6. Final Numbers
**Binary.** P(4Q26 interest income ≤ 90% of 4Q25's $162M, i.e. ≤ $145.8M) = **0.05**, credible interval **0.02–0.10**.
Companion: 4Q26 interest income median ≈ $177M (+9% y/y), p10–p90 $158–196M; P(≤ $162M, any y/y decline) ≈ 0.13; P(≥ $190M) ≈ 0.20.
Extreme-probability gate (≤ 5%): triggered and audited. (1) Criteria re-read: "≤ 0.90 × 4Q25 interest income (4Q26 release / 10-K)". (2) Edge cases and residuals: a restated or re-presented 4Q25 comparative (e.g. interest on funds held reclassified into "other income") — 0.005; a release that prints only the FY line, forcing FY26-less-9M with a rounding cell of ±$1M — no effect at this distance from the threshold; a 4Q25 base read as $183M (4Q24) or $155M (1Q26) by a resolver — excluded by convention (1); an accounting change under which RNPL-related funds are no longer held by Airbnb (a third-party payment partner) — 0.005 (nothing disclosed); an emergency easing cycle (priced 0.02 × 0.67); a buyback upsize of ≥ $3bn in 2H26 combined with a lower yield (priced 0.03 × 0.38). (3) Sum of residuals ≈ 0.04–0.05. (4) The extreme number is confirmed at 0.05, not lower, because the two priced tails are real and correlated with a falling stock (the short's own scenario).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| 4Q26 T-bill average 4.10 ± 0.15 (one more hike likely) | 3.97 held flat (no more hikes): 0.05; 4.30: 0.03; 3.25 (emergency cuts as the base case): 0.60 |
| Realised yield β 0.88 ± 0.045 | 0.83: 0.09; 0.94 (4Q25 realised): 0.03 |
| Funds held +12.7% y/y less a 0–10% RNPL overlay | flat y/y: 0.07; overlay 0–20%: 0.06; no overlay: 0.04 |
| Cash + STI ≈ $12bn through 2H26 | −$1.5bn (moderate buyback upsize): 0.12; −$3bn: 0.35 |
| Tail weights 0.07 / 0.03 / 0.02 (upsize $1.5bn / $3bn / emergency cuts) | doubled: 0.08; zero: 0.02 |
| Residual sd 5% | 10%: 0.09 |

Pre-mortem ("it is 11 Feb 2027 and 4Q26 interest income printed ≤ $145.8M"): (1) management upsized the buyback after a post-print sell-off and spent $4–5bn in 2H26 on a $130 stock, cutting the corporate cash base by ~$3bn — priced at 0.03 × 0.38 and correlated with the short's own scenario (the memo should note that its own success raises this item); (2) the Fed reversed into cuts after a growth scare (Kalshi: ≤ 0.02 by December) — priced; (3) RNPL and a slower Q4 booking season left funds held flat or down y/y while the yield mix fell — 0.07 × 0.09 in the joint; (4) a presentation change moved interest on customer funds out of the line (0.005). "It printed $175–185M": the modal outcome. Asymmetry: this is a bonus item whose mechanism (RNPL) is real but too small against a rising rate; an over-stated number would put a wrong-signed macro claim in the memo, so the log keeps 0.05 and says the item is immaterial.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo due | Quote 0.05 (0.02–0.10); immaterial, drop from the memo body; note the sign: rates are now a tailwind to interest income |
| 2026-10-28 | FOMC | a hike → 0.04; a hold → 0.05; a cut → 0.15 |
| 2026-11-05 (after close) | 3Q26 release: interest income (M7 $184M, q10–q90 161–206), cash + STI, funds held at 30 Sep, buybacks in Q3, any authorisation increase | 3Q26 ≤ $165M → 0.10; funds held y/y ≤ +5% → +0.02; a new ≥ $6bn authorisation with accelerated pace → +0.05 |
| 2026-12-09 | FOMC (with SEP) | a second hike → 0.03; a cut → 0.20 |
| 2027-01-27 | FOMC | last catalyst inside the window |
| ~2027-02-11 | 4Q26 release: interest income line and the year-end balance sheet | resolve; audit read: a 3Q26 line ≤ $165M with funds held ≤ +5% y/y should have put the pre-print P near 0.15 |

## 9. Impact
If the event happens (4Q26 interest income ≤ $145.8M, taken at $145M against the team path's $165M, −$20M; FY27 run-rate −$90M against M7's $765M):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a below-EBITDA line |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 | — |
| FY27 revenue ($M) | 0 | — |
| FY26 adj. EBITDA margin (pp) | 0 | interest income is excluded from adjusted EBITDA |
| FY27 adj. EBITDA margin (pp) | 0 | — |
| FY27 EPS ($) | −0.13 | −$90M × (1 − 0.175) / 573m shares (the line-build sensitivity: ±100bp of T-bill ≈ ±$0.28 of FY27 EPS); 4Q26 EPS −$0.03 |
| Stock ($/share) | −2 | interest income carries a low multiple (a cash-yield line); −$0.13 at ~15× ≈ −$2 |
| **EV = P × stock** | **0.05 × −$2 ≈ −$0.1/share** | **Immaterial** (< $1/share): drop from the memo; if the RNPL cash-timing point is made, make it on unearned fees (C12), not on interest income, where rates dominate and are now a tailwind |

RESUME: the next agent (audit response) should re-run `datasets/b10_model.py` (seconds), check claim 1's interest-income series against the 2Q26 letter's nine-quarter table (4Q25 $162M) and the 4Q26 rate path against a fresh Kalshi/FRED pull after the 28 Oct FOMC, and challenge the tail weights in §5 (the buyback-upsize branch is the only route to Yes that does not need a Fed reversal; align its weight with R06's final number). The item is immaterial at any P below ~0.5.
