# Workstream 24: reproducibility, the next-print append path, and machine-detectable audit failures

*Overnight run, 6-7 Sep 2026. Repairs audit findings **A11**, **A13** and **A07** from
`C:/Users/krish/citadel-abnb/docs/2026-09-06_audit_findings_ai_handoff.md` (sections 13, 15, 9).
Builds on WS19's earlier edits to the same three scripts rather than reverting them.*

## Bottom line

Three things are now true that were not true this morning.

1. **The next print can actually be appended.** `16_merge_and_rerun.py` has a real
   `--append` path with schema validation, uniqueness on (quarter, metric, vendor), required
   actual/consensus/guide values, source-and-vintage enforcement, and a frozen pre-event forecast
   that a post-event refit cannot overwrite. Derived surprise and sign fields are recomputed from
   their primitives for **every** row on **every** run, not only when the cell happens to be blank.
   33 checks in `24_test_merge_rerun.py` pass.
2. **A passing exit status now means a passing audit.** `17_excel_audit.py` and
   `17_scenario_switch.py` return 0 / 1 / 2 (reconciles / material failure / missing input). Proved
   both ways with real Excel: a scratch copy of the workbook with one required output forced 2%
   wrong exits 1 and names the cell; the clean workbook exits 0. 7/7 cases in
   `data/processed/overnight/24_exit_code_tests.csv`.
3. **The build is documented and no longer reaches into a session scratchpad.**
   `docs/overnight/BUILD.md` is the authoritative entry point with an ordered build graph; the
   native Excel driver now lives in the repo as `analysis/src/overnight/17_recalc_dump.ps1`; five
   scripts that hard-coded `C:\Users\krish\...\scratchpad\NN` now default to `data/cache/NN`.

**And one correction that matters more than any of the above:** the committed
`16_reaction_tests.csv` was **stale relative to the panel it claims to describe**. See "Corrections
to existing work".

---

## A11 — the next-print rerun

### What was wrong (confirmed, then fixed)

WS19 had already moved execution behind `main()`, made the root project-relative, and widened the
recompute rule. Four things were still missing or broken:

| | |
|---|---|
| No append path that validates a new event | a new quarter was accepted with any columns at all; the `print_date` fallback branch raised `KeyError` on an additions table without a `print_date` column |
| Recompute was scoped to touched quarters only | a stale derived field elsewhere in the panel stayed stale |
| No suppression policy | a blanket recompute would have *filled* `eps_surprise_pct` for 2023Q3 and 2023Q4, which WS04 deliberately blanks (`eps_comparable = 0`: the GAAP EPS carries a one-off tax item the consensus was not on) |
| No frozen forecast | a post-print rerun would have overwritten the prospective 5 Nov card with a refit that had already seen the actual |

### What it does now

- `argparse` with `--root` (default: found relative to the script file), `--additions`, `--append`,
  `--prefix`, `--no-rerun`. Nothing executes on import.
- **Patch mode** (default) applies `16_consensus_additions.csv` and refuses an unseen quarter with
  an instruction to use `--append`.
- **Append mode** validates, in order: required columns (`print_quarter, column, new_value,
  source_url, confidence` plus `print_date, vendor, source_date` for an append); uniqueness on
  `(print_quarter, column, vendor)`; one record per target cell `(print_quarter, column)`; columns
  that exist in the panel; a non-blank `source_url` and `source_date` (the **vintage**) on every
  vendor-sourced row; exactly one genuinely new quarter; and the required primitives
  `print_date, actual_revenue_musd, cons_revenue_musd, next_q_guide_mid_musd`.
- **Policy: sourced primitives win, derived fields are always recomputed.** A derived value supplied
  by an additions table is kept but cross-checked against the recomputation and reported as a
  conflict if the two disagree. `eps_surprise_pct` stays blank when `eps_comparable = 0`.
