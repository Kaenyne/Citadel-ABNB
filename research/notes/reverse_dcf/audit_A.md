# Audit of workstream A (joint solve): verdict and findings

Auditor run 12-13 Sep 2026, branch `krish/reverse-dcf`, worktree `citadel-abnb-reversedcf`. Scope: `research/notes/reverse_dcf/A_joint-solve.md`, `analysis/src/reverse_dcf/A_common.py`, `A_01_multiple_regressions.py`, `A_02_market_implied_solves.py`, `A_03_decomposition_comparison.py`, the 23 CSVs under `data/processed/reverse_dcf/A/`. Findings CSV: `data/processed/reverse_dcf/audit/audit_A_findings.csv`. Nothing outside those two audit paths was written; the A scripts were re-run in place and produced byte-identical CSVs.

## Verdict: PASS WITH FIXES

No blockers. The code is correct, every output reproduces exactly, the quadratic has a unique in-range root and is monotone in price, the simple holds, the reverse DCF, the decomposition identity and the consensus reconciliation all check by hand. Four material findings, all about how the headline is stated rather than how it is computed: (1) the "band" in the headline table omits the level uncertainty of the fitted line and so collapses to nothing at the mean target; (2) the FY27 point (11.5%) hides a mapping range (10.4 to 11.5% at the price) and the direct FY27 basis in the CSV is a mis-specification rather than a third mapping; (3) the headline is in guide-proxy units, which the note itself measures as 1.4pp too high, and does not carry the realised-units reading alongside; (4) the tail figures (FY27 +7% at $150, +21% at $220, nights 4.7% and 18.4%) are a compound of slope, mapping and a fixed-base growth convention and should be labelled JUDGEMENT and quoted as ranges. Seven minor findings.

