**B08 — submitted probability: 0.38, interval 0.25–0.52.**
Defensible as written: no — not because the model is wrong, but because it contradicts the pitch's own margin view without saying what the memo should do about it.
First fix: `40_lines_quarterly.csv` puts 4Q26 cost of revenue at **$578.0M** in its base scenario and at or above the $575M threshold in **six of its eight published scenarios**; B08 publishes a $559M median and P = 0.26. The team cannot show a base case of $578M and a 26% probability of ≥$575M in the same document.
Next fix: the 0.45 weight on the "evidence-only" hosting branch is the one input that produces that gap, and it is the branch management has explicitly said its own guidance does not assume (Mertz, 6 Aug: the guidance "does assume a material increase in terms of the AI spend over the course of the year").
Independent comparison: **0.45** (0.32–0.58), leg 2 = 0.32. The §9 EPS row is correct (one application of the coefficient); the share count (620m) and the "−0.9pp on the Street" figure are not.

**B09 — submitted probability: 0.10, interval 0.05–0.20.**
Defensible as written: yes, and the single best piece of work in the batch is inside it — the 4Q24 $368M / 4Q25 $411M correction verifies verbatim against the releases and the repo's driver history is wrong.
First fix: the log corrects the SBC *series* and then calibrates route C's miss branch on the *uncorrected* one. `02_guidance_ledger`'s FY24 actual of 30.82% reproduces only from the erroneous driver history; on the printed releases FY24 was +25.6%, so the 3Q24 "~25%" guide was **met**, not missed by 5.8 points, and the 1Q24 "~20%" guide missed by **5.6**, not 10.8.
Next fix: three of six §7 rows do not replay (sd 0.02 → 0.09 not 0.05; last-8 y/y → 0.18 not 0.22; 1H26 rate → 0.10 not 0.06); two are route values reported as final values.
Independent comparison: **0.08** (0.04–0.14). Immaterial either way; the verdict "drop from the memo body" stands.

**B10 — submitted probability: 0.05, interval 0.02–0.10.**
Defensible as written: yes. Every series, every FRED quarter mean and every Kalshi quote reproduces exactly, and the extreme-probability gate is audited properly.
First fix: the buyback-upsize branch applies the full incremental draw to both the 30 Sep and 31 Dec balances. Ramping it (half by 30 Sep) takes the conditionals from 0.096/0.381 to 0.062/0.207 and the published mixture from 0.043 to **0.036**. The error runs toward Yes, so 0.05 is a ceiling.
Next fix: the companion "P(≤$162M, any y/y decline) ≈ 0.13" is wrong — the model's own base regime gives **0.155** and the published mixture **0.213**. That is the number the memo would actually quote.
Independent comparison: **0.04** (0.015–0.08). Immaterial; and the log's best sentence — "the memo should make the RNPL cash-timing point on unearned fees, not here, where rates are now a tailwind" — should survive into the memo verbatim.

**B17 — submitted probability: 0.42, interval 0.28–0.56.**
Defensible as written: the conventions are right and the headline is close to mine; the impact table is not defensible and the key route probability comes from the wrong reference class.
First fix: §9 prices the modal Yes as news. Route (b) — 0.80 of the Yes mass — is the CFO repeating a sentence she gave on **6 August**, already in the Street's 4Q26 and FY27 numbers. R04 revision 2 made exactly this correction for the mirror question (A10-01, "the event is a statement, not a delivered take-rate step"); B17 did not. On an R04-style split of the Yes mass, E[stock | Yes] = **−$2.5**, EV **−$0.95** — borderline, not "material" at −$2.5/share.
Next fix: P(take rate is a topic) = 0.80 is imported from R04's "3 of the last 3 calls", which are the 4Q25/1Q26/2Q26 calls. The **3Q24 and 3Q25 calls contain the string "take rate" zero times** — in full 146k- and 165k-character mirrors with ten and nine analyst firms in Q&A — and no shareholder letter has ever named customer incentives as reducing the take rate, so route (b) is a call-only route in the one slot where the call has been silent.
Independent comparison: **0.38** (0.26–0.52); strict-convention companion **0.31**, not 0.33.

## Rulings requested by the audit prompt

**B17 convention (1) — an FY26 take-rate sentence delivered on 5 Nov counts: UPHELD, with a tightening.** The question's second clause — "*or that incentives/new businesses will reduce it*" — carries **no period qualifier at all**, so a statement that incentives are reducing the implied take rate is a qualifying statement on the question's own text regardless of the period label. The first clause is period-bound ("4Q26 or FY27"), and on 5 Nov an FY26 statement's only unreported content is 4Q26, so it is a forward 4Q26 statement in substance. The tightening: the log's wording ("an FY26 statement made on 5 Nov qualifies") is broader than the question. It must be forward in form (*expect / anticipate / will*) and its period must extend into 4Q26 — the 2Q26 sentence ("we expect… during 2026") does; a retrospective "our 9M take rate was held back by incentives" does not. That is a shading of route (b), not a change of regime. **Convention (5) — "flat, with incentives offsetting gains" counts — is also upheld**, and is not really a convention: it is the question's parenthetical read literally. The §7 "net-only reading → 0.22" therefore belongs in §7 and nowhere else. The strict alternative (0.33 as published, 0.31 on my inputs) should be carried as a companion, not promoted.

**B08's leg 2 is the question; B17's is the convention.** B08 has no convention risk that matters except the 10-K commitments table, and on that convention (2) is right: a contractual schedule is not a management quantification of incremental spend. But §7 prices the alternative at 0.85 when it is nearer **0.97** — the FY26 10-K will restate a schedule that already implies ~+$246M for 2027 — so it is the largest single lever in the log and the RESUME is right to want it settled before 2 October.

## Scope and verification

Audit date **2026-09-17**, read-only, revision 1 of all four logs. `py -3.13` (numpy, pandas) and the repo `python` were both available. **No saved model was executed in place** — all four write CSVs into their own `datasets/` directories — so every figure below comes from an independent re-implementation and from the reproduction script at the end. No network was used: the FRED, Kalshi and Polymarket claims were checked against the timestamped snapshots in each `sources/` folder. No prohibited directory was opened. Nothing in the repository was modified except this file.

**All four models reproduce.** B08: leg 2 p 0.2586 against the published 0.2598, median $559M, p10–p90 $530–591M, and every sensitivity row in `b08_results.csv`. B09: routes A 0.0475 / B 0.0776 / C 0.1965 against 0.0478 / 0.0786 / 0.1990, blend 0.0893 against 0.0904. B10: base-regime P 0.0132 against 0.01365, median $177M, and every §7 conditional. B17: the copula union replays to 0.4824 against 0.4812 and the strict variant to 0.3342 against 0.3344.

**The load-bearing external facts verify.** The 4Q24/4Q25 SBC correction (`$368` / `$411`), FY25 SBC $1,592M, 1H26 $897M, the 2Q26 nine-quarter row `382 362 368 358 424 399 411 410 487`, the interest-income row `(226) (207) (183) (173) (190) (180) (162) (155) (183)`, FY25 interest income $705M, the FY25 10-K Note 13 schedule (`$1,749 / 219 / 930 / 600 / —`, "at least $1.7 billion… through 2031"), the FY23/FY24/FY25 SBC guidance sentences, Mertz's 2Q26 take-rate paragraph word for word, and all thirteen letter take-rate direction sentences in the guidance ledger — every one of them is as the logs state. The FRED DTB3 quarter means (4Q25 3.726, 1Q26 3.594, 2Q26 3.624, 3Q26-to-date 3.749) and all eleven quoted Kalshi Fed prices reproduce exactly.

**One retrieval artefact corrected in the forecaster's favour.** Every `updated_time` in both Kalshi Fed files reads `2026-04-09` — including strikes for January 2027 that cannot have existed then — while `volume_24h_fp` runs to 298,901 contracts on the October ladder. The field is series metadata, not a quote timestamp. That is the **opposite** inference to the one A01-04 and A12-14 drew from the same field on the ABNB nights ladder, and it means B10's adjacent-market evidence is live and deep, not stale.

