# Prompting and Running `abnb_forecasting`

Start a fresh Codex project task after adding or changing the custom-agent file
so Codex reloads `.codex/agents/abnb_forecasting.toml`. Address the agent by its
exact name.

## FORECAST

```text
Use abnb_forecasting in FORECAST mode.
Target event: <event name and issuing fiscal period>.
Information cutoff: <offset-aware timestamp>.
Decision question: <guidance metric, period, and unit>.
Approved input manifests: <manifest IDs or none>.
Approved consensus/Bloomberg packet: <packet ID or none>.
Human inputs: <human-input IDs or none>.

Run the strict point-in-time audit and retain all rejected evidence. Build the
outside-view and management-policy baselines first. Show the macro, operating,
and management-policy bridges. Express agentic judgment only as signed,
evidence-linked adjustments with falsification conditions. Produce P10/P50/P90
and issue an AlternativeDataRequest for any decision-relevant evidence gap.
Freeze the packet without training or opening a test period.
```

## UPDATE

```text
Use abnb_forecasting in UPDATE mode.
Parent forecast: <frozen forecast ID>.
New information cutoff: <offset-aware timestamp>.
New reviewed evidence: <evidence or manifest IDs>.
Reason for update: <what became available>.

Create a new version and directory. Do not edit the parent. Re-run eligibility
at the new cutoff and provide a numeric bridge from the prior forecast to the
new forecast, including evidence additions, exclusions, and changed assumptions.
```

## RESOLVE

```text
Use abnb_forecasting in RESOLVE mode for <frozen forecast ID>.
Reviewed outcome evidence: <actual, guidance, consensus, and market evidence IDs>.

Attach outcomes without changing the frozen forecast. Score every available
target and interval, separate economic, guidance-policy, expectations, and
reaction errors, and preserve missing or non-comparable outcomes explicitly.
```

## AUDIT

```text
Use abnb_forecasting in AUDIT mode for <forecast packet directory>.

Verify checksums, run identity, evidence-manifest approval, strict cutoff
eligibility, rejected rows, baseline arithmetic, adjustment arithmetic, and
parent linkage. Do not add evidence or revise the forecast.
```

## MVP commands

The deterministic rehearsal command will be installed by the MVP implementation:

```bash
python3 scripts/run_forecast_rehearsal.py forecast \
  --input tests/fixtures/forecast_rehearsal.json \
  --output /tmp/abnb-forecast-mvp/ABNB-MVP-REHEARSAL-v1
python3 scripts/run_forecast_rehearsal.py audit \
  --packet-dir /tmp/abnb-forecast-mvp/ABNB-MVP-REHEARSAL-v1
```

The fixture is synthetic. A successful run validates workflow and controls; it
is not an ABNB forecast, backtest, alpha estimate, or measure of model accuracy.

Run repository checks with:

```bash
python3 -m pytest -q
python3 scripts/validate_project.py --root . --expected-transcripts 23
```
