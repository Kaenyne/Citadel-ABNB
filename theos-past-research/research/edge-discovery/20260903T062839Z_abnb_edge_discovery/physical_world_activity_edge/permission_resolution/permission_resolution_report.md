# Physical-world permission-resolution continuation

## Agent hierarchy

1. **ABNB Edge-Data Research Orchestrator** — main Codex task; owns orchestration, user communication, and the final decision.
2. **abnb_alt_data** — permanent research lead; owns canonical governance, point-in-time methodology, reconciliation, and combined artifacts.
3. **physical_world_activity_edge** — permission-resolution owner for the eight retained physical-lane sources.
4. **supply_scarcity_web_edge** — separate supply/scarcity lane; not used here.

## Outcome

Exactly eight retained physical-lane IDs were evaluated. TfL and CDOT were neither included nor requested. The `abnb-forecasting` skill's audit boundary was applied: this continuation establishes permission and evidence eligibility only and does not create or update an ABNB forecast.

The append-only permission manifest has **52 rows**: 26 original official URLs plus exactly one preregistered retry row for each sandbox failure. There were **43 unique permission GET attempts**: 26 sandbox attempts that all failed with DNS `URLError`, followed by 17 of the 26 one-time escalated retries. The provider batch returned 14 HTTP 200 responses and three HTTP 403 responses; outcome classification was 13 completed evidence pages and four stops, including the HTTP-200 Melbourne CAPTCHA marker. Nine later retries were not sent because the linked source had already reached a stop condition. All 17 provider responses were cached and checksummed. With the preserved NYC data payload, the directory contains 18 cached response bodies. The shared NOAA policy URL was deduplicated for HMS and MarineCadastre, so per-source linked counts in the structured findings intentionally sum above the unique network total.

After cached evidence review and the final reconciliation correction, all eight exact data paths were reconstructed as `ScrapeCandidate` objects and rerun through `assess_scrape_candidate`. **No source is `allowed=true`.** NYC 311 was initially treated as allowed because its robots file supplies a crawl delay and does not list `/resource/` among its disallows. That interpretation was superseded: without an explicit `Allow` for `/resource/`, robots silence remains `unclear`. DP-PW-001 is preserved rather than concealed: the one preregistered request used a server-side `count(*)` projection for a single calendar day, transported no row-level or personal fields, and returned HTTP 200 with a one-row, one-field `request_count` schema. No further data request was made or is permitted. The payload is a present-day aggregate response, not a historical vintage and not an ABNB signal test.

WSF did not gain lawful access: its robots rules permit the registered landing-page and PDF paths, but the cached WSDOT open-data policy supports public access without clearly authorizing automation. No WSF report or data payload was requested. The frozen H-004 replay therefore remains **0 eligible events out of 23** and explicitly `not_testable`; its existing event file was not rebuilt or altered.

## Per-source resolution

| Source | Terms | Robots | Data-path gate | Data requests | E1 disposition | Resolution |
|---|---|---|---:|---:|---|---|
| NASA Black Marble | Unclear after policy HTTP 403 | Unclear; robots URL redirected to Earthdata Login | false | 0 | `WATCH_PROSPECTIVELY` | Authentication remains blocked; no credentials or data accessed. |
| NOAA HMS smoke | Unclear after shared policy HTTP 403 | Unclear; only `User-agent` and `Sitemap`, no affirmative path guidance | false | 0 | `CONTROL_ONLY` | Permission and original-vintage evidence unresolved. |
| WSF ferry ridership | Unclear for automation | Allowed for registered paths | false | 0 | `INCONCLUSIVE` | H-004 remains `not_testable`, 0/23 eligible. |
| NPS visitor use | Allowed; public-domain reuse and official GET API docs | Disallowed: `Disallow: /` | false | 0 | `WATCH_PROSPECTIVELY` | No data request; current API also lacks historical vintages. |
| FTA NTD ridership | Unclear | Unclear after robots HTTP 403 | false | 0 | `CONTROL_ONLY` | Source stopped; no policy, metadata, or data request. |
| MarineCadastre AIS | Unclear after shared NOAA policy HTTP 403 | Unclear; source stopped before robots GET | false | 0 | `WATCH_PROSPECTIVELY` | No metadata or data request after stop. |
| NYC 311 | Allowed for application/feed use | Unclear; crawl delay and unrelated disallows do not explicitly allow `/resource/` | false | 1 | `REJECT` | DP-PW-001 completed under the superseded interpretation and is preserved; no further request. |
| Melbourne pedestrian counts | Undefined terms | Disallowed for `/api/` | false | 0 | `WATCH_PROSPECTIVELY` | Cached terms response triggered conservative CAPTCHA marker; no further request. |

