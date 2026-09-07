# Quantifying Airbnb's housing-related regulatory exposure

**Follow-up:** [Matched inventory and performance evidence](../phase2/README.md) refines Barcelona and Maui cohorts, adds a NYC activity benchmark and a versioned Hawaii performance panel, and provides a companion sensitivity workbook. The tables below preserve the first-pass inventory and assumptions.

Research cutoff: **5 September 2026**. This is the first quantitative extension of the regulatory database. It covers all 32 prior factors and adds Lisbon's inactive-registration cleanup. It includes 20 downloaded Airbnb market snapshots, 32 inventory records, seven Spanish supply histories, 13 quarters of guidance/actual comparisons and eight editable annualized illustrations.

**The main finding is that substantial local supply losses can coexist with resilient Airbnb revenue. The missing bridge is the booked revenue of the affected properties and how much Airbnb retains elsewhere. Listing counts alone cannot establish a consolidated earnings loss.**

## What is measured so far

| Market | Latest inventory counted | What could actually be affected |
|---|---:|---|
| New York City | 30,234 Airbnb listing IDs, Aug 2026; 5,813 advertise minimum stays below 30 nights | Historical restriction sharply reduced short-stay supply. Current IDs include longer stays, hosted stays and hotels. AirDNA reported an 83% short-stay decline one year after enforcement. |
| Spain | 341,001 tourist dwellings across platforms, May 2026 | Reported 65,122 Airbnb ads removed in July 2025 are an enforcement cohort, not necessarily distinct or productive dwellings. Do not divide this count by the INE denominator to obtain an Airbnb revenue share. |
| Barcelona | 15,406 Airbnb IDs, Jun 2026; 7,069 entire homes with minimum stays below 30 nights | City policy targets 10,101 tourist-apartment licences in 2028 across channels. In the Airbnb snapshot, 6,698 entire-home short-minimum listings contain HUTB licence text. These are candidate matches, not verified legal affected units. |
| Maui County | 12,687 Airbnb IDs, Jun 2026; 11,473 short-minimum entire homes | County identifies 6,208 active Minatoya units in May 2024. Exposure depends on the 2029/2031 phases and rezoning. The 4,519 proposed rezoning candidates cannot be subtracted without matching the cohorts. |
| Lisbon municipality | 17,098 Airbnb IDs, Jun 2026; 12,227 short-minimum entire homes | Containment rules primarily constrain entry and certain transfers. Separately, 6,765 registrations were cancelled as inactive. Registry cleanup can have little immediate revenue effect if the properties were already inactive. |
| Athens | 14,342 Airbnb IDs, Jun 2026; 13,276 short-minimum entire homes | Freeze covers districts 1–3, not the whole city. Need exact district matching, prevented entrants and transfers. It does not mandate removal of every grandfathered listing. |
| Thessaloniki municipality | 4,408 Airbnb IDs, Jun 2026; 4,244 short-minimum entire homes | Only the first municipal community is covered. Exact affected subdistrict count remains unresolved. |
| Paris | 77,679 Airbnb IDs, Jun 2026; 54,280 short-minimum entire homes | Only relevant primary residences previously operating beyond 90 nights lose capacity under the 120-to-90 rule. Entire-home status does not establish primary residence. |
| Amsterdam | 10,465 Airbnb IDs, Jun 2026; 8,421 short-minimum entire homes | The tighter 30-to-15 cap affects eight neighbourhoods and the relevant holiday-rental category. Exact polygons and B&B exclusions need matching. |
| British Columbia | Just over 23,000 active STR listings, government release Jun 2026 | Down from about 28,000. Exact Airbnb share and regulatory causality are unknown. Vancouver and Victoria snapshots are available, but do not represent all BC. |
| Montreal | 10,677 Airbnb IDs, Jun 2026; 4,159 short-minimum entire homes | Need to identify primary-residence licences and bookings outside the allowed summer window. Commercially permitted accommodation is different. |
| Madrid | 22,835 Airbnb IDs, Jun 2026; 13,903 short-minimum entire homes | Identify location, building use and operating permissions. INE's narrower tourist-dwelling count is 10,836 in May 2026. |
| Malaga | 8,288 INE tourist dwellings, May 2026 | Entry moratorium affects future additions. A July 2026 extension also restricts new hotels/apartment blocks on residential land, with pipeline exceptions. Airbnb download failed. |
| Florence | 13,508 Airbnb IDs, Jun 2026; 10,640 short-minimum entire homes | Match A1/A3/A4 areas, licence class and transition dates. The 9,903 IDs in Centro Storico are not an exact legal-zone match. |
| Budapest district VI | 2,226 historical legal private/other accommodation establishments | Covered zero-day cohort, not Airbnb-only inventory. Current Airbnb download failed. Surviving commercial accommodation and reclassification need matching. |
| Canary Islands | 48,356 INE tourist dwellings, May 2026 | Island and municipal planning rules, transition provisions and grandfathering determine the subset. |
| Ibiza | 2,314 INE tourist dwellings, May 2026 | Enforcement-linked supply contraction needs to be separated from demand, seasonality and other channels. |
| Ireland | 32,456 Airbnb IDs, Jun 2026 | Registration starts in Dec 2026. The rule covers stays up to 21 nights; the general below-30-night screen is not the exact legal cohort. |
| Portugal | 119,147 active RNAL registrations reported in Jun 2026 | This is not a national active Airbnb count. Partly reversed national policy and municipal cleanup must be separated. |
| Greece | 203,122 finalized registry properties, data received Mar 2026 | National standards require a compliance assessment. Athens and Thessaloniki are overlapping subsets. |
| Scotland | 32,317 licences/exemptions operating, Dec 2025 | Not Airbnb-only. Official statistics caution against trend comparisons while the series matures. |
| England / EU | Comparable Airbnb totals not verified | London supplies a partial England proxy only. EMEA revenue is not EU revenue. Broad registration or data-sharing requirements do not imply universal listing removals. |

