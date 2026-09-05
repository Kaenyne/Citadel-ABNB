# Theo's Past Research Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Theo Machado's complete policy-compliant ABNB research snapshot under `theos-past-research/` and open a reviewed pull request against the team repository's `main` branch.

**Architecture:** Build a self-contained nested Python project from the source `main` working tree, then integrate the complementary `abnb-guidance-intelligence` branch by content. Preserve restricted and oversized assets through checksummed manifests, normalize final artifacts under one `outputs/` tree, and enforce the import boundary with automated tests and a repository audit command.

**Tech Stack:** Python 3.12, setuptools, pytest, pandas, pydantic, openpyxl, PyYAML, requests, scikit-learn, pyarrow, Git, GitHub CLI

**Spec:** `docs/superpowers/specs/2026-09-04-theos-past-research-import-design.md`

## Global Constraints

- Work only on `codex/theos-past-research-import`; never commit directly to `main`.
- The destination path is exactly `theos-past-research/`.
- Treat the source checkout and linked worktree as read-only; do not move, rewrite, or delete their files or branches.
- Do not commit the 23 FactSet CallStreet PDFs or the 23 cleaned full-text Markdown transcripts.
- Do not commit any file larger than 50 MiB, any `.parquet` file, raw global-lodging downloads, secrets, local absolute paths, caches, virtual environments, or LaTeX intermediates.
- Preserve source `main` commit `cebd7f3a3fca93dd92f7a04ee3692ec809990505` and guidance commit `580b7b9b981b1c8fab617eaae63f52692e3f180b` in tracked provenance.
- Leave the team repository's existing `analysis/`, `data/`, `deck/`, `docs/`, `model/`, and `research/` content unchanged except for the approved migration spec and plan.
- The only team-root product change is one discoverability row in `README.md`.
- The pull request must not merge itself.

## File Structure Map

- `theos-past-research/README.md`: package entry point, setup, research map, provenance, and restricted-data workflow.
- `theos-past-research/pyproject.toml`: combined dependency and package-discovery contract for all three Python packages.
- `theos-past-research/.gitignore`: nested safeguards for licensed text, secrets, oversized outputs, caches, and build files.
- `theos-past-research/src/abnb_alt_data/`: alternative-data logic plus import-manifest and repository-policy helpers.
- `theos-past-research/src/abnb_forecasting/`: macro-to-guidance packet and baseline logic.
- `theos-past-research/src/abnb_guidance/`: guidance intelligence, source controls, market reaction, and normalized storage.
- `theos-past-research/scripts/build_import_manifests.py`: reproducibly generate restricted and omitted-asset manifests from authorized local sources.
- `theos-past-research/scripts/validate_import.py`: verify the Git snapshot contains no prohibited files, secrets, or local paths.
- `theos-past-research/research/provenance/import-manifest.md`: source commits, capture boundary, and inclusion/exclusion record.
- `theos-past-research/research/provenance/restricted-data-manifest.csv`: one row per omitted PDF and cleaned transcript.
- `theos-past-research/research/provenance/omitted-data-manifest.csv`: one row per oversized, raw-global, zip, or Parquet asset omitted from Git.
- `theos-past-research/outputs/`: final reports, workbooks, figures index, and compact reproducibility inputs.
- `theos-past-research/tests/test_import_manifest.py`: deterministic manifest generation tests.
- `theos-past-research/tests/test_import_policy.py`: import-boundary and file-policy tests.
- `README.md`: one link from the team workspace map to the imported package.

---

### Task 1: Import the Main Research Snapshot

**Files:**
- Create: `theos-past-research/.codex/**`
- Create: `theos-past-research/data/README.md`
- Create: `theos-past-research/docs/**`
- Create: `theos-past-research/research/**`
- Create: `theos-past-research/scripts/**`
- Create: `theos-past-research/src/abnb_alt_data/**`
- Create: `theos-past-research/src/abnb_forecasting/**`
- Create: `theos-past-research/tests/**`
- Create: `theos-past-research/.env.example`
- Create: `theos-past-research/.gitignore`
- Create: `theos-past-research/pyproject.toml`
- Create: `theos-past-research/uv.lock`

