# K0 — corrected kernel engine v2

Pass. Gate 1 passed: 12/12 reference intervals, six Q3/Q4 displays, 63 module tests, 47 frozen tests and CLI exit 0 in 5.38 seconds. Revision authorized by the user after the failed v1 checkpoint; v1 evidence remains preserved.

## Pre-registered acceptance — 2026-09-12, before v2 results

All 12 accounting identities must lie within the published three-decimal rounding interval (absolute error <= 0.0005 percentage points plus 1e-12 numerical tolerance). The six specified Q3/Q4 values must additionally reproduce at two decimals. This resolves double rounding of the 2025Q1 reference without loosening its stated precision. Independent boundary tests must reject values outside that interval. All module tests must pass, all six public functions must refuse same-day/future/undated supplied data, regional dollar aggregation and provenance must work, the CLI must complete under 60 seconds, and the frozen harness/L0 must still return exactly 47 passed.

Live variant selection remains lowest common-W1 LOO relative revenue RMSE, with chronological nested historical selection and ex-COVID fallback below eight selection cells. This is a specification diagnostic, not an alpha backtest. No team decision is adopted.

## Work to verify

Fix acceptance precision, regional integer validation and publication provenance, prevent forecasts of already printed targets, and calibrate guide intervals using full pre-origin cushion history with the requested statistic. Retain explicit abstention where a pre-guide lag or vintage is unavailable. Execute the complete runner before declaring the gate passed.

## RESUME

Parent owns v2 Gate 1. Do not import the failed v1 module for downstream work. Results pending.

## Verified results

```text
Module command: python -X utf8 -m pytest analysis/src/forecast_methods/kernel_engine_v2/tests -q
63 passed in 24.29s; exit 0.

Frozen command: python -X utf8 -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q
...............................................                          [100%]
47 passed in 5.44s

CLI command: python -X utf8 analysis/src/forecast_methods/kernel_engine_v2/run.py
acceptance test: PASS on all 12 cells
quarter  lambda_pct  expected_pct display_2dp  match_reference_precision
 2023Q3   17.390785        17.391       17.39                       True
 2023Q4   11.946140        11.946       11.95                       True
 2024Q1   13.034483        13.034       13.03                       True
 2024Q2   13.448613        13.449       13.45                       True
 2024Q3   17.145482        17.145       17.15                       True
 2024Q4   12.117264        12.117       12.12                       True
 2025Q1   12.325497        12.325       12.33                       True
 2025Q2   13.945946        13.946       13.95                       True
 2025Q3   17.181818        17.182       17.18                       True
 2025Q4   12.025974        12.026       12.03                       True
 2026Q1   12.612245        12.612       12.61                       True
 2026Q2   13.736041        13.736       13.74                       True
LIVE DEFAULT ewm (historical default selection is nested before each origin)
 variant window  n  rmse_pct                       basis
ex_covid     W1 14  1.829421 retrospective_LOO_selection
ex_covid     W2 10  2.067514 retrospective_LOO_selection
   last3     W1 14  1.829421 retrospective_LOO_selection
   last3     W2 10  2.067514 retrospective_LOO_selection
     ewm     W1 14  1.804318 retrospective_LOO_selection
     ewm     W2 10  2.020128 retrospective_LOO_selection
quarter       point  guide_mid_musd               status
 2026Q3 4808.362929     4723.784001         printed_lags
 2026Q4 3214.775751     3158.227962 conditional_scenario
 2027Q1 3121.422848     3066.517133 conditional_scenario
{
  "as_of": "2026-09-12",
  "acceptance_pass": true,
  "acceptance_n": 12,
  "live_default": "ewm",
  "historical_default": "nested W1 LOO within the pre-origin information set; ex_covid fallback below eight common cells",
  "run_seconds": 5.384324299986474,
  "under_60_seconds": true,
  "guide_origins": 14,
  "guide_origins_refused": 14,
  "rnpl_scenario_available": "2026-09-11",
  "frozen_files_modified": false,
  "registered_forecasts": 0
}

```

Historical control alarms: 1/6 eligible cells in W1 and 1/6 in W2 (same six cells). At strict historical guide origins, printed-lag kernel is unavailable on 14/14 W1 and 10/10 W2; this is an information-set failure for a pre-guide alpha claim, not an accounting failure. First v2 development test failed solely on the supplemental 17.145 display comparison (binary bankers rounding); explicit decimal half-up fixed that comparison, preserving the original precision interval. Full failed development summary is in LANE1_RUN_LOG_v2.md.

## Parameters and interpretation

Fixed lag weight 2/3; three lambda candidates; EWM half-life 2 years; trailing 8 cushions; two-year blocks; 4,000 fixed-seed draws; last 6 chronological calibration residuals; two-parameter ledger regression. LOO default ewm is retrospective model selection, not historical evidence of alpha. RNPL ramps and subsequent GBV growth persistence remain conditional scenarios dated 11 September; no undisclosed ramp is backdated. The live ewm training history is broader than the common-W1 selection sample and should be stress-tested downstream. Regional coefficients remain X-owned and dollar aggregation is tested.

## RESUME

A must import kernel_engine_v2. Its pre-guide dates must remain strict, report unavailable cells and separate any post-letter diagnostics. Parent may start Gate 2 now. No forecasts registered by K0; no scorer required at this checkpoint.