Recommended primary for the synthesis: joint solve, spec A, on its native NTM basis (MEASURED: NTM revenue growth 12.9% in proxy units, implied EV/NTM EBITDA 17.7x), mapped to FY27 as a range from the two legitimate mappings (proportional and chained through the Street's 2H26), with the fitted-line band, not the slope-rotation band. At $170.19 quote: FY27 revenue $15.7 to 15.9bn (+10.4 to +11.5% on the delivered FY26 base; NTM +12.9%, 1 s.e. band 11.5 to 14.3), EBITDA $5.69 to 5.75bn, EV/FY27 EBITDA 16.0 to 16.2x, nights +8 to +9%; in realised-growth units about a point lower (FY27 +9.5 to +10.5%), which puts the price on the Street rather than the team base.

## 1. Reproduction (task 1)

MEASURED. Copied the 23 CSVs, re-ran `A_01`, `A_02`, `A_03` in order with `py -3.13` from the worktree root (exit 0 each), and compared byte for byte: all 23 identical. Headline numbers as claimed:

| Item | Claimed | Reproduced |
|---|---|---|
| $170.19: NTM growth / FY27 proportional / EBITDA / nights / EV/FY27 EBITDA | 12.9% / 11.5% / $5,745m / 8.9% / 16.0x | 12.93 / 11.51 / 5,744 / 8.92 / 16.02 |
| $150 / $220 FY27 proportional | 7.2% / 21.2% | 7.20 / 21.24 |
| Case-implied prices Literal / Street / Team / Delivered / Ambition | $162 / 166 / 168 / 175 / 203 | 162.20 / 166.02 / 167.99 / 175.49 / 202.68 |
| Reverse DCF at $170.19, reported / SBC-adjusted | 4.61% / 15.95% | 4.61 / 15.95 |

## 2. The regression (task 2)

MEASURED, independent re-estimation from `12_abnb_multiples_monthly.csv` (own OLS with Bartlett Newey-West, 6 lags; cross-checked with statsmodels HAC):

| Spec | A's claim | Auditor |
|---|---|---|
| EV/NTM EBITDA on ntm_growth_proxy_pct, Jan 2023 to Sep 2026 | slope 0.3955, intercept 12.533, t 3.06, R2 0.23, DW 0.53, n 45 | 0.3955, 12.533, t 3.06 (non-robust t 3.63), R2 0.234, DW 0.53, n 45; residual s.d. 2.95 turns; sample means 14.65% and 18.33x |
| 12-month changes | +0.072, t 1.30 | +0.0722, t 1.30 (NW 12), R2 0.06 |
| 2024-26 levels | +0.14, t 0.6 | +0.1388, t 0.60, n 33 |
| Rolling 24-month slope | -0.18 to +0.94 | -0.177 (window ending Jun 2026) to +0.938 (window ending Jan 2026; Dec 2025 is 0.929) |
| WS12 headline spec: EV/LTM EBITDA on LTM growth | +0.333, R2 0.59 | +0.3327, intercept 15.099, R2 0.590 |

How the proxy is built (`analysis/src/overnight/12_abnb_multiples_history.py`, lines 139-167): NTM revenue = next-quarter guide midpoint x (1 + trailing four-print mean beat cushion), with the guide-implied y/y growth applied to quarters q+2 to q+4; NTM EBITDA = that revenue x LTM margin. So it is guide-based, not consensus (WS12 caveat C2), and the multiple's denominator carries the LTM margin. A's realised comparison (`A_ntm_proxy_vs_realised.csv`) is computed correctly: for the 12 vintages 3Q22 to 2Q25 the proxy exceeds realised NTM growth by 1.37pp on average (RMSE 2.90, range -2.9 to +4.8); the sign flips in 2025 (understates by 1 to 3pp) after overstating by 1.5 to 4.8pp in 2022-24, so the bias is not stable either.

Which specification is right for a forward-looking solve. The solve needs the multiple as a function of the growth that is being solved for, on the same EBITDA the multiple divides. WS12's headline +0.48 (R2 0.59 without controls, 0.68 with) is EV/LTM EBITDA on LTM growth: both sides are trailing, so it describes how the market has priced the last four quarters and cannot be inverted for forward growth without a further assumption that NTM growth equals LTM growth. A's primary (EV/NTM EBITDA on the NTM proxy, R2 0.23) is the correct pairing for the question asked, and its lower R2 is the honest cost: the forward multiple explains less because the denominator already absorbs the guide. Does the choice change the answer? Not materially at the price: `A_regression_specs.csv` shows the WS12 headline spec would put NTM growth at 9.4% (direct basis 5.5%) but that inversion is not meaningful (LTM growth today is 13.6% and is known); the forward specs A to E span 11.9 to 13.7% NTM at $170.19, and the answer is pinned near the sample mean regardless of slope. The choice matters at the tails (see section 4).

## 3. The three FY27 mappings (task 3)

The regression identifies g_NTM on the LTM base ($13,159m) with the LTM margin (35.09%), exactly the panel's construction. Hand solve at $170.19: EV = 170.19 x 597.0 - 9,593 = 92,010; (12.533 + 0.3955 g)(1 + g/100) x 4,617 = 92,010 gives 0.003955 g^2 + 0.5208 g - 7.396 = 0, g = 12.93 (the other root is -144.6). NTM revenue $14,860m, NTM EBITDA $5,214m, multiple 17.65x. That is the only MEASURED number in the headline. Everything in FY27 terms is a JUDGEMENT about the quarterly path:

| Mapping | What it assumes | $150 | $170.19 | $220 | Verdict |
|---|---|---|---|---|---|
| Proportional (A's primary) | FY27 level scaled by implied NTM / Delivered NTM; growth quoted on the fixed Delivered FY26 base $14,231m | 7.2 | 11.5 | 21.2 | Legitimate as a level; the fixed base makes the growth rate a level index, not a growth expectation |
| Proportional, base-consistent (auditor) | same scaling applied to 2H26 as well, so the FY26 base moves | 10.2 | 12.1 | 16.2 | The growth rate the market would actually expect for FY27 under the same scaling; compresses the tails |
| Chained through Street 2H26 | 2H26 fixed at $7,921m, 1H27 absorbs the whole gap, 2H27 grows at the 1H27 rate | 1.4 | 10.4 | 30.8 | Legitimate if the brief's anchored quarters are taken as given; extreme at the tails by construction |
| Direct FY27 basis | NTM-fitted multiple applied to FY27 EBITDA at 36.2% | 5.5 | 9.5 | 18.7 | Not legitimate |

Hand recompute of the direct solve at $170.19: (12.533 + 0.3955 g) x 14,231 x (1 + g/100) x 0.362 = 92,010 gives 0.003955 g^2 + 0.5208 g - 5.328 = 0, g = 9.54. It differs from the NTM solve for two mechanical reasons: FY27 EBITDA at any g is 11.6% larger than NTM EBITDA at the same g (base 14,231 x 0.362 = 5,152 vs 13,159 x 0.351 = 4,617), so a multiple fitted to NTM EBITDA applied to FY27 EBITDA over-values EBITDA and forces g down by about 2pp; and 36.2% is not the 35.1% LTM margin the multiple was fitted with. An EV/FY27 multiple observed in Sep 2026 would sit roughly 1.4 turns below the EV/NTM multiple (the NTM to FY27 EBITDA growth), and the direct solve does not roll the intercept down. It is a mis-specification, not a third mapping; it should be dropped from the range or footnoted as such. The task's suggested range "9.5 to 11.5" therefore over-widens on the low side; the defensible range at the price is 10.4 to 11.5% on the fixed base (10.0 if the Delivered 2H26 chain is included), or 10.4 to 12.1% if the base-consistent proportional is admitted.

Should the headline be a range? Yes. At the price the two legitimate mappings differ by 1.1pp, the same size as the whole gap between the team base and the Delivered case, so a point estimate over-states precision. Quote NTM 12.9% as the measured number and FY27 as "$15.7 to 15.9bn, +10.4 to +11.5%".

## 4. Joint-solve mechanics and the band (tasks 4 and 5)

Mechanics. (a + b g)(1 + g/100) R m = EV is a quadratic in g with roots at g = -a/b (-31.7 for spec A) and g = -100; its vertex is at g = -65.8, so for every g above -31.7 the left side is strictly increasing in g and there is exactly one root; EV is increasing in price, so the root is monotone in price. Verified for all eight specs (`A_joint_solve_checks.csv` monotone_in_price True) and by closed-form solution at $150, $170.19, $179.50, $220 (NTM 8.62 / 12.93 / 14.84 / 22.66, second roots -140 to -154, matching the bisection to two decimals). The bisection bracket [-50, 100] contains only the relevant root for every spec.

The band. The note's "slope +/- 1 s.e." band rotates the line about the sample means (14.65%, 18.33x), so it carries only the slope's uncertainty and none of the level's. At $179.50 the solve lands at g 14.84 and M 18.40, i.e. on the pivot, so all three lines pass through the same point and the band is 13.4 to 13.5 by construction. It is an artefact, not a coding error, but it is an error of omission: the variance of the fitted multiple at g is var(a) + g^2 var(b) + 2g cov(a, b), which at the mean equals the variance of the mean multiple and is far from zero with DW 0.53. Recomputed with the Newey-West covariance (delta method, then inverted through the solve):

| Price | NTM point | Note's band (slope only) | Fitted-line 1 s.e. band, NTM | Same, FY27 proportional | Note's FY27 band | +/- 1 residual s.d. (2.95 turns), NTM |
|---|---|---|---|---|---|---|
| $150 | 8.6 | 6.8 to 9.8 | 7.3 to 10.0 | 5.8 to 8.6 | 5.3 to 8.4 | 3.3 to 14.1 |
| $165 | 11.8 | 11.0 to 12.4 | 10.5 to 13.2 | 9.1 to 11.8 | 9.6 to 11.0 | 6.5 to 17.3 |
| $170.19 | 12.9 | 12.4 to 13.3 | 11.5 to 14.3 | 10.1 to 12.9 | 11.0 to 11.8 | 7.7 to 18.4 |
| $179.50 | 14.8 | 14.8 to 14.9 | 13.2 to 16.5 | 11.8 to 15.1 | 13.4 to 13.5 | 9.6 to 20.2 |
| $185 | 15.9 | 15.7 to 16.3 | 14.2 to 17.8 | 12.7 to 16.3 | 14.3 to 14.9 | 10.7 to 21.3 |
| $197.50 | 18.4 | 17.7 to 19.5 | 16.2 to 20.7 | 14.8 to 19.2 | 16.3 to 18.1 | 13.2 to 23.7 |
| $220 | 22.7 | 21.2 to 25.0 | 19.6 to 25.7 | 18.2 to 24.3 | 19.8 to 23.6 | 17.6 to 27.9 |

The fitted-line s.e. is 0.74 to 1.74 turns across the tape (0.78 at the price), against the note's effective zero at $179.50. The residual s.d. column is the different question (where the market sits relative to the line, which is what spec F is about) and is 5pp either side at every price; it is the honest statement of how much the regression can say about growth from the price alone. Fix: replace the band column with the fitted-line band (a three-line change in `A_02`: compute se_fit = sqrt(x' V x) at the solved g and re-solve with the intercept shifted +/- se_fit), and quote the residual s.d. once in the caveats.

