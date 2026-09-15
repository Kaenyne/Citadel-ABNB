# GitHub alt-data catalogue — run state and resume runbook

Started 13 Sep 2026 late evening (local). Branch `krish/github-altdata-catalog`, worktree `C:\Users\krish\citadel-abnb-ghcat`.
Purpose: catalogue (not test) open-source GitHub repos holding or acquiring data useful for the ABNB pitch.
Shared brief for agents: `docs/github-altdata/CONTEXT.md`.

## Pipeline (three stages, each idempotent on disk)

| Stage | Model | Script | Ground truth on disk |
|---|---|---|---|
| S — scouts (262: 123 themes × {gh, web} + 16 wildcard lenses) | Sonnet | `analysis/src/github_altdata/wf_scouts.js` (args `{only:[idx,...]}` = resume mode) | `data/processed/github_altdata/scouts/scout_NNN.json` |
| R — review, 5 candidates per Opus agent | Opus | `analysis/src/github_altdata/wf_reviews.js` (args `{batches:[...]}` from `state.py --batches`) | `reviews/review_NNN.json` (verdicts keyed by URL) |
| F — sample pull, one Fable agent per `sample` verdict, ≤ 25 MB | Fable | `analysis/src/github_altdata/wf_samples.js` (args `{jobs:[...]}` from `state.py --jobs`) | `samples/<slug>/manifest.json` |

`python analysis/src/github_altdata/state.py` prints the state and the next step. It never depends on the workflow cache.

## Live tasks (append a line whenever a workflow is launched)

- 13 Sep 2026 ~23:50 local — combined S+R workflow, task `wzp1522t5`, run `wf_b64b09fa-96c`
  (script persisted at `C:\Users\krish\.claude\projects\C--Users-krish-citadel-abnb\fed6ec60-0618-4506-8d5e-dfd74f10c375\workflows\scripts\github-altdata-scout-and-review-wf_b64b09fa-96c.js`).
  Its review phase batches whatever scouts succeeded; any scout that died (usage limit → null) has no file and is re-run by the resume path.
  **DONE 14 Sep ~01:00** — 177/262 scouts returned (175 files on disk, 2 malformed), 1,592 raw → 1,287 unique candidates; the usage limit hit at ~01:00 (reset 03:20 ET) so all 259 Opus review batches died. 344 of 521 agents errored. 13.7M subagent tokens, 71 min.
- Note: WebSearch has a session-wide budget (~200 calls, pooled across concurrent agents); 80 of 86 web-modality scouts reported it exhausted and fell back to WebFetch/gh. `wf_scouts.js` now tells web scouts to use DuckDuckGo/Bing HTML via WebFetch when that happens.
- 14 Sep 03:55 local — scouts resume, 87 indices ([17, 24, 137, 175, 177, 179, 181-261]), `wf_scouts.js` with args.only — task `wo3qbfebz`, run `wf_4c5a3487-d67`. (First launch attempt failed: the script file had CRLF line endings, which the permission dialog rejects as control characters; all three wf_*.js are now LF-only. Keep them that way.)
  **DONE 14 Sep 04:40** — 87/87 returned, 0 errors, 6.75M tokens, 44 min. Four scouts (213, 232, 258, 261) returned without writing a file; recovered from the run's journal.jsonl (`type:"started"` lines map key→label, `type:"result"` lines carry the return value).
- 14 Sep 04:45 local — Opus review, batches 0..346 (1,735 unique candidates, 5 per batch; batch files in `reviews/pending/`), `wf_reviews.js` with args.batch_ids — task `w0meoutmj`, run `wf_3c42fcac-c6e`. Args are now id lists only; the candidate data lives in per-batch files (same for samples: `samples/_jobs/<slug>.json`, args.slugs). Candidates from the four recovered scouts are not in batches 0..346; the next `state.py --batches` after this run will pick them up as batch 500+.

  **DONE 14 Sep ~05:00** — usage limit hit after 21 batches (105 verdicts: 33 sample / 64 catalog_only / 8 discard; ~93k tokens per 5-repo batch); 326 batches died. 28 review files on disk (140 verdicts) after the 7 that landed in the first run's window.

## Scope cut (Krish, 14 Sep 08:50): "347 batches of 5 is way too much"

