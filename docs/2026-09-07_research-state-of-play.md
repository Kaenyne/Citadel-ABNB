# Citadel-ABNB: what we have, where each avenue stands, who is on what (7 Sep 2026)

Written after the 7 Sep cleanup. `origin/main` (df833f5) now holds everything: PR #16 merged, no open PRs, no side branches, no worktrees. Number-level detail lives in `docs/2026-09-06_research-inventory.md`; the two-page thesis is `docs/overnight/FINAL_SUMMARY.md`. This note is the map.

## 1. The datasets

**Company and Street.** A 119-column quarterly KPI panel 1Q21 to 2Q26 built from 23 shareholder letters, 23 call transcripts and XBRL, with 342 verbatim quotes behind it. GAAP cost lines, an ex-SBC cash cost stack per night, FY22 to FY25 margin bridges, a 22-quarter FCF bridge, a capital-return panel with a seven-name peer scorecard, and a 79-column regional panel. A guidance ledger of 194 statements across all 23 prints, and consensus reconstructed at each print from 145 sourced press quotes, which closes the biggest hole in Theo's archive. Current Street as of 4 Sep: 466 sell-side actions, 31 live targets, monthly point-in-time multiples, and a 19-name peer cross-section.

**Stock and options.** Daily closes for ABNB and 20 tickers since IPO, Ken French factors, 84 short-interest settlements, 41 attributed moves of 7% or more, 1/5/20-session reactions to every print on an executable next-open entry, and a Yahoo options ledger. Theo's OneDrive share adds the Bloomberg options workbook (daily implied and realised vol since IPO, 67 monthly ATM straddles, full chain on 4 Sep) and a Bloomberg long export. Both are licensed and stay off git. The Bloomberg "consensus history" is a revision history of the FY26 estimate, not point-in-time consensus, and must not be used as such.

**Supply-side alternative data.** Inside Airbnb for 13 cities and 168 dumps Dec 2022 to Aug 2026 (like-for-like price pairs, churn, host concentration, 1.71M fee-inclusive quotes). Common Crawl: 2.08M index rows over 50 crawls, 1.2M unique listing ids, 1,500 matched pairs for survival and review velocity. Theo's booking curves: blocked-night rate by market, snapshot and horizon for 120 markets, plus a 2026 market summary. Jessie's Austin daily active licence series, 527 dates. Theo's external SSD holds the full 120-market store (982k listings, 588M calendar rows, 67.5M reviews) and 25 municipal registries, described by SHA-256 manifests but not in our hands.

**Demand, macro and category.** Eurostat platform nights monthly 2018 to Mar 2026, now with Jessie's platform-versus-hotel country panels. BEA PCE travel, 28 FRED series, TSA, BTS and IATA air traffic, NTTO inbound, Google Trends (not point-in-time), an FX schedule to 4Q27 with fitted ADR and revenue contributions, 93 peer earnings releases parsed to KPIs, and Hawaii DBEDT visitor surveys by accommodation type.

**Regulatory.** A 32-factor register, 48 source records, a SQLite full-text database, per-market supply-at-risk inventories, identifier-matched cohorts for Barcelona and Maui, and a 20-event probability table.

**Language.** 1,677 speaker turns and 132 features per call, a 317-row analyst roster with churn, a 14-topic mix, 37 hand-verified "declined to quantify" instances, 83 management claims scored for credibility, and five Third Bridge expert calls digested.

**What we do not have.** Point-in-time terminal consensus, occupancy, realised ADR from any free source, NYC dumps around Local Law 18, card or app-download panels, and Theo's v3 alt-data tables, 17 of 20 of which never reached the share.

## 2. The avenues and where each stands

**Driver model and valuation. Done to a first version, parked by decision.** The Excel model (9 sheets, 2,353 live formulas, scenario selector, Python mirror reconciling cell for cell) produces bear $74, base $157, bull $228 against $182 spot. The main finding is that the earlier $248 base case was the exit multiple, not the business: three independent methods put fair EV/EBITDA at 13.5 to 18.5x, not 18 to 25.5x. Krish's standing instruction is that revenue, margin and EPS views come first, so the valuation lenses and target prices stay parked until those are agreed. Open items: memo multiples hard-coded, FY25 interest expense reads zero, quarterly regulatory drag not wired, and the build graph has not been run end to end in a clean checkout.

**Margins and cash. Mature.** The lever model (nights, ADR ex-FX, FX, take rate, cost per GBV dollar, support cost per night, brand versus field marketing) and a 40,000-draw Monte Carlo to FY28. Brand and performance marketing growth is the single most informative line for FY margin. The FCF bridge ties to the letters in all 22 quarters.

**Revenue FX. Mature, needs weekly upkeep.** Revenue FX lags spot by one to two quarters, so the Q4 2026 guide steps down about 3 points on arithmetic alone. The bridge exists; the FX schedule needs one FRED pull a week so nobody reads the step-down as a demand break on 5 November.

