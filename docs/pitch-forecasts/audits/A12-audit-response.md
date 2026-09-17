# A12 — audit response (R10, R11, R15, R16)

Response date **2026-09-17**. Responds to [`A12-research-audit.md`](A12-research-audit.md) (independent Opus auditor standing in for Codex `gpt-6-astra`; 25 findings, 3 critical; independent numbers R10 0.11 / R11 0.29 / R15 0.18 / R16 0.30). Every finding was reproduced with `py -3.13` before it was ruled on; the audit's own reproduction script is saved verbatim as [`A12-reproduce.py`](A12-reproduce.py) and its output as [`A12-reproduce.stdout.txt`](A12-reproduce.stdout.txt) (run from the repository root, exit 0, no path fixes needed).

All four logs are now at **revision 2** with a `## 10. Revision notes` section, and all four `forecasts/2026-09-17-forecast.json` files carry `"revision": 2`.

## 1. Summary

**Ruling: 22 findings accepted, 3 accepted in part, 0 rejected outright.** The three partials are A12-04 (the comp credit — removed from the blend as asked, but replaced by a smaller *measured* credit on one leg), A12-10 (one object for R11 and B15 — accepted; its specific instruction, "R11 must adopt B15's 0.10", rejected because both inputs behind that 0.10 moved) and A12-14 (the Kalshi parser error — accepted; the audit's proposed *replacement* reason rejected, see §4).

| question | revision 1 | auditor | **revision 2** | what moved it |
|---|---|---|---|---|
| R10 dollar ≥4% weaker by 11 Feb | 0.09 | 0.11 | **0.10** | forward vol 4.62% instead of trailing 4.12% (+0.012), poll drift −0.66% instead of −0.42% (+0.006), H = 100 instead of 105 (−0.004) |
| R11 4Q26 US RevPAR ≥ +4% | 0.38 | 0.29 | **0.26** | the +0.8pp comp credit cut to a measured +0.2 (−0.09), the FY-implied leg recomputed on *measured* 2026 H1 months (−0.03), a measured base rate at weight 0.2 (−0.02) |
| R15 World Cup quantified as small | 0.14 | 0.18 | **0.18** | the base rate rebuilt from the coded record (0.10 → 0.23) and then cut by the slot argument the audit supplied; the two "immateriality" routes re-priced |
| R16 4Q26 nights print ≥ 134.0m | 0.27 | 0.30 | **0.31** | one mixture at one cushion, published unrounded, on the C02 revision-2 vector, a residual sd of 2.0 and R01 revision 2's 9.5 centre |

Three things changed that are bigger than any single number.

1. **There is now one 4Q26 nights distribution.** `questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json` is the object; R16, B13, F01/F02 and X01 read it. Its two tails are 0.307 and 0.309 — published unrounded, from one cushion, on one set of legs. The three-versions-of-one-object problem in A12-01 is gone.
2. **There is now one 4Q26 US RevPAR distribution**, `questions/risk-q4-us-revpar-strong/datasets/r11_v2_joint_object.json`, whose *both* tails are fitted to the same three-view blend. R11 publishes 0.259 and B15 must publish 0.232.
3. **R11's base rate is a measured series.** 58 Lodging Magazine reprints of the CoStar monthly US release were fetched and saved under `questions/risk-q4-us-revpar-strong/sources/lodging_monthly/`; a new parser, `datasets/r11_extract_lodging_monthly.py`, turns them into 28 dated monthly observations with a per-file accept/reject report. The hand-typed list at `r11_model.py:36` is withdrawn, and so is every number B15 took from it.

## 2. Finding-by-finding

Severity and question are the audit's. "Recomputed" figures are mine unless stated.

### The three critical findings

| id | ruling | recomputation / reason |
|---|---|---|
| **A12-01** R16/B13/F01 are not one object | **accepted** | Confirmed exactly: `r16_views.csv` carries a blend of 0.3032 and `b13_views.csv` 0.2622, and reproducing them needs V2 = 0.40 in one and 0.1558 in the other — cushions N(0.78, 1.3) and N(1.2, 1.3). Two tails of "one distribution" from two different parameters, each then rounded down. **Fixed by building the distribution once** on R01 revision 2's centre N(9.5, 1.70), C02 revision 2's vector, one cushion N(1.0, 1.3), one Street leg N(9.926, 1.23) and a stated residual, and publishing it as `adopted_q4_states_v2.json`. Numbers in §3. One note against the audit: its finding text offers 1.2 *or* 0.78 as "the" cushion, and then its own repaired mixture (§Independent numbers) silently uses **1.0** — a third value. 1.0 is the right one and the reason is now written down in the file: the directional-era record is mean −0.2 sd 1.3 on five stable guides and the two bucket-era beats are +4.8 and +1.15, so 1.0 is the midpoint, not a hand-cut. |
| **A12-02** the 0.66 coefficient applied twice in every §9 EPS row | **accepted** | Reproduced on the FY27 line build (revenue $15,829M, EBITDA $5,483M, margin 34.639%): +$250M held gives +1.02pp and **+$0.350**, not +$0.23. The error is exactly as described — the margin row spends the 0.66 as pp-per-point and the EPS row spends it again as a dollar rate. **Every §9 EPS row in the batch is rebuilt** on ΔRevenue × $0.0014 applied once, with the flex alternative (0.42pp/pt) stated beside it: R10 **+$0.51**, R11 **+$0.07**, R15 **$0** (the row is zero for a different reason, A12-24), R16 **+$0.41**. B13's −$0.31 is the A17 batch's to fix; it is named in §3. |
| **A12-03** R11's base rate is typed into the script; `sources/` empty | **accepted** | Confirmed: `r11_model.py:36` is `hist=[12,3,1.5,2,1,1,2,3,0,-0.5,-1,0,3.8,5.2]`, presented in claim 10 as derived from claims 3–5, which contain no such series; the repo's only quarterly hotel panel (`q3nowcast/G/G_quarterly_panel.csv`) is operator/global/system-wide, a different object. **Fixed by retrieval, not by relabelling**: 58 Lodging Magazine reprints saved, 28 monthly observations parsed out of them (30 weekly or P&L pages rejected with a logged reason), quarters computed with `n_months` carried. The measured base rate is **1 of 9 quarters ≥ +4.0% (Laplace 0.18)**, or 1 of 6 on the fully-snapshotted subset (Laplace 0.25); the mirror is **4 of 9 ≤ +1.0%**, not B15's "6 of 13". Two figures are still hand-carried and are flagged in every output: March 2026 (+5.9, repo note) and December 2025 (−2.2, implied from FY2025 −0.3%). |

### R10

| id | ruling | recomputation / reason |
|---|---|---|
| A12-05 trailing vol used as forward vol | **accepted** | Reproduced: on DTWEXBGS 2006–2026, windows starting in the calm quintile realise **4.64%** over the next 105 observations (ratio 1.32); at H = 100 the model's own regime table gives 4.62% for quintile 1 and 4.80% for the ±1pp band. Parametric leg 0.07 → **0.103**. The log now carries the forward-vol column in claim 5 and moves "trailing vol is the forward vol" to §4 as a discarded hypothesis. |
| A12-06 poll drift mis-derived twice | **accepted** | Reproduced to the decimal: interpolating spot 1.1538 → 3m 1.16 → 6m 1.17 to the 4.85-month point gives 1.1662, +1.07% log, which at the measured broad/EUR beta −0.62 is **−0.64%**. The model's own re-derivation at the 4.86-month resolution point gives −0.66%; the 2bp difference is the day count and is immaterial. Published: **−0.66%**. |
| A12-13 claim 9 cites the degraded 07:56 option pull | **accepted** | Both JSONs read. The 07:56 pull has every bid, ask and OI at 0; the **03:50** pull has UUP Jan-2027 28C bid 0.40 / ask 0.75 with OI 6,924 and 28P bid 0.30 / ask 1.15 with OI 2,180. Black–Scholes on the mids gives a call IV of 5.2% and a put IV of 14.1% — a band so wide the "no usable quote" verdict survives, but not on the evidence revision 1 gave. Claim 9 rewritten on the 03:50 pull, with the measured DXY/broad realised ratio (5.25% / 4.12% = **1.27**) used to bring the basket band back to the broad index. Anchor 0.10 → **0.111**. |
| A12-15 H is 100, not 105 | **accepted** | Reproduced: weekdays 17 Sep 2026 – 11 Feb 2027 net of Columbus, Veterans, Thanksgiving, Christmas, New Year and MLK = **100**, and the 2025–26 analogue window in the saved FRED file carries exactly 100 non-null observations. Empirical P 0.1218 → **0.1167**. Effect −0.004, and the input is now a stated convention (§0b convention 5). |
| A12-19 ADR row and revenue row disagree 3–4× | **accepted** | The reconciliation the audit names is right and was missing: the ADR row is a **booking-date** effect on the quarter's bookings, the revenue row is the **kernel-recognised** effect on the quarter's revenue (B4 §6, ⅔ prior quarter + ⅓ two back). One sentence added; both numbers kept. |
| A12-20 $158M/pt is 1% of FY27, not of FY26 | **accepted** | B4 §5.2 states $142.9M per growth point (1% of the $14,293M FY26 base) and its own table prices +2.5pp at +$354M. Recomputed at this log's E[move \| Yes] of −5.5% (2.53pp, not the audit's 2.58pp at −5.6%): **+$362M**, margin +1.46pp, EPS **+$0.51**. The audit's +$368M is the same arithmetic one tenth of a point of FX further out; the row is also now labelled a **ceiling**, because B4's scenario is an immediate parallel shift while this event completes only on 11 February. |
| A12-21 "0 in 12 of 21 years" overstates | **accepted, with a correction to the audit** | Recomputed: **10 of 21** years with zero sub-threshold windows, and the rest of claim 4 checks (2007 40.8%, 2009 47.0%, 2010 35.4%, 2020 41.6%, 2025 26.4%, 2017 29.3%). The audit's effective-sample figure is for H = 105: at H = 105 the non-overlapping block count is 49 and the SE 5.5pp; at **H = 100, which is the right horizon (A12-15), it is 51 blocks** and the phase range across block starts is 0.059–0.196 — the interval now cites 51 blocks and SE ≈ 4.5pp as its source, not the audit's "about 48 / 4.7pp". |

