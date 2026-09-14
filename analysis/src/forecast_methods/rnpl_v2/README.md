# RNPL v2

From repository root, with `.venv` activated:

```text
python analysis/src/forecast_methods/rnpl_v2/run.py --as-of 2026-09-13 --register
python -m pytest analysis/src/forecast_methods/rnpl_v2/tests -q
```

The script rebuilds the new output folder only and registers `rnpl-v2__revenue_next_q.csv` only when requested. Parent owns both scorer runs. No network, frozen-harness edits, existing-model writes or historical scenario backdating.

Inputs: reported KPI panel; frozen K1 ex-COVID pooled coefficients (8 inherited fitted parameters, used only for retrospective stock reconstruction); D1 grid dated 11 September (2,025 scenario cells, not an empirical distribution); K0 v2 public API for all forecast lambdas and charts. The stock norm window is 2022Q1–2025Q2. The legacy 2023Q1 start and $4,800M Q3 scenario are preserved only as rejected-joint-solve sensitivity. No restated-unearned-fee forecast is constructed.

Forecasts use four inherited K0 seasonal coefficients, fixed 2/3 lag weight, three externally specified nights paths, constant Q3 ADR across paths, and D1 central assumed differential propensity (+4pp). D1's GBV share is recovered exactly from its nights share and RNPL/non-RNPL ADR ratio. Leakage is **gross flow-share × differential propensity**, not a measured conditional-backlog cancellation rate. The grid's lead-time/rebooking dimensions do not enter this deliberately simple stress; repeated results are not independent observations or a predictive distribution.

Q3 revenue cannot respond to contemporaneous nights under this two-lag kernel. Q4 responds only to Q3 nights; Q4 nights would first enter Q1 2027. The central D1 stress is applied to Q3 in all three paths and Q4 for team/ex-NA paths. Q4 Theo is registered with **no extra leakage**, because its Q3 nights input already includes the cancellation tail and the overlap is unidentified. All pure-kernel and full-stress columns are retained. This asymmetry is an explicit overlap guard and makes these conditional scenarios, not a ranking of forecasts. No user/team path is adopted.

Registry has LIVE rows only, with three `spec_id` variants and both replay labels (identical current information); no distribution quantiles beyond q50 are supplied. Historical W1/W2 performance is unmeasured. The scorer pools `spec_id`; future variant scoring must read individual rows rather than interpreting its blended object score.

`false_alarm_rates.csv` separates pre-RNPL empirical false alarms, all-history alarms, and retrospective fixed-card thresholds. Small descriptive samples do not estimate a reliable RNPL detection probability. D-06 evidence and D-10 proposal are in `ALPHA_F_RNPL.md`.
