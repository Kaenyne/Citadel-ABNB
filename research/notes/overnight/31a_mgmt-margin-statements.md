# 31a. What management has actually said about margin and cost lines, 2020-2026

Krish with Claude Code, 8 Sep 2026. Script `analysis/src/overnight/31a_mgmt_margin_statements.py` (`py -3.13`, rebuilds every CSV from raw text). Outputs `data/processed/overnight/31a_mgmt_margin_statements.csv` (194 statements), `31a_margin_algorithm_quotes.csv` (25), `31a_mgmt_implied_profile.csv` (9 cost lines x FY2026/27/28 = 30 rows). Sources: all 23 shareholder letters 4Q20-2Q26, all 23 earnings calls over the same span, and 5 investor-conference appearances. Every quote is verified programmatically as an exact substring of its source document after whitespace normalisation; the script prints any failure and there are none. Extends workstream 03 (83 curated claims) and workstream 07 (22 operational initiatives); does not replace them.

## Bottom line

1. **The operating rule is explicit, repeated and load-bearing: find variable-cost efficiency every year and spend most of it.** Mertz, 3Q24 call: *"the way we do that is to find incremental efficiencies every year across, in particular, variable costs and invest some of that into greater service levels on both sides of the marketplace."* Restated at 4Q24, 1Q25, 4Q25 (*"we plan to reinvest most of these efficiencies"*) and 2Q26. The consequence for a model is that **margin is a policy variable, not an output**: FY margins have sat in a 35-37% band for four years (36.84 / 36.40 / 35.10, FY26 guided >=35.5) while every underlying cost line moved by 100-800bp. Do not model margin as the residual of a cost build; model the cost lines, then check the residual against the floor.
2. **The floor is real and has never been tested.** Mertz introduced it at 4Q23 (*"we are basically giving ourselves a floor"*) and named it at 2Q26 (*"there's a relative floor in our ability to continue to invest against that"*). Every FY floor has been beaten: FY2024 35.0% -> 36.40% (+140bp), FY2025 34.5% -> 35.10% (+60bp), FY2026 raised twice from "stable" to >=35% to >=35.5%. The mean cushion on the seven floor rows in `02_guidance_accuracy.csv` is 1.51pts. Total-margin statements are 91% kept (n=43). **Trust the floor; do not trust anything they say about the lines beneath it.**
3. **Marketing is where the guides break, and it has broken in the same direction three years running.** S&M % of revenue: 17.78 (FY23) -> 19.35 (FY24) -> 21.14 (FY25) -> 25.87 (1H26). The FY2024 guide was Stephenson's *"we're going to keep marketing costs as a percentage of revenue largely the same as what it was in 2023"* (4Q23 call) and it missed by **157bp**, worth ~4% of EBITDA. Stephenson's 4Q21 promise of post-2023 marketing leverage (*"we could see it in 2023 and beyond"*) never arrived. Brand-marketing statements are 63% kept (n=35), the second-worst line in the file. Note also that the S&M line stopped being an advertising ratio in 2025 (2Q25: the increase *"is focused in particular on our field operations, our go-to-market activities and supply acquisition"*) - but in 1H26 brand+performance cash marketing itself grew 32% y/y against 17% revenue growth, so the field-ops excuse no longer covers it.
4. **AI has produced exactly one disclosed cost number and zero disclosed productivity numbers, and management contradicted itself on the spend in six months.** The cost claim is real: customer-support cost per booking -10% y/y (1Q26) and -16% y/y (2Q26), AI resolution share a third (4Q25) -> over 40% (1Q26) -> nearly 45% in 50+ languages (2Q26). The productivity claim is not: Chesky's "+30% engineering productivity" has been in the record since 1Q23 and product development has deleveraged every year since (17.36 -> 18.52 -> 19.23 -> 20.84% of revenue). On spend, Chesky at 4Q25: *"our investment in AI will not affect the P&L. I don't think you'll see it in the P&L."* Mertz at 2Q26: the guidance *"does assume a material increase in terms of the AI spend over the course of the year."* Neither the size nor the line is given.
5. **Take-rate guides run one way: promised up, delivered flat.** The 4Q24 call promised FY2025 gets *"the full benefit of 20 basis points increase"*; FY2025 printed 13.41% against 13.57%, -16bp y/y and 36bp below the guide. The 1Q26 letter said monetisation *"expected to lift our full year take rate"*; the 2Q26 letter took it back to *"relatively flat"* because of customer incentives on the new businesses, whose size is not given. Take-rate statements are 59% kept (n=17). The multi-year monetisation claims are worse: Chesky told Morgan Stanley in Mar 2023 he could *"easily"* imagine adding a few percentage points of take rate; three and a half years later it has moved inside a ~50bp band and advertising is explicitly deferred behind AI search.

