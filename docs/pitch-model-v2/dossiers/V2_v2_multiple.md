# V2 — Exit multiple and the turns-per-point rule

## 1. Header
- Line: V2 · Judge's question: "Why 16.5x, and why does one point of growth move the multiple half a turn?"
- Digger: opus · Date: 2026-09-18 · Commit: e39d9e4

Note on the brief: it names commit `f1ce2cd`; the working tree is at `e39d9e4` on `theo/pitch-model-v2`. All
paths and values below are read at `e39d9e4`.

**The two-sentence answer.** 16.5x is a *judgement*: the mean of three family medians — ABNB's own
2023–26 time series (17.16x), a 19-name peer cross-section (12.79x) and a 10-year fade DCF at the FY27 exit
(19.71x) — which averages 16.554x and is rounded to the nearest half turn. Half a turn per point is a
*descriptive regression*: +0.4860 EV/EBITDA turns per percentage point of forward revenue growth, HAC 95%
CI [0.3172, 0.6548], four parameters, n = 35 overlapping monthly 12-month changes. The slope does not
produce the level (16.5 + β(g − g₀) = 16.5 at the anchor for any β, including zero), and the level was
blended on a growth vintage the final model has since replaced.

## 2. The number

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| bear | FY27E exit EV/adj. EBITDA | 13.5 | 10.671 | 15.120 | x | WS12 blend 13.361, rounded to nearest half turn; low/high = the three family medians; fit on 5 Sep scenario growth 4.269% |
| base | FY27E exit EV/adj. EBITDA | 16.5 | 12.792 | 19.713 | x | WS12 blend 16.554, same rounding; fit on 5 Sep scenario growth 12.269% |
| bull | FY27E exit EV/adj. EBITDA | 18.5 | 13.889 | 23.051 | x | WS12 blend 18.737, same rounding; fit on 5 Sep scenario growth 15.270% |
| base | turns per point of forward growth | 0.4860 | 0.3172 | 0.6548 | x per pp | 12-month-change regression, dependent Δ12 EV/**LTM** adj. EBITDA, 4 params (intercept + growth + 10y yield + NDX fwd P/E), Newey–West 12 lags, R² 0.451, n = 35 monthly changes, 2023-11-30 → 2026-09-04, `as_of` 2026-09-12 |
| base | turns per point, W2 restriction | 0.4765 | 0.3100 | 0.6431 | x per pp | same spec, n = 33, first obs 2024-01-31 |
| base | turns per point, **levels** spec W2 | 0.1948 | −0.3233 | 0.7129 | x per pp | EV/**NTM** EBITDA in levels, n = 33 — **CI contains zero** |
| — | spot the model uses | 181.94 | — | — | USD | 4 Sep 2026 close, `data/processed/abnb_daily_close.csv` (last row); hard-coded as `LAST_PRICE` in `12_exit_multiples_and_targets.py`; every "upside" in `13_valuation_summary.csv` and `12_exit_multiple_recommendation.csv` is measured from it |
| base | FY27E net cash **ex float** | 10,116.0 | 8,592.6 (bear) | 11,329.3 (bull) | $M | `13_model_annual.csv` `net_cash`, FY27 rows; rolled forward from $9,593M actual at 30 Jun 2026 less buybacks **and** RSU tax withholding (`model/assumptions.md` line 78, "CORRECTS the earlier net-cash path") |
| — | spot-basis net cash ex float | 9,569 | — | — | $M | `data/processed/abnb_multiples_today.csv` `net_cash_ex_float_musd`, 30 Jun 2026: cash $6.8bn + short-term investments $5.2bn − notes $2.5bn; **funds held for clients $12,224M excluded** (SEC XBRL 10-Q, `model/assumptions.md` line 27) |
| base | FY27E modelled diluted shares | 574.5982 | 571.3972 (bull) | 580.4293 (bear) | m | `13_model_annual.csv` `shares_end`, FY27 rows; roll-forward from the 597.0M anchor after the 7 Sep 1H26 double-count fix |
| — | spot-basis diluted shares | 597.0 | — | — | m | 2Q26 **diluted weighted-average** shares (SEC XBRL), used as a *proxy* for a 30 Jun 2026 period-end fully diluted count — `model/assumptions.md` line 28 and "Model conventions" §2 |

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| exit_multiple_x | bear | FY27 | 13.5 | x | WS12 blend 13.361 rounded to the nearest half turn, fit on the 5 Sep scenario growth 4.269%; `12_exit_multiple_recommendation.csv` |
| exit_multiple_x | base | FY27 | 16.5 | x | WS12 blend 16.554 rounded to the nearest half turn, fit on the 5 Sep scenario growth 12.269%; `12_exit_multiple_recommendation.csv` |
| exit_multiple_x | bull | FY27 | 18.5 | x | WS12 blend 18.737 rounded to the nearest half turn, fit on the 5 Sep scenario growth 15.270%; `12_exit_multiple_recommendation.csv` |
| exit_multiple_x | bear_slope | FY27 | 12.29 | x | 13.5 + 0.4860 x (1.7772 − 4.269); slope-corrected to the final 6–7 Sep model growth; `receipts/V2/growth_vintage_reanchoring.csv` |
| exit_multiple_x | base_slope | FY27 | 16.03 | x | 16.5 + 0.4860 x (11.3086 − 12.269); slope-corrected to the final 6–7 Sep model growth; `receipts/V2/growth_vintage_reanchoring.csv` |
| exit_multiple_x | bull_slope | FY27 | 20.76 | x | 18.5 + 0.4860 x (19.9224 − 15.270); slope-corrected to the final 6–7 Sep model growth; `receipts/V2/growth_vintage_reanchoring.csv` |
| slope_turns_per_pt | base | all | 0.4860 | x per pp | descriptive regression: Δ12 EV/LTM adj. EBITDA on Δ12 forward-growth proxy, controls 10y yield + NDX fwd P/E, Newey–West 12 lags, 4 params, n = 35, R² 0.451; `valuation_v1/regression_reproduction.csv` |
| slope_ci_low | base | all | 0.3172 | x per pp | HAC 95% lower bound, same fit |
| slope_ci_high | base | all | 0.6548 | x per pp | HAC 95% upper bound, same fit |
| spot_usd | base | all | 167.51 | USD | 16 Sep 2026 close, memo v3 |
| net_cash_ex_float_musd | base | all | 9569 | $M | 30 Jun 2026: cash $6.8bn + short-term investments $5.2bn − notes $2.5bn, funds held for clients $12,224M excluded; SEC XBRL 10-Q via `data/processed/abnb_multiples_today.csv` (`model/assumptions.md` line 27 says $9,593M — a $24M disagreement) |
| diluted_shares_m | base | all | 597.0 | m | 2Q26 diluted weighted-average shares (SEC XBRL), used as a proxy for a 30 Jun 2026 period-end fully diluted count; `data/processed/abnb_multiples_today.csv`, `model/assumptions.md` line 28 |

The last three rows are the **spot basis** memo v3 prices on. The FY27-exit basis the football field uses is
different — net cash $10,116.0M and 574.5982m shares (`13_model_annual.csv`, base FY27) — and at one price
the two bases differ by about 1.5 turns. Do not mix them in a row.

**Which of these are regressions and which are judgements.**

- **Descriptive regressions (fitted, with intervals):** the +0.4860 turns-per-point slope and its W1/W2/levels
  variants; the two time-series family inputs (a banded median, n = 18/24/32 months, and an OLS on NTM growth
  + margin, n = 45, b_growth +0.477, t 2.3, R² 0.24); the five peer cross-sectional log-linear fits
  (n = 12–18, R² 0.19–0.53). All are labelled `descriptive_only` by the governing package; none is a scored
  point-in-time forecast.
- **Judgements (chosen, not estimated):** which three families count and that they are equally weighted;
  which five of the ten cross-sectional specs enter the family median (the EV/EBITDA-on-margin and
  SBC-loaded fits were excluded as artefactual); the DCF's WACC 10% / terminal g 3% / 10-year fade; rounding
  the blend to the **nearest half turn**; the ~30 Sep 2027 target convention; treating funds held for clients
  as excluded from net cash; and using a weighted-average share count as a period-end proxy.
- **Arithmetic identities (no estimation at all):** every price. `price = (x × FY27 adj. EBITDA + FY27 net
  cash) / FY27 shares`. Base: `(16.5 × 5,685.7698 + 10,115.9869) / 574.5982 = $180.876286`. One turn is
  worth **$9.8952** a share in the base, $6.9378 in the bear, $11.5854 in the bull.

## 3. Derivation chain

**Leg A — the level (13.5 / 16.5 / 18.5x).**
1. `data/processed/overnight/12_abnb_multiples_monthly.csv` + `12_abnb_multiples_history.csv` (ABNB's own
   monthly PIT multiples) and `12_peer_multiples.csv` (19 names, 4 Sep 2026) + `data/processed/abnb_valuation_scenarios.csv`
   (the **5 Sep** operating cases: FY27 growth 4.269 / 12.269 / 15.270%) →
2. `analysis/src/overnight/12_exit_multiples_and_targets.py` — three families, ten methods, five excluded
   from the blend →
3. `data/processed/overnight/12_exit_multiple_evidence.csv` (one row per scenario × method, `used_in_blend`) →
4. `data/processed/overnight/12_exit_multiple_recommendation.csv`, columns `time_series_x` /
   `cross_section_x` / `intrinsic_x` / `blend_x` / `recommended_x` = **13.361→13.5**, **16.554→16.5**,
   **18.737→18.5** (`recommended = round(blend × 2) / 2`) →
5. adopted in `model/assumptions.md` line 81 ("**REPLACES 18 / 22 / 25.5x**").

**Leg B — the price the level implies.**
1. `data/processed/overnight/13_model_annual.csv` FY27 rows (the **6–7 Sep** model: adj. EBITDA, net cash,
   shares_end) →
2. `analysis/src/overnight/13_driver_model.py` →
3. `data/processed/overnight/13_valuation_summary.csv` lens `EV / adj. EBITDA, FY27E` = **$108.4647 /
   $180.8763 / $234.1564**, and `Football field mean` = $74.1782 / $156.7868 / $228.1826 →
4. re-derived independently in `data/processed/forecast_methods/valuation_v1/football_field_reconciliation.csv`.

**Leg C — the turns-per-point slope.**
1. `data/processed/overnight/12_abnb_multiples_monthly.csv` (month_end, EV/LTM adj. EBITDA, forward-growth
   proxy, 10y yield, NDX forward P/E) →
2. `analysis/src/forecast_methods/valuation_v1/run.py` (`fit()`, Newey–West 12 lags, 4 params) →
3. `data/processed/forecast_methods/valuation_v1/regression_reproduction.csv`, row
   `spec=12_row_changes, dependent=ev_ltm_ebitda_x, window=ALL`, column `slope_turns_per_growth_pp` =
   **0.4860216575**, `ci95_lo/hi` = 0.31722947 / 0.65481385 →
4. applied in `growth_multiple_price_bridge.csv` as `multiple = 16.5 + 0.486022 × (g − 11.3086)` over the
   B3 FY27 growth band 9.18 / 10.35 / 11.52% → **15.465 / 16.034 / 16.603x** → **$170.64 / $176.27 / $181.89**.
   PIT stability of the same spec: `guide_date_refits.csv`.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 5 Sep 2026 | `research/notes/2026-09-05_driver-model.md`, `data/processed/abnb_valuation_scenarios.csv`, `abnb_valuation_sensitivity.csv` | exit 18 / 22 / 25.5x; base 12-month target $248 | **superseded** by WS12 (6–7 Sep). Both CSVs are still entirely on the withdrawn basis (`price_ev_ebitda` base $247.82 at 22x) |
| 6–7 Sep 2026 | `analysis/src/overnight/12_exit_multiples_and_targets.py` → `12_exit_multiple_recommendation.csv` | 13.5 / 16.5 / 18.5x from an equal-weight mean of three family medians, rounded to the nearest half turn | **governs the level**. I replicated all three blends: max abs diff 0.0005, all three round to the committed value |
| 6–7 Sep 2026 | `research/notes/overnight/12_valuation-multiple-regime.md` | "each point of forward revenue growth is worth about half a turn": levels b = +0.48, t 8.3, R² 0.68, **DW 0.93**, so "read the 12-month-change specs, where the growth coefficient is +0.49, t 5.6, R² 0.45"; margin moves it zero; a defensible ABNB multiple anchored on BKNG is **12–16x** | **origin of the rule**; superseded on the coefficient itself by `valuation_v1` (+0.4860, HAC CI). Its 12–16x BKNG anchor sits *below* the adopted 16.5x and is not reconciled anywhere |
| 7 Sep 2026 | `model/assumptions.md` lines 27, 28, 77, 78, 81 + "Model conventions" | adopts 13.5/16.5/18.5x; FY27 net cash ex float $8.6 / **10.1** / 11.3bn; FY27 shares 589/**575**/562M; 597M weighted-average anchor as a period-end proxy; funds held for clients excluded; ~30 Sep 2027 target date | **governs the bridge inputs** |
| 7 Sep 2026 | `research/notes/overnight/25_conventions-and-cleanup.md`, `13_driver-model-build.md` | the FY28 lens is discounted one year, so all six field lenses sit at ~30 Sep 2027; base field mean $160.22 → **$156.79** | **governs**; supersedes `25_valuation_conventions.csv`, which is stale (still undiscounted FY28, mean $160.22) |
| 7 Sep 2026 | `docs/overnight/FINAL_SUMMARY.md` lines 29–39 | "The recommended set is 13.5 / 16.5 / 18.5x… **Growth is the only fundamental that has ever moved this multiple: +0.48 turns per point of forward revenue growth. Margin moves it zero.**" | **superseded on causality** by V (12 Sep); see §7 |
| 11 Sep 2026 | `deck/drafts/memo_v0_2026-09-11.md` lines 48–55, 100–101 | branch analogues $140–152 / $170–185 / $205–215, with the bull branch stated as "~2pp of growth, ~+1 turn"; at $174.54 the stock is 16.1x against "an independently derived fair band of 13.5–18.5x, base 16.5x" | **superseded as the pitch** by memo v3; the "+2pp → +1 turn" phrasing is where "half a turn" reaches the page |
| 12–13 Sep 2026 | `05_backtests/V_VALUATION_RECONCILIATION.md` + `analysis/src/forecast_methods/valuation_v1/` | verdict **PARTIAL**. Slope +0.4860 [0.3172, 0.6548], n = 35, 4 params, `status=descriptive_only`, `source_vintage_status = "inherited monthly PIT label; source vintages unverified"`, **0 scored W1 cells, 0 scored W2 cells**; "a slope does not identify the intercept"; no target adopted | **GOVERNS this line** |
| 12 Sep 2026 | `05_backtests/REFUTE_V_mechanism.md`, `REFUTE_V_vintage.md`, `REFUTE_V_power.md` | all three return **survived** on the exact arithmetic sentence. `_power` additionally finds the W1 change regression requires an **undisclosed Jan–Oct 2023 exclusion** and that the level-regression HAC intervals do not reproduce from the literal stated spec. `_mechanism` corrects one turn to **$9.90**, not $9.89 | **governs the caveats** |
| 17 Sep 2026 | `deck/drafts/memo_v3_short_2026-09-17.md` | the pitch is now a **short**: $167.51 (16 Sep), 597m diluted, net cash ex-float $9.6bn, **15.7x Street / 19.0x our short case** on FY27E adj. EBITDA; PT base $143, prob.-weighted $148, short case $125; "about 1.3 turns at +0.4–0.5 turns per point" | **governs the memo framing**. It does **not** use 13.5/16.5/18.5x and does not cite the football field |

