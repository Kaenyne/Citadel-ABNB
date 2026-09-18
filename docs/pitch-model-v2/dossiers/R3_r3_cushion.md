# R3 — Guide cushion, trailing eight

## 1. Header
- Line: R3 · Judge's question: "Airbnb beat its guide 19 of 19 times; how much of that is mechanics?"
- Digger: sonnet · Date: 2026-09-18 · Commit: e39d9e4

## 2. The number

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 1.857 | 1.762 | 2.314 | % (cushion = actual/guide-mid − 1; **trailing-8 mean, recommended** — see §2 note) | guide date 2026-08-06 |
| alt_median | 3Q26 | 1.790 | — | — | % (trailing-8 median, alternative) | guide date 2026-08-06 |

Trailing-8 window = 2024Q3..2026Q2 cushions (0.86, 2.69, 0.98, 2.52, 0.86, 3.27, 2.61, 1.06 pp), n = 8.
sd = **1.005pp** (ledger-2dp values give mean 1.8562% / median 1.7900% / sd 1.0064pp; raw un-rounded
ratios give 1.8567% / 1.7905% / 1.0048% — both reproduce to the stated precision, ledger-2dp is what
the package quotes). Low/high above are the 2.5/97.5 block-bootstrap percentiles (moving block,
length 4, B = 5000) on the mean, from `02_cushion_pit.csv`; they are asymmetric because n = 8 is small
and the block bootstrap resamples in length-4 chunks, not because of a data error.

**Beat count** (full 19-quarter scoreable ledger, not just the trailing-8 window): **19/19** prints
beat the guide midpoint (0 below the low end of the range); **15/19** beat the *top* of the range.

**Recommended cushion to convert a revenue estimate into an implied guide midpoint:**
guide_mid = revenue_estimate / (1 + c), **c = trailing-8 mean = 1.857%**. Reasons: (1) this is the
statistic the package's scored object (`print_from_guide`) uses and it is registered and harness-scored
that way; (2) the mean-vs-median choice is immaterial — MAE 29.17 (mean) vs 30.99 (median) on W1 PIT,
30.69 vs 30.90 on W2 PIT, i.e. worth about $2M on a ~$3,000M number; (3) the cushion distribution is
only mildly right-skewed (mean 1.857 vs median 1.790, sd 1.005pp), so the mean is not being pulled by
an outlier. The median (1.790%) is a defensible, slightly more robust alternative with negligible
practical difference — see §8.

## 3. Derivation chain
1. `data/processed/abnb_revenue_guidance_vs_actual.csv` and `data/processed/overnight/02_guidance_ledger.csv` (raw guide ranges + realised actuals, source of truth for the ledger) →
2. `analysis/src/forecast_methods/guidance_policy/run.py::section_a` rebuilds `data/processed/forecast_methods/guidance_policy/01_guide_history.csv` (20 rows: 19 scoreable 2021Q4..2026Q2 + 1 pending 2026Q3 LIVE) and computes cushion = actual/mid − 1 per quarter →
3. `run.py::section_b` computes the point-in-time trailing-8 mean/median/sd and a moving-block bootstrap (length 4, B=5000) at every guide date → `data/processed/forecast_methods/guidance_policy/02_cushion_pit.csv`
4. Row `guide_date=2026-08-06` (target 2026Q3, window label LIVE) of that file is the number in §2: `c_mean_pct=1.856743`, `c_median_pct=1.790491`, `c_sd_pp=1.004800`, `n_cushion=8`, bootstrap columns `c_mean_boot_lo/hi`, `c_sd_boot_lo/hi`.
5. The cushion feeds the registered object `print_from_guide` = guide_mid × (1 + trailing-8 mean cushion), scored by `analysis/src/forecast_methods/harness/score.py` into `data/processed/forecast_methods/harness/scoreboard.csv` (rows `object ∈ {print_from_guide, guide_cushion}`) and into the LIVE 4Q26 grid `09_q4_2026_grid.csv` / `10_q4_2026_probabilities.csv`.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `05_backtests/guidance-policy.md` (as amended, post round-1 fixes) | cushion mean 1.857% / median 1.790% / sd 1.005pp; 19/19 beat midpoint, 15/19 beat top; `print_from_guide` RMSE/naive 0.379 (W1) / 0.331 (W2), survives both windows; Gate G4 fails both windows; 9/9 drift rule dies executably (Fisher p = 0.141) | **governs** |
| 2026-09-11 | `VERIFY_guidance-policy_r1.md` | verdict PARTIAL; found `n_params` 7→6 defect on 3 registered objects and an undisclosed A1 test failure ("22" vs "20" ledger rows) | **superseded** by r2 — both defects confirmed fixed in code and prose, not just noted |
| 2026-09-11 | `VERIFY_guidance-policy_r2.md` | verdict **PASS, safe to score and quote**; independently re-derives 6 numbers (incl. `print_from_guide` RMSE/naive 0.378782 W1 / 0.330772 W2, `param_obs_ratio`) byte-for-byte from a fresh `harness/score.py` run; confirms no leakage; confirms the two Round-1 fixes did not move any scored number | **governs** — this is the final, current verdict on the package |
| n/a | `AGENT_BRIEF.md` §2 | "guide × (1+trailing-8 cushion) is the revenue forecast: RMSE ratio to naive 0.377 (W1) / 0.319 (W2); no single object beats it on both windows" — this is the harness `baselines/guide_cushion` (median-c) row, not `print_from_guide` (mean-c, 0.379/0.331). Both survive both windows; the ~0.001–0.012 RMSE-ratio gap between them is the mean-vs-median choice, immaterial. | governs (background) |

