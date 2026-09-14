The initial Lane 2 run stopped when the frozen scorer rewrote its CSV with platform-level float serialization differences. This change makes the authorized workflow reproducible while retaining that failure: both existing scorer implementations run against the real registry into new audit snapshots, with every frozen file preserved. It also repairs the A2 crash after M appended mixed-format timestamps, hardens A2/B2 historical intraday cutoffs, and corrects B2's registry horizon units.

The completed packages add 109 registry rows (including 18 LIVE rows), 10 dated current consensus observations, and 35,124 normalized public macro observations. Nine independent refuters reproduced the three qualified sentences below. A2 and F remain PARTIAL; B2 remains FAIL. No established trading edge is asserted.

## Gates and validation

- 0b: all 55 required paths present, MISSING 0. The verbatim audit and original failed run remain in [LANE2_RUN_LOG.md](docs/revenue-forecast-strategy/05_backtests/LANE2_RUN_LOG.md); the resumed execution is [LANE2_RUN_LOG_v2.md](docs/revenue-forecast-strategy/05_backtests/LANE2_RUN_LOG_v2.md).
- Gate 1 and final CLOSE: 47 frozen tests, 37 FORMAT 1.1 tests, 8 returns tests, 63 kernel tests; kernel acceptance 12/12 PASS. Both scorers exit 0, frozen first, then FORMAT 1.1. Final registry: 4,218 rows /72 objects; final snapshots: 284 scores.
- All 276 pre-existing score rows retain exact keys, counts, flags, text and missingness; numeric differences are below the preregistered 1e-9 absolute tolerance, rtol=0 (maximum 7.28e-12). The two current scorer snapshots match exactly. All 81 protected tracked file hashes remain unchanged; the committed frozen scoreboard is byte-identical.
- Returns: 23 events, every entry strictly after its letter, all executable excess legs equal ABNB minus QQQ within 1e-9. Legacy tie-out median absolute difference 0.028568pp, n=23.
- Gate 2: A2 note checked for its verbatim preregistration before results, both-window counts/Wilson intervals, consensus provenance, executable returns, controls, imported kernel and live registration. One provenance correction retained the unknown-vendor control limitation. Independent parent checks reproduced 12 kernel guides and 56 return cells. See [A2_GATE_REVIEW.md](docs/revenue-forecast-strategy/05_backtests/A2_GATE_REVIEW.md).
- New-package checks: A2 28 tests; B2 44; F 12; C2 9; M 8 plus the 20 frozen L0 tests; audit comparator/receipt-protection 10. Independent parent audits cover A2/B2/F/C2, M's append and all LIVE rows. Initial new-code failures and corrected runs are preserved.
- Final source comparison to base modifies only the sanctioned L0 append and WORKBOARD among pre-existing files. No environment, bytecode, raw store or licensed export is included.

Reproduce final integration from the repo root with the existing environment, using a fresh stage name:

```text
python -X utf8 analysis/src/forecast_methods/lane2_validation_v1/run.py --stage reviewer_audit_20260913 --tests
python -X utf8 -m pytest analysis/src/forecast_methods/lane2_validation_v1/tests -q
python -X utf8 analysis/src/forecast_methods/lane2_validation_v1/review_lane.py --backup data/processed/forecast_methods/L0/backups/L0_vintage_register_20260913T151840Z.csv --stage reviewer_audit_20260913
```

Saved final evidence: `data/processed/forecast_methods/lane2_validation_v1/close/`. The runner rejects an existing stage before doing work. It calls the actual scorer entry points with only output destinations redirected; it does not substitute alternative scores.

## Packages

