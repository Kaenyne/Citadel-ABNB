# ABNB earnings calls: who asks, what they ask, and what management will not put a number on

- **Sources:** all 23 earnings-call transcripts Q4 2020 to Q2 2026. Official FactSet corrected transcripts from the Airbnb IR CDN for Q4 2021 and Q1 2023 to Q2 2026 (15 calls); stockanalysis.com web transcripts for Q4 2020 to Q4 2022 (8 calls). Source IDs S35 and S36 in `research/sources/README.md`. Raw text sits in `data/raw/transcripts/` (gitignored).
- **Date:** 2026-09-05
- **Author:** Krishang Surapaneni (compiled with Claude Code)
- **Datasets:** `data/processed/abnb_call_roster.csv`, `abnb_call_roster_churn.csv`, `abnb_call_topics.csv`, `abnb_declined_to_quantify.csv`. All four rebuild with `python analysis/src/transcript_analytics.py`.
- **Builds on:** `research/airbnb_earnings_call_study.md` (sentiment by quarter, topic mix, narrative eras) and the margin-drivers note on branch `krish/margin-drivers` (section 5 guidance log, section 9 open items). This note does not repeat those. It adds the roster, a speaker-split topic count, and the decline log.

---

## 1. Bottom line

1. **The sell-side following is thinning at the edges and stable at the core.** Analysts asking per call: 15.0 in 2022, 13.5 in 2023, 13.8 in 2024, 13.5 in 2025, 11.5 across the two 2026 calls. Questions per call fell from 36 (2022) to 22 (2026). 31 firms have asked a question over 23 calls; 14 of them showed up on a 2026 call. Six firms have asked in every year (Morgan Stanley, Goldman Sachs, Bank of America, Oppenheimer, Jefferies, TD Cowen).
2. **No new house has picked up the name since 2024.** The only "new" firms since 2024 are B. Riley (Q1 2024) and BNP Paribas (Q1 2026), and both are analysts who moved (Naved Khan from Truist, Nick Jones from Citizens JMP). Seven firms have not asked since 2023 or earlier: Credit Suisse (folded into UBS), Needham, Wolfe Research, Piper Sandler, RBC, Loop Capital, Canaccord. A shrinking Q&A roster on a stock this large is a mild negative for liquidity of ideas and a mild positive for variant perception.
3. **Management talks volume and margin; analysts ask about take rate, marketing, hotels and regulation.** Per 1,000 words, prepared remarks mention nights and demand 13.9 times, supply and hosts 13.9, margin and EBITDA 6.4. Analysts mention take rate 2.3 times as often as prepared remarks do, marketing 2.8 times, hotels 1.6 times, regulation 4.9 times (small base). Margin runs the other way: management volunteers it 3 times as often as analysts ask.
4. **Take rate was never in the prepared remarks until 2025.** Zero prepared-remark mentions in 2020 to 2024 while analysts asked every year, peaking at 3.5 mentions per 1,000 words in 2023. Management began volunteering it in 2025 (0.5) and 2026 (3.1) once the single service fee, insurance and Reserve Now, Pay Later made it move. The same pattern held for AI in reverse: by 2026 management mentions AI more in prepared remarks (4.9) and in answers (6.2) than analysts ask about it (3.7).
5. **37 requests for a number were declined or answered qualitatively**, 1.6 per call, with clusters in 2022 (10) and 2025 (10). By category: other KPI detail 14, guidance detail 8, new-business economics 6, market-level economics 3, take rate detail 2, long-term margin target 2, AI spend 2, headcount 0. Headcount is the one quantity management does answer (7% to 8% in 2022, about 1% in 2023, low-to-mid single digits for 2024).
6. **The four that matter for the pitch have never been answered with a number.** Experiences attach rate ("we don't have any numbers to share", Q2 2025) and seats as a share of Nights and Seats Booked ("indeed immaterial", not broken out, Q2 2025). Hotels scale and timeframe ("single-digit percent of nights booked", Q2 2026). AI spend ("will not affect the P&L", Q4 2025; inference cost "de minimis", Q2 2026), which sits next to Mertz on the same Q2 2026 call saying the guide "does assume a material increase in terms of the AI spend". Long-term margin ("I don't have a new long-term target", Q2 2023; "not going to give you a specific guide for 2027 and beyond", Q2 2026). The last numeric long-term margin target was "30% or greater" in February 2021.
7. **Next-year margin is declined in Q2 and Q3 and floored in February, every year.** 2021 target declined Feb 2021; 2025 declined Aug 2024; 2026 declined Aug and Nov 2025. Expect the FY2027 floor on the February 2027 call and nothing numeric before it.

