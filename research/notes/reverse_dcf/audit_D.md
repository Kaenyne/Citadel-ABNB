# Audit of workstream D: sell-side dispersion

Auditor note for the 12-13 Sep 2026 market-implied run. Audited: `research/notes/reverse_dcf/D_sell-side-dispersion.md`, `analysis/src/reverse_dcf/D_00_refresh_tape.py`, `D_01_targets_implied.py`, `D_02_revisions_positioning.py`, all 17 CSVs under `data/processed/reverse_dcf/D/`. Findings CSV: `data/processed/reverse_dcf/audit/audit_D_findings.csv`. Audit date 12 Sep 2026.

## Verdict: PASS WITH FIXES

No blocker. The tape arithmetic, the implied-multiple table, the estimate-dispersion mapping and the 2Q26 revision path all reproduce and are correct. Five material findings, all in the interpretation layer: the headline "targets chase up, not down" is not supported once the full print history and a sign-split regression are used; the block regression is quoted at the one block offset that gives the highest R2 and lowest contemporaneous t; the yfinance feed misses far more than the two Goldman actions the note reports; Bernstein's 25.5x is a P/E and shows that bull carrying earnings well above management's FY27 case; and the decomposition assumptions are mislabelled ANCHOR. Eight minor items.

## 1. Reproduction (task 1)

| Step | Result |
|---|---|
| `D_00_refresh_tape.py` (py -3.13, yfinance) | Ran, exit 0. Feed 469 rows, 3 new vs 6 Sep, 0 removed; all five outputs byte-identical to the saved files |
| `D_01_targets_implied.py` | Ran, exit 0; all six outputs byte-identical |
| `D_02_revisions_positioning.py` | Ran, exit 0; all five outputs byte-identical |
| Files not produced by any script | `D_headline.csv`, `D_thesis_quotes.csv` (hand-built; headline is a subset of `D_tape_percentiles.csv`, values match) |

The saved outputs were backed up before the re-run and every file compared with `cmp`; 17 of 17 identical. MEASURED.

## 2. Target-implied arithmetic (task 2)

Hand recompute with EV = target x 597.0 less 9,593, EBITDA $5,801m, margin 36.2%, FY26 base $14,231m, and the nights formula in the task (revenue growth less 3.0 for ADR plus 0.6 for the FX headwind removed, take rate 0):

| Target | EV $m | EV/EBITDA spot | FY27-end basis | EBITDA at 16.5x | Revenue | Growth % | Nights additive | Nights log-additive (script) | Note's value |
|---|---|---|---|---|---|---|---|---|---|
| 125 | 65,032 | 11.21 | 10.47 | 3,941 | 10,888 | -23.5 | -25.9 | -25.3 | -25.3 |
| 165 | 88,912 | 15.33 | 14.40 | 5,389 | 14,886 | 4.6 | 2.2 | 2.2 | 2.2 |
| 170.19 | 92,010 | 15.86 | 14.91 | 5,576 | 15,404 | 8.2 | 5.9 | 5.7 | 5.7 |
| 181.81 | 98,949 | 17.06 | 16.06 | 5,997 | 16,566 | 16.4 | 14.0 | 13.7 | 13.7 |
| 220 | 121,747 | 20.99 | 19.81 | 7,379 | 20,383 | 43.2 | 40.8 | 39.9 | 39.9 |

Every column in `D_headline.csv`, `D_tape_percentiles.csv` and `D_target_implied.csv` matches to rounding (the script uses $5,800.957m and $14,231.303m, which moves nothing at one decimal). The EPS map (-2.301 + 1.445 per $bn) reproduces; its delivered check is 6.084, not 6.078, because a line through three points is not exact; immaterial. EV at $170.19 is $92,010m, matching the brief's $92.0bn.

FX sign convention: the script computes nights = (1 + g) / (1.03 x 0.994) - 1. Dividing by 0.994 adds about 0.6pp to nights, so the FX term is a -0.6pp contribution to revenue growth that is removed to recover nights. That is the convention in the task ("+0.6, FX headwind removed") and it is applied the same way in the headline, per-target, percentile and estimate-dispersion files. The note writes it as "FX -0.6pp", the revenue-contribution sign; consistent. Additive and log-additive differ by 0.0-0.9pp, most at the $125 and $220 extremes; the script's log-additive form is the better one and is what section 2 of the note describes. No discrepancy.