Airbnb counts are independently calculated from [Inside Airbnb downloads](https://insideairbnb.com/get-the-data/), with individual URLs and snapshot dates in `market_inventory.json` and the workbook. Files contain scraped listing IDs, not verified unique properties or bookings. The Lisbon and Porto datasets extend beyond their namesake municipalities, so the model filters them. Maui is filtered from the Hawaii snapshot and Thessaloniki from its wider region.

Other anchors: [INE national/regional table](https://www.ine.es/jaxiT3/Tabla.htm?L=0&t=39364), [INE municipal table](https://www.ine.es/jaxiT3/Tabla.htm?L=0&t=39363), [Maui County](https://www.mauicounty.gov/m/newsflash/home/detail/18061), [Lisbon cancellations](https://informacao.lisboa.pt/en/news/detail/local-authority-cancels-40-of-inactive-local-accommodation-registrations), [BC government](https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026HMA0028-000639.pdf), [ELSTAT](https://www.statistics.gr/documents/20181/9520c869-6216-4180-2282-d92150044d23), [Scotland statistics](https://www.gov.scot/news/short-term-lets-licensing-statistics-to-31-december-2025/), [Portugal RNAL report](https://eco.sapo.pt/2026/06/11/mais-de-dez-mil-alojamentos-locais-encerrados-pelos-municipios/), [Budapest historical cohort](https://nepszava.hu/3245205_airbnb-terezvaros-betiltas).

## Observed changes worth testing

| INE market | May 2025 | May 2026 | Change | YoY |
|---|---:|---:|---:|---:|
| Spain | 381,837 | 341,001 | -40,836 | -10.7% |
| Madrid | 15,242 | 10,836 | -4,406 | -28.9% |
| Barcelona | 9,579 | 8,231 | -1,348 | -14.1% |
| Ibiza island | 3,158 | 2,314 | -844 | -26.7% |
| Balearic Islands | 24,361 | 21,304 | -3,057 | -12.5% |
| Canary Islands | 50,686 | 48,356 | -2,330 | -4.6% |
| Malaga | 8,597 | 8,288 | -309 | -3.6% |

These are same-month changes in tourist dwellings across platforms. They are neither separate losses to add together nor causal estimates. Ibiza is the sum of its five municipalities, excluding Formentera. Spain's November 2025 comparison also shows contraction: 329,764 versus 376,463 in November 2024, or 12.4%. The more recent May comparison shows a smaller contraction. Sources: [INE national/regional data](https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/39364.csv), [INE municipal data](https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/39363.csv).

New York provides the clearest severe-enforcement case. Airbnb disclosed approximately 1% of global revenue before September 2023, while AirDNA later reported an 83% drop in short-stay listings. The 1% is a historical market-exposure anchor, not a realized consolidated revenue loss. Booking substitution toward nearby cities, longer stays and hotels means an 83% listing decline cannot simply be multiplied by 1%. [Company disclosure](https://www.sec.gov/Archives/edgar/data/1559720/000119312523268164/d481318dex991.htm), [AirDNA](https://www.airdna.co/blog/nycs-short-term-rental-crackdown).

Greece provides a useful counterpoint: national declared lease days increased 4.7% in 2025, while Attiki increased only 0.8%. This is consistent with uneven regional performance but does not identify the effect of Athens' three-district freeze. Attiki is substantially broader than the treated area. [ELSTAT, tables 1 and 4](https://www.statistics.gr/documents/20181/9520c869-6216-4180-2282-d92150044d23).

## Revenue, margins and guidance

**No quantified jurisdiction-specific revenue or EBITDA loss, or explicit regulatory guidance bridge, was found in the reviewed transcript archive and filings.** That is an evidence gap, not evidence of zero impact. Management discusses geographic diversification, nearby homes and hotel supply as mitigation. Treat the proposition that existing effects are embedded in booking trends as an analyst inference, not a confirmed policy allowance.

| Quarter | Revenue guidance, $m | Actual, $m | Versus midpoint | Adjusted EBITDA margin | Interpretation |
|---|---:|---:|---:|---:|---|
| Q4 2023 | 2,130–2,170 | 2,218 | +3.2% | 33.3% | First full quarter after NYC enforcement. Revenue exceeded guidance despite the restriction. |
| Q2 2025 | 2,990–3,050 | 3,096 | +2.5% | 33.7% | Spanish delisting orders and BC registration period. Consolidated results do not isolate either. |
| Q3 2025 | 4,020–4,100 | 4,095 | +0.9% | 50.1% | Spain's registry/enforcement period. Actual stayed within the range. |
| Q4 2025 | 2,660–2,720 | 2,778 | +3.3% | 28.3% | Fine headlines do not establish an expense in this quarter. |
| Q2 2026 | 3,540–3,600 | 3,608 | +1.1% | 35.0% | Company subsequently raised full-year growth and margin outlook. |

The full comparison contains Q3 2023–Q3 2026, with Q3 2026 actuals left blank. It reuses the project's guidance and cost-line datasets. All actual quarters shown meet or exceed their revenue ranges. This cannot establish full absorption of regulatory risk: demand, FX, fees, product changes and marketing can offset lost supply. Quarterly margin comparisons also require seasonal controls. Source archive: [Airbnb financials](https://investors.airbnb.com/financials/default.aspx).

The latest outlook is Q3 2026 revenue of $4.69–4.77bn, full-year revenue growth of at least mid teens and an adjusted EBITDA margin of at least 35.5%. The company attributes the increase to demand, product/growth initiatives and operating leverage, not a separately quantified regulatory adjustment. [Q2 2026 shareholder letter, outlook](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm).

**Spain fine correction:** the Q2 2026 Form 10-Q reports a €70m ($80m) surety bond obtained in May to suspend enforcement pending resolution. Airbnb continues to describe the potential loss as neither probable nor estimable. The bond's face amount is not a recognized fine expense and does not establish an equal cash payment. Bond premiums, collateral, future loss recognition and cash settlement are distinct. Do not automatically subtract the headline fine from adjusted EBITDA, since a non-income-tax consumer fine is not automatically covered by the company's tax-reserve exclusions. [Q2 2026 Form 10-Q, regulatory matters and non-GAAP definition](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

## How the editable model works

Annual lost platform fee revenue equals:

**affected units × Airbnb channel share × unique productive share × lost nights per unit × realized room ADR × fee rate × net scope/enforcement × (1 − revenue recapture).**

For removal rules, lost nights are the productive nights the unit would have supplied. For caps, use only the excess above the cap. For entry freezes, start from a counterfactual new-listing pipeline and the fraction of the year each prevented entrant would have operated. For seasonal bans, use month-specific demand weights. Include legacy bookings, implementation lags, grandfathering and reinstatement.

Eight examples are populated to make the mechanics usable. **They are illustrations, not estimated outcomes or probability-weighted forecasts.**

| Illustration | Assumptions beyond the observed cohort | Annualized net revenue loss | EBITDA loss at assumed 70% contribution margin |
|---|---|---:|---:|
| 10,000 productive Airbnb listings removed | 150 nights, $200 ADR, 15.5% room-value fee, 50% fee-revenue recapture | $23.3m | $16.3m |
| Barcelona 10,101 licences | 65% Airbnb channel share; 85% unique/productive; 180 nights; $220 ADR; 15.5% fee; 50% recapture; full phase-out | $17.1m | $12.0m |
| Maui 6,208 active historical units | 60% Airbnb channel share; 210 nights; $375 ADR; 15.5% fee; 50% recapture; no rezoning exemption | $22.7m | $15.9m |
| Same Maui cohort, 60% assumed exempt | Same economics; only 40% net scope remains | $9.1m | $6.4m |
| Spain 65,122 removed ads | 35% unique productive net-lost share; 150 nights; $180 ADR; 15.5% fee; 50% recapture | $47.7m | $33.4m |
| Paris 10,000 cap-binding homes | Hypothetical count; 30 lost nights; $220 ADR; 15.5% fee; 50% recapture | $5.1m | $3.6m |

Barcelona and Maui refer to a full year after their relevant phase-outs, not a 2026 loss. Spain is an illustrative reconstruction of a historical event, not incremental downside to current guidance. Alternative rows and nested jurisdictions must not be summed. The 15.5% fee is applied to room value, excluding cleaning and taxes, and is an explicit scenario assumption informed by the announced fee migration. It is not interchangeable with revenue divided by GBV.

The 10,000-unit example equals approximately 0.19% of FY25 revenue and about 6.6 basis points of standalone margin compression on a static FY25 base. The workbook uses FY25 revenue of $12,241m and adjusted EBITDA of $4,297m. Its margin calculation is `(baseline EBITDA − loss × contribution margin) / (baseline revenue − loss)`. The 70% contribution margin is an assumption, not management guidance. Additional legal/compliance expense would be a separate deduction. [FY25 financials](https://www.sec.gov/Archives/edgar/data/1559720/000119312526048670/d58192dex991.htm).

## Next research sequence

1. **Resolve affected inventory:** prioritize Barcelona licence matching, Spain removed-ad history, Maui parcel/rezoning overlap, and Athens/Amsterdam policy boundaries. Then separate Paris/Montreal primary residences from licensed commercial accommodation.
2. **Measure economics:** obtain monthly Airbnb-only active listings, booked nights and realized room/cleaning revenue for affected and unaffected cohorts, ideally 12–24 months before and after each event. Scraped calendar unavailability is not a booking. Reviews are lagged and incomplete demand proxies.
3. **Estimate causality and recapture:** compare against matched unaffected destinations with pre-trend checks. Nearby destinations can receive displaced demand, so use them to measure spillovers, not automatically as untreated controls. Control for seasonality, FX, major events and the Maui wildfire recovery.
4. **Connect to guidance:** map information known at each earnings date to destination-level operating changes. Ask management for contribution to revenue growth, geographic exposure and retained demand. A consolidated guidance beat alone does not prove a risk is fully reflected in guidance or priced into the stock.
5. **Translate to the pitch:** apply only incremental, non-overlapping losses to the current baseline. Calculate recurring EBITDA and after-tax earnings effects separately from fines and cash collateral. A stock-price estimate additionally requires valuation multiples, share count, taxes and the market's prior expectations.

## Files and reproducibility

- `market_inventory.json`: inventory definitions, dates and direct source URLs.
- `factor_exposures.json`: all 32 original factors plus supplemental Lisbon cleanup, affected-count interpretation and data gaps.
- `listing_snapshots.json` and `neighbourhood_counts.json`: calculated public snapshot aggregates and hashes.
- `spain_supply_history.json`: seven geographical comparisons from downloaded INE tables.
- `guidance_history.json`: revenue guidance, actuals, margin and regulatory context.
- `illustrative_scenarios.json`: clearly labeled illustrative inputs and calculated reference results.
- Five `regulatory_*` tables extend `data/processed/abnb_regulatory.sqlite` without replacing the original research tables.

Refresh scripts: `analysis/src/quantify_regulatory_supply.py`, `analysis/src/pull_regulatory_quant_sources.py`, `analysis/src/build_regulatory_quantification.py`, and `analysis/src/build_regulatory_workbook.mjs`. The original database builder should run before the quantification builder. Raw downloads and workbook verification outputs remain under gitignored `data/raw/regulatory/quantification`. Workbook formulas were reconciled to independently calculated outputs, and missing-input and full-recapture cases were checked.

The existing Refinitiv/LSEG setup and news archive were reused. Full quarterly transcript text remains in the prior local archive; LSEG's retrieved transcript entries were EventsViewer links rather than full transcript bodies. No paid listing dataset was purchased or assumed available. Missing England/EU totals and failed Malaga/Budapest downloads are recorded, not replaced by zeros.
