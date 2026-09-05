"""Construction and storage of auditable ABNB forecast packets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path

from .baselines import (
    median_range_width,
    policy_adjusted_baseline,
    residual_interval,
    seasonal_naive,
)
from .contracts import validate_record, validate_run
from .eligibility import audit_features


_REQUIRED_PAYLOAD_KEYS = (
    "run",
    "target",
    "manifests",
    "features",
    "history",
    "operating_nowcast",
    "policy_offsets",
    "range_widths",
    "residuals",
    "agentic_adjustments",
    "alternative_data_requests",
    "research_evidence",
)

_REQUIRED_ADJUSTMENT_KEYS = (
    "label",
    "amount",
    "evidence_ids",
    "rationale",
    "falsification_condition",
)


def _mapping(value: object, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object")
    return value


def _sequence(value: object, field_name: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field_name} must be a list")
    return value


def _decimal(value: object, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{field_name} must be numeric") from error


def _require_keys(row: Mapping[str, object], keys: Sequence[str], name: str) -> None:
    missing = [key for key in keys if key not in row]
    if missing:
        raise ValueError(f"{name} missing required fields: {missing}")


def _manifest_index(rows: Sequence[object]) -> dict[str, Mapping[str, object]]:
    manifests: dict[str, Mapping[str, object]] = {}
    for source in rows:
        row = _mapping(source, "manifest")
        validate_record("EvidenceManifest", row)
        manifest_id = str(row["manifest_id"])
        if not manifest_id:
            raise ValueError("manifest_id cannot be empty")
        if manifest_id in manifests:
            raise ValueError(f"duplicate manifest_id {manifest_id!r}")
        manifests[manifest_id] = row
    return manifests


def _validate_adjustments(
    rows: Sequence[object], eligible_evidence_ids: set[str]
) -> tuple[list[dict[str, object]], Decimal]:
    adjustments: list[dict[str, object]] = []
    total = Decimal("0")
    for source in rows:
        row = dict(_mapping(source, "agentic adjustment"))
        _require_keys(row, _REQUIRED_ADJUSTMENT_KEYS, "agentic adjustment")
        evidence_ids = _sequence(row["evidence_ids"], "evidence_ids")
        if not evidence_ids:
            raise ValueError("agentic adjustment requires eligible evidence")
        unknown = sorted(
            str(evidence_id)
            for evidence_id in evidence_ids
            if str(evidence_id) not in eligible_evidence_ids
        )
        if unknown:
            raise ValueError(
                f"agentic adjustment must cite eligible evidence; rejected={unknown}"
            )
        amount = _decimal(row["amount"], "agentic adjustment amount")
        row["amount"] = str(amount)
        adjustments.append(row)
        total += amount
    return adjustments, total


def build_packet(payload: Mapping[str, object]) -> dict[str, object]:
    """Build one deterministic workflow-rehearsal packet from typed inputs."""
    _require_keys(payload, _REQUIRED_PAYLOAD_KEYS, "forecast payload")
    if payload["research_evidence"] is not False:
        raise ValueError("MVP accepts workflow rehearsal data only")

    run = dict(_mapping(payload["run"], "run"))
    validate_run(run)
    target = dict(_mapping(payload["target"], "target"))
    _require_keys(
        target,
        ("target_id", "model_stage", "metric", "guided_period", "unit", "currency"),
        "target",
    )

    manifest_rows = _sequence(payload["manifests"], "manifests")
    manifests = _manifest_index(manifest_rows)
    missing_manifests = sorted(set(run["input_manifest_ids"]) - set(manifests))
    if missing_manifests:
        raise ValueError(f"run references missing manifests: {missing_manifests}")

    feature_rows = _sequence(payload["features"], "features")
    for feature in feature_rows:
        validate_record("FeatureObservation", _mapping(feature, "feature"))
    feature_audit = audit_features(feature_rows, manifests, str(run["as_of_utc"]))
    eligible_evidence_ids = {
        str(row["evidence_id"]) for row in feature_audit.eligible
    }

    adjustments, adjustment_total = _validate_adjustments(
        _sequence(payload["agentic_adjustments"], "agentic_adjustments"),
        eligible_evidence_ids,
    )

    history = _sequence(payload["history"], "history")
    operating_nowcast = _mapping(payload["operating_nowcast"], "operating_nowcast")
    if "p50" not in operating_nowcast:
        raise ValueError("operating_nowcast missing required field: p50")
    operating_p50 = _decimal(operating_nowcast["p50"], "operating_nowcast p50")
    seasonal = seasonal_naive(history, str(target["guided_period"]))
    policy = policy_adjusted_baseline(
        operating_p50,
        _sequence(payload["policy_offsets"], "policy_offsets"),
    )
    width = median_range_width(
        _sequence(payload["range_widths"], "range_widths")
    )
    p50 = policy + adjustment_total
    p10, p90 = residual_interval(
        p50,
        _sequence(payload["residuals"], "residuals"),
    )

    alternative_requests: list[dict[str, object]] = []
    for source in _sequence(
        payload["alternative_data_requests"], "alternative_data_requests"
    ):
        request = dict(_mapping(source, "alternative data request"))
        validate_record("AlternativeDataRequest", request)
        alternative_requests.append(request)

    forecast_output = {
        "forecast_id": run["forecast_id"],
        "target_id": target["target_id"],
        "model_stage": target["model_stage"],
        "model_specification_id": "mvp-agentic-policy-v1",
        "baseline_id": "seasonal-and-median-policy-v1",
        "seasonal_naive_p50": str(seasonal),
        "operating_nowcast_p50": str(operating_p50),
        "policy_baseline_p50": str(policy),
        "agentic_adjustment_total": str(adjustment_total),
        "p10": str(p10),
        "p50": str(p50),
        "p90": str(p90),
        "guidance_range_width_p50": str(width),
        "guidance_range_low_p50": str(p50 - width / Decimal("2")),
        "guidance_range_high_p50": str(p50 + width / Decimal("2")),
        "probability_up": None,
        "probability_flat": None,
        "probability_down": None,
        "outside_view_p50": str(seasonal),
        "inside_view_adjustment": str(adjustment_total),
        "management_policy_adjustment": str(policy - operating_p50),
        "consensus_value": None,
        "surprise_p50": None,
        "interval_method": "empirical_prior_residual_quantiles_10_90",
        "training_end_at_utc": None,
        "effective_sample_size": len(_sequence(payload["residuals"], "residuals")),
        "evidence_ids": sorted(eligible_evidence_ids),
        "sensitivity_ids": [],
        "warnings": [
            "Synthetic workflow rehearsal only.",
            "Interval coverage has not been calibrated on historical ABNB forecasts.",
        ],
        "agentic_weight": "1.0",
        "local_llm_weight": "0.0",
    }

    return {
        "packet_schema_version": "1",
        "research_claim": "workflow_rehearsal_not_backtest",
        "run": run,
        "target": target,
        "manifests": [dict(row) for row in manifest_rows],
        "eligible_features": list(feature_audit.eligible),
        "rejected_features": list(feature_audit.rejected),
        "operating_nowcast": dict(operating_nowcast),
        "agentic_adjustments": adjustments,
        "alternative_data_requests": alternative_requests,
        "forecast_output": forecast_output,
    }


_ARTIFACT_NAMES = (
    "eligibility_audit.csv",
    "forecast_packet.json",
    "review_memo.md",
)


def _json_text(packet: Mapping[str, object]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def _eligibility_csv(packet: Mapping[str, object]) -> str:
    fields = (
        "feature_id",
        "evidence_id",
        "manifest_id",
        "first_available_at_utc",
        "eligible",
        "rejection_reason",
    )
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for source in packet["eligible_features"]:
        row = _mapping(source, "eligible feature")
        writer.writerow(
            {
                "feature_id": row.get("feature_id", ""),
                "evidence_id": row.get("evidence_id", ""),
                "manifest_id": row.get("manifest_id", ""),
                "first_available_at_utc": row.get("first_available_at_utc", ""),
                "eligible": "true",
                "rejection_reason": "",
            }
        )
    for source in packet["rejected_features"]:
        row = _mapping(source, "rejected feature")
        writer.writerow(
            {
                "feature_id": row.get("feature_id", ""),
                "evidence_id": row.get("evidence_id", ""),
                "manifest_id": row.get("manifest_id", ""),
                "first_available_at_utc": row.get("first_available_at_utc", ""),
                "eligible": "false",
                "rejection_reason": row.get("rejection_reason", ""),
            }
        )
    return buffer.getvalue()


def _review_memo(packet: Mapping[str, object]) -> str:
    run = _mapping(packet["run"], "run")
    target = _mapping(packet["target"], "target")
    forecast = _mapping(packet["forecast_output"], "forecast_output")
    adjustments = _sequence(packet["agentic_adjustments"], "agentic_adjustments")
    requests = _sequence(
        packet["alternative_data_requests"], "alternative_data_requests"
    )
    lines = [
        "# ABNB Forecast Workflow Rehearsal",
        "",
        "> This packet is a synthetic workflow rehearsal, not a historical",
        "> backtest, investment forecast, alpha estimate, or measure of accuracy.",
        "",
        f"- Forecast ID: `{run['forecast_id']}`",
        f"- Mode: `{run['run_mode']}`",
        f"- Information cutoff: `{run['as_of_utc']}`",
        f"- Target: `{target['target_id']}`",
        f"- Eligible features: {len(packet['eligible_features'])}",
        f"- Rejected features: {len(packet['rejected_features'])}",
        "",
        "## Quantitative bridge",
        "",
        f"- Seasonal-naive P50: {forecast['seasonal_naive_p50']}",
        f"- Operating-nowcast P50: {forecast['operating_nowcast_p50']}",
        f"- Management-policy baseline P50: {forecast['policy_baseline_p50']}",
        f"- Agentic adjustment total: {forecast['agentic_adjustment_total']}",
        f"- Guidance forecast P10/P50/P90: {forecast['p10']} / {forecast['p50']} / {forecast['p90']}",
        f"- Forecast range width P50: {forecast['guidance_range_width_p50']}",
        "",
        "## Agentic adjustments",
        "",
    ]
    for source in adjustments:
        row = _mapping(source, "agentic adjustment")
        lines.extend(
            [
                f"- **{row['label']} ({row['amount']}):** {row['rationale']}",
                f"  Falsified when: {row['falsification_condition']}",
            ]
        )
    if not adjustments:
        lines.append("- None.")
    lines.extend(["", "## Alternative-data requests", ""])
    if requests:
        for source in requests:
            row = _mapping(source, "alternative data request")
            lines.append(f"- `{row['request_id']}`: {row['evidence_gap']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    for warning in forecast["warnings"]:
        lines.append(f"- {warning}")
    return "\n".join(lines) + "\n"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_packet(output_dir: Path, packet: Mapping[str, object]) -> Path:
    """Write one packet to a newly created directory and refuse overwrites."""
    output_dir = Path(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(exist_ok=False)

    artifacts = {
        "forecast_packet.json": _json_text(packet),
        "eligibility_audit.csv": _eligibility_csv(packet),
        "review_memo.md": _review_memo(packet),
    }
    for name, text in artifacts.items():
        (output_dir / name).write_text(text, encoding="utf-8")
    checksums = "".join(
        f"{_sha256(artifacts[name])}  {name}\n" for name in sorted(artifacts)
    )
    (output_dir / "checksums.sha256").write_text(checksums, encoding="utf-8")
    return output_dir


def audit_packet(packet_dir: Path) -> tuple[str, ...]:
    """Return checksum findings for a packet without modifying it."""
    packet_dir = Path(packet_dir)
    checksum_path = packet_dir / "checksums.sha256"
    if not checksum_path.is_file():
        return ("checksums.sha256 missing",)

    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", maxsplit=1)
        if len(parts) != 2:
            return ("checksums.sha256 is malformed",)
        digest, name = parts
        expected[name] = digest

    findings: list[str] = []
    for name in _ARTIFACT_NAMES:
        path = packet_dir / name
        if not path.is_file():
            findings.append(f"{name} missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected.get(name) != actual:
            findings.append(f"{name} checksum mismatch")
    return tuple(findings)
