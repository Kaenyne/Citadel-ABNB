# Memo update pack — 29 Sep 2026

This file lists everything the two-page memo needs to match the team model as it stands. It is written for a session that can see
only this GitHub branch. Branch: **`krish/pitch-charts`**. Every number below was read from
`model/Caimanes_Citadel_ABNB_Model_v2.xlsx` by script, not retyped. The current memo is `model/ABNB Citadel Pitch Memo.docx` / `.pdf`
(24 Sep, v1 numbers), committed here unchanged.

---

## 0. What changed and why (28–29 Sep decisions, all by Krish)

1. **The team model is the source of truth**: `model/Caimanes_Citadel_ABNB_Model.xlsx` (v1, unchanged). The short-case
   variants built along the way ($108, then $128; `analysis/src/pitch_charts/short_case_inputs.py`, branch `krish/cost-leg`
   package 48) are superseded and kept only for the record. Do not quote them.
2. **v2 = v1 + two edits** (`model/Caimanes_Citadel_ABNB_Model_v2.xlsx`, made in Excel, full recalculation):
   - **3Q26 nights = 9.2% y/y, all-in** (Thesis 2's final estimate). Input cell `Nights_Engine!B77`. The 3Q26 "underlying" cell
     `X79` is now the residual `=$B$77-SUM(X80:X82)-X91`. The figure is all-in because the stays-based reads behind 9.2% already
     net out cancellations. Subtracting cancellations again would double-count.
   - **RNPL cancellations are in the base case** (Thesis 1). `Nights_Engine` row 91, added into the base print sum (row 83).
     The values are the cohort engine's central cell: management-implied +6pt cancellation rate on RNPL bookings (16%→17%
     platform), 25% rebooked, lead 2.2, ADR +25%. That gives **−0.93pt 3Q26, −0.85pt 4Q26** (source `overnight2/D/D1_rnpl_cohort_scenarios.csv`).
     The 2027 values are the cohort tail's base-case shape scaled ×1.566 (the 4Q26 ratio): −0.39, −0.21, −0.11, −0.05. The 2027 values
     are an assumption; the 2026 values come straight from the engine.
   - A display fix: `ADR_Engine` rows 120–129 ("alternatives carried beside the base") showed GBV frozen at v1 nights. Those cells
     are now live formulas (model nights × each rule's ADR). Nothing else reads them.
3. **World Cup stays at +0.5pt in 2Q26** (lapped −0.5 in 2Q27). This is a team decision. Host-market reviews measure ~0.1pt (PR #68).
   Do not put both numbers in the memo.
4. **Street FY27 margin = 36.8%**: the sum of the four LSEG quarterly estimates (13 Sep), the same basis the workbook uses. The memo's 36.4%
   was LSEG's annual-row mean.

---

## 1. Headline numbers (v2)

| | v1 (memo today) | **v2** |
|---|---|---|
| Stock price (24 Sep) | $151.39 | $151.39 |
| **Target price** | $122 (Cover E35) | **$120.19 → quote $120** (Cover E35) |
| Implied return | −19.4% (memo header says "20%") | **−20.6%** |
| Cover headline cell A2 (average without the −$0.70) | $122.7 | $120.89 |

**How the target is built (Cover rows 31–36).** Three EV-based prices: consensus multiple less a haircut, applied to our EBITDA,
+ cash $12,069M − debt $2,476M, ÷ 589.6M shares.

| Multiple | Ours | Consensus | Target multiple | Target price v2 (v1) |
|---|---|---|---|---|
| EV / NTM EBITDA (3Q26–2Q27) | **17.03x** (16.81x) | 14.93x | 13.43x (= consensus − 1.5) | $122.81 ($124.17) |
| EV / 4Q26 EBITDA | 98.16x (95.78x) | 87.19x | 77.19x (= consensus − 10) | $122.53 ($125.17) |
| EV / FY27 EBITDA | 16.28x (16.05x) | 13.67x | 12.17x (= consensus − 1.5) | $117.33 ($118.76) |
| Average | | | | $120.89 ($122.70) |
| **E35 = average − $0.70** | | | | **$120.19 ($122.00)** |

The memo's valuation sentence says the target comes from "13.43x NTM EBITDA". On its own that multiple gives $122.81. The target
is the average of the three prices less a $0.70 haircut, so reword the sentence (suggestion in §6).

---

## 2. Quarterly numbers (v2; $M unless stated; Street = LSEG 13 Sep, Street nights = Bloomberg 12 Sep)

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| **Nights (m)** | **145.89** | **130.76** | 168.41 | 156.78 | 154.78 | 138.52 |
| Nights y/y | **9.20%** | **7.27%** | 7.82% | 5.72% | 6.09% | 5.93% |
| Street nights (m) / y/y | 149.0 / 11.53% | 134.0 / 9.93% | — | — | — | — |
| ADR ($) | 175.66 | 170.96 | 187.91 | 185.59 | 177.88 | 173.47 |
| ADR y/y (ex-FX / FX, pp) | 2.55% (2.96 / −0.41) | 2.06% (2.43 / −0.37) | 0.58% (0.95 / −0.37) | 1.02% (1.44 / −0.43) | 1.26% | 1.47% |
| Street ADR ($) | 177.06 | 171.33 | — | — | — | — |
| GBV ($bn) | 25.63 | 22.35 | 31.65 | 29.10 | 27.53 | 24.03 |
| **Revenue** | **4,608.7** | **3,078.7** | 2,902.3 | 3,859.9 | 4,951.1 | 3,309.2 |
| Street revenue | 4,744.3 | 3,161.8 | 3,010.3 | 4,036.9 | 5,270.0 | 3,528.9 |
| ours vs Street | −2.9% | −2.6% | −3.6% | −4.4% | −6.1% | −6.2% |
| **Adj. EBITDA** | **2,232.1** | **811.6** | 420.3 | 1,214.7 | 2,430.6 | 829.1 |
| Adj. EBITDA margin | 48.43% | 26.36% | 14.48% | 31.47% | 49.09% | 25.05% |
| Street adj. EBITDA | 2,361.5 | 913.7 | 610.7 | 1,451.7 | 2,695.6 | 1,068.4 |
| Street margin | 49.78% | 28.90% | 20.29% | 35.96% | 51.15% | 30.28% |
| Diluted EPS | 2.65 | 0.64 | 0.11 | 1.16 | 2.97 | 0.61 |
| Street EPS (Cover) | 2.85 | 0.86 | 0.39 | 1.53 | — | — |

v1 for comparison: nights 9.89 / 8.12 / 8.20 / 5.93 / 6.21 / 5.98%; revenue 4,637.6 / 3,103.1; EBITDA 2,257.2 / 831.8; EPS 2.68 / 0.67.

Probabilities the workbook computes: P(3Q26 nights print ≥ Street) = **0.08** (`Nights_Engine!X90`); P(3Q26 ADR ≥ Street) =
0.21, P(4Q26 ADR ≥ Street) = 0.45 (`ADR_Engine` row 102).

## 3. Full-year numbers (v2)

| | FY26 | FY27 |
|---|---|---|
| Nights (m) / y/y | 581.15 / +9.0% | 618.49 / **+6.4%** (v1 6.6%) |
| Revenue | 13,973.4 | 15,022.4 (Street 15,846.1: **−5.2%**; v1 −4.7%) |
| Adj. EBITDA | 4,823.7 | **4,894.7** (Street 5,826.4: −16.0%) |
| Adj. EBITDA margin | **34.52%** (Street 35.62%) | **32.58%** (Street **36.77%**) |
| Margin if costs follow the Street's plan, flexed down with our revenue (k 0.364) | **34.94%** | **34.56%** |
| Diluted EPS | — | 4.86 (Street 6.24) |
| Cash cost growth, ours | +14.9% | +10.6% |
| Cash cost growth the Street implies | +15.0% | **+9.7%** |

FY26 misses management's "at least 35.5%" floor both on our costs (34.5%) and on the Street's own cost plan flexed (34.9%).

---

## 4. Nights: what each quarter is made of (Graph 2 data: `data/processed/pitch_charts/n07_nights_caimanes.csv`)

| pp | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Underlying (ex bundle) | 7.82 | 7.21 | 6.66 | 6.43 | 6.21 | 5.98 |
| Product bundle still live (RNPL, 14-day cancellation, host-only fee) | +2.31 | +0.91 | +0.54 | 0 | 0 | 0 |
| **RNPL cancellations** | **−0.93** | **−0.85** | −0.39 | −0.21 | −0.11 | −0.05 |
| World Cup | 0 | 0 | 0 | −0.5 (lap) | 0 | 0 |
| Middle East | 0 | 0 | +1.0 (lap) | 0 | 0 | 0 |
| **Total** | **9.20** | **7.27** | **7.82** | **5.72** | **6.09** | **5.93** |

History (reported; bundle split by leg): 3Q25 8.8 (bundle 0.7), 4Q25 9.8 (2.2), 1Q26 9.2 (3.0; Middle East −1.0), 2Q26 10.3 (3.0; World
Cup +0.5); underlying ~7% (7.1 in 1Q26, 6.8 in 2Q26).

The bundle laps it by leg (workbook `Nights_Engine` rows 80–81, "backed out" in Thesis 2): fee/cancellation −0.78 (4Q26), then
−0.74; ex-NA RNPL −0.36 (1Q27), then −0.91. Combined: **0.8pt 4Q26, 1.1pt 1Q27, 1.6pt from 2Q27**. The US RNPL leg laps in 3Q26.

Net bundle after cancellations (Thesis 1's framing): 2.31 − 0.93 = **1.4pt in 3Q26**; 0.91 − 0.85 = **~0.1pt in 4Q26**.

3Q26 evidence in the workbook (`Nights_Engine` block D/E): stays index 5.99% for covered cities (composite QTD 5.90%) → 8.92% global
via the frozen two-parameter mapping (±1.85pp band). With the RNPL option term it reads 9.41% (mean gap) and 10.47% (largest gap).
Thesis 2's final 9.2% sits inside that range.

---

## 5. Margin bridge, Street → our model (Graph 3 data: `data/processed/pitch_charts/r07_margin_bridge_caimanes.csv`)

Method: Street margin, then our revenue with the Street's costs flexed at the historical rate (0.364% of costs per 1% revenue),
then each cost line against the Street's plan (spread at one growth rate on the prior-year base).

| pp | 3Q26 | 4Q26 | FY27 |
|---|---|---|---|
| Street consensus | 49.78% | 28.90% | 36.77% |
| Lower revenue (costs flex down) | −0.94 | −1.22 | **−2.21** |
| Sales & marketing | −2.28 | −1.72 | **−1.29** |
| Hosting & AI compute | −0.78 | −1.23 | **−0.63** |
| AI support savings | +0.25 | +0.32 | **+0.20** |
| Ops & support: payroll, other | +0.48 | +0.32 | −0.05 |
| Payments & other cost of revenue | +0.75 | +0.46 | −0.11 |
| Product development (incl. $30M FY27 AI tooling) | +0.52 | +0.14 | −0.26 |
| G&A | +0.66 | +0.40 | +0.16 |
| **Our model** | **48.43%** | **26.36%** | **32.58%** |

The AI items in the workbook: support cost per booking −14% (2H26) / −10% (FY27) (`Income_Statement` B62:B63), hosting & AI compute $224M
a year (FY25) → $330M (FY27) (B57:B59), and $30M of FY27 PD AI tooling (B68). Graph 3 shows lower revenue, S&M, hosting & AI compute and AI support
savings separately; the other four lines are folded into "Other costs (net)".

---

## 6. Memo, line by line (current text → replacement)

**Header.** "Target Price: $122 | Implied Return: 20%" → **"Target Price: $120 | Implied Return: −20.6%"**. Mkt cap: the memo has
$88.19B; the workbook Cover has $89.26B (589.6M shares × $151.39). Pick one share count. R/R 2:1 and SI 3.59% are not in the workbook
and have no source here.

**Investment Thesis.** "(2) 2026 World Cup surge masks decelerating nights" is fine now that the team keeps +0.5pt, but the World
Cup is only 0.5pt of the ~3pt story. Suggested: "(2) Nights print below consensus as the product bundle laps and RNPL cancellations
land: we have 3Q26 at +9.2% and 4Q26 at +7.3% against the Street's +11.5% and +9.9%."

**Market/Variant View.**
- "4Q26 nights at a growth rate of +11.45% (range of 9.9% to 12.5%)". The +11.5% is the Street's **3Q26** figure; 4Q26 is +9.9%.
  The 9.9–12.5% range has no source in this pack; check it before quoting.
- "we price ABNB nights at 9.89% YoY on 3Q26, 8.12% 4Q26, and 8.21% 1Q27" → **"9.20% on 3Q26, 7.27% 4Q26, and 7.82% 1Q27"**.
  Consensus "11.53%, 9.93%, and 9.62%": the first two are in the workbook; the 1Q27 9.62% is not (workbook has no Street nights after
  4Q26). Keep its source to hand.
- "ABNB has fallen 9 of 19 times after beating revenue" and "5 of 5 (Graph 1)" are unchanged (history).

**Thesis 1.** Everything up to "those cancellations cost 0.9pt in 3Q26" now matches the model (0.93pt). Replace the last sentence:
"The bundle falls from ~3pts to ~1.4 nights growth contribution, then ~0 in 4Q26: leading to a bear case ~7% nights growth vs the
Street's +11.53%" → **"Net of cancellations the bundle falls from ~3pts to ~1.4pt in 3Q26 and ~0.1pt in 4Q26, taking nights
growth to +9.2% in 3Q26 and +7.3% in 4Q26 against the Street's +11.5% and +9.9%."** (It is no longer a bear case; it is the base
model. The old sentence also compared a 4Q26 number with a 3Q26 Street figure.) The implied 22% RNPL cancellation rate assumes RNPL
averages ~17% of nights over the period (16% × 0.83 + 22% × 0.17 ≈ 17%); say so if challenged.

**Thesis 2.**
- "Our Q3 and Q4 nights model projects +9.2% and +8.1% YoY" → **"+9.2% and +7.3%"**.
- Stays index 5.99%, two-parameter model 8.9%, range 8.0–9.9%, final 9.2%: all match the workbook.
- "The three-bundle contribution is backed out ... reductions of 0.8pts in 4Q26, 1.1pts 1Q27, and 1.6pts from 2Q27 onward, arriving
  at a final FY27 nights growth of 6.6%" → keep the laps. Add the cancellations and change the total: "... and Thesis 1's RNPL cancellations
  (0.9pt in 3Q26 and 0.8pt in 4Q26, fading through 2027) come off, arriving at FY27 nights growth of **6.4%**".
- "versus the market expected 8.9%": the FY27 consensus nights figure is not in the workbook. Keep its source.
- ADR: Street $177.06, ours $175.66, FX −0.4pp, +1.0% ex-FX by 1Q27 (0.95), mix −1.6pp (1Q27 −1.62): all match. "A simple currency
  straight line gives ($177.07)" and "+0.4pp" are not in the workbook; keep their source. "the bundle's ~1pt ADR lift nets out with
  cancellations": the ADR engine only laps the bundle and has no cancellation term. Suggested: "the bundle's ~1pt ADR lift laps".

**Thesis 3.**
- "The Street's expected FY27 margin (36.4%, up from 35.6%)" → **"(36.8%, up from 35.6%)"**.
- "needs cost growth to slow from ~15% to 10%": holds (15.0% → 9.7%).
- "$17M ... S&M rose $184M", the management quotes, and "S&M has outgrown revenue for nine quarters (16.5% ... 23.9%)" all come from filings
  and are unchanged.
- "hosting and AI compute take 59bp of margin while AI support savings return 20bp" → **"take 63bp ... return 20bp"**.
- "Our forecasted 2.5% lower FY27 revenue" → **"5.2% lower"**.
- "FY27 margin is 35.4% and FY26 35.4%, below the 'at least 35.5%' management floor" → **"FY27 margin is 34.6% and FY26 34.9%"**.
- "On our cost, FY27 is 34.0% ($5.24bn EBITDA vs $5.77bn)" → **"32.6% ($4.89bn EBITDA vs $5.83bn)"**.

**Valuation.** "On our numbers ABNB trades at 16.81x NTM EBITDA, while consensus numbers imply 14.93x ... we value ABNB at 13.43x NTM
EBITDA ... target price of $122" → suggested: **"On our numbers ABNB trades at 17.0x NTM EBITDA against 14.9x on consensus. Applying
compressed multiples to our estimates (13.4x NTM, 12.2x FY27 and 77.2x 4Q26 EBITDA, each 1.5–10 turns below consensus) gives $117–123
a share; our target is $120, 20.6% below today's $151.39."** (If the team drops the −$0.70 haircut in E35, the target is $120.89.)

**Catalysts / Risks.** No numbers change. Risk 1 (spending cuts): FY26 is 34.5% on our costs, so holding the 35.5% floor would take roughly $140M
of 2H26 cost cuts. Mention it if space allows.

---

## 7. Known workbook issues (fix or avoid quoting)

1. **Cover E35 subtracts a hand −$0.70** (`=AVERAGE(E32:E34)-0.7`) while A2 shows the average without it; the Cover's
   downside cell (E36, −20.6%) uses E35. Quote one number and say which.
2. **Cover "Our Model vs Consensus" table, "2Q27" columns**: Revenue (4,951.1 vs 5,270.0) and Nights (154.78) are **3Q27** values.
   EBITDA (1,214.7 vs 1,451.7) and EPS (1.16 vs 1.53) there are genuinely 2Q27. True 2Q27 revenue is 3,859.9 vs 4,036.9 (−4.4%).
   The same bug is in v1.
3. The market cap mismatch in §6 (the Cover uses 589.6M shares; the income statement's diluted shares are 591.7M for 3Q26).

---

## 8. Charts for the memo (all rebuilt from v2)

Two looks, same numbers. Pick one set:

- `deck/Graphs/caimanes_model_v2/refined/`: Airbnb look, "Graph N:" titles, captions on the image.
- `deck/Graphs/caimanes_model_v2/stylemd/`: STYLE.md look (`STYLE.md` at repo root). The takeaway and source lines go in the document;
  the text is in `deck/Graphs/caimanes_model_v2/stylemd/DOC_CAPTIONS.md`.

| File | Shows | Numbers on it |
|---|---|---|
| `graph1_both_guides_miss.png` | Day-1 return vs QQQ by guide group | both guides missed: 5 of 5 fell, −8.0% average (n 5, 3, 4, 6) |
| `graph2_nights_bundle_separated.png` | Nights y/y 1Q25–4Q27, bundle / cancellations / World Cup / Middle East | §4; Street 11.5 / 9.9 |
| `graph3_margin_bridges.png` | Street → ours, 3Q26 / 4Q26 / FY27 | §5 (folded to 5 steps) |

Superseded chart sets, kept for the record (do not use): `deck/Graphs/short_case`, `short_case_128`, `caimanes_model` (v1). The
originals the 24 Sep memo used are `deck/Graphs/download (1–5).png` and `image.png`.

Rebuild: `py -3.13 analysis/src/pitch_charts/caimanes_inputs.py`, then `Rscript analysis/src/pitch_charts/two_pager_refined.R`
and `two_pager_stylemd.R` (see `analysis/src/pitch_charts/README.md`).

---

## 9. File index (everything the rewrite might need, on this branch)

| Need | Path |
|---|---|
| Team model v2 (use this) / v1 | `model/Caimanes_Citadel_ABNB_Model_v2.xlsx` / `model/Caimanes_Citadel_ABNB_Model.xlsx` |
| Current memo (24 Sep, v1 numbers) | `model/ABNB Citadel Pitch Memo.docx`, `.pdf` |
| Thesis drafts and earlier cut notes | `deck/drafts/thesis1_rnpl_v1_2026-09-23.md`, `thesis2_nights_adr_v1_2026-09-23.md`, `thesis3_margins_v1_2026-09-24.md`, `two_pager_cuts_2026-09-24.md` |
| Earlier memo versions | `deck/drafts/memo_v3_short_2026-09-17.md` (and v0–v2) |
| Charts + captions | `deck/Graphs/caimanes_model_v2/` |
| Chart data (CSV) | `data/processed/pitch_charts/n07_nights_caimanes.csv`, `r07_margin_bridge_caimanes.csv`, `s04_two_gates.csv` |
| Chart code | `analysis/src/pitch_charts/` |
| Chart style guide | `STYLE.md` |
| Research behind the theses (on `main`, also here) | `docs/pitch-forecasts/SYNTHESIS.md`, `docs/q3nowcast/SYNTHESIS.md`, `docs/adrv3/SYNTHESIS.md`, `docs/overnight2/SYNTHESIS.md` (RNPL cohort engine), `docs/reverse_dcf/SYNTHESIS.md` |
| Margin work behind Thesis 3 (branch `krish/cost-leg`) | `docs/margin-build/notes/43_thesis3_integration.md`, `43a_sm_evidence.md`, `43b_valuation_link.md`, `45_ai_margin.md`; bridge code `analysis/src/margin_build/46_margin_bridge/run.py`; superseded $128 case `analysis/src/margin_build/48_short_case_v3/README.md` |