One labelling error (finding 5): the caption on the headline table calls ADR +3.0%, FX -0.6pp and take rate flat "ANCHOR inputs". The brief has no FY27 ADR, FX or take-rate assumption; these were set in the task and are JUDGEMENT. For the record, management's delivered case has FY27 ADR +3.1% in USD, take rate -0.7% and no FX line; the note's decomposition applied to delivered revenue growth (+12.6%) gives nights +10.0%, equal to management's 646.98m / 588.164m, so the mapping agrees with management at the delivered point.

## 3. Spot basis vs FY27-end basis (task 3)

The script uses 570.7m shares and $10,608.664m net cash (the delivered-case 4Q27 row in `mgmt_implied_summary.csv`), which rounds to the brief's $10,609m. The FY27-end column runs 0.75-1.2 turns below spot across the tape (10.5 vs 11.2 at $125; 16.1 vs 17.1 at the mean; 19.8 vs 21.0 at $220) and the same pairs appear in section 1, the headline table, section 3, section 4 (Morgan Stanley 11.2 / 10.5, Truist 14.9 / 14.0, Rosenblatt 21.0 / 19.8) and caveat 1. Consistent throughout. The "ambition case at 19.6x" for $220 is (220 x 597 - 9,593) / 6,212.5 = 19.6, correct. MEASURED.

## 4. Revision analysis (task 4)

2Q26 path from `D_target_panel_daily.csv`: 6 Aug $159.82 (n 28), 7 Aug $172.68 (n 31), 10 Aug $173.90, 4 Sep $179.55 (n 31), 11 Sep $181.81 (n 32). Reproduced. Chase ratio 12.34 / 17.43 = 0.708. Window actions: 24 changes, 24 raises, 0 cuts, median +12.9%, mean +14.4%, range +2.8% to +31.6%, 17 same-day. All reproduced.

Block regression: offset 0 reproduces exactly (n 66, betas 0.053 / 0.170 / 0.114, t 1.49 / 4.82 / 3.28, R2 0.341). The blocks are non-overlapping in the dependent variable (every 21st session of the daily series after the dropna); the regressors are the same 21-session price changes shifted, so each price change appears once per lag position, a normal distributed-lag design. Residual autocorrelation is not a problem (Durbin-Watson 1.6-2.3, lag-1 residual autocorrelation -0.10), so plain OLS standard errors are defensible; HC1 t-statistics for lag 1 are 2.2-5.5 across offsets, still significant.

The problem is the block offset (finding 2). Running all 21 possible offsets:

| Statistic | Offset 0 (note) | Range over 21 offsets | Mean over offsets |
|---|---|---|---|
| n | 66 | 65-66 | |
| R2 | 0.341 | 0.193-0.341 | 0.25 |
| contemporaneous beta (t) | 0.053 (1.49) | 0.035-0.111 (0.91-3.08) | 0.075 |
| lag-1 beta (t) | 0.170 (4.82) | 0.090-0.194 (2.46-4.92) | 0.13 |
| lag-2 beta (t) | 0.114 (3.28) | 0.061-0.122 (1.64-3.76) | 0.095 |

Offset 0 is the maximum R2 and one of the three lowest contemporaneous betas; the contemporaneous term is significant at 5% in 10 of 21 offsets. The shape (lagged response larger than same-month) holds at every offset, so "targets follow the price with a one-to-two-month lag" survives; "the contemporaneous response is small (t 1.5)" does not. The overlapping daily Newey-West numbers in the note (0.07 / 0.13 / 0.10) sit close to the offset average and are the better single citation.

"Targets chase up, not down" (finding 1) is not supported:

- Sign-split regression (positive and negative price changes as separate regressors). Blocks, offset 0: negative-change betas 0.11 / 0.16 / 0.20 (t 1.9 / 2.6 / 3.2) against positive-change betas -0.03 / 0.16 / 0.01 (t -0.4 / 2.4 / 0.1). Daily Newey-West, n 1,366: negative 0.10 / 0.12 / 0.12 (t 1.9 / 3.2 / 3.2) against positive 0.05 / 0.13 / 0.07 (t 0.7 / 3.2 / 1.8). Falls pull targets down at least as much as rises pull them up.
- All 23 prints, not eight. Six prints with a day-1 move of -5% or worse drew a mean-target change of -3.8% by +20 sessions (chase 0.26) and -3.9% by +40; six prints of +5% or better drew +6.3% (chase 0.42). The four large down prints the eight-print window excludes all produced cuts: 3Q22 (-13.4% print, targets -7.6% at +20, 11 cuts / 2 raises), 1Q23 (-10.9%, -6.4%, 14 cuts / 0 raises), 2Q24 (-13.4%, -14.1%, 19 cuts / 0 raises), and 2Q22 (-1.1% print after a 21% pre-print run, targets -10.1%, 14 cuts).
- Outside prints: the 126 days on which the stock had fallen more than 15% over 21 sessions were followed by a -5.0% change in the mean target over the next 42 sessions; the 121 days after a 15%+ rise were followed by +4.0%.
- The note's own 1Q25 row (20 cuts, median -8.8%, after the April 2025 drawdown) is a chase-down with the usual lag, not an exception to it.

The two down prints in the eight-print window: 3Q24 (-8.7% on 8 Nov 2024) followed an 11.0% rise over the prior 21 sessions and drew 9 raises / 1 cut, mean target +3.5%, so the tape was catching up to the pre-print level, as the note says. 2Q25 (-8.0% on 7 Aug 2025) drew 8 raises and 6 cuts (Morgan Stanley -7.7%, UBS -5.1%, Wedbush -3.7%, Jefferies -3.0%, Truist -1.9%, Wells -0.9%), mean target 0.0%; the note's "no cut in the mean target at all" is right on the mean and wrong on the cuts. Both prints had a 9-11% pre-print discount of price to mean target, which is why the fall produced no net cut. The "what would change the reading" paragraph should be inverted: the regression and the six-print history make a 3-4% cut in the mean target over the next two to three months the base case after the 8-10 Sep fall, not the exception.

## 5. Estimate-dispersion mapping (task 5)

| Revenue $m | Base $m | Growth % | Nights (log-additive) % | Note |
|---|---|---|---|---|
| 14,990 | 14,231 | 5.33 | 2.88 | 2.9 |
| 14,990 | 14,100 | 6.31 | 3.84 | 3.8 |
| 15,730 | 14,231 | 10.53 | 7.96 | 8.0 |
| 15,730 | 14,100 | 11.56 | 8.96 | 9.0 |
| 16,290 | 14,231 | 14.47 | 11.80 | 11.8 |
| 16,290 | 14,100 | 15.53 | 12.84 | 12.8 |

Reproduced. Implied prices at 16.5x ($166.0 / $173.4 / $179.1) and the EPS rows (EBITDA 5,293 / 5,757 / 6,296) reproduce. Caveat for the synthesis (finding 5 and claim 2 below): the "consensus nights +8-9%" is a derived quantity under fixed ADR, FX and take rate, not a nights consensus; the Zacks FY26 base is itself 0.9% below delivered, so about half of the FY27 revenue gap to management is base; and the one direct nights consensus in the brief (Bloomberg FA 3Q26 +11.1%, 4Q26 +10.1%) is 0.4 points below management's delivered quarters, not 2.

## 6. Quote spot-checks (task 6)

| Row | URL fetched | Result |
|---|---|---|
| Rosenblatt (Investing.com, 1 Sep) | yes | All three thesis phrases verbatim. KPI row drops one word: the page reads "Nights and seats booked growth accelerated to 10% year-over-year in the quarter"; the CSV omits "growth" (finding 7) |
| Bernstein (TipRanks, 24 Aug) | yes | All seven phrases verbatim; Richard Clarke, $217 from $168 |
| Raymond James (Investing.com, 8 Sep) | yes | All three phrases verbatim; Josh Beck, Market Perform to Outperform, $200 |
| Goldman 20 Jul (MarketScreener) | yes | Headline verbatim, "Maintains Neutral Rating" present, 20 Jul 2026 06:41 EDT |
| Goldman 7 Aug (MarketScreener) | yes | Headline verbatim "Adjusts Airbnb Price Target to $165 From $155", 7 Aug 2026 11:28 EDT; no rating on the visible page (finding 8) |
| MarketBeat 30 Jul MS alert | yes | Page no longer carries the Morgan Stanley action; carries the consensus line quoted (2 / 25 / 11 / 2, $179.97) and a Gordon Haskett raise to $180 from $146 |