**Interfaces:**
- Consumes: the source `main` working tree rooted at `/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026`.
- Produces: a nested project snapshot without licensed, oversized, raw-global, generated-output, or machine-local files.

- [ ] **Step 1: Confirm source and destination identities**

Run from the team checkout:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git -C "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026" rev-parse main
git -C "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026" rev-parse abnb-guidance-intelligence
```

Expected: destination branch `codex/theos-past-research-import`; source SHAs exactly match the two Global Constraints; only the committed spec and this plan exist on the destination branch.

- [ ] **Step 2: Copy the approved main-working-tree boundary**

Run:

```bash
SOURCE_RESEARCH="/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026"
IMPORT_ROOT="$(pwd -P)/theos-past-research"
mkdir -p "$IMPORT_ROOT"
rsync -a \
  --exclude='/.git/' \
  --exclude='/.worktrees/' \
  --exclude='/.venv/' \
  --exclude='/.pytest_cache/' \
  --exclude='/.superpowers/' \
  --exclude='/.DS_Store' \
  --exclude='EARNING-TRANSCRIPTS/' \
  --exclude='data/licensed/earnings_transcripts/clean_md/' \
  --exclude='output/' \
  --exclude='outputs/' \
  --exclude='src/*.egg-info/' \
  --exclude='**/__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='*.parquet' \
  --exclude='*.zip' \
  --exclude='*.aux' \
  --exclude='*.fdb_latexmk' \
  --exclude='*.fls' \
  --exclude='*.log' \
  --exclude='*.out' \
  --exclude='research/edge_discovery/20260903T211121Z_50_source_expansion/processed/new_observations.csv' \
  "$SOURCE_RESEARCH/" "$IMPORT_ROOT/"
