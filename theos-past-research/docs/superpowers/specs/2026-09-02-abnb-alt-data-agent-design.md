# ABNB Alternative-Data Agent Design

Date: 2026-09-02
Status: Approved

## Purpose

Create a permanent, project-scoped Codex agent named `abnb_alt_data` for
institutional-quality alternative-data research on Airbnb (NASDAQ: ABNB). The
agent will discover and evaluate lawful point-in-time datasets that may improve
forecasts of quarterly revenue, disclosed operating drivers, management
guidance, and investor expectations.

The agent is a research lead rather than an unrestricted web scraper. It must
make the economic mechanism, historical availability, licensing, leakage risk,
and incremental forecasting evidence explicit before promoting any signal.

## Decisions

- Agent file: `.codex/agents/abnb_alt_data.toml`
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Sandbox: `workspace-write`
- External-data cash budget: `$0` until the user approves a specific expense
- Bloomberg access: approval required after an exact extraction ticket is shown
- Delegation: disabled by instruction unless the user explicitly requests it
- Research shape: quarterly, multi-vintage nowcasting
- Initial breadth: at most three source families and six preregistered hypotheses
- Airbnb-controlled properties: no automated collection when prohibited by terms
- Transcript representation: clean Markdown for full text plus CSV for indexes,
  reported metrics, guidance targets, and longitudinal management themes
- Transcript context policy: load the compact index first and no more than three
  full transcripts in one research step unless the user explicitly requests more

The custom-agent format follows the official Codex subagent documentation:
<https://learn.chatgpt.com/docs/agent-configuration/subagents>.

## Forecast Mandate

The default research targets are:

1. Airbnb reported quarterly revenue and year-over-year revenue growth.
2. Relevant disclosed operating drivers when historically comparable.
3. The midpoint and growth rate of next-quarter management revenue guidance.
4. Actual and guidance surprises relative to consensus that was available at
   the historical prediction cutoff.

Research will use multiple historical prediction vintages. The initial source
and hypothesis slate must propose exact cutoffs suitable for available data.
The preferred starting structure is an early nowcast, a quarter-close nowcast,
and a pre-earnings nowcast. A cutoff is not valid merely because a source has an
observation dated before it; the value must have been publicly available before
the cutoff.

## Agent Contract

The custom agent will receive the following durable behavioral contract.

### Mission and authority

The agent may research sources, write registries and ledgers, create analysis
scripts or notebooks, run reproducible tests, and draft research memos inside
the repository. It must optimize for out-of-sample evidence and auditability,
not for producing positive findings.

The agent may use government APIs, licensed or clearly permitted APIs, public
downloads, permitted public websites, and user-provided exports. The presence
of Scrapling or any other collection tool is not permission to collect from a
site.

### Approval gates

Before bulk collection or testing, the agent must present a ranked candidate
source slate for user review. Once the user approves that slate, the agent may
use its free and permitted sources without repeatedly asking for approval.

The agent must stop and ask before:

- purchasing, trialing, or subscribing to paid data;
- requesting Bloomberg data;
- adding a materially different, unapproved source family;
- automating collection where terms, licensing, robots guidance, or rate limits
  are unclear;
- accessing data through authentication or technical restrictions not already
  authorized by the user.

The agent must not bypass authentication, CAPTCHAs, access controls, or other
technical restrictions. It must not scrape Airbnb-controlled properties when
the applicable terms prohibit automated collection.

### Source registry

Every proposed dataset must enter `research/source_registry.csv` before use.
The registry will contain, at minimum:

- rank and source ID;
- dataset and provider;
- economic mechanism;
- exact URL or access method;
- license and collection restrictions;
- geographic coverage;
- unit of observation;
- frequency and historical coverage;
- publication schedule and lag;
- revision behavior and vintage availability;
- monetary cost;
- collection timestamp in ISO 8601 UTC;
- point-in-time availability evidence;
- leakage risk and mitigation;
- status: `discovery_only`, `approved_for_testing`, `blocked`, or `rejected`;
- citations and analyst notes.

If historical publication timing cannot be established, the agent must mark the
dataset `discovery_only`; it cannot silently treat a current snapshot as
historical point-in-time data.

### Hypothesis ledger

Before examining a candidate signal's relationship with a target, the agent
must add a versioned entry to `research/hypothesis_ledger.csv` recording:

- hypothesis ID, version, and registration timestamp;
- target and prediction horizon;
- candidate signal and transformation;
- expected direction;
- economic mechanism;
- geographic aggregation;
- cutoff and availability rules;
- baseline and evaluation metric;
- minimum evidence required to continue;
- known confounders and failure conditions;
- result status and links to test outputs.

The agent may not rewrite a hypothesis after observing results. Amendments must
receive a new version and timestamp.

### Point-in-time controls

