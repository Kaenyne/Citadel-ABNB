# L3 cohort FX/RNPL — results and reproducibility

Agent cohort_fx · 2026-09-13 · codex/lane3-full · base 1c87628 · new package cohort_fx_v1.
Elapsed active task time was not separately instrumented; no estimate is substituted for a measurement.

## Verdict

**Implementation PASS; research PARTIAL; investment adoption pending.** All 35 specified engineering tests pass; the unchanged K0 API reconstructs exactly on two targets; all eleven root output files rebuild byte-for-byte. The engine has explicit w/u/p exposure accounting, coherent currency units and incremental replacement. Observed RNPL revenue-cohort shares, fixing timing and a certified pre-hedge baseline remain unidentified. W1 n=0 and W2 n=0: no claim to forecast FX better than a baseline is supported.

The illustrative 20% RNPL exposure, 56% non-USD mix, equal recognition-month timing and flat cached-spot path changes Q3 kernel revenue by **-$2.434M**. It is a sensitivity, not a measured expected drag. Varying timing and FX can change its sign. No probability is attached and no combined forecast, guide, model, registration or trade decision is adopted.

## What ran

Preregistered in `L3_COHORT_FX_PREREG.md` at 23:02 UTC before package tests/scenarios. All shell commands used the isolated worktree as cwd. Exact interpreter commands:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -m pytest analysis/src/forecast_methods/cohort_fx_v1/tests -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 analysis/src/forecast_methods/cohort_fx_v1/run.py --out data/processed/forecast_methods/cohort_fx_v1 --fx-bundle 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE'
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 analysis/src/forecast_methods/cohort_fx_v1/run.py --out data/processed/forecast_methods/cohort_fx_v1/qa_rebuild --fx-bundle 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE'
```

Tests: exit 0, **35 passed in 4.56 seconds** (tool wall 6.59 seconds). Both full runners: exit 0, each returned 180 scenarios, 2,520 cohort/currency rows, 3,780 RNPL allocation rows and 1,080 adapter rows. Their end-to-end duration was not instrumented; asynchronous tool waits are not presented as runtime. The separate byte comparison command returned exit 0 in 0.93 tool-wall seconds:

```python
from pathlib import Path
p = Path('data/processed/forecast_methods/cohort_fx_v1')
assert all(f.read_bytes() == (p/'qa_rebuild'/f.name).read_bytes()
           for f in p.iterdir() if f.is_file())
