"""Fail-closed, exact-path permission reassessment for the seven retained sources.

This script performs no network activity.  Its inputs are the official permission
and metadata responses already cached in this directory.  It represents every
resolved data path as a ScrapeCandidate and emits the deterministic policy result.
"""

from __future__ import annotations

import csv
import sys

from abnb_alt_data.scraping_policy import ScrapeCandidate, assess_scrape_candidate


USER_AGENT = "ABNB-Edge-Research/1.0 (institutional research; contact: repository-owner)"


CANDIDATES = (
    ScrapeCandidate(
        source_id="SCW-005",
        public_access=True,
        terms_url="https://www.nyc.gov/home/terms-of-use.page",
        terms_status="unclear",
        robots_url="https://www.nyc.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/site/specialenforcement/registration-law/registration-and-listing-data.page",
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
        user_agent=USER_AGENT,
    ),
    ScrapeCandidate(
        source_id="SCW-006",
        public_access=True,
        terms_url="https://www.occompt.com/copyright",
        terms_status="unclear",
        robots_url="https://www.occompt.com/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/quicklinks.aspx?CID=39",
            "/Archive.aspx?AMID=56",
            "/DocumentCenter/View/<monthly-report-id>/<YYYY-MM-Month-TDT-Collection-PDF>",
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
        user_agent=USER_AGENT,
    ),
    ScrapeCandidate(
        source_id="SCW-004",
        public_access=True,
        terms_url="https://vancouver.ca/your-government/terms-of-use.aspx",
        terms_status="unclear",
        robots_url="https://opendata.vancouver.ca/robots.txt",
        robots_status="disallowed",
        intended_paths=(
            "/api/explore/v2.1/catalog/datasets/business-licences/records?limit=2&refine=businesstype:%22Short-term%20Rental%20Operator%22",
        ),
        authenticated=False,
        paywalled=False,
        captcha_required=True,
        access_control_bypass=False,
        personal_data=True,
        airbnb_controlled=False,
        explicit_airbnb_automation_permission=False,
        requests_per_minute=6,
        cache_responses=True,
        user_agent=USER_AGENT,
    ),
    ScrapeCandidate(
        source_id="SCW-010",
        public_access=True,
        terms_url="https://www.nyc.gov/home/terms-of-use.page",
        terms_status="unclear",
        robots_url="https://www.nyc.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/site/specialenforcement/about/data-reports.page",
            "/assets/specialenforcement/downloads/excel/2025_LL87_2025_Annual_Report.xlsx",
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
        user_agent=USER_AGENT,
    ),
    ScrapeCandidate(
        source_id="SCW-002",
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
        user_agent=USER_AGENT,
    ),
    ScrapeCandidate(
        source_id="SCW-003",
        public_access=True,
        terms_url="https://data.nola.gov/stories/s/Data-Policy-Annual-Report-2017/6a26-q6dq/",
        terms_status="unclear",
        robots_url="https://data.nola.gov/robots.txt",
        robots_status="unclear",
        intended_paths=(
            "/resource/uzyk-jrck.json?$limit=2&$select=agency,case_type,hearing_date,case_established,violation_count",
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
        user_agent=USER_AGENT,
    ),
    ScrapeCandidate(
        source_id="SCW-008",
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
        user_agent=USER_AGENT,
    ),
)


def main() -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("source_id", "allowed", "decision_reasons"))
    for candidate in CANDIDATES:
        decision = assess_scrape_candidate(candidate)
        writer.writerow(
            (
                candidate.source_id,
                str(decision.allowed).lower(),
                " | ".join(decision.reasons),
            )
        )


if __name__ == "__main__":
    main()
