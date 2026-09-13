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

Next: checkpoint Gate 2; run F/B2/M in parallel, C2 as a slot frees, then three refuters per A2/B2/F. L skipped: not sanctioned (`SANCTIONED_BY_THEO: no`). CLOSE uses the new snapshot runner and its preregistration, preserving every prior result.
