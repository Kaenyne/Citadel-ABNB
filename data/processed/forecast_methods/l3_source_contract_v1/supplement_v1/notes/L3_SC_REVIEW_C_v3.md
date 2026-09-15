# SC-C — final independent closure of monthly fee requirements

Reviewer: cohort_fx (SC-B). Author: nclh (SC-C). Date: 2026-09-14. **Final accepted canonical output is `data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v3/`.** This narrow addendum closes `L3_SC_REVIEW_C_FEE_TIMING_v1.md`. The broader source, accounting and integrity acceptance in `L3_SC_REVIEW_C_v2.md` remains in force; no new scope or empirical test was introduced.

The fee requirements now match the original preregistration's separate monthly estimands. Row 1081, scenario `sep`, requires September 14/16/18; row 1082, `oct`, requires October 12/14/16. Each requires its own monthly treatment/control, residence, price/currency and coverage gates. Each explicitly says the other month is not required for that coefficient and disallows automatic pooling. Both current theta values remain blank and unavailable. No capture is invented, initiated or awaited.

Independent comparison found exactly **two changed consumption rows**, with changes only to `exact_additional_inputs` and `dependency_contract`. All **33,236 original cells** and all **1,187 statuses** remain unchanged. Counts remain 576 conditional exhibits, 603 descriptive, four comparators, four unavailable, zero observed and zero rejected. All direct L4 applications remain blocked. The accounting/hedge/source interpretation is unchanged, including the requirement for a separately compatible operating-only FX ratio and reconciled H.

Independent focused regression command:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q -p no:cacheprovider -k 'fee or triplet or monthly'
```

Result: **3 passed, 24 deselected in 0.17 seconds, exit 0**. These cover each named monthly triplet and rejection of an unknown fee month. The author reports the complete final 27-test suite passing in `verification_v3/receipt.json`; the reviewer did not relabel that full-suite receipt as its own run. The broader 24 tests passed independently on v2 before this limited metadata repair.

The reviewer independently compared all final output files with `results_verify_v3`: **8/8 byte-identical**. The frozen input manifest is unchanged, preserving the previously independently verified nine L4 Git blobs and 16 local inventory records. No new source-vintage claim or observation was added.

## Final reviewed identities

| Artifact | SHA-256 |
|---|---|
| consumption/run.py | `f2900e2d4ab065c0cf7914f46d969c9bc71325c8908569d0f155d2eb1ea86058` |
| consumption/test_consumption.py | `2acaeb79bac29bcb518d232d4a7c3893128577d67dbfa84fbb41da89eb183d6e` |
| consumption/README.md | `053d0532309d0655d8bf29a7971435ed8517b586beb9f0735d5e2b862b80f172` |
| consumption/freeze_evidence.py, unchanged | `f69cb5e7b11aef548ae3894a365d261b36c5cc8eb02cc86d212b2722b412ec87` |
| inputs_v2/manifest.json, unchanged | `8dbb605edd033daab92a0fb5299b96156940bc1816843376df243dab289c13e1` |
| results_v3/manifest.json | `8243dc27810af147d4333bd25bc9331f76bceec8bcab66690f0a524a0ff1e374` |
| results_v3/consumption_matrix.csv | `e01442ae80e0e203a93541c5dd40485a8be4edbba09c60b31b3dd007a3220ae1` |

**No open SC-C review findings remain against these bytes.** Acceptance covers evidence classification and gap definitions, not production application, source collection, model adoption or an investment decision. All review notes and superseded outputs remain intact.

## RESUME

Lead may bind this final v3 receipt alongside the broader v2 review and exact input identities into aggregate acceptance, then reproduce the supplement. Use accounting/results_v4 and its independent SC-A approval separately. No further review expansion is required absent an actual source, numerical or production-gating change.
