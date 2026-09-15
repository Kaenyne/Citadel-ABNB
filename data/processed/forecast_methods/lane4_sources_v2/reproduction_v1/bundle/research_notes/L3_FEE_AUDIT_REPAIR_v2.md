# L3 fee consumer — independent review repairs

Lead · 2026-09-13 · codex/lane3-full. Supplements L3_FEE_RESULTS_v1.md; original outputs and preregistration preserved.

Independent reviewer `adr_hotel` constructed adversarial panels and found four material input/gating defects. All four are repaired in the new uncommitted implementation; canonical reviewed outputs are `data/processed/forecast_methods/fee_panel_v1/reviewed_v2/`.

| Finding | Repaired behavior | Regression |
|---|---|---|
| Unknown room/size/host-class strata could escape the primary overlap gate | Every observed stratum within known-residence population gates, including unknown non-residence attributes | Known-residence unknown-room group loses all post rows: blocked despite strong pooled overlap |
| Full-wave outputs discarded unknown-residence descriptive overlap | Separate all-descriptive and known-residence-primary populations exported | Unknown-residence overlap retained, never primary treatment |
| Missing Mexico country label silently received the standard fee denominator | Known-residence primary rows require explicit two-letter listing country | Missing listing country raises rather than returning biased theta |
| Later metadata could assign residence to the pre-capture panel | Source metadata must exist on/before each actual capture date | September 18 metadata cannot label September 14 observations |

The revised suite also explicitly rejects missing metadata dates. Tests: `python -m pytest analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py -q`, exit 0, **18 passed in 7.33 seconds**. The repaired offline run is `python analysis/src/forecast_methods/fee_panel_v1/run.py --as-of 2026-09-13 --out data/processed/forecast_methods/fee_panel_v1/reviewed_v2`, exit 0. All empirical conclusions remain partial: scheduled captures n=0, no theta, no precision interval, and the dry run has 6/225 residence-known rows. The synthetic counterexamples are validation fixtures, never evidence about Airbnb pricing.

Parameter count and original pass lines are unchanged. The updated code gives the exact preregistered meaning to residence exclusions and coverage strata. It does not widen capture scope or infer new fee economics.

## RESUME

Use the reviewed_v2 L4 input file and preserve both original and reviewed receipts. The reviewer should rerun the adversarial cases against the repair. Future data must enter new output directories and retain actual capture dates, pre-capture metadata dates, explicit fee regimes and all descriptive coverage. No fee uplift can be adopted from current n=0 output.
