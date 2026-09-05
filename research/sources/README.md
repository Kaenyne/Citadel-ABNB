# Source log

Log every source as you use it. Cite it in the deck by the ID.

| ID | Source | Date | Link / location | Used for |
|---|---|---|---|---|
| S1 | ABNB 10-K FY2025 | | https://investors.airbnb.com | |
| S2 | | | | |
| S27 | Theo's ABNB guidance dataset (23 events, Q4 2020 to Q2 2026): revenue guides, KPI direction guides, actuals, 110 letter excerpts, 146 coded management drivers | 2026-09-03 | theos-past-research/research/guidance/data/normalized/ (guidance_items.csv, quarterly_actuals.csv, source_excerpts.csv, driver_observations.csv) | Revenue guide vs actual table (data/processed/abnb_revenue_guidance_vs_actual.csv); guidance timestamps |
| S28 | Theo's event-window returns: ABNB vs QQQ, 1/5/20 sessions after each print, Nasdaq closes | 2026-09-02 | theos-past-research/research/guidance/data/normalized/market_returns.csv | Post-print drift (major moves note 2b) |
| S32 | Inside Airbnb listings.csv.gz dumps, 13 cities, 168 dumps Dec 2022 to Aug 2026 (CC-BY 4.0; attribute "Inside Airbnb" on slides) | 2026-09-05 | https://insideairbnb.com/get-the-data/ ; CDN pattern https://data.insideairbnb.com/<country>/<region>/<city>/<date>/data/listings.csv.gz ; manifest data/raw/inside_airbnb/manifest.csv | Same-listing price y/y, listing retention, review velocity, host concentration, exposed nights (research/notes/2026-09-05_inside-airbnb-supply-panel.md). S29 to S31 are on krish/margin-drivers and krish/crossover-kit |

Paid/licensed sources (Bloomberg, CapIQ, etc.): store the export in the shared Drive and link the Drive path here. Do not commit the raw file.
