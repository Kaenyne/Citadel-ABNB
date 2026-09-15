# A2 — Vintage refutation

Agent `refute_a2_vintage` · 13 Sep 2026 · parent branch `codex/lane2-full` · approximately 10 minutes. All new work: `analysis/src/forecast_methods/refute_a2_vintage/` and `data/processed/forecast_methods/refute_a2_vintage/`. Parent owns the shared WORKBOARD update.

## Verdict

**SURVIVED.** The exact sentence is reproduced under the required letter-close convention: **7/8 W1 and 6/7 W2** high-signal guide-sign hits; signed next-open 20-day excess returns **−0.307680pp and −0.983347pp**, respectively. Independently clipped historical inputs match the A2 guide points within **4.55e−13 USD million**. No future lambda, GBV or realised cushion is needed. This verdict applies to the quoted association and unproven-trade sentence, not to a before-release forecasting claim. A synthetic timestamp attack found a real selector boundary defect, described below; no current historical denominator exercises that defect.

Exact sentence audited: “At letter-close vintages, the kernel agrees with the guide-gap sign in 7/8 W1 and 6/7 W2 cases with |S|>1pp, but the executable next-open 20-day return test does not establish a trading edge.”

## Pre-registered pass line

Written **2026-09-13 17:24:24 UTC**, before empirical refuter computation, in `data/processed/forecast_methods/refute_a2_vintage/preregistration.md`.

“Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.”

The preregistered audit covers every historical L0 consensus row, independently clipped K0 inputs, the exact sign count and next-open mean, deliberately future lambda/GBV variants, registry dates and synthetic timestamp attacks. No specification chosen from the sensitivities replaces the headline. Parameter count added: **0**; K0 supplies its existing estimator. No new forecast is produced for registration.

## What ran

From the repository root:

```text
.venv/Scripts/python.exe analysis/src/forecast_methods/refute_a2_vintage/run.py
```

The invocation captured stdout/stderr with PowerShell `Tee-Object` into `data/processed/forecast_methods/refute_a2_vintage/run_receipt.txt`. First run completed, exit **0**, measured Python runtime **16.365 seconds**. No failed run or repair was needed. The script asserts exact headline counts, numerical reconciliation, publication cutoffs, next-open event joins, hedge arithmetic, PIT registry points and matching shared-input hashes. Neither scorer nor frozen tests were run; no existing file was changed and nothing was registered.

The headline reconstruction does **not** call A2's cell builder, consensus selector or statistics functions. It selects L0 observations independently, maps publication dates from the frozen calendar, clips raw KPI and realised-cushion frames to `print_date <= d`, and supplies those frames to authoritative K0 `kernel_guide(q, d+1)`. This follows CONVENTION §1's instruction to use K0 rather than estimate another lambda model. A second K0 call with its normal input loading confirms that independently clipped inputs produce the same point. Only the separate synthetic stress test calls A2's consensus selector.

## Results

| Independently reconstructed PIT statistic | W1 | W2 |
|---|---:|---:|
| Candidate letters | 14 | 10 |
| Admissible named-vendor pre-guide consensus | 13/14 | 9/10 |
| Evaluable kernel/guide-gap pairs | 11/14 | 9/10 |
| Strictly \|S\| > 1pp, unambiguous rounded sign | 8 | 7 |
| Sign hits | 7/8 | 6/7 |
| Signed next-open 20-day mean | −0.307680pp, n=8 | −0.983347pp, n=7 |

W2 is a subset of W1. The retained high-signal W1 quarters are 2023Q4, 2024Q1, 2024Q4, 2025Q1, 2025Q2, 2025Q4, 2026Q1 and 2026Q2. W2 removes 2023Q4. The shared miss is 2025Q1: S=+1.238192pp against a −2.173913pp guide gap, using **LSEG $2,300m, stamped 2025-02-13**. That event's next-open excess return is −11.818581pp. The negative mean is reproduced directly from the executable return columns; this audit does not claim to prove zero alpha from a small sample.

### Every W1 pre-guide source

All rows below have `role=pre_guide`, metric revenue and `vendor_attributed=True`; each row is one observation, **n=1**. Dollar amounts are USD million. Date-only stamps are treated as morning-of-print under CONVENTION §2, not independently verified clock times. Every value agrees with the separate next-quarter-consensus column in the named merged input; the letter's guide occupies a different column.

