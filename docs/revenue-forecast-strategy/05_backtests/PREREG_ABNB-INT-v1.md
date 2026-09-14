# PREREG ABNB-INT-v1 — the integrated 3Q26 / 4Q26 pre-registration card

> # FROZEN when the team signs — do not edit after signature; scored 6 Nov 2026
>
> `spec_id` **ABNB-INT-v1**. Print date **5 Nov 2026** (confirmed independently by Zacks,
> Yahoo and S&P). Scoring date **6 Nov 2026**. Machine-readable twin:
> `data/processed/forecast_methods/prereg/ABNB-INT-v1_card.csv`.
>
> **This card sits BESIDE `ABNB-WS20-v1`, it does not replace it.**
> `data/processed/overnight/20_frozen_q3_2026.csv` and
> `research/notes/overnight/20_temporal-validation.md` stay untouched and are scored on
> their own terms. WS20 is a *surprise-vs-Street* card on two targets; INT-v1 is a *level
> and disclosure* card on twenty-one items plus three branch rules. Both are scored on
> 6 Nov; neither is edited to agree with the other.
>
> Signature block is §7. **Until every `decision_required = TRUE` row in §5 is resolved and
> the block is signed, this is a draft and nothing in it may be quoted as pre-registered.**
> After signature: no value, band, rule or baseline is revised, and no item is added or
> removed, whatever prints on 5 November.

Compiled 11 Sep 2026 from four number sets that all exist in the tree today. `harness/score.py`
was **not** run. No existing file was modified.

---

## 0. The four sources, and why there are four

| # | source | spec / package | what it is | files |
|---|---|---|---|---|
| **1** | **Frozen WS20 card** | `ABNB-WS20-v1`, frozen 2026-09-06 | A *surprise-vs-Street* card. 18 rows, 8 features fitted on labels through 2026Q2. **Nothing beat its baselines in both windows**, so the designated forecast is the surviving baseline (trailing-4 mean). | `data/processed/overnight/20_frozen_q3_2026.csv`, `research/notes/overnight/20_temporal-validation.md` |
| **2** | **v2 live block** | `live-block-v2`, `guidance-policy-v2`, `fx-lag-v2`, 2026-09-11 | The programme's own reconciled block. GBV = nights × ADR and take rate = revenue ÷ same-quarter GBV imposed inside 500,000 joint draws; one GBV now used by B1 and B2. | `05_backtests/B1`–`B4`, `data/processed/forecast_methods/live_block_v2/`, `registry/live-block-v2__*.csv`, `guidance-policy-v2__*.csv`, `fx-lag-v2__*.csv` |
| **3** | **Krish's parallel runs** (PRs #39–#44) | q3nowcast (E/F/G/H), adrq3 (I/J) "card v2", overnight2 (A–D) | The only *team-built alternative data* that beats a naive forecast out of sample (reviews stays index), plus a rebuilt ADR card and an RNPL statement ledger with a 7-row 5 Nov score sheet. | `docs/q3nowcast/`, `docs/adrq3/`, `docs/overnight2/`, `research/notes/{q3nowcast,adrq3,overnight2}/`, `data/processed/overnight2/D/D1_prereg_thresholds.csv` |
| **4** | **Theo's RNPL balance-sheet note** | 2026-09-11 | Re-bases nights off the RNPL/fee-migration bundle and replaces the confounded unearned-fees threshold with funds payable. | `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`, `analysis/src/rnpl_balance_sheet_bridge.py`, `data/processed/nights_baseline_reconciliation.csv` |
| — | **Consensus vintages** | `L0` register, A1 | The bars every "beat / below" rule is scored against. | `data/processed/forecast_methods/L0/L0_vintage_register.csv`, `05_backtests/A1_consensus_vintages.md` |

3Q25 comparison base, used for every y/y in this card:
**nights 133.6 M · ADR $171.29 · GBV $22,900 M · revenue $4,095 M · printed take rate 17.882 %.**
4Q25 base: **ADR $167.51 · revenue $2,778 M.**

---

## 1. Reconciliation table — 3Q26, one column per source

### 1.1 The block

| | **(1) Frozen WS20** | **(2) v2 live block** | **(3) Krish: Q3 nowcast + ADR card v2** | **(4) Theo re-based bridge** |
|---|---|---|---|---|
| **Nights, level** | 147.2 M | **147.376 M** | **146.3 M** at +9.5 %; team baseline 146.8 M | **146.0 M** (band 145.3–146.7) |
| **Nights, y/y** | **+10.2 %** | **+10.31 %** | **+9.5 %** (band 8.5–11.0); headline row +10.0 (8.6–11.5); team baseline +9.9 (8.5–10.3) | **+9.27 %** (band 8.76–9.78) |
| **ADR, level** | $177.80 | **$180.15** | **$176.47** (band $174.20–178.75) | — (bridge is nights-only) |
| **ADR, y/y** | **+3.8 %** | **+5.17 %** *(identity output)* | **+3.03 %** (band +1.70 to +4.35) | — |
| **ADR, ex-FX** | not decomposed | not decomposed | **+3.46 %** (central 2.13–4.78); FX −0.43 pp midpoint (EUR fit −1.12 / baskets +0.26) | — |
| **GBV** | **$26,185 M** (+14.34 %) | **$26,549.8 M** (+15.94 %); q10/q90 25,456 / 27,643 | **$25,906 M** (+13.1 %) = 146.8 × $176.47 | $25,765 M (+12.5 %) if paired with ADR card v2 |
| **Revenue** | **$4,801 M** (+17.24 %); WS20's own designated implied print **$4,805 M** | **$4,816.1 M** (+17.61 %), sd 48.0 | **"about $4.80 bn"** in the synthesis — **unsourced**; the underlying note (J §2.6) prints **$4,632 M** (+13.1 %) at an *assumed flat* 17.88 % take rate | not an object |
| **Printed take rate** | 18.335 % *(implied, not an object)* | **18.140 %**, sd 0.4628, **P(≥18.10) = 0.534** | 18.53 % on $4,800 M / **17.88 % on $4,632 M** — *assumed, not forecast* | 18.63 % if paired with $4,800 M |
| **Revenue FX, pp** | not an object (guide embeds ~+3.0) | free fit **+1.3** stated (+1.2 gross, the registered row); **Φ × 0.851 = +2.9** (adopted for "what management states") | **+2.19 gross / +1.98 after hedge**, WS05 vintage **28 Aug** | not an object |
| **Internal identity** | nights × ADR = 26,177 vs 26,185 stated → **−0.03 %** (rounding) | **0.00000 %** by construction | 0.00 % by construction (GBV is derived) | n/a |

### 1.2 Method in one line, and backtest standing

