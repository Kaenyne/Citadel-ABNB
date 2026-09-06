"""Workstream 01: data census and predictive-mapping matrix.

Reads:  nothing large. The row table below was compiled by hand on 6 Sep 2026 from
        data/processed/**, data/raw/**, data/manifests/*.csv, theos-past-research/**,
        the main tree's research/regulatory/** and ABNB-Crossover/**, and the notes in
        research/notes/. Row counts and date ranges were read with pandas at compile
        time (see research/notes/overnight/01_data-census.md for the method).
        At run time the script only checks whether each cited file still exists.
Writes: data/processed/overnight/01_data_census.csv (one row per series/dataset)
        and prints the tallies quoted in the note (rows by target KPI, by role,
        tested vs untested, surviving signal).

Run: py -3.13 analysis/src/overnight/01_data_census.py
"""
from __future__ import annotations

import csv
import os
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAIN = ROOT.parent / "citadel-abnb"          # main tree: ABNB-Crossover/, research/regulatory/ (read only)
PREDICT = ROOT.parent / "citadel-abnb-predict"  # predictive worktree: data/raw/macro, peers, prices
OUT = ROOT / "data" / "processed" / "overnight" / "01_data_census.csv"

COLS = ["id", "name", "file_or_location", "owner", "source", "licence", "frequency",
        "first_date", "last_date", "n_obs", "point_in_time_lag", "maps_to", "role",
        "tested_already", "verdict_so_far", "untested_idea", "combinable_with",
        "build_forward", "on_disk"]

# Short aliases used in the table
P = "data/processed/"
PP = "data/processed/predictive/"
PO = "data/processed/overnight/"
R = "data/raw/"
T = "theos-past-research/"
TG = T + "research/guidance/data/normalized/"
TE = T + "research/edge-discovery/"
REG = "MAIN:research/regulatory/"            # main tree, read-only
XO = "MAIN:ABNB-Crossover/"
SSD = "Theo external volume (/Volumes/PortableSSD/ABNB_DATA_EXPANSION), manifest in data/manifests/"
DRIVE = "private shared Drive (licensed, not in repo)"

LETTERS = "Shareholder letters 8-K Ex.99.1 (S23)"
XBRL = "SEC XBRL companyfacts CIK 1559720 (S25)"
FRED = "FRED keyless CSV (S30/S38)"
BEA = "BEA NIPA underlying Tables 2.4.4U/5U/6U (S29)"
IA = "Inside Airbnb listings.csv.gz (S32)"
CC = "Common Crawl CDX + WARC (S33)"
EUS = "Eurostat tour_ce_omr (S35)"
THEO = "Theo guidance dataset (S27)"

NOTE_PRED = "2026-09-06_predictive-study + predictive/03"
NOTE_REACT = "predictive/04"
NOTE_PEER = "predictive/02"
NOTE_BASE = "predictive/01"
NOTE_DRV = "2026-09-05_driver-model"
NOTE_MRG = "2026-09-05_margin-drivers"
NOTE_CAP = "2026-09-05_capital-return-panel"
NOTE_EU = "2026-09-05_eu-platform-and-backlog"
NOTE_IA = "2026-09-05_inside-airbnb-supply-panel"
NOTE_CC = "2026-09-05_cc-listing-panel"
NOTE_REG = "2026-09-05_regulatory-forecast-profile"
NOTE_TR = "2026-09-05_transcript-analytics"
NOTE_MOV = "2026-09-05_abnb-major-moves"
NOTE_PITCH = "predictive/05"


def r(id_, name, loc, owner, source, licence, freq, first, last, n, lag, maps_to, role,
      tested, verdict, idea, comb="", bf="no"):
    return dict(id=id_, name=name, file_or_location=loc, owner=owner, source=source,
                licence=licence, frequency=freq, first_date=first, last_date=last, n_obs=n,
                point_in_time_lag=lag, maps_to=maps_to, role=role, tested_already=tested,
                verdict_so_far=verdict, untested_idea=idea, combinable_with=comb,
                build_forward=bf)


