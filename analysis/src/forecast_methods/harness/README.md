# harness — shared point-in-time backtest harness

**FORMAT VERSION 1.0 — FROZEN 2026-09-11. This file is authoritative.**
If a column name here disagrees with anything you were told elsewhere, this file wins.
Do not invent a second format. If the harness lacks something you need, write a
"harness change request" in your own note and work around it locally.

## Run command

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/run.py
```

Rebuilds `calendar.csv`, `targets.csv`, the five baseline registry files, and the
scoreboard. Exit code 0 on success. Safe to re-run; it overwrites its own outputs
and never touches another package's registry files.

Score only (after other packages have registered):

```bash
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

## What the harness gives you

```python
import sys, pathlib
sys.path.insert(0, "<repo>/analysis/src/forecast_methods")
from harness import (
    load_calendar, load_targets,            # point-in-time spine
    GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE, WINDOW_MEMBERSHIP,
    register, load_registry, validate_registry_frame, REGISTRY_COLUMNS,
    history_as_of,                          # PIT slice of the target panel
    baseline_naive, baseline_ar1, baseline_trailing4,
    baseline_guide_cushion, baseline_street,
    score_registry,
)
```

## 1. Registry file format (FROZEN)

One CSV per `(method, object)` pair, at

```
data/processed/forecast_methods/registry/<method>__<object>.csv
```

`method` = your package name (`fx-lag`, `kernel-lambda`, `baselines`, ...).
`object` = the forecast object name within your package (`naive`, `q4_print`, ...).
Both are slugged to `[a-z0-9_-]` on write; `__` (double underscore) is the separator
and may not appear inside either part.

**One file holds every row of that object**: all windows (W1, W2, LIVE), both prior
replays, every target metric, every vintage date. Do not split by window.

### Required columns (must be present and non-null)

| column | type | meaning |
|---|---|---|
| `method` | str | package name; must equal the filename part before `__` |
| `object` | str | object name; must equal the filename part after `__` |
| `target` | str | target **metric** name, must exist as a column in `targets.csv` (e.g. `revenue_musd`, `revenue_yoy`, `gbv_musd`, `nights_m`, `adr_usd`, `take_rate_pct`) |
| `quarter` | str | target **period**, canonical `YYYYQn` (e.g. `2026Q4`) |
| `vintage_date` | ISO date | date the forecast was made. MUST be a guide date from `calendar.csv` or today (`2026-09-11`) |
| `horizon_q` | int | quarters from the quarter containing `vintage_date` to `quarter` (>=0) |
| `point` | float | the point forecast, in the units of `target` |
| `q50` | float | median of the predictive distribution |
| `window` | str | `W1`, `W2` or `LIVE` (upper-cased on write) |
| `prior_basis` | str | `PIT` or `full_sample` |
| `n_params` | int | free-parameter count of the object (publish it; it is scored) |
| `n_train` | int | number of observations in the information set at `vintage_date` |

### Optional columns (write them if you have them; scorer degrades gracefully)

`q05`, `q10`, `q25`, `q75`, `q90`, `q95`, `sd`,
`base_naive`, `base_ar1`, `base_trailing4`, `base_guide_cushion`, `base_street`,
`street_vendor`, `street_as_of`, `knowable_from`, `spec_id`, `notes`.

Notes on the optional block:

* **Quantiles.** The decision document asks for `q10/q50/q90`; the package spec asks
  for `q05/q25/q50/q75/q95`. The frozen format accepts **all seven**; only `q50` is
  required. CRPS is computed from whatever ladder you supply (see §5). Write at least
  `q10` and `q90` if you want an 80% coverage number, otherwise coverage is reported
  from `q05/q95` and labelled nominal 90%.
* **`base_*`** are the five baseline values at the same `(target, quarter,
  vintage_date)`, carried alongside your forecast for convenience. You do **not** have
  to fill them; the scorer joins the `baselines` method itself. Fill them only if you
  computed a baseline differently and want the difference visible.
