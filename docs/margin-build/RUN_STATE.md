# Margin build run: state ledger and continuation instructions

Owner: Krish (asleep from ~00:00 14 Sep 2026). Orchestrator: Claude Code (Fable 5.1) session in the main tree, working in
`C:\Users\krish\citadel-abnb-margins` (branch `krish/margin-build`). This file is the single source of truth for continuing
the run after a usage-limit pause, a crash, or a new session. Update the status table whenever a stage changes.

## How to continue (any orchestrator, any session)

1. Read `docs/margin-build/00_BRIEF.md` and this file. Then `ListAgents` to see what is still running.
2. For each workstream below with status not `done`: if its note `docs/margin-build/notes/<NN_slug>.md` exists and ends with a
   "For the model" section, mark it `done`. Otherwise, if no agent is running on it (ListAgents; or file mtimes under
   `data/processed/margin_build/<NN_slug>/` older than 40 min), relaunch it with `Agent` (subagent_type general-purpose,
   **model opus** (Krish's instruction 14 Sep 14:45, after the Fable limit; the table's model column is superseded)) using its prompt file `docs/margin-build/prompts/<NN>_*.md`, prefixed with
   `RESUME: check your output folder first and continue from what is on disk.` Pass the prompt file's full text as the prompt.
3. **Concurrency cap: at most 4 subagents running at once.** Respect stage order and the dependencies column.
4. After every stage completes: `git add` the margin_build folders (`docs/margin-build`, `analysis/src/margin_build`,
   `data/processed/margin_build`, `data/manifests/margin_build`, `analysis/figures/margin_build`, `model/ABNB_margin_model*.xlsx`)
   and commit on the branch with a message naming the stage. Verify nothing licensed is staged (`git diff --cached --stat`; no `data/raw`,
   nothing matching `*bloomberg*`, `*factset*`, `lseg`). Do not push until stage 4 is done.
5. Stage 4 (Codex audit) runs `codex exec` read-only from the worktree with `docs/margin-build/prompts/30_codex_audit.md`
   (see that file for the exact command); output `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`. Then 31 applies fixes, then 32 writes
   the morning report, updates `docs/revenue-forecast-strategy/WORKBOARD.md` (append rows only), commits, pushes, opens a draft PR.
6. Never run `git checkout`, `merge`, `stash`, `reset` here, and never touch `C:\Users\krish\citadel-abnb` or other worktrees.
7. A heartbeat cron in the orchestrator session fires every 30 minutes with the instruction to read this file and act on steps 2-5.

Manual restart if the session is gone: open a terminal in `C:\Users\krish\citadel-abnb` (main tree), run `claude`, and paste:
"Continue the margin build run per C:\Users\krish\citadel-abnb-margins\docs\margin-build\RUN_STATE.md. Fable subagents, max 4 concurrent."

## Stages and status (update in place)

Status values: `pending`, `running`, `done`, `failed`, `skipped`.