## Provider stops and no-retry behavior

- NASA data-policy URL: HTTP 403; NASA stopped, and the auth-document retry was not sent.
- Shared NOAA data-policy URL: HTTP 403; HMS and MarineCadastre stopped, and their remaining metadata/robots retries were not sent.
- FTA robots URL: HTTP 403; the remaining FTA permission pages were not sent.
- Melbourne terms URL: HTTP 200 but the raw HTML contained a CAPTCHA marker; the dataset-metadata retry was not sent. The visible cached terms text independently states that domain terms have not been defined, and robots explicitly disallows `/api/`.

No provider stop was retried. No authentication, cookies, personal data, environment values, paid source, Airbnb-controlled source, OTA, or commercial booking engine was accessed.

## Cached evidence and checksums

`permission_recon_retry_results.csv` is the authoritative ledger for all 17 cached permission responses, including safe effective URL, UTC timestamps, status, content type, relative cache path, and SHA-256. Key evidence includes:

- WSF robots: `cache/permission_recon_retry/PR-PW-R001.txt`, SHA-256 `773fb8d35bb9a39d35335ee6db8dc5c912d2aacbfb823152d9c61cd647dd902d`.
- WSF open-data policy: `cache/permission_recon_retry/PR-PW-R002.html`, SHA-256 `dbdf7eba811c628d22df19ddf28f5bcd12c69237496755e653fef5d0c629b686`.
- NPS robots: `cache/permission_recon_retry/PR-PW-R010.txt`, SHA-256 `133e4db054e73a10017a1f429c80c35cd5bfa9c3a1aba581b364ecc459c48a4b`.
- NYC robots: `cache/permission_recon_retry/PR-PW-R021.txt`, SHA-256 `0cb268a68e4fc210b4b7391392a87b19ac4c79e59704c6276620c5ec0efa0cde`; it has no explicit `Allow` for `/resource/`, so the corrected status is `unclear`.
- NYC terms: `cache/permission_recon_retry/PR-PW-R022.html`, SHA-256 `c1da5afe9ece362f57e0f351ff20e954f046a173c3a0d643b4c100d846977e33`.
- NYC dataset metadata: `cache/permission_recon_retry/PR-PW-R023.json`, SHA-256 `a88a99dc69f17a16a936a0249d35c9ba9325c2ba9bd89e02c14a52f622ac1927`.
- NYC aggregate data probe: `cache/data_probe/DP-PW-001.json`, SHA-256 `c84303069da97fd855fdf52d7a7814ce717976b358f439e21136eb4ffb60714e`.
- Melbourne robots: `cache/permission_recon_retry/PR-PW-R024.txt`, SHA-256 `3ad4d84d142bf7b82e0e1902ee2f74e2c5bfaadc34401575f3f9d3486ef4eba2`.

The other response paths and hashes, including all 403 bodies, remain preserved in the retry ledger. `data_probe_results.csv` records the sole data request's exact safe URL, UTC timestamps, status, type, payload hash, endpoint, schema, license conclusion, and vintage limitation.

## Point-in-time conclusion

Permission resolution did not convert any retained physical source into a historical ABNB feature. No exact data path is finally allowed. NYC's preserved privacy-safe schema probe occurred under a superseded robots interpretation and remains historically ineligible. WSF, the only frozen physical hypothesis, still has no lawful source values or exact initial-publication evidence. The correct H-004 outcome remains `not_testable`, not zero, neutral, hit, miss, or a negative alpha result.
