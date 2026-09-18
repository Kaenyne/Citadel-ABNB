# D6 — GBV and the regional cross-check

## 1. Header
- Line: D6 · Judge's question: "Does nights times ADR give your GBV, and does the regional build sum to it?"
- Digger: sonnet · Date: 2026-09-18 · Commit: e6d9832 (branch `theo/pitch-model-v2`; the brief names b098ac2, which this branch has moved past — D2's dossier records the same HEAD, e6d9832, a harness-only commit)

**One-sentence answer to the judge.** Yes to both, but with a caveat on each: nights × ADR reproduces printed GBV to within **0.270%** across 1Q23–2Q26 (14 quarters), the residue being pure disclosure rounding (GBV to $0.1bn, nights to 0.1M), so the identity holds exactly and the small gap is not a modelling error; the regional build (`regional_kernel_v1`) also sums to consolidated GBV/revenue at **0.000%**, but only because it is constructed to do so from already-known consolidated actuals in every one of its 22 historical quarters — it has **zero** live regional GBV cells for 2026Q3 or 2026Q4, so it cannot yet check the decided forecast GBV numbers, only history.

## 2. The number

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 25877.5 | 25877.5 | 25877.5 | $M | 146.3M × $176.88, DEC-0004 × DEC-0008, computed 2026-09-18 |
| short | 3Q26 | 25201.0 | 25201.0 | 25201.0 | $M | 145.0M × $173.80, D1 short × DEC-0009 short |
| breaker | 3Q26 | 26235.1 | 26235.1 | 26235.1 | $M | 147.0M × $178.47, D1 breaker × DEC-0009 breaker |
| base | 4Q26 | 22925.3 | 22925.3 | 22925.3 | $M | 131.8M × $173.94, D2 base × DEC-0008 base |
| short | 4Q26 | 22427.3 | 22427.3 | 22427.3 | $M | 131.2M × $170.94, D2 short × DEC-0009 short |
| breaker | 4Q26 | 23782.6 | 23782.6 | 23782.6 | $M | 134.1M × $177.35, D2 breaker × DEC-0009 breaker |
| alt_blocki | 3Q26 | 25816.0 | — | — | $M | PREREG D-04 block (i), "backtest-winner", 2026-09-11 |
| alt_blockii | 3Q26 | 26550.0 | 25456.3 | 27643.2 | $M | PREREG D-04 block (ii) = B1's registered/reconciled block; low/high are B1's own joint-draw q10/q90, not an envelope of D1/D4 |
| history_identity | 1Q23–2Q26 | 0.270 | 0.015 | 0.270 | pct max dev | worst quarter 2024Q4 of 14; B1_TAKE_RATE_RECONCILIATION.md independently states the same ≤0.270% |

**Low/high note.** For the six decided scenario rows, low = high = point. D1's and D4's own low/high columns are each a *scenario envelope* (D1: the short-to-breaker range; D4: "the short point → breaker point," repeated identically across its own base/short/breaker rows), not independent statistical bands, so multiplying a nights low/high by an ADR low/high would manufacture a false interval rather than measure one. The only properly-derived probabilistic GBV band in the repository is B1's joint-draw result for block (ii) — sd $853.2M, q10–q90 $25,456.3–27,643.2M, ρ(revenue,GBV) = 0.7595 on 14 walk-forward quarters — quoted above as `alt_blockii`'s low/high; it corresponds to the registered block, not to the currently decided nights/ADR inputs. Building an equivalent joint-draw band for the decided block is Open choice 2 (§8).

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| gbv_musd | base | 3Q26 | 25877.544 | musd | 146.3 x 176.88 (DEC-0004 nights x DEC-0008 ADR) |
| gbv_musd | short | 3Q26 | 25201.000 | musd | 145.0 x 173.80 (D1 short nights x DEC-0009 short ADR) |
| gbv_musd | breaker | 3Q26 | 26235.090 | musd | 147.0 x 178.47 (D1 breaker nights x DEC-0009 breaker ADR) |
| gbv_musd | base | 4Q26 | 22925.292 | musd | 131.8 x 173.94 (D2 base nights x DEC-0008 base ADR) |
| gbv_musd | short | 4Q26 | 22427.328 | musd | 131.2 x 170.94 (D2 short nights x DEC-0009 short ADR) |
| gbv_musd | breaker | 4Q26 | 23782.635 | musd | 134.1 x 177.35 (D2 breaker nights x DEC-0009 breaker ADR) |
| gbv_printed_musd | actual | 1Q23 | 20400 | musd | abnb_driver_history_quarterly.csv, quarter 1Q23 |
| gbv_printed_musd | actual | 2Q23 | 19100 | musd | abnb_driver_history_quarterly.csv, quarter 2Q23 |
| gbv_printed_musd | actual | 3Q23 | 18300 | musd | abnb_driver_history_quarterly.csv, quarter 3Q23 |
| gbv_printed_musd | actual | 4Q23 | 15500 | musd | abnb_driver_history_quarterly.csv, quarter 4Q23 |
| gbv_printed_musd | actual | 1Q24 | 22900 | musd | abnb_driver_history_quarterly.csv, quarter 1Q24 |
| gbv_printed_musd | actual | 2Q24 | 21200 | musd | abnb_driver_history_quarterly.csv, quarter 2Q24 |
| gbv_printed_musd | actual | 3Q24 | 20100 | musd | abnb_driver_history_quarterly.csv, quarter 3Q24 |
| gbv_printed_musd | actual | 4Q24 | 17600 | musd | abnb_driver_history_quarterly.csv, quarter 4Q24 |
| gbv_printed_musd | actual | 1Q25 | 24500 | musd | abnb_driver_history_quarterly.csv, quarter 1Q25 |
| gbv_printed_musd | actual | 2Q25 | 23500 | musd | abnb_driver_history_quarterly.csv, quarter 2Q25 |
| gbv_printed_musd | actual | 3Q25 | 22900 | musd | abnb_driver_history_quarterly.csv, quarter 3Q25 |
| gbv_printed_musd | actual | 4Q25 | 20400 | musd | abnb_driver_history_quarterly.csv, quarter 4Q25 |
| gbv_printed_musd | actual | 1Q26 | 29200 | musd | abnb_driver_history_quarterly.csv, quarter 1Q26 |
| gbv_printed_musd | actual | 2Q26 | 27200 | musd | abnb_driver_history_quarterly.csv, quarter 2Q26 |
| gbv_identity_max_dev_pct | actual | all | 0.270 | pct | worst of 14 quarters (2024Q4: 17,552.43 implied vs 17,600 printed); cause is disclosure rounding (GBV to nearest $0.1bn = ±0.25%, nights to nearest 0.1M), matching B1_TAKE_RATE_RECONCILIATION.md §3's own 0.270% finding |
| regional_sum_dev_pct | base | all | 0.0 | pct | sum of 4 regions' `regional_gbv_k0.csv` GBV vs consolidated `gbv_musd`, 22 quarters 2021Q1-2026Q2; exact by construction (X_REGIONAL_KERNEL_OD_FX.md: "an accounting identity... not forecasting validation"); 0 rows exist for 2026Q3/2026Q4 |
| gbv_blockii_musd | alt_blockii | 3Q26 | 26550 | musd | PREREG D-04 block (ii), registered/headline block: 147.38M nights x $180.15 ADR |
| gbv_blocki_musd | alt_blocki | 3Q26 | 25816 | musd | PREREG D-04 block (i), backtest-winner block, published beside (ii): 146.3M nights x $176.47 ADR |

## 3. Derivation chain
1. Airbnb 10-Q/10-K filings and shareholder letters (KPI box: nights and seats booked, GBV, ADR), 1Q23–2Q26 →
2. `docs/pitch-model-v2/dossiers/H0_h0_history.md` (line-by-line tie-out) and `data/processed/abnb_driver_history_quarterly.csv` (columns `nights_m`, `adr`, `gbv_musd`) →
3. `data/processed/pitch_model_v2/receipts/D6/d6_recompute.py` (derived arithmetic, not a package run; reads only the committed CSV, writes only inside this receipt folder) → `d6_history_identity.csv`: `nights_m × adr` vs `gbv_musd`, max |dev| = **0.2703%** at **2024Q4** →
4. `docs/pitch-model-v2/dossiers/D1_d1_nights_3q26.md` §2a (146.3/145.0/147.0 3Q26 nights) and `D2_d2_nights_4q26_lap.md` §2a (131.8/131.2/134.1 4Q26 nights); `docs/pitch-model-v2/DECISIONS.md` DEC-0008/DEC-0009 and `D4_d4_adr.md` §2a (176.88/173.80/178.47 3Q26 ADR, 173.94/170.94/177.35 4Q26 ADR) → same script → `d6_decided_gbv.csv`: GBV = nights × ADR per scenario/period (§2a above) →
5. `docs/revenue-forecast-strategy/05_backtests/PREREG_ABNB-INT-v1.md` §1.5 and §5 D-04 (three consistent 3Q26 blocks) and `B1_TAKE_RATE_RECONCILIATION.md` §2–3 (registered block's joint-draw GBV distribution and the ≤0.270% history-identity finding) → same script → `d6_d04_comparison.csv`: decided base ($25,877.5M) vs block (i) ($25,816M, −0.24%) vs block (ii) ($26,550M, +2.60%) →
6. `analysis/src/forecast_methods/regional_kernel_v1/run.py` (reproduced through the wrapper, §5) → `data/processed/forecast_methods/regional_kernel_v1/regional_gbv_k0.csv`, `reconciliation.csv`, `summary.json`, `k0_handoff_check.json` → `d6_recompute.py` → `d6_regional_sum_check.csv`: regional GBV sum vs consolidated, 22 quarters, max |dev| = **0.000%**; and a direct check that `regional_gbv_k0.csv` has **0** rows for `2026Q3`/`2026Q4` →
7. committed line: **none**. D6 has no adopted point of its own; it certifies that (a) the identity holds to disclosure rounding in history, (b) `regional_kernel_v1` sums to consolidated GBV/revenue exactly but only as an in-sample accounting identity, and (c) the decided 3Q26 GBV ($25,877.5M) sits 2.60% above PREREG's backtest-winner block and 2.53% below PREREG's still-written headline block, a gap the team's later nights/ADR decisions have not reconciled with D-04 in writing.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `docs/revenue-forecast-strategy/05_backtests/B1_TAKE_RATE_RECONCILIATION.md` §3 | History identity check: "printed history 2023Q1–2026Q2: GBV vs nights × ADR, worst quarter **0.270%** — PASS — the letter rounds GBV to $0.1bn (±0.25%) and nights to 0.1M, so the identity is only checkable to ~0.32%. It holds in the disclosures to the rounding." Also gives the registered block's joint-draw GBV: $26,549.8M, sd $853.2M, q10–q90 $25,456.3–27,643.2M | **Governs the identity-tolerance number** (independently reproduced here to the same figure and the same worst quarter) and the block-(ii) probabilistic band |
| 2026-09-11 / 2026-09-17 | `docs/revenue-forecast-strategy/05_backtests/PREREG_ABNB-INT-v1.md` §1.5, §5 D-04 | Combining each line's own backtest-winning object breaks Airbnb's ADR-defines-GBV identity by **−3.13pp**; three consistent blocks: (i) 146.3M/$176.47/$25,816M, P(take rate ≥18.10%) = 0.88; (ii) 147.38M/$180.15/$26,549.8M (registered headline), P = 0.53; (iii) an implied-ADR hybrid, **rejected**. Card pre-registers **(ii) as headline, (i) published beside it** | **Governs the block framing and the take-rate hinge.** Superseded *in effect but not in writing* by DEC-0004/DEC-0008 below — see §7 conflict 1 |
| 2026-09-12 | `docs/revenue-forecast-strategy/05_backtests/X_REGIONAL_KERNEL_OD_FX.md` | Pre-registered pass line: "the regional reconstruction must sum to consolidated revenue within 0.3% in every quarter." Result: "quarter sums 18/18, maximum error 0.000%. The latter is an accounting identity because each cell's revenue defines its lambda; it is **not forecasting validation**." Overall verdict **"underpowered"**; measured O-D currency cells 0; eligible PIT forecasts 0/14 W1, 0/10 W2 | **Governs the regional-sum criterion and its own caveat** — reproduced here (same 0.000% and 0-cell findings) |
| 2026-09-12 | `docs/revenue-forecast-strategy/05_backtests/R_REGIONAL_REFRESH.md` | A different, non-touchable package (`l1_reconciliation_v3`) confirms "G2 matches 72/72 cells... Total quarterly GBV and Nights-and-Seats also close. This is an exact **accounting identity by construction**, not an out-of-sample validation." Flags a 2024 ex-FX ADR residual of −1.39pp; states it "does not supersede X's regional FX recomputation" | Corroborates the identity-only nature of the sum check from an independent build; not reproduced by me (outside the two packages this brief lets me touch) |
| 2026-09-18 | `docs/pitch-model-v2/DECISIONS.md` DEC-0004, DEC-0008, DEC-0009 | Fixes the model's live GBV inputs: 3Q26 nights 146.3/145.0/147.0; 3Q26 ADR 176.88/173.80/178.47; 4Q26 ADR 173.94/170.94/177.35 (`without_K` card variant) | **Governs the current model's GBV**, and postdates PREREG D-04. Its nights/ADR land on block (i)'s numbers, not block (ii)'s, without D-04 having been formally revisited (§7 conflict 1) |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/D1_d1_nights_3q26.md`, `D2_d2_nights_4q26_lap.md`, `D4_d4_adr.md` | Reproduce and grade B the nights (3Q26/4Q26) and ADR (3Q26/4Q26) factors this line multiplies | Governs the two factors of the identity; D6 owns only the multiplication and the two cross-checks, not the factors themselves |

**Web fetches: zero.** Everything above is in the repository.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/D6/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id D6 --watch data/processed/forecast_methods/regional_kernel_v1 --cmd "python3 analysis/src/forecast_methods/regional_kernel_v1/run.py"` · Exit: 0 · Wall: 2.4s · Interpreter: python3 (3.13.0, pandas 3.0.0)
- Output: `data/processed/forecast_methods/regional_kernel_v1/summary.json` cell `max_reconciliation_error_pct` = 0.0, `reconciliation_quarters` = 18, `quarterly_exact_cells` = 72 · Committed value: same (all 20 changed files were float noise, max abs diff 1.9e-6 on `regional_gbv_k0.csv`, the rest ≤1.7e-8) · Tolerance: exact match on the reconciliation metric, ≤1e-5 on float carries · **Match: yes**
- Restored: true.
- Derived arithmetic (not a package run, so not through the wrapper; reads only `data/processed/abnb_driver_history_quarterly.csv` and the reproduced `regional_gbv_k0.csv`, writes only inside this receipt folder): `python3 data/processed/pitch_model_v2/receipts/D6/d6_recompute.py` → `d6_history_identity.csv`, `d6_regional_sum_check.csv`, `d6_decided_gbv.csv`, `d6_d04_comparison.csv`, `d6_recompute_stdout.txt`. History-identity max |dev| **0.2703%** at 2024Q4 matches B1's independently-stated **0.270%** to the third decimal · **Match: yes**. Regional-sum max |dev| **0.000000%** across 22 quarters matches X's and R's own **0.000%** claim exactly · **Match: yes**.

## 6. Test record
This line is an accounting identity and a sum-to-consolidated check, not a forecast, so there is no W1/W2 backtest of "GBV" as a scored object and no naive/guide+cushion/Street baseline applies; the table uses the two packages' own pre-registered pass lines instead.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| 1Q23–2Q26 (W1) | 14 | max abs dev%, nights × ADR vs printed GBV | 0.270% (2024Q4) | n/a (identity) | n/a | n/a | B1: "checkable to ~0.32%" given disclosed rounding | PASS |
| 2021Q1–2026Q2 | 22 | max abs dev%, sum of 4 regional GBVs vs consolidated GBV | 0.000% | n/a | n/a | n/a | X_REGIONAL_KERNEL_OD_FX.md: within 0.3% every quarter | PASS, but **by construction** — X's own `registration_abstentions.csv`/`window_coverage.csv` record 0/14 W1 and 0/10 W2 live/PIT-eligible cells |
| 3Q26 / 4Q26 (live) | 0 | regional GBV split vs the decided GBV in §2a | not available | n/a | n/a | n/a | same 0.3% criterion | **NOT TESTABLE** — `regional_gbv_k0.csv` has zero rows for 2026Q3/2026Q4; only a regional *revenue* point exists (`k0_handoff_check.json`, 2026Q3 = $4,754.7M) |

Strongest known failure: the one cross-check the judge is actually asking about — the regional build reproducing the *decided* 3Q26/4Q26 GBV — cannot be run at all, because `regional_kernel_v1` has zero live regional GBV cells for those quarters; its 0.000% match is a historical accounting identity, not a forecast validation, by its own governing note's admission.

## 7. Kill list and consistency
- **Kill-list check: none.** None of this line's numbers (the 0.270% identity tolerance, the 0.000% regional sum, the D-04 block figures) appears on AGENT_BRIEF §6's kill list.
- **Conflict 1 — the block D-04 recommends is not the block the model runs on, and nobody has said so.** PREREG_ABNB-INT-v1.md (11–17 Sep) pre-registers block (ii) — 147.38M nights / $180.15 ADR / $26,549.8M GBV — as the headline, with block (i) — 146.3M / $176.47 / $25,816M — published beside it as the named alternative. DECISIONS.md (18 Sep, later, and per the brief's own rule the later note governs) fixes 3Q26 nights at 146.3M (DEC-0004) and ADR at $176.88 (DEC-0008) — matching block (i)'s nights exactly and its ADR to within $0.41 (0.23%). The decided GBV, $25,877.5M, is 2.53% ($672.5M) below the still-written headline and only 0.24% ($61.5M) above the published alternative. D-04 itself calls this "the single largest unresolved number on the card" and states it moves P(take rate ≥18.10%) from 0.53 to 0.88 — the decision has effectively been made by DEC-0004/DEC-0008, but D-04 has not been formally revisited to say so. See §8.1.
- **Conflict 2 — the regional-sum pass line is met only in the sense its own author warns against.** X_REGIONAL_KERNEL_OD_FX.md states its 0.000% result plainly: "an accounting identity because each cell's revenue defines its lambda... not forecasting validation." R_REGIONAL_REFRESH.md says the same of its own 72/72 cell match: "an exact accounting identity by construction, not an out-of-sample validation." A memo line that cites "the regional build sums to consolidated GBV/revenue" without this caveat would overstate what either package does, especially since neither has a live 2026Q3/2026Q4 regional GBV split to check the decided numbers against. See §8.2.
- **Minor consistency note.** D2_d2_nights_4q26_lap.md §7 quotes a 4Q26 ADR of "$173.55" from N memo 2 for its own illustrative revenue-gap arithmetic; the committed `without_K` 4Q26 ADR this dossier uses (DEC-0008, D4 dossier) is $173.94 — a $0.39 (0.22%) difference, immaterial to either line's conclusion but worth reconciling if both figures end up on the same slide.

## 8. Open choices
1. **Which PREREG D-04 block the model's GBV should be formally attributed to.** Options: (a) leave DECISIONS.md silent (status quo) — the model runs on block-(i)-shaped numbers without saying so; (b) add a dated correction to PREREG/DECISIONS stating that DEC-0004 and DEC-0008 supersede D-04's headline choice and formally adopt block (i), publishing block (ii) as the labelled alternative instead; (c) revert DEC-0004/DEC-0008 to reproduce block (ii)'s 147.38M/$180.15 exactly. — **Recommendation: (b).** Why: the model already computes GBV live from nights × ADR (per DEC-0007), and those inputs are now block-(i)-shaped; saying so explicitly costs a paragraph and prevents a judge who reads both PREREG and DECISIONS from finding an unexplained $672M, 2.53% gap on the line D-04 itself calls the card's largest unresolved number.
2. **Whether to publish a probabilistic GBV band for 3Q26/4Q26 alongside the point.** Options: (a) none (status quo here: point only, since D1's and D4's own low/high are scenario envelopes, not statistical intervals, and multiplying them would manufacture a false interval); (b) re-run B1's joint-draw machinery (correlation of walk-forward errors, 500,000 draws) on the currently decided nights/ADR/revenue points to get a proper sd and q10–q90; (c) quote B1's existing q10–q90 ($25,456–27,643M) as-is, explicitly labelled as the block-(ii) band, alongside the block-(i)-shaped decided point. — **Recommendation: (b) if time allows before 2 Oct, otherwise (c) with the label made explicit; not (a) for a judge-facing exhibit,** though (a) is sufficient for this dossier's own grading.
3. **Whether the memo may claim the regional build "validates" GBV/revenue for 3Q26/4Q26.** Options: (a) keep the claim as-is, citing the 0.3% pass line's 0.000% result; (b) drop the claim for the forecast quarters and keep it only as a historical tie-out statement (22/22 quarters, 0.000%); (c) build the missing live 2026Q3/2026Q4 regional GBV split (today only regional revenue exists) before claiming anything about GBV regionally. — **Recommendation: (b).** Why: X's own governing note calls the 0.000% result an accounting identity, not forecasting validation, and rates the whole package "underpowered" with 0 PIT-eligible cells; presenting it as a live cross-check for 3Q26/4Q26 without that caveat overstates what the package does.

## 9. Judge Q&A
1. Q: Does nights times ADR give your GBV? A: Yes, by definition — Airbnb defines ADR as GBV ÷ nights and seats booked, so this is an identity, not a forecast. In the printed 1Q23–2Q26 history it holds to within **0.270%** (worst quarter 4Q24), and the entire gap is disclosure rounding (GBV to the nearest $0.1bn, nights to the nearest 0.1M) — reproduced independently here and matching the governing B1 note's own 0.270% finding to the third decimal.
2. Q: Does the regional build sum to your consolidated GBV? A: Exactly, to 0.000%, in every one of the 22 historical quarters we can check (2021Q1–2026Q2) — but only because the package is built by construction to reconcile to the known consolidated actual, as its own governing note says outright ("an accounting identity... not forecasting validation"). There is no live regional GBV split for 3Q26 or 4Q26 in the package today, only a regional revenue point for 2026Q3, so the regional build cannot yet independently check the decided forecast GBV numbers.
3. Q: How does your registered 3Q26 GBV compare to the $26,550M / 147.38M nights / $180.15 ADR block in your own pre-registration? A: The decided inputs (146.3M nights, $176.88 ADR) give $25,877.5M — $672M (2.53%) below that headline block, and close (within 0.24%) to the "backtest-winner" block the same pre-registration published beside it as the named alternative. The pre-registration itself flagged this exact gap as moving the take-rate hinge probability from 0.53 to 0.88; the team's later nights and ADR decisions have moved onto the alternative block's numbers without that reconciliation being written down yet.

## 10. Grade
Grade: B — both reproductions are exit 0 (`restored: true`, `regional_kernel_v1`'s float-noise diffs cap at 1.9e-6) and every quoted number matches its governing note (0.270% history identity matches B1 to the third decimal; 0.000% regional sum matches X and R exactly), so this is a clean, corroborated reproduction — but the object itself is **an accounting identity and an in-sample construction, not a forecast**: there is no W1/W2 test for "does nights × ADR equal GBV" to survive (it is true by Airbnb's own definition), and the regional package's 0.3%-pass-line success is explicitly, by its own author's words, "not forecasting validation," with zero live regional GBV cells for the two quarters the judge is actually asking about.