**Web fetches: zero.** The rule allows five, for public filings and press releases only. Everything §2 needs
already exists in-repo with an SEC XBRL provenance note (`model/assumptions.md` lines 27–28); a live quote is
neither a filing nor a press release, so the stale-spot problem in §7 is reported, not patched.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/V2/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id V2 --watch analysis/src/forecast_methods/valuation_v1 --watch data/processed/forecast_methods/valuation_v1 --cmd "python3 analysis/src/forecast_methods/valuation_v1/run.py"` · Exit: 0 · Wall: 1.2s · Interpreter: `python3` (3.13, system framework build; pandas 3 not needed)
- Output: `data/processed/forecast_methods/valuation_v1/regression_reproduction.csv` cell `slope_turns_per_growth_pp`, row `spec=12_row_changes / dependent=ev_ltm_ebitda_x / window=ALL` = **0.4860216575119952** · Committed value: 0.4860216575119952 · Tolerance: ±1e-9 (observed max abs diff across all regenerated CSVs 2.0e-13) · **Match: yes**
- Also reproduced exactly (max abs diff 0.0): `football_field_reconciliation.csv` (13.5 / 16.5 / 18.5x →
  $108.4647 / $180.8763 / $234.1564) and `memo_branches.csv`. `growth_multiple_price_bridge.csv` and
  `guide_date_refits.csv` matched to 2.8e-14 and 1.7e-13. `restored: true`, watched paths clean afterwards.
- Second receipt: `data/processed/pitch_model_v2/receipts/V2/receipt_pytest.json` —
  `python3 -m pytest analysis/src/forecast_methods/valuation_v1/tests -q`, exit 0, wall 1.0s, **6 passed**,
  zero files changed.
- **One honest failure inside the receipt.** `input_manifest.json` is flagged changed on every re-run. The
  cause is not a data change: the committed SHA-256s were computed on a CRLF checkout (the V package and all
  three refuters ran under PowerShell). I verified that all 13 inputs hash to the committed value after
  `b.replace(b"\n", b"\r\n")` — e.g. `13_model_annual.csv` → `e97388cd…` only under CRLF. So the package's
  integrity chain **cannot be verified on a POSIX checkout as shipped**; the content is byte-identical modulo
  line endings. `run_summary.json` / `final_run_receipt.txt` also differ, on `runtime_seconds` only, and the
  PDF/PNG differ on embedded render timestamps.
- My own cross-checks (arithmetic only, no package code re-run, written under the receipts directory):
  `exit_multiple_blend_replication.csv`, `growth_vintage_reanchoring.csv`, `priced_in_cross_check.csv`,
  `pit_slope_stability.csv`, `v2_cross_check_summary.json`.

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 (monthly calendar restriction, **not** the harness) | 35 changes / 12 reported quarters | turns per pp, Δ12 EV/LTM adj. EBITDA | +0.4860 [0.3172, 0.6548] | 0 (no relation) | n/a | n/a | "reference ≈ +0.48 reproduces within its CI" (V note, 2026-09-12 23:33 UTC, written before the run) | **pass** |
| W2 (monthly calendar restriction) | 33 changes / 12 reported quarters | same | +0.4765 [0.3100, 0.6431] | 0 | n/a | n/a | same | **pass** |
| W1, levels spec | 45 months | turns per pp, EV/NTM EBITDA level | +0.4825 [0.1182, 0.8468] | 0 | n/a | n/a | "also report the level regression" (no sign screen) | pass (wide) |
| W2, levels spec | 33 months | same | +0.1948 [−0.3233, 0.7129] | 0 | n/a | n/a | same | **fail — CI contains zero** |
| PIT guide-date refits, W1 | 8 origins that fit (6 abstain as underpowered) | slope at each guide date, strictly earlier months only | 3 origins positive with CI excluding zero; **1 origin significantly negative** (6 Aug 2024: −1.405 [−2.254, −0.557]); 4 span zero | 0 | n/a | n/a | "expanding guide-date fits… labelled inherited-vintage diagnostics" | **fail as a PIT rule** |
| PIT guide-date refits, W2 | 6 origins that fit | same | 4 of 6 positive with CI excluding zero; latest (7 May 2026) **+0.4271 [0.3756, 0.4786]** | 0 | n/a | n/a | same | partial |
| Harness-scored quarterly cells | **0 / 0** | any scored forecast of price or multiple | none exist | — | — | — | CLAUDE.md rule 2: "a result must survive both to be quoted" | **not testable** — the frozen harness has no price or multiple target |
| Blend replication (my own) | 3 scenarios × 3 families | `round(mean(family medians) × 2)/2` | 13.361 / 16.554 / 18.737 → 13.5 / 16.5 / 18.5 | — | — | — | reproduce `12_exit_multiple_recommendation.csv` | **pass** (max abs diff 0.0005) |

Only 5 of the 15 fitted guide-date refits have a CI containing the headline +0.486. At the latest PIT origin
the slope is **+0.419 (W1) / +0.427 (W2)**, about 14% below the full-sample number — the full sample runs to
4 Sep 2026, i.e. it uses data no guide date could see.

**Strongest known failure:** the 13.5 / 16.5 / 18.5x set was blended on the superseded 5 Sep scenario growths
(4.27 / 12.27 / 15.27%) which the 6–7 Sep final model replaced with 1.78 / 11.31 / 19.92%, so applying the
line's own +0.486 turns-per-point rule to that revision gives **12.29 / 16.03 / 20.76x** — the base is ~0.5
turns too high (−$4.62 a share), the bull ~2.3 turns too low (+$26.20), and the bear-to-bull multiple spread
should be 8.5 turns, not 5.

## 7. Kill list and consistency

**Kill-list check (AGENT_BRIEF §6): none.** V2 quotes no item from that list. Two adjacent hazards:

- **Locally withdrawn, not on §6:** the 18 / 22 / 25.5x set and the $248 base target
  (`FINAL_SUMMARY.md`: "Three claims to stop making: the 18/22/25.5x exit multiples"). They are still live in
  the tree — `13_valuation_summary.csv` carries a lens literally named
  `"EV / adj. EBITDA, FY27E (5 Sep multiples 18/22/25.5x)"` (base **$235.30**), and
  `abnb_valuation_scenarios.csv` / `abnb_valuation_sensitivity.csv` are entirely on that basis. Do not quote
  any price from those two CSVs.
- **The governing note states the rule too strongly.** `FINAL_SUMMARY.md` says "Growth is the **only**
  fundamental that has **ever** moved this multiple." The later governing package (V, 12 Sep) contradicts
  that: the relation is `descriptive_only`, monthly-overlapping, with inherited component vintages, and
  "a universal causal +0.48 rule is unsupported" (W2 level coefficient includes zero). The defensible
  sentence is: *in 2023–26, forward revenue growth is the only fundamental with a measurable association with
  ABNB's multiple; margin has none in any specification.* `REFUTE_V_power` adds that the W1 change fit needs
  an **undisclosed Jan–Oct 2023 exclusion** that the spec description does not state.

**Conflicts.**

1. **Four spot prices in circulation.** The valuation model uses **$181.94 (4 Sep)**; memo v0 uses $174.54;
   `valuation_v1`'s positioning panel uses $170.19 (11 Sep close, Yahoo); memo v3 uses **$167.51 (16 Sep)**.
   Every "upside" percentage in `13_valuation_summary.csv` and `12_exit_multiple_recommendation.csv` is
   measured off $181.94 and is therefore 8.6% stale. On the base FY27 bridge, $180.88 is −0.6% vs $181.94 but
   **+8.0%** vs $167.51.
2. **The growth vintage the multiples were fit on no longer exists** (the §6 failure). Quantified in
   `growth_vintage_reanchoring.csv`.
3. **The base 16.5x is above the regime note's own BKNG-anchored band of 12–16x** and above the
   implied-equivalent multiple of the six-lens field (14.066x, `REFUTE_V_mechanism` attack 3). Three
   "independent" anchors give 16.5x, 14.1x and 12–16x and none supersedes the others in writing.
4. **Two different scenario axes are both called bear/base/bull.** 13.5/16.5/18.5x indexes *operating*
   cases (FY27 growth 1.78/11.31/19.92%); the 15.47/16.03/16.60x band indexes *kernel weights* w = 0.33/0.5/⅔
   on the **base** case (growth 9.18/10.35/11.52%). They are not the same bear/base/bull and must never share
   a row. The base model's own FY27 growth (11.3086%) is not any of 9.18/10.35/11.52 either — it is 0.21pp
   below the w = ⅔ value, worth 0.10 turns.
5. **memo v3 does not use this line at all.** It frames 15.7x Street / 19.0x short case at $167.51 on
   *spot-basis* cash and shares (597m, $9.6bn ex-float), not FY27-exit cash and shares (574.6m, $10.1bn).
   The two bases differ by ~1.5 turns at the same price; the deck must not mix them.
6. **Minor:** net cash ex-float at 30 Jun 2026 is $9,593M in `model/assumptions.md` and $9,569M in
   `abnb_multiples_today.csv` — a $24M, 0.04-a-share disagreement. One turn is $9.90, not the $9.89 printed in
   the V note (`REFUTE_V_mechanism` attack 8).
7. **Provenance:** `guide_date_refits.csv` carries `source_vintage_status = "inherited monthly PIT label;
   source vintages unverified"` on every fitted row, and `monthly_vintage_audit.csv` has
   `source_component_timestamps_complete = False` on **all 47** rows. The forward-growth proxy and the NDX
   valuation input have no documented vintage. Label the slope a diagnostic, never a PIT forecast.

