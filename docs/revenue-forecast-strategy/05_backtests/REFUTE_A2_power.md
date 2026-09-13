# A2 — power refutation

Agent refute_a2_power · 2026-09-13 · branch `codex/lane2-full` · approximately 10 minutes. All audit code, outputs and notes are new files.

## Verdict

**SURVIVED.** The exact proposed sentence survives this power audit: “At letter-close vintages, the kernel agrees with the guide-gap sign in 7/8 W1 and 6/7 W2 cases with |S|>1pp, but the executable next-open 20-day return test does not establish a trading edge.” The arithmetic reproduces independently from the registered PIT guide points and source returns. This is an accurate description of eight distinct observations and an inconclusive trading test. It does **not** establish a population hit rate of at least 70%, an independently replicated result, a confirmed mechanism, or the absence of economically useful returns.

## Pre-registered pass line

Recorded **2026-09-13T17:24:37Z**, before the audit calculation, in the new [pre-registration](REFUTE_A2_power_PREREG.md):

> Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.

The power reference design was fixed at one-sided alpha 5% and 80% power. The refuter pre-specified thresholds 0.5/1/1.5pp, both main windows, all three reported variants and horizons 1/5/20/60. The additional thresholds are audit stress tests, not retrospective evidence that the original package tried them. They cannot replace the original pass line. No forecast was created or registered, and neither scorer was run; the parent owns the shared workboard and scoring.

## What ran

From the repository root:

```text
.\.venv\Scripts\python.exe analysis/src/forecast_methods/refute_a2_power_v1/run.py
```

Exit **0**, shell wall time **2.772 seconds**, measured audit computation **0.238 seconds**. The script imports no A2 helper functions. It joins the `PIT`/`W1` rows of `registry/alpha-a2__guide_mid_next_q.csv` to A2's attributed consensus denominators, recomputes `S=100*(registered guide/consensus-1)`, derives actual signs using midpoint ±$0.5m, and joins the source `returns_v1/earnings_reactions_open_v1.csv` by event date. Assertions verify unique dates, source-return equality, reported counts, Wilson bounds and signed-return means. W2 is independently selected by quarter from that reconstructed event table.

Outputs: `data/processed/forecast_methods/refute_a2_power_v1/audit.json`, `primary_events_W1.csv`, `primary_events_W2.csv`, and `threshold_sensitivity.csv`. The JSON contains SHA-256 hashes for every input. The event tables retain vendor, timestamp and register IDs. No consensus dollar estimate is quoted in this note. Code and command documentation are in `analysis/src/forecast_methods/refute_a2_power_v1/`.

## Results — PIT default, |S|>1pp

| Independently recomputed statistic | W1 | W2 |
|---|---:|---:|
| Sign agreement | 7/8, 87.5% | 6/7, 85.7% |
| Wilson 95% interval | 52.91–97.76%, n=8 | 48.69–97.43%, n=7 |
| Exact fixed-label permutation p, one-sided | 0.071429, n=8 | 0.142857, n=7 |
| IID binomial p against 50%, one-sided | 0.035156, n=8 | 0.062500, n=7 |
| Direction-adjusted next-open 20-day mean | −0.307680pp, n=8 | −0.983347pp, n=7 |
| Signed-return sample standard deviation | 6.59195pp, n=8 | 6.81434pp, n=7 |
| IID Student-t 90% interval for the mean | −4.7232 to +4.1078pp, n=8 | −5.9882 to +4.0215pp, n=7 |
| IID normal mean effect required for 80% power, one-sided alpha 5% | +6.4480pp, n=8 | +7.2685pp, n=7 |
| IID normal power if true mean is +2pp | 19.27%, n=8 | 17.02%, n=7 |
| Leave-one-out signed mean range | −1.8718 to +1.3367pp; 8 deletions, remaining n=7 | −2.9208 to +0.8225pp; 7 deletions, remaining n=6 |

The exact label permutation enumerates all assignments with the observed number of positive guide gaps. It yields 5/70 and 5/35 extreme assignments. A2's Monte Carlo p-values of 0.0687 and 0.1428 are consistent with these exact probabilities; this is numerical refinement, not a material correction. The different binomial and permutation p-values use different null models and must not be substituted opportunistically.

