export const meta = {
  name: 'github-altdata-scout-and-review',
  description: 'Fan out ~260 Sonnet scouts over GitHub for ABNB-relevant open data, dedupe, then Opus reviews every flagged repo',
  phases: [
    { title: 'Scout', detail: 'one Sonnet agent per theme x modality, plus wildcard lenses', model: 'sonnet' },
    { title: 'Review', detail: 'Opus reviews deduped candidates in batches of 5', model: 'opus' },
  ],
}

const WT = 'C:/Users/krish/citadel-abnb-ghcat'
const CONTEXT = `${WT}/docs/github-altdata/CONTEXT.md`
const SCOUT_DIR = `${WT}/data/processed/github_altdata/scouts`
const REVIEW_DIR = `${WT}/data/processed/github_altdata/reviews`

const CATS = ['str_airbnb_direct','competitor_ota','hotel_lodging','travel_volume_transport','housing_rental','macro_consumer_spend','fx_rates','web_app_engagement','social_text_news','regulatory_legal','company_filings_estimates','markets_options_positioning','events_weather_shocks','geospatial_poi_mobility','methods_tooling','academic_replication','other']

const THEMES = [
  // --- STR / Airbnb direct
  ['Inside Airbnb historical dump mirrors and archives (pre-2023 listings/calendar/reviews CSVs committed or released; archive.org mirrors referenced from GitHub)', 'inside airbnb listings.csv.gz archive, insideairbnb data 2016 2017 2018 2019, airbnb dataset all cities'],
  ['Inside Airbnb New York City snapshots around Local Law 18 (2023-06 to 2024-03) stored in repos', 'airbnb nyc 2023 listings, local law 18 airbnb data, nyc airbnb september 2023'],
  ['Kaggle-style Airbnb listing snapshot datasets committed to GitHub (any city, any year), especially multi-year or multi-city collections', 'airbnb price prediction dataset csv, airbnb listings dataset, AB_NYC_2019 airbnb'],
  ['Airbnb reviews text corpora and review-date datasets on GitHub (review counts over time as a stays proxy)', 'airbnb reviews dataset, airbnb reviews.csv nlp, airbnb sentiment reviews corpus'],
  ['Airbnb calendar / availability / blocked-night datasets and occupancy-estimation code (San Francisco model, review-to-booking ratios)', 'airbnb calendar.csv occupancy estimate, airbnb occupancy model reviews, airbnb availability dataset'],
  ['Academic replication packages using Airbnb data: Zervas Proserpio Byers (hotel impact), Barron Kung Proserpio (housing), Farronato Fradkin, Horn Merante, Garcia-Lopez Barcelona, Koster Los Angeles, Edelman discrimination, Fradkin reviews', 'zervas airbnb replication, proserpio airbnb data, airbnb rents replication dataverse github'],
  ['AirDNA / Mashvisor / AllTheRooms / Transparent / Key Data / Rabbu / Awning sample exports or scraped market pages committed to GitHub', 'airdna dataset, airdna market data csv, mashvisor data, alltherooms data, airdna scraper'],
  ['Municipal short-term-rental licence and registration datasets (Austin, LA HSO, SF OSTR, Denver, New Orleans, Nashville, Seattle, Portland, Boston, Chicago, San Diego, Honolulu) mirrored or pulled by code', 'short term rental license dataset city, str permits open data, airbnb registration data socrata'],
  ['European STR registration and tourist-accommodation registries (Portugal RNAL, Spain tourist dwellings, Italy CIN, France meublés de tourisme, Amsterdam, Berlin, Vienna, Lisbon, Barcelona HUTB, Paris)', 'alojamento local RNAL dataset, viviendas turisticas dataset, meublés de tourisme données, registro alloggi turistici CIN'],
  ['Canadian and Australian STR registries and datasets (Toronto, Vancouver, Montreal, Quebec CITQ, BC registry, Sydney NSW STRA register, Melbourne)', 'toronto short term rental registration data, quebec CITQ dataset, NSW STRA register data'],
  ['Airbnb host-side datasets: superhost/multi-listing/professional host panels, host earnings, DAC7 platform-reporting statistics, IRS/tax authority STR income stats', 'airbnb hosts dataset multi-listing, DAC7 platform data, airbnb host income data'],
  ['Airbnb Experiences, Services and hotel-on-Airbnb listing data; Viator / GetYourGuide / Klook tour and activity datasets', 'airbnb experiences dataset, viator scraper dataset, getyourguide data, tours activities dataset'],
  ['Airbnb pricing tools and dynamic-pricing repos that embed market data (PriceLabs, Beyond, Wheelhouse style; open-source STR pricing with comps)', 'airbnb dynamic pricing tool market data, short term rental pricing open source, pricelabs data'],
  ['Airbnb API wrappers and search-page clients (catalogue only, never run): pyairbnb, airbnb-scraper, airbnb search results parsers; note what fields they expose', 'pyairbnb, airbnb scraper python, airbnb api unofficial'],
  ['Airbnb cancellation, refund and Reserve-Now-Pay-Later related datasets; STR booking lead-time and cancellation-rate data from any platform or PMS', 'airbnb cancellation dataset, booking lead time short term rental data, vacation rental cancellations dataset'],
  ['Property-management / channel-manager / PMS public data (Guesty, Hostaway, Lodgify, OwnerRez, Hostfully, Smoobu, Beds24, iCal feeds) and vacation-rental manager benchmarks', 'vacation rental manager benchmark data, hostaway api data, PMS open dataset vacation rental'],
  // --- competitor OTAs
  ['Vrbo / HomeAway datasets and scrapers, Vrbo listing snapshots, Expedia Group vacation rental supply data', 'vrbo dataset, homeaway scraper, vrbo listings csv'],
  ['Booking.com datasets beyond the 515k reviews: listing/price snapshots, alternative-accommodation counts, Booking scrapers, WSDM/RecSys Booking challenge data', 'booking.com dataset hotels prices, booking.com scraper, booking challenge dataset recsys'],
  ['Expedia and Hotels.com datasets (Expedia hotel recommendation Kaggle, personalized ranking ICDM 2013, Expedia scrapers), Trivago RecSys 2019, Kayak/Skyscanner scrapers', 'expedia dataset, trivago recsys 2019 dataset, hotels.com scraper'],
  ['TripAdvisor datasets: hotel/vacation-rental reviews, review velocity, TripAdvisor rentals, scraper repos', 'tripadvisor dataset reviews, tripadvisor scraper, tripadvisor hotel reviews csv'],
  ['Agoda, Trip.com, Tujia, Xiaozhu, Meituan, MakeMyTrip, OYO, Traveloka datasets and scrapers (APAC OTA and STR platforms)', 'agoda dataset, tujia dataset, xiaozhu airbnb china data, ctrip dataset hotels'],
  ['Hostelworld, Hipcamp, Outdoorsy, RVshare, Sonder, Vacasa, Inspirato, Marriott Homes & Villas, Plum Guide, onefinestay, Flatio, Blueground datasets or filings parsers', 'hostelworld dataset, sonder data, vacasa dataset, marriott homes villas listings'],
  ['Google Hotel Ads / Google Travel price datasets and scrapers; hotel metasearch price panels', 'google hotels scraper, google travel prices dataset, hotel metasearch price data'],
  // --- hotels / lodging
  ['Hotel performance data: STR / CoStar weekly and monthly US RevPAR figures scraped from press releases, HotStats, Smith Travel history compiled on GitHub', 'STR weekly hotel data csv, revpar dataset, hotel occupancy adr revpar historical'],
  ['State and city hotel occupancy and lodging-tax datasets (Nevada, Florida tourist development tax, Texas hotel occupancy tax, California TOT, NYC hotel occupancy tax, Hawaii TAT)', 'hotel occupancy tax data, transient occupancy tax dataset, tourist development tax collections'],
  ['Hotel booking demand datasets (Antonio Almeida Nunes and successors), hotel PMS datasets, revenue-management datasets with cancellations and lead times', 'hotel booking demand dataset, hotel reservations dataset cancellations, revenue management dataset hotel'],
  ['Hotel supply data: Overture/OSM hotel POI counts, hotel pipeline datasets, lodging census (Census QSS NAICS 721), county business patterns tooling', 'hotel pipeline dataset, osm tourism hotel extract, NAICS 721 data'],
  ['Cruise line data: NCLH / Carnival / Royal Caribbean advance ticket sales, capacity, occupancy, cruise schedules and port calls', 'cruise data advance ticket sales, cruise ship schedules dataset, cruise capacity dataset'],
  // --- travel volume / transport
  ['US air travel: BTS T-100 segment, DB1B fares, Form 41, on-time performance; repos that download and tidy them; TSA throughput scrapers', 'bts t100 download python, DB1B dataset, tsa checkpoint throughput scraper'],
  ['Flight tracking and schedules: OpenSky, ADS-B Exchange, FlightRadar scrapers, aviationstack samples, airline seat capacity by route', 'opensky network dataset, flight schedules dataset, airline capacity seats route dataset'],
  ['European and global aviation stats: Eurocontrol, EASA, ACI airport passenger stats, IATA public figures, airport monthly traffic scrapers (Heathrow, Schiphol, ADP, Fraport, AENA)', 'eurocontrol data, airport passenger statistics monthly dataset, aena passenger data'],
  ['International arrivals: NTTO I-94, UNWTO, StatCan travellers, JNTO Japan, Korea KTO, Australia ABS overseas arrivals, Mexico INEGI/DATATUR, Brazil, Thailand MOTS, Indonesia BPS, India MoT', 'tourist arrivals dataset monthly, JNTO data python, unwto dataset github, international arrivals scraper'],
  ['European tourism statistics tooling: Eurostat tour_occ / tour_ce clients, INE Spain Frontur Egatur EOAT tourist-apartment tables, ISTAT, INSEE, Destatis, ONS travel, Portugal INE', 'eurostat python tour_occ, INE frontur api, istat turismo dati, eurostat tourism package'],
  ['Rail and ground travel: Amtrak ridership, SNCF/DB/Trenitalia open data, Eurostar, bus (FlixBus), rideshare datasets (Uber Movement), NYC TLC airport trips, Chicago taxi', 'amtrak ridership data, sncf open data, nyc tlc airport trips, uber movement data'],
  ['Cross-border and visa data: Schengen visa statistics, ESTA, ETIAS, CBP wait times, passport index, border crossings BTS', 'schengen visa statistics dataset, border crossing data bts, cbp wait times dataset'],
  ['Road travel and fuel: gas prices (EIA, AAA), vehicle miles travelled, holiday driving, toll data', 'gas prices dataset weekly eia, vehicle miles traveled data, aaa gas prices scraper'],
  ['Destination demand proxies: US National Park Service visitation stats API, state park attendance, museum/theme-park attendance, ski resort data, beach visitation', 'national park visitation data api, theme park attendance dataset, state park visits data'],
  ['Restaurant and leisure proxies: OpenTable state of the industry CSV, Yelp dataset, Google Maps reviews scrapers, event ticket data', 'opentable state of industry data, yelp dataset, google maps reviews scraper'],
  // --- housing / rental
  ['Long-term rent indices: Zillow ZORI/ZHVI downloaders, Apartment List, Redfin data center, Realtor.com, HUD Fair Market Rents, Census ACS rent, CoStar-like', 'zillow research data python, apartment list rent data, redfin data center download, hud fmr api'],
  ['Rental listing scrapers and datasets (Craigslist, Zillow rentals, Apartments.com, Idealista, Rightmove, Zoopla, Immoscout24, SeLoger, Immobiliare, Domain, realestate.com.au)', 'craigslist rentals dataset, idealista dataset, rightmove scraper, immoscout dataset'],
  ['Housing supply and investor activity: building permits, Redfin investor purchases, mortgage rates, county assessor/parcel data, LLC ownership, NYC PLUTO/ACRIS', 'building permits dataset, investor home purchases data, parcel data llc ownership, nyc pluto acris'],
  ['Housing affordability and STR-housing studies data: rent-burden, vacancy, STR share of housing stock by tract', 'short term rental housing stock share dataset, rental vacancy rate data tract, str housing impact data'],
  ['Coliving, corporate housing, furnished mid-term rental data (Blueground, Landing, Furnished Finder, Zeus), remote-work and digital-nomad data (WFH Research SWAA, Nomad List, nomad visas)', 'furnished finder data, WFH research SWAA data, nomad list dataset, digital nomad visa dataset'],
  // --- macro / consumer
  ['Public consumer-spend panels: Opportunity Insights Economic Tracker (Affinity card spend), ONS card spending, Bank of England CHAPS, BBVA/CaixaBank research open data, Banco de Portugal SIBS, Norges Bank card data', 'opportunity insights economic tracker data, ons card spending data, sibs card data portugal, affinity card spending csv'],
  ['Real-time and weekly economic indicators: OECD Weekly Tracker (Google Trends based), NY Fed WEI, ONS faster indicators, Dallas Fed mobility, Bundesbank weekly activity index', 'oecd weekly tracker github, weekly economic index data, faster indicators ons github'],
  ['Point-in-time macro vintages: ALFRED tooling, Philly Fed real-time dataset, ONS revisions, Eurostat vintages; packages for vintage-aware backtests', 'alfred vintages python, real time data set philadelphia fed, macro data vintages package'],
  ['FRED / BEA / BLS / Census API clients and curated macro panels (consumer sentiment, PCE services, CPI lodging, airfares, unemployment by metro)', 'fredapi, bea api python, bls api python, census api client'],
  ['Consumer sentiment and surveys: UMich, Conference Board, NY Fed SCE, EU consumer confidence, travel-intent surveys (Longwoods, Destination Analysts, MMGY) scraped', 'consumer sentiment data michigan download, travel intentions survey data, sce survey data'],
  ['Consumer credit and BNPL: Klarna/Affirm public stats, Fed G.19, credit card delinquency, CFPB complaints dataset (Airbnb refund complaints), BBB complaint scrapers', 'cfpb complaints dataset airbnb, bnpl usage data, consumer credit data'],
  ['FX and purchasing power: exchange-rate history (ECB, BIS, FRED), broad-dollar indices, PPP/Big Mac, tourist affordability indices, company FX-exposure tooling', 'exchange rates dataset ecb python, big mac index data, fx exposure regression tool'],
  ['Regional macro for LatAm and APAC: Mexico INEGI/Banxico, Brazil IBGE/BCB, Argentina INDEC, Colombia DANE, Chile, Japan e-Stat, Korea KOSIS, Australia ABS, India MOSPI clients', 'inegi api python, ibge api, e-stat japan api python, kosis api'],
  ['Inflation and price indices for accommodation: BLS CPI lodging, Eurostat HICP accommodation, national CPI hotel components, Japan CPI, Australia CPI accommodation', 'cpi lodging away from home data, hicp accommodation services data, cpi hotel component dataset'],
  // --- web / app engagement
  ['App download and ranking histories: App Store / Google Play rank scrapers, app-store-scraper, google-play-scraper, AppFigures/Sensor Tower/data.ai open samples, app review-count time series', 'app store rank history scraper, google-play-scraper, app annie dataset, app downloads estimates dataset'],
  ['Web-traffic estimates and domain ranks: Similarweb scrapers or samples, Cloudflare Radar API, Chrome UX Report popularity rank, Tranco, Majestic Million, Common Crawl host-graph rank', 'similarweb scraper, cloudflare radar api python, chrome ux report rank, tranco list history'],
  ['Wikipedia pageviews tooling and destination-demand datasets (pageviews for cities/attractions as tourism proxies)', 'wikipedia pageviews api python, pageviews tourism forecasting, wikipedia pageviews dataset'],
  ['Google Trends tooling and datasets: pytrends, gtab anchored trends, historical trends archives, trends nowcasting repos', 'pytrends, gtab google trends anchor, google trends dataset historical'],
  ['Search/SEO and referral data: Bing/Google keyword volume tools, SERP scrapers, Common Crawl web graph, backlink datasets, AI-bot crawler traffic stats (Cloudflare, Vercel)', 'common crawl web graph rank, serp scraper dataset, ai crawler traffic data cloudflare'],
  ['Airbnb corporate footprint signals: careers/Greenhouse job-posting scrapers, LinkedIn headcount trackers, layoffs.fyi data, Glassdoor/Indeed review datasets, GitHub org activity (GH Archive)', 'greenhouse jobs api scraper, job postings dataset company, layoffs data, gh archive company activity'],
  ['Product-launch monitors: certificate transparency (crt.sh) tooling, app release-notes scrapers, Wayback diff tools, help-center change monitors, trademark/patent (USPTO, PatentsView) clients', 'crt.sh python, wayback machine diff tool, patentsview api python, uspto trademark api'],
  // --- social / text / news
  ['Reddit dumps and tooling: Pushshift archives, r/airbnb r/AirBnBHosts r/travel datasets, Airbnb Community Center scrapes, host forum datasets', 'pushshift reddit dump download, reddit airbnb dataset, airbnb community center scrape'],
  ['Twitter/X, Instagram, Flickr, TikTok tourism datasets: geotagged tourism flows, YFCC100M tourism subsets, Foursquare/Gowalla/Brightkite check-ins', 'geotagged tweets tourism dataset, yfcc100m tourism, foursquare check-in dataset'],
  ['News and event databases: GDELT tooling, Google News scrapers, travel-industry news datasets (Skift, PhocusWire), regulatory news trackers', 'gdelt python, news scraper dataset travel, gdelt events tourism'],
  ['Earnings-call transcript datasets and NLP tooling (ECT datasets, Motley Fool scrapers, Seeking Alpha parsers), management-tone corpora', 'earnings call transcripts dataset, earnings call nlp github dataset, transcripts scraper'],
  // --- regulatory / legal
  ['STR regulation trackers and ordinance datasets: city STR law databases, Legistar/LegiScan clients, EU parliament open data, court records (CourtListener/RECAP) on Airbnb litigation', 'short term rental regulation database, legistar api python, courtlistener api airbnb'],
  ['Housing-policy and STR-ban datasets: HOA/condo STR bans, NYC OSE enforcement data, Barcelona/Amsterdam/Paris enforcement, Spanish 2025 platform registration numbers', 'nyc office special enforcement data, str enforcement dataset, ley alquiler turistico dataset'],
  ['Tourist tax and city-tax datasets: Paris taxe de sejour, Amsterdam toeristenbelasting, Italian imposta di soggiorno, Airbnb remittance reports, occupancy-tax remittance by platform', 'taxe de sejour donnees, imposta di soggiorno dati, tourist tax collections dataset airbnb'],
  // --- company / estimates / markets
  ['SEC EDGAR tooling: full-text search, 8-K/10-Q parsers, XBRL frames, financial statement datasets, edgar-crawler; peer print scrapers (BKNG EXPE MAR HLT)', 'edgartools, sec-api python, xbrl frames python, edgar full text search python'],
  ['Analyst estimates and consensus history: Yahoo/Zacks/Finviz/Estimize/Alpha Vantage scrapers, historical EPS estimate datasets, estimate-revision datasets, I/B/E/S-like open data', 'analyst estimates history scraper, earnings estimates dataset historical, zacks scraper, estimize data'],
  ['13F holdings parsers and institutional-ownership history, short-interest datasets, insider-transaction parsers (Form 4), ETF holdings trackers', '13f parser python, sec form 4 parser, short interest dataset finra, etf holdings scraper'],
  ['Options and event-move tooling: historical option chains (CBOE samples, ORATS-like), earnings implied-move calculators, IV term-structure datasets, earnings-drift datasets', 'historical options data free github, earnings implied move calculator, option chain history dataset'],
  ['Event-study and factor packages; earnings-surprise datasets; post-earnings-drift replication; Ken French factor loaders', 'event study python package, earnings surprise dataset, fama french factors python'],
  ['Prediction markets and betting data: Polymarket/Kalshi/Manifold APIs and datasets on earnings and travel/regulation events', 'polymarket api python, kalshi api data, manifold markets dataset'],
  // --- events / weather / shocks
  ['Event calendars: FIFA World Cup 2026 schedule and host-city data, Olympics, concerts (Setlist.fm, Songkick, Ticketmaster API), conferences, PredictHQ samples, holiday calendars by country', 'world cup 2026 schedule dataset, ticketmaster api python, holidays python package, predicthq sample data'],
  ['Weather, hurricanes, wildfires, disasters: NOAA/NHC tracks, EM-DAT, FEMA declarations, wildfire perimeters (Maui, LA fires), heatwaves; tourism-shock datasets', 'hurricane tracks dataset, fema disaster declarations api, wildfire perimeter data, em-dat'],
  ['Public-health and mobility indices: Google/Apple mobility archives, Cuebiq, SafeGraph/Advan/Dewey samples, Placer.ai-like foot traffic, mobility datasets by city', 'google mobility reports data archive, safegraph sample data, foot traffic dataset poi'],
  // --- geospatial
  ['POI and place data: Overture Maps places, OSM extracts (tourism=*), Foursquare open places, Geofabrik tooling; counting STR/hotel supply from maps', 'overture maps places python, osm tourism extract, foursquare open source places'],
  ['Geocoding, neighbourhood boundaries and census-tract crosswalks used for STR studies; city GIS portals with STR layers', 'neighborhood boundaries geojson cities, census tract crosswalk, city gis short term rental layer'],
  // --- methods / tooling
  ['Nowcasting methods and packages: MIDAS, dynamic factor models, bridge equations, nowcasting with Google Trends, KPI nowcasting for companies', 'midas regression python, dynamic factor model nowcasting python, nowcasting package'],
  ['Wayback Machine / Internet Archive tooling and archived-page datasets (archived airbnb.com pages, archived AirDNA/Mashvisor market pages, archived Inside Airbnb site)', 'waybackpy, wayback machine scraper, internet archive cdx python'],
  ['Common Crawl tooling: cdx-toolkit, warcio, host-level indexes, columnar index queries; datasets derived from Common Crawl for travel sites', 'cdx toolkit common crawl, common crawl columnar index athena, warcio'],
  ['Open-data portal discovery: Socrata/CKAN/data.gov/EU data portal clients, dataset search tools, Google Dataset Search scrapers; city portals with STR datasets', 'socrata api python sodapy, ckan api python, data.gov dataset search tool'],
  ['Data-hosting mirrors pointed at from GitHub: Zenodo, Figshare, Harvard Dataverse, HuggingFace, Kaggle, Mendeley Data collections on Airbnb, STR, hotels, tourism', 'zenodo airbnb dataset, dataverse short term rental, huggingface dataset airbnb, kaggle airbnb dataset github'],
  ['Awesome lists and curated catalogues: awesome-public-datasets, awesome-alternative-data, awesome-quant data, awesome-economics, awesome-tourism, awesome-real-estate, awesome-transportation-data', 'awesome public datasets, awesome alternative data, awesome tourism data, awesome real estate data'],
  ['Alternative-data vendor sample repos: vendors publishing free samples on GitHub (Advan, Similarweb, Apptopia, Yipit-like, Consumer Edge, Earnest, M Science, Quiver Quant, Thinknum)', 'alternative data sample dataset github vendor, quiver quantitative api, thinknum data sample'],
  ['Kaggle competitions and datasets on travel demand forecasting mirrored on GitHub (Expedia, Trivago, Booking, Airbnb new-user bookings, hotel demand)', 'airbnb new user bookings kaggle, expedia hotel recommendations kaggle github, travel demand forecasting dataset'],
  ['Company KPI and alt-data backtest repos for ABNB or OTAs: anyone who already assembled Airbnb quarterly KPI datasets, consensus, or alt-data panels', 'airbnb quarterly kpi dataset, ABNB earnings dataset, airbnb nights booked data github'],
  ['Airbnb corporate open source (airbnb org) and public data pipelines built on Airbnb-internal-style data; Airbnb Data Science blog notebooks; Airbnb Newsroom scrapers', 'airbnb newsroom scraper, airbnb data science notebook public, airbnb org datasets'],
  ['Tourism satellite accounts and tourism spending data: WTTC, UNWTO, BEA travel and tourism satellite account, national tourism expenditure surveys', 'tourism satellite account data, wttc data, bea travel tourism satellite account api'],
  ['Hospitality labour and cost data: BLS QCEW/CES leisure and hospitality, hotel wages, cleaning-service prices, STR operating cost datasets', 'bls qcew leisure hospitality data, hotel wages data bls, cleaning cost dataset str'],
  ['Payments and merchant data: Visa/Mastercard SpendingPulse releases, Stripe/Adyen indexes, remittance and cross-border card data, tourism receipts from balance of payments', 'spendingpulse data, balance of payments travel receipts data, cross border card spending data'],
  ['Currency and travel affordability crowdsourced data: Numbeo, Expatistan, hotel price indices (Hotels.com HPI archives), Trivago Hotel Price Index, Kayak price trackers', 'numbeo scraper dataset, hotel price index dataset, trivago hotel price index data'],
  ['University and municipal research datasets on STRs published on GitHub (city planning departments, urban labs, McGill UPGo, Inside Airbnb collaborators)', 'upgo mcgill short term rental data, urban planning str dataset city report github, str research dataset city'],
  ['UPGo (McGill) and strr R package: STR research tooling and datasets for Canada/US cities', 'strr r package, upgo strr, upgo short term rental'],
  ['Hotel and STR reviews as demand: review velocity datasets (Google, TripAdvisor, Booking) with dates; review-based nowcasting repos', 'hotel reviews dataset with dates, review velocity tourism nowcast, review count time series dataset'],
  ['China outbound and domestic travel data: CNTA/Ministry stats, Ctrip reports, Chinese holiday travel datasets, Hong Kong/Macau arrivals', 'china tourism statistics dataset, hong kong visitor arrivals data, macau visitor data'],
  ['Middle East, Africa and India travel data: UAE/Dubai DET stats, Saudi, Turkey MoT, Morocco, Egypt, South Africa StatsSA, India foreign tourist arrivals', 'dubai visitor statistics data, turkey tourism statistics dataset, india foreign tourist arrivals data'],
  ['Caribbean, Central America and island tourism stats (CTO, Costa Rica ICT, Dominican Republic BCRD, Bahamas, Puerto Rico) and Hawaii-like party-size / length-of-stay surveys', 'caribbean tourism statistics data, costa rica ICT tourism data, puerto rico tourism data'],
  ['Length-of-stay, party-size and trip-purpose survey microdata (NTTO SIAT, UK IPS, Eurostat tour_dem, Japan travel survey, national travel surveys)', 'survey of international air travelers data, international passenger survey data, tour_dem eurostat'],
  ['Airport and city tourism dashboards scraped to CSV (NYC Tourism, Visit Florida, Las Vegas LVCVA, Orlando, Hawaii DBEDT, Destination DC, Visit California)', 'lvcva visitor statistics data, visit florida data, nyc tourism statistics data'],
  ['Insurance, safety and travel advisories datasets (State Dept advisories history, travel insurance claims, crime by city) as demand shocks', 'travel advisories dataset history, state department advisory data scraper'],
  ['Short-term-rental insurance/incident, noise complaint and 311 datasets mentioning Airbnb (NYC 311, LA MyLA311, SF 311) as enforcement/activity proxies', 'nyc 311 airbnb complaints data, 311 short term rental complaints dataset'],
  ['Electricity, water and waste data as occupancy proxies (smart-meter open data, tourist-area utility consumption), and mobile-phone tourism statistics (Eurostat MNO experimental)', 'mobile phone data tourism statistics, smart meter occupancy dataset, mno tourism eurostat'],
  ['Hotel chain and REIT public datasets: loyalty program sizes, unit counts, Marriott/Hilton/Hyatt pipelines, hotel REIT portfolio RevPAR by market from filings', 'hotel reit revpar by market dataset, marriott hilton pipeline data, hotel loyalty members data'],
  ['Vacation rental damage/turnover/cleaning marketplaces (Turno, TurnoverBnB), STR supply services (Airbnb photographer, key exchange) datasets', 'turnoverbnb data, str cleaning marketplace data, vacation rental services dataset'],
  ['Country-level Airbnb studies with shared data: OECD/EU/UN reports with data appendices on platform tourism, Eurostat-Airbnb data-sharing agreement outputs, ECB/IMF papers', 'eurostat airbnb data sharing platform, oecd platform tourism data, imf tourism platform data'],
  ['Booking-curve / pace / pickup datasets for hotels and STRs (on-the-books, forward bookings), Key Data / Transparent / Lighthouse (OTA Insight) samples, revenue-management forward curves', 'hotel booking pace dataset, forward bookings on the books data, otb pickup dataset'],
  ['Housing and rent inflation nowcasts (Zillow observed rent, Apartment List, Fed rent nowcasts), new-tenant rent index, shelter CPI nowcasting repos', 'new tenant rent index data, shelter cpi nowcast github, rent nowcast repo'],
  ['Population, migration and second-home data (IRS migration, Census CPS, USPS change of address, second-home counts, holiday-home shares Europe)', 'irs migration data, usps change of address data, second homes dataset'],
  ['Corporate travel and business-travel data (GBTA, Concur/SAP, Navan public indices, conference calendars), MICE datasets', 'business travel index data, conference calendar dataset, corporate travel dataset'],
  ['Student, seasonal-worker, medical and other niche travel-demand datasets; university calendars; military moves', 'university academic calendar dataset, seasonal worker visa data, medical tourism dataset'],
  ['Gig-economy and platform-economy datasets (Uber/DoorDash/Etsy/Upwork public data) used as cross-platform consumer-behaviour reads', 'gig economy dataset platform, uber data public, etsy dataset public'],
  ['Retail and ecommerce alt-data open samples (web-scraped prices, Amazon rank), as templates for platform KPI nowcasting', 'web scraped prices dataset, amazon best seller rank dataset, ecommerce alt data open'],
  ['Time-series datasets curated for tourism forecasting research (Monash, M-competitions tourism, Kaggle tourism forecasting), tourism demand models with data', 'tourism forecasting dataset monash, tourism competition dataset, tourism demand forecasting github data'],
  ['Airbnb and hotel price-elasticity, hedonic and mix-decomposition studies with data (bedroom counts, listing quality, superhost premium)', 'airbnb hedonic pricing data github, hotel price elasticity dataset, airbnb price determinants dataset'],
  ['Occupancy/demand estimation from satellite, nightlights, or imagery; parking-lot counts; Sentinel-based tourism activity', 'nightlights tourism data, satellite parking lot counts dataset, viirs nightlights tourism'],
  ['Airline fare tracking datasets (Google Flights scrapers, Skyscanner, Hopper reports), airfare price indices', 'google flights scraper dataset, airfare price history dataset, skyscanner api data'],
  ['Public transit ridership and airport rail links (MTA, TfL, RATP, JR) as visitor proxies; ridership open data', 'mta ridership data, tfl ridership data, ratp open data ridership'],
  ['Hotel and STR supply from CoStar/CBRE/JLL/Cushman public reports scraped; real-estate broker STR reports with data', 'cbre hotel data, jll hotel report data, str supply report data csv'],
  ['STR listing-level histories compiled by researchers (listing survival, churn, professionalisation, multi-year listing IDs across cities)', 'airbnb listing survival dataset, airbnb churn listings multi-year, airbnb professionalization dataset'],
  ['Amsterdam, Berlin, Vienna, Copenhagen, Prague, Lisbon, Athens, Florence, Venice, Dublin STR datasets and city-report data appendices', 'amsterdam airbnb dataset, berlin airbnb data, lisbon alojamento local data, florence airbnb dataset'],
  ['Latin America STR datasets: Mexico City, Cancun, Rio, Sao Paulo, Buenos Aires, Bogota, Medellin, Lima, Santiago Airbnb data and regulation', 'airbnb mexico city dataset, airbnb rio de janeiro data, medellin airbnb dataset'],
  ['APAC STR datasets: Tokyo/Kyoto minpaku registration data, Seoul, Bangkok, Bali, Sydney/Melbourne, Auckland, Singapore, Hong Kong Airbnb data and regulation', 'minpaku data japan, airbnb tokyo dataset, bali airbnb data, auckland airbnb dataset'],
  ['US sunbelt and mountain STR markets datasets: Florida (Orlando, Miami, Tampa), Arizona (Scottsdale, Sedona), Texas, Colorado (Breckenridge, Denver), Tennessee (Gatlinburg), Great Smoky Mountains', 'florida airbnb dataset, scottsdale short term rental data, gatlinburg airbnb data, breckenridge str data'],
]

