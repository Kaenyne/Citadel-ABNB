# B2 power refuter — preregistration

Codex `refute_b2_power` · 2026-09-13 17:42:26 UTC · parent branch `codex/lane2-full`.

The exact sentence under review is: “The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.”

## Pre-registered pass line

“Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.”

This is an audit of an already disclosed negative result. Independently recompute the sentence's counts and means from B2 event cells and the source next-open return file, then evaluate at least five explicit attempts to refute it. A descriptive arithmetic statement is not refuted merely because the experiment has low power; an implied population claim must be distinguished from that statement.

Fixed diagnostics before execution: 95% Wilson intervals; exact one-sided binomial lower-tail probabilities against p=0.70; illustrative exact-binomial skill detection against p=0.50 at alpha=0.05 with 80% power; and the minimum detectable return mean under an independent normal one-sample t model at one-sided alpha=0.05 and 80% power. These are optimistic planning benchmarks, not valid independence assurances for this small time series. Return intervals use two-sided 95% Student t intervals, also illustrative. Report window overlap and leave-one-event-out return signs without treating observations or windows as independent replications.

Count the specifications evidenced by B2's preregistration, code and output tables. Explicitly distinguish the original 0.5pp threshold and 20/60-day horizons from a new post-hoc audit grid: thresholds 0.5/1/1.5pp, horizons 1/5/20/60 days, weights 0.33/0.5/2/3, both PIT/full-sample replays, and both windows. The new grid cannot replace the original gate or rehabilitate a failed result. Retain all outcomes. Do not import B2's statistical helpers. No registrations or scorer runs are needed because this audit creates no forecasts.

## RESUME

Run the new independent audit in `analysis/src/forecast_methods/refute_b2_power_v1/`, preserve a timestamped output directory and receipts, and write the final exact-sentence verdict to the new `REFUTE_B2_power.md` note. Parent owns the shared workboard and final integration.
