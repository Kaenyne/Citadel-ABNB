# Pitch-forecasts run — state ledger

Branch `krish/pitch-forecasts`. Started 16 Sep 2026 22:40 local. Orchestrator: Claude Fable 5.1 main session; heartbeat cron
every ~30 min resumes from disk (`py -3.13 analysis/src/pitch_forecasts/state.py`).

## How to resume (for the heartbeat or a fresh session)

1. `cd "C:/Users/krish/citadel-abnb" && git status --short docs/pitch-forecasts | head` and
   `py -3.13 analysis/src/pitch_forecasts/state.py`.
2. For every batch whose next stage is `forecast` or `response` and fewer than 4 forecast/response agents are running:
   launch an `Agent` (general-purpose, model fable; opus if fable is rate-limited) with the prompt template in
   `docs/pitch-forecasts/prompts/forecast_agent.md` or `response_agent.md`, `{BATCH}` and `{QIDS}` substituted from
   `batches.json`. Priority order: A01–A08 (core, stock, Feb), then A09–A18, then A19 last.
3. For the first batch whose next stage is `audit` and no `audits/*.stdout.log` is newer than its `.done`
   (i.e., no Codex audit running): write `prompts/audit_<BATCH>.md` from `audit_template.md` (substitute), then
   `bash analysis/src/pitch_forecasts/run_audit.sh <BATCH>`. One Codex at a time. If a `.done` shows a non-zero exit twice,
   run the audit prompt through an Opus `Agent` instead and note it here.
4. After each completed stage: append a line below and `git add -A docs/pitch-forecasts analysis/src/pitch_forecasts && git commit -m "pitch-forecasts: <stage> <batch>"`.
5. When state.py shows every batch `done` (A19 included): write `docs/pitch-forecasts/SYNTHESIS.md`, update
   `deck/drafts/memo_v2_short_2026-09-16.md` + `.html`, re-render the PDF (command in `docs/pitch-forecasts/MEMO_CHANGES.md`),
   commit, then delete the heartbeat cron.

## Concurrency and limits

- Max 4 forecast/response agents at once; Codex audits strictly sequential; never run method `run.py` packages.
- WebSearch is a shared session budget; agents are capped at 5 per question.
- Fable weekly limit: on a rate-limit error, relaunch the same prompt on Opus and record it here.

## Ledger

- 22:40 branch created; memo drafts committed (4e8e6e7). Brief, question registry (54 questions, 19 batches), prompts,
  state script, audit launcher, examples written.