---

## 2. Roster churn

Roster is Q&A only: one row per analyst per call, firm as stated by the operator or the transcript, normalised (Bank of America and BofA Securities are one firm; Cowen and TD Cowen; JMP and Citizens JMP; Evercore and Evercore ISI; Sanford Bernstein and Bernstein Autonomous; and so on). Full per-call table with new and dropped firms is in `abnb_call_roster_churn.csv`.

| Year | Calls | Analyst slots | Analysts per call | Distinct firms | Questions per call | Firms first seen this year | Firms not seen after this year |
|---|---|---|---|---|---|---|---|
| 2020 | 1 | 13 | 13.0 | 13 | 25 | (first call) | Canaccord Genuity |
| 2021 | 4 | 58 | 14.5 | 22 | 31 | Citizens JMP, D.A. Davidson, Evercore ISI, JPMorgan, Loop Capital, Mizuho, Needham, Truist, UBS, Wells Fargo, Wolfe Research | Loop Capital |
| 2022 | 4 | 60 | 15.0 | 24 | 36 | Bernstein, RBC Capital Markets | RBC Capital Markets, Wolfe Research |
| 2023 | 4 | 54 | 13.5 | 22 | 29 | Melius Research, Piper Sandler, Redburn Atlantic | Credit Suisse, Needham, Piper Sandler |
| 2024 | 4 | 55 | 13.8 | 20 | 28 | B. Riley | B. Riley, Citizens JMP, Truist |
| 2025 | 4 | 54 | 13.5 | 20 | 29 | none | Barclays, D.A. Davidson, Deutsche Bank, Evercore ISI, KeyBanc, Redburn Atlantic, UBS (not yet on a 2026 call) |
| 2026 | 2 | 23 | 11.5 | 14 | 22 | BNP Paribas | |

Reading it:

- **2021 looks like a wave of new coverage only because the Q4 2020 call was the first.** Initiations landed through 2021 and the roster peaked at 24 firms in 2022, when the calls were also longest (36 questions per call).
- **Since 2023 the roster has lost firms and gained none.** Credit Suisse disappeared with the UBS merger (Stephen Ju moved to UBS in Q1 2024). Needham, Wolfe, Piper Sandler and RBC stopped asking. B. Riley and BNP Paribas are the same two people, Naved Khan and Nick Jones, at new employers.
- **The 2026 calls are shorter and more concentrated.** 11 and 12 analysts asked, versus 15 to 17 at the 2022 peak. The seven firms last seen in 2025 include Evercore (Mahaney last asked Q4 2025), Deutsche Bank and UBS. Two calls is too few to call that a drop in coverage; it is a drop in who gets a slot.
- **The core has not moved.** Oppenheimer (Jed Kelly) has asked on 22 of 23 calls, TD Cowen (Kevin Kopelman) 19, Morgan Stanley (Brian Nowak) 18, Bank of America (Justin Post) 18, Evercore (Mark Mahaney) 18, JPMorgan (Doug Anmuth) 17, Wells Fargo 16, Jefferies 15, Mizuho 15. Evercore, Bank of America, UBS, Citi and Bernstein most often get the first question.
- **Four analysts changed firms** inside the sample: Lloyd Walmsley (Deutsche Bank to UBS to Mizuho), Stephen Ju (Credit Suisse to UBS), Naved Khan (Truist to B. Riley), Nick Jones (JMP/Citizens to BNP Paribas). Firm-level churn overstates true churn by about that much.

Top firms by appearances:

| Firm | Calls asked (of 23) | First | Last | Analysts |
|---|---|---|---|---|
| Oppenheimer | 22 | 2020Q4 | 2026Q2 | Jed Kelly |
| TD Cowen | 19 | 2020Q4 | 2026Q2 | Kevin Kopelman, Jake Seed |
| Morgan Stanley | 18 | 2020Q4 | 2026Q1 | Brian Nowak |
| Bank of America | 18 | 2020Q4 | 2026Q2 | Justin Post, Jen Shi |
| Evercore ISI | 18 | 2021Q1 | 2025Q4 | Mark Mahaney |
| JPMorgan | 17 | 2021Q3 | 2026Q2 | Doug Anmuth, Dae Lee |
| Wells Fargo | 16 | 2021Q1 | 2026Q2 | Brian Fitzgerald, Ken Gawrelski |
| Jefferies | 15 | 2020Q4 | 2026Q2 | Brent Thill, John Colantuoni |
| Mizuho | 15 | 2021Q1 | 2026Q2 | James Lee, Lloyd Walmsley |
| Deutsche Bank | 14 | 2020Q4 | 2025Q4 | Lee Horowitz, Lloyd Walmsley |
| Citi | 14 | 2020Q4 | 2026Q2 | Ron Josey, Jason Bazinet |
| Goldman Sachs | 13 | 2020Q4 | 2026Q2 | Eric Sheridan, Heath Terry |
| Bernstein | 13 | 2022Q3 | 2026Q2 | Richard Clarke |
| KeyBanc | 12 | 2020Q4 | 2025Q2 | Justin Patterson |
| Barclays | 12 | 2020Q4 | 2025Q3 | Mario Lu, Trevor Young |
| UBS | 12 | 2021Q4 | 2025Q4 | Lloyd Walmsley, Stephen Ju |
| Baird | 11 | 2020Q4 | 2026Q2 | Colin Sebastian |
| Credit Suisse | 11 | 2020Q4 | 2023Q2 | Stephen Ju |
| Citizens JMP | 9 | 2021Q4 | 2024Q2 | Nick Jones, Andrew Boone |
| Truist | 8 | 2021Q1 | 2024Q3 | Naved Khan, Patrick Scholes |
| Needham | 7 | 2021Q4 | 2023Q4 | Bernie McTernan |
| Wolfe Research | 6 | 2021Q1 | 2022Q4 | Deepak Mathivanan |
| D.A. Davidson | 4 | 2021Q1 | 2025Q1 | Tom White |
| Melius Research | 4 | 2023Q3 | 2026Q2 | Conor Cunningham |
| Redburn Atlantic | 2 | 2023Q4 | 2025Q1 | Alex Brignall |
| B. Riley | 2 | 2024Q1 | 2024Q4 | Naved Khan |
| Canaccord, Loop Capital, RBC, Piper Sandler, BNP Paribas | 1 each | | | Michael Graham, Rob Sanderson, Brad Erickson, Tom Champion, Nick Jones |

---

## 3. Topic mix: management versus analysts

Method: a fixed dictionary of 14 topics (regex keyword lists in `TOPICS` in the script), counted as mentions per 1,000 words in three speaker buckets: management prepared remarks (31,800 words over 23 calls), management answers in Q&A (151,600 words), analyst questions (35,000 words). Rates, not raw counts, because the buckets differ in size by 5x. Per-call counts are in `abnb_call_topics.csv`.

All 23 calls, mentions per 1,000 words:

| Topic | Mgmt prepared | Mgmt Q&A answers | Analyst questions | Analyst / prepared |
|---|---|---|---|---|
| margin_ebitda | 6.41 | 1.63 | 2.17 | 0.3x |
| take_rate_fees | 0.60 | 0.73 | 1.37 | 2.3x |
| adr_pricing | 3.49 | 4.12 | 4.09 | 1.2x |
| nights_demand | 13.92 | 5.77 | 7.12 | 0.5x |
| supply_hosts | 13.89 | 9.05 | 7.55 | 0.5x |
| marketing | 0.75 | 2.18 | 2.12 | 2.8x |
| ai | 1.79 | 1.99 | 1.32 | 0.7x |
| international_expansion | 3.83 | 4.12 | 3.49 | 0.9x |
| services_experiences | 3.08 | 2.51 | 3.60 | 1.2x |
| hotels | 1.16 | 2.78 | 1.83 | 1.6x |
| regulation | 0.09 | 0.55 | 0.46 | 4.9x |
| buyback_capital | 2.04 | 0.40 | 0.54 | 0.3x |
| fx | 1.01 | 0.33 | 0.60 | 0.6x |
| guidance | 1.79 | 0.73 | 1.83 | 1.0x |

