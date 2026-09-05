# Phase-A checkpoint

- Run ID: `20260903T053309Z_abnb_readiness`
- Owner: `abnb_alt_data`
- Orchestrator: `ABNB Research Orchestrator`
- Repository HEAD at start: `70f3bb9b85cfe11bb66e74eb6c7cbf3277843cd4`
- Permanent agent: `gpt-5.6-sol`, high reasoning, workspace-write
- Scrapling import: `0.4.15`
- Project validator: PASS for 23 indexed transcripts
- Canonical target panel: 23 guidance events, including 20 numeric ranges and three explicitly qualitative/non-numeric events
- Preregistered signals: H-001 unchanged; H-002 ECB EUR/USD; H-003 BLS lodging CPI
- Scraping gate: BLS documentation preflight allowed, but the single Scrapling request returned HTTP 403 and was not retried; TSA and Airbnb-controlled investor site blocked
- Restricted transcript PDFs and Markdown were not modified, moved, reproduced, or committed.
- No credential, paid source, Bloomberg request, model, regression, correlation, or threshold search was used.

Collection commands are limited to the fixed three-signal panel. H-001 uses dated Board H.10 archives; H-002 requests the ECB SDMX endpoint with `includeHistory=true`; H-003 is retained but remains ineligible wherever exact historical BLS release time is not proven.
