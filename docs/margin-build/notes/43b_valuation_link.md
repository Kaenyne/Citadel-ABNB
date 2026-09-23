# 43b. How the cost leg enters the target price, in dollars per share

Claude (Fable 5.1) for Krish, 22 Sep 2026, branch `krish/cost-leg`. Script `analysis/src/margin_build/43b_valuation_link/run.py`
(`py -3.13 -X utf8`, exit 0, ~5 s), outputs `data/processed/margin_build/43b_valuation_link/`. Reads only. Spot $166.84 (21 Sep close,
per the brief; DEC-0015 leaves the memo's $167.51 provisional), 597.0m diluted shares, $9,593m net cash ex float (the reverse-DCF
run's spot convention). **No discounting anywhere**: every price is FY27 adj. EBITDA x multiple + net cash, over shares, which is the
convention the joint solve, the memo's $143 and Jessie's Monte Carlo all use. Nothing is fitted here (parameter count at the end).

## Bottom line

1. **$143 contains no cost view.** It is the reverse-DCF joint solve (workstream A, spec A: EV / NTM EBITDA = 12.533 + 0.3955 x NTM
   growth, LTM revenue $13,159m, LTM margin **35.1% held fixed**) inverted at NTM growth of 7.1% (the memo's "~7.5%" gives $144.9;
   7.0% gives $142.7). $150 is 8.6% (reproduced exactly), $148 is 8.2%, $138 is 5.9%, $125 is 2.9% NTM. Margin does not enter the
   joint solve (WS12/A: margin coefficient on the multiple t 0.4). The official v2 model reaches the same number by a different route:
   its FY27 EBITDA $5,240m at the multiple the market pays today for the Street's FY27 (15.61x) less DEC-0014's half turn per point of the
   2.2pp growth gap (14.53x) is **$143.6**. That route does contain the cost leg, and it is the one the memo should cite.
2. **Of the $23 a share from $166.84 to $143.6, thesis 3 is $5.8 (25%)**: $2.4 because costs do not flex down with revenue (M6) and
   $3.4 because the line build's FY27 cost growth (+11.1%) exceeds the Street's (+10.0%). Revenue below the Street with costs flexing is
   $7.9 (34%) and multiple compression on lower growth is $9.5 (41%). On the FY24-25 cost-growth path (+12.6%) the target is $140 and
   thesis 3 is $9.5 (36%); on a repeat of FY26's +15% it is $135 and $15.3 (48%). On the workbook's own flex convention (memo rows 43-44,
   costs held to the line build's margin) the non-flex leg is $6.6 instead of $2.4 and thesis 3 is $10.0 (43%).
3. **Jessie's Monte Carlo argues for a long at today's price.** Replicated (median $175.7, P5 $146.3, P95 $203.9, P(> $181.94) 0.374
   vs her 0.368), it gives **P(price > $166.84) = 0.68** and a median 5% above spot. Its growth PERT is centred on the old +11.3% base,
   its multiple PERT (13.5/16.5/18.5x, mean 16.2x) sits above the 15.6x the market pays for the Street's EBITDA, and nothing links the
   multiple to growth, so bull growth draws are not paid for and bear draws are not punished.
4. **The corrected Monte Carlo** (margin = 1 - costs / revenue; cost growth PERT 8.7 / 11.1 / 15.0% with revenue elasticity k = 0.36
   +/- 0.06; revenue growth PERT 5.5 / 9.3 / 15.1%; multiple spot-anchored at the Street's growth with slope 0.49 +/- 0.09; 20,000 draws,
   seed 2026, second seed within $0.2) gives **median $145.1, P5 $126.2, P95 $168.5, P(< $166.84) 0.94, P(< $143) 0.44**; median margin
   34.0%, median multiple 14.7x. With 1.5 turns of residual multiple noise: P5 $116.5, P95 $177.1, P(< spot) 0.87. The distribution
   supports a short with a target at its median, $143-145, **conditional on the team's revenue view**: the revenue thesis alone (costs at
   the Street's +10.0%) gives a $148 median and P(< spot) 0.90; the cost leg alone at the Street's revenue gives $164 (P(< spot) 0.84;
   $161 if centred on history). Thesis 3 moves the median $3, the bridge $6-15.
5. **A reverse DCF cannot see the cost leg.** On the repo's `fade_dcf` at Street growth the constant margin the price implies is
   24.6-34.7% on reported FCF and 36.5-46.6% SBC-adjusted (WACC 9-11%, terminal 2.5-3%): the SBC treatment (12pp) and each WACC point
   (4pp) swamp the 1-3pp between the cost paths. On the multiple lens, DEC-0014's literal line at Street growth (16.1x) says the price
   already implies FY27 EBITDA $5,584m, margin 35.3%, cost growth 12.0%: about one point of the cost leg is in the price on that reading,
   none on the spot-anchored reading. The target rests on the EV/EBITDA lens, and the memo should say so.

Wording caveat for the memo: Point 3 says S&M. The repo's FY27 cost excess over the Street is in cost of revenue (+$101m, hosting), not
opex (+$30m) (`41_cost_leg.md`), and there is no Street S&M consensus to compare against. S&M cash does grow 13.8% in the line build
against 11.1% for total costs, and M6's asymmetry (k_up 1.83 vs k_dn -0.12) is an S&M finding, so "the cost base does not flex" is
defensible; "S&M dropping slower than the market models" is not measured anywhere in the repo.

## 1. Where the targets come from (`43b_target_trace.csv`, `43b_target_checks.csv`)

| price | memo label | joint-solve NTM growth | EV/NTM EBITDA | FY27 growth (proportional) | x Street FY27 EBITDA | x official v2 | x 40 short case |
|---|---|---|---|---|---|---|---|
| $170.19 | A's price, 11 Sep | 12.9% | 17.7x | 11.5% | 16.0x | 17.6x | 19.3x |
| $166.84 | spot | 12.2% | 17.4x | 10.8% | 15.6x | 17.2x | 18.9x |
| $150 | base range top | 8.6% | 15.9x | 7.2% | 13.9x | 15.3x | 16.8x |
| $148 | probability-weighted | 8.2% | 15.8x | 6.8% | 13.7x | 15.0x | 16.5x |
| $143 | base target | 7.1% | 15.3x | 5.7% | 13.1x | 14.5x | 15.9x |
| $138 | base range bottom | 5.9% | 14.9x | 4.5% | 12.6x | 13.9x | 15.3x |
| $125 | short case | 2.9% | 13.7x | 1.5% | 11.3x | 12.4x | 13.7x |

The joint solve is `A_02_market_implied_solves.py` (spec A, n 45 monthly, t 3.1, R2 0.23; `research/notes/reverse_dcf/A_joint-solve.md`).
It solves the quadratic (a + b g) x $13,159m x (1 + g) x 35.1% = P x 597.0m - $9,593m for g. The memo's "$143 at ~7.5% NTM growth;
$150 at 8.6%" is this line; $150 is exact, $143 is 7.1% (7.5% gives $144.9). The plan note (V3) records that the short-case $125 "is not in
the run and was interpolated"; it coincides with the 40 short case's EBITDA ($4,761m, 31.9%) at the spot-anchored DEC-0014 multiple for its
+7.0% growth (13.45x -> $123.3) and with that EBITDA at 13.5x ($123.7). The memo's "team bear $121-137 at 16.5x" is the 7 Sep driver
model, kill-listed for the official model (DEC-0014's 12.29/16.03/20.76x re-anchoring is of that vintage).

Reproductions: official v2 EBITDA x DEC-0014 literal (16.5 + 0.486 x (9.26 - 12.27) = 15.04x) = $148.1; x spot-anchored 14.53x = $143.6;
x 16.5x = $160.9. Street FY27 EBITDA x DEC-0014 literal at Street growth (16.12x) = $171.8; x 16.5x = $175.4.

## 2. The downside bridge (`43b_bridge_steps.csv`, `43b_bridge_summary.csv`)

Sequential, EV / FY27 adj. EBITDA, spot convention. Step 0 is the Street's FY27 (LSEG 11 Sep, n 44: revenue $15,819m, EBITDA $5,766m,
36.45%) at the multiple the price pays for it today, 15.61x, which returns $166.84 by construction. (a) moves revenue to the official v2
$15,425m (-2.49%) with costs following at M6's total-cash-cost elasticity k = 0.364 (1Q22+, n 18, t 6.6); (b) removes that flex (DEC-0022
carries cost dollars flat; M6's asymmetric fit gives k_dn -0.26, p 0.08, i.e. no measurable cut when revenue slows); (c) moves costs from the
Street's growth rate to the 41 path, on the official FY26 cost base ($9,170m, $34m above the Street's); (d) moves the multiple by
DEC-0014's slope times the growth gap (9.26% vs 11.49%, -2.22pp).

| step | FY27 EBITDA | margin | multiple | price | $/share |
|---|---|---|---|---|---|
| 0 Street FY27 at today's multiple | 5,766 | 36.45% | 15.61x | 166.84 | |
| (a) revenue below the Street, costs flexing at k 0.36 | 5,463 | 35.42% | 15.61x | 158.91 | **-7.93** |
| (b) costs do not flex | 5,371 | 34.82% | 15.61x | 156.52 | **-2.39** |
| (c) costs above the Street: line build +11.1% | 5,240 | 33.97% | 15.61x | 153.09 | **-3.43** |
| (d) multiple, 0.486 x -2.22pp | 5,240 | 33.97% | 14.53x | 143.59 | **-9.50** |

**Thesis 3 accounts for $5.8 of the $23.2 per share of downside (25%)** on the line-build path; $9.5 of $26.7 (36%) on FY24-25's +12.6%;
$15.3 of $32.0 (48%) on FY26's +15.0%; $3.4 of $21.0 (16%) if costs grow at the Street's rate (the FY26 base gap only). Slope CI 0.32-0.65
moves the target $146.9-140.3 and (d) $6.2-12.8. On the workbook's own flex convention (memo rows 43-44: EBITDA if costs held the line
build's margin, +$255m in FY27) the split of (a)+(b) is $3.8 + $6.6 and thesis 3 is $10.0 (43%). On the 40 short-case revenue ($14,914m):
target $117, thesis 3 $8.9 of $49.6 (18%; the revenue and multiple legs dominate there).

The cost leg is small in the bridge for one arithmetic reason: the official model's revenue is only 2.5% below the Street, so the flex leg
(k x 2.5% x $10bn of costs) is $90m, and the line build's cost growth is only 1.0pp above the Street's, worth $130m. Each point of FY27 cost
growth is $92m of EBITDA, 58bp of margin (41), and **$2.4 a share** at 15.6x. Each point of FY27 revenue growth is worth $1.5 through EBITDA
at fixed costs plus $4.3 through the multiple: the multiple leg is what makes the target a growth call.

## 3. Monte Carlo (`43b_mc_summary.csv`, `43b_mc_primary_marginals.csv`, `43b_mc_primary_by_bucket.csv`)

Specification, primary run (pre-stated, then run once per seed):

- FY27 revenue growth g ~ PERT(5.53, 9.26, 15.14)% on the official FY26 base $14,118m: low = 40's `rev_bear` FY27 growth, mode = official v2,
  high = 40's `rev_bull`. Median draw 9.5%, P5-P95 6.8-12.7%.
- FY27 cost growth at base revenue c ~ PERT(8.7, 11.07, 15.0)%: low = the Street's FY28 cost growth (the lowest anywhere on the tape), mode
  = line build, high = Street FY26E. The Street's +10.0% is at P20, FY24-25's +12.6% at P75.
- realised cost growth = c + k x (g - 9.26), k ~ N(0.364, 0.055) (M6 total cash costs, lag 0, 1Q22+, rw, n 18). Costs on the official FY26
  base $9,170m. Margin = 1 - costs / revenue is an output.
- multiple = 15.61 + b x (g - 11.49), b ~ N(0.486, 0.086) (DEC-0014 slope and HAC CI); no margin term (A, WS12: t 0.4); no residual.
- price = (EBITDA x multiple + $9,593m) / 597.0m. N 20,000, seeds 2026 and 20260922.

| variant | median | P5 | P95 | P(< $166.84) | P(< $143) | median margin | median multiple |
|---|---|---|---|---|---|---|---|
| **corrected: primary** | **145.1** | 126.2 | 168.5 | **0.94** | **0.44** | 34.0% | 14.7x |
| second seed | 145.0 | 125.7 | 168.2 | 0.94 | 0.45 | 33.9% | 14.7x |
| asymmetric k (k_up 0.58, k_dn 0) | 144.8 | 124.3 | 166.5 | 0.95 | 0.45 | 33.8% | 14.7x |
| + multiple residual sd 1.5 turns | 145.3 | 116.5 | 177.1 | 0.87 | 0.45 | 34.0% | 14.7x |
| cost centred on the Street (8.7/10.0/12.6) | 147.5 | 128.6 | 170.8 | 0.91 | 0.37 | 34.6% | 14.7x |
| cost centred on history (10.0/12.6/15.0) | 142.3 | 123.7 | 165.1 | 0.96 | 0.52 | 33.2% | 14.7x |
| DEC-0014 literal anchor (16.5x at 12.27%) | 149.6 | 130.1 | 173.3 | 0.88 | 0.31 | 34.0% | 15.2x |
| costs fully variable (k = 1) | 144.8 | 128.8 | 163.1 | 0.98 | 0.44 | 33.9% | 14.7x |
| growth centred on the Street (5.5/11.5/15.1) | 158.5 | 136.2 | 179.6 | 0.72 | 0.14 | 35.0% | 15.5x |
| thesis 3 alone: Street base and revenue, costs uncertain | 164.0 | 159.0 | 168.2 | 0.84 | 0.00 | 35.8% | 15.6x |
| thesis 3 alone, history-centred costs | 160.8 | 157.2 | 164.5 | 1.00 | 0.00 | 35.0% | 15.6x |
| revenue thesis alone: costs at the Street's +10.0% | 148.0 | 129.1 | 170.9 | 0.90 | 0.36 | 34.7% | 14.7x |
| revenue thesis alone, k = 1 (no cost mechanism) | 147.6 | 132.0 | 165.5 | 0.96 | 0.33 | 34.6% | 14.7x |
| **Jessie 7 Sep MC, replicated** | **175.7** | 146.3 | 203.9 | **0.32** | 0.03 | 35.2% | 16.4x |

Jessie's inputs, backed out as her script does: shares 574.6m and net cash $10,116m implied from `13_scenario_grid.csv`, FY26 base
$14,233m, growth PERT 1.78 / 11.31 / 19.92%, margin PERT 28.40 / 35.89 / 38.00%, multiple PERT 13.5 / 16.5 / 18.5x, Gaussian copula rho 0.5.
Her P(> $181.94) reproduces (0.374 vs 0.368; the R random stream is not replicated, the summary is). At $166.84 her P(price > spot) is 0.68.

Reading. The corrected distribution's centre is the official model's own number, and 94% of it sits below spot. That is not a strong
independent finding: the revenue centre (9.3%) is 2.2pp below the Street and the multiple is anchored to the Street's growth, so every
growth shortfall is charged twice, in EBITDA and in the multiple, which is DEC-0014's rule. The variants say what is doing the work: moving
the growth centre to the Street's takes the median to $158.5; removing the cost mechanism altogether (k = 1, costs at the Street's rate)
moves it only from $145 to $148. By growth bucket (primary run), every draw with FY27 growth below 11.5% prices below spot; among draws with
growth above the Street's, 46% are below spot when cost growth is below 11.1% and 70% when it is 12.6-15.0%. The cost leg decides the sign
only when the revenue call is wrong.