```

No package implementation/test failures occurred in this first run. All initial research identification gaps remain gaps. No scorer or registry was invoked by this agent; lead owns frozen-score verification and publication.

## Results

Source data and dependencies are hashed in `input_manifest.csv`. USD millions are used in this note; CSV monetary units are individual USD. No consensus input appears.

| Check / object | n | Result | Interpretation |
|---|---:|---|---|
| Engineering tests | 35 | PASS | Conservation, arithmetic, boundaries, rates, provenance and counterexamples |
| Current K0 Q3 2026 reconstruction | 2 booking cohorts | $4,808.362929M; zero difference from API | Same inherited reported-USD kernel |
| Year-ago K0 Q3 2025 reconstruction | 2 booking cohorts | $4,115.571862M; zero difference from API | K0 origin 7 August 2025; FX/shares assembled retrospectively |
| Complete sensitivity grid | 180 scenarios | Executed | 3 currency-exposure x 5 RNPL-exposure x 4 timing x 3 FX choices |
| Immutable rebuild | 11 root files | Byte-identical | Includes input manifest and output checksum file |
| Historical cohort FX predictive effectiveness | W1 0 / W2 0 | Unmeasured | No fabricated historical u or p |

At the illustrative 56% non-USD composition the reference contributions allocate **65.0703% to Q2 and 34.9297% to Q1** (n=2). These are conditional reference-dollar weights, not literal 66.7/33.3 percentages and not measured stay probabilities. Current-year normalized-reference revenue is $4,703.151M. The ordinary booking translation reproduces $4,808.363M, giving a 1.0223705 level multiplier before any RNPL retiming.

Flat cached spot, illustrative foreign currency mix, equal target-month allocation:

| Assumed RNPL revenue exposure | n scenarios | Ordinary booking revenue, $M | Retimed revenue, $M | Incremental replacement, $M |
|---|---:|---:|---:|---:|
| 0% | 1 | 4,808.363 | 4,808.363 | 0.000 |
| 10% | 1 | 4,808.363 | 4,807.146 | -1.217 |
| 20% | 1 | 4,808.363 | 4,805.928 | -2.434 |
| 30% | 1 | 4,808.363 | 4,804.711 | -3.652 |
| 100% boundary | 1 | 4,808.363 | 4,796.191 | -12.172 |

For u=20% and the 56% non-USD composition (n=12 scenarios):

| Assumed fixing/recognition timing | n FX paths | Post-cache foreign USD rate x0.95, $M | Flat, $M | x1.05, $M |
|---|---:|---:|---:|---:|
| Equal July/August/September recognition months | 3 | -9.797 | -2.434 | +4.928 |
| July recognition | 3 | -7.932 | -7.932 | -7.932 |
| September recognition | 3 | -20.814 | +1.274 | +23.362 |
| June payment/fixing proxy | 3 | -5.091 | -5.091 | -5.091 |

Every cell is incremental replacement versus the same ordinary kernel, not total revenue FX. July and June were already observed at the 4 September cache cutoff, so later FX multipliers do not alter those rows. The entire 180-cell grid spans -$130.086M to +$146.012M, including 100% RNPL and 70% foreign boundary stresses; those extrema are not a forecast interval or plausible-probability bound.

For the 20%/56%/flat/equal-month example, the level effect is **+2.1853% relative to normalized reference revenue**, while model-to-model retimed YoY growth is **+16.7743%**. Reference growth is +13.0214%, giving a +3.7529pp model FX growth gap. RNPL retiming alone contributes **-0.05915pp** versus the ordinary kernel's model YoY growth, on a $4,115.572M year-ago model denominator with u_year_ago=0 (n=1 constructed comparison). These are distinct quantities; none is a forecast of management's FX disclosure.

## Accounting and economic interpretation

The companion `L3_COHORT_FX_ACCOUNTING.md` documents primary sources, timing roles, the unchanged K0 coefficients, the actual inspected R API and hedge restrictions. Confirmed RNPL reservations can retain FX exposure before payment; delay in cash does not establish the date that belongs in revenue translation. The recognition hypothesis is implemented as requested and retained as a hypothesis. The model's sensitivity changes sign because recognition-period rates can lie on either side of booking-period rates.

No RNPL booking share, L2 unpaid stock or legacy u/m solve is silently relabeled contributing revenue exposure. The new package fits **zero** parameters; it inherits K0's single seasonal lambda per illustrated target from its existing API. Seven currency shares (six independent under sum-to-one), one u per sensitivity, four chosen timing distributions, three selected FX paths and the annual reference choice are assumptions. More scenario cells do not create more observations or confidence.

## What failed or could not be done

The research acceptance line cannot pass: dated observed cohort/currency RNPL u, measured p, economic FX fixing rules, compatible hedge removal and historical cohort vintages are missing. The current example cannot tell L4 which share or timing to select. Q4/2027 combined GBV/guide forecasts are outside L3 ownership and are deliberately not manufactured to extend the illustration. The generic API supports those target quarters when L4 supplies a compatible reference/contribution table. Future dates, positive-exposure missing rates and incompatible references are errors rather than guessed values.

## L4 accepted inputs and checksum receipt

Accepted as research inputs: auditable engine, 35 tests, actual K0 contribution identity, frozen public rate table with real cutoff, conditional w/u/p tables, scenario sensitivities, distinct YoY arithmetic and replacement metadata. No absolute forecast is promoted. `l4_adapter.csv` records the exact baseline, embedded booking FX, unresolved hedge treatment and adoption gate.

Canonical files are directly under `data/processed/forecast_methods/cohort_fx_v1/`; `qa_rebuild/` preserves the identical rebuild. SHA-256:

| File | SHA-256 |
|---|---|
| output_checksums.csv | `8c5f019feffd0b275a56647c961db81b0e868a366643648c893f2cf214cec15e` |
| l4_adapter.csv | `2e0aa7e9a6bb462a483d57ec9804967abe805b4e13bea77be2448b5c4a1afccf` |
| scenario_summary.csv | `4b9d3f7ac89301b34a872466fdcd22a199ae2b7cf423e49bc2c41ab299784b3a` |
| cohort_currency_recognition_weights.csv | `fea5fdf2513215ac34df87b025840d13a43c89df1c66b6688b3bdec8887635e3` |

Git may normalize CSV line endings without a local attribute rule; lead will preserve bundle bytes and record the reviewable committed location. This agent did not stage or commit files.

## Harness change requests

None. These are L3 conditional inputs, not ABNB registrations.

## RESUME

Lead should complete independent provenance/accounting review, include only the canonical root outputs in the immutable L4 bundle, preserve their byte hashes across Git line-ending conversion, and publish the bundle's commit and location. L4 should read treatment and hedge metadata before consuming a value. The next substantive research advance requires dated currency/fixing and RNPL revenue-cohort evidence, not a larger synthetic grid. Copy to a new version for changes; retain this research PARTIAL and all boundary sensitivities.
