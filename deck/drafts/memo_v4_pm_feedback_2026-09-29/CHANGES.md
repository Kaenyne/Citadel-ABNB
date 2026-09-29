# Memo v4: the 24 Sep memo rewritten for the PM's feedback (29 Sep 2026)

Written with Claude (Opus 5.5) on branch `claude/airbnb-pitch-narrative-kev6oi`, built on `krish/pitch-charts` @ 8dbf8d55.
**Numbers:** `deck/MEMO_UPDATE_2026-09-29.md` and `model/Caimanes_Citadel_ABNB_Model_v2.xlsx` are the source of truth. The target is
quoted as $120.

**Files in this folder:**

| File | What |
|---|---|
| `ABNB_Citadel_Pitch_Memo_v4.docx` | The memo in Word (Aptos 11pt, 0.5in margins, US Letter; same format as the 24 Sep memo) |
| `memo_v4_text.md` | The text the .docx is built from |
| `build_memo.js` | The builder |
| `BLIND_REVIEW.md` | The blind comparison against the 24 Sep memo |

**Charts:**

| Chart | Where | What |
|---|---|---|
| Graph 1 | `deck/Graphs/caimanes_model_v2/stylemd/graph2_nights_bundle_separated.png` | The team's v2 nights chart, unchanged |
| Graph 2 | `analysis/src/pitch_charts_pm/proof_chart.py` → `deck/Graphs/pm_feedback_v4/graph2_stays_index_proof.png` | New |

Captions go onto the images through `analysis/src/pitch_charts_pm/compose.py`.

**Rebuild, from the repo root:**

```
python analysis/src/pitch_charts_pm/proof_chart.py
python analysis/src/pitch_charts_pm/compose.py
NODE_PATH=<folder containing node_modules/docx> node deck/drafts/memo_v4_pm_feedback_2026-09-29/build_memo.js
```

**Page fit.**
- The fit was checked in LibreOffice, because Aptos is not installable here. The check was calibrated by rendering the 24 Sep .docx the same way.
- **Carlito**: the old memo renders to 2 pages ending at 745pt, which matches the real PDF. v4 ends at **705pt**.
- **Liberation Sans**, which is wider: both the old memo and v4 run 63pt onto a third page.
- So v4 is no longer than the memo that fit in Word. **Open it in Word and confirm two pages before sending.**
- Cut order if it spills:
  1. The "Macro no longer helps" last sentence.
  2. Risk 5.
  3. The fourth "no longer a growth company" bullet.

---

## 1. What the PM asked for, and what changed

