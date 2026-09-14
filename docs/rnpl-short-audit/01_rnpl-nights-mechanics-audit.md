# RNPL nights mechanics: an adversarial audit of the team's four models, and one unified module

> **STATUS, added 11 Sep 2026 (evening):** this note inherited a claim from `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` that was **refuted** by `docs/rnpl-short-audit/04_balance-sheet-verification.md` after this note was written: the single-fee migration does *not* remove fees from unearned fees (FY2025 10-K Note 2 puts host and guest fees in unearned fees), so **unearned fees is the clean RNPL line and funds payable is the FX-noisy one**. Wherever this note says "score funds payable, not unearned fees", read instead: score **(3Q26 unearned fees y/y) − (3Q26 GBV y/y)**, at or below −18 points supports the drag, −12 to −18 in line with 1H26, wider than −8 weakens; Krish's −3% unearned-fees row stands. The balance-sheet unpaid-book figure is **17–28 million nights at 30 June** (not 7–19), which brackets the disclosed RNPL flow share and reconciles with the nights module's ~21 million. Everything else in this note is unaffected. Synthesis: `docs/rnpl-short-audit/00_SYNTHESIS.md`.


- **Date:** 2026-09-11. **Author:** Opus audit agent for Theo.
- **Script (new):** `analysis/src/rnpl_short_audit/rnpl_nights_module.py`. Run from the repo root with `python analysis/src/rnpl_short_audit/rnpl_nights_module.py`. No network, no reads, writes only under `data/processed/rnpl_short_audit/`.
- **Outputs (new):** `rnpl_nights_module.csv` (quarterly y/y with each mechanism's contribution), `_state.csv`, `_params.csv`, `_cohort_matrix.csv`, `_audit_sensitivities.csv`.
- **Read, read-only:** `docs/RNPL_HANDOFF.md`; `research/notes/2026-09-10_rnpl-conversion-framework.md`; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` and `analysis/src/overnight2/D1_rnpl_cohort_scenarios.py` (Krish); `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` and `analysis/src/rnpl_balance_sheet_bridge.py` (Theo); `research/notes/2026-09-10_nights-baseline-reconciliation.md`; `research/notes/2026-09-10_h1-to-h2-bridge.md`; PR #32 on `origin/krish/nights-quarterly`; `origin/jessie/backlog-conversion`; `docs/q3nowcast/SYNTHESIS.md`; `research/notes/q3nowcast/E_reviews-stays-index.md`; `data/processed/overnight/02_kpi_panel_quarterly.csv`.
- **Nothing existing was modified.** D1 was reproduced in a scratch copy so its committed outputs were not overwritten.
- Every number below carries an evidence label: **measured** (in a filing, letter or call), **derived** (arithmetic on measured inputs plus one stated identity), **assumed** (a scenario input), **withdrawn** (do not quote as live).

---

## 1. Bottom line

1. **D1 reproduces bit-identically.** The central cell is -0.15 / -0.31 / -0.62 / -0.93 growth points at +1 / +2 / +4 / +6pp propensity for 3Q26 and -0.14 / -0.28 / -0.57 / -0.85 for 4Q26; the booking-quarter by cancellation-quarter matrix reproduces to the third decimal, including the 46% and 49% earlier-cohort shares; the full grid runs -1.37 to -0.10 (3Q26) and -1.36 to -0.08 (4Q26). All eight committed CSVs match after stripping CRLF line endings (Krish ran it on Windows). **No discrepancy.** *(derived)*

2. **The forward-solve objection fails, and I can put a number on the failure.** Run A does absorb the 2025 excess cancellations into "gross", and Run B does then subtract them from the prior year a second time. But 3Q25 excess is only 0.118% of 3Q25 nights, so the double count is worth **0.001 to 0.002 growth points**. The analytic "burden-ratio-constant" treatment — hold the prior year at the disclosed print and charge only the y/y *increase* in the excess burden — gives **-0.926** for 3Q26 against D1's **-0.927**. The construction is sound. *(derived)*

3. **What actually makes the tail small is a different assumption: the 2025 base-year RNPL share, and it is assumed.** Forcing the 2025 share to zero (a genuinely pre-RNPL 2025 base) widens the 4Q26 tail by **0.18 points** and the 3Q26 tail by only 0.05. The slow-versus-fast 2025 ramp spans 0.05 (3Q26) and 0.11 (4Q26). So the base-year treatment is a 4Q26 question, not a 3Q26 one — the opposite of where the team has been looking. *(derived from an assumed share path)*

4. **The pull-forward is real, is not in PR #32 at all, and its largest quarter is 1Q27, which no team model carries.** PR #32 treats the whole fitted +2.40 NA points as permanent level, i.e. it sets pull-forward to exactly zero. Theo's bridge charges -0.10 to -0.30 points in 3Q26 (his own derivation in section 2.4 of that note gives 0.17 to 0.55), which on PR #32's parameters implies **14% to 43% of the fitted RNPL level was pull-forward, and up to 80% at the top of his own range** — a large implicit claim never stated as one. Derived from the share path instead, the reversal is **-0.11 (3Q26), -0.16 (4Q26), -0.46 (1Q27)** in base and **-0.26 / -0.36 / -1.03** at a 15% lead-time uplift. 1Q27 is four times 3Q26 because that is the quarter that laps the 20-point international share step. *(derived; the lead-time uplift magnitude is assumed)*

5. **Of the three assumptions the brief singles out, two are inert and one is the widest thing in the model.** The 25% baseline-cancellations-in-booking-month split moves 3Q26 by **0.000 points** (it applies in both years and cancels). The 85/15 stay-month split moves it by **0.001** (it only bites at quarter boundaries, one month in three). The rebooking offset moves it by **±0.20 points at the base +4pp propensity and ±0.29 to ±0.31 at the management-implied +6pp**, and it has never been measured — the calendar pilot's 32-44% reclosure is a descriptive lead, not a rebooking rate. *(derived)*

6. **The ex-NA lap is applied three different ways across three team artefacts, and the disagreements are worth 0.4 to 0.9 points a quarter.** PR #32 applies a flat -1.75 points of total nights from 1Q27 through 4Q27 and nothing in 4Q26. The ledger's dated schedule says **-0.70 to -0.88 in 4Q26** (the October-December 2025 cancellation redesign and fee tranche 1 were global, and PR #32 laps them in North America only), **-1.07 to -1.32 in 1Q27** (the fee lap carried plus only 5.5 of 13 weeks of the ex-NA RNPL lap), and -1.57 to -1.93 from 2Q27. So PR #32 is **too generous in 4Q26 by 0.70 to 0.88** and **too harsh in 1Q27 by 0.43 to 0.68**, and about right from 2Q27. The H1-H2 bridge has no geography at all — its -1.5 / -2.5 / -3 overlays are unfitted and already flagged as such. *(derived from sourced dates plus one split pinned out of sample by the 4Q25 disclosure)*

7. **The same partial-lap logic has never been applied to the US, and it cuts against the short.** D applies "the go-lives landed in the last 5-6 weeks of a 13-week quarter, so the lap is partial" to ex-NA in 1Q27. Nobody applies it to US RNPL in 3Q26, where the 3Q25 call says "beginning of Q3" but the newsroom announcement is dated 14 August 2025. If US RNPL was live 6.5 of 13 weeks in 3Q25, the 3Q26 lap should remove only half of the 0.69 points and **+0.35 points come back**. This is weakening evidence and it is kept on the record; PR #32's bull case reaches the same place by a different route (+0.5 x 2.40). *(assumed; the two sources conflict)*

8. **Jessie's C(t) and Krish's tail are the same object. Using both double counts.** Both are the reported-nights drag from a higher RNPL cancellation propensity, modelled in both years. Jessie's FY26 drag is **-0.60 points** at a +2pp excess propensity; Krish's engine at the same +2pp gives **-0.31**. The factor of two is Jessie's RNPL share of bookings at **50% in 2026** against a disclosure-consistent **16.7 to 18%** of nights. Jessie's L(t) and PR #32's fitted +2.40 / +2.29 are also the same object. The unified module carries each mechanism once. *(derived)*

9. **The short is a lap thesis, not a cancellation thesis, and the audit strengthens that.** The cancellation drag is -0.3 to -0.9 points in 3Q26 on any plausible propensity. The level lap plus the ex-NA correction is 1.4 to 2.6 points by 4Q26. Anyone pitching RNPL cancellations as the driver is pitching the small term.

10. **Unified module, base case: 3Q26 +9.49% (146.3mm), 4Q26 +7.61% (131.2mm), FY27 +6.41% (619mm).** Bands 8.76 to 10.25, 6.58 to 8.35, 5.64 to 6.88. 3Q26 sits inside the reviews index band (8.5 to 11.0) and below the 10.0 floor of "low double digits" in base and bear but not in bull. 4Q26 and FY27 are where the module and the team baseline actually diverge: **1.3 points and 1.8 points**. *(derived)*

---

## 2. Tables

### 2.1 Reproduction of D1 (task 1)

| Check | Committed | Reproduced | Status |
|---|---|---|---|
| Central cell 3Q26, +1 / +2 / +4 / mgmt-implied pp | -0.15 / -0.31 / -0.62 / -0.93 | identical | pass |
| Central cell 4Q26 | -0.14 / -0.28 / -0.57 / -0.85 | identical | pass |
| Full grid range, 3Q26 excluding zero-delta cells | -1.37 to -0.10 | identical | pass |
| Booking x cancellation matrix, 3Q26 column | 1.823mm, 46% from earlier cohorts | identical | pass |
| Booking x cancellation matrix, 4Q26 column | 1.851mm, 49% from earlier cohorts | identical | pass |
| Management-implied propensity | 6.0pp at a 16.67% 1Q26 nights share | identical | pass |
| All eight CSVs, byte-compare | — | identical after CRLF strip | pass |

### 2.2 What moves the 3Q26 tail (task 2c), measured

Reference cell: +4pp propensity, ADR ratio 1.33, 2.2-month lead, +7% uplift, 25% rebooking. Regenerate with `rnpl_nights_module_audit_sensitivities.csv`.

| Assumption | Range tested | 3Q26 move, pts | 4Q26 move, pts | > 0.2 pts? | Label |
|---|---|---:|---:|---|---|
| Baseline cancellations in the booking month | 0 / 25 / 50% | 0.000 | 0.001 | no | mechanism measured, magnitude assumed |
| Excess cancellations in the stay month | 70 / 85 / 100% | 0.001 | 0.005 | no | window measured, split assumed |
| **Rebooking offset** | **0 / 25 / 50%** | **±0.196** | **±0.180** | **borderline at +4pp; ±0.29 to ±0.31 at +6pp** | mechanism measured, magnitude assumed |
| Mean lead time | 1.8 / 2.2 / 3.0 months | ±0.014 | ±0.012 | no | derived |
| RNPL / non-RNPL ADR ratio, at a fixed propensity | 1.00 to 1.33 | 0.149 | 0.130 | no | derived at 1.33 |
| **Incremental propensity** | **+2 / +4 / +6pp** | **±0.294** | **±0.271** | **yes** | assumed |
| 2025 base-year share, slow vs fast | 2.5/7.0 vs 6.0/12.0 | 0.048 | 0.114 | no | assumed |
| 2025 base-year share forced to zero | 0 / 0 | 0.051 | **0.176** | no (3Q26); near (4Q26) | limiting case |

A trap worth recording: under the management-implied rule the propensity is defined as 1.0 / (RNPL nights share), so propensity x share is identically 1 and **the ADR ratio cancels exactly**. Three of D1's six grid axes (ADR ratio, and to a lesser extent lead time and its uplift) are near-inert in the management-implied cells. The 2,025 cells have far fewer effective degrees of freedom than they look; the honest count is propensity x rebooking x base-year share.

### 2.3 The pull-forward, two ways (task 2b)

| Route | 3Q26 | 4Q26 | 1Q27 | 2Q27 |
|---|---:|---:|---:|---:|
| PR #32, as built (whole +2.40 is permanent level) | 0.00 | 0.00 | 0.00 | 0.00 |
| x = 10% of the fitted +2.40 is pull-forward | -0.07 | — | — | — |
| x = 25% | -0.17 | — | — | — |
| x = 50% | -0.35 | — | — | — |
| Theo's bridge (mild / central / heavy), implying x = 14 / 29 / 43% | -0.10 / -0.20 / -0.30 | 0 | 0 | 0 |
| **Module M2, base (L 2.2m, u 7%)** | **-0.11** | **-0.16** | **-0.46** | **-0.04** |
| **Module M2, at u = 15%** | **-0.26** | **-0.36** | **-1.03** | **-0.10** |

Two findings. Theo's -0.10 to -0.30 in 3Q26 implies 29% to 87% of PR #32's fitted RNPL level was pull-forward, which nobody has claimed in words. And the reversal is largest in **1Q27**, because pull-forward scales with the *change* in RNPL share and the biggest change was the February 2026 international step from ~9% to ~20% of GBV. Every team model carries zero there.

### 2.4 The ex-NA lap, three treatments (task 2d)

| Quarter | PR #32 | Ledger-dated schedule | PR #32 error |
|---|---:|---:|---:|
| 4Q26 | 0.00 | -0.70 to -0.88 | too generous by 0.70 to 0.88 |
| 1Q27 | -1.75 | -1.07 to -1.32 | too harsh by 0.43 to 0.68 |
| 2Q27 onward | -1.75 | -1.57 to -1.93 | -0.18 to +0.18, consistent |
| H1-H2 bridge | no geography; flat -1.5 / -2.5 / -3 at total level, unfitted, horizon stops at 4Q26 | — | not comparable |

### 2.5 The unified module, base case (task 3)

Reference = team reconciled baseline for 3Q26/4Q26, PR #32 base with the NA lap only and **no** ex-NA lap for 1Q27-4Q27 (the ex-NA lap is supplied by M1 on its dated schedule, so using PR #32's `exna_lap=True` row instead would double count).

| Quarter | Reference % | M1 level/lap | M2 pull-fwd | M3 deferral | M4 propensity | Total | **Nights y/y** | **Nights mm** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 3Q26 | 9.89 | +0.30 | -0.11 | -0.02 | -0.57 | -0.40 | **+9.49** | **146.3** |
| 4Q26 | 8.90 | -0.59 | -0.16 | -0.10 | -0.45 | -1.29 | **+7.61** | **131.2** |
| 1Q27 | 8.17 | -1.00 | -0.46 | -0.15 | -0.10 | -1.70 | **+6.47** | **166.3** |
| 2Q27 | 8.17 | -1.55 | -0.04 | -0.07 | -0.07 | -1.73 | **+6.44** | **157.9** |
| 3Q27 | 8.17 | -1.68 | -0.04 | -0.04 | -0.03 | -1.80 | **+6.37** | **155.6** |
| 4Q27 | 8.17 | -1.75 | -0.04 | -0.03 | -0.00 | -1.82 | **+6.35** | **139.5** |
| **FY27** | | | | | | | **+6.41** | **619.3** |

Bands (bear / bull): 3Q26 8.76 / 10.25, 4Q26 6.58 / 8.35, 1Q27 5.28 / 7.34, FY27 5.64 / 6.88.

Cross-checks. 3Q26 base +9.49 against Theo's re-based +9.27, the reviews index +9.5 (band 8.5 to 11.0) and the external stack +9.2. 4Q26 base +7.61 against Theo's +7.64. FY27 base +6.41 against PR #32's global-lap row of +6.42 — the two converge from different constructions, which is the strongest single validation in this note. Against WS10 the module is 0.8 / 2.3 / 2.7 points lower in 3Q26 / 4Q26 / FY27.

### 2.6 State variables and the exposure cross-check

| Quarter (base) | RNPL nights share | Live unpaid backlog, mm nights | Excess cancellations recognised, mm |
|---|---:|---:|---:|
| 2Q26 (cross-check) | 16.7% | 20.8 | 1.03 |
| 3Q26 | 17.5% | 22.6 | 1.15 |
| 4Q26 | 18.3% | 22.3 | 1.17 |
| 1Q27 | 18.3% | 26.1 | 1.32 |
| 4Q27 | 18.3% | 24.8 | 1.32 |

The module's 30 June 2026 live unpaid book of **20.8mm nights** sits just above the top of the **7 to 19mm** range the balance-sheet joint solve derived from unearned fees and funds payable, and well below the 40mm illustrative exposure in `outputs/rnpl-audit-20260910/materiality.md`. That is a mild warning that the assumed 2H26 share path is generous; if the 3Q26 10-Q solve lands at the low end again, the tail scales down roughly proportionally.

---

## 3. Method

**Reproduction.** `D1_rnpl_cohort_scenarios.py` was copied to a scratch tree and run there, so its committed outputs in `data/processed/overnight2/D/` were never touched. The script reads nothing from disk, so the copy is exact. Outputs were compared byte-for-byte after normalising line endings.

**The unified module.** One monthly booking-cohort engine, January 2024 to June 2028, reporting 3Q26 through 4Q27. Gross monthly bookings are solved forward so that reported nights reproduce every disclosed quarter and then the reference path; the solve runs with the excess leg off, so the reference is the no-RNPL-tail counterfactual by construction. Four mechanisms are then made orthogonal and added in growth points:

- **M1, conversion uplift and its lap.** A dated level gain contributes to y/y only inside its window. The reference already laps the North American legs, so M1 carries only what PR #32 omits or mis-dates: the ex-NA fee and cancellation lap from 4Q26, the ex-NA RNPL lap at 5.5/13 in 1Q27 and in full from 2Q27, the July-2026 booking-type expansion as a positive level whose own lap falls in 3Q27, and the US partial-quarter correction.
- **M2, pull-forward.** `PF(q) = Δp(q) × L × u / 3` of a quarter's nights, a flow addition proportional to the *change* in RNPL nights share, so it vanishes at plateau. The y/y effect is `PF(q) − PF(q−4)`.
- **M3, cancellation deferral.** The timing-only term: excess cancellations recognised at the payment deadline minus the same quantity recognised in the booking quarter. It flatters during the ramp and deposits the tail afterwards, and nets to approximately zero over a full cycle. It contains no propensity level.
- **M4, higher propensity.** The steady-state drag: what the cost would be if every excess cancellation landed in its own booking quarter. Scales with the y/y *change* in RNPL nights share.

**M3 + M4 is Krish's tail, re-partitioned, not added to.** The module asserts this in a self-check: at D1's central-cell parameters it returns -0.93 (3Q26) and -0.85 (4Q26) against D1's -0.927 and -0.855. The y/y form used is the first-order-exact version of D1's `growth_B − growth_A`, which holds the prior year at the reference and charges only the increase in the excess-cancellation burden ratio.

**Scenario design.** Bear / base / bull vary the six parameters that survived the sensitivity audit: propensity (6 / 4 / 2pp), rebooking (0 / 25 / 50%), the 2025 and 2H26 share paths, the lead-time uplift (15 / 7 / 0%), the ex-NA lap split (0.88 / 0.79 / 0.70 and 1.05 / 0.96 / 0.87), the July expansion (0.10 / 0.20 / 0.30) and the US partial-lap correction (0 / +0.17 / +0.34). The two inert assumptions are held fixed and labelled inert in `_params.csv`.

**Withdrawn numbers are not used anywhere:** the -3.4pp FX step, "82% determined", the +4.05% fee uplift, the 9/9 drift rule, "half of ADR is unit size", and the "+10.2% consensus" (which is the team's own frozen 5 November card, not consensus — see the reconciliation note, section 1.2). They are listed as withdrawn in `_params.csv` so nobody re-imports them.

---

## 4. What this can and cannot identify

**It can.** Separate the four mechanisms so they can be added without double counting, and say which of the team's four models is carrying which one. Size what an assumed propensity is worth once both years are modelled and the timing is right. Put the ex-NA lap on its sourced dates and show where PR #32 is too generous and where too harsh. Rank the assumptions by how much they actually move the answer, and retire two of them. Extend the horizon to 4Q27 and FY27, where the divergence from the team baseline is largest and the February catalyst lives. Reconcile to Jessie's structure without importing her calibration.

**It cannot.** Measure the RNPL cancellation propensity — it is a scenario input in every cell, and the management-implied +6.0pp rests on attributing the whole 16-to-17 platform move to RNPL, which the 2Q26 Strict-to-Firm policy migration alone makes unsafe. Measure the live unpaid backlog; the FY2025 10-K confirms Airbnb hedges an unbilled balance for confirmed RNPL bookings but never discloses it. Measure the rebooking offset, which is the widest remaining assumption. Separate a payment-timing shift from a cancellation on either balance-sheet line, because a cancelled RNPL booking never appeared on them. Establish causality: the October 2025 cancellation redesign, two fee tranches, the Strict-to-Firm migration, the Middle East conflict and the World Cup all overlap the window, and currency-level exclusion of BRL, INR and TRY means country is not treatment assignment. Error-bound PR #32's two fitted product parameters, which rest on four WS10 North American estimates.

**Evidence that weakens the thesis, kept on the record.** The 2Q26 10-Q's "higher cancellation rates" sentence is official but unquantified, and the same filing says management tests cohorts to be net beneficial at check-in. Management says realised cancellation curves track tests and that elevated cancellations are already absorbing into reported results. The July 2026 booking-type expansion is fresh treatment landing inside 3Q26 and is entirely unquantified — it is the largest single offset to the 3Q26 lap. The US partial-lap correction is worth up to +0.35 points and nobody has applied it. The guide has been beaten 19 of 19 times. And on the arithmetic itself, the cancellation drag never reaches the original bridge's -1.5 to -2.5 overlay at any plausible propensity with any rebooking offset at all.

---

## 5. The five numbers a short would quote

| # | Number | Evidence status | Pinned by |
|---|---|---|---|
| 1 | **4Q26 nights +7.6% (131.2mm), band 6.6 to 8.4**, against the team baseline +8.9% and WS10 +9.9%. The guide issued 5 November is the trade. | derived | `analysis/src/rnpl_short_audit/rnpl_nights_module.py` -> `data/processed/rnpl_short_audit/rnpl_nights_module.csv` |
| 2 | **0.70 to 0.88 points of 4Q26 nights**: the ex-NA October-2025 cancellation-redesign and single-fee lap that PR #32 and therefore the team baseline omit entirely. Dates are sourced; the split is pinned out of sample by the 4Q25 "over 200 basis points". | derived | `data/processed/overnight2/D/D1_exna_4q26_gap.csv`; `research/notes/overnight2/D_...md` s2.5 |
| 3 | **46% of 3Q26 and 49% of 4Q26 excess cancellations arrive from earlier booking cohorts.** This is the tail, sized, and it is why a booking-date KPI can deteriorate while stays and revenue do not. | derived | `data/processed/overnight2/D/D1_cohort_matrix_cancellation.csv` |
| 4 | **1Q27 pull-forward reversal of -0.46 to -1.03 points**, the largest single quarter of the reversal, carried by no team model. It laps the February 2026 international share step. | derived (lead-time uplift magnitude assumed) | `rnpl_nights_module.csv`, column `m2_pull_forward_pts`; `_audit_sensitivities.csv` rows b2 |
| 5 | **RNPL is over 20% of GBV and its bookings "have experienced higher cancellation rates than historic bookings"; GBV, revenue and cash receipts "may become less correlated".** Audited MD&A, not a call mirror. The platform cancellation rate went ~16% to ~17%. | measured (the 16-to-17 remark is hedged three ways: no base period, no denominator, unit of account unstated) | 2Q26 10-Q MD&A, `data/raw/regulatory/quantification/abnb_2026q2_10q.html`; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` s1.1 |

**The number a short should not lead with:** the cancellation drag itself, at -0.3 to -0.9 points in 3Q26. It is two to fifteen times smaller than the level lap. This is a lap-and-pull-forward thesis with a cancellation tail attached, not a cancellation thesis.

---

## 6. What would falsify this module

**On 5 November (3Q26 print and the 4Q26 guide).**

| Test | Falsifies the module if | Module says |
|---|---|---|
| 3Q26 nights y/y | at or above **10.3%** (147.3mm), i.e. no deceleration from 2Q26 with the US anniversary inside the quarter | base +9.49% (146.3mm); only the bull cell reaches 10.25% |
| **4Q26 nights guide** | implies **9.5% or above** — that needs the ex-NA lap to be absent *and* the tail to be zero *and* tranche-2 plus the July expansion to more than cover the 2025 bundle | base +7.61% (131.2mm) |
| Funds payable y/y (not unearned fees) | **+11% or above** with the unearned-fees-minus-funds-payable gap narrowing: deferral arriving on schedule, no unpaid hole | +5% to +11% is on-schedule; the unearned-fees line alone is confounded by the fee migration and can print -2% to -17% with no cancellation effect at all |
| Quantified bundle contribution for 3Q26 | management gives **2.5 points or more** | M1 says the bundle's y/y contribution is near zero in NA and negative from 4Q26 globally |
| RNPL GBV share disclosed for 3Q26 | **25% or above with nights at or above 10%** | base assumes 22%; a higher share with no deceleration breaks the flattening-flow/growing-stock asymmetry the thesis rests on |
| Implied live unpaid book, re-solved on the 3Q26 10-Q | comes back at **7 to 12mm nights** again | module implies ~20.8mm at 2Q26 and ~22.6mm at 3Q26; a low re-solve means the share path is too generous and the whole tail scales down |

**In February (the 1Q27 guide and the FY27 framing).** 1Q27 is the single cleanest test in the horizon, because all three disputed mechanisms land in it at once: the partial ex-NA lap (M1), the largest pull-forward reversal (M2), and the residual tail (M3+M4).

- **1Q27 guide at or above +8.2% (169.0mm or more)** falsifies the module outright: that is PR #32's no-ex-NA-lap reference, and it requires both the 1.0-point M1 correction and the 0.46-point M2 reversal to be absent. Module base is **+6.47% (166.3mm)**.
- **1Q27 between +7.3% and +8.2%** is consistent with the module's bull cell only, and would say the pull-forward reversal is near zero — i.e. RNPL never lengthened lead times materially, which contradicts management's own language in four prints.
- **FY27 nights framed at 9% or above** falsifies FY27 +6.4%. Note PR #32 reaches +6.42% by a completely different route; both would have to be wrong together.
- **If management dates the ex-NA RNPL contribution as a full-quarter 1Q26 effect**, the 5.5/13 partial-lap fraction is wrong in the direction that makes 1Q27 *worse*, not better — the module would be too generous, not too harsh.
- **If the July-2026 booking-type expansion is quantified at more than ~0.5 points of nights**, M1 turns positive through 2Q27 and the 4Q26 and 1Q27 calls both weaken.

---

## 7. Next evidence, in order of value per unit of effort

1. **Ask IR for the unbilled confirmed-bookings balance for RNPL.** The FY2025 10-K says Airbnb hedges it, so it exists internally. It collapses the widest exposure assumption and scores the 20.8mm-versus-7-to-19mm gap in section 2.6 directly.
2. **Ask for the RNPL GBV share and the RNPL nights share for the same quarter.** Their ratio is the ADR ratio, currently derived at 1.33x from the 1Q26 nights-versus-GBV wedge rather than disclosed.
3. **Ask what the July 2026 "types of bookings" expansion covers.** It is the only fresh treatment inside the quarter being printed and the largest unquantified offset to the 3Q26 lap.
4. **Pin the US RNPL live date inside 3Q25** ("beginning of Q3" versus 14 August). Worth 0 to +0.35 points of 3Q26 and it currently sits as an unresolved conflict between a call and a newsroom post.
5. **Re-solve the two prepaid lines on the 3Q26 10-Q the evening of 5 November** and score funds payable, not unearned fees, per Theo's replacement rule.
6. **Relabel PR #32's "+10.2% consensus" as the team frozen card (WS13/WS14)** before anything is frozen. It is unrelated to this workstream and is the line most likely to mislead a reader.

---

## 8. Files

**New, written by this audit:**

- `docs/rnpl-short-audit/01_rnpl-nights-mechanics-audit.md` — this note.
- `analysis/src/rnpl_short_audit/rnpl_nights_module.py` — the unified module and the audit sensitivities.
- `data/processed/rnpl_short_audit/rnpl_nights_module.csv` — quarterly y/y for 3Q26 to 4Q27 and FY27, bear/base/bull, with each mechanism's contribution per quarter.
- `data/processed/rnpl_short_audit/rnpl_nights_module_state.csv` — RNPL GBV and nights share, live unpaid backlog, excess cancellations recognised, lead times, propensity, rebooking.
- `data/processed/rnpl_short_audit/rnpl_nights_module_params.csv` — every parameter labelled measured / derived / assumed / withdrawn with its source.
- `data/processed/rnpl_short_audit/rnpl_nights_module_cohort_matrix.csv` — booking quarter by cancellation-recognition quarter, per scenario, through 4Q27.
- `data/processed/rnpl_short_audit/rnpl_nights_module_audit_sensitivities.csv` — regenerates every number in section 2.2, 2.3 and 2.4.

**Read, unchanged:** `docs/RNPL_HANDOFF.md`; `research/notes/2026-09-10_rnpl-conversion-framework.md`; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`; `analysis/src/overnight2/D1_rnpl_cohort_scenarios.py`; `data/processed/overnight2/D/*.csv`; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`; `analysis/src/rnpl_balance_sheet_bridge.py`; `research/notes/2026-09-10_nights-baseline-reconciliation.md`; `research/notes/2026-09-10_h1-to-h2-bridge.md`; `origin/krish/nights-quarterly` (`research/notes/nights_quarterly.md`, `analysis/src/nights_quarterly.py`, `data/processed/nights_quarterly_na.csv`, `nights_quarterly_total.csv`); `origin/jessie/backlog-conversion` (`analysis/src/nights_simple.py`, `research/notes/choice_nights_driver.md`); `docs/q3nowcast/SYNTHESIS.md`; `research/notes/q3nowcast/E_reviews-stays-index.md`; `data/processed/overnight/02_kpi_panel_quarterly.csv`.