## (a) What has actually driven margin since 2021, in order of size

By management's own attribution, cross-checked against `abnb_quarterly_costlines.csv`. Margin went from 26.57% (FY2021) to 36.84% (FY2023), then down to 35.10% (FY2025).

| Rank | Driver | Size, FY21 -> FY23 | Who says so |
|---|---|---|---|
| 1 | Product development leverage | 23.78 -> 17.36% of revenue, **-642bp** | Stephenson 4Q21 (*"growing our product development expenses more slowly than we're growing revenue"*), 3Q23 (headcount +4%) |
| 2 | Marketing reset | 19.79 -> 17.78%, **-201bp**, and -1,390bp against 2019's 33.7% | Chesky 4Q20, Stephenson 4Q20/3Q21; workstream 07 OPS-01 |
| 3 | Ops & support | 14.13 -> 11.96%, **-217bp** | Stephenson 4Q20 (*"discipline of variable expenses"*), 1Q23, 3Q23 |
| 4 | Cost of revenue / payments | 19.29 -> 17.17%, **-212bp** | Stephenson 4Q20/1Q23; merchant fees + chargebacks 2.51% of GBV (FY20) -> 1.80% (FY21) |
| 5 | ADR | not disclosed | Mertz, Bernstein 2024: *"a portion of that margin expansion comes from higher ADR"*; Stephenson 4Q21: *"the tailwind of average daily rate... definitely helped our margins"* |
| 6 | G&A | 13.95 -> 11.31% FY22 (FY23 is distorted +1,160bp by the Italian tax reserves) | Mertz 4Q24 |

Two honest qualifications. First, management concedes ADR did some of the work usually credited to cost discipline (Mertz, Bernstein, May 2024) - which means the cost-side attribution above is an upper bound. Second, **every one of the top four drivers has stopped working**: product development, marketing and cost of revenue have all deleveraged since FY2023, and only ops & support is still compounding.

## (b) What they say drives it from here, line by line, with their numbers

| Line | FY2026 statement | Their number | Statement ids |
|---|---|---|---|
| Total margin | *"at least 35.5%... reflects stronger topline growth and underlying operating leverage in our core business"* (2Q26 letter) | >=35.5%, i.e. >=+40bp y/y | S159, S150, S137 |
| Cost of revenue | *"cost of revenue and ops and support will scale somewhat linearly... We'll have some efficiencies there"* (Mertz 4Q25) | flat % of revenue | S146 |
| Ops & support | support cost per booking -16% y/y; *"we expect those costs to continue to decline"* (Chesky 2Q26) | -10% (1Q26), -16% (2Q26) | S151, S152, S160, S188 |
| Product development | *"we don't need to grow our head count at levels that we did in the past"* (Mertz 2Q26); *"growth rate of SBC and headcount will be lower than 2025"* (4Q25 letter) | slower than FY25's ~+12% | S163, S144 |
| Brand marketing | *"Where you will see some incremental investment to drive growth is, obviously, in sales and marketing"* (Mertz 4Q25); reinvestment in *"efficient marketing spend, international expansion, and AI initiatives"* (1Q26) | no number; 1H26 actual 25.87% of revenue | S147, S153, S193 |
| Field ops / new business | *"some of the investments this year will carry into next year as fixed head count"* (Mertz 2Q25) | **no FY26 dollar figure** | S127, S182 |
| G&A / tax | *"we expect our effective tax rate to be in the high teens"* (1Q26 letter) | high teens vs 20% FY25 | S157, S148 |
| SBC | growth rate lower than 2025 | no number | S144 |
| Take rate | *"relatively flat compared to 2025"* after *"higher customer incentives related to new businesses"* (2Q26) | flat; incentive drag **unsized** | S165, S166 |
| FX | *"an approximate 3 percentage point foreign exchange tailwind after factoring in our hedging program"* (2Q26) | ~3pts on revenue, fading | S122 |

