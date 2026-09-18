# D1 — 3Q26 nights, level and y/y

## 1. Header
- Line: D1 · Judge's question: "Why 146.3m when 28 sell-side estimates average 148.9m and the lowest is 147.0m?"
- Digger: opus · Date: 2026-09-18 · Commit: e39d9e4 (branch `theo/pitch-model-v2`; the brief names f1ce2cd, which this branch has since moved past)

**One-sentence answer to the judge.** 146.3m is not the reviews index's reading — the index's own headline row reads **+10.04% (147.0m, exactly the Street's lowest estimate)** — it is that row **corrected for the +0.52pp average over-prediction the index makes on its own ten scored walk-forward quarters**, and that correction (10.041 − 0.518 = **+9.52% → 146.32m**) is the whole of the 2.6m gap to the Street mean; the index also fails its pre-registered 0.75 validation hurdle on both windows once the 2023 training quarters are re-read from a fresh vintage, so the number is a bias-corrected read with a caveat, not a validated survivor.

## 2. The number

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 146.3 | 145.0 | 147.0 | m nights | memo v3, 17 Sep 2026 (band +8.5 to +10.0) |
| base_yoy | 3Q26 | 9.5 | 8.5 | 10.0 | pct | same |
| short | 3Q26 | 145.0 | 143.4 | 146.3 | m nights | memo v3 scenario column; low = P10 of the adopted print object |
| short_yoy | 3Q26 | 8.5 | 7.3 | 9.5 | pct | same |
| breaker | 3Q26 | 147.0 | 147.0 | 149.2 | m nights | management's "low double digits" floor; high = P90 of the adopted print object |
| breaker_yoy | 3Q26 | 10.0 | 10.0 | 11.7 | pct | same |

Base is the team's evidence-weighted view; short is the print landing at the low end; breaker is management delivering its guide (the "low double digits" floor is +10.0%, i.e. 147.0m — the same number as the Street's lowest estimate, so the breaker case and the bottom of the sell-side range coincide exactly).

All six levels are **recomputed here** from the printed 3Q25 base of 133.6m (`data/processed/abnb_driver_history_quarterly.csv`) — see `d1_scenarios.csv` in the receipt folder. Exact recomputed levels before rounding: base 146.29 / 144.96 / 146.96; short 144.96 / 143.38 / 146.29; breaker 146.96 / 146.96 / 149.20.

**Reproduced vs inherited, cell by cell.**
- **Reproduced (exit 0, this machine, this commit):** the 133.6m base and the 2Q26 naive +10.342%; the index's raw read +10.041% and its 8.56–11.52 band; its W2 ratio 0.6832 and W1 ratio 0.8371; its walk-forward bias +0.5185pp (W2, n 10) and +1.6318pp (W1, n 14); the bias-corrected **+9.5226% → 146.32m** that the committed 146.3m is; the re-vintaged W2 ratios 0.757 / 0.841; the external stack (n 12, median +9.23%, range 6.75–11.96); every nights level in the table above from its growth rate.
- **Inherited (not reproduced here):** the *choice* of +9.5% as the point (no script in my packages emits 9.5 or 146.3 — it is a judgement selection that the recompute now shows is exactly the W2 bias correction); the band widths +8.5/+10.0 (memo v3) and the adopted N(9.5, 1.70) that gives the outer low/high; the +8.5% short and the "low double digits" breaker floor; the RNPL module's independent +9.49% / 146.3m (D2's package, out of my lane); the Bloomberg MODL aggregate (28 estimates, 147.0 / 148.9 / 151.0m, 12 Sep 2026) — licensed, never in the repo as raw.

### 2a. Model inputs (machine-readable)

