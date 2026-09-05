# Source log

Log every source as you use it. Cite it in the deck by the ID.

| ID | Source | Date | Link / location | Used for |
|---|---|---|---|---|
| S1 | ABNB 10-K FY2025 | | https://investors.airbnb.com | |
| S2 | | | | |
| S27 | Theo's ABNB guidance dataset (23 events, Q4 2020 to Q2 2026): revenue guides, KPI direction guides, actuals, 110 letter excerpts, 146 coded management drivers | 2026-09-03 | theos-past-research/research/guidance/data/normalized/ (guidance_items.csv, quarterly_actuals.csv, source_excerpts.csv, driver_observations.csv) | Revenue guide vs actual table (data/processed/abnb_revenue_guidance_vs_actual.csv); guidance timestamps |
| S28 | Theo's event-window returns: ABNB vs QQQ, 1/5/20 sessions after each print, Nasdaq closes | 2026-09-02 | theos-past-research/research/guidance/data/normalized/market_returns.csv | Post-print drift (major moves note 2b) |
| S35 | Eurostat tour_ce_omr, short-stay accommodation booked via collaborative-economy platforms (Airbnb, Booking, Expedia, TripAdvisor), nights spent by month and guest residence, EU27 and 31 countries, 2018 to Mar 2026 (experimental statistics; attribute Eurostat) | 2026-09-05 | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr ; https://ec.europa.eu/eurostat/web/experimental-statistics/collaborative-economy-platforms | European platform category growth vs Airbnb EMEA; country growth across regulatory regimes (research/notes/2026-09-05_eu-platform-and-backlog.md) |
| S36 | SEC XBRL company facts, Airbnb: unearned fees (ContractWithCustomerLiabilityCurrent) and funds held for clients (FundsHeldForClients), quarter ends 4Q20 to 2Q26 | 2026-09-05 | https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json | Backlog indicators vs next-quarter revenue; RNPL break; 3Q26 funds-held read (same note). S32 to S34 are on PRs #11, #12, #13 |

Paid/licensed sources (Bloomberg, CapIQ, etc.): store the export in the shared Drive and link the Drive path here. Do not commit the raw file.
