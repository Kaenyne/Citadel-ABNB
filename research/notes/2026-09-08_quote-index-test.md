# Can a quote-based price index track disclosed regional ADR? No.

Krish with Claude Code, 8 Sep 2026. Script `analysis/src/adr/11_quote_index_test.py`;
outputs `data/processed/adr/11_quote_index_pairs.csv`, `11_quote_index_test.csv`.

## Why this was run

A proposal to collect Airbnb quotes at scale (agents browsing tens of thousands of listings)
to build a sub-regional ADR series. Before spending on collection: Inside Airbnb already holds
listing-level quotes for 34 markets, so build the best quote index the data allows and test
it against the regional constant-currency ADR y/y Airbnb discloses. Agents would collect the
same quantity (a quoted nightly rate), so if this fails, that fails.

## Two panels, five index constructions

Local-currency prices throughout, so the comparator is regional ADR ex-FX.

- **A. Same basis.** Both dumps carry the pre-Oct-2025 listed nightly rate and both are
  full-scope scrapes (`price_pair_eligible`). 13 pairs: Rome 4Q23-3Q25 (8), Paris 1Q25-2Q25,
  Austin 2Q25, Nashville 2Q25-3Q25. That is every clean year-over-year quote pair that exists.
- **B. Cross basis.** A 2025 listed-rate dump against the 2026 stay-quote dump ~12 months on,
  every market that has both: 47 pairs, 31 markets, four regions, 2Q26 and 3Q26.

