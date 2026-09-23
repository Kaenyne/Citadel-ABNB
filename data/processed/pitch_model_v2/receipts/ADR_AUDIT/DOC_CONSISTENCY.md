# ADR line audit — document consistency receipt

22 Sep 2026. Worktree `C:\Users\krish\citadel-abnb-adraudit` (detached HEAD 84c430b7 of `theo/pitch-model-v2`).
Read-only: engine CSVs under `data/processed/pitch_model_v2/adr_engine/` (reproduced today to 1e-6), the docs under
`docs/pitch-model-v2/`, the engine code, and `model/ABNB_official_model.xlsx` via openpyxl read-only. Nothing was run
that writes tracked outputs. Helper: `doc_consistency_check.py` in this folder (log in `doc_consistency_check.log`).
Convention: where a later note contradicts an earlier one the later governs; a stale number in a still-live document
is recorded as a finding with its materiality for a quoted ADR number.

---

## Task 1 — the brief's table recomputed from the output files

| object | claimed | recomputed | file : column | verdict |
|---|---|---|---|---|
| identity vs disclosed FX | ≤ 0.042pp, 14 quarters | max abs 0.0422 on 1Q23–2Q26 (n 14); KPI panel `adr_yoy_reported_pct − adr_yoy_exfx_pct − fx_pts_adr` closes to 0.0000 (n 14) | `q3nowcast/H/adr_history_components.csv : identity_check_pp`; `overnight/02_kpi_panel_quarterly.csv` | match |
| walk-forward ratio, four promotion cells | 0.344 / 0.303 / 0.383 / 0.317 | 0.3437 / 0.3027 / 0.3831 / 0.3173 | `fx_scores.csv : ratio_vs_naive`, variant `V0_translation`, (W1,O2)(W1,O3)(W2,O2)(W2,O3) | match |
| bootstrap 90% upper | 0.438 / 0.369 / 0.509 / 0.418 | 0.4384 / 0.3688 / 0.5091 / 0.4181 | `fx_scores.csv : ratio_boot90_hi` | match |
| O1 cells (final_adr §2.5) | W1 n13 1.313/3.002/0.437/0.728/0.366; W2 n10 1.473/2.358/0.625/0.881/0.560 | identical to 3 dp | `fx_scores.csv : n, rmse_pp, rmse_naive_pp, ratio_vs_naive, ratio_boot90_hi, interval_ratio` | match |
| interval ratios O2/O3 | 0.211 / 0.151 / 0.240 / 0.153 | 0.2105 / 0.1511 / 0.2405 / 0.1527 | `fx_scores.csv : interval_ratio` | match |
| V0 bias | +0.11 / +0.15 / −0.07 / −0.04 | +0.113 / +0.145 / −0.070 / −0.040 | `fx_scores.csv : bias_pp` | match (but §2.6 prose "+0.11 to −0.07" should be "+0.15 to −0.07") |
| V1 ratios | 0.375 / 0.337 / 0.347 / 0.290 | 0.3750 / 0.3373 / 0.3469 / 0.2904 | `fx_scores.csv`, `V1_passthrough` | match |
| V2 euro-only ratios / biases | 0.270/0.281/0.268/0.272; −0.33/−0.27/−0.34/−0.27 | 0.2700/0.2813/0.2684/0.2717; −0.331/−0.272/−0.342/−0.272 | `fx_scores.csv`, `V2_eur_ols` | match (O1 cells add −0.46 W1 / −0.40 W2 ratio 0.399/0.531 — see §2 item 6) |
| V3 / naive rows (§2.6) | 0.532/0.517/0.599/0.568; naive bias −0.49/−0.49/+0.08/+0.08 | identical | `fx_scores.csv` | match |
| 3Q26 / 4Q26 FX | +0.415 / +0.514 | +0.4153 / +0.5137 | `adr_path.csv : fx_pp` | match |
| 3Q26 / 4Q26 ADR | $177.68 / $173.03 | 177.681 / 173.034 (= 171.29×1.03731, 167.51×1.03298) | `adr_path.csv : adr_usd` | match |
| bands | ±0.978 / ±1.932pp; $176.01–179.36 / $169.80–176.27 | 0.9775 / 1.9319; 176.007–179.356 / 169.798–176.270 | `adr_path.csv : band_half_pp, adr_usd_lo/hi` | match |
| P(print ≥ Street) | 0.645 / 0.701 | 0.6447 / 0.7008 (z +0.371 / +0.527; Street 177.06 n26 / 171.33 n25) | `adr_path.csv : p_print_ge_street` | match |
| 2027 path | 190.65 / 188.38 / 182.51 / 178.10; FX −0.369/−0.427/−0.147/0.000; FY26 180.62; FY27 185.21 (+2.544%, 621.85m) | identical | `adr_path.csv` | match |
| GBV | 26.08 / 22.81 / 105.29 / 115.17 | 26.084 / 22.806 / 105.289 / 115.174 | `adr_path.csv : gbv_busd` | match |
| 3Q26 obs share, in-quarter band, 4Q26 P10/P90, 5-Nov 32% printed and [−0.78, +1.97] | as stated | 0.8788; 0.355–0.481; −1.056/+2.259; 0.318, −0.779/+1.970 | `fx_forecast_asof.csv` | match |
| **geo-mix method vs H term, 2Q24–2Q26** | "within 0.13pp" | **mean abs 0.1344, max abs 0.2181 (3Q24), n 9**; 1Q23 diverges by 1.69 | `geo_mix_method_check.csv : diff_pp` | **mismatch in wording**: 0.13 is the mean, not a bound; max is 0.22 (upgrade 6 §3 S1 and adr_v1_design:240 state both correctly) |
| annual mix vs 10-K | −1.10/−1.33/−1.67 vs −1.08/−1.24/−1.58 | −1.102/−1.325/−1.672 vs −1.083/−1.244/−1.584; gaps 0.019/0.081/0.088 | `reconcile_annual.csv : our_geo4_pp, geo_mix_pp_10k` | match |
| sub-regional term | mean −0.453 (1Q23–2Q26); −0.152 (last four); forward −0.137/−0.147 | −0.4534 (n 14, label-filtered); −0.1517 on {3Q25,4Q25,1Q26,2Q26} = [−0.259, +0.011, −0.258, −0.100]; −0.1372 / −0.1468 | `geomix_subregional_term.csv : subgeo_pp`; `…_forward.csv` | match. Trap (b) confirmed: file ends with a partial 3Q26 row (+0.051); positional `iloc[-4:]` gives −0.074. Workbook G1 filters to HIST_LAST before `iloc[-4:]` (value −0.1517 in the sheet), so the shipped code avoids it |
| sub-regional $ on 4Q26 | −$0.24 | −0.246 (scenario 172.788 vs 173.034); DEC-0038 says −0.25 | `adr_scenarios.csv : vs_base_usd` | rounding only |
| origin rotation | non-EN +81.0% vs EN +40.0%; EN share 62.9→56.8 | +81.04 / +39.96; 62.94 → 56.76, from the `region == GLOBAL` × `lang ∈ {ALL_NON_EN, en}` rows | `origin_lang_rotation_ltm.csv : growth_pct_24_26, share_pct_*` | match. Trap (a) confirmed: summing all non-`en` rows across GLOBAL + four regions + TOTAL/ALL_NON_EN gives +66.2% |
| non-EN cheaper within market | 13.4% (16.7% weighted) | review-weighted mean of `rel_price_vs_en_median` = 0.8657 → 13.4%; of `_wtd` = 0.8333 → 16.7% | `origin_lang_price_summary.csv`, weights `total_reviews_ltm_2026` | match |
| rotation price effect | −0.35%/yr | `mix_pct_25_26_wtd` GLOBAL −0.354 (24→26 −0.690 ÷ 2 = −0.345) | `origin_lang_price_mix_effect.csv` | match |
| EN share 71% (2022) → 58% (2026) | as stated | 71.15 → 58.44 | `origin_proxy_review_language_by_region_year.csv` GLOBAL | match |
| quarterly EN share drop flat ≈ 2.9pp | −2.79/−3.21/−2.73/−2.91 | identical (2025Q3–2026Q2) | `origin_lang_global_quarter.csv : share_chg_pp`, lang en | match |
| **"EMEA printed its first sub-50% English quarter in 2Q26"** | first sub-50% = 2Q26 | EMEA en share: 3Q25 51.37, **4Q25 49.54, 1Q26 46.17**, 2Q26 49.69 | `origin_lang_region_quarter.csv` | **unsupported**: first sub-50% quarter was 4Q25 (final_adr:414, mitigation D:204) |
| size-mix 2025, hedonic | +0.739pp inside [+0.42, +1.29] | H route 2025 = 0.7395; filed-arbiter rows 0.4166 … 1.2879 | `sizemix_routes.csv : size_pp`; `sizemix_rebased_plug.csv` variant B/C | match |
| like-for-like 2025 after DEC-0040 | 2.68–2.93 flat vs 2024 2.69–2.75 | variant C 2.679 / B 2.934; 2024 C 2.685 / B 2.754; as-filed 3.925 (withdrawn) | `sizemix_rebased_plug.csv : implied_lfl_price_pp` | match |
| currency contributions 3Q26 (§2.8) | AUD .402, MXN .365, BRL .313, GBP −.021, KRW −.021, CAD −.053, INR −.055, JPY −.132, EUR −.384; Σ .415; y/y and weights as listed | identical to 3 dp; AUD+MXN+BRL = +1.081 ("+1.08 of the +0.42") | `fx_currency_contributions.csv` | match |
| currency contributions 4Q26 | AUD .413, MXN .270, BRL .237, EUR −.398; three = +0.92 | .4128 / .2702 / .2369 / −.3981; sum of three +0.920; Σ +0.5137 | same | match |
| 4Q27 FX = 0.000 | artefact | all nine `yoy_pct` = 0.0 (spot-held numerator and denominator) | `fx_currency_contributions.csv`, quarter 4Q27 | confirmed by construction |
| 4Q26 ladder (§6.2) | 3.69/174.55; 3.16/173.66; 2.88/173.19; 2.78/173.03; 2.64/172.79; 2.27/172.18; 2.39/172.38; 1.99/171.71; 1.33/170.60 | 3.691/174.554; 3.159/173.661; 2.878/173.192; 2.784/173.034; 2.637/172.788; 2.273/172.178; 2.393/172.379; 1.991/171.705; 1.333/170.603 | `adr_scenarios.csv : exfx_pct, adr_usd` | match |
| core statistics (§3.3) | core 2023–25 mean 2.272; 2Q26 core 3.849 is 1.58 above; residual mean 2.398; core reversion $170.39 vs filed $170.60; own 1-q error 0.88 | core mean 2.2724 (n 12); gap 1.577; residual mean 2.3983 (gap 1.451); mean-reversion 4Q26 at 2.398 → $170.60, at 2.272 → $170.39; sd of quarterly core changes 0.882 (ddof 1) | `exfx_history.csv : core, residual`; `exfx_forward_base.csv` | match |
| residual steps | +0.92 (3Q25), +0.88 (4Q25) | +0.917 / +0.877 (1Q26 +0.682, 2Q26 +0.469) | `exfx_history.csv : residual` diffs | match |
| ex-FX forward terms (§3.2) | table | identical to `exfx_forward_base.csv` (core 3.849, bundle 0.489/0, geo −1.293…−1.109, unit 0.797, LOS 0.056, seats −0.483/−0.565, int −0.100, ex-FX 3.316/2.784/2.417/2.957/2.863/2.928) | `exfx_forward_base.csv` | match |
| H2 ratios | 0.909 W1 / 0.719 W2 | 0.9089 (n 10) / 0.7190 (n 6) | `geomix_h2_scores.csv` | match |
| market panel | b +0.083 p 0.794 [−0.539, 0.705], n 94 / 92 mkts; ex-US +0.041 p 0.956 [−1.41, 1.49] | 0.0829 / 0.7940 / [−0.5394, 0.7052] / 94 / 92; 0.0411 / 0.9558 / [−1.4117, 1.4939] (n 70 / 68) | `market_panel_scores.csv` rows `M2 …` and `M2-exUS` | match |
| posterior β | 0.994 / 1.199 / 0.460 / 1.266 | identical (workbook block E row 112) | `fx_weights_posterior.csv` via block E | match |
| "27 tests" | 27 | `tests/test_adr_engine.py` 10 + `tests/test_geomix.py` 17 = 27; `pytest.log` "27 passed" | code | match |
| **"The core is 40% of your ex-FX number"** (final_adr:565) | 40% | core 3.849 / ex-FX 2.784 = **138%** (4Q26); 116% (3Q26). The only 40% in the data is the unexplained step ÷ core = 1.577 / 3.849 = 41% | `exfx_forward_base.csv` | **unsupported as written** |

