# Canadian Border Crossings Analysis

**Author**: Alex Bogden | [LinkedIn](https://www.linkedin.com/in/alex-bogden/)

SQL and Python analysis of Canadian land border crossing trends from 2024 to 2026, using publicly available data from the Bureau of Transportation Statistics (BTS), plus survey data from the Border Policy Research Institute at Western Washington University.

## Project Background

Following the introduction of US tariffs on Canadian imports in early 2025 and the subsequent Canadian travel boycott, Canadian land border crossings into the US declined significantly. This project uses SQL to quantify that decline, identify when it started, which travel modes were most affected, and which states and ports of entry saw the largest drops. It also incorporates individual-level survey data to explore why the decline happened, not just where.

## Data Sources

- **Source**: Bureau of Transportation Statistics (BTS) Border Crossing Entry Data
- **URL**: https://data.bts.gov/stories/s/Border-Crossing-Entry-Data/jswi-2e7b/
- **Coverage**: Monthly inbound crossings at US ports of entry, 1996 to present
- **Note**: This dataset captures inbound crossings into the US only. Outbound data is not collected.

- **Source**: Individual-level passenger vehicle intercept survey, Whatcom County border crossings
- **Provided by**: Laurie Trautman, Director, Border Policy Research Institute (BPRI), Western Washington University, in partnership with the International Mobility and Trade Corridor (IMTC) Program
- **Coverage**: Four survey waves (Summer 2018, Winter 2019, Summer 2025, Winter 2026), 31,208 responses

- **Source**: National Travel and Tourism Office (NTTO), International Air Passenger Monitor (I-92/APIS)
- **URL**: https://www.trade.gov/data-visualization/apisi-92-monitor
- **Coverage**: Monthly Canadian air passenger arrivals and departures at US ports, January 2019 through July 2026

## Tools

- PostgreSQL
- DBeaver
- Python (psycopg2, pandas, numpy, matplotlib, python-dotenv)

## Analytical Framework

This project works through a structured set of questions, moving from baseline trends to geographic breakdowns to event correlation and confounding factors. The BTS-based questions (Q1-Q13) cover year-over-year totals, measure type breakdowns, state and port-level geography, correlation with political events, exchange rate effects, port-level recovery patterns, and data quality. Survey-based queries (S1, S2) cover trip purpose and crossing frequency, season-matched across comparable waves. Air travel queries (A1, A2), drawn from a separate NTTO-sourced table, cover year-over-year air arrivals and the monthly gap between arrivals and departures. See `border_crossings_analysis.sql` for the full annotated query set.

## Key Findings

- Total Canadian land border crossings dropped 20% from 2024 to 2025 (69M to 55M)
- No early signal in late 2024 -- the decline began after tariffs were signed in February 2025
- The sharpest single-month drops occurred in July and August 2025, coinciding with the announcement and implementation of a 35% tariff
- Road travel accounted for nearly all of the decline; pedestrian and train passenger crossings actually increased year over year
- Vermont (-28.2%) and North Dakota (-26.6%) saw the steepest state-level percentage drops
- New York (-4.64M) and Washington (-3.93M) saw the largest raw declines
- Small, routine crossings like the Walpole-Algonac Ferry in Michigan (-42.4%) were hit harder on a percentage basis than high-volume tourist corridors like Niagara Falls
- Crossings dropped at each tariff escalation, with 2026 tracking below even the depressed 2025 levels -- 14 consecutive months of year-over-year decline confirmed through March 2026
- April 2026 turned positive year-over-year (+10.2% vs April 2025), breaking the streak -- though it remains 18.1% below April 2024 and below every pre-COVID April on record
- CAD/USD exchange rate movements appear to follow crossing declines rather than lead them, pointing toward policy events as the primary driver
- Of 32 qualifying ports, only 6 showed positive year-over-year change in January-April 2026 vs 2025 -- and none of those gains appear at the state level
- Season-matched trip purpose comparisons (Summer 2018 vs. 2025, Winter 2019 vs. 2026) show gas purchases and shopping trips declining consistently across both pairs, while family visits grew in both, pointing toward necessity-driven travel replacing discretionary travel
- Crossing frequency tier analysis shows the "Frequent" traveler tier (13-52x/year) shrinking in both season-matched pairs, while "Regular" and "Very Frequent" tiers grew
- Canadian air arrivals into the US show the same pattern as land crossings: every month from 2024 to 2025 declined, with the year-over-year gap narrowing through 2026 and briefly turning positive in June and July
- The monthly gap between Canadian air arrivals and departures, a proxy for stay length, holds the same seasonal shape every year back to 2019 (2020-2021 excluded as a COVID-driven anomaly) -- the recent decline shows up as fewer travelers, not shorter or longer stays

## LinkedIn Posts

This analysis is being shared progressively on LinkedIn as each section is completed.

- [Post 1: Year-over-year totals](https://www.linkedin.com/feed/update/urn:li:activity:7460829029156151296/)
- [Post 2: Sharpest monthly drops and travel mode breakdown](https://www.linkedin.com/feed/update/urn:li:activity:7462951984451579904/)
- [Post 3: State and port-level geography](https://www.linkedin.com/feed/update/urn:li:activity:7463675567435935745/)
- [Post 4: Monthly trend correlation with political events](https://www.linkedin.com/feed/update/urn:li:activity:7465524856168595456/)
- [Post 5: First year-over-year gain and what it does and doesn't mean](https://www.linkedin.com/feed/update/urn:li:activity:7468767226439897088/)
- [Post 6: CAD/USD exchange rate as a competing explanation](https://www.linkedin.com/feed/update/urn:li:activity:7470533020140150785/)
- [Post 7: Port-level recovery -- how narrow, and why](https://www.linkedin.com/feed/update/urn:li:activity:7473396620609474560/)
- [Post 8: Trip purpose, season-matched](https://www.linkedin.com/feed/update/urn:li:activity:7480332046008041474/)
- [Post 9: Crossing frequency tiers, season-matched](https://www.linkedin.com/feed/update/urn:li:activity:7486082199545565185/)
- [Post 10: Air arrivals, year-over-year](https://www.linkedin.com/feed/update/urn:li:activity:7496311203145633792/)
- [Post 11: Air arrivals vs. departures, the monthly gap](https://www.linkedin.com/feed/update/urn:li:activity:7498466626816663553/)

## Status

Completed: Baseline trends, travel mode breakdown, state and port-level geography, event correlation, exchange rate analysis, port-level recovery, passenger vehicle survey analysis (trip purpose, crossing frequency), and air travel analysis (year-over-year arrivals, arrival/departure gap)

Upcoming: Data quality review, traveler sentiment analysis (self-reported travel frequency and experience change)