## 4. Reverse DCF at Street growth (`43b_reverse_dcf_implied_margin.csv`, `43b_reverse_dcf_required_growth.csv`)

The repo has no margin-solving DCF; it has A's `fade_dcf` (10-year linear fade of FY28 growth to terminal, PV at 30 Sep 2026) and the
management-implied model's per-quarter margin inputs. Used here: revenue at the Street (FY27 +11.5%, FY28 +10.9% fading to terminal), a
constant margin from FY27, FCF = EBITDA x 1.024 (delivered conversion) or less SBC $1,936m, solved for the margin that returns EV $90,010m.

| lens | implied FY27 margin | implied FY27 cost growth | note |
|---|---|---|---|
| DEC-0014 literal line, 16.12x at Street growth | 35.3% | 12.0% | between line build (11.1) and history (12.6); spot is 2.9% below the Street case |
| joint solve A at spot | 35.1% (held) | n/a | solves for growth (NTM 12.2%), not margin |
| fade DCF, reported FCF, WACC 9 / 10 / 11%, tg 3% | 24.6 / 28.8 / 33.1% | 31 / 23 / 16% | price looks cheap on reported FCF |
| fade DCF, SBC-adjusted FCF, WACC 9 / 10 / 11%, tg 3% | 36.5 / 40.8 / 45.1% | 10 / 3 / -5% | price looks rich on SBC-adjusted FCF |

