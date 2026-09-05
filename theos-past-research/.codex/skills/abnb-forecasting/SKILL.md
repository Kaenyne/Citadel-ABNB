---
name: abnb-forecasting
description: Create, update, resolve, or audit an Airbnb guidance forecast from timestamped reviewed evidence. Use for ABNB macro-to-operating-to-guidance forecasting; do not use for alternative-data collection or local-LLM training.
---

# ABNB Forecasting

Produce a versioned, falsifiable forecast whose evidence eligibility and
arithmetic can be reproduced independently of the model narrative.

Before a run, read [the agent contract](../../../docs/forecasting/agent-contract.md).
Use [the operator runbook](../../../docs/forecasting/prompting-and-running.md) for
the exact prompt and local command appropriate to the requested mode.

## Select the mode

- `FORECAST`: create a new pre-event forecast at an immutable information cutoff.
- `UPDATE`: create a new version linked to a frozen parent after new information.
- `RESOLVE`: attach reviewed outcomes after the event; never rewrite the forecast.
- `AUDIT`: reproduce eligibility and checksums without adding evidence or judgment.

## Forecast workflow

1. Establish the target event, fiscal periods, strict `as_of_utc`, market
   calendar, and target definition. Stop if the decision question is ambiguous.
2. Load only typed inputs. Separate outside-view public history, macro,
   consensus, and price evidence from inside-view human research and reviewed
   alternative data.
3. Run the repository eligibility audit. Retain rejected rows and reasons.
4. Build seasonal and management-policy baselines before differentiated evidence.
5. Bridge macro conditions to the operating state, then the operating state to
   management's likely guidance policy. Keep the reported-results nowcast,
   guidance, expectations, and reaction outputs separate.
6. Express agentic judgment only as signed adjustments to a reproducible
   baseline. Each adjustment needs evidence IDs, rationale, and a falsification
   condition.
7. If a decision-relevant operating signal is missing, write an
   `AlternativeDataRequest`. Do not collect it yourself and do not use scratch
   work returned by another agent.
8. Generate P10/P50/P90, scenarios, warnings, and sensitivity. State when an
   interval is uncalibrated because history is insufficient.
9. Freeze the packet with `scripts/run_forecast_rehearsal.py`. Do not overwrite a
   prior version.

## Evidence boundary

A feature is eligible only when its availability is verified, its approved
manifest is present, and `first_available_at_utc < as_of_utc`. Equality fails.
Do not use same-event guidance, documents that disclose the target, post-event
research, current snapshots represented as historical vintages, or parametric
model memory as evidence.

The current MVP is a workflow rehearsal. Do not describe synthetic outputs as a
real ABNB forecast, backtest, alpha, or model accuracy. Training, SARIMAX, Qwen,
cross-company pooling, learned forecast weights, and reaction-model fitting each
require a separate approved experiment.
