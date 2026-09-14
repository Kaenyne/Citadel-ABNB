# Audit of workstream B (options-implied): verdict PASS WITH FIXES

Auditor: independent agent, 12 Sep 2026. Scope: `research/notes/reverse_dcf/B_options-implied.md`, `analysis/src/reverse_dcf/B_pull_chains.py`, `B_options_implied.py`, `B_bloomberg_summary.py`, `B_tables.py`, outputs under `data/processed/reverse_dcf/B/`. Saved chain `raw_chain_20260912T044930Z.csv` was used as is; nothing was re-pulled. Scripts were re-run in a scratchpad mirror so the worktree outputs were not touched. Findings CSV: `data/processed/reverse_dcf/audit/audit_B_findings.csv`.

## Verdict

Pass with fixes. No blockers. The options maths is right and every headline number reproduces byte for byte from the saved chain. Three material findings: (1) the "realised print move" series is the QQQ-excess return, not the raw close-to-close return the note says it is, which shifts the base-rate table and the conditional up/down split; (2) two derived columns in a committed-path CSV jointly reconstruct raw Bloomberg IV levels, which the brief says must never be copied; (3) the synthesis has adopted the skew-adjusted RND percentiles, and the lognormal version is the better headline. The headline conclusions (print priced at its own history; skew ordinary; 12-month interquartile range about $125-215) survive all three.

| Check | Result |
|---|---|
| 1 Reproduction | All 24 B_*.csv and B_dist_12m_meta.json identical after re-run (cmp, zero diffs). Straddle 13.544%, ATM IV 31.11 / 38.42 / 37.06 / 36.51, event sd 9.88 / 9.16 / 9.73 / 8.30, RR25 -3.47, percentiles as quoted, P(>179.5) 0.428 |
| 2 Event variance maths | Correct. E = T_post (sig_post^2 - sig_pre^2) = 0.19189 x (0.3842^2 - 0.3111^2) = 0.00975, sd 9.87% (9.88% with exact T). Brief formula gives 0.01903, sd 13.79%. Diffusion term 0.00928. sqrt(2/pi) = 0.798, so 9.5% sd is 7.58% expected absolute move |
| 3 Black-76 inversion | Five strikes by hand match B_chain_clean to 0.01 vol pt (155P 41.12, 160P 39.58, 165P 38.57, 170C 40.20, 170P 37.74, 175C 38.08, 185C 38.21). Forward 171.186 = median of 9 near-ATM parity forwards. r 3.5-4.5% moves ATM IV by 0.02-0.05 pt |
| 4 Skew | RR25 -3.47 (call minus put, standard convention). Flat-vol Black-76 at F 171.19: call10 $5.62, put10 $4.12, ratio 1.363; smile: $5.29 / $4.60, ratio 1.152, relative 0.845. Actual 185C / 155P mids 6.175 / 5.30 = 1.165 |
| 5 12-month distribution | Lognormal at 39.52%, F 177.14: p5-p95 = 85.5 / 98.7 / 125.5 / 163.8 / 213.9 / 271.9 / 313.8, exact match. Variance interpolation weight 0.470 on Dec 27 reproduces 39.52%. Skew RND percentiles reproduce from the saved grid |
| 6 Base rates | Reproduce on `legacy_1d_pct` (rms 8.48, mean abs 6.81, median 5.14, 47.8% at 7%+, 11/12). But that column is the QQQ-excess return (finding 1) |
| 7 Bloomberg | Recomputed from the workbook: crush mean 10.47 / median 10.42 / last 8 10.03, kink45 8.51 (23 of 23 positive), ratio 0.81 on excess returns, corr -0.026; straddles print 11.77 vs 13.30, non-print 9.75 vs 9.45, shares 0.565 / 0.381. All match to 0.005 |

## Findings

### 1. MATERIAL. The realised print-move series is the market-excess return, not the raw close-to-close return

File and location: `analysis/src/reverse_dcf/B_options_implied.py` line 477 (`m["cc_1d_pct"] = m.legacy_1d_pct  # pre-print close -> reaction-day close`); `B_bloomberg_summary.py` line 238; note section 7 (first paragraph and the whole table), section 1 row "Realised print move", section 3.3, `B_reconcile_reaction_files.csv`, `B_print_base_rates.csv`, `B_print_moves.csv`, `B_implied_vs_realised_print.csv`, `B_bbg_print_implied_vs_realised_summary.csv`.