**FY2027 and FY2028 are almost entirely silent.** The only quantified statement outstanding past FY2026 on any cost line is the OBBBA long-term effective tax rate of mid-to-high teens - and that sits below the EBITDA line. Mertz refused a 2027 number twice on the 2Q26 call: *"I'm not going to give you a specific guide for 2027 and beyond."* Airbnb has had no long-term margin target since Stephenson's 30%-or-greater of Feb 2021, and explicitly declined to replace it at 2Q23 (*"I don't have a new long-term target"*). `31a_mgmt_implied_profile.csv` marks 12 of its 30 rows `mgmt_silent = yes`. Anything a model asserts about FY2027-28 cost lines is the analyst's view, not management's.

## (c) Where the forward claims have been reliable, by cost line

Closed statements only (open and unverifiable excluded). "Hit rate" = kept / (kept + partly + missed).

| Cost line | kept | partly | missed | hit rate | n |
|---|---|---|---|---|---|
| total_margin | 39 | 2 | 2 | **91%** | 43 |
| ops_support | 13 | 0 | 0 | **100%** | 13 |
| cost_of_revenue | 9 | 1 | 1 | 82% | 11 |
| field_ops | 8 | 0 | 3 | 73% | 11 |
| brand_marketing | 22 | 7 | 6 | **63%** | 35 |
| product_dev | 9 | 3 | 3 | 60% | 15 |
| take_rate | 10 | 3 | 4 | **59%** | 17 |
| sbc | 2 | 1 | 2 | **40%** | 5 |
| g_and_a / tax | 1 | 2 | 0 | 33% | 3 |

By horizon: next-quarter 93% (n=14), full-year 74% (n=85), structural 89% (n=27), **multi-year 48% (n=31)**. By speaker: Mertz 89% (n=44 closed), shareholder letter 77% (n=48), Stephenson 61% (n=44), **Chesky 57% (n=21)**. This tracks workstream 03's finding on the wider claim set (multi-year 26.3%, Chesky 42.1%) and sharpens it: the CEO's cost claims are the least reliable in the file and every one of the four largest misses is his or is a multi-year one.

The four misses worth carrying into a model:

- **Marketing leverage after 2023 (Stephenson, 4Q21).** *"we don't expect to see that additional leverage in 2022, but we could see it in 2023 and beyond."* S&M % of revenue has risen 810bp since the FY2023 trough.
- **FY2024 marketing flat (Stephenson, 4Q23).** Missed by 157bp. It is absent from `02_guidance_ledger.csv` because that file is letter-sourced - see corrections.
- **New businesses cost little (Chesky, 2Q24).** *"Most of these new services and offerings, though, are going to not cost very much."* Six months later the 4Q24 letter put FY2025 at $200-250m, and field-operations cash grew 43% ($693m -> $993m).
- **FY2025 take rate +20bp (Mertz, 4Q24).** Printed -16bp, a 36bp miss.

And the one reversal inside a single quarter, which is worth more than any of them as a signal about how firm these numbers are: the **4Q24 letter** said the new-business margin drag would be *"most pronounced during the first nine months of 2025"*; the **1Q25 letter** said *"during the second half of the year."*

## (d) The AI claims, split into cost claims and productivity claims

**Cost claims - one has landed, one is contradicted, one is unfalsifiable.**

