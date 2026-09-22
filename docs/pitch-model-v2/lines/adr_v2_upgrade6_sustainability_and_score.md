# ADR line v2, upgrade 6 — the geo-mix layer made reproducible, and how it will be scored

Date **22 September 2026**, written before the 3Q26 print. This file does two things and nothing else:

1. it records that the sub-regional (country-level) geo-mix term is no longer an ad-hoc script — it is a stage of
   `pitch_model_v2.adr_engine.run`, its three inputs are rebuilt from the raw stores by `refresh_prices.py`, and
   seventeen tests hold the arithmetic down (`tests/test_geomix.py`);
2. it **pre-registers the score**: the targets, the numbers we are predicting *now*, the pass/fail lines, and the
   refresh cadence, for the two dates that settle them — **5 November 2026** (3Q26 print, 4Q26 guide) and
   **11 February 2027** (4Q26 print, FY27 guide).

Governing pre-registrations, unchanged: `adr_fx_prereg.md` (the FX leg) and `adr_v2_geomix_prereg.md` (this layer,
including its §2 hypotheses and its §4 filed results). **DEC-0016 stands**: both terms are reported whichever way
they land, and nothing below is re-chosen after a print.

---

## 1. What is being scored

Two layers add to the ex-FX ADR mechanism, and they are scored separately because they can fail independently.

| layer | object | source | file |
|---|---|---|---|
| **four-region term** | mix across the four disclosed buckets — NAM / EMEA / LatAm / APAC — at frozen base-quarter regional ADR levels | the nights line's regional path (`nights_v2_design.md` §2.1) + `04_regional_quarterly_wide.csv` ADR levels | `geo_mix_forward.csv`, `geo_mix_tilt_sensitivity.csv` |
| **sub-regional term** | mix across countries *inside* each region, at Inside Airbnb USD price levels, GBV-weighted across regions | the 123-market stays panel (`stays_yoy_by_country_vmatch.csv`) + `country_price_levels_usd.csv` | `geomix_subregional_term_forward.csv`, `geomix_within_region_forward.csv` |

### Targets (what Airbnb will actually print)

- **T1 — disclosed regional ADR, reported and ex-FX.** The shareholder letter states regional ADR y/y in whole
  points for each of the four regions, and an ex-FX figure for EMEA / LatAm / APAC. Captured in
  `data/processed/overnight/10_regional_panel_quarterly.csv` as `<reg>_adr_yoy_reported_pct` and
  `<reg>_adr_yoy_exfx_pct`. Last four quarters, for scale: reported NAM 5 / 5 / 7 / 7, EMEA 10 / 12 / 15 / 7,
  LatAm 4 / 9 / 10 / 9, APAC 2 / 2 / 6 / 1 (3Q25→2Q26); ex-FX EMEA 4 / 4 / 4 / 5, LatAm 3 / 3 / 3 / 2,
  APAC 3 / 2 / 2 / n.d.
