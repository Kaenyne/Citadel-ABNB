# Web calls for R14 (risk-feb-print-up-day), 17 Sep 2026

WebSearch budget: 1 of 5 used for R14 (the batch's final 72-hour neutral recency check).

## WebSearch 1 — "Airbnb news past 3 days" (2026-09-17, ~08:00 UTC; the batch-level final 72-hour neutral recency check, per the skill's step 7e)
Results: CBS/Google/Bloomberg/Yahoo topic pages, Airbnb Newsroom, 2026 Summer Release page. Search-engine summary of the last three days: ~60,000 fake listings removed this year and 157,000 blocked; a $250 million "Housing Accelerator"; mixed analyst sentiment (Morgan Stanley EW $170 on 16 Sep, S04 capture); a World Cup story about hosts still waiting for bookings. Nothing on the 4Q26 print date, 1Q27 guidance, or the February event. No change to the number.

## Reused from S03 (same day)
S03 query 13 (WebSearch, 17 Sep): "Airbnb fourth quarter 2026 earnings date February 2027" — no 2027 date announced; the 4Q25 release was 12 Feb 2026 after the close; Q4 releases have been 25 Feb 2021, 15 Feb 2022, 14 Feb 2023, 13 Feb 2024, 13 Feb 2025, 12 Feb 2026, all after the close, so the expected resolving session is Friday 12 Feb 2027.

## Market cross-reference (no search cost)
Kalshi KXABNB / KXABNBA (03:10Z, 03:56Z) and Polymarket "airbnb" (03:10Z, 03:56Z): Q3-2026 nights strikes and September price-hit ladders only; nothing dated February 2027 or on the Q4 print reaction.

## Options (repo pulls, 16 Sep close)
`../../close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv`: 15 Jan 2027 ATM IV 37.21% (T 0.3315), 19 Mar 2027 38.02% (T 0.5041). The Feb-print event variance = Mar total variance − Jan total variance − background variance over the 0.173y between them: event sd 8.5% at 33.85% background (S01's least-squares background), 9.5% at 32.3% (Oct ATM), 11.2% at 29%, 6.8% at 36% (`datasets/r14_base_rates.json`).