const MODALITIES = {
  gh: `MODALITY: GitHub CLI search. Use Bash with \`gh search repos <terms> --limit 50 --sort stars --json fullName,description,stargazersCount,updatedAt,url,license\` (also try \`--sort updated\` and \`--topic=<topic>\`). HARD LIMIT: at most 6 gh search calls total; the search API allows 30/min shared with ~10 other agents. If you see "rate limit" / 403 / 429, run PowerShell \`Start-Sleep -Seconds 40\` once and retry once; if it fails again, switch to WebSearch (\`site:github.com ...\`). Do NOT use \`gh search code\` (10/min limit) more than once. To inspect a promising repo, prefer WebFetch on https://github.com/<owner>/<repo> or https://raw.githubusercontent.com/<owner>/<repo>/HEAD/README.md (no API cost) over \`gh api\`; use \`gh api repos/<owner>/<repo>/contents/<path>\` only when you need a directory listing to confirm data files are actually committed (max 8 such calls).`,
  web: `MODALITY: web search. Use WebSearch (load it with ToolSearch "select:WebSearch,WebFetch" first) with queries like \`site:github.com <terms>\`, \`<terms> github dataset csv\`, \`<terms> "github.com" data\`, and also queries that find Kaggle / Zenodo / Dataverse / HuggingFace pages, awesome-lists and blog posts that link to GitHub repos. Run 8-15 searches. Verify each promising repo by WebFetch on https://github.com/<owner>/<repo> (or its raw README). If WebSearch reports its session budget is exhausted (it is shared across all scouts), switch to WebFetch on a search engine results page: https://html.duckduckgo.com/html/?q=<url-encoded query> or https://www.bing.com/search?q=<url-encoded query> (include site%3Agithub.com), and you may then also use up to 4 \`gh search repos <terms> --limit 50 --json fullName,description,stargazersCount,updatedAt,url,license\` calls (on 403/429: PowerShell Start-Sleep -Seconds 40, retry once). Otherwise do NOT use \`gh search\` in this modality.`,
}