Summary of Task 1: every quoted ADR, FX, band, probability, ladder and mitigation number reproduces. Three statements
do not: "within 0.13pp" (a mean quoted as a bound; max 0.22), "first sub-50% English quarter in 2Q26" (4Q25 was
49.5%), and "the core is 40% of the ex-FX number" (it is 138%). None changes a quoted ADR number.

---

## Task 2 — stale, superseded and unsupported numbers in live documents

Format: `document:line` — stale text — what supersedes it — materiality.

1. `lines/adr_v1_design.md:8` — "`run.py` rebuilds everything, exit 0, **10 tests**" — superseded by upgrade 6 /
   `final_adr.md:15` and the same file's own line 305 ("27 tests"; `pytest.log` 27 passed). Immaterial.
2. `lines/adr_v1_design.md:197` — core 3.85 "still **1.45pp** above its 2023–25 mean" — 1.45 is the gap to the
   **residual** mean 2.398; the core's own mean is 2.272 and the gap 1.58. Superseded by `final_adr.md` §3.3
   (lines 260, 267–272) and `adr_v2_mitigation_B_market_panel.md:275–277`. Same stale 1.45 in
   `adr_v2_geomix_prereg.md:73`, `adr_v2_upgrade3_reconciliation.md:249`, `adr_v2_mitigation_A_sizemix_and_10q.md:363`,
   `adr_v2_mitigation_B_market_panel.md:7` (quoting the thesis). Materiality: none for the base; the mean-reversion
   scenario still reverts to 2.398 (`exfx.py CORE_MEAN_2023_25`), i.e. $170.60 rather than $170.39 (+$0.21, against
   the short), which `final_adr.md` §3.3 flags and leaves for Theo.