## 5. Simple holds, reverse DCF, decomposition, consensus (tasks 6 to 9)

Simple holds (`A_simple_holds_grid.csv`), three cells by hand: 16.5x at $150: EV 79,957 / 16.5 / 0.362 = 13,387, -5.93% on 14,231 (grid -5.9). 16.5x at $220: 121,747 / 16.5 / 0.362 = 20,384, +43.2% (grid 43.2). 16.5x at $170.19: 92,010 / 16.5 / 0.362 = 15,404, +8.24% (grid 8.2). P/E 27x at $170.19 through the Delivered P&L: EPS 6.30, revenue (6.30 x 577.05 / 0.82 - 516 + 1,936) / 0.3555 = 16,471, +15.7% (grid 15.7). All correct.

Reverse DCF. `A_common.fade_dcf` is textually identical to `mgmt_implied_model.fade_dcf` (mid-year discounting from 30 Sep 2026, linear fade FY28 to FY36, Gordon terminal). At $170.19, WACC 10%, terminal 3%: 4.61% reported / 15.95% SBC-adjusted (note: 4.6 / 16.0); Literal 5.60, Ambition 2.74. Across the tape on reported FCF: 0.65% at $150 to 12.63% at $220. Correct.

Decomposition history (`A_decomposition_history_check.csv` vs `02_kpi_panel_quarterly.csv`). Exact identity residual (nights x reported ADR x take rate) mean absolute 0.17pp; management-decomposition residual matches the panel quarter by quarter (3Q24 -0.72, 4Q24 -2.46, 2Q25 +3.76, 3Q25 -1.12, 4Q25 -1.97, 1Q26 +0.81, 2Q26 -2.38; trailing four -1.16, s.d. 2.69). Implied nights at $170.19: ln(1.1151) - ln(1.030) - ln(0.994) = 0.0854, nights +8.92%. FX sign: `fx_pts_revenue` in the panel is positive for a tailwind (1Q26 +3.0, 2Q26 +4.0) and `FX_FY27_PP = -0.6` is the WS29 consensus-EUR headwind (revenue-weighted -1.0 / -0.8 / -0.6 / -0.1 across FY27), so nights = revenue - ADR - FX = 11.5 - 3.0 + 0.6 arithmetically, consistent. ADR +2 / +4 gives 9.98 / 7.87, one point of ADR is one point of nights. Correct.