Required FY28 starting FCF growth (reported FCF, tg 3%) at each cost-leg margin held from FY27: Street 36.45% needs 0.0 / 4.2 / 8.0% at WACC
9 / 10 / 11%; line build 35.7% needs 0.6 / 4.8 / 8.7%; official v2 34.0% needs 1.9 / 6.2 / 10.1%; the 40 short case 31.9% needs 3.6 / 7.9 /
11.9%, all at or below the Street's 10.9% FY28 revenue growth. Consistent with A: on reported FCF the stock is not expensive at any point on
the tape, so the DCF lens does not support the short and cannot separate the cost paths. Say the target is a multiple-lens number.

## 5. Scenario table for the memo (`43b_scenario_table.csv`, spot-anchored DEC-0014 line)

| scenario | FY27 revenue | FY27 adj. EBITDA (margin) | EV/EBITDA | $/share | vs $166.84 |
|---|---|---|---|---|---|
| Street (LSEG, n 44) | 15,819 | 5,766 (36.4%) | 15.6x | 167 | 0% |
| Street revenue, FY24-25 cost growth +12.6% | 15,819 | 5,531 (35.0%) | 15.6x | 161 | -4% |
| Official v2 base (revenue -2.5%, line-build costs +11.1%) | 15,425 | 5,240 (34.0%) | 14.5x | 144 | -14% |
| Official v2 revenue, cost growth +12.6% | 15,425 | 5,136 (33.3%) | 14.5x | 141 | -15% |
| 40 short case (costs at budget) | 14,914 | 4,761 (31.9%) | 13.5x | 123 | -26% |
| 40 both_bear | 14,948 | 4,409 (29.5%) | 12.7x | 110 | -34% |
| 40 rev_bull | 16,571 | 6,253 (37.7%) | 17.4x | 198 | +19% |

