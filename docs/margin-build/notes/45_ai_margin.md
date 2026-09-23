# 45. Does AI rescue the Street's FY27 margin?

Krish with Claude (Opus 5.5), 23 Sep 2026, branch `krish/cost-leg`. Script `analysis/src/margin_build/45_ai_margin/run.py` (`py -3.13`,
exit 0), outputs `data/processed/margin_build/45_ai_margin/`. It reuses the line-build engine (the `44_short_case_v2` copy of
`40_line_build`) unchanged, so cost of revenue and ops & support re-key to each revenue path's GBV, nights and bookings; the cost cases
are FY27 adjustments on top. Street = LSEG 11 Sep 2026 (FY27 revenue $15,819M, adjusted EBITDA $5,766M, 36.45%); a 23 Sep re-pull gave
$15,818M / $5,763M, so nothing moved. LSEG's I/B/E/S has no S&M, R&D or G&A fields: the Street's cost lines are not observable, only its
total (revenue − EBITDA) and a cost-of-goods field. Zero fitted parameters.

The question (Krish, 23 Sep): the Street models spending growth coming down through 2027 because management says AI is already cutting
costs; is assuming our cost path a safe bet, and does the thesis survive if AI delivers?

## Bottom line

1. **We do not assume flat opex; the line build already credits AI and efficiency.** Ops & support, product development and G&A
   together fall from 29.2% of revenue in FY25 to 25.6% in FY27 on the line-build revenue path (26.2% on the official model's lower
   revenue, −2.9pp): ops 10.1% → 8.7% (support cost per booking −14% in 2H26 and −10% in FY27 on the third-party-support fifth of the
   line, worth $53.5M in FY27 against no further decline from 2H26: $30M from FY27's decline, $23M carried from 2H26), G&A 8.1% → 6.6%,
   PD 10.9% → 10.3%. S&M (+2.5pp) and cost of revenue (+0.4pp, mostly hosting and AI compute) absorb it.
2. **The AI saving in the filings is real but small, and management is spending it.** The 2Q26 10-Q credits AI with a $17M fall in
   third-party support costs in the quarter ($15M in 1H26), against +$27M ops payroll, +$62M product-development payroll and +$184M S&M in
   the same quarter (1H26: +$41M, +$132M, +$372M; server costs +$15M). Management's own words: "We plan to reinvest most of these
   efficiencies into marketing, product and technology" (Mertz, 12 Feb 2026, when FY26 margin was guided "stable"); cost of revenue and
   ops & support "will scale somewhat linearly with ... the growth in revenue" (same call); the 2026 guide "does assume a material
   increase in terms of the AI spend" (6 Aug 2026); the support staff AI frees up are being trained "to do more premium customer service"
   (Chesky, 8 Sep 2026). The headline metric (support cost per booking −16% in 2Q26) covers the third-party contact cost, not the line:
   total ops & support still grew 8-9% in 1H26.
3. **The margin miss does not depend on our AI view.** Take the Street's own FY27 cost path, with whatever AI savings it embeds, and let
   it flex down with our lower revenue at the measured elasticity (0.364, i.e. costs come down "a bit"): on the official model's revenue
   FY27 margin is **35.4% against 36.4% (−103bp), EBITDA −$303M (−5.3%)**, price $149 on the 43b multiple. That is operating leverage in
   reverse, not a cost call.
4. **To hold the Street's margin on our revenue, Airbnb would need FY27 cost growth of 7.3%** (vs the Street's 10.0% and 12.5-25% in
   every year since the IPO), $251M below the Street's own cost plan and $377M below our line build. Holding the Street's EBITDA dollars
   needs 5.7%. For scale, a deliberately generous case of AI efficiencies plus lower assumed compute spending (ops & support per
   booking −10% across the *whole* line, product development +5%, G&A +3%, hosting at the $340M low estimate from DEC-0023; $107M of its
   $281M is the lower compute assumption, not measured automation) still leaves FY27 at **35.8% (−62bp), EBITDA −$240M**. Closing the
   remaining margin gap takes another ~$96M of savings anywhere; of the cases tested, only D (every AI lever plus S&M capped at the
   Street-implied residual) reaches the Street's margin (36.7%, +23bp), and even then EBITDA is $108M below the Street and the stock is
   worth $154 because growth, and so the multiple, is lower. **So the margin call is contestable if everything on costs goes right; the
   EBITDA and multiple call is not.**
5. **FY26 (the 5 Nov sentence).** On official-model revenue, FY26 is 35.1% on our costs and **35.4% even on the Street's own 2H26 cost
   path flexed**, both below the "at least 35.5%" floor. Whatever one believes about AI, our revenue path forces a choice on 5 Nov: trim
   Q4 spending or soften the floor.

## The FY27 grid (`45_fy27_grid.csv`; margin, EBITDA vs the Street, price on the spot-anchored growth-linked multiple)