Consensus reconciliation. 148.9 / 133.6 = +11.45% (page +11.1%): correct, and the note uses the level. 4Q26 take rate 3,177 / 23,000 = 13.813% vs 2,778 / 20,400 = 13.618%, +19.5bp: "up 20bp" is correct (the 4Q25 GBV is rounded to $0.1bn, so the baseline is good to about 3bp). Residual +1.47pp at the Street's nights 10.09%, ADR ex-FX 2.77%, FX -0.4: correct. Quarterly sum 6,286 + 4,744 + 3,177 = 14,207 vs 14,100 to 14,160 (+47 to +107) and Zacks 6,286 + 4,740 + 3,200 = 14,226 vs 14,100 (+126): "$50-126m" is correct. The team's 4Q26 residual (-0.5) placed under the Street's nights and ADR gives 2,778 x exp(0.0961 + 0.0273 - 0.0040 - 0.0050) = $3,115m, correct. One label problem: the "-1.5" residual shown for the team's 3Q26 in the 4.2 table is WS29's guide-implied residual (nights 11.0, ADR 3.0, revenue at the guide midpoint, `29_bridge_assumptions.csv`), not the team base's own 3Q26 (nights 9.9, $4,771m), which is about -0.5pp at ADR ex-FX 3.5; the number is not in any A CSV.

