# WS22 Discussion round: method groups answer the red team (WS21) and the scoreboard (WS20)

Assembled by the orchestrator 15 Sep 2026 ~01:50 from `discussion/group_A.md` (M1, M4, M6), `group_B.md` (M2, M3), `group_C.md` (M5, M7, harness). Prompt: `prompts/22_discussion.md`. After all three finished, `score.py` and `20_scoreboard/run.py` were re-run once (both exit 0), so `data/processed/margin_build/10_harness_margin/scoreboard_margin.csv` and `20_scoreboard/` now reflect the post-discussion registry (oracle specs removed, M3 post-hoc specs flagged, `nov_sentence_pin` registered, M1 step dummies gated, significance columns added).

## Orchestrator digest of decisions

- **3Q26 card converges on the management ceiling.** Group A clipped the driver family to the 'down slightly' sentence (50.09% / $2,406M) after showing the 1.5pp gap is noise, not a line error; Group C showed M5's beat was two-thirds the clip floor and without it 3Q26 is 49.96% / $2,387M; Group B's bias-corrected sentence rule gives 49.4-49.9%. The run's 47-51.5% spread has closed to roughly 49.4-50.1%.

- **What survives significance.** M5's dollar flow-through (W2 p 0.007, W1 sign p 0.029); M3's `m[q-4]+delta` allocation vs the harness proration (p 0.028 / 0.030, pre-registered specs); M6's cost-of-revenue slope vs seasonal-naive-drift (p 0.0004 / 0.008). M5's margin-points claim, M1's 'cost stack is forecastable', M2's dollar win over Street, M7's tax under-coverage, M6's FY26 floor cushion (now 0.24-0.68% of 2H26 revenue, a 4Q26 question) and quarterly FCF are withdrawn.

- **New object:** `guide-policy-margin__nov_sentence_pin` (zero estimated parameters): 4Q26 29.90% / $950M at a 50.09% Q3, FY26 36.00%, vs Street $914M / 28.90%. Replaces the withdrawn 34.51%.

