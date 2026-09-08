# Ideas backlog for ABNB — ranked by value per hour, each with the SIG lesson behind it

Rank reflects (differentiation to a judge) × (probability it works) ÷ (hours). "SIG lesson" is the specific thing that worked or failed on SIG that motivates the idea. Nothing here asserts an ABNB fact; every idea ends in a checkable output.

## Tier 1 — build in week one

**1. Quarterly KPI panel with derived series (4h).** Nights, GBV, revenue, ADR, take rate, adj EBITDA, FCF, SBC, buybacks, diluted shares, from every shareholder letter since IPO, each number source-tagged. Derived: take rate ex-FX, implied ADR vs BEA hotel price index, FCF after SBC, net share change after SBC.
*SIG lesson:* the two highest-alpha exhibits in the SIG deck were **derived** series nobody had computed from public disclosures (implied unit comps; gold-in-COGS ledger). Find ABNB's equivalent: the number that reconciles management's words every quarter and that no sell-side note prints.

**2. Guidance-vs-actual table and the reaction-function test (3h).** For ~22 prints: guided revenue range vs actual, guided nights/ADR direction vs actual, next-quarter guide midpoint vs consensus, print-day (T+1) move. Test: does the guide-vs-consensus gap explain the reaction better than the revenue/EBITDA beat?
*SIG lesson:* "the market prices the guide, not the print" held on SIG (clean corr +0.45 vs EPS-surprise corr −0.44) and across every mall-retail case studied. If it holds on ABNB, the catalyst slide is about the Q4 guide, not Q3.

**3. BEA travel panel exhibit (1h, data in hand).** Accommodations nominal vs real vs price; hotels & motels; inbound vs outbound foreign travel. Frame: US lodging spend is running mid-single-digit nominal and ~+2% real; ABNB's US nights growth vs that = share.
*SIG lesson:* BEA jewelry turned the Sept 9 print into a share test with one chart, and the real-vs-nominal split was the honest concession the judges expect ("the category is all price").

**4. Google Trends share-of-search with the first-differences test (3h).** airbnb / vrbo / booking.com / hotels.com / expedia in one payload (comparable); category terms in another. Backtest y/y vs nights growth in levels AND first differences; check for contamination events before quoting any y/y.
*SIG lesson:* a 0.85 correlation collapsed to 0.13 in first differences; a celebrity event and an unexplained surge contaminated two quarters; a decade of share-of-search told a story the thesis had to address. Run the same tests before believing the ABNB series.

**5. Options ledger + print-day distribution (1h).** `tools/options_ledger.py` with travel tickers; print-day |move| distribution from ~22 prints vs current implied move.
*SIG lesson:* the corrected implied move (±11.6%, not 10.5%) and "40% of prints exceed it" were the honest positioning lines; call skew vs peers was a one-line differentiator.

**6. Pitch-mine every ABNB writeup and score it (8h).** VIC, SumZero headlines, Seeking Alpha RSS, Substack, short reports, sell-side PT dispersion. Each call priced at its date from daily prices; tally which metrics every writeup used and which none did.
*SIG lesson:* the "nobody has used a POS panel, foot traffic, or customs data on this name" finding defined the edge; the "every short since Jan-25 was right for 8 weeks then wrong" scorecard pre-empted the bear; a 2018 student long that lost 65% was worth a prep line. ABNB's writeup corpus is deep enough that the *gap* analysis is the whole point.

## Tier 2 — build in week two

**7. Buyback-vs-SBC cannibal scorecard (5h).** XBRL `companyfacts` for ABNB + BKNG, EXPE, META, NFLX, UBER, DASH: diluted shares, SBC, buybacks, FCF, FCF after SBC, payout÷FCF, net debt. Exhibits: net share count path, "years to retire the float at current pace", EPS glide on flat earnings.
*SIG lesson:* buybacks were 11–23% of EPS growth in every winner and saved no trap (BBWI retired 27.7% and fell 69%). Never lead with the buyback; use it as the multiplier. For ABNB the honest version is net of SBC.

**8. Common Crawl listing-price panel (8–12h, prototype first).** Archived airbnb.com listing pages by crawl: nightly rate, fees, total-price display, reviews, Superhost; matched-listing panel across two windows for like-for-like ADR; vrbo.com as control. Compare to reported ADR and to hotel ADR (STR headlines / BEA price index).
*SIG lesson:* the CC scrape replicated a UBS Evidence Lab discount factor for free, **contradicted UBS on one banner** (breadth doubled while depth fell), and the matched-SKU like-for-like panel became the cleanest pricing slide. The prototype rule: fetch one WARC record and inspect the JSON before committing to the index harvest.