No fabricated quotes. One near-verbatim slip.

## 7. Goldman correction and feed label errors (task 7)

Goldman: the correction (Neutral $165) is applied as separate columns in `D_live_targets_2026-09-12.csv` and a separate block in `D_tape_percentiles.csv`; the note uses the as-pulled tape for the headline numbers while stating the corrected mean ($182.13 vs $181.81) and the corrected rating mix (22 / 9 / 1). Consistent. The 20 Jul Neutral label is verified on the MarketScreener headline; the 7 Aug $165 headline carries no rating, so "Neutral $165" is Neutral by continuity, which the CSV should say.

Morgan Stanley: web sources (MarketScreener, TheFly) show $125 from $130 (May 2025), $130 from $125 (Jul 2025), $120 from $130 (Aug 2025) and $125 from $120 (30 Jul 2026), and no January 2026 action; the feed's 13 Jan 2026 "raises $120 to $130" row is the spurious one. Live $125 Underweight is confirmed. The note leaves the contradiction unresolved (finding 9).

Wider feed problem (finding 3). Chaining each firm's rows, the stated prior target differs from the feed's own previous target for that firm in 96 actions, 17 of them since Sep 2025 on live-tape firms: Wedbush (feed 130 in Aug 2025, then "from 152" to 200), Evercore (155, "from 190" to 200), Piper Sandler (132, "from 145" to 170), BofA (146, "from 160" to 175), B. Riley (170, "from 180" to 210), Bernstein (162, "from 168" to 217), Mizuho (151, "from 156" to 175), Jefferies (165, "from 160" to 175), Cantor, BMO, Baird, Truist (also a duplicated 12 Jun 2026 row), Goldman and Morgan Stanley. Gordon Haskett (Hold; MarketScreener shows a run of at least nine target changes in 2025-26 ending at $180 from $146 in Aug 2026) has no feed row since Jan 2023. So the feed drops whole firms and roughly a third of intermediate actions, not just two Goldman raises. Consequences: the daily mean-target panel is stepwise wrong between prints, the print-window raise and cut counts are lower bounds, and the "32 live targets" is 32 of a 40-46 universe. The ranking, percentiles and 2Q26 path are robust to this because post-print raises are the actions the feed does carry; the regression is not obviously biased but its dependent variable is noisier than stated.

## 8. Headline claims (task 8)

| Claim | Verdict | Reason |
|---|---|---|
| "The tape is a multiple call on management's delivered numbers" | Partly supported | At 16.5x and 36.2% the whole Zacks revenue range is worth $166-179 and the EPS range $162-190, against a $125-220 tape, so estimate dispersion explains at most a quarter of the target spread; Morgan Stanley, Truist, Raymond James, Rosenblatt and DA Davidson fit the reading. Bernstein does not: "25.5 times its core earnings" is a P/E, and $217 / 25.5 = $8.51 of core EPS, 40% above delivered FY27 $6.08 and 27% above ambition, i.e. out-year and ex-SBC earnings well above management's FY27 case (finding 4). The claim is also partly tautological: without each house's estimates a target cannot be split between multiple and numbers, and the note's construction assigns all of it to the multiple by design |
| "Consensus nights about 2 points below delivered" | Partly supported | 1.0 point on the Zacks FY26 base, 2.0 on the delivered base; it is a derived figure under fixed ADR, FX and take rate, half of the gap is the FY26 base, and the direct quarterly nights consensus is 0.4 points below management. Say "one to two points, derived from revenue" and label the decomposition JUDGEMENT |
| "Targets chase up, not down" | Not supported | Sign-split regression, the six down prints since 2022 (mean -3.8% at +20 sessions, 2Q24 -14.1%), the 42-session response to non-print drawdowns (-5.0%) and the note's own 1Q25 row all show targets chasing down with the same lag. What is supported: print-day cuts are rare, and a down print that follows a run-up or a wide pre-print discount does not produce a net cut within 20 sessions |
| "Positioning has no predictive content" | Partly supported | The tests are in-sample correlations with n 13-78 and no out-of-sample check; the correct statement is that no content is detectable at these sample sizes. The one result at p 0.05 (3-month change in Buy share vs forward 1-month excess, r -0.24) is the right sign for a contrarian signal, which the note dismisses as wrong-signed for a confirming one |

