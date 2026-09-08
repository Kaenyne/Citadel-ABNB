# Blotnick's 13 "Levels of the Game" Applied to Airbnb (ABNB)

*Prepared 2026-09-07. Source text: Gregory Blotnick post, 27 Aug 2026 (`research/blotnick_post_fulltext.md`). Template: the Signet audit in `research/blotnick_framework_sig.md`. ABNB $181.94 (4 Sep 2026 close); Q3 2026 print 5 Nov 2026. This is a synthesis of the existing corpus (the overnight notes `research/notes/overnight/01-28`, the predictive study, the margin-drivers note, the earnings-call study, the regulatory profile) plus targeted greps. No new external research.*

**Why this matters.** Blotnick's list is a catalogue of how retail comps, guides and alt data mislead sophisticated investors. Airbnb is not a retailer: it has no stores, no inventory it owns, no cost of goods, and its revenue is a ~13% slice of a gross booking value it does not keep. So most of the 13 points do not apply literally. But almost every one has a marketplace twin, and in several cases the twin is *more* dangerous than the retail original because the disclosure is thinner. The audit below runs each point through the same gates as the Signet version: what it means, whether the dynamic exists at ABNB, what our data says, what is on the record, and which way it cuts. The pitch direction is not yet decided (`research/thesis.md` is a blank template), so verdicts are stated as **which side the trap cuts for** and what we should do about it, rather than "safer/riskier for the long".

**The translation key**, used throughout:

| Blotnick's retail object | Airbnb twin |
|---|---|
| Same-store sales (SSS%) | Nights and Seats Booked growth; GBV growth |
| Gross margin % | Implied take rate (revenue / GBV) and Adjusted EBITDA margin |
| Promo / markdown | Brand and performance marketing; customer incentives (hotel credits, price match); Reserve Now Pay Later; cancellation-policy loosening |
| Comp base | KPI definitions, disclosure set, regional buckets, listing purges |
| Store vs e-com blend | Regional blend; homes vs hotels vs seats inside one "nights" number |
| BOPIS / returns | Booking-date KPIs vs check-in-date revenue; cancellations netted from later GBV |
| Franchise conversions | Hotels and other new supply types entering the base |
| 2H guide | The Q4 2026 and FY27 guide, where the FX and product laps land |
| Aging inventory | Booked-not-stayed backlog (unearned fees, funds held); listing quality; AI hosting commitments |
| Wholesale vs DTC shift | Core vs expansion markets; homes vs hotels/services; split fee vs single fee vs direct-link fee |
| Loyalty / gift card / credit accounting | Unearned fees, float interest, contra-revenue incentives, hedge gains in revenue, Adjusted EBITDA add-backs |

---

## 1. "Alt data QTD SSS% is often more accurate than mgmt SSS% est, so 3D chess becomes 'will mgmt lie,' and/or imply in their SSS% guide some sequential accel due to a new product intro"

**TRANSLATION.** Intra-quarter alt data can beat the guide. The higher game is credibility: is the guide honest, and does it quietly embed an acceleration the trend does not support?

**ABNB APPLICATION: the premise is inverted, and the credibility test splits cleanly by metric.**

*The guide beats the alt data, not the other way round.* Airbnb has beaten its own quarterly revenue midpoint **19 of 19** times and finished above the *top* of the range 15 of 19 (mean beat +2.54%, trailing-eight +1.86%; the range itself has tightened from 4.9% to 1.9% of the midpoint, `02_kpi-panel-and-guidance-ledger.md`). The full-year margin floor has been cleared every year it has existed (FY24 35% floor, 36.4% actual; FY25 34.5%, 35.1%) and the full-year guide has only ever been raised, never cut. Meanwhile our own alt-data layer, tested across **598 feature-target-window cells** (Google Trends, XBRL backlog, Eurostat platform nights, a 13-city Inside Airbnb panel), produced nothing that beats an AR(1) on both evaluation windows (`08_altdata-index-and-backtests.md`, `15_red-team.md` CONF-07). Google Trends alone: 432 tests, zero of 162 pairs beat naive on the full window; Airbnb's share of search fell 5.7 points over two years while nights growth *rose*. So "will management lie" resolves the same way it did at Signet: the guide is a floor, the sandbag is measurable, and the guide-plus-cushion is the best revenue forecast we own (mean error 1.1%).

*But the credibility test fails on exactly the lines a marketplace model cares about.* The guides that have missed are the monetisation and expense lines, not volume: the FY25 take-rate guide of +20bp delivered **−16bp** (a 36bp miss, never revisited); the 1Q26 "modest upside to our take rate" was walked back to "relatively flat" within one quarter; FY24 SBC guided +20% then +25%, delivered +30.8%; FY24 marketing "largely the same % of revenue" missed by 150bp and the line has risen every year since (`03_management-language-and-stock.md` §4). The scorecard of 83 forward claims: next-quarter 80% hit, full-year 73%, **multi-year 26%**; quantified 82%, unquantified 49%; CFO 69%, **CEO 42%**; pricing/affordability **0 for 7**.

*The embedded-acceleration test for 3Q26.* The guide moves nights from +10.3% (2Q26) to "low double-digit" and revenue to +15-17% with "approximately three points" of FX. Three things are embedded: (a) the FX point is hedges plus check-in lag, not spot (the revenue-weighted spot basket is +0.32% y/y QTD, `10_regional-and-segment-decomposition.md` §6); (b) the guide is reproduced exactly by nights +11%, ADR +4.05% and a zero revenue-minus-GBV gap, so it assumes the favourable 2Q26 timing gap persists (`08` §8); (c) it is set against the first RNPL anniversary (US launch 3Q25) which management itself called "tougher comps in the back half". None of that is a lie; all of it is a coherent guide leaning on timing rather than demand. The World Cup is *not* an embedded acceleration for nights: the bookings landed in 2Q26 and the stays in 2Q/3Q26, so 3Q26 nights get little lift (`10` §5).

**WHAT OTHERS SAY.** Sell-side tone tracks the second derivative of nights, not the level: harshest in record 2022-23 quarters when growth decelerated (3-4/10), friendliest in 2026 at 9-10% growth that was accelerating (7-8/10) (`airbnb_earnings_call_study.md` §5). 2Q26 had **15 analyst questions from 12 analysts, both record lows**, on a print that moved the stock +17.4%. Nobody is pressing the guide.

