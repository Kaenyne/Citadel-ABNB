# ABNB | Unsigned November review card

Status: Review-ready, not signed. Direction, target, probabilities and formal adoption remain open. No score is a trading instruction. All conversion-dependent forecasts use the fixed 2/3 K0 BENCHMARK and are provisional pending L3 conversion validation. L3 FX/RNPL integration is a separate pending input. The fixed historical card denominator/thresholds do not silently change with a future conversion fit.

Fixed conversion denominator: 27866.666666666664 USDm. Warning 17.09% corresponds to 4762.413333333 USDm; escalation 16.93% to 4717.826666667 USDm. These exact percentage cutoffs control.

Capture protocol: record each primary file/URL, page/table, published units, precision, information timestamp, extraction timestamp and restatement version. Never fill missing evidence with zero. November 5 is the inherited project event date; verify the issuer calendar before use. Score on November 6 once the letter and 10-Q are available. Freeze any pre-letter consensus benchmark separately before release; keep the September snapshot as a historical review comparator.

## L4-C01 - 2026Q3 consolidated revenue conversion

**Units:** %

**Definition:** 100 * Q3 revenue USDm / 27866.666666666664; fixed card denominator (2*27200+29200)/3

**Reference:** warning 17.09%; escalation 16.93%

**Rule:** NO ALARM if lambda interval low>=17.09; WARN if low>=16.93 and high<17.09; ESCALATE if high<16.93; otherwise AMBIGUOUS; missing=ABSENT

**Source:** Q3 2026 shareholder letter/10-Q revenue; frozen F lambda_card_rule.json

**Precision:** Integer USDm revenue +/-0.5; denominator fixed by definition

**Standing:** UNSIGNED diagnostic; cannot identify RNPL cancellations

## L4-C02 - 2026Q4 guide midpoint

**Units:** USD millions

**Definition:** Arithmetic mean of management's Q4 revenue guide endpoints

**Reference:** review_with_k 3123.419115173

**Rule:** Report midpoint minus each frozen scenario; absolute and % error; endpoint-rounding interval versus forecast. No arbitrary hit tolerance. Score versus each vendor separately.

**Source:** Q3 letter: Q4 revenue guidance; L4 forecast snapshot; dated consensus snapshot

**Precision:** Round each published endpoint by half its stated precision; midpoint extrema average endpoint extrema

**Standing:** UNSIGNED forecast comparison; no probability of beat/miss asserted

## L4-C03 - 2026Q3 revenue

**Units:** USD millions

**Definition:** Reported consolidated revenue for quarter ended 30 September 2026

**Reference:** review_with_k 4808.362929494

**Rule:** Report observed interval minus each scenario. No guide hit awarded by comparing revenue with Q4 guide.

**Source:** Q3 letter/10-Q; L4 forecast snapshot

**Precision:** Whole USDm +/-0.5

**Standing:** UNSIGNED; current-quarter nights absent from two-lag revenue equation

## L4-C04 - 2026Q3 take rate jointly with GBV

**Units:** %; USD millions

**Definition:** 100 * Q3 consolidated revenue / Q3 GBV; show both denominator and revenue

**Reference:** Inherited diagnostic 18.10% with GBV >=26300 USDm; adoption open

**Rule:** Apply ratio extrema using both rounding intervals; pair threshold only wholly met when TR low>=18.10 and GBV low>=26300. Crossing=AMBIGUOUS. Never a cover/reverse instruction.

**Source:** Q3 letter revenue and GBV; AGENT_BRIEF proposed joint diagnostic

**Precision:** Use precision of original units: USD billions to USDm before half-unit bounds; do not assume GBV exact

**Standing:** UNSIGNED candidate; cutoff not newly calibrated

## L4-C05 - 2026Q3 reported ADR

**Units:** USD/night; percentage-point YoY

**Definition:** Company reported blended ADR and its like-for-like prior-year comparison

**Reference:** ADR v3 midpoint with-K 177.17; central scenario bounds [174.76,179.58]

**Rule:** Report point error and whether printed interval overlaps scenario band; band is RSS sensitivity, not a coverage-calibrated prediction interval. Preserve separate reported-dollar and integer-fair ex-FX target scores.

**Source:** Q3 letter ADR and FX/ex-FX disclosures; committed ADRv3 P card and S harness

**Precision:** ADR printed to cents +/-0.005 USD; whole-point ex-FX +/-0.5pp; respect explicit <1% intervals

**Standing:** UNSIGNED; ADR history n=10/9 differs from main W1/W2

## L4-C06 - 2026Q4 nights guidance

**Units:** Exact quoted words; % only if disclosed

