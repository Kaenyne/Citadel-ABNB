# Critique C-M1 — MIXSTATE (chain-linked conditional-index state space)

Adversarial review. Author: IC-side reviewer (econometrics). Date 11 Sep 2026. Repo `main @ a5d6dbb`.
Standard applied: the proposal survives only where I failed to break it. Every number below marked
**[verified]** I recomputed in this session from the cited file; the commands are one-liners over pandas.

**Verdict: ADOPT WITH FIXES — but not as a state space.** The identifying asset is real and is the best
thing in the proposal. The estimator built on top of it is over-parameterised by roughly two orders of
magnitude relative to its own claim, its headline "no take-rate plug" claim is numerically false, and its
single most persuasive exhibit (the 24-cell free OOS test) does not exist in the data.

---

## 0. What I verified before attacking

| Claim | Result |
|---|---|
| `10_xbrl_revenue_geography.csv` yields 72 exact quarterly regional revenue cells 1Q22-2Q26 | **TRUE [verified]**. 56 filed three-month cells (14 quarters × 4 regions; Q1/Q2/Q3 only, 2022Q1-2026Q2), zero conflicting duplicates, plus 16 Q4 back-outs |
| Q4 back-out reproduces 4Q23 $2,218M / 4Q24 $2,480M / 4Q25 $2,778M | **TRUE [verified]** to $1M, and 4Q22 = $1,902M as a fourth check |
| 28 genuine `basis=='bucket'` nights cells, 4Q24-2Q26 | **TRUE [verified]** (7 quarters × 4 regions) |
| 14 `basis=='derived…'` cells to be excluded | Count TRUE, **date range FALSE**: they run 4Q22-3Q24 (NA 8 cells, EMEA 6), not "1Q24-3Q24" as §2.2 states |
| 38 reported + 30 ex-FX regional ADR y/y, all integers | **TRUE [verified]**; NA ex-FX ends 1Q25, APAC ends 1Q26 as claimed |
| Törnqvist geo drag −1.06pp (2024) / −1.48pp (2025); within +2.71 / +4.46pp | **TRUE [verified]** on `adr/01_regional_annual.csv` (nights-weighted Törnqvist) |
| FY25 take-rate fall is ~95% NA | **TRUE [verified]**: NA 13.274→13.238→12.895%, EMEA −5.6bp, LatAm −8.3bp, APAC +5.0bp 2024→25; blended −16.4bp, NA share-weighted contribution −15.1bp = 92% |
| `06_quote_line_items.csv` is a 1.71M-quote hedonic panel | **FALSE**. 76 data rows of `city, dump_date, quotes, li_*` fee-line-item **counts**. No price, capacity, bedrooms or LOS field. §2.6/§3/§7-D4 cite it four times as the source of "ONE joint hedonic" |
| 22 further `basis=='numeric'` regional nights cells exist (3Q22-3Q24 LatAm/APAC etc.) | **TRUE [verified]** — and the proposal never mentions them |

So the foundation stone is genuine. Everything I break below is built on top of it.

---

## 1. Identification — score 4/10

**The take-rate plug is not removed. It is renamed and multiplied by four, and I can prove it numerically.**

§2.7 row 1 and the JSON one-liner both assert "There is NO take-rate forecast and NO FX wedge anywhere in
the model", killed by the φ-kernel. But §2.1 defines `τ_{r,t} = τ_{r,t-1} + ε_τ` (slow RW, σ_τ tiny) and
the author's own Stan block (§6) declares `matrix[T,R] tau` — 120 free parameters where the incumbent had
one carry. The claim and the code contradict each other on the same page.

Worse, the arithmetic defence fails. I applied the proposal's own prior kernel φ = (0.05, 0.62, 0.30, 0.03)
to disclosed quarterly GBV and solved for the residual conversion `Rev_t / Σφ_k GBV_{t-k}` **[verified]**:

| | 1Q | 2Q | 3Q | 4Q |
|---|---|---|---|---|
| implied fee, mean of last 12q | **12.39%** | **13.69%** | **17.45%** | **12.08%** |
| printed take rate | 9.2% | 13.1% | 18.3% | 14.0% |

