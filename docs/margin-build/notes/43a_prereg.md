# Pre-registration for 43a_sm_evidence (sales & marketing statistics behind Thesis 3)

Written 22 Sep 2026 (evening) by Krish with Claude (Fable 5.1), before any test below was run and before
`analysis/src/margin_build/43a_sm_evidence/run.py` existed. Branch `krish/cost-leg`, worktree `citadel-abnb-marginaudit`.

**What was already seen before writing this** (all of it in the repo, none of it computed by me):
Jessie's `05_cost_elasticities.csv` (S&M levels elasticity 1.409, NW SE 0.075, DW 0.93, n 18) and `09_sm_vs_nights_ccf.csv`
(contemporaneous 0.66, leads <= 0.27); M6's k-table (`k_sm` 0.418 t 2.25, `c_sm` 0.155, asymmetry k_up +1.83 / k_dn -0.12,
p 0.003, n 16; `k_sm` 0.87 at the 2022 vintage, 0.27-0.42 since 2025); the 10-K/10-Q S&M split tables (brand & performance
marketing vs field operations & policy) as printed in the cached filings; the 05_statements ledger entries on marketing; and the
41/42 notes and Codex audits. I have not computed any regression, correlation, CAGR, trend, or efficiency ratio on the panel.

**Data.** `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (1Q19-2Q26; `sm_cash` = GAAP S&M less S&M SBC;
`revenue`, `nights_m`, `gbv_busd`, `adr_usd`, regional revenue `rev_na/emea/latam/apac` from 1Q22). Component split from the
filings cached in the repo: 10-Qs at `docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq/abnb-20230630 ... 20260630.htm` (2Q23, 3Q23, 1Q24, 2Q24, 3Q24, 1Q25, 2Q25, 2Q26) and 10-Ks at `C:/Users/krish/citadel-abnb/data/raw/filings/abnb_10k_FY2020..FY2025.htm`
(main tree, read-only). The 3Q25 10-Q is not in the repo, so 3Q25 and 4Q25 components are only available as 2H25 (FY25 minus 1H25);
1Q22 = 1H22 - 2Q22; 4Q22/4Q23/4Q24 = FY - 9M. Components are GAAP (they include S&M SBC; SBC sits almost entirely in field
operations, which is payroll). Regional ADR is the modelled series in `data/processed/adr/04_regional_quarterly_wide.csv` and is
flagged as modelled wherever used.

**Windows.** Per CLAUDE.md, W1 = observations dated 1Q23-2Q26 (n 14), W2 = 1Q24-2Q26 (n 10). For y/y growth series the observation
date is the later quarter. A result is quoted only if it passes in both. Jessie's 1Q22-2Q26 (n 18) is reported for reproduction only.
HAC = Newey-West; lag 2 for quarterly-level regressions (matching Jessie), lag 3 for y/y series (overlap). One-sided p unless stated.

## H1. What the 1.41 is (reproduction and decomposition; no pass line, descriptive)

- H1a Reproduce: `log(sm_cash) ~ log(revenue) + quarter dummies`, 1Q22-2Q26, OLS, NW(2). Expect 1.41 +- 0.02 and DW ~0.93.
- H1b Trend ratio: fit `log(sm_cash) ~ t + quarter dummies` and `log(revenue) ~ t + quarter dummies` on the same 18 quarters. The
  ratio of the two trend slopes is the "ratio of trend growth rates". **Stated expectation:** the levels elasticity is within 0.15 of
  this ratio, i.e. it is mostly two trends divided, not a response coefficient.
- H1c Add a linear trend to H1a: `log(sm_cash) ~ log(revenue) + t + quarter dummies`. **Stated expectation:** the log(revenue)
  coefficient loses significance (its 95% NW interval includes 1, or its sign is unstable).
- H1d Residual diagnostics: DW, residual AR(1) coefficient, Breusch-Godfrey p; ADF on the residual (Engle-Granger, small-n caveat).
  With DW < 1.2 the levels regression is reported as "spurious-regression risk: high".
- H1e Windows: same H1a spec on W1 (n 14) and W2 (n 10), to show how far the coefficient moves with the sample.

## H2. Growth-rate version: does S&M grow faster than revenue? (pre-registered pass line)

Series: `g_sm = log(sm_cash_q / sm_cash_{q-4})`, `g_rev = log(revenue_q / revenue_{q-4})`. Seasonality-free by construction.

- H2a Elasticity in growth rates: `g_sm ~ c + k g_rev`, HAC(3), on 1Q22+ (n 18, to match M6), W1, W2. Reported; expected k
  well below 1.41 (M6 has 0.42). No pass line (M6 already owns this coefficient and calls it unstable).
- H2b **The quotable claim.** Growth gap `d = g_sm - g_rev` (log points). **Pass line:** mean d > 0 with one-sided HAC(3) p <= 0.10
  in BOTH W1 and W2, and d > 0 in at least 10 of 14 (W1) / 7 of 10 (W2) quarters. If it passes, the memo may say "S&M has grown
  faster than revenue in X of 14 quarters since 1Q23, by a mean of Y pp a year". If it fails, the memo may only quote the annual
  CAGR ratio as a description.
- H2c CAGR ratio: (FY22->FY25 S&M cash CAGR) / (FY22->FY25 revenue CAGR); the same for FY23->FY25, and 1H24->1H26. Descriptive.
  This is the number I expect the memo to quote in place of 1.41 for "every 10% of revenue growth has cost X% more marketing".

## H3. "This trend is accelerating" (pre-registered pass line)

Three measures, each on trailing-4Q sums (T4Q) so seasonality cancels:
- (a) S&M cash share of revenue, T4Q;
- (b) incremental S&M per incremental revenue dollar, T4Q y/y: `(sm_T4Q - sm_T4Q[-4]) / (rev_T4Q - rev_T4Q[-4])`;
- (c) growth gap of T4Q sums: `log(sm_T4Q/sm_T4Q[-4]) - log(rev_T4Q/rev_T4Q[-4])`.
Test: OLS of each measure on a time index, HAC(3), one-sided for slope > 0, in W1 and W2.
**Pass line for "accelerating":** measure (c) slope > 0 with p <= 0.10 in both windows. (a) and (b) are reported alongside. If
(c) passes in W1 only, the memo says "rising", not "accelerating". A by-year table (FY22-FY25, 1H25, 1H26) is reported regardless.
Stated expectation: (a) passes (share is rising is already visible in the ledger: 18.05 -> 17.78 -> 19.35 -> 21.14 -> 25.87); (c) is
uncertain because FY24 and FY25 gaps may be similar and 1H26 is one half-year.

## H4. Component split: which piece drives the excess growth? (descriptive)

By FY19-FY25 and 1H25/1H26 (and quarterly where available): brand & performance marketing (B&PM) and field operations & policy (FOP),
levels, y/y growth, share of revenue, and each component's contribution (pp) to `S&M growth - revenue growth`.
Stated expectation: FY25's excess is FOP (the launch teams, +43%); 1H26's excess is B&PM (+32%, the emerging-market paid growth).
Also the 2020 cut (B&PM -58%, FOP +45%) as the historical demonstration that marketing is discretionary and field ops is not.
No pass line. Consistency check: B&PM + FOP = GAAP S&M in the panel for every period parsed (tolerance $2M rounding).

## H5. "Marketing is paying for this quarter's nights, not the next" (pre-registered)

- H5a Cross-correlations of `g_sm` (and `g_bpm`, marketing-only, where quarterly data exist) with `g_nights = log(nights_q/nights_{q-4})`
  at lags -4..+4 (negative = S&M leads nights), samples 1Q22+ (n 18, to reproduce Jessie's 0.66) and W1 (n 14). The 95% band is
  1.96/sqrt(n). **Pre-registered reading:** the sentence "paying for this quarter's nights, not the next" is supported ONLY if the
  contemporaneous r exceeds the band AND every lead r (lags -1, -2) is below the band in both samples. If the contemporaneous r is
  inside the band in W1, the honest reading is "no measurable relation at this n", and the memo must not assert either direction.
- H5b Partial version: `g_nights ~ g_nights[-1] + g_sm + g_sm[-1] + g_sm[-2]`, HAC(3), n 16. Reported only; n too small for a pass line.
- H5c Marketing efficiency: incremental nights (m) per incremental $1M of B&PM and incremental revenue ($) per incremental $1 of
  S&M cash, by year FY22-FY25 and 1H26 vs 1H25, plus T4Q. **Pass line for "efficiency is falling":** the T4Q incremental revenue
  per incremental S&M dollar regressed on time has slope < 0 with p <= 0.10 in both windows. Expectation: passes W1, uncertain W2.
- H5d Mix: share of incremental revenue coming from LatAm + APAC by year (panel regional revenue) and modelled regional ADR
  (flagged modelled). Descriptive: does the 2025-26 spend coincide with low-ADR regions carrying more of the incremental revenue?
  Confounders named in advance: World Cup (2Q26 nights, North America), RNPL (revenue timing), FX (2026 tailwind), the May 2025
  Services/Experiences launch, and the 2Q23 Easter/marketing front-load.

## What will be quoted, decided in advance

- The 1.41 is not to be quoted as an elasticity. If H1b holds, it is described as "the ratio of two trends".
- The number for "S&M grows faster than revenue" is the H2c CAGR ratio and/or the H2b mean gap, with n and p.
- "Accelerating" only if H3(c) passes both windows; otherwise "rising".
- "This quarter's nights, not the next" only under the H5a rule; otherwise it is dropped.
- M6's asymmetry (p 0.003, n 16) may be quoted as the repo's existing evidence that S&M does not flex down, with its n.
- Nothing on the kill lists (AGENT_BRIEF section 6; SYNTHESIS section 9): in particular not "Airbnb has no cost dial", not any
  "survives both windows" phrasing as evidence of skill.

Parameter count: H1a 5 (1 slope + 4 dummies incl. intercept), H1c 6, H2a 2, H3 2 per measure, H5b 5. Nothing here is a forecast.
