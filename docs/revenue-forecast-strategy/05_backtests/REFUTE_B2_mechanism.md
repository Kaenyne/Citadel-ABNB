# B2 mechanism refutation

Codex B2 mechanism refuter · 2026-09-13 · branch `codex/lane2-full` · approximately 8 minutes · new `refute_b2_mechanism/` code and outputs only.

## Verdict

**SURVIVED.** The exact descriptive sentence reproduces: 5/9 strong-signal revision signs in W1 and 4/7 in W2, with negative signal-aligned 20- and 60-day executable excess-return means in both windows. This verdict does **not** establish an independent kernel mechanism. The announced-guide gap alone correlates 0.984 with revisions in each window, and the kernel's partial correlation after controlling for that gap is only 0.162/0.195. The evidence is consistent with consensus converging toward information already public when the kernel signal becomes executable. The proposed sentence correctly reports failure rather than claiming alpha.

Exact sentence audited:

> The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.

## Pre-registered pass line

At 2026-09-13 17:47 UTC, before the diagnostic, [the immutable refuter preregistration](REFUTE_B2_mechanism_PREREG.md) recorded:

> Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.

Seven attacks were fixed there: numerical reconstruction, announced-guide comparison, guide-controlled residual correlation, endpoint revision beyond the guide, unchanged-revision sensitivity, return leave-one-out sensitivity, and the QQQ hedge comparison. The original B2 threshold remains |S1| > 0.5%, with at least 70% signs correct and correlation above 0.4 on both windows. No threshold is changed in this audit.

## What ran

From the repository root:

```text
.venv\Scripts\python.exe analysis/src/forecast_methods/refute_b2_mechanism/run.py
```

The first run exited 1 after 0.94 seconds because the new reader omitted the L0 CSV's comment preamble handling. Its receipt is preserved as `data/processed/forecast_methods/refute_b2_mechanism/failed_run_receipt.txt`. The one local correction added `comment="#"`. The corrected run exited 0 after 1.78 seconds wall time; the analytical script reports 0.228 seconds. No frozen tests, source files, forecasts, registrations or scorers were changed.

Successful outputs are in `data/processed/forecast_methods/refute_b2_mechanism/run_20260913T174953_724563Z/`: `audit_cells.csv`, `mechanism_statistics.csv`, `return_statistics.csv`, `return_leave_one_out.csv`, `input_manifest.json`, and `summary.json`. The new script verifies unique source/join keys, source IDs and values, roles, attribution and timestamps, S1 and revision arithmetic, guide midpoint agreement with its low/high bounds and the returns table, original return cells, and all components of the exact sentence. It does not import B2 statistical functions. It uses B2's saved PIT kernel levels; independently rebuilding kernel fitting is the vintage refuter's task.

## Results

All main results below use PIT, weight 2/3. W2 is a subset of W1, not independent replication. The authoritative input is B2's metadata-corrected `run_20260913T171654_499731Z`. Vendor and timestamp accompany every consensus level in `audit_cells.csv`; the script reconciles them to the source register IDs. Aggregate statistics below are not additional consensus estimates.

Let C0 be pre-letter consensus, C1 consensus on the next print morning, K the post-letter kernel-implied guide, and G the guide announced in the same letter. In percentage units:

`S = 100(K/C0 − 1); R = 100(C1/C0 − 1); A = 100(G/C0 − 1)`.

The guide diagnostic compares A and S on the same eligible rows. Its hit count uses the **kernel's** strong-signal selection; it is not a separately tested guide strategy.

| PIT window | Paired n | Strong n | Kernel hits | Announced-guide sign hits on same strong cells | corr(S,R) | corr(A,R) | corr(S,R given A) |
|---|---:|---:|---:|---:|---:|---:|---:|
| W1 | 11 | 9 | 5/9 = 55.6% | 6/9 = 66.7% | 0.6872 | 0.9841 | 0.1622 |
| W2 | 9 | 7 | 4/7 = 57.1% | 5/7 = 71.4% | 0.6705 | 0.9836 | 0.1946 |

Residualization uses an intercept and A for both S and R. Guide-only in-sample R² is 0.96849/0.96756 (n=11/9); adding S yields 0.96932/0.96879, increments of only 0.00083/0.00123, or 0.083/0.123 percentage points of explained variance. The guide-only regression has two fitted coefficients; the enlarged regression has three. These are retrospective diagnostic fits, not point-in-time trading models. Their high R² neither proves causality nor creates an executable revision edge.

