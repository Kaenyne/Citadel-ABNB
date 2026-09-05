# Source log

Log every source as you use it. Cite it in the deck by the ID.

| ID | Source | Date | Link / location | Used for |
|---|---|---|---|---|
| S1 | ABNB 10-K FY2025 | | https://investors.airbnb.com | |
| S2 | | | | |
| S27 | Theo's ABNB guidance dataset (23 events, Q4 2020 to Q2 2026): revenue guides, KPI direction guides, actuals, 110 letter excerpts, 146 coded management drivers | 2026-09-03 | theos-past-research/research/guidance/data/normalized/ (guidance_items.csv, quarterly_actuals.csv, source_excerpts.csv, driver_observations.csv) | Revenue guide vs actual table (data/processed/abnb_revenue_guidance_vs_actual.csv); guidance timestamps |
| S28 | Theo's event-window returns: ABNB vs QQQ, 1/5/20 sessions after each print, Nasdaq closes | 2026-09-02 | theos-past-research/research/guidance/data/normalized/market_returns.csv | Post-print drift (major moves note 2b) |
| S34 | Driver model note (decomposition, reaction function, scenarios, reverse DCF) and model/assumptions.md; balance sheet from SEC XBRL 10-Q for 30 Jun 2026 (cash $6,821M, short-term investments $5,248M, notes $2,500M, funds held for clients $12,224M, diluted shares 597M) | 2026-09-05 | research/notes/2026-09-05_driver-model.md ; https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json | Valuation lenses, what the price implies, reaction-function result. S32 and S33 are on krish/inside-airbnb-supply (PR #11) and krish/cc-listing-panel (PR #12) |

Paid/licensed sources (Bloomberg, CapIQ, etc.): store the export in the shared Drive and link the Drive path here. Do not commit the raw file.
