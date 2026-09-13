# M2: Time-series and ratio methods for the margin and the lines

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M2_margin_ts`. Method name: `margin-ts`.

## Idea

The simplest honest competitors. Every serious method must beat these, and one of them may be the best single object at h=0.

Objects (each a separate registry object; parameter counts small):
1. `yoy_margin_change`: margin_q = margin_{q-4} + delta, where delta is the recency-weighted mean y/y margin change over the last k quarters (k in 2,4);
   variant with the delta shrunk toward zero.
2. `incremental_margin`: EBITDA_q = EBITDA_{q-4} + m * (Rev_q - Rev_{q-4}), m the PIT recency-weighted incremental margin (last 4-8 y/y pairs), with
   the revenue forecast PIT from the frozen harness guide-cushion baseline (and a revenue-known spec).
3. `pct_rev_seasonal`: each cash line as % of revenue = same quarter last year's ratio + trailing y/y ratio drift; sum to EBITDA.
4. `per_night_seasonal`: each cash line per night = last year's per-night value x (1 + trailing per-night growth), times the nights forecast.
5. `sarima_margin`: a small seasonal ARIMA / ETS on the margin series and on log(lines), PIT refit (statsmodels), with documented order selection
   on the training window only. Only if it fits in time; skip with a note otherwise.
6. `ensemble_simple`: equal-weight mean of 1-4; and an inverse-MAE weighted mean using only past PIT errors (no look-ahead in weights).

## Tests (pre-register)

Which object beats `seasonal_naive` on adj EBITDA margin MAE at h=0/1/2 in both windows, both weightings; per-line results for 3 and 4;
calibration of the residual-based quantiles (coverage 80/90). Report the whole grid; count tests.

## LIVE

Same LIVE table as every method (3Q26-4Q27, FY26-28), base/bear/bull revenue, vs consensus and management. Say explicitly what 3Q26 margin the
seasonal-naive-with-drift gives, because that is the number the Street mostly uses.
