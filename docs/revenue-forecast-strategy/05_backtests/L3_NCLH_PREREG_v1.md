# L3 NCLH transferability preregistration v1

Saved 2026-09-13 before data extraction or model execution. Owner: nclh subagent, branch codex/lane3-full. Claim: WORKBOARD_L3_v1.md. No ABNB registry entries.

## Decision and immutable hurdles

Test whether publicly disclosed advance ticket sales (ATS), a deposit stock, support the claimed portable seasonal revenue kernel. Primary target is NCLH consolidated passenger ticket revenue; total revenue is a separately labelled secondary target. Onboard revenue and capacity/occupancy/net yield are diagnostic comparators, never silently substituted for ticket revenue. The instrument is a stock containing overlapping future voyages, not booked-quarter flow, so fitted lag weights are predictive weights, not measured recognition probabilities.

The original conjunctive pass line is unchanged: every season's 2023–2025 lambda range must be strictly below 0.5 percentage points; PIT RMSE divided by seasonal-naive RMSE must be strictly below 0.6 in BOTH W1 (2023Q1 onward) and W2 (2024Q1 onward), through the latest available target no later than 2026Q2. If metric-matched historical guidance and timestamped consensus exist, guide-surprise sign hit-rate must be at least 65%; missing consensus blocks only that comparison. Negative tests remain published.

## Information and targets

Public NCLH issuer quarterly earnings releases/filings, 2015–2026Q2. Extract the current period financial tables from each ORIGINAL quarter's release, not the later comparative column; retain publication date/time precision, retrieval timestamp, source URL and hash. A publication date without a clock time is conservatively treated as available at 23:59:59 America/New_York on that date and labelled date-only. Historical numerical revisions from later releases never replace original targets. If SEC facts are needed, require original accession/date and record first known value, not latest value. Q4 flows can be direct quarterly release figures or annual-minus-nine-months with both source vintages recorded. Missing data create explicit exclusions.

At the prior quarter's earnings-release vintage, forecast target q using known ATS q−1, q−2, q−3 only. Never use ATS q, even in fitting. Historical training target values and lagged ATS must have been published by that vintage. Calendar target q and quarter ends are separately represented; source availability, not period end, governs knowledge.

## Fixed modelling procedure

Drop target years 2020–2021 and any training row whose ATS lags fall in 2020–2021; 2022 is flagged and INCLUDED in the primary reopening-sensitive specification when lag availability permits. Report a sensitivity also excluding 2022 target years. Start estimation at 2015, minimum eight eligible observations and two per season; if insufficient, report unavailable instead of weakening the threshold. Pool all eligible training observations using expanding windows at every forecast vintage.

For each target metric and expanding fold fit nonnegative lag weights phi1, phi2, phi3 summing to one. Deterministic 0.1-simplex grid (66 candidates), objective training mean squared proportional error. For each candidate and season fit lambda_s = mean(revenue/weighted ATS); choose lowest objective then lexicographic weight order on ties. Six independent fitted coefficients (two weights plus four seasonal lambdas); the grid is a fixed approximation, not an additional post-result search. A fixed 2/3,1/3,0 diagnostic is reported without retuning.

Baselines on identical available folds: seasonal naive R(q−4); seasonal naive with most recently known YoY growth R(q−4)×R(q−1)/R(q−5); AR(1) levels with intercept fit to eligible contiguous historical pairs; trailing-four mean. Do not pair across COVID gaps. Guides × (1 + trailing-eight cushion) are evaluated only when a prior-date guide targets the identical GAAP revenue metric and period; net yield, adjusted EPS, net cruise costs and EBITDA do not qualify. Consensus and guide tests require matched definitions, currencies and fiscal quarters.

Stability is a labelled full-sample diagnostic: freeze weights estimated using training information available before 2023Q1, then compute realized lambda by season over 2023–2025 from original targets/lagged ATS. This prevents fitting the stability statistic's weights on the period being scored. Report all four seasonal ranges and counts; incomplete three-year seasons cannot pass. Also plot the repository's ABNB kernel seasonal levels/ranges for context only, explicitly separate stocks/flows and scale.

## Outputs, checks and status

Reproducible offline runner plus optional public fetch; source and input manifests; original-vintage numerical panel; fold predictions/coefficients/exclusions; score and stability tables; matched-guidance availability inventory; figure; L4 rows with quarter, metric, scenario, value/bounds, units, information_date, evidence_status, source_reference and replacement_vs_incremental treatment. L4 receives evidence about transferability, no ABNB forecast adjustment.

Tests: unavailable target-quarter ATS, quarter continuity, no future publication timestamps, source date precision, target metric identity, COVID exclusions, simplex constraints, missing/zero denominators, fail-line strictness, deterministic offline reconstruction. Runner exits 0 for a research FAIL; malformed inputs fail loudly.

## RESUME

Fetch/extract public issuer releases, preserve first-publication observations, then execute this unchanged protocol. Record coverage gaps and metric mismatches. Any repair discovered after execution must be documented in a new audit note; do not rewrite this preregistration.