ROWS = [
    # ---------------------------------------------------------------- A. Company-reported KPIs and financials
    r("D001", "Nights & Seats Booked, quarterly", P + "abnb_quarterly_kpis_from_study.csv; abnb_driver_history_quarterly.csv", "Krish", LETTERS, "public (SEC filing)", "quarterly", "1Q21", "2Q26", 22, "0: print day (after close)", "nights", "level / y-y / second derivative",
      "yes: " + NOTE_REACT + ", " + NOTE_PRED, "Nights acceleration sign sets day-1 reaction 17/21; level not forecastable pre-print", "Score the 5 Nov card: does Q3 nights y/y beat 10% (Q2) and what sign follows", "D002,D003,D060,D110,D121", "no"),
    r("D002", "Gross Booking Value, quarterly", P + "abnb_quarterly_kpis_from_study.csv", "Krish", LETTERS, "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "GBV", "level / y-y",
      "yes: " + NOTE_PRED, "Only macro hit (real PCE lag 1, r -0.84) flips sign across windows: spurious", "GBV growth minus nights growth as the price-plus-mix line vs Hawaii total rate (D165)", "D001,D003,D014,D015", "no"),
    r("D003", "ADR reported, quarterly", P + "abnb_quarterly_kpis_from_study.csv; hotel_price_monitor_monthly.csv", "Krish", LETTERS, "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "ADR", "price",
      "yes: " + NOTE_PRED, "USD trade-weighted y/y explains reported ADR y/y r -0.92 post-2022 (FX channel)", "Regress reported ADR on hotel CPI + FX + IA quote price once the 2026 quote basis has 4 quarters", "D004,D087,D088,D070,D165", "no"),
    r("D004", "ADR ex-FX (letter-stated 4Q25-2Q26; annual FX impact earlier)", P + "hotel_price_monitor_monthly.csv (abnb_adr_exfx_yoy_pct); abnb_revenue_decomposition.csv", "Krish", LETTERS, "public", "quarterly (3 exact, rest derived)", "1Q22", "2Q26", 18, "0: print day", "ADR", "price",
      "yes: " + NOTE_PRED + ", " + NOTE_REACT, "Initial claims y/y r -0.78 post-2022 (WATCH); ADR ex-FX adds nothing to margin once S&M known", "Ask IR / parse every letter for quarterly ex-FX ADR to replace the annual-FX approximation", "D078,D072,D003", "no"),
    r("D005", "Revenue, quarterly (GAAP)", P + "abnb_quarterly_costlines.csv; abnb_edgar_quarterly_kpis.csv", "Krish; Theo", XBRL + "; " + LETTERS, "public", "quarterly", "1Q20", "2Q26", 26, "0: print day (8-K acceptance ~16:05 ET)", "revenue", "level / y-y",
      "yes: " + NOTE_BASE + ", " + NOTE_EU, "Guide midpoint + trailing cushion is the best revenue forecast (MAE 1.1%); beat 19/19", "None needed; model revenue = guide top + 0 to 1%", "D030,D014,D015", "no"),
    r("D006", "Take rate (revenue / GBV), quarterly", P + "abnb_quarterly_kpis_from_study.csv (take_rate_pct); abnb_revenue_decomposition.csv", "Krish", "derived from letters", "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "take rate", "mix / level",
      "yes: " + NOTE_DRV + ", " + NOTE_PITCH, "A timing line (check-in recognition); flat and guided flat; take-rate bulls wrong 3 years unpunished", "Same-quarter y/y take rate vs RNPL share of GBV (mgmt: >20% in Q2 26) and single-fee migration dates", "D002,D005,D032", "no"),
    r("D007", "Adjusted EBITDA and margin, quarterly", P + "abnb_quarterly_costlines.csv; abnb_quarterly_cost_stack_exsbc.csv", "Krish", LETTERS + " reconciliation", "public", "quarterly", "1Q20", "2Q26", 26, "0: print day", "EBITDA margin", "level / y-y",
      "yes: " + NOTE_REACT, "Margin nowcast LOO 2.0 pts vs guide 2.8 only with print-day S&M; lagged inputs tie the guide", "Score Q3 26 nowcast 49.1-49.8% vs 50.1% ceiling on 5 Nov", "D009,D031", "no"),
    r("D008", "GAAP cost lines (CoR, ops & support, product dev, S&M, G&A, restructuring, SBC total)", P + "abnb_quarterly_costlines.csv", "Krish", XBRL, "public", "quarterly", "1Q20", "2Q26", 26, "0: print day (10-Q same day or within days)", "cost line", "level / % revenue",
      "yes: " + NOTE_MRG, "S&M 18.0% to 24.3% of revenue 2Q22 to 2Q26; every other line down; mix rotation", "Brand vs performance marketing split from 10-K as an annual driver of S&M leverage", "D009,D010", "no"),
    r("D009", "Ex-SBC cash cost stack per line, per night and % revenue", P + "abnb_quarterly_cost_stack_exsbc.csv", "Krish", LETTERS + " SBC-by-function footnote + XBRL", "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "cost line / EBITDA margin", "level / per-night",
      "yes: " + NOTE_REACT + ", " + NOTE_MRG, "Prior-quarter S&M cash deleverage vs next day-1 excess r +0.59 (n 17); one hit in ~60 tests", "Pre-register the S&M-deleverage tilt for 5 Nov; score it; re-run with n 23", "D007,D008,D042", "no"),
    r("D010", "SBC by function (ops, PD, S&M, G&A)", P + "abnb_quarterly_cost_stack_exsbc.csv (sbc_* cols)", "Krish", LETTERS + "; 1Q21/2Q21 from 10-Q", "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "SBC", "level / % revenue",
      "yes: " + NOTE_CAP, "SBC 13.1% of revenue FY25, 34.7% of FCF; heaviest in peer set", "SBC per employee vs headcount disclosures as a leading read on FY27 SBC guide", "D013,D023", "no"),
    r("D011", "D&A and other Adj. EBITDA add-backs", P + "abnb_quarterly_cost_stack_exsbc.csv (da, other_addbacks)", "Krish", LETTERS + " reconciliation", "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "EBITDA margin / FCF", "level",
      "no", "", "None; immaterial (D&A 0.7% of revenue)", "D012", "no"),
    r("D012", "FCF bridge: Adj. EBITDA, interest income/expense, tax, other, change in unearned fees, CFO, capex, FCF", P + "abnb_fcf_bridge.csv", "Krish", LETTERS + " FCF reconciliation; cash taxes from 10-K", "public", "quarterly + FY", "1Q21", "FY2025", 27, "0: print day", "FCF", "level / conversion",
      "yes: " + NOTE_MRG + ", " + NOTE_CAP, "FCF/EBITDA 105-111% FY23-25 is float growth plus interest income; nobody models it", "Interest income vs Fed funds path as an explicit FY27 FCF line", "D014,D015,D013", "no"),
    r("D013", "Capital return: buybacks, RSU withholding, diluted and basic shares, net cash return", P + "abnb_capital_return_quarterly.csv", "Krish", XBRL + "; letters from 1Q23", "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "share count / SBC", "level / y-y",
      "yes: " + NOTE_CAP, "Share count -3% to -4% a year; net cash return 60% of FCF after SBC", "Buyback pace vs 20-day post-print drawdown: does the company buy the dips", "D010,D040", "no"),
    r("D014", "Unearned fees (ContractWithCustomerLiabilityCurrent), quarter-end", P + "abnb_backlog_indicators.csv", "Krish", XBRL, "public", "quarterly", "4Q20", "2Q26", 23, "0: 10-Q filing (print day)", "revenue (next quarter)", "second derivative / backlog",
      "yes: " + NOTE_EU, "R^2 0.96 on next-Q revenue growth 4Q21-2Q25; RNPL broke it from 3Q25 (gap 2.6 to 13.2 pts)", "Unearned fees + RNPL share of GBV (letter) as a two-variable backlog once 4 RNPL quarters exist", "D015,D005", "no"),
    r("D015", "Funds held for clients (FundsHeldForClients), quarter-end", P + "abnb_backlog_indicators.csv", "Krish", XBRL, "public", "quarterly", "4Q20", "2Q26", 23, "0: 10-Q filing", "revenue (next quarter)", "backlog / nowcast",
      "yes: " + NOTE_EU, "R^2 0.78 next-Q revenue growth; 2Q26 read implies 3Q26 $4.56B vs guide $4.69-4.77B", "Score the 3Q26 funds-held read on 5 Nov; if it misses, drop the series", "D014,D030", "no"),
    r("D016", "XBRL quarterly revenue and deferred revenue (Theo's pull)", P + "abnb_edgar_quarterly_kpis.csv", "Theo", XBRL, "public domain", "quarterly", "2020-03-31", "2026-06-30", 43, "0: filing day", "revenue", "level",
      "no (duplicate of D005/D014)", "", "None", "D005,D014", "no"),
    r("D017", "KPI sentences from 10-Q/10-K text (nights 231, GBV 127, ADR 8, RNPL 2)", P + "abnb_filing_kpis.csv", "Theo", "SEC 10-Q/10-K primary documents", "public domain", "quarterly", "2023-03-31", "2026-06-30", 368, "0: filing day", "nights / GBV / ADR", "evidence (not series)",
      "no", "Evidence-grade only; clean KPI tables are HTML tables, not prose (data/README)", "Parse the 10-Q KPI HTML tables directly (nights, GBV by quarter) as a cross-check on the letters", "D001", "no"),
    r("D018", "Revenue by geography (host location): EMEA/NA/LatAm/APAC", P + "eurostat_platform_nights_quarterly.csv (emea_usd_m); " + PO + "10_xbrl_revenue_geography.csv (in flight, ws 10)", "Krish", "10-Q/10-K Geographic Information note; XBRL segment facts", "public", "quarterly (annual pre-2023 in 10-K)", "4Q23", "2Q26", 258, "0: 10-Q filing", "regional nights (proxy: regional revenue)", "mix / regional",
      "yes: " + NOTE_EU, "EMEA revenue grows with the Eurostat category, not faster (-2.4 pts 4Q23-2Q25, +8.6 on euro 3Q25-1Q26)", "Regional revenue y/y minus regional FX as the regional-nights proxy; test vs Eurostat by country", "D110,D111,D088", "no"),
    r("D019", "Revenue growth decomposition: nights, ADR ex-FX, FX, take rate, residual (pts)", P + "abnb_revenue_decomposition.csv", "Krish", "derived (letters + Theo FX split)", "public", "quarterly", "1Q22", "2Q26", 18, "0: print day", "revenue", "mix",
      "yes: " + NOTE_DRV, "Nights 8-10 pts every quarter since 2Q23; FX borrowed 3-4 pts in 1H26; take rate a timing line", "None; it is the model's identity", "D001,D004,D087", "no"),
    r("D020", "Balance sheet and multiples snapshot (30 Jun 2026 / 4 Sep 2026 close)", P + "abnb_multiples_today.csv", "Krish", XBRL + "; yfinance", "public", "one-off", "2026-06-30", "2026-09-04", 1, "n/a", "share count / valuation", "level",
      "yes: " + NOTE_DRV, "$182 discounts 7.5% FCF growth (reported) or 13.3% (SBC-adjusted) for 10 years", "None", "D013", "no"),
    r("D021", "Adj. EBITDA margin bridge FY22->FY25 by cost line and revenue-per-night component", P + "abnb_margin_bridge.csv", "Krish", "derived from D009", "public", "annual", "FY2022", "FY2025", 33, "n/a", "EBITDA margin", "mix",
      "yes: " + NOTE_MRG, "Revenue per night +5.1 pts of margin, S&M took back 4.2; all other cash lines within 0.5 pt", "None", "D009", "no"),
    r("D022", "ABNB vs BKNG vs EXPE annual: growth, take rate, marketing %, SBC %, margins, FCF, buybacks", P + "abnb_vs_bkng_annual.csv", "Krish", "SEC XBRL for 3 CIKs (S31); BKNG press releases for gross bookings", "public", "annual", "FY2021", "FY2025", 15, "~6-8 weeks after FY end (10-K)", "EBITDA margin / take rate (peer context)", "level",
      "yes: " + NOTE_MRG, "BKNG cut share count 18.5% 2022-25 at $1.3B per point with SBC 7% of FCF", "None for prediction; keep for the margin ceiling argument", "D023", "no"),
    r("D023", "Cannibal scorecard: SBC, buybacks, FCF, diluted shares for ABNB, BKNG, EXPE, META, NFLX, UBER, DASH", P + "capital_return_scorecard_annual.csv", "Krish", "SEC XBRL 7 CIKs (S33)", "public", "annual", "FY2021", "FY2025", 42, "~6-8 weeks after FY end", "share count / SBC", "level",
      "yes: " + NOTE_CAP, "ABNB SBC 13.1% of revenue vs META 10.2, DASH 7.7, UBER 3.5, BKNG 2.3", "None", "D013", "no"),
    r("D024", "Cash taxes paid (10-K memo)", P + "abnb_fcf_bridge.csv (cash_taxes_paid_10k)", "Krish", "10-K via XBRL", "public", "annual", "FY2021", "FY2025", 5, "~6-8 weeks after FY end", "FCF", "level",
      "no", "", "Cash tax vs provision gap as a FY27 FCF swing (Pillar 2, NOL exhaustion)", "D012", "no"),

    # ---------------------------------------------------------------- B. Guidance (Theo's dataset + Krish's additions)
    r("D030", "Next-quarter revenue guide (low/high/mid), 20 numeric + 3 qualitative", TG + "guidance_items.csv (metric revenue); " + P + "abnb_revenue_guidance_vs_actual.csv", "Theo (Krish derived)", THEO + " from letters", "public", "quarterly", "2020Q4 event", "2026Q2 event (guides 2026Q3)", 23, "0: letter release", "guidance / revenue", "level / y-y",
      "yes: " + NOTE_BASE + ", " + NOTE_PRED, "Beat midpoint 19/19, top of range 15/19; guide direction does not predict day-1", "Guide width (range as % of mid) as an uncertainty signal for the 20-day drift", "D005,D038,D036", "no"),
    r("D031", "Adj. EBITDA margin guides: next quarter (23) and full year (21), floor/point/ceiling", TG + "guidance_items.csv (metric adj_ebitda_margin, 44 rows added by Krish); " + PREDICT.name + "/data/external/guidance_items_with_margin.csv", "Krish (into Theo's schema)", LETTERS + " Outlook sections", "public", "quarterly", "2020Q4 event", "2026Q2 event", 44, "0: letter release", "guidance / EBITDA margin", "level",
      "yes: " + NOTE_REACT + ", 2026-09-05_guidance-margin-items", "FY floors beaten 4/4 by 1.3-6.3 pts; Q ceilings undershot 8/9 by 0.5-2.5 pts", "FY floor raise (Q3 letters) as a reaction feature: only 3 raises so far, n too small", "D007,D030", "no"),
    r("D032", "KPI direction guides: ADR y/y (14), nights y/y (9), take rate (6), GBV (4), mostly qualitative", TG + "guidance_items.csv", "Theo", THEO, "public", "quarterly", "2020Q4", "2026Q2", 33, "0: letter release", "guidance / ADR / nights / take rate", "direction",
      "partly: " + NOTE_MOV + " (nights guide commentary drives 8-13% drops)", "Four beats-and-falls (3Q22, 1Q23, 2Q24, 2Q25) were nights-guide or lead-time commentary", "Code each print's nights-guide direction (up/flat/down vs current y/y) and test vs day-1 sign, n 23", "D001,D042", "no"),
    r("D033", "Guidance event timestamps (webcast start as public-by proxy; SEC acceptance not captured)", TG + "guidance_events.csv", "Theo", THEO, "public", "per print", "2021-02-25", "2026-08-06", 23, "n/a (defines cutoff)", "guidance (timing)", "metadata",
      "no", "Open issue: use SEC 8-K acceptance time (Theo research_issues)", "Pull EDGAR acceptance times for the 23 8-Ks (accession list in abnb_exsbc_stack.py)", "", "no"),
    r("D034", "Coded management drivers (146 observations, 8 families: booking economics, mix, external, behaviour, demand, calendar, commercial, supply)", TG + "driver_observations.csv; evidence_claims.csv (114)", "Theo", THEO + " from letter Outlook text", "public", "per print", "2020Q4", "2026Q2", 146, "0: letter release", "guidance (rationale)", "sentiment / mix",
      "no", "", "Count of negative-direction drivers per letter vs next-Q revenue beat and day-1 sign (n 23)", "D052,D030", "no"),
    r("D035", "Source excerpts (154 verbatim letter sentences) and 48 source documents manifest", TG + "source_excerpts.csv; " + T + "research/guidance/data/manifests/source_documents.csv", "Theo", THEO, "public", "per print", "2020Q4", "2026Q2", 154, "0", "guidance (provenance)", "metadata",
      "no", "", "None", "", "no"),
    r("D036", "Pre-guidance consensus snapshots (revenue mean)", TG + "consensus_snapshots.csv", "Theo", "Bloomberg BEst point-in-time request pending", "licensed (not collected)", "per print", "", "", "0 of 23 (all rows missing)", "n/a", "consensus", "positioning",
      "no: GAP", "All 23 rows missing; plan-of-attack branch 3 (Hough Hall terminal) not done", "Bloomberg transcript-export page headers give consensus at each call for free; then test guide-vs-consensus gap vs day-1", "D030,D042,D190", "yes"),
    r("D037", "Revenue guide vs actual: midpoint, top, beat %", P + "abnb_revenue_guidance_vs_actual.csv", "Krish", "derived from D030 + D005", "public", "quarterly", "2021Q4", "2026Q3 (actual blank)", 20, "0", "guidance / revenue", "level",
      "yes: " + NOTE_BASE, "Mean beat +2.5% (range +0.9 to +6.8); post-2022 +2.2% sd 1.15", "None; model as a constant", "D030", "no"),
    r("D038", "Trailing-4 guidance cushion and cushion-adjusted guide direction", PP + "01_print_base_rates.csv (trailing_cushion_pct, guide_direction_cushion_adj)", "Krish", "derived", "public", "quarterly", "2020Q4", "2026Q2", 23, "0", "guidance / revenue", "second derivative",
      "yes: " + NOTE_BASE, "Guide + cushion MAE 1.1%; cushion-adjusted guide acceleration does not set day-1", "None", "D030", "no"),

    # ---------------------------------------------------------------- C. Market data and reactions
    r("D040", "ABNB daily close", P + "abnb_daily_close.csv; " + PO + "09_prices_daily.csv (ws 09, 13 tickers)", "Krish", "Yahoo Finance via yfinance", "Yahoo terms (non-redistributable at scale)", "daily", "2020-12-10", "2026-09-04", 1440, "same day", "stock reaction", "positioning",
      "yes: " + NOTE_MOV + ", " + NOTE_BASE, "Prints sold on average: 20-day excess -4.7%; two biggest up days followed runs of down prints", "Pre-print 20-day drawdown as a positioning proxy for day-1 sign (mean reversion), n 23", "D042,D043,D044", "no"),
    r("D041", "Peer and factor daily closes: BKNG, EXPE, HLT, MAR, QQQ (+ DASH, H, JETS, IWM, IVE, IVW, MTUM in ws 09)", PREDICT.name + "/data/raw/prices/*.csv; " + PO + "09_prices_daily.csv", "Krish", "yfinance", "Yahoo terms", "daily", "2020-12-01", "2026-09-04", 1447, "same day", "stock reaction (benchmark)", "positioning / macro",
      "yes: " + NOTE_PEER + " (peer day-1 excess)", "Peer reactions do not read through to ABNB's; hotel prints arrive first, OTAs often after", "Travel-basket beta pre-print vs ABNB idiosyncratic move; factor exposure (growth vs value) before prints", "D040,D060", "no"),
    r("D042", "Earnings reactions: ABNB, QQQ and excess at 1/5/20 sessions for 23 prints", P + "abnb_earnings_reactions.csv; " + TG + "market_returns.csv (69 rows)", "Theo (Krish rebuilt)", "Nasdaq official closes (S28)", "public", "per print", "2021-02-26", "2026-08-07", 23, "n/a (target)", "stock reaction", "target",
      "yes: " + NOTE_REACT + ", " + NOTE_BASE + ", " + NOTE_DRV, "Day-1 excess R^2 0.04-0.07 on print numbers; 1-day > 0 only 11/23", "None as a feature; it is the target", "D001,D009,D031", "no"),
    r("D043", "Major moves >=7%: 41 events attributed (macro/earnings/company/industry) with peer same-day moves", P + "abnb_major_moves_events.csv", "Krish", "derived from closes + press", "public", "event", "2020-12-16", "2026-08-07", 41, "n/a", "stock reaction", "sentiment / attribution",
      "yes: " + NOTE_MOV, "Since 2023 an earnings-day stock; 6 of 11 earnings moves negative despite beats; no mgmt-change move", "None", "D040", "no"),
    r("D044", "Options ledger: ATM IV, straddle, 25d skew, P/C ratios, event-implied move for ABNB + 7 travel names", "MAIN:data/processed/abnb_options_ledger.csv (main tree, uncommitted); script analysis/src/abnb_options_ledger.py", "Krish", "yfinance option chains (adapted from " + XO + "tools/options_ledger.py)", "Yahoo terms", "weekly intended; 1 run so far", "2026-09-05", "2026-09-05", 16, "same day", "stock reaction (implied move)", "positioning",
      "no: 1 capture", "Nov-20 expiry ATM IV 37.9%, straddle 13.4% of spot (single run)", "Implied vs realised print move over the next 2 prints; needs captures the week of 5 Nov", "D040,D042", "yes"),
    r("D045", "Nasdaq ABNB/SPY daily history (Theo's public reproduction)", T + "outputs/reproducibility/us-europe-guidance/nasdaq_public_market_history.csv", "Theo", "Nasdaq historical pages", "public", "daily", "2020-12", "2026-09", 1402, "same day", "stock reaction", "positioning",
      "no (duplicate of D040)", "", "None", "D040", "no"),
    r("D046", "Pitch scorecard: 37 dated calls (direction, PT, KPIs used, method) scored vs ABNB and QQQ; 44 metrics usage", PP + "05_pitch_scorecard.csv; 05_metric_usage.csv", "Krish", "pitch landscape and catalogue notes (S14)", "public web", "event", "2024-09-17", "2026-09-03", 37, "n/a", "stock reaction / positioning", "sentiment",
      "yes: " + NOTE_PITCH, "Longs right 17/18 but beat QQQ 11/18; all 7 holds wrong; take-rate bulls wrong on KPI unpunished", "Sell-side PT dispersion at each print as a crowding proxy (needs consensus history D190)", "D036,D190", "no"),

    # ---------------------------------------------------------------- D. Transcripts and text
    r("D050", "Earnings-call transcripts, 23 calls (IR FactSet PDFs 4Q21, 1Q23-2Q26; stockanalysis.com 4Q20-4Q22)", R + "regulatory/transcripts/ (14 PDF+JSON); citadel-abnb-transcripts/data/raw/transcripts/ir + sa (23 txt); " + T + "research/transcripts/transcript_index.csv", "Krish; Theo", "Airbnb IR CDN (S22/S35); stockanalysis.com", "IR PDFs public; FactSet copies licensed", "per print", "2021-02-25", "2026-08-06", 23, "0 to 1 day after call (corrected PDF ~1-2 days)", "guidance / sentiment", "sentiment",
      "yes: " + NOTE_TR, "Mgmt talks volume and margin; analysts ask take rate, marketing, hotels, regulation", "Prepared-remarks tone score per call vs next-Q guide direction (n 23), LLM-coded and pre-registered", "D051,D052,D053", "no"),
    r("D051", "Analyst roster per call: 317 analyst-call rows; firm churn by call; 31 firms", P + "abnb_call_roster.csv; abnb_call_roster_churn.csv", "Krish", "transcripts (D050)", "public", "per print", "2020Q4", "2026Q2", 317, "0-1 day", "positioning (coverage)", "positioning",
      "yes: " + NOTE_TR, "Analysts asking per call 15.0 (2022) to 11.5 (2026); no new house since 2024", "Roster size change vs 20-day post-print drift (attention proxy), n 22", "D046", "no"),
    r("D052", "Call topic mentions per 1,000 words, 14 topics x 23 calls, split mgmt prepared / mgmt Q&A / analysts", P + "abnb_call_topics.csv", "Krish", "transcripts, regex TOPICS dict", "public", "per print", "2020Q4", "2026Q2", 322, "0-1 day", "guidance / sentiment / take rate / regulation", "sentiment",
      "yes: " + NOTE_TR + " (descriptive only)", "Take rate absent from prepared remarks until 2025; AI now volunteered; regulation asked 4.9x more than volunteered", "Analyst-minus-management topic gap (e.g. take rate) vs next-print reaction; nights_demand mentions vs nights guide", "D034,D050", "no"),
    r("D053", "Declined-to-quantify log: 37 analyst asks management would not number", P + "abnb_declined_to_quantify.csv", "Krish", "transcripts, hand-read", "public", "per print", "2020Q4", "2026Q2", 37, "0-1 day", "guidance (what is unknowable)", "sentiment",
      "yes: " + NOTE_TR, "Four never numbered: Experiences attach, hotels scale, AI spend, long-term margin", "Declines per call vs day-1 sign (opacity penalty), n 23", "D052", "no"),
    r("D054", "Regulatory earnings observations (9 coded call statements, 2023Q3-2026Q2)", REG + "earnings_observations.json; earnings_digest.md", "Krish", "transcripts", "public", "per print", "2023-Q3", "2026-Q2", 9, "0-1 day", "regulation", "sentiment",
      "no", "", "None (too few)", "D160", "no"),
    r("D055", "Third Bridge expert calls, 5 transcripts (Booking AI, OTA AI, India alt-acco, UK/EU VRM, US VRM)", R + "licensed/third-bridge/*.pdf; digest 2026-09-05_third-bridge-transcripts.md", "Krish", "Third Bridge (S16-S20)", "licensed, do not quote at length", "one-off", "2026-05-26", "2026-08-19", 5, "n/a", "take rate / supply-side / regulation", "sentiment / supply-side",
      "yes: digest", "Supplier power sits with property managers; Awaze pays 15-17%; AI-native share ~3%", "None quantitative", "", "no"),
    r("D056", "LSEG/Refinitiv headlines: 59 regulatory news, 88 Spain, 6 transcript entries, 18 story bodies", R + "regulatory/lseg/*.json,*.html; " + R + "regulatory/phase2/lseg/", "Krish", "LSEG Workspace news (Reuters)", "licensed (LSEG terms)", "event", "2025-07-30", "2026-09-04", 153, "same day", "regulation", "sentiment / event dating",
      "no", "Used for event dating only (regulatory note ledger)", "Monthly count of STR-regulation headlines as a regulatory-pressure index; needs a longer pull", "D160,D161", "yes"),
    r("D057", "Theo transcript fact tables (guidance_facts, reported_metrics, management_themes)", T + "research/transcripts/*.csv", "Theo", "planned extraction from FactSet PDFs", "n/a", "per print", "", "", "0 (empty schemas)", "n/a", "guidance / nights / ADR", "n/a",
      "no: schemas only", "Never populated", "Populate reported_metrics from the letters instead (D001-D007 already do)", "", "no"),

    # ---------------------------------------------------------------- E. Peer prints
    r("D060", "Peer print KPIs: BKNG room nights/GB/revenue, EXPE room nights/GB, MAR and HLT RevPAR, adj. EBITDA margins, next-Q direction; 256 source sentences", PP + "02_peer_prints.csv; 02_peer_prints_long.csv; 02_peer_sources.csv", "Krish", "8-K Ex.99.1 via EDGAR submissions API (S37)", "public", "quarterly", "2020Q4", "2026Q2", 92, "0: peer 8-K (HLT ~21 Oct, MAR ~3 Nov, BKNG/EXPE often after ABNB)", "nights (read-through) / stock reaction", "demand-side / level",
      "yes: " + NOTE_PEER, "HLT/MAR RevPAR r 0.88/0.91 with nights but no LOO gain over ABNB's own AR(1) (10 of 11 worse)", "MAR/HLT RevPAR acceleration as a sign check only; test BKNG Q4 room-nights guide vs ABNB Q4 guide direction", "D001,D041", "no"),
    r("D061", "Peer 8-K exhibits raw, 93 filings (BKNG 23, EXPE 23, HLT 24, MAR 23)", PREDICT.name + "/data/raw/peers/ (BKNG, EXPE, HLT, MAR subfolders of *.htm); peer_filings_manifest.csv", "Krish", "EDGAR", "public", "quarterly", "2021-02-11", "2026-08-05", 93, "0", "nights / ADR (peer)", "raw",
      "yes (parsed into D060)", "", "Parse BKNG's ADR and EXPE's lodging ADR growth for a peer price index", "D060,D003", "no"),
    r("D062", "Peer print calendar: report dates, acceptance times, lead days vs ABNB", PP + "02_peer_readthrough_panel.csv (*_lead_days)", "Krish", "EDGAR acceptance timestamps", "public", "quarterly", "2021Q1", "2026Q2", 22, "n/a", "guidance (timing)", "metadata",
      "yes: " + NOTE_PEER, "Calendar blocks half the pairs; BKNG/EXPE usually report after ABNB", "None", "D060", "no"),

    # ---------------------------------------------------------------- F. Macro: FRED
    r("D070", "CPI lodging away from home, SA (CUSR0000SEHB)", R + "fred/CUSR0000SEHB.csv; " + PREDICT.name + "/data/raw/macro/", "Krish", FRED, "public domain", "monthly", "1997-12", "2026-07", 344, "~2 weeks after month end (CPI release); Oct-2025 missing", "ADR / nights", "price / macro",
      "yes: " + NOTE_PRED + ", " + NOTE_MRG, "Nights r 0.80 post-2022 is trend; hotel price monitor: CPI lodging +2.8% Jul-26 after +4.4 to +5.0", "CPI lodging minus ADR ex-FX (hotel-STR price wedge) vs next-Q ADR ex-FX, n 14", "D003,D004,D090,D165", "no"),
    r("D071", "CPI lodging away from home, NSA (CUUR0000SEHB)", PREDICT.name + "/data/raw/macro/CUUR0000SEHB.csv; Theo SSD", "Krish; Theo", FRED, "public domain", "monthly", "1997-12", "2026-07", 344, "~2 weeks", "ADR", "price",
      "yes: " + NOTE_PRED + "; Theo H-003 v1/v2", "Theo H-003: not testable (no ALFRED vintage access); Krish: same as SA", "ALFRED vintages once a FRED key is synced (Theo's blocker)", "D070", "no"),
    r("D072", "CPI airline fares (CUSR0000SETG01)", R + "fred/CUSR0000SETG01.csv", "Krish", FRED, "public domain", "monthly", "1989", "2026-07", 450, "~2 weeks", "ADR ex-FX / nights", "price / macro",
      "yes: " + NOTE_PRED, "Runner-up for ADR ex-FX after initial claims; not promoted", "Airfare y/y + claims y/y two-factor ADR ex-FX model, walk-forward from 2023", "D078,D004", "no"),
    r("D073", "CPI all items (CPIAUCSL)", R + "fred/CPIAUCSL.csv", "Krish", FRED, "public domain", "monthly", "1947", "2026-07", 955, "~2 weeks", "nights (control) / real ADR", "macro",
      "yes: " + NOTE_PRED, "'Predicts' nights r 0.85 as well as BEA: disinflation trend, not travel", "Use only as deflator", "D070", "no"),
    r("D074", "CPI new vehicles (CUSR0000SETA01), discretionary control", PREDICT.name + "/data/raw/macro/CUSR0000SETA01.csv", "Krish", FRED, "public domain", "monthly", "1953-01", "2026-07", 883, "~2 weeks", "nights (control)", "macro",
      "yes: " + NOTE_PRED + " (one of 25 series)", "No surviving pair", "None", "", "no"),
    r("D075", "UMich consumer sentiment (UMCSENT)", PREDICT.name + "/data/raw/macro/UMCSENT.csv; " + XO + "data/", "Krish", FRED, "public domain", "monthly (prelim mid-month)", "1952-11", "2026-07", 885, "prelim ~2 weeks before month end", "nights / GBV", "demand-side / macro",
      "yes: " + NOTE_PRED, "No surviving pair on any target post-2022", "None", "", "no"),
    r("D076", "Personal saving rate (PSAVERT)", PREDICT.name + "/data/raw/macro/PSAVERT.csv", "Krish", FRED, "public domain", "monthly", "1959-01", "2026-07", 811, "~4 weeks", "stock reaction / GBV", "macro",
      "yes: " + NOTE_PRED, "Day-1 excess r -0.70 post-2022 but +0.03 full sample: sign flip, spurious", "None", "", "no"),
    r("D077", "Retail sales ex auto (RSXFS)", PREDICT.name + "/data/raw/macro/RSXFS.csv", "Krish", FRED, "public domain", "monthly", "1992-01", "2026-07", 415, "~2 weeks", "revenue beat / nights accel", "macro",
      "yes: " + NOTE_PRED, "Beat vs midpoint r -0.55 (q 0.33): nothing; accel r 0.64 (q 0.21) not a lead", "None", "", "no"),
    r("D078", "Initial jobless claims (ICSA), weekly", PREDICT.name + "/data/raw/macro/ICSA.csv", "Krish", FRED, "public domain", "weekly", "1967-01-07", "2026-08-29", 3113, "5 days (Thursday release)", "ADR ex-FX", "macro / price",
      "yes: " + NOTE_PRED, "ADR ex-FX r -0.86 (n 17), -0.78 post-2022, LOO 0.82 vs 1.05 naive: WATCH, not promoted", "Score against 3Q26 and 4Q26 ex-FX ADR before promoting; pre-register direction (rising claims, weaker pricing)", "D004,D072", "no"),
    r("D079", "Unemployment rate (UNRATE)", PREDICT.name + "/data/raw/macro/UNRATE.csv", "Krish", FRED, "public domain", "monthly", "1948-01", "2026-08", 944, "first Friday", "nights", "macro",
      "yes: " + NOTE_PRED, "No surviving pair", "None", "", "no"),
    r("D080", "Leisure and hospitality employment (USLAH)", PREDICT.name + "/data/raw/macro/USLAH.csv; Theo SSD", "Krish; Theo", FRED, "public domain", "monthly", "1939-01", "2026-08", 1052, "first Friday", "nights", "demand-side / macro",
      "yes: " + NOTE_PRED, "r 0.82 post-2022 is trend; 0.14 from 2024", "None", "", "no"),
    r("D081", "Real PCE (PCEC96)", PREDICT.name + "/data/raw/macro/PCEC96.csv; Theo SSD", "Krish; Theo", FRED, "public domain", "monthly", "2007-01", "2026-07", 235, "~4 weeks", "GBV", "macro",
      "yes: " + NOTE_PRED, "GBV y/y r -0.84 post-2022 lag 1 but +0.13 full sample: spurious", "None", "", "no"),
    r("D082", "Real disposable income (DSPIC96)", PREDICT.name + "/data/raw/macro/DSPIC96.csv; Theo SSD", "Krish; Theo", FRED, "public domain", "monthly", "1959-01", "2026-07", 811, "~4 weeks", "GBV / nights", "macro",
      "yes: " + NOTE_PRED, "No surviving pair", "None", "", "no"),
    r("D083", "PCE services (PCES)", PREDICT.name + "/data/raw/macro/PCES.csv", "Krish", FRED, "public domain", "monthly", "1959-01", "2026-07", 811, "~4 weeks", "nights / GBV", "macro",
      "yes: " + NOTE_PRED, "No surviving pair", "None", "", "no"),
    r("D084", "PCE durable goods (PCEDG)", PREDICT.name + "/data/raw/macro/PCEDG.csv; " + XO + "data/", "Krish", FRED, "public domain", "monthly", "1959-01", "2026-07", 811, "~4 weeks", "stock reaction (goods vs services rotation)", "macro",
      "yes: " + NOTE_PRED, "Best full-sample |r| on day-1 (0.41, lag 1); no perm p < 0.05", "None", "", "no"),
    r("D085", "Air revenue passenger miles (AIRRPMTSID11)", PREDICT.name + "/data/raw/macro/AIRRPMTSID11.csv; Theo SSD", "Krish; Theo", FRED + " (from BTS)", "public domain", "monthly", "2000-01", "2026-05", 317, "~3 months (BTS): NOT knowable before print", "nights", "demand-side",
      "yes: " + NOTE_PRED, "r 0.84 post-2022 but not in hand at print; trend", "Replace with TSA daily throughput (D102) captured by browser if the 403 stands", "D102", "no"),
    r("D086", "Vehicle miles travelled (TRFVOLUSM227NFWA)", PREDICT.name + "/data/raw/macro/TRFVOLUSM227NFWA.csv; Theo SSD", "Krish; Theo", FRED + " (from FHWA)", "public domain", "monthly", "1970-01", "2026-07", 679, "~6-8 weeks", "nights (domestic drive-to)", "demand-side",
      "yes: " + NOTE_PRED + "; Theo H-008 (FHWA direct: robots-blocked)", "No surviving pair; Theo: inconclusive/blocked", "None", "", "no"),
    r("D087", "Trade-weighted broad USD (DTWEXBGS), daily", PREDICT.name + "/data/raw/macro/DTWEXBGS.csv; " + PO + "10_fx_daily.csv (ws 10); Theo H.10 archive", "Krish; Theo", FRED + " / Fed H.10 (S38)", "public domain", "daily (H.10 weekly release)", "2006-01-02", "2026-08-28", 5390, "1 business day (H.10 Monday)", "ADR (FX effect) / revenue FX pts", "price / macro",
      "yes: " + NOTE_PRED + "; Theo H-001", "FX effect on ADR r -0.95 (n 14), LOO 0.76 vs 2.11 pp: the one mechanical forecast; Theo H-001 9/16 hits, no edge", "Weekly FX-to-ADR tracker for the 5 Nov card (3Q26 FX lift ~+0.8 pt vs +1.3 in 2Q26)", "D088,D004,D018", "no"),
    r("D088", "EUR/USD (DEXUSEU), daily", PREDICT.name + "/data/raw/macro/DEXUSEU.csv; " + PO + "10_fx_daily.csv (9 currencies, ws 10)", "Krish", FRED, "public domain", "daily", "1999-01-04", "2026-08-28", 7215, "1 business day", "ADR (FX effect) / EMEA revenue", "price / macro",
      "yes: " + NOTE_PRED + "; Theo H-002 (ECB: zero strict-PIT)", "FX effect r +0.97 post-2022 (+0.99 full), LOO 0.57 pp vs 2.11 naive", "Currency-weighted FX basket from the 10-K host-country mix (ws 10 builds 9 currencies)", "D087,D018", "no"),
    r("D089", "BEA PCE accommodations: nominal SAAR, real, price index", R + "bea/bea_pce_travel_monthly_2015_2026.csv; " + P + "abnb_kpi_vs_category_quarterly.csv", "Krish", BEA, "public domain", "monthly", "2015-01", "2026-07", 139, "month 3 of quarter ~1 week before print; revised vintage in hand", "nights / ADR (US category)", "demand-side / price",
      "yes: " + NOTE_PRED + "; ABNB-Crossover share test", "Nights r 0.87 post-2022 is 2023 trend, 0.22 from 2024; real accommodations only +1.8% Jul-26", "Log first-print month-3 values each release (point-in-time) and re-test the share gap as a coincident check only", "D090,D073,D097", "no"),
    r("D090", "BEA PCE hotels and motels: nominal, real, price", R + "bea/bea_pce_travel_monthly_2015_2026.csv; " + P + "hotel_price_monitor_monthly.csv", "Krish", BEA, "public domain", "monthly", "2015-01", "2026-07", 139, "as D089", "nights / ADR", "demand-side / price",
      "yes: " + NOTE_PRED + ", " + NOTE_MRG, "Nights r 0.88 post-2022, 0.28 from 2024: trend; hotel price index used in the hotel monitor", "Hotel price index vs ADR ex-FX one quarter ahead (hotel pricing leads STR pricing?), n 14", "D070,D004", "no"),
    r("D091", "BEA PCE air transportation: nominal, real, price", R + "bea/bea_pce_travel_monthly_2015_2026.csv", "Krish", BEA, "public domain", "monthly", "2015-01", "2026-07", 139, "as D089", "nights", "demand-side",
      "partly: " + NOTE_PRED + " (via CPI airfare); Crossover", "Air +21% nominal Jul-26 is +17% price; real air ~+4%", "Real air PCE y/y vs nights y/y post-2024 only (n 10)", "D072,D085", "no"),
    r("D092", "BEA foreign travel in the US (inbound)", R + "bea/bea_pce_travel_monthly_2015_2026.csv", "Krish", BEA, "public domain", "monthly", "2015-01", "2026-07", 139, "as D089", "nights (inbound US)", "demand-side / cross-border",
      "yes: " + NOTE_PRED, "Level r 0.83 trend; diff1 lag1 r -0.86 with Spearman 0.30: spurious", "Inbound y/y vs NA-region revenue y/y (D018) rather than global nights", "D018,D093", "no"),
    r("D093", "BEA foreign travel by US residents (outbound)", R + "bea/bea_pce_travel_monthly_2015_2026.csv", "Krish", BEA, "public domain", "monthly", "2015-01", "2026-07", 139, "as D089", "nights (cross-border mix)", "demand-side / cross-border",
      "yes: " + NOTE_PRED, "r 0.83 post-2022: trend; outbound negative y/y all 2026", "Outbound y/y vs EMEA+LatAm+APAC revenue y/y (US guests abroad), n 11", "D018,D092", "no"),
    r("D094", "BEA package tours, motor vehicle rental, food services, recreation services, services total", XO + "data/bea_pce_travel_monthly_2015_2026.csv (extra series in the Crossover extract)", "Krish (prior project)", BEA, "public domain", "monthly", "2015-01", "2026-07", 4170, "as D089", "nights (travel wallet)", "demand-side",
      "no", "", "Travel-wallet share (accommodations / services total) as a mean-reverting demand index", "D089,D091", "no"),
    r("D095", "Crossover FRED extras: PCEPI, ECOMSA, ECOMPCTSA (+UMCSENT, PSAVERT, PCEDG, RSXFS, CPIAUCSL copies)", XO + "data/fred_*.csv", "Krish (prior project)", FRED, "public domain", "monthly", "various", "2026-07", 8, "~2-4 weeks", "deflators / not relevant", "macro",
      "no", "E-commerce share flagged 'probably not needed'", "None", "", "no"),
    r("D096", "Hotel price monitor: CPI lodging y/y, BEA hotel price y/y, ABNB ADR y/y (reported, letter, ex-FX)", P + "hotel_price_monitor_monthly.csv", "Krish", "derived D070+D090+D003/D004", "public", "monthly", "2023-01", "2026-07", 43, "~2 weeks", "ADR", "price",
      "yes: " + NOTE_MRG + " 3.4", "Hotels caught up with ABNB ADR in 2Q26; CPI lodging re-accelerated then cooled to +2.8% Jul", "The hotel-minus-ABNB price wedge as a margin (revenue per night) driver in the FY27 scenarios", "D070,D090,D003", "no"),
    r("D097", "Nights-minus-category share gap (nights y/y minus BEA real accommodations y/y)", P + "abnb_kpi_vs_category_quarterly.csv (share_gap_nights_vs_bea_real_pct)", "Krish", "derived", "public", "quarterly", "2021Q1", "2026Q2", 22, "0", "nights", "second derivative",
      "yes: " + NOTE_PRED, "Circular as a nowcast; not a lead", "None", "D089", "no"),
    r("D098", "Theo FRED cohort (10 series: SEHB SA/NSA, USLAH, UMCSENT, PCEC96, DSPIC96, SETA01, AIRRPM, VMT, DTWEXBGS)", SSD + "macro_download_log.csv (JSON, 11,516 obs)", "Theo", FRED, "public domain", "monthly/daily", "various", "2026-08", 11516, "as above", "nights / ADR", "macro",
      "duplicate of D070-D087", "", "None", "", "no"),
    r("D099", "Fed H.10 dated weekly release archive -> 23 strict point-in-time broad-dollar features", T + "research/readiness/20260903T053309Z_abnb_readiness/ (results); source FED_H10_ARCHIVE", "Theo", "federalreserve.gov H.10 release pages (62 dated)", "public domain", "weekly", "2021", "2026-08", 23, "strict PIT verified (release timestamp before cutoff)", "guidance (revenue guide midpoint)", "macro / price",
      "yes: Theo H-001 (predictive/01 sec 2.3)", "9 hits, 7 misses on 16 comparable events; 75% early cohort to 50% late: no edge", "Walk-forward MAE vs seasonal baseline in 8 folds (plan-of-attack branch 10, optional)", "D087", "no"),
    r("D100", "ECB EUR/USD reference rate (H-002)", "Theo ECB_EXR_USD_EUR source; not held as a file in repo", "Theo", "ECB Data Portal", "public", "daily", "", "", "n/a", "no verified initial-publication timestamp", "guidance", "macro",
      "yes: Theo H-002", "Zero strict-PIT eligible; 16:00 UTC sensitivity 10 hits/6 misses: not evidence", "None; D088 covers it", "D088", "no"),
    r("D101", "TSA checkpoint throughput, daily", "not held (403 to non-browser clients; Theo manifest row)", "none", "tsa.gov/travel/passenger-volumes", "public domain", "daily", "2019", "", 0, "1 day", "nights (US air demand)", "demand-side",
      "no: not acquired", "Theo: 403, used FRED AIRRPM instead (3-month lag)", "Visible-browser download once, then daily append; the only daily US demand series with 2019 base", "D085,D091", "yes"),

    # ---------------------------------------------------------------- G. Eurostat and European platform data
    r("D110", "Eurostat tour_ce_omr EU27 platform nights (Airbnb+Booking+Expedia+TripAdvisor), domestic/foreign split, 31 countries monthly", P + "eurostat_platform_nights_monthly.csv; " + R + "eurostat/; " + PO + "10_eurostat_platform_monthly_latest.csv (ws 10)", "Krish (re-pull of Theo cohort)", EUS, "Eurostat re-use with attribution", "monthly", "2018-01", "2026-03", 99, "~3-5 months (Jun/Jul 2026 not yet published at 5 Sep)", "regional nights (EMEA) / nights", "demand-side / level / y-y",
      "yes: " + NOTE_EU + "; Theo H-012 (diagnostic only)", "EU27 +11.4% 2025, +9.7% Q1 26; ABNB EMEA grows with the category, not faster", "Trailing-3-month EU27 y/y (with 4-month lag) vs EMEA revenue y/y walk-forward from 2023; only 2 of 4 quarter-months are in hand at the print", "D018,D111,D088", "no"),
    r("D111", "Eurostat platform nights by country: annual 2019/2023/2024/2025, growth, Q1 2026 y/y, EU share", P + "eurostat_platform_nights_by_country.csv", "Krish", EUS, "Eurostat re-use", "annual + Q1 2026", "2019", "2026Q1", 32, "~3-5 months", "regional nights / regulation", "supply-side / regional",
      "yes: " + NOTE_EU, "Regulated markets (ES, PT, NL, AT) grow slowest: Spain +6.5% Q1 26 vs Germany +14.9%", "Country growth vs regulatory factor tier as the cross-section for the regulatory loss model", "D160,D161,D164", "no"),
    r("D112", "EU27 platform nights y/y vs ABNB EMEA revenue y/y and global nights y/y, quarterly", P + "eurostat_platform_nights_quarterly.csv", "Krish", "derived D110 + D018", "public", "quarterly", "1Q18", "2Q26", 33, "~3-5 months", "regional nights", "y-y",
      "yes: " + NOTE_EU, "EMEA minus platform: -2.4 pts avg 4Q23-2Q25, +8.6 3Q25-1Q26 (euro)", "Deflate EMEA revenue by EUR/USD before the comparison", "D110,D088", "no"),
    r("D113", "Eurostat tour_ce_* full set: 8 datasets (oam, oan3, oar, oarc, oasc, oaw, omn12, omr): stays, guests by residence, NUTS 1/2/3 and cities", SSD + "expansion_file_inventory.csv (7.1 MB JSON-stat, 485,144 values)", "Theo", "Eurostat dissemination API", "Eurostat re-use", "monthly / annual", "2018", "2026", 485144, "~3-5 months", "regional nights / regulation (city level)", "supply-side / regional",
      "no", "", "City/NUTS3 platform nights for Barcelona, Paris, Amsterdam, Lisbon, Athens pre/post rule dates: the regulatory diff-in-diff nobody has run", "D111,D160,D162", "no"),
    r("D114", "Theo 50-source expansion: 41 extra Eurostat products (total tourism nights, capacity, hotel occupancy, flights, air passengers, airport pairs)", TE + "20260903T211121Z_50_source_expansion/ (source_manifest_50.csv; 590,949 obs off-repo, over 50 MiB)", "Theo", "Eurostat", "Eurostat re-use", "monthly/quarterly/annual", "various", "2026", 590949, "~2-5 months; current snapshot only", "regional nights (Europe)", "demand-side / macro",
      "no", "Theo: breadth, not edge; nested and correlated", "Eurostat monthly air passengers by country vs EMEA revenue y/y as a second European demand series", "D110", "no"),
    r("D115", "Theo broad scrape: UK CAA airport passengers, Toronto, DataSF SFO, StatCan, Eurostat regional", TE + "20260903T204950Z_broad_scrape/processed/valid_observations.csv", "Theo", "official open-data portals", "open (various)", "monthly", "various", "2026-08", None, "1-3 months", "nights (regional demand)", "demand-side",
      "no", "Theo: operating-data sample, not an earnings-event sample", "Fold into a North-America airport index with SFO/LAX (D211)", "D211", "no"),

    # ---------------------------------------------------------------- H. Inside Airbnb: Krish's historical 13-city panel
    r("D120", "Inside Airbnb listings dumps, 13 cities, 168 dumps (raw .csv.gz + parquet)", R + "inside_airbnb/ (2.7 GB, gitignored); manifest.csv (279 URLs, 111 return 403)", "Krish", IA + " CDN + Wayback discovery", "CC BY 4.0 (attribute)", "quarterly to Dec 2025, monthly since", "2022-12-13 (Rome)", "2026-08-30", 168, "dump published ~1-4 weeks after scrape date", "supply (listings) / ADR (asking price) / regulation", "supply-side / raw",
      "yes (via D121-D131)", "Three breaks: price basis (2026 fee-inclusive quote), no-price months, partial-scope monthlies", "Fixed-panel monthly capture going forward; request NYC pre-LL18 dumps from Inside Airbnb", "D121,D140", "yes"),
    r("D121", "City snapshot metrics per dump: listings, entire-home share, active/reviewed-LTM listings, reviews LTM and L30d sums, superhost, multi-listing, licensed, min-nights, availability, instant book", P + "inside_airbnb_city_snapshots.csv; " + PO + "08_ia_dump_metrics.csv (ws 08)", "Krish", IA, "CC BY 4.0", "per dump (13 cities)", "2022-12-13", "2026-08-30", 168, "~1-4 weeks after scrape", "nights (proxy: reviews) / supply", "supply-side / level",
      "yes: " + NOTE_IA + ", " + NOTE_PRED + " 03 alt data", "reviews_ltm y/y vs nights y/y r +0.30 (n 11); city mix changes each quarter", "Fixed 13-city reviews_l30d y/y (ws 08 builds it) vs nights y/y once 8+ same-city quarters exist", "D124,D125,D001", "yes"),
    r("D122", "Like-for-like (same listing, year-ago) listed nightly price change, entire homes", P + "inside_airbnb_like_for_like.csv (lfl_price_chg_median); " + PP + "03_altdata_quarterly.csv", "Krish", IA, "CC BY 4.0", "per year-ago pair", "2023-12", "2025-09 (price basis ends)", 258, "~1-4 weeks", "ADR", "price",
      "yes: " + NOTE_PRED + " 03", "r +0.07 vs ADR y/y (n 8, Rome-only early); series discontinued by the 2026 price-basis change", "Restart on the 2026 quote basis (D130) after 4 same-basis quarters; compare to ADR ex-FX not reported ADR", "D130,D003", "yes"),
    r("D123", "Listing retention (year-ago and sequential), gross adds, exits, exit/add mix by reviewed, entire-home, multi-listing", P + "inside_airbnb_like_for_like.csv (retention, exits, gross_adds, *_share)", "Krish", IA, "CC BY 4.0", "per pair", "2022-12", "2026-08", 258, "~1-4 weeks", "supply (churn) / regulation", "supply-side",
      "yes: " + NOTE_IA + " (descriptive)", "20-30% of listings gone a year later; NYC/Barcelona/LA lowest retention", "City retention y/y vs Eurostat country nights (D111) and vs regulatory events (D160): does churn lead category growth", "D111,D160,D151", "no"),
    r("D124", "Matched-listing reviews LTM change (survivors only)", P + "inside_airbnb_like_for_like.csv (matched_reviews_ltm_chg); " + PO + "08_ia_city_yoy.csv", "Krish", IA, "CC BY 4.0", "per pair", "2023-12", "2026-08", 258, "~1-4 weeks", "nights", "demand-side",
      "yes: " + NOTE_PRED + " 03", "r +0.20 with nights y/y (n 11); -0.55 with acceleration (wrong sign, Rome-driven)", "Weight cities by est_nights_ltm and drop partial-scope dumps; ws 08 is doing this", "D121,D125", "yes"),
    r("D125", "Reviews in last 30 days, sum per city per dump", P + "inside_airbnb_city_snapshots.csv (reviews_l30d_sum); " + PO + "08_ia_dump_metrics.csv", "Krish", IA, "CC BY 4.0", "per dump (monthly since Dec 2025)", "2022-12", "2026-08", 168, "~1-4 weeks", "nights (monthly demand proxy)", "demand-side / nowcast",
      "partly: ws 08 in flight", "Monthly cadence only since Dec 2025, so 9 same-city months", "13-city reviews_l30d y/y as the monthly nights nowcast; first test possible at the 4Q26 print", "D121,D142", "yes"),
    r("D126", "Multi-listing host share, professional (5+) share, hosts, top-10/top-100 host share", P + "inside_airbnb_city_snapshots.csv", "Krish", IA, "CC BY 4.0", "per dump", "2022-12", "2026-08", 168, "~1-4 weeks", "supply mix / take rate (host power) / regulation", "supply-side / mix",
      "yes: " + NOTE_IA + " (descriptive)", "55-81% of listings on multi-listing hosts; rose y/y in all 13 cities", "Professional share vs host-fee pilot markets; professional share as a take-rate ceiling proxy in the model", "D128,D055", "no"),
    r("D127", "Superhost share, licensed share, instant-book share, short-min-nights share, median rating, host tenure", P + "inside_airbnb_city_snapshots.csv", "Krish", IA, "CC BY 4.0", "per dump", "2022-12", "2026-08", 168, "~1-4 weeks", "supply quality / regulation", "supply-side / mix",
      "yes: " + NOTE_IA, "NYC: 81% of listings need 30+ nights post-LL18; Paris/Rome 80-86% carry registration numbers", "Licensed-share step changes as the enforcement date detector for the regulatory events table", "D160,D162", "no"),
    r("D128", "Host concentration: top-25 hosts per city (listings, entire-home, reviews LTM, share of city)", P + "inside_airbnb_host_concentration.csv", "Krish", IA, "CC BY 4.0", "one snapshot per city", "2026-08-10", "2026-08-30", 325, "~1-4 weeks", "supply mix / take rate", "supply-side",
      "yes: " + NOTE_IA, "908-listing corporate hosts dominate what is left in NYC", "None until a second snapshot", "D126", "yes"),
    r("D129", "Inside Airbnb estimated nights LTM and estimated revenue L365d (their occupancy model), exposed nights (short entire homes)", P + "inside_airbnb_city_snapshots.csv (est_nights_ltm, est_revenue_l365d, exposed_nights_short_entire)", "Krish", IA + " (Inside Airbnb's own model)", "CC BY 4.0", "per dump", "2022-12", "2026-08", 168, "~1-4 weeks", "nights / GBV (city) / regulation exposure", "demand-side / supply-side",
      "partly: " + NOTE_REG + " (city GBV shares as weights)", "Used as weights in the regulatory profile, not as a series", "est_revenue y/y per city vs Eurostat country nights: calibrate the review-to-nights multiplier", "D161,D121", "no"),
    r("D130", "2026 quote-basis price: median quote total for entire homes, quote stay nights, lead days, median_price_entire on the new basis", P + "inside_airbnb_city_snapshots.csv (price_basis=quote_per_night, quote_* cols)", "Krish", IA, "CC BY 4.0", "monthly", "2026-01", "2026-08", 78, "~1-4 weeks", "ADR (fee-inclusive stay quote)", "price",
      "no: too short", "New basis from 2026; not comparable to listed_nightly", "From Jan 2027 a same-basis y/y exists; the 2026 quote is closer to what guests pay (fees in) than the old listed price", "D122,D003", "yes"),
    r("D131", "Availability 365 / 90 (calendar) and blocked_30/blocked_90 per dump", P + "inside_airbnb_city_snapshots.csv (median_availability_365, mean_availability_90); " + PO + "08_ia_dump_metrics.csv (blocked_30/90)", "Krish", IA, "CC BY 4.0", "per dump", "2022-12", "2026-08", 168, "~1-4 weeks", "nights (forward, bounded proxy)", "demand-side / booking curve",
      "partly: ws 08 in flight (blocked_30_yoy_pts)", "Blocked conflates booked, host-blocked, inactive; never call it occupancy", "Same-city blocked_30 y/y pts vs next-Q nights y/y once 8 pairs exist", "D141,D165", "yes"),

    # ---------------------------------------------------------------- I. Theo's Inside Airbnb current cohort (off-machine)
    r("D140", "Inside Airbnb current listings, 120 markets / 35 countries incl. all 34 US (982,188 listing rows) -> market summary", SSD + "inside_airbnb_download_log.csv; summary in " + P + "market_summary_2026.csv", "Theo", IA, "CC BY 4.0", "one snapshot per market", "2026-06-14", "2026-08-10", 120, "~1-4 weeks", "supply / regulation / ADR (asking, native currency)", "supply-side / cross-section",
      "yes: " + NOTE_PRED + " 03 (booking-curve ranking only)", "One-date cross-section; hemisphere seasonality dominates any ranking", "Cross-section: licence-disclosed share and multi-host share vs Eurostat country growth (D111)", "D121,D111", "yes"),
    r("D141", "Forward booking curves: blocked-night rate by horizon bucket (0-30/31-60/61-90/91-180/181-372) and daily days-ahead, 120 markets", P + "booking_curves_by_market.csv (600); booking_curve_daily.csv (44,379); source 588M calendar rows on SSD (5 columns, NO price)", "Theo", IA + " calendar.csv.gz", "CC BY 4.0", "one snapshot per market", "2026-06-14", "2026-08-10", 600, "~1-4 weeks", "nights (forward bookings, bounded proxy) / RNPL lead-time claim", "demand-side / booking curve",
      "yes: " + NOTE_PRED + " 03 (descriptive)", "Seasonality ranking until a second vintage exists (Copenhagen 0.85 at 31-60 days)", "T6.2 in CODEX handoff: far-minus-near horizon y/y shift as the RNPL lead-time test; needs 2025 vintages (83% live on CDN)", "D131,D165", "yes"),
    r("D142", "Inside Airbnb reviews files, 120 markets, 67.5M review rows with review dates", SSD + " (reviews.csv.gz per market; 91 files in inside_airbnb_download_log.csv)", "Theo", IA + " reviews.csv.gz", "CC BY 4.0", "one dump, but each review is dated (2010-2026)", "~2010", "2026-08", 67500188, "~1-4 weeks after dump; history embedded", "nights (monthly review flow by market, years of history)", "demand-side / nowcast",
      "no: NOT TESTED by anyone", "The largest untested asset: dated reviews give a monthly market-level demand series back to 2010s from a single dump", "Build monthly review counts per market 2018-2026 (survivor-biased), sum by region, test vs quarterly nights y/y 2021-2026 (n 22) with the bias modelled from D123 churn", "D125,D110,D001", "no"),
    r("D143", "license_text populated on ~46% of core listings across 18 countries (Theo cohort)", SSD + " listings; noted in CODEX_HANDOFF_V2 T6.4", "Theo", IA, "CC BY 4.0", "one snapshot", "2026-06", "2026-08", None, "~1-4 weeks", "regulation (registered supply)", "supply-side",
      "no", "", "Join licence text to municipal registries (D170) to measure lawful vs unlawful supply per market", "D170,D162", "no"),

    # ---------------------------------------------------------------- J. Common Crawl
    r("D150", "Common Crawl CDX index rows for airbnb.com/rooms/* + 8 country domains: per-crawl rows, status-200 renders, unique ids", P + "cc_index_summary.csv (50 crawls); raw " + R + "commoncrawl/index/ (450 jsonl.gz, 2.08M rows, 1.2M ids)", "Krish", CC, "Common Crawl terms; page bodies are Airbnb copyright (extract fields only)", "per crawl (~monthly)", "2021-01-25", "2026-08-17", 50, "crawl published ~2-4 weeks after crawl", "supply (archive reach, not supply)", "supply-side / raw",
      "yes: " + NOTE_CC, "Rows per crawl fell from 80-110k (2021) to 17-40k (2023+): crawler budget, not supply", "None as a level series", "D151", "no"),
    r("D151", "Listing survival by crawl (re-fetched live / removed / redirect), with status_informative flag, and by listing age", P + "cc_listing_survival.csv (48); cc_listing_survival_by_age.csv (4)", "Krish", CC, "as above", "per crawl", "2021-04-26", "2026-08-17", 48, "~2-4 weeks", "supply (churn)", "supply-side",
      "yes: " + NOTE_CC, "85-90% a year on; older listings die slower; consistent with Inside Airbnb retention", "Survival by region-year vs Eurostat country growth", "D123", "no"),
    r("D152", "Parsed listing captures: reviews, rating, Superhost, Guest Favorite (2025+), room type, capacity, lat/lng, host years, instant book; no price", P + "cc_listing_panel.csv", "Krish", CC + " WARC records (3,000 renders)", "as above", "per capture", "2021", "2026", 3000, "~2-4 weeks", "supply quality", "supply-side / mix",
      "yes: " + NOTE_CC, "No price in any era; Superhost 58% to 61%, entire-home 80% to 90% of captures", "Guest Favorite share vs ADR premium is not testable without price; drop", "D154", "no"),
    r("D153", "Same-listing review velocity on 1,500 matched pairs (reviews per year by window)", P + "cc_matched_listings.csv; cc_panel_summary.csv (19); " + PP + "03_cc_velocity_annual.csv", "Krish", CC, "as above", "per pair / annual", "2021", "2026", 1500, "~2-4 weeks", "nights", "demand-side",
      "yes: " + NOTE_PRED + " 03, " + NOTE_CC, "Velocity flat for five years (median 9-17 reviews/yr); a supply-quality series, not demand", "None; supply-quality only", "D124", "no"),
    r("D154", "Panel mix by capture year: superhost, guest favorite, entire-home share, median reviews, geography (NA/Europe/LatAm/APAC)", P + "cc_panel_by_year.csv", "Krish", CC, "as above", "annual", "2021", "2026", 6, "~2-4 weeks", "supply mix", "mix",
      "yes: " + NOTE_CC, "Geography shift to North America is crawler reach (utm_source=chatgpt.com), not supply", "None", "D152", "no"),
    r("D155", "WARC records raw (3,000 full renders, 0.5-1 MB each)", R + "commoncrawl/records/ (gitignored, ~700 MB)", "Krish", CC, "extract fields only, never redistribute", "per capture", "2021", "2026", 3000, "~2-4 weeks", "supply", "raw",
      "yes (parsed into D152)", "", "T6.6 in CODEX handoff: CC vs Inside Airbnb same-id rating/review deviation as a data-quality check", "D152,D121", "no"),

    # ---------------------------------------------------------------- K. Regulatory database and quantification
    r("D160", "Regulatory factor register: 32 factors in 4 tiers (NYC LL18, Spain, Greece, Portugal, Paris, Amsterdam, BC, Montreal, Madrid, Malaga, Florence, Budapest, Canaries, EU DSR, Scotland, Barcelona 2028, Maui, Ireland, EU AHA draft...)", REG + "factors.json; factor_register.md; sources.json (48); source_index.md", "Krish", "official laws, court decisions, press (research log)", "public", "event register", "2023", "2026-09-05", 32, "event date (news same day; rule text days-weeks)", "regulation", "supply-side / event",
      "yes: " + NOTE_REG + " (as inputs)", "Regulation is a valuation haircut (median 0.45% revenue 2027, 1.7% 2030), not existential", "Event-study: ABNB day-0 move on the 20 dated events vs QQQ (most are <1% but untested)", "D161,D111,D040", "no"),
    r("D161", "Regulatory forecast: 20 events with p(in force) 2027/2030, loss ranges, Monte Carlo profile (200k draws) and per-event contributions", P + "abnb_regulatory_events.csv (20); abnb_regulatory_profile.csv (24); abnb_regulatory_contributions.csv (40)", "Krish", "analyst forecast on D160 + D162 + D111", "public", "one-off", "2026-09-05", "2026-09-05", 20, "n/a", "regulation / revenue / EBITDA / value per share", "supply-side / scenario",
      "yes: " + NOTE_REG, "Median hit $2.8/share 2027, $8.4 2030; EU act carries the tail; re-run after 9 Sep EU proposal", "None until the EU proposal text", "D160", "no"),
    r("D162", "Market inventory: Airbnb listing IDs, short-minimum and short-entire counts for 32 markets (June-Aug 2026 snapshots); 20 listing snapshots; 1,434 neighbourhood counts", REG + "quantification/market_inventory.json; listing_snapshots.json; neighbourhood_counts.json; raw " + R + "regulatory/quantification/*_listings.csv", "Krish", IA + " visualisations listings.csv", "CC BY 4.0", "one snapshot per market", "2026-06-15", "2026-08-10", 32, "~1-4 weeks", "regulation (exposed supply)", "supply-side / cross-section",
      "yes: " + NOTE_REG + " (exposure denominators)", "Substantial local supply losses can coexist with resilient revenue; listing counts alone cannot show earnings loss", "Monthly re-capture of the same 20 markets to get affected-cohort supply change through the 2027-28 phase-outs", "D160,D113", "yes"),
    r("D163", "Barcelona HUTB licence match (5,146 distinct licences on 5,910 ads) and Maui Minatoya parcel match (3,862 units on 4,350 ads); matched-cohort loss scenarios (18)", REG + "phase2/barcelona_match_summary.json; maui_match_summary.json; matched_cohort_scenarios.json; raw registries in " + R + "regulatory/phase2/", "Krish", "Barcelona open datastore; Maui County PDFs + state GIS", "open government", "one-off", "2026-06", "2026-06", 2, "n/a", "regulation (affected cohort)", "supply-side",
      "yes: " + NOTE_REG + " (cohort sizes)", "Deduplicated cohorts replace assumed counts; booked value per identifier remains the gap", "Track the matched Barcelona cohort's review activity monthly to 2028 as the phase-out signal", "D162,D125", "yes"),
    r("D164", "Spain INE tourist dwellings (all platforms): Spain, Canaries, Balearics, Barcelona, Madrid, Malaga, Ibiza; May-25, Nov-24, Nov-25, May-26", REG + "quantification/spain_supply_history.json; raw " + R + "regulatory/quantification/ine_national.csv, ine_municipal.csv", "Krish", "INE experimental statistics (tables 39363/39364)", "INE open", "semi-annual snapshots held (INE publishes more)", "2024-11", "2026-05", 28, "~2-3 months after reference month", "regulation / regional nights (Spain supply)", "supply-side",
      "yes: " + NOTE_REG + " (descriptive)", "Spain -10.7% y/y May-26; Madrid -28.9%; Barcelona -14.1%", "Pull the full INE series (all reference months, all municipalities) and test vs Eurostat ES nights and ABNB EMEA", "D111,D110", "no"),
    r("D165", "Hawaii vacation-rental performance panel (Lighthouse, all-channel): supply nights, demand nights, occupancy, total rate; state + 4 counties; monthly with report vintages", REG + "phase2/hawaii_monthly_latest.json (155); hawaii_monthly_vintages.json (190); raw " + R + "regulatory/phase2/hawaii_*.xlsx (19 workbooks)", "Krish", "Hawaii DBEDT vacation rental reports", "public (state)", "monthly", "2024-01", "2026-07", 155, "~4-6 weeks after month end; vintages kept", "ADR / occupancy (regional realised), Maui regulation", "price / demand-side",
      "no (used only for Maui exposure context)", "2026 monthly vintages do not reconcile to July restated YTD; do not splice", "The ONLY realised occupancy-and-rate series in hand: Hawaii total rate y/y vs ABNB ADR ex-FX y/y (n 10 quarters); and as the calibration for blocked-rate vs occupancy (D131/D141)", "D003,D131,D141", "no"),
    r("D166", "NYC Local Law 18 activity benchmark: guest-nights 6.56M (Sep22-Aug23) to 2.88M (Sep23-Aug24), lost host earnings $351M", REG + "phase2/nyc_activity_benchmark.json; raw " + R + "regulatory/phase2/nyc_cra_2025.pdf", "Krish", "Airbnb-commissioned CRA report (Dec 2024)", "public", "one-off", "2023", "2024", 3, "n/a", "regulation (loss anchor)", "supply-side",
      "yes: " + NOTE_REG, "56% activity decline is the benchmark, not the 83% listing decline", "None", "D160", "no"),
    r("D167", "Regulatory guidance history: 13 guided quarters with policy context", REG + "quantification/guidance_history.json", "Krish", "derived from D030/D007", "public", "quarterly", "2023Q3", "2026Q3", 13, "0", "guidance", "level",
      "yes: " + NOTE_REG, "All guided quarters met or beat the range through Spain/NYC enforcement; cannot isolate regulation", "None", "D030", "no"),
    r("D168", "Regulatory raw documents: REG-S07/S10/S11/S21 HTML, 10-K FY25 and 10-Q 2Q26 text, Greece 2025 report, Maui resolutions, Barcelona registry zip", R + "regulatory/documents/; quantification/; phase2/", "Krish", "official sources", "public", "one-off", "2025", "2026-09", 60, "n/a", "regulation", "raw",
      "yes (inputs to D160)", "", "None", "", "no"),
    r("D169", "Regulatory SQLite database (events, factors, sources, quantification tables)", "MAIN:data/processed/abnb_regulatory.sqlite (main tree, uncommitted)", "Krish", "built by analysis/src/build_regulatory_database.py + phase2", "public", "n/a", "", "", None, "n/a", "regulation", "database",
      "yes (D160-D167 are views of it)", "", "None", "", "no"),
    r("D170", "Municipal STR registries and lodging taxes, 25 datasets / 17 portals / 109,343 rows: Austin active-STR counts (527 dates), Austin locations, California county+city TOT FY2017-24, NOLA permits/licences (4 sets), Seattle licences, Denver (3), Calgary, Winnipeg, Nova Scotia, Norfolk, Orlando, Cambridge, Marin (registry + TOT revenue), Missouri, Montgomery MD, Oregon lodging tax by type, WeHo buyouts, San Mateo", SSD + "municipal_download_log.csv", "Theo", "Socrata / open-data portals", "open government", "daily to annual (varies)", "2016", "2026-09", 109343, "days (portal refresh) to 1 year (fiscal tax)", "regulation (lawful supply) / regional nights (TOT = taxable lodging revenue)", "supply-side / demand-side",
      "partly: Theo H-006 (NYC OSE) and SCW-001 (Austin) INCONCLUSIVE", "Zero strict-PIT eligible events; portals' historical vintages not established", "Austin daily active-STR count vs Austin Inside Airbnb listings (D121) as a validation; California TOT / tax rate = taxable lodging revenue for 482 cities FY17-24 vs ABNB NA growth (annual, n 4)", "D143,D121,D164", "no"),
    r("D171", "Theo's candidate supply/regulatory sources not acquired: NYC OSE snapshots and enforcement reports, Vancouver STR licences, NOLA permit events and hearings, San Diego STRO, Hawaii TAT district (terms prohibit)", TE + "20260903T062839Z_abnb_edge_discovery/candidate_edge_registry.csv (rows 4, 6, 8, 10-12) and rejected_and_inconclusive_sources.md", "Theo", "municipal portals", "pending permission / prohibited (Hawaii TAT)", "annual to daily", "2016", "", 0, "n/a", "regulation / supply", "supply-side",
      "yes: Theo E1 (all INCONCLUSIVE or blocked)", "No permission cleared; zero observations", "Prospective timestamped snapshots only (Theo's own conclusion)", "D170", "yes"),

    # ---------------------------------------------------------------- L. Academic replication data (Theo, off-machine)
    r("D180", "Harvard Dataverse 'To Airbnb? A question of revenues' (Melbourne / Port Phillip): str_daily_1.tab 210 MB, str_daily_2.csv 370 MB, ltr_data.tab 657 MB, suburb shapefiles", SSD + "dataverse_log.csv (doi:10.7910/DVN/1XPDEU, Q0VVTH)", "Theo", "Harvard Dataverse", "CC0 1.0", "daily (historical)", "~2016", "~2019", None, "historical only", "ADR / occupancy (methodology)", "price / demand-side (historical)",
      "no", "", "Daily booked-vs-blocked-vs-price at listing level (AirDNA-style) to calibrate the blocked-rate to occupancy mapping used in D131/D141", "D141,D131", "no"),
    r("D181", "Other Dataverse files: Rio de Janeiro listings (56 MB), New Zealand Nov 2018, 'Airbnb Feb/May 2018-2021' (Airbnb_DS_real), Brazilian small towns 2019 (6 xlsx), NYC 2019 (AB_NYC), Seattle tax compliance by loccode; Boston (HTTP 400) and Venice/Reykjavik/Boston-MSA AirDNA daily (403, guestbook)", SSD + "dataverse_log.csv (29 rows, 21 files ok)", "Theo", "Harvard Dataverse", "CC0 / per record", "one-off", "2018", "2022", 21, "historical only", "supply (historical)", "supply-side (historical)",
      "no", "Guestbook-gated AirDNA sets need a manual browser form", "Complete the Dataverse guestbook for the Venice/Reykjavik/Boston-MSA AirDNA daily sets: realised occupancy and ADR for three markets to 2020-22", "D165,D180", "no"),
    r("D182", "Zenodo: Barcelona Airbnb (2 files), AirBSet Brazil listings + reviews (1.8 MB), Vienna active apartments Mar 2020", SSD + "repositories_log.csv (8 rows)", "Theo", "Zenodo", "CC BY 4.0 / MIT-0", "one-off", "2020", "2024", 4, "historical only", "supply (historical)", "supply-side",
      "no", "", "None (superseded by Inside Airbnb Barcelona dumps)", "", "no"),

    # ---------------------------------------------------------------- M. Licensed and off-machine terminal exports
    r("D190", "Bloomberg Excel add-in exports: 6,365 rows of consensus estimates, revisions, comps, daily prices (sheets 1, 4, 5, 6 of 6; sheets 2-3 outstanding)", DRIVE + "; described in docs/CODEX_HANDOFF_V2.md sec 4 and 8 (raw_expansion_licensed/v2_2026-09-05/bloomberg/)", "Theo", "Bloomberg terminal (BEST_SALES, BEST_EBITDA, BDH)", "licensed_norestribute", "daily / per revision", "", "2026-09", 6365, "same day (terminal); point-in-time via BDH history", "consensus / positioning / stock reaction", "positioning",
      "no: not in repo; Street Q3 26 consensus $4,744m and FY26 13,371 -> 14,162 quoted from it", "Consensus at each call is the biggest hole in the reaction function", "Extract BEST_SALES / BEST_EBITDA history at each of the 23 call dates into Theo's consensus_snapshots.csv, then guide-vs-consensus gap vs day-1 (the plan's branch 3)", "D036,D030,D042,D046", "no"),
    r("D191", "FactSet CallStreet transcript PDFs (Theo's licensed local copies of the 23 calls)", "Theo private input root (ABNB_PRIVATE_INPUT_ROOT); metadata in " + T + "research/transcripts/transcript_index.csv", "Theo", "FactSet", "licensed_norestribute", "per print", "2021-02-25", "2026-08-06", 23, "1-2 days", "guidance / sentiment", "sentiment",
      "duplicate of D050", "", "None", "D050", "no"),
    r("D192", "SIG-project Bloomberg consensus-at-call extract (schema template: mktcap, price, cons EPS/sales Q and FY at each call)", XO + "data/bb_consensus_at_call.csv (14 SIG rows)", "Krish (prior project)", "Bloomberg transcript-PDF page headers", "licensed (SIG data, not ABNB)", "per call", "2015", "2026", 14, "same day", "consensus (template only)", "positioning",
      "no: template", "Proves the transcript export carries consensus at each call for free", "Run the same export for ABNB at Hough Hall (fills D036)", "D036,D190", "yes"),
    r("D193", "STR / CoStar hotel weekly (planned licensed cohort; entitlement unconfirmed)", "not held (docs/2026-09-05-abnb-data-extraction-v2.md Task 9)", "none", "STR/CoStar", "licensed", "weekly", "", "", 0, "1 week", "ADR / nights (hotel wedge)", "price / demand-side",
      "no: not acquired", "", "Weekly US hotel RevPAR headline numbers are free via CoStar press releases; capture weekly", "D060,D070", "yes"),

    # ---------------------------------------------------------------- N. Build-forward captures and not-yet-acquired channels
    r("D200", "Google Trends weekly: airbnb, vrbo, booking.com, hotels.com, expedia (stitched windows, US and worldwide)", PO + "08_trends_weekly.csv (ws 08, in flight; 9,580 rows)", "Krish (ws 08)", "Google Trends via pytrends", "Google terms (indexed, not redistributable at scale)", "weekly", "2019-01-06", "2026-09-06", 9580, "same day (rescaled per payload)", "nights / share of search", "demand-side / sentiment",
      "in flight (plan branch 5)", "Not yet tested", "Share-of-search (airbnb / sum of five) y/y vs nights y/y and vs NA revenue, quarter averages, n 22; first differences", "D001,D018,D201", "yes"),
    r("D201", "SimilarWeb / Semrush free-tier web traffic snapshot for airbnb.com, vrbo.com, booking.com, expedia.com, hotels.com", "not captured for ABNB; schema in " + XO + "data/web_traffic_snapshot_2026-08.csv (SIG rows)", "none", "SimilarWeb free tier", "free tier (3-month aggregate, MoM only)", "monthly", "", "", 0, "~1 week after month end", "nights (traffic)", "demand-side",
      "no: not acquired (plan branch 8 not done)", "Free tier gives no history: must be built forward from day one", "Start monthly capture now; by December there are 3 points", "D200,D202", "yes"),
    r("D202", "App intelligence (Sensor Tower / Appfigures / AppMagic free tiers): downloads, DAU/MAU for Airbnb, Vrbo, Booking, Hopper", "not captured; access map " + XO + "03_ACCESS_MAP.md sec 3", "none", "vendor free tiers", "free tier / licensed", "monthly", "", "", 0, "days", "nights (app engagement)", "demand-side",
      "no: not acquired", "Flagged Tier 1 for ABNB in the access map", "Verify free-tier depth; capture monthly", "D200,D201", "yes"),
    r("D203", "Card-panel data (Earnest Dash free tier, Consumer Edge academic trial, Bloomberg Second Measure ECAN)", "not acquired; " + XO + "03_ACCESS_MAP.md sec 1", "none", "Earnest / Consumer Edge / Bloomberg", "free tier or terminal", "weekly/monthly", "", "", 0, "~1-2 weeks", "GBV (US card spend at booking) / nights", "demand-side",
      "no: not acquired", "Captures guest charge at booking (GBV-like, US-skewed), not revenue", "Earnest Airbnb-vs-Vrbo spend y/y vs GBV y/y; the only free route to a booking-time series", "D002", "yes"),
    r("D204", "AirDNA / Key Data free market pages and blog posts (STR occupancy, ADR, RevPAR, supply by market)", "not captured; " + XO + "03_ACCESS_MAP.md sec 4", "none", "AirDNA, Key Data", "free surfaces only", "monthly", "", "", 0, "~2-4 weeks", "ADR / occupancy / supply (STR industry)", "price / demand-side",
      "no: not acquired", "Sell-side cites AirDNA; NYC 83% listing decline came from it", "Screenshot AirDNA city pages monthly for the 13 panel cities; ask for an academic sample", "D165,D122", "yes"),
    r("D205", "NTTO I-94 international arrivals to the US by country, monthly", "not captured; " + XO + "03_ACCESS_MAP.md sec 4", "none", "trade.gov/i-94-arrivals", "public", "monthly", "", "", 0, "~4-6 weeks", "nights (inbound US) / cross-border mix", "demand-side / cross-border",
      "no: not acquired", "", "Inbound arrivals y/y vs NA revenue y/y and vs BEA inbound (D092) as a cross-check", "D092,D018", "no"),
    r("D206", "US airport passenger sleeve: SFO monthly aggregate passengers (384 rows), LAX (blocked by CAPTCHA marker), PANYNJ parking (quarterly)", T + "outputs/reproducibility/us-europe-guidance/abnb_us_europe_altdata_long.csv (525 rows: SFO + EU27)", "Theo", "DataSF SODA; LAWA; data.ny.gov", "open data", "monthly", "~1994", "2026-07", 384, "~1-2 months; historical vintages unavailable", "guidance (revenue guide y/y) / nights (US)", "demand-side",
      "yes: Theo H-007, H-010, H-011, H-012 v1/v2", "SFO T3M y/y Pearson 0.78 vs guidance y/y but current-snapshot diagnostic, not PIT; -0.65 on acceleration", "Treat as WATCH_PROSPECTIVELY (Theo); add LAX via browser; test vs NA revenue not guidance", "D115,D018,D085", "no"),
    r("D207", "Census Quarterly Services Survey NAICS 721 accommodation revenue (H-009)", "not acquired (Theo sleeve: INCONCLUSIVE / blocked)", "Theo", "Census QSS API", "public", "quarterly", "", "", 0, "~2.5 months after quarter end (after the print)", "revenue (US category)", "demand-side",
      "yes: Theo H-009 (no observations)", "Blocked on permission; and arrives after the ABNB print anyway", "None for prediction; annual category share only", "D089", "no"),
    r("D208", "Theo's moonshot / physical-world candidates: NASA Black Marble night lights, NOAA HMS smoke, WSF ferry ridership (H-004), Orange County FL TDT (H-005), NPS visitor use, FTA transit ridership, MarineCadastre AIS, NYC 311, Melbourne pedestrians", TE + "20260903T062839Z_abnb_edge_discovery/candidate_edge_registry.csv (15 ranked); ex-ante scores 58-80", "Theo", "various federal / municipal", "public but permission gates unresolved", "daily to quarterly", "2002", "", 0, "varies; historical vintages unproven", "nights (regional realised activity) / guidance", "demand-side",
      "yes: Theo E1 (H-004, H-005 INCONCLUSIVE; others pending)", "Zero strict-cutoff observations for every pilot; no source promoted", "Orange County TDT monthly PDFs (2019+) are the one with genuine release vintages: capture by browser, test vs NA revenue (n ~12)", "D170,D206", "yes"),
    r("D209", "Overture Maps hotel places + world atlas (Theo's global lodging 3D map inputs)", T + "research/source_registry.csv (rows 44-45); " + T + "scripts/build_global_lodging_map.py", "Theo", "Overture Maps Foundation; Natural Earth", "open", "one-off", "2026-08", "2026-08", None, "n/a", "supply (hotel density context)", "supply-side / context",
      "no", "", "None for prediction", "", "no"),

    # ---------------------------------------------------------------- O. Derived analysis panels and model outputs
    r("D220", "Merged quarterly macro-KPI panel (37 columns: KPIs, FX, CPI, BEA, employment, claims, sentiment)", PP + "03_quarterly_panel.csv", "Krish", "derived from D001-D004, D070-D093", "public", "quarterly", "2019Q1", "2026Q3", 31, "mixed (see components)", "nights / GBV / ADR / revenue beat / day-1", "panel",
      "yes: " + NOTE_PRED + " 03", "890 pairs; 5 pass Bonferroni (3 FX mechanism, 2 nights trend)", "Re-run at n 23 after 5 Nov with the same pre-registered pairs only", "D221", "no"),
    r("D221", "Nowcast test results: 900 series-transform-lag-target cells with perm p, BH q, LOO RMSE vs naive, split-half signs", PP + "03_nowcast_results.csv", "Krish", "derived", "public", "n/a", "", "", 900, "n/a", "all KPIs", "results",
      "yes", "As D220", "None", "D220", "no"),
    r("D222", "Print features: 47 contemporaneous and pre-print features per print with 1/5/20-day excess", PP + "04_print_features.csv; 04_reaction_results.csv (394 tests)", "Krish", "derived", "public", "per print", "2021Q1", "2026Q2", 22, "0 / pre-print as labelled", "stock reaction / EBITDA margin", "panel",
      "yes: " + NOTE_REACT, "63 contemporaneous and 60 pre-print tests per sample; none passes Bonferroni", "Add consensus gap (D190) and options-implied move (D044) as columns", "D042,D036,D044", "no"),
    r("D223", "Peer read-through panel and results (255 cells, LOO 51 rows)", PP + "02_peer_readthrough_panel.csv; 02_peer_readthrough_results.csv; 02_peer_readthrough_loo.csv", "Krish", "derived from D060", "public", "quarterly", "2021Q1", "2026Q2", 22, "peer report date", "nights / beat / day-1", "results",
      "yes: " + NOTE_PEER, "Only hotel-RevPAR pairs survive BH post-2022; none beats AR(1)", "None", "D060", "no"),
    r("D224", "Print base rates: per-print beat, guide direction, margin met, FY floor action, reactions; 311 summary cells", PP + "01_print_base_rates.csv; 01_print_base_rates_summary.csv", "Krish", "derived", "public", "per print", "2020Q4", "2026Q2", 23, "0", "stock reaction / guidance", "base rates",
      "yes: " + NOTE_BASE, "Margin met + nights accelerating +5.0% (7 prints); met + decelerating -2.1% (11)", "Score 5 Nov into the same cells", "D042", "no"),
    r("D225", "Margin predictability tests (80) and per-quarter margin surprise panel (14)", PP + "04_margin_predictability.csv; 04_margin_predictability_quarters.csv", "Krish", "derived", "public", "quarterly", "2022Q1", "2026Q2", 14, "0 / lag 1", "EBITDA margin", "results",
      "yes: " + NOTE_REACT, "Lagged S&M deleverage beats the guide bound by 0.2 pts LOO (2.61 vs 2.79)", "None", "D009", "no"),
    r("D226", "Valuation scenarios FY26-28 (bear/base/bull), sensitivity grids (51), reverse DCF (18)", P + "abnb_valuation_scenarios.csv; abnb_valuation_sensitivity.csv; abnb_reverse_dcf.csv; model/assumptions.md", "Krish", "driver model on D001-D013", "public", "annual forecast", "FY2026E", "FY2028E", 9, "n/a", "revenue / EBITDA / FCF / share count / value", "model output",
      "yes: " + NOTE_DRV, "Base $248 EV/EBITDA, $172 SBC-adjusted FCF; bear $176; price implies 7.5% (reported) or 13.3% (SBC-adj) FCF growth", "None (this is the model)", "", "no"),
    r("D227", "Margin scenarios: FY26E, FY27E, Q3 26E, implied Q4 26E by cost line (bear/base/bull)", P + "abnb_margin_scenarios.csv", "Krish", "margin bridge SCEN dict", "public", "forecast", "Q3 2026E", "FY2027E", 12, "n/a", "EBITDA margin / cost line", "model output",
      "yes: " + NOTE_MRG + " 11", "FY26 35.3 / 35.9 / 37.7%; FY27 33.8 / 36.5 / 39.8%", "None", "D226", "no"),
    r("D228", "IA city-level y/y panel from ws 08 (listings, reviews LTM/L30d all and matched, blocked 30/90 y/y pts)", PO + "08_ia_city_yoy.csv", "Krish (ws 08)", "derived from D120", "CC BY 4.0", "per year-ago pair", "2023-12-15", "2026-08-30", 103, "~1-4 weeks", "nights / supply", "demand-side / supply-side",
      "in flight (ws 08)", "Delivered 6 Sep: 103 matched year-ago pairs across 13 cities", "See D125/D131", "D125,D131", "yes"),
    r("D229", "FX quarterly averages and y/y for 9 currencies (ws 10) and XBRL revenue by geography (ws 10)", PO + "10_fx_quarterly.csv (36); 10_xbrl_revenue_geography.csv (258 facts)", "Krish (ws 10)", FRED + "; XBRL segment facts", "public", "quarterly", "2018Q1", "2026Q3", 36, "1 day / filing day", "ADR (FX) / regional revenue", "price / regional",
      "in flight (ws 10)", "Delivered 6 Sep: 9 currencies quarterly, 258 XBRL geography facts", "See D087/D018", "D087,D018", "no"),

    # ---------------------------------------------------------------- P. Overnight run outputs, 6-7 Sep 2026 (workstreams 02-12)
    r("D230", "Reconciled quarterly KPI panel, 30 metrics per quarter (nights, GBV, ADR, revenue, EBITDA, SBC, FCF, cost lines, shares) with XBRL cross-columns", PO + "02_kpi_panel_quarterly.csv", "Krish (ws 02)", LETTERS + "; " + XBRL, "public", "quarterly", "3Q20", "2Q26", 24, "0: print day", "nights / GBV / ADR / revenue / cost line", "level / panel",
      "in flight (ws 02)", "Single reconciled input table; supersedes D001-D013 as the model's feed", "Use as the driver model's input sheet; reconcile the letter-vs-XBRL columns quarter by quarter", "D001,D005,D008,D231", "no"),
    r("D231", "KPI panel long form: 1,050 metric-quarter cells with source quote, source file and verified flag", PO + "02_kpi_panel_long.csv", "Krish (ws 02)", LETTERS, "public", "quarterly", "3Q20", "2Q26", 1050, "0: print day", "all KPIs (provenance)", "evidence / panel",
      "in flight (ws 02)", "Every cell carries a letter sentence; this is the audit trail for D230", "Spot-check the unverified cells before the deck cites them", "D230,D035", "no"),
    r("D232", "Metric coverage register: 74 metrics with first/last quarter and a stopped-before-2Q26 flag", PO + "02_metric_coverage.csv", "Krish (ws 02)", "derived from D231", "public", "quarterly", "3Q20", "2Q26", 74, "n/a", "all KPIs (metadata)", "metadata",
      "in flight (ws 02)", "Names which disclosures Airbnb has quietly stopped giving", "Cross the stopped list against what the model needs; ask IR for the dropped ones", "D233", "no"),
    r("D233", "Disclosure changes log: 23 dated changes in what Airbnb reports", PO + "02_disclosure_changes.csv", "Krish (ws 02)", LETTERS + "; 10-K/10-Q", "public", "event", "2020Q4", "2026Q2", 23, "0: filing", "all KPIs (metadata)", "metadata",
      "in flight (ws 02)", "Disclosure regime shifts (e.g. regional nights bands) break long series", "Flag every model series whose definition changed mid-sample", "D232,D018", "no"),
    r("D234", "Cross-check table letter vs XBRL (ws 02)", PO + "02_crosscheck.csv", "Krish (ws 02)", "derived", "public", "quarterly", "", "", 0, "n/a", "revenue / cost line", "quality control",
      "in flight (ws 02)", "DEFECT: file is empty (2 bytes, no header) as of 01:41", "Re-run 02_kpi_panel.py; the cross-check is the one thing that validates D230", "D230", "yes"),
    r("D235", "Call feature panel: 23 calls x ~60 features (Loughran-McDonald tone, hedging, uncertainty, speaker shares, analyst counts, numbers and forward-looking counts)", PO + "03_call_features.csv", "Krish (ws 03)", "transcripts (D050)", "public", "per print", "2020Q4", "2026Q2", 23, "0-1 day after call", "guidance / stock reaction", "sentiment",
      "in flight (ws 03)", "First quantified tone series for ABNB calls; pairs with 03_reaction_tests.py", "Tone change vs day-1 excess and vs next-quarter guide direction, pre-registered, n 23", "D050,D052,D042", "no"),
    r("D236", "Call turn table: 1,677 speaker turns with role, firm, words, LM counts, numbers, forward-looking phrases", PO + "03_call_turns.csv", "Krish (ws 03)", "transcripts (D050)", "public", "per print", "2020Q4", "2026Q2", 1677, "0-1 day", "sentiment", "sentiment / raw",
      "in flight (ws 03)", "Turn-level base for any later text work (per-analyst, per-exec)", "Per-executive tone drift (Chesky vs CFO) across the CFO transition", "D235,D051", "no"),
    r("D237", "Theme lexicon: 18 regexes used to tag call text", PO + "03_theme_lexicon.csv", "Krish (ws 03)", "hand-built", "public", "one-off", "", "", 18, "n/a", "sentiment (metadata)", "metadata",
      "in flight (ws 03)", "Wider than the 14-topic dict in D052", "Reconcile with D052's TOPICS so topic counts are comparable across notes", "D052", "no"),
    r("D238", "Macro-KPI quarterly panel (ws 05): 31 quarters x ~40 columns (KPIs, margins, FX, BEA, CPI, claims, VMT, regional bands)", PO + "05_macro_quarterly_panel.csv", "Krish (ws 05)", FRED + "; " + BEA + "; " + LETTERS, "public", "quarterly", "2019Q1", "2026Q3", 31, "mixed (see D070-D093)", "nights / ADR / EBITDA margin", "macro / panel",
      "in flight (ws 05)", "Wider and longer than D220 (37 cols, 2021+); includes an in-progress 2026Q3 row", "Use the 2026Q3 partial row as the 5 Nov macro card", "D220,D239", "no"),
    r("D239", "Macro transmission tests: 1,408 macro-transform-lag-target cells with perm p, LOO and post-2024 r", PO + "05_macro_tests_all.csv", "Krish (ws 05)", "derived from D238", "public", "test results", "", "", 1408, "n/a", "nights / ADR / GBV / EBITDA margin", "results",
      "in flight (ws 05)", "Confirms D221: almost all macro-KPI links are 2023 recovery trend", "Count how many of the 1,408 survive perm p < 0.05 AND hold from 2024", "D221,D240", "no"),
    r("D240", "Macro sensitivities with confidence grades: 256 macro-target pairs, effect per unit, margin effect via the cost chain", PO + "05_macro_sensitivities.csv", "Krish (ws 05)", "derived from D239", "public", "test results", "", "", 256, "n/a", "nights / ADR / EBITDA margin", "results / elasticity",
      "in flight (ws 05)", "Only 4 of 256 graded high, all FX-to-ADR/revenue (USD y/y -0.59 pp per pt, r -0.95)", "Put the 4 high-confidence elasticities into the model as explicit FX levers; ignore the rest", "D087,D088,D242", "no"),
    r("D241", "FX fits: 24 target-driver-lag-window fits (ADR FX effect, revenue FX pts) with LOO vs naive", PO + "05_fx_fits.csv", "Krish (ws 05)", "derived from D087/D088", "public", "test results", "", "", 24, "n/a", "ADR (FX) / revenue", "results / price",
      "in flight (ws 05)", "EUR/USD y/y to ADR FX effect r 0.97, +0.46 pp per pt (n 14)", "None; it is the mechanism, already the model's FX line", "D087,D088", "no"),
    r("D242", "FX schedule: fitted ADR and revenue FX contribution by quarter under 3 currency paths, 2025Q3-2027Q4", PO + "05_fx_schedule.csv", "Krish (ws 05)", "derived from D241 + spot", "public", "quarterly (forward)", "2025Q3", "2027Q4", 30, "1 day (spot known daily)", "ADR (FX) / revenue", "price / forecast",
      "in flight (ws 05)", "Turns today's spot into next year's reported ADR and revenue pts mechanically", "Update weekly to 5 Nov; this is the cleanest pre-print number the team owns", "D087,D229,D269", "yes"),
    r("D243", "Macro scenarios: 3 probability-weighted macro paths to 4Q26 and FY27 (nights, ADR ex-FX, FX pts, take rate, margin)", PO + "05_macro_scenarios.csv", "Krish (ws 05)", "derived from D240/D242", "public", "scenario", "4Q26", "FY2027", 3, "n/a", "revenue / EBITDA margin / guidance", "scenario",
      "in flight (ws 05)", "Macro overlay for the bear/base/bull cases in D226", "Reconcile with D226 and D227 so the deck has one set of scenarios, not three", "D226,D227", "no"),
    r("D244", "Shock episode studies: 4 macro shocks with what was guided, what printed and what the stock did", PO + "05_shock_episodes.csv", "Krish (ws 05)", "letters + closes", "public", "event", "2020", "2026", 4, "n/a", "guidance / stock reaction", "analogue",
      "in flight (ws 05)", "Analogue evidence for how management guides into a shock", "None quantitative; use as narrative in the risk section", "D043", "no"),
    r("D245", "Cross-border share of gross nights (management-stated), quarterly", PO + "05_crossborder_share.csv", "Krish (ws 05)", LETTERS + " / calls", "public", "quarterly", "2019Q1", "2024Q1", 15, "0: print day", "nights (mix) / ADR (FX exposure)", "mix",
      "no", "Disclosure stops in 2024Q1; a stopped series (see D232)", "Cross-border share sets how much of ADR is FX-exposed; ask IR to restate it", "D232,D242", "no"),
    r("D246", "Regional growth panel: 4 regions' stated nights bands vs Eurostat, BEA inbound/outbound and USD, 8 quarters", PO + "05_regional_growth.csv", "Krish (ws 05)", LETTERS + "; " + EUS + "; " + BEA, "public", "quarterly", "2024Q3", "2026Q2", 8, "0: print day", "regional nights", "regional / demand-side",
      "in flight (ws 05)", "n 8; too short for a test, useful as a coincident check", "Extend back by coding the pre-2024 regional phrases (D272 has 766 sentences)", "D018,D270,D272", "no"),
    r("D247", "Reaction split by nights-acceleration sign (mean/median 1/5/20-day excess in 4 buckets)", PO + "05_reaction_by_accel.csv", "Krish (ws 05)", "derived from D042 + D001", "public", "summary", "2021", "2026", 4, "n/a", "stock reaction", "base rates",
      "in flight (ws 05)", "Re-states the predictive-study finding (accel sign sets day-1) in bucket form", "None; already the headline of " + NOTE_REACT, "D001,D042", "no"),
    r("D248", "Cost lines per night and % revenue, extended stack with interest, tax, FCF and unearned-fee change", PO + "07_cost_lines_per_night.csv", "Krish (ws 07)", XBRL + "; " + LETTERS, "public", "quarterly", "1Q21", "2Q26", 22, "0: print day", "cost line / EBITDA margin / FCF", "level / per-night",
      "in flight (ws 07)", "Superset of D009: adds interest, tax, FCF and float change per quarter", "Per-night cost lines vs nights growth: which lines are fixed, which scale", "D009,D012", "no"),
    r("D249", "Cost components annual: 38 components FY19-FY25 in dollars, % revenue and % GBV", PO + "07_cost_components_annual.csv", "Krish (ws 07)", XBRL + "; 10-K", "public", "annual", "FY2019", "FY2025", 38, "~6-8 weeks after FY end", "cost line / EBITDA margin", "level / mix",
      "in flight (ws 07)", "% of GBV view is new; normalises cost lines to volume not to revenue", "Cost per night vs cost per dollar of GBV as the operating-leverage test", "D008,D021", "no"),
    r("D250", "Peer margin benchmark: 10 companies x FY21-25, GAAP op margin, SBC %, EBITDA proxy, marketing-only %, FCF conversion", PO + "07_peer_margin_benchmark.csv", "Krish (ws 07)", "SEC XBRL, multiple CIKs", "public", "annual", "2021", "2025", 50, "~6-8 weeks after FY end", "EBITDA margin / SBC (peer context)", "level / peer",
      "in flight (ws 07)", "Wider than D022/D023; separates marketing-only from total S&M", "Where ABNB's margin sits on the peer growth-vs-margin frontier; feeds the multiple argument", "D022,D023,D287", "no"),
    r("D251", "Alt-data feature panel (ws 08): 31 quarters x ~50 point-in-time features (backlog, Eurostat, peers, Inside Airbnb, Trends, CC, macro)", PO + "08_panel_quarterly.csv", "Krish (ws 08)", "derived from D014-D015, D110, D060, D120, D253", "mixed (CC BY 4.0, public)", "quarterly", "2019Q1", "2026Q3", 31, "per-column; available_before_print flag in D252", "nights / GBV / ADR / revenue", "panel",
      "in flight (ws 08)", "The single widest pre-print feature matrix the team has", "Feed the 2026Q3 row into the 5 Nov card; keep the flag discipline", "D220,D238", "no"),
    r("D252", "Feature tests (ws 08): 233 feature-target cells with perm p, LOO and walk-forward vs naive, AR(1) and prior-year", PO + "08_feature_tests_all.csv (trends 152, eurostat 32, backlog 21, inside_airbnb 18, component 10)", "Krish (ws 08)", "derived from D251", "public", "test results", "", "", 233, "n/a", "nights / GBV / ADR / revenue", "results",
      "in flight (ws 08)", "0 of 233 point-in-time features beat AR(1) walk-forward; the honest headline", "None: report the zero. It is the strongest negative result in the pile", "D221,D239,D263", "no"),
    r("D253", "Google Trends weekly, stitched: 12,454 term-geo-week rows (airbnb, vrbo, booking.com, expedia, hotels, near-me variants; US and worldwide)", PO + "08_trends_weekly.csv", "Krish (ws 08)", "Google Trends via pytrends, overlapping windows stitched", "Google terms (no redistribution)", "weekly", "2019-01-06", "2026-09-06", 12454, "~2 days (current week partial)", "nights / GBV", "demand-side / sentiment",
      "in flight (ws 08)", "Plan-of-attack branch 5 delivered; stitch ratios recorded per window", "Weekly refresh to 5 Nov; the quarter-to-date search level is a live nowcast input", "D254,D255", "yes"),
    r("D254", "Trends quarterly features: 31 quarters x ~30 derived features (y/y, share vs peers, airbnb-minus-hotel, near-me ratio)", PO + "08_trends_quarterly_features.csv", "Krish (ws 08)", "derived from D253", "public (derived)", "quarterly", "2019Q1", "2026Q3", 31, "~2 days", "nights / regional nights", "demand-side",
      "in flight (ws 08)", "US share-of-search y/y implies 3Q26 nights ~14.7% vs naive 10.3%: wide band, weak fit", "Score the 3Q26 Trends nowcast on 5 Nov before anyone quotes it", "D253,D264", "yes"),
    r("D255", "Trends tests: 152 Trends feature-target cells, walk-forward against AR(1)", PO + "08_trends_tests.csv", "Krish (ws 08)", "derived", "public", "test results", "", "", 152, "n/a", "nights / GBV / ADR", "results",
      "in flight (ws 08)", "None beats AR(1) walk-forward (part of the 0 of 233)", "None", "D252", "no"),
    r("D256", "Inside Airbnb dump metrics (ws 08 rebuild): listings, reviews LTM and L30d, availability, blocked 30/90, entire share per city-dump", PO + "08_ia_dump_metrics.csv", "Krish (ws 08)", IA, "CC BY 4.0", "per dump (monthly-ish)", "2022-12-13", "2026-08-30", 168, "~1-4 weeks after the dump date", "nights / supply", "supply-side / demand-side",
      "in flight (ws 08)", "Adds blocked-night and L30d review columns to the D121 metric set", "Blocked-30 y/y as a forward occupancy proxy; see the booking-curve caveat in D141", "D121,D125,D131", "no"),
    r("D257", "Inside Airbnb tests: 18 IA feature-target cells with walk-forward", PO + "08_ia_tests.csv", "Krish (ws 08)", "derived", "public", "test results", "", "", 18, "n/a", "nights / ADR", "results",
      "in flight (ws 08)", "13-city coverage is too small a slice of global nights to forecast the print", "None", "D252", "no"),
    r("D258", "Eurostat tests: 32 platform-nights feature-target cells with walk-forward", PO + "08_eurostat_tests.csv", "Krish (ws 08)", "derived from D110", "public", "test results", "", "", 32, "n/a", "regional nights / nights", "results",
      "in flight (ws 08)", "Coincident with EMEA revenue, not a lead (confirms " + NOTE_EU + ")", "None", "D110,D112", "no"),
    r("D259", "Backlog tests: 21 unearned-fee and funds-held feature-target cells with walk-forward", PO + "08_backlog_tests.csv", "Krish (ws 08)", "derived from D014/D015", "public", "test results", "", "", 21, "n/a", "revenue (next quarter)", "results",
      "in flight (ws 08)", "Funds-held y/y lag 1 r 0.95 in-sample but walk-forward RMSE 1.85x AR(1): in-sample only", "Corrects the R^2 0.96 headline in " + NOTE_EU + "; re-state before the deck uses it", "D014,D015", "no"),
    r("D260", "Supply index (equal-weight z of IA listings y/y and CC survival)", PO + "08_supply_index_quarterly.csv", "Krish (ws 08)", "derived from D120/D151", "CC BY 4.0 / public", "quarterly", "2021Q1", "2026Q3", 23, "~1-4 weeks", "supply / nights", "supply-side",
      "in flight (ws 08)", "n 9 usable, r -0.14 with nights: no signal", "None", "D256,D151", "no"),
    r("D261", "Demand index (equal-weight z of EU platform nights, hotel RevPAR, air RPM, IA matched reviews, Trends share)", PO + "08_demand_index_quarterly.csv", "Krish (ws 08)", "derived from D110/D060/D085/D124/D254", "mixed", "quarterly", "2021Q1", "2026Q3", 23, "mixed", "nights / GBV / revenue", "demand-side",
      "in flight (ws 08)", "r 0.76-0.85 in-sample; walk-forward 1.28-2.07x AR(1): loses to AR(1)", "Only the NNLS-weighted nights version beats AR(1) (0.88); fragile, do not promote", "D263,D264", "no"),
    r("D262", "Price index (equal-weight z of IA like-for-like price, CPI lodging, fitted FX contribution)", PO + "08_price_index_quarterly.csv", "Krish (ws 08)", "derived from D122/D070/D241", "mixed", "quarterly", "2021Q1", "2026Q3", 23, "~2-4 weeks", "ADR", "price",
      "in flight (ws 08)", "Reported ADR y/y walk-forward 0.65x AR(1): one of only two things that beat AR(1)", "Score the price index against 3Q26 reported ADR on 5 Nov; it is mostly the FX term", "D242,D264", "yes"),
    r("D263", "Index backtests: 21 index-target-method cells (equal-weight and NNLS expanding) with walk-forward sign accuracy", PO + "08_index_backtests.csv", "Krish (ws 08)", "derived from D260-D262", "public", "test results", "", "", 21, "n/a", "nights / ADR / GBV / revenue", "results",
      "in flight (ws 08)", "Only FX contribution (0.42x AR(1), sign 92%) and the price index (0.65x) beat AR(1)", "Build the 5 Nov card on the FX line only; label the rest as failed", "D242,D262", "no"),
    r("D264", "3Q26 nowcast card: 13 target-feature point forecasts with bands vs naive and prior year", PO + "08_q3_2026_nowcast.csv", "Krish (ws 08)", "derived from D251", "public", "one-off (scoreable 5 Nov)", "2026Q3", "2026Q3", 13, "as of 6 Sep 2026", "nights / GBV / ADR / revenue", "nowcast",
      "in flight (ws 08)", "Nights point 22.9% (band 14.8-31.0) vs naive 10.3%: implausibly high, index inflation", "Freeze this file now and score every row on 5 Nov; that is the honest test", "D265,D242", "yes"),
    r("D265", "3Q26 component values to date (16 inputs feeding D264)", PO + "08_q3_2026_components.csv", "Krish (ws 08)", "derived", "public", "one-off", "2026Q3", "2026Q3", 16, "as of 6 Sep 2026", "nights / ADR", "nowcast (inputs)",
      "in flight (ws 08)", "Snapshot of every quarter-to-date input; re-cut weekly", "Weekly re-cut to 5 Nov", "D264", "yes"),
    r("D266", "Fama-French 5 factors plus momentum, daily", PO + "09_ff_factors_daily.csv", "Krish (ws 09)", "Kenneth French data library", "public (academic use)", "daily", "2020-12-01", "2026-07-31", 1422, "~1 month lag on the library", "stock reaction (risk model)", "positioning / factor",
      "in flight (ws 09)", "Lets the reaction work use factor-adjusted excess rather than QQQ excess", "Re-run the day-1 reaction regressions on FF-adjusted excess; does R^2 0.04-0.07 change", "D040,D042", "no"),
    r("D267", "Sell-side ratings and price-target actions: 466 dated actions (348 maintain, 38 initiate, 35 reiterate, 25 upgrades, 20 downgrades), PTs to $245", PO + "09_analyst_actions.csv", "Krish (ws 09)", "yfinance upgrades/downgrades feed", "Yahoo terms", "event", "2020-12-11", "2026-09-01", 466, "same day", "positioning / stock reaction", "positioning / sentiment",
      "in flight (ws 09)", "First real positioning series in the repo; partly fills the consensus gap (D036)", "Net upgrades minus downgrades and mean PT drift in the 30 days before a print vs day-1 excess, n 23", "D036,D046,D190", "yes"),
    r("D268", "Short interest, semi-monthly settlement dates (12.86M shares latest)", PO + "09_short_interest.csv", "Krish (ws 09)", "exchange short-interest reports", "public", "semi-monthly", "2023-02-28", "2026-08-14", 84, "~8 calendar days after settlement", "positioning / stock reaction", "positioning",
      "in flight (ws 09)", "Short interest ~2% of float; small, but a real crowding read", "Short-interest change into the print vs day-1 excess and vs the 20-day drift, n ~14", "D267,D044", "no"),
    r("D269", "FX basket weights: 22 currency-region rows with proxy series, weights and 1Q26-3Q26 y/y", PO + "10_fx_basket.csv", "Krish (ws 10)", "10-K host-country mix + " + FRED, "public", "one-off + quarterly", "1Q26", "3Q26", 22, "1 day", "ADR (FX) / regional revenue", "price / regional",
      "in flight (ws 10)", "Replaces the single broad-dollar index with an Airbnb-weighted basket", "Basket FX y/y vs stated ADR FX effect: does the weighted basket beat DTWEXBGS (D087)", "D087,D242,D271", "yes"),
    r("D270", "Regional panel quarterly: nights bands, ADR reported and ex-FX for NA, EMEA, LatAm, APAC with the source phrase", PO + "10_regional_panel_quarterly.csv", "Krish (ws 10)", LETTERS + " regional commentary", "public", "quarterly", "4Q20", "2Q26", 23, "0: print day", "regional nights / ADR", "regional / mix",
      "in flight (ws 10)", "Turns qualitative regional phrases into numeric bands, 23 quarters", "Regional nights bands vs Eurostat by country (D111) and vs BEA inbound/outbound", "D018,D246,D272", "no"),
    r("D271", "Regional ADR reported vs ex-FX and the FX gap, 4 regions x 23 quarters", PO + "10_regional_adr_fx.csv", "Krish (ws 10)", "derived from D270 + D269", "public", "quarterly", "4Q20", "2Q26", 92, "0: print day", "ADR (regional)", "price / regional",
      "in flight (ws 10)", "Isolates where the FX borrow actually lands (EMEA and LatAm)", "Regional FX gap vs basket FX y/y as a regional version of the D087 mechanism", "D269,D003", "no"),
    r("D272", "Regional sentence bank: 766 letter sentences tagged by region and metric", PO + "10_regional_quotes.csv", "Krish (ws 10)", LETTERS, "public", "quarterly", "4Q20", "2Q26", 766, "0: print day", "regional nights (provenance)", "evidence",
      "in flight (ws 10)", "Provenance for D270; also the raw material to extend D246 back to 2020", "Code the pre-2024 sentences into bands to lengthen the regional panel", "D270,D246", "no"),
    r("D273", "Quarterly revenue by region from the XBRL geographic axis, 4Q derived as FY less 9M", PO + "10_regional_revenue_xbrl.csv (33 rows); source facts " + PO + "10_xbrl_revenue_geography.csv (258)", "Krish (ws 10)", XBRL + " srt:StatementGeographicalAxis", "public", "quarterly", "2021", "2026Q2", 33, "0: filing day", "regional nights (revenue proxy)", "regional / level",
      "in flight (ws 10)", "DEFECT: the CSV's first line is a comment, so the header row is malformed", "Re-write with a proper header before anything reads it; then regional revenue y/y minus regional FX", "D018,D271", "yes"),
    r("D274", "Supply economics series: 80 metric-date rows (host earnings, listings, supply growth, take-rate and fee facts)", PO + "11_supply_economics.csv", "Krish (ws 11)", LETTERS + "; press; Third Bridge digest", "mixed", "annual/quarterly", "2020-12-31", "2026-12-31", 80, "varies", "supply / take rate", "supply-side",
      "in flight (ws 11)", "Collects the host-side economics the model needs for the fee-change debate", "Host-fee pilot (6-10%, S12) scenarios against take rate", "D006,D055", "no"),
    r("D275", "Alt-accommodation share: ABNB nights vs BKNG alt-accom nights, annual (6) and quarterly (11)", PO + "11_alt_accom_share.csv; 11_alt_accom_share_quarterly.csv", "Krish (ws 11)", "ABNB letters; BKNG releases and calls", "public", "quarterly/annual", "2Q22", "2Q26", 17, "0 to +2 weeks (BKNG often reports after ABNB)", "nights (share) / GBV", "competitive / mix",
      "in flight (ws 11)", "Two-player share of alt-accom nights; the share-shift question quantified", "Share change vs ABNB nights growth: is ABNB losing alt-accom share to Booking", "D060,D276", "no"),
    r("D276", "Alt-accommodation market sizing: 17 third-party estimates by period", PO + "11_alt_accom_market_sizing.csv", "Krish (ws 11)", "third-party research", "public web", "annual", "1Q26", "2029", 17, "n/a", "GBV (TAM)", "context",
      "in flight (ws 11)", "TAM anchors for the long-run growth case", "None quantitative", "D275", "no"),
    r("D277", "Competitor event log: 37 dated moves (Booking, Expedia, Vrbo, Marriott, AI entrants)", PO + "11_competitor_events.csv", "Krish (ws 11)", "press", "public web", "event", "2019-03-07", "2026-09-01", 37, "same day", "stock reaction / nights", "competitive / sentiment",
      "in flight (ws 11)", "Event dating for the competitive narrative; overlaps D043's industry moves", "Competitor-event days vs ABNB same-day excess return, n 37", "D043", "no"),
    r("D278", "AI referral exposure scenarios: 27 year-case rows (AI-referred share of GBV, referral fee, cost in $m and % of EBITDA)", PO + "11_ai_exposure_scenarios.csv", "Krish (ws 11)", "derived; Third Bridge AI calls (S16/S17)", "derived (licensed inputs)", "annual", "2026", "2028", 27, "n/a", "cost line / EBITDA margin", "scenario",
      "in flight (ws 11)", "Sizes the AI-disintermediation bear case in margin points", "Tie to the S&M line: does AI referral spend substitute for or add to performance marketing", "D008,D055", "no"),
    r("D279", "New-business scenarios: 27 rows for Experiences, Services and Hotels, FY25-FY28 revenue", PO + "11_new_business_scenarios.csv", "Krish (ws 11)", "letters + management commentary", "public", "annual", "FY2025", "FY2028", 27, "n/a", "revenue", "scenario",
      "in flight (ws 11)", "Management declined to quantify Experiences attach and hotels scale (D053)", "Hold to the low case until Airbnb discloses; that is the D053 lesson", "D053,D226", "no"),
    r("D280", "Regulatory overlay for the model: revenue drag % by year (median/mean/p95) split EMEA vs NA", PO + "11_regulatory_overlay.csv", "Krish (ws 11)", "derived from D161", "public", "annual", "2026", "2028", 3, "n/a", "revenue / regional nights", "scenario / regulation",
      "in flight (ws 11)", "The regulatory Monte Carlo reduced to three model lines", "Apply as a haircut to EMEA nights in the driver model rather than to global revenue", "D161,D226", "no"),
    r("D281", "Pending regulatory items: 7 dated catalysts with model link and 6 Sep status", PO + "11_regulatory_pending_items.csv", "Krish (ws 11)", "derived from D160/D161", "public", "event", "2026 H2", "2029-01-01", 7, "n/a", "regulation / guidance", "catalyst",
      "in flight (ws 11)", "Calendar of what could move the regulatory line before the pitch", "Watch list for the 5 Nov card and the December pitch", "D160,D280", "yes"),
    r("D282", "ABNB multiples history, quarterly: EV/revenue, EV/EBITDA, EV/FCF, P/SBC-adj FCF, NTM proxies, float-adjusted net cash", PO + "12_abnb_multiples_history.csv", "Krish (ws 12)", "closes + " + XBRL, "public / Yahoo terms", "quarterly", "4Q20", "3Q26", 24, "same day", "valuation / share count", "level / valuation",
      "in flight (ws 12)", "First proper multiple history; nets the $12.2B float out of EV", "Where in its own range does ABNB trade at each print; entry-point evidence", "D020,D283", "no"),
    r("D283", "ABNB multiples monthly: 68 month-ends with LTM fundamentals and yields", PO + "12_abnb_multiples_monthly.csv", "Krish (ws 12)", "closes + " + XBRL, "public / Yahoo terms", "monthly", "2021-02-28", "2026-09-04", 68, "same day", "valuation", "level / valuation",
      "in flight (ws 12)", "Monthly frequency makes the de-rating visible against fundamentals", "Multiple vs LTM growth scatter as the 'what is priced' exhibit", "D282,D284", "no"),
    r("D284", "Multiple regressions: 30 specifications of ABNB's multiple on growth, margin, rates and NDX P/E", PO + "12_abnb_multiple_regressions.csv", "Krish (ws 12)", "derived from D283", "public", "test results", "", "", 30, "n/a", "valuation / stock reaction", "results",
      "in flight (ws 12)", "Explains the multiple with growth and rates; the de-rating is mostly growth", "Use the fitted multiple as the base-case exit multiple instead of a picked number", "D226,D288", "no"),
    r("D285", "Lens tracking: which valuation lens (EV/rev, EV/EBITDA, FCF yield, SBC-adj FCF) tracks the market cap best, by window", PO + "12_abnb_lens_tracking.csv", "Krish (ws 12)", "derived from D283", "public", "test results", "", "", 18, "n/a", "valuation", "results",
      "in flight (ws 12)", "Tells the deck which multiple to lead with", "None", "D284", "no"),
    r("D286", "Print decomposition: 19 prints split into estimate change vs multiple change (NTM revenue before/after)", PO + "12_abnb_print_decomposition.csv", "Krish (ws 12)", "derived from D283 + D042", "public", "per print", "4Q21", "2Q26", 19, "n/a (target-side)", "stock reaction", "results / attribution",
      "in flight (ws 12)", "Separates 'numbers moved' from 'multiple moved' on print days", "If print-day moves are mostly multiple, KPI forecasting cannot pay; test it explicitly", "D042,D001", "no"),
    r("D287", "Peer multiples cross-section: 19 tickers with EV, LTM and NTM fundamentals, SBC and buybacks", PO + "12_peer_multiples.csv", "Krish (ws 12)", "SEC XBRL + closes + NTM proxies", "public / Yahoo terms", "one-off", "2026-09-04", "2026-09-04", 19, "same day", "valuation (peer)", "level / peer",
      "in flight (ws 12)", "The comp table the pitch needs, built from filings not from a screen", "Refresh the day before the pitch", "D250,D288", "yes"),
    r("D288", "Peer regressions: 20 fits of peer multiples on growth, rule-of-40, SBC and FCF conversion; ABNB premium vs fitted", PO + "12_peer_regressions.csv", "Krish (ws 12)", "derived from D287", "public", "test results", "", "", 20, "n/a", "valuation", "results",
      "in flight (ws 12)", "ABNB sits 1% to 95% above fitted depending on spec: the spec choice is the answer", "Report the range, not one number; pick the travel-and-marketplace spec and say why", "D284,D226", "no"),

    # ---------------------------------------------------------------- Q. Fill-ins found in the audit (previously uncensused)
    r("D290", "Reaction regression inputs: 18 prints x 13 print-day features and 1/5/20-day excess", P + "abnb_reaction_inputs.csv", "Krish", "derived from D001-D007 + D042", "public", "per print", "2021Q4", "2026Q2", 18, "0: print day", "stock reaction", "results (inputs)",
      "yes: " + NOTE_DRV, "The input table behind the R^2 0.04-0.07 reaction regression", "None; superseded by D222's 47 features", "D222,D042", "no"),
    r("D291", "Reaction regression output (10 specs) and leave-one-out coefficients (18 drops)", P + "abnb_reaction_regression.csv; abnb_reaction_regression_loo.csv", "Krish", "derived from D290", "public", "test results", "", "", 28, "n/a", "stock reaction", "results",
      "yes: " + NOTE_DRV, "Beat and guide coefficients are not stable to dropping one print", "None", "D290", "no"),
    r("D292", "Booking-curve ranking: 120 market-snapshot rows of blocked-rate by horizon bucket and 30-to-180 slope", PP + "03_booking_curve_ranking.csv", "Krish", IA + " calendar fields", "CC BY 4.0", "per snapshot", "2026-06-14", "2026-08-10", 120, "~1-4 weeks", "nights (forward)", "supply-side / forward",
      "yes: " + NOTE_PRED, "Blocked-rate is not occupancy (hosts block for many reasons); 3 snapshots only", "Needs 4+ quarters of snapshots before any test; keep capturing monthly", "D141,D131", "yes"),
    r("D293", "EDGAR acquisition log: 14 filings with acceptance metadata, sha256 and licence tier", "data/manifests/edgar_filings_log.csv", "Theo", "EDGAR", "public domain", "per filing", "2023-03-31", "2026-06-30", 14, "n/a", "guidance (timing)", "metadata",
      "no", "Has the acceptance metadata D033 says is missing, for 14 of 23 filings", "Extend Theo's logger over all 23 8-Ks to close the D033 timestamp gap", "D033", "yes"),
    r("D294", "Expansion source manifest (3 rows) and expansion log", "data/manifests/expansion_source_manifest.csv; expansion_log.md", "Theo", "Theo acquisition layer", "mixed", "one-off", "2026-09", "2026-09", 3, "n/a", "metadata", "metadata",
      "no", "Thin; the substantive manifests are the municipal and macro logs (D170, D098)", "None", "D170", "no"),
    r("D295", "Crossover prior-project templates with data: bear scoreboard, KPI panel, print-day moves, notable moves", XO + "templates/bear_scoreboard.csv; kpi_panel_quarterly.csv; print_day_moves.csv; sig_notable_moves.csv", "Krish (prior project)", "prior pitch (SIG project)", "internal", "one-off", "", "", 4, "n/a", "stock reaction / all KPIs (template)", "template",
      "no", "Method transfer only; the numbers are another company's", "Copy the bear-scoreboard format for the ABNB risk slide", "D046,D192", "no"),
    r("D296", "Regulatory factor exposures and illustrative loss scenarios (33 factor exposures, 8 illustrative, 18 matched-cohort)", REG + "quantification/factor_exposures.json; illustrative_scenarios.json; " + REG + "phase2/matched_cohort_scenarios.json", "Krish", "derived from D160/D162/D163", "public", "one-off", "2026-08", "2026-09", 59, "n/a", "revenue / regional nights", "regulation / scenario",
      "yes: " + NOTE_REG, "Bottom-up listing-level loss estimates; the input to the Monte Carlo D161", "Reconcile the bottom-up cohort losses with the top-down overlay D280", "D161,D280", "no"),
    r("D297", "Regulatory data-access and validation status (what the pull could not reach; integrity checks)", REG + "phase2/data_access_status.json; phase2_validation.json; quantification/download_errors.json", "Krish", "pipeline metadata", "public", "one-off", "2026-09", "2026-09", 3, "n/a", "metadata", "metadata / gaps",
      "no", "Names the regulatory sources that failed (LSEG intermittent, STR export unavailable)", "Use as the gap list if the regulatory case needs hardening before December", "D056,D193", "no"),
]


