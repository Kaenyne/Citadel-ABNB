"""Re-evaluate the exact E0-registered supply-lane paths for E1.

This is a fail-closed policy audit, not a collector. It reads the immutable
lane-local E0 preflight register and represents each row as a ScrapeCandidate
before calling assess_scrape_candidate. It prints a CSV decision log to stdout
and makes no network requests.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from abnb_alt_data.scraping_policy import ScrapeCandidate, assess_scrape_candidate


LANE_DIR = Path(__file__).resolve().parent.parent
REGISTER = LANE_DIR / "lane_preflight.csv"
USER_AGENT = "ABNB-Edge-Research/1.0 (institutional research; contact: repository-owner)"


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def load_candidates() -> list[ScrapeCandidate]:
    candidates: list[ScrapeCandidate] = []
    with REGISTER.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            candidates.append(
                ScrapeCandidate(
                    source_id=row["source_id"],
                    public_access=as_bool(row["public_access"]),
                    terms_url=row["terms_url"],
                    terms_status=row["terms_status"],
                    robots_url=row["robots_url"],
                    robots_status=row["robots_status"],
                    intended_paths=tuple(
                        path.strip()
                        for path in row["proposed_paths"].split(" | ")
                        if path.strip()
                    ),
                    authenticated=as_bool(row["authenticated"]),
                    paywalled=as_bool(row["paywalled"]),
                    captcha_required=as_bool(row["captcha_required"]),
                    access_control_bypass=as_bool(row["access_control_bypass"]),
                    personal_data=as_bool(row["personal_data_in_proposed_sample"]),
                    airbnb_controlled=as_bool(row["airbnb_controlled"]),
                    explicit_airbnb_automation_permission=False,
                    requests_per_minute=int(row["requests_per_minute"]),
                    cache_responses=as_bool(row["cache_responses"]),
                    user_agent=row["user_agent"] or USER_AGENT,
                )
            )
    return candidates


def main() -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(
        [
            "source_id",
            "exact_source_url",
            "intended_paths",
            "allowed",
            "decision_reasons",
        ]
    )
    source_rows = {}
    with REGISTER.open(newline="", encoding="utf-8") as handle:
        source_rows = {row["source_id"]: row for row in csv.DictReader(handle)}
    for candidate in load_candidates():
        decision = assess_scrape_candidate(candidate)
        writer.writerow(
            [
                candidate.source_id,
                source_rows[candidate.source_id]["exact_source_url"],
                " | ".join(candidate.intended_paths),
                str(decision.allowed).lower(),
                " | ".join(decision.reasons),
            ]
        )


if __name__ == "__main__":
    main()
