# M1: Driver-based cost lines v2 (per-unit costs on the revenue drivers), point-in-time

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M1_driver_lines`. Method name for the registry: `driver-lines`.

## Idea

WS31b modelled each cash cost line per unit (per night, per $GBV) with elasticities on 14 quarters, equal-weighted, full sample. Rebuild it as a
point-in-time, recency-weighted, driver-conditional model that uses the revenue-side inputs the team already forecasts: nights, GBV, ADR
(ex-FX and FX), take rate, regional nights mix (NA / EMEA / LatAm / APAC), seats and Experiences/Services volumes, length of stay and party size
where WS01's census says they are available with PIT timing, and the disclosed step-changes (AI support, hosting contracts, brand campaigns).

## Specification (keep it small; publish parameter counts)

For each cash line L in {cor, ops, pd, sm, ga} (and sm split brand/performance if WS02 has the split):
  log(L_q) = a_L + b_L * log(driver_q) + s_L[quarter-of-year] + g_L * t + e_q, with `driver` = GBV$ for cor, nights for ops, revenue for sm (test
  nights too), and trend-only (headcount-like) for pd and ga, plus optional regional-mix and seats terms tested one at a time.
Fit on 1Q21 onward (2020 is a shock; test including it as a variant), exponential weights half-life 4Q. Adjusted EBITDA = revenue - sum(lines)
- other add-backs (from WS02's small residual items, modelled as % of revenue trailing-4). Margin follows.
Variants to register as separate `spec_id`s: (a) per-unit trend only (31b-style), (b) with regional mix, (c) with seats/experiences, (d) with the
disclosed step dummies, (e) revenue-known. Keep the object count manageable (one object per line-model family, specs inside).

## Tests (pre-register)

Beat `seasonal_naive` and `pct_rev_last4` on adj EBITDA margin MAE at h=0 and h=1 in W1 and W2, equal and recency weighted; report per-line
MAE too. Report leave-one-year-out stability of b_L. Report which variant wins and whether the win survives both windows. Expect the
discretionary lines to be near-unforecastable from drivers; say so if true, with the numbers.

## LIVE

3Q26, 4Q26, 1Q27-4Q27 by line and total, base/bear/bull revenue paths; FY26/27/28 annual; compare to WS31b's three profiles, WS30's walk,
consensus (WS03) and the management floor. State the incremental margin your model implies for FY27 vs FY26 and the seasonal Q1/Q3 profile.
