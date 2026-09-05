# ABNB Alternative-Data Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a permanent `abnb_alt_data` Codex agent, convert the 23 user-provided earnings-call PDFs into an ignored Markdown research corpus, and enforce a point-in-time workflow for testing alternative-data signals against transcript-derived management guidance.

**Architecture:** Keep proprietary PDFs and full converted text outside version control while tracking code, metadata, schemas, prompts, and derived research tables. A small Python package owns schemas, transcript conversion, timestamp eligibility, and project validation. The custom agent uses those controls to register sources and hypotheses before conducting expanding-window tests.

**Tech Stack:** Python 3.12 standard library, `pytest`, Poppler (`pdftotext` and `pdfinfo`), TOML via `tomllib`, Codex project agent configuration, and Scrapling only for later user-approved permitted collectors.

**Spec:** `docs/superpowers/specs/2026-09-02-abnb-alt-data-agent-design.md`

## Global Constraints

- Do not move, rename, rewrite, or commit files in `EARNING-TRANSCRIPTS/`.
- Do not commit converted full transcript text without explicit license approval.
- Do not use guidance issued on an earnings call as an input to a prediction made before that call.
- Reject any feature whose historical availability is blank, unverified, equal to, or later than the guidance cutoff.
- Preserve `[indiscernible]`; never infer missing speech, numbers, dates, or source provenance.
- Do not collect paid data or request Bloomberg data without user approval.
- Do not automate collection from Airbnb-controlled properties where terms prohibit it.
- Use only synthetic transcript excerpts in the test suite.
- Run the named failing test before each implementation step and the full suite before completion.

---

## Task 1: Establish the Python Package and Repository Safety Policy

**Files:**

- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `data/README.md`
- Create: `src/abnb_alt_data/__init__.py`
- Create: `tests/test_repository_policy.py`

- [ ] **Step 1: Write the failing repository-policy tests**

Create `tests/test_repository_policy.py` with tests that run `git check-ignore`
against representative proprietary paths and verify that research CSV paths are
not ignored:

```python
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def is_ignored(relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", relative_path], cwd=ROOT, check=False
    )
    return result.returncode == 0


def test_proprietary_transcripts_are_ignored() -> None:
    assert is_ignored("EARNING-TRANSCRIPTS/example.pdf")
    assert is_ignored("data/licensed/earnings_transcripts/clean_md/example.md")


def test_research_metadata_is_trackable() -> None:
    assert not is_ignored("research/transcripts/transcript_index.csv")
    assert not is_ignored("research/transcripts/guidance_facts.csv")
```

- [ ] **Step 2: Run the test and confirm the expected failure**

Run:

```bash
python3 -m pytest tests/test_repository_policy.py -q
```

Expected: failure because `.gitignore` and the package scaffold do not yet
exist.

- [ ] **Step 3: Add the minimal package and test configuration**

Create `pyproject.toml` with:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "abnb-alt-data"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

Create `.gitignore` with these project-specific rules:

```gitignore
.DS_Store
.pytest_cache/
__pycache__/
*.py[cod]
.superpowers/
EARNING-TRANSCRIPTS/
data/licensed/earnings_transcripts/clean_md/
```

Create `src/abnb_alt_data/__init__.py` with only a package docstring and
`__version__ = "0.1.0"`.

Document in `data/README.md` that source PDFs remain in
`EARNING-TRANSCRIPTS/`, converted Markdown is local licensed working data,
metadata and derived facts may be tracked, and no source may be collected until
its license and point-in-time status are recorded.

- [ ] **Step 4: Run the focused test**

Run:

```bash
python3 -m pytest tests/test_repository_policy.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Verify the PDF corpus is no longer shown as untracked**

Run:

```bash
git status --short
git check-ignore -v EARNING-TRANSCRIPTS/*.pdf
```

Expected: no individual PDF is listed by `git status`; `git check-ignore`
identifies the project rule.

- [ ] **Step 6: Commit the safety scaffold**

```bash
git add .gitignore pyproject.toml data/README.md src/abnb_alt_data/__init__.py tests/test_repository_policy.py
git commit -m "chore: establish alt-data repository safeguards"
```

---

## Task 2: Define and Materialize the Research Schemas

**Files:**

- Create: `src/abnb_alt_data/schemas.py`
- Create: `research/source_registry.csv`
- Create: `research/hypothesis_ledger.csv`
- Create: `research/transcripts/transcript_index.csv`
- Create: `research/transcripts/guidance_facts.csv`
- Create: `research/transcripts/reported_metrics.csv`
- Create: `research/transcripts/management_themes.csv`
- Create: `research/memos/.gitkeep`
- Create: `tests/test_schemas.py`

- [ ] **Step 1: Write schema tests before the constants exist**

In `tests/test_schemas.py`, import each field tuple and
`validate_csv_header`. Assert that the six CSV files have exactly the declared
headers and that each header has unique names:

```python
import csv
from pathlib import Path

from abnb_alt_data.schemas import CSV_SCHEMAS, validate_csv_header


ROOT = Path(__file__).resolve().parents[1]


def test_declared_schema_fields_are_unique() -> None:
    for fields in CSV_SCHEMAS.values():
        assert len(fields) == len(set(fields))


def test_tracked_csv_headers_match_schema() -> None:
    for relative_path, fields in CSV_SCHEMAS.items():
        validate_csv_header(ROOT / relative_path, fields)
```

- [ ] **Step 2: Run the schema tests and confirm import failure**

Run:

```bash
python3 -m pytest tests/test_schemas.py -q
```

Expected: collection error because `abnb_alt_data.schemas` does not exist.

- [ ] **Step 3: Implement canonical schema constants**

Create `src/abnb_alt_data/schemas.py` with immutable tuples and these exact
field orders:

```python
SOURCE_REGISTRY_FIELDS = (
    "rank", "source_id", "dataset", "provider", "economic_mechanism",
    "source_url", "access_method", "license", "collection_restrictions",
    "geographic_coverage", "unit_of_observation", "frequency",
    "history_start", "history_end", "publication_schedule",
    "publication_lag", "revision_policy", "vintage_available", "cost",
    "collection_timestamp_utc", "pit_evidence", "leakage_risk",
    "leakage_mitigation", "status", "citations", "analyst_notes",
)

HYPOTHESIS_FIELDS = (
    "hypothesis_id", "version", "registered_at_utc", "target",
    "prediction_horizon", "signal", "transformation", "expected_direction",
    "economic_mechanism", "geographic_aggregation", "cutoff_rule",
    "availability_rule", "baseline", "evaluation_metric", "minimum_evidence",
    "confounders", "failure_conditions", "result_status", "result_path",
)

TRANSCRIPT_INDEX_FIELDS = (
    "transcript_id", "ticker", "fiscal_period", "event_date", "event_at",
    "corrected_transcript_created_at", "pdf_creation_at", "published_at",
    "retrieved_at_utc", "indexed_at_utc", "point_in_time_usable_after",
    "availability_status", "source_provider", "source_filename",
    "source_sha256", "transcript_status", "license_status", "page_count",
    "word_count", "markdown_path",
)

GUIDANCE_FIELDS = (
    "guidance_id", "issuing_fiscal_period", "call_event_at", "available_at",
    "guided_period", "metric", "guidance_type", "value_low", "value_high",
    "value_midpoint", "qualitative_direction", "unit", "currency",
    "constant_currency_basis", "source_markdown", "source_turn_id",
    "indiscernible_affects_record", "extraction_status", "confidence",
    "analyst_notes",
)

REPORTED_METRIC_FIELDS = (
    "fact_id", "fiscal_period", "available_at", "metric", "reference_period",
    "value", "unit", "currency", "constant_currency_basis",
    "source_markdown", "source_turn_id", "confidence",
)

MANAGEMENT_THEME_FIELDS = (
    "theme_id", "fiscal_period", "available_at", "theme", "direction",
    "geography", "source_markdown", "source_turn_id", "confidence",
    "analyst_notes",
)
```

Add the exact path-to-schema mapping:

```python
CSV_SCHEMAS: dict[str, tuple[str, ...]] = {
    "research/source_registry.csv": SOURCE_REGISTRY_FIELDS,
    "research/hypothesis_ledger.csv": HYPOTHESIS_FIELDS,
    "research/transcripts/transcript_index.csv": TRANSCRIPT_INDEX_FIELDS,
    "research/transcripts/guidance_facts.csv": GUIDANCE_FIELDS,
    "research/transcripts/reported_metrics.csv": REPORTED_METRIC_FIELDS,
    "research/transcripts/management_themes.csv": MANAGEMENT_THEME_FIELDS,
}
```

Implement `validate_csv_header(path: Path, expected: Sequence[str]) -> None` and
`write_empty_csv(path: Path, fields: Sequence[str]) -> None` below the mapping.

`validate_csv_header` must raise `ValueError` containing the path, expected
header, and actual header. `write_empty_csv` must create parent directories and
write only the header; it must refuse to overwrite a nonempty file unless the
existing header already matches.

- [ ] **Step 4: Materialize the six empty tracked CSV templates**

Use a short one-time command that imports `CSV_SCHEMAS` and calls
`write_empty_csv` for each declared path. Do not manually duplicate the headers.

Run:

```bash
PYTHONPATH=src python3 -c 'from pathlib import Path; from abnb_alt_data.schemas import CSV_SCHEMAS, write_empty_csv; [write_empty_csv(Path(p), f) for p, f in CSV_SCHEMAS.items()]'
```

Create `research/memos/.gitkeep` with `apply_patch`.

- [ ] **Step 5: Run focused tests**

Run:

```bash
python3 -m pytest tests/test_schemas.py -q
```

Expected: all schema tests pass.

- [ ] **Step 6: Commit the schemas and templates**

```bash
git add src/abnb_alt_data/schemas.py research tests/test_schemas.py
git commit -m "feat: define alt-data research schemas"
```

---

## Task 3: Create the Permanent Codex Agent Contract

**Files:**

- Create: `.codex/agents/abnb_alt_data.toml`
- Create: `tests/test_agent_config.py`

- [ ] **Step 1: Write a failing TOML contract test**

Create `tests/test_agent_config.py` using `tomllib` and assert:

```python
def test_agent_configuration() -> None:
    config = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
    assert config["name"] == "abnb_alt_data"
    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "high"
    assert config["sandbox_mode"] == "workspace-write"
    assert config["description"].strip()
    instructions = config["developer_instructions"]
    for phrase in (
        "point-in-time", "source_registry.csv", "hypothesis_ledger.csv",
        "strictly before", "paid data", "Bloomberg", "negative",
        "EARNING-TRANSCRIPTS", "no more than three full transcripts",
    ):
        assert phrase.casefold() in instructions.casefold()
```

Also assert that the instructions ban invented values, prohibited automated
Airbnb collection, silent use of revised data, and unapproved delegation.

- [ ] **Step 2: Run the focused test and confirm missing-file failure**

Run:

```bash
python3 -m pytest tests/test_agent_config.py -q
```

Expected: failure because `.codex/agents/abnb_alt_data.toml` does not exist.

- [ ] **Step 3: Implement `.codex/agents/abnb_alt_data.toml`**

Use these required top-level scalar values, followed by the complete developer
instructions described below:

```toml
name = "abnb_alt_data"
description = "Institutional-quality point-in-time alternative-data research lead for Airbnb (NASDAQ: ABNB)."
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

The developer instructions must fully encode the approved design rather than
refer to chat history. Organize them into mission, required workflow, source
registry fields, hypothesis ledger fields, transcript/guidance rules,
point-in-time testing, approval gates, provenance, reporting, and scope budget.
Require the agent to:

1. read `research/transcripts/transcript_index.csv` before full transcripts;
2. load no more than three full transcripts unless explicitly asked;
3. treat guidance as a target and require features strictly before
   `available_at`;
4. compare against simple baselines with walk-forward validation;
5. record negative and inconclusive results;
6. stop for paid sources, Bloomberg, ambiguous permissions, or a new source
   family;
7. preserve source URL, retrieval timestamp, availability evidence, and
   citations;
8. refuse to invent missing values, dates, transcript words, or sources;
9. use at most three source families and six initial hypotheses;
10. avoid spawning or delegating unless the user explicitly asks.

- [ ] **Step 4: Parse and test the agent file**

Run:

```bash
python3 -m pytest tests/test_agent_config.py -q
python3 -c 'import tomllib; print(tomllib.load(open(".codex/agents/abnb_alt_data.toml", "rb"))["name"])'
```

Expected: tests pass and the command prints `abnb_alt_data`.

- [ ] **Step 5: Commit the agent configuration**

```bash
git add .codex/agents/abnb_alt_data.toml tests/test_agent_config.py
git commit -m "feat: add ABNB alternative-data agent"
```

---

## Task 4: Build the Deterministic FactSet PDF-to-Markdown Converter

**Files:**

- Create: `src/abnb_alt_data/transcripts.py`
- Create: `tests/fixtures/factset_sample.txt`
- Create: `tests/test_transcripts.py`

- [ ] **Step 1: Create a synthetic transcript fixture**

Write a short original fixture—not copied from the licensed PDFs—that contains:

- a synthetic FactSet-style cover and metadata block;
- repeated page headers, page numbers, and disclaimer text;
- `MANAGEMENT DISCUSSION SECTION` and `QUESTION AND ANSWER SECTION`;
- three named speaker turns;
- one `[indiscernible]` marker;
- a dotted separator line.

The fixture must be sufficient to test cleaning without including proprietary
speech.

- [ ] **Step 2: Write failing converter unit tests**

Test these public data structures:

```python
@dataclass(frozen=True)
class TranscriptSection:
    name: str
    turns: tuple[SpeakerTurn, ...]

@dataclass(frozen=True)
class TranscriptMetadata:
    transcript_id: str
    ticker: str
    fiscal_period: str
    event_date: str
    event_at: str | None
    corrected_transcript_created_at: str | None
    pdf_creation_at: str | None
    published_at: str | None
    retrieved_at_utc: str | None
    indexed_at_utc: str
    point_in_time_usable_after: str | None
    availability_status: str
    source_provider: str
    source_filename: str
    source_sha256: str
    transcript_status: str
    license_status: str
    page_count: int
    word_count: int
```

The public functions are `parse_pdfinfo(output: str) -> dict[str, str]`,
`parse_factset_metadata(raw_text, pdfinfo, source_path, retrieved_at,
indexed_at) -> TranscriptMetadata`, `clean_factset_text(raw_text,
transcript_id) -> tuple[TranscriptSection, ...]`, `render_markdown(metadata,
sections) -> str`, and `convert_pdf(pdf_path, output_dir, retrieved_at,
indexed_at, pdftotext_bin, pdfinfo_bin) -> dict[str, str]`.

Assert that:

- repeated headers, footer numbers, dotted separators, and disclaimers disappear;
- all speech remains in order;
- `[indiscernible]` remains verbatim;
- management/Q&A boundaries remain;
- turn IDs are stable and unique, for example
  `ABNB-2026Q2-MD-001` and `ABNB-2026Q2-QA-001`;
- unknown timestamps render as YAML `null`, not guessed values;
- PDF creation time is distinct from public availability;
- front matter contains source checksum and license status;
- calling the renderer twice with the same inputs returns identical bytes.

- [ ] **Step 3: Run the tests and confirm import failure**

Run:

```bash
python3 -m pytest tests/test_transcripts.py -q
```

Expected: collection error because the converter does not exist.

- [ ] **Step 4: Implement Poppler invocation and metadata parsing**

In `transcripts.py`, use `subprocess.run` with `check=True`,
`capture_output=True`, `text=True`, argument arrays, and no shell. Implement
`run_poppler(pdf_path: Path, pdftotext_bin: str = "pdftotext",
pdfinfo_bin: str = "pdfinfo") -> tuple[str, dict[str, str]]`.

Call `pdftotext -layout <pdf> -` and `pdfinfo <pdf>`. Compute SHA-256 by
streaming the PDF in chunks. Parse only metadata that the PDF/text actually
establishes. Leave exact call time, transcript publication, retrieval time, and
PIT usability blank when unverified. Store PDF creation metadata separately.

- [ ] **Step 5: Implement conservative text cleaning and stable turns**

Use line-oriented parsing with explicit patterns for page artifacts and section
labels. Do not globally normalize numbers or rewrite speech. Join wrapped lines
only within the same recognized speaker turn. A turn begins only when the
speaker marker is structurally recognized; ambiguous text stays attached to the
current turn.

Derive IDs as:

```python
f"{transcript_id}-{section_code}-{ordinal:03d}"
```

where section codes are `MD`, `QA`, and `OTHER`. Preserve source order.

- [ ] **Step 6: Render front matter and cited turns**

Render Markdown as UTF-8 with stable key order:

```markdown
---
transcript_id: ABNB-2026Q2
ticker: ABNB
fiscal_period: 2026Q2
event_date: "2026-08-06"
event_at: null
availability_status: unverified
source_provider: FactSet CallStreet
license_status: user_provided_restricted
---

# ABNB 2026Q2 Earnings Call

## Management discussion

<a id="ABNB-2026Q2-MD-001"></a>
### ABNB-2026Q2-MD-001 — Speaker Name, Role

Synthetic spoken text used only to illustrate the output format.
```

Do not introduce PyYAML solely for front matter; quote strings safely with
`json.dumps` and render absent values as `null`.

- [ ] **Step 7: Run converter unit tests**

Run:

```bash
python3 -m pytest tests/test_transcripts.py -q
```

Expected: all converter tests pass.

- [ ] **Step 8: Commit the converter**

```bash
git add src/abnb_alt_data/transcripts.py tests/fixtures/factset_sample.txt tests/test_transcripts.py
git commit -m "feat: convert licensed transcripts to cited markdown"
```

---

## Task 5: Add the Corpus Conversion CLI and Index All 23 Transcripts

**Files:**

- Create: `scripts/convert_transcripts.py`
- Create: `tests/test_convert_transcripts_cli.py`
- Modify: `research/transcripts/transcript_index.csv`
- Generate, ignored: `data/licensed/earnings_transcripts/clean_md/*.md`

- [ ] **Step 1: Write a failing CLI integration test**

The test should place two minimal generated PDFs or use a mocked Poppler runner
in a temporary source directory, invoke `main(argument_list)`, and assert:

- one Markdown file and one index row per PDF;
- rows are sorted by fiscal period and source filename;
- rerunning replaces generated outputs deterministically rather than appending
  duplicate rows;
- a duplicate fiscal period or duplicate transcript ID fails loudly;
- the source files are unchanged.

- [ ] **Step 2: Run the CLI test and confirm the expected failure**

Run:

```bash
python3 -m pytest tests/test_convert_transcripts_cli.py -q
```

Expected: failure because `scripts/convert_transcripts.py` does not exist.

- [ ] **Step 3: Implement the CLI**

Add arguments:

```text
--source-dir       default EARNING-TRANSCRIPTS
--output-dir       default data/licensed/earnings_transcripts/clean_md
--index            default research/transcripts/transcript_index.csv
--retrieved-at     optional ISO 8601 UTC; blank means unknown
--indexed-at       optional ISO 8601 UTC override
--pdftotext        default pdftotext
--pdfinfo          default pdfinfo
```

Validate supplied timestamps as timezone-aware ISO 8601 values and normalize to
`Z`. When `--indexed-at` is omitted, reuse the existing index timestamp for an
unchanged source checksum; otherwise assign the current UTC time once for all
new or changed inputs. Glob case-insensitive `.pdf` files, sort by filename,
call `convert_pdf`, write the index atomically through a temporary file, and
remove only obsolete generated Markdown files inside the exact output
directory. Never modify source PDFs.

- [ ] **Step 4: Run the integration test**

Run:

```bash
python3 -m pytest tests/test_convert_transcripts_cli.py -q
```

Expected: all CLI integration tests pass.

- [ ] **Step 5: Convert the real local corpus**

Let the first run assign its indexing timestamp. Do not provide
`--retrieved-at` unless there is defensible evidence for when the existing files
were retrieved.

Run:

```bash
python3 scripts/convert_transcripts.py \
  --source-dir EARNING-TRANSCRIPTS \
  --output-dir data/licensed/earnings_transcripts/clean_md \
  --index research/transcripts/transcript_index.csv
```

- [ ] **Step 6: Audit corpus completeness without printing licensed text**

Run a Python metadata check that asserts:

- PDF count is 23;
- Markdown count is 23;
- index row count is 23;
- transcript IDs and fiscal periods are unique;
- fiscal periods cover 2020Q4 through 2026Q2 without gaps;
- every source checksum is 64 lowercase hexadecimal characters;
- every indexed Markdown file exists;
- every transcript includes at least one management and one Q&A turn;
- every turn ID is unique inside its transcript.

Do not print transcript bodies in test logs.

- [ ] **Step 7: Confirm licensed Markdown remains ignored**

Run:

```bash
git check-ignore -v data/licensed/earnings_transcripts/clean_md/*.md
git status --short
```

Expected: generated Markdown is ignored; only the compact index and source code
are candidates for version control.

- [ ] **Step 8: Commit the CLI and metadata index**

```bash
git add scripts/convert_transcripts.py tests/test_convert_transcripts_cli.py research/transcripts/transcript_index.csv
git commit -m "feat: index ABNB earnings transcript corpus"
```

---

## Task 6: Enforce Guidance-Target Integrity and Point-in-Time Eligibility

**Files:**

- Create: `src/abnb_alt_data/leakage.py`
- Create: `tests/test_leakage.py`

- [ ] **Step 1: Write failing leakage-control tests**

Test `parse_utc(value, field_name) -> datetime`,
`assert_feature_available_before_cutoff(feature_available_at,
guidance_available_at) -> None`, `eligible_features(rows, cutoff) -> list`,
`guidance_midpoint(value_low, value_high) -> Decimal`, and
`validate_guidance_row(row, transcript_index_by_markdown,
valid_turn_ids_by_markdown) -> None`.

Required cases:

1. feature at `2026-08-06T19:59:59Z`, cutoff at `20:00:00Z`: allowed;
2. feature exactly at cutoff: rejected;
3. feature after cutoff: rejected;
4. missing feature or guidance timestamp: rejected;
5. naive timestamp without offset: rejected;
6. qualitative target with any numeric value: rejected;
7. numeric range with explicit low/high and correct midpoint: allowed;
8. midpoint not equal to the exact low/high arithmetic mean: rejected;
9. guidance Markdown path absent from index: rejected;
10. source turn absent from Markdown: rejected;
11. transcript availability status `unverified`: rejected as a test cutoff;
12. an `[indiscernible]`-affected row must not have `confidence=high`.

- [ ] **Step 2: Run focused tests and confirm import failure**

Run:

```bash
python3 -m pytest tests/test_leakage.py -q
```

Expected: collection error because `abnb_alt_data.leakage` does not exist.

- [ ] **Step 3: Implement strict UTC and cutoff checks**

Use timezone-aware `datetime` and `Decimal`; never compare timestamp strings or
binary floating point. `assert_feature_available_before_cutoff` must implement
strict `<`, not `<=`, and include both timestamps in its error message. Missing
or unverified historical publication time is an ineligibility result, not a
value to impute.

- [ ] **Step 4: Implement guidance-row validation**

Allow `guidance_type` values `range`, `point`, `qualitative`, and
`non_comparable`. Enforce compatible fields for each type. Validate the cited
Markdown path and turn ID. Require `available_at` to be at or after a verified
call `event_at`, while allowing a separately documented later corrected
transcript publication timestamp. Do not use PDF creation time as a substitute.

- [ ] **Step 5: Run focused tests**

Run:

```bash
python3 -m pytest tests/test_leakage.py -q
```

Expected: all leakage tests pass.

- [ ] **Step 6: Commit leakage controls**

```bash
git add src/abnb_alt_data/leakage.py tests/test_leakage.py
git commit -m "feat: enforce point-in-time guidance cutoffs"
```

---

## Task 7: Add Project-Level Validation

**Files:**

- Create: `src/abnb_alt_data/validation.py`
- Create: `scripts/validate_project.py`
- Create: `tests/test_validation.py`

- [ ] **Step 1: Write failing validation tests**

Create temporary good and bad project trees. Assert that validation detects:

- invalid agent TOML or wrong model settings;
- changed CSV headers;
- expected transcript count mismatch;
- duplicate fiscal periods or turn IDs;
- missing Markdown files;
- invalid guidance source paths or turn IDs;
- unverified target cutoffs;
- proprietary PDF/Markdown or likely secret files in the Git staging area.

Define an immutable `ValidationFinding` dataclass with `code` and `message`
strings, plus `validate_project(root: Path, expected_transcript_count: int = 23)
-> list[ValidationFinding]`.

- [ ] **Step 2: Run focused tests and confirm import failure**

Run:

```bash
python3 -m pytest tests/test_validation.py -q
```

Expected: collection error because `abnb_alt_data.validation` does not exist.

- [ ] **Step 3: Implement composable validation checks**

Reuse schema and guidance validators. Read staged filenames using:

```bash
git diff --cached --name-only --diff-filter=ACMR
```

Flag, but do not delete or unstage, any file under `EARNING-TRANSCRIPTS/` or
`data/licensed/earnings_transcripts/clean_md/`. Flag common credential filenames
and extensions conservatively. Never inspect or print secret contents.

When Markdown outputs do not exist, report a specific `corpus_not_converted`
finding rather than crashing. When guidance CSV has header only, validate the
schema and return no guidance-row error.

- [ ] **Step 4: Implement the command wrapper**

`scripts/validate_project.py` must accept `--root` and
`--expected-transcripts`, print one concise line per finding, and exit 1 on any
finding or 0 with `ABNB alt-data project validation passed`.

- [ ] **Step 5: Run focused and real-project validation**

Run:

```bash
python3 -m pytest tests/test_validation.py -q
python3 scripts/validate_project.py --root . --expected-transcripts 23
```

Expected: tests pass and real-project validation exits 0 after the corpus is
converted.

- [ ] **Step 6: Commit project validation**

```bash
git add src/abnb_alt_data/validation.py scripts/validate_project.py tests/test_validation.py
git commit -m "feat: validate alt-data research controls"
```

---

## Task 8: Document the Agent Contract and Exact Research Prompts

**Files:**

- Create: `docs/alt-data/agent-contract.md`
- Create: `docs/alt-data/prompting-and-running.md`
- Create: `tests/test_documentation.py`

- [ ] **Step 1: Write failing documentation tests**

Assert that both documents exist, the run guide names `abnb_alt_data`, and it
contains prompt examples for source discovery, transcript guidance extraction,
hypothesis registration, PIT audit, a single-signal guidance test, a Bloomberg
ticket, negative results, and the final top-three memo. Assert that the guidance
test prompt contains `strictly before`, `walk-forward`, `baseline`, and
`available_at`.

- [ ] **Step 2: Run the focused test and confirm missing-file failure**

Run:

```bash
python3 -m pytest tests/test_documentation.py -q
```

Expected: failure because the documentation files do not exist.

- [ ] **Step 3: Write the human-readable agent contract**

Summarize the durable TOML instructions in plain language. Include a small
workflow table:

| Stage | Agent action | User gate | Tracked artifact |
|---|---|---|---|
| Discover | Rank sources, no collection | Approve source slate | `source_registry.csv` |
| Prepare targets | Index Markdown and extract cited guidance | Review ambiguous facts | `guidance_facts.csv` |
| Preregister | State mechanism and test | Approve priorities | `hypothesis_ledger.csv` |
| Collect | Pull only approved free/permitted data | Ask on access change | timestamped local data |
| Test | Apply strict cutoff and walk-forward baselines | none within approved scope | result tables/memo |

Explain that the transcript is known only at/after the call: it supplies the
outcome to predict, not a pre-call feature.

- [ ] **Step 4: Write the prompting and running guide**

Include copy-ready prompts in the intended order. The central test prompt must
be exactly actionable, for example:

```text
Use the abnb_alt_data agent to test hypothesis H-001 against management revenue
guidance. Read research/transcripts/transcript_index.csv and
research/transcripts/guidance_facts.csv first. Use the cited Markdown turns to
verify every target. Treat guidance available_at as the prediction cutoff and
use only alternative-data releases with verified availability strictly before
that cutoff. Reject missing or unverified timestamps. Compare against the
prior-quarter and seasonal baselines using expanding-window walk-forward
validation. Keep transformations inside each training fold. Report MAE, RMSE,
directional accuracy, sample size, lag sensitivity, and all negative or
inconclusive findings. Do not add a new source, use paid data, or request
Bloomberg data without asking me first.
```

Also provide:

- a source-only discovery prompt that explicitly says `Do not collect yet`;
- a guidance extraction prompt that limits context to three full transcripts,
  requires source-turn IDs, and leaves unknown timestamps null;
- a hypothesis preregistration prompt with no outcome inspection;
- a collection/provenance audit prompt;
- a Bloomberg ticket-only prompt with securities, fields, dates, frequency,
  units, and XLSX layout;
- a negative-result review prompt that forbids post-hoc tuning;
- a memo prompt ranking three signals by PIT defensibility and incremental edge.

State that a new Codex project task may be required after adding a custom agent
so the configuration is reloaded.

- [ ] **Step 5: Run documentation tests**

Run:

```bash
python3 -m pytest tests/test_documentation.py -q
```

Expected: all documentation tests pass.

- [ ] **Step 6: Commit the contract and prompt guide**

```bash
git add docs/alt-data tests/test_documentation.py
git commit -m "docs: add ABNB agent research playbook"
```

---

## Task 9: End-to-End Verification and First Safe Handoff

**Files:**

- Modify only if tests reveal a defect in files created above.

- [ ] **Step 1: Run the complete automated suite**

Run:

```bash
python3 -m pytest -q
```

Expected: all tests pass with no warnings caused by project code.

- [ ] **Step 2: Re-run conversion deterministically**

Omit `--indexed-at`; the converter must reuse the timestamp for every unchanged
source checksum from the existing index:

```bash
python3 scripts/convert_transcripts.py \
  --source-dir EARNING-TRANSCRIPTS \
  --output-dir data/licensed/earnings_transcripts/clean_md \
  --index research/transcripts/transcript_index.csv
git diff --exit-code research/transcripts/transcript_index.csv
```

Expected: no tracked index diff, proving deterministic output for fixed inputs
and timestamps.

- [ ] **Step 3: Run project validation and inspect Git state**

Run:

```bash
python3 scripts/validate_project.py --root . --expected-transcripts 23
git diff --check
git status --short
git diff --cached --name-only
```

Expected: project validation passes; no proprietary transcript text, source PDF,
credential, or unrelated user file is staged.

- [ ] **Step 4: Exercise the first user workflow without collecting data**

Start a fresh project task if required for agent discovery and use:

```text
Use the abnb_alt_data agent to propose and rank the first 12 free or
institutionally accessible source candidates for predicting ABNB quarterly
revenue and next-quarter revenue guidance. Do not collect or test data yet.
Populate proposed research/source_registry.csv rows with mechanism, URL,
license, restrictions, geography, frequency, history, publication lag,
revisions, cost, point-in-time evidence, and leakage risk. Limit the slate to
three source families and wait for my approval.
```

Expected: a ranked, citation-preserving proposal; no collection, paid request,
Bloomberg request, or Airbnb-prohibited scraping.

- [ ] **Step 5: Create a final verification commit only if needed**

If verification required code fixes, inspect `git diff`, stage each named fixed
file explicitly, and commit with `git commit -m "fix: complete ABNB agent
verification"`. If no files changed, do not create an empty commit.

## Completion Checklist

- [ ] `.codex/agents/abnb_alt_data.toml` parses with the approved model,
  reasoning effort, sandbox, and durable research contract.
- [ ] The source registry and hypothesis ledger include every required field.
- [ ] The 23 source PDFs remain untouched and ignored.
- [ ] Exactly 23 ignored Markdown transcripts and 23 tracked index rows exist.
- [ ] Markdown front matter distinguishes event, publication, PDF creation,
  retrieval, indexing, and PIT-usable timestamps.
- [ ] Guidance rows cite real Markdown turn IDs and never fabricate numeric
  values from qualitative or indiscernible text.
- [ ] Strict pre-guidance feature eligibility is enforced in code and tests.
- [ ] Prompts teach the agent to preregister, use baselines, preserve negatives,
  and ask before paid/Bloomberg access.
- [ ] Full tests and project validation pass.
- [ ] Git staging contains no proprietary transcript text, PDFs, credentials, or
  unrelated changes.
