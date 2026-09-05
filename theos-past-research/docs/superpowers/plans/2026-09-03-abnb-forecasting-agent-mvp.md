# ABNB Forecasting Agent MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a project-scoped `abnb_forecasting` Codex agent, its reusable forecasting skill, and a deterministic MVP engine that validates point-in-time evidence and writes auditable guidance-forecast rehearsal packets.

**Architecture:** SOL at `xhigh` is the research control plane; a dependency-free Python package is the quantitative plane. The agent consumes reviewed manifests, timestamped human/consensus inputs, and prior targets; simple deterministic baselines anchor explicitly labeled agentic adjustments. Each run writes an immutable packet that can be independently audited. This MVP implements design phases A and B only—no model training, SARIMAX fitting, Qwen integration, reaction fitting, or cross-company pooling.

**Tech Stack:** Codex custom-agent TOML, project-local Codex skill, Python 3.12 standard library, `pytest`, JSON/CSV/Markdown artifacts, SHA-256 checksums.

**Spec:** `docs/superpowers/specs/2026-09-03-abnb-forecasting-agent-design.md`

## Global Constraints

- Preserve every pre-existing working-tree change; use new forecasting-specific files and never stage unrelated files.
- Initial runtime is exactly `gpt-5.6-sol` with `model_reasoning_effort = "xhigh"` and `sandbox_mode = "workspace-write"`.
- SOL is the control plane; deterministic Python owns timestamp validation, eligibility, arithmetic, artifact writing, and audit.
- Every usable feature must have verified availability strictly before `as_of_utc` and belong to a manifest whose status is `approved_for_forecasting`.
- Unknown, ambiguous, equal-to-cutoff, post-cutoff, unreviewed, or current-snapshot-only evidence is rejected and retained in the audit.
- Guidance from the target event, same-event shareholder letters that disclose the target, and post-event reports are prohibited inputs.
- The forecasting agent may issue an `AlternativeDataRequest`; it may not scrape directly or consume alt-data scratch work.
- Every forecast is versioned and immutable. `UPDATE` creates a new directory with a parent forecast ID.
- Licensed raw transcripts, Bloomberg exports, bank reports, credentials, and proprietary full text are never copied into forecast packets or committed.
- The first MVP-recorded weights are `agentic_weight = 1.0` and `local_llm_weight = 0.0`.
- Rehearsal data is visibly synthetic and cannot be represented as investment evidence or historical model performance.
- No training begins in this plan.

---

### Task 1: Add the Custom Agent and Project Forecasting Skill

**Files:**

- Create: `.codex/agents/abnb_forecasting.toml`
- Create: `.codex/skills/abnb-forecasting/SKILL.md`
- Create: `docs/forecasting/agent-contract.md`
- Create: `docs/forecasting/prompting-and-running.md`
- Test: `tests/test_forecasting_agent_config.py`

**Interfaces:**

- Consumes: the approved design specification and existing `abnb_alt_data` reviewed-artifact boundary.
- Produces: a Codex custom agent named `abnb_forecasting` and an automatically discoverable project skill named `abnb-forecasting`.

- [ ] **Step 1: Write the failing structural configuration test**

Create `tests/test_forecasting_agent_config.py`:

```python
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def load_agent() -> dict[str, object]:
    with (ROOT / ".codex/agents/abnb_forecasting.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_forecasting_agent_loads_with_approved_runtime() -> None:
    config = load_agent()
    assert config["name"] == "abnb_forecasting"
    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "xhigh"
    assert config["sandbox_mode"] == "workspace-write"
    assert str(config["description"]).strip()
    assert str(config["developer_instructions"]).strip()


def test_forecasting_skill_and_operator_docs_are_installed() -> None:
    assert (ROOT / ".codex/skills/abnb-forecasting/SKILL.md").is_file()
    assert (ROOT / "docs/forecasting/agent-contract.md").is_file()
    assert (ROOT / "docs/forecasting/prompting-and-running.md").is_file()
```

