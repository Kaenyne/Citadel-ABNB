# Airbnb absolute hotel disclosure audit

As of September 7, 2026. Scope: public Airbnb/HotelTonight disclosures and an independent historical consumer-panel study. This is a disclosure audit, not an estimate of current hotel revenue.

**Result: no verified absolute quarterly or annual Airbnb hotel nights, hotel GBV, or hotel fee revenue was found in the searched corpus.** We obtained a substantially more complete primary-source archive and a genuine separate HotelTonight consumer-data lead. Neither supplies the missing current Airbnb hotel denominator.

## What was actually examined

- Downloaded and text-searched **69 official IR PDFs covering all 23 quarters from Q4 2020 through Q2 2026**: 23 shareholder letters, 23 earnings transcripts, and 23 financial filings. The files contain **3,224 PDF pages**, **709 occurrences of the hotel keyword across 42 documents**, and 69 distinct SHA-256 hashes. Keyword occurrences are search coverage, not independent economic observations. Relevant passages were inspected; this is not a claim that every page was manually read.
- Downloaded the **489-page November 16, 2020 IPO prospectus**, hosted by NYU with original SEC page references; inspected the acquisition note and hotel-related passages. The original SEC opening failed. The 2020 and 2021 annual acquisition notes were also read directly on SEC.
- Retrieved seven supplementary company/newswire HTML pages covering the 2017 HotelTonight partner footprint and 2018–2019 hotel initiatives. One March 2019 acquisition announcement now has essentially no substantive article body; it contributes no verified financial observation. The Spanish acquisition release is a translation of the English source, not independent corroboration.
- Retrieved a **23-page September 14, 2023 author version** of the McCarthy/Wilbur merger study. A different version on the FTC submission server returned 403 and was not used for quantitative extraction.
- The public IR event feed contains eight historical investor-conference entries through September 2025 with no attached transcripts; its presentation feed returned zero items. Conference remarks are an explicit remaining coverage gap. This audit does not assert exhaustive coverage of every interview, conference or paid broker note.

The reproducible collection script, PDFs/text, feed responses, hashes and search contexts are under `data/raw/hotel_absolute_disclosures/`. The source/claim ledger is `research/sources/hotel_absolute_disclosure_search.json`.

## Strongest numerical disclosures and their limits

| Period / source | Verified observation | What it establishes | What it does not establish |
|---|---|---|---|
| Q4 2025 call, pp. 17–18 | Hotel nights were a single-digit percentage; growth nearly twice the overall platform; **more than 100 NYC hotels and more than 20,000 rooms** available on the site | A bounded hotel mix description and a city supply anchor | Room-night allotment, occupancy, hotel ADR/commission, or absolute nights |
| Q1 2026 call, p. 9 | Hotel share still single-digit; hotel top-line metrics growing **more than twice** the whole business in recent quarters | Continued growth from a small starting mix | Exact absolute top-line metrics; the ratio does not isolate nights from revenue |
| Q2 2026 letter, p. 5 | **Thousands** of hotels across **more than 20** destinations; hotel night growth approximately **3x homes** | Rollout breadth and relative category growth | Exact hotels added, physical rooms, absolute nights, revenue or matched-hotel productivity |
| April 2019 acquisition close | HotelTonight room nights **>41% YoY in Q1 2019**, revenue **+39% in 2018**, new hotel partnerships **+110% since beginning 2018**, partner inquiries **3x normal in March 2019** | A historical supplier/demand growth episode | An absolute HotelTonight financial base or evidence about the 2026 product |
| January 2019 Airbnb hotel update | Available rooms in self-classified boutique/B&B/hostel/resort properties **+152% in 2018**; average rating **4.7/5** | Historical expansion of a broad hospitality taxonomy | Boutique-only property/room stock, causal conversion or current revenue |
| April 2017 HotelTonight company release | **>25,000 hotel partners**, **1,700 cities**, **>35 countries** | Historical separate-platform distribution footprint | Those hotels being simultaneously bookable, independent-only, or present on Airbnb |

