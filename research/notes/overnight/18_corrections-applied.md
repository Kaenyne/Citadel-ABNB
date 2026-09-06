# 18. Applying the WS16 and WS17 corrections, and fixing the share count

*Overnight run follow-up, 7 Sep 2026. Inputs: `17_excel-audit.md` (the one open high-severity finding)
and `16_web-gap-fill.md` (twelve line edits plus new evidence). Outputs: a corrected model, a corrected
synthesis, and a ledger of everything that moved.*

## Bottom line

**The FY2026 share-count roll-forward double-counted the 1H26 buyback; it is fixed in both the Python
model and the Excel builder, and every per-share and price number in the run falls about 1.5%.** The base
case is now worth **$181** on the EV/FY27E-adj.-EBITDA lens against a $181.94 spot, and the base
football-field mean is **$160.22** (bear **$75.95**, bull **$232.68**). Nothing above the share line
moved: revenue, margins, adj. EBITDA, FCF and net cash are byte-identical to the 6 Sep build. The
regenerated workbook was rebuilt in real Excel 16.0 and re-passed WS17's whole audit.

| | as built (6 Sep) | fixed (7 Sep) | delta |
|---|---|---|---|
| FY2026E diluted shares, base | 580.30M | **588.85M** | +8.55M (+1.47%) |
| FY2027E diluted shares, base | 566.05M | **574.60M** | +1.51% |
| FY2028E diluted shares, base | 552.98M | **561.53M** | +1.55% |
| Base FCF / share, FY2027E | $9.58 | **$9.43** | −1.49% |
| Base SBC-adj. FCF / share, FY2027E | $6.10 | **$6.01** | −1.49% |
| Base earnings proxy / share, FY2027E | $5.76 | **$5.67** | −1.49% |
| Base EV / adj. EBITDA lens (the headline price) | $183.61 | **$180.88** | −$2.73 |
| Base DCF on FCF | $185.35 | **$182.59** | −$2.76 |
| **Base football-field mean** | **$162.65** | **$160.22** | **−1.50%** |
| Bear / bull football-field mean | $77.09 / $236.24 | **$75.95 / $232.68** | −1.48% / −1.51% |

The reverse DCF is untouched (8.51% / 14.42% implied ten-year FCF growth at a 10.5% cost of equity): it
prices today's enterprise value off the *2Q26* share count, not the roll-forward.

Full before/after for all 73 affected outputs: `data/processed/overnight/18_share_fix_delta.csv`.
Every edit made to every file: `data/processed/overnight/18_corrections_applied.csv` (55 rows).

---

## 1. The share-count fix

### What was wrong

`Cash` rows 23 / 48 / 73 (bear / base / bull) and the identical line in the Python mirror rolled the
share count forward as

```
shares(FY2026) = 2Q26 diluted count − FY2026 buybacks / price + FY2026 SBC / price × (1 − withholding)
```

while the net-cash line three rows below correctly consumed only the 2H26 flows
(`FY2026 less the 1H26 actual` for FCF, buybacks and withholding). Both roll-forwards start from the same
30 Jun 2026 balance sheet — **597.0M diluted shares and $9,593M of net cash** — so applying a full-year
flow to one and a half-year flow to the other cannot both be right. The 1H26 repurchase
(**$2,139M = 11.756M shares at $181.94**) was subtracted twice, less the 1H26 RSU issuance that was also
double-counted (**$897M of SBC → 3.204M shares net of 35% withholding**), for a net **−8.552M shares** on
FY2026E and, because the roll compounds, on FY2027E and FY2028E too.

### Which convention, and why

**Roll from the 2Q26 count using 2H26 flows only.** That is the convention the net-cash line already uses
and the one the model's own starting point demands: `shares_2q26 = 597.0M` is the *2Q26* diluted
weighted-average, so the only thing left to happen in FY2026 is the second half. Rolling from a FY2025
count instead would have needed a FY2025 diluted share number the model does not carry, and would have
made the share line inconsistent with the net-cash line it sits next to. FY2027 and FY2028 are unaffected
and still take the full year.

### The change

- `analysis/src/overnight/13_driver_model.py` — `H1_26` gains `sbc=410.0 + 487.0` (1Q26 and 2Q26 SBC from
  `02_kpi_panel_quarterly.csv`), and the roll becomes, for 2026 only,
  `shares − (FY26 buybacks − 1H26 buybacks) / px + (FY26 SBC − 1H26 SBC) / px × (1 − withholding)`.
  A module-level flag `SHARE_ROLL_NETS_1H26` (default `True`) documents the convention and lets the
  pre-fix path be reproduced for the delta table.
