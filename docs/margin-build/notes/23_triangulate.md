# WS23 — triangulation: the final margin model, its forecasts, the workbook

Margin build run, 14 Sep 2026. Slug `23_final_model`. Method name `final-margin`.
Interpreter `py -3.13`. **The document Krish should read is `docs/margin-build/SYNTHESIS.md`;
this note is the procedural record** — what ran, the exact commands, the tables with n, what
failed, and the parameter count.

---

## Bottom line

**3Q26 adjusted EBITDA margin 49.94% / $2,399M against a Street 49.78% / $2,361.5M.** The
combination object `final-margin|combined|stack_clip` passes its pre-registered primary test
(beats the seasonal naive at h=0 and h=1 in both windows and both weightings) and is the best
object in the build on **dollar** adjusted EBITDA at h=0 in both windows, on **2 declared
parameters**. It **fails** its pre-registered secondary test at h=1 (1.20x / 1.28x the raw
Street), so 4Q26 is quoted from the Street, and it **fails outright at h=2 in W2** (1.024x the
naive), so 2027 is a scenario.

---

## Commands

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/23_final_model/run.py            # everything, ~4 min, exit 0
# or, step by step:
py -3.13 analysis/src/margin_build/23_final_model/combine.py        # 25 s  -> registry + scores
py -3.13 analysis/src/margin_build/23_final_model/diagnostics.py    # 20 s  -> leave-one-out etc
py -3.13 analysis/src/margin_build/23_final_model/forecast.py       # 10 s  -> forecast set + card
py -3.13 analysis/src/margin_build/23_final_model/workbook.py       #  5 s  -> model/ABNB_margin_model.xlsx
py -3.13 analysis/src/margin_build/10_harness_margin/score.py       # 47 s  -> rescore, run ONCE
```

`MARGIN_SKIP_SCORE=1` on `run.py` skips the scorer. **Never run this while another method
package is running** — they all shell out to `score.py` (WS20 §10).

## Pre-registration

`analysis/src/margin_build/23_final_model/prereg.json`, written before any result. It fixes the
member pool per horizon, the weight rule (`inverse-MAE, shrinkage λ = 0.5 toward equal weights,
leave-future-out`), the guide-clip rule, the four spec names with `stack_clip` named primary, the
interval recipe (split conformal on the combination's own PIT errors), the declared parameter
count, the revenue legs, the pass line and the failure policy. Four tests planned; four run; two
failed and are reported below.

## What was built

| step | script | output |
|---|---|---|
| 1 combination | `combine.py` | PIT + full_sample replay at W1/W2 h=0,1,2 and LIVE h=0..5 for `adj_ebitda_margin_pct` and `adj_ebitda_musd`, four specs; **1,152 registry rows**; weights table; conformal table; scores with NW(1) and sign tests against all seven baselines |
| 2 diagnostics | `diagnostics.py` | leave-one-member-out, the no-clip variant, the Street-independent variant, member-by-member MAE, shock vs calm, the Street-independent LIVE point |
| 3 forecast | `forecast.py` | adopted path rule, bands, reconciled six-line stack (history 1Q21-2Q26 + forecast 3Q26-4Q27 x 3 scenarios), full quarterly P&L to EPS, annual FY26-28, vs-consensus, scenario grid, seasonality, macro sensitivity, FY26 floor break-even, the 5 Nov card, the budget identity |
| 4 workbook | `workbook.py` | `model/ABNB_margin_model.xlsx` — README, Inputs, Lines, Bridge (formula cells for the identities), Scenarios, Consensus, Seasonality, Weights, Card |

## The combination, formally

At vintage `v`, target quarter `t`, horizon `h`:

```
w_i^inv  = (1/MAE_i(prior)) / sum_j (1/MAE_j(prior))       prior = quarters printed before t
w_i      = (1 - lambda) * w_i^inv + lambda * (1/K),        lambda = 0.5, K = |pool|
raw      = sum_i w_i * p_i(v, t)
point    = min(raw, y[t-4] + g)  if the quarterly sentence in force at v is a ceiling
           max(raw, y[t-4] + g)  if it is a floor
           raw                   otherwise
