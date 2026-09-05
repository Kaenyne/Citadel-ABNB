# Airbnb Guidance Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a permanent Codex role and a reproducible, point-in-time research system that identifies which observable factors most consistently explain Airbnb's quarterly revenue-guidance level, range, tone, and apparent conservatism.

**Architecture:** Use an audit-first Python package with typed normalized records, immutable source provenance, leakage-controlled modeling views, and generated analyst-facing outputs. Official documents and narrowly scoped excerpts feed normalized CSV/Parquet tables; deterministic transforms create the quarterly panel, walk-forward tests, evidence tiers, and final report.

**Tech Stack:** Python 3.12, Pydantic 2, pandas, PyArrow, scikit-learn, PyYAML, openpyxl, requests, `pdftotext`, pytest, TOML.

**Spec:** `docs/superpowers/specs/2026-09-02-abnb-guidance-intelligence-design.md`

## Global Constraints

- Research cutoff for the initial build: `2026-09-02T23:59:59-04:00`.
- Candidate earnings events: Q4 2020 through Q2 2026 results; retain unusable events with an explicit exclusion reason.
- The management-information view is primary; the strictly public pre-release view is the robustness case.
- Do not use an observation published after the initial guidance timestamp as a predictor of that guide.
- Do not store or reproduce a complete third-party transcript; retain only minimal cited excerpts.
- Ask before paid collection or Bloomberg extraction; creating an XLSX request does not authorize extraction.
- Preserve contradictions and negative evidence; never overwrite a sourced observation silently.
- Store raw official documents byte-for-byte with SHA-256 hashes when lawful.
- Do not initialize Git unless the user separately asks. Because this workspace is not a Git repository, each task ends with a tested local checkpoint rather than a commit.
- Do not infer a missing value as zero.

## File Map

```text
.codex/agents/abnb_guidance_intelligence.toml
pyproject.toml
research/abnb_guidance/AGENT_PLAYBOOK.md
src/abnb_guidance/
|-- __init__.py                 Package version and public exports
|-- types.py                    Shared enums and period/identifier types
|-- records.py                  Pydantic records for normalized tables
|-- storage.py                  CSV/Parquet loading, writing, FK and hash checks
|-- sources.py                  Lawful source capture and source-manifest helpers
|-- extraction.py               PDF/HTML text extraction and excerpt verification
|-- features.py                 Derived targets, driver features, and wide panel
|-- leakage.py                  Information-clock eligibility rules
|-- tone.py                     Blinded outlook-tone coding rubric and adjudication
|-- market.py                   Reaction-session and return-window calculations
|-- modeling.py                 Walk-forward baselines and incremental driver tests
|-- ranking.py                  Transparent driver evidence tiers
|-- reporting.py                Markdown reports and unresolved-question output
`-- cli.py                      Reproducible command-line entry points
research/abnb_guidance/
|-- config/
|   |-- collection.yaml
|   |-- driver_taxonomy.yaml
|   `-- tone_rubric.yaml
|-- schemas/
|   |-- data_dictionary.yaml
|   `-- generated/              Pydantic-generated JSON schemas
|-- data/
|   |-- source_documents/       Lawfully retained official files
|   |-- manifests/source_documents.csv
|   `-- normalized/             Canonical normalized CSV and Parquet tables
|-- evidence/management_driver_ledger.csv
|-- analysis/model_results.csv
|-- reports/
|   |-- guidance_panel.csv
|   |-- guidance_panel.parquet
|   |-- ranked_driver_assessment.md
|   |-- unresolved_questions.md
|   `-- validation_log.md
`-- requests/                   Exact data requests generated when needed
tests/
|-- __init__.py
|-- helpers.py
|-- test_agent_config.py
|-- test_records.py
|-- test_storage.py
|-- test_sources.py
|-- test_extraction.py
|-- test_features.py
|-- test_leakage.py
|-- test_tone.py
|-- test_market.py
|-- test_modeling.py
|-- test_ranking.py
`-- test_end_to_end.py
```

### Task 1: Create the project package and permanent Codex role

**Files:**
- Create: `pyproject.toml`
- Create: `.codex/agents/abnb_guidance_intelligence.toml`
- Create: `research/abnb_guidance/AGENT_PLAYBOOK.md`
- Create: `src/abnb_guidance/__init__.py`
- Create: `tests/test_agent_config.py`

**Interfaces:**
- Consumes: approved design specification.
- Produces: importable package `abnb_guidance`; TOML role with nonblank `description` and `developer_instructions`.

- [ ] **Step 1: Write the failing role-contract test**

```python
from pathlib import Path
import tomllib


ROLE = Path(".codex/agents/abnb_guidance_intelligence.toml")


def test_agent_role_contains_durable_research_constraints():
    config = tomllib.loads(ROLE.read_text())
    instructions = config["developer_instructions"]
    assert config["description"]
    assert "point-in-time" in instructions.lower()
    assert "Bloomberg" in instructions
    assert "complete third-party transcript" in instructions
    assert "contradictory" in instructions
    assert "walk-forward" in instructions