const SCOUT_SCHEMA = {
  type: 'object',
  properties: {
    candidates: { type: 'array', items: { type: 'object', properties: {
      url: { type: 'string', description: 'https://github.com/<owner>/<repo> (or a non-GitHub host if the repo only points there; say so in notes)' },
      name: { type: 'string' },
      category: { type: 'string', enum: CATS },
      data_kind: { type: 'string', enum: ['stored_dataset', 'acquisition_method', 'both', 'pointer_to_external_host'] },
      what_it_holds: { type: 'string', description: 'concrete: files, tables, fields, how many rows, what source' },
      geography: { type: 'string' },
      time_coverage: { type: 'string' },
      last_activity: { type: 'string', description: 'last commit / release date if seen' },
      size_hint: { type: 'string' },
      license: { type: 'string' },
      why_useful: { type: 'string', description: 'one or two sentences tying it to an ABNB KPI or a numbered gap in CONTEXT.md' },
      potential: { type: 'string', enum: ['high', 'medium', 'low'] },
      gap_targets: { type: 'array', items: { type: 'integer' }, description: 'numbers of the CONTEXT.md gap list this addresses, if any' },
      duplicate_of_holding: { type: 'string', description: 'if it duplicates something we already hold, say what; empty otherwise' },
    }, required: ['url', 'name', 'category', 'data_kind', 'what_it_holds', 'why_useful', 'potential'] } },
    queries_run: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string', description: 'dead ends, rate-limit problems, ideas for other themes worth a scout' },
  },
  required: ['candidates', 'queries_run', 'notes'],
}

