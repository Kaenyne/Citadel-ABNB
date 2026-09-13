# L3 NCLH — the current-deposit kernel does not transfer under the preregistered test

**Implementation complete; research FAIL; no ABNB investment adoption.** For passenger ticket revenue, the expanding PIT kernel's RMSE is **1.376× seasonal naive on W1 (n=14)** and **3.841× on W2 (n=10)**, versus the required <0.6 in both. Every 2023–2025 seasonal lambda range exceeds the original <0.5pp hurdle: **2.006–3.187pp**, n=3 per season. Total revenue also fails. Metric-matched guide/consensus comparison remains unavailable and is not counted as a failed numerical test. This result rejects this predictive specification using the **current ATS balance**; it does not establish that all cruise recognition models fail. BKNG/EXPE expansion remains deferred.

Branch `codex/lane3-full`; scope claimed in `WORKBOARD_L3_v1.md`; preregistered in `L3_NCLH_PREREG_v1.md` before extraction/model execution. Canonical outputs: `data/processed/forecast_methods/nclh_transfer_v1/results_v3/`. Canonical input snapshot: `inputs_v3/`. No ABNB registry/scorer writes.

## Data and economic meaning

The fetcher collected all **46 original-quarter issuer earnings releases from 2015Q1 through 2026Q2**, yielding 184 complete core financial facts: current ATS, passenger ticket revenue, onboard/other revenue and total revenue. There are also 109 KPI observations. Every core source row carries the issuer publication clock/timezone, retrieval UTC timestamp, URL and full-response SHA256. Current-quarter columns are selected from each original-quarter release; current-retrieval comparative columns never replace historical values. Q4 comes from the quarterly columns of the corresponding FY release. All 46 passenger-plus-onboard totals reconcile within $0.002M tolerance; observed maximum floating-point discrepancy is < $0.000001M.

