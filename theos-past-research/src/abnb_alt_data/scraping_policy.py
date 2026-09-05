"""Deterministic safety gate for autonomous public-web collection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


TermsStatus = Literal["allowed", "prohibited", "unclear"]
RobotsStatus = Literal["allowed", "disallowed", "unclear"]
MAX_AUTONOMOUS_REQUESTS_PER_MINUTE = 10


@dataclass(frozen=True)
class ScrapeCandidate:
    """Inputs that must be established before an autonomous scrape begins."""

    source_id: str
    public_access: bool
    terms_url: str
    terms_status: TermsStatus
    robots_url: str
    robots_status: RobotsStatus
    intended_paths: tuple[str, ...]
    authenticated: bool
    paywalled: bool
    captcha_required: bool
    access_control_bypass: bool
    personal_data: bool
    airbnb_controlled: bool
    explicit_airbnb_automation_permission: bool
    requests_per_minute: int
    cache_responses: bool
    user_agent: str


@dataclass(frozen=True)
class ScrapeDecision:
    """Auditable decision returned by :func:`assess_scrape_candidate`."""

    allowed: bool
    reasons: tuple[str, ...]


def assess_scrape_candidate(candidate: ScrapeCandidate) -> ScrapeDecision:
    """Allow only low-rate, documented, clearly permitted public collection."""
    reasons: list[str] = []

    if not candidate.public_access:
        reasons.append("source is not publicly accessible")
    if not candidate.terms_url.strip():
        reasons.append("terms URL is missing")
    if candidate.terms_status == "prohibited":
        reasons.append("terms prohibit automated collection")
    elif candidate.terms_status != "allowed":
        reasons.append("terms do not clearly permit automation")
    if not candidate.robots_url.strip():
        reasons.append("robots URL is missing")
    if candidate.robots_status == "disallowed":
        reasons.append("robots guidance disallows the intended paths")
    elif candidate.robots_status != "allowed":
        reasons.append("robots guidance does not clearly allow the intended paths")
    if not candidate.intended_paths:
        reasons.append("intended paths are missing")
    if candidate.authenticated:
        reasons.append("authentication is required")
    if candidate.paywalled:
        reasons.append("content is paywalled")
    if candidate.captcha_required:
        reasons.append("CAPTCHA is required")
    if candidate.access_control_bypass:
        reasons.append("collection would bypass access controls")
    if candidate.personal_data:
        reasons.append("collection includes personal data")
    if (
        candidate.airbnb_controlled
        and not candidate.explicit_airbnb_automation_permission
    ):
        reasons.append(
            "Airbnb-controlled source lacks explicit automation permission"
        )
    if not candidate.cache_responses:
        reasons.append("responses will not be cached")
    if candidate.requests_per_minute <= 0:
        reasons.append("rate must be positive")
    elif candidate.requests_per_minute > MAX_AUTONOMOUS_REQUESTS_PER_MINUTE:
        reasons.append(
            "rate exceeds autonomous limit of 10 requests per minute"
        )
    if not candidate.user_agent.strip():
        reasons.append("identifiable user agent is missing")

    return ScrapeDecision(allowed=not reasons, reasons=tuple(reasons))