What is wrong. `legacy_1d_pct` in `20_executable_returns.csv` equals `excess_1d_pct` in `abnb_earnings_reactions.csv` on all 23 prints (max difference 0.04 pt); it is the close-to-close return less QQQ. The WS20 note calls it "the full legacy day-1 excess return" (line 21). The raw close-to-close return is `abnb_1d_pct` in the older file, or `entry_postclose_px / pre_close - 1` in the WS20 file (max difference to `abnb_1d_pct` 0.05 pt). The reconciliation table's "diff" column is exactly minus the QQQ day-1 return (max residual 0.07 pt), so the note's explanation for the differences ("different reaction-day conventions") is wrong. The 2Q26 print is quoted as +16.3% in the note and +17.4% in the brief's anchor table; both are right, one is excess and one is raw.

Effect. The options market prices the raw move, so the like-for-like comparison is raw. On raw close-to-close returns (23 prints): rms 8.92%, mean abs 7.07%, median abs 6.87%, 47.8% at 7%+, 34.8% at 10%+, 4.3% at 15%+, 13 up / 10 down, mean +1.16%, last-eight rms 9.19%. Realised rms to mean IV-crush implied sd becomes 8.92 / 10.47 = 0.85 rather than 0.81. The central 9.5% implied event sd is then about 0.6 pt above realised rms, not "about one point". The conditional split on raw returns: nights accelerated 6 up / 2 down (mean +3.9%), decelerated 3 up / 8 down (mean -3.3%); on excess returns 6 / 2 and 1 / 10 (the two flips are 1Q25 raw +1.0% and 1Q26 raw +0.7%, both up days on which QQQ rose 1.5-2.3%). The "priced at its own history" reading survives on either series.

Fix. Relabel `cc_1d_pct` as `excess_cc_1d_pct` everywhere; add a raw column from `entry_postclose_px / pre_close - 1`; report the base-rate table twice or with both columns; make the implied-versus-realised rows and the 0.81 ratio use the raw series; rewrite the reconciliation paragraph (the two files agree once QQQ is added back); quote 2Q26 as +17.4% raw / +16.3% excess.

### 2. MATERIAL. Two committed-path columns jointly reconstruct raw Bloomberg IV levels

File and location: `data/processed/reverse_dcf/B/B_bbg_print_implied_vs_realised.csv`, columns `iv_crush_volpts` and `implied_event_sd_crush_pct`; `B_bloomberg_summary.py` line 233 (comment "raw IV levels deliberately not written (licensed)").

What is wrong. With d = pre - post (the crush column) and pre^2 - post^2 = E x 365/30 (from the sd column), pre + post = (E x 365/30) / d, so both the print-date and reaction-date 30D ATM IV levels are recoverable. Check on two dates: reconstructed 87.8 / 72.9 against the workbook's 88.1 / 73.2 (4Q20), and the same to within rounding on 2Q26. That is 46 raw Bloomberg levels in a file on a committed path. Related but tolerated by the brief's own practice (its anchor table quotes single Bloomberg figures): `B_bbg_term_structure_4sep.csv` writes the four 4 Sep constant-maturity ATM IV levels (30.12 / 33.52 / 35.94 / 37.88) and the 4 Sep realised vols; `B_bbg_iv_history_summary.csv` writes `value_4sep_2026`; the note quotes the same four levels in section 3.2. `B_bbg_print_month_straddles.csv` copies 23 of the workbook's 65 rows of `Implied move %` and `Realized move %` (workbook-derived columns, not raw quotes, but row-level).

Fix. Drop `iv_crush_volpts` from the per-print CSV (the sd column alone gives only pre^2 - post^2 and is a genuine summary), or round the sd to whole points. Keep the summary CSV as is. For the print-month straddle rows, keep only the `realised_over_implied` ratio, or leave the file and let Krish decide; it is the least clear case.

### 3. MATERIAL (decision). The synthesis should quote the lognormal 12-month percentiles as the headline, the skew-adjusted RND as the sensitivity

File and location: note section 5 ("Skew-adjusted RND (preferred)") and the final paragraph of section 5; `B_price_points_for_synthesis.csv` (the three added rows use the skew RND); `docs/reverse_dcf/RUN_STATE.md` synthesis row ($124 / $167 / $217).

