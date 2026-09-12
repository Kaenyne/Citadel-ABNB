"""R3: build the reviewer audit table, one row per V and P candidate plus the gap sources R pulled.

Workstream R, government data survey, 12 Sep 2026. Krishang Surapaneni (compiled with Claude Code).

Each row carries the original verdict and first failing criterion (copied from V_candidates.csv and P_candidates.csv,
which are not modified), the audit result (upheld / overturned / reclassified), the new verdict and the evidence.
"upheld" means the stated first failing criterion is true and is the right first criterion; "overturned" means the
stated fact was wrong (a route that works, a code that exists, a file that is held); "reclassified" means the fact
is true but the verdict or its use changes (a coverage date that falls before 5 November, a supply series with a
use, a survivor that does not hold up on the reviewer window). Evidence cites R_reruns.csv, R_duplicates.csv and
raw/MANIFEST.csv. All ratios are walk-forward RMSE vs naive; "reviewer window" is 2024Q1+ scored from 1Q25 (n 6).

Run: py -3.13 analysis/src/govdata/R3_audit.py
"""
from __future__ import annotations

import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
GD = os.path.join(ROOT, "data", "processed", "govdata")
OUT = os.path.join(GD, "R")

U, O, RC = "upheld", "overturned", "reclassified"

# (workstream, candidate id) -> (audit_result, new_verdict, evidence)
DECISIONS = {
    # ------------------------------------------------------------------------------------------------ V
    ("V", "anac_brazil"): (U, "survivor (LatAm bucket only)", "Replicated 0.754 / 0.791 (2022Q1+ scored 1Q23 / 2023Q1+), jk max 0.87 / 0.90, r 0.88 / 0.64; reviewer window 0.746 but 0.983 vs the expanding mean and r 0.38 (p 0.29); on total nights 1.76 / 1.80. The LatAm mid takes 6 distinct values on 2023Q1+ and 3 on the reviewer window, so it is a fit to a step function, as V said."),
    ("V", "ibge_pms_8688"): (RC, "corroboration", "Replicated 0.929 / 0.929 but perm p 0.49 to 0.52, jk max 1.22 (8 of 9 below 1) and reviewer window 0.949 with jk max 1.12 and r -0.02. Fails the jackknife on both windows; V's own prose declined to call it a survivor. Verdict moved to corroboration (July accommodation volume -4.6% y/y)."),
    ("V", "statcan_liia"): (U, "short-window survivor", "Replicated 3.29 / 0.656 on land vehicles (full quarter), jk max 0.80; reviewer window 0.505 (jk max 1.11, r 0.51) and 0.82 vs the expanding mean, the best of the short-window group. The m2 vintage (0.811 short) fails the reviewer window (1.65). NA bucket 1.00 / 1.07 / 4.06. Corroboration for NA cross-border, as V said."),
    ("V", "jnto_arrivals"): (U, "short-window survivor", "Replicated 62.6 / 0.683 (Taiwan lag1); reviewer window 0.670 but r 0.07 (p 0.83) and 1.09 vs the expanding mean: on 2025Q1 to 2026Q2 the fit adds nothing over the target's own mean. The short-window ratio is the 2023 to 2024 normalisation."),
    ("V", "jta_nights"): (U, "short-window survivor", "Replicated 9.49 / 0.684 (foreign nights m1); reviewer window 0.709, r -0.11, 1.15 vs the expanding mean. Same normalisation artefact as JNTO."),
    ("V", "abs_340101"): (U, "short-window survivor", "Replicated 3.06 / 0.786; reviewer window 0.673, r 0.05, 1.09 vs the expanding mean. Normalisation artefact."),
    ("V", "nz_mbie_adp"): (U, "short-window survivor", "Replicated 4.53 / 0.793; reviewer window 0.698, r 0.20, 1.13 vs the expanding mean. Normalisation artefact."),
    ("V", "ine_eoap_1998"): (U, "corroboration", "Replicated 1.32 / 1.18 on total (foreign nights lag1) and 1.51 / 1.35 on the EMEA bucket; reviewer window 0.82 / 0.81 with r -0.23 / 0.11. Does not beat naive; the flat July read (-0.03%) stands as the EMEA market sentence."),
    ("V", "hawaii_vacation_rental"): (U, "corroboration (reason corrected)", "V's history reason is wrong: the 2024 report files V recorded as 404 sit under files.hawaii.gov/dbedt/visitor/vacation-rental/ (P's manifest, 38 vintages 2023-06 to 2026-07 cached). Re-tested from P's cache on within-vintage y/y: unit demand fails the NA bucket (1.38 to 1.67 on every window) and beats naive on total nights only with the wrong sign (lag1 0.78 / 0.78, r -0.22; occupancy lag1 0.65 with r -0.68). Corroboration stands on merit, not on missing history."),
    ("V", "statcan_24100053"): (U, "duplicate of statcan_liia", "Quarterly y/y correlation with the LIIA counterpart on 2023Q1+: US residents overnight vs LIIA air 0.997, non-residents 0.996, other-country residents 0.991, Canadians returning from the US vs LIIA air total 0.992 (R_duplicates.csv). The one series without an LIIA twin, Canadians returning from other countries, is r 0.72 and fails naive on the NA bucket (0.96, jk max 1.10)."),
    ("V", "italy_istat_sdmx"): (U, "duplicate of eurostat_tour_occ_nim IT", "Same source data. Eurostat IT reaches 2026-06 in the cache; ISTAT's own monthly release is not evidenced to be faster than that (SDMX timed out for V; not retried by R, low value against a June series either way)."),
    ("V", "croatia_evisitor_htz"): (RC, "no access (HTZ and DZS 404 today); timing gain over Eurostat HR unverified", "Duplicate is the wrong first criterion: Eurostat HR I552 ends 2026-06 while eVisitor publishes within days of month-end, so a working eVisitor route would add two months of coverage. R retried podaci.dzs.hr (two paths, 404) and HTZ (404). Recorded as no access; the content claim is right, the timing claim was not checked by V."),
    ("V", "france_insee_bdm"): (U, "duplicate of eurostat_tour_occ_nim FR", "Same source data; INSEE's monthly hotel occupancy lands about six weeks after month-end, a small gain over Eurostat FR (2026-06). Not retried; France is not an STR-class series in either route."),
    ("V", "portugal_ine_alojamento_local"): (O, "survivor by the letter on the EMEA bucket, pre-print coverage via the INE flash; corroboration in substance", "The INE catalogue (326 indicators, xml_indic.jsp opc=3) lists 0012088, monthly nights by establishment type incl. local accommodation, keyless JSON, one period per call; R assembled the national series 2022-01 to 2026-06 (54 months, raw/ine_pt_nights_by_type_monthly.csv). Local accommodation is a content duplicate of Eurostat PT I552 (quarterly y/y r 0.992, n 14; level ratio 0.81, sd 0.03), so the Eurostat fits carry over. Tested directly: local accommodation on the EMEA bucket 0.734 (jk max 0.90, r 0.90) scored from 1Q24 but 1.69 on the reviewer window; all-establishment total nights on the EMEA bucket 0.785 / 0.785 / 0.623 with jk max 0.92 on all three windows (bucket has 2 distinct values on the reviewer window); on total nights 0.815 then 2.95. What INE adds over Eurostat is timing: the flash press release lands about 30 days after month-end (July on 29 Aug per P; August about 30 Sep; September about 31 Oct), before 5 November, where Eurostat PT September lands after the print. Not a duplicate for the score sheet."),
    ("V", "japan_immigration_moj"): (U, "duplicate of jnto_arrivals", "JNTO compiles arrivals from the same immigration counts."),
    ("V", "census_qss"): (RC, "no coverage for the print; FY27 list", "Replicated 0.755 / 0.767 and 0.590 on the reviewer window (jk max 1.07 / 0.97 / 1.07, r 0.95 / 0.87 / 0.30), 0.96 vs the expanding mean on the reviewer window: the most robust fit in either survey. 3Q26 advance 19 Nov is after the print, so useless for 5 Nov; the 2Q26 read (+4.2% NAICS 721 revenue) is already the deceleration sentence. Carry for the February FY27 view."),
    ("V", "eurostat_tour_occ_nim"): (RC, "corroboration pre-print (July by about 20 Oct); FY27 list", "Cache ends 2026-06 for all 16 geos, dataset updated 11 Sep: a 72-day lag (descriptive), so July lands about 20 Oct (before 5 Nov) and August about 20 Nov (after), not both on 27 Oct as V assumed. EU27 I551 on the EMEA bucket 0.767 / 0.786 / 0.561 with jk max 0.90 / 0.92 / 0.86 is the best regional fit in the survey; PT I552 on the EMEA bucket 0.893 / 0.719 / 0.658. The bucket has 2 distinct values on the reviewer window. Re-score on the July release."),
    ("V", "eurostat_avia_paoc"): (U, "no coverage", "Cache confirms EU27 ends 2025-12, ES 2026-03, IT 2026-04, only AT and HR to 2026-07. Airport authorities (Heathrow monthly xlsx, August 2026 posted) are the faster route to the same arrivals class, which V showed is a normalisation fit."),
    ("V", "ntto_country"): (RC, "corroboration pre-print (August by late Oct)", "Canada and Mexico rows end 2026-06; July lands late Sep and August late Oct, both before 5 Nov, September after. Replicated 0.788 / 0.788 and 0.721 on the reviewer window (jk max 0.93 / 0.94 / 1.36). Content duplicate of StatCan Canadians returning from the US (r 0.98 to 0.99), so it is a cross-check of the StatCan read, not a new source."),
    ("V", "colombia_migracion"): (RC, "corroboration pre-print (August by about 20 Oct)", "June out 20 Aug (about 7 weeks): July about 20 Sep, August about 20 Oct, September about 20 Nov. Replicated 0.807 / 0.865 (m1 on the LatAm bucket) but 1.22 on the reviewer window with jk max 1.40, perm p 0.05 to 0.26. Not a forecaster; a LatAm destination read only."),
    ("V", "eurostat_tour_occ_ninat"): (U, "no coverage (annual)", "Cache confirms the table is annual only."),
    ("V", "fred_AIRRPMTSID11"): (U, "no coverage (reason corrected: no access today either)", "V's first failing criterion says coverage but the pull failed (fredgraph timed out four times). R retried fredgraph.csv and data/{id}.txt six times: connection reset and read timeouts; data.bts.gov Socrata MTS has no airline-traffic column. Coverage would fail anyway: September RPMs land mid-December. TSA already covers US air volume and fails."),
    ("V", "uk_ons_ott"): (U, "no coverage", "Confirmed by V's manifest (annual 2019 to 2023 workbook only). The UK series to use is the ONS short-term lets platform dataset, which V did not list (see P ons_stl_pilot)."),
    ("V", "wales_stl"): (U, "no coverage", "No series exists."),
    ("V", "texas_hot"): (U, "no coverage (annual)", "Socrata catalogue (R): Local Hotel Occupancy Tax Reporting 2022, 2023, 2024, 2025 (annual by municipality) and a Hotel Tax Permits registry; no monthly or quarterly receipts series."),
    ("V", "statcan_24100045"): (U, "no coverage", "Cube ends 2025Q4."),
    ("V", "mexico_datatur"): (O, "corroboration (hotel class, Mexico; history 2024-01, too short to test)", "Reachable on 12 Sep with a browser UA (200, three pages). hoteleria.aspx lists 30 monthly hotel-monitoring zips 2024-MES_01 to 2026-MES_06, each an xlsx with rooms available and occupied for 70 destinations against the two prior years; June 2026 total rooms occupied -2.0% y/y, rooms available +3.7% (sourced, raw/datatur_hotel_monitoring_latest_month.csv). Six y/y quarters only, so no walk-forward; July zip due about late Sep, August late Oct. The site also mirrors INEGI international-traveller PDFs to June 2026."),
    ("V", "mexico_banxico_sie"): (U, "no access (token is a key)", "SieInternet front end returns HTML without series and 400 on a CSV guess; the SIE API token is a per-user key even though registration is free, so out of scope. The DATATUR mirror carries the INEGI visitor PDFs instead."),
    ("V", "mexico_upm_boletin"): (O, "corroboration (arrivals class, PDF only, monthly to July 2026)", "politicamigratoria.gob.mx still unreachable (SSL and connection errors, no Wayback snapshot) but DATATUR mirrors the UPM bulletin as monthly PDFs by residence and nationality, 2024-01 to 2026-07 (31 files each). Not parsed within the time box; arrivals class for Mexico."),
    ("V", "korea_kto_datalab"): (U, "no access", "datalab.visitkorea.or.kr answers 200 but is a JS portal with no file endpoint; e-nara index page carries no 2026 rows; the KTO English statistics URL redirects to knto.or.kr."),
    ("V", "greece_bank_of_greece"): (U, "no access", "403 on the page and on a direct xlsx guess with a browser UA. Eurostat's monthly BoP (bop_c6_m) carries services only, no travel line (item list checked); travel is quarterly (bop_c6_q), 3Q26 in January."),
    ("V", "greece_hcaa"): (U, "no access", "403 with a browser UA; Athens airport statistics page 404. Eurostat avia EL ends 2026-03."),
    ("V", "japan_mlit_minpaku"): (U, "no access", "The host index page (200) links no PDF; the two report-page guesses are 404; the business system is behind a login (minpaku.mlit.go.jp/jigyo/login). The bimonthly results are not on a machine path R could find."),
    ("V", "bts_t100"): (U, "no access", "See fred_AIRRPMTSID11: FRED reset on every attempt; BTS Socrata MTS has no airline column; the T-100 download is form-gated."),
    ("V", "india_mot_fta"): (U, "no access", "tourism.gov.in statistics pages (three) carry no xlsx or pdf links; the monthly FTA figure is a PIB press release."),
    ("V", "scotland_stl_licensing"): (RC, "corroboration (supply signal), FY27 list", "Right first criterion for a nights proxy, but the series has a use V did not state: licence applications and grants are a supply count, and the ADR v3 M note leaves a supply-growth lead (fewer entrants correlating with firmer incumbent pricing, wedge-corrected r -0.68). Quarterly, about a three-month lag. V did not find the publication link; not pulled by R."),
    ("V", "nyc_ose_registry"): (RC, "corroboration (supply signal), already in the regulatory package", "Registered-host counts are the NYC supply series; the LL18 supply collapse is already carried by the regulatory package (PR #19). Registration-data page 404 today; nothing to pull."),
    ("V", "florida_dbpr_vacation_rental"): (RC, "corroboration (supply signal), low value", "Licence counts by county are a supply series, not a nights series; usable only for the supply-growth lead, and Florida is one state. Not probed by V or R."),
    # ------------------------------------------------------------------------------------------------ P
    ("P", "hicp_cp112_countries"): (RC, "short-window survivor", "P scores both windows from 1Q24 (the long window only lengthens the fit); scored from 1Q23 as V does, Portugal HICP level is 1.042 vs naive on 2022Q1+ (jk max 1.23, 1 of 14 below 1). Short window 0.790 replicated (jk max 0.90). Reviewer window 0.942, jk max 1.30, 1.05 vs the expanding mean. The euro-area series J2 already holds is 0.953 / 0.914 / 1.178 on the same construction. Portugal adds a flat-slope level model, not a stronger one."),
    ("P", "ine_rtapi"): (U, "rejected (wrong sign)", "Replicated 0.911 (long, scored 1Q23) / 0.808 with r -0.75 / -0.83, slope negative on every refit; reviewer window 1.39 (jk max 1.66); 2.6 / 5.1 on EMEA ex-FX. A negative fit to the USD-reported series that fails out of the normalisation."),
    ("P", "nz_cpi_accommodation"): (U, "short-window survivor", "Replicated 0.762 short (jk max 0.86), 2.06 long; reviewer window 1.108 (jk max 1.35). APAC target modelled before 4Q24."),
    ("P", "hicp_cp11202"): (U, "short-window survivor (wrong sign)", "Swiss level on the residual replicated 0.806 with r -0.85; reviewer window 1.262 (jk max 1.50). Multiple-comparison accident, as P said."),
    ("P", "abs_cpi_holiday"): (U, "short-window survivor", "Replicated 0.848 short, 2.21 long; reviewer window 0.999, r -0.19."),
    ("P", "hicp_cp11201"): (U, "short-window survivor (wrong sign)", "Greek hotels level on reported ADR replicated 0.761 with r -0.84; it also holds on the reviewer window (0.698, jk max 0.83, r -0.88) and the slope is negative on every refit, so it is a stable negative correlation rather than an accident, most plausibly EUR-USD moving Greek euro inflation against USD-reported ADR. Rejected as a price proxy stands; noted as an FX artefact worth one line in the FX estimator work, not here."),
    ("P", "japan_cpi_hotel"): (U, "short-window survivor", "Replicated 0.906 short (jk max 1.02), 2.07 long; reviewer window 0.818 with r 0.45 (p 0.24). Weak."),
    ("P", "ine_hotel_adr"): (U, "short-window survivor", "RevPAR level on EMEA ex-FX replicated 0.911 short (jk max 1.17), 1.85 long; reviewer window 0.954. IPH already held."),
    ("P", "ons_cpi_112"): (U, "short-window survivor", "Hotels level on EMEA ex-FX replicated 0.936 short (jk max 1.17), 1.45 long; reviewer window 0.725 (jk max 0.79, r 0.73) is the best EMEA feature on 2025Q1 to 2026Q2, on a target with 3 distinct values there."),
    ("P", "bea_travel_xm_price"): (U, "short-window survivor", "Export travel price diff on the residual replicated 0.824 (jk max 0.96, r 0.70); reviewer window 1.134 (jk max 1.36): the 0.82 rests on the 2024 scored quarters. Keep the 29 Oct check as a corroboration line only, as P proposed."),
    ("P", "hawaii_vr_adr"): (U, "corroboration", "Replicated 1.217 with r -0.56; basis breaks as P described; V's volume re-test from the same cache fails too."),
    ("P", "ine_hdpi"): (U, "corroboration", "Replicated 1.10 on reported ADR with r -0.72 (negative on every refit); on EMEA ex-FX 1.77 / 2.05 / 0.83."),
    ("P", "bea_pce_accom_travel"): (U, "corroboration", "Does not beat naive; held series."),
    ("P", "portugal_ine_adr"): (U, "corroboration (reason corrected)", "The catalogue (326 indicators) carries no ADR or RevPAR indicator at all, only nights, guests, capacity and occupancy, so the varcd is not undiscoverable, it does not exist in the JSON API; the flash PDF is the only monthly route. The nights indicator 0012088 does exist (see V portugal_ine_alojamento_local)."),
    ("P", "ons_cpi_11203"): (U, "corroboration", "1.33 replicated; step series."),
    ("P", "ine_tcpi"): (U, "corroboration", "1.16, negative r."),
    ("P", "bls_cpi_sehb02"): (U, "corroboration", "Replicated 1.007 short (jk max 1.16), 2.86 long, 1.30 reviewer window."),
    ("P", "statcan_cpi_trav_acc"): (U, "corroboration", "1.10, does not beat naive."),
    ("P", "bls_ppi_hotels"): (U, "corroboration", "1.21, does not beat naive."),
    ("P", "ibge_ipca_hosped"): (U, "corroboration", "1.29, negative r, LatAm target disclosed only from 4Q24."),
    ("P", "eurostat_sppi_i55"): (U, "no coverage for the print; FY27 list", "3Q26 in December, confirmed. Portugal I55 level short window 0.683 replicated (jk max 0.77); long window scored from 1Q23 is 1.023, so 'both windows' again rests on P's 1Q24 scoring; reviewer window 0.813 (jk max 1.18)."),
    ("P", "hicp_cp11209"): (O, "corroboration (published to 2026-07 under code CP11203; does not beat naive)", "In the coicop18 (ECOICOP v2) code list the sub-class for accommodation services of other establishments is CP11203, not CP11209. R pulled prc_hicp_minr CP11203 RCH_A: 14 geos to 2026-07, EA and EU27 from 2017-12, ES, DE, FR, IT, PT from 2015 to 2018. Tested on the four targets (224 pairs, 672 tests): 3 beat naive on the short window (CZ 0.898, DE 0.932 on EMEA ex-FX; HU 0.98 on the residual, wrong sign), none on all three windows. Readings: EA July 2.5 (2Q26 2.7, 1Q26 3.0), EU27 4.7 (4.9), ES 2.6 (2.6), FR 3.1 (3.3), IT 1.9 (2.4), PT 2.7 (2.7), DE 2.1 (2.9): the private-lets price item is decelerating gently where the hotel item is not."),
    ("P", "statcan_taspi"): (U, "no coverage", "Terminated 2019Q4."),
    ("P", "mexico_inpc_hotel"): (U, "no access (token is a key)", "INEGI and Banxico tokens are per-user keys; datos.gob.mx CKAN search 404 on 12 Sep. Low value, as P said."),
    ("P", "lvcva_adr"): (U, "no access (no machine-readable file)", "lvcva.com answers 200 with a browser UA (P recorded 403) but the visitor-statistics page exposes no xlsx or pdf link (dashboard); no Wayback snapshot returned. Hotel class, one city."),
    ("P", "singapore_stb_arr"): (U, "no access", "data.gov.sg v2 search returns unrelated datasets for 'hotel'; the old CKAN endpoint is 404; data.gov.hk search and the C&SD API guess return nothing for hotels."),
    ("P", "hongkong_hktb_arr"): (U, "no access", "PartnerNet login; no open-data route found."),
    ("P", "nz_mbie_adp"): (U, "wrong asset class for P", "Volume series; V tested it (short-window survivor, normalisation artefact)."),
    ("P", "croatia_evisitor"): (U, "wrong asset class for P", "Volume series; see V croatia_evisitor_htz (no access)."),
    ("P", "japan_mlit_minpaku"): (U, "wrong asset class for P", "Volume series; see V japan_mlit_minpaku (no access)."),
    ("P", "ons_stl_pilot"): (RC, "no coverage for the print (right asset class); FY27 list", "P's 404 was a moved page. The ONS 'Short-term lets through online collaborative economy platforms, UK' family is live: bulletin July 2023 to December 2025 released 24 June 2026, monthly dataset of guest nights, nights and stays from Airbnb, Booking and Expedia data (R pulled it: UK nights 2023-07 to 2025-12, y/y +9 to +12% in 2H25, sourced). Semi-annual with a six-month lag, so 1H26 lands about December 2026: no 3Q26 read, and 30 months is too short to walk-forward. It is Airbnb's own asset class for the UK and V never listed it; carry for the FY27 view next to Eurostat tour_ce_omr."),
    ("P", "lodging_tax_us"): (U, "wrong asset class", "Dollars without nights (Florida TDT, Texas HOT, NYC, Colorado, Vermont); no receipts-and-nights pair found that would form an ADR. The Vermont meals-and-rooms STR line is a quarterly GBV-type series at best."),
    ("P", "tourist_tax_eu"): (U, "wrong asset class", "Annual, dollars only."),
    ("P", "us_census_qss_721"): (U, "wrong asset class for P", "Revenue; V's row carries it (FY27 list)."),
    ("P", "bls_ipp_air_fares"): (U, "wrong asset class", "Airfares; CPI airfares already tested in G."),
    # ------------------------------------------------------------------------------------------------ R gap sources
    ("R", "bcb_sgs_travel"): ("new", "survivor by the letter (LatAm bucket), same step-function caveat as ANAC; knowable before the print", "Banco Central do Brasil SGS API, keyless, monthly USD millions to 2026-07 (published about the 25th of the following month, so August about 25 Sep and September about 25 Oct). Personal-tourism receipts on the LatAm bucket 0.796 / 0.788 / 0.717 with jk max 0.85 / 0.84 / 0.86 (the only LatAm feature below 1 on all three windows), r 0.88 / 0.67 / 0.34; travel expenses (Brazilians abroad) 0.731 / 0.746 / 0.853 (jk max 0.87 / 0.87 / 1.01), 1.12 vs the expanding mean on the reviewer window. Readings: expenses July +3.7% y/y against 2Q26 +23.1% and 1Q26 +21.9%; card-based outbound July +26.4% (2Q26 +32.2%); receipts July -2.9% (2Q26 +11.7%). Nominal USD, so BRL moves are inside it."),
    ("R", "eurostat_bop_c6_m"): ("new", "not worth a pull", "Eurostat monthly BoP carries goods and services aggregates only (63 items, no travel line); travel is quarterly (bop_c6_q), 3Q26 in January. National central banks publish monthly travel receipts (Spain, Portugal, Italy) but they are nominal receipts, about a two-month lag, arrivals-class information."),
    ("R", "us_monthly_travel_trade"): ("new", "reading only (history in the file starts 2024)", "Census FT-900 exhibit 3, travel exports SA (inbound visitor spend), monthly to 2026-07: y/y April -5.0, May -0.1, June +2.3, July -0.6 (sourced). BEA's time-series workbook was 404 today and FRED is unreachable, so no walk-forward. September lands 4 or 5 Nov with the trade release."),
    ("R", "airport_authority_traffic"): ("new", "list only", "Heathrow posts monthly traffic xlsx (August 2026 already up); Aena's statistics page 404 on the guessed path. Fast arrivals-class series, September by mid-October; V's arrivals results say the class is a normalisation fit, so not pulled."),
    ("R", "visa_issuance"): ("new", "list only", "US State Department monthly nonimmigrant visa issuances by nationality (xlsx, one to two month lag) would lead inbound arrivals from visa countries (Brazil, India) that management names as origin growth; not an accommodation series; not probed."),
    ("R", "central_bank_card_spend"): ("new", "list only", "Official card-spend series with an accommodation or travel split exist for small markets only (Central Bank of Ireland monthly card statistics, Stats NZ electronic card transactions); the large-market series are private (BofA, Mastercard, CaixaBank). Not probed."),
    ("R", "port_cruise_wttc_unwto"): ("new", "not worth a pull", "Cruise passengers do not use short-term rentals; WTTC and UNWTO barometers are annual or paid."),
}