- **T2 — disclosed regional nights growth.** `<reg>_nights_yoy_mid` (the letter's phrase, mid-pointed). Last four:
  NAM 5 / 5 / 8 / 8, EMEA 5 / 8 / 5 / 8, LatAm 21.5 / 18 / 18 / 20, APAC 15 / 15 / 18 / 18.
- **T3 — disclosed global ex-FX ADR y/y** (`global_adr_exfx_yoy_pct`; 2 / 3 / 4 / 4 over 3Q25–2Q26) and the
  **reported ADR level** in dollars (`02_kpi_panel_quarterly.csv`, `adr_usd`).

T1 and T2 settle the four-region term. The sub-regional term has **no disclosed counterpart** — Airbnb does not
publish country ADR — so it is scored against its own realised panel value, which is what makes the scoring rule
below necessary: the panel must be rebuilt from the same code, on the completed quarter, and compared with what we
wrote today.

---

## 2. The predictions, written now (22 September 2026 build)

FX through 18 September 2026; `00_summary.json` `run_at` 2026-09-22, `adr_3q26` 177.681, `adr_4q26` 173.034.

### P1 — four-region geo-mix term (`geo_mix_forward.csv`)

| quarter | nights-linked term | card v3 term | implied regional nights growth (NAM / EMEA / LatAm / APAC) |
|---|---|---|---|
| **3Q26** | **−1.293 pp** | −1.428 pp | 5.60 / 7.08 / 17.70 / 15.93 |
| **4Q26** | **−1.336 pp** | −1.428 pp | 3.31 / 6.32 / 15.79 / 14.21 |

Tilt envelope (`geo_mix_tilt_sensitivity.csv`), the four pre-registered ex-NA growth patterns:

| quarter | tilt C (Europe leads, 10/15/14) | base (8/20/18) | tilt A (6/25/22) | tilt B (5/30/25) |
|---|---|---|---|---|
| **3Q26** | −1.009 | **−1.293** | −1.535 | **−1.674** |
| **4Q26** | −1.076 | **−1.336** | −1.565 | **−1.700** |

### P2 — sub-regional country-mix term (`geomix_subregional_term_forward.csv`)

| quarter | **subgeo total** | NAM part | EMEA part | LatAm part | APAC part |
|---|---|---|---|---|---|
| **3Q26** | **−0.137 pp** | −0.104 | +0.029 | −0.020 | −0.043 |
| **4Q26** | **−0.147 pp** | −0.109 | +0.021 | −0.015 | −0.044 |

Within-region mixes behind them (`geomix_within_region_forward.csv`), which are the falsifiable part:

| quarter | NAM | EMEA | LatAm | APAC |
|---|---|---|---|---|
| **3Q26** | **−0.235** | **+0.077** | **−0.210** | **−0.475** |
| **4Q26** | **−0.247** | **+0.056** | **−0.162** | **−0.483** |

History for context (`geomix_subregional_term.csv`): 1Q23–2Q26 mean **−0.453 pp** (sd 0.320, q/q change sd 0.240);
1Q24–2Q26 mean −0.296; 3Q25–2Q26 mean **−0.152**; 1Q26 −0.258, 2Q26 −0.100. **The claim being tested is that the
drag has faded, not that it is large.**

### P3 — the line itself (`exfx_forward_base.csv`, `exfx_envelope.csv`, `adr_path.csv`)

| quarter | ex-FX ADR y/y | half-band | FX pp | reported ADR y/y | ADR $ | $ band | Street |
|---|---|---|---|---|---|---|---|
| **3Q26** | **+3.316%** | ±0.976 pp | +0.415 | **+3.731%** | **177.68** | 176.01 – 179.36 | 177.06 (n 26) |
| **4Q26** | **+2.784%** | ±1.424 pp | +0.514 | **+3.298%** | **173.03** | 169.80 – 176.27 | 171.33 (n 25) |

Adding the sub-regional term to the base moves 4Q26 ADR by **−$0.24** (173.03 → 172.79); tilt B on top moves the
four-region term a further **−0.364 pp** in 4Q26 (`exfx_alternatives.csv`, rows "base + sub-regional …" and
"base + sub-regional + composition tilt B …").

---

## 3. Pass / fail lines (fixed now)

Scored on **5 Nov 2026** for 3Q26 and **11 Feb 2027** for 4Q26. Each line is stated so that a single number decides
it. A line that cannot be evaluated because the letter did not disclose the input is recorded **"not settled"**, not
"passed".

**S1 — four-region term, point.** Recompute the term with `exfx.geo_mix_pp` on the **disclosed** regional nights
growth mids for the quarter (T2) and the base-quarter regional ADR levels — the exact call
`geo_mix_history_check()` already makes for history. Call it `geo_mix_realised`.
**PASS if |predicted − realised| ≤ 0.35 pp and both are negative.**
The 0.35 pp line is the method's own reproduction error, not a hope: on 2Q24–2Q26 the bucket arithmetic reproduces
the H decomposition's geo-mix term with mean |diff| 0.135 pp and max 0.218 pp (`geo_mix_method_check.csv`).

**S2 — four-region envelope.** **PASS if `geo_mix_realised` lies inside [tilt B, tilt C]** — [−1.674, −1.009] for
3Q26, [−1.700, −1.076] for 4Q26. A realised value outside that band means the four pre-registered ex-NA patterns
did not bracket the composition, and the tilt exhibit is retired from the pitch even if S1 passes.

**S3 — sub-regional term, point.** Once the quarter's Inside Airbnb dumps have landed (the panel needs all three
months), rebuild the panel and recompute the **realised** term for the quarter with the shipped code:
`run.geomix_stage()` writes `geomix_subregional_term.csv`; read the quarter's `subgeo_pp`.
**PASS if |predicted − realised| ≤ 0.25 pp and the sign is negative.**
0.25 pp is one quarterly change sd of the term over 1Q23–2Q26 (0.240 pp).

**S4 — the fading claim.** The substantive statement in `adr_v2_geomix_prereg.md` §4 is that the sub-regional drag
has faded from −0.45 pp to about −0.15 pp. **PASS if the realised term is > −0.30 pp** for the quarter.
**FAIL if it is ≤ −0.45 pp** (back at the 1Q23–2Q26 mean), which would mean the fade was a 2026 artefact and the
forward carry understates the drag. Between −0.45 and −0.30: **"weakened"**, reported as such.

**S5 — within-region signs.** The term's mechanism is four regional statements, all four written above.
**PASS if at least three of the four realised within-region mixes match the predicted sign** (NAM negative,
EMEA non-negative, LatAm negative, APAC negative). Two or fewer is a FAIL of the mechanism, whatever S3 does — a
right total from wrong parts is not evidence.