**VERDICT: cuts for the bull on revenue and margin, for the bear on take rate. Posture: quote the cushion, discount every take-rate sentence.** Model next-quarter revenue at midpoint × (1 + ~1.8%). Treat any take-rate or SBC guide as directional at best. **5 Nov check:** whether the Q4 revenue guide implies ≥+14% y/y with the FX assumption quantified; the base-rate expectation is a Q4 guide of +11-13% against a Street at $3.20bn (+15.2%), which is the "guide below Street" setup (see #3).

---

## 2. "Knowing which retailers have a high % of cash transactions (thus tanking RSQ on cc/alt data)"

**TRANSLATION.** Card panels only see card rails. Where a big slice of the business is off-panel, the panel-to-reported regression collapses.

**ABNB APPLICATION: we hold no card-panel data, and the structural reasons a panel would mislead on Airbnb are worth stating before anyone shows us one.** The data census lists card panel, app downloads, web traffic and AirDNA as "identified in the Crossover access map, none captured" (`01_data-census.md` D201-D205); the terminal guide flags Bloomberg ALTD (Consumer Edge, Earnest, Second Measure, Yipit) as "availability depends on UF's entitlements". So this point is a pre-emptive concession, not an exhibit. Five blind spots, in order of size:

1. **Geography.** US revenue is **39.3%** of the total (FY25 10-K, down from 50.0% in 2021) and every incremental market is non-USD. A US card panel sees under 40% of the business, and the 40% it sees is the slowest-growing region (NA revenue +3.8% FY25).
2. **RNPL moved the charge date.** Airbnb is merchant of record, so a panel sees the guest's full charge on the day the card is charged. Until 3Q25 that was the booking date, so panel spend mapped onto GBV. Reserve Now Pay Later (>20% of GBV, ~70% adoption where eligible) defers the charge toward check-in. The same product change that killed unearned fees as a leading indicator (−0.9% y/y at 2Q26 against GBV +16%, `2026-09-05_what-theos-alt-data-shows.md`) breaks the panel-to-GBV mapping in the same quarter, and a vendor whose panel history is calibrated pre-RNPL will under-read bookings exactly as our funds-held model under-predicted 1Q26 and 2Q26 by 3.4pp and 2.8pp.
3. **The panel sees GBV, not revenue.** A guest charge is host payout plus cleaning fee plus taxes plus Airbnb's fee. Airbnb's revenue is ~13% of it, and the take rate is the swing variable (see #11). A panel can be right on spend and wrong on revenue by the whole take-rate story.
4. **Revenue is recognised at check-in.** Even a perfect spend read leads reported revenue by one to two quarters (the same lag that makes revenue FX trail spot; `05_macro-outlook-and-transmission.md`).
5. **Off-card rails.** Third-party instalments (Mexico interest-free instalments from June 2026), gift cards, and local payment methods in LatAm and APAC, the two regions delivering 52% of nights growth.

**WHAT OTHERS SAY.** No analyst note in the pitch catalogue (`2026-09-04_abnb-pitch-catalogue.md`, 37 rows) cites a card panel as its primary evidence on ABNB; the nights number the Street trades is the StreetAccount consensus, not a panel read.

**VERDICT: neutral, and a differentiator if stated first. Posture:** one line in the deck: *"US card panels see under 40% of Airbnb's revenue, on the wrong date since Reserve Now Pay Later, and measure gross bookings rather than the 13% Airbnb keeps. That is why our checks are the guidance cushion, the FX schedule and the balance-sheet backlog, not a spend panel."* If Bloomberg ALTD becomes available, use it for **Airbnb vs Booking/Expedia US share** and guest demographics only, never for a nights nowcast.

---

## 3. "Mgmt will buy the comp, so you have SSS% upside + GM% downside forecasted with confidence, but what you don't know is how the stock will react even if your numbers are 100% accurate"

**TRANSLATION.** Management can trade margin for volume; the beat-and-margin-miss is predictable; the reaction is not.

**ABNB APPLICATION: both halves are documented at scale, and the second half is the best-evidenced negative result in the whole repo.**

*Buying the comp, marketplace version.* Since 2Q22 revenue per night rose $4.04 and cash cost per night rose $2.44; **$2.08 of that $2.44, 85%, is sales and marketing** (`07_ops-and-margin-levers.md` §2.1). Brand and performance marketing ran **+32% in 1H26** against revenue +17%, field operations +24%; GAAP S&M has gone from 18.0% of revenue (2Q22) to 24.3% (2Q26). "Roughly 90% of our traffic is direct or unpaid" has been said on five calls and cannot be true as an efficiency claim alongside those numbers (`07` §3). The second lever is incentives: price match and up to 15% Airbnb credit on featured hotels, funded by Airbnb and booked as contra-revenue, which is why the 2026 take rate is guided flat "accounting for higher customer incentives related to new businesses" despite a 15.5% single fee, an FX fee and insurance revenue growing 60%. The third is product: RNPL, looser cancellation policies and the fee migration were credited by management with ~2pt of nights and ~3pt of GBV in 4Q25 and ~3/~4 in 1Q26, and RNPL raised the platform cancellation rate from ~16% to ~17%. So the ABNB form of "SSS upside + GM downside" is **nights upside + take-rate flat + S&M deleverage**, and it is already in the numbers: FY25 margin fell on take rate (−16bp, −0.8 margin points) plus S&M (−1.9 points), covered by ADR ex-FX (`2026-09-05_margin-drivers.md` §10).

*The reaction is unknowable, with receipts.* Across three independent workstreams and roughly 150 specifications: no day-1 regressor has a positive leave-one-out R² (beat vs guide, beat vs consensus, guide vs Street, nights surprise, EPS surprise, margin guide direction, FY guide action, call tone), and the revenue beat's sign hit rate on day 1 is **0.37, below a coin flip** (`02` §4, `04_consensus-and-reaction.md`, `03` §2). The one result that looked real, nights-vs-Street forecasting the 20-day drift (LOO +0.13, n 18), went to **−0.016** once the return window starts at the first executable price (`20_temporal-validation.md`). 73% of the historical day-1 "signal" is the overnight gap. The mean absolute day-1 move is 7.1%, 10 of 23 prints moved ≥8%, and the option market's event premium is currently **not identified** (`23_options-estimator-fix.md`). The worked examples are Blotnick's point exactly: 2Q24 record nights, −12.3% on a lead-time sentence that did not verify; 4Q24 revenue guide *below* Street, +14.0% on a nights beat; 2Q25 revenue and EPS beat, −8.4% on a "tougher comps" sentence after which nights accelerated for three quarters.

**WHAT OTHERS SAY.** Eight of the ten largest reactions were driven by a sentence in the letter or a scripted guide paragraph, not the reported quarter (`03` §3). The stock went from 13.3x to 18.2x forward EBITDA in 2026 and **84% of the +17.4% on the 2Q26 print was multiple, not estimates** (`12_valuation-multiple-regime.md`).

**VERDICT: cuts for the bear on quality of growth, neutral on the print. Posture: never build the pitch on a print call; build it on what the marketing line does when the cycle turns.** The FINAL_SUMMARY line stands: *"the single most informative line in the release is brand-and-performance marketing"*. Above +28% for the year and the FY margin lands at the 35.5% floor; below +20% and the reinvestment cycle is easing. **5 Nov check:** brand and performance marketing y/y in the 10-Q split table; support cost per booking against −16%; whether the Q4 guide sits below $3.20bn (all nine prior guide-below-Street prints had a negative 20-day excess return, mean −4.2% on an executable entry, base-rate p 0.038, n 9).

---

## 4. "Mgmt juicing qtr-end SSS% thru some 1Q promo where expenses won't hit til 2Q ('exit rate accel'), alt data rips into q-end even though promos/cannibalization are 1-2 q's away"

**TRANSLATION.** End-of-quarter stimulus inflates the exit rate; the bill arrives a quarter or two later; the data reads the sugar high as momentum.

**ABNB APPLICATION: this is Reserve Now Pay Later, described in Blotnick's grammar.** RNPL is a booking-date stimulus whose costs land in later quarters:

- **Bookings pulled forward.** Zero due at booking removes the conversion barrier and lengthens lead times ("locking in earlier calendar share"); management said the tested lift was measured "net of cancellations", but the platform cancellation rate still rose about a point.
- **The cost lands later, in three places.** (i) GBV is *net of cancellations in the period they occur*, so bookings made in Q1 and cancelled in Q2/Q3 depress later GBV and ADR; (ii) unearned fees and funds held under-state the backlog, so the balance-sheet check that would catch a soft quarter is blinded (#10); (iii) the anniversary: US launch start of 3Q25, up-funnel merchandising 4Q25, global 1Q26. **The laps are 3Q26, 4Q26 and 1Q27, in that order**, and management flagged the first one on the 1Q26 call.
- **Attribution went diffuse on schedule.** 4Q25 and 1Q26 quantified the three-feature lift; 2Q26 became "no single product, an AI-native company" as the quantified drivers approached their anniversaries (`airbnb_earnings_call_study.md` §7). That is the retail pattern of a promo-led exit rate being re-described as brand strength.

The second, smaller instance is the letter's own QTD language. The 2Q26 letter raised FY26 "supported by the accelerated pace of Nights and Seats Booked we've observed", i.e. an exit-rate sentence, and it was the sentence that drove the +16.3% excess return. History says those sentences are usually right at the next-quarter horizon (80%) and usually wrong beyond it (26%).

**DATA NEEDED.** There is no promo scrape equivalent. The closest checkable series are: the funds-held-minus-GBV growth gap (5.2pp at 2Q26, from 3.8pp a year earlier; if it widens again the pull-forward is still ramping, if it narrows while revenue holds the ramp is done, `08` §12); the disclosed cancellation rate; and the NA nights bucket against the RNPL anniversary (the bear case for 3Q26 NA is a slip from high-single back to mid-single, `10` §7).

**WHAT OTHERS SAY.** Deutsche Bank called RNPL "the largest near-term upside driver"; the bull-bear line in the pitch landscape is precisely "structural vs borrowed reacceleration" with the bears attributing 2-4 points to the three features and ~3 points to FX (`2026-09-04_abnb-pitch-landscape.md` §111). Chesky now calls AI host pricing "many multiples bigger than RNPL", which is the next unquantified stimulus.

**VERDICT: cuts for the bear on FY27 nights, and it is the cleanest Blotnick trap at ABNB because management dated it themselves. Posture:** do not carry the full 3 points out of the FY27 nights path as "RNPL" (it was three features; `15` CONF-12), but do model a decelerating nights path through 1Q27 and say why. **5 Nov check:** NA nights bucket, any cancellation-rate disclosure, and whether management re-quantifies the three-feature contribution or lets it disappear.

---

## 5. "Mgmt's ability to play games with the comp base (impossible to forecast as minority shareholder), ditto remodels, relos, expansions, or excluding one-off weather/disruption events"

**TRANSLATION.** The comp base is management's sandbox: redefinitions, additions, exclusions and one-off carve-outs flatter the headline in ways outsiders cannot model.

**ABNB APPLICATION: the most on-point trap after #4, and the ledger of it is already built.** `02_disclosure_changes.csv` (23 items) shows a one-way pattern: **the company stopped giving each mix metric as it turned less flattering, and replaced exact regional growth with buckets.**

| Move | When | Effect |
|---|---|---|
| Cross-border share and growth dropped | last given 1Q24 (46%) | the mix series that had been decelerating goes dark |
| High-density urban share dropped | last given 4Q23 (51%) | same |
| Long-term-stay (28+) share dropped | last given 1Q24 (17%, from 24%) | the "live anywhere" thesis exits without comment |
| Active listings growth % dropped | last given 1Q24 (15-19% in 2022-24) | replaced by "over 8 million", then "in line with nights" from 1Q25 |
| Regional exact % → buckets | from 4Q24 | "mid-single digit" for all four regions; no quarter has a hard number for all four |
| China domestic listings removed | 3Q22 | supply growth quoted ex-China thereafter |
| **Nights and Experiences → Nights and Seats Booked** | 2Q25 | seats bundled into the core volume KPI; Mertz, asked directly: "seats booked today are indeed immaterial" (`2026-09-05_transcript-analytics.md`) |
| **Bedroom Nights Booked introduced** | 2Q26 | a new metric growing +12% against nights +10%, introduced in the quarter it flattered |
| 550,000+ low-quality listings removed since 2023 | ongoing | base quality improves; nights per listing "flat within rounding" |

The one-off carve-outs are the same species as Signet's weather line: Easter and leap day (~3 points to 1Q24 revenue growth, reversed in 2Q24 and 1Q25); the Middle East conflict ("grew 9% after accounting for an approximate 100-basis-point headwind", 1Q26); the Paris Games (3Q24 "buoyed", 3Q25 "unfavourable comparison"); and every number given "ex-FX". None is wrong. All are offered on the flattering side of the ledger and never on the other.

The difference from Blotnick's "impossible to forecast" version: at Signet the changes were quantified to the basis point; at Airbnb **the changes are not quantified at all**, they are silences. That makes the disclosure regression more, not less, of a judge's question.

**WHAT OTHERS SAY.** Morgan Stanley's bear work anchors on listings deceleration precisely because the company stopped disclosing it (`2026-09-04_abnb-pitch-landscape.md`). One analyst (Barclays, 2Q25) asked the seats-share question and got "immaterial". Nobody has pressed the bedroom-nights introduction.

**VERDICT: cuts for the bear on transparency, and is neutral-to-bull on substance (the surviving KPIs are clean; the KPI panel cross-checks against XBRL with zero restatements). Posture: own it on one slide.** List the five dropped series with last values and dates, note that our regional build reconciles to reported total nights within 1.1pp using the buckets (`10` §2), and quote bedroom nights *with* nights, never instead of them. **5 Nov check:** whether any further series goes dark (first-time bookers and app share are the current candidates), and whether hotels finally get a number (#8).

---

## 6. "Mgmt's ability to play games with omni + ecom in triangulating consolidated SSS%: stores soft, ecom strong, report 'blended comp' with minimal disclosure otherwise"

**TRANSLATION.** One blended number lets weak channels hide behind strong ones.

**ABNB APPLICATION: the blend is regional, and for six quarters it hid a North American stall.** North America is ~29% of nights and **42.4% of revenue**; Latin America and Asia Pacific are 31% of nights but **18.9% of revenue** (`10` §1). In 1H25 the blended nights number printed +7-8% while NA was **low-single digit** (bucket) and NA revenue growth fell to **+3.0% in 3Q25**; LatAm and APAC carried the total. In 2Q26 LatAm and APAC, at 31% of nights, delivered **52% of the growth**. Because those regions run at roughly half NA's ADR (regional ADR index NA 1.42, LatAm 0.68, APAC 0.59), every point of mix shift is dilutive to revenue per night, and the blended "ADR ex-FX +3-4%" is a mix-weighted number that understates like-for-like pricing in every region.

The direction of the blend has flipped to benign: NA nights are back to high-single digit ("the highest growth in almost three years") and NA revenue was +15.8% in 2Q26, mostly the Canada and inbound lap (Canadians returning from the US went from −31% to +5.6% y/y). That is a mechanical comparison, not a demand change, and it means the blend will flatter NA through 1H27 before the World Cup lap hits 2Q27.

Two further blends inside "nights": hotels (single-digit percent of nights, growing ~3x homes, no GBV or nights disclosed) and seats (immaterial). A blended nights number that includes a fast-growing hotel line with an undisclosed, "best-in-class" commission is a channel blend by construction.

**DATA NEEDED.** The XBRL regional revenue split each 10-Q (check-in basis, so y/y only); the letters' four regional buckets; Booking Holdings' room-nights acceleration (r +0.88 with ABNB EMEA acceleration on n 7, prints ~8 days earlier). **Eurostat cannot help**: 150-day lag, and its EU27 platform nights have outgrown ABNB EMEA by a mean 5.5pp since 4Q24, a share-loss signal with real geography and basis caveats.

**WHAT OTHERS SAY.** The 1Q25 call had an analyst raise "EMEA slower than competitor"; the Eurostat gap is the quantified version of that question and is the bear question to be ready for (`10` §"For the 5 Nov card").

**VERDICT: neutral now, was bear through 2025, turns bear again in 2Q27. Posture:** show the regional contribution table, state that half the growth comes from a third of the nights at half the ADR, and use it to explain why blended ADR ex-FX under-reads pricing. **5 Nov check:** NA bucket ("high-single" again or back to "mid-single"), EMEA vs the late-October Booking print, and a first hotels number.

---

## 7. "Ditto BOPIS/curbside/ship from store, ditto what store an ecom sale gets assigned to, ditto return rates (book sales 1Q juiced by promos, returns hit 2Q)"

**TRANSLATION.** Fulfilment mechanics, sale assignment and returns are invisible levers inside the comp.

**ABNB APPLICATION: the timing mechanics are the whole revenue model, and they are disclosed; the "returns" are cancellations, and they are not.**

- **Assignment.** Nights, GBV and ADR are dated at *booking*; revenue is recognised at *check-in*. Revenue by region is by *host location*; the expansion-market growth claims are on an *origin* (guest) basis. So a Brazilian booking a Florida home in Q1 for July is Q1 LatAm-origin nights, Q1 GBV, Q3 North America revenue. This is why Q1 ADR is the highest of the year (peak-season entire homes booked early), why Q3 revenue is 34% of the year on 25% of GBV, and why the implied quarterly take rate swings 9% / 13% / 18% / 14% with no change in fees (`airbnb_earnings_call_study.md` §8.3). Anyone reading a quarterly take rate against the prior quarter is reading seasonality.
- **Returns.** GBV is net of cancellations occurring in the period. The aggregate cancellation rate is disclosed only in prose (~16% to ~17% after RNPL); the RNPL cohort's rate is "higher" and unquantified; there is no cancellation reserve disclosure. The Signet parallel is exact: zero return-rate disclosure, and the mechanism most exposed to promo timing (RNPL bookings cancelled before the charge date) is the one that is dark.
- **The one lever we can size.** The revenue-minus-GBV growth gap, which is the timing residual, ran −4.2pp (3Q25), −3.9, −1.3, **+0.8pp (2Q26)**. The 3Q26 guide assumes it stays near zero; the trailing mean is −2.15pp. Every alt-data nowcast that sits below the guide sits there because of this term, not demand (`08` §8).

**DATA NEEDED.** Nothing external exists. Inside Airbnb calendar files could in principle give a booked-to-available flip rate as a cancellation proxy (`2026-09-05_austin-str-rnpl-hotel-factors.md` §85); not built.

**VERDICT: neutral, because it is unobservable in both directions. Posture:** one sentence in Q&A: *"Cancellations are not disclosed beyond a rounded platform rate; the timing gap between bookings and stays is disclosed and it, not demand, is the swing in every quarterly revenue reconciliation."* Model revenue off GBV with a stated gap assumption, never off nights alone.

---

## 8. "Also conversion of franchise/licensed stores. Sometimes it's in the 10-Q but the stock has moved by then, #'s moved, you ain't getting paid"

**TRANSLATION.** Adding a different kind of unit to the base distorts growth and margin comparisons, and is disclosed too late to trade.

**ABNB APPLICATION: the base is being converted, one supply type at a time, and none of the converted units is disclosed.** Airbnb has no franchisees; what it has is a nights number that increasingly includes units with different economics:

- **Hotels.** "Thousands" of hotels across 20+ destinations, single-digit percent of nights, growing roughly 3x homes, commission "best-in-class" and undisclosed, guest incentives (price match, up to 15% credit) funded by Airbnb. If hotels are 3-5% of nights growing 30%, they are contributing about a point of nights growth at a lower take rate net of incentives. Mertz intends to "exit 2026 with hotels being a meaningfully larger percent of the overall business"; the return-to-homes statistic was 55% on the 1Q26 call and ~35% in the 2Q26 letter (`airbnb_earnings_call_study.md` §8.1).
- **Seats** (Experiences and Services): inside the KPI since 2Q25, immaterial by management's own word, unit economics never given.
- **Co-host network and professional managers.** Supply growth is increasingly professional (`2026-09-05_austin-str-rnpl-hotel-factors.md`): multi-homed across Airbnb, Vrbo and direct, which is the take-rate and share pressure behind the direct-link fee pilot (#11).
- **Partnership channels.** Delta SkyMiles is a revenue share ("no negative take-rate impact", management) with no size given.

None of this is in the 10-Q either. The nearest filed evidence is the S&M split (field operations and policy +43% to $993M in FY25, +24% in 1H26), which is where hotel and services go-to-market lands, and the contra-revenue line that holds the take rate flat.

**WHAT OTHERS SAY.** Analysts asked for services/experiences/hotels contribution margin on the 2Q24, 3Q25 and 2Q26 calls and got no number each time (`2026-09-05_margin-drivers.md` §267). Chesky's own admission that Airbnb's conversion "is significantly lower than, say, Booking.com" is the bull case for hotels and the bear case for the core in one sentence.

**VERDICT: cuts for the bear on KPI quality, is the bull's optionality bucket in substance. Posture:** in the model, keep hotels as a separately named and separately sized optionality line (FINAL_SUMMARY's third upside source), and never let "nights" carry it silently. **5 Nov check:** the first hotel nights or GBV figure; if none, ask why a business "going significantly better than I expected" for five quarters still has no number.

---

## 9. "Getting the quarter right, the guide right (say 1Q/2Q), and then the 2H guide is trash for reasons you could never have alt-data'd your way into"

**TRANSLATION.** Nail the near quarter and lose on a back-half guide that breaks on something no panel tracks.

**ABNB APPLICATION: this is the central finding of the overnight run, and the mechanism is dated to the quarter.** Three laps converge on the Q4 2026 guide and FY27:

1. **The FX lap.** Revenue FX lags spot by one to two quarters because the USD value of a stay's fee is fixed at booking (`28_fx-hedge-disclosures.md` §3, `05_macro-outlook-and-transmission.md`). The 3Q26 tailwind is ~+3pp; the Q4 2026 contribution is **already 84% determined at about −0.4pp**. **The Q4 revenue guide steps down roughly 3 points on arithmetic alone, with no change in demand.** Hedges cannot rescue it: the designated book ($3.4bn notional, 46% of LTM non-USD revenue) has been reclassifying *losses* into revenue since 3Q25 (−$42M, −$23M, −$15M, −$19M, i.e. −1.1 to −0.6pp of growth) and ~$26M more is scheduled over the next twelve months.
2. **The product lap.** RNPL US (3Q26), RNPL merchandising (4Q26), RNPL global plus the cancellation-policy and fee changes (1Q27); see #4.
3. **The event lap.** The World Cup, never sized by Airbnb, lands as a 2Q27 comparison; STR has already put −0.8% on June 2027 US hotel RevPAR for the same reason.

Against those, the cost side is committed: brand and performance marketing at +25-32%, a data-hosting commitment that went from "at least $672M through 2027" to **"at least $1.7bn through 2031"**, and Mertz's August statement that the guide "does assume a material increase in terms of the AI spend" against Chesky's February "our investment in AI will not affect the P&L". The margin bridge says the whole FY26 gain is ADR-plus-FX (+3.6 points) minus marketing (−2.2) plus support and G&A leverage (+1.2); **if ADR ex-FX and FX both go to zero the base case is a 2.5-point margin decline, not a 1-point gain** (`07` §5.2).

The reaction-function evidence sits on top: all nine "guide below Street" prints had a negative 20-day excess return; the two largest drawdowns of the last three years (2Q24 −12.3%, 2Q25 −8.4%) were hedged forward sentences that did not verify. The 2Q24 warning ("shorter booking lead times") preceded a 0.2-point moderation; the 2Q25 warning ("tougher comparison toward the end of the quarter") preceded three quarters of acceleration. The market takes ABNB's caution at face value every time.

**WHAT OTHERS SAY.** The Street has Q4 2026 at $3.20bn (+15.2%) with a 21% high-low spread ($3.05-3.70bn), the widest in the consensus table: nobody has converged on the post-lap Q4 (`04` §"For the 5 Nov card"). Zero of 22 target changes since August were cuts.

**VERDICT: cuts hard for the bear on 5 Nov and 1H27 reported growth, and it is the variant perception whichever way the pitch goes. Posture:** build the Q4 and FY27 bridge (FX, product lap, marketing) *before* 5 November and present it as arithmetic. If long: the step-down is mechanical, the market will misread it as demand, and that is the entry. If short: the market has not priced a dated 3-point revenue-growth step-down in a stock whose multiple moves +0.48 turns per point of forward growth and zero on margin. **5 Nov check:** does management quantify the Q4 FX assumption as they quantified Q3's; is any "moderation / shorter lead times / tougher comps" construction used; is there any first 2027 framing.

---

## 10. "Timing of aging inventory / channel stuffing (will inventory be marked down in 3 months, 6 months, unclear)"

**TRANSLATION.** Aged inventory is a deferred hit of unknowable timing; build masquerades as health until the markdown.

**ABNB APPLICATION: Airbnb owns no inventory, so this splits into three things that behave like it.**

1. **The booked-not-stayed backlog is the inventory, and RNPL made it un-auditable.** Unearned fees ($2,831M at June 2026) used to cover 65-70% of next-quarter revenue and 87-89% of Q2's; in 2026 they covered 76% and are flat to down y/y against GBV +16%. Funds held for clients ($12.2bn) still grow but the funds-held-minus-GBV gap widened to 5.2pp. The "markdown" on this inventory is cancellation (#7), and its timing is exactly Blotnick's "3 months, 6 months, unclear" because RNPL bookings cancel before they are paid. The one genuinely new alt-data survivor in the run, funds held forecasting next-quarter revenue at 0.60x naive, is **1.85x AR(1) on the other window in the same file** (`15` CONF-07): the backlog indicator is itself of unknowable reliability now.
2. **Listing quality is the channel.** Supply grew 18-19% against demand 11-14% in 2023 and the sell side asked "which should we extrapolate?" (1Q23, score 4/10). The response was a quality purge (550,000+ listings removed) and the withdrawal of the listings-growth disclosure. The host-level markdown, price cuts and occupancy loss, lands on hosts not Airbnb, but shows up in ADR ex-FX, which is the single most powerful margin driver management does not control. Regulation is the exogenous write-down: median revenue loss 0.45% at 2027 and 1.66% at 2030, 95th percentile 6.7% (`2026-09-05_regulatory-forecast-profile.md`), and no European regulatory event has ever moved the stock.
3. **The AI build is a purchase commitment before it is a cost.** Non-cancellable purchase obligations $719M (Dec 2024) to **$1,749M (Dec 2025)**; server costs +$15M in 1H26 on reserved-instance amortisation; the level of cloud cost has never been disclosed, only its increase. This is the closest thing Airbnb has to inventory whose P&L timing is unclear, and it is four to eight quarters ahead of cost of revenue (`07` §2.2).

**WHAT OTHERS SAY.** Management frames the backlog as visibility and the commitments as capex that "will not affect the P&L"; the CFO has since said the opposite. Our own Inside Airbnb supply work is where the false markdown signals came from (#13).

**VERDICT: neutral-to-bear, and mostly a discipline about which series to retire. Posture:** retire unearned fees as an indicator; quote funds held only with both windows; carry the hosting commitment as the leading indicator of AI cost. **5 Nov check:** funds-held y/y against GBV y/y; cost of revenue per $100 GBV against $2.40; any change to the purchase-obligation language in the 10-Q.

---

## 11. "Mgmt channel shift disclosure (wholesale/DTC): lot of room to obfuscate revs/GM%s/fixed cost deleverage"

**TRANSLATION.** Shifting revenue between channels blurs like-for-like growth and margin mix.

**ABNB APPLICATION: the channel shift is in the fee structure, and take rate is where it hides.** Three simultaneous fee regimes sit inside one "implied take rate":

| Regime | Who pays | Status | Take-rate effect |
|---|---|---|---|
| Split fee (host 3%, guest 14.1-16.5%) | mostly guest | legacy, being retired | baseline |
| **Single 15.5% host fee** | host, embedded in price | "over a quarter" of listings 1Q26, "approximately half" 2Q26 (call, line 272), all by year-end | **+40 to +50bp if the replaced guest fee averaged ~14.1%; negative if it averaged 15%+** (`06` §2). Management says "modest upside"; it has not appeared yet (Q2 take rate 12.96% / 13.17% / 13.26% in 2024-26 is booking-vs-stay timing) |
| **Direct-link fee, 6-10%** | host, for bookings the host brings | pilot announced 29-31 Aug 2026 | first explicit take-rate concession; a −0.8pt scaling has circulated but rests on a paywalled Skift piece and is **unverified** (`15_red-team.md`, correction 16) |

Around them: the FX service fee (+20bp, in the base since 2025), travel insurance revenue (+40% FY25, +45% 1Q26, >60% 2Q26 off a small base), the Delta revenue share, and the new-business incentives as contra-revenue. Net: **the 2026 take rate is guided flat at ~13.4%**, which means the single fee and insurance are being spent on hotels and services incentives in real time, and the disclosure that would let anyone check is absent: no take rate by fee regime, by supply type or by region. That is the wholesale/DTC obfuscation in marketplace form, with the added twist that GBV is defined to include the guest fee, so the migration also changes what GBV means.

The second shift is core vs expansion markets ("roughly twice core" on an origin basis, ten consecutive quarters), where expansion-market brand budgets are described as fixed per market, i.e. the fixed-cost deleverage Blotnick names sits in the S&M line with no market-level disclosure.

**WHAT OTHERS SAY.** Take-rate talk on calls has doubled in 2026 (`03` §1). Three of five expert calls say the OTA take rate is at a ceiling and bargaining power sits with professional managers (`2026-09-05_third-bridge-transcripts.md`). Calls built on take-rate expansion have been wrong on the KPI for three years and unpunished (`2026-09-06_predictive-study.md` §8).

**VERDICT: cuts for the bear on FY27 monetisation, and the take-rate bull case as worded should be dropped (FINAL_SUMMARY already says so). Posture:** model take rate flat with a ±10bp band; if the deck mentions the single fee, show the sign-depends-on-the-replaced-fee table. **5 Nov check:** Q3 implied take rate against 17.9% (the first clean read after four quarters of migration); any direct-link pilot quantification; the "entire supply base by year end" claim (C081).

---

## 12. "Accounting for loyalty/gift-card/card credit programs to boost EBIT/EPS"

**TRANSLATION.** Deferred-revenue and program accounting carries judgement that can be tuned toward earnings.

**ABNB APPLICATION: Airbnb has no loyalty program and no credit book, so the retail objects are absent, but the earnings-quality items are larger than Signet's and sit in plainer sight.**

- **The float.** $12.2bn of funds held for clients plus ~$12bn of own cash earned **$705M of interest income in FY24** (7.4% of revenue that year; 5.2% TTM; 15-18% of FCF). It is below Adjusted EBITDA but inside net income, EPS and FCF, and it is falling as rates fall and as RNPL slows the float (`2026-09-05_margin-drivers.md` §12). It should not be capitalised at an EBITDA multiple and the FCF margin it inflates (37.7% FY25 against 35.1% EBITDA) is not "cleaner" than EBITDA.
- **SBC.** 12.9-13.1% of revenue, excluded from Adjusted EBITDA and non-cash in FCF. GAAP operating margin 20.8% against Booking's 32.8%; **the entire 12-point gap is SBC** (13.0% vs 2.3%). SBC-adjusted FCF margin: ABNB 24.6%, BKNG 31.5%. ~$0.7bn a year of RSU tax withholding is a cash cost the old model never subtracted from net cash (FINAL_SUMMARY). The FY24 SBC guide missed by 6-11 points.
- **Contra-revenue incentives.** Hotel credits, price match and services incentives are netted from revenue and are what hold the take rate flat; their size is never given. This is the loyalty-cost analogue, without the program.
- **Hedge gains and losses in revenue.** Realised cash-flow-hedge results are reclassified into revenue: −$42M / −$23M / −$15M / −$19M over 3Q25-2Q26 (`28`). Immaterial until 2025; now a stated line in every FX sentence, and one that could just as easily add to revenue in a strong-dollar year. Carry it as its own row.
- **One-offs, all disclosed, all excluded on the flattering side:** 2Q23 payment-processor incentives (non-recurring benefit to cost of revenue), 4Q23 gift-card breakage, ~$935M of Italy withholding and lodging-tax reserves in 4Q23 G&A that GAAP took and Adjusted EBITDA excluded, the 3Q23 $2.7bn valuation-allowance release, 3Q25 discrete tax items. Cash taxes ($232M FY25) are running at a third of the provision ($626M) while released deferred tax assets are consumed; **FCF/EBITDA falls from 107% to ~93% by FY28 in the base case** as they converge (`07` §5).
- **Unearned fees** are recognised at check-in with no judgement involved; that line is clean by construction, which is the mirror image of Signet's ESP book.
- **Insurance revenue** (+60%) is the one line where recognition and reserving judgement exist and nothing is disclosed.

**WHAT OTHERS SAY.** The predictive study's scorecard found nobody in the 37-pitch set modelled net cash return after SBC or interest income inside FCF; the crowd has been long and right on direction while missing the per-share arithmetic (`2026-09-06_predictive-study.md` §8).

**VERDICT: cuts for the bear on earnings quality, and it is our differentiation because the numbers are all filed. Posture:** a forensic appendix with five rows: interest income inside FCF, SBC and withholding against the buyback, contra-revenue incentives vs the flat take rate, hedge reclass into revenue, cash tax convergence. Then the bull turn: cash cost per night ex S&M has fallen every year since 2022 and the core has been getting cheaper the whole time. **5 Nov check:** interest income against $180M (3Q25); SBC growth against the "lower than 2025" guide; the hedge reclass sentence in the 10-Q.

---

## 13. "Data is just straight up wrong because what do they care, you're paying for it anyway"

**TRANSLATION.** Vendors have no skin in your P&L. Panels are miscomposed, revised and stale.

**ABNB APPLICATION: our data is free, so the vendors are us, and the red team found the same failure modes.** `15_red-team.md` re-derived 98 claims (82 confirmed, 11 wrong, 1 unsupported, 4 unverifiable) and the wrong ones are a Blotnick appendix in themselves:

1. **Inside Airbnb.** Partial-scope monthly dumps produced the "Paris 33% / Nashville 44% / Chicago 40% supply exit" numbers, all artefacts; the seven-city retention fall (75.4% to 71.1%) was Austin's listing-count step, ex-Austin 75.5% to 73.4% with new-listing share exactly flat (`21_inside-airbnb-pair-eligibility.md`); the discount-share series "tripled" because the share of quotes carrying a taxes line went 0.2% to 6.5% (a schema change, not behaviour); listed prices were discontinued in late 2025 so the like-for-like price series is dead (r +0.03 with ADR on n 8, resting on 1-4 cities); the CDN keeps about a year, so every missed month is unrecoverable.
2. **Google Trends** renormalises the 0-100 index on every pull, so nothing computed today is what an analyst saw in 2024; single-term quarterly pulls swing 40-70pp between adjacent quarters.
3. **Eurostat** platform nights arrive ~150 days late; there will be no 3Q26 read until early 2027, and 2Q26 will still be incomplete on 5 November.
4. **Consensus** is spliced across LSEG, Zacks, StreetAccount, Visible Alpha and S&P Global, which differ by ~2% on at least one nights comparison and, on the 4Q22 next-quarter guide, put the guide on **opposite sides of the Street** (LSEG $1.69bn vs Zacks $1.90bn); Theo's Bloomberg consensus workbook is pull-date anchored, not point-in-time; no ADR consensus has ever been published; no Q3 2026 nights or EBITDA consensus exists in any free source.
5. **XBRL** `AdvertisingExpense` ($843M FY25) is not the brand-and-performance line ($1,595M); `PurchaseObligation` carries no calendar-year frames.
6. **Our own outputs.** The "zero of 233 alt-data features" count came from a half-finished file (598 rows, 52 beat AR(1)); the funds-held survivor is window-dependent; the "no implied event premium (0.002 pts)" was an estimator that could not detect one; "RNPL added 3 points" was three features; the −0.8pt direct-booking hit is a paywalled article nobody read; the FX model "predicted +2.9pp" was +2.2pp in its own CSV.
7. **Peer timing.** Marriott and Hilton RevPAR entered the panel as "available before print" in three quarters where they were not (fixed in WS20/26).

**VERDICT: cuts for us, whichever side we take. Posture:** the "where the data lies about Airbnb" appendix slide, and the standing rule from FINAL_SUMMARY: *read the labels before quoting a number*. Every exhibit carries its window, its vendor and its fetch date.

---

## Where the analogy breaks

Four places where importing the retail frame would mislead, worth saying out loud before a judge does:

1. **There is no gross margin to trade for volume.** Cost of revenue is ~2.3% of GBV (payments, hosting) and scales with bookings, not with fees, so a take-rate change flows almost entirely to EBITDA and a marketing dollar has no COGS offset. The "buy the comp" cost is all opex and contra-revenue, which is why it is visible in the S&M split and the take rate rather than in a margin line.
2. **The guide is a floor by design, not by sandbagging alone.** 65-90% of next-quarter revenue is pre-funded by bookings already made, so the revenue range is tight and the beat is small and universal. The stock trades nights, GBV, take rate and margin; revenue surprise vs consensus adds nothing once nights is in the regression.
3. **The "comp base" cannot be reconstructed by the company either.** Management does not control which markets travellers book into, so mix shift is demand-driven, not a management choice; the disclosure silence is the choice.
4. **Alt data fails for a structural reason, not a vendor one.** Airbnb's KPI is global, booking-dated and net of cancellations; every free series we hold is regional, stay-dated or supply-side. The test count (roughly 3,500 across the run) is the honest answer to "did you try".

---

# THE BLOTNICK AUDIT, ABNB: one-page table

| # | Blotnick point | Exists at ABNB? | The ABNB-specific fact | Cuts for | 5 Nov / pre-pitch check |
|---|---|---|---|---|---|
| 1 | Alt data beats mgmt guide; will mgmt lie / imply accel | Inverted on revenue; live on take rate | Revenue midpoint beaten 19/19, top of range 15/19; nothing in 598 alt-data tests beats AR(1) on both windows; FY25 take-rate guide missed by 36bp, 1Q26 walked back in a quarter; multi-year claims 26% hit, CEO 42% | Bull (revenue/margin), bear (take rate) | Q4 revenue guide ≥+14%? FX assumption quantified? |
| 2 | Cash % tanks card-panel fit | Structural, no panel held | US 39% of revenue; RNPL moved the charge date for >20% of GBV; panel sees GBV not the 13% revenue; check-in recognition lags | Neutral (say it first) | Never quote a panel nowcast; use ALTD for US share only |
| 3 | Mgmt buys the comp; reaction unknowable | Yes, both | 85% of 4-yr cost/night increase is S&M; brand & performance +32% 1H26; take rate held flat by incentives; no day-1 spec has positive LOO R²; 84% of 2Q26 +17.4% was multiple | Bear (growth quality), neutral (print) | Brand & performance y/y in 10-Q; Q4 guide vs $3.20bn Street |
| 4 | Exit-rate juicing; costs hit 1-2 qtrs later | **Yes: RNPL** | ~70% adoption, >20% GBV, cancellations 16%→17%, attribution went diffuse 2Q26; laps 3Q26 / 4Q26 / 1Q27, flagged by CFO | Bear (FY27 nights) | NA bucket; cancellation rate; funds-held-minus-GBV gap |
| 5 | Comp-base games; one-off carve-outs | **Yes, by silence** | Cross-border, urban, long-term-stay, listings growth all dropped 4Q23-1Q24 as they decelerated; regional exact % → buckets 4Q24; seats bundled 2Q25; bedroom nights introduced 2Q26; Easter / Middle East / Paris / ex-FX carve-outs | Bear (transparency), neutral (substance) | Any further series going dark; hotels number |
| 6 | Blended comp hides channel mix | Yes, regional | LatAm+APAC 31% of nights, 19% of revenue, 52% of 2Q26 growth; NA revenue +3.0% in 3Q25 while total +10%; Eurostat outgrew ABNB EMEA by 5.5pp/qtr | Neutral now; bear again 2Q27 | NA bucket; Booking print late Oct |
| 7 | BOPIS / assignment / returns | Timing disclosed, cancellations dark | Booking-date KPIs vs check-in revenue vs host-location geography; rev-minus-GBV gap −4.2 → +0.8pp; no cancellation reserve disclosure | Neutral | State the gap assumption in every revenue bridge |
| 8 | Franchise / licensed conversions | Yes: hotels, seats, partners | Hotels single-digit % of nights growing ~3x, commission and incentives undisclosed, return-to-homes stat 55% → ~35%; no contribution margin ever given | Bear (KPI quality), bull (optionality) | First hotel nights/GBV figure |
| 9 | 2H guide trash for un-alt-data-able reasons | **Yes, the core finding** | Revenue FX lags spot 1-2 qtrs; Q4 FX ≈ −0.4pp vs +3 in Q3, 84% determined; hedges reclassifying losses; product laps; World Cup 2Q27; 9/9 guide-below-Street prints negative at 20d | Bear on 5 Nov, variant perception either way | Q4 FX quantified? "moderation" language? 2027 framing? |
| 10 | Aging inventory / channel stuffing | Three forms | Unearned fees dead as indicator; funds held 0.60x on one window, 1.85x on the other; 550k listings purged and listings disclosure dropped; hosting commitment $672M→$1.7bn through 2031 | Neutral-to-bear | Funds held vs GBV; cost of revenue per $100 GBV; Note 13 |
| 11 | Wholesale/DTC shift obfuscation | Yes: three fee regimes in one take rate | Single 15.5% fee ~half migrated, +40-50bp *if* replaced fee was ~14.1%; direct-link 6-10% pilot; incentives net it to flat 13.4% | Bear (FY27 monetisation) | Q3 take rate vs 17.9%; pilot quantification |
| 12 | Loyalty / gift-card / credit accounting | Absent literally; bigger in substance | $705M interest income inside FCF; SBC 13% = entire GAAP margin gap to BKNG; contra-revenue incentives unsized; hedge reclass −0.6 to −1.1pp; cash tax at a third of provision | Bear (earnings quality) | Interest income vs $180M; SBC vs guide; hedge sentence |
| 13 | Data is just wrong | Yes, ours | Inside Airbnb partial scrapes and schema change; Trends renormalisation; Eurostat 150-day lag; consensus vendors on opposite sides of the Street; six of our own headline numbers restated | Us | "Where the data lies" appendix; labels on every exhibit |

**Score: 6 cut for the bear, 2 split (bull on one half, bear on the other: #1 and #8), 4 neutral, 1 cuts for us.** Read that carefully: it is not a short thesis. It says that the *accounting and disclosure* layer favours the sceptic while the *guidance and execution* layer favours the believer, and that the most valuable object in the repo, the dated Q4 FX step-down, is a trade for either side depending on whether the market misreads it.

---

# TOP 5 ACTIONS FOR THE PITCH

1. **Make the Q4 / FY27 bridge the centrepiece (points 9 + 4 + 3).** *Built 7 Sep 2026: `research/notes/overnight/29_q4-fy27-bridge.md`, script `analysis/src/overnight/29_q4_fy27_bridge.py`, figure `analysis/figures/overnight/29_q4_fy27_bridge.png`.* Three dated laps: FX (−3pp of reported growth, 84% determined), RNPL and the two sister features (3Q26 / 4Q26 / 1Q27), World Cup (2Q27). Present it as arithmetic before 5 November. Then say plainly which way we take it: a long argues the market will misread mechanics as demand and that is the entry; a short argues a growth-set multiple (+0.48 turns per point) has not priced a dated step-down. Either way the FINAL_SUMMARY risk stands: if management does not quantify the Q4 FX assumption, expect the guide-below-Street pattern.

2. **Own the disclosure regression on one slide (points 5 + 6 + 8).** Five dropped series with last values and dates; regional buckets reconciled to reported nights within 1.1pp; hotels and seats inside the KPI with no unit economics; bedroom nights quoted alongside nights, never instead. Being harder on the KPI set than the bear converts Blotnick's silence trap into a credibility win.

3. **Retire the take-rate bull case and replace it with the fee-regime table (points 11 + 12).** Three fee regimes in one 13.4% number, the sign-depends-on-the-replaced-fee arithmetic, incentives as contra-revenue, and the direct-link pilot flagged as unverified. Model take rate flat ±10bp. This is where three years of bulls have been wrong and unpunished, which is exactly why it is not priced.

4. **Carry a forensic appendix on cash quality (point 12).** Interest income inside FCF, SBC and RSU withholding against the buyback, cash tax convergence, hedge reclass into revenue. Then pivot to the bull substance: cash cost per night ex-S&M has fallen every year since 2022; the core is cheaper than it looks and the whole margin story is a spending choice.

5. **State the alt-data and card-panel position before a judge asks (points 1 + 2 + 13).** Roughly 3,500 tests, nothing beats AR(1) on both windows, the guide-plus-cushion is the best revenue forecast we hold, US card panels see under 40% of the business on the wrong date since RNPL. Then the "where the data lies about Airbnb" slide with our own restated numbers on it. A team that shows its own corrections is harder to catch than one that shows a panel chart.

---

*Cross-references: every ABNB fact above traces to the notes named in the text; primary citations (letters, 10-Q/10-K notes, transcript line numbers, FRED/EDGAR pulls) live in those notes and their CSVs under `data/processed/overnight/`. Nothing herein is newly sourced. The Signet audit's five-gate structure is reused deliberately so the two documents can be read side by side.*
