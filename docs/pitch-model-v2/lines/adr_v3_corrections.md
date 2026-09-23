# ADR line v3 — the audit's corrections, what each one moves, and what is still open

**23 September 2026.** Krish (ADR owner); for Theo's review. Source: the adversarial audit
`docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md` (receipts in `data/processed/pitch_model_v2/receipts/ADR_AUDIT/`).
Engine: `analysis/src/pitch_model_v2/adr_engine_v3/`, a copy of `adr_engine` with one commit per fix. `adr_engine`
and its tracked outputs are untouched. Numbers: `data/processed/pitch_model_v2/adr_engine_v3/v3_vs_v2_*.csv`.

```bash
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.adr_engine_v3.run --no-posterior --no-workbook --no-refresh-prices   # exit 0
PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests -q                           # 48 pass
```

## 1. The line after the corrections

The recommended FX leg is the card-method midpoint: the average of the V0 identity and the V2 euro-only fit, used
for 3Q26 and 4Q26 only (fix j). The identity (v2's leg) and the registered fitted variant V1 are shown as labelled
alternatives.

| | v2 as filed | **v3 (midpoint FX)** | v3, identity FX | v3, V1 FX | Street |
|---|---:|---:|---:|---:|---:|
| 3Q26 FX (pp) | +0.42 | **−0.41** | +0.42 | +0.03 | |
| 3Q26 ADR | $177.68 | **$176.18** | $177.59 | $176.93 | $177.06 |
| 3Q26 P(print ≥ Street) | 0.645 | **0.305** | 0.620 | 0.469 | |
| 4Q26 FX (pp) | +0.51 | **−0.37** | +0.51 | +0.28 | |
| 4Q26 ADR | $173.03 | **$171.46** | $172.94 | $172.56 | $171.33 |
| 4Q26 P(print ≥ Street) | 0.701 | **0.517** | 0.694 | 0.650 | |
| FY27 ADR | $185.21 | **$184.36** | $185.07 | | none exists |
| half-band 3Q26 / 4Q26 (±1σ) | 0.978 / 1.932pp | 1.005 / 1.895pp | 1.005 / 1.985pp | | |

**What this means for the pitch.**

- **3Q26 ADR is more likely below the Street than above it** on the best-tested FX estimate ($176.18, P 0.31).
  The three FX estimates span $176.2–$177.6 around a Street of $177.06.
- **4Q26 sits on the Street** on the recommended leg ($171.46, P 0.52), and $1.2–$1.6 above it on the identity
  or V1.
- **The FX estimate is now the largest single swing in the ADR line.** The 5 Nov print is the test.

**The 4Q26 ladder.** 4Q26 ADR under each rule:

| rule | v3 (midpoint FX) | identity FX | V1 FX | vs Street (v3) |
|---|---:|---:|---:|---:|
| core mean reversion (to the core's own mean) | $168.82 | $170.30 | $169.91 | −$2.51 |
| AR(1) fitted on the core | $169.58 | $171.05 | $170.67 | −$1.75 |
| lap-only (every 2025–26 step laps) | $170.13 | $171.61 | $171.23 | −$1.20 |
| tilt B (retired) | $170.78 | $172.25 | $171.87 | −$0.55 |
| sub-regional country mix (netted) | $171.39 | $172.86 | $172.48 | +$0.06 |
| **base** | **$171.46** | **$172.94** | **$172.56** | **+$0.13** |
| measured origin–destination tilt | $171.79 | $173.27 | $172.88 | +$0.46 |
| fee-migration K line | $172.09 | $173.57 | $173.18 | +$0.76 |
| card v3 carry, no lap | $173.20 | $174.68 | $174.30 | +$1.87 |

**The binding negative, restated.** On the identity or V1 FX, no mix-only row reaches the Street, as the audit
found. On the recommended midpoint FX, the base is $0.13 above the Street, and the best mix-only row (sub-regional)
sits $0.06 above it. The World Cup premium measured on `krish/worldcup-premium` (0.05–0.20pp, $0.08–$0.33) would
take the base below. So: **the FX estimate, not mix, is what decides whether 4Q26 is below the Street.**

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
3. **LOS in fix (c):** case A (−$0.09) or case B (−$0.50). Recommend A until a same-construction 2Q26 LOS exists.
4. **The 2027 core rule.** Not changed here. The core's point-in-time record favours its expanding mean at h ≥ 3,
   which puts FY27 ADR about $2.5 lower. It deserves its own pre-registration.
5. **World Cup row.** Add −0.05 to −0.20pp from 4Q26 once `krish/worldcup-premium` is committed. On the midpoint
   leg it takes the 4Q26 base below the Street.
6. **Workbook.** `model/ABNB_official_model.xlsx` still reads `adr_engine` (v2). It needs an approved rebuild.
7. **Posterior.** Not re-run (no PyMC here); its draws are seeded from v2.
8. **FX refresh.** Everything uses FRED through 18 Sep. Refresh before the memo (`run.py --fetch` writes a new
   dated file; point `config.FX_DAILY` at it).

## RESUME

The next agent should read this note, then `git log origin/main..krish/adr-audit-fixes`: one commit per fix.

- **Switches** reproduce v2 behaviour: `config.FX_LEG = "identity"`, and in `exfx.py` `CONSTRUCTION_FIX`,
  `CORE_FIX`, `SUBGEO_NETTING`.
- **On 5 Nov:** recompute the V0, V1 and midpoint points at O3. Then run
  `fx_falsifier.score_print(y, FF.CANDIDATES_3Q26_J, leg="midpoint_refreshed")` with the printed ADR-FX pp, and apply
  the §12 ratio rule.
- **Choices 2, 3 and 4 move numbers.** Refresh FRED before the memo.
