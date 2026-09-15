# L4 source integration v2

Consumes the explicitly accepted L3 Git bundle and checks accounting eligibility.
No research model is fitted or statistically revalidated. All old packages are
read-only. Only the two explicitly supplied QVS notes are captured from the
original workspace; their links to L3 working files are not followed.

Run from the L4 worktree root with Python's standard library:

```powershell
python -B analysis/src/forecast_methods/lane4_sources_v2/run.py --out data/processed/forecast_methods/lane4_sources_v2/snapshot_NEW --qvs-root 'C:/Users/wille/Desktop/Citadel - ABNB'
python -B -m unittest discover -s analysis/src/forecast_methods/lane4_sources_v2 -p 'test_*.py' -v
```

On this host Python is
`C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
`--stage extract` and `--stage audit` support sharing verified source copies
before the source classification completes. Every output destination refuses
overwrite. The default `all` runs both phases. Never reuse `snapshot_v1`.

The canonical bundle-containing commit is
`8821961853e4068febbfe2712f9a4e1036c9e629`, with research source
`7fb6fe0f248d5492b899672b9b70545da62d63ee`. The 108-entry manifest's SHA256 is
`9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`.
Binary `git cat-file --batch` supplies exact blobs, bypassing shell text
decoding and checkout newline conversion. Scoped `.gitattributes` preserve
new source/data bytes. The verifier checks the manifest itself, exact file
inventory, every payload, both ancestry edges, 104 source-output/note objects,
and all 32 acceptance bindings against actual research objects. Newline-only
differences have an explicit status if found; none occurred in this bundle.
No optional supplement is read without a separately authorized commit.

## Outputs

- `bundle/`: original 109 files, including the checksum manifest itself.
- `handoff/`, `qvs/`, `support_manifest.json`: explicit support sources and hashes.
- `integrity_receipt.json`, `research_lineage.csv`,
  `conversion_acceptance_bindings.csv`: immutable identity checks.
- `row_dispositions.csv`: all 1,187 rows and every original source field, plus
  distinct measurement/disposition/applicability axes, reason, stable row ID,
  source-row hash and payload foreign key/hash.
- `accounting_interface.csv`, `accounting_eligibility.json`: denominator,
  timing, pre-hedge and hedge contract definitions and missingness.
- `baseline/`: exact forecast blob from starting L4 commit
  `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`, with its hash.
- `cohort_baseline_compatibility.csv`: all 15 existing scenario/quarter rows.
- `fx_arithmetic_checks.csv`: 180 source-grid conservation/replacement checks.
- `fx_isolated_diagnostics.csv`: four existing Q3 timing conventions at fixed
  source assumptions; no financial application.
- `snapshot_checksums.json`: byte identities of all snapshot inputs/outputs
  existing at completion; does not self-hash.

`source_measurement_class` describes how a research row was obtained.
`integration_disposition` is one of observed/calculated/conditional/descriptive/
comparator/unavailable/rejected. `financial_eligibility` independently describes
whether the row may affect the financial model. No raw directly observed ABNB
cohort parameter is present among these research-adapter rows; underlying rates
and public price indices are separate observed inputs, not relabelled results.

Conversion validation is complete; free-weight promotion failed W1/W2. Keep
K0's existing fixed 2/3 seasonal estimation policy; all22 free/fixed OLS and joint
draws remain descriptive. Cohort FX is accepted conditional research but is
ineligible for the current central forecast: the source T/B denominator is not
certified pre-hedge, H and H_new are absent, u/p/currencies are assumptions, and
current scenarios cover only Q3. Missing FX is null, not an estimated zero.

For genuinely matching future inputs, the guarded identity is
`R_new=m_pre*(R-H)+H_new`. `H_new=H` must be named explicitly; missing hedges do
not qualify. `T/R0` cannot multiply reported USD kernel revenue. ADR totals
already contain their named FX/fee mechanics; replacement routes are exclusive.
Fee theta remains missing, hotel indices are comparators, and NCLH transfer FAIL
supplies no ABNB adjustment. Investment and operational adoption stay separate.

## Validation scope

Tests attack corrupt/extra manifests, content and newline bindings, unsafe paths,
missing Git objects, overwrite attempts, missing or incompatible hedge inputs,
unknown evidence schemas and invented theta values. They also verify every
source field in 1,187 rows and all 180 source accounting scenarios. The source
exports use rounded decimals; dollar identities allow at most USD1 absolute
error (USD0.000001m), and normalized weights allow 1e-9. These are arithmetic
tolerances, not economic uncertainty bounds. No L3 research runner is executed.
