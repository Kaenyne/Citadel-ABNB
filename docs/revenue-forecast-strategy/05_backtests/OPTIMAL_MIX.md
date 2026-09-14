# optimal-mix — finding the optimal combination of methods

Package: `analysis/src/forecast_methods/optimal_mix/`
Data: `data/processed/forecast_methods/optimal_mix/`
Registry: `data/processed/forecast_methods/registry/optimal-mix__*.csv` (20 files)
Run: `/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/optimal_mix/run.py` — exit 0, 504 scheme rows, 440 single-method rows.

---

## 0. The headline, in four sentences

1. **No combination scheme beats the best single method on both windows, for any target.**
   Under the pre-registered rule the verdict is the same eighteen times over:
   *the best single method is the mix.*
2. But the bar is an **oracle**. Against the *implementable* single-method choice —
   pick the lowest-trailing-MSE candidate at each guide date, which is what an analyst
   could actually have done — the combination wins on **both** windows in **16 of 18**
   target/pool cells. Combining is not free money against the true best model; it is a
   large and reliable insurance premium against picking the wrong one.
3. On revenue level, every scheme independently converges on the same answer:
   **guide × (1 + trailing-8 cushion)**. BMA on the full 14-candidate pool puts
   0.546 on `baselines guide_cushion` and 0.454 on `guidance-policy print_from_guide`
   and gives all twelve others — including all seven kernel objects — less than 0.5%.
   The kernel earns zero weight *once a guide exists*, and essentially all of the
   weight in the pool where no guide exists. That is the sharpest statement in the
   whole programme about where our edge is and is not.
4. The combined 3Q26 print is **$4,816M**, 80% conformal interval **$4,757–4,876M**
   (n_cal = 8, attainable band 88.9–100%, exchangeability violated). The combined
   4Q26 guide midpoint is **$3,142M** with no fee step and **$3,181M** at half weight,
   predictive sd **2.73%**, P(guide below Zacks $3,200M) **0.75 / 0.59** and
   P(guide below the 36-analyst $3,158M) **0.58 / 0.40**.

---

## 1. Method

### 1.1 Candidates

A **candidate** is a `(method, object, spec_id)` triple, with the `PIT`/`full_sample`
token stripped out of `spec_id` so one candidate has one identity across both replays.
Without that strip, `ar1|gbv_musd|PIT` and `ar1|gbv_musd|full_sample` are two different
candidates and the full-sample replay silently pools to nothing; this bit me on the
first run and is worth flagging to other packages that key on `spec_id`.

110 candidates exist in the registry. The `tracker-backlog` objects carry eight specs
each, which the harness scorer pools into one series; **optimal-mix scores per spec**,
matching the fix the scoreboard agent applied.

### 1.2 Pools, declared on coverage and on published attributes only

| pool | membership rule | why it is leakage-free |
|---|---|---|
| `all` | every candidate covering all 14 W1 target quarters | coverage, not performance |
| `noguide` | `all` minus everything that consumes a guide or a consensus number (`guide_cushion`, `street`, `print_from_guide`) | a structural property of the object |
| `parsimonious` | `all` restricted to candidates whose **published** `n_params` ≤ 2 | an attribute each package published itself |
| `repaired` | take rate only: `all` minus `calibration-rail ref_*` | a known harness classification bug, not a forecast (see §5) |

Two candidates are excluded from every pool, declared before any scoring:
`baselines naive_seasonal` (the harness README calls it a transparency object, not the
ratio denominator and not a forecast anyone would run) and
`l1-reconciliation revenue_contemporaneous` (its own package declares it a deliberate
negative control, RMSE ratio 11.3). Partial-coverage objects — `calibration-rail`'s two
GBM objects, `l1`, `fx-lag`'s H2 — fall out on the coverage rule, not on a judgement.

### 1.3 Schemes

| scheme | definition | free parameters |
|---|---|---|
| `equal` | 1/K | 0 |
| `inv_mse` | ∝ 1 / trailing MSE | 0 (deterministic in the training block) |
| `stack_ls` | min ‖y − Fw‖², w ≥ 0, Σw = 1 | K − 1 |
| `stack_shrunk` | 0.5·`stack_ls` + 0.5·`equal`, shrinkage fixed a priori | K − 1 |
| `bma_logscore` | ∝ exp(Σ_t log N(y_t | f_it, s_it)), uniform prior | 0 |
| `top3_inv_mse` | keep the 3 lowest-trailing-MSE candidates, inverse-MSE weight them | 0 |
| `top1_trailing` | **comparator, not a combination**: the single lowest-trailing-MSE candidate | 0 |

