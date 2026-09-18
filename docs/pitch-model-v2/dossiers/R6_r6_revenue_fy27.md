# R6 — FY27 revenue and its band

## 1. Header
- Line: R6 · Judge's question: "FY27 +11% is the Street; you have +10.9% base and +4.5% short. Which is the pitch, and what is the honest band?"
- Digger: opus · Date: 2026-09-18 · Commit: e6d9832

## 2. The number

**Short answer to the judge.** The pitch's FY27 revenue line is the **base, $15,829M, +10.94%** on its
own FY26 of $14,268M (`06_fy27_path_v2`, v2b). The **+4.5% short is a scenario, not a forecast**
(DEC-0016), and it is quoted on a base it does not own: the short's own FY26 is $13,933M, so on a
self-consistent y/y the short is **+7.04%**, not +4.5%. The **honest band is not one band but three
different objects**, and the memo has to say which it is quoting — see §2b.

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | FY27 | 15828.6 | 15720.3 | 16570.7 | USD m | 06_fy27_path_v2 v2b, path built 13–14 Sep 2026 |
| base | FY27 growth | 10.94 | 9.18 | 11.52 | pct | B3 pre-registered w-band (`fy27_kernel_band_v2.csv`, 11 Sep 2026) |
| short | FY27 | 14913.5 | — | — | USD m | 40_line_build short case, 15 Sep 2026 |
| short | FY27 growth | 7.04 | 4.52 | — | pct | 7.04 on the short's own FY26 13,932.8; 4.52 is the published figure, on the **base** FY26 14,268.1 |
| breaker | FY27 | 16570.7 | — | — | USD m | 06_fy27_path_v2 v2b, scenario `bull` |
| breaker | FY27 growth | 15.14 | — | — | pct | on its own FY26 14,391.9 |
| street | FY27 | 15798 | 15758 | 15819 | USD m | LSEG-family; V1 dossier row (Yahoo 13 Sep n=43 / LSEG desktop as-of 11 Sep n=44) |
| street | FY27 growth | 11.49 | 11.32 | 11.63 | pct | LSEG desktop FY27 15,819.3 ÷ own FY26 14,189.6 (n=44 both, pull 13 Sep 01:15); vendor range from `fy27_street_edges_v2.csv` |

Scenario names are the pitch-model-v2 vocabulary (DEC-0009, DEC-0010). The revenue packages do not use
them: `06_fy27_path_v2` ships `bear / base / bull`, and `40_line_build` ships a separate `short case`.
My mapping, stated so it can be rejected (§8, choice 1): **base = 06 `base`**; **short = the
`40_line_build` short case** (this is what C4's dossier already uses for `sm_pct_rev | short`);
**breaker = 06 `bull`**, whose revenue-FX leg is *exactly* DEC-0010's breaker path (+1.45pp 4Q26,
+2.88pp 1Q27) while 06 `bear`'s is exactly DEC-0010's short path (+0.52 / −1.01). 06 `bear`
($14,948.3M, +5.53%) is therefore a **fourth** object, not the short: it lands within **$34.8M
(0.23%)** of the short case's FY27 dollar from a completely different construction, yet the two are
quoted at +5.5% and +4.5% purely because they divide by different FY26 bases.

### 2a. Model inputs (machine-readable)

