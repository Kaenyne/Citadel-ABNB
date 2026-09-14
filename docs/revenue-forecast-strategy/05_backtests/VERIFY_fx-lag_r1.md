# VERIFY fx-lag — round 1

Verifier run 2026-09-11. Independent re-run + line-by-line number check against the
implementer's note and the delivered CSVs. Nothing outside `analysis/src/forecast_methods/fx_lag/`,
`data/processed/forecast_methods/fx_lag/`, and the registry was touched.

## Verdict: **PARTIAL** — safe to score and quote, with one named implementation bug to fix
before this package's full-sample-prior rows are used for anything, and one lower-severity
caveat to carry forward.

---

## 1. Re-run

```bash
cd "<repo>"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fx_lag/run.py
```

Exit code **0**. Wall time **29s** (README says "~90s"; harmless discrepancy, not a defect —
maybe a cold-cache first run on the implementer's side).

Existing outputs were copied to `fx_lag_prev/` and the registry's three `fx-lag__*.csv` files
to `registry_fxlag_prev/` before the re-run. **Every one of the 20 data-output CSVs, `00_summary.json`,
and all three registry files are byte-identical between the two runs.** Fully deterministic,
no unseeded randomness leaking into outputs (the block bootstrap uses a fixed seed).

## 2. Registry format

All three registered files (`fx-lag__fx_rev_next_q_h2.csv` 40 rows, `fx-lag__fx_rev_next_q_h3.csv`
48 rows, `fx-lag__live_fx_schedule.csv` 2 rows) were produced by calling the harness's own
`register()`, which raised on nothing — confirmed by re-running and by reading
`analysis/src/forecast_methods/harness/registry.py` directly. Required columns present and
non-null, `window` values valid, `prior_basis` in {PIT, full_sample}, quantiles non-decreasing,
`vintage_date` is a real guide date or TODAY, `knowable_from = vintage_date - 1` (always
`<= vintage_date`), no `street_vendor`/`street_as_of` (correctly absent since no consensus is
consumed). The two coverage warnings printed (`fx_rev_next_q_h2 ... W1 ... covers 10 quarters,
expected 14`, PIT and full_sample) are genuine and correctly surfaced, not suppressed. **Registry
format: PASSED.**

I independently verified the harness's `GUIDE_DATES_W1`/`GUIDE_DATES_W2`/`GUIDE_DATE_LIVE`
against the package's own hard-coded `GUIDES` dict in `stages.py` — they match exactly (14/10
dates, identical to the day). No drift between the package's private copy of the calendar and
the frozen harness spine.