| WS | Topic | Model | Depends on | Status | Launched | Note path | Last update |
|---|---|---|---|---|---|---|---|
| 01 | Repo census of margin-relevant inputs | fable | - | done | 23:55 | notes/01_input_census.md | 00:15 |
| 02 | Financial panel: every P&L, add-back, below-EBITDA and FCF line, quarterly and annual, with seasonality | fable | - | done | 23:55 | notes/02_financial_panel.md | 04:50 |
| 03 | Point-in-time consensus for EBITDA/EPS/FCF/cost lines (LSEG + Bloomberg), surprise history | fable | - | done | 23:55 | notes/03_consensus_pit.md | 00:20 |
| 04 | External / alt-data signals for each cost line (archives, third-party public, macro) | fable | - | done | 23:55 | notes/04_alt_signals.md | 00:35 |
| 05 | Management statements v2 (all events incl. conferences) and 5 Nov guide-language pattern | fable | - | done | 00:15 | notes/05_mgmt_statements_v2.md | 04:30 |
| 06 | FY27 quarterly revenue path v2: audit and fix PR #32 lap on real quarters, reconcile to bridge v3 exit and WS29 | fable | - | done | 00:20 | notes/06_fy27_path_v2.md | 04:45 |
| 06v | Independent check of 06 (arithmetic, PIT, reconciliation); writes corrections into 06's folder as `_v2b` if needed | fable | 06 | done | 04:45 | notes/06v_fy27_path_check.md | 05:35 |
| 10 | Margin harness: targets panel, baselines, recency-weighted scorer, registry (imports frozen harness calendar/validator) | fable | 02, 03 | done | 00:35 | notes/10_harness_margin.md | 05:15 |
| M1 | Driver-based cost lines v2 (per-unit costs on nights, GBV, ADR, regional mix, seats, FX), PIT refits | fable | 10, 01 | done | 05:15 | notes/M1_driver_lines.md | 05:50 |
| M2 | Time-series and ratio methods (seasonal margin, incremental margin, % of revenue with drift) + baselines | fable | 10 | done | 05:15 | notes/M2_margin_ts.md | 06:05 |
| M3 | Guidance-policy model: FY floor + cushion, Q4-implied margin, language pattern; forecasts the guide and the actual given the guide | opus | 10, 05 | done | 06:05 | notes/M3_guide_policy_margin.md | 15:55 |
| M4 | Alt-data-augmented line model (headcount, ads, support, payments, rates), incremental value vs M1 | opus | 10, 04, M1 | done | 05:50 | notes/M4_alt_augmented.md | 15:25 |
| M5 | Consensus-anchored model: Street EBITDA at guide date + systematic bias and revenue-surprise flow-through | opus | 10, 03 | done | 22:30 | notes/M5_street_bias.md | 23:55 |
| M6 | Cycle and cost-flex model: cost response to growth deceleration; scenario engine over bear/base/bull revenue paths | opus | 10, 06v | done | 05:35 | notes/M6_cycle_flex.md | 15:05 |
| M7 | Below-EBITDA bridge: SBC, D&A, interest income, tax, share count, EPS; FCF bridge; backtests | opus | 10 | done | 05:15 | notes/M7_below_ebitda.md | 15:05 |
| 20 | Scoreboard: all methods and baselines, both windows, equal and recency weighted, coverage, parameter counts, error correlations | opus | M1-M7 | done | 23:00 | notes/20_scoreboard.md | 00:35 |
| 21 | Red team: leakage/PIT audit, overfitting, kill-list compliance, for every method | opus | M1-M7 | done | 22:30 | notes/21_red_team.md | 23:55 |
| 22 | Discussion round: three Opus agents (A: M1/M4/M6, B: M2/M3, C: M5/M7/10) answer the red team now and the scoreboard when it lands; orchestrator concatenates discussion/group_*.md into DISCUSSION.md and re-runs score.py once | opus | 21 (+20 for part 2) | done | 00:15 | DISCUSSION.md | 01:50 |
| 23 | Triangulation: final combined model, quarterly forecasts 3Q26-4Q27 + FY28, vs consensus and management, cyclicality, scenarios, workbook, SYNTHESIS.md | opus | 22 | done | 01:50 | SYNTHESIS.md + notes/23_triangulate.md | 05:35 |
| 30 | Codex (gpt-6-astra) read-only audit of the final model | codex | 23 | done | 02:30 | audit/CODEX_ASTRA_AUDIT.md | 02:55 |
| 31 | Apply the audit: triage, fix, re-run, re-score, record accept/reject | opus | 30 | running | 02:55 | audit/AUDIT_RESPONSE.md | 02:55 |
| 32 | Morning report, explainer HTML artifact, WORKBOARD rows, commit, push, draft PR | opus + orchestrator | 31 | pending | | MORNING_REPORT.md | |

## Log

- 15 Sep 02:55 Codex astra audit done (18 findings: 1 critical = h=1/h=2 calibration pools not print-date gated, h=0 unchanged; 12 major incl. cost stack not summing on display, add-back mismatch between cost and GAAP bridges, P(beat) 77% from a different object than the band (68.5% band-consistent), scenario P&L at constant margin, EPS bands EBITDA-only, FCF not re-derived from NI, consensus provenance missing in the final registry, n_params/n_train semantics, post-selection overstatement, 'attained coverage' wording, floor treated as a point, 'no cost dial' overclaim; 5 minor). Verdict: not ready to quote until fixed; h=0 point reproduces. WS31 apply-audit launched (Opus).

- 15 Sep 02:30 WS23 committed (final-margin__combined stack_clip 1.126/0.788pp h=0, p 0.0003/0.0001; h=1 fails vs Street; 3Q26 49.94%/$2,399M P(beat) 0.77; FY26 35.73%; 5 Nov 'approximately 36%'; FY27 34.64% vs Street 36.45%). Codex astra audit launched (stage 30, read-only, background).

