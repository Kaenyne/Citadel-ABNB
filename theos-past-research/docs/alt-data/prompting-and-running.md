# Prompting and Running `abnb_alt_data`

Start a Codex task from this project and address the agent by its exact name,
`abnb_alt_data`. If a task was already open when the agent file was added, start
a fresh project task so Codex reloads `.codex/agents/abnb_alt_data.toml`.

Use one research stage per prompt. Give the agent a concrete target, allowed
sources, prediction cutoff, and required output. The recommended order is
source selection → target preparation → hypothesis registration → small-sample
collection audit → testing → synthesis.

The transcript Markdown is context for extracting the historical outcome. It
does not loosen the context policy: the agent reads the compact index first and
opens no more than three full calls in one step. A guidance-only Markdown note
must retain its source URL, collection timestamp, exact quoted source location,
and stable citation anchor before it can support a target row.

## 1. Source discovery

```text
Use the abnb_alt_data agent to propose and rank the first 12 free or
institutionally accessible source candidates for predicting ABNB quarterly
revenue and next-quarter revenue guidance. Do not collect or test data yet.
Draft rows for research/source_registry.csv with the economic mechanism, exact
URL or access method, license, collection restrictions, geography, unit of
observation, frequency, history, publication schedule and lag, revision policy,
vintage availability, cost, collection timestamp, point-in-time evidence,
leakage risk, mitigation, and citations. Limit the slate to three source
families. Clearly mark anything without defensible historical timing as
discovery_only, then wait for my approval.
```

Good follow-up guidance is specific: “Prioritize government aviation data and
Google Trends; reject app-ranking vendors for now.” Approval of a source family
does not authorize a paid tier or a different collection method.

## 1A. Permitted scrape and free-API reconnaissance

```text
Use the abnb_alt_data agent to run a smallest-sample web and free-API
reconnaissance for travel-demand signals that could improve ABNB revenue or
guidance forecasts. You have freedom to inspect candidate domains, but collect
only when the autonomous scraping gate passes. Before every first request,
register the dataset in research/source_registry.csv, log the terms URL, robots
URL, review time, intended paths, rate, cache policy, user agent, selectors, and
decision in research/scraping_audit.csv, and run assess_scrape_candidate. Use
Scrapling only for allowed public pages. Do not use Airbnb-controlled pages
without explicit automation permission, authentication, paywalls, CAPTCHAs,
personal data, or access-control bypasses. Cap requests at 10 per minute or the
site's stricter rule and cache responses.

For every potentially useful free API, update research/free_api_registry.csv
with its mechanism, documentation, signup flow, free tier, rate limits,
history, geography, frequency, lag, revisions, vintage support, restrictions,
and citations. State whether it needs no key or list only its required
environment-variable names. Add recommended names with empty values to
.env.example; never create or expose real credentials. Finish with: (1) tested
and rejected sites, (2) permitted samples and what they contain, (3) ranked
free APIs, (4) exact variables I should sync, and (5) the best next test. Do
not run a predictive model yet.
```

This prompt authorizes tiny discovery samples, not a crawl. The resulting API
shortlist is the handoff for credential setup and source selection.

## 1B. API credential sync and smoke test

```text
Use the abnb_alt_data agent to inspect .env.example without reading or printing
my local .env values. Tell me which listed free-API variables are still needed
for the approved source IDs and wait while I sync them. After I explicitly
confirm syncing, make one minimal authenticated request per approved API,
respecting its documented limit. Record endpoint shape, safe parameters,
response timestamp, coverage, units, revision/vintage behavior, checksum, and
any failure in the registries. Never include a credential in commands, logs,
URLs, artifacts, citations, or chat output. Stop before bulk collection or
modeling and recommend which API is usable for a point-in-time backtest.
```

## 1C. Complete agent-readiness assessment

Copy this entire prompt into a fresh Codex project task so the updated custom
agent configuration is loaded. The task intentionally pauses once for API-key
sync and resumes in the same conversation.

