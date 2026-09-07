# Host-only fee: prior reactions, elasticity model, take-rate/margin read-through, and Experiences/Services share

Author: Jessie (drafted with Claude), 2026-09-06
Files: `analysis/src/fee_split_elasticity_model.py`, `data/processed/fee_split_elasticity_scenarios.csv`, `docs/fee_split_elasticity_sensitivity.png`
Companion notes: `research/revenue_model_abnb_vs_bkng_expe.md`, `research/direct_booking_threat_to_abnb.md`

## 1. What happened the last time Airbnb forced host-only (2019–2020) — quantified where possible

| Item | Figure | Source |
|---|---|---|
| Host-only offered as an option to larger hosts | May 2019, 14–16% (standard 15%) | [Rental Scale-Up](https://www.rentalscaleup.com/airbnb-simplified-pricing/) |
| Made mandatory for software-connected hosts | Nov 1, 2020 (Australia), Dec 7, 2020 (most countries); US, Canada, Mexico, Bahamas, Argentina, Taiwan, Uruguay exempt | [Rental Scale-Up](https://www.rentalscaleup.com/airbnb-simplified-pricing/), [Hostaway](https://www.hostaway.com/blog/airbnb-new-fee-structure/) |
| Airbnb's stated result | Hosts who switched "and priced competitively" got **+17% bookings on average** | [Rental Scale-Up](https://www.rentalscaleup.com/airbnb-simplified-pricing/), [Hostaway](https://www.hostaway.com/blog/airbnb-new-fee-structure/) |
| Airbnb's stated rationale | Match Booking.com (~15% host commission, 0% guest fee); guests convert better with no checkout fee | [Rental Scale-Up](https://www.rentalscaleup.com/airbnb-simplified-pricing/) |
| Host reaction | "Initially resisted… viewed it as a way to force hosts to list exclusively with Airbnb"; no survey or attrition number published | [Hostaway](https://www.hostaway.com/blog/airbnb-new-fee-structure/) |
| Required host re-price to stay whole | ~+14% (2020 guidance); +14.8% payout-neutral / +18.34% "full" today | [Hostaway](https://www.hostaway.com/blog/airbnb-new-fee-structure/), [Rental Scale-Up](https://www.rentalscaleup.com/airbnb-host-fees/) |

**Honest read:** nobody has published host attrition or listing-count effects from the 2020 migration. The rollout landed in the middle of COVID (2020 GBV −37%), so any Europe-vs-US listing comparison for 2020–21 is hopelessly confounded. The only hard number is Airbnb's own +17%, which is (a) self-reported, (b) conditional on competitive re-pricing, and (c) a *relative* lift vs. neighbours still on the split fee — not a platform-level demand effect.

**What the +17% implies about elasticity.** If a switched host's listed price stayed flat, the guest's all-in price fell ~12.3% (114 → 100). A 17% booking lift from a 12.3% price cut implies a listing-level elasticity of ln(1.17)/ln(100/114) ≈ **−1.2** — same order as the low end of the academic literature (below).

**2026 differs from 2020 in three ways that matter:** (1) total price has been the default display globally since Apr 2025 ([CNN](https://www.cnn.com/2025/04/21/business/airbnb-total-pricing)), so there is no "hidden fee" for the switch to remove — the 2020 conversion lift should be smaller now; (2) it's mandatory for *everyone*, so the relative-price advantage vanishes once neighbours switch too; (3) it hits the US, where the hobby-host share is high and Vrbo/direct alternatives are more developed.

## 2. Elasticity inputs

| Parameter | Value | Source / note |
|---|---|---|
| Listing-level own-price elasticity | −4.27 average (range −2.58 to −8.63 by city/segment); Airbnb listings less elastic than luxury hotels | [Farronato & Fradkin, AER 2022, §III.A](https://andreyfradkin.com/assets/airbnb_welfare_paper.pdf) — this is demand for *one accommodation type in one city* vs. substitutes, not for the platform |
| Airbnb host supply elasticity | 3.4–3.9 (hotels 1.0–1.3) — "peer hosts are three times as elastic as hotel supply" | same, Table 3 |
| Outside-option share if Airbnb unavailable | 32% would not book a hotel (19–42% by city); 87% during peak demand | same, §II.A |
| Implied listing-level elasticity from Airbnb's 2020 claim | ≈ −1.2 | computed above |
| Airbnb's own guest price-sensitivity model | Exists (IV + experiments), numbers withheld; observational estimates were "slightly higher in magnitude" than experiments | [Wu & Schmierer (Airbnb), arXiv 2607.00280](https://arxiv.org/html/2607.00280v1) |
| Fee salience (drip pricing) | Hidden back-end fees → +14% purchase completion, +21% spend; experienced users still +15% | [Blake, Moshary, Sweeney, Tadelis — StubHub RCT, Marketing Science](https://newsroom.haas.berkeley.edu/research/buyer-beware-massive-experiment-shows-why-ticket-sellers-hit-you-with-hidden-fees-drip-pricing/) |
| Platform-level elasticity used | −0.5 to −2.0 band; −1.0 central | assumption — platform-level demand is less elastic than listing-level because the outside option is "don't travel / hotel", not "the listing next door" |

## 3. Model results (`fee_split_elasticity_scenarios.csv`)

Per $100 host subtotal. Old: guest pays $114, host nets $97, Airbnb $17 (14.9% of guest spend). New: host re-prices by θ × 14.8%, guest pays that, Airbnb 15.5% of it. Nights scale with (new perceived price / old perceived price)^ε. σ = 0 (total price visible) unless stated.

**Airbnb revenue, % change vs. split fee (σ = 0):**

| ε \ host re-price | 0% | +7.4% | +14.8% (payout-neutral) | +18.3% (Reddit "full") |
|---|---|---|---|---|
| −0.5 | −2.7 | +0.9 | +4.3 | +5.9 |
| −1.0 | +3.9 | +3.9 | +3.9 | +3.9 |
| −1.5 | +11.0 | +7.1 | +3.6 | +2.0 |
| −2.0 | +18.5 | +10.3 | +3.2 | +0.1 |
| −4.27 (listing-level, not platform) | +59.5 | +26.3 | +1.6 | −8.0 |

**Nights, % change:** at payout-neutral re-pricing, −0.3% to −1.4% across ε = −0.5…−2.0 (guest price rises only 0.7%). If hosts don't re-price at all, +7% to +30%.

**Host payout, % change:** at payout-neutral re-pricing, −0.3% to −1.4%. If hosts don't re-price, −7% (ε = −0.5) to +13% (ε = −2.0) — i.e. a host is only better off eating the fee if demand is elastic enough.

**Take rate on guest spend:** 14.9% → 15.5% (+58 bp) regardless of ε or θ — the single fee is mechanically ~60 bp richer than the split because 15.5% is levied on the grossed-up price.

**Three things the model says:**
1. **At ε = −1 Airbnb is indifferent to host behaviour.** Revenue ∝ p^(1+ε), so at unit elasticity Airbnb gets +3.9% whether hosts gross up or not. Below unit elasticity (likely for the platform as a whole) Airbnb *wants* hosts to raise prices; above it, Airbnb wants them to hold — which is exactly why 2020-era Airbnb pushed "price competitively" messaging and why the 18.34% Reddit advice slightly hurts Airbnb if demand is elastic.
2. **The migration is worth ~+3–4% revenue at the central case (ε −1, full pass-through), i.e. roughly +50–60 bp of take rate** — consistent with the CFO saying take rate would be "slightly higher" in 2026 absent new-business incentives (§4). On FY26 GBV of ~$105B that's ~$0.5B of revenue at ~90% flow-through.
3. **The transition window is where the risk lives, not the end state.** Mixed populations (switched vs. not) inside the same market recreate the 2020 relative-price effect in reverse: early switchers look 15% more expensive on dateless searches. Reddit threads confirm bookings/views drops for early switchers and full autumn calendars for holdouts. That noise resolves after Sept 15 / Oct 13.

**Salience (σ > 0) sensitivity:** in the CSV. With σ = 0.5 (guests half-ignored the old guest fee, StubHub-like), the switch to an all-in price *raises* the perceived price by ~7% at payout-neutral re-pricing → nights −3.5% at ε = −0.5, −13% at ε = −2. This is the bear case for a pre-2025 fee change; it is mostly moot now that total price display is default, but it is the right frame for the 2020 Europe episode.

**Limitations:** no cross-platform substitution (Vrbo/direct) — that's in `direct_booking_threat_to_abnb.md`; no host exit; ignores taxes (levied on the grossed-up price, a real host complaint) and cleaning-fee mechanics; single representative listing.

## 4. What management has said about take rate and margins (earnings review)

| Quarter | Implied take rate | Management explanation | Margin link |
|---|---|---|---|
| Q3'25 | 17.9% vs 18.6% (−70 bp; Q3 is seasonally high because summer check-ins recognize revenue) | "FX and the timing of when guests booked their travel and when guests stayed"; PMS hosts migrated to 15.5% in Oct | Adj. EBITDA margin 50% vs 52% — "investments in new growth and policy initiatives," ~$200M for Services & Experiences ([Q3'25 letter](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q3/v2/Airbnb_Q3-2025-Shareholder-Letter.pdf)) |
| Q4'25 | 13.6% vs 14.1% (−50 bp); FY25 ≈ 13.4% | "primarily due to FX and the timing of when guests booked … and when guests stayed" | FY25 adj. EBITDA margin 35%; FY26 guided "approximately flat" with efficiencies reinvested in marketing/product ([Q4'25 letter](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb_Q4-2025-Shareholder-Letter.pdf)) |
| Q1'26 | n/a in extract | >25% of listings on single fee; single fee + RNPL + cancellation redesign together = ~3 pts nights growth, ~4 pts GBV growth; "modest upside to full-year take rate" from fee migration and insurance | FY26 margin raised to ≥35% ([Q1'26 call](https://www.fool.com/earnings/call-transcripts/2026/05/07/airbnb-abnb-q1-2026-earnings-call-transcript/)) |
| Q2'26 | 13.2%, flat YoY | Mertz: FY26 take rate "relatively flat … accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses. **Absent these incentives, we would have anticipated our implied take rate to be slightly higher**, driven by our monetization initiatives"; ~half of listings on single fee, 100% by YE | Margin +100 bp YoY "driven by strong revenue growth and cost efficiencies in operations and support and product development"; support cost per booking −16%; FY26 margin ≥35.5% ([Q2'26 call](https://www.fool.com/earnings/call-transcripts/2026/08/13/airbnb-abnb-q2-2026-earnings-call-transcript/), [Q2'26 newsroom](https://news.airbnb.com/airbnb-q2-2026-financial-results/)) |

**Answer to "does the take-rate change impact anything?"**
- Management has never attributed a take-rate move to the fee migration. Every YoY decline is blamed on FX and booking-vs-stay timing (now RNPL); the migration is framed as a small *positive* that is being consumed by customer incentives for Services/Experiences/hotels.
- Mechanically, take rate is the single highest-leverage line in the P&L: costs scale with GBV/bookings (payments, support, insurance), not with revenue, so ~90% of a take-rate change drops to EBITDA. ±50 bp on FY25 GBV of $91.3B ≈ ±$460M revenue ≈ ±3.5 pts of EBITDA margin (revenue base ~$13.5B FY26E). That's larger than the entire FY26 margin-guidance range.
- The 2026 story is therefore: **fee migration adds ~50 bp gross, incentives (contra-revenue) give it back, and the reported margin expansion comes from opex efficiency (AI in support, product-dev leverage), not from take rate.** The bear reading: the "flat take rate" hides that new businesses are being subsidised inside revenue rather than shown in S&M. The bull reading: once incentives roll off, 50+ bp of take rate is latent.
- Watch in Q3/Q4'26: implied take rate vs. the flat guide; any disclosure of incentive size; Q3's seasonal take rate against 17.9% last year.

## 5. Experiences + Services share of revenue

Airbnb does not disclose it. Evidence for a bound:

| Data point | Figure | Source |
|---|---|---|
| S-1 (2020) | "Substantially all of the bookings on our platform to date have come from nights"; no Experiences revenue disclosed | [SEC S-1 via Arival](https://arival.travel/experiences-ignored-tours-activities-the-airbnb-ipo/) |
| 2019 estimate | ~$35M Experiences revenue (≈0.7% of $4.8B revenue); ~$175M GBV at a 20% take; 40k experiences | [Arival, citing The Information](https://arival.travel/experiences-ignored-tours-activities-the-airbnb-ipo/) |
| Fee rates | Experiences ~20%, Services ~15% | `revenue_model_abnb_vs_bkng_expe.md`; [Zeevou](https://zeevou.com/blog/what-we-mean-about-airbnb-service-fees/) |
| Q3'25 | ~$200M FY25 investment in Services & Experiences; >110k host applications; "almost half of experiences bookings were not attached to an accommodation booking" | [Q3'25 letter](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q3/v2/Airbnb_Q3-2025-Shareholder-Letter.pdf) |
| Q1'26 | ~1/4 of new guests booking an Experience also book a stay or service; ~1/3 book a stay within 90 days; revenue "not separately quantified" | [Q1'26 call](https://www.fool.com/earnings/call-transcripts/2026/05/07/airbnb-abnb-q1-2026-earnings-call-transcript/) |
| Q2'26 | Experiences supply +~80% YoY; Services & Experiences "growing quickly but on a small base," "multi-year time horizon," not yet large enough to "contribute to overall nights and seats booked" | [Q2'26 newsroom](https://news.airbnb.com/airbnb-q2-2026-financial-results/), [GuruFocus call highlights](https://www.gurufocus.com/news/9015175/airbnb-inc-abnb-q2-2026-earnings-call-highlights-record-revenue-and-aidriven-growth-propel-strong-quarter) |

**Estimate: ~1% of revenue, ≤2% at the outside (FY26E).** Reasoning: management says the segment is too small to move a 148M-unit quarterly "nights and seats" metric, meaning seats are at most low-single-digit millions a quarter. At an illustrative $75 average experience/service ticket and 20% take, 3M seats/quarter ≈ $225M GBV ≈ $45M revenue ≈ 1.2% of a $3.6B quarter. The 2019 anchor (0.7%) and a $200M annual *investment* line that would be embarrassing against a $50M revenue line both point to ~1%. Treat as an estimate, not a disclosure; the memo should say "immaterial (<2%) today; a 2027–28 option, not a 2026 driver."

## Open items
- Pull Inside Airbnb listing counts for 2–3 European cities (Dec 2020 mandatory) vs. US control cities, 2019→2021, for a difference-in-differences on pro-host attrition — the only way to put a number on the 2020 episode.
- Re-run the elasticity model with a cross-platform leakage term once `direct_booking_threat_to_abnb.md` inputs are finalised.
- Log Q3'26 implied take rate (due ~Nov 5) against the flat guide.
