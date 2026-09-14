# B2 — Power refuter

Codex `refute_b2_power` · 13 September 2026 · parent branch `codex/lane2-full` · approximately 12 minutes · all audit files new.

## Verdict

**SURVIVED.** The exact sentence is an accurate description of the fixed test's observed counts and means. It survives eight refutation attempts below. The strongest attack succeeds against a stronger interpretation: these data do **not** establish that population accuracy is below 70%, or that expected executable returns are negative. B2's research gate remains **FAIL**; the refuter's verdict concerns the sentence's fidelity to that result.

Sentence reviewed: “The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.”

## Pre-registered pass line

“Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.”

Written before numerical execution at **2026-09-13 17:42:26 UTC** in [the new refuter preregistration](REFUTE_B2_power_PREREG.md). This audit was necessarily informed by B2's published results. Its diagnostic grid is post-hoc relative to B2 and cannot replace B2's original gate. The original [B2 preregistration](ALPHA_B2_TERM_STRUCTURE_V2.md) requires, in both windows, at least six strong observations, at least 70% sign accuracy at |S1| > 0.5%, and correlation above 0.4. Return results are reported, not gating.

## What ran

From the repository root:

```text
.venv\Scripts\python.exe analysis/src/forecast_methods/refute_b2_power_v1/run.py
```

Exit **0**; command wall time **2.624 seconds**, numerical audit **0.623 seconds**. The wrapper preserved stdout in `data/processed/forecast_methods/refute_b2_power_v1/receipt_20260913T1345042959.txt`. The receipt filename uses local time; the run folder uses UTC. No execution failed and no frozen tests or scorers were run.

The [independent audit script](../../../analysis/src/forecast_methods/refute_b2_power_v1/run.py) imports no B2 statistical functions. It rebuilds S1 and the revision from B2's component levels, checks copied returns against the source `returns_v1/earnings_reactions_open_v1.csv`, then replaces copied returns with source observations. Assertions verify the ratios, exact headline counts, all four negative means and window nesting. Its source is B2's metadata-corrected `run_20260913T171654_499731Z/`; it leaves B2, its registry and protected files untouched. Output tables and input SHA-256 hashes are in `data/processed/forecast_methods/refute_b2_power_v1/run_20260913T174504_089575Z/`.

The original specification inventory also used read-only `rg` and `Get-Content` inspection of B2's `run.py` and its named kernel input, `kernel_engine_v2/engine.py`, and row counts from B2's four output tables. This is a power audit; it does not independently recapture vendor vintages or rerun the kernel.

## Results

| PIT window | Origins n | Revision pairs n | Strong n | Correct / strong n | Independent 95% Wilson interval | Correlation, pair n | Lower-tail probability under p=70% |
|---|---:|---:|---:|---:|---:|---:|---:|
| W1 | 14 | 11 | 9 | 5/9 = 55.6% | 26.7–81.1% | 0.687, n=11 | 0.270 |
| W2 | 10 | 9 | 7 | 4/7 = 57.1% | 25.0–84.2% | 0.671, n=9 | 0.353 |

The binomial probabilities are illustrative independent-Bernoulli calculations. Even on that assumption the observed accuracy is insufficient to reject p=70% on the lower side. Both Wilson intervals contain 50% and 70%. Passing the package's minimum n=6 rule does not confer adequate statistical power.

| PIT window / horizon | Strong n | Mean aligned excess, pp | Illustrative 95% t interval, pp | 80%-power mean MDE, pp | Positive leave-one-event-out means / omissions n |
|---|---:|---:|---:|---:|---:|
| W1 / 20 days | 9 | −0.4425 | −5.192 to +4.307 | 5.617 | 2/9 |
| W1 / 60 days | 9 | −0.0330 | −5.829 to +5.763 | 6.853 | 4/9 |
| W2 / 20 days | 7 | −0.9833 | −7.286 to +5.319 | 7.269 | 1/7 |
| W2 / 60 days | 7 | −1.2525 | −7.348 to +4.843 | 7.030 | 2/7 |

