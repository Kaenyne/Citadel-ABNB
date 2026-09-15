# L4 sources v2 — committed inputs and accounting eligibility

Source worker / committed_evidence_audit · 13 September 2026 information snapshot,
completed 14 September UTC · branch `codex/lane4-full`. New code/data package
`lane4_sources_v2` only; no old package, frozen input, research result or registry
changed. Parent owns local staging/commit and independent review.

## Verdict

**Source integrity PASS; accepted L3 conversion validation is complete. Free-weight
promotion FAILS both matched windows, so the existing fixed 2/3 K0 seasonal policy
is retained. Current central FX financial application is INELIGIBLE.** The latter
is a distinct accounting/identification outcome: the verified cohort tables cover
Q3 and reconstruct that reported baseline, but do not certify a pre-hedge
denominator or supply the embedded hedge split. No new fit was run. All22 free
and fixed OLS coefficients remain descriptive, and investment adoption is open.

## Source identity and exact reproduction

The runner reads binary Git objects from bundle commit
`8821961853e4068febbfe2712f9a4e1036c9e629`, never mutable L3 working files. Research
source commit is `7fb6fe0f248d5492b899672b9b70545da62d63ee`; it descends from the
verified L1/L2 base `1c87628cedbc94ab8a0e8552743c94485ef353b8` and is an ancestor
of the bundle commit. The bundle's `SHA256SUMS.json` SHA256 matches the supplied
`9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`.

Canonical consumption directory:
`data/processed/forecast_methods/lane4_sources_v2/snapshot_v1/`.
The original bundle is its `bundle/` subdirectory; original handoff is under
`handoff/`. The two explicitly supplied QVS notes were copied from the original
workspace to `qvs/`, with before/after capture checks and hashes in
`support_manifest.json`. Their references to L3 working files were not followed.
No optional supplemental source was accepted.

| Integrity object | n | Result |
|---|---:|---|
| Manifest-covered files | 108 | All exact; manifest itself independently hashed |
| Research output/note Git objects | 104 | All exact matches to canonical bundle payload |
| Conversion acceptance bindings | 32 | 24 outputs, five source files, two reviews, repeated specification binding; all exact against actual research objects |
| Explicit QVS support notes | 2 | Exact snapshot copies, hashes retained |
| End-to-end snapshot files | 125 | Byte-identical independent rebuild |
| Package tests | 18 | PASS, 1.290 seconds, exit 0 |

The verifier has explicit statuses for CRLF/LF-only differences and rejects
other content differences. None occurred in the actual 104 lineage comparisons
or 32 acceptance bindings. This verifies identity and receipt closure, not an
independent rerun of L3's statistical tests.