The break caught is a missing or misconfigured forecasting agent installation.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m pytest tests/test_forecasting_agent_config.py -q
```

Expected: FAIL because `.codex/agents/abnb_forecasting.toml` does not exist.

- [ ] **Step 3: Create the custom-agent configuration**

Create `.codex/agents/abnb_forecasting.toml` with the approved runtime and a
concise but binding developer contract. It must tell the agent to:

```toml
name = "abnb_forecasting"
description = "Point-in-time ABNB macro-to-guidance forecasting lead that produces auditable forecast packets from reviewed evidence."
model = "gpt-5.6-sol"
model_reasoning_effort = "xhigh"
sandbox_mode = "workspace-write"
developer_instructions = """
You are the agentic forecasting lead for an institutional-quality Airbnb
(NASDAQ: ABNB) stock pitch. Read the abnb-forecasting skill and
docs/forecasting/agent-contract.md before a forecasting run.

Your primary task is to forecast management guidance by translating the lawful,
point-in-time macro and operating state into management's likely policy choice.
Keep economic nowcast, guidance policy, market expectations, and stock reaction
as separately scored stages. Build the outside-view baseline before using
differentiated inside-view evidence.

Use only reviewed datasets and approved evidence manifests. Every factual input
needs a source and as-of timestamp. Reject missing, unverified, equal-to-cutoff,
post-cutoff, revised-without-vintage, or unreviewed evidence. Prior transcripts,
letters, and filings may support source-bound management-policy features only
when published strictly before the forecast cutoff. The target event's guidance
and documents that disclose it are forbidden inputs.

Use deterministic repository code for eligibility, arithmetic, baselines,
packet writing, and audit. Never replace a failed calculation with mental math.
Label each value as sourced input, computed result, human assumption, or agentic
judgment. Start from a numeric baseline and expose every signed agentic
adjustment with evidence IDs and a falsification condition.

You may request alternative data by writing a structured AlternativeDataRequest.
Do not scrape directly and do not consume the alternative-data agent's scratch
work. Accept only its reviewed dataset plus an approved evidence manifest.

Run modes are FORECAST, UPDATE, RESOLVE, and AUDIT. Freeze each packet. UPDATE
creates a new version linked to its parent and never overwrites history. Report
P10/P50/P90, assumptions, uncertainty limitations, rejected evidence, and
sensitivity. Preserve negative and inconclusive results. Do not train or tune a
model, open an untouched test period, request Bloomberg extraction, change the
target registry, add a new data family, add a local-LLM weight, or replace SOL
with Fable without the user's explicit approval.

Keep raw licensed transcripts, Bloomberg exports, bank reports, credentials,
and proprietary full text outside tracked forecast artifacts. Do not delegate
or spawn agents unless the user explicitly asks.
"""
```

- [ ] **Step 4: Create the project skill and human-facing contracts**

Create `.codex/skills/abnb-forecasting/SKILL.md` with frontmatter:

```yaml
---
name: abnb-forecasting
description: Create, update, resolve, or audit an Airbnb guidance forecast from timestamped reviewed evidence. Use for ABNB macro-to-operating-to-guidance forecasting; do not use for alternative-data collection or local-LLM training.
---
```

Its body must route `FORECAST`, `UPDATE`, `RESOLVE`, and `AUDIT`; require the
event clock and outside-view baseline first; direct the agent to use
`scripts/run_forecast_rehearsal.py`; and link to the two documents below for the
full packet contract and operator examples.

Create `docs/forecasting/agent-contract.md` as the concise operational version
of the approved design: mission, control/quantitative-plane split, four-stage
chain, evidence buckets, run modes, point-in-time gate, alt-data boundary,
immutable output, and human approval gates.

Create `docs/forecasting/prompting-and-running.md` with exact operator templates
for all four modes and the local validation/rehearsal commands. State that a new
Codex project task is needed for Codex to discover a newly added custom agent.

- [ ] **Step 5: Validate the skill and run the focused test**

Run:

```bash
python3 /Users/theomachado/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/abnb-forecasting
python3 -m pytest tests/test_forecasting_agent_config.py -q
```

Expected: skill validation succeeds and `2 passed`.

- [ ] **Step 6: Commit only Task 1 files**

```bash
git add .codex/agents/abnb_forecasting.toml .codex/skills/abnb-forecasting/SKILL.md docs/forecasting/agent-contract.md docs/forecasting/prompting-and-running.md tests/test_forecasting_agent_config.py
git commit -m "feat: add ABNB forecasting agent"
```

---

### Task 2: Implement Typed Forecast Contracts and Point-in-Time Eligibility

**Files:**

- Create: `src/abnb_forecasting/__init__.py`
- Create: `src/abnb_forecasting/contracts.py`
- Create: `src/abnb_forecasting/eligibility.py`
- Create: `research/forecasting/target_registry.csv`
- Create: `research/forecasting/runs/.gitkeep`
- Test: `tests/test_forecasting_contracts.py`
- Test: `tests/test_forecasting_eligibility.py`

**Interfaces:**

- Consumes: JSON-compatible mappings containing `ForecastRun`,
  `EvidenceManifest`, `FeatureObservation`, `HumanInput`,
  `ConsensusObservation`, `AlternativeDataRequest`, and `ForecastOutput` rows.
- Produces: `validate_record(schema_name, row) -> None`,
  `validate_run(row) -> None`, `parse_utc(value, field_name) -> datetime`, and
  `audit_features(rows, manifests, as_of_utc) -> EligibilityAudit`.

- [ ] **Step 1: Write failing contract tests**

Create `tests/test_forecasting_contracts.py` with hand-built literals:

```python
from pathlib import Path