`revenue_yoy_pct` is on **each scenario's own prior-year period** for all three scenarios — the
convention the 06 path already uses, applied to the short case as well so the three columns are
comparable. The published short headline (+4.5%, short FY27 ÷ base FY26) is carried as its own,
differently-named row so nothing silently overwrites it.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| revenue_musd | base | 1Q27 | 3053.1 | USD m | 06_revenue_path_3q26_4q27_v2b.csv, revenue_musd |
| revenue_musd | base | 2Q27 | 4029.0 | USD m | same |
| revenue_musd | base | 3Q27 | 5280.7 | USD m | same |
| revenue_musd | base | 4Q27 | 3465.8 | USD m | same |
| revenue_musd | base | FY27 | 15828.6 | USD m | sum of the four 2027 quarters; equals 06_annual_fy26_fy28_v2b.csv to $0.0001M |
| revenue_yoy_pct | base | 1Q27 | 14.01 | pct | 06 path revenue_yoy_pct |
| revenue_yoy_pct | base | 2Q27 | 11.67 | pct | same |
| revenue_yoy_pct | base | 3Q27 | 9.92 | pct | same |
| revenue_yoy_pct | base | 4Q27 | 9.05 | pct | same |
| revenue_yoy_pct | base | FY27 | 10.94 | pct | on own FY26 14268.1 |
| revenue_musd | short | 1Q27 | 2835.5 | USD m | 40_short_case_revenue_path.csv |
| revenue_musd | short | 2Q27 | 3763.0 | USD m | same |
| revenue_musd | short | 3Q27 | 4988.2 | USD m | same |
| revenue_musd | short | 4Q27 | 3326.8 | USD m | same |
| revenue_musd | short | FY27 | 14913.5 | USD m | sum of the four; equals 40_short_case_summary.csv fy27_revenue exactly |
| revenue_yoy_pct | short | 1Q27 | 5.88 | pct | on printed 1Q26 2678.0 |
| revenue_yoy_pct | short | 2Q27 | 4.30 | pct | on printed 2Q26 3608.0 |
| revenue_yoy_pct | short | 3Q27 | 6.56 | pct | on the short's own 3Q26 4680.9 |
| revenue_yoy_pct | short | 4Q27 | 12.17 | pct | on the short's own 4Q26 2965.9 — a lap artefact of the short's own weak 4Q26, not strength |
| revenue_yoy_pct | short | FY27 | 7.04 | pct | on the short's own FY26 13932.8 |
| revenue_yoy_pct_vs_base_fy26 | short | FY27 | 4.52 | pct | the published "+4.5%": short FY27 ÷ **base** FY26 14268.1 (mixed bases; see §6) |
| revenue_musd | breaker | 1Q27 | 3119.9 | USD m | 06 path, scenario bull |
| revenue_musd | breaker | 2Q27 | 4189.9 | USD m | same |
| revenue_musd | breaker | 3Q27 | 5559.9 | USD m | same |
| revenue_musd | breaker | 4Q27 | 3701.0 | USD m | same |
| revenue_musd | breaker | FY27 | 16570.7 | USD m | sum of the four; equals 06_annual_fy26_fy28_v2b.csv to $0.0001M |
| revenue_yoy_pct | breaker | 1Q27 | 16.50 | pct | 06 path revenue_yoy_pct, bull |
| revenue_yoy_pct | breaker | 2Q27 | 16.13 | pct | same |
| revenue_yoy_pct | breaker | 3Q27 | 15.73 | pct | same |
| revenue_yoy_pct | breaker | 4Q27 | 14.65 | pct | same |
| revenue_yoy_pct | breaker | FY27 | 15.14 | pct | on own FY26 14391.9 (v2b re-based; the superseded v1 file says 15.73 on 14318.0) |
| fy27_band_low_pct | base | FY27 | 9.18 | pct | B3 `fy27_kernel_band_v2.csv`, w = 0.33; recomputed 9.1795 |
| fy27_band_high_pct | base | FY27 | 11.52 | pct | B3 `fy27_kernel_band_v2.csv`, w = ⅔; recomputed 11.5228 |
| revenue_street_musd | street | FY27 | 15798 | USD m | V1 dossier adopted LSEG-family row (Yahoo 13 Sep 2026 15:20 UTC, n=43); LSEG desktop as-of 11 Sep is 15819.3 (n=44) |

### 2b. The honest band: four objects that are routinely confused

| # | band | FY27 growth | span | what it actually measures | may it be quoted as "the band"? |
|---|---|---:|---:|---|---|
| 1 | B3 kernel-weight band, λ fixed at w=⅔ | +9.18 to +11.52% | 2.343pp | a **fitting convention**, 99.0% of it the "print channel" (FY26 1H printed vs kernel) | pre-registered and kill-list-mandated whenever we quote an FY27 level edge — but it is an **upper bound on the w effect**, not forecast error (B3 caveat 1 says so itself) |
| 2 | same, λ **re-fit** at each w | +11.48 to +11.52% | **0.042pp** | the same object done self-consistently | this is the honest reading of the w question; `kernel-lambda` finds the quarterly analogue ($6M on the 4Q26 print) |
| 3 | B3 at w=⅔ with an RNPL/bundle **lap** in N | +8.41 to +10.24% | 1.834pp | the lap B3's own volume line does not contain | the only band in the record built from a **dated, disclosed mechanism** |
| 4 | B3's own predictive interval (sd) | ±3.68 to ±3.71pp | ~7.4pp at ±1sd | out-of-sample error, dominated by the kernel strict-PIT MAPE 2.313% (= $459.1M of $468.2M total sd) | the only one that is an actual forecast interval — and it is **wider than all three others combined** |

