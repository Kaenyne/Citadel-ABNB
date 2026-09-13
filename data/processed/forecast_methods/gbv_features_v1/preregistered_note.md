# C3 — GBV features and kernel residual

Agent sub-C3 · 2026-09-13 UTC · branch codex/lane1-full

**underpowered** — pre-registration; no results have run. The required historical RNPL correction has no admissible vintage in the supplied inputs. This verdict will be completed after the availability audit and feature tests.

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

Pending execution.

## RESUME

Run the new package only; parent owns workboard edits, frozen tests, scoring and git. Preserve the distinction between missing required denominator and a failed or successful raw-ledger diagnostic. Never relabel the September RNPL ramp or retrospectively fitted R target as historical PIT data.
