# Airbnb Guidance Intelligence Research System

Date: 2026-09-02
Status: Approved design, awaiting written-spec review
Issuer: Airbnb, Inc. (NASDAQ: ABNB)

## 1. Objective

Build a permanent, project-scoped Codex agent and an auditable quarterly research system that evaluates:

> What information plausibly available to Airbnb management when guidance was set best explains the guidance level, range, tone, and apparent conservatism?

The system must distinguish management's information set from the public information set, preserve point-in-time provenance, test candidate drivers against seasonal and consensus baselines, and report contradictory and negative evidence alongside supporting evidence.

The research is intended to support institutional analysis, not to assert access to management's private forecasting model or prove causal relationships from a small observational sample.

## 2. Scope

The initial historical panel covers every usable post-IPO quarterly guidance event from Airbnb's first public-company earnings cycle through the latest event available at the project's declared research cutoff. The cutoff is recorded in every generated report and dataset release.

The system covers:

- The quarter whose results Airbnb reports at an earnings event.
- The next fiscal quarter for which management issues guidance.
- Other quarterly or annual metrics management guides at the same event.
- Same-event clarifications and later formal revisions, stored separately from the initial guide.
- Event-window market returns as context, not as evidence of management's internal weighting.

An absent guide, unavailable consensus snapshot, or unavailable driver is recorded as missing with a reason. It is never treated as zero.

## 3. Recommended Architecture

The canonical research layer is normalized and audit-first. Source metadata, excerpts, extracted facts, derived variables, and model outputs remain separate. A wide, one-row-per-initial-guidance-event panel is generated from the normalized tables.

Canonical tables are stored in open, machine-readable formats. CSV is the human-review interchange format; Parquet is the typed analytical format when the required local dependency is available. Schemas and validation rules are versioned alongside the data. Any XLSX file is a generated review or data-request artifact, not the canonical database.

The system has five layers:

1. Source registry and lawful document collection.
2. Short, pinpointed evidence extraction.
3. Normalized financial, guidance, consensus, driver, and return observations.
4. Leakage-controlled modeling views and tests.
5. Evidence rankings, unresolved questions, and reproducible reports.

## 4. Permanent Agent Contract

The project-scoped role file is:

`.codex/agents/abnb_guidance_intelligence.toml`

The role is paired with `research/abnb_guidance/AGENT_PLAYBOOK.md`, which defines its user-visible operating modes, research sequence, information-set gates, source controls, deterministic commands, and output contract. The role is the primary research product; the Python package is its reproducible calculation and validation layer.

The role's durable instructions require the agent to:

1. State the research cutoff and target guidance events before collection or analysis.
2. Prefer Airbnb Investor Relations materials and SEC filings; use other sources only when their access and reuse are lawful and documented.
3. Preserve source URL, canonical URL, publisher, document date, exact publication or SEC acceptance timestamp when available, retrieval timestamp, collection method, local path, content hash, and rights/access note.
4. Store only narrowly relevant exact excerpts from third-party transcripts and never reproduce or persist a complete copyrighted transcript unless the user supplies a licensed copy and explicitly authorizes its use.
5. Ask before paid collection or Bloomberg extraction and, when Bloomberg is needed, first produce an exact XLSX field request with tickers, fields, dates, periodicity, currency, adjustment, and point-in-time requirements.
6. Separate sourced values from derived values, retain formulas and units, and never silently reconcile contradictory sources.
7. Apply the information-clock policy in Section 7 before any feature is admitted to a model.
8. Use expanding-window walk-forward evaluation as the primary test and label any leave-one-quarter-out analysis as a non-real-time sensitivity.
9. Evaluate each candidate driver individually before testing small, economically coherent groups.
10. Report coverage, missingness, measurement quality, sign stability, prediction-error change, contradictory evidence, and null findings.
11. Describe results as associations or predictive evidence unless a separate causal design supports stronger language.
12. Leave a reproducible audit trail for every material number and conclusion.

