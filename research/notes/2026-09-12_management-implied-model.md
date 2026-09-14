# The management-implied model: what Airbnb's management is telling us, priced

Krish with Claude Code, 12 Sep 2026. Branch `krish/reverse-dcf`. Workbook `model/ABNB_management_implied.xlsx` (formula-driven, recalculated in Excel and reconciled to a Python mirror: max difference 0.007 on $M lines). Builder `analysis/src/reverse_dcf/mgmt_implied_model.py` (`py -3.13`). Outputs under `data/processed/reverse_dcf/` (`mgmt_implied_summary.csv`, `_inputs.csv`, `_targets.csv`, `_dcf.csv`, `_recon.csv`).

Sources read for this note: all 23 shareholder letters (outlook sections 4Q25, 1Q26, 2Q26 verbatim), the 2Q26 call (6 Aug 2026), the Communacopia fireside (8 Sep 2026), the 2Q26 10-Q, the guidance ledger (194 statements, `02_guidance_ledger.csv`), the management margin-statement file (194 statements, `31a_mgmt-margin-statements.md`), Bloomberg FA consensus (4 Sep), Zacks and S&P Global consensus (3-4 Sep), the live sell-side target tape (31 targets). Price used: $170.19, the 11 Sep 2026 close (the stock fell 7.8% from $181.94 on 4 Sep to $167.65 on 10 Sep around the Communacopia appearance, then closed $170.19 on 11 Sep).

## 1. Bottom line

1. **Management has given numbers for exactly one quarter and one year, and the Street has copied them.** The only quantified forward statements are 3Q26 revenue $4.69-4.77bn (+15-17%, ~3pp FX), nights "low double digits", GBV "mid teens", margin "down slightly" from 50.1%, FY26 revenue "at least mid teens", FY26 margin "at least 35.5%", take rate "relatively flat" vs 13.41%, tax "high teens", SBC growth "lower than 2025". For FY27 there is nothing: "I'm not going to give you a specific guide for 2027 and beyond" (Mertz, 2Q26). Translating the FY26 guide plus management's own historical cushion into FY27 on management's stated algorithm (hold the exit growth rate, keep margin flat, reinvest the efficiencies) gives **FY27 revenue $16.0bn and GAAP EPS $6.08. Street FY27 is $15.75bn and $6.02-6.14.** Consensus is not ahead of management and not behind it; it is management's guide with the usual beat applied.

2. **At $170.19 the stock pays 16x FY27E EBITDA and 28x FY27E EPS for that case.** On the exit multiples the team's WS12 work supports (13.5 / 16.5 / 18.5x EV/EBITDA), the "guide as delivered" case is worth **$156 / $186 / $207**; on 22 / 27 / 30x P/E **$134 / $164 / $182**; on 14 / 17 / 20x EV/FCF **$164 / $196 / $227**. The average of the three mid-multiple lenses is **$182 (+7%)**; the average of all nine cells is $180. The mean sell-side target is $179-182. So the management-implied value, at middle-of-the-road multiples, is the sell-side target, and the stock sits about 7% below both.

3. **The guide-literal case (floors as points, "low double digits" = 10) is worth $174 at mid multiples, the management-ambition case $196.** The whole management spectrum at mid multiples is $174-196, i.e. +2% to +15%. The multiple matters more than the case: moving EV/EBITDA from 13.5x to 18.5x moves the Delivered case from $156 to $207, a $51 range, against a $30 range across the three cases at a fixed 16.5x.

4. **A reverse DCF on management's own FCF says the market is not asking for much.** At $170.19 the enterprise value ($92.0bn) requires FY28 FCF growth of 4.6% fading to 3% over ten years on reported FCF (Delivered case FY27 FCF $5.9bn, WACC 10%). On SBC-adjusted FCF ($4.0bn) it requires 16%. That seven-turn gap is the SBC debate the overnight synthesis already identified, and it has not changed.