| # | PM ask | What v4 does |
|---|---|---|
| 1 | More narrative and sales pitch, less numeric description, the "why" | The memo now reads as one argument: the call → the setup (2022–25 slowdown, the bundle) → why the market is wrong → why the bundle is an illusion → our proof → why Airbnb is no longer a growth company → margins → macro → catalysts → valuation → risks. The three "Thesis 1/2/3" evidence blocks are gone as headings. The ADR/FX detail (Street $177.06 vs straight line $177.07, −0.4pp FX, +1.0% ex-FX, mix −1.6pp) and the margin-bridge bars are cut from the text. |
| 2 | Story: 2–5 years of slowing growth → why the market disconnected (Street hugging guidance after beats) → proof it reconnects | "The Setup": nights +31.0 / +13.8 / +9.7 / +8.4% (2022–25), trough +7.4% (2Q25), the bundle, +10.3% (2Q26), stock +17.4% on the print, management stops sizing the bundle. "Why the market is wrong": 19 straight guide beats, all 28 estimates ≥+10.0% for 3Q26, LSEG FY27 revenue +11.7%, and the 23 Sep sell-off cut the multiple, not the estimates. "Our proof": the stays index. |
| 3 | Thesis opens with return, time frame, catalyst, and the fundamental truth the catalyst reveals | The Investment Thesis paragraph states: $120, −20.6%, 12 months; the truth (growth has slowed since 2022; 2026 was bought; underlying ~7% heading to ~6%); the path (5 Nov starts the reveal; February completes it; FY27 consensus converges through 2027); the size (FY27 revenue +7.5% vs +11.7%, EBITDA $4.89bn vs $5.83bn, −16%). |
| 4 | Graph 1 (both-guides-miss event study): n=5, regime, and it implies an 8% one-day trade that does not match a −20% 12-month target | **Dropped**, for four reasons, listed below the table. The PM's own concern survives as one sentence of mechanism in Catalysts: the three largest post-print falls (3Q22 −13.4%, 1Q23 −10.9%, 2Q24 −13.4%) all came on revenue beats with nights guided lower. That sentence carries no average, no hit rate and no trade claim. |
| 5 | A consistent catalyst path | November starts the reveal (nights print, a Q4 guide below the Street, the Q4 nights descriptor, the FY26 floor at risk; first FY27 cuts). February completes it (1Q27 guide against a +17.9% revenue comparison; FY27 margin outlook). Through 2027: ~6% prints bring the Street to our numbers. The same path appears in the thesis paragraph and in Catalysts. |
| 6 | Size, liquidity, low SI, a gradual decline | One sentence at the end of the thesis paragraph: "a liquid $89B large cap with low short interest… estimate cuts over several prints, not one binary event." |
| 7 | Briefly, why the bundle created an illusion of growth | A new paragraph: a level shift lifts the growth rate only until it laps (the lap dates); RNPL share has plateaued ("roughly 20%" → "over 20%"); cancellations arrive later (~22% implied). Net of cancellations, the bundle adds 1.4pt in 3Q26 and 0.1pt in 4Q26. |
| 8 | Make the stays index clear as the secret sauce | Its own paragraph, "Our proof: we count the stays that actually happen", plus a **new Graph 2**: out-of-sample predictions vs reported nights (1Q24–2Q26), the 3Q26 read with its band, our model and the Street range. |
| 9 | Macro tailwinds (rates, fuel) | Two sentences: the Fed hike, airfares, CoStar's 2027 RevPAR forecast, Booking's Q3 room-night guide. They are explicitly *not* leaned on, because dearer flights push travellers to drive-to stays, Airbnb's strongest segment (`research/notes/overnight/05_macro-outlook-and-transmission.md` §21; Third Bridge T5). The team also found the stock's sensitivity to the 10-year yield statistically zero (`09_stock-behaviour-and-alpha.md`), and higher rates raise Airbnb's interest income. The literal version of this ask would hand a judge an easy rebuttal. |
| 10 | Why Airbnb is not a growth company anymore | A new section with four causes: growth from new homes, not demand per home; North America saturated, with growth shifting to low-ADR regions; rising S&M intensity with falling revenue per S&M dollar; regulation plus small new businesses. |
| 11 | Risks, rigorously dismissed: AI agent, buyback, loyalty/ads | Five numbered risks. **AI:** absent from every AI booking channel so far; partnering means paying for distribution it now gets free; the filed savings are small and being reinvested. **Buyback:** conceded as likely, dismissed on mechanics. **Loyalty/ads:** no program; incentives already weigh on take rate; ads are sized against our EBITDA gap. **Plus** the flip rule and the February timing risk. |

**Why Graph 1 was dropped (row 4).**
- The chart says "5 of 5 fell". That is true only against QQQ. In absolute terms 1Q25 rose +1.0%, so it is 4 of 5. The team had already logged this correction on 17 Sep (`docs/pitch-forecasts/MEMO_CHANGES.md` row 6).
- It belongs to the guide-below-Street family on the kill list (AGENT_BRIEF §6). On the executable next-open convention, the day-1 effect is 3 of 9 negative, mean +0.9% (`data/processed/overnight/20_convention_restatement.csv`).
- The team's joint reaction model puts that cell at a −5.1% median, not −8%.
- It frames a one-day trade, which the PM says does not fit a 12-month −20% target.