`stack_ls` is solved by NNLS on a design augmented with a heavily weighted sum-to-one
row, then polished by SLSQP, keeping whichever objective is lower. **This matters**:
SLSQP alone stalls at its starting point whenever K is large relative to T, which
silently returned the equal weights and made the stack look identical to `equal` on the
14-candidate pool. The first run of this package reported exactly that artefact. It was
a solver failure, not a finding.

Below `MIN_TRAIN = 4` training pairs every scheme falls back to equal weights.
BMA takes each candidate's registered `sd`, or `(q90 − q10)/2.5631` when `sd` is absent.

The combined predictive sd is the **mixture** sd, `√(Σ wᵢ(sᵢ² + (μᵢ − μ̄)²))`, not
`√(Σ wᵢ²sᵢ²)`: disagreement between candidates is genuine predictive uncertainty and
must widen the interval, not narrow it.

### 1.4 The winner rule

A scheme is the winner for a `(target, pool)` only if its RMSE is below the best single
candidate's RMSE on **both** W1 and W2. Otherwise the table records
`BEST SINGLE METHOD IS THE MIX`. `top1_trailing` is reported alongside but can never be
declared the winner, because it is a selection rule, not a combination.

---

## 2. Leakage controls

1. **Leave-future-out weights.** The weights used at guide date *d* are fit only on
   `(forecast, outcome)` pairs whose target quarter has `print_date < d`, taken from
   `calendar.csv`. Expanding window; no lookahead and no re-use of the quarter being
   forecast. `combine.py` has no notion of time at all — the training block is assembled
   by the caller — so the schemes cannot leak on their own.
2. **Both windows, always.** Every scheme is scored on W1 (14 targets, 1Q23–2Q26) and
   W2 (10 targets, 1Q24–2Q26) and a result is quoted only if it survives both. The W2
   training history is allowed to reach back into 2023 — those quarters printed before
   the W2 vintages, so using them is point-in-time correct, not leakage.
3. **Both prior replays, published side by side** in `07_replay_pit_vs_fullsample.csv`.
4. **Pool membership is never chosen on performance.** Every pool rule is coverage,
   a structural property, or a published `n_params`. Where performance-based pruning
   is wanted, it is done *inside* the replay by `top3_inv_mse` and `top1_trailing`,
   which prune on trailing MSE only and are therefore leave-future-out themselves.
5. **The 2026-08-06 guide is LIVE** and enters no metric and no gate. All backtest rows
   stop at 2026Q2.
6. **The Street is vintage-stamped by the harness**, which raises `StreetVintageError`
   on any consensus row postdating the vintage. The September vendors are never used as
   the 6-Aug pre-guide Street. The Zacks 4-Sep and Alpha Vantage 11-Sep anchors appear
   only against the 2026-09-11 live objects, with their `as_of` carried in the JSON.
7. **No candidate is re-derived.** optimal-mix reads registered points and quantiles and
   never recomputes another package's number, so it cannot quietly disagree with a
   package's own published figure.
8. **Own output excluded** from the input registry on every run.

---

## 3. Results

### 3.1 The verdict table (PIT replay, `04_winner_per_target.csv`)

RMSE in the units of the target. "mix" = the best-by-W1 combination scheme.