## 8. Open choices

1. **Re-anchor the exit multiples to the final model's growth, or keep 13.5/16.5/18.5x?** — options:
   (a) keep the published set and add one footnote that it was fit on the 5 Sep growth vintage; (b) re-run
   `12_exit_multiples_and_targets.py` against `13_model_annual.csv` growths and re-blend; (c) apply the
   line's own slope as a first-order correction to **12.3 / 16.0 / 20.8x**. — recommendation: **(c) for the
   memo, (b) before finals** — why: (a) leaves the deck asserting a rule it visibly violates, and the first
   judge who multiplies 0.486 by the growth revision finds it; (c) is one line of arithmetic the line already
   owns; (b) is the right answer but the cross-section and DCF legs need re-running on the new margins and
   FY28 growths, which is a half-day, not a footnote.
2. **Which multiple basis the memo quotes** — options: (a) FY27-exit basis (16.5x, 574.6m shares, $10.1bn
   FY27 net cash), (b) spot basis (597m, $9.6bn at 30 Jun 26) as memo v3 does, (c) both, labelled. —
   recommendation: **(b), with (a) in the appendix** — why: memo v3 is a short with a 3–6 month horizon and
   its reader prices the stock today; the FY27-exit basis flatters the price by ~1.5 turns purely through
   forecast cash and buybacks, which is exactly the criticism a judge will make of a short.
