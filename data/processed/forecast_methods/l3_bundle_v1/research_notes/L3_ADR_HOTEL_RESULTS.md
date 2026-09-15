# L3 ADRv3 and hotel comparisons — reproduction and identification audit

Agent `adr_hotel` · 2026-09-13 · branch `codex/lane3-full`, starting commit `1c87628cedbc94ab8a0e8552743c94485ef353b8` · all work in new `l3_adr_hotel_v1` source/output folders · approximately 35 minutes.

## Verdict

**Implementation PASS; original descriptive ADR research PASS; guide-date PIT evidence NOT ESTABLISHED; hotel pricing transmission and hotel onboarding demand UNIDENTIFIED; investment adoption PENDING.** The frozen ADRv3 numbers reproduce. The key qualification is stronger than “small sample”: the historical model uses realised quarter-t geographic, size and LOS mix, and retrospectively calibrated fixed FX estimators. These are descriptive walk-forward results conditional on information unavailable at a historical guide date. They cannot substantiate a PIT forecasting edge. The adapter exports conditional research inputs with this limitation, not a chosen card or combined ABNB forecast.

Preregistration: [L3_ADR_HOTEL_PREREG.md](L3_ADR_HOTEL_PREREG.md). No preregistered hurdle was changed after execution.

## What ran

