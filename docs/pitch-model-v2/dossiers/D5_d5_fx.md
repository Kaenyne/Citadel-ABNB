# D5 — ADR FX and revenue FX by quarter

## 1. Header
- Line: D5 · Judge's question: "How much of 4Q26 revenue growth is FX, and is it already known?"
- Digger: sonnet · Date: 2026-09-18 · Commit: e39d9e4

## 2. The number

Scenario labels are mine, not the package's own names, and are an interpretation (see §8, choice 1).
The package's three native paths are `spot_held` (FX held at the last FRED print, 2026-09-04),
`usd_strong_-1sd` (−5% parallel dollar shift, about one std. dev. of a two-quarter move) and
`usd_weak_+1sd` (+5% shift). I map these to **base = spot_held**, **short = usd_strong_-1sd** (a
stronger dollar removes FX tailwind and reinforces the short thesis) and **breaker = usd_weak_+1sd**
(a weaker dollar restores tailwind and is the scenario `docs/pitch-forecasts/questions/risk-dollar-weakens/`
scores as pushing the stock against the short). 3Q26 is ~71–78% printed as of the FX data date, so its
point is nearly identical across scenarios; only the unprinted tail of 3Q26 and all of 4Q26–2Q27 move.

### 2a. Revenue-FX contribution (pp of y/y revenue growth), adopted spec = Φ kernel (0, ⅔, ⅓) × 0.851

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 2.89 | 0.33 | 3.49 | pp | fx_lag_v2, FX through 2026-09-04 |
| base | 4Q26 | 0.98 | 0.31 | 2.16 | pp | fx_lag_v2, FX through 2026-09-04 |
| base | 1Q27 | 0.93 | 0.22 | 1.21 | pp | fx_lag_v2, FX through 2026-09-04 |
| base | 2Q27 | 0.62 | 0.17 | 0.95 | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 3Q26 | 2.89 | −0.20 | 3.04 | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 4Q26 | 0.52 | −1.54 | 0.46 | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 1Q27 | −1.01 | −2.68 | −0.82 | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 2Q27 | −1.92 | −3.16 | −1.16 | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 3Q26 | 2.89 | 0.75 | 4.00 | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 4Q26 | 1.45 | 0.74 | 4.78 | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 1Q27 | 2.88 | 1.50 | 4.68 | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 2Q27 | 3.16 | 1.50 | 4.73 | pp | fx_lag_v2, FX through 2026-09-04 |

Low/high = the Object-A 95% confidence-set weight vectors pushed through the same baskets
(`cs_interval_lo_pp` / `cs_interval_hi_pp`), i.e. parameter uncertainty around the adopted point, not
a predictive band. The package also carries an 80% predictive band (σ = 1.03pp) not reproduced here for
space; see `23_forecast_4q26_v2.csv` columns `band80_lo_pp`/`band80_hi_pp`.

### 2b. `point_phi_adrfx_pp` — NOT ADR FX (relabelled `revenue_fx_phi_lagged_pp` per DEC-0027/X1; see correction in §7)

