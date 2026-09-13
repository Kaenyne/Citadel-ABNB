# V — Valuation reconciliation

Partial — arithmetic replication and the one-screen exhibit pass; fully verified point-in-time source vintages and a justified translation from a change coefficient to an exit-multiple level do not. Agent sub-V; 12 September 2026 (results completed 13 September UTC); branch `codex/lane1-full`. The pass line below was written before regressions, price mappings or network refresh were run.

## Pre-registered pass line — 2026-09-12 23:33 UTC

Every number on the page traces to a file or a shown calculation; the growth-to-multiple slope reproduces within its confidence interval; the page fits one screen. Reproduce the supplied monthly 12-month-change regression, with EV/LTM adjusted EBITDA as dependent variable, forward-growth proxy, 10-year Treasury yield and Nasdaq forward P/E as regressors, an intercept, and Newey–West covariance with 12 lags. The reference is approximately +0.48 turns per percentage point of forward growth. Also report the forward-multiple level regression and W1/W2 monthly diagnostics. No sign or significance screen is used to select a specification.

Strict dated-data validation is separate from arithmetic replication: quarterly quarter-end multiples using the same quarter's later-reported accounts are excluded. Supplied monthly series alone cannot establish source publication vintages. Expanding guide-date fits use only earlier month-end rows and are labelled inherited-vintage diagnostics unless every source stamp can be verified. A successful numerical replication cannot repair a provenance failure.

Growth scenarios are the brief's 9.18%, 10.35%, 11.52%. Change-regression slope is used only as a *conditional sensitivity* anchored to the existing 16.5x multiple at the final FY27 base-model growth, never as an independently estimated fair-multiple intercept. Price = (multiple × FY27 adjusted EBITDA + FY27 net cash) / FY27 modelled diluted shares. Keep these annual-model inputs fixed across the growth sensitivity to isolate the multiple channel; no direction is recommended.

The one-page exhibit and supporting audit will be produced by the new `valuation_v1` package. No existing file, licensed export, frozen harness file or existing registry entry will be modified. No price forecast will be forced into the revenue harness.

## What ran

Run from the repository root with its `.venv` interpreter:

```text
python -X utf8 analysis/src/forecast_methods/valuation_v1/run.py
python -X utf8 analysis/src/forecast_methods/valuation_v1/run.py --refresh
python -X utf8 -m pytest analysis/src/forecast_methods/valuation_v1/tests -q
```

Final rebuild exit 0; six package tests passed in 5.01 seconds. Initial arithmetic run exit 0 in 0.55 script seconds; public refresh exit 0 in 6.06 script seconds. Rendering initially failed because Matplotlib interpreted literal dollar signs as math delimiters; disabling math parsing repaired it, and the complete render/rebuild exited 0. The final exact script runtime and public snapshot are in `data/processed/forecast_methods/valuation_v1/final_run_receipt.txt`. The 1920×1080 standalone PNG was visually reviewed; a one-page PDF and Markdown exhibit accompany it. A local read waited approximately 22 minutes inside the tool before completing; no data or source was mutated during that wait. Measured elapsed time from the first captured clock (23:31:37 UTC) to final checks (00:22:24 UTC) was 50m47s, including that wait. Actual token usage is unavailable from this runtime.

## Results

Compact exhibit: `data/processed/forecast_methods/valuation_v1/valuation_page.pdf` (also `.png` and `.md`). Every source input has a SHA-256 entry in `input_manifest.json`. Tables below are descriptive arithmetic, not adopted target prices.

| Diagnostic | W1 n | W1 slope [HAC 95% CI] | W2 n | W2 slope [HAC 95% CI] |
|---|---:|---:|---:|---:|
| 12-row change in EV/LTM adjusted EBITDA versus forward-growth proxy change; controls: rate and Nasdaq multiple | 35 monthly changes / 12 reported quarters | +0.4860 [0.3172, 0.6548] | 33 monthly changes / 12 reported quarters | +0.4765 [0.3100, 0.6431] |
| EV/NTM EBITDA level versus forward-growth proxy level; same controls | 45 months / 16 reported quarters | +0.4825 [0.1182, 0.8468] | 33 months / 12 reported quarters | +0.1948 [−0.3233, 0.7129] |

Four parameters per regression. The pre-registered +0.48 reference falls within the reproduced change-regression interval; the supplied reference coefficient is 0.486 rounded to three decimals. Monthly observations overlap and share accounting releases; n is not the number of independent events. W1/W2 in this table are calendar-start restrictions on **monthly diagnostics**, not the harness's 14/10 scored quarterly forecasts. Guide-date expanding refits separately cover 14/10 origins, with sufficient training data at 8/7 and abstentions at 6/3. Zero forecasts are counted as fully vintage-verified scored W1/W2 cells. There is no baseline for a price/multiple ratio in the frozen harness.

The monthly file's reported-quarter labels pass the frozen-calendar publication-date check on 47/47 eligible rows. The quarterly file explicitly pairs quarter-end prices with accounts reported about five weeks later, so it is excluded from the regression. Monthly component vintages, including the forward-growth proxy and Nasdaq valuation input, are not independently documented in the supplied CSV. A date-label check cannot certify those components. All training rows in guide-date fits precede their origin strictly, but this does not repair missing source vintages. New current analyst targets are used only in the positioning panel, never in a historical regression or historical Street forecast.

