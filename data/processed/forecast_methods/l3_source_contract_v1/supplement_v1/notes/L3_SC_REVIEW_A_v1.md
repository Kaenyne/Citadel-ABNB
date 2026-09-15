# Independent SC-A review: initial findings

2026-09-14. Reviewer C (`nclh`), not the precision-package author. Review covers `l3_source_contract_v1/precision` code, compact facts, coverage, units, source chronology, fixed-lambda arithmetic and immutable-output behavior. No authored precision file or prior output was changed. Repairs are required before acceptance; the author has acknowledged the findings below.

The package audits all 96 cells across 24 quarters and four metrics, with 92 original observations checked and all four original 2020Q3 cells explicitly unavailable. Its later corroborations do not establish original IPO availability. Classification counts are 67 exact, 18 rounding, four later precision, two definition differences and five unresolved. These are source-audit classifications, not performance observations. The primary-text audit scope is 46 checked documents and one unavailable IPO body; this reviewer spot-checked selected material values independently rather than claiming to repeat all 46 readings.

Independent original-source checks confirm Q1 2026 GBV of 29,187 USDm in the original Q1 filing, so the August H1 subtraction is later corroboration, not first availability. The source also defines the Nights/Seats measure as stay nights plus experience and service participant seats, rather than reservation count. [Q1 2026 SEC filing](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/abnb-20260331.htm).

The original Q4 2020 letter gives 859,264 thousand dollars of quarterly GAAP revenue and directly reports historical Q3/Q4 ADR of 129.95/127.56. This supports preserving the frozen 859.1 USDm discrepancy and distinguishing ratios calculated from rounded inputs from directly disclosed ADR. [Q4 2020 SEC earnings exhibit](https://www.sec.gov/Archives/edgar/data/1559720/000119312521056952/d147144dex991.htm).

The later Q4 2023 quarterly summary displays Q2 2022 GBV as 16.9B; the original Q2 2022 evidence in the package records 17.0B and 16,980.6m. That presentation discrepancy should remain unresolved without an explicit revision explanation. [Q4 2023 SEC earnings exhibit, quarterly summary](https://www.sec.gov/Archives/edgar/data/1559720/000119312524033706/d646462dex991.htm).

Independent checks also confirm the Q2 2025 original letter's 23.5B versus its 10-Q's 23,447m. The difference exceeds the headline 50m half-step, so retaining an unresolved primary presentation conflict is appropriate. [Q2 2025 original letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312525174438/d17531dex991.htm), [Q2 2025 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972025000025/abnb-20250630.htm).

Publication dates and currently served original-period content are separate from historical archived-byte assurance. The sources explicitly do not claim historical bytes. Inherited webcast times are conservative certainly-public-by proxies, not exact release clocks. Missing or timezone-unspecified SEC acceptance times must retain those limitations; no earlier source-vintage replacement follows from a current retrieval.

The fixed-lambda current-Q3 arithmetic independently agrees: `(2/3×47 + 1/3×−13) = 27 USDm` of weighted GBV difference, times `0.172548908953` gives **4.658820541731 USDm**. This is n=1 held-lambda sensitivity, not a revised forecast, parameter fit or guide. Revenue-outcome/refit effects remain deliberately outside that derivative. Fixed operational policy and free-weight FAIL are unchanged; W2 is nested in W1.

The author's 23 tests independently pass. However, five additional in-memory attacks are accepted by `validate/build` and are preserved in `data/processed/forecast_methods/l3_source_contract_v1/consumption/independent_A_review_v1/receipt.json`:

1. Both inherited lambda `information_date` and `lambda_knowable_from` changed to 2027-01-01 are accepted at September 14 as-of.
2. Frozen 2020Q4 revenue changed to `nan` produces nonfinite frozen/difference ledger cells.
3. Changing source `2020Q4_letter.access_status` to unavailable still labels all four original quarter cells checked.
4. A finite original 1e308 billion-dollar value overflows unit conversion to infinity in the output.
5. A boolean original Nights observation is accepted as numeric one.

Canonical frozen inputs and their checksums are valid, so these attacks do not invalidate the numerical source findings above. They expose gaps in the callable validator and the supported alternative-input path. Repair should require finite values before and after unit conversion, finite panel cells, rejection of booleans, coherent inherited-lambda availability and checked source parents for observations and derivations. Tests should reproduce each rejection.

Two metadata clarifications are also needed. Normalized Nights/Seats units should be `million_aggregate_booked_units` or equivalent; the original internal `million_bookings` lexeme can remain separately preserved. Sensitivity output should carry its actual analysis-information date and separately label source-value availability, so an August value date does not imply a September-lambda audit existed in August.

Reviewed SHA-256 bindings:

| Artifact | SHA-256 |
|---|---|
| precision/run.py | `73b1e52d02b795f57d8bebe71d1ce3254cc306478d9f7421445a04d96309f5cc` |
| precision/test_precision.py | `bf9b6f2cfe5997c857a313e510fb240bdb73660366b016cd4042318c5d004172` |
| precision/inputs_v1/input_manifest.json | `af137faedf8df00513234e500b265b6809b1a595d6c4a87329f245614f4e5a80` |
| precision/results_v1/output_manifest.json | `abdf39efbffb97a93e8896de4247859aebc4dd92d3c8cab68a539dc3d102829a` |

Exact independent command: `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe -X utf8 -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/precision/test_precision.py -q`, from the isolated L3 root. Exit 0, 23 passed. Attack and command receipt time: 2026-09-14T04:46:13.161133+00:00. No source or output mutation was used for the attacks.

## RESUME

Author should preserve results_v1 and publish repaired outputs into a new directory, retaining the five accepted counterexamples in this review record. Reviewer C will rerun these attacks, verify final code/input/output hashes, original-source coverage, chronology and numerical invariance, then write a separate closure note. Parent owns adoption and integration; this initial note is not acceptance.
