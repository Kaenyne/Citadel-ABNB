"""Deterministic exact-path ScrapeCandidate gate for this source-side lane.

The script makes no network requests.  Inputs come only from this run's cached
permission reconnaissance and explicitly referenced same-day permission evidence.
"""

from __future__ import annotations

import csv
import sys

from abnb_alt_data.scraping_policy import ScrapeCandidate, assess_scrape_candidate


UA = "ABNB-altdata-research/1.0 (+https://github.com/theomachado05/airbnb-citadel-2026)"


CANDIDATES = (
    ScrapeCandidate(
        source_id="BLS_CPI_LODGING",
        public_access=True,
        terms_url="https://www.bls.gov/developers/termsOfService.htm",
        terms_status="allowed",
        robots_url="https://www.bls.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/bls/news-release/cpi.htm",
            "/news.release/archives/cpi_<MMDDYYYY>.htm",
        ),
        authenticated=False,
        paywalled=False,
        captcha_required=False,
        access_control_bypass=False,
        personal_data=False,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent=UA,
    ),
    ScrapeCandidate(
        source_id="CENSUS_QSS_ACCOMMODATION",
        public_access=False,
        terms_url="https://www.census.gov/data/developers/about/terms-of-service.html",
        terms_status="allowed",
        robots_url="https://api.census.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/data/timeseries/qss/variables.json",
            "/data/timeseries/qss?get=<aggregate-fields>&time=from+2021-Q1&category_code=721",
        ),
        authenticated=False,
        paywalled=False,
        captcha_required=False,
        access_control_bypass=False,
        personal_data=False,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent=UA,
    ),
    ScrapeCandidate(
        source_id="NYC_OSE_STR_SNAPSHOTS",
        public_access=True,
        terms_url="https://www.nyc.gov/home/terms-of-use.page",
        terms_status="unclear",
        robots_url="https://www.nyc.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/assets/specialenforcement/downloads/excel/January_7_2026_STR_Registration_Dataset.xlsx",
        ),
        authenticated=False,
        paywalled=False,
        captcha_required=False,
        access_control_bypass=False,
        personal_data=True,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent=UA,
    ),
    ScrapeCandidate(
        source_id="NOLA_STR_PERMIT_EVENTS",
        public_access=True,
        terms_url="https://data.nola.gov/stories/s/Data-Policy-Annual-Report-2017/6a26-q6dq/",
        terms_status="unclear",
        robots_url="https://data.nola.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/resource/en36-xvxg.json?$limit=2&$select=permit_number,permit_type,current_status,expiration_date,application_date,issue_date",
        ),
        authenticated=False,
        paywalled=False,
        captcha_required=True,
        access_control_bypass=False,
        personal_data=False,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent=UA,
    ),
    ScrapeCandidate(
        source_id="SAN_DIEGO_STRO_ACTIVE",
        public_access=True,
        terms_url="https://data.sandiego.gov/help/guides/terms/",
        terms_status="unclear",
        robots_url="https://seshat.datasd.org/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/stro_licenses/stro_licenses_datasd.csv",
        ),
        authenticated=False,
        paywalled=False,
        captcha_required=False,
        access_control_bypass=False,
        personal_data=True,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent=UA,
    ),
)


def main() -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("source_id", "allowed", "decision_reasons"))
    for candidate in CANDIDATES:
        decision = assess_scrape_candidate(candidate)
        writer.writerow((
            candidate.source_id,
            str(decision.allowed).lower(),
            " | ".join(decision.reasons),
        ))


if __name__ == "__main__":
    main()
