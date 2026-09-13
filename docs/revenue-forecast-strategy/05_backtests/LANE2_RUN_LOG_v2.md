# Lane 2 — resumed execution and audit correction

Codex parent · 13 Sep 2026 · `codex/lane2-full` · base `051b03a864593f35c75236c8e1bcf4e0cc40c67e`.

## 0b and prior-run audit

The original [run log](LANE2_RUN_LOG.md) and full failure receipts remain unchanged. That run verified 55/55 files, 47 frozen tests, 37 FORMAT 1.1 tests, 8 returns tests, 63 kernel tests and 12/12 kernel acceptance cells. It then stopped on cross-platform floating-point serialization differences produced by writing over the frozen scoreboard. No downstream analysis was delivered.

The user's follow-up explicitly requests that this be audited and made to work. The committed `harness_v1_1/tests/test_v1_1.py::test_historical_scores_are_identical_to_the_frozen_scoreboard` already uses absolute differences below 1e-9 for MAE/RMSE. Treating sub-1e-11 differences as an analytical failure was an unhelpful implementation of the gate. The original literal-Git STOP is retained as a failed attempt, not relabelled PASS.

## Pre-registration — recorded before resumed execution, 2026-09-13 14:54 UTC

WP-H11/RET resume claimed by parent; A2 and all other packages remain pending until this gate passes. Add a new `lane2_validation_v1` wrapper; edit no frozen source, input, or previous note. Call the actual existing scorer `main()` functions with only the three output destinations redirected to a new audit directory. The frozen scorer runs first, then FORMAT 1.1. Both read the real registry and the frozen calendar/targets. They must exit 0. Their saved output must match on every column; all 276 pre-existing rows must be present, with exact keys, sample counts, text, booleans, integer fields and missingness; every floating metric must have absolute error <1e-9 (rtol=0). No tolerance is applied to pass/fail flags. This extends the committed test's numerical criterion to all metrics. Every frozen tracked file must retain its SHA-256 throughout. At later stages, new method rows may be added only in the new snapshots; all original rows remain checked.

Run the 47/37/8/63 existing tests unchanged, plus meaningful tests proving the new comparator rejects missing/duplicate keys, changed counts, changed verdicts, missingness and material numeric drift. Rebuild RET with the existing code into the new audit directory, verify 23 events and entry strictly after each letter, and verify each excess leg equals ABNB minus QQQ within 1e-9. Retain the earlier kernel acceptance receipt and its unchanged-source check; no need to rewrite its outputs again. Complete the loader and network audits. Then proceed through A2, packages, refuters and CLOSE under the original user instructions.

## Results

Gate 1 **PASS** at 2026-09-13 14:57:54 UTC. Command: `python -X utf8 analysis/src/forecast_methods/lane2_validation_v1/run.py --stage gate1 --tests`, exit 0. New comparator tests: 9/9, exit 0. Existing tests: frozen 47, FORMAT 1.1 37, returns 8, kernel 63. Both scorers: 4,109 registry rows / 69 objects, 276 scoreboard rows; exit 0. All original 276 rows match across all columns under the preregistered criterion. All 81 protected tracked file hashes are unchanged.

RET: 23 events; every entry strictly after its letter; excess identity verified at absolute tolerance 1e-9. Legacy tie-out n=23, median absolute difference 0.02856791pp. Committed OHLC retrieved 2026-09-13T06:07:17+00:00, last bar 2026-09-11. Sunday is not a later trading day, so no refresh is needed. Loader: calendar 25 / targets 25 / L0 161; RUN_DATE 2026-09-13. Pre-guide Q3 consensus LSEG 4610.0 at 2026-08-06, pit_usable True.

Full reproducible receipts: `data/processed/forecast_methods/lane2_validation_v1/gate1/summary.json`, `tests_*.txt`, scorer stdout/CSV/Markdown snapshots, rebuilt returns and before/after SHA-256 manifests. No frozen files were rewritten. Kernel acceptance 12/12 PASS is retained from the original run; unchanged kernel source and output hashes are verified in this run.

Network: sandbox sockets were blocked; approved public-endpoint retry returned FRED 200, Trade.gov 200, Eurostat 200, Yahoo root 404 (reachable; root has no resource). Approved yfinance history check succeeded, last bar 2026-09-11. `gh` is absent; use the GitHub connector or the compare URL at close. This is a real public-network path for C2/M, with sandbox escalation where necessary.

