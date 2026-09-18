# Research audit: USD / Iranian toman on December 31, 2026

Audit date: 2026-09-11  
Question: [Metaculus post 45340](https://www.metaculus.com/questions/45340/)  
Research reviewed: [research-log.md](../research-log.md), initial run dated 2026-09-11  
Disposition: **Open — original researcher reconciliation requested.** No revised forecast was submitted or implemented.

## Assessment

The scenario mixture is mathematically reproducible and the spot-rate evidence broadly checks out. The supporting argument needs correction: the Polymarket anchor is not a coherent normalized distribution, the crisis threshold is mislabeled, historical event windows are misinterpreted, and the proposed update rules do not follow the stated model.

The audit does not establish that 55.5% above 250,000 is an unreasonable judgmental forecast. It invalidates the claim that three independent approaches agree within two percentage points. Do not automatically replace the forecast with a market number.

The reorganization changed only the log's local evidence paths. Its substantive claims and conclusions are preserved so the original researcher can respond to this audit.

## Scope and reproduction

Reviewed all sections of the log, the [saved Metaculus metadata](../sources/post_45340.json), [TGJU history](../datasets/tgju_usd_irr_history.csv), and [Bonbast data](../datasets/bonbast_usd_toman_2026-07-13_to_09-11.json). Spot-checked live Bonbast, AlanChand, Euronews, Iran International, TIME, Polymarket, and GlobalSecurity pages.

Live Metaculus and TGJU API retrieval and the cited Bloomberg article were not accessible during the audit. Saved-data calculations do not independently establish the provenance of every historical observation. The original Polymarket order-book snapshot was not saved among the supplied files; arithmetic below uses the quotes transcribed in the log. This was a targeted source audit, not independent corroboration of every geopolitical detail.

Run the included dependency-free calculation from the project root:

```powershell
node Fall-Cup-2026/questions/usd-iranian-toman-2026-12-31/audits/reproduce-2026-09-11.cjs
```

The script reads the saved CSV and prints results. It does not contact APIs, modify data, or submit forecasts. Normal CDF values use an approximation accurate enough for the displayed precision.

Historical method: 111 calendar-day forward windows; last observation on or before each target date; require a fully observed forward horizon and 90 days of historical coverage. Results below use a 235,000-toman starting quote. Dates with no quote use the preceding available observation.

## 1. High priority: reconstruct the market anchor

References: claim 12; section 4 market-shape hypothesis; section 5 anchor and final-minus-anchor.

Recorded bracket probabilities are 0.155, 0.215, 0.095, 0.305, 0.130, and 0.040. They sum to **0.94**. Therefore:

- Sum of brackets at or above 250k: **57%**.
- Complement of brackets below 250k: **63%**.
- Proportional normalization of all six brackets: **60.64%** at or above 250k.

These are different repairs or representations, not interchangeable estimates. Normalizing the probabilities also puts the median in the **300–350k bracket**, not 270–300k.

The two lower brackets have recorded bid/ask intervals of 15–16% and 21–22%. A coherent probability vector lying inside those intervals has a complementary mass of **62–64%** at or above 250k. This assumes synchronized quotes, exhaustive nonoverlapping outcomes, and treating spreads as admissible probability intervals. It is not a statistical confidence interval or evidence of executable size. Polymarket includes equality in the higher bracket, so its event is technically >=250k; for the continuous model the distinction has zero mass, but the resolver can use discrete quotes.

The forecast's 55.5% is consequently 6.5–8.5 points below that spread-based comparison, not 1.5 points. The [live market rules](https://polymarket.com/event/usd-x-iranian-rials-end-of-december) confirm the bracket structure, Bonbast source, and higher-bracket treatment at boundaries.

**Requested correction:** save timestamped market responses and books; build and document one coherent anchor; distinguish prices, midpoints, and spreads; recalculate the claimed disagreement. Thin liquidity justifies discounting the market. Multiple peaks alone do not prove a liquidity artifact.

## 2. High priority: correct the crisis threshold and base-rate probability

References: claim 19 and section 5 base_rate_estimate.

The unconditional statistics reproduce: 3,861 windows, mean log return 0.10110, sample SD 0.17008, median 0.06394.

The reported crisis statistics reproduce with **trailing 90-day log return >0.25**, equivalent to a quote increase of **28.40%**. A simple quote increase >25% gives 599 windows, not 490.

| Statistic | Reproduced 490-window sample |
|---|---:|
| Mean log return | 0.11913 |
| Sample SD | 0.25875 |
| 5th / 50th / 95th log-return percentiles | -0.26508 / 0.09934 / 0.67037 |
| P(terminal quote >250k), starting at 235k | **57.55%** |
| P(negative forward log return) | 33.27% |

The claimed 55% upper-bound probability does not follow from this empirical sample. The headline percentile transformation does approximately reproduce.

The windows overlap and are concentrated in a few historical episodes; 490 is not an independent-event sample size. With the same crisis definition, changing the start-year restriction gives P(>250k) of 54.18% for 2018 onward, 52.28% for 2020 onward, and 48.94% for 2023 onward. These are sensitivity checks, not endorsements of a particular cutoff.

**Requested correction:** specify simple versus log return, date alignment, quantile method, and sample-SD convention; correct the probability; show period and episode sensitivity. If uncertainty intervals are added, account for overlapping observations.

## 3. High priority: fix the rally comparison and causal inference

References: claim 20; section 4 large-rally and lower-bound hypotheses.

The five reported event minima reproduce within **20 calendar days** after the selected dates. They are not 111-day historical extremes. For the February 27 anchor there is no same-day quote; the calculation uses February 26. The log elsewhere dates war onset to February 28.

The saved series contains a **39.74% decline in the USD/IRR quote from 2018-09-25 to 2019-01-14**, a 111-day log return of -0.50644. That is larger than the approximately 36.17% quote decline needed to move from 235k to 150k. The log's examples of -20% and -11% cannot serve as exceptions to a purported maximum exceeding 36%.

A fall in the dollar quote and an increase in the dollar value of the rial have different percentage denominators. Define which one is being measured. Event-day-close anchors can also miss the immediate event-day response; selected post-event minima do not isolate a causal effect.

**Requested correction:** separate fixed-horizon historical returns from event studies; specify the pre-announcement baseline, event timing, and observation window. Weaken the assertion that only blockade relief or regime change can produce >20% appreciation. This finding alone does not establish that the 1.5% lower tail is too small.

## 4. High priority: derive updates from a consistent model

References: sections 7 and 8.

| Check | Log | Recalculation |
|---|---|---|
| Spot increases 5%, all mixture parameters fixed | Distribution +4%; P(>250k) +4 points | Distribution +5%; P rises from 55.44% to **64.33%** |
| 235k compounded at 6% weekly for 16 weeks | ~500k | **596,983** |
| Sep 30 spot =250k under the stated weekly lognormal rule | Median ~285k; P >=70% | Median **271,604**; P **63.69%** |

For the last row the weekly rule is interpreted as a single lognormal with log drift 0.10 × 92/111 and SD 0.26 × sqrt(92/111). This is itself a change from the five-component mixture. A higher event-triggered forecast is possible if additional momentum information is deliberately incorporated, but that conditioning must be stated.

Increasing scenario B from 20% to 35% does not identify which other weights lose 15 points. Fixed late-November tail floors also need to be reconciled with spot and remaining uncertainty.

**Requested correction:** define one update procedure with explicit weight transfers, horizon treatment, and any event-conditioned adjustments. Recompute all sensitivity rows from it. Avoid presenting unexplained judgmental overrides as outputs of the existing model.

## 5. Medium priority: qualify economic-source claims

References: claims 4–6 and 11; section 4 intervention hypothesis.

- **Capacity affected versus capacity lost:** the [Iran International page](https://www.iranintl.com/en/202609055912) contains an appended appliance-industry article saying the struck complexes account for roughly 50% of steel capacity and 70% of petrochemical capacity. It also says detailed damage and operational-status figures are unavailable. Those shares do not establish that 50%/70% of national capacity was disabled. Cite the individual appended article and qualify the claim.
- **Percentage denominator:** moving from 1.35M to 2.1M rials per dollar is a 55.56% increase in the dollar quote and a 35.71% fall in the rial's dollar value. The approximately 60% loss language is erroneous even though it appears in the [Euronews source](https://www.euronews.com/business/2026/09/02/iranian-rial-hits-record-low-as-us-dollar-breaks-22-million-mark).
- **Intervention sustainability:** the [CBI report](https://www.iranintl.com/en/202609018792) attributes $500M of intervention in the previous week to the governor. That does not establish a sustained $500M/week burn rate, accessible reserve balances, or net foreign-exchange flows. The $2B is an announced intervention capacity, not a verified reserve ceiling.
- **Evidence dependence:** the snippet-only oil-export claim is marked non-load-bearing but is used to argue against quarter-long stabilization. Either verify and promote it to load-bearing, or remove its quantitative role. Retain the distinction between an official's claim and verified resources.

## 6. Medium priority: separate resolution uncertainty from economic tails

References: section 0b and section 7 resolution-source sensitivity.

The saved API metadata contains null resolution criteria and fine print. Bonbast remains a working assumption; another platform's rules do not establish Metaculus's rules. Do not label the contracts identical before confirming source, quote side, timing, finalization, missing data, redenomination, and boundary semantics.

The mixture's 1.486% below 150k is entirely an economic tail. It does not allocate separate probability to a different source. Illustratively, a distinct 1.5% chance of certain below-bound resolution would produce:

```text
0.015 + (1 - 0.015) × 0.0148577 = 0.0296349
```

This is an illustration, not a recommendation to assign 1.5% to resolver mismatch.

**Requested correction:** frame the current forecast as conditional on the assumed contract, or explicitly model source uncertainty. Refresh the official criteria when available and regenerate the forecast if necessary.

## 7. Lower priority: reproducibility and presentation

- The listed mixture has an in-range density maximum around **237,700 toman**, rather than increasing all the way to 250k.
- Mixture mass in 150–200k is approximately **10.00%**, and in 200–250k approximately **33.07%**, rather than 11% and 32%.
- P(>400k) is **8.15%**, rather than approximately 7%.
- Claim 21's annualized volatility figures need the original calculation code: calendar-day versus observation windows, missing-date handling, and annualization factor were not documented sufficiently to reproduce all five reported figures.
- The saved Bonbast filename ends in 09-11 but observations end on **09-10**. State that distinction explicitly.
- The independence claim is not established by the query log: market searches preceded the detailed book fetch, and the base-rate and decomposition estimates share inputs. Preserve a timestamped pre-anchor estimate if claiming independence.
- The suggested slider settings are qualitative. Export and inspect the actual CDF, boundary masses, and scoring constraints before treating them as an implementation of the five-component model.

## What passed

[AlanChand](https://alanchand.com/en/currencies-price/usd) confirms the stated 2,369,000-rial sell and 2,345,500-rial buy quotes. [Bonbast](https://www.bonbast.com/graph/usd) confirms its display is in toman, with 1 toman = 10 rials. The saved metadata supports the stated 150–250k bounds and 200 in-range buckets, with both bounds open.

Analytically evaluating the stated five-component normal mixture of log returns gives:

| Output | Recalculated |
|---|---:|
| 5th percentile | 179,966 |
| 10th percentile | 196,405 |
| 25th percentile | 223,718 |
| Median | 257,977 |
| 75th percentile | 314,395 |
| 90th percentile | 384,160 |
| 95th percentile | 439,189 |
| P(<150k) | 1.4858% |
| P(>250k) | 55.4417% |

These support the log's final numbers to normal rounding / Monte Carlo precision. The distinction between November forecast closure and December resolution is also correctly recognized.

## Handoff checklist for the original agent

- [ ] Correct the market anchor and explain the remaining disagreement.
- [ ] Correct the crisis threshold and empirical upper-bound probability; document methodology and sensitivities.
- [ ] Replace the historical rally argument with comparable windows and qualified event inference.
- [ ] Derive coherent monitoring and sensitivity rules with explicit scenario-weight transfers.
- [ ] Qualify capacity-loss and intervention claims; verify or downgrade snippet-only quantitative evidence.
- [ ] Confirm the Metaculus resolution contract before submission.
- [ ] Reconcile minor distribution summaries and export a verifiable forecast CDF.
- [ ] Add a dated response under this audits folder, stating accepted findings, justified disagreements, forecast changes, and remaining uncertainties. Link it from the research log and question overview.

Keep this audit as the dated review record. Put the response and any revised forecast in separate dated artifacts so another reviewer can follow the changes.