function scoutPrompt(idx, theme, hints, modality) {
  return `You are scout #${idx} in a cataloguing sweep of GitHub for open data that could help forecast Airbnb (ABNB). First Read ${CONTEXT} (about 120 lines) — it says what we hold, the 20 numbered gaps, and the rules.

YOUR THEME: ${theme}
Keyword hints (starting points only — go broader): ${hints}

${MODALITIES[modality]}

What to return: every repository you find that MIGHT have potential — a committed dataset, release assets, a data mirror, a one-command pull from a public source, an academic replication package, or a scraper/client for a NON-Airbnb site. Cast a wide net: 5-25 candidates is typical. Rate 'potential' honestly (high = fills a numbered gap or is a substantial dataset; medium = plausibly useful; low = marginal but real). Exclude: pure tutorials/notebooks re-analysing the single well-known Kaggle NYC-2019 Airbnb file with nothing new, generic ML boilerplate, dead links, repos with no data and no working method. Do not evaluate signal or alpha. Do not run any scraper. Do not clone anything.

Be concrete in what_it_holds (file names, row counts, years, cities). When a repo only points to an external host (Zenodo, Kaggle, Dataverse, Google Drive, S3), record the external URL in what_it_holds and set data_kind='pointer_to_external_host'.

Before returning, also Write your full result as JSON to ${SCOUT_DIR}/scout_${String(idx).padStart(3, '0')}.json (include a top-level "theme" and "modality" field: theme=${JSON.stringify(theme)}, modality="${modality}"). Then return the structured output. Budget: roughly 25 tool calls; stop searching when results repeat.`
}