**R10 outcome.** Blend 0.35 × 0.10 (regime-conditioned empirical) + 0.35 × 0.103 (parametric at the forward vol) + 0.30 × 0.111 (implied construction) = **0.104 → 0.10** (0.06–0.17). One point below the auditor; the gap is the horizon (its 0.11 is at H = 105).

### R11

| id | ruling | recomputation / reason |
|---|---|---|
| A12-04 the +0.8pp easy-comp credit is double-counted | **accepted in part** | The audit's arithmetic reproduces exactly: dropping the credit takes the centre 3.517 → 2.717 and P(≥4) 0.3867 → **0.2221**. Its *argument* is accepted for the FY-implied leg — a published FY26 y/y forecast necessarily embeds the 4Q25 base, so crediting the comp on top of it is a double count, and §7 never tested that direction. It is **not** accepted for the AR leg, and the replacement is measured rather than argued: on the newly parsed series 3Q25 printed −1.40 and 4Q25 −1.80, so a one-step y/y extrapolation into Q4 faces a comp easier by exactly **0.4pp**. Credited to the AR leg only = **+0.2 on the 50/50 blend**, against revision 1's +0.8 on the whole blend. Both directions are now in §7 (no credit: 0.24; the full +0.8 restored: 0.32). |
| A12-10 R11 and B15 publish different values for one quantity | **accepted in part** | Confirmed: R11 §6 said P(≤1) = 0.07 (its normal), B15 published 0.10 (its mixture), and B15's mixture reproduces R11's 0.3868 to three decimals. The principle — one object — is accepted and implemented. The instruction — "replace R11 §6's 0.07 with B15's 0.10" — is **rejected as superseded**: both of that 0.10's inputs have moved (the centre, by A12-04 and by the measured H1 months; the base rate, by A12-03). The object is now fitted so that **both** tails equal the same 0.5/0.3/0.2 blend, which is the only way a single distribution can serve both questions honestly. **P(≤ +1.0) = 0.232.** Matching only R11's tail, which is what a simple re-centring does, would have handed B15 0.177 — a number this log's own blend does not imply. |
| A12-11 the anchor has no saved snapshot | **accepted** | `sources/` was empty at audit time. It now holds **66 files**: the 58 Lodging monthlies, four timestamped forecast/annual pages (`hotelnewsresource_costar_forecast_10aug2026_*`, `hoteldive_costar_te_raise_outlook_aug2026_*`, `hoteldive_costar_te_forecast_jun2026_*`, `hoteldive_fy2025_us_hotel_performance_*`) and the FY2023 annual. The audit's proposal is followed: claim 2 is re-cited to the dated repo note as **primary**, with the trade press as secondary. Claim 8 (October 2025 −0.9%, "declines continue throughout December") is marked **"search snippet, unsaved"** — str.com and costar.com 403 and a Wayback pull returned nothing (`sources/str_wayback/` is empty and stays empty as the record of that). |
| A12-17 the AR leg is called a two-step and applies one | **accepted** | `r11_model.py:23` applies `lr + phi*(q3 - lr)` — one step, 2.0 + 0.6 × 3.5 = 4.10. Label corrected in §5, in the claim and in the JSON field. φ and the long run are now stated as hand-set and bracketed in §7 (φ 0.4–0.8 → 0.23–0.29; lr 2.1–3.0 → 0.26–0.27). A second start is added because the Q3 average embeds July's World Cup month: from the mid-August clean exit rate (+4.4, w/e 22 Aug, excluding the Labor-Day pair 1.7 / 16.1) the step gives **+3.54**, so the leg is +3.87, not +4.10. |
| A12-18 the §9 margin and EPS rows are understated 2–3× | **accepted** | Recomputed on the line build: at the revision-2 delta (+$27M of FY26 revenue, +$50M of FY27) the rows are **+0.12pp**, **+0.21pp** and **+$0.07**. The audit's figures (+0.09 / +0.12 / +$0.042) are the same arithmetic on revision 1's smaller deltas and reproduce exactly. All three remain immaterial; the point — that two R-tables should not use one coefficient two ways — is taken. |