The TOML remains lean: a discriminating description and durable `developer_instructions` are required. Model choice and mutable runtime settings are inherited unless a supported local configuration field is validated and a project-specific override is justified.

## 5. Source Policy

### 5.1 Source hierarchy

1. Airbnb Investor Relations shareholder letters, earnings releases, webcasts, and company-hosted transcripts or prepared remarks.
2. SEC EDGAR filings and exhibits, especially Forms 8-K, 10-Q, and 10-K.
3. Official government or first-party economic, regulatory, calendar, and market-data sources.
4. Lawfully accessible third-party news, consensus references, and transcripts, with source limitations recorded.
5. Paid or licensed sources only after explicit user approval.

When an Airbnb document and an SEC-filed copy disagree, both versions are preserved. The filed copy is normally the authoritative archival version, but differences in timing or later correction remain visible.

### 5.2 Transcript handling

For each transcript source, store metadata, access date, citation location, and short evidence excerpts only. Do not store a complete third-party transcript. Excerpts should be limited to the minimum language needed to substantiate a claim and should carry speaker and timestamp or section information when available.

### 5.3 Source integrity

Official documents that may lawfully be downloaded are preserved byte-for-byte with SHA-256 hashes. Dynamic pages are represented by a source record and, when lawful and technically feasible, a timestamped capture of the relevant passage. Every capture records the retrieval method and any known risk that the page may have changed after publication.

## 6. Event and Period Semantics

`reported_period` is the fiscal quarter whose actual results are announced at the event. `target_period` is the future fiscal quarter covered by the guidance item. `guidance_event_id` identifies a publication event rather than a fiscal quarter alone.

The initial numeric guide is anchored to the earliest authoritative public release timestamp. Prepared remarks or call Q&A later that day may explain or clarify the guide but do not change the initial timestamp. A genuine revision receives a new event record linked to the initial event.

For market returns, `reaction_session` is:

- The same regular trading session when the release is before market open.
- The next regular trading session when the release is after market close.
- Explicitly adjudicated when the release is intraday or the timestamp is uncertain.

## 7. Information-Clock and Leakage Policy

Each observation receives both an economic availability assessment and, where applicable, a public timestamp.

Availability classes:

1. `public_prior`: publicly available strictly before the initial guidance timestamp.
2. `contemporaneous_management_known`: first disclosed with the guide but plausibly known to management when the guide was set, such as the reported quarter's operating results.
3. `management_private_proxy`: an internal condition represented only by contemporaneous management commentary, such as forward bookings or cancellation behavior.
4. `post_event_ineligible`: published or realized after the guidance timestamp and prohibited as a predictor.

Two modeling views are maintained:

- `management_information_view` is primary and may use classes 1 and 2. Class 3 may be analyzed in a separately labeled proxy specification when the observation can be coded without using the numerical guide or eventual outcome.
- `public_prior_view` is the robustness case and uses class 1 only.

Management explanations published with or after the numerical guide are attribution evidence. They are not predictive inputs for the initial numerical guide. Eventual actuals, subsequent commentary, revised macro data, and market reactions are outcomes or diagnostics only.

Every external series records its vintage or first-publication date when revisions are possible. A current revised historical value may not substitute for the vintage available at the guidance date without an explicit leakage warning and sensitivity analysis.

## 8. Normalized Data Model

### 8.1 `guidance_events`

Grain: one initial guidance release or formal revision.

Required fields:

- `guidance_event_id`
- `issuer_id`
- `reported_period`
- `event_type`
- `published_at_utc`
- `published_at_precision`
- `release_timing`
- `research_cutoff_at_utc`
- `initial_event_id`
- `is_initial_guide`
- `primary_document_id`
- `event_notes`

### 8.2 `guidance_items`

Grain: one guided metric, horizon, and basis per event.

Required fields:

- `guidance_item_id`
- `guidance_event_id`
- `target_period`
- `metric_code`
- `measure_type`
- `value_low`
- `value_high`
- `value_mid`
- `unit`
- `currency`
- `accounting_basis`
- `is_company_stated`
- `derivation_formula`
- `comparator_period`
- `source_excerpt_id`
- `extraction_confidence`

Revenue, revenue growth, Adjusted EBITDA or margin, nights, GBV, take rate, stock-based compensation, and other guided metrics use the same row structure rather than separate ad hoc columns.

### 8.3 `quarterly_actuals`

Grain: one reported metric, fiscal period, basis, and scope.

Required fields:

- `actual_observation_id`
- `fiscal_period`
- `metric_code`
- `scope_code`
- `value`
- `unit`
- `currency`
- `accounting_basis`
- `yoy_growth_reported`
- `yoy_growth_constant_currency`
- `is_company_stated`
- `derivation_formula`
- `public_available_at_utc`
- `source_excerpt_id`

### 8.4 `consensus_snapshots`

Grain: one source, target period, metric, statistic, and as-of snapshot.

Required fields:

- `consensus_snapshot_id`
- `guidance_event_id`
- `target_period`
- `metric_code`
- `statistic_type`
- `value`
- `unit`
- `currency`
- `analyst_count`
- `snapshot_at_utc`
- `snapshot_precision`
- `snapshot_age_hours`
- `is_strictly_pre_event`
- `point_in_time_verified`
- `source_name`
- `license_or_access_basis`
- `source_document_id`
- `quality_grade`

The preferred consensus is the nearest verified snapshot strictly before guidance. A date-only news reference is retained with reduced precision and a lower quality grade rather than treated as an intraday snapshot.

### 8.5 `driver_observations`

Grain: one driver, event, measurement window, and scope.

Required fields:

- `driver_observation_id`
- `guidance_event_id`
- `driver_family`
- `driver_code`
- `value_numeric`
- `value_category`
- `unit`
- `period_start`
- `period_end`
- `scope_code`
- `direction_interpretation`
- `availability_class`
- `known_to_management_by_utc`
- `public_available_at_utc`
- `is_derived`
- `derivation_formula`
- `source_excerpt_id`
- `quality_grade`
- `leakage_risk`
- `leakage_notes`

Initial driver families are demand volume, booking economics, mix, booking behavior, supply, commercial activity, external conditions, and calendar effects.

### 8.6 `source_documents`

Grain: one source document or captured version.

Required fields:

- `document_id`
- `document_type`
- `title`
- `publisher`
- `source_url`
- `canonical_url`
- `fiscal_period`
- `document_date`
- `published_at_utc`
- `sec_accession_number`
- `retrieved_at_utc`
- `capture_method`
- `mime_type`
- `local_path`
- `sha256`
- `rights_or_access_note`
- `version_status`
- `supersedes_document_id`

### 8.7 `source_excerpts`

Grain: one minimal exact evidence passage.

Required fields:

- `source_excerpt_id`
- `document_id`
- `page_number`
- `section_heading`
- `speaker`
- `timecode`
- `source_anchor`
- `exact_excerpt`
- `excerpt_word_count`
- `context_paraphrase`
- `copyright_handling`
- `extraction_method`
- `verified_against_source`

### 8.8 `evidence_claims`

Grain: one management claim or relevant negative-evidence claim.

Required fields:

- `evidence_claim_id`
- `guidance_event_id`
- `source_excerpt_id`
- `driver_family`
- `driver_code`
- `claim_type`
- `evidence_stance`
- `direction`
- `attribution_strength`
- `time_horizon`
- `scope_code`
- `quantified_value`
- `quantified_unit`
- `coder_confidence`
- `contradicts_claim_id`
- `adjudication_note`

`evidence_stance` supports `supporting`, `contradictory`, `mixed`, `neutral`, and `negative_evidence`. `attribution_strength` distinguishes an asserted driver, contributor, risk, contextual correlation, and no attribution.