3. `lines/adr_v1_design.md:520` — "core_pp … 2023-25 mean **2.398** is the downside" — labels the residual's mean as the
   core's. Superseded by `final_adr.md` §3.3. Same $0.21 materiality as item 2.
4. `lines/adr_v1_design.md:268` — "Net of it, the 2026 step in like-for-like price is **1.1pp**, not 1.45" — the
   sub-regional-adjusted core2 step recomputes to 1.18 (3.949 vs 2.771), which `adr_v2_geomix_prereg.md:73` states as
   1.2; `adr_v2_thesis.md:79` gives "about 1.2pp on a flat base" from a third base (3.85 − 2.68…2.93 = 0.92–1.17);
   `final_adr.md:260` uses 1.58 (core vs its own mean). Three step sizes on three bases survive in live documents;
   final_adr governs. Immaterial to ADR.
5. `lines/adr_v1_design.md:272` — tilt B "adds −$0.84 (**$172.19**)" — engine 172.178, −0.856 → $172.18 / −$0.86, as
   `adr_v1_design.md:310` and `final_adr.md:509` say. Stale rounding from an earlier build; retired scenario; immaterial.
6. V2 euro-only bias range stated three ways with no cell set named: `adr_fx_prereg.md:195` "−0.27 to −0.46" (all six
   cells; W1 O1 is −0.46), `adr_v1_design.md:96,449` and `adr_fx_prereg.md:204` "−0.3 to −0.5" (rounded six-cell
   range), `final_adr.md:145,157` "−0.27 to −0.34" (four promotion cells), DEC-0034 "biased −0.3". All reproduce
   from `fx_scores.csv : bias_pp`; only the framing differs. Immaterial.