5. **Where the FY26 guide bites is 4Q26, not 3Q26.** "At least mid teens" with 3Q26 at the midpoint implies 4Q26 revenue of at least $3.06bn (+10.2% y/y), and "at least 35.5%" with 3Q26 "down slightly" implies a 4Q26 margin of at least 28.6% (flat y/y on 28.3%). Street 4Q26 is $3.15-3.20bn (+13.5-15%) and 29.0%. So the Street's Q4 already assumes the beat; the guide floor is $100-140m below it. The team's WS29 base has 4Q26 at $3.11bn (+12.0%). This is where the 5 Nov print is decided and it is consistent with the trade pivot note.

## 2. The three cases

Each case is a translation of management's words into numbers. Every input cell in the workbook carries the sentence it comes from (column P of each scenario sheet).

| Case | Rule | 3Q26 | 4Q26 | FY26 | FY27 |
|---|---|---|---|---|---|
| **Literal** | range midpoints, floors as points, buckets at the low end; FY27 = the guide management would give in Feb 2027 on its own pattern ("low double digits", floor carried) | nights +10.0%, ADR ex-FX +3.0%, rev $4,730m (+15.5%), margin 49.5% | nights +8.5%, rev $3,061m (+10.2%), margin 28.6% | rev $14,077m (+15.0%), margin 35.5%, EPS $5.16 | nights +9.0%, ADR +2.5%, rev $15,630m (+11.0%), margin 35.5%, EBITDA $5,549m, EPS $5.72, FCF $5,738m |
| **Delivered** | guide plus management's own cushion: quarterly revenue +1.8% vs midpoint (median of the last eight prints; 19 of 19 beaten), nights one point above the bucket top (3 of 3 bucket guides since 4Q25 printed above range), FY margin floor +70bp (FY24 +140, FY25 +60); FY27 holds the FY26 exit rate with margin flat | nights +11.5%, ADR ex-FX +3.5%, rev $4,815m (+17.6%), margin 50.0% | nights +10.5%, rev $3,130m (+12.7%), margin 30.8% | rev $14,231m (+16.3%), margin 36.2%, EPS $5.37, FCF $5,317m | nights +10.0%, ADR +3.0%, rev $16,025m (+12.6%), margin 36.2%, EBITDA $5,801m, EPS $6.08, FCF $5,941m |
| **Ambition** | the 8 Sep CEO framing: "almost every market is accelerating", hotels 3x homes, India +60%, sponsored listings "a straight shot to $1bn"; take rate +20bp in FY27, margin drifting to 37% | nights +12.5%, ADR +4.0%, rev $4,882m (+19.2%), margin 50.4% | nights +12.0%, rev $3,188m (+14.8%), margin 31.4% | rev $14,356m (+17.3%), margin 36.5%, EPS $5.49 | nights +12.0%, ADR +3.0%, take rate +20bp, rev $16,791m (+17.0%), margin 37.0%, EBITDA $6,213m, EPS $6.68, FCF $6,347m |
| Street | Bloomberg FA 4 Sep, Zacks 4 Sep, S&P 3 Sep | nights 148.9m (+11.1%), GBV $26.4bn (+15.1%), ADR $177 (+3.3%), rev $4,744m, margin 49.7%, EPS $2.87-2.88 | nights 134.2m (+10.1%), rev $3,154-3,200m, margin 29.0%, EPS $0.82-0.85 | rev $14,100-14,160m, EPS $5.23-5.28, FCF $5.35bn | rev $15,730-15,760m, EPS $6.02-6.14 |
| Team (WS29/WS30 base) | H1-to-H2 bridge, nights deceleration base case | nights +9.9%, rev $4,771m, margin 50.8% | nights +8.9% (8.0-8.2% if the ex-NA lap is adopted), rev $3,111m (+12.0%), margin 29.7% | rev $14,168m, margin 36.2%, EPS $5.30 | rev $15,804m (+11.6%), margin 36.4%, EPS $5.90 |

