**R10 — submitted probability: 0.09, interval 0.05–0.15.**
Defensible as written: nearly. Every FRED and regime number reproduces exactly; the two inputs that set the answer are both biased in the same direction.
First fix: the parametric leg uses *trailing* realised vol (4.12%) as the *forward* vol. On this series, windows starting in the calm quintile go on to realise **4.64%** over the next 105 observations — 1.32× the trailing reading. The vol input is low, and the log itself says the number is "a vol call".
Next fix: the Reuters-poll drift is mis-derived (the log prorates a 9-month leg as if it were 12 and drops the spot→3m leg); the poll path implies **−0.64%**, not −0.42%. Also H should be **100**, not 105.
Independent comparison: **0.11** (0.06–0.18). The immaterial verdict survives; the §9 EPS row does not (+$0.52, not +$0.37).

**R11 — submitted probability: 0.38, interval 0.25–0.52.**
Defensible as written: no. The model replays to four decimals, but its base rate is typed into the script and its centre double-counts the one adjustment that moves it most.
First fix: claim 10's "1 of 13 quarters ≥ +4%" is a hand-entered list (`r11_model.py:36`), not a series. No US quarterly RevPAR history exists in the repo, and `sources/` is **empty** — the anchor (CoStar/TE FY26 +4.4%) has no saved snapshot.
Next fix: the +0.8pp "easy 4Q25 comp" credit is applied to a blend that is half a CoStar FY26 forecast, which already embeds the 4Q25 base. Removing it takes the number to **0.22**, and §7 never tests that direction.
Independent comparison: **0.29** (0.17–0.44); B15's mirror rises to ~0.16, and the R11 log's own "P(≤1) = 0.07" must be replaced by B15's 0.10.

**R15 — submitted probability: 0.14, interval 0.07–0.25.**
Defensible as written: the headline is close to mine; the base rate under it is not the calculation the log says it is.
First fix: §5 derives 0.10 as "1 − (0.95)²" while citing a Laplace of **0.10 per discussion** and a size-language frequency of **1 of 8**. Those inputs give 0.23–0.36 over two prints, not 0.10.
Next fix: the genuinely strong argument for a low number is nowhere in the log — the World Cup's *own-quarter* letter (2Q26), the exact slot in which the one Paris size-language line appeared (2Q24), has already passed without it.
Independent comparison: **0.18** (0.10–0.30); still immaterial (EV under $0.20/share) and still "drop from the risks list".

**R16 — submitted probability: 0.27, interval 0.15–0.42.**
Defensible as written: the number is close to mine, but it is not the number its own model produces and it is not the same distribution B13 and F01 publish.
First fix: R16, B13 and F01 rev 2 claim to share one 4Q26 object and state **three** different versions of it (0.27 / 0.27 / 0.29 for P(≥134.0m); means 8.3 / 8.3 / 8.70) — and the models' own blend rows say **0.3035 / 0.2622**. The two tails are computed at different guide cushions.
Next fix: the V2 leg is built on **C02 revision 1**, superseded on disk 18 minutes before this forecast was written; and V1's total sd (1.85) is half the observed Q3→Q4 sequential-change sd (3.74, n=4).
Independent comparison: **0.30** (0.18–0.44), with E[4Q26 | Yes] = **11.1**, not 10.7. Material verdict holds and strengthens.

## Scope and verification

Audit date **2026-09-17**, read-only, revision 1 of all four logs. `py -3.13` (numpy 2.4.4, pandas 2.3.3, scipy 1.17.1) and the repo venv `python` (3.11.14, pandas 3.0.5) were both available. No saved model was executed in place — all four write CSVs into their own `datasets/` directories, so every figure below comes from an independent re-implementation in this audit's scratch space and from the reproduction script at the end. No network was used: the FRED, yfinance, Kalshi and Polymarket claims were checked against the timestamped snapshots in each `sources/` folder. No prohibited directory was opened. Nothing in the repository was modified except this file.

**All four models reproduce.** R10: `beta` 0.5731 against the model's 0.57216 (the model divides a ddof=1 covariance by a ddof=0 variance; the difference is 0.16% and changes nothing), s16 119.0239 vs 119.02255, threshold 114.2630 vs 114.26164, n 5,083 windows, P 0.1218, tail n 619 mean −0.0560 median −0.0527, and every cell of `r10_regime.csv` and `r10_by_year.csv`. R11: centre 3.517, sd 1.676, P(≥4) 0.3867, E[x|≥4] 5.18 — the published 0.3866 / 5.2 exactly. R15: the tree gives 0.1509 and every sensitivity row replays. R16/B13: a stdlib rewrite of the Monte Carlo gives V1 0.1227 / 0.4206 / mean 7.789 against the saved 0.1219 / 0.4211 / 7.788 at N = 400,000, and V2 0.4737 / 0.1555 against 0.4741 / 0.1558.

**FRED and Kalshi snapshots were used as stated, with two exceptions.** The R10 FRED pull (`fred_DTWEXBGS_20260917T075453Z.csv`, 5,400 rows, 5,188 non-null, last 2026-09-11 = 118.2126) supports claim 1 in every particular, including the six monthly closes and the three trailing log changes. The R16 Kalshi ladders support every quoted bid and ask. The exceptions are (i) R16 claim 10's "volume and open interest null", which is false — `volume_fp` runs 36–294 contracts and `open_interest_fp` up to 170 on the FY26 ladder, and up to 999/690 on the Q3 ladder; what is true is that every `updated_time` is **2026-08-04** with `volume_24h_fp` 0.00, i.e. the quotes pre-date the 6 Aug 2Q26 print (finding A12-14); and (ii) R10 claim 9's characterisation of the option chains, which describes the degraded 07:56 pull and never mentions the 03:50 pull sitting in the same folder with two-sided ATM quotes and five-figure open interest (A12-13).

**Sibling revisions have moved under this batch.** C02 went to revision 2 at commit `85887c5` (03:51:45), eighteen minutes before R16's forecast file was written (04:09:31); R16 and B13 use the revision-1 vector. R01 went to revision 2 at `3deb9b8` (09:13:59) and C05 at 04:32:19 — both after this batch ran, so those are re-basing obligations for the response agent rather than errors by the forecaster.

