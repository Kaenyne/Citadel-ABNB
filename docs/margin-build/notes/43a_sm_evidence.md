# 43a. Sales & marketing: the evidence behind Thesis 3, rebuilt

Krish with Claude (Fable 5.1), 22 Sep 2026. Script `analysis/src/margin_build/43a_sm_evidence/run.py` (`py -3.13 -X utf8`, exit 0,
~5 s), outputs `data/processed/margin_build/43a_sm_evidence/`. Pre-registered in `43a_prereg.md` (written before the script existed;
every pass line below was fixed there). Inputs: the authoritative panel `02_panel_quarterly.csv` (cash lines = GAAP less SBC), the
S&M split tables from the 10-Ks (FY2018-FY2025) and the eight 10-Qs cached in the repo, and the management-statement ledger
`05_mgmt_statements_v2/05_statements.csv`. Nothing in `40_line_build`, `41_cost_leg` or the official model is changed. Nothing here is
a forecast; every number is a description of the printed history and carries its n.

Windows: W1 = observations dated 1Q23-2Q26 (n 14), W2 = 1Q24-2Q26 (n 10); "J" = Jessie's 1Q22-2Q26 (n 18), reported for
reproduction only. HAC = Newey-West (lag 2 for levels, lag 3 for y/y series). A result is quoted only if it passes both W1 and W2.

## Bottom line

1. **The 1.41 reproduces exactly and is not an elasticity.** It is the ratio of two trend growth rates (S&M cash +4.6% a quarter,
   revenue +3.2% a quarter, ratio 1.44; the FY22-FY25 log-growth ratio is 1.40). Adding a linear trend to the same regression takes
   the revenue coefficient to 0.05 (95% CI -0.98 to +1.08). DW 0.93, residual AR(1) 0.52: spurious-regression risk high. The
   coefficient rises to 1.61 (W1) and 1.70 (W2) as the window shortens, which is what a trend ratio does and a structural elasticity
   does not. The memo must not call it an elasticity or say "every 10% of revenue growth has cost 14% more marketing".
2. **"S&M grows faster than revenue" survives as a growth statement, and that is the number to quote.** Cash S&M compounded at 19.2%
   a year FY22-FY25 against 13.4% for revenue (ratio 1.44; 1.86 FY23-FY25). Quarter by quarter, S&M y/y growth exceeded revenue
   growth in **11 of 14** quarters since 1Q23 (mean gap 5.8pp a year, HAC p 0.047, sign-test p 0.029) and **9 of 10** since 1Q24
   (8.9pp, p < 0.001, sign p 0.011). Pre-registered pass line met in both windows.
