# Supply, scarcity, regulatory, and public-web edge — E0 report

1. **ABNB Edge-Data Research Orchestrator** — main Codex task; owns orchestration, user communication, and the final decision.
2. **abnb_alt_data** — permanent gpt-5.6-sol research lead; owns source governance, permission decisions, canonical registries, point-in-time methodology, hypothesis reconciliation, and the final ranked slate.
3. **physical_world_activity_edge** — searches physical sensors, mobility, transportation, remote sensing, environmental, and infrastructure data.
4. **supply_scarcity_web_edge** — searches STR supply, regulatory, public-calendar, capacity-scarcity, pricing, and permitted web-exhaust data.

## Ownership and phase boundary

These are `supply_scarcity_web_edge` findings for run `20260903T062839Z_abnb_edge_discovery`. This lane performed E0 discovery only. It did not inspect any relationship with ABNB outcomes, preregister hypotheses, fit a model, start E1, or modify canonical registries. The lead owns final reconciliation and source selection.

## Outcome

Ten serious candidates were retained. None passed the autonomous collection gate, so **zero direct source requests and zero tiny samples** were made. This is a substantive result: the strongest temporal archive, Hawaiʻi TAT, is explicitly unusable for automated/commercial collection; otherwise attractive city portals lack verified robots or exact automation permission for the intended paths. Search-index reconnaissance supplied primary official URLs and source metadata without opening the candidate sites directly.

Predictive alpha has not been tested.

## Ranked slate

| Rank | ID | Dataset | E0 status | Historical strength | Biggest failure reason |
|---:|---|---|---|---|---|
| 1 | SCW-005 | NYC OSE registration reports and dated datasets | pending permission | Genuine annual reports FY23+; dated 2026 snapshot | New regime, short history, constrained legal market |
| 2 | SCW-006 | Orange County FL monthly TDT collections | pending permission | Strong release-specific PDFs, at least 2019–2026 | Lagged, hotel/theme-park-heavy, not Airbnb-specific |
| 3 | SCW-004 | Vancouver STR business licences | pending permission | Historical event dates and folder years, but current extract | Status survivorship; no historical snapshots proven |
| 4 | SCW-010 | NYC annual STR enforcement reports | pending permission | Annual append-only reports 2016–2024 | Annual policy effort may not equal supply withdrawal |
| 5 | SCW-007 | Hawaiʻi monthly TAT liability by district | rejected | Excellent monthly vintages 1997–2026 | Automation and commercial use explicitly prohibited |
| 6 | SCW-002 | New Orleans STR permit applications | pending permission | Application/issue/expiry events from 2017 | Public-at-cutoff timing and current-status survivorship unresolved |
| 7 | SCW-001 | Austin active STR counts | inconclusive | Historical chart label only | Underlying query may be broken/deleted |
| 8 | SCW-003 | New Orleans STR adjudication hearings | pending permission | Event dates from 2018; portal created 2022 | Backfill/revised workflow and policy endogeneity |
| 9 | SCW-008 | San Diego active STRO licences | prospective only | None; active-only snapshot from 2023 | No issue date, overwritten stock, avoidable PII fields |
| 10 | SCW-009 | Recreation.gov availability calendars | pending permission / prospective only | None | Undocumented availability interface and no archive |

The numerical component scores are in `edge_scorecard.csv`. Ranking breaks ties by historical usability and permission outcome, not novelty.

## Historical versus prospective readiness

**Backtestable now and collectible now:** none. No candidate has both defensible historical availability and a passed autonomous permission gate.

**Archive-proven but permission-blocked:** SCW-005, SCW-006, and SCW-010. These are the only serious historical-pilot candidates because their separate reports/snapshots are real vintages rather than a present-day reconstruction.

**Historical event dates but vintage-unverified:** SCW-002, SCW-003, and SCW-004. They must not enter a historical test until prompt publication or archived extracts are proven.

**Prospective-only:** SCW-008 and SCW-009, subject to permission resolution. SCW-001 remains inconclusive until a stable underlying dataset is recovered. SCW-007 is rejected under current terms.

## Best three conditional historical pilots

1. **SCW-006 — Orange County TDT.** Economic advantage: a release-specific, realized lodging-receipt measure in a globally important leisure market. Primary formula: for the latest collection month `m` whose original report was released strictly before cutoff, `ln(TDT_m) - ln(TDT_m-12)`. One sensitivity: the analogous three-month trailing-sum log growth. Main risk: it is lagged and hotel/theme-park-heavy.
2. **SCW-005 — NYC registration reports.** Economic advantage: direct legal host-supply formation under an unusually binding rule. Primary formula: `active_registrations_r / active_registrations_r-1 - 1` using the latest two annual reports both published strictly before cutoff. One sensitivity: `(granted + renewals_granted - refused - revoked) / (applications + renewals)` from the latest eligible report. Main risk: too few post-regime observations and too small a legal home-share base.
3. **SCW-010 — NYC enforcement reports.** Economic advantage: direct regulatory-friction vintages back to 2016. Primary formula: `ln(1 + STR_summonses_y) - ln(1 + STR_summonses_y-1)` using annual reports released strictly before cutoff. One sensitivity: `STR_summonses_y / STR_complaints_y`. Main risk: annual enforcement effort may reflect staffing or policy rather than economically material supply removal.

These three remain conditional on exact permission resolution. SCW-002 and SCW-004 are watch-list substitutes if historical publication semantics can be proven; current extracts alone are insufficient.

## Moonshot prospective collectors

- **SCW-009 federal reservation scarcity:** fixed multi-park facility panel, fixed 7/14/30/60/90-day lead buckets, daily sold-out share. Start only with documented availability access and affirmative terms/robots permission.
- **SCW-008 San Diego STRO snapshots:** daily aggregate counts by tier/planning area and expiration bucket, with row-level personal/contact/location data discarded immediately. Start only after the exact CSV path clears robots.

## Credentials and cost

No environment variable is required for the retained access methods, and no authenticated API was accessed. RIDB may offer authenticated metadata services, but its documented API does not solve reservation availability and was not used. No paid source, trial, Bloomberg request, or credential sync was initiated.

## Audit trail

- `candidate_edge_registry.csv` contains mechanism, coverage, timing, vintage, rights, leakage, formulas, and failure conditions.
- `edge_scorecard.csv` contains all eight ex-ante score components.
- `permission_and_license_audit.csv` and `lane_preflight.csv` preserve exact paths, terms/robots evidence, and fail-closed decisions.
- `historical_archive_matrix.csv` distinguishes event dates from genuine vintages and estimates guidance-cutoff coverage.
- `tiny_sample_manifest.csv` records every no-sample decision and stop reason.
- `preflight_assessment.py` constructs each `ScrapeCandidate` and calls `assess_scrape_candidate`.

E0 is complete for this lane. Stop here pending the lead's source-selection decision.