import pytest

from abnb_forecasting.contracts import validate_record, validate_run


ROOT = Path(__file__).resolve().parents[1]


def test_forecast_run_requires_an_offset_aware_cutoff() -> None:
    row = {
        "forecast_id": "ABNB-2026Q3-20260903T120000Z",
        "forecast_version": 1,
        "ticker": "ABNB",
        "issuing_fiscal_period": "2026Q3",
        "target_event": "Q3 2026 earnings",
        "target_event_at_utc": "",
        "as_of_utc": "2026-09-03T12:00:00",
        "generated_at_utc": "2026-09-03T12:01:00Z",
        "run_mode": "FORECAST",
        "status": "workflow_rehearsal",
        "agent_model": "gpt-5.6-sol",
        "reasoning_effort": "xhigh",
        "prompt_version": "1",
        "code_revision": "test",
        "input_manifest_ids": [],
        "parent_forecast_id": "",
        "analyst_owner": "test",
        "notes": "synthetic",
    }
    with pytest.raises(ValueError, match="timezone"):
        validate_run(row)


def test_update_requires_a_parent_forecast() -> None:
    row = valid_run(run_mode="UPDATE", forecast_version=2)
    row["parent_forecast_id"] = ""
    with pytest.raises(ValueError, match="parent_forecast_id"):
        validate_run(row)


def test_manifest_validation_reports_missing_review_status() -> None:
    with pytest.raises(ValueError, match="review_status"):
        validate_record("EvidenceManifest", {"manifest_id": "M-1"})


def test_target_registry_has_the_canonical_header() -> None:
    header = (ROOT / "research/forecasting/target_registry.csv").read_text(
        encoding="utf-8"
    ).splitlines()[0]
    assert header == (
        "target_id,model_stage,metric,target_definition,target_version,"
        "issuing_fiscal_period,reference_period,guidance_type,unit,currency,"
        "constant_currency_basis,available_at_utc,source_evidence_id,"
        "comparability_status,notes"
    )
```

Define `valid_run` locally in the test with the same literal fields and valid
UTC timestamps. The breaks caught are permissive run validation, an UPDATE that
can rewrite history without ancestry, and silent schema drift.

- [ ] **Step 2: Run contract tests and verify RED**

Run:

```bash
python3 -m pytest tests/test_forecasting_contracts.py -q
```

Expected: collection ERROR because `abnb_forecasting` does not exist.

- [ ] **Step 3: Implement schemas and run validation**

Create `src/abnb_forecasting/contracts.py` with immutable field tuples for all
seven design interfaces and this public validation shape:

```python
SCHEMA_FIELDS: dict[str, tuple[str, ...]] = {
    "ForecastRun": FORECAST_RUN_FIELDS,
    "EvidenceManifest": EVIDENCE_MANIFEST_FIELDS,
    "FeatureObservation": FEATURE_OBSERVATION_FIELDS,
    "HumanInput": HUMAN_INPUT_FIELDS,
    "ConsensusObservation": CONSENSUS_OBSERVATION_FIELDS,
    "AlternativeDataRequest": ALTERNATIVE_DATA_REQUEST_FIELDS,
    "ForecastOutput": FORECAST_OUTPUT_FIELDS,
}


