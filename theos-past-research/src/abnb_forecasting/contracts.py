"""Canonical records and validation for ABNB forecast packets."""

from __future__ import annotations

from collections.abc import Mapping

from .eligibility import parse_utc


FORECAST_RUN_FIELDS = (
    "forecast_id",
    "forecast_version",
    "ticker",
    "issuing_fiscal_period",
    "target_event",
    "target_event_at_utc",
    "as_of_utc",
    "generated_at_utc",
    "run_mode",
    "status",
    "agent_model",
    "reasoning_effort",
    "prompt_version",
    "code_revision",
    "input_manifest_ids",
    "parent_forecast_id",
    "analyst_owner",
    "notes",
)

EVIDENCE_MANIFEST_FIELDS = (
    "manifest_id",
    "dataset_id",
    "dataset_version",
    "producer",
    "reviewer",
    "review_status",
    "created_at_utc",
    "coverage_start",
    "coverage_end",
    "release_lag_rule",
    "vintage_method",
    "schema_version",
    "row_count",
    "content_checksum",
    "license_class",
    "permitted_uses",
    "source_registry_ids",
    "evidence_locations",
    "known_limitations",
)

FEATURE_OBSERVATION_FIELDS = (
    "feature_id",
    "feature_definition_version",
    "manifest_id",
    "source_id",
    "evidence_id",
    "evidence_bucket",
    "metric",
    "value",
    "value_type",
    "unit",
    "currency",
    "geography",
    "reference_start",
    "reference_end",
    "observed_at_utc",
    "first_available_at_utc",
    "vintage_at_utc",
    "collected_at_utc",
    "revision_status",
    "availability_status",
    "review_status",
    "license_class",
    "transformation_id",
    "missing_reason",
)

HUMAN_INPUT_FIELDS = (
    "human_input_id",
    "submitted_at_utc",
    "valid_as_of_utc",
    "input_type",
    "claim_or_metric",
    "value",
    "unit",
    "source_evidence",
    "entitlement_status",
    "confidence",
    "analyst_name",
    "review_status",
    "notes",
)

CONSENSUS_OBSERVATION_FIELDS = (
    "expectation_id",
    "security_id",
    "provider",
    "broker_id",
    "report_id",
    "report_published_at_utc",
    "estimate_snapshot_at_utc",
    "target_period",
    "metric",
    "estimate_value",
    "unit",
    "currency",
    "estimate_basis",
    "contributor_count",
    "dispersion",
    "source_location",
    "extraction_method",
    "extractor_version",
    "review_status",
    "entitlement_status",
)

ALTERNATIVE_DATA_REQUEST_FIELDS = (
    "request_id",
    "requested_at_utc",
    "forecast_id",
    "evidence_gap",
    "target",
    "proposed_proxy",
    "economic_mechanism",
    "expected_sign",
    "required_lag",
    "geography",
    "required_history",
    "needed_by_utc",
    "minimum_coverage",
    "decision_use",
)

FORECAST_OUTPUT_FIELDS = (
    "forecast_id",
    "target_id",
    "model_stage",
    "model_specification_id",
    "baseline_id",
    "p10",
    "p50",
    "p90",
    "probability_up",
    "probability_flat",
    "probability_down",
    "outside_view_p50",
    "inside_view_adjustment",
    "management_policy_adjustment",
    "consensus_value",
    "surprise_p50",
    "interval_method",
    "training_end_at_utc",
    "effective_sample_size",
    "evidence_ids",
    "sensitivity_ids",
    "warnings",
)

TARGET_REGISTRY_FIELDS = (
    "target_id",
    "model_stage",
    "metric",
    "target_definition",
    "target_version",
    "issuing_fiscal_period",
    "reference_period",
    "guidance_type",
    "unit",
    "currency",
    "constant_currency_basis",
    "available_at_utc",
    "source_evidence_id",
    "comparability_status",
    "notes",
)

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
    """Require the canonical fields for one named record type."""
    try:
        required = SCHEMA_FIELDS[schema_name]
    except KeyError as error:
        raise ValueError(f"unknown schema {schema_name!r}") from error
    missing = [field for field in required if field not in row]
    if missing:
        raise ValueError(f"{schema_name} missing required fields: {missing}")


def validate_run(row: Mapping[str, object]) -> None:
    """Validate the identity, mode, and event clock for a forecast run."""
    validate_record("ForecastRun", row)
    cutoff = parse_utc(str(row["as_of_utc"]), "as_of_utc")
    parse_utc(str(row["generated_at_utc"]), "generated_at_utc")

    event_value = str(row["target_event_at_utc"]).strip()
    if event_value and cutoff >= parse_utc(event_value, "target_event_at_utc"):
        raise ValueError("as_of_utc must be strictly before target_event_at_utc")

    mode = str(row["run_mode"]).upper()
    if mode not in {"FORECAST", "UPDATE", "RESOLVE", "AUDIT"}:
        raise ValueError(f"unsupported run_mode {mode!r}")

    version = row["forecast_version"]
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ValueError("forecast_version must be a positive integer")
    if mode == "UPDATE":
        if version < 2:
            raise ValueError("UPDATE forecast_version must be at least 2")
        if not str(row["parent_forecast_id"]).strip():
            raise ValueError("UPDATE requires parent_forecast_id")
    if mode == "FORECAST" and str(row["parent_forecast_id"]).strip():
        raise ValueError("FORECAST cannot have parent_forecast_id")

    if not isinstance(row["input_manifest_ids"], list):
        raise ValueError("input_manifest_ids must be a list")
