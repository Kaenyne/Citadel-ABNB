# Joint versus fixed conversion — comparable next-guide snapshot

15 September2026 ·`codex/submission-readiness-v1`. New `gbv_joint_cohort_v1/next_guide_v1/` package. Engineering consistency **PASS** against the frozen workboard specification. Prior predictive-promotion failure and unavailable physical-cohort measurement are unchanged.

| Q4 2026 snapshot, USD millions | Joint candidate | Fixed-lag comparator |
|---|---:|---:|
| Revenue |3,244.389|3,219.235|
| Implied guide midpoint |**3,185.247**|**3,160.552**|
| Q4 seasonal conversion scale |12.681513%|12.040367%|
| Training count |20 complete quarters|5 eligible Q4 observations|

The jointly comparable guide difference is$24.695m. Calculation vintage and information cutoff are15September2026; last available company publication is6August2026, for Q2. Both predictors use the same Q3GBV forecast of$26,505.532m. The joint candidate also uses Q4GBV forecast$23,611.915m. Both GBV forecasts carry the latest published GBV growth of15.744681%; Q2GBV$27,200m and older inputs are reported. `gbv_inputs.csv` labels every status and publication date.

The accepted primary rule is refitted on all20 complete quarters,2021Q3–2026Q2. Its pooled exposure weights are35.895645% current quarter,47.291024% lag1,16.813331% lag2 and0% on the equal lag3/4 tail. These are model coefficients, not measured cohort percentages; the zero tail is a fitted boundary, not evidence that old bookings generate no revenue. The earlier W1/W2 sensitivity points used14/10-quarter subsets and therefore are different fits.

Both revenue estimates divide by the same `1 + 1.856743%` arithmetic-mean cushion, computed from the last8 completed guided quarters,2024Q3–2026Q2. Source values and each ratio are saved in `cushion_history.csv`. The complete dollar contributions and forward/backward identities are in `contributions.csv`.

Command: `python analysis/src/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/run.py`, using the repository virtual environment as documented in README. First run and new-directory rebuild exit0. All6 result files and the manifests reproduce byte-for-byte;4 source hashes remain unchanged, including accepted core source. Basic arithmetic independently reproduces contributions, totals, cushion and guides. Appending a future unpublished quarter with extreme GBV/revenue and poisoning the future issued guide changes neither point. Receipt: `next_guide_v1/validation_v1/receipt.json`. Manifest SHA-256: `3a6682753c2a14de6dde51c2f84386c4759a6fa3cfb5e8998f463d35235e8b18`.

No predictive interval is calculated. Historical RMSE and near-fit sensitivity are not calibrated next-event probability bands. These two points do not establish an edge against date-matched Street expectations or a causal RNPL effect; no stock-price target or thesis-direction decision follows. Parameter counts are7/8 for joint revenue/guide and4/5 for the fixed seasonal model/guide, with the shared cushion included in guide counts. Parent owns any new LIVE registration and scorer runs.

## RESUME

Use this exact same-cutoff point pair to explain how the two predictors work, while keeping historical fit, forecast robustness, physical cohort evidence and Street-relative trading edge separate. Independent reviewer verifies the saved inputs/formulas; parent may register the two research snapshots under new LIVE-only method names. Do not promote the candidate or present its coefficients as observed reservations.