def validate_record(schema_name: str, row: Mapping[str, object]) -> None:
    try:
        required = SCHEMA_FIELDS[schema_name]
    except KeyError as error:
        raise ValueError(f"unknown schema {schema_name!r}") from error
    missing = [field for field in required if field not in row]
    if missing:
        raise ValueError(f"{schema_name} missing required fields: {missing}")


def validate_run(row: Mapping[str, object]) -> None:
    validate_record("ForecastRun", row)
    parse_utc(str(row["as_of_utc"]), "as_of_utc")
    parse_utc(str(row["generated_at_utc"]), "generated_at_utc")
    mode = str(row["run_mode"]).upper()
    if mode not in {"FORECAST", "UPDATE", "RESOLVE", "AUDIT"}:
        raise ValueError(f"unsupported run_mode {mode!r}")
    if mode == "UPDATE" and not str(row["parent_forecast_id"]).strip():
        raise ValueError("UPDATE requires parent_forecast_id")
```

Put the offset-aware `parse_utc` helper in `eligibility.py` and import it into
`contracts.py`. Add the package version in `__init__.py`, create the canonical
target-registry header with no data rows, and add the run-directory `.gitkeep`.

- [ ] **Step 4: Run contract tests and verify GREEN**

Run:

```bash
python3 -m pytest tests/test_forecasting_contracts.py -q
```

Expected: all contract tests pass.

- [ ] **Step 5: Write failing eligibility tests**

Create `tests/test_forecasting_eligibility.py`:

```python
from abnb_forecasting.eligibility import audit_features


CUTOFF = "2026-09-03T12:00:00Z"
APPROVED = {
    "M-1": {
        "manifest_id": "M-1",
        "review_status": "approved_for_forecasting",
    }
}


def feature(feature_id: str, available_at: str, **changes: object) -> dict[str, object]:
    row = {
        "feature_id": feature_id,
        "manifest_id": "M-1",
        "availability_status": "verified",
        "first_available_at_utc": available_at,
        "source_id": "S-1",
        "evidence_id": f"E-{feature_id}",
        "metric": "synthetic_macro_index",
        "value": 100.0,
    }
    row.update(changes)
    return row


def test_cutoff_is_strict_and_rejections_remain_auditable() -> None:
    audit = audit_features(
        [
            feature("before", "2026-09-03T11:59:59Z"),
            feature("equal", CUTOFF),
            feature("after", "2026-09-03T12:00:01Z"),
        ],
        APPROVED,
        CUTOFF,
    )
    assert [row["feature_id"] for row in audit.eligible] == ["before"]
    assert {row["feature_id"] for row in audit.rejected} == {"equal", "after"}
    assert {row["rejection_reason"] for row in audit.rejected} == {
        "not_available_strictly_before_cutoff"
    }


def test_unverified_and_unreviewed_features_are_rejected() -> None:
    audit = audit_features(
        [
            feature("unverified", "2026-09-03T11:00:00Z", availability_status="unverified"),
            feature("unknown-manifest", "2026-09-03T11:00:00Z", manifest_id="M-X"),
        ],
        APPROVED,
        CUTOFF,
    )
    assert [row["rejection_reason"] for row in audit.rejected] == [
        "availability_not_verified",
        "manifest_not_approved_for_forecasting",
    ]
```

The production mutations caught are changing `<` to `<=`, admitting unverified
history, and consuming scratch work without an approved manifest.

- [ ] **Step 6: Run eligibility tests and verify RED**

Run:

```bash
python3 -m pytest tests/test_forecasting_eligibility.py -q
```

Expected: FAIL because `audit_features` is not implemented.

- [ ] **Step 7: Implement the point-in-time audit**

In `eligibility.py`, add:

```python
@dataclass(frozen=True)
class EligibilityAudit:
    eligible: tuple[dict[str, object], ...]
    rejected: tuple[dict[str, object], ...]


