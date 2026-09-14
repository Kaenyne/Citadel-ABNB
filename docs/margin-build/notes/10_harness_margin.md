# WS10 — The margin harness: targets, PIT slice, seven baselines, recency-weighted scorer, registry

Slug `10_harness_margin`. Written 13 Sep 2026 (Sat night / Sun 04:40) by the second WS10 agent (the first was cut off
at 01:24 after writing `targets.csv`, `targets_units.csv`, `targets_source.json` and five draft modules, which I kept and
finished). Code: `analysis/src/margin_build/10_harness_margin/` (README there is the API document). Data:
`data/processed/margin_build/10_harness_margin/`. Registry: `data/processed/margin_build/registry/baselines-margin__*.csv`.

## Bottom line

1. **The harness exists and passes its pre-registered pass line.** `run.py` exits 0 (41 s) under both `py -3.13`
   (pandas 2.3) and the venv `python` (pandas 3) with identical output; every one of the seven baseline objects covers all
   14 W1 and 10 W2 guide dates for adjusted EBITDA margin and dollars at h=0; the seasonal-naive MAE on adj EBITDA margin at
   h=0 in W1 is **2.24 pp (n=14)**, W2 **1.96 pp (n=10)**; 11/11 unit tests pass. Targets are built from the final WS02
   panel (13 Sep 04:26, validated, no fallback needed).
2. **The hardest baseline for the margin itself is the Street** (LSEG pre-guide mean at the guide date, WS03): h=0 MAE
   1.59 pp W1 / 1.31 pp W2 (recency-weighted 1.25 / 1.12), ratio to seasonal naive 0.71 / 0.67, and it is the only object
   that survives both windows at h=0 and h=1. Its bias is **-1.22 pp W1 / -1.13 pp W2**: the pre-guide Street sits below
   the eventual margin, the same under-call WS03 found at print. Any method that claims to forecast the margin must beat
   1.31 pp in W2, not 1.96.
3. **For the six cash cost lines in dollars the hardest baseline is `seasonal_naive_drift`** (last year's line plus the
   trailing y/y dollar change) by a factor of 2-5 over the plain seasonal naive — cost lines trend, margins do not. For the
   lines as % of revenue the plain seasonal naive is hardest for cost of revenue and ops & support (MAE 0.6 / 0.9 pp), the
   drift for product development and sales & marketing (0.6 / 1.1-1.3 pp); G&A % of revenue is the one line where the
   equal- and recency-weighted answers disagree (naive vs trailing-4). `pct_rev_last4` (trailing ratio times the PIT revenue
   forecast) is the WORST baseline everywhere (MAE 2-3x naive) because a 4-quarter mean ratio ignores seasonality; it is kept
   as the honest "what a % of revenue model buys you" floor.
4. **Management's FY margin floor, prorated, is a poor quarterly forecaster** (`guide_implied` h=0 MAE 4.4 pp W1, 3.8 W2;
   bias -4.4 / -3.8): the floor is beaten every year and the prorating puts the shortfall on whichever quarters remain.
   **Management's quarterly margin sentence is coded as ±0 pp y/y in the guidance ledger** ("down slightly", "decline",
   "expand" are all a ceiling/floor at zero), so `q_guide_implied` equals `seasonal_naive` to the third decimal on margin.
   The direction, though, was right 13/14 times in W1 and 9/10 in W2 (2Q25 the miss): a one-parameter rule "last year
   ±1.5 pp in the direction of the sentence" would have scored MAE 1.43 (W1) / 1.17 (W2), in-sample, i.e. on a par with
   the Street. That is a method, not a baseline, and is left for the M-workstreams (see "For the model").
5. Caveats that matter: n is 14 / 10; the recency-weighted MAEs are 15-25% lower than equal-weighted for margin (the
   2023 misses were larger), and the two weightings disagree on the winner in 7 of 87 target/window/horizon cells; PIT
   interval coverage is 100% for most objects at h=0 (the walk-forward sd pools still carry 2021-22 errors at the early W1
   vintages), so `cov80` is not yet informative for baselines — it will be for methods that fit tighter pools.