## 9. What the synthesis should and should not use (task 9)

Use (MEASURED unless marked):

- Implied EV / FY27 delivered EBITDA per target and per percentile, both bases (`D_tape_percentiles.csv`, `D_target_implied.csv`): 15.3x at $165, 15.9x at the price, 17.1x at the mean and median, 18.9x at $200, 21.0x at $220; FY27-end basis about one turn lower.
- Required EBITDA, revenue and revenue growth at 13.5 / 16.5 / 18.5x. The nights column only with the decomposition relabelled JUDGEMENT (ADR +3.0%, FX +0.6pp removed, take rate flat).
- Zacks FY27 revenue range mapped to nights +2.9% to +11.8% (delivered base) and to $166-179 at 16.5x; consensus $15.73bn to $173.4.
- The 2Q26 revision path ($159.82, $172.68, $179.55, $181.81), 24 raises 0 cuts, chase 0.71, as a print-day fact.
- The lagged chase regression as a range: sum of betas 0.30-0.40 over three months, lag 1 largest, contemporaneous 0.04-0.11; symmetric in sign.
- Positioning levels: short interest 2.2% (bottom decile of its history), Buy share 59.5% (series high), mean target premium +6.8% against a since-2023 median of +8.8%, price above the mean target on 20% of days.
- The Goldman correction (Neutral $165) and the feed-coverage caveat, expanded per finding 3.
- Truist's published 2027E EBITDA $5.37bn (7.4% below delivered) as the only bear operating number; Raymond James's nights +10-12% is worth $176-179 at 16.5x (not $178-184).

Do not use:

- "Targets chase up, not down", and the inference that the 8-10 Sep fall will not produce cuts; the base case is a 3-4% cut in the mean target over two to three months.
- Bernstein as evidence that bulls carry management's operating case; its 25.5x is a P/E on out-year core EPS around $8.5.
- The nights numbers at the tape extremes ($125 needs nights -25%, $220 needs +40%) as operating forecasts; they are the arithmetic of a held multiple and show only that the ends of the tape are multiple calls.
- The contemporaneous-beta t of 1.5 as a finding; the "34-37% Hold-or-worse on the 32-firm tape" (it is 31% on 32 firms, 37% on 35); the Raymond James "$178-184".
- The second decimal of any multiple (caveat 1 in the note already says this).

Relabel: headline-table caption "ANCHOR inputs ... ADR +3.0%, FX -0.6pp, take rate flat" to JUDGEMENT (task-set); section 6 "consensus is nights +8.0% to +9.0%" to MEASURED-derived with the decomposition as JUDGEMENT; section 5 bullet 1 from MEASURED to "not supported"; section 7 "none has measured predictive content" to "none shows detectable content in the in-sample tests available".

## 10. Numbered findings