```

- [ ] **Step 2: Run the test and confirm the role is absent**

Run: `pytest tests/test_agent_config.py -v`

Expected: FAIL because `.codex/agents/abnb_guidance_intelligence.toml` does not exist.

- [ ] **Step 3: Add package metadata and the minimal role file**

Use this project metadata contract:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "abnb-guidance-intelligence"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "openpyxl",
  "pandas",
  "pyarrow",
  "pydantic>=2",
  "PyYAML",
  "requests",
  "scikit-learn",
]

[project.optional-dependencies]
test = ["pytest"]

[project.scripts]
abnb-guidance = "abnb_guidance.cli:main"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

The role file must use only fields accepted by the installed Codex role parser. Start with `description` and `developer_instructions`; copy the twelve durable duties from Section 4 of the design spec into the multiline instruction string. Do not pin a model.

- [ ] **Step 4: Run the contract test**

Run: `pytest tests/test_agent_config.py -v`

Expected: PASS.

- [ ] **Step 5: Record the checkpoint**

Append the test command, UTC timestamp, and result to `research/abnb_guidance/reports/validation_log.md` when that file is created in Task 3.

### Task 2: Define typed records, enums, and generated schemas

**Files:**
- Create: `src/abnb_guidance/types.py`
- Create: `src/abnb_guidance/records.py`
- Create: `research/abnb_guidance/schemas/data_dictionary.yaml`
- Create: `research/abnb_guidance/config/driver_taxonomy.yaml`
- Create: `tests/test_records.py`

**Interfaces:**
- Consumes: table and field definitions in design Section 8.
- Produces: `TABLE_MODELS: dict[str, type[BaseModel]]`; `primary_key_for(table_name: str) -> str`; Pydantic models for all eleven canonical tables.

- [ ] **Step 1: Write failing record-invariant tests**

```python
import pytest
from pydantic import ValidationError

from abnb_guidance.records import GuidanceItem, DriverObservation


def test_guidance_range_rejects_reversed_bounds():
    with pytest.raises(ValidationError):
        GuidanceItem.model_validate({
            "guidance_item_id": "ABNB_2024Q3_REV",
            "guidance_event_id": "ABNB_2024Q3_RESULTS",
            "target_period": "2024Q4",
            "metric_code": "revenue",
            "measure_type": "absolute",
            "value_low": 2200.0,
            "value_high": 2100.0,
            "value_mid": 2150.0,
            "unit": "USD_millions",
            "currency": "USD",
            "accounting_basis": "GAAP",
            "is_company_stated": True,
            "source_excerpt_id": "EX1",
            "extraction_confidence": "high",
        })


def test_derived_driver_requires_formula():
    with pytest.raises(ValidationError):
        DriverObservation.model_validate({
            "driver_observation_id": "D1",
            "guidance_event_id": "E1",
            "driver_family": "booking_economics",
            "driver_code": "take_rate",
            "value_numeric": 0.14,
            "unit": "ratio",
            "availability_class": "contemporaneous_management_known",
            "is_derived": True,
            "quality_grade": "A",
            "leakage_risk": "low",
        })
```

- [ ] **Step 2: Run the focused tests**

Run: `pytest tests/test_records.py -v`

Expected: FAIL because the record types do not exist.

- [ ] **Step 3: Implement shared types and all canonical records**

Define `FiscalPeriod` validation with `^[0-9]{4}Q[1-4]$`. Define string enums for availability class, evidence stance, attribution strength, confidence, quality grade, event type, accounting basis, issue status, and severity. Implement Pydantic models named:

```python
GuidanceEvent
GuidanceItem
QuarterlyActual
ConsensusSnapshot
DriverObservation
SourceDocument
SourceExcerpt
EvidenceClaim
MarketReturn
ModelResult
ResearchIssue
```

All columns listed in design Section 8 must exist. Columns may be nullable when the source does not disclose a value, but each table must include `value_status` and `missing_reason`; use `value_status="observed"` and `missing_reason=None` as model defaults, and require a reason whenever `value_status != "observed"`. Enforce low ≤ midpoint ≤ high whenever all three are present. Enforce a nonblank formula for derived values.

- [ ] **Step 4: Complete the field dictionary and taxonomy**

For every field, record table, data type, nullability, unit convention, semantic definition, and derivation rule. Define the eight approved driver families and stable snake-case driver codes; aliases map issuer wording to a stable code without deleting the original wording.

- [ ] **Step 5: Run record tests**

Run: `pytest tests/test_records.py -v`

Expected: PASS.

### Task 3: Implement canonical storage and dataset validation

**Files:**
- Create: `src/abnb_guidance/storage.py`
- Create: `research/abnb_guidance/data/manifests/source_documents.csv`
- Create: eleven header-only CSVs under `research/abnb_guidance/data/normalized/`
- Create: `research/abnb_guidance/reports/validation_log.md`
- Create: `tests/test_storage.py`

**Interfaces:**
- Consumes: `TABLE_MODELS` and primary-key map from Task 2.
- Produces: `load_table(name: str, root: Path) -> pd.DataFrame`; `write_table(name: str, frame: pd.DataFrame, root: Path) -> None`; `validate_dataset(root: Path) -> list[ValidationFinding]`; `export_json_schemas(path: Path) -> None`.

- [ ] **Step 1: Write failing storage tests**

```python
from pathlib import Path
import pandas as pd