Common inputs across cases: ADR FX +0.3 / -0.4 / -0.4 / 0.0 / +0.7 / 0.0 pp and revenue FX after hedging +3.0 / -0.4 / -1.0 / -0.8 / -0.6 / -0.1 pp for 3Q26-4Q27 (the WS29 consensus-EUR schedule; management guides FX one quarter ahead only); D&A 0.65% of revenue; interest income $170m falling to $160m a quarter; interest expense $31m a quarter on the $2.5bn of March 2026 senior notes; tax 18%; buybacks $1,050m a quarter ($4.2bn a year, which exhausts the $3.4bn authorisation by 2Q27, so a new programme is the likely 4Q26 or 1Q27 announcement); net RSU issuance 1.6m shares a quarter after 35% withholding; FCF/EBITDA seasonal (0.70x in Q3 and Q4, 3.2x in Q1, 1.0x in Q2, i.e. FY26 1.03x and FY27 1.01x against FY25 1.07x and LTM 1.05x). The 3Q26 timing residual is calibrated so revenue lands on the guide midpoint (Literal) or midpoint +1.8% (Delivered); it comes out at -1.05 to -1.11pp in every case, which is the RNPL book-versus-stay gap the 2Q26 guide embeds (15.5% growth = 11 nights + 3 ADR + 3 FX - 1.5).

## 3. What management is looking at, by area

Full table with sources on the `Mgmt_Statements` sheet. Condensed:

| Area | Near term (3Q26 / FY26) | Mid term (FY27+) | How reliable is this line |
|---|---|---|---|
| Nights | "low double-digit" 3Q26; every region up in 2Q26, expansion markets ~2x core, first-time bookers +11% (four-year high), app 64% of nights | No number. "Almost every market is accelerating", "four of the five countries [70% of the business] are accelerating", India +60%, core "could probably be double the size" | Bucket guides: 3 of 3 since 4Q25 printed above range by 1-5pts |
| ADR | "moderate increase... mix shift and price appreciation"; 2Q26 +4% ex-FX, larger homes fastest, bedroom nights +12% vs nights +10% | The AI pricing tool is "one of the biggest single levers", "many multiples bigger than RNPL", and it is aimed at affordability, so it argues for lower host prices over time; ADR ex-FX above ~3% is mix, not price | ADR floors and points 16 of 18 met |
| GBV | "mid teens" 3Q26; RNPL >20% of GBV, eligibility widened in July | "approaching $100 billion"; FY26 lands ~$106bn in the Delivered case | Bucket guides beaten by 4-6pts, 3 of 3 |
| Take rate | FY26 "relatively flat" vs 13.41% because of RNPL timing and "higher customer incentives related to new businesses"; single fee completed by year-end (half of listings already) | Sponsored listings "a pretty easy straight shot to $1 billion incremental high margin revenue" (undated); insurance "very high margin"; advertising waits behind AI search | The weak line: 59% kept (n=17); FY25 promised +20bp, printed -16bp; the 1Q26 "lift full-year take rate" was withdrawn in August |
| Cancellations | Never disclosed; nights and GBV are net of cancellations. The one forward-testable statement: unearned fees higher y/y in 3Q26 (1Q26 letter). Middle East cost ~1pt of 1Q26 nights | Nothing. The team's RNPL ledger (overnight2 D) models -0.1 to -1.4pts of nights | n/a |
| Revenue | 3Q26 $4.69-4.77bn; FY26 "at least mid teens" (third raise this year: low double digits in Feb, low-to-mid teens in May) | No FY27 number; the Feb guide is a floor, raised twice, printed 1-3pp above | 19 of 19 quarterly ranges beaten at the midpoint (median +2.5%, last eight +1.8%), 15 above the top |
| Margin | FY26 "at least 35.5%"; 3Q26 "down slightly" from 50.1% on "timing of investments" | "There's a relative floor"; "pretty steady, 35% margins" (8 Sep); rule: find variable-cost efficiencies each year and reinvest most of them | Total-margin statements 91% kept (n=43); floors beaten by +140bp and +60bp; the floor becomes a point at the Q3 print |
| Cost lines | Cost of revenue scales linearly; support cost per booking -16% (AI resolves ~45% of tickets); headcount growth below FY25's ~12%; S&M is where "incremental investment" goes; AI spend "a material increase", unsized | No FY27 line has a number | Ops and support 100% kept; brand marketing 63%; product dev 60%; SBC 40% |
| SBC / shares | FY26 SBC growth "lower than 2025" (1H26 +14.7%); 37.8m RSUs, 5.7m options; diluted shares 597m (-4.6% y/y) | Silent; the SBC-equals-headcount promise was withdrawn | 40% kept (n=5) |
| Capital return | $1.1bn a quarter; $3.4bn authorisation left; "a core component" | Nothing; the authorisation runs out at the current pace by ~2Q27 | FY24 $3.4bn, FY25 $3.8bn delivered; never guided |
| Tax | "high teens" (1H26 17.1% incl. a $77m prior-year benefit) | OBBBA long-term "mid-to-high teens" | Direction landing |
| Hotels | Single-digit share of nights, growing ~3x homes; 35% of first-time hotel guests return to book a home; "stepping on the gas" | "10x larger" than homes (8 Sep); "$ billions incremental revenue", horizon 2 | No hotel nights or revenue figure has ever been given |
| Services, experiences, cars | Services expanded May 2026; experiences supply +80%, bookings accelerating on a small base; car rentals "one of the biggest sellers... at one point" | Horizon 3, "multi-year", "not this year" | Multi-year claims 48% kept (n=31); Chesky 57% (n=21) |
| AI | ~45% of support tickets AI-resolved, cost per booking -16%; AI search in test on a small share of traffic; "80% more features than a year ago"; "not buying up a whole bunch of GPUs" | Consumer AI shift "the next 18 to 24 months"; full trip-planning within ~18 months; sponsored listings gated behind AI search | The support claim landed; the +30% engineering-productivity claim (since 1Q23) has never shown in a filed number |

