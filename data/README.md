# Data

| File | Source | Pulled by | Date | Notes |
|---|---|---|---|---|
| processed/abnb_daily_close.csv | Yahoo Finance daily closes (ABNB), via yfinance | Krish (Claude Code) | 2026-09-05 | Date, Close, 10 Dec 2020 to 4 Sep 2026 (1,440 sessions). Input to the major-moves screen. |
| processed/abnb_major_moves_events.csv | Derived from abnb_daily_close.csv plus same-day QQQ, BKNG, EXPE moves; triggers from shareholder letters, call transcripts and same-day press | Krish (Claude Code) | 2026-09-05 | 41 close-to-close moves of 7% or more, each attributed macro/industry vs company-specific with headline and KPI detail. Attribution is hand-checked, not scripted. See research/notes/2026-09-05_abnb-major-moves.md. |
| processed/abnb_earnings_reactions.csv | Theo's guidance dataset (`theos-past-research/research/guidance/data/normalized/market_returns.csv`, Nasdaq closes vs QQQ) | Krish (Claude Code) | 2026-09-05 | 1/5/20-session ABNB, QQQ and excess returns for all 23 prints Q4 2020 to Q2 2026. Rebuild with `python analysis/src/abnb_from_theo_guidance.py`. Q2 2026 20-session window incomplete at Theo's 3 Sep cutoff. |
| processed/abnb_revenue_guidance_vs_actual.csv | Theo's guidance dataset (`guidance_items.csv`, `quarterly_actuals.csv`, from SEC-filed shareholder letters) | Krish (Claude Code) | 2026-09-05 | Next-quarter revenue guide range, midpoint, actual, beat vs midpoint and vs top, Q4 2021 to Q3 2026 (20 numeric guides). Same rebuild script. |
| processed/abnb_edgar_quarterly_kpis.csv | SEC EDGAR XBRL companyfacts, CIK 1559720 | Theo (Claude Code) | 2026-09-05 | 20 quarterly revenue + 23 deferred-revenue points, 2020Q1-2026Q2. Public domain. Rebuild: `python analysis/src/acquisition/run_edgar_filings.py`. |
| processed/abnb_filing_kpis.csv | ABNB 10-Q/10-K primary documents (SEC EDGAR) | Theo (Claude Code) | 2026-09-05 | 368 KPI sentences from 14 filings 2023Q1-2026Q2, tagged nights_booked/gbv/adr/rnpl, 50 carrying figures. Evidence-grade not series-grade: the clean KPI tables are HTML tables, not prose. Public domain. |
| manifests/*.csv | Acquisition provenance for every file pulled | Theo (Claude Code) | 2026-09-05 | Append-only logs: source, URL, HTTP status, byte count, SHA-256, licence tier. Bulk data itself lives on an external volume - see below. |
| processed/inside_airbnb_city_snapshots.csv, inside_airbnb_like_for_like.csv, inside_airbnb_host_concentration.csv | Inside Airbnb `listings.csv.gz` dumps (CC-BY 4.0): 13 cities, 168 dumps Dec 2022 to Aug 2026, discovered from Wayback captures of the get-the-data page plus daily CDN probes (manifest `data/raw/inside_airbnb/manifest.csv`; raw 2.6 GB gitignored) | Krish (Claude Code) | 2026-09-05 | Per-dump city metrics with `price_basis` and `partial_scope` flags (the 2026 dumps switched price to a fee-inclusive stay quote and the Dec 2025 to May 2026 monthlies are partial); matched-listing pairs, sequential and year-ago (retention, same-listing price change on one price basis, reviews LTM change, exit/add mix); top-25 hosts per city. Rebuild: `py -3.13 analysis/src/inside_airbnb_supply_panel.py all` (needs pyarrow). Write-up: research/notes/2026-09-05_inside-airbnb-supply-panel.md. Complements Theo's current-dump cohort below. |

`raw/` is gitignored except this log - put the actual files in the shared Drive if they're large or licensed, and record them here.
`processed/` files should be reproducible by running something in `analysis/src/`.

## Alt-data cohort (2026-09-05, Theo)

Bulk files are **not** in the repo - too large for git, per CONTRIBUTING. They live on an
external volume and are fully described by `data/manifests/`, with a SHA-256 for every file.

| Cohort | Scope | Size | Licence |
|---|---|---|---|
| Inside Airbnb current | 120 markets incl. **all 34 US**, listings + calendar + reviews | ~10 GB | CC BY 4.0 |
| Municipal STR registries | 25 datasets, 17 portals, 109,343 rows. Austin daily active-STR counts (527 dates); California TOT, 482 cities x 8 fiscal years | 28 MB | Open government |
| Eurostat `tour_ce_*` | Platform-sourced guest nights/stays, 32 countries, 2018-2026 monthly, NUTS 1/2/3 + cities | 6.8 MB | Eurostat re-use |
| FRED | 10 macro series incl. CPI lodging-away-from-home (ADR proxy) and trade-weighted USD | 1.1 MB | Public domain |
| SEC EDGAR | XBRL companyfacts + 14 10-Q/10-K primary documents | 20 MB | Public domain |
| Zenodo / Figshare / Dataverse | Academic replication packages | small | Per-record |

**Not committed, by design:** FactSet transcripts and Bloomberg terminal exports are licensed
and live in the private shared Drive, per CONTRIBUTING. They appear in the manifests as
references with `license_tier=licensed_norestribute` so provenance stays complete, but no
licensed content is in this public repo.

**Known blockers (lawful, not worked around):**
- Harvard Dataverse AirDNA-derived sets (Venice, Reykjavik, Boston MSA daily) require a
  Guestbook form response - must be completed manually in a browser.
- Inside Airbnb retired snapshots: ~39% return HTTP 403. Country-consistent, verified with
  paced retries as a source decision, logged and respected.
- TSA passenger volumes returns 403 to non-browser clients; FRED air revenue passenger miles
  is used instead rather than spoofing a user agent.
