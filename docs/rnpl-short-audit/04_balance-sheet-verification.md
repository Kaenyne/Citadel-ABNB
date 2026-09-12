# 04 — Adversarial verification of the RNPL balance-sheet note

- **Date:** 2026-09-11. **Author:** Opus verification agent for Theo.
- **Under test:** `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`, script `analysis/src/rnpl_balance_sheet_bridge.py`, output `data/processed/rnpl_balance_sheet/rnpl_balance_sheet_bridge_output.txt`.
- **This audit:** `analysis/src/rnpl_short_audit/verify_balance_sheet.py`; printed output and six CSVs under `data/processed/rnpl_short_audit/verify_balance_sheet_output.txt`, `verify_bs_*.csv`.
- **Nothing under test was edited.** Read-only on every existing file.

## 1. Verdict table

| Claim | Verdict | One line |
|---|---|---|
| **C1** 10-Q carries the "higher cancellation rates" / "less correlated" language, absent from the 60-row ledger | **CONFIRMED** | Both sentences verbatim in the 10-Q MD&A; ledger contains neither (0 hits on "less correlated"; the one "higher cancellation" hit is a `note` field on D006, not a quote). D057–D059 are indeed its only 10-Q rows. |
| **C2** UF/FP diverge from 4Q25 **because of the single-fee migration** | **REFUTED on mechanism and on the headline quarter** | The 10-K puts *both* fees in unearned fees and routes the guest payment to funds payable **net of service fees**, so the migration moves UF/FP the *opposite* way (+3–4%). The 4Q25 "FP beats GBV" cell is 15pts of FX translation on a base that FX had already depressed. Arithmetic of table 2.1 reproduces exactly; the attribution does not. |
| **C3** Two-equation solve; u = 6.4%/7.5% at B=1.00, 15–16% at B=1.10; m = 8.0–8.5%; 7–19mm unpaid nights | **REFUTED (m) / MODIFIED (u, materially larger)** | m is not identified — it returns **−1.4% for 3Q25**, before the migration existed, and is mathematically invariant to B. On the FX-clean line alone u = **13.9%/15.4%** at B=1.00 and 21.7%/23.1% at B=1.10, i.e. **17–28mm** unpaid nights at 30 June on the note's own 1.33x ADR (13.6–37.3mm across the full divisor/ADR stress). A divisor error (0.124 instead of the ~0.133–0.155 total fee) also inflates the backlog 7–25%. |
| **C4** Score funds payable, not unearned fees; rule "FP y/y +5% to +11%" | **REFUTED** | Funds payable carries an **±8.7pt** FX swing per year; unearned fees reconciles to the cash-flow statement within **$3–8mm**. The proposed window is about one FX move wide. Krish's −3% unearned-fees row is **not** trippable by migration and survives, with one conditioning fix. |
| **C5** Marginal ADR = 4/3 = 1.33x; 1.5x from 4Q25 | **MODIFIED** | 4/3 is right *relative to the prior-year ADR* (1.22x vs the 1Q26 ADR), and is an **upper bound**, not a point. The 4Q25 "1.5x" is an upper bound only — the source denominator is ">200bp". The bundle/RNPL-only label is mixed. |

## 2. Evidence

### C1 — CONFIRMED

Verbatim byte-match against `data/raw/regulatory/quantification/abnb_2026q2_10q.html`, Part I Item 2 MD&A, "Key Business Metrics and Non-GAAP Financial Measures — Gross Booking Value":

> "Our flexible payment options allow guests to defer a portion or all of their payment from the time of booking to a date closer to stay. In 2025, we launched RNPL and expanded it internationally in 2026. To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking. As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated."

`data/processed/overnight2/D/rnpl_statement_ledger.csv` has 60 rows; "less correlated" returns zero hits, "higher cancellation" one hit in D006's `note` field only. D057/D058/D059 are the only rows citing the 2Q26 10-Q. **The note is right, and the gap is worth closing.**

### C2 — the decisive filing language

The note's mechanism is: "The migration to a 15.5% host-only fee removes the separate guest fee from unearned fees and puts the guest's whole payment into funds payable." The FY2025 10-K says the opposite on both halves.

> **`abnb_2025_10k.json` p.63, Note 2, "Funds Receivable and Funds Payable":** "The Company records guest payments, **net of service fees**, as funds receivable and amounts held on behalf of customers with a corresponding amount in funds payable and amounts payable to customers when cash is received in advance of check-in. **Host and guest fees are recorded as cash with a corresponding amount in unearned fees.**"

> **p.62, Note 2, "Revenue Recognition":** "**For all bookings**, the guest pays the booking amount to the Company, which disburses the booking amount to the host after check-in, **net of the host's service fees**." — the paragraph that immediately precedes: "In October 2025, the Company began transitioning to a single-fee structure, charging only the host a service fee."

