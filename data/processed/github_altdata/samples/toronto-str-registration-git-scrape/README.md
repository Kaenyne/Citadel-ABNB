# toronto-str-registration-git-scrape — sample

Daily git-scraped snapshots of the City of Toronto "Short Term Rentals Registration" open-data CSV
(https://github.com/RamVasuthevan/city-of-toronto-short-term-rentals-registration). One row per active
registered STR unit: registration number (STR-YYMM-xxxxxx encodes issue month), address, postal FSA, property
type, ward. Commits run nightly since 20 Feb 2024 (917 commits as of 13 Sep 2026), so each commit is a dated vintage.

Pulled 14 Sep 2026 with curl from raw.githubusercontent.com: the HEAD file plus five historical vintages
(2024-02-20, 2024-09-01, 2025-03-01, 2025-09-01, 2026-03-01) whose SHAs were resolved with
`gh api repos/<repo>/commits?until=<date>&path=short-term-rental-registrations-data.csv`. Total 3.9 MB, well under the 25 MB cap;
no scraper was run and open.toronto.ca was not touched. Row counts: 8094 / 8673 / 8510 / 7259 / 7293 / 8750.

Full dataset: `git clone https://github.com/RamVasuthevan/city-of-toronto-short-term-rentals-registration` then
`git log --format=%H,%cI -- short-term-rental-registrations-data.csv` and `git show <sha>:short-term-rental-registrations-data.csv`
per vintage. Data licence: Open Government Licence – Toronto v1.0 (attribution required); code MIT.
