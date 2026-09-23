# ADR line v2 — the thesis in ten sentences, and where it is strong and weak

22 September 2026. Built on `adr_v1_design.md` (FX identity, ex-FX mechanism), `adr_v2_geomix_prereg.md` (the
sub-regional term) and the four upgrade notes filed today: `adr_v2_upgrade1_eurostat_reweight.md`,
`adr_v2_upgrade2_origin_destination.md`, `adr_v2_upgrade3_reconciliation.md`,
`adr_v2_upgrade6_sustainability_and_score.md`. Figures: `figures/adr_geomix_logic.png` (the six-panel logic),
`figures/adr_full_logic.png` (the FX and ex-FX engine). Every number is reproducible with
`PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run` (27 tests).

## The thesis (ten sentences; sentences 3, 6 and 8 carry the statistical evidence)

1. Airbnb's reported ADR growth is the sum of a constant-currency rate and an FX translation effect, and both are
   disclosed every quarter, so the ADR line is built as an accounting identity rather than a regression.
2. The FX half is computed, not fitted: the 10-K GBV currency mix times the year-on-year change of the
   booking-quarter average exchange rate gives +0.42pp for 3Q26 with 88% of the quarter already printed and +0.51pp for
   4Q26 at held spot, against the committed card's −0.43pp.
3. **That identity, with zero fitted parameters, beats the naive carry point in time on all 17 quarters Airbnb has
   disclosed the effect: RMSE ratio 0.34 at day 60 and 0.30 pre-print on the 14-quarter window and 0.38 / 0.32 on the
   10-quarter window, with moving-block bootstrap 90% upper bounds of 0.44 to 0.51 against a pre-registered pass
   line of 0.75, and a fitted pass-through posterior (EMEA 1.20, 90% interval 1.09 to 1.31; Latin America 0.46,
   0.17 to 0.78) that explains its small misses without improving it out of sample.**
4. The constant-currency half decelerates from +4.0% to +3.3% in 3Q26 and +2.8% in 4Q26 because the three dated
   product effects management sized at about one point of ADR (US RNPL from August 2025, the cancellation redesign
   and single fee from October 2025) lap on their filed anniversaries, not because of any assumption on pricing.
5. Geographic mix is the second driver and it is now measured on two layers: between regions, the nights line's own
   regional path priced at the 10-K regional ADRs gives −1.3pp a year (one point of nights share moving from North
   America to Latin America costs 0.89pp of blended ADR); inside regions, country mix from 123 Inside Airbnb markets
   and USD price levels for 30 countries gives a further −0.15pp.
6. **The between-region term reconciles to the company's own accounting: annualised, ours is −1.10 / −1.33 / −1.67pp
   for 2023–25 against the 10-K's −1.08 / −1.24 / −1.58, within 0.02 to 0.09pp in each of three years from
   independent sources; pooled across the 23 disclosed constant-currency regional prints, the disclosed rate minus
   regional accommodation inflation regresses on our within-region mix with a slope of 1.13, but with four regional
   clusters no valid p-value exists (wild-cluster bootstrap p 0.89), three-quarters of Latin America's slope is the
   Brazil hotel-CPI comparator rather than Airbnb's own numbers (−0.30 without Latin America), and the earlier
   EMEA-only reading of 1.09 turns to −0.38 when two further disclosed quarters are admitted, so the quarterly scale
   is not established by anything Airbnb has published.**
7. The composition story management tells is real in the data but flatter than its letters imply: on 53 million
   reviews, non-English-origin guests grew 81% against 40% for English on day-matched windows from 2024 to 2026
   (English share 62.9 → 56.8% on those windows, and on the quarterly series the y/y drop has been flat at about
   2.9pp for four straight quarters after running faster earlier; cross-border Portuguese runs 11.9pp above its own
   scope where the filed Brazil-origin statement runs 14pp above company nights, the same excess within about 2pp),
   and within the same market a listing reviewed in a non-English language is 13% cheaper, so the
   origin rotation alone costs about 0.35% a year of the price of the listing booked; but the tourism-board origin
   flows (NTTO, JNTO, ABS, StatCan) put the Indian and Brazilian growth entirely outside North America yet imply an
   ex-NA split of EMEA 10.5 / LatAm 16.4 / APAC 14.9 rather than the letters' 8 / 20 / 18, so the steeper "tilt B"
   is retired.
8. **The origin-to-destination layer passes an ordering test against the disclosed regional buckets in 4 of 7
   quarters (binomial p 0.018; 4 of 5 on the quarters where the ordering is identified, p 0.003), the sub-regional
   term's construction reproduces the disclosed-share four-region term within 0.13pp on 2Q24–2Q26, and re-weighting
   Europe with Eurostat platform nights instead of panel shares moves France from 10% to 21% of EMEA yet changes the
   term by 0.02pp, so the conclusion does not rest on the scrape's footprint.**
