# OpenDigger monthly GitHub metrics — sample (pulled 2026-09-14)

**What:** X-lab OpenDigger (https://github.com/X-lab2017/open-digger, Apache-2.0) computes per-repo open-source metrics from GH Archive and serves them keyless at `https://oss.open-digger.cn/github/<owner>/<repo>/<metric>.json`. Each JSON maps period keys (`YYYY`, `YYYY-MM`, `YYYYQn`, plus an undocumented `2021-10-raw`) to a float. Sample here: 5 airbnb-org repos (javascript, lottie-android, lottie-ios, epoxy, knowledge-repo) x 5 metrics (openrank, activity, stars, participants, technical_fork), monthly 2015-01 to 2026-08, tidied into `opendigger_airbnb_repo_metrics_long.csv` (4,127 rows) and `opendigger_airbnb_openrank_monthly_wide.csv` (138 months x 5 repos). Also the repo's company taxonomy YAML for Airbnb (org id 698437) and Ctrip, and the LICENSE.

**How pulled:** 25 `curl -s -L -o` GETs (all HTTP 200), then `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set labeled_data/companies sample_data` (HEAD 63e4b89, 2026-08-20). No login, no API key, no scraper.

**Caps applied:** 279 KB total, 34 files; only 5 of ~200 airbnb repos and 5 of ~30 metrics. `sample_data/` in the repo holds only ClickHouse export scripts, not data, so nothing was copied from it.

**Full dataset:** enumerate the org's repos (`gh api orgs/airbnb/repos --paginate`) and loop the curl over every repo and metric (~6,000 small JSONs, ~15-20 MB for Airbnb; same again per peer org: booking-com, ExpediaGroup, marriott, ctripcorp). Org-level endpoints 404; sum across repos yourself. Metric list and semantics: repo README and `labeled_data/`.

**Caveats:** months can be absent (2026-06/07 missing for airbnb/javascript openrank); Airflow and Superset left the airbnb org for Apache so the org series is mostly legacy decay; CDN data has no explicit licence statement and is hosted on Aliyun OSS.
