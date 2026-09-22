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
   independent sources, and in EMEA the disclosed constant-currency ADR minus panel-weighted accommodation inflation
   regresses on our within-region mix with a slope of 1.09 where the identity implies 1.0 (r 0.48, n 7, p 0.27, so
   the sign and scale are right and the sample is too small to call it significant).**
7. The composition story management tells is real in the data but flatter than its letters imply: reviewer language
   shows English falling from 71% to 58% of panel reviews since 2022 with Spanish, Portuguese and other origins
   growing 37 to 45% in 2025 against 17% for English, while the tourism-board origin flows (NTTO, JNTO, ABS, StatCan)
   put the Indian and Brazilian growth entirely outside North America yet imply an ex-NA split of EMEA 10.5 / LatAm
   16.4 / APAC 14.9 rather than the letters' 8 / 20 / 18, so the steeper "tilt B" is retired.
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

## Why the same analyst would call it weak

- The core like-for-like price (3.85pp, 1.45pp above its 2023–25 mean) is carried, not explained; the
  supply-utilisation test failed its line and the sub-regional term explains only 0.2pp of the 2026 step.
- The bundle's one point of ADR is transcript-only; no filing carries it, and its split into legs is assumed from
  the residual's own steps.
- The sub-regional term is small and fading (−0.15pp), it has no demonstrated forecast content (H2 failed), and the
  panel cannot see India, the Gulf or South-East Asia as destinations.
- The reconciliation samples are n 7 to 10 and the EMEA slope is not significant; the 10-K annual route and the H
  route disagree on the 2025 size-mix sign by a full point.
- Composition, measured as far as the data allow, does not put 4Q26 ADR below the Street; a short that needs that
  is leaning on a core assumption, and the analyst will say so.

## Proposed decisions (pending Theo)

DEC-0037: the four-region term stays on the letter buckets as base, with the measured origin-destination split as
its floor and tilt B retired. DEC-0038: the sub-regional term enters the workbook as a labelled attribution and
forward row (−0.15pp), not the base. DEC-0039: the eight score lines of `adr_v2_upgrade6_sustainability_and_score.md`
are the ADR line's falsifiers for 5 Nov and 11 Feb.