By year, analysts (A) versus management prepared remarks (M), mentions per 1,000 words:

| Topic | 2020 A / M | 2021 A / M | 2022 A / M | 2023 A / M | 2024 A / M | 2025 A / M | 2026 A / M |
|---|---|---|---|---|---|---|---|
| margin_ebitda | 0.6 / 2.4 | 1.2 / 3.7 | 3.1 / 9.6 | 1.7 / 3.7 | 2.5 / 7.9 | 2.5 / 7.6 | 2.3 / 7.2 |
| take_rate_fees | 0.6 / 0.0 | 2.2 / 0.0 | 0.8 / 0.0 | 3.5 / 0.0 | 0.5 / 0.0 | 0.5 / 0.5 | 0.9 / 3.1 |
| adr_pricing | 2.5 / 0.0 | 3.4 / 0.6 | 5.0 / 0.3 | 7.2 / 11.0 | 2.8 / 0.5 | 2.5 / 3.8 | 3.7 / 5.1 |
| nights_demand | 3.8 / 0.8 | 9.3 / 8.7 | 7.2 / 18.7 | 7.2 / 13.2 | 6.7 / 18.0 | 6.4 / 12.2 | 6.0 / 18.8 |
| supply_hosts | 12.7 / 17.0 | 11.5 / 16.6 | 7.3 / 15.0 | 7.9 / 21.6 | 6.7 / 21.2 | 3.0 / 4.8 | 6.4 / 9.8 |
| marketing | 3.2 / 1.6 | 2.9 / 1.7 | 2.0 / 0.0 | 2.4 / 0.0 | 1.9 / 0.7 | 1.8 / 0.8 | 0.0 / 0.8 |
| ai | 0.0 / 0.0 | 0.0 / 0.0 | 0.3 / 0.0 | 1.3 / 1.1 | 1.2 / 0.0 | 3.9 / 3.6 | 3.7 / 4.9 |
| international_expansion | 0.6 / 0.0 | 3.1 / 2.5 | 3.8 / 1.6 | 7.0 / 6.7 | 3.2 / 4.3 | 2.5 / 4.4 | 0.5 / 3.9 |
| services_experiences | 1.3 / 0.0 | 1.9 / 0.2 | 2.0 / 1.6 | 2.6 / 3.0 | 5.8 / 4.7 | 7.6 / 5.7 | 2.8 / 2.5 |
| hotels | 0.6 / 0.0 | 1.7 / 0.0 | 0.9 / 0.0 | 0.6 / 0.4 | 1.6 / 0.7 | 2.8 / 1.9 | 7.8 / 3.5 |
| regulation | 0.0 / 0.0 | 0.6 / 0.0 | 0.1 / 0.0 | 0.4 / 0.0 | 1.2 / 0.0 | 0.0 / 0.3 | 0.9 / 0.2 |
| buyback_capital | 0.6 / 0.0 | 0.5 / 0.0 | 1.4 / 0.8 | 0.2 / 2.6 | 0.4 / 2.3 | 0.0 / 3.8 | 0.5 / 2.3 |
| fx | 0.0 / 0.0 | 0.0 / 0.0 | 1.4 / 1.3 | 0.4 / 0.2 | 0.0 / 1.4 | 1.4 / 1.6 | 0.0 / 1.6 |
| guidance | 0.6 / 0.8 | 0.6 / 0.2 | 1.9 / 0.5 | 2.8 / 0.2 | 2.3 / 1.8 | 2.7 / 2.6 | 0.5 / 4.9 |

Where the two diverge, and what analysts keep asking that management does not volunteer:

- **Take rate.** Not one prepared-remark mention in five years (2020 to 2024). Analysts asked every year and hardest in 2023 (3.5 per 1,000 words), the year of total-price display and the lower fee after the third month. Management started volunteering it only when it began to move in its favour (single fee, insurance, RNPL) in 2025 and 2026. The two take-rate declines in the log (Q2 2022, Q3 2022) both amount to "underlying take rate unchanged, the rest is timing".
- **Marketing.** Analysts ask about marketing spend, ROI and the brand-versus-performance split at 2.8 times the prepared-remark rate. Management answers in Q&A (2.2) but does not lead with it. Given that sales and marketing is the one cost line that has grown as a share of revenue since 2022 (margin-drivers note, section 3), this is the gap to keep pressing.
- **Hotels.** The most lopsided topic of 2026: analysts 7.8 per 1,000 words, prepared remarks 3.5, answers 6.2. Analysts want scale and timeframe; management gives share of nights and a growth multiple.
- **Regulation.** Nearly absent from prepared remarks (0.1 over the whole period). Analyst interest spiked in 2024 (New York Local Law 18, Barcelona) and again in 2026. Management addresses it only when asked.
- **Margin and buybacks run the other way.** Prepared remarks mention margin and EBITDA 3 times as often as analysts ask, and capital return 4 times as often. Both are recap items in the results summary. Analysts treat the margin as settled and ask about growth.
- **AI flipped.** In 2023 and 2024 analysts raised AI slightly more than management did in prepared remarks. By 2026 management leads on it in both prepared remarks and answers. This matches the narrative-era shift in `airbnb_earnings_call_study.md` (AI-native framing arriving in Q2 2026).
- **Supply and demand are management's home ground.** Nights and supply together make up more than half of all prepared-remark topic mentions in every year but 2025, when the Summer Release pushed services and experiences to the front (5.7) and supply mentions fell to 4.8.

---

## 4. Declined to quantify

Method: a rule-based pass over all 489 analyst turns flagged 73 questions containing a quantity request (how much, quantify, size, what percent, basis points, contribution, attach rate, unit economics, target, headcount, capex, break out, and similar). Every candidate was read, together with a hand sweep of every margin, take-rate, new-business, AI-spend and guidance question that the regex missed. 37 were kept as true declines or qualitative answers. Cases where management gave a number, even a rough one, were dropped (for example APAC at 12% of the business, headcount growth ranges, the 100 to 200 bps Easter effect, China pre-COVID at low-single-digit percent of GBV). The script checks every excerpt verbatim against the transcript and fails the build if one is missing.

The four that matter most for the pitch:

1. **Services and experiences unit economics.** Never quantified in five asks. Attach rate: "We don't have any numbers to share as far as what we see for potential attach rate" (Chesky, Q2 2025). Seats share of Nights and Seats Booked: "we have not historically broken out nights booked versus experiences booked. We were not going to do that today. What I can tell you is that the seats booked today are indeed immaterial" (Mertz, Q2 2025). Contribution next year: answered with "about half don't have an Airbnb stay associated" (Chesky, Q3 2025). Unit economics by category: "car rentals is going to be the biggest one by far" (Chesky, Q2 2026). This is the $200M-a-year investment line in the margin guide with no disclosed return.
2. **Hotels economics.** Asked for timeframe or scale: "hotels are only a single-digit percent of nights booked on the platform, so a relatively small segment" plus a growth multiple (Mertz, Q2 2026). No take rate, no contribution margin, no target share. The margin-drivers note flags hotel take rate as a mix risk; management has not said whether it is above or below the homes take rate.
3. **AI spend.** Chesky, Q4 2025: "our investment in AI will not affect the P&L. I don't think you'll see it in the P&L." Chesky, Q2 2026: "the inference cost of Airbnb are kind of de minimis relative to the ROI of our business model." Mertz, same Q2 2026 call, on the FY margin guide: it "does assume a material increase in terms of the AI spend". Two answers to the same question on one call. The dollar figure has not been asked for directly and should be.
4. **Long-term margin target.** Stephenson, Q2 2023: "I don't have a new long-term target." Mertz, Q2 2026: "I'm not going to give you a specific guide for 2027 and beyond", then "there's a relative floor". The only numeric long-term target on record is "30% EBITDA margins or greater" (Stephenson, Feb 2021), which the company passed in 2022. Every FY margin number since has been a floor set in February.

Full list by category:

### Contribution margin of new businesses (6)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2024Q3 | John Colantuoni, Jefferies | Size of the tech and marketing investment behind the Experiences relaunch | "I do not anticipate very many businesses in the next five years are going to need significant investments." | Brian Chesky |
| 2025Q2 | Mark Mahaney, Evercore ISI | Target attach rate for Experiences | "We don't have any numbers to share as far as what we see for potential attach rate." | Brian Chesky |
| 2025Q2 | Trevor Young, Barclays | Share of Nights and Seats Booked that is seats (1% or zero?) | "we have not historically broken out nights booked versus experiences booked. We were not going to do that today. What I can tell you is that the seats booked today are indeed immaterial." | Ellie Mertz |
| 2025Q3 | Justin Post, Bank of America | Whether experiences contribute yet and the expected contribution next year | "The first thing we're seeing is that a large percentage of people that are booking experiences, about half don't have an Airbnb stay associated with the reservation." | Brian Chesky |
| 2026Q2 | Lloyd Walmsley, Mizuho | Timeframe or scale of the hotels opportunity | "hotels are only a single- digit percent of nights booked on the platform, so a relatively small segment." | Ellie Mertz |
| 2026Q2 | Colin Sebastian, Baird | Unit economics of the new service categories relative to expectations | "car rentals is going to be the biggest one by far just because of how big the asset is" | Brian Chesky |

### Long-term margin target (2)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2023Q2 | Tom Champion, Piper Sandler | Long-term EBITDA margin potential | "But all of that said, I don't have a new long-term target. I'm just proud of the fact that we've been able to deliver the profitability we have as quickly as we have." | David E. Stephenson |
| 2026Q2 | Eric Sheridan, Goldman Sachs | Long-term incremental margins and how much gets reinvested versus dropping through | "So I'm not going to give you a specific guide for 2027 and beyond, but I think looking at our track record, you can even see a couple of things." | Ellie Mertz |

### Capex and AI spend (2)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2025Q4 | Brian Nowak, Morgan Stanley | P&L (gross margin) impact of increased AI investment in 2026 versus 2025 | "So unlike other companies, we're not building models. We do not have a huge CapEx cost base. So our investment in AI will not affect the P&L. I don't think you'll see it in the P&L." | Brian Chesky |
| 2026Q2 | John Colantuoni, Jefferies | Impact of the AI-native transition on product costs | "the inference cost of Airbnb are kind of de minimis relative to the ROI of our business model" | Brian Chesky |

### Take rate detail (2)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2022Q2 | John Colantuoni, Jefferies | Puts and takes behind the higher implied Q3 take rate | "The underlying kind of if you shifted take rate is unchanged. You know, any of the variation in take rate is just a timing difference between revenue stays versus timing of bookings." | Dave Stephenson (inferred) |
| 2022Q3 | Justin Post, Bank of America | Confirm the operational take rate is above 14% and stable | "We do not have an intention to increase take rate." | Brian Chesky (inferred) |

### Market-level economics (3)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2022Q2 | Mario Lu, Barclays | How large China outbound bookings are | "We focused all that on outbound, which we think is the greater prize and the most important part for the long term." | Dave Stephenson (inferred) |
| 2024Q1 | Conor Cunningham, Melius Research | Take rate, ADR and profit of expansion markets versus the core | "what we've been able to achieve over time is very strong economics at the booking level for a wide range of ADRs. So it is not a concern for us to be expanding in markets where the average ADRs are lower." | Ellie Mertz |
| 2025Q1 | Tom White, D.A. Davidson | Profitability of expansion markets relative to core markets, level and pace | "we're able to generate very attractive contribution profit at a variety of ADRs, and that typically is the biggest determinant on the overall level of profitability at a market level" | Ellie Mertz |