The scenario band on the adopted path (bear +5.53 / base +10.94 / bull/breaker +15.14%, i.e.
$14,948–16,571M) is a fifth object again: it prices nights and ADR assumptions, not the kernel.

## 3. Derivation chain

**Leg A — the pitch line (adopted path).**
1. printed KPIs (1Q26 $2,678M, 2Q26 $3,608M; GBV/nights/ADR through 2Q26) → `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv`
2. H2-26 exit → `analysis/src/h1_to_h2_bridge_v3.py` → `data/processed/h2_bridge_v3/` (3Q26 $4,804.0M, 4Q26 $3,178.1M) — R5's line, not re-run here
3. 2027 nights/ADR/GBV/FX decomposition → `analysis/src/margin_build/06_fy27_path_v2/run.py` (**not run by me**; D3 and R5 own it this wave)
4. → `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv`, rows `line = revenue_musd`, quarters 1Q27–4Q27, scenarios base/bear/bull
5. → my recompute `data/processed/pitch_model_v2/receipts/R6/recompute_fy27.py` sums those four quarters → FY27 = $15,828.6066M base, matching `06_annual_fy26_fy28_v2b.csv` to **$0.0001M**

**Leg B — the band (B3, reproduced end to end).**
1. v1 driver-base artefacts → `data/processed/forecast_methods/l1_reconciliation/`
2. → `analysis/src/forecast_methods/l1_reconciliation_v2/{data,model,project}.py` + `run.py` (the B3 package)
3. → `data/processed/forecast_methods/l1_reconciliation_v2/fy27_kernel_band_v2.csv`, column `fy27_growth_pct`, rows `kernel_w` 0.33 / 0.50 / 0.6667 = 9.1795 / 10.3547 / 11.5228
4. → `fy27_annual_object_v2.csv`, `fy27_musd` = 15,720.26 / 15,779.49 / 15,837.57

**Leg C — the short scenario.**
`analysis/src/margin_build/40_line_build/run.py` → `40_short_case_revenue_path.csv` (quarterly revenue
override, a scaling of the team path by nights/ADR deltas, **not** a re-run of the bridge kernel) →
`40_short_case_summary.csv`, `fy27_revenue` = 14,913.5115.

Legs A and B share the **same kernel** (DEC-0006: λ by season, w = ⅔). 06's λ is re-estimated from its
own KPI panel and lands within 0.03pt of B3's (`06_assumptions.csv`). They are independent only in the
**GBV driver path**, not in the conversion — so their $9M agreement on the FY27 level is weaker
evidence than it looks (§9 Q2).

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `05_backtests/B3_FY27_DECOMPOSITION.md` / `l1-reconciliation-v2` | FY27 $15,720.3–15,837.6M, **+9.18 to +11.52%** across w; GBV growth +11.5111% w-invariant; EXPLORATORY; "quote the band, never the point" | **governs** the band object and the decomposition; superseded v1's 14-line additive table (RED_TEAM F1) |
| 2026-09-11 (evening) | `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` + `00_SYNTHESIS.md` §1.5 | the 2.343pp w-band is **99% a λ-convention artefact**; re-fit λ → 0.042pp; B3's N contains **no lap, no cancellation, no pull-forward**; lap-aware FY27 = +8.41 to +10.24% | **governs** the interpretation of the band; supersedes B3 §4's "the indeterminacy is ~25× the edge" as the memo's central sentence |
| 2026-09-11 | `05_backtests/ALPHA_F_RNPL.md` / rnpl module | FY27 nights **+6.4%** (5.6–6.9) | governs the nights input the lap-aware band uses; consistent with 06 v2's +6.64% |
| 2026-09-13/14 | `docs/margin-build/notes/06_fy27_path_v2.md` + package | FY27 base **$15,829M (+10.94%)**, bear $14,948M, bull $16,571M; 7/7 pre-registered tests pass, incl. "base growth inside the B3 band" | **governs** the pitch's FY27 dollar; supersedes WS29 ($15,804M, FX line rejected by B4) and PR #32 (no FY27 object existed) |
| (same package, v2b) | `06_annual_fy26_fy28_v2b.csv`, `06_v2b_changes.csv` | 3Q26 no longer identical across scenarios; FY26 bear 14,164.8 / bull 14,391.9; **bull FY27 growth 15.14%, bear 5.53%** | **governs**; supersedes `06_annual_fy26_fy28.csv` (bull 15.73%, bear 5.17%) and the note's own bear/bull growth sentence |
| 2026-09-15 | `docs/margin-build/notes/40_line_build.md` §"The short case" | short FY27 **$14,914M (+4.5%)**; not re-audited by Codex; revenue path is a scaling, not a kernel re-run | **governs** the short scenario's dollars; its **+4.5%** growth label is superseded by this dossier's +7.04% own-base recomputation (§6) |
| 2026-09-17 | `docs/pitch-forecasts/questions/q1-27-revenue-guide-growth/research-log.md` row 18 (rev 2) | F02 median 1Q27 **guide** growth **+10.5%**, P(<10) 0.45 | **governs**; supersedes that folder's own `README.md` (still showing rev 1, +9.4%) — the README is stale |
| 2026-09-18 | `docs/pitch-model-v2/DECISIONS.md` | DEC-0006 fixed kernel for forward revenue; DEC-0010 FX by scenario; DEC-0016 no leaning | **governs** the scenario vocabulary and the "short is a scenario" framing |

