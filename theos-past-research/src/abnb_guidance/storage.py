"""Deterministic storage and cross-table validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from .records import PRIMARY_KEYS, TABLE_MODELS


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    table: str
    record_id: str | None
    message: str
    severity: str = "high"


def table_path(table_name: str, root: Path, suffix: str = "csv") -> Path:
    if table_name not in TABLE_MODELS:
        raise KeyError(f"unknown table: {table_name}")
    if table_name == "source_documents":
        return root / "data" / "manifests" / f"source_documents.{suffix}"
    return root / "data" / "normalized" / f"{table_name}.{suffix}"


def _clean_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in mapping.items():
        if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
            cleaned[key] = None
        elif isinstance(value, str) and not value.strip():
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned


def _validated_frame(table_name: str, frame: pd.DataFrame) -> pd.DataFrame:
    model = TABLE_MODELS[table_name]
    columns = list(model.model_fields)
    records: list[dict[str, Any]] = []
    for raw in frame.to_dict(orient="records"):
        parsed = model.model_validate(_clean_mapping(raw))
        records.append(parsed.model_dump(mode="json"))
    return pd.DataFrame(records, columns=columns)


def write_table(table_name: str, frame: pd.DataFrame, root: Path) -> None:
    root = Path(root)
    validated = _validated_frame(table_name, frame)
    csv_path = table_path(table_name, root, "csv")
    parquet_path = table_path(table_name, root, "parquet")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    validated.to_csv(csv_path, index=False, lineterminator="\n")
    validated.to_parquet(parquet_path, index=False)


def load_table(table_name: str, root: Path) -> pd.DataFrame:
    path = table_path(table_name, Path(root), "csv")
    if not path.exists():
        return pd.DataFrame(columns=list(TABLE_MODELS[table_name].model_fields))
    return pd.read_csv(path, keep_default_na=False)


def create_templates(root: Path) -> None:
    root = Path(root)
    for table_name, model in TABLE_MODELS.items():
        path = table_path(table_name, root, "csv")
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=list(model.model_fields)).to_csv(
            path, index=False, lineterminator="\n"
        )


def export_json_schemas(path: Path) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    for table_name, model in TABLE_MODELS.items():
        schema_path = path / f"{table_name}.schema.json"
        schema_path.write_text(
            json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


FOREIGN_KEYS: tuple[tuple[str, str, str, str], ...] = (
    ("guidance_events", "primary_document_id", "source_documents", "document_id"),
    ("guidance_items", "guidance_event_id", "guidance_events", "guidance_event_id"),
    ("guidance_items", "source_excerpt_id", "source_excerpts", "source_excerpt_id"),
    ("quarterly_actuals", "source_excerpt_id", "source_excerpts", "source_excerpt_id"),
    ("consensus_snapshots", "guidance_event_id", "guidance_events", "guidance_event_id"),
    ("consensus_snapshots", "source_document_id", "source_documents", "document_id"),
    ("driver_observations", "guidance_event_id", "guidance_events", "guidance_event_id"),
    ("driver_observations", "source_excerpt_id", "source_excerpts", "source_excerpt_id"),
    ("source_excerpts", "document_id", "source_documents", "document_id"),
    ("evidence_claims", "guidance_event_id", "guidance_events", "guidance_event_id"),
    ("evidence_claims", "source_excerpt_id", "source_excerpts", "source_excerpt_id"),
    ("market_returns", "guidance_event_id", "guidance_events", "guidance_event_id"),
    ("model_results", "test_event_id", "guidance_events", "guidance_event_id"),
)


def validate_dataset(root: Path) -> list[ValidationFinding]:
    root = Path(root)
    findings: list[ValidationFinding] = []
    frames = {name: load_table(name, root) for name in TABLE_MODELS}

    for table_name, frame in frames.items():
        primary_key = PRIMARY_KEYS[table_name]
        if primary_key in frame.columns and not frame.empty:
            duplicated = frame[primary_key].astype(str).duplicated(keep=False)
            for record_id in frame.loc[duplicated, primary_key].astype(str).unique():
                findings.append(
                    ValidationFinding(
                        code="duplicate_primary_key",
                        table=table_name,
                        record_id=record_id,
                        message=f"duplicate {primary_key}: {record_id}",
                    )
                )
        model = TABLE_MODELS[table_name]
        for row_number, raw in enumerate(frame.to_dict(orient="records"), start=2):
            try:
                model.model_validate(_clean_mapping(raw))
            except ValidationError as exc:
                record_id = str(raw.get(primary_key) or "") or None
                findings.append(
                    ValidationFinding(
                        code="invalid_record",
                        table=table_name,
                        record_id=record_id,
                        message=f"row {row_number}: {exc.errors(include_url=False)}",
                    )
                )

    for child_table, child_field, parent_table, parent_field in FOREIGN_KEYS:
        child = frames[child_table]
        parent = frames[parent_table]
        if child.empty or child_field not in child.columns:
            continue
        parent_values = set(parent[parent_field].astype(str)) if parent_field in parent.columns else set()
        for _, row in child.iterrows():
            value = str(row.get(child_field, "")).strip()
            if value and value not in parent_values:
                findings.append(
                    ValidationFinding(
                        code="missing_foreign_key",
                        table=child_table,
                        record_id=str(row.get(PRIMARY_KEYS[child_table], "")) or None,
                        message=f"{child_field}={value} not found in {parent_table}.{parent_field}",
                    )
                )

    return findings


def append_validation_log(log_path: Path, command: str, result: str) -> None:
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().isoformat()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {timestamp} | `{command}` | {result}\n")