The resumed gate changes output handling and applies the existing test tolerance. It does not alter model calculations, test code, source data, forecast vintages, or research pass lines. Initial failure evidence remains separately preserved.

## RESUME

Gate 1 checkpoint `a825542` pushed and remote hash verified. A2 ran alone with exactly its brief. Gate 2 now PASS after one final-review correction; research verdict PARTIAL. Parent independently audited 14 candidate rows, 12 K0 estimates, 56 return cells, Wilson intervals and control residualization. W1 11/14 evaluable, 7/8 hits; W2 9/10, 6/7 hits. Signed 20-day returns -0.308pp / -0.983pp; both intervals cross zero. Joint control n=6 in both windows has unknown vendors and is provenance-limited. Two LIVE Q4 rows at 2026-09-13; 48 A2 registry rows total. Both scorers after reviewed registration exit 0, 4,157 rows / 280 scores, all 276 old rows and 81 protected hashes unchanged. Details: [A2_GATE_REVIEW.md](A2_GATE_REVIEW.md).

Gate 2 checkpoint `1c0ce4a` pushed. F/B2/M received exactly their respective brief paths, no inherited history; C2 received its exact brief when F returned. L skipped: not sanctioned (`SANCTIONED_BY_THEO: no`). CLOSE uses the new snapshot runner and its preregistration, preserving every prior result.

## Batch 1 integration audit — 2026-09-13 17:13 UTC

F completed with research PARTIAL, 12 package tests and a successful rebuild/registration. Parent independently recomputed 18 stock observations from the raw GBV panel and frozen phi coefficients, three excess observations and all six LIVE scenario points. Exact excess is +1.969114/+8.047784/+9.705899pp; the middle value rounds to +8.0, so literal +8.1 acceptance remains failed. The later correction in Theo's source rejects the original joint solve; m remains unidentified, and the fee-only u values are conditional. Twelve LIVE rows use three scenario IDs, two quarters, two replay labels. Evidence: `lane2_validation_v1/f_independent_review.json`. The figure is legible. No team decision was adopted.

B2 completed its numerical run with research FAIL: W1 11/14 pairs, 5/9 high-signal hits, corr 0.687245; W2 9/10 pairs, 4/7 hits, corr 0.670530. Parent independently reproduced 12 K0 guide points, 28 executable return cells, consensus roles/stamps, counts and correlations. Evidence: `lane2_validation_v1/b2_independent_review.json`. The unseasonal GBV extrapolation is a limitation; the large LIVE term values are conditional arithmetic. Forty-nine rows registered, including four LIVE rows. B2's initial new-package baseline loader integration failed; the failure receipt remains and the one corrected run passed. No frozen test failed.

M appended 10 documented current observations, 161→171: eight Yahoo/LSEG-family and two S&P. The original raw byte prefix and protected August row remain identical. Twenty frozen L0 tests passed. Parent also compared the dated backup to the pre-lane Git content and validated all 18 FORMAT 1.1 LIVE rows. The first parent audit incorrectly compared CRLF working bytes directly with Git's normalized LF blob; that test bug was fixed once with its receipt retained. Content comparison normalizes CRLF only; local prefix preservation remains byte-exact. M additionally preserves canonical hashes for clean-checkout verification.

The cross-package rebuild check exposed a real A2 bug after the append: pandas rejected the mixed date-only / UTC-minute timestamps. The parent retained `lane2_validation_v1/a2_after_m_failure.txt` (exit 1, no registration write). Repair is pending; historical evidence is unchanged. This is a new-package integration defect, not a frozen infrastructure failure.

Parent command `python -X utf8 analysis/src/forecast_methods/lane2_validation_v1/run.py --stage after_batch1` exited 0: both scorers 4,218 registry rows /72 objects and 284 score rows; all 276 original rows and 81 protected hashes unchanged. Returns still 23 with every entry after its letter. The independent append/LIVE audit is `lane2_validation_v1/after_m/integration_review.json`.

Remaining: repair A2 timestamp handling, complete C2, review all final notes and their exact proposed sentences, checkpoint, nine refuters, then CLOSE and the PR.

## Repairs completed and completed-package checkpoint — 17:20 UTC

