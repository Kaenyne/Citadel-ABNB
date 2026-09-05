"""Typed records for every canonical research table."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from .types import (
    AccountingBasis,
    AttributionStrength,
    AvailabilityClass,
    Confidence,
    EventType,
    EvidenceStance,
    IssueStatus,
    LeakageRisk,
    QualityGrade,
    ReleaseTiming,
    Severity,
    TimestampPrecision,
    ValueStatus,
)


def _timezone_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value


FiscalPeriod = Annotated[str, Field(pattern=r"^[0-9]{4}Q[1-4]$")]
AwareDateTime = Annotated[datetime, AfterValidator(_timezone_aware)]


class CanonicalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    value_status: ValueStatus = ValueStatus.OBSERVED
    missing_reason: str | None = None

    @model_validator(mode="after")
    def require_missing_reason(self) -> "CanonicalRecord":
        if self.value_status != ValueStatus.OBSERVED and not self.missing_reason:
            raise ValueError("missing_reason is required when value_status is not observed")
        return self


class GuidanceEvent(CanonicalRecord):
    guidance_event_id: str
    issuer_id: str
    reported_period: FiscalPeriod
    event_type: EventType
    published_at_utc: AwareDateTime
    published_at_precision: TimestampPrecision
    release_timing: ReleaseTiming
    research_cutoff_at_utc: AwareDateTime
    initial_event_id: str | None = None
    is_initial_guide: bool
    primary_document_id: str | None = None
    event_notes: str | None = None


class GuidanceItem(CanonicalRecord):
    guidance_item_id: str
    guidance_event_id: str
    target_period: FiscalPeriod
    metric_code: str
    measure_type: str
    value_low: float | None = None
    value_high: float | None = None
    value_mid: float | None = None
    unit: str
    currency: str | None = None
    accounting_basis: AccountingBasis
    is_company_stated: bool
    derivation_formula: str | None = None
    comparator_period: FiscalPeriod | None = None
    source_excerpt_id: str | None = None
    extraction_confidence: Confidence

    @model_validator(mode="after")
    def validate_range_and_derivation(self) -> "GuidanceItem":
        if self.value_low is not None and self.value_high is not None:
            if self.value_low > self.value_high:
                raise ValueError("value_low cannot exceed value_high")
            if self.value_mid is not None and not self.value_low <= self.value_mid <= self.value_high:
                raise ValueError("value_mid must lie within the guidance range")
        if not self.is_company_stated and not self.derivation_formula:
            raise ValueError("derivation_formula is required for a derived guidance item")
        return self


class QuarterlyActual(CanonicalRecord):
    actual_observation_id: str
    fiscal_period: FiscalPeriod
    metric_code: str
    scope_code: str
    value: float | None = None
    unit: str
    currency: str | None = None
    accounting_basis: AccountingBasis
    yoy_growth_reported: float | None = None
    yoy_growth_constant_currency: float | None = None
    is_company_stated: bool
    derivation_formula: str | None = None
    public_available_at_utc: AwareDateTime | None = None
    source_excerpt_id: str | None = None

    @model_validator(mode="after")
    def require_derivation(self) -> "QuarterlyActual":
        if not self.is_company_stated and not self.derivation_formula:
            raise ValueError("derivation_formula is required for a derived actual")
        return self


class ConsensusSnapshot(CanonicalRecord):
    consensus_snapshot_id: str
    guidance_event_id: str
    target_period: FiscalPeriod
    metric_code: str
    statistic_type: str
    value: float | None = None
    unit: str
    currency: str | None = None
    analyst_count: int | None = None
    snapshot_at_utc: AwareDateTime | None = None
    snapshot_precision: TimestampPrecision
    snapshot_age_hours: float | None = None
    is_strictly_pre_event: bool
    point_in_time_verified: bool
    source_name: str
    license_or_access_basis: str
    source_document_id: str | None = None
    quality_grade: QualityGrade


class DriverObservation(CanonicalRecord):
    driver_observation_id: str
    guidance_event_id: str
    driver_family: str
    driver_code: str
    value_numeric: float | None = None
    value_category: str | None = None
    unit: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    scope_code: str
    direction_interpretation: str | None = None
    availability_class: AvailabilityClass
    known_to_management_by_utc: AwareDateTime | None = None
    public_available_at_utc: AwareDateTime | None = None
    is_derived: bool
    derivation_formula: str | None = None
    source_excerpt_id: str | None = None
    quality_grade: QualityGrade
    leakage_risk: LeakageRisk
    leakage_notes: str | None = None

    @model_validator(mode="after")
    def require_derivation(self) -> "DriverObservation":
        if self.is_derived and not self.derivation_formula:
            raise ValueError("derivation_formula is required for a derived driver")
        if self.value_numeric is None and self.value_category is None and self.value_status == ValueStatus.OBSERVED:
            raise ValueError("an observed driver needs a numeric or categorical value")
        return self


class SourceDocument(CanonicalRecord):
    document_id: str
    document_type: str
    title: str
    publisher: str
    source_url: str
    canonical_url: str
    fiscal_period: FiscalPeriod | None = None
    document_date: date | None = None
    published_at_utc: AwareDateTime | None = None
    sec_accession_number: str | None = None
    retrieved_at_utc: AwareDateTime | None = None
    capture_method: str
    mime_type: str | None = None
    local_path: str | None = None
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    rights_or_access_note: str
    version_status: str
    supersedes_document_id: str | None = None


class SourceExcerpt(CanonicalRecord):
    source_excerpt_id: str
    document_id: str
    page_number: int | None = Field(default=None, ge=1)
    section_heading: str | None = None
    speaker: str | None = None
    timecode: str | None = None
    source_anchor: str | None = None
    exact_excerpt: str
    excerpt_word_count: int = Field(ge=1)
    context_paraphrase: str
    copyright_handling: str
    extraction_method: str
    verified_against_source: bool


class EvidenceClaim(CanonicalRecord):
    evidence_claim_id: str
    guidance_event_id: str
    source_excerpt_id: str
    driver_family: str
    driver_code: str
    claim_type: str
    evidence_stance: EvidenceStance
    direction: str
    attribution_strength: AttributionStrength
    time_horizon: str
    scope_code: str
    quantified_value: float | None = None
    quantified_unit: str | None = None
    coder_confidence: Confidence
    contradicts_claim_id: str | None = None
    adjudication_note: str | None = None


class MarketReturn(CanonicalRecord):
    market_return_id: str
    guidance_event_id: str
    instrument: str
    benchmark: str | None = None
    reaction_session_date: date
    window_sessions: int = Field(gt=0)
    price_adjustment: str
    raw_total_return: float | None = None
    benchmark_total_return: float | None = None
    excess_return: float | None = None
    price_source: str
    source_as_of_utc: AwareDateTime
    quality_grade: QualityGrade


class ModelResult(CanonicalRecord):
    model_result_id: str
    target_code: str
    information_view: str
    baseline_code: str
    specification_code: str
    train_start_event_id: str
    train_end_event_id: str
    test_event_id: str
    feature_codes: str
    prediction: float | None = None
    actual_target_value: float | None = None
    absolute_error: float | None = None
    squared_error: float | None = None
    baseline_absolute_error: float | None = None
    error_improvement: float | None = None
    fit_warnings: str | None = None
    random_seed: int
    code_version: str
    created_at_utc: AwareDateTime


class ResearchIssue(CanonicalRecord):
    research_issue_id: str
    issue_type: str
    severity: Severity
    guidance_event_id: str | None = None
    related_record_type: str | None = None
    related_record_id: str | None = None
    description: str
    proposed_resolution: str
    status: IssueStatus
    requires_user_approval: bool
    created_at_utc: AwareDateTime
    resolved_at_utc: AwareDateTime | None = None


TABLE_MODELS: dict[str, type[CanonicalRecord]] = {
    "guidance_events": GuidanceEvent,
    "guidance_items": GuidanceItem,
    "quarterly_actuals": QuarterlyActual,
    "consensus_snapshots": ConsensusSnapshot,
    "driver_observations": DriverObservation,
    "source_documents": SourceDocument,
    "source_excerpts": SourceExcerpt,
    "evidence_claims": EvidenceClaim,
    "market_returns": MarketReturn,
    "model_results": ModelResult,
    "research_issues": ResearchIssue,
}

PRIMARY_KEYS: dict[str, str] = {
    "guidance_events": "guidance_event_id",
    "guidance_items": "guidance_item_id",
    "quarterly_actuals": "actual_observation_id",
    "consensus_snapshots": "consensus_snapshot_id",
    "driver_observations": "driver_observation_id",
    "source_documents": "document_id",
    "source_excerpts": "source_excerpt_id",
    "evidence_claims": "evidence_claim_id",
    "market_returns": "market_return_id",
    "model_results": "model_result_id",
    "research_issues": "research_issue_id",
}


def primary_key_for(table_name: str) -> str:
    return PRIMARY_KEYS[table_name]
