# Source log

Log every source as you use it. Cite it in the deck by the ID.

| ID | Source | Date | Link / location | Used for |
|---|---|---|---|---|
| S1 | ABNB 10-K FY2025 | | https://investors.airbnb.com | |
| S2 | | | | |
| S27 | Theo's ABNB guidance dataset (23 events, Q4 2020 to Q2 2026): revenue guides, KPI direction guides, actuals, 110 letter excerpts, 146 coded management drivers | 2026-09-03 | theos-past-research/research/guidance/data/normalized/ (guidance_items.csv, quarterly_actuals.csv, source_excerpts.csv, driver_observations.csv) | Revenue guide vs actual table (data/processed/abnb_revenue_guidance_vs_actual.csv); guidance timestamps |
| S28 | Theo's event-window returns: ABNB vs QQQ, 1/5/20 sessions after each print, Nasdaq closes | 2026-09-02 | theos-past-research/research/guidance/data/normalized/market_returns.csv | Post-print drift (major moves note 2b) |
| S35 | Airbnb earnings-call transcripts, Q4 2020 to Q2 2026 (23 calls), Q&A roster, topic counts and decline log | 2021-02-25 to 2026-08-06 | FactSet corrected PDFs on Airbnb IR: https://s26.q4cdn.com/656283129/files/doc_financials/{yyyy}/q{n}/Airbnb-Q{n}-{yy}-Earnings-Call-Transcript.pdf (Q1 2023 onward) and .../2021/q4/CORRECTED-TRANSCRIPT-Airbnb,-Inc.(ABNB-US),-Q4-2021-Earnings-Call-15-Feb-22.pdf; Q4 2020 to Q4 2022 from https://stockanalysis.com/stocks/abnb/transcripts/. Local copies in data/raw/transcripts/ (gitignored) | data/processed/abnb_call_roster.csv, abnb_call_roster_churn.csv, abnb_call_topics.csv, abnb_declined_to_quantify.csv |
| S36 | Transcript analytics note: sell-side roster churn, topic mix management vs analysts, declined-to-quantify log | 2026-09-05 | research/notes/2026-09-05_transcript-analytics.md | Coverage trend, what analysts ask that management does not volunteer, the four unquantified items (services/experiences economics, hotels, AI spend, long-term margin) |

Paid/licensed sources (Bloomberg, CapIQ, etc.): store the export in the shared Drive and link the Drive path here. Do not commit the raw file.
