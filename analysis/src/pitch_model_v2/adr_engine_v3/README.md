# adr_engine_v3 — the ADR line with the 22 Sep audit's corrections

A copy of `adr_engine` (the ADR line v1/v2, Theo) with the corrections from
`docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md`, one commit per fix so each can be accepted or rejected on its own.
`adr_engine` and its tracked outputs are untouched (CLAUDE.md rule 1: copy, never overwrite).

```bash
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.adr_engine_v3.run --no-posterior --no-workbook --no-refresh-prices
PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests -q
```

- Outputs: `data/processed/pitch_model_v2/adr_engine_v3/`. Figures: `docs/pitch-model-v2/lines/figures/v3/`.
- Frozen inputs v3 does not rebuild (FX daily files, the geo-mix country panel and price levels, the OD tilt, the
  posterior draws) are copied once, read-only, from `adr_engine`'s outputs (`config.SEED_FILES`).
- The workbook stage is disabled: it writes `model/`, which is protected.
- The PyMC posterior is not re-run (`--no-posterior`); its draws are seeded from `adr_engine`.

The corrections and their before/after numbers are in `docs/pitch-model-v2/lines/adr_v3_corrections.md`.

| fix | where in the code | switch to reproduce v2 |
|---|---|---|
| (a) V1 FX beside V0 | `fx_diagnostics.py`, `run.py`, `assemble.py` (`fx_pp_v1`, `adr_usd_fx_v1`) | read the V0 columns |
| (b) falsifier | `fx_falsifier.py`; `docs/pitch-model-v2/lines/adr_fx_prereg.md` section 11 | not an engine output |
| (c) one construction | `exfx.construction_offsets()`, `forward()` `basis_adj`; `exfx_construction_cases.csv` | `exfx.CONSTRUCTION_FIX = False` |
| (d) downside rows | `exfx.core_mean_2023_25()`, `exfx.core_ar1()` | `exfx.CORE_FIX = False` |
| (e) sub-regional netting | `exfx.alternatives()` | `exfx.SUBGEO_NETTING = False` |
| (f) bundle band | `exfx.BUNDLE_BAND` | set to (0.8, 1.2) |
| (h) labels | `assemble.build()` `note`, `band_basis` | — |

`compare_v2.py` writes `v3_vs_v2_path.csv` and `v3_vs_v2_ladder.csv` (every rule, 3Q26 and 4Q26, both FX legs).
Tests: `tests/test_adr_engine.py` and `tests/test_geomix.py` (copied), `tests/test_v3_fixes.py` (one block per fix).