from abnb_guidance.storage import validate_dataset, write_table


def test_duplicate_primary_key_is_rejected(tmp_path: Path):
    frame = pd.DataFrame([
        {"guidance_event_id": "E1", "issuer_id": "ABNB"},
        {"guidance_event_id": "E1", "issuer_id": "ABNB"},
    ])
    write_table("guidance_events", frame, tmp_path)
    findings = validate_dataset(tmp_path)
    assert any(f.code == "duplicate_primary_key" for f in findings)


def test_missing_foreign_key_is_rejected(tmp_path: Path):
    # Fixture helpers write a guidance item referring to an absent event.
    frame = pd.DataFrame([{"guidance_item_id": "G1", "guidance_event_id": "MISSING"}])
    write_table("guidance_items", frame, tmp_path)
    findings = validate_dataset(tmp_path)
    assert any(f.code == "missing_foreign_key" for f in findings)
```

- [ ] **Step 2: Confirm failures**

Run: `pytest tests/test_storage.py -v`

Expected: FAIL because storage functions do not exist.

- [ ] **Step 3: Implement deterministic read, write, and validation**

Write CSV using UTF-8, LF line endings, stable column order, ISO-8601 timestamps, and blank cells for nulls. Write Parquet from the same validated frame. Validate primary keys, foreign keys, enums, period format, range arithmetic, SHA-256 shape, excerpt links, missing-value reasons, and formulas for derived observations. Return findings rather than mutating source records.

- [ ] **Step 4: Generate canonical templates and JSON schemas**

Create exact headers from the Pydantic models for all normalized tables. Generate JSON schemas into `research/abnb_guidance/schemas/generated/`. Seed the validation log with the research cutoff, Python version, and package versions.

- [ ] **Step 5: Run storage and record tests**

Run: `pytest tests/test_records.py tests/test_storage.py -v`

Expected: PASS.

### Task 4: Build lawful source capture and provenance controls

**Files:**
- Create: `src/abnb_guidance/sources.py`
- Create: `research/abnb_guidance/config/collection.yaml`
- Create: `tests/test_sources.py`

**Interfaces:**
- Consumes: `SourceDocument` and collection policy.
- Produces: `is_allowed_source(url: str, document_type: str) -> bool`; `capture_official_document(record: SourceDocument, destination: Path, user_agent: str) -> SourceDocument`; `sha256_file(path: Path) -> str`; `detect_duplicate_document(records: list[SourceDocument]) -> dict[str, list[str]]`.

- [ ] **Step 1: Write failing domain, hash, and duplicate tests**

```python
from pathlib import Path

from abnb_guidance.sources import is_allowed_source, sha256_file


def test_official_domains_are_allowed_and_unknown_transcript_host_is_not():
    assert is_allowed_source("https://investors.airbnb.com/financials/", "shareholder_letter")
    assert is_allowed_source("https://www.sec.gov/Archives/edgar/data/1559720/x.htm", "sec_filing")
    assert not is_allowed_source("https://example.com/abnb-transcript", "third_party_transcript")


def test_sha256_is_stable(tmp_path: Path):
    path = tmp_path / "doc.txt"
    path.write_bytes(b"ABNB")
    assert sha256_file(path) == "6d50f3cd55fb1bba76aabc8edc12a886c70509b2887e95b4bd49ab5443ccaa31"
```

- [ ] **Step 2: Confirm failures**

Run: `pytest tests/test_sources.py -v`

Expected: FAIL because the source functions do not exist.

- [ ] **Step 3: Implement source policy and capture**

Allow first-party downloads from `investors.airbnb.com`, documented Airbnb CDN hosts, and `sec.gov`. Require an explicit source record for every URL. For SEC requests, require a caller-supplied identifying user agent and use a conservative one-request-per-second delay. Follow redirects only to allowed hosts. Reject authentication bypasses, paywall circumvention, and unapproved transcript archiving. Stream response bytes to a temporary file, calculate the hash, then move the completed file to its stable document-ID path.

- [ ] **Step 4: Populate the official source manifest**

Enumerate Q4 2020 through Q2 2026 earnings events from Airbnb IR and SEC EDGAR. For each event, record the shareholder letter, 8-K exhibit, 10-Q or 10-K, earnings webcast page, and company-hosted transcript or prepared remarks when available. Record missing sources and link changes in `research_issues` rather than substituting an uncited aggregator.

- [ ] **Step 5: Capture official documents and verify hashes**

Run the capture command with an identifying SEC user agent supplied through `SEC_USER_AGENT`. Store only official documents permitted by the policy. Re-run capture in verification mode and assert that unchanged source bytes reproduce the recorded hashes.

- [ ] **Step 6: Run source tests and full validation**

Run 1: `pytest tests/test_sources.py -v`

Run 2: `PYTHONPATH=src python -m abnb_guidance.cli validate`

Expected: tests PASS; validation reports no malformed document IDs, disallowed retained sources, or invalid hashes.

### Task 5: Implement document extraction and excerpt verification

**Files:**
- Create: `src/abnb_guidance/extraction.py`
- Create: `tests/test_extraction.py`

**Interfaces:**
- Consumes: captured official documents and `SourceExcerpt` rows.
- Produces: `extract_text(document: SourceDocument) -> ExtractedDocument`; `normalize_for_match(text: str) -> str`; `verify_excerpt(excerpt: SourceExcerpt, document: ExtractedDocument) -> bool`; `find_outlook_sections(document: ExtractedDocument) -> list[TextSpan]`.

- [ ] **Step 1: Write failing excerpt-verification tests**

```python
from abnb_guidance.extraction import ExtractedDocument, normalize_for_match, verify_excerpt
from abnb_guidance.records import SourceExcerpt


