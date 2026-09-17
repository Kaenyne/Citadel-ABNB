# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A13 with R12 and R14). Reproduction: `datasets/marketbeat_history.py` (pandas; needs the saved MarketBeat HTML in `sources/`) then `datasets/r13_model.py` (numpy/pandas, seed 20260917, 300,000 paths per simulation, ~60 s). A previous attempt at this batch was cut off before writing; its data pulls and history extension were re-run and checked; the model was rebuilt from the fresh 31 Aug reading.

## 0. Metadata
- question_name: risk-short-interest-crowding
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R13)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-01-15
- resolution_date: 2027-01-15
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will ABNB short interest exceed 5.0% of shares outstanding at any Nasdaq settlement date between 30 Sep 2026 and 15 Jan 2027?
### Resolution Criteria
Yes if any settlement-date short interest ÷ shares outstanding ≥ 0.05 (Nasdaq/MarketBeat series as in `data/processed/overnight/09_short_interest.csv`). Resolution 15 Jan 2027 (data lag allowed).
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted: (1) settlements in the window: 30 Sep, 15 Oct, 30 Oct, 13 Nov (15 Nov is a Sunday; FINRA uses the prior business day), 30 Nov, 15 Dec, 31 Dec, 15 Jan — eight readings, published by Nasdaq/FINRA about eight business days after each settlement, the last around 27 Jan 2027 (the "data lag allowed" clause); (2) numerator = the Nasdaq-reported short interest in shares (`api.nasdaq.com/api/quote/ABNB/short-interest`, the series the repo file cross-checks against); (3) denominator = basic shares outstanding, Class A plus Class B, as the repo file uses (`shares_out_m` from `abnb_capital_return_quarterly.csv`; 592m at the latest row), updated to the 10-Q cover count nearest each settlement — the threshold is therefore ≈29.5–29.6m shares; (4) the "% of float" figures shown by MarketBeat, Yahoo and Finviz (float ≈406m Class A) are NOT the object; under that basis the threshold would be ≈20.3m shares (3.43% of total shares) and the answer would differ materially — reported in §6 as a sensitivity; (5) "exceed 5.0%" and "≥ 0.05" are read together as ≥ 5.00% on the rounded percentage; (6) a share count change from buybacks (≈1% per quarter) moves the threshold by <0.3m shares and is ignored.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Latest Nasdaq settlement 31 Aug 2026: 14,228,547 shares short, average daily volume 4,747,241, days to cover 3.0; prior 14 Aug 12,860,433, 31 Jul 12,914,119, 15 Jul 13,994,933; the 15 Sep settlement is not yet published. On 592m basic shares the latest is 2.40%; yfinance `sharesPercentSharesOut` 2.41% (same basis), `shortPercentOfFloat` 3.44% (float 405.8m), Class A count 419.5m, implied total 598.8m | `sources/nasdaq_short_interest_20260917T080127Z.json` (https://api.nasdaq.com/api/quote/ABNB/short-interest?assetclass=stocks); `sources/yfinance_info_short_20260917T035213Z.json` | 2026-09-17 | 2026-09-17 | yes |
| 2 | Repo series: 84 settlements 28 Feb 2023 – 14 Aug 2026, % of basic shares: mean 2.84, median 2.66, min 1.74, max 5.44 (30 Sep 2023), latest 2.17 (14 Aug); one reading ≥5, three ≥4.5 (30 Sep, 15 Oct, 31 Oct 2023). Positioning tests: SI level vs forward 3-month excess return r 0.15 (n 78, p 0.18), change r −0.08 / +0.04; "no short squeeze left to harvest and no crowded-short signal" | `data/processed/overnight/09_positioning_short_interest.csv`; `data/processed/reverse_dcf/D/D_positioning_summary.csv`; `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 item 9, "Short interest" paragraph | 2026-09-06 / 2026-09-12 | 2026-09-17 | yes |
| 3 | Extended series (MarketBeat dollar series ÷ settlement-date close ÷ basic shares; calibrated 1.00 on the 84 overlapping settlements): 100 settlements 30 Sep 2021 – 31 Aug 2026 incl. the Nasdaq 31 Aug row; mean 2.76, max 5.44, min 1.48 (30 Apr 2022); 2022 max 3.50 (15 Jul 2022), 2022 mean 2.41; the latest 2.40 is the 34th percentile. Local peaks ≥3.3: Jul 2022 3.50, Dec 2022 3.34, Jan 2023 3.49, Jun 2023 4.04, Sep 2023 5.44, Sep 2025 3.53 — six episodes in five years, one at 5 | `datasets/si_history_2022_2026.csv` (`marketbeat_history.py`); `datasets/r13_summary.json` | 2026-09-17 | 2026-09-17 | yes |
| 4 | Eight-settlement window maxima (n 92 windows with a known prior level): P(max ≥ 5.0) 0.087 (8 windows, start dates 15 Jun – 30 Sep 2023: one episode), P(≥4.5) 0.109, P(≥4.0) 0.185, P(≥3.5) 0.37; largest rise from the prior level inside a window 2.34pt (p90 1.58) against the 2.60pt now needed (0 of 92). Conditional on a prior level < 2.5 (n 42): P(≥5) 0, P(≥4.5) 0, P(≥4) 0.024 (max 4.04); < 3.0 (n 61): 0 / 0 / 0.049. 2023+ windows (n 62): P(≥5) 0.129 | `datasets/si_window_max.csv`; `r13_summary.json` windows_* | 2026-09-17 | 2026-09-17 | yes |
| 5 | The 5.44% peak is the S&P 500 inclusion: announced after the close on Fri 1 Sep 2023 (+7.1% abnormal on 5 Sep, t 2.7), effective 18 Sep 2023 (−0.1%), the following 20 sessions −9.7%; short interest 31 Aug 3.10% → 15 Sep 4.04% (+0.94) → 30 Sep 5.44% (+1.40, 34.8m shares) → 15 Oct 4.70 → 31 Oct 4.56 → 15 Nov 3.91 → 31 Dec 3.00. These are the only two single-step rises ≥0.9pt in 99 steps (per-step sd 0.31, p95 0.43). "Index inclusion is a pre-effective-date event ... classic index-demand front-run and unwind" | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 item 6 and the event table; `data/processed/abnb_big_moves_7pct.csv` row 33; `datasets/r13_summary.json` changes | 2026-09-06 | 2026-09-17 | yes |
| 6 | Structural short sources: the $2.0bn 0% convertible senior notes due March 2026 "matured in March 2026" (1Q26 letter) and are "fully settled; no dilution left to model" (M7 note); they were repaid from a $2.5bn straight senior-note offering (4.400% 2029, 4.650% 2031, 5.250% 2036; prospectus supplement 12 Mar 2026) — no new convertible, hence no new arbitrage hedge short. Short interest fell from 17.9m (31 Dec 2025) through 16.9m (15 Jan), 15.2m (13 Feb), 14.4m (31 Mar) to 12.9m (31 Jul) over the redemption. ABNB is an S&P 500 (Sep 2023) and Nasdaq-100 member; no inclusion event is scheduled | `data/raw/letters/1Q26_d23351dex991.htm`; `docs/margin-build/notes/M7_below_ebitda.md` line 207; https://www.sec.gov/Archives/edgar/data/1559720/000119312526106418/d107518d424b2.htm (`sources/web_search_log.md`); `data/processed/overnight/09_short_interest.csv` | 2026-03-12 to 2026-05 | 2026-09-17 | yes |
| 7 | AR(1) in levels on the 100-settlement series: slope 0.906, long-run mean 2.78, residual sd 0.31; simulated from 2.40 with one unobserved step (15 Sep) then the eight window settlements, bootstrapped residuals: P(max ≥5) 0.005, P(≥4.5) 0.019, P(≥4) 0.068, P(≥3.5) 0.175; median max 2.90, p90 3.81, p99 4.75, p99.9 5.54. Fitted on 2024+ only (resid sd 0.20, long-run mean 2.47): P(≥5) 0.0000, P(≥4) 0.0003. Fitted 2023+: P(≥5) 0.008 | `datasets/r13_summary.json` ar1_* (`r13_model.py`) | 2026-09-17 | 2026-09-17 | yes |
| 8 | Jump and overlay variants: jump probability 2/99 per step, size U(0.9, 1.5): P(≥5) 0.018; jump probability doubled 0.036; jump size U(1.5, 2.5) 0.057; jump plus a down-print overlay (P 0.41 = S01 P(day-1 ≤ −5%), +0.7pt spread over the 13 Nov and 30 Nov settlements) **0.030**; overlay +1.5pt 0.080. Post-print history (short interest over the three settlements after each print vs the last before): down ≤−5% prints (n 6) mean max rise +0.35pt, largest +0.70 (1Q23); up ≥+5% prints +0.17; small prints +0.03 | `datasets/r13_summary.json` ar1_full_jump*, si_after_prints; `datasets/si_after_prints.csv` | 2026-09-17 | 2026-09-17 | yes |
| 9 | Alternative basis: on the ~406m float the latest reading is 3.51%; a 5.0%-of-float threshold is 20.3m shares = 3.43% of total shares, exceeded by the series on 15 Sep 2025 (21.69m), 30 Sep 2025 (21.17m) and through most of 2023; AR(1)+jump simulations give P(max ≥ 3.43) 0.20–0.40 | `datasets/r13_summary.json` alt_basis_*, P(max>=3.43_float_basis_equiv) | 2026-09-17 | 2026-09-17 | yes |
| 10 | Web (17 Sep): Yahoo 22 Aug "Short interest sits at just 3.39% of float as of mid-August"; no report of a September positioning change; no market on short interest on Kalshi or Polymarket | `sources/web_search_log.md` | 2026-08-22 / 2026-09-17 | 2026-09-17 | no |
| 11 | S01: P(5 Nov day-1 ≤ −5%) 0.41, ≤ −8% 0.29; the memo's short case; a down print is the only dated mechanism in the window that has historically raised short interest | `../day1-move-5nov/forecasts/2026-09-17-forecast.json` | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the Nasdaq pull (17 Sep, same day) and the computed tables; the series' last observation (31 Aug) is 17 days old but is the latest published reading (next publication ~24 Sep, monitoring row 1). Within the rule: no newer data exists.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and format references, example log; finished logs S01, S02, S04, R01
2. [repo] `data/processed/overnight/09_short_interest.csv`, `09_positioning_short_interest.csv` (all rows); `data/processed/reverse_dcf/D/D_positioning_summary.csv`; `research/notes/overnight/09_stock-behaviour-and-alpha.md` (grep "short interest", §1 items 6 and 9, event table)
3. [repo] grep "S&P 500 / index inclusion" in `research/notes/2026-09-05_abnb-major-moves.md`, `data/processed/abnb_big_moves_7pct.csv`; grep "convertible" in letters, `docs/margin-build/notes/M7_below_ebitda.md`
4. [Nasdaq API] short-interest table, pulled 03:52Z (earlier attempt) and 08:01Z (this run), saved
5. [yfinance] `info` short-interest keys (earlier attempt, 03:52Z, saved)
6. [MarketBeat] short-interest page saved (earlier attempt); `datasets/marketbeat_history.py` re-run: calibration and the 2021–2023 extension checked
7. [computed] `datasets/si_base_rates.py` (earlier attempt, 84-settlement file: windows 8/77, start<2.5 0/27, AR(1) 0.0045) — superseded by `r13_model.py` on the 100-settlement series with the 31 Aug reading
8. [computed] `datasets/r13_model.py` → `r13_summary.json`, `si_window_max.csv`, `si_after_prints.csv`
9. WebSearch: Airbnb short interest September 2026
10. WebFetch: SEC 424B2 (12 Mar 2026 senior notes) — confirms straight debt, 2026 converts repaid
11. WebFetch: finance.yahoo.com 22 Aug article (short interest 3.39% of float mid-August; shared with R12)
12. WebSearch: Airbnb news past 3 days (batch-level final 72-hour neutral recency check, charged to R14: nothing on positioning; no change)

WebSearch calls charged to R13: 1 (query 9); batch total 3 of 15.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, Nasdaq short interest, FINRA settlement dates, S&P 500 inclusion September 2023, 2026 convertible notes, 5 Nov 2026 print, MarketBeat, basic shares outstanding

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Unconditional window base rate 0.087–0.129 taken at face value | discarded as the point | all eight qualifying windows are one episode (claim 4) driven by an index-inclusion hedge (claim 5); the regime-conditioned rate (start < 3.0%, no inclusion event, converts gone) is 0 of 61 windows |
| "% of float" basis (Yahoo/MarketBeat display) | discarded for the object; reported | the question names the repo file, which uses basic shares outstanding; under the float basis the threshold is 20.3m shares and P ≈ 0.20–0.30 (claim 9) — the single biggest resolution risk, fenced in the extreme-probability audit |
| A down 5 Nov print drives shorts to 5% | kept as an overlay (+0.7pt, P 0.41) | the largest post-down-print rise in six cases is +0.70pt; even +1.5pt (twice the record) gives 0.08; 5% needs +2.6pt |
| A new convertible or exchangeable issue creates a hedge short | tail, inside the jump term | the March 2026 refinancing was straight debt; $9.6bn net cash; no filing; a $2bn convert would add ~5–8m shares (≈1pt), not 15m |
| Index event (S&P/Nasdaq-100 reweight, a new index) | tail | already a member of both; quarterly rebalances did not move the series in 2024–26 |
| Convert the AR(1) into a log model or a regime-switching model | not done | the level AR(1) with bootstrapped residuals already reproduces the empirical p99 (4.75 vs the series' 4.70 second-highest reading); the jump variant covers the one out-of-model episode |
| Team's own short adds to the count | ignored | a student pitch has no position |

## 5. Independent Estimates
- base_rate_estimate: 0.06 — six local peaks ≥3.3% in 60 months (claim 3) → P(a peak episode inside a 4.5-month window) ≈ 0.4; P(peak ≥ 5 | episode) 1 of 6, or 0 of 5 once the index-inclusion episode is excluded as a non-recurring driver (Laplace 1/7); 0.4 × 0.14 ≈ 0.06; the raw unconditional window rate 0.087 and the conditional 0/61 bracket it
- decomposition_estimate: 0.03 — AR(1) from 2.40% with bootstrapped residuals (0.005) plus the calibrated jump term (0.018) plus the down-print overlay at S01's P(≤ −5%) (0.030; claim 8)
- anchor_estimate: 0.01 — no tradable market (claim 10); the repo prior is the 09 note's positioning judgement ("no short squeeze left to harvest", claim 2) and the earlier attempt's AR(1) on the 84-settlement file (0.0045); read as ≈0.01
- anchor_value: n/a (no market); repo prior ≈ 0.01 (09 note 2026-09-06; AR(1) 2026-09-17)
- final_estimate: **0.03** (credible interval 0.01–0.08)
- final_minus_anchor: +0.02. NOT_INDEPENDENTLY_DERIVED does not apply in substance: the final is the decomposition (0.03) pulled slightly toward the episode base rate (0.06) and the interval's top (0.08) is the "overlay twice the record" case; the agreement with the repo prior in level is because both rest on the same series, not deference

## 6. Final Numbers
P(short interest ≥ 5.0% of basic shares outstanding at any of the eight settlements 30 Sep 2026 – 15 Jan 2027) = **0.03**, credible interval **0.01–0.08**.
Companion numbers on the same basis: P(max ≥ 4.0%) ≈ 0.13–0.18; P(max ≥ 3.5%) ≈ 0.27–0.37; the window maximum's median ≈ 3.0%, p90 ≈ 4.1%.
Alternative basis (5% of the ~406m float = 20.3m shares = 3.43% of total shares): P ≈ 0.25 (0.20–0.40 across the simulation variants) — quoted only if the resolver adopts the float basis.
Conditional on a 5 Nov day-1 ≤ −5%: ≈ 0.05; on a day-1 ≥ +5%: ≈ 0.015.

Extreme-probability gate (triggered, P ≤ 5%). Resolution-criteria audit: (1) criteria re-read: "exceed 5.0% of shares outstanding at any Nasdaq settlement date between 30 Sep 2026 and 15 Jan 2027", "Nasdaq/MarketBeat series as in `09_short_interest.csv`", "data lag allowed". (2) Edge cases: (a) denominator basis — the repo file divides by basic total shares; MarketBeat's page headline is "% of float" (~406m); if a resolver uses the float, Yes becomes ≈0.25: this is the dominant edge, fenced by convention (3)–(4) and carried in the interval's top; residual assigned 0.01 (the orchestrator reads the repo convention); (b) a restatement of shares outstanding (10-Q cover count) — ±1%, immaterial; (c) Nasdaq's series revised after publication — has not happened in the cross-checked rows since Sep 2025; residual 0.002; (d) a 13 Nov vs 15 Nov settlement-date labelling difference — no effect; (e) an unscheduled structural event (new convertible, index change, M&A with a stock component) — inside the jump term, ≈0.01; (f) the 15 Jan reading published after the question's resolution date — allowed by the fine print. (3) Residuals sum to ≈0.02 on top of the model's 0.03 → the interval top 0.08 and the point 0.03 are confirmed; the point is not taken below 0.02 because of edge (a).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Jump term calibrated to 2 rises ≥0.9pt in 99 steps, size U(0.9, 1.5) | no jump term: 0.005; jump probability doubled: 0.036; size U(1.5, 2.5): 0.057 |
| Down-print overlay +0.7pt at P 0.41 | none: 0.018; +1.5pt (twice the historical maximum): 0.080 |
| AR(1) fitted on the full 2021–26 series (resid sd 0.31) | 2024+ fit (resid sd 0.20): ≈ 0.000; 2023+ fit: 0.008 |
| Starting level 2.40% (31 Aug) | if the 15 Sep reading prints 3.0%: ≈ 0.06; 2.0%: ≈ 0.02 |
| Denominator basic shares (592m) | float basis (406m): ≈ 0.25 |
| Episode base rate excludes the index-inclusion episode | included at full weight (1 of 6 peaks): base rate 0.07, final unchanged |

Pre-mortem ("it is 27 Jan 2027, the 15 Jan reading is out, and I was wrong"): (1) **A convertible or exchangeable issue in Q4** — Airbnb refinanced with straight debt in March and holds $9.6bn net cash; a $2bn convert would add roughly a point, and the arbitrage hedge alone cannot reach 5%; priced inside the jump term. (2) **A dedicated short campaign after a bad 5 Nov print** (an "RNPL is a receivables problem" note going viral) — the 2Q24 and 1Q23 down prints, the two worst in the sample, added 0.5–0.7pt; reaching 5% needs four times that; priced at 0.08 in the "twice the record" row. (3) **Merger-arbitrage or index-arb flow from an acquisition announced with stock** — no deal reported; founder-controlled; tail. (4) **The resolver used the float basis** — the audit's edge (a); the log states the basis and the alternative number so the memo cannot be caught by it. (5) **Nasdaq changes its reporting basis or misses a settlement** — "data lag allowed"; no residual beyond 0.002. Asymmetry: a confident No that resolves Yes on the stated basis would coincide with a squeeze-risk regime the memo would want to know about; the interval's top holds the structural-event case.

## 8. Monitoring Calendar
Update procedure: after each Nasdaq publication, re-run `datasets/r13_model.py` with the new reading appended (change `latest_shares` and the window count); hazard decay is mechanical — with each settlement that prints below 3.0%, the remaining window shortens and P falls.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| ~2026-09-24 | 15 Sep settlement published (pre-window) | ≤ 2.6%: 0.025; 3.0–3.4%: 0.06; ≥ 3.5%: 0.12 |
| 2026-10-02 | prelim memo due | quote 0.03 (0.01–0.08); state the basis; drop the item as immaterial |
| ~2026-10-09 | 30 Sep settlement (first in-window) | ≤ 2.8%: 0.02; ≥ 3.5%: 0.10; ≥ 4.0%: 0.25 |
| ~2026-10-26, 11-10 | 15 Oct, 30 Oct settlements (pre-print) | same ladder; each reading ≤ 3.0% with fewer settlements left: −0.005 |
| 2026-11-05/06 | 3Q26 print | day-1 ≤ −5%: 0.05; ≥ +5%: 0.015 |
| ~2026-11-24, 12-09 | 13 Nov, 30 Nov settlements (post-print) | the historical post-down-print rise is in by 30 Nov; reading ≤ 3.5%: 0.01; ≥ 4.2%: 0.20 |
| ~2026-12-24, 2027-01-12 | 15 Dec, 31 Dec settlements | ≤ 3.5%: 0.005 (one settlement left; a +1.5pt single step has happened once in 99) |
| ~2027-01-27 | 15 Jan settlement published | resolve |

## 9. Impact
If R13 resolves Yes (short interest ≥5% of shares, ≈29.6m shares, six days to cover at current volume):

| Item | Delta if R13 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | positioning has no operating content |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 | — |
| FY27 revenue ($M) | 0 | — |
| FY26 / FY27 adj. EBITDA margin (pp) | 0 / 0 | — |
| FY27 EPS ($) | 0 | — |
| Stock ($/share) | **+$3** (judgement): a crowded short widens the right tail on an accelerating print — with 29.6m shares short against 4.7m average daily volume, covering into a +5% day adds an estimated 2–3 points on that branch (P 0.24), i.e. ≈ +$1 unconditional at $167.5; the level itself has no forward-return content (r 0.15, p 0.18, claim 2); the 2Q26 +17.4% squeeze-like day happened at 2.4% short interest, so crowding is not required for the right tail already in S01 | claim 1 (days to cover), claim 2, S01 |
| **EV = P × impact** | 0.03 × $3 = **$0.09/share** | |
| Materiality | **Immaterial** (well under $1/share). The memo can drop "short-interest crowding" as a price risk. The residual consequence is trade-level, not price: at 5% the borrow fee and recall risk rise and the team's short is one of many | |

## RESUME
The next agent (audit response) should re-run `datasets/marketbeat_history.py` (needs `sources/marketbeat_short_interest_20260917.html`) and `datasets/r13_model.py` (deterministic, ~60 s) and attack: (1) the denominator convention — confirm with the orchestrator that "shares outstanding" means the repo file's basic count (592m), because the float basis flips the answer to ≈0.25; (2) the jump calibration (2 of 99 steps, both from one 2023 episode) and whether a Poisson jump per step is the right shape for an episode that lasted two settlements; (3) the down-print overlay (+0.7pt at P 0.41) against `si_after_prints.csv` (n 6 down prints, max +0.70). By ~24 Sep the 15 Sep settlement will be out: append it and re-run before anything else.