- **Freeze before append.** `16_q3_2026_breakeven.csv`, `16_reaction_tests.csv` and
  `16_consensus_at_print_merged.csv` are copied to `16_frozen_pre_<quarter>_*.csv` before anything
  is written, and are never re-frozen over. The refit lands under `16_post_<quarter>_*`, so the
  prospective prediction and the post-event refit are two different files by construction.

### Tests — `analysis/src/overnight/24_test_merge_rerun.py`, 33/33 pass

Every test runs in a throwaway sandbox project root; nothing in `data/processed/overnight` is
touched. `py -3.13 analysis/src/overnight/24_test_merge_rerun.py` → exit 0.

| Group | Checks | Result |
|---|---|---|
| T1 append an unseen 2026Q3 | exits 0; writes its own file; 23 → 24 rows; **no prior primitive changes** (15 primitive columns × 23 quarters); the new surprise and guide-vs-street sign are computed from primitives | 7/7 |
| T2 revise an existing consensus | the 2026Q2 revenue surprise was **not** blank (0.782) and moves to -0.216 = (actual − new consensus)/|new consensus|; the recomputation is logged; a revised `next_q_cons_revenue_musd` flips `guide_vs_street_sign` +1 → −1 | 6/6 |
| T3 bad tables fail | duplicate (quarter, column, vendor); two vendors writing one cell; a new quarter on the patch path; `--append` on an existing quarter; missing consensus; missing guide; missing source URL; missing vintage; unknown column | 9/9 |
| T4 frozen forecast | the refit exits 0; the card and the tests are frozen; the frozen card **is** the pre-event card; neither shipped pre-event file is overwritten; the refit writes its own tests file and differs from the frozen one; the frozen panel lacks 2026Q3 while the refit panel has it; a second append leaves the frozen file byte-identical and says "kept existing" | 11/11 |

---

## Byte-identity of the WS16 outputs after the refactor

Re-ran `16_merge_and_rerun.py` in default mode against the committed inputs (WS19 had restored the
four WS16 outputs to their committed state before I started, so the "before" hashes below are the
committed ones).

| File | Committed md5 | After the refactor | |
|---|---|---|---|
| `16_consensus_at_print_merged.csv` | `35f74d26…` | `35f74d26…` | **byte-identical** |
| `16_reaction_panel.csv` | `b1219c45…` | `b1219c45…` | **byte-identical** |
| `16_q3_2026_breakeven.csv` | `4bd28492…` | `4bd28492…` | **byte-identical** |
| `16_reaction_tests.csv` | `e40432be…` | `b63a611e…` | **differs — see below** |
| `16_rerun_delta.csv` | `19eb907e…` | `aa5f8066…` | differs, downstream of the above |

### The diff is not caused by the refactor: the committed tests file was stale

`16_reaction_tests.csv` and `16_reaction_panel.csv` are written by the *same* execution of
`04_reaction_vs_consensus.py`. The panel is byte-identical, so the tests file cannot have come from
the same run as the shipped panel. Comparing every column except `perm_p_r2`:

- **Exactly three of 97 rows change substantively**, all of them `uni_eps_surprise_pct`
  (targets `excess_1d_pct`, `excess_5d_pct`, `excess_20d_pct`): **n 17 → 20, 17 → 20, 16 → 19.**
  20 is the number of non-null `eps_surprise_pct` values in the merged panel; **17** is the number
  in the *unmerged* `04_consensus_at_print.csv`. The committed tests file was produced before
  `16_consensus_additions.csv` gained the sourced FactSet EPS pairs for 2020Q4, 2021Q1 and 2021Q2
  (added at 10:37 on 6 Sep; they also flip `eps_comparable` 0 → 1 for those three prints).
- **The other 72 changed rows differ only in `perm_p_r2`** (median move 0.0033, max 0.268), and
  every point estimate, t-stat, R², LOO R² and n in them is bit-identical. Cause: `04` draws its
  5,000 permutations from a single module-level `np.random.default_rng(20260906)`, and
  `RNG.permutation(y)` consumes a different amount of entropy when `len(y)` changes, so one changed
  `n` early in the sequence shifts every later fit's permutation p-value.

