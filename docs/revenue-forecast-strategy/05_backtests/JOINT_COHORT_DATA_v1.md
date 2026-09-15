# GE-JOINT-DATA — source admissibility for joint booking shares and conversion

Codex data subagent · 15 September 2026 · branch `codex/submission-readiness-v1` · all new package `gbv_joint_cohort_v1/data_audit_v1` · approximately 30 minutes. Claimed in `WORKBOARD_improvement_0915_theo_joint_v1.md` before the audit.

## Verdict

**Direct current corporate cohort measurement is UNAVAILABLE in the inspected local sources.** The data-admission gate is not satisfied; this is not an empirical rejection of booking survival or evidence that its variance is high. The script's `direct_cohort_gate="FAIL"` means only that no qualifying measured source was admitted. Twenty actual tables and three missing advertised sample tables were inspected, along with the catalogue and 59 sample manifests. A joint aggregate model can still be estimated and subjected to identification/variance tests, but its booking-cohort allocations must remain fitted assumptions until measured cohort data validate them.

PR 60 does provide one useful **stored historical-vintage demand feature** for a separate GBV forecast ablation: EUROCONTROL first-75-day flights. Its stored lineage passes all local consistency checks, with a limitation that original historical git blobs are absent on this machine. Flights are informative about demand; they do not turn an unidentified booking-to-revenue allocation into a measured one.

## What ran

Read `AGENT_BRIEF.md`, `WORKBOARD.md`, and `improvement_0915_theo_cohort_audit_v1.md`. Verified that PR 60 commit `dd3aa1440b152b46fdee8c094875d178b802d74a` is an ancestor of worktree HEAD `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`:

```powershell
git merge-base --is-ancestor dd3aa1440b152b46fdee8c094875d178b802d74a HEAD
git diff --name-only dd3aa1440b152b46fdee8c094875d178b802d74a^ dd3aa1440b152b46fdee8c094875d178b802d74a -- data/manifests data/samples docs analysis/src
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/run.py
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/check_flight_lineage.py
```

All four commands exited 0. Audit script approximately 5 seconds; lineage check approximately 2 seconds. Both scripts refuse existing output directories; use `--out NEW_PATH` for a repeat. One later interactive PowerShell report command had an empty-pipeline syntax error and was rerun correctly; no data/model mutation resulted.

Outputs under `data/processed/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/`:

- `evidence_inventory.csv`: actual local presence, row/column counts, exact columns, economic units, date/value/cancellation/fee fields, permitted use and explicit exclusions.
- `field_profile.csv`: actual column dtypes, nonnull/unique counts, and non-personal date-field ranges. Irregular date formats remain lexical ranges, not invented timestamps.
- `sample_manifest_locality.csv`: 59 sample manifests; 227 advertised CSV paths of which 215 are locally present. This count is limited to string-valued advertised path entries; it is not a count of all possible upstream data files.
- `catalog_crosswalk.csv`: relevant sources tied to the 1,773-row discovery catalogue.
- `summary.json`: source SHA-256 hashes, source counts, PR ancestry and the data-admission result.
- `flight_lineage_v1/flight_vintage_checks.csv` and `flight_lineage_v1/summary.json`: 17 quarter-by-quarter checks against the 1,071 stored git-commit records, exact UTC timestamps, source hashes, and completeness limitations.

No public web requests, purchases, outreach, new scraping, credentials, forecast registration, scorer runs or live-model changes. No individual reviewer names, comments, calendar identifiers or reservation records are copied into the audit output. Added fitted parameters: zero.

## Results: what each promising source actually supplies

| Source | Actual local n | Joint-cohort usefulness | Admission |
|---|---:|---|---|
| K2 recommended prior | 12 season-by-weighting rows; four value-weighted groups | Old reconstructed Melbourne accommodation-value composition, not fee dollars or a compatible booking-cohort denominator | Sensitivity prior only; raw reconstruction unavailable |
| K2 truncation check | 4 experiment rows | Records failure to recover the reference lead-time mean under simulated truncation | Diagnostic, not validated correction |
| Financial KPI panel | 24 corporate quarters | Net reported GBV and total recognized revenue give aggregate margins, not joint cells | Aggregate model input subject to existing source/publication rules |
| Calendar reopening | 130 market-interval rows | Reopening is a cancellation-sensitive proxy mixed with blocks and listing changes; no matched booking value or final status | Descriptive corroboration only; short 2025–26 history |
| RNPL stay matrix | 8 booking-quarter scenario rows | A model-generated nights allocation; does not independently validate cohort weights | Scenario only |
| PR 60 EUROCONTROL PIT | 17 quarters, 3Q22–3Q26 | Actual demand index from historical git-vintage aggregates; no reservation linkage | Preregistered dated GBV ablation candidate |
| PR 60 review-vintage table | 60,811 market-vintage-month rows | Review posting dates and counts; absent original booking date, price, cancellations and fees | Source diagnostics; no direct cohort constraint |
| PR 60 reviews raw manifest | 114 advertised raw files; zero advertised absolute raw paths exist locally | Captures and hashes document prior acquisition, not current local raw availability | Manifest evidence only |
| PR 60 Buenos Aires review sample | 8,000 reviews | Actual columns `listing_id,id,date,reviewer_id,reviewer_name,comments`; posting dates only | Schema validation; no fee or booking cohort |
| WSDM booking sample | Missing locally; prior manifest claims 62,861 train-head reservations | README advertises `created_date`, but sampled-schema manifest explicitly reports it absent; also no prices/cancellations | Excluded; do not infer a booking date from README |
| RecTour users sample | Missing locally; prior manifest claims 19,330 sampled stays | Guest type, room nights, month and property attributes; no booking dates/monetary value/cancellations | Excluded from joint model |
| Bright Data quotes | Missing locally; prior manifest claims 1,000 quotes | Requested stay dates, offered price and cancellation policy, not accepted/completed bookings | Excluded |
| Boston imputed bookings / stays | 100 city-scrape rows / 110 city-month rows | Separate aggregate margins with no joint key; 2018–19, month-only stay panel | Method example only |
| iCal demo | 13 events, one `DTSTAMP` | `DTSTAMP` is single file-generation time; no original booking dates, dollars or cancellation history | Excluded |
| Opportunity Insights spending | 1,359 dates | National spending index ends 16 June 2024; not Airbnb-only or linked to stays | No usable current joint-cohort constraint |
| BNPL adoption directory | 278 merchant-provider rows; zero nonnull `adoption_date_best` | Web-directory first appearance does not measure true adoption, usage or booking survival | Excluded |
| BNPL financial panel | 4,675 company quarters | SEC-derived aggregate financials; duplicates accounting margins | No new cohort constraint |
| Texas lodging receipts | 50,011 property-period rows | Annual and quarterly receipts mixed, latest partial; no booking date or fees | No joint-cohort constraint; no W1 coverage |