| source | method, one line | backtest standing — beats naive? on which windows? |
|---|---|---|
| **(1) Frozen WS20** | Surprise-vs-Street regressions on 8 point-in-time features, fitted on labels through 2026Q2; the *designated* forecast is the **trailing-4 mean** baseline because nothing beat it. | **NO.** "Zero of the 18 primary rows beat their baselines; all executable ratios are 1.03–1.23." 54 summary rows, **0 of 18 primary (executable)** survive. The card's own honesty: the baseline *is* the forecast. |
| **(2) v2 live block** | Optimal-mix combined revenue (`bma_logscore`, pool `all`) + GBV (`stack_shrunk`) + nights (`top3_inv_mse`), then **ABNB's own identities imposed** inside 500,000 joint draws (ρ(rev,GBV) = 0.7595, W1/PIT, n = 14, seed 20260911). | **MIXED, and the volume legs LOSE.** Revenue: the carrier is `guide_cushion`, the **scoreboard winner on both windows** (RMSE ratio **0.377 W1 / 0.319 W2**), and $4,816.1 = $4,730 × 1.0182 — one estimator, not fourteen. GBV: `mix_gbv_musd` **loses** to a seasonal naive on both windows (**1.312 / 1.021**). Nights: `mix_nights_m` **loses** on both (**1.549 / 1.105**). ADR and take rate have **no registered baseline at all** (ratio NaN; `survives_both_windows = False` is vacuous, not a defeat). Walk-forward bias is up: revenue +0.80 % (t 2.14), GBV +1.77 %, nights +2.17 % (t 2.25). |
| **(3) Krish — reviews stays index (nights)** | Review-date counts per market per dump vintage, survivorship-corrected by vintage matching (n₂₀₂₆[m] / n₂₀₂₅[m−12]), windows closed 14 days before each dump, day-matched to 364 days earlier; mapped through OLS of nights y/y on the index, 2023Q1–2026Q2, slope 0.32. | **YES — the only team-built series that does.** Walk-forward **RMSE 1.48 pp vs naive 2.16 → ratio 0.68**, n = 10 scored quarters, from 2024Q1, expanding. Family 0.65–0.75 across 2,560 cells (**463 beat naive**); best cell 0.60; jackknife **0.63–0.86**; permutation p 0.001. Eurostat monthly cross-check **0.59** (36 of 37 country tests beat naive). Lag-1 (fully knowable) only marginal, 0.87–0.91; first differences never (1.47). |
| **(3) Krish — corroborating externals** | Expanding-window walk-forward of 36 external features on nights y/y, 288 tests. | **PARTIAL.** Hotel RevPAR `hlt_revpar_full` **0.665**, `mar_revpar_full` 0.691; **NTTO I-94 inbound arrivals a NEW survivor: 0.720 (full) / 0.724 (QTD-1m, observable today)**, 9 of 24 tests beat naive and 5 by ≥20 % — the highest "beat by 20 %+" count of any family. CPI lodging 0.716. **TSA fails (0.924).** Calendar booking pace (F) **fails with an inverted sign** (r −0.43 on n = 5) and is retired. G's own caveat: 6 of 14 families beat naive on the 14-observation window and **0 on the 18-observation window** — "the signature of a common deceleration rather than of prediction." |
| **(3) Krish — ADR card v2** | Additive identity: reported = FX + ex-FX; ex-FX = geo mix + unit size + LOS + new business + interaction + **pricing residual**, with the three mix terms now *measured* from the reviews panel and the residual set by a persistence rule. | **NO — the pre-registered test was NOT passed.** Threshold: RMSE ratio vs naive "ex-FX same as last disclosed quarter" **strictly below 1.0**. Result **0.994** (0.903 vs 0.908) on 1Q24–2Q26 n = 10, **1.042** on 2Q24–2Q26 n = 9, jackknife **0.87–1.05** with only 5 of 10 below 1. **A tie is not a pass.** It does beat AR(1) (0.79) and the old H component build (0.70; H itself is **1.58**, RMSE 1.292 vs naive 0.816). The failing term is the residual rule: the model is biased low **0.8–1.7 pp in every acceleration quarter**. ⚠ `I_adr-mix-terms-3q26.md` L17/L105 label the same 0.994 "PASS"; J §1.5 and the synthesis label it FAIL. **The FAIL reading is the one this card adopts.** |
| **(4) Theo re-based bridge** | Four additive growth-point terms on the fixed 3Q25 denominator of 133.6 M, starting from PR #32's +9.89 %: cancellation tail from Krish's D1 cohort engine central cell (**−0.62**), pull-forward reversal of the 3Q25 US launch quarter (**−0.20**), July 2026 eligibility expansion (**+0.20**), ex-NA lap (**0 in 3Q26**, **−0.79 in 4Q26**). 9.89 − 0.62 − 0.20 + 0.20 = **9.27**. Separately, a joint solve for the unpaid RNPL share `u` and the single-fee migration share `m` on unearned fees *and* funds payable. | **NO STANDING — it is not registered and nothing on nights is.** `SCOREBOARD.md` `nights_m` carries **only the four `baselines` objects**; `survives both = no` on every row; **no team method is entered at all**. `nights_yoy` has **no `baselines__naive` row**, so the tracker's 1.750 / 2.216 are against a locally built denominator and are **not harness ratios**. The bridge's contribution is **identification** — it separates the migration leg from the RNPL leg — not a predictive score. What it has instead is **convergence**: the independent unified module gives 3Q26 +9.49 % / 146.3 M and 4Q26 **+7.61 %** against the bridge's +9.27 % and **+7.64 %** (0.03 pp apart from a different construction). ⚠ The pull-forward term implies **14 % to 43 %** (up to 80–87 % at the top of its own range) of PR #32's fitted +2.40 NA RNPL level was pull-forward — **a large implicit claim never stated as one**. |

### 1.3 The take-rate hinge, priced at every source's GBV

The printed take rate is a **near-linear function of GBV** and almost all of its uncertainty is
GBV uncertainty (sd(revenue)/revenue = 1.00 % against sd(GBV)/GBV = 3.21 %). Probabilities below
use the **B1 distribution**: take-rate sd = 0.4628 pp × (26,549.8 ÷ GBV), P = Φ((τ − 18.10)/sd).
This analytic form reproduces B1's own 500,000-draw sensitivity grid to ≤ 0.001
(25,900 → 0.852 vs B1's 0.853; 26,185 → 0.734 vs 0.735; 26,300 → 0.675 vs 0.676; 26,549.8 → 0.534;
27,000 → 0.282 vs 0.281).

| view | GBV, $M | revenue, $M | **take rate** | sd, pp | **P(≥ 18.10 %)** |
|---|---|---|---|---|---|
| (1) Frozen WS20 card | 26,185.0 | 4,801.0 | **18.335 %** | 0.469 | **0.69** |
| (1) Frozen card GBV × registered revenue | 26,185.0 | 4,816.1 | 18.393 % | 0.469 | 0.73 |
| **(2) v2 live block — the reconciled object** | **26,549.8** | **4,816.1** | **18.140 %** | **0.463** | **0.53** |
| (2) v2 GBV × kernel revenue $4,804 M | 26,549.8 | 4,804.0 | 18.094 % | 0.463 | **0.49** |
| (3) Krish GBV × the synthesis's "$4.80 bn" | 25,905.8 | 4,800.0 | 18.529 % | 0.474 | **0.82** |
| (3) Krish GBV × the **note's own** $4,632 M | 25,905.8 | 4,632.0 | 17.880 % | 0.474 | **0.32** |
| (3) Krish GBV × registered revenue | 25,905.8 | 4,816.1 | 18.591 % | 0.474 | 0.85 |
| (4) Theo 146.0 M × ADR card v2 × registered revenue | 25,764.6 | 4,816.1 | 18.693 % | 0.477 | **0.89** |
| (4) Theo 146.0 M × ADR card v2 × kernel revenue | 25,764.6 | 4,804.0 | 18.646 % | 0.477 | 0.87 |
| **REC** reviews index +9.5 % × ADR card v2 × registered revenue | 25,816.1 | 4,816.1 | 18.655 % | 0.476 | 0.88 |

