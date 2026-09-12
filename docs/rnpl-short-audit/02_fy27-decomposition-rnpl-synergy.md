# How RNPL enters the FY27 decomposition, and where it plugs into the composition thesis

> **STATUS, added 11 Sep 2026 (evening):** this note inherited a claim from `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` that was **refuted** by `docs/rnpl-short-audit/04_balance-sheet-verification.md` after this note was written: the single-fee migration does *not* remove fees from unearned fees (FY2025 10-K Note 2 puts host and guest fees in unearned fees), so **unearned fees is the clean RNPL line and funds payable is the FX-noisy one**. Wherever this note says "score funds payable, not unearned fees", read instead: score **(3Q26 unearned fees y/y) − (3Q26 GBV y/y)**, at or below −18 points supports the drag, −12 to −18 in line with 1H26, wider than −8 weakens; Krish's −3% unearned-fees row stands. The balance-sheet unpaid-book figure is **17–28 million nights at 30 June** (not 7–19), which brackets the disclosed RNPL flow share and reconciles with the nights module's ~21 million. Everything else in this note is unaffected. Synthesis: `docs/rnpl-short-audit/00_SYNTHESIS.md`.


- **Date:** 2026-09-11. **Author:** Opus audit agent for Theo.
- **Brief:** trace what B3 v2's FY27 driver-base nights number actually embeds; map every channel by which Reserve Now, Pay Later reaches FY27 revenue growth; phase FY27 against the FY26 comps; and write the synergy map between the RNPL work and the composition thesis.
- **Read-only pass on everything that already existed.** Two new files were written: this note and `analysis/src/rnpl_short_audit/fy27_rnpl_channels.py`, whose outputs land under `data/processed/rnpl_short_audit/`. Nothing under `forecast_methods/`, `registry/`, `model/` or `research/` was edited; `harness/score.py` was not run. `analysis/src/forecast_methods/l1_reconciliation_v2/run.py` was re-run as instructed and reproduces B3 v2 exactly (identity check max error 2.31e-14pp).
- **Companion:** `docs/rnpl-short-audit/03_short-thesis-viability.md` (same author, same date) prices RNPL as a *standalone short*. This note asks the different question: what does RNPL do to the *decomposition*.
- **Evidence labels:** *measured* (disclosed or computed from a primary source), *derived* (computed from measured inputs under stated assumptions), *assumed* (a scenario input), *unidentified* (no public data pins it), *withdrawn* (retracted; never quoted as live).
- **Withdrawn numbers deliberately absent:** the −3.4pp 4Q26 FX step, "82% determined", the +4.05% fee uplift as measured, the 9/9 drift rule, "half of ADR is unit size", and PR #32's "+10.2% consensus" (which is the team's own frozen card — `research/notes/2026-09-10_nights-baseline-reconciliation.md` §1.2).
- **Quoting rule observed throughout:** the FY27 number is a **band**, never a point.

---

## Bottom line

**RNPL does not enter B3's FY27 number anywhere. It is not in the volume line, not in the price line, not in the kernel term, and not in the assumed block. B3's `N` is four flat regional growth rates rolled forward with no lap schedule, no cancellation term and no pull-forward term.** That is not an error in B3 — B3 is a *decomposition* of a driver path it inherited — but it means the memo's headline composition sentence ("the FY26→FY27 halving is dollars, comps and mix") currently has a **product-bundle lap in the narrative and zero product-bundle lap in the arithmetic**.

Three things follow.

1. **The RNPL evidence supports FY27 nights of +6.4% to +8.2%. B3 publishes +9.46%, which is above the top of that range** [*derived*]. The low end is reached by two independent constructions 0.10pp apart — PR #32's global lap (+6.42%) and Jessie's plateau-plus-drag (+6.52%) — which is corroboration. Both are unmerged branch artefacts and neither is registered.

2. **The 2.343pp kernel-weight band that B3 calls "the single most important sentence in this note" is 99% an artefact of the λ-fitting convention, not economics.** Re-fit λ self-consistently at each `w`, as B3's own caveat 1 says would shrink the band, and FY27 growth spans **0.042pp**, not 2.343pp — **0.02 turns, not 1.12** [*derived*, `data/processed/rnpl_short_audit/kappa_anatomy_and_lambda_refit.csv`]. This is new and it changes the memo's central rhetorical move.

3. **Because of (2), RNPL clears the bar.** The RNPL lap is worth **−1.08pp to −3.22pp** of FY27 growth against the vendor-stamped Street, i.e. **−0.52 to −1.55 turns**, one-directional and dated. Against the *honest* w-indeterminacy of 0.02 turns it is 25× to 75× larger; against the *published* 1.12 turns it is comparable in size but, unlike `w`, it has a sign. **Yes: RNPL strengthens the composition thesis by more than the uncertainty it sits inside** — subject to the evidence caveat that the lap magnitude is fitted on four North American observations and lives on a branch.

---

## 1. What B3's driver-base `N` (+9.4558%) actually embeds