3. **Which spot and date the whole deck uses** — options: (a) freeze $167.51 / 16 Sep with every upside
   recomputed; (b) refresh to the latest close before submission and recompute once; (c) leave $181.94 in the
   model outputs and restate only in prose. — recommendation: **(b), with a single named refresh date** —
   why: (c) is what is in the tree now and it puts a −0.6% and a +8.0% upside on the same base number in two
   documents.
4. **How to state the slope on the page** — options: (a) "+0.5 turns per point"; (b) "+0.49 turns per point
   (95% CI 0.32–0.65, n = 35 overlapping monthly changes, descriptive)"; (c) "a third to two-thirds of a turn
   per point". — recommendation: **(b)** — why: the point estimate is the honest headline, and the CI is what
   converts the FY27 growth band (2.34pp of kernel-weight indeterminacy) into 0.74–1.53 turns, i.e. $7.3–15.2
   a share. Never say "the only fundamental that has ever moved it" (§7).
5. **Whether the six-lens football field appears at all** — options: (a) keep it (base mean $156.79);
   (b) drop it and show the single EV/EBITDA lens; (c) show it only as a dispersion exhibit with the
   implied-equivalent 14.07x named. — recommendation: **(c)** — why: all three refuters agree the six lenses
   are one operating case seen six ways, not six observations; presenting the mean beside $180.88 as
   corroboration is the single easiest thing for a judge to break.