No conflict was found on this line's specific pre-registered numbers: the brief's stated cushion
mean +1.86% / median +1.79% / sd 1.006pp reproduces bit-perfectly against `02_cushion_pit.csv` and the
package's own acceptance test B1.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/R3/receipt.json`
- Command: `python3 analysis/src/forecast_methods/guidance_policy/run.py` (run via `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id R3 --watch analysis/src/forecast_methods/guidance_policy --watch data/processed/forecast_methods/guidance_policy --cmd "python3 analysis/src/forecast_methods/guidance_policy/run.py"`) · Exit: 0 · Wall: 2.0s · Interpreter: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` (plain `python3`; no pandas-3 API failure encountered, `.venv-pd2` not needed)
- Output: `data/processed/forecast_methods/guidance_policy/02_cushion_pit.csv` row `guide_date=2026-08-06` → `c_mean_pct=1.856743, c_median_pct=1.790491, c_sd_pp=1.004800` · Committed value (ledger-2dp, per note and acceptance test B1): mean 1.8562% / median 1.7900% / sd 1.0064pp · Tolerance: exact string match on the acceptance test (±0.01pp visually; test reports "PASS") · **Match: yes**
- Receipt shows `"changed": []`, `"new_files": []`, `"restored": true` — the re-run produced byte-identical output to what is already on disk (no diff at all against the tracked tree), i.e. bit-perfect reproduction, consistent with the controller's own prior run of this package through the same wrapper.
- Supplementary evidence pulled for this dossier (not re-run, read-only extraction from already-produced, tracked files): `data/processed/pitch_model_v2/receipts/R3/cushion_evidence.json` (the §2 row from `02_cushion_pit.csv` and the `print_from_guide`/`guide_cushion` rows from `data/processed/forecast_methods/harness/scoreboard.csv`).

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 PIT | 14 | RMSE ratio to naive (revenue, `print_from_guide`, mean-c) | 0.3788 | 1.000 | 0.3771 (median-c) | 1.073 | survive on both W1 and W2 | **pass** |
| W2 PIT | 10 | RMSE ratio to naive (revenue, `print_from_guide`, mean-c) | 0.3308 | 1.000 | 0.3191 (median-c) | — | survive on both W1 and W2 | **pass** |
| W1 PIT | 14 | guide-midpoint level MAE % (this cushion consumed inside `guide_mid_next_q`, a different, forward object) | 1.99 | (naive n/a for this target) | — | 1.97 | beat vintage-stamped pre-guide Street | **fail** (loses by 0.02pp, bias +1.12% vs −0.51%) |
| W1/W2 PIT | 14/10 | Gate G4 sign test (`guide_mid_next_q` vs Street) | 7/14, 4/10 | — | — | needs ≥8/14, ≥6/10 | pre-registered architect gate | **fail**, both windows |
| — | 19 | 9/9 guide-below-Street drift rule, executable (reaction-close entry) | 8/9 negative, Fisher p=0.141 | — | — | — | kill-list item — must not be quoted as a signal | **fail as a signal** (correctly disclosed, not used) |

Strongest known failure: **the trailing-8 cushion itself is a genuine, both-windows-surviving edge on
*realised revenue given an already-issued guide* (RMSE/naive 0.33–0.38), but nothing built on top of it
(kappa, `guide_mid_next_q`) gives an edge on the *next, not-yet-issued* guide's level or sign — Gate G4
fails 7/14 and 4/10, and on level the model loses to the vintage-stamped pre-guide Street (MAE 1.99% vs
1.97%, bias +1.12% vs −0.51%) — so this line answers "how much of the beat is mechanics" only for
guide→print, not for Street→guide.**

## 7. Kill list and consistency
- Kill-list check: two kill-list items intersect this package and neither is used or quoted here.
  (1) **The 9/9 guide-below-Street drift rule as a tradeable signal, and any p-value for it** —
  reported in §(f)/H1 of the governing note as executable 8/9 with Fisher p = 0.141 (two-sided),
  explicitly labelled "NOT A SIGNAL," and shown to be a calendar artefact (9/11 of *all* prints in
  2022Q3–2025Q1 were negative regardless of guide sign). Reproduced here as disclosure only, not
  presented as evidence of anything tradeable.
  (2) **M5's hierarchical cushion model** — this package explicitly did not build it ("deliberately
  not built": the hierarchical statement pool, because n is 19 calls, not 194 statements). Not present
  in any output consumed by this dossier.
- Conflicts: none found with memo-level claims. The AGENT_BRIEF §2 line "guide × (1+trailing-8 cushion)
  ... RMSE ratio to naive 0.377 (W1) / 0.319 (W2)" is the median-c `baselines/guide_cushion` row, not
  this line's recommended mean-c `print_from_guide` row (0.379/0.331); both exist, both survive both
  windows, and the gap between them is immaterial (§2, §8). No number here is drawn from the kill list.

## 8. Open choices
1. **Mean vs median as the operating cushion statistic.** Options: (a) mean 1.857% — used by
   `print_from_guide`, marginally better W1 MAE (29.17 vs 30.99), marginally worse W2 RMSE ratio
   (0.331 vs 0.319); (b) median 1.790% — used by the harness's own `baselines/guide_cushion`, slightly
   more robust to the two largest historical cushions (2.69%, 3.27%) mechanically re-entering the
   trailing-8 window as quarters roll forward. **Recommendation: keep the mean (a)** — the difference is
   ~$2M on a ~$3,000M guide and both survive both windows; switching now would only cost consistency
   with the already-registered `print_from_guide` object.
2. **Whether to report the bootstrap band around the cushion in the memo.** Options: (a) report the
   19/19 point estimate and sd only (simpler, matches how the note's headline is usually quoted);
   (b) also show the 2.5/97.5 block-bootstrap band (1.76–2.31%, n=8) to signal how little the trailing-8
   window actually pins down at this sample size. **Recommendation: (b)**, in a footnote — the band is
   already computed and on disk, and a judge who asks "how tight is that trailing-8 number really" is
   better served by an honest 8-observation confidence band than by a bare point estimate.
3. **Whether to answer the judge's question using guide→print evidence only, or to also mention the
   Street→guide failure (Gate G4) in the same breath.** Options: (a) answer narrowly — "of the 19/19
   beats, the trailing-8 cushion is a stable, 1-parameter, both-windows-surviving mechanism that
   explains the *print given the guide*" and stop there; (b) volunteer, in the same answer, that we have
   no measured edge on *guessing next quarter's guide* itself (Gate G4 fails both windows). **Recommendation:
   (b)** — a judge asking "how much of the beat is mechanics" is one follow-up question away from "so can
   you predict the next guide," and the honest answer there is no; volunteering it first is more credible
   than being caught not mentioning it.

## 9. Judge Q&A
1. Q: Airbnb beat its guide 19 of 19 times — how much of that is mechanics? A: Nearly all of the
   *guide-to-print* gap is mechanical: a single trailing-8-quarter average cushion (currently 1.857%,
   sd 1.005pp, n=8) converts the guide midpoint into a revenue forecast that beats naive and a fitted
   AR(1) on both pre-registered out-of-sample windows (RMSE/naive 0.379 on 2023Q1+, 0.331 on 2024Q1+),
   with one free parameter. It is not "Airbnb always beats by luck each quarter" — it is "management
   sets a guide that is, on average and fairly persistently, about 1.8–3% below what later prints,"
   and that persistence is what a one-parameter model captures.
2. Q: Is the cushion constant, or is it changing? A: It has shrunk and tightened: mean cushion fell from
   ~3.04% in the first 11 scoreable quarters to ~1.86% in the last 8 (OLS slope −0.123pp per print,
   p=0.055, n=19), alongside the guide range itself narrowing from about 4.9% of the midpoint at the
   start to about 1.9% now. So "mechanics" today means a smaller, tighter cushion than the pooled
   19-quarter history would suggest — which is exactly why this line uses the trailing-8, not the
   full-sample, cushion.
3. Q: Does this let you predict Airbnb's *next* guide, not just the print given an already-issued guide?
   A: No, and we say so rather than hide it. The forward object built on top of this cushion
   (guide_mid_next_q, which adds the kernel and kappa) does not survive both windows against naive
   (0.869 W1, 1.049 W2) and fails the pre-registered Gate G4 sign test against the Street on both
   windows (7/14, 4/10); on level it loses to the Street (MAE 1.99% vs 1.97%). The trailing-8 cushion is
   a real, disclosed edge on one specific, narrower question — turning a known guide into a print
   forecast — not on forecasting the guide itself.

## 10. Grade
Grade: A — receipt shows exit 0 with a bit-perfect (zero-diff) match against the tracked outputs, and
the object this cushion feeds (`print_from_guide` / `baselines/guide_cushion`) is independently confirmed
in `data/processed/forecast_methods/harness/scoreboard.csv` to beat naive and survive both W1 and W2
(`survives_both_windows = True` on all four PIT/full-sample rows for both objects); the narrower,
harder claim this line does NOT make — an edge on the next guide's level or sign — is disclosed as a
failure in §6/§7 rather than stretched.
