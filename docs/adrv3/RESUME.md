# ADR v3: resume notes

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Branch:** `krish/adr-v3`, worktree `C:\Users\krish\citadel-abnb-adrv3`, based on main 5bd2d08. Not pushed. Read `docs/adrv3/SYNTHESIS.md` first, then `docs/adrv3/BRIEF.md` for the pre-registered criteria.

## What is on disk

| Path | What |
|---|---|
| `docs/adrv3/BRIEF.md` | the run's brief and the pre-registered criteria (do not edit) |
| `docs/adrv3/SYNTHESIS.md` | the answer, card v3 next to card v2 and the H card, one row per workstream, the pitch reading, next steps |
| `research/notes/adrv3/S_*.md`, `K_*.md`, `L_*.md`, `M_*.md`, `N_*.md` | the five Phase 0 and Phase 1 notes |
| `analysis/src/adrv3/S1_scoring.py` | the harness (importable, no side effects); `S2_rescore_v2.py` rescored every J3 variant |
| `analysis/src/adrv3/K1..K4`, `L0..L4`, `M1..M6`, `N1..N2` | Phase 1 scripts, all `py -3.13`, offline; M1 needs the main-tree listings dumps and rebuilds a 204 MB cache (not committed) in about two minutes |
| `analysis/src/adrv3/P1_card_v3.py` | card v3 (both variants, three FX estimators, both 4Q26 nights cases), the term table with memo lines, the card's own S-harness walk-forward |
| `analysis/src/adrv3/P2_score_sheet.py` | the 5 November score sheet (command-line arguments = the printed numbers) |
| `data/processed/adrv3/P/adr_card_v3.csv` | 18 rows: quarter x variant x FX estimator x nights case; every row carries `source`-style columns (`mix_source`, `nights_case_source`, `band_basis`, `label`) |
| `data/processed/adrv3/P/P1_card_v3_terms.csv` | 48 rows: every term in the point per quarter and variant (lo, point, hi, source, label) plus the memo lines (L, M, H fee increment, card v2, H card, naive, consensus) |
| `data/processed/adrv3/P/P1_card_v3_backtest.csv` | S.score rows for the benchmarks, the plain last_q rule and the exact v3 point specification (last_q + measured mix + K line), with `S_preregistered_pass` and the K-criterion flag |
| `data/processed/adrv3/P/P1_card_v3_pass_table.csv`, `P1_card_v3_backtest_paths.csv` | the pass tables and the per-quarter scored paths (the score sheet extends the paths by one quarter) |
| `data/processed/adrv3/P/P2_score_sheet_dry_run.txt` | the score sheet run at the card's own point, so the format is visible |
| `data/processed/adrv3/S/`, `K/`, `L/`, `M/`, `N/` | Phase 0 and Phase 1 outputs, read by P1 and P2, untouched |

## How to re-run

From the worktree root, in this order (P1 reads S, K, L, M, N outputs and the I mix terms; P2 reads P1's outputs):

```
py -3.13 analysis/src/adrv3/P1_card_v3.py
py -3.13 analysis/src/adrv3/P2_score_sheet.py --nights 146.8 --adr 177.17 --fx -0.43 --exfx 4 --q4-nights-guide 8.1 --q4-revenue-guide 3134 --out data/processed/adrv3/P/P2_score_sheet_dry_run.txt
```

P1 takes seconds, asserts that it reproduces S's `v3_preregistered_result.csv` to 1e-9 and K's `K3_residual_rule_scores.csv` for the K primary rule, and prints `S.preregistered_pass` for both variants (PASS, 4 of 4, for both as of 11 September). P2 prints the sheet and writes it to `--out`; the only required arguments are `--nights` and `--adr`. On 5 November replace the placeholder arguments with the printed numbers (add `--regional NA=.. EMEA=.. LatAm=.. APAC=..` if the letter gives buckets and `--bundle-figure <points>` if management restates the product-bundle contribution) and write to a dated file. `--variant without_K` scores the pre-registered v3 point instead of the with-K point; the sheet shows both in the walk-forward section regardless.

## What T requires

T is the September Inside Airbnb dumps (landing 10 to 30 September; probe the CDN daily). When the listings, reviews and calendar files for September are in the main-tree raw directories (`C:\Users\krish\citadel-abnb\data\raw\inside_airbnb\`, `inside_airbnb_reviews\`, `inside_airbnb_calendar\`, with manifests), re-run:

1. `analysis/src/q3nowcast/E1_inventory_and_discover.py` through `E7_report.py` (stays index, regional split) and `F0b_cdn_dense_probe.py`.
2. `analysis/src/adrq3/I1b_party_size_windows.py` (refreshes `data/processed/adrq3/I/I_mix_terms_3q26.csv`, which P1 reads); `I3_geo_mix.py` as well if E's regional split moved.
3. `analysis/src/adrv3/M1_dump_census.py`, `M2_new_listing_premium.py`, `M3_new_listing_share.py`, `M4_term_quarterly.py`, `M6_term_3q26.py` (M5 does not change until a scored quarter is added; the M term is a memo line either way).
4. `analysis/src/adrv3/P1_card_v3.py`, then the P2 dry run again so the placeholder point matches the refreshed card.

S, K, L and N do not re-run on a dump. Then freeze the card the week of 21 September for the 2 October pitch. Commit only your own paths (`git add analysis/src/adrv3/P* data/processed/adrv3/P docs/adrv3/`); never push from the worktree.