- 15 Sep 05:35 **WS23 DONE.** `final-margin__combined` registered (1,152 rows, 4 pre-registered specs, PIT + full_sample,
  W1/W2/LIVE); `score.py` re-run once, exit 0; `analysis/src/margin_build/23_final_model/run.py` rebuilds everything end to end
  (exit 0, ~4 min). **PRIMARY PASS LINE MET**: `stack_clip` (six-member leave-future-out inverse-MAE blend, lambda 0.5 fixed a
  priori, plus a zero-parameter management-sentence clip) beats `seasonal_naive` on `adj_ebitda_margin_pct` at h=0 AND h=1 in both
  windows and both weightings -- h=0 MAE 1.126pp W1 (0.504x naive, 0.708x Street, NW(1) t -3.60 p 0.0003, better in 11 of 14,
  sign p 0.0032) and 0.788pp W2 (0.402x, 0.601x, t -3.84 p 0.0001, 9 of 10, sign p 0.011), on 2 declared parameters (52 inherited).
  In DOLLARS the four `final-margin` specs take the top four places at h=0 in both windows ($39.7M / $30.9M, 0.61x / 0.53x Street,
  sign p 0.090 / 0.011) ahead of M5 flow-through's $42.8M / $33.8M. **TWO FAILURES, both reported**: the pre-registered secondary
  test fails at h=1 (1.196x / 1.285x the raw Street) so 4Q26 is quoted from the Street, and h=2 fails in W2 (1.024x naive) so 2027
  is a labelled scenario. Hindsight share 0.019 / -0.059. CARD: **3Q26 49.94% / $2,399M** vs Street 49.78% / $2,361.5M (80% band
  $2,299-2,499M, conformal qhat 2.08pp on the 2024Q1+ errors, P(beat) 0.77, EPS $2.88 vs $2.845); the beat is DOLLARS, not margin
  (at Street revenue it is worth $8M). Clip does not bind at LIVE; the bias-corrected point (50.21%) would be capped at 50.085%, so
  both routes land 49.9-50.1%. **4Q26 28.90% / $918M (Street)**, combination 29.04%, M3 sentence path 29.90%. **FY26 35.73% /
  $5,098M**, +0.23pp over the 35.5% floor, which breaks on a 2H26 revenue miss of only 0.63% held / 0.94% flexed ($50-75M).
  **5 Nov sentence forecast "approximately 36%", which needs 4Q26 of 30.1% vs Street 28.9% (+$39M) -- the contestable number.**
  **FY27 SCENARIO 34.64% / $5,483M vs Street 36.45% / $5,766M (-$283M); incremental margin 24.7% vs Street's implied 43.7%; the
  whole gap is S&M at 23.6% of FY27 revenue.** 3Q26 line stack: S&M $790M +35% y/y, CoR $617M +12.5%, Ops $365M +6.4%, PD $382M
  +14.8%, G&A $283M +10.0% (the weakest number: 1H26 G&A ran -5.4% y/y). Street-independent variant (no consensus input anywhere)
  prints 49.88% and runs at 0.61-0.63x the naive. Leave-one-out: the two M5 objects are the accuracy (+0.08-0.09pp each if dropped);
  Street, M3 and FAMILY_A are insurance and each costs 0.02-0.04pp. Workbook `model/ABNB_margin_model.xlsx` (9 sheets) opens.
  OPEN FOR WS30/31: (1) the WS22 group C `revenue_leg_live.csv` harness patch is still unwritten -- every package's LIVE dollar row
  except WS23's sits on the naive leg; (2) WS31b's 4Q26 profile (24.7-25.9%) contradicts this build, the Street and the guide
  arithmetic, and is still the incumbent repo margin model; (3) there is no h=1 object with an edge and the 5 Nov trade is
  structurally h=1 on 4Q26.

- 15 Sep 01:50 WS22 done: three group files assembled into DISCUSSION.md; score.py and 20_scoreboard/run.py re-run once (exit 0). 3Q26 converges on the 50.09% ceiling (49.4-50.1%); M5 dollar flow-through, M3 allocation and M6 cost-of-revenue slope survive significance; nov_sentence_pin registered (4Q26 29.9%). WS23 triangulation launched (Opus).