**Decision: the regenerated file is kept.** It is the one consistent with the merged panel, the
additions table and the sources. The three affected specs all remain uninformative
(`uni_eps_surprise_pct` on `excess_1d_pct`: R² 0.0004, LOO R² −0.081, t −0.10), so no conclusion in
the WS16 note flips — but the numbers in that note's EPS rows are now off by the amounts above.

**Recommendation (not implemented, it would change more outputs):** seed the permutation test per
specification (`np.random.default_rng(hash(label))`) so that changing one fit cannot move the
p-value of an unrelated one. As it stands, any edit anywhere in the panel silently perturbs 70+
published p-values, which is a reproducibility hazard in its own right.

---

## A13 — machine-detectable audit failures

`17_excel_audit.py` and `17_scenario_switch.py` now have a documented exit contract:
**0** = passed, **1** = a material reconciliation / scenario failure, **2** = a required input is
missing. The informational static scan (343 raw pattern hits: 273 row-neighbour differences, 45 SUM
ranges, 25 in-formula constants) is printed and written to `17_auto_scan.csv` and **never** sets the
exit status — hundreds of pattern differences are not hundreds of defects.

**Tolerances (justified, both applied, either one passing counts as a match):**

- `REL_TOL = 1e-6` — scale-free, ~9 significant figures. The observed worst case across all 216
  named outputs is 4.2e-15, so this is ~9 orders of magnitude of headroom over Excel's own
  evaluation-order noise.
- `ABS_TOL = 1e-6` — a relative test is *undefined* on the Recon sheet's 216 delta cells, which are
  exactly 0 by construction. In the workbook's units 1e-6 is one US dollar on a $-million line,
  1e-4 basis points on a margin, and a hundredth of a cent per share. Section 2 (named outputs)
  previously had no absolute floor at all; it does now.

Full-precision comparison is preserved: the Python mirror is re-run in process rather than read
back from the 4-decimal `13_reconciliation.csv`, and that rounded value is carried alongside as a
separate column.

### Proof — `data/processed/overnight/24_exit_code_tests.csv`, 7/7

Produced by `analysis/src/overnight/24_exit_code_tests.py`, which runs each script as a separate
**process** (the exit status can only be demonstrated at the process boundary). Nothing under
`model/` or `data/processed/overnight/` is modified; the broken workbook lives in a temp directory.

| Case | Script | Expected | Got | Report |
|---|---|---|---|---|
| clean workbook reconciles | `17_excel_audit.py` | 0 | **0** | `PASS: 216/216 named outputs and 2349 formula cells reconcile` |
| a required output altered | `17_excel_audit.py` | 1 | **1** | `FAIL: 40 of 216 named outputs fail at 1e-06 relative / 1e-06 absolute` |
| the report names the altered cell | `17_excel_audit.py` | — | — | `Bear 4Q27 ADR ($)` is among the 40, with its 39 downstream dependants |
| missing Excel dump | `17_excel_audit.py` | 2 | **2** | `FAIL: required input missing: …` |
| clean scenario selector | `17_scenario_switch.py` | 0 | **0** | `PASS: 141 scenario comparisons, 0 mismatches` |
| inert selector (the original WS17 defect) | `17_scenario_switch.py` | 1 | **1** | `FAIL: 90 of 141 comparisons mismatch; selector moves 0 cells for ['Bear','Bull']` |
| missing scenario dumps | `17_scenario_switch.py` | 2 | **2** | `FAIL: missing Excel dump(s): …` |