3. **The growth is an intercept, not a response to revenue.** In y/y logs `g_sm = c + k g_rev` gives k 0.41 (t 3.3) on 1Q22+ (the
   same number as M6's 0.410), but k 0.25 (SE 0.57) in W1 and 0.77 (SE 0.73) in W2, both insignificant, while the intercept is
   0.11-0.16: S&M grows 12-17% a year at zero revenue growth. That is the same finding as M6's `c_sm` 0.155 and its asymmetry
   (k_dn -0.12 vs k_up +1.83, p 0.003, n 16). The honest sentence is "S&M is a budget that rises regardless of revenue", not
   "S&M is 1.4x levered to revenue".
4. **"Accelerating" passes its pre-registered test, but say "widened every year" and quote the by-year numbers, not the p-values.**
   The S&M-minus-revenue growth gap was -1.6pp in FY23, +9.2pp in FY24, +9.9pp in FY25 and +12.8pp in 1H26; cash S&M went from 16.5%
   of revenue (FY23) to 19.4% (FY25) to 23.9% (1H26); each incremental revenue dollar cost $0.15 of S&M in FY23, $0.29 in FY24, $0.35
   in FY25 and $0.38 in 1H26. The trailing-4Q trend tests all pass both windows (t 3.8 to 18.7), but those series are smooth sums and
   HAC does not fully correct that, so the t-statistics overstate certainty. FY24 to FY25 was only +0.7pp; the step is 1H26.
5. **Which component: FY25 was field operations, 1H26 is marketing.** Brand & performance marketing grew +20% in FY24, only +10% in
   FY25 (below revenue), and **+32% in 1H26**; field operations & policy grew +25%, **+43%** and +24%. Of FY25's 20.5% S&M growth,
   field ops contributed 14.0pp and marketing 6.5pp; of 1H26's 29.7%, marketing contributed 21.3pp and field ops 8.4pp. So the FY27
   base the Street expects to lever is two layers: launch headcount that management calls fixed, on top of a marketing step that the
   10-Q attributes to "paid growth marketing initiatives in emerging markets and partnerships".
6. **Marketing efficiency is falling on every ratio, but "paying for this quarter's nights, not the next" is NOT supported.**
   Incremental revenue per incremental S&M dollar: $7.6 (FY22), $6.6 (FY23), $3.4 (FY24), $2.9 (FY25), $2.7 (1H26); incremental
   nights per incremental $1M of S&M: 0.29m, 0.24m, 0.13m, 0.10m, 0.08m (trend tests pass both windows). But the lead/lag evidence
   does not identify timing: the contemporaneous correlation of S&M growth with nights growth is 0.04 in W1 (n 14) and 0.23 for
   marketing-only (n 12), all inside the 95% band; Jessie's 0.66 is a 1Q22+ artefact of the 2022 reopening year. Drop the sentence.

## Tables

**H1. Jessie's levels regressions reproduced** (`43a_h1_levels_elasticity.csv`; log(line) ~ log(revenue) + quarter dummies)

| sample | line | coef | NW SE | 95% CI | R2 | DW | resid AR(1) | BG p | n |
|---|---|---|---|---|---|---|---|---|---|
| 1Q22+ | Sales & marketing | **1.410** | 0.088 | 1.24-1.58 | 0.95 | **0.93** | 0.52 | 0.076 | 18 |
| 1Q22+ | Cost of revenue | 0.862 | 0.027 | 0.81-0.92 | 0.98 | 2.41 | -0.24 | 0.57 | 18 |
| 1Q22+ | Ops & support | 0.534 | 0.077 | 0.38-0.68 | 0.88 | 1.38 | 0.27 | 0.067 | 18 |
| 1Q22+ | Product development | 0.868 | 0.061 | 0.75-0.99 | 0.93 | **0.68** | 0.64 | 0.036 | 18 |
| 1Q22+ | G&A | 0.491 | 0.330 | -0.16-1.14 | 0.27 | 1.86 | 0.07 | 0.94 | 18 |
| W1 | Sales & marketing | 1.614 | 0.158 | 1.30-1.92 | 0.95 | 1.08 | 0.37 | 0.10 | 14 |
| W2 | Sales & marketing | 1.701 | 0.082 | 1.54-1.86 | 0.99 | 1.16 | 0.39 | 0.12 | 10 |
| 1Q22+ | S&M, **+ linear trend** | **0.051** | 0.526 | -0.98-1.08 | 0.96 | 1.28 | 0.34 | 0.25 | 18 |
| W1 | S&M, + linear trend | 0.183 | 1.037 | -1.85-2.22 | 0.96 | 1.36 | 0.20 | 0.23 | 14 |
| W2 | S&M, + linear trend | 1.394 | 0.422 | 0.57-2.22 | 0.99 | 1.02 | 0.45 | 0.03 | 10 |

Jessie's SE 0.075 is Newey-West without the small-sample correction; with it 0.088 (her CI 1.26-1.56 becomes 1.24-1.58). Her
other four coefficients reproduce to three decimals. Engle-Granger ADF on the S&M residual p 0.027 (n 18, one lag), so the two
series are not provably unrelated, but a DW of 0.93 with 18 quarters is the textbook spurious-regression signature.

**H1b. Trend ratio** (`43a_h1b_trend_ratio.csv`): trend of log S&M / trend of log revenue (both with quarter dummies)

| sample | n | S&M trend /q | revenue trend /q | ratio | levels coef | difference |
|---|---|---|---|---|---|---|
| 1Q22+ | 18 | 0.0462 | 0.0322 | **1.435** | 1.410 | -0.025 |
| W1 | 14 | 0.0483 | 0.0293 | 1.647 | 1.614 | -0.033 |
| W2 | 10 | 0.0513 | 0.0299 | 1.714 | 1.701 | -0.013 |

Pre-registered expectation (within 0.15): holds in all three samples.

**H2. Growth rates** (`43a_h2a_growth_elasticity.csv`, `43a_h2b_growth_gap.csv`; y/y logs)

| sample | n | k (SE) | c (SE) | R2 | mean gap g_sm - g_rev | HAC t | one-sided p | quarters positive | sign p | pass line |
|---|---|---|---|---|---|---|---|---|---|---|
| 1Q22+ | 18 | 0.410 (0.124) | 0.131 (0.034) | 0.25 | +2.3pp | 0.64 | 0.27 | 12/18 | 0.12 | n/a |
| W1 | 14 | 0.252 (0.574) | 0.155 (0.056) | 0.01 | **+5.8pp** | 1.81 | **0.047** | **11/14** | 0.029 | PASS |
| W2 | 10 | 0.769 (0.731) | 0.112 (0.075) | 0.17 | **+8.9pp** | 5.70 | **<0.001** | **9/10** | 0.011 | PASS |

(The three quarters below zero in W1: 3Q23, 4Q23 and 1Q24 — the 2023 ADR-normalisation trim, when marketing grew 2% and 7% y/y;
every quarter since 2Q24 is positive, ten in a row.)

**H2c. CAGR** (`43a_h2c_cagr_ratio.csv`, `43a_h2c_cagr_all_lines.csv`; cash lines, panel FY sums)

| span | S&M cash CAGR | revenue CAGR | ratio | log-growth ratio | gap pp/yr |
|---|---|---|---|---|---|
| FY22 -> FY25 | 19.2% | 13.4% | **1.44** | 1.40 | +5.9 |
| FY23 -> FY25 | 20.6% | 11.1% | 1.86 | 1.78 | +9.5 |
| 1H24 -> 1H26 | 22.3% | 13.4% | 1.67 | 1.60 | +8.9 |
| 1H25 -> 1H26 | 29.9% | 17.1% | 1.75 | 1.66 | +12.8 |
| FY19 -> FY25 | 6.8% | 16.9% | 0.41 | 0.42 | -10.0 |

All cash lines, FY22 -> FY25 CAGR against revenue 13.4%: S&M 19.2% (1.44x), product development 11.9% (0.89x), cost of revenue
11.7% (0.87x), G&A ex lodging reserves 10.7% (0.80x), ops & support 8.2% (0.61x), total cash costs 13.3% (0.99x). **FY23 -> FY25:
product development 14.0% (1.27x) also outgrew revenue (11.1%)**, so "the one cost line that does not scale with revenue" is only
true on the FY22 base; on the FY23 base S&M (1.86x) and PD (1.27x) both did.

**H3. Acceleration** (`43a_h3_by_year.csv`, `43a_h3_acceleration.csv`)

| period | revenue y/y | S&M cash y/y | gap pp | S&M cash % rev | inc. S&M per inc. revenue $ | inc. revenue per inc. S&M $ | inc. nights (m) per inc. S&M $M |
|---|---|---|---|---|---|---|---|
| FY22 | +40.2% | +29.1% | -11.1 | 16.7% | 0.13 | 7.6 | 0.29 |
| FY23 | +18.1% | +16.5% | -1.6 | 16.5% | 0.15 | 6.6 | 0.24 |
| FY24 | +12.0% | +21.1% | **+9.2** | 17.8% | 0.29 | 3.4 | 0.13 |
| FY25 | +10.3% | +20.1% | **+9.9** | 19.4% | 0.35 | 2.9 | 0.10 |
| 1H25 | +9.8% | +15.1% | +5.3 | 21.6% | 0.32 | 3.1 | 0.13 |
| 1H26 | +17.1% | +29.9% | **+12.8** | 23.9% | 0.38 | 2.7 | 0.08 |

Trailing-4Q trend-on-time tests (HAC 3, one-sided): share of revenue slope +0.28pp/q W1 (p 0.001, n 14), +0.46pp/q W2 (p < 0.001,
n 10); incremental S&M per revenue $ +0.022/q W1, +0.030/q W2 (both p < 0.001); growth gap (c) +1.3pp/q W1, +1.8pp/q W2 (both
p < 0.001) — the pre-registered "accelerating" line passes both windows. Revenue per incremental S&M $ slope -0.40/q W1 (p < 0.001),
-0.61/q W2 (p 0.003); nights per S&M $M -0.014/q, -0.019/q (both p < 0.001) — "efficiency falling" passes both windows. Caveat: T4Q
sums are heavily autocorrelated and HAC(3) with n 10-14 understates the SE; treat the p-values as directional and quote the table.

**H4. The 10-K split** (`43a_h4_components_annual.csv`, `_halfyear.csv`; GAAP, $M; verified against every cached filing)

| | FY19 | FY20 | FY21 | FY22 | FY23 | FY24 | FY25 | 1H25 | 1H26 |
|---|---|---|---|---|---|---|---|---|---|
| Brand & performance marketing | 1,140 | 479 | 723 | 1,030 | 1,208 | 1,455 | 1,595 | 824 | 1,091 |
| y/y | +71% | **-58%** | +51% | +42% | +17% | +20% | **+10%** | +9% | **+32%** |
| % of revenue | 23.7 | 14.2 | 12.1 | 12.3 | 12.2 | 13.1 | 13.0 | 15.4 | 17.4 |
| Field operations & policy | 481 | 697 | 463 | 486 | 555 | 693 | 993 | 430 | 535 |
| y/y | +11% | +45% | -34% | +5% | +14% | +25% | **+43%** | +29% | +24% |
| % of revenue | 10.0 | 20.6 | 7.7 | 5.8 | 5.6 | 6.2 | 8.1 | 8.0 | 8.5 |
| S&M SBC (panel) | 24 | 435 | 100 | 114 | 130 | 170 | 212 | 96 | 122 |
| Revenue y/y | +32% | -30% | +77% | +40% | +18% | +12% | +10% | +10% | +17% |
| Nights y/y | | -41% | +56% | +31% | +14% | +10% | +8% | +8% | +10% |
| contribution to S&M growth: marketing / field (pp) | | | | 25.9 / 1.9 | 11.7 / 4.6 | 14.0 / 7.8 | **6.5 / 14.0** | 6.4 / 8.9 | **21.3 / 8.4** |
| inc. nights (m) per inc. marketing $M | | | | 0.30 | 0.31 | 0.18 | 0.30 | 0.28 | **0.10** |
| inc. revenue per inc. marketing $ | | | | 7.9 | 8.5 | 4.8 | 8.1 | 6.8 | **3.4** |

Quarterly marketing y/y (`_quarterly.csv`): 3Q23 +2%, 4Q23 +7%, 1Q24 +21%, 2Q24 +6%, 3Q24 +26%, 4Q24 +34%, 1Q25 +2%, 2Q25 +16%,
2H25 +10% (3Q25 10-Q not in the repo; 2H25 = FY25 - 1H25), 1Q26 +35%, 2Q26 +30%. Field ops 2H25 +56%. The field-ops cash figure
the line build uses ($781M = $993M - $212M SBC) assumes all S&M SBC sits in field operations; the 10-K does not say so.

The 2020 demonstration: with nights -41% and revenue -30%, brand & performance marketing was cut 58% while field operations & policy
rose 45% (severance and policy work). Marketing is the discretionary half; field operations is the sticky half.

**H5. Lead/lag with nights** (`43a_h5a_ccf.csv`; y/y log growth; lead > 0 = S&M earlier, nights later; band = 1.96/sqrt(n))

| series | sample | nights lead 2 | nights lead 1 | contemporaneous | S&M lead 1 | S&M lead 2 | S&M lead 3 | band |
|---|---|---|---|---|---|---|---|---|
| S&M cash | 1Q22+ (n 18) | 0.22 | 0.02 | **0.60** (0.66 arithmetic = Jessie) | 0.45 (R-style 0.23) | 0.65 (0.29) | 0.49 (0.18) | 0.46-0.51 |
| S&M cash | W1 (n 14) | **-0.64** (n 12) | -0.26 | **0.04** | 0.24 | 0.30 | 0.13 | 0.52-0.59 |
| S&M cash | W2 (n 10) | -0.05 | -0.59 | 0.42 | 0.60 | -0.19 | -0.48 | 0.62-0.74 |
| Marketing only (GAAP) | W1 (n 12) | -0.52 (n 10) | -0.13 | 0.23 | 0.28 | 0.11 | 0.30 | 0.57-0.62 |

Pre-registered rule ("this quarter's nights, not the next" needs contemporaneous r outside the band and leads inside, in 1Q22+ and
W1): **NOT supported** for either series. Jessie's 0.66 reproduces exactly (arithmetic y/y, R's ccf estimator) and comes from the
2022 quarters, where S&M and nights both lapped the 2021 reopening; inside W1 the contemporaneous correlation is 0.04. Partial
regression `g_nights ~ g_nights[-1] + g_sm + g_sm[-1] + g_sm[-2]` (n 16, all lags inside 1Q22+): g_sm 0.04 (t 0.4), lag 1 0.00,
lag 2 0.12 (t 1.6, p 0.11); only lagged nights growth matters (0.62, t 5.7). Exploratory, not pre-registered and not to be quoted as
a test: the W1 correlation of S&M growth with nights growth two to three quarters *earlier* is -0.60 to -0.64 (n 11-12, at the edge
of the band) — S&M growth rose after nights growth slowed in 2025, i.e. the spend reads as a response to deceleration, not a cause of
acceleration. With 27 correlations per series that could be noise.