| Cost case | Street-level revenue ($15,829M) | Official v2 revenue ($15,425M) | Short-case revenue ($14,563M, no RNPL overlays) |
|---|---|---|---|
| A. Line build (our costs) | 35.7%, −$122M, $161 | 34.0%, −$521M, $144 | 31.3%, −$1,206M, $110 |
| B. A with S&M capped at the base-path Street residual (+9.5%) | 36.5%, +$9M, $165 | 34.9%, −$390M, $147 | 32.2%, −$1,074M, $112 |
| C. A plus AI bull (efficiencies + lower assumed compute) | 37.4%, +$159M, $168 | 35.8%, −$240M, $151 | 33.5%, −$893M, $116 |
| D. AI bull and S&M slowing | 38.3%, +$290M, $172 | 36.7%, −$108M, $154 | 34.4%, −$762M, $119 |
| E. Street's cost path, flexed down with revenue (k 0.364) | 36.5%, +$7M, $164 | **35.4%, −$303M, $149** | 33.0%, −$965M, $114 |
| F. Street's cost path, no flex | 36.5%, +$9M, $165 | 34.8%, −$395M, $147 | 31.0%, −$1,256M, $108 |

Reading it: across a row the damage comes from revenue; down a column, the cost case moves FY27 margin by about 2.7 points between the
line build and the most generous case. On Street-level revenue the AI bull case would make the stock a long ($168-172 against $167); on
our revenue even the most generous cost case leaves EBITDA below the Street. The short does not need a cost call. It needs the revenue
call plus the absence of a cost cut large enough to offset it, and the table sizes that cut.

## Break-evens (`45_breakeven.csv`)

| Revenue path | FY27 cost growth that holds the Street's 36.45% | Cut vs the Street's cost plan | Cut vs our line build | Cost growth that holds the Street's $5,766M EBITDA |
|---|---|---|---|---|
| Street-level | 10.1% | none | $125M | 10.1% |
| Official v2 | **7.3%** | **$251M** | $377M | 5.7% ($395M below the Street's plan) |
| Short case | 1.3% | $798M | $748M | −3.7% |

Cost growth is on the Street's FY26 cost base ($9,136M, revenue − EBITDA); FY21-FY25 actual cost growth was 21.2 / 25.0 / 14.0 / 12.7 /
12.5%.

## The AI ledger (`45_ai_ledger.csv`, FY27 unless stated)

| Item | $M | Kind |
|---|---|---|
| Support automation already in the line build (vs no further support-cost-per-booking decline from 2H26) | +53.5 | AI saving in our model |
| Engineering productivity if PD's slowdown from +14.3% (FY25) to +8% is all credited to AI (generous) | +93 | AI saving in our model, if attributed |
| AI tooling in PD | −30 | AI cost in our model |
| Hosting above the FY25 run-rate of $224M | −223 | compute cost in our model (DEC-0023 low estimate would cut it by $107M) |
| Filed, 2Q26: third-party support costs, "lower agent contact volume resulting from increased use of AI" | +17 (quarter) | realised |
| Filed, 1H26: same | +15 (six months) | realised |
| Filed, 1H26: ops & support payroll / PD payroll / S&M / server costs | −41 / −132 / −372 / −15 | realised cost growth |

AI bull case components against the line build on official-model revenue: ops & support −$110M, product development −$44M, G&A −$20M,
hosting −$107M; total $281M.

## What the Street's numbers do and do not show (`45_street_split.csv`)

The Street's FY27 margin expansion (+0.83pp over its FY26) comes almost entirely from the EBITDA-cost residual after LSEG's COGS field
(47.5% → 46.75% of revenue, −0.76pp); its cost of goods stays at ~16.8% of revenue. The residual is not observed functional opex (add-back
allocation and COGS comparability are unestablished), and we cannot see whether its leverage is AI, S&M slowing or both,
because no vendor publishes the lines; the C4 dossier's "S&M +9.5%" is a residual on our other four lines, not a Street number. Our
line build's opex leverage is smaller (−0.3pp of revenue, from a lower FY26 base) and our cost of revenue rises 0.4pp on hosting: of our
FY27 costs' $131M excess over the Street, $101M is cost of revenue (hosting and AI compute) and $30M is opex (41, `41_cogs_attribution.csv`).
On costs, the disagreement with the Street is mostly about what AI costs to run, not what it saves.

## What failed or is weak

- The AI bull case is a construction, not a forecast: each lever is set at the favourable end of what management has said or done
  (whole-line ops decline is twice the best observed line-level decline of −5.3% per booking in 2Q26).
- The flex elasticity (0.364) is a contemporaneous quarterly association (M6), used here as "costs come down a bit"; the restricted-window
  estimates are 0.30-0.34.
- The short-case column runs the short revenue path at base costs, without 44's RNPL cost overlays, so it is not the short case's EBITDA.
- Prices use 43b's spot-anchored multiple with the 0.49 turns-per-point slope (estimated on the trailing multiple); treat them as
  scenario values.

## Codex check

`audit/CODEX_AI_MARGIN_CHECK.md`: every number in the six CSVs reproduced; seven wording findings (A01-A07) applied above (revenue
path for the line shares, the compute component of the AI bull case, "of the cases tested", $53.5M, the Street FY26 cost base, the S&M
residual label, the COGS residual label). The inherited parameter note calling the +$12M server cost a half-year figure is a quarterly
figure (1H26 +$15M); no number here uses it.

## RESUME

Done. Quote bottom lines 3-5 in the memo (the thesis survives the AI argument because it is a revenue-deleverage argument) and bottom
line 2 in Q&A. On 5 Nov, the tells for this note: ops & support growth vs the third-party-support saving in the 10-Q MD&A; any
quantified AI saving; the FY26 margin sentence (the floor is at risk on our revenue even on the Street's costs).