6. **Whether to reconcile 16.5x with the 12–16x BKNG anchor** — options: (a) drop the BKNG anchor;
   (b) keep both and state the bridge (BKNG 12.8x + ~2.3 turns balance sheet + ~0.7 turns growth − an SBC
   charge); (c) adopt the BKNG-anchored band as the base. — recommendation: **(b)** — why: the bridge is
   already written in `12_valuation-multiple-regime.md` and it is the strongest comparable argument the line
   has; leaving 16.5x and "12–16x" unreconciled in the same repo is the gift.

## 9. Judge Q&A
1. Q: Why 16.5x and not 15x or 18x? A: It is not estimated, it is a chosen blend. Three families —
   ABNB's own 2023–26 multiple at comparable forward growth (17.16x), a 19-name peer cross-section
   (12.79x) and a 10-year fade DCF at the FY27 exit at WACC 10% / g 3% (19.71x) — averaged equally give
   16.554x, rounded to the nearest half turn. The families disagree by seven turns, so the honest range is
   12.8–19.7x and 16.5x is its centre, not its conclusion. Two things it is *not*: it is not produced by the
   growth regression (16.5 + β(g − g₀) equals 16.5 at the anchor for any β, including zero), and it is not
   reconciled with the same workstream's BKNG-anchored 12–16x band.