Indices: matched-listing median (the repo's like-for-like), matched-listing nights-weighted,
nights-weighted arithmetic mean over all listings each dump (the closest analogue to ADR =
GBV / nights, composition included), the same in logs, and the unweighted mean (what a random
click sample gives). Weights are Inside Airbnb estimated nights booked, as in step 05.

## Result A: on a constant methodology, quotes do not track ADR

| pp y/y, entire homes | 4Q23 | 1Q24 | 2Q24 | 3Q24 | 4Q24 | 1Q25 | 2Q25 | 3Q25 |
|---|---|---|---|---|---|---|---|---|
| Rome, matched median | +9.3 | +12.5 | +5.0 | +2.2 | 0.0 | −7.5 | −5.0 | −5.7 |
| Rome, nights-weighted mean, all listings | +6.2 | +11.2 | +2.0 | +1.0 | −3.5 | −12.0 | −6.4 | −6.1 |
| **EMEA ADR ex-FX, disclosed** | **+6.0** | **+5.0** | **+4.6** | **+4.6** | **+6.0** | **+4.0** | **+3.0** | **+4.0** |

Paris 1Q25/2Q25: −4.2 / −1.0 (matched) against EMEA +4.0 / +3.0. Austin 2Q25 −3.9 and
Nashville 2Q25/3Q25 −7.7 / −10.9 against NA +3.3 / +5.0.

| 13 pairs vs disclosed regional ex-FX | r | p | MAE pp | bias pp | sign agreement |
|---|---|---|---|---|---|
| matched median | +0.51 | 0.08 | 7.3 | −5.6 | 31% |
| matched, nights-weighted | +0.48 | 0.10 | 8.3 | −5.3 | 31% |
| all listings, nights-weighted arithmetic | +0.33 | 0.27 | 7.9 | −6.1 | 38% |
| all listings, nights-weighted log | +0.41 | 0.16 | 7.6 | −6.0 | 38% |
| all listings, unweighted | +0.67 | 0.01 | 9.9 | −8.5 | 31% |

The one significant correlation is Rome's 2023-24 sequence, the tail of the post-reopening
decline, co-moving with EMEA's drift from +13.6% (1Q23) to +4.6%. On the eight 2025 pairs
alone every index has r between −0.75 and +0.34. Quotes have a standard deviation of 7-9pp
across the panel; disclosed regional ADR has 1.0pp. **The quote index said prices were falling
4-12% through 2025 in four cities while constant-currency ADR in their regions rose 3-5%.**
Whether that means listed rates lag realised rates, or realised ADR is mix while like-for-like
pricing really is negative, the index cannot be used as an ADR nowcast either way.

## Result B: the quote basis is not calibratable across the 2026 break

Same-listing y/y from 2025 listed rate to 2026 stay quote, matched median, entire homes:

| region | markets | mean | min | max |
|---|---|---|---|---|
| NA | 7 | +39% | +10 (NYC) | +62 (Nashville) |
| EMEA | 4 | +23% | +15 | +27 |
| LatAm | 4 | +47% | +31 | +69 (Rio) |
| APAC | 16 | +30% | −34 (Singapore) | +52 |

Against disclosed 2Q26 regional ex-FX of +6.8 / +5.0 / +2.0 / −1.4. The wedge is 20-70pp and
market-specific (Tokyo ~0, Singapore negative, Nashville +62), so it cannot be removed with a
constant fee factor. The raw 2026 quotes carry **no** service-fee, cleaning-fee or tax lines
(checked on six dumps; the `price_quote_raw` JSON has only `nightly_subtotal` and discount
items), so the wedge is date and stay-length selection in the quote, not fees. Restricting to
stays ≤7 nights and recovering the undiscounted nightly subtotal makes it larger, not
smaller (NA +60%). The repo's description of the 2026 basis as "fee-inclusive" is wrong for
these dumps; the conclusion that the bases cannot be compared stands.

## What this means for the proposal

1. A quote index built on a constant methodology across 13 clean pairs has no demonstrated
   power against disclosed regional ADR. Collecting more quotes by hand or by agent produces
   the same quantity with the same problem, plus a ToS and compliance problem.
2. Quotes do carry one thing ADR does not: the direction of asking rates on surviving
   listings. That is a supply-side pricing-behaviour signal, worth keeping as context (hosts
   cut listed rates through 2025 while ADR rose), not an ADR input.
3. Sub-regional ADR needs a realised-rate source: AirDNA / Transparent (calendar-inferred
   booked rates), or country-level nights to split the mix half of the unidentified line.
   See `research/notes/2026-09-07_adr-decomposition.md` section 3.

## Addendum: can the same data measure host repricing at the single-fee switch? Also no.

`analysis/src/adr/12_fee_migration_reprice.py`, `12_reprice_hist.csv`, `12_reprice_summary.csv`.
Sequential same-basis 2026 quote pairs (Mar-Aug), 105 pairs, 34 markets, matched listings,
undiscounted nightly subtotal on stays of 7 nights or fewer at both ends. If a host that
switches to the 15.5% fee reprices payout-neutral, the same-listing rate jumps ~+14.8% in one
window; with a quarter of listings switching between the 1Q26 and 2Q26 calls, the expected
excess mass in +12..+20pp is ~8% of listings per monthly pair.

Observed excess over the local baseline: 0.0-1.6% per pair, mean 0.4-0.7% by region.
Month-to-month stay quotes move more than 10% in either direction for a fifth to a quarter of
listings every month (different check-in dates each dump), so the noise floor is ~10% of
listings in the signature bins and a discrete reprice step is not recoverable from quotes.
Either switchers do not reprice as a step, or the switch dates do not line up with the dump
windows; the data cannot tell which.

**What the prints already bound.** ADR is gross of the guest fee, so a payout-neutral reprice
is +0.7% on the migrated cohort, no reprice is -12.3%, and the "+18.3%" advice is +3.8%. If
the ~25% of listings that switched during 1H26 had not repriced, ADR ex-FX would have lost
~3pp; instead NA accelerated to +6.3/+6.8. The no-reprice case is rejected by the prints, and
even full over-repricing on the remaining half is under +2pp of ADR. **Carry the migration in
the ADR forecast as +0.5pp with a -0.5/+1.5pp band on 4Q26 and 1Q27, and put the fee effect
where it actually lives, in take rate.** No tracker is needed for the ADR side.