```

Pool at h=0 (six members): M5 `dispersion_conditioned|rw_hl4_med`, M5
`street_plus_flowthrough|rw_hl4`, the `street` baseline, M3 `actual_given_guide|nov_sentence_pin`,
M2 `q_sentence_direction|k_fit_median`, and `FAMILY_A` (the equal mean of M1 `b_elastic_rw`,
M6 `l0_rw`, M2 `sarima_margin|lines_aicc`). At h=1 the pool drops M5-disp and M2-sentence
(the latter is n=1 at h=1); at h=2 it is M3 + M2 `incremental_margin|k8_median` + `FAMILY_A`.
Excluded a priori and listed in `prereg.json`: all of M4, M5 `street_plus_bias`, M2's ratio
objects, M3's rejected pins and `q4_implied`, M1 `d_steps_rw`, every oracle spec.

**Parameter count.** The combination adds **2** (λ, fixed a priori; plus one fitted residual scale
for the band). It **inherits 52** from its members (5 + 6 + 1 + 1 + 2 + 37). Honest total **54**.
The clip adds **0**. FAMILY_A's 37 are carried for narrative, not accuracy: dropping FAMILY_A
*improves* W1 MAE by 0.040pp.

## Results

### `adj_ebitda_margin_pct`, PIT, spec `stack_clip`

| window | h | n | MAE (pp) | rw MAE | bias | vs seasonal_naive | rw | vs drift | vs street | rw | NW(1) t / p vs naive | k better / n | sign p vs naive | sign p vs street | cov80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 0 | 14 | **1.126** | 0.823 | −0.669 | **0.504** | **0.430** | 0.472 | **0.708** | 0.659 | −3.60 / **0.0003** | **11/14** | **0.0032** | **0.029** | 0.93 |
| W2 | 0 | 10 | **0.788** | 0.662 | −0.470 | **0.402** | **0.377** | 0.390 | **0.601** | 0.593 | −3.84 / **0.0001** | **9/10** | **0.011** | 0.055 | 1.00 |
| W1 | 1 | 13 | 1.962 | 1.567 | −0.442 | 0.835 | 0.810 | 0.501 | 1.196 | 1.252 | −1.03 / 0.303 | 9/13 | 0.133 | 0.954 | 0.85 |
| W2 | 1 | 9 | 1.275 | 1.291 | +0.222 | 0.808 | 0.806 | 0.364 | 1.285 | 1.333 | −0.74 / 0.457 | 6/9 | 0.254 | 0.980 | 1.00 |
| W1 | 2 | 12 | 2.255 | 1.893 | −0.462 | 0.910 | 0.966 | 0.621 | — | — | −0.65 / 0.519 | 7/12 | 0.387 | — | 0.83 |
| W2 | 2 | 8 | 1.762 | 1.711 | +0.426 | **1.024** | 1.029 | 0.573 | — | — | +0.13 / 0.899 | 3/8 | 0.855 | — | 0.88 |

### `adj_ebitda_musd`, PIT, spec `stack_clip`

| window | h | n | MAE ($m) | rw MAE | vs naive | vs street | rw vs street | NW(1) t / p vs naive | k better / n | sign p vs street |
|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 0 | 14 | **39.7** | 29.7 | 0.322 | **0.608** | 0.476 | −3.51 / **0.0004** | **12/14** | 0.090 |
| W2 | 0 | 10 | **30.9** | 25.5 | 0.316 | **0.531** | 0.429 | −3.56 / **0.0004** | **9/10** | **0.011** |
| W1 | 1 | 13 | 75.3 | 70.4 | 0.577 | 1.150 | 1.216 | −1.97 / 0.049 | 9/13 | 0.709 |
| W2 | 1 | 9 | 69.0 | 67.3 | 0.761 | 1.475 | 1.325 | −1.15 / 0.250 | 5/9 | 0.910 |

At h=0 the four `final-margin` specs occupy the top four places on **dollars** in both windows
(the best non-`final-margin` object is M5 `street_plus_flowthrough` at $42.8M / $33.8M), and the
top four places on the **margin in W1**; in W2 on the margin `stack_clip` is 5th behind three M5
specs and its own `stack_lam25_clip`; the W2 leader is M5
`dispersion_conditioned|rw_hl4` at 0.743pp, 5.9% better, on five parameters.

### Spec grid (all pre-registered, primary named in advance)

| spec | λ | clip | W1 h=0 MAE | W2 h=0 MAE |
|---|---|---|---|---|
| `stack_ew_clip` | 1.00 (equal) | yes | 1.123 | 0.802 |
| **`stack_clip` (primary)** | 0.50 | yes | **1.126** | **0.788** |
| `stack_lam25_clip` | 0.25 | yes | 1.129 | 0.780 |
| `stack` | 0.50 | no | 1.195 | 0.788 |

The λ grid moves W1 MAE by 0.007pp. **The weighting is not where the result lives.**

### Hindsight (PIT vs full_sample), h=0

margin W1 **0.019**, W2 **−0.059**; dollars W1 0.001, W2 0.009. Essentially nothing is fitted on
the future.

### Leave-one-out and variants (`23_diag_leave_one_out.csv`)

| variant | W1 MAE | Δ | W2 MAE | Δ |
|---|---|---|---|---|
| all six + clip | 1.126 | — | 0.788 | — |
| drop M5 `dispersion_conditioned` | 1.221 | +0.094 | 0.871 | +0.083 |
| drop M5 `street_plus_flowthrough` | 1.163 | +0.037 | 0.869 | +0.082 |
| drop the raw Street | 1.099 | −0.028 | 0.753 | −0.034 |
| drop M3 `nov_sentence_pin` | 1.107 | −0.020 | 0.775 | −0.012 |
| drop M2 sentence rule | 1.130 | +0.004 | 0.815 | +0.027 |
| drop FAMILY_A | 1.087 | −0.040 | 0.814 | +0.026 |
| **Street-independent only** | 1.419 (0.635x naive) | +0.293 | 1.202 (0.614x naive) | +0.415 |
| no clip | 1.195 | +0.068 | 0.788 | 0.000 |

Street-independent LIVE 3Q26 = **49.88%** (`23_diag_street_independent_live.csv`).

### The clip in the backtest

Binds in 2 of 14 W1 quarters — **2023Q1** (raw 15.536 → 15.176, actual 14.411) and **2023Q2**
(raw 34.388 → 33.791, actual 32.971). It helps both times. It does **not** bind at LIVE.

### Bands (`23_bands.csv`)

| target | h | calibration | n | qhat80 | qhat90 | attained cov80 | Gaussian-from-MAE 80 |
|---|---|---|---|---|---|---|---|
| margin | 0 | all 14 W1 | 14 | 2.204pp | 3.906pp | [0.800, 0.867] | 1.809pp |
| margin | 0 | 2024Q1+ | 10 | **2.080pp** | 2.600pp | [0.818, 0.909] | 1.297pp |
| dollars | 0 | 2024Q1+ | 10 | **$66.6M** | $81.4M | [0.818, 0.909] | $49.9M |

The registered LIVE quantiles use the n=14 calibration (conservative); the note and the card quote
the n=10 one. The two routes to a width (conformal vs Gaussian-from-MAE) disagree by 60% because
the error distribution is fat-tailed — 2023Q4 −3.91pp and 2024Q1 −2.60pp against a median |error|
of 0.60pp. WS22 group C's recipe produced qhat 1.584pp for **WS20's** 60/20/20 blend; this is a
different object with a lower MAE and a worse worst case, and its own qhat is 2.08pp. Carry the
harness's exchangeability caveat: an expanding-window refit over a regime break is not exchangeable,
so this is a descriptive band.

## Pass line — result

| test | verdict |
|---|---|
| Primary: beats `seasonal_naive` on the margin at h=0 **and** h=1, both windows, both weightings | **PASS** |
| Secondary: within 10% of the best single non-oracle object at h=0 | **PASS** (margin W2 5.9% worse than M5-disp; better everywhere else; better than every single object on dollars) |
| Secondary at h=1 | **FAIL** — 1.196x / 1.285x the raw Street. Consequence applied: 4Q26 is quoted from the Street. |
| h=2 | **FAIL** — W2 1.024x the naive. Consequence applied: 2027 is a labelled scenario. |
| Workbook opens; `run.py` exits 0; every SYNTHESIS number traces to a CSV | **PASS** |

## What failed, and what that means

1. **h=1.** No amount of blending beats the raw Street one quarter out. This is the same finding
   WS20 reached and it survives the discussion round. The practical consequence for the pitch is
   uncomfortable and should be said out loud: **the trade into 5 Nov is an h=1 position on 4Q26 and
   an h=0 position on 3Q26, and we only have an edge on the second.**
2. **h=2.** The combination is 0.91x the naive in W1 and 1.02x in W2. FY27 is arithmetic on a
   spending assumption, not a forecast.
3. **Intervals still over-cover** (cov80 0.93 / 1.00 against 0.80) even on a conformal band. At
   n 10-14 the attainable coverage grid is coarse; there is no fix at this sample size.
4. **The member pool is a post-hoc selection.** It inherits WS20's and WS22's exclusions. The
   paired tests price the combination *given* the pool, not the pool. The leave-one-out table is
   the mitigation offered, not a proof.
5. **The line residual allocation is mechanical.** Allocating by PIT error variance puts 76.6% of
   the residual in S&M, 14.0% in G&A and 9.4% in product development, and that pushes 3Q26 G&A to
   +10.0% y/y when 1H26 ran −5.4% y/y. Flagged, not fixed.

## Corrections to existing work

- **WS31b's forward profiles (`research/notes/overnight/31b_operating-profile.md`) put 4Q26 margin
  at 24.65-25.93%.** Every method in this build, the Street (28.90%) and the FY guide arithmetic
  (27.6-30.9%) disagree by 3-4pp. WS23 does not carry WS31b's 4Q26 number and recommends it not be
  cited until reconciled. No existing file was modified.
- **WS30's walk** (3Q26 50.80% / 4Q26 29.70%) is 0.86pp / 0.80pp above this build; directionally
  the same view, not carried as a forecast.
- **Every package's LIVE dollar row except this one still sits on the harness naive revenue leg**
  (4Q26 $3,237M vs bridge v3's $3,178M; FY27 $16,709M vs $15,819M). WS22 group C specified the fix
  and did not write it; WS23 applied bridge v3 by hand to the final model only.

## For the model

| name | value | unit | source |
|---|---|---|---|
| 3Q26 adj EBITDA margin | 49.940 | % | `23_card_5nov.csv` |
| 3Q26 adj EBITDA | 2,399.1 | USD m | `23_forecast_quarterly.csv` |
| 3Q26 adj EBITDA, dollar object | 2,411.0 | USD m | `23_combination_live.csv` |
| 3Q26 margin 80% band | ±2.08 | pp | `23_bands.csv` (2024Q1+ conformal) |
| 3Q26 adj EBITDA 80% band | ±66.6 | USD m | same |
| 4Q26 adj EBITDA margin | 28.897 | % | Street baseline, h=1 rule, `23_path_rule.csv` |
| 4Q26 adj EBITDA on bridge v3 | 918.4 | USD m | `23_forecast_quarterly.csv` |
| FY26 adj EBITDA margin | 35.727 | % | `23_forecast_annual.csv` |
| FY26 adj EBITDA | 5,097.5 | USD m | same |
| FY27 adj EBITDA margin (scenario) | 34.642 | % | same |
| FY27 adj EBITDA (scenario) | 5,483.3 | USD m | same |
| FY26 / FY27 incremental margin | 39.5 / 24.7 | % | `23_forecast_annual.csv` + FY25 actual |
| Combination weights, LIVE 3Q26 | 0.199 M5-disp / 0.168 M5-flow / 0.172 street / 0.158 M3 / 0.152 M2-sent / 0.150 family | share | `23_combination_live.csv` |
| Shrinkage λ | 0.5 | ratio | `prereg.json` (fixed a priori) |
| EPS per $M of adj EBITDA | 0.001386 | USD/share | (1 − 0.18)/591.7 |
| FY26 floor break-even (2H26 revenue) | −0.63% held / −0.94% flexed | % | `23_fy26_floor_breakeven.csv` |
| Margin per 1pt of revenue shortfall, FY27 | 0.66 held / 0.42 flexed | pp | `23_macro_sensitivity.csv` |
| FY26 budget identity | 1pp FY = 4.49pp of 4Q26; 1pp of 3Q26 = −1.51pp of 4Q26 | — | `23_card_budget_identity.csv` |

## For the 5 Nov card

See `docs/margin-build/SYNTHESIS.md` §5 for the full card. The three lines:
**3Q26 $2,399M vs Street $2,361.5M, 80% band $2,299-2,499M, P(beat) 0.77**;
**FY26 35.73% against a 35.5% floor that breaks on a 0.6-0.9% 2H26 revenue miss**;
**the FY sentence goes to "approximately 36%", which asks the Street to raise 4Q26 by 1.2pp / $39M.**

## RESUME

See the RESUME section of `docs/margin-build/SYNTHESIS.md` — it is the authoritative one. In one
line: write the WS22 group C `revenue_leg_live.csv` harness patch, reconcile or retire WS31b's
4Q26 profile, and build a genuine h=1 object for 4Q26, because that is the quarter the 5 Nov guide
actually lands on and the only one where this build has no edge.

---

## Audit response (appended by WS31, 14 Sep 2026 — history above is not rewritten)

The Codex/Astra audit (`docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`, 18 findings: 1 critical,
12 major, 5 minor) was applied to this package. Triage table with a decision per finding:
`docs/margin-build/audit/AUDIT_RESPONSE.md`. Every number that moved, before -> after:
`docs/margin-build/SYNTHESIS.md` §11. **No finding was rejected**; finding 16 is accepted in part
(the workbook is now labelled a frozen report; wiring it into an input-driven model is deferred,
with the reason). Pre-audit copies of every CSV live in
`data/processed/margin_build/23_final_model/_pre_audit/`, the registry in
`registry/final-margin__combined_pre_audit.csv.bak`, the workbook in
`model/ABNB_margin_model_pre_audit.xlsx`.

**The one that matters (critical, 01).** `combine.run_backtest` and `diagnostics.replay` chose the
weight-calibration pool and the conformal-band pool by *quarter order* (`qs[:i]`), not by what had
printed. At h=1 and h=2 that let a vintage use an actual it could not have seen — 2023Q3 forecast
on 9 May 2023 was weighted on 2023Q2 errors, and 2023Q2 printed on 3 August. Both pools are now
gated on `print_date <= vintage_date` (`combine.printed_before`, from the harness `targets.csv`).
h=0 is unchanged by construction. h=1 W1 MAE 1.962 -> 1.952, W2 1.275 -> 1.269; h=2 W1 2.255 ->
2.229, W2 1.762 -> 1.766; h=2 W1 cov80 0.833 -> 0.750. **Every pass/fail verdict survives**: h=0
still passes both windows and both weightings, h=1 still loses to the raw Street (1.189 / 1.278),
h=2 still fails in W2 (1.026x the naive).

**What else changed in this package's code.**

1. *One add-back schedule* (02, 03). The cost stack used M1's `other_net` rule (0.68% of revenue,
   $32.5M in 3Q26) while the GAAP bridge subtracted only D&A ($20.6M) — $11.9M of unsupported
   add-backs, and a five-line sum that did not equal the displayed total. The stack now carries
   **D&A only** (`addbacks_musd`, from the same M7 bridge the GAAP walk uses); on actuals
   2024Q1-2026Q2 `other_net - D&A` runs -12 to +6, mean -1.2, so D&A is the schedule the data
   supports. `sum_five_lines_musd`, `addbacks_musd` and `recon_gap_musd` are now displayed columns,
   and the Bridge sheet shows the reconciliation as three rows. Effect: 3Q26 S&M $790.2M -> $781.1M
   (+35.0% -> +33.5% y/y), pd and G&A a little lower; EBITDA, margin, operating income and EPS
   unchanged.
2. *The adopted dollar object* (04). What the card quotes is the margin combination times revenue,
   which was never registered or calibrated; the band came from the margin route and the beat
   probability from the four-member dollar combination. `final-margin__combined_dollar_from_margin`
   is now built, scored and registered (576 rows): W1/W2 h=0 MAE **$30.7M / $25.8M**, 0.25x / 0.26x
   the naive, 0.47x / 0.44x the Street, better than the Street in 14 of 14 and 10 of 10 (sign p
   0.0001 / 0.0010). Band **$2,337-2,462M**, P(beat) **0.779** on its sd of $48.8M. The old **0.77
   is withdrawn**, not restated.
3. *Scenario statements* (05). Bear and bull now carry M6's fitted cost response (k = 0.364 on
   total cash costs) rather than the base margin on a different revenue. FY27 bear/bull margin
   34.51/34.71 -> **32.15/36.53**.
4. *EPS bands* (06). Joint, not EBITDA-only: M7's measured bridge sd $0.083 (W2 h=0 with EBITDA
   known) in quadrature with the EBITDA term. 3Q26 $2.74-3.02 -> **$2.70-3.05**. The old column is
   kept as `eps_q10/q90_ebitda_only`.
5. *Cash flow and annual arithmetic* (07, 15). CFO is rebuilt from the updated **net income**
   (`CFO = NI + D&A + SBC + working capital + other`, M7's identity), not moved by the pretax
   EBITDA delta; annual tax and net income are the sum of the quarters with the ETR derived
   afterwards. FY26 FCF mid 4,830 -> **4,844**; FY26 base NI 3,145.93 -> **3,146.12**.
6. *Registry hygiene* (08, 09, 17). `street_vendor` / `street_as_of` / `knowable_from` propagated
   (768 consensus-anchored rows); `n_params` = 54 with the 2+52 split in `notes`; `n_train` =
   prior observations; `n_members`, the member list and `consensus_anchored` in `notes`; the
   `<bound method NDFrame.clip>` bug fixed (`r["clip"]`). A first-class `n_members` **column** is
   impossible without a harness change: FORMAT 1.0 is frozen and `validate_registry_frame` raises
   on unknown columns.
7. *Guards* (18, and new). `MARGIN_VERIFY_ONLY=1` recomputes the whole package into `_verify/`,
   writes nothing and no registry row, and prints a per-file comparison against the committed CSVs.
   `run.py` step 4b asserts every identity above and exits 2 if one breaks.
8. *Wording* (10, 11, 12, 13) — rewritten in SYNTHESIS §1, §2, §5 and §9, not here: results are
   retrospective and conditional on a pool selected after seeing the scoreboard; "attained coverage
   82-91%" is withdrawn (it was a rank grid from n, not a measurement); the FY floor is an
   inequality, not a 27.6% point forecast or an automatic sell; and the peer opex regression is
   imprecise (k 0.14, t 0.47, SE 0.30, 95% CI -0.44 to +0.72), not a demonstration that costs do
   not respond.

**Incidental repair found on the way.** `combine.run_live` looked up the bridge-v3 revenue path with
canonical quarter codes (`2026Q3`) against a file keyed `3Q26`, so the `ebitda_musd_{base,bear,bull}`
columns of `23_combination_live.csv` were silently never written. Fixed (`bridge_v3_revenue()`);
nothing downstream had used them, so no published number changed.

**Commands re-run, in this order, sequentially (never two at once — they shell out to `score.py`):**

```bash
py -3.13 analysis/src/margin_build/23_final_model/run.py      # exit 0; ends by calling score.py
py -3.13 analysis/src/margin_build/20_scoreboard/run.py       # exit 0
```