- `analysis/src/overnight/13_excel_builder.py` — a new sourced History anchor **`1H2026 SBC ($M)`**
  (`=1Q26 + 2Q26 sbc_musd` over the History quarterly table, no hard-code), and the FY2026E column of the
  Cash share row becomes
  `=C23-(D21-History!$B$48)/D20+(D17-History!$B$50)/D20*(1-Inputs!$C$18)`.
  FY2027E and FY2028E keep the full-year form. The Cash sheet header note, which previously *documented*
  the asymmetry as a known defect, now states the corrected convention.
- Excel and Python agree cell for cell: `Cash!D23` reads **589.019478949104**, `D48` **588.850030229746**,
  `D73` **588.680581510388**, each matching the mirror exactly.

### Verification after regeneration

| Check | Result |
|---|---|
| `13_driver_model.py` reconciliation | **216 checks, 0 mismatches** |
| `13_xlsx_eval.py` (the evaluator) | **2,349 formula cells, 0 errors** |
| Excel 16.0 `CalculateFullRebuild()` on a copy | **5,547 cells, 0 error cells**, no circular reference, `xlDone` |
| `17_excel_audit.py` — named outputs | **216 compared, 0 fail at 1e-6** |
| `17_excel_audit.py` — all formula cells, Excel vs evaluator | **2,349 compared, 0 outside 1e-6** |
| `17_scenario_switch.py` — selector = 1 / 2 / 3 | **143 comparisons, 0 mismatches**; the selector moves **135** cells at Bear (Inputs 96, Valuation 22, Card_5Nov 17) and **136** at Bull |
| `17_formula_review.py` | 29 rows; status now **12 fixed / 4 open / 13 clean** (was 11 / 5 / 13) |

The formula-cell count went 2,348 → **2,349**: the one new History anchor. No other cell moved, and the
`cell_reference` column of `13_reconciliation.csv` is unchanged row for row.

---

## 2. WS16's twelve line edits, applied

All twelve are in `14_master-synthesis.md`, each verified to match exactly once before replacement
(`scratchpad/18/edit_synth.py`):

| # | Where | What |
|---|---|---|
| 1 | §3 evidence table, guide-below-Street row | 8 prints / −7.95% / base-rate p 0.078 → **9 / −8.90% / 0.057**, with the 2Q24 source (Reuters 6 Aug 2024, LSEG $3.84bn vs a $3.70bn midpoint) and the Mann-Whitney p 0.040 |
| 2 | §6.1 alpha scorecard | 8/8 → **9/9**, p 0.078 → **0.057** |
| 3 | §6.4 honest statement | appended "(9/9, mean −8.90%; WS16 re-run on `16_reaction_tests.csv`)" |
| 4 | §7 card, ADR row | "no publisher quotes an ADR consensus, ever" → the Zacks series (five prints, beaten 5 of 5), collected ~2-3 days before each print |
| 5 | §7 card, Q4 guide row | 8/8 → **9/9**, p → **0.057** |
| 6 | §8.3 claims to stop making | the "about half of listings on the single fee" clause **deleted** — it is verbatim in the 2Q26 call |
| 7 | §8.3 direct-booking pilot | "paywalled, never read from a primary source" → **verified** (15.5% → 6% or 10%, invite-only, US) but the −0.8pt needs 8.4-14.5% of GBV; **use 0-15bp of FY27 take rate** |
| 8 | §8.4 risk register | 8/8 → **9/9** |
| 9 | §9 build-forward item 5 | "no free nights consensus exists" → Zacks publishes one ~2-3 Nov; cost falls from "2h + calls" to **0 calls, 10 minutes** |
| 10 | §10.2 AirROI | "do not cite the 55.9%" → characterise it: a *modelled* 3-night total including lodging tax and cleaning fee on a stale 14% guest fee |
| 11 | thesis-file catalysts | adds **8 Sep, Chesky at Goldman Communacopia, 6:05pm ET**; notes the 9 Sep EU proposal **leaked 4 Sep** and devolves capping powers to member states |
| 12 | §10.2 corrections list | adds the line withdrawing red-team corrections 11 and 15 |

