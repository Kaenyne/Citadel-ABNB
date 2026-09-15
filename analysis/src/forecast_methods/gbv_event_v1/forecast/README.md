# GE forecast reliability audit

Replays the exact frozen quant-validation preannouncement candidate. No estimator search, added forecast or production adoption. The preserved source worktree and pinned Git commit `4533811d8405403b7f465bda3b69790e4367b2d6` are required. The replay reads the original frozen model/protocol, writes only to a new output, and checks all20 original CSV outputs byte-for-byte.

From the submission-readiness worktree root:

```powershell
python -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/forecast/run.py --source '../quant-thesis-validation-v1' --out data/processed/forecast_methods/gbv_event_v1/forecast_v1/reproduction_NEW
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/forecast/test_forecast.py
```

`--source` is configurable and may be any preserved checkout containing the pinned source commit and its required protocol/input files. The default is the sibling `quant-thesis-validation-v1` worktree, not a machine-specific absolute path. The source commit is deliberately fixed in `run.py` to prevent an accidental model upgrade. The runner verifies its code, source tests and every canonical prior result against that commit; the invoked original runner separately verifies its protocol hashes and frozen L3 code/input identities. It does not fetch the unmerged branch. A checkout of merged main alone is therefore insufficient: supply the preserved source checkout explicitly or make the pinned commit and its frozen files available in an equivalent checkout. `source_manifest.csv` binds exact Git-object and working-file hashes; only known LF/CRLF representation equivalence is accepted when comparing to Git. Runtime `--python` defaults to the interpreter invoking this command, so it is configurable without editing code. Canonical all10-tests command above uses the tested preserved sibling layout; the analytical replay itself accepts any explicit source root.

Canonical outputs: `data/processed/forecast_methods/gbv_event_v1/forecast_v1/results_v1/`. The test file verifies this canonical audit and all21 frozen origins. Runtime dependencies are pandas, NumPy, Git and the earlier runner's timezone support. The exact source directory is trusted only through a subprocess-local Git safe.directory setting; no persistent Git configuration changes.

`pre_event_forecasts.csv` contains every63 method/origin row with abstentions. `per_event_decomposition.csv` retains every candidate scored row and the original fields, adds symmetric three-factor Shapley effects, and separates an ex-post actual-GBV substitution. `forecast_audit.json` supplies compact workbook/chart data. `frozen_scores.csv` preserves matched/own/pair and raw/interval errors. `shapley_cross_moments.csv` and `variance_reconciliation.csv` preserve covariance and mean terms. `event_influence.csv`, `paired_event_deletion.csv`, `frozen_year_deletion.csv` and `season_scores.csv` expose influence without refitting.

Interpretation: the three factors are weighted GBV, seasonal lambda and the inverse cushion divisor. Shapley averages every ordering of substituting predicted for ex-post factors. It is an exact symmetric attribution, not causal measurement of RNPL, FX or fees. All three effects sum to raw guide error; the administrative rounding adjustment is kept separate. Raw MSE includes factor cross moments; variance includes covariance. No independence assumption, new probability, four-quarter empirical calibration or executable oracle strategy is claimed.

The first execution stopped at Git's ownership check before calculations; `attempt_1.json` preserves the failure and process-local repair. Existing output IDs are refused. Research promotion FAIL is a successful completed audit.