The Student-t intervals and power calculations are explicitly **IID reference designs**, using the observed standard deviation and a normal model. They do not validate independence, correct event selection, or reproduce A2's circular-block bootstrap. A2's reported bootstrap 90% intervals also include zero. The reference MDEs come from solving the noncentral-t power equation, not adding an observed significance threshold to the package verdict. They indicate weak resolution; they are not calibrated forecasts of future return uncertainty.

| Exact binomial reference design, null hit rate 50%, one-sided alpha 5% | W1, n=8 | W2, n=7 |
|---|---:|---:|
| Rejection requires at least | 7 hits | 7 hits |
| Actual rejection probability under null | 3.516% | 0.781% |
| Power when the true hit rate is 70% | 25.530% | 8.235% |
| True hit rate needed for 80% power | 89.563% | 96.863% |
| Detectable improvement over 50% | +39.563pp | +46.863pp |
| Smallest possible p against a 70% null, even with every observation correct | 0.057648 | 0.082354 |

Thus even a perfect score in either actual sample would not reject a 70% null at one-sided 5% using the exact binomial test. The package's `n>=6` gate is an operational minimum, not evidence of adequate inferential power.

## Specification inventory and threshold attacks

The original A2 code/output contains **864 reported return cells**, of which **592 have n>0**: 3 variants × 3 windows (including the old extension) × 4 strategies × 2 subsets (all or |S|>1) × 3 sides × 4 horizons. These are overlapping report cells, **not 864 independent specifications or tests**. Restricting to pooled kernel returns in W1/W2 gives 48 cells, or 24 when restricted to |S|>1. The original threshold menu visible in the code is all versus >1pp; there is no evidence that the original run tried >0.5 or >1.5pp. Its outputs also contain 9 sign/gap summary rows, 45 control rows (5 control sets × 3 variants × 3 windows), and 19 ridge prediction rows. No count purports to recover unrecorded research history.

Default and ex-COVID signals are identical on all saved observations, so they are one realized signal path. The full-sample variant is a separate, retrospectively selected specification. W2 is nested in W1. The wide table must not be presented as a comparable number of independent confirmations, nor searched for one favorable horizon to override the pre-registered 20-day result.

The refuter generated **72 sensitivity return cells** (3 variants × 2 windows × 3 thresholds × 4 horizons); 48 use new 0.5/1.5pp cutoffs. The following are the 20-day results; ex-COVID duplicates default exactly:

| Variant | Cutoff | W1 sign hits; signed mean | W2 sign hits; signed mean |
|---|---:|---:|---:|
| PIT default | >0.5pp | 7/9; −0.443pp, n=9 | 6/7; −0.983pp, n=7 |
| PIT default | >1.0pp | 7/8; −0.308pp, n=8 | 6/7; −0.983pp, n=7 |
| PIT default | >1.5pp | 6/6; −0.214pp, n=6 | 5/5; −1.141pp, n=5 — underpowered |
| Full-sample specification sensitivity | >0.5pp | 8/11; −2.817pp, n=11 | 6/8; −1.480pp, n=8 |
| Full-sample specification sensitivity | >1.0pp | 7/10; −3.193pp, n=10 | 5/7; −1.827pp, n=7 |
| Full-sample specification sensitivity | >1.5pp | 6/9; −3.567pp, n=9 | 4/6; −2.160pp, n=6 |

Every listed signed-return mean is negative. Raising the default cutoff produces attractive perfect hit rates by removing observations, but W2 falls below the minimum sample. The retrospective variant fails a 70% sample hit-rate line at >1.5pp in both windows. These observations refute a broad claim of strong variant-invariant evidence; they do not refute the exact default-sample sentence.

## Explicit refutation attempts

1. **Claim: the headline really is 7/8 and 6/7. Attack:** rebuild the signal from registry PIT points, independently form interval-aware guide-gap signs, and source-match returns. **Survived.** Both counts and both return means reproduce. No ambiguous rounded sign occurs in this high-signal set. This audit does not re-estimate lambda; vintage refutation owns that question.

