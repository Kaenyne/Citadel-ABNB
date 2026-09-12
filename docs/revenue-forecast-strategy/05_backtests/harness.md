# harness — the shared point-in-time backtest harness

**Package:** `harness` · **Format version 1.0, FROZEN 2026-09-11** · run exit code 0 · 27/27 tests pass

The authoritative format specification is
`analysis/src/forecast_methods/harness/README.md`. This note is the record of what
ran, what it found, and where the harness deviates from the brief.

---

## 1. Commands

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"

# rebuild everything (spine, windows, baselines, conformal grid, scoreboard)
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/run.py

# re-score only, after other packages have registered
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py

# tests
/Users/theomachado/.venvs/citadel-abnb/bin/python -m pytest analysis/src/forecast_methods/harness/tests -q

# copy-paste template for a package
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/EXAMPLE.py
```

`run.py` took ~6 s. It is idempotent and touches only `harness/` outputs and its own
six `baselines__*.csv` registry files.

## 2. What shipped

| file | what |
|---|---|
| `analysis/src/forecast_methods/harness/README.md` | **the frozen format spec — authoritative** |
| `.../harness/paths.py` | every path resolved from `__file__`; runs from anywhere |
| `.../harness/quarters.py` | canonicalises `3Q26` / `2026Q3` / period-end to `YYYYQn` |
| `.../harness/windows.py` | W1/W2/LIVE hard-coded **and** re-derived from the ledger by `assert_matches_ledger()` |
| `.../harness/spine.py` | builds `calendar.csv` and `targets.csv`; every source column documented in the module docstring |
| `.../harness/registry.py` | `register()`, `load_registry()`, `validate_registry_frame()` |
| `.../harness/baselines.py` | the five baselines as functions |
| `.../harness/metrics.py` | CRPS, PIT, rolling split conformal, attainable-coverage grid |
| `.../harness/score.py` | the full metric block → `scoreboard.csv` + `scoreboard.md` |
| `.../harness/EXAMPLE.py` | 60-line copy-paste template for a package's `run.py` |
| `.../harness/tests/test_harness.py` | 27 tests |
| `data/processed/forecast_methods/harness/calendar.csv` | 25 events, 2020Q3–2026Q3 |
| `data/processed/forecast_methods/harness/targets.csv` | 25 quarters × 27 columns |
| `data/processed/forecast_methods/harness/windows.csv` | the guide-date lists as data |
| `data/processed/forecast_methods/harness/conformal_attainable_grid.csv` | attainable coverage by `n_cal` × `alpha` |
| `data/processed/forecast_methods/harness/scoreboard.csv` / `.md` | 72 scored rows |
| `data/processed/forecast_methods/registry/baselines__{naive,naive_seasonal,ar1,trailing4,guide_cushion,street}.csv` | 900 registry rows |

## 3. The frozen registry format, in one paragraph

One CSV per `(method, object)` at
`data/processed/forecast_methods/registry/<method>__<object>.csv`, holding **all**
windows and **both** replays. Required: `method, object, target, quarter,
vintage_date, horizon_q, point, q50, window, prior_basis, n_params, n_train`.
Optional: `q05, q10, q25, q75, q90, q95, sd, base_naive, base_ar1, base_trailing4,
base_guide_cushion, base_street, street_vendor, street_as_of, knowable_from, spec_id,
notes`. `target` is the **metric** (a column of `targets.csv`); `quarter` is the
**period**, canonical `YYYYQn`. `window ∈ {W1, W2, LIVE}`, `prior_basis ∈ {PIT,
full_sample}`. Unknown columns are a hard error — the format is frozen; put anything
else in `notes` or open a change request.

**The decision document asks for `q10/q50/q90`; the package brief asks for
`q05/q25/q50/q75/q95`. The frozen format accepts all seven and only requires `q50`.**
That is the one place I added rather than chose, and it costs nothing.

### What the validator refuses

1. `vintage_date` that is not one of the 20 ledger guide dates or `TODAY = 2026-09-11`.
2. **Look-ahead**: `vintage_date >= print_date` of the target quarter.
3. `street_as_of > vintage_date` or `knowable_from > vintage_date` →
   `StreetVintageError`. This is how "do not use the 4-Sep Zacks value as the 6-Aug
   pre-guide Street" is enforced mechanically rather than by memo. There is a test
   that proves it fires.
4. Non-monotone quantiles; two objects in one file; a `window` inconsistent with its
   `quarter` (a 2023Q2 row may not be labelled W2; a 2026Q3 row may only be LIVE).
5. An object carrying only one `prior_basis` is a **hard error** unless the caller
   passes `allow_single_replay=True`; it also warns. Missing W1/W2 coverage (≠14/≠10
   quarters) warns loudly.

## 4. Windows — verified against the ledger

22 revenue-guide rows exist in `02_guidance_ledger.csv`; 20 are `metric ==
revenue_usd_m, guide_type == range` with a dated call. Of those, 19 have a realised
actual and one — the 2026-08-06 guide for 3Q26 — does not.

* **W1** = targets 2023Q1…2026Q2, **14** guide dates (2023-02-14 … 2026-05-07). Asserted.
* **W2** = targets 2024Q1…2026Q2, **10** guide dates (2024-02-13 … 2026-05-07). Asserted, and a strict subset of W1.
* **LIVE** = 2026-08-06 → 3Q26. Excluded from every metric by the scorer, not by convention.

## 5. Deviation from the brief you must all know about — the same-day letter

The binding rule reads *"the information set at guide date d is letters and 10-Qs
filed strictly before d"*. Taken literally that excludes **the letter that carries the
guide**: 2Q26 results and the 3Q26 revenue range are one 8-K Ex.99.1 dated
2026-08-06. A forecaster standing at that guide date obviously knows 2Q26 revenue.

`history_as_of()` therefore defaults to `print_date <= vintage_date` and documents
this at the call site. Pass `include_same_day=False` for the literal reading.

**This is not a convenience — it is what reproduces the chief of staff's cushion.**
The trailing-8 `actual / guide_mid` window as of 2026-08-06 gives

| statistic | harness | CoS |
|---|---|---|
| mean | **+1.8567 %** | +1.856 % |
| median | **+1.7905 %** | +1.790 % |
| sd | **1.0048 pp** | 1.006 pp |
| n | 8 | 8 |

`run.py` asserts this and **exits non-zero if it breaks**. Under a strict `<` rule the
window slides back one quarter and none of the three numbers reproduce.

**Correction to circulate:** +1.86 % is the **trailing-8** cushion at the live guide
date, not a sample statistic. Over all 19 realised guides the cushion is **mean
+2.541 %, median +2.517 %, sd 1.552 pp**; over the 14 W1 targets, **mean +2.190 %,
median +2.183 %, sd 1.152 pp**. Anyone quoting "+1.86 % cushion" as the historical
average is quoting an eight-quarter window and should say so. The Q4 guide-midpoint
object is built on the trailing-8, so the object is right and the prose is loose.

The FX rule ("FRED FX through d−1") is a *daily* series and is untouched by this
convention. Packages consuming FX must still cut at d−1 themselves; the harness does
not hold FX.

## 6. Baselines — definitions and free-parameter counts

| object | rule | free params |
|---|---|---|
| `naive` | `y[q−4] × (1 + g_last)`, `g_last` = most recent **observed** y/y growth. **This is the RMSE-ratio denominator.** | 1 (residual sd) |
| `naive_seasonal` | `y[q−4]` (zero y/y growth). Transparency only. | 1 |
| `ar1` | OLS AR(1) on y/y growth, refit expanding, iterated to the horizon, mapped back through `y[q−4]` | 3 |
| `trailing4` | mean of the last 4 observed y/y growths applied to `y[q−4]` | 2 |
| `guide_cushion` | `guide_mid × median(trailing-8 actual/guide_mid)`; quantiles are the **empirical** cushion quantiles, not Gaussian | 1 |
| `street` | the vintage-stamped pre-guide Street, `next_q_cons_revenue_musd` from `16_consensus_at_print_merged.csv` | 0 |

Interval widths for `naive`/`naive_seasonal`/`ar1`/`trailing4` come from the sd of up
to 12 pseudo-out-of-sample errors of the same rule inside the information set — which
is why those objects carry one parameter more than the point rule alone implies. I
counted the residual sd as a free parameter everywhere. If a package disagrees, say so
in its own note; do not silently drop it.

## 7. Results — revenue_musd, both windows, both replays (n = 14 / 10)

RMSE in $m. `ratio` is RMSE ÷ RMSE(naive) on the same series, window and replay.

| object | window | replay | n | MAE | RMSE | bias | ratio | CRPS | 80% cov | PIT KS p | survives both |
|---|---|---|---|---|---|---|---|---|---|---|---|
| guide_cushion | W1 | PIT | 14 | 31.0 | 35.5 | +10.6 | **0.377** | 19.7 | 0.64 | 0.39 | **yes** |
| guide_cushion | W1 | full | 14 | 28.5 | 35.3 | +13.5 | **0.375** | 17.8 | 0.79 | 0.81 | **yes** |
| guide_cushion | W2 | PIT | 10 | 30.9 | 34.6 | +8.7 | **0.319** | 20.4 | 0.60 | 0.37 | **yes** |
| guide_cushion | W2 | full | 10 | 31.2 | 38.9 | +17.8 | **0.359** | 19.6 | 0.70 | 0.49 | **yes** |
| ar1 | W1 | PIT | 14 | 90.1 | 103.5 | −48.8 | 1.101 | 68.8 | 0.29 | **0.001** | no |
| ar1 | W1 | full | 14 | 64.1 | 84.6 | −5.1 | 0.900 | 47.0 | 0.71 | 0.82 | yes |
| ar1 | W2 | PIT | 10 | 93.4 | 109.4 | −35.6 | 1.009 | 71.1 | 0.40 | 0.15 | no |
| ar1 | W2 | full | 10 | 82.8 | 99.3 | −7.6 | 0.916 | 57.0 | 0.60 | 0.76 | yes |
| naive | W1 | PIT | 14 | 75.1 | 94.0 | +12.8 | 1.000 | 57.9 | 0.93 | 0.61 | — |
| naive | W2 | PIT | 10 | 91.5 | 108.4 | +4.2 | 1.000 | 64.4 | 0.90 | 0.94 | — |
| street | W1 | PIT | 14 | 87.7 | 100.9 | −68.3 | 1.073 | 58.4 | 0.79 | 0.013 | no |
| street | W2 | PIT | 10 | 82.1 | 94.5 | −54.9 | 0.871 | 54.7 | 0.70 | 0.14 | no |
| trailing4 | W1 | PIT | 14 | 134.8 | 169.8 | +75.3 | 1.806 | 108.4 | 0.86 | 0.39 | no |
| trailing4 | W2 | PIT | 10 | 99.0 | 119.4 | +15.8 | 1.101 | 77.2 | 1.00 | 0.49 | no |
| naive_seasonal | W1 | PIT | 14 | 340.0 | 352.9 | −340.0 | 3.754 | 227.7 | 0.71 | 0.000 | no |
| naive_seasonal | W2 | PIT | 10 | 324.2 | 337.8 | −324.2 | 3.115 | 230.9 | 0.60 | 0.000 | no |

Full block including gbv_musd, nights_m and revenue_yoy is in `scoreboard.csv` /
`scoreboard.md`.

### The four things a reader should take from that table

**(a) The bar is the guide, not the naive.** `guide_cushion` scores RMSE **34.6–38.9**
against the naive's **94–108**: a ratio of 0.32–0.38 that survives both windows on
both replays. Any object in this programme that claims an edge on *printed revenue*
one quarter out must be compared with ≈ **$35 m RMSE**, not with $94 m. Management's
own range plus a median trailing-8 cushion is an extremely strong forecaster, and it
costs one free parameter. It does carry a bias of **+9 to +18 $m** — the median-cushion
rule over-shoots slightly — so there is a little left on the table, but not much.

**(b) AR(1) is the case for running two replays, and it is not subtle.** PIT AR(1)
**loses** to naive (ratio 1.101 on W1, 1.009 on W2). Full-sample AR(1) **beats** it
(0.900, 0.916). Same rule, same data, same windows — the only difference is whether
the AR coefficients and the residual sd were estimated on the information set or on
the whole sample. Its PIT histogram also fails a uniformity test point-in-time
(KS p = **0.001**) and passes on the full sample (p = 0.82). **Any package that
publishes only a full-sample replay will publish a win that does not exist
point-in-time.** This is the empirical justification of the two-replay rule; quote it
if anyone argues the rule is bureaucratic.

**(c) The pre-guide Street does not survive both windows.** Ratio 1.073 on W1 (worse
than naive), 0.871 on W2 (better). Under the stated rule it therefore may not be
quoted as a beaten benchmark either way. Its bias is **−68 $m on W1 and −55 $m on W2**:
the pre-guide Street is systematically **below** the eventual print by roughly 2 %,
consistently, which is the same phenomenon as the cushion seen from the sell side. Its
PIT is non-uniform on W1 (p = 0.013) for exactly that reason.

**(d) Beating naive is not free.** `naive_seasonal` (zero y/y growth) scores 3.1–3.8×
naive. The trend term does most of the work, so "we beat a naive benchmark" means
little unless the benchmark is the one defined here.

## 8. Conformal coverage — the honest version

Rolling split conformal, `n_cal = 6`, `alpha = 0.2`. At that sample size
`k = ceil((n+1)(1−α)) = ceil(7 × 0.8) = 6`, so `qhat` is the **maximum of the six
calibration residuals** and attainable coverage lies in `[k/(n+1), (k+1)/(n+1)] =
[6/7, 7/7] = [85.7 %, 100 %]`.

**There is no 80 % guarantee available at n_cal = 6 and the harness will not print
one.** The grid (`conformal_attainable_grid.csv`) shows the only `n_cal` in range at
which 80 % is *exactly* attainable is `n_cal = 4` (k = 4, floor 4/5 = 0.800); n_cal =
5, 6, 7, 8 give floors of 0.833, 0.857, 0.875, 0.889, all conservative.

Every scoreboard row carries, in the same row, the column `coverage_caveat`:

> EXCHANGEABILITY VIOLATED: residuals are a time-ordered non-exchangeable sequence
> (expanding-window refits, a trending target, and a regime change at the 2022
> reopening); conformal coverage here is descriptive, not a guarantee.

Observed `conformal_cov_empirical` runs 0.75–1.00 on the six evaluable points — which
is what an over-wide max-residual interval on six points should look like, and carries
essentially no information. Report it; do not lean on it.

## 9. CRPS convention

CRPS uses the quantile-score identity `CRPS = 2∫₀¹ QS(τ)dτ`, trapezoid over the
supplied τ ladder with the pinball loss held **constant** outside the outermost
supplied τ. A naive piecewise-linear-CDF integration returns `inf` whenever the actual
falls outside the ladder, which happens repeatedly here; this form is bounded and
mildly conservative in the tails. An object supplying only `q50` gets `crps = MAE`,
which is the exact CRPS of a point mass. Tested both ways.

## 10. What failed, and what is approximate

* **AR(1) at the 2023Q1 origin initially had no estimable fit** (only 8 quarters of
  visible history) and the object covered 13 of 14 W1 dates. Fixed by extending
  `calendar.csv` back to 2020Q3 with `print_date = quarter_end + 46 days` for the
  quarters the guidance ledger does not date, flagged as
  `print_date_basis = approx_qend_plus_46d` (**1 row only**: 2020Q3; 4Q20 is in the
  ledger). The approximation only ever decides whether a 2020 quarter is visible in
  2023, which is not a close call, but it is an approximation and it is labelled.
* **`targets.csv` recomputes y/y growth from levels** rather than taking the panel's
  `revenue_yoy_reported_pct`, so baselines and targets are arithmetically consistent.
  The panel's reported columns are carried alongside as `revenue_yoy_panel` /
  `gbv_yoy_panel` for reconciliation. They differ by rounding only.
* **`nights_m` and `gbv_musd` baselines are weaker than revenue's** (AR(1) PIT ratios
  1.7–2.2). Nothing beats naive on those series among the baselines. Registered anyway
  so volume-target packages have a denominator.
* **No L0 vintage register existed at build time.** `targets.csv` falls back to
  `04_current_consensus.csv` for forward quarters and stamps the vendor and `as_of`
  from it. `spine._forward_consensus()` prefers
  `data/processed/forecast_methods/L0/L0_vintage_register.csv` the moment it appears
  with columns `period, metric, value, vendor, as_of`; re-run `run.py` after L0 lands
  and the Street baseline picks it up with no code change. **I did not create, edit or
  read-modify anything in `L0/`.**
* **Not built** (deliberately, per the addendum): no model of any kind; no ensemble;
  no FX handling; no plotting.

## 11. Free-parameter counts published

`naive` 1 · `naive_seasonal` 1 · `trailing4` 2 · `ar1` 3 · `guide_cushion` 1 ·
`street` 0. Against n = 14 (W1) / 10 (W2) observations, `param_obs_ratio` runs
0.07–0.30. Every scoreboard row carries `n_params`, `n_obs` and `param_obs_ratio`.

## 12. Harness change requests

None are blocking. Four format decisions were forced on me and the team may want to
ratify or reverse them; all four are one-line changes:

1. **Seven quantile columns, not three or five.** The decision document and the
   package brief specified different ladders. I accepted both supersets; only `q50` is
   required. *Recommend: keep.*
2. **Same-day letter is inside the information set** (§5). This is a genuine deviation
   from "filed strictly before d" and it is load-bearing — it is what makes the
   trailing-8 cushion reproduce. *Recommend: ratify explicitly, because every package
   inherits it through `history_as_of()`.*
3. **`window` is a row value, not a file split.** A 2024Q1+ target appears twice in an
   object file, once as W1 and once as W2. This is duplication, but it makes the
   scorer's grouping trivial and makes "survives both windows" a join rather than a
   convention. *Recommend: keep.*
4. **`calendar.csv` spans 2020Q3–2026Q3**, not the specified 2021Q1–2026Q2: one
   approximated row earlier (to buy AR(1) its 14th origin) and the 2026-11-05 forecast
   row later, as the brief asked. *Recommend: keep; the extra row is flagged.*

Open a change request by writing it under a `## Harness change request` heading in
your own `05_backtests/<package>.md`. Do not edit `harness/`.

## 13. For the other packages — the shortest possible instruction

Copy `EXAMPLE.py`. Loop over `GUIDE_EVENTS_ALL`; for each `(guide_date,
target_quarter)` loop over `window_of_target(target_quarter)` and over
`("PIT", "full_sample")`; build your forecast using only `history_as_of(guide_date,
metric)`; call `register(df)`. If `register` raises, the message says exactly which
rule you broke. Then run `score.py` and read `scoreboard.md`. Your object is quotable
only if `survives_both_windows` is `True` **and** `replays_present == 2`.
