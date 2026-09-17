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
- 23:37 A08 forecast done on Fable (F01 P 0.22; F02 p50 +9.4%, P(<10) 0.56; F03 a 0.08 / b 0.17 / c 0.27 / d 0.38 / e 0.10; F04 P 0.55). A11 forecast (R06,R08,R09) launched on Fable. Running: A09, A10, A11 forecasts; A01 response; Codex audit A02.
- 23:38 Codex audit A02 finished (exit 0, 23:35, 31 KB); Codex audit A03 launched. A02 response queued for a free slot.
- 23:41 A09 forecast done on Fable (R01 P 0.42 CI 0.30-0.55, EV $8.0/sh material; R02 P 0.32, EV $7.2/sh material subset; R03 P 0.07, EV $1.6/sh marginal). A02 response agent launched on Fable. Running: A10, A11 forecasts; A01, A02 responses; Codex audit A03.
- 23:44 A01 response done (C01 0.75 -> 0.72 CI 0.60-0.82; 11 accepted, 2 in part, 0 rejected; A01 DONE). A12 forecast (R10,R11,R15,R16) launched on Fable. Running: A10, A11, A12 forecasts; A02 response; Codex audit A03.
- 23:48 A10 forecast done on Fable (R04 P 0.58 EV $4.1/sh material; R05 P 0.17 EV $0.5 immaterial; R07 P 0.17 EV $1.2 marginal). A13 forecast (R12,R13,R14) launched on Fable. Running: A11, A12, A13 forecasts; A02 response; Codex audit A03.
- 00:05-03:50 SESSION LIMIT OUTAGE (5-hour window; reset 3:50am). Killed mid-work: A11 forecast (files complete on disk: R06/R08/R09 logs+JSONs), A12 and A13 forecasts (nothing on disk), A02 response (both logs and JSONs at revision 2; A02-audit-response.md not written). Codex audit A03 completed 23:54 during the outage (exit 0, 31 KB).
- 03:52 resumed. Launched: A02 response finisher, A03 response, A12 forecast, A13 forecast (all Fable); Codex audit A04.
- 03:57 heartbeat: no change since 03:52 relaunch; running A02 response finisher, A03 response, A12, A13 forecasts; Codex audit A04.
- 03:57 A02 response done (C02 rev2 0.18/0.17/0.30/0.31/0.04; C03 rev2 0.36/0.16/0.28/0.08/0.12; 16 findings accepted; A02 DONE). A14 forecast (B01-B03) launched on Fable. Running: A03 response; A12, A13, A14 forecasts; Codex audit A04.
- 04:15 A03 response done (C04 rev2 0.33/0.30/0.05/0.27/0.05; C09 rev2 0.22/0.26/0.47/0.05; 17 accepted, 3 in part; A03 DONE). A15 forecast (B04-B07) launched on Fable. Running: A12, A13, A14, A15 forecasts; Codex audit A04.
- 04:15 A13 forecast done (R12 P 0.42 EV $0.6 immaterial; R13 P 0.03 immaterial; R14 P 0.30 EV $5.3 material; corrected Q4 day-1 record 5/6 positive, 3/6 >=+5%). Codex audit A04 finished 04:04 (29 KB); A04 response launched on Fable; Codex audit A05 launched. Running: A12, A14, A15 forecasts; A04 response; Codex A05.
- 04:17 A12 forecast done (R10 P 0.09 immaterial; R11 P 0.38 immaterial; R15 P 0.14 immaterial; R16 P 0.27 EV $2.7 material). A16 forecast (B08,B09,B10,B17) launched on Fable. Running: A14, A15, A16 forecasts; A04 response; Codex audit A05.
- 04:19 A14 forecast done (B01 P 0.34 = base-case marker; B02 P 0.18 EV -$2.2 material; B03 P 0.18 immaterial). A17 forecast (B11,B12,B13) launched on Fable. Running: A15, A16, A17 forecasts; A04 response; Codex audit A05.
- 04:27 heartbeat: no change; running A15, A16, A17 forecasts, A04 response; Codex audit A05 (20 min in).
- 04:36 A04 response done (C05 rev2 0.07/0.11/0.10/0.72; C06 rev2 0.25/0.20/0.26/0.29; C07 rev2 0.27 CI 0.15-0.40; 14 accepted, 4 in part; A04 DONE). NOTE for A09 response: recompute R03 with C06(a)=0.25 -> ~0.13. A18 forecast (B14,B15,B16) launched on Fable. Running: A15, A16, A17, A18 forecasts; Codex audit A05.
- 04:37 A17 forecast done (B11 P 0.14 immaterial; B12 P 0.50 literal / 0.38 material, EV -$2.5; B13 P 0.26 EV -$2.6 material). Codex audit A05 finished; A05 response launched on Fable; Codex audit A06 launched. Running: A15, A16, A18 forecasts; A05 response; Codex A06.
- 04:38 A15 forecast done (B04 P 0.15 EV -$1.0 borderline; B05 P 0.68 EV -$1.7 small; B06 P 0.35 immaterial; B07 P 0.58 immaterial). No launch: responses wait on Codex audits (A06 running), A19 runs last. Running: A16, A18 forecasts; A05 response; Codex A06.
- 04:42 A16 forecast done (B08 P 0.38 EV -$1.5 marginal; B09 P 0.10 immaterial; B10 P 0.05 immaterial; B17 P 0.42 EV -$2.5 material). DATA NOTE: abnb_driver_history_quarterly.csv SBC is wrong for 4Q24 ($368M, not 400) and 4Q25 ($411M, not 400) per the releases; flag in SYNTHESIS, do not edit the tracked CSV. RULE CHANGE: Codex audits are the bottleneck (13 queued); two read-only Codex audits may now run concurrently (they write nothing but their own output). Codex audit A07 launched alongside A06. Running: A18 forecast; A05 response; Codex A06, A07.
- 04:57 heartbeat: Codex audits A06 (04:49) and A07 (04:56) finished. A06 and A07 responses launched on Fable; Codex audits A08 and A09 launched. Running: A18 forecast; A05, A06, A07 responses; Codex A08, A09.
- 04:59 A18 forecast done (B14 P 0.08, B15 P 0.10, B16 P 0.87; all immaterial). All forecast batches A01-A18 written. A19 (X01) waits for the A06 (S01) and A09 (R01/R02) responses. Running: A05, A06, A07 responses; Codex A08, A09.
- 05:06 A05 response done (C08 rev2 0.49/0.28/0.21/0.02; C11 0.55 -> 0.76 CI 0.60-0.88 after making the conditional table and headline one model; C12 0.55 -> 0.43; A05 DONE). Running: A06, A07 responses; Codex A08, A09.
- 05:21 A06 response done (S01 rev2: p50 -2.1%, P(<=-8) 0.27, P(<=-5) 0.38, P(>=+5) 0.22; base-case cell p50 -5.1%, P(<=-8) 0.37 [rev1 -8.6 / 0.53 withdrawn]; A06 DONE). MEMO NOTE: the memo's '-8% to -13% base-case day' must be re-based to the joint model. Running: A07 response; Codex A08, A09.
- 05:21 Codex audits A08 (05:11) and A09 (05:15) finished. A08 and A09 responses launched on Fable; Codex audits A10 and A11 launched. Running: A07, A08, A09 responses; Codex A10, A11.
- 05:24-08:50 SECOND SESSION-LIMIT OUTAGE. A07 response completed before it (S02/S03/S04 rev 2, committed b3d3bba). A08 and A09 responses killed before writing; relaunched 08:52 on Fable.
- 08:53 CODEX USAGE LIMIT EXHAUSTED (both A10 and A11 audits exit 1 at 05:24: "You've hit your usage limit ... try again at Sep 19th 7:05 PM"). Fallback per 00_BRIEF §Orchestration: remaining audits A10-A18 (and A19) run as independent OPUS agents using the same prompts/audit_<batch>.md, writing audits/<batch>-research-audit.md + .done themselves. A10 and A11 fallback audits launched on Opus.
- 08:57 heartbeat: no change since 08:53; stale Codex exit=1 .done markers for A10/A11 removed so the Opus fallback audits' markers are authoritative. Running: A08, A09 responses (Fable); A10, A11 audits (Opus).
- 09:13 A11 audit (Opus fallback) done: 25 findings; independent R06 0.42 / R08 0.13 / R09 0.25. A12 audit launched on Opus. Running: A08, A09 responses; A10, A12 audits.
- 09:15 A10 audit (Opus fallback) done: 25 findings, 3 critical (R05 D&A add-back identity; R07/B02 one distribution; R04 impact prices a statement as delivered take rate); independent R04 0.52 / R05 0.21 / R07 0.19 (B02 0.08). A10 response launched on Fable. Running: A08, A09, A10 responses; A12 audit (Opus).
- 09:17 A09 response done (R01 0.42 -> 0.39 CI 0.30-0.47 nowcast-only; R02 0.32 -> 0.26; R03 0.07 -> 0.11; adopted print states P(<10) 0.614 / 10-10.6 0.126 / >=10.6 0.260 in questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json; EVs $3.4/$2.5/$0.7; A09 DONE). S01/S02 re-base to these states is immaterial and will be handled in X01/SYNTHESIS rather than re-run. A11 response launched on Fable. Running: A08, A10, A11 responses; A12 audit (Opus).
- 09:19 A08 response done (F01 0.28; F02 p50 +10.5%, P(<10) 0.45; F03 literal convention a 0.02/b 0.04/c 0.10/d 0.36/e 0.48; F04 0.55; A08 DONE). A13 audit launched on Opus. Running: A10, A11 responses; A12, A13 audits.
- 09:27 heartbeat: no change; running A10, A11 responses (Fable); A12, A13 audits (Opus).
- 09:38 A11 response done (R06 0.46; R08 0.13; R09 0.25; all immaterial; A11 DONE). A14 audit launched on Opus. Running: A10 response; A12, A13, A14 audits.
- 09:42 A10 response done (R04 0.52 EV $1.1 borderline; R05 0.22 immaterial; R07 0.17 EV $1.7; B02 0.12 EV -$1.4; A10 DONE). SYNTHESIS NOTES: C11 should read ~0.73 on the joint ADR model (mean +3.35 vs +3.04); C04's 3Q26 margin sd 1.0 is an outlier vs the card's conformal 1.62; C04/C11 quote R01 0.42 (now 0.39). A15 audit launched on Opus. Running: A12, A13, A14, A15 audits.
- 09:43 A13 audit (Opus) done: 25 findings, 3 critical (R12 uses S02/S04 rev-1 params; R13 jump double count; R14 one-sided impact); independent R12 0.47 / R13 0.02 / R14 0.26. RUN NOTE: sweep for other logs carrying S02/S04 rev-1 PARAMS; R12 vs B11 feed-capture convention (0.85 vs 1.0) must be unified. A13 response launched on Fable. Running: A13 response; A12, A14, A15 audits.
- 09:45 A12 audit (Opus) done: 25 findings, 3 critical (R16/B13/F01 are three 4Q26 objects; EPS rows double-apply 0.66; R11 base rate unsourced, sources/ empty); independent R10 0.11 / R11 0.29 / R15 0.18 / R16 0.30. A12 response launched on Fable (to publish adopted_q4_states_v2.json). Running: A12, A13 responses; A14, A15 audits.
- 09:57 heartbeat: no change; running A12, A13 responses (Fable); A14, A15 audits (Opus).
- 10:05 A15 audit (Opus) done: 25 findings; independent B04 0.24 / B05 0.62 / B06 0.33 / B07 0.63; all immaterial. A16 audit launched on Opus. Running: A12, A13 responses; A14, A16 audits. Queued: A15 response.
- 10:06 A13 response done (R12 0.47 immaterial standalone; R13 0.02; R14 0.26 exit-timing only, $5.3 EV line withdrawn; A13 DONE). NOTE: B11 (A17) still carries S02 rev-1 PARAMS - its response must rebuild on abnb_path_mixture_v2; X01 must use the A09 adopted states (accel 0.26), S02 rev 2 still carries 0.32 (immaterial). A15 response launched on Fable. Running: A12, A15 responses; A14, A16 audits.
- 10:06 A14 audit (Opus) done: 25 findings, 3 critical (stale rev-1 inputs in B01/B03; B02 lower-tail components; B03 stock line untraceable); independent B01 0.33 / B02 0.09 (R07 0.19) / B03 0.21. A14 response launched on Fable. Running: A12, A14, A15 responses; A16 audit.
- 11:39 FABLE WEEKLY LIMIT hit on the first account: A12, A14, A15 responses killed (A15 had written B04 partially). A16 audit (Opus) done: independent B08 0.45 / B09 0.08 / B10 0.04 / B17 0.38. Paused launches pending Krish's decision on scope/model.
- 11:45 PLAN CHANGE (Krish, awake): Fable weekly limit on account 1; ~20% left on account 2. Remaining risk/bonus responses run on OPUS; A14 audit-only (marker audits/A14.audit_only; state.py now honours it); A18 audit-only after its audit; A15 needs only its response doc (all four logs already rev 2). Fable reserved for A19 (X01) and the synthesis + memo update. Launched on Opus: A12 response, A16 response, A17 audit, A15 finisher. Next: A18 audit, A17 response (Opus), then A19 (Fable).
- 11:53 A15 response done (B04 0.21, B05 0.62, B06 0.32, B07 0.63; none material; A15 DONE). A18 audit launched on Opus (audit-only afterwards). Running: A12, A16 responses; A17, A18 audits (all Opus).
- 11:57 heartbeat: no change; running A12, A16 responses and A17, A18 audits (all Opus).
- 12:06 A12 response done (R10 0.10, R11 0.26, R15 0.18, R16 0.31 EV $3.4 material; A12 DONE). ADOPTED OBJECTS: adopted_q4_states_v2.json (mean 8.61, sd 2.28, P>=134.0m 0.307, P<=131.0m 0.309) and r11_v2_joint_object.json (RevPAR mean +2.60, P>=4 0.259, P<=1 0.232). SYNTHESIS must re-base F01/F02 (0.29/0.27 object), B13 (0.31 not 0.26) and B15 (0.23 not 0.10) to them. Running: A16 response; A17, A18 audits.