mv "$IMPORT_ROOT/research/edge_discovery" "$IMPORT_ROOT/research/edge-discovery"
```

Expected: source files remain unchanged; the destination contains `abnb_alt_data` and `abnb_forecasting`; restricted paths and output trees are absent.

- [ ] **Step 3: Verify the copy boundary before staging**

Run:

```bash
find theos-past-research -type f -size +50M -print
find theos-past-research -type f \( -name '*.parquet' -o -name '*.pyc' -o -name '*.zip' -o -name '*.aux' -o -name '*.log' -o -name '*.out' \) -print
find theos-past-research -type d \( -name '.venv' -o -name '__pycache__' -o -name '.pytest_cache' -o -name '.worktrees' \) -print
test ! -e theos-past-research/EARNING-TRANSCRIPTS
test ! -e theos-past-research/data/licensed/earnings_transcripts/clean_md
```

Expected: all `find` commands print nothing and both `test` commands exit zero.

- [ ] **Step 4: Commit the base snapshot**

```bash
git add theos-past-research
git diff --cached --check
git commit -m "Import Theo ABNB research snapshot for team review"
```

Expected: one commit containing only `theos-past-research/` base-snapshot files.

### Task 2: Integrate Guidance Intelligence and Reconcile Configuration

**Files:**
- Create: `theos-past-research/.codex/agents/abnb_guidance_intelligence.toml`
- Create: `theos-past-research/src/abnb_guidance/**`
- Create: `theos-past-research/research/guidance/**`
- Create: `theos-past-research/tests/test_guidance_*.py`
- Create: `theos-past-research/docs/superpowers/plans/2026-09-02-abnb-guidance-intelligence.md`
- Create: `theos-past-research/docs/superpowers/specs/2026-09-02-abnb-guidance-intelligence-design.md`
- Modify: `theos-past-research/pyproject.toml`
- Modify: `theos-past-research/uv.lock`
- Modify: `theos-past-research/.codex/agents/abnb_guidance_intelligence.toml`
- Modify: `theos-past-research/research/guidance/AGENT_PLAYBOOK.md`
- Test: `theos-past-research/tests/test_guidance_agent_config.py`
- Test: `theos-past-research/tests/test_guidance_leakage.py`

**Interfaces:**
- Consumes: guidance worktree at `/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026/.worktrees/abnb-guidance-intelligence`.
- Produces: importable `abnb_guidance` package and guidance research rooted at `research/guidance/`.

- [ ] **Step 1: Copy complementary guidance paths without collisions**

```bash
GUIDANCE_SOURCE="/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026/.worktrees/abnb-guidance-intelligence"
IMPORT_ROOT="$(pwd -P)/theos-past-research"
cp "$GUIDANCE_SOURCE/.codex/agents/abnb_guidance_intelligence.toml" "$IMPORT_ROOT/.codex/agents/"
rsync -a --exclude='__pycache__/' --exclude='*.py[cod]' "$GUIDANCE_SOURCE/src/abnb_guidance/" "$IMPORT_ROOT/src/abnb_guidance/"
rsync -a --exclude='*.parquet' --exclude='__pycache__/' --exclude='*.py[cod]' "$GUIDANCE_SOURCE/research/abnb_guidance/" "$IMPORT_ROOT/research/guidance/"
cp "$GUIDANCE_SOURCE/docs/superpowers/plans/2026-09-02-abnb-guidance-intelligence.md" "$IMPORT_ROOT/docs/superpowers/plans/"
cp "$GUIDANCE_SOURCE/docs/superpowers/specs/2026-09-02-abnb-guidance-intelligence-design.md" "$IMPORT_ROOT/docs/superpowers/specs/"
rsync -a --exclude='test_agent_config.py' --exclude='test_leakage.py' --exclude='__pycache__/' --exclude='*.py[cod]' "$GUIDANCE_SOURCE/tests/" "$IMPORT_ROOT/tests/"
cp "$GUIDANCE_SOURCE/tests/test_agent_config.py" "$IMPORT_ROOT/tests/test_guidance_agent_config.py"
cp "$GUIDANCE_SOURCE/tests/test_leakage.py" "$IMPORT_ROOT/tests/test_guidance_leakage.py"
```

Expected: no existing main-snapshot test is overwritten; no Parquet or cache file is copied.

- [ ] **Step 2: Write the failing integrated-layout assertions**

Add these assertions to `tests/test_guidance_agent_config.py`:

```python
ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / ".codex/agents/abnb_guidance_intelligence.toml"
PLAYBOOK = ROOT / "research/guidance/AGENT_PLAYBOOK.md"


def test_guidance_role_uses_imported_research_path() -> None:
    instructions = tomllib.loads(ROLE.read_text(encoding="utf-8"))["developer_instructions"]
    assert "research/guidance/AGENT_PLAYBOOK.md" in instructions
    assert "research/abnb_guidance/" not in instructions
```

- [ ] **Step 3: Run the focused test to verify the old path fails**

Run from `theos-past-research/`:

```bash
python -m venv .venv
.venv/bin/python -m pip install 'pytest>=8'
.venv/bin/python -m pytest tests/test_guidance_agent_config.py -v
```

Expected: FAIL because the imported role and test still reference `research/abnb_guidance/`.

- [ ] **Step 4: Reconcile paths and project metadata**

Use exact replacements in the active role, playbook, validation log, and guidance-agent test:

```text
research/abnb_guidance/ -> research/guidance/
research/abnb_guidance -> research/guidance
```

Do not rewrite the historical design or implementation plan; their original paths are part of provenance.

Replace `pyproject.toml` with:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "abnb-research-toolkit"
version = "0.1.0"
description = "Theo Machado's historical ABNB research toolkit"
requires-python = ">=3.12"
dependencies = [
  "matplotlib",
  "numpy",
  "openpyxl",
  "pandas",
  "pyarrow",
  "pydantic>=2",
  "PyYAML",
  "requests",
  "scikit-learn",
]

[project.optional-dependencies]
dev = ["pytest>=8"]
scraping = ["scrapling>=0.4.15,<0.5"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
filterwarnings = [
  "ignore:datetime.datetime.utcfromtimestamp\\(\\) is deprecated:DeprecationWarning:dateutil.tz.tz",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

Run `uv lock` to regenerate `uv.lock` from this combined dependency contract.

- [ ] **Step 5: Install and test all three packages**

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests/test_guidance_agent_config.py tests/test_guidance_leakage.py -v
.venv/bin/python -c 'import abnb_alt_data, abnb_forecasting, abnb_guidance'
```

Expected: focused tests pass and all three imports exit zero.

- [ ] **Step 6: Commit the branch integration**

```bash
git add theos-past-research
git diff --cached --check
git commit -m "Integrate guidance intelligence into Theo research archive"
```

Expected: the commit adds only guidance content plus reconciled nested-project configuration.

### Task 3: Support Metadata-Only Validation

**Files:**
- Modify: `theos-past-research/src/abnb_alt_data/validation.py`
- Modify: `theos-past-research/scripts/validate_project.py`
- Modify: `theos-past-research/tests/test_validation.py`

**Interfaces:**
- Consumes: `validate_project(root: Path, expected_transcript_count: int = 23)`.
- Produces: `validate_project(root: Path, expected_transcript_count: int = 23, require_licensed_text: bool = True)` and CLI flag `--metadata-only`.

- [ ] **Step 1: Write failing tests for a Git-safe clone**

Add to `tests/test_validation.py`:

```python
def test_metadata_only_validation_allows_absent_restricted_text(tmp_path: Path) -> None:
    build_project(tmp_path)
    (tmp_path / MARKDOWN).unlink()

    findings = validate_project(
        tmp_path,
        expected_transcript_count=1,
        require_licensed_text=False,
    )

    assert not [finding for finding in findings if finding.code in {"missing_markdown", "invalid_guidance"}]
    assert main([
        "--root",
        str(tmp_path),
        "--expected-transcripts",
        "1",
        "--metadata-only",
    ]) == 0
```

- [ ] **Step 2: Verify the new API fails before implementation**

```bash
.venv/bin/python -m pytest tests/test_validation.py -q
```

Expected: FAIL because `require_licensed_text` and `--metadata-only` do not exist.

- [ ] **Step 3: Implement the metadata-only mode**

Thread `require_licensed_text` through `_validate_transcripts`, `_validate_guidance`, and `validate_project`. When it is false:

```python
if not markdown_path.exists():
    if require_licensed_text:
        findings.append(ValidationFinding("missing_markdown", f"missing {markdown_value}"))
    continue
```

Skip guidance-anchor validation when licensed text is unavailable, while still validating the guidance CSV schema and the 23-row transcript index. Add this parser flag:

```python
parser.add_argument(
    "--metadata-only",
    action="store_true",
    help="validate tracked metadata without requiring licensed transcript text",
)
```

Call `validate_project(..., require_licensed_text=not args.metadata_only)`.

Add `--relative` to the staged-path Git check so `_validate_staging` receives paths relative to the nested project root when it runs inside the team repository.

- [ ] **Step 4: Run validation tests and the Git-safe validator**

```bash
.venv/bin/python -m pytest tests/test_validation.py -q
.venv/bin/python scripts/validate_project.py --root . --expected-transcripts 23 --metadata-only
```

Expected: both commands pass; the CLI prints `ABNB alt-data project validation passed`.

- [ ] **Step 5: Commit metadata-only validation**

```bash
git add theos-past-research/src/abnb_alt_data/validation.py theos-past-research/scripts/validate_project.py theos-past-research/tests
git diff --cached --check
git commit -m "Validate transcript metadata without redistributing licensed text"
```

### Task 4: Generate Provenance and Enforce Import Policy

**Files:**
- Create: `theos-past-research/src/abnb_alt_data/import_policy.py`
- Create: `theos-past-research/scripts/build_import_manifests.py`
- Create: `theos-past-research/scripts/validate_import.py`
- Create: `theos-past-research/tests/test_import_manifest.py`
- Create: `theos-past-research/tests/test_import_policy.py`
- Create: `theos-past-research/research/provenance/import-manifest.md`
- Create: `theos-past-research/research/provenance/restricted-data-manifest.csv`
- Create: `theos-past-research/research/provenance/omitted-data-manifest.csv`

**Interfaces:**
- Produces: `sha256_file(path: Path) -> str`.
- Produces: `build_restricted_rows(source_root: Path, transcript_index: Path) -> list[dict[str, str]]`.
- Produces: `build_omitted_rows(source_root: Path, guidance_root: Path) -> list[dict[str, str]]`.
- Produces: `collect_violations(project_root: Path, candidate_paths: Iterable[Path]) -> list[str]`.
- Produces: CLI exit code `0` for a compliant snapshot and `1` with one line per violation otherwise.

- [ ] **Step 1: Write failing manifest tests**

Create deterministic fixtures in `tmp_path` and assert:

```python
rows = build_restricted_rows(source_root, transcript_index)
assert {row["asset_type"] for row in rows} == {"licensed_pdf", "licensed_markdown"}
assert all(len(row["sha256"]) == 64 for row in rows)
assert {row["tracking_status"] for row in rows} == {"excluded_restricted"}
```

For omitted assets:

```python
rows = build_omitted_rows(source_root, guidance_root)
assert {row["reason"] for row in rows} == {
    "over_50_mib",
    "raw_global_lodging_download",
    "zip_source_payload",
    "parquet_csv_twin_included",
}
```

- [ ] **Step 2: Write failing policy tests**

Test a safe file plus each prohibited class:

```python
violations = collect_violations(
    project_root,
    [
        project_root / "research/source_registry.csv",
        project_root / "EARNING-TRANSCRIPTS/example.pdf",
        project_root / "data/licensed/earnings_transcripts/clean_md/example.md",
        project_root / "results.parquet",
        project_root / ".venv/token.txt",
    ],
)
assert len(violations) == 4
assert not any("source_registry.csv" in violation for violation in violations)
```

Add separate tests for a file over `50 * 1024 * 1024`, text containing `/Users/`, text containing `C:\\Users\\`, and a non-template file containing `API_KEY=real-value`.

- [ ] **Step 3: Verify both new test modules fail**

```bash
.venv/bin/python -m pytest tests/test_import_manifest.py tests/test_import_policy.py -v
```

Expected: FAIL because `abnb_alt_data.import_policy` does not exist.

- [ ] **Step 4: Implement manifest generation**

Use CSV field order:

```python
MANIFEST_FIELDS = (
    "asset_type",
    "source_branch",
    "logical_path",
    "reason",
    "bytes",
    "sha256",
    "tracked_replacement",
    "rebuild_command",
    "tracking_status",
)
```

Generate two restricted rows per transcript-index record: the PDF path is `Path("EARNING-TRANSCRIPTS") / row["source_filename"]`, and the cleaned Markdown path is `Path(row["markdown_path"])`. Generate omitted rows for the exact 334 MB panel, every file below the raw global-lodging directory, every source `.zip`, and every guidance `.parquet`; use the CSV twin as `tracked_replacement` for Parquet files.

The CLI requires explicit `--source-root`, `--guidance-root`, and `--output-root` paths and writes both CSVs with UTF-8, `newline=""`, sorted logical paths, and Unix line endings.

- [ ] **Step 5: Implement the repository audit**

Reject these path components or suffixes:

```python
BLOCKED_PARTS = {
    ".venv", ".pytest_cache", ".superpowers", ".worktrees", "__pycache__"
}
BLOCKED_SUFFIXES = {
    ".pyc", ".pyo", ".parquet", ".zip", ".aux", ".fdb_latexmk", ".fls", ".log", ".out"
}
MAX_BYTES = 50 * 1024 * 1024
```

Also reject `EARNING-TRANSCRIPTS/`, `data/licensed/earnings_transcripts/clean_md/`, editable-install directories ending in `.egg-info`, and absolute `/Users/` or `C:\\Users\\` paths in text files. Outside `.env.example`, reject nonblank assignments to `API_KEY`, `AWS_SECRET_ACCESS_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `FACTSET_API_KEY`, and `FRED_API_KEY`. Scan only `.py`, `.md`, `.toml`, `.csv`, `.json`, `.ndjson`, `.yaml`, `.yml`, `.txt`, `.tex`, and `.mjs` as text. `scripts/validate_import.py` obtains the candidate set with `git ls-files --cached --others --exclude-standard -- theos-past-research` from the team root.

- [ ] **Step 6: Generate the real manifests and provenance note**

```bash
.venv/bin/python scripts/build_import_manifests.py \
  --source-root "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026" \
  --guidance-root "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026/.worktrees/abnb-guidance-intelligence" \
  --output-root research/provenance
```

Write `import-manifest.md` with the two exact source SHAs, snapshot timestamp `2026-09-04`, the curated-snapshot decision, excluded classes, manifest descriptions, and the command above with logical placeholders `SOURCE_RESEARCH` and `GUIDANCE_SOURCE` instead of Theo's absolute path.

- [ ] **Step 7: Run focused tests and audit**

```bash
.venv/bin/python -m pytest tests/test_import_manifest.py tests/test_import_policy.py -v
.venv/bin/python scripts/validate_import.py
```

Expected: tests pass and the audit prints `Theo past research import policy passed`.

- [ ] **Step 8: Commit provenance and policy enforcement**

```bash
git add theos-past-research/src/abnb_alt_data/import_policy.py theos-past-research/scripts theos-past-research/tests theos-past-research/research/provenance
git diff --cached --check
git commit -m "Document omitted research assets and enforce import policy"
```

### Task 5: Consolidate Reviewable Outputs and Documentation

**Files:**
- Create: `theos-past-research/outputs/reports/**`
- Create: `theos-past-research/outputs/workbooks/**`
- Create: `theos-past-research/outputs/figures/README.md`
- Create: `theos-past-research/outputs/reproducibility/us-europe-guidance/**`
- Create: `theos-past-research/README.md`
- Modify: `theos-past-research/data/README.md`
- Modify: `theos-past-research/.gitignore`
- Modify: `README.md`
- Test: `theos-past-research/tests/test_documentation.py`
- Test: `theos-past-research/tests/test_repository_policy.py`

**Interfaces:**
- Consumes: source `output/`, source `outputs/01a065f3-9f9d-7c33-a034-621059cc8c6f/`, and the guidance request workbook.
- Produces: team-review artifacts without raw global data or licensed source material.

- [ ] **Step 1: Write documentation and ignore-policy assertions**

Extend `tests/test_documentation.py` to assert the package README contains all of:

```python
for phrase in (
    "Historical research",
    "abnb_alt_data",
    "abnb_forecasting",
    "abnb_guidance",
    "metadata-only",
    "restricted-data-manifest.csv",
    "omitted-data-manifest.csv",
    "does not replace the team thesis",
):
    assert phrase.casefold() in readme.casefold()
```

Extend `tests/test_repository_policy.py` to assert raw global downloads, `.parquet`, `.zip`, LaTeX intermediates, and the 334 MB panel path are ignored while `.env.example`, provenance CSVs, final reports, and review workbooks remain trackable.

- [ ] **Step 2: Run the focused tests to verify documentation is incomplete**

```bash
.venv/bin/python -m pytest tests/test_documentation.py tests/test_repository_policy.py -v
```

Expected: FAIL because the new package README and expanded ignore rules do not exist.

- [ ] **Step 3: Copy and classify approved outputs**

```bash
cd "$(git rev-parse --show-toplevel)"
SOURCE_RESEARCH="/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/CAIMANES/CITADEL 2026"
GUIDANCE_SOURCE="$SOURCE_RESEARCH/.worktrees/abnb-guidance-intelligence"
IMPORT_ROOT="$(pwd -P)/theos-past-research"
mkdir -p "$IMPORT_ROOT/outputs/reports" "$IMPORT_ROOT/outputs/workbooks" "$IMPORT_ROOT/outputs/figures" "$IMPORT_ROOT/outputs/reproducibility/us-europe-guidance"
cp "$SOURCE_RESEARCH/output/pdf/abnb_macro_to_equity_ic_brief.pdf" "$IMPORT_ROOT/outputs/reports/"
cp -R "$SOURCE_RESEARCH/output/overleaf/abnb_macro_to_equity_ic_brief_overleaf" "$IMPORT_ROOT/outputs/reports/"
cp "$SOURCE_RESEARCH/outputs/01a065f3-9f9d-7c33-a034-621059cc8c6f/"*.xlsx "$IMPORT_ROOT/outputs/workbooks/"
cp "$SOURCE_RESEARCH/outputs/01a065f3-9f9d-7c33-a034-621059cc8c6f/"*.inspect.ndjson "$IMPORT_ROOT/outputs/workbooks/"
cp "$SOURCE_RESEARCH/outputs/01a065f3-9f9d-7c33-a034-621059cc8c6f/"*.csv "$IMPORT_ROOT/outputs/reproducibility/us-europe-guidance/"
cp "$SOURCE_RESEARCH/outputs/01a065f3-9f9d-7c33-a034-621059cc8c6f/"*.mjs "$IMPORT_ROOT/outputs/reproducibility/us-europe-guidance/"
cp "$GUIDANCE_SOURCE/outputs/abnb-guidance-intelligence/ABNB_Bloomberg_Request.xlsx" "$IMPORT_ROOT/outputs/workbooks/ABNB_consensus_data_request_template.xlsx"
```

Expected: final/reporting assets are present; no `output/` directory, UUID output directory, raw global download, or LaTeX intermediate is present.

If an `.inspect.ndjson` file contains an absolute local path, omit that inspection file and add a row to `omitted-data-manifest.csv` with reason `absolute_local_path`; do not rewrite machine-generated inspection evidence.

- [ ] **Step 4: Verify the request workbook is a blank template**

Run with the nested environment:

```bash
.venv/bin/python -c 'from openpyxl import load_workbook; from pathlib import Path; p=Path("outputs/workbooks/ABNB_consensus_data_request_template.xlsx"); w=load_workbook(p, read_only=True, data_only=True); populated=[v for s in w.worksheets for row in s.iter_rows() for c in row if (v:=c.value) not in (None, "")]; print(len(populated)); w.close()'
```

Expected: the workbook contains headings/instructions only and no vendor-returned consensus values. If any vendor-returned values appear, omit the workbook and add it to `omitted-data-manifest.csv` with reason `licensed_terminal_output`.

- [ ] **Step 5: Write package documentation and nested ignore rules**

The package README must include:

```bash
cd theos-past-research
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
python scripts/validate_project.py --root . --expected-transcripts 23 --metadata-only
python scripts/validate_import.py
```

Document the three research streams, source SHAs, outputs map, manifest locations, and private acquisition/checksum workflow. State exactly: `This historical research does not replace the team thesis, model, or shared research folders.`

The nested `.gitignore` must include:

```gitignore
.venv/
.pytest_cache/
.superpowers/
.worktrees/
__pycache__/
*.py[cod]
*.egg-info/
.DS_Store
.env
.env.*
!.env.example
EARNING-TRANSCRIPTS/
data/licensed/earnings_transcripts/clean_md/
research/edge-discovery/20260903T211121Z_50_source_expansion/processed/new_observations.csv
outputs/**/raw/
*.parquet
*.zip
*.aux
*.fdb_latexmk
*.fls
*.log
*.out
```

Add a `Where things live` row to the team root README:

```markdown
| `theos-past-research/` | Theo's historical ABNB research, reproducibility code, and provenance manifests | Theo |
```

- [ ] **Step 6: Run focused documentation and policy tests**

```bash
.venv/bin/python -m pytest tests/test_documentation.py tests/test_repository_policy.py -v
.venv/bin/python scripts/validate_import.py
```

Expected: all focused tests pass and the import audit passes.

- [ ] **Step 7: Commit outputs and documentation**

```bash
git add README.md theos-past-research
git diff --cached --check
git commit -m "Document and publish reviewable Theo research artifacts"
```

### Task 6: Verify the Full Snapshot and Open the Pull Request

**Files:**
- Modify only if verification reveals an in-scope defect: files already listed in Tasks 1-5.
- Verify: every tracked path in the branch diff.

**Interfaces:**
- Consumes: completed `theos-past-research/` snapshot and root README link.
- Produces: pushed branch and reviewable GitHub pull request targeting `main`.

- [ ] **Step 1: Run the complete nested test suite**

From `theos-past-research/`:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/validate_project.py --root . --expected-transcripts 23 --metadata-only
.venv/bin/python scripts/validate_import.py
.venv/bin/python -c 'import abnb_alt_data, abnb_forecasting, abnb_guidance'
```