**R11 outcome.** FY-implied 4Q26 **+2.69** (on measured Q1 +3.53 and Q2 +5.60), AR leg **+3.87**, adjustments −0.4 election week / −0.2 CR expiry / +0.2 measured comp = centre **+2.88**. Blend 0.5 × 0.284 + 0.3 × 0.248 + 0.2 × 0.216 = **0.259 → 0.26** (0.17–0.40).

### R15

| id | ruling | recomputation / reason |
|---|---|---|
| A12-08 "1 − (0.95)²" is not the cited arithmetic | **accepted** | Reproduced: 1 − 0.95² = 0.0975, which needs a per-print 0.05; the cited inputs give 1/8 = 0.125 raw (0.234 over two prints) or Laplace 0.20 (0.360). The 0.95 appears from nowhere. The base rate is rebuilt from the record and **published at what the record says** — 0.44 raw / 0.51 Laplace over two prints — and then cut explicitly, with the cut named. Base-rate estimate 0.10 → **0.23**. |
| A12-09 the strongest argument for a low number is missing | **accepted, and it is the best finding in the audit** | Verified independently: the two size-language precedents sit in the **run-up** and **own-quarter** slots, and the World Cup's equivalents — the 4Q25 preview, 1Q26 and the 2Q26 letter and call of 6 Aug 2026 — have all passed producing only "bookings from any single event may be temporary", which convention 3 correctly excludes; the one lap precedent (3Q25 Paris) produced "a slightly unfavorable year-over-year comparison", a headwind framing. So the highest-hazard slots are spent and the observed post-event rate is 0 of 3. Promoted to §4, §5 and the pre-mortem; it is what takes the record-implied 0.44–0.51 down to 0.19 on the size-language route. |
| A12-22 the anchor quotes a superseded C05 and is not independent | **accepted** | C05 is at revision 2 with 0.28 and its own anchor null. `anchor` set to **null** with `NO_EXTERNAL_ANCHOR`; C05 (0.28), R09 (0.25) and R08 (0.15) relabelled **sibling comparisons**; \|final − anchor\| no longer reported for R15. |
| A12-23 the 4Q25 "incremental but not primary growth" line is a site summary | **accepted** | Confirmed: the phrase occurs once, inside an escaped `<li>` in the mirrored transcript. It was never coded as size language, so the count does not move, but the event-record cell is now marked. |
| A12-24 §9 books revenue and margin for a disclosure | **accepted** | The team's path already carries only +0.5pt of World Cup effect in 2Q26, so a confirming statement moves no line. Revenue and margin rows set to **0**; the stock line stays at +$1 as an explicitly narrative entry. (The audit is also right that the old margin row was arithmetically wrong — 0.66 × 0.13pt is 0.086pp, not 0.01 — but the correct value is zero for the prior reason.) EV **$0.18**; "drop from the risks list" unchanged and better supported. |

