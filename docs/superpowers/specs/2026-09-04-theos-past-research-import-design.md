# Theo's Past Research Import Design

- **Date:** 2026-09-04
- **Destination repository:** `https://github.com/Kaenyne/Citadel-ABNB.git`
- **Destination branch:** `codex/theos-past-research-import`
- **Destination path:** `theos-past-research/`

## Purpose

Import Theo Machado's complete ABNB research project into the team repository as a self-contained, reviewable research package. The import must preserve useful code, tests, documentation, derived data, research runs, and final artifacts while complying with the source project's licensing controls and the team repository's file-size and paid-source policies.

The import is a curated working-tree snapshot rather than a subtree or submodule. Detailed source provenance is recorded in the package, while the team repository receives a compact history and a normal pull-request review flow.

## Source State

The package combines two source lines:

| Source | Captured state | Contribution |
|---|---|---|
| `theomachado05/airbnb-citadel-2026`, `main` | Commit `cebd7f3a3fca93dd92f7a04ee3692ec809990505` plus the reviewed working-tree changes present during import | Alternative-data research, macro-to-guidance forecasting, transcript-derived facts, readiness work, edge discovery, global lodging analysis, reports, scripts, and tests |
| `theomachado05/airbnb-citadel-2026`, `abnb-guidance-intelligence` | Commit `580b7b9b981b1c8fab617eaae63f52692e3f180b` | Guidance data contracts, extraction and market-reaction tooling, normalized guidance datasets, schemas, documentation, workbook, and tests |

The original checkout, its linked worktree, and its branches remain unchanged. The import records source paths and commit identities but does not embed the source repository's `.git` directory or linked worktree metadata.

## Destination Architecture

```text
theos-past-research/
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── .codex/
│   ├── agents/
│   └── skills/
├── src/
│   ├── abnb_alt_data/
│   ├── abnb_forecasting/
│   └── abnb_guidance/
├── scripts/
├── tests/
├── docs/
├── research/
│   ├── transcripts/
│   ├── forecasting/
│   ├── guidance/
│   ├── readiness/
│   ├── edge-discovery/
│   └── provenance/
├── data/
│   └── README.md
└── outputs/
    ├── reports/
    ├── workbooks/
    ├── figures/
    └── reproducibility/
```

The package is independently runnable after changing into `theos-past-research/`. Its relative paths must not depend on the team repository root. The team repository's existing `analysis/`, `data/`, `deck/`, `docs/`, `model/`, and `research/` areas remain untouched except for this migration specification.

## Import Rules

### Included

- Python packages from all three research streams.
- Project scripts and all non-cache tests and fixtures.
- Agent configurations and the project-local forecasting skill.
- Research memos, registries, schemas, validation records, point-in-time evidence, checksums, and derived fact tables.
- Audited forecasting and edge-discovery run folders, excluding restricted or oversized payloads.
- Final PDFs, presentation-ready figures, review workbooks, and reproducibility scripts that satisfy team repository policy.
- An import manifest that identifies the source repositories, branches, commits, capture date, and inclusion rules.
- Restricted-data and large-file manifests that let authorized teammates identify and verify local/private assets without reproducing them in Git.

### Excluded

- `.git/`, `.worktrees/`, `.venv/`, `.pytest_cache/`, `.superpowers/`, `__pycache__/`, `*.pyc`, `.DS_Store`, and editable-install metadata such as `*.egg-info/`.
- Secrets, local environment files, credentials, private keys, and editor settings.
- The 23 FactSet CallStreet PDFs under `EARNING-TRANSCRIPTS/`.
- The 23 cleaned full-text Markdown transcripts under `data/licensed/earnings_transcripts/clean_md/`.
- `research/edge_discovery/20260903T211121Z_50_source_expansion/processed/new_observations.csv`, which is approximately 334 MB and exceeds GitHub's hard file limit and the team's 50 MB policy.
- Raw global lodging downloads and any other raw or binary payload above 50 MB.
- LaTeX intermediates such as `*.aux`, `*.fdb_latexmk`, `*.fls`, `*.log`, and `*.out`.

Exclusion from Git does not mean exclusion from the research record. Each restricted or oversized research asset is represented by tracked metadata and retrieval guidance.

## Licensed Transcript Handling

`research/transcripts/transcript_index.csv` remains the canonical tracked transcript inventory. It already records provider, source filename, SHA-256 checksum, page count, word count, quarter, event date, and `user_provided_restricted` license status.

The imported `data/README.md` will state that authorized teammates must obtain the underlying FactSet CallStreet material through their approved institutional or private team channel. The README will describe the expected local directories and the checksum-validation command without naming Theo's absolute local filesystem path.

