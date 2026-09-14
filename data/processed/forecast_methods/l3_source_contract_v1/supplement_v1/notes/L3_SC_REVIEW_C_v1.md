# SC-C — independent consumption review, initial findings

Reviewer: cohort_fx (SC-B). Author: nclh (SC-C). Date: 2026-09-14. Read-only review of code/evidence and `consumption/results_v1`; only this new review note is written. No SC-C or L4 code edit. Closure pending the bounded repairs below.

## Verified evidence and preservation

Independently read all 1,187 original L3 rows and the output as CSV strings: every one of the **33,236 original cells** matches, including blank values, precision lexemes, source dates and the original 28-column scope. Counts reproduce: 576 conditional scenario exhibits, 603 descriptive diagnostics, four comparator-only rows, four unavailable rows, zero observed-input rows and zero rejected rows. All direct L4 applications remain blocked. The four blanks remain blank, including both fee theta estimates. Valid negative research is retained as evidence rather than discarded.

Joined all **1,080 FX rows** against final SC-B accounting contracts by quarter/scenario/metric. Every classification agrees: 540 conditional T/T-B/T-over-B alternatives and 540 R0/B/reference-factor diagnostics. No source row was promoted or combined. The 36 conditional ADR rows are additional to the FX rows; descriptive components and identities are not standalone additions.

Independently executed `git show` and `git rev-parse` for **nine selected L4 paths** at pinned commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`: all SHA-256 hashes and Git blob IDs match the frozen snapshot. The four exact helper functions and contract source reproduce the committed interface. Separately re-read **16 current local inventory file instances** and their baseline Git blobs: all recorded source hashes and CRLF-normalized equality checks match; twelve byte differences are newline-only. The four directory scopes and filename-only supplemental search are explicitly bounded; no global absence of fee captures or public disclosures is inferred. The snapshot time is preserved and no collector ran.

The pinned L4 contract requires JSON revenue-adapter rows and a different manifest schema from this research CSV bundle. All original rows fail its required-field gate, and the original bundle fails the required commit field. L4's positive-hedge fixture gives (100-10)*1.05+10=104.5. It refuses missing H, wrong baseline, nonconserved allocations and a second application. The snapshot faithfully documents the remaining upstream gaps: no root quote metadata enforcement and no proof that hashed payloads belong to the supplied commit. These are existing L4 responsibilities, not repairs to L4 performed here.

The guide comparison preserves a revenue consensus of 3161.02149 USDm, conditional revenue 3179.3436542864 USDm and guide 3123.41911517339 USDm. The positive revenue/revenue difference and negative guide/revenue difference describe distinct objects. No observed guide expectation is manufactured.

Independent focused suite: **18 passed in 1.31 seconds, exit 0**. The suite's two fresh outputs are byte-identical and reuse is refused. No empirical backtest or model refit was run.

## Findings sent to author and lead

**F1 — direct classifier accepts invalid dates (moderate, current immutable output protected).** In memory, mutate only first-row `information_date` to `2027-01-01`, or `source_information_date` to `nonsense`, and call `classify_all(fields, rows)`: both are accepted. The canonical runner's bound input hash prevents silently editing its on-disk input, so these are callable-validator holes rather than corruption of the current output. Require explicit ISO dates and no date beyond classification cutoff, with consistent source and row vintages; add regression tests.

**F2 — direct classifier accepts metric-unit changes (moderate, current immutable output protected).** Changing the first FX row's `units` from USD to `USD_millions` is accepted. The resulting definition and copied unit then disagree by a factor of one million. Add metric-specific unit validation, retaining all original valid lexemes and values.

**F3 — make hedge ratio compatibility explicit (wording/contract clarification).** The pinned L4 arithmetic can preserve a supplied reconciled H, but the original aggregate inherited-lambda T/B is not thereby a certified operating-only ratio. Gap text and findings should require that separately reconciled ratio and H, explicitly disallowing automatic relabeling. With H unidentified, SC-B permits only unresolved aggregate exhibits and makes no hedge-neutrality claim.

**F4 — ADR growth terminology (minor).** The ex-FX ADR YoY definition currently calls the level a percentage-point presentation. Define it as a growth rate in percent; percentage points describe differences between growth rates. Preserve the original unit field as a legacy lexeme rather than changing source values.

The author accepted all four findings and plans a new immutable `results_v2`, with old v1 preserved. Counts and source values must remain unchanged. These findings do not alter the accepted L3 descriptive calibration or its free-weight promotion FAIL, and cannot promote any input to production.

## Reproduction and reviewed identities

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q -p no:cacheprovider
```

The independent source/preservation/attack command read the CSV using `csv.DictReader`, used `subprocess.check_output(['git','show',commit+':'+path])` and `git rev-parse` with the isolated root as cwd, and compared raw SHA-256 plus CRLF-to-LF normalized content. Each attack deep-copied the original list, changed exactly one first-row field and called the actual classifier; all three malformed inputs were accepted before repair. The command exited 0 and reported all counts above. The tests are failure demonstrations, not sourced financial evidence.

| Reviewed artifact | SHA-256 |
|---|---|
| consumption/run.py, before repairs | `7c684e2859337ec847d67e8d8bbe81743a492157e7f50e2ea1ab8372eaeb616f` |
| consumption/test_consumption.py, before repairs | `75e0d58305ea04ff289435dd6f0a06f22aac30b0c8de76a7282cc26bd32f6a74` |
| results_v1/manifest.json | `94129f3130120478e9ae3f541a9f39f2e00f0714d9267e1d832f3c397011da36` |

## RESUME

Author repairs only its new package and rebuilds into a new output. Reviewer then re-executes the exact malformed-input attacks, checks corrected unit/hedge wording, confirms all original cells and status counts, verifies byte reproduction and binds final code/input/output hashes in a new closure note. Lead independently integrates all three packages after those reviews; no direct L4 or investment adoption follows.
