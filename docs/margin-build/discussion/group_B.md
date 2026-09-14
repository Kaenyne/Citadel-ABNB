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