2. Q: Why does one point of growth move the multiple half a turn — and would you bet on it? A: +0.4860
   turns per percentage point, from regressing the 12-month change in EV/LTM adjusted EBITDA on the 12-month
   change in the forward-growth proxy, controlling for the 10-year yield and the Nasdaq-100 forward P/E:
   four parameters, Newey–West 12 lags, n = 35 overlapping monthly changes spanning only 12 reported
   quarters, R² 0.45, 95% CI [0.32, 0.65]. It survives both calendar windows in changes (+0.486 / +0.477) and
   it is economically legible — the 2021–24 de-rating is roughly two-thirds explained by forward growth going
   from 74% to 13%. I would not bet on it as a *causal* rule: the level version fails on W2 (+0.195, CI
   [−0.32, 0.71]); refit point-in-time at each guide date it was significantly **negative** in August 2024 and
   only turned reliably positive from November 2025; at the latest PIT origin it is +0.42, not +0.49; and the
   component vintages are unverified on all 47 monthly rows. It is a sensitivity, not a forecast.
3. Q: Your own rule says the multiple follows growth. Your final model cut base FY27 growth and raised bull
   FY27 growth after you set the multiples. Did you update them? A: No, and that is this line's real weakness.
   The blend was fit on the 5 Sep cases (4.27 / 12.27 / 15.27%); the 6–7 Sep model replaced them with
   1.78 / 11.31 / 19.92%. Applying our own +0.486 gives 12.29 / 16.03 / 20.76x — base $176.26 instead of
   $180.88, bull $260.35 instead of $234.16, bear $100.06 instead of $108.46. The fix is arithmetic and it is
   in `growth_vintage_reanchoring.csv`; the better fix is re-running the blend, which also needs the new FY28
   growths and margins. Note the direction: it makes the base modestly *worse* and the bull materially
   *better*, so it is not a fix we are hiding for convenience.

## 10. Grade
Grade: B — the package reproduces exactly (exit 0, slope to 1e-13, all three multiples and all six lens
prices to the cent, six tests green) and every source note is traceable, but the object is avowedly
descriptive: zero scored W1/W2 harness cells exist, the levels spec fails W2, the point-in-time refits are
sign-unstable, and 16.5x is a rounded judgement fit on a growth vintage the final model has replaced.