| Package | Preregistered hurdle | Result | Refuters: vintage /power /mechanism |
|---|---|---|---|
| A2 | Both windows: ≥70% guide-sign hits for abs(S)>1pp with n≥6, positive signed 20-day excess return with 90% interval excluding zero, and joint-control correlation sign retained. | PARTIAL: 7/8 and 6/7 hits; returns −0.308/−0.983pp with intervals crossing zero; joint control n=6 has unknown consensus vendors. | SURVIVED /SURVIVED /SURVIVED |
| F | Reproduce 2.0/8.1/9.7pp stock diagnostic; publish alarm n, three nights paths, filing answer and proposed refutation condition. | PARTIAL: exact 1.969/8.048/9.706pp, so the middle literal rounds to 8.0 and that hurdle fails. All scenarios run; historical scenario n=0/0. The inherited joint migration solve is rejected, with unidentified migration and explicit gross stress retained. | SURVIVED /SURVIVED /SURVIVED |
| B2 | Both windows: ≥70% sign accuracy for abs(S1)>0.5% with n≥6 and correlation>0.4. | FAIL: 5/9 and 4/7 hits; correlations .687/.671; negative 20/60-day mean aligned returns. | SURVIVED /SURVIVED /SURVIVED |
| C2 | Document every source, cadence, lag and publication column; reproduce the stated NTTO nights baseline ratio on the same cells or publish the observed ratio and reason. | PARTIAL infrastructure /FAIL full research line: 35,124 rows, 14 source records, 124 dated releases, zero historical PIT admissions. Corrected nights-level ratios 1.0324× W1 n14 /0.6771× W2 n10. | Not a headline package |
| M | Vendor, stamp and n on every appended row; dated backup; protected August row unchanged; before/after counts and passing L0 tests. | Integrity PASS /coverage PARTIAL: 161→171 rows; eight Yahoo/LSEG-family and two S&P observations. Exact raw byte prefix and protected row preserved. | Not a headline package |
| L | Header must authorize access. | L skipped: not sanctioned (`SANCTIONED_BY_THEO: no`). | Not run |

The nine refuters document 68 explicit attacks. They validate narrowly worded descriptions of failed or conditional results; no positive hypothesis receives a pass by inference from those votes.

A2 now rejects explicit timestamps at/after 16:00 New York or without a timezone while preserving date-only convention rows. B2 applies the same boundary, records both transitive kernel CSV hashes, and uses calendar-quarter difference for FORMAT `horizon_q`; printed-quarter horizon remains a separate sidecar field. Both repairs rebuild historical tables and registry previews byte for byte. M's September current rows never enter historical tests.

C2 fixes the NTTO calendar gap: the old cache omitted Jan–Sep 2022 and row shifts crossed the gap. The old growth-ratio result can be reproduced, but is not the same object as a corrected nights-level forecast against frozen naive. DATATUR rows are traveler counts, not monetary income; the BLS fallback uses the requested seasonally adjusted series.

## Prospective score sheet and unchanged leaders

[LANE2_LIVE_SCORE_SHEET.md](docs/revenue-forecast-strategy/05_backtests/LANE2_LIVE_SCORE_SHEET.md) and `lane2_validation_v1/close/live_format_1_1_rows.csv` list all 18 FORMAT 1.1 LIVE rows: A2 two, B2 four, F twelve. Nine scenario/quarter combinations each carry PIT and full_sample labels, vintage 2026-09-13. The sheet keeps scenario identities separate. A2 predicts the November guide; B2/F revenue outcomes are scored when the relevant actuals arrive.

No new eligible historical leader changed: A2's guide_mid has no baseline; B2 PIT revenue RMSE is 4.374× W1 and 4.283× W2 naive. Consequently no SCOREBOARD_v3.md is created. LIVE rows are unscored prospective scenarios.

## Memo-ready claims — complete file

