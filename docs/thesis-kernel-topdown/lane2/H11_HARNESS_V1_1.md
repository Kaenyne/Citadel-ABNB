# H11 — Harness FORMAT 1.1: verify, do not build (run by the parent; Gate 1, part 1)

**Role in Lane 2:** the package is already in git (`analysis/src/forecast_methods/harness_v1_1/`). Gate 1 confirms it on this machine so
every later registration has somewhere to go.

## Files this agent reads
- `analysis/src/forecast_methods/harness_v1_1/README.md` (the one-rule change), `harness_v1_1/tests/`
- `data/processed/forecast_methods/harness/scoreboard.csv` (frozen board, for the identity check)

## Task
```bash
python -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q        # expect 47 passed (frozen, untouched)
python -m pytest analysis/src/forecast_methods/harness_v1_1/tests -q                                    # expect 37 passed
python analysis/src/forecast_methods/harness_v1_1/score.py                                              # exit 0; 276 rows -> harness_v1_1/scoreboard_v1_1.csv
python - <<'PY'
import sys; sys.path.insert(0, "analysis/src/forecast_methods")
from harness_v1_1 import RUN_DATE, LIVE_VINTAGE_MIN, paths as P; print("RUN_DATE", RUN_DATE, "LIVE from", LIVE_VINTAGE_MIN, "format", P.FORMAT_VERSION)
PY
```
Then confirm `git status` shows no change under `data/processed/forecast_methods/harness/` (the frozen board must not move) and that
`scoreboard_v1_1.csv` has the same 276 (method, object, target, window, prior_basis) rows with identical `rmse` — the test
`test_historical_scores_are_identical_to_the_frozen_scoreboard` already asserts it; quote its pass in the run log.

## Pass line (pre-registered)
47 frozen tests green · 37 FORMAT 1.1 tests green · 1.1 scorer exit 0 with 276 rows identical to the frozen board · RUN_DATE prints today's date.
Anything else → STOP (this is infrastructure, not a research result).

## Outputs
A section in `05_backtests/LANE2_RUN_LOG.md` with the verbatim outputs. No new package.