def audit_features(
    rows: Iterable[Mapping[str, object]],
    manifests: Mapping[str, Mapping[str, object]],
    as_of_utc: str,
) -> EligibilityAudit:
    cutoff = parse_utc(as_of_utc, "as_of_utc")
    eligible: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    for source in rows:
        row = dict(source)
        reason = _rejection_reason(row, manifests, cutoff)
        if reason is None:
            eligible.append(row)
        else:
            row["rejection_reason"] = reason
            rejected.append(row)
    return EligibilityAudit(tuple(eligible), tuple(rejected))
```

`_rejection_reason` checks, in order: verified availability, approved manifest,
present offset-aware timestamp, then strict pre-cutoff timing. This stable order
makes each excluded row explainable.

- [ ] **Step 8: Run Task 2 tests and commit**

Run:

```bash
python3 -m pytest tests/test_forecasting_contracts.py tests/test_forecasting_eligibility.py -q
```

Expected: all tests pass.

Commit only Task 2 files:

```bash
git add src/abnb_forecasting/__init__.py src/abnb_forecasting/contracts.py src/abnb_forecasting/eligibility.py research/forecasting/target_registry.csv research/forecasting/runs/.gitkeep tests/test_forecasting_contracts.py tests/test_forecasting_eligibility.py
git commit -m "feat: enforce forecasting evidence contracts"
```

---

### Task 3: Implement Reproducible Guidance Baselines and Intervals

**Files:**

- Create: `src/abnb_forecasting/baselines.py`
- Test: `tests/test_forecasting_baselines.py`

**Interfaces:**

- Consumes: historical numeric guidance rows, an operating nowcast, historical
  policy offsets, historical range widths, and strictly prior residuals.
- Produces: `seasonal_naive(history, target_period) -> Decimal`,
  `policy_adjusted_baseline(operating_p50, policy_offsets) -> Decimal`,
  `median_range_width(widths) -> Decimal`, and
  `residual_interval(p50, residuals) -> tuple[Decimal, Decimal]`.

- [ ] **Step 1: Write failing baseline tests with hand-calculated outputs**

Create `tests/test_forecasting_baselines.py`:

```python
from decimal import Decimal

import pytest

from abnb_forecasting.baselines import (
    median_range_width,
    policy_adjusted_baseline,
    residual_interval,
    seasonal_naive,
)


def test_seasonal_naive_uses_latest_prior_same_quarter() -> None:
    history = [
        {"guided_period": "2024Q3", "guidance_midpoint": "2700"},
        {"guided_period": "2025Q2", "guidance_midpoint": "2750"},
        {"guided_period": "2025Q3", "guidance_midpoint": "3000"},
    ]
    assert seasonal_naive(history, "2026Q3") == Decimal("3000")


def test_seasonal_naive_fails_when_comparator_is_absent() -> None:
    with pytest.raises(ValueError, match="same-quarter"):
        seasonal_naive([], "2026Q3")


def test_policy_baseline_uses_median_signed_management_offset() -> None:
    assert policy_adjusted_baseline("3200", ["-100", "-50", "25"]) == Decimal("3150")


def test_range_width_and_residual_interval_are_deterministic() -> None:
    assert median_range_width(["80", "100", "120"]) == Decimal("100")
    assert residual_interval("3150", ["-200", "-100", "0", "100", "200"]) == (
        Decimal("2990.0"),
        Decimal("3310.0"),
    )