**Four readings of the same quarter put the hinge anywhere from 0.32 to 0.89.** Three things
follow, and all three belong in the memo:

1. **The sources that are most bearish on volume are mechanically the most bullish on the take
   rate.** Revenue is set by the guide plus a cushion — an object that does not see nights or ADR
   at all — so cutting GBV raises the ratio. A team that presents "nights decelerate to +9.3 %"
   and "the take rate clears 18.10 %" as two independent bullish/bearish findings is presenting
   one arithmetic fact twice.
2. **The 0.32 row is not a forecast and must not be scored.** Krish's $4,632 M is
   GBV × an *assumed flat* 17.88 % take rate. It is the identity closed with an assumption, so
   reading a take rate back out of it is circular. The unsourced "$4.80 bn" in the same synthesis
   is the row that should be retired, not promoted (see §5, D-06).
3. **The revenue-object choice alone straddles the line.** At the registered GBV, guide+cushion
   $4,816.1 M gives 18.140 % and P = **0.53**; the kernel's $4,804.0 M gives 18.094 % and
   P = **0.49**. B1 says it out loud: *"the pre-registered test is decided at the 5 bp level by
   which revenue object you use."* That is why §5 D-01 is a decision, not a default.

Break-evens, stated once: at the registered revenue the **flip GBV is $26,608.3 M**, 0.22 % above
the registered point. At the registered GBV the test needs a revenue print of **≥ $4,805.5 M —
above the top of management's own 3Q26 guide range of $4,770 M** — and it clears only because the
trailing-8 cushion (+1.86 %) is larger than the gap.

### 1.4 Cells that are empty on purpose, and one that is not

| cell | status |
|---|---|
| (1) Frozen WS20 — revenue FX, ADR ex-FX | **not an object in WS20.** Correctly empty, not pending. |
| (4) Theo bridge — ADR, revenue, GBV | **not objects.** The bridge is a nights construction; every GBV/take-rate figure shown for it in §1.1 and §1.3 is *this card* pairing its nights with another source's ADR and revenue, and is labelled so. |
| (4) Theo bridge — harness ratio vs naive | **structurally absent, and that is the finding.** No nights object in this repository is registered in the harness, and none beats naive — except Krish's reviews index, which by construction **cannot see the booking-date cancellation tail the bridge is built around.** The two most load-bearing volume numbers on this card therefore have **no common scoreboard**. |
| **`D1_prereg_thresholds.csv` row 3** | ⚠ **STILL THE OLD RULE.** Three documents ask for the unearned-fees row to be swapped for funds payable "before the card is frozen"; **none has done it.** INT-11/INT-12 below are that swap. The CSV is left untouched (this card creates only new files); the swap is recorded here and in `ABNB-INT-v1_card.csv`. |

### 1.5 The finding this card exists to surface: **you cannot take the backtest winner object by object**

Pick the best-scoring object for each line — reviews index for nights, ADR card v2 for ADR, the
registered GBV for GBV — and **the block does not satisfy Airbnb's own definition of ADR.**

```
reviews index  +9.5 %  ->  146.292 M nights
ADR card v2            ->  $176.47
                          146.292 x 176.47      =  $25,816 M   (+12.73 % y/y)
registered GBV                                  =  $26,549.8 M (+15.94 % y/y)
                          (1+n_yoy)(1+adr_yoy)-1 = +12.81 %  against a stated +15.94 %

                                    identity break = -3.13 pp
```

*(+12.73 % and +12.81 % differ by 0.08 pp only because the letter rounds 3Q25 GBV to $22.9 bn
while 133.6 × $171.29 = $22,884 M. B1 measures the same rounding at ≤0.27 % across 2023Q1–2026Q2.
The −3.13 pp break is 40× that, and is not rounding.)*

**That is 14× the 0.22 pp break B1 was written to close, and it is the F3 defect re-created by a
different route.** The three consistent alternatives, stated so the team picks one *knowingly*:

| block | nights | ADR | GBV | take rate @ $4,816.1 M | **P(≥18.10)** | what each leg's backtest says |
|---|---|---|---|---|---|---|
| **(i) backtest-winner block** | **146.3 M (+9.5 %)** | **$176.47 (+3.03 %)** | **$25,816 M (+12.7 %)** | **18.655 %** | **0.88** | nights **0.68 vs naive**; ADR **0.994 — a tie**; GBV is a *derived* identity with no object behind it, and **+12.7 % sits below management's own "mid teens" guide** |
| **(ii) registered block** | 147.38 M (+10.31 %) | $180.15 (+5.17 %) | $26,549.8 M (+15.94 %) | **18.140 %** | **0.53** | nights **loses** to seasonal naive (1.549 / 1.105); GBV **loses** (1.312 / 1.021); ADR is a **definitional residual** with no baseline. Only the revenue carrier scores (0.377 / 0.319) |
| **(iii) implied-ADR hybrid** | 146.3 M (+9.5 %) | **$181.48 (+5.95 %)** *(plug)* | $26,549.8 M | 18.140 % | 0.53 | keeps the registered GBV and the skilful nights, and charges the whole difference to ADR — i.e. it prints an ADR **2.9 pp above** the ADR card and calls it a forecast |

**This card does not silently pick.** It pre-registers block **(ii)** as the headline — because it is
the only block whose internal dependence was actually derived rather than asserted, and the only one
the programme has registered — and pre-registers block **(i)** beside it as the named alternative,
with the hinge probability stated for both. §5 D-04 is the decision; it must be taken by a person,
not by a spreadsheet.

**What the memo says out loud:** *"Our two most skilful objects and our registered GBV cannot all be
right. Nights and ADR both score against a naive; GBV does not, and GBV is 90 % of the take-rate
bet. So we pre-register the pair — the take rate **and** the GBV it is read off — and we tell you in
advance that a $734 M move in a $26 bn number, 2.8 %, moves our probability from 0.53 to 0.88."*

---

## 2. The card — twenty-one items

Bands are **80 %** unless the row says otherwise. "Baseline" is the thing the rule must beat for
the item to count as *support*; matching the baseline is a tie and scores as AMBIGUOUS.
Owners use the repo's own role codes (`07_MORNING_REPORT.md` §9) and, where a person is named in
the source, the person: **P1** core engine, **P2** data, **P3/R** FX + take rate, **P4** market
data, **W** writing/exhibits, **X** model plumbing.

### 2.1 The 3Q26 block