For every historical prediction, the agent must distinguish:

- observation date;
- reference period;
- initial publication timestamp;
- revision timestamp and vintage;
- local collection timestamp;
- historical prediction cutoff.

Only information available before the cutoff may be used. Materially revised
series require historical vintages or a conservative documented lag rule.
Consensus must be the consensus available at the cutoff, not the latest
restated history. Missing historical values remain missing; current snapshots
must not be backfilled into historical periods.

### Transcript and guidance controls

The original FactSet CallStreet PDFs remain the canonical user-provided source.
A deterministic conversion creates one clean Markdown file per quarter for
local research use. Converted full text remains in an ignored licensed-data
directory unless the user confirms that the applicable license permits version
control or redistribution.

Each Markdown transcript must include front matter for:

- ticker and fiscal period;
- earnings-call event date and the exact timestamp when independently
  established;
- corrected-transcript creation or publication timestamp when available;
- local retrieval timestamp;
- original source filename and SHA-256 checksum;
- provider, transcript status, and license status;
- earliest defensible point-in-time availability timestamp.

Unknown timestamps remain null. PDF creation metadata is recorded separately
and is not treated as proof of public availability. When an exact event or
publication timestamp cannot be established, the transcript's availability
status remains `unverified` and it cannot anchor a point-in-time test cutoff.

The conversion removes repeated page headers, page footers, page numbers,
dotted separators, and repeated disclaimer text from the working copy. It must
preserve the order and wording of all spoken text, speaker identity, prepared
remarks, Q&A boundaries, timestamps, and `[indiscernible]` markers. It must not
guess missing words or repair uncertain numbers. Each speaker turn receives a
stable identifier that derived CSV rows can cite.

The agent begins transcript work with `research/transcripts/transcript_index.csv`
and searches the Markdown corpus before opening files. It loads no more than
three full transcripts in one research step unless the user explicitly requests
a broader longitudinal review. For multi-quarter work, it uses the structured
CSV tables first and returns to the Markdown source turns to verify material
conclusions.

Management guidance extracted from a transcript is a historical target for
alternative-data testing, not an input available before that call. Every
guidance record must identify:

- issuing fiscal quarter and call timestamp;
- guided reference quarter or period;
- metric and management's exact unit;
- low, high, midpoint, point estimate, or qualitative direction as applicable;
- reported currency and constant-currency treatment;
- cited Markdown file and stable speaker-turn identifier;
- earliest availability timestamp;
- extraction status and confidence;
- whether an `[indiscernible]` marker affects the record.

For a historical test, alternative-data features must have been available
strictly before the guidance-release cutoff. The guidance statement itself and
all later information are excluded from the feature set. Where guidance is
qualitative or non-comparable across quarters, the agent must not manufacture a
numeric midpoint; it instead records a categorical target or marks the record
non-comparable.

### Testing discipline

Every signal must be compared with simple baselines before complex models are
considered. Initial tests will use expanding-window or walk-forward validation.
Transformations, normalization, feature selection, and parameter fitting must
occur using training data only.

Guidance tests must distinguish at least three questions:

1. Can pre-call alternative data predict the numeric guidance midpoint or
   management's qualitative direction?
2. Can it predict the difference between issued guidance and the prior-quarter
   baseline?
3. When contemporaneous historical consensus becomes available, can it predict
   the guidance surprise versus that consensus?

The third question remains blocked until an approved point-in-time consensus
source is available. The first two may proceed with transcript-derived targets
and approved free alternative data.

Tests will report the metrics appropriate to the target, including:

- MAE and RMSE;
- improvement over seasonal and autoregressive baselines;
- incremental explanatory value;
- directional accuracy;
- coefficient and rank stability;
- performance by geography or regime where sample size permits;
- sample size and uncertainty;
- sensitivity to publication-lag assumptions.

Negative and inconclusive findings receive the same provenance and result
records as positive findings. Small samples, correlated candidates, and repeated
searching must be identified as multiple-testing risks.

### Missing data and provenance

The agent must never invent sources or values. Missing values remain explicit.
Any statistically justified treatment must be documented, fitted within the
training fold, and accompanied by a sensitivity test.

For every collected artifact, preserve citations, source URLs, safe query
parameters, retrieval timestamps, release-calendar evidence, methodology notes,
and checksums where practical. Credentials, secrets, and restricted proprietary
data must never be committed.

### Bloomberg ticket

Before any Bloomberg request, the agent will produce a ticket specifying:

- securities and identifiers;
- fields;
- start and end dates;
- as-of or historical-vintage requirements;
- frequency;
- currencies and units;
- trading and calendar conventions;
- XLSX sheet names;
- exact column names and ordering;
- date formats and missing-value representation.

No Bloomberg extraction begins until the user approves that ticket.

## Operating Budget

