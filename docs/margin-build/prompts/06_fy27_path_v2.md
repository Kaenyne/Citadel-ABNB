# WS06: FY27 quarterly revenue path v2: audit and fix the PR #32 lap on real quarters, reconcile to the bridge v3 exit and WS29

Read `docs/margin-build/00_BRIEF.md` first. Slug: `06_fy27_path_v2`.

## Goal

The margin model needs a quarterly revenue path for 1Q27-4Q27 (nights, ADR ex-FX, FX points, GBV, take rate, revenue) that is consistent
with the adopted 3Q26/4Q26 view (`data/processed/h2_bridge_v3/`). Krish says the FY27 quarterly path from PR #32 "hasn't been worked on much".
Audit it, fix what is wrong in a v2, and produce base / bear / bull paths. An independent checker (WS06v) will re-derive your arithmetic.

## Inputs to read

- PR #32: `analysis/src/nights_quarterly.py`, `data/processed/nights_quarterly_total.csv`, `nights_quarterly_na.csv`, `research/notes/nights_quarterly.md`
  (the three-feature NA lap on real quarters). Memory note: FY26 reconciles, FY27 is the trade; the lap features and what would kill them.
- H2 bridge v3: `analysis/src/h1_to_h2_bridge_v3.py`, `data/processed/h2_bridge_v3/*.csv`, `docs/revenue-forecast-strategy/05_backtests/REBASE_h2_bridge_v3_nights_adr.md`.
- WS29 FY27 bridge: `data/processed/overnight/29_fy27_bridge.csv`, `29_fy27_quarterly_path.csv`, `29_bridge_assumptions.csv`, `research/notes/overnight/29_*.md`.
- `docs/revenue-forecast-strategy/05_backtests/B3_FY27_DECOMPOSITION.md` (multiplicative decomposition, band +9.2-11.5%), `PREREG_ABNB-INT-v1.md`,
  the Lane 1 term-structure and guide-surprise notes under `05_backtests/` (PR #53), `docs/revenue-forecast-strategy/AGENT_BRIEF.md` (kill list §6).
- ADR v3 card (`docs/adrv3/SYNTHESIS.md`, `data/processed/adrv3/`), FX kernel (`analysis/src/forecast_methods/fx_lag_v2/`), regional split
  (`data/processed/overnight/10_*.csv`, `docs/overnight2/SYNTHESIS.md` for the WS-D global lap), seats dilution (`data/processed/adr/15_*.csv`),
  reverse DCF Street path (`docs/reverse_dcf/SYNTHESIS.md`, `model/ABNB_market_implied.xlsx`), consensus FY27 (L0 register; WS03 output if on disk).

## What to do

1. Re-derive PR #32's quarterly nights path from its stated features and check: does the FY sum match; are the lap quarters placed on the right
   comparison base (which 2026 quarters carry the RNPL / Canada / World Cup effects and therefore which 2027 quarters lap them); does the
   exit rate of 4Q26 in bridge v3 (nights +8.1%, ADR ex-FX +4.1%) flow into 1Q27 without a jump; is the seasonal shape of nights consistent
   with 2023-2025 quarterly shares; are the ex-NA regions modelled or held flat.
2. Build `06_fy27_path_v2`: for each quarter 1Q27-4Q27 and FY27, base / bear / bull: nights y/y and level, ADR ex-FX y/y, FX points
   (spot-held-constant from the fx_lag_v2 kernel, with the +/-1sd USD variants), ADR USD, GBV, take rate (with the 3Q26 printed-take-rate
   asymmetry from the pre-registration card), revenue, and revenue y/y. Show the comparison with PR #32, WS29, B3, and consensus FY27
   (as columns, never as inputs). Document every assumption in `06_assumptions.csv` (name, value, unit, source, is_judgement).
3. Also carry 3Q26 and 4Q26 unchanged from bridge v3 into the same file so the margin model reads one path file `06_revenue_path_3q26_4q27.csv`
   (quarter x scenario x line), plus FY26, FY27 and an FY28 annual continuation (base only, growth-rate assumptions from B3 / reverse DCF, flagged).
4. Script `analysis/src/margin_build/06_fy27_path_v2/run.py` rebuilding everything from the input CSVs (exit 0), README.
5. Note `docs/margin-build/notes/06_fy27_path_v2.md`: bottom line (FY27 revenue base and band, what changed vs PR #32 and why), the quarterly
   table, the audit findings (numbered, with severity), assumptions, "For the model", RESUME.

## Pass line (pre-registered)

FY27 base revenue growth inside the B3 band (+9.2-11.5%) or an explicit argument why not; quarterly sums equal annual; 1Q27 growth within
2 points of the 4Q26 exit unless a named lap explains the difference; every number traceable to an input file.
