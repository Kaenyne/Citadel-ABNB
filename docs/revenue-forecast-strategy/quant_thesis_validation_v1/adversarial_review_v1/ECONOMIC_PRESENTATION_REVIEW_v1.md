# Wave 3 H — independent economic and adversarial presentation review

2026-09-14 · reviewer source_auditor · author reviewed: test_designer (wave 2 E) and lead-owned foundations/figures · new adversarial_review_v1 output directories · no edits to reviewed packages.

## Verdict

**PASS for conditional arithmetic and the inspected presentation boundaries.** Independent reconstruction agrees with all **567** reviewed economic cells within **4.36e−11** in the relevant units. These are deterministic checks, with empirical-validation n=0 and zero newly estimated parameters. The review does not approve an investment direction or a twelve-month price target. It accepts the narrower conclusion that the isolated operating gap has little per-share impact, while persistence, multiple and balance-date assumptions can dominate.

The final combined claim ledger and one-page decision summary had not yet been provided at this review's cutoff. They require a short separate review supplement. The prospective calculation's numerical independence is reviewed by wave 3 G, because H authored that implementation. H's inspection of the forecast figure covers display, labeling and linkage to the published record only.

## Inputs, independence and exact command

Reviewed E canonical output: `data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/results_v2`, governed by `RESULTS_v1.md`, `PUBLICATION_REPAIR_v2.md` and `README_FINAL_v2.md`. Every reviewed file's exact SHA-256 is recorded in this review receipt.

Independent source inputs were loaded directly with `git show` from L4 commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`: `lane4_model_v1/snapshot_v4/annual.csv`, `model_input.json`, `lane4_revenue_v1/snapshot_v1/forecast.csv` and `consensus_selection.csv`. This reviewer imported no author function. The reviewer reconstructed counterfactual income/cash statement **levels** and then differenced them, rather than calling E's marginal-impact formula. The endpoint check integrated modeled H2/FY27 flows from June 2026 source balances, rather than interpolating E's endpoint output table.

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/adversarial_review_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/adversarial_review_v1/results_v2
```

Exit 0; 1.1 seconds. Canonical independent artifacts: `results_v2/independent_checks.csv` and `results_v2/receipt.json`. Source code SHA-256 `01b1e5c6d01e7eeb15900b53e2b52536d20066eb45c72320cd517755fcb844b9`. Initial results_v1 (540 checks) remains preserved; results_v2 adds the required 27 repurchase-price checks. No mathematical failure occurred and no reviewed author number was changed.

| Independently inspected object | Economic rows | Numerical checks | Status |
|---|---:|---:|---|
| Annual L4 cash costs, EBITDA, operating/net income, FCF, SBC-adjusted FCF, net cash and shares | 21 scenario-years | 168 | PASS |
| Conditional endpoint cash/share flows and fixed-FY27 EBITDA lens | 4 endpoints | 12 | PASS |
| One-quarter versus sustained, fixed/proportional SBC and three cash-cost responses | 24 scenario-year rows | 192 | PASS |
| Per-share lower-revenue counterfactuals over 3/6/12 months and December 2027 | 48 scenario-endpoint rows | 48 | PASS |
| Multiple, cash and share sensitivity | 108 grid cells | 108 | PASS |
| Break-even multiple and cash/multiple derivatives | 4 endpoints | 12 | PASS |
| Fixed spending with transaction-price/issuance-price alternatives | 9 price-endpoint rows | 27 | PASS |

The 567 check count happens to equal the author's separate reconciliation count; they are different decompositions of dependent equations, not two sets of independent financial observations.

## Economic conclusions that survive the challenge

The like-basis Q4 revenue gap is positive **18.3221642864 USDm**, from immutable own review revenue minus a captured Yahoo/LSEG-family revenue expectation. No guide expectation is manufactured. A one-quarter contrast with fixed compensation has no recurring FY27 EBITDA effect; its maximum twelve-month fixed-assumption value is approximately **$0.03067/share**. Sustaining the fractional contrast through FY27 can increase the conditional value effect to **$2.77137/share**, but requires persistence that is neither observed in this comparison nor validated by the kernel test.

The **$182.867016** value at September 13, 2027 holds FY27 EBITDA and 16.5x constant and changes modeled cash/share balances only. It is a **horizon-convention sensitivity**, not an underwritten price target or expected stock price. Its **$1.795739** difference from the inherited December 31, 2027 **$184.662755** number and the **$10.032807/share per multiple turn** are correctly calculated. Endpoint time changes the forward metric's remaining duration as well as balances; holding the multiple fixed is an isolating assumption, not an assertion that investors use identical valuation treatment at every endpoint.

