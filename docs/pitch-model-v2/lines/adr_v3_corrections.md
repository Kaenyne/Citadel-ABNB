# ADR line v3 — the audit's corrections, what each one moves, and what is still open

**23 September 2026.** Krish (ADR owner); for Theo's review. Source: the adversarial audit
`docs/pitch-model-v2/dossiers/ADR_AUDIT_krish.md` (receipts in `data/processed/pitch_model_v2/receipts/ADR_AUDIT/`).
Engine: `analysis/src/pitch_model_v2/adr_engine_v3/`, a copy of `adr_engine` with one commit per fix; `adr_engine`
and its tracked outputs are untouched. Numbers below: `data/processed/pitch_model_v2/adr_engine_v3/v3_vs_v2_*.csv`.

```bash
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.adr_engine_v3.run --no-posterior --no-workbook --no-refresh-prices   # exit 0
PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests -q                           # 43 pass
```

## 1. The line after the corrections

| | v2 as filed | **v3** | v3 with the V1 FX variant | Street |
|---|---:|---:|---:|---:|
| 3Q26 ADR | $177.68 | **$177.59** | $176.93 | $177.06 |
| 3Q26 P(print ≥ Street) | 0.645 | **0.620** | 0.469 | |
| 4Q26 ADR | $173.03 | **$172.94** | $172.56 | $171.33 |
| 4Q26 P(print ≥ Street) | 0.701 | **0.686** | 0.644 | |
| FY27 ADR | $185.21 | **$185.07** | | none exists |
| half-band 3Q26 / 4Q26 (±1σ) | 0.978 / 1.932pp | 1.005 / 1.985pp | | |

**What this means for the pitch.**

- **3Q26 is on the Street.** The honest range is $176.9–$177.6, depending on which registered FX number you
  believe. That is a coin flip, not a 65% beat.
- **4Q26 stays above the Street** under both FX numbers ($172.56–$172.94 against $171.33).
- **The ADR line is shape and attribution.** The variant view lives in nights and margins.

**The 4Q26 ladder.** 4Q26 ADR under each rule, v3 with the identity FX, then with V1:

| rule | v3 | v3, V1 FX | vs Street (v3) |
|---|---:|---:|---:|
| core mean reversion (to the core's own mean) | $170.30 | $169.91 | −$1.03 |
| AR(1) fitted on the core | **$171.05** | $170.67 | **−$0.28** |
| lap-only (every 2025–26 step laps) | $171.61 | $171.23 | +$0.28 |
| tilt B (retired) | $172.25 | $171.87 | +$0.92 |
| sub-regional country mix (netted) | $172.86 | $172.48 | +$1.53 |
| **base** | **$172.94** | **$172.56** | **+$1.61** |
| measured origin–destination tilt | $173.27 | $172.88 | +$1.94 |
| fee-migration K line | $173.57 | $173.18 | +$2.24 |
| card v3 carry, no lap | $174.68 | $174.30 | +$3.35 |

**The binding negative stands, now stated precisely.**

- No composition row reaches the Street under either FX leg. The lowest non-retired one is sub-regional at $172.48.
- Three core assumptions reach it: mean reversion, the fitted AR(1), and, with V1's FX, lap-only.
- A short that needs a below-Street 4Q26 ADR is making a call on the core. The World Cup premium measured on
  `krish/worldcup-premium` (0.05–0.20pp) is a small labelled composition row, not a route across.

## 2. The corrections, one commit each

| fix | what was wrong | what changed | 3Q26 / 4Q26 effect |
|---|---|---|---|
| **(a) FX** | V0's point-in-time error rises with its own LatAm component in every promotion cell (slope +0.55 to +0.69, p 0.002–0.012); 3Q26 is a LatAm-heavy quarter. | V0 stays the leg (the registered tie-break). V1, the registered fitted variant (LatAm 0.41, EMEA 1.20), is computed and carried beside it everywhere. | Leg unchanged. V1: 3Q26 +0.03pp / −$0.66; 4Q26 +0.28pp / −$0.39 |
| **(b) FX falsifier** | "Printed FX inside [0.36, 0.48] or withdraw" fails a correct identity about 88% of the time: the printed figure carries ±0.5pp of whole-point rounding. | `adr_fx_prereg.md` §11 is appended (dated 23 Sep, before the print): a comparative interval score of the named candidates. V0 is withdrawn only if it scores worst. Scorer: `fx_falsifier.py`. | None. It changes the 5 Nov test. |
| **(c) one construction** | The core is ex-FX minus the H terms. The forward added geo from the bucket method (+0.132pp above H at 2Q26, one-signed since 4Q24) and unit size from workstream I (+0.166pp). The H 2Q26 capacity came from dumps in which 2Q26 was still partly reviewed. LOS switched from H's assumed 0.30 to I's measured 0.056. | Each forward term is put on the core's footing. Case A carries LOS at its in-core value, because no same-construction 2Q26 value exists. Case B (the LOS drop is real) is saved as the bound. | Base −0.054pp, −$0.09 each quarter (case B: −0.298pp, −$0.50) |
| **(d) downside rows** | Mean reversion used the residual's mean (2.398), not the core's (2.272). "AR(1) on core" used the residual's AR(1) (implied mean 2.96). | The core's own mean. An AR(1) fitted on the core: ρ 0.465, mean 2.41. | MR $170.60 → $170.30; AR(1) $172.38 → $171.05 (4Q26) |
| **(e) sub-regional row** | Added the full forward term (−0.147pp) on top of a core that already holds 2Q26's (−0.100pp). | Adds the change from 2Q26, read by label. | Row +$0.17 (net of the other fixes +$0.08) |
| **(f) bundle band** | 0.8–1.2pp is narrower than management's rounding: 0–1.5 in 4Q25, 0–2.0 in 1Q26. | 0.5–1.5pp. The 1Q26 figure includes about 6 weeks of ex-NA RNPL. | Half-band +0.03 to +0.05pp; P(≥ Street) −0.01 |
| **(g) reconciliation** | "Cannot reject the identity; compatible". With four clusters there is no valid p-value (wild-cluster bootstrap 0.89), and 76% of LatAm's slope is Brazil's hotel CPI. | "Not established". The annual 10-K reconciliation stands. | None (wording) |
| **(h) labels** | 4Q27 FX 0.000 is a spot-held artefact, unlabelled where it flows into FY27 (about $0.40 of FY27 ADR per 1pp). The band was unlabelled. | Labelled in the docs, the income-statement note and `adr_path.csv` (`note`, `band_basis`). | None (labels) |
| **(i) factual errors** | "Core is 40% of ex-FX" (it is 116–138%). Lap-only "crosses" (it is $0.38 above). "RNPL not named in a filing until 2Q26" (the 3Q25 letter names it). "EMEA's first sub-50% English quarter 2Q26" (it was 4Q25). "Within 0.13pp" (that is the mean; the max is 0.22). Thesis sentence 3. The V0 bias range. | Corrected in place with the evidence. | None (text) |

## 3. The FX leg: what we now know about the identity's LatAm miss (step 2)

Three probes on archived Airbnb search pages (`docs/cc-search-price/`, branch `krish/cc-search-price`) narrow the
cause.

- **Conversion is exact and immediate (I6, I6b).** 1,796 same-stay pairs across storefronts: Airbnb converts the
  host's price at spot, with a margin inside ±25bp and no lag. This confirms the identity's functional form
  (contemporaneous, unhedged, no lag operator). It also means the guest's paying currency cannot matter, because the
  USD amount is the host's price times spot either way.
- **Hosts price in local currency (I6c).** On the Brazilian storefront, 45% of Brazilian listings show round-BRL
  prices, against 25% for US listings. The airbnb.com estimate of a USD-priced share is 0.36–0.38 with every
  interval containing zero. Host pricing currency does not explain a LatAm weight of 0.41.
- **So the miss is a weighting error.** The identity's LatAm exposure (10-K GBV share × a judgement basket: BRL .45,
  MXN .38, USD .07, other LatAm .10 mapped to BRL) is too large. The likeliest causes are the basket and the annual
  GBV weights, not pricing or conversion. Pinning it down needs a LatAm country mix of Airbnb's GBV, which is not in
  the repo. That is post-memo work.
