# R2 — 3Q26 revenue: kernel vs guide+cushion vs bridge

## 1. Header
- Line: R2 · Judge's question: "You say 3Q26 revenue beats and you do not trade it; what is the number and why three of them?"
- Digger: opus · Date: 2026-09-18 · Commit: e6d9832

> The brief names commit `b098ac2`. HEAD was `11b3d39` when this dossier opened and `e6d9832` when both
> receipts were written (other diggers are committing on `theo/pitch-model-v2` in parallel). Both receipts
> carry `e6d9832`. Nothing in this line's inputs changed between those commits.

**One-paragraph answer.** There are **not three numbers — there are two mechanisms and one of them is quoted
twice.** `h2_bridge_v3`'s 3Q26 revenue row is *arithmetically the kernel*: λ_Q3 = 0.1723936185 applied to the
same $27,866.667M of lagged printed GBV, reproducing $4,804.0355M — identical to the kernel to **$0.000000M**.
The bridge's own 3Q26 nights, ADR and GBV never touch 3Q26 revenue; they are the *4Q26* lagged base. So the
real choice is (i) the kernel, **$4,804.0M**, and (ii) guide midpoint × (1 + trailing-8 cushion), **$4,817.8M**
at DEC-0001's 1.857% mean. They are **$13.8M — 0.29% — apart**, which is inside what Airbnb's own $0.1bn GBV
disclosure rounding is worth on this arithmetic (±$8.6M). The $4,816.1M in the pre-registration is neither: it
is a BMA-log-score blend, 0.5366 on the *median*-cushion baseline ($4,814.69M) and 0.4633 on the *mean*-cushion
`print_from_guide` ($4,817.82M), and its own JSON records `mix_beats_best_single_both_windows: false`. We do not
trade the level because on this line the Street's measured bias is **−$68.3M (W1) / −$54.9M (W2)** — the same
size as the $60.0M "beat" we would be claiming over the $4,744M Street mean.

## 2. The number