| id | item | pre-registered value | 80 % band | scoring rule — SUPPORT / REFUTE | baseline it must beat | read on 6 Nov from | owner | decision? |
|---|---|---|---|---|---|---|---|---|
| **INT-01** | 3Q26 revenue, $M | **4,816** | **4,755 – 4,878** | SUPPORT if the print is inside the band **and** closer to 4,816 than to the print-day consensus. REFUTE if outside the band. Absolute error scored against every baseline below. | print-day consensus (re-pulled 3–4 Nov; 11 Sep vintage: **LSEG-family $4,737.5 n=36 / Zacks $4,740 n=7 / Yahoo $4,740 n=35 / S&P $4,740 n=35**), guide midpoint $4,730, harness `naive_seasonal` | Q3 shareholder letter, income statement | **P1 / Theo** | **YES → D-01** |
| **INT-02** | 3Q26 nights and seats, y/y % | **+9.5 %** (146.3 M) | **+8.5 to +11.0** | SUPPORT if inside the band **and** the reviews-index error is below the naive error (naive = 2Q26's +10.34 %). REFUTE if outside. Separately: print ≤ +8.5 % supports the RNPL drag, ≥ +10.3 % weakens it, 8.6–10.2 inconclusive (D §5 row 1). | naive last quarter **+10.34 %**; team baseline **+9.9 %**; prior year +8.8 %; external stack +9.2 %. **There is no Street baseline: no nights, ADR or GBV consensus exists at any vendor** (the L0 register's 19 `nights` and 13 `gbv` rows are all `role=at_print` historical with `vendor_not_recorded`). The "+10.2 % consensus" in circulation is **our own frozen WS20 card**, mislabelled. Re-check 2–3 Nov; if Zacks still publishes none, this item is scored against naive only and **the memo must not say "versus consensus"**. | shareholder letter, "Nights and Seats Booked" | **Krish** | **YES → D-02** |
| **INT-03** | 3Q26 ADR, y/y % and $ | **+3.0 %, $176.47** | **$174.20 – $178.75** (+1.70 to +4.35 %) | SUPPORT if inside the band **and** the card-v2 error is below the naive error. REFUTE if outside. The card's own pre-registered test already **failed at 0.994**, so a hit is corroboration, not vindication. | naive "ex-FX same as last disclosed quarter (+4.0 %)", RMSE 0.908 pp on n = 10 | shareholder letter, ADR line | **Krish** | **YES → D-03** |
| **INT-04** | 3Q26 ADR **ex-FX**, y/y % | **+3.46 %** (score against **+3.5**) | +2.13 to +4.78 | SUPPORT if the letter's stated ex-FX ADR rounds to +3 or +4. REFUTE if ≤ +2 or ≥ +5. Record the implied residual: if ex-FX prints at the mean-reversion case the persistence rule is **retired**, not re-fitted. | persistence residual **+4.61**; mean-reversion residual **+2.40**; 1H26 actual +4.38 / +4.85 | letter's ex-FX ADR remark | **Krish** | no |
| **INT-05** | 3Q26 GBV, $M | **26,550** *(registered)* | **25,456 – 27,643** (q10–q90) | SUPPORT if inside the band. Record **both** blocks: identity-implied from the two backtest winners is **$25,816 M (+12.7 %)**, which is **below management's own "mid teens" GBV guide**. Whichever prints, write down which block was right *before* reading the take rate off it. | seasonal naive (which `mix_gbv_musd` **loses to**, 1.312 / 1.021); management's "mid teens" bucket = 14–16 % | letter, GBV line | **P1 / Theo** | **YES → D-04** |
| **INT-06** | 3Q26 **printed take rate**, % | **18.14 %**, sd 0.46 | 17.57 – 18.76 (q10–q90) | Computed as **100 × revenue ÷ same-quarter GBV**, never quoted from a model. SUPPORT for the fee thesis if ≥ **18.10 %**. The card commits to the *pair*: at the registered revenue the flip GBV is **$26,608.3 M**; at the registered GBV the flip revenue is **$4,805.5 M**. | 3Q25 printed **17.882 %**; `fee-takerate take_rate_lastyear`, which **still loses to a plain seasonal naive** (1.003 / 1.055; **0 of 8 rows beat it**) | letter: revenue ÷ GBV, same quarter | **P3/R** | **YES → D-01** |
| **INT-07** | P(take rate ≥ 18.10 %) | **0.53** | stable 0.53–0.54 under every estimable dependence assumption | Scored as a **probability**, not a call: log score and Brier against the realised 0/1, alongside the same at each rival GBV view (§1.3). The card is *right* if the realised outcome is unsurprising under 0.53, not if it "wins". | a coin (0.50); the three superseded figures 0.254 / unstated / 0.775 | derived from INT-01 and INT-05 | **P3/R** | no |
| **INT-08** | 3Q26 **stated revenue FX**, letter-rounded pp | **+3** | point +2.9; CS interval +0.3 to +3.5 | **B4's rule, verbatim:** printed **+3 or more → supports the lag-loaded Φ kernel** and closes the argument in the architect's favour; **0 or +1 → supports the free fit**, meaning the +1.2 pp the programme registered was right and management's guide was conservative; **+2 is ambiguous and is reported as ambiguous.** No row is revised after the print. | free fit (registered) **+1.3 → +1**; Φ × 0.653 **+2.2 → +2**; contemporaneous **+0.3 → 0**; overnight2 WS05 (28 Aug) **+1.98 → +2** | letter's FX remark on revenue growth | **P3/R** | **YES → D-05** |
| **INT-09** | 3Q26 **GBV growth minus nights growth**, pts | **+3.6 pts** (15.94 − 10.31 on the registered block; **+3.6** on the reviews/ADR-v2 block, 13.1 − 9.5) | 4.5 – 7.0 = inconclusive | D §5 row 2, verbatim: gap **above 7 pts with nights ≤ 9 %** supports the drag; **below 4.5 pts with nights ≥ 10 %** weakens it. | 2Q26 gap **5.4 pts**; 1Q26 **10.0**; 3Q25 **5.1**; the guide implies ~4–5 | letter, two lines | **Krish** | no |
| **INT-10** | 3Q26 reviews-index slope check | printed nights inside **8.6 – 11.5** | — | SUPPORT if the print lands inside the index's own headline band. **REFUTE if adding 3Q26 to the walk-forward pushes the ratio above 0.80** — that is the level at which the index becomes what note 08 found for every other composite. Re-run and record the new ratio the same day. | current ratio **0.68** (n = 10) | the print, fed back into `E_reviews-stays-index` | **Krish** | no |

### 2.2 Balance sheet and the RNPL drag