| target | pool | best scheme | mix W1 | mix W2 | best single (oracle) | oracle W1 | oracle W2 | top1 W1 | top1 W2 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| revenue_musd | all | bma_logscore | 40.60 | 33.92 | baselines guide_cushion | 35.46 | 34.60 | 40.87 | 34.38 | single |
| revenue_musd | parsimonious | bma_logscore | **33.88** | 36.04 | baselines guide_cushion | 35.46 | 34.60 | 34.66 | 37.06 | single |
| revenue_musd | noguide | top3_inv_mse | 66.77 | 63.60 | kernel last3_ex_covid | 52.21 | 51.19 | 74.53 | 74.69 | single |
| revenue_yoy | all | equal | 3.48 | 2.16 | tracker unearned_rnpl k1.0 | 2.60 | 2.54 | 4.86 | 4.57 | single |
| nights_yoy | all | bma_logscore | 3.46 | 2.07 | tracker unearned_rnpl k0.5 | 2.16 | 1.89 | 3.51 | 2.19 | single |
| take_rate_pct | repaired | inv_mse | 0.3274 | **0.3199** | fee-takerate lastyear | 0.3262 | 0.3354 | 0.3379 | 0.3348 | single |
| take_rate_pct | all | inv_mse | 1.374 | 0.878 | fee-takerate lastyear | 0.3262 | 0.3354 | 1.378 | 0.887 | single |
| gbv_musd | all | stack_shrunk | 947.0 | 753.0 | baselines naive | 722.0 | 737.3 | 955.0 | 766.9 | single |
| nights_m | all | top3_inv_mse | 4.90 | 2.87 | baselines naive | 3.17 | 2.59 | 4.94 | 2.96 | single |
| adr_yoy | all | stack_ls | 1.924 | 2.198 | calibration-rail ref_ar1 | 1.880 | 2.156 | 1.870 | 2.132 | single |
| gbv_yoy | all | stack_shrunk | 5.09 | 3.49 | calibration-rail ref_naive | 3.66 | 3.42 | 5.13 | 3.58 | single |

**Eighteen cells, eighteen "best single method is the mix".** Two are dead heats worth
naming rather than dismissing:

* **revenue level, parsimonious pool.** BMA is 4.4% *better* than guide+cushion on W1
  (33.88 vs 35.46) and 4.2% *worse* on W2 (36.04 vs 34.60). That is precisely the
  pattern the both-windows rule exists to catch: a scheme that looks like an
  improvement on one origin and an equal-sized deterioration on the other is noise on
  n = 14 and n = 10, not signal.
* **take rate, repaired pool.** The mix is 0.4% worse on W1 and 4.6% better on W2 — a
  tie, on a two-candidate pool, on a target where **nothing beats a plain seasonal
  naive** anyway (every ratio in the table is above 1.00).

### 3.2 Improvement over the best single method, stated honestly

Against the **oracle** best single: the mix improves nothing on both windows.
Best single-window improvements: revenue parsimonious +4.43% on W1, take-rate repaired
+4.64% on W2, revenue `all` +1.95% on W2. Median deterioration across the eighteen
cells, on the worse of the two windows, is about **−10%**.

