# R5 — 4Q26 and FY26 revenue

## 1. Header
- Line: R5 · Judge's question: "Walk me from 3Q26 to FY26 revenue."
- Digger: sonnet · Date: 2026-09-18 · Commit: e6d9832 (branch `theo/pitch-model-v2`; brief names f1ce2cd / 11b3d39 was HEAD at session start, the branch moved on during the parallel wave)
- One-line answer: the walk is **H1 actual ($6,286M) + 3Q26 kernel ($4,804M, fixed by printed GBV, no scenario spread) + 4Q26 kernel (λ_Q4 12.03% × ⅔·GBV_3Q26 + ⅓·GBV_2Q26)**; on the team's own governing 3Q26 inputs (DEC-0004 nights, DEC-0008 ADR) that gives 4Q26 **$3,166M base / $3,112M short / $3,195M breaker** and FY26 **$14,256M / $14,202M / $14,285M** — about $12M (0.4%) below the bridge v3 script's own committed output, because that script still runs on nights and ADR inputs the team has since superseded.

## 2. The number

Convention, same device as D1/D4/D5: **base/short/breaker** are mechanical consequences of the stated D1 (nights) and D4 (ADR) scenario inputs pushed through the fixed R1 kernel (DEC-0006), not a separate judgment call (DEC-0016, no leaning). "bridge_as_coded" rows show what the committed script actually emits today, on its own (now-superseded) nights/ADR choices — see §4/§7 for why the two differ.

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 4Q26 | 3166.1 | 3111.8 | 3194.8 | musd | digger recompute, this dossier, 18 Sep 2026 (DEC-0004/0006/0008/0010 inputs) |
| short | 4Q26 | 3111.8 | — | — | musd | same |
| breaker | 4Q26 | 3194.8 | — | — | musd | same |
| bridge_as_coded | 4Q26 | 3178.1 | 3156.0 | 3201.2 | musd | `h2_bridge_revenue_dollars.csv`, committed 18 Sep 2026 (team-baseline nights + `v3_with_K` ADR — superseded, §4/§7) |
| street (LSEG-family) | 4Q26 | 3161 | 3158 | 3162 | musd | V1, LSEG/Yahoo/Alpha Vantage/S&P, 10–13 Sep 2026 |
| street (Zacks, footnote) | 4Q26 | 3200 | 3050 | 3700 | musd | V1, Zacks, 11 Sep 2026, n=10 (thin panel) |
| base | FY26 | 14256.1 | 14201.9 | 14284.8 | musd | digger recompute = H1 actual (6286.0) + 3Q26 kernel (4804.0, invariant) + 4Q26 kernel base |
| short | FY26 | 14201.9 | — | — | musd | same, 4Q26 short leg |
| breaker | FY26 | 14284.8 | — | — | musd | same, 4Q26 breaker leg |
| bridge_as_coded | FY26 | 14268.1 | — | — | musd | digger sum of bridge's own 3Q26+4Q26 cells (bridge emits no FY26 row); cross-checks to `40_annual.csv` base row 14268.1433 (§4) |
| street (LSEG-family) | FY26 | 14160 | 14155 | 14190 | musd | V1, 10–13 Sep 2026 |
| street (Zacks, footnote) | FY26 | 14100 | 13960 | 14210 | musd | V1, 11 Sep 2026, n=8 |
| memo short case (40_line_build, not this scenario device) | 4Q26 | 2966.0 | — | — | musd | `docs/margin-build/notes/40_line_build.md` §"The short case", 15 Sep 2026 — a disclosed-mechanism nights/RNPL path, not the D1/D4 short scenario (§7) |
| memo short case (40_line_build, not this scenario device) | FY26 | 13932.8 | — | — | musd | `40_short_case_summary.csv`, `fy26_revenue` |

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| revenue_musd | base | 4Q26 | 3178.11 | musd | bridge v3 produces this: committed cell `h2_bridge_revenue_dollars.csv`, built on team-baseline 3Q26 nights 146.8m + `v3_with_K` ADR (177.17); superseded by DEC-0004/DEC-0008, see §4/§7 |
| revenue_musd | base | FY26 | 14268.14 | musd | digger computed: bridge does not emit an FY26 row; = 1Q26+2Q26 actual (6286.00, `abnb_driver_history_quarterly.csv`) + bridge's own 3Q26 (4804.04) + bridge's own 4Q26 (3178.11) |
| revenue_musd | short | 4Q26 | n/a | musd | bridge v3 carries no short/breaker split for the revenue-dollar path; see revenue_kernel_musd below for the digger-computed scenario spread |
| revenue_musd | breaker | 4Q26 | n/a | musd | same as above |
| revenue_musd | short | FY26 | n/a | musd | same as above |
| revenue_musd | breaker | FY26 | n/a | musd | same as above |
| revenue_kernel_musd | base | 4Q26 | 3166.10 | musd | digger computed: λ_Q4 12.03% (DEC-0006) × (⅔·GBV_3Q26_base + ⅓·GBV_2Q26_actual); GBV_3Q26_base = nights 146.3m (DEC-0004) × ADR $176.88 (DEC-0008, `without_K`) = $25,877.5M; GBV_2Q26 = $27,200.0M actual (`abnb_driver_history_quarterly.csv`) |
| revenue_kernel_musd | short | 4Q26 | 3111.84 | musd | GBV_3Q26_short = nights 145.0m × ADR $173.80 (D4 §2a, DEC-0009 lap-only residual, no K) = $25,201.0M |
| revenue_kernel_musd | breaker | 4Q26 | 3194.77 | musd | GBV_3Q26_breaker = nights 147.0m × ADR $178.47 (D4 §2a, residual at last_q plus K at ceiling) = $26,235.1M |
| revenue_street_musd | street | 4Q26 | 3161 | musd | V1 §2a, LSEG-family (DEC-0013 headline row) |
| revenue_street_musd | street_zacks | 4Q26 | 3200 | musd | V1 §2a, Zacks footnote, n=10 |
| revenue_street_musd | street | FY26 | 14160 | musd | V1 §2a, LSEG-family |
| revenue_street_musd | street_zacks | FY26 | 14100 | musd | V1 §2a, Zacks footnote, n=8 |

