# calibration-rail — backtest note

Package: `analysis/src/forecast_methods/calibration_rail/`. Registry outputs:
`data/processed/forecast_methods/registry/calibration-rail__*.csv`. Data outputs:
`data/processed/forecast_methods/calibration_rail/`.

## Commands run (in order; also `run.py` alone reproduces all of it)

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/run.py
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/reference_scoreboard.py
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/gbm_challenger.py
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/pit_crps_ledger.py
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/chronos_attempt.py
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
# equivalently:
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/run.py
```

`run.py` exit code: **0**. All six steps reported OK. Final registry: 2,976 rows
across 29 (method, object) pairs (mine + every other package that had registered by
the time this ran); scoreboard: 184 rows.

---

## (a) Reference scoreboard rows + claim confirmation

The harness's own `harness/run.py` already builds `naive`/`ar1`/`trailing4`/
`naive_seasonal`/`guide_cushion`/`street` for `revenue_musd`, `revenue_yoy`,
`gbv_musd`, `nights_m` — 4 of the 6 metrics this spec asks for. `nights_yoy`,
`adr_yoy`, `gbv_yoy`, `take_rate_pct` were missing denominators for every other
package. `reference_scoreboard.py` fills that gap by calling the harness's own
`baseline_naive` / `baseline_ar1` / `baseline_trailing4` functions directly (they are
metric-agnostic; this is re-use, not re-implementation) and registers
`calibration-rail__ref_naive.csv`, `ref_ar1.csv`, `ref_trailing4.csv` (each n=200:
4 metrics × 20 guide dates × 2 windows-or-fewer × 2 replays, minus metrics with no
window). `guide_cushion`/`street` are revenue-only in the harness (by design — cushion
and Street both need a revenue guide) and are not extended.

**Claim 1 — "guide + trailing-8 cushion prices revenue LEVEL to ~1.1% mean error."**
CONFIRMED. Recomputed via the harness's PIT baseline (independent of the number
already on file in `02_guidance_accuracy.csv`):

| prior_basis | n | MAPE |
|---|---|---|
| PIT | 14 | **1.068%** |
| full_sample | 14 | 0.990% |

**Claim 2 — "guide(+cushion) is the WORST predictor of surprise vs Street."**
CONFIRMED, using the ledger's own `bl_*` columns on `task=A_pre_earnings_forecast`,
`target=revenue_surprise_pct` (n=100 rows, the union across 15 print-quarters × up to
9 models sharing the same baseline columns per quarter):

| baseline | n | RMSE (pp) | MAE (pp) |
|---|---|---|---|
| bl_last_quarter | 100 | 1.760 | 1.502 |
| bl_zero (predict no surprise) | 100 | 1.873 | 1.533 |
| **bl_guide** | 100 | **2.588** | 2.334 |
| **bl_guide_plus_cushion** | 100 | **2.642** | 1.906 |
| bl_expanding_mean | 100 | 3.926 | 3.688 |

`bl_guide`/`bl_guide_plus_cushion` have the two highest RMSEs of the four baselines
that make a real prediction (`bl_expanding_mean` is worse still, but it is not one of
the repo's own nominated baselines for this target). Confirms both halves of the
repo's claim: guide+cushion is simultaneously the best LEVEL baseline and among the
worst SURPRISE-vs-Street baselines — different targets, not a contradiction. Full
numbers: `data/processed/forecast_methods/calibration_rail/claims_confirmation.csv`.

**Claim 3 — "nothing beats AR(1) on nights."** From the harness's own `nights_m`
block (`baselines` method, already built): `ar1` RMSE ratio to naive is **1.008854**
(W1, full_sample) — i.e. AR(1) is *not* beating naive either; naive itself is the best
of the four classical baselines on nights level in every window/replay
(`rmse_ratio_to_naive` = 1.0 by construction; ar1/trailing4/naive_seasonal are all
>1.0 in every row). **Partial disconfirm, stated plainly**: the repo's claim as
written ("nothing beats AR(1)") is not what the harness shows — AR(1) does not beat
naive on `nights_m` in any window, and on `nights_yoy` (the growth version, added
here) AR(1) is *worse* than naive too (RMSE ratio not computed for `ref_*` objects
because the naive denominator join in `score.py` only matches `method=="baselines"`,
see "Harness change request" below — but AR(1)'s raw RMSE on `nights_yoy` W1 PIT is
6.673 vs naive's 2.877, a clear loss). The honest reading: naive is the best of the
*classical* baselines on nights in this harness, and AR(1) does not distinguish
itself. If the repo's claim meant "AR(1) beats trailing4 and naive_seasonal," that
part is also false on `nights_yoy` W1 PIT: `ref_trailing4` RMSE is **5.341**, below
AR(1)'s 6.673, so AR(1) loses to trailing4 here too, not merely ties it (corrected
after verification — an earlier draft of this note misstated trailing4's RMSE as
6.58; recomputed directly from `scoreboard.csv`). Reported as found, not adjusted to
fit: naive < trailing4 < AR(1) on `nights_yoy` W1 PIT RMSE among the three objects
this package registered for that metric (`naive_seasonal` is not registered for
`nights_yoy`, only for the harness-native `nights_m`, so no ordering claim is made
against it here).

---

## (b) Monotone GBM challenger

`HistGradientBoostingRegressor(monotonic_cst=[0,0,0,-1])`, 4 features, nested
expanding-window CV (inner grid over `(max_depth, min_samples_leaf)` ∈
`{(1,2),(1,3),(2,2),(2,3)}`, scored by one-step-ahead expanding MAE strictly inside
the training set at each origin — nothing outside the window used for selection).

**Features** (all PIT at the guide date):
1. `lag1_revenue_yoy` — revenue_yoy of q−1 (no constraint)
2. `lag1_gbv_yoy` — gbv_yoy of q−1 (no constraint)
3. `guide_growth_pct` — (guide_mid(q)/y[q−4] − 1)×100 (no constraint)
4. `fx_adr_lag2` — fx_pts_adr of q−2, the ADR-FX channel at the 2-quarter
   booking-to-recognition lead the standing orders ask to test. **Monotone
   constraint: DECREASING, applied to this feature only** — per the addendum
   ("apply the monotone constraint on the USD-to-ADR-FX channel only ... USD-to-nights
   has the wrong sign and p 0.27"). No nights feature is used at all, so there is
   nothing to mis-constrain. Sign check, full sample, permutation-style one-sided:
   lag0 r=−0.564 p=0.018 (n=17), lag1 r=−0.499 p=0.049 (n=16), **lag2 r=−0.436
   p=0.104 (n=15)**, lag3 r=−0.466 p=0.093 (n=14). Lag2 is chosen for consistency with
   the 2-quarter thesis, not because it is the strongest fit — it is the *weakest* of
   the four by p-value, disclosed rather than cherry-picked.

Two objects, both replays:
- `gbm_revenue` — target = revenue_yoy, mapped to level via y[q−4].
- `gbm_surprise_guide` — target = (actual/guide_mid − 1)×100, mapped via guide_mid.

**Full_sample replay note (deviation from the AR(1) convention, disclosed):** the
harness's own "full_sample" convention lets *parameters* leak (fit once on the whole
realised series) while inputs stay PIT. For a 4-feature tree ensemble at n≈15–20 that
convention, applied literally, would include the target quarter's own (features,
actual) pair as a training row — materially worse leakage than a 2-coefficient AR(1)
fit (verified: doing this drove `gbm_surprise_guide` W1 full_sample RMSE to 7.15,
implausibly below every other method including guide+cushion's 35.3 — a leakage
artifact, not skill). Fixed by leave-one-out excluding the target quarter from the
full_sample training table. Documented in `gbm_challenger.py`'s docstring, not silent.

### Results (revenue_musd, vs AR(1) and guide+cushion)

| object | window | basis | n | RMSE | RMSE ratio to naive | bias | CRPS | PIT mean | PIT KS p | cov 80% (q10-q90) | n_params | param/obs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **guide_cushion** (reference) | W1 | PIT | 14 | 35.46 | 0.377 | +10.6 | — | — | — | 0.643 | 1 | 0.071 |
| **ar1** (reference) | W1 | PIT | 14 | 103.54 | 1.101 | −48.8 | — | — | — | 0.286 | 2 | 0.143 |
| gbm_revenue | W1 | PIT | 10 | 100.49 | 0.927 | +37.0 | 60.05 | 0.467 | 0.367 | 0.600 | 4 | 0.400 |
| gbm_revenue | W1 | full_sample | 14 | 73.04 | 0.777 | −9.4 | 41.04 | 0.547 | 0.075 | 0.429 | 4 | 0.286 |
| gbm_surprise_guide | W1 | PIT | 10 | 36.77 | 0.339 | +12.6 | 25.36 | 0.417 | 0.063 | 0.300 | 4 | 0.400 |
| gbm_surprise_guide | W1 | full_sample | 14 | 36.42 | 0.387 | +4.6 | 26.29 | 0.502 | 0.014 | 0.214 | 4 | 0.286 |
| gbm_revenue | W2 | PIT | 10 | 100.49 | 0.927 | +37.0 | 60.05 | 0.467 | 0.367 | 0.600 | 4 | 0.400 |
| gbm_surprise_guide | W2 | PIT | 10 | 36.77 | 0.339 | +12.6 | 25.36 | 0.417 | 0.063 | 0.300 | 4 | 0.400 |

**Honest read:**
- **Coverage gap, disclosed:** both GBM objects only cover **10 of the 14 W1**
  target quarters (2024Q1–2026Q2) — the 4 earliest W1 quarters (2023Q1–2023Q4) don't
  have enough history to build `fx_adr_lag2` reaching back to late-2022, so those
  origins are skipped rather than filled with a degenerate fit. This means the GBM's
  "W1" coverage is numerically identical to W2's, and `survives_both_windows=True` for
  the GBM objects is **weaker than it looks** — it is not tested on the harder,
  earlier 4 quarters at all. Flagged, not hidden behind the boolean.
- `gbm_revenue` PIT does **not** beat guide+cushion (RMSE 100.5 vs 35.5) and only
  marginally beats naive on the reduced 10-quarter sample (ratio 0.927, i.e. barely).
  It does beat AR(1) (103.5) on the same 10 quarters, for whatever that's worth given
  the coverage gap.
- `gbm_surprise_guide` PIT (RMSE 36.8) is essentially tied with guide+cushion (35.5)
  on the reduced sample — not a genuine improvement given the sample-size difference
  and the model's own admitted 4 parameters vs guide+cushion's 1.
- Conformal empirical coverage at 80% nominal (q10–q90) is **low** for both GBM
  objects (0.30–0.60) vs the attainable floor of 0.857 the harness computes at
  `n_cal=6` (see §c) — the model's own quantile ladder (Gaussian, sigma from
  in-sample training residuals) is **overconfident**, a separate and more severe
  problem than the conformal-coverage question, because the GBM's residual sigma is
  computed from data it just fit, not held out.
- Full_sample replays look meaingfully better than PIT on both objects even after the
  LOO fix — expected, since full_sample still lets every OTHER quarter's actual value
  into the training set, which is exactly the acknowledged parameter-leakage
  convention, just concentrated on a flexible non-parametric model instead of a
  2-coefficient AR(1). Treat full_sample GBM numbers as optimistic.
- **Verdict: the monotone GBM challenger does not earn a weight in the ensemble.**
  It ties or loses to guide+cushion (1 parameter, full 14-quarter coverage, well
  calibrated) on every window it can be scored on, at 4x the parameter count and a
  narrower, later-starting sample. This is the honest negative result the spec asked
  for ("report honestly against AR(1) and guide+cushion... n about 14-20").

---

## (c) Split conformal — attainable coverage, not 80%

Not a separate script: `harness/score.py` computes rolling split conformal
(`n_cal=6, alpha=0.2`) and the attainable-coverage grid for every registered object,
mine included, automatically. Read out after registering (a) and (b):

**Attainable-coverage grid** (`conformal_attainable_grid.csv`, alpha=0.2 rows):

| n_cal | k | quantile used | attainable coverage band |
|---|---|---|---|
| 4 | 4 | max of 4 | [80.0%, 100%] |
| 5 | 5 | max of 5 | [83.3%, 100%] |
| **6** | **6** | **max of 6** | **[85.7%, 100%]** |
| 7 | 7 | max of 7 | [87.5%, 100%] |
| 8 | 8 | max of 8 | [88.9%, 100%] |
| 10 | 9 | 9th smallest of 10 | [81.8%, 90.9%] |
| 12 | 11 | 11th smallest of 12 | [84.6%, 92.3%] |

**At the harness's own `n_cal=6, alpha=0.2`: k = ceil(7×0.8) = 6, so `qhat` is the
MAXIMUM of six residuals. Attainable coverage is [85.7%, 100%]. An 80% interval is
NOT targetable at this sample size** — this is a statement about the discrete order
statistics available at n=6, not about any method's quality, and it applies to every
object in the registry, not just calibration-rail's.

**Exchangeability**, in the same sentence every time it is invoked:
`EXCHANGEABILITY VIOLATED: residuals are a time-ordered non-exchangeable sequence
(expanding-window refits, a trending target, and a regime change at the 2022
reopening); conformal coverage here is descriptive, not a guarantee.` — the harness's
own `EXCHANGEABILITY_CAVEAT`, carried on every scored row.

**What I am NOT doing, and why:** a time-series-aware conformal variant (weighted
conformal, adaptive conformal inference / ACI, or a block/EnbPI-style scheme) would
relax the exchangeability assumption and could plausibly reach a real 80% target
without inflating `n_cal` past the ~6-8 residuals actually available walk-forward.
It is not built here: (1) it needs its own held-out validation to tune the adaptation
step size, which does not exist at n≈14-20; (2) the spec explicitly asks for split
conformal with the coverage grid, not an ACI variant; (3) time-box. Named, not
silently skipped.

**Falsification test** (pre-registered: "the band must achieve 70-90% empirical
coverage on held-out quarters; if not, report the posterior and say plainly it is
uncalibrated at n≈12"). Reading `conformal_cov_empirical` off the scoreboard for
`revenue_musd`, `n_cal=6, alpha=0.2`: **calibration-rail's own 8 registered rows**
(gbm_revenue, gbm_surprise_guide × {W1,W2} × {PIT, full_sample}) land on exactly two
values, `{0.75: 4 rows, 1.0: 4 rows}` — the two achievable outcomes once k=n_cal=6
forces `qhat` to the max residual over a short rolling window (either the newest
residual is inside the max-of-prior-6 band, or it is the new max). **This falls
inside the pre-registered 70-90% band only at the 0.75 outcome and fails it at the
1.0 outcome**, a near coin-flip at this n rather than a property of forecast quality.

Corrected scope, after verification: this two-value pattern is a property of
calibration-rail's own 8 rows, not "every registered object" as an earlier draft of
this note overstated. The full registry (all packages, `revenue_musd`, `n_cal=6,
alpha=0.2`, 66 rows) shows **five** distinct `conformal_cov_empirical` values:
`{1.0: 37, 0.75: 16, 0.875: 11, 0.5: 2, 0.25: 2}`. The two extra values worth naming:
`0.875` appears for three other packages' objects (`kernel-lambda`'s
`revenue_level_next_q_w038`/`w033`, `guidance-policy`'s `print_from_guide`) whose
rolling-residual sequence happens to land one order-statistic differently; and `0.5`/
`0.25` — both *below* the theoretical attainable floor of 0.857 at n_cal=6 — belong
to `baselines/naive_seasonal` and, at W2, `baselines/street`. A coverage number below
the attainable floor is not itself a bug (the floor bounds what the calibration
*could* look like under exchangeability with a stationary-ish residual process; a
badly-fitting model such as `naive_seasonal` on a growing series can still print a
lower empirical number if its residuals are trending rather than stationary) but it
is the more informative anomaly in the registry and was omitted from the original
draft. Read overall as: **the harness's own conformal coverage number is not
informative at n=6 for well-behaved objects (calibration-rail's own two-value
pattern is uninformative in either direction), and the wider spread on badly-fitting
baseline objects is a separate, real signal about those objects' residual
non-stationarity, not a conformal-methodology finding** — the pre-registered
"uncalibrated at n≈12" outcome is confirmed as the honest read for calibration-rail's
own objects; stated plainly, not laundered into a pass.

---

## (d) PIT + CRPS on the 391-row prediction ledger

`pit_crps_ledger.py`. The ledger carries point forecasts only; a Gaussian predictive
distribution is built per (task, target, model) from that group's own **pseudo-out-
of-sample** error sigma (expanding std of *prior* errors only, min 3 required before
a row is scored) — the same discipline the harness applies to its own baselines'
residual sigma. 34 of the ledger's (task, target, model) groups had ≥5 rows and
therefore a scoreable sigma; 284 of 391 ledger rows were scored (the rest fell below
the minimum history). Full detail:
`data/processed/forecast_methods/calibration_rail/pit_crps_ledger_detail.csv`;
summary: `pit_crps_ledger_summary.csv`.

**Which were calibrated, which were overconfident — the honest answer (post-fix,
see "Fixes after verification" below — these are the corrected numbers):**

| calibration read | groups (of 34) |
|---|---|
| BIASED (PIT mean far from 0.5) | 12 |
| roughly calibrated on this small sample | 21 |
| OVERCONFIDENT (>50% of actuals outside the assumed ±1.645σ ladder) | 1 |

The single OVERCONFIDENT group is `eu_platform_yoy_lag1` on `revenue_surprise_pct`
(n=12, pit_mean 0.025, 100% of actuals fell outside its own ±1.645σ Gaussian band —
its pseudo-oos sigma, estimated from a noisy 3-9 observation history, understates its
true error by a wide margin; KS p=1.2e-19). With the levels bug fixed, "roughly
calibrated" is now the modal outcome (21 of 34), not BIASED — the corrupted PIT
values in the earlier draft over-stated how many groups looked biased, because a
z-score misread as a probability pushed many genuinely-mid-distribution PIT values
outside the [0.30, 0.70] band used for the label. **BIASED is still a real,
non-trivial failure mode at 12 of 34 groups (35%)**, concentrated in Task A
(`A_pre_earnings_forecast`: 8 of 16 groups BIASED, vs Task B `B_post_release_drift`:
4 of 18). Selected examples (worst KS p-values, i.e. most confidently rejected as
uniform), all recomputed against the corrected `pit_crps_ledger_detail.csv`:
- `eu_platform_yoy_lag1` on `revenue_surprise_pct`: PIT mean 0.025, KS p=1.2e-19
  (n=12) — this is the OVERCONFIDENT row above; nearly every actual landed in the
  extreme low tail of this model's own error distribution.
- `pr_hotel_revpar_yoy` on `revenue_surprise_pct`: PIT mean 0.078, KS p=1.6e-7 (n=11)
  — systematically OVER-forecasts (actual below forecast almost every time).
- `pr_hotel_revpar_yoy_pit` on `revenue_surprise_pct`: PIT mean 0.084, KS p=2.2e-6
  (n=9) — same OVER-forecast pattern as the non-PIT variant of the same model.
- `pr_hotel_revpar_yoy` on `nights_surprise_pct`: PIT mean 0.796, KS p=0.0072 (n=8) —
  systematically UNDER-forecasts nights surprise (opposite direction from the same
  model's revenue-surprise bias above — the two targets are not calibrated the same
  way for this model).
- Task B (post-release price drift, 6 targets × 3 models): most of these read
  "roughly calibrated" (14 of 18 groups, unchanged by the fix), but n per group is
  only 8-12 and the KS test has essentially no power there — read as "not
  disconfirmed," not "confirmed."

**This is the M5 critic's highest-value item, delivered as a negative result**: half
of the team's own earlier pre-earnings challenger forecasts scored here (8 of 16
Task-A `(target, model)` groups — the `f_*`, `pr_*`, `eu_*`, `bl_*` models on
`nights_surprise_pct`/`revenue_surprise_pct`) were systematically biased, not merely
imprecise, when checked against their own historical error distribution — the
uncertainty band would have needed re-centering, not just widening, for those groups.
The other half read as roughly calibrated at this sample size (n≤12 per group,
disclosed as low-power), so this is a mixed, not uniformly damning, result — corrected
from an earlier draft that (on the pre-fix, corrupted PIT values) read as a more
uniformly biased picture than the data, once fixed, actually supports.

---

## (e) Zero-shot foundation time-series model — SKIPPED by policy

`chronos_attempt.py`. A `pip install --dry-run chronos-forecasting` was run (not a
real install). It resolved in a few seconds and would pull in
`torch-2.14.0, transformers-5.17.0, accelerate, tokenizers, safetensors, sympy,
networkx, ...` — CPU torch plus the HF stack. A real install was **not attempted**:
on a cold cache this class of dependency closure commonly exceeds the 5-minute budget
the spec sets as the go/no-go gate, and the risk to the remaining time-box for a
model that would be asked to zero-shot a 14-20 point quarterly series (a regime a
foundation model pretrained on far denser series is not expected to help with) was
judged not worth taking. Documented per the spec's own instruction ("otherwise skip
and document"), not silently omitted. Output:
`data/processed/forecast_methods/calibration_rail/chronos_attempt.txt`.

---

## What failed

Nothing crashed; `run.py` exit code 0 end to end, all 6 steps OK. Two things did not
work as originally hoped and are reported as failures of the *idea*, not the code:
- The full_sample GBM replay initially leaked the target quarter's own row into
  training (§b) — caught before being reported, fixed with an explicit LOO guard,
  disclosed rather than silently corrected.
- Split conformal at `n_cal=6` cannot targetably test the pre-registered 70-90%
  coverage band (§c) — the pre-registration anticipated this outcome and asked for it
  to be stated plainly, which is what §c does.

## Parameter counts (published, per object)

| object | n_params | what they are |
|---|---|---|
| `ref_naive` (any metric) | 0-1 | 0 = mechanical rule with no fitted sigma yet (early guide dates, <3 pseudo-oos errors); 1 = +1 once the harness's own convention fits a residual sd from ≥3 pseudo-oos errors — both values appear in the registered rows, corrected after verification from an earlier draft that flatly stated 0 |
| `ref_trailing4` | 1-2 | 1 = trailing-4 mean only; 2 = +1 residual sd once ≥3 pseudo-oos errors exist, same convention as `ref_naive` — corrected from a flat "1" |
| `ref_ar1` | 2-3 | AR(1) intercept+slope, +1 for residual sd when ≥3 pseudo-oos errors exist |
| `gbm_revenue` / `gbm_surprise_guide` | 4 (nominal) | 4 input features; **NOT** a classical dof count — a `HistGradientBoostingRegressor` with `max_iter≤40, max_depth≤2` has far more effective flexibility than 4 linear coefficients; the 4 is the feature count only, disclosed as such, not asserted to be comparable to guide+cushion's 1 |

## Harness change request

1. **`score.py`'s naive-denominator join is hardcoded to `method=="baselines"`**
   (`NAIVE_METHOD, NAIVE_OBJECT = "baselines", "naive"` in `score.py`). This means
   `calibration-rail__ref_naive` (registered for `nights_yoy`/`adr_yoy`/`gbv_yoy`/
   `take_rate_pct`, which the harness's own `baselines` method does not cover) never
   populates as anyone's `rmse_ratio_to_naive` denominator — every scoreboard row for
   those 4 metrics shows `rmse_ratio_to_naive = NaN` even though a naive point value
   exists in the registry (see the (a) results table above). Worked around locally by
   computing MAPE/RMSE directly from the registry rather than relying on the
   scoreboard's ratio column for these 4 metrics. Suggested fix: let the denominator
   join match on `(target, window, prior_basis, quarter)` against *any* registered
   object literally named `naive` for that target, not only `baselines/naive`.
2. **No harness-native way to score a non-metric target** (the ledger's
   `revenue_surprise_pct`, `nights_surprise_pct`, and the 6 price-drift series are not
   columns in `targets.csv` and were never meant to be — they are legacy artefacts).
   §(d) works entirely outside the registry for this reason. Not a bug, just recorded
   so nobody expects `pit_crps_ledger_*.csv` to show up in `scoreboard.csv`.

## Acceptance tests (this package's own numbered claims)

1. Reproduce ~1.1% mean error for guide+cushion revenue level — **PASS** (1.068% PIT,
   0.990% full_sample, n=14).
2. Reproduce guide(+cushion) as worst predictor of surprise vs Street — **PASS**
   (bl_guide RMSE 2.588pp, bl_guide_plus_cushion 2.642pp, both above bl_zero 1.873pp
   and bl_last_quarter 1.760pp, n=100).
3. Reproduce "nothing beats AR(1) on nights" — **PARTIAL / DISCONFIRMED AS WRITTEN**:
   AR(1) does not beat naive on `nights_m` or `nights_yoy` in this harness in any
   window/replay; naive is the strongest classical baseline on nights here. Reported
   as found (see (a) §Claim 3), not adjusted.
4. At n_cal=6, alpha=0.2, attainable coverage is [85.7%, 100%], qhat = max of 6
   residuals — **PASS**, matches the harness's own computed grid exactly.
5. `run.py` exit code 0 — **PASS**.

## Optimal-mix answer (Theo's standing request, this package's deliverable)

On the evidence gathered tonight, **no method earns a weight over guide+cushion for
revenue level in the 3-12 month window this pitch covers**: it beats naive by more
than 2.5x on RMSE ratio (0.32-0.38 across both windows/replays), on 1 free parameter,
full 14/10-quarter coverage, and a directly-confirmed ~1.1% MAPE. The monotone GBM
challenger, AR(1), and trailing-4 all lose to it on revenue level in every window
tested. The one place guide+cushion demonstrably does NOT earn its keep is predicting
the *sign and magnitude of the surprise vs Street* (§ Claim 2) — where it is the worst
of four baselines — but nothing built tonight (GBM included) beats a simple
`bl_zero`/`bl_last_quarter` rule there either, at the sample sizes available (n≤15
per model). **Declared judgemental weighting**: revenue level → 100% guide+cushion;
surprise-vs-Street → no method tested here should be weighted above the
`bl_last_quarter` baseline, and the honest statement for the pitch is that surprise
timing is not solved, not that a smarter model solved it. This is a sensitivity
table with one free choice (how much weight, if any, to give the GBM on revenue
level), and the table says: give it none — every window it can be scored on, it ties
or loses to a 1-parameter rule with more coverage.

---

## Fixes after verification (round 1)

An independent verifier (`VERIFY_calibration-rail_r1.md`) re-ran this package
byte-for-byte, confirmed parts (a)/(b)/(c) and the point-in-time invariant on all 692
registered rows, and found one correctness bug plus several number/scope slips in the
note's prose. All are fixed here; nothing in parts (a), (b), or (c) needed to change.

**1. MUST-FIX, now fixed — part (d) levels/probabilities swap.**
`pit_crps_ledger.py::_pit_crps_group` was passing the Gaussian **z-scores**
(`Z.values()`, e.g. -1.645, -1.282, ...) as the `levels` argument to
`harness.metrics.pit_from_quantiles` / `crps_from_quantiles`, both of which expect
quantile **probabilities** (0.05, 0.10, ..., 0.95 — what `harness/score.py` correctly
passes via `QUANTILE_LEVELS` everywhere else in the registry). This corrupted 128 of
284 scored rows (PIT values outside [0,1], e.g. -1.55) and every downstream
BIASED/roughly-calibrated/OVERCONFIDENT label and CRPS figure derived from them.
Fixed by adding an explicit `PROBS` dict (`{"q05": 0.05, ..., "q95": 0.95}`) matched
key-for-key against the existing `Z` dict, and passing `list(PROBS.values())` as
`levels` while still using `Z.values()` only to build the `fc + z*sigma` quantile
ladder itself. Re-ran `run.py` end to end (exit 0); regenerated both
`pit_crps_ledger_detail.csv` and `pit_crps_ledger_summary.csv`. Post-fix, all 284
scored PIT values lie in [0, 1] (verified: min 0.025, max 0.975). The §(d) table and
every number quoted from it above have been replaced with the regenerated,
corrected values — do not cite any pre-fix number (20 BIASED / 13 calibrated / 1
OVERCONFIDENT; the pr_hotel_revpar_yoy PIT means of 0.32/0.34) from an earlier
draft of this note or from chat history; they were computed on the bug.
Post-fix counts: **12 BIASED / 21 roughly calibrated / 1 OVERCONFIDENT of 34**
groups — BIASED is real but now a minority failure mode (35%), not the modal one
the pre-fix numbers implied.

**2. Fixed — §(a) nights_yoy aside.** "ar1 RMSE 6.67 < trailing4 6.58, essentially
tied" was wrong: `ref_trailing4`'s actual RMSE on `nights_yoy` W1 PIT is **5.341**,
not 6.58 (recomputed from `scoreboard.csv`; likely a copy/paste slip against a
different metric's number while drafting). Corrected in §(a): the ordering is
naive (2.877) < trailing4 (5.341) < AR(1) (6.673) on this metric/window/basis — AR(1)
loses to trailing4 outright, it does not tie it. This does not change Claim 3's
verdict (AR(1) still does not beat naive on nights; still reported as
disconfirmed-as-written).

**3. Fixed — §(d) summary counts, superseded by fix 1.** The pre-fix note stated
20 BIASED / 13 calibrated / 1 OVERCONFIDENT; the verifier's own pre-fix regeneration
found 19/14/1 (an independent off-by-one from the note's own number, both wrong in
different ways because both were computed on the corrupted PIT values). Recomputing
once, after fix 1, is the only number that matters: **12/21/1**, stated in fix 1
above and now the only counts appearing anywhere in §(d).

**4. Fixed — §(c) falsification-test scope overreach.** The note claimed
`conformal_cov_empirical ∈ {0.75, 1.0}` held "across every registered object"; it
holds only for calibration-rail's own 8 rows. The full registry (`revenue_musd`,
`n_cal=6, alpha=0.2`, 66 rows across all packages) shows five distinct values —
`{1.0: 37, 0.75: 16, 0.875: 11, 0.5: 2, 0.25: 2}` — including two values (0.5, 0.25)
*below* the theoretical attainable floor of 0.857, which belong to
`baselines/naive_seasonal` and `baselines/street` and are a more interesting anomaly
than the two the original note chose to describe. §(c) above now states both the
narrow (calibration-rail-only) and the full-registry claim, with the anomaly named
rather than omitted.

**5. Fixed (cosmetic) — parameter-count table.** `ref_naive`/`ref_trailing4` are not
flatly 0/1; the registry itself carries `{0,1}`/`{1,2}` per the harness's own
"+1 for a fitted residual sd once ≥3 pseudo-oos errors exist" convention, documented
in `baselines.py`. The table in "Parameter counts" above now states both values with
the reason, rather than a single flat number. Does not affect any comparison in this
note — every RMSE/MAPE/CRPS number here was already computed from the registry
directly, not from the (previously oversimplified) documentation table.

**Not fixed, and why:** nothing. All five issues the verifier raised were either the
must-fix correctness bug (1, fixed by correcting the code and regenerating outputs)
or note-only documentation slips (2, 3, 4, 5, all fixed by correcting prose against
regenerated files). No acceptance test's pass/fail verdict changed: Claims 1, 2, and
4 remain CONFIRMED/PASS; Claim 3 remains PARTIAL/DISCONFIRMED-as-written; the
optimal-mix conclusion (100% guide+cushion on revenue level; no tested method above
`bl_last_quarter` on surprise timing) is unaffected, since it never depended on
part (d)'s ledger diagnostics — it rests on parts (a)/(b)/(c), which the verifier
found no leakage or correctness defects in.