def test_normalization_preserves_words_while_collapsing_layout_noise():
    assert normalize_for_match("Revenue\n  will be $2.0—$2.1 billion") == (
        "Revenue will be $2.0-$2.1 billion"
    )


def test_excerpt_must_exist_in_its_document():
    document = ExtractedDocument(document_id="DOC1", text="Revenue should grow.", pages={1: "Revenue should grow."})
    excerpt = SourceExcerpt.model_validate({
        "source_excerpt_id": "EX1",
        "document_id": "DOC1",
        "page_number": 1,
        "exact_excerpt": "language absent from source",
        "excerpt_word_count": 4,
        "context_paraphrase": "Absent test language",
        "copyright_handling": "official_document",
        "extraction_method": "manual",
        "verified_against_source": False,
    })
    assert verify_excerpt(excerpt, document) is False
```

- [ ] **Step 2: Confirm failures**

Run: `pytest tests/test_extraction.py -v`

Expected: FAIL because extraction functions do not exist.

- [ ] **Step 3: Implement text extraction**

Use `pdftotext -layout` for PDFs and a deterministic HTML text parser for SEC/IR HTML. Preserve page boundaries for PDFs and headings or element anchors for HTML. Normalize typography only for matching; keep `exact_excerpt` exactly as displayed in the authoritative source.

- [ ] **Step 4: Implement excerpt compliance checks**

Require every excerpt to resolve to its document and pinpoint. Configure third-party transcript limits of 25 words per excerpt and 100 quoted words per transcript source per earnings event. Flag records over either cap. Do not ingest or persist the full third-party transcript body.

- [ ] **Step 5: Run extraction tests**

Run: `pytest tests/test_extraction.py -v`

Expected: PASS.

### Task 6: Populate core guidance, actuals, and quantitative drivers

**Files:**
- Modify: normalized `guidance_events.csv`
- Modify: normalized `guidance_items.csv`
- Modify: normalized `quarterly_actuals.csv`
- Modify: normalized `driver_observations.csv`
- Modify: normalized `source_excerpts.csv`
- Modify: normalized `research_issues.csv`

**Interfaces:**
- Consumes: verified official documents and extraction helpers.
- Produces: cited official core dataset for every candidate event.

- [ ] **Step 1: Create the event chronology**

For each Q4 2020 through Q2 2026 results event, record reported period, exact initial publication timestamp and precision, release timing, primary source, and whether Airbnb issued usable next-quarter revenue guidance. Assign stable IDs in the form `ABNB_<reported-period>_RESULTS_<YYYY-MM-DD>`.

- [ ] **Step 2: Extract revenue guidance and all other guided metrics**

Enter company-stated low, high, midpoint, unit, currency, accounting basis, target period, and exact outlook excerpt. When midpoint or growth is derived, retain source components and formula. Store annual guidance as its own target horizon rather than mixing it with next-quarter guidance.

- [ ] **Step 3: Extract reported actuals and growth**

Enter reported revenue and YoY growth plus Nights and Seats Booked, GBV, ADR, take rate, regional or cross-border measures, active listings, marketing expense, and other consistently disclosed candidate drivers. Distinguish company-stated growth from calculations.

- [ ] **Step 4: Reconcile each next-quarter guide with the eventual result**

Link each target quarter to its later reported revenue. Calculate neither surprise nor realized cushion in the input tables; those values are generated in Task 9. Record missing eventual results beyond the cutoff as unavailable after cutoff.

- [ ] **Step 5: Perform independent second-entry verification**

Re-open the authoritative source without viewing the first extraction values. Re-enter guidance bounds, revenue, nights, and GBV into a temporary comparison frame. Resolve differences against the source and record every material discrepancy in `research_issues`.

- [ ] **Step 6: Validate the core dataset**

Run: `PYTHONPATH=src python -m abnb_guidance.cli validate --tables guidance_events guidance_items quarterly_actuals driver_observations source_excerpts`

Expected: zero high-severity findings; every observed number has a source excerpt or derivation.

### Task 7: Build the management-driver evidence ledger and tone coding

**Files:**
- Create: `src/abnb_guidance/tone.py`
- Create: `research/abnb_guidance/config/tone_rubric.yaml`
- Modify: normalized `evidence_claims.csv`
- Modify: `research/abnb_guidance/evidence/management_driver_ledger.csv`
- Create: `tests/test_tone.py`

**Interfaces:**
- Consumes: verified outlook and call excerpts without eventual actuals or market returns.
- Produces: `code_tone(coding_input: ToneCodingInput, rubric: ToneRubric) -> ToneCoding`; `adjudicate_tone(first: ToneCoding, second: ToneCoding) -> ToneAdjudication`; cited evidence ledger.
- `ToneCoding` fields: `score: int`, `demand_direction: int`, `uncertainty_emphasis: int`, `commitment_strength: int`, and `rationale: str`.

- [ ] **Step 1: Write failing tone and evidence tests**

```python
from abnb_guidance.tone import ToneCoding, ToneCodingInput, adjudicate_tone