def main() -> None:
    rows = []
    for row in ROWS:
        loc = row["file_or_location"]
        # crude on-disk check for the first path token that looks like a repo path
        token = loc.split(";")[0].split(" (")[0].strip()
        on_disk = ""
        cand = None
        if token.startswith("MAIN:"):
            cand = MAIN / token[5:]
        elif token.startswith(PREDICT.name + "/"):
            cand = PREDICT / token[len(PREDICT.name) + 1:]
        elif token.startswith(("data/", "theos-past-research/", "research/", "docs/", "analysis/")):
            cand = ROOT / token
        if cand is not None:
            if "*" in cand.name:          # wildcard token: check the parent folder
                cand = cand.parent
            on_disk = "yes" if cand.exists() else "missing"
        else:
            on_disk = "off-machine" if ("SSD" in loc or "external" in loc or "Drive" in loc) else "n/a"
        row["on_disk"] = on_disk
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in COLS})

    # tallies for the note
    print(f"rows: {len(rows)} -> {OUT}")
    print("on_disk:", Counter(r_["on_disk"] for r_ in rows))
    print("owner:", Counter(r_["owner"].split(" (")[0].split(";")[0] for r_ in rows))
    tested = Counter("yes" if r_["tested_already"].startswith("yes") else
                     ("partly" if r_["tested_already"].startswith(("partly", "in flight", "duplicate")) else "no")
                     for r_ in rows)
    print("tested:", tested)
    print("build_forward yes:", sum(r_["build_forward"] == "yes" for r_ in rows))
    kpi = Counter()
    for r_ in rows:
        primary = r_["maps_to"].split("/")[0].split("(")[0].strip()
        kpi[primary] += 1
    print("primary maps_to:", kpi.most_common())
    role = Counter(r_["role"].split("/")[0].strip() for r_ in rows)
    print("primary role:", role.most_common())
    missing = [r_["id"] for r_ in rows if r_["on_disk"] == "missing"]
    print("missing paths:", missing)


if __name__ == "__main__":
    main()
