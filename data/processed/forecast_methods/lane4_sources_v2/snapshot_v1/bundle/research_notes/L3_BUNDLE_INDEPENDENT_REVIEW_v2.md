# L3 bundle independent review v2 — integrity repairs accepted

Reviewer: nclh subagent, independent of integration implementation. Date: 2026-09-13. This continues `L3_BUNDLE_INDEPENDENT_REVIEW_v1.md` by reviewer adr_hotel. **The reviewed builder repairs are accepted; production bundle publication still requires the lead's actual committed-payload verification.** No production bundle was built by this reviewer.

## Additional source-commit counterexample and closure

The initial Git-status guard did not fully enforce the first review's committed-source condition. In a disposable test repository on branch `codex/review-fixture`, the reviewer committed only ignore/configuration files, placed a valid one-row adapter under an ignored directory, and called `build`. Git status was clean, `git ls-files` returned no input, yet the bundle was built and claimed the repository HEAD as its research source. The test used only a temporary repository, never the project's Git history or production payload.

The lead repaired this by requiring each copied payload and each actual package `.py`, `.md` and `.gitattributes` file to exist in HEAD and match its committed blob bytes. The builder captures those blob bytes, rechecks the normalized inputs against them, and copies the captured blobs rather than reopening the source during payload copying.

Independent replay of the exact ignored-directory test now raises `Research source not committed in HEAD: ignored_source/input.csv` **before creating the destination**. A positive control then explicitly commits the input with byte-preserving attributes: build succeeds and verify reports five valid checksum entries and schema PASS. Appending a newline to the now-tracked source makes the direct blob comparison reject with `Research source bytes differ from HEAD`. This closes the ignored-source gap and checks that the stricter guard does not merely reject every source.

## Earlier findings and regression suite

The unexpected nested `SHA256SUMS.json` case is covered by the repaired exact root-relative exclusion. A nested file now participates in the actual recursive manifest and fails checksum equality when unmanifested. Replacement/multiply rows with missing embedded-FX metadata normalize to an inapplicable marker and are then rejected; current canonical replacement rows retain explicit metadata. The matching-baseline guard remains active.

Independent test command from the isolated project root:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -m pytest analysis/src/forecast_methods/l3_integration_v1/test_bundle.py -q -p no:cacheprovider
```

Exit 0, **15 tests passed in 2.28 seconds**. This includes the prior checksum, date, duplicate, bounds and adoption guards plus ignored/uncommitted/changed source checks. The disposable repository replay above was an additional independent test, not a mock of Git status.

Reviewed `bundle.py` SHA256: `8e4af1f614f9e67e13c02834a0b0e3321bbd9345e8223ef12a662c84347a3f20`.

## Independent canonical-input preservation check

The reviewer normalized and validated the four completed canonical adapters without writing a production bundle:

| Package | Canonical source | Rows |
|---|---|---:|
| Cohort FX | `cohort_fx_v2/results_v2/l4_adapter.csv` | 1,080 |
| Fee panel | `fee_panel_v1/reviewed_v3/l4_inputs.csv` | 2 |
| ADR/hotel | `l3_adr_hotel_v1/l4_adr_hotel_inputs.csv` | 86 |
| NCLH | `nclh_transfer_v1/results_v4/l4_evidence.csv` | 12 |

All **1,180 rows** preserve numerical values (including NaNs), units, original source periods and original source information dates exactly. Columns remain unique; the concatenated schema validates. Historical NCLH ranges are correctly labelled historical in the canonical quarter field, while the original ranges and underlying-publication timestamps remain in dedicated source fields. New research information dates are 13 September rather than backdated to historical outcomes. Existing treatment and replacement-versus-incremental restrictions remain present.

The new conversion package is a fifth required CLI input and was still being completed during this review. Its actual adapter and the final five-package artifact require the lead's subsequent validation; the row count above does not claim to include it. Likewise, a passing source guard and temp fixture do not substitute for verifying the production artifact's checksums and source commit after publication.

## RESUME

Commit the finalized canonical research code/outputs with their byte-preserving attributes, include the independently reviewed conversion adapter, build a new immutable five-package bundle, then verify local and committed Git bytes and publish the source/bundle commit identifiers. Keep the first review and this closure. No integrity repair adopts any research scenario or relaxes its identification and baseline-compatibility limits.
