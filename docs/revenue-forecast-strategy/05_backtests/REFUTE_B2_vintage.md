# REFUTE B2 vintage — dated reconstruction of the failed signal

Codex B2 vintage refuter · 13 September 2026 · `codex/lane2-full` · approximately 12 minutes. New code and outputs: `refute_b2_vintage_v1/` only.

## Verdict

**SURVIVED.** The exact sentence is numerically correct under the repository's point-in-time convention. An independent reconstruction gives **5/9 = 55.6% in W1 and 4/7 = 57.1% in W2**, below 70%, and negative mean signal-aligned executable excess returns at both horizons in both windows. No future information is needed. Two attacks do identify limitations: the selector accepts a synthetic explicitly post-close consensus stamp, and the revision interval begins before the signal exists. Neither changes the actual historical rows or the narrow descriptive sentence. This is not a PASS for B2's underlying research hypothesis.

Exact sentence assessed:

> The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.

## Pre-registered pass line

Recorded before the audit run in [REFUTE_B2_vintage_PREREG.md](REFUTE_B2_vintage_PREREG.md), timestamp `2026-09-13T17:42:00Z`:

“Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.”

The exact sentence must reproduce without inadmissible consensus or future kernel inputs. The original B2 gate remains |S1| > 0.5%, sign accuracy ≥70%, at least six strong cells, and correlation >0.4 in BOTH windows. Counterfactual leak scenarios below are audit attacks, not new candidate models or alternative pass lines.

## What ran

From the repository root:

```text
.venv\Scripts\python.exe analysis/src/forecast_methods/refute_b2_vintage_v1/run.py
```

Exit 0; analytical elapsed time 2.863 seconds, shell wall time 3.713 seconds. The first run passed all reconstruction assertions. Pandas emitted a performance warning about dataframe fragmentation; it did not alter values or fail execution. No frozen tests, registrations or scorer runs were performed. No original package or input file was edited.

Outputs and execution receipt are under `data/processed/forecast_methods/refute_b2_vintage_v1/run_20260913T174436_543988Z/`: `cells.csv`, `consensus_audit.csv`, `kernel_audit.csv`, `summary.csv`, `input_hashes.csv`, `registry_audit.csv`, `diagnostics.json`, and `receipt.json`.

The reconstruction does not call B2's signal or statistics functions. It selects historical consensus independently, supplies an independently date-truncated KPI panel to the imported `kernel_engine_v2.pit_lambda`, constructs the trailing-eight median actual/guide ratio directly from the cushion CSV, and joins return components separately. The engine remains the authoritative lambda implementation, as required; this audit is independent of B2's wrapper, not an independent rewrite of lambda estimation. B2's selector is imported only for the synthetic robustness attack.

## Results

All rows below are PIT, weight 2/3, with the fixed strong-signal threshold |S1| > 0.5%. Revisions equal `100 × (next-print consensus / pre-guide consensus − 1)`. Returns are `sign(S1) × (ABNB next-open return − QQQ next-open return)`, in percentage points, before costs.

| Window | Origins n | Paired n | Strong n | Hits | Hit rate | Correlation | Mean aligned 20d, pp | Mean aligned 60d, pp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| W1 | 14 | 11 | 9 | 5 | 55.556% | 0.687245 | −0.442539 | −0.032975 |
| W2 | 10 | 9 | 7 | 4 | 57.143% | 0.670530 | −0.983347 | −1.252455 |

W1's 60-day mean is particularly close to zero; the claim is its observed sign, not a reliably negative expectation. W2 is a subset of W1 and is not independent confirmation.

### Historical consensus row audit

Each table row represents one guided quarter (n=1); the source register has 28 PG/AP candidates, of which 27 are admissible and one PG row is quarantined. Each accepted row has `pit_usable=True`, `vendor_attributed=True`, the required role, and a date-only timestamp that `CONVENTION.md` explicitly treats as morning-of-print. PG and AP IDs are respectively `PG-<quarter>-revenue` and `AP-<quarter>-revenue`. Every value is USD millions. The source values, flags, register IDs, timestamps and source paths are retained in `consensus_audit.csv`.