- 14 Sep 00:35 WS20 DONE (relaunch). All seven method `run.py` plus the harness rebuild exit 0 (runtimes 11-226 s;
  `data/processed/margin_build/20_scoreboard/20_runpy_status.csv`); `score.py` re-run alone from clean, exit 0, 141 s.
  **Incident:** the first WS20 session's shell was still alive and running the same sequence, so two ran concurrently
  for ~12 min; in the relaunch sequence `M1_driver_lines/run.py` returned exit 127 where it shells out to `score.py`
  (a collision, not an M1 defect - the other sequence's M1 returned 0 and M1's registry files are intact). Every table
  was rebuilt from the clean re-score. **Lesson for the run: method packages invoke `score.py` internally, so two
  agents must never run method packages at the same time.**
  Results: M5 `dispersion_conditioned` is first in all four h=0 margin cells (W1 1.33 eq / 0.82 rw; **W2 0.74 / 0.62**
  vs Street 1.59 / 1.31 - ratios 0.57-0.67) and is the only family that beats Street at h=0; at h=1 **nothing beats
  the raw Street**; at h=2 nothing survives both windows on the margin. Error correlations say there are only ~3
  independent views (M1/M4/M6/M2-SARIMA r 0.93-1.00; M5 family r 0.85-0.92; M3 r 0.02-0.20 against everything).
  M4's warning CONFIRMED: 11 of 25 line-level objects that beat the naive on the lines are at or worse than naive on
  the margin, and the best-lines object (M4 `best1_rw`, 0.549x) is 1.101x naive on the margin. Registered quantiles
  are unusable (mean 80% coverage 0.91-1.00 vs nominal 0.80). **Recommended to WS23 (leave-future-out):** 60% M5
  `dispersion_conditioned|rw_hl4_med` + 20% M3 `actual_given_guide|rw_hl4_pin` + 20% driver family, MAE 0.99pp full /
  1.10 first half / 0.88 second half, beating Street in every split (0.76 / 0.70 / 0.84x). LIVE 3Q26 combination
  **50.39%**, method median 50.19% / $2,406M vs LSEG 49.78% / $2,361.5M; 4Q26 methods 28.64% vs Street 28.90%;
  FY27 methods $5,566M vs Street $5,766M (-3.5%). Two items need an owner: the LIVE revenue leg for 4Q26/FY27 is the
  harness naive rule ($75M above bridge v3 for 4Q26, +5.6% vs Street for FY27), and WS31b's 4Q26 margin profile
  (24.7-25.9%) contradicts every method and the Street. 13 numbered open questions for WS22 in section 11 of the note.
- 14 Sep 00:10 WS20 caveat: the WS22 discussion round started re-registering methods (M3 23:54, M1 23:55, M2 23:56,
  M4 00:01, M6 00:03) while WS20 was writing up. The WS20 board reflects the registry as scored at 03:55 UTC. M1
  dropping `e_revknown_rw` and M4 adding the knowable-from gate are exactly what WS20 section 0 rule 2 and open
  question 13 asked for, and WS20 excluded every oracle spec from every ranking already, so no conclusion changes.
  **After WS22 finishes, refresh the board with `py -3.13 analysis/src/margin_build/10_harness_margin/score.py`
  then `py -3.13 analysis/src/margin_build/20_scoreboard/run.py` (~60 s, exit 0) with no method package running.**

- 15 Sep 00:15 WS21 red team done and committed (890afeb): 27 findings (2 critical, 14 major), all PIT rules pass mechanically, but survives_both_windows is ~30% free and only M5's dollar flow-through beats the Street at p<0.05. Discussion round launched early as three Opus agents (prompt 22_discussion.md) so it overlaps WS20; original method agents are not addressable after the session change.