def test_disagreement_requires_adjudication_reason():
    cautious = ToneCoding(score=-1, demand_direction=-1, uncertainty_emphasis=2,
                           commitment_strength=0, rationale="uncertainty emphasized")
    constructive = ToneCoding(score=1, demand_direction=1, uncertainty_emphasis=0,
                               commitment_strength=1, rationale="demand emphasized")
    result = adjudicate_tone(cautious, constructive)
    assert result.requires_review is True
    assert result.final_score is None


def test_outcome_fields_are_not_accepted_by_tone_input():
    assert "eventual_revenue" not in ToneCodingInput.model_fields
    assert "stock_return" not in ToneCodingInput.model_fields
```

- [ ] **Step 2: Confirm failures**

Run: `pytest tests/test_tone.py -v`

Expected: FAIL because tone types and functions do not exist.

- [ ] **Step 3: Implement the approved five-point rubric**

Code the overall score from -2 to 2 and retain demand direction, uncertainty emphasis, commitment strength, cited phrases, and rationale. Do not pass the numerical guidance surprise, eventual actual, or stock reaction into the coding interface.

- [ ] **Step 4: Populate evidence claims**

For each event, extract minimal passages that connect guidance to candidate drivers. Code claim type, driver, direction, horizon, scope, attribution strength, stance, and confidence. Include statements that deny an effect, identify offsets, or contradict earlier commentary.

- [ ] **Step 5: Complete two coding passes and adjudicate disagreements**

Run the rubric twice with the evidence order changed and without outcomes visible. Log disagreements and final rationales. Material ambiguity remains `mixed` rather than being forced into a directional label.

- [ ] **Step 6: Generate and validate the evidence ledger**

The analyst-facing ledger joins claims to short excerpts and document citations without duplicating entire source documents.

Run 1: `pytest tests/test_tone.py -v`

Run 2: `PYTHONPATH=src python -m abnb_guidance.cli validate --tables evidence_claims source_excerpts`

Expected: PASS with no uncited evidence claims.

### Task 8: Add consensus snapshots, market data, and Bloomberg escalation

**Files:**
- Create: `src/abnb_guidance/market.py`
- Modify: normalized `consensus_snapshots.csv`
- Modify: normalized `market_returns.csv`
- Modify: normalized `research_issues.csv`
- Create when needed: `research/abnb_guidance/requests/ABNB_Bloomberg_Request.xlsx`
- Create: `tests/test_market.py`

**Interfaces:**
- Consumes: event timestamps, lawful public consensus references, and daily adjusted prices.
- Produces: `reaction_session(published_at: datetime, exchange_calendar: Sequence[date]) -> date`; `compute_total_return(prices: pd.Series, start: date, sessions: int) -> float`; exact Bloomberg request workbook when public data is inadequate.

- [ ] **Step 1: Write failing event-timing and return tests**

```python
from datetime import date, datetime
from zoneinfo import ZoneInfo

from abnb_guidance.market import reaction_session


NY = ZoneInfo("America/New_York")


def test_after_close_release_reacts_next_session():
    sessions = [date(2024, 5, 8), date(2024, 5, 9)]
    published = datetime(2024, 5, 8, 16, 5, tzinfo=NY)
    assert reaction_session(published, sessions) == date(2024, 5, 9)