What is wrong. Nothing is wrong with the arithmetic; the question is which of two near-identical numbers to carry. The case for the lognormal: (a) it is two numbers (39.5% and $177.1) that anyone can reproduce; (b) its mean equals the forward by construction, whereas the skew RND's mean is $175.7 against a $177.1 forward, a 0.8% shortfall produced by clipping 1.7% negative density, flat extrapolation of a quadratic smile beyond the quoted strikes, and renormalising; (c) the skew RND's tails are not measured: the Jun 27 quotes run from $115 to $250 (log-moneyness -0.42 to +0.35), so p5 $81, p10 $94, p90 $264 and p95 $302 come from the extrapolated part of the smile, and the model-free check cannot validate them (negative mass 14% at Jun 27, 30% at Jan 28); (d) at the quartiles the two agree within $2-4 (p25 $124 vs $126, p50 $167 vs $164, p75 $217 vs $214), which is below the noise from the LEAPS forward (0.5-1.5% of spot) and bid-ask (8-15% of mid). The case for the skew RND is that it respects the measured 25-delta risk reversal of -3.0 to -3.8 vol points at the long expiries; that is a real feature, but it moves the quartiles by less than the method noise and its effect on P(below $150) is 0.40 versus 0.41.

Fix. In the synthesis use lognormal p25 / p50 / p75 = $126 / $164 / $214 (or rounded $125 / $165 / $215 with the method spread stated) and P(above $179.5) 0.41 lognormal / 0.43 skew RND as a range; label the skew RND's p5, p10, p90, p95 as extrapolated (JUDGEMENT on the smile shape, not MEASURED). If the synthesis keeps the skew RND, it should say the mean is 0.8% below the forward.

### 4. MINOR. The 90/110 skew comparison against Bloomberg history is cross-method

File and location: note section 1 row "25-delta risk reversal", section 4 last paragraph ("at or below the 2021-26 median of 4.4"), `B_headline.csv` row `skew_90_110_20nov_volpts`.