The φ-convolution removes only about 40% of the seasonality (printed range 9.1pp → residual range 5.4pp,
12.01-17.62%). The residual is *still* a 5.4pp seasonal swing — 43% of its own level. With `σ_τ tiny` on a
random walk and 72 regional revenue cells entered at `σ = 1e-6`, the model is infeasible unless `τ_{r,t}`
swings 12.4 → 17.5 → 12.1 every year. That is a **quarterly seasonal take rate**, i.e. exactly the plug
§2.7 claims to have deleted, now estimated four times over with no mechanism. The honest specification is
`fee_{r,q(t)}` with four quarter-specific levels (which the data support beautifully — 3Q 17.62/17.37/17.36,
4Q 12.01/12.16/12.08 **[verified]**, matching the repo's measured 17.4/17.1/17.2 and 12.0/12.1/12.0).
That is a fine model. It is not the model that was pitched, and the pitch line "no take-rate forecast
exists" must be withdrawn before a judge finds this.

**The parameter count is wrong by ~70×.** §4 and §8 claim "~16 estimated parameters… 6-9 observations per
parameter". Counting the author's own `parameters` block at T = 30 quarters (3Q20-4Q27), R = 4:
`lnNhome` 30, `u` 90, `g` 120, `c` 120, `p` 30, `q` 120, `msize` 120, `mlos` 120, `msub` 120,
`lnNhotel`/`lnSexp`/`lnSsvc` 90, `tau` 120, plus ~16 hyperparameters ≈ **1,100 free quantities**. Against
them: 72 independent exact totals (nights/GBV/revenue; ADR is not independent), 72 regional revenue cells,
28 bucket intervals, 68 ADR integer intervals, 24 annual nights intervals ≈ **264 informative data points**.
`msize`/`mlos` do not add information — 120 states each with 120 one-to-one normal "measurements" is a
prior, not data. The model is identified **by its priors**, which is legitimate Bayesian practice but is
the opposite of what §8's rebuttal to "you fit the answer" says.

**The hidden plug, located.** `q[t,r] ~ N(0, σ_q)` and `msub[t,r] ~ N(0, 0.01)` are two T×R matrices
entering the *same* equation additively with zero-mean priors and **no observation that distinguishes
them**. They are exactly collinear. Their sum is (loosely) identified; the split is 100% a ratio of two
prior variances the author chose, one of them fixed at 0.01 by hand. §2.6 confesses that `P` and `M^sub`
are jointly unidentified and promises a 2-d credible region — good — but it does not confess that
(`q`, `M^sub`) is *also* exactly collinear, that `p` is collinear with the average of `q` across regions,
and that in the historical replay `msize` and `mlos` are prior-only too (§4 says so explicitly: market
panels excluded entirely). So in the backtest **five of the six named ADR terms are mutually
unidentified** and their published "credible intervals" are prior echoes. The memo's headline exhibit —
the decomposition waterfall with a credible interval on every named term — would be, over most of its
width, a picture of the author's priors. That is assumption dressed as estimation, and it is the term
(+3.6pp price/sub-regional residual) that drives the FY27 ADR call.

**The concrete double count the construction does NOT kill: FX × price, via pass-through.**
`10_regional_fx_passthrough.csv` **[verified]** gives slopes of disclosed reported-minus-ex-FX ADR gap on
the team's own regional basket: EMEA 1.043 (r 0.987, n 10), APAC 0.860 (r 0.972, n 5), **LatAm 0.623**
(r 0.996, n 7, basket range 27.1pp), NA not identified. MIXSTATE translates at unit pass-through:
`lna[t,r] = lna[t-4,r] + p + q + msize + mlos + msub + (lnXB[t,r] − lnXB[t-4,r])`. Take LatAm, where the
basket moved +11.4% y/y in 2Q26. MIXSTATE removes 11.4pp as translation; Airbnb's own disclosure removes
only 0.623 × 11.4 = 7.1pp. The 4.3pp difference lands in `p`/`q`/`msub` — labelled "like-for-like price"
and "sub-regional mix". Because `p` is a *global* random walk with no mean reversion, a LatAm currency move
is then propagated into the FY27 price forecast **for all four regions**. FX is counted once as
translation and a second time, with the wrong sign and global reach, as price. This is the same
procyclicality defect (audit §3.2) the proposal claims to have killed, re-entering through a door the
proposal opened itself by citing the pass-through file and then not using it. And it is not cosmetic: it
directly contaminates the residual that the FY27-below-Street call rests on. A pass-through parameter
`θ_r` on the FX term, with the measured 0.62/0.86/1.04 as a prior, is the minimum fix; it also resolves
the standing conflict between a unit-pass-through `X^B` and the 30 ex-FX ADR integer observations, which
will otherwise fight each other inside a likelihood where both are near-exact.

**Second concrete overlap: seats.** §2.3's identity `N = Σ n^home + n^hotel + s^exp + s^svc` is true and
vacuous. Total `N` is exact, so `Σ n^home` is exactly `N` minus three latent states observed only through
phrases ("single-digit % of nights", "seats immaterial"). GBV is exact too, and `p^exp`/`p^svc` are
undisclosed constants. So a 2M over-estimate of Experiences seats removes 2M from home nights and pushes
home ADR up to hold GBV, which shifts the geo-mix and price terms. The audit's $88M three-way
inconsistency is replaced by *one* consistent treatment whose inputs are unidentified. That is a real
improvement in coherence. It is not a resolution, and the memo must not claim the $88M is "resolved".

**Internal inconsistency between the Törnqvist table and the model.** §2.0 level 2 is "product line within
region" (`M^prod`), justified by the 13 May 2025 denominator change. It does not appear in the state
equation (§2.1) or in the Stan block (§6): hotel and seats are *global* states with global prices, not a
within-region partition. The six-term "strictly refining partitions" story that carries the
no-double-counting argument is therefore not the object being estimated.

---

## 2. Point-in-time safety and backtest validity — score 4/10

The **data-side** discipline is the best I have seen in this repo: `filed`-dated XBRL, `print_date`-filtered
guidance, FX from forwards not realised spot, Eurostat by publication lag, the explicit exclusion of the
14 derived rows, and — genuinely creditable — the refusal to use the Inside Airbnb panel in the historical
replay at all on the strength of `08_altdata_backtests.py:248` (**[verified]**: "the retrospective scope
flag uses LATER scrapes, so a frozen replay may only use the trailing-window judgement"). Most proposers
would have quietly used it.

**The leak is on the prior side, and in this model that is the whole game.** The PIT harness filters
inputs by `knowable_from`. It does not filter the *specification*, and the specification is where the
identification lives. Every one of these was chosen with full-sample knowledge:
- `σ_q ~ half-N(0, 0.01)` — justified in §2.1 by a **7 Sep 2026** research note ("regional pricing is one
  number now, not four"). At a 2Q23 guide date nobody knew that.
- `φ ~ Dirichlet(2·(0.05, 0.62, 0.30, 0.03))` — centred on the ⅔/⅓ fit computed on 3Q23-3Q25
  (`h2_bridge_gbv_lag_conversion.csv`, 6 rows **[verified]**). Used to re-fit 2022 guide dates.
- `τ_{r,0} ~ N(2025 10-K regional take, 0.3pp²)` — a 2025 number seeded into a 2022 replay.
- `c̄ ~ N(0.08, 0.05²)` — platform nights growth known ex post.
- The bucket/derived exclusion rule, the region set, the lap structure of `d_t`.

In an over-parameterised model whose posterior is driven by priors, priors specified from the full sample
**are** look-ahead. The 19-date PIT histogram will look well-calibrated for exactly that reason, and the
author will have no way to tell. Fix: freeze a prior-elicitation rule that depends only on data available
at T (e.g. φ from trailing conversions through T−1), and report both replays.

**The free OOS test does not exist as specified.** §4: "fit on the buckets alone, form the 80% interval for
annual regional nights, score against the 10-K — 24 clean out-of-sample checks (6 years × 4 regions)…
19-21/24 target, 14/24 rejects it. The single most persuasive exhibit available." Bucket disclosures exist
only 4Q24-2Q26 **[verified]**. Full-year bucket coverage therefore exists for **2025 only**: 4 cells. 2024
has one bucket quarter (4Q24) and three derived NA/EMEA quarters the proposal itself excludes. 2020-2022
have none. Admitting the 22 `numeric` cells (which the proposal never discusses) buys LatAm/APAC 2023-24 —
at most 8-10 cells, and only by abandoning the disclosure-purity rule the same section insists on.
With n = 4, the probability that all four fall inside a correctly-calibrated 80% interval is 0.41; the
test cannot distinguish 19/24 from 14/24 because neither outcome is reachable. Worse, "buckets alone" is
ambiguous: if the 72 exact regional revenue cells and the 68 regional ADR integers stay in the fit, the
regional nights are nearly pinned by `n = Rev/(τ·ADR)` and the test measures the accounting identity, not
the buckets; if they are dropped, the model under test is not the model being pitched. Either way the
headline exhibit is compromised. It is recoverable as an honest **4-cell 2025 check plus a leave-one-year-out
on the 56 filed quarterly cells**, but it must be re-labelled and de-headlined.

**Not flagged by the proposal:** the ADR ex-FX integer readings (`10_regional_adr_fx.csv`) are letter-sourced
and, per audit §4.2(c), the letters round "less than 1%" to a coded 0.5. Entering these as symmetric
[x−0.5, x+0.5] intervals is right for genuine integers but wrong for coded qualitative phrases; the
interval-observation file must carry a `phrase_kind` flag or it will silently assert precision where the
letter asserted a bound.

---

## 3. Statistical power and overfitting — score 3/10

~1,100 latent quantities, ~264 informative observations, 24 company-quarters, and 7 quarters of the only
quarterly regional nights signal there is. §8's rebuttal — "roughly 190 informative observations, 120 of
which are exact constraints that reduce the feasible set rather than consume degrees of freedom" — is a
category error dressed as a defence. Exact constraints reduce dimension by their *count*, not by their
importance: 72 exact regional revenue cells remove 72 dimensions from a 1,100-dimensional space. What
remains is ~800 dimensions of prior.

Detectable effect size: the FY27 call turns on ~1.1pp of ADR (≈$175M). The regional ADR observations are
±0.5pp intervals, present for 68 of 4 × 18 = 72 possible region-quarters but with NA — 30% of nights —
dark on ex-FX after 1Q25. The buckets are 2-3pp wide on 7 quarters. There is no configuration of this data
that resolves a 1.1pp blended-ADR question to better than roughly ±1pp, which is the width of the answer.
The proposal half-admits this in §2.5 ("the posterior on the split widens while the product stays tight")
and then hands the memo a point estimate of $15.5-15.7bn anyway.

On the 3,500-test record: the proposal's argument (§4, "why the earlier negatives do not condemn it") is
the strongest part of the document and it is mostly right. Information as constraint ≠ information as
regressor; market-grain coefficients ≠ aggregate-grain regressors; a shrunk zero-centred covariate with a
published posterior is a categorically different object from a walk-forward horse race at n = 12. I tried
to break this and could not. **Survived.** But one failed design *is* quietly repeated: `λ_r` and `δ_r`
(8 parameters) are fitted on 96 region-quarter cells that are themselves latent and mostly prior-driven.
A posterior on `λ` that sits on zero will be reported as "Eurostat earns nothing" when the honest reading
is "this design cannot tell". The contraction table must report prior-to-posterior sd ratio per parameter,
and any parameter that contracts less than ~20% should be struck from the exhibit, not published as a
result.

---

## 4. Tradeability over 3-12 months — score 5/10

The trade identified is the right one and is the best in the repo: `P(4Q26 guide midpoint < $3,200M)`,
executed on the 9/9 negative-20-day-drift rule at next-open entry. **But MIXSTATE does not produce it.**
The stated mechanism (§5b) is purely arithmetic: 4Q26 revenue FX is ~84% determined at −0.4pp against
+3.0pp guided for 3Q26, a −3.4pp step. That number comes from `29_q4-fy27-bridge.md` and
`05_fx_schedule.csv`, not from a regional state space. The repo already has two below-Street 4Q26 numbers
($3,111M from the bridge, $3,145M from the driver model) against Street $3,200M **[verified,
`04_current_consensus.csv`]**. A PM will ask: what does 1,100 latent states change about the trade?
Honest answer: nothing about the direction, only the error bar — and the error bar is prior-driven.

Two further tradeability problems the proposal does not raise:
1. **The Street number is not frozen.** Zacks 4Q26 $3,200M with 10 estimates, range $3,050-3,700M
   **[verified]** — a $650M spread, i.e. the "guide below Street" trigger is within the dispersion. On
   5 Nov the guide is compared to a consensus that will have moved on the Q3 print delivered 30 seconds
   earlier. The rule's 9 historical observations were scored against a contemporaneous consensus; the
   pitch must state which vendor's number and which timestamp defines the trigger, or the trade is not
   executable as claimed.
2. **n = 9 and a single event.** The pitch is one draw from a 9-observation base rate. Position sizing and
   the option overlay (the Bloomberg IV surface in `Theo Data` is unused here) matter more than the third
   decimal of a posterior.

FY27 vs Street is the weaker leg and the proposal knows it (§8, "you are just going to land on the
Street"). Two of its three channels are genuinely differentiated and **[verified]** — the deepening geo
drag (−1.06 → −1.48pp) and the ~95%-NA take-rate decline. Those are exhibits a Citadel judge will
respect. Neither requires a state space; both are ten lines of pandas on `adr/01_regional_annual.csv`.

---

## 5. Buildability in three weeks — score 3/10

Against 3-4 undergraduates, a 2 Oct prelim, a 2-page memo and five other lenses:

- **The joint hedonic cannot be run on the cited file.** `06_quote_line_items.csv` is 76 rows of
  city × dump-date fee-line-item counts (`quotes, li_nightly_subtotal, field_taxes, li_cleaning_fee`…)
  **[verified]**. There is no capacity, bedroom, LOS or price column. The real hedonic lives in
  `06_wtp_hedonic_coefs.csv` (n = 951,134, 47 dumps, `price_basis = listed_nightly` **[verified]**) and its
  microdata is in the 9.9 GB raw Inside Airbnb dumps in the sibling folder — and per audit §4.2(e) Inside
  Airbnb **dropped listed prices from late-2025 dumps**, so a current-vintage joint hedonic on capacity ×
  bedrooms × LOS × market FE is not a D4 afternoon; it is a multi-day rebuild against a truncated price
  field. The §2.7 row "size × party × LOS killed by ONE joint hedonic" is not currently executable.
- **Stan geometry.** ~1,100 parameters with 96 constraints at `σ = 1e-6` is a near-degenerate manifold.
  Hard constraints should be solved analytically (reduce the state, do not penalise it); imposing them
  with a tiny sigma is the standard way to make NUTS diverge. Undergraduates debugging divergent
  transitions in week 2 with a 2 Oct deadline is a schedule risk, not a modelling risk.
- **The Week-1 D3 gate cannot fail.** "The MAP fit must place all 24 annual regional nights cells inside
  ±0.5M while reproducing every quarterly total exactly." With softmax shares and ~1,100 free parameters
  against 24 intervals, feasibility is guaranteed for essentially any data. A gate that cannot fail is not
  a gate; the informative version is a *minimum-norm* feasibility check that reports how much prior mass
  had to be spent.
- The cut list is sensible and correctly ordered, and the "cannot cut" four are the right four.

**Minimum viable version, which I would build instead and which keeps ~80% of the edge:**
1. `01_exact_regional_revenue.csv` — the 72-cell filed-dated panel (D1, real, verified, genuinely unused).
2. A constrained reconciliation in `scipy`: log levels, softmax shares, `Σ n_r = N` exact, buckets and
   ADR integers as hinge intervals, annual 10-K cells as equalities, **quarter-specific regional
   conversion `fee_{r,q}`** (16 parameters) in place of `τ_{r,t}` (120), FX with a measured pass-through
   `θ_r`. ~60 parameters, ~264 observations. Runs in seconds; leave-one-year-out is cheap.
3. Geo mix and seats as outputs of that identity — this alone closes the audit's $175M and $88M gaps.
4. Conformal intervals from the 19-date replay for uncertainty; no MCMC, no "Monte Carlo" fight with the
   judges at all.
That is three days of work, it is defensible line by line, and it produces every exhibit that matters
except the joint posterior — which, as shown in §1, would have been mostly prior anyway.

---

## 6. Defensibility in a 2-page memo and 10-minute hostile Q&A — score 5/10

The one-sentence version that works: *"Airbnb's regional revenue is disclosed exactly every quarter and
nobody uses it; forced through the accounting identity it says geography is draining blended ADR faster
every year (−1.06pp in 2024, −1.48pp in 2025) and that the FY25 take-rate decline is 95% North American —
so the Street's FY27 ADR is too high, and 4Q26's guide steps down 3.4 points on FX arithmetic alone."*
That sentence is defensible, verified, and does not require the word "posterior".

The §8 hostile-judge script is unusually good — the MCMC-vs-Monte-Carlo distinction is correct, the
"bands are marketing" rebuttal with the ±3pp widening test is exactly right, and the regime-break answer
is honest. But the first question a Citadel PM asks is **"what is your FY27 number and what is the single
assumption it turns on?"**, and the second, from anyone who reads §6, is **"you told me on page 3 there is
no take-rate forecast; your own code declares `matrix[T,R] tau`. Which is it?"** The proposal has no answer
to the second, and my Q3/Q4 conversion table above makes it worse, not better. The third question —
"show me the posterior of `q` separately from `msub`" — also has no answer.

Two-page memo feasibility: a decomposition waterfall with eleven named terms, a 2-d credible region, a
PIT histogram, a 24-cell coverage table, a reconciliation table and an ordering-reversal spread is four
pages of exhibits for a two-page memo. Pick two: the waterfall and the reconciliation table.

---

## 7. Refutation attempts, logged

| # | Claim | Attack | Outcome |
|---|---|---|---|
| 1 | "72 exact regional revenue cells, Q4 exactly recoverable, unused in the repo" | Rebuilt from `10_xbrl_revenue_geography.csv`: counted 56 filed three-month cells, zero conflicting duplicates, backed out Q4 against `adr/01_regional_annual.csv` | **Survived** — reproduces 4Q22 $1,902M, 4Q23 $2,218M, 4Q24 $2,480M, 4Q25 $2,778M to $1M |
| 2 | "The φ-kernel replaces the take rate; there is no take-rate forecast" | Applied the proposal's own φ=(0.05,0.62,0.30,0.03) to disclosed GBV and solved the residual conversion | **Refuted** — residual is still seasonal 12.39/13.69/17.45/12.08% by quarter, a 5.4pp swing; `τ_{r,t}` must carry it, and §6 declares 120 such parameters |
| 3 | "~16 estimated parameters, 6-9 observations each" | Counted the author's own `parameters` block at T=30, R=4 | **Refuted** — ~1,100 free quantities against ~264 informative observations; identification is by prior |
| 4 | "Overlap is killed by construction; only (P, M^sub) is unidentified" | Inspected the ADR state equation for collinear terms | **Refuted** — `q` and `msub` are exactly collinear (two T×R zero-mean matrices, same equation, no distinguishing observation); in the backtest `msize`/`mlos` are prior-only too, so 5 of 6 named terms are unidentified |
| 5 | "FX enters exactly twice and cannot cancel or contaminate" | Checked unit pass-through against the measured `10_regional_fx_passthrough.csv` (LatAm 0.623, APAC 0.860) | **Refuted as specified** — 38% of a LatAm FX move is misattributed to the *global* price RW and persists into the FY27 forecast; fixable with a `θ_r` pass-through parameter |
| 6 | "The free OOS test: 24 clean checks, 6 years × 4 regions" | Checked bucket coverage in `10_regional_panel_quarterly.csv` | **Refuted** — buckets exist 4Q24-2Q26 only; 4 clean cells (2025), ~8-10 if `numeric` rows are admitted, which contradicts the proposal's own purity rule. At n=4 the stated pass/fail thresholds are unreachable |
| 7 | "The historical replay is PIT-safe" | Checked whether priors are filtered by `knowable_from` | **Refuted** — σ_q, φ, τ_0, c̄ are all elicited from 2025-26 findings and fed into 2022-23 replays. In a prior-identified model that is look-ahead |
| 8 | "ONE joint hedonic on `06_quote_line_items.csv` kills the size × party × LOS trap" | Opened the file | **Refuted** — 76 rows of fee-line-item counts, no price/capacity/bedroom/LOS columns; the real microdata is 9.9 GB of raw dumps whose price field was dropped from late-2025 vintages |
| 9 | "Geo drag is deepening: −1.06pp 2024, −1.48pp 2025; FY25 take-rate fall is ~95% NA" | Recomputed Törnqvist and the take-rate within/mix split on `adr/01_regional_annual.csv` | **Survived** — −1.06/−1.48pp and NA 92-95% of the −16.4bp blended fall both reproduce. (Unit error: the proposal writes "within-region −1.36pp" for a *relative* −1.32% change in a take rate that moved 16bp. Fix the units before a judge sees them) |
| 10 | "The earlier 3,500 negatives do not condemn this design" | Tried to find a repeated failed design (aggregate regressor at n≈20, IA at city grain, surprise-vs-Street target) | **Survived, partially** — the constraint-vs-regressor and grain arguments hold. But `λ_r`/`δ_r` are 8 parameters on latent, prior-driven cells; a zero posterior there means "cannot tell", not "no signal", and must be reported that way |
| 11 | "The trade is P(4Q26 guide < $3,200M)" | Traced the mechanism to its source | **Survived as a trade, refuted as an output of M1** — the −3.4pp FX step comes from `29_q4-fy27-bridge.md` and `05_fx_schedule.csv`; the state space adds an error bar, not a direction. Also Zacks 4Q26 range is $3,050-3,700M on 10 estimates, so the trigger sits inside dispersion |

---

## 8. FATAL flaws

1. **"No take-rate forecast" is false and numerically refutable in one table** (§1 above). As written, the
   proposal's central claim to have removed the repo's largest plug does not hold; the plug reappears as
   `matrix[T,R] tau` and must absorb a 5.4pp residual seasonal. This is fatal *to the claim*, not to the
   model — a quarter-specific regional conversion fixes it — but it must be fixed before anything is
   presented.
2. **The headline OOS exhibit does not exist.** 4 clean cells, not 24. A proposal whose single most
   persuasive validation is unavailable in the data cannot be adopted as pitched.
3. **Identification is by prior, and the priors are elicited from the full sample.** Together these make
   the PIT histogram uninformative, which removes the proposal's own answer to "MCMC is Monte Carlo".

## 9. MUST-FIX (in order)

1. Replace `τ_{r,t}` (120 RW states) with `fee_{r,q}` — 16 quarter-specific regional conversion levels,
   prior-centred on the measured 17.4/17.1/17.2 (Q3) and 12.0/12.1/12.0 (Q4). Re-write §2.7 row 1 honestly:
   the φ-kernel removes ~40% of the seasonality, not all of it.
2. Add a measured FX pass-through `θ_r` (EMEA 1.04, APAC 0.86, LatAm 0.62, NA fixed at 1.0 and flagged
   not-identified) to the ADR chain, or explain in one sentence why unit pass-through is right and how the
   30 ex-FX ADR integers are reconciled to it.
3. Publish the parameter count honestly: ~1,100 latent quantities, ~264 observations, identification by
   prior, with a prior-to-posterior contraction ratio per reported term. Strike from the decomposition
   exhibit any term contracting <20%.
4. Re-label the OOS test: 4 clean 2025 cells plus leave-one-year-out on the 56 filed quarterly cells. Drop
   the 19-21/24 language entirely.
5. Freeze a **PIT-safe prior-elicitation rule** (priors from trailing data through T−1) and report both the
   full-sample-prior and PIT-prior replays side by side.
6. Fix the data claims: `06_quote_line_items.csv` is a fee-coverage tally, not a hedonic panel — re-point
   the hedonic at `06_wtp_hedonic_coefs.csv` / raw dumps and re-cost it; the derived rows span 4Q22-3Q24
   not 1Q24-3Q24; state explicitly what happens to the 22 `numeric` regional nights cells.
7. Merge `q` and `msub` into one regional ADR deviation state, or add an observation that separates them.
   Reporting both with credible intervals is not defensible.
8. Fix the take-rate decomposition units ("−1.36pp" vs a 16bp move).
9. Cut the Stan path to the constrained-LS MVP as the *primary* deliverable, with Stan as a stretch goal
   gated at end of Week 1 — not the reverse.
10. Add `phrase_kind` to the interval file so coded qualitative phrases ("less than 1%" → 0.5) are not
    entered as ±0.5 symmetric intervals around a false integer.
11. State the trigger convention for the trade: which consensus vendor, which timestamp, next-open entry.

## 10. WHAT TO KEEP even if the whole is rejected

1. **The 72-cell exact filed-dated regional revenue panel.** Verified, real, unused anywhere in the repo,
   and it is the only quarterly regional constraint that is not an interval. Build it on day 1 regardless
   of which lens wins.
2. **Interval-censored likelihood for the disclosures** — buckets, rounded integers, annual rounded nights,
   qualitative guides. Strictly better than the repo's midpoint practice, and the ±3pp robustness rebuttal
   in §8 is the right way to defend it.
3. **Geographic mix and seats dilution as outputs of an identity, not rows.** Closes the audit's $175M and
   $88M inconsistencies by construction; costs almost nothing.
4. **The exclusion of the 14 `derived` rows and of the Inside Airbnb panel from the historical replay.**
   Both correct, both verified, both the kind of discipline a Citadel judge rewards.
5. **Softmax/log-level adding-up** in place of `CALIB = −0.41pp` and current-period growth weighting.
6. **The two verified differentiating facts**: geo drag deepening −1.06 → −1.48pp, and the FY25 take-rate
   decline ~92-95% North American. These are the memo's exhibits and they survive independent of the model.
7. **The model-to-model reconciliation table** (§5d) — the artefact the audit says does not exist. Do it
   even as plain arithmetic rather than as parameter restrictions.
8. **The 4Q26 FX step-down as the trade**, with the 9/9 base rate and next-open execution.

## 11. How this lens should interlock with the others

M1 should be demoted from "the model" to **the repo's accounting spine**: a constrained reconciliation
engine that owns one thing — the regional nights × ADR × conversion identity forced through the 72 exact
revenue cells, the 28 buckets, the 68 ADR integers and the 24 annual cells, with geography and seats as
outputs. Everything above that line belongs elsewhere. M6 owns FX and the booking→check-in kernel and
must hand M1 a *quarter-specific, pass-through-adjusted* conversion, not a τ state. M4 owns the hedonic and
the regulatory DiD and must hand M1 coefficients estimated on real microdata, with the honest caveat that
the current-vintage price field is gone. M2's covariates should be dropped from M1 entirely for the
prelim — at 8 loadings on prior-driven cells they cannot be evaluated, and the shrinkage story is a
distraction in a two-page memo. M3 is the lens that carries the trade: M1 hands it a 4Q26 revenue interval
and the already-booked-GBV convolution, M3 maps that to the guide midpoint through the cushion
distribution and to the 9/9 drift rule. M5 should challenge the *sum* of the price/sub-regional residual
at market grain — not the split, which is unidentified by construction. If the team can build only one
thing from this proposal, build the 72-cell panel and the constrained reconciliation; if it can build two,
add the reconciliation table. The state space itself is a three-week research project masquerading as a
three-week deliverable.
