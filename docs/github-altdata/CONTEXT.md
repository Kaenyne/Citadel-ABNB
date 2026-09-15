# GitHub alt-data catalogue — shared context for every agent (13 Sep 2026)

You are helping catalogue **open-source GitHub repositories that store, mirror, or provide easy methods for
acquiring data that could be useful for forecasting Airbnb (ABNB)**. This is a cataloguing pass only: nobody
in this run tests for signal or alpha. The question is "does something potentially useful exist, where, and
what is in it". Breadth beats depth. Data that never mentions Airbnb can still matter.

## Who we are and what the pitch needs

Student stock-pitch team (Citadel competition, memo due 2 Oct 2026, next ABNB print 5 Nov 2026). The model
forecasts Airbnb's quarterly KPIs: **nights & seats booked, ADR (average daily rate, ex-FX and FX parts),
gross booking value (GBV), revenue (recognised at check-in, ~60% of a quarter booked before it starts),
take rate, adj. EBITDA margin**, the **Q4 revenue guide** management gives on 5 Nov, and regional splits
(North America, EMEA, LatAm, APAC). Anything that reads on **travel demand, short-term-rental supply,
pricing, cancellations, FX, consumer strength, regulation, competitor volumes, or Airbnb's own engagement**
is in scope. So is tooling that makes a public source machine-pullable (API clients, scrapers of *non-Airbnb*
sites, archive tooling), point-in-time / vintage data, and academic replication packages.

## What we already hold (do not re-flag as new; DO flag better/longer/older versions)

- Inside Airbnb: 13-city panel (NYC, LA, Chicago, Austin, Nashville, New Orleans, San Diego, Paris, London,
  Barcelona, Rome, Sydney, Mexico City), 168 dumps Dec 2022–Aug 2026; 2024–25 calendar vintages for 34
  markets; a 120-market Jun-2026 cohort (listings, calendars, reviews); reviews-based "stays index" over 123
  markets. **Gaps: dumps older than ~1 year are off the Inside Airbnb CDN, NYC pre/post Local Law 18 dumps
  (2023-06 to 2024-03) are missing, 2026 calendars carry no price column.** Any GitHub mirror/archive of
  historical Inside Airbnb dumps (2015–2023, any city) is HIGH value.
- Common Crawl CDX index over airbnb.com listing pages (2.08M rows, 50 crawls), 3,000 WARC renders.
- Booking.com: 515k hotel reviews (Kaggle), RecTour24 user dataset. Portugal hotel-booking demand dataset
  (Antonio/Almeida/Nunes). Peer 8-K KPIs for BKNG, EXPE, MAR, HLT.
- Eurostat `tour_ce_omr` platform nights (monthly, 2018–2026); BEA PCE travel panel; FRED (CPI lodging,
  airfares, ~40 series); FX schedules; Google Trends (9 terms, NOT point-in-time); TSA throughput; NTTO I-94
  arrivals; INE Spain Frontur/EOH; BLS CPI; euro-area HICP accommodation; MAR/HLT RevPAR from releases;
  Hawaii DBEDT visitor stats (only public party-size series); OECD consumer confidence panel.
- Municipal STR registries (Austin daily licences, Barcelona HUTB, Maui, NYC OSE, California TOT for 482
  cities, ~25 datasets); regulatory event database (32 factors).
- Company data: all letters/transcripts/XBRL since IPO, guidance ledger, press-quote consensus at 23 prints,
  analyst targets, options chains (Yahoo, current), daily prices, short interest, Ken French factors.
- Third Bridge expert transcripts (licensed), Bloomberg options/consensus workbook (licensed).

## What we are missing (HIGH-value targets — anything on GitHub touching these is worth flagging)

1. Historical / archived Inside Airbnb dumps (pre-2023, and NYC 2023-06 → 2024-03).
2. Realised ADR or realised occupancy for STRs from any free source (AirDNA / Key Data / Transparent /
   AllTheRooms sample exports, scraped market pages, academic datasets with booked prices).
3. Booking lead time / cancellation-rate distributions for STRs (RNPL = "reserve now pay later" thesis).
4. Point-in-time / vintage series: ALFRED-style macro vintages, historical analyst-consensus snapshots
   (revenue/EPS estimates history for ABNB, BKNG, EXPE), historical Google Trends pulls with pull dates.
5. Engagement: app downloads / rankings history, web-traffic estimates (Similarweb-like, Cloudflare Radar,
   Chrome UX Report popularity rank, Tranco / Common Crawl host-graph ranks), Wikipedia pageviews tooling.
