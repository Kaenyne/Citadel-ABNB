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