All 3Q26 revenue objects below are **scenario-invariant by construction** (see §2a): the kernel and the bridge
run on printed 1Q26 and 2Q26 GBV, the guide midpoint is a filed fact, the cushion is DEC-0001, and a consensus
stamp has no scenario. Only the *card* varies, and only if the model routes 3Q26 revenue through the decided
nights and ADR (§8 choice 2).

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 — **kernel**, λ_Q3 × lagged printed GBV | **4804.0** | 4777.9 | 4846.2 | musd | printed GBV to 2Q26 (2026-08-06); λ pkg 2026-09-11 |
| base | 3Q26 — **guide + cushion**, DEC-0001 mean 1.857% | **4817.8** | 4777.1 | 4858.6 | musd | guide 2026-08-06; cushion PIT 2026-08-06 |
| base | 3Q26 — guide + cushion, trailing-8 **median** 1.790% (harness `baselines/guide_cushion`) | 4814.7 | — | — | musd | same |
| base | 3Q26 — **bridge v3** | **4804.0** | 4777.9 | 4846.2 | musd | bridge built 2026-09-12, FX through 2026-09-04 |
| base | 3Q26 — optimal-mix BMA blend carried by `live-block-v2` (INT-01's number) | 4816.1 | 4754.6 | 4877.6 | musd | 2026-09-11 |
| base | 3Q26 — K1 ledger-only conditional (a different information set) | 4795.0 | 4683.0 | 4914.0 | musd | 2026-09-11, 80% interval |
| street | 3Q26 — **Street** | **4744.0** | 4737.5 | 4744.9 | musd | LSEG-family, as-of 2026-09-11 (DEC-0013) |
| n/a | 3Q26 — management guide range and midpoint | 4730.0 | 4690.0 | 4770.0 | musd | 2Q26 letter, 2026-08-06 |
| base | 3Q26 — **card (recommended)** | **4804.0** | 4777.9 | 4846.2 | musd | kernel, DEC-0006 |
| short | 3Q26 — card | **4678.4** | — | — | musd | decided nights × ADR at the base-tying take rate |
| breaker | 3Q26 — card | **4870.4** | — | — | musd | same |

Notes that must travel with the table:

- **Kernel arithmetic, reproduced here.** Printed GBV used: **1Q26 $29,200M** and **2Q26 $27,200M**
  (`data/processed/airbnb_quarterly_kpis.csv`, column `gbv_usd_b` = 29.2 and 27.2; Airbnb discloses GBV only to
  the nearest $0.1bn, per H0). Base = ⅔ × 27,200 + ⅓ × 29,200 = 18,133.333 + 9,733.333 = **$27,866.667M**.
  λ_Q3 is the 3-cell same-season mean of 3Q23 17.390785%, 3Q24 17.145482%, 3Q25 17.181818% = **17.239362%**.
  0.17239362 × 27,866.667 = **$4,804.04M**. At DEC-0006's rounded λ of 17.24% it is **$4,804.21M**. Both round
  to the $4,804M memo v3 and `tieout_targets.csv` carry; the machine-readable point below is 4804.0.
- **The low/high on the kernel are λ's own three cells**, not a forecast interval: 17.145482% → $4,777.9M and
  17.390785% → $4,846.2M, a **$68.3M** span — five times the kernel-vs-guide+cushion disagreement the open
  D-01 decision is fighting over.
- **The $0.1bn GBV rounding is worth ±$8.6M** on the kernel (±$50M on the lagged base × λ). Two thirds of the
  D-01 gap is inside Airbnb's disclosure granularity.
- **The bridge is not a third route.** `h2_bridge_revenue_dollars.csv` row 3Q26 carries
  `lagged_gbv_busd = 27.866666…` and `conversion_mean = 0.17239361851…`; bridge − kernel = **$0.000000M**.
  Its `revenue_low/high` (4,777.9 / 4,846.2) are the same λ min/max, not scenarios.
- **The $4,816.1M is guide + cushion too**, at an effective cushion of 1.8203% that nobody decided: weights
  0.5366 × $4,814.69M (median-c) + 0.4633 × $4,817.82M (mean-c). Every other carrier in the pool has weight
  < 1e-4. DEC-0001 chose the **mean**, so the DEC-consistent number is **$4,817.8M**.
- **Take-rate consequence.** $4,804.0M on the decided GBV (D1 nights 146.3m × D4 ADR $176.88 = $25,877.5M) is a
  printed take rate of **18.5645%** — see §7 and §8 choice 3.

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| revenue_kernel_musd | base | 3Q26 | 4804.0 | musd | lambda_Q3 17.239362 pct x (2/3 x 27200 + 1/3 x 29200 = 27866.667); SCENARIO-INVARIANT because both GBV are printed facts; 4804.2 at DEC-0006 rounded lambda 17.24 pct |
| revenue_kernel_musd | short | 3Q26 | 4804.0 | musd | identical value; scenario-invariant, printed 1Q26 GBV 29200 and 2Q26 GBV 27200 |
| revenue_kernel_musd | breaker | 3Q26 | 4804.0 | musd | identical value; scenario-invariant, printed 1Q26 GBV 29200 and 2Q26 GBV 27200 |
| revenue_guide_cushion_musd | base | 3Q26 | 4817.8 | musd | guide midpoint 4730 x (1 + 1.857 pct), DEC-0001 trailing-8 mean; SCENARIO-INVARIANT |
| revenue_guide_cushion_musd | short | 3Q26 | 4817.8 | musd | identical value; guide midpoint is a filed fact and the cushion is a decided statistic |
| revenue_guide_cushion_musd | breaker | 3Q26 | 4817.8 | musd | identical value; guide midpoint is a filed fact and the cushion is a decided statistic |
| revenue_bridge_musd | base | 3Q26 | 4804.0 | musd | h2_bridge_v3 3Q26 row; IDENTICAL to the kernel to 0.000000 musd; SCENARIO-INVARIANT |
| revenue_bridge_musd | short | 3Q26 | 4804.0 | musd | identical value; the bridge has no 3Q26 revenue scenario split |
| revenue_bridge_musd | breaker | 3Q26 | 4804.0 | musd | identical value; the bridge has no 3Q26 revenue scenario split |
| revenue_street_musd | base | 3Q26 | 4744.0 | musd | V1 scenario street, LSEG-family as-of 2026-09-11 (DEC-0013); SCENARIO-INVARIANT, a consensus stamp has no scenario |
| revenue_street_musd | short | 3Q26 | 4744.0 | musd | identical value; V1 scenario street row, LSEG-family as-of 2026-09-11 |
| revenue_street_musd | breaker | 3Q26 | 4744.0 | musd | identical value; V1 scenario street row, LSEG-family as-of 2026-09-11 |
| revenue_card_musd | base | 3Q26 | 4804.0 | musd | MECHANISM kernel lambda_Q3 x lagged printed GBV per DEC-0006; equals memo v3 and tieout_targets |
| revenue_card_musd | short | 3Q26 | 4678.4 | musd | MECHANISM decided nights 145.0 x ADR 173.80 x take rate 18.5645 pct held at the base-tying level |
| revenue_card_musd | breaker | 3Q26 | 4870.4 | musd | MECHANISM decided nights 147.0 x ADR 178.47 x take rate 18.5645 pct held at the base-tying level |
| revenue_guide_mid_musd | base | 3Q26 | 4730.0 | musd | management guide midpoint, 2Q26 letter 2026-08-06, range 4690 to 4770 |
| revenue_live_block_musd | base | 3Q26 | 4816.1 | musd | optimal-mix BMA blend carried by live-block-v2; the number INT-01 pre-registers; 0.5366 x 4814.69 median-c plus 0.4633 x 4817.82 mean-c |
| implied_take_rate_pct | base | 3Q26 | 18.5645 | pct | consequence of carrying 4804.0 on decided GBV 25877.5; NOT a decided input, D6 and D7 own it |
| implied_gbv_musd | base | 3Q26 | 25877.5 | musd | D1 nights 146.3 x D4 ADR 176.88; shown so the card can be checked against the identity |
| implied_gbv_musd | short | 3Q26 | 25201.0 | musd | D1 nights 145.0 x D4 ADR 173.80 |
| implied_gbv_musd | breaker | 3Q26 | 26235.1 | musd | D1 nights 147.0 x D4 ADR 178.47 |

## 3. Derivation chain

**Kernel / bridge (the carried base):**
1. 2Q26 shareholder letter and 10-Q, 6 Aug 2026 — GBV $27.2bn; 1Q26 10-Q, 7 May 2026 — GBV $29.2bn →
2. `data/processed/airbnb_quarterly_kpis.csv`, column `gbv_usd_b`, rows `2026Q1` = 29.2 and `2026Q2` = 27.2
   (cross-checked against `docs/pitch-model-v2/dossiers/H0_h0_history.md` `gbv_musd` 29200 / 27200) →
3. λ_Q3 from `data/processed/forecast_methods/live_block_v2/06_seasonal_history_and_kernel_wedge.csv`,
   column `lambda_pct`, rows 2023Q3 / 2024Q3 / 2025Q3 = 17.390785 / 17.145482 / 17.181818; 3-cell mean
   17.239362% (R1 dossier `lambda_q3_pct` 17.24, DEC-0006) →
4. `data/processed/pitch_model_v2/receipts/R2/r2_recompute.py` → `r2_objects.json`, key
   `kernel_at_package_lambda` = 4804.0355 · identical cell: `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv`,
   row `3Q26`, column `revenue_musd` = 4804.035502546225.

**Guide + cushion:**
1. 2Q26 shareholder letter, 6 Aug 2026, "We expect to generate revenue of $4.69 billion to $4.77 billion" →
2. `data/processed/overnight/02_guidance_ledger.csv`, row `ABNB-2Q26-revenue_usd_m-3Q26-182`,
   `value_low/high/mid` = 4690 / 4770 / 4730 →
3. `data/processed/forecast_methods/guidance_policy/02_cushion_pit.csv`, row `guide_date=2026-08-06`,
   `c_mean_pct` = 1.856743 (DEC-0001 rounds to 1.857), `c_median_pct` = 1.790491 →
4. `r2_recompute.py` → `r2_objects.json`, keys `guide_cushion_at_DEC0001` = 4817.836 and
   `guide_cushion_at_median` = 4814.690.

**Street:** `data/processed/forecast_methods/L0/L0_vintage_register.csv` (frozen) → `V1_v1_street.md` §2a,
`street_revenue_musd`, street, 3Q26 = 4744 (LSEG desktop as-of 2026-09-11 n=37 $4,744.3M; Yahoo 2026-09-13
15:20Z n=36 $4,744.9M; Alpha Vantage 2026-09-11 n=36 $4,737.5M — one LSEG-family panel, counted once).

**Card scenarios:** DEC-0004 nights (146.3 / 145.0 / 147.0) × DEC-0008 and DEC-0009 ADR (176.88 / 173.80 /
178.47) → `r2_objects.json`, `scenario_gbv_musd` → × `implied_take_rate_pct_tying_base_to_kernel` 18.5645 →
`card_musd`.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-18 | `docs/pitch-model-v2/DECISIONS.md` DEC-0001 / 0004 / 0006 / 0008 / 0009 / 0013 / 0016 | cushion 1.857% mean; nights 146.3 / 145.0 / 147.0; **fixed kernel λ_Q3 17.24% at ⅔–⅓ drives forward revenue for R2 and R5**; ADR 176.88 / 173.80 / 178.47; LSEG-family Street; no leaning | **governs** — the latest and binding register |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` | 3Q26 revenue base **$4,804M**, short $4,681M, Street $4,744M; "3Q26 revenue itself is a beat on our numbers … we say so and do not trade it" | **governs** the carried card; consistent with DEC-0006 and with `model/pitch_model_v2/spec/tieout_targets.csv` (R2 3Q26 base 4804, short 4681) |
| 2026-09-12 | `05_backtests/REBASE_h2_bridge_v3_nights_adr.md`, `data/processed/h2_bridge_v3/` | 3Q26 revenue $4,804.0M; 3Q26 GBV $26.03bn; 4Q26 revenue $3,178M; implied 4Q26 guide mid $3,059M | governs the bridge, **but its 3Q26 revenue is not an independent object**: `lagged_gbv_busd` and `conversion_mean` are the kernel's own inputs, difference $0.000000M (§5) |
| 2026-09-11 | `data/processed/forecast_methods/optimal_mix/combined_live_objects.json` → `print_3Q26_revenue_musd` | $4,816.1M = 0.5366 × `baselines/guide_cushion` $4,814.69M + 0.4633 × `guidance-policy/print_from_guide` $4,817.82M; `mix_beats_best_single_both_windows: false`, "reported as a tie with the best single method" | **governs** what $4,816.1M actually is; **supersedes the PREREG's "guide + cushion" label** for that figure |
| 2026-09-11 | `analysis/src/forecast_methods/live_block_v2/` + `LIVE_3Q26_CARD.csv` | identity-reconciled 3Q26 block: revenue $4,816.1M, GBV $26,549.8M, nights 147.38m, ADR $180.15, take rate 18.1399%, P(≥18.10) 0.534 | **governs** the reconciliation; **supersedes** optimal-mix 17.8065% and `fee_takerate` 07a 18.3971% (its own `supersedes` key) |
| 2026-09-11 | `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` | 3Q26 ledger-only conditional **$4,795M** (80% $4,683–4,914); combined live $4,816M; λ_Q3 control centre 17.239% on $27,867M, warning 17.086% ($4,761M), escalate 16.934% ($4,719M); RNPL leakage −$8M to −$67M | **governs** the conditional range and the control chart; it is a *different information set* (ledger backlog), not a third card candidate |
| 2026-09-11 | `05_backtests/RED_TEAM.md` §F3 and the pre-registration table line "3Q26 print ~4,816 musd (= guide 4,730 × 1.0182)" | F3: three live 3Q26 objects mutually inconsistent, the take-rate pre-registration turns on which you read | F3 **governs** and was fixed by `live_block_v2`; the "× 1.0182" gloss is a **back-solved ratio**, not a decided cushion — **superseded by DEC-0001** (mean 1.857%) |
| 2026-09-11 (as amended) | `05_backtests/SCOREBOARD_v2.md` revenue-level PIT prior | W1 n=14 / W2 n=10 MAE and RMSE ratio: `guide_cushion` 30.994 / 0.377 and 30.895 / 0.319; `print_from_guide` 29.167 / 0.379 and 30.689 / 0.331; `kernel last3_ex_covid` 38.507 / 0.555 and 36.165 / 0.472; `street` 87.714 / 1.073 and 82.100 / 0.871; all four survive both windows except `street` | **governs** the test record in §6 |
| undated (pre-registration) | `05_backtests/PREREG_ABNB-INT-v1.md` INT-01 and D-01 | INT-01 pre-registers 3Q26 revenue **$4,816M**, band $4,755–4,878M; D-01 recommends (a) "guide + cushion / live-block-v2 $4,816.1M" over (b) "kernel $4,804.0M", because guide_cushion wins both windows on a guided quarter | **superseded on the mechanism by DEC-0006**, and on the carried value by memo v3 / the tieout target ($4,804M). **INT-01's own number has not been amended** — that is this line's live conflict (§7, §8 choice 1) |
| 2026-09-18 | `docs/pitch-model-v2/dossiers/V1_v1_street.md` §2a and `R1_r1_kernel.md` §2a / `R3_r3_cushion.md` §2a | Street 3Q26 $4,744M; λ_Q3 17.24% at w₁ = ⅔; cushion mean 1.857% | **govern** their own inputs; this line consumes them unchanged |

**Web fetches: none.** Every figure above is in the repo; no public-filing fetch was needed (0 of the 5 allowed).

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/R2/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id R2 --watch data/processed/forecast_methods/live_block_v2 --watch data/processed/h2_bridge_v3 --cmd "python3 data/processed/pitch_model_v2/receipts/R2/r2_recompute.py"` · Exit: 0 · Wall: 0.2s · Interpreter: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` (plain `python3`, pandas 3.0.0; `.venv-pd2` not needed) · `restored: true` · `changed: []`
- Output: `data/processed/pitch_model_v2/receipts/R2/r2_objects.json` key `kernel_at_package_lambda` = **4804.0355** and key `bridge_equals_kernel.revenue_diff_musd` = **0.000000** · Committed value: `data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv` row 3Q26 `revenue_musd` = 4804.035502546225, memo v3 and `tieout_targets.csv` $4,804M · Tolerance: ±$0.5M · **Match: yes**
- Second receipt (package run): `data/processed/pitch_model_v2/receipts/R2/receipt_live_block_v2.json` · Command: same wrapper, `--watch analysis/src/forecast_methods/live_block_v2 --watch data/processed/forecast_methods/live_block_v2 --cmd "python3 analysis/src/forecast_methods/live_block_v2/run.py"` · Exit: **0** · Wall: 2.1s · `restored: true` · `changed: []` — i.e. the package **rewrote all 13 committed outputs and the 5 registry files bit-for-bit identically**, revenue $4,816.1M and take rate 18.1399% / P(≥18.10) = 0.5345 reproduced exactly (`stdout_live_block_v2.txt`). The only new file was a `__pycache__` artefact, which the wrapper removed. `harness/score.py` was not run.
- Also reproduced in the same receipt, each to the printed digit: guide + cushion at DEC-0001 **$4,817.84M** and at full precision **$4,817.82M**; at the trailing-8 median **$4,814.69M** (= the `baselines/guide_cushion` live carrier point in `combined_live_objects.json`, to 1e-9); the BMA blend **$4,816.14M**; the bridge's own card GBV $26,028.0M and its implied take rate 18.4572%.
- **Not reproduced here:** the λ_Q3 estimate itself (R1's line, its own receipt), the cushion PIT bootstrap (R3's line), the Street stamp (V1's line), and the optimal-mix walk-forward weights (read from the committed JSON, not refitted). Those are consumed as committed values.

## 6. Test record

Revenue level (`revenue_musd`), PIT prior, from `SCOREBOARD_v2.md`. "This line" = the carried card's mechanism,
`kernel-lambda | revenue_level_next_q_last3_ex_covid` (DEC-0006's window). The guide+cushion column shows both
parameterisations: `baselines/guide_cushion` (median-c) / `guidance-policy/print_from_guide` (mean-c, DEC-0001's).

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 (1Q23+) | 14 | MAE, musd | 38.507 | 75.093 | 30.994 / 29.167 | 87.714 | beat naive | **pass** |
| W2 (1Q24+) | 10 | MAE, musd | 36.165 | 91.482 | 30.895 / 30.689 | 82.100 | beat naive | **pass** |
| W1 (1Q23+) | 14 | RMSE ratio to naive | 0.555 | 1.000 | 0.377 / 0.379 | 1.073 | < 1.0 on both windows | **pass** |
| W2 (1Q24+) | 10 | RMSE ratio to naive | 0.472 | 1.000 | 0.319 / 0.331 | 0.871 | < 1.0 on both windows | **pass** |
| W1 (1Q23+) | 14 | bias, musd | +0.256 | +12.777 | +10.598 / +14.689 | **−68.286** | none pre-registered | n/a |
| W2 (1Q24+) | 10 | bias, musd | +5.857 | +4.239 | +8.728 / +12.145 | **−54.900** | none pre-registered | n/a |
| W1 / W2 | 14 / 10 | 80% interval coverage | 0.643 / 0.700 | 0.929 / 0.900 | 0.643 / 0.600 | 0.786 / 0.700 | none pre-registered | n/a |
| W1 and W2 | 14 / 10 | survives both windows | yes | — | yes / yes | **no** (W1 1.073) | required to be quoted | **pass** |
| W1 and W2 | 14 / 10 | does the carried mechanism beat guide+cushion? | **no** — 38.507 vs 29.167 (W1) and 36.165 vs 30.689 (W2) | — | — | — | INT-01 pre-registers the guide+cushion blend $4,816M | **fail** |
| n/a | n/a | bridge v3 vs kernel, 3Q26 revenue | **$0.000000M apart** | — | — | — | this is an identity, not a test | **no test exists** |
| n/a | n/a | card $4,804.0M ÷ decided GBV $25,877.5M | **18.5645%** | — | — | — | INT-06 pre-registers 18.14%, flip at 18.10% | **fail** |

Two wording rules observed. Following the kill list, the claim is **"no single object beats guide × cushion on
both windows"**, not "nothing beats it": `optimal-mix mix_revenue_musd_parsimonious` beats it on W1 alone
(0.360 vs 0.377) and `mix_revenue_musd_all` on W2 alone (0.313 vs 0.319); neither does both. And the naive
denominators differ slightly between objects because each scores only the quarters it can form, so the MAE and
ratio columns are not exactly proportional.

**Strongest known failure:** the model carries the *loser* of its own scoreboard — the kernel's $4,804.0M is
24–32% worse than guide × cushion on both PIT windows and contradicts INT-01's pre-registered $4,816M — and,
worse, carrying it on the model's own decided nights and ADR forces a printed take rate of **18.5645%**,
68bp above 3Q25's printed 17.882% and 42bp above the pre-registered INT-06 18.14%, against management's 6 Aug
guide that the implied take rate "remain relatively in-line year-over-year".

## 7. Kill list and consistency

- **Kill-list check: clear, with two live risks.** (i) "Nothing beats guide × cushion" is on the kill list; this
  dossier uses the sanctioned wording (§6). (ii) `fee_takerate` 07a's 18.3971% reaches its number through a fee
  uplift step whose θ = 1 variant is the killed "+4.05% fee uplift"; it is quoted here only as the object
  `live_block_v2` explicitly supersedes, never as ours. No withdrawn number is carried. The "9/9
  guide-below-Street drift rule", the −3.4pp Q4 FX step, the restated-unearned-fees pin and M5's hierarchical
  cushion model do not enter this line at all.
- **A governing note quotes a number the decisions have since replaced.** `RED_TEAM.md` glosses the
  pre-registered 3Q26 print as "4,816 musd (= guide 4,730 × 1.0182)". 1.8203% is not a cushion the programme
  ever estimated — it is the ratio implied by the BMA blend, back-solved. DEC-0001 chose the trailing-8 **mean**
  1.857%, which gives **$4,817.8M**. Stated per rule 4.
- **Conflict 1 — with the pre-registration (D-01, open).** `PREREG_ABNB-INT-v1.md` INT-01 pre-registers $4,816M
  and D-01 recommends option (a); DEC-0006, memo v3 and `tieout_targets.csv` carry $4,804M (option b). The
  model and its own pre-registration currently disagree by $12.1M on the single revenue cell that gets scored
  on 5 Nov. One of the two documents must move before the memo is filed. §8 choice 1.
- **Conflict 2 — with D7 / INT-06 (the take rate).** Three GBVs are live for 3Q26: the decided D1 × D4 identity
  **$25,877.5M**, the bridge card **$26,028.0M**, and `live-block-v2` **$26,549.8M**. The card revenue divided by
  each gives **18.5645% / 18.4572% / 18.0945%**. INT-06 pre-registers 18.14% with the flip pair "take rate
  ≥ 18.10% **on GBV ≥ $26.3bn**"; the decided GBV is $423M below that GBV leg, so on the decided inputs the
  model clears the take-rate leg only because it fails the GBV leg. D6 and D7 own the resolution; R2 flags it.
- **Conflict 3 — the short case's basis.** Memo v3's short $4,681M comes from `40_line_build` §8b on
  nights 144.956m and GBV $25,360.9M at a take rate of 18.4573% (the *bridge card's* implied rate). Neither its
  nights nor its GBV is the decided D1 short (145.0m, $25,201.0M). Recomputing on the decided inputs at the
  base-tying rate gives **$4,678.4M**, $2.6M (0.06%) from the memo — so the memo's number is nearly right for
  the wrong reason, and the workbook should carry the mechanical one (§8 choice 2).
- **Conflict 4 — knock-on to R5 (flagged, not decided here).** The 4Q26 kernel base in bridge v3 uses
  GBV_3Q26 = $26,028.0M. On the decided D1 × D4 GBV of $25,877.5M the 4Q26 lagged base falls from $26,418.6M to
  $26,318.4M and 4Q26 revenue from $3,178.1M to about **$3,166.0M** (−$12.1M) at λ_Q4 12.0298%. R5 owns it; the
  arithmetic is recorded here because it is the same kernel.
- **No conflict with R1 or R3.** λ_Q3 17.24% at w₁ = ⅔ and cushion 1.857% reproduce from their dossiers'
  committed values to the digit, and the λ_Q3 control thresholds ($4,761M warning, $4,719M escalate) are
  consistent with the base carried here.
- **Memo v3 wording is safe on this line.** "3Q26 revenue itself is a beat on our numbers ($4,804M vs $4,744M
  Street) … we say so and do not trade it" is accurate, and §6's Street-bias rows are the reason not to trade
  it — they should be added to the memo sentence rather than left implicit.

## 8. Open choices

1. **D-01: which mechanism the card carries for 3Q26 revenue.** Options: (a) guide × (1 + DEC-0001 cushion)
   **$4,817.8M** — the best-tested object on a guided quarter (MAE 29.2 / 30.7, RMSE ratio 0.379 / 0.331,
   survives both windows) and what INT-01 pre-registers; (b) kernel **$4,804.0M** — DEC-0006, memo v3, the
   tieout target, and the same machinery that has to produce 4Q26 and FY27 where no guide exists; (c) carry (b)
   and print (a) beside it as a labelled row. — **Recommendation: (c), card $4,804.0M**, and amend INT-01 to
   $4,804M with the band re-centred. — Why: DEC-0006 already binds the fixed kernel to R2 *and* R5, and running
   guide+cushion for 3Q26 while running the kernel for 4Q26 puts two mechanisms inside one revenue line for the
   sake of $13.8M (0.29%), which is smaller than the ±$8.6M Airbnb's $0.1bn GBV rounding is worth and one fifth
   of λ_Q3's own three-cell span. **Either way the pre-registration must be corrected** — it presently
   pre-registers a number the memo does not carry, and that is the version a judge will find.
2. **Whether 3Q26 revenue varies by scenario, and by what mechanism.** Options: (a) scenario-invariant $4,804.0M
   for base, short and breaker, because the kernel's inputs are printed facts; (b) the identity route — decided
   nights × decided ADR × a take rate held fixed at the base-tying 18.5645% → **4,804.0 / 4,678.4 / 4,870.4**;
   (c) keep memo v3's short $4,681M from `40_line_build` §8b. — **Recommendation: (b).** — Why: it is the only
   route that obeys DEC-0016 (scenarios are mechanical consequences of the decided assumptions), it ties the
   base to the kernel exactly, it reproduces memo v3's short to $2.6M, and it gives C6/C7 a breaker-case revenue
   that does not exist anywhere in the record today. (a) leaves the short and breaker columns empty; (c) carries
   a GBV that no longer matches D1 and D4.
3. **What to do about the 18.5645% implied take rate.** Options: (a) cut the card to **$4,694.2M** — the decided
   GBV at `live-block-v2`'s reconciled 18.14% — which puts 3Q26 revenue $36M *below* the guide midpoint and
   turns the memo's beat into a miss; (b) raise GBV, i.e. reopen DEC-0004 or DEC-0008; (c) carry $4,804.0M and
   **print the 18.5645% as a stated consequence**, with the y/y step (+68bp) shown against management's
   "relatively in-line". — **Recommendation: (c), with the number printed, and D6/D7 asked to rule before the
   memo is filed.** — Why: DEC-0016 forbids choosing an input to reach a wanted output, and (a) and (b) would
   both be exactly that; but 18.56% puts us on the "fee migration is visible in the print" side of our own
   pre-registered test **by construction rather than by evidence**, and a judge who divides our revenue by our
   GBV will find it in ten seconds. Better said by us first.
4. **The label on $4,816.1M.** It is a 53.7 / 46.3 BMA-log-score blend of the median-cushion and mean-cushion
   objects, at an effective cushion of 1.8203% nobody decided, and its own JSON says it does not beat the best
   single method on both windows. Options: (a) replace it with DEC-0001's mean-cushion **$4,817.8M** everywhere
   it appears (PREREG D-01(a), INT-01, K1's "combined live $4,816M"); (b) keep the blend and relabel it
   accurately. — **Recommendation: (a).** — Why: DEC-0001 already chose the mean; the blend is a third
   parameterisation of a decided statistic; the change is $1.7M and it removes a mislabel from the one
   pre-registered revenue test.
5. **Whether the bridge is presented as a third number at all.** It is arithmetically the kernel for 3Q26
   ($0.000000M apart). Options: (a) stop calling it a third route — say "two mechanisms, and the second is quoted
   at three cushions"; (b) keep three columns in the memo. — **Recommendation: (a).** — Why: the judge's question
   is literally "why three of them", and the honest answer is that there are not three. Keeping the third column
   invites a check that we lose.

## 9. Judge Q&A

1. Q: "You say 3Q26 revenue beats and you do not trade it; what is the number and why three of them?"
   A: One number — **$4,804M** — and there are two mechanisms, not three. The bridge is not a third route: its
   3Q26 revenue row is λ_Q3 = 17.239% applied to the same $27,867M of lagged printed GBV, and it reproduces the
   kernel to the cent. The genuine alternative is the guide midpoint of $4,730M grossed up by the trailing-eight
   cushion of 1.857% — **$4,817.8M**. That is a $13.8M disagreement, 0.29%, and Airbnb only discloses GBV to the
   nearest $0.1bn, which is worth ±$8.6M of it. We do not trade the level because on fourteen point-in-time
   quarters the Street's bias on this line is **−$68M**, and the "beat" we would be claiming is $60M. We would be
   selling you the Street's own low bias as our edge.
2. Q: "Then why carry the kernel, if guide plus cushion is the better-tested object?"
   A: It is the better-tested object and we say so: MAE $29.2M against our $38.5M on W1, $30.7M against $36.2M on
   W2, RMSE ratio 0.379/0.331 against 0.555/0.472. Both survive both windows; guide+cushion wins both. We carry
   the kernel because the same machinery has to produce 4Q26 and FY27, where there is no guide to lean on, and we
   would rather run one mechanism across the whole revenue line than have the best number in the one cell that
   does not move the stock. That choice costs $13.8M, it is written down, and the decision is still open.
3. Q: "Divide your revenue by your own GBV. What take rate is that, and does management agree?"
   A: **18.56%**, and no. Our nights of 146.3m and ADR of $176.88 give $25,877M of GBV, and $4,804M on that is
   18.5645% against 17.882% printed in 3Q25 — a 68bp step — while the 6 August letter guides the implied take
   rate to "remain relatively in-line year-over-year". This is the weakest joint in the line and we put it first:
   either revenue is about $110M too high on our own volume and price, or our nights and ADR are too low. Our
   pre-registered flip is the *pair*, take rate ≥ 18.10% **with** GBV ≥ $26.3bn, precisely because neither leg
   means anything alone — and on our own inputs we clear the first leg only because we fail the second.
4. Q: "If the print comes in at $4,761M, what have you learned?"
   A: Nothing about the thesis. $4,761M is λ_Q3 = 17.086%, the one-sigma warning line on a control chart built
   from three Q3 cells; the escalate line is $4,719M. On the pooled-sigma chart, which is 2.3× wider, $4,761M is
   noise. The thesis is the 3Q26 nights print against a 148.9m bar and the 4Q26 guide against $3,157–3,162M, not
   this level — which is why we pre-registered a flip rule on nights and take rate and not on revenue.

## 10. Grade
Grade: B — both receipts exit 0 with `restored: true` and zero diffs (the package rewrote all 13 committed
outputs bit-for-bit and the kernel arithmetic reproduces to $0.000000M), and every candidate object survives
both W1 and W2, but the line cannot be graded A: the value the model carries ($4,804.0M) is **not** the value
its own pre-registration commits to ($4,816M, INT-01), D-01 is open, one of the three advertised routes is an
identity rather than an independent test, and the carried number breaks the model's own take-rate
pre-registration on the decided nights and ADR.
