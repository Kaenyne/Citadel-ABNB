"""Reconstruct and assess the eight final retained exact data paths."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from abnb_alt_data.scraping_policy import ScrapeCandidate, assess_scrape_candidate


HERE = Path(__file__).resolve().parent
INPUT = HERE / "data_path_candidates.csv"
OUTPUT = HERE / "data_path_assessments.csv"
FIELDS = (
    "source_id", "exact_source_url", "intended_paths", "assessment_allowed",
    "assessment_reasons", "assessed_at_utc", "terms_status", "robots_status",
    "authenticated", "personal_data", "candidate_evidence_note",
)


def truth(value: str) -> bool:
    return value.lower() == "true"


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite existing assessment: {OUTPUT}")
    rows = list(csv.DictReader(INPUT.open(newline="", encoding="utf-8")))
    assert len(rows) == 8
    assessed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    output: list[dict[str, str]] = []
    for row in rows:
        candidate = ScrapeCandidate(
            source_id=row["source_id"],
            public_access=truth(row["public_access"]),
            terms_url=row["terms_url"],
            terms_status=row["terms_status"],
            robots_url=row["robots_url"],
            robots_status=row["robots_status"],
            intended_paths=tuple(row["intended_paths"].split("|")),
            authenticated=truth(row["authenticated"]),
            paywalled=truth(row["paywalled"]),
            captcha_required=truth(row["captcha_required"]),
            access_control_bypass=truth(row["access_control_bypass"]),
            personal_data=truth(row["personal_data"]),
            airbnb_controlled=truth(row["airbnb_controlled"]),
            explicit_airbnb_automation_permission=truth(row["explicit_airbnb_automation_permission"]),
            requests_per_minute=int(row["requests_per_minute"]),
            cache_responses=truth(row["cache_responses"]),
            user_agent=row["user_agent"],
        )
        decision = assess_scrape_candidate(candidate)
        output.append({
            "source_id": row["source_id"],
            "exact_source_url": row["exact_source_url"],
            "intended_paths": row["intended_paths"],
            "assessment_allowed": str(decision.allowed).lower(),
            "assessment_reasons": " | ".join(decision.reasons),
            "assessed_at_utc": assessed_at,
            "terms_status": row["terms_status"],
            "robots_status": row["robots_status"],
            "authenticated": row["authenticated"],
            "personal_data": row["personal_data"],
            "candidate_evidence_note": row["decision_note"],
        })
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    print(f"wrote {len(output)} decisions; allowed={sum(row['assessment_allowed'] == 'true' for row in output)}")


if __name__ == "__main__":
    main()