Per DEC-0004 (base 146.3m / +9.5%; band 8.5–11.0 for pre-registration, P10–P90 of N(9.5, 1.70) for workbook scenarios) and DEC-0005 (Street bar 149.0m). One item per row, same values as the §2 table.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| nights_m | base | 3Q26 | 146.3 | m nights | bias-corrected index read, 133.6m x 1.0952 |
| nights_m | short | 3Q26 | 145.0 | m nights | print lands at the low end |
| nights_m | breaker | 3Q26 | 147.0 | m nights | management delivers "low double digits" |
| nights_yoy_pct | base | 3Q26 | 9.5 | pct | on the fixed 133.6m 3Q25 base |
| nights_yoy_pct | short | 3Q26 | 8.5 | pct | on the fixed 133.6m 3Q25 base |
| nights_yoy_pct | breaker | 3Q26 | 10.0 | pct | guide floor |
| nights_m_low | base | 3Q26 | 145.0 | m nights | +8.5% |
| nights_m_low | short | 3Q26 | 143.4 | m nights | P10 of N(9.5, 1.70), +7.3% |
| nights_m_low | breaker | 3Q26 | 147.0 | m nights | +10.0%, the guide floor is the floor |
| nights_m_high | base | 3Q26 | 147.0 | m nights | +10.0% |
| nights_m_high | short | 3Q26 | 146.3 | m nights | +9.5% |
| nights_m_high | breaker | 3Q26 | 149.2 | m nights | P90 of N(9.5, 1.70), +11.7% |
| street_nights_m | street | 3Q26 | 149.0 | m nights | Bloomberg MODL 12 Sep, n 28 (DEC-0005) |