Plus, as asked, a new paragraph in §7 (the 5 Nov card) telling the reader to pull Zacks' *"Wall Street's
Insights Into Key Metrics Ahead of Airbnb (ABNB) Q3 Earnings"* on ~2-3 Nov — nights, ADR and GBV
consensus, free, two to three days early — and to expect a 1-2% vendor gap to StreetAccount (Zacks had
2Q25 nights at 130.76m where WS04's StreetAccount row has 133.35m).

## 3. New section 11, "Post-run corrections (WS16, WS17, WS18)"

Added to `14_master-synthesis.md` before "For the thesis file". Three subsections: **11.1** the WS16
consensus and web findings (the ninth guide-below-Street print and the 2021 EPS trap, the Zacks ADR
series, the withdrawn red-team corrections, the bounded direct-booking drag, AirROI, the press
attribution re-read — guide 6 / KPI 2 / macro 1 / spend 1 rather than guide 4 / KPI 4, with 2020Q4's
"margin" attribution unsupported by any same-day source — and the 8 Sep / 4 Sep calendar); **11.2** the
WS17 Excel audit (0 errors in 5,547 cells, the inert scenario selector and the pasted reverse-DCF answer,
both fixed, numeric literals 121 → 3 cells, four items left open for a human); **11.3** this share fix
with its before/after table. Every existing section keeps its structure; only numbers and this appended
section changed.

## 4. Numbers renumbered across the four documents

`14_master-synthesis.md` (§0 headline bridge, §0 and §4.5 weighted lenses, §4 bottom line and workbook
description, §4.1 base table, §4.4 price bridge, §4.5 lens table, §4.6 Street comparison, §8.1, §9 item
9, the file map, the thesis file), `docs/overnight/FINAL_SUMMARY.md` (headline and model line),
`13_driver-model-build.md` (header, §1, the three scenario tables, the lens table, the price bridge, the
Street EPS rows, the file list) and `model/assumptions.md` (the diluted-shares output row and its
rationale). The headline bridge now reads:

> The base-case price fell from **$248** (5 Sep) to **$181** (7 Sep), and **$55 of that $67** is the exit
> multiple. The rest moved $12: −$5 EBITDA, −$4 net cash, **−$3 share count**. The multiple is **82%** of
> the change (was 86%).

25/50/25-weighted: **$176** on the EV/EBITDA lens (−3.2% vs spot), **$157** across all six football-field
means (−14%), **$231** on the old 18/22/25.5x multiples (+27%). FY26 adjusted EPS is now **$5.20** vs a
Street $5.23-5.28 (−0.5% / −1.4%, from +1.0% / 0.0%); FY27 **$5.67** vs $6.02-6.14 (−5.8% / −7.7%, from
−4.3% / −6.2%). **The "more revenue, more SBC, more AI cost, fewer shares retired than the sell side
assumes" framing gets slightly stronger, not weaker.**

## 5. Corrections to existing work

- **`17_formula_review.csv` row for the Cash roll-forward is now `fixed`, not `open`.** I edited the one
  status string in `analysis/src/overnight/17_formula_review.py` because re-running WS17's own scripts (as
  instructed) would otherwise have re-emitted a stale "OPEN" for a finding this workstream closed. No
  other WS17 row was touched, and WS17's note (`17_excel-audit.md`) still describes the finding as open —
  **its "To-do list for a human" item 1 is now done**, and its four remaining items (the DCF valuation
  date, an Inputs row for the 5 Sep memo multiples, FY2025 interest expense, a quarterly regulatory drag)
  are still open.
- **`17_scenario_switch.csv` is now 143 rows, not 145.** The two missing rows are the *pre-fix* baseline
  counts, which the script only emits when WS17's original scratch dumps are present; I re-ran it against
  fresh dumps in `scratchpad/18`. The 143 "after" rows are all there and all match.
- **`13_driver-model-build.md` choice 9** claimed the workbook "cannot be recalculated" because
  LibreOffice and the `formulas` package are unavailable. WS17 showed Excel 16.0 is reachable over COM on
  this machine; the claim is corrected in place, along with the 2,303 → 2,349 formula count and the
  `Inputs!$B$3` → `$B$4` selector reference.
- **`15_claim_checks.csv` and the other WS15 files were not touched**, per instruction. WS15's
  corrections 11 and 15 are withdrawn and correction 7's "every positive sits at 20 days" clause is now
  false (five at 20 days, four at five days, none at day 1); both are recorded in the synthesis §11.1 and
  in `18_corrections_applied.csv` rather than by editing WS15's files.