A2 now parses mixed timestamps in UTC and cuts off at the actual run-start instant. Sixteen tests pass; rebuild exits 0 in 21.170s. Prior evidence is copied under `alpha_a2/pre_m_refresh_20260913T171409Z/`. The old Alpha Vantage $3,158M (11 Sep) comparison is replaced by Yahoo/LSEG $3,161.02149M (13 Sep 15:20 UTC); S changes from +0.00721857% to -0.08837420%. Kernel guide $3,158.227962M, all historical tables, exact memo sentence and all 48 registry bytes are unchanged. The parent independently reran the A2 audit successfully after repair.

B2's printed-quarter horizon label conflicted with FORMAT's `horizon_q` definition (harness README line 66). Parent required the authoritative unit: target calendar quarter minus vintage calendar quarter. All 49 registry horizons are corrected: 47 rows use 1 and two LIVE Q1 rows use 2; the sidecars retain printed-quarter horizons 2/3. The old registry is preserved in a diagnostic snapshot. All point forecasts and seven research CSVs are unchanged; 23 tests pass. Parent's integration audit now enforces this field's units.

F supplied its exact proposed memo sentence and clarified active versus elapsed time. M completed eight append-safety tests as well as the 20 frozen L0 tests. The parent reviewed each final note, provenance and limits. C2 remains in progress; no refuter verdict is available yet.

`run.py --stage after_repairs --tests` exits 0: 47 frozen /37 FORMAT 1.1 /8 returns /63 kernel tests, both scorers 4,218 rows and 284 scores, original276 rows and81 protected hashes unchanged. `review_lane.py --stage after_repairs` exits 0: append invariants, all18 LIVE rows and horizon units valid. The new [LIVE score sheet](LANE2_LIVE_SCORE_SHEET.md) lists nine scenarios with both replay labels. No new method beats its historical baseline: A2 guide_mid has no baseline; B2 PIT RMSE ratios are 4.374× W1 and 4.283× W2. No new eligible leader warrants SCOREBOARD_v3.md.

This additional checkpoint preserves the completed A2/F/B2/M work and integration repairs while C2 runs. The all-package checkpoint and nine refuters still follow; nothing is promoted in advance.

Checkpoint `cc79a40` pushed successfully. To keep the queue full, two refuters began on these committed package artifacts while C2 completed its independent capture; no early claim was promoted, and the all-package checkpoint remains due after C2.

## Refuter ledger (all exact proposed sentences; partial is not survived)

| Package | Lens | Verdict | Explicit attacks | Finding |
|---|---|---|---:|---|
| A2 | vintage | SURVIVED | 9 | Independent clipped-input reconstruction matches 7/8 and6/7; no future data needed. Synthetic same-day23:59 consensus exposes a historical selector defect; current date-only data do not exercise it. Routed to A2 author for hardening without changing the historical result. |
| A2 | power | SURVIVED | 7 | Eight unique high-signal events; W2 reuses seven. Exact permutation p=.07143/.14286; IID reference 80%-power return MDE +6.448/+7.269pp. The sentence is descriptive and does not prove an absent edge. |
| A2 | mechanism | SURVIVED | 6 | Counts and 22 raw OHLC return legs reproduce. Guide-gap correlation falls .626236→.000585 after GBV-surprise control on the same six unknown-vendor cases; this is a limited confound diagnostic. All three fixed hedge choices retain negative mean returns and zero-crossing intervals. |
| F | vintage | SURVIVED | 8 | Raw KPI/frozen-phi reconstruction reproduces 21 stock cells, endpoints 1.969114/9.705899pp and Q4 stress $3,185.195735M. The stock fit is retrospective; historical forecast n=0 in both windows. Alternative inherited fits change the residual's level. |
| F | power | SURVIVED | 8 | The conditional arithmetic reproduces; 2,025 grid cells collapse to 37 unique leakage values per quarter and provide no empirical sample. The overlapping six-event alarm check is underpowered. No causal or forecast power is claimed. |
| F | mechanism | SURVIVED | 7 | Both host and guest fees enter UF, so payer migration alone cannot reroute fees into FP. A hypothetical 15.20% fee-yield decline could mimic Q2 excess. The $29.580M stress is gross: applying 25% rebooking gives $3,192.591M, versus $3,214.776M if fully embedded already. |
| B2 | vintage | SURVIVED | 8 | Independent clipped-input reconstruction matches 5/9 and 4/7 and all four negative return means. Actual PG/AP stamps are admissible date-only rows. Synthetic post-close acceptance and two omitted transitive CSV hashes are documented and routed for repair. Revision measurement begins before signal availability. |
| B2 | power | SURVIVED | 8 | Wilson intervals 26.7–81.1% /25.0–84.2% include 70%; the claim reports failure of the sample hurdle, not population accuracy below 70%. W2's seven strong events are nested within W1's nine. Every negative mean can flip after one omission. |
| B2 | mechanism | SURVIVED | 7 | Announced-guide gaps correlate .984 with revisions in both windows; kernel partial correlations are only .162/.195 and incremental in-sample R² .00083/.00123. The interval begins before signal availability. These diagnostics reject stronger independent-mechanism or stable-negative-alpha claims. |

