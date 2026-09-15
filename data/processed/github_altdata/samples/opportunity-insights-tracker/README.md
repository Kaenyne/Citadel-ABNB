# Sample: Opportunity Insights Economic Tracker (Affinity card spend)

Source: https://github.com/OpportunityInsights/EconomicTracker (data/ folder, committed CSVs). Provider for these series: Affinity Solutions; cite Chetty, Friedman, Hendren, Stepner et al. (2020) and tracktherecovery.org per the upstream README (copied here as README_upstream.md).

What it is: daily consumer card spend as a seasonally adjusted 7-day-average percent change vs January 2020, by geography (national, state; county head only), merchant industry (spend_acf = accommodation and food service, spend_aer = arts/entertainment/recreation, spend_tws = transport, ...) and consumer income quartile. Rows run 2018-12-31 to 2024-06-16; real values start 2020-01-13. The series ended 16 Jun 2024, so it covers 2020-1H24 only.

How pulled (14 Sep 2026): `curl -L` on raw.githubusercontent.com HEAD paths for National Daily, State Daily, Industry Composition, GeoIDs - State, docs/oi_tracker_data_dictionary.md and README.md; County Daily taken as a 4 MB byte-range head (`curl -r 0-3999999`) and trimmed to a full last line (158k rows, Jan 2019 to 6 Apr 2020). Cap applied: 12.2 MB written (limit 25 MB); no clone, 7 files.

Full dataset: `git clone --depth 1 https://github.com/OpportunityInsights/EconomicTracker` (~470 MB across 48 CSVs incl. COVID, employment, job postings, UI claims, Womply, Zearn, Google Mobility); Affinity block ~62 MB, County Daily alone 41 MB. Monthly and City-level Affinity files were not sampled.