| Target / register ID suffix | Vendor | Source stamp | Value | `pit_usable` | Headline use |
|---|---|---|---:|---|---|
| PG-2023Q1-revenue | Refinitiv | 2023-02-14 | 1,690 | True | Kernel unavailable |
| PG-2023Q2-revenue | Refinitiv | 2023-05-09 | 2,420 | True | Included |
| PG-2023Q3-revenue | Refinitiv | 2023-08-03 | 3,220 | True | Kernel unavailable |
| PG-2023Q4-revenue | LSEG | 2023-11-01 | 2,180 | True | Included |
| PG-2024Q1-revenue | LSEG | 2024-02-13 | 2,030 | True | Included |
| PG-2024Q2-revenue | LSEG | 2024-05-08 | 2,740 | True | Included |
| PG-2024Q3-revenue | LSEG label only | Missing | 3,840, quarantined | False | Excluded |
| PG-2024Q4-revenue | LSEG | 2024-11-07 | 2,420 | True | Included |
| PG-2025Q1-revenue | LSEG | 2025-02-13 | 2,300 | True | Included |
| PG-2025Q2-revenue | LSEG | 2025-05-01 | 3,040 | True | Included |
| PG-2025Q3-revenue | LSEG | 2025-08-06 | 4,050 | True | Included |
| PG-2025Q4-revenue | LSEG | 2025-11-06 | 2,670 | True | Included |
| PG-2026Q1-revenue | LSEG | 2026-02-12 | 2,530 | True | Included |
| PG-2026Q2-revenue | LSEG | 2026-05-07 | 3,460 | True | Included |

The quarantined 2024Q3 source says `NEXT-QUARTER CONSENSUS NOT FOUND`; its unattributed numerical appearance in the merged file cannot restore a vintage. The source audit also lists all five older extension letters and every at-print revenue/GBV control observation, with role, stamp, eligibility, actual vendor text, units and exclusion reasons. September `current` rows are never historical candidates.

### Refutation attempts

| Claim being attacked | Attack and evidence | Outcome |
|---|---|---|
| Historical signals use pre-guide Street | Independently select `role=pre_guide` by target, inspect eligibility/vendor/date, and compare to the merged file's distinct consensus and guide fields. The 13/14 W1 and 9/10 W2 admitted denominators have named vendors and date-only stamps at the correct letter date. No current snapshot or letter guide was substituted. | **Survived** for the exact claim. |
| Historical timestamp screening enforces the intraday boundary | Change an in-memory copy of `PG-2025Q1-revenue` to `2025-02-13T23:59:00`. A2 returns `available` because it normalizes both timestamps to dates. This hypothetical late observation should not be accepted as morning-of-print. Actual historical denominators have no intraday stamps, so none uses this path. | **Partially:** the implementation's general timestamp guarantee is refuted; current headline is unchanged. |
| Lambda estimates are PIT | Supply only KPI observations published by d, call K0, and inspect every listed training quarter's publication date. The latest same-season training print is earlier than the guide date for all 12 available W1 kernel points; all nested-selection data are clipped to d. Independently clipped points agree with A2 within 4.55e−13m. Then deliberately update target-season lambda using the next letter. This produces different counts, shown below. | **Survived:** future lambda is unnecessary. |
| Both GBV lags are known at formation | Check the two required quarterly GBV publication dates against d, including the letter's freshly printed q−1 GBV. Replace them deliberately with q and q−1, which requires target-quarter GBV released at the next letter. Hit counts fall to 5/11 W1 and 4/9 W2. | **Survived:** future GBV is unnecessary; these remain after-letter signals. |
| The guide divisor does not use the target's eventual beat | Rebuild realised actual/guide ratios from the raw cushion series, date them by the quarter's actual print, keep only dates ≤d, and take the last eight. The target q is absent from every divisor; medians match K0 to <1e−12. All available W1 points use eight ratios except 2023Q2, which uses six. The latest ratio is released on d and is allowed at this vintage. | **Survived** under the explicit convention. |
| Missing cells are not silently restored | Reconstruct all 14/10 candidates: the two early ex-COVID seasonal histories remain unavailable; 2024Q3 remains quarantined even though the merged file has a number. Rebuilt counts are exactly 11/9 evaluable and 8/7 high-signal. | **Survived.** |
| The return leg is executable and supports the sentence's negative conclusion | Join returns by letter date; require `entry_date>d` and the correct guided quarter. Recompute ABNB-minus-QQQ from the component next-open 20-day columns, then multiply by sign(S). Neither overnight gap nor close-to-close return enters the mean. Both independently reconstructed means are negative. | **Survived.** |
| Ancillary controls have named-vendor provenance | Audit at-print GBV controls against their actual vendor text. The package's six complete control cases have `vendor_not_recorded` despite attributed/usable flags. A real named-vendor requirement leaves that control unavailable; a boolean flag alone does not cure the defect. The reviewed A2 note already reports this limit. | **Partially:** stronger control/causal support fails; the exact descriptive sentence does not depend on it. |
| Registration backdates unavailable information | Check every PIT historical row's vintage against its guide date, `knowable_from<=vintage`, and its point against the independent rebuild: 22/22 PIT rows agree (12 W1, 10 W2, overlapping). The registry has 46 historical rows including the separately labelled retrospective replay and 2 LIVE rows. No full-sample point enters the headline. | **Survived** for historical point provenance. |