```

- [ ] **Step 2: Confirm failures**

Run: `pytest tests/test_market.py -v`

Expected: FAIL because market functions do not exist.

- [ ] **Step 3: Implement reaction sessions and return calculations**

Use regular NASDAQ sessions, adjusted closing prices, and windows of 1, 5, 20, and 60 sessions. Store ABNB raw total return and excess return versus QQQ and SPY. Mark 20- and 60-session windows as materially confounded in generated reports.

- [ ] **Step 4: Collect public point-in-time consensus evidence**

For each event, search for the nearest lawfully accessible estimate snapshot strictly before the initial release. Record statistic type, analyst count, snapshot timestamp and precision, age, source, and access basis. Do not treat an article published after the event as pre-event consensus even if it describes an earlier analyst estimate without a verified as-of time.

- [ ] **Step 5: Decide whether a Bloomberg request is required**

If any event lacks a verified pre-event revenue consensus or adjusted price history adequate for the specified windows, record the gap and generate an XLSX workbook with these sheets:

```text
Instructions
Guidance_Events
Consensus_Request
Price_Request
Field_Definitions
```

`Consensus_Request` must request ABNB revenue consensus for each target fiscal quarter as of one minute before the event timestamp, including mean, median when available, high, low, contributor count, currency, and fiscal-period identifier. `Price_Request` must request ABNB, QQQ, and SPY daily adjusted closes and corporate-action factors from 2020-12-10 through the latest required 60-session endpoint. The workbook must say clearly that completing it does not authorize Bloomberg extraction.

- [ ] **Step 6: Validate and stop at the paid-data gate**

Run 1: `pytest tests/test_market.py -v`

Run 2: `PYTHONPATH=src python -m abnb_guidance.cli validate --tables consensus_snapshots market_returns`

Expected: tests PASS. If the XLSX request exists, present it to the user and wait for approval before any Bloomberg work.

### Task 9: Build leakage-controlled targets, features, and quarterly panel

**Files:**
- Create: `src/abnb_guidance/leakage.py`
- Create: `src/abnb_guidance/features.py`
- Create: `tests/test_leakage.py`
- Create: `tests/test_features.py`
- Generate: `research/abnb_guidance/reports/guidance_panel.csv`
- Generate: `research/abnb_guidance/reports/guidance_panel.parquet`

**Interfaces:**
- Consumes: validated normalized tables.
- Produces: `eligible_for_view(observation: FeatureObservation, event: GuidanceEvent, view: InformationView) -> EligibilityDecision`; `derive_one_target(guide_low: float, guide_high: float, consensus: float | None, actual: float | None) -> DerivedTarget`; `derive_guidance_targets(...) -> pd.DataFrame`; `build_guidance_panel(root: Path, view: InformationView) -> pd.DataFrame`.

- [ ] **Step 1: Write failing leakage tests**

```python
from abnb_guidance.leakage import eligible_for_view


def test_post_event_observation_is_rejected(event, post_event_observation):
    result = eligible_for_view(post_event_observation, event, "management_information_view")
    assert result.eligible is False
    assert result.reason_code == "post_event"


def test_contemporaneous_actual_is_management_only(event, contemporaneous_actual):
    assert eligible_for_view(contemporaneous_actual, event, "management_information_view").eligible
    assert not eligible_for_view(contemporaneous_actual, event, "public_prior_view").eligible
```

- [ ] **Step 2: Write failing target-math tests**

```python
import pytest

from abnb_guidance.features import derive_one_target


def test_guidance_target_sign_conventions():
    row = derive_one_target(guide_low=95, guide_high=105, consensus=110, actual=108)
    assert row.guide_mid == 100
    assert row.range_width_pct == 0.10
    assert row.guidance_surprise_pct == pytest.approx(-10 / 110)
    assert row.ex_ante_conservatism_pct == pytest.approx(10 / 110)
    assert row.realized_cushion_pct == 0.08
    assert row.actual_range_position == "above"
```

- [ ] **Step 3: Confirm failures**

Run: `pytest tests/test_leakage.py tests/test_features.py -v`

Expected: FAIL because leakage and feature functions do not exist.

- [ ] **Step 4: Implement information-view eligibility**

Reject post-event timestamps, revised macro vintages unavailable at the event, and unverified consensus snapshots from strict public-prior models. Return a reason code and audit detail for every inclusion or rejection.

- [ ] **Step 5: Implement target and driver derivations**

Calculate guidance midpoint, guided YoY midpoint, normalized range width, guidance surprise, ex-ante conservatism, baseline-relative conservatism, realized cushion, and range position exactly as defined in design Section 9. Derive ADR as GBV divided by nights and take rate as revenue divided by GBV only when units and periods align; preserve formulas and zero-denominator guards.

- [ ] **Step 6: Generate both panel views**

Create a primary management-information panel and a strict public-prior panel. Include source IDs, quality flags, missingness flags, and eligibility audit columns. Sort by initial guidance timestamp and use stable column order.

- [ ] **Step 7: Run feature tests and validate generated panels**

Run 1: `pytest tests/test_leakage.py tests/test_features.py -v`

Run 2: `PYTHONPATH=src python -m abnb_guidance.cli build-panel --all-views`

Expected: PASS; no post-event predictor appears in either panel.

### Task 10: Implement walk-forward baselines and incremental driver tests

**Files:**
- Create: `src/abnb_guidance/modeling.py`
- Create: `tests/test_modeling.py`
- Generate: `research/abnb_guidance/analysis/model_results.csv`

**Interfaces:**
- Consumes: time-ordered guidance panels and driver taxonomy.
- Produces: `walk_forward_splits(events: Sequence[str], min_train_size: int) -> list[Fold]`; `summarize_errors(baseline_errors: Sequence[float], model_errors: Sequence[float]) -> ErrorSummary`; `fit_baseline(train: pd.DataFrame, target: str, baseline: str) -> Predictor`; `evaluate_driver(panel: pd.DataFrame, target: str, driver: str, view: str) -> pd.DataFrame`; `run_model_suite(...) -> pd.DataFrame`.

- [ ] **Step 1: Write failing chronological-split tests**

```python
from abnb_guidance.modeling import walk_forward_splits


