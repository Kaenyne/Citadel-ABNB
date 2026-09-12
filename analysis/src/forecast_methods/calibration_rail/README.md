# calibration-rail

The challenger and calibration rail: baselines, monotone GBM challenger, split
conformal, and PIT/CRPS on the existing prediction ledger. Infrastructure and
referee, not a lens: the deliverable is whether the interval is honest at n≈20.

## Run command

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/run.py
```

Exit code 0 on success (1 if any step failed; the steps that ran before a failure
still write their outputs, so a crash never wipes prior progress). Steps can also be
run individually in this order: `harness/run.py` → `reference_scoreboard.py` →
`gbm_challenger.py` → `pit_crps_ledger.py` → `chronos_attempt.py` →
`harness/score.py`.

## Files

| file | part | what it does |
|---|---|---|
| `_common.py` | — | path setup, imported first by every script |
| `reference_scoreboard.py` | (a) | extends harness baseline coverage to `nights_yoy`, `adr_yoy`, `gbv_yoy`, `take_rate_pct` (the harness's own `BASELINE_SPECS` only covers 4 of the 6 metrics this package needs as denominators for every other package); confirms two ground-truth claims from data already on disk |
| `gbm_challenger.py` | (b) | monotone-constrained `HistGradientBoostingRegressor`, 4 PIT features, monotone constraint on the ADR-FX lag-2 channel only, nested expanding-window CV, two objects (`gbm_revenue`, `gbm_surprise_guide`), both replays |
| `pit_crps_ledger.py` | (d) | PIT histogram + CRPS on the 391-row `20_prediction_ledger.csv`, Gaussian predictive distribution from each (target, model)'s own pseudo-out-of-sample error sigma |
| `chronos_attempt.py` | (e) | attempts a dry-run pip resolve for `chronos-forecasting`; documents the skip decision rather than gambling the time-box on a cold-cache torch install |
| `run.py` | — | entry point; runs everything above in order, then re-runs `harness/score.py` |

Part (c), split conformal, is not a separate script: the harness's own `score.py`
computes rolling split-conformal coverage and the attainable-coverage grid for
**every** registered object (mine and every other package's) as soon as they are
registered, using `n_cal=6, alpha=0.2` by convention. Running `harness/score.py` at
the end of this package's `run.py` is what produces those numbers; see the note for
the read-out on my own objects specifically.

## Registered objects

- `calibration-rail__ref_naive.csv`, `ref_ar1.csv`, `ref_trailing4.csv` — reference
  baselines on `nights_yoy`, `adr_yoy`, `gbv_yoy`, `take_rate_pct` (harness-gap fill).
- `calibration-rail__gbm_revenue.csv` — monotone GBM, target = `revenue_musd` via
  predicted `revenue_yoy`.
- `calibration-rail__gbm_surprise_guide.csv` — monotone GBM, target = `revenue_musd`
  via predicted surprise vs the guide midpoint.

## Data outputs (not registry)

`data/processed/forecast_methods/calibration_rail/`:
`claims_confirmation.csv`, `pit_crps_ledger_detail.csv`, `pit_crps_ledger_summary.csv`,
`chronos_attempt.txt`.

## Harness change request

See the note (`docs/revenue-forecast-strategy/05_backtests/calibration-rail.md`),
heading "Harness change request".
