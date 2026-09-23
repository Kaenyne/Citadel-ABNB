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
