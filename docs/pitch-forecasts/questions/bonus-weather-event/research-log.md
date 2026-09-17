# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A18 with B15 and B16). Reproduction: [datasets/b14_hurdat_base_rate.py](datasets/b14_hurdat_base_rate.py) (`py -3.13`, stdlib only, under 2 s; reads `sources/hurdat2-1851-2025.txt`, writes `b14_landfalls.csv`, `b14_base_rates.csv`). The management-citation base rate is the grep of the 23 letters and 22 call mirrors described in claim 1.

## 0. Metadata
- question_name: bonus-weather-event
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B14)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-12-31
- resolution_date: 2026-12-31
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable
- batch: A18

## 0b. Question (verbatim)
### Title
Between 17 Sep 2026 and 31 Dec 2026, will a hurricane or other natural disaster be cited by Airbnb management as reducing nights or GBV, or will a Category 3+ hurricane make US landfall in Florida, Texas or the Carolinas?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on either condition (NHC landfall record; letter/call citation). Resolution 31 Dec 2026 (management citation counted through the Feb print).
### Fine Print
None beyond the resolution sentence. Conventions adopted:
1. Leg L (landfall): a hurricane at Category 3 or higher (sustained winds >= 96 kt / 111 mph) at the moment of landfall on the coast of Florida, Texas, North Carolina or South Carolina between 17 Sep and 31 Dec 2026, per the NHC's operational advisories at the time (the post-season best track is not available before resolution). A Cat 3+ storm that weakens to Cat 2 before landfall resolves No on this leg (Ian 2022 and Michael 2018 would count; Florence 2018 and Matthew 2016 would not). A landfall in Louisiana, Mississippi, Alabama or Georgia does not count.
2. Leg C (citation): Airbnb management (letter, prepared remarks, Q&A, an 8-K or a conference appearance) attributes a reduction in nights, Nights and Seats Booked, or GBV to a hurricane or other natural disaster (wildfire, earthquake, typhoon, flood, volcanic ash, extreme heat) that occurs between 17 Sep and 31 Dec 2026. The citation may come at the 5 Nov print, an intra-quarter conference, or the Feb 2027 print. Airbnb.org relief-housing paragraphs (the 3Q24 and 4Q24 templates) are not citations of a reduction. A citation of an event before 17 Sep (for example a September typhoon in Japan before the 17th) does not count.
3. "Reducing" includes "elevated cancellations", "weighed on", "headwind", or a quantified drag; a bare mention of the event in a risk factor does not count.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Across all 23 shareholder letters (4Q20-2Q26) and 22 call mirrors, management has never attributed a reduction in nights or GBV to a hurricane or natural disaster. Regex hits for hurricane/storm/wildfire/natural disaster/weather/earthquake/flood: 4Q20 letter (Airbnb.org founding), 3Q24 letter (Airbnb.org for Helene/Milton, ~800 hosts, 6,000 people housed), 4Q24 letter and call (Airbnb.org housed 19,000 after the LA fires); no hit in the 3Q22/4Q22 letters or calls (Ian, 28 Sep 2022, Cat 4 in SW Florida; 4Q22 nights +20%), none in 3Q24/4Q24 for Helene/Milton as a demand item (4Q24 nights +12%); the 4Q25 call's "weather disruptions in the 1Q" was an analyst's phrase and Mertz answered on RNPL cancellations only | `data/raw/letters/*.htm`, `data/raw/transcripts/web/[1-4]Q*.html` (grep run 2026-09-17; hit passages summarised in query-log entry 1) | 2021-02 to 2026-08 | 2026-09-17 | yes |
| 2 | The only external shock management has ever sized in growth points is the Middle East conflict (1Q26: "approximately 100bps headwind"); the RNPL ledger row D042 calls it the only cancellation shock ever quantified | `data/raw/letters/1Q26_d23351dex991.htm`; `data/processed/overnight2/D/rnpl_statement_ledger.csv` D042; B06 log claim 4 | 2026-05-07 | 2026-09-17 | yes |
| 3 | HURDAT2 (NHC best track through 2025): Cat 3+ ('L' record, HU, >= 96 kt) landfalls in FL/TX/NC/SC on or after 17 Sep occurred in 8 of 60 satellite-era seasons 1966-2025 (0.133): 1967 Beulah TX, 1989 Hugo SC, 1995 Opal FL, 2004 Jeanne FL, 2005 Wilma FL, 2018 Michael FL, 2022 Ian FL, 2024 Helene and Milton FL; 6 of 35 for 1991-2025 (0.171); 5 of 26 for 2000-2025 (0.192). After 1 Oct: 4/60 (0.067); after 15 Oct: 1/60 (Wilma, 0.017); after 1 Nov: 0/175 since 1851. Any month of the year: 15/60 (0.25) | `datasets/b14_base_rates.csv`, `b14_landfalls.csv` (from `sources/hurdat2-1851-2025.txt`, https://www.nhc.noaa.gov/data/hurdat/) | 2026-04 (2025 season added) | 2026-09-17 | yes |
| 4 | El Nino analogs (ASO RONI >= 1.0 per the CPC table cited in the Fall Cup log claim 17: 1957, 1963, 1965, 1972, 1982, 1987, 1994, 1997, 2002, 2015, 2023): 0 of 11 had a Cat 3+ FL/TX/NC/SC landfall on or after 17 Sep (1965 Betsy on 8 Sep and 2023 Idalia on 30 Aug were before the window) | `datasets/b14_hurdat_base_rate.py` output; Fall Cup log `major-atlantic-hurricanes-2026/research-log.md` claims 17, 23-24 | 2026-09-04 | 2026-09-17 | yes |
| 5 | 2026 season as of 03 UTC 17 Sep (NHC): 5 named storms (-4 vs normal), 0 hurricanes (-4), 0 majors (-1), ACE 4.4 (-94%); all five storms peaked at or below 50 kt; the only disturbance on 17 Sep (AL98, east of Bermuda) has 40% 7-day formation odds in the subtropical Atlantic; 2026 has passed the satellite-era record for the latest first hurricane (11 Sep, 2002 and 2013) | `sources/nhc_tcr_2026_20260917.html`; `sources/nhc_twoat_20260917.html`; weather.com 2026-09-10 (search) | 2026-09-17 | 2026-09-17 | yes |
| 6 | CSU 5 Aug 2026 forecast (final update): 9 NS / 4 H / 1 MH; P(>= 1 major landfall after 4 Aug): entire US coast 16% (1880-2020 average 43%), East Coast incl. peninsula Florida 7% (avg 21%), Gulf Coast from the Florida panhandle to Brownsville 9% (avg 27%); "extremely confident" of a strong El Nino at the peak. NOAA 6 Aug: 7-13 NS, 2-6 H, 0-2 MH, 75% below-normal. CPC (13 Aug): over 90% chance of a very strong El Nino in the fall; Caribbean shear the strongest on record since 1979 | `sources/csu_2026-08.pdf` (text in `csu_2026-08_text_first12pages.txt`); Fall Cup log claims 5, 14, 15 | 2026-08-05 / 2026-08-13 | 2026-09-17 | yes |
| 7 | Fall Cup question (4 Sep, rev 2) on 2026 major hurricanes: P(0 MH for the season) 0.51, P(1) 0.31, P(2+) 0.18; hazard-decay shares of a season's MH still to form: after 18 Sep 39%, after 30 Sep 28%, after 14 Oct 15%, after 1 Nov 6% (1991-2020) | `C:/Users/krish/AppData/Local/Temp/claude/C--Users-krish-citadel-abnb/f013c41a-4bb8-4250-9236-41e91754a1e2/scratchpad/forecasting/Fall-Cup-2026/questions/major-atlantic-hurricanes-2026/research-log.md` sections 5-8 | 2026-09-04 | 2026-09-17 | yes |
| 8 | Kalshi KXHURCTOTMAJ-26DEC01 (2026-09-17T08:41Z): P(>0 major hurricanes in 2026) bid 0.32 / ask 0.36 / last 0.33 (mid 0.34); P(>1) 0.13/0.16; P(>2) 0.02/0.04; volume field null (thin). KXHURPATHNC-26DEC (any hurricane landfall in NC) 0.03/0.12. No open Kalshi market for Florida, Texas, South Carolina or "major landfall" in 2026 (the series exist but returned no 2026 markets) | `sources/kalshi_markets_KXHURCTOTMAJ.json`, `kalshi_markets_KXHURPATHNC.json`, `kalshi_markets_all_*.json` | 2026-09-17 | 2026-09-17 | yes |
| 9 | Polymarket (2026-09-17T08:42Z): "Will any Category 4 hurricane make landfall in the US before 2027?" yes 0.055 (24h volume $133); no Cat-3 or Florida-specific market | `sources/polymarket_hurricane_landfall_20260917.json` | 2026-09-17 | 2026-09-17 | no |
| 10 | Conditional landfall rate: in 1991-2025 there are 6 window-years of Cat 3+ FL/TX/NC/SC landfall out of roughly 26 seasons with at least one major hurricane forming after mid-September (39% of 97 MH in 1991-2020 formed after 18 Sep, about 1.3 per season, so about three quarters of seasons had one), giving P(qualifying landfall given >= 1 late-season MH) of about 0.23; the share of US Cat 3+ landfalls that fall in FL/TX/NC/SC in 1950-2025 is about 0.65 (LA/MS/AL take the rest: Audrey, Camille, Frederic, Elena, Katrina, Rita, Ivan, Laura, Ida, Zeta) | computed from claim 3 and claim 7 | 2026-09-17 | 2026-09-17 | yes |
| 11 | Operating exposure: North America about 30% of nights; Florida about 10% of US listings (Inside Airbnb market panel), so about 3% of global nights; the 4Q22 (Ian) and 4Q24 (Helene/Milton) quarters printed nights +20% and +12% with no attribution; hurricane markets see offsetting relief, contractor and insurance-funded demand (Airbnb.org 800 hosts, 6,000 people in 3Q24) | claim 1; `research/notes/overnight/10_regional-and-segment-decomposition.md`; `docs/pitch-forecasts/00_BRIEF.md` sensitivities | 2026-09-06 | 2026-09-17 | yes |
| 12 | Brief sensitivities: 1pt of 4Q26 nights = $30M revenue; 1pt of FY27 nights = $1.50/share (fixed multiple); decelerating prints with a named external cause react better (B06 log: 1Q26 +0.7% day-1 with a 100bp conflict headwind vs -5.6% for decelerating prints) | `docs/pitch-forecasts/00_BRIEF.md`; B06 log section 9 | 2026-09-16 | 2026-09-17 | yes |
| 13 | Final recency check (17 Sep, WebSearch query 10): weather.com 10 Sep "record hurricane delay"; nothing on 16-17 Sep beyond the NHC outlook in claim 5 | `sources/web_search_log_2026-09-17.md` | 2026-09-10 | 2026-09-17 | no |

Newest load-bearing source: the NHC season summary and outlook of 17 Sep (same day) against a 105-day window; the CSU forecast is 43 days old and is used only as a seasonal prior that the 17 Sep state supersedes.

## 2. Query Log
1. [repo] regex `hurricane|storm|wildfire|natural disaster|weather|earthquake|flood` over `data/raw/letters/*.htm` and `helene|milton|ian|maui|lahaina|typhoon|flood|weather` over `data/raw/transcripts/web/[1-4]Q*.html`; hits listed in claim 1; a plain count of "hurricane" on the 3Q22, 4Q22, 3Q24, 4Q24 mirrors is 0
2. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill and format references; example log; R11, R13, R16, B06 logs
3. [repo] `research/notes/overnight/05_macro-outlook-and-transmission.md`, `10_regional-and-segment-decomposition.md` grep `florida|hurricane` (only the Canadian-visitation line); `data/processed/abnb_big_moves_7pct.csv` (no weather-driven move in 41 rows)
4. [scratchpad] Fall Cup `major-atlantic-hurricanes-2026/research-log.md` (read in full); HURDAT2 file copied to `sources/`
5. [computed] `datasets/b14_hurdat_base_rate.py` (window rates by start year and cut date; El Nino analog check)
6. [fetch] nhc.noaa.gov TCR season summary 2026; MIATWOAT text outlook; gtwo page (saved)
7. [fetch] tropical.colostate.edu/Forecast/2026-08.pdf (saved, text extracted); noaa.gov August outlook (403)
8. [Kalshi API] series?category=Climate and Weather; markets for KXHURCTOTMAJ, KXHURCTOT, KXHURCAT, KXHURPATHNC, KXHURPATHFLA, KXHURPATHGENERALMAJOR, KXHURPATHGULFCOAST, KXHURCOASTTEX, KXHURPATHSCAROLINA, KXHURTB, KXHURMIA, KXHURPATHHOU
9. [Polymarket API] public-search "hurricane landfall", "hurricane Florida"
10. WebSearch: Atlantic hurricane season outlook late September 2026 tropics (also the final 72-hour recency check: nothing newer than the 17 Sep NHC outlook)

WebSearch calls charged to B14: 1 of 5.

## 3. Leading Hypothesis Entities
El Nino, wind shear, NHC, HURDAT2, CSU Klotzbach, Florida, Kalshi KXHURCTOTMAJ, Airbnb.org, Ian, Helene, Milton

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Climatology alone (0.13-0.19 for the window) | discarded as the point; kept as the upper bound | 2026 is the most hostile Atlantic since at least 1966 (claim 5); the 11 El Nino analogs are 0/11 in the window (claim 4) |
| A late-season Caribbean "backdoor" major (Wilma 2005, Michael 2018 type) hits Florida in October | kept, the main Yes path (about 0.05) | October Caribbean genesis is the historical route in El Nino years; Kalshi still prices a one-in-three chance of some major this season (claim 8) |
| Management cites a hurricane as reducing nights even without a Cat 3 landfall (a Cat 1-2 Florida storm, a Mexican Pacific hurricane, a typhoon in Japan) | kept as a small leg (about 0.02) | 0 of 23 letters have ever done so, including Ian and Helene/Milton (claim 1); the 1Q26 conflict citation shows management now sizes external shocks when they reach about 1pt, which no plausible Q4 disaster reaches (claim 11) |
| A non-hurricane disaster (a Tokyo or Istanbul earthquake, European floods, Australian fires) cited at the Feb print | inside the 0.02 leg | a global-scale event is the only route; the base rate of such events with a visible Airbnb effect is a few percent per quarter, and the citation conditional on the event is itself well under one half |
| Texas or the Carolinas | inside leg L at a small share | after 17 Sep the record is Florida-dominated (10 of 14 events since 1950, claim 3); Beulah 1967 (TX) and Hugo 1989 (SC) are the exceptions |
| NHC operational Cat 2 vs post-analysis Cat 3 flips | priced in convention 1 | the operational advisory at landfall governs; a borderline storm (Zeta/Otto type) resolves No |

## 5. Independent Estimates
- base_rate_estimate: 0.08 - climatology 0.133 (1966-2025) / 0.171 (1991-2025) for the window, regime-conditioned by the El Nino analogs (0/11, Laplace 1/13 = 0.077) and the 2026 season-to-date (0 hurricanes at ACE -94%, no analog in the satellite era); plus about 0.015 for the citation leg outside a qualifying landfall
- decomposition_estimate: 0.085 - P(>= 1 major forms after 17 Sep) 0.34 (Kalshi mid; the Fall Cup log's own model gives 0.49 for the season on 4 Sep, decayed to about 0.38 by the 18 Sep hazard share) x P(Cat 3+ landfall in FL/TX/NC/SC given >= 1 late major) 0.23 (claim 10) = 0.078, taken to 0.065 after a hostile-regime haircut on the conditional (shear-limited majors tend to be short-lived and to recurve); plus citation leg 0.02 (independent of leg L: P(disaster with a visible Airbnb effect) about 0.10 x P(management cites it) about 0.20)
- anchor_estimate: 0.08 - Kalshi P(>0 majors in 2026) mid 0.34 (claim 8) x the historical conditional 0.23 (claim 10); the Polymarket Cat-4 US market (0.055, claim 9) scaled to Cat 3+ (x1.8) and to the four states (x0.65) gives 0.064
- anchor_value: 0.08 (Kalshi-derived; no direct market on the question)
- final_estimate: 0.08 (credible interval 0.04-0.14)
- final_minus_anchor: 0 points. NOT_INDEPENDENTLY_DERIVED flag: the anchor is itself a computation on a thin Kalshi market; the base-rate (analog) and decomposition legs were computed from HURDAT2 before the Kalshi read and land at 0.08-0.085 on their own, so the agreement is convergence rather than deference

## 6. Final Numbers
**Binary.** P(Yes) = **0.08**, credible interval **0.04-0.14**.
Split: leg L (Cat 3+ landfall in FL/TX/NC/SC, 17 Sep-31 Dec) about 0.065; leg C (management citation of a disaster in the window as reducing nights/GBV, not already a leg-L event) about 0.02; overlap negligible (a leg-L event would also be the most likely citation, but the record says even Ian and Helene/Milton were not cited).
Extreme-probability gate: not triggered (0.08 > 0.05). Resolution-criteria audit done anyway because the interval's lower end touches 0.04: (1) the operational-vs-best-track category (convention 1) and (2) whether an Airbnb.org paragraph is a "citation" (convention 2) are the two edge cases; both are resolved in the fine print and neither adds more than 0.01.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Kalshi P(>= 1 major) 0.34 | 0.20 (the Fall Cup strong-analog Poisson decayed to 18 Sep): 0.06; 0.50 (shear relaxes in October): 0.13 |
| Conditional landfall 0.23 given a late major | 0.15 (majors recurve in the subtropical Atlantic): 0.06; 0.35 (Caribbean genesis dominates): 0.13 |
| El Nino analogs weighted fully (0/11) | 0.04 |
| Climatology weighted fully (0.13-0.17) | 0.15 |
| Citation leg 0.02 | 0.0 (management never cites): 0.065; 0.05 (a global disaster and a deceleration print that wants an excuse): 0.11 |
| A hurricane forms by 30 Sep | about 0.12; NHC 7-day outlook still empty on 30 Sep: about 0.05 |

Pre-mortem ("it is 31 Dec 2026 and this resolved Yes"): (1) an October Caribbean major (the Wilma/Michael route) crossed the Florida peninsula or panhandle at Cat 3; El Nino shear is weakest in the western Caribbean in October and the analogs' zero is a small-sample zero (n 11); (2) a Cat 2/3 borderline storm was called Cat 3 operationally at landfall (the resolution uses the advisory, not the best track); (3) management, guiding a deceleration on 5 Nov or in Feb, named a disaster (a typhoon in Japan, a fire in Australia) as a reason for elevated cancellations; the 1Q26 conflict citation is the template and the incentive is real (B06 log claim 11). ("Resolved No"): the modal outcome; no update needed. Asymmetry: a Yes has almost no operating content (section 9), so the cost of being wrong is the memo's credibility, not the numbers.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| daily to 2026-11-30 | NHC Tropical Weather Outlook (2 AM / 8 AM / 2 PM / 8 PM EDT) | any area >= 60%/7-day in the Caribbean or Gulf: move to 0.15; a named hurricane forecast to Cat 3 with a US watch: move to 0.5+ within hours |
| 2026-09-30 | End of September; CSU two-week forecast; 28% of climatological MH remain | no hurricane yet: 0.05 |
| 2026-10-02 | Prelim memo freeze | quote 0.08 (0.04-0.14); state that the item is immaterial (section 9) |
| 2026-10-15 | 15% of climatological MH remain; only Wilma (2005) qualifies after this date in 60 years | no major: 0.03 |
| 2026-11-01 | No Cat 3+ FL/TX/NC/SC landfall on record after 1 Nov (0/175) | leg L mechanically dead: snap to the citation leg only (about 0.02) |
| 2026-11-05 | 5 Nov print | any attribution of cancellations to a disaster in the window: resolve Yes; otherwise leg C for Q4 events stays at about 0.02 through Feb |
| 2026-11-30 | Season end | leg L closed |
| 2027-02-11 (approx.) | Feb print (letter and call) | final check of leg C; resolve |

## 9. Impact
If Yes (modal Yes = a Cat 3+ Florida landfall in October; the citation leg carries the same operating content):

| Item | Delta if B14 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | the window starts 17 Sep; Q3 bookings are done |
| 4Q26 nights (pts) | **-0.1** (Florida about 3% of global nights x about 25% of the state affected x two weeks of a 13-week quarter x -50% net of relief and contractor demand = -0.06pt; rounded to -0.1 for evacuation-driven cancellations) | claim 11 |
| ADR (pts) | 0 | mix-neutral; relief stays are lower-ADR but tiny |
| 4Q26 revenue ($M) | **-3** (0.1 x $30M) | claim 12 |
| FY27 revenue ($M) | 0 (rebuild demand offsets by 1Q27) | claim 11 |
| FY26 adj. EBITDA margin (pp) | 0.00 (-$3M x 0.59 / $12.9bn) | brief |
| FY27 adj. EBITDA margin (pp) | 0 | brief |
| FY27 EPS ($) | 0.00 | brief |
| Stock ($/share) | **-0.2** fundamental (0.1pt x $1.50); a named external cause would if anything soften a deceleration print (B06 template), a risk to the short's narrative rather than a bonus | claim 12; B06 log section 9 |
| **EV = P x impact** | **0.08 x -$0.2 = -$0.02/share** | |
| Materiality | **Immaterial.** Management has never attributed a nights or GBV effect to a hurricane (Ian 2022, Helene/Milton 2024) or a wildfire (LA 2025); the only quantified external shock in the record is the 1Q26 Middle East conflict at about 100bp. Drop the item from the memo; keep the NHC outlook on the monitoring list only because a landfall would give management an excuse in Feb | claims 1, 2 |

RESUME: the next agent (audit response) should attack (1) the conditional landfall rate 0.23 in claim 10, which is a rough count (rebuild it as P(qualifying landfall given >= 1 MH forming after 17 Sep) directly from HURDAT2 first-96-kt dates); (2) the state boxes in `b14_hurdat_base_rate.py` (Rita 2005 at the TX/LA line is excluded; check Georgia and the panhandle boundary); (3) whether the citation leg deserves 0.02 or 0.01. Re-run after any NHC 7-day area >= 40% in the Caribbean or Gulf and on 1 Nov (leg L dies).
