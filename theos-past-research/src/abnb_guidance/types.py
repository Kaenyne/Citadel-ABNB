"""Shared controlled vocabularies for the guidance dataset."""

from enum import StrEnum


class ValueStatus(StrEnum):
    OBSERVED = "observed"
    MISSING = "missing"
    NOT_DISCLOSED = "not_disclosed"
    NOT_APPLICABLE = "not_applicable"


class AvailabilityClass(StrEnum):
    PUBLIC_PRIOR = "public_prior"
    CONTEMPORANEOUS_MANAGEMENT_KNOWN = "contemporaneous_management_known"
    MANAGEMENT_PRIVATE_PROXY = "management_private_proxy"
    POST_EVENT_INELIGIBLE = "post_event_ineligible"


class EvidenceStance(StrEnum):
    SUPPORTING = "supporting"
    CONTRADICTORY = "contradictory"
    MIXED = "mixed"
    NEUTRAL = "neutral"
    NEGATIVE_EVIDENCE = "negative_evidence"


class AttributionStrength(StrEnum):
    DRIVER = "driver"
    CONTRIBUTOR = "contributor"
    RISK = "risk"
    CONTEXTUAL_CORRELATION = "contextual_correlation"
    NO_ATTRIBUTION = "no_attribution"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class QualityGrade(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class LeakageRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


class EventType(StrEnum):
    INITIAL = "initial"
    CLARIFICATION = "clarification"
    REVISION = "revision"


class AccountingBasis(StrEnum):
    GAAP = "GAAP"
    NON_GAAP = "non_GAAP"
    OPERATING = "operating"
    NOT_APPLICABLE = "not_applicable"


class IssueStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    ACCEPTED_LIMITATION = "accepted_limitation"


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReleaseTiming(StrEnum):
    BEFORE_OPEN = "before_open"
    INTRADAY = "intraday"
    AFTER_CLOSE = "after_close"
    NON_TRADING_DAY = "non_trading_day"
    UNKNOWN = "unknown"


class TimestampPrecision(StrEnum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DATE = "date"
    UNKNOWN = "unknown"