> # Lane 2 memo-ready claims
>
> All three exact sentences below received SURVIVED from the vintage, power and mechanism refuters (3/3 each). These votes validate the qualified descriptions; the original research verdicts remain unchanged.
>
> **A2 — PARTIAL**
>
> > At letter-close vintages, the kernel agrees with the guide-gap sign in 7/8 W1 and 6/7 W2 cases with |S|>1pp, but the executable next-open 20-day return test does not establish a trading edge.
>
> W1: 11/14 evaluable, 7/8 high-signal hits, Wilson 95% 52.9–97.8%; W2: 9/10 evaluable, 6/7 hits, 48.7–97.4%. Mean aligned 20-day excess returns are −0.308/−0.983pp; both 90% intervals cross zero. W2 is nested in W1. Six joint-control observations have unknown consensus vendors, and guide-sign agreement uses the letter's own prints. A2 did not establish an executable expectations edge or independent causal mechanism. Evidence: `ALPHA_A2_GUIDE_SURPRISE_V2.md`, `A2_GATE_REVIEW.md` and `REFUTE_A2_mechanism.md`.
>
> **F — PARTIAL**
>
> > Our frozen-model estimate of excess unpaid share rose from 2.0pp in Q4 2025 to 9.7pp in Q2 2026, and an assumed 4pp incremental RNPL cancellation stress yields $3,185M of Q4 2026 revenue under the team nights path; these conditional estimates do not identify an RNPL causal effect.
>
> Exact endpoints: 1.969114/9.705899pp; conditional revenue $3,185.195735M. Historical forecast evaluation: W1 n=0, W2 n=0. The stock fit is retrospective. F replaces the rejected joint payment/migration solve with an explicit conditional stress; migration remains unidentified. The $29.580M haircut is gross: a 25% rebooking offset gives $3,192.591M, and full overlap with the baseline gives $3,214.776M. Evidence: `ALPHA_F_RNPL.md`, `REFUTE_F_vintage.md` and `REFUTE_F_mechanism.md`.
>
> **B2 — FAIL**
>
> > The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.
>
> W1: 11/14 paired, 5/9 hits, Wilson 95% 26.7–81.1%; W2: 9/10 paired, 4/7 hits, 25.0–84.2%. Aligned 20/60-day means are −0.443/−0.033pp and −0.983/−1.252pp. These small overlapping samples do not establish population accuracy below 70% or negative expected returns. Revision measurement begins before signal availability; the announced guide explains most of its association. Evidence: `ALPHA_B2_TERM_STRUCTURE_V2_RESULTS.md`, `REFUTE_B2_power.md` and `REFUTE_B2_mechanism.md`.
>
> **Refuted or partial interpretations — excluded**
>
> No exact headline was refuted. Stronger claims of an established A2/B2 trading or independent mechanism edge, measured RNPL causation, and reliable negative expected returns failed the attacks above. C2's corrected NTTO level-RMSE ratios are 1.0324× W1 (n=14) and 0.6771× W2 (n=10), with historical PIT admissions 0/14 and 0/10; it supplies covariates but no promoted forecasting edge (`C2_MACRO_PULLS.md`). M supplies dated current observations, not historical consensus vintages (`M_CONSENSUS_2026-09-13.md`).
>

## Remaining limitations

- No established A2/B2 executable expectations edge. A2's guide association uses same-letter information; six joint controls lack vendor provenance. B2 revision measurement starts pre-letter and mostly tracks the public guide; no immediate post-letter consensus anchor or adequate q+2/FY historical consensus is available.
- F does not identify RNPL's causal contribution, migration share, or incremental revenue loss. The retrospective fee-stock residual and gross cancellation scenario must retain their qualifications.
- C2 historical values are revised current captures, so publication dates alone confer no historical PIT status. FRED timed out; exact BLS data is a separate fallback. Direct CoStar returned 403; four official dated facts are a static fallback, not a working weekly refresh. JNTO uses a pinned edition. These parts remain explicitly incomplete.
- M did not obtain fresh Zacks, quarterly S&P, or verified nights/ADR/GBV/EBITDA observations. Older stamps remain intact; raw Yahoo EPS is not mislabelled adjusted EPS.
- No team investment decision, card adoption, scheduled fee-panel capture or policy-monitor access was performed. The separate Mac fee-panel check for 14 September 09:00 remains outside this run.

Checkpoints were pushed after Gate 1 (`a825542`), A2 (`1c0ce4a`), package integration (`cc79a40`), all packages (`dba7abe`) and all refuters (`cce5c6c`). Final publication uses `codex/lane2-full` against `main`.
