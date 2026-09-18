# GE-JOINT-QUANT — timing and PR60 addendum, before first execution

15 September 2026. Independent review caught that using newly printed lag1 GBV at the event would be contemporaneous with the guide, not a forecast of it. No new fits/tests/results had been run when this addendum was written.

The **primary origin for target t is the earnings release for t−2**, predicting the guide released with t−1 earnings. Example: the August Q2 release forecasts the Q4 guide issued at the November Q3 release. Both t−1 and t GBV are unprinted at the origin and must be recursively forecast. Known information includes the t−2 actual released that day; no later company actual or target guide enters fitting. The oracle diagnostic supplies both unprinted GBV values only after fitting. All coverage exclusions remain recorded. This supersedes the contemporaneous origin in prereg item5.

Every matrix now exposes both `A/allocated_column` (conditional share) and `A/actual_revenue` (observed-total attribution), plus actual minus allocated dollar residual. The latter denominator does not convert an assumed allocation into an observation.

One bounded PR60 ablation uses `govdata_v2/qtd75_pit.csv`, selecting only an actual stored `commit_date <= origin`, with maximum age two quarters relative to the latest company quarter printed at that origin. Source is inherited historical git-vintage lineage; local raw EUROCONTROL mirror is absent and completeness remains qualified. No final-vintage flight series is admissible. For completed historical one-quarter-ahead pairs, regress the change in GBV year-on-year growth on `latest_available_flight_yoy - latest_company_gbv_yoy`, through the origin with one slope. Minimum six dated training pairs; slope constrained to [−2,2] as a stability policy; nonpositive GBV predictions are refused. Apply the slope to the origin's growth forecast, held constant across the one- and two-quarter recursive horizon. Primary no-flight method remains unchanged, and all ablation ineligible origins/reasons are retained. This is an auxiliary demand predictor, not a cohort measurement. No additional feature search.

Paired evaluation uncertainty: 2,000 deterministic year-cluster resamples of primary candidate/baseline losses, with 90% RMSE-ratio and mean-loss-difference percentile intervals, preserving pairs. Few evaluation years limit interpretation. A ratio interval including1 is not an established forecasting edge even if a point threshold happens to pass. Share-set uncertainty may be translated into conditional future revenue/guide ranges using the same origin inputs; those are model sensitivity ranges, not predictive intervals.

## RESUME

Run the frozen core implementation now; report the primary early-origin guide test first, then clearly separated flexible identification, stale-K2 and one-feature flight diagnostics. No post-event guide result can qualify for promotion.