9. Putting the pieces together, 3Q26 ADR is $177.68 (+3.7%, band $176.01 to $179.36) on a Street of $177.06 and
   4Q26 is $173.03 (+3.3%, band $169.80 to $176.27) on a Street of $171.33, with the full composition case at
   $172.79 to $173.19 and FY27 at $185.21 (+2.5%).
10. The defensible ADR claim is therefore shape, not level: ex-FX ADR decelerates by more than a point through
    4Q26 as the product effects lap and the incremental night keeps landing in $95–$159 regions, FX turns from a
    3–5pp tailwind to zero, and a below-Street 4Q26 ADR ($171.71 lap-only, $170.60 mean reversion) requires the
    unobserved core to give back its 2026 step, which we carry as a labelled scenario with its argument and its
    one-quarter error of 0.88pp, not as an engine output.

## Why a lodging analyst would call it strong

- The FX leg is the company's own accounting basis (booking-date GBV, prior-year rates, unhedged) validated at three
  point-in-time origins with a pre-registered pass line; there is nothing to fit and nothing to overfit.
- The mix terms tie to the 10-K three years running and to the EMEA disclosures quarter by quarter; the lever is
  explicit and the analyst can redo it on a napkin ($255 vs $95).
- Origins are measured with the analyst's own sources (NTTO, JNTO, ABS, StatCan) and the answer is reported even
  though it cuts against the steeper thesis.
- Every scenario that could move the number is on one ladder with its assumption named; the downside is not hidden
  in a band.
- The whole thing re-runs from raw stores in twenty seconds, has 27 tests, and has eight pass/fail lines written
  for 5 November and 11 February.

## Why the same analyst would call it weak (after the four mitigations of 22 Sep)

- The core like-for-like price (3.85pp) is carried, not explained, and the mitigations made the gap **larger**: with
  2025's size term adjudicated (the 10-K route's negative sign was a Paris-weighting artefact; the H route +0.74 is
  adopted, bracketed by the filed bedroom-nights metric at +0.42 to +1.29), 2025 like-for-like price was flat at 2.68
  to 2.93pp against 2024's 2.69 to 2.75, so the 2026 step is about 1.2pp on a flat base rather than the
  deceleration off a high 2025 the filed chain implied. The market-level panel (94 pairs, 92 markets) put
  the price-to-utilisation elasticity at +0.08 (p 0.79; cannot reject 0.32, rules out above 0.7), which buys at
  most 0.6pp of the core in the wrong direction for a give-back; the fix is a September-2026 capture wave against
  the September-2025 one, not more analysis.
- The bundle's one point of ADR is transcript-only, and that label is now exhaustive: the FY25 10-K, the 1Q26 and
  2Q26 10-Qs and both letters were read; no filing carries a magnitude; Airbnb did not even name RNPL in a filing
  until 2Q26.
- The sub-regional term is small and fading (−0.15pp), has no demonstrated forecast content (H2 failed), and the
  panel cannot see India, the Gulf or South-East Asia as destinations; the origin rotation is priced within
  markets (−0.35% a year) but from a single review vintage and a snapshot price.
- The quarterly reconciliation is not established: the pooled slope of 1.13 rests on Latin America, three-quarters of
  whose slope is the Brazil hotel-CPI comparator (Brazil alone, 24–33% coverage), and with four clusters no valid
  p-value exists (wild-cluster bootstrap p 0.89); the EMEA-only slope is window-dependent
  (1.09 on n 7, −0.38 on n 9); and the Eurostat-weighted and panel-weighted EMEA mix series correlate −0.30 quarter
  by quarter even though the sub-regional term moves 0.02pp between them.
- Composition, measured as far as the data allow, does not put 4Q26 ADR below the Street; a short that needs that
  is leaning on a core assumption, and the analyst will say so.

## What the mitigations closed and what they did not (22 Sep, notes `adr_v2_mitigation_A/B/C/D_*.md`)

Closed: the size-mix sign (DEC-0040 proposed: the annual decomposition carries the H route); the X3 open lead on
the 1Q26 10-Q (DEC-0041 proposed: "transcript-only" is exhaustive and stays); the "no price link" caveat on origin
(a within-market price by language exists and is used as an exhibit). Narrowed: the reconciliation's n (23 pooled
prints, slope compatible with 1, but one-region-dependent). Not closed: the core (needs a same-season capture
wave or realised rates); destination coverage (needs the Bright Data file or an extended capture, both Theo's
decisions).

## Proposed decisions (pending Theo)

DEC-0037: the four-region term stays on the letter buckets as base, with the measured origin-destination split as
its floor and tilt B retired. DEC-0038: the sub-regional term enters the workbook as a labelled attribution and
forward row (−0.15pp), not the base. DEC-0039: the eight score lines of `adr_v2_upgrade6_sustainability_and_score.md`
are the ADR line's falsifiers for 5 Nov and 11 Feb. DEC-0040: the annual decomposition carries the H size
route, which makes 2025 like-for-like price flat and the 2026 core step larger. DEC-0041: "transcript-only"
on the bundle's ~1pp is exhaustive and stays, closing the X3 lead and DEC-0031's digger question.