Return intervals and MDEs assume independent normal event outcomes with unknown variance. MDE is the positive mean yielding 80% power in a one-sided 5% one-sample t test, using each sample's observed standard deviation; it is **not** an estimated alpha or a dependable power guarantee. Standardized MDE is 0.909 sample standard deviations at n=9 and 1.067 at n=7. Dependence, unstable variances, exposure to QQQ and costs are not resolved by this calculation. These are event averages before trading costs.

For sign skill, define a planning benchmark explicitly: an exact one-sided test of p≤50%, alpha=5%, power=80%. W1 needs at least **8/9** correct to reject that null and a true hit probability of **90.74%** to achieve 80% power—an MDE of **40.74pp** above 50%. W2 needs **7/7**, with true accuracy **96.86%**, an MDE of **46.86pp**. At true accuracy 70%, power is just **19.60%** and **8.24%**. The smallest independent sample size reaching 80% power against p=50% at true p=70% is **37** under this exact test. Fifty percent is an illustrative Bernoulli benchmark, not B2's permutation null: B2 has positive, zero and negative revision outcomes.

B2's empirical 70% hurdle differs from a significance test: it requires 7/9 or 5/7 hits. At true p=70%, the probabilities of meeting those respective sample hurdles are 46.28% and 64.71%; no joint probability is asserted because the windows overlap.

## Specification inventory

The observed original run computed **84 event/scenario rows = 14 origins × 3 weights × 2 replays**. Three weights (0.33, 0.5, 2/3) were declared before execution; only 2/3 feeds the original statistical summaries. The original threshold is **0.5pp only**, and original return horizons are **20 and 60 days only**. There is no evidence in the inspected B2 files that 1/1.5pp or 1/5-day results selected the headline.

Original outputs contain **12 sign/correlation rows**: three signal/outcome pairs (S1/revision, T/revision, T/FY bucket) × two replays × two windows. They contain **16 return rows**: two signals × two horizons × two replays × two windows; and **8 baseline rows**: two baselines × two replays × two windows. Only **two S1/PIT rows** gate the headline. S2 has no evaluable historical consensus. These counts are descriptive specifications, not independent experiments or an adjusted significance calculation.

The inherited kernel has **three lambda alternatives** (`ex_covid`, `last3`, `ewm`) and a selector requiring at least eight W1 leave-one-out cells before choosing the lowest historical RMSE; otherwise it defaults to `ex_covid`. The B2 term table records 75 valid PIT term rows with `ex_covid`, nine unavailable PIT rows and 84 full-sample term rows with `ewm`. Each set includes two horizons and three weights. Thus upstream model selection exists, but it did not create three independently scored B2 PIT replays. The full-sample `ewm` replay is retrospective. Headline S1 uses the seasonal lambda and cushion summaries; its q+2/FY relatives also introduce the trailing growth summary. Fixed weights and half-life are not fitted coefficients, but remain specification choices.

The refuter's new grid contains **36 sign rows** = 3 thresholds × 3 weights × 2 replays × 2 windows, and **144 return rows** after adding four horizons. All are preserved. No PIT weight/threshold combination passes the original sign-plus-correlation gate in either window. At headline weight, the new threshold sensitivities are:

| Threshold | W1 correct / strong n | W2 correct / strong n |
|---|---:|---:|
| 0.5pp | 5/9 = 55.6% | 4/7 = 57.1% |
| 1.0pp | 5/8 = 62.5% | 4/7 = 57.1% |
| 1.5pp | 4/6 = 66.7% | 3/5 = 60.0%; below minimum n |

## Explicit refutation attempts

1. **Claim → the numerator or denominator is wrong. Attack → independently reconstruct the ratios and count exact signs after the fixed threshold. SURVIVED:** 5/9 and 4/7 reproduce. Correctly signed means equal signs; a directional prediction of an unchanged revision is a miss.

