# Forecast scope: Q3 2026 through Q2 2027 maximum

15 September 2026. User-directed scope correction. Codex parent with a bounded independent dependency review by roadmap_auditor. Branch `codex/submission-readiness-v1`, base main `2dfe0c2a`.

## Decision

The active submission forecast ends at **Q2 2027**. Its four forecast columns are **Q3 2026, Q4 2026, Q1 2027 and Q2 2027**. This supersedes any suggestion in `SR_QUARTER_SUBMISSION_READINESS_v1.md` that longer-horizon L4 financial or valuation schedules should be part of the required submission build.

The objective is to use top-down conversion and bottom-up operating evidence to predict upcoming forward guidance and define conditional earnings-event stock reactions. Historical data remains available for calibration and comparisons; it is not an extension of the forecast horizon. As-of-date forecasts and later event-date updates must be stored as separate vintages.

## Four-quarter roles

| Quarter | Role | Required outputs |
|---|---|---|
| Q3 2026 | Current-quarter nowcast; informs the next announcement | Booked units, ADR, GBV, revenue, quarterly costs/margin. Compare with already-issued Q3 guidance; do not present its guide as an unknown future announcement. |
| Q4 2026 | Primary forward forecast at the Q3 results event | Predicted nights-guidance language/interval, revenue-guide range, and margin/spending implications. |
| Q1 2027 | Next guide forecast and persistence check | The same quarterly operating/guidance objects, with explicit assumptions for RNPL and other temporary effects. |
| Q2 2027 | Maximum extension | Same calculation framework and visible assumptions; no further quarters are required to produce its revenue/guide. |

Company guidance language and analyst forecasts of realized booked units are separate objects. A forecast of 7% realized growth is not automatically a prediction of management's guide wording. An annual management-policy statement may be recorded as context without constructing a full-year 2027 financial forecast.

## Correct dependency map

The retained operational equation is `revenue[t] = lambda[season] * (2/3 * GBV[t-1] + 1/3 * GBV[t-2])`; the guide applies the explicitly selected cushion policy. This is the retained predictive model, not a claim about physical booking-cohort shares.

| Revenue/guide target | First lag, weight 2/3 | Second lag, weight 1/3 | Status at the frozen September origin |
|---|---|---|---|
| Q3 2026 | Q2 2026 GBV | Q1 2026 GBV | Both printed; Q3 guide already issued |
| Q4 2026 | Q3 2026 GBV | Q2 2026 GBV | One forecast GBV input |
| Q1 2027 | Q4 2026 GBV | Q3 2026 GBV | Two forecast GBV inputs |
| Q2 2027 | Q1 2027 GBV | Q4 2026 GBV | Two forecast GBV inputs; Q1 operating assumptions need an explicit contract |

Q2 2027 booked units and ADR can be forecast as operating KPIs, but they must not mechanically determine Q2 revenue under this lag model. No Q3/Q4 2027 or 2028 input is necessary for the four-quarter revenue/guide sequence.

## What the existing implementation actually covers

L4's detailed revenue adapter produces Q3 2026, Q4 2026 and Q1 2027. Its downstream financial builder has `YEARS=[2026,2027,2028]`; Q2 2027 onward falls back to inherited revenue growth when a detailed forecast row is absent. The frozen reference Q2 2027 revenue is approximately $4,048.79m, using inherited 12.217009% growth, and has no guide output. That is not an explicit Q2 guide forecast.

The model also contains Q1 2027 GBV of approximately $32,424.36m and booked units of 170.01m. These are inherited assumptions, not a newly validated Q1 booking build. Explicit Q1 revenue coverage does not validate Q1 bookings because Q1 revenue depends on earlier GBV.

Evidence: `analysis/src/forecast_methods/lane4_revenue_v2/README.md`, `lane4_revenue_v2/adapter.py`, `lane4_model_v2/run.py`, `data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1/forecast.csv`, and `lane4_model_v2/snapshot_v2/model_input.json`.

## The bounded implementation package

1. Create a new four-quarter integration/export version. Its downstream outputs must not depend on H2 2027 or 2028 assumptions; merely hiding those columns is insufficient.
2. Make the Q1 2027 nights/ADR/GBV assumptions explicit and internally consistent. Feed Q1 2027 and Q4 2026 GBV into the existing Q2 seasonal conversion policy and a documented guide-cushion assumption. Missing inputs must produce a visible unavailable result or an error, never an inherited-growth fallback labeled as a completed guide forecast.
3. Connect the same four-quarter operating cases to the existing bottom-up quarterly cost build. Reuse the margin branch's quarterly schedules and reconcile their source versions. Do not require another annual financial model.
4. Freeze vendor, target, timestamp and comparison definition for each expectations row. Retain observed revenue consensus separately from direct or explicitly implied guide expectations.
5. Verify lag timing, units/ADR/GBV identities, overlap of RNPL assumptions, quarterly cost/EBITDA tie-outs and the selected-case recalculation. Use the existing research verdicts; implementing Q2 arithmetic does not validate the input forecast.

## Submission design

The main view has four forecast columns, with historical comparisons alongside only where useful. It shows booked-unit growth, ADR, GBV, revenue, predicted guide, margin outlook, matching expectations, and scenario/falsifier notes. Supporting views contain the operating evidence, conversion/cushion bridge, quarterly costs, event scenarios, and source/check details.

Prioritize three visual questions: what changes across these four quarters; how bookings convert into each forthcoming guide; and what weaker/in-line/stronger announcements mean for the event thesis. Price outcomes remain conditional scenarios unless separately supported. Do not make a terminal valuation or a 2028 EBITDA multiple the explanation for the quarterly trade.

## Remove from the active work plan

Q3/Q4 2027 forecasts; FY2028; terminal DCF assumptions; full-year FY2027 target adoption; September-versus-December 2027 value reconciliation. Existing artifacts are preserved as prior research and need no further work for this scope.

## Completion record and verification

4Q-SCOPE and 4Q-DEPENDENCY are complete as a scope/dependency audit. Parent read the current revenue CSVs and source code; the independent reviewer checked the frozen model JSON and confirmed the Q2 fallback. No new forecasts, refits, tests, registrations, workbook changes or trades were performed; new estimated parameter count is zero. This note records the implementation contract, not completion of the future four-quarter workbook.

## RESUME

Build the submission only through Q2 2027. Reuse the completed Q3/Q4/Q1 conversion code, make Q1 booking assumptions explicit, add an actual Q2 revenue/guide output through the retained lag equation, and connect the existing quarterly cost build. Freeze and review the four-quarter Excel and event charts with matching expectations and honest scenario labels. Do not reopen 2028 or full-year 2027 valuation work as a prerequisite.