```text
You are the ABNB Research Orchestrator. Run a complete readiness assessment of
the permanent abnb_alt_data agent for institutional-quality Airbnb (NASDAQ:
ABNB) alternative-data research. This is a two-pass, point-in-time research
exercise: Phase A ends with an API sync ticket and a mandatory stop; Phase B
begins only after I confirm which approved free-API credentials I synced.

RUN IDENTITY AND OWNERSHIP

At the beginning of every progress report and final report, print this hierarchy
and distinguish the work performed by each participant:

1. ABNB Research Orchestrator — the main Codex task; owns orchestration and the
   final readiness verdict.
2. abnb_alt_data — the gpt-5.6-sol research lead; owns source discovery,
   permission review, collection, preregistration, reconciliation, canonical
   registries, comparison validity, and the quant handoff.
3. guidance_2020q4_2023q2 — transcript-context subagent for 2020Q4 through
   2023Q2.
4. guidance_2023q3_2026q2 — transcript-context subagent for 2023Q3 through
   2026Q2.

I explicitly authorize exactly two transcript-context subagents with those
exact names. The abnb_alt_data lead must launch them internally. Do not launch
any other subagent. The lead alone may edit shared canonical files. Each cohort
subagent must return structured findings to the lead or write only to its own
cohort-specific output path; neither may overwrite source_registry.csv,
hypothesis_ledger.csv, free_api_registry.csv, scraping_audit.csv, or a combined
handoff artifact.

OBJECTIVE

Assess whether the complete research system is operationally ready to:

- discover lawful scraped and API-based ABNB signals;
- establish economic mechanisms before testing;
- reconstruct what was knowable at each historical guidance cutoff;
- use the earnings transcripts and authoritative first-party filings to verify
  management-guidance targets without treating transcript content as a
  pre-call feature;
- run a fixed-rule pre-model historical replay in both transcript cohorts;
- compare the two cohort results only when doing so is methodologically valid;
- rank the free APIs that are worth syncing;
- resume safely after credential sync; and
- deliver a model-ready, leakage-audited handoff to a quant.

NON-NEGOTIABLE RESEARCH RULES

- Never invent values, timestamps, source availability, citations, transcript
  words, API capabilities, permissions, or missing observations.
- Use only information verified as available strictly before each historical
  guidance available_at timestamp. Equality with the cutoff is ineligible.
- Form and register each hypothesis before looking at its target relationship.
  Never rewrite a hypothesis after observing a result; append a version.
- Keep observation date, reference period, first-publication time, revision
  time, vintage, collection time, and prediction cutoff separate.
- Do not silently use revised present-day history. Use archived releases or
  real vintages where available; otherwise label the signal discovery_only or
  run a conservative documented lag sensitivity.
- Never use guidance language, reported results, later filings, or later
  consensus as a feature for predicting the same guidance event.
- Report negative, inconclusive, invalid, and not-testable outcomes with the
  same provenance as positive outcomes.
- Do not use paid data, start a paid/free trial requiring payment details, or
  request Bloomberg data without asking me first.
- Do not scrape an Airbnb-controlled property without explicit documented
  automation permission. Do not bypass authentication, a paywall, CAPTCHA,
  access control, block, or robots restriction. Do not collect personal data.
- Never read, print, echo, log, return, or commit a credential. Inspect
  .env.example and environment-variable names only; do not display .env values.
- Do not move, modify, reproduce, or commit EARNING-TRANSCRIPTS or restricted
  converted Markdown. Do not commit or push repository changes unless I ask.

PHASE A — READINESS, RECONNAISSANCE, AND NO-KEY REPLAY

A0. Establish repository readiness

1. State the run ID in UTC using YYYYMMDDTHHMMSSZ_abnb_readiness.
2. Inspect git status and preserve all pre-existing changes, including existing
   H.10 source-registry and hypothesis-ledger rows.
3. Read .codex/agents/abnb_alt_data.toml, docs/alt-data/agent-contract.md,
   research/source_registry.csv, research/hypothesis_ledger.csv,
   research/free_api_registry.csv, research/scraping_audit.csv, and the compact
   transcript tables.
4. Confirm the configured model and reasoning effort, import Scrapling and
   report only its version, and run the project validator. Do not install or
   upgrade packages during this assessment.
5. Create research/readiness/<run_id>/ for readiness outputs. Record commands,
   timestamps, and outcomes without secrets or restricted transcript text.

A1. Discover and permission-audit sources

Inspect up to 21 candidate datasets across these research categories:

- travel-search demand and destination interest;
- airline passengers, airport traffic, and cross-border travel;
- hotel prices, occupancy, and Airbnb-versus-hotel price positioning;
- app rankings, web traffic, and consumer engagement;
- Google Trends and destination-level search behavior;
- host-supply proxies and short-term-rental regulation;
- events, holidays, weather, and regional disruptions;
- consumer willingness-to-pay or future conjoint inputs; and
- FX and international-travel affordability.

Discovery may span those categories, but select at most three source families
for actual Phase-A collection and replay. Prefer government data, official
APIs, licensed sources already supplied by the user, clearly permitted public
downloads, and permitted public websites. Search current first-party
documentation, terms, robots files, release calendars, API specifications, and
pricing pages. Preserve direct citations and UTC review timestamps.

For every candidate dataset, update or draft its source_registry.csv record
with economic mechanism, provider, exact URL/access method, license and
collection restrictions, geography, unit, frequency, history, publication
schedule and lag, revision policy, vintage availability, cost, collection
timestamp, point-in-time evidence, leakage risk, mitigation, and status.

For every potentially useful free API, update free_api_registry.csv with:

- research mechanism and candidate feature;
- official documentation, signup, base, terms, and pricing URLs;
- whether no credential is required;
- authentication method and required environment-variable names only;
- free-tier quotas, rate limits, pagination, and retention limits;
- historical start, frequency, geographic granularity, and expected coverage of
  both transcript cohorts;
- publication lag, revision behavior, and genuine vintage support;
- license, redistribution, caching, and derived-data restrictions;
- operational reliability and reproducibility risks;
- linked source IDs, citations, and review timestamp.

Score each API out of 100 before any target test:

- 25 points: point-in-time and vintage defensibility;
- 20 points: economic relevance to ABNB revenue guidance;
- 15 points: historical coverage of the two cohorts;
- 10 points: frequency and publication lag;
- 10 points: license and collection clarity;
- 10 points: free-tier adequacy and operational reliability;
- 5 points: geographic granularity; and
- 5 points: integration burden.

Rank no-key and credential-required APIs separately. Do not allow predictive
results to retroactively change this ex-ante readiness score.

A2. Test the autonomous scraping gate

For each website considered for a tiny sample, register it before requesting
content. Record domain, exact intended paths, purpose, terms URL, robots URL,
reviewed_at UTC, permission findings, authentication/paywall/CAPTCHA/access-
control status, personal-data status, Airbnb-control status, explicit
automation permission if relevant, proposed rate, cache behavior, truthful user
agent, and selectors in scraping_audit.csv.

Construct abnb_alt_data.scraping_policy.ScrapeCandidate and run
assess_scrape_candidate. Use Scrapling only if allowed is true. Use at most 10
requests per minute or the site's stricter documented rule, request the minimum
sample, cache the response, and record retrieval time and SHA-256. If the gate
fails, do not request the page; preserve the rejection and every reason. A
successful fetch does not prove historical usability.

A3. Preregister the replay

Select at most three candidate signals with actual no-key or permitted
historical data. Before viewing their relationship with guidance, append or
version hypotheses in hypothesis_ledger.csv. Specify target, horizon, exact
signal, immutable transformation, expected direction, mechanism, geography,
cutoff, availability rule, naive baselines, replay metric, minimum evidence,
confounders, and failure conditions.

Do not replace or mutate the existing H.10 H-001 hypothesis. If it is included,
use its existing version exactly or append a clearly justified version before
looking at results.

A4. Build point-in-time inputs

Build the smallest historical panel needed to test eligibility across both
cohorts. Every raw observation must retain source ID, observation/reference
date, original release timestamp, vintage/revision identifier, collection UTC,
units, safe source URL, checksum, and the guidance cutoff to which it is
aligned. Exclude an observation unless its verified release time is strictly
before the cutoff. Preserve missing values as missing.

For API candidates requiring an unsynced credential, do not collect, estimate,
or substitute values. Mark them pending_sync and evaluate only their documented
readiness.

A5. Launch the two transcript-context subagents

Provide both subagents with:

- research/transcripts/transcript_index.csv;
- research/transcripts/guidance_facts.csv;
- the assigned fiscal-period cohort only;
- the preregistered hypotheses and fixed signal definitions;
- the point-in-time feature panel relevant to that cohort;
- authoritative SEC/shareholder-letter citations already used for numeric
  guidance when transcript wording does not contain the range; and
- the same eligibility, output, and no-model rules.

Each subagent must read compact tables first. It may open cited Markdown turns
to verify material facts and discrepancies, but no more than three full
transcripts in one research step. It must preserve [indiscernible] and never
infer a number from qualitative language. It must flag conflicts between
transcript text and authoritative first-party guidance rather than silently
choosing or averaging them.

A6. Required pre-model historical replay

Both guidance_2020q4_2023q2 and guidance_2023q3_2026q2 must independently
produce one row per guidance event and signal containing:

- prediction_id, issuing quarter, guided quarter, and cutoff UTC;
- target source, turn/filing citation, target low/high/midpoint, unit, currency,
  and constant-currency basis;
- signal ID, fixed formula, observation window, latest eligible release UTC,
  vintage, raw value, transformed value, and expected direction;
- named naive baseline and target change versus that baseline;
- eligible true/false and exact exclusion reason;
- fixed-rule signal implication and actual target direction;
- hit, miss, neutral, excluded, or not_testable classification;
- missingness, discrepancies, and leakage warnings; and
- subagent name and completion timestamp.

This is a pre-model historical replay. Do not fit a regression, AR model,
machine-learning model, correlation screen, threshold, normalization using
future observations, or outcome-selected subgroup. Simple prior-quarter and
same-quarter-prior-year baseline values may be calculated directly, but no
parameters may be fit. Report counts and event-level evidence, not a claim of
statistical significance.

A7. Reconcile and test whether comparison is valid

The abnb_alt_data lead must reconcile both cohort reports against canonical
targets and cutoff evidence. Compare the two cohort results only if all of the
following were fixed before outcomes and match across cohorts:

- target definition, guided horizon, units, currency basis, and treatment of
  qualitative guidance;
- signal formula, observation window, geographic aggregation, and expected
  direction;
- publication-time, equality-at-cutoff, revision/vintage, and missing-data
  rules;
- baseline definition and hit/miss logic; and
- the preregistered minimum-evidence rule.

If any condition fails, do not pool or compare rates. Present separate cohort
tables and name the exact incompatibility. If comparison is valid, report each
cohort separately before any pooled descriptive count, identify regime shifts,
and label the exercise small-sample. Disagreement is evidence, not an error to
tune away.

A8. Phase-A outputs and mandatory sync gate

Write these secret-free artifacts under research/readiness/<run_id>/:

- readiness_matrix.csv with capability, PASS/PARTIAL/FAIL, evidence path,
  blocker, owner, and next action;
- candidate_source_scorecard.csv;
- api_scorecard.csv;
- scrape_gate_results.csv;
- cohort_2020q4_2023q2_replay.csv;
- cohort_2023q3_2026q2_replay.csv;
- cohort_comparison.md;
- api_sync_ticket.md; and
- phase_a_summary.md.

The API sync ticket must rank the free APIs, identify the best empirical no-key
signal separately from the best credential-required candidate, list exact API
IDs and environment-variable names, provide official signup links, explain why
each credential is worth syncing, and state the smallest Phase-B smoke test.
Add recommended variable names with blank values and comments to .env.example.
Never add real values.

Then stop and wait for me to sync credentials. Do not make an authenticated
request, collect bulk history, fit a predictive model, produce a final quant
handoff, or claim full readiness in Phase A.

My continuation message will be:

Credentials synced for API IDs: <approved API IDs>. Continue Phase B of the
same readiness run. Do not display or return any credential value.

PHASE B — AUTHENTICATED SMOKE TEST, SECOND REPLAY, AND QUANT HANDOFF

Begin Phase B only after my explicit continuation message. Reuse the same two
cohort subagents; do not spawn replacements or additional agents.

B1. Credential-safe smoke tests

Check only whether each approved variable is present and non-empty; never print
its value or length. Make one minimum authenticated request per approved API.
Keep secrets out of shell command text, logged URLs, query strings retained in
artifacts, exceptions, response dumps, and citations. If a provider requires a
query-parameter credential, sanitize the effective URL before any output.

Record HTTP outcome, sanitized endpoint, safe parameters, request UTC, response
UTC, schema, pagination, units, coverage, publication fields, revision/vintage
fields, rate-limit headers, missing-value conventions, checksum, and failure
reason. Stop using an API on unexpected cost, permission, schema, or quota
conditions.

B2. Minimum historical collection

For APIs that pass the smoke test, collect only the history required for the
preregistered replay and later walk-forward folds. Preserve raw immutable
responses locally where licensing permits, plus checksums and a collection
manifest. Do not represent current reconstructed history as historical vintage
data. Mark every event ineligible when release timing cannot be proven.

B3. Repeat both cohort replays

Send the approved API panels to the same two transcript-context subagents using
their original cohort boundaries and unchanged replay rules. Require revised
cohort files that distinguish Phase-A no-key results from Phase-B API results.
The lead must rerun the comparison-validity gate before comparing or pooling.

B4. Produce the quant handoff

For every signal that is point-in-time valid and meets its preregistered minimum
evidence, create research/quant_handoffs/<run_id>/ with exactly these files:

1. targets.csv
   prediction_id, issuing_fiscal_period, guided_fiscal_period,
   guidance_available_at_utc, target_metric, target_low, target_high,
   target_midpoint, target_unit, currency, constant_currency_basis,
   target_source_id, target_citation, target_confidence.

2. features_long.csv
   prediction_id, signal_id, source_id, feature_name, observation_window_start,
   observation_window_end, source_release_at_utc, feature_available_at_utc,
   source_vintage, raw_value, transformation, feature_value, unit, geography,
   collected_at_utc, source_sha256, eligible, exclusion_reason.

3. model_matrix.csv
   One row per prediction_id with target fields, baseline fields, and one
   snake_case column per eligible preregistered feature. Include no post-cutoff
   field, formula, URL, citation text, or ineligible feature value.

4. folds.csv
   fold_id, prediction_id, role, train_start_period, train_end_period,
   test_period, embargo_or_gap, generated_at_utc. Folds must be expanding-window
   or walk-forward and must never train on a later prediction event.

5. cutoff_audit.csv
   prediction_id, signal_id, observation_id, observation_date,
   reference_period, first_published_at_utc, revised_at_utc, vintage_id,
   guidance_cutoff_at_utc, strictly_before_cutoff, included, exclusion_reason,
   availability_evidence_url, collected_at_utc.

6. source_provenance.csv
   source_id, provider, dataset, source_url, access_method, license,
   collection_restrictions, terms_url, robots_url, terms_reviewed_at_utc,
   publication_lag, revision_policy, vintage_available, cost,
   collection_timestamp_utc, artifact_path, sha256, citations.

7. data_dictionary.csv
   file_name, column_name, data_type, nullable, unit, allowed_values,
   point_in_time_meaning, derivation, source_id, analyst_notes.

8. pre_model_replay.csv
   The reconciled event-level output from both named subagents, retaining
   subagent, cohort, phase, fixed hypothesis direction, baseline comparison,
   eligibility, hit/miss/not-testable result, and discrepancy notes.

9. model_spec.md
   Define target, horizon, candidate features, fixed transformations, seasonal
   and prior-quarter baselines, optional expanding-window AR baseline, fold
   construction, embargo/gap, metrics, minimum sample, missing-data policy,
   standardization inside training folds, leakage prohibitions, lag/vintage
   sensitivities, coefficient/sign stability tests, and allowed model classes.
   The quant—not this readiness run—will fit the mathematical models.

10. handoff_summary.md
    State source readiness, target coverage, feature coverage, cohort agreement
    or incompatibility, negative/inconclusive evidence, known confounders,
    licensing limits, small-sample risks, and what the quant may and may not
    infer.

11. manifest.json
    Include run_id, created_at_utc, agent hierarchy, git commit and dirty-state
    disclosure, hypothesis versions, source IDs, file row counts, date range,
    eligible prediction count, missingness summary, schema version, and every
    included relative file path.

12. checksums.sha256
    Include SHA-256 checksums for every handoff file except checksums.sha256
    itself. Do not include restricted transcript files or credentials.

Use UTF-8, comma-delimited CSV with one header row, ISO-8601 UTC timestamps,
YYYY-MM-DD dates, periods formatted YYYYQ#, decimal points without thousands
separators, lowercase true/false, stable IDs, no spreadsheet formulas, and
blank fields for missing values. Never encode missing as zero. Keep ineligible
observations in features_long.csv and cutoff_audit.csv but exclude them from
model_matrix.csv. Do not reproduce licensed transcript text.

B5. Validate the handoff

Before declaring readiness:

- verify unique primary keys and referential integrity across files;
- verify model_matrix has one row per eligible prediction_id;
- verify every included feature has cutoff_audit evidence strictly before the
  corresponding guidance cutoff;
- verify no target or future-period field appears among model inputs;
- verify fold chronology and no train/test overlap;
- verify units, currencies, transformations, and missing values agree with the
  data dictionary;
- verify all manifest row counts and SHA-256 checksums;
- run the repository tests and project validator; and
- preserve validation failures instead of editing data merely to pass.

FINAL READINESS REPORT

Report the named agent hierarchy first. Then provide:

1. an overall READY, CONDITIONALLY_READY, or NOT_READY verdict;
2. separate PASS/PARTIAL/FAIL findings for orchestration, source governance,
   scraping safety, API discovery, credential safety, transcript grounding,
   point-in-time alignment, preregistration, early-cohort replay, late-cohort
   replay, comparison validity, negative-result handling, reproducibility, and
   quant handoff;
3. work performed by abnb_alt_data and by each named subagent;
4. the two cohort results separately and a comparison only if valid;
5. the three most promising signals, without claiming edge when evidence is
   merely descriptive or inconclusive;
6. all rejected, blocked, negative, and not-testable sources with reasons;
7. exact artifact paths and citations;
8. unresolved blockers and the next falsification test; and
9. a concise note addressed to the quant explaining whether modeling may begin.

Do not claim predictive usability merely because an API works or a scrape
succeeds. Operational readiness, point-in-time validity, descriptive signal
evidence, and modeled incremental forecast value are four separate conclusions.
```