### Consensus and guidance detail (8)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2020Q4 | Justin Post, Bank of America | Margin target for 2021 to model against | "I'd love to give you specific targets for 2021, but it's just too hard to know what our revenue is going to be, and so therefore, kind of the flow through to profitability." | Dave Stephenson (inferred) |
| 2021Q3 | Kevin Kopelman, TD Cowen | Q4-to-date booking growth versus 2019 | "I don't have a specific percentage that we're sharing on the call today." | Dave Stephenson (inferred) |
| 2023Q3 | Brian Nowak, Morgan Stanley | Confirm the Q4 nights-growth range implied by the guide | "In terms of the nights guide, we're just seeing some variability in our nights demand here early in the quarter. And so, we're just being cautious with that guide. And so, we're not being specific on it" | David E. Stephenson |
| 2024Q2 | Justin Patterson, KeyBanc | How long the investment cycle lasts and when returns show (2025 margin) | "we obviously have not given a guide for 2025. We'll provide you a view on 2025 as it approaches." | Ellie Mertz |
| 2025Q1 | Kevin Kopelman, TD Cowen | Geo mix versus underlying softness in the Q2 ADR guide, and the FX assumption | "One is there is underlying real price appreciation, which is a tailwind in terms of bringing prices up. There is a movement in terms of the FX headwinds." | Ellie Mertz |
| 2025Q1 | Ron Josey, Citi | Contribution of the May 13 launches included in guidance | "the impact from a top line in the current quarter will be relatively modest, whereas as we scale those offerings, they will obviously increasingly contribute to the top line." | Ellie Mertz |
| 2025Q2 | Kevin Kopelman, TD Cowen | How 2026 margins will be managed given new launches | "On margins, I'm not going to guide right now to 2026." | Ellie Mertz |
| 2025Q3 | Lee Horowitz, Deutsche Bank | 2026 incremental investment plan; how much of the $200M is sticky | "Obviously we're not providing explicit guidance for 2026 margins today." | Ellie Mertz |

### Headcount (0)

No declines. Headcount is the one quantity management answers when asked: 7% to 8% hiring plan (Chesky, Q3 2022), about 1% growth in 2023 and low-to-mid single digits planned for 2024 (Stephenson, Q4 2023), fixed headcount up about 4% (Q3 2023).

### Other KPI detail (14)

| Call | Analyst, firm | Asked | Answer (verbatim) | Speaker |
|---|---|---|---|---|
| 2021Q2 | Brian Fitzgerald, Wells Fargo | How much of their calendar new hosts make available; professional vs casual mix | "We continue to see 90% of our hosts are individual hosts. That remains to be the case." | Dave Stephenson (inferred) |
| 2021Q3 | Stephen Ju, Credit Suisse | Share of users with young unvaccinated children, to size pent-up demand | "I don't think we have that data specifically, but I can just share a couple high-level thoughts with you." | Brian Chesky (inferred) |
| 2021Q3 | Mark Mahaney, Evercore ISI | How significant the APAC short-term-rental restrictions are as a drag | "we're not anticipating that any short-term rental regulation changes as being a major negative drag on our business over time." | Dave Stephenson (inferred) |
| 2021Q4 | Mark Mahaney, Evercore ISI | Size of the long-term-stay effect on ADR (accretive or dilutive, by how much) | "On the ADR, long-term stays are dilutive on the ADR as the percentage goes up" | David E. Stephenson |
| 2022Q2 | Kevin Kopelman, TD Cowen | Listings growth rate excluding the China domestic shutdown | "what we've stated is that we're still well above 6 million active listings, even excluding the takedown of the China domestic." | Dave Stephenson (inferred) |
| 2022Q3 | Naved Khan, Truist | ROI on advertising dollars | "Our brand marketing results are delivering excellent results overall with a strong rate of return, and it's been so successful that we're actually expanding to more countries" | Dave Stephenson (inferred) |
| 2022Q3 | Richard Clarke, Bernstein | Quantify the ADR headwind as urban mix returns | "Urban is strengthening each quarter. That's the trend that we're seeing on the urban side." | Dave Stephenson (inferred) |
| 2022Q4 | Brian Nowak, Morgan Stanley | New-guest growth in 2022 and 2023; adoption metrics for I'm Flexible (a KPI disclosed in 2021 and dropped) | "on the new guests, we don't disclose the exact number of the, you know, new guest growth." | Dave Stephenson (inferred) |
| 2022Q4 | Mario Lu, Barclays | Breakdown of the 900,000 listings added: new versus reactivated | "I don't have any other more specific breakout to give to you." | Dave Stephenson (inferred) |
| 2022Q4 | Stephen Ju, Credit Suisse | Aggregate host availability growth versus host-count growth | "What we noticed is over time, hosts generally increase the number of days available, and they tend to get more productive every year." | Brian Chesky (inferred) |
| 2022Q4 | Bernie McTernan, Needham | FX drag on 2022 EBITDA margin | "Maybe we can follow up offline on that. I mean, it was a material, you know, probably several hundred million dollars, but we would have to give you the... Maybe we'll work offline on the specific calculation." | Dave Stephenson (inferred) |
| 2023Q1 | Mario Lu, Barclays | Percent of listings exclusive to Airbnb (not addressed; answer covered loyalty only) | "I always believe that the best loyalty program is people loving your product and if they love your products, they come back." | Brian Chesky |
| 2024Q1 | Nick Jones, Citizens JMP | Share of supply removed for quality and how many hosts return | "I don't have the stats on the top of my head" | Brian Chesky |
| 2025Q3 | Richard Clarke, Bernstein | Percent of the US acceleration that came from Reserve Now, Pay Later | "So about 70% of people that we offer Reserve Now, Pay Later, take us up on that offering." | Ellie Mertz |

