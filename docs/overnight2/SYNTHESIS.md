# Overnight run 11-12 Sep 2026: synthesis

- **Date:** 2026-09-11 (an earlier draft said 12 Sep). **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Branch:** `krish/overnight-2026-09-11` (worktree `../citadel-abnb-overnight2`), commits 9e6df17 (A), 90b7c73 (B), 7e1243e (C), b823005 (D). Not pushed. Nothing in the live model or on main was changed.
- **Read next:** the four notes under `research/notes/overnight2/`. Shared brief: `docs/overnight2/BRIEF.md`.

## 1. What changes for the 5 Nov trade

| Item | Before tonight | After tonight | Source |
|---|---|---|---|
| 3Q26 nights baseline | +9.9% (146.8mm), band 8.5-10.3 | unchanged | A, B, C, D all leave it |
| 4Q26 nights baseline | +8.9% (132.7mm), band 8.1-9.9 | **open question: 8.0-8.2% (131.7-131.9mm)** if the global October 2025 cancellation-redesign and single-fee legs are lapped ex-NA as PR #32 laps them in NA | D, point 5 |
| RNPL cancellation drag | unfitted -1.5 / -2.5 overlay in the old bridge | modelled both years: 3Q26 -0.10 to -1.37 pts, 4Q26 -0.08 to -1.36; central cell -0.15 to -0.93. The old overlay is reachable only at the corner of the grid | D, point 6 |
| Calendar reopening evidence for RNPL cancellations | Rome +4.3 pts, hypothesis open | Rome is idiosyncratic; London, Paris, Barcelona fall; non-US minus US +2.1 pts with permutation p 0.26, driven by Australia (opposite season) and fragile to one 29-listing market. **Weakens the hypothesis** | A |
| International RNPL rollout | undated, top open question | UK 18 Feb, Australia and APAC 23 Feb, Canada 4 Mar 2026; excluded by payment currency (BRL, INR, TRY). Ex-NA lap is 1Q27 and partial (5-6 of 13 weeks). PR #32's "NA only" 2025 cohort is really US only | D, point 2 |
| 4Q26 ADR FX | -0.7 pp (WS05 EUR-only fit) | **-0.7 to +1.0 pp** depending on estimator; the unfitted four-basket build says +1.0 because LatAm and APAC baskets are still +5 to +6% y/y. 3Q26: -1.1 to +0.3 | B, point 7 |
| 3Q26 / 4Q26 revenue FX | WS05 vintage 28 Aug | 3Q26 +2.2 pp gross / +2.0 after hedge (guide embeds ~+3.0 after hedge); 4Q26 -0.4 / -0.6. ~86% of the driver is observed FX | B, point 9 |
| Regional split 3Q26 (NA / EMEA / LatAm / APAC) | WS10 7 / 8 / 18 / 17 | C: 6.7 / 5.9 / 19.5 / 17.1 (+/-1.5); B's FX mix swing is -0.3 / +0.2 / +0.3 / -0.3 and nets to zero. Neither moves the total. EMEA-loser call in C rests on a wrong-signed fit and is a flag only | B, C |
| WS10 regional shares | LatAm 15.1%, APAC 16.3% | 10-K FY25: LatAm 16.9%, APAC 13.1%. Re-weighting WS10's own cells lowers its total 0.12-0.18 pp (3Q26 10.57, 4Q26 10.17) | C, point 6 |

## 2. Verdicts by workstream

**A. Calendar reopening, 34 markets.** Method frozen from the pilot; Austin, Rome and Sydney reproduce exactly on both python versions. Pre-registered result (non-US rise after 17 Feb larger than US) is not found at any conventional threshold, and the pieces that do move (Australia, San Diego, Barossa Valley) are the wrong places for a February treatment. Pre-rollout US level is higher than non-US, so the cross-section reflects composition. Short-run reclosure 33-41% per interval. Use this as evidence that the calendar proxy does not show an RNPL cancellation signature; it still cannot identify cancellations directly.