| Claim | Said | Shown in filed numbers |
|---|---|---|
| Support automation cuts cost | Stephenson 2Q23 (*"automate more customer service contacts"*), Chesky 1Q24 (*"biggest impact... on customer service"*), 4Q25 (*"reduce the cost base of Airbnb customer service"*) | **Yes.** Cost per booking -10% (1Q26), -16% (2Q26). Deflection 15% (2Q25) -> ~33% (4Q25) -> >40% (1Q26) -> ~45%, 50+ languages (2Q26). Ops & support 11.83% of revenue in 1H25 -> 10.93% in 1H26 |
| AI spend is invisible in the P&L | Chesky 4Q25: *"our investment in AI will not affect the P&L"* | **No.** Mertz 1Q26: *"an expense that will ramp over the course of the year."* Mertz 2Q26: *"a material increase in terms of the AI spend."* Separately, purchase obligations went $719m -> $1,749m and the hosting commitment from $672m through 2027 to $1.7bn through 2031 (workstream 07 OPS-09) |
| No AI capex | Chesky 4Q23 (*"we're not going to be investing in infrastructure"*), 4Q25 (*"we're not building data centers"*), 2Q26 (*"We are not buying up a whole bunch of GPUs"*) | **Yes on capex** (~1% of revenue), but it says nothing about inference opex, which is the item that is rising |
| Inference cost is de minimis | Chesky 2Q26: *"the inference cost is so outweighed by the amount of money we make on that increased ROI"* | **Unfalsifiable.** Airbnb discloses neither inference cost nor AI-attributable revenue |

**Productivity claims - nothing has shown up in a filed number.** Chesky, 1Q23: employees, *"especially our developers, 30% more productive in the short to medium term."* Chesky, 4Q24, two years later: *"I don't think it's flowing to like a fundamental step-change in productivity yet... in some kind of medium term of a few years, you could easily see like a 30% increase."* Chesky, 4Q25: *"More than 80% of engineers are now using AI tools."* Mertz, 2Q26, the first claim of an actual effect: *"we don't need to grow our head count at levels that we did in the past because we're getting so much more output and speed from our existing workforce."*

Against that: product development is 17.36 (FY23) -> 18.52 (FY24) -> 19.23 (FY25) -> 20.84% of revenue (1H26); product-development cash rose $669m -> $749m (+12%), all payroll; headcount grew about 12% in 2025 and revenue per employee fell for the first time, $1,521k -> $1,493k (workstream 07 OPS-03 and OPS-08). Adoption metrics (80% of engineers, 60% of code AI-authored) are inputs. **The only AI productivity claim with a falsifiable date attached is the 4Q25 support one, and it is running ahead of schedule; the engineering one has now been three years without evidence.**

## (e) Every full-year margin guide sentence, 4Q23 to 2Q26

Exact wording from the letters (call restatements in `31a_mgmt_margin_statements.csv`).

| Print | Date | Sentence | Guide | Outcome |
|---|---|---|---|---|
| 4Q23 | 13 Feb 2024 | "For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year." | floor 35.0% | 36.40%, **+140bp** |
| 1Q24 | 8 May 2024 | "For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year." | floor 35.0% | +140bp |
| 2Q24 | 6 Aug 2024 | "For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%" | floor 35.0% | +140bp |
| 3Q24 | 7 Nov 2024 | "For the full-year 2024, we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%." | point 35.5% | **+90bp** |
| 4Q24 | 13 Feb 2025 | "Inclusive of these investments, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5% - maintaining our strong track record of profitability without compromising our growth initiatives." | floor 34.5% | 35.10%, **+60bp** |
| 1Q25 | 1 May 2025 | "For full-year 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%, maintaining our strong track record of profitability while making meaningful investments behind future growth levers." | floor 34.5% | +60bp |
| 2Q25 | 6 Aug 2025 | "For 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%, maintaining our strong track record of profitability while making meaningful investments behind future growth levers." | floor 34.5% | +60bp |
| 3Q25 | 6 Nov 2025 | "For the full-year 2025, we now expect to deliver an Adjusted EBITDA Margin of approximately 35%." | point 35.0% | **+10bp** |
| 4Q25 | 12 Feb 2026 | "For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year as we reinvest top-line efficiencies to support growth across the business, primarily in marketing, product, and technology." | y/y 0.0pts | open |
| 1Q26 | 7 May 2026 | "For 2026, we now expect our Adjusted EBITDA Margin to be at least 35%." | floor 35.0% | open |
| 2Q26 | 6 Aug 2026 | "For 2026, we now expect to deliver a full-year Adjusted EBITDA Margin of at least 35.5% - an improvement from 2025 that reflects stronger topline growth and underlying operating leverage in our core business, while continuing to invest behind opportunities to drive future growth." | floor 35.5% | open |

