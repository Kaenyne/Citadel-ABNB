# L3 NCLH independent-audit repairs v1

2026-09-13. This note supersedes canonical-version/test-count references in `L3_NCLH_RESULTS_v1.md`; every published research number and FAIL verdict remains unchanged. **Canonical outputs are now `results_v4/`; canonical facts remain `inputs_v3/`.**

Independent reviewer `cohort_fx` reproduced five malformed-input acceptance defects without changing canonical inputs: (1) a source exactly at 2026-09-14 00:00 UTC passed the September-13 cutoff; (2) a missing timestamp on one metric was hidden by the quarter-level timestamp aggregation; (3) simultaneously infinite passenger/total values passed the accounting identity; (4) a 64-character non-hex source hash passed the length check; (5) whitespace provenance passed the null check. These are implementation findings, not evidence that the actual input snapshot was malformed.

The author tightened validation before aggregation: all per-row timestamps must parse and be nonmissing; the next-day cutoff is exclusive; all values must be finite/numeric; source references must be nonblank after trimming; SHA256 must be hexadecimal; and metric units must match the explicit dictionary. Six regression tests cover the five reported cases and wrong units. **18 tests pass**. The independent reviewer additionally matched all 47 cached raw response hashes to the manifest (46 releases plus the index), spot-inspected 2015Q1/2021Q1/2025Q4/2026Q2 table column selection, and reproduced both-window research failures. Contemporaneous byte-archive proof remains unavailable, as already disclosed.

Exact repaired-run commands from the isolated worktree root:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -m unittest discover -s analysis/src/forecast_methods/nclh_transfer_v1 -p test_nclh.py -v
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" analysis/src/forecast_methods/nclh_transfer_v1/run.py
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" analysis/src/forecast_methods/nclh_transfer_v1/run.py --out data/processed/forecast_methods/nclh_transfer_v1/results_verify_v2
```

All exited 0. `reproduction_receipt_v2.json` records byte identity across all eleven canonical output files and their rebuild. Scores, fold predictions, coefficients, stability, lambda observations and verdict JSON are also byte-identical to results v3. The L4 source references now point to results v4. Earlier files remain unchanged as audit history. No new tests were used to search for a better research result.

## RESUME

Lead should consume only `data/processed/forecast_methods/nclh_transfer_v1/results_v4/l4_evidence.csv` and include this repair note alongside the independent review. The twelve evidence rows remain cross-issuer diagnostics with no ABNB forecast adjustment. Preserve the original preregistration, failed transferability result and source-retrieval limitation. Further modelling requires a separately preregistered package.
