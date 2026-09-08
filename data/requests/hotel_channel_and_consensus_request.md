# Airbnb hotel research: Bloomberg / Refinitiv export request

Prepared September 7, 2026. Security: Airbnb, Inc., NASDAQ Class A common stock, Bloomberg **ABNB US Equity**. In LSEG Workspace select the matching Airbnb NASDAQ equity and retain its resolved identifier. Do not substitute HotelTonight's former private-company entity for Airbnb consolidated results.

**Confirmed destination scope: all 13 original listing-panel markets** — Austin, Barcelona, Chicago, London, Los Angeles, Mexico City, Nashville, New Orleans, New York City, Paris, Rome, San Diego and Sydney. The [active market file](../../analysis/config/hotel_markets_13.csv) is the scope authority. Retain all 13 in coverage exports, including explicit missing/zero-coverage rows; do not restrict the request to the six cities with current page captures or substitute country totals for destination markets. Company consensus remains consolidated ABNB, rather than 13 artificial geographic estimate series. Jessica's separate accommodation-choice list is not the hotel panel.

Use the [13-row provider coverage request](../processed/hotel_13_market_panel/provider_coverage_request_13.csv) for destination coverage diagnostics. [Existing hotel evidence by market](../../research/notes/2026-09-07_hotel-original-13-market-coverage.md) identifies the available supply references and unresolved production fields.

**Priority order: hotel-specific broker models first, current company expectations second, historical revisions third.** CSV/XLSX is useful for numbers; the original PDF or model page is useful for source definitions. Keep original exports locally with their dates and vendor labels. No credentials or API keys need to be sent in chat.

## 1. Hotel-specific research and model lines — most valuable missing input

Search the entitled company research and Bloomberg Intelligence/industry content for Airbnb AND each of:

`hotel revenue`, `hotel nights`, `hotel bookings`, `hotel gross bookings`, `hotel GBV`, `HotelTonight`, `hotel commission`, `hotel take rate`, `boutique`, `independent hotels`, `hotel credit`, `hotel room inventory`.

Window: January 1, 2024 through the latest available September 2026 date for the current program. Retain earlier notes only where they contain an absolute historical HotelTonight/hotel actual or explain the starting base. Include all distinct entitled brokers; revised versions of one model remain one broker lineage.

Specific lead: **Jefferies, approximately June 5, 2026**, hotel opportunity reportedly about $1bn annual revenue by 2030. Obtain the original note/model and any post-Q2-2026 update. The public description is a broker forecast, not company-reported actual or consensus.

Export the relevant table/model with:

| Field | Needed detail |
|---|---|
| Hotel nights | Absolute value; room nights versus reservations; booked versus stayed; net/gross cancellations |
| Hotel booking value | Gross room value versus guest payment including fees/taxes; currency; period |
| Airbnb hotel revenue | Net platform fee revenue versus hotels' own room revenue; revenue-recognition basis |
| Fee / take rate | Gross contractual versus realized after credits; applicable product/storefront |
| Supply | Unique hotels, physical rooms, allocated rooms; existing versus newly added |
| Costs | Credits, redemption, acquisition and launch spend, contribution assumptions |
| Forecast labels | Actual, estimated historical base, current forecast, scenario; FY2024–FY2028 where present and any 2030 target |
| Provenance | Broker/analyst, title/date, exact model row and source cited for any number described as an actual |

If the terminal has a hotel/HotelTonight segment or KPI field, export its description, source and actual/estimate status as well as the values. If none exists, record that result. A model row supplied by a broker is still an estimate unless tied to a company disclosure. Do not spend time generating a large table of missing hotel segment values.

## 2. Current company forecast — the comparison baseline

As of the latest available session, export **all entitled brokers plus consensus**, for **Q3 2026 through Q4 2028 and FY2026–FY2028**. Priority is Q4 2026–Q3 2027, the next four full quarters; later years test whether hotels change the longer-run outlook.

Metrics: **revenue, adjusted EBITDA, EBITDA margin, GAAP diluted EPS, adjusted EPS, nights/seats booked, GBV and ADR**. Include operating profit, SBC, diluted shares and free cash flow when available to reconcile earnings definitions. Preserve unavailable KPIs as missing. Do not apply a generic hotel industry metric to Airbnb.

For each metric-period export mean, median, low, high, standard deviation and contributor count where available, plus individual broker values, broker name/ID and estimate publication/update date. Include actuals on the same vendor's comparable basis. Keep GAAP and adjusted EPS separate.

Do not count the same broker from Bloomberg and Refinitiv as two independent opinions. Prefer one provider as the primary series and use the other to investigate discrepancies. Vendor contributor samples and definitions can differ.

## 3. Historical expectations — maximize usable history, preserve vintages

For the same company metrics, request:

- Daily consensus and individual-broker revision history from **January 1, 2024 to September 7, 2026**, retaining explicit target fiscal periods through FY2028 and available quarterly targets.
- For every earnings event from **Q4 2020 through Q2 2026**, the latest snapshot strictly before the release and the first, fifth and twentieth trading sessions after release, for the reported quarter, next quarter and relevant fiscal years. Mark post-event windows not yet complete as missing.
- If easy to obtain, extend the daily history back to the December 2020 IPO. The extra daily rows improve timing resolution, not the number of independent earnings events.

The existing [Theo request workbook](../../theos-past-research/outputs/workbooks/ABNB_consensus_data_request_template.xlsx) already provides 23 event timestamps and historical revenue/price requests. Reuse it rather than rebuilding those dates. The newer team WS04/WS16 public consensus reconstruction is useful corroboration; this request fills vendor-consistent, timestamped history and hotel-specific assumptions.

Required identifiers: instrument; metric; value; currency/scale; fiscal period start/end; estimate timestamp; export/as-of timestamp and timezone; broker ID; statistic; actual/estimate flag; accounting basis; vendor field/mnemonic; supplied parameters; contributor count; missing-reason/status.

**Period warning:** an FY1/FQ1 series rolls its target over time. Export fixed fiscal-period identities, or include the target period on every row. A current estimate cannot reconstruct what investors expected before a historical print. Unchanged daily estimates must retain their original estimate date.

## Verified routes and limits

Bloomberg describes company/broker/segment estimate comparisons and research access; precise field availability depends on entitlement and coverage. [Bloomberg investor-relations workflow](https://professional.bloomberg.com/institutions/corporations/investor-relations/)

LSEG documents company guidance, individual broker revenue estimates and daily consensus history. Its example fields include `TR.RevenueEstValue`, `.date`, `.brokername`, `.analystname`, `.analystcode`, `TR.RevenueMean`, `TR.RevenueNumIncEstimates` and `TR.EPSMean`. Use Workspace's Data Item Browser / export builder to select other metrics and confirm fixed-period/date behavior. These are documented field families, **not a tested ABNB extraction script**. [LSEG official example, updated July 2025](https://developers.lseg.com/en/article-catalog/article/fundamentals-estimates-dcf)

Neither subscription is assumed to contain Airbnb's undisclosed actual hotel revenue. The purpose is to find any absolute figure with provenance and establish the estimates the stock is being assessed against. No terminal extraction has been performed in this session.

## 4. Existing alternative-data entitlements — a coverage check before a full feed

Check existing subscriptions/catalog access for **Measurable AI travel receipts**, **Earnest HotelTonight merchant data**, or hotel PMS/channel production. Terminal access by itself does not imply these entitlements. Measurable's Bloomberg distribution footnote applies to its in-app-purchase data, so Airbnb/travel distribution through Bloomberg remains unverified.

Request a small *coverage table covering the entire available population*, not ten hand-picked booking examples: month × consumer-origin country × hotel-destination market × storefront, from January 2024 through the latest complete 2026 month (older reliable history welcome). Fields: raw receipts, deduplicated reservations, gross/cancelled/uncancelled bookings, reserved room nights, booking value, active panel consumers, matched physical hotels, hotel/home/unknown classifications, separate HotelTonight, and null rates for each field. Include all covered destinations; preserve geography so the final market scope can be applied without discarding data. NYC needs a destination-specific count.

Only a satisfactory coverage table justifies processing the full feed. The [machine-readable panel specification](hotel_channel_panel_schema.json) details stable property and reservation IDs, timestamps, source/storefront lineage, room nights, refunds, commissions, all-channel outcomes and inventory. Pseudonymous IDs are sufficient; guest names, emails and payment credentials are unnecessary. Retain unknown classification and missing periods explicitly.

Measurable's current article describes approximately 200,000 Hong Kong-consumer travel receipts across six platforms including Airbnb, **not 200,000 Airbnb hotel transactions**. Its public generic travel dictionary is an Agoda example, so Airbnb hotel fields must be demonstrated in the actual export. [Current provider study](https://blog.measurable.ai/2026/08/05/mainland-china-overtakes-japan-hong-kong-travel-data/), [coverage map](https://file.measurable.ai/coverage.pdf)

For a true global boutique/independent room TAM, also check whether an existing hotel-census entitlement supplies property ID/address, operating status, physical rooms, brand affiliation and operator/owner. Keep boutique positioning, independence and chain membership as separate fields; a size cutoff alone is insufficient. No such entitlement or global hotel census was obtained in this session.

## Next dated disclosure opportunity

Chesky is scheduled to speak on **September 8, 2026 at 6:05pm ET** at Goldman Sachs Communacopia. Add the full transcript to the hotel keyword search when it is published; a hotel update is not guaranteed. [Official event announcement](https://investors.airbnb.com/press-releases/news-details/2026/Airbnb-to-Participate-in-the-Goldman-Sachs-Communacopia--Technology-Conference-2026/default.aspx)
