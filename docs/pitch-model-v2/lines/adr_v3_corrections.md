# ADR line v3 — the audit's corrections, what each one moves, and what is still open

**23 September 2026.** Krish (ADR owner); for Theo's review. Source: the adversarial audit
`docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md` (receipts in `data/processed/pitch_model_v2/receipts/ADR_AUDIT/`).
Engine: `analysis/src/pitch_model_v2/adr_engine_v3/`, a copy of `adr_engine` with one commit per fix. `adr_engine`
and its tracked outputs are untouched. Numbers: `data/processed/pitch_model_v2/adr_engine_v3/v3_vs_v2_*.csv`.

```bash
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.adr_engine_v3.run --no-posterior --no-workbook --no-refresh-prices   # exit 0
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.los_nowcast.run --workers 3                                          # fix (k) input, exit 0
PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests analysis/src/pitch_model_v2/los_nowcast/tests -q   # 59 pass
```

## 1. The line after the corrections

The recommended FX leg is the card-method midpoint: the average of the V0 identity and the V2 euro-only fit, used
for 3Q26 and 4Q26 only (fix j). The identity (v2's leg) and the registered fitted variant V1 are shown as labelled
alternatives.

Fixes (k) and (l) were added later on 23 Sep:
- **(k)** LOS is measured, not carried;
- **(l)** the World Cup premium is taken out of the carried core;
- **(m)** 2027 uses the core's expanding mean instead of the 2Q26 carry (`core_2027_prereg.md`).

The note is `los_nowcast.md`. The table shows the line with all fixes.

| | v2 as filed | **v3 (midpoint FX)** | v3, identity FX | v3, V1 FX | Street |
|---|---:|---:|---:|---:|---:|
| 3Q26 FX (pp) | +0.42 | **−0.41** | +0.42 | +0.03 | |
| 3Q26 ADR | $177.68 | **$175.66** | $177.07 | $176.41 | $177.06 |
| 3Q26 P(print ≥ Street) | 0.645 | **0.207** | 0.502 | 0.352 | |
| 4Q26 FX (pp) | +0.51 | **−0.37** | +0.51 | +0.28 | |
| 4Q26 ADR | $173.03 | **$170.96** | $172.44 | $172.05 | $171.33 |
| 4Q26 P(print ≥ Street) | 0.701 | **0.453** | 0.636 | 0.590 | |
| FY27 ADR | $185.21 | **$181.56** | | | none exists |
| half-band 3Q26 / 4Q26 (±1σ) | 0.978 / 1.932pp | 0.999 / 1.892pp | | | |

Through fix (j) only, the line read 3Q26 $176.18 (P 0.31) and 4Q26 $171.46 (P 0.52). Fix (k) takes about $0.43 off
each quarter, and fix (l) about $0.09 (`los_wc_ladder.csv`). Fix (m) leaves 2026 alone and lowers FY27 from
$184.00 to $181.56.

**The trajectory with all fixes** (midpoint FX for 2026, the identity at held spot for 2027):

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 |
|---|---:|---:|---:|---:|
| ex-FX y/y | +2.96% | +2.43% | +0.95% | +1.44% |
| FX (pp) | −0.41 | −0.37 | −0.37 | −0.43 |
| reported y/y | +2.55% | +2.06% | +0.58% | +1.01% |
| ADR | **$175.66** | **$170.96** | **$187.91** | **$185.59** |
| ±1σ band | $173.95–177.37 | $167.79–174.13 | $183.22–192.60 | $179.91–191.28 |
| core rule | carry 3.80 | carry 3.80 | mean 2.46 | mean 2.46 |
| Street | $177.06 | $171.33 | none | none |

**What this means for the pitch.**

- **3Q26 ADR is likely below the Street** on the best-tested FX estimate ($175.66, P 0.21). The three FX
  estimates span $175.7–$177.1 around a Street of $177.06.
- **4Q26 sits $0.37 below the Street** on the recommended leg ($170.96, P 0.45), and $0.7–$1.1 above it on the
  identity or V1.
- **The FX estimate is now the largest single swing in the ADR line.** The 5 Nov print is the test.

**The 4Q26 ladder.** 4Q26 ADR under each rule, with all fixes:

| rule | v3 (midpoint FX) | identity FX | V1 FX | vs Street (v3) |
|---|---:|---:|---:|---:|
| core mean reversion (to the core's own mean) | $168.40 | $169.88 | $169.49 | −$2.93 |
| AR(1) fitted on the core | $169.13 | $170.61 | $170.23 | −$2.20 |
| lap-only (every 2025–26 step laps) | $169.71 | $171.19 | $170.80 | −$1.62 |
| tilt B (retired) | $170.27 | $171.75 | $171.36 | −$1.06 |
| sub-regional country mix (netted) | $170.88 | $172.36 | $171.97 | −$0.45 |
| **base** | **$170.96** | **$172.44** | **$172.05** | **−$0.37** |
| measured origin–destination tilt | $171.28 | $172.76 | $172.37 | −$0.05 |
| fee-migration K line | $171.58 | $173.06 | $172.68 | +$0.25 |
| card v3 carry, no lap | $172.70 | $174.18 | $173.79 | +$1.37 |

**The binding negative, restated.**
- **On the identity or V1 FX,** no mix-only row reaches the Street, as the audit found.
- **On the recommended midpoint FX,** the base is $0.37 below the Street. The measured LOS change (fix k, −$0.42)
  and the World Cup row (fix l, −$0.08) together moved it from $0.13 above.
- **Every composition row on that leg sits at or below the Street.** Only the K line and the card's no-lap carry
  sit above.
- **So:** the FX estimate still decides the sign of 4Q26 against the Street, but on the best-tested FX, measured mix
  now points below it.

## 2. The corrections, one commit each

| fix | what was wrong | what changed | 3Q26 / 4Q26 effect |
|---|---|---|---|
| **(a) FX V1** | V0's point-in-time error rises with its own LatAm component in every promotion cell (slope +0.55 to +0.69, p 0.002–0.012); 3Q26 is a LatAm-heavy quarter. | V1, the registered fitted variant (LatAm 0.41, EMEA 1.20), is computed and carried everywhere. | V1: 3Q26 +0.03pp, 4Q26 +0.28pp |
| **(b) FX falsifier** | "Printed FX inside [0.36, 0.48] or withdraw" fails a correct identity about 88% of the time (±0.5pp rounding). | `adr_fx_prereg.md` §11 is appended: a comparative interval score of the named candidates; V0 is withdrawn only if it scores worst. Scorer: `fx_falsifier.py`. §12 adds the rule for the midpoint leg (fix j). | Changes the 5 Nov test |
| **(c) one construction** | The core is ex-FX minus the H terms. The forward added geo from the bucket method (+0.132pp above H at 2Q26, one-signed since 4Q24) and unit size from workstream I (+0.166pp). The H 2Q26 capacity came from dumps in which 2Q26 was still partly reviewed. LOS switched from H's assumed 0.30 to I's measured 0.056. | Each forward term is put on the core's footing. Case A carries LOS at its in-core value; case B (the LOS drop is real) is the bound. | Base −0.054pp, −$0.09 (case B: −$0.50) |
| **(d) downside rows** | Mean reversion used the residual's mean (2.398), not the core's (2.272). "AR(1) on core" used the residual's AR(1) (implied mean 2.96). | The core's own mean; an AR(1) fitted on the core (ρ 0.465, mean 2.41). | MR −$0.30; AR(1) −$1.33 (4Q26, same FX) |
| **(e) sub-regional row** | Added the full forward term on top of a core that already holds 2Q26's. | Adds the change from 2Q26, read by label. | Row +$0.17 |
| **(f) bundle band** | 0.8–1.2pp is narrower than management's rounding (0–1.5, 0–2.0). | 0.5–1.5pp | Half-band +0.03 to +0.05pp |
| **(g) reconciliation** | "Compatible with the identity": four clusters give no valid p-value, and 76% of LatAm's slope is Brazil's hotel CPI. | "Not established". The annual 10-K reconciliation stands. | Wording |
| **(h) labels** | 4Q27 FX 0.000 (a spot-held artefact) unlabelled where it flows into FY27; the band unlabelled. | Labelled in the docs, the income-statement note and `adr_path.csv`. | Labels |
| **(i) factual errors** | "Core is 40% of ex-FX" (it is 116–138%), "lap-only crosses", "RNPL not named in a filing until 2Q26", "EMEA's first sub-50% English quarter 2Q26", "within 0.13pp", thesis sentence 3, the V0 bias range. | Corrected in place, with the evidence. | Text |
| **(j) FX leg** | The identity was the leg because the V0 registration promotes it; accuracy was never compared with the card's method on the same footing. | **Recommended leg: the card-method midpoint (V0 + V2)/2 for 3Q26 and 4Q26.** It beats every variant point in time in all four promotion cells (section 3). 2027 keeps the identity: see section 3 on V2's intercept. `config.FX_LEG = "identity"` restores the v2 leg. | 3Q26 −$1.41, 4Q26 −$1.48 against the identity |
| **(k) LOS measured** | LOS was held at H's assumed 0.30 in 2Q26, 3Q26 and 4Q26, so the forecast assumed it never changes. | Measured from the calendars already in the repo: the change in the LOS term from 2Q26 to 3Q26 bookings, on a new-bookings flow and I2's stock, both reproduced (gate passed to 0.0003pp). All four constructions: −0.17 to −0.38pp; point −0.253. Forward LOS 3Q26 = 4Q26 = +0.047pp. Pre-registered (`los_nowcast_prereg.md`); note `los_nowcast.md`. `exfx.LOS_NOWCAST=False` reverts. | 3Q26 −$0.43, 4Q26 −$0.42 |
| **(l) World Cup out of the core** | The carried 2Q26 core holds the World Cup booking premium (audit F5). | −0.05pp in every forward quarter, plus the 2Q27 lap of the 2Q26 base. Band 0 to the 0.20pp bound. A post-hoc translation (`docs/worldcup-premium/RESULTS.md` §3b). The World Cup's LOS effect was also tested: +0.46pp in host cities, 0.005pp globally, not added. `exfx.WC_CORE_ADJ=False` reverts. | 3Q26 −$0.09, 4Q26 −$0.08 |
| **(m) 2027 core rule** | The core was carried at its 2Q26 level (a 14-quarter high) into 2027. The core's point-in-time record favours its expanding mean from 3 quarters out: the audit found this at h = 3–4 in both windows (post-hoc). | Carry at h ≤ 2. The expanding mean (2.46, 2Q26 net of the World Cup) at h = 3–4, and at h = 5 / 6 only where a newly registered test passes (`core_2027_prereg.md`, `core_horizon.py`, which reproduces the audit's h = 1–4 exactly). h = 5 passed (0.81, n 6). h = 6 passed on the letter at 0.99 (n 5), which is effectively a tie. On the mean quarters, LOS enters as its own expanding mean (0.279), bounded by the carried 3Q26 read (0.047). The band's core term is the mean rule's own RMSE. `exfx.CORE_HORIZON_RULE=False` reverts. | 2026 unchanged; 1Q27 −$2.54, 2Q27 −$2.50, FY27 −$2.44 |

## 3. The FX leg: the evidence behind fix (j)

**The point-in-time test.** This is the engine's own walk-forward, same origins and same windows, with the midpoint
added as a scored variant (`fx_scores.csv`). Each cell is the RMSE ratio to the naive carry; lower is better.

| variant | W1 O1 | W1 O2 | W1 O3 | W2 O1 | W2 O2 | W2 O3 |
|---|---:|---:|---:|---:|---:|---:|
| **midpoint (V0 + V2)/2** | **0.390** | **0.223** | **0.199** | 0.553 | **0.247** | **0.201** |
| V2 euro-only OLS | 0.399 | 0.270 | 0.281 | **0.525** | 0.268 | 0.272 |
| V0 identity (v2 leg) | 0.437 | 0.344 | 0.303 | 0.625 | 0.383 | 0.317 |
| V1 fitted pass-through | 0.497 | 0.375 | 0.337 | 0.672 | 0.347 | 0.290 |

**Reading the test.**

- **The midpoint wins every promotion cell** (O2 and O3, both windows), with bootstrap 90% upper bounds of
  0.25–0.38. At quarter start (O1), which is 4Q26's footing today, it is best on W1 and second on W2.
- **Why it works:** its two components miss in opposite directions. The identity over-predicts when LatAm
  currencies strengthen; the euro fit under-predicts in the same quarters. Averaging cancels part of both.
- **Its own bias is −0.06 to −0.28pp**, a slight lean toward too low an FX.

**Caveats, stated against the choice.**

1. **The comparison was run on 23 Sep, after the audit, not pre-registered.** It survives both windows (the repo's
   rule), and the card had already chosen this method on 11 Sep in-sample (DEC-0027).
2. **The choice lowers ADR.** 3Q26 falls $1.41 and 4Q26 $1.48 against the identity, which helps the short. It is
   made on the test result alone; the table above is the defence.
3. **It does not break a pre-registration.** The V0 registration governs whether the *identity* has skill; it does
   not oblige the owner to adopt it. DEC-0034, which proposed replacing the card's FX with the identity, was never
   adopted, so keeping the card's method is the incumbent choice (DEC-0027), refreshed on current data.
4. **2027 keeps the identity.** The midpoint was tested only on the current quarter or the next. V2's −0.57pp
   intercept has no translation content and would drag every spot-held 2027 quarter about 0.28pp. For 2027 every
   variant is an untested spot-held extrapolation, and the identity at least returns zero when rates do not move.

**Why the identity over-weights LatAm (step 2, `krish/cc-search-price`).**

- **Conversion is exact.** Airbnb converts the host's price at spot, with a margin inside ±25bp and no lag (I6b,
  1,796 same-stay pairs). Because of that, the guest's paying currency cannot matter.
