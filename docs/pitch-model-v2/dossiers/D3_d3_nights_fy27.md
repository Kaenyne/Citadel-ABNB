# D3 — FY27 nights path

## 1. Header
- Line: D3 · Judge's question: "What does FY27 nights growth have to be for your revenue, and what is it made of?"
- Digger: sonnet · Date: 2026-09-18 · Commit: e6d9832 (branch `theo/pitch-model-v2`; the brief names b098ac2, which this branch has since moved past — the repo advanced under a parallel digger while this dossier was in progress; nothing under §D3's watched paths changed)

**One-sentence answer to the judge.** FY27 nights growth has to be **+6.6% (base, 621.8m)**, built quarter by quarter as NA nights (~29% of the prior-year mix) at +2.3% plus ex-NA nights decelerating from a ~10.8% pre-lap run rate to ~9.8% by 4Q27, less a −0.74pt ex-NA fee/cancellation lap (already inside the adopted 4Q26 exit) and a −0.36 to −0.91pt ex-NA RNPL lap phased in from 1Q27; it is **not** an independent forecast — it is what the H2-bridge-v3 exit plus the WS10 regional path plus the RNPL lap schedule arithmetically produce, and it sits exactly between the two numbers a predecessor script (PR #32) never chose between: +6.4% (global lap, every ex-NA region) and +8.2% (NA-only lap).

## 2. The number

Scenario labels are mine (base/short/breaker), mapped onto the package's own native scenario names (base/bear/bull) as: **base = bridge v3 base**, **short = bridge v3 bear** (a weaker print reinforces the short thesis), **breaker = bridge v3 bull** (an upside print breaks it) — see §8 choice 1. The package's bear/bull are **stacked envelopes** (2H26 band lows/highs on nights and ex-FX ADR taken jointly, plus PR #32's levers, plus ±1σ FX), not a statistical interval; the note that built them says so explicitly. Low/high columns below are therefore the bear/bull scenario values themselves, not a confidence band around base.

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | FY27 | 6.64 | 3.64 | 9.18 | pct y/y | `06_fy27_path_v2` v2, built 13–14 Sep 2026, WS06v-audited 14 Sep |
| base | FY27 | 621.84 | 602.26 | 639.27 | m nights | same |

**Reproduced vs inherited, cell by cell.**
- **Reproduced (exit 0, this machine, this commit, byte-identical — see §5):** every cell in `06_nights_build.csv`, `06_revenue_path_wide.csv`, `06_annual_fy26_fy28.csv`/`_v2b.csv` and `06_pr32_rederivation.csv` quoted in this dossier, by re-running `h1_to_h2_bridge_v3.py` then `06_fy27_path_v2/run.py` through the wrapper.
- **Inherited (not reproduced here, out of my packages):** the WS10 regional-forecast rates that feed the NA/ex-NA split (`nights_baseline_reconciliation.csv`, `10_regional_forecast.csv`); the ADR v3 card and K-line (D4's package); the FX kernel (D5's package); the 3Q26 nights *level* itself, which comes from D1's line and is currently **stale in this build** (see §4, §7); the WS06v independent second build (`data/processed/margin_build/06v_fy27_path_check/`), read here but not in my touchable packages, so not re-run.

### 2a. Model inputs (machine-readable)

One item per row, same values as `06_annual_fy26_fy28_v2b.csv` (annual) and `06_revenue_path_wide.csv` (quarterly); `_v2b` did not change any nights cell (verified: `06_revenue_path_3q26_4q27.csv` and `_v2b.csv` are identical on every `nights_yoy_pct` row). Named paths: **base = bridge v3 base**, **short = bridge v3 bear**, **breaker = bridge v3 bull**, **alt_rnpl** = a fourth, non-bridge construction (see note on the last two rows).

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| nights_m | base | 1Q27 | 169.02 | m nights | bridge v3 base |
| nights_m | base | 2Q27 | 157.10 | m nights | bridge v3 base |
| nights_m | base | 3Q27 | 155.96 | m nights | bridge v3 base |
| nights_m | base | 4Q27 | 139.77 | m nights | bridge v3 base |
| nights_m | base | FY27 | 621.84 | m nights | sum of quarters |
| nights_yoy_pct | base | 1Q27 | 8.21 | pct | bridge v3 base |
| nights_yoy_pct | base | 2Q27 | 5.93 | pct | bridge v3 base |
| nights_yoy_pct | base | 3Q27 | 6.23 | pct | bridge v3 base |
| nights_yoy_pct | base | 4Q27 | 6.05 | pct | bridge v3 base |
| nights_yoy_pct | base | FY27 | 6.64 | pct | level sum vs FY26 level sum |
| nights_m | short | 1Q27 | 163.55 | m nights | bridge v3 bear |
| nights_m | short | 2Q27 | 152.79 | m nights | bridge v3 bear |
| nights_m | short | 3Q27 | 149.89 | m nights | bridge v3 bear |
| nights_m | short | 4Q27 | 136.03 | m nights | bridge v3 bear |
| nights_m | short | FY27 | 602.26 | m nights | sum of quarters |
| nights_yoy_pct | short | 1Q27 | 4.71 | pct | bridge v3 bear |
| nights_yoy_pct | short | 2Q27 | 3.03 | pct | bridge v3 bear |
| nights_yoy_pct | short | 3Q27 | 3.41 | pct | bridge v3 bear |
| nights_yoy_pct | short | 4Q27 | 3.33 | pct | bridge v3 bear |
| nights_yoy_pct | short | FY27 | 3.64 | pct | level sum vs FY26 level sum |
| nights_m | breaker | 1Q27 | 172.64 | m nights | bridge v3 bull |
| nights_m | breaker | 2Q27 | 161.38 | m nights | bridge v3 bull |
| nights_m | breaker | 3Q27 | 161.17 | m nights | bridge v3 bull |
| nights_m | breaker | 4Q27 | 144.07 | m nights | bridge v3 bull |
| nights_m | breaker | FY27 | 639.27 | m nights | sum of quarters |
| nights_yoy_pct | breaker | 1Q27 | 10.52 | pct | bridge v3 bull |
| nights_yoy_pct | breaker | 2Q27 | 8.82 | pct | bridge v3 bull |
| nights_yoy_pct | breaker | 3Q27 | 8.68 | pct | bridge v3 bull |
| nights_yoy_pct | breaker | 4Q27 | 8.57 | pct | bridge v3 bull |
| nights_yoy_pct | breaker | FY27 | 9.18 | pct | level sum vs FY26 level sum |
| fy27_nights_yoy_rnpl_pct | alt_rnpl | FY27 | 6.42 | pct | **on the record but mislabelled upstream** — see note below |

**Note on `fy27_nights_yoy_rnpl_pct`.** `docs/pitch-model-v2/LINES.md` attributes "FY27 nights +6.4%" to `05_backtests/ALPHA_F_RNPL.md`; that file does not contain an FY27 nights figure (it is a Q3/Q4-2026 excess-unpaid-share stress test, out of scope for a full year). The actual figure is PR #32's flat "global lap" rate, re-derived byte-for-byte inside my own reproduction at `06_pr32_rederivation.csv` row `PR32 total base FY27 nights level, exna_lap=True` = 621.6mm on PR #32's own 584.1mm FY26 base = **+6.42%** (rounds to +6.4%), and independently corroborated to 0.02pp by two unmerged, un-registered constructions in `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md`: PR #32's own global lap **+6.42%** and Jessie's plateau-plus-drag **+6.52%**. It is real and reproducible, just wrongly sourced in `LINES.md`; the dossier states the correction rather than silently fixing the pointer.

## 3. Derivation chain
1. WS10 regional nights forecast (NA / ex-NA rates, prior-year NA share) → `data/processed/nights_baseline_reconciliation.csv`, `10_regional_forecast.csv` (D2's / Krish's package, read-only here) →
2. ADR v3 card terms and K-line (D4's package) + the FX kernel (D5's package) feed the 2H26 exit only, not nights directly →
3. `analysis/src/h1_to_h2_bridge_v3.py` → `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`: 3Q26 nights **+9.89% (146.81mm)**, 4Q26 **+8.12% (131.80mm)** — the team baseline, replacing v1/v2's unfitted RNPL/World-Cup overlays →
4. `analysis/src/margin_build/06_fy27_path_v2/run.py` reads that exit plus WS10's FY27 regional rates, the NA prior-year share (`na_share_prior_year`, 0.291→0.282 across quarters), the ex-NA fee/cancellation lap (−0.742pt, already embedded from 4Q26), the ex-NA RNPL lap (−0.363pt in 1Q27 at 40% phase-in, −0.907pt from 2Q27 at full), and two dated events (Middle East base +1.0 in 1Q27, World Cup lap −0.5/−0.75/0 in 2Q27 by scenario) → `data/processed/margin_build/06_fy27_path_v2/06_nights_build.csv` (growth-space decomposition, per quarter, per scenario) →
5. Same script compounds `nights_yoy_pct` onto the printed prior-year (2026) nights level → `06_revenue_path_wide.csv` (`nights_mm` column) and sums to `06_annual_fy26_fy28.csv` / `_v2b.csv` (FY27 base **621.8414mm, +6.642%**; bear 602.2637mm, +3.6406%; bull 639.2667mm, +9.1837%) →
6. `analysis/src/margin_build/06v_fy27_path_check/run.py` (14 Sep, **not** in my touchable packages, read-only) independently rebuilds the same nights logic from the same named inputs before reading WS06's script or note and gets FY27 base **+6.56% (621.4mm)** — 0.08pp / 0.4mm from WS06's own number, both traced to two named, disclosed judgement calls (1Q27 RNPL phase fraction 0.40 vs 0.423; the ex-NA phasing shape) →
7. `06_v2b_changes.csv` (WS06v's correction, copied into this folder) fixes only the 3Q26/FY26 **revenue** bear/bull lines (which had been scenario-invariant because the kernel reads only printed GBV); it changes **no nights cell** (verified in this reproduction: `06_revenue_path_3q26_4q27.csv` and `_v2b.csv` are identical on every `nights_yoy_pct`/`nights_mm` row) →
8. committed line: **FY27 nights +6.64% base / +3.64% short (bear) / +9.18% breaker (bull)**, feeding FY27 revenue +10.94% / +5.53% / +15.14% (`06_annual_fy26_fy28_v2b.csv`).

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` (Opus) | B3's FY27 driver base has **no lap schedule at all**; "RNPL evidence supports FY27 nights +6.4% (global lap, PR #32) to +8.2% (NA-only lap, PR #32)"; B3's own +9.46% sits above the top of that range | Identifies the gap. **Superseded, for the FY27 nights object itself**, by WS06 (below), which builds a laps-included path between the two PR #32 cases |
| 2026-09-12 | `REBASE_h2_bridge_v3_nights_adr.md` (Krish) | 3Q26 nights team baseline **+9.89% (146.8mm)**, 4Q26 **+8.12% (131.8mm)**, replacing v1/v2's unfitted overlays | **Governs** the 2H26 exit this line's FY27 path is anchored to |
| 2026-09-13/14 | `docs/margin-build/notes/06_fy27_path_v2.md` (WS06) | FY27 nights **+6.64% base** (between PR #32's +6.4%/+8.2%), audits PR #32 finding "no FY27 object existed" (levels never summed, 3Q27/4Q27 blank) and "lap placement inconsistent with the adopted exit" (double-count risk in PR #32's "everywhere from 1Q27" case) | **Governs** the committed FY27 nights number and its construction |
| 2026-09-14 | `docs/margin-build/notes/06v_fy27_path_check.md` (independent audit, out of my packages) | "PASS WITH CORRECTIONS": independent rebuild FY27 nights **+6.56%** (0.08pp from WS06); explicitly finds WS10 does **not** already embed the RNPL lap, so no double count; flags the ex-NA phasing as "the single largest judgement in the path" (a sensitivity without the 2027 ex-NA lap gives **+8.17%**, "just outside the B3 band") | **Governs** as the second, independent construction that corroborates WS06 within 0.08pp; its one correction (3Q26/FY26 **revenue** bear/bull, not nights) is in the adopted `_v2b` files |
| 2026-09-18 (today) | `docs/pitch-model-v2/DECISIONS.md` DEC-0004 (D1) | 3Q26 nights base **146.3m / +9.5%** (bias-corrected reviews-index read), superseding the team-baseline 146.8mm/+9.89% this whole FY27 path is still anchored to | **Governs** the 3Q26 level generally, but is **not yet threaded through** `h1_to_h2_bridge_v3.py` or `06_fy27_path_v2` — flagged, not fixed, since those packages are outside D1's lane and I may only reproduce, not edit them (see §7) |

**Web fetches: zero.** Everything above is in the repository.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/D3/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id D3 --watch data/processed/h2_bridge_v3 --watch data/processed/margin_build/06_fy27_path_v2 --cmd "python3 analysis/src/h1_to_h2_bridge_v3.py && python3 analysis/src/margin_build/06_fy27_path_v2/run.py"` · Exit: 0 · Wall: 0.7s · Interpreter: python3 (3.13, pandas 3.0.0 — no pandas-3 API failure, `.venv-pd2` not needed)
- Output: `data/processed/margin_build/06_fy27_path_v2/06_annual_fy26_fy28_v2b.csv` cell `nights_mm_yoy_pct, row (FY27, base)` = 6.642 · Committed value: 6.642 · Tolerance: ±0.001pp (byte-identical) · **Match: yes**. Also byte-identical on this run: every cell of `06_nights_build.csv`, `06_revenue_path_wide.csv`, `06_annual_fy26_fy28.csv`, `06_pr32_rederivation.csv` (none appear in the receipt's `changed` list at all, i.e. zero diff, not merely within tolerance).
- Restored: true. Two files showed floating-point noise only, both in `data/processed/h2_bridge_v3/`: `h2_bridge_v3_vs_v1_delta.csv` and `h2_bridge_v3_vs_v2_delta.csv`, max abs diff 4.5e-13 (neither carries a value quoted in this dossier's §2/§2a). No new files; tree returned to HEAD.
- If no: n/a — match is exact.

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| n/a — forward object, no historical window exists | — | — | FY27 nights +6.64% (base) | n/a | n/a | reverse-DCF market/Street path 8–9% (comparison column only, `06_comparison_annual.csv`) | — | **not applicable**: this is a forward FY27 build, not a scored backtest; W1/W2 do not exist for a period that has not printed |
| internal pass-line (`06_pass_line.csv`) | 7 | assorted arithmetic/consistency checks (quarterly sums = annuals; 1Q27 within 2pt of 4Q26 exit; FY27 base inside B3's ±9.18–11.52% revenue band; seasonal shares within 1pt of 2023–25 mean) | 7/7 pass | — | — | — | all 7 must pass | **pass** |
| independent second build (`06v_fy27_path_check`, WS06v, 14 Sep) | 1 (single independent re-derivation, not a time-series window) | \|Δ pp\| on FY27 nights / revenue growth, this build vs WS06 | 6.64% / 10.94% | — | — | 6.56% / 10.71% (independent build) | WS06v's own >0.3pp / >$15M threshold flags a finding | **pass** (0.08pp / 0.23pp gap, both traced to two named, disclosed judgement calls — not an error) |

Strongest known failure: **the FY27 nights number cannot be backtested (it is a forward build on judgement, not a fitted or historically-scored object, so it fails the "survives both W1 and W2" bar by construction) — and the single largest judgement inside it, the ex-NA RNPL lap phasing, is a coin-flip on one unresolved question ("does WS10's own FY27 regional rate already contain a product-bundle deceleration, or is the lap additive on top of it?"); WS06v's own sensitivity answers "additive, no double count" and gets +6.64%, but flipping that one judgement — not a data revision, a reading of a qualitative rationale string — moves FY27 nights to +8.17%, which is closer to PR #32's un-adopted NA-only case and just outside the pre-registered B3 revenue band that today's number sits comfortably inside.**

## 7. Kill list and consistency
- Kill-list check: none of AGENT_BRIEF.md §6's items are quoted as ours in this line. Specifically checked and clear: no −3.4pp Q4 FX step (this line's 4Q26 revenue FX is +0.98pp); no "+4.05% fee uplift" as measured; no restated-unearned-fees circularity; no 120-market panel used as a nights measurement (this line's nights source is WS10's regional forecast, not the reviews index); "any FY27 level edge without the +9.2–11.5% band" is respected — the base case (+10.94% revenue) is checked against and sits inside B3's +9.18–11.52% band as a pre-registered pass-line test (§6).
- Conflicts:
  1. **With D1 / DEC-0004 (this branch, today).** D1's governing 3Q26 nights level is now 146.3m/+9.5% (bias-corrected reviews-index read). This entire FY27 path is still anchored to the pre-DEC-0004 team baseline 146.8mm/+9.89% (`h1_to_h2_bridge_v3.py`, 12 Sep). The FY27 quarterly build itself (§3 step 4) does not chain arithmetically off the literal 3Q26 level — it is built from WS10's regional y/y rates and prior-year NA shares — so the 0.5mm/0.39pp gap does not mechanically propagate into the +6.64% FY27 figure, but the *narrative* continuity ("the path starts here") and the 4Q26-exit consistency checks in `06_pass_line.csv` are computed against the stale 146.8mm base. Not fixed here: `h1_to_h2_bridge_v3.py` and `06_fy27_path_v2` are outside D1's lane and touching them beyond reproduction is against the brief's rules.
  2. **With memo v3 / LINES.md's stated conflict.** "Memo v3 gives FY27 nights +6.4% (global lap) to +8.2% (NA-only) against +8–9% in the price; bridge v3 base is +10.9% revenue." Resolved as follows: the two memo-v3 numbers are PR #32's two unmerged, un-summed, never-chosen-between cases (re-derived here in §2a/§3 to +6.42%/+8.17% on PR #32's own FY26 base); "+8–9% in the price" is the reverse-DCF market/Street nights path, a comparison column, not a forecast object; "bridge v3 base is +10.9% revenue" is this line's own FY27 revenue growth (10.94%, riding on **+6.64%** nights, not either PR #32 case) — the revenue number and the nights number in the price are therefore not the same nights path, which is exactly what the brief asked this dossier to state.
  3. **The `alt_rnpl` +6.4% figure is mislabelled in `LINES.md`** (attributed to `ALPHA_F_RNPL.md`, which does not contain it) — see the note under §2a. Stated as a correction, not silently fixed.

## 8. Open choices
1. **Whether "short"/"breaker" is the right label for the package's native "bear"/"bull".** Options: (a) keep my mapping (short = bear, breaker = bull, as used throughout this dossier); (b) treat bear/bull as pure sensitivity envelopes and not force them into the short/breaker frame at all, since the note that built them explicitly disclaims they are "a scenario envelope, not a predictive interval." Recommendation: (a) for consistency with the other dossiers' vocabulary, with the caveat in §2 carried forward into the deck. Why: the deck needs one consistent scenario name across lines; the disclaimer travels with the number either way.
2. **Whether to re-run the FY27 path on D1's new 3Q26 base (146.3m) before the memo locks.** Options: (a) leave `h1_to_h2_bridge_v3.py` / `06_fy27_path_v2` as is, since the FY27 build's own arithmetic doesn't chain off the literal 3Q26 level and the effect is disclosed as narrative-only (§7 conflict 1); (b) ask Krish's lane (owner of both packages) to re-run once DEC-0004 is final, so the pass-line checks (`06_pass_line.csv`'s 4Q26-exit tests) are computed against the governing number instead of the superseded one. Recommendation: (b), low cost (exit 0, 0.7s), but it is a cross-lane request, not something D3 can do inside its own packages.
3. **Which FY27 nights figure the memo should headline: +6.64% (base, this line) or the wider +6.4%–8.2% RNPL-support band (rnpl-short-audit).** Options: (a) quote the point +6.64% as the base case with bear +3.64%/bull +9.18% as the scenario envelope (this dossier's framing); (b) quote the +6.4–8.2% band directly, since it brackets both PR #32 readings and this line's own sensitivity (§6's "strongest failure" row) reaches +8.17% under one plausible re-reading of WS10. Recommendation: (b) for the judge Q&A, because it is honest about the single largest unresolved judgement call in the build; (a) for the model, because the margin build needs one number per scenario, not a scenario-free band. Why: DEC-0016 says scenarios are mechanical consequences of stated assumptions, not judgement calls we make to hit a target — the band communicates that the +6.64% choice is itself an assumption (the ex-NA lap is additive on WS10, not embedded in it), not a discovered fact.

## 9. Judge Q&A
1. Q: What does FY27 nights growth have to be for your revenue? A: **+6.64% in the base case (621.8m nights)**, ranging +3.64% (short/bear, 602.3m) to +9.18% (breaker/bull, 639.3m); it drives FY27 revenue of $15,829M / +10.94% off a base built from the 2H26 exit forward, not the other way around.
2. Q: What is it made of? A: NA nights (~29% weight) at +2.3%, plus ex-NA nights decelerating from a ~10.8% pre-lap run rate toward ~9.8% by 4Q27, less a −0.74pt ex-NA fee/cancellation lap already inside the 4Q26 exit and a −0.36 to −0.91pt ex-NA RNPL lap phased in 40% from 1Q27 and fully from 2Q27, plus two small dated events (Middle East base +1.0pt in 1Q27, World Cup lap −0.5 to −0.75pt in 2Q27). None of this is fitted; it is 55 named assumptions (10 judgement) applied in growth space.
3. Q: PR #32 gave two numbers, +6.4% and +8.2% — which is right, and why doesn't your line just pick one? A: Neither, on purpose — PR #32 never chose because it never summed either case to real quarterly levels or resolved a double-count risk in its "everywhere from 1Q27" case; this line rebuilds from named inputs and lands at **+6.64%**, between the two, independently corroborated within 0.08pp by a second, separately-built reproduction (WS06v) that also confirms no double count. The honest caveat is that one unresolved reading of WS10's own regional rationale — additive lap vs. already-embedded lap — swings this line's own number as high as +8.17%, which is why §8 keeps the wider band on the table for the judge conversation even though the model needs a single point.

## 10. Grade
Grade: B — the receipt shows exit 0 and a byte-identical match on every quoted cell (not merely within tolerance), and a second, independently-built reproduction of the same object lands within 0.08pp of it, so this is a reproduced, corroborated number; it is not an A because it is a forward FY27 build with no historical window to score it against (W1/W2 do not exist for an unprinted year), it is anchored to a 3Q26 base that a same-day decision (DEC-0004) has already superseded but that has not been re-run through this package, and its single largest judgement call (the ex-NA RNPL lap's additivity) is undecided evidence, not a fitted or measured parameter — a plausible re-reading of that one call moves the number 1.5pp.
