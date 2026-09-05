# Curated import provenance

Snapshot date: 2026-09-04.

This package is a curated working-tree snapshot, not a Git subtree or
submodule. It preserves reviewable code, derived research, metadata, and
reproducibility inputs while deliberately excluding assets that are licensed,
raw, binary, cache-generated, or larger than the team’s 50 MiB boundary.

| Source branch | Source commit | Captured contribution |
| --- | --- | --- |
| `main` | `cebd7f3a3fca93dd92f7a04ee3692ec809990505` | Alternative-data research, forecasting, transcript-derived facts, edge discovery, and global-lodging analysis. |
| `abnb-guidance-intelligence` | `580b7b9b981b1c8fab617eaae63f52692e3f180b` | Guidance contracts, extraction, normalized guidance datasets, documentation, and tests. |

## Exclusion decision

The snapshot excludes the 23 FactSet CallStreet PDFs and 23 cleaned full-text
transcripts; the approximately 334 MB observation panel; every raw
global-lodging download; source ZIP payloads; and guidance Parquet files when
their CSV twins are tracked. It also excludes caches, environments, Git and
linked-worktree metadata, editable-install metadata, secrets, local paths, and
LaTeX build intermediates. Exclusion from Git does not remove an asset from the
research record: its logical path, size, checksum, replacement, and retrieval
guidance are preserved in a CSV manifest.

## Manifest files

- `restricted-data-manifest.csv` has one checksummed row for each excluded
  licensed PDF and cleaned Markdown transcript. The tracked transcript index is
  the inventory and checksum-validation reference.
- `omitted-data-manifest.csv` has one checksummed row for the oversized panel,
  every raw global-lodging download, every source ZIP payload, and each guidance
  Parquet with its tracked CSV replacement.
- `source-boundary-inventory.csv` has one row for every file in the complete
  plan-defined main and guidance source boundaries. Each row records source and
  destination checksums where applicable, a classification, and an existing
  replacement or deterministic retrieval/rebuild reference.

## Rebuild manifests

Run from the package root with authorized local source snapshots represented by
logical placeholders:

```bash
.venv/bin/python scripts/build_import_manifests.py \
  --source-root SOURCE_RESEARCH \
  --guidance-root GUIDANCE_SOURCE \
  --output-root research/provenance

.venv/bin/python scripts/build_import_manifests.py \
  --source-root SOURCE_RESEARCH \
  --guidance-root GUIDANCE_SOURCE \
  --output-root research/provenance \
  --check
```

Reconcile or verify the complete source boundary with:

```bash
.venv/bin/python scripts/reconcile_source_boundary.py \
  --source-root SOURCE_RESEARCH \
  --guidance-root GUIDANCE_SOURCE \
  --project-root .

.venv/bin/python scripts/reconcile_source_boundary.py \
  --source-root SOURCE_RESEARCH \
  --guidance-root GUIDANCE_SOURCE \
  --project-root . \
  --check
```