* **`street_vendor` / `street_as_of`** are mandatory *if* your object consumes a
  consensus number. `street_as_of` must be <= `vintage_date` or the validator errors.
* **`knowable_from`** is the date the last input to the forecast became public. It must
  be <= `vintage_date`.
* **`spec_id`** is a free string identifying the exact specification (so a grid of
  variants can live in one object file). **`notes`** must contain no commas-in-anger;
  it is quoted on write but keep it short.

### Writing

```python
register(df)                       # validates, then writes; raises on any error
register(df, allow_single_replay=True)   # suppress the two-replay hard error (still warns)
```

`register` refuses to write if validation fails. It prints warnings (not errors) for:
* an object present with only one `prior_basis` (the two-replay rule);
* a W1/W2 object that does not cover all 14 / 10 guide dates for its target metric.

### Reading

```python
reg = load_registry()                 # everything
reg = load_registry(method="fx-lag")  # one package
```

## 2. Point-in-time rules the validator enforces

1. `vintage_date` must be in `GUIDE_DATES_ALL` (the 22 revenue-guide call dates from
   `02_guidance_ledger.csv`) or equal to `TODAY = 2026-09-11`. Anything else is an error.
2. **PIT rule.** `vintage_date` must be **strictly before** the `print_date` of
   `quarter` (from `calendar.csv`). A forecast made on or after the print of the quarter
   it forecasts is rejected. Quarters with no print date yet (3Q26 onward) always pass.
3. `street_as_of <= vintage_date` and `knowable_from <= vintage_date` when present.
4. Quantiles must be non-decreasing across the ladder you supply.
5. `window` must be consistent with `quarter`: `W1` requires `quarter` in
   2023Q1..2026Q2; `W2` requires 2024Q1..2026Q2; `LIVE` requires 2026Q3 or later.
   The 2026-08-06 guide is **LIVE** and enters no metric and no gate.

## 3. Windows (hard-coded from the guidance ledger revenue rows; asserted at import)

* `GUIDE_DATES_W1` — 14 dates, targets 2023Q1..2026Q2.
* `GUIDE_DATES_W2` — 10 dates, targets 2024Q1..2026Q2 (a subset of W1).
* `GUIDE_DATE_LIVE` — `2026-08-06`, target 2026Q3. Scored in nothing.

A result must survive **both** W1 and W2 to be quoted. The scoreboard carries
`survives_both_windows`.

## 4. Baselines (use these; do not re-implement)

All five are functions of `(targets, calendar, vintage_date, metric)` and use only
information knowable at `vintage_date`.

| function | definition | `n_params` |
|---|---|---|
| `baseline_naive` | `y[q-4] * (1 + g_last)` where `g_last` is the most recent **observed** y/y growth of the metric. This is the canonical RMSE-ratio denominator. | 0 |
| `baseline_ar1` | OLS AR(1) on y/y growth, refit expanding at each vintage; growth mapped back to level through `y[q-4]`. Quantiles from the residual sd, Gaussian. | 3 |
| `baseline_trailing4` | mean of the last 4 observed y/y growths, applied to `y[q-4]`. | 1 |
| `baseline_guide_cushion` | `guide_mid * (1 + c)`, `c` = **median** of the trailing-8 `actual_over_guide_mid` ratios whose target quarter printed strictly before the vintage date. Revenue only. | 1 |
| `baseline_street` | the vintage-stamped **pre-guide** Street. Sourced from `next_q_cons_revenue_musd` in `16_consensus_at_print_merged.csv`, whose `as_of` is the morning of the print date — ABNB reports after the close, so that number precedes the letter and the guide. **REFUSES** (raises `StreetVintageError`) any consensus row whose `as_of` postdates the vintage date, which is how the kill-list rule "no September vendor as the 6-Aug pre-guide Street" is enforced mechanically. | 0 |

`baseline_naive` also has a sibling `baseline_naive_seasonal` (`y[q-4]`, zero y/y
growth) registered as object `naive_seasonal` for transparency; it is **not** the ratio
denominator.

