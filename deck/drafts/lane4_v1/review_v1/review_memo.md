# Airbnb | Forecast the guide, test the composition

Status: UNSIGNED | ABNB, Nasdaq Class A | USD | As of 2026-09-13; operating inputs 2026-09-11, consensus dates below. Fixed 2/3 K0 BENCHMARK; conversion-dependent claims are provisional pending L3 validation. FX/RNPL integration is separately pending. Direction, target and probabilities remain open.

**The benchmark operating review implies a Q4 guide of $3,123M**, $37.6M (1.19%) below captured LSEG-family revenue consensus. The same revenue at the inherited Q4 cushion implies $3,061M. This is conditional arithmetic; it does not establish a trading edge. [R]

## Operating inputs reach revenue with a lag

The review uses 146.8M Q3 nights x $177.17 ADR = $26.0086bn GBV. Revenue = lambda x [(2/3) prior-quarter GBV + (1/3) second-prior GBV]; guide = revenue / (1 + cushion). Imported Q4 lambda is 12.04037% and the trailing-eight median cushion is 1.79049%. Dollar contribution shares are 65.66% / 34.34%, not literal 2/3 and 1/3 revenue shares. Q3 nights affect Q4 revenue; Q4 nights first affect Q1 2027. [R]

## Main exhibit | Q4 guide and cushion sensitivity

| Conditional case | Q3 GBV $bn | Q4 revenue $m | Q4 guide $m | Gap to LSEG $m |
| --- | --- | --- | --- | --- |
| ADR v3 with-K / review | 26.009 | 3,179.3 | 3,123.4 | -37.6 |
| ADR v3 without-K | 25.966 | 3,175.9 | 3,120.1 | -41.0 |
| ADR residual reversion | 25.392 | 3,129.9 | 3,074.8 | -86.2 |
| K0 conditional ledger | 26.450 | 3,214.8 | 3,158.2 | -2.8 |
| Review / mean cushion | 26.009 | 3,179.3 | 3,121.4 | -39.6 |
| Review / legacy cushion | 26.009 | 3,179.3 | 3,060.6 | -100.4 |

Notes: LSEG-family $3,161.021M, 2026-09-13T15:20Z; S&P $3,160M, 2026-09-10; Zacks $3,200M, 2026-09-11. Yahoo/Alpha Vantage relays count as one LSEG-family panel. These are revenue consensus comparators, not explicit management-guide consensus. All rows are scenarios, not probability intervals. [R]

The older $3,059.4M H2-v3 guide reconciles to K0's $3,158.2M: changing Q3 GBV adds $32.58M, lambda $2.72M, and the cushion $63.53M in that order. The review uses its own ADRv3 operating block; numbers were not selected for their sign versus Street. [R]

**FX integration remains unresolved.** USD GBV already contains booking-period FX. L3 must supply verified cohort/currency weights and recognition timing before replacing the relevant FX component once. RNPL remains in total exposure; payment, FX fixing and recognition are distinct dates. No full FX factor or assumed zero hedge line is added. ADRv3's Q3 -0.43pp / Q4 +0.15pp ADR FX is already embedded and is not the revenue-FX contribution. [R, F]

Sources: [R] L4 revenue snapshot: forecast, operating_inputs, guide_reconciliation, sensitivity and consensus_comparison CSVs; [M] L4 model snapshot: scenario_summary, annual and valuation CSVs. Exact paths, information dates and SHA-256 hashes accompany this memo.

<!-- PAGEBREAK -->

# Valuation is conditional; adoption is open

**The review financial path produces $184.66/share at 16.5x FY27 adjusted EBITDA.** This uses FY27-end cash and diluted shares, a 31 December 2027 convention; it is not an adopted target. FY27 beyond the kernel-covered quarters inherits the model's growth, cost, cash and share assumptions. The +/-1% rows below test incremental revenue sensitivity; they are not L3 FX estimates or probability bounds. [M]

| Conditional case | FY27 rev $bn | Adj. EBITDA $bn | FCF $bn | Value $/share |
| --- | --- | --- | --- | --- |
| Operating review | 15.952 | 5.808 | 5.537 | 184.66 |
| K0 conditional ledger | 16.058 | 5.888 | 5.612 | 187.13 |
| -1% revenue sensitivity | 15.833 | 5.688 | 5.423 | 180.89 |
| +1% revenue sensitivity | 16.071 | 5.927 | 5.651 | 188.43 |

Notes: +/-1% applies to covered Q3/Q4 2026 and Q1 2027 revenue. FY27 Q3/Q4 inherit growth on the changed 2026 base; Q2 is unchanged. FCF = adjusted EBITDA + net interest - cash taxes + change in unearned fees + working-capital residual - capex. Review FY27 cash taxes are $542.4M, capex $47.9M; FCF after deducting SBC is $3,571.6M. These cash-flow assumptions are inherited. [M]

Reference per-share value = (16.5 x $5,807.5M EBITDA + $10,282.6M net cash) / 574.598M shares: EV $95,824.3M; equity $106,106.9M. Legacy arithmetic reproduces $180.88 for its EBITDA lens versus $156.79 for its six-lens mean, with an approximate September-2027 label using year-end balances. These are distinct objects. The unvalidated +0.48 growth/multiple relation is excluded. [M, V]

## Opposing evidence limits the conviction

A2 is PARTIAL: at letter-close vintages it matched guide-gap signs in 7/8 W1 and 6/7 W2 strong cases, but executable aligned 20-day excess returns averaged -0.308/-0.983pp; intervals cross zero. B2 FAILS its 70% revision hurdle (5/9 and 4/7); its unseasonal compounded-GBV LIVE values are excluded here. W2 is nested in W1. These findings cannot establish an actionable expectations edge. [E]

ADRv3's residual-carry rule passes its dollar target on n=10/9 windows, distinct from the main n=14/10 harness; its integer-fair ex-FX target does not pass both windows. Selection was post-hoc; the binding without-K jackknife margin is 0.011. Its 4.85pp residual remains unobserved. Reversion gives a $3,075M Q4 guide versus $3,158M for stronger K0 GBV, without assigned probabilities. [A, R]

## What would change the conclusion

At the November print, score conversion using 100 x Q3 revenue / 27,866.666667: warn below 17.09% and escalate below 16.93%, with whole-million rounding intervals. F's proposed refutation requires all three: lambda wholly at least 17.09%; UF growth less GBV growth wholly above -8pp; and explicit Q4 nights guidance of low double digit or stronger. Missing or crossing evidence remains absent/inconclusive. This is an unsigned condition, not a trade instruction or RNPL causal test. [F]

F's corrected stock history is 2.0/8.0/9.7pp; migration and RNPL revenue-cohort shares remain unidentified. The October 2 submission precedes the project-calendar November 5 catalyst and October 22-24 finals. Accepted L3 conversion and FX/RNPL inputs may change these provisional values. [F, R]

Sources: [A] docs/adrv3/SYNTHESIS.md (11 Sep 2026); [E] LANE2_MEMO_READY_CLAIMS.md (13 Sep); [F] ALPHA_F_RNPL.md and D_CARD_ADDENDUM_LAMBDA.md (13/12 Sep); [V] LANE1_MEMO_READY_CLAIMS_v2.md (13 Sep). [R/M] exact snapshot paths and SHA-256 ledger accompany the editable source. Evidence base: commit 1c87628cedbc94ab8a0e8552743c94485ef353b8. Scenario values carry no expected-return or probability claim.