What is wrong. The 3.3 points is the agent's own quadratic-smile skew at a 70-day expiry evaluated at 0.9 and 1.1 times spot; the 4.4 median is Bloomberg's 30-day constant-maturity 90/110 skew. Skew in vol points falls with maturity (the note's own table: 3.5 at 35 days, 3.3 at 70, 2.1 at 189). On 4 Sep, the same day, the agent's own method gave 3.0-3.7 at the 28-35 day expiries (`B_bbg_chain_4sep_term_structure.csv`) while Bloomberg's 30D series read 4.51, so the own method sits about 1 point below Bloomberg's. Mapped onto Bloomberg's scale the 11 Sep near-dated skew is roughly 4.5-5.0, around the 55th-60th percentile rather than "at or below the median".

Fix. Say the comparison is approximate and that the like-for-like change is own-method 4 Sep versus 11 Sep (16 Oct 2.8 to 3.5, 20 Nov 1.8 to 3.3). The conclusion (ordinary skew, not a crowded hedge) is unchanged.

### 5. MINOR. "18% richer" in the note, "15% richer" in the headline CSV

File and location: note section 1 row "10% OTM put vs 10% OTM call" and section 4; `B_tables.py` headline note for `call10_over_put10_20nov_relative_to_flat` ("0.85 = downside 15% richer than symmetric").

What is wrong. 0.845 means the market call/put ratio is 15.5% below the flat-smile ratio, equivalently the put is 1 / 0.845 = 1.183 times richer relative to the call. Both are correct statements of the same number; the two files pick different ones.

Fix. Use one phrasing in both places. Also note that the 1.36 benchmark is mostly strike geometry: strikes 10% either side of spot in dollars are 9.4% above and 11.1% below the forward in log terms, and a flat vol at log-symmetric strikes about the forward gives 1.105, not 1.36. The "relative to flat" ratio is the right skew measure precisely because it removes that geometry; the sentence explaining it as "the price distribution is right-skewed in dollars" is fine.

### 6. MINOR. The parity check has little power; the $170 straddle sits on a wide put quote

File and location: note section 2 ("theory_inside_bid_ask true for 118 of 118, so no stale quote was detected"); `B_parity_check.csv`; `B_term_structure.csv` row 2026-11-20.

What is wrong. The bid-ask band on the strike-by-strike forward is 0.5-6.2% of spot wide (median 2.5%), so "spot carry inside the band" is a weak test; the informative check is the within-expiry dispersion of the mid-based forwards (0.25-1.5% of spot), which the note also reports. At 20 Nov the 170 put is quoted 8.85 / 12.30 (33% relative spread), putting that strike's forward 0.43% above the median and the 170 call and put mid IVs 2.5 points apart (40.2 vs 37.7). The headline 13.5% straddle is therefore the mid of a 12.0 / 15.0 market; the smile-model ATM straddle is 13.4%. Several usable 20 Nov quotes last traded before 11 Sep (155 put 9 Sep, 220 call 10 Sep); this is fine because bid and ask, not last, are used, but it should be said.

Fix. State the straddle as 13.5% mid on a 12.0-15.0 market; describe the parity test as necessary, not sufficient; cite the dispersion figure as the stale-quote check.

### 7. MINOR. The event-sd point estimate should carry its sensitivity to the ATM IV fit

File and location: note section 3.2 results table and the 9.5% central reading; `B_headline.csv` rows `event_sd_central_pct`, `event_exp_abs_move_central_pct`.

What is wrong. The pair estimate moves by about 0.7 pt of event sd per 1 vol point of either leg's ATM IV (dE/dsig_post = 2 T_post sig_post = 0.147 per unit of vol; dE/dsig_pre = -0.119). The smile fit RMSE is 0.5-0.7 vol points and the 170-strike call and put disagree by 2.5 points, so the pair carries about plus or minus 1 pt of event sd on its own; the LOO range 8.0-10.1 on the five-expiry LS says the same. The 9.5% is labelled JUDGEMENT, which is right; the expected-absolute-move 7.6% is derived from it and should carry the same label (it does in B_headline).

Fix. Quote the central reading as 9.5% with a range of 8.5-10.5 (or the identified 8.3-11.0), not as a point. No change to the conclusion.

### 8. MINOR. Duplicate specification rows and small labelling issues

File and location: `B_event_variance.csv` rows `LS_to_Jan27_one_print_max` and `LS_pre_plus_single_print_expiries` (identical: same five maturities, same result); note section 1 reading paragraph; note section 3.3; note section 5 last paragraph.

What is wrong. (a) The two LS rows are the same regression under two names. (b) The reading paragraph in section 1 mixes MEASURED facts with JUDGEMENT sentences that are not labelled: "The print is priced at its own history, not above it", "the market is paying its usual premium for downside, not an unusual one", and in 3.3 "This is the measure comparable with today's reading" (the 45-day kink). (c) The 12M IV percentile (about the 40th of ABNB's own history) compares own-method IV with Bloomberg's series; on 4 Sep the own method read 0.4-0.8 pt above Bloomberg's 12M (38.3-38.7 vs 37.9), so the percentile is approximate. (d) The IV-crush formula assumes the whole 30D IV drop on the reaction day is event variance and that the constant-maturity window is exactly 30 days; both are stated conventions, fine, but the resulting 10.5% is an upper-bound style measure and the note should say so where it is compared with the 8.5% kink measure.

Fix. Drop one LS row; add the labels; add "approximate" to the percentile; one sentence on the crush measure.

## What the synthesis should and should not use

Use, with these labels:

| Item | Value | Label |
|---|---|---|
| 20 Nov $170 straddle | 13.5% of spot, mid of a 12.0-15.0 market; a 70-day total, not the print move | MEASURED |
| Implied 5 Nov event sd | 9.5%, range 8.5-10.5 (identified specs 8.3-11.0); expected absolute move 7.6% | JUDGEMENT on MEASURED inputs |
| 25-delta risk reversal, 20 Nov | -3.5 vol pts (puts richer); ordinary for ABNB | MEASURED; "ordinary" is JUDGEMENT |
| 12-month price band | lognormal p25 / p50 / p75 $126 / $164 / $214 headline; skew RND $124 / $167 / $217 as sensitivity; both risk-neutral | MEASURED |
| 12-month risk-neutral P(above $179.5) | 0.41-0.43; P(below $150) 0.40-0.41 | MEASURED, risk-neutral |
| Realised base rate, raw close-to-close, 23 prints | rms 8.9%, mean abs 7.1%, median 6.9%, 48% at 7%+, 35% at 10%+, 13 up / 10 down | MEASURED (after fix 1) |
| Same, QQQ-excess | rms 8.5%, mean abs 6.8%, median 5.1%, 11 up / 12 down | MEASURED |
| Conditional split, nights accelerated vs decelerated (n 8 / 11, threshold 0) | raw 6 up / 2 down vs 3 up / 8 down; excess 6 / 2 vs 1 / 10 | MEASURED, base rate not model |
| Historical implied event sd, Bloomberg | crush 10.5% mean, kink at 45 days 8.5% mean; realised raw rms 8.9% (ratio 0.85), excess 8.5% (0.81) | MEASURED |

Do not use:

1. Any P(above X) or P(below X) as a real-world probability. They are risk-neutral. An equity premium of about 5% shifts the one-year median up by roughly $8 and a variance risk premium narrows the band; neither is estimated here. The band width is the usable object, not the level of a tail probability.
2. The one-year median below spot ($164-167 vs $170.19) as a bearish signal; it is the risk-neutral drift (4% carry less half of 39.5% squared).
3. The 0.85 x straddle "11.5%" as the print move; it is the 70-day upper bound.
4. The skew RND's p5, p10, p90, p95; they are extrapolated beyond the quoted strikes.
5. The "1 up / 10 down" decelerating split without saying it is on QQQ-excess returns with n 11 and threshold 0 (raw 3 up / 8 down; workstream C's dead-band coding 1 up / 9 down excess, 3 up / 7 down raw).
6. "The put is 18% richer than symmetric" as evidence of a crowded hedge; the note itself says it is the usual premium.
7. Section 6's claim that the implied event variance "did not move" between 4 Sep and 11 Sep as more than approximately true; the two snapshots are 9.8 vs 9.2-9.9, inside the plus or minus 1 pt noise.

## Cross-check with workstream C on the acceleration split

B and C read the same `nights_yoy_accel_pts` column from `02_kpi_panel_quarterly.csv` (19 prints from 4Q21) and the same excess return (`legacy_1d_pct` in B equals `ret_1d_cc_excess_pct` in C). B splits at zero (> 0 accelerated, <= 0 decelerated); C uses a plus or minus 0.25 point dead band, which moves 1Q22 (+0.01, up +3.7% excess) and 3Q24 (-0.21, down -8.8%) into a "flat" bucket. On excess returns: B 6/2 and 1/10; C 5/2, 1/1 flat, 1/9. On raw returns: B 6/2 and 3/8; C 5/2, 1/1, 3/7. The two agree once the threshold is aligned; what drives the lopsided decelerating count is the excess-return choice (two raw up days of +0.7% and +1.0% become down days after subtracting QQQ) rather than the threshold. Threshold sensitivity on excess returns: at 0.5 and 1.0 points the decelerated bucket is 1 up of 9 and 1 up of 7.

## Method notes for the record

Event variance: E = T_post (sigma_post^2 - sigma_pre^2) is the right expression for one pre-print and one post-print expiry under a constant background; the brief's T_after sigma_after^2 - T_before sigma_before^2 is the forward variance between the two expiries and includes 35 days of diffusion (0.0093 of the 0.0190), so it would have given 13.8% and the agent was right to correct it. The two-post-print pair (20 Nov, 18 Dec) is identified by two equations in b and E and gives b 33.4%, E 8.3% sd; the five-expiry LS gives b 32.7%, 9.2%; the eleven-expiry sloped-background LS gives 9.7%. All reproduced independently from `B_term_structure.csv`.

Black-76 inversion: mid prices on the parity-median forward at r = 4.0% continuous, T in calendar days / 365 to 16:00 ET. Repricing each mid at the solved IV returns the mid to three decimals. The yfinance `impliedVolatility` column sits 1.91 vol points above the own IV with sd 3.53 on the 197 usable quotes, as the note says.

Skew: the 25-delta strikes in `B_skew.csv` have Black-76 deltas of exactly -0.25 and +0.25 at their smile IVs; the smile fit coefficients (0.3842, -0.1589, 0.2683) reproduce from the 12 usable 20 Nov quotes; raw-quote IVs at 155P / 195C (41.1 / 37.9) give the same -3.3 to -3.5 risk reversal without the fit.

Bloomberg: workbook opened read-only from the main tree (`C:/Users/krish/citadel-abnb/data/raw/theo_onedrive/AIRBNB DATA/`, gitignored). No workbook cell was modified. The three February prints (15 Feb 2022, 14 Feb 2023, 13 Feb 2024) fall one day before the March straddle's entry date and are correctly counted in the February straddle, not March; the print-month count of 23 is right.