| FY27 growth sensitivity (n=1 each) | Conditional multiple | Conditional price | Basis |
|---|---:|---:|---|
| 9.18%, w=0.33 | 15.4655x | $170.64 | Fixed final base EBITDA/cash/shares; anchored to 16.5x at 11.3086% growth |
| 10.35%, w=0.50 | 16.0341x | $176.27 | Same |
| 11.52%, w=2/3 | 16.6027x | $181.89 | Same |

Arithmetic: `x = 16.5 + 0.4860216575 × (g − 11.3086)`; `price = (x × 5685.7698 + 10115.9869) / 574.5982`. Dollar inputs are USD millions. These are conditional multiple-channel sensitivities, not confidence bounds on price. Holding EBITDA fixed while varying revenue growth deliberately omits the operating-profit channel. The anchor is an existing model scenario, not a regression-estimated fair intercept. Even a correct change-regression slope does not justify applying it unchanged to a FY27 exit level.

| Existing scenario (n=1 each; six field lenses) | Final-model EBITDA multiple/lens price | Six-lens field mean [range] | Memo v0 event analogue (2 endpoints) |
|---|---:|---:|---:|
| Bear | 13.5x / $108.46 | $74.18 [$37.23–108.46] | $140–152 |
| Base | 16.5x / $180.88 | $156.79 [$110.58–196.92] | $170–185 |
| Bull | 18.5x / $234.16 | $228.18 [$176.49–281.01] | $205–215 |

These rows align ranks for comparison, not identical assumptions. All three final-model EV/EBITDA prices reproduce `13_valuation_summary.csv` to less than $0.001. The older exit-recommendation file uses different EBITDA, cash and share inputs and yields $136.955/$191.317/$242.235. The memo connects its bull branch to approximately two points of growth and one multiple turn but supplies no exact remaining EBITDA/cash/share bridge; its base and bear branches have no full numerical derivation. No bridge has been invented to force agreement.

Public positioning refresh: Yahoo Finance via yfinance, retrieved **2026-09-13 00:18:59 UTC**, [public quote page](https://finance.yahoo.com/quote/ABNB/). The last regular-session close is **$170.1900 on 11 September**. Yahoo's 31 August short-interest snapshot is **14,228,547 shares, 3.44% of float, 2.56 days**. Current target snapshot: **40 analysts**, mean **$182.125**, median **$185**, range **$125–220**. Per-target publication stamps and the current target standard deviation are unavailable; retrieval time is not backdated to 12 September or any guide date. The earlier supplied 6 September actions panel has **21 Buy / 11 Hold / 2 Sell, n=34** and target SD/mean **0.131, n=31**. These populations differ from the older 46-analyst prose summary; their values are not pooled.

## Three inconsistencies left for the team

1. A change relation involving an LTM denominator does not determine an FY27 exit multiple. The W2 forward-multiple level coefficient includes zero in its interval; a universal causal +0.48 rule is unsupported.
2. The preliminary exit recommendation, final model's single EBITDA lens, and six-lens football field are different arithmetic objects with different input sets. The base values $191.317, $180.88 and $156.79 cannot be interchanged.
3. Event analogues have a different horizon and an incomplete earnings/cash/share bridge. At fixed final base inputs, one turn adds only $9.89. The adopted ~30 September 2027 model convention and weighted-average diluted-share proxy remain labelled; this package makes no team decision.

## Proposed memo sentence — exactly one

“Using the final FY27 base model, 16.5x adjusted EBITDA implies a $180.88 12-month target, while the existing six-lens base football-field mean is $156.79; these are different valuation objects.”

Evidence: `football_field_reconciliation.csv`, `13_model_annual.csv`, `13_valuation_summary.csv`, and `model/assumptions.md` model conventions. Caveat: arithmetic on existing model scenarios, not an independently validated valuation recommendation; W1/W2 forecast performance is not applicable to this accounting sentence.

## What failed or remains unavailable

Full source-vintage verification is incomplete; the strong claim that growth uniquely or causally determines the multiple is not supported. Current target dispersion is limited to the range, with no current SD; the rating split remains explicitly dated 6 September. The current market snapshot is not a historical guide-date consensus input. New reserved method name `valuation-v1` is not registered because the frozen harness has no annual equity-price or multiple target; forcing it into a revenue target would be invalid. Parent owns scorer runs and workboard changes. No frozen package, existing note, licensed export or source data file was modified.

## RESUME

Refute the exact proposed accounting sentence against the new output and its raw model/valuation inputs. Keep the conditional $170.64–181.89 growth sensitivity labelled as an anchored scenario, and never promote the inherited-vintage regression to a causal or scored PIT forecasting result. Further valuation work needs a dated component-vintage reconstruction and an explicit operating-profit/cash/share/horizon bridge chosen by the team; this package does not make that choice. Rebuild from the repository root with the commands above; `--refresh` updates only this package's public snapshot and outputs.
