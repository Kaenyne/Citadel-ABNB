# M3: Guidance-policy model for margin: forecasts the guide, and the actual given the guide

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M3_guide_policy_margin`. Method name: `guide-policy-margin`.
Inputs: WS05 (`05_guide_language_pattern.csv`, `05_statements.csv`, `05_reliability_by_line.csv`), `overnight/02_guidance_ledger.csv`,
`overnight/31a_*.csv`, the revenue guidance-policy package `analysis/src/forecast_methods/guidance_policy_v2/` and its note
`docs/revenue-forecast-strategy/05_backtests/guidance-policy.md` (same idea applied to revenue; reuse the structure, not the numbers).

## Three objects

1. `actual_given_guide`: at each vintage date where an FY margin guide (floor/point) is in force, the forecast of the FY margin and of the
   remaining quarters is guide + cushion, where the cushion is the PIT recency-weighted history of (actual - guide) for the same guide type
   (floor in Feb; reaffirmed floor in May/Aug; point in Nov), and the quarterly allocation uses the 2023-25 seasonal shares (from WS02) with the
   YTD actuals subtracted. Register FY-level results in the annual CSV and quarterly h=0/1/2 rows in the registry.
2. `guide_forecast`: the forecast of the NEXT margin guide sentence: for 5 Nov 2026, the probability it is a floor / point / range, its level
   (distribution), and the first FY27 statement (probability management gives a number, and what). Backtest: at each November since 2021,
   predict the sentence from YTD delivery vs the floor, the Q4 revenue guide, and the language pattern; score hit rate on type and MAE on level (n 5).
   Also the February FY guide: predict its level from the prior-year actual and the reinvestment algorithm statements; MAE (n 5).
3. `q4_implied`: at each November vintage, Q4 margin implied by the FY guide and 9M actuals, vs Q4 actual (n 5) and vs consensus Q4 (WS03).

## Tests (pre-register)

Object 1 beats `seasonal_naive` and `street` on FY margin MAE (n 5 FY guides 2021-25; small, say so) and on quarterly h=0 rows in W1/W2.
Object 2: type hit rate >= 4/5 and level MAE < 50bp are the pass lines; report whatever comes out.

## LIVE / for the 5 Nov card

The full 5 Nov margin sentence forecast (type, level distribution, FY27 first look), FY26 margin distribution, 4Q26 margin, and the
implied EBITDA $ vs consensus. State the cushion history table (n, mean, min, max, by guide type) in the note.
