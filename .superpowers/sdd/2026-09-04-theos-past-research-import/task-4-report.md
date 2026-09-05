# Task 4 — Provenance and import-policy report

## Status

Complete. The package now has deterministic omission manifests, a repository
boundary audit, focused behavior tests, and portable source provenance.

## Files

- `theos-past-research/src/abnb_alt_data/import_policy.py`
- `theos-past-research/scripts/build_import_manifests.py`
- `theos-past-research/scripts/validate_import.py`
- `theos-past-research/tests/test_import_manifest.py`
- `theos-past-research/tests/test_import_policy.py`
- `theos-past-research/research/provenance/import-manifest.md`
- `theos-past-research/research/provenance/restricted-data-manifest.csv`
- `theos-past-research/research/provenance/omitted-data-manifest.csv`

## RED / GREEN evidence

RED: after adding the two test modules, running
`.venv/bin/python -m pytest tests/test_import_manifest.py tests/test_import_policy.py -v`
failed at collection with `ModuleNotFoundError: No module named
'abnb_alt_data.import_policy'` in both modules.

GREEN: after the minimal manifest and policy implementation, the same command
reported `6 passed`. The oversized-file fixture initially used a nonexistent
`Path.truncate` method; it was corrected to truncate an opened file handle, and
the focused suite again reported `6 passed`.

## Generated manifests

- Restricted: 46 rows — 23 `licensed_pdf` and 23 `licensed_markdown`, all with
  64-character SHA-256 digests and `excluded_restricted` status.
- Omitted: 31 rows — one 334,408,167-byte observation panel, 17
  `raw_global_lodging_download` rows, two `zip_source_payload` rows, and 11
  `guidance_parquet` rows with tracked CSV twins.

The portable provenance note records snapshot date `2026-09-04`, source commits
`cebd7f3a3fca93dd92f7a04ee3692ec809990505` and
`580b7b9b981b1c8fab617eaae63f52692e3f180b`, the curated-snapshot decision,
and logical rebuild placeholders only.

## Commands and results

- Generated manifests with `scripts/build_import_manifests.py` against the two
  authorized read-only source snapshots. Hashing the cloud-backed 334 MB panel
  exceeded the interactive command window, so the same authorized read-only
  command ran in the background; it produced both CSVs with complete hashes.
- `.venv/bin/python -m pytest tests/test_import_manifest.py tests/test_import_policy.py -v`
  — `6 passed`.
- `.venv/bin/python scripts/validate_import.py` — `Theo past research import
  policy passed`.
- `git diff --check` — no output.
- Candidate-path size scan — largest candidate was `theos-past-research/uv.lock`
  at 315,041 bytes, below 50 MiB.
- Candidate-path absolute-path scan and restricted/raw/ZIP/Parquet filename scan
  — no prohibited tracked assets or local absolute paths.

## Self-review

Verified the required field order, 50 MiB threshold, blocked components and
suffixes, restricted transcript directories, text-suffix allowlist, absolute
path markers, secret-assignment exception for `.env.example`, and the required
Git candidate enumeration. Secret fixture strings are concatenated so the
tracked test source cannot trigger the audit it exercises.

## Concerns

The source snapshot is cloud-backed, so regeneration can take longer than a
normal local run while checksums are read. The generated manifests are complete
and do not embed local absolute paths or restricted payloads.
