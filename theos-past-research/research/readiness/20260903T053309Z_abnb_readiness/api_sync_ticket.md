# Free-API credential sync ticket

Run ID: `20260903T053309Z_abnb_readiness`  
Owner: `abnb_alt_data`  
Gate: Phase A ends after this ticket. No authenticated call is authorized until the user confirms the selected API IDs.

## Best no-key empirical signal

**FED_H10_ARCHIVE / H-001** needs no credential. It is the only selected source with genuine dated historical releases and strict-PIT replay coverage. Its 9 hits and 7 misses across 16 comparable events are descriptive and unstable across cohorts; they do not establish incremental forecast value.

## Ranked credential candidates

1. **FRED_ALFRED** — set `FRED_API_KEY`.
   - Signup: https://fred.stlouisfed.org/docs/api/api_key.html
   - Why sync: real-time periods and ALFRED vintages can add macro controls with defensible historical availability for supported series.
   - Smallest Phase-B smoke test: one sanitized `fred/series` metadata request for `DTWEXBGS`, confirming HTTP status, real-time fields, schema, and rate-limit behavior. It must not substitute FRED's current history for dated Board H.10 releases.

2. **BLS_PUBLIC_DATA_V2** — set `BLS_API_KEY`.
   - Signup: https://data.bls.gov/registrationEngine/
   - Why sync: increases the query history from 10 to 20 years and documented daily quota from 25 to 500. It does **not** solve the missing historical release-timestamp problem.
   - Smallest Phase-B smoke test: one series (`CUUR0000SEHB02`) for one calendar year, with the key supplied only in the request body and excluded from logs.

3. **NOAA_CDO_V2** — set `NOAA_CDO_TOKEN`.
   - Signup: https://www.ncdc.noaa.gov/cdo-web/token
   - Why sync: enables a later, preregistered weather-disruption control after fixed destinations/stations are approved.
   - Smallest Phase-B smoke test: one dataset-metadata request with the token in the header. Do not collect weather history until the source family and conservative lag rule are approved.

The tracked `.env.example` contains those three names with empty values. Put any selected real values only in ignored local `.env`; never send or display them. Continue with:

`Credentials synced for API IDs: <approved API IDs>. Continue Phase B of the same readiness run. Do not display or return any credential value.`

Not recommended for this sync: Ticketmaster (no historical inventory snapshots), BEA/Census/EIA (weak or slow initial mechanisms), Google Ads (high access burden and no vintages), and Google Trends alpha (restricted rolling-history access).

