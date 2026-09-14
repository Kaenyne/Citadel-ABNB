# K0 — Kernel engine

fail. Gate 1 STOP. Parent Codex; 2026-09-12; branch `codex/lane1-full`. The first K0 pytest returned 1 failed / 46 passed. No downstream agents were spawned.

## Pre-registered pass line

Registered before any new K0 estimates or tests on 2026-09-12 21:25:30 UTC. The twelve historical lambda cells must reproduce to two decimals (Q3 17.391 / 17.145 / 17.182 and Q4 11.946 / 12.117 / 12.026 for 2023–2025; Q1 and Q2 use 2024–2026). The new module's pytest must pass, including refusal of inputs printed on or after `as_of` in every public analytical function. The regional interface must accept booking-dated GBV in USD plus separately supplied, dated regional lambda parameters, and consolidated revenue must equal the sum of regional revenue. The entry point must exit 0 in under 60 seconds. The frozen harness/L0 suite must remain 47 passed.

## Pre-registered implementation and selection policy

Retain the published two-lag weight 2/3, 1/3. Compare ex-COVID same-season mean (absolute nights year-on-year above 25% excluded), last-three same-season mean, and exponentially weighted same-season mean (fixed half-life two same-season observations). Choose the live default by leave-one-quarter-out relative revenue RMSE on W1. That comparison is explicitly retrospective specification selection, not a historical PIT performance claim; historical default selection must be nested within data available before each origin, with a deterministic ex-COVID fallback when selection is underpowered. Publish counts, exclusions and both windows.

Use exact quarter-key joins rather than row shifts after filtering. Explicitly supplied observations with missing publication dates, duplicates, nonfinite or nonpositive values, or dates on/after `as_of` are rejected. Repository loaders may filter their full source before passing observations to functions. The calendar supplies publication dates when the specified regional GBV schema omits them. Regional lambda estimation belongs to X; K0 validates and applies supplied coefficients and never sums coefficients as if they were dollar revenue.

The specification's timing claims will be tested rather than assumed: the prior quarter's GBV arrives in the same letter as the next-quarter guide, and the strict-before rule can make it unavailable at a date-only guide origin. Future GBV must be explicitly forecast and labelled. RNPL ramp assumptions are scenario inputs, not disclosures; uncertainty or missing vintages must remain visible. No team decisions are made here.

## Results

Command: `python -m pytest analysis/src/forecast_methods/kernel_engine_v1/tests -q`. Exit code 1; 1 failed, 46 passed, 69 performance warnings; pytest wall time 6.85 seconds. Full output: `data/processed/forecast_methods/kernel_engine_v1/gate1_pytest.txt` and `LANE1_RUN_LOG.md`.

The failing acceptance comparator separately rounds the computed 2025Q1 lambda `12.325497287522605` and its published three-decimal reference `12.325` to two decimals, obtaining `12.33` and `12.32`. This is a rounding-boundary defect in my test; it does not establish an arithmetic error in the revenue/GBV identity. Nevertheless, the required pytest is not green and the explicit Gate 1 STOP applies. The comparator was not repaired after the stop.

The other 46 tests passed, including temporal refusals in all six public functions, missing-quarter refusal, input validation, regional dollar aggregation, guide arithmetic and chronology, scenario labelling, and withholding the live monitoring rule at earlier origins. These passes do not override the failed gate.

The K0 entry point was not executed after the failed test. Its runtime requirement, final lambda output, LOO results and frozen live default remain unverified. The present module has no accepted status. The frozen harness/L0 integrity suite was checked after the failure and remained 47 passed in 11.60 seconds.

## RESUME

Wait for the user's response to the Gate 1 STOP. Resolve and document the reference-precision comparator while retaining the original failure evidence. Review all implementation choices, then rerun the complete gate before freezing a default or using the module downstream. A, X, the other packages and all refuters remain unstarted.