| id | item | pre-registered value | band | scoring rule | baseline | read on 6 Nov from | owner | decision? |
|---|---|---|---|---|---|---|---|---|
| **INT-11** | **3Q26 funds payable, y/y %** — *replaces the confounded unearned-fees threshold* | **+5 % to +11 % = deferral on schedule**; modelled central **+7.5 % to +10.6 %** | **+5.0 to +11.0** = **$7,569 M to $8,002 M** on the 3Q25 base of **$7,209 M** | **Two-sided.** SUPPORT (deferral on schedule, migration doing the work, **no cancellation signal**) if **+5 % to +11 %** *and* the unearned-fees-minus-funds-payable growth gap **widens**. **Below +3 % ($7,425 M)** → the unpaid book is larger than modelled: **more adoption, not more cancellation** — say it in exactly those words. **At or above +11 % with the gap narrowing** → deferral has already arrived and there is no unpaid hole. Score the **UF-minus-FP growth gap** as a second number, not a footnote: it *is* the migration term. | 3Q25 base **$7,209 M**. Pre-RNPL / pre-migration expectation for 3Q26: **$8,468 M, +17.5 %**. Path of the gap: through 3Q25 both lines lagged GBV by the same ~4 pts (pure RNPL); from **4Q25** they split — **FP +17.3 % vs GBV +15.9 % while UF grew +7.9 %**. Only a transfer between the lines produces that sign pattern. | 3Q26 Form 10-Q, **Part I Item 1, Condensed Consolidated Balance Sheets**, current liabilities: **"Funds payable and amounts payable to customers"** (the offsetting asset "Funds receivable and amounts held on behalf of customers" gives the same number — **only the level is informative, never the net**). Expect `abnb-20260930.htm`, CIK 0001559720, filed on or about 5–6 Nov. Unearned fees from the same statement. | **Theo** | **YES → D-10** |
| **INT-12** | 3Q26 unearned fees, y/y % — **carried as a DESCRIPTION only, not a test** | record the print | modelled range **−16.6 % to +7.5 %** on deferral alone | **NOT SCORED as evidence on cancellation. This row retires D §5 row 3.** That threshold (≤ −3 % supports the drag) **can be tripped by the fee migration alone**: the five deferral-only cells give 3Q26 unearned fees at **−2.1 / −8.4 / −16.6 / +7.5 / −1.7 %** with **zero** cancellation effect. Record the number, record the implied `u` and `m`, and read **no verdict** off the line. Its remaining use is the second leg of INT-11's migration gap. | 3Q25 base **$1,820 M**; path **+9.8 / +7.9 / +0.4 / −0.9 %** (3Q25→2Q26); pre-RNPL/pre-migration expectation **$2,105 M, +15.6 %**. Management's own dated prediction (1Q26 letter, 7 May 2026, ledger D038): RNPL "results in lower unearned fees in Q1 and Q2 and **higher** unearned fees in Q3" — the one official forward-testable statement in the record, and the reason the row is kept at all. | 10-Q, same balance sheet | **Theo** | no |
| **INT-13** | Backlog conversion — revenue ÷ (revenue + closing unearned fees), 3Q26 | record the print | 71–74 % inconclusive | D §5 row 4: **≥ 74 %** = the 2026 wedge persisting or widening in the quarter management said it would reverse; **70–71 %** = back on the pre-RNPL seasonal constant. **Inherits INT-12's confound** — a migration-driven unearned-fee fall raises this ratio with no cancellation. Flag that on the slide. | 3Q 2022–25 constant **69.2 % to 70.3 %**; 2026 ran **4.0 pts high** in both 1Q and 2Q | letter + 10-Q | **Jessie** | no |
| **INT-14** | An RNPL GBV share disclosed for 3Q26 | **no new quantified share** is the modal outcome | 21–24 % inconclusive | D §5 row 6: flat or down vs 2Q26 **while nights decelerate** supports the drag; **≥ 25 % with nights ≥ 10 %** weakens it. If no share is disclosed, score ABSENT — not SUPPORT. | 1Q26 ~20 % (official); 2Q26 ">20 %" (call mirror only) | letter, call Q&A | **Krish** | no |
| **INT-15** | Does management **restate the bundle contribution figure**? | **no quantified figure given** | — | D §5 row 7: **no figure, or a figure ≤ 1.5 points → the anniversary is arriving** (SUPPORT). **≥ 2.5 points for 3Q26 → the bundle is still adding despite the US lap** (REFUTE). A qualitative update only = inconclusive, which is what 2Q26 gave. **Never subtract management's "+3 points" as an RNPL-only lap** — it is a three-feature bundle and two of the three are still ramping. | 4Q25 call: *"over 200 basis points"* nights, *"roughly 300 basis points"* GBV. 1Q26 call: **~3 points nights, 4 points GBV**. 2Q26: **none given** | call transcript, prepared remarks | **Krish** | no |

### 2.3 The 4Q26 guide — the line the trade is actually judged on

| id | item | pre-registered value | 80 % band | scoring rule | baseline | read on 6 Nov from | owner | decision? |
|---|---|---|---|---|---|---|---|---|
| **INT-16** | **4Q26 guide midpoint, $M** | **3,161** (no fee step) / **3,179** (θ = 0.83 primitives, half step) | **3,012 – 3,312** / **3,029 – 3,330** | SUPPORT if inside the band. Total sd 3.70 % unconditional (vs 3.03 % conditional) — the honest cost of not knowing GBV_3Q26 at the pitch date. **Never conflate the guide with the print** ($3,220 / $3,238, 1.86 % higher). | `guidance-policy guide_mid_next_q` **LOSES both windows** (MAE 1.986 vs naive 1.966 W1; 1.762 vs 1.609 W2; bias +1.12 vs −0.51). **Gate G4 fails both windows on sign: 7/14 p 0.605, 4/10 p 0.828.** We have **no measured edge** on the level or the sign of the next guide midpoint — this item is scored to find out, not to claim. | letter, Q4 outlook paragraph | **P1 / Theo** | **YES → D-06** |
| **INT-17** | **P(4Q26 guide midpoint below each anchor)** | **LSEG-family $3,158 M (n = 36, 11 Sep): 0.49** no-fee / **0.43** fee-step · **S&P Global MI $3,160 M (n = 35, 10 Sep): 0.50 / 0.44** · **Zacks $3,200 M (n = 10, 11 Sep): 0.63 / 0.57** | — | Scored **per vendor**, by log score and Brier, against anchors **re-pulled and timestamped 2–3 Nov** — the 11 Sep vintages above are the pre-registration, the Nov re-pull is the scoring bar, and **both are recorded**. **Three panels, not five:** Yahoo and Alpha Vantage are one LSEG/Refinitiv-family feed (their high/low agree to the dollar; their 30-day revision counts are identical). MarketBeat/Fiscal.ai's $4,600 M is **quarantined, not a data point** (n = 2, below Airbnb's own guide floor, and the same table misprints 4Q24 actual as $1.90 B against a true $2.48 B). **Mandated presentation order, from A1: say first that consensus disagrees with itself and that the vendors are $42 M apart on Q4, then give P(below) as a RANGE (0.43–0.63), never one number.** | the whole apparent edge is the **$42 M** by which the panels disagree with each other — itself smaller than the **$126 M** by which Zacks disagrees with its own FY26 line ($14,226 M of quarters vs a $14,100 M FY26 line). And **no vendor publishes a revenue median**: Zacks' $3,200 M mean carries a $3,700 M high that is probably bad data, and **its median is nearer $3,150 M — which would put it with the other two panels and remove the trade.** | vendor terminals, timestamped, screenshotted to `data/raw/consensus/2026-11-0X/`; letter for the guide | **P4 — unassigned, propose Willem** | **YES → D-07** |
| **INT-18** | **4Q26 nights bucket word** | **"high single digit"** is the modal outcome; **P("low double digit") = 0.30–0.35** | bucket vocabulary, read off the letters: mid-single 4–6, **high-single 7–9**, **low-double 10–12**, low teens 12–14, mid teens 14–16 | SUPPORT for the bear branch if the word is **"high single digit"**; SUPPORT for the bull branch if **"low double digit"** is reiterated. D §5 row 5 on the implied rate: **≤ 7.5 % supports the drag**, **≥ 9.5 % weakens it**, 7.6–9.4 inconclusive. **Publish 0.30–0.35, not 0.55** — the declared 0.55 is above what the n − 3 delta estimator supports and is labelled judgement. | team baseline **+8.9 % (132.7 M)**; ex-NA lap adjusted **+8.0 to +8.2 % (131.7–131.9 M)**; Theo re-based **+7.64 % (131.2 M)**, and the independent unified module **+7.61 % (131.2 M)** from a different construction. Historically management guides the nights bucket **below** the last observed rate in 2 of 3 cases and the realised number lands **above** the bucket in 2 of 2. ⚠ The three lower baselines are not three independent votes — they share the ex-NA lap, which **must not also be counted in 1Q27** (D-11). | letter, Q4 outlook paragraph | **Krish** | **YES → D-08, D-11** |

### 2.4 Annual items