### 8.9 `market_returns`

Grain: one guidance event, instrument, benchmark, and return window.

Required fields:

- `market_return_id`
- `guidance_event_id`
- `instrument`
- `benchmark`
- `reaction_session_date`
- `window_sessions`
- `price_adjustment`
- `raw_total_return`
- `benchmark_total_return`
- `excess_return`
- `price_source`
- `source_as_of_utc`
- `quality_grade`

Default windows are 1, 5, 20, and 60 regular trading sessions. QQQ is the primary benchmark and SPY is a robustness benchmark. Twenty- and sixty-session results are labeled as materially confounded.

### 8.10 `model_results`

Grain: one target, specification, and held-out event.

Required fields:

- `model_result_id`
- `target_code`
- `information_view`
- `baseline_code`
- `specification_code`
- `train_start_event_id`
- `train_end_event_id`
- `test_event_id`
- `feature_codes`
- `prediction`
- `actual_target_value`
- `absolute_error`
- `squared_error`
- `baseline_absolute_error`
- `error_improvement`
- `fit_warnings`
- `random_seed`
- `code_version`
- `created_at_utc`

### 8.11 `research_issues`

Grain: one data, methodology, rights, contradiction, or unresolved research issue.

Required fields:

- `research_issue_id`
- `issue_type`
- `severity`
- `guidance_event_id`
- `related_record_type`
- `related_record_id`
- `description`
- `proposed_resolution`
- `status`
- `requires_user_approval`
- `created_at_utc`
- `resolved_at_utc`

## 9. Target Definitions

The primary targets are:

- Revenue guidance midpoint in USD.
- Guided revenue YoY-growth midpoint.
- Normalized range width: `(high - low) / midpoint`.
- Guidance surprise: `(guidance midpoint - pre-guidance consensus) / consensus`.
- Ex-ante conservatism: `(consensus - guidance midpoint) / consensus`, so a positive number is more conservative than consensus.
- Baseline-relative conservatism: `(point-in-time baseline - guidance midpoint) / baseline`.
- Realized cushion: `(eventual reported revenue - prior guidance midpoint) / prior guidance midpoint`.
- Range outcome: below, within, or above the prior range, plus distance from each bound.

Realized cushion and range outcome are ex-post calibration outcomes. They are never predictors of the guide that preceded them and are not interpreted as pure managerial conservatism because post-guidance shocks can affect actual revenue.

Forward-looking tone is coded on a five-point ordinal scale:

- `-2`: materially cautious
- `-1`: cautious
- `0`: balanced or mixed
- `1`: constructive
- `2`: materially confident

Separate fields retain demand direction, uncertainty emphasis, and commitment strength. Tone coding is performed without viewing eventual actuals or stock returns. Two independent coding passes are compared; disagreements and adjudication rationales are logged.

## 10. Candidate Driver Taxonomy

### Demand volume

- Nights and Seats Booked level and growth.
- Recent or forward booking momentum.
- Demand volatility and conversion indicators.

### Booking economics

- GBV level and growth.
- ADR level and growth.
- Reported and derived take rate.
- Fee-structure or cross-currency changes.

### Mix

- Regional growth and exposure.
- Cross-border and domestic/international mix.
- Urban, non-urban, and length-of-stay mix when disclosed consistently.

### Booking behavior

- Lead times.
- Cancellation behavior.
- Backlog or bookings already on the books.

### Supply

- Active listings and supply growth.
- Availability, host growth, and listing quality.

### Commercial activity

- Sales and marketing expense, growth, and percent of revenue.
- Promotions, product launches, and investment cadence.

### External conditions

- FX and company-disclosed constant-currency impacts.
- Point-in-time macroeconomic series.
- Airfare or travel-cost indicators when lawfully and consistently available.
- Regulatory changes with effective dates and exposed geographies.

### Calendar effects