const LENSES = [
  'a hedge-fund alternative-data buyer who has seen every vendor deck (card panels, receipts, app data, web traffic, satellite, geolocation) and knows which of those have free or academic open-source analogues on GitHub',
  'an urban economist studying platform housing effects who knows every replication package and city-open-data STR extract',
  'a national tourism-statistics official who knows which agencies publish monthly accommodation, platform, and arrivals microdata and which GitHub clients wrap them',
  'a revenue manager at a large vacation-rental property-management company who knows pace reports, comp sets, PMS exports, channel data and where samples leak onto GitHub',
  'a quant building a KPI nowcast for a consumer-internet company who cares about point-in-time vintages, engagement proxies and mixed-frequency methods',
  'an airline network planner who knows capacity, schedule, fare and passenger datasets and their open-source loaders',
  'a payments and consumer-credit analyst who knows public card-spend trackers, BNPL disclosures, central-bank real-time indicators and complaint databases',
  'a regulator/compliance analyst tracking STR ordinances, registration numbers, enforcement data and DAC7 platform reporting across the EU, US, Canada and Australia',
  'a data journalist at a travel-industry outlet who has scraped OTA sites, hotel price indices, app rankings and Wayback snapshots and published the code',
  'an FX and macro strategist who models translation effects and cross-border travel flows and knows open exchange-rate, purchasing-power and balance-of-payments tourism data',
  'an Airbnb superhost / small property manager who uses open-source tools (calendar sync, pricing, occupancy dashboards) that embed market comps',
  'a computational social scientist who works with Reddit dumps, Twitter/Flickr geotags, Wikipedia pageviews, GDELT and app-store reviews for demand measurement',
  'a real-estate investor who tracks Zillow/Redfin/Realtor exports, county assessor data, mortgage rates and STR yield calculators with embedded market data',
  'an events and shocks analyst (World Cup 2026, hurricanes, wildfires, strikes, visa changes) who knows the open event calendars and disaster databases',
  'a sell-side analyst covering online travel who assembles consensus history, peer KPIs, 13F ownership, options-implied moves and earnings-drift datasets',
  'a computer-vision / geospatial researcher using satellite, nightlights, POI and mobility datasets to estimate tourism activity',
]