- **Hosts price locally.** Brazilian hosts price in BRL (I6c).
- **So the miss is a weighting error:** the LatAm share and basket are too large. Pinning it down needs a LatAm
  country mix of Airbnb's GBV, which is not in the repo. That is post-memo work.

**FX line v2 is not carried.** That construction (`docs/adr-card-v3_1/FX_LINE_V2.md`) failed its own
pre-registered test (RMSE 0.82 against the midpoint's 0.42). Its weights are same-quarter revenue shares, which are
stay-dated, while ADR FX is booking-dated. Its 4Q26 +1.66pp should not enter the risk section.

## 4. Evidence from the other ADR thread that this line uses or deliberately does not

| item | where | used here? |
|---|---|---|
| Card v3.1: the unit-size mismatch comes from review accrual (2Q26 held 14% fewer reviews in the June/July dumps); routes A and B agree within 0.01pp (card v3 −$0.28) | `docs/adr-card-v3_1/CARD_V3_1.md` | **Yes**, as fix (c)'s unit leg (route-B equivalent). Theo's ladder shows the card row at +$0.13 rather than −$0.28, because case A also carries LOS at 0.30. That is open choice 2. |
| Unit-size elasticity 0.53–0.55 (pitch 0.59) | `docs/cc-search-price/I3b_elasticity_layer.md` | No change: under 2 cents once re-solved |
| New listings price +3.5% (±1.2) above comparable incumbents | `docs/cc-search-price/I4c_targeted_sample.md` | No term here. It weakens the supply-dilution argument for core reversion. |
| Listing-age term v2 | `docs/adr-card-v3_1/LISTING_AGE_V2.md` | No change (about −$0.02) |

## 5. Open choices for Krish and Theo

1. **Adopt v3 as line 2** (DEC-0043): fixes a and c–f. Recommend yes. Each fix reverts alone.
2. **FX leg** (DEC-0048, superseding DEC-0044): the midpoint for 3Q26 and 4Q26, with the identity and V1 as
   labelled alternatives. Recommend yes, on the test in section 3. The alternative keeps the identity: 3Q26 +$1.41,
   4Q26 +$1.48.
3. **LOS in fix (c): resolved by fix (k).** A same-construction 2Q26 LOS now exists. The measured change (−0.253pp) lands where case B had assumed (forward +0.047 vs I's +0.056). Recommend adopting (k) (DEC-0049).
4. **The 2027 core rule: fix (m)** (DEC-0051). Carry at h ≤ 2, the expanding mean at h ≥ 3. It was registered
   before the h = 5 / 6 test was run, and adopted at h = 3–4 on the audit's already-seen result, labelled post-hoc.
   FY27 is $181.56. 4Q27's mean-vs-carry margin is a tie (0.99). Recommend adopting it, and stating the tie.
5. **World Cup row: fix (l),** 0.05pp point and 0.20pp bound, from 3Q26 (the tournament ended 19 Jul) with the 2Q27 lap. Recommend adopting (DEC-0050), labelled post-hoc. `krish/worldcup-premium` still needs committing so the source is on a branch.
6. **Workbook.** `model/ABNB_official_model.xlsx` still reads `adr_engine` (v2). It needs an approved rebuild.
7. **Posterior.** Not re-run (no PyMC here); its draws are seeded from v2.
8. **FX refresh.** Everything uses FRED through 18 Sep. Refresh before the memo (`run.py --fetch` writes a new
   dated file; point `config.FX_DAILY` at it).

## RESUME

The next agent should read this note, then `git log origin/main..krish/adr-audit-fixes`: one commit per fix.

- **Switches** reproduce v2 behaviour: `config.FX_LEG = "identity"`, and in `exfx.py` `CONSTRUCTION_FIX`,
  `CORE_FIX`, `SUBGEO_NETTING`, `LOS_NOWCAST` (k), `WC_CORE_ADJ` (l) and `CORE_HORIZON_RULE` (m).
- **LOS nowcast:** `los_nowcast.md` RESUME. Rerun on the September calendars before 5 Nov, after amending the
  pre-registration.
- **On 5 Nov:** recompute the V0, V1 and midpoint points at O3. Then run
  `fx_falsifier.score_print(y, FF.CANDIDATES_3Q26_J, leg="midpoint_refreshed")` with the printed ADR-FX pp, and apply
  the §12 ratio rule.
- **Choice 2 (FX) moves 2026 numbers; choice 4 (fix m) moves 2027.** Refresh FRED before the memo.
