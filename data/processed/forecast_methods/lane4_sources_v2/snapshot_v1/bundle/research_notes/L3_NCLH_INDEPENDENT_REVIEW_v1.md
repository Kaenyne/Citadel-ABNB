# L3 NCLH — independent review v1

Reviewer cohort_fx (not NCLH author) · 2026-09-13 · codex/lane3-full.
Reviewed `nclh_transfer_v1` code, preregistration, `inputs_v3` and `results_v3`.

## Verdict

**Research FAIL independently reproduced; implementation repair required before final acceptance.** The implementation correctly excludes target-quarter deposits and future outcomes from the tested prediction vintage, preserves the issuer-specific ticket/total targets, and fails both original numerical hurdles. Five malformed-input validation holes were reproduced. They do not change the checked canonical data's numerical negative finding, but could admit bad future inputs. The findings were sent to author and lead; this v1 preserves them before repair.

## Scope and evidence

Read `docs/thesis-kernel-topdown/prompts/WP-E1_nclh_kernel.md`, `L3_NCLH_PREREG_v1.md`, `run.py`, `fetch.py`, `test_nclh.py`, original source manifests, core observation rows, fold coefficients, predictions, scores and stability. The user explicitly corrected the old k=0..3 prompt to known k=1..3; the code honors that correction. Its 66-point simplex, four seasonal means, minimum sample, COVID exclusions and pre-2023 frozen stability weights match the preregistration. The original prompt's unspecified naive is explicitly seasonal naive in the saved preregistration; changing to the harder most-recent-growth benchmark does not rescue the result.

All 47 source bytes in the temporary public cache match the manifest (46 quarter-specific issuer releases plus the index). Independent table-header inspection covered 16 core financial cells across 2015Q1, 2021Q1, 2025Q4 and 2026Q2. The current-quarter columns precede comparison and annual columns in these sources, and the deposited balance is the **current** ATS line. Q4 2025 total $2,244.400M was selected rather than FY $9,827.592M; Q1 2021 passenger revenue $0.166M was retained rather than a large comparison-period value. Primary release examples: [Q4/FY2025](https://www.nclhltd.com/investors/news-events/press-releases/detail/768/norwegian-cruise-line-holdings-reports-fourth-quarter-and), [Q2 2026](https://www.nclhltd.com/investors/news-events/press-releases/detail/812/norwegian-cruise-line-holdings-reports-second-quarter-2026).

These are original-period columns on quarter-specific issuer pages **retrieved in 2026**. Their current posted publication dates are supported; absence of subsequent website revision is not proved by contemporaneous archived bytes. No evidence of a changed historical value was found in this review. No current comparative columns were used to replace earlier quarter values.

## Independent numerical checks

Loaded canonical input, called `evaluate`, and independently divided paired-fold RMSEs from its predictions. No output files or other package code were changed.

| Target | Window | n | Kernel / seasonal-naive RMSE | Kernel / recent-growth-naive RMSE | Verdict |
|---|---|---:|---:|---:|---|
| Passenger ticket revenue | W1 | 14 | 1.376459 | 1.324196 | FAIL (<0.6 required) |
| Passenger ticket revenue | W2 | 10 | 3.840746 | 4.689324 | FAIL |
| Total revenue | W1 | 14 | 1.199835 | 1.166046 | FAIL |
| Total revenue | W2 | 10 | 3.462821 | 4.335703 | FAIL |

Passenger-revenue seasonal lambda ranges are 2.3601/2.3985/2.0061/3.1867pp, each n=3; every season fails the <0.5pp hurdle. All total-revenue ranges also fail. These are descriptive realized ranges on pre-2023-fitted weights, not out-of-sample parameter estimates or cross-issuer valuation adjustments.

At target 2024Q2, replacing ATS and passenger revenue for that quarter and every future quarter with 1e15 leaves both its feature vector and its entire training frame exactly unchanged (n=2 perturbation checks). The vector uses ATS q−1, q−2, q−3, with q−1's release timestamp as origin. No target-quarter deposit leakage was found on canonical inputs.

Guide+cushion and Street comparisons have n=0 and remain unavailable rather than failing numerically. Net yield, EPS, EBITDA and cost guides are not compared against GAAP ticket/total revenue. The availability inventory is not evidence that all historical public revenue-guidance quotations were exhaustively searched. ATS remains an overlapping deposit stock, so fitted lag weights are not measured voyage recognition probabilities. The negative result is specific to the preregistered stock specification, not a proof that no cruise revenue model could work.

## Reproduced implementation findings

Each attack used a temporary copy of `inputs_v3/observations.csv`, called `load_panel(temp_directory)` and deleted only the temporary directory using Python's context manager. No real data or outputs were mutated.

| ID | Priority | Mutation | Observed initial result | Required fix |
|---|---|---|---|---|
| N-01 | P1 | Set every 2026Q2 `published_at` to `2026-09-14T00:00:00Z` | Accepted | Use exclusive end-of-day upper bound; next day itself is future |
| N-02 | P1 | Set only 2024Q2 ATS `published_at` blank | Accepted; group max/nunique hides NaT | Validate every row's timestamp before aggregation |
| N-03 | P2 | Set both 2024Q2 passenger and total revenue to +inf | Accepted; infinity identity passes allclose | Require finite positive/appropriate core values |
| N-04 | P2 | First source SHA set to 64 copies of `z` | Accepted | Validate 64 hexadecimal characters and manifest correspondence |
| N-05 | P2 | First source reference set to three spaces | Accepted | Strip and reject blank provenance |

N-01 was also flagged by lead before this independent test. N-02 is particularly relevant to ATS: a missing observation-level clock must not inherit the target quarter's other rows' valid publication clock. N-03 does not contaminate today's valid values, but violates the promised malformed-input failure behavior.

## Exact reproduction

From the isolated repository root, invoke the project interpreter with `-X utf8`; set `sys.path.insert(0, 'analysis/src/forecast_methods/nclh_transfer_v1')`, then `import run`. The relevant deterministic operations are:

```python
import tempfile
from pathlib import Path
import pandas as pd
obs = pd.read_csv(run.INPUT / 'observations.csv')
bad = obs.copy()
bad.loc[bad.quarter.eq('2026Q2'), 'published_at'] = '2026-09-14T00:00:00Z'
with tempfile.TemporaryDirectory(prefix='l3_nclh_independent_') as tmp:
    bad.to_csv(Path(tmp) / 'observations.csv', index=False)
    run.load_panel(Path(tmp))  # v1 incorrectly accepted; repaired version must raise
panel = run.load_panel()
predictions, coefficients, exclusions = run.evaluate(panel)
```

The same pattern applies N-02 through N-05 with the mutations specified in the table. The audit command returned exit 0 in 7.07 tool-wall seconds, printed all five `ACCEPTED_INVALID_INPUT` results and the independently computed ratios. The separate cache-hash/table-header command returned exit 0 in 3.56 tool-wall seconds, verifying 47/47 source hashes. These scripts produce no research registrations.

## RESUME

NCLH author should reject all five malformed-input attacks, add regression tests, preserve the current result snapshots, and rebuild into a new canonical result directory. A second independent review note must record repaired code/source hashes, rerun the attacks and show that valid-input forecasts and stability remain unchanged. Lead should not mark final implementation accepted based solely on this initial review; the substantive research FAIL may be retained now with its exact scope and data-vintage limitation.