function wildcardPrompt(idx, lens) {
  return `You are wildcard scout #${idx}. First Read ${CONTEXT}. Think as ${lens}. Write down 10 data-source ideas that are NOT obviously "Airbnb" searches but could plausibly matter for forecasting Airbnb's nights, ADR, GBV, revenue, take rate, regional mix, cancellations/RNPL or the Q4 guide. Then hunt for each idea on GitHub using BOTH WebSearch (site:github.com …; load with ToolSearch "select:WebSearch,WebFetch") and at most 5 \`gh search repos ... --limit 40 --json fullName,description,stargazersCount,updatedAt,url,license\` calls (if rate-limited: PowerShell Start-Sleep -Seconds 40, retry once, else web only). Verify promising repos with WebFetch on the GitHub page or raw README. Return every repo with any potential (aim 8-25), concrete what_it_holds, and put your 10 ideas (hit or miss) in notes so another agent can follow up. Do not evaluate signal. Do not run scrapers. Also Write the JSON to ${SCOUT_DIR}/scout_${String(idx).padStart(3, '0')}.json with top-level fields theme="wildcard: ${lens.slice(0, 60)}" and modality="wildcard".`
}

// ---------- Phase 1: scouts ----------
phase('Scout')
const jobs = []
THEMES.forEach(([theme, hints], i) => {
  jobs.push({ idx: jobs.length, kind: 'theme', theme, hints, modality: 'gh' })
  jobs.push({ idx: jobs.length, kind: 'theme', theme, hints, modality: 'web' })
})
LENSES.forEach(lens => jobs.push({ idx: jobs.length, kind: 'wild', lens }))
// Resume mode: args.only = [idx, ...] re-runs just those scouts and skips the review phase
const ONLY = (args && Array.isArray(args.only)) ? new Set(args.only) : null
const runJobs = ONLY ? jobs.filter(j => ONLY.has(j.idx)) : jobs
if (ONLY) log(`RESUME: re-running ${runJobs.length} scouts: ${[...ONLY].join(',')}`)
log(`Scout fleet: ${THEMES.length} themes x 2 modalities + ${LENSES.length} wildcards = ${jobs.length} Sonnet agents`)