6. Consumer spend panels that are public (Opportunity Insights Economic Tracker card spend, ONS/BoE card
   spend, central-bank card data in Portugal/Norway/Spain, BBVA/CaixaBank open data, OpenTable seated diners).
7. Regional travel volume outside the US/EU: LatAm (Mexico DATATUR/INEGI, Brazil Embratur/IBGE, Colombia,
   Argentina), APAC (JNTO Japan, Korea KTO, Australia ABS/TRA, Thailand, India, Indonesia), Canada StatCan.
8. Hotel supply/demand: STR/CoStar weekly figures scraped from press releases, regional RevPAR, state-level
   occupancy (Nevada, Florida bed tax, Hawaii), lodging-tax collections (transient occupancy tax by city).
9. Competitor and adjacent supply: Vrbo/HomeAway, Booking.com alternative accommodation, Expedia, Agoda,
   Marriott Homes & Villas, Sonder/Vacasa, Hostelworld, Hipcamp; Chinese platforms (Tujia, Xiaozhu).
10. Airline/rail/road capacity and traffic: BTS T-100 / DB1B, OpenSky/ADS-B, Eurocontrol, airport monthly
    passenger stats, Amtrak/SNCF/DB, NYC TLC airport taxi trips, gas prices.
11. Events and shocks: FIFA World Cup 2026 (US/Canada/Mexico, Jun–Jul 2026, inside 3Q26), concerts,
    conferences, hurricanes/wildfires, holiday calendars by country.
12. Regulation: STR ordinance trackers, city registration datasets (LA HSO, SF OSTR, Toronto, Vancouver,
    Montreal/Quebec CITQ, Amsterdam, Berlin, Vienna, Lisbon RNAL, Italy CIN, France), EU DAC7 platform
    reporting statistics, Legistar/LegiScan tooling, court records.
13. Long-term rental and housing: Zillow ZORI/Redfin/Apartment List/Realtor.com data, Idealista/Rightmove/
    Immoscout scrapes, HUD FMR, permits, mortgage rates — host supply economics and STR↔LTR crossover.
14. Text/social: Reddit dumps (r/airbnb, r/AirBnBHosts, r/travel), Airbnb Community Center scrapes, app-store
    review scrapers, Glassdoor/Indeed, job-posting trackers (Airbnb hiring as headcount proxy), GDELT.
15. Company-structure signals: 13F holdings parsers (concentration history), SEC EDGAR full-text/XBRL tooling,
    patents/trademarks, certificate-transparency / app-release monitors, Airbnb's own GitHub org activity.
16. Remote-work / long-stay demand: WFH Research SWAA data, Nomad List, digital-nomad visa datasets.
17. Methods: nowcasting with mixed-frequency data (MIDAS, DFM), anchored Google Trends (gtab), event-study
    packages, earnings-implied-move estimators, Wayback Machine tooling (archived airbnb.com pages, archived
    AirDNA market pages), Socrata/CKAN open-data discovery clients (to find STR datasets across cities).
18. Cruise lines (NCLH advance ticket sales) and other "book-ahead" businesses as kernel analogues.
19. AI-referral traffic: bot/crawler share datasets (Cloudflare Radar, Vercel), LLM travel-agent benchmarks.
20. Party size / group travel, length-of-stay, cross-border share proxies (geotagged tourism datasets:
    YFCC100M, Foursquare/Gowalla check-ins, Twitter tourism flows).

## Ideas already tested and found NOT to work (still catalogue better data; do not argue the test)

Google Trends as pulled (0/162 beat naive; renormalisation), Eurostat platform nights as a nowcast (150-day
lag), the 13-city Inside Airbnb listing counts as a nights measurement, macro sentiment vs nights, TSA
throughput since 2024, management tone, composite alt-data indexes. These failed on *our constructions*; a
longer, older, point-in-time, or differently-grained dataset is still worth cataloguing.

## Rules for this run

- Catalogue only. Do not evaluate signal. Do not run scrapers against airbnb.com or any site behind a login;
  scraper repos are catalogued as "method" and left unrun (a human decides terms-of-service questions).
- Cite the repository URL exactly. Prefer repos with data files committed, release assets, or a clear
  one-command pull from a public source. Note licence, last commit date, geography, time span, size.
- Duplicates of what we hold are still worth one line if they are longer, older, or finer-grained.
- Never type credentials; never use paid API keys. `gh` is authenticated for public reads only.