**Prediction of the print and the stock. Complete, and the answer is mostly negative.** About 3,500 tests. Survivors: dollar-to-ADR FX, guide plus cushion for revenue, and "guide below Street" (nine of nine negative over 20 days, small sample). Alt data, Trends, macro, tone and peer prints do not beat a naive baseline on both windows. The 5 November prediction card is frozen under spec ABNB-WS20-v1 and gets scored on 6 November. The list of withdrawn claims in the master synthesis section 11 is binding; do not re-use them.

**Supply-side panels. Built, awaiting monthly capture.** The Inside Airbnb and Common Crawl panels are in the tree with the partial-scrape artefacts flagged. The one thing that decays is the capture itself: the Inside Airbnb CDN keeps about a year, so the monthly pull on the fixed 13 cities has to start now or the months are lost. NYC pre- and post-LL18 dumps still need to be requested.

**Regulatory. Built, one PR outstanding.** The register, database and Monte Carlo are on main. The probability table should be re-run after the EU Affordable Housing Act text lands on 9 September. Theo's five municipal registry sources should be added.

**Consumer choice and hotel competition. Active, Jessie's lane.** See section 3. This is the avenue with the most new material in the last three days and the least integration into the model.

**Options and event variance. Blocked until late October.** The estimator was rewritten during the audit and is currently unidentified. Re-run in the week of 26 October once the 6 November weekly options list.

**Thesis writing. Not started.** `research/thesis.md`, `docs/TIMELINE.md` and the top of `model/assumptions.md` are still templates. The synthesis supplies the text; nobody has moved it into the deck.

## 3. Who is working on what

**Krish.** Owner of the company panel, guidance and consensus reconstruction, the margin and FCF work, the driver model, the regulatory package, the transcript analytics, the predictive study, the two supply panels, and the overnight synthesis, audit and red team. Immediate queue in order: update the exit-multiple assumptions to 13.5 / 16.5 / 18.5x with the old grid as a labelled sensitivity, refresh the FX schedule weekly, start the monthly Inside Airbnb capture, publish the frozen prediction card, then reconcile the four FY27 revenue estimates into one number.

**Theo.** Built the alt-data acquisition layer (PRs #9 and #10), the 120-market Inside Airbnb store, the booking-curve aggregates, the market summary, and the historical Codex archive under `theos-past-research/` (forecasting packets, guidance contracts, 37 tests). Theo also corrected an important claim: 2026 Inside Airbnb calendars carry no price column, so realised ADR is not obtainable from that data and calendars are a forward booking curve instead. What we need from Theo: the Bloomberg export, the 67.5M-review store and the 25 municipal registries off the SSD, the 17 missing v3 artifacts onto the share, and removal of the `.secrets/env.sh` file from the OneDrive share.

**Jessie.** Owner of the top-down and consumer-choice lanes. Merged in PR #17: TSA, BTS and IATA air traffic against nights (correlations near zero since 2024), a macro top-down framework whose conclusion is that Airbnb's volume is macro-insensitive right now while reported growth is FX-sensitive, Austin daily licences (+29% in 18 months, step changes tied to enforcement dates), Eurostat crowding tests, Hawaii DBEDT accommodation splits, NYC and Vancouver enforcement data, and a listing-size-versus-demand regression. Still in root zips and not yet in the tree: direct-booking leakage (sized at about 1.8% of FY25 revenue in an aggressive case, so a take-rate ceiling argument, not a short thesis), a host-only fee elasticity model, hotel loyalty (membership near universal but weakest in leisure, where Airbnb competes), hotel news transmission channels and a catalyst calendar, an ABNB versus BKNG versus EXPE revenue-model comparison, and the stay-length and party-size study. That study's headline numbers are worth carrying into the model: Airbnb stays run about 1.8x US hotel stays, a kitchen adds 1.2 to 1.5 nights per booking, the mean party is about 3 people, and the price crossover where an entire home beats two hotel rooms is a party of 3. Version 6 adds a choice-probability nights driver calibrated on 2025 US data.

## 4. Where the avenues meet

Three of Jessie's findings feed directly into the operating view Krish wants built first. The party-size crossover and the bedroom-nights finding from the synthesis say the same thing from two directions: half of ADR growth is a bigger unit, not a higher price. The direct-booking and host-only fee work bound the take-rate line. The hotel loyalty note removes an overstated bear point. None of the three is wired into the driver model yet, and the choice-probability nights driver has not been reconciled with the regional nights build. That reconciliation is the natural next joint task.

## 5. Housekeeping still open

Unpack Jessie's 14 root zips on one branch (keep only stay-length v6) and delete the zips. Purge the five licensed Third Bridge PDFs tracked under `research/`. Decide whether Theo's archive stays in this repo or moves to its own. Reset the stale local `main` checkout, which is 54 commits behind with 93 uncommitted files, after confirming nothing in it is unique. New source ids start at S66.