const scoutResults = await parallel(runJobs.map(j => () =>
  agent(j.kind === 'wild' ? wildcardPrompt(j.idx, j.lens) : scoutPrompt(j.idx, j.theme, j.hints, j.modality),
    { label: `scout:${j.idx}:${j.kind === 'wild' ? 'wild' : j.modality}`, phase: 'Scout', schema: SCOUT_SCHEMA, model: 'sonnet', effort: 'medium' })
    .then(r => r ? { ...r, idx: j.idx, theme: j.kind === 'wild' ? 'wildcard' : j.theme, modality: j.kind === 'wild' ? 'wildcard' : j.modality } : null)
))

const ok = scoutResults.filter(Boolean)
log(`Scouts returned: ${ok.length}/${runJobs.length}`)
if (ONLY) return { resume: true, scouts_launched: runJobs.length, scouts_returned: ok.length, returned_idx: ok.map(s => s.idx) }

// ---------- dedupe (barrier justified: cross-scout merge) ----------
function keyOf(url) {
  const m = (url || '').toLowerCase().match(/github\.com\/([^\/\s#?]+)\/([^\/\s#?]+)/)
  if (m) return `github:${m[1]}/${m[2].replace(/\.git$/, '')}`
  return `other:${(url || '').toLowerCase().replace(/\/+$/, '')}`
}
const RANK = { high: 3, medium: 2, low: 1 }
const merged = new Map()
let raw = 0
for (const s of ok) {
  for (const c of s.candidates || []) {
    raw++
    const k = keyOf(c.url)
    if (!k.startsWith('github:') && !k.startsWith('other:')) continue
    const prev = merged.get(k)
    if (!prev) {
      merged.set(k, { key: k, ...c, hits: 1, themes: [s.theme], why_all: [c.why_useful] })
    } else {
      prev.hits++
      if (!prev.themes.includes(s.theme)) prev.themes.push(s.theme)
      prev.why_all.push(c.why_useful)
      if ((RANK[c.potential] || 0) > (RANK[prev.potential] || 0)) prev.potential = c.potential
      if ((c.what_it_holds || '').length > (prev.what_it_holds || '').length) prev.what_it_holds = c.what_it_holds
    }
  }
}
const unique = [...merged.values()]
log(`Candidates: ${raw} raw → ${unique.length} unique (high ${unique.filter(c => c.potential === 'high').length}, medium ${unique.filter(c => c.potential === 'medium').length}, low ${unique.filter(c => c.potential === 'low').length})`)

// ---------- Phase 2: Opus review in batches of 5, grouped by category ----------
phase('Review')
unique.sort((a, b) => (a.category || '').localeCompare(b.category || '') || (RANK[b.potential] || 0) - (RANK[a.potential] || 0))
const BATCH = 5
const batches = []
for (let i = 0; i < unique.length; i += BATCH) batches.push(unique.slice(i, i + BATCH))
log(`Review: ${batches.length} Opus agents, ${BATCH} candidates each`)

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      url: { type: 'string' },
      slug: { type: 'string', description: 'short filesystem-safe slug, e.g. insideairbnb-archive-2015-2019' },
      exists_and_has_content: { type: 'boolean' },
      usefulness: { type: 'string', enum: ['possibly_useful', 'unlikely', 'none'] },
      verdict: { type: 'string', enum: ['sample', 'catalog_only', 'discard'] },
      category: { type: 'string', enum: CATS },
      data_kind: { type: 'string', enum: ['stored_dataset', 'acquisition_method', 'both', 'pointer_to_external_host'] },
      one_line: { type: 'string', description: 'catalogue line: what it is, coverage, size, licence' },
      abnb_use: { type: 'string', description: 'which KPI / gap it could inform and how' },
      sample_plan: { type: 'string', description: 'if verdict=sample: exact files/paths or the exact keyless pull command, and the row/byte cap (<= 25 MB total, prefer <= 5 MB)' },
      tos_or_license_flag: { type: 'boolean' },
      duplicate_of_existing: { type: 'string' },
      reasoning: { type: 'string' },
    }, required: ['url', 'slug', 'exists_and_has_content', 'usefulness', 'verdict', 'category', 'data_kind', 'one_line', 'abnb_use', 'sample_plan', 'tos_or_license_flag', 'reasoning'] } },
  },
  required: ['verdicts'],
}