The package's `.gitignore` will explicitly block both canonical PDF and cleaned-full-text locations. Derived fact tables, management themes, reported metrics, guidance facts, and compact test fixtures remain versioned because they do not reproduce the licensed transcripts.

## Oversized and Raw Data Handling

The 334 MB observation panel will be omitted and listed in `research/provenance/large-file-manifest.csv` with its logical path, byte size, checksum, producing script, source manifest, and validation record. The import retains `build_50_source_panel.py`, `verify_50_source_panel.py`, the source manifests, and `validation_50.json` so an authorized teammate can reconstruct and validate the panel from permitted inputs.

Raw third-party downloads are included only when redistribution is permitted and each file is below the team's limit. When permission is unclear, the payload is omitted and its existing acquisition log, source manifest, permission audit, and checksum record are retained. The team repository's restrictive policy wins over the source snapshot whenever the two differ.

## Branch Integration

The guidance branch is integrated by content, not by merging its Git history. Complementary paths are copied into the package. Conflicting project files are reconciled as follows:

- `pyproject.toml` contains the union of runtime and test dependencies and includes all three packages.
- `.gitignore` combines source safeguards with the destination repository's restrictions.
- Agent-configuration tests are combined so all three agents are covered without duplicate test module names.
- Guidance schemas, normalized data, source manifests, and validation logs live under `research/guidance/`.
- `src/abnb_guidance/` and its tests retain their package names to avoid needless API changes.
- The Bloomberg request workbook is treated as a review workbook, not as a data source; its filename and surrounding documentation must not contain licensed Bloomberg output.

No branch is deleted or force-updated as part of this import.

## Output Consolidation

The source project's `output/` and `outputs/` directories become one `outputs/` hierarchy:

- `outputs/reports/` contains final rendered research briefs and their editable source packages.
- `outputs/workbooks/` contains team-review workbooks and their inspection metadata.
- `outputs/figures/` contains presentation-ready plots and preview images.
- `outputs/reproducibility/` contains generation scripts and compact machine-readable inputs that are not more naturally part of a research run folder.

LaTeX source needed to rebuild a final report is retained. Build logs and auxiliary files are not. Audited run packets remain under `research/forecasting/` or `research/edge-discovery/` when their directory context is part of the evidence trail.

## Documentation

The package `README.md` provides:

1. Scope and ownership of Theo's imported research.
2. A map of the three research streams.
3. Setup using the package's `pyproject.toml` and the team-supported Python environment.
4. Commands for validation and common report generation.
5. Restricted-data setup and checksum verification.
6. Source commit provenance and the snapshot date.
7. A warning that the package is historical research and does not replace the team's current thesis, model, or shared research folders.

The team root `README.md` receives one link to `theos-past-research/README.md`; no other shared team documentation is rewritten.

## Verification

Before the pull request is opened, the import must pass all of the following checks:

1. Install the nested project in a fresh virtual environment using its declared dependencies.
2. Run the combined test suite from `theos-past-research/`.
3. Run the repository-policy and validation scripts from the nested project root.
4. Confirm all three Python packages import successfully.
5. Scan tracked files for environment secrets, credentials, private keys, and absolute local paths.
6. Confirm no tracked file exceeds 50 MB.
7. Confirm no FactSet PDF, cleaned full-text transcript, `.parquet`, raw restricted payload, cache, virtual environment, or build intermediate is tracked.
8. Validate transcript index rows and checksums against Theo's unchanged local canonical PDFs without copying those PDFs into the destination repository.
9. Confirm the 334 MB panel and all other omitted assets appear in a provenance manifest.
10. Confirm the diff against the team `main` branch touches only `theos-past-research/`, the single root README link, and this migration specification.

If a check fails, the branch is not pushed until the failure is corrected or the affected artifact is excluded and documented.

## Pull Request

The change is delivered from `codex/theos-past-research-import` to `main`. The pull request will summarize the three research streams, list the restricted and oversized exclusions, report verification results, and call out binary workbooks or PDFs that require one-editor-at-a-time coordination.

The pull request will not merge itself. A teammate must review it under the destination repository's contribution policy.

## Acceptance Criteria

- `theos-past-research/` is understandable and runnable without reading the source repository.
- Useful material from the source `main` working tree and the seven unique guidance-branch commits is represented.
- Licensed transcript content and oversized/restricted payloads are absent from Git but fully represented by metadata and access instructions.
- Existing team work outside the approved import boundary is unchanged.
- The combined tests and repository-policy checks pass.
- A reviewable pull request targets the team repository's `main` branch.