> **p.45, Item 7:** "We record the service fees that we collect from customers prior to check-in on our balance sheet as unearned fees."

So the host fee is **collected at booking and sits in unearned fees**, exactly as the guest fee did; funds payable never held the guest fee under either structure. Holding the host's net take constant, the migration moves UF/FP from ~0.177 to ~0.183 — **up 3–4%, at every parameterisation tested (host fee 2.5–3.5%, guest fee 10.0–14.2%)**. Observed UF/FP is **down 8.1% (4Q25), 12.7% (1Q26), 10.3% (2Q26)**. Wrong sign, wrong magnitude.

Two corroborations: (i) the 2Q26 10-Q **never mentions the fee structure** — no "single fee", no "15.5%" — and attributes the UF shortfall to "the increased guest adoption of our **flexible payment options**"; (ii) the 1Q26 and 2Q26 letters (ledger D037, D051) say "**Absent the impact of Reserve Now, Pay Later** bookings … we expect that unearned fees would have grown year-over-year"; (iii) `research/notes/host_only_fee_history_and_elasticity.md:54` has the migration **accretive** to take rate (14.9% → 15.5%), which raises fees in UF rather than removing them.

### C2 — the 4Q25 divergence, alternatives sized

Recomputed y/y table matches the note to 0.1pt on every cell (`verify_bs_yoy_gap_table.csv`). The attribution does not survive.

**Reconciliation** (balance-sheet move minus cash-flow-statement move = translation), all from the filings:

| Line / period | Δ balance | Cash-flow stmt | Residual | Memo: disclosed FX-on-cash |
|---|---:|---:|---:|---:|
| Funds payable FY2025 | +1,028 | +401 | **+627** | +655 |
| Funds payable FY2024 | +62 | +320 | **−258** | −237 |
| Funds payable 1H2025 | +5,136 | +4,510 | **+626** | +689 |
| Funds payable 1H2026 | +5,265 | +5,426 | **−161** | −146 |
| **Unearned fees FY2025** | +127 | +122 | **+5** | — |
| **Unearned fees 1H2025** | +1,241 | +1,236 | **+5** | — |
| **Unearned fees 1H2026** | +1,088 | +1,085 | **+3** | — |

The 10-K: "The effect of exchange rate changes … relates to certain assets, **principally cash balances held on behalf of customers** … In 2025, we recorded an increase of $655 million … due to the weakening of the U.S. dollar." **Note the task brief's premise is a transcription error: the +$689M is the six months ended 30 June 2025 column; 1H26 was −$146M**, "primarily due to the **strengthening** of the U.S. dollar".

Consequence for 4Q25: reported FP +17.33%; ex the FY25 translation **+6.76%**; ex FY24 translation in the base too **+2.31%** — against GBV +15.91%. **Funds payable lagged GBV by 9 to 14pts in 4Q25, worse than unearned fees' −8.1pt gap.** The sign pattern the note calls diagnostic does not exist. Two-year stacks say the same: 4Q25 FP CAGR 8.89% vs GBV 14.72%.

For 2Q26 the FX residual over Jul-25 to Jun-26 is only **−$160M**, so ex-FX FP is **+11.9%** — the UF/FP split *widens* to 12.8pts. FX does not explain 1H26.

**Alternatives, with verdicts** (`verify_bs_alternatives.csv`):

| Alternative | Size | Survives? |
|---|---|---|
| FX translation of non-USD funds payable | swing $885mm = **14.9pts** of the +17.3% | **Yes — larger than the whole divergence** |
| Depressed 4Q24 base (4Q24 FP +1.06% vs GBV +13.55%) | 5.8pt two-year lag | **Yes (same root cause)** |
| Pay Less Upfront mix | 10-K pp.63-64: full fee to UF on the **first instalment**, partial payment to FP. Explains the 0.23–0.30 UF/FP level (vs 0.15–0.18 theoretical) *and* its 1H26 fall as RNPL cannibalises PLU | **Yes — and it is an RNPL story, not a fee story** |
| Host payout timing after check-in | undisclosed | **Yes, as an unquantifiable residual** |
| Single-fee migration | wrong sign, ~10x too small | **No** |
| Lead-time lengthening | scales both stocks by B; cancels from the ratio | No (rescales level only) |
| Lodging/occupancy taxes | grows with GBV; no coverage change disclosed | No |
| Strict→Firm cancellation migration (2Q26 letter, D048) | reverses out of both lines symmetrically | No |
| Experiences/Services seats | "Substantially all of the bookings … have come from nights" | No |
| Hedge cash | 10-K: 10% adverse move on net monetary assets = **$38mm** | No |
| Funds receivable vs funds payable | identical on the 10-Q balance sheet ($6,959 / $12,224) | No |