These counts measure rows, not independent quarterly samples. The source directories and SHA-256 hashes are in the machine-readable inventory. Fields described solely by a manifest remain explicitly distinguished from actual local schemas.

### Why the Boston panels cannot simply be consolidated

`long_date_booked.csv` has `price,nights,unit,dates` and scrape-gap fields. `long_reservation_date_by_month.csv` has `month,price,nights,unit,trt`. There is no common reservation/cohort key to identify how a particular booking interval maps into a particular stay month. A city-level join creates many-to-many possibilities, not observed cohort cells. The upstream `compute_reservations.py` labels available-to-unavailable transitions as bookings, filters surviving listings and takes the last row per listing/stay date under a comment about removing cancellations. This erases the cancellation history needed for a forward original-booking-to-completed-stay denominator. Running the old script cannot recover absent historical raw snapshots.

### PR 60 flight feature: a usable calculation with bounded claims

The preferred file is `data/processed/govdata_v2/qtd75_pit.csv`, with `quarter,q_start,day75,commit,commit_date,lag_days,eu40_flt_da_cur,eu40_flt_da_prev,eu40_flt_da_yoy` and EU-core equivalents. Inspection of `analysis/src/govdata_v2/C2_vintages.py` confirms that both current-year and comparison-year daily aggregates are read from the **same historical commit**, selected as the first stored commit whose file contains day 75. This is different from using the latest full-quarter series.

All 17 prefixes map uniquely to `git_commits.csv`; dates match, lag arithmetic reconciles, all 75-date flags are present, and both YoY ratios reproduce from numerator/denominator. The helper output adds full UTC commit timestamps for precise origin gating. Publication delays are not always one day: 2Q26 took 16 days, 2Q23 15 days and 3Q25 nine days. A previous quick agent message incorrectly mentioned 90 days; this was corrected before final delivery and is not a value in the inventory.

For a guide-origin forecast, admit a feature only when its actual `committed_utc` is no later than the forecast origin. The target quarter's day-75 reading is unavailable at the prior-quarter guide. A permissible ablation may use the latest previously available feature with its age recorded, or the prior-quarter feature if available; pre-register which rule applies. Missing early training features remain missing, so the effective W1/W2 sample and fallback behavior must be explicit. The quant package owns this specification and the forecast comparison.

This audit certifies stored-table internal consistency, not a fresh retrieval of original raw files. The external git mirror does not exist at either checked user location. Upstream code checks that 75 dates exist but does not require all 40 states on every day. In the stored daily revision panel, median absolute revision is zero, yet one first estimate on 22 March 2026 changes from 698 to 35,060 flights. That date is **after** 1Q26's day-75 cutoff, so this is not evidence that the saved QTD75 is contaminated. It does show why the old note's broad language that revisions are nil is too strong and why raw completeness remains a qualification.

Recommended label: **inherited stored historical-commit-vintage diagnostic; original blobs not locally recertified**. A successful GBV ablation could support incremental forecast usefulness conditional on this source lineage. It would not measure booking survival, cancellation rates or corporate fee cohort shares.

## Interpretation for variance and pitch eligibility

The direct cohort variance cannot be measured from these sources because the direct joint cohort object is absent. This is different from finding that a measured cohort variance is too large. Aggregate forecast errors and fitted-cohort sensitivity can be calculated now. If multiple allocations fit the same corporate margins while implying different forward conversions and revenue shares, that is evidence of weak identification. Neither many review observations nor a stronger prior resolves that identification problem by itself.

Use the quant package's preregistered W1/W2 forecast comparison and identification results for the pitch decision. Do not claim a current percentage of bookings converts, a cohort cancellation rate, or a measured RNPL effect from this audit. It is appropriate to state that the current GBV model is an aggregate historical conversion benchmark, with explicit uncertainty about timing and same-quarter booking contributions.

## Harness change requests

None. No forecasts registered and no scorer run required.

## RESUME

The quant agent should consume the aggregate accounting inputs and test the coherent joint allocation as an identified-set/sensitivity model, not measured customer cohorts. Use the PR 60 `qtd75_pit.csv` EU40 demand feature in the preregistered GBV ablation with actual commit-time gating and explicit source-lag/coverage reporting; the helper supplies verified stored commit timestamps. Retain the raw-completeness limitation and distinguish predictive usefulness from economic cohort identification. New direct data would need original booking timestamps, check-in/recognition dates, compatible original value, final modifications/cancellations and fees; none of the inspected local sources currently provides that complete object.