**R15 outcome.** Tree 0.02 / 0.04 / 0.06 / 0.08 → union **0.186**, published **0.18** (0.10–0.30) after the convention-3 strictness cut. Identical to the auditor's number, reached through its own reasoning.

### R16

| id | ruling | recomputation / reason |
|---|---|---|
| A12-07 V2 is built on C02 revision 1 | **accepted** | Confirmed by `git log`: C02 revision 2 landed in `85887c5` at 03:51:45 and the R16 forecast file was written at 04:09:31. Re-running V2 on the revision-2 vector (0.18 / 0.17 / 0.30 / 0.31 / 0.04) moves 14 points of mass into the bucket where the conditional is ~0.01. Alone: −0.02 on R16 and +0.02 on B13 — the symmetry A12-01 asks for, arriving almost for free, exactly as the audit says. |
| A12-12 V1's residual is half the observed sequential-change sd | **accepted** | Reproduced from `abnb_driver_history_quarterly.csv`: the Q3→Q4 changes are −4.93, −1.52, +3.87, +1.03, mean −0.39, sd **3.74** on n = 4, against V1's total sd of 1.85. Residual widened 1.4 → **2.0**, and the reason is stated rather than fitted: n = 4, and the lap is a mechanism estimate, not an estimated effect, so the residual should sit between the mechanism's own uncertainty and the raw sequential scale. Alone: +0.03. The audit's pure outside view (N(9.11, 4.11), P = 0.42) is carried in §7 as the upper bracket. |
| A12-14 "volume and open interest null" is a parser error | **accepted in part** | The parser error is real and reproduces: `volume_fp` runs 36–294 and `open_interest_fp` to 170. The audit's **replacement reason is rejected**: it rests on `updated_time` = 2026-08-04, and the A16 audit showed that same field frozen at 2026-04-09 across 131 Kalshi Fed markets carrying 298,901 contracts of 24-hour volume — it is **series metadata, not a quote timestamp** (A16-18). Claim 10 now disqualifies the ladder on three verifiable grounds instead: `volume_24h_fp` is 0.00 on every rung; the spreads run to 80 cents (>570m bid 0.63 / ask 0.99); and the last prices imply a 4Q26 of 120–123m against a 1H26 actual of 304.5m, a quarter no participant in this debate holds. Zero weight, unchanged. |
| A12-16 the conditionals published are V1's, not the mixture's | **accepted, with a recomputation** | Confirmed. The published object gives E[4Q26 \| ≥134.0m] = **11.16%** and E[4Q26 \| <134.0m] = 7.48%. The audit's 11.14 matches; its E[· \| ≤131.0m] of **6.16 does not** — that figure comes from a mixture built on the revision-1 legs (residual 1.4, C02 revision 1), not from its own repaired one. On the adopted object it is **5.93**. §9 rebuilt on the mixture conditionals: 4Q26 nights **+3.1pt**, 4Q26 revenue **+$92M**, FY27 revenue **+$290M**, stock **$11**, EV **$3.4**. Material either way, as the audit says. |
| A12-25 the at-print bar record has three gaps and an unstamped vendor | **accepted** | Recomputed: 16 of the 19 quarters exist; **3Q22, 1Q23 and 2Q24 are absent**; the last 12 give mean +0.874% and sd **1.414** (the log said 1.5) with ≥0 in 10 of 12; a 2023-01-01 calendar cut gives 13 prints, +0.678%, 10 of 13. All 19 L0 nights rows carry `vendor = vendor_not_recorded`, against brief rule 5. All four corrections are in claim 6, and the window is now given as a print count. The conclusion (the bar is usually beaten) is unaffected; the memo must not call these "the LSEG-family consensus". |