The negative control is a real one: `Revenue!$H$26` (Bear 4Q27 ADR) was forced from 167.8898 to
171.2476 in a scratch copy of the workbook, and that copy was **recalculated by real Excel** through
`17_recalc_dump.ps1` before the audit read it. The 40 flagged outputs are the altered cell plus its
genuine dependants (Bear quarterly revenue and adj. EBITDA, 1Q27-4Q27, and the Bear annual chain) —
the report is precise, not a blanket failure.

---

## A07 — reproducibility

1. **`analysis/src/overnight/17_recalc_dump.ps1`** — the native Excel COM driver, moved out of the
   session scratchpad and made self-contained: every default path derives from `$PSScriptRoot`, the
   workbook is checked before Excel opens, Excel is quit and released in a `finally` block, and the
   exit status is 0 / 1 / 2. Verified: run with no arguments it reproduces the shipped base dump
   (5,547 cells, `calc_state_after=xlDone`, no circular reference). The Bear and Bull dumps
   (`17_dump_after_scen1.csv`, `17_dump_after_scen3.csv`) were regenerated with it **into the repo**,
   so `17_scenario_switch.py` now runs with no arguments; they previously existed only in a temp
   directory.
2. **`requirements.txt`** — de-duplicated (`requests` and `statsmodels` each appeared twice from a
   union merge) and completed against a grep of every import in `analysis/src/**/*.py`. Added
   `pytrends`, `pypdf`, `pysentiment2`; kept and commented `scipy`, `statsmodels`, `pyarrow`,
   `openpyxl`, `yfinance`, `duckdb`. Note the audit's dependency complaint is a **MAIN** problem:
   this tree already had scipy/statsmodels/pyarrow. Two non-pip prerequisites are documented rather
   than added: poppler's `pdftotext` and desktop Excel.
3. **`docs/overnight/BUILD.md`** — the authoritative entry point: what is current vs historical,
   the ordered build graph (availability check → normalized panels → feature tests → model →
   workbook → native Excel dump → reconciliation → next-print append → verification → notes), the
   exact commands, machine assumptions (junctions, `py -3.13`, Excel COM, `pdftotext`, the download
   cache), which inputs are external or licensed and how to obtain them, and which artifacts
   regenerate vs are frozen.