From `.worktrees/lane3-full`:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_adr_hotel_v1/run.py
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/l3_adr_hotel_v1 -p 'test_*.py' -v
```

Runner exit 0, about 9 seconds after initial dependency load; tests exit 0, 12/12 in 0.084 seconds. Independent score implementation reproduces the stored paths. The first runner also passed; two additions subsequently made the preservation of failed L/M additions and the identification ledger explicit. No source writer or original P1 script was executed. No ABNB collection, licensed data, teammate contact or registration occurred. The public FRED metadata page was checked read-only; newly posted August data were not imported into this frozen-source audit.

## Integrity and arithmetic

| Check | n | Result |
|---|---:|---|
| P1 model/target/window/FX reproduction | 16 | max delta 2.22e-16 over n, RMSE, naive denominator/ratio, jackknife limits |
| Independent stored-path scoring | 16 | max delta 3.33e-16 |
| J3 reproduction | 32 | max delta 8.88e-16, required <0.001 |
| Historical residual identity | 14 | max delta 8.88e-16 pp |
| Historical imposed K rule | 10 | max delta 6.25e-16 pp |
| Live card rounded arithmetic | 126 checks, 18 card rows | all within stated final rounding tolerance |
| Frozen source hashes | 29 | unchanged before/after |
| Integrity/reproduction gates | 14 | all pass |
| Adapter uniqueness/date/FX contracts | 86 rows | pass |

`checks.csv`, `source_manifest.csv`, `adr_card_identity.csv` and `adr_identification_audit.csv` retain the receipts. Source paths are repository-relative for portability; hashes are actual file bytes, not normalized text. The runner makes no source writes.

## What the original ADR result does and does not establish

These windows are **ADR-A = 2024Q1–2026Q2 (n=10)** and **ADR-B = 2024Q2–2026Q2 (n=9)**. They are not the ABNB harness W1/W2. The original pass rule requires ratio to naive and every drop-one ratio below one on reported dollar ADR growth, under both the euro and basket estimators, on both ADR windows.

| Rule | FX | ADR-A ratio; jackknife max (n=10) | ADR-B ratio; jackknife max (n=9) |
|---|---|---|---|
| Last-quarter residual + measured mix | euro | 0.916; 0.969 | 0.905; 0.989 |
| Same | baskets | 0.876; 0.918 | 0.871; 0.924 |
| Same | midpoint | 0.893; 0.945 | 0.882; 0.955 |
| Same + imposed K | euro | 0.912; 0.966 | 0.898; 0.984 |
| Same + imposed K | baskets | 0.873; 0.916 | 0.868; 0.921 |

Both original variants retain PASS 4/4 on their stated descriptive criterion. The binding plain-rule jackknife margin is 0.010916. The midpoint is a comparison estimator, not one of the four required checks.

The original rounded-ex-FX target remains 0.9847 / 1.0801 (n=10/9) for both variants, with jackknife maxima 1.0801 / 1.1832. The separately preregistered +/-0.5 interval sensitivity scores continuous predictions to the disclosed intervals: plain-rule ratios 0.7951 / 0.7451 and with-K 0.7882 / 0.7328 (n=10/9). This illustrates target/scoring dependence; it is not a new original-rule verdict, a main-harness score or a PIT claim. Actual targets in these scored windows are integers, but 3Q23/4Q23 history contains 0.5 and the 1Q24 naive is 0.5. The frozen scoring was preserved exactly rather than silently converting that history to integers.

Reasons these ratios cannot be promoted to guide-date evidence:

- `S1_scoring.v2_components` directly reads quarter-t `geo_mix_pp`, `unit_size_pp` and `los_mix_pp`. The original S note calls this the upper bound on the proposed mix measurement. Lagging only the residual does not make the entire input path PIT.
- The FX routine fixes the euro intercept/slope at -0.5687/0.4512 from the ex21 n=17 fit; it applies FY2025 regional GBV weights and fixed regional pass-through to older quarters. It also uses complete target-quarter FX averages. No historical per-guide-date re-fit or source-vintage register is supplied here.
- `last_q` was selected after inspecting J3's sensitivity table. Its later v3 preregistration is documented, but does not erase that selection.
- The K cohort path is calibrated from 2026 calls and assumed regional/nights-per-listing mappings. The original path is not a measured history of fee-migrating revenue cohorts.
- The reported-minus-ex-FX-minus-FX gap reaches 0.0422398 pp in absolute value (n=14), slightly above a literal 0.04 cutoff. The original rounded “0.04” wording is reasonable to two decimals; the exact values are recorded. The source note says several FX effects were solved from the identity, so a tight identity is not independent FX validation.

No parameters were fitted in this audit. The plain residual rule has one prescribed lag/carry choice, three supplied mix components and two supplied fills. K adds one imposed coefficient (0.007, with 0–0.038 sensitivity), plus its inherited assumed cohort schedule. FX inherits two fitted euro coefficients or fixed four-region shares, currency baskets and regional pass-through coefficients. Spearman/Pearson diagnostics introduce no forecast parameters. These inherited choices and post-hoc rule selection must accompany any statement about parsimony.

## Residual, mix, fees, FX and nights reconciled

| Scenario, midpoint FX | 2026Q3 (one quarter) | 2026Q4 (one quarter) |
|---|---:|---:|
| Carried unobserved residual | 4.849326 pp | 4.849326 pp |
| Geo + size + LOS | -0.575490 pp | -0.575490 pp, carried |
| New business + interaction fills | -0.582570 pp | -0.582570 pp |
| Ex-FX ADR without K | 3.691266% | 3.691266% |
| Imposed K increment relative to flat Q2 residual | 0.171500 pp | 0.374500 pp |
| Ex-FX ADR with K | 3.862766% | 4.065766% |
| ADR FX | -0.430000 pp | +0.150000 pp |
| Reported ADR without / with K | 3.261266% / 3.432766% | 3.841266% / 4.215766% |
| ADR dollars without / with K | $176.88 / $177.17 | $173.94 / $174.57 |

The geo contribution is -1.428426, size +0.796672, LOS +0.056264 pp. The source explicitly labels geographic and LOS mappings as unvalidated; “measured” should never be read as direct measurement of their contribution to consolidated Airbnb ADR. Historical new-business cells are missing in eight 2023–2024 quarters and treated as zero by the original component identity; the audit retains that fact. The residual includes omitted composition and reconstruction error, so it is not observed like-for-like pricing.

K uses 0.007 × 24.5 = 0.1715 pp for Q3. Q4's **cumulative** increment is 0.007 × (75.0 − 21.5) = 0.3745 pp; its Q4-only addition is 0.2030. The high mechanics bounds are 0.9310 / 2.0330 pp. L4 must not add Q3's 0.1715 to the already cumulative Q4 number again. The fitted coefficient 0.114074 per pp of share, about 16.30 times central mechanics (n=14, four nonzero cohort observations), remains rejected as fee identification. A fitted time-window association does not measure mandatory-cohort pass-through.

The regional primary addition remains FAIL 0/4 and the primary new-listing addition remains FAIL 2/4 improvements (history n=14). Their model coefficients and failed forecast numbers are not in the L4 adapter. The reported ADR, ex-FX ADR and dollars are alternative representations of the same scenario, not additive components. RSS bands are scenario ranges, with no coverage probability asserted.

All 18 card rows reproduce `GBV = nights × ADR`, including Q3 146.8m nights and Q4 131.8m or 132.7m nights. Those are inherited alternative assumptions; L3 adopts neither. The contemporaneous `GBV × prior-year same-quarter take rate` revenue comparison also reproduces, but is deliberately omitted from the adapter. It is not the seasonal lagged-GBV revenue kernel and cannot replace L4's guide forecast. Reported ADR/GBV already contains its named ADR FX; no full FX factor may be layered on again.

## Hotel comparisons and robustness

The archived monitor reconstructs from 42 nonmissing US CPI lodging growth observations and 43 BEA hotel-price observations, January 2023–July 2026. Maximum differences from the monitor are 0.04926/0.04946 pp, entirely consistent with its one-decimal rounding. October 2025 CPI is absent, making Q4 2025 incomplete. Q3 2026 has only July (1/3 months) and is not exported as a complete-quarter value. Quarterly comparisons use the mean of three monthly growth rates; they are neither hotel ADR observations nor transaction-weighted Airbnb rates.

| Comparator vs Airbnb ex-FX ADR | Full history r; n | ADR-A r; n | ADR-B r; n | Change-in-growth r, ADR-A; n |
|---|---|---|---|---|
| US CPI lodging | 0.132; 13 | 0.475; 9 | 0.467; 8 | 0.009; 7 |
| BEA hotels/motels price | 0.011; 14 | 0.272; 10 | 0.273; 9 | -0.010; 9 |

On ADR-A the CPI Pearson drop-one range is 0.012–0.601, Spearman 0.316; BEA is -0.295–0.441, Spearman 0.000. Growth changes remove almost all positive contemporaneous ex-FX association. Against reported Airbnb ADR, ADR-A correlations are only 0.078 (CPI n=9) and -0.186 (BEA n=10). These diagnostics do not establish pricing transmission or a forecast addition. Overlapping y/y growth, geography/product mismatch, small n and unreconstructed release vintages preclude causal or PIT readings. All 24 specifications are retained, including weak and negative results, without choosing a winner.

Q1 2026 complete-quarter mean growth is CPI -0.148%, BEA -2.190%; Q2 is +4.722%/+4.960% (three months each), while Airbnb ex-FX is +4% in both quarters. This contrast illustrates why a common pricing story is insufficient. Source definitions: [FRED's BLS lodging CPI](https://fred.stlouisfed.org/series/CUSR0000SEHB) is a monthly seasonally adjusted US index; [BEA underlying NIPA tables](https://apps.bea.gov/national/Release/XLS/Underlying/Section2All_xls.xlsx) supply hotels/motels PCE price indices. The archived files and source table `research/sources/README.md` retain their historical snapshot. The live FRED page was checked on 13 September and already displays August; this audit intentionally keeps the committed July dataset and does not assert latest-data coverage.

The separate hotel supply panel reproduces 13 markets, 113 existing page observations and 111 property clusters, with observed pages in only 4/13 markets. There are 26 accepted registered-room links covering 1,060 rooms. **0/13 markets have actual Airbnb hotel nights, hotel revenue or current verified independent-room totals.** Those missing values are not zeros. The 13 capacity references combine rooms, licenses, properties, different boundaries and dates, so no capacity sum, occupancy inference, incremental-demand estimate or national Airbnb hotel forecast is defensible. These are comparators and supply context only.

## L4 delivery and limitations

`data/processed/forecast_methods/l3_adr_hotel_v1/l4_adr_hotel_inputs.csv` contains 86 uniquely keyed rows: conditional ADR replacements, their descriptive component breakdowns, GBV identity comparisons and complete/missing hotel comparator rows. Every row has units, information date, evidence status, source, treatment, the baseline replaced, embedded FX and limitations. Audit information date is 2026-09-13; ADR source snapshot 2026-09-11 is stated separately. No probabilities, revenue guide, trade direction, card adoption or registry entries are supplied. L4 should use only the commit published by the lead, not assume visibility into this working tree.

What could not be done: no historical mix/FX vintage reconstruction, no identification of true like-for-like price or mandatory-cohort fee pass-through, no actual hotel production outcomes, no August refresh in this frozen audit, and no chosen nights baseline. These affect the corresponding claims, not the completed reproducible implementation. No harness change is requested.

## RESUME

The lead should independently review this package, run the runner/tests, preserve the 29 source hashes and publish these inputs in L3's immutable bundle. L4 can choose an ADR scenario as a replacement while carrying the unobserved residual, assumed K and embedded FX exactly once; it should derive revenue through its lagged kernel and keep nights choices explicit. A future PIT improvement needs dated mix/FX inputs and an independently preregistered refit, not a relabel of these descriptive ratios. A fresh complete month/quarter can be added only in a new output version; actual hotel-demand claims require actual production outcomes. The ADR agent's next task is independent review of the lead's fee-panel package.