**9. Inside Airbnb supply and host-concentration panel (4h).** Listings, entire-home share, multi-listing (professional) host share, review velocity, by city and quarter; NYC pre/post Local Law 18 as the natural experiment; registry counts where cities publish them.
*SIG lesson:* supplier concentration was "the single most reliable trap signal" in the cannibal study; official supply data (GJEPC customs) that nobody used scored 8.5/10. Host concentration and regulatory exposure are ABNB's supply-side equivalents, and Inside Airbnb is free.

**10. Transcript analytics on ~22 calls (5h incl. parser).** Analyst roster churn, topic frequency (take rate, regulation, Experiences, marketing, SBC, AI), congrats count, attendance, "declined to quantify" list, hedge-word density around guides.
*SIG lesson:* sentiment predicted nothing; attendance was contrarian; the topic matrix produced "zero questions on services in six quarters" which became a slide; the "questions management declined to answer" list drove the Q&A prep. With ~40 analysts on ABNB the attendance signal is weaker, but the topic-void finding is likely stronger.

**11. Expectations map for the early-November print (6h, refresh the week before).** Guidance detail, consensus by aggregator, revision direction, analyst actions log, alt-data scoreboard, positioning (options, SI, 13F, Form 4 founder sales), peer read-through calendar (BKNG/EXPE/MAR/HLT report first), scenario map with the reaction function.
*SIG lesson:* the file was the most perishable and most used; the peer-calendar section caught that Macy's reported the next morning and that Movado flagged a catalyst nobody had priced. For ABNB the peer prints land days earlier and will set the tape.

**12. Regulatory tracker from primary text (6h).** Every material STR ordinance with effective date and mechanism (registration, primary-residence, night caps), exposed nights estimated from Inside Airbnb; scored against what actually happened to listings in NYC post-LL18.
*SIG lesson:* verifying tariffs against the Federal Register and HTSUS corrected a folklore claim ("5-month duty-free window" was 4 days) that would have been a kill-shot. Regulation is ABNB's tariff.

## Tier 3 — if time allows, or as Q&A ammunition

**13. Blotnick trap audit for ABNB (2h).** Apply the 13 traps: GBV-vs-revenue timing (#1), nights/GBV/revenue blending (#6), the 2H guide (#9), unearned fees and interest income (#12), AirDNA supply counts being wrong (#13). Output: SAFER / RISKIER / NEUTRAL table → appendix architecture.

**14. Consensus-at-call vs price series (1h once the transcript export exists).** Does the stock follow estimates or the multiple? SIG's version showed two regimes.

**15. Annotated stock-history event ledger since IPO (5h).** Top moves computed first, attributed second, confidence graded; separate company from QQQ/BKNG beta. Publish as an artifact chart as SIG did.

**16. FX and interest-income ledgers (3h).** ADR FX-neutral vs reported by quarter vs DXY; funds held × short rates → interest income by quarter. The SIG gold ledger's role (turn a management promise into arithmetic) mapped to ABNB's two exogenous P&L lines.

**17. App-tracker panel (3h).** Downloads and MAU for Airbnb vs Vrbo vs Booking vs Hopper from free tiers; monthly captures forward. Was a verified dead end for SIG; is the natural distribution metric for ABNB.

**18. SimilarWeb / Semrush monthly captures (30 min/mo).** airbnb.com vs vrbo.com vs booking.com; within-vendor changes only.

**19. Expert-call dated-claims table (6h with an AlphaSense trial).** Extract every forward claim with a check date; score the ones already resolved.

**20. Pre-registered prediction card + bear scoreboard (3h).** Numeric predictions for the November print with falsifiers and trackers; the best published bear's dated predictions vs actuals, fiscal periods pinned.
*SIG lesson:* the prediction card (S12) and falsifier trackers (S14) were what made the deck's three calls *dated* and checkable, which is what the judge corpus rewards over undated theses.

## Ideas explicitly rejected after the SIG experience

- **Nowcasting the quarter from any single alt-data series.** Every SIG series failed as a nowcaster (Trends ±3.45 pts; Tenoris ±3.6 pts; foot traffic n/a). Use alt data as spread or mechanism; the winning-deck corpus says the same (VITL won on a spread widening, not a level).
- **Quoting a vendor number without the cross-vendor disagreement caveat.** SimilarWeb vs Semrush differed 3.4x on the same domain-month.
- **Drawdown-as-thesis.** Zero of 18 winning Sohn longs used it; the decade chart goes in the appendix.
- **Wayback snapshot frequency as a traffic proxy.** Rejected on SIG; rejected here.
- **Building a TAM slide from unreconciled third-party sizing.** Two SIG sources were 2x apart.
