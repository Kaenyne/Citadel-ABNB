# Validation Log

- Research cutoff: `2026-09-02T23:59:59-04:00`
- Python: `3.12.7`
- Initial agent contract: `/opt/anaconda3/bin/python -m pytest tests/test_agent_config.py -v` — 3 passed.
- Typed records and storage: `/opt/anaconda3/bin/python -m pytest tests/test_records.py tests/test_storage.py -v` — 10 passed.
- Source and excerpt controls: `/opt/anaconda3/bin/python -m pytest tests/test_sources.py tests/test_extraction.py -v` — 8 passed.
- First full suite: `/opt/anaconda3/bin/python -m pytest -v` — 21 passed.
- Target, information-clock, tone, and return arithmetic: `/opt/anaconda3/bin/python -m pytest tests/test_tone.py tests/test_market.py tests/test_leakage.py tests/test_features.py -v` — 16 passed.
- Official history, transcript manifest, management evidence, and deterministic dataset build: `/opt/anaconda3/bin/python -m pytest tests/test_official_history.py tests/test_transcript_manifest.py tests/test_management_evidence.py tests/test_dataset_build.py tests/test_storage.py -q` — 18 passed.
- Normalized dataset validation after build: `validate_dataset(research/guidance)` — 0 findings.
- User-supplied transcript pinpoint verification: 2/2 stored excerpts matched their source PDFs; no transcript full text was retained.
- Public Nasdaq market-return tests: `/opt/anaconda3/bin/python -m pytest tests/test_market.py tests/test_market_data.py -q` — 9 passed.
- Public Nasdaq event-window ingest: 69 rows created for 23 events across 1-, 5-, and 20-session windows; 68 observed and 1 explicitly missing because the Q2 2026 20-session window was incomplete at the research cutoff.
- Normalized dataset validation after market-return ingest: `validate_dataset(research/guidance)` — 0 findings.
- Bloomberg request workbook: six sheets rendered and visually inspected; XLSX archive integrity passed; formula/error scan found no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, or `#N/A` values. The workbook remains explicitly unexecuted pending separate paid-data approval.
- Checkpoint full suite: `/opt/anaconda3/bin/python -m pytest -q` — 55 passed.
- Checkpoint normalized dataset validation: `PYTHONPATH=src /opt/anaconda3/bin/python -c ...` — 0 findings.