Below, `log`, `model` and `forecast` mean `research-log.md`, `datasets/<id>_model.py` and `forecasts/2026-09-17-forecast.json` under `docs/pitch-forecasts/questions/<slug>/`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A16-01 | B08 | critical | `log:85–88` (anchor and independence note); `forecast.estimates.anchor` 0.63; `model:30` (`host_mix`) | The published number contradicts the pitch's own adopted margin view and the log resolves the contradiction silently, in prose, in favour of the forecast. `40_lines_quarterly.csv` puts 4Q26 cost of revenue at **$578.0M** in the `base` scenario and at or above the $575M threshold in **six of eight** published scenarios (578.0, 586.9, 581.9, 575.3, 575.5, 583.9; only `evidence_only` $548.8M and `rev_bear` $571.9M are below). B08's median is **$559M** and its P(leg 2) is 0.26. A judge reading the model tab and the risk table together sees a base case above a threshold the memo says is 26% likely. | Read every 4Q26 row of `40_lines_quarterly.csv` (reproduction script, block B08/1). The $19M gap is entirely the hosting line: the model's mixture mean is 56 + 26.25 = $82.3M against the build's $100.2M; fees ($403.7M vs $404.4M), chargebacks ($26M) and other ($47.8M vs $47.4M) agree. | Decide once, for both documents. Either the line build's 4Q26 hosting drops toward the evidence-only $71M — which also moves the FY26 margin cushion and the 3Q26 card — or B08's hosting mixture rises. At 0.33/0.37/0.30 with outcome-scale GBV and fee spreads, leg 2 is **0.324** and the headline **0.45**. Whichever is chosen, §9 must say which path the memo is quoting. |
| A16-02 | B17 | critical | `log:115,127,128`; `forecast.impact.stock_usd_per_share` −6, `ev_stock_usd_per_share` −2.5, `material` true | §9 prices the modal Yes as new information. Route (b) is **0.80 of the Yes mass** and its modal form is the CFO restating the FY26 sentence she gave on **6 August 2026** — a sentence the Street has had for six weeks and which is already inside the LSEG 4Q26 revenue mean the log itself uses ($3,162M) and inside FY27 estimates. Marking it at −13bp on 4Q26 and −15bp on FY27 books a re-rating for a restatement. R04 revision 2 makes exactly this correction on the mirror question and splits the Yes mass by form; B17 does not. | `../risk-single-fee-take-rate-accretion-stated/forecasts/2026-09-17-forecast.json` `impact.note` (A10-01) and `impact.split_by_form`. Re-priced with an R04-style split (repeat of the standing form 0.60 at −$0.5; incentives named for a new period or mechanism 0.15 at −$5; the letter's Q4 sentence reading "lower" 0.20 at −$5; a quantified FY27 decline 0.05 at −$9): **E[stock \| Yes] = −$2.50**. | Publish the split. EV at my 0.38 is **−$0.95/share**; at the published 0.42 it is −$1.05. Change `material` to the borderline language R04 rev 2 uses, and keep the row only because the tail form (a quantified FY27 take-rate decline) is genuinely worth −$9. |
| A16-03 | B17 | major | `log:124,125`; `forecast.impact.margin_fy26_pp` −0.2, `margin_fy27_pp` −1.0 | Both margin rows divide the EBITDA delta by the **unchanged** revenue base. When revenue falls, the denominator falls with it. FY27: (5,483 − 153)/(15,829 − 170) = 34.038% against 34.639% = **−0.60pp**, not −1.0. FY26: (5,098 − 27)/(14,268 − 30) = 35.613% against 35.730% = **−0.11pp**, not −0.2. The same batch's mirror row in R04 rev 2 (+$23M revenue → +0.09pp) is computed correctly on the same annuals, so the run uses one coefficient two ways. | `docs/margin-build/SYNTHESIS.md:299–301` (FY26 14,268 / 5,098 / 35.73%; FY27 15,829 / 5,483 / 34.64%); arithmetic in the reproduction script, block B17/5, which also replays R04's +0.080pp against its published 0.09. | Publish **−0.1pp** and **−0.6pp**. The EPS row (−$0.21 = $0.0014 × $153M) is already correct — it applies the flow-through once — and does not move. Stock and EV move for the reason in A16-02, not this one. |
| A16-04 | B09 | major | `log:35` (claim 3), `:37` (claim 5); `model:48–52` (route C) | The log corrects the SBC series in convention (2) and then calibrates route C's miss branch on the **uncorrected** series. `02_guidance_ledger`'s `sbc_yoy_pct` actuals (FY23 18.28%, FY24 30.82%) reproduce only from `abnb_driver_history_quarterly.csv` (4Q23 270, 4Q24 400) — the file the log has just declared wrong. On the printed releases FY23 was **+20.4%** (guide "~20%": met, not beaten), FY24 **+25.6%** (the 1Q24 "~20%" guide missed by **5.6** points, not 10.8; the 3Q24 "~25%" guide **met**, not missed by 5.8). So the record behind "management misses its own SBC sentence" is 1 of 3, and the one miss is half the stated size. | Letters: FY23 1,120/930, FY24 1,407/1,120, FY25 1,592/1,407 → 20.43 / 25.63 / 13.15. Driver history: 1,100/930, 1,439/1,100, 1,581/1,439 → 18.28 / 30.82 / 9.87, which is what the ledger carries. Block B09/2. | Re-cut route C to P(miss) ≈ **0.15** with a **+4** mean: the route falls 0.199 → **0.128**. Note the same defect in the ledger for anyone else using `sbc_yoy_pct` — it is a point-in-time-clean ledger reporting a wrong actual. |
| A16-05 | B09 | major | `log:91–93`; `forecast.sensitivity` rows 2, 3, 4 | Three of six §7 rows are not the model's blend. Recomputing 0.4A + 0.4B + 0.2C (+0.02) under each reversal gives **0.131 / 0.093 / 0.180 / 0.095 / 0.134 / 0.094** against the published 0.13 / **0.05** / **0.22** / **0.06** / 0.14 / 0.08. The 0.05 and 0.06 are route-level readings (A at sd 0.02 = 0.006; B at the 1H26 rate = 0.041) reported as if they were final numbers; the 0.22 is neither route (0.256) nor blend (0.180). | Full replay in the reproduction script, block B09/3. `b09_results.csv` contains only route values; no §7 row is computed anywhere in `b09_model.py`. | Publish the recomputed blends and add the sensitivity loop to the model so the table is generated, not typed. The honest width of the question across §7 is **0.09–0.18**, narrower than the published 0.05–0.25, which matters because the log's own credible interval is 0.05–0.20. |
| A16-06 | B10 | major | `model:42–43` (`extra_cash_draw`), `:66–68` (mixture); `log:41` (claim 9), `:95` | The buyback-upsize branch subtracts the **full** incremental draw from both the 3Q26 and the 4Q26 balance. An upsize spent across 2H26 has reached roughly half its size by 30 September, and the earning base is the average of the two quarter-ends. Ramping the draw (750/1,500 and 1,500/3,000) takes the conditionals from 0.096/0.381 to **0.062/0.207** and the published mixture from 0.0435 to **0.0355**. The bias runs toward Yes. | Reproduction script, block B10/2; the historical `avg_base` construction in `b10_history.csv` confirms the average-of-quarter-ends definition. | Ramp the draw. The mixture becomes 0.036; with the unmodelled presentation and M&A tails the final is **0.04**, and the published 0.05 should be described as the top of the range rather than the centre. |
| A16-07 | B10 | major | `log:86`; `forecast.companion` (absent — the figure appears only in §6) | "P(≤ $162M, any y/y decline) ≈ 0.13" is below the model's own base regime. The base regime gives **0.155** and the published mixture **0.213**. This is the number a memo sentence would actually use ("interest income more likely than not rises"), and it is understated by 6–8 points. | Reproduction script, block B10/2, which returns P(≤145.8) and P(≤162) from the same draws. P(≥$190M) 0.191 matches the published 0.20. | Publish **0.16** (base regime) or **0.21** (mixture) and say which. The headline P(Yes) is unaffected. |
| A16-08 | B17 | major | `log:42` (claim 10), `:98`; `model:32` (`p_topic=0.80`); claim 7 | P(take rate is a topic) = 0.80 is imported from R04's "9 of 22 calls, **3 of the last 3**" — and those three are the 4Q25, 1Q26 and 2Q26 calls. The Q3 slot, which is the slot this question resolves on, is different: the **3Q24 and 3Q25 call mirrors contain the string "take rate" zero times**, along with zero "GBV" and zero "monetization", in 146,320 and 165,027 characters of text with ten and nine analyst firms in the Q&A. 3Q23 has 16, 3Q22 14, 3Q21 2. And route (b) has no letter door: **no shareholder letter has ever named customer incentives as reducing the take rate** (the only letter since 1Q23 containing the word at all is 1Q24, and there it is "payment processing incentive benefits", a cost item). | Regex over all mirrors and all 23 letters; reproduction script, block B17/2, which prints the character count and the analyst-firm count for each call so the zero cannot be read as a truncated file. | Set P(topic) to about **0.65** — above the 1-of-3 recent Q3 record because the single-fee migration, the direct-link pilot and a standing FY26 take-rate guidance all make it likelier this year, below 0.80 because the last two Q3 calls were silent. The decomposition falls 0.481 → **0.426**. Say in the log that the Q3 call is historically a product call. |
| A16-09 | B17 | major | `log:71,73`; §4 row 1; §6 | The strongest argument against route (b) is in the team's own model and the log never makes it. The adopted path has the **FY26 implied take rate rising**: FY26 revenue $14,268M ÷ GBV $105.4bn = **13.535%** against FY25 $12,241M ÷ $91.3bn = **13.407%**, i.e. **+12.8bp**, against management's standing "relatively flat compared to 2025". If the team's own path is right, the 5 Nov FY sentence is likelier to read "up slightly" — the 4Q25 and 1Q26 letters' form — than to repeat "flat, held back by incentives". C11 revision 2 compounds it: 0.76 that the 3Q26 take rate prints **above +22bp y/y**. | 1H26 revenue 2,678 + 3,608 on GBV 29.2 + 27.2 (`02_panel_quarterly.csv`); 3Q26/4Q26 from `40_lines_quarterly.csv` (4,804.04 / 26.028 and 3,178.11 / 22.987); FY25 from the same panel. `q3-take-rate-above-1810/forecasts` revision 2, p 0.76. | Add the row to §4 and to §7 as "the team's own FY26 take-rate path is +13bp, not flat". It is the reason to sit below 0.42 rather than above it, and it is the sentence a judge will ask about when the memo quotes both C11 at 0.76 and B17 at 0.42. |
| A16-10 | B08 | major | `log:38` (claim 6), `:72`, `:88`; `forecast.estimates.independence_note` | The 10-K argument is over-read. The `less than 1 year` bucket ($219M for 2026) is a **contractual minimum**, not a budget, and it does not bound the P&L line that leg 2 resolves on. The 2Q26 10-Q attributes the increase to "higher amortization related to **reserved instance purchases** and increased infrastructure spend" — prepaid capacity whose expense recognition is an amortisation schedule, which can step ahead of the committed minimum. "The contracted step is in 2027, not 2026" is true of the commitment and carries no weight against a 4Q26 expense line; the log uses it as the primary reason to cut the team's own hosting path from 1.00 to 0.20. | FY25 10-K Note 13 verified verbatim (block B08/3): `$1,749 / 219 / 930 / 600 / —` and "at least $1.7 billion for vendor services through 2031". 2Q26 10-Q MD&A sentence read in full. | Keep claim 6 as evidence on the FY27 leg-1 route, where it is strong and where it makes leg 1 more likely, and drop it from the leg-2 argument. Replace it with the only 2026-relevant evidence there is: 2Q26 server costs +$12M y/y and Mertz's "material increase… over the course of the year". |
| A16-11 | B08 | major | `model:30` (`host_mix=(0.45,0.35,0.20)`); `log:73`, `:98` | The 0.45 weight on the evidence-only branch contradicts claim 7. That branch is +$15M/quarter on a $56M FY25 base — roughly the y/y increase **already printed** in 2Q26 (+$12M of server costs). It is therefore the "no further ramp" case, and management has said on the record that the guidance assumes the opposite: "the updated guidance… obviously does assume a material increase in terms of the AI spend over the course of the year" (S162, 6 Aug). The mixture is the single largest lever in the log (0.10 → 0.57 across its range) and it is set against the log's own strongest evidence. | `05_statements.csv` S162 quoted in claim 7; `40_params.csv` hosting construction; the branch arithmetic in `model:39–41`. Re-weighting to 0.33/0.37/0.30 lifts leg 2 from 0.259 to **0.302** at the published spreads. | Re-weight to about 0.33/0.37/0.30 and state the reason in §4 rather than in the anchor note. With the spread fix (A16-12) leg 2 is 0.324. |
| A16-12 | B08 | major | `model:30` (`gbv_sd=650`, `rate_sd=0.04`) | The two spreads are **cross-sectional analyst dispersion**, not outcome uncertainty, for a quarter that has not started and prints in five months. $650M is the MODL range (22,177–23,565, n 28); the team's own 4Q26 nights uncertainty in the same run (R16/B13) is about 2 points ≈ $460M of GBV **before** ADR and FX, and the merchant-fee annual-equivalent rate has moved 1.69 → 1.76 → 1.68 across three years against an assumed sd of 0.04 (2.3%). Both understate the tail on the side the question resolves. | Reproduction script, block B08/2: at gbv_sd 800 and rate_sd 0.05 the published mixture gives leg 2 **0.292**; with the A16-11 re-weight, **0.323**. | Use outcome-scale spreads (gbv_sd ≈ 800–900, rate_sd ≈ 0.05–0.06) and say they are outcome spreads, not the Street range. |
| A16-13 | B08, B09, B10, B17 | major | all four `forecast.estimates.anchor` / `anchor_source` | **No question in this batch has an external anchor**, and all four report `final_minus_anchor` against an internal object: B08 against the team's own line build (the same formula its decomposition uses — the two differ only in the hosting mixture), B09 against the team's own M7 rule, B10 against the same M7's LIVE band, B17 against a self-chosen flat 0.50 prior. A12-22 ruled on the identical pattern in R15. B08 additionally sets `not_independently_derived_flag` **false** while the other three set it true on weaker grounds. | Read all four `anchor_source` fields; confirmed no Kalshi or Polymarket market exists on any of the four objects (the three ABNB pulls are byte-identical copies of one fetch of the `KXABNB-26NOVNEB` nights ladder, sha256 `b0c7ad4da6d8…`). | Set `anchor: null` with `NO_EXTERNAL_ANCHOR` in all four, keep the internal objects as labelled comparisons, and stop reporting `final_minus_anchor` against them. B08's flag must be **true**: the anchor is its own model with one parameter changed. |
| A16-14 | B17 | major | `log:39` (claim 7); `forecast` written 04:41:01 | Sibling re-basing. Claim 7 quotes R04 at **0.58 (0.42–0.72)**; R04 went to revision 2 at **0.52 (0.38–0.66)** (commit `d0c4d81`, 09:38) and C11 to revision 2 at 0.76 (commit `e33be28`, 05:06), both after B17's forecast file was written. Not an error by the forecaster — but R04 rev 2's impact treatment is the template B17 needs (A16-02) and C11 rev 2's corrected language record is the input to A16-09. | `git log` on both forecast files; file mtimes (B17 04:41:01, C11 05:01:47, R04 09:28:50). | Re-base claim 7 to R04 0.52, and carry R04's `split_by_form` structure into B17's §9. The two questions are not exclusive and should share one Yes-mass taxonomy. |
| A16-15 | B09 | minor | `model:43–58`; `log:77` (route C) | Route C is not an independent third route. It re-expresses the same y/y information as an FY constraint and then loads **all** of the FY residual onto Q4 — 3Q26 is fixed at 399 × 1.132 with zero error — so it is neither independent of route B nor a correct decomposition of the FY uncertainty (a high-SBC regime raises Q3 and Q4 together; the residual construction makes them offset). It carries 0.2 of the weight and is the highest of the three (0.199). | `model:45–47` sets `q3 = 399 * 1.132` as a scalar; adding independent Q3 noise of $25M *raises* route C to 0.216, which is the wrong sign for the correlation that actually holds. | Cut route C's weight to about 0.10 and describe it as a guidance-miss overlay on route B rather than a third estimate. With the A16-04 recalibration the blend is **0.079** and the headline **0.08**. |
| A16-16 | B09 | minor | `log:85`; `forecast.companion` | The companion quantiles are not computed anywhere. Sampling the published 0.4/0.4/0.2 blend gives median **$465M**, P(≥$480M) **0.27**, P(≤$450M) **0.29** against the published $468M / 0.30 / 0.25. | Reproduction of the three routes and a weighted draw; `b09_results.csv` contains no quantile rows. | Publish the sampled figures, or label them as the seasonal route's quantiles rather than the blend's. |
| A16-17 | B10 | minor | `log:37` (claim 5); `sources/fred_DFEDTARU_…csv`, `fred_DTB3_…csv` | The 16 September FOMC decision — the fact the whole question turns on — **is not in this question's saved evidence**. `DFEDTARU`'s last observation is 2026-09-16 = **3.75** and `DTB3`'s is 2026-09-15 = 3.97; the hike is sourced to R10 claim 10, which A12 found has no saved snapshot either. | Read both files' tails (block B10/1). The hike *is* corroborated inside B10's own `sources/`: **`KXFED-26OCT-T3.75` is bid 0.98 / ask 0.99** ("upper bound above 3.75% at the October meeting"), with 22,734 contracts of volume and 8,559 in the last 24 hours — a market certain the upper bound is already 4.00. | Re-cite claim 5 to the Kalshi ladder, not to R10, and state that DFEDTARU's 3.75 on 16 Sep is the pre-effective-date reading. The rate path does not change. |
| A16-18 | B10 | minor | `log:38` (claim 6), `:71` | "Volume fields mostly None; thin" is carried across from the Polymarket pull and colours the reading of the Kalshi evidence, which is the opposite of thin: `KXFEDDECISION-26OCT-H0` has **502,083 contracts of volume, 360,307 open interest and 298,901 in the last 24 hours**. Every `updated_time` reads 2026-04-09 across all 131 markets, including January-2027 strikes that cannot have existed then — the field is series metadata, not a quote stamp (the reverse of the inference A01-04/A12-14 drew on the ABNB ladder). | Both JSONs parsed in full; block B10/1. | Say plainly that the Fed ladders are deep and live, and give them more weight, not less. They price a 4Q26 cut at **0.01–0.02**, while the log's "emergency cuts" branch is a 4Q26 *average* T-bill of 3.25% — roughly three cuts — carried at a weight of 0.02. That branch belongs at ~0.005. |
| A16-19 | B10 | minor | `log:93,94`; `forecast.sensitivity` | Two §7 rows do not replay at mixture level: β 0.94 gives **0.014**, not 0.03; funds held flat y/y gives **0.089**, not 0.07. The other six land within a point, so the table is mixture-level, not route-level — worth stating, because B09's equivalent table is not. | Reproduction of the mixture under each reversal. | Correct the two rows and state the level the table is computed at. |
| A16-20 | B08 | minor | `log:127,129`; `forecast.impact.margin_fy27_pp`, `stock_usd_per_share`; claim 14 | Three arithmetic slips in one table. (i) "~−0.9pp on the Street's $15.8bn" is not derivable: +$100M of cost on the Street's $15,819M revenue is **−0.63pp**, the same as on the team's base — what widens is the team-vs-Street margin *gap*, from 1.81pp to 2.44pp. (ii) The FY26 row is −0.08pp, published as −0.1. (iii) The stock level effect uses **620m** diluted shares against M7's FY27 573m, the line build's 4Q26 586.4m, and the 573m used by B09 and B10 in this same batch (R04 uses 591.7m): at 573m the level effect is −$2.79, not −$2.58. | `docs/margin-build/SYNTHESIS.md:338` (Street FY27 5,766.1 / 36.45%); `40_lines_quarterly.csv` `diluted_shares_m`; `M7_below_ebitda_annual_forecasts.csv` FY2027 573.04. Block B08/4. | Publish −0.63pp against both bases and say the *gap* widens to 2.4pp; use one share count across the run. The EPS row (−$0.14 = 0.0014 × $100M) is correct and stays — it is the only §9 EPS row in the batch that applies the coefficient exactly once, and B09's and B10's GAAP-EPS rows (−$0.202 and −$0.130) both replay exactly. |
| A16-21 | B08 | minor | `log:102`; `forecast.sensitivity` last row | "If the commitments table counts as a quantification: ~0.85" understates the log's own largest convention risk. The FY26 10-K **will** restate a schedule; the FY25 version already implies ~+$246M for 2027 against the 2026 bucket. If a resolver counts it the question is ~**0.97**, not 0.85. | FY25 10-K Note 13: 2026 $219M against 1–3 years $930M ≈ $465M/yr. | Publish ~0.95–0.97 and move the row to the top of §7. It makes the RESUME's request — settle convention (2) with Krish before 2 October — the log's first order of business, which is correct. |
| A16-22 | B08 | minor | `log:24,28` (convention 1); `model:47–48` | Two thresholds for one question. The registry gives both "≥ +18% y/y" and "$575M"; $487M × 1.18 = $574.66M. The model computes both (`leg2_p_base` 0.2598 for ≥$575M, `leg2_p_yoy_ge_18` 0.2642 for ≥18%) and the log quotes only the first without noting that the two differ by 0.4 points. | `b08_results.csv` rows 4 and 8. | State that convention (1) adopts the dollar threshold and that the percentage reading is 0.4 points higher. Releases print whole millions, so no realistic print falls between the two. |
| A16-23 | B17 | minor | `model:40–41` (`strict` branch) | The strict-convention variant multiplies route (b) by an unsourced **0.55**. Nothing in the record supports that split between FY-worded and quarter-worded statements; the only two forward take-rate objects of the last print went one each way (the 2Q26 call FY-worded, the 2Q26 letter quarter-worded). | `model:41`; the log gives no derivation. | Either derive it from the letter/call record (1 of 2 in the last print; 4 of 13 letters carry an FY-form sentence) or label the strict number a judgement. On my route inputs the strict companion is **0.31**, not 0.33. |
| A16-24 | B17 | minor | `log:37` (claim 5); `sources/` | Claim 5 is the newest load-bearing source in the log (29–31 Aug, 17 days old) and **nothing was saved**. `sources/` holds only the shared Kalshi and Polymarket pulls and the query log; the Skift article exists as a summary line, and the Bloomberg piece was never fetched. The "−0.8pt scaling has circulated but is unverified (paywalled)" row cites no retrievable object at all. This is A12-11 recurring. | Listed `sources/` in all four folders; the three ABNB Kalshi and Polymarket files are byte-identical copies of one fetch shared across B08/B09/B17. | Save whatever can still be fetched, and mark the unsaveable rows "search snippet, unsaved" rather than citing a URL. Do not let the "−0.8pt" figure enter the memo under any label. |
| A16-25 | B17 | minor | `model:24–26`; `b17_results.csv` row `tr_4q26_short_case_rev_2966_gbv_scaled` | The short-case row is tautological: GBV is scaled by revenue ÷ 3,178.1, so the take rate is identically the team's **13.8256%**, to four decimals. The log discloses the point in prose ("the short case… keeps the take rate on the team path") but the CSV row reads as an independent scenario and the §6 companion quotes from that table. | `b17_results.csv`: the `team_bridge_v3` and `short_case` rows are the same number. | Drop the row or rename it `short_case_take_rate_held_by_construction`. |

## B08 — what the log does well and should keep

The evidence assembly is the best in the batch. Every number in claim 1 reproduces from `02_panel_quarterly.csv` to the decimal — the six quarterly cost-of-revenue values, the GBV series, all eight CoR/GBV ratios, the ten y/y ratio changes with mean −1.00% and sd 3.74%, and the FY25 $2,086M less 9M25 $1,599M reconciliation that produces the registry's $487M base. Claim 3 reproduces the whole of the line build's 4Q26 cost stack, scenario by scenario, including the evidence-only $548.8M and the four bear/bull variants. Claim 6's 10-K schedule is verbatim. Claim 5's 2Q26 MD&A sentence is verbatim, including the offsetting amortisation clause that the residual is meant to carry.

The best single decision in the log is convention (2) — the 10-K commitments table does not count as a management quantification — made **before** the modelling, stated as a convention rather than smuggled in, and priced in §7. That is exactly the discipline the flow is for, and the RESUME correctly identifies it as the thing to settle with a human.

Claim 4 deserves to survive into the memo unchanged: the line build's own note calls the hosting run-rate step "the least-sourced number in the build", and a forecast that quotes its own model's self-criticism is more useful to a judge than one that does not. My disagreement (A16-01) is not that the criticism is wrong but that it belongs in the line build, not only in the risk table.

The strongest case against the published 0.38 is that the memo's own model already says Yes. The 0.45 weight that pulls the number down is placed on the one branch management has said its guidance does not assume.

## B09 — what the log does well and should keep

The SBC correction is the best piece of source work in the batch and must be preserved verbatim. `abnb_driver_history_quarterly.csv` carries 4Q23 $270M, 4Q24 $400M and 4Q25 $400M; the releases print **$290M, $368M and $411M**, and FY25 $1,592M reconciles only with $411M. The log found this, stated it as convention (2), showed the reconciliation, kept the threshold fixed at $500M because the threshold is absolute, and said plainly that the registry line is wrong. Every figure verifies against the 4Q24, 4Q25 and 2Q26 letters. That correction is worth more than the forecast: it is a repo data error affecting anything that uses the SBC series, including the guidance ledger (A16-04).

The Q4/Q2 seasonal construction is the right object for this question and its evidence is unusually clean: 0.954, 0.963, 0.969 in three consecutive years, sd 0.0078, against a required 1.027 that has been seen once, in the post-IPO double-trigger regime. Widening the sd to 0.035 — 4.5× the observed — before computing is the honest way to handle three observations, and it is why the route survives audit.

Claim 3's management record is complete and correctly quoted across three February letters, and the recognition that the FY26 sentence ("growth rate of SBC and headcount will be lower than 2025") is already tracking a miss on the half — 1H26 +14.7% against FY25's +13.1% — is the kind of fact the memo can use even though the question is immaterial.

The strongest case against the published 0.10 is that its highest-weighted upside route rests on a guidance-miss record that the log's own correction dissolves.

## B10 — what the log does well and should keep

This is the most disciplined log of the four. The extreme-probability gate at 0.05 is triggered, declared, and audited in the form the skill asks for: criteria re-read, four named edge cases with individual weights, residual sum, and a stated reason for not going lower. Every one of the edge cases is a real resolution risk rather than filler.

The evidence is exact. The interest-income series matches the 2Q26 letter's nine-quarter row value for value; FY25 $705M and FY24 $818M match the 4Q25 letter; the cash and funds-held balances match `02_panel_quarterly.csv`; β = 0.8765 and the backtest MAEs match `M7_parameter_sheet.csv` and the M7 note; the FRED quarter means reproduce to three decimals; all eleven Kalshi quotes are exactly as stated.

The single best sentence in the batch is §9's: "if the RNPL cash-timing point is made, make it on unearned fees (C12), not on interest income, where rates dominate and are now a tailwind." That is the correct reading of a mechanism the short thesis wants to be true and that the arithmetic says is too small — funds held still grew +10.5% y/y at 2Q26 with RNPL above 20% of GBV, and a −20% overlay is worth about a fifth of the required miss. The pre-mortem's observation that the memo's own success raises this item (a sell-off invites a buyback upsize, which drains the earning base) is the right kind of self-aware correlation and should be kept.

The strongest case against the published 0.05 is that it is too **high**: the only route to Yes that does not require a Fed reversal is modelled with the cash draw applied a quarter early.

## B17 — what the log does well and should keep

The conventions are the best-drafted in the batch and all six are stated before the modelling. Convention (3)'s line — RNPL booking-versus-stay timing named alone counts only under leg (a), while incentives or new businesses named as reducing the forward take rate counts under leg (b) — is a rule a resolver could apply on 5 November without calling anyone, and it is the right cut of a question whose whole difficulty is wording. Publishing the strict-convention number alongside the headline is the honest way to carry convention risk.

The record work verifies completely. All thirteen letter take-rate sentences match `02_guidance_ledger.csv` row for row, with the correct direction counts (1 lower, 4 flat/similar/in-line, 8 higher) and the correct realised y/y points including the three consecutive undershoots (−69, −47, −10bp). The decision to exclude the 2021–22 sequential-form sentences as seasonal is right and is argued. Mertz's 2Q26 paragraph is verbatim to the word, and the observation that "this is the first print in which incentives were named as reducing the take rate" is both true and the pivot of the question.

Claim 3's May-to-August arc is the insight the memo should carry: between 1Q26 and 2Q26 the FY26 take-rate guidance moved from "expected to lift our full-year take rate" and "modest upside… from both the migration to the single fee structure as well as our Insurance Program" to "relatively flat… accounting for… higher customer incentives". Management changed its own forward take-rate story in one quarter, in the direction the short needs, and said why. That is a better memo line than the probability.

The strongest case against the published 0.42 is in the team's own model and the log does not make it: the adopted path has FY26 take rate up 13bp against management's "relatively flat", so the likelier 5 November FY sentence is "up slightly", not a repeat of the incentives clause.

## Independent audit numbers

These are audit judgements built from the same repository inputs, not blinded second forecasts. No tradable market exists for any of the four objects; I confirmed that against the saved Kalshi and Polymarket pulls rather than refreshing them.

**B08: P(Yes) = 0.45.** Judgmental 80% interval **0.32–0.58**; leg 2 = **0.32**, median 4Q26 cost of revenue **$563M**; leg 1 | leg 2 No = 0.19.
Leg 2 on the line build's own formula with the hosting mixture re-weighted to **0.33 / 0.37 / 0.30** — because the evidence-only branch is the "no further ramp" case that Mertz has said the guidance does not assume (A16-11), and because the 10-K's 2026 minimum bounds a commitment, not an amortisation schedule (A16-10) — and with outcome-scale rather than analyst-dispersion spreads (gbv_sd 800, rate_sd 0.05, A16-12): **0.324**. Leg 1 at **0.19** rather than 0.18, because the February letter must explain an FY27 margin guide that F03 puts at 0.38 in bucket (d) and the Feb 2025 precedent quantified the investment when it cut the floor, against a record of 0 of 5 February letters naming an AI or hosting dollar figure. Union: 0.324 + 0.676 × 0.19 = **0.452**.
The gap to the published 0.38 is entirely the hosting mixture and the spreads. Note which direction the memo's own model points: at the line build's base path this question resolves Yes.

**B09: P(Yes) = 0.08.** Judgmental 80% interval **0.04–0.14**; companion median 4Q26 SBC **$465M**, P(≥$480M) 0.27, P(≤$450M) 0.29.
Routes: seasonal 487 × N(0.962, 0.035) + N(0, 8) = **0.047** (the sd is already 4.5× the three-year observed 0.0078); y/y 411 × (1 + N(13.2, 6)/100) = **0.078**; the FY26-sentence overlay recalibrated to P(miss) 0.15 × N(+4, 3) after A16-04 = **0.128**, at a weight of 0.10 rather than 0.20 because it is a re-expression of the y/y route, not a third estimate (A16-15). Blend 0.45 / 0.45 / 0.10 = 0.069, plus **0.010** for the unmodelled discrete-grant tail = **0.079**.
The question needs +21.7% y/y or a Q4/Q2 ratio of 1.027 in a regime that has printed 0.954–0.969 three years running and whose double-trigger step is spent. It is immaterial at any value in the interval; the memo should carry the $411M correction and drop the probability.

**B10: P(Yes) = 0.04.** Judgmental 80% interval **0.015–0.08**; companion median **$177M** (+9% y/y), P(≤$162M, any decline) **0.16** base regime / **0.21** on the mixture.
The base regime is decisive and the log's arithmetic is right: the 4Q26 T-bill is +10% y/y against 4Q25's 3.726 average (Kalshi: 0.82 that the December upper bound is above 4.00), the earning base is +6% at ~$19.6bn, and the rule gives $177M against a $145.8M threshold — a 3.3-sigma miss. P = **0.013**. Ramping the buyback draw (A16-06) gives conditionals of 0.062 at $1.5bn and 0.207 at $3bn; cutting the emergency-easing branch from 0.02 to 0.005, because the market prices a *single* December cut at 0.01–0.02 and this branch needs about three (A16-18), and adding ~0.006 for an unmodelled large cash draw (M&A, special dividend) and ~0.005 for a presentation change: **0.036 → 0.04**.
Gate audit at 0.04: the residuals that keep it off 0.02 are the buyback branch (correlated with the memo's own thesis) and the unmodelled cash-draw tail. Immaterial at every value.

**B17: P(Yes) = 0.38.** Judgmental 80% interval **0.26–0.52**; strict-convention companion **0.31**; E[stock | Yes] **−$2.5**, EV **−$0.95**.
Routes at ρ 0.5: (a) the letter's 4Q26 sentence reads "lower" **0.13** — 1 of 13 letters, 1 of 3 Q3 letters, against an easy 4Q25 comp (the base is 47bp depressed) and a team path of +21bp; (b) incentives, new businesses or the pilot named as reducing a qualifying period's take rate = P(topic) **0.65** (A16-08: the last two Q3 calls were silent, and there is no letter door) × P(qualifies) **0.52**; (c) an explicit FY27 decline **0.06**. Union **0.426**. Blended 0.65 on that decomposition and 0.35 on the base rate of 0.29 (1 of 5 prints of the new-business regime, Laplace) — with **no weight on a flat prior**, which is not an anchor (A16-13): **0.379**.
The reason to sit below the published 0.42 rather than above it is A16-09: the team's own adopted path has FY26 take rate at 13.535% against FY25's 13.407%, i.e. **up 12.8bp** against management's "relatively flat", so the likelier 5 November FY sentence is "up slightly". If the memo wants a take-rate line, the one worth carrying is not this probability but the May-to-August arc in claim 3.

## Cross-question coherence settled by this audit

*B17 against R04 and C11.* The three are one object seen three ways and should share one taxonomy of management's take-rate language. R04 revision 2 (0.52) prices the **gross** statement (fee migration is accretive); B17 prices the **net** statement (incentives reduce it); C11 revision 2 (0.76) prices the **printed** 3Q26 ratio. They are not exclusive — the 2Q26 call contains the gross and the net clause in one sentence, which is why R04's A10-04 rescoring of that print to No and B17's scoring of it to Yes are both correct. Two obligations follow: B17 must re-base claim 7 from 0.58 to **0.52**, and B17's §9 must adopt R04's `split_by_form` structure, after which the two impact tables are mirrors (+$2.2 and −$2.5 expected stock, EV +$1.1 and −$1.0) instead of one borderline and one "material". C11's 0.76 is in tension with B17's route (b) and the tension should be stated, not resolved by fiat: if the 3Q26 take rate prints above +22bp, the FY26 sentence more likely reads "up slightly".

*B08 against the line build.* These cannot both stand as published. The line build's adopted 4Q26 hosting of $100.2M is the team's number in `docs/margin-build/notes/40_line_build.md` and in the FY26 margin cushion; B08's mixture mean is $82.3M. One of the two must move before 2 October, and the same choice sets the 3Q26 cost-of-revenue monitoring threshold ($641M reconciled against $612M evidence-only), which is the first read on 5 November for both documents.

*B09 and B10 against M7.* Both use M7 correctly and both are immaterial, but their §9 EPS rows are the only two in the batch built on GAAP EPS below adjusted EBITDA, and both use 573m shares while B08 uses 620m and R04 uses 591.7m. One share count, published once, in the brief.

*The batch against brief rule 7.* Four questions, four anchors, zero markets. The correct output is `anchor: null` four times with the internal objects labelled as comparisons — and then the batch's `|final − anchor|` column in SYNTHESIS.md is empty for all four, which is the honest presentation.

## Reproduction script

Read-only, stdlib plus pandas, no numpy, no scipy, no network, no file writes. Run from the repository root with `python -B docs/pitch-forecasts/audits/A16-reproduce.py`. The saved models use numpy; this script re-implements all four with `random` at N = 200,000 and reproduces their published figures to within Monte Carlo error (B08 leg 2 0.2586 against 0.2598; B09 blend 0.0893 against 0.0904; B10 base 0.0132 against 0.01365; B17 union 0.4824 against 0.4812).

```python
"""A16 read-only reproduction (B08, B09, B10, B17 + the R04/C11 coherence checks).
Run from the repository root: python -B docs/pitch-forecasts/audits/A16-reproduce.py
Requires stdlib + pandas only (no numpy, no scipy). Writes nothing; uses no network.
The saved models use numpy; this script re-implements them with `random` and reproduces
their published figures to within Monte Carlo error (N = 200,000).
"""
from pathlib import Path
import html, json, math, random, re, statistics as st
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
B10 = Q / "bonus-interest-income-falls"
N = 200_000


def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def text(p):
    s = Path(p).read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def dmargin(dR, dE, R, E):
    return 100 * (E + dE) / (R + dR) - 100 * E / R


FY26R, FY26E, FY27R, FY27E = 14268.0, 5098.0, 15829.0, 5483.0
print("=" * 78)
print("0. line-build annuals behind every section 9 table")
print("   FY26 rev %.0f ebitda %.0f margin %.3f%% | FY27 rev %.0f ebitda %.0f margin %.3f%%"
      % (FY26R, FY26E, 100 * FY26E / FY26R, FY27R, FY27E, 100 * FY27E / FY27R))

# ======================================================================= B08
print("=" * 78)
print("B08 / 1. claims 1 and 3 against the repo")
p = pd.read_csv(ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv")
h = p[p.quarter.isin(["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
                      "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"])]
print("   panel cor_cash 1Q25-2Q26:", [int(x) for x in h.cor_cash.tail(6)])
print("   FY25 %d ; 9M25 %d ; 4Q25 %d  (registry base 487)"
      % (h[h.quarter.str.endswith("25")].cor_cash.sum(),
         h[h.quarter.isin(["1Q25", "2Q25", "3Q25"])].cor_cash.sum(), 487))
ratio = list(h.cor_cash / h.gbv_busd / 10)
ryoy = [(ratio[i] / ratio[i - 4] - 1) * 100 for i in range(4, len(ratio))]
print("   CoR/GBV y/y (n=%d) mean %.2f sd %.2f   (log: -1.0 / 3.7)"
      % (len(ryoy), st.mean(ryoy), st.stdev(ryoy)))
print("   needed ratio change at GBV +12.7pct = %.2f ; observed >= that in %d of %d quarters"
      % ((1.18 / 1.127 - 1) * 100, sum(1 for x in ryoy if x >= 4.70), len(ryoy)))
lb = pd.read_csv(ROOT / "data/processed/margin_build/40_line_build/40_lines_quarterly.csv")
q4 = lb[lb.quarter == "4Q26"][["scenario", "cor_fees", "cor_chargebacks", "cor_hosting",
                               "cor_other", "cor_cash", "cor_cash_yoy_pct"]]
print("   40_lines_quarterly 4Q26 cost of revenue by scenario:")
print(q4.to_string(index=False))
print("   scenarios at or above the 575 threshold: %d of %d" % ((q4.cor_cash >= 575).sum(), len(q4)))

print("B08 / 2. leg-2 Monte Carlo (stdlib replay of b08_model.py)")


def leg2(mix=(0.45, 0.35, 0.20), gbv_sd=650.0, rate_sd=0.04, gbv_mu=22990.0,
         rate_mu=1.756, resid_sd=12.0, thr=575.0, seed=8):
    rng = random.Random(seed)
    cut1, cut2 = mix[0], mix[0] + mix[1]
    hits = 0
    vals = []
    for _ in range(N):
        fees = rng.gauss(gbv_mu, gbv_sd) * rng.gauss(rate_mu, rate_sd) / 100.0
        cb = rng.gauss(0.72 * 132.7 / 3.65, 4.0)
        other = rng.gauss(0.36 * 132.7, 3.0)
        u = rng.random()
        step = rng.gauss(15, 5) if u < cut1 else (rng.gauss(30, 8) if u < cut2 else rng.gauss(45, 10))
        cor = fees + cb + 56.0 + max(step, 0.0) + other + rng.gauss(0, resid_sd)
        vals.append(cor)
        hits += cor >= thr
    vals.sort()
    return hits / N, vals[N // 2]


for lbl, kw in (("published 0.45/0.35/0.20, gbv_sd 650", {}),
                ("audit 0.33/0.37/0.30, gbv_sd 800, rate_sd 0.05",
                 dict(mix=(0.33, 0.37, 0.30), gbv_sd=800.0, rate_sd=0.05))):
    p2, med = leg2(**kw)
    print("   %-46s p2 %.4f median %.0f | total at leg1|no 0.18 %.4f / 0.19 %.4f"
          % (lbl, p2, med, p2 + (1 - p2) * 0.18, p2 + (1 - p2) * 0.19))
print("   model values: p2 0.2598, median 559.2, total 0.3930; published headline 0.38")

print("B08 / 3. FY25 10-K purchase-obligation schedule (claim 6)")
t = text(ROOT / "data/raw/filings/abnb_10k_FY2025.htm")
i = t.find("Purchase obligations $")
print("   ", t[i - 150:i + 250].strip())

print("B08 / 4. section 9 arithmetic")
print("   FY26 +12 of cost, revenue unchanged -> %+.3fpp (log -0.1)" % dmargin(0, -12, FY26R, FY26E))
print("   FY27 +100 of cost -> %+.3fpp (log -0.6); on Street revenue 15819 -> %+.3fpp (log ~ -0.9)"
      % (dmargin(0, -100, FY27R, FY27E), -100.0 / 15819.0 * 100))
print("   EPS -100 x 0.0014 = %+.3f (log -0.14): one application, correct" % (-100 * 0.0014))
print("   level effect -100 x 16 / 573m = %+.2f ; / 620m as the log uses = %+.2f"
      % (-1600 / 573, -1600 / 620))

# ======================================================================= B09
print("=" * 78)
print("B09 / 1. SBC series: the releases against the repo CSVs")
for f, lbl in ((ROOT / "data/raw/letters/4Q25_d58192dex991.htm", "4Q25 letter"),
               (ROOT / "data/raw/letters/4Q24_d915198dex991.htm", "4Q24 letter")):
    s = text(f)
    j = s.find("Stock-based compensation expense $")
    print("   %s -> %s" % (lbl, s[j:j + 55].strip()))
s = text(ROOT / "data/raw/letters/2Q26_d70413dex991.htm")
j = s.find("Stock-based compensation expense 382")
print("   2Q26 letter nine-quarter row -> %s" % s[j:j + 60].strip())
dh = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
for qq, printed in (("4Q23", 290), ("4Q24", 368), ("4Q25", 411)):
    print("   %s: driver_history %.0f | 02_panel sbc_total_is %.0f | printed release %d"
          % (qq, dh.loc[dh.quarter == qq, "stock_based_comp_total_musd"].iloc[0],
             p.loc[p.quarter == qq, "sbc_total_is"].iloc[0], printed))

print("B09 / 2. the guidance ledger's sbc_yoy_pct actuals are on the DRIVER-HISTORY basis")
g = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_ledger.csv")
print(g[g.metric == "sbc_yoy_pct"][["print_quarter", "target_period", "value_mid", "actual",
                                    "outcome"]].to_string(index=False))
print("   printed basis: FY23 %.2f  FY24 %.2f  FY25 %.2f"
      % ((1120 / 930 - 1) * 100, (1407 / 1120 - 1) * 100, (1592 / 1407 - 1) * 100))
print("   driver basis : FY23 %.2f  FY24 %.2f  FY25 %.2f  <- the ledger's 18.28 / 30.82"
      % ((1100 / 930 - 1) * 100, (1439 / 1100 - 1) * 100, (1581 / 1439 - 1) * 100))
print("   so FY23 ~20pct was MET, FY24 ~20pct missed by 5.6 points not 10.8, 3Q24 ~25pct was MET")

print("B09 / 3. seasonal and y/y routes")
sbc = dict(zip(["1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24",
                "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
               [195, 247, 234, 254, 240, 304, 286, 290, 295, 382, 362, 368, 358, 424, 399, 411,
                410, 487]))
rat = [sbc["4Q%d" % y] / sbc["2Q%d" % y] for y in (22, 23, 24, 25)]
print("   Q4/Q2 %s | mean4 %.4f sd4 %.4f | mean 23-25 %.4f sd %.5f | needed %.4f"
      % ([round(x, 4) for x in rat], st.mean(rat), st.stdev(rat), st.mean(rat[1:]),
         st.stdev(rat[1:]), 500 / 487))
print("   needed y/y on the printed 4Q25 411 = %.2f pct (on the registry's 400 = 25.0)"
      % ((500 / 411 - 1) * 100))


def rA(mu, sd, seed=1):
    rng = random.Random(seed)
    return sum(1 for _ in range(N) if 487 * rng.gauss(mu, sd) + rng.gauss(0, 8) >= 500) / N


def rB(mu, sd, seed=2):
    rng = random.Random(seed)
    return sum(1 for _ in range(N) if 411 * (1 + rng.gauss(mu, sd) / 100) >= 500) / N


def rC(pmiss=0.20, mu=6.0, sd=3.0, seed=3, q3=399 * 1.132):
    rng = random.Random(seed)
    k = 0
    for _ in range(N):
        gg = rng.gauss(mu, sd) if rng.random() < pmiss else rng.gauss(-1.5, 2.5)
        k += (1592 * (1 + (13.1 + gg) / 100) - 897 - q3 + rng.gauss(0, 10)) >= 500
    return k / N


A = rA(st.mean(rat[1:]), 0.035)
Bm7 = rB(13.18, 6.0)
C = rC()
print("   A(.962,.035) %.4f | B(M7 13.2 +- 6) %.4f | C(miss .20 / +6) %.4f -> blend %.4f, +0.02 = %.4f"
      % (A, Bm7, C, 0.4 * A + 0.4 * Bm7 + 0.2 * C, 0.4 * A + 0.4 * Bm7 + 0.2 * C + 0.02))
print("   model blend 0.0904; published headline 0.10")
print("   section 7 replay: all-four %.3f (pub 0.13) | sd 0.02 %.3f (pub 0.05) | last-8 %.3f (pub 0.22)"
      " | 1H26 %.3f (pub 0.06)"
      % (0.4 * rA(st.mean(rat), st.stdev(rat)) + 0.4 * Bm7 + 0.2 * C + 0.02,
         0.4 * rA(st.mean(rat[1:]), 0.02) + 0.4 * Bm7 + 0.2 * C + 0.02,
         0.4 * A + 0.4 * rB(17.14, 6.86) + 0.2 * C + 0.02,
         0.4 * A + 0.4 * rB(14.7, 4.0) + 0.2 * C + 0.02))
Cc = rC(0.15, 4.0)
print("   corrected C (0.15 x N(+4,3)) %.4f -> blend .45/.45/.10 + 0.010 = %.4f  [audit number]"
      % (Cc, 0.45 * A + 0.45 * Bm7 + 0.10 * Cc + 0.010))
print("   section 9: +140 FY27 SBC x (1 - 0.175) / 573m = %+.3f EPS (log -0.20)" % (-140 * 0.825 / 573))

# ======================================================================= B10
print("=" * 78)
print("B10 / 1. interest-income series, threshold, rates")
s = text(ROOT / "data/raw/letters/2Q26_d70413dex991.htm")
j = s.find("Interest income (226)")
print("   2Q26 letter nine-quarter row -> %s" % s[j:j + 70].strip())
print("   threshold = 0.90 x 162 = %.1f" % (0.9 * 162))
d = pd.read_csv(B10 / "sources/fred_DTB3_20260917T082052Z.csv")
d.columns = ["date", "v"]
d["v"] = pd.to_numeric(d.v, errors="coerce")
d = d.dropna()
d["q"] = pd.to_datetime(d.date).dt.to_period("Q")
print("   DTB3 quarter means:", {str(k): round(v, 3) for k, v in d.groupby("q").v.mean().tail(4).items()})
f = pd.read_csv(B10 / "sources/fred_DFEDTARU_20260917T082052Z.csv")
print("   DFEDTARU last row %s = %s ; DTB3 last row %s = %.2f -> the 16 Sep hike is NOT in the snapshot"
      % (f.iloc[-1, 0], f.iloc[-1, 1], d.iloc[-1].date, d.iloc[-1].v))
kf = json.loads((B10 / "sources/kalshi_KXFED_open_20260917T082121Z.json").read_text(encoding="utf-8"))
kd = json.loads((B10 / "sources/kalshi_KXFEDDECISION_open_20260917T082121Z.json").read_text(encoding="utf-8"))
for m in kf["markets"]:
    if m["ticker"] in ("KXFED-26OCT-T3.75", "KXFED-26DEC-T4.00", "KXFED-26DEC-T4.25"):
        print("   %-18s bid %.2f ask %.2f vol %.0f oi %.0f vol24 %.0f updated %s"
              % (m["ticker"], float(m["yes_bid_dollars"]), float(m["yes_ask_dollars"]),
                 float(m["volume_fp"]), float(m["open_interest_fp"]),
                 float(m["volume_24h_fp"]), str(m["updated_time"])[:10]))
oct0 = [m for m in kd["markets"] if m["ticker"] == "KXFEDDECISION-26OCT-H0"][0]
print("   updated_time is 2026-04-09 on all %d KXFEDDECISION and all %d KXFED markets, newly listed"
      % (len(kd["markets"]), len(kf["markets"])))
print("   27JAN strikes included -> metadata, not a quote stamp; 26OCT-H0 volume_24h = %.0f, so live."
      % float(oct0["volume_24h_fp"]))

print("B10 / 2. the M7 rule replay and the buyback-draw ramp")


def b10(r_mu=4.10, r_sd=0.15, beta_mu=0.88, beta_sd=0.045, c3m=12100.0, c4m=12000.0,
        c_sd=500.0, fh=0.127, fh_sd=0.03, rnpl=0.10, resid=0.05, d3=0.0, d4=0.0, seed=10):
    rng = random.Random(seed)
    thr = 0.9 * 162
    k = k162 = 0
    tot = []
    for _ in range(N):
        r = rng.gauss(r_mu, r_sd)
        b = rng.gauss(beta_mu, beta_sd)
        gg = rng.gauss(fh, fh_sd)
        rn = rng.uniform(0, rnpl) if rnpl > 0 else 0.0
        base = ((rng.gauss(c3m, c_sd) - d3 + 7209 * (1 + gg) * (1 - rn))
                + (rng.gauss(c4m, c_sd) - d4 + 6959 * (1 + gg) * (1 - rn))) / 2
        ii = b * r / 100 * base / 4 * (1 + rng.gauss(0, resid))
        tot.append(ii)
        k += ii <= thr
        k162 += ii <= 162
    tot.sort()
    return k / N, k162 / N, tot[N // 2]


base, b162, med = b10()
print("   base regime P(<=145.8) %.4f | P(<=162, any decline) %.4f | median %.0f"
      % (base, b162, med))
print("   model values 0.01365 / -- / 176.7 ; the log's companion states P(<=162) about 0.13")
flat15 = b10(d3=1500, d4=1500)[0]
flat30 = b10(d3=3000, d4=3000)[0]
ramp15 = b10(d3=750, d4=1500)[0]
ramp30 = b10(d3=1500, d4=3000)[0]
cuts = b10(r_mu=3.25, r_sd=0.2)[0]
print("   upsize conditionals: flat 1.5bn %.4f / 3bn %.4f  vs ramped 1.5bn %.4f / 3bn %.4f"
      % (flat15, flat30, ramp15, ramp30))
print("   mixture .88/.07/.03/.02 published %.4f | ramped %.4f"
      % (.88 * base + .07 * flat15 + .03 * flat30 + .02 * cuts,
         .88 * base + .07 * ramp15 + .03 * ramp30 + .02 * cuts))
print("   section 9: -90 FY27 x (1 - 0.175) / 573m = %+.3f EPS (log -0.13)" % (-90 * 0.825 / 573))

# ======================================================================= B17
print("=" * 78)
print("B17 / 1. the 13-letter take-rate direction record (claim 1)")
tr = g[g.metric == "take_rate_yoy_pts"]
print("   ledger rows %d | 'lower' %d | flat/similar/in-line %d | higher/above %d"
      % (len(tr), sum(1 for x in tr.quote if "lower" in x),
         sum(1 for x in tr.quote if re.search(r"similar|flat|in-line", x)),
         sum(1 for x in tr.quote if re.search(r"higher|above", x))))
print("   realised y/y pts:", [None if pd.isna(x) else round(x, 2) for x in tr.actual])

print("B17 / 2. the Q3-call record, the gate route (b) must pass")
for qq in ("3Q21", "3Q22", "3Q23", "3Q24", "3Q25", "4Q25", "1Q26", "2Q26"):
    s = text(ROOT / ("data/raw/transcripts/web/%s.html" % qq))
    firms = len(set(re.findall(r"(Barclays|Goldman|Morgan Stanley|Bernstein|Jefferies|Truist|Citi|"
                               r"Deutsche|Wells Fargo|Piper|Evercore|Susquehanna|BTIG|Mizuho|Cowen|"
                               r"UBS|KeyBanc|Benchmark|Oppenheimer)", s)))
    print("   %s call chars %6d | Q&A firms %2d | 'take rate' %2d | 'moneti' %d | 'incentive' %d"
          % (qq, len(s), firms, len(re.findall(r"take rate", s, re.I)),
             len(re.findall(r"moneti", s, re.I)), len(re.findall(r"incentive", s, re.I))))
inc = {}
for f in sorted((ROOT / "data/raw/letters").glob("*.htm")):
    s = text(f)
    inc[f.name[:4]] = len(re.findall(r"incentive", s, re.I))
print("   letters from 1Q23 on that contain the word 'incentive': %s"
      % [k for k, v in sorted(inc.items()) if v > 0 and k[-2:] >= "23"])
print("   so route (b) has no letter door, and the Q3 call was silent in 2 of the last 3 years")

print("B17 / 3. the 2Q26 sentence (claim 2), verbatim")
s = text(ROOT / "data/raw/transcripts/web/2Q26.html")
j = s.find("For the full year, we expect our implied take rate")
print("   ", s[j:j + 390].strip())
print("   (CFO prepared-remarks outlook block, not Q&A)")

print("B17 / 4. route union replay")


def sim(pa=0.12, pt=0.80, pq=0.50, pc=0.06, rho=0.5, strict=None, seed=17):
    rng = random.Random(seed)
    k = 0
    r2 = math.sqrt(1 - rho ** 2)
    for _ in range(N):
        z0 = rng.gauss(0, 1)
        a = Phi(z0) < pa
        b = Phi(rho * z0 + r2 * rng.gauss(0, 1)) < pt and rng.random() < pq
        if b and strict:
            b = rng.random() < strict
        c = Phi(rho * z0 + r2 * rng.gauss(0, 1)) < pc
        k += a or b or c
    return k / N


print("   published (.12/.80/.50/.06, rho .5) %.4f (model 0.4812) | strict x0.55 %.4f (model 0.3344)"
      % (sim(), sim(strict=0.55)))
print("   audit     (.13/.65/.52/.06, rho .5) %.4f | strict %.4f"
      % (sim(0.13, 0.65, 0.52), sim(0.13, 0.65, 0.52, strict=0.55)))

print("B17 / 5. section 9 arithmetic, the R04 mirror, and the team's own FY26 take rate")
print("   FY26 -30 rev / -27 ebitda -> %+.3fpp (log -0.2) | FY27 -170 / -153 -> %+.3fpp (log -1.0)"
      % (dmargin(-30, -27, FY26R, FY26E), dmargin(-170, -153, FY27R, FY27E)))
r04 = json.loads((Q / "risk-single-fee-take-rate-accretion-stated/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
c11 = json.loads((Q / "q3-take-rate-above-1810/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
print("   R04 mirror +23 rev / +20.7 ebitda -> %+.3fpp ; R04 publishes %s (computed correctly there)"
      % (dmargin(23, 20.7, FY27R, FY27E), r04["impact"]["margin_fy27_pp"]))
print("   R04 revision %s p %.2f (B17 claim 7 quotes 0.58) | C11 revision %s p %.2f"
      % (r04["revision"], r04["final"]["p"], c11["revision"], c11["final"]["p"]))
g26 = float(p.loc[p.quarter == "1Q26", "gbv_busd"].iloc[0]) + float(p.loc[p.quarter == "2Q26", "gbv_busd"].iloc[0])
r26 = float(p.loc[p.quarter == "1Q26", "revenue"].iloc[0]) + float(p.loc[p.quarter == "2Q26", "revenue"].iloc[0])
lb26 = lb[(lb.scenario == "base") & (lb.quarter.isin(["3Q26", "4Q26"]))]
g25 = sum(float(p.loc[p.quarter == q_, "gbv_busd"].iloc[0]) for q_ in ("1Q25", "2Q25", "3Q25", "4Q25"))
r25 = sum(float(p.loc[p.quarter == q_, "revenue"].iloc[0]) for q_ in ("1Q25", "2Q25", "3Q25", "4Q25"))
tr26 = (r26 + lb26.revenue.sum()) / ((g26 + lb26.gbv_busd.sum()) * 1000) * 100
print("   team FY26 implied take rate %.3f%% vs FY25 %.3f%% = %+.1fbp -- management guides 'relatively flat'"
      % (tr26, r25 / (g25 * 1000) * 100, (tr26 - r25 / (g25 * 1000) * 100) * 100))
forms = (("repeat of the standing 2Q26 FY26 form", 0.60, -0.5),
         ("incentives named for a new period or mechanism", 0.15, -5.0),
         ("letter Q4 sentence reads lower y/y", 0.20, -5.0),
         ("explicit quantified FY27 lower", 0.05, -9.0))
e = sum(w * v for _, w, v in forms)
print("   R04-style split of the Yes mass -> E[stock|Yes] %.2f ; EV at p 0.38 = %.2f (log -6 and -2.5)"
      % (e, 0.38 * e))

# ================================================================== registers
print("=" * 78)
print("Batch register")
for slug in ("bonus-ai-hosting-cost-step", "bonus-sbc-step-up", "bonus-interest-income-falls",
             "bonus-take-rate-guided-down"):
    o = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8"))
    im = o["impact"]
    print("  %-4s rev %s p %.2f ci %s | anchor %.2f flag %s | stock %s EV %s material %s | EV check %.2f"
          % (o["question_id"], o["revision"], o["final"]["p"], o["final"]["ci"],
             o["estimates"]["anchor"], o["estimates"].get("not_independently_derived_flag"),
             im["stock_usd_per_share"], im["ev_stock_usd_per_share"], im["material"],
             o["final"]["p"] * im["stock_usd_per_share"]))
```
