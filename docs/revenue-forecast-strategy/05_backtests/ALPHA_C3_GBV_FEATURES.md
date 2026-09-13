# C3 — GBV features and kernel residual

Agent sub-C3 · 2026-09-13 UTC · branch codex/lane1-full

**underpowered** — no feature qualifies for promotion. The required historical RNPL correction has no admissible vintage in the supplied inputs, leaving zero matched comparator cells in W1 and W2. This is an untestable pass line on the supplied vintages, not evidence that all alternative data are useless. The available GBV features also lose to a separately labelled raw-ledger diagnostic on three common quarters.

## Pre-registration, written before results

Pass line, unchanged: **A feature earns a place only if it beats the ledger baseline (RNPL-corrected unearned fees) on GBV on BOTH windows with a stable coefficient sign. Report everything that did not, with ratios.**

The pre-registered feature list is:

1. RNPL-corrected unearned-fees growth, the required ledger baseline.
2. Funds-payable / funds-held growth.
3. GBV momentum: latest available booking-dated GBV y/y.
4. NTTO arrivals, only if observations have a historical publication vintage.
5. Reviews stays index, if present, only if the index weights and underlying dump vintage predate the forecast origin.
6. Hotel RevPAR: mean of Marriott and Hilton latest common-quarter observations published strictly before the origin.
7. Calendar pickup, only if a published historical vintage exists in the WP-C1 / q3nowcast tree.

Google Trends and sentiment are excluded. No internet requests or raw-store access are needed for this screen. Missing vintages lead to abstention, not assumed historical availability.

Specification: expanding-window intercept-plus-one-feature OLS, fixed minimum four training observations, no tuned hyperparameters, no feature combinations, no selection by full-sample correlation. Refit on each frozen guide date. Each training observation uses its own historical feature snapshot and a target published strictly before the current origin. Features dated on the guide date are refused. GBV y/y is calculated from dollar amounts, not treated as an exact letter-rounded integer; reported integer growth is additionally scored on its ±0.5 interval when supplied. Both W1 (2023Q1–2026Q2) and W2 (2024Q1–2026Q2) are reported, with common-cell counts and excluded quarters.

The required RNPL-adjusted denominator remains unavailable unless a correction has a dated admissible source. Raw unearned-fees OLS is a **separate diagnostic comparator**, never substituted for the pass line. A stable sign means the slope is nonzero and has the same sign at every scored origin in both windows. A feature can only be promoted if the required denominator exists and its RMSE ratio is below one in both windows; restricted identical cells are explicitly labelled vacuous.

Target (b) is exactly the supplied `kernel_phi_v2/D0_carried_and_residual_panel.csv` R_musd. Its carried component uses retrospectively estimated coefficients. Any numerical replay against this fixed target is labelled `full_sample_target_diagnostic`, not PIT evidence. No such replay can support a promotion. Creating a different residual would change the requested target and is not done.

Ledger publication dates come from dated filings in the frozen calendar. Missing filing dates are not inferred from statutory deadlines or borrowed from letter dates; those historical observations are excluded. Hotel dates come from the supplied peer release-date columns. Report dates are normalized to calendar dates, so same-day timestamps cannot evade the cutoff.

## Results

The original pre-results note is preserved verbatim in `data/processed/forecast_methods/gbv_features_v1/preregistered_note.md`; its SHA-256 is recorded in `preregistration.json`. The pass line and list above were written before any model execution.

| Feature | W1 GBV n / 14 | W2 GBV n / 10 | Required RNPL-ledger ratio W1 / W2 | Raw-ledger diagnostic ratio W1 / W2 | Diagnostic matched n W1 / W2 | Stable slope W1 / W2 |
|---|---:|---:|---|---:|---:|---|
| RNPL-corrected unearned fees | 0 | 0 | no baseline exists / no baseline exists | unavailable | 0 / 0 | unavailable |
| Funds-payable / funds-held growth | 3 | 3 | no baseline exists / no baseline exists | 3.1371 / 3.1371 | 3 / 3 | no / no |
| GBV momentum | 13 | 10 | no baseline exists / no baseline exists | 1.5444 / 1.5444 | 3 / 3 | no / yes |
| NTTO arrivals | 0 | 0 | no baseline exists / no baseline exists | unavailable | 0 / 0 | unavailable |
| Reviews stays index | 0 | 0 | no baseline exists / no baseline exists | unavailable | 0 / 0 | unavailable |
| Hotel RevPAR | 14 | 10 | no baseline exists / no baseline exists | 3.7089 / 3.7089 | 3 / 3 | yes / yes |
| Calendar pickup | 0 | 0 | no baseline exists / no baseline exists | unavailable | 0 / 0 | unavailable |