## 5. Scorer

`score.py` reads every registry file and emits, per
`(method, object, target, window, prior_basis)`:

`n`, `mae`, `rmse`, `bias`, `rmse_ratio_to_naive`, `mape_pct`, `crps`, `pinball_mean`,
`pit_mean`, `pit_ks_p`, the PIT histogram in 5 bins (`pit_bin_1..5`),
`cov_nominal`, `cov_empirical`, `cov_interval`,
`conformal_n_cal`, `conformal_alpha`, `conformal_cov_empirical`,
`conformal_attainable_lo`, `conformal_attainable_hi`, `coverage_caveat`,
`n_params`, `n_obs`, `param_obs_ratio`, `survives_both_windows`, `replays_present`.

* **CRPS** uses the quantile-score identity `CRPS = 2 * int_0^1 pinball(tau) dtau`,
  trapezoid over the supplied tau ladder, with the pinball loss held constant outside
  the outermost supplied tau. With a `q05..q95` ladder that approximation is mildly
  conservative in the tails; it is bounded and it never returns `inf`, which a naive
  piecewise-linear-CDF integration does when the actual falls outside the ladder.
  Objects with only `q50` get `crps = MAE` (which is the correct degenerate value).
* **PIT** is the piecewise-linear CDF implied by the quantile ladder, evaluated at the
  actual, clipped to [0,1]; rows outside the ladder are flagged in `pit_edge_frac`.
* **Coverage** uses `[q10,q90]` (nominal 80%) when present, else `[q05,q95]`
  (nominal 90%). `cov_interval` names which.
* **Split conformal** is run as a rolling calibration: at each scored quarter `i >= n_cal`,
  calibrate `qhat` on the previous `n_cal` absolute residuals and check the interval
  `point +/- qhat`. Default `n_cal = 6`, `alpha = 0.2`.
* `coverage_caveat` carries, in the same row, the string:
  `EXCHANGEABILITY VIOLATED: residuals are a time-ordered non-exchangeable sequence; conformal coverage here is descriptive, not a guarantee.`
* The **attainable-coverage grid** is written to
  `data/processed/forecast_methods/harness/conformal_attainable_grid.csv`. At `n_cal=6`,
  `alpha=0.2`, `k = ceil((n+1)(1-alpha)) = 6`, so `qhat` is the **maximum** of six
  residuals and the attainable coverage band is `[k/(n+1), (k+1)/(n+1)] = [6/7, 7/7] =
  [85.7%, 100%]`. There is no 80% guarantee available at this sample size, and the
  harness will not print one.

Outputs: `scoreboard.csv` and `scoreboard.md` in
`data/processed/forecast_methods/harness/`.

## 6. Files the harness produces

| file | contents |
|---|---|
| `data/processed/forecast_methods/harness/calendar.csv` | one row per earnings event 2021Q1..2026Q2 plus the 2026-11-05 forecast row |
| `data/processed/forecast_methods/harness/targets.csv` | quarterly target panel with guides, cushions and vintage-stamped consensus |
| `data/processed/forecast_methods/harness/windows.csv` | the W1/W2/LIVE guide-date lists as data |
| `data/processed/forecast_methods/harness/conformal_attainable_grid.csv` | attainable conformal coverage by `n_cal` and `alpha` |
| `data/processed/forecast_methods/harness/scoreboard.csv` / `.md` | the metric block |
| `data/processed/forecast_methods/registry/baselines__*.csv` | the five baselines (six objects) |

## 7. Tests

```bash
/Users/theomachado/.venvs/citadel-abnb/bin/python -m pytest analysis/src/forecast_methods/harness/tests -q
```

Covers the validator, the scorer on a toy example with a known answer, and the PIT rule
(a forecast whose `vintage_date` postdates the target's print date must be rejected).

## 8. Harness change requests

Open one by writing it in your own note at
`docs/revenue-forecast-strategy/05_backtests/<package>.md` under a heading
`## Harness change request`. Do not edit this folder.
