# REFUTE A2 — mechanism

Agent refute_a2_mechanism · 2026-09-13 · branch `codex/lane2-full`.

## Verdict

**SURVIVED.** The exact descriptive sentence reproduces: “At letter-close vintages, the kernel agrees with the guide-gap sign in 7/8 W1 and 6/7 W2 cases with |S|>1pp, but the executable next-open 20-day return test does not establish a trading edge.” This verdict does **not** validate the stronger phrase “mechanism confirmed.” On the six shared GBV-control observations, corr(S, actual guide gap) falls from **0.626236 to 0.000585** after controlling for printed GBV surprise. Those six consensus vendors are unrecorded, so the result is a serious confound diagnostic with incomplete provenance, not an identified causal explanation. All three fixed hedge choices retain negative mean returns and zero-crossing descriptive 90% intervals in both windows.

## Pre-registered pass line

Written 2026-09-13T17:32:02Z before running these new diagnostics. REFUTER.md's pass line: “Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. ‘Partial’ does not count as survived.”

The exact descriptive sentence survives if its sign counts reproduce and the proposed executable test supplies no established positive trade edge. This is distinct from establishing a kernel mechanism. Five attacks are fixed here: independently rebuild GBV-surprise partial correlations from the KPI panel and L0 values; compare the contemporaneously available raw-guide-gap strategy; vary the QQQ hedge using no hedge and a pre-event 252-day beta; condition descriptive relationships on target season and leave each season out; compare simple sign baselines and identify the shared-consensus construction. All are hostile sensitivity diagnostics, not newly selected trading strategies. The beta uses daily close returns strictly before the letter date, at least 126 observations, an intercept, and at most 252 observations. No costs are assumed; no signal thresholds or horizons are optimized. The headline remains |S|>1pp at 20 next-open trading days, W1 and nested W2. Season fixed effects are in-sample diagnostics and never a tradable forecast. Fewer than six cases is underpowered and is not promoted.

## What ran

From the repository root, `.venv` Python:

```text
python analysis/src/forecast_methods/refute_a2_mechanism_v1/run.py
```

The first run succeeded, exit **0**, Python diagnostic time **0.580 seconds**, tool wall time **2.732 seconds**. `data/processed/forecast_methods/refute_a2_mechanism_v1/run_receipt.txt` preserves the output; the original shell receipt also remains at `data/processed/forecast_methods/refute_a2_mechanism_v1_run_initial.txt`. No empirical run failed and no post-result code correction was required.

The script imports neither A2 nor its statistics functions. It reads the kernel point from A2's registered **W1 PIT** row, independently joins each pre-guide consensus from L0, independently extracts actual guide midpoints from the guidance ledger, and independently recomputes printed GBV surprise from the KPI panel's letter-precision `gbv_busd` and the `AP-<printed quarter>-gbv` consensus. All eleven rebuilt signals and gaps agree to 1e-10pp; GBV controls agree including missingness. It validates 22 ABNB/QQQ twenty-bar returns against raw OHLC. Beta hedges use 252 daily observations strictly before each event; their event-level coefficients and sample counts are in `cells.csv`.

OLS residualization uses an intercept and the listed controls separately for S and the target, on the same complete cases. No A2 fitted lambda or cushion is re-derived. Existing package controls are a comparison, not inputs to these calculations. `audit.json` hashes all seven input files and records zero registrations and no scorer runs. This is a mechanism audit, not a substitute for the separate vintage refuter's independent kernel-availability check.

## Results

All headline rows use the PIT default. W2 is a subset of W1; the identical GBV control sample is the **same six events**, not independent replication. Returns are percentage points, next trading-day open through the twentieth trading-day close. No overnight gap enters a statistic.

| Rebuilt statistic | W1 | W2 |
|---|---:|---:|
| Evaluable signal/gap pairs | n=11 | n=9 |
| High-signal guide-sign hits | 7/8, n=8 | 6/7, n=7 |
| Kernel signed 20-day return mean | −0.307680pp, n=8 | −0.983347pp, n=7 |
| Actual guide-gap signed return mean | +2.646965pp, n=8 | +2.393391pp, n=7 |
| Guide-gap minus kernel mean | +2.954645pp, n=8 | +3.376738pp, n=7 |
| corr(S, guide gap), all evaluable | 0.676803, n=11 | 0.654747, n=9 |
| GBV controls with an actual named vendor | 0/6 | 0/6 |