- 14 Sep 23:55 WS21 red team DONE (M1-M7 + M5 + harness; 10 reproducible checks under
  `analysis/src/margin_build/21_red_team/checks/`, `run.py` exit 0 in ~50 s; 27 findings in
  `data/processed/margin_build/21_red_team/21_findings.csv`: 2 critical, 14 major, 7 minor, 4 pass, 14 affect ranking).
  PASSES: all 8 mechanical PIT rules clean on 32 registry files / 87,628 rows (no input dated after its vintage, no
  street_as_of after its vintage, no already-printed quarter, no window or horizon mismatch); no kill-list number, no
  "close to known", no licensed row in a tracked path; full `run.py` replay of 10/M1/M2/M3/M4/M6/M7 + score.py all exit 0
  with 7 of 181 processed files changed, all of them build-stamp JSONs or the scoreboard M5 grew.
  CRITICAL: `survives_both_windows` is ~30% free at n 14/10 (sign-flip null 22.1 expected survivors vs 25 observed,
  P 0.39) and NO method built from ABNB's own history beats seasonal naive on margin at any conventional level
  (largest W1 |t| 0.83; all 9 significant cell-windows are W2-only and 7 of them are M5).
  MAJOR: 7 oracle specs (`*revknown*`, `*nightsknown*`) registered as prior_basis=PIT and one of them tops the survivor
  table; M1 `d_steps_rw` uses WS04 step dummies without the knowable_from gate at 7 of 14 W1 vintages (real PIT break);
  M3's two passing specs are post-hoc on its own pre-registration text and its W1 win is entirely 2023Q4; M2's sentence
  rule direction flips only 3 times in W1; intervals OVER-cover (mean cov80 0.95 vs 0.80) so M7's tax under-coverage
  claim is withdrawn; M1/M4/M6 put 3Q26 at 51.2-51.6% against a 50.09% ceiling sentence; M3's registered LIVE 4Q26
  34.51% is above every historical Q4. M5 AUDITED: its $ flow-through object is the one result in the run that
  survives an adversarial test (W2 ratio 0.581 vs Street, t -2.71 p 0.007, 9/10 quarters; W1 11/14, sign p 0.029),
  its margin claim does not (t -0.57 / -1.46), its dispersion regression is p 0.005 only on the sample its own
  pre-registration excludes (p 0.052 on 2022Q1+), and its LIVE +0.41pt 3Q26 beat is the 0.5 clip floor, which binds in
  21 of 39 backtest vintages. A 9-item kill-list addendum is proposed at the end of the note. WS20 and WS22 should read
  the note's RESUME section first.

- 14 Sep 23:20 WS20 first launch stalled (stream watchdog, no output on disk); relaunched on Opus with RESUME prefix.

- 14 Sep 23:00 M5 committed; first method to beat Street at h=0 (dispersion_conditioned 1.33/0.74pp vs 1.59/1.31; flowthrough $43/$34M vs $65/$58M); h=1 fails; 3Q26 $2,412M / 50.19%, P(beat) 0.64; quantiles unusable. WS20 scoreboard launched (Opus).

- 14 Sep 23:55 M5 done (street-bias: three objects `street_plus_bias`, `street_plus_flowthrough`, `dispersion_conditioned`,
  6 specs x 2 replays each, 1,296 rows per object registered; scorer re-run, 288 scoreboard rows; run.py exit 0).
  **PRE-REGISTERED PASS LINE FAILS for all 18 object-spec pairs** — every failure is at h=1, where the pre-guide next-quarter
  Street error has W2 mean +0.21pt against sd 1.94 (snr 0.11) and flips sign by era, so any bias correction adds noise
  (ratios 1.05-4.10). **At h=0 the Street is beaten decisively and this is the first method in the run to do it:**
  `dispersion_conditioned|rw_hl4` margin MAE 1.33pp W1 / **0.74pp W2** (Street 1.59/1.31), ratios 0.835/0.567, rw 0.656/0.557;
  `street_plus_flowthrough|rw_hl4` EBITDA $ MAE $43.1m W1 / **$33.8m W2** (Street 65.3/58.1), ratios 0.660/0.581, rw 0.545/0.524;
  four (object, spec) pairs pass all four h=0 cells, all with survives_both_windows AND rw_survives_both_windows = yes, and all
  clear seasonal_naive 0.35-0.78x. KEY MECHANISM: analyst dispersion works — margin surprise on EBITDA sd/mean slope +28.3pt per
  unit (se 8.8, p 0.005, n 19), and 3Q26 dispersion is the lowest in the sample (0.0085 vs rw reference 0.0497, ratio clipped at
  the pre-registered 0.5 floor), which is why the call is a SMALL beat. Seasonality of the surprise fails the pre-registered gate
  (ANOVA p 0.73 from 2022, p 0.43 in W2). Pre-registered 2022Q1 pool start validated: the `rw_hl4_from21` sensitivity is worse
  everywhere; equal weights (`ew`) are worse than doing nothing on margin — recency weighting is what makes this work.
  SUPPLEMENTARY (non-registrable, stamp fails the PIT rule): today's 4Q26 Street is a POST-guide number, and the post-guide h=1
  consensus under-calls margin by +1.11pt W2 (n 10, sd 1.61, 9/10 beats; last 8 +0.88, sd 0.73, 8/8) vs +0.21pt pre-guide —
  direction only, the correction beats raw on $ (0.85/0.85) but not on margin (1.30/1.12). CARD: 3Q26 adj EBITDA **$2,412m /
  50.19%** (4-spec composite; range 2,384-2,436 and 50.03-50.30) vs Street $2,361.5m / 49.78% = **+$51m / +0.41pt, P(beat) 0.64**
  (bear 0.57 / bull 0.73); re-run from the 6 Aug pre-guide vintage gives $2,390m, so the dollar call is $2,390-2,412m either way.
  FY26 35.92% on revenue $14,268m vs Street 35.62% and the ">=35.5%" floor. 4Q26 $932m / 29.16% is **NOT validated** (h=1) — quote
  a tilt, not a number. FY-floor anchoring confirmed and extended: consensus sits +0.37pt above the floor, 12/15 within 0.5pt.
  CAVEAT for WS20/21: M5's quantiles are useless (cov80 = 1.00 in every cell, CRPS worse than raw Street) — points only.
  CORRECTION to WS03: the lag-1 autocorrelation of the h=0 margin surprise, demeaned over the same 22 quarters, is 0.496
  (Ljung-Box Q(1) 6.18, p 0.013), not 0.26; WS03's conclusion (no exploitable AR) still holds — the structure is the downward
  trend in the size of the beat. Cross-method: M5 3Q26 50.2% sits between M1 51.6% and M2 48.1% and is the only one anchored to
  a published number.

