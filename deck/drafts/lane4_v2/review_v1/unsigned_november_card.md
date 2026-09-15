# Airbnb | Unsigned November review card

Status: UNSIGNED. No direction, target, probabilities or execution authority. Validation complete; free-weight promotion FAIL W1/W2; existing fixed 2/3 K0 seasonal policy retained. Verified source; current financial application ineligible: pre-hedge baseline and H/H_new missing. Q3 only; no Q4/Q1 extrapolation.

The inherited project event date is 5 November 2026; verify issuer schedule before use. Score after complete publications on 6 November. Preserve primary file/URL, page/table, units, precision, publication and extraction timestamps, and restatement version. Missing is ABSENT. Freeze any new pre-letter comparator separately; the September revenue consensus remains a historical comparator.

The fixed Q3 card denominator is (2*27200+29200)/3 = 27,866.666667 USDm. Warning 17.09% corresponds to 4,762.413333 USDm; escalation 16.93% to 4,717.826667 USDm. These are proposed diagnostic rules, not newly calibrated structural thresholds.

## L4v2-C01: 2026Q3 consolidated revenue conversion

**Units:** %

**Definition:** 100 * Q3 revenue USDm / 27866.666666666664; fixed card denominator (2*27200+29200)/3

**Reference:** warning 17.09%; escalation 16.93%

**Rule:** NO ALARM if lambda interval low>=17.09; WARN if low>=16.93 and high<17.09; ESCALATE if high<16.93; otherwise AMBIGUOUS; missing=ABSENT

**Source:** Q3 2026 shareholder letter/10-Q revenue; frozen F lambda_card_rule.json

**Precision:** Integer USDm revenue +/-0.5; denominator fixed by definition

**Standing:** UNSIGNED diagnostic; cannot identify RNPL cancellations

## L4v2-C02: 2026Q4 guide midpoint

**Units:** USD millions

**Definition:** Arithmetic mean of management's Q4 revenue guide endpoints

**Reference:** review_with_k 3123.419115173

**Rule:** Compare published guide midpoint and rounding interval with frozen own guide scenarios. Compare with explicit, dated guide expectations only if available. Revenue-consensus comparisons are separately labelled different-object diagnostics; never scored as guide surprise.

**Source:** Q3 letter Q4 guide; fixed L4 v2 scenarios. Explicit guide expectations unavailable at frozen 13 Sep 2026 snapshot.

**Precision:** Round each published endpoint by half its stated precision; midpoint extrema average endpoint extrema

**Standing:** UNSIGNED forecast comparison; no probability of beat/miss asserted

## L4v2-C03: 2026Q3 revenue

**Units:** USD millions

**Definition:** Reported consolidated revenue for quarter ended 30 September 2026

**Reference:** review_with_k 4808.362929494

**Rule:** Report observed interval minus each scenario. No guide hit awarded by comparing revenue with Q4 guide.

**Source:** Q3 letter/10-Q; L4 forecast snapshot

**Precision:** Whole USDm +/-0.5

**Standing:** UNSIGNED; current-quarter nights absent from two-lag revenue equation

## L4v2-C04: 2026Q3 take rate jointly with GBV

**Units:** %; USD millions

**Definition:** 100 * Q3 consolidated revenue / Q3 GBV; show both denominator and revenue

**Reference:** Inherited diagnostic 18.10% with GBV >=26300 USDm; adoption open

**Rule:** Apply ratio extrema using both rounding intervals; pair threshold only wholly met when TR low>=18.10 and GBV low>=26300. Crossing=AMBIGUOUS. Never a cover/reverse instruction.

**Source:** Q3 letter revenue and GBV; AGENT_BRIEF proposed joint diagnostic

**Precision:** Use precision of original units: USD billions to USDm before half-unit bounds; do not assume GBV exact

**Standing:** UNSIGNED candidate; cutoff not newly calibrated

## L4v2-C05: 2026Q3 reported ADR

**Units:** USD/night; percentage-point YoY

**Definition:** Company reported blended ADR and its year-over-year comparison with prior-year reported blended ADR

**Reference:** ADR v3 midpoint with-K 177.17; central scenario bounds [174.76,179.58]

**Rule:** Report point error and whether printed interval overlaps scenario band; band is RSS sensitivity, not a coverage-calibrated prediction interval. Preserve separate reported-dollar and integer-fair ex-FX target scores.

**Source:** Q3 letter ADR and FX/ex-FX disclosures; committed ADRv3 P card and S harness

**Precision:** ADR printed to cents +/-0.005 USD; whole-point ex-FX +/-0.5pp; respect explicit <1% intervals

**Standing:** UNSIGNED; ADR history n=10/9 differs from main W1/W2

## L4v2-C06: 2026Q4 nights guidance