2. **Claim → “below 70%” proves the population is below 70%. Attack → Wilson coverage, lower-tail tests and MDE. SURVIVED as written; stronger interpretation refuted:** both intervals include 70%; lower-tail probabilities are 0.270/0.353. The sentence describes the observed score relative to a preregistered hurdle. It cannot establish absence of skill or true sub-70% accuracy.

3. **Claim → both windows provide replication. Attack → compare event identities. SURVIVED as written; independence interpretation refuted:** all seven W2 strong events are among W1's nine, so the union is nine, not sixteen. W1 adds only 9 May and 1 November 2023, one miss and one hit. The exact sentence reports both mandated windows without calling them independent evidence; B2's note also discloses overlap.

4. **Claim → all four negative means imply reliable negative alpha. Attack → return-source reconciliation, intervals and leave-one-out signs. SURVIVED as a sample statement; population interpretation refuted:** all four means reproduce, all illustrative intervals cross zero, and every mean can turn positive after omitting one event. W1's −0.033pp at 60 days is especially fragile. Its exact sign must not be presented as economic magnitude or as evidence to reverse the trade.

5. **Claim → a chosen threshold manufactured failure or hid a passing result. Attack → inspect the original preregistration and run the new 0.5/1/1.5pp grid across all three weights. SURVIVED:** the original hurdle is 0.5pp and the wider PIT grid yields no gate pass. The 1.5pp W2 headline-weight result has only five cells. These new results are diagnostics, not additional preregistered confirmation.

6. **Claim → averaging across chosen horizons/replays overstated the negative result. Attack → inspect all original output rows and source 1/5-day returns. SURVIVED for the specified 20/60-day PIT sentence:** no averaging across weights, replays or horizons was needed. The new 1-day result is positive in W1 (+0.163pp, n=9) and negative in W2 (−1.072pp, n=7); 5-day means are −1.646pp/−2.420pp at n=9/7. Therefore an extension to “all horizons are negative” would be false.

7. **Claim → positive correlation rescues the failed sign claim. Attack → inspect two endpoints and original inferential diagnostics. SURVIVED:** correlations exceed 0.4, but the gate is conjunctive and sign accuracy fails. B2 reports block intervals crossing zero; its time-shuffling permutation probabilities are explicitly descriptive. Multiple endpoints, upstream alternatives and overlapping windows make an unadjusted selected p-value unsuitable as replacement evidence.

8. **Claim → the apparent failure reflects counting unchanged consensus as misses. Attack → exclude the zero-revision observations. SURVIVED under the preregistered estimand:** removing three zero outcomes in W1 and two in W2 changes accuracy to 5/6 and 4/5. That conditional question selects on the realized target and is not the registered all-strong-signals question; W2 then also falls below six cells. This is a useful qualification of what failed, not a correction to 5/9 or 4/7.

## What failed or could not be done

All audit assertions passed. The refutation attempts against population-level claims worked: power and dependence prevent those claims. A defensible dependence-adjusted return interval or precise power estimate cannot be identified from seven to nine events, so the planning calculations remain explicitly conditional on their assumptions. No attempt was made to infer every specification ever considered outside the permitted source files. This lens does not replace vintage or mechanism refuters.

## Interpretation

No number in the proposed sentence needs correction. For greater clarity, the writer may insert **“in these small, overlapping samples”** after the first clause and **“before costs”** after the return description. Preserve the failed preregistered result and distinguish failure to demonstrate an edge from evidence of no edge.

## RESUME

Parent should record this refuter's **SURVIVED** exact-sentence verdict, preserve the preregistration, script, receipt and timestamped grid, and combine this verdict with the separate vintage and mechanism lenses. Keep W2's nesting and the distinction between an empirical 70% hurdle and a population inference visible if this sentence enters the memo. No registries changed and this audit requires no scorer run; parent retains integration and shared-workboard ownership.