**R16 outcome.** V1 0.181 / V2 0.379 / V3 0.514, blend 0.5 / 0.3 / 0.2 = **0.307 → 0.31** (0.19–0.44). One point above the auditor; the difference is that this revision re-bases the pass-through reference to R01 revision 2's 9.5, which keeps the team's 8.1 as the unconditional Q4 centre, while the audit's replay kept 9.67 and let the centre drift to 8.0.

## 3. The two adopted objects

### 4Q26 nights — `questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json`

Three-component mixture on 4Q26 nights y/y growth over the fixed 121.9m base, printed to 0.1m.

- **V1, weight 0.5** — 3Q26 ~ N(9.5, 1.70) (R01 revision 2's `adopted_print_states_v2.json`); 4Q26 = 8.1 + 0.5 × (Q3 − 9.5) + N(0, **2.0**); 12% short tail at 5.5 ± 1.5.
- **V2, weight 0.3** — C02 revision 2's vector (0.18 / 0.17 / 0.30 / 0.31 / 0.04) × bucket midpoint (10.75 / 9.75 / 8.0 / 6.0) + cushion **N(1.0, 1.3)**; "no descriptor" falls back to V1.
- **V3, weight 0.2** — N(9.926, 1.23) = Bloomberg MODL 134.0m ± 1.5m (n 28, 2026-09-12).

| quantity | value |
|---|---|
| mean / sd / median | **8.61 / 2.28 / 8.75** |
| P(≥ 134.0m) — R16 | **0.307** |
| P(131.1–133.9m) | **0.384** |
| P(≤ 131.0m) — B13 | **0.309** |
| E[4Q26 \| ≥ 134.0m] | **11.16%** (135.5m) |
| E[4Q26 \| ≤ 131.0m] | 5.93% |
| E[4Q26 \| < 134.0m] | 7.48% |
| E[3Q26 \| ≥ 134.0m] | 9.78% |
| percentiles 5/10/25/50/75/90/95 | 4.70 / 5.56 / 7.06 / 8.75 / 10.24 / 11.44 / 12.14 |

**Logs that must adopt it, and what they must change:**

| log | batch | currently | must publish |
|---|---|---|---|
| R16 `risk-q4-nights-print-meets-street` | A12 | — | **done in this revision**: 0.31 |
| **B13 `bonus-q4-nights-print-weak`** | **A17** | 0.26, "mean ≈ 8.3" (the V1 mean carried onto mixture weights), V2 at cushion 1.2 | **P(≤131.0m) = 0.309 → 0.31**; mixture mean **8.61**, sd **2.28**; E[4Q26 \| ≤131.0m] **5.93**; its §9 EPS row on ΔRevenue × 0.0014 once (**−$0.31**, not the 0.66-doubled figure) |
| **F01 `q1-27-nights-guide-above-82` and F02** | A08 | revision 2's own object: mean 8.70, sd 2.05, P(≥134.0m) 0.29, P(≤131.0m) 0.27 (the cushion-0.78 mixture) | **replace it with this file**; re-run `f01_model_v2.py` against it (its cushion 0.9 and the adopted 1.0 differ) |
| **X01 scenario MC** | A19 | — | read this file, not any log's prose |

### 4Q26 US hotel RevPAR — `questions/risk-q4-us-revpar-strong/datasets/r11_v2_joint_object.json`

0.90 × N(+2.795, 2.111) + 0.10 × N(+0.8, 1.8), both trend parameters solved so that both tails equal the 0.5 / 0.3 / 0.2 blend.

| quantity | value |
|---|---|
| mean / sd | **+2.60% / 2.17** |
| P(≥ +4.0) — R11 | **0.259** |
| P(+1.0 < x < +4.0) | 0.508 |
| P(≤ +1.0) — B15 | **0.232** |
| P(≤ 0) | 0.116 |
| E[RevPAR \| ≥ +4] / E[RevPAR \| ≤ +1] | **+5.31%** / −0.25% |

**B15 `bonus-q4-us-revpar-soft` (batch A18) must publish P(≤ +1.0) = 0.23, not 0.10**, and must replace its base-rate row "6 of 13 quarters ≤ +1%" with **"4 of 9"** on the parsed quarters (its 6 of 13 came from the withdrawn hand list). Its own §9 (−$2.5/share, EV −$0.25) becomes EV ≈ **−$0.6/share** at the new probability and stays immaterial. X01 should read the file rather than either log.

## 4. What the audit missed, and where it is itself wrong

1. **R15 has two Paris size-language sentences, not one.** The **1Q24** letter's EMEA section reads "While the impact of a single city for a limited duration is **insignificant** to the total nights booked in a region…" — the same construction as the 2Q24 line, in the *run-up* quarter. The audit's proximity search ran seven event words against a phrase list that contained "immaterial", "not material", "not meaningful" and "relatively small" but **not "insignificant"**, so it reported "exactly two hits, both the same 2Q24 sentence". There are two distinct sentences in two different quarters. This *strengthens* A12-09 rather than weakening it: both precedents sit in slots the World Cup has already spent, and the record becomes 2 of 5 in pre-event/own-quarter slots against 0 of 3 in post-event slots — a sharper contrast than 1 of 8 pooled.
2. **A12-14's replacement reason is wrong, and the audit could have caught it from its own batch.** `updated_time` is series metadata (A16-18); the ABNB ladder's disqualifiers are `volume_24h_fp` = 0.00, 80-cent spreads and an implied 4Q26 nobody holds. Ruled in §2.
3. **A12-16's conditional mean below the lower threshold is from the unrepaired mixture.** 6.16 is the revision-1 legs; the repaired object gives 5.93.
4. **A12-21's effective sample is quoted at the wrong horizon.** The same finding set (A12-15) establishes H = 100, at which the block count is 51 and the SE 4.5pp, not 48 and 4.7pp.
5. **A12-01 asks for one cushion and then uses a third value.** The finding text offers 1.2 or 0.78; the audit's own repaired mixture uses 1.0. 1.0 is right; the file now says why.
6. **The audit's R11 anchor is computed on revision 1's assumed H1.** Its "+3.1 on the published weights" uses the Q2 4.5–6.0 / Q3 4.5–6.0 grid from `r11_model.py`. On the **measured** months (Q1 +3.53, Q2 +5.60) the same weights give **+2.69**. Its election-week drag of −0.7 is also asserted rather than derived: one week at roughly −5% inside a 13-week quarter is −0.4. Both corrections are in the log and both push below the audit's number — see §5.
7. **A12-10 and the audit's own R11 paragraph disagree with each other.** The finding says R11 must adopt B15's 0.10; the independent number says "the mirror rises to ~0.16". Only a single fitted object resolves that, which is what revision 2 publishes.
8. **Not a finding, but worth recording:** the audit's four "what the log does well" sections are the most useful part of it for the memo, and three sentences from them are now load-bearing in the pitch — R10's threshold-and-level-cancel convention, R15's exhaustive negative result ("zero event contributions have ever been quantified in points or basis points"), and R16's framing of the disagreement between the lap arithmetic and management's Q4 delivery record.

## 5. Where revision 2 differs from the auditor by more than a rounding

Only **R11** is outside 2 points (0.26 against 0.29 — 3 points, inside the ~10-point band, but the largest gap in the batch and the only one worth naming).

The audit's route: anchor +3.1, AR +4.1, blend +3.6, then −0.7 election and −0.2 CR and no comp credit for +2.7, then **back up to +3.0** because "the AR long run (TE's FY27 +2.1%) is itself depressed by a June-2027 World Cup comparison that has nothing to do with 4Q26". Two of those inputs are superseded by measurement in this revision, and one is accepted but relocated:

- the anchor is **+2.69**, not +3.1, because the FY-implied leg now runs on the actual 2026 H1 months instead of the revision-1 assumption grid;
- the election-week drag is **−0.4**, not −0.7, on the one-week arithmetic;
- the World Cup argument for adding back 0.3 is **accepted**, but it belongs in the AR long run, where §7 prices it (lr 2.1 → 3.0 moves the final by +0.01), not as a free addition to the centre. Adding it to the centre and *also* leaving the long run at 2.25 would count it twice — the same shape of error as A12-04.

Net: centre +2.88 against the audit's +3.0, final 0.26 against 0.29. **The asymmetry that justifies staying below the auditor** is that every correction the audit itself demanded on this question (measure the base rate, measure the H1 months, stop double-counting the comp) moves the number down, and the only thing moving it up is a long-run assumption the sensitivity grid says is worth one point. Decision recorded in the R11 log §5 and §10.

R10 (0.10 vs 0.11) is a horizon difference; R15 agrees exactly; R16 (0.31 vs 0.30) is the pass-through re-basing to R01 revision 2.

## 6. Reproduction output

`A12-reproduce.py` is the audit's script saved verbatim — **no path bugs; no fixes were needed.** Run from the repository root with `py -3.13 -B docs/pitch-forecasts/audits/A12-reproduce.py`; exit code 0; full output in [`A12-reproduce.stdout.txt`](A12-reproduce.stdout.txt). Note that the script reads the *current* forecast JSONs, so its cross-question register block now prints the revision-2 numbers, not the revision-1 ones it was written against.