def test_walk_forward_never_trains_on_future_events():
    events = [f"E{i}" for i in range(10)]
    folds = walk_forward_splits(events, min_train_size=6)
    assert [fold.test for fold in folds] == ["E6", "E7", "E8", "E9"]
    assert all(max(fold.train_index) < fold.test_index for fold in folds)
```

- [ ] **Step 2: Write failing baseline-comparison test**

```python
from abnb_guidance.modeling import summarize_errors


def test_error_improvement_is_baseline_mae_minus_driver_mae():
    result = summarize_errors(baseline_errors=[10, 20], model_errors=[8, 18])
    assert result.baseline_mae == 15
    assert result.model_mae == 13
    assert result.error_improvement == 2
```

- [ ] **Step 3: Confirm failures**

Run: `pytest tests/test_modeling.py -v`

Expected: FAIL because modeling functions do not exist.

- [ ] **Step 4: Implement baselines**

Implement these fixed baselines:

- Revenue seasonal/history: same target-quarter revenue one year earlier multiplied by one plus the most recent trailing-four-quarter revenue growth eligible in the selected information view.
- Revenue consensus: the nearest verified consensus snapshot strictly before the event.
- Revenue combined: a ridge regression on the seasonal/history forecast and consensus, with scaling and penalty selection fit inside the training fold.
- Range width: the median prior normalized range width for the same target calendar quarter when at least two such observations exist, otherwise the median of all prior observations.
- Tone: the median prior tone for the same target calendar quarter when at least two observations exist, otherwise the median of all prior observations.
- Ex-ante conservatism versus consensus: zero, equivalent to guidance centered on consensus; the seasonal robustness baseline uses the seasonal revenue forecast instead of consensus in the approved conservatism formula.

Use a minimum expanding training window of eight eligible events when available; if fewer events support a target, report it as data-limited rather than relaxing chronology silently.

- [ ] **Step 5: Implement incremental driver evaluation**

Add each driver separately to each eligible baseline. Permit only predefined groups from the taxonomy and cap predictors so the fitted model remains identifiable relative to the training sample. Store held-out predictions, errors, training endpoints, feature codes, warnings, and fixed random seed.

- [ ] **Step 6: Implement target-specific metrics**

Report MAE, RMSE, and baseline error improvement for continuous targets; interval coverage and normalized width for ranges; ordinal MAE and confusion counts for tone; directional accuracy and magnitude error for conservatism. Run leave-one-quarter-out only as a labeled sensitivity table separate from real-time results.

- [ ] **Step 7: Run model tests and the model suite**

Run 1: `pytest tests/test_modeling.py -v`

Run 2: `PYTHONPATH=src python -m abnb_guidance.cli model --all-targets --all-views`

Expected: PASS; every primary result uses chronological folds and includes eligible-event count.

### Task 11: Rank drivers and generate the cited research report

**Files:**
- Create: `src/abnb_guidance/ranking.py`
- Create: `src/abnb_guidance/reporting.py`
- Create: `tests/test_ranking.py`
- Generate: `research/abnb_guidance/reports/ranked_driver_assessment.md`
- Generate: `research/abnb_guidance/reports/unresolved_questions.md`

**Interfaces:**
- Consumes: model results, evidence claims, quality grades, coverage, and leakage findings.
- Produces: `assess_driver(driver_code: str, inputs: EvidenceBundle) -> DriverAssessment`; `render_ranked_report(assessments: list[DriverAssessment]) -> str`; `render_unresolved_report(issues: pd.DataFrame) -> str`.
- `EvidenceBundle` fields: `error_improvement: float`, `error_improvement_pct: float`, `stable_direction_share: float`, `supporting_claims: int`, `contradictory_claims: int`, `eligible_quarters: int`, `robustness_error_improvement_pct: float | None`, `independent_error_improvement_pct: float | None`, `quality_grade: str`, `leakage_risk: str`, `management_direction: int | None`, and `fitted_direction: int | None`. Nullable fields default to `None`; `quality_grade` defaults to `"C"` and `leakage_risk` to `"medium"` in unit-test fixtures only.

- [ ] **Step 1: Write failing ranking tests**

```python
from abnb_guidance.ranking import EvidenceBundle, assess_driver


def test_positive_narrative_with_worse_oos_error_is_not_strong():
    bundle = EvidenceBundle(
        error_improvement=-5.0,
        error_improvement_pct=-0.05,
        stable_direction_share=0.80,
        supporting_claims=8,
        contradictory_claims=0,
        eligible_quarters=15,
    )
    assert assess_driver("nights_booked_yoy", bundle).tier in {"weak", "contradicted"}


def test_low_coverage_is_data_limited():
    bundle = EvidenceBundle(error_improvement=2.0, error_improvement_pct=0.10,
                            stable_direction_share=0.75, supporting_claims=3,
                            contradictory_claims=0, eligible_quarters=3)
    assert assess_driver("booking_lead_time", bundle).tier == "data_limited"