Every numerical raw-ledger ratio uses **2025Q4, 2026Q1 and 2026Q2**, in both windows. The cross-window comparison is therefore **vacuous**. These are three diagnostic forecast errors, not fourteen independent ledger comparisons. The RNPL-adjusted pass line is not replaced by this raw comparator. Funds-held can differ from funds payable because of balance-sheet classification; only the named funds-held series in the supplied KPI panel is tested.

| Target / feature | W1 n | W1 RMSE | W2 n | W2 RMSE | RMSE unit / basis |
|---|---:|---:|---:|---:|---|
| GBV y/y / funds growth | 3 | 6.4651 | 3 | 6.4651 | pp; dated features and expanding target history |
| GBV y/y / GBV momentum | 13 | 9.5767 | 10 | 5.5577 | pp; dated features and expanding target history |
| GBV y/y / hotel RevPAR | 14 | 5.7119 | 10 | 5.0861 | pp; dated features and expanding target history |
| R / funds growth | 3 | 118.6228 | 3 | 118.6228 | USD millions; full-sample target diagnostic |
| R / GBV momentum | 13 | 283.2193 | 10 | 264.2953 | USD millions; full-sample target diagnostic |
| R / hotel RevPAR | 14 | 264.2065 | 10 | 242.4810 | USD millions; full-sample target diagnostic |

For the retrospective R target, ratios to the raw-ledger diagnostic are funds 0.6077 / 0.6077, GBV momentum 0.9067 / 0.9067 and hotel RevPAR 0.7625 / 0.7625 (W1 / W2, each n=3 common cells). None is PIT residual evidence or a survivor. The underlying carried-part coefficients use subsequent observations; keeping feature dates clean does not cure a contaminated target definition.

Supplementary distance-to-integer-interval GBV RMSE is funds 5.9918 pp on n=3 / 3; momentum 9.1346 / 4.5981 pp on n=12 / 9; hotel RevPAR 5.2863 / 4.7448 pp on n=13 / 9. Noninteger reported growth is not coerced into an integer interval. The main target remains growth calculated from GBV dollars.

Exclusions are explicit in `full_failure_table.csv` and `availability_and_exclusions.csv`. Funds and the raw ledger lack enough dated annual source pairs before 2025Q4; missing filing dates are not manufactured. W1 momentum excludes 2023Q1 because four training observations were not yet published; momentum covers all W2 and hotel covers both full windows. All four unavailable feature families exclude every W1/W2 quarter. NTTO's supplied monthly observations lack publication and revision vintages. The reviews index extends backward in review time but uses later dumps; neither the historical weights nor the historical selected-listing universe is reconstructed at each guide date. Calendar pair observations exist, but their retrospectively selected historical pairs are not an archived forecast feature vintage. No raw stores were accessed and no downloads were made.

## What ran and verification

From the repository root, using its `.venv` interpreter:

```text
python -m pytest analysis/src/forecast_methods/gbv_features_v1/tests -q
# exit 0; 7 passed in 2.07s
python analysis/src/forecast_methods/gbv_features_v1/run.py
# exit 0; 0.932 seconds in the final measured CLI run
```

The tests cover same-day refusal (including intraday attempts), invariance to changing future peer values, unavailable annual filing pairs, rejection of same-day training outcomes, integer interval boundaries, refusal to substitute the raw baseline, and strict date ordering for every emitted forecast. Initial successful tests produced harmless pandas fragmentation warnings; reading only the necessary KPI columns eliminated them, with the same results. No harness files or other packages were changed. Parent owns frozen-harness regression checks and scoring.

The package writes 66 forecast/diagnostic rows across its complete training/replay calendar, zero registry rows, and all 28 feature × target × window result rows. Each OLS has two fitted parameters (intercept and slope), minimum n_train=4; there are zero tuned hyperparameters. Consensus is not consumed, so vendor/timestamp fields do not apply. Outputs preserve input hashes; they do not copy licensed data or raw stores. Sources remain the supplied processed summaries, whose publication metadata do not independently prove absence of later revisions.

## Interpretation and exact proposed memo sentence

**“No C3 feature qualifies for promotion: the required RNPL-adjusted ledger comparison has zero admissible historical cells in either window.”**

This is an infrastructure and evidence-availability statement, not a demand forecast. The separate raw-ledger losses offer no basis to assert that retargeting the entire earlier feature universe failed: this run tests the pre-registered subset, and most alternative-data vintages are unavailable under the stricter pre-guide rule. Do not infer that lower R diagnostic ratios establish incremental forecast power.

Completion recorded 2026-09-13 UTC. Actual agent token usage and full task wall time are unavailable from this runtime; code/test timings above are measured, not substitutes for agent usage.

## RESUME

Run the new package only; parent owns workboard edits, frozen tests, scoring and git. Preserve the distinction between missing required denominator and a failed or successful raw-ledger diagnostic. Never relabel the September RNPL ramp or retrospectively fitted R target as historical PIT data.
