# Adjusted EBITDA margin guidance added to Theo's guidance dataset

- **Source:** Airbnb shareholder letters Q4 2020 to Q2 2026, "Outlook" sections (8-K Ex. 99.1, S23); appended to `theos-past-research/research/guidance/data/normalized/guidance_items.csv` and `source_excerpts.csv` by `analysis/src/abnb_margin_guidance_items.py`.
- **Date:** 2026-09-05
- **Author:** Krishang Surapaneni (compiled with Claude Code). Plan-of-attack branch 6.

## What was added

44 guidance items with metric code `adj_ebitda_margin`, one per event for the next quarter and, from Q4 2020 onward where stated, one for the full year (21 full-year items, 23 next-quarter or forward-quarter items), each with a pinpoint excerpt row quoting the letter sentence. Theo's validator (`abnb_guidance.storage.validate_dataset`) reports no findings on the new rows; the 93 pre-existing findings are all in his `driver_observations` table and are untouched.

| measure_type | Meaning | Value field | Example |
|---|---|---|---|
| absolute_floor | "at least X%" or "exceeds last year's X%" | value_low | FY2024 at least 35% (Q4 2023 letter) |
| absolute_point | "approximately X%", "stable", "in line with" | value_mid | FY2024 approximately 35.5% (Q3 2024 letter) |
| absolute_ceiling | "down slightly" or "lower than" a stated prior period | value_high | Q3 2026 below 50.1% (Q2 2026 letter) |
| qualitative_direction | direction only, no usable bound | none | Q1 2021 "lowest during Q1" |

Where the bound comes from the prior-period margin rather than the letter, `is_company_stated` is False, `comparator_period` names the period and `derivation_formula` states the arithmetic. Full-year guides are filed with `target_period` equal to Q4 of the fiscal year because Theo's `FiscalPeriod` type only accepts quarters; this is logged as research issue `ABNB-ISSUE-FY-PERIOD-ENCODING`.

## What it enables

- Pairing each margin guide with the reported margin (the margin note's section 5 table) gives the floor-beat series: every full-year floor since 2023 was beaten by 60 to 180 bps, and every next-quarter direction was met.
- Theo's reaction-function test can now use the margin guide as a second explanatory variable alongside the revenue range; the margin note argues the stock trades on margin and nights, not revenue.
- The 5 November prediction card can be scored against structured fields rather than prose.

## Not done

- `guidance_events.csv` timestamps still use the webcast start; the plan asked for SEC 8-K acceptance times, which need the EDGAR index pages per accession (the accession list is in `analysis/src/abnb_exsbc_stack.py` on branch `krish/margin-drivers`).
- Reported Adjusted EBITDA margin actuals are not added to `quarterly_actuals.csv`; they live in `data/processed/abnb_quarterly_costlines.csv` on the margin branch.