| Independently rebuilt relationship and control | W1 raw → partial | W2 raw → partial |
|---|---:|---:|
| S vs return; GBV surprise | −0.069129 → −0.463405, n=6 | −0.069129 → −0.463405, n=6 |
| **S vs guide gap; GBV surprise** | **0.626236 → 0.000585, n=6** | **0.626236 → 0.000585, n=6** |
| S vs return; raw guide gap | +0.015639 → −0.392108, n=11 | −0.051548 → −0.441007, n=9 |
| S vs return; GBV surprise + raw guide gap | −0.069129 → −0.538118, n=6 | −0.069129 → −0.538118, n=6 |
| S vs return; target-season fixed effects | +0.015639 → −0.104796, n=11 | −0.051548 → −0.145578, n=9 |
| S vs guide gap; target-season fixed effects | +0.676803 → +0.718409, n=11 | +0.654747 → +0.743485, n=9 |

The single-GBV control has two fitted coefficients per residualization, including intercept; joint GBV+gap has three; season has four. These are descriptive small-sample regressions. The apparent disappearance of the S–guide-gap association after GBV control is not proof that the kernel is redundant: GBV surprise contains printed GBV that is also a legitimate kernel input, consensus GBV coverage is selected, and all six GBV vendor names are missing. It does disallow saying this sample distinguishes an independent recognition-kernel mechanism from the printed GBV surprise.

| Fixed hedge sensitivity | W1 signed mean [block 90% interval], n | W2 signed mean [block 90% interval], n |
|---|---|---|
| ABNB − 1×QQQ | −0.308 [−3.707, +3.424], n=8 | −0.983 [−4.229, +2.453], n=7 |
| Unhedged ABNB | −3.164 [−8.832, +1.825], n=8 | −3.169 [−9.397, +2.637], n=7 |
| ABNB − pre-event beta×QQQ | −0.147 [−3.919, +4.217], n=8 | −1.144 [−4.465, +2.277], n=7 |

Beta is a fixed-weight factor-return diagnostic, not a full financing/rebalancing model. Its sign-result does not depend on that nuance: the no-positive-edge conclusion also holds unhedged. Bootstrap intervals use 2,000 circular length-2 draws at fixed seed 20260913, reproduce A2's unit-QQQ intervals, and remain descriptive at n=7–8.

| High-signal season | W1 hits; signed return mean | W2 hits; signed return mean |
|---|---|---|
| Q1 target | 2/3; −0.063pp, n=3 | 2/3; −0.063pp, n=3 |
| Q2 target | 2/2; −1.942pp, n=2 | 2/2; −1.942pp, n=2 |
| Q3 target | No cases, n=0 | No cases, n=0 |
| Q4 target | 3/3; +0.537pp, n=3 | 2/2; −1.405pp, n=2 |

Every seasonal subset is underpowered. Dropping Q2 changes W1's return mean to +0.237pp (n=6), but W2 remains −0.600pp (n=5, underpowered). Every other nonempty seasonal deletion leaves W2 negative. Season fixed effects do not remove the all-sample S–guide-gap association, but high-signal Q3 is untested. A strictly prior-observation same-season guide-sign rule gets only 2/6 on the common high-signal subset (n=6 in each window); it abstains when the first usable observation of a season has not yet appeared. Always-positive and always-negative guide-sign baselines both get 4/8 in W1 (n=8); W2 is 4/7 and 3/7 (n=7). These elementary rules do not explain away the reported sign accuracy.

### Six explicit refutation attempts

1. **Claim → the 7/8 and 6/7 counts reflect the registered PIT output. Attack →** independently join registry points, source guide dollars and source pre-guide consensus; recompute signs and threshold eligibility. **SURVIVED:** the counts reproduce, with eleven/nine evaluable pairs and eight/seven high-signal pairs. No lambda is re-estimated in this lens.
2. **Claim → the sign association supports a distinct kernel mechanism. Attack →** independently residualize both S and the actual guide gap on printed GBV surprise. **PARTIALLY:** correlation becomes 0.000585 from 0.626236 on the same six rows. This attacks the broader mechanism interpretation; missing vendor provenance and shared kernel/GBV inputs prevent attributing the association conclusively to GBV surprise. The exact sentence only reports agreement and survives.
3. **Claim → the kernel adds executable information after the letter. Attack →** use the actual guide gap available at the same next open. **REFUTED for this stronger incremental-edge claim:** the guide-gap rule's mean exceeds the kernel's by 2.955pp/3.377pp (n=8/7); all of that difference comes from the one high-signal disagreement, the 2025-02-13 letter guiding 2025Q1. The kernel's positive signal loses 11.819pp; the actual negative gap gains 11.819pp. Neither rule is thereby proven profitable. The exact sentence's no-established-edge conclusion survives.
4. **Claim → the negative pooled return result might be an artifact of subtracting too much QQQ. Attack →** replace unit QQQ with no hedge and a strictly pre-event beta. **SURVIVED:** all six window/hedge cells have negative signed means and intervals crossing zero. This attack fails to reveal a robust positive edge.
5. **Claim → seasonality alone produces the guide-sign association, or hides a stable positive reaction. Attack →** season fixed effects, every leave-season-out check, and the prior same-season sign baseline. **PARTIALLY:** season effects do not eliminate the guide-gap association, but seasonal reaction cells are n≤3, Q3 has no high-signal observation, and a W1-only deletion flips its return sign. No seasonal robustness claim is warranted; the original bounded sentence survives.
6. **Claim → raw S/guide-gap correlation by itself demonstrates special recognition information. Attack →** examine the shared construction and simple sign baselines. Both S=(K−C)/C and gap=(G−C)/C share C; exactly S−gap=(K−G)/C. The letter also reveals G before the proposed entry. **PARTIALLY:** the common benchmark and timing prevent treating raw agreement as an independent forecast/causal identification test. Always-long/always-short and prior-season rules fail to match the observed sign hits, so this attack does not falsify the numerical association. A pre-release comparison would require a GBV forecast actually available before the letter.