**B. FX relative strength to geographic mix.** Mix elasticity ~0.11 pp of regional differential per 1 pp of inbound purchasing power (n 28, perm p 0.04). At current spot it nets to nothing for total nights and -0.06 pp on ADR. The identified piece is US outbound at a two-quarter lag (r +0.89 on BEA); US inbound has the wrong sign because visa fee, tariffs and the Canadian boycott moved against the dollar in 2025-26. India, the fastest origin at +60%, has the worst corridor purchasing power, so FX is not what drives origin growth. Carry-forward: use booking-date FX (two-quarter lag), and state which ADR-FX estimator is in use.

**C. Consumer relative strength to regional split.** Clean index, 71 verified letter quotes in the target panel, but the fit has the wrong sign (stronger consumer, slower relative growth, t -3.4, n 28) and is almost certainly confounded by the RNPL/fee timing in NA and the LatAm comp. Not a leading indicator (lags insignificant). Missed NA both times. Standalone reading through Aug 2026: US consumer weakest of the large origins (-0.19 z), UK, Mexico, Korea, Japan strongest. Do not let it set a base case.

**D. RNPL ledger and cohort scenarios.** 60 dated statements, 57 verified verbatim. New facts: a 4Q25 bundle contribution of "over 200 bps nights / ~300 bps GBV" precedes the known 1Q26 ~3 pts / ~4 pts, and 2Q26 gave no figure, so whether it returns on 5 Nov is the most direct lap read. Payment falls due just before the free-cancellation window closes, so excess cancellations land in the stay quarter; 46-49% of any excess in 3Q26/4Q26 comes from earlier booking cohorts. One official forward-testable prediction: unearned fees higher y/y in 3Q26 (letter 1Q26). PR #32 and management agree on 1Q26 by construction; the 4Q25 figure is an out-of-sample check that pins the ex-NA fee-plus-cancellation share at 40-50% and opens the 4Q26 gap above.

## 3. Decisions for Krish

1. **Adopt or reject the 4Q26 ex-NA lap.** D's arithmetic moves the 4Q26 baseline from 8.9 to 8.0-8.2%. It rests on sourced dates plus one pinned split. If adopted, the Q4 guide arithmetic in the trade pivot note moves with it. Recommend adopting it as the base with 8.9 as the top of the band, and asking Jessie to check the 40-50% split against the backlog-conversion table.
2. **Retire the calendar-reopening line of attack for RNPL cancellations.** A ran the full 34-market version and it does not show the signature. Keep A's output as the answer to "did you check", and stop spending time on it.
3. **Pick one ADR-FX estimator for Q4 and say so in the model.** The 1.7 pp gap between the EUR-only fit and the basket build is larger than anything else in tonight's run for the Q4 ADR line.
4. **Fix WS10's regional shares to the 10-K** (LatAm 16.9, APAC 13.1) wherever WS10 cells feed the workbook. Small, but it is an error.
5. **Do not use the consumer index for the base case.** Keep it as a standalone macro backdrop line (US consumer weakest of the large origins).
6. **Score sheet for 5 Nov** is in D section 5 (nights growth, GBV-to-nights gap, unearned-fees y/y, whether the bundle contribution figure returns). Add it to the pre-registered card.

## 4. Side findings and open pulls

- `data/processed/overnight/06_fee_timeline.csv` on main attributes both single-fee penetration figures to letters; they are call-only (D).
- NTTO country-of-residence monthly files would replace judgement NA origin weights with measured ones (B). OECD travel-price CPI and consumer opinion endpoints 404'd; Canada and India confidence are proxied (C).
- FRED H.10 had published only to 4 Sep; "to 10 Sep" means 4 Sep plus flat spot (B).
- No 4Q26 macro month exists; C's 4Q26 split carries the 3Q26 reading with a wider band.
