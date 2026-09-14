# RNPL: what the balance sheet already discloses, the fee-migration confound, and a re-based 3Q26 nights bridge

> **STATUS, added 11 Sep 2026 (evening) after adversarial verification — read before using any number below.**
> Verification note: `docs/rnpl-short-audit/04_balance-sheet-verification.md` (script `analysis/src/rnpl_short_audit/verify_balance_sheet.py`).
> - **Bottom line 1 (10-Q language) — CONFIRMED.** Both sentences are verbatim in the 2Q26 10-Q MD&A and absent from the 60-row ledger.
> - **Bottom line 2 and section 2.1 (single-fee migration confounds unearned fees) — REFUTED.** FY2025 10-K Note 2: "Host and guest fees are recorded as cash with a corresponding amount in unearned fees"; guest payments are recorded "net of service fees" in funds payable; "for all bookings" the host is paid "net of the host's service fees". So the host-only fee sits in unearned fees exactly as the guest fee did, and the migration moves unearned fees *up* 3–4%, not down. The 4Q25 divergence is FX translation of non-USD funds payable (+$627M in FY25; ex-FX funds payable +2 to +7% vs GBV +16%). **Unearned fees is the FX-clean, migration-neutral line; funds payable is the noisy one.**
> - **Bottom line 3 and section 2.2 (joint solve) — MODIFIED.** `m` is not identified (it returns −1.4% for 3Q25, before the migration existed, and is invariant to B). Solved on unearned fees alone, the unpaid RNPL share is **14–15% at B = 1.00 and 22–23% at B = 1.10**, i.e. **17–28 million unpaid nights at 30 June** (13.6–37.3 across the divisor and ADR stress). That brackets the disclosed 20–21% flow share and needs no pre-payment-cancellation story; the data favour a book 4–6% longer-dated. **The 7–19 million figure is withdrawn.** The script also divides by the guest-fee share (0.124) where the total fee (~0.133–0.155) belongs, overstating the backlog 7–25%.
> - **Bottom line 2's consequences and section 2.3 (score funds payable) — REFUTED.** Funds payable carries an ±8.7-point annual FX swing; unearned fees reconciles to the cash-flow statement within $3–8M. **Krish's −3% unearned-fees row stands** and cannot be tripped by the migration; **Jessie's +4-point conversion break is not confounded.** Corrected 5 November rule: score **(3Q26 unearned fees y/y) − (3Q26 GBV y/y)**: at or below −18 points supports the drag; −12 to −18 in line with 1H26; wider than −8 weakens it. At mid-teens GBV that maps to −3% (~$1,765M), Krish's number, conditioned on the GBV print.
> - **Bottom line 7 (marginal ADR 1.33x / 1.5x) — MODIFIED.** 4/3 is an upper bound against prior-year ADR (1.22x against the 1Q26 ADR); the 4Q25 "1.5x" rests on a ">200bp" denominator and is not supported.
> - **Section 2.4 (the bridge) stands** but is superseded by the unified module in `docs/rnpl-short-audit/01_rnpl-nights-mechanics-audit.md`: the US lap in 3Q26 is partial ("beginning of Q3"), worth +0.35 against the short, and the pull-forward's biggest quarter is 1Q27 (−0.46 to −1.03), so the module's 3Q26 is +9.49% (band 8.8–10.3), 4Q26 +7.61% (6.6–8.4), FY27 +6.41% (5.6–6.9).
> - Next-evidence item 3 (replace the unearned-fees row) is withdrawn; item 4 (add the 10-Q sentences to the ledger) stands.