The endpoint quantities `S−A = 100(K−G)/C0` and `R−A = 100(C1−G)/C0` remove a full move to the guide. Their correlations are only 0.2361/0.2541 (n=11/9), with 6/11 and 5/9 matching signs. These quantities measure disagreement with the guide at the later endpoint; without an immediate post-letter consensus observation, they do not isolate subsequent drift.

| PIT window | Horizon | Strong n | Mean aligned excess return, pp | Mean aligned raw ABNB return, pp | Leave-one-out excess-mean range, pp | Positive leave-one-out means |
|---|---:|---:|---:|---:|---:|---:|
| W1 | 20 days | 9 | −0.44254 | −2.13480 | −1.82800 to +0.97947 | 2/9 |
| W1 | 60 days | 9 | −0.03297 | −0.46245 | −1.63917 to +1.26623 | 4/9 |
| W2 | 20 days | 7 | −0.98335 | −3.16945 | −2.92077 to +0.82253 | 1/7 |
| W2 | 60 days | 7 | −1.25245 | −1.39735 | −2.31460 to +0.27657 | 2/7 |

Each leave-one-out mean contains n−1 events. No events are dropped from the headline result. The negative means are sample facts, especially the near-zero W1 60-day mean; they are not robust estimates of negative expected returns. Removing QQQ entirely leaves all four aligned raw ABNB means negative, so the prescribed hedge does not create the headline sign. This does not validate QQQ as an optimal risk hedge.

## Explicit refutation attempts

| Claim attacked | Attack and outcome | Status |
|---|---|---|
| The proposed sign counts and return means are numerically correct. | Reconstructed S and R from saved kernel levels and source-verified consensus, then joined executable returns directly. Obtained the exact counts and all four negative means. | **Survived.** |
| Revision association represents information contributed by the kernel. | Replace S with the already-announced guide gap A on identical cells. A has much higher revision correlation and one additional correct strong-cell sign in each window; adding S improves in-sample R² by less than 0.0013. | **Refuted as an established independent mechanism.** This stronger claim is absent from the proposed sentence. |
| R measures consensus drift occurring after executable entry. | C0 is observed before the letter while S and G are known afterward. The endpoint includes adjustment to the public guide. Post-entry consensus is missing; the beyond-guide diagnostic gives only 0.236/0.254 correlation. | **Partially refuted.** Future-drift attribution is unidentified; the measured endpoint revision remains valid. |
| Failure against 70% persists under plausible alternative zero handling. | Remove unchanged outcomes: hits become 5/6 = 83.3% in W1 and 4/5 = 80.0% in W2; W2 then has fewer than six cells. This changes the estimand after observing outcomes. The preregistration explicitly treats zero as a distinct sign. | **Survived for the exact preregistered claim; not invariant to outcome selection.** |
| Negative historical means imply a stable adverse trading effect. | Every horizon/window can turn positive after removing one event; W1's 60-day mean is only −0.033pp. | **Refuted for robustness or expected-return language.** Exact full-sample descriptive signs survive. |
| QQQ subtraction manufactures the negative average signs. | Recompute the same signed observations using raw ABNB next-open returns. All four raw means remain negative. | **Survived against this attack.** No beta-adjusted hedge was estimated. |
| Kernel disagreement with the guide predicts the remaining revision. | Compare S−A with R−A on every paired row. Only 6/11 and 5/9 signs match, and correlations remain below 0.26. | **Refuted as an established incremental signal.** A small positive association remains, without inference or a predictive pass. |

## What failed or could not be done

The new reader's first-run parsing failure was fixed once and preserved; the corrected assertions passed. Pandas issued two deprecation warnings about `set_index(verify_integrity=True)` under the installed version, without affecting execution. An immediate post-letter consensus history is absent from the named inputs, so a clean post-entry revision test cannot be made. The guide-control regressions use 11/9 overlapping observations, with shared denominators and no identification of why analysts revise. No new statistical significance or trade recommendation is claimed.

## Interpretation

Retain the exact proposed sentence and B2's FAIL verdict. The strongest successful attack is economic: the observed revision correlation largely tracks the public guide, while the kernel adds little conditional association. That limits any stronger mechanism or timing language. It does not overturn a sentence that already reports failed sign thresholds and negative descriptive returns. The audit also prevents the opposite overstatement: these small, event-sensitive negative means do not establish a profitable inverse strategy.

## RESUME

Parent should record B2 mechanism as **SURVIVED on the exact sentence**, link this new note, and preserve the guide-convergence limitation in the combined refuter review. No scorer run is caused by this audit. Any future B specification should obtain an attributed consensus snapshot after the guide has been absorbed, preregister guide-only and incremental-kernel comparisons on common samples, and keep the negative original finding; the present diagnostics should not be converted into a newly selected trading rule.
