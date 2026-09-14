# RNPL short-thesis audit: synthesis of the four Opus passes

- **Date:** 2026-09-11 (evening). **Author:** Theo Machado, compiled with Claude Code, from four parallel Opus audit agents (notes 01–04 in this folder).
- **Question asked:** can Reserve Now, Pay Later carry a short thesis on ABNB, and how does the RNPL work plug into the FY27 decomposition the overnight forecast session rebuilt today (`docs/revenue-forecast-strategy/05_backtests/B3_FY27_DECOMPOSITION.md`)?
- **Nothing existing was modified** except three status blocks prepended to notes that carried a claim refuted here (`research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`, `01_*.md`, `02_*.md`). All files uncommitted.

## 1. Bottom line

1. **Verdict: RNPL is a supporting leg of a composition ("shape") thesis, not a standalone short and not a red herring** (note 03). It is the only dated, disclosed, mechanical reason 2026 growth does not repeat, and the only leg with a compounding term. It is too small to carry a short alone: the cancellation drag is −0.15 to −0.93 points of 3Q26 nights, and the anniversary is two to fifteen times the drag.
2. **It is a lap-and-pull-forward thesis, not a cancellation thesis** (note 01). Krish's cohort engine reproduces bit-for-bit; two of its three named assumptions are inert and only the unmeasured rebooking offset moves the answer (±0.2 to ±0.3). The divergence from the team baseline is in 4Q26 (1.3 points) and FY27 (1.8 points), not 3Q26. The pull-forward is absent from every team model and its biggest quarter is 1Q27 (−0.46 to −1.03). The US lap in 3Q26 is partial ("beginning of Q3"), worth +0.35 against the short.
3. **Unified module base case (note 01, `analysis/src/rnpl_short_audit/rnpl_nights_module.py`):**

| | team baseline | uplift lap | pull-forward | deferral | propensity | **y/y** | band | nights, mm |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| 3Q26 | 9.89 | +0.30 | −0.11 | −0.02 | −0.57 | **9.49** | 8.8 to 10.3 | 146.3 |
| 4Q26 | 8.90 | −0.59 | −0.16 | −0.10 | −0.45 | **7.61** | 6.6 to 8.4 | 131.2 |
| 1Q27 | 8.17 | −1.00 | −0.46 | −0.15 | −0.10 | **6.47** | | 166.3 |
| 2Q27 | 8.17 | −1.55 | −0.04 | −0.07 | −0.07 | **6.44** | | 157.9 |
| FY27 | | | | | | **6.41** | 5.6 to 6.9 | 619.3 |

   FY27 +6.41% converges on PR #32's global-lap +6.42% by a different route. Jessie's C(t) drag and Krish's tail are the same object; using both double counts.
4. **RNPL is nowhere in the rebuilt FY27 number** (note 02). B3's volume line is four flat regional rates (NA +6, EMEA +7, LatAm +16, APAC +15) applied to every 2027 quarter: no lap, no tail, no pull-forward. The memo has a product-bundle lap in the narrative and none in the arithmetic. The RNPL-supported FY27 nights range is +6.4% to +8.2%; B3 sits 1.3 points above the top.
5. **The kernel-weight band is a fitting artefact** (note 02, `data/processed/rnpl_short_audit/kappa_anatomy_and_lambda_refit.csv`). B3 quotes FY27 growth +9.18% to +11.52% across w = 0.33 to ⅔ (±1.12 turns) with λ fixed at ⅔. Re-fit λ at each w and the span is 0.042 points (0.02 turns); at fixed λ the w = 0.33 kernel misses printed 2Q26 by −11.4%, re-fit it reproduces it within 0.3%. `kernel-lambda` found the same at quarterly horizon ($6M on the 4Q26 print). With that counterweight gone, **the RNPL lap is −1.1 to −3.2 points of FY27 growth against the vendor-stamped Street, or −0.5 to −1.6 turns**, directional and dated. The honest competitor is the dollar: ±2.3 points of FY27 growth per one-sigma FX move.
6. **My balance-sheet note was partly wrong, and the correction strengthens the RNPL read** (note 04). The single-fee migration does not remove fees from unearned fees (FY2025 10-K Note 2 records host and guest fees in unearned fees; guest payments sit in funds payable net of fees). The 4Q25 divergence between the two lines is FX translation of non-USD funds payable. So unearned fees is the clean RNPL line, and solved on it alone the unpaid RNPL share of the backlog is 14–15% (book no longer-dated) to 22–23% (book 10% longer-dated): **17–28 million unpaid nights at 30 June**, consistent with the disclosed 20–21% flow share and with the module's ~21 million. Krish's 5 November unearned-fees row stands. Jessie's +4-point conversion break is not confounded.
7. **Trade (note 03):** short ABNB against QQQ into the **February shape** (1Q27 guide roughly +9.4 to +11.6% against a +17.9% comp; 2Q27 +10.7% against +16.5%), not into 5 November. The print trade's expected value is about +2.5% with a 7.5% standard deviation and a 26% chance of loss on an executable next-open entry; conditioning on the guide adds only 0.33 points over the base rate. Options are unidentified today. No pair works. Size 1 to 2% notional, underwritten to a +17% day.

## 2. What the "RNPL short-thesis model" is, if the team builds it

Not a new model. A module that feeds three existing exhibits:

| component | object | file | evidence status |
|---|---|---|---|
| Lap schedule | US RNPL 3Q26 partial; global fee and cancellation legs 4Q26; ex-NA RNPL 1Q27 partial (5–6 of 13 weeks), 2Q27 full | `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §2.2; module | dated by disclosure; magnitude fitted on four NA observations (PR #32) |
| Pull-forward reversal | one-time, reverses in the comp; largest in 1Q27 | module (mechanism M2) | derived from the share path and management's lead-time language; unmeasured |
| Cancellation tail and propensity | y/y-differenced; 46–49% from earlier cohorts | `D1_rnpl_cohort_scenarios.py`; module M3+M4 | propensity is a scenario input; 10-Q now says it is higher |
| Live unpaid book | 17–28 million nights at 30 June | `verify_balance_sheet.py` | derived from unearned fees against pre-RNPL norms; u vs B not separable |
| 5 November card rows | nights ≥10.3 weakens / ≤8.5 supports; 4Q26 guide ≥9.5 weakens / ≤7.5 supports; bundle figure ≥2.5 weakens / none or ≤1.5 supports; RNPL share ≥25% with nights ≥10 weakens; **(UF y/y − GBV y/y) ≤ −18 supports, −12 to −18 in line, > −8 weakens** | `D1_prereg_thresholds.csv` with the conditioning fix | pre-registered |
| February falsifier | 1Q27 guide ≥ +8.2% (169.0mm) falsifies the module outright | module | pre-registered |

The module's output goes into: B2's Q4 guide grid (the 4Q26 nights row), B3's volume line (as a three-column lap exhibit: none / NA-only / global), and the thesis map's composition story.

## 3. Synergy with the FY27 decomposition, channel by channel (note 02)

| channel | FY27 growth points | status | double-count rule |
|---|---|---|---|
| (a) bundle lap in volume | −3.06 to 0.00 | derived, fitted | (a) and (f) share the single-fee leg; (a) and (b) are two routes to one total (PR #32 global +6.42 with no tail; Jessie +6.52 with no lap) |
| (b) cancellation tail and propensity | −0.90 to 0.00 | derived | never add to (a) |
| (c) pull-forward reversal | −1.80 to 0.00 | unidentified | same object as (e); price in N or in κ, never both |
| (d) ADR mix and pricing residual | −2.00 to +1.78 | assumed | two-sided; B3's +2.83 remainder already sits at the mean-reversion end |
| (e) kernel recognition κ via lead time | −0.02 honest (−2.34 published) | derived | the published band is the λ convention |
| (f) fee line | +0.36 to +0.90 | assumed | migration subtracts −0.62 from GBV growth that B3 does not carry |
| (g) take-rate timing | 0.00, an output | measured | never a lever |

RNPL-aware reported growth at w = ⅔: 1Q27 +9.5 to +10.6% against a +17.9% comp; 2Q27 +8.5 to +10.6% against +16.5%. The Street's FY27 is a flat ~+11% in every quarter.

## 4. What the overnight forecast session needs before the memo freezes

1. **Re-fit λ at each w inside `l1-reconciliation-v2` and republish the band.** About 20 lines; it changes the memo's central sentence ("the indeterminacy is ~25× the edge" is true only under a convention B3 itself labels an upper bound).
2. **Put a lap term in B3's volume line or strike "product-bundle lap" from the thesis map.** Cheapest: carry the decomposition at three lap schedules as a three-column exhibit.
3. **Keep Krish's unearned-fees row on the 5 November card, conditioned on the GBV print.** Do not score funds payable. The earlier proposal to replace the row is withdrawn.
4. **Update the thesis map's stale attribution values** (geo mix −1.09 not −1.5; bedroom nights +0.63 not +0.46).
5. **Add the two 10-Q sentences to the statement ledger as official rows** and flag in the kernel note that λ stability is now contradicted by the issuer.
6. **Reconcile the 29 bridge's 1Q27 lap label with its FY27 nights number** (a 2.8-point gap inside the base case).

## 5. What would change the verdict

- A 1Q27 guide at or above +8.2% in February kills the module (both the ex-NA lap and the pull-forward reversal would have to be absent).
- Management repeating a quantified bundle contribution of 2.5 points or more on 5 November weakens the lap story; none, or 1.5 or less, supports it.
- A 3Q26 print at or above 10.3% nights with an RNPL share at or above 25% says the July expansion is bigger than the US anniversary.
- The unbilled RNPL balance from IR, if obtained, replaces the widest assumption (the unpaid book) with a disclosed number.

## 6. Files

- `docs/rnpl-short-audit/01_rnpl-nights-mechanics-audit.md` — reproduction of D1, five audit findings, module spec and run; `analysis/src/rnpl_short_audit/rnpl_nights_module.py`; `data/processed/rnpl_short_audit/rnpl_nights_module*.csv`.
- `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` — what B3's N embeds, the channel table, the λ re-fit, the phasing, the synergy map; `analysis/src/rnpl_short_audit/fy27_rnpl_channels.py`; nine CSVs.
- `docs/rnpl-short-audit/03_short-thesis-viability.md` — the thesis, the attacks ranked, the trade construction with EV, the judges' questions.
- `docs/rnpl-short-audit/04_balance-sheet-verification.md` — verdicts C1–C5 on Theo's note with the filing language; `analysis/src/rnpl_short_audit/verify_balance_sheet.py`; six CSVs.
- Team page (corrected and extended): https://claude.ai/code/artifact/d2a50fd7-fd7d-42a9-a3fe-e542f4abd99d