Reproduced from the same two inputs B3 uses — the printed 1H26 regional panel and the FY27 driver scenario — and it reconciles to B3 to six decimals [*derived*, `data/processed/rnpl_short_audit/b3_n_quarterly_trace.csv`]:

| | FY26 | FY27 | growth |
|---|---:|---:|---|
| Nights and Seats `N` | 584.08M | 639.30M | **+9.455783%** (B3: +9.455783%) |
| GBV | $104,400.1M | $116,417.7M | **+11.511084%** (B3: +11.511084%) |
| blended reported ADR | $178.7444 | $182.1007 | **+1.877745%** (B3: +1.877745%) |

**The only exogenous nights inputs in the whole FY27 path are four numbers,** each a single annual rate applied **flat to all four 2027 quarters** [*assumed*, `data/processed/overnight/10_regional_forecast.csv`, period FY27, scenario `base`, via `data/processed/forecast_methods/l1_reconciliation/l1_fy27_regional_scenario_driver.csv`]:

> **NA +6.0 · EMEA +7.0 · LatAm +16.0 · APAC +15.0**

The mechanism is `project_regional()` in `analysis/src/forecast_methods/l1_reconciliation_v2/project.py`: `nights_yoy` is a `{region: pct}` scalar override, so every 2027 quarter grows at its region's single rate. Non-home composition is held flat through 2027, which is why the seats/hotel dilution line carries **0.00** in the v2 build rather than the plan's −0.50pp.

The quarterly shape of that `N` — which B3 never publishes — is the finding:

| quarter | nights y/y | ADR y/y | GBV y/y | source of `N` |
|---|---:|---:|---:|---|
| 2026Q1 | +9.15% | +9.19% | +19.18% | printed panel |
| 2026Q2 | +10.34% | +4.90% | +15.75% | printed panel |
| 2026Q3 | +9.37% | +0.59% | +10.01% | flat regional y/y |
| 2026Q4 | +9.48% | +2.12% | +11.80% | flat regional y/y |
| **2027Q1** | **+9.30%** | +2.62% | +12.16% | flat regional y/y |
| **2027Q2** | **+9.37%** | +1.53% | +11.04% | flat regional y/y |
| **2027Q3** | **+9.53%** | +1.23% | +10.87% | flat regional y/y |
| **2027Q4** | **+9.65%** | +2.09% | +11.94% | flat regional y/y |

**FY27 nights *accelerate* quarter by quarter in B3, +9.30 → +9.65%, and the acceleration is pure regional mix** (LatAm and APAC gaining weight at 16% and 15%). There is no deceleration anywhere. Answering the three parts of the question directly:

- **Lap schedule: none.** Not NA-only, not global — absent. The word "lap" appears in `10_regional_forecast.csv`'s FY27 *rationale* text ("Canada/inbound base effects are fully lapped by 2Q27") but that is a macro base effect, not the product bundle, and it carries no number. The only RNPL mention in the whole file is a 3Q26 NA rationale: "3Q25 was itself the Reserve Now Pay Later acceleration quarter" [*measured*, that file]. It moved no cell.
- **Regional cells:** the four above, from WS10's FY27 base scenario. Bear is NA+3 / EMEA+4 / LatAm+12 / APAC+11 → total +5.82%; bull is NA+8 / EMEA+9 / LatAm+19 / APAC+18 → total +11.48%. B3 carries only the base.
- **RNPL cancellation tail or pull-forward: neither, anywhere.** Confirmed by reading `project.py`, `data.py`, `run.py` and the scenario CSV.

### Comparison with the other four FY27 nights constructions

| construction | FY27 nights | lap treatment | status |
|---|---:|---|---|
| **B3 v2 / WS10 driver base** | **+9.46%** | none | *derived*; the object B3 decomposes |
| 29-bridge FY27 walk | +9.20% | imports WS10 gross, but *labels* 1Q27 "global three-feature lap" | *derived*; `research/notes/overnight/29_q4-fy27-bridge.md` |
| PR #32, NA-only lap | **+8.20%** | US RNPL 3Q26, NA fee + cancellation 4Q26 | *derived*, **fitted on 4 NA observations**, branch-only |
| PR #32, global lap | **+6.40%** | above + ex-NA from 1Q27 (flat −1.75pp) | *derived*, **fitted**, branch-only |
| Jessie plateau-plus-drag | **+6.52%** | lap contributes **0.00**; cancellation drag **−0.90pp** | *derived*, annual only, branch-only |

**The FY27 nights range the RNPL evidence supports is +6.4% to +8.2%, and B3 sits +1.26pp above the top of it** [*derived*, `data/processed/rnpl_short_audit/fy27_nights_lap_grid.csv`].

Three status flags that must travel with that range:

- The 29 bridge is **internally inconsistent**: its 1Q27 row is labelled "global three-feature lap" while its FY27 nights is WS10's lap-free +9.2%. If its own label were taken literally, PR #32 says the number should be +6.4%. That is a **2.8pp unreconciled gap inside the base case**.
- PR #32's **flat −1.75pp from 1Q27 is refuted** by the later D-note: "too large in 1Q27 and about right from 2Q27", because the worldwide go-live (17 Feb 2026, UK 18 Feb, AU/APAC 23 Feb, CA 4 Mar) lands ~48% of the way through the anniversary quarter [*derived*, `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §2.2]. **Do not quote PR #32's 1Q27 cell.**
- Theo's re-based **4Q26 = 7.64%** is built as PR #32's 8.90 − cancellation tail 0.57 + July expansion 0.10 − **ex-NA lap 0.79** [*derived*, `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4]. It is a *4Q26* number and belongs to the FY26 base, not to FY27.

---

## 2. Every channel by which RNPL reaches FY27 revenue growth

`data/processed/rnpl_short_audit/rnpl_channel_ledger.csv` carries the full source string for each row.

| # | channel | FY27 growth points | status | in B3? |
|---|---|---|---|---|
| **a** | volume `N` — product-bundle lap (US 3Q26, NA fee/cancel 4Q26, ex-NA 1Q27 partial / 2Q27 full, Jul-26 types expansion 3Q27) | **−3.06 to 0.00** (central −1.26) | *derived*, fitted on 4 obs | **no** |
| **b** | volume `N` — cancellation tail and rising propensity (~16% → ~17%) | **−0.90 to 0.00** (central −0.30) | *derived* | **no** |
| **c** | volume `N` — pull-forward reversal from lead-time lengthening | **−1.80 to 0.00** (central −0.90) | *unidentified* | **no** |
| **d** | ADR line — RNPL larger-home mix and the pricing residual | **−2.00 to +1.78** (central 0.00) | *assumed* | attribution only, **zero weight** |
| **e** | kernel recognition `κ_w` — longer booking-to-stay lag argues for lower `w` | **−2.34 to 0.00** as published; **−0.02** honest | *derived* | band yes, argument no |
| **f** | fee line × RNPL on unearned fees | **+0.36 to +0.90** (restated central +0.59) | *assumed* | assumed block, **outside the computed dollar** |
| **g** | take-rate timing residual (2Q26 13.26%, FY26 guided flat) | **0.00** — take rate is an output | *measured* | no, correctly |

### (a) The bundle lap — the biggest channel, and the one B3 omits entirely

Management's own attribution is **">200bp nights / ~300bp GBV" (4Q25)**, **"~3 points nights / ~4 points GBV" (1Q26)**, and **nothing in 2Q26** [*measured*, ledger D014 / D032 / D045]. The dated decomposition closes on disclosure: NA bundle 1.35 pts of total nights + ex-NA fee/cancellation 0.70–0.88 + ex-NA RNPL 0.87–1.05 = **2.9 to 3.3 pts** against management's ~3.0 [*derived*, D-note §2.2]. Roll-off dates are the schedule above. Against B3's `N`, the lap is worth **−1.26pp (NA-only) to −3.06pp**, i.e. −1.28pp to −3.11pp of GBV growth.

### (b) Cancellation tail and propensity

Two routes, and they do **not** add. The D1 cohort grid gives a tail of **−0.15 to −0.93pp** per quarter in 3Q26/4Q26 (central cell, +4pt propensity: −0.62 / −0.57), with **46% of 3Q26 and 49% of 4Q26 excess cancellations arriving from earlier booking cohorts** [*derived*, `D1_rnpl_cohort_scenarios.csv`, `D1_cohort_matrix_cancellation.csv`]. Jessie's model instead carries a rising platform rate **17.00% (2026) → 17.75% (2027)** worth **−0.90pp** of FY27 nights growth [*derived*, `nights_simple.csv`]. The 2Q26 10-Q makes the direction official: RNPL bookings "have experienced higher cancellation rates than historic bookings" [*measured*].

Critical correction: **the 16%→17% step is a level already inside printed FY25/FY26 net nights.** It hits FY27 *growth* only if the rate keeps rising. The D-note is explicit that the drag laps too: "the 2025 denominator carries its own RNPL cancellations."

### (c) Pull-forward reversal

The US-cohort calculation is in the repo: 3Q25 US RNPL nights share 3.3–5.0% × a 7–15% lead-time uplift on a 2.2-month mean lead time = **0.17–0.55% of nights booked early**, applied as **−0.2 to −0.4pp** to 3Q26 [*derived*, `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4]. The ex-NA cohort laps in FY27 at a RNPL **nights** share of ~16.7% (21% GBV share ÷ a 1.33× ADR ratio, itself now *derived* from 4 pts GBV on 3 pts nights in 1Q26), i.e. three to five times the US cohort — hence −0.9 to −1.8pp. **Status *unidentified*:** the lead-time *distribution* has never been disclosed, only the mean is anchored, and the 7–15% uplift is assumed (the only quantified lead-time move on record is **−7% in April 2025, pre-RNPL**).

### (d) The ADR line — two-sided, and B3 already sits at the mean-reversion end