### C3 — the solve

Replication is exact (m 2.38/8.02/8.47%, u 3.19/6.40/7.55% at B=1.00). Three failures:

1. **3Q25 falsification.** The same solve returns **m = −1.4% for 3Q25**, three months before the migration began. The note's table 2.2 omits that row; the script's own output carries it.
2. **m is invariant to B** — both ratios divide by the same B, so B cancels out of the ratio. m is a pure restatement of the (FX-contaminated) UF/FP ratio.
3. **Divisor.** `rnpl_balance_sheet_bridge.py:41` grosses the UF norm back to GBV with `G_SPLIT = 0.124`, the *guest-fee* share. UF holds both fees (~15.1% split / 15.5% single; 13.3% realised take rate). The backlog is overstated 7–25%.

**Stress (8 norm constructions × guest-fee coef 0.10/0.124/0.142 × B 1.00/1.05/1.10):** m ranges 1.1–2.5% (4Q25), 6.4–8.4% (1Q26), 8.1–9.6% (2Q26) — tight, because it is just the ratio. u ranges −0.7% to 13.6% (4Q25), 3.1–16.4% (1Q26), 5.0–16.7% (2Q26). Norm window moves u more than the denominator choice does.

**The identified alternative** — solve u from unearned fees alone, which the reconciliation above shows is FX-clean and which the 10-K shows is migration-neutral:

| B | 1Q26 u | 2Q26 u |
|---|---|---|
| 1.00 | 10.7 – 13.9% (median 13.0) | 14.0 – 16.8% (median 15.1) |
| 1.05 | 14.9 – 18.0% | 18.1 – 20.8% |
| 1.10 | 18.8 – 21.8% | 21.8 – 24.4% |