## What ran (exact commands)

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/10_harness_margin/run.py     # targets, guides, street, revenue leg, shares, 7 baselines, scoreboard; exit 0
py -3.13 analysis/src/margin_build/10_harness_margin/tests.py   # 11/11 pass (also under venv python)
py -3.13 analysis/src/margin_build/10_harness_margin/score.py   # rescore only
```

Inputs: WS02 `02_panel_quarterly.csv` (final; 34 quarters, validated: no nulls 1Q21-2Q26, |rebuild gap| <= 2, adj EBITDA within
$1.5M of `abnb_quarterly_cost_stack_exsbc.csv`); WS03 `03_consensus_at_dates.csv` (roles `guided_q_pre_guide`, `next_q_pre_guide`,
`current_q`, `current_next_q`; vendor LSEG; `as_of` = calc date D-1); `overnight/02_guidance_ledger.csv` (38 numeric margin guides);
frozen harness `targets.csv` / `calendar.csv` / `baselines.py` for the revenue leg; WS05 `05_guide_language_pattern.csv` read for the
direction diagnostic only.

## Pre-registered pass line (from the prompt) and result

| test | pass line | result |
|---|---|---|
| build | `run.py` exits 0 | PASS (41 s, both interpreters) |
| coverage | every baseline object covers all 14 W1 / 10 W2 guide dates for adj EBITDA margin | PASS 14/14, 10/10 for all 7 objects (margin and $; `pct_rev_last4` is $-only) |
| headline | seasonal-naive MAE on adj EBITDA margin, h=0, W1, n=14 reported | 2.237 pp (rw 1.913); W2 n=10: 1.959 (rw 1.755) |
| tests | `tests.py` passes | 11/11 |

Tests count: 4 pass-line checks + 11 unit tests (PIT slice incl. 424B4 dating of 1Q20, validator PIT rule, unknown target /
bad vintage, window membership incl. LIVE 2026Q4 acceptance, seasonal naive / drift / trailing-4 hand case at 2025-08-06,
pct_rev_last4 hand case incl. the h=1 naive revenue leg, guide_implied 34.5% identity at 2025-08-06, PIT vs full-sample
seasonal shares, scorer toy with known EW/RW answers, survives-both logic, fallback panel vs WS02). None failed after the two
fixes below.

## What the harness gives (short; the README is the reference)

- `targets.csv`: 42 target metrics x 26 actual quarters 1Q20-2Q26 (+ forward rows to 4Q27), print dates from the frozen calendar
  (1Q20/2Q20 stamped at the 424B4, 2020-12-10). Units in `targets_units.csv`.
- `history_as_of(vintage)`: quarters printed <= vintage (same-day letter included, as the frozen harness).
- `register(df)`: the frozen FORMAT 1.0 validator plus the margin target and window rules; files under `margin_build/registry/`.
- LIVE vintages: 2026-08-06 and **2026-09-11** (the frozen validator's TODAY; the prompt's 12 Sep is stamped 11 Sep — the WS03
  "current" consensus row is the 11 Sep LSEG row, so nothing is lost).
- `score.py`: per (method, object, target, window, horizon, replay, spec_id): n, MAE, RMSE, bias, CRPS, pinball, 80/90% coverage,
  PIT mean, MAE ratio to each of the seven baselines on matched quarters, rolling conformal, `survives_both_windows`, `n_params`;
  all again recency-weighted (`rw_` prefix, half-life 4 quarters anchored at 2026Q2). `scoreboard_by_quarter.csv` long file.
- `revenue_forecast_pit(vintage, quarter)`: the PIT revenue leg every cost method should use for backtests (frozen guide-cushion
  at h=0, frozen naive beyond) — `revenue_leg_pit.csv`.
- `fy_guide_in_force`, `q_guide_in_force`, `load_street`: management guides and vintage-stamped Street for M-methods.

## Baseline scoreboard — adjusted EBITDA margin (pp), PIT replay

| object | window | h | n | MAE ew | MAE rw | bias ew | bias rw | ratio to naive ew / rw | cov80 | n_params | survives both (ew / rw) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **street** | W1 | 0 | 14 | **1.59** | **1.25** | -1.22 | -1.10 | 0.71 / 0.65 | 1.00 | 1 | yes / yes |
| seasonal_naive | W1 | 0 | 14 | 2.24 | 1.91 | -0.47 | -0.02 | 1 / 1 | 1.00 | 1 | – |
| q_guide_implied | W1 | 0 | 14 | 2.24 | 1.91 | -0.47 | -0.02 | 1.00 / 1.00 | 0.86 | 1 | no |
| seasonal_naive_drift | W1 | 0 | 14 | 2.38 | 1.98 | +0.26 | -0.17 | 1.07 / 1.04 | 1.00 | 1 | no |
| guide_implied | W1 | 0 | 14 | 4.38 | 3.27 | -4.38 | -3.27 | 1.96 / 1.71 | 0.79 | 4 | no |
| trailing4 | W1 | 0 | 14 | 9.48 | 8.49 | +0.64 | +1.21 | 4.24 / 4.44 | 0.79 | 2 | no |
| **street** | W2 | 0 | 10 | **1.31** | **1.12** | -1.13 | -1.03 | 0.67 / 0.64 | 1.00 | 1 | yes / yes |
| seasonal_naive | W2 | 0 | 10 | 1.96 | 1.75 | +0.19 | +0.27 | 1 / 1 | 1.00 | 1 | – |
| q_guide_implied | W2 | 0 | 10 | 1.96 | 1.75 | +0.19 | +0.27 | 1.00 / 1.00 | 0.90 | 1 | no |
| seasonal_naive_drift | W2 | 0 | 10 | 2.02 | 1.85 | +0.54 | -0.07 | 1.03 / 1.05 | 1.00 | 1 | no |
| guide_implied | W2 | 0 | 10 | 3.80 | 3.06 | -3.80 | -3.06 | 1.94 / 1.74 | 0.90 | 4 | no |
| trailing4 | W2 | 0 | 10 | 8.98 | 8.32 | +1.77 | +1.73 | 4.58 / 4.74 | 0.90 | 2 | no |
| street | W1 | 1 | 13 | 1.64 | 1.25 | -0.66 | -0.34 | 0.70 / 0.65 | 1.00 | 1 | yes / yes |
| seasonal_naive | W1 | 1 | 13 | 2.35 | 1.93 | -0.57 | -0.03 | 1 / 1 | 1.00 | 1 | – |
| guide_implied | W1 | 1 | 10 | 3.15 | 2.38 | -2.45 | -1.95 | 1.39 / 1.20 | 0.80 | 4 | no |
| street | W2 | 1 | 9 | 0.99 | 0.97 | +0.28 | +0.03 | 0.63 / 0.60 | 1.00 | 1 | yes / yes |
| seasonal_naive | W2 | 1 | 9 | 1.58 | 1.60 | +0.81 | +0.51 | 1 / 1 | 1.00 | 1 | – |
| seasonal_naive | W1 | 2 | 12 | 2.48 | 1.96 | -0.68 | -0.05 | 1 / 1 | 1.00 | 1 | hardest at h=2 |
| seasonal_naive | W2 | 2 | 8 | 1.72 | 1.66 | +0.86 | +0.52 | 1 / 1 | 1.00 | 1 | hardest at h=2 |

The full_sample replay changes only interval width for six objects; for `guide_implied` it also swaps in the FY2023-25
seasonal shares and the h=1/h=2 rows then "survive both windows" (MAE 2.02 / 1.55 pp) — pure hindsight, which is what the
two-replay rule is for. Street has no h=2 (WS03 stamps the guided quarter and the next only).

## Baseline scoreboard — adjusted EBITDA dollars (USD m), h=0, PIT

| object | W1 MAE ew / rw (n=14) | W1 bias | W2 MAE ew / rw (n=10) | W2 bias | ratio to naive W1 / W2 |
|---|---|---|---|---|---|
| q_guide_implied (= last-year margin x PIT revenue) | **63 / 58** | -3 | 62 / **56** | +16 | 0.51 / 0.63 |
| street | 65 / 62 | -51 | **58** / 59 | -42 | 0.53 / 0.59 |
| seasonal_naive_drift | 103 / 93 | -3 | 82 / 86 | +1 | 0.84 / 0.84 |
| guide_implied | 104 / 87 | -104 | 97 / 84 | -97 | 0.85 / 0.99 |
| seasonal_naive | 123 / 116 | -122 | 98 / 106 | -96 | 1 / 1 |
| pct_rev_last4 | 272 / 253 | -42 | 265 / 249 | -7 | 2.20 / 2.71 |

Reading: in dollars the seasonal naive is easy to beat because EBITDA grows; the honest floor is "last year's margin on this
year's PIT revenue" (`q_guide_implied`, which is exactly that when the sentence is ±0), MAE ~$60M, or the Street, ~$60M with a
$40-50M under-call.

## Baseline scoreboard — cost lines, h=0 (hardest object; MAE ew / rw; n = 14 W1, 10 W2)

| target | W1 hardest | W1 MAE | W2 hardest | W2 MAE | seasonal_naive W1 / W2 | agree ew-rw |
|---|---|---|---|---|---|---|
| cor_cash_musd | drift | 24.4 / 23.7 | drift | 26.8 / 24.3 | 53.7 / 54.7 | yes |
| ops_cash_musd | drift | 18.8 / 18.1 | naive | 17.2 / 17.6 | 22.4 / 17.2 | yes |
| pd_cash_musd | drift | 10.1 / 8.8 | drift | 9.3 / 8.5 | 33.0 / 38.9 | yes |
| sm_cash_musd | drift | 32.2 / 29.3 | drift | 30.6 / 28.7 | 94.3 / 108.9 | yes |
| ga_cash_musd | naive | 162.8 / 117.4 | naive | 122.8 / 95.0 | (4Q23 reserve dominates) | yes |
| sbc_musd | drift | 11.6 / 10.6 | drift | 11.3 / 10.4 | 55.5 / 58.7 | yes |
| da_musd | drift | 3.4 / 3.1 | drift | 2.5 / 2.7 | 6.9 / 5.4 | yes |
| cor_cash_pct_rev (pp) | naive | 0.64 / 0.53 | naive | 0.62 / 0.51 | – | yes |
| ops_cash_pct_rev | naive | 0.81 / 0.85 | naive | 0.89 / 0.87 | – | yes |
| pd_cash_pct_rev | drift | 0.66 / 0.58 | drift | 0.58 / 0.56 | 0.80 / 0.69 | yes |
| sm_cash_pct_rev | drift | 1.27 / 1.07 | drift | 1.07 / 1.01 | 1.71 / 1.73 | yes |
| ga_cash_pct_rev | naive (ew) / trailing4 (rw) | 6.90 / 4.98 | naive / trailing4 | 5.47 / 3.98 | 6.90 / 5.47 | **NO** |
| sbc_pct_rev | drift | 0.63 / 0.53 | drift | 0.62 / 0.53 | 0.68 / 0.82 | yes |
| op_margin_pct | naive | 7.70 / 6.02 | naive | 6.72 / 5.32 | – | yes |
| eps_diluted (USD) | street | 0.52 / 0.27 | street | 0.12 / 0.12 | 0.97 / 0.71 | yes |
| fcf_margin_pct | naive | 7.65 / 7.32 | naive | 7.05 / 7.01 | – | yes |
| tax_rate_pct | trailing4 | 34.0 / 22.3 | trailing4 | 22.3 / 17.6 | 41.7 / 27.1 | yes |
| diluted_shares_m | drift | 12.2 / 6.8 | drift | 6.1 / 4.9 | 21.4 / 19.5 | yes |

Full table for every target, window and horizon: `hardest_baseline_by_target.csv` / `baseline_scoreboard_summary.md`
(87 cells; the weightings disagree in 7: G&A %/per-night in both windows, cost-of-revenue per night, S&M % at h=1-2 in W1, adj EBITDA $ in W2).

## LIVE baselines at vintage 2026-09-11 (PIT replay)

| object | 3Q26 margin % (q10-q90) | 3Q26 EBITDA $M | 4Q26 margin % | 4Q26 EBITDA $M |
|---|---|---|---|---|
| street (LSEG 11 Sep, n 36) | **49.78** (47.8-51.7) | **2,362** | **28.90** | **914** |
| seasonal_naive (= q_guide_implied on margin) | 50.09 (46.1-54.1) | 2,051 / q_guide 2,411 | 28.29 | 786 |
| seasonal_naive_drift | 51.35 | 2,269 | 29.56 | 1,004 |
| guide_implied (FY26 floor 35.5%, shares FY23-25) | 49.38 (45.4-53.3) | 2,377 | 28.81 | 933 |
| trailing4 | 33.18 | – | 33.18 | – |
| pct_rev_last4 (33.2% x revenue leg) | – | 1,597 | – | 1,074 |

Revenue leg at TODAY: 3Q26 $4,815M (guide-cushion), 4Q26 $3,237M (naive). Pre-guide Street at the 2026-08-06 vintage: 3Q26
$2,324M / 50.41%; the guide moved it to $2,362M / 49.78% by 11 Sep (WS03).

## What failed / what I changed while building

- First cut of the interval logic gave LIVE h=3-5 rows an additive fallback sd of 3.0 on *dollar* metrics (a 1,257-1,265 band on
  2Q27 EBITDA) and made adj EBITDA $ additive because one 2021Q4-vintage pool row was negative. Fixed: relative/additive is
  decided by metric class (positive level metrics relative; ratios, per-night, EPS and zero-crossing levels additive), non-positive
  rows are dropped from relative pools, and horizons without a realised pool borrow the deepest backtested horizon's pool (labelled
  `_borrowed_h2` in `notes`).
- The frozen validator's strict window check rejects any LIVE quarter after 2026Q3 (`LIVE_TARGETS == ['2026Q3']`, README says
  "2026Q3 or later"); every revenue package that registered 2026Q4 passed `strict_windows=False`. The margin wrapper does the
  same and applies the README rule itself. Logged as a harness change request in the README.
- The frozen scorer ignores `spec_id`; the margin scorer keys on it so a grid of variants in one file scores separately.
- No fallback panel was needed; it is tested (agrees with WS02 on adj EBITDA to $1.5M, 1Q21-2Q26).

## Corrections to existing work

None to data. Two observations for the ledger owners: (1) every quarterly margin sentence in `02_guidance_ledger.csv` is coded
`value 0.0` (ceiling/floor/point), so its numeric content is "same as last year" and the direction lives in `guide_type`; a
method wanting the magnitude must map the words. (2) Frozen-harness `windows.LIVE_TARGETS` vs its README, above.

## Parameter count

Baselines: seasonal_naive 0, seasonal_naive_drift 0, trailing4 1, pct_rev_last4 2 (ratio + cushion median), guide_implied 3
(share vector), q_guide_implied 0, street 0; each +1 when a residual sd is fitted (registered `n_params`). Scorer: 1 fixed
constant (half-life 4 quarters), pre-set by the brief, not tuned.

## For the model

| item | value | unit | source |
|---|---|---|---|
| hardest margin baseline to beat, h=0 | Street MAE 1.59 W1 / 1.31 W2 (rw 1.25 / 1.12), n 14 / 10 | pp | `scoreboard_margin.csv`, object street |
| naive margin MAE, h=0 | 2.24 W1 / 1.96 W2 (rw 1.91 / 1.75) | pp | same, seasonal_naive |
| Street margin bias at guide date, h=0 | -1.22 W1 / -1.13 W2 | pp | same |
| cost-line $ baseline to beat | seasonal_naive_drift: CoR 24 / 27, Ops 19 / 17, PD 10 / 9, S&M 32 / 31, SBC 12 / 11, D&A 3 / 3 (W1 / W2 MAE) | USD m | `hardest_baseline_by_target.csv` |
| revenue leg for backtests | `revenue_forecast_pit` (frozen guide-cushion h=0, naive beyond) | USD m | `revenue_leg_pit.csv` |
| LIVE revenue leg | 3Q26 4,815; 4Q26 3,237; 1Q27 3,121; 2Q27 4,205 | USD m | same (bridge v3 is the adopted path; this leg is the baseline's) |
| seasonal EBITDA shares FY23-25 | Q1 9.1 / Q2 22.9 / Q3 48.8 / Q4 19.1 | % of FY | `seasonal_shares.csv` |
| direction rule candidate (M-method) | last-year margin ±1.5 pp in the sentence's direction: MAE 1.43 W1 / 1.17 W2 in-sample, sign right 13/14, 9/10 | pp | diagnostic in this note; not registered |

## For the 5 Nov card

Baseline row for 3Q26: naive 50.1% / $2,051M; Street (11 Sep) 49.8% / $2,362M; FY-floor-implied 49.4% / $2,377M; management
"down slightly vs 50.1%". The harness's job on 5 Nov is to score every method's 3Q26 row against the print at these three
comparison columns; the naive band is 46-54% (80%), the Street band 47.8-51.7%.

## Discussion response (WS22, group C, 14 Sep 2026)

WS21's central finding (R01) is against the harness, and it is **accepted in full**: the flag the README told
every method author to quote is close to free at this n. The fix is a test, and it is now in the scorer.

| finding | decision | reproduced | what changed |
|---|---|---|---|
| **R01** `survives_both_windows` is ~30% free (sign-flip null 22.1 expected vs 25 observed, P 0.39; W2 ⊂ W1) | **ACCEPT** | yes — `check_07_survivor_placebo.py` re-read; the structural argument needs no simulation: W2's 10 target quarters are a subset of W1's 14, so the two flags are one sample and its tail | new scorer columns (below) and a rewritten instruction in `scoreboard_margin.md`'s header and in README §6.1: quote "beats `<baseline>` by d, better in k of n quarters, sign-test p", **never** "survives both windows". |
| **R02** no non-Street margin win is distinguishable from zero | **ACCEPT** | yes, on the new columns: of the 150 (object, spec, window) cells at `adj_ebitda_margin_pct`, h=0, PIT, excluding baselines, **52 carry both survivor flags (26 object-spec pairs); 14 cells (7 pairs) survive the n>=8 and W1 sign-test gates, and 6 of the 7 are M5 street-bias specs** (the seventh is M3's `last_pin`, whose W1 mean d is −0.03pp) | same columns; WS23 can now filter instead of arguing. |
| **R08** flags asserted on as few as 2 matched quarters | **ACCEPT** | yes — `guide-policy-margin/q4_implied\|guide_mid` carries both flags on n=2 in W2 (4 both-flag cells across the whole registry have `n_min_both_windows < 8`) | new column `n_min_both_windows` and the gated flags `survives_both_windows_n8` / `survives_both_windows_sig`. The original flags are **untouched**, so nothing that has already been quoted moves. |
| **R09** `replays_present` reads 1 for all 1,452 baseline rows | **ACCEPT (additively)** | yes — the baselines write `\|PIT` / `\|full_sample` into `spec_id`, which is in the group key | new column `replays_present_fixed` (the same count with that suffix stripped) reads **2** for every baseline row. `replays_present` itself is left as it was so no existing scoreboard number changes in the orchestrator's re-score. |
| **R17** h=0 is a post-letter, post-guide forecast | **ACCEPT** | yes (`panel.history_as_of`, `include_same_day=True`) | no code change — this is the frozen convention and changing it would break comparability with the revenue harness. Stated in README §2 and to be stated on the card: a 4Q26 trade into 5 Nov is an h=1-type position, not an h=0 one. |

**The new columns** (`analysis/src/margin_build/10_harness_margin/harness_margin/significance.py`, wired into
`score.py`; all new, none replaced). For each scored cell, against `seasonal_naive` and against `street`, on
matched quarters: `d_mean_<b>` (mean paired loss differential `|e_method| − |e_base|`, negative = better),
`t_nw1_<b>` / `p_nw1_<b>` (Newey-West(1) SE, two-sided), `k_better_<b>` / `n_cmp_<b>` / `p_sign_<b>` (one-sided
exact binomial sign test, ties dropped), plus `n_min_both_windows`, `w1_p_sign_seasonal_naive`,
`survives_both_windows_n8`, `survives_both_windows_sig` and `replays_present_fixed`. The markdown scoreboard
gains three columns (`k/n`, `p_sn`, `p_street`) and a header paragraph carrying R01's null result. The NW(1)
and sign-test conventions are byte-for-byte WS21's (`check_02` / `check_10`), so the discussion numbers and the
scoreboard numbers are the same numbers. A 12th unit test (`test_significance_columns_known_answer`) pins the
sign test, the differential and the n-gate on a hand case; **`tests.py` is 12/12 under `py -3.13`**.

**WS20's question 13 (an `is_oracle` column instead of a naming convention): done.**
`significance.mark_oracle()` writes a boolean `is_oracle` from `ORACLE_MARKERS = ("revknown", "nightsknown",
"ebitda_known")` matched against `object|spec_id`. It flags **756 of 6,768** scored cells across 14
(method, object, spec) combinations — WS21's six, their `lines` twins, and M7's four `ebitda_known` specs. It is
a marker, not a filter: the rows stay registered and scored, which is what the two-replay discipline wants.
`scoreboard_significance.csv` already carries it. WS20's other two asks to the harness — the interval recipe for
WS23 and whether a second (bridge v3) revenue leg should exist — are answered in
`docs/margin-build/discussion/group_C.md` §4; the short version is that the LIVE leg should gain a second,
clearly named `bridge_v3` column and the **backtest leg must not change**, because every registered row and both
replays were scored against it.

`survives_both_windows_sig` is deliberately gated at the **W1** sign test with **p < 0.10**, not W2 at 0.05:
W2 is a subset of W1, so a W2-only result is the tail of the same sample, and at n=14 the sign test cannot
return anything between 0.090 (10/14) and 0.029 (11/14) — a 5% line at this n is a 11-of-14 line, which is a
harder bar than the evidence in this run can carry. The gate is a filter for WS23, not a pass line.

**Because three discussion agents were running, `score.py` was NOT re-run.** The same columns were computed
straight from `scoreboard_by_quarter.csv` by a new standalone script, so WS20/23 has the numbers now:

```
py -3.13 analysis/src/margin_build/10_harness_margin/significance_check.py   # exit 0, ~2 min
```
-> `data/processed/margin_build/10_harness_margin/scoreboard_significance.csv` (6,768 cells; existing MAE
ratios and flags joined to the new statistics). When the orchestrator re-runs `score.py`, `scoreboard_margin.csv`
will carry the same columns and this file becomes redundant.

## RESUME

The harness is complete and scored; nothing is pending in WS10. If WS02 or WS03 are rebuilt, re-run
`py -3.13 analysis/src/margin_build/10_harness_margin/run.py` (it re-derives targets from the WS02 panel, validates it,
and falls back to the repo panels only if validation fails — check `targets_source.json`). Method authors: read the README,
use `py -3.13`, register both replays and h=0,1,2 at all 14 W1 dates plus LIVE h=0..5 at `TODAY = 2026-09-11`, put variants in
`spec_id`, and re-run `score.py`; quote a result only if both `survives_both_windows` and `rw_survives_both_windows` are True.
Two cheap follow-ups if anyone has time: (a) a `street_post_guide` object (WS03 `guided_q_post_guide_5td`) registered at a
later vintage is not possible under the frozen vintage rule — leave it; (b) the ±k direction rule above is the obvious first
M-method test, with k fit PIT on the magnitude of past y/y moves in that direction.

**RESUME addendum (WS22, 14 Sep).** The scorer now carries paired-loss and sign-test columns, n-gated survivor flags, `replays_present_fixed` and `is_oracle`; `tests.py` is 12/12 and `score.py` was deliberately NOT run (the orchestrator re-scores once). Next agent: run `score.py` once, confirm `scoreboard_margin.csv` gains the new columns and that no pre-existing column changed, then delete `scoreboard_significance.csv` as redundant. Outstanding: the LIVE-only `bridge_v3` revenue leg (§4 of the group C discussion note) — additive, ~30 lines, must not run concurrently with another method's `run.py`.