Three regularities. **The guide is a floor in February and a point in November** (FY24 and FY25 both), so expect the FY26 floor to become "approximately X" on 5 Nov 2026. **The floor is set 60-140bp below the eventual print.** And **the reason given shifts**: 2024-25 floors were justified by the flexibility to invest; the 2Q26 raise is justified by "operating leverage in our core business" - not by the new businesses, and not by AI.

## Corrections to existing work

1. **`2026-09-05_guidance-margin-items.md` and `2026-09-05_margin-drivers.md` (§5.1, §7) say the FY floors were beaten by "60 to 180 bps". No guide/actual pair produces 180bp.** The correct floor beats are FY2024 +140bp and FY2025 +60bp; on final (point) guides, FY2023 +78bp, FY2024 +90bp, FY2025 +10bp. `30_mgmt_language.csv` already has "60-140bps", so the repo is internally inconsistent. Use 60-140bp.
2. **`2026-09-05_margin-drivers.md` §7 folds FY2023 into the floor series. FY2023 was never a floor guide** - the 4Q22 letter said "maintain", the 2Q23 letter "modestly higher" and the 3Q23 letter "approximately 150 bps higher". The floor regime starts at 4Q23.
3. **`02_guidance_ledger.csv` is missing the two FY guides that matter most for cost work.** It is letter-sourced (2 of 194 rows carry `source=transcript`), so the FY2024 flat-marketing guide (Stephenson, 4Q23 call) and the FY2025 +20bp take-rate guide (Mertz, 4Q24 call) are absent, and `02_guidance_accuracy.csv` therefore understates the miss rate on both lines. Both are in this file as S071/S072 and S110.
4. **`2026-09-05_margin-drivers.md` §4 states the SBC guides were "missed by 6-11 points". That range is series-dependent and should be stated as such.** XBRL (`abnb_quarterly_costlines.csv`): FY2024 +30.8% against guides of +20% and +25%, i.e. misses of 10.8 and 5.8pts. Shareholder letters (`abnb_fcf_bridge.csv`): +25.6%, i.e. misses of 5.6 and 0.6pts. Pick one and say which.
5. **The claim that the SBC-equals-headcount promise "has never been met" is wrong for FY2025.** FY2025 SBC grew +9.9% (XBRL) / +13.1% (letters) against headcount growth of about +12%. That is convergence. The 4Q25 letter nonetheless retreated to the weaker "lower than 2025", which is a signal about management's confidence, not a failure of the rule.
6. **`2026-09-05_margin-drivers.md` §1.4 and §4 still say the S&M growth "is not ads", on FY2025 data.** 1H26 reversed it: brand+performance cash +32% y/y against +17% revenue growth (workstream 07 OPS-19). The note's own §7 already contradicts its §1.
7. **The FY2024 adjusted EBITDA margin is 36.40%, not 35.8%.** Several drafts in this session's working set used 35.8%; the panel gives 36.40% and the 4Q24 letter says "36%". The FY2024 floor cushion is therefore 140bp, not 80bp.

## For the model