Below, `log`, `model` and `forecast` mean `research-log.md`, `datasets/<id>_model.py` and `forecasts/2026-09-17-forecast.json` under `docs/pitch-forecasts/questions/<slug>/`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A12-01 | R16, B13 | critical | R16 `log:79,82`; B13 `log:5` (`coherence`), `forecast.estimates.coherence`; `r16_views.csv`, `b13_views.csv` | The two logs assert "one 4Q26 object … X01 should use this one object", and they are not one object. R16 blends V1 0.1219 / V2 **0.40** / V3 0.50; B13 blends V1 0.4211 / V2 **0.1558** / V3 0.0245. A V2 of 0.40 corresponds to a guide cushion of about **N(0.78, 1.3)**; a V2 of 0.1558 is cushion **N(1.2, 1.3)**. The two tails of the "same" distribution are drawn from different parameters, and each published headline is then rounded down again (R16 0.281 → 0.27; B13 0.262 → 0.26). F01 revision 2 publishes a *third* version — 0.29 / 0.27, mean 8.70, sd 2.05. | Stdlib replay: at cushion 1.2 the mixture is **(0.3035, 0.2615)**; at 0.78 it is **(0.2821, 0.2759)**; `r16_views.csv` itself carries `blend (0.5, 0.3, 0.2) = 0.3032` and `b13_views.csv` carries 0.2622. F01's `estimates.conditioning.q4_object` reproduces the cushion-0.78 mixture almost exactly. | Fix one cushion, publish the mixture's two tails unchanged, and let R16, B13 and F01 all quote it. At cushion 1.2 the pair is **(0.30, 0.26)**; at 0.78 it is **(0.28, 0.28)**. Do not round one tail down and not the other. |
| A12-02 | R16, R10, R15, B13 | critical | R16 `log:126` / `forecast.impact.eps_fy27_usd`; R10 `log:133`; R15 `log:119`; B13 `forecast.impact` | Every §9 EPS row multiplies the FY27 revenue delta by **0.66 before** applying the brief's $0.0014 per $M of EBITDA. 0.66 is *pp of margin per point of revenue*, not a dollar flow-through — and the margin row in the same table already spends it. Used consistently, a held-cost revenue delta flows to EBITDA one-for-one. R16 publishes margin **+1.05pp** (which is full flow-through) and EPS **+$0.23** (which is 66% flow-through) in adjacent rows of one table. | FY27 line build `docs/margin-build/SYNTHESIS.md:295–308`: revenue $15,829M, EBITDA $5,483M, margin 34.639%. +$250M held: margin 35.66% = **+1.02pp**, EPS **+$0.350**. R10 at +$400M: margin +1.64pp, EPS **+$0.570**. | Publish EPS = ΔRevenue × 0.0014 when the margin row uses the held coefficient, or state a flex assumption and cut both rows together (flex 0.42: R16 margin +0.65pp, EPS +$0.22). R16 → **+$0.35**; R10 → **+$0.52** (see A12-05); B13 → **−$0.31**. Stock and EV lines are unaffected; the materiality verdicts stand. |
| A12-03 | R11, B15 | critical | `log:40` (claim 10); `model:36`; B15 `forecast.estimates.inputs.base_rate_le1_*` | The base rate for both questions is the list `hist=[12,3,1.5,2,1,1,2,3,0,-0.5,-1,0,3.8,5.2]` typed into `r11_model.py:36`. Claim 10 presents it as derived from claims 3–5, which contain no such series: they give October 2025, FY2025, Jan–Apr 2026, March, July and the FY forecast, and nothing else. The repo holds **no** US quarterly RevPAR history, and `sources/` is empty, so nothing in the ledger supports 2023Q2 +3, 2023Q3 +1.5, 2024Q1 +1, 2024Q4 +3, 2026Q2 +5.2. Both the R11 base rate (1 of 13) and B15's (6 of 13, 6 of 8) rest on it. | Searched every RevPAR-bearing CSV under `data/processed`; the only quarterly hotel series is `q3nowcast/G/G_quarterly_panel.csv`, whose `mar_revpar_full` / `hlt_revpar_full` are **operator, global, system-wide** (2024Q4 5.0/3.5, 2025Q3 0.5/−1.1, 2026Q2 3.4/3.9) — a different object from all-US STR. `R11/sources/` returns `[]`. | Either fetch an STR/CoStar quarterly table and cite it, or relabel claim 10 "reconstructed from monthly press reports and the analyst's recollection; not a measured series", drop it from the claims ledger's load-bearing rows, and give the base-rate estimate the weight that deserves. B15 must carry the same caveat. |
| A12-04 | R11 | major | `model:24–27,30`; `log:39` (claim 9) | The +0.8pp "easy 4Q25 comp" credit is added to a centre that is 50% a **CoStar/TE FY2026 forecast**. A published FY26 y/y forecast necessarily embeds the 4Q25 base; crediting the comp again on top of it double-counts. The AR(1) leg is the only half where a comp adjustment could be argued, and even there it extrapolates y/y rates, which already average over base effects. | Removing the +0.8 (adj_mu −0.9 instead of −0.1) moves the centre 3.517 → **2.717** and P(≥4.0) **0.3867 → 0.2221**; P(≤1.0) rises 0.067 → 0.153. §7's "Election-week and CR drags | none: 0.60" tests the adjustment only in the *upward* direction; the downward direction is untested. | Apply the comp credit to the AR leg only (+0.4 on the blend) or drop it, and add the row to §7. My own centre puts it back partway, at +3.0 (see the independent number). |
| A12-05 | R10 | major | `log:82` (decomposition estimate); `model:26–28,39–40` | The parametric leg uses the **trailing** 252-day realised vol (4.12%) as the **forward** 105-day vol. On DTWEXBGS 2006–2026, windows that start in the calm quintile go on to realise **4.64%** over the next 105 observations, a ratio of **1.32×**; in the ±1pp band around today's reading the forward vol is 4.83% (ratio 1.14). Vol mean-reverts upward from calm, and the log's own §7 calls the regime conditioning "the weakest link" without pricing this. | Built the trailing/forward pair on every window (n 4,831) and conditioned on the trailing quintile; see the reproduction script, block R10/4. At vol 4.60% the normal gives 0.085 (zero drift) / **0.109** (poll drift), against the published 0.062 / 0.084. | Use a forward vol of about **4.6%** in the parametric leg, which happens to validate the 4.8% judgement in the anchor leg and makes the two legs consistent for the right reason. Decomposition 0.07 → **0.11**. |
| A12-06 | R10 | major | `log:28` (convention 1), `:35` (claim 3), `:41` (claim 8), `:82`; `model:41–42` | The Reuters-poll drift is mis-derived twice. The log takes the poll's **3-month → 12-month** leg (1.16 → 1.18, +1.72%), calls it a 12-month move, converts it at the broad/EUR beta to −1.0%/12m and prorates 105/252 to −0.42%. That (i) treats a nine-month span as twelve and (ii) discards the spot → 3-month leg, which is where most of the move sits now that EUR/USD has fallen to 1.1538 post-FOMC. | Interpolating the poll path (spot 1.1538, 3m 1.16, 6m 1.17, 12m 1.18) to the 4.85-month resolution point gives EUR/USD 1.1662, **+1.07% log**; at the measured broad/EUR beta of **−0.620** (daily, 2024+, r −0.879, n 675; −0.574 on 12-month changes) that is **−0.64%**, not −0.42%. | Publish −0.0064 as the poll drift and keep zero drift as the hawkish-regime alternative, which §7 already prices at 0.07. The parametric leg then reads 0.099 at 4.12% vol and 0.125 at 4.6%. |
| A12-07 | R16, B13 | major | R16 `log:38` (claim 8), `model:23`; `q4-nights-bucket/forecasts` revision 2 | The V2 guide route — 30% of the blend — uses **C02 revision 1** `(0.21, 0.19, 0.39, 0.17, 0.04)`. C02 revision 2 was on disk before this forecast was written and is `(0.18, 0.17, 0.30, **0.31**, 0.04)`: fourteen points of probability move out of "high single digits" and into "mid single / moderate", the bucket where R16's conditional is 0.02 and B13's is 0.59. | `git log` on `q4-nights-bucket/forecasts/2026-09-17-forecast.json`: revision 2 committed in `85887c5` at 03:51:45; `risk-q4-nights-print-meets-street/forecasts/…json` mtime 04:09:31. Re-running V2 on the revision-2 vector: **0.4054 / 0.2293** against 0.4737 / 0.1555; the blend becomes **(0.2830, 0.2836)**. | Re-run both models on the C02 revision-2 vector. It moves R16 only −0.02 (0.303 → 0.283) but moves B13 **+0.02** (0.262 → 0.284) — the symmetry A12-01 asks for arrives almost for free. |
| A12-08 | R15 | major | `log:73` (base_rate_estimate) | The stated derivation does not compute. §5 cites "Laplace **0.10** per discussion" for points figures and "size-language statements … **1 of 8**", then writes "two prints … → 1 − (0.95)² ≈ 0.10". The 0.95 appears from nowhere; neither cited input produces it. Taking the log's own numbers, the size-language route alone is 1/8 = 0.125 per discussion (Laplace 0.20), which over two prints is **0.234** (Laplace: 0.360), before adding any points route. | Replayed all three arithmetics in the reproduction script, block R15. `r15_event_record.csv` confirms 8 discussions, 0 points figures, 1 qualifying size-language line (2Q24 Paris). | Either publish the record-implied rate (~0.23) and then argue it down explicitly, or relabel the 0.10 a judgement. The argument that justifies going down is A12-09 and is missing from the log. |
| A12-09 | R15 | major | `log:64–68` (hypotheses), `:73`, `:97` (pre-mortem) | The strongest case *for* the low number is absent. The single qualifying precedent (2Q24: "the impact of a single city for a limited duration is relatively small compared to the total nights booked in a region") appeared in the letter covering the **event's own quarter**. The World Cup's equivalent slot — the 2Q26 letter and call, 6 Aug 2026 — has already passed and produced only "bookings from any single event may be temporary", which convention 3 correctly excludes. The one lap precedent (3Q25 Paris) produced "a slightly unfavorable year-over-year comparison": a headwind framing, not an immateriality framing. So the highest-hazard print is spent and the observed lap rate is 0 of 1. | Regex over all 23 letters and all mirrored transcripts for the seven event words within 320 characters of {basis point, percentage point, points of, immaterial, not material, not meaningful, relatively small}: **exactly two hits, both the same 2Q24 Paris sentence**. Verified verbatim in `data/raw/letters/2Q24_d831385dex991.htm`, `2Q26_d70413dex991.htm`, `3Q25_d40503dex991.htm` and `data/raw/transcripts/web/2Q26.html`. | Promote this to §4 and §5 as the reason the record rate is cut. It is the argument that makes 0.14–0.18 defensible rather than arbitrary, and it is the sentence the memo should carry. |
| A12-10 | R11, B15 | major | R11 `log:85`; `forecast.estimates.implied_distribution.p_le_1pct_B15` = 0.07 vs B15 `forecast.final.p` = 0.10 | The two logs publish different values for the *same* quantity. R11 §6 states "P(≤ +1.0%) = 0.07 (the mirror question B15)"; B15 publishes 0.10 and constructs a left-skewed mixture to get there, which is a defensible improvement — but R11 was never updated, so the batch carries 0.07 and 0.10 for P(4Q26 US RevPAR ≤ +1%). | B15's mixture `0.90·N(3.7,1.6) + 0.10·N(0.8,1.8)` reproduces to P(≥4) **0.3868**, P(≤1) **0.0956**, mean 3.41 — internally consistent and consistent with R11's 0.38. R11's own normal N(3.517, 1.676) gives 0.0666. | Replace R11 §6's 0.07 with B15's 0.10 and state that the pair is the mixture, not the normal. Then E[x|≥4] should also come from the mixture (5.15, not 5.18) — immaterial, but the memo should quote one object. |
| A12-11 | R11 | major | `log:78,81`; `forecast.estimates.anchor`; `sources/` (empty) | The anchor — CoStar/TE FY2026 US RevPAR +4.4%, 10 Aug 2026 — is the single most load-bearing external number in the question, and **nothing was saved**. `R11/sources/` is empty. Seven WebFetches and five WebSearches are logged; no payload, no result list, no timestamped snapshot. B15 did save three HTML files, but two are navigation chrome and the third (`hoteldive_perf_20260917.html`, 286 KB) strips to **43 characters** of text: none of them contains "RevPAR", "4.4" or "2027". | Listed both `sources/` directories and tag-stripped every saved HTML. The number itself *is* corroborated inside the repo (`research/notes/overnight/05_macro-outlook-and-transmission.md` §4.5 carries the 7 Aug revision, FY26 +4.4%/ADR +3.1%/occ 63.1% and FY27 +2.1%/+1.6%/63.4%) — so the claim is true; it is the retrieval discipline that failed. | Re-cite claim 2 to the repo note as the primary source (it is dated and in-repo) and treat the trade-press URLs as secondary. Save whatever can still be fetched. Where nothing can be saved — October 2025 RevPAR −0.9% / $110.35, and "declines continue throughout December" (claim 4) — mark the row "search snippet, unsaved" rather than citing a str.com URL that returned 403. |
| A12-12 | R16 | major | `log:75`, `model:14,19`; `r16_summary.csv` `q4_sd_V1` 1.8544 | V1's spread is too tight for the object. The model puts 4Q26 at 8.1 + 0.5·(Q3 − 9.67) + N(0, 1.4), total sd **1.85**, for a quarter that has not started and prints in five months. The observed Q3→Q4 change in nights growth is **−4.93, −1.52, +3.87, +1.03** — mean −0.39, sd **3.74** (n = 4). The team's lap thesis justifies a centre below the naive extrapolation; it does not justify a residual half the historical scale. | `data/processed/abnb_driver_history_quarterly.csv`, `nights_m_yoy_pct`, 3Q22–4Q25. A pure outside view (Q3 ~ N(9.5, 1.70), Δ ~ N(−0.39, 3.74)) gives 4Q26 ~ N(9.11, 4.11) and **P(≥134.0m) = 0.42**. Widening V1's residual to 2.0 with the R01 revision-2 centre gives V1 **0.173 / 0.465** instead of 0.112 / 0.440. | Widen the residual to about 2.0 and say why (n = 4, and the lap is a mechanism estimate, not a fitted effect), or add the sequential-change outside view as a fourth view at low weight. Either route lifts R16 by 2–3 points and B13 by 2 points — in the same direction, which is what a single distribution requires. |
| A12-13 | R10 | major | `log:41` (claim 9); `sources/yfinance_fx_etf_options_20260917T0350Z.json` vs `…T075603Z.json` | Claim 9 states that no option-implied dollar vol was obtainable and characterises the chains as "one-lot markets with bid 0 or ask/bid > 3". It cites the **07:56** pull, in which every bid, ask and open-interest field returned 0 — a degraded fetch. The **03:50** pull, saved in the same folder and cited nowhere, has the UUP January-2027 ATM chain with real two-sided quotes and five-figure open interest: 28C bid 0.40 / ask 0.75, **OI 6,924**, volume 59; 30C OI 16,342, volume 177; 28P bid 0.30 / ask 1.15, OI 2,180. UUP tracks a DXY-like basket. | Read both JSONs. Black–Scholes on the 03:50 mids (S 28.40, K 28, T 0.3315y): call IV 5.2%, put IV 14.1%, straddle-mid ≈ 9.6% — a spread so wide that the *conclusion* (no usable quote) survives, but not on the evidence given. Realised: DXY 252d **5.24%** against broad **4.12%**, ratio 1.27. | Rewrite claim 9 to cite the 03:50 pull, report the ATM straddle band, and derive the broad implied vol from the measured DXY/broad ratio rather than from a training-knowledge EUR/USD figure: 4.12% × a 10–15% implied premium is 4.5–4.7%, which is the same place A12-05 arrives from the forward-vol evidence. Keep the "no tradable quote" verdict; it is right. |
| A12-14 | R16 | minor | `log:40` (claim 10) | "volume and open interest null" is a parser error, not a fact — the same one A01-04 raised for the Q3 ladder and that has not propagated. The fields are `volume_fp` and `open_interest_fp`, and they are populated. | `kalshi_KXABNBA_open_20260917T075503Z.json`: >570m volume 162.01 / OI 86.01, >575m 277.20 / 87.02, >595m 293.01 / 160.02, >600m 294.02 / 170.00. Every `updated_time` is **2026-08-04**, `volume_24h_fp` 0.00, and 4 Aug is **two days before the 2Q26 print**. | Say what is actually disqualifying: the ladder's last trade pre-dates the 6 Aug print that moved the 4Q26 bar from 132.4m to 133.9m, so the implied 120–123m 4Q26 is a stale-information artefact, not a disagreement. That is a stronger reason for zero weight than "no liquidity", and it is verifiable. |
| A12-15 | R10 | minor | `model:12`; `log:90`; `forecast.estimates.inputs.horizon_obs` 105 | The horizon is wrong by five observations. The model's comment asserts "106 business days 16 Sep → 11 Feb, 105 FRED observations net of holidays". Counting weekdays from 17 Sep 2026 to 11 Feb 2027 and removing the six federal holidays in the window (Columbus 12 Oct, Veterans 11 Nov, Thanksgiving 26 Nov, Christmas 25 Dec, New Year 1 Jan, MLK 18 Jan) gives **100**. | Day count in the reproduction script, block R10/2; cross-checked against the series, which carries blank rows on holidays (e.g. 2026-09-07). At H = 100 the empirical P is **0.1167** (vs 0.1218) and the parametric sd falls 2.4%. | Set H = 100. Net effect on the headline is about −0.004; the point is that the stated input is checkable and wrong. |
| A12-16 | R16 | minor | `log:84`; `forecast` (no field); §9 row 2 | E[4Q26 | Yes] = 10.7 and E[4Q26 | No] = 7.5 are **V1's** conditional means, reported as the headline's. Under the published mixture they are 11.14 and 7.76. §9 then computes the 4Q26 nights delta as 10.7 − 8.1 = +2.6, understating it. | Simulated the full mixture (2m draws): mean 8.793, sd 2.089, E[·|≥134.0m] **11.14**, E[·|≤131.0m] 6.16. B13's "mean ≈ 8.3" is likewise the V1 mean carried onto mixture weights. | Publish the mixture conditionals. §9 becomes 4Q26 nights **+3.0**, 4Q26 revenue **+$90M**, FY27 revenue +$285M at 60% persistence, stock $9–13, EV $2.7–3.9. Material either way. |
| A12-17 | R11 | minor | `log:39` (claim 9), `:76`; `forecast.estimates.inputs.ar1_two_step` | The AR(1) leg is described as a "two-step" in §5, in claim 9's prose and in the JSON field name. `r11_model.py:23` applies **one** step: `lr + phi*(q3 - lr)` = 2.0 + 0.6 × 3.5 = 4.10. φ is also asserted, not estimated — no AR(1) is fitted anywhere in the log, and the long-run anchor of 2.0 is TE's FY2027 forecast, which is itself depressed by the June-2027 World Cup comparison (−0.8%). | Read `model:22–23,30`; replayed to centre_ar 4.10 and the blend 3.517. | Correct the label, and justify φ = 0.6 and lr = 2.0 or call them hand-set. The sensitivity grid already spans φ 0.4–0.8 (0.31–0.47), which is the honest width of this leg on its own. |
| A12-18 | R11 | minor | `log:126–128`; `forecast.impact.margin_fy26_pp`, `margin_fy27_pp`, `eps_fy27_usd` | The margin and EPS rows are understated by 2–3×, in the opposite direction from A12-02. +$20M of FY26 revenue held gives (5,098+20)/(14,268+20) = 35.822% vs 35.729% = **+0.09pp**, not +0.03. +$30M of FY27 revenue gives **+0.12pp** and **+$0.042** of EPS, not +0.05 and +0.01. | Line build annual table, `docs/margin-build/SYNTHESIS.md:295–308`. R16's equivalent rows (+0.35pp FY26, +1.05pp FY27) are computed correctly from the same coefficients, which is how the discrepancy shows. | Publish +0.09 / +0.12 / +$0.04, or state a flex assumption. All three are immaterial; a judge reading two R-tables side by side should not find the same coefficient used two ways. |
| A12-19 | R10 | minor | `log:128–129`; `forecast.impact.adr_pts` 1.5 vs `rev_4q26_musd` 17 | Two rows of one table disagree by 3–4×. ADR +1.5pt in 4Q26 at the brief's "1pt of ADR ≈ $46M of quarterly revenue" (scaled to Q4's $3,178M ≈ $30M/pt) implies about **+$45M** of 4Q26 revenue; the revenue row says **+$17M**. The reconciliation is that ADR-FX is booking-date and revenue-FX is recognition-lagged — exactly the distinction B4 exists to make — but the log never says so. | Brief §Sensitivities; `B4_FX_EXHIBIT.md` §3.3 (4Q26 moves ±0.5pp under a ±5% shift) and §6 (the Φ kernel, ⅔ prior quarter + ⅓ two back). | Add one sentence: the ADR row is a booking-date effect on the quarter's bookings, the revenue row is the kernel-recognised effect on the quarter's revenue, and they are not additive. Keep both numbers. |
| A12-20 | R10 | minor | `log:130`; `forecast.impact.rev_fy27_musd` 400 | The FY27 revenue delta uses **$158M** per point of FY27 revenue *growth*. The exhibit R10 itself cites states the conversion: "1pp of FY27 growth = 1% of FY26 revenue; FY26 base $14,293M, so **$142.9M per pp**" — and its own scenario table prices "+2.5pp = **+$354M**". $158M is 1% of FY27 revenue, a different object. | `B4_FX_EXHIBIT.md:199` and the four-way FY27 table. At 2.58pp (2.3 × 5.6/5.0, on the line build's $14,268M FY26 base) the delta is **+$368M**, not +$400M. | Use $142.9M/pt for growth points (and then the matching 0.60pp/pt margin coefficient), or keep the brief's $158M/0.66 pair and say the row is in points of FY27 revenue. Either way the memo should not show two meanings of "1pt" — this is the same inheritance A11-20 flagged. |
| A12-21 | R10 | minor | `log:36` (claim 4) | "0 in 12 of 21 years" overstates how concentrated the episodes are. The true count is **10 of 21** with exactly zero; 2008 (0.38%) and 2011 (3.19%) are small but not zero. | `r10_by_year.csv`, recomputed: zero in 2006, 2012, 2013, 2014, 2015, 2018, 2019, 2021, 2023, 2026. The rest of the claim checks — 2007 40.8%, 2009 47.0%, 2010 35.4%, 2020 41.6%, 2025 26.4%, 2017 29.3%. | Say 10 of 21, and add the number that matters: the 5,083 windows are 105-day overlaps, so the **effective** sample is about 48. At P = 0.12 that is a standard error of 4.7pp — which is roughly the published interval, and should be stated as its source rather than left implicit. |
| A12-22 | R15 | minor | `log:40` (claim 10); `forecast.estimates.anchor_source` | The anchor quotes C05 at **0.27**. C05 is at revision 2 with `p_any_quantification` = **0.28**, and its own `anchor` is now `null` with the three-estimate requirement declared unmet. R15 builds its anchor from two sibling forecasts of this same run (C05 and R08) whose disclosure priors come from the same 23-print record as R15's base rate and tree, so the "three independent estimates" of brief rule 7 are effectively one. | `bundle-attribution-quantified/forecasts/2026-09-17-forecast.json` (revision 2, committed 04:32:19, after R15 was written at 04:15:59). | Update to 0.28, set `anchor: null` with `NO_EXTERNAL_ANCHOR`, and keep C05/R08 as labelled sibling comparisons. Do not report \|final − anchor\| against them. This is A11-08 recurring in a second batch. |
| A12-23 | R15 | minor | `log:35` (claim 5); `datasets/r15_event_record.csv` row 6 | "The call summary reads 'Major events … expected to provide incremental but not primary growth'" is not management's words. The phrase occurs only inside an escaped `<li>` bullet list — a site-generated summary — in the mirrored transcript. The log does label it a summary; the event-record CSV then carries it in the same cell as genuine quoted remarks, with no marker. | `grep -o` on `data/raw/transcripts/web/4Q25.html`: the phrase appears once, inside `<li>…</li>`. Management's actual 4Q25 World Cup language is Chesky's "the biggest event on Earth" and the Anmuth exchange, both of which the log quotes correctly. | Mark the cell "site summary, not a transcript quote" or drop it. It is one of eight rows in the base-rate denominator, so it matters slightly. |
| A12-24 | R15 | minor | `log:117,119,121`; `forecast.impact` | The impact table books +$20M of FY27 revenue and +0.01pp of FY27 margin for a *disclosure*. The team's model already carries only +0.5pt of World Cup effect in 2Q26 — i.e. it already believes the lap is small — so a confirming statement changes no line. The log half-concedes this ("the team's numeric path barely moves") and books the number anyway. The margin row is also arithmetically wrong: 0.66 × 0.13pt = 0.086pp, not 0.01. | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.6 ("the World Cup is a 2Q26 event and therefore a 2Q27/3Q27 comparison problem"); the bridge overlay cited in claim 8. | Set the revenue and margin rows to 0 and keep the stock line at +$1 as an explicitly narrative entry. EV falls to $0.14; the "drop from the risks list" verdict is unchanged and better supported. |
| A12-25 | R16 | minor | `log:36` (claim 6); `data/processed/reverse_dcf/E/E_street_sign_history.csv` | The at-print bar record is quoted as "16 prints 4Q21–2Q26" and "since 2023 (12 prints)". Sixteen of the nineteen quarters in that span exist; **3Q22, 1Q23 and 2Q24 are absent** from the panel (and from the L0 register), and the log does not say so. "Since 2023" is really "the last twelve prints, i.e. from 2Q23"; a calendar cut at 2023-01-01 gives 13 prints and 10 of 13. Separately, every one of the 19 L0 nights rows carries `vendor = vendor_not_recorded`, against brief rule 5. | Recomputed: all 16 `nights_vs_street_pct` values match the log's list; last 12 mean **+0.874%**, sd **1.414** (the log says 1.5), ≥0 in **10 of 12**; the 2023-01-01 cut gives 13 / +0.678 / 10 of 13. `L0_vintage_register.csv`, metric = nights: 19 rows, all `vendor_not_recorded`, all `pit_usable = True`. | State the three gaps, give the window rule as a print count rather than a year, correct sd to 1.4, and flag the vendor field. The conclusion (the bar is usually beaten) is unaffected — but the memo cannot call these "the LSEG-family consensus" as QUESTIONS.md's convention does. |

## R10 — what the log does well and should keep

The evidence work is the cleanest in the batch. Every number in claim 1 reproduces from the saved FRED file — 5,188 non-null observations, 11 Sep = 118.2126, all six monthly closes, and the three trailing log changes to the decimal shown. The whole of `r10_regime.csv`, `r10_by_year.csv` and `r10_tail.csv` replays. The beta construction and the 16 Sep estimate reproduce to four decimals, and the 16 Sep FOMC claim, which has no saved snapshot, is independently corroborated by the price data in the folder: DXY 99.65 → 100.31 on the day, +0.66%, consistent with the "Bloomberg Dollar Spot +0.5%, best day in three months" the claim reports.

The single best decision in the log is §7's last row and the sentence behind it: the unpublished 16 Sep value moves the threshold *and* the starting level together, so the level uncertainty cancels out of a ratio question. That is exactly right, it is the thing most forecasters get wrong on a "X% below a not-yet-published reference" question, and the monitoring calendar still fixes the true threshold on 21 Sep. Keep the whole convention block.

The impact section's conclusion should also survive. "The memo should keep FX as arithmetic, not as a risk line: the risk that matters is the sign of the FY27 FX line under spot-held (+0.5pp) vs the strong-dollar camp (−1.8pp), which is symmetric and already in the bridge" is the correct reading of B4 and the right thing to tell a judge. It survives every repair above.

The strongest case against the published 0.09 is the one the log half-makes and then drops: the number is a vol call, both vol inputs are conservative, and the historical record says calm dollar regimes are where the two largest episodes in the sample (2007, 2025) began.

## R11 — what the log does well and should keep

The intra-quarter tape is real and correctly read. The weekly slope — +7.3, +7.2, +6.2, +4.4, +1.7 through late August, with ADR decelerating +5.7 → +0.6 — is the single most informative thing available about 4Q26, and the log's handling of the 5 September +16.1% week ("calendar mirror image, not a demand signal") is exactly the discipline the question needs. `str_weekly_us_3q26_repo_copy.csv` is byte-identical to the repo original, which is the right way to freeze an input.

Claim 6's operator arithmetic is the best outside view in the log and deserves more weight than it gets: Marriott and Hilton both at FY26 3.0–3.5% with H1 near +4 implies an H2 near +2.5, and the repo panel confirms the global levels (MAR 1Q26 +4.2, 2Q26 +3.4). Claim 8's finding — that US hotel RevPAR predicts Airbnb nights at r 0.88 in levels but has been decoupled since 2024, and that hotel ADR does not track Airbnb's pricing residual — is the right reason the impact line is small, and it is why the immaterial verdict holds under my number as well as the log's.

The strongest case against the published 0.38 is arithmetic, not judgement: the anchor route says +3.1, the FY26 forecast that produced it already knows the easy 4Q25 comp, and the +0.8pp credit is then added on top. Remove it and the question is a 1-in-5, not a 2-in-5.

## R15 — what the log does well and should keep

The source work is the best in the batch and should be preserved verbatim. All four Paris quotes, the 3Q25 lap sentence, the 2Q26 letter and call passages and the 1Q26 Milan/World Cup paragraph verify word for word against `data/raw/letters/` and `data/raw/transcripts/web/`. More important, the *negative* result is genuinely exhaustive: a proximity search over all 23 letters and every mirrored transcript for seven event words against every quantification or immateriality phrase returns **exactly two hits, and both are the same 2Q24 Paris sentence**. Zero event contributions have ever been quantified in points or basis points. That is the evidence, it is verifiable in one command, and it should go in the memo in that form.

Convention 3 is a real resolution rule that a judge could apply, and the line it draws — "relatively small compared to the total nights booked" counts, "bookings from any single event may be temporary" does not, because one is about size and the other about duration — is the correct distinction and is stated before the modelling. Pricing the lenient reading at 0.24 rather than hiding it is the honest way to carry convention risk.

Claim 7's contrast is the insight worth keeping: management quantifies calendar, FX and exogenous drags (the Middle East "roughly 100bps") in points, and has never quantified an event or a product tailwind. The asymmetry — numbers for what hurts, superlatives for what helps — is a behavioural model the memo can use across C05, R08, R09 and R15 at once.

## R16 — what the log does well and should keep

The three-view structure is the right shape for a question whose whole difficulty is that the team's thesis and the Street's bar disagree by 1.8 points, and §5 says so plainly: "the three estimates disagree by 38 points and the disagreement is one thing: whether the ex-NA lap arithmetic or management's four-for-four Q4 delivery record is the better read of a quarter that has not started." That is the sentence a Citadel judge wants, and it should survive into the memo unchanged.

The data checks pass. Claim 4's nights history reproduces exactly from `abnb_driver_history_quarterly.csv` (3Q24 8.48 → 4Q24 12.35, 3Q25 8.80 → 4Q25 9.82, 3Q23 13.54 → 4Q23 12.02, 3Q22 25.09 → 4Q22 20.16); claim 6's sixteen at-print gaps match `E_street_sign_history.csv` value for value; claim 7's fourteen five-month revenue vintages match `r16_revenue_consensus_5m_vs_actual.csv` with median +2.58% and 11 of 14 above zero. The decision to discard the five-month revenue record as a direct rate for nights — because revenue is guided with a cushion and nights are guided in words — is correct and is argued, not assumed.

The conditional tables in §6 are the most useful thing the run will produce for 5 November: a bucket-by-bucket update rule written down before the event, with the monitoring row that applies it. Keep them, and re-derive them from whichever single mixture survives A12-01.

The strongest case against the published 0.27 is that it is *too low, not too high*, and the log contains the material for it without assembling it: the 4Q26 bar rose from 132.4m in May to 134.2m on 12 September because the Street marks up after beats; the at-print bar has been beaten in 10 of the last 12 prints by a mean 0.9%; and the five-month-ahead bar, which is what this question fixes, has been beaten 11 of 14 times on revenue by a median 2.6%. Setting V3 at exactly 0.50 is a conservative choice dressed as a neutral one.

## Independent audit numbers

These are audit judgements built from the same repository inputs, not blinded second forecasts. No tradable market exists for any of the four questions; I confirmed that against the saved Polymarket, Kalshi and option snapshots rather than refreshing them.

**R10: P(Yes) = 0.11.** Judgmental 80% interval **0.06–0.18**.
Keep the regime-conditioned empirical leg at 0.10 (quintile 1 gives 0.110, the ±1pp band 0.072, the momentum band 0.121) but state its effective sample size: 48 independent 105-day blocks, standard error ~4.7pp. Replace the parametric leg's trailing vol with the **forward** vol that calm starts actually realise — 4.64%, ratio 1.32 — and the poll drift with the correctly interpolated **−0.64%**: normal 0.125, Student-t(4) ~0.095, leg **0.11**. Keep the implied-vol construction at 4.8%, which the DXY/broad realised ratio (1.27) and a 10–15% implied premium both support: leg **0.115**.
Blend 0.35 / 0.35 / 0.30 = **0.108**. The gap to the published 0.09 is entirely the vol input; if the Fed's hawkish turn justifies zero drift the number is 0.085, and that is the honest lower edge.

**R11: P(Yes) = 0.29.** Judgmental 80% interval **0.17–0.44**; mirror P(≤ +1.0%) ≈ **0.16**.
Take the anchor route at +3.1 (CoStar/TE FY26 +4.4% net of Q1 +3.8, Q2 ~+5.2, Q3 ~+5.5 on the published weights) and the AR route at +4.1, blend 50/50 to +3.6, then apply only the adjustments that are not already inside a vendor FY forecast: election week **−0.7** and CR risk **−0.2**, and no comp credit — centre **+2.7**. Put it back to **+3.0** because the AR long-run (TE's FY27 +2.1%) is itself depressed by a June-2027 World Cup comparison that has nothing to do with 4Q26, and widen the spread to **1.8** because the quarter has not started and the one quantified error scale in the log is a forecast *revision*, not a forecast error.
N(3.0, 1.8) gives P(≥4.0) **0.289** and P(≤1.0) **0.133**; adding B15's 10% shock branch for the CR expiry takes the lower tail to ~0.16. The unconditional base rate would put this near 0.10 and the joint-bull case near 0.78: 0.29 is where the arithmetic lands once the double count is removed.

**R15: P(Yes) = 0.18.** Judgmental 80% interval **0.10–0.30**; lenient resolver 0.28, strict 0.13.
Start from the record the log actually coded: qualifying size language in **1 of 8** event discussions, which over two remaining prints is 0.234 (Laplace 0.360), plus a never-observed points route. Cut it for the two reasons the log should have given and did not — the event's own-quarter letter (2Q26), the exact slot that produced the 2Q24 Paris line, has already passed silently, and the one lap precedent (3Q25) was framed as a headwind rather than as nothing.
That gives per-print hazards of about **0.07** at 5 November (an analyst ask on the Q3 air pocket is likely if Q3 decelerates, which is the team's own base case) and **0.09** at February (the incentive to defuse the 2Q27 comp before the May guide, in a letter that will carry an FY27 outlook), plus 0.02 and 0.03 for a ≤1pt figure: union **0.196**, taken to **0.18** for convention-3 strictness. It sits where it should among the siblings — above R08's 0.15 (never done, one door) and below R09's 0.25 and C05's 0.28.

**R16: P(Yes) = 0.30.** Judgmental 80% interval **0.18–0.44**; E[4Q26 | Yes] = **11.1** (135.4m), mixture mean **8.6**, sd **2.3**.
Rebuild the mixture once and use it for R16, B13 and F01: V1 on the R01 revision-2 centre (Q3 ~ N(9.5, 1.70)) with the residual widened from 1.4 to 2.0 — because the observed Q3→Q4 sequential-change sd is 3.74 on n = 4 and a mechanism estimate is not a fitted effect — giving **0.173**; V2 on the **C02 revision-2** vector at cushion N(1.0, 1.3), giving **0.38**; V3 at the Street's 0.50, which is if anything generous to the short given that the five-month-ahead bar has been beaten 11 of 14 times.
Blend 0.5 / 0.3 / 0.2 = **0.302**, and the same mixture gives P(≤131.0m) = **0.315**, i.e. B13 should move from 0.26 to about **0.31** and the middle band is 0.38. The pair is near-symmetric because a quarter that has not started, five months out, is genuinely two-tailed — which is the honest thing for the memo to say about its own Q4 leg.

**Ruling on the three cross-question coherences the batch was asked to settle.**
*R16 vs B13 vs F01.* F01 revision 2's object (P(≥134.0m) 0.29, P(≤131.0m) 0.27, mean 8.70, sd 2.05) is the only one of the three that is internally consistent — it is the exact mixture implied by R16's own stated legs at cushion N(0.78, 1.3). R16's 0.27 and B13's 0.26 are both hand-cuts below their own models, taken from *different* cushions, and B13's asserted mean of 8.3 is wrong (the mixture mean is 8.67–8.79). The run should adopt one mixture — my repaired one at (0.30, 0.31), or F01's at (0.29, 0.27) if the C02 and R01 revisions are left alone — and publish it in all three logs. **F01's "implied ~0.12" is stale**: it describes F01 revision 1 and equals R16's V1 alone; F01 revision 2 has already adopted the blend, so R16 §5's sentence about it must be deleted, not defended.
*R11 vs B15.* B15's mixture is correct and reproduces R11's 0.387 to three decimals; the incoherence is one-directional and easy — R11 §6's "P(≤1) = 0.07" is the normal, B15's 0.10 is the mixture, and R11 must adopt B15's. Both move under A12-04.
*R10 vs the brief's FX schedule.* The ±2.3 points of FY27 growth per one-sigma move is quoted correctly (B4 §3.3: weak USD +2.8pp, spot held +0.5pp, strong USD −1.8pp, so ±2.3 against spot-held), and the 1.12× scaling to E[move|Yes] = 5.6% is legitimate. Two caveats the log should carry: B4's scenario is an immediate parallel shift, while R10's event is a drift that completes only on 11 February, so the FY27 pass-through is a ceiling; and the dollar conversion should be **$142.9M per growth point** (B4 §5.2), giving **+$368M**, not $400M.
*R15 vs C05.* C05 revision 2 is at 0.28, not the 0.27 R15 quotes, and its anchor is now null. R15's 0.18 is consistent with it: a product that has been quantified twice gets 0.28 at one print; an event that has never been quantified, with a second door and two prints, gets 0.18.

## Reproduction script

Read-only, stdlib plus pandas, no numpy, no scipy, no network, no file writes. Run from the repository root with `python -B docs/pitch-forecasts/audits/A12-reproduce.py`. The saved models use numpy and scipy; this script re-implements the R16/B13 Monte Carlo with `random` and reproduces the published figures to within Monte Carlo error (V1 0.1227 against 0.1219 at N = 400,000), and reproduces the R10, R11 and R15 arithmetic exactly.

```python
"""A12 read-only reproduction (R10, R11, R15, R16 + the B13/B15/F01 coherence checks).
Run from the repository root: python -B docs/pitch-forecasts/audits/A12-reproduce.py
Requires stdlib + pandas only (no numpy, no scipy). Writes nothing; uses no network.
"""
from pathlib import Path
import csv, datetime as dt, json, math, random, statistics as st
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
R10 = Q / "risk-dollar-weakens"
R11 = Q / "risk-q4-us-revpar-strong"
R15 = Q / "risk-world-cup-quantified-small"
R16 = Q / "risk-q4-nights-print-meets-street"
B13 = Q / "bonus-q4-nights-print-weak"
B15 = Q / "bonus-q4-us-revpar-soft"


def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def npdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def psd(xs):
    return st.pstdev(xs) if len(xs) > 1 else 0.0


# ======================================================================= R10
print("=" * 78)
print("R10 / 1. FRED snapshot, spot, threshold")
f = sorted((R10 / "sources").glob("fred_DTWEXBGS_2026*.csv"))[-1]
rows = list(csv.DictReader(f.open(encoding="utf-8")))
dates = [r["observation_date"] for r in rows if r["DTWEXBGS"].strip()]
vals = [float(r["DTWEXBGS"]) for r in rows if r["DTWEXBGS"].strip()]
print("  file rows %d | non-null %d (log claim 1: 5,188) | last %s = %.4f"
      % (len(rows), len(vals), dates[-1], vals[-1]))
lv = [math.log(v) for v in vals]
dl = [lv[i + 1] - lv[i] for i in range(len(lv) - 1)]
for k, lbl in ((252, "12m"), (126, "6m"), (63, "3m")):
    print("  trailing %s log change %+.4f" % (lbl, lv[-1] - lv[-1 - k]))
dxf = sorted((R10 / "sources").glob("yfinance_dxy_daily_2026*T0756*.csv"))[-1]
dx = {r[0]: float(r[1]) for r in list(csv.reader(dxf.open(encoding="utf-8")))[1:]}
bmap = dict(zip(dates, vals))
pairs = [(math.log(bmap[d] / bmap[p]), math.log(dx[d] / dx[p]))
         for p, d in zip(dates, dates[1:]) if d >= "2024-01-01" and d in dx and p in dx]
mb = st.mean([a for a, _ in pairs])
mx = st.mean([b for _, b in pairs])
cov = sum((a - mb) * (b - mx) for a, b in pairs) / (len(pairs) - 1)
varx = sum((b - mx) ** 2 for _, b in pairs) / (len(pairs) - 1)
beta = cov / varx
s16 = vals[-1] * math.exp(beta * math.log(dx["2026-09-16"] / dx["2026-09-11"]))
print("  beta(broad on DXY, 2024+) %.4f n=%d | s16 est %.4f | threshold %.4f"
      % (beta, len(pairs), s16, 0.96 * s16))
print("  model values: 0.57216 / 119.02255 / 114.26164")

print("R10 / 2. horizon: FRED observations 16 Sep 2026 to 11 Feb 2027")
hol = {dt.date(2026, 10, 12), dt.date(2026, 11, 11), dt.date(2026, 11, 26),
       dt.date(2026, 12, 25), dt.date(2027, 1, 1), dt.date(2027, 1, 18)}
d, nobs = dt.date(2026, 9, 16), 0
while d < dt.date(2027, 2, 11):
    d += dt.timedelta(1)
    if d.weekday() < 5 and d not in hol:
        nobs += 1
print("  business days net of federal holidays = %d   (the model hard-codes H = 105)" % nobs)

print("R10 / 3. empirical windows and the effective sample size")
THR = math.log(0.96)
for H in (100, 105):
    r = [lv[i + H] - lv[i] for i in range(len(lv) - H)]
    k = sum(1 for x in r if x <= THR)
    blk = r[::H]
    kb = sum(1 for x in blk if x <= THR)
    pb = kb / len(blk)
    print("  H=%3d n=%4d P=%.4f mean=%+.4f sd=%.4f | non-overlapping n=%d P=%.4f se=%.4f"
          % (H, len(r), k / len(r), st.mean(r), psd(r), len(blk), pb,
             math.sqrt(pb * (1 - pb) / len(blk))))
H = 105
r105 = [lv[i + H] - lv[i] for i in range(len(lv) - H)]
tail = [x for x in r105 if x <= THR]
print("  tail: n=%d mean=%.4f median=%.4f   (log claim 7: 619 / -0.056 / -0.0527)"
      % (len(tail), st.mean(tail), st.median(tail)))
byyr = {}
for i, x in enumerate(r105):
    byyr.setdefault(dates[i][:4], []).append(x)
zero = sorted(y for y, xs in byyr.items() if not any(x <= THR for x in xs))
print("  years with ZERO sub-threshold windows: %d of %d -> %s" % (len(zero), len(byyr), zero))
print("  log claim 4 says 12 of 21")

print("R10 / 4. vol regime: trailing 252d vol vs the FORWARD 105d vol")
trail = [psd(dl[i - 252:i]) * math.sqrt(252) if i >= 252 else None for i in range(len(dl))]
fwd = [psd(dl[i:i + H]) * math.sqrt(252) if i + H <= len(dl) else None for i in range(len(dl))]
pr2 = [(t, g, r105[i]) for i, (t, g) in enumerate(zip(trail, fwd))
       if t is not None and g is not None and i < len(r105)]
cur = psd(dl[-252:]) * math.sqrt(252)
print("  current trailing vols: 63d %.4f 126d %.4f 252d %.4f full %.4f"
      % (psd(dl[-63:]) * math.sqrt(252), psd(dl[-126:]) * math.sqrt(252), cur,
         psd(dl) * math.sqrt(252)))
for lo, hi, lbl in ((0.0, 0.042, "quintile 1 (<=4.20%)"),
                    (cur - .01, cur + .01, "band +/-1pp"),
                    (0.0, 9.0, "all windows")):
    sel = [(t, g, x) for t, g, x in pr2 if lo <= t < hi]
    print("  %-22s n=%5d  P(<=-4.08%%) %.4f  mean FORWARD vol %.4f  ratio %.2f"
          % (lbl, len(sel), sum(1 for _, _, x in sel if x <= THR) / len(sel),
             st.mean([g for _, g, _ in sel]), st.mean([g / t for t, g, _ in sel])))
print("  => a calm start does not stay calm; the forward-vol input should be ~4.6%, not 4.12%")

print("R10 / 5. drift: what the Reuters poll actually implies")
spot = 1.153762
path = ((0, spot), (3, 1.16), (6, 1.17), (12, 1.18))
tm = 4.85
eur = spot
for (m0, v0), (m1, v1) in zip(path, path[1:]):
    if m0 <= tm <= m1:
        eur = v0 + (v1 - v0) * (tm - m0) / (m1 - m0)
print("  EUR/USD 16 Sep %.4f -> poll-interpolated at %.2f months %.4f = %+.4f log"
      % (spot, tm, eur, math.log(eur / spot)))
print("  broad at beta -0.6 = %+.4f ; the log uses -0.0042" % (-0.6 * math.log(eur / spot)))


def pn(vol, drift, hh=105):
    return Phi((THR - drift) / (vol * math.sqrt(hh / 252)))


for vol in (0.0412, 0.046, 0.048):
    print("  vol %.4f: drift 0 -> %.4f | -0.0042 -> %.4f | -0.0066 -> %.4f"
          % (vol, pn(vol, 0.0), pn(vol, -0.0042), pn(vol, -0.0066)))
print("  published blend 0.35*0.10 + 0.35*0.07 + 0.30*0.10 = %.4f"
      % (0.35 * 0.10 + 0.35 * 0.07 + 0.30 * 0.10))
print("  repaired blend 0.35*0.10 + 0.35*0.11 + 0.30*0.115 = %.4f"
      % (0.35 * 0.10 + 0.35 * 0.11 + 0.30 * 0.115))

print("R10 / 6. impact arithmetic (B4 exhibit section 5.2 + brief)")
FY26R, FY27R, FY27E = 14268.0, 15829.0, 5483.0
base_m = 100 * FY27E / FY27R
print("  FY27 line build: revenue %.0f EBITDA %.0f margin %.3f%%" % (FY27R, FY27E, base_m))
dpp = 2.3 * 5.6 / 5.0
for basis, lbl in ((FY26R / 100.0, "142.9 per pt = 1% of FY26 revenue (B4 5.2)"),
                   (158.0, "158.0 per pt = 1% of FY27 revenue (the brief)")):
    dR = dpp * basis
    print("  %-44s dRev %+6.0fM  margin %+.2fpp  EPS %+.3f"
          % (lbl, dR, 100 * (FY27E + dR) / (FY27R + dR) - base_m, dR * 0.0014))
print("  the log publishes dRev +400M, margin +1.6pp, EPS +0.37 = 400 x 0.66 x 0.0014,")
print("  i.e. 0.66 is used twice: once as pp-per-pt for the margin row and again as a dollar rate")

# ======================================================================= R11
print("=" * 78)
print("R11 / 1. FY-implied Q4 grid, AR(1) leg, blend")
w = (0.23, 0.26, 0.27, 0.24)
q1 = 3.8
grid = [(fy - w[0] * q1 - w[1] * q2 - w[2] * q3) / w[3]
        for q2 in (4.5, 5.2, 6.0) for q3 in (4.5, 5.2, 6.0) for fy in (4.0, 4.4, 4.8)]
c_str = st.mean(grid)
c_ar = 2.0 + 0.6 * (5.5 - 2.0)
adj = 0.8 - 0.7 - 0.2
centre = 0.5 * c_str + 0.5 * c_ar + adj
sdv = math.sqrt(1.6 ** 2 + 0.5 ** 2)
z = (4.0 - centre) / sdv
print("  FY-implied mean %.3f (n=%d) | AR(1) one step %.2f | adj %+.1f | centre %.3f sd %.3f"
      % (c_str, len(grid), c_ar, adj, centre, sdv))
print("  P(>=4.0) %.4f  P(<=1.0) %.4f  E[x|>=4] %.2f   (log: 0.3866 / 0.07 / 5.2)"
      % (1 - Phi(z), Phi((1.0 - centre) / sdv), centre + sdv * npdf(z) / (1 - Phi(z))))
print("  section 5 and the JSON call the AR leg a 'two-step'; r11_model.py applies one step")
c2 = centre - 0.8
print("  DROP the +0.8 easy-comp credit (the CoStar FY26 forecast already embeds the 4Q25 base):")
print("    centre %.3f -> P(>=4.0) %.4f  P(<=1.0) %.4f   [not in section 7]"
      % (c2, 1 - Phi((4.0 - c2) / sdv), Phi((1.0 - c2) / sdv)))

print("R11 / 2. the claim-10 base rate is a hand-entered list, not a repo series")
hist = [12, 3, 1.5, 2, 1, 1, 2, 3, 0, -0.5, -1, 0, 3.8, 5.2]
print("  r11_model.py line 36 hist =", hist)
print("  >=4%%: %d of %d | <=1%%: %d of %d (B15 claims 6 of 13)"
      % (sum(1 for x in hist[1:] if x >= 4), len(hist) - 1,
         sum(1 for x in hist[1:] if x <= 1), len(hist) - 1))
try:
    g = pd.read_csv(ROOT / "data/processed/q3nowcast/G/G_quarterly_panel.csv").rename(
        columns={"Unnamed: 0": "q"})
    print("  the only hotel RevPAR series in the repo are OPERATOR, GLOBAL, system-wide:")
    print(g[g.q >= "2023Q1"][["q", "mar_revpar_full", "hlt_revpar_full"]].to_string(index=False))
except Exception as exc:
    print("  panel unavailable:", exc)

print("R11 / 3. sources")
print("  R11 sources/ contents:", sorted(p.name for p in (R11 / "sources").glob("*")))
print("  B15 sources/ raw html bytes:",
      {p.name: p.stat().st_size for p in (B15 / "sources").glob("*.html")})

print("R11 / 4. mirror-question coherence with B15")
tw, tc, ts, sw, sc, ss = 0.90, 3.7, 1.6, 0.10, 0.8, 1.8
mix4 = tw * (1 - Phi((4.0 - tc) / ts)) + sw * (1 - Phi((4.0 - sc) / ss))
mix1 = tw * Phi((1.0 - tc) / ts) + sw * Phi((1.0 - sc) / ss)
print("  B15 mixture 0.9*N(3.7,1.6)+0.1*N(0.8,1.8): P(>=4) %.4f P(<=1) %.4f mean %.2f"
      % (mix4, mix1, tw * tc + sw * sc))
print("  R11 section 6 states P(<=1) = 0.07; B15 publishes 0.10 for the same quantity")

# ======================================================================= R15
print("=" * 78)
print("R15 / event record, Laplace variants, tree replay")
rec = list(csv.DictReader((R15 / "datasets/r15_event_record.csv").open(encoding="utf-8")))
n_pts = sum(1 for x in rec if x["points_figure"] != "no points")
n_size = sum(1 for x in rec if x["size_language"].startswith("relatively small"))
print("  event discussions %d | with a points figure %d | with qualifying size language %d"
      % (len(rec), n_pts, n_size))
print("  Laplace(points)/discussion %.4f | Laplace(size language)/discussion %.4f"
      % ((n_pts + 1) / (len(rec) + 2), (n_size + 1) / (len(rec) + 2)))
for lbl, p1 in (("log's implicit per-print rate 0.05", 0.05),
                ("raw size-language frequency 1/8", n_size / len(rec)),
                ("Laplace size language 2/10", (n_size + 1) / (len(rec) + 2))):
    print("    %-38s over two prints -> %.4f" % (lbl, 1 - (1 - p1) ** 2))
tree = {"A_nov": 0.02, "A_feb": 0.04, "B_nov": 0.05, "B_feb": 0.05}
prod = 1.0
for v in tree.values():
    prod *= (1 - v)
print("  tree replay 1 - prod(1-p) = %.4f   (r15_tree.csv: 0.1509)" % (1 - prod))
print("  section 5 claims 1-(0.95)^2 = %.4f, which uses 0.05/print, not the 0.10 Laplace it cites"
      % (1 - 0.95 ** 2))
c05 = json.loads((Q / "bundle-attribution-quantified/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
print("  C05 revision %s p_any_quantification = %s ; R15 claim 10 and its anchor quote 0.27"
      % (c05["revision"], c05["p_any_quantification"]))

# ================================================================== R16 / B13
print("=" * 78)
print("R16 / B13 / stdlib replay of the three views and of the mixture")
BASE, THRH, THRL, Q3REF = 121.9, 134.0, 131.0, 9.67
print("  thresholds: %.1fm = %+.4f%%  |  %.1fm = %+.4f%%"
      % (THRH, 100 * (THRH / BASE - 1), THRL, 100 * (THRL / BASE - 1)))


def v1(q3_mu=9.67, q3_sd=1.70, q4_mu=8.1, beta=0.5, res_sd=1.4, tail_w=0.12,
       n=400000, seed=12):
    rng = random.Random(seed)
    hi = lo = 0
    tot = 0.0
    for _ in range(n):
        q3 = rng.gauss(q3_mu, q3_sd)
        if rng.random() < tail_w:
            q4 = 5.5 + beta * (q3 - Q3REF) + rng.gauss(0, 1.5)
        else:
            q4 = q4_mu + beta * (q3 - Q3REF) + rng.gauss(0, res_sd)
        tot += q4
        nights = round(BASE * (1 + q4 / 100), 1)
        hi += nights >= THRH
        lo += nights <= THRL
    return hi / n, lo / n, tot / n


def v2(vec, cm=1.2, cs=1.3, fall=(0.1219, 0.4211), n=200000, seed=13):
    rng = random.Random(seed)
    mids = (10.75, 9.75, 8.0, 6.0, None)
    ph = pl = 0.0
    for wgt, m in zip(vec, mids):
        if m is None:
            ph += wgt * fall[0]
            pl += wgt * fall[1]
            continue
        a = b = 0
        for _ in range(n):
            x = m + rng.gauss(cm, cs)
            nights = round(BASE * (1 + x / 100), 1)
            a += nights >= THRH
            b += nights <= THRL
        ph += wgt * a / n
        pl += wgt * b / n
    return ph, pl


V3 = (0.50, Phi((THRL - 134.0) / 1.5))
base = v1()
print("  V1 (Q3 9.67, res_sd 1.4): P>=134 %.4f  P<=131 %.4f  mean %.3f" % base)
print("     models give 0.1219 / 0.4211 / 7.788")
print("  V3 Street N(134.0,1.5): P>=134 %.4f  P<=131 %.4f   (models: 0.50 / 0.0245)" % V3)
C02v1 = (0.21, 0.19, 0.39, 0.17, 0.04)
C02v2 = (0.18, 0.17, 0.30, 0.31, 0.04)
for lbl, vec, cm in (("C02 rev 1, cushion N(1.2,1.3)   [the models]", C02v1, 1.2),
                     ("C02 rev 1, cushion N(0.78,1.3)  [R16 hand 0.40]", C02v1, 0.78),
                     ("C02 rev 2, cushion N(1.2,1.3)", C02v2, 1.2)):
    gg, ll = v2(vec, cm=cm)
    print("  %-46s V2 %.4f / %.4f -> blend %.4f / %.4f"
          % (lbl, gg, ll, 0.5 * base[0] + 0.3 * gg + 0.2 * V3[0],
             0.5 * base[1] + 0.3 * ll + 0.2 * V3[1]))
print("  published: R16 0.27, B13 0.26; F01 rev 2 carries 0.29 / 0.27, mean 8.70, sd 2.05")
print("  B13 section 5 states V2 0.18 and anchor 0.05: 0.5*0.4211+0.3*0.18+0.2*0.05 = %.4f"
      % (0.5 * 0.4211 + 0.3 * 0.18 + 0.2 * 0.05))
print("  b13_views.csv 0.2622 needs V2 = 0.1558 and V3 = 0.0245: %.4f"
      % (0.5 * 0.4211 + 0.3 * 0.1558 + 0.2 * 0.0245))
v2mean = 0.21 * 11.95 + 0.19 * 10.95 + 0.39 * 9.2 + 0.17 * 7.2 + 0.04 * 7.788
print("  mixture mean = 0.5*7.788 + 0.3*%.3f + 0.2*9.926 = %.3f   (B13 asserts about 8.3)"
      % (v2mean, 0.5 * 7.788 + 0.3 * v2mean + 0.2 * 9.926))

print("R16 / V1 residual sd vs the historical Q3->Q4 sequential change")
seq = [20.163 - 25.094, 12.018 - 13.541, 12.348 - 8.481, 9.820 - 8.795]
print("  observed Q3->Q4 changes %s  mean %+.2f sd %.2f (n=4); V1 total sd is 1.85"
      % ([round(x, 2) for x in seq], st.mean(seq), st.stdev(seq)))
for rs in (1.4, 2.0, 2.6):
    a, b, _ = v1(q3_mu=9.5, res_sd=rs, seed=14)
    print("    Q3 centre 9.5 (R01 rev 2), res_sd %.1f -> P>=134 %.4f  P<=131 %.4f" % (rs, a, b))

print("R16 / impact arithmetic")
dR = 250.0
print("  +250M of FY27 revenue, costs held -> margin %+.2fpp, EPS %+.3f"
      % (100 * (FY27E + dR) / (FY27R + dR) - base_m, dR * 0.0014))
print("  the log publishes +1.05pp and +0.23, where 0.23 = 250 x 0.66 x 0.0014")

# ================================================================ registers
print("=" * 78)
print("Cross-question register")
for slug in ("risk-dollar-weakens", "risk-q4-us-revpar-strong",
             "risk-world-cup-quantified-small", "risk-q4-nights-print-meets-street",
             "bonus-q4-nights-print-weak", "bonus-q4-us-revpar-soft",
             "q1-27-nights-guide-above-82", "risk-q3-nights-meets-guide",
             "q4-nights-bucket", "bundle-attribution-quantified"):
    o = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8"))
    fin = o["final"]
    head = fin.get("p", fin.get("vector"))
    line = "  %-9s rev %s  final %s" % (o["question_id"], o["revision"], head)
    imp = o.get("impact")
    if imp:
        line += " | stock %s EV %s material %s | EV check %.3f" % (
            imp["stock_usd_per_share"], imp["ev_stock_usd_per_share"], imp["material"],
            round(fin["p"] * imp["stock_usd_per_share"], 3))
    print(line)

print("Kalshi snapshot fields the R16 log reports as null")
kj = json.loads((R16 / "sources/kalshi_KXABNBA_open_20260917T075503Z.json")
                .read_text(encoding="utf-8"))
for m in sorted(kj["markets"], key=lambda x: x["floor_strike"]):
    print("  >%3dm bid %s ask %s last %s volume_fp %s open_interest_fp %s updated %s"
          % (m["floor_strike"] / 1e6, m["yes_bid_dollars"], m["yes_ask_dollars"],
             m["last_price_dollars"], m["volume_fp"], m["open_interest_fp"],
             m["updated_time"][:10]))
```