Pool at the cut: 1,773 unique repos, 1,635 unreviewed = high 122 / medium 480 / low 1,033; 1,299 single-scout hits; 340 flagged as duplicates of holdings.
1. **Only high + medium go to Opus** (602 repos). Low-potential repos stay in the catalogue as "scout-only" rows with the scout's description; never reviewed.
2. **25 per Opus agent, metadata triage, ≤ 6 WebFetches per batch, no `gh api`, effort medium** → ~25 Opus agents instead of 326. New fields: `priority` (1/2/3) and `source_family`.
3. **Sampling = priority-1 'sample' verdicts only, one per source_family** (pre-cut verdicts without a priority count as 1 if possibly_useful). Expect ~60–120 Fable pulls instead of ~550.
`state.py` encodes all three (BATCH, REVIEW_TIERS, SAMPLE_PRIORITY_MAX). Review batch ids for the triage start at 500.
4. **Krish's pick (09:00): Sonnet triages the medium tier, Opus only the high tier.** `state.py --batches` prints `ARGS={opus_batch_ids, sonnet_batch_ids}`; pass that object to `wf_reviews.js`. Reviews stage cost ≈ 5 Opus + 20 Sonnet agents.

- 14 Sep 09:05 local — tiered triage: batches 500–504 Opus (122 high), 505–524 Sonnet (480 medium), `wf_reviews.js` — task `w31bf3y7q`, run `wf_586507df-b0b`. After it: `state.py --jobs` → `wf_samples.js` with `{slugs: [...]}` (priority-1, one per source_family; 40 already queued from the pre-cut verdicts).
  **DONE 14 Sep 09:15** — 25/25 batches, 602 verdicts (164 sample / 431 catalog_only / 7 discard; 21 priority-1), 2.15M tokens, 11 min. Totals now: 642 verdicts, 187 sample verdicts, 58 priority-1 after source_family dedupe.
- 14 Sep 09:20 local — Fable sampling, 56 jobs (58 minus the two `factden-*-scraper` slugs, which are third-party scrapers and would only have recorded sampled=false), `wf_samples.js` with args.slugs — task `wbwoi8bh8`, run `wf_f6912183-502`. When it finishes: `state.py --merge`, write the note, commit on the branch, PushNotification, CronDelete `157c1eee`.
  **DONE 14 Sep 10:10** — 56/56 sampled, 3.64M tokens, 51 min, 202 MB on disk (files > 2 MB kept out of git via `samples/.gitignore`; see `LARGE_FILES_NOT_COMMITTED.txt`). Cron `157c1eee` deleted; the finish is being done inline.
- 14 Sep 10:30 — the note-writing agent found four Sonnet review batches (507, 509, 517, 518) that returned but never wrote their file (same failure as the four scouts). Recovered 100 verdicts from `wf_586507df-b0b/journal.jsonl` → 742 verdicts total; `review_tier` in catalog.csv now derived from the batch number (pre-cut Opus-verified / Opus triage / Sonnet triage) instead of the wrong constant "opus".
- 14 Sep 10:35 — three new priority-1 samples from the recovered batches (joeydejager-nyc-2015, tmasjc-vienna-berlin-2017-plus-downloader, neshitov-la-inside-airbnb-2018; the two factden scrapers skipped again), `wf_samples.js` — task `wmce5rjof`, run `wf_6d427764-525`. After it: re-run `state.py --merge`, patch the note (recovered batches, 59 samples), commit.

## Heartbeat tick (cron in this session, every 40 min) — what to do on each fire

1. `python "C:\Users\krish\citadel-abnb-ghcat\analysis\src\github_altdata\state.py"` and read `next_step`.
2. For every task ID listed above that is not marked DONE, `TaskOutput(task_id, block=false, timeout=5000)`. If any is still running → say "still running: <counts>" in one line and stop (no relaunch).
3. If none is running, act on `next_step`:
   - scouts missing → `Workflow({scriptPath: ".../wf_scouts.js", args: {only: <scouts_missing>}})`.
   - unreviewed candidates → `python state.py --batches`, Read `reviews/batches_pending.json`, `Workflow({scriptPath: ".../wf_reviews.js", args: {batches: <that JSON>}})`.
   - samples pending → `python state.py --jobs`, Read `samples/sample_jobs_pending.json`, `Workflow({scriptPath: ".../wf_samples.js", args: {jobs: <that JSON>}})`.
   - all complete → `python state.py --merge`, write `research/notes/github_altdata/2026-09-14_github-altdata-catalog.md` (bottom line, top finds by gap, counts table, what could not be sampled, RESUME), commit on this branch (never main), PushNotification the user, CronDelete the heartbeat.
   Append the new task ID here. Never run two workflows at once.
4. If the tick itself fails because the usage limit is hit, nothing is needed: the cron fires again after the reset and picks up from disk.

## Notes

- Workflow agents that hit the usage limit return null; the workflow keeps going and "completes" with holes. That is why ground truth is the files, not the workflow return value.
- Never run scrapers against airbnb.com or any third-party site; those repos are `catalog_only`. Never type credentials or use paid keys.
- Do not commit `*.zip` / `*.parquet` (gitignored); sample CSV heads only.
