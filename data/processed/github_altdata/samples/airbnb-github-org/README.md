# airbnb-github-org sample

Repo-level metadata for all 204 public repositories in Airbnb's GitHub organisation (https://github.com/airbnb), plus commit
timestamps since 2024-01-01 for its two active flagships, `chronon` (575 commits) and `viaduct` (1,594 commits).
Pulled 2026-09-14 with `gh api` (public read, no key): `orgs/airbnb/repos --paginate` and `repos/airbnb/<repo>/commits --paginate`.
`airbnb_org_repos.json` is the raw paginated API output; the `.csv` is a 15-column reduction (name, created_at, pushed_at,
language, stars, archived, fork, license...). Total 1.3 MB, under the 25 MB cap; no clone, nothing from airbnb.com.
Caveat: the snapshot is not point-in-time (only `created_at` is a fixed historical stamp); 82 repos are forks, 24 archived.
Full dataset: repo metadata is already complete; for full event history use GH Archive (https://www.gharchive.org/) or the
BigQuery `githubarchive` dataset filtered to `org.login = 'airbnb'`, or page `repos/airbnb/<repo>/commits` for each repo.