The pattern that matters for the model: **the total-margin and next-quarter revenue lines are near-certain, the take-rate and multi-year lines are coin flips.** That is why the Delivered case applies a cushion to revenue and margin but leaves the take rate flat and gives the new businesses zero incremental revenue, and why the Ambition case is the only place a take-rate lift appears.

## 4. Target prices

Target = (multiple x FY27E metric + end-FY27 net cash) / end-FY27 diluted shares (570.7m); the P/E lens uses FY27E GAAP EPS directly. Net cash ex float at end-FY27: $10.3bn / $10.6bn / $11.1bn (from $9.6bn today, after $6.3bn of buybacks and $1.3bn of RSU withholding).

| Lens (multiple) | Literal | Delivered | Ambition |
|---|---|---|---|
| EV / FY27E adj. EBITDA 13.5x | $149 | $156 | $166 |
| EV / FY27E adj. EBITDA 16.5x | $178 | **$186** | $199 |
| EV / FY27E adj. EBITDA 18.5x | $198 | $207 | $221 |
| P / FY27E GAAP EPS 22x | $126 | $134 | $147 |
| P / FY27E GAAP EPS 27x | $155 | **$164** | $180 |
| P / FY27E GAAP EPS 30x | $172 | $182 | $200 |
| EV / FY27E FCF 14x | $159 | $164 | $175 |
| EV / FY27E FCF 17x | $189 | **$196** | $208 |
| EV / FY27E FCF 20x | $219 | $227 | $242 |
| Average of the three mid multiples | $174 | **$182** | $196 |
| Average of all nine cells | $172 | $180 | $193 |
| Upside vs $170.19 (mid average) | +2% | **+7%** | +15% |

What $170.19 pays today: EV/FY26E EBITDA 18.4 / 17.9 / 17.6x; EV/FY27E EBITDA 16.6 / 15.9 / 14.8x; P/FY27E EPS 29.7 / 28.0 / 25.5x; FY27E FCF yield 5.7 / 5.9 / 6.3%.

DCF on management FCF (10-year fade to 3%, WACC 10%, valued at 30 Sep 2026): starting FY28 growth at the case's own FY27 FCF growth gives $197 / $214 / $278. Reverse: the growth the current EV requires is 5.6 / 4.6 / 2.7% on reported FCF and 17.5 / 16.0 / 13.0% on SBC-adjusted FCF.