Same Φ construction applied to the disclosed-ADR-FX-on-basket fit (slope 0.872, intercept −0.076, r
0.962, n=14) — despite its column name in the code, X1 found this scores as a **revenue-FX**
construction (it equals `revenue_fx_pp` to two decimals at 3Q26, and RMSE 2.2pp against Airbnb's
disclosed ADR-FX series vs 0.42pp for the ADR card's contemporaneous term). **The model's ADR-FX
input is D4's N midpoint (−0.43pp 3Q26, +0.15pp 4Q26), not this table.**

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 2.89 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| base | 4Q26 | 0.93 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| base | 1Q27 | 0.88 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| base | 2Q27 | 0.56 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 3Q26 | 2.89 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 4Q26 | 0.45 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 1Q27 | −1.11 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| short (usd_strong_-1sd) | 2Q27 | −2.05 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 3Q26 | 2.89 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 4Q26 | 1.40 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 1Q27 | 2.87 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |
| breaker (usd_weak_+1sd) | 2Q27 | 3.16 | n/a | n/a | pp | fx_lag_v2, FX through 2026-09-04 |

The package does not publish a separate confidence set for this construction: `23_forecast_4q26_v2.csv`'s
`cs_interval_*` columns are the revenue-FX Object-A confidence set, shared with `revenue_fx_pp` above,
not an ADR-FX-specific one. "n/a" is therefore honest, not a placeholder for a number I didn't look for.

### 2a. Model inputs (machine-readable)

Per DEC-0010: this mapping (base = spot held, short = USD one sigma stronger, breaker = USD one sigma
weaker) is adopted. Per DEC-0027 (X1 reconciliation): the item below is `revenue_fx_phi_lagged_pp`, not
`adr_fx_pp` — see the correction at the top of §7.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| revenue_fx_pp | base | 3Q26 | 2.89 | pp | Φ(0,2/3,1/3)×0.851 kernel on basket, spot held from 2026-09-04 |
| revenue_fx_pp | base | 4Q26 | 0.98 | pp | same, spot held |
| revenue_fx_pp | base | 1Q27 | 0.93 | pp | same, spot held |
| revenue_fx_pp | base | 2Q27 | 0.62 | pp | same, spot held |
| revenue_fx_pp | short | 3Q26 | 2.89 | pp | same, usd_strong_-1sd (-5% parallel shift) |
| revenue_fx_pp | short | 4Q26 | 0.52 | pp | same, usd_strong_-1sd |
| revenue_fx_pp | short | 1Q27 | -1.01 | pp | same, usd_strong_-1sd |
| revenue_fx_pp | short | 2Q27 | -1.92 | pp | same, usd_strong_-1sd |
| revenue_fx_pp | breaker | 3Q26 | 2.89 | pp | same, usd_weak_+1sd (+5% parallel shift) |
| revenue_fx_pp | breaker | 4Q26 | 1.45 | pp | same, usd_weak_+1sd |
| revenue_fx_pp | breaker | 1Q27 | 2.88 | pp | same, usd_weak_+1sd |
| revenue_fx_pp | breaker | 2Q27 | 3.16 | pp | same, usd_weak_+1sd |
| revenue_fx_phi_lagged_pp | base | 3Q26 | 2.89 | pp | relabelled per DEC-0027/X1 (was `adr_fx_pp`): Φ on ADR-FX-on-basket fit — a revenue-FX construction, not ADR FX (RMSE 2.2pp vs disclosed ADR FX; equals revenue_fx_pp to 2dp at 3Q26); spot held |
| revenue_fx_phi_lagged_pp | base | 4Q26 | 0.93 | pp | same, spot held |
| revenue_fx_phi_lagged_pp | base | 1Q27 | 0.88 | pp | same, spot held |
| revenue_fx_phi_lagged_pp | base | 2Q27 | 0.56 | pp | same, spot held |
| revenue_fx_phi_lagged_pp | short | 3Q26 | 2.89 | pp | same, usd_strong_-1sd |
| revenue_fx_phi_lagged_pp | short | 4Q26 | 0.45 | pp | same, usd_strong_-1sd |
| revenue_fx_phi_lagged_pp | short | 1Q27 | -1.11 | pp | same, usd_strong_-1sd |
| revenue_fx_phi_lagged_pp | short | 2Q27 | -2.05 | pp | same, usd_strong_-1sd |
| revenue_fx_phi_lagged_pp | breaker | 3Q26 | 2.89 | pp | same, usd_weak_+1sd |
| revenue_fx_phi_lagged_pp | breaker | 4Q26 | 1.40 | pp | same, usd_weak_+1sd |
| revenue_fx_phi_lagged_pp | breaker | 1Q27 | 2.87 | pp | same, usd_weak_+1sd |
| revenue_fx_phi_lagged_pp | breaker | 2Q27 | 3.16 | pp | same, usd_weak_+1sd |
| revenue_fx_pp_low | base | 3Q26 | 0.33 | pp | Object-A 95% confidence-set low, base scenario |
| revenue_fx_pp_low | base | 4Q26 | 0.31 | pp | Object-A 95% confidence-set low, base scenario |
| revenue_fx_pp_low | base | 1Q27 | 0.22 | pp | Object-A 95% confidence-set low, base scenario |
| revenue_fx_pp_low | base | 2Q27 | 0.17 | pp | Object-A 95% confidence-set low, base scenario |
| revenue_fx_pp_high | base | 3Q26 | 3.49 | pp | Object-A 95% confidence-set high, base scenario |
| revenue_fx_pp_high | base | 4Q26 | 2.16 | pp | Object-A 95% confidence-set high, base scenario |
| revenue_fx_pp_high | base | 1Q27 | 1.21 | pp | Object-A 95% confidence-set high, base scenario |
| revenue_fx_pp_high | base | 2Q27 | 0.95 | pp | Object-A 95% confidence-set high, base scenario |

**Management's own reference point (not this package's output):** the 6 Aug 2026 letter guided 3Q26
revenue FX at "approximately three percentage points... after factoring in our hedging program" (stated,
after-hedge). The adopted Φ×0.851 construction gives +2.89pp for the same quarter — within 0.11pp.