| Parameter | Management's number | Source (file + locator) |
|---|---|---|
| FY2026 adj. EBITDA margin | >= 35.5% | `31a` S159, letter:2Q26 |
| FY2026 cost of revenue | flat % of revenue ("scale somewhat linearly") | S146, call:4Q25 QA |
| FY2026 ops & support | support cost per booking -10% to -16% y/y and still falling | S151/S152/S160, call+letter 1Q26 and 2Q26 |
| FY2026 product development | headcount growth below FY2025's ~+12% | S163, call:2Q26 QA; S144, letter:4Q25 |
| FY2026 S&M | rising; no number. 1H26 actual 25.87% of revenue | S147, call:4Q25 prepared |
| FY2026 field ops / new business | no dollar figure. FY2025 was ~$200m and did not roll off | S127, call:2Q25 QA |
| FY2026 SBC | growth rate below FY2025's | S144, letter:4Q25 |
| FY2026 take rate | flat vs FY2025 13.41%; incentive drag unsized | S165/S166, call:2Q26 prepared |
| FY2026 effective tax rate | high teens (vs 19.95% FY2025) | S157, letter:1Q26 |
| FY2026 FX | ~3pt revenue tailwind after hedges, fading through the year | S122 + 4Q25/1Q26/2Q26 letters |
| 3Q2026 margin | "down slightly compared to Q3 2025" (50.1%) | S170, letter:2Q26 |
| FY2027 anything | **nothing.** Only the OBBBA mid-to-high-teens tax rate | S179, call:2Q26 QA |
| FY2028 anything | **nothing** | - |
| Brand marketing structure | fixed cost per market; performance is a "surgical topper" | S108, call:4Q24 QA; S126, call:2Q25 QA |
| Reinvestment rule | find variable-cost efficiency yearly, reinvest most of it | S097, call:3Q24 QA; S138, call:4Q25 prepared |
| Floor rule | margin will not be spent below the delivered band | S069, call:4Q23 QA; S164, call:2Q26 QA |

Practical implication: **the only forward cost line management has given a usable number for is customer support.** Everything else is either a direction (marketing up, headcount slower), a structural claim (brand is fixed per market), or silence. A cost build for FY2026 that is not anchored on the 35.5% floor is anchored on nothing management said.

## Caveats

- **Curation, not exhaustion.** 194 statements out of roughly 630 passages that clear a cost-or-margin keyword plus a forward-looking marker. The selection is towards statements that name a line or a number; unfalsifiable product talk is excluded. Read the hit rates as "hit rate among checkable statements".
- **Quote source.** 4Q21 and 1Q23-2Q26 are quoted from FactSet corrected transcripts (IR CDN / `data/raw/regulatory/transcripts`). 4Q20-3Q21, 1Q22-4Q22 and the five conferences have no FactSet copy on this machine and are quoted from stockanalysis.com, which is audio-aligned rather than corrector-reviewed; those rows carry the `-sa` suffix in `source`. Wording there may differ by a word or two from the corrected record. **All 23 prints 4Q20-2Q26 are covered; nothing is missing.**
- **Verdicts are mine.** "kept / partly / missed" scores whether the stated outcome happened, not whether it was reasonable at the time. A cost guide missed in the cost-favourable direction (2022 headcount) still scores as missed.
- **Where this file disagrees with workstream 03.** 32 rows carry a `claim_id_03`; five score differently and the difference is deliberate. C005 (4Q20 "too hard to give 2021 targets"): 03 says unverifiable, I say kept, because no FY2021 guide was ever given and that is the checkable fact. C014 and C021 (FY2022 flat marketing): 03 says kept, I say partly, because the line came in 175bp better than flat. C016 (4Q21 ADR margin headwind): 03 says missed, I say partly, because the mechanism is right and only the direction of ADR was wrong. C036 (2Q23 "margin expansion by launching incremental services"): 03 says missed, I say open, because the stated horizon is "over the coming years" and services shipped only in May 2025.
- **Two series problem.** SBC and cost-line percentages differ between the XBRL panel and the shareholder-letter series. This file uses the XBRL panel (`abnb_quarterly_costlines.csv`) for cost-line percentages and names both series wherever SBC growth is scored.
- **Contra-revenue.** The 2Q24 letter says some customer-service investment is booked as contra-revenue rather than in operations and support. The ops & support line therefore understates support cost, and the implied take rate absorbs part of it. Neither effect has ever been sized.
- **Unsized items in the FY2026 P&L, in descending order of likely importance:** the AI spend increase ("material", never quantified), new-business investment (no FY26 figure at all), the customer-incentive drag on take rate (the difference between flat and up), and the hotels build-out (no budget). Together these are the reason the FY26 margin guide can be raised twice while no cost line is guided.