| # | Severity | File | Location | What is wrong | Fix |
|---|---|---|---|---|---|
| 1 | material | D_sell-side-dispersion.md | s.5 bullet 1, s.5 last para, s.7 closing sentence, s.1 implicit | "Targets chase up, not down" rests on the last eight prints; the six down prints since 2022, a sign-split regression and non-print drawdowns show symmetric chasing; 2Q25 had 6 cuts | Reword to "targets chase the price both ways with a one-to-two-month lag; print-day cuts are rare; a down print after a run-up or a wide pre-print discount produces no net cut within 20 sessions". Invert the "what would change the reading" paragraph: a 3-4% cut is the base case. Add the 23-print table to `D_print_revisions.csv` or a new file |
| 2 | material | D_02_revisions_positioning.py; D_chase_regression.csv; note s.5 bullet 2 | `S_no = S.iloc[::L]` (offset 0 only) | Block results depend on the offset: R2 0.19-0.34, contemporaneous beta 0.035-0.111 (t 0.9-3.1, significant in 10 of 21), lag-1 0.09-0.19; offset 0 is the max R2 and near-min contemporaneous t | Loop over the 21 offsets and report mean and range; cite the Newey-West daily numbers as the single estimate; drop "contemporaneous response is small (t 1.5)" |
| 3 | material | note s.2, s.8 caveat 2; D_live_targets_2026-09-12.csv; D_target_panel_daily.csv; D_print_revisions.csv | feed coverage | The feed misses whole firms (Gordon Haskett, Hold $180 from $146 Aug 2026, no row since Jan 2023) and about a third of intermediate actions (96 prior-target chain breaks, 17 since Sep 2025 on live-tape firms), not only two Goldman raises; print-window counts are lower bounds; the tape is 32 of 40-46 | State the chain-break count and the Gordon Haskett omission in caveat 2; label n_raises / n_cuts as lower bounds; add a `chain_break` flag column to the live-targets file |
| 4 | material | note s.1 bullet 2, s.4 Bernstein, s.4 summary; D_analyst_own_multiples.csv | "25.5 times core earnings" tested against EBITDA | 25.5x is a P/E; $217 / 25.5 = $8.51 core EPS, 40% above delivered FY27 EPS, so Bernstein carries out-year or ex-SBC earnings well above management; "every bull with a published number is at or below management's delivered operating case" fails for Bernstein | Recompute as P/E; reword the Bernstein paragraph and the camps summary; keep "12% growth is consensus-like" |
| 5 | material | note s.1 headline-table caption, s.2, s.6 reading | "ANCHOR inputs ... ADR +3.0%, FX -0.6pp, take rate flat"; "consensus nights 8-9%, two points below" | The decomposition terms are not in the brief; they are task-set JUDGEMENT. The nights gap is derived, 1-2 points, half of it FY26 base; the direct quarterly nights consensus is 0.4 below management | Relabel; say "one to two points, derived from revenue consensus under fixed ADR/FX/take rate"; cite the Bloomberg quarterly nights consensus alongside |
| 6 | minor | note s.4 Raymond James; D_analyst_own_multiples.csv note field | "$178-184" | Nights +10% to +12% at 16.5x and 36.2% on the spot basis is $176.4-179.3 | Correct the figures |
| 7 | minor | D_thesis_quotes.csv | Rosenblatt KPI row | Page reads "Nights and seats booked growth accelerated to 10%"; CSV omits "growth" | Restore the word |
| 8 | minor | D_thesis_quotes.csv; note s.4 Goldman | 7 Aug 2026 row "Neutral" | The 7 Aug MarketScreener headline carries no rating; Neutral is by continuity from the verified 20 Jul headline | Say "rating by continuity" in quote_type |
| 9 | minor | note s.4 Morgan Stanley, s.8 caveat 2; D_analyst_actions_2026-09-12.csv | "cannot both be right" | Web sources show no Jan 2026 action; the 13 Jan 2026 "$120 to $130" row is the spurious one; live $125 UW confirmed. Feed also duplicates Truist 12 Jun 2026 | State which row is wrong; note the duplicate |
| 10 | minor | note s.7 reading | "on the 32-firm active tape it is 34-37%" | Hold-or-worse is 10 / 32 = 31.3% (feed and corrected) and 13 / 35 = 37.1% | Correct to 31-37% |
| 11 | minor | note s.3 reading | "Only three targets (Mizuho, BofA, Jefferies at $175 and Benchmark at $180)" | Four names | "four targets" |
| 12 | minor | note s.5 bullet 1 | "The two -8% prints drew no cut in the mean target at all" | 2Q25 drew 6 cuts and 8 raises; the mean was flat | "no net cut" |
| 13 | minor | note s.7 reading, s.1 | "none has measured predictive content" | In-sample, n 13-78, no out-of-sample test; the p 0.05 result is contrarian-signed | "no detectable content at these sample sizes"; note the sign |

## 11. Method note

Re-runs: `py -3.13` on all three scripts in the worktree, outputs compared with `cmp` against a scratchpad backup. Hand recomputes and the regression robustness (21 offsets, HC1, sign-split, 23-print table, non-print drawdowns) were run from the saved CSVs in a scratchpad session and not written to the repo. Web checks by fetch of the cited URLs on 12 Sep 2026. Nothing in `data/processed/reverse_dcf/D/` was modified; the re-run left every file byte-identical.