## 2. Transcript and guidance preparation

```text
Use the abnb_alt_data agent to prepare transcript-derived targets. Read
research/transcripts/transcript_index.csv first. Work chronologically in batches
and open no more than three full Markdown transcripts in this step. Extract
management revenue guidance into research/transcripts/guidance_facts.csv and
reported results into reported_metrics.csv. Every row must cite the Markdown
path and stable speaker-turn ID. Preserve management's exact unit, range, point,
midpoint, currency basis, guided period, and qualitative wording. Never infer a
number from qualitative language or [indiscernible]. Leave unknown timestamps
null. Separately identify authoritative evidence needed to verify the exact call
and guidance-release time; do not use filenames or PDF creation metadata as
proof. Stop for my review when this batch is complete.
```

Repeat the prompt for later batches. Structured rows—not all 23 transcripts in
one context—become the longitudinal dataset.

## 3. Hypothesis preregistration

```text
Use the abnb_alt_data agent to preregister up to six hypotheses using only the
source registry and economic reasoning. Do not inspect target-signal
correlations or test results yet. For each hypothesis, append a versioned row to
research/hypothesis_ledger.csv specifying the target, horizon, signal,
transformation, expected direction, mechanism, geography, cutoff and
availability rules, baseline, evaluation metric, minimum evidence, confounders,
and failure conditions. Explain which hypotheses are distinguishable with the
available quarterly sample, then wait for my priority approval.
```