- **Weights for WS23 (groups' recommendations):** M5 flow-through (dollars) as the anchor, M3 `nov_sentence_pin` or `rw_hl4_pin` about 20%, the driver family (clipped) about 20%; M4 and M2 ratio objects 0; M6 only for the cost-of-revenue line and scenario deltas; M7 for everything below EBITDA with EPS quoted two ways.

- **Harness:** significance columns (`t_nw1_*`, `p_nw1_*`, `p_sign_*`, `survives_both_windows_sig`, `is_oracle`) are new columns; gating on them cuts margin h=0 survivors from 26 pairs to 7 (6 of them M5). Conformal recipe for WS23: qhat 1.584pp at n 10 from the combination's PIT errors. A LIVE-only bridge-v3 revenue leg is endorsed; the backtest leg stays.

- **Operational:** method `run.py`s shell out to `score.py`; never run two concurrently. `MARGIN_SKIP_SCORE=1` (A) and `--no-score` (B) guards were added.


---

# group_A.md

# WS22 discussion — GROUP A: M1 driver-lines, M4 alt-augmented, M6 cycle-flex

Margin build run, 14 Sep 2026. Agent: group A discussion agent. Interpreter `py -3.13` throughout.
Sources read: `00_BRIEF.md`, `prompts/M_common.md`, `prompts/22_discussion.md`, the three method notes and their
`run.py`, `notes/21_red_team.md`, `data/processed/margin_build/21_red_team/21_findings.csv`, and
`notes/20_scoreboard.md` (section 2 below).

Each method's own note now carries a **"Discussion response"** section with the full before/after detail:
`notes/M1_driver_lines.md` (D1-D7), `notes/M4_alt_augmented.md` (D1-D6), `notes/M6_cycle_flex.md` (D1-D8).
All three packages were rebuilt with `MARGIN_SKIP_SCORE=1` (a new guard, so three concurrent agents do not race
on `score.py`); each exits 0. **`score.py` was not run — the orchestrator re-scores once.**

---

## 1. Decisions on the red-team findings

| finding | method | decision | reproduced? | what changed | files |
|---|---|---|---|---|---|
| **R04** step dummies used without the `knowable_from` gate | M1 | **ACCEPT — fixed** | **Yes**, exactly (the red team's `check_09` re-run: 7/14 W1, 6/10 W2 vintages) | `step_level(sc, q, vd)` gates every step by `04_signal_knowable_from.csv` in the fit *and* the forecast. `d_steps_rw` W1 h=0 ratio 1.1416 -> 1.1443 (rw 0.9112 -> 0.9177), W2 0.9738 -> 0.9782 (rw 0.8401 -> 0.8479); 26 rows at 10 vintages move, max 0.82pp. **The leak was buying spurious accuracy; the spec is worse without it and still fails.** No other spec moves. | `analysis/src/margin_build/M1_driver_lines/run.py`; `data/processed/margin_build/M1_driver_lines/*` |
| **R03** oracle specs registered as `prior_basis=PIT` | M1, M6 (M4: no) | **ACCEPT — fixed** | **Yes**: 1,376 M1 rows + 1,248 M6 rows | `prior_basis` is validated against `{PIT, full_sample}` by the frozen FORMAT 1.0, so re-labelling inside the registry is impossible. Both oracle specs are **withdrawn from the registry** into labelled diagnostic files. Registry rows: `driver-lines__margin_v2` 3,612->**3,096**, `__lines_v2` 6,020->**5,160**, `cycle-flex__flex_margin` 1,872->**1,404**, `__flex_lines` 3,120->**2,340**. | `M1_driver_lines_oracle_diagnostic.csv`, `M6_cycle_flex_oracle_diagnostic.csv`, both `run.py` |
| **R03** "M4 inherits the oracle spec" | M4 | **REJECT** | **No** | A substring scan for `revknown`/`nightsknown` over both `alt-augmented__*.csv` returns **0 rows**. M4's seven specs are `none_*`, `best1_*`, `ridge_all_*`, `surv_*`; it never calls M1's family-`e` path. Nothing to fix. | — |
| **R11** LIVE 3Q26 above the guidance ceiling | M1, M4, M6 | **ACCEPT — reconciled (the sentence wins)** | **Yes**: M1/M4 51.575%, M6 51.233%/51.575% vs a 50.085% ceiling and Street 49.776% | Tested the only defence — that the *quarterly* sentence is sandbagged — and it **fails**: the `q_guide_implied` realised (actual - sentence) gaps are W1 mean +0.47 / median **-0.60**, 6/14 above; W2 mean **-0.19** / median **-0.94**, **4/10** above; last 8 quarters **-0.86pp**. The 60-140bp beat pattern is an **FY floor** phenomenon, not a quarterly one. Card 3Q26 becomes the clipped **50.09% / $2,406M**; the unclipped 51.6% stays on the record, labelled "the 2025-26 spending ramp pauses". FY26 36.18% -> **35.68%**. No registered number moved (LIVE rows are not scored). | `M1_driver_lines_live_guide_reconciled.csv`, `M6_cycle_flex_guide_clipped_floor.csv` |
| **R15** M6's FY28 compounds positive intercepts | M6 | **ACCEPT — fixed** | **Yes**: five rows at 31.33% vs Street 37.65% | FY28 is **replaced in place** by a flat roll-forward of the same row's FY27 margin (34.36%, 35.00% for `cut`), the lines set to NaN, the withdrawn value kept in `withdrawn_growth_model_margin_pct` and in a separate file, and a `fy28_basis` string on every row. Kill-list item 6 is now enforced by the data file, not only a sentence. | `M6_cycle_flex_annual_forecasts.csv`, `M6_cycle_flex_fy28_withdrawn.csv` |
| **R14** line wins are close to free | all three | **ACCEPT — and worse than stated** | **Yes, and extended**: against `seasonal_naive_drift` the mean line ratio is **1.000-1.029**, not 0.51-0.59 | Re-scored every line and the margin against `seasonal_naive_drift` with paired NW(1) tests and sign tests. **Only cost of revenue survives** (M6 `l0_rw` 0.652 W1 / 0.677 W2, t -3.57 / -2.67, p 0.0004 / 0.008, better in 13/14 and 9/10; M1 `b_elastic_rw` 0.753, t -2.03, p 0.042). pd, S&M and **total cash costs** are *worse* than drift (1.11-1.28). M1's "every line but G&A beats the naive by 20-70%" and "total cash costs 0.27/0.22 — the cost stack is forecastable" are **withdrawn**. | `analysis/src/margin_build/22_discussion_group_A/repro_drift.py`; notes M1 D4, M4 D3, M6 D4 |
| **R01/R02** the survivor flag is ~30% free; no W1 skill | all three | **ACCEPT — quoting rule** | **Yes**, on our own cells | M1 `b_elastic_rw` vs naive: W1 t **+0.07** p 0.95, 7/14; W2 t -0.14 p 0.89, 5/10. M6 `l0_rw`: W1 t **-0.10** p **0.92**, 7/14; W2 t -0.52 p 0.60, 5/10. M4 `best1_rw` is *worse* (t +0.57). **M6's "the registered forecaster passes its harness test" is downgraded** to "a tie with y[q-4] carrying a flag the red team priced at ~30% free". Every ratio group A supplies now carries p and quarters-better; "survives both windows" is retired from our language. | `22_discussion_group_A/repro_skill.py`; notes M1 D5, M4 D4, M6 D6 |
| **R10** intervals too wide | all three | **ACCEPT-DEFER** | **Yes**: cov80 0.93-1.00 vs a nominal 0.80 | A conformal / realised-error band is a new object needing its own pre-registration and there is no time tonight. Meanwhile: **take the 5 Nov band from the realised h=0 error distribution** (M1 W1 MAE 2.26pp / W2 1.91pp / sd 2.8pp; M6 2.20 / 1.77) and do not quote any group A q05-q95 ladder as a probability. M6's own rule stands: use the **scenario spread**, not the residual band. | — |
| **R13** M6 `run.py` raises `FileNotFoundError` on the licensed peer files | M6 | **REJECT in part, ACCEPT in part** | **No** for the crash claim | Reproduced by loading `run.py` as a module with `PEER_OPEX`/`PEER_SM` pointed at non-existent paths: `peer_k_table()` returns **0 rows, no exception** (it opens with an `.exists()` guard), and both files are already manifested with sha256 in `04_alt_signals.csv`. **Accepted:** the prerequisite was undocumented and the failure silent. Fixed: a loud `!! MISSING LICENSED INPUT` warning, a **Licensed prerequisites** section in the README naming the files, their manifest and the LSEG fields to re-pull, and a new `M6_cycle_flex.csv` manifest cross-reference. | `M6_cycle_flex/run.py`, `M6_cycle_flex/README.md`, `data/manifests/margin_build/M6_cycle_flex.csv` |
| **R08** flags asserted on n as low as 2 | harness / all | **ACCEPT — not ours to fix** | Yes | No group A cell rests on n < 8 except two **labelled** slices (M6's pre-registered T3, n=4; the 2H22 slice, n=3) and M4's `pd|careers_open_roles@2`, where the signal is present in only **2 of 14** quarters and M4's own note says it is untestable. Agreed that the scoreboard should print n beside every flag (group C). | — |
| **R17** h=0 is post-letter, post-guide | all | **ACCEPT — card language** | Yes | Carried to the card. It also *justifies* the R11 clip: the sentence is inside the model's information set, so ignoring it is a choice, not an oversight. | notes M1 D5, M4 D4, M6 D6 |
| **R19** pre-registration timestamps | all | **PASS** | Yes | M1 `d5da4e4`, M4 `fdf3447`, M6 `bebbf4e`, all before results. No action. | — |
| **R20/R21/R22** reproducibility, kill list, licence, mechanical PIT | all | **PASS — confirmed** | Yes | M4 rebuilt **byte-identical** including both registry files; M6's non-FY28 outputs byte-identical; M1's only changed file besides the new ones is `per_line_mape.csv` (the `d_steps_rw` rows). | — |

### Coordination note on R03: the three groups fixed it two different ways

A registry scan after all three discussion agents had re-registered shows **two different resolutions of the same
finding**, and WS23 needs to know both:

- **Group A removed its oracle rows from the registry entirely.** `driver-lines__*` and `cycle-flex__*` now
  contain no `revknown` / `nightsknown` spec at all; the rows live in labelled `*_oracle_diagnostic.csv` files.
- **Groups B and C renamed theirs in place with an `oracle_` prefix** — `guide-policy-margin|oracle_rw_hl4_revknown`,
  `margin-ts|oracle_k4_rw_revknown`, `oracle_drift_k4_rw_revknown`, `oracle_g_k4_rw_nightsknown` — so those rows
  are still scored and still appear in rankings unless the scorer filters them.
- **`below-ebitda__eps` and `__fcf` still carry unprefixed `ebitda_known` / `swing_x_gbv_ebitda_known` specs**
  (WS20 excluded them by hand, and its open question 11 asked M7 about them).

**Recommendation to the orchestrator and WS23:** filter on **both** — the `oracle_` prefix *and* the substrings
`revknown`, `nightsknown`, `ebitda_known` — exactly as WS20 section 0 rule 2 already does. Group A's rows cannot
leak because they are gone; the others can. WS20's open question 13 (add an `is_oracle` column to the harness
rather than relying on a naming convention) is the right permanent fix and we support it.

### Backups and rebuild commands

`data/processed/margin_build/{M1_driver_lines,M4_alt_augmented,M6_cycle_flex}/_pre_discussion/` hold every CSV and
JSON as it stood before the round; `data/processed/margin_build/registry/*_pre_discussion.csv.bak` hold all six
registry files.

```bash
cd "C:\Users\krish\citadel-abnb-margins"
MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/M1_driver_lines/run.py    #  39 s, exit 0
MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/M4_alt_augmented/run.py   # 130 s, exit 0
MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/M6_cycle_flex/run.py      #  23 s, exit 0
```

---

## 2. What each method now claims

**M1 (driver-lines).** A ten-parameter cost stack conditional on a revenue path, and a negative result on the
margin. It claims **no margin skill**: `b_elastic_rw` h=0 is a tie with `y[q-4]` (ratio 1.010 W1 / 0.975 W2,
t +0.07, p 0.95, better in 7 of 14) and Street is 1.3-1.5x more accurate; both pre-registered pass lines failed
and stay failed. Its surviving line claim is **cost of revenue only**: b = 0.81 on GBV (LOYO 0.66-0.98), MAE
ratio **0.753 against a drift naive, p 0.042, 9 of 14 quarters**. The claim that the whole cost stack is
forecastable is withdrawn (total cash costs are 1.165x a drift naive). Its oracle diagnostic still shows that
about a quarter of the h=0 margin error is the revenue leg, not the cost model. LIVE, on the card:
**3Q26 50.09% / $2,406M** (clipped to the guidance sentence; unclipped model 51.57% / $2,478M, labelled as the
"spending ramp pauses" case), **4Q26 28.47% / $905M**, **FY26 35.68%** (+0.18pp over the floor),
**FY27 35.14%, down 1.0pp against a Street at +0.8pp** — which remains the most useful thing M1 produces,
because it is arithmetic on the spending trends rather than a forecast of a print.

**M4 (alt-augmented).** Unchanged in substance and byte-identical after the rebuild. It claims: **there is no
external dataset in our reach that improves the 3Q26 margin call.** Fifty pre-registered point-in-time tests
under a strict `knowable_from` gate produced one survivor (G&A on computer-systems-design employment, lead 2,
IV 0.895-0.898), which its own 1,000-draw random-series placebo says fires on noise 5.5% of the time per G&A test
and 22.5% under best-of-5; across 50 tests the null expects 1.0 and we observed 1. It moves margin MAE by 0.6% /
0.1% and 3Q26 by +0.13pp. Two amendments from this round: (a) its cross-method warning is **stronger** than it
wrote — against a drift baseline `best1` improves **no** line, not four of five, while still degrading the margin
(1.019 / 1.068); (b) its LIVE table is M1's and therefore carries M1's clipped 3Q26. Its most valuable output is
the calibrated prior it hands everyone else: **an unvalidated alt-data cost regressor costs 1-5% of margin
accuracy, and a line-level pass line like the scoreboard's fires on pure noise 2.5-22.5% of the time.**

**M6 (cycle-flex).** A measurement, a scenario engine, and a negative result on the forecaster. Its strongest
claim is **"Airbnb has no cost dial"**: total opex elasticity to revenue 0.14, not significant, against BKNG 0.61,
TRIP 0.63, EXPE 0.44 and BKNG advertising 0.87-0.98 (n = 18 each). Its second claim is now the strongest
quantitative result in group A: **`k_cor` = 0.56 on cost of revenue beats a drift naive with ratio 0.652 (W1) /
0.677 (W2), NW(1) t -3.57 / -2.67, p 0.0004 / 0.008, better in 13 of 14 and 9 of 10 quarters** — the only object
built from ABNB's own history that we can find surviving an adversarial baseline in both windows on both tests.
Its forecaster claims nothing: `l0_rw` h=0 is a tie (t -0.10, p 0.92, 7 of 14) and h>=1 fails. Two headline
numbers are withdrawn: **FY28 (31.3%)**, replaced by a labelled flat roll-forward, and **"the FY26 35.5% floor
survives a 1.9-2.5% 2H26 revenue shortfall ($149-203M)"** — with 3Q26 clipped to the guidance sentence the
cushion is **+0.09 to +0.18pp, a 0.24-0.68% shortfall ($19-54M)**, and the floor becomes a **4Q26** question
where M1 (28.5%) and M3's sentence-modal (30.9%) differ by 2.4pp = 0.54pp of FY26. Everything M6 supplies as a
**delta** — the k's, the peer table, the asymmetry (k_dn < k_up for ops, S&M and total cash costs, p < 0.02),
0.27pp of FY26 margin per 1% of 2H26 revenue flexed / 0.36pp held, flexing recovering only 30-40% of a revenue
miss, the 1Q27 trough at 19.5% (band 17-22%) — is untouched by every fix in this round.

---

## 3. Recommended WS23 weights for group A's objects

| object | weight | one-line reason |
|---|---|---|
| M6 `k_cor` = 0.56 (cost of revenue on revenue growth) | **1.0** | the only ABNB-history object in group A significant against a drift baseline in both windows and on both tests |
| M6 peer `k` table (ABNB 0.14 ns vs BKNG 0.61 / TRIP 0.63 / EXPE 0.44) | **1.0** | a measurement, not a forecast; the strongest qualitative point the driver family owns |
| M6 scenario-engine **deltas** and the asymmetry result | **1.0** | never depended on the level; untouched by every fix here |
| M6 FY26 floor break-even, **clipped form only** (`_guide_clipped_floor.csv`) | **1.0** (unclipped form: **0**) | the unclipped cushion overstates by 3-8x |
| M4's negative result + its false-positive priors | **1.0** | the best-evidenced statement in the run and the only calibrated prior for "an unvalidated cost regressor" |
| M1 `lines_v2` cost-of-revenue elasticity (b 0.81 on GBV) + `other_net` rule | **1.0** | the surviving line claim and an accounting identity |
| M1 FY27 arithmetic (35.1%, incremental margin 25.6%) | 0.75 | the clearest statement of the S&M problem; a scenario, not a validated forecast |
| M1 `lines_v2` ops & support (b 0.76 on nights) | 0.5 | right sign, stable LOYO, but a tie against drift; needed to close the stack |
| M6 `k_sm` = 0.42 | 0.25 | t 2.3 but unstable (0.87 in 2022, 0.30-0.42 since 2025); scenario deltas only |
| M6 `flex_margin` as an h=0 margin **point** | 0.15 | t -0.10, p 0.92, 7 of 14; keep only as one arm of the cross-method spread |
| M1 `margin_v2` as a margin **point forecast** | **0** | tie with naive; Street is 1.3-1.5x better at h=0 (see section 4 Q5 for which one member should carry the family leg) |
| M1 pd / sm / G&A trends; M6 `k_pd`, `k_ga` | **0** | worse than a drift naive; M6's T1 failed on pd; take levels from M3 or management language |
| M4 `margin_aug` / `lines_aug` as forecasts (any spec) | **0** | `none` is M1; `best1` and `ridge_all` are worse on the margin and worse against drift |
| M4 `surv_emp_computer_systems_design_rw` | **0** | registered and explicitly not recommended by its own author |
| M6 `dl_rw`, M1 `c_mix_rw`, M1 `d_steps_rw` | **0** | 22 parameters and worse on every cut; no content; no content |
| Both oracle specs (`e_revknown_rw`, `revknown_rw`) | **0** as forecasts; keep as diagnostics | now out of the registry entirely |
| All group A quantiles | **0** | cov80 0.93-1.00 against a nominal 0.80 |
| M1/M6 FY28 levels | **0** from M6 (withdrawn); M1's 32.6% only if labelled a trend extrapolation | R15 |

---

# Section 2 — answers to the WS20 scoreboard's open questions

`docs/margin-build/notes/20_scoreboard.md` section 11, questions **5, 6 and 7** are addressed to this group.
The board reflects the registry as of 03:52-03:55 UTC; section 12 already notes our re-registrations and says the
direction of the board is unaffected, which we confirm: **every ranking in that note excluded the oracle specs we
have now physically removed, and no object carrying its recommendation belongs to group A.**

## Q5. "Your h=0 margin errors correlate 0.99-1.00. Which one carries the narrative, what would the other two have to show for their ~35 combined parameters, and is there any quarter where your points differ by more than 0.5pp?"

**First, the correlation is understated in one place and overstated in another.** M1 `b_elastic_rw` and M4
`none_rw` are not merely correlated at 1.00 — they are **the same numbers**. M4 imports M1's `run.py` and calls
its fitting code, so `none_*` is M1 bit-for-bit; the re-run confirms it (identical to the last decimal at all 14
quarters). M6 `l0_rw` against M1 is r **0.992**, and M4 `best1_rw` against M1 is r **0.951**.

**Quarterly points, PIT, h=0, W1 (all 14 quarters):**

| | max |M1 - M6| | quarters > 0.5pp | max spread across M1 / M4-best1 / M6 |
|---|---|---|---|
| value | **0.96pp (2026Q1)** | **2** — 2026Q1 (0.96pp) and 2023Q1 (0.53pp) | **2.70pp (2025Q4)**, then 1.93pp (2026Q1), 1.40pp (2026Q2) |

So the answer to the last part is **yes, twice, and the reason is specific**: M1 puts each line on *its own*
driver (cor on GBV, ops on nights, S&M on revenue, pd and G&A on a trend alone), while M6 puts **every** line on
*revenue*, including pd (k -0.21) and G&A (k -0.11), whose loadings are insignificant and wrong-signed. Those two
terms only bite when revenue growth departs sharply from its recent average — and **2026Q1 is the largest
revenue-growth acceleration in the sample (+17.9% y/y against +12.0% the quarter before)**, which is exactly where
the two models separate. 2023Q1 is the mirror image at the start of the sample. In the twelve calm quarters
between, the two are inside 0.48pp of each other, which is a fifth of either model's own MAE. **They are one
model with two parameterisations of the discretionary lines, and the difference only shows up in the quarters
where neither is accurate anyway.**

**Which one carries the narrative: M1.** Three reasons. (i) It is the base the rest of the family consumes —
M4 imports it literally and M6's scenario engine runs on M1's LIVE cost path (`base=M1_b_elastic_rw`), so
choosing anything else would make the family internally inconsistent. (ii) It is the cheapest full cost stack at
**10 parameters**, against M6's 12, M4's 15 (`best1`) and 37 (`ridge_all`). (iii) Its lines are economically
labelled — each on the driver that plausibly causes it — so the memo can say *why* a line moves, which is the
only thing this family is actually for.

**What the other two show for their parameters — and the honest answer is that most of those parameters should
not be in the blend at all.** M4's forecasting objects should carry **weight 0**; what M4 earns its place with is
a *negative* result and a calibrated false-positive prior, which cost the blend nothing. M6's forecaster should
carry almost nothing; what M6 earns its place with is `k_cor` (the one significant line result against a drift
baseline), the peer table, the asymmetry test and the scenario engine — none of which is a point forecast. On
that reading the driver family contributes **10 parameters (M1's stack) plus two used k's**, not 35.

**On the board's 20% family leg specifically, two amendments we would make.** The board averages
`M1 b_elastic_eq`, `M4 ridge_all_eq`, `M6 l0_rw` and `M2 sarima|lines_aicc` at 5% each. (a) `M4 ridge_all_eq` is
**37 free parameters against 14 backtest quarters**, and its apparent edge is t **-0.20** (W1, p 0.84, 7 of 14) /
t -0.52 (W2, p 0.60, 5 of 10) — it is a shrinkage artefact and should be replaced by `M1 b_elastic_rw`, the
pre-named main spec, or simply dropped so the leg is M1 + M6 + M2-SARIMA. (b) `M1 b_elastic_eq` was picked by the
in-script grid, not pre-registered; it beats the pre-named `b_elastic_rw` by 0.02 in ratio, which is inside
selection noise on 14 quarters. Neither amendment changes the LIVE number by more than ~0.1pp, but the memo
should not have to defend 37 parameters.

## Q6. "Your LIVE 3Q26 margins (51.2-51.7%) breach the ceiling implied by 'margin down slightly compared to Q3 2025' (50.085%). Either your cost lines are too low or the sentence is sandbagging. Which line is responsible, and what would it take for 3Q26 margin to print *above* 3Q25?"

**Neither, and that is the finding.** We tested the sandbagging hypothesis directly and it fails, and we then
decomposed the gap line by line and **no line is responsible**.

**(a) The sentence is not sandbagging.** The harness `q_guide_implied` baseline *is* the quarterly sentence turned
into a level. Its realised (actual - sentence) gaps:

| window | n | mean | median | quarters above the sentence | last 8 quarters |
|---|---|---|---|---|---|
| W1 | 14 | +0.47pp | **-0.60pp** | 6 / 14 | — |
| W2 | 10 | **-0.19pp** | **-0.94pp** | **4 / 10** | mean **-0.86pp** |

The 60-140bp beat WS05/31a document is an **FY floor** phenomenon. The **quarterly** sentence has been *missed*
slightly more often than beaten. There is no empirical licence to override it.

**(b) No line is responsible.** Re-pacing every one of M1's five 3Q26 lines at that line's own realised 1H26 y/y
growth closes **0.28pp of the 1.49pp gap** (51.58% -> 51.29%), because the lines pull in opposite directions:

| line | 3Q25 actual | M1 3Q26 | M1 y/y | 1H26 realised y/y | at the 1H26 pace | delta $M | delta pp |
|---|---|---|---|---|---|---|---|
| cost of revenue | 549 | 617 | +12.5% | **+15.6%** | 635 | +17 | -0.36 |
| operations & support | 343 | 365 | +6.4% | +5.6% | 362 | -3 | +0.06 |
| product development | 333 | 375 | +12.5% | +12.0% | 373 | -2 | +0.04 |
| **sales & marketing** | 585 | **730** | **+24.8%** | **+29.9%** | **760** | **+30** | **-0.62** |
| **G&A ex reserves** | 257 | **272** | +5.8% | **-5.4%** | **243** | **-29** | **+0.60** |
| total | | | | | | **+14** | **-0.28** |

S&M is the line most under-forecast relative to the company's own recent pace (-0.62pp), but **G&A is over-forecast
by almost exactly as much (+0.60pp)** — M1 carries G&A growing at +5.8% while 1H26 actually ran *down* 5.4% y/y.
The two cancel. So "the model's cost lines are too low" is not right either: they are too low on marketing and too
high on G&A, and on net roughly right against the company's own 1H26 behaviour.

**(c) What the gap actually is: noise.** 1.489pp on a $4,804M quarter is **$71.5M of cost**, which is **1.23x
M1's own h=0 total-cash-cost MAE ($58.1M in W1, $49.8M in W2)** and 0.53x its h=0 margin sd (2.8pp). A one-sigma
cost miss covers most of it. **The model does not contradict the sentence at any meaningful confidence — it is a
noisy point that happens to land on the wrong side of a line.** That is why we clipped rather than re-fitted:
there is no defensible re-specification, and the sentence is information the model does not have.

**(d) What it would take.** Turning the question around, because our model already prints above 3Q25: for 3Q26 to
land *at* the sentence, total cash costs must be **$2,398M** rather than the model's $2,326M — **S&M at $802M,
+37.0% y/y**, above anything the company has printed (1H26 peak was +34.1% in 1Q26), or the same $72M spread over
pd and G&A. For 3Q26 to print *above* 3Q25 costs only need to stay below $2,398M, which both the model's S&M
(+24.8%) and the 1H26 pace (+29.9%) comfortably do. Read plainly: **the sentence is management telling us they
intend to spend more in Q3 than any cost trend implies.** That is a statement about intent, and it beats our
extrapolation — but it is also exactly the statement the memo should put pressure on, because $48M of S&M is
1.0pp of 3Q26 margin and management has more discretion over that line than over anything else on the P&L.

**(e) Consequences we have booked.** Card 3Q26 = **50.09% / $2,406M**; FY26 = **35.68%**, +0.18pp over the floor
(was 36.18% / +0.68pp); M6's floor-cushion claim restated (Q5 of its own note's D3). And one consequence for the
board: **the recommended `60/20/20` blend's LIVE 3Q26 of 50.39% is itself 0.31pp above the ceiling**, carried
there by the 20% family leg (implied family average 51.29%). Clipping only the family leg moves the blend to
**50.15%**; clipping nothing leaves the memo recommending a number management has told us not to expect.

## Q7. "Is `best1` selecting a different alt-signal per line per vintage, and would a single shared signal across lines give up line accuracy for margin accuracy?"

**No, `best1` is not churning.** The selection is made **once**, on the full-window h=0 recency-weighted line IV
averaged over W1 and W2, and then held fixed at every vintage; only the coefficient `c` is refit
(`M4_alt_augmented_best1_selection.csv`, `_coefs_by_vintage.csv`). The five picks are:
cor `event_E02_cor_cash@1`, ops `emp_business_support_services@1`, pd `careers_open_roles@2`,
sm `trends_qtd4_share_ww@0`, ga `emp_computer_systems_design@2`. So the margin damage is **not** vintage-to-vintage
signal instability; it is five different, mutually uncorrelated series pushing five line errors in five directions
that no longer cancel in the sum.

**And the damage is concentrated in one pick.** The per-signal margin IVs in the same file (h=0, W1, rw) are
cor **1.011**, ops **1.032**, pd **1.018**, ga **1.009** — and sm `trends_qtd4_share_ww@0` **1.253**. The composite
is 1.233. **The single signal with the best *line* IV in the whole grid (sm 0.899, a 10% improvement in the S&M
line) is also, on its own, responsible for essentially all of the composite's 23% margin degradation.** The reason
is mechanical and worth putting in the memo: S&M is the largest cash line ($730M of a $2,326M stack) and M1's S&M
error is **negatively** correlated with the rest of the stack's error. "Improving" S&M in isolation removes a
hedge. This is the sharpest available illustration of M4's own warning.

**Would selecting on the margin instead do better? We checked the whole grid, and the honest answer is
"marginally, and not distinguishably from luck."** Restricting to the **50 real (gated) tests** — placebo rows
excluded — and ranking each line's candidates by margin IV rather than line IV:

| line | n candidates | best-on-margin signal | margin IV W1 / W2 | candidates with margin IV < 1 in **both** windows |
|---|---|---|---|---|
| cor | 10 | `ppi_data_hosting@1` | 0.974 / 0.948 | 2 |
| ops | 10 | `playstore_ratings_new_per_day@2` | **0.903 / 0.876** | 6 |
| pd | 12 | `ahe_information@2` | 0.992 / 0.988 | 5 |
| sm | 12 | `trends_airbnb_share_us@2` | **0.906 / 0.901** | 2 |
| ga | 6 | `careers_open_roles@1` | 0.989 / 0.986 | 3 |

So a margin-selected `best1` would land around **0.90-0.99** rather than `best1_rw`'s 1.233 — an improvement, but
one that should not be believed and that we deliberately did **not** fit. Four reasons. (i) The **median** margin
IV over the 50 real tests is **1.010 (W1) / 1.011 (W2)**, and **18 of 50** sit below 1.0 in both windows — 36%,
which is the coin-flip rate M4's own 1,000-draw random-series placebo predicts for a two-window bar, and the same
order as the red team's 30% survivor null. (ii) It is a five-way best-of-6-to-12 **in-sample selection on 14
quarters**, exactly the procedure M4's placebo prices at a **22.5%** false-positive rate for best-of-5 on the
noisiest line. (iii) The two picks doing the work fail on economics: `playstore_ratings_new_per_day` on ops is
**wrong-signed at both leads** (c -0.007 to -0.020 against an expected +, M4 section 7), and
`trends_airbnb_share_us@2` is the same Trends series M4 showed is worth nothing once it is knowable (lead 1 line
IV 1.079 / 1.023). (iv) It would be a **post-hoc spec added after seeing the grid** — the exact failure mode R05
caught in M3.

The single-shared-signal variant is weaker still: of the five signals `best1` actually picked, four have margin
IVs of **1.009-1.032**, so a shared version of any of those is worse than `none`. The only composite anywhere
near 1.00 is `ridge_all_eq` at 0.972 / 0.966 — the shared-signal idea taken to its limit as heavy L2 shrinkage
across all 26 candidates — and that "improvement" is t **-0.20** (W1, p 0.84, 7 of 14) / t **-0.52** (W2, p 0.60,
5 of 10) on **37 free parameters against 14 quarters**. It is not a result.

**The constructive answer is therefore a change of selection criterion with a pre-registered pass line, not a
different signal count.** M4's amended rule should read: *score cost-line work on `adj_ebitda_margin_pct`, score
lines against `seasonal_naive_drift` and never against `seasonal_naive`, and price any selection rule against the
random-series placebo before believing it.* If anyone does want to fit the margin-selected composite before the
finals, it needs its own pre-registration, its own best-of-k placebo, and a paired p-value — on this evidence we
would expect it to come back inside noise.

## Note on section 2 of the board (25 line objects beat naive on lines, 11 at/worse on margin)

Confirmed, and we would go further: **against `seasonal_naive_drift` the line "wins" largely disappear too.**
Mean line ratio vs drift at h=0: M1 `b_elastic_rw` **1.000** (W1) / 1.029 (W2), M6 `l0_rw` 1.007 / 1.021,
M4 `best1_rw` 0.958 / 0.950. Per line, only cost of revenue survives (0.65-0.84); pd and S&M lose in every
method; total cash costs lose in every method (1.14-1.24). So the board's "+0.59 correlation between the line
ratio and the margin ratio is weak" understates it — a large part of the line ratio is not skill at all, it is
the growth term in a baseline that does not have one. Recommend the board's section 2 add the drift column, and
that WS23's selection rule be stated as **"select on `adj_ebitda_margin_pct`; report line ratios only against
`seasonal_naive_drift`."**

---

## Files changed by group A

**Code:** `analysis/src/margin_build/22_discussion_group_A/` (new: `repro_skill.py`, `repro_drift.py`, `README.md`);
`analysis/src/margin_build/M1_driver_lines/run.py`, `.../M4_alt_augmented/run.py`,
`.../M6_cycle_flex/run.py`; `.../M1_driver_lines/README.md`, `.../M4_alt_augmented/README.md`,
`.../M6_cycle_flex/README.md`.

**New data:** `data/processed/margin_build/M1_driver_lines/M1_driver_lines_oracle_diagnostic.csv`,
`..._live_guide_reconciled.csv`; `data/processed/margin_build/M6_cycle_flex/M6_cycle_flex_oracle_diagnostic.csv`,
`..._fy28_withdrawn.csv`, `..._guide_clipped_floor.csv`; `data/manifests/margin_build/M6_cycle_flex.csv`;
`data/processed/margin_build/22_discussion_group_A/{groupA_paired_tests,groupA_paired_vs_drift}.csv`;
`_pre_discussion/` backup folders in all three package data folders and six
`data/processed/margin_build/registry/*_pre_discussion.csv.bak`.

**Changed data:** `registry/driver-lines__margin_v2.csv` (3,612 -> 3,096 rows),
`registry/driver-lines__lines_v2.csv` (6,020 -> 5,160), `registry/cycle-flex__flex_margin.csv` (1,872 -> 1,404),
`registry/cycle-flex__flex_lines.csv` (3,120 -> 2,340); `M1_driver_lines_{forecasts_wide,registry_long,
params_by_vintage,grid_margin,per_line_mape,build}.{csv,json}` (`d_steps_rw` rows only);
`M6_cycle_flex_{forecasts_wide,registry_long,annual_forecasts,build}.{csv,json}`.
`alt-augmented__*.csv` and every other M4 output are **unchanged, byte-identical**.

**Notes:** `docs/margin-build/notes/M1_driver_lines.md`, `M4_alt_augmented.md`, `M6_cycle_flex.md` (appended
"Discussion response" sections); this file.

**Not run:** `score.py` (per the prompt). Every scoreboard number quoted here is from the pre-discussion scoring
plus our own paired tests computed directly off the registry and the by-quarter file; the orchestrator's single
re-score is what the memo should read off.


---

# group_B.md

# WS22 discussion — group B: M2 `margin-ts` and M3 `guide-policy-margin`

Margin build, 14 Sep 2026. Agent: group B (history and guide). Interpreter `py -3.13`. `score.py` was **not**
run (the orchestrator scores once at the end). Reproduction scripts:
`analysis/src/margin_build/M2_margin_ts/discussion_checks.py` and
`analysis/src/margin_build/M3_guide_policy_margin/discussion_checks.py` (both exit 0, ~10 s each).
Full before/after detail is in the "Discussion response" sections appended to
`docs/margin-build/notes/M2_margin_ts.md` and `docs/margin-build/notes/M3_guide_policy_margin.md`.

**Headline.** Both methods accept the red team's central finding: at n = 14 / 10, neither M2 nor M3 forecasts
the adjusted EBITDA margin better than last year's margin by an amount distinguishable from zero, and the
`survives_both_windows` flag should not be quoted. Both methods' registered numbers are unchanged — the fixes
are labels, one withdrawal and one added spec. One claim is rebuilt and defended with a paired test that the
red team did not run: **M3's allocation rule beats the harness's `guide_implied` proration in both windows
(W1 p 0.028, 12/14; W2 p 0.030, 9/10) using pre-registered specs only.** And one M2 claim is downgraded
without being asked: the sentence rule's dollar-EBITDA win over the Street is 10/14 and 8/10 quarters but
p 0.51 / 0.31, so it corroborates M5's flow-through rather than standing on its own.

## 1. Findings table

| finding | method | decision | reproduced? | what changed | files |
|---|---|---|---|---|---|
| **R01** survivor flag ~30% free | M2, M3 | ACCEPT | yes (accepted the red team's 2,000-draw null; did not re-run it) | every claim in both notes re-quoted with a paired NW(1) p-value and a quarters-better count; "survives both windows" language withdrawn from both | `M2_discussion_paired_tests.csv`, `M3_discussion_paired_tests.csv` |
| **R02** no W1-significant margin win | M2, M3 | ACCEPT (+ one addition) | yes, exactly (M2 sentence t -0.22 W1; M3 `rw_hl4_pin` W2 p 0.033, `last_pin` W2 p 0.006) | M2 bottom-line 2 and M3 P1 restated as "not distinguishable from y[q-4]"; **added**: M3 vs the harness `guide_implied` baseline IS significant in both windows, on pre-registered specs | both paired-test CSVs |
| **R03** oracle specs labelled PIT | M2, M3 | ACCEPT + fix | yes (4 specs across the two methods) | specs renamed with an `oracle_` prefix (substrings `revknown`/`nightsknown` kept) and every row's `notes` opens "ORACLE DIAGNOSTIC … exclude from survivor and ranking tables"; 4,548 rows stamped | `m2_margin_ts.py`, `M3/run.py`, 4 registry files |
| **R05** M3's passing specs are post-hoc | M3 | ACCEPT | accepted the red team's git evidence (no git in this round); the note's own text confirms it | `PRE_REGISTERED_SPECS` / `POST_HOC_SPECS` added to the code; every post-hoc row stamped in `notes`; **pass line restated on pre-registered specs only: P1 fails (rw_hl4 3.83 pp W1 vs naive 2.24)** | `M3/run.py`, M3 note |
| **R06** the pin's win is one quarter | M3 | ACCEPT | yes, to 3 decimals (4/14, -3.18 pp in 2023Q4, +0.186 without it) | the pin is described as clipping the break quarters, not as quarter-to-quarter accuracy | `M3_discussion_pin_decomposition.csv` |
| **R07** sentence rule hypothesis from the test set | M2 | ACCEPT | yes (13 non-zero, 9/4, **3 sign changes**, always-negative agrees 8/13, rule 12/13) | presented as a descriptive regularity with an effective n of 4 direction changes; not quoted as a tested forecaster | `M2_discussion_sentence_summary.csv` |
| **R08** flags asserted at n=3 | M3 | ACCEPT | yes (`q4_implied\|guide_mid` n=3 W1 / 2 W2) | the flag is withdrawn; P5 restated as three quarters with a mean +2.87 pp under-call | M3 note |
| **R10** intervals too wide | M2, M3 | ACCEPT (with one distinction) | yes | M3's LIVE band (9.3-9.6 pp) replaced for quoting by the realised h=0 spread (±2.5 pp); M2's sentence band is the right *width* (4.33 vs 4.39 pp) but centred 1.3-1.8 pp low — bias-corrected 3Q26 is **49.4-49.9%** | `M2_discussion_bands.csv`, `M3_discussion_live_coherence.csv` |
| **R12** M3's LIVE 4Q26 34.51% | M3 | ACCEPT + fix | yes (above every 2022-26 Q4; FY26 37.03%) | `rw_hl4_pin` / `rw_hl4` / `equal` LIVE rows stamped "NOT QUOTABLE (WS21 R12)"; new zero-parameter spec **`nov_sentence_pin`** registered: 3Q26 50.09, **4Q26 29.90% / $950M**, FY26 36.00%, every quarter inside its historical range | `M3/run.py`, registry (+312 rows) |
| **R14** line wins are near-free | M2 | ACCEPT | n/a (M2 already scores lines against `seasonal_naive_drift`) | restated: the specs whose lines beat drift (CoR 0.82, Ops 0.90) lose to y[q-4] on the margin (1.05-1.08); no line result may be quoted as evidence about the margin | M2 note |
| **R17** h=0 is post-letter | M2, M3 | ACCEPT | n/a | stated on both cards; for 4Q26 before the 5 Nov letter the honest anchors are y[q-4] 28.29% / Street 28.90% | both notes |
| **R18** M2's Street stamp | M2 | ACCEPT + fix | yes | LIVE table now carries `street_pull_date` (2026-09-13), `street_is_comparison_only`, `street_post_vintage` beside `vintage_date` (2026-09-11) | `m2_margin_ts.py` |
| **R19/R20/R21/R22** process, reproducibility, kill list, PIT | M2, M3 | ACCEPT (pass) | yes — both packages rebuilt byte-identically apart from the intended label changes | nothing | — |
| orchestrator: M2 `q_guide_in_force` leakage via `print_date` | M2 | **REJECT, with numbers** | yes | none needed: **20 of 20** quarterly margin guides have `guide_date` = the print date of the quarter in `print_quarter`, **19 of 20** have `target_period = print_quarter + 1`, and the exception (2Q25 letter -> 4Q25) is a *forward* two-quarter guide. No sentence can leak backwards | `M2_discussion_guide_ledger.csv` |
| orchestrator: M2 to adopt M3's "slightly" k (~1.0-1.5) as a spec | M2 | **REJECT as a spec**, ACCEPT as a scenario | yes (n=3: -0.76, +1.16, -2.55; two clean cases mean 0.96 pp) | no new spec — post-hoc, n 2-3, one of the three has the wrong sign, and it would add a parameter to a rule that already cannot be distinguished from the naive. Quoted as a scenario: adverb haircut 48.6-49.4% vs bias-corrected 49.4-49.9% — the two routes agree | M2 note §7 |

Nothing was deleted. Both `_pre_discussion/` folders hold every CSV and registry file as it stood before this
round; `max abs diff` between the old and new registry points is **0.0** for M2 (3,936 LIVE rows checked) and
**0.0** for M3 (all 2,808 pre-existing rows), with 312 rows added for the one new M3 spec.

## 2. What each method now claims

**M2 `margin-ts`.** No time-series object built from ABNB's own history forecasts the adjusted EBITDA margin
better than last year's margin by a distinguishable amount at n 14/10. The best of them — the
management-sentence rule, `q_sentence_direction|k_fit_rw`, 2 free parameters — runs at 0.92x the naive in W1
(t -0.22, p 0.83, 7/14) and 0.84x in W2 (p 0.59, 5/10), and at 1.25-1.30x the Street. In EBITDA **dollars** the
same rule sits 14-18% below the Street's MAE and is better in 10 of 14 and 8 of 10 quarters, but p is 0.51 /
0.31: it corroborates M5's dollar flow-through finding, it does not independently establish one. Its LIVE 3Q26
reading is 48.06% as registered and **49.4-49.9% once its own -1.3 to -1.8 pp PIT bias is removed**, which is
where the Street (49.78%), M3's adverb answer (48.6-49.4%) and M3's ceiling pin (50.09%) also sit. At h=1
nothing in M2 beats y[q-4]; the 4Q26 anchor is 28.29% naive / 28.90% Street. The sentence rule's direction has
been right 12 of the 13 times management gave one, with 3 sign changes in 14 quarters — a regularity worth
stating on the card, with the effective n said out loud.

**M3 `guide-policy-margin`.** The FY margin guide is a budget constraint, and the way to read it is
`m_q = m_{q-4} + delta` with one delta solved on the remaining quarters — not the seasonal-share proration the
harness `guide_implied` baseline uses, which is significantly **worse** than y[q-4] (W1 ratio 2.06, t +2.96,
p 0.003). Replacing the proration halves the guide-implied error in both windows on a pre-registered,
zero-cushion spec (`nocushion`: W1 0.546x, t -2.20, p 0.028, 12/14, sign p 0.013; W2 0.669x, t -2.16, p 0.030,
9/10, sign p 0.021), and the result survives dropping the single best quarter. That is a measurement of the
guide, not forecasting skill: the repaired object still does not beat y[q-4] (2.39 vs 2.24 pp W1) or the Street
(1.59 / 1.31). The pre-registered main spec `rw_hl4` fails its pass line; the pin specs are exploratory and
their W1 edge is 2023Q4. The November sentence is mechanical — numeric floor + 50 bp, exact 2 of 2 — so 5 Nov
reads **"approximately 36%"** (p ~0.45-0.50), and that sentence plus the budget identity puts **4Q26 at
29.9-30.9% and $950-983M against a Street $914M**, band ±2.5 pp, with 3Q26 the swing factor at **-1.51 pp of
4Q26 per +1 pp of 3Q26**. The February floor is not mechanical (82 bp MAE, wrong in both years that mattered)
and no FY27 margin should be taken from this method.

## 3. Recommended weights for the WS23 combination

| object (spec) | weight | reason |
|---|---|---|
| M3 `actual_given_guide` **`nov_sentence_pin`** — the 4Q26 / FY26 *conditional* path | **0.20 of the 4Q26 margin view** (0 elsewhere) | the only LIVE path in M3 that is inside every historical quarter range and consistent with the sentence the November rule predicts; 0 estimated parameters; it is the one thing in this run that prices the 5 Nov *guide* rather than the print. Conditional on the FY sentence — re-solve it live on the call. |
| M3 the **budget identity** (1 pp of 3Q26 = -1.51 pp of 4Q26) | **not a weight — a constraint on the combination** | no other object in the run produces it; the combined 3Q26 and 4Q26 margins should be forced to satisfy it at whatever FY sentence the model assumes, instead of being averaged independently. |
| M3 `actual_given_guide` `rw_hl4_pin`, `rw_hl4`, `equal`, `last_pin`, `nocushion_pin` | **0** | R12 (LIVE path rejected by M3's own FY backtest) and R05/R06 (post-hoc, one-quarter win). Keep `nocushion` in the *diagnostic* table as the object that carries the allocation result. |
| M3 `q4_implied` | **0 as a forecast**, keep as a fact | n=3; its content — the sentence-implied Q4 has been under-called by +0.7 to +4.3 pp every year, and the Street sits on the implied number — belongs on the card as a statement, not in a weighted average. |
| M2 `q_sentence_direction` `k_fit_rw` — margin | **0.10**, and only with the bias correction | the best history-only margin object in the run, but p 0.83 / 0.59 against y[q-4]; as registered it is 1.7 pp below the Street on 3Q26 and that gap is its own PIT bias. Use 49.4-49.9%, not 48.06%. |
| M2 `q_sentence_direction` — EBITDA dollars | **0**, cite alongside M5 | 0.86x / 0.82x the Street, 10/14 and 8/10, p 0.51 / 0.31 — the same direction as M5's `street_plus_flowthrough`, which is the object that should carry the dollar weight. Double-weighting two correlated statements of "the Street is low" would overstate the evidence. |
| M2 `sarima_margin` (both specs), `yoy_margin_change`, `incremental_margin`, `pct_rev_seasonal`, `ensemble_simple` | **0** | P1 failed; 13-15 parameters on 22 observations for the SARIMA lines; the LIVE 51.5% sits above management's ceiling sentence with no argument for overriding it. |
| M2 `per_night_seasonal` `g_k4_rw` | **0 unconditionally, 0.10 of the cost-line view if the team adopts its nights forecast** | with nights known its W2 margin MAE is 1.31 pp (Street level) and its per-night growth rates beat drift for CoR and Ops; with a naive nights leg it is worse than y[q-4]. That is a conditional statement for M1's nights path to cash, not an independent forecaster. |
| every `oracle_*` spec in both methods | **0, permanently** | diagnostics; they read the actual revenue or nights. |

Sum of the non-zero margin weights above is deliberately small: on this evidence the combination's centre of
gravity should be the Street plus M5's flow-through, with M3's budget identity as the constraint that ties
3Q26 to 4Q26 and M2's sentence rule as a sanity bound.

## 4. For the orchestrator

1. **Re-run `score.py` after all three groups finish.** M3's registry gained 312 rows (one new spec) and four
   spec_ids were renamed across the two methods, so `scoreboard_margin.csv`, the WS20 tables built before
   00:00 and `20_excluded_oracle_and_thin.csv` are stale for `margin-ts` and `guide-policy-margin`.
   New / renamed spec ids: `margin-ts`: `oracle_k4_rw_revknown`, `oracle_drift_k4_rw_revknown`,
   `oracle_g_k4_rw_nightsknown`; `guide-policy-margin`: `oracle_rw_hl4_revknown`, **`nov_sentence_pin`** (new).
2. **`M2_margin_ts_scoreboard_extract.csv` was not rewritten** (the rebuild ran with `--no-score`); re-run
   `py -3.13 analysis/src/margin_build/M2_margin_ts/run.py` without the flag after the final score if the
   extract is wanted fresh. All other M2 outputs are current.
3. **Do not let `nov_sentence_pin` be read as a pass.** It is post-hoc (added tonight as the R12 fix) and it is
   labelled as such in the registry `notes`. Its numbers are quotable as a *conditional* path; its backtest
   (0.842x naive in W1, p 0.28) is not a win.
4. **Kill-list addendum, group B's items:** M3's LIVE 4Q26 34.51% / FY26 37.03% (withdrawn here); M3's
   `q4_implied` "survives both windows" flag (n=3); "M2's sentence rule beats the Street in dollars" without
   its p-value; any `oracle_*` number presented as a forecast.

---

# 5. Answers to the WS20 scoreboard's open questions (`notes/20_scoreboard.md` §11)

Questions 3 and 4 are addressed to M3, 8 and 9 to M2, and 6 to "M1, M4, M6 and M2-SARIMA" jointly — the
M2-SARIMA half is answered here. Question 13's recommendation is endorsed. Everything below is computed from
the rebuilt registry and the two `discussion_checks.py` scripts.

## Q3 (to M3) — are the pinned specs the ones you want quoted, and can the cushion be estimated on more than four observations?

**No, and no.**

*Which specs.* Not `rw_hl4_pin` or `last_pin`. On the note's own text they are post-hoc (R05), their W1
advantage over y[q-4] is one quarter wide (R06: 2023Q4, the $931M lodging-tax reserve; without it they are
*worse* than the naive by +0.19 and +0.22 pp), and `rw_hl4_pin`'s LIVE path is the one R12 rejects. Quote
instead:
- **the allocation result on the pre-registered `nocushion` spec** — `m_q = m_{q-4} + delta` against the
  harness's seasonal-share proration: 0.546x in W1 (t -2.20, p 0.028, 12/14, sign p 0.013) and 0.669x in W2
  (t -2.16, p 0.030, 9/10, sign p 0.021), robust to dropping the best quarter. This is M3's real, defensible
  finding and it uses no cushion at all;
- **`nov_sentence_pin`** (registered tonight, labelled post-hoc) for the LIVE path, because it is the only M3
  spec whose 3Q26-4Q27 quarters all sit inside the 2022-26 range for their quarter of the year;
- the **budget identity** and the **November sentence rule** (floor + 50 bp, exact 2/2), which are
  parameter-free and are the parts of M3 no other method produces.

*The hindsight share.* 0.24 for the pinned specs and 0.64 for `rw_hl4_prorata` is exactly the cushion doing
the hindsight work — note that `nocushion` and `nov_sentence_pin` have **zero estimated cushion parameters**,
so their PIT and full_sample replays differ only through the revenue leg. Preferring them removes the
criticism rather than answering it.

*Can the cushion sample be enlarged?* Not within this estimand. `M3_cushion_history.csv` shows the FEB, MAY
and AUG buckets are not three samples: they are **the same four fiscal years measured against the same guide
level** (FY22 +7.97, FY23 +2.27, FY24 +1.40, FY25 +0.60 appear identically in all three buckets, because the
floor was unchanged through the year in every year). Pooling them changes the mean by 0.00 pp and the
effective n not at all. The November bucket is three more observations of the *same four* fiscal years against
a later, tighter sentence (+0.77, +0.90, +0.10), and pooling it with the February floors would import a
+0.59 pp cushion into a guide type whose realised cushion averages +3.06 — the direction the FY backtest (P2)
already rejects. **The hard ceiling is the number of fiscal years with both a guide and a realised FY margin:
four, rising to five when FY26 prints in February 2027.** The only honest ways out are (a) stop estimating the
cushion — which is what `nocushion` and `nov_sentence_pin` do, and they are the better specs — or (b) change
the estimand to something with n ≈ 20, e.g. the *revenue* guide cushion in the frozen harness or the quarterly
margin sentences, as a prior on management conservatism. I did not fit (b) tonight; it is a WS23 option, and it
would be a new parameter with its own pre-registration.

### Q3 addendum — the WS23 plan to weight `actual_given_guide|rw_hl4_pin` at ~20%

The coordinator relays that WS23 intends about 20% on `rw_hl4_pin` because M3 is the only orthogonal view
(mean pairwise r 0.118) and the best in the 1H23 regime break (0.79 pp). **Keep the 20%, move it to
`nov_sentence_pin`, and know what the swap costs.** Reproduced on the W1 h=0 PIT errors
(`M3_discussion_cross_method.csv`, `M3_discussion_error_correlations.csv`):

| object | mean pairwise r vs the other methods | 1H23 stress MAE (2023Q1-Q2) | W1 h=0 MAE |
|---|---|---|---|
| M3 `rw_hl4_pin` | **0.141** | 0.79 pp | 2.18 |
| **M3 `nov_sentence_pin`** | 0.482 | **0.77 pp** | **1.88** |
| M3 `nocushion` | 0.366 | 0.85 pp | 2.39 |
| M2 `q_sentence_direction\|k_fit_rw` | **-0.075** | 4.65 pp | 2.07 |
| M1 / M4 / M6 main specs | 0.60 each (0.99-1.00 with each other) | 1.99-2.42 | 2.20-2.26 |
| Street | 0.568 | 1.34 | 1.59 |

1. **The regime-break property is the guide, not the pin's cushion**: `nov_sentence_pin` is *better* in 1H23
   (0.77 vs 0.79 pp) and better over W1 as a whole (1.88 vs 2.18). The swap loses nothing WS20 valued there.
2. **The orthogonality is partly the rejected cushion.** `rw_hl4_pin`'s r of 0.14 comes substantially from the
   erratic AUG-bucket cushion (+7.97 pp at the first vintages, +0.60 at the last); with the cushion removed the
   guide-based view correlates 0.48 with the rest. Low correlation produced by a parameter that the method's
   own FY backtest rejects is noise diversification, not information diversification, and WS23 should not pay
   for it. **If WS23 wants a genuinely uncorrelated object, it is M2's sentence rule (r = -0.075)** — but it
   is the worst object in 1H23 (4.65 pp) and it has no 4Q26 row, so it diversifies the 3Q26 call, not the
   4Q26 one.
3. **What the swap does to the blend.** At a 20% weight the LIVE difference is
   0.20 x (34.51 - 29.90) = **+0.92 pp on the blended 4Q26 margin** and 0.20 x ($1,097M - $950M) = **+$29M on
   blended 4Q26 EBITDA**. With `rw_hl4_pin` in at 20% the blend sits about 0.9 pp above the method median and
   materially above Street on the quarter that 5 Nov will actually guide; with `nov_sentence_pin` it sits
   ~1.0 pp above Street (29.9% vs 28.90%), which is the claim M3 is willing to defend.

## Q4 (to M3) — is 34.51% the arithmetic or an allocation artefact?

**Both, and it is withdrawn.** The mechanism is an amplifier, and it is worth writing down because it will
recur on 5 Nov. With 1H26 actual ($6,286M revenue, $1,780M adj EBITDA) and the v2b path (3Q26 $4,804M,
4Q26 $3,178M, FY26 $14,268M), pinning 3Q26 at the ceiling (50.09% = $2,406M) leaves 4Q26 as the residual, so

> **1 pp of FY margin = 4.49 pp of 4Q26 margin** (14,268 / 3,178), and 1 pp of 3Q26 margin = -1.51 pp of 4Q26.

| FY sentence assumed | FY adj EBITDA | residual after 1H and the Q3 pin | 4Q26 margin | 4Q26 $ |
|---|---|---|---|---|
| 37.03% (`rw_hl4_pin`: floor 35.5 + the AUG cushion +1.53) | $5,283M | $1,097M | **34.52%** | 1,097 |
| **36.00% (`nov_sentence_pin`: the predicted November sentence)** | $5,137M | $950M | **29.90%** | **950** |
| 35.50% (floor held literally) | $5,065M | $879M | 27.65% | 879 |

So the 5.6 pp outlier is a **1.53 pp cushion multiplied by 4.49** — and that cushion is the AUG-bucket estimate
that M3's own FY backtest shows over-predicts by 1.2-3.2 pp PIT (P2 fails; the literal guide beats every
cushioned version at the FY level, MAE 1.22 vs 2.75). The allocation rule is not the problem — the residual has
to land somewhere once Q3 is pinned, and that is the true economics of an FY guide — the rejected cushion is.
**Carry 29.9% ($950M) at a 50.09% Q3, or 30.9% ($983M) at a 49.4% Q3 ("down slightly" sized by M3's adverb
study), against a Street $914M. Band ±2.5 pp** (the realised h=0 error spread, not the registered 9.3 pp
Gaussian band). The `rw_hl4_pin` LIVE rows are now stamped NOT QUOTABLE in the registry.

## Q6 (to M2-SARIMA) — which line breaches the 50.09% ceiling, and what would put 3Q26 above 3Q25?

`sarima_margin|lines_aicc` LIVE 3Q26 is 51.50% on total cash costs of **$2,330M**. The ceiling needs
$2,397M, i.e. **$68M more cost**. The line responsible is **sales & marketing**: SARIMA puts 3Q26 S&M at
**$708M** (+21% y/y on 3Q25's $585M) against $797M from the %-of-revenue object and $751M from the per-night
object, and the gap to those two ($89M and $43M) more than covers the $68M breach; the other four lines are
within $15M of each other across all three objects (CoR 630-648, Ops 364-366, PD 373-374, G&A 261-282).

The reason is mechanical: AICc picks `(0,0,0)(0,1,0)4` for the S&M log-line — a pure seasonal difference with
no drift — so it carries 3Q25's level forward with the average log step, while S&M has stepped up **+34.1% y/y
in 1Q26 and +26.4% in 2Q26** (22.8% -> 26.0% and 20.6% -> 22.4% of revenue). Holding SARIMA's other four lines,
the ceiling implies 3Q26 S&M of **$748M, i.e. +27.9% y/y — exactly the 1H26 run-rate.** So the sentence and the
1H26 spending trend agree with each other, and it is the SARIMA S&M line that is the outlier.

**What would put 3Q26 above 3Q25 (50.09%)?** S&M below ~$748M in the quarter — a genuine deceleration from
+27% to +21% y/y in the middle of the brand-marketing ramp — with no offset from CoR (2Q26 $633M, +16% y/y)
or Ops. Nothing in M2 supports that, and M2's own pass line P1 failed, so **M2 does not defend
the 51.5% number and recommends weight 0 on it**; the time-series anchor M2 stands behind is the
sentence rule, bias-corrected, at 49.4-49.9%.

## Q8 (to M2) — is `q_sentence_direction` usable without a sentence, and should the n=1 h=1 rows be withdrawn?

*Without a sentence, it is the naive.* The rule is `m[q-4] + k x d`; when management gives no directional
sentence, d = 0 and the forecast **is** y[q-4], with the same error. That happened once in W1 (1Q26,
"approximately flat", scored as the naive) and the sentence was absent in none of the other 13 quarters — of
which 9 were ceilings and 4 floors, with only 3 sign changes in the sequence (R07). So the object is usable
only in the 13 of 14 W1 quarters that carried a *directional* sentence, and in the rest it adds nothing. Practically this is not a
limitation for 5 Nov: the 3Q26 sentence exists ("down slightly", 6 Aug letter). It **is** a limitation for
4Q26, which will not have a sentence until the 5 Nov letter itself — which is the same point as R17.

*The h=1 rows.* There are exactly **four h=1 rows per replay per window** — one target quarter (2025Q4,
guided two quarters ahead in the 2Q25 letter) across the four specs — so **n = 1 in every h=1 cell**, and
W1 and W2 are the same single quarter. **Yes: withdraw them from the quotable and flag-bearing set.** I have
not deleted them from the registry (a failed or thin test is written up, not deleted, and they are legitimate
rows), but no flag or ratio computed on n=1 should appear in WS20 or WS23 — which is exactly the generic fix
R08 proposes (suppress the flags below n=8, or print n beside every flag). For the record the four points
were 28.75 / 27.55 / 29.32 / 28.54 against an actual 28.29 (errors +0.46, -0.74, +1.03, +0.25), which is
respectable and means nothing at n=1.

## Q9 (to M2) — is there a LIVE 1Q27-4Q27 path from `incremental_margin|k8_median` I will stand behind?

**No.** It is registered, it is in `M2_margin_ts_live_forecasts.csv`, and here it is, but M2 does not defend
it and recommends weight 0:

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 | FY27 |
|---|---|---|---|---|---|---|---|
| margin % | 47.93 | 29.20 | 21.36 | 35.01 | 46.81 | 29.72 | **35.15** |
| adj EBITDA $M | 2,303 | 928 | 652 | 1,410 | 2,472 | 1,030 | **5,565** |
| Street | 2,362 | 914 | 611 | 1,452 | 2,696 | 1,068 | 5,766 (36.45%) |

Three reasons. (1) **The parameter is unstable:** m has been 0.53 (Feb-23), 0.33 (Aug-23), 0.57 (May-24),
0.21 (Feb-26) and is 0.355 today — a path built on a single incremental margin held fixed for six quarters is
a statement about m, not about 2027. (2) **Its h=2 dollar survival is the weak-baseline artefact R14 warns
about:** seasonal naive is easy to beat in dollars for a growing series (the same object is 1.16x the naive on
the *margin* in W1), and its h=2 margin cells fail in W2 (1.21x). (3) **The $201M FY27 gap to Street is not
this object's evidence:** it is the same S&M-ramp extrapolation that puts every M2 ratio object 1.5-2.2 pp
below Street in FY27, and that is a spending decision for M1/M3 to argue, not a time-series result. If WS23
wants an FY27 EBITDA from M2 at all, the honest version is the range 34.2-35.2% margin with the note that it
assumes the 2025-26 brand-marketing ramp continues one more year at the same rate.

## Q13 (to WS21) — the `is_oracle` column

Endorsed, and half-done tonight: group B renamed all four of its oracle specs with an `oracle_` prefix
(keeping the `revknown` / `nightsknown` substrings) and stamped every row's `notes` with an ORACLE DIAGNOSTIC
warning, because FORMAT 1.0 admits no extra column and `prior_basis` accepts only `PIT` / `full_sample`. A
real `is_oracle` boolean in the frozen validator is the right fix and needs a harness change request — the
naming convention is a stopgap, and it only holds while every author uses it.

## One note on how the three groups fixed R03 differently

WS20 §12 records that M1 **removed** `e_revknown_rw` from the registry and routed it to a separate
`M1_driver_lines_oracle_diagnostic.csv`. Group B instead **kept** its four oracle specs registered and
re-labelled them (`oracle_` prefix, ORACLE DIAGNOSTIC stamp in `notes`). Both satisfy WS22's instruction;
the difference matters only to anyone counting registry rows. Group B's reason for keeping them: the whole
point of a revenue-known spec is to split cost error from revenue error *on the same scoreboard rows*, and
M_common rule 6 asks for it — deleting it costs that comparison, whereas the prefix plus the stamp makes it
impossible to mistake for a forecast and is caught by both the old (`revknown`/`nightsknown`) and the new
(`oracle_`) filters. If the orchestrator wants one convention, the prefix is the cheaper one to apply
everywhere, and the real fix is question 13's `is_oracle` column in the frozen validator.

## One flag back to WS20

`20_rankings_headline.csv`, `20_excluded_oracle_and_thin.csv` and the digest were built before these fixes, so
for `margin-ts` and `guide-policy-margin` they carry the old spec names and do not contain
`nov_sentence_pin`. They need rebuilding after the orchestrator's final `score.py`.


---

# group_C.md

# WS22 discussion — group C: M5 `street-bias`, M7 `below-ebitda`, and the margin harness (10)

Margin build run, 14 Sep 2026. Interpreter `py -3.13`. Red team read: `docs/margin-build/notes/21_red_team.md`
and `data/processed/margin_build/21_red_team/21_findings.csv` (findings addressed to M5, M7, `harness (10)`
and `ALL`). **Every finding addressed to this group reproduced.** Nothing was rejected; one finding (R25) is
accepted *and strengthened* by a new counterfactual, and one (R10) is accepted against M7's own note text.
`score.py` was not run (three agents in flight); the harness fix ships as new scorer columns plus a standalone
recomputation so WS20/23 has the numbers tonight.

## 1. Findings

| finding | method | decision | reproduced? | what changed | files |
|---|---|---|---|---|---|
| R01 `survives_both_windows` is ~30% free (null 22.1 vs 25 observed, P 0.39; W2 ⊂ W1) | harness | **ACCEPT** | yes (structural: W2's 10 quarters are a subset of W1's 14; WS21 check 07 re-read, not re-simulated) | scorer now emits a paired-loss test and a sign test per cell; the README and the scoreboard markdown header tell the reader to quote those instead of the flag | `harness_margin/significance.py` (new), `harness_margin/score.py`, `10_harness_margin/README.md` §6.1, `10_harness_margin/tests.py` |
| R02 no non-Street margin win is distinguishable from zero | harness / all | **ACCEPT** | yes: of 150 margin h=0 PIT method cells, 52 carry both survivor flags (26 object-spec pairs); **14 cells / 7 pairs** survive the n>=8 + W1 sign-test gates and **6 of the 7 are M5** | new columns `survives_both_windows_n8`, `survives_both_windows_sig`, `n_min_both_windows` | `scoreboard_significance.csv` (new) |
| R08 flags asserted on as few as 2 matched quarters | harness | **ACCEPT** | yes: `guide-policy-margin/q4_implied\|guide_mid` carries both flags on n=2; 4 both-flag cells in the whole registry have `n_min_both_windows < 8` | `n_min_both_windows` + the n8 flag; original flags untouched | same |
| R09 `replays_present` = 1 for all 1,452 baseline rows | harness | **ACCEPT (additively)** | yes: baselines write `\|PIT` / `\|full_sample` into `spec_id`, which is in the group key | new column `replays_present_fixed` (= 2 for baselines); the old column is left alone so no existing number moves in the re-score | `harness_margin/score.py` |
| R17 h=0 is a post-letter, post-guide forecast | harness / all | **ACCEPT** | yes (`panel.history_as_of`, `include_same_day=True`) | no code change (frozen convention, applied consistently); stated in the note and to be stated on the card — the 4Q26 trade into 5 Nov is an h=1-type position | `10_harness_margin.md` |
| R23 M5's margin claim fails a paired test, its dollar claim passes | M5 | **ACCEPT** | yes, to 4 dp | headline "the Street is beatable, and by a lot" withdrawn as a *margin* claim; the dollar flow-through becomes M5's single claim, always quoted with p and quarters-better | `M5_street_bias.md` §Discussion response, `M5_discussion_paired_tests.csv` (new) |
| R24 dispersion slope significant only off the pre-registered pool | M5 | **ACCEPT** | yes (`M5_secondary_tests.json`: +28.3, p 0.005, n 19 full sample vs **+17.1, se 8.1, p 0.052, n 17** from 2022Q1) | the 2022Q1+ number is now the supporting statistic; +28.3 / p 0.005 is withdrawn from the card | `M5_street_bias.md`, `M5_discussion_summary.json` |
| R25 the clip constant, not dispersion, drives `dispersion_conditioned` | M5 | **ACCEPT, strengthened** | yes: floor binds in 19 of 37 dispersion-bearing backtest rows (20/39 with LIVE; 21/39 counting the two rows within 0.01 of the floor), and in 9 of the 14 h=0 vintages from 2023-05 | **new counterfactual**: a fixed multiplier of 0.5 with no dispersion input at all scores 1.370 (W1) / 1.034 (W2) against the object's 1.330 / 0.743 and Street's 1.592 / 1.311. The dispersion conditioning adds −0.04pt in W1 (t −0.16, p 0.87, better in 6/14) and −0.29pt in W2 (t −1.16, p 0.25, better in only **4/10**). The object is "halve the bias", not "condition on dispersion". At LIVE the identity is exact: `rw_hl4` 49.7757 + 0.5 x 1.0569 = 50.3042%; `rw_hl4_med` 49.7757 + 0.5 x 0.6841 = 50.1178% | `M5_discussion_counterfactual.csv` (new), `M5_discussion_clip_audit.csv` (new) |
| R27 M5's quantiles unusable | M5 | **ACCEPT** (author already said so) | yes: cov80 = cov90 = 1.00 in all 24 h=0 cells | unchanged; band must come from another method or the realised h=0 error distribution | `M5_street_bias.md` |
| R26 M5's consensus inputs are PIT | M5 | pass, no action | yes | — | — |
| R11 M5's LIVE 3Q26 50.19% is above the 50.09% sentence ceiling | M5 | **ACCEPT / reconciled** | yes | the 0.10pt excess **is the clip**: uncapped, the object gives 49.9%, below the ceiling. M5 does not override the sentence; card reads "3Q26 margin flat vs 50.09%", beat taken in dollars | `M5_street_bias.md` |
| R10 M7's "tax quantiles under-cover" | M7 | **ACCEPT — withdrawn** | yes, and M7's note contradicted itself (0.86 / 0.90 is *above* nominal 0.80) | against the exact binomial 5-95 band, **0 of 128** M7 h=0 cov80 cells sit below it and 42 of 384 sit above; mean cov80 **0.941**. The only sub-band cells are `capex_musd` W1 h=1 (0.538 vs floor 0.615) | `M7_below_ebitda.md`, `M7_discussion_coverage_band.csv` (new) |
| R16 backtested EPS/FCF error is the EBITDA input, not the bridge | M7 | **ACCEPT with a number** | yes, and it splits by window | the EBITDA input carries **64% of the h=0 EPS MAE in W2** (corr 0.92) but only **17% in W1** (corr 0.23), where the 2023 break quarters are the bridge's own error. Quoting rule: below-the-line accuracy from `ebitda_known` ($0.066 W2), total EPS error from `ebitda_pit` ($0.125), never mixed | `M7_below_ebitda.md`, `M7_discussion_eps_decomp.csv` (new) |
| R13 M7's FRED inputs have no re-pull fallback | M7 | **ACCEPT-DEFER** | yes (`run.py:109` `load_daily`) | not fixed tonight: M7's `run.py` ends by calling `score.py`, which this round may not run, so a code change could not be replayed. The exact 6-line patch is written into the note for the morning; meanwhile the three files are manifested and the README says to re-pull by hand | `M7_below_ebitda.md` |
| R14 line-level wins are close to free | M7 (and all) | **ACCEPT, mostly not binding** | yes | M7 makes no margin claim, and already quotes `seasonal_naive_drift` / `trailing4` alongside. One correction: of its four-target block, against the *drift* baseline only share count (0.40 / 0.67) and weakly D&A (0.81 / 1.00) are genuine; SBC is 0.93 / 0.96 | `M7_below_ebitda.md` |
| R19, R20, R21, R22 (process, reproducibility, kill list, PIT) | all | accepted / pass | yes | no action for this group | — |

## 2. What each object now claims

**M5 `street-bias`.** One claim, and it is the only object in the run that survives an adversarial test. Starting
from the Street's h=0 EBITDA and adding the fitted flow-through of our own revenue surprise (`m` 0.464, intercept
+$15.9M, 5 free parameters + a residual sd) cuts dollar-EBITDA MAE from **$58.1M to $33.8M in W2 (ratio 0.581,
NW(1) t −2.71, p 0.007, better in 9 of 10 quarters, sign p 0.011)** and from $65.3M to $43.1M in W1 (ratio 0.660,
t −1.39, p 0.16, better in **11 of 14**, sign p 0.029). Nothing else is a claim. The margin object's apparent win
(1.59 → 1.33 W1, 1.31 → 0.74 W2) is not significant (t −0.57 / −1.46) and, per the new counterfactual, is
delivered by halving the bias rather than by conditioning on dispersion. At h=1 there is no harvestable bias at
all. LIVE: **3Q26 adjusted EBITDA $2,390-2,412M** (11 Sep vintage $2,412M, backtest-consistent 6 Aug pre-guide
vintage $2,390M) against Street $2,361.5M, with the margin stated as **flat vs 3Q25's 50.09%** — not "+0.41pt",
which is the clip floor. Descriptive support that is still quotable: the Street has under-called the margin at 21
of 22 prints, the beat has decayed to +0.4-0.7pt, dispersion is at a record low (sd/mean 0.0085 against a 0.0497
recency-weighted reference, below the whole backtest range), and the post-guide 4Q26 consensus has under-called
the margin in 9 of the last 10 quarters by ~+1.1pt — a tilt, not a number.

**M7 `below-ebitda`.** An auditable bridge, not an edge. Interest income is the real result: MAE **$17.9M (W1,
n 14) / $10.5M (W2, n 10)** at h=0, 0.81x / 0.68x the *hardest* baseline, on one fitted parameter (yield beta
0.876). Share count is genuine against the drift baseline (0.40x / 0.67x); SBC and D&A are near-ties with it.
EPS is quoted two ways and never mixed: with the actual EBITDA in, W2 h=0 MAE **$0.066**; with a PIT EBITDA
baseline in, **$0.125**, 64% of which is the EBITDA input. Against the Street the bridge is 0.94x (W1) / 1.04x
(W2) — no alpha, by design. Quarterly FCF **fails** its pre-registered line (1.018 W1 / 0.927 W2 equal-weighted,
1.090 / 1.054 recency); FY FCF passes 3 of 4 years, biased +$399M high. All intervals, tax included, are **too
wide** — the under-coverage claim is withdrawn. Bridge parameters for 3Q26: interest income $184M, SBC $452M,
D&A $20.6M, interest expense $37M/q, ETR 18.0%, diluted shares ~591-592m; the Street's own 3Q26 EBITDA through
this bridge gives EPS $2.83 against the LSEG mean $2.85, so **5 Nov's EPS debate is an EBITDA debate**.

**The harness (10).** The PIT machinery, the seven baselines and the two-replay rule stand (WS21's R20/R22
cleared them). What it claimed too much is the pass rule. `survives_both_windows` is now documented as what it
is — a filter, with a ~30% null pass rate at this n — and the scorer carries the statistic that was missing:
`d_mean_*`, `t_nw1_*`, `p_nw1_*`, `k_better_*`, `n_cmp_*`, `p_sign_*` against `seasonal_naive` and `street`, plus
`n_min_both_windows`, `survives_both_windows_n8`, `survives_both_windows_sig` and `replays_present_fixed`. Every
one is a new column; no existing column changes value, so the orchestrator's re-score moves nothing that has
already been quoted. `tests.py` is 12/12. Applying the gates to the margin board at h=0 PIT: 52 both-flag cells
(26 object-spec pairs) become **14 cells / 7 pairs, six of them M5 and the seventh M3's `last_pin`** — which is
the same conclusion WS21 reached, now as a column WS23 can filter on.

## 3. Recommended weights for the WS23 combination

| object (spec) | weight | reason |
|---|---|---|
| M5 `street_plus_flowthrough` `rw_hl4` — **3Q26 adj EBITDA $** | **highest single weight on the 3Q26 dollar view** (I would anchor the point on it and let the others move it) | the only object in the run that beats the hardest baseline at p<0.05 (W2 t −2.71, p 0.007) and is corroborated in the other window by the sign test (11/14, p 0.029); h=0 only |
| M5 `dispersion_conditioned` `rw_hl4_med` — 3Q26 margin | **cut WS20's 0.60 to ~0.30-0.40, and re-point it** | lowest margin MAE on the board and I am not asking for it to be dropped — but its content is "street + half the recency-weighted bias" (2 parameters, not 5), its W1 paired test is p 0.57, and the backtest prefers **no floor at all** (see §4 Q1), which moves its LIVE 3Q26 from 50.12% to 49.89%. At 0.60 the blend is 60% a clipped constant. Re-run the blend on the floor-free variant and re-weight |
| M5 `street_plus_bias` (all specs) | **0** | fails W2 on $ (1.17) and applies a pre-2025 beat unconditionally; M5's own note says discard |
| M5 anything at h=1, and the `_fyalloc` 1Q27-4Q27 rows | **0** | every h=1 correction is worse than doing nothing; the `_fyalloc` rows borrow the failed h=1 estimate and are not backtested |
| M5 quantiles (any object) | **0** | cov80 = cov90 = 1.00 everywhere; CRPS worse than the raw Street |
| M7 `interest_income`, `share_count` (`rw`) | **1.0 — sole source** | no competing object in the run; both beat the hardest baseline in both windows on one parameter |
| M7 `sbc`, `da`, `tax` (`rw`) | **1.0 — sole source, with the caveat** | near-ties with the drift baseline; the ETR rule is right on the FY and wrong on any single quarter |
| M7 `eps` chain | **1.0 as a converter, 0 as a forecaster** | it converts whichever EBITDA the combination picks into EPS; it has no edge over the Street (0.94x / 1.04x) and its own error is 64% EBITDA input in W2 |
| M7 `fcf` quarterly | **0**; FY FCF **0.5** (quote as a range) | the quarterly pass line failed outright; the FY leg passed 3 of 4 years but is biased +$399M high |
| harness baselines (`street`, `seasonal_naive`, `q_guide_implied`) | **0 as forecasters — they are the comparison columns** | `street` is the hardest margin baseline (1.59 / 1.31pp) and the number the 5 Nov card is traded against |
| selection rule for the combination | use `survives_both_windows_sig` (or `_n8` plus the quoted sign test), **not** `survives_both_windows` | at n 14/10 the raw flag has a ~30% null pass rate (R01) |

## 4. Answers to the WS20 scoreboard's open questions (§11 of `20_scoreboard.md`)

New evidence for this section: `M5_discussion_clip_sensitivity_live.csv`,
`M5_discussion_clip_sensitivity_backtest.csv`, `M5_discussion_regime_by_quarter.csv`,
`M7_discussion_blend_eps.csv` (all written by the two `discussion_checks.py` scripts, exit 0).

### Q1 to M5 — what does `dispersion_conditioned` print at floor 0.3 and 0.7, and how much of the beat is the clip?

The object is `street + b x clip(disp/disp_ref, floor, 2.0)`, so the floor is a straight lever on the beat.
Rebuilt at every floor (the rebuild reproduces the registered floor-0.5 points to 0.0 exactly — the
`max_abs_diff_vs_registered` column). LIVE 3Q26, `b_pt` +1.057 (`rw_hl4`) / +0.684 (`rw_hl4_med`), raw ratio
**0.171** (PIT reference; 0.084 against the full-sample reference, which is WS21's number):

| floor | `rw_hl4` margin | beat vs Street | `rw_hl4_med` margin (**the spec WS23 weights 60%**) | beat | `rw_hl4` EBITDA $m |
|---|---|---|---|---|---|
| none (raw 0.171) | **49.96%** | +0.18pp | **49.89%** | +0.12pp | 2,387 |
| 0.3 | 50.09% | +0.32pp | 49.98% | +0.21pp | 2,406 |
| **0.5 (registered)** | **50.30%** | **+0.53pp** | **50.12%** | **+0.34pp** | **2,436** |
| 0.7 | 50.52% | +0.74pp | 50.25% | +0.48pp | 2,466 |
| 1.0 (no conditioning) | 50.83% | +1.06pp | 50.46% | +0.68pp | 2,510 |

**Roughly two-thirds of the beat is the clip.** Uncapped, the four-spec composite is ~49.97% (+0.19pp) against
the registered 50.19% (+0.41pp) — the floor supplies ~0.22pp of the 0.41pp, and the flow-through member is the
only one unaffected. **And the backtest does not support the 0.5 floor.** Re-scoring h=0 at each floor:

| spec / target | floor 0.0 | 0.3 | 0.5 | 0.7 | 1.0 | Street |
|---|---|---|---|---|---|---|
| `rw_hl4` margin W1 (n 14) | **1.326** | 1.328 | 1.330 | 1.388 | 1.547 | 1.592 |
| `rw_hl4` margin W2 (n 10) | **0.743** | 0.747 | 0.743 | 0.855 | 1.114 | 1.311 |
| `rw_hl4` $ W1 | **50.7** | 50.9 | 52.9 | 54.3 | 60.0 | 65.3 |
| `rw_hl4` $ W2 | **46.2** | 46.5 | 50.3 | 54.7 | 66.3 | 58.1 |
| `rw_hl4_med` $ W2 | **45.2** | 45.5 | 48.8 | 52.5 | 64.4 | 58.1 |

Removing the floor entirely is **equal-or-better in all ten cells** (margin flat, dollars 4-8% better), and it
takes the LIVE call to 49.9-50.0%, i.e. essentially the Street and **below** the management ceiling. So the
answer to the question behind the question: the clip is not a defended parameter, it is the thing producing the
disagreement with the Street, and the backtest prefers its removal. **Recommendation to WS23: do not carry the
+0.41pp. Either drop the floor (LIVE 3Q26 49.96% / $2,387M) or state the object as "street + half the
recency-weighted bias" and own the constant.** Either way the 3Q26 margin point lands at or just below the
50.09% ceiling, which removes the R11 inconsistency at the same time.

### Q2 to M5 — is 3Q26 the 1H23 regime or the 1H25 regime, and what observable settles it before 5 Nov?

Quarter by quarter (`M5_discussion_regime_by_quarter.csv`, W1, `rw_hl4`, h=0; `street_err` = Street − actual,
so negative means the Street was low):

| quarter | Street err | M5 err | M5 helped? | dispersion at the vintage | `b_pt` used |
|---|---|---|---|---|---|
| 2023Q1 | −1.00 | **+3.75** | no, −2.75 | 0.189 | **4.81** |
| 2023Q2 | **+1.69** | +3.62 | no, −1.93 | 0.054 | 3.86 |
| 2023Q3 | −2.74 | −1.37 | yes | 0.049 | 2.74 |
| 2024Q1 | −4.06 | +0.03 | yes, +4.04 | 0.212 | 2.65 |
| 2025Q1 | −1.95 | +1.04 | yes | 0.226 | 1.55 |
| 2025Q2 | −2.49 | −1.73 | yes | 0.040 | 1.53 |
| 2025Q3 | −0.58 | +0.22 | yes | 0.025 | 1.60 |
| 2026Q1 | −0.85 | −0.15 | yes | 0.044 | 1.21 |
| 2026Q2 | −1.03 | −0.47 | yes | 0.020 | 1.11 |

The 1H23 failure is **mechanical, not regime-mystical**: the bias pool still held the 2021-22 beats, so `b_pt`
was **4.81pp** against a Street error of −1.00pp, and in 2023Q2 the Street was *above* the actual while M5 added
more. The correction has helped in **8 of the last 10** quarters. Today `b_pt` is **1.06pp** — a fifth of the
2023Q1 value — and the multiplier is clipped to 0.5, so the most a wrong-signed Street error can cost is
**~0.5pp**, against 2.75pp in 2023Q1. That is the real answer: at today's parameter values the 1H23 regime is
not reachable, which is also why the object cannot be worth a 60% weight on its margin point.

Three observables before 5 Nov, in order of power: **(1) dispersion.** sd/mean is 0.0085 today against 0.189 at
the 2023-02 vintage and 0.054 at 2023-05; a widening above ~0.03 into the print is the 2023 signature and says
cut the correction. **(2) The shape of the revision.** The 2023Q2 failure was an *upward EBITDA revision with no
revenue revision* — the Street chasing margin. Track LSEG EBITDA mean vs revenue mean weekly; if EBITDA rises
without revenue, M5's bias is already being priced and must not be added twice. **(3) Our own revenue nowcast.**
The flow-through object is arithmetic: beat = 0.464 x (our revenue − Street revenue) + $16M = 0.464 x
(4,804 − 4,744) + 16 = **+$44M**. If the Q3 nowcast converges to the Street's $4,744M the beat collapses to
$16M. **The 3Q26 EBITDA call is a revenue call, not a margin call** — which is the same statement as R23.

### Q10 to M7 — withdraw the FCF rows?

**Yes for the quarterly rows, no for the annual.** `fcf_musd` (1.018x naive W1 / 0.927x W2 equal-weighted,
1.090 / 1.054 recency), `cfo_musd` and `fcf_margin_pct` are withdrawn from the quotable set — they fail the
pre-registered line and fail it on the recency weighting the pitch uses. The only FCF claim the memo should
make is the **annual** one: the February-vintage FY forecast beat the prior-FY-actual naive in **3 of 4** years
(FY22 +467 vs −1,117; FY23 +742 vs −432, the loss; FY24 +348 vs −647; FY25 +40 vs −129), with a **+$399M mean
high bias** that must be quoted with it. FY26 $4.91-5.13bn against Street $4.92bn is a range, not a point, and
capex sits $5M/quarter below the Street's, worth ~$20M of FY26 FCF. Keep the registry rows (they are correctly
registered and the failure is the result); mark them not-quotable.

### Q11 to M7 — feed the recommended blend into the bridge instead of the harness baseline: what moves?

The waterfall is linear in EBITDA, so this is exact: **d(EPS)/d(EBITDA) = (1 − ETR) / diluted shares =
0.82 / 591.7 = $0.001386 per $M**, i.e. **$0.0666 of EPS per 1pp of 3Q26 margin** on revenue $4,804M.

| EBITDA input | 3Q26 margin | 3Q26 EBITDA | 3Q26 EPS |
|---|---|---|---|
| M1 `driver-lines` (what M7's LIVE waterfall carries) | 51.76% | $2,486M | **$3.000** |
| **WS23 recommended blend (50.39%)** | 50.39% | $2,421M | **$2.909** |
| Street (LSEG 11 Sep) | 49.16%* | $2,361.5M | $2.827 |

\* on the team's $4,804M revenue, not Street revenue. **So the blend costs $0.09 of 3Q26 EPS versus M1 and
leaves us $0.06 above the Street's $2.845** — a much easier number to defend than $3.00. Everything below the
line is unchanged (D&A $20.6M, SBC $452M, interest income $184M, interest expense $37M, ETR 18.0%, shares
591.7m).

**Does the interval widen? No — properly propagated it gets narrower than the registered one.** M7's registered
3Q26 EPS band (q10-q90 $2.73-3.09, ±$0.18) is bridge-only and over-wide (cov80 0.97). Propagating instead:
bridge sd from the realised W2 h=0 error with EBITDA known ($0.066 MAE -> sd $0.083) combined with the EBITDA
sd implied by the blend's margin error (0.74pp MAE -> 0.93pp sd -> $0.062 of EPS) gives sd **$0.103** and an
80% band of **$2.78-3.04**. Quote that, and say the two sources are roughly equal in size — the bridge is not
the small term any more once the EBITDA input is a blend rather than an oracle.

### Q13 (addressed to WS21, but it is a harness change) — an `is_oracle` column instead of a naming convention

**Done.** `harness_margin/significance.py` now carries `ORACLE_MARKERS = ("revknown", "nightsknown",
"ebitda_known")` and `mark_oracle()`, and the scorer writes a boolean **`is_oracle`** column; it flags **756 of
6,768** scored cells across 14 (method, object, spec) combinations — the six WS21 listed, plus their `lines`
twins, plus M7's four `ebitda_known` specs. `scoreboard_significance.csv` already carries it, so WS20/23 can
filter tonight without waiting for the re-score. It is a marker column, not a filter: the rows stay registered
and scored, which is what the two-replay discipline wants.

### Coordinator's extra ask 1 — the interval recipe for WS23

Registry quantiles are unusable board-wide (cov80 0.91-1.00; M5's are exactly 1.00), so build the band from the
**combination's own leave-future-out errors**, which `20_combination_backtest.csv` already contains (n=10,
2024Q1-2026Q2, expanding window). Recipe, in order:

1. **Split-conformal on the blend's |errors|.** At n=10, alpha=0.2 the harness's own `attainable_coverage` gives
   k = ceil(11 x 0.8) = 9, so qhat = the **9th smallest of the 10** absolute errors = **1.584pp**, and the true
   coverage sits in **[0.818, 0.909]** — label it "~82-91%", never "80%".
2. **Cross-check with the Gaussian-from-MAE width:** 1.2816 x 1.2533 x 0.992 = **1.594pp**. The two routes agree
   to 0.01pp, which is the reason to believe the width.
3. **Centre it on the bias.** The blend runs **+0.155pp high** over the ten quarters (+0.37 first half, −0.06
   second). Either subtract the bias from the point or use the empirical signed 10-90, **[−1.31, +1.49]pp**.
4. **3Q26 therefore: 50.39% ± 1.58pp -> [48.8%, 52.0%]** (bias-corrected centre 50.24%), and in dollars at
   $4,804M of revenue, ±$76M -> **[$2,345M, $2,497M]**. Say out loud what that means: **the 80% band contains
   the Street**, so the +0.4pp point disagreement is a fifth of the band and the memo should sell the direction
   and the dollar flow-through, not the decimal.
5. **Do not add the revenue-path spread into the margin band** (they are near-independent here: M5's incremental
   margin on a revenue surprise is 0.46 against a level margin of 0.50, so revenue moves dollars, not the
   ratio); add it only when converting to dollars, using bridge v3's base/bear/bull $4,755-4,878M.
6. Carry the harness's exchangeability caveat verbatim — expanding-window refits over a regime break are not
   exchangeable, so this is a descriptive band, not a guarantee.
7. For EPS, chain step 4 through M7's slope ($0.001386/$M) as in Q11 rather than using M7's own quantiles.

### Coordinator's extra ask 2 — should the harness carry a second revenue leg?

**Yes, but LIVE-only, and as a new leg beside the existing one — never as a change to `revenue_forecast_pit`.**
Every registered backtest row and both replays were computed against the frozen guide-cushion / naive leg;
re-pointing it would invalidate all 32 registry files and make the two-replay rule meaningless. What is actually
wrong is only the LIVE column: the naive leg gives 4Q26 **$3,237M** against bridge v3's $3,178M (+$59M) and
Street's $3,162M (+$75M), and FY27 $16,709M against LSEG $15,819M (**+5.6%**). At a ~33% incremental rate the
4Q26 wedge is **$20-25M of EBITDA** on every method's dollar row, and on FY27 it is the difference between a
33.31% and a 35.18% method margin.

Concretely: add `revenue_leg_live.csv` with a `leg` column (`baseline_pit` | `bridge_v3`) and have every LIVE
table publish margin x both legs, with `bridge_v3` (3Q26 $4,804M, 4Q26 $3,178M, FY27 from WS06 v2b) as the
quoted one. ~30 lines in `baselines.py` + `build_live.py`, no scored row touched. I have **not** written it
tonight: it must not run concurrently with another agent's `run.py`/`score.py`, and it belongs with the
orchestrator's single re-score. Until it exists, the standing rule for WS23 is the one WS20 already wrote —
**quote 4Q26 in margin terms and convert with bridge v3 by hand.**

## 5. Files changed by this group

New: `analysis/src/margin_build/10_harness_margin/harness_margin/significance.py`,
`analysis/src/margin_build/10_harness_margin/significance_check.py`,
`analysis/src/margin_build/M5_street_bias/discussion_checks.py`,
`analysis/src/margin_build/M7_below_ebitda/discussion_checks.py`,
`data/processed/margin_build/10_harness_margin/scoreboard_significance.csv`,
`data/processed/margin_build/M5_street_bias/M5_discussion_{paired_tests,clip_audit,counterfactual,
clip_sensitivity_live,clip_sensitivity_backtest,regime_by_quarter}.csv` + `M5_discussion_summary.json`,
`data/processed/margin_build/M7_below_ebitda/M7_discussion_{coverage_band,eps_decomp,blend_eps}.csv` +
`M7_discussion_summary.json`, this file.
Edited (additively): `analysis/src/margin_build/10_harness_margin/harness_margin/score.py` (new columns and three
new markdown columns only), `analysis/src/margin_build/10_harness_margin/tests.py` (12th test),
`analysis/src/margin_build/10_harness_margin/README.md` (§6.1),
`docs/margin-build/notes/{M5_street_bias,M7_below_ebitda,10_harness_margin}.md` (Discussion response sections).
No registry file, no existing processed CSV and no number already quoted was modified; M5 and M7 were **not**
re-run because nothing they produce changed, and `score.py` was not run.