Expected: zero test failures, both validators pass, and imports exit zero.

- [ ] **Step 2: Validate branch hygiene from the team root**

```bash
git diff --check main...HEAD
git diff --name-only main...HEAD | awk '!/^theos-past-research\// && $0 != "README.md" && $0 != "docs/superpowers/specs/2026-09-04-theos-past-research-import-design.md" && $0 != "docs/superpowers/plans/2026-09-04-theos-past-research-import.md"'
git ls-files -z | xargs -0 stat -f '%z %N' | awk '$1 > 52428800 {print}'
git status --short
```

Expected: diff check passes; the boundary command and size command print nothing; status is clean.

- [ ] **Step 3: Review the final diff and commit history**

```bash
git diff --stat main...HEAD
git log --oneline --decorate main..HEAD
git diff -- README.md
```

Expected: the diff contains the approved nested package, root README link, spec, and plan only; commit messages explain each import stage.

- [ ] **Step 4: Push the branch**

```bash
git push -u origin codex/theos-past-research-import
```

Expected: the branch is available on `Kaenyne/Citadel-ABNB` without modifying remote `main`.

- [ ] **Step 5: Open the pull request**

```bash
gh pr create \
  --repo Kaenyne/Citadel-ABNB \
  --base main \
  --head codex/theos-past-research-import \
  --title "Import Theo's ABNB research archive" \
  --body "$(printf '%s\n' '## Summary' '- adds a self-contained `theos-past-research/` archive spanning alternative data, forecasting, and guidance intelligence' '- preserves licensed transcripts and oversized/raw-global datasets through checksummed manifests without committing restricted content' '- consolidates reviewable reports, workbooks, code, tests, and reproducibility inputs' '' '## Verification' '- full nested pytest suite' '- metadata-only project validation' '- import policy audit' '- 50 MiB tracked-file boundary and restricted-path scan' '' '## Review notes' '- binary PDFs and workbooks are review artifacts and follow one-editor-at-a-time coordination' '- this PR does not replace the team thesis, model, or shared research folders')"
```

Expected: GitHub returns a pull-request URL targeting `main`; do not merge it.

- [ ] **Step 6: Report the PR and exclusions**

Report the PR URL, branch, verification results, source SHAs, restricted transcript count, omitted data count, largest tracked file, and confirmation that the source checkout and team `main` remain unchanged.
