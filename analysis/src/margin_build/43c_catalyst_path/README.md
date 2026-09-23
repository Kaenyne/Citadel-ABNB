# 43c — catalyst path for the cost leg

Rebuild:

```
py -3.13 -X utf8 analysis/src/margin_build/43c_catalyst_path/run.py
```

Exit 0; runs in about two seconds; reads only files already in the repo (financial panel, peer prints, the C04×C09 joint,
the 40 line build). No web, no scraping, nothing overwritten.

Outputs in `data/processed/margin_build/43c_catalyst_path/`:

| file | contents |
|---|---|
| `43c_e2023_test.csv`, `43c_e2023_summary.csv` | the pre-registered E-2023 test (S&M deceleration → nights, ABNB vs BKNG/EXPE) |
| `43c_e2526_regional.csv`, `43c_e2526_summary.csv` | regional nights growth from the letters vs the 2024 average through the paid-growth step |
| `43c_decision_tree_5nov.csv` | five 5 Nov branches from the audited joint, Street FY27 response, moves on 42's slope range and at a constant multiple |
| `43c_decision_tree_overlays.csv` | R05, B03 and C01 overlays that are not cells of the joint |
| `43c_decision_tree_11feb.csv` | the February branch from B12 / F03 |
| `43c_watchlist.csv` | 5 Nov disclosures with confirm / refute thresholds |

Pre-registration: `docs/margin-build/notes/43c_prereg.md`. Note: `docs/margin-build/notes/43c_catalyst_path.md`.
