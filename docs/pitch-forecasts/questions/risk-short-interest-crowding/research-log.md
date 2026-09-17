# RESEARCH LOG

Revision 2 (2026-09-17, audit-response revision of the 2026-09-17 initial forecast, Fable 5.1, batch A13 with R12 and R14; responds to `docs/pitch-forecasts/audits/A13-research-audit.md`, response in `audits/A13-audit-response.md`). Reproduction: `datasets/marketbeat_history.py` (pandas; needs the saved MarketBeat HTML in `sources/`; unchanged) then `datasets/r13_model_v2.py` (numpy/pandas, seed 20260917, 300,000 paths per simulation, ~60 s; outputs `r13_v2_summary.json`, `r13_v2_stdout.txt`). Revision 1's `r13_model.py` and its outputs (`r13_summary.json`, `si_window_max.csv`, `si_after_prints.csv`) are left untouched; revision 2 reads `si_after_prints.csv` from it. What changed: the decomposition is restated without the jump double count and with the mean rather than the maximum post-down-print overlay, at S01 revision 2's down-print probability; the headline moves from 0.03 to 0.02 and its stated derivation is now the one doing the work (§10).

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
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will ABNB short interest exceed 5.0% of shares outstanding at any Nasdaq settlement date between 30 Sep 2026 and 15 Jan 2027?
### Resolution Criteria
Yes if any settlement-date short interest ÷ shares outstanding ≥ 0.05 (Nasdaq/MarketBeat series as in `data/processed/overnight/09_short_interest.csv`). Resolution 15 Jan 2027 (data lag allowed).
### Fine Print
(none in the registry beyond the resolution sentence)

