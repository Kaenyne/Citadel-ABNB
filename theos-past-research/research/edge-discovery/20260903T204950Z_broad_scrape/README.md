# Broad free-source alternative-data acquisition

Run ID: `20260903T204950Z_broad_scrape`

## Outcome

The run acquired and normalized aggregate observations from official, free public-data sources covering platform guest nights, regional platform activity, total tourism nights, legal STR registration and enforcement, airport passengers, accommodation pricing, and international travellers.

The user-requested minimum is measured as successfully parsed, timestamped, numeric observations after validation—not as page visits or attempted HTTP requests. The final validated count is written to `processed/validation.json`.

## Important interpretation

This run creates a broad operating-data sample, not an earnings-event sample and not demonstrated alpha. Rows within the same geography, provider, or month are correlated. Except for the current UK CAA release, the downloaded files are current provider snapshots; historical reference periods must not be represented as original historical publication vintages. The conservative `first_available_at_utc` is therefore the collection timestamp for prospective use.

No source is promoted for forecasting. Promotion requires a separately approved point-in-time experiment showing incremental guidance-residual value over the public seasonal and management-policy baseline.

## Files

- `source_manifest.csv`: source, licence, access method, forecast linkage, and point-in-time treatment.
- `acquisition_log.csv`: successful requests and stopped or rejected attempts.
- `raw/`: immutable downloaded payloads and metadata.
- `processed/raw_file_manifest.csv`: byte counts, SHA-256 checksums, and capture timestamps.
- `processed/valid_observations.csv`: unified validated observations.
- `processed/rejected_observations.csv`: rejected rows with reasons.
- `processed/source_summary.csv`: coverage summary by source.
- `processed/validation.json`: deterministic validation result.
- `guidance_linkage.csv`: proposed operating-to-guidance bridge and falsification conditions.
- `process_scrapes.py`: deterministic normalizer and validator.
- `verify_scrapes.py`: independent row-count, uniqueness, source-coverage, licence-field, and raw SHA-256 integrity checks.

## Reproduce and verify

Run `python3 process_scrapes.py`, followed by `python3 verify_scrapes.py`, from this directory. The verifier exits non-zero if any required integrity check fails.

## Attribution

- Eurostat statistical data are reused with attribution under the Eurostat reuse notice.
- Toronto data contain information licensed under the Open Government Licence – Toronto.
- DataSF airport data are published under the Open Data Commons Public Domain Dedication and License.
- Statistics Canada data are adapted from the named tables under the Statistics Canada Open Licence; this does not constitute Statistics Canada endorsement.
- UK CAA statistical data require attribution and may not be sold to a third party; retained use is internal analysis only.