Same rows on the DEC-0014 literal line are $4-5 higher (official v2 $148); at a fixed 16.5x the official v2 is $161 and the short case $148.

## 6. Replacement valuation paragraph (proposed)

Our $143 target is the official model's FY27 (revenue $15.4bn, 2.5% below the Street; adjusted EBITDA $5.24bn, a 34.0% margin against the
Street's 36.4%) at 14.5x EV/EBITDA: the 15.6x the market pays today for the Street's FY27, less half a turn per point of the 2.2pp growth
gap (slope 0.49, CI 0.32-0.65, giving $140-147). Of the $23 a share between $167 and $143, $8 is revenue below the Street with costs following
at their measured elasticity (0.36), $9.5 is the multiple that follows lower growth, and $6, a quarter, is the cost leg: $2.4 because
Airbnb's cost base has not come down when revenue slowed (no measurable cut in ops, S&M or total cash costs since 2022) and $3.4 because our
cost path grows 11.1% against a Street 10.0% that would be the slowest year since the IPO; FY24-25's 12.6% is worth $140 and a repeat of
FY26's 15% is worth $135. A Monte Carlo in which margin is an output of cost growth (8.7-15%, mode 11.1%) and the multiple moves with
growth gives a median $145, a 5-95% range of $126-168 and P(< $143) 0.44 (20,000 draws; the old driver-model simulation, re-scored at
today's price, gives a $176 median and 68% upside because it holds the multiple independent of growth). Costs alone at the Street's
revenue are worth $3-6 a share; the target is a multiple-lens number, and a reverse DCF cannot distinguish the cost paths (WACC and SBC
treatment move the implied margin by 4-12 points). What breaks it: FY27 costs growing 10% or less with revenue at the Street puts the
stock at $167-172.

## What failed or is weak

- The corrected MC is a restatement of the official model with uncertainty, not new evidence: its centre is the official v2 number by
  construction, and its P(< spot) of 0.94 comes from charging every growth shortfall twice. Quote the median and the range; do not quote
  0.94 as the probability the short works.
- The spot-anchored multiple (15.61x at the Street's growth) treats today's price as fair for the Street's case. On DEC-0014's literal line
  the Street's case is $171.8 and the price already discounts about one point of cost growth above the Street (35.3% implied margin). The two
  readings differ by $4-5 on every row; the note carries both and takes the spot-anchored one as primary because the $143 was built by
  solving from the price.
- The cost-growth PERT (8.7 / 11.1 / 15.0) is a judgement distribution over 41's four anchors. 41's own evidence for costs above the Street is
  descriptive (n 4 recent prints; the COGS test depends on two rounding-level prints), so the mode at the line build is an assumption. The
  Street-centred variant ($147.5) is the fair comparison.
- k is the contemporaneous total-cash-cost elasticity (0.36); the asymmetric fit (k_dn -0.26, p 0.08, n 16) is not significant and was
  clipped to 0 in the variant. Using it moves the median by $0.3.
- No multiple residual in the primary run; A's regression residual is about 3 turns. The 1.5-turn variant is the honest width: P5-P95
  $117-177.
- FY26 revenue and cost bases are held at the official v2 values (half actual, half forecast); the 2H26 gap to the Street ($72m revenue,
  $34m costs) is inside step (a) and (c).
- The fade DCF is A's function copied in form; WACC and SBC treatment dominate, as A found. It is reported so the memo can say the target
  does not rest on it.
- Parameter count: **zero fitted here**. Inherited: joint-solve intercept and slope (2, spec A), DEC-0014 slope (1 of 4 in that regression),
  M6 k (1 of 2 per line), FCF conversion (1). Judgement constants: six PERT bounds, the 1.5-turn residual, the clip at 6x, the spot anchor.

## RESUME

Done. If the memo adopts the paragraph in section 6, cite `43b_scenario_table.csv` for the table and `43b_bridge_summary.csv` (official v2,
line build, m6, slope 0.486) for the split; re-run after DEC-0015 refreshes the spot (change `SPOT` at the top of `run.py`; every number
re-anchors) and after the September Inside Airbnb dumps move the official revenue line (change the `OFFICIAL` block from
`final_income_statement.md`). Two open choices for Theo: (i) spot-anchored versus DEC-0014-literal multiple line ($4-5 on every row);
(ii) which cost path is the base for the memo's Point 3 (line build 11.1% gives $143.6; history 12.6% gives $140.1). On 5 Nov the 3Q26 cost
print against the Street's $2,383m (41's live call) is the first test of the cost PERT's mode.

## Erratum (23 Sep 2026, Codex check `audit/CODEX_THESIS3_TEXT_CHECK.md`)

- "Each point of revenue growth = $1.5 via EBITDA" is wrong: at the final multiple it is ~$3.4 a share with fixed costs and ~$2.6 with the
  0.364 flex (the $4.3 via the multiple stands).
- Jessie's simulation does link growth and the multiple, through its 0.5 Gaussian copula (reproduced correlation 0.497); the difference
  is that the link is generic, not the cost mechanism. The updated median is $158.5 with revenue centred on the Street.
- The thesis-3 share is order-dependent: $5.82 (25%) revenue first, $3.43 (15%) costs first, $4.62 (20%) order average. Step (c)
  includes $37M from the line build's higher FY26 cost base.
- The 0.49 slope is estimated on changes in the trailing EV/LTM EBITDA multiple; applying it to the forward multiple is an assumption.