| id | item | pre-registered value | band | scoring rule | baseline | read on 6 Nov from | owner | decision? |
|---|---|---|---|---|---|---|---|---|
| **INT-19** | **FY26 guide action** | **RAISED**, at **P = 0.67** | — | SUPPORT if the FY26 revenue-growth guide is raised (a notch to "high teens", or replaced by a point estimate). REFUTE if merely reiterated — that would be **the first non-raise since the guide existed**, and the repo's own "what a bad Q4 guide looks like". Cut = strong refutation. | base rates from 23 FY re-statements: **Q3-print re-statements 5 raises / 0 cuts / 7 opportunities → Laplace 0.67**; FY26-revenue-line only 2/2 → Laplace **0.75**. **Publish 0.67 (larger n), record 0.75.** The "only raised, never cut" claim is **wrong** — there is one cut in the record (FY2025 new-business investment, 225M → 200M, 2Q25). | letter, FY26 outlook | **P1 / Theo** | **YES → D-09** |
| **INT-20** | **1Q27 guide (Feb 2027)** — **PLACEHOLDER, NOT SCORED 6 NOV** | midpoint **$2,930 – 2,990 M**, +9.4 % to +11.6 % y/y on 1Q26's $2,678 M | — | **Recorded now so it cannot be fitted later.** Scored at the **Feb 2027** print, on this card, unrevised. λ̂(Q1) = 12.66 % on `lagGBV(1Q27) = ⅔·GBV(4Q26) + ⅓·GBV(3Q26)`. If a first FY27 guide is given as a bucket: **"low double digits" P ≈ 0.55, "low to mid teens" P ≈ 0.25, sub-10 % P ≈ 0.20.** | 1Q26 actual +17.9 % — this would be the **first sub-teens quarterly guide since 2023** | Feb 2027 letter | **P1 / Theo** | no |
| **INT-21** | FY27 revenue — **EXPLORATORY, NOT A SCORED OBJECT** | **$15,720 – 15,838 M**, growth **+9.18 % to +11.52 %** | quote the band, never the point | **Not scored on 6 Nov and not scored at all.** Harness format v1.0 has no annual slot; at FY27 horizon both lagged GBV terms in the kernel are themselves forecasts. The "+0.09 pp edge over the Street" exists **only at kernel weight w = ⅔**; at w = 0.33 the same build is **−2.25 pp behind**. | Street FY27: **Zacks $15,740 (n=13) / Alpha Vantage $15,758 (n=44) / S&P $15,770 / Yahoo $15,790 (n=43)** | — | **P1 / Theo** | no |

---

## 3. Branch rules — pre-registered conditional statements

These are the pitch's flip rules, written as conditionals **before** the print, so the judges can
see the team would change its mind. Each resolves on 5 November from two lines of one letter.

> **B-BULL.** *If the printed 3Q26 take rate is **≥ 18.10 %** **AND** the 4Q26 nights guide word is
> **"low double digit"**, then the bull branch is live: price target **$205–215**.*
>
> **B-BEAR.** *If the 4Q26 nights guide word is **"high single digit"** **AND** the printed 3Q26
> take rate is flat — defined here as **≤ 17.88 %**, i.e. no better than 3Q25, the "fully offset"
> case at P = 0.28 — then the bear branch is live: price target **$140–152**.*
>
> **B-BASE.** *Otherwise — including every mixed outcome, and including a take rate between
> 17.88 % and 18.10 % — the base branch stands: price target **$170–185**.*

Four things are fixed now so they cannot be re-read on the day:

1. **B-BULL needs both legs.** A take rate of 18.14 % with "high single digit" nights is **not** a
   bull flip; it is B-BASE. The two legs are not independent evidence — INT-06 and INT-18 are read
   off the same demand path — which is exactly why the rule requires both.
2. **The "flat take rate" leg is defined as ≤ 17.88 %, not "below 18.10 %".** Between the two lies
   a 22 bp corridor in which the fee thesis is neither confirmed nor dead. Our own central case
   (18.14 %) sits 4 bp above the top of that corridor and the kernel's (18.09 %) sits 1 bp below
   it. **The branch rule must not be decided at the 5 bp level**, so the corridor is B-BASE.
3. **λ_Q3 = 17.24 % is not a take rate below 18.10 %.** It is revenue over **lagged** GBV; converted
   at the 3Q26 base ratio of 1.0496 it is **18.09 %**. The 16.77–17.06 % figures in circulation are
   the same lagged object at kernel weight w = 0.38. **If any of those numbers reaches a slide next
   to 18.10 %, the slide is wrong.**
4. **The 18.10 % test is a GBV test wearing a fee test's clothes.** At the frozen card's GBV the
   *no-fee* counterfactual already clears at 18.35 %. Move GBV by 0.22 % and the test flips. Say so
   on the slide rather than letting a judge find it.

---

## 4. What this card deliberately does NOT do

- **It does not take the v2 live block's nights or ADR as card values.** B1 §5.1 is explicit that
  the marginals are inherited and their sins with them: `mix_nights_m` **loses to a seasonal naive
  on both windows (1.549 / 1.105)** and `mix_gbv_musd` loses on both (1.312 / 1.021). The
  reconciliation fixed the block's **internal consistency**; it did not make those objects
  skilful. The ADR figure of +5.17 % is a **definitional residual** — it is where the published
  block's 0.22 pp identity break was charged, because ADR is the only one of the three with no
  registered baseline at all. Quoting +5.17 % as an ADR forecast would be quoting a plug.
  The nights and ADR card values come instead from the two objects that have a measured standing
  against naive: the **reviews stays index (0.68)** and **ADR card v2 (0.994 — a tie, and labelled
  a tie)**.
- **It does not re-open `ABNB-WS20-v1`.** No feature, transformation, window or baseline in WS20 is
  touched; touching any of them would make the 5 Nov observation exploratory rather than
  prospective.
- **It does not run `harness/score.py`,** and it registers nothing. Every row here is a LIVE
  pre-registration, not a scored object.
- **It does not quote the kill list:** the −3.4 pp Q4 FX step · "82 % of Q4 FX already determined" ·
  "+4.05 % fee uplift" as measured · the 9/9 guide-below-Street rule as a signal · "half of ADR
  growth is bigger units" · any FY27 level edge without the +9.2–11.5 % band · any p-value for the
  drift rule · **the restated unearned-fees "pin"** (proved circular: `restated_unearned_q ≡
  coverage_norm_season(q) × revenue_{q+1}`, and the 2Q26 value uses the 3Q26 **guide midpoint**).
- **It does not claim ex-FX acceleration.** The sign of "ex-FX accelerates into 4Q26" flips on a
  **$65 M move in a $26 bn GBV estimate (0.25 %)**: −0.2 pp at the frozen card's $26,185 M, +0.1 pp
  at $26,300 M, +0.9 pp at $26,550 M, break-even $26,250 M. The claim the arithmetic supports is
  that **ex-FX growth is flat**.

---

## 5. Decisions required before signature

Eleven card rows carry `decision_required = TRUE`. They are resolved by the eleven decisions below —
except D-06, which is housekeeping and attaches to no row. Each has a recommended default, the
reason, and what moves if the team overrides it. **No decision may be left open at signature.**