```

The expected residual interval uses linearly interpolated empirical 10th and
90th residual quantiles: `-160` and `160`.

- [ ] **Step 2: Run baseline tests and verify RED**

Run:

```bash
python3 -m pytest tests/test_forecasting_baselines.py -q
```

Expected: collection ERROR because `abnb_forecasting.baselines` is missing.

- [ ] **Step 3: Implement the minimal baseline module**

Use `Decimal` throughout. Parse `YYYYQn` with a strict regular expression.
Select only historical periods earlier than the target and then the largest year
with the same quarter. Use `statistics.median` for signed policy offsets and
range widths. Implement quantiles without a dependency:

```python
def _quantile(values: Sequence[Decimal], probability: Decimal) -> Decimal:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("at least one residual is required")
    position = Decimal(len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - Decimal(lower)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def residual_interval(
    p50: str | Decimal, residuals: Sequence[str | Decimal]
) -> tuple[Decimal, Decimal]:
    center = Decimal(p50)
    parsed = [Decimal(value) for value in residuals]
    return center + _quantile(parsed, Decimal("0.10")), center + _quantile(
        parsed, Decimal("0.90")
    )
```

Reject negative range widths and empty policy-offset/range-width/residual
histories with explicit errors.

- [ ] **Step 4: Run baseline tests and verify GREEN**

Run:

```bash
python3 -m pytest tests/test_forecasting_baselines.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit Task 3 files**

```bash
git add src/abnb_forecasting/baselines.py tests/test_forecasting_baselines.py
git commit -m "feat: add ABNB guidance baselines"
```

---

### Task 4: Build and Audit Immutable Forecast Packets

**Files:**

- Create: `src/abnb_forecasting/packet.py`
- Test: `tests/test_forecasting_packet.py`

**Interfaces:**

- Consumes: one JSON-compatible rehearsal payload containing `run`, `target`,
  `manifests`, `features`, `history`, `operating_nowcast`, `policy_offsets`,
  `range_widths`, `residuals`, `agentic_adjustments`, and optional
  `alternative_data_requests`.
- Produces: `build_packet(payload) -> dict[str, object]`,
  `write_packet(output_dir, packet) -> Path`, and
  `audit_packet(packet_dir) -> tuple[str, ...]`.

- [ ] **Step 1: Write the failing packet-construction test**

Create `tests/test_forecasting_packet.py` with a `rehearsal_payload()` literal
using only synthetic data. Include one eligible and one cutoff-equal feature,
the approved `M-1` manifest, the Task 3 history values, an operating P50 of
`3200`, policy offsets `[-100, -50, 25]`, residuals
`[-200, -100, 0, 100, 200]`, range widths `[80, 100, 120]`, and two agentic
adjustments: `+20` and `-10`.

```python
def test_packet_exposes_baseline_adjustments_and_rejected_evidence() -> None:
    packet = build_packet(rehearsal_payload())
    forecast = packet["forecast_output"]
    assert forecast["seasonal_naive_p50"] == "3000"
    assert forecast["policy_baseline_p50"] == "3150"
    assert forecast["agentic_adjustment_total"] == "10"
    assert forecast["p50"] == "3160"
    assert forecast["p10"] == "3000.0"
    assert forecast["p90"] == "3320.0"
    assert forecast["guidance_range_width_p50"] == "100"
    assert forecast["agentic_weight"] == "1.0"
    assert forecast["local_llm_weight"] == "0.0"
    assert [row["feature_id"] for row in packet["eligible_features"]] == ["before"]
    assert packet["rejected_features"][0]["rejection_reason"] == (
        "not_available_strictly_before_cutoff"
    )
    assert packet["research_claim"] == "workflow_rehearsal_not_backtest"
```

The mutation caught is an unexplained agentic forecast, use of rejected
evidence, or accidental representation of synthetic output as research skill.

- [ ] **Step 2: Run the construction test and verify RED**

Run:

```bash
python3 -m pytest tests/test_forecasting_packet.py::test_packet_exposes_baseline_adjustments_and_rejected_evidence -q
```

Expected: collection ERROR because `abnb_forecasting.packet` is missing.

- [ ] **Step 3: Implement packet construction**

`build_packet` must:

1. validate the run and required top-level keys;
2. audit all features against the run cutoff and manifests;
3. calculate seasonal and management-policy baselines;
4. require each agentic adjustment to have `label`, `amount`, `evidence_ids`,
   `rationale`, and `falsification_condition`;
5. compute P50 as policy baseline plus signed adjustments;
6. center the residual interval on adjusted P50;
7. record range width and fixed MVP weights;
8. retain both eligible and rejected rows;
9. label the packet `workflow_rehearsal_not_backtest` unless
   `research_evidence` is explicitly true—and reject `research_evidence=true`
   in the MVP to prevent an unsupported performance claim.

Use stringified `Decimal` values in JSON artifacts so representation is stable.

- [ ] **Step 4: Write failing immutability and checksum-audit tests**

Append:

```python
def test_packet_directory_is_immutable_and_checksum_is_auditable(tmp_path: Path) -> None:
    packet = build_packet(rehearsal_payload())
    packet_dir = tmp_path / "ABNB-REHEARSAL-v1"
    write_packet(packet_dir, packet)
    assert audit_packet(packet_dir) == ()

    with pytest.raises(FileExistsError):
        write_packet(packet_dir, packet)

    packet_path = packet_dir / "forecast_packet.json"
    packet_path.write_text("{}\n", encoding="utf-8")
    assert audit_packet(packet_dir) == ("forecast_packet.json checksum mismatch",)


def test_update_packet_requires_a_new_version_and_parent() -> None:
    payload = rehearsal_payload()
    payload["run"]["run_mode"] = "UPDATE"
    payload["run"]["forecast_version"] = 2
    payload["run"]["parent_forecast_id"] = "ABNB-REHEARSAL-v1"
    payload["run"]["forecast_id"] = "ABNB-REHEARSAL-v2"
    packet = build_packet(payload)
    assert packet["run"]["parent_forecast_id"] == "ABNB-REHEARSAL-v1"
```

The production breaks caught are overwriting prior forecasts, failing to detect
tampering, and creating an ancestry-free UPDATE.

- [ ] **Step 5: Implement artifact writing and audit**

`write_packet` creates the output directory with `exist_ok=False`, then writes:

```text
forecast_packet.json
eligibility_audit.csv
review_memo.md
checksums.sha256
```

Serialize JSON with `sort_keys=True`, `indent=2`, and a final newline. The CSV
contains feature ID, evidence ID, manifest ID, availability timestamp,
eligibility, and rejection reason. The memo clearly labels the run as a
workflow rehearsal and shows seasonal baseline, policy baseline, agentic
adjustments, P10/P50/P90, evidence counts, gaps, and alternative-data requests.
`checksums.sha256` stores the SHA-256 of the first three files in sorted filename
order. `audit_packet` recomputes each listed checksum and returns a tuple of
human-readable findings; it performs no writes.

- [ ] **Step 6: Run packet tests and commit**

Run:

```bash
python3 -m pytest tests/test_forecasting_packet.py -q
```

Expected: all packet tests pass.

Commit only Task 4 files:

```bash
git add src/abnb_forecasting/packet.py tests/test_forecasting_packet.py
git commit -m "feat: write auditable forecast packets"
```

---

### Task 5: Add the Rehearsal CLI and Execute the In-Session MVP

**Files:**

- Create: `scripts/run_forecast_rehearsal.py`
- Create: `tests/fixtures/forecast_rehearsal.json`
- Create: `tests/test_forecasting_cli.py`
- Modify: `docs/forecasting/prompting-and-running.md`

**Interfaces:**

- Consumes: `forecast --input PATH --output DIRECTORY` and
  `audit --packet-dir DIRECTORY` command-line arguments.
- Produces: exit code `0` and a packet/audit summary on success; exit code `1`
  with a concise error on invalid input, overwrite attempts, or audit findings.

- [ ] **Step 1: Write the failing end-to-end CLI test**

Create `tests/fixtures/forecast_rehearsal.json` with the exact synthetic payload
from Task 4 and no licensed or real investment data. Create
`tests/test_forecasting_cli.py`:

```python
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_forecast_rehearsal.py"
FIXTURE = ROOT / "tests/fixtures/forecast_rehearsal.json"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_forecast_then_audit_round_trip(tmp_path: Path) -> None:
    packet_dir = tmp_path / "packet"
    forecast = run("forecast", "--input", str(FIXTURE), "--output", str(packet_dir))
    assert forecast.returncode == 0, forecast.stderr
    assert "ABNB-MVP-REHEARSAL-v1" in forecast.stdout
    assert "workflow_rehearsal_not_backtest" in forecast.stdout

    audit = run("audit", "--packet-dir", str(packet_dir))
    assert audit.returncode == 0, audit.stderr
    assert "audit passed" in audit.stdout.casefold()


def test_forecast_refuses_to_overwrite_existing_packet(tmp_path: Path) -> None:
    packet_dir = tmp_path / "packet"
    assert run("forecast", "--input", str(FIXTURE), "--output", str(packet_dir)).returncode == 0
    second = run("forecast", "--input", str(FIXTURE), "--output", str(packet_dir))
    assert second.returncode == 1
    assert "already exists" in second.stderr
```

These tests exercise the real script and catch broken CLI wiring and mutable
forecast history.

- [ ] **Step 2: Run the CLI tests and verify RED**

Run:

```bash
python3 -m pytest tests/test_forecasting_cli.py -q
```

Expected: FAIL because the script does not exist.

- [ ] **Step 3: Implement the CLI**

Follow the repository's existing script pattern: prepend `src` to `sys.path`,
use `argparse` subparsers, load UTF-8 JSON, call `build_packet` and
`write_packet` for `forecast`, and call `audit_packet` for `audit`. Catch
`OSError`, `ValueError`, `KeyError`, `TypeError`, and `json.JSONDecodeError`,
write one error line to stderr, and return `1`. Do not catch unexpected
programming exceptions.

Successful forecast output is exactly three concise facts:

```text
forecast_id: ABNB-MVP-REHEARSAL-v1
research_claim: workflow_rehearsal_not_backtest
packet_dir: <resolved output directory>
```

Successful audit output is `Forecast packet audit passed: <resolved path>`.

- [ ] **Step 4: Run CLI tests and verify GREEN**

Run:

```bash
python3 -m pytest tests/test_forecasting_cli.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Update the runbook with the verified CLI**

Document:

```bash
python3 scripts/run_forecast_rehearsal.py forecast \
  --input tests/fixtures/forecast_rehearsal.json \
  --output /tmp/abnb-forecast-mvp/ABNB-MVP-REHEARSAL-v1
python3 scripts/run_forecast_rehearsal.py audit \
  --packet-dir /tmp/abnb-forecast-mvp/ABNB-MVP-REHEARSAL-v1
```

State that this fixture validates workflow and controls only. It contains no
real ABNB forecast and provides no backtest evidence.

- [ ] **Step 6: Run the complete repository test suite**

Run:

```bash
python3 -m pytest -q
```

Expected: all existing and new tests pass. If an unrelated concurrent change
causes a failure, report the exact failing test and do not alter that work.

- [ ] **Step 7: Validate the skill and repository policies**

Run:

```bash
python3 /Users/theomachado/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/abnb-forecasting
python3 scripts/validate_project.py --root . --expected-transcripts 23
```

Expected: the skill validator passes. The project validator must either pass or
report only a pre-existing, evidence-backed blocker; do not relax point-in-time
controls to force a pass.

- [ ] **Step 8: Execute the MVP rehearsal in a fresh temporary directory**

Run:

```bash
MVP_TMP="$(mktemp -d /tmp/abnb-forecast-mvp.XXXXXX)"
python3 scripts/run_forecast_rehearsal.py forecast --input tests/fixtures/forecast_rehearsal.json --output "$MVP_TMP/ABNB-MVP-REHEARSAL-v1"
python3 scripts/run_forecast_rehearsal.py audit --packet-dir "$MVP_TMP/ABNB-MVP-REHEARSAL-v1"
find "$MVP_TMP/ABNB-MVP-REHEARSAL-v1" -maxdepth 1 -type f -print | sort
```

Expected: forecast succeeds, audit passes, and the directory contains exactly
the four packet artifacts. Preserve the output path for the final handoff.

- [ ] **Step 9: Commit Task 5 files without staging concurrent work**

```bash
git add scripts/run_forecast_rehearsal.py tests/fixtures/forecast_rehearsal.json tests/test_forecasting_cli.py docs/forecasting/prompting-and-running.md
git commit -m "feat: run ABNB forecast rehearsal"
```

- [ ] **Step 10: Final scope and status verification**

Run:

```bash
git status --short
git log --oneline -6
```

Confirm that the implementation commits contain only forecasting-agent files
and that all pre-existing modified/untracked alt-data files remain present and
unstaged.
