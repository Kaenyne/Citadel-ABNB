# ABNB 50-source free alternative-data panel

Run ID: `20260903T211121Z_50_source_expansion`

## Outcome

This run expands the prior nine-source panel to exactly 50 nonempty official datasets. It adds 41 distinct Eurostat products covering collaborative-platform activity, accommodation demand and capacity, hotel occupancy, commercial flights, air passengers, airport pairs, and route connectivity.

The additions produced 590,949 validated numeric observations. Together with the 33,347 observations from the referenced baseline run, the consolidated manifest covers 624,296 observations.

## What “source” means

A source is a distinct official dataset or published data product with its own dataset code and endpoint. It is not a webpage visit, a query variation, or an individual row. The 41 additions share Eurostat as provider and therefore must not be treated as 41 independent information channels.

## Permission and point-in-time treatment

Eurostat permits reuse of statistical data for commercial or non-commercial purposes with source acknowledgement. The official notice captured in `metadata/eurostat_copyright_notice.html` governs the 41 additions. All sources in the consolidated manifest are free, and no personal data are retained.

The downloaded data are current provider snapshots. Historical reference periods are not original historical release vintages. Every added observation is conservatively marked `current_snapshot_prospective_only`, with first availability equal to this run’s collection time.

## Files

- `source_manifest_50.csv`: the consolidated set of exactly 50 sources.
- `source_summary_50.csv`: validated observation coverage for every source.
- `raw/`: 41 new official JSON-stat payloads.
- `metadata/eurostat_toc_20260903.txt`: official catalogue snapshot used to resolve dataset titles and metadata.
- `metadata/eurostat_copyright_notice.html`: captured official reuse notice.
- `processed/new_observations.csv`: 590,949 normalized observations from the 41 additions.
- `processed/new_source_manifest.csv`: source manifest for the 41 additions only.
- `processed/raw_file_manifest.csv`: exact acquisition URLs, byte counts, SHA-256 hashes, timestamps, and numeric row counts.
- `processed/validation_50.json`: deterministic build result.
- `build_50_source_panel.py`: reproducible normalizer and consolidation script.
- `verify_50_source_panel.py`: independent streaming integrity verifier.

## Reproduce and verify

Run `python3 build_50_source_panel.py`, followed by `python3 verify_50_source_panel.py`, from this directory. The verifier exits non-zero if the 50-source gate, row integrity, uniqueness, free-source policy, or raw-file checks fail.

## Research use

The expansion increases breadth but does not establish market edge. Many observations are nested, overlapping, revised, and highly correlated. Forecast promotion requires predeclared features, cutoff-safe release timestamps, walk-forward testing against management guidance, and incremental residual improvement over the public seasonal baseline.