Conventions adopted: (1) settlements in the window: 30 Sep, 15 Oct, 30 Oct, 13 Nov (15 Nov is a Sunday; FINRA uses the prior business day), 30 Nov, 15 Dec, 31 Dec, 15 Jan — eight readings, published by Nasdaq/FINRA about eight business days after each settlement, the last around 27 Jan 2027 (the "data lag allowed" clause); (2) numerator = the Nasdaq-reported short interest in shares (`api.nasdaq.com/api/quote/ABNB/short-interest`, the series the repo file cross-checks against); (3) denominator = the repo file's share count, which is the **basic weighted-average** share count (`basic_wa_shares_m` in `data/processed/abnb_capital_return_quarterly.csv`, 592.0m at 2Q26; the 09 note says "converted to % of shares outstanding using basic weighted-average shares"), updated to the latest quarter's figure at each settlement — the threshold is therefore 29.6m shares; the alternative **shares-outstanding** count (yfinance `impliedSharesOutstanding` 598.786m, Class A 419.5m plus Class B) puts the threshold at 29.94m shares and the latest reading at 2.376% rather than 2.403% — a 0.34m-share difference that changes nothing below (A13-19); (4) the "% of float" figures shown by MarketBeat, Yahoo and Finviz (float ≈406m Class A) are NOT the object; under that basis the threshold would be ≈20.3m shares (3.43% of total shares) and the answer would differ materially — reported in §6 as a sensitivity; (5) "exceed 5.0%" and "≥ 0.05" are read together as ≥ 5.00% on the rounded percentage; (6) a share count change from buybacks (≈1% per quarter) moves the threshold by <0.3m shares and is ignored.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Latest Nasdaq settlement 31 Aug 2026: 14,228,547 shares short, average daily volume 4,747,241, days to cover 3.0; prior 14 Aug 12,860,433, 31 Jul 12,914,119, 15 Jul 13,994,933; the 15 Sep settlement is not yet published. On 592.0m basic weighted-average shares the latest is 2.403% (2.376% on 598.786m outstanding); yfinance `sharesPercentSharesOut` 0.0241 (same basis, rounding). **Float basis, computed: `sharesShort` 14,228,547 / `floatShares` 405,782,346 = 3.51%**; yfinance's own `shortPercentOfFloat` field reads 0.0344, which is not reproducible from its own two inputs and is not used (A13-20). Class A count 419.5m, `impliedSharesOutstanding` 598.8m | `sources/nasdaq_short_interest_20260917T080127Z.json` (https://api.nasdaq.com/api/quote/ABNB/short-interest?assetclass=stocks); `sources/yfinance_info_short_20260917T035213Z.json` | 2026-09-17 | 2026-09-17 | yes |
| 2 | Repo series: 84 settlements 28 Feb 2023 – 14 Aug 2026, % of basic weighted-average shares: mean 2.84, median 2.66, min 1.74, max 5.44 (30 Sep 2023), latest 2.17 (14 Aug); one reading ≥5, three ≥4.5 (30 Sep, 15 Oct, 31 Oct 2023). Positioning tests: SI level vs forward 3-month excess return r 0.15 (n 78, p 0.18), change r −0.08 / +0.04; "no short squeeze left to harvest and no crowded-short signal" | `data/processed/overnight/09_positioning_short_interest.csv`; `data/processed/reverse_dcf/D/D_positioning_summary.csv`; `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 item 9, "Short interest" paragraph | 2026-09-06 / 2026-09-12 | 2026-09-17 | yes |
| 3 | Extended series (MarketBeat dollar series ÷ settlement-date close ÷ basic shares; calibrated against the repo file on the 65 overlapping settlements with a known percentage: ratio mean 0.9999, sd 0.0009): 100 settlements 30 Sep 2021 – 31 Aug 2026 incl. the Nasdaq 31 Aug row; mean 2.76, median 2.61, max 5.44, min 1.48 (30 Apr 2022); 2022 max 3.50 (15 Jul 2022), 2022 mean 2.41; the latest 2.40 is the 34th percentile. Local peaks ≥3.3: Jul 2022 3.50, Dec 2022 3.34, Jan 2023 3.49, Jun 2023 4.04, Sep 2023 5.44, Sep 2025 3.53 — six episodes in five years, one at 5 | `datasets/si_history_2022_2026.csv` (`marketbeat_history.py`); `datasets/r13_summary.json` | 2026-09-17 | 2026-09-17 | yes |
| 4 | Eight-settlement window maxima (n 92 windows with a known prior level): P(max ≥ 5.0) 0.087 (8 windows, start dates 15 Jun – 30 Sep 2023: one episode), P(≥4.5) 0.109, P(≥4.0) 0.185, P(≥3.5) 0.37; largest rise from the prior level inside a window 2.34pt (p90 1.58) against the 2.60pt now needed (0 of 92). Conditional on a prior level < 2.5 (n 42): P(≥5) 0, P(≥4.5) 0, P(≥4) 0.024 (max 4.04); < 3.0 (n 61): 0 / 0 / 0.049, largest rise 2.03pt. 2023+ windows (n 62): P(≥5) 0.129 | `datasets/si_window_max.csv`; `r13_summary.json` windows_* | 2026-09-17 | 2026-09-17 | yes |
| 5 | The 5.44% peak is the S&P 500 inclusion: announced after the close on Fri 1 Sep 2023 (+7.1% abnormal on 5 Sep, t 2.7), effective 18 Sep 2023 (−0.1%), the following 20 sessions −9.7%; short interest 31 Aug 3.10% → 15 Sep 4.04% (+0.94) → 30 Sep 5.44% (+1.40, 34.8m shares) → 15 Oct 4.70 → 31 Oct 4.56 → 15 Nov 3.91 → 31 Dec 3.00. These are the only two single-step rises ≥0.9pt in 99 steps (per-step sd 0.31, p95 0.43); against the AR(1) fit they are residuals of +0.97 and +1.52, the only two with \|residual\| ≥ 0.75. "Index inclusion is a pre-effective-date event ... classic index-demand front-run and unwind" | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 item 6 and the event table; `data/processed/abnb_big_moves_7pct.csv` row 33; `datasets/r13_summary.json` changes; `datasets/r13_v2_summary.json` ar1 | 2026-09-06 | 2026-09-17 | yes |
| 6 | Structural short sources: the $2.0bn 0% convertible senior notes due March 2026 "matured in March 2026" (1Q26 letter) and are "fully settled; no dilution left to model" (M7 note); they were repaid from a $2.5bn straight senior-note offering (4.400% 2029, 4.650% 2031, 5.250% 2036; prospectus supplement 12 Mar 2026) — no new convertible, hence no new arbitrage hedge short. Short interest fell from 17.9m (31 Dec 2025) through 16.9m (15 Jan), 15.2m (13 Feb), 14.4m (31 Mar) to 12.9m (31 Jul) over the redemption. ABNB is an S&P 500 (Sep 2023) and Nasdaq-100 member; no inclusion event is scheduled | `data/raw/letters/1Q26_d23351dex991.htm`; `docs/margin-build/notes/M7_below_ebitda.md` line 207; https://www.sec.gov/Archives/edgar/data/1559720/000119312526106418/d107518d424b2.htm (`sources/web_search_log.md`); `data/processed/overnight/09_short_interest.csv` | 2026-03-12 to 2026-05 | 2026-09-17 | yes |
| 7 | AR(1) in levels on the 100-settlement series: slope 0.906, intercept 0.262, long-run mean 2.78, residual sd 0.31 (full pool, n 99) / **0.25 with the two index-inclusion residuals removed (n 97)**; simulated from 2.40 with one unobserved step (15 Sep) then the eight window settlements, bootstrapped residuals. Full pool, no jump: P(max ≥5) 0.005, P(≥4.5) 0.019, P(≥4) 0.068, P(≥3.5) 0.175; median max 2.90, p90 3.81, p99 4.75. Clean pool, no jump: P(≥5) 0.000, P(≥4) 0.004. Fitted on 2024+ only (resid sd 0.20, long-run mean 2.47): P(≥5) 0.0000, P(≥4) 0.0003 (revision 1). Fitted 2023+: P(≥5) 0.008 (revision 1) | `datasets/r13_summary.json` ar1_* (`r13_model.py`); `datasets/r13_v2_summary.json` (`r13_model_v2.py`) | 2026-09-17 | 2026-09-17 | yes |
| 8 | Jump and overlay variants, revision 2 (`r13_v2_summary.json` sims): jump probability 2/99 per step, size U(0.9, 1.5), **bootstrap pool with the two calibrating shocks removed** (A13-08): P(≥5) 0.004; plus the down-print overlay at the **mean** post-down-print three-settlement rise +0.35pt (A13-09) at **S01 revision 2's P(day-1 ≤ −5%) = 0.38** (revision 1 used revision 1's 0.41), spread over 13 Nov and 30 Nov: **0.0054** (the decomposition); overlay +0.70 (the maximum) 0.009; +1.5 (twice the maximum) 0.036; jump probability doubled 0.019; jump size U(1.5, 2.5) 0.044; start 3.0% 0.014, start 2.0% 0.003; conditional on a down print 0.008, on an up print 0.004. Revision 1's construction (full pool + jump + 0.70 overlay at 0.41) reproduces at 0.0307 and is withdrawn as the decomposition: it priced the September-2023 episode twice (in the pool and in the jump) and set the overlay at the maximum of six observations. Post-print history (short interest over the three settlements after each print vs the last before): down ≤−5% prints (n 6) rises +0.68, +0.70, −0.32, +0.51, +0.06, +0.44 → mean +0.35, median +0.48, max +0.70 (1Q23); up ≥+5% prints +0.17; small prints +0.03 | `datasets/r13_v2_summary.json`; `datasets/si_after_prints.csv` (revision 1); `datasets/r13_summary.json` ar1_full_jump* (revision 1) | 2026-09-17 | 2026-09-17 | yes |
| 9 | Alternative basis: on the ~406m float the latest reading is 3.51%; a 5.0%-of-float threshold is 20.3m shares = 3.43% of total shares, exceeded by the series on 15 Sep 2025 (21.69m), 30 Sep 2025 (21.17m) and through most of 2023; the revision-2 simulations give P(max ≥ 3.43) 0.20–0.26 (revision 1's variants 0.20–0.40) | `datasets/r13_v2_summary.json` sims (P(max>=3.43_float_basis_equiv)); `r13_summary.json` alt_basis_* | 2026-09-17 | 2026-09-17 | yes |
| 10 | Web (17 Sep): Yahoo 22 Aug "Short interest sits at just 3.39% of float as of mid-August"; no report of a September positioning change; no market on short interest on Kalshi or Polymarket | `sources/web_search_log.md` | 2026-08-22 / 2026-09-17 | 2026-09-17 | no |
| 11 | **S01 revision 2**: P(5 Nov day-1 ≤ −5%) **0.38**, ≤ −8% 0.27, ≥ +5% 0.22 (revision 1: 0.41 / 0.29 / 0.20); the memo's short case; a down print is the only dated mechanism in the window that has historically raised short interest. S02 revision 2 accelerating-print weight 0.32 (revision 1: 0.24) | `../day1-move-5nov/forecasts/2026-09-17-forecast.json` (revision 2, `threshold_probs`); `../close-15dec-2026/forecasts/2026-09-17-forecast.json` | 2026-09-17 | 2026-09-17 | yes |

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
13. [revision 2, repo] `../day1-move-5nov/forecasts/2026-09-17-forecast.json` (revision 2: P(≤ −5%) 0.38), `../close-15dec-2026/forecasts/2026-09-17-forecast.json` (revision 2: accel weight 0.32), `data/processed/abnb_capital_return_quarterly.csv` header (`basic_wa_shares_m`), `sources/yfinance_info_short_20260917T035213Z.json` (`sharesShort`, `floatShares`, `shortPercentOfFloat`, `impliedSharesOutstanding`)
14. [revision 2, computed] `audits/A13-reproduce.py` (the auditor's script; output in `audits/A13-reproduce.stdout.txt`): every series figure re-verified; the clean-pool decomposition 0.0041 (jump) / 0.0095 (jump + 0.70 overlay at 0.41)
15. [revision 2, computed] `datasets/r13_model_v2.py` → `r13_v2_summary.json`, `r13_v2_stdout.txt` (claim 8, §7)

WebSearch calls charged to R13: 1 (query 9); batch total 3 of 15. No new web queries in revision 2.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, Nasdaq short interest, FINRA settlement dates, S&P 500 inclusion September 2023, 2026 convertible notes, 5 Nov 2026 print, MarketBeat, basic weighted-average shares

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Unconditional window base rate 0.087–0.129 taken at face value | discarded as the point | all eight qualifying windows are one episode (claim 4) driven by an index-inclusion hedge (claim 5); the regime-conditioned rate (start < 3.0%, no inclusion event, converts gone) is 0 of 61 windows |
| "% of float" basis (Yahoo/MarketBeat display) | discarded for the object; reported | the question names the repo file, which uses the basic weighted-average count; under the float basis the threshold is 20.3m shares and P ≈ 0.20–0.26 (claim 9) — the single biggest resolution risk, fenced in the extreme-probability audit |
| Jump term added on top of a bootstrap pool that still holds the two calibrating shocks (revision 1: 0.018 jump, 0.031 with overlay) | withdrawn (A13-08) | the same episode was priced twice; with the two residuals removed from the pool the jump model gives 0.004 and the decomposition 0.005 |
| Down-print overlay at the maximum observed rise (+0.70pt, revision 1) | replaced by the mean (+0.35pt) (A13-09) | six observations, mean +0.35, median +0.48, max +0.70; the maximum and twice the maximum are the sensitivity rows (0.009, 0.036) |
| A down 5 Nov print drives shorts to 5% | kept as an overlay (+0.35pt, P 0.38) | the largest post-down-print rise in six cases is +0.70pt; even +1.5pt (twice the record) gives 0.036; 5% needs +2.6pt |
| A new convertible or exchangeable issue creates a hedge short | tail, carried as a stated structural allowance (§5), not inside the jump term | the March 2026 refinancing was straight debt; $9.6bn net cash; no filing; a $2bn convert would add ~5–8m shares (≈1pt), not 15m; the 100-settlement series contains no such event, so the jump term (calibrated on the index episode) cannot price it |
| Index event (S&P/Nasdaq-100 reweight, a new index) | tail, inside the structural allowance | already a member of both; quarterly rebalances did not move the series in 2024–26 |
| Convert the AR(1) into a log model or a regime-switching model | not done | the level AR(1) with bootstrapped residuals already reproduces the empirical p99 (4.75 vs the series' 4.70 second-highest reading); the clean-pool-plus-jump variant covers the one out-of-model episode without double counting |
| Team's own short adds to the count | ignored | a student pitch has no position |

## 5. Independent Estimates
- base_rate_estimate: 0.06 — six local peaks ≥3.3% in 60 months (claim 3) → P(a peak episode inside a 4.5-month window) ≈ 0.4; P(peak ≥ 5 | episode) 1 of 6, or 0 of 5 once the index-inclusion episode is excluded as a non-recurring driver (Laplace 1/7); 0.4 × 0.14 ≈ 0.06; the raw unconditional window rate 0.087 and the conditional 0/61 bracket it
- decomposition_estimate: **0.010** — stated as three parts, each with its source: (a) the internally consistent model (AR(1) from 2.40% on the clean residual pool + the calibrated jump term + the mean down-print overlay at S01 revision 2's 0.38): **0.005**, or 0.009 with the overlay at the observed maximum; (b) a **structural-event allowance ≈ 0.008** for routes the settlement series cannot contain — a new convertible or exchangeable (≈0.03 in the window × ≈0.15 that the hedge alone reaches 5% ≈ 0.005), a stock-component acquisition or index event (≈0.003); (c) nothing for the resolver basis here (carried in §6). (a) + (b) ≈ 0.013; the revision-1 "0.03" was the full-pool jump model plus the maximum overlay and is withdrawn as the decomposition
- anchor_estimate: 0.01 — no tradable market (claim 10); the repo prior is the 09 note's positioning judgement ("no short squeeze left to harvest", claim 2) and the earlier attempt's AR(1) on the 84-settlement file (0.0045); read as ≈0.01
- anchor_value: n/a (no market); repo prior ≈ 0.01 (09 note 2026-09-06; AR(1) 2026-09-17)
- final_estimate: **0.02** (credible interval 0.005–0.06)
- final_minus_anchor: +0.01. NOT_INDEPENDENTLY_DERIVED does not apply in substance: the final is the decomposition (0.013) plus the resolver-basis residual from §6 (≈0.007) = 0.02, held below the episode base rate (0.06) because that rate is one episode with a driver that cannot recur; the interval's top (0.06) is the "structural event or twice-the-record overlay" region; the agreement with the repo prior in level is because both rest on the same series, not deference

## 6. Final Numbers
P(short interest ≥ 5.0% of basic shares at any of the eight settlements 30 Sep 2026 – 15 Jan 2027) = **0.02**, credible interval **0.005–0.06**.
Companion numbers on the same basis (revision-2 base simulation): P(max ≥ 4.0%) ≈ 0.07–0.10; P(max ≥ 3.5%) ≈ 0.20–0.26; the window maximum's median ≈ 3.0%, p90 ≈ 3.9%, p99 ≈ 4.8%.
Alternative basis (5% of the ~406m float = 20.3m shares = 3.43% of total shares): P ≈ 0.22 (0.20–0.26 across the revision-2 variants; 0.20–0.40 in revision 1's) — quoted only if the resolver adopts the float basis.
Conditional on a 5 Nov day-1 ≤ −5%: ≈ 0.025 (model 0.008 + allowances); on a day-1 ≥ +5%: ≈ 0.015.

Extreme-probability gate (triggered, P ≤ 5%). Resolution-criteria audit: (1) criteria re-read: "exceed 5.0% of shares outstanding at any Nasdaq settlement date between 30 Sep 2026 and 15 Jan 2027", "Nasdaq/MarketBeat series as in `09_short_interest.csv`", "data lag allowed". (2) Edge cases: (a) denominator basis — the repo file divides by the basic weighted-average count; MarketBeat's page headline is "% of float" (~406m); if a resolver uses the float, Yes becomes ≈0.22: this is the dominant edge, fenced by conventions (3)–(4); P(resolver adopts the float basis) ≈ 0.03 → residual ≈ 0.007; (b) weighted-average vs outstanding count — 0.34m shares on the threshold, no effect (A13-19); (c) a restatement of shares outstanding (10-Q cover count) — ±1%, immaterial; (d) Nasdaq's series revised after publication — has not happened in the cross-checked rows since Sep 2025; residual 0.002; (e) a 13 Nov vs 15 Nov settlement-date labelling difference — no effect; (f) an unscheduled structural event (new convertible, index change, M&A with a stock component) — the §5 structural allowance ≈ 0.008, not inside the jump term; (g) the 15 Jan reading published after the question's resolution date — allowed by the fine print. (3) Model 0.005 + structural 0.008 + resolver edges ≈ 0.009 → **0.022, quoted as 0.02**; the interval's top 0.06 holds the structural-event and twice-the-record cases together.

## 7. Sensitivity
Reruns of `datasets/r13_model_v2.py` (`r13_v2_summary.json` sims); base (a) = 0.0054; the final carries each delta on top of the fixed allowances (≈ +0.015).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Bootstrap pool with the two Sep-2023 residuals removed (n 97, sd 0.25) when the jump term is on | full pool (revision 1's double count): model 0.018 (jump) / 0.031 (with the 0.70 overlay at 0.41) → final ≈ 0.03–0.045 |
| Jump term q 2/99, size U(0.9, 1.5) | no jump term: model 0.000 → final ≈ 0.015; probability doubled: 0.019 → 0.035; size U(1.5, 2.5): 0.044 → 0.06 |
| Down-print overlay +0.35pt at P 0.38 | none: 0.004; +0.70 (the maximum): 0.009 → 0.025; +1.5pt (twice the maximum): 0.036 → 0.05; P 0.41 (S01 rev 1): 0.006 |
| AR(1) fitted on the full 2021–26 series | 2024+ fit (resid sd 0.20): ≈ 0.000 (revision 1); 2023+ fit: 0.008 (revision 1) |
| Starting level 2.40% (31 Aug) | if the 15 Sep reading prints 3.0%: model 0.014 → final ≈ 0.03; 2.0%: 0.003 → 0.015 |
| Denominator basic weighted-average shares (592m) | float basis (406m): ≈ 0.22; outstanding count (598.8m): unchanged |
| Structural-event allowance 0.008 | none: final 0.012; doubled: 0.03 |
| Episode base rate excludes the index-inclusion episode | included at full weight (1 of 6 peaks): base rate 0.07, final unchanged |

Pre-mortem ("it is 27 Jan 2027, the 15 Jan reading is out, and I was wrong"): (1) **A convertible or exchangeable issue in Q4** — Airbnb refinanced with straight debt in March and holds $9.6bn net cash; a $2bn convert would add roughly a point, and the arbitrage hedge alone cannot reach 5%; priced in the structural allowance. (2) **A dedicated short campaign after a bad 5 Nov print** (an "RNPL is a receivables problem" note going viral) — the 2Q24 and 1Q23 down prints, the two worst in the sample, added 0.5–0.7pt; reaching 5% needs four times that; priced at 0.05 in the "twice the record" row. (3) **Merger-arbitrage or index-arb flow from an acquisition announced with stock** — no deal reported; founder-controlled; tail, in the allowance. (4) **The resolver used the float basis** — the audit's edge (a); the log states the basis and the alternative number so the memo cannot be caught by it. (5) **Nasdaq changes its reporting basis or misses a settlement** — "data lag allowed"; no residual beyond 0.002. (6) **The clean-pool model is too narrow** — removing the two shocks cuts the residual sd from 0.31 to 0.25 and the jump term is meant to carry what was removed; if a non-index shock of the same size exists in the process, the full-pool row (0.03–0.045) is the answer. Asymmetry: a confident No that resolves Yes on the stated basis would coincide with a squeeze-risk regime the memo would want to know about; the interval's top holds the structural-event case.

## 8. Monitoring Calendar
Update procedure: after each Nasdaq publication, re-run `datasets/r13_model_v2.py` with the new reading appended (change `latest_shares` and the window count); hazard decay is mechanical — with each settlement that prints below 3.0%, the remaining window shortens and P falls.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| ~2026-09-24 | 15 Sep settlement published (pre-window) | ≤ 2.6%: 0.015; 3.0–3.4%: 0.03; ≥ 3.5%: 0.08 |
| 2026-10-02 | prelim memo due | quote 0.02 (0.005–0.06); state the basis; drop the item as immaterial and keep the borrow-cost sentence |
| ~2026-10-09 | 30 Sep settlement (first in-window) | ≤ 2.8%: 0.015; ≥ 3.5%: 0.06; ≥ 4.0%: 0.20 |
| ~2026-10-26, 11-10 | 15 Oct, 30 Oct settlements (pre-print) | same ladder; each reading ≤ 3.0% with fewer settlements left: −0.003 |
| 2026-11-05/06 | 3Q26 print | day-1 ≤ −5%: 0.025; ≥ +5%: 0.015 |
| ~2026-11-24, 12-09 | 13 Nov, 30 Nov settlements (post-print) | the historical post-down-print rise is in by 30 Nov; reading ≤ 3.5%: 0.01; ≥ 4.2%: 0.15 |
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
| Stock ($/share) | **+$1 (judgement, branch-weighted)**: a crowded short widens the right tail on an accelerating print — with 29.6m shares short against 4.7m average daily volume, covering into a +5% day adds an estimated 2–3 points (≈ +$3–5) on that branch, which S02 revision 2 weights at 0.32, i.e. ≈ +$1 at $167.5 unconditional on the branch; the level itself has no forward-return content (r 0.15, p 0.18, claim 2); the 2Q26 +17.4% squeeze-like day happened at 2.4% short interest, so crowding is not required for the right tail already in S01. The consequential part is trade-level, not price: at 5% the borrow fee and recall risk rise and the team's short is one of many | claim 1 (days to cover), claim 2, claim 11, S01/S02 revision 2 |
| **EV = P × impact** | 0.02 × $1 = **$0.02/share** (0.02 × $3 = $0.06 on the accelerating branch alone) | |
| Materiality | **Immaterial** (well under $1/share). The memo can drop "short-interest crowding" as a price risk and keep one sentence on borrow cost and recall | |

## 10. Revision notes
| # | Change (revision 1 → revision 2) | Finding |
|---|---|---|
| 1 | Jump model re-simulated on a bootstrap pool with the two Sep-2023 calibrating residuals removed (n 97, sd 0.25): jump-only 0.018 → 0.004; claim 7–8 and §4 rewritten; the full-pool construction kept as the "double count" sensitivity row | A13-08 |
| 2 | Down-print overlay +0.70 (max of six) → +0.35 (mean); +0.70 and +1.5 as sensitivities | A13-09 |
| 3 | Not in the audit: overlay probability 0.41 (S01 revision 1) → 0.38 (S01 revision 2 `p_le_minus5`); claim 11 rewritten | — |
| 4 | §5 restated as decomposition = model 0.005 + structural allowance 0.008; §6 residuals re-listed (resolver basis ≈ 0.007); headline **0.03 (0.01–0.08) → 0.02 (0.005–0.06)**; companions and the float-basis alternative (0.25 → 0.22) updated | A13-25, A13-08, A13-09 |
| 5 | Convention (3) and claim 1: denominator described as the repo file's basic weighted-average count (592.0m); the outstanding count (598.786m, threshold 29.94m shares, latest 2.376%) recorded; no change to the answer | A13-19 |
| 6 | Claim 1: the float-basis figure quoted as the computed 3.51% (14,228,547 / 405,782,346); yfinance's `shortPercentOfFloat` 3.44% noted as not reproducible and not used | A13-20 |
| 7 | §9: one stock figure (+$1 branch-weighted, +$3 on the accelerating branch) at S02 revision 2's 0.32 weight; EV $0.09 → $0.02; the borrow-cost/recall sentence leads the row | A13-21 |
| 8 | Monitoring ladder re-based on the revision-2 numbers | — |

## RESUME
The next agent (X01 or a further revision) should re-run `datasets/marketbeat_history.py` (needs `sources/marketbeat_short_interest_20260917.html`) and `datasets/r13_model_v2.py` (deterministic, ~60 s). Two things remain open: (1) the denominator convention — confirm with the orchestrator that "shares outstanding" means the repo file's basic weighted-average count (592m), because the float basis flips the answer to ≈0.22; (2) whether the clean-pool model is too narrow (pre-mortem item 6) — the full-pool row (0.03–0.045) is the alternative. By ~24 Sep the 15 Sep settlement will be out: append it and re-run before anything else.
