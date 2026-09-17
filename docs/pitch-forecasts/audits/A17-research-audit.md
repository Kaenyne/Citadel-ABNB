# Research audit — batch A17 (B11, B12, B13)

**B11 — 0.14: the right number, reached through inputs that are one revision and one convention out of date.**
The model replicates to the fourth decimal (my stdlib rebuild 0.1550 against the file's 0.15393; mean count 1.173 vs 1.169; E[15 Dec | Yes] $147.9 vs $148.05), and every feed fact, base rate and pool count in claims 2–5 re-reads exactly from the repo.
But the whole thing runs on **S02 revision 1** (0.24/0.14/0.10/0.52, 35/27 sessions, 29% vol, 3% drift): on revision 2 the model gives **0.1408** and the §9 marker moves from −$13.1 to **−$14.8**.
Two deeper errors then offset. The count rates are measured **on the feed** and are then thinned again by the feed's 0.85 capture (double-thinning: capture 1.0 gives 0.179), while the post-print branch means (0.15/0.5/0.7/1.1) sit above the feed's own print-window means by day-1 sign (0.00/0.55/0.83) and the exponential modulations lift the unconditional mean to **4.8 downgrades a year** against measured rates of 3.5 / 3.5 / 2.6 / 0. Fixing both: **0.137**.
The task-brief's stated concern — that B11 uses capture 1.0 against R12 revision 2's 0.85 — is **not correct**: B11's base capture is 0.85, the same value R12 revision 2 adopted. The two questions are coherent on capture; they are incoherent on S02, and both double-thin. Auditor comparison: **0.13** (0.06–0.23); the immaterial verdict stands.

**B12 — 0.50 literal / 0.38 material: the arithmetic survives revision 2; the regime structure does not survive its own record.**
Both readings replicate (my rebuild 0.5181 / 0.3890 against 0.517 / 0.388) and, re-run on F03 **revision 2**'s joint engine, land at 0.5086 / 0.3748 — so the headline is coherent with the run's current F03 to within a point, exactly as the A08 response states. The five letter sentences are verbatim-correct in the files.
The citations are not: the log's FY26 print distribution (mean 35.88, P(<35.5) 0.09), regime weights (T1 .20/T2 .22/T3 .30/T4 .08/T5 .10/T6 .10), F03 (d) 0.38, implied B12 0.35 and F04's 0.70 conditional are all **revision 1**; revision 2 gives 35.82 / 0.18, T1 .20/T2 .20/T3 .33/T4 .08/T5 .12/T6 .07, (d) 0.36, B12 0.51/0.37 and 0.673.
Two regimes carry the answer and neither has a February precedent. **T5** (0.10) is modelled as a *mutually exclusive alternative* to a numeric floor, but its only instance in the record — Mertz's "the modest guide down" — *accompanied* the FY24 T1 floor; as a language overlay instead of a regime, literal falls to **0.44** and material to **0.31**. **T2** ("at least 35.5%" on a 35.7 print) is the mid-2026 guidance form, never used in a February letter, and it carries the *entire* literal-vs-material wedge: at T2 = 0 the two readings coincide at 0.30.
§9 contradicts itself (headline "−0.3pp vs the team's line build"; the parenthetical computes 35.9 realised against the line build's 35.7, i.e. +0.2) and books −$5 / EV −$2.5 as additive without the "already inside S03" test that B11 applies to itself. Auditor comparison: **0.47 literal** (0.35–0.60), **0.36 material** (0.25–0.48); material as a line, but it needs the S03 netting sentence.

**B13 — 0.26: superseded. The run's adopted 4Q26 object names this question by id and says 0.31.**
`questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json` (written 10:11 today; R16 revision 2 published at 10:20) carries `must_adopt: ["B13 bonus-q4-nights-print-weak (batch A17): P(<=131.0m) = 0.309, not 0.26"]`. I rebuilt it from `r16_model_v2.py` in stdlib and get **0.3074** against the file's 0.3089 — the object is right and B13's 0.26 is a withdrawn parameter set (Q3 9.67, residual 1.4, C02 revision 1, cushion 1.2).
The log's own coherence claim fails even on revision-1 parameters. §3 and §5 assert "one 4Q26 object … 0.26 / 0.47 / 0.27, mean ≈ 8.3": the revision-1 mixture's mean is **8.79** and its middle mass **0.432**; the 0.47 is arithmetic on two hand-cut headlines (R16 revision 1 cut its model's 0.3032 to 0.27 while B13 used its 0.2622 raw). The adopted object's mean is 8.61.
§9 then compounds it: 3Q26 is booked at −0.9pt against a 9.9 centre when R01 revision 2 is N(9.5, 1.70) and the adopted object's E[Q3 | Yes] is 9.091 (**−0.41pt**, and reverse-causal besides — 3Q26 is known three months before this resolves); and the FY27 EPS line applies the brief's *held-cost margin* coefficient (0.66pp per pt) as a *dollar flow-through* ($220M × 0.66), which is neither the held case (100%, EPS −$0.34) nor the brief's flex case (which solves to 78%, −$0.26).
The good news is that the correction moves the memo the right way: on the adopted object the deltas are −2.18pt of 4Q26 nights, −$65M of 4Q26 revenue, −$241M of FY27 revenue, −1.01pp of FY27 margin and −$0.34 of FY27 EPS. Auditor comparison: **0.30** (0.19–0.43) — adopt 0.31 for coherence and note the one-point trim I would take on the V2 cushion.

Audit scope: read-only review of revision 1 of all three logs and their saved evidence, plus the repo files they cite and the revision-2 forecasts of S02, S04, R12, C02, C04, R01, R16, F01, F02, F03 and F04 for cross-question coherence, and the A08 and A12 audit responses. No network fetch was attempted; the yfinance, Kalshi, Polymarket and investing.com captures were read as saved. Neither prohibited directory was opened. `b11_model.py`, `b12_model.py` and `b13_model.py` all write into their own `datasets/` folders, so none was executed; all three were re-implemented from source (numpy for the working runs, stdlib for the shipped script) and reproduce to ±0.005. Below, `log`, `model` and `forecast` mean `research-log.md`, `datasets/b1N_model.py` and `forecasts/2026-09-17-forecast.json` under the question's folder.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A17-01 | B13 | critical | `forecast.final.p`; `log:3`, `log:76–77`; `model:13–33` | The published **0.26** is computed on a parameter set the run has since **withdrawn**. The adopted 4Q26 object (`../risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json`, A12 revision 2) replaces Q3 N(9.67, 1.70) with N(9.5, 1.70), the V1 residual sd 1.4 with 2.0, the C02 revision-1 vector (.21/.19/.39/.17/.04) with revision 2 (.18/.17/.30/.31/.04) and the V2 cushion N(1.2, 1.3) with N(1.0, 1.3). Its `must_adopt` list names this question: "B13 bonus-q4-nights-print-weak (batch A17): P(<=131.0m) = 0.309, **not 0.26**". | Rebuilt `r16_model_v2.py` in stdlib at 120k draws: **P(≤131.0m) 0.3074**, P(≥134.0m) 0.3054, mean 8.614, sd 2.276, E[Q4 \| Yes] 5.922, E[Q3 \| Yes] 9.091 — the file's 0.3089 / 0.307 / 8.6122 / 2.2782 / 5.925 / 9.091 to Monte-Carlo error. R16's own revision-2 forecast (written 10:20 today) publishes 0.31 and carries the same `adopted_object` block. | Set `final.p = 0.31`, CI **0.19–0.43**, and rewrite §5–6 against the adopted object (V1 0.451 / V2 0.259 / V3 0.025, blend 0.309). Every §9 delta moves with it (A17-14, A17-15). |
| A17-02 | B13 | critical | `log:3`; `log:77` coherence; `log:83` "One 4Q26 object for X01" | The "one 4Q26 object" claim — the log's stated reason for not re-litigating anything — was **false when written**. §5/§6 publish "0.26 / 0.47 / 0.27, mean ≈ 8.3". No model in the run produces that triple: R16 revision 1 hand-cut its blend from 0.3032 to 0.27 while B13 used its own blend 0.2622 raw, so the two tails came from two different numbers, and the 0.47 middle is 1 − 0.26 − 0.27 rather than anything computed. | Rebuilt the revision-1 mixture: V1 0.4225 / V2 0.1568 / V3 0.0240 → blend **0.2628** (file 0.2622) with **mean 8.789, sd 2.090** and P(≥134.0m) **0.3054**, i.e. middle mass **0.432**. `r16_views.csv` row "blend (0.5, 0.3, 0.2)" = 0.3032 against R16 revision 1's published 0.27; `adopted_q4_states_v2.json.superseded.rev1_model_blend_rows` records both (0.3032 / 0.2622). | Quote the adopted object's triple **0.309 / 0.384 / 0.307, mean 8.61, sd 2.28** and delete the 8.3. If the response keeps a mean in the log, it must be a computed mixture mean, not the V1 mean or a guess between the views. |
| A17-03 | B11 | major | `model:17,37–38` `capture=0.85`; `log:39` claim 7; `log:74` | The counts are thinned **twice**. `pre_mu` and `post_mu` are calibrated on `downgrade_base_rates.json`, which counts rows in the yfinance/Benzinga feed — they already embody whatever the feed drops. Thinning them again by 0.85 prices the feed's gaps a second time. (The same construction is in R12 revision 2, which applies 0.85 to rates measured on the same feed; whichever way the run resolves it, it must resolve it the same way in both.) | Re-ran on revision-2 S02 parameters: capture 0.85 → **0.1408**, capture 1.0 → **0.1792**. The rates being thinned are the feed's own: `feed_downgrades_all.csv` is `Action == "down"` rows from `D_analyst_actions_2026-09-12.csv`, whose `source` column reads "yfinance Ticker('ABNB').upgrades\_downgrades (Yahoo Finance / Benzinga feed)". | Either drop the capture term (the resolving object and the calibration sample are the same feed) or state that `post_mu` is a *true-world* rate and show the grossing-up. Combined with A17-04 the corrected model is **0.137** — the published 0.14 by a different route. |
| A17-04 | B11 | major | `model:17` `post_mu=(0.15,0.5,0.7,1.1)`, `k_pre=k_post=3.0`, `beta_d1=0.06`; `log:80` | The model's unconditional mean is above every base rate it is compared with, and the gap is entirely the exponential modulations. `k_pre = k_post = 3.0` is calibrated so a −10% move gives the measured ×1.35 lift, which is right as a *shape*, but `pre_mu`/`post_mu` are then set at the *unconditional* rates, so E[exp(−3·min(r,0))] > 1 inflates the level. The decel-below post mean 1.1 also sits 1.33× the feed's own post-print mean for day-1 ≤ −5% prints (0.833). | Re-ran with `k_pre = k_post = beta_d1 = 0`: mean 1.173 → **0.938**, P 0.1550 → **0.1075** — the 2021+ 90-day base rate 0.1063 almost exactly. With the modulations the model runs at **4.8 downgrades a year** (1.173 per 89 days, after capture) against measured 3.51 (2021+), 3.51 (2023+), 2.59 (2024+), 0 (trailing twelve months) and a print-shaped-window mean of 0.739 per 89 days = **3.03/yr**. Substituting the feed's print-window post means by day-1 sign (0.02 / 0.55 / 0.55 / 0.83) on revision-2 parameters: **0.1064**. | Either re-centre `pre_mu`/`post_mu` so the unconditional mean matches a named base rate, or say in §5 that the decomposition deliberately runs 1.6× the print-shaped-window rate and why. The honest corrected band on revision-2 parameters is **0.12–0.14**. |
| A17-05 | B11 | major | `model:13–15` `S02` dict; `log:40` claim 8; `log:127`; `forecast.model.structure` | The entire simulation uses **S02 revision 1**. S02 revision 2 (`../close-15dec-2026/datasets/abnb_path_mixture_v2.py:24–36`) uses print weights **0.32 / 0.10 / 0.13 / 0.45**, post-print drifts **−1.5 / −0.5 / −0.5 / −1.0**, **36** pre / **26** post sessions, **30%** background vol, **6.97%** total drift and a within-branch day-1 sd solved to S01's unconditional 9.5%. Every downstream statement inherits the error: §9's "0.52 unconditional", the −$13.1 marker, and the monitoring rows keyed to the revision-1 branch probabilities. | Re-ran parameter-for-parameter: revision-2 parameters give **P 0.1408**, mean 1.096, **E[15 Dec \| Yes] $150.5 vs $165.5 = −$14.8**. The variance identity on the revision-2 weights returns within-branch sd **8.451**, matching `abnb_path_mixture_v2.py`'s solved value. | Re-run on revision 2. The point barely moves (0.154 → 0.141, which is *closer* to the published 0.14), but the marker becomes **−$14.8** (EV −$2.1) and `P(decel-guide-below)` becomes 0.45, not 0.52. |
| A17-06 | B11 | major | `log:81–84`; `forecast.estimates.anchor` | The "anchor" is one of the log's own base-rate families. `anchor_estimate 0.09` is the print-shaped-window P(≥3) = 0.087, which also appears inside `base_rate_detail` as `print_windows_all`. So `final_minus_anchor = +0.05` measures the final against a component of itself, and there is no `NOT_INDEPENDENTLY_DERIVED` flag — which R12 revision 2 does carry for exactly this situation. | `downgrade_base_rates.json` `print_windows_P(>=3)_all` = 0.08696; `forecast.estimates.base_rate_detail.print_windows_all` = 0.087; `estimates.anchor` = 0.09. R12 revision 2 `forecast.estimates.anchor_independent: false` with the flag spelled out. | Keep 0.09 as the anchor but set `anchor_independent: false` and say in §5 that no independent anchor exists for this object (the Kalshi/Polymarket scan in claim 11 already establishes that). |
| A17-07 | B11 | major | `log:28` conventions (1) and (4); `log:39` claim 7 | The conventions contradict each other on the one firm that matters. Convention (4) puts "Phillip Securities … outside the feed"; claim 7 says Phillip **has a row in the feed** (12 Nov 2024) and it was the *August 2026 action* the feed dropped. As written, convention (4) would exclude a Phillip downgrade in the window even if the feed carried it. | `feed_downgrades_all.csv` row 18: `2024-11-12, Phillip Securities, Neutral, Reduce`. The saved WebFetch (`sources/web_search_log.md` item 2) dates the un-captured action 11 Aug 2026. | Rewrite convention (4) as "actions the feed does not carry do not count, whoever the firm" and drop Phillip from the excluded-firm list; Weiss (no feed row at all) stays. This is the resolution sentence the 15 Dec pull will actually be run against. |
| A17-08 | B11 | major | `log:89`, `log:118`; `forecast.count_distribution.p_given_day1_le_minus8`; `log:108` pre-mortem (1) | The model's headline mechanism has **no positive observation**. It prices P(Yes \| day-1 ≤ −8%) at 0.30 and ≤ −5% at 0.26, and the memo is told to re-centre on that on 6 November. In the feed's own record, **0 of the 6 print windows around a day-1 ≤ −5% print ever reached 3 downgrades**; both ≥3 windows followed *small* day-1 moves (Feb 2022 +3.6%, Nov 2023 −3.3%). The 2023 wave came after a "moderate" guide, not after a crash. | Recomputed from `feed_downgrades_all.csv` × `abnb_earnings_reactions.csv` on the log's own −49/+39-day window: up ≥ +5% n 6 mean 0.167 P(≥3) 0.000; small n 11 mean 0.909 P(≥3) **0.182**; down ≤ −5% n 6 mean 1.000 P(≥3) **0.000**. `downgrade_base_rates.json` `print_windows_P(>=3)_by_day1_sign` carries the same three numbers and the log does not quote them. | Quote the by-sign P(≥3) row in claim 4 and say plainly that the conditional ladder in §6/§8 is a model output with n 6 and zero supporting events, not a base rate. The honest monitoring line is "the bucket language matters more than the day-1 move", which is what both historical waves say. |
| A17-09 | B12 | major | `model:15` `T5=0.10`; `log:34` claim 2; `log:68` | T5 ("explicit down / investment year") is modelled as a regime **mutually exclusive** with a numeric floor, which is the opposite of how its only historical instance occurred. Claim 2's own evidence is Mertz calling the **FY24 T1 floor** "the modest guide down … a modest amount of margin compression this year" — the language came *with* the number, not instead of it. As a separate 10-point regime it adds Yes mass that the record does not support (explicit down language in a letter: 0 of 5, Laplace 0.14). | Re-ran with T5 pushed to 0.02 (standalone down-language with no number) and the 0.08 redistributed to T3/T6: literal 0.518 → **0.438**, material 0.389 → **0.309**. On F03 revision 2's joint engine the same change gives **0.425 / 0.292**. `05_statements.csv` V007 (2024-05-30, Bernstein) and V011 (2024-09-10, Goldman) both post-date and gloss the Feb 2024 letter. | Model T5 as a language overlay on T1 (and, at low weight, on T3) rather than an alternative to it, or justify a standalone explicit-down regime against 0 of 5. Worth **−0.07 literal / −0.08 material**. |
| A17-10 | B12 | major | `model:15` `T2=0.22`; `log:67` | T2 — "a numeric floor at the print rounded down to the 0.5 grid" — has **never appeared in a February letter**. The three February numeric sentences are two ~190bp haircuts (FY24, FY25) and a qualitative "stable" (FY26); "at least 35.5%" is the *mid-2026* form. T2 is also the only thing separating the two published readings. | Re-ran the model: T2 halved to 0.11 gives literal **0.409** / material 0.345; T2 = 0 gives **0.300 / 0.300** — the readings coincide. Verified the letter forms by regex over `data/raw/letters/4Q21…4Q25`: the 4Q25 letter's only FY sentence is "For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year…" (plus a separate *quarterly* "approximately flat" line). | Keep T2 but say in §4 that it is a transplant from the November form with n 0 in February, and put its weight in §7 as the headline sensitivity (it is worth 0.30–0.52 on the literal reading, a wider band than any other assumption in the log). |
| A17-11 | B12 | major | `log:36` claim 4, `log:37` claim 5, `log:40` claim 8; `forecast.estimates.fy26_print_distribution_from_f03`, `regime_weights_from_f03`, `reconciliation_with_f03` | Every F03/F04 figure is **revision 1**. F03 revision 2 (`fy27-margin-guide/forecasts/…json`, `datasets/f03_f04_joint_v2.py`) uses FY26 print **N(35.72, 0.58)** with C04 revision 2's 50% floor-defence rule (realised mean 35.82, **P(A<35.5) 0.18**, not 35.88 / 0.09), realised regime weights **T1 .20 / T2 .20 / T3 .33 / T4 .08 / T5 .12 / T6 .07**, option (d) **0.36** (not 0.38), and publishes B12 **literal 0.5086 / material 0.3748** (not an implied 0.35). | Rebuilt `f03_f04_joint_v2.py`: literal 0.5086, material 0.3748, regime weights {T1 .191, T2 .205, T3 .339, T4 .079, T5 .115, T6 .071}, FY26 print mean 35.8203 sd 0.4941 P(<35.5) 0.1766 — identical to the A08 response's line 305. Swapping B12's own engine onto the revision-2 print gives literal 0.5183 / material 0.3878, i.e. the FY26 level genuinely does not matter. | Re-cite revision 2 throughout and delete the "F03's implied B12 0.35" reconciliation — F03 revision 2 computes B12 directly and agrees with it. **No change to the headline**; this is a citation repair, and it is the one that stops a judge finding two different F03s in one deck. |
| A17-12 | B12 | major | `log:124` FY27 margin row; `forecast.impact.margin_fy27_pp` | The row contradicts its own derivation. The headline books **−0.3pp versus the team's line build**; the parenthetical computes E[floor \| Yes] ≈ 34.9, realised = floor + 60–140bp → centre **35.9**, and then says "the line build's 35.7 is roughly what a Yes delivers" — which is **+0.2pp**, not −0.3. The −0.9pp versus the Street is the only defensible number in the row, and it is the one the stock line uses. | Read the row against `docs/margin-build/notes/40_line_build.md` (FY27 35.7%) and `23_vs_consensus.csv` (Street 36.45%). The arithmetic 35.9 − 35.7 = +0.2 is in the cell itself. | Book **0.0 / +0.2pp vs the team** and **−0.9pp vs the Street**, and label which base the EPS and stock lines use (they use the Street). The impact table is the one part of the log a Citadel judge reads line by line. |
| A17-13 | B12 | major | `log:126–128`; `forecast.impact.stock_usd_per_share`, `ev_stock_usd_per_share`, `material` | −$5 and EV −$2.5 are booked as a standalone material line with no test of whether S03 already prices it. S02/S03 revision 2 carries a February event with branch means +2.5 / +1.0 / +0.5 / −0.5 at sd 9.0 — the 11 Feb reaction to the letter that contains this very sentence. B11 §9 makes exactly the right distinction ("already counted in S01/S02/C01 and not additive") and B12 does not. Claim 9's own evidence cuts the same way: the Feb 2025 letter cut the floor 190bp and the stock rose **+14.4%**. | S02 revision 2 `PARAMS.scen[*]["feb"]` = 2.5 / 1.0 / 0.5 / −0.5, `feb_sd` 9.0; `abnb_earnings_reactions.csv` 4Q24 `abnb_1d_pct` +14.4, 4Q23 −1.7. | Split the line the way B11 does: an **additive** Street-estimate effect (−$140M of FY27 EBITDA → ≈ −$4 at a constant multiple, EV ≈ −$2 — still material) and a **non-additive** reaction marker owned by S03. Say explicitly that the day-1 sign is not the sign of the estimate cut. |
| A17-14 | B13 | major | `log:126` FY27 EPS; `forecast.impact.eps_fy27_usd` | The brief's coefficient is used in two incompatible ways in one table. "$220M × 0.66 = $145M EBITDA" treats **0.66 as a dollar flow-through**; two rows above, the same 0.66 is used as the **held-cost margin coefficient** (0.66pp per 1pt of revenue). Held costs mean the revenue shortfall drops straight through: ΔEBITDA = ΔR, and the brief's *flex* case solves to 78%, not 66%. The published −$0.20 is below both. | Identity check on the Street base (R 15,829, margin 36.45%): ΔR = 158 with costs held gives margin 35.81% = −0.64pp ✓ (the brief's 0.66); solving the flex 0.42pp back out gives ΔE = 124 = **78%** of ΔR. On the adopted object's ΔQ4 = −2.18pt: FY27 revenue **−$241M**, FY27 margin **−1.01pp**, FY27 EPS **−$0.337** (held) or **−$0.263** (flex). | Use one convention. On held costs: 4Q26 nights **−2.18pt**, 4Q26 revenue **−$65M**, FY27 revenue **−$241M**, FY26 margin **−0.29pp**, FY27 margin **−1.01pp**, FY27 EPS **−$0.34**. The correction runs *toward* the short case, so the memo gains from it. |
| A17-15 | B13 | major | `log:119` 3Q26 row; `forecast.impact.nights_3q26_pts` | Two errors in one cell. (i) The −0.9pt is E[Q3 \| Yes] 9.0 against **9.9**, but the run's adopted 3Q26 object is R01 revision 2 **N(9.5, 1.70)**, and the adopted 4Q26 object's own `q3_given_le_131` is **9.091** → **−0.41pt**. (ii) The row is reverse-causal and, by the resolution date, moot: 3Q26 prints on 5 Nov 2026 and B13 resolves ~11 Feb 2027, so a weak Q4 cannot change a known Q3 — it only selects worlds in which Q3 was already lower. | `adopted_q4_states_v2.json.conditional_means_pct`: `q3_given_le_131_0m` 9.091, `corr_q3_q4` 0.192; my rebuild returns 9.091 with E[Q3] 9.494. `../risk-q3-nights-meets-guide/` revision 2 adopts N(9.5, 1.70). | Restate as **−0.4pt, selection not impact**, and label it "(indirect)" the way B11 §9 labels its own indirect rows. |
| A17-16 | B13 | major | `log:72` base_rate_estimate 0.18; `forecast.estimates.views.V2_used` 0.18 vs `V2_decomposition` 0.156; `log:77` | The three "independent estimates" are not three estimates, and one of them is not the number used. §5 sets `base_rate_estimate` = 0.18 by hand-cutting V2 between its cushion-1.2 value (0.156) and its cushion-0.6 value (0.227) — but the published 0.262 blend uses **0.1558**. Had 0.18 been used the blend would be 0.2695. More broadly the "base rate" (V2) and the "decomposition" (V1) are two legs of the same published blend and the "anchor" (V3) is the third, so `final_minus_anchor` compares the blend with one of its own components. | 0.5 × 0.4211 + 0.3 × 0.1558 + 0.2 × 0.0245 = **0.2622** = `b13_views.csv` "blend (0.5, 0.3, 0.2)". With V2 = 0.18 the same blend gives 0.2695. `forecast.estimates.views` lists both `V2_guide_route_cushion_1.2: 0.156` and `V2_used: 0.18`. | Pick one V2 (the adopted object settles it at cushion N(1.0, 1.3) → 0.2585) and say in §5 that this question has **no independent anchor**, as R16 revision 2 now does. Do not present the blend's own legs as three independent estimates. |
| A17-17 | B11 | minor | `log:96` §7 row 1; `log:80` | The row labels `pre_mu = 0.35` "the 2023+ off-print rate". It is not: the 2023+ rate is 3.51/yr and claim 4 puts the off-print share at 0.55, so the off-print rate over the 49-day pre-print block is **0.26**. 0.35 sits between the off-print rate and the all-window rate (0.47) and is a judgement, not a measurement. | `downgrade_base_rates.json` `2023-01-01.events_per_year` 3.5068, `share_within_30d_after_print` 0.45. 3.5068 × 0.55 × 49/365 = 0.259. Re-ran at 0.26 on revision-2 parameters: **P 0.1271**. | Relabel the row and add 0.26 as the measured-off-print sensitivity (0.127). The "0.20 (trailing-12m drought)" and "0.55 (2021+ all-window)" rows are correctly labelled. |
| A17-18 | B11 | minor | `model:35` `np.exp(-k_post*np.minimum(r_post,0.0))`; `log:36` claim 4 | `k_post = 3.0` is calibrated on claim 4's **39-day post-print move**, which in the data *includes the reaction day* ("post-print counts … by the 39-day price move: ≤ −8% mean 1.00"). In the model `r_post` is the drift-plus-diffusion from 6 Nov, i.e. it **excludes** day 1, which enters only through `beta_d1` as a deviation from the branch mean. A −10% print day therefore raises the post-print rate only through the branch index, not through the price channel the coefficient was measured on. | Read `model:27–28,35`: `day1` is drawn separately and `r_post = log1p(post_drift) + diff(sessions_post)`. `downgrade_base_rates.json` `print_windows_post_by_post39d_move` is keyed on `post39d_move`, which the base-rate script measures from the reaction close forward — the claim's own wording ("reaction day to +39 calendar days") confirms day 1 is inside. | Either apply `k_post` to `r_day1 + r_post` or re-measure the coefficient ex-day-1. The direction is ambiguous (it removes a lift but the branch means already carry the day-1 signal), so this is a specification note, not a number change. |
| A17-19 | B11 | minor | `log:134` stock row; `forecast.impact.stock_usd_per_share` −1.5 | The direct effect is asserted against the source cited for it. The 09 note finding quoted in the same cell is that "analyst actions outside prints produce abnormal returns indistinguishable from zero"; the cell then assumes −0.3% per downgrade day. The arithmetic is right (3 × 0.3% × $167.51 = $1.51) but the coefficient is an unsourced overlay on a null result. | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §1 items 6, 9 as quoted in claim 9; `D_positioning_summary.csv` "Buy share vs forward 3m excess return r 0.128, n 66, p 0.30". | Say "the measured effect is zero; −$1.5 is a conservative overlay for the one exception in the record (Morgan Stanley, 7 Dec 2022, −5%)". EV −$0.2 and the immaterial verdict are unchanged either way. |
| A17-20 | B12 | minor | `log:33` claim 1 "5 of 5 since 4Q21" | The reference class is cut at 4Q21 without saying why. The **4Q20 letter (Feb 2021)** also carries forward-looking full-year margin language — "we will be focused on making continued progress in expanding our Adjusted EBITDA margin as we scale", plus "we expect our Adjusted EBITDA margins to be lower in the first half of 2021 than the second half". Read as a February FY sentence it is a T4/expand form and a No, taking the base rate to **2 of 6 = 0.333** (Laplace 0.375). | Regex over `data/raw/letters/4Q20_d147144dex991.htm` returns both sentences verbatim. `feb_fy_margin_sentences.csv` has no 4Q20 row. | Either add the 4Q20 row with its reason for exclusion (first post-IPO letter, no formal guidance regime) or carry 2 of 6 alongside 2 of 5 in §5. Worth ≈ −0.02 on the base-rate leg. |
| A17-21 | B12 | minor | `log:40` claim 8 | F04 figures are revision 1. The claim quotes "P 0.55 … conditional on F03's (d) 0.70". F04's joint revision-2 run gives unconditional **0.5805** with conditionals a 0.398 / b 0.463 / c 0.564 / **d 0.673** / e 0.531 (F04's published headline stayed 0.55). | `f04_v2_conditionals.csv` via the A08 response line 305; `fy27-sm-share-above-219/forecasts/2026-09-17-forecast.json` revision 2 `final.p` 0.55. | Cite 0.673 and note the published-vs-model gap. The claim is not load-bearing for the number. |
| A17-22 | B12 | minor | `log:127`; `forecast.impact.ev_stock_usd_per_share_material_reading` −2.7 | "material: 0.38 × −$7" introduces a −$7 that appears nowhere else. The gap ladder in the row above prices −$2 / −$5 / −$9 by gap size and the literal mean is −$5; −$7 is presumably the mean over the material subset (gap ≥ 50bp) but it is never computed. | The literal ladder reconciles: with `share_lt_50bp` 0.25 and P(gap > 1.5pp) ≈ 0.20, 0.25(−2) + 0.55(−5) + 0.20(−9) = **−5.05** ✓. No equivalent calculation exists for the material subset. | Show the material-subset mean from the same draws (E[gap \| material Yes] ≈ 1.4pp) or drop the second EV. |
| A17-23 | B13 | minor | `forecast.estimates.anchor` 0.05 vs `anchor_value` 0.02 vs `final_minus_anchor` 0.24; `log:74–75` | Two anchors in one block and the gap measured off the one the log says it does not use. §5 says the anchor is "gap-adjusted to 0.05"; `anchor_value` is 0.02 and `final_minus_anchor` 0.24 = 0.26 − 0.02. | Read the JSON block; `log:77` states both ("+0.24 vs the raw 0.02; +0.21 vs the gap-adjusted 0.05"). | Publish one anchor. On the adopted object the gap is 0.31 − 0.05 = **+0.26**, and the reason is the same either way (the Street bar is a pre-reset 2Q26 carry-forward). |
| A17-24 | B13 | minor | `log:127` stock row; `forecast.impact.stock_usd_per_share` −10 | The two components are one move. −$6.9 is 1.4pt of FY27 nights at the brief's **$4.90 joint solve**, which already embeds the multiple contraction; the added "≈ −$3 Feb-print reaction" is the market *arriving* at that level. The row says "net of what S03 already carries" for the −$3 but does not net the joint-solve leg. | Brief §Sensitivities: "1pt of FY27 nights ≈ $4.90/share (joint solve) **or** $1.50 (fixed multiple)" — the two are alternatives, and the joint solve is the post-repricing level. On the corrected 1.53pt: 1.53 × 4.90 = **−$7.5**. | Book **−$7.5** (joint solve) with the February reaction named as the mechanism rather than an addition. EV = 0.31 × −7.5 = **−$2.3** — still material, still the mirror of R16. |
| A17-25 | B13 | minor | `log:36` claim 6; `model:30–33` V3 | V3 uses the **cross-sectional dispersion of 28 analyst estimates** as the predictive sd of the print, and ignores the one measured fact in the same claim: since 2023 the actual has beaten the at-print bar by **+0.9% on average (sd 1.5%, ≥ 0 in 10 of 12)**. A view built from that record would be centred at ≈135.2m with sd ≈2.0m, not at 134.0m with sd 1.5m. | Read `E_street_sign_history.csv` via claim 6; N(135.2, 2.0) gives P(≤131.0m) ≈ **0.02**, against V3's 0.0245 — the correction is immaterial *here* but it is not immaterial for R16, where the same V3 carries 0.2 weight on the upper tail. | Say in §4 that V3 is the Street's dispersion, not a forecast, and that the measured at-print error would shift it up. Keep the weight; the adopted object already does. |

## B11 — what the log does well and should keep

The tape work is exact and should survive intact. I re-read the feed pull: **469 rows**, action mix main 350 / init 38 / reit 35 / up 26 / down 20, **20 downgrades all to Hold or Sell**, by year 2021 2 / 2022 5 / 2023 6 / 2024 5 / 2025 2 / 2026 0 — every figure in claim 2 matches, as does the firm-by-firm list and the grade buckets. The **474 days** since Truist's 30 May 2025 downgrade is right and is correctly identified as the longest gap in the series (the previous maximum is 345 days, Jan–Dec 2021). The same-calendar counts (2021 0 / 2022 2 / 2023 5 / 2024 1 / 2025 0) reproduce exactly, including the fact that RBC's 16 Dec 2021 downgrade falls one day outside the window. `analyst_price_targets` (mean $182.975, median $185, high $220, low $125, spot $167.51) matches the saved JSON to the cent, and the 22 Buy / 11 Hold / 2 Sell pool and the 59.46% Buy share reproduce from `D_positioning_summary.csv`.

Every base rate reproduces from scratch: 90-day rolling windows 2021+ n 1995 mean 0.860 P(≥3) **0.1063**, 2023+ n 1265 mean 0.874 P(≥3) **0.0822**, 2024+ n 900 mean 0.650 P(≥3) **0.0056** (max 3); print-shaped (−49/+39-day) counts `0,0,0,0,3,0,0,2,1,0,0,4,1,2,1,1,0,2,0,0,0,0,0`, mean **0.739**, P(≥3) **2 of 23 = 0.087**, 2023+ **1 of 15 = 0.067**; price-conditioned windows after a 21-session fall ≤ −10% mean 1.175 P(≥3) **0.164**. That is four genuinely different reference classes, computed correctly, spanning 0.006–0.20 — the best base-rate section in the batch, and §5's refusal to pick one of them is right.

The structural argument is the one the memo should use: downgrades are **not** a print event the way upgrades are (20–25% within 5–10 days of a print against 38–48% for upgrades; 45% within 30 days *after*), they lag the price by two to five weeks, and the 2Q24 precedent — a −13.4% day-1 with 19 target cuts and a single rating downgrade — is exactly why the decel-below branch is 0.23 and not 0.5. Convention (2)'s exclusion of `main` rows with target cuts is the right reading of "rating downgrades" and correctly hands that object to S04. The pre-mortem is honest in both directions, and item (3) is the strongest sentence in the log. The §9 verdict — a marker of the base-case branch, immaterial as a standalone line, fold it into the narrative — is correct and should be kept verbatim.

## B12 — what the log does well and should keep

The letter work is the best-sourced thing in the batch and it is verbatim-correct. I extracted the Outlook sections of all five February letters by regex and every sentence in claim 1 matches the file, word for word, including the FY24 "at least 35%, providing us flexibility to invest in incremental growth opportunities" and the FY25 "$200 million to $250 million towards launching and scaling new businesses … Adjusted EBITDA Margin of at least 34.5%—maintaining our strong track record". The prior-actual levels (26.57, 34.56, 36.84, 36.40, 35.10) and the haircuts (−184bp, −190bp, 0) reconcile with `05_mgmt_statements_v2.md` line 125's "February 2027 FY27 floor: FY26 actual minus 0–190bp (n 3: −184, −190, 0)". Every statement id in claims 2 and 7 (V004, V007, V011, S164, S179, V017, V018, V023) exists in `05_statements.csv` with the dates and speakers the log gives.

Publishing **both readings** with the resolution consequences spelled out is the right call and should be kept. The question's title ("guide FY27 margin down year over year") and its resolution sentence ("Yes if the FY27 margin floor/point is below the FY26 reported margin") are not the same object, the difference is worth 12 points, and §0b resolves the ambiguity by stating a convention rather than changing the question — exactly what brief rule 3 asks. The observation that the number is **flat across FY26-print levels** (0.52 in every bucket) is real and load-bearing: I reproduce it on both the revision-1 and the revision-2 print distribution (0.5181 vs 0.5183 despite P(A<35.5) doubling from 0.09 to 0.18), and it is the reason the 5 Nov FY26 sentence does *not* move this question. The decision in §4 not to re-weight F03's regimes for a second opinion on the same five sentences is the right discipline. And claim 9's Feb 2025 precedent — a 190bp haircut that produced a **+14.4%** day — is the single most useful fact here for a short memo that wants to lean on "investment year", and it belongs in the memo next to the probability.

## B13 — what the log does well and should keep

The repo arithmetic is exact. The threshold conversion is right to four decimals (131.0 / 121.9 − 1 = **7.4651%**, 134.0 → 9.9262%) and the convention that the level governs and the title's "+7.5%" is a label is the correct reading. Claim 3's Q3→Q4 transitions reproduce from `abnb_driver_history_quarterly.csv` (3Q22 25.094 → 4Q22 20.163 = −4.93; 3Q23 13.541 → 12.018 = −1.52; 3Q24 8.481 → 12.348 = +3.87; 3Q25 8.795 → 9.820 = +1.03; mean −0.39), and the framing — a ≤7.5% print needs a −2.0 to −2.4 step, which 2 of 4 observed steps exceed — is the right way to make a four-observation series useful. Claim 2's RNPL module rows are exact (`rnpl_nights_module.csv` 4Q26 base 7.61 / 131.2m, bear 6.58 / 129.9m, bull 8.35 / 132.1m), and the observation that the module's **base** sits 0.2m above the threshold while its **bear** sits 1.1m below is the most decision-relevant sentence in the log. Claim 5 matches `E_street_distribution_vs_team.csv` exactly (28 estimates, low 130.0m = +6.645%, mean 134.0m = +9.926%, high 136.0m = +11.567%).

The Kalshi verdict is right and well-argued: the KXABNBA FY26 ladder implies 4Q26 ≈ 120–123m, which is inconsistent with the KXABNB Q3 ladder in the same snapshot and with every repo model, so zero weight is the correct treatment (and R16, F01 and C02 reached it independently). The §4 hypothesis table is genuinely adversarial — it kills the "Street low estimate proves the tail" argument, refuses to treat the short case as a probability-weighted scenario, and keeps the guide route as the outside view at 0.3 rather than dismissing it. The conditional ladder on the 5 Nov bucket ("mid single / moderate" → ~0.60, "high single digits" → ~0.12) is the most useful output in the log because it turns 5 November into a scorable test, and §8's re-centring rule should be executed exactly as written. The pre-mortem's closing asymmetry — "the 0.26 should be quoted as 'one in four', not as the base case" — is the right instruction to the memo, and survives at 0.31 as "roughly one in three".

## Independent numbers

**B11 — P(Yes) = 0.13**, judgmental 80% interval 0.06–0.23.
Derivation: rebuild the published simulation on the run's **current** inputs — S02 revision 2 (weights 0.32/0.10/0.13/0.45, post drifts −1.5/−0.5/−0.5/−1.0, 36 pre / 26 post sessions, 30% background, 6.97% drift, within-branch day-1 sd 8.451) — which gives **0.1408**; then apply the two corrections that run in opposite directions: drop the double-thinning, because `pre_mu` and `post_mu` are calibrated on feed rows and the feed is the resolving object (→ 0.1792), and replace the post-print branch means with the feed's own print-window means by day-1 sign, 0.02 / 0.55 / 0.55 / 0.83 (→ **0.1374**); setting the pre-print block at the measured 2023+ off-print 49-day rate of 0.26 as well gives **0.1207**. Corrected model band **0.12–0.14**.
Check it against base rates built the same way: print-shaped windows 2 of 23 = 0.087 (1 of 15 = 0.067 since 2023), 90-day 2021+ 0.106, same-calendar 1 of 5 = 0.20, windows after a 21-session fall ≤ −10% 0.164 — centre ≈ 0.11, and the trailing-twelve-month rate is zero against a 22-firm Buy pool at a series-high Buy share. Weighting the corrected model 0.6 and the base rates 0.4 gives **0.127 → 0.13**. Impact unchanged in substance: direct effect ≈ **−$1.5/share** (and the cited evidence says zero), **EV ≈ −$0.2 — immaterial as a standalone line**; as a marker of the decel-guide-below branch, E[15 Dec \| Yes] **$150.5 vs $165.5 = −$14.8** on revision-2 parameters (EV −$1.9), explicitly not additive with S01/S02/C01.

**B12 — P(Yes) = 0.47 literal** (0.35–0.60); **0.36 material** (0.25–0.48).
Derivation: the decomposition is F03 revision 2's joint engine, **0.5086 literal / 0.3748 material**, which I reproduce exactly. Apply the one structural correction — T5 as a language overlay on the numeric floor rather than a mutually exclusive regime, which is the only form it has ever taken (Mertz's "modest guide down" glossed the Feb 2024 floor) — and the decomposition becomes **0.425 / 0.292**. The base rate is a numeric February FY27 floor at all, 2 of 5 = 0.40 (Laplace **0.429**), with explicit down language 0 of 5 (Laplace 0.143) and 2 of 6 = 0.333 if the Feb 2021 letter is counted; both historical floors were ≥184bp, so the material base rate is the same 0.40–0.43. The anchor is WS05's "FY26 actual minus 0–190bp (n 3)" → 0.65 literal / 0.60 material, on a sample that contains no qualitative February at all.
Weight 0.5 / 0.3 / 0.2: literal 0.5(0.425) + 0.3(0.429) + 0.2(0.65) = **0.471**; material 0.5(0.292) + 0.3(0.429) + 0.2(0.60) = **0.394**, trimmed to **0.36** because the material reading also requires the floor to clear 50bp and the model's T2 band (0–25bp, n 0 in February) is the assumption doing that work. The literal number is essentially "does February carry a number at all, or say down" — the memo should say so, because that is a very different sentence from "management guides margin down". Impact: additive Street-estimate effect only — Street FY27 36.45% → ≈35.5%, −$142M of EBITDA, **−$0.20 of FY27 EPS**, ≈ **−$4/share** at a constant multiple, **EV ≈ −$1.9 — material**; the 11 Feb price reaction belongs to S03 and is not additive (the Feb 2025 precedent printed a 190bp haircut and **+14.4%**).

**B13 — P(Yes) = 0.30**, judgmental 80% interval 0.19–0.43; adopt **0.31** for run coherence.
Derivation: the run's adopted 4Q26 object (`adopted_q4_states_v2.json`, A12 revision 2) is the correct starting point and I reproduce it in stdlib at **P(≤131.0m) 0.3074** against its published 0.3089 (V1 0.4528 / V2 0.2574 / V3 0.0240; mean 8.614, sd 2.276). My single disagreement is the V2 cushion: N(1.0, 1.3) sits between a directional-era mean of −0.2 and two bucket-era beats of +4.8 and +1.15, and management has met 4 of 4 Q4 nights guides; at cushion 1.5 the object gives **0.288** and at 2.0 **0.272**. Splitting that against the V1 side, where the RNPL module's own base (7.61) would give **0.347**, lands at **0.30**.
Companions on the adopted object: P(≥134.0m) 0.307, P(131.1–133.9m) 0.384, mean 8.61, sd 2.28, E[4Q26 \| Yes] **5.93%**, E[3Q26 \| Yes] **9.09%**. Impact, recomputed on that object with **one** cost convention (held, i.e. 100% flow-through, the convention the margin line already uses):

| Item | Delta if B13 happens | vs the log |
|---|---:|---:|
| 3Q26 nights (pts) — selection, not impact | −0.41 | −0.9 |
| 4Q26 nights (pts) | −2.18 | −2.0 |
| ADR (pts) | 0.0 | 0.0 |
| 4Q26 revenue ($M) | −65 | −60 |
| FY27 revenue ($M, 70% persistence) | −241 | −220 |
| FY26 adj. EBITDA margin (pp) | −0.29 | −0.27 |
| FY27 adj. EBITDA margin (pp) | −1.01 | −0.92 |
| FY27 EPS ($) | −0.34 (flex −0.26) | −0.20 |
| Stock ($/share, joint solve) | −7.5 | −10 |
| **EV = P × stock** | **0.31 × −7.5 = −$2.3** | −2.6 |

**Material**, and still the mirror of R16 (+$2.7 at 0.31): the memo should carry the pair as "the Q4 number is about one in three to meet the Street and about one in three to print ≤7.5%", with the middle third named.

## Reproduction script

Run from the repository root with `python -B docs/pitch-forecasts/audits/A17-reproduce.py`. Stdlib and pandas only; it writes nothing and executes none of the three forecast models (all write into their own `datasets/` folders). The Monte Carlos are re-implemented with `random.Random` at 120,000 draws rather than numpy at 400,000–1,000,000, so they reproduce the seeded numpy figures to about ±0.005; each block prints the file's own numbers underneath for comparison. Runtime ≈ 3 minutes.

```python
"""A17 audit reproduction - B11, B12, B13. stdlib + pandas only; writes nothing.
Run from the repository root:  python -B docs/pitch-forecasts/audits/A17-reproduce.py
None of the three forecast models is executed (all write into their own datasets/ folders); each is
re-implemented here from source. The Monte Carlos use random.Random at 120,000 draws rather than numpy
at 400,000-1,000,000, so they reproduce the seeded numpy figures to about +/-0.005; every block prints
the file's own numbers underneath for comparison. Runtime ~3 minutes."""
from pathlib import Path
from statistics import mean, stdev
import math
import random
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
N = 120_000


def hdr(s):
    print("\n" + "=" * 10 + " " + s + " " + "=" * 10)


def pct(v, q):
    s = sorted(v)
    k = (len(s) - 1) * q
    lo = int(k)
    return s[lo] if lo + 1 >= len(s) else s[lo] + (k - lo) * (s[lo + 1] - s[lo])


# ------------------------------------------------------------------ B11 tape facts
hdr("B11  the downgrade feed and every base rate in claims 2-4")
feed = pd.read_csv(Q / "bonus-sellside-downgrades/datasets/feed_downgrades_all.csv", parse_dates=["date"])
raw = pd.read_csv(Q / "bonus-sellside-downgrades/sources/yfinance_upgrades_downgrades_20260917T082155Z.csv")
print("feed pull rows %d, action mix %s" % (len(raw), raw.Action.value_counts().to_dict()))
print("down rows %d, all to Hold/Sell %s, by year %s"
      % (len(feed), bool(feed.to_hold_or_sell.all()), feed.date.dt.year.value_counts().sort_index().to_dict()))
print("last downgrade %s -> %d days to 2026-09-16; largest earlier gap %d days"
      % (feed.date.max().date(), (pd.Timestamp("2026-09-16") - feed.date.max()).days, feed.date.diff().dt.days.max()))
print("same-calendar 17 Sep - 15 Dec: %s"
      % {y: int(((feed.date >= pd.Timestamp(y, 9, 17)) & (feed.date <= pd.Timestamp(y, 12, 15))).sum())
         for y in range(2021, 2026)})
for start, lab in [("2021-01-01", "2021+"), ("2023-01-01", "2023+"), ("2024-01-01", "2024+")]:
    starts = pd.date_range(pd.Timestamp(start), pd.Timestamp("2026-09-16") - pd.Timedelta(days=90))
    c = [int(((feed.date >= t) & (feed.date < t + pd.Timedelta(days=90))).sum()) for t in starts]
    print("  90-day windows %-6s n %4d  mean %.4f  P(>=3) %.4f  P(>=2) %.4f  max %d"
          % (lab, len(c), mean(c), sum(x >= 3 for x in c) / len(c), sum(x >= 2 for x in c) / len(c), max(c)))
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv", parse_dates=["reaction_date"])
ns = [int(((feed.date >= d - pd.Timedelta(days=49)) & (feed.date <= d + pd.Timedelta(days=39))).sum())
      for d in rx.reaction_date]
n23 = [n for n, d in zip(ns, rx.reaction_date) if d >= pd.Timestamp("2023-01-01")]
print("  print-shaped (-49/+39d) counts %s" % ns)
print("  all n %d mean %.4f P(>=3) %.4f | 2023+ n %d mean %.3f P(>=3) %.4f"
      % (len(ns), mean(ns), sum(x >= 3 for x in ns) / len(ns), len(n23), mean(n23), sum(x >= 3 for x in n23) / len(n23)))
sgn = {"up>=5": [], "small": [], "down<=-5": []}
for n, r in zip(ns, rx.abnb_1d_pct):
    sgn["up>=5" if r >= 5 else ("down<=-5" if r <= -5 else "small")].append(n)
print("  by day-1 sign: %s" % {k: "n %d mean %.3f P(>=3) %.3f" % (len(v), mean(v), sum(x >= 3 for x in v) / len(v))
                               for k, v in sgn.items()})
print("  NOTE: both >=3 windows (Feb 2022, Nov 2023) followed SMALL day-1 moves (+3.6, -3.3);")
print("        0 of 6 windows around a day-1 <= -5pct print ever reached 3 - the model's mechanism has no positive case")


# ------------------------------------------------------------------ B11 model
def b11(seed=20260917, n=N, weights=(.24, .14, .10, .52), d1=(4., -1., -2.5, -6.), d1sd=7.5,
        post_drift=(-2., -1., -1., -2.5), spre=35, spost=27, bg=.29, drift=.03, spot=167.51,
        pre_mu=.35, k_pre=3.0, post_mu=(.15, .5, .7, 1.1), beta=.06, k_post=3.0,
        od=1.6, capture=.85, pool=1.0):
    g = random.Random(seed)
    dt = 1 / 252
    cum, acc = [], 0.
    for w in weights:
        acc += w
        cum.append(acc)
    f = 21 / spre

    def nb(m):
        lam = m if od <= 1.0 else g.gammavariate(m / (od - 1.0), od - 1.0)
        k, term, cdf, u = 0, math.exp(-lam), math.exp(-lam), g.random()
        while u > cdf and k < 60:
            k += 1
            term *= lam / k
            cdf += term
        return k

    cnt, dec, yes = [], [], []
    for _ in range(n):
        u = g.random()
        z = next(i for i, c in enumerate(cum) if u <= c)
        rpre = (drift - .5 * bg * bg) * spre * dt + bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        day1 = d1[z] / 100 + d1sd / 100 * g.gauss(0, 1)
        rpost = (math.log1p(post_drift[z] / 100) + (drift - .5 * bg * bg) * spost * dt
                 + bg * math.sqrt(spost * dt) * g.gauss(0, 1))
        p1 = f * rpre + math.sqrt(f * (1 - f)) * bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        m_pre = pre_mu * pool * math.exp(-k_pre * min(p1, 0.0))
        m_post = post_mu[z] * pool * math.exp(-beta * (day1 * 100 - d1[z])) * math.exp(-k_post * min(rpost, 0.0))
        c = nb(m_pre) + nb(m_post)
        if capture < 1.0:
            c = sum(1 for _ in range(c) if g.random() < capture)
        cnt.append(c)
        dec.append(spot * math.exp(rpre + math.log1p(day1) + rpost))
        yes.append(c >= 3)
    return dict(p=sum(yes) / n, mean=mean(cnt), p_ge2=sum(c >= 2 for c in cnt) / n,
                E_dec_yes=mean(d for d, y in zip(dec, yes) if y), E_dec=mean(dec))


_m2 = .32 * 4 + .10 * -1 + .13 * -2.5 + .45 * -6
_between = (.32 * (4. - _m2) ** 2 + .10 * (-1. - _m2) ** 2 + .13 * (-2.5 - _m2) ** 2 + .45 * (-6. - _m2) ** 2)
S02R2 = dict(weights=(.32, .10, .13, .45), post_drift=(-1.5, -.5, -.5, -1.), spre=36, spost=26,
             bg=.30, drift=.0697, d1sd=math.sqrt(9.5 ** 2 - _between))
hdr("B11  published model, the revision-2 parameter swap, and the two corrections")
print("  S02 revision-2 within-branch day-1 sd from the variance identity: %.3f (S02 v2 solves 8.451)" % S02R2["d1sd"])
for name, kw in [("published (S02 revision 1, capture 0.85)", {}),
                 ("no modulation at all (k_pre = k_post = beta = 0)", dict(k_pre=0., k_post=0., beta=0.)),
                 ("S02 revision-2 parameters", S02R2),
                 ("rev2 + capture 1.0 (base rates are ALREADY feed counts)", dict(S02R2, capture=1.0)),
                 ("rev2 + feed print-window post means .02/.55/.55/.83", dict(S02R2, post_mu=(.02, .55, .55, .83))),
                 ("rev2 + capture 1.0 + feed post means", dict(S02R2, capture=1.0, post_mu=(.02, .55, .55, .83))),
                 ("rev2 + pre 0.26 (2023+ OFF-print 49-day rate)", dict(S02R2, pre_mu=.26)),
                 ("rev2 + capture 1.0 + pre 0.26 + feed post means",
                  dict(S02R2, capture=1.0, pre_mu=.26, post_mu=(.02, .55, .55, .83)))]:
    r = b11(**kw)
    print("  %-52s P %.4f  mean %.3f (= %.2f/yr)  E[Dec|Yes] %.1f vs %.1f"
          % (name, r["p"], r["mean"], r["mean"] * 365 / 89, r["E_dec_yes"], r["E_dec"]))
print("  the file's numpy run (b11_summary.json): P 0.15393 mean 1.169 E[Dec|Yes] 148.05 vs 161.11")
print("  measured rates: 3.51/yr (2021+), 3.51 (2023+), 2.59 (2024+), 0 trailing 12m;")
print("  print-shaped-window mean 0.74 per 89 days = 3.03/yr")


# ------------------------------------------------------------------ B12
hdr("B12  the five February letters and the literal / material record")
fs = pd.read_csv(Q / "bonus-fy27-investment-year/datasets/feb_fy_margin_sentences.csv")
for _, r in fs.iterrows():
    print("  %s %s  prior %.2f  floor_vs_prior %+d bp  literal %s material %s  [%s]"
          % (r.letter, r.letter_date, r.prior_fy_actual_pct, int(r.floor_vs_prior_bp),
             r.b12_literal, r.b12_material, r.form))
print("  literal 2 of 5 = %.3f (Laplace %.3f); a numeric floor given at all 2 of 5; explicit 'down' 0 of 5 (Laplace %.3f)"
      % (2 / 5, 3 / 7, 1 / 7))
print("  NOTE the 4Q20 (Feb 2021) letter also carries a forward FY margin sentence - 'focused on ... expanding our")
print("  Adjusted EBITDA margin as we scale' - so the reference class can be read as 2 of 6 = %.3f" % (2 / 6))


def b12(seed=20260917, n=N, A_mu=35.85, A_sd=.55, p_defend=.85, miss=(35.4, .4),
        w=(("T1", .20), ("T2", .22), ("T3", .30), ("T4", .08), ("T5", .10), ("T6", .10)),
        h1=(1.0, 2.0), h2=(0.0, .25), material=.5):
    g = random.Random(seed)
    keys = [k for k, _ in w]
    tot = sum(p for _, p in w)
    cum, acc = [], 0.
    for _, p in w:
        acc += p / tot
        cum.append(acc)
    lit = mat = t2flat = 0
    gaps = []
    for _ in range(n):
        A = A_mu + A_sd * g.gauss(0, 1)
        A = max(A, 35.5 + abs(g.gauss(0, .12))) if g.random() < p_defend else miss[0] + miss[1] * g.gauss(0, 1)
        A_r = round(A, 1)
        u = g.random()
        T = keys[next(i for i, c in enumerate(cum) if u <= c)]
        if T == "T1":
            lvl = math.floor((A - g.uniform(*h1)) / .5) * .5
        elif T == "T2":
            lvl = math.floor((A - g.uniform(*h2)) / .5) * .5
        else:
            lvl = None
        yl = (T == "T5") or (lvl is not None and A_r - lvl > 1e-9)
        ym = (T == "T5") or (lvl is not None and A_r - lvl >= material - 1e-9)
        lit += yl
        mat += ym
        t2flat += (T in ("T5", "T1"))
        if yl and lvl is not None:
            gaps.append(A_r - lvl)
    return dict(literal=lit / n, material=mat / n, t2_as_flat=t2flat / n, gap_mean=mean(gaps),
                gap_p50=pct(gaps, .5), gap_p90=pct(gaps, .9), share_lt_50bp=sum(x < .5 for x in gaps) / lit)


hdr("B12  published model, and what the T5 and T2 regimes are doing")
r = b12()
print("  published rebuild: literal %.4f material %.4f T2-as-flat %.4f gap mean %.2f p50 %.2f p90 %.2f share<50bp %.2f"
      % (r["literal"], r["material"], r["t2_as_flat"], r["gap_mean"], r["gap_p50"], r["gap_p90"], r["share_lt_50bp"]))
print("  the file's numpy run: literal 0.517 material 0.388 t2-as-flat 0.299 gap mean 1.04 p50 0.7 p90 2.1 share 0.25")
for name, kw in [("F03 rev-2 FY26 print N(35.72,0.58), 50pct defence",
                  dict(A_mu=35.72, A_sd=.58, p_defend=.50, miss=(35.72, .58))),
                 ("F03 rev-2 realised regime weights (T1 .20 T2 .20 T3 .33 T4 .08 T5 .12 T6 .07)",
                  dict(w=(("T1", .20), ("T2", .20), ("T3", .33), ("T4", .08), ("T5", .12), ("T6", .07)))),
                 ("T5 as a LANGUAGE OVERLAY on T1, not a separate regime (T5 0.02)",
                  dict(w=(("T1", .20), ("T2", .22), ("T3", .38), ("T4", .08), ("T5", .02), ("T6", .10)))),
                 ("T2 halved to 0.11 (no February letter has ever used that form)",
                  dict(w=(("T1", .20), ("T2", .11), ("T3", .41), ("T4", .08), ("T5", .10), ("T6", .10)))),
                 ("T2 = 0", dict(w=(("T1", .20), ("T2", .0), ("T3", .52), ("T4", .08), ("T5", .10), ("T6", .10))))]:
    v = b12(**kw)
    print("  %-62s literal %.4f  material %.4f" % (name, v["literal"], v["material"]))
print("  the whole literal-vs-material wedge is T2: at T2 = 0 the two readings coincide.")
print("  F03 revision 2's own joint model (f03_f04_joint_v2.py, A08 response) publishes literal 0.5086 / material 0.3748.")


# ------------------------------------------------------------------ B13
hdr("B13  the published blend, its mean, and the ADOPTED 4Q26 object")
BASE, LO, HI = 121.9, 131.0, 134.0
thr_lo, thr_hi = (LO / BASE - 1) * 100, (HI / BASE - 1) * 100
print("  thresholds: <=131.0m = %.4f pct y/y ; >=134.0m = %.4f pct y/y" % (thr_lo, thr_hi))


def mixture(seed=20260917, n=N, q3_mu=9.67, q3_sd=1.70, q3_ref=9.67, q4_mu=8.1, beta=.5, res_sd=1.4,
            tail_w=.12, vec=(.21, .19, .39, .17, .04), cushion=(1.2, 1.3), street_sd=1.23,
            w=(.5, .3, .2)):
    g = random.Random(seed)
    mids = (10.75, 9.75, 8.0, 6.0, None)
    cv, acc = [], 0.
    for p in vec:
        acc += p
        cv.append(acc)
    wv, acc = [], 0.
    for p in w:
        acc += p
        wv.append(acc)
    q3s, q4s, v1s, v2s, v3s = [], [], [], [], []
    for _ in range(n):
        q3 = g.gauss(q3_mu, q3_sd)
        v1 = (5.5 + beta * (q3 - q3_ref) + g.gauss(0, 1.5)) if g.random() < tail_w \
            else (q4_mu + beta * (q3 - q3_ref) + g.gauss(0, res_sd))
        u = g.random()
        b = next(i for i, c in enumerate(cv) if u <= c)
        v2 = v1 if mids[b] is None else mids[b] + g.gauss(*cushion)
        v3 = g.gauss(thr_hi, street_sd)
        u = g.random()
        k = next(i for i, c in enumerate(wv) if u <= c)
        q3s.append(q3)
        v1s.append(v1)
        v2s.append(v2)
        v3s.append(v3)
        q4s.append((v1, v2, v3)[k])

    def st_(x):
        nights = [round(BASE * (1 + v / 100), 1) for v in x]
        return (sum(v <= LO for v in nights) / len(x), sum(v >= HI for v in nights) / len(x), mean(x))
    lo_, hi_, m_ = st_(q4s)
    nights = [round(BASE * (1 + v / 100), 1) for v in q4s]
    le = [(a, b) for a, b, c in zip(q4s, q3s, nights) if c <= LO]
    return dict(p_le_131=lo_, p_ge_134=hi_, mean=m_, sd=stdev(q4s),
                V1=st_(v1s), V2=st_(v2s), V3=st_(v3s),
                E_q4_le=mean(a for a, b in le), E_q3_le=mean(b for a, b in le), E_q3=mean(q3s))


r1 = mixture()
print("  revision-1 parameters (the published B13): V1 %.4f  V2 %.4f  V3 %.4f  ->  blend P(<=131.0m) %.4f"
      % (r1["V1"][0], r1["V2"][0], r1["V3"][0], r1["p_le_131"]))
print("    file: V1 0.4211  V2 0.1558  V3 0.0245  blend 0.2622 -> published 0.26")
print("    BLEND MEAN %.3f, sd %.3f  <-- the log's sections 3 and 5 assert 'mean ~ 8.3'" % (r1["mean"], r1["sd"]))
print("    blend P(>=134.0m) %.4f -> middle mass %.4f, not the log's 0.47"
      % (r1["p_ge_134"], 1 - r1["p_le_131"] - r1["p_ge_134"]))
ADOPT = dict(q3_mu=9.5, q3_ref=9.5, res_sd=2.0, vec=(.18, .17, .30, .31, .04), cushion=(1.0, 1.3))
r2 = mixture(**ADOPT)
print("  ADOPTED object (adopted_q4_states_v2.json, R16 rev 2): V1 %.4f  V2 %.4f  V3 %.4f  -> P(<=131.0m) %.4f"
      % (r2["V1"][0], r2["V2"][0], r2["V3"][0], r2["p_le_131"]))
print("    file: V1 0.4514  V2 0.2585  V3 0.0248  blend 0.3089  mean 8.6122  sd 2.2782")
print("    my rebuild mean %.3f sd %.3f ; E[Q4|Yes] %.3f (file 5.925) ; E[Q3|Yes] %.3f (file 9.091) ; E[Q3] %.3f"
      % (r2["mean"], r2["sd"], r2["E_q4_le"], r2["E_q3_le"], r2["E_q3"]))
for name, kw in [("cushion 1.5", dict(cushion=(1.5, 1.3))), ("cushion 2.0", dict(cushion=(2.0, 1.3))),
                 ("Q4 centre 7.61 (RNPL module)", dict(q4_mu=7.61)), ("Q4 centre 8.9 (case A)", dict(q4_mu=8.9)),
                 ("blend 0.4/0.4/0.2", dict(w=(.4, .4, .2))), ("equal thirds", dict(w=(1 / 3, 1 / 3, 1 / 3)))]:
    kk = dict(ADOPT)
    kk.update(kw)
    print("    %-32s P(<=131.0m) %.4f" % (name, mixture(**kk)["p_le_131"]))

hdr("B13  the section-9 impact arithmetic on the adopted object")
dq4 = r2["E_q4_le"] - 8.1
dq3 = r2["E_q3_le"] - 9.5
print("  4Q26 nights  %+.2f pt   (log: -2.0)" % dq4)
print("  3Q26 nights  %+.2f pt   (log: -0.9, measured against 9.9 rather than R01 revision 2's 9.5)" % dq3)
print("  4Q26 revenue %+.0f M    (log: -60)   [1pt = $30M]" % (dq4 * 30))
print("  FY27 revenue %+.0f M    (log: -220)  [70pct persistence x $158M/pt]" % (.7 * dq4 * 158))
print("  FY27 margin  %+.2f pp   (log: -0.92) [0.66pp per pt, HELD costs]" % (.66 * .7 * dq4))
print("  FY27 EPS held-cost %+.3f  flex-cost %+.3f   (log: -0.20, from $220M x 0.66 x $0.0014)"
      % (.7 * dq4 * 158 * .0014, .7 * dq4 * 158 * .78 * .0014))
print("  the log books the HELD margin coefficient (0.66pp/pt) and a 66pct dollar flow-through in the same table;")
print("  held costs = 100pct flow-through; the brief's flex case solves to 78pct. Either way the EPS line is understated.")
print("  stock, joint solve %+.2f  (log: -6.9 on 1.4pt); the -$3 February reaction is that same repricing, not an addition"
      % (.7 * dq4 * 4.90))
```
