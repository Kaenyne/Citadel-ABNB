# L3 cohort FX/RNPL — final v2 receipt

Agent cohort_fx · independent reviewer nclh · 2026-09-13 · codex/lane3-full.
Preserves v1 and its original results; canonical code is `cohort_fx_v2`.

## Verdict

**Implementation PASS after independent audit; research PARTIAL; investment adoption pending.** Forty-six tests pass, all four independent rate-integrity attacks are now rejected, and all eleven final files rebuild byte-for-byte. The audit repairs leave every economic scenario and rate value unchanged. The limitations in `L3_COHORT_FX_ACCOUNTING.md` still govern: u and p are unidentified revenue-cohort sensitivities, recognition FX is a working hypothesis, the reported-kernel hedge basis is unresolved, and historical predictive evidence is W1 n=0/W2 n=0.

Canonical outputs: `data/processed/forecast_methods/cohort_fx_v2/results_v2/`.
Rebuild: `data/processed/forecast_methods/cohort_fx_v2/results_verify_v2/`.
The files directly under `cohort_fx_v2/` preserve the earlier pre-period-coverage checkpoint and are not canonical. All `cohort_fx_v1` files likewise remain audit history.

## Audit findings and repairs

Independent review found that direct input could (1) claim a quote after its source vintage, (2) claim an observed period with a cutoff outside that period, (3) call one 2025 quote a complete annual reference, or (4) call one quarter-end quote a quarterly average. None was present in the actual frozen input, but all could undermine future use.

The saved pre-test repair protocols are `L3_COHORT_FX_AUDIT_REPAIR_v2.md` and `L3_COHORT_FX_PERIOD_COVERAGE_v2.md`. V2 validates quote/source/period temporal coherence, treats date-only vintages as UTC close, requires annual daily coverage, and checks observed-period weekday coverage, endpoints and internal gaps. These are data-integrity gates, not fitted market parameters. USD identity metadata is also coherent with its source date. Each source rate and observation remains distinct from the hypothetical RNPL fixing date.

The first v2 test run returned **42 passed / 1 failed** in 8.08 seconds (exit 1): pandas' default single-format inference rejected a deliberately mixed date-only/intraday timestamp fixture. The failure was repaired with explicit `format="mixed"`, then 43 tests passed in 3.64 seconds. After adding the independent period-coverage attack and variants, the final suite returned **46 passed in 5.80 seconds** (exit 0, tool wall 8.46 seconds). The independent reviewer separately ran all 46 tests in 3.50 seconds and reproduced each of the four attacks' rejection. See `L3_COHORT_FX_INDEPENDENT_REVIEW_v2.md`; the initial findings remain in its v1 counterpart.

## Final execution and preservation checks

Exact commands from the isolated repository root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -m pytest analysis/src/forecast_methods/cohort_fx_v2/tests -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 analysis/src/forecast_methods/cohort_fx_v2/run.py --out data/processed/forecast_methods/cohort_fx_v2/results_v2 --fx-bundle 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE'
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 analysis/src/forecast_methods/cohort_fx_v2/run.py --out data/processed/forecast_methods/cohort_fx_v2/results_verify_v2 --fx-bundle 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE'
```

Both final runners exited 0 and returned 180 scenarios, 2,520 cohort/currency rows, 3,780 allocation rows and 1,080 adapter rows. End-to-end runner duration was not captured reliably; asynchronous wait durations are not substituted. The final eleven-file byte comparison exited 0 in 0.43 tool-wall seconds:

```python
from pathlib import Path
p = Path('data/processed/forecast_methods/cohort_fx_v2/results_v2')
q = p.parent / 'results_verify_v2'
assert len(list(p.iterdir())) == 11
assert all(f.read_bytes() == (q/f.name).read_bytes() for f in p.iterdir())
```

| Preservation / audit object | n | Result |
|---|---:|---|
| Independent malformed-input attacks | 4 | Rejected |
| Final tests | 46 | PASS |
| Final reconstruction files | 11 | Byte-identical |
| Economic output files versus v1 | 6 | Byte-identical |
| FX rate and reference numerical fields | All 252 rate rows | Identical |
| Adapter value fields | 1,080 | Identical |

The six byte-identical economic files are kernel_identity, kernel_inputs, scenario_summary, cohort_currency_detail, cohort_currency_recognition_weights and yoy_bridge. The rate table changes only three USD identity cutoff metadata rows; numerical rates do not change. Adapter source/version labels, input/code manifests and checksums appropriately change. No frozen module, data file, registry or scorer was modified by this package.

## Decision-useful result remains conditional

At 20% assumed contributing-revenue RNPL exposure, 56% assumed non-USD currency mix, equal recognition-month timing and flat cached spot, the incremental Q3 timing replacement is **-$2.434M**, on the unchanged inherited **$4,808.363M** ordinary kernel (n=1 scenario). It is not an expected drag. The matching replacement multiplier is about **0.999494**; the reference-basis FX level multiplier must not be applied to the reported kernel. Other timing and FX assumptions change the sign. The full 180-cell grid and separate model-to-model YoY arithmetic retain the original qualified interpretation in `L3_COHORT_FX_RESULTS.md`.

Accepted L4 inputs are the repaired API, explicit contribution/timing weights, public rate/provenance table, conditional scenarios and replacement metadata. New fitted parameters: zero. No migration, stock-to-flow bridge, causal RNPL effect, hedge forecast, probability, guide forecast or investment decision has been inferred.

## Frozen hashes and handoff

| Canonical file | SHA-256 |
|---|---|
| output_checksums.csv | `733d20de4a0f767d6f3c82dd90cb0190482765a03d4df9d139b0ee80ca5edebc` |
| l4_adapter.csv | `e16d610554b64d9537ed4b3e7e4a36854b27cbb3e9dbda62f6d9229c7f74443f` |
| scenario_summary.csv | `4b9d3f7ac89301b34a872466fdcd22a199ae2b7cf423e49bc2c41ab299784b3a` |
| rates.csv | `22b06c7178f8c8c39a6572eb060edd7ebf948ed61d163866b9e098ca319fbf79` |

Reviewed engine SHA-256: `b6cf645f3b265475f5c676e17526bcb3f656950bcc79e7b5d34b4de200256860`.
Runner SHA-256: `7e0eb300fedef876a59ff7ea3fa97ba6df5408314d720da939d1da0c17f8d859`.

Package-relative adapter source labels use `cohort_fx_v2/scenario_summary.csv`. The lead should copy canonical contents to a `cohort_fx_v2/` folder in the L4 bundle or map those labels to its exact bundled location. The bundle must include the accounting and independent-review notes. The external R bundle is hashed as an inspected interface dependency and is never copied or required to run the financial calculations.

## RESUME

Lead may freeze and publish this independently accepted implementation as conditional L3 research inputs, preserving its file bytes and final code commit. L4 should consume only final v2 canonical outputs, verify the baseline being replaced, retain the unresolved hedge/u/p labels and refrain from selecting an investment scenario without the appropriate evidence or team decision. Future data or model changes require a new version; original findings and all v1/v2 checkpoints remain preserved.
