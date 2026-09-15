# Scoring convention correction

The independent replay's `horizon_v1/receipt.json` and original reviewer note v1 contain a mistaken descriptive implication that frozen harness scores are interval-based. Direct review of frozen `harness/score.py` confirms it calculates raw point-minus-actual errors. Both local replay and frozen scorer are raw midpoint metrics. This correction supersedes that descriptive limitation string; all source hashes, numerical checks, pass counts, covariance tables and raw-error conclusions remain valid. No original result or frozen scorer is overwritten. The parent commissioned an additive ±$0.5M sensitivity and a harness change request; its results have their own receipt.

Canonical corrected narrative: `docs/revenue-forecast-strategy/05_backtests/GD_REVIEW_RESULTS_v2.md`. This is a documentation correction, not a changed forecast, test threshold or quantitative outcome.