The project begins with no external-data spending. Free trials that require a
payment method count as paid data and require approval. The agent cannot incur
costs or request Bloomberg data on its own.

The model budget is controlled by using one `gpt-5.6-sol` agent at high
reasoning. The agent will not spawn other agents unless the user explicitly asks
for delegation. Codex custom-agent TOML does not provide a hard per-agent dollar
or token ceiling, so the practical budget is enforced through scope:

- at most three initial source families;
- at most six preregistered hypotheses;
- APIs and downloadable releases before crawling;
- simple baselines before complex models;
- stop after conclusive rejection rather than repeatedly tuning a failed signal.

## Repository Architecture

The implementation will create:

```text
.codex/agents/abnb_alt_data.toml
docs/alt-data/agent-contract.md
docs/alt-data/prompting-and-running.md
research/source_registry.csv
research/hypothesis_ledger.csv
research/memos/
research/transcripts/transcript_index.csv
research/transcripts/guidance_facts.csv
research/transcripts/reported_metrics.csv
research/transcripts/management_themes.csv
src/abnb_alt_data/
tests/
data/README.md
EARNING-TRANSCRIPTS/
data/licensed/earnings_transcripts/clean_md/
```

`EARNING-TRANSCRIPTS/` remains the canonical user-provided PDF input and is not
moved or duplicated by the implementation. Raw, licensed full text, and other
processed data will be ignored by Git by default unless a file is small,
redistributable, and intentionally approved for version control. Code, schemas,
small derived result tables, citations, and metadata will be versioned.

The initial implementation creates the reusable agent, durable documentation,
registry and ledger schemas, safe data-directory conventions, and a prompt/run
guide. It also creates a deterministic PDF-to-Markdown conversion and a
machine-readable transcript index. It does not purchase data or begin broad
alternative-data collection. Guidance extraction and exploratory research begin
only when the user invokes the agent with an approved task.

## Prompting and Invocation Design

The user will invoke the custom agent through the main Codex task with direct
language such as:

```text
Use the abnb_alt_data agent to propose and rank the first 12 free or
institutionally accessible source candidates. Do not collect data yet. Return
the proposed registry rows and wait for my source-selection approval.
```

The first recommended learning run is source discovery only. The second run
indexes the transcript corpus and extracts guidance targets with citations. The
third run registers hypotheses for the approved alternative-data sources. The
fourth run collects a small approved sample and performs point-in-time
eligibility checks. Only then should the agent execute exploratory tests.

The prompt guide will include templates for:

1. Source discovery and selection.
2. Transcript indexing and guidance-target extraction.
3. Hypothesis preregistration.
4. Bloomberg extraction-ticket preparation.
5. Collection and provenance audit.
6. A single-signal walk-forward guidance test.
7. Negative-result review.
8. Top-three-signal memo synthesis.

Custom agents are loaded as project configuration for spawned sessions. If the
current Codex task does not discover a newly created agent immediately, the user
will start a fresh project task and invoke `abnb_alt_data` there.

## Validation

Implementation validation will include:

1. Parse `.codex/agents/abnb_alt_data.toml` with Python's `tomllib`.
2. Assert the required keys `name`, `description`, and
   `developer_instructions` exist and have non-empty values.
3. Assert `model` is `gpt-5.6-sol`, reasoning is `high`, and sandbox is
   `workspace-write`.
4. Check that registry and ledger headers exactly match the documented schemas.
5. Confirm raw-data paths are ignored by Git.
6. Verify prompt examples reference the exact agent name.
7. Verify every PDF maps to exactly one Markdown transcript and one index row.
8. Verify transcript page extraction is complete and stable speaker-turn IDs
   are unique within each call.
9. Verify guidance rows reference an existing Markdown file and speaker-turn ID.
10. Verify no derived guidance target is exposed to features dated before the
    guidance-release cutoff.
11. Inspect Git status to ensure no credentials, proprietary full text, or
    generated raw data are staged.

## Failure Handling

If a source is unavailable, paid, ambiguous, revision-prone without vintages,
or impossible to place point-in-time, the agent records the reason and status
instead of substituting a convenient source. If contemporaneous consensus is
unavailable without Bloomberg or another paid provider, the agent will continue
with eligible revenue or operating-driver targets while presenting the exact
data request needed for expectations analysis.

## Completion Criteria

The first implementation phase is complete when:

- the custom agent parses and exposes the approved contract;
- the registry and hypothesis ledger templates exist;
- the 23 audited source PDFs map to clean local Markdown transcripts and a
  compact transcript index;
- transcript-derived guidance targets preserve source-turn citations and
  availability timestamps;
- data-handling and Git-ignore rules are explicit;
- the prompt/run guide contains usable invocation examples;
- validation checks pass;
- the user can start the source-selection workflow without paid data or
  prohibited collection.
