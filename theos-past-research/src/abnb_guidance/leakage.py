"""Information-clock eligibility decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .types import AvailabilityClass


@dataclass(frozen=True)
class FeatureObservation:
    observation_id: str
    availability_class: AvailabilityClass | str
    public_available_at_utc: datetime | None = None
    known_to_management_by_utc: datetime | None = None


@dataclass(frozen=True)
class EligibilityDecision:
    eligible: bool
    reason_code: str
    detail: str


def _is_aware(value: datetime | None) -> bool:
    return value is not None and value.tzinfo is not None and value.utcoffset() is not None


def eligible_for_view(
    observation: FeatureObservation,
    event_time: datetime,
    view: str,
) -> EligibilityDecision:
    if not _is_aware(event_time):
        raise ValueError("event_time must be timezone-aware")
    availability = AvailabilityClass(observation.availability_class)
    if availability == AvailabilityClass.POST_EVENT_INELIGIBLE:
        return EligibilityDecision(False, "post_event", "observation is explicitly post-event")

    public_prior = (
        availability == AvailabilityClass.PUBLIC_PRIOR
        and _is_aware(observation.public_available_at_utc)
        and observation.public_available_at_utc < event_time
    )
    management_known = (
        _is_aware(observation.known_to_management_by_utc)
        and observation.known_to_management_by_utc <= event_time
    )

    if view == "public_prior_view":
        if public_prior:
            return EligibilityDecision(True, "public_prior", "strictly public before event")
        return EligibilityDecision(False, "not_public_prior", "no verified timestamp before event")

    if view == "management_information_view":
        if public_prior:
            return EligibilityDecision(True, "public_prior", "strictly public before event")
        if availability == AvailabilityClass.CONTEMPORANEOUS_MANAGEMENT_KNOWN and management_known:
            return EligibilityDecision(True, "management_known", "known by management no later than event")
        if availability == AvailabilityClass.MANAGEMENT_PRIVATE_PROXY:
            return EligibilityDecision(False, "proxy_requires_separate_view", "private proxy excluded from primary view")
        return EligibilityDecision(False, "availability_unverified", "management availability is not verified")

    if view == "management_proxy_view":
        if public_prior:
            return EligibilityDecision(True, "public_prior", "strictly public before event")
        if availability in {
            AvailabilityClass.CONTEMPORANEOUS_MANAGEMENT_KNOWN,
            AvailabilityClass.MANAGEMENT_PRIVATE_PROXY,
        } and management_known:
            return EligibilityDecision(True, "management_proxy", "eligible only in proxy view")
        return EligibilityDecision(False, "availability_unverified", "management availability is not verified")

    raise ValueError(f"unknown information view: {view}")