- **Date:** 2026-09-11 (after pulling origin/main at 5bd2d08, PRs #39 to #44). **Author:** Theo Machado (compiled with Claude Code).
- **Script:** `analysis/src/rnpl_balance_sheet_bridge.py` (reads only `data/processed/overnight/02_kpi_panel_quarterly.csv` and `data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv`; no network). Printed output: `data/processed/rnpl_balance_sheet/rnpl_balance_sheet_bridge_output.txt`.
- **Builds on:** `docs/RNPL_HANDOFF.md`, `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` (Krish), `research/notes/2026-09-05_eu-platform-and-backlog.md` section 3b on `origin/jessie/backlog-conversion` (Jessie), `docs/q3nowcast/SYNTHESIS.md`.
- **Nothing in the live model, the workbook or any other workstream's paths was changed.**

## 1. Bottom line

1. **The 2Q26 10-Q says, in audited MD&A, what the ledger only has from call mirrors.** "To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking. As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated." (`data/raw/regulatory/quantification/abnb_2026q2_10q.html`, MD&A, Key Business Metrics.) The ledger's three 10-Q rows (D057 to D059) do not carry this sentence. Two consequences: the "higher cancellations" fact is now official, not mirror; and Airbnb itself warns that the GBV-to-revenue timing the recognition kernel relies on will drift as adoption grows. The kernel's lambda table reproduces to 2dp through 2Q26; the 10-Q says not to expect that to hold.

2. **Unearned fees and funds payable have moved in opposite directions relative to GBV since 4Q25, and that is the single-fee migration, not RNPL.** RNPL removes a booking from both lines until the guest pays. The migration to a 15.5% host-only fee removes the separate guest fee from unearned fees and puts the guest's whole payment into funds payable. In 4Q25, the first migration quarter, funds payable grew faster than GBV (+17.3% vs +15.9%) while unearned fees grew half as fast (+7.9%). Only a transfer between the two lines produces that sign pattern. So Jessie's +4-point backlog-conversion break in 1H26 is RNPL plus migration, and the pre-registered 5 November unearned-fees test in D section 5 (at or below -3% y/y "supports the drag") can be tripped by migration alone: deferral-only scenarios give 3Q26 unearned fees anywhere from -2% to -17% y/y with no cancellation effect at all. **Score funds payable, not unearned fees, and score the gap between the two lines as the migration term.**

3. **Solving the two lines jointly gives the unpaid RNPL backlog the handoff calls its widest assumption.** With the pre-RNPL seasonal norms and a 12.4% guest-fee share, the unpaid share of the paid-equivalent backlog is 6.4% at 1Q26 and 7.5% at 2Q26 if the book is no longer-dated than before, and 15% to 16% if it is 10% longer-dated (management says lead times lengthened in all regions). That is $1.6 to $4.7bn of unpaid GBV, or **7 to 19 million live unpaid nights at 30 June**, against the 40 million illustrative exposure in `outputs/rnpl-audit-20260910/materiality.md`. At 7 to 19 million, a one-point 3Q26 haircut from the opening backlog alone needs a 7 to 17 point upward revision in the conditional cancellation probability, which is implausible. That corroborates Krish's cohort engine from an independent direction: the opening-backlog tail is 0.5 to 1.1 million nights, and the within-quarter flow matters more.

4. **The migration share of the backlog solves at 8.0% to 8.5% of GBV in 1H26** against "over a quarter" and "about half" of active listings on the single fee (D041, D047). Listings are not GBV, and the backlog at 30 June was booked when penetration was lower, so the two are not inconsistent; but it says the fee migration is far from done on a dollar basis, and the unearned-fees line will keep falling through 2H26 regardless of RNPL.

5. **How RNPL inflates reported nights, in one sentence:** the US launch quarter (3Q25) received the gross uplift, the pull-forward and the cancellation deferral with almost no cancellation tail, and 3Q26 is the quarter that pays the tail while lapping the uplift. Four mechanisms, two permanent and two that reverse: (i) real conversion uplift, permanent level, contributes zero to y/y once lapped; (ii) pull-forward from longer lead times, one-time, subtracts from y/y in the comp quarter (-0.2 to -0.4 points in 3Q26 from the US cohort alone); (iii) cancellation deferral to the payment deadline, which inflates net nights during the ramp and deposits excess cancellations in later quarters (Krish's tail: -0.3 to -0.9 points in 3Q26); (iv) a higher cancellation propensity, permanent, which drags net nights as the share rises. Management's "net beneficial at check-in" test (D019) is true and irrelevant to (ii) and (iii), which are pure timing.

6. **Re-based 3Q26 nights: +9.3% central (146.0mm), band 8.8 to 9.8; 4Q26 +7.6% (131.2mm), band 7.2 to 8.1.** The team baseline of 9.9 / 8.9 carries none of the tail, the pull-forward or the July eligibility expansion, and 4Q26 omits the ex-NA lap Krish sized at 0.70 to 0.88. The reviews index reads 9.5 on a stay basis and cannot see a booking-date tail; subtracting the central tail gives 8.9. Every route lands below the 10.0 floor of "low double digits". The 5 November nights line is a deceleration from 10.3 and, on these numbers, a miss on the KPI with the revenue beat intact. The Q4 nights guide, which is the trade, points at high single digits.

7. **Two parameters the D grid labels assumed are pinned by disclosure.** The marginal ADR of bundle-driven bookings is 4/3 = 1.33x the average (1Q26: ~4 points GBV on ~3 points nights) and 3/2 = 1.5x (4Q25: ~300bp on >200bp). At 21% GBV share and 1.33x, the RNPL nights share is 16.7%, which is the D note's adr_plus25 case, so nothing in the grid moves; but the label changes from assumed to derived.

## 2. Tables

### 2.1 The two prepaid-customer lines against GBV (y/y, %)

| Quarter | GBV | Unearned fees | UF minus GBV | Funds payable | FP minus GBV | UF gap minus FP gap |
|---|---:|---:|---:|---:|---:|---:|
| 1Q25 | 7.0 | 11.9 | +4.9 | 5.0 | -2.0 | +6.9 |
| 2Q25 | 10.8 | 9.0 | -1.8 | 7.0 | -3.8 | +2.0 |
| 3Q25 | 13.9 | 9.8 | -4.1 | 9.7 | -4.2 | +0.2 |
| 4Q25 | 15.9 | 7.9 | -8.1 | **17.3** | **+1.4** | **-9.5** |
| 1Q26 | 19.2 | 0.4 | -18.8 | 15.0 | -4.2 | -14.6 |
| 2Q26 | 15.7 | -0.9 | -16.6 | 10.4 | -5.3 | -11.4 |

Through 3Q25 (US RNPL live, no migration) both lines lag GBV by the same 4 points: pure RNPL. From 4Q25 the lines split, and the split is the migration.

### 2.2 Joint solve for the unpaid RNPL share (u) and the single-fee share (m) of the backlog

Model: `UF / norm = (1 - u)(1 - m) B` and `FP / norm = (1 - u)(1 + 0.142 m) B`, with the pre-RNPL seasonal norm for each line (stock over next-quarter revenue, 2023 to 1H25), 0.142 = guest fee over host payout under the split fee, and B the backlog scale against the norm (1.00 = no lengthening).

| Quarter | UF ratio | FP ratio | B | m | u | Unpaid GBV, $bn | Unpaid nights, mm at 1.33x ADR |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4Q25 | 0.945 | 0.971 | 1.00 | 2.4% | 3.2% | 0.5 | 2.1 |
| 1Q26 | 0.861 | 0.947 | 1.00 | 8.0% | 6.4% | 1.6 | 6.6 |
| 1Q26 | 0.861 | 0.947 | 1.10 | 8.0% | 14.9% | 4.2 | 16.9 |
| 2Q26 | 0.846 | 0.936 | 1.00 | 8.5% | 7.5% | 2.0 | 8.3 |
| 2Q26 | 0.846 | 0.936 | 1.05 | 8.5% | 11.9% | 3.4 | 13.9 |
| 2Q26 | 0.846 | 0.936 | 1.10 | 8.5% | 15.9% | 4.7 | 19.4 |

The disclosed 20 to 21% GBV flow share would put RNPL at 20% or more of the backlog if RNPL bookings sat in the book as long as others. The balance sheet shows less. The gap is either a longer-dated book (B above 1) or RNPL bookings that cancel before they ever pay, which never touch either line. Both are RNPL fingerprints; the data cannot split them, which is why u is given as a range.

### 2.3 3Q26 quarter-end lines under deferral only, for the 5 November score sheet

Pre-RNPL, pre-migration expectation at the team's 4Q26 revenue of $3,166mm: unearned fees $2,105mm (+15.6% y/y), funds payable $8,468mm (+17.5% y/y).

| u | m | Unearned fees, $mm | y/y | Funds payable, $mm | y/y | Reading |
|---:|---:|---:|---:|---:|---:|---|
| 7% | 9% | 1,781 | -2.1% | 7,975 | +10.6% | 2Q26 solved values carried |
| 10% | 12% | 1,667 | -8.4% | 7,751 | +7.5% | share 22 to 23%, migration ~60% of listings |
| 12% | 18% | 1,519 | -16.6% | 7,642 | +6.0% | July expansion plus migration ~80% |
| 7% | 0% | 1,957 | +7.5% | 7,875 | +9.2% | no migration effect at all |
| 15% | 0% | 1,789 | -1.7% | 7,198 | -0.2% | unearned-fees hole all RNPL |

Proposed replacement for the unearned-fees row in D section 5: **funds payable y/y between +5% and +11% is deferral on schedule; below +3% means the unpaid book is larger than modelled (more adoption, not more cancellation); the unearned-fees minus funds-payable growth gap is the migration term and should widen.** Neither line can see the cancellation hazard, because a cancelled RNPL booking was never recorded.

### 2.4 The bridge

| Scenario | Tail (D1 central cell) | Pull-forward reversal | July expansion | Ex-NA lap (4Q26) | 3Q26 | 4Q26 |
|---|---:|---:|---:|---:|---:|---:|
| Team baseline (PR #32) | 0 | 0 | 0 | 0 | 9.89% (146.8mm) | 8.90% (132.7mm) |
| Mild (+2pp propensity) | -0.31 / -0.28 | -0.10 | +0.30 / +0.15 | -0.70 | 9.78% (146.7) | 8.07% (131.7) |
| **Central (+4pp)** | -0.62 / -0.57 | -0.20 | +0.20 / +0.10 | -0.79 | **9.27% (146.0)** | **7.64% (131.2)** |
| Heavy (+6pp, management-implied) | -0.93 / -0.85 | -0.30 | +0.10 / +0.05 | -0.88 | 8.76% (145.3) | 7.22% (130.7) |
| Reviews index minus central tail | | | | | 8.9% | |

Pull-forward: 3Q25 US RNPL nights share 3.3 to 5.0% times a 7 to 15% lead-time uplift on 2.2 months gives 0.17 to 0.55% of 3Q25 nights booked early, which the 3Q26 comp gives back. July expansion is the one unquantified positive (D044) and is deliberately small.

## 3. Method

Norms are the 2023, 2024 and 1H25 means of each line divided by the following quarter's revenue, by season; 3Q26 revenue is the team point of $4.80bn. The guest-fee share of GBV is 14.2% of the host subtotal, so 12.4% of GBV. The joint solve divides the two ratios to remove (1 - u), solves for m, then for u. B is a stated sensitivity, not a fitted number. Unpaid GBV is u times the paid-equivalent backlog implied by the unearned-fees norm; nights use the quarter's ADR times 1.33.

## 4. What this can and cannot identify

It can show that the unearned-fees line is confounded by the fee migration from 4Q25, size that confound, and give a two-line exposure estimate that is disclosure-derived rather than assumed. It can size the pull-forward reversal from management's own lead-time language and the D note's share path. It cannot measure the cancellation propensity, cannot see cancelled RNPL bookings on either balance-sheet line, cannot separate a longer-dated book from pre-payment cancellations, and inherits every assumption in the D1 central cell for the tail. The funds-payable line also holds occupancy taxes and payouts in transit, which the norm absorbs only if their share is stable. Two clean pre-RNPL years per season is the sample.

## 5. Next evidence

1. Ask IR for the unbilled RNPL balance (D056) and the single-fee share of GBV, not listings. Those two numbers close section 2.2 exactly.
2. Re-run the solve on the 3Q26 10-Q the evening of 5 November; the change in u against the change in the disclosed RNPL share is the first public read on whether unpaid bookings are surviving to payment.
3. Replace the unearned-fees row in `D1_prereg_thresholds.csv` with the funds-payable rule in 2.3 before the card is frozen.
4. Add the 10-Q "higher cancellation rates" and "less correlated" sentences to `rnpl_statement_ledger.csv` as official rows, and flag the kernel note that lambda stability is now contradicted by the issuer.