## 4. Collection and provenance audit

```text
Use the abnb_alt_data agent to collect only a small validation sample from the
approved free sources S-001 and S-002. Before collection, recheck license,
robots guidance where applicable, rate limits, and historical-vintage access.
Preserve exact URLs, safe query parameters, release timestamps, local collection
timestamps in UTC, units, raw checksums, and citations. Do not access an
Airbnb-controlled property or authenticated endpoint. Do not expand the source
families. Report missing history, revisions, or timing ambiguity and stop before
modeling.
```

Replace the source IDs with approved registry entries. If permissions or cost
changed since approval, the agent must ask again.

## 5. Single-signal guidance test

```text
Use the abnb_alt_data agent to test hypothesis H-001 against management revenue
guidance. Read research/transcripts/transcript_index.csv and
research/transcripts/guidance_facts.csv first. Use the cited Markdown turns to
verify every target. Treat guidance available_at as the prediction cutoff and
use only alternative-data releases with verified availability strictly before
that cutoff. Reject missing or unverified timestamps. Compare against the
prior-quarter and seasonal baseline using expanding-window walk-forward
validation. Keep transformations and missing-data treatment inside each
training fold. Report MAE, RMSE, directional accuracy, sample size, uncertainty,
coefficient or rank stability, publication-lag sensitivity, and improvement
over each baseline. Preserve every negative or inconclusive result. Do not tune
the hypothesis after seeing the outcome, add a new source, use paid data, or
request Bloomberg data without asking me first.
```