def main():
    v = pd.read_csv(os.path.join(GD, "V", "V_candidates.csv"))
    p = pd.read_csv(os.path.join(GD, "P", "P_candidates.csv"))
    rows = []
    for _, r in v.iterrows():
        a = DECISIONS.get(("V", r.source))
        rows.append(dict(workstream="V", rank=int(r["rank"]), candidate=r.source, source=r["name"], original_verdict=r.verdict, original_reason=r.first_failing_criterion,
                         audit_result=a[0] if a else "not audited", new_verdict=a[1] if a else "", evidence=a[2] if a else ""))
    for _, r in p.iterrows():
        a = DECISIONS.get(("P", r.candidate))
        rows.append(dict(workstream="P", rank=int(_) + 1, candidate=r.candidate, source=r.source, original_verdict=r.verdict, original_reason=r.first_failing_criterion,
                         audit_result=a[0] if a else "not audited", new_verdict=a[1] if a else "", evidence=a[2] if a else ""))
    for (ws, cand), a in DECISIONS.items():
        if ws == "R":
            rows.append(dict(workstream="R", rank="", candidate=cand, source=cand, original_verdict="not in V or P", original_reason="", audit_result=a[0], new_verdict=a[1], evidence=a[2]))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "R_audit.csv"), index=False)
    print(df[df.workstream != "R"].audit_result.value_counts())
    print(df[df.audit_result == "not audited"][["workstream", "candidate"]])
    print(df.groupby(["workstream", "audit_result"]).size())


if __name__ == "__main__":
    main()
