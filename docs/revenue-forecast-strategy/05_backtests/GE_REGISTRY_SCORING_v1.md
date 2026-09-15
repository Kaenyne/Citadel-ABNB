# GE conditional LIVE registration and scorer preservation audit

15 September 2026. Owner: roadmap_auditor. Source is the parent's new four-quarter `integration_v2/model.json`, SHA256 `91f8eb92d4a94ba52750e5aefb8a74f6a03fa50f5b548cbd1101c22f46b1e349`. Registration is conditional recordkeeping, not empirical model promotion or a trading recommendation.

**PASS:** seven new FORMAT1.1 LIVE PIT rows registered under `gbv-event-v1`; both unchanged scorers ran successfully before and after; all288 historical score rows agree between the formats and remain unchanged after registration. All120 pre-existing harness/source/registry files in the protection census remain byte-identical. No frozen source, checked-in scoreboard or original registry file was edited.

## Registered objects

| Object | Target column | Quarter | Horizon q | Point, USDm | Lambda n_train |
|---|---|---|---:|---:|---:|
|four-quarter-revenue|revenue_musd|2026Q3|0|4808.362929493917|5|
|four-quarter-revenue|revenue_musd|2026Q4|1|3179.343654286404|5|
|four-quarter-revenue|revenue_musd|2027Q1|2|3055.680580442422|6|
|four-quarter-revenue|revenue_musd|2027Q2|3|4048.395307573128|6|
|forward-guide|guide_mid|2026Q4|1|3123.419115173388|5|
|forward-guide|guide_mid|2027Q1|2|3001.9312702955167|6|
|forward-guide|guide_mid|2027Q2|3|3977.1841815226035|6|

The exact machine-readable rows are the two new registry files. `revenue_musd` and `guide_mid` are authoritative metric columns in the frozen targets panel. Horizons count calendar quarters from the quarter containing vintage2026-09-15, namely2026Q3; they are not the forecast-to-release day count. Knowable-from is conservatively recorded as13September2026. No consensus enters the forecast equation, so no Street vendor input is invented.

Each row carries n_params5 for the path's four seasonal lambdas and shared cushion. n_train is the row's seasonal-lambda observations5/6; the cushion uses8 distinct realized revenue/guide observations and is noted separately. These counts are not summed into an independent statistical sample. q50 equals the point because the format requires that field; every other quantile and SD is absent. This supplies no calibrated predictive distribution. Q3 guidance is already issued, so its diagnostic implied guide is deliberately not registered.

Registry file SHA256 values:

- `registry/gbv-event-v1__four-quarter-revenue.csv`: `edbc66f687d1509b327f50f7e335c0806910d34ba218b470e2b10f78c2538adb`.
- `registry/gbv-event-v1__forward-guide.csv`: `a63bac08c5306d260ddcb57d19f630e31f6c8a34faf2077e23e82c0a7b9c9055`.

## Execution and preservation

From the submission-readiness worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/registry_scoring/run.py --mode register --out data/processed/forecast_methods/gbv_event_v1/scoring_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/registry_scoring/test_registry_scoring.py
```

Both commands exited0; five focused tests passed. The authoritative FORMAT1.1 validator/writer prepared new CSV bytes in a new staging directory, after which exclusive-create file handles added the two registry files. Existing object names are refused before any output directory or registry change. A test confirms that refusal. The original registry writer is not patched on disk.

The wrapper imports each unchanged scorer module and calls its original `main()`, redirecting only runtime output destinations for scoreboardCSV, scoreboardMarkdown and the conformal grid. Four successful runs are retained: before_FORMAT1.0, before_FORMAT1.1, after_FORMAT1.0 and after_FORMAT1.1. Logs and outputs are under `data/processed/forecast_methods/gbv_event_v1/scoring_v1/`. All288 score rows match numerically at1e-9 absolute tolerance; new LIVE rows enter no historical metric. The unchanged source files, checked-in scorer outputs and original registry files are bound in `protection_before.json` and independently rechecked in `preservation.csv`. SciPy is available in the actual runtime, so the missing-SciPy PIT omission was not introduced.

The wrapper receipt records the exact model, code and new registry hashes. Its manifest binds all audit outputs. The five focused tests cover no overwrite, no already-issued guide registration, calendar horizons, formula/sample-size corruption rejection, absent probability fields, model-to-registry values and preserved historical scores/files.

## Pre-existing checked-in scoreboard drift

This is measured **before** the new LIVE files are added and is not caused by them:

| Checked-in scoreboard | Baseline difference |
|---|---|
|FORMAT1.0,280 rows|Eight existing alpha-a2/alpha-b2 score rows are absent from the checked-in file; eight tracker-backlog rows have two changed conformal fields each (coverage and mean width).|
|FORMAT1.1,276 rows|Twelve existing score rows are absent: alpha-a2/alpha-b2 plus the four DoltHub baseline rows. No overlapping numerical differences were found.|
|Fresh both formats,288 rows|Identical before/after the seven new LIVE rows and identical across formats.|

`preexisting_scoreboard_drift.csv` contains36 records:20 row-presence differences and16 numeric-cell differences. The old scoreboard files remain untouched in accordance with the copy-only rule. This audit settles that the current shared registry reproduces288 historical rows consistently; it does not retroactively rewrite legacy snapshot provenance or alter prior failed research verdicts.

## Reproduction and RESUME

The objects now exist, so never repeat register mode against them. Use `--mode audit-existing --out data/processed/forecast_methods/gbv_event_v1/scoring_reproduction_NEW`; it validates the existing files against the exact model and re-runs both scorers into new paths without changing registration. Every output directory must be new. Parent may include the two registry additions and this completed audit in the eventual publication review. No new historical forecast method, calibrated band or promotional claim follows from LIVE registration.