### Source provenance for the GBV control

Each row below is one observation (n=1). The six rows are common to W1 and W2. L0 labels them `role=at_print`, `pit_usable=True` and `vendor_attributed=True`, yet the stored vendor string is `vendor_not_recorded`. Date-only stamps are morning-of-print under the convention. A named-vendor requirement leaves **n=0**.

| Guided quarter | GBV register ID | Stored vendor | Timestamp | Source consensus, USD bn | Rebuilt surprise |
|---|---|---|---|---:|---:|
| 2024Q4 | AP-2024Q3-gbv | vendor_not_recorded | 2024-11-07 | 19.90 | +1.005025% |
| 2025Q1 | AP-2024Q4-gbv | vendor_not_recorded | 2025-02-13 | 17.20 | +2.325581% |
| 2025Q3 | AP-2025Q2-gbv | vendor_not_recorded | 2025-08-06 | 22.66 | +3.706973% |
| 2025Q4 | AP-2025Q3-gbv | vendor_not_recorded | 2025-11-06 | 21.90 | +4.566210% |
| 2026Q1 | AP-2025Q4-gbv | vendor_not_recorded | 2026-02-12 | 19.40 | +5.154639% |
| 2026Q2 | AP-2026Q1-gbv | vendor_not_recorded | 2026-05-07 | 27.82 | +4.960460% |

Every pre-guide revenue consensus value, vendor, source ID and timestamp used by this audit is preserved in the new `cells.csv`. High-signal pre-guide revenue rows are named LSEG, stamped their respective guide dates. The other evaluable 2023Q2 row is Refinitiv. No `current` consensus, LIVE row or historical full-sample point enters these diagnostics.

## What failed or could not be done

An independently identified kernel mechanism could not be established. The only complete GBV-control sample is six observations with unnamed vendors; season-specific tests contain at most three high-signal observations. No reliable market-neutral alpha follows from one factor beta, and no significance test on one missed signal proves the direct guide-gap rule dominates out of sample. No new data were fetched and no licensed data accessed.

The original package's phrase “mechanism confirmed” is stronger than either the disclosed control provenance or this refutation supports. Replace it with **“descriptive letter-close guide-sign association; independent mechanism unestablished.”** Keep the exact submitted memo sentence unchanged if it is accompanied by the sample counts and the letter-close interpretation.

## Interpretation

The strongest successful attack is on attribution, not arithmetic: controlling for GBV surprise nearly erases the S–guide-gap association in the available six-event slice. The strongest execution attack is simpler: the actual guide is already known at entry and improves the realized return on the same opportunity set. Neither finding contradicts the carefully limited sentence, which avoids asserting an incremental, causal or pre-release forecast edge. The negative return result survives the pre-fixed QQQ hedge alternatives. This refuter votes **SURVIVED on the exact sentence**, and **not established on the independent-kernel-mechanism interpretation**.

## RESUME

Parent should record this refuter as complete, combine its exact-sentence vote with the vintage and power votes, and retain the distinction between descriptive guide-sign agreement and mechanism identification. Review `refute_a2_mechanism_v1/controls.csv` for the 0.626236→0.000585 GBV-controlled guide-gap result and `hedge.csv` for all three fixed negative-return checks. No package input, registry, frozen harness or scorer output was changed; zero forecast rows were registered, and parent alone owns the shared WORKBOARD and any CLOSE scorer runs. If named historical GBV vendors later become available, rerun this pre-fixed audit in a new versioned folder; do not relax provenance or promote the six-event control result as causal proof.
