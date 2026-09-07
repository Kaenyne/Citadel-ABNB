# Top-down: how macro conditions reach Airbnb (and how much they matter)

**Author:** Jessie (with Claude). **Date:** 2026-09-05. **Data:** `data/processed/macro_us_monthly.csv` (FRED), `us_real_gdp_growth_quarterly.csv`, `sp500_monthly_close.csv`, `airbnb_adr_takerate_quarterly.csv` (ADR/take rate from Krishang's earnings-call study), plus the Airbnb KPI and regional-revenue files already in the repo. **Script:** `analysis/src/macro_topdown.py`; full output in `analysis/macro_topdown/results.md`.

> **Correction 2026-09-05 (v2):** row 3 (oil vs North America revenue) is marked spurious after extending the window and running t-tests; see analysis/figures/oil_vs_na_revenue.png and the chat thread. Everything else unchanged.

## The causal chain (what a top-down model of Airbnb has to contain)

| Layer | Macro input | Airbnb line it hits | What the data says (2024Q1–2026Q2) |
|---|---|---|---|
| 1. Demand volume | Employment, real income, real consumption, consumer confidence, GDP | Nights booked | **Nothing.** Nights YoY vs real PCE 0.00, sentiment +0.16, unemployment +0.03, GDP −0.27. Nights grew 7–10% while Michigan sentiment hit a record-low 44.8 (May 2026). |
| 2. Price | FX translation (USD vs EUR and others); inflation | ADR, GBV, reported revenue | **FX is the whole story.** Broad-dollar YoY vs ADR YoY r = −0.99, vs GBV −0.92, vs revenue −0.66, vs EMEA revenue −0.71. EUR/USD YoY vs ADR +0.91. US CPI vs ADR ≈ 0. |
| 3. Substitution / mix | Oil → airfares and driving costs → drive-to and value travel | North America revenue | **SPURIOUS — dropped.** r = +0.92 (2024Q1–2026Q2, n=11) came from a shared inflection: oil spiked with the Strait of Hormuz closure in the same quarters Airbnb reaccelerated. Extended: 2023Q1–2026Q2 n=14 r = +0.56; drop 2026Q2 alone → r = +0.14 (p = 0.65); 2021–22 r = +0.86 is pure reopening. No stable relationship, no mechanism that survives (higher oil should reduce travel, not raise it). Do not use in the pitch. |
| 4. Financial lines | Policy rate | Interest income on ~$12B of cash/float; buyback capacity | Not visible in KPIs, but real: each 100 bp on ~$12B ≈ $120M pre-tax ≈ ~4% of net income (≈ $0.20/share). Fed funds fell from 5.33% to 3.63% — a quiet EPS headwind hiding in "other income." |
| 5. Valuation | Rates, equity market | Multiple, stock return | ABNB quarterly beta to the S&P 500 ≈ 1.16 (r +0.47). No macro variable explains *excess* returns (all |r| < 0.5 except GDP at −0.63 on 10 points — noise). |
| 6. Supply | Mortgage rates, home prices, local regulation | Listings growth, host economics | Not tested here (no clean series). Hosts' incentive to list rises when carrying costs rise; regulation is the binding constraint in top cities. |

## Three conclusions

1. **Airbnb's volume is macro-insensitive right now.** Consumer confidence, income and employment have had no measurable pull on nights booked since 2024 — the same result as the air-traffic study. This is a share-gain story, not a consumer-cycle story, and the memo should say so plainly.
2. **Airbnb's *reported* growth is FX-sensitive.** The 2025–26 GBV acceleration (+16–19%) carries a dollar-weakness component: EMEA revenue growth moves ~0.8 pts per 1% move in EUR/USD; management itself put ~3 pts of Q3 2026 revenue growth on FX. If the dollar rebounds, reported GBV growth converges toward nights growth (~10%) with no change in the business — and a market that just re-rated the stock 17% on "acceleration" would notice. This is the cleanest macro risk to name.
3. **Rates matter through the P&L and the multiple, not through demand.** Lower rates cut interest income on the float; higher rates compress a 34x multiple. Either way it isn't about travel.

## The trap to avoid

Over 2022–2026 the raw correlations look dramatic (10-year yield vs nights −0.92, CPI vs nights +0.78). They are artifacts: 2022 combined 60% post-COVID nights growth with 8% inflation and zero rates, and everything normalized together. Any macro claim about Airbnb has to be made on 2024 onward, and with n = 10 it is descriptive, not statistical.

## How this fits the team's other work

Theo's IC brief reached the same place from the other side: a travel-activity composite correlates with guidance *levels* (0.78, retrospective) but shows no forecast edge and no guidance-to-return relationship. Krishang's call study shows the 2025–26 reacceleration came from product changes (RNPL, cancellation policy, single fee), not macro. Together: bottom-up product and take rate decide the pitch; macro's job is the FX sensitivity and the interest-income line in the model.

## Sources

FRED series UMCSENT, UNRATE, CPIAUCSL, DSPIC96, PSAVERT, FEDFUNDS, GS10, TWEXBGSMTH, MCOILWTICO, PCEC96, EXUSEU, A191RL1Q225SBEA (fred.stlouisfed.org/data/<ID>.txt, pulled 2026-09-05); Yahoo Finance ^GSPC and ABNB monthly closes; Airbnb shareholder letters (KPIs; ADR and take rate via research/airbnb_earnings_call_study.md); Airbnb 10-Q/10-K regional revenue.