The source index is [NCLH financial results](https://www.nclhltd.com/investors/financial-information/financial-results). Examples are [Q4 2023](https://www.nclhltd.com/investors/news-events/press-releases/detail/584/norwegian-cruise-line-holdings-reports-strong-fourth), [Q4 2025](https://www.nclhltd.com/investors/news-events/press-releases/detail/768/norwegian-cruise-line-holdings-reports-fourth-quarter-and), and [Q2 2026](https://www.nclhltd.com/investors/news-events/press-releases/detail/812/norwegian-cruise-line-holdings-reports-second-quarter-2026). The latest outcome was published 30 July 2026 at 06:30 EDT. Raw HTML remains solely in the system temporary cache; only compact extracted rows and manifests are in the package.

The input ATS is the current balance-sheet liability, not total deposits including the long-term portion. For example, the Q4 2023 release reports current ATS $3,060.666M while management describes total ATS, including long-term, rounded to $3.2bn. The [2023 10-K](https://www.sec.gov/Archives/edgar/data/1513761/000155837024001935/nclh-20231231x10k.htm) explains that the total also includes future cruise credits. This distinction is not repaired by adding a rounded headline to the exact line. A separately preregistered total-deposit sensitivity would need exact long-term deposits on every historical source vintage.

A deposit stock overlaps future voyages over successive quarter ends. Its lag weights are predictive weights, not booking-quarter recognition probabilities. Booking horizon, deposit/payment policy, future cruise credits, prepaid onboard purchases, fleet capacity and mix can alter its revenue ratio. The [Q2 2023 release](https://www.nclhltd.com/news-media/press-releases/detail/558/norwegian-cruise-line-holdings-reports-strong-second) describes a deliberate move to longer itineraries and increased pre-sold onboard revenue. Those are plausible reasons the stock-to-revenue coefficient can move; this test does not identify their individual effects.

These are original-quarter issuer release vintages retrieved in September 2026, not archival byte captures retrieved on each historical date. Publication metadata and quarter-specific current columns are preserved; the package does not claim to prove that the issuer never corrected an old page. Accessions are not invented for IR URLs. SEC primary filings are cited to clarify definitions, not silently substituted as the publication date of the earlier release.

## Method and PIT accounting

For target q, the forecast vintage is the public timestamp of the q−1 release. Features are ATS q−1/q−2/q−3; no q deposit is used. Historical targets and all lagged inputs must be published by the vintage. Target years 2020–2021 and rows with COVID-year deposit lags are excluded. This leaves 2022Q4 eligible and flagged in the primary specification; a second run excludes 2022 targets. At the first main-window fold there are 18 primary training observations. No training observation or source timestamp exceeds its fold vintage.

Fit a deterministic 66-candidate simplex grid (0.1 increments), with seasonal lambda as the mean target/weighted-ATS ratio. Select the candidate with the lowest training proportional mean squared error; keep the stated deterministic tie order. There are **six independent fitted coefficients**: two free lag weights plus four seasonal lambdas. Both metrics use the same preregistered procedure. The fixed 2/3,1/3,0 kernel is a diagnostic, not a re-optimized model.

The stability statistic freezes weights on information published before 1 January 2023: n=17 training rows. Frozen ticket weights are (1,0,0); total-revenue weights are (0.9,0,0.1). Lambda observations over 2023–2025 are **realized full-sample diagnostics** using those frozen weights, not forecasts. All four seasons require three observations and range <0.5pp to pass.

## PIT results

RMSE is measured in USD million; ratios divide by the **same-fold seasonal-naive level RMSE**. Every numerical row below uses W1 n=14 and W2 n=10. Main windows end at 2026Q2.

| Target / model | W1 RMSE $M | W1 ratio | W2 RMSE $M | W2 ratio |
|---|---:|---:|---:|---:|
| Ticket — simplex kernel | 506.469 | 1.376 | 513.554 | 3.841 |
| Ticket — fixed 2/3,1/3 | 489.391 | 1.330 | 471.908 | 3.529 |
| Ticket — seasonal naive | 367.951 | 1.000 | 133.712 | 1.000 |
| Ticket — naive with recent YoY growth | 382.473 | 1.039 | 109.515 | 0.819 |
| Ticket — AR(1) levels | 340.668 | 0.926 | 334.679 | 2.503 |
| Ticket — trailing-four mean | 283.087 | 0.769 | 219.189 | 1.639 |
| Total — simplex kernel | 654.238 | 1.200 | 665.904 | 3.463 |
| Total — fixed 2/3,1/3 | 633.361 | 1.162 | 618.025 | 3.214 |
| Total — seasonal naive | 545.273 | 1.000 | 192.301 | 1.000 |
| Total — naive with recent YoY growth | 561.073 | 1.029 | 153.586 | 0.799 |
| Total — AR(1) levels | 459.646 | 0.843 | 441.476 | 2.296 |
| Total — trailing-four mean | 395.684 | 0.726 | 285.191 | 1.483 |

The primary ticket kernel overpredicts every main-window observation: mean bias +$476.082M/+490.955M in W1/W2. Its pre-COVID coefficients adapt slowly to the different post-reopening deposit/revenue relationship. This is a material failure, not a marginal hurdle miss. Excluding 2022 does not rescue it: ticket ratios **1.402/3.750**, total **1.217/3.396**, with the same n=14/10. No post-result recency/weight search was used to replace the failure.

| Season | Ticket lambda range (pp) | Total lambda range (pp) | n per metric | <0.5pp verdict |
|---|---:|---:|---:|---|
| Q1 | 2.360 | 5.890 | 3 | FAIL |
| Q2 | 2.399 | 4.828 | 3 | FAIL |
| Q3 | 2.006 | 2.417 | 3 | FAIL |
| Q4 | 3.187 | 3.894 | 3 | FAIL |

`lambda_comparison.png` shows ABNB and NCLH side by side using identical 2023–2025 calendar cells, with different denominators and vertical scales explicitly labelled. ABNB values reproduce the existing `kernel_lambda/01_lambda_table.csv`; this contextual chart makes no claim that every ABNB seasonal range passes the NCLH hurdle.

## Guidance and consensus gate

NCLH outlooks commonly guide non-GAAP net yield, costs, EBITDA and adjusted EPS. For example, the [27 February 2024 8-K](https://www.nclhltd.com/investors/sec-filings/all-sec-filings/content/0001171843-24-001001/0001171843-24-001001.pdf) contains constant-currency net-yield guidance. Net yield per capacity day is not GAAP passenger ticket or total revenue: a conversion requires capacity and expense/definition bridges. No such bridge is invented. The inventory preserves guidance rows where the table parser finds them, but does not assert exhaustive discovery of every historical public quotation.

No matched quarterly GAAP-revenue guidance and timestamped same-metric consensus dataset was assembled from these issuer sources. Guide+cushion and Street baselines therefore have **n=0, UNSCORED** for both targets/windows. The >=65% guide-surprise hurdle remains **unavailable**, distinct from the failed kernel/stability tests. Current EPS consensus, total annual guide language, and net-yield guidance cannot be relabelled a historical quarterly revenue guide. Missing consensus does not prevent the completed deposit-kernel test.

## Reproduction, source repairs and checks

Exact executed commands from the isolated repository root:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" analysis/src/forecast_methods/nclh_transfer_v1/fetch.py
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -m unittest discover -s analysis/src/forecast_methods/nclh_transfer_v1 -p test_nclh.py -v
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" analysis/src/forecast_methods/nclh_transfer_v1/run.py
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" analysis/src/forecast_methods/nclh_transfer_v1/run.py --out data/processed/forecast_methods/nclh_transfer_v1/results_verify_v1
```

All commands exited 0. **12 tests pass**, including timestamp leakage, refusal of unavailable lagged deposits, immutable current-target influence, missing calendar lag, denominator validation, COVID/reopening eligibility, accounting identity, issuer timestamps, source parsing, simplex recovery and strict pass thresholds. The offline rebuild is byte-identical across every canonical output including manifests, recorded in `reproduction_receipt_v1.json`. The comparison chart was visually inspected. Empty exclusions have a valid CSV header; all 14 forecast folds are available for each target/scenario.

Before the first research run, extraction found and repaired: (1) FY headings supply Q4; (2) blank suspended-sailing KPI cells must not select later comparative values; (3) $0.166M ticket revenue in 2021Q1 must survive a tiny-value filter; (4) `Capacity Days (1)` footnotes must not lose the row; (5) the Q4 2023 outlook's 15.8% net-yield growth cannot substitute for actual $243.27 net yield. Canonical `inputs_v3` incorporates these repairs; earlier input snapshots remain explicitly superseded. Model results are unchanged across results v1/v2/v3; later versions only expand the L4 evidence export and clarify empty bounds/CSV headers. No failed numerical result was removed.

## L4 handoff and RESUME

L4 may consume **12 evidence-only rows** in `results_v3/l4_evidence.csv`: four both-window RMSE ratios and eight seasonal stability ranges. Values are ratios or percentage points with explicit units, source references, information dates and `neither; cross-issuer diagnostic only` treatment. Bounds are empty because no uncertainty distribution is estimated. The matching hashes and source dependencies are in `results_v3/run_manifest.json`. Do not use this package to change ABNB revenue, its guide, valuation or trade direction. The lead incorporates the independent review and commit into the versioned bundle; nothing is registered here.

**RESUME:** The completed preregistered current-ATS test fails and should stay in the research record. A future exact total-deposit dataset or capacity/deposit-duration model requires a new preregistration and output package, not a retrospective replacement. A guide-surprise study additionally needs matching NCLH guidance targets and vendor/time-stamped consensus. BKNG/EXPE stays deferred; no team decision is inferred. Reuse the parser and PIT guards with those caveats, and preserve the original failure and canonical source snapshot.