Exact commands from the L4 worktree root (all exit 0):

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/lane4_sources_v2/run.py --stage extract --out data/processed/forecast_methods/lane4_sources_v2/snapshot_v1 --qvs-root 'C:/Users/wille/Desktop/Citadel - ABNB'
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/lane4_sources_v2/run.py --stage audit --out data/processed/forecast_methods/lane4_sources_v2/snapshot_v1 --qvs-root 'C:/Users/wille/Desktop/Citadel - ABNB'
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/lane4_sources_v2 -p 'test_*.py' -v
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/lane4_sources_v2/run.py --out data/processed/forecast_methods/lane4_sources_v2/reproduction_v1 --qvs-root 'C:/Users/wille/Desktop/Citadel - ABNB'
```

Extraction took 2.3724 tool-wall seconds; audit 0.9407; complete independent
rebuild 2.9835. Every one of the 125 snapshot file bytes matched. See
`data/processed/forecast_methods/lane4_sources_v2/validation_receipt_v1.json` for
code hashes and receipts. Existing output IDs refuse overwrite. Scoped new
`.gitattributes` files preserve source and output bytes through Git.

## All-row disposition and source fields

`row_dispositions.csv` retains all 28 original source columns and 1,187 rows,
including source periods, information dates, treatment/replacement fields,
missing values, units and bounds. Added stable IDs, source-row hashes, package
payload references/hashes and both commits make each row traceable. Measurement
class, integration disposition and financial eligibility are separate axes.

| Integration disposition | n | Treatment |
|---|---:|---|
| Conditional | 962 | FX/ADR scenarios or components; limits retained |
| Calculated | 198 | 180 ordinary-kernel identities and 18 GBV identities; no additive adjustment |
| Descriptive | 7 | Accepted conversion calibration and chronological comparison |
| Comparator | 4 | Complete-quarter hotel price indices only |
| Unavailable | 4 | Two fee-theta and two incomplete hotel-quarter rows; never zero |
| Rejected | 12 | NCLH transfer FAIL retained; no ABNB adjustment |
| Directly observed research parameter | 0 | Raw observed rates/indices are separate payload inputs, not adapter estimates |

The historical NCLH periods are retained with their original publication stamps;
they are not relabelled current ABNB forecasts. Hotel production is unavailable.
At the frozen September13 snapshot, zero of six scheduled fee captures exist,
so theta is not measured. ADR component rows are explanatory, and reported ADR
totals already contain their named FX estimate and imposed fee mechanics. Use
one coherent replacement route; no component or full FX factor is added twice.

## Accounting interface and baseline compatibility

The source normalizes reported-dollar contributions by assumed currency/fixing
factors: `C0_bc=lambda*a_b*GBV_reported_b*s_bc/f_booking_bc`, with `R0=sum C0_bc`.
This constructs conditional reference-currency GBV/revenue, not an observed
company constant-currency series. The backward contribution share is
`w_bc=C0_bc/R0`, whose denominator is target-quarter reference revenue across
booking/currency cohorts. `u_bc` is an assumed RNPL portion of that cohort's
reference contribution; `sum w*u` is its target-quarter reference share. Neither
is the unpaid-balance stock, booked RNPL flow, nor a measured forward
booking-cohort recognition share. `p` sums to one within each RNPL cohort/currency
allocation. Payment, fixing, recognition and hedge dates remain distinct.

The actual source arithmetic is `B=sum C0*f_booking`,
`T=sum C0*((1-u)*f_booking+u*sum p*f_recognition)` and `m_source=T/B`.
**It does not supply a certified `m_pre`.** The inherited lambda is fitted to
reported revenue, which can include hedge reclassifications. The full reference
factor `T/R0` must never multiply already translated reported-USD revenue.

For certified matching future inputs, `R_new=m_pre*(R-H)+H_new`, where H is the
signed revenue hedge contribution already embedded in the same-quarter baseline
and H_new is its scenario counterpart. They are not hedge notional or total AOCI.
`H_new=H` is a named unchanged-hedge assumption after H is supplied; it is not
silently imposed. Missing H/H_new cannot be converted to zero. The guarded
identity is unit-tested on synthetic accounting inputs only.

| Source/L4 check | n | Result |
|---|---:|---|
| Source scenario identities | 180 | PASS; largest error USD0.027601, tolerance USD1 for rounded exports |
| Cohort/currency contributions | 2,520 | Included in reference, ordinary and retimed reconstruction |
| Recognition/fixing allocations | 3,780 | Conditional p and normalized weights reconcile |
| Existing Q3 L4 scenario baselines | 5 | Reported revenue, weighted GBV and lambda match source precision |
| Existing Q4/Q1 L4 scenario baselines | 10 | No source target-specific scenario/cohort basis; extrapolation blocked |
| Financially eligible FX baselines | 0 of 15 | Pre-hedge/H split and measured cohort contract absent |

Baseline source is the exact forecast Git blob at L4 starting commit
`29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. Source Q3 ordinary revenue is
USD4,808.36292949m. The current Q4 review reference remains USD3,179.343654286m
revenue / USD3,123.419115173m guide under its own existing assumptions. No Q3
FX multiplier is applied to either Q4 or Q1. The revenue worker confirmed the
retained consolidated reported-USD basis and absence of a hedge split.

Four existing Q3 timing diagnostics are isolated under the source's flat cached
FX, assumed 56% non-USD and 20% RNPL reference-contribution exposure. They are
conditional source examples, not probabilities or expected drags:

| Timing hypothesis | n | Source T-B, USDm |
|---|---:|---:|
| Equal recognition months | 1 | -2.434476 |
| First recognition month | 1 | -7.931654 |
| Last recognition month | 1 | +1.274079 |
| Prior-month payment/fixing proxy | 1 | -5.090603 |

`fx_isolated_diagnostics.csv` retains original levels, multipliers, units and
statuses. The baseline remains unchanged because financial application is
ineligible. The estimated incremental effect is **null**, not estimated zero.

## What failed or could not be done

No integrity, arithmetic or package test failed. Free-w promotion failure is
accepted L3 research evidence, not an L4 software failure. A certified central
FX/RNPL adjustment could not be produced from this bundle because the hedge
split, structural cohort inputs and later-quarter scenarios are unavailable.
This closes source consumption without relabelling those missing inputs.
No extra fitting, source collection, registry/scorer change, public publication,
outreach or investment adoption occurred. New fitted parameters: **0**.

## RESUME

Consume only `snapshot_v1`; `reproduction_v1` is its byte-identical verification.
Use the completed conversion acceptance and failed-promotion wording, replacing
old L4 claims that validation was still pending. Keep accounting eligibility
distinct: accepted conditional FX research is not a deployable central effect.
The artifact worker independently reviews this package; the source worker can
now review financial/memo claims without self-approving source implementation.
Any later supplement requires a separately supplied explicit commit, exact
source/review checks and a fresh output version. Parent preserves all earlier
files and owns final integration, local commit and unsigned team decisions.