Against the **implementable** best single (`top1_trailing`, which is what "use the best
method" actually means before you know the answer), the mix wins on both windows in
**16 of 18** cells. The two losses are both `adr_yoy`, where the pool is three
near-identical calibration-rail references and there is nothing to diversify.
The margins where it matters:

| target / pool | mix W1 | top1 W1 | mix W2 | top1 W2 |
|---|---|---|---|---|
| revenue_musd / noguide | 66.77 | 74.53 (−10.4%) | 63.60 | 74.69 (−14.8%) |
| revenue_yoy / all | 3.48 | 4.86 (−28.5%) | 2.16 | 4.57 (−52.6%) |
| revenue_musd / parsimonious | 33.88 | 34.66 (−2.2%) | 36.04 | 37.06 (−2.8%) |

That is the defensible sentence for a judge: *combining does not beat the model that
turned out to be best; it beats the model you would have chosen.*

### 3.3 The revenue-level weights — the most quotable result

BMA weights at the last W1 vintage (2026-05-07, target 2026Q2), 14-candidate pool:

| candidate | weight |
|---|---|
| baselines guide_cushion | **0.5457** |
| guidance-policy print_from_guide | **0.4542** |
| the other twelve, including all seven kernel objects | < 0.005 combined |

`stack_ls` on the 6-candidate parsimonious pool, same vintage:

| candidate | weight |
|---|---|
| guidance-policy print_from_guide | 0.6717 |
| baselines guide_cushion | 0.1821 |
| baselines street (pre-guide, vintage-stamped) | 0.1462 |
| naive / ar1 / trailing4 | 0.000 |

Read together: once the guide exists, a leave-future-out optimiser puts **~85–100% of
its weight on the guide-plus-cushion object** and nothing on the kernel, the AR(1), the
trailing mean or the naive. The one thing it adds to the guide is a ~15% tilt toward
the pre-guide Street — a genuinely new, small, earned result.

In the **no-guide** pool, which is the pitch-date information set, the weight goes
where it should:

| candidate (top3_inv_mse, 2026Q2 vintage) | weight |
|---|---|
| kernel-lambda revenue_level_next_q_ex_covid | 0.3965 |
| kernel-lambda revenue_level_next_q_last3_ex_covid | 0.3965 |
| guidance-policy print_kernel_policy | 0.2069 |

100% on the kernel family. The two models are not competitors; they occupy different
information sets, and the combination makes that visible rather than asserting it.

### 3.4 Calibration

For revenue level, `all` pool, PIT (from `03_scheme_scores.csv`):

| scheme | W1 RMSE ratio to naive | W2 ratio | W1 CRPS | W1 PIT KS p | W1 80% coverage |
|---|---|---|---|---|---|
| equal | 0.637 | 0.573 | 41.32 | 0.018 | 1.00 |
| inv_mse | 0.521 | 0.433 | 33.80 | 0.039 | 1.00 |
| stack_ls | 0.456 | 0.347 | 29.56 | 0.208 | 1.00 |
| stack_shrunk | 0.540 | 0.456 | 36.16 | 0.034 | 1.00 |
| **bma_logscore** | **0.432** | **0.313** | **25.76** | 0.139 | 1.00 |
| top3_inv_mse | 0.466 | 0.361 | 28.77 | 0.159 | 1.00 |
| guide_cushion (best single) | 0.377 | 0.319 | — | — | — |

`equal` and `inv_mse` are **rejected on the PIT** at the 5% level on W1 (KS p 0.018 and
0.039): they are systematically biased high (+29.2 and +23.1 musd) because the pool
contains twelve candidates that over-forecast. `stack_ls` and `bma_logscore`, which zero
those candidates out, pass. 80% coverage is 100% everywhere — the mixture intervals are
too wide, which is the honest direction to be wrong in but is not calibrated.

### 3.5 PIT prior vs full-sample prior — the clearest leakage evidence in the programme

`07_replay_pit_vs_fullsample.csv`. Negative = full-sample priors look better.

| target / pool | scheme | PIT RMSE | full-sample RMSE | delta |
|---|---|---|---|---|
| revenue / noguide W1 | top3_inv_mse | 66.77 | 35.97 | **−30.80** |
| revenue / noguide W1 | bma_logscore | 66.82 | 38.08 | **−28.74** |
| revenue / noguide W2 | top3_inv_mse | 63.60 | 35.35 | **−28.25** |
| revenue / all W1 | equal | 59.88 | 43.86 | −16.03 |
| revenue / parsimonious W1 | bma_logscore | 33.88 | 38.68 | +4.79 |

The kernel-based no-guide pool nearly **halves** its error when its seasonal λ cells are
estimated on the full sample. That is the single largest replay gap in the package and
it is entirely a property of the kernel objects, not of the combination: the guided and
parsimonious pools, which lean on the cushion, are almost replay-invariant or slightly
*worse* under full-sample priors. Any kernel walk-forward number quoted without saying
which replay produced it is off by roughly a factor of two. This corroborates the
scoreboard's finding that the kernel's quoted 1.74% walk-forward MAE is not reproducible
under strict PIT.

Separately, `top1_trailing` gets *worse* under full-sample priors on the guided pools
(+13.5 W2 `all`, +20.0 W2 parsimonious): full-sample estimation makes the candidates
more alike, so the trailing-MSE pick flips more often. Model selection is less stable
than model combination — which is the argument for combining, restated in the data.

---

## 4. The combined live objects

`data/processed/forecast_methods/optimal_mix/combined_live_objects.json`.

### 4.1 3Q26 print — revenue

Scheme `bma_logscore`, pool `all`, weights fit on everything that printed before
2026-08-06 (13 pairs). Live weight coverage 1.00 (every weighted candidate has a LIVE
row or a declared carrier).

* **Point $4,816.1M**, mixture sd $48.0M, q10–q90 **$4,754.7–4,877.6M**.
* **Split-conformal 80% interval $4,756.7–4,875.6M**, half-width $59.5M, from the
  combination's own 14 walk-forward residuals, n_cal = 8.
  **Exchangeability is violated** — expanding-window refits on a trending target with a
  2022 regime change — so at n_cal = 8, α = 0.2 the attainable coverage band is
  **[88.9%, 100%]** and **no 80% guarantee exists**. The interval is descriptive.
* vs the guide range $4,690–4,770M: above the top of the range, which is what a
  +1.86% cushion implies. vs Zacks $4,740M (as of 2026-09-04): **+$76M**.
  vs the LSEG pre-guide $4,610M (as of 2026-08-06): +$206M.
* Carrier mapping: the six `kernel-lambda revenue_level_next_q*` pool members have no
  LIVE row of their own and are mapped onto `kernel-lambda live_3q26_print`;
  `revenue_level_h1` is a different horizon and its weight is dropped and renormalised.
  All of these carry < 0.5% weight, so the mapping changes the answer by under $0.1M.

### 4.2 3Q26 print — the other metrics

| object | pool | scheme | point | q10–q90 | status |
|---|---|---|---|---|---|
| take_rate_pct | repaired | inv_mse | **17.81%** | 17.24–18.37 | OK |
| nights_m | all | top3_inv_mse | 147.38 | 143.43–151.32 | OK |
| gbv_musd | all | stack_shrunk | 26,549.8 | 25,456–27,643 | OK |
| adr_yoy | all | stack_ls | +5.27% | 2.55–7.98 | OK |
| gbv_yoy | all | stack_shrunk | +15.94% | 11.27–20.60 | OK |
| nights_yoy | all | bma_logscore | 10.34% | 7.47–13.22 | **NOT USABLE** |

`nights_yoy` fails a check I built in deliberately: the winning weights sit almost
entirely on `tracker-backlog` specs, **none of which registered a LIVE 2026Q3 row**, so
the surviving weight coverage is 2.4e−11 and the printed number is a renormalisation
onto `calibration-rail ref_naive`, not the mix. It is labelled `NOT USABLE` in the JSON
rather than quietly published. Same gap, smaller, for `revenue_yoy`. **Package gap for
tracker-backlog and kernel-lambda: register LIVE 2026Q3 rows for the growth targets.**

**Take rate against the pre-registration.** The frozen 3Q26 threshold is ≥ 18.10% if the
fee migration is flowing. The combination says 17.81% with sd 0.44, so
**P(clearing 18.10%) = 0.254**. That is the power of the test made visible, as the
conflicts document asked: the pre-registration as written is a coin-toss-or-worse test
that our own central case expects to fail. Note also that no take-rate object of any
kind beats a plain seasonal naive on either window, so the 17.81% is a mechanism story
with no backtest support behind it — carry it as a mechanism, not as a forecast.

### 4.3 The 5 Nov 2026 guide midpoint for 4Q26

4Q26 is **not guided** at the pitch date, so the uncertainty must come from the
**no-guide** combination's own walk-forward error, not from the guided pool's.
That is **2.73% of level** (the wider of W1/W2, `top3_inv_mse`), against the 3.03pp the
guidance-policy package assumed and the 2.6pp the architect assumed. Central
GBV_3Q26 $26,300M.

| case | print | guide mid | guide range | P(guide < Zacks $3,200M, 10 est., 4 Sep) | P(guide < AV 36-analyst $3,158M, 11 Sep) |
|---|---|---|---|---|---|
| no fee step | 3,199.9 | **3,141.6** | 3,115–3,168 | **0.752** | **0.576** |
| half-weight fee step | 3,239.9 | **3,180.9** | 3,154–3,208 | **0.587** | **0.396** |
| full-weight fee step | 3,279.9 | 3,220.1 | 3,193–3,248 | 0.409 | 0.240 | 

The full-weight row is printed for completeness and **excluded from the quoted range**:
`fee-takerate` measures θ below 1, at which the migrated cohort's GBV *falls*.
Across the whole GBV grid $25,900–27,000M the guide midpoint spans $3,110–3,277M.

**The trade flips on the vendor.** 59–75% against Zacks; 40–58% against the 36-analyst
panel — a coin toss. Name the vendor and the timestamp or do not state the trade. And
say first that **consensus disagrees with itself by $126M** (Zacks' own quarterly sum
$14,226M against its own FY26 $14,100M), which is larger than our edge.

These numbers are tighter than the guidance-policy package's own
(0.730/0.568 and 0.579/0.406) purely because the combination's measured sd is 2.73%
rather than the 3.03pp assumed there. The direction of every conclusion is unchanged.

### 4.4 FY27 and the Feb-2027 guide

Carried from `l1-reconciliation`, with the FX term from `fx-lag` and the fee delta from
`fee-takerate`. optimal-mix does not re-derive any of it.

* FY27 revenue **$15,837.6M** at kernel w = 2/3; $15,779.5M at 0.50; $15,720.3M at 0.33.
  Growth **+11.52%**. Kernel-weight sensitivity **$117.3M / 2.34pp of growth**.
* Street (Zacks, as of 2026-09-04) $15,730–15,760M → we are **+0.59%**.
  Street-implied FY27 growth +11.43% → our growth edge is **+0.09pp**.
  Say that in the first 200 words; it is inside the kernel's own walk-forward error and
  a judge finds it in ninety seconds.
* Decomposition, one owner per line, carried verbatim: NA nights +2.34, EMEA +2.90,
  LatAm +1.60, APAC +1.41 (volume +8.26); within-region ADR ex-FX +3.00, deliberately
  unsplit; geographic mix −1.09 as an identity output; unit size and LOS +0.38;
  seats and hotel dilution 0.00 (nets out of GBV); booking-date FX **0.00** — already
  inside the lagged GBV base and never subtracted a second time; fee +0.90, new lines
  +0.20, regulation −0.30, hedge 0.00, all **assumed and not rebuilt tonight**;
  kernel timing +0.17 as an identity. Total **+11.52%**.
* **FX term from fx-lag: +0.2pp**, the revenue-*weighted average* of the four quarterly
  y/y contributions on spot held. The sum, 0.9, is meaningless and must not be quoted.
  This is the stated-series reading; it does not re-enter the decomposition, whose
  booking-date FX line stays at 0.00.
* **Fee line from fee-takerate: −0.31pp.** At central θ = 0.833 the +0.90pp half-weight
  fee line is 0.31pp too generous.
* **The Feb-2027 "FY27 guide" does not exist as a point.** ABNB guides a 1Q27 revenue
  range plus qualitative FY colour. The comparable object is the 1Q27 guide midpoint,
  which lives in `l1_unregistered_fy27_revenue.csv` ($2,996M print at w = 2/3). Do not
  let the memo imply management gives an FY27 revenue number in February.

### 4.5 The forward-multiple implication, applied once

Rule: **+0.48 EV/EBITDA turns per point of forward revenue growth**, applied **once**,
to our FY27 growth minus the Street-implied FY27 growth.

* Growth edge **+0.09pp → +0.043 EV/EBITDA turns.**
* Kernel-weight sensitivity (w from 0.33 to 0.667, 2.34pp of growth) → **±1.12 turns.**

This is an **implication, not a price target**, and the honest reading is uncomfortable
and worth saying out loud: **the kernel-weight indeterminacy is worth roughly 25× more
multiple than our level edge over the Street.** Which is exactly why the pitch is about
the *guide* and the *composition*, not about the FY27 level.

---

## 5. What failed, and the bugs found

1. **The winner rule fails everywhere.** Eighteen cells, zero winners. Published as the
   primary negative.
2. **`equal` and `inv_mse` are PIT-rejected** on revenue level W1 (KS p 0.018, 0.039),
   biased +29 and +23 musd. A large pool with a majority of over-forecasting candidates
   makes naive averaging actively harmful.
3. **SLSQP stalled** at the equal-weight start for K = 14, making `stack_ls` identical
   to `equal` on the first run. Fixed with an NNLS simplex solve plus polish. Flagged
   here because it is the kind of silent numerical failure that reads as a finding.
4. **`spec_id` embeds the prior_basis token** in `baselines` and `calibration-rail`
   (`ar1|gbv_musd|PIT`). Any consumer keying on `spec_id` sees two candidates where
   there is one. optimal-mix strips the token; other packages should too.
5. **The harness take-rate classification bug is confirmed and quantified.** With the
   `calibration-rail ref_*` rows in the pool, the best mix RMSE is 1.374 (ratio 4.23 to
   a plain seasonal naive); with them removed it is 0.327 (ratio 1.007). A 4.2×
   difference, entirely from three rows the harness generated wrongly.
6. **No LIVE rows for the growth targets.** `tracker-backlog` (both objects) and
   `kernel-lambda revenue_yoy_next_q` register no LIVE 2026Q3 row, so the combined
   `nights_yoy` and `revenue_yoy` live objects cannot be produced and are labelled
   `NOT USABLE`. This is the one thing that would materially improve the package.
7. **`fx_pts_revenue` is not combinable.** Only H3 covers all 14 W1 quarters; H2 covers
   10. A two-candidate mix exists on W2 alone and therefore can never survive the
   both-windows rule. **The best single method is the mix: `fx-lag` H3.**
8. **`guide_mid` is not combinable.** One object (`guidance-policy guide_mid_next_q`)
   is registered against that target; there is nothing to combine. It loses to the
   Street on both windows (Gate G4 fails), and combining cannot rescue it.
9. **80% coverage is 100% everywhere.** The mixture intervals are too wide. Conservative,
   but not calibrated, and it should not be presented as an 80% interval without the
   attainable-band caveat.

## 6. Parameter counts

| object | free parameters |
|---|---|
| `equal`, `inv_mse`, `bma_logscore`, `top3_inv_mse`, `top1_trailing` | **0** beyond the candidates' own; the weights are deterministic functions of the training block |
| `stack_ls`, `stack_shrunk` | **K − 1** (13 on the `all` revenue pool, 5 on parsimonious, 1 on the take-rate repaired pool) |
| shrinkage intensity λ = 0.5 | fixed a priori, not fitted |
| BMA prior | uniform over the pool, not fitted |

The winning schemes on every target that matters (`bma_logscore`, `inv_mse`,
`top3_inv_mse`) add **zero** free parameters. The combination layer costs nothing in
parameter count; where it spends parameters (`stack_ls`), it does not win.

## 7. Caveats

* n is 14 and 10. A 4% RMSE difference is not a result. That is the honest reading of
  both dead heats in §3.1 and it is why the both-windows rule is doing real work here.
* The oracle best-single comparator is not achievable in practice; the implementable
  comparator (`top1_trailing`) is the fair one and the mix wins against it. Both are
  reported and neither is hidden.
* The combined intervals are Gaussian summaries of a mixture. They are wide (100%
  coverage) and the conformal half-width is the more honest width.
* Split conformal here is **descriptive, not a guarantee**: exchangeability is violated,
  and at n_cal = 8, α = 0.2 the attainable band is [88.9%, 100%].
* FRED daily FX ends 2026-08-28, so nothing downstream of `fx-lag` is genuinely as of
  11 Sep. The 15 Sep / 13 Oct fee-migration deadlines have no source in the repository.
* The 4Q26 GBV grid is an input, not a forecast. The $3,110–3,277M guide-midpoint span
  is driven by that grid far more than by anything optimal-mix estimates.
* Everything in §4.4 is carried, not rebuilt. The four lines marked
  `assumed_not_rebuilt_tonight` (+0.90 fee, +0.20 new lines, −0.30 regulation,
  0.00 hedge) are assumptions with a stated owner and no build behind them.

## 8. Harness change request

1. **A LIVE slot for annual and multi-quarter objects.** The LIVE window admits 2026Q3
   only. `l1` parks five FY27 quarters and `fx-lag` five forward rows in unregistered
   files; optimal-mix had to pass `strict_windows=False` to register the 4Q26 guide
   midpoint. Add `LIVE` acceptance for any quarter with no print date, plus an
   `FY2027`-style annual period.
2. **Strip the `prior_basis` token out of `spec_id`** in the `baselines` and
   `calibration-rail` writers, or add an explicit `spec_family` column. As written,
   `spec_id` is not a stable candidate identifier across replays.
3. **Fix the growth-vs-level classification** so `take_rate_pct` is treated as a level.
   The `calibration-rail ref_*` take-rate rows are not forecasts and should not be in
   the registry in their current form.
4. **A `weight_coverage` or `carrier` convention** for LIVE rows, so a consumer can tell
   mechanically whether a backtested object has a live counterpart. optimal-mix had to
   hard-code a `LIVE_CARRIER` map.
5. **A combination-aware scorer.** `score.py` treats each registry file independently;
   there is no way to register "this object is a function of those objects" and have the
   parameter count or the overlap accounted for.
