from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "src/abnb_alt_data/scraping_policy.py"


def load_policy_module():
    if not POLICY_PATH.is_file():
        pytest.fail("scraping policy gate is missing")
    spec = importlib.util.spec_from_file_location("scraping_policy_under_test", POLICY_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def permitted_candidate(module):
    return module.ScrapeCandidate(
        source_id="PUBLIC-001",
        public_access=True,
        terms_url="https://example.org/terms",
        terms_status="allowed",
        robots_url="https://example.org/robots.txt",
        robots_status="allowed",
        intended_paths=("/public/data/",),
        authenticated=False,
        paywalled=False,
        captcha_required=False,
        access_control_bypass=False,
        personal_data=False,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent="ABNBAltDataResearch/1.0 contact=research@example.org",
    )


def test_permitted_public_candidate_passes_autonomous_gate() -> None:
    module = load_policy_module()

    decision = module.assess_scrape_candidate(permitted_candidate(module))

    assert decision.allowed is True
    assert decision.reasons == ()


@pytest.mark.parametrize(
    ("changes", "expected_reason"),
    [
        ({"public_access": False}, "source is not publicly accessible"),
        ({"terms_url": ""}, "terms URL is missing"),
        ({"terms_status": "unclear"}, "terms do not clearly permit automation"),
        ({"terms_status": "prohibited"}, "terms prohibit automated collection"),
        ({"robots_url": ""}, "robots URL is missing"),
        ({"robots_status": "disallowed"}, "robots guidance disallows the intended paths"),
        ({"robots_status": "unclear"}, "robots guidance does not clearly allow the intended paths"),
        ({"intended_paths": ()}, "intended paths are missing"),
        ({"authenticated": True}, "authentication is required"),
        ({"paywalled": True}, "content is paywalled"),
        ({"captcha_required": True}, "CAPTCHA is required"),
        ({"access_control_bypass": True}, "collection would bypass access controls"),
        ({"personal_data": True}, "collection includes personal data"),
        ({"cache_responses": False}, "responses will not be cached"),
        ({"requests_per_minute": 0}, "rate must be positive"),
        ({"requests_per_minute": 11}, "rate exceeds autonomous limit of 10 requests per minute"),
        ({"user_agent": ""}, "identifiable user agent is missing"),
    ],
)
def test_unsafe_candidate_is_blocked(changes: dict[str, object], expected_reason: str) -> None:
    module = load_policy_module()
    candidate = replace(permitted_candidate(module), **changes)

    decision = module.assess_scrape_candidate(candidate)

    assert decision.allowed is False
    assert expected_reason in decision.reasons


def test_airbnb_controlled_candidate_needs_explicit_permission() -> None:
    module = load_policy_module()
    candidate = replace(
        permitted_candidate(module),
        airbnb_controlled=True,
        explicit_airbnb_automation_permission=False,
    )

    decision = module.assess_scrape_candidate(candidate)

    assert decision.allowed is False
    assert "Airbnb-controlled source lacks explicit automation permission" in decision.reasons
