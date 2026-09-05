# Early-cohort Phase-A replay notes

Owner: `guidance_2020q4_2023q2`  
Cohort: issuing periods 2020Q4 through 2023Q2  
Completed: 2026-09-03T06:00:21Z

## Scope and controls

This is an event-by-event fixed-rule replay, not a fitted model. The replay used the compact transcript index, the frozen target panel, the preregistered H-001/H-002/H-003 definitions, and the lead-owned point-in-time feature panel. No full transcript was opened. SEC exhibits or the cited first-party release control the target; transcript context was not used as a feature.

The named baseline is the numeric revenue-guidance midpoint for the same guided fiscal quarter one year earlier. Eleven guidance events and three signals produced 33 audit rows. The first three targets are qualitative. The next four numeric targets have no numeric year-earlier baseline because the corresponding earlier targets are absent or qualitative. Therefore only four events can support a directional baseline comparison.

## Strict replay result

- H-001 Federal Reserve H.10: four strict-PIT comparable events, three hits and one miss. The hit events are 2022Q3, 2023Q1, and 2023Q2 issuances; 2022Q4 is a miss. The sample is descriptive only, and all four target changes versus the seasonal baseline are positive. This does not establish edge or statistical significance.
- H-002 ECB EUR/USD: zero strict-PIT eligible comparisons. The API response does not expose exact initial publication timestamps. Under the separately labeled, conservative 16:00 UTC same-day sensitivity convention, the same four target-comparable events produce three hits and one miss. That sensitivity result is not promoted into the strict replay.
- H-003 BLS lodging CPI: zero strict-PIT eligible comparisons. Historical release timestamps were not independently verified, so current API history was not backfilled into historical features.

H-002 and H-003 fail the preregistered minimum of six eligible events in this cohort. The early cohort alone also cannot satisfy H-001's overall threshold of at least 16 numeric targets and eight test folds; no fold construction or predictive fitting was attempted.

## Leakage and interpretation warning

The guidance statement itself and all post-cutoff information were excluded from features. Equality at the cutoff was ineligible. The H.10 releases used in the four strict comparisons precede each guidance cutoff. The 3/4 H.10 direction count must not be interpreted as incremental forecast value: it is a four-event descriptive audit against a baseline in which every observed target change is upward.
