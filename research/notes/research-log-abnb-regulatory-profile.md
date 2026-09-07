# RESEARCH LOG

## 0. Metadata
- question_name: abnb-regulatory-profile
- question_url: n/a
- type: continuous
- run_mode: initial
- run_date: 2026-09-05
- open_date: 2026-09-05
- close_date: 2030-12-31
- resolution_date: 2031-03-31
- scoring: unknown
- cp_visible: no
- cp_value: n/a

## 0b. Question (verbatim)
### Title
Incremental net annual revenue loss to Airbnb from housing-driven short-term-rental regulation, as a percentage of global revenue, at the end-2027 run-rate and at the end-2030 run-rate
### Resolution Criteria
Net of demand recaptured on Airbnb (nearby homes, longer stays, hotels sold on the platform). Incremental to the Q2 2026 run-rate: losses already in reported numbers (NYC Local Law 18 enforcement from September 2023, Spain's July 2025 removals) are excluded. Measured as a run-rate at the horizon date, not cumulative. One-off fines and cash items are reported separately. Sub-questions (binary, in-force-by-horizon) are listed in section 6 with their probabilities.
### Fine Print
Losses are analyst estimates scaled from the regulatory package's illustrative sensitivities and exposure anchors; there is no company disclosure of city-level revenue. Correlation between European events is imposed through a Gaussian copula (rho 0.45 EU, 0.25 US). The EU Affordable Housing Act's loss is modelled as incremental to local events, which double counts at the margin.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | The Commission will present the Affordable Housing Act on 9 September 2026; it then goes to Parliament and Council | https://www.thelocal.de/20260905/eu-to-help-cities-clamp-down-on-tourist-rentals | 2026-09-05 | 2026-09-05 | yes |
| 2 | The draft empowers cities to limit STRs, especially commercial multi-property operators, in housing-stress areas assessed by price-to-income ratios; it is not designed as a complete ban and excludes primary residences rented briefly | https://skift.com/2026/09/04/european-commission-short-term-rental-crackdown/ | 2026-09-04 | 2026-09-05 | yes |
| 3 | Regulation (EU) 2024/1028 on STR data sharing applies since 20 May 2026 | https://single-market-economy.ec.europa.eu/news/new-rules-bring-increased-transparency-short-term-rentals-sector-2026-05-20_en | 2026-05-20 | 2026-09-05 | yes |
| 4 | NYC registered hosts passed 3,500, highest since LL18 enforcement began September 2023 | https://www.nyc.gov/site/specialenforcement/news/new-yorkers-registered-to-host-surpassed-3500-for-first-time.page | 2026-09-01 | 2026-09-05 | no |
| 5 | Int 879-2026 (owner-occupied one- and two-family homes: four guests, owner not present, locked doors) introduced 30 Apr 2026, six sponsors, no committee hearing as of 31 Aug 2026 | https://intro.nyc/0879-2026+ | 2026-04-30 | 2026-09-05 | yes |
| 6 | Airbnb disclosed NYC was about 1% of global revenue before LL18 enforcement | https://www.sec.gov/Archives/edgar/data/1559720/000119312523268164/d481318dex991.htm | 2023-11-01 | 2026-09-05 | yes |
| 7 | Chicago sued Airbnb, Airbnb Living and host Slumber Stay on 23 Jun 2026 for Shared Housing Ordinance violations, seeking fines, disgorgement and an injunction | https://www.chicago.gov/city/en/depts/dol/provdrs/lit/news/2026/june/city-of-chicago-sues-airbnb-and-high-volume-host-for-operating-i.html | 2026-06-23 | 2026-09-05 | yes |
| 8 | Madrid High Court refused to suspend the EUR64m Spanish consumer fine on 23 Mar 2026; the merits appeal continues | https://www.phocuswire.com/news/online/spain-enforce-airbnb-short-term-rental-advertising-64-million | 2026-03-23 | 2026-09-05 | yes |
| 9 | Airbnb obtained a EUR70m ($80m) surety bond in May 2026 to suspend enforcement pending resolution; loss neither probable nor estimable | https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm | 2026-08-06 | 2026-09-05 | yes |
| 10 | Spain's Supreme Court annulled the single-registry procedure in RD1312/2024 (judgment 19 May 2026, published 8 Jun 2026) | https://www.boe.es/buscar/doc.php?id=BOE-A-2026-12300 | 2026-06-08 | 2026-09-05 | yes |
| 11 | INE tourist dwellings: Spain 341,001 in May 2026, -10.7% y/y; Madrid -28.9%; Barcelona -14.1%; Ibiza -26.7% | https://www.ine.es/jaxiT3/Tabla.htm?L=0&t=39364 | 2026-06 | 2026-09-05 | yes |
| 12 | Spain's Constitutional Court upheld the Catalan decree underlying Barcelona's 2028 licence non-renewal in March 2025; all 10,101 licences expire November 2028 without renewal under city policy | https://www.stampednomad.com/updates/barcelonas-tourist-apartment-phaseout | 2026 | 2026-09-05 | yes |
| 13 | Barcelona phase-2 matched cohort: 5,146 distinct HUTB identifiers; illustrative net loss $23.9m = 0.20% of FY25 revenue | research/regulatory/phase2/README.md | 2026-09-05 | 2026-09-05 | yes |
| 14 | Maui Bill 9 signed 15 Dec 2025; West Maui phase-out 1 Jan 2029, rest 1 Jan 2031; lawsuits filed Dec 2025, no injunction as of mid-2026 | https://mauinow.com/2026/01/02/as-expected-bill-9-challenged-in-court-lawsuits-seek-to-block-short-term-rental-phaseout/ | 2026-01-02 | 2026-09-05 | yes |
| 15 | Maui Planning Commission recommended against the H-3/H-4 hotel rezoning framework (Feb 2026), so rezoning needs a two-thirds council supermajority | https://mauinow.com/2026/03/05/future-of-4500-maui-vacation-rentals-uncertain-following-planning-commissions-no-vote/ | 2026-03-05 | 2026-09-05 | yes |
| 16 | Maui phase-2 matched cohort: 3,862 unit identifiers; $18.0m = 0.15% of FY25 revenue post-2031 | research/regulatory/phase2/README.md | 2026-09-05 | 2026-09-05 | yes |
| 17 | French Constitutional Council validated (19 Mar 2026) co-ownership two-thirds votes to ban tourist furnished rentals under the Le Meur law of 19 Nov 2024; Paris cut the primary-residence cap to 90 nights from 1 Jan 2025 | https://kohenavocats.fr/2026/07/28/location-meublee-touristique-copropriete-interdiction-majorite-article-26-qpc-2025-1186/ | 2026-07-28 | 2026-09-05 | yes |
| 18 | Council of State upheld (15 Jul 2026) Paris' authorisation requirement for converting commercial space to tourist rentals | https://www.clairance-urba.fr/meubles-de-tourisme-a-paris-verrouillage-des-locaux-commerciaux-par-la-mairie/ | 2026-07 | 2026-09-05 | no |
| 19 | Paris is about 1.0% of Airbnb global GBV; multi-listing hosts hold 36% of Paris listings (supply panel, Aug 2026 dump) | data/processed/inside_airbnb_city_snapshots.csv | 2026-09-05 | 2026-09-05 | yes |
| 20 | Ireland's STL register opens 1 Dec 2026 with registration required by 31 Dec 2026 (delayed from May 2026); hosts must declare planning compliance | https://www.gov.ie/en/department-of-enterprise-tourism-and-employment/press-releases/short-term-let-register-to-come-into-effect-from-december-2026/ | 2026-05 | 2026-09-05 | yes |
| 21 | England's registration scheme is not live as of July 2026 after targets of 2024, April 2026 and 'later in 2026' | https://stlsolutions.co.uk/blog/england-registration-scheme-april-2026 | 2026-07 | 2026-09-05 | yes |
| 22 | Athens districts 1 to 3 freeze runs through 2026; a joint ministerial decision on 2027 extension had not been published as of mid-August 2026; registrations no longer transfer on sale or inheritance in high-pressure areas | https://thehostdaily.com/athens-airbnb-rules-2026-2027/ | 2026-08 | 2026-09-05 | yes |
| 23 | Italy 2026: three or more properties in short lets triggers business status (VAT, SCIA); CIN mandatory; municipalities adding local day limits (Florence) | https://www.we-wealth.com/news/affitti-brevi-airbnb-2026-tre-case-partita-iva | 2026 | 2026-09-05 | no |
| 24 | Florence expanded its historic-centre STR ban to zones A1, A3, A4 (approved 4 Jun 2026, effective 21 Jun 2026); 2024 operators get a three-year transition to May 2028 | https://www.comune.firenze.it/turismo/locazioni-turistiche-brevi | 2026-06 | 2026-09-05 | yes |
| 25 | EU27 platform nights 952M in 2025; country shares France 22%, Spain 20%, Italy 15%, Greece 5.5%, Portugal 5.2%; Spain +6.5% and Portugal +4.9% y/y in Q1 2026 versus EU +9.7% | data/processed/eurostat_platform_nights_by_country.csv (Eurostat tour_ce_omr) | 2026-09-05 | 2026-09-05 | yes |
| 26 | Airbnb revenue by region: EMEA 39% (FY25 10-K geographic revenue) | citadel-abnb-files 2/data/processed/airbnb_regional_revenue_quarterly.csv | 2026-09-04 | 2026-09-05 | yes |
| 27 | California SB 346 (effective 1 Jan 2026) lets local governments compel platforms to share host and property data; Houston platform enforcement began 1 Apr 2026 | https://www.rentresponsibly.org/california-passes-bill-requiring-airbnb-vrbo-to-share-host-data-with-cities/ | 2025 | 2026-09-05 | no |
| 28 | A federal judge found Clark County (NV) STR rules likely unconstitutional and paused fines | https://thenevadaindependent.com/article/airbnb-likely-to-win-legal-battle-against-clark-county-nevada-according-to-judge | 2026 | 2026-09-05 | no |
| 29 | BC active STR listings fell from about 28,000 to just over 23,000 (government release, 2 Jun 2026) | https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026HMA0028-000639.pdf | 2026-06-02 | 2026-09-05 | no |
| 30 | Management: 80% of top 200 markets already regulated with workable rules; NYC an outlier (Q3 2023, Q4 2024 calls); Madrid and NYC named as hotel-pilot markets constrained by regulation (Q3 2025) | research/regulatory/earnings_digest.md | 2026-09-05 | 2026-09-05 | no |
| 31 | Airbnb $50m three-year rural-Spain commitment (mitigation spend) | https://news.airbnb.com/es/compromiso-rural-una-apuesta-por-el-turismo-descentralizado-en-espana | 2025-11 | 2026-09-05 | no |
| 32 | No Polymarket, Kalshi or Metaculus market exists on Airbnb regulation outcomes | search (see query log) | 2026-09-05 | 2026-09-05 | no |
| 33 | EU ordinary legislative procedure: STR data regulation proposed Nov 2022, adopted Apr 2024 (17 months) | training | unknown | 2026-09-05 | yes |
| 34 | CJEU Airbnb Ireland (C-390/18, Dec 2019) classified Airbnb as an information-society service, limiting national restrictions | training | unknown | 2026-09-05 | no |

## 2. Query Log
1. short-term rental regulation news September 2026
2. EU Affordable Housing Act short-term rental proposal Commission September 9 2026
3. New York Local Law 18 short-term rental amendment bill 2026 owner-occupied
4. Chicago Airbnb lawsuit June 2026 short-term rental
5. Airbnb Spain 64 million fine appeal court 2026 registry
6. Barcelona tourist apartment licences 2028 non-renewal court challenge 2026
7. Maui Bill 9 vacation rental phase-out lawsuit rezoning 2026 update
8. Paris meublés de tourisme interdiction multipropriétaires 2026 conseil de Paris
9. Ireland short-term let register December 2026 Fáilte Ireland planning permission listings
10. Athens short-term rental registration freeze extension 2027 Greece
11. Italy affitti brevi nuova legge 2026 limiti città Airbnb
12. England short-term let registration scheme launch date 2026 2027 government
13. Polymarket OR Kalshi OR Metaculus market "short-term rental" OR Airbnb regulation ban 2026
14. Airbnb regulation news this week (72-hour recency check: Nevada Clark County ruling, California SB 346, Chesky services expansion; nothing that moves an estimate)

## 3. Leading Hypothesis Entities
European Commission, Affordable Housing Act, Teresa Ribera, Barcelona, Spain Ministry of Consumer Affairs, Paris, Maui County, New York City Council, Chicago

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| EU act adopted and enforced by end-2027 as a base case | discarded as base, kept at 12% | claim 33: 17-month precedent means adoption inside 15 months is the fast tail; enforcement lags adoption by a year or more |
| EU act as an outright EU-wide ban | discarded | claims 1, 2: draft is an enabling framework excluding primary residences; housing is a shared competence |
| Barcelona 2028 already blocked in court | discarded | claim 12: Constitutional Court upheld the decree in March 2025; residual risk is the May 2027 election and Catalan renewal discretion, priced at 25% blocked or delayed |
| Maui phase-out substantially exempted by hotel rezoning | kept at 30% within the Maui branch | claim 15: Planning Commission denial raises the bar to a two-thirds supermajority |
| NYC further tightening | kept at 5% residual within status quo | claim 4: enforcement stable, hosts registering; no bill to tighten identified |
| Spain fine paid in full as certain | discarded, 55% | claims 8, 9, 34: stay denied but merits open; platform-liability precedent favours Airbnb; company says loss not probable |
| Deferred-revenue style demand loss from regulation visible in guidance | discarded | regulatory package: every quarter since NYC enforcement beat its revenue range; consolidated numbers do not isolate regulation |
| Portugal national re-tightening as likely | kept at 20% | national policy reversed in Oct 2024; referendum blocked |

## 5. Independent Estimates
- base_rate_estimate: 1.4% (2030 median) — sum over events of (base-rate probability x package illustrative sensitivity), EU act excluded for lack of precedent
- decomposition_estimate: 1.7% (2030 median), 0.45% (2027 median) — Monte Carlo over the gated event table with copula correlation
- anchor_estimate: n/a — no market; Airbnb's NYC 1% disclosure and the guidance beat record are qualitative anchors only
- anchor_value: n/a
- final_estimate: 2027 median 0.45% (P5 0.02, P25 0.20, P75 0.85, P95 2.7); 2030 median 1.7% (P5 0.27, P25 0.88, P75 3.1, P95 6.4)
- final_minus_anchor: n/a — no quantitative anchor; independence justified by construction from gates and base rates

## 6. Final Numbers
Continuous, % of global revenue, incremental net run-rate loss:
| Percentile | End-2027 | End-2030 |
| 5 | 0.02 | 0.27 |
| 10 | 0.05 | 0.43 |
| 25 | 0.20 | 0.88 |
| 50 | 0.45 | 1.71 |
| 75 | 0.85 | 3.07 |
| 90 | 1.95 | 4.14 |
| 95 | 2.74 | 6.38 |
Mass below 0%: 5% (2027), 1% (2030) — NYC loosening branch. Mass above 8%: under 1% (2027), 1% (2030) — EU binding-caps tail. Modes (2030): 1.0% : 0.45, 3.0% : 0.37, 5.5% : 0.08, 0.2% : 0.10. Floor check: density is low but non-zero above 6% (EU tail); no region inside 0% to 8% where resolution would shock.
Binary sub-questions (P in force by end-2027 / end-2030): EU-AHA 12/45; EU-TAIL 2/8; ES-FINE paid 55/70; ES-REMOVE 35/55; ES-REGIONS 45/65; BCN-2028 0/45; BCN-PARTIAL 0/~25; MAUI 0/40; PARIS-PRO 30/55; PARIS-COPRO 90/95; GR-FREEZE 70/80; IE-REG 35/55; UK-ENG 20/45; IT-NAT 30/60; PT-RETIGHT 20/35; NL-AMS 30/50; US-CITY 30/55; NYC-LOOSEN 20/35; CHI-SUIT 40/60; COMPLIANCE 90/95.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| EU-AHA 2030 probability 45% (to 65%, tail 15%) | 2030 median 1.7% to 2.5%; P90 4.2% to 6.4% |
| EU-AHA conditional loss mode 1.2% (to 2.0%) | 2030 mean 2.2% to 2.5%; median 1.8% |
| Recapture 35% to 50% (all conditional losses x1.5) | 2030 median 2.6%; P95 9.6% |
| EU act never adopted | 2030 median 1.2%; P95 2.1% |
| No correlation between European events | 2030 P90 3.8%, P95 5.2% |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-09 | Commission presents the Affordable Housing Act | If enabling framework excluding primary residences: hold. If binding caps or primary residences covered: EU-AHA 2030 to 60%, tail to 15%. If presentation slips: EU-AHA 2027 to 8% |
| 2026-10-15 | NYC registration renewals and OSE enforcement data | Status quo confirmation; if Int 879 gets a hearing, NYC-LOOSEN 2027 to 30% |
| 2026-11-05 | Airbnb Q3 2026 call | Update recapture assumption from any hotel or Spain commentary; compliance cost line |
| 2026-12-01 | Ireland register launch | If live: IE-REG 2027 to 45%; if slipped again: to 20% |
| 2026-12-31 | Greek joint ministerial decision on 2027 freeze | If extended and expanded: GR-FREEZE to 90%; if lapses: to 30% |
| 2027-03-31 | Chicago motion rulings; Council/Parliament first readings on the EU act | Reprice CHI-SUIT and EU-AHA adoption gate |
| 2027-05-31 | Barcelona municipal election | Council change against non-renewal: BCN-2028 to 25%, BCN-PARTIAL to 40% |
| 2027-06-30 | Maui court rulings, rezoning vote | Injunction: MAUI to 20%; rezoning passes: MAUI to 25% |
| 2027-12-31 | Hazard checkpoint | Any event not in force snaps to its 2030-only branch; re-run the script |
| quarterly | Default re-check cadence after the EU text | Monthly until 2026-09-09, then quarterly |