## 6. The headline claims (task 10)

| Claim | Verdict | Reason |
|---|---|---|
| (i) The joint solve is usable as primary at and near the price but not in the tails | Partly supported | The point at the price is stable to slope choice only because $170.19 sits near the sample pivot (implied 17.7x at 12.9% vs means 18.3x at 14.7%). The level uncertainty the note omits is +/- 1.4pp at 1 s.e. (fitted line) and the residual scatter is +/- 5pp; the regression cannot separate "12.9% on the line" from "17.8% guide, 4 to 6 turns below the line", which is where the multiple sat from Feb to Jul 2026. The note's own 2.5 argument that "methods 1 and 2 agree at the price" is that the implied 16.0x is inside the team's 13.5 / 16.5 / 18.5x band, not that the growth agrees: the hold at the team's mid 16.5x gives 8.2%. Usable at the price with the wider band and the mapping range; not usable in the tails, as the note says |
| (ii) The price sits on the team base / Street, about $5 below Delivered | Supported, with a units caveat | Delivered prices at $175.49 (+$5.30). On the proportional mapping the nearest case is the team base (gap 0.5pp); on the chained mapping (10.4%) and in realised-growth units (about 10.1 to 10.5%) it is the Street or slightly below. "Street to team base" is the right phrase; "team base" alone is not |
| (iii) A point of FY27 nights is worth about $4.80 a share on the joint solve vs $1.40 on a fixed multiple | Supported on the joint solve, understated on the hold | Joint solve: +/- 1pp of FY27 growth moves the price $165.40 to $175.04, $4.82 per pp of revenue, $4.93 per point of nights. Fixed multiple: 1% of FY27 revenue $159m, EBITDA $57m, at the price's 16.0x = $1.54 a share (16.5x $1.59); $1.40 corresponds to 14.5x. Also the "about 60/40" split of a price move between growth and multiple is 72 / 28 multiple / EBITDA per pp of NTM growth at the price (dlnM 2.24% vs dlnEBITDA 0.89%), which strengthens rather than weakens the brief's point that nights move the multiple |
| (iv) The peer cross-section cannot solve for growth | Supported | `12_peer_regressions.csv`: b 0.021 (t 1.9, R2 0.19) and 0.033 (t 4.9, R2 0.35) in logs; the no-premium solve returns 21.6% / 18.2% NTM at $170.19 and 16.8% / 14.8% at $150, above every case; with the premium held it is circular. Correctly set aside |

## 7. Recommendation for the synthesis (task 11)

Primary method: joint solve, spec A (EV/NTM EBITDA on the NTM proxy, 2023-26 levels), on its native NTM basis, with the fixed-multiple hold at 16.5x reported as the cross-check at the price only. Do not use the WS12 LTM specification in the solve. Drop the direct FY27 basis from the CSV and the note, or keep it with the label "mis-specified, shown to explain the 2pp gap".

FY27 mapping: quote a range, proportional (11.5% at the price) to chained through the Street's 2H26 (10.4%), and state that growth rates are on the fixed Delivered FY26 base of $14,231m, which is a level index; give the FY27 revenue level as the headline quantity ($15.7 to 15.9bn at $170.19). At the tails, quote NTM growth with the fitted-line band as the number, and FY27 and nights as JUDGEMENT ranges (at $150: FY27 +5.8 to +10.2%, nights about +3.5 to +7.5%; at $220: FY27 +16.2 to +24.3%, nights about +13 to +21%).

What to quote at $170.19:

| Quantity | Label | Value |
|---|---|---|
| NTM revenue growth, guide-proxy units | MEASURED | 12.9% (1 s.e. fitted-line band 11.5 to 14.3; residual s.d. band 7.7 to 18.4) |
| Same, realised-growth units | MEASURED adjustment, JUDGEMENT to apply | about 11.5% (proxy bias +1.4pp, RMSE 2.9, n 12) |
| Implied EV / NTM EBITDA | MEASURED | 17.7x (panel convention, LTM margin) |
| FY27 revenue | JUDGEMENT on MEASURED | $15.7 to 15.9bn, +10.4 to +11.5% on the Delivered FY26 base (+12.1% base-consistent); about +9.5 to +10.5% in realised units |
| FY27 adj. EBITDA at 36.2% | JUDGEMENT | $5.69 to 5.75bn; EV/FY27 EBITDA 16.0 to 16.2x |
| FY27 nights, ADR ex-FX +3, FX -0.6, residual 0 | JUDGEMENT | +8 to +9% (7.9 to 8.9 across the mappings; +/- 1 for each point of ADR; +1.2 if the residual stays at its trailing mean) |
| Nearest case | JUDGEMENT | Street to team base; Delivered is $5 above |

Re-labelling: the headline table (section 1) and sections 3.1, 4.3 and 5 present the FY27 growth, EPS, nights and "nearest case" columns as MEASURED; they are JUDGEMENT on a MEASURED NTM solve because they depend on the mapping, the base convention, the 36.2% margin and the decomposition assumptions. Only the NTM growth, the implied NTM multiple and the case-implied prices under the stated mapping are MEASURED.

## 8. Findings

Severity: blocker (wrong answer or unreproducible), material (changes what the synthesis should quote), minor (label or precision).

