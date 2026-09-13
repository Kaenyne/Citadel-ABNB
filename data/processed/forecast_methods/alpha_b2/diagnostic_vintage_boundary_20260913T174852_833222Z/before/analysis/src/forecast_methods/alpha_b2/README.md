# B2: term structure and consensus revisions

From the repository root with `.venv` active:

```text
python -m pytest analysis/src/forecast_methods/alpha_b2/tests -q
python analysis/src/forecast_methods/alpha_b2/run.py
```

Each execution creates an immutable timestamped subfolder under `data/processed/forecast_methods/alpha_b2/`. `--no-register` writes a candidate only. Registration uses FORMAT 1.1; repeated identical registrations preserve the existing file. The explicitly authorized metadata correction uses `--correct-horizon-metadata`: it verifies that every column other than `horizon_q` and explanatory notes is unchanged, preserves the old registry bytes in the new run directory, and re-registers. The parent runs both scorers.

Preregistration: `docs/revenue-forecast-strategy/05_backtests/ALPHA_B2_TERM_STRUCTURE_V2.md`. Main results: the companion `_RESULTS.md` note.

S1 uses the imported kernel at the day after the letter, asserts latest input date is no later than the letter, and uses the same letter's GBV. The imported seasonal lambda and trailing-eight median cushion include all prints available on that letter date. Historical current-consensus rows and quarantined or unattributed rows are excluded. W1/W2 evaluation windows follow the guided quarter; registry windows follow the q+2 target, as required by the frozen validator.

The brief prescribes GBV(next) = latest-quarter GBV × (1 + trailing-four observed y/y growth). This ignores seasonal levels. The LIVE Q1 2027 extension applies the same growth twice. Weight sensitivity (0.33/0.5/2/3) holds imported lambda fixed; it is not an alternative fit or a predictive interval. Output tables show both raw revenue and guide-equivalent revenue divided by cushion. Registration targets realised `revenue_musd`, so it correctly uses the raw revenue before cushion. The sidecar's `horizon_from_print=2` retains the brief's q+2 identity; the LIVE Q1 2027 extension has `horizon_from_print=3`. The registry instead follows the authoritative FORMAT unit: `horizon_q = target-quarter ordinal - vintage-calendar-quarter ordinal`. Historical rows and LIVE Q4 2026 therefore have `horizon_q=1`; LIVE Q1 2027 has `horizon_q=2` at the September 2026 vintage.

Full-sample coefficients/cushion explicitly look ahead to RUN_DATE; historical GBV inputs remain vintage-correct. Only PIT statistics gate. Missing q+2 consensus, sparse FY buckets, zero revisions, or unavailable lambda remain visible. FY uses printed revenue, next-two kernel guide midpoints, and prior-year same-quarter revenue beyond; this is an arithmetic sensitivity against management's bucket midpoint, not FY consensus.

Inference: 95% Wilson sign intervals; 10,000 fixed-seed permutations; paired two-event moving-block bootstrap for correlation. Permutations break serial order and bootstrap blocks are short: p-values/intervals are descriptive. Return legs use only executable next-open excess returns. No forecasts, scores, or results are sourced from Airbnb web requests or licensed data.