**Definition:** Management's prospective Q4 nights growth language, with full context

**Reference:** Record whether explicitly low double digit or stronger; do not translate a model's 10% into management words

**Rule:** Human classify exact quote as at_least_low / below_low / ambiguous; omitted=ABSENT. Quantified statement preserved as interval with stated precision.

**Source:** Q3 letter/earnings remarks; exact document/page/time

**Precision:** No invented numerical mapping for high single digit/low double digit

**Standing:** UNSIGNED input to proposed F conjunction

## L4-C07 - Q3 UF growth less Q3 GBV growth

**Units:** percentage points YoY

**Definition:** 100*(UF26Q3/UF25Q3-1) - 100*(GBV26Q3/GBV25Q3-1)

**Reference:** Proposed F gap strictly above -8pp

**Rule:** Form ratio extrema for each growth series then difference extrema. Criterion holds only if entire gap interval >-8pp; crossing or equality=inconclusive; missing=ABSENT.

**Source:** Q3 2026/2025 comparative 10-Q UF balances and letter GBV

**Precision:** All four observations have their disclosed precision; use low current/high prior for growth minimum

**Standing:** Cleaner payment-timing diagnostic; not an identified RNPL exposure share

## L4-C08 - Q3 funds payable growth

**Units:** % YoY

**Definition:** 100*(FP26Q3/FP25Q3-1); compare documented prior base 7209 USDm

**Reference:** Neutral descriptive band [5,11]%

**Rule:** Wholly inside=INSIDE; wholly below/above=BELOW/ABOVE; boundary crossing=AMBIGUOUS. Require translation/noncash reconciliation before any interpretation.

**Source:** Comparative 10-Q funds payable and cash-flow/accounting notes

**Precision:** Whole USDm balances +/-0.5 on numerator and denominator

**Standing:** UNSIGNED; inside band does not mean deferral on schedule

## L4-C09 - Stated revenue FX and cohort FX

**Units:** pp YoY; USDm; dimensionless multiplier separately

**Definition:** Management's stated after-hedge revenue FX contribution versus L3 currency-timing output when accepted

**Reference:** L3 cohort recognition FX pending; no central value assigned

**Rule:** Record stated integer contribution as interval and hedge wording separately. No score against absent L3 estimate. Do not add full FX factor to USD-GBV revenue; do not equate contribution change with level multiplier.

**Source:** Q3 letter/10-Q FX and hedging disclosures; future versioned L3 adapter

**Precision:** Whole percentage contribution +/-0.5pp; no fabricated precision

**Standing:** PENDING INTEGRATION; baseline pending is not zero

## L4-C10 - Product-bundle contribution and cancellation language

**Units:** Exact words; pp if disclosed

**Definition:** Record bundle scope (RNPL, cancellation redesign, price display/fees) and any quantified nights/GBV/ADR contribution

**Reference:** No bundle component assumed to equal RNPL alone

**Rule:** Save exact statement with period/denominator. Omitted amount=ABSENT, not zero; a quantified bundle is not feature-specific causation.

**Source:** Q3 letter/earnings remarks; exact quotation and publication stamp

**Precision:** Stated numerical precision; preserve more than/approximately language

**Standing:** UNSIGNED descriptive evidence

## L4-C11 - F combined proposed refutation condition

**Units:** Three observable conditions

**Definition:** ALL: lambda interval >=17.09%; UF-minus-GBV growth interval strictly >-8pp; explicit Q4 nights wording low double digit or stronger

**Reference:** ALPHA_F_RNPL.md single D-10 option; not adopted

**Rule:** All true=PROPOSED REFUTATION CONDITION MET; any missing=ABSENT; otherwise INCONCLUSIVE. Does not validate the opposite thesis, identify a causal RNPL effect or authorize a trade.

**Source:** C01/C06/C07 with primary publication fields

**Precision:** Inherit each input's conservative interval and exact quote review

**Standing:** UNSIGNED proposed thesis-condition only

## Additional diagnostic limits

The corrected excess-unpaid history is 1.969114 / 8.047784 / 9.705899pp (Q4 2025 / Q1 2026 / Q2 2026), rounded 2.0 / 8.0 / 9.7. These are retrospective frozen-stock estimates, not prospective scoreable release items or measured RNPL cohort shares. A future reconstruction requires a new version using frozen K1 coefficients and documented allocations; the press release and 10-Q alone cannot supply that model stock.

Scoring implementation: `analysis/src/forecast_methods/lane4_review_v1/scoring.py`; full source hashes are in the accompanying input manifest. There are zero newly fitted parameters.