| # | Severity | File | Location | What is wrong | Fix |
|---|---|---|---|---|---|
| 1 | material | A_02_market_implied_solves.py; A_joint-solve.md | specs A-low / A-high (rotation about sample means); headline table "Band" column; sections 1, 2.5, 4.3, 7.1 | The band carries slope uncertainty only; the level (intercept) uncertainty is omitted, so the band collapses to 13.4 to 13.5 at $179.50 and reads 11.0 to 11.8 at the price when the fitted-line 1 s.e. band is 10.1 to 12.9 (NTM 11.5 to 14.3) | Compute se_fit = sqrt(x' V x) from the Newey-West covariance at the solved g and re-solve with the intercept shifted +/- se_fit; replace the column; quote the residual s.d. (2.95 turns, +/- 5pp) once in the caveats |
| 2 | material | A_joint-solve.md; A_joint_solve.csv | section 1 headline (11.5% point); section 3.1; column fy27_growth_direct_fy27_basis_pct | The FY27 point hides a 1.1pp mapping range at the price (10.4 chained vs 11.5 proportional; 12.1 on a base-consistent proportional); the "direct FY27 basis" is a mis-specification (NTM-fitted multiple applied to an FY27 EBITDA 11.6% larger at the same g, at a margin the line was not fitted on), not a mapping | Headline FY27 as a range "$15.7 to 15.9bn, +10.4 to +11.5%" with NTM 12.9% as the measured number; drop or relabel the direct column; state that growth is quoted on a fixed base and is a level index |
| 3 | material | A_joint-solve.md | section 1 headline; section 5 "nearest case"; A_nearest_case_by_price.csv | Headline growth is in guide-proxy units, which the note measures as 1.4pp above realised; the realised-units reading (FY27 about 9.5 to 10.5%) moves the nearest case from team base to Street and is confined to 2.3 and caveat 2 | Carry the realised-units figure in the headline table as a second row or column at every price; say "Street to team base" at $170.19 |
| 4 | material | A_joint-solve.md; A_headline.csv; A_implied_nights.csv | tails ($150, $220 rows): FY27 growth, EBITDA, EPS, nights, "nearest case" | Tail figures compound slope uncertainty, the mapping choice (1.4 vs 7.2 vs 10.2 at $150; 16.2 vs 21.2 vs 30.8 at $220) and the fixed-base convention, and are labelled MEASURED | Label the tail FY27 and nights figures JUDGEMENT; quote as ranges (FY27 $150: 5.8 to 10.2; $220: 16.2 to 24.3); keep NTM growth with the fitted-line band as the measured tail number |
| 5 | minor | A_joint-solve.md | section 4.3 cross-check paragraph; section 1 "Third" | "$1.40 a share on a fixed 16x multiple" is $1.54 at the price's 16.0x ($1.59 at 16.5x); $1.40 corresponds to 14.5x | Correct to about $1.50 |
| 6 | minor | A_joint-solve.md | section 1 "First" ("about 60/40 at the price") | Per pp of NTM growth at the price the EV move is 72% multiple (dlnM 2.24%) and 28% EBITDA (0.89%); "60/40" is neither direction | State "about 70/30 multiple to EBITDA" |
| 7 | minor | A_01_multiple_regressions.py; A_regression_specs.csv; A_joint-solve.md | window_note "first diff available Nov 2023"; section 2.1 table rows "12m changes ... Nov 2023 to Sep 2026" | The EV/NTM EBITDA series starts Nov 2021, so the 12-month-change sample is Jan 2023 to Sep 2026 (n 45), not Nov 2023 | Correct the label |
| 8 | minor | A_joint-solve.md | section 2.1 point 3; caveat 1 | Rolling 24-month maximum +0.94 is the window ending Jan 2026 (Dec 2025 is +0.93) | Correct the date |
| 9 | minor | A_regression_specs.csv; A_regression_loo.csv; A_regression_rolling.csv | column implied_fy27_growth_at_170.19_pct (9.54 for the primary spec) | The column is the direct FY27-basis solve, inconsistent with the note's proportional headline (11.51); a reader of the CSV sees a different FY27 number for the same spec | Rename to implied_fy27_growth_direct_basis_pct or compute the proportional mapping |
| 10 | minor | A_joint-solve.md | section 4.2 table, "Residual" row, "3Q26 Delivered / Team" cell (-1.1 / -1.5) | -1.5 is WS29's guide-implied residual (nights 11.0, ADR 3.0, guide midpoint, 29_bridge_assumptions.csv), not the team base's 3Q26 (nights 9.9, $4,771m), which is about -0.5 at ADR ex-FX 3.5; not in any A CSV | Relabel or recompute from the team's 3Q26 inputs and add to A_quarterly_consensus_decomposition.csv |
| 11 | minor | A_common.py; A_03_decomposition_comparison.py | Q3_25_TAKE uses 3Q25 GBV 22,892 (management model) while the history check uses the panel's 22,900 | 1bp difference in the 3Q25 take-rate baseline; immaterial | Note the source once |

## 9. What was verified and found correct (no finding)

Quadratic uniqueness and monotonicity (all specs, closed form); the eight-spec solve table; LOO ranges (NTM 12.5 to 13.4 by block, 12.7 to 13.2 by month; slopes 0.33 to 0.47 / 0.37 to 0.43); expanding-window slope 0.40 to 0.57 since mid-2025; residuals Feb to Jul 2026 -3.7 to -5.9 turns and Aug-Sep -1.2 / -1.4; spec F intercept 9.671; spec B intercept 11.130 at the LTM margin; simple-holds grid; the $146 / $174 / $193 mapping of 13.5 / 16.5 / 18.5x on the Street's FY27; the one-turn end-FY27 convention gap; reverse DCF and its sensitivities; the annual identity residuals (FY24 -0.2, FY25 0.0, 1H26 -0.9); the Street 3Q26 take rate +12bp and residual -2.0; the FY26 component sums (587.6m nights, $105.75bn GBV, ADR $179.97, take rate 13.435%); Street FY27 EPS needing $16,029m or 36.8% margin; GAAP EPS $6.00 at the price through the Delivered P&L; the elasticity anchor consistency ($4.82 per pp vs WS12's $9.11 per turn); the peer cross-section coefficients and solves; team bear / bull revenue $14,318m / $16,910m (29_fy27_bridge.csv).
