# Memo v4.2: Krish's review of v4.1 (29 Sep 2026)

Built on v4.1 (`deck/drafts/memo_v4_1_2026-09-29/`, unchanged). The page fit was checked in Microsoft Word with Aptos: 2 pages,
with page 2 ending at 750pt of 756pt. **There is no slack**, so any addition needs an equal cut.

## Rebuild, from the repo root

```
Rscript analysis/src/pitch_charts_pm/graph1_history.R          # Graph 1 (unchanged from v4.1)
Rscript analysis/src/pitch_charts_pm/graph2_triangulation.R    # Graph 2 (new)
python analysis/src/pitch_charts_pm/compose_v4_1.py            # Graph 1 caption
python analysis/src/pitch_charts_pm/compose_v4_2.py            # Graph 2 and 3 captions
NODE_PATH=<dir with node_modules/docx> node deck/drafts/memo_v4_2_2026-09-29/build_memo.js
```

## What changed, against the review points

| Review point | v4.2 |
|---|---|
| "Why the market is wrong" is too long; don't cite vendors | Merged with the setup into one paragraph, "The setup, and why the Street is wrong". The text no longer names a data vendor (the chart source lines still do). |
| Thesis, setup and market-wrong repeat each other | The headline numbers (+9.2 vs +11.5, FY27 revenue and EBITDA, the catalyst dates) now appear only in the thesis. The setup carries the history, the bundle, 19 guide beats, the FY27 nights +8.9% vs +6.4%, and the 23 Sep sell-off. The FX 3–4pts sentence was dropped from the setup; FX stays in the thesis and the illusion paragraph. |
| Graph 2 looks weakly calibrated | Replaced. The new Graph 2 (`graph2_triangulation.R`) has two panels. The left shows 3Q26 nights by route (stays index 8.9 ± 1.9, twelve external series 9.2, regional build 9.9, our model 9.2) against the Street's range of 28 estimates (+10.0% to +13.0%, mean 11.5). The right shows ADR, ours vs the Street, for 3Q26 and 4Q26. The backtest result (about 0.7x naive) stays in the text. |
| Margins graph dropped; margins under-covered | Graph 3 is back: the team's model v2 margin bridge, floated beside a full margins paragraph. The paragraph covers the Street's 15.0% → 9.7% cost-growth ask; S&M (16.5% → 19.4% of revenue, nine quarters outgrowing revenue, $6.6 → $2.7 of revenue per extra dollar); AI ($17M of savings vs S&M +$184M, hosting and AI compute $224M → $330M, "reinvest most", "a material increase" in AI spend); our margins vs the Street in 3Q26, 4Q26 and FY27; and the flexed Street plan below the 35.5% floor. |
| First mitigant far too long | Cut to 2 lines. The AI-savings evidence moved to the margins paragraph. |
| Growth-company and risks bullets take space | Both are prose now. The risks are one paragraph with (1)–(4). |
| Add nowcast methodology | The nowcast paragraph now explains why reviews measure completed stays; how the 15–16% annual deletion is cancelled (same-age comparison across two snapshots); regional weighting by stay-quarter share; the pre-RNPL two-parameter mapping (1Q23–2Q25); the backtest; and the two cross-check routes. |
| ADR dropped | New paragraph, "Price does not rescue it": 3Q26 $175.66 vs $177.06, the FX leg (−0.4pt), ex-FX slowing from +4.0% to ~+1% by 1Q27 (bundle lap, pricing reversion, mix −1.6pt), and 4Q26 roughly in line ($170.96 vs $171.33). |

## Wording checks

- **Stays-index weighting.** The text says cities are rolled up "to Airbnb's four regions, weighted by each region's share of
  stays that quarter". That is v2.1's stay-quarter mix (`REVIEWS_INDEX_v2.md` §5), not city nights shares.
- **ADR, 3Q26.** Under the straight-translation FX leg, the Street's implied ex-FX equals ours, so the whole 3Q26 ADR gap is FX
  (thesis 2 draft). The memo says "our FX estimate… makes FX a −0.4pt drag". It does **not** claim the Street misses length of stay or mix.
- **ADR, 4Q26.** The memo says "roughly in line". It makes no 4Q26 price-miss claim.
- **Regional build (+9.9%).** This is the team's pre-v2 base (DEC-0029, `stage_e_view_vs_street.csv`). It is independent of the
  reviews, but it is an older team estimate, not a new route. If a judge asks, it is the build from North America vs the rest of the world.
- **The stays-index band overlaps the Street's low end.** Its upper end (10.8) is above the lowest estimate (10.0). The chart shows
  this, which is honest. "Every route lands below the lowest Street estimate" refers to the point reads.

## Still open (carried from v4.1)

1. The Bloomberg FY27 nights (+8.9%) pull date.
2. SI 3.59% has no source.
3. Re-stamp the price.
4. The 3Q26 underlying 7.8% bar in Graph 1.

## RESUME

Open the .docx in Word and confirm 2 pages. With no slack on page 2, any addition needs a cut; the Macro sentence at the end of
the growth-company paragraph is first to go. The open items above are the team's calls.