| Guided quarter | PG value | PG vendor | PG timestamp | AP value | AP vendor | AP timestamp |
|---|---:|---|---|---:|---|---|
| 2023Q1 | 1,690 | Refinitiv | 2023-02-14 | 1,790 | Refinitiv | 2023-05-09 |
| 2023Q2 | 2,420 | Refinitiv | 2023-05-09 | 2,420 | Refinitiv | 2023-08-03 |
| 2023Q3 | 3,220 | Refinitiv | 2023-08-03 | 3,370 | LSEG | 2023-11-01 |
| 2023Q4 | 2,180 | LSEG | 2023-11-01 | 2,170 | LSEG | 2024-02-13 |
| 2024Q1 | 2,030 | LSEG | 2024-02-13 | 2,060 | LSEG | 2024-05-08 |
| 2024Q2 | 2,740 | LSEG | 2024-05-08 | 2,740 | LSEG | 2024-08-06 |
| 2024Q3 | Excluded | LSEG | Missing; PIT=False | 3,720 | LSEG | 2024-11-07 |
| 2024Q4 | 2,420 | LSEG | 2024-11-07 | 2,420 | LSEG | 2025-02-13 |
| 2025Q1 | 2,300 | LSEG | 2025-02-13 | 2,260 | LSEG | 2025-05-01 |
| 2025Q2 | 3,040 | LSEG | 2025-05-01 | 3,040 | LSEG | 2025-08-06 |
| 2025Q3 | 4,050 | LSEG | 2025-08-06 | 4,080 | LSEG | 2025-11-06 |
| 2025Q4 | 2,670 | LSEG | 2025-11-06 | 2,720 | LSEG | 2026-02-12 |
| 2026Q1 | 2,530 | LSEG | 2026-02-12 | 2,620 | LSEG | 2026-05-07 |
| 2026Q2 | 3,460 | LSEG | 2026-05-07 | 3,580 | LSEG | 2026-08-06 |

### Explicit refutation attempts

1. **Claim: historical consensus is PIT. Attack: substitute a current row, a guide, an unattributed observation, or a later timestamp. SURVIVED.** All 27 admitted endpoint candidates are revenue PG/AP rows with the required flags and same-day morning convention; zero are `current`, zero are post-close stamps, and no actual guide is used as consensus. The 2024Q3 PG row remains excluded despite its numeric source value. On the actual paired sample, 11 W1 and 9 W2 revisions reproduce exactly, maximum difference 0.000000pp.

2. **Claim: the denominator is 9/7 strong cases. Attack: restore unavailable seasonal lambdas or count zero revisions as correct. SURVIVED.** The default seasonal kernel is unavailable for 2023Q1 and 2023Q3; quarantined PG-2024Q3 creates the third missing W1 pair. W2 loses only that quarantine. The paired samples contain four unchanged revisions in W1 and three in W2. A nonzero signal does not hit a zero revision. The fixed threshold yields nine and seven strong cases; hits are five and four. No imputed missing consensus or retroactive seasonal estimate is necessary.

3. **Claim: lambda and cushion use only prints ≤ d. Attack: truncate source inputs independently before rebuilding. SURVIVED.** Twelve available q+1 guides reproduce to a maximum absolute difference of **9.095×10⁻¹³ USD million**; the maximum signal difference is **2.220×10⁻¹⁴pp**. All 12 use `ex_covid`; lambda sample n ranges from one to four same-season observations. Both variant selection and coefficient estimation see only the truncated panel. Cushion sample n is six at the first available guide and eight thereafter, with its last realised quarter printed exactly on d. Each used GBV lag is also printed by d. Training-quarter and cushion-quarter lists and their latest publication dates are recorded for every guide in `kernel_audit.csv`. Same-day data are admissible here; the engine receives d+1 as prescribed.

4. **Claim: future information is not needed. Attack: force next-letter coefficients and next-quarter GBV into the calculation. SURVIVED.** The lawful reconstruction already matches. The illegal variants below change results and sometimes coverage. `Next lambda` refits the target season at the next letter while holding original GBV and cushion; `Next GBV` shifts the entire two-lag GBV base forward one quarter, using the unprinted target quarter's realised GBV, while retaining the lawful lambda/cushion; `Combined` does both and also uses the next-letter cushion. These are transparent deliberate leaks, not the published full-sample replay.

| Window | Counterfactual | Paired n | Strong n | Hits | Correlation |
|---|---|---:|---:|---:|---:|
| W1 | Next lambda | 13 | 11 | 7 | 0.858592 |
| W2 | Next lambda | 9 | 8 | 4 | 0.863535 |
| W1 | Next GBV | 11 | 11 | 4 | 0.282376 |
| W2 | Next GBV | 9 | 9 | 3 | 0.199497 |
| W1 | Combined | 13 | 13 | 5 | 0.396060 |
| W2 | Combined | 9 | 9 | 3 | 0.231762 |

