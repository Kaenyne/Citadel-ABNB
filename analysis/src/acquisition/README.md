# Alt-data acquisition

Reusable acquisition layer for the ABNB pitch. Stdlib-only HTTP plus `duckdb` for
querying. No third-party HTTP client, so it runs anywhere the repo venv runs.

## Modules

| Module | Purpose |
|---|---|
| `fetch.py` | HTTP with retry/backoff, request pacing, and **fault classification** |
| `integrity.py` | SHA-256 plus structural validation (gzip/zip/csv/json), rejects stub responses |
| `sources/inside_airbnb.py` | Inside Airbnb index parsing and download planning |
| `run_*.py` | One runner per source; each appends to its own log in `data/manifests/` |

## The two rules that matter

**1. Classify every failure.** `fetch.classify()` splits failures into
`source-restriction` (401/402/403/404/410/451 - log it and stop, never retry or
route around) and `local-fault` (everything else - fix and retry, 3x with backoff).

This is not bureaucracy. During this work three separate "access denied" results
turned out to be bugs in our own code, not the source:

- Socrata returned 404 on every municipal dataset because its catalog API federates
  across all Socrata domains - we were requesting NYC dataset IDs from SF's host.
- Harvard Dataverse returned 403 on every file because we passed the API token as a
  `?key=` query parameter instead of the `X-Dataverse-key` header.
- Argentina and Hungary Inside Airbnb URLs raised because non-ASCII path segments
  (`ciudad-autónoma-de-buenos-aires`) need percent-encoding.

Rule of thumb: **uniform failure across a whole source is almost always the client.
Scattered failure is the source.** Inside Airbnb's 403s were scattered by country,
so those were real and are respected.

**2. Validate before trusting a 200.** `integrity.validate()` rejects any `.csv.gz`
under 2,048 bytes. Common Crawl served an HTTP 200 with a 511-byte body for one
Airbnb page - a stub, not data. A naive pipeline would have counted it as success.

## Running

```bash
source .venv/bin/activate
export FRED_API_KEY=...            # free key: fredaccount.stlouisfed.org/apikey
export DATAVERSE_API_TOKEN=...     # optional
python analysis/src/acquisition/run_macro.py
python analysis/src/acquisition/run_municipal.py
```

Bulk downloads write outside the repo (external volume) - only manifests are committed.
Every runner is resumable: re-running skips work already recorded in its log.
