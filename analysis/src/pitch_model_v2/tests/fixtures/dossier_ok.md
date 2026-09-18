# T1 — Guide cushion, trailing eight

## 1. Header
- Line: T1 · Judge's question: "How much of the guide-plus-cushion gap is structural versus one quarter of conservatism?"
- Digger: sonnet · Date: 2026-09-18 · Commit: dff6020

## 2. The number
| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 1.86 | 1.5 | 2.2 | pct | 2026-09-11 |
| bull | 3Q26 | 2.40 | 2.0 | 2.9 | pct | 2026-09-11 |

## 3. Derivation chain
1. Airbnb 10-Q, Nights and Experiences Booked disclosure →
2. `data/processed/pitch_model_v2/kpi_nights_booked.csv` →
3. `analysis/src/pitch_model_v2/guide_cushion.py` →
4. `data/processed/pitch_model_v2/guide_cushion_output.csv`, column `cushion_pct`, row `3Q26`

## 4. Governing sources
| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | Overnight results note | guide+cushion beats naive on trailing-eight window | governs |
| 2026-08-30 | Draft memo v2 | guide+cushion untested beyond one quarter | superseded by 2026-09-11 note |

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/T1/receipt.json`
- Command: `python3 analysis/src/pitch_model_v2/guide_cushion.py --window trailing8` · Exit: 0 · Wall: 4.2s · Interpreter: python3
- Output: `data/processed/pitch_model_v2/guide_cushion_output.csv` cell `cushion_pct, 3Q26` = 1.86 · Committed value: 1.86 · Tolerance: ±0.05 · **Match: yes**
- If no: why, and what was reproducible instead.

## 6. Test record
| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 (trailing 8) | 8 | MAE | 0.31 | 0.58 | 0.31 | 0.44 | beat naive by 15% | pass |
| W2 (holdout 4) | 4 | MAE | 0.35 | 0.61 | 0.35 | 0.47 | beat naive by 15% | pass |
Strongest known failure: in 2Q24 the line understated the actual cushion by 0.4pp when occupancy mix shifted faster than the trailing-eight average could track.

## 7. Kill list and consistency
- Kill-list check: none
- Conflicts: none

## 8. Open choices
1. Whether to widen the trailing window from eight quarters to twelve — options: (a) keep trailing eight (b) move to trailing twelve — recommendation: keep trailing eight — why: W2 holdout already passes and a longer window dilutes the post-2023 regime shift.

## 9. Judge Q&A
1. Q: Why trailing eight quarters and not four? A: Four quarters is too short to average out a single guidance miss; eight is the shortest window where the naive baseline stops winning.
2. Q: Does this survive the FX lag identified in the overnight note? A: Yes, the cushion figure is computed on constant-currency nights, so the ~0.4-quarter FX lag does not enter this line.
3. Q: What breaks this thesis? A: A structural change in Airbnb's guidance conservatism (e.g. a new CFO resetting the cushion policy) would invalidate the trailing-eight average within one or two quarters.

## 10. Grade
Grade: B — reproduced with an exact receipt match, but only tested against a single trailing-eight/holdout-four split rather than the full W1/W2 pre-registered pass line.