5. **Claim: average aligned returns are negative and executable. Attack: replace next-open returns with the gap or a mismatched event/window. SURVIVED.** For all 14 historical origins and both horizons (28 comparisons), the separate ABNB-minus-QQQ open-return components reproduce B2's `excess_open_*` fields. Every entry date is after the letter. There are nine W1 and seven W2 strong signals with both horizons observed. Reversing returns only for a negative signal produces the four negative means above. No gap or close-to-close return enters this audit. Underlying OHLC accuracy is inherited from `returns_v1`; this task does not repeat that package's price-download audit.

6. **Claim: the historical evidence is free from intraday consensus leakage. Attack: provide a synthetic `pre_guide` row stamped 17:00 New York time on a letter day. PARTIALLY.** B2's selector accepts it because its cutoff is the end of the UTC calendar day and `exact_day=True` compares the normalized UTC date. An explicit post-close row is not morning consensus and should be rejected. The diagnostic uses one synthetic observation and changes no input. **None of the 27 actual admitted historical observations has such a timestamp**, so no correction to the current fractions or means follows. A new version should preserve the convention for date-only PG/AP rows while enforcing the local pre-close boundary for explicit intraday stamps.

7. **Claim: the result describes next-quarter consensus revisions. Attack: ask whether the entire outcome lies after the executable signal. PARTIALLY.** All 11/9 revision pairs begin at pre-letter consensus, while S1 uses same-letter GBV and is only available after the letter. The outcome therefore combines the reaction to the already issued guide with later consensus movement. This refutes a stronger interpretation that B2 predicts exclusively post-entry consensus drift. It does not refute the proposed sentence, which reports the failed descriptive hit rate and negative returns without claiming a trading edge. A future test needs an attributed post-letter consensus anchor to isolate subsequent revisions.

8. **Claim: the result can be reconstructed from recorded inputs and correctly dated registry rows. Attack: compare source hashes and calendar-relative horizons. PARTIALLY.** All eight inputs listed in B2's original manifest still match their recorded SHA-256 hashes. All 22 historical PIT registry rows satisfy `knowable_from ≤ vintage_date`, and the horizon equals target-quarter ordinal minus vintage-calendar-quarter ordinal. The full B2 registry has 49 rows. However, the original manifest omits the two CSVs read transitively by the kernel: `02_kpi_panel_quarterly.csv` and `02_guidance_cushion_series.csv`. This audit records their current hashes and reproduces the published cells, but cannot recover an absent original hash. A new production manifest should include these dependencies. The omission is a provenance weakness, not evidence that a future observation entered the reconstruction.

## What failed or could not be done, and why

The synthetic post-close selector challenge succeeded in exposing a robustness gap; no source file was patched because the refuter is read-only outside its new files. The revision target does not isolate exclusively post-entry changes. Exact original hashes for the two transitive kernel inputs were never recorded in B2's manifest. The audit can establish consistency with the current dated panel and the repository's morning-of-print convention; it does not independently prove the source vendor's original intraday collection time. No unsupported archival or licensed-data claim is made.

No new estimated parameter was introduced. The audit uses the imported seasonal coefficient and observed median cushion, the fixed 2/3 weight and fixed 0.5% threshold. The leaky scenarios are explicit substitutions with no fit or tuning by this refuter.

## Interpretation

Keep the exact sentence as a failed historical result. Its timing qualifier should remain the repository's post-letter PIT convention, and the broader B2 discussion should continue to disclose that revision measurement begins pre-letter. The four return means are arithmetic observations from nine/seven strong cases, not estimates with established negative expected return. The selector and manifest limitations should be repaired in a separate version before expanding the study to explicit timestamped vintages; neither justifies changing the existing numerical sentence.

## RESUME

Parent: record **SURVIVED** for the exact B2 sentence under the vintage lens and link this note in the shared workboard/refuter tally. Preserve the original B2 result, this preregistration, and this audit's run folder. No registry changed, so this refutation requires no scorer rerun. If B2 is extended, add a separately versioned intraday timestamp guard, hash the kernel's transitive input CSVs, and obtain a post-letter consensus anchor before describing the outcome as post-entry drift. Do not treat this verdict as a PASS of B2's research gate or resolve any team investment decision from it.