2. **Claim: those hit rates demonstrate at least 70% population accuracy or a “confirmed mechanism.” Attack:** recompute Wilson intervals and the exact binomial detection limits at the actual n. **Refuted as an inference.** Both intervals include rates below 70%; W2 includes 50%. Power at a true 70% hit rate is only 25.5%/8.2% in the reference design. The exact sentence survives because it reports observed agreement and does not assert population accuracy.

3. **Claim: both windows are independent confirmation. Attack:** intersect their reconstructed event IDs. **Refuted.** W2 contains seven of the eight W1 events; only 2023Q4 lies outside it. There are eight unique high-signal events, not fifteen. The package already discloses this nesting, and the exact sentence does not say otherwise.

4. **Claim: the negative return means establish that the edge is absent. Attack:** quantify detectable positive effects and test sensitivity to one-event deletion. **Refuted as an inference.** A +2pp true mean would be detected with only about 19%/17% power in the reference design. Deleting one event changes the mean's sign in 3/8 W1 deletions and 1/7 W2 deletions. The data cannot establish equivalence to zero or a stable negative strategy. The exact wording, “does not establish,” survives.

5. **Claim: the >1pp result is a unique confirmation immune to specification selection. Attack:** count the original horizons, subsets, variants and control sets; then run pre-specified threshold stresses. **Partially.** The exact original >1pp counts remain correct, and the original threshold was fixed before the package run. But the surrounding diagnostic family is large and dependent; higher-cutoff perfect scores and isolated horizon intervals cannot be promoted. A broad claim of robust inferential confirmation fails.

6. **Claim: a PIT variant check independently corroborates the mechanism. Attack:** compare saved default and ex-COVID signal vectors, then inspect the retrospective variant under identical cutoffs. **Partially.** Default and ex-COVID are numerically identical, not replication. The full-sample sensitivity gives weaker agreement and consistently negative mean returns. It cannot add independent PIT evidence or rescue the trade.

7. **Claim: the six-row control analysis supplies reliable incremental evidence. Attack:** count complete cases and residual degrees of freedom from the reported joint control. **Refuted as an inference.** W1 and W2 use the same six rows; partial correlation with two controls has only `n−k−2=2` residual degrees of freedom for its usual correlation test. The package additionally reports unresolved named-vendor provenance for all six GBV controls. Its numerical preservation of an already negative correlation sign does not identify a favorable expected-return effect. This is consistent with the exact sentence's restraint.

## What failed or could not be done

The attempt to disprove the headline arithmetic failed. The audit found no new numerical error requiring a package correction, no local script failure, and no need to rerun frozen tests or scorers. Stronger interpretations of the hit rates, window replication, control evidence and absence of returns failed the attacks above. Total researcher degrees of freedom before A2 cannot be determined from these artifacts; the inventory is limited to the visible package. Valid empirical power under time-varying, dependent event returns is not identifiable from eight selected events. No fees, transaction costs or alternative hedge model were estimated.

Parameter count: this audit fits no forecasting parameters. It estimates each selected sample's mean and standard deviation for descriptive calculations; the MDE holds that observed standard deviation fixed as a design input. Wilson intervals and exact permutations require no fitted nuisance parameters. The alpha, target power, cutoffs and horizons were fixed in the refuter pre-registration.

## Interpretation

Retain the exact proposed sentence. In accompanying discussion, replace “mechanism confirmed” with “observed sign association in eight distinct events.” Label W2 as nested and keep the wide intervals visible. A larger sample of independently available vintages is required to distinguish a modest useful effect from zero; expanding a diagnostic menu cannot supply that information.

## RESUME

Parent can count this power-lens vote as **SURVIVED** for the exact proposed sentence and link this note in the shared workboard and Gate-2 decision. Combine it with the separate vintage and mechanism refutations; this audit neither substitutes for those checks nor changes A2's package-level PARTIAL verdict. Preserve the 8/7 denominators, eight-event nesting, negative next-open means and distinction between failure to establish an edge and proof of no edge. Audit code and source-hashed outputs are complete in the new `refute_a2_power_v1` folders; no new registration, source acquisition or human decision is needed from this refuter.