Who asks the questions that get declined: Kevin Kopelman 4, then Justin Post, Brian Nowak, John Colantuoni, Mark Mahaney and Mario Lu with 3 each. The pattern is the same one the margin-drivers note found on the guidance log: management quantifies the core (nights, ADR, headcount, marketing as a share of revenue) and describes the new (services, experiences, hotels, AI, expansion-market economics).

---

## 5. Method and caveats

- **Two transcript grades.** Q4 2021 and Q1 2023 to Q2 2026 are FactSet corrected transcripts with tagged speakers, titles and firm names. Q4 2020 to Q4 2022 (Q4 2021 excepted) are stockanalysis.com web transcripts with no speaker tags at all. For those eight calls the roster comes from the operator's hand-off line ("Your next question comes from Brian Nowak with Morgan Stanley"), which is reliable, and the speaker role of each paragraph is inferred: the paragraph after a hand-off is the analyst; later paragraphs are management if they contain a hand-off phrase ("Dave, do you want to take this?"), address the analyst by first name, or use "we/our" more than "you/your", otherwise analyst. Spot checks show occasional misattribution of analyst follow-ups to management and of management closing lines to the analyst. Treat the 2020 to 2022 analyst word counts and question counts as approximate. Speakers in the decline log for those calls are marked "(inferred)".
- **Q&A only for the roster.** Analysts named in the participant list who did not ask are not counted. Order asked is the operator's order. Number of questions is the count of question marks in the analyst's turns, so a two-part question with one question mark counts once.
- **Firm normalisation** collapses operator shorthand and legal names into one label per house. Analyst moves between firms (four in the sample) are recorded as firm churn. Stand-ins are attributed to the named analyst's firm: Jen Shi for Justin Post (Q3 2021), "Ben" for Mark Mahaney (Q3 2021), "Chris" for Lloyd Walmsley (Q4 2022), Jake Seed for Kevin Kopelman (Q2 2023). The roster keeps the name the operator announced.
- **Topic counts are keyword mentions, not classified sentences.** The dictionary is in `TOPICS` in the script. Known trade-offs: "services" excludes "customer service", "guest services" and "host services"; "experiences" excludes the KPI name "nights and experiences booked"; "regulation" excludes the generic word "policy" so it does not pick up cancellation policy; "nights_demand" includes "seats" from 2025 on. Prepared remarks are short on Airbnb calls (about 1,400 words per call), so a rare topic's per-1,000-word rate in a single year can swing on a handful of mentions. The 2020 column is one call. The 2026 column is two.
- **Decline log.** Rule-based candidates (73 of 489 analyst turns) were read in full together with the following management turns, plus a manual sweep of margin, take-rate, new-business, AI-spend, guidance, consensus and headcount questions that the regex did not flag. Kept only where a specific quantity was requested and none was given, or the answer was directional only. Borderline items were dropped rather than kept. Excerpts are verbatim and capped at 300 characters; the build fails if an excerpt is not found in the transcript. Some IR transcripts render em dashes as a replacement character; excerpts avoid those spans.
- **Not done.** No sentiment scoring (see `airbnb_earnings_call_study.md` section 5). No prepared-remark text for the participant lists, so the roster cannot say who was invited but not called on. Web transcripts were not re-fetched; the eight cached files were used as is.