**Units:** Exact quoted words; % only if disclosed

**Definition:** Management's prospective Q4 nights growth language, with full context

**Reference:** Record whether explicitly low double digit or stronger; do not translate a model's 10% into management words

**Rule:** Human classify exact quote as at_least_low / below_low / ambiguous; omitted=ABSENT. Quantified statement preserved as interval with stated precision.

**Source:** Q3 letter/earnings remarks; exact document/page/time

**Precision:** No invented numerical mapping for high single digit/low double digit

**Standing:** UNSIGNED input to proposed F conjunction

## L4v2-C07: Q3 UF growth less Q3 GBV growth

**Units:** percentage points YoY

**Definition:** 100*(UF26Q3/UF25Q3-1) - 100*(GBV26Q3/GBV25Q3-1)

**Reference:** Proposed F gap strictly above -8pp

**Rule:** Form ratio extrema for each growth series then difference extrema. Criterion holds only if entire gap interval >-8pp; crossing or equality=inconclusive; missing=ABSENT.

**Source:** Q3 2026/2025 comparative 10-Q UF balances and letter GBV

**Precision:** All four observations have their disclosed precision; use low current/high prior for growth minimum

**Standing:** Cleaner payment-timing diagnostic; not an identified RNPL exposure share

## L4v2-C08: Q3 funds payable growth

**Units:** % YoY

**Definition:** 100*(FP26Q3/FP25Q3-1); compare documented prior base 7209 USDm

**Reference:** Neutral descriptive band [5,11]%

**Rule:** Wholly inside=INSIDE; wholly below/above=BELOW/ABOVE; boundary crossing=AMBIGUOUS. Require translation/noncash reconciliation before any interpretation.

**Source:** Comparative 10-Q funds payable and cash-flow/accounting notes

**Precision:** Whole USDm balances +/-0.5 on numerator and denominator

**Standing:** UNSIGNED; inside band does not mean deferral on schedule

## L4v2-C09: Stated revenue FX and cohort FX

**Units:** pp YoY; USDm; dimensionless multiplier separately

**Definition:** Stated reported revenue FX contribution, its hedge wording, and separately labelled conditional L3 timing scenarios.

**Reference:** L3 source accepted; incremental FX remains unestimated. Source matches Q3 baseline only; Q4/Q1 cohort inputs absent.

**Rule:** Record stated contribution as a rounding interval. Require certified matching pre-hedge baseline R-H, signed baseline H and scenario H_new before R_new=m*(R-H)+H_new. No comparison against a missing central estimate and no full FX overlay on USD GBV.

**Source:** Q3 letter/10-Q FX and hedging disclosures; future versioned L3 adapter

**Precision:** Whole percentage contribution +/-0.5pp; no fabricated precision

**Standing:** INELIGIBLE FINANCIAL APPLICATION; null is not zero.

## L4v2-C10: Product-bundle contribution and cancellation language

**Units:** Exact words; pp if disclosed

**Definition:** Record bundle scope (RNPL, cancellation redesign, price display/fees) and any quantified nights/GBV/ADR contribution

**Reference:** No bundle component assumed to equal RNPL alone

**Rule:** Save exact statement with period/denominator. Omitted amount=ABSENT, not zero; a quantified bundle is not feature-specific causation.

**Source:** Q3 letter/earnings remarks; exact quotation and publication stamp

**Precision:** Stated numerical precision; preserve more than/approximately language

**Standing:** UNSIGNED descriptive evidence

## L4v2-C11: F combined proposed refutation condition

**Units:** Three observable conditions

**Definition:** ALL: lambda interval >=17.09%; UF-minus-GBV growth interval strictly >-8pp; explicit Q4 nights wording low double digit or stronger

**Reference:** ALPHA_F_RNPL.md single D-10 option; not adopted

**Rule:** All true=PROPOSED REFUTATION CONDITION MET; any missing=ABSENT; otherwise INCONCLUSIVE. Does not validate the opposite thesis, identify a causal RNPL effect or authorize a trade.

**Source:** C01/C06/C07 with primary publication fields

**Precision:** Inherit each input's conservative interval and exact quote review

**Standing:** UNSIGNED proposed thesis-condition only

## L4v2-C12: Explicit Q4 management-guide expectations

**Units:** USD millions; vendor/timestamp

**Definition:** A source explicitly forecasting management revenue-guide midpoint, distinct from analyst revenue estimate

**Reference:** UNAVAILABLE at frozen 13 Sep 2026 15:20 UTC snapshot

**Rule:** Keep ABSENT until direct source, object, horizon, vendor and pre-release timestamp are captured. S/(1+c) remains hypothetical, never observed consensus.

**Source:** Direct dated guide-expectations source if obtained

**Precision:** Source precision; no fabricated interval

**Standing:** UNSIGNED