All nine refuters returned SURVIVED for the three exact, qualified sentences, with 68 explicit attacks in total. Each sentence clears the 2-of-3 threshold; no positive research hypothesis is promoted by these votes. Every final note contains at least five explicit attacks. The synthetic timestamp receipts remain intact; implementation repairs are separate follow-ups rather than rewritten refuter verdicts.

## All packages returned — 2026-09-13 17:35 UTC

C2 delivers `macro_pulls/review_capture/`: 35,124 normalized rows across14 source records,124 rows with verified release dates,0 historical PIT admissions. Nine tests pass; the agent's offline rebuild exactly reproduces three NTTO analysis CSVs. Parent's independent `review_c2.py` also passes: all14 source hashes, row counts, finite values, unique keys, release/retrieval chronology and two level-RMSE ratios checked. Corrected NTTO total-full levels: W1 1.032389× naive(n14), W2 .677116×(n10); this fails both-window acceptance. The old cache omitted Jan–Sep2022 and used row shifts across the gap. DATATUR contains700 traveler-count rows distinguished from monetary rows by Level03; the initial missing-value adapter rejection was fixed once and retained. BLS supplies103 exact-series CPI rows; a4-row dated CoStar excerpt is a static fallback. FRED timed out; automatic CoStar refresh and JNTO edition discovery remain incomplete. No forecast was registered. C2 is PARTIAL infrastructure /FAIL research line, not a fabricated PIT pass.

A2's intraday selector is now hardened: explicit times require a timezone and must precede16:00 America/New_York on the letter day. Exact-close, late and ambiguous naive times are rejected; date-only morning-of-print rows remain admissible. Initial10 failing boundary cases are preserved. Final28 tests pass; isolated no-registration rebuild exits0 in16.137s. All21 existing output/registry files remain untouched; seven rebuilt historical CSVs and48-row registry preview are byte-identical. Snapshot: `alpha_a2/intraday_boundary_validation_20260913T173104Z/`. The vintage refuter's original finding remains a valid pre-fix receipt, and its exact-claim verdict is unchanged.

All five requested research/data packages have returned. L skipped: not sanctioned. The all-package checkpoint includes C2 and this boundary repair; the remaining refuter queue continues independently on unchanged empirical tables.

Staged-file review: only this lane's source, normalized public data, notes and retained receipts. No environment, bytecode, licensed export or unrelated working file is staged. The only full diff-whitespace findings are pytest formatting in the preserved initial A2 failure receipt; the receipt is intentionally retained verbatim. Source and documentation whitespace checks pass.

All-package checkpoint `dba7abe` pushed. F's three refuter votes are now recorded above; B2 vintage/power reviews independently reproduce the historical numbers and are writing their final notes, while B2 mechanism is running. A B2 synthetic explicit post-close consensus row exposes the same class of historical timestamp boundary defect found in A2. All actual historical rows used are the convention-authorized date-only stamps. The parent will require a preserved regression receipt and a no-registration rebuild after hardening; no empirical result is changed in advance.

## Refuter checkpoint — 2026-09-13

All nine notes have been read by the parent, checked against the exact sentences and their independent receipts, and recorded in the ledger above. A2/F/B2 each receive vintage SURVIVED, power SURVIVED, mechanism SURVIVED. The strongest attacks constrain causal, population and trading interpretations; those qualifications will accompany all three sentences in the claims file. The B2 mechanism reader's initial comment-preamble failure was repaired once and retained. No refuter ran a scorer or changed a registry. B2's separate timestamp/dependency repair is finishing its isolated rebuild before CLOSE.

Parent audited the diff against starting commit `051b03a`: the only modified pre-existing files are the sanctioned append to `L0_vintage_register.csv` and `WORKBOARD.md`; all previous packages, notes and frozen files are unchanged. This checkpoint stages only the nine new refuter packages/receipts/notes and the shared status/log updates. Unrelated workspace files remain unstaged.
