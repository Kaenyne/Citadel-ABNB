# ABNB alternative-data readiness — Phase A

Run ID: `20260903T053309Z_abnb_readiness`

## Agent hierarchy and ownership

1. **ABNB Research Orchestrator** — main task; orchestration and final verdict.
2. **abnb_alt_data** — source governance, permission audit, preregistration, fixed no-key collection, reconciliation, comparison validity, and sync ticket.
3. **guidance_2020q4_2023q2** — independent 11-event early-cohort replay.
4. **guidance_2023q3_2026q2** — independent 12-event late-cohort replay.

## Phase-A verdict

**CONDITIONALLY_READY_FOR_CREDENTIAL_SYNC; NOT_READY_FOR_MODELING.**

The system successfully preserved fixed hypotheses, strict cutoffs, genuine H.10 release vintages, negative results, and two independent cohort reports. Full readiness is blocked because ECB and BLS timing is not strict-PIT verified, the early seasonal-baseline sample is small, credentials have not been smoke-tested, Phase B has not repeated the replay, and no executable quant handoff exists.

## Three selected signals

1. **H-001 Federal Reserve H.10 broad dollar.** Strongest operational source: 62 dated Board release pages produced 23 feature rows, each with a release timestamp strictly before its cutoff. On the only 16 events with numeric targets and the fixed seasonal baseline, the replay recorded 9 hits and 7 misses. Early was 3/4; late was 6/12. This instability makes evidence inconclusive rather than alpha.
2. **H-002 ECB USD per EUR.** Economically coherent and API-accessible, but exact initial publication timestamps are absent. Strict replay has zero eligible rows. A pre-fixed conservative 16:00 UTC sensitivity was 3/4 early and 7/12 late; it cannot be pooled because the early cohort fails the preregistered six-event minimum and it is not strict-PIT evidence.
3. **H-003 BLS unadjusted lodging CPI.** Useful hotel-price-positioning mechanism and final-on-release unadjusted values, but exact historical release timestamps were not lawfully reconstructed. All replay rows are not testable. The v2 key improves quota/history, not timing validity.

No result establishes incremental revenue-guidance predictability. No regression, AR model, correlation, threshold, or machine-learning method was used.

## Collection and governance results

- 21 candidate source families and 18 free APIs were registered and scored before target testing.
- Fixed collection produced 1,728 raw observations, 69 event-signal feature rows, and 66 provenance records.
- H-001 strict feature eligibility: 23/23. H-002 strict: 0/23, sensitivity-only: 23/23. H-003 strict: 0/23.
- The BLS documentation scrape passed the deterministic preflight, but the single Scrapling request returned HTTP 403. It was cached, recorded, and not retried. TSA was blocked for unclear terms/robots; Airbnb-controlled automation was blocked for lack of explicit permission.
- Paid app/traffic and STR market datasets were not accessed. Bloomberg was not requested. No credential was read or used.
- Three qualitative early guidance events remain qualitative; no midpoint was invented. The 2023Q4 transcript 70%/official SEC 17% discrepancy is preserved.

## Required stop

See `api_sync_ticket.md` for exact optional variables and smoke tests. Phase A stops here. The user must choose and sync approved credentials before any authenticated call or Phase-B collection.