This is the channel most likely to be argued backwards. The pricing residual that carried 1H26 stepped **3.70 (4Q25) → 4.38 (1Q26) → 4.85 (2Q26)**, mean **4.61** [*derived*, `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md` §2.1/§2.3]. The mean-reversion case is the 2023–25 mean of **2.40** (IQR 2.04–2.93, full range 0.83–3.70). **B3's own unidentified remainder is +2.83pp** — already at the mean-reversion end. So:

- B3 is **not exposed** to residual mean reversion; it assumes it. Downside to the 0.83 floor is −2.00pp; **upside if persistence holds is +1.78pp.**
- The **attribution gap is the finding**: *neither* ADR note names RNPL anywhere, while the residual stepped +1.15pp across exactly the two quarters management credits the bundle with ~3 pts nights / ~4 pts GBV. The bedroom-count part of RNPL's larger-homes effect sits inside the **+0.63pp** unit-size line (elasticity 0.23, 29 markets, 2Q26); the trade-up-at-same-bedroom-count and lead-time-into-peak-dates parts sit inside the **+2.83pp** remainder, unattributed.
- Basis flag: **+0.63pp is a 2Q26 measurement used as an FY27 annual attribution.** The 2025 *annual* unit-size line is **−0.25pp**. B3 caveat 4 half-concedes this ("n = 1 disclosed quarter").
- **This channel cannot move B3's dollar** unless the driver's "every region +3.00% ex-FX" assumption is restated. Say that out loud or the exhibit implies a sensitivity it does not have.

### (e) `κ_w` and the 10-Q warning — the direction is right, the magnitude is not what B3 says

Longer booking-to-stay lag means more of a quarter's revenue comes from GBV booked **two** quarters ago, i.e. a **lower `w`**, i.e. the **−2.33pp** end of B3's band. Directionally the RNPL evidence does argue for that end, and the 2Q26 10-Q supports it: the timing among GBV, revenue and cash receipts "may become less correlated" — which is a direct issuer statement that the kernel's λ stability should not be expected to hold.

**But the published band is almost entirely an accounting artefact, and this is the audit's most consequential finding** [*derived*, `data/processed/rnpl_short_audit/kappa_anatomy_and_lambda_refit.csv`]:

| λ convention | FY27 growth at w=0.33 | at w=0.50 | at w=⅔ | band | turns of spread |
|---|---:|---:|---:|---:|---:|
| **fixed at w=⅔ (B3's convention)** | +9.180% | +10.355% | +11.523% | **2.343pp** | **1.125** |
| **re-fit at each w (B3 caveat 1)** | +11.480% | +11.495% | +11.523% | **0.042pp** | **0.020** |
| pure lag channel span | — | — | — | 0.023pp | 0.011 |

κ splits into a **lag** channel (−0.0698% to −0.0923%, the real economics) and a **print** channel (+0.0803% to −1.9986%, which is FY26 1H being the printed number while FY26 2H and all of FY27 are kernel). **The print channel carries 99.0% of the published band.** And the printed 1H26 quarters are themselves a read on `w`: at w=0.33 the kernel misses printed 2Q26 by **−11.4%**; at w=⅔ by **−0.16%** — though λ was fit at ⅔, so the non-circular version is the re-fit row, where every `w` reproduces 1H26 inside 0.7%.

**This is independently corroborated at quarterly horizon by `kernel-lambda`**, which does perform the self-consistent re-fit (λ_Q4 re-estimated at each `w`) and finds the entire w ∈ [0.20, 0.80] range moves the 4Q26 print by **$13M, or 0.42%**, and the ⅔-vs-0.38 fight by **$6M, or 0.20%**; the whole mandated band spans **$3,192–3,200M** [*derived*, `05_flatness_cost_4q26.csv` via `docs/revenue-forecast-strategy/05_backtests/kernel-lambda.md` §(b)]. The finding above is the FY27 analogue of that result. **Two packages, two horizons, same answer: re-fit λ and the weight stops mattering.**

**Counter-evidence that must travel with the RNPL lead-time argument.** `kernel-lambda` §(e) fits a free lag polynomial and finds **φ₀ = 0.23 to 0.41** — materially positive, pre-registration **KL-3 FAILED** — with an implied mean lag of **0.95 to 1.18 quarters, *shorter* than the 1.33 a ⅔–⅓ kernel implies**. A shorter mean lag argues for a **higher** `w`, the opposite direction from RNPL. The honest reconciliation: that fit is in-sample, badly identified (the φ vector swings from 0.23/0.60/0.17/0.00 to 0.39/0.04/0.57/0.00 across windows on collinear regressors), and estimated mostly on **pre-RNPL** quarters. RNPL is a *forward* argument that the historical lag will lengthen — which the 10-Q supports and the fit cannot see. **State both. Do not quote the RNPL-lowers-w argument as though the repo's own lag fit agreed with it.**

**Consequence:** the memo's line "the indeterminacy is ~25× the edge" is true only under a convention B3 itself labels an upper bound, and `kernel-lambda` has already shown at quarterly horizon that it does not survive. Restate it, or the first judge who re-fits λ removes the sentence.

### (f) The fee line and unearned fees

B3 carries **+0.90pp** [*assumed*]; `fee-takerate` restates it from primitives at **+0.36pp** (the 11.5pp observed modal listed-price jump) to **+0.59pp** (central θ = 0.833) at half weight, i.e. the carried line is **0.31pp too generous** and is consistent with either a corrected step at ~77% weight or an uncorrected θ = 1 step at ~38%. Two double counts sit here, both named in B3 §2 and neither netted: the migration also subtracts **−0.62pp from FY27 GBV growth** (−1.03pp at the 11.5pp jump), which B3's GBV build does not carry; and the single-fee leg is *inside* the bundle in channel (a).

On the balance sheet: unearned fees **−0.9% y/y in 2Q26** against GBV **+15.7%** [*measured*]. **The two legs cannot be separated on this line.** From 4Q25 funds payable grew *faster* than GBV (+17.3% vs +15.9%) while unearned fees grew half as fast (+7.9%) — only a transfer between the lines produces that sign pattern, and the transfer is the **migration**, not RNPL [*derived*, `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.1]. **Do not lean on the restated +15.4%:** `tracker-backlog` §T1 proves `restated_unearned_q ≡ coverage_norm_season(q) × revenue_{q+1}` to <0.001% on all four rows, and the 2Q26 value uses the **3Q26 guide midpoint**, not a print — **doubly circular** for any 3Q26 forecast. The restated series is **STRUCK as a pin, a feature, and an input** across the programme. Quote the distortion as a *description* of the gap, never as a corrected series.

### (g) Take rate

2Q26 printed **13.26%** [*measured*, `02_kpi_panel_quarterly.csv`], against 13.17% (2Q25) and 12.96% (2Q24) — a **+9bp** move; 1Q26 was **−10bp**, 4Q25 **−47bp**, 3Q25 **−69bp**. The letter attributes it to "the timing of when guests booked their travel and when guests stayed — a dynamic that reflects the growth of Reserve Now, Pay Later"; FY26 take rate is guided flat "accounting for the timing of bookings versus check-in with Reserve Now, Pay Later" [*measured*].

`fee-takerate` §5 carries **RNPL at 0 / 0 / 0 bp** in its FY27 take-rate build — *"timing, not a take-rate lever — zero by construction, flagged"* — and that is the correct treatment. Two supporting facts: a 40% migrated revenue share at a +1.8% cohort uplift is worth about **+7bp on a 13.3% base, well inside the ±50–70bp the seasonal mix moves it**, so **the absence of a take-rate move through 2Q26 is not evidence the migration is not flowing**; and the regression of Δtake on migrated revenue share is a null (n = 20, slope −105.7bp, t −0.24, permutation p 0.730, R² 0.003). **Take rate is `revenue ÷ GBV`, an output.** Any take-rate "lever" added to a build that already models revenue and GBV is counted twice; **0 of 8 registered take-rate objects beats a plain seasonal naive on either window.**

### Every place the lap could be counted twice

1. **(a) vs (f) — the fee leg.** The "+3 pts nights / +4 pts GBV" is the **bundle**: RNPL + cancellation redesign + **single fee**. Subtract a bundle lap from `N` *and* carry the fee line and the fee leg is in twice. `03_insider_mechanics.md` §1.6 says it in terms: **"Anyone subtracting 3 points for a US RNPL anniversary is double-counting."**
2. **(a) vs (b) — two routes, same total.** PR #32 global gives **+6.42%** with *no* cancellation term; Jessie gives **+6.52%** with a lap of *zero* and a −0.90pp cancellation term. **0.10pp apart, decomposed oppositely.** Adding them gives ~+5.5% and is a double count.
3. **(c) vs (e) — same object, two sides.** A booking-dated pull-forward and a kernel lead-time shift are the same phenomenon. Price it in `N` **or** in `κ_w`, never both.
4. **Theo's 4Q26 vs PR #32's 1Q27.** Theo's 7.64% already takes **−0.79pp** for the ex-NA lap in 4Q26; PR #32 defers the whole ex-NA lap (−1.75pp) to 1Q27. Chain the two and the ex-NA fee/cancellation leg is counted twice.
5. **The additive sum is the tell.** (a)+(b)+(c) sum to −5.76pp, which puts FY27 nights at **+3.70%** — below every published construction. That arithmetic is itself evidence of overlap; quote the **range**, not the sum.
6. **Narrative vs arithmetic.** `08_THESIS_MAP.html` §01 and §05 both assert a "product-bundle lap" in the composition story while the number underneath it carries none. Either put the lap in `N` or strike the claim.
7. **Stale attribution values in the thesis map.** `08_THESIS_MAP.html` still carries **geo mix −1.5pp** and **bedroom nights +0.46pp**; B3 v2 supersedes both with **−1.09pp** and **+0.63pp**. Fix before the deck.

---

## 3. RNPL-aware FY27 quarterly phasing

At `w = ⅔`. `κ_q` is the quarterly recognition term (reported revenue growth less GBV growth). FY26 comps are **revenue** growth: 1Q26 and 2Q26 are printed; 3Q26 and 4Q26 are **forecasts**, from different notes, and this is stated rather than netted [*measured* / *derived*, `data/processed/rnpl_short_audit/notes_and_provenance.csv`].

| | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---:|---:|---:|---:|
| **FY26 comp (revenue)** | **+17.9%** | **+16.5%** | **+16.6%** | **+12.0%** |
| B3 nights | +9.30 | +9.37 | +9.53 | +9.65 |
| B3 ADR | +2.62 | +1.53 | +1.23 | +2.09 |
| B3 `κ_q` | −0.29 | +0.84 | +0.56 | −1.00 |
| **B3 reported revenue growth** | **+11.88** | **+11.89** | **+11.44** | **+10.93** |
| RNPL nights, NA-only lap | +8.05 | +8.12 | +8.27 | +8.39 |
| **RNPL revenue, NA-only lap** | **+10.59** | **+10.61** | **+10.16** | **+9.65** |
| RNPL nights, global lap | +6.98 | +6.07 | +6.23 | +6.35 |
| **RNPL revenue, global lap** | **+9.50** | **+8.53** | **+8.09** | **+7.56** |
| **Street FY27 phased like FY26** | **+10.8 to +11.2** | **+10.8 to +11.2** | **+10.8 to +11.2** | **+10.8 to +11.2** |

Lap phasing [*assumed*, sourced]: the **NA leg is flat** in every FY27 quarter (PR #32's `na_contribution_delta_pts = −0.98` is constant), because US RNPL lapped in 3Q26 and the NA fee/cancellation legs in 4Q26; the **ex-NA leg is partial in 1Q27 (0.52 of full)** and full from 2Q27, per the dated go-lives.

**What the Street's FY27 implies if phased like FY26.** Proportional phasing is flat by construction, and that is exactly the point: **the Street's $15,740–15,790M is a ~+11% line in every quarter of 2027, including 1Q27 against a +17.9% comp and 2Q27 against a +16.5% comp.** The gap to the RNPL-aware path [*derived*]:

| gap, pp | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---:|---:|---:|---:|
| NA-only lap vs Street | −0.25 to −0.60 | −0.23 to −0.58 | −0.67 to −1.02 | −1.18 to −1.54 |
| global lap vs Street | −1.34 to −1.69 | −2.30 to −2.65 | −2.74 to −3.09 | −3.27 to −3.62 |

Two caveats on shape. First, **at `w` below ⅔ the quarterly path is not economically interpretable**: at w=0.33 the kernel prints 1Q27 **+15.68%** and 2Q27 **−0.84%**. B3 caveat 6 concedes 2027Q2 is "the wide quarter"; the quarterly grid shows how wide. Second, this contradicts the 29 bridge's FY27 shape (**+9.9 / +10.7 / +11.9 / +13.4**, accelerating on an *assumed* −1.2/−0.7/+0.4/+1.3 nights spread). **1Q27 is precisely where a global lap bites hardest, so an accelerating FY27 path is the least defensible cell in that walk.**

### Turns, against the w-indeterminacy

At **+0.48 EV/EBITDA turns per point of forward revenue growth, applied once**. Street-implied growth is each vendor's own FY27 ÷ own FY26: **+11.32% to +11.63%** [*measured*, `fy27_street_edges_v2.csv`].

| | growth edge vs Street | **turns** |
|---|---:|---:|
| B3 as published, w = ⅔ | −0.11 to +0.20pp | −0.05 to +0.10 |
| B3 + **NA-only** RNPL lap, w = ⅔ | −1.08 to −1.39pp | **−0.52 to −0.67** |
| B3 + **global** RNPL lap, w = ⅔ | −2.91 to −3.22pp | **−1.40 to −1.55** |
| memo: `w` band **as published** | 2.343pp of spread | **1.12** |
| memo: `w` band **λ re-fit** | 0.042pp of spread | **0.02** |

**Does RNPL strengthen the composition thesis by more than the uncertainty it sits inside? Yes — plainly.** On the honest accounting of `w`, RNPL is **25× to 75× the kernel-weight uncertainty**. Even on B3's published (upper-bound) convention, RNPL is comparable in magnitude and **strictly better in kind**: `w` is symmetric, undated and unobservable, while the lap is one-directional, tied to disclosed go-live dates, and testable on 5 November. The honest counterweight is not `w` at all — it is the kernel's own strict-PIT walk-forward error of **3.19–3.23pp of growth**, which dominates everything and which nothing in this note reduces.

The evidence discount is real and must be stated: the lap magnitude is **fitted on four NA observations**, PR #32's 1Q27 cell is refuted, and both low-end constructions are **unmerged branch artefacts with no registered row**.

**And the honest competitor for memo space is not `w` — it is the dollar.** B4's adopted FY27 FX is **+0.5pp** (Φ × 0.851, spot held; +0.40pp at Φ × 0.653), against B3's flat-spot carry of **0.00pp** and `fx-lag`'s rival **+0.2pp**. But a ±1 sd parallel dollar move (±5%) swings FY27 FX to **+2.8pp / −1.8pp = $657M of FY27 revenue** [*derived*, `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md` §4]. **The FY27 dollar path is worth roughly twice the RNPL lap and is not forecastable.** Say that before anyone else does. (B4 also rejects the 29 bridge's FY27 FX step as "the same double subtraction one year out"; B3's zero carry is the conservative reading and is the one to publish.)

---

## 4. The synergy map — what plugs into what

| RNPL object | plugs into | what it adds | what a judge needs to see |
|---|---|---|---|
| **Statement ledger** — 60 statements, 33 official, 57/57 file-sourced quotes verbatim-verified (`data/processed/overnight2/D/rnpl_statement_ledger.csv`) | **B3 Table 1**, the volume line; and the composition narrative in `08_THESIS_MAP.html` | Turns "product-bundle lap" from an assertion into **dated, quoted, source-classed evidence**, with the four basis traps named (the two 70% figures are different statistics; the 16→17% remark is hedged three ways; 8 of 60 statements are night-weighted; `06_fee_timeline.csv` mis-attributes fee penetration to the letters) | The **decomposition closing on disclosure**: NA 1.35 + ex-NA fee/cancel 0.70–0.88 + ex-NA RNPL 0.87–1.05 = **2.9–3.3 pts vs management's ~3.0**. That is the credibility moment — an independent build reproducing management's own number from dated go-lives. |
| **Cohort engine** — monthly booking cohorts Jan-24 to Jun-27, 2,025-cell grid, two-run design so the 2025 denominator carries its own RNPL cancellations (`D1_rnpl_cohort_scenarios.csv`) | **B3's `N`** (as a lap term it does not have) and **B2's GBV_3Q26 input** | Prices the cancellation tail at **−0.10 to −1.37pp (3Q26)** / **−0.08 to −1.36 (4Q26)**, and sizes the tail: **46% of 3Q26 and 49% of 4Q26 excess cancellations come from earlier booking cohorts** | The engine's own **adverse finding**, said first: *"the anniversary is two to fifteen times the cancellation drag"*, and that the drag laps too. A judge who finds that in your appendix instead of your mouth discounts everything else. |
| **Balance-sheet exposure** — joint solve for unpaid share `u` and migration share `m` on unearned fees + funds payable (`analysis/src/rnpl_balance_sheet_bridge.py`) | **The take-rate hinge** and **B3's fee line (f)** | Replaces the 40M illustrative RNPL exposure with **7–19M live unpaid nights / $1.6–4.7bn of unpaid GBV at 30 Jun**, and separates the migration leg (`m` = 8.0–8.5% of GBV in 1H26) from the RNPL leg | That the exposure is **too small to carry a one-point haircut from the opening backlog** — it would need a 7–17pt revision in conditional cancellation probability. The honest read shrinks the claim, which is why it is worth showing. |
| **Pre-registered 5 Nov thresholds** — 7 rows (`D1_prereg_thresholds.csv`) | **B2's Q4 guide grid** (row 5: the 4Q26 nights guide) and **the take-rate hinge** (the 3Q26 ≥18.10% pre-registration) | Converts a narrative into a **dated, falsifiable card written before the print** — the single most persuasive thing in a student pitch | Row 7 (does management repeat a quantified bundle figure?) and the **replacement of row 3**: unearned fees can be tripped by the migration alone (−2% to −17% with zero cancellation effect), so **score funds payable** — +5% to +11% y/y is deferral on schedule, below +3% means more adoption, not more cancellation. And that the take-rate threshold **already clears at the no-fee counterfactual of 18.35%**, so it discriminates on GBV, not on the fee. |
| **The κ / λ finding in this note** — `kappa_anatomy_and_lambda_refit.csv` | **B3 Table 3** and **the memo's central rhetorical sentence** | Removes the ±1.12-turn counterweight that currently dwarfs everything, so the composition argument (RNPL lap, geo mix, FX) becomes the *largest* identified term rather than the second-largest | Two lines of arithmetic: re-fit λ at each `w`, band collapses from 2.343pp to 0.042pp — and `kernel-lambda`'s independent quarterly version of the same result ($6M on the 4Q26 print). |

---

## 5. Method

1. Re-ran `analysis/src/forecast_methods/l1_reconciliation_v2/run.py`; it reproduces B3 v2's grid and identity checks.
2. Rebuilt B3's `N` and ADR path quarterly from `l1_panel_quarterly.csv` (1H26 printed) + `l1_fy27_regional_scenario_driver.csv`, reconciling to B3's annual pair to 1e−6.
3. Read `project.py` / `data.py` / `run.py` to establish that `nights_yoy` is a per-region scalar with no time index — the basis for the "no lap schedule" finding.
4. Re-implemented `seasonal_lambda` and `kernel_kappa` so λ could be **re-fit at each `w`**, which B3's caveat 1 names but does not compute. This is the only new estimation in the note.
5. Priced each channel off repo primitives only; no new external data.
6. Phased the lap on the dated go-lives, NA leg flat and ex-NA leg partial-then-full.

## 6. What this can and cannot identify

**Can:** that B3's `N` contains no lap, cancellation or pull-forward term (read from code and data, not inferred); the exact split of `κ_w` into lag and print channels; that the published `w` band collapses to 0.042pp under a self-consistent λ re-fit; that B3's ADR remainder already sits at the pricing residual's mean-reversion end; the double-count map above.

**Cannot:** separate the RNPL deferral leg from the single-fee migration leg on unearned fees — the balance sheet cannot see it, and a cancelled RNPL booking was never recorded on either line; the night-weighted RNPL cancellation curve, the platform eligibility share, and the booking-to-stay lag **distribution** (only the ~2.2-month mean is anchored); how much of the +2.83pp ADR remainder is RNPL; whether the bundle's ~3 pts split NA/ex-NA at 40%, 50% or 70%; and — because λ was fit at w=⅔ — whether the 1H26 prints genuinely favour ⅔ or merely reflect the convention.

## 7. Next evidence, in order

1. **Re-fit λ at each `w` inside `l1-reconciliation-v2` and republish the band.** It is ~20 lines and it changes the memo's central sentence. Add to the RED_TEAM must-fix list.
2. **Put a lap term in `N`, or strike "product-bundle lap" from the thesis map.** Cheapest version: carry B3's decomposition at three lap schedules (none / NA-only / global) as a three-column exhibit.
3. **5 Nov, threshold 7:** does management repeat a quantified bundle contribution? None given, or ≤1.5 pts, supports the lap; ≥2.5 pts weakens it. This is the highest-information-per-ambiguity RNPL row.
4. **Score funds payable, not unearned fees,** on 5 Nov: +5% to +11% y/y is deferral on schedule; below +3% means the unpaid book is larger than modelled. The unearned-fees threshold can be tripped by the fee migration alone (−2% to −17% with zero cancellation effect). Replace row 3 of `D1_prereg_thresholds.csv` before the card freezes.
5. **Ask IR for the unbilled confirmed-bookings balance** (disclosed as a concept in the FY2025 10-K) and for an RNPL GBV share *and* nights share for the same quarter. Those two close the widest assumptions in the grid.
6. **Reconcile the 29 bridge's 1Q27 lap label with its FY27 nights number** — a 2.8pp gap inside the base case.
7. **Update `08_THESIS_MAP.html`** geo mix to −1.09pp and bedroom nights to +0.63pp.

## 8. Files

**Written by this pass (new only):**
- `docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md` — this note
- `analysis/src/rnpl_short_audit/fy27_rnpl_channels.py`
- `data/processed/rnpl_short_audit/b3_n_quarterly_trace.csv`, `fy27_nights_lap_grid.csv`, `kappa_anatomy_and_lambda_refit.csv`, `kernel_1h26_reconstruction_by_w.csv`, `rnpl_channel_ledger.csv`, `fy27_quarterly_phasing_b3.csv`, `fy27_quarterly_phasing_rnpl_aware.csv`, `turns_vs_street_and_w_band.csv`, `notes_and_provenance.csv`, `run_log.txt`

**Read (unmodified):** `docs/revenue-forecast-strategy/05_backtests/{B3_FY27_DECOMPOSITION,RED_TEAM,l1-reconciliation,fee-takerate,B2_Q4_GUIDE_EXHIBIT,B4_FX_EXHIBIT,kernel-lambda,tracker-backlog}.md`; `docs/revenue-forecast-strategy/{07_MORNING_REPORT.md,08_THESIS_MAP.html}`; `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md`; `docs/RNPL_HANDOFF.md`; `analysis/src/forecast_methods/l1_reconciliation_v2/*`; `data/processed/forecast_methods/l1_reconciliation{,_v2}/*`; `data/processed/overnight/{02_kpi_panel_quarterly,10_regional_forecast}.csv`; `data/processed/overnight2/D/*`; `research/notes/overnight/{10_regional-and-segment-decomposition,12_valuation-multiple-regime,29_q4-fy27-bridge}.md`; `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`; `research/notes/{2026-09-07_adr-decomposition,2026-09-10_nights-baseline-reconciliation,2026-09-11_rnpl-balance-sheet-and-q3-bridge}.md`; `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md`; `git show origin/krish/nights-quarterly:research/notes/nights_quarterly.md`; `git show origin/jessie/backlog-conversion:research/notes/choice_nights_driver.md`.

---

*Research note for the Citadel Intercollegiate Stock Pitch. Exploratory. Not investment advice.*

## Reproduce

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/rnpl_short_audit/fy27_rnpl_channels.py
```