**H5d. Where the incremental revenue came from** (`43a_h5d_regional_mix.csv`; disclosed regional revenue, panel)

| | FY23 | FY24 | FY25 | 1H25 | 1H26 |
|---|---|---|---|---|---|
| LatAm + APAC share of revenue | 16.8% | 17.7% | 18.9% | 20.6% | 22.0% |
| LatAm + APAC share of incremental revenue | 26% | 25% | 31% | 32% | 30% |
| North America revenue growth | +10.2% | +7.9% | +3.8% | +4.7% | +12.4% |

Modelled regional ADR, FY25-1H26 mean (`data/processed/adr/04_regional_quarterly_wide.csv`, **modelled, not disclosed**): NA $263,
EMEA $164, APAC $120, LatAm $97. The expansion markets carry ~30% of incremental revenue at 17-22% of the base and at ADRs less than
half North America's; that is consistent with "the spend buys lower-value nights" but it is a mix observation, not a marketing
attribution. Confounders named in the pre-registration and not removable at this n: the World Cup (2Q26 NA nights), RNPL (revenue
timing), FX (+1pp on 2026 revenue), the May 2025 Services/Experiences launch and the 2Q23 marketing front-load.

## Management statements that bear on it (all from `05_mgmt_statements_v2/05_statements.csv`, verbatim, with the ledger's file)

