# Memo v4.1: review of v4 against the PM's feedback, new Graph 1, two-page fit (29 Sep 2026)

Built on `claude/airbnb-pitch-narrative-kev6oi` @ 723b33ec (memo v4). v4's folder
(`deck/drafts/memo_v4_pm_feedback_2026-09-29/`) is unchanged. This folder holds the v4.1 text, builder, .docx and the PDF Word exported.

## Rebuild, from the repo root

```
Rscript analysis/src/pitch_charts_pm/graph1_history.R
python analysis/src/pitch_charts_pm/compose_v4_1.py
NODE_PATH=<folder containing node_modules/docx> node deck/drafts/memo_v4_1_2026-09-29/build_memo.js
```

Page fit was checked **in Microsoft Word with Aptos** (COM export to `ABNB_Citadel_Pitch_Memo_v4_1.pdf`). The PDF is 2 pages and
page 2 ends at 740pt of 756pt. v4 exported the same way came to **3 pages**, about 130pt over. v4's LibreOffice/Carlito check
missed that.

## 1. Correction to v4's CHANGES §3.3: the "market expected 8.9%" FY27 nights

v4 said the 24 Sep memo's "FY27 nights +6.6% vs market expected 8.9%" was a reverse-DCF, market-implied figure computed at
$170.19. It then dropped the comparison. **That is wrong.** The team pulled the 8.9% from Bloomberg as the FY27 nights consensus;
it was not derived from the stock price. The reverse-DCF run also produces a +8.9% at $170.19
(`docs/reverse_dcf/RUN_STATE.md`), which is probably how the two got confused.

v4.1 puts the comparison back as a Street estimate, in "Why the market is wrong" and on Graph 1: "For FY27, Bloomberg consensus
has nights at **+8.9%** (ours **+6.4%**)". Our FY27 figure is model v2's +6.4%, not the 24 Sep memo's +6.6%.

**Still open:** the Bloomberg pull date and the number of estimates. The 8.9% is in no repo file (the update pack says the
workbook has no Street nights after 4Q26). Add the date to the Graph 1 source line and to the L0 vintage register before
submission, per the point-in-time rule.

## 2. Graph 1 changed: from the 1Q25–4Q27 bundle chart to 1Q23–4Q27 history

v4 had already dropped the old Graph 1 (the n=5 "both guides miss" event study the PM questioned) and promoted the nights-bundle
chart. That chart began in 1Q25, so it could not show the story the memo now tells: slowing growth since 2022, a re-acceleration
the bundle bought, then reversion. The new chart (`graph1_history.R`, team STYLE.md look, same colours):

- Quarterly nights y/y from **1Q23**: 18.6 → 11.0 → 13.5 → 12.0 → 9.5 … 7.4 (2Q25), from reported nights
  (`abnb_quarterly_kpis_from_study.csv`), then the model v2 split from `n07_nights_caimanes.csv` unchanged.
- Full-year strip above the bars: FY23 +13.8, FY24 +9.7, FY25 +8.4, FY26E +9.0, **FY27E +6.4**. The script checks these
  against the memo's +13.8 / +9.7 / +8.4.
- Street: 3Q26 11.5 and 4Q26 9.9 (Bloomberg, 12 Sep), plus the **FY27 8.9** line across the 2027 quarters.
- Takeaway: "Nights growth has slowed since 2023; the bundle bought 2026's bump; 2027 fades to ~6% vs the Street's 8.9%".

## 3. Text changes from v4 (all to fit two pages, except the first)

| Where | Change |
|---|---|
| Why the market is wrong | Adds the Bloomberg FY27 nights +8.9% vs ours +6.4% (§1). Drops "an acceleration from 2Q26". |
| Header | Drops "EV/NTM EBITDA 14.9x/17.0x" (it is in Valuation). "Implied Return … Horizon: 12M" becomes "12M Return". The header now fits on one line. |
| Illusion paragraph | Drops the repeat of the nights figures (+9.2/+7.3 vs +11.5/+9.9, FY27 +6.4), which are already in the thesis, Graph 1 and Catalysts. Shortens the RNPL-share sentence. |
| Proof | Shortens the attrition clause. Drops the STR RevPAR parenthetical. The "under 10%" sentence is reworded. |
| Growth bullets | Regulation bullet shortened (New York; Spain 65,122). The Barcelona 2028 date is dropped. |
| Margins | Drops "S&M has outgrown revenue for nine straight quarters" (the S&M bullet covers it). |
| Macro | Ends with "the short does not fight the macro", the PM's framing. v4's "we do not lean on it: dearer flights push travellers to drive-to trips" is cut, so keep that rebuttal for Q&A. The CoStar "+2.1%" is also cut. |
| Catalysts | "FY26 floor at risk (ours 34.5%…)" becomes "FY26 margin floor at risk". The "Through 2027" sentence is shortened. |
| Valuation | Reordered into one sentence (multiples, then the $117–123 range). Numbers unchanged. |
| Risks | AI: trimmed wording; all arguments kept. Buyback: drops "(every authorization came in a print-day letter)". Loyalty/ads: shorter. Risk 4: "Upside marker: the 7 Aug close ($178, +18%)"; the February 5-of-6 up-days sentence is dropped. |
| Layout | Paragraph spacing after is 4pt (v4: 5pt). |

## 4. Review against the PM's feedback (v4 and v4.1)

| PM ask | Status |
|---|---|
| Narrative and sales pitch; the "why" | Done in v4. The memo reads as one argument. |
| Thesis leads with return, horizon, catalyst, the truth revealed | Done. |
| Which trade? The Graph 1 one-day 8% vs the −20% 12M target | Done. The event study was dropped (v4), and Graph 1 is now the 12-month story (v4.1). |
| Consistent catalyst path (Nov starts, Feb completes, 2027 converges) | Done, and the thesis and Catalysts match. |
| Why the bundle creates an illusion | Done. |
| Stays index as the secret sauce | Done (paragraph plus Graph 2). |
| Macro tailwinds | Done, framed as "does not fight the macro". |
| Why Airbnb is no longer a growth company | Done (four bullets). |
| Risks: AI agent, buyback, loyalty/ads | Done. Each is bounded rather than hand-waved. |
| Size and liquidity | Asserted only. ADV, days to cover and borrow are still not sourced. |

**Open items for the team (not decided here):**

1. The Bloomberg FY27 nights pull date (§1).
2. SI 3.59% has no source (v4 §3.1).
3. The price is stamped 24 Sep ($151.39). Re-stamp it on submission day.
4. **The 3Q26 "underlying" is 7.8%, above 2Q26's 6.8%.** It is the residual of the 9.2% all-in (v4 §3.4). On the longer Graph 1
   it is more visible: a grey bar that rises in the quarter we call a slowdown. A judge will ask about it. The team decides
   whether that point belongs in underlying or in its own segment.
5. "Growth has slowed every year since 2022" vs FY26E +9.0% (FY25 +8.4%). The text says the 2026 lift was bought, and Graph 1
   shows it, but the literal claim is about the underlying rate.
6. Items carried from v4 and still open: bundle quotes to verify against the IR replay; press-only sources (the 23 Sep sell-off,
   Muse, AI Mode, ChatGPT, "next year"); the target's time basis; no stop or R/R.

## RESUME

Get the Bloomberg FY27 nights date and add it to the Graph 1 source (`compose_v4_1.py`) and the vintage register. Decide open
item 4. Re-stamp the price, then open the .docx in Word and confirm two pages. There is about one line of slack on page 2. If an
edit adds text, cut the Macro sentence first.