Plainly: **the bridge v3 script produces** `revenue_musd` for 4Q26 (3178.11) as a single point with no scenario split, built on its own now-superseded nights/ADR choices. **I computed**: the FY26 sum (bridge emits none), the entire `revenue_kernel_musd` block (base/short/breaker, per the brief's exact formula, from committed DEC-governed inputs), and re-stated V1's already-governing `revenue_street_musd` rows for this line's two periods.

## 3. Derivation chain

**3Q26 → 4Q26 kernel leg (what R1's kernel actually needs):**
1. `data/processed/abnb_driver_history_quarterly.csv`, rows `1Q26`/`2Q26` → printed `gbv_musd` 29,200.0 / 27,200.0 (actual, no forecast) →
2. D1 dossier §2a (`nights_m`, DEC-0004) and D4 dossier §2a (`adr_total_usd`, DEC-0008/DEC-0009) → scenario nights/ADR for 3Q26 (146.3/145.0/147.0 m; $176.88/$173.80/$178.47) →
3. GBV_3Q26 = nights × ADR (this dossier's arithmetic, not a package run) → $25,877.5M / $25,201.0M / $26,235.1M →
4. R1 dossier §2a `lambda_q4_pct` = 12.03 (DEC-0006) applied to ⅔·GBV_3Q26 + ⅓·GBV_2Q26 (this dossier's arithmetic) → 4Q26 `revenue_kernel_musd` 3166.10 / 3111.84 / 3194.77.

**Bridge v3's own path (what is actually reproduced through the wrapper):**
1. `analysis/src/h1_to_h2_bridge_v3.py` reads the same driver-history CSV plus `data/processed/adrv3/P/adr_card_v3.csv` (variant `v3_with_K`) and `data/processed/nights_baseline_reconciliation.csv` (team baseline) →
2. computes `gbv_yoy_reported_pct` for 3Q26 (13.66%, `v3_with_K`/team-baseline) and compounds it onto the printed 3Q25 GBV level to get a 3Q26 GBV forecast (not the direct nights × ADR product used above) →
3. `lag4 = ⅔ × GBV_3Q26_forecast + ⅓ × GBV_2Q26_actual`; `revenue_musd = 1000 × lag4 × conversion_mean` (a 3-cell historical 4Q revenue/lagged-GBV ratio, ≈ 12.03%, not literally R1's labelled λ_Q4) →
4. output cell `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv`, row `4Q26`, column `revenue_musd` = 3178.107848266214.

**FY26:** H1 2026 actual (rows `1Q26`, `2Q26` of the driver-history CSV, `revenue_musd` 2678.0 + 3608.0 = 6286.0, no forecast) + 3Q26 (bridge's own kernel cell, $4,804.0M, invariant to scenario because it uses only printed GBV) + 4Q26 (either leg above, scenario-dependent).

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-12 (script header) | `analysis/src/h1_to_h2_bridge_v3.py`, `data/processed/h2_bridge_v3/` | 3Q26 nights = team baseline 146.8m; ADR = `v3_with_K` card ($177.17 / $174.57) | **superseded** by DEC-0004 (nights) and DEC-0008 (ADR variant), both 2026-09-18 |
| 2026-09-18 | `DECISIONS.md` DEC-0004 (D1) | 3Q26 nights base = 146.3m (bias-corrected reviews index), rejecting the 146.8m team baseline | **governs** |
| 2026-09-18 | `DECISIONS.md` DEC-0008 / D4 dossier §2a | 3Q26/4Q26 ADR base excludes the K line: $176.88 / $173.94 (`without_K`), rejecting `with_K` $177.17 / $174.57 as the base | **governs**; `with_K` retained as labelled sensitivity `alt_with_k` |
| 2026-09-18 | `DECISIONS.md` DEC-0009 / D4 dossier §2a | 4Q26 short-scenario ADR uses the lap-only residual (3.056pp), giving 3Q26 short $173.80 and 4Q26 short $170.94 | **governs** the short-scenario ADR used in this dossier's GBV_3Q26 |
| 2026-09-18 | `DECISIONS.md` DEC-0016 | no-leaning rule: short 3Q26 ADR stays at the lap-only $173.80, not D4's earlier mean-reversion floor $172.97 | **governs**; this dossier uses $173.80, not $172.97 |
| 2026-09-18 | `DECISIONS.md` DEC-0006 / R1 dossier | fixed kernel Revenue_q = λ_s × (⅔·GBV_{q-1} + ⅓·GBV_{q-2}); λ_Q4 = 12.03%; drives forward revenue (R2, R5) | **governs** |
| 2026-09-18 | `DECISIONS.md` DEC-0010 / D5 dossier | 4Q26 revenue FX +0.98pp base / +0.52 short / +1.45 breaker | **governs**; matches bridge v3's own `fx_pts_revenue` cell exactly (0.98) — no conflict on this one input |
| 2026-09-18 | V1 dossier §2a | Street 4Q26 revenue LSEG-family $3,161M (footnote Zacks $3,200M); FY26 LSEG-family $14,160M (footnote Zacks $14,100M) | **governs** the street row (DEC-0013 picks LSEG-family as headline) |
| 2026-09-15 | `docs/margin-build/notes/40_line_build.md` "The short case" | memo short case 4Q26 $2,966M / FY26 $13,932.8M, a disclosed-mechanism (RNPL + nights deceleration) construction, independent of the D1/D4/D5 bridge-scenario device | **coexists, does not govern this dossier's short row** — flagged as a different object in §7 |
| 2026-09-18 (kernel-lambda.md) | `05_backtests/kernel-lambda.md` | kernel `last3_ex_covid` revenue-level object: RMSE ratio 0.555 (W1) / 0.472 (W2), survives both windows; loses to guide+cushion (0.377/0.319) once a guide exists | **governs §6**; the 4Q26/FY26 point sits ahead of the 5 Nov guide, where guide+cushion is undefined |

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/R5/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id R5 --watch data/processed/h2_bridge_v3 --cmd "python3 analysis/src/h1_to_h2_bridge_v3.py"` · Exit: 0 · Wall: 0.3s · Interpreter: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`
- Output: `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv`, row `4Q26`, column `revenue_musd` = 3178.107848266214 · Committed value: 3178.107848266214 · Tolerance: ±0.01 · **Match: yes**
- Two comparison-only files (`h2_bridge_v3_vs_v1_delta.csv`, `h2_bridge_v3_vs_v2_delta.csv`) showed floating-point noise of 4.5e-13, not a real change; `restored: true` in the receipt, so no hand restore was needed. Before running, `data/processed/pitch_model_v2/receipts/D3/receipt.json` did not yet exist (checked first, per brief); D3's own receipt for the same script appeared afterward (started 15:51:47 UTC vs this run's 15:50:27 UTC) with the identical exit 0 / near-zero diff, confirming no collision.
- This receipt reproduces the **bridge_as_coded** row only. `revenue_kernel_musd` (the DEC-governed recompute) is arithmetic on committed cells, not a package run, so it is not itself the subject of a wrapper receipt — its inputs (D1 §2a, D4 §2a, R1 §2a, driver-history CSV) are each independently reproduced in their own dossiers' receipts.

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | RMSE ratio to naive, kernel `last3_ex_covid` revenue level | 0.555 | 1.000 | 0.377 (unavailable pre-guide) | 1.073 | ratio < 1.00 (beat naive) on both windows | pass |
| W2 | 10 | RMSE ratio to naive, kernel `last3_ex_covid` revenue level | 0.472 | 1.000 | 0.319 (unavailable pre-guide) | 0.871 | ratio < 1.00 (beat naive) on both windows | pass |

Strongest known failure: the fixed-kernel **mechanism** (λ, ⅔/⅓ weights) survives both windows and beats naive/AR1/pre-guide Street, but it **loses to guide-plus-cushion by a wide margin (0.555 vs 0.377 W1)** once a guide exists — the kernel's job is only the pre-guide window (2–24 Oct pitch dates, before the 5 Nov print) — and even within that job, the specific 4Q26/FY26 **point** this dossier reports is not itself a backtested object: it is the validated kernel formula fed by two grade-B, single-window/descriptive inputs (D1's bias-corrected nights, which fails its own 0.75 hurdle on both windows; D4's unidentified like-for-like ADR residual, carried forward by assumption, not measured), so the level itself carries their weaker grade, not the kernel mechanism's.

## 7. Kill list and consistency
- Kill-list check: none of §6's kill-list items (the −3.4pp Q4 FX step, "82% of Q4 FX already determined," "+4.05% fee uplift," the 9/9 drift rule, "half of ADR growth is bigger units," an FY27 level edge without its band, any drift-rule p-value, restated unearned fees, the 1.71M quote panel, "nothing beats guide×cushion," M5's hierarchical cushion, the 120-market panel, or the Stan state space) appear anywhere in this dossier's derivation.
- Conflicts:
  1. **With Street (brief's named conflict).** Bridge v3's committed 4Q26 base $3,178M sits $16–21M above LSEG-family Street ($3,158–3,162M). Recomputing on the governing DEC-0004/DEC-0008 inputs narrows this to $3,166M, $4–9M above Street — closer, not eliminated.
  2. **Bridge v3 vs the team's own later decisions.** The script's README and code both explicitly name `v3_with_K` and the "team baseline" (146.8m) as their inputs; DEC-0004 and DEC-0008 (same day, later in the decision log, and explicitly reasoned against those two choices) supersede them. The committed CSVs have not been re-run against the new decisions — a genuine staleness, not a reproduction failure (the script still reproduces itself exactly, §5).
  3. **With the memo's short case.** `docs/margin-build/notes/40_line_build.md` prints 4Q26 short $2,966M / FY26 short $13,932.8M under "The short case," a materially more bearish, disclosed-mechanism (nights deceleration to 5–8% y/y plus RNPL cost overlays) construction — **not** the D1/D4/D5 bridge-scenario short used in this dossier's `short` row ($3,112M / $14,202M). Quoting "$2,966M" as *the* model's short case without naming which construction is exactly the brief's flagged risk.
  4. **`40_line_build`'s own "base" is bridge v3's stale number, not the DEC-governed one.** `40_annual.csv` FY26 `base` = $14,268.1433M, matching this dossier's `bridge_as_coded` FY26 sum ($14,268.1M) to the cent — confirming margin-build imports bridge v3 directly and therefore also carries the same staleness downstream into EBITDA/EPS.

## 8. Open choices
1. **Patch the bridge v3 script to the governing inputs, or keep the recomputation as a side calculation?** Options: (a) edit `h1_to_h2_bridge_v3.py` (or a new `v4`) to use DEC-0004 nights and DEC-0008's `without_K` ADR as its base, so the committed CSV and every downstream consumer (`40_line_build`, margin build) update automatically; (b) leave the script as-is and carry this dossier's `revenue_kernel_musd` as the corrected number wherever R5 is quoted. — **Recommendation: (a).** Why: `40_annual.csv` already shows the staleness propagating into the cost-build base case; a one-line-per-cell fix removes a ~$12M/quarter, compounding discrepancy that nobody chose on purpose.
2. **Which "short" is the memo's bear case for 4Q26/FY26 — the bridge-scenario short ($3,112M / $14,202M) or the 40_line_build disclosed-mechanism short ($2,966M / $13,933M)?** Options: (a) bridge-scenario short only, since it is mechanically generated from the same D1/D4/D5 objects as base/breaker; (b) 40_line_build's short only, since it is the one built from a named, evidence-based mechanism (RNPL + nights deceleration) rather than a parameter perturbation; (c) both, labeled by construction. — **Recommendation: (c).** Why: they answer different judge questions (a mechanical low tail vs. a narrative bear thesis) and DEC-0016 (no leaning) argues against silently picking the milder one.
3. **Does FY26's 3Q26 leg get a scenario spread of its own?** This dossier holds 3Q26 at its kernel-invariant $4,804M in all three FY26 rows (it uses only printed 1Q/2Q26 GBV, so DEC-0006's fixed kernel gives one number, not three) — meaning all of FY26's scenario spread comes from the 4Q26 leg alone. Options: (a) keep it invariant, consistent with DEC-0006's mandate that the kernel "drives forward revenue"; (b) substitute R2's own 3Q26 scenario numbers (if/when R2 publishes a short/breaker split) to widen the FY26 band. — **Recommendation: (a) until R2 exists, then reconcile.**
4. **Street row: LSEG-family or Zacks as the printed headline?** Already decided at V1/DEC-0013 (LSEG-family); this dossier just carries that forward — confirming it should not be silently re-opened here.

## 9. Judge Q&A
1. Q: Walk me from 3Q26 to FY26 revenue.
   A: H1 2026 is booked ($6,286M). 3Q26 revenue is the kernel applied to *already-printed* 1Q/2Q26 GBV — λ_Q3 17.24% on ⅔·$27,200M + ⅓·$29,200M — giving $4,804M with no scenario spread, because nothing in that calculation is still a forecast. 4Q26 needs one forecast step: 3Q26's own GBV, which is nights × ADR from the team's 3Q26 scenario cards (146.3m × $176.88 base). Apply λ_Q4 12.03% to ⅔ of that plus ⅓ of printed 2Q26 GBV and 4Q26 comes to $3,166M base ($3,112M short / $3,195M breaker). Sum the four quarters and FY26 is $14,256M base ($14,202M / $14,285M).
2. Q: Why does your number differ from the model's own committed bridge output ($3,178M)?
   A: The committed script still runs on 3Q26 inputs the team has since replaced — a 146.8m "team baseline" nights read (DEC-0004 replaced it with a 146.3m bias-corrected read) and the ADR card's `with_K` variant (DEC-0008 picked `without_K`). Recomputing on the governing decisions brings 4Q26 down about $12M (0.4%) to $3,166M and FY26 down about $12M to $14,256M — both closer to, but still above, the LSEG-family Street ($3,161M / $14,160M).
3. Q: How much of this is actually validated, versus assumed?
   A: The kernel mechanism itself — λ by season, the ⅔/⅓ lag weights — beats naive, AR(1), trailing-4 and pre-guide Street on both point-in-time windows (RMSE ratio 0.555 W1 / 0.472 W2) and is the right tool before a guide exists. But the specific 4Q26 number also needs 3Q26's GBV, which rests on a bias-corrected nights read that fails its own validation hurdle on both windows (D1, grade B) and an ADR like-for-like pricing residual that is carried forward by assumption because it cannot be measured (D4, grade B). The formula is tested; two of its three inputs are not.

## 10. Grade
Grade: B — the bridge v3 reproduction receipt shows exit 0 and a match to committed cells (§5), and the kernel mechanism it uses survives both W1 and W2 against its pre-registered pass line (§6); it is not an A because the 4Q26/FY26 *point value* this dossier reports depends on two grade-B, single-window/descriptive inputs (D1 nights, D4 ADR residual) rather than being itself a validated forecast, and the committed bridge output it reproduces is built on nights/ADR choices the team's own later decisions (DEC-0004, DEC-0008) have superseded.