- **A caution on FX line v2** (`docs/adr-card-v3_1/FX_LINE_V2.md`). That construction failed its own pre-registered
  test (RMSE 0.82 against the committed midpoint's 0.42; 0 of 24 jackknife wins). Its weights are same-quarter
  *revenue* shares, which are stay-dated and seasonal (LatAm and APAC heavy in Q4), while ADR FX is booking-dated.
  Its 4Q26 +1.66pp ("$2.0–2.5 of unpriced upside against the short") should not enter the risk section as a number.
  The estimators that passed put 4Q26 FX at +0.28 (V1) to +0.51 (V0), and the LatAm evidence leans to the lower end.

## 4. Evidence from the other ADR thread that this line uses or deliberately does not

| item | where | used here? |
|---|---|---|
| Card v3.1: the unit-size mismatch comes from review accrual in the June/July dumps (2Q26 held 14% fewer reviews); routes A and B agree within 0.01pp (card v3 −$0.28) | `docs/adr-card-v3_1/CARD_V3_1.md` | **Yes**, as fix (c)'s unit leg (route-B equivalent). Theo's ladder shows the card row at +$0.13 rather than −$0.28, because case A also carries LOS at its in-core 0.30. That LOS treatment is open choice 2. |
| Unit-size elasticity 0.53–0.55 with place FE (pitch 0.59) | `docs/cc-search-price/I3b_elasticity_layer.md` (dated correction) | No change: re-solved consistently it is worth under 2 cents |
| New listings price +3.5% (±1.2) above comparable incumbents within market, not −5.6% | `docs/cc-search-price/I4c_targeted_sample.md` | No term in this engine. It weakens the supply-dilution argument for core reversion; carry it in the §9 analyst answers. |
| Listing-age term v2: the M term was a memo line, so promoting it moves ADR about −$0.02 | `docs/adr-card-v3_1/LISTING_AGE_V2.md` | No change |

## 5. Open choices for Krish and Theo

1. **Adopt v3 as line 2** (proposed DEC-0043): fixes a and c–f. Recommend yes. Each fix can be reverted alone.
2. **LOS in fix (c): case A** (carry the in-core 0.30, −$0.09) **or case B** (trust I's measured drop, −$0.50).
   Recommend A until a same-construction 2Q26 LOS exists; quote B as the bound.
3. **How 3Q26 FX is presented** (proposed DEC-0044): V0 as the leg with V1 beside it and the §3 explanation.
   Recommend this. Promoting V1 would break the registered tie-break.
4. **The 2027 core rule.** Not changed here. The core's own point-in-time record favours its expanding mean over
   the carry at h ≥ 3 in both windows (n 6–8). That gives FY27 ADR about $182.7, against $185.1. It is a
   short-relevant decision for FY27 and deserves its own pre-registration.
5. **World Cup row.** Add "World Cup premium inside the 2Q26 core, −0.05 to −0.20pp from 4Q26" as a labelled
   composition row once `krish/worldcup-premium` is committed.
6. **Workbook.** `model/ABNB_official_model.xlsx` still reads `adr_engine` (v2). Rewiring it to v3 and adding the
   4Q27 label needs an approved workbook rebuild; `model/` is protected.
7. **Posterior.** Not re-run (no PyMC on this machine); its draws are seeded from v2. Re-run on the build machine.

## RESUME

The next agent should read this note, then `git log origin/main..krish/adr-audit-fixes`. Commits are one per fix:
revert any single commit to drop that fix. Toggle flags in `exfx.py` (`CONSTRUCTION_FIX`, `CORE_FIX`,
`SUBGEO_NETTING`) reproduce v2 behaviour for comparison. On 5 Nov, run `fx_falsifier.score_print(y)` with the
printed ADR-FX pp (reported y/y minus the letter's ex-FX), after recomputing the V0 and V1 points at O3. Open
choices 2 and 4 are the ones that move numbers.