**Other changes:**
- **Header:** $120 / −20.6% / $89.3B (workbook Cover: 589.6M shares × $151.39); adds the horizon and EV/NTM EBITDA; drops "R/R 2:1", which has no source.
- **Company overview:** dropped. The segment split was description, not argument.
- **Thesis 2 and 3 numbers** moved to the v2 workbook: nights 9.20 / 7.27%, FY27 +6.4%, margins 34.6 / 34.9 / 32.6%, Street FY27 36.8%.
- **Valuation:** reworded as the update pack suggests (three multiples, $117–123, target $120). One sentence adds why 1.5 turns of compression is conservative.

## 2. Numbers that are new to the memo, and their sources

| Claim | Number | Source |
|---|---|---|
| Street FY27 revenue growth | +11.7% | Workbook Cover K24 $15,846.1M ÷ FY26 Street ($6,286M 1H26A + $4,744.3M + $3,161.8M = $14,192.1M) − 1 = 11.65% |
| Our FY27 revenue growth | +7.5% | Workbook: $15,022.4M ÷ FY26 $13,973.4M − 1 = 7.51% |
| Growth gap used in the valuation sentence | 4.1pts | 11.65 − 7.51 |
| FY27 EBITDA vs Street | $4.89bn vs $5.83bn, −16% | Update pack §3 |
| Annual nights growth | +31.0 / +13.8 / +9.7 / +8.4% (2022–25) | `research/notes/overnight/11_competition-supply-and-overlays.md` lines 37–40 (filings) |
| Quarterly trough | +7.4% (2Q25) | Workbook `Income_Statement` K5 |
| Five straight quarters of re-acceleration; +10.3% (2Q26) | | Workbook `Income_Statement` K5–O5 |
| Stock on the 2Q26 print | +17.4% | `data/processed/abnb_guidance_reaction_panel.csv` (2Q26, ret_1d) |
| Underlying growth | 7.1% (1Q26), 6.8% (2Q26) | Update pack §4 |
| Bundle sizes | "over 200 basis points" (4Q25), "approximately three points" (1Q26) | `data/processed/overnight2/D/rnpl_statement_ledger.csv` D014, D032. **Call transcripts only**; no SEC filing carries them (WORKBOARD corrections, 18 Sep). Verify against the IR replay. |
| Revenue-guide beats | 19 straight | `abnb_revenue_guidance_vs_actual.csv` via memo v3 |
| 28 Bloomberg estimates | low 147.0m = +10.03% on 3Q25's 133.6m; mean +11.5% | `data/processed/forecast_methods/reviews_index_v2/stage_e_view_vs_street.csv` (MODL, 12 Sep) |
| 23 Sep sell-off | −7.6% (close $149.58), Expedia–Meta Muse integration announced 22 Sep | Press (24/7 Wall St, TravelPulse). **Secondary sources**; primary pages blocked in this session. Verify. |
| LSEG FY27 unchanged on 23 Sep | $15,818M / $5,763M | `docs/margin-build/notes/45_ai_margin.md` (branch `krish/cost-leg`) |
| RNPL share | "roughly 20%" (1Q26 letter), "over 20%" (2Q26 call) | Ledger D031, D043 |
| RNPL cancellation rate | ~22%; platform "maybe 16%… going to 17%"; "higher cancellation rates" | Ledger D018; 2Q26 10-Q; `deck/drafts/thesis1_rnpl_v1_2026-09-23.md`. The update pack notes the ~22% assumes RNPL averages ~17% of nights. |
| Net bundle | 1.4pt (3Q26), 0.1pt (4Q26) | Update pack §4 |
| Stays index | 75M reviews, 123 cities; attrition 15–16% a year; 5.99% covered-city growth; +8.9% ±1.9pp; mapping frozen 1Q23–2Q25 | Update pack §4; `stage_c3_3q26.json`; `docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md` |
| Stays index error vs naive | ~0.7x | `stage_b_walkforward.csv`: yoy_vmatch_mix level ratio 0.723 on both W1 (n 14) and W2 (n 10). **Diebold–Mariano p ≈ 0.22–0.26**, 90% intervals reach 1.08 / 0.97. Say "about 0.7x", never "significant". |
| External stack | +9.2%; STR RevPAR +8.2% July → ~4% mid-August | `deck/drafts/thesis2_nights_adr_v1_2026-09-23.md`; `research/notes/q3nowcast/G_external-sources-q3-read.md` |
| P(print ≥ Street) | 8% | Workbook `Nights_Engine!X90` (update pack §2) |
| Nights per active listing | ~62.6, 2022–25 | `11_competition…md` lines 106–117. Team calculation. |
| Same-listing stays | −3% to −7% y/y (2026) | `research/notes/q3nowcast/E_reviews-stays-index.md` line 27 (−3.3% 2Q26, −7.4% July); memo v3 |
| North America share of nights | 39.8% (1Q22) → ~29% | `research/notes/overnight/10_regional-and-segment-decomposition.md` |
| FY25 ADRs | NA $255, LatAm $95, APAC $118 | FY25 10-K via `research/notes/overnight2/C_consumer-relative-strength-regional-split.md` line 117 |
| LatAm + APAC share of growth | "over half" (52% of 2Q26 growth) | `10_regional…md` line 13 |
| Cash S&M | 16.5% of revenue (FY23) → 19.4% (FY25) | `data/processed/abnb_quarterly_cost_stack_exsbc.csv`; note 43. The 24 Sep memo's "16.5% FY23 → 23.9% 1H26" compared a full year with the seasonally heavy half, so v4 uses full years. |
| Revenue per incremental S&M dollar | $6.6 (FY23) → $2.7 (1H26) | `43a_h3_by_year.csv` via `deck/drafts/thesis3_margins_v1_2026-09-24.md`. It is a ratio, not a return. |
| Spain | 65,122 listings removed | `research/regulatory/factor_register.md` lines 19–35 (2Q26 10-Q) |
| Barcelona | Licences lapse Nov 2028 | `factor_register.md` lines 409–424 |
| Hotels | Single-digit share of nights | Management, `docs/pitch-forecasts/questions/risk-new-businesses-quantified-material/README.md` |
| Ad revenue | Zero | `11_competition…md` line 274 |
| Macro | Fed hike 16 Sep; CPI airfares +25.5% y/y (July); CoStar RevPAR +4.4% (2026) → +2.1% (2027); Booking Q3 room nights +3–5% | `docs/pitch-forecasts/questions/bonus-interest-income-falls/README.md` line 23; `research/notes/overnight/05_macro-outlook-and-transmission.md` lines 202–251 |
| Three largest post-print falls | 3Q22 −13.4%, 1Q23 −10.9%, 2Q24 −13.4%; nights guided lower in each | `abnb_guidance_reaction_panel.csv` (ret_1d, nq_nights_dir); revenue beats per memo v3 |
| February letters | A full-year margin outlook every year since Feb 2023 | `data/processed/overnight/02_guidance_ledger.csv` lines 58–175 |
| February print day-1 returns | Up in 5 of 6 years | Reaction panel: 4Q20 +13.3, 4Q21 +3.6, 4Q22 +13.4, 4Q23 −1.7, 4Q24 +14.4, 4Q25 +4.6 |
| Multiple-growth slope | ~0.5 turns per point | `data/processed/forecast_methods/valuation_v1/regression_reproduction.csv`: 0.486 on 12-month changes in EV/**LTM** (both windows, descriptive only). The NTM-level version fails W2, so it is quoted as "~0.5" and as support for "conservative", not as the target's basis. |
| AI channels | Not a ChatGPT Apps launch partner (Oct 2025; Chesky "not quite ready"); not a Google AI Mode hotel-booking partner (27 Aug 2026; Booking, Expedia, Marriott, Hilton are); no Muse deal (Expedia's announced 22 Sep) | Press: Bloomberg / CNBC 21–22 Oct 2025; Skift / PhocusWire 27 Aug 2026; TravelPulse 22 Sep 2026. **Secondary sources**; also `11_competition…md` lines 196–218 |
| Agent "next year" | | Skift, 23 Sep 2026 (secondary) |
| ~90% direct or unpaid traffic | | Management (repeated since 2020); `hotel_loyalty_stickiness_vs_abnb.md` lines 73–84 (in `citadel-abnb-hotel-loyalty.zip`) |
| AI $17M vs S&M +$184M; "reinvest most…"; "a material increase" | | 2Q26 10-Q and calls via `45_ai_margin.md` §2 |
| Buyback: ~$2.3bn left at 5 Nov; ~$1.1bn a quarter; authorizations announced in print-day letters | | `docs/pitch-forecasts/questions/risk-buyback-upsize/research-log.md` lines 36–47 |
| ~5% of shares a year | | ~$4.4bn ÷ $89.3bn |
| SBC | $1.6bn (FY25), over a third of buybacks | `research/notes/2026-09-05_capital-return-panel.md` line 11 (FY25 buybacks ~$3.8bn) |
| Authorization-day returns | +5.2%, +2.2%, +0.2%, −1.0% | research-log line 38 |
| Buying fell to $857M after the Aug 2025 drop | | research-log line 42 |
| Take rate "relatively flat" on "higher customer incentives related to new businesses" | | `research/notes/2026-09-12_management-implied-model.md` line 42 |
| Ads | Analysts expect a 2027 launch (Wells Fargo, Wedbush); team bull FY27 ads $250M; 70% incremental margin | `11_competition…md` lines 265, 274; `model/assumptions.md` lines 66–67 |
| FY27 EBITDA gap | $0.93bn | 5,826.4 − 4,894.7 |

## 3. Open items for the team before 2 Oct (not decided here)

1. **SI 3.59%** has no source in the workbook or the update pack. Web checks this session found 2.2%–3.4% (Aug–Sep settlements), none confirmed current. Re-pull it, and add days to cover if there is room.
2. **Price.** The memo still uses $151.39 (24 Sep), per the update pack. The stock was ~$156 on 28 Sep (press, unverified). Re-stamp the price and implied return on submission day.
3. **The reverse-DCF problem the 24 Sep memo had.**
   - Its "FY27 nights +6.6% vs market expected 8.9%" used a market-implied figure computed at **$170.19**. At ~$150 the same method implies ~4.7% (`data/processed/reverse_dcf/A/A_headline.csv` lines 2 and 4).
   - v4 drops that comparison and argues against Street *estimates* (FY27 revenue +11.7%, EBITDA $5.83bn), which the workbook has.
   - Expect a judge to ask "isn't your view priced after the 23 Sep drop?" The answer is in "Why the market is wrong": the drop cut the multiple, not the estimates.
4. **3Q26 underlying nights in Graph 1 is 7.8%**, above 2Q26's 6.8%. It is the residual of an all-in 9.2% (update pack §0), so the chart shows the "underlying" re-accelerating in the quarter we call a slowdown. The text says "~7% heading to ~6%", which matches 3Q26–4Q27 on average (7.8, 7.2, 6.7, 6.4, 6.2, 6.0). A judge may still ask. The team decides whether the residual belongs in underlying or in a separate "other" segment.
5. **Bundle magnitudes** (">200bp", "~3 points") are call-transcript quotes only. Verify them against the IR replay (WORKBOARD corrections, 18 Sep).
6. **Sources press-verified only:** the 23 Sep sell-off, the Muse / AI Mode / ChatGPT facts, and Chesky's "next year". Primary pages were blocked by the proxy in this session.
7. **"R/R 2:1"** was removed because nothing supports it. If the team wants a risk/reward figure, it needs a defined upside case (e.g., the $178 post-print close) or a stop.
8. **Chesky's "$1bn straight shot"** is deliberately not quoted. The repo tags it once as host/seller services (`05_statements.csv` line 374) and once as sponsored listings (`management-implied-model.md` line 27). Check the Communacopia transcript before using it in Q&A.
