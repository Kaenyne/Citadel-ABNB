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
- 22:52 heartbeat cron created (every 30 min at :13/:43). Forecast agents launched on Fable: A01 (C01), A02 (C02,C03), A03 (C04,C09), A04 (C05,C06,C07). Audit prompts pre-generated for all 19 batches under prompts/audit_<batch>.md.
- 23:20 A01 forecast done on Fable (C01: P 0.75, CI 0.62-0.85; midpoint p50 $3,100M; guide-surprise object 0.51). Codex audit A01 launched (run_audit.sh). A05 forecast launched on Fable.
- 23:34 A03 forecast done on Fable (C04 vector a 0.26 / b 0.42 / c 0.05 / d 0.24 / e 0.03; C09 down 0.28 / flat 0.27 / up 0.40 / none 0.05). A06 forecast (S01) launched on Fable. Running: A02, A04, A05, A06; Codex audit A01.
- 23:38 A02 forecast done on Fable (C02: a 0.21 / b 0.19 / c 0.39 / d 0.17 / e 0.04; C03: raised 0.37 / reiterated 0.18 / narrowed ~15% 0.28 / lowered 0.08 / none 0.09). A07 forecast (S02,S03,S04) launched on Fable. Running: A04, A05, A06, A07; Codex audit A01 (heavy compute, still running). Codex stdout logs now gitignored.
- 23:56 A04 forecast done on Fable (C05: not quantified 0.73, a 0.08 / b 0.12 / c 0.07; C06: a 0.15 / b 0.24 / c 0.31 / d 0.30; C07: P 0.20, CI 0.12-0.32). A08 forecast (F01-F04) launched on Fable. Running: A05, A06, A07, A08; Codex audit A01.
- 23:19 A06 forecast done on Fable (S01: unconditional p50 -2.9%, P(<=-8) 0.29, P(<=-5) 0.41, P(>=+5) 0.20; base-case cell p50 -8.6%, P(<=-8) 0.53; event sd 9.0-9.5). A09 forecast (R01-R03) launched on Fable. Running: A05, A07, A08, A09; Codex audit A01 (since 23:03).
- 23:22 Codex audit A01 finished (exit 0, 23:14, 22 KB). Codex audit A02 launched. A01 response agent waits for a free slot (4 forecast agents running: A05, A07, A08, A09).
- 23:30 A05 forecast done on Fable (C08: a 0.50 / b 0.30 / c 0.18 / d 0.02; C11: P 0.55 CI 0.40-0.70; C12: P 0.55 CI 0.40-0.70). A01 audit-response agent launched on Fable. Running: A07, A08, A09 forecasts; A01 response; Codex audit A02.
- 23:27 heartbeat: no change; running A07, A08, A09 forecasts, A01 response, Codex audit A02. No slot free.
- 23:42 A07 forecast done on Fable (S02 15 Dec p50 $162, P(<=150) 0.33, P(<=143) 0.24, P(>=180) 0.28; S03 12 Feb p50 $165, 0.34/0.27/0.35; S04 P 0.29 CI 0.20-0.40; MS re-initiated EW $170 on 16 Sep). MEMO FIX QUEUED: Q4 prints day-1 positive 5 of 6 (4Q23 -1.7%), not 6 of 6. A10 forecast (R04,R05,R07) launched on Fable. Running: A08, A09, A10 forecasts; A01 response; Codex audit A02.
