# WS22: Discussion round (method agents answer the red team and the scoreboard)

Orchestrator note: the original method agents are not addressable after the session change, so the round is run by three fresh Opus
agents, each defending a group of methods. Each writes `docs/margin-build/discussion/<group>.md`; the orchestrator concatenates them into
`docs/margin-build/DISCUSSION.md` and re-runs `score.py` once at the end. Groups: A = M1, M4, M6 (driver family); B = M2, M3 (history and guide);
C = M5, M7 and the harness (10).

## Instructions for each discussion agent

Read `docs/margin-build/00_BRIEF.md`, `docs/margin-build/prompts/M_common.md`, the notes and code of the methods in your group, the red team note
`docs/margin-build/notes/21_red_team.md` and `data/processed/margin_build/21_red_team/21_findings.csv` (filter to your methods and to findings
addressed to "all"), and, when it lands, `docs/margin-build/notes/20_scoreboard.md` (its numbered open questions addressed to your methods).

For every finding or question addressed to your methods:
1. Reproduce it (run the red team's check or your own few lines). State whether it reproduces.
2. Decide: ACCEPT (with the fix), ACCEPT-DEFER (why it cannot be fixed tonight, and how the numbers should be quoted meanwhile), or REJECT
   (with the evidence, reproduced, that the finding is wrong). No hand-waving: a rejection needs numbers.
3. For ACCEPT: apply the fix inside the method's own folder (`analysis/src/margin_build/<slug>/`), keep a `_pre_discussion` copy of any CSV or
   registry file whose numbers change, re-run that method's `run.py` under `py -3.13` (exit 0), and record before -> after for every headline
   number in the method's note under an appended "Discussion response" section. Specifically:
   - Oracle specs (`*revknown*`, `*nightsknown*`) registered as `prior_basis=PIT` must be re-labelled or removed from PIT rows so they never
     enter a survivor table; keep them as clearly labelled diagnostics.
   - Any input used without its `knowable_from` gate (M1 `d_steps`) must be gated or the spec withdrawn.
   - LIVE forecasts inconsistent with the guide sentence ceiling (3Q26 above 50.09% where management said "down slightly") must be either
     defended explicitly (why the model overrides the sentence) or reconciled; do not silently keep both.
   - Specs added after the first run (M3) must be labelled as post-hoc in the registry `notes` and the note, and the pass-line claim restated
     on the pre-registered specs only, with the post-hoc result shown separately.
4. **Do not run `score.py`** (three agents would race on it); the orchestrator runs it once after all three finish.
5. Write `docs/margin-build/discussion/<group>.md`: a table `finding_id | method | decision | reproduced? | what changed | files`, then a short
   statement per method of what it now claims (one paragraph, with the surviving numbers), then your recommended weight for each of your
   objects in the WS23 combination (0 if dead) with one sentence of reason.
6. Then poll for `docs/margin-build/notes/20_scoreboard.md` (every ~10 minutes, up to 60 minutes after you finish the red-team items). When it
   exists, answer its open questions addressed to your methods in a second section of the same file. If it never appears, say so and finish.

Budget about 1.5-2 hours. Make judgement calls yourself; do not ask questions. Finish with a 300-500 word summary listing decisions and every
file you changed. Do not run git commands.