Customer funds do not enter corporate net cash. D&A is part of total EBITDA addbacks and is not deducted twice. Full SBC is not also subtracted as cash from a roll that separately includes withholding and net issuance. The economic SBC-adjusted FCF view is kept distinct. The June 2026 starting share count remains a weighted-average diluted proxy, not an observed ending share count; future grant/settlement/buyback timing is unknown. These limits are already explicit in E's final notes.

The eta=1 negative cash effect is mathematically valid under the inherited formulas: proportional cash taxes, capex and working-capital assumptions can consume cash even when the extra core revenue is offset by core costs. The tiny positive sustained EBITDA-lens effect can arise from revenue-scaled addbacks. Neither is evidence of an economically identified cost response. E discloses both artifacts, so no numerical repair or removal of unfavorable scenarios is warranted.

## Adversarial claim examination

| Proposed inference or likely judge objection | Review disposition | Defensible reply or required boundary |
|---|---|---|
| The guide is below the Street, therefore downside is forecastable | REJECT | Revenue consensus is a different object; use equal-basis comparisons and retain missing explicit guide expectations |
| The September reconstruction's guide near 3,162m confirms the September 13 revenue consensus near 3,161m | REJECT | Similar numbers still differ in metric and information origin. Do not bridge them without a labeled hypothetical policy assumption |
| The isolated Q4 gap provides an investable earnings discrepancy | UNSUPPORTED | Maximum fixed-compensation one-off effect is only about three cents/share under this grid; large effects require persistent earnings assumptions |
| The 182.87 calculation is the correct competition twelve-month target | REJECT | It isolates one balance-timing convention while holding FY27 EBITDA/multiple fixed. It is not a newly underwritten target |
| Negative eta=1 cash proves revenue growth destroys cash | REJECT | This is a conditional algebraic consequence of imposed marginal tax/WC/capex conventions |
| Buybacks are all capital return and SBC is costless because noncash | REJECT | Repurchases, withholding, issuance and economic compensation must be reconciled together, with explicit share-price/timing assumptions |
| No validated preannouncement or revision edge means a short is impossible | REJECT | It rejects this proposed evidence of edge, not every possible short thesis. A different thesis needs independently supported economics |
| A reliable conversion reference can coexist with a constructive investment view | SUPPORTED CONDITIONALLY | Growing cash generation and reduced modeled shares are compatible with the same retained kernel. Broad consensus agreement can leave no differentiated operating view |

The strongest competing interpretation is that stable conversion and cash generation support the business, broad revenue panels already anticipate much of its growth, and unsupported RNPL/FX causal magnitudes cannot justify an automatic short. A favorable investment argument would still need a dated price, a supported persistence/cost view and an adequate per-share gap. Neither direction follows mechanically from this validation.

Measurable evidence that would change the conclusion includes the first Q4 guide and Q3 booked GBV, compared with expectations of the same object at a lawful earlier timestamp; evidence that an operating gap persists; actual incremental costs/cash taxes; corporate working capital; and issued/withheld/repurchased shares at their actual prices. A cushion-only movement changes a guide forecast without changing revenue or cash and cannot substitute for these links.

## Presentation and figure inspection

Visually inspected `figures_v1/expectations_break_even.png` and `figures_forecast_v2/preannouncement_forecast_test.png`. Both are legible with no clipping. The first labels the hypothetical common-cushion comparison, LSEG-family timestamp, one conditional reference and deterministic stresses. It does not present the lines as confidence bounds. The second shows W1/W2 matched n=12/10, nested W2, the actual origin rule, two abstentions, integer-loss convention and historical reconstruction. It visibly preserves the failed two-comparator hurdle. No display repair is required.

Lead `PRESENTATION_DEFENSE_FOUNDATIONS_v1.md` correctly separates reduced-form lag weights, arithmetic variance, flow versus stock denominators, source precision, causal mechanisms and investment consequences. Its “actual first-lag arithmetic contribution” should be understood only as the contribution implied by the fixed formula, never a measured physical cohort share; the final claim ledger should preferably say **“implied first-lag arithmetic contribution.”** The foundations are labeled incomplete pending reviewed empirical/economic results, which is appropriate.

## Findings and closure

No material unresolved numerical or accounting finding in E's canonical economic bridge. All persistent limitations restrict its permitted wording: unvalidated marginal costs/persistence, fixed multiple/forward metric, conditional uniform flow timing, starting weighted-average shares and historical price/consensus references. These are findings, not missing engineering work. Final combined prose review remains open only until the parent supplies its final files; it must not be treated as an approval of those unseen files.

## RESUME

Parent may consume E's canonical results_v2 with this independent receipt for conditional economic materiality, preserving all limiting labels. Supply final claim ledger, one-page decision summary and presentation defense to H for a short follow-up review; H will check that each conclusion stays within its source/forecast/economic evidence and that the strongest opposing interpretation remains visible. Wave 3 G separately signs the prospective implementation. No model, workbook, source, registry, scorer, card or investment decision was modified by this review.