Run one preregistered hypothesis at a time initially. The surprise-versus-
consensus target remains blocked until an approved point-in-time consensus
series exists.

## 6. Bloomberg ticket only

```text
Use the abnb_alt_data agent to prepare—but not execute—an exact Bloomberg
extraction ticket for the point-in-time consensus data needed by hypothesis
H-004. Specify every security and identifier, field, start and end date,
historical as-of or vintage requirement, frequency, currency, units, trading and
calendar convention, XLSX sheet name, exact column order, date format, and
missing-value representation. Explain how each field enters the guidance-
surprise calculation. Ask for my approval before any Bloomberg request.
```

## 7. Negative-result review

```text
Use the abnb_alt_data agent to review the completed result for hypothesis H-002.
Do not change its specification, add transformations, or search subgroups to
rescue it. Verify the point-in-time cutoff, baseline construction, sample size,
lag sensitivity, and fold-local preprocessing. Classify the evidence as
negative, inconclusive, or invalid. Record the status and result path in
research/hypothesis_ledger.csv, preserve the reproducible outputs, and state
what genuinely new evidence—not post-hoc tuning—would justify a new version.
```

## 8. Top-three-signal memo

```text
Use the abnb_alt_data agent to write a short institutional research memo ranking
the three most promising tested signals. Rank point-in-time defensibility and
incremental improvement over baseline ahead of in-sample fit. For each signal,
state the mechanism, data provenance, target and horizon, sample size, walk-
forward result, lag sensitivity, stability, known confounders, license/cost
constraints, and the next falsification test. Include negative findings that
changed the source ranking. Preserve citations and collection timestamps, and
do not claim an edge where results remain inconclusive.
```

## Local validation commands

Run these from the repository root after changing schemas, transcript metadata,
or guidance facts:

```bash
python3 -m pytest -q
python3 scripts/validate_project.py --root . --expected-transcripts 23
```

The validator deliberately rejects invalid guidance citations, unverified
guidance cutoffs, duplicate transcript periods, schema drift, and staged
proprietary or likely credential files.