- 14 Sep 22:25 Session resumed after Krish's re-login; M3, M4, M6, M7 all done on Opus (committed 5bd8fb5). M5 launched (Opus); WS21 red team launched (Opus) auditing M1-M4/M6/M7 now and M5 when it lands. WS20 scoreboard waits for M5.

- 14 Sep ~06:10 FABLE LIMIT reached (separate from the 5-hour window): M3, M4, M6, M7 killed. M3 had nothing on disk; M4 run.py + pre-registration only; M6 and M7 had code, outputs, registry files and pre-registration notes but no results write-up.
- 14 Sep 14:45 Krish (awake): 'move what you can to opus'. All four relaunched on Opus with RESUME prefixes; every remaining stage (20, 21, 23, 31, 32) switched to Opus. Heartbeat cron recreated as cf29b46b with the Opus instruction.

- 14 Sep 06:05 M2 done (7 objects, 29 specs; drift/ratio objects FAIL vs naive; q_sentence_direction|k_fit_rw passes: 2.07/1.64pp, rw 1.53/1.38, ratio 0.92/0.84; best in EBITDA $ and beats Street there; nothing beats Street on margin PIT; LIVE 3Q26 sentence rule 48.1% $2,309M vs Street 49.8%, naive-with-drift 51.35%). M3 launched.

- 14 Sep 05:50 M1 done (driver-lines registered; pass lines FAIL: margin h=0 MAE 2.26/1.91pp = naive equal-weighted, 0.87/0.85 rw; h=1 worse than naive because of the revenue leg; oracle-revenue spec beats naive everywhere; cor elasticity 0.81 on GBV stable, ops 0.76 on nights, sm 0.42 unstable; LIVE base 3Q26 51.6% vs LSEG 49.8%, gap = S&M; FY26 36.2%, FY27 35.1% vs LSEG 36.4%). M4 launched.

- 14 Sep 05:35 WS06v done: PASS WITH CORRECTIONS (independent FY27 $15,797M +10.71% vs WS06 $15,829M; all diffs are named judgement calls; one MEDIUM fix: 3Q26 bear/bull revenue was base in all scenarios -> v2b sets $4,755M/$4,878M). Margin model reads 06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv (copied in by orchestrator). Open decision for Krish: stacked ex-NA deceleration (base) vs no-2027-lap (+11.9%). M6 launched.

- 14 Sep 05:15 WS10 done (margin harness; 7 baselines x 14/10 dates; seasonal naive MAE 2.24/1.96pp; Street hardest 1.59/1.31pp, bias -1.2pp, only object surviving both windows; quarterly-sentence direction rule 13/14 right, flagged for a method; LIVE vintage 2026-09-11). Stage 2 launched: M1, M2, M7 (06v still running).

- 14 Sep 04:50 WS02 done (34-quarter x 145-column panel, 3,066 provenance rows; adj EBITDA rebuilt within $0.97M all 22 quarters; seasonality mechanical except Q1; G&A ex-lodging series; ops cash per booking $10.74 -> $8.06; correction: repo Q4 SBC totals wrong in three panels). Brief corrected: venv python lacks scipy/statsmodels/sklearn; all modelling on py -3.13.