- Fiscal-quarter seasonality.
- Easter and other material holiday shifts.
- Leap years and explicitly identified one-off events.

Calendar and event features are defined before inspecting their apparent model contribution to reduce cherry-picking.

## 11. Modeling and Evaluation

The primary evaluation is expanding-window walk-forward testing. A held-out quarter may only be predicted using observations and trained parameters available before that quarter's guidance timestamp. The minimum training window and each model's eligible-event count are reported.

Primary baselines:

1. Seasonal/history-only baseline.
2. Nearest verified pre-guidance consensus.
3. Combined seasonal-plus-consensus baseline.

Range-width and tone models use trailing and seasonal baselines appropriate to those targets. Candidate drivers enter one at a time first. Small grouped models are permitted only for predefined economically related features and use regularization or dimensionality limits appropriate to the sample size.

Primary revenue-level scoring uses walk-forward mean absolute error, root mean squared error, and out-of-sample error improvement versus the relevant baseline. Range models also report interval coverage and width. Tone models report ordinal absolute error and confusion patterns. Conservatism models report directional accuracy and magnitude error.

Leave-one-quarter-out results may be provided as a stability sensitivity, but must be labeled as using future observations in some training folds and therefore not representative of a real-time forecast.

Coefficient estimates, confidence intervals, and resampling statistics are diagnostic. They do not override weak coverage, unstable signs, or poor out-of-sample performance. No causal claim is made from these models.

## 12. Driver Ranking

The ranked assessment does not rely on a hidden weighted score. Each driver displays:

- Walk-forward error improvement versus seasonal and consensus baselines.
- Eligible-quarter count and missingness.
- Direction and rank stability.
- Explicit management-attribution frequency and strength.
- Incremental contribution after closely related drivers.
- Contradictory, mixed, and negative evidence.
- Measurement quality and leakage risk.

Drivers are assigned transparent evidence tiers: `strong`, `moderate`, `weak`, `contradicted`, or `data_limited`. The report explains why each tier was assigned and shows the component evidence so a reader can disagree with the synthesis.

## 13. Bloomberg Escalation

Public and first-party collection is attempted first. If exact point-in-time consensus or adjusted historical pricing cannot be obtained with sufficient precision, the system creates an XLSX request before any Bloomberg work begins.

The request must specify:

- Security and identifier.
- Requested Bloomberg field names or field descriptions.
- Target fiscal periods and event timestamps.
- Required estimate statistic and contributor count.
- Point-in-time snapshot convention, including strict pre-release timing.
- Currency and units.
- Price adjustment and trading-calendar convention.
- Desired output columns and worksheet structure.
- Known public-source gap that the request resolves.

The user must approve that request before extraction.

## 14. Planned Repository Layout

```text
.codex/agents/abnb_guidance_intelligence.toml
research/abnb_guidance/
|-- schemas/
|-- data/
|   |-- source_documents/
|   `-- normalized/
|-- evidence/
|-- analysis/
|-- reports/
|-- requests/
`-- tests/
```

The repository is not currently a Git repository. Implementation must not initialize Git unless the user separately requests it.

## 15. Validation and Acceptance Criteria

The implementation is acceptable when:

1. The local Codex installation recognizes the agent role file without configuration errors.
2. Schema validation rejects missing primary keys, invalid enums, malformed periods, inconsistent range bounds, and derived values without formulas.
3. Every populated guidance, consensus, driver, actual, and management-evidence record links to a source document or explicit derivation.
4. Automated temporal checks reject post-event predictors and unverified consensus snapshots from the strict public-prior view.
5. Duplicate documents and records are detected using stable identifiers and hashes.
6. The wide guidance panel is reproducibly generated from normalized tables.
7. Model tests demonstrate strict train/test time ordering.
8. Copyright checks prevent full third-party transcript persistence and flag excessive excerpt accumulation.
9. The final ranking includes null, contradictory, and negative evidence.
10. The final report lists unresolved issues and any proposed Bloomberg request.