function reviewPrompt(b, batch) {
  const items = batch.map((c, i) => `${i + 1}. ${c.url}
   scout potential: ${c.potential}; flagged by ${c.hits} scout(s) under: ${c.themes.slice(0, 3).join(' | ')}
   category: ${c.category}; data_kind: ${c.data_kind}; geography: ${c.geography || '?'}; coverage: ${c.time_coverage || '?'}; size: ${c.size_hint || '?'}; licence: ${c.license || '?'}
   what_it_holds: ${c.what_it_holds}
   why_useful: ${c.why_all.slice(0, 2).join(' // ')}
   duplicate_of_holding: ${c.duplicate_of_holding || ''}`).join('\n\n')
  return `You are review batch ${b} of an alt-data cataloguing run for an Airbnb (ABNB) stock pitch. First Read ${CONTEXT}. Sonnet scouts flagged the ${batch.length} GitHub repositories below. For EACH one, verify it yourself: WebFetch https://github.com/<owner>/<repo> and, where needed, the raw README (https://raw.githubusercontent.com/<owner>/<repo>/HEAD/README.md) and directory listings via \`gh api repos/<owner>/<repo>/contents/<path>\` (Bash; ≤ 6 API calls per repo) to confirm what data is ACTUALLY committed or downloadable (file names, sizes, dates), the licence, last activity, and whether it merely re-analyses a well-known Kaggle file.

Decide per repo:
- usefulness: 'possibly_useful' if there is ANY plausible way it informs an ABNB KPI, a numbered gap in CONTEXT.md, a regional read, a method we lack, or a longer/older/finer version of something we hold. Be generous — this is cataloguing, not signal testing — but 'none' for dead, empty, or irrelevant repos.
- verdict: 'sample' when a Fable agent should pull a SMALL sample (stored data files, release assets, external-host file, or run a keyless pull command against a PUBLIC statistical source) — write an exact sample_plan (paths, commands, caps: ≤ 25 MB total, ≤ 5 MB preferred; take the head of large files with curl -r or a Range request; for git-tracked data use \`git clone --depth 1 --filter=blob:none --sparse\` then \`git sparse-checkout set <dir>\`). 'catalog_only' when it is useful but should NOT be pulled by an agent: scrapers of third-party websites (running them is a terms-of-service decision for a human), anything requiring an API key or login, anything touching airbnb.com, licences forbidding reuse, or datasets too large to sample sensibly. 'discard' when usefulness='none'.
- If the repo is only a pointer to an external host (Zenodo, Dataverse, Kaggle, Google Drive, S3), 'sample' is fine for Zenodo/Dataverse/S3/GitHub-releases direct links; Kaggle needs a login → 'catalog_only' with the Kaggle URL in one_line.

Write reasoning in two or three sentences each. Also Write the full JSON to ${REVIEW_DIR}/review_${String(b).padStart(3, '0')}.json before returning the structured output.

CANDIDATES:
${items}`
}

const reviews = await pipeline(batches,
  (batch, _item, b) => agent(reviewPrompt(b, batch), { label: `review:${b}`, phase: 'Review', schema: REVIEW_SCHEMA, model: 'opus', effort: 'high' })
)

const verdicts = reviews.filter(Boolean).flatMap(r => r.verdicts || [])
const counts = { sample: 0, catalog_only: 0, discard: 0 }
for (const v of verdicts) counts[v.verdict] = (counts[v.verdict] || 0) + 1
log(`Review done: ${verdicts.length} verdicts — sample ${counts.sample}, catalog_only ${counts.catalog_only}, discard ${counts.discard}`)

return {
  scouts_launched: jobs.length, scouts_returned: ok.length, raw_candidates: raw, unique_candidates: unique.length,
  review_batches: batches.length, reviews_returned: reviews.filter(Boolean).length,
  counts,
  scout_notes: ok.map(s => ({ idx: s.idx, theme: s.theme.slice(0, 60), modality: s.modality, n: (s.candidates || []).length, notes: (s.notes || '').slice(0, 300) })),
  to_sample: verdicts.filter(v => v.verdict === 'sample').map(v => ({ url: v.url, slug: v.slug, category: v.category, one_line: v.one_line, sample_plan: v.sample_plan })),
  catalog_only: verdicts.filter(v => v.verdict === 'catalog_only').map(v => ({ url: v.url, category: v.category, one_line: v.one_line })),
}