**S6 — global ex-FX ADR.** **PASS if the disclosed `global_adr_exfx_yoy_pct` (a whole number) lies inside the
predicted band**: 3Q26 [2.34, 4.29] → 3 or 4 passes; 4Q26 [1.36, 4.21] → 2, 3 or 4 passes.

**S7 — reported ADR level.** **PASS if the printed `adr_usd` lies inside the band**: 3Q26 [176.01, 179.36],
4Q26 [169.80, 176.27]. Recorded beside the Street figure and the z already filed (`adr_path.csv`:
z 0.371 / 0.527, P(print ≥ Street) 0.64 / 0.70).

**S8 — coverage honesty.** `adr_v2_geomix_prereg.md` §4 states what the panel cannot see: no Indian, Emirati,
Malaysian, Indonesian or Vietnamese destination market. **If the letter again attributes APAC growth mainly to
India origin (as in 1Q26 +50% and 2Q26 +60%) while the realised APAC within-region mix is within ±0.10 pp of zero,
that is recorded as confirmation that the panel is blind to the channel**, and the APAC part of the term is shown
with that caveat on the exhibit rather than as evidence.

### What would retire the layer

Both S1 and S2 failing at either print retires the four-region tilt exhibit. S3 and S5 both failing at either print
retires the sub-regional term from the pitch and leaves it as an attribution row only — which is already all H2
allows it to be (`geomix_h2_scores.csv`: ratio to the residual carry 0.909 W1 / 0.719 W2, W1 above the 0.75 line,
**not promoted**).

---

## 4. Refresh cadence and the exact commands

Three stores feed this layer and they move on different clocks.

| store | cadence | what refreshes it |
|---|---|---|
| Inside Airbnb dumps (`~/abnb_ia_capture/<country>/<state>/<market>/<dump>/`) | monthly per market, rotated off the CDN — a missed dump is unrecoverable | `analysis/src/acquisition/ia_daily_capture.py` (daily job, 120 markets) |
| the E stays panel (`data/processed/q3nowcast/E/market_monthly_yoy.csv`) | rebuilt when new dumps land | `analysis/src/q3nowcast/E4_build_index.py` |
| FRED H.10 + ECB reference rates | weekly (H.10 prints Monday, ~1-week lag) | `adr_engine/fetch_fx.py` |

```bash
cd ~/Citadel-ABNB

# 1. capture (daily; it is what makes the monthly dumps recoverable at all)
PYTHONPATH=analysis/src python3 -W ignore analysis/src/acquisition/ia_daily_capture.py

# 2. rebuild the stays panel after new dumps have landed
PYTHONPATH=analysis/src python3 -W ignore analysis/src/q3nowcast/E4_build_index.py

# 3. FX (weekly). Writes a NEW dated file; point config.FX_DAILY at it before step 4.
PYTHONPATH=analysis/src python3 -W ignore analysis/src/pitch_model_v2/adr_engine/fetch_fx.py

# 4. rebuild the geo-mix inputs only (~14 s, reads 120 listings.csv.gz)
PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.refresh_prices

# 5. the whole ADR line, geomix stage included (~20 s without the posterior/workbook)
PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.run
PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.run --no-refresh-prices   # reuse saved inputs
PYTHONPATH=analysis/src python3 -W ignore -m pytest analysis/src/pitch_model_v2/adr_engine/tests -q
```

**On each score date** the sequence is 1 → 2 → 3 → 5, then read `geomix_subregional_term.csv` (S3, S4, S5),
`geo_mix_method_check.csv` rebuilt with the new disclosed mids (S1, S2), `00_summary.json` and `adr_path.csv`
(S6, S7), and enter the disclosed figures in `10_regional_panel_quarterly.csv` first — the score lines read from
it, not from the letter by eye.

Every run prints its own reproduction check before overwriting anything:

```
  reproduction checks (against the outputs on disk, before overwriting):
    geomix_subregional_term.csv            max |diff| 2.220e-16  -> reproduced (<1e-6)
    geomix_subregional_term_forward.csv    max |diff| 9.368e-17  -> reproduced (<1e-6)
    geo_mix_tilt_sensitivity.csv           max |diff| 3.553e-15  -> reproduced (<1e-6)
```

A line reading `CHANGED` after a refresh is the intended signal that a store moved; it is **not** a licence to
re-choose a rule. The three judgement constants live at the top of `refresh_prices.py` and are frozen:
`COUNTRY_CCY` (destination currency per country, Hong Kong = HKD), `FX_YEAR = 2026` (local → USD at the
calendar-year-average rate) and `MIN_USD_LEVEL = 5.0` (the floor that drops the three Swiss dumps, whose `price`
column carries 0.16–0.18 CHF a night).

Current coverage, printed by the same command: 123 panel markets / 37 countries; 120 markets found in the capture
store; **113 priced**; 30 countries priced; unpriced at the region median — argentina, chile (no FRED rate),
malta, new-zealand (no capture), switzerland (broken price field).