Load-bearing lines:

```
R10 / 1.  file rows 5400 | non-null 5188 (log claim 1: 5,188) | last 2026-09-11 = 118.2126
          beta(broad on DXY, 2024+) 0.5731 n=670 | s16 est 119.0239 | threshold 114.2630
R10 / 2.  business days net of federal holidays = 100   (the model hard-codes H = 105)
R10 / 3.  H=100 n=5088 P=0.1167 ... non-overlapping n=51 P=0.1961 se=0.0556
          H=105 n=5083 P=0.1218 ... non-overlapping n=49 P=0.1837 se=0.0553
          tail: n=619 mean=-0.0560 median=-0.0527   (log claim 7: 619 / -0.056 / -0.0527)
          years with ZERO sub-threshold windows: 10 of 21   (log claim 4 says 12 of 21)
R10 / 4.  quintile 1 (<=4.20%)  n=997  P 0.1103  mean FORWARD vol 0.0464  ratio 1.32
          band +/-1pp           n=2338 P 0.0723  mean FORWARD vol 0.0483  ratio 1.14
R10 / 5.  EUR/USD 16 Sep 1.1538 -> poll-interpolated at 4.85 months 1.1662 = +0.0107 log
          broad at beta -0.6 = -0.0064 ; the log uses -0.0042
          repaired blend 0.35*0.10 + 0.35*0.11 + 0.30*0.115 = 0.1080
R10 / 6.  142.9 per pt (B4 5.2)  dRev +368M  margin +1.48pp  EPS +0.515
          158.0 per pt (brief)   dRev +407M  margin +1.64pp  EPS +0.570
          the log publishes +400M, +1.6pp, +0.37 = 400 x 0.66 x 0.0014 -- 0.66 used twice
R11 / 1.  FY-implied mean 3.135 | AR one step 4.10 | adj -0.1 | centre 3.517 sd 1.676
          P(>=4.0) 0.3867  P(<=1.0) 0.0666  E[x|>=4] 5.18   (log: 0.3866 / 0.07 / 5.2)
          DROP the +0.8: centre 2.717 -> P(>=4.0) 0.2221  P(<=1.0) 0.1528
R11 / 2.  r11_model.py line 36 hist = [12, 3, 1.5, 2, 1, 1, 2, 3, 0, -0.5, -1, 0, 3.8, 5.2]
R11 / 4.  B15 mixture 0.9*N(3.7,1.6)+0.1*N(0.8,1.8): P(>=4) 0.3868 P(<=1) 0.0956 mean 3.41
R15       event discussions 8 | with a points figure 0 | with qualifying size language 1
          section 5 claims 1-(0.95)^2 = 0.0975, which uses 0.05/print, not the 0.10 it cites
          C05 revision 2 p_any_quantification = 0.28 ; R15 claim 10 quotes 0.27
R16       V1 (Q3 9.67, res_sd 1.4): P>=134 0.1227  P<=131 0.4206  mean 7.789
          C02 rev 1, cushion N(1.2,1.3)  -> blend 0.3035 / 0.2615
          C02 rev 1, cushion N(0.78,1.3) -> blend 0.2821 / 0.2759
          C02 rev 2, cushion N(1.2,1.3)  -> blend 0.2830 / 0.2836
          observed Q3->Q4 changes [-4.93, -1.52, 3.87, 1.03]  mean -0.39 sd 3.74 (n=4)
          Q3 centre 9.5 (R01 rev 2), res_sd 2.0 -> P>=134 0.1726  P<=131 0.4653
          +250M of FY27 revenue, costs held -> margin +1.02pp, EPS +0.350
Kalshi    >570m bid 0.63 ask 0.99 last 0.63 volume_fp 162.01 open_interest_fp 86.01 updated 2026-08-04
```

