# Regional reconciliation v3

R refreshes the copied v2 constrained regional model using soft annual 10-K ADR anchors. It preserves filed regional revenue and total GBV and nights exactly. It does not infer causal booking-dated regional revenue timing from those identities.

Run from the repository root with the project environment:

```text
python analysis/src/forecast_methods/l1_reconciliation_v3/fetch_arrivals.py
python analysis/src/forecast_methods/l1_reconciliation_v3/run.py --bootstrap 40
python -m pytest analysis/src/forecast_methods/l1_reconciliation_v3/test_refresh.py -q
python analysis/src/forecast_methods/l1_reconciliation_v3/run.py --candidates-only
```

The public download step is optional for an offline rerun. It requests explicit official workbooks and API queries, processes payloads in memory, and saves only normalized monthly aggregates and a URL/status/hash manifest. The core run never fetches the network and never modifies old packages or the scorer.

The 5% log-ADR anchor is a regularization scale, not a claimed confidence interval. Sensitivity includes 2.5%, 10% and effectively no ADR anchor. Four-quarter block refits measure conditional disclosure/composition variation. Exact accounting residuals equal zero; bootstrapping those yields a zero-width interval and cannot validate a forecast. Regional levels remain conditional on persistent relative take-rate assumptions and interval likelihood restrictions.

All public arrivals downloads in this run are current revisions. Their `knowable_from` is the retrieval date, which excludes them at every historical guide origin. Lagged current-revision correlations are descriptive only. No arrival coefficient crosses into the FY27 projection. Eurostat `tour_occ_nim` measures accommodation nights rather than visitor arrivals; JNTO is Japan inbound rather than all APAC or domestic travel; NTTO covers US inbound rather than all NA bookings. DataTur's advertised workbook was monetary receipts/expenses, so it was rejected as a count-unit covariate. Australia and Brazil were not substituted with unrelated series.

The FY27 projection carries existing scenario growth rates, fixed unit-size and LOS assumptions, constant seats composition, and zero FX y/y. Its attribution rows carry zero additional weight in revenue. The K0 v2 `pit_lambda` interface supplies the EWM coefficients; these are held fixed in the kernel-weight sensitivity. Conditional composition bounds exclude uncertainty in macro growth, FX, future booking paths, cushions and lambda; they are never called predictive intervals.

The frozen harness has neither an annual slot nor a current run-date slot. The original attempt to use 2026-09-11 as a format slot was rejected by parent; `full_sample` did not repair its inaccurate date. The two rejected files are preserved byte for byte under the package output's `UNREGISTERED_rejected_registry_20260913/` directory and removed from the shared registry. The runner now has no registry-writing path. Both a full run and `--candidates-only` emit local `UNREGISTERED_fy27_candidates.csv` plus `registration_status.json`, with the actual UTC reconstruction timestamp separate from the financial input cutoff, and no asserted historical vintage. The candidates-only command reuses existing fitted outputs without repeating any regional model fit. There are no W1/W2 forecast registry rows or predictive quantiles. Annual objects and conditional bounds remain local. Parent owns scoring and any future schema change.

See `docs/revenue-forecast-strategy/05_backtests/R_REGIONAL_REFRESH.md` for the pre-registration, results, limitations and proposed memo sentence.