| id | date | who | statement | source file | what it means for Thesis 3 |
|---|---|---|---|---|---|
| S003 | 25 Feb 2021 | Chesky | "We don't intend to ever again spend the amount of money as a percentage of revenue on marketing in the future as we did in 2019." | `data/raw/transcripts/web/4Q20.html` | the 2020 cut was a policy choice: marketing is discretionary |
| S025 | 15 Feb 2022 | Stephenson | "we're continuing to focus more of our spend on brand marketing and less on the search engine marketing ... the brand marketing then should be more fixed. It's more of a fixed investment." | `data/raw/transcripts/ir/4Q21.pdf` | brand = fixed; the growth is a budget, not a per-night cost |
| S057 | 3 Aug 2023 | Chesky | "we'll have pretty consistent marketing spend as a percent of revenue over time because of the strength of the brand" | `data/raw/regulatory/transcripts/2023-Q2.pdf` | **missed**: 17.8% (FY23) -> 19.4% (FY25) -> 23.9% (1H26), cash basis |
| S094 | 6 Aug 2024 | Mertz | "From a performance marketing standpoint ... the ROI is very specific and relatively short-term. We think about that in terms of weeks and months, not quarters. In terms of brands, we think about that over a longer time horizon." | `data/raw/regulatory/transcripts/2024-Q2.pdf` | performance spend is same-quarter by management's own account; brand is not |
| S108 | 13 Feb 2025 | Mertz | "brand marketing ... is effectively a fixed amount of spend for each market in terms of the minimum amount that you need to spend for that market to be efficient." | `data/raw/regulatory/transcripts/2024-Q4.pdf` | every new market adds a fixed floor |
| S125 | 6 Aug 2025 | Mertz | "the increase in sales and marketing that you see associated with services and experiences is focused in particular on our field operations, our go-to-market activities and supply acquisition." | `data/raw/regulatory/transcripts/2025-Q2.pdf` | confirms FY25 = field ops (+43%) |
| S126 | 6 Aug 2025 | Mertz | "we continue to use performance marketing as a, I would say, surgical topper to the majority of our spend being in brand." | `data/raw/regulatory/transcripts/2025-Q2.pdf` | performance is the minority; the 1H26 +32% is therefore mostly brand/localised campaigns plus "paid growth" |
| S147 | 12 Feb 2026 | Mertz | "Where you will see some incremental investment to drive growth is, obviously, in sales and marketing. This is both in the form of programmatic marketing, but more so in terms of our go-to-market efforts." | `data/raw/regulatory/transcripts/2025-Q4.pdf` | 2026 guided as more go-to-market (field), yet 1H26 landed in marketing |
| 10-Q | 2Q26 MD&A | filing | S&M "increased $184 million, or 27%, primarily due to a $132 million increase in marketing spend, driven by higher paid growth marketing initiatives in emerging markets and partnerships, and a $48 million increase in payroll-related expenses driven by higher average headcount" (three months); six months: "increased $372 million, or 30%, primarily due to a $258 million increase in marketing spend, driven by higher paid growth marketing initiatives in emerging markets and partnerships, a $90 million increase in payroll-related expenses driven by higher average headcount, and a $10 million increase in third-party service provider expenses" | `docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq/abnb-20260630.htm` | the 1H26 step is paid marketing in expansion markets |
| V021 | 8 Sep 2026 | Chesky | "Nearly 90% of our traffic is direct or organic." | `data/raw/margin_build/05_mgmt_statements_v2/web/GS26.html` | why incremental-nights-per-marketing-dollar is a weak attribution: most nights are not bought |