## 3. Derivation chain
1. FRED daily bilateral FX + DTWEXBGS broad-USD index, cached `fx_daily_2026-09-11.csv` (through 2026-09-04; `fetch_fx_v2.py` NOT re-run per the brief) →
2. `baskets.py` builds regional/global revenue-weighted FX baskets → `data/processed/forecast_methods/fx_lag_v2/02_basket_quarterly.csv` (global y/y: 1Q26 +5.67%, 2Q26 +2.27%, 3Q26 QTD/spot-held +0.60%)
3. `fits.py::object_a` fits a joint interval-likelihood lag regression of the **stated** (after-hedge) revenue-FX series on lag-0/1/2 of the basket, n=14 (1Q23–2Q26), giving weights a=(0.447, 0.364, 0.030), total scale 0.841, effective lag 0.50q, and its 95% confidence set → `06_object_a_summary.csv`
4. `exhibit.py::forecast_4q26` applies the architect's Φ kernel shape (0, ⅔, ⅓) at the free fit's own total scale (0.851 — RED_TEAM-validated, a construction, not itself a fitted number) to the basket lagged 1/2 quarters, for three scenario paths (spot held / ±5% parallel USD shift) and six forward quarters → `23_forecast_4q26_v2.csv` columns `point_phi_basket_scale_0.851_pp` (revenue FX) and `point_phi_adrfx_pp` (same Φ shape/scale applied to the ADR-FX-on-basket contemporaneous fit)
5. The same Object-A 95% confidence set (every candidate weight vector), pushed through the identical baskets → `cs_interval_lo_pp`/`cs_interval_hi_pp` in the same file
6. `registry_out.py` emits the LIVE 4Q26 base-case point (+0.98pp) and its predictive quantile ladder → `data/processed/forecast_methods/registry/fx-lag-v2__fx_pts_revenue_2026q4_v2.csv`

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| pre-2026-09-11 (FX through 2026-08-28) | `fx-lag.md` (`analysis/src/forecast_methods/fx_lag/`) | 4Q26 revenue FX +0.7 to +1.2pp depending on reading; FX-determined share 0.65 central at 5 Nov guide; eff. lag 0.50q | **superseded** by `B4_FX_EXHIBIT.md`/`fx_lag_v2` — refreshed FX to 2026-09-04, and a holiday-fill bug in `pit_fx._q_avg_spot_held` is fixed (moves basket-driven specs 0.1–0.3pp of RMSE; H2, the adopted spec, is unchanged because its driver is the disclosed ADR-FX point, not the basket) |
| 2026-09-11 | `VERIFY_fx-lag_r1.md` | round-1 verify of `fx_lag` (not v2): PARTIAL — found a full-sample-prior replay bug | **superseded** by r2 (bug confirmed fixed); governs the pre-refresh package's correctness, not v2's new exhibit module |
| 2026-09-11 | `VERIFY_fx-lag_r2.md` | round-2 verify of `fx_lag` (not v2): **PASS**, 8 numbers independently re-derived byte-for-byte, no leakage | governs the base package `fx_lag`; **`fx_lag_v2` itself has no independent third-party verify note** — my own reproduction (§5, byte-identical, exit 0) is the only check on the v2 refresh and the new `exhibit.py` module found in this repo |
| 2026-09-11 | `B4_FX_EXHIBIT.md` (`fx_lag_v2`, **this package**) | GOVERNS: 4Q26 revenue FX +1.0pp (CS +0.3 to +2.2); 3Q26 two live numbers +1.3 (free fit, PIT-clean, registered) / +2.9 (Φ×0.851, adopted for forecasting a guide); eff. lag 0.43–0.50q; H2 wins the PIT horse race (RMSE 0.99pp) on both windows but covers only 10/14 W1 quarters and is explicitly "not quotable as a W1 winner" | **GOVERNS** |
| 2026-09-12 | `FXSWAP_h2_bridge_kernel_fx.md` | swaps the H1→H2 bridge's 4Q26 revenue-FX assumption for this package's +0.98pp; flags an internal 0.15–1.0pp inconsistency between the bridge's "pattern route" (basket-Φ, this package) and its "dollar route" (ADR-FX-Φ pushed through the GBV lag, using the ADR v3 midpoint's 3Q26 point of −0.43 instead of this package's contemporaneous-basket fit of +0.4) | consistent with / downstream of B4; not itself an independent FX estimate, and names an unresolved 0.8pp disagreement this dossier does not resolve |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` §5 | "revenue FX is 84% observed for 4Q26" | **UNRECONCILED, likely mislabeled** — see §7 |
| 2026-09-17 | `docs/pitch-forecasts/questions/q3-revenue-fx-integer/` (C08) | anchors on "the programme's registered fx-lag-v2 H2 point, +1.85" for 3Q26 | not a conflict — `c08_spec_points.csv` shows +1.85 is the **PIT** coefficient (0.7313) fitted at the 2026-08-06 guide date applied to disclosed ADR-FX, a different vintage from this dossier's **live** (2026-09-11, data through 09-04) Φ×0.851 point of +2.89; both are legitimate, dated constructions of the same spec family |

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/D5/receipt.json`
- Command: `python3 analysis/src/forecast_methods/fx_lag_v2/run.py` (run via `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id D5 --watch analysis/src/forecast_methods/fx_lag_v2 --watch data/processed/forecast_methods/fx_lag_v2 --cmd "python3 analysis/src/forecast_methods/fx_lag_v2/run.py" --timeout 300`) · Exit: 0 · Wall: 7.7s · Interpreter: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` (plain `python3`; no pandas-3 API failure hit, `.venv-pd2` not needed) · `fetch_fx_v2.py` was NOT run, per the brief; the cached `fx_daily_2026-09-11.csv` was used as-is (asserted present by `run.py`)
- Output: `data/processed/forecast_methods/fx_lag_v2/23_forecast_4q26_v2.csv`, `path=spot_held, quarter=4Q26`, column `point_phi_basket_scale_0.851_pp` = 0.98 · Committed value: 0.98 · Tolerance: exact match required · **Match: yes**
- Receipt shows `"changed": []`, `"new_files": []` (after `.pyc` cache files were ignored/cleaned up by the wrapper's untracked-file handling — see receipt), `"restored": true`: the fresh run reproduced the entire watched tree, including every numbered CSV and both registry files, **byte-identical** to what is already committed. Console output (`stdout.txt`) independently confirms the live 4Q26 point (+0.98pp, CS +0.31 to +2.16pp) and the W1 coverage warning ("fx_rev_next_q_h2_v2 ... W1 PIT covers 10 quarters, expected 14") printed live during the run, not just asserted in the note.

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 PIT | 10 (of the pre-registered 14; H2's ADR-FX driver starts 2Q22) | RMSE (pp, letter-interval scored), H2 spec | 0.9936 | not available — no naive baseline registered for `fx_pts_revenue` in the harness | n/a (not a revenue object) | n/a (no FX consensus consumed) | best PIT forecaster among the FX-lag specs on both windows | **pass** (best_in_window = True) but **partial coverage** — 10/14, not the full W1 |
| W2 PIT | 10 | RMSE (pp), H2 spec | 0.9936 | not available | n/a | n/a | best PIT forecaster among the FX-lag specs on both windows | **pass** (best_in_window = True), full W2 coverage |
| full sample (n=14) | 14 | LR test, Φ-shape restriction (H0) vs free fit, stated series | LR 10.214, p 0.0168 | — | — | — | Φ restriction should NOT be rejected if it is to justify the adopted shape | **Φ is rejected** (p<0.05); the adopted 0.851 scale is a construction validated only on 3 live quarters (n=3), not a fitted, in-sample-surviving object |

Strongest known failure: **H2 wins the point-in-time horse race against every other FX-lag spec on
both W1 and W2 (RMSE 0.99pp, identical on both because its 10-quarter sample sits inside both windows),
but that sample is only 10 of the pre-registered 14 W1 quarters and no naive baseline exists for
`fx_pts_revenue` in the harness — so under the programme's own survives-both-windows convention this is
a best-in-class, partial-coverage result, not a scored, baseline-beating pass, and the governing note
itself states H2 is "not quotable as a W1 winner."**

## 7. Kill list and consistency

**Correction (2026-09-18, DEC-0027, citing `docs/pitch-model-v2/dossiers/X1_x1_adr_fx_reconciliation.md`):**
the quantity §2's machine-readable block originally called `adr_fx_pp` is fx_lag_v2's
`point_phi_adrfx_pp`, the Φ(0, ⅔, ⅓) kernel applied to the ADR-FX-on-basket fit at lags 1 and 2 — a
**revenue-FX construction**, not ADR FX: it equals this dossier's own `revenue_fx_pp` to two decimals
at 3Q26 and scores RMSE 2.2pp against Airbnb's disclosed ADR-FX series, versus 0.42pp for the ADR
card's contemporaneous term (X1). It has been renamed `revenue_fx_phi_lagged_pp` throughout §2. **The
ADR-FX object for the model is D4's N midpoint: −0.43pp (3Q26), +0.15pp (4Q26).**

- Kill-list check: **the −3.4pp Q4 FX step and "82% of Q4 FX already determined" are both on the kill
  list and neither is used or quoted as ours anywhere in this dossier.** The −3.4pp step is reproduced
  only inside `24_four_way_4q26.csv` as a labelled, REJECTED comparison row, with the double-subtraction
  named explicitly: the −3.4pp is the `05_fx_schedule` level (−0.4pp) subtracted from a guide-anchored
  walk whose 3Q26 start already contains management's +3.0pp, and from a lagged-GBV base that already
  carries booking-date FX. "82% already determined" appears nowhere in `fx_lag_v2`'s outputs; the
  package instead always reports the observed-share **triple** (free fit / Φ kernel / contemporaneous)
  together with two readings of "elapsed" (calendar vs FRED business days actually printed).
- Conflict, reconciled as far as the evidence allows: **memo v3 §5 states "revenue FX is 84% observed
  for 4Q26," which does not reproduce as a 4Q26 number anywhere in the governing package.** At the 5 Nov
  4Q26 guide date, `20_observed_share_triple.csv` gives the free-fit share at **0.67** (CS band 0.38 to
  1.00), the Φ kernel at **1.00**, and the contemporaneous reading at **0.38** — none is 0.84. The
  closest match in the whole file is row `as_of=2026-09-11, target_quarter=3Q26,
  spec=a_free_fit_gross`, `fx_determined_share_fred_observed = 0.8372` (≈84%) — i.e. **today's 3Q26
  share, on the gross-weight free fit, read off actual FRED prints**, not a 4Q26 figure at all. My
  reading is that memo v3's "84% observed for 4Q26" is a mislabelled carry-over of the 3Q26 "as of
  today" number, not a new, independently computed 4Q26 claim; it should not be quoted for 4Q26 without
  correction, and doing so would land uncomfortably close to the kill-listed "82%" framing this package
  was built to replace with the triple.

## 8. Open choices
1. **Whether "base / short / breaker" is the right scenario framing for this line, and whether my
   mapping is the intended one.** The package's native scenarios are `spot_held`, `usd_strong_-1sd`,
   `usd_weak_+1sd` (a symmetric ±5% parallel dollar shift, no forward curve is derivable from FRED).
   Options: (a) my mapping — base=spot_held, short=usd_strong (reinforces the bear thesis by removing
   FX tailwind), breaker=usd_weak (the scenario `risk-dollar-weakens` scores as pushing the stock against
   the short); (b) treat all three as a symmetric sensitivity band with no thesis-linked labels, since the
   package itself never names a "short" or "breaker" case; (c) replace the ±5% shift with the actual
   probability-weighted dollar path from `risk-dollar-weakens` (P=0.09 of a ≥4% decline by 11 Feb 2027).
   **Recommendation: (a)** for the memo's readability, but state the mapping explicitly every time, since
   it is my label, not the programme's.
2. **Which 4Q26 revenue-FX point to carry into the model: the adopted Φ×0.851 (+0.98pp) or the
   shape-only-fitted Φ×0.653 (+0.75pp).** Both are computed in the same file; 0.851 is a construction
   (the free fit's total scale re-assigned onto the Φ shape) validated only on 3 live quarters, while
   0.653 is what the Φ *shape* fits to when its own scale is estimated (and is still rejected in-sample,
   p=0.0072). **Recommendation: keep 0.851** for consistency with what `FXSWAP` and the bridge already
   adopted, but disclose the 0.23pp gap every time the number is quoted.
3. **Whether to reconcile D5's ADR-FX line with the ADR v3 (D4) line before the memo is finalised.**
   `FXSWAP_h2_bridge_kernel_fx.md` §4 shows an unresolved 0.8pp gap on the 3Q26 ADR-FX point between this
   package's contemporaneous-basket fit (+0.4) and the ADR v3 midpoint (−0.43), which propagates to a
   +0.15 to +0.98pp range on 4Q26 revenue FX depending on which route is used. Options: (a) carry this
   package's basket-Φ number as the headline (what this dossier does) and cite D4 only as a bracket;
   (b) let D4's digger own the reconciliation since it is their input that disagrees. **Recommendation:
   (b)** — D5 should not silently pick a winner between two packages it does not own.
4. **What to do about memo v3's "84% observed for 4Q26."** Options: (a) correct it to attach to 3Q26 and
   restate it as one of the triple's three numbers, with its specification and date; (b) drop the figure
   entirely and use the governing 5-Nov-4Q26 triple (67% / 100% / 38%) instead. **Recommendation: (b)** —
   a single re-attached number would still invite the same "which specification?" question the triple
   exists to answer.

## 9. Judge Q&A
1. Q: How much of 4Q26 revenue growth is FX, and is it already known? A: Under the base (spot-held)
   scenario, +0.98pp (confidence-set interval +0.31 to +2.16pp), from the lag-loaded Φ kernel — the
   right spec for forecasting what management will *say* at a guide date, because at that date only
   32–38% of the guided quarter's own FX has printed. Whether it is "already known" depends entirely on
   which of three specifications you trust: 67% (free fit), 100% (Φ kernel) or 38% (contemporaneous) at
   the 5 Nov guide date — this package always reports the triple, never a single number, because picking
   one silently is exactly how the kill-listed "82%" and memo v3's unreconciled "84%" got made.
2. Q: Why doesn't the model use the −3.4pp Q4 FX step, or say "82% already determined"? A: Both are on
   the kill list. The −3.4pp step double-subtracts a level (−0.4pp) that is already embedded twice — once
   in a guide-anchored walk that starts from management's own +3.0pp, and once in a lagged-GBV base that
   already carries booking-date FX. "82%" (and memo v3's unreconciled "84%") collapse three
   specifications and two readings of "elapsed" into one number; this package reports the observed-share
   triple instead, at every decision date, together.
3. Q: How much of the 4Q26–2Q27 FX outlook is model choice versus the dollar itself? A: The dollar
   dominates. The ±5% parallel-shift scenarios move 4Q26 revenue FX from +0.52pp (dollar strengthens) to
   +1.45pp (dollar weakens) against a +0.98pp base, and by 1Q27–2Q27 the spread widens to roughly −2pp to
   +3pp — wider than the 3.0pp spread among all four *rejected* 4Q26 constructions (the repo bridge, the
   repo schedule, the M6 reconstruction, and holding the guide flat) combined. The method argument is
   smaller than the currency-risk argument, and the memo should say so.

## 10. Grade
Grade: B — the receipt shows exit 0 and a byte-identical (better than within-tolerance) match against
the tracked outputs, so reproduction is not in question. It is not an A because the adopted spec (H2,
Φ kernel) does not survive the full pre-registered W1: it covers only 10 of 14 quarters (its ADR-FX
driver starts 2Q22), the governing note itself says it is "not quotable as a W1 winner," and no naive
baseline exists in the harness for `fx_pts_revenue` at all, so there is no baseline-beating ratio to
score on either window — it wins a same-family horse race, not the programme's own both-windows test.