## 3. Derivation chain
1. Inside Airbnb review dumps, 363 market-vintages across 123 markets, review dates 2018 to 17 Aug 2026 → **raw not on this machine** (Krish's `abnb_ia_capture`); the counted layer is committed →
2. `data/processed/q3nowcast/E/market_vintage_daily.csv` (697,888 rows, 123 markets, 363 vintages), `market_vintage_monthly.csv`, `market_geo.csv` →
3. `analysis/src/q3nowcast/E5_backtest.py` → `data/processed/q3nowcast/E/backtest_abnb_quarterly.csv`, `backtest_wf_paths.csv`, `backtest_survivor_robustness.csv` →
4. `analysis/src/q3nowcast/E6_nowcast.py` → `data/processed/q3nowcast/E/q3_2026_nowcast.csv`, row `measure=yoy_all, weighting=w_reviews, region=GLOBAL`, column `implied_nights_yoy` = **10.041046** (columns `lo`, `hi` = 8.5641, 11.5179; `wf_ratio_vs_naive` = 0.683209) →
5. `data/processed/pitch_model_v2/receipts/D1/d1_recompute.py` → mean of `err_feature` over the ten W2 scored quarters in `backtest_wf_paths.csv` = **+0.5185pp**; 10.041046 − 0.5185 = **9.5226%**; × 133.6m (`abnb_driver_history_quarterly.csv`, year 2025 q 3, `nights_m`) = **146.32m** →
6. committed line: **146.3m, +9.5%** (`deck/drafts/memo_v3_short_2026-09-17.md` "Nights" and scenario table; `PREREG_ABNB-INT-v1.md` INT-02 and D-02(a)).

Corroborating chains, both reproduced: `G2_external_backtests.py` → `data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv`, 12 knowable features on nights, median **+9.23%** (6.75 to 11.96); and `analysis/src/q3nowcast_v2/E/V6_backtest_substituted.py` → `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv`, the re-vintaged validation.

The index is a **stay-date** series mapped onto a **booking-date** KPI by an OLS slope of 0.32 nights-points per index-point (r 0.86, 14 quarters). That mapping, not the counting, is where the forecast lives.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-08-06 | 2Q26 shareholder letter, via `docs/2026-09-06_research-inventory.md` §311 and `data/processed/overnight/02_guidance_ledger.csv` | 3Q26 guide: nights "low double digits", revenue $4,690–4,770M, GBV mid-teens | Governs the breaker definition. "Low double digits" is a bucket, not a company range; the ≥10.0% → 147.0m mapping is ours (`nights_baseline_reconciliation.csv`, last row) |
| 2026-09-11 | `docs/q3nowcast/SYNTHESIS.md` (Krish) | 3Q26 nights **+9.5 to +10.0%, band 8.5 to 11.0**; index beats naive 0.68x; headline row +10.0, 8.6 to 11.5 | Governs the *evidence*; the 0.68 claim is **superseded by WPK-A (14 Sep) and SR (15 Sep)**; the 8.5–11.0 band is superseded as the memo's band by memo v3's 8.5–10.0 |
| 2026-09-11 | `docs/rnpl-short-audit/01_*.md`, `00_SYNTHESIS.md` (Theo) | Unified RNPL module base 3Q26 **+9.49% (146.3mm)**, band 8.76–10.25 | Governs as an independent second route to the same level. Its 4Q26/FY27 legs are D2's and D3's lines, not mine |
| 2026-09-14 | `05_backtests/WPK_reviews-index-2023-vintage.md` (build A) | T1 wedge-constancy **FAILS** (−9.96pp global vs a ±2.0pp line); T2 attrition **FAILS** (0.660 vs a 0.75–0.90 band); the quoted 0.683 was **W2-only** and W1 was already **0.837**; honest re-vintaged W2 **0.757**, literal **0.841** — both above the 0.75 hurdle | **Governs** the validation status of the index. Supersedes the SYNTHESIS survivor headline |
| 2026-09-15 | `05_backtests/SR_QUARTER_SUBMISSION_READINESS_v1.md` | "Do not present the old 0.68x result as a current two-window validated forecast." Also: the 2023 archive result "supersedes the older stable-wedge/survivor headline"; "descriptive and scenario use remain possible with limitations" | **Governs** how the index may be quoted |
| 2026-09-17 | `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json` (A09 rev 2) | Adopted print object **N(9.5, 1.70)**; `centre_source` = "team nowcast +9.5% (reviews index 9.5-10.0 **bias-corrected 9.52**; external stack 9.2; module 9.49)"; `sd_source` = the fresh-vintage W2 RMSE range 1.634–1.816. P(≥147.0m) **0.386**, P(≥147.8m) **0.260** | **Governs** the distribution and, crucially, states in the record that the point is the bias-corrected read. Supersedes R01/R02 revision 1 (0.42 / 0.32) |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` | 3Q26 nights **+9.5% (146.3m), band 8.5–10.0**; short 145.0m / +8.5%; breaker gate ≥10.6%; Street 147.0 / 148.9 / 151.0m, n 28, Bloomberg MODL 12 Sep | **Governs** the committed line and the scenario points. Its sentence "walk-forward RMSE 0.68x the naive" is the SR note's forbidden wording — see §7 |
| — | `analysis/src/q3nowcast/F*.py`, SYNTHESIS §2 row F | Calendar booking pace: flow y/y correlates **−0.43** with disclosed nights; sign inverted; retired as a nights input | Governs: direction check only, never a number |

**Web fetches: zero.** Everything above is in the repository. The one number that is not (the Bloomberg MODL aggregate) is licensed and is quoted only as a dated aggregate, per AGENT_BRIEF §5 and the V1 convention.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/D1/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id D1 --watch data/processed/q3nowcast --watch data/processed/q3nowcast_v2 --cmd "python3 …/receipts/D1/run_krish_script.py analysis/src/q3nowcast/E5_backtest.py && … E6_nowcast.py && … analysis/src/q3nowcast_v2/E/V6_backtest_substituted.py && python3 …/receipts/D1/d1_recompute.py"` · Exit: 0 · Wall: 7.0 s · Interpreter: python3 (3.13.0, pandas 3.0.0, numpy 2.4.2, scipy 1.17.0; `.venv-pd2` not needed)
- Output: `data/processed/q3nowcast/E/q3_2026_nowcast.csv` cell `implied_nights_yoy, row (yoy_all, w_reviews, GLOBAL)` = 10.041046; `backtest_wf_paths.csv` W2 mean `err_feature` = +0.518452 → derived level **146.32m** · Committed value: **146.3m** · Tolerance: ±0.1m · **Match: yes** (|Δ| = 0.02m)
- Restored: true. Six watched CSVs were rewritten with a maximum absolute difference of **1.4e-14** (float noise); no new files; the tree was returned to HEAD. Side receipts: `receipt_E5.json`, `receipt_E6.json`, `receipt_G2.json`, `receipt_V6.json`, each exit 0, with `stdout_*.txt`.
- Also reproduced in the same run: W2 ratio 0.683209 and jackknife 0.6276–0.8598; W1 ratio 0.837125 (n 14); the four V6 variants **0.683 / 0.841 / 0.757 / 0.713** byte-identical to the committed `t1_fail_e5_rerun.csv`; the external stack n 12, median +9.2324%.

**What could not be reproduced, and what stood in for it.** The 2023 Inside Airbnb raw mirror (114 files, 4.88 GB) lives on Krish's machine and is not on this one, so WPK-A's **T1 (wedge constancy), T2 (attrition curve) and T3 (NYC Local Law 18)** could not be re-derived from raw here; their tables are inherited. The 2026 review dumps are likewise raw-only elsewhere, so `E1`–`E4` (discover, download, count, build index) were not re-run — the reproduction starts at the **committed processed counts** (`market_vintage_daily.csv`, 697,888 rows), which is what the brief asks for. That is a real limit: a counting error inside E3/E4 would survive my reproduction untouched. What I *did* get from the v2 folder is better than expected — `data/processed/q3nowcast_v2/E/market_vintage_monthly.csv` already holds the 2023-vintage counted months, so **V6's re-vintaged backtest ran here without the raw mirror** and confirms 0.757 / 0.841 independently of Krish's Windows box.

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W2 (scored 1Q24–2Q26) | 10 | WF RMSE ratio vs naive, reviews index on nights y/y | **0.683** | 1.000 | n/a (nights is not guided as a number) | no nights consensus in L0 | ≤ 0.75 | pass |
| W1 (scored 1Q23–2Q26) | 14 | same | **0.837** | 1.000 | n/a | — | ≤ 0.75 | **fail** |
| W2, re-vintaged (honest, V6 variant b) | 10 | same, 1Q23 re-read from the 2023 dumps | **0.757** | 1.000 | n/a | — | ≤ 0.75 | **fail** |
| W2, re-vintaged (literal, V6 variant a) | 10 | same | **0.841** | 1.000 | n/a | — | ≤ 0.75 | **fail** |
| W2 | 10 | WF mean error (pred − actual), reviews index | **+0.52pp** | 0.00 by construction | n/a | — | not pre-registered | descriptive |
| W1 | 14 | same | **+1.63pp** | 0.00 | n/a | — | not pre-registered | descriptive |
| W1 | 14 | sign accuracy of the index | **0.50** | — | — | — | not pre-registered | coin flip |
| W2 | 10 | best external feature (HLT RevPAR, full quarter) | 0.665 | 1.000 | n/a | — | ≤ 0.75 | pass |
| W1 | 14 | same feature | 0.755 | 1.000 | n/a | — | ≤ 0.75 | **fail (by 0.005)** |
| W2 / W1 | 10 / 11 | NTTO I-94 overseas, qtd 1 month | 0.743 / 0.903 | 1.000 | n/a | — | ≤ 0.75 | W2 pass, W1 fail |
| n/a | 5 | calendar booking pace vs disclosed nights | r = **−0.43** (sign inverted) | — | — | — | positive correlation | **fail; retired** |
| T1 (WPK-A) | 1,357 market-months | fresh-minus-stale within-vintage y/y wedge | **−9.96pp** global; every region fails | — | — | — | \|Δ\| ≤ 2.0pp global, ≤ 3.0pp regional | **fail** |
| T2 (WPK-A) | 1,246 pairs | attrition ratio at 26–40 months | **0.660** | — | — | — | 0.75–0.90 | **fail** (the band itself was mis-derived; the hazard is 12–18%/yr) |

**Strongest known failure:** the index's central reading is **+10.0%, which is 147.0m — the Street's lowest estimate — and 146.3m exists only because we subtract the index's own +0.52pp walk-forward bias, a correction estimated on ten quarters whose training years fail their vintage-constancy test and whose W1 counterpart would subtract +1.63pp instead and put the line at 144.8m.**

**Two things this table does not say, and the memo must not either.** (a) The index *does* beat naive on both windows (0.683 and 0.837 are both below 1.0); what it fails is the stricter 0.75 survivor hurdle, on W1 outright and on W2 once re-vintaged. (b) There is **no Street nights baseline inside the harness** — the L0 vintage register's 19 `nights` rows are all `role=at_print` historical with `vendor_not_recorded` (`PREREG` INT-02). The 148.9m bar is a Bloomberg MODL aggregate, not a scoreable consensus object, so every "versus consensus" claim on this line is a memo claim, not a harness claim.

## 7. Kill list and consistency
- **Kill-list check: none of this line's numbers is on AGENT_BRIEF §6 or margin-build §9.** Two near-misses checked and cleared: (i) "the 120-market panel as a nights measurement" is the Inside Airbnb *listings/calendar* bottom-up panel (gate G3 in `docs/rnpl-short-audit/03_*.md`), a different object from the 123-market **review-date** stays index used here — the reviews index is not the killed panel; (ii) "any FY27 level edge without the +9.2–11.5% band" binds D3/R6, not this line.
- **Conflict 1, and it is live: memo v3 quotes the index at "walk-forward RMSE 0.68x the naive" with no caveat.** The SR note (15 Sep) says in terms: "Do not present the old 0.68x result as a current two-window validated forecast." The later note wins; memo v3 is the later *document* but the SR note is the later *finding about that number*, and WPK-A (14 Sep) is the measurement both rest on. **The memo sentence must be changed before submission.** The defensible wording is: *"walk-forward RMSE 0.68x naive on the 10-quarter window, 0.84x on the 14-quarter window, and 0.76x when the 2023 training quarters are re-read from a fresh vintage; it beats a naive forecast on both windows but does not clear our 0.75 survivor hurdle on either."*
- **Conflict 2, the band.** Three bands are in the record for one number: **8.5–10.0** (memo v3), **8.5–11.0** (SYNTHESIS and PREREG INT-02), and **7.3–11.7** (the 10th–90th of the adopted N(9.5, 1.70), 17 Sep). They are not reconcilable by rounding: 8.5–10.0 is 1.5pp wide, the adopted object is 4.4pp wide. INT-02's refutation rule is written against 8.5–11.0, so publishing 8.5–10.0 in the memo while scoring against 8.5–11.0 on 6 Nov would score a number we never published.
- **Conflict 3, the point that is not the index's point.** SYNTHESIS, PREREG and memo v3 all present +9.5% as "the reviews index". The index's headline row is **+10.04%**; +9.5% is the bias-corrected read, and only `adopted_print_states_v2.json` (17 Sep) says so in the record. Presented the current way, a judge who reproduces `q3_2026_nowcast.csv` finds 147.0m and concludes we shaded the number.
- **Conflict 4, stale probability in a question folder.** `risk-q3-nights-meets-guide/README.md` still shows revision 1, **P = 0.42**, while `forecasts/2026-09-17-forecast.json` is revision 2, **P = 0.39** (memo v3 quotes 0.39, correctly). The README is stale, not the memo. Same for R02 (README 0.32 rev 1; the adopted object gives 0.260). E1's lane to fix; flagged here because D1 feeds it.
- **Conflict 5, the Street level.** Memo v3 and `research/notes/2026-09-13_market-implied-model.md` use mean **148.9m**; `analysis/src/reverse_dcf/E_positioning_card.py` uses **149.0m** with the same low/high/n; the EEG legend value is **148.96m** at 12 Sep. All one MODL read, rounded three ways. Pick one before the memo, because the "2.6m below the Street" headline moves to 2.7m.
- **Consistency with other lines.** D4's ADR ($176.9, +3.3%) sits on the MODL mean, so D6's GBV identity carries the entire nights disagreement; at 146.3m × $176.9 the GBV is ~$25.88bn against the Street's $26.35bn. D-04 (PREREG) is the open choice about which *block* is registered — the backtest-winner block uses this 146.3m, the registered block uses 147.38m. D2 must not re-apply the RNPL cancellation drag: the +9.49% module and this +9.5% are two routes to the same level, not two effects to be stacked.

## 8. Open choices
1. **How the index's validation status is worded in the memo.** Options: (a) keep "0.68x naive" as it stands; (b) the three-ratio sentence in §7 (0.68 W2 / 0.84 W1 / 0.76 re-vintaged, beats naive on both windows, clears 0.75 on neither); (c) drop the ratio and call the index descriptive corroboration. — **Recommendation: (b).** — Why: (a) is what the SR note forbids and is the single most reversible thing a judge can check in four minutes; (c) throws away the one series that does beat naive on both windows, which is a real and defensible finding. (b) is the only wording that is both true and still an argument. It costs about 25 words.
2. **Whether the memo says out loud that 146.3m is a bias correction.** Options: (a) present +9.5% as "the index read", as now; (b) present the chain — index +10.0%, minus its own +0.52pp walk-forward bias, equals +9.5% — in the memo body; (c) present it only in the appendix/Q&A. — **Recommendation: (b), one clause.** — Why: the chain is the strongest version of our argument (we are not guessing lower than the Street, we are applying the series' own measured error) and it is already in `adopted_print_states_v2.json`. Leaving it out invites exactly the judge question in the header, with no good answer. The cost is admitting the W1 bias would give 144.8m, which we should pre-empt rather than be shown.
3. **One band for D1.** Options: (a) 8.5–10.0 (memo v3); (b) 8.5–11.0 (PREREG INT-02, the pre-registered refutation range); (c) 7.3–11.7, the 10th–90th of the adopted N(9.5, 1.70). — **Recommendation: (b) for the pre-registration and the 6 Nov score sheet, (c) for the workbook's scenario low/high, and retire (a).** — Why: INT-02's pass/fail is already written against 8.5–11.0 and a frozen card cannot be re-banded after the fact; the adopted normal is the object every probability in the memo (R01 0.386, R02 0.260, X01, S01) is computed from, so the workbook must use it or the scenario prices stop tying to the probabilities. (a) is narrower than either and is not derived from anything.
4. **D-02: the card's nights value.** Options: (a) reviews index +9.5% / 146.3m; (b) team baseline +9.9% / 146.8m; (c) index point with the baseline band. — **Recommendation: (a), unchanged.** — Why: after the WPK re-vintaging, (a)'s claim to be "the only scored survivor" is weaker than PREREG says, but (b) is a bridge with no walk-forward score at all and the harness carries no team method on `nights_m`; and (a) is now corroborated three ways at the same level (bias-corrected index 9.52, RNPL module 9.49, H1–H2 bridge 9.49) with the external stack 0.3pt below. (c) mixes a point and a band from different objects, which PREREG itself calls not defensible.
5. **Whether to re-run E on the September Inside Airbnb dumps before 2 Oct.** Options: (a) yes, re-run E1–E6 and re-centre; (b) no, freeze at the 17 Aug review window and disclose the cut-off. — **Recommendation: (a) if and only if the dumps land by 27 Sep and Krish's raw store is reachable; otherwise (b), stated in the memo.** — Why: September is the one month of 3Q26 no current read covers, and the adopted update rule is already published (centre 9.0 → P 0.28, 9.5 → 0.39, 10.0 → 0.50), so a re-centre is cheap and mechanical. But the raw dumps are not on this machine, E1–E4 cannot run here, and a half-finished re-run two days before submission is worse than a disclosed cut-off.
6. **Which MODL rounding the memo uses for the Street.** Options: (a) 148.9m; (b) 149.0m; (c) 148.96m. — **Recommendation: (a), and make `E_positioning_card.py`'s 149.0 match it.** — Why: it is what memo v3, the market-implied note and the reverse-DCF audits already use; the positioning card is the odd one out. Any of the three is defensible; two of them in one deck is not.

## 9. Judge Q&A
1. Q: Why 146.3m when 28 sell-side estimates average 148.9m and the lowest is 147.0m? A: Our review-date stays index, built from 363 Inside Airbnb dumps across 123 markets, reads +10.0% for 3Q26 — which is 147.0m, the bottom of your range. Over its ten scored walk-forward quarters that index has over-predicted printed nights by an average of 0.52 points. Subtract its own measured bias and you get +9.52%, or 146.3m. Two independent builds land in the same place: the RNPL lap module at +9.49% and the H1–H2 seasonal bridge at +9.49%, and an external stack of twelve knowable series — hotel RevPAR, NTTO arrivals, CPI lodging, Spanish INE — medians +9.2%. So the disagreement is not a level opinion; it is that the Street's bar is management's guide carried forward one-for-one after the 2Q26 beat, and no measured series we can find is accelerating through August.
2. Q: Your alternative-data series beats a naive forecast 0.68 to 1. Does that survive scrutiny? A: Partly, and I will give you the number that does not. 0.68 is the ten-quarter window. On the fourteen-quarter window it is 0.84. And when we bought a second Inside Airbnb vintage from March 2023 and re-read the training quarters from fresh data instead of from a stale dump, the ten-quarter ratio moved to 0.76. So it beats naive on both windows but clears our own 0.75 survivor hurdle on neither. It is corroboration with a measured error, not a validated forecaster, and we do not present it as one.
3. Q: This is a stay-date series. Nights and Seats Booked is a booking-date KPI. How do you bridge that? A: With an OLS slope of 0.32 nights-points per index-point, r 0.86, fitted on fourteen quarters, and the walk-forward error of that mapping is exactly the 1.5-point standard deviation in our band. It absorbs the average booking-to-stay lag historically. What it cannot see is a late-quarter shift in when people book — which is precisely where RNPL cancellations and any September demand shock would act. That residual is why our band is 2 to 4 points wide rather than half a point, and why we are not trading the 3Q26 level: we are trading the 4Q26 guide that the 3Q26 GBV mechanically sets.
4. Q: What if management delivers "low double digits" again? A: Then we are wrong on the gate, and 147.0m is the number — the same as your lowest estimate. We put that at 0.39 on our adopted distribution, N(9.5, 1.70); an outright acceleration, 147.8m or better, at 0.26. The flip rule is written down: nights at or above +10.3% with a restated product-bundle contribution of 2.5 points or more and we cover.
5. Q: What single piece of evidence would most change your mind before 5 Nov? A: The September Inside Airbnb dumps, which close the only month of the quarter nothing we hold can see. The update rule is pre-registered and mechanical: re-centre the same normal, and a centre of 9.9 takes P(meets guide) from 0.39 to 0.48. After that, Marriott's Q3 RevPAR on 4 November, since hotel RevPAR is the strongest external feature we have on this KPI.

## 10. Grade
Grade: B — the number reproduces end to end on this machine (exit 0, 146.32m against a committed 146.3m, and the re-vintaged 0.757/0.841 confirmed without the raw mirror), but the object behind it is single-window: its W1 walk-forward ratio is 0.837 and its honest re-vintaged W2 is 0.757, so it does not survive both windows against its pre-registered 0.75 line, and the +9.5% point is a bias correction on top of the index rather than an output of it.