- 14 Sep 04:45 WS06 done (FY27 revenue base $15,829M +10.94%, bear +5.2%, bull +15.7%; nights +6.6% vs B3 +9.5; front-loaded quarters 1Q27 +14.0% to 4Q27 +9.1%; 8 audit findings on PR #32, two HIGH: no FY27 levels, lap placement inconsistent with bridge v3). WS06v launched.

- 14 Sep 04:32 LSEG desktop API (localhost:9000) refuses connections although Workspace processes are alive; WS03's daily raw pulls (to 11 Sep) are cached so no downstream stage needs LSEG. Krish: re-open/re-sign-in Workspace in the morning if a fresher pull is wanted. Not touching credentials.

- 14 Sep 04:30 WS05 done (377 statements, 183 new, 155 from 31 non-earnings events; November rule: numeric floor -> 'approximately floor+50bp'; 5 Nov prior: approx 36% (0.45), 35.5% held (0.35), at least 36% (0.15); Q4 print beats sentence-implied Q4 by 0.7-4.3pt n 3; margin_total kept 85% n 55).

- 14 Sep 01:24 USAGE LIMIT hit (session limit, reset 3:50am ET): WS02, WS05, WS06, WS10 agents killed mid-work (WS02 had all CSVs but no note; 05/06 only run.py stubs; 10 only targets.csv). Heartbeats queued.
- 14 Sep 04:20 Limit reset; all four relaunched with RESUME prefixes.

- 14 Sep 00:35 WS04 done (58 series, 1,146 tests; survivors: 3m T-bill -> interest income r 0.83 n 18, rule 0.86 x T-bill x earning base; Trends category share -> S&M per night r -0.64 n 18; careers postings vs PD r 0.9 but n 6-7; all else fails). WS10 harness launched on fallback panel, will switch to WS02 when it lands.

- 14 Sep 00:20 WS03 done (LSEG daily PIT consensus 2021-2026, 22/22 prints; Street under-called margin 21/22, W1 +1.82pt, W2 +1.70pt, last four +0.43pt; flow-through beta 0.57 weak; Street anchors on FY floor; 3Q26 cons EBITDA $2,361.5M / 49.78%, FY26 35.62%, FY27 36.45%; Bloomberg file pull-date anchored). WS06 launched.

- 14 Sep 00:15 WS01 done (123-row census, 26 gaps, top-10 unused inputs: interest income = balances x DTB3, 10-Q MD&A deltas, lagged S&M deleverage, regional-mix line, hosting commitments...). WS05 launched.

- 13 Sep 23:10 Krish's brief received; questions answered (targets: adj EBITDA + six lines, GAAP/EPS bridge, FCF, 5 Nov language;
  revenue path: bridge v3 + audited FY27; sources: archives, third-party public, Bloomberg local, LSEG API, EDGAR, transcripts;
  Codex audit-only then Claude fixes; in-session heartbeat resume; Fable, max 4 concurrent, Opus for simple tasks; seasonal + macro cycle; branch/push/PR).
- 13 Sep 23:30 LSEG desktop session tested OK via lseg-data on `py -3.13` with `LSEG_APP_KEY`. Codex exec smoke test OK (read-only, ephemeral).
- 13 Sep 23:55 Stage 1 launched: WS01-04 on Fable (4 concurrent). Heartbeat cron 6c78a4f3 at :13 and :43.
- 13 Sep 23:40 Worktree `citadel-abnb-margins` created from origin/main fd4272f; raw junctions added; brief and ledger written.
- 14 Sep 15:05 M6 done (cycle-flex registered, 384 scoreboard rows; run.py reproduces byte-identical, exit 0). Cost elasticity to revenue: cor 0.56 (t 5.6), ops 0.44 (t 3.4), sm 0.42 (t 2.3), pd -0.21 (ns), ga -0.11 (ns), total 0.36; ABNB total opex k 0.14 ns vs BKNG 0.61 / TRIP 0.63 / EXPE 0.44 and BKNG advertising 0.87-0.98 -- ABNB has no cost dial. T1 FAIL (pd wrong sign at every lag), T2 FAIL (2H22 reproduction 1 of 3 quarters inside 1.5pp; the miss is the PIT revenue leg, not the k s), T3 PASS (2025 shock quarters ratio 0.92 both windows), T4 costs fall slower than they rise for ops/sm/total p<0.02. Harness: l0_rw h=0 W1 MAE 2.20pp ratio 0.984 (rw 0.812), W2 1.77pp 0.905 (rw 0.769), survives both windows both weightings; h>=1 fails. LIVE on M1 base: 3Q26 51.57% (Street 49.78%, guide-implied 50.09%), 4Q26 28.47%, FY26 36.18%, FY27 35.14%; 1Q27 trough 19.5% (band 17-22). FY26 floor 35.5% survives a 1.9-2.5% 2H26 revenue shortfall ($149-203m), 8.0% with cuts; 1% of 2H26 revenue = 27bp flexed / 36bp held. FY27 bear 31.3-32.4% needs a $386-508m cut. DO NOT use M6 FY28 (31.3% vs Street 37.7%): positive growth intercepts compound.

