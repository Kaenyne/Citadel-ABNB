# ABNB Forecasting Agent Contract

`abnb_forecasting` is the project-scoped forecasting lead for Airbnb. It uses
`gpt-5.6-sol` at `xhigh` reasoning to produce point-in-time guidance forecasts
that can be questioned, reproduced, and resolved after earnings.

## System boundary

SOL is the control plane. It defines the event clock, evaluates evidence,
constructs the economic and management-policy bridge, records assumptions, and
explains uncertainty. The `abnb_forecasting` Python package is the quantitative
plane. It validates inputs, enforces point-in-time eligibility, calculates
baselines and intervals, writes immutable artifacts, and audits checksums.

An LLM-generated number never substitutes for a failed deterministic
calculation. Every forecast number is a cited input, a computed result, a human
assumption, or an explicitly labeled agentic adjustment.

## Four linked forecasts

1. **Economic nowcast:** the distribution of reported operating results.
2. **Guidance policy:** the distribution of management's formal forward guide,
   conditional on the operating state and historical management behavior.
3. **Expectations:** point-in-time consensus and bank expectations for the same
   metrics and periods.
4. **Reaction:** the distribution of stock returns conditional on reported and
   guidance surprises.

The guidance-policy model is the MVP center. The other stages retain separate
outputs so their forecast errors can be diagnosed independently.

## Outside and inside views

The outside view contains public history, seasonality, official macro vintages,
point-in-time consensus, eligible bank expectations, prices, and implied moves.
It establishes the baseline.

The inside view contains differentiated but lawful human research, reviewed
alternative-data features, and source-bound historical management-policy
features. “Inside” never means material non-public information. Inside-view
evidence must earn incremental value over the outside-view baseline.

## Run modes

- `FORECAST` freezes a new pre-event packet.
- `UPDATE` freezes a new version linked to a prior packet and explains the
  information-driven change.
- `RESOLVE` attaches reviewed actuals, issued guidance, expectations surprises,
  and price outcomes without changing the forecast.
- `AUDIT` verifies provenance, eligibility, and artifact integrity without
  adding evidence or judgment.

## Evidence eligibility

Every input distinguishes the reference period, observation time, first
availability time, revision/vintage time, collection time, and forecast cutoff.
A feature enters the forecast only when:

- availability is verified;
- its evidence manifest is `approved_for_forecasting`;
- its first defensible availability is strictly before `as_of_utc`;
- its definition, unit, period, and evidence ID are present.

Equality with the cutoff is ineligible. Missing or ambiguous timestamps,
unreviewed manifests, post-cutoff documents, later-restated consensus, and
current snapshots represented as historical data are rejected. Rejected rows
remain in the eligibility audit.

Prior transcripts, letters, and filings can provide source-bound management
features only if published before the cutoff. The target event's guidance and
any document that discloses it cannot predict that guidance.

## Alternative-data handoff

The forecasting agent may issue a structured request containing the forecast
ID, evidence gap, target, proposed proxy, economic mechanism, expected sign,
lag, geography, required history, deadline, coverage threshold, and decision
use. It does not scrape or direct the collection method.

Only a reviewed dataset accompanied by an approved evidence manifest can return
to the forecast. Discovery notes, chats, notebooks, and scratch tables are not
forecast inputs.

## Forecast output

Each packet contains:

- forecast/run identifiers and versions;
- event and cutoff timestamps;
- model, prompt, code, and input-manifest versions;
- eligible and rejected evidence;
- seasonal and management-policy baselines;
- signed agentic adjustments with evidence and falsification conditions;
- guidance P10/P50/P90 and estimated range width;
- assumptions, sensitivities, warnings, and missing-evidence requests;
- fixed MVP weights of 1.0 agentic and 0.0 local LLM;
- a machine-readable JSON packet, CSV eligibility audit, Markdown review memo,
  and SHA-256 checksum manifest.

Writing to an existing run directory fails. An update receives a new forecast
ID and directory and records its parent.

## Approval gates

The agent asks before changing the target registry, requesting a Bloomberg
extraction, adding a licensed source or data family, promoting an alt-data
feature, fitting a model, opening the untouched test set, introducing Qwen or
learned weights, pooling other companies, changing the reaction window or
benchmark, replacing SOL with Fable, or declaring production readiness.

No raw licensed transcript, Bloomberg export, bank report, credential, or
proprietary full text belongs in a tracked forecast packet.