I also independently verified the harness change request. `harness/windows.py`'s
`LIVE_TARGETS = [q for _,q in GUIDE_EVENTS_ALL if q >= "2026Q3"]` looks like it should admit any
quarter from 2026Q3 onward (matching the README's "LIVE requires 2026Q3 or later"), but
`GUIDE_EVENTS_ALL` itself has no entry past 2026Q3, so `LIVE_TARGETS` is in fact `["2026Q3"]`
only and `window_of_target("2026Q4")` returns `[]`. The implementer's claimed error message and
workaround are real; this is a genuine gap between the harness's own README and its own code,
correctly identified rather than fabricated. The change request is legitimate.

## 3. Leakage audit

**Core PIT machinery is sound.** `pit_fx.py`'s `basket_yoy_asof()` and `regional_shares_asof()`
correctly restrict to FX data `<= asof` (asof = guide_date - 1 day) and L0 rows with
`knowable_from <= asof`; this is the only place the target quarter's own lag-0 basket is built,
and it is used correctly in `stages.pit_forecasts()`. `H4` (which uses the target quarter's own
disclosed ADR-FX point) is correctly excluded from `PIT_SPECS` and scored full-sample only.
Guide date = print date = letter date for the *preceding* quarter in this company's calendar
(confirmed directly from `harness/calendar.csv`), so training on `quarter < target_quarter`
correctly includes the quarter disclosed on the guide date itself — not a leak.

**Two issues found:**

**(a) CONFIRMED BUG — the "full-sample-prior" replay does not actually replay full-sample
weights.** In `run.py`, the code that is supposed to build the full-sample-prior comparison
(`09d_pit_forecasts_full_sample_prior.csv`) fits full-sample coefficients (`full_coef`) but
never applies them to recompute the point forecast — it only overwrites `sigma`:

```python
pf_full = pf.copy()
...
rows = []
for _, r in pf.iterrows():
    coef, sg = full_coef[r["spec"]]
    rows.append(sg)
pf_full["sigma"] = rows          # <- coef is computed and discarded; point is untouched
```

I confirmed this directly: `09b_pit_expanding_window_forecasts.csv` and
`09d_pit_forecasts_full_sample_prior.csv` have **identical `point` columns on every row**
(verified programmatically), and only `sigma` differs. This propagates into the registry:
in both `fx-lag__fx_rev_next_q_h2.csv` and `fx-lag__fx_rev_next_q_h3.csv`, every
`(quarter, vintage_date, window)` triple has **`point` (and `q50`) identical across
`prior_basis in {PIT, full_sample}`** — only `sd`/the quantile ladder differ. The harness's
`check_replays()` only checks that both `prior_basis` *labels* are present, so this passed
registration silently.

This matters because the standing point-in-time rule is explicit: "publish full-sample-prior
and PIT-prior replays side by side" — the entire point of that comparison is to show what a
forecaster who (illegitimately) knew the full-sample-fit weights would have done differently
from one who only ever saw data through T-1. As shipped, the two replays are visually present
but substantively the same forecast with a relabelled uncertainty band, which is not what the
rule asks for and would mislead anyone who scores `prior_basis` splits off the registry (a
naive reader would conclude "PIT and full-sample priors give identical point accuracy," which
is an artifact of the bug, not a finding). **This does not affect the headline PIT results in
the note** — section 6.2's W1/W2 RMSE/bias/interval-RMSE table is built from `09c_pit_window_scores.csv`,
which scores `pf` (the true PIT replay) alone, and I reproduced those numbers exactly from source
(see §5). The bug is confined to the full-sample side of the two registered PIT objects.
**Fix: recompute `point = X_target @ coef` using `full_coef[spec]`, not just `sigma`, before
writing `09d` and before `registry_out.build_rows(pf_full, ...)`.**

The acceptance-test claim "Point-in-time expanding window, refit at guide dates, both W1 and
W2, both prior replays: PASSED... 96 PIT forecast rows plus 96 full-sample-prior rows" is
therefore **overstated** — the row *count* is right, but the full-sample rows are not a distinct
replay in substance. This should be listed as failed-in-part, not passed, in the next round.

**(b) Minor, lower-severity — historical basket lag features are not vintage-stamped.**
The columns `b_lag1`, `b_lag2`, `eur_lag1/2`, `adrfx_lag1/2` used as *predictors* in the PIT
expanding-window fits (H1/H2/H2b/H3/H3b) come from `04_analysis_panel.csv`, which is built once
from `02_basket_quarterly.csv`. That file's regional weights come from `baskets.py`'s
`regional_revenue_weights()`, which uses the **full, current-vintage** L0 regional-revenue file
with no `knowable_from` filter — unlike `pit_fx.py`'s `regional_shares_asof()`, which is
correctly vintage-filtered and is used (only) for the target quarter's own lag-0 basket. In
principle, if a historical quarter's regional revenue split were later restated, a PIT fit at an
earlier guide date would be using the *revised* (not contemporaneously knowable) split for its
training-feature history. In practice this is likely immaterial: FRED bilateral spot rates never
revise, and I found no restatement evidence in `L0_exact_regional_revenue.csv` (`basis` values
are `filed`/`back_out`, not restated/derived) — but it is a real, undocumented asymmetry between
how the target quarter and the training history are constructed, and should be named as a
caveat rather than left implicit. Not severe enough to change the verdict on its own.

**basis == 'derived' rule:** not applicable to this package. It does not touch
`10_regional_panel_quarterly.csv` (the regional-nights-bands file the standing rule refers to)
at all; the regional revenue file it does use (`L0_exact_regional_revenue.csv`) has `basis` in
{`filed`, `back_out`}, never `derived`. Correctly a non-issue, not a silently-skipped rule.

**Consensus / Street leakage:** none found. No object consumes a consensus figure;
`street_vendor`/`street_as_of` are correctly absent throughout.

**Letter-rounded integers scored as points:** not found. Every fit on `fx_pts_revenue` /
`gross_fx_ex_hedge_pp` goes through `interval_loglik`/`fit_interval_linear` with a documented
half-width (0.5pp for the revenue integer, 0.05pp for the one-decimal ADR series, 0.55pp for the
Object-B wedge). Confirmed by reading `common.py` and every call site in `fits.py`/`stages.py`.

## 4. Number check (11 numbers recomputed from the CSVs, independent of the note's own text)

| # | claim | recomputed | match |
|---|---|---|---|
| 1 | Object A gross: scale 0.95, eff. lag 0.43, 95% CS eff. lag [0.03, 0.92] | 0.9515 / 0.4346 / [0.029, 0.923] | YES |
| 2 | Object A stated: scale 0.84, eff. lag 0.50, 95% CS [0.00, 1.19] | 0.8412 / 0.5044 / [0.000, 1.188] | YES |
| 3 | H0 (architect Phi x0.56): LR 16.8 p 0.0008 (gross), LR 10.2 p 0.017 (stated) | 16.762/0.0008, 10.214/0.0168 | YES |
| 4 | Object B gross wedge: c_lag0 -0.43, c_lag1 +0.59, uni lag1 t 1.82, uni lag0 r -0.05 | -0.4269, +0.588, t 1.818, r -0.0477 | YES |
| 5 | Object C ADR-FX raw~raw n12: slope 0.389 se 0.277 t 1.40 p 0.19; max |t| 1.40 over 20 rows | 0.3885/0.2769/1.403/0.1909; max 1.403 | YES |
| 6 | Repo LOO benchmark 1.2868 (rev_fx, `usd_broad_avg01`, post22); "never 2.3038" (that's `eurusd_avg12`/ex21) | 1.2868 exactly at that row; 2.3038 exactly at the named row | YES |
| 7 | PIT H2 (both windows): RMSE 0.99 bias +0.10 interval RMSE 0.58, n=10 both | 0.9936/0.0975/0.5782, n=10/10 | YES |
| 8 | Target series: n=14, population sd 2.337pp, 6 exact zeros | n=14, sd=2.33728, 6 zeros (1Q24-4Q24, 2Q25, 3Q25) | YES |
| 9 | Basket reconciliation: global basket diffs up to 0.08pp, regional <0.01pp (max 0.007) | max global diff 0.0761pp, max regional diff 0.0068pp | YES |
| 10 | Four-way reconciliation: -0.4 / -3.4 / +0.4 / +2.6 / +0.7pp; spread 6.0pp = $167M | exact match, spread 6.0, $167M | YES |
| 11 | Determined share, 4Q26 @ 5-Nov guide: point 0.65, band [0.40,0.91]; M6 lambda 0.75 -> 0.54; volume-determined 1.00 @ 5-Nov vs 0.333 @ pitch date | 0.6497, [0.398,0.909], 0.5353, 1.0 vs 0.3333 | YES |
| 12 | Hedge effect 3Q25-2Q26: -1.13, -0.93, -0.66, -0.61pp; identity holds to 1e-6 on all rows | exact match; identity True on every checked row | YES |
| 13 | Forward schedule spot-held: 3Q26 +1.2, 4Q26 +0.7, 1Q27 +0.5, 2Q27 +0.1, 3Q27 +0.2, 4Q27 +0.1 | exact match | YES |

**Zero mismatches** across 13 independently recomputed numbers spanning every object in the
package. This is unusually clean reproduction for a package of this scope; I did not cherry-pick
easy numbers — I deliberately targeted the H0 test statistics, the two acceptance tests the
implementer marked FAILED, the benchmark disambiguation (1.2868 vs 2.3038), and the
cross-cutting reconciliation table, since those are the places a fabricated or rounded-in-prose
number would most likely diverge from source.

One arithmetic point worth flagging for clarity, not correctness: the note's "FY27 FX is about
+0.2pp" is the **average** of the four quarterly forward-schedule figures (0.5+0.1+0.2+0.1 = 0.9,
÷4 = 0.225 ≈ +0.2), not their sum (+0.9pp). The arithmetic is defensible (a roughly
equal-revenue-weighted quarterly average is the right way to annualize a set of y/y FX
contributions) but is not shown anywhere in the note or the CSV, so a reader summing the table
by eye would get +0.9pp and be confused. Recommend adding one line showing the averaging.

## 5. Acceptance tests

Checked against the underlying CSVs in every case (not taken on the implementer's word):

- Basket reconciliation, 05_fx_fits ADR reproduction, target-series check, Object A CS/H0,
  benchmark disambiguation, PIT coverage/hazard labelling, registry format: **all confirmed
  PASSED as claimed**, with source numbers matching to the stated precision (see §4).
- `05_fx_fits.csv` rev_fx reproduction: **confirmed FAILED as claimed** — n=14 vs published
  n=13, slope -0.5023 vs -0.5348. Correctly not used anywhere downstream.
- Object C slope reproduction: **confirmed PARTIAL as claimed** — n and se close, slope does
  not reproduce on any of 8 conventions tried, conclusion (|t|<2 everywhere) robust across all
  20 rows.
- H2 W1 coverage: **confirmed FAILED as claimed** — 10/14, driven by adrfx_lag1/lag2 not
  jointly available with >=5 training rows until the 2024-02-13 guide date (I traced the exact
  mechanism: ADR-FX starts 2Q22, so both lags are simultaneously non-null only from 4Q22 on, and
  five such training quarters don't accumulate until the 1Q24 guide date — a slightly more
  precise account than the note's "driver doesn't exist before 2Q22," but the conclusion, 10/14
  and not quotable as a W1 winner, is exactly right).
- LIVE registration for 4Q26+: **confirmed BLOCKED as claimed**, root cause verified directly in
  `harness/windows.py` (see §2).
- **"Both prior replays" acceptance test: claimed PASSED, actually only PARTIALLY true** — see
  §3(a). The row-count and structural claim (96+96, W1/W2 scored) is accurate; the substantive
  claim that these are two distinct replays is not, because of the point-forecast bug.

No acceptance test was marked passed without CSV evidence to back it up. This implementer's
self-reporting is honest everywhere I checked except for over-stating the full-sample-prior
replay, which reads more like an unnoticed bug than a misrepresentation (the code visibly
computes `full_coef` and then doesn't use it — a copy-paste/completion slip, not a fabrication).

## 6. Honesty of interpretation vs results

High. The note repeatedly downgrades its own strongest-looking numbers: it states plainly that
LOO differences of 0.2-0.3pp at n=14 are within 1 standard error and refuses to name a winner
from the full-sample horse race; it states the PIT-window "best" result (H2) is only a
1.5-standard-error separation from H3 and instructs "say best, within noise, not wins"; it
declines to reproduce the architect's Object C slope rather than guessing at a convention that
would make it match; it states the ex-FX acceleration claim it was asked to confirm is **not**
supported and gives the flat/negative number instead; it labels the forward curve as
undeliverable from the data on hand rather than fabricating one; and it is explicit, repeatedly,
that no additive FX pp is applied to revenue anywhere in the package. All of that is exactly the
epistemic posture the standing orders ask for, and none of it is undercut by anything I found.
The one place the self-report is too generous is the "both prior replays: PASSED" line addressed
above — a real but narrow overstatement, not a pattern.

## Priority-ordered issues to fix before round 2 relies on this package

1. **(Must fix)** `run.py`'s full-sample-prior block recomputes `sigma` but not `point` for the
   `09d`/registry `full_sample` rows — both registered PIT objects (`fx-lag__fx_rev_next_q_h2`,
   `fx-lag__fx_rev_next_q_h3`) currently carry a full-sample replay whose point forecasts are a
   byte-for-byte copy of the PIT replay. Recompute the point from `full_coef` before writing.
   Until fixed, do not use the `full_sample` rows of these two registry files for any
   PIT-vs-full-sample comparison; the `PIT` rows and everything in the note's own §6.2 table are
   unaffected and safe to use now.
2. **(Should document)** Name, in the note, that the historical training-feature basket lags
   (b_lag1/2, eur_lag1/2, adrfx_lag1/2) are built from a non-vintage-stamped regional-weight
   construction, unlike the target quarter's own PIT-legal basket. Low practical risk (spot FX
   doesn't revise; no restatement evidence found in L0), but currently undocumented.
3. **(Cosmetic)** Show the quarterly-average arithmetic behind "FY27 FX is about +0.2pp" so a
   reader doesn't sum the forward-schedule table and get +0.9pp instead.

None of these three change any headline number already being quoted in the memo-facing
narrative (the lag confidence set, the H0 rejection, the PIT reconciliation, the determined
share, the forward schedule, the four-way reconciliation) — they are all confirmed correct
against source. The fix in (1) matters before anyone downstream scores or cites the
full-sample-prior side of this package's two registered objects specifically.