Three further reproductions were run for this response and are not in the audit's script:

```
r11_extract_lodging_monthly.py : months extracted 28 (2023-07 to 2026-07); rejected files 30; no month
                                 appears twice with a different value
r11_model_v2.py                : base rate 1 of 9 >= +4 (Laplace 0.182); 4 of 9 <= +1 (Laplace 0.455);
                                 complete quarters 1 of 6 and 3 of 6; Dec-2025 implied -2.20;
                                 comp gap 3Q25 -> 4Q25 +0.40; sd of sequential change 2.56 (n 8);
                                 blend 0.2594 / 0.2323; published mixture mean 2.595 sd 2.166
r16_model_v2.py                : re-run reproduces adopted_q4_states_v2.json byte for byte
```

## 7. Final table

| question | rev 1 | auditor | **rev 2** | anchor | \|final − anchor\| | EV $/share | material |
|---|---|---|---|---|---|---|---|
| **R10** risk-dollar-weakens | 0.09 | 0.11 | **0.10** (0.06–0.17) | 0.11 — constructed implied-vol distribution at 4.8%; NO tradable quote | 0.01 | **+$0.50** | no |
| **R11** risk-q4-us-revpar-strong | 0.38 | 0.29 | **0.26** (0.17–0.40) | 0.25 — CoStar/TE FY26 +4.4% implied 4Q26 of +2.69; NO market | 0.01 | **+$0.52** | no |
| **R15** risk-world-cup-quantified-small | 0.14 | 0.18 | **0.18** (0.10–0.30) | **null** — NO_EXTERNAL_ANCHOR (C05 0.28, R09 0.25, R08 0.15 are sibling comparisons) | n/a | **+$0.18** | no |
| **R16** risk-q4-nights-print-meets-street | 0.27 | 0.30 | **0.31** (0.19–0.44) | 0.50 — Bloomberg MODL 134.0m, 28 estimates, 2026-09-12; NO tradable market | 0.19 | **+$3.41** | **yes** |

Three of the four are immaterial and the memo should carry them as arithmetic, not as risk lines: FX (R10) belongs in the bridge, hotels (R11) belong in the alt-data monitor, and the World Cup disclosure (R15) belongs in one sentence of the thesis text. **R16 is the one that matters** — and it is now paired with B13 as the two tails of one distribution that is very nearly symmetric (0.307 / 0.309), which is the honest thing for the memo to say about a quarter that has not started.

**Adopted 4Q26 nights object:** mean **8.61**, sd **2.28**, P(≥134.0m) **0.307**, P(131.1–133.9m) **0.384**, P(≤131.0m) **0.309**, E[4Q26 \| ≥134.0m] **11.16%**.
**Must adopt it:** B13 (batch A17), F01 and F02 (batch A08), X01 (batch A19) — and R16, which does.
**Adopted 4Q26 US RevPAR object:** mean **+2.60**, sd **2.17**, P(≥+4.0) **0.259**, P(≤+1.0) **0.232**, E[· \| ≥+4] **+5.31**.
**Must adopt it:** B15 (batch A18) and X01 — and R11, which does.