7. `lines/adr_v2_upgrade3_reconciliation.md:25,35,241` and `lines/adr_v1_design.md:298` — 2025 like-for-like price
   **3.93** (3.34 / 3.15 / 3.93) — withdrawn by mitigation A (`…_A_sizemix_and_10q.md:225,361`), DEC-0040 and
   `final_adr.md:441–443`; upgrade 3 carries no supersession banner (mitigation A says its tables A.2/A.4 "should be
   read with variant C"). Changes the narrative (2025 flat, 2026 step larger), not a quoted ADR.
8. `lines/final_adr.md:308,551,552`, `adr_v2_thesis.md:49`, DEC-0035 — "within **0.13pp**" — the file gives mean
   0.134, max 0.218; `adr_v2_upgrade6_sustainability_and_score.md:106–107` and `adr_v1_design.md:240` state both.
   Also `final_adr.md:552` ("Sub-regional construction reproduces the disclosed-share four-region term") and
   `adr_v2_thesis.md:49` mislabel the check: `geo_mix_method_check.csv` compares the four-region bucket arithmetic to
   the H term; the sub-regional construction is not what is checked. Immaterial to ADR.
9. `lines/final_adr.md:565` — "The core is **40%** of your ex-FX number" — unsupported (138% of 4Q26 ex-FX; the 41% is
   the unexplained step as a share of the core). Wording only.
10. `lines/final_adr.md:414`, `adr_v2_mitigation_D_origin_language_quarterly.md:204` — "EMEA printed its **first**
    sub-50% English quarter in 2Q26" — `origin_lang_region_quarter.csv`: 4Q25 49.54%, 1Q26 46.17%. Unsupported.
11. `lines/adr_v2_upgrade6_sustainability_and_score.md:87–88` — half-band "±0.976 / ±1.424 pp" beside the $ bands
    176.01–179.36 / 169.80–176.27 — the pp is the **ex-FX** half band (`exfx_envelope.csv : exfx_half_band_pp`) while
    the $ band is the **reported** one (±0.978 / ±1.932). Two objects in one row; `final_adr.md` §6.1 uses the reported
    band consistently. Immaterial.
12. `lines/final_adr.md:346,675` — sub-regional "worth **−$0.24**" — engine −$0.246; DEC-0038 says −0.25. Rounding.
13. `lines/final_adr.md:157` — "the identity's bias is +0.11 to −0.07" — cells run +0.15 to −0.07. Trivial.
14. `dossiers/D4_d4_adr.md:131–138,143–145` — the 2027 path (ex-FX 3.133 / 2.776 / 2.510 / 2.311, 4Q27 **$177.47**, FX
    −0.301 / −0.193 / +0.034 / −0.285) is the superseded card-v3 path (18 Sep) with no supersession banner; the engine
    (`final_adr.md`, DEC-0034/0035) replaces it. Note that FY27 ADR is **$185.21 on both paths** (D4:138 and
    `adr_path.csv`), so the FY figure cannot tell the two apart. `LINES.md` D4 row (l. 33–38) still describes the
    pre-engine state ("+0.46–0.8pp", "residual +2.8–3.6pp"). Immaterial provided the memo reads final_adr.
15. `lines/adr_v1_design.md:36,395`, `adr_v2_thesis.md:54`, `final_adr.md:489,668`, DEC-0035 — FY27 **$185.21** and
    4Q27 **$178.10** quoted without the 4Q27-artefact label at the point of quotation (see Task 3, third check).

RNPL "not named in a filing until 2Q26" — internal inconsistency recorded (filings themselves are another agent's job):

- `final_adr.md:282` ("Airbnb did not name RNPL in a filing at all until 2Q26"), `:575`, `adr_v2_thesis.md:85–86`,
  `adr_v2_mitigation_A_sizemix_and_10q.md:350`, DEC-0041.
- Against: `final_adr.md:282–283` in the same paragraph cites, as a *filed substitute*, "roughly 20% of global GBV came
  from Reserve Now, Pay Later" — that is the 1Q26 shareholder letter, which `dossiers/ADR_A_disclosure_ledger.md:198`
  marks **D031 (1Q26 letter, FILED)** and `corrections_2026-09-18.md:292` places in 8-K 0001193125-26-211816 Ex 99.1,
  filed 2026-05-07. `adr_v1_design.md:223` and the ledger (l. 172, 299) also mark the 3Q25 letter's RNPL sentence
  **D008 FILED**. So under the ledger's own "filed" convention (8-K exhibits count) RNPL was named in a filing in
  Nov 2025 and May 2026. The sentence is true only if "filing" means 10-Q/10-K: `sizemix_10q_sentences.csv` has
  `names_rnpl = no` for all 14 tagged 1Q26 10-Q sentences and `yes` for 9 of 25 in the 2Q26 10-Q, which is the context
  of mitigation A:350. The documents use "filing" in both senses without saying so. No number depends on it.

---

## Task 3 — quarantine checks

### C6 — the sub-regional term (H2 failed; DEC-0038 attribution only)

Verdict: **quarantined in the base path; labelled where it appears; blind spots stated; the 57% is a single-quarter
base-share figure the documents do not date.**

- Code. `exfx.forward()` (`adr_engine/exfx.py:136–164`) builds ex-FX from `core` (carry / mean-reversion / AR1) +
  `bundle_schedule` + `geo_mix_forward()` (four-region, nights-linked) + card terms; it reads no sub-regional file.
  `assemble.build()` (`assemble.py:13–46`) calls only `X.forward()` and `X.envelope()`. `geomix_subregional_term_forward.csv`
  is read solely in `exfx.alternatives()` (`exfx.py:176–181`) for the three "base + sub-regional …" scenario rows, and
  in `workbook.py:266–273` for evidence block G1. `envelope()` half-widths are `core_carry|bundle|exna|geo|unit|los|seats|interaction`
  (`exfx_envelope.csv : halfwidths`) — no sub-regional term in the band either.
- Workbook (`model/ABNB_official_model.xlsx`, openpyxl read-only, not saved). `ADR_Engine` base rows: 62 geo mix
  `=Y91` (block C1 four-region arithmetic), 68 core `=X68` (carry), 73 bundle `=SUM(Y70:Y72)`, 75 mechanism
  `=Y68+Y73+SUM(Y62:Y66)`, 94 `=Y51`, 95 `=Y75+Y94`, 96 `=U7*(1+Y95/100)` — none references block F (rows 121–130,
  scenario values incl. sub-regional 172.79 / tilt B 172.18) or block G (row 132 header "none of this is in the base
  path above"; row 133 "G1 … DEC-0038: attribution + forward row, NOT the base"; row 134 "H2 … FAILS, so the term
  stays out of the base"). `Income_Statement` rows 8–11: row 10 `=ADR_Engine!Y7` (row 7 `=Y96`), row 8 `=Q5*Q10/1000`,
  rows 9/11 y/y; FY columns for rows 8–11 are empty. Cached values are absent (workbook not recalculated in Excel), so
  the numeric tie is by formula inspection plus block E (row 114: 177.6812 / 173.034 / 190.6458 / 188.3776).
- Documents label it attribution-only: `final_adr.md:339–346, 616, 674–675`; `adr_v2_geomix_prereg.md:77–79`;
  `adr_v2_upgrade6…md:79–81`; `adr_v2_thesis.md:87–88, 109–110`; DEC-0038.
- Blind spots stated: `final_adr.md:580–582` (Indian, Emirati, Malaysian, Indonesian, Vietnamese; one each Thailand and
  Singapore; Australia 57% of panel APAC stays); `adr_v2_geomix_prereg.md:85–88` (same list); `adr_v2_thesis.md:88`
  ("India, the Gulf or South-East Asia"); `adr_v1_design.md:269` lists only Indian, Emirati, Indonesian (omits
  Malaysian and Vietnamese — incomplete, not wrong). Data: APAC countries in `stays_yoy_by_country_vmatch.csv` are
  australia, china, new-zealand, singapore, taiwan, thailand; india / united-arab-emirates / malaysia / indonesia /
  vietnam are absent from the whole 34-country panel.
- The 57%. Australia's share of APAC panel stays, complete quarters only: 2Q26 current-quarter (`n_cur`) 56.2%; 2Q26
  **base-quarter** (`n_prior`, the 2Q25 stays as counted in the 2Q26 vintage-matched pair) **57.1%** — this is
  `geomix_country_contributions.csv : share_base` for (APAC, 2Q26, australia) = 0.5709, the share the 2Q26 term is
  built on. Other windows: 3Q25 58.1% (base 58.8%), 4Q25 54.0%, 1Q26 48.6% (base 50.3%), CY2025 53.7%, LTM 3Q25–2Q26
  53.8%, pooled 1Q23–2Q26 52.9%. So "57%" = the 2Q26 base-quarter share; neither document says which quarter, and the
  figure ranges 49–58% across recent quarters.

### C7 — the market-level utilisation panel (mitigation B)

Verdict: **reported as a failure everywhere it appears; read by nothing in the base or the band.**

- `market_panel_scores.csv`: `M2 y_med ~ x_util + FE` (PRIMARY) b 0.0829, se 0.318, p 0.794, CI [−0.539, 0.705],
  n 94 pairs / 92 markets; `M2-exUS` b 0.0411, p 0.956. Registered line b > 0 and p ≤ 0.05 on both → fail.
- Reported as fail: `adr_v2_mitigation_B_market_panel.md` (title, l. 214, 225, 270–271, 331), `final_adr.md:447–460`,
  `adr_v2_thesis.md:80–83`, workbook `ADR_Engine` row 142 ("registered pass line b>0 and p≤0.05 → FAILS").
- Readers of `market_panel_*` outputs outside `market_panel.py`: only `workbook.py:302` (evidence block G4) and the
  Sources row at `workbook.py:385`. Not read by `exfx.py`, `assemble.py`, `envelope()`, `income_statement.py` or
  `build.py`; no `utilisation` term in `exfx_envelope.csv : halfwidths`. The earlier regional test
  (`adr_v1b_utilisation_prereg.md:56–69`) is likewise "FAIL … every region", "reported and not used"; its NA β 0.32
  appears in mitigation B §8 only as a comparison column.

### 4Q27 FX = 0.000 — artefact labelling

Verdict: **labelled in the FX-specific places; unlabelled wherever 4Q27 ADR or FY27 ADR is quoted as a number, and in
the workbook.**

- Labelled: `final_adr.md:209–212` (§2.8), `:495` (warning 1), `:666` (§13 row "FX 0.000 (artefact)");
  `adr_v1_design.md:149` ("0.00 by construction"), `:506`; `adr_fx_prereg.md:209` ("base 4Q26 also spot-held");
  `dossiers/ADR_B_fx_translation_inventory.md:449–450`.
- Not labelled at the point of quotation: `final_adr.md:487` (4Q27 row of §6.1 shows FX 0.000 without note — the
  warning sits eight lines below), `:489` and `:668` (FY27 $185.21 rows, note "nights-weighted, 621.85m nights" — no
  mention that 22.5% of the weight is the artefact quarter); `adr_v2_thesis.md:54` ("FY27 at $185.21 (+2.5%)");
  `adr_v1_design.md:36` (FY27 $185.21, first mention) and `:331, :393, :543–544`; DEC-0035 ($178.10 in the path list).
- Workbook: `ADR_Engine` column AD (4Q27E) row 51 `=SUMPRODUCT(AD45:AD48,AD40:AD43)` and row 94 `=AD51` return the
  identity with no artefact text anywhere in the sheet (a text search for "artefact", "spot-held", "both quarters",
  "base quarter" finds only the block-B "forward = spot held from 2026-09-18" row labels and the DEC-0040 note);
  `Income_Statement!V10` (4Q27 ADR) `=ADR_Engine!AD7` inherits it unlabelled; there is no FY ADR cell in the
  Income_Statement (rows 8–11 FY columns empty), but FY27 revenue `=SUM(S12:V12)` embeds 4Q27 GBV.
- `lines/final_income_statement.md` quotes no 4Q27 ADR, 4Q27 FX or FY27 ADR; its FY27 revenue and margin (33.97% vs
  Street 36.45%, l. 236, DEC-0042) embed the 4Q27 ADR without the label.
- Size of the artefact for FY27 ADR: 4Q27 carries 139.77 / 621.85 = 22.5% of FY27 nights, so each 1pp of 4Q27 FX moves
  FY27 ADR by ≈ $0.40 (and FY27 GBV by ≈ $0.25bn); the engine's own 4Q27 P10/P90 is −4.3 / +5.1pp.

---

## Files used

Engine outputs: `adr_path.csv`, `adr_scenarios.csv`, `fx_scores.csv`, `fx_forecast_asof.csv`, `fx_currency_contributions.csv`,
`exfx_history.csv`, `exfx_forward_base.csv`, `exfx_envelope.csv`, `geo_mix_method_check.csv`, `reconcile_annual.csv`,
`geomix_subregional_term.csv`, `geomix_subregional_term_forward.csv`, `geomix_h2_scores.csv`, `geomix_country_contributions.csv`,
`origin_lang_rotation_ltm.csv`, `origin_lang_price_summary.csv`, `origin_lang_price_mix_effect.csv`, `origin_lang_global_quarter.csv`,
`origin_lang_region_quarter.csv`, `origin_proxy_review_language_by_region_year.csv`, `sizemix_routes.csv`, `sizemix_rebased_plug.csv`,
`sizemix_10q_sentences.csv`, `market_panel_scores.csv`, `stays_yoy_by_country_vmatch.csv`, `00_summary.json`, `workbook_refs.json`;
`data/processed/q3nowcast/H/adr_history_components.csv`; `data/processed/overnight/02_kpi_panel_quarterly.csv`.
Code: `adr_engine/exfx.py`, `assemble.py`, `workbook.py`, `run.py`, `reconcile.py`, `sizemix_adjudication.py`, `tests/`.
Workbook: `model/ABNB_official_model.xlsx` sheets `ADR_Engine`, `Income_Statement` (read-only).