```

- [ ] **Step 2: Confirm failures**

Run: `pytest tests/test_ranking.py -v`

Expected: FAIL because ranking functions do not exist.

- [ ] **Step 3: Implement transparent evidence tiers**

Rank primarily on walk-forward improvement, then sign stability, explicit attribution, independent contribution, and coverage. Apply these predeclared tier rules and show sensitivity at 0%, 2.5%, 5%, and 10% MAE-improvement cutoffs:

- `data_limited`: fewer than five held-out events, regardless of apparent effect.
- `strong`: at least 5% MAE improvement in the primary view, stable fitted direction in at least 70% of folds, at least three explicit driver/contributor claims, and no material reversal in an eligible robustness view.
- `moderate`: positive MAE improvement, stable direction in at least 60% of folds, and at least two explicit driver/contributor claims.
- `contradicted`: nonpositive MAE improvement and either more contradictory than supporting claims or a fitted direction opposite management's stated direction in at least 70% of folds.
- `weak`: all other adequately covered cases.

A driver cannot receive `strong` solely from management mention frequency. Contradictory and negative claims are counted and displayed, not netted away invisibly.

- [ ] **Step 4: Generate the driver report**

For each driver, show rank or tier, target affected, information view, eligible quarters, baseline and augmented errors, direction stability, representative short citations, contradictory evidence, leakage risk, and interpretation limits. Separate observations about management weighting from investor-return associations.

- [ ] **Step 5: Generate unresolved questions and potential paid-data requests**

List missing sources, weak timestamps, consensus gaps, inconsistent metric definitions, regulatory exposure gaps, transcript restrictions, and model limitations. Link any generated Bloomberg XLSX request without claiming it was executed.

- [ ] **Step 6: Run ranking tests and report generation**

Run 1: `pytest tests/test_ranking.py -v`

Run 2: `PYTHONPATH=src python -m abnb_guidance.cli report`

Expected: PASS; the report contains supporting, contradictory, negative, and null evidence sections.

### Task 12: Add CLI orchestration and end-to-end verification

**Files:**
- Create: `src/abnb_guidance/cli.py`
- Create: `tests/__init__.py`
- Create: `tests/helpers.py`
- Create: `tests/test_end_to_end.py`
- Modify: `research/abnb_guidance/reports/validation_log.md`

**Interfaces:**
- Consumes: all package functions.
- Produces: commands `validate`, `capture`, `extract`, `build-panel`, `model`, `report`, and `all`; `write_fixture_project(root: Path, event_count: int = 9) -> Path`; complete reproducible research run.

- [ ] **Step 1: Write the failing end-to-end fixture test**

```python
from pathlib import Path

from abnb_guidance.cli import run_pipeline
from tests.helpers import write_fixture_project


def test_fixture_pipeline_builds_all_outputs_without_leakage(tmp_path: Path):
    fixture_project = write_fixture_project(tmp_path, event_count=9)
    result = run_pipeline(fixture_project, cutoff="2024-12-31T23:59:59Z")
    assert result.high_severity_findings == 0
    assert (fixture_project / "reports/guidance_panel.csv").exists()
    assert (fixture_project / "analysis/model_results.csv").exists()
    assert (fixture_project / "reports/ranked_driver_assessment.md").exists()
    assert result.post_event_predictor_count == 0
```

- [ ] **Step 2: Confirm failure**

Run: `pytest tests/test_end_to_end.py -v`

Expected: FAIL because CLI orchestration does not exist.

- [ ] **Step 3: Implement CLI commands and deterministic run metadata**

Each command accepts `--root` and `--cutoff`; `all` runs validation, panel creation, modeling, and reporting but does not perform paid collection. Record command, package versions, cutoff, source-manifest hash, normalized-data hashes, and completion status in the validation log.

- [ ] **Step 4: Run all automated tests**

Run: `pytest -v`

Expected: all tests PASS.

- [ ] **Step 5: Run the full historical pipeline**

Run: `PYTHONPATH=src python -m abnb_guidance.cli all --root research/abnb_guidance --cutoff 2026-09-02T23:59:59-04:00`

Expected: zero high-severity validation findings; generated panel, model results, ranked assessment, unresolved-question report, and validation log exist.

- [ ] **Step 6: Validate the permanent role against the installed Codex build**

Parse the TOML with Python, verify the mandatory `developer_instructions`, then run the least-cost local Codex role-discovery or dry-run mechanism supported by the installed CLI. Record the command, Codex version, and result. Do not claim role compatibility if discovery cannot be verified; log that limitation as a research issue.

- [ ] **Step 7: Perform final evidence audit**

Select every high-impact ranked claim and trace it backward through the assessment, model result or evidence claim, exact excerpt, and source document. Select every derived target and recompute it from stored source inputs. Confirm the report uses association language and explicitly describes post-guidance shocks as a limitation of realized-cushion analysis.

- [ ] **Step 8: Deliver the research system**

Provide links to the permanent role, normalized guidance panel, schema dictionary, management-driver ledger, ranked assessment, unresolved questions, validation log, and any unexecuted Bloomberg request. State event coverage, consensus coverage, source restrictions, and all remaining high- or medium-severity issues.