Web fetches used: **none** (0 of the 5 permitted). Every number above is in the repo.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/R6/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id R6 --watch data/processed/forecast_methods/l1_reconciliation_v2 --cmd "python3 analysis/src/forecast_methods/l1_reconciliation_v2/run.py"` · Exit: 0 · Wall: 1.2s · Interpreter: python3 (3.13.0 / pandas 3.0.0)
- Output: `data/processed/forecast_methods/l1_reconciliation_v2/fy27_kernel_band_v2.csv` cell `fy27_growth_pct, kernel_w=0.6666666666666666` = 11.52282099464208 (and 9.179455505663281 at w=0.33) · Committed value: identical · Tolerance: ±0.01pp · **Match: yes**
- The wrapper reports `changed: []` and `new_files: []` on both watched trees: the package regenerates all six CSVs and both registry files **byte-identical** to the committed copies. `"restored": true`. The package's own internal identity check (multiplicative vs additive vs model growth, every w) closes at max **2.3e−14pp** against a required 0.01pp.
- Second receipt, same folder: `receipt_recompute_fy27.json` (exit 0, wall 0.2s, `changed: []`, `restored: true`), command `python3 data/processed/pitch_model_v2/receipts/R6/recompute_fy27.py` through the same wrapper. It recomputes FY27 **from the committed FY27 path CSVs** rather than re-running `06_fy27_path_v2` (D3 and R5 own that script this wave). Full console output at `stdout_recompute_fy27.txt`, tidy result at `recompute_fy27.csv` (35 rows).
  - base FY27 = 15,828.6066 vs committed 15,828.6067 (**−$0.0001M**); y/y 10.9367% vs 10.9367% (**−0.0000pp**)
  - bear 14,948.3339 (+0.0000) / 5.5315%; bull 16,570.7436 (−0.0001) / 15.1391%
  - short FY27 = 14,913.5115, exact against `40_short_case_summary.csv`; short FY26 = 13,932.7677, exact
  - B3 band recomputed 9.1795% → 11.5228%, span 2.3434pp; λ-re-fit span 0.0425pp; lap-aware 8.4094% → 10.2432%

## 6. Test record

**Pre-registered lines that exist for this object.** (i) B3's identity test — the multiplicative form,
the additive pp column and the model's own growth must agree at every w to ≤0.01pp. (ii) 06 v2's
seven-test pass line, of which the binding one is *"FY27 base revenue growth inside the B3 band
+9.18 to +11.52"*. **Neither is an out-of-sample test.** Harness format v1.0 derives `LIVE_TARGETS`
from `GUIDE_EVENTS_ALL`, so the only legal LIVE quarter is 2026Q3 and **there is no annual slot at
all**; B3 registers with `strict_windows=False` and its own §5 says LIVE rows "are scored in nothing,
so `survives_both_windows = False` on them must never be read as tested and failed." No W1/W2 result
for FY27 revenue exists anywhere in the repo, and I did not run a scorer.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| identity (all w) | 3 w-points | max abs error, multiplicative vs additive vs model | **2.3e−14pp** | — | — | — | ≤ 0.01pp | **pass** |
| 06 v2 pass line | 7 tests | tests passed | **7/7** | — | — | — | 7/7 | **pass** |
| 06 v2 pass line, binding test | 1 | FY27 base growth inside B3 band | **10.94** | — | — | — | within 9.18–11.52 | **pass** |
| repro (B3) | 8 files | byte-identity vs committed | **8/8 identical** | — | — | — | exit 0, within ±0.01pp | **pass** |
| repro (06 path, from committed CSVs) | 3 scenarios × 5 periods | max abs level error | **$0.0001M** | — | — | — | ±$1M | **pass** |
| W1 (1Q23+) | **0** | anything on FY27 revenue | **not run** | — | — | — | no annual slot exists | **not testable** |
| W2 (1Q24+) | **0** | anything on FY27 revenue | **not run** | — | — | — | no annual slot exists | **not testable** |
| out-of-sample error actually carried | 24 train q | kernel strict-PIT walk-forward MAPE | **2.313%** → sd $459.1M → **±3.19–3.23pp** of growth | — | — | — | none pre-registered | **descriptive** |
| vs Street, level (FY27) | 1 | base $15,828.6M vs LSEG $15,819.3M (n 44, obs 8 Sep, pull 13 Sep) | **+0.06%** | — | — | — | none | **on consensus** |
| vs Street, growth (FY27) | 1 | base +10.94% vs LSEG own-FY26 implied +11.49% | **−0.55pp** | — | — | — | none | **on consensus** |
| vs Street, growth (FY27), B3 w=⅔ | 1 | +11.52% vs same | **+0.04pp** | — | — | — | none | **on consensus** |

Two arithmetic failures found in the committed record, both verified line by line:

1. **The "+4.5%" short growth divides the short's FY27 by the base's FY26.** Short FY27 $14,913.51M ÷
   base FY26 $14,268.14M = +4.5231%; ÷ the short's **own** FY26 $13,932.77M = +7.0391%. The gap is
   **2.516pp**. `40_line_build`'s own summary CSV carries both FY26 numbers, so this is a labelling
   error in the note's table, not in the build. It flatters the deceleration story by 2.5 points.
2. **Two superseded bear/bull growth labels are still in circulation.** `06_annual_fy26_fy28.csv` and
   the 06 note both say bear +5.17% / bull +15.73%; v2b re-based FY26 for both scenarios and the
   correct figures are **+5.53% / +15.14%** (`06_v2b_changes.csv`). The FY27 *dollars* never moved.

Strongest known failure: the +9.18–11.52% band the kill list forces us to quote alongside any FY27
level edge measures a **λ-fitting convention** — re-fit λ self-consistently at each w and it collapses
from 2.343pp to **0.042pp** — while the object's only real out-of-sample error (kernel strict-PIT MAPE
2.313% ⇒ **±3.7pp of growth**) is larger than every band in the memo and has never been scored in
either window because the harness has no annual slot.

## 7. Kill list and consistency

- **Kill-list check.** "Any FY27 level edge without the +9.2–11.5% band" — respected: every level
  statement in §2 and §6 is paired with the band, and §2b says what the band is and is not. The
  −3.4pp Q4 FX step, "82% of Q4 FX already determined", "+4.05% fee uplift", the 9/9 drift rule and
  "half of ADR growth is bigger units" appear nowhere here. B3's **ASSUMED block** (fee +0.90pp, new
  lines +0.20, regulation −0.30, hedge 0.00) is **not** inside any dollar quoted above; B3 itself
  restates the fee line at **+0.36 to +0.59pp** at θ ≈ 0.833 and warns that at central θ the same
  migration takes **−0.62pp off FY27 GBV growth** which the GBV build does not carry.
- **Withdrawn numbers quoted by a governing note.** B3 §2 carries the fee line at **+0.90pp** from
  `00_IMPLEMENTATION_DECISIONS.md` §8.1. `fee-takerate` supersedes it; +0.90pp must not be quoted as
  ours. B3 also prints "+0.09pp edge over the Street" — true only at w = ⅔ against the 4 Sep Zacks
  vintage, and **−2.25pp** at w = 0.33; it is not a defensible edge and the audit removes the
  counterweight that made the sentence work.
- **Conflicts.**
  1. **Composition, not level.** 06 v2 and B3 agree on the FY27 dollar to **$9M (0.06%)** but disagree
     on how they got there: nights **+6.64%** vs **+9.46%**, reported ADR **+2.72%** vs **+1.88%**,
     FY26 base $14,268M vs $14,201M. Same answer, different derivative. The memo must not present the
     agreement as corroboration (§9 Q2).
  2. **B3 has no lap.** The audit is explicit: B3's N is four flat regional rates with no lap,
     cancellation or pull-forward term. The memo's narrative has a bundle lap; B3's arithmetic does
     not. 06 v2 *does* carry the lap (that is most of the +9.46 → +6.64 nights gap), so the pitch line
     and the band come from models that disagree about whether the lap exists.
  3. **Quarterly shape.** 06 base runs +14.0 / +11.7 / +9.9 / +9.1 through 2027; LSEG runs
     +12.4 / ~+11 / ~+11 / +11.6. Our decel is front-loaded and the Street's is not — that is the
     tradable disagreement, and it is a *shape* claim, not a level claim.
  4. **1Q27 guide.** F02 rev 2 median **+10.5%** (governing) against our 1Q27 revenue +14.0% (base)
     and +5.9% (short). These are different objects — a *guide* midpoint vs a *print* — and the
     cushion (R3: +1.86% mean) takes the implied 1Q27 print to ~+12.6% ($3,014M); the residual
     **~1.5pp** to our $3,053M is unexplained and belongs in R4/E2, not here.
  5. **Consistency with R5 / D3.** I did not run `h1_to_h2_bridge_v3.py` or `06_fy27_path_v2/run.py`;
     both FY26 exits used here are read from their committed outputs, so R5's and D3's numbers are
     inputs to mine by construction and cannot disagree unless they re-run and the outputs move.
  6. **Street row.** I quote V1's adopted `street_revenue_musd` FY27 = **$15,798M**, but compute the
     Street's *growth* from the LSEG desktop pull ($15,819.3M ÷ $14,189.6M, both n=44, same pull) so
     numerator and denominator share a vintage — A1's rule. Zacks' $15,740M (n=13) is the footnote row
     per DEC-0013 and is **not** independent of the LSEG family for Yahoo/Alpha Vantage.

## 8. Open choices

1. **Which band the memo quotes for FY27.** Options: (a) B3's pre-registered **+9.18 to +11.52%**, as
   the kill list mandates; (b) the λ-re-fit **+11.48 to +11.52%**, which is the same object done
   self-consistently; (c) the lap-aware **+8.41 to +10.24%**; (d) B3's predictive interval, **±3.7pp**
   around the point. — **Recommendation: quote (a) as the pre-registered band *and immediately say
   what (b) does to it*, then pitch (c) as the variant view.** Why: (a) is what we pre-registered and
   the kill list is written around it, so dropping it silently looks like moving the goalposts; but
   the first judge who re-fits λ gets (b) and the 2.34pp counterweight disappears. Stating both
   converts our weakest sentence into a demonstration that we audited our own work. (d) is the honest
   forecast interval and should appear once, in a footnote, because it swallows everything.
2. **Which FY27 revenue line is "the pitch".** Options: (a) 06 v2 base **$15,829M / +10.94%**;
   (b) B3 w=⅔ **$15,838M / +11.52%**; (c) a lap-aware midpoint near **$15.5–15.6bn / ~+9.3%**. —
   **Recommendation: (a).** Why: it is the only build with real 2027 quarterly *levels* that sum, it
   carries the dated lap, it passes its own 7/7 pre-registered line, and B3 is labelled EXPLORATORY by
   its own authors. (b) stays as the decomposition exhibit. (c) is not in any package and would have
   to be built — do not invent it at the memo stage.
3. **How the short case is labelled.** Options: (a) correct the headline to **+7.04%** (short FY27 on
   the short's own FY26) and state FY26 $13,933M alongside; (b) keep **+4.5%** and label it
   explicitly "FY27 short vs FY26 base, i.e. the two-year step down from the base path";
   (c) publish both. — **Recommendation: (c), with (a) as the headline.** Why: +4.5% is not a y/y and
   a judge who divides $14,914 by $13,933 will find +7.0% in fifteen seconds. Per DEC-0016 this is a
   scenario either way and must be labelled as such on the slide.
4. **Whether 06 `bear` or the 40 short case is the pitch-model-v2 `short` revenue row.** They land
   $34.8M apart on FY27 ($14,948M vs $14,914M) from different constructions; C4's dossier already
   uses the 40 short case. — **Recommendation: adopt the 40 short case as `short` and carry 06 `bear`
   as a labelled sensitivity**, so the cost stack and the revenue stack are on one object. Flag to
   Theo: if the 06 FX scenario legs are what defines short/breaker (DEC-0010), 06 `bear` is the more
   literal `short` and C4 would need re-pointing.
5. **Fix the two stale growth labels before the memo freeze.** `06_annual_fy26_fy28.csv` and the 06
   note say bear +5.17 / bull +15.73; v2b says +5.53 / +15.14. — **Recommendation: quote v2b and add
   one line to the 06 note**; this is D3's package, not mine, so it is a request, not an edit.
6. **The F02 question folder README is stale** (rev 1, +9.4%) against research-log rev 2 (+10.5%). —
   **Recommendation: whoever owns E2/R4 refreshes that README**; I did not edit it (out of scope).

## 9. Judge Q&A

1. Q: "Which is the pitch — +10.9% or +4.5%?"
   A: +10.94%, $15,829M, is the forecast; the short case is a scenario and per our own standing rule
   no input is chosen to match a priced downside. And the short's headline is mis-stated: +4.5%
   divides its FY27 by the base path's FY26. On its own FY26 of $13,933M it is **+7.0%**. So the
   honest statement of the disagreement is: our base is on the Street's FY27 dollar; our short says
   FY26 exits $335M lower and FY27 grows 7%, not 11.5%.

2. Q: "Two of your models land within $9M of each other on FY27. Isn't that corroboration?"
   A: No, and we say so in the memo. They share the same kernel — λ by season, ⅔/⅓ — so the only
   independent part is the GBV path, and there they disagree materially: nights +6.6% against +9.5%,
   reported ADR +2.7% against +1.9%. Two different compositions reaching the same dollar is evidence
   that the FY27 *level* is not informative about the composition, which is exactly why we pitch the
   composition and the quarterly shape rather than the level.

3. Q: "Your band is 2.3 points wide because of a weight you chose. Re-fit λ and it vanishes, doesn't it?"
   A: Yes — and we did that ourselves before you asked. Re-fit λ self-consistently at each w and the
   band goes from 2.343pp to **0.042pp**; `kernel-lambda` finds the same at quarterly horizon, $6M on
   the 4Q26 print. So the published band is an upper bound on a fitting convention, not forecast
   error. With that counterweight removed, the largest *identified* term in FY27 is the bundle/RNPL
   lap — worth **−1.1 to −3.2pp** of growth against the vendor-stamped Street, or −0.5 to −1.6
   EV/EBITDA turns — and the honest competitor to it is the dollar, at ±2.3pp per one-sigma FX move.
   The real forecast interval on a pure-kernel FY27 is ±3.7pp, driven by the kernel's own strict-PIT
   walk-forward error of 2.313%, and no FY27 object in this repo has ever been scored, because the
   harness has no annual slot.

4. Q: "Where does FY27 actually decelerate, and how would we know early?"
   A: In the first half. Base runs +14.0% in 1Q27 then +11.7 / +9.9 / +9.1; the Street runs roughly
   +12.4 / +11 / +11 / +11.6. The kernel carries 2H26's ~+13% GBV into 1H27 revenue while nights step
   down to ~6% as the bundle laps, so the revenue decel shows up a quarter *after* the nights decel.
   The first read is the 1Q27 guide on 11 Feb 2027 — F02's median is **+10.5%** against a 1Q26 comp of
   +17.9%, with P(<10%) 0.45.

## 10. Grade
Grade: B — both reproductions are exit 0 with byte-identical outputs and the recomputed FY27 matches
the committed CSVs to $0.0001M, but the object is **descriptive and untested**: harness v1.0 has no
annual slot, so no FY27 revenue number in this repo has ever been scored in W1 or W2, the only
pre-registered lines it passes are internal identity and in-band checks, and the band it is required
to quote collapses to 0.042pp under a self-consistent λ re-fit.
