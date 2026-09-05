#!/usr/bin/env python3
"""Apply the deterministic gate to ADR pilot data paths after exact-host review."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


RUN = Path(__file__).resolve().parent
REPO = RUN.parents[2]
sys.path.insert(0, str(REPO / "src"))
from abnb_alt_data.scraping_policy import ScrapeCandidate, assess_scrape_candidate  # noqa: E402


UA = "ABNB-altdata-research/1.0 (+https://github.com/theomachado05/airbnb-citadel-2026)"


def make(source_id: str, terms_url: str, terms_status: str, robots_url: str,
         robots_status: str, paths: tuple[str, ...], authenticated: bool) -> ScrapeCandidate:
    return ScrapeCandidate(
        source_id=source_id,
        public_access=True,
        terms_url=terms_url,
        terms_status=terms_status,
        robots_url=robots_url,
        robots_status=robots_status,
        intended_paths=paths,
        authenticated=authenticated,
        paywalled=False,
        captcha_required=False,
        access_control_bypass=False,
        personal_data=False,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=9,
        cache_responses=True,
        user_agent=UA,
    )


def main() -> None:
    candidates = [
        ("ADR-GATE-001", "FRED authenticated API", make(
            "BLS_CPI_LODGING|BLS_CPI_ALL_ITEMS_NSA",
            "https://fred.stlouisfed.org/docs/api/terms_of_use.html", "allowed",
            "https://api.stlouisfed.org/robots.txt", "unclear",
            ("/fred/series/observations?series_id=CUUR0000SEHB02", "/fred/series/observations?series_id=CPIAUCNS"),
            True,
        ), "Free FRED key is absent; exact API-host robots was not reviewed because no authenticated request is authorized."),
        ("ADR-GATE-002", "ALFRED no-key graph CSV", make(
            "BLS_CPI_LODGING|BLS_CPI_ALL_ITEMS_NSA",
            "https://fred.stlouisfed.org/legal/", "prohibited",
            "https://alfred.stlouisfed.org/robots.txt", "allowed",
            ("/graph/alfredgraph.csv?id=CUUR0000SEHB02", "/graph/alfredgraph.csv?id=CPIAUCNS"),
            False,
        ), "Website terms prohibit automated extraction outside the API; exact lodging series page also returned HTTP 404."),
        ("ADR-GATE-003", "BLS public API v1", make(
            "BLS_CPI_LODGING",
            "https://www.bls.gov/developers/termsOfService.htm", "allowed",
            "https://api.bls.gov/robots.txt", "disallowed",
            ("/publicAPI/v1/timeseries/data/CUUR0000SEHB02",),
            False,
        ), "Exact api.bls.gov robots says User-agent: * and Disallow: /; no payload may be requested."),
        ("ADR-GATE-004", "BLS archived CPI releases", make(
            "BLS_CPI_LODGING",
            "https://www.bls.gov/developers/termsOfService.htm", "allowed",
            "https://www.bls.gov/robots.txt", "unclear",
            ("/news.release/archives/cpi_*.htm",),
            False,
        ), "Same-day www.bls.gov robots request returned HTTP 403 and established a no-retry host stop."),
    ]
    rows = []
    for gate_id, family, item, note in candidates:
        decision = assess_scrape_candidate(item)
        rows.append({
            "gate_id": gate_id,
            "path_family": family,
            "source_id": item.source_id,
            "terms_url": item.terms_url,
            "terms_status": item.terms_status,
            "robots_url": item.robots_url,
            "robots_status": item.robots_status,
            "intended_paths": " | ".join(item.intended_paths),
            "authenticated": str(item.authenticated).lower(),
            "personal_data": "false",
            "requests_per_minute": item.requests_per_minute,
            "allowed": str(decision.allowed).lower(),
            "decision_reasons": " | ".join(decision.reasons),
            "evidence_note": note,
        })
    with (RUN / "data_path_gate_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