| id | the decision | options | **recommended default** | why | what it moves |
|---|---|---|---|---|---|
| **D-01** | Which revenue object sets INT-01, and therefore INT-06/07 | (a) guide + cushion / `live-block-v2` **$4,816.1 M** · (b) kernel λ_Q3 × lagged GBV **$4,804.0 M** | **(a) $4,816 M** | For a quarter that has **already been guided**, `guide_cushion` is the scoreboard winner on **both** windows (RMSE ratio 0.377 / 0.319) and beats the pre-guide Street. The kernel's `ex_covid` (0.565 / 0.484) is the winner on the **no-guide** information set — a different question. The two are 0.25 % apart, "two constructions, not three". | **The hinge: P(≥18.10) = 0.53 under (a), 0.49 under (b).** The test straddles the line on this choice alone. Both must appear in the memo. |
| **D-02** | Whether the card's nights value is the reviews index (+9.5 %) or the team baseline (+9.9 %) | (a) index **+9.5 %**, band 8.5–11.0 · (b) team baseline **+9.9 %**, band 8.5–10.3 · (c) index point with the baseline band | **(a) +9.5 %, band 8.5–11.0** | The index is the **only team-built series that beats naive out of sample** (0.68, n = 10, jackknife 0.63–0.86, permutation p 0.001, corroborated by a 0.59 Eurostat cross-check). The team baseline is a bridge, not a scored object. **Do not mix the baseline point with the index band** — the synthesis does this in one place and it is not defensible. | Nights level 146.3 M vs 146.8 M; GBV 25,816 vs 25,906; 5 bp of take rate. |
| **D-03** | Whether ADR card v2 is quoted as a forecast at all, given it failed its own test | (a) quote it, with FAIL stated · (b) quote the naive (+4.0 % ex-FX) and carry v2 as attribution only | **(a), with the FAIL stated in the same sentence** | 0.994 is a **tie, not a pass**, and the card says so. But it beats AR(1) (0.79) and the old H build (0.70), and the mix terms are genuinely measured. What must travel with it: the **+4.61 pp pricing residual is a persistence rule, not a measurement**, and if the residual mean-reverts to 2.40 reported ADR is about **+0.8 %, not +3.0 % — roughly $2.2 bn of annualised GBV**. ⚠ Also resolve the **PASS/FAIL contradiction** inside `research/notes/adrq3/` (I says PASS twice, J and the synthesis say FAIL). | ADR ±2.2 pp; GBV ±$570 M; ~40 bp of take rate. |
| **D-04** | **Which BLOCK the card pre-registers** — not which GBV. §1.5 shows the per-object winners break ABNB's own ADR identity by **−3.13 pp**, so the choice is a block, taken once | (i) backtest-winner block: 146.3 M / $176.47 / **$25,816 M** · (ii) registered block: 147.38 M / $180.15 / **$26,549.8 M** · (iii) implied-ADR hybrid (keeps registered GBV, charges the difference to a **$181.48 plug**) | **(ii) as the headline, (i) published beside it, (iii) rejected** | **(iii) is rejected outright**: it prints an ADR 2.9 pp above our own ADR card and calls it a forecast — the F3 defect wearing new clothes. Between (i) and (ii): (i)'s two legs are the only objects on the card with a measured standing against naive (0.68 and a 0.994 tie), and (ii)'s nights and GBV both *lose* to a seasonal naive. But (i)'s GBV is a **derived residual with no GBV object behind it**, and at **+12.7 % it sits below management's own "mid teens" (14–16 %) guide** — set on 6 Aug with July bookings in hand, at a company that has beaten its guide **19 of 19**. (ii) is headline because its dependence was *derived* (ρ = 0.7595 on 14 walk-forward quarters) rather than asserted, and because it is what the programme registered; (i) is published because burying it would hide that our skilful objects disagree with our registered one. | **The hinge: P = 0.53 under (ii), 0.88 under (i).** $734 M of GBV, 2.8 %, 52 bp of take rate. **This is the single largest unresolved number on the card, and the one place where quietly choosing would decide the trade.** |
| **D-05** | Which FX spec sets the stated-3Q26 prediction | (a) lag-loaded **Φ × 0.851 → +2.9 → integer +3** · (b) free fit (registered) **+1.3 → +1** · (c) overnight2 WS05 **+1.98 → +2** | **(a) → +3, with (b) published beside it** | For *what management will state*, the lag-loaded spec is right regardless of which better describes the world: at a guide date only **32–38 % of the guided quarter's FX has printed**, so a lag-0 loading forecasts something nobody can see. H2 is the best point-in-time forecaster (RMSE 0.99 pp vs 1.59–1.88 free fit). (c) is the **same family on an older vintage (28 Aug vs 4 Sep)** and is superseded, not contradicted. **But the full-sample rejection of Φ stands (LR 10.2, p 0.017) and the live evidence for Φ is n = 3** — both are reported, neither suppresses the other. | Nothing on the block; everything on which internal number survives 5 Nov. This is the cleanest genuinely falsifiable call on the card. |
| **D-06** | Retire the unsourced "$4.80 bn" 3Q26 revenue in `docs/q3nowcast/SYNTHESIS.md` L13 | (a) retire it · (b) source it · (c) leave it | **(a) retire it** | It reconciles to nothing. The underlying note (J §2.6) prints **$4,632 M** from GBV × an *assumed flat* 17.88 % take rate; $25.95 bn × 17.88 % ≈ $4.64 bn. $4.80 bn appears in **no** note under `research/notes/`. Left standing it silently supplies a **0.82** take-rate probability from a number nobody computed. | Removes the 0.82 and the 0.32 rows from §1.3 as *forecasts*; they stay as an audit trail. |
| **D-07** | Fee step on or off for the INT-16/17 headline | (a) no fee step **$3,161 M** · (b) θ = 0.83 primitives half step **$3,179 M** · (c) both | **(c) — headline (a), publish (b)** | The no-fee column is the **conservative** read: at θ = 0.83 the migrated cohort's GBV *falls* 1.60 %, so a GBV_3Q26 that already embedded the migration ramp would sit below the grid point paired with it. And **θ is unidentified, not measured** — a histogram bin midpoint from a *voluntary* Austin sub-sample; the mandatory cohort has not repriced. | P(below Zacks) 0.63 vs 0.57; P(below the broad panels) 0.49/0.50 vs 0.43/0.44 — i.e. straight through a half. |
| **D-08** | Whether to adopt the ex-NA lap in the 4Q26 nights baseline | (a) team baseline **+8.9 %** · (b) ex-NA lap **+8.0–8.2 %** · (c) Theo re-based **+7.6 %** | **(b) as the base, with +8.9 % as the top of the band** | The cancellation redesign and single-fee tranche 1 were **global** from October 2025, so their y/y windows close everywhere from 4Q26; PR #32 laps them in **North America only** (and its "NA" cohort is really **US only** — Canada got RNPL on 4 Mar 2026). The 40–50 % split is **pinned out-of-sample** by the 4Q25 disclosure: it is the only split that reproduces management's "over 200 basis points". **Action: ask Jessie to check the 40–50 % split against the backlog-conversion table** before signature. | 0.70–0.88 points of 4Q26 nights; moves INT-18's implied rate toward D §5's ≤ 7.5 % "supports the drag" line. Note the *level* lap (1.35 pts NA + 0.70–0.88 ex-NA) is **2× to 15× the RNPL cancellation drag** (central cell −0.15 to −0.93 pts) — the anniversary, not the cancellations, is the story. |
| **D-09** | Which FY26 guide-raise base rate is published | (a) **0.67** (Q3-print re-statements, n = 7) · (b) **0.75** (FY26-revenue line only, n = 2) | **(a) 0.67** | n = 7 beats n = 2, and 0.75 is a Laplace rate on two observations. Publish 0.67, record 0.75, and state that **there is one cut in the record** — the tell file's "only raised, never cut" is wrong. | ~8 pp on one probability; nothing structural. |
| **D-10** | **The funds-payable refutation condition is written two incompatible ways in the tree** | (a) **below +3 %** refutes (`03_short-thesis-viability.md`, twice) · (b) **at or above +11 % with the gap narrowing** refutes (`01_rnpl-nights-mechanics-audit.md` §6) · (c) **two-sided** | **(c) two-sided, as written in INT-11** | The two are not a contradiction so much as two different objects being falsified — (a) breaks the **exposure solve**, (b) breaks the **module**. But a card that carries only one of them is **unfalsifiable in practice**, because a print outside the band in either direction would find a document saying it was expected. Fix it before signature: **< +3 % and > +11 % both break something, and the card says which.** Add the companion falsifier: re-solving `u` on the 3Q26 10-Q and getting **7–12 M nights** again would contradict the module's ~22.6 M for 3Q26. | Nothing on the block; it is the difference between a test and a rationalisation. **This is the one decision that makes INT-11 a real pre-registration.** |
| **D-11** | **Whether Theo's 4Q26 ex-NA lap and PR #32's 1Q27 ex-NA lap are chained** | (a) chain them · (b) **adopt one and zero the other** | **(b) — adopt the 4Q26 lap (−0.79 pp) and zero PR #32's 1Q27 −1.75 pp, or vice versa; never both** | The bridge already takes **−0.79 pp** for the ex-NA lap in 4Q26 while PR #32 defers the **whole −1.75 pp** to 1Q27. **Chain them and the ex-NA fee/cancellation leg is counted twice** — worth ~0.8 pp of 4Q26 nights, which is most of the distance between the two candidate 4Q26 baselines in D-08. Related, and also unresolved: the pull-forward reversal is **−0.11 / −0.16 / −0.46 pts** for 3Q26 / 4Q26 / **1Q27** derived from the share path, against the bridge's −0.20 in 3Q26 — **1Q27 is ~4× 3Q26 and every team model carries zero there.** | Up to 0.8 pp of 4Q26 nights and ~1.8 pp of FY27 — i.e. it moves INT-18 across the D §5 "supports the drag" line on its own. |