At divisors 0.124–0.155 and ADR ratios 1.00–1.33x this is **$3.3–6.9bn of unpaid GBV at 30 June and 13.6–37.3mm unpaid nights** (17.0–28.0mm holding the note's 1.33x ADR and 0.124 divisor fixed), against the note's 7–19mm and the 40mm illustrative row in `outputs/rnpl-audit-20260910/materiality.md`.

**Longer-dated book vs pre-payment cancellations.** The note poses a shortfall (6–7% stock vs 20–21% flow) that mostly *is not there* once the spurious migration term is removed: 14–15% at B=1.00 and 22–23% at B=1.10 brackets the disclosed flow share. B of 1.04–1.06 closes the remainder, and management has said lead times lengthened in all regions (1Q26 letter, D039). So the data favour **the longer-dated book**, and do **not require** pre-payment cancellations — though the balance sheet remains structurally blind to them, and the 10-Q asserts they are higher.

**Third constraints.** The cash-flow "Unearned fees" line is the *same* information as the balance (residual $3–8mm) — no new constraint. Funds receivable equals funds payable exactly — none. The FX-on-cash line *is* a real constraint, and is what this audit uses. The hedge notional on "unbilled amounts for confirmed bookings under the terms of our payment programs (Pay Less Upfront and Reserve Now, Pay Later)" (10-K p.50) would identify the unpaid book directly, but only the $38mm sensitivity is disclosed. **No public constraint separates u from B; u stays a range.** The note's item 5.1 IR ask is right.

### C4 — the 3Q26 table and the rule

The note's pre-RNPL 3Q26 expectation reproduces exactly ($2,105mm UF / +15.6%; $8,468mm FP / +17.5%). Under 10-K accounting (m = 0):

| u | UF ($mm) | UF y/y | FP ex-FX y/y |
|---:|---:|---:|---:|
| 5% | 1,999 | +9.9% | +11.6% |
| 10% | 1,894 | +4.1% | +5.7% |
| 15% | 1,789 | −1.7% | −0.2% |
| 20% | 1,684 | −7.5% | −6.0% |

**Krish's −3% row is not trippable by migration.** With m = 0 the line reaches −3% only at u ≈ 16% and the note's −17% tail only at u ≈ 28%. The note's paragraph 2 rests entirely on the (1−m) term the 10-K removes.

**Funds payable is the noisier gauge, not the cleaner one.** Both lines move ~1.16pts of y/y per 1pt of u; only funds payable *also* carries an ±8.7pt annual FX swing (FY25 +$627mm on a $7.2bn 3Q25 base), plus taxes, payout cadence and the PLU mix. The proposed "+5% to +11%" window is about one FX move wide and cannot discriminate.

**Corrected 5 November rule** — score the FX-clean line, conditional on the realised GBV print:

> **Primary: (3Q26 unearned fees y/y) − (3Q26 GBV y/y).**
> - at or below **−18pts** → unpaid book at or above the 1H26 run-rate; drag on
> - **−12 to −18pts** → in line with 1H26; thesis intact, no escalation
> - wider than **−8pts** → deferral is not deepening; drag hypothesis weakened
>
> **Cross-check (not a trigger):** reconcile the unearned-fees balance move to the cash-flow statement's "Unearned fees" line; they have agreed within $8mm for six quarters, so a divergence is an accounting change, not RNPL.
> **Funds payable:** scoreable only after subtracting (Δ balance − financing-activities "Change in funds payable"), which is the translation effect. Un-adjusted funds-payable y/y is not a scoreable line.

At the guided mid-teens GBV, the −18pt gap maps to **−3% on unearned fees (~$1,765mm)** — i.e. Krish's existing number. **Do not replace D1's unearned-fees row; condition it on the GBV print** so a GBV miss cannot be scored as a deferral signal.

### C5 — the 4/3 ratio

If RNPL adds *a* pts to GBV growth and *b* pts to nights growth, then ΔGBV/ΔNights = (a/b) × ADR_{t−1}. So 4/3 is marginal ADR against the **prior-year** ADR; against the 1Q26 ADR it is **1.22x**. The note applies 1.33x to the quarter's own ADR when converting unpaid GBV to nights, which understates unpaid nights ~8%.

The 4Q25 "1.5x" comes from "~300bp GBV on **>200bp** nights". A lower-bounded denominator gives an **upper-bounded** ratio: at 250bp it is 1.20x, at 290bp 1.03x. Quoting 1.5x as a derived parameter is not supported.

Interpretation: the ratio equals marginal ADR only if the attributed GBV points are pure incremental volume. The 10-Q says "The increase in ADR was driven in part by the continued adoption of RNPL" — re-mix on bookings that would have happened anyway lands in the GBV numerator with no nights in the denominator. **4/3 is an upper bound.** Separately, `docs/RNPL_HANDOFF.md:41` records that the 1Q26 "3pts nights / 4pts GBV" was attributed to **RNPL, cancellation-policy changes and simplified fees combined**; note paragraph 7 then applies the resulting 1.33x to the **RNPL-only** 21% GBV share. Finally, 0.21/1.333 = 15.8% if 1.33x is against the overall average and 16.7% only if against the non-RNPL average; the note does not say which.

## 3. Method

All panel figures from `data/processed/overnight/02_kpi_panel_quarterly.csv`. All filing constants transcribed into `FILING_FACTS` in the audit script with their location, and the 10-Q sentences byte-matched against the stripped HTML at run time. Norms rebuilt independently in eight variants (denominator: next-quarter revenue / same-quarter GBV / trailing-4 revenue; window: 2022–24, 2023–24, ±1H25). FX decomposition is the identity `Δ balance − cash-flow-statement change = translation + other`, applied to both lines over FY2024, FY2025, 1H2025 and 1H2026, cross-checked against the disclosed FX-on-cash line.

## 4. Limits

- The 1Q26 funds-payable FX residual cannot be isolated: only half-year and full-year cash-flow periods are published, so 4Q25 and 2Q26 are exact and 1Q26 is bracketed.
- The Pay Less Upfront reading of the UF/FP level and its 1H26 decline is consistent with the 10-K accounting but **is not separately disclosed** and cannot be distinguished from a change in host payout cadence. It is a hypothesis with the right sign, not a measurement.
- `data/raw/letters/` does not exist on this checkout (gitignored); letter language was taken from the verbatim `quote` fields of `rnpl_statement_ledger.csv`, not from the letters themselves.
- Jessie's section 3b exists only on `origin/jessie/backlog-conversion`, not on disk.
- u remains a range. Nothing public separates it from B; the unbilled-bookings balance behind the 10-K hedge line would close it.

## 5. What should change in the note

1. Strike the migration attribution in paragraph 2 and table 2.2's `m` column; replace with the FX decomposition. The fee migration is UF-*accretive*, not UF-dilutive.
2. Reinstate the 3Q25 row of the solve, which falsifies `m`.
3. Withdraw item 5.3 ("replace the unearned-fees row with the funds-payable rule"). Condition the existing row on GBV instead.
4. Withdraw the statement that Jessie's +4pt break is "RNPL plus migration" — the ratio uses only unearned fees and revenue, both clean.
5. Keep paragraph 1, and keep item 5.1 (the IR ask for the unbilled balance), which this audit reinforces.
6. Re-state the 30 June unpaid-nights range as **17–28mm** on its own parameters (13.6–37.3mm stressed), not 7–19mm, and note that this makes the "implausible 7 to 17 point revision" argument weaker, not stronger.
