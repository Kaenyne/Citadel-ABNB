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