**Two cross-cutting items that are not card rows but must be actioned before 5 Nov:**

- **Re-pull and timestamp every consensus anchor 3–4 Nov** (Zacks, Alpha Vantage/LSEG-family, S&P
  Global, Yahoo) for 3Q26, 4Q26, FY26, FY27, and re-pull again if Zacks publishes a nights/ADR/GBV
  consensus. **Vendors overwrite. The trade flips on which vendor we cite.** The 11 Sep vintages in
  this card are the pre-registration; the Nov vintages are the scoring bar. Owner **P4 — unassigned**.
- **Owner gap.** Krish, Theo and Jessie are named in the sources. **Willem is named in no document
  in this programme.** INT-17 and the vintage re-pull are proposed to him because market-data
  capture is the one unowned role, but that is an assignment this card *proposes*, not one it
  found. Confirm at signature.

---

## 6. Scoring template — 6 Nov 2026

Copy this table into `SCORED_ABNB-INT-v1.md` on 6 Nov. **Fill it before reading any sell-side
note.** One row per item; no row is deleted, including the ones that refute us.

| item_id | prereg_value | lo | hi | printed_value | source_read (file/page/line) | inside_band Y/N | verdict SUPPORT / REFUTE / AMBIGUOUS / ABSENT | beat_baseline Y/N | abs_error | baseline_abs_error | scorer | timestamp | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INT-01 | 4816 | 4755 | 4878 | | | | | | | | | | |
| INT-02 | +9.5 | +8.5 | +11.0 | | | | | | | | | | |
| INT-03 | 176.47 | 174.20 | 178.75 | | | | | | | | | | |
| INT-04 | +3.46 | +2.13 | +4.78 | | | | | | | | | | |
| INT-05 | 26550 | 25456 | 27643 | | | | | | | | | | |
| INT-06 | 18.14 | 17.57 | 18.76 | | | | | | | | | | |
| INT-07 | 0.53 | | | | | | | | | | | | |
| INT-08 | +3 | +0.3 | +3.5 | | | | | | | | | | |
| INT-09 | +3.6 | 4.5 | 7.0 | | | | | | | | | | |
| INT-10 | 0.68 | 8.6 | 11.5 | | | | | | | | | | |
| INT-11 | +8.0 | +5.0 | +11.0 | | | | | | | | | | |
| INT-12 | record | | | | | | | | | | | | |
| INT-13 | record | 71 | 74 | | | | | | | | | | |
| INT-14 | absent | 21 | 24 | | | | | | | | | | |
| INT-15 | none | | 1.5 | | | | | | | | | | |
| INT-16 | 3161 | 3012 | 3312 | | | | | | | | | | |
| INT-17 | 0.49/0.50/0.63 | | | | | | | | | | | | |
| INT-18 | high single digit | 7.6 | 9.4 | | | | | | | | | | |
| INT-19 | raised, 0.67 | | | | | | | | | | | | |
| INT-20 | 2960 | 2930 | 2990 | — Feb 2027 — | | | | | | | | | |
| INT-21 | — exploratory, not scored — | | | | | | | | | | | | |
| **B-BULL** | conditional | | | take rate ≥18.10 **AND** "low double digit" → | | | LIVE / NOT LIVE | | | | | | |
| **B-BEAR** | conditional | | | "high single digit" **AND** take rate ≤17.88 → | | | LIVE / NOT LIVE | | | | | | |
| **B-BASE** | conditional | | | otherwise → | | | LIVE / NOT LIVE | | | | | | |

**Scoring discipline, fixed now:**

1. **Probabilistic rows (INT-07, INT-17, INT-18, INT-19) are scored by log score and Brier, not
   by right/wrong.** A 0.53 that resolves the other way is not a failure; a 0.53 quoted as a call
   is.
2. **Every level row is scored against its named baseline as well as against the band.** Inside the
   band while losing to naive is **not** a success and is recorded as such.
3. **Read each number from the primary document** — the shareholder letter, the 10-Q, the
   transcript — and record file, page and line in `source_read`. A vendor summary is not a read.
4. **Re-run the two live backtests the same day**: add 3Q26 to the reviews-index walk-forward
   (INT-10) and to the ADR card-v2 walk-forward, and record the new ratios whichever way they go.
   *If the ADR print lands at the mean-reversion case, the persistence rule is retired, not
   re-fitted.*
5. **Nothing in §2, §3 or §5 is edited on or after 5 Nov.** Corrections go in a dated addendum to
   `SCORED_ABNB-INT-v1.md`.

---

## 7. Signature block — complete at freeze

```
spec_id            : ABNB-INT-v1
frozen_at          : ____________________  (UTC timestamp at signature)
commit_hash        : ____________________  (fill from C3 once the branch is pushed)
decisions_resolved : D-01 ___  D-02 ___  D-03 ___  D-04 ___  D-05 ___  D-06 ___
                     D-07 ___  D-08 ___  D-09 ___  D-10 ___  D-11 ___
pre_signature_acts : ADR PASS/FAIL contradiction in research/notes/adrq3/ resolved ___
                     Jessie confirms the 40-50% ex-NA split ___
                     P4 named and consensus re-pull diarised for 2-3 Nov ___
signatories        : Theo ______  Krish ______  Willem ______  Jessie ______
scored_on          : 2026-11-06
```

**Not valid until every decision above reads RESOLVED and every pending cell is filled.**