## 6. What I did not do

- **No consensus or reaction CSV was rebuilt.** WS16's re-run outputs (`16_reaction_tests.csv` etc.) stand
  as WS16 wrote them; WS04's originals are untouched. The synthesis now quotes the WS16 numbers.
- **The exit-multiple debate is unchanged.** The share fix moves every lens by the same ~1.5%, so it does
  not touch the run's central conclusion that the multiple, not the operating case, is the whole pitch.
- **The four WS17 items left for a human are still open**, and the most consequential is the DCF's
  valuation date: the strip is a value as of end-FY2027 against a 4 Sep 2026 spot, so the DCF lens is
  arguably a forward value sitting in a spot-referenced football field.

## For the model

| Name | Value | Unit | Source |
|---|---|---|---|
| 1H2026 SBC (new model anchor) | 897.0 | $M | `02_kpi_panel_quarterly.csv`, 1Q26 410 + 2Q26 487 |
| FY2026E diluted shares, bear / base / bull | 589.02 / 588.85 / 588.68 | M | `13_model_annual.csv` |
| FY2027E diluted shares, bear / base / bull | 580.43 / 574.60 / 571.40 | M | `13_model_annual.csv` |
| FY2028E diluted shares, bear / base / bull | 573.06 / 561.53 / 555.18 | M | `13_model_annual.csv` |
| Base FCF / share FY26 / FY27 / FY28 | 8.71 / 9.43 / 11.04 | $ | `13_model_annual.csv` |
| Base SBC-adj. FCF / share FY26 / FY27 / FY28 | 5.68 / 6.01 / 7.26 | $ | `13_model_annual.csv` |
| Base earnings proxy / share FY26 / FY27 / FY28 | 5.20 / 5.67 / 6.96 | $ | `13_model_annual.csv` |
| Football-field mean, bear / base / bull | 75.95 / 160.22 / 232.68 | $ | `13_valuation_summary.csv` |
| Football-field low / high, base | 110.58 / 217.51 | $ | `13_valuation_summary.csv` |
| Headline lens (EV / FY27E adj. EBITDA at 16.5x), base | 180.88 | $ | `13_valuation_summary.csv` |
| Direct-booking pilot drag, FY27 take rate | 0 to 15 | bp | WS16; replaces the −0.8pt that was never in the workbook |

## For the 5 Nov card

1. **On ~2-3 Nov, pull the Zacks key-metrics preview** — nights, ADR and GBV consensus, free, two to
   three days before the print. It closes the card's only unpublished bar at zero cost.
2. **The Q4 guide-below-Street flag is now 9 of 9 negative at 20 days, mean −8.90%** (base-rate p 0.057).
   The Street is at $3,200m for Q4-26 against our $3,145m; a midpoint below $3.20bn triggers it.
3. **8 Sep, 6:05pm ET: Chesky at Goldman Sachs Communacopia**, the only scheduled management appearance
   before the print.
4. **Card item 4's revenue and item 5's margin are unchanged by this fix.** Only the per-share and
   valuation rows moved.

## Files

- `analysis/src/overnight/18_share_fix_delta.py` — runs the model with the fix off and on, tabulates the delta
- `data/processed/overnight/18_share_fix_delta.csv` — 73 rows: kind, scenario, item, before, after, delta, delta %
- `data/processed/overnight/18_corrections_applied.csv` — 55 rows: source workstream, file, what changed, old, new
- edited: `analysis/src/overnight/13_driver_model.py`, `13_excel_builder.py`, `17_formula_review.py`
- regenerated: `model/ABNB_driver_model.xlsx`, `data/processed/overnight/13_model_annual.csv`,
  `13_model_quarterly.csv`, `13_valuation_summary.csv`, `13_scenario_grid.csv`, `13_reconciliation.csv`,
  `17_excel_recalc_dump.csv`, `17_excel_vs_python.csv`, `17_all_formula_cells.csv`,
  `17_scenario_switch.csv`, `17_formula_review.csv`, `17_auto_scan.csv`
- edited prose: `research/notes/overnight/14_master-synthesis.md`, `13_driver-model-build.md`,
  `docs/overnight/FINAL_SUMMARY.md`, `model/assumptions.md`, `docs/overnight/RUN_STATE.md`
- scratch only: `scratchpad/18/` (the edit scripts, the Excel recalc driver and its three dumps)