### Deliberate look-ahead, excluded from the verdict

The next-letter-lambda attack calls K0 `pit_lambda` for the same target season after the target quarter prints; this includes unavailable future information. The next-quarter-GBV attack advances the two-lag base from (q−1,q−2) to (q,q−1). Both retain the original dated cushion and consensus so the leakage channel is identifiable. These are adversarial sensitivities, **not PIT estimates and not candidate signals**.

| Deliberate construction | W1 eligible / high-signal hits | W2 eligible / high-signal hits | Signed 20-day mean W1 / W2 |
|---|---|---|---|
| Correct PIT reconstruction | 11; 7/8 | 9; 6/7 | −0.307680pp (n=8) / −0.983347pp (n=7) |
| Next-letter lambda | 13; 9/9 | 9; 6/6 | −0.917984pp (n=9) / +0.822526pp (n=6) |
| Next-quarter GBV | 11; 5/11 | 9; 4/9 | −0.480774pp (n=11) / −0.909900pp (n=9) |
| Both future inputs | 13; 6/13 | 9; 4/9 | −0.693463pp (n=13) / −0.909900pp (n=9) |

Future lambda can manufacture a perfect guide-sign record on a different selected sample; the original result does not require it. In particular, this future variant restores early observations that are genuinely unavailable in the default PIT construction. Comparing those cells as if they were an independent validation would be wrong.

## What failed or could not be done

The synthetic post-close selector attack worked. `valid_consensus` compares `.normalize()` values, which discards an explicit time. Harden this check before ingesting historical intraday stamps: date-only records require the documented morning-of-print convention; explicit timestamps require a defined pre-letter cutoff with an explicit timezone. Do not guess an intraday cutoff or convert all date-only rows to exclusion. This refuter leaves A2 code unchanged and reports the issue to the parent.

L0's historical pre-guide rows have date-only stamps and no source URLs in that register. The named merged input corroborates their values and labels but is not an independent raw vendor archive. Under the mandated convention they are admissible; this audit cannot certify their original intraday capture from these files. No public-source re-acquisition or licensed database access was attempted. Historical revision risk in the consolidated KPI input also cannot be eliminated without archived first-release snapshots, although the input values and hashes are exactly those audited by the package.

The published bootstrap intervals were not independently rebuilt by this vintage lens; the independently negative means suffice to reject the package's positive-mean return condition. The control provenance flaw and timestamp defect limit stronger claims but do not alter the specific count or negative return conclusion. This is a refutation of an existing registration, so no additional registry rows or scorer run were appropriate.

## Interpretation

Keep the sentence exactly as limited: letter-close sign association and no established executable trading edge. The guide and the GBV used in S arrive in the same release. That timing makes the comparison descriptive of the newly disclosed information set; it does not demonstrate anticipation of the guide. Missing consensus and seasonal-history exclusions remain necessary. Source provenance rests on the explicit repository convention, while the timestamp guard needs hardening for future intraday history.

## RESUME

Parent should count this as **SURVIVED for the exact sentence**, link the note from its Gate-2 record and WORKBOARD update, preserve the timestamp and unnamed-GBV-control findings, and run its own required scorers at CLOSE. The audit is reproducible from `run.py`; `independent_cells.csv`, `consensus_row_audit.csv`, `summary_and_lookahead.csv`, `audit.json` and the successful receipt contain every reconstruction and input hash. Do not replace the headline with a future-lambda sensitivity or treat a date-only stamp as independently verified intraday provenance. No human decision is needed to retain this narrow wording.
