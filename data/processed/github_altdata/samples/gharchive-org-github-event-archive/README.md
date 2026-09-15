# GH Archive (gharchive.org) — sample

**What it is.** GH Archive records every public GitHub event (pushes, PRs, issues, stars, forks, releases...) as hourly gzipped JSON files at
`https://data.gharchive.org/YYYY-MM-DD-H.json.gz`, keyless, from 12 Feb 2011 to the present (also a BigQuery public dataset `githubarchive`).
The repo https://github.com/igrigorik/gharchive.org holds only the site/code (MIT code, CC-BY-4.0 content) — no data is committed there.

**How this sample was pulled (14 Sep 2026).** Keyless `curl` range requests against data.gharchive.org: the full hour 2026-09-01T15Z
(`gharchive_2026-09-01-15_full.json.gz`, 1.7 MB, 1,844 events; also decoded to a 200-line JSONL head and a flat CSV of all 1,844 events),
and the first 3 MB of 2024-09-01T15Z decoded to a 7,000-row flat CSV (`id, type, actor_login, repo_name, org_login, created_at`).
`curl -I` confirmed 2011-02-12 and 2015-01-01 files exist. Caps applied: <= 5 MB written, no clone, no BigQuery, no login.

**Caveat found while sampling.** Hourly file sizes fell from ~80-100 MB (2024-25) to ~13-40 MB through 2026, and the 2026-09-01-15 hour
contains no PushEvent/CreateEvent rows at all (2024 slice: 66% PushEvent). Coverage of 2026 looks incomplete or the feed changed — check
before building a monthly Airbnb-org series across the 2025/2026 boundary.

**Full dataset.** ~24 files/day x 5,700+ days, ~100 MB/hour at 2024-25 volumes (tens of TB). Loop over hours with curl and filter
`repo.name` starting `airbnb/`, or query BigQuery `githubarchive.month.*` (needs a Google account — a human decision).