- 14 Sep 15:25 M4 done (alt-augmented registered, 9,632 rows in lines_aug + margin_aug; run.py 465 s exit 0). NEGATIVE RESULT: 50 pre-registered one-signal tests on M1 lines under a strict knowable_from gate; 1 survivor (ga ~ emp_computer_systems_design lead 2, IV 0.898/0.896 W1, 0.895/0.898 W2, c +1.91 t 2.11 n 18) and the 1,000-draw random-series placebo puts the false-positive rate of that same pass line at 5.5% single / 22.5% best-of-5 on G&A, so the survivor is inside the noise; it moves margin MAE by 0.6%/0.1% and the 5 Nov quarter by +0.13pp. 47 leakage placebos (gate off): median IV 1.02-1.05, zero pass -- even future values do not predict the cost lines. KEY CROSS-METHOD FINDING: best1 (best signal per line, in-sample) improves 4 of 5 LINES yet makes the MARGIN worse (MAE 2.26 -> 2.43pp W1, 1.91 -> 2.16 W2) because M1 line errors cancel in the sum; every line-level tuning claim in this run should be re-scored on adj_ebitda_margin_pct (flag for WS20/21). WS04 Trends -> S&M does not survive knowability (lead 0 gate-off 0.83-0.85, knowable lead 1 1.02-1.08; honest quarter-to-date version 0.88-0.94, fails the equal-weighted leg); careers -> pd has 2 usable backtest quarters, untestable. LIVE margin table = M1 unchanged (3Q26 51.6% $2,478m, 4Q26 28.5% $905m, FY26 36.2%, FY27 35.1%). Interest-income hand-off to M7: avg earning base x tbill3m x 0.862 (2Q26 checks $183m vs $183m).

- 14 Sep 15:55 M3 done (guide-policy-margin: `actual_given_guide` 9 specs x 2 replays + `q4_implied`, both registered, scorer
  re-run, 224 scoreboard rows, run.py exit 0). The harness `guide_implied` baseline's -4pp bias is the PRORATION, not the guide:
  same guide, same PIT revenue leg, but allocating remaining EBITDA by m[q-4]+delta and clipping the quarter that carries a
  quarterly sentence gives h=0 MAE 2.18pp W1 / 1.44pp W2 (rw 1.64/1.34), 0.50x/0.38x guide_implied, 0.98x/0.74x naive -
  survives_both_windows AND rw_survives_both_windows = yes (specs rw_hl4_pin and last_pin); nothing beats Street (1.59/1.31).
  FAILS: the pre-registered main spec rw_hl4 (no pin) 3.83/1.97; the cushion at FY level (literal guide MAE 1.22pp beats last
  1.98 / rw_hl4 2.75 ex-FY22) - the cushion collapsed 7.97 -> 2.27 -> 1.40 -> 0.60 and any backward-looking estimate over-predicts;
  the February floor rule (MAE 82bp, wrong in 2024 and 2026); no usable h=1/h=2. PASSES: November sentence rule type 4/5 and level
  0bp on the two numeric-floor years -> 5 Nov 2026 = "approximately 36%"; q4_implied beats naive (2.87 vs 3.88pp, n 3) but is
  systematically 2.87pp LOW, and the Street sits on the implied number. CARD: FY26 36.0-36.6% (Street implies 35.63%); 4Q26 at the
  modal sentence 30.9% / $983m vs Street 28.90% / $914m; budget identity 1pp of 3Q26 margin = -1.51pp of 4Q26. For M2: "slightly"
  carries magnitude (mean |y/y| 1.5pp n 3 vs 3.6pp plain n 13), so k should be ~1.0-1.5pp for 3Q26, not 2.03.