## Replacement Thesis 3 evidence paragraph (every number traceable to the tables above)

> Sales and marketing is the cost line that has outgrown revenue for three years. Cash S&M compounded at 19% a year from FY22 to FY25
> against 13% for revenue, and the gap has widened every year: S&M growth minus revenue growth was -2pp in FY23, +9pp in FY24, +10pp in
> FY25 and +13pp in 1H26, taking cash S&M from 16.5% of revenue to 23.9%. Quarter by quarter, S&M has grown faster than revenue in 11
> of the 14 quarters since 1Q23 (mean gap 5.8pp a year, p 0.05) and 9 of the last 10 (8.9pp, p < 0.001). The spend is a budget, not a
> response to revenue: in growth terms S&M rises 12-17% a year at zero revenue growth and the revenue coefficient is small and unstable
> (0.4 on 18 quarters, insignificant on either window), and when revenue growth slowed in 2025 S&M did not (k_down -0.1 vs k_up +1.8,
> p 0.003, n 16). Each incremental S&M dollar has bought less every year: $7.6 of incremental revenue in FY22, $6.6 in FY23, $3.4 in
> FY24, $2.9 in FY25 and $2.7 in 1H26 (0.29m to 0.08m incremental nights per incremental $1M). The 2025 step was field operations
> (+43%, launch headcount management calls fixed); the 1H26 step is brand and performance marketing (+32%, "paid growth marketing
> initiatives in emerging markets and partnerships" per the 10-Q), where ~30% of incremental revenue now comes from LatAm and APAC at
> ADRs under half of North America's — so the FY27 base the Street expects to lever is one layer of payroll and one of paid growth that
> management has cut only once, in 2020.

(Six sentences; the last is the interpretive one. Drop the LatAm/APAC clause if the memo needs to avoid the modelled ADR.)

## Quotable statements

| # | statement | n / p | source | caveat |
|---|---|---|---|---|
| 1 | Cash S&M CAGR FY22-FY25 19.2% vs revenue 13.4% (ratio 1.44); FY23-FY25 20.6% vs 11.1% (1.86) | FY sums | `43a_h2c_cagr_ratio.csv` | cash = GAAP less SBC; GAAP S&M CAGR is 19.5% |
| 2 | S&M y/y growth exceeded revenue growth in 11 of 14 quarters since 1Q23 (mean +5.8pp/yr, HAC p 0.047, sign p 0.029) and 9 of 10 since 1Q24 (+8.9pp, p < 0.001, sign p 0.011) | 14 / 10 | `43a_h2b_growth_gap.csv` | pre-registered pass line, both windows; not true on 1Q22+ (12 of 18, p 0.27) because 2022 revenue outgrew S&M |
| 3 | S&M-minus-revenue growth gap -1.6pp (FY23), +9.2 (FY24), +9.9 (FY25), +12.8 (1H26); cash S&M 16.5% -> 17.8% -> 19.4% -> 23.9% of revenue | FY / 1H sums | `43a_h3_by_year.csv` | 1H26 is a half-year on a seasonally heavy S&M half; FY26 will be lower than 23.9% |
| 4 | Incremental S&M per incremental revenue dollar $0.15 (FY23), $0.29 (FY24), $0.35 (FY25), $0.38 (1H26) | FY / 1H | `43a_h3_by_year.csv` | ratio of increments; not a marginal cost |
| 5 | In y/y growth terms S&M rises 12-17% a year at zero revenue growth; the revenue coefficient is 0.41 (t 3.3, n 18) but 0.25 (SE 0.57, n 14) and 0.77 (SE 0.73, n 10) in the windows | 18 / 14 / 10 | `43a_h2a_growth_elasticity.csv`; M6 `c_sm` 0.155 | consistent with M6, which already calls `k_sm` unstable; quote the intercept, not k |
| 6 | Costs do not flex down: S&M k_down -0.12 vs k_up +1.83, p 0.003, n 16 (M6 T4) | 16 | `M6_cycle_flex_k_table.csv`, M6 note section T4 | M6's own caveat: directional, regime change inside the sample |
| 7 | Brand & performance marketing +10% in FY25 and +32% in 1H26; field operations & policy +43% in FY25 and +24% in 1H26; FY25's S&M growth was 14.0pp field / 6.5pp marketing, 1H26's is 21.3pp marketing / 8.4pp field | 10-K / 10-Q tables | `43a_h4_components_annual.csv`, `_halfyear.csv`; verified in `43a_h4_filing_verification.csv` | GAAP split (includes SBC); 3Q25/4Q25 only as 2H25 |
| 8 | Incremental revenue per incremental S&M dollar $7.6 (FY22), $6.6, $3.4, $2.9, $2.7 (1H26); incremental nights per incremental $1M 0.29m, 0.24m, 0.13m, 0.10m, 0.08m; both trends pass in W1 and W2 | 14 / 10 | `43a_h3_by_year.csv`, `43a_h3_acceleration.csv` | attribution, not causation (90% of traffic direct/organic, V021); confounded by ADR, FX, World Cup, RNPL |
| 9 | 2020: marketing -58%, field ops +45% with nights -41% — marketing is the discretionary half | 10-K FY2020 | `43a_h4_components_annual.csv` | one episode |
| 10 | Management said the ratio would stay flat (Chesky 2Q23, S057) and it did not; brand is "effectively a fixed amount of spend for each market" (Mertz 4Q24, S108) | ledger | `05_statements.csv` | quotes are verbatim from the ledger; file paths above |

## Statements in the current draft that must be dropped or reworded

| draft statement | verdict | why |
|---|---|---|
| "Regressing each cash cost line on revenue over Q1 2022 to Q2 2026 gives an S&M elasticity of 1.41 (95% CI 1.26 to 1.56)" | **drop the word elasticity and the CI** | it is a log-log levels regression on 18 trending quarters: DW 0.93, residual AR(1) 0.52; the coefficient equals the ratio of the two trend growth rates (1.44) within 0.03 in every sample; with a trend term it is 0.05 (CI -0.98 to 1.08); it rises to 1.61/1.70 as the window shortens. The CI also omits the small-sample correction (1.24-1.58 with it). Replace with statement 1 or 2. |
| "against 0.53 for operations and support, 0.49 for G&A, 0.86 for cost of revenue, and 0.87 for product development" | **reword in CAGR terms** | same regressions (product development DW 0.68; G&A SE 0.33, CI -0.16 to 1.14). FY22-FY25 CAGR vs revenue 13.4%: S&M 19.2%, PD 11.9%, COR 11.7%, G&A 10.7%, ops 8.2%. |
| "Sales and marketing is the one cost line that does not scale with revenue" | **reword** | true on the FY22 base; on the FY23 base product development (14.0% CAGR vs revenue 11.1%) also outgrew revenue. Say "the cost line that has outgrown revenue by the most". |
| "every 10% of revenue growth has cost 14% more marketing" | **drop** | implies a response coefficient; the growth-rate response is 0.41 and insignificant in both windows. The growth is an intercept (12-17%/yr at zero revenue growth). Say "S&M has grown about 1.4x as fast as revenue since FY22 (1.9x since FY23)". |
| "and this trend is accelerating" | **allowed as "the gap has widened every year"** | pre-registered test passes both windows, but FY24 -> FY25 was +0.7pp; the acceleration is the 1H26 step (+12.8pp). Quote the by-year numbers, not the trend p-values (smooth T4Q series). |
| "So marketing is paying for this quarter's nights, not the next" | **drop** | not supported: contemporaneous r 0.04 in W1 (n 14), 0.23 marketing-only (n 12), all lead correlations inside the band; Jessie's 0.66 is a 1Q22+ artefact of the 2022 reopening year. Replace with the falling-efficiency numbers (statement 8), which say what the memo wants without the timing claim. |
| Headline "High costs associated with S&M that are dropping slower than the market is modeling" | **keep the idea, fix the words** | S&M is not "dropping" anywhere in the data; it is rising as a share of revenue. The Street's FY27 implies S&M +9.5% / 21.0% of revenue (C4 dossier, Street-implied residual) against a line that has grown 20%+ for two years. Say "rising faster than the market is modelling". |

## What failed or is weak

- H5a failed as pre-registered (both series). The sentence about timing has no support at this n and is dropped.
- The trailing-4Q trend tests (H3, H5c) pass with implausibly large t-statistics; the series are four-quarter sums and HAC(3) on 10-14
  points does not remove that. They are reported as directional; the annual table is the evidence.
- "Efficiency" ratios attribute every incremental night/dollar to S&M. Management says ~90% of traffic is direct or organic (V021), so
  the level of the ratio means little; only its direction is quoted, and even that is confounded by ADR, FX, the World Cup and RNPL.
- The component split is GAAP (includes SBC, $212M in FY25); the cash field-ops number used elsewhere assumes all S&M SBC is field ops.
- 3Q25 and 4Q25 component values are not separable (3Q25 10-Q not in the repo); 2H25 is used.
- Regional ADR is modelled. The regional revenue shares are disclosed.
- W2 is a subset of W1, and the windows were fixed by CLAUDE.md, not chosen here; the 1Q22+ sample is Jessie's.
- The exploratory negative correlation of S&M growth with nights growth 2-3 quarters earlier (W1, r -0.6, n 11-12) is one of 27
  correlations per series and is not a finding.

Parameter count: levels regressions 5 (6 with trend) each, 13 fitted; growth regressions 2 each, 3 fitted; gap means 1 each; trend
tests 2 each, 10 fitted; partial regression 5. Zero forecasts; every pass line pre-registered in `43a_prereg.md`.

## Commands

```
py -3.13 -X utf8 analysis/src/margin_build/43a_sm_evidence/run.py      # exit 0; prints every table; writes 17 CSVs
git -C . show origin/jessie/r-stats:analysis/r_stats/R/04_regressions.R   # the spec being reproduced
git -C . show origin/jessie/r-stats:analysis/r_stats/tables/05_cost_elasticities.csv
```

## RESUME

Done for the 2 Oct memo: use the replacement paragraph and the quotable table above; drop the 1.41 elasticity, the "10% costs 14%"
sentence and the "this quarter's nights" sentence. Next agent: (1) if the 3Q25 10-Q is added to the repo, split 2H25 into 3Q25/4Q25 in
`QTR` in `run.py` and re-run (the quarterly marketing y/y then covers 1Q23-2Q26 without a gap); (2) on 5 Nov append 3Q26 to the panel
and re-run — the live question Thesis 3 poses is whether 3Q26 marketing grows more than ~20% y/y against the 3Q25 base of $585M cash
S&M (a print above the +25% the line build carries would extend the 1H26 step, below +15% would mean management is already flexing);
(3) do not re-run Jessie's levels regression on a longer window and quote it — every extension makes the trend ratio, not an elasticity;
(4) 43b/43c/43d are the other three legs of the same Thesis 3 pass and were written in parallel; reconcile the memo wording once.
