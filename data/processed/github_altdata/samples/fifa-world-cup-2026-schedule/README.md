# fifa-world-cup-2026-schedule — sample (pulled 2026-09-14)

Source repo: https://github.com/Tylerx404/World-Cup-2026-Schedule-Calendar (MIT, Next.js site, last push 2026-07-03).
The repo's committed `data/schedule.ts` is only a 24-row placeholder (13 cities, no scores); the live site and its
WebCal/ICS feed are generated at request time (`lib/generateIcs.ts`) from the upstream openfootball feed
`https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json` (CC0-1.0, last push 2026-08-11).
So the real fixture data lives in openfootball, and this sample pulls both: the repo's TS files and the upstream JSON.

Files: `schedule.ts` / `repo_schedule_placeholder.csv` (24 placeholder matches), `worldcup.ts` + `generateIcs.ts` (the fetch
and ICS logic), `openfootball_worldcup_2026.json` -> `openfootball_worldcup_2026_matches.csv` (all 104 matches, 16 host
cities, 11 Jun-19 Jul 2026, local kickoff + UTC, full-time scores), `openfootball_worldcup_2026_stadiums.json/.csv`
(16 stadiums: city, timezone, country, capacity, coords). Pulled with `curl -sL` from raw.githubusercontent.com and
`gh api repos/.../contents` for tree listing; CSVs built by `convert.py` (scratchpad). Total ~80 KB, far under the 25 MB cap;
nothing truncated. Full dataset = the whole openfootball `2026/` folder (~740 KB incl. squads, groups, playoffs) — one
`git clone --depth 1 https://github.com/openfootball/worldcup.json`.