The multiple choice is the pitch. 16.5x is where WS12's three methods (ABNB's own multiple against forward growth 2023-26, the 19-name cross-section, the fade DCF) meet; the highest live sell-side target ($220, Rosenblatt and DA Davidson) implies 19.3x, the mean ($179) 15.4x, Morgan Stanley's $125 10.0x. The P/E lens is the lowest because ABNB's GAAP EPS carries $1.9bn of SBC; the EV/FCF lens is the highest because FCF runs above EBITDA. Put the three side by side in the deck rather than picking one.

## 5. What this does and does not say

**Says.** The consensus FY26 and FY27 numbers are the management guide with its historical cushion; there is no independent Street view to "back out" beyond that. The share price is inside the management spectrum ($174-196 at mid multiples), about 7% below the Delivered case, and consistent with either (a) the Delivered case at 15.9x EBITDA or (b) the Literal case at 16.6x. The distance from the guide floor to the Street is concentrated in 4Q26. Nothing management has said supports a take-rate lift in FY27, and the only quantified mid-term revenue claim ($1bn of sponsored listings) is undated and sits behind an AI-search rollout that is still in a small-traffic test.

**Does not say.** Anything about what the market itself believes beyond consensus: that needs the options surface, the target dispersion and the reaction function (next step). Anything regional (WS10), line-by-line cost (WS30/31) or nights-driver (PR #32) that the team's own forecasts carry. The FY27 inputs are the analyst's reading of management's algorithm; management has not said them. The FCF build is annual-grade (quarterly seasonality handled by prior-year ratios, not a working-capital model). Buybacks are held at the 1H26 pace past the current authorisation. GAAP EPS excludes other add-backs (lodging tax reserves, restructuring) that history absorbs into operating income; FY27 "other income" is zero.

**Checks in the workbook** (rows at the foot of each scenario sheet): 3Q26 revenue vs the $4,690-4,770m range; FY26 growth vs 15%; FY26 margin vs 35.5%; FY26 take rate vs 13.41%; 3Q26 margin vs 50.1%; buybacks vs the $3.4bn authorisation. Literal lands exactly on the guide in all four; Delivered lands 0.9% above the 3Q26 top, 16.3%, 36.2% and flat take rate.

## 6. Next: the market-implied case

Open questions for the brainstorm, in the order they matter:

1. **What is "the market's" target?** Options: (a) the current price as the fair value of the median belief, which backs out one set of numbers at a chosen multiple; (b) the mean sell-side target ($179-182), which is 5-7% above the price; (c) the price plus the option-implied drift; (d) a probability-weighted price from the options surface (the Bloomberg workbook on OneDrive has the full 4 Sep chain with IV, ATM term structure to 12 months and 67 monthly straddles since 2021; the 5 Nov straddle will give the implied move and the skew the up/down asymmetry).
2. **Which multiple does the back-calculation hold fixed?** Backing revenue, nights and ADR out of a price needs a multiple and a margin; holding 16.5x and 36.2% and solving for revenue gives one answer ($15.6bn, i.e. the Literal case), holding the Street's revenue and solving for the multiple gives another (15.9x). WS12's finding that growth, not margin, moves the multiple (+0.48 turns per point of forward growth) means revenue growth and multiple are not independent, so the cleanest approach is a joint solve: find the revenue growth at which WS12's fitted multiple times the implied EBITDA equals today's EV.
3. **Decomposing revenue into nights, ADR, take rate and cancellations.** The market does not price these separately; it prices revenue and margin. The decomposition has to come from (a) Bloomberg FA's quarterly consensus for nights, GBV and ADR (3Q26 and 4Q26 only), (b) the prediction ledger of how the stock reacted to each component surprise at 23 prints (WS04/WS20: 71% of the print-day move is the multiple, the component betas are weak), and (c) the team's own elasticities (1pt of nights = ~$46m of 3Q26 revenue = ~1% of EBITDA). Cancellation rate is not observable and not priced separately; RNPL's effect shows only in the revenue-to-GBV gap.
4. **Up versus down asymmetry.** The 8-10 Sep fall (7.8% in three sessions, no company news beyond the fireside) is itself evidence about positioning. The 41-move study (7%+) and the executable-entry reaction ledger can give a base rate for the 5 Nov move conditional on the beat size; the options straddle gives the market's. The gap between them is the trade.
