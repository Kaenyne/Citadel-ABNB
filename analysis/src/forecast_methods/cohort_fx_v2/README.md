# Cohort FX/RNPL v2

An offline, deterministic sensitivity engine on top of the unchanged K0 two-lag kernel. It preserves total cohort exposure, normalizes reported-dollar contributions to a fixed reference currency basis, and replaces only assumed RNPL FX timing. No new forecast registration, lambda fitting, RNPL share estimate, cancellation or hedge model.

## Reproduce

From the repository root (Python with pandas, numpy, pytest):

```powershell
python -X utf8 -m pytest analysis/src/forecast_methods/cohort_fx_v2/tests -q
python -X utf8 analysis/src/forecast_methods/cohort_fx_v2/run.py --out data/processed/forecast_methods/cohort_fx_v2_new_run
```

Output must be new or empty; the runner refuses to overwrite. Optional `--fx-bundle 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE'` hashes five external files consulted in the interface audit. It does not execute them or consume synthetic example inputs. Omit this option on another checkout; only the optional external rows in `input_manifest.csv` and its checksum differ. No network is required.

Frozen canonical outputs are in `data/processed/forecast_methods/cohort_fx_v2/results_v2/`. `results_verify_v2/` is the independent exact rerun. The files in the parent directory preserve the pre-period-coverage checkpoint and are not canonical. Numerical CSVs use USD, never implicit millions; notes may display USD millions.

## Inputs and API

`engine.py` exposes:

- `from_reported_contributions(contributions, rates, as_of)`: currency-split reported kernel dollars -> compatible conditional reference contributions.
- `apply_timing(cohorts, allocations, rates, as_of, basis_status=...)`: details, cohort/currency/recognition weight audit and aggregate ordinary/reference/retimed paths.
- `yoy_bridge(current, prior)`: distinct growth and level effects using the same reference basis and an actual year-ago quarter.
- `RateBook(rates, as_of)`: strict rate, provenance, information-date, quote-direction and reference-basis checks.

Every cohort has `quarter, booking_quarter, currency, reference_contribution_usd, rnpl_share, information_date, source_ref, evidence_status, reference_basis`. The normalization API instead receives `reported_contribution_usd`. Allocation rows have the same keys and metadata, plus `fx_period, p, timing_hypothesis`; p sums to one per key. Rates have `period, currency, usd_per_unit, reference_usd_per_unit`, the metadata, `quote_cutoff` and `rate_status`. Periods are YYYYQn or YYYY-MM. Recognition timing must stay inside the revenue target quarter; a different fixing date must be explicitly labeled `payment_fixing_proxy`.

Inputs are not probabilities inferred from public stocks. `rnpl_share` is the RNPL share of **that contributing revenue cohort**. Currency contributions must already reflect the correct exposure denomination; origin/destination proxies require explicit labels. In the supplied example currency shares apply to reported-dollar kernel contributions. The output reference weights are calculated after removing each currency's booking FX, so they differ from both the kernel coefficients and reported-dollar currency shares.

## Results and integration

The runner outputs 180 Q3 2026 scenarios (3 non-USD shares x 5 u shares x 4 timing alternatives x 3 post-cache FX paths), using public Q1/Q2 booked GBV and public frozen FRED history. A year-ago K0 forecast supplies a separately labeled model-to-model YoY illustration, not a PIT cohort backtest. Newly fitted parameters: zero. Historical cohort FX forecast evidence: W1 n=0, W2 n=0.

`l4_adapter.csv` includes quarter/metric/scenario/value/bounds/units/information date/evidence/source/treatment, the exact replaced baseline, embedded FX and unresolved hedge convention. To a **matching** ordinary reported-USD kernel, add `incremental_replacement_usd` or multiply by `replacement_multiplier`. Never multiply it by `retimed_level_multiplier` (that factor applies only to reference-normalized revenue). No hedge dollars are supplied; totals after explicit hedges remain blank. Adoption requires baseline/accounting compatibility.

`cohort_currency_detail.csv` and `cohort_currency_recognition_weights.csv` show every w/u/p and dollar contribution. `rates.csv` carries observation counts, extrapolated weekdays, actual quote cutoffs, rates, ratios' reference and source URLs. `yoy_bridge.csv` keeps YoY pp separate. `kernel_inputs.csv` and `kernel_identity.csv` reproduce K0's public API exactly. `input_manifest.csv` hashes dependencies; `output_checksums.csv` hashes the frozen analytical outputs.

Read `docs/revenue-forecast-strategy/05_backtests/L3_COHORT_FX_PREREG.md`, `L3_COHORT_FX_ACCOUNTING.md` and `L3_COHORT_FX_RESULTS.md` for acceptance lines, accounting limits and receipts.

## RESUME

Keep this version immutable. For a changed input vintage or implementation, make a new package/output version. Measured cohort currency/RNPL/fixing inputs can use the generic API, but current output remains conditional research, and L4 owns combined forecasts, guide conversion, registrations and investment decisions.