4. **Hard-coded absolute paths.** Replaced in `03_call_features.py`, `07_peer_benchmark.py`,
   `08_trends_pull.py`, `12_abnb_multiples_history.py`, `12_peer_multiples.py` (now
   `ABNB_SCRATCH`/`XBRL_CACHE`, defaulting to `<root>/data/cache/NN`, added to `.gitignore`),
   `04_reaction_vs_consensus.py` and `04_consensus_at_print.py` (now `ABNB_ROOT` or the path of the
   file itself; the latter's silent absolute fallback is now a loud failure), and
   `17_scenario_switch.py` (the default dump directory was one user's session scratchpad; it is now
   `<root>/data/processed/overnight`).
   **Still open, owned by other agents tonight:** `15_script_runs.py` (scratch dir plus absolute
   `OUT`/`SRC`) and `08_altdata_backtests.py` (scratch dir). `19_audit_triage.py` and
   `25_conventions_and_cleanup.py` mention absolute paths in prose only, which is fine.
5. **Superseded marker.** `research/notes/overnight/17_excel-audit.md` now carries a status banner
   under its title and a marker at the top of finding 3, pointing at WS18 / audit R01 and warning
   against re-applying the correction. The note's own text, its "(OPEN)" labels and its
   fixed-vs-open counts are left as written — it is a dated audit record.

---

## Corrections to existing work

1. **`data/processed/overnight/16_reaction_tests.csv` was stale** and internally inconsistent with
   the `16_consensus_at_print_merged.csv` committed beside it (n = 17 vs a panel with 20 usable EPS
   pairs). Regenerated. WS16's note quotes the old EPS rows; the three affected specs stay
   uninformative, so the conclusions hold, but the numbers should be refreshed.
2. **`04_reaction_vs_consensus.py`'s permutation p-values are order-dependent** across the whole
   test table (one shared RNG stream). 72 of 97 published `perm_p_r2` values move when any single
   fit's n changes. Not a defect in any one number; a reproducibility hazard for the file.
3. **`16_merge_and_rerun.py` had a latent `KeyError`** in the new-quarter branch WS19 added: it read
   `rows_q["print_date"]` on additions tables that need not have that column. Unreachable with the
   curated file, fatal on the first real use. Fixed.
4. **`04_consensus_at_print.py` silently fell back** to `C:\Users\krish\citadel-abnb-overnight` when
   its own relative root had no `data/` directory — i.e. on a clean checkout elsewhere it would have
   read another tree. Now a loud failure.

## For the model

Nothing in this workstream changes a model parameter. It changes what you may believe about a run:

| Name | Value | Unit | Source |
|---|---|---|---|
| Named workbook outputs reconciling Excel ↔ Python | 216 / 216 | count | `24_exit_code_tests.csv`, case 1 |
| Formula cells reconciling Excel ↔ evaluator | 2,349 / 2,349 | count | same |
| Reconciliation tolerance | 1e-6 relative **and** 1e-6 absolute | — | `17_excel_audit.py` |
| Worst observed Excel-vs-Python relative error | 4.2e-15 | — | WS17 note, unchanged |
| Scenario comparisons passing | 141 / 141 | count | `17_scenario_switch.csv` |
| Cells the selector moves (Bear / Bull) | 135 / 136 | cells | same |

## For the 5 Nov card

- The prospective card is `data/processed/overnight/16_q3_2026_breakeven.csv` (Street revenue bar
  $4,740m; guide midpoint $4,730m; the Street sits on the guide). **Do not re-run WS16 in default
  mode after the print** — use `--append`, which freezes that card as
  `16_frozen_pre_2026Q3_q3_2026_breakeven.csv` and writes the refit under `16_post_2026Q3_*`.
  Procedure and the required columns: `docs/overnight/BUILD.md` §6.
- Before quoting any workbook number on the card, run `17_excel_audit.py` and check the **exit
  status**, not the log. Same for `17_scenario_switch.py`. Regenerate the Excel dumps first if
  `13_excel_builder.py` has been re-run since — the dumps are snapshots of one workbook build and go
  stale silently.

## Files written

| Path | What |
|---|---|
| `analysis/src/overnight/16_merge_and_rerun.py` | rewritten: argparse, `--append`, validation, full derived recompute, frozen forecast |
| `analysis/src/overnight/24_test_merge_rerun.py` | 33 checks for the above |
| `analysis/src/overnight/24_exit_code_tests.py` | 7 process-level exit-status cases |
| `analysis/src/overnight/17_recalc_dump.ps1` | the native Excel COM driver, moved into the repo |
| `analysis/src/overnight/17_excel_audit.py` | argparse, `--root`/`--dump`/`--workbook`/`--out-dir`, absolute + relative tolerance, exit 0/1/2 |
| `analysis/src/overnight/17_scenario_switch.py` | argparse, repo-relative dump directory, exit 0/1/2 |
| `analysis/src/overnight/{03_call_features, 04_consensus_at_print, 04_reaction_vs_consensus, 07_peer_benchmark, 08_trends_pull, 12_abnb_multiples_history, 12_peer_multiples}.py` | absolute paths removed |
| `docs/overnight/BUILD.md` | the authoritative build document |
| `requirements.txt` | de-duplicated and completed |
| `.gitignore` | `data/cache/` |
| `data/processed/overnight/24_exit_code_tests.csv` | the exit-status evidence |
| `data/processed/overnight/{16_reaction_tests, 16_rerun_delta}.csv` | regenerated (see Corrections) |
| `data/processed/overnight/{17_dump_after_scen1, 17_dump_after_scen3}.csv` + metas | regenerated into the repo by the in-repo driver |
| `research/notes/overnight/17_excel-audit.md` | superseded-by-WS18 markers only |