Sources: [Q4 2025 official transcript](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb-Q4-25-Earnings-Call-Transcript.pdf), [Q1 2026 official transcript](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q1/Airbnb-Q1-26-Earnings-Call-Transcript.pdf), [Q2 2026 letter](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q2/v2/Airbnb-Q2-2026-Shareholder-Letter.pdf), [2019 acquisition close](https://news.airbnb.com/hoteltonight-and-airbnb-finalize-acquisition), [2019 hospitality update](https://news.airbnb.com/more-hotels-are-using-airbnb), [HotelTonight partner release](https://www.prnewswire.com/news-releases/aeg-and-hoteltonight-announce-exclusive-partnership-at-live-event-locations-in-the-los-angeles-metro-area-300443273.html).

The old growth narrative is a useful caution, not a matched comparison: COVID interrupted hotel investment, and the 2025–2026 product differs. Q4 2020 and Q4 2021 calls explicitly describe reduced hotel investment. Q4 2025 management cautioned that material growth contribution would take time. The Q2 2026 call places homes in the nearest growth horizon, with hotels/international in the next horizon. Its supplier-interest passage concerns hotels wanting to list; it does not quantify booking uplift at participating hotels. [Official Q2 2026 transcript, pp. 8, 10, 14](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q2/Airbnb-Q2-2026-Earnings-Call-Transcript.pdf)

## The acquisition accounting does not solve the denominator

The 2020 annual report, Note 6, identifies **$441.357 million of HotelTonight purchase consideration**, comprising $237.387 million cash, $201.079 million common stock and $2.891 million replacement options. It shows $88 million identifiable intangibles and $329.899 million goodwill. **These are acquisition-price and balance-sheet measurements, not revenue.** It consolidates HotelTonight from April 15, 2019 but does not publish separate post-acquisition revenue or a numeric combined pro forma revenue bridge. The note says the relevant acquisition results were immaterial without assigning a usable percentage ceiling. The IPO note and 2021 Note 18 do not supply the missing figures either. [2020 10-K, printed pp. 103–104](https://www.sec.gov/Archives/edgar/data/1559720/000155972021000010/airbnb-10k.htm), [2021 10-K, Note 18](https://www.sec.gov/Archives/edgar/data/1559720/000155972022000006/abnb-20211231.htm), [IPO prospectus mirror](https://pages.stern.nyu.edu/~adamodar/pc/blog/AirbnbProspectus.pdf).

Historical media estimates of HotelTonight revenue exist, but are not company-reported actuals. In particular, a 2019 Forbes article describes an estimated $60 million 2016 revenue figure. It cannot anchor current hotel revenue after acquisition, COVID and platform changes. [Forbes historical report](https://www.forbes.com/sites/bizcarson/2019/03/07/airbnb-to-buy-hoteltonight-as-it-pushes-deeper-into-hotel-booking-business/)

## A defensible conditional ceiling, not an estimate

If the Q2 2026 single-digit statement refers to the same quarter and a consistent hotel lodging-night definition, then:

`Hotel nights < 10% × accommodation nights ≤ 10% × (Nights and Seats Booked) = 14.83 million`.

The last input is the reported **148.3 million Q2 2026 Nights and Seats Booked**. Seats make this a deliberately loose upper bound. Management does not explicitly reconcile the category definition or share measurement window, so retain the condition. Do not label 14.83 million actual hotel nights, annualize it, call it physical hotel room nights, or monetize it with Airbnb's blended ADR/take rate. No non-trivial lower bound follows. The 3x growth ratio supplies no absolute denominator because the exact home-night growth rate and pure lodging-night total are also missing. [Q2 2026 letter](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q2/v2/Airbnb-Q2-2026-Shareholder-Letter.pdf)

## A real large-panel source: separate HotelTonight card data

McCarthy and Wilbur use an Earnest panel of **2.23 million U.S. consumers**, covering **January 2016–May 2022**. In their seven-platform travel category, HotelTonight represents **2.0% of paying-customer share in February 2019 and 1.9% in February 2020**; its mean payer payments are **$217–218**. Category paying cards increase from **89,532 to 100,540**. Means exclude the largest **0.1% of payments**. These are consumer-panel metrics, not company revenue or room nights. Underlying records are not provided. [Author paper, pp. 3–7, 12–13](https://raw.githubusercontent.com/kennethcwilbur/website/master/mccarthy-wilbur%20wp%202023%20did%20recent%20platform%20mergers%20reduce%20competition.pdf)

**Do not multiply category cards × HotelTonight share × mean payment into claimed actual sales.** The share denominator is not fully reconciled to unique category cards with multihoming, and means are trimmed. The useful finding is separable historical HotelTonight activity. Updated merchant data could track the legacy channel; product-level receipts would still be needed to distinguish hotels within Airbnb. No Earnest entitlement or raw records were obtained.

## Exact terminal follow-up

1. Search all ABNB transcripts, conference appearances and management interviews for `hotel`, `HotelTonight`, `boutique`, `room nights`, `hotel revenue`, `hotel GBV`, `hotel share`, `commission`, `take rate`, and `single digit`; return the complete surrounding exchange, event date, speaker and original source.
2. Export the **June 5, 2026 Jefferies hotel/experiences note and its latest post-Q2 update**, including forecast tables and stated underlying data. Public summaries describe a forecast, not actual hotel revenue. Obtain broker hotel revenue/nights estimates separately from management-sourced figures. [Public summary lead](https://finance.yahoo.com/markets/stocks/articles/airbnb-hotels-experiences-push-could-153900298.html)
3. Query Bloomberg/Refinitiv segment/operating-KPI fields for hotel nights, HotelTonight revenue and hotel GBV, including field descriptions and source documents. A populated custom/broker field must not be called company-reported. A missing field is a coverage result, not zero revenue.
4. Ask the terminal data catalog whether existing entitlements include **Earnest or another provider with separate HotelTonight merchant history**, and whether any product-level Airbnb receipt classifier distinguishes hotels from homes. Request monthly history, current coverage, unweighted counts, weights, card-country mix, refund/installment treatment and merchant-parent mapping before using a scaled estimate. This is a data request; no outreach, subscription purchase or terminal access occurred in this audit.

## Overlap and pitch disposition

The Q4 2025/Q1–Q2 2026 management hotel claims already appear in team hotel/WS11 work. Reuse them with attribution; changing from a third-party transcript to the official PDF improves provenance but creates no independent confirmation. The primary 2018–2019 expansion/acquisition evidence and author consumer-panel paper extend the present review; exact-URL matches and semantic overlap remain distinct concepts. Team notes were searched before the new audit; no claim is made about inaccessible personal research.

Current hotel revenue remains a scenario variable, with broker/model provenance attached. A pitch may compare required hotel production against observed rollout and obtainable channel data. It cannot claim to have measured absolute current hotel production or statistical significance from this archive alone.
