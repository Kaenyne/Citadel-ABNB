# 25. Model conventions and documentation cleanup

*Overnight run follow-up, 7 September 2026. Inputs: `docs/2026-09-06_audit_findings_ai_handoff.md`
sections 14 (A12), 16 (R01/R02) and 17 (evidence limits and smaller cleanup items). Outputs: four
documents relabelled, four documents corrected, three new CSVs. **No model number changed anywhere.***

## Bottom line

Four conventions that the audit said needed an explicit decision are now decided and written down, and
six pieces of stale or misleading metadata are fixed.

1. **The valuation outputs are 12-month forward targets**, not present fair values. Target date ~30 Sep
   2027, FY2027E exit metrics, and "upside" is a 12-month expected price return from the 4 Sep 2026 close
   of $181.94.
2. **The 597.0M share anchor is a proxy** — 2Q26 diluted *weighted-average* shares standing in for a
   period-end fully diluted count — SBC dollars at a share price is an **issuance proxy**, and the EPS
   line is an **earnings proxy on modelled shares**, not GAAP EPS. A more precise bridge is *proposed,
   not built*.
3. **Two lines in the FY2025 cash bridge are estimates or residuals**, and its $0M interest-expense memo
   is a classification, not an economic zero.
4. **The DCF fade-period input is inert in Excel but live in the Python mirror.** The warning stays, and
   now says the second half too.

And: the 4Q23 ex-SBC identity gap is **fully explained** (it is a footnote column-selection defect worth
exactly $36M, not economics); the 20-vs-22-quarter history mismatch is a stale main-tree artifact, not a
live disagreement; `research/sources/README.md` no longer reuses seven S-numbers; and "does not exist"
has become "not found in public previews" wherever the run could not locate a nights consensus or an
options preview.

---

## 1. A12 decision 1 — valuation date

**Decision: the football-field and DCF outputs are FORWARD TARGETS at a 12-month horizon.** Adopted
target date **~30 September 2027**, exit metrics **FY2027E**. Upside against the 4 Sep 2026 spot is a
**12-month expected price return**, not a discount to a present discounted value.

Why: `valuation()` in `13_driver_model.py` is forward in every line. It seeds the DCF with FY2027 FCF,
discounts the next annual flow one period, and divides FY2027 net cash and the FY2027 period-end share
count into the result. The multiple lenses do the same with FY2027E metrics. Converting the set to
present values would mean discounting each target back to 4 Sep 2026 and adding the FY2026-27 interim
flows explicitly — a real change to the numbers, which was out of scope and would have been a silent
economic edit under the label "audit cleanup".

Three things the convention has to say out loud, all now written into the notes:

- **The lenses are not all dated alike.** Five of the six football-field lenses are values as of
  **end-FY2027**; the sixth (EV / adj. EBITDA on **FY2028E**) is a value as of end-FY2028 and is **not
  discounted back**. It is the highest of the six, so it lifts the base football-field mean by **$11.46**
  ($160.22 with it, $148.76 without). This is now labelled as a deliberate one-year-out / two-years-out
  blend. The audit's instruction was "do not average values at different dates without a defined
  convention"; the convention is defined and the cost of it is quantified.
- **No lens adds interim cash flows.** Cash generated between the spot date and the value date enters
  only through the FY2027E (or FY2028E) net-cash balance on the two EV lenses and the DCF, and only
  through the buyback-reduced share count on P / SBC-adjusted FCF and the earnings proxy.
- **The end-FY2027 arithmetic is mildly generous as a "30 Sep 2027" label.** Straight-lining net cash and
  the share count three quarters of the way from FY2026E to FY2027E gives **$179.44** on the base
  EV/EBITDA lens against the model's **$180.88** — $1.44, or 0.8%. Recorded, not restated.

Written to **`data/processed/overnight/25_valuation_conventions.csv`**: one row per lens with its metric,
metric year, exit basis, net-cash year, share-count year, the date the value is actually as of, the
adopted target date, whether interim cash flows are counted, whether it is in the football field, and the
bear/base/bull price. Plus four memo rows (the football-field mean by scenario, and the Sep-2027 vs
end-FY2027 comparison above).

## 2. A12 decision 2 — share count

**Decision: label the approximation; do not rebuild it tonight.** The three labels now travel with every
per-share number:

| Item | What it actually is | Why it matters |
|---|---|---|
| The 597.0M anchor | 2Q26 **diluted weighted-average** shares (SEC XBRL), used as a proxy for the 30 Jun 2026 **period-end fully diluted** count | A weighted average spans the quarter; a period-end fully diluted count is a point-in-time capitalisation. The roll-forward's output is called "period end" but inherits the anchor's basis |
| SBC dollars ÷ share price × (1 − 35% withholding) | An **issuance proxy** | Real issuance follows vesting schedules on awards granted at historical prices. No such schedule is disclosed |
| Net income ÷ modelled period-end shares | An **earnings proxy** | GAAP diluted EPS uses weighted-average shares under the treasury-stock method. The model's EPS is not a GAAP EPS forecast, and the Street comparison is against Street *adjusted* EPS |

**R01 is respected: the share roll is not touched.** WS18's fix removed the 1H26 double-count and is
correct (`SHARE_ROLL_NETS_1H26 = True`). What remains is the weighted-average-versus-period-end
convention, which is A12, not a recurrence of the arithmetic bug. Both the assumptions file and
`18_corrections-applied.md` now say so explicitly so nobody "fixes" it a second time.

**Proposed, not built — a period-end fully diluted bridge.** Anchor on the 10-Q cover-page Class A +
Class B shares outstanding at 30 Jun 2026 (basic, point-in-time). Add unvested RSUs outstanding and
in-the-money options from the equity-incentive footnote to get a point-in-time fully diluted count. Then
roll that on a real vesting schedule: the 10-K discloses unrecognised stock-based compensation and its
weighted-average recognition period, which pins the dollar path without assuming a share price. Expected
effect: low single-digit millions of shares, i.e. under 1% on price. Worth doing before the deck; not
worth doing to a number that now carries its own label.

## 3. A12 decision 3 — the FY2025 cash bridge

The FY2025A memo column on `Cash` (anchors on `History`, "FY2025 CASH-BRIDGE ANCHORS") is eleven cells,
of which **two are not observations and one is a classification**:

- **Cash taxes −$232M: an ESTIMATE.** WS07's 1.9% of revenue × $12,241M. Not a disclosed FY2025 cash-tax
  line; the book provision was $626M.
- **Working-capital residual −$139M: a RECONCILIATION RESIDUAL.** It is chosen so the other eight lines
  reproduce the reported FY2025 FCF of $4,613M exactly. A plug, not an observed movement.
- **Interest expense $0M: a CLASSIFICATION, not an economic zero.** `abnb_fcf_bridge.csv` reports zero
  interest expense in every quarter of 2025 because the coupon on the $2.5bn of senior notes sits inside
  other income/(expense) in the letters' own bridge for that period. Airbnb had borrowing cost in FY2025;
  this cell does not show it. The forecast years take interest expense from `Inputs` ($120–128M a year)
  and are unaffected.

The remaining six (D&A $91M, D&A and other add-backs $161M, interest income $705M, other income/(expense)
−$112M, change in unearned fees $127M, capex −$33M) are **derived actuals**: sums of the 1Q25–4Q25
quarters of `abnb_fcf_bridge.csv`, each read from its own shareholder letter. Buybacks and RSU withholding
are live sums of the 2025 quarters on the sheet. **No forecast year depends on any of these cells.**

## 4. A12 decision 4 — the DCF-years input

**Confirmed inert in Excel; the warning stays and is strengthened.** WS17 marked the `DCF fade period
(years)` input LAYOUT-FIXED because the DCF grid on `Valuation` section 3 is ten written-out rows: editing
the cell resizes nothing and changes no Excel output (`13_excel_builder.py` around line 122;
`17_excel-audit.md` finding 8 and open item 5).

**What the existing warning does not say, and now does elsewhere:** the same input **is** functional in
the Python mirror — `13_driver_model.py` passes `V["dcf_years"]` to `dcf()` for both DCF lenses and to
`implied_growth()` for the reverse-DCF grid. So a user who edits the Bear or Bull cell away from 10 gets
no change in Excel, a real change in Python, and a 216-output reconciliation that starts failing for a
reason the workbook does not explain. Until someone builds a dynamic strip, **treat the cell as read-only
at 10 years in all three scenarios.** Added to `model/assumptions.md` and the 13 note. The builder itself
was not edited (another agent owns `13_excel_builder.py` for A10).

Also recorded, per the audit: applying the same annual regulatory growth drag to each quarter is **not**
automatically four times the annual effect. Assess the weighted annual aggregate before calling it a bug.

---

## 5. Section 17 cleanup

### (a) Stale README counts and duplicated rows

**`research/sources/README.md` — S-number collisions fixed.** The union merge of the branch READMEs left
**seven reused IDs** (WS01 finding 4): S30 twice for the same FRED/BLS CPI series, and S32–S37 each used
for two *different* sources. A deck citation of the form "(S33)" was ambiguous. Applied:

| Old | New | Source | Action |
|---|---|---|---|
| S30 (2nd row) | — | FRED / BLS CPI, lodging away from home etc. | **Merged** into the first S30 row, whose "Used for" was a superset. No source lost |
| S32 | **S40** | Inside Airbnb listings dumps, 13 cities, 168 dumps | Renumbered (S32 stays with the 10-K geographic note + 1Q21/2Q21 SBC footnotes) |
| S33 | **S41** | Common Crawl listing-page archive | Renumbered (S33 stays with ABNB + six-peer XBRL) |
| S34 | **S42** | 5 Sep driver-model note and `model/assumptions.md` | Renumbered (S34 stays with the capital-return panel note) |
| S35 | **S43** | Eurostat `tour_ce_omr` platform nights | Renumbered (S35 stays with the earnings-call transcripts / Q&A roster) |
| S36 | **S44** | XBRL unearned fees and funds held for clients | Renumbered (S36 stays with the transcript-analytics note) |
| S37 | **S45** | Peer earnings releases (BKNG, EXPE, MAR, HLT, 93 filings) | Renumbered (S37 stays with the regulatory forecast profile) |

The table is now **45 rows, IDs S1–S45, all unique**, sorted by ID. A header note warns that a citation
written before 7 Sep 2026 as (S32)–(S37) may mean either member of its pair. The stale in-cell branch
notes ("S32 to S36 are on PRs #11 to #14") are **kept** — the audit said not to erase dated provenance —
but each is now prefixed "Branch note, 5 Sep 2026" and gives the new IDs in brackets. Machine-readable
mapping: **`data/processed/overnight/25_source_id_remap.csv`**.

**`data/README.md` — table repaired and counts verified.** The merge had left the `inside_airbnb_*` row
*outside* the table, stranded after the transcripts paragraph; it is back in the table. Added a row for
`data/processed/overnight/` (191 CSVs, 56 scripts, 24 figures, 21 notes as of the 7 Sep count - the 19-25
repair workstreams were still writing, so the row says to recount rather than quote), which the file did
not mention at all. Then every countable claim in the file was checked against the files themselves:

| Claim | File | Actual |
|---|---|---|
| 1,440 sessions | `abnb_daily_close.csv` | 1,440 ✓ |
| 41 moves ≥7% | `abnb_major_moves_events.csv` | 41 ✓ |
| 23 prints | `abnb_earnings_reactions.csv` | 23 ✓ |
| 20 numeric guides | `abnb_revenue_guidance_vs_actual.csv` | 20 ✓ |
| 368 KPI sentences | `abnb_filing_kpis.csv` | 368 ✓ |
| 50 crawls / 1,500 matched listings | `cc_index_summary.csv`, `cc_matched_listings.csv` | 50 / 1,500 ✓ |
| 600 and 44,379 rows | booking curves | 600 / 44,379 ✓ |
| 120 markets | `market_summary_2026.csv` | 120 ✓ |
| 20 regulatory events | `abnb_regulatory_events.csv` | 20 ✓ |
| 168 dumps, 13 cities | `inside_airbnb_city_snapshots.csv`, `data/raw/inside_airbnb/manifest.csv` | 168 of 279 probed (111 returned HTTP 403), 13 cities ✓ |
| 317 / 322 / 37 rows | call roster, topics, declined-to-quantify | 317 / 322 / 37 ✓ |
| 22 quarters, 1Q21–2Q26 | `abnb_quarterly_cost_stack_exsbc.csv` | 22 ✓ |

**Every claim held.** The stale-count check block and the results are now in the file itself.

**`research/regulatory/README.md` — checked, correct, and out of reach.** Its "**48** source records,
**32** factors, nine earnings observations, 14 quarterly transcripts" all match `sources.json` (48),
`factors.json` (32), `earnings_observations.json` (9), `transcript_manifest.json` (14) and the tables in
`data/processed/abnb_regulatory.sqlite`. **The stale count the audit saw is elsewhere:** the *main
working tree's* uncommitted `data/README.md` says the database holds "**44** source records" — it holds
48. That file, `research/regulatory/` and the SQLite database were never committed and do not exist in
this tree, so WS25 could not fix them here. A pointer and the correct number are recorded in this tree's
`data/README.md` under "Not in this tree".

### (b) Historical-state banners

Added a dated banner, in the same style WS19 used on `15_red-team.md`, to:

- **`research/notes/overnight/17_excel-audit.md`** — "HISTORICAL STATE": the whole note is pre-WS18-fix.
  Its workbook counts (5,544 cells, 2,348 formulas — now 5,547 and 2,349) and every per-share and
  football-field number in it are pre-fix. Do not quote a price or a share count from it; the eleven
  mechanical fixes and the audit method remain current. The banner also records that the valuation-date
  question the note left open was decided on 7 Sep.
- **`research/notes/overnight/18_corrections-applied.md`** — "PARTLY HISTORICAL": its "as built (6 Sep)"
  columns are deliberately pre-fix and the "fixed (7 Sep)" columns are current. The banner adds the two
  later decisions that its wording predates: the residual share convention is A12, not a recurrence of
  the bug it fixed (so do not re-fix the share roll), and its prices are 12-month forward targets.

**No text was deleted from either note.**

### (c) The ~$36M 4Q23 ex-SBC identity gap, and 20 vs 22 quarters

**The $36M gap is fully explained and is not economics.** Reconciliation in
**`data/processed/overnight/25_history_reconciliation.csv`**:

The ex-SBC stack builds cash cost lines as *GAAP line less SBC by function*, taking SBC by function from
the shareholder letter's footnote. `abnb_exsbc_stack.py` picks the footnote **column** whose total is
nearest to a target taken from XBRL. For 4Q23 the target is the XBRL Q4 value **$270M**, itself derived as
FY-less-9M. The 4Q23 letter's footnote shows four columns — 3M Dec 2022 **$254M**, 3M Dec 2023 **$290M**,
FY2022 $930M, FY2023 $1,120M. Because |254 − 270| = 16 is smaller than |290 − 270| = 20, **the parser
picked the prior-year column.** The stack therefore subtracts $254M of SBC where the letter's own
Adjusted EBITDA reconciliation adds back $290M:

```
254 - 290 = -36   =   the reported identity_gap for 4Q23
```

Re-running the identity with the correct 31 Dec 2023 column (operations and support 17, product
development 179, sales and marketing 33, G&A 61; total 290) closes it exactly:
`2,218 − (2,714 − 290) + 16 + 928 = 738`, the reported Adjusted EBITDA.

Effect, confined to 4Q23: **product development cash cost overstated by $29M, G&A by $9M, operations and
support by $1M; sales and marketing understated by $3M.** Every other quarter's gap is within ±$1.7M and
1Q23–2Q26 are exactly zero, so nothing else is affected. **Not fixed here** — WS25 is documentation-only
and does not own `analysis/src/abnb_exsbc_stack.py`. The fix is to prefer the footnote column whose header
*year* matches the quarter and fall back to nearest-total only when the header cannot be read.

**The 20-vs-22-quarter mismatch is not a live disagreement.** This tree's
`abnb_quarterly_cost_stack_exsbc.csv` has **22** quarters (1Q21–2Q26) and agrees with
`abnb_capital_return_quarterly.csv`, `abnb_quarterly_kpis_from_study.csv` and
`abnb_driver_history_quarterly.csv`, all 22. The **main tree's** copy has 20 (3Q21–2Q26) because it
predates the `SBC_FALLBACK` table that supplies 1Q21 and 2Q21 SBC by function from 10-Q accessions
0001628280-21-010389 and 0001628280-21-016979 — the 2021 letters carry no SBC-by-function footnote.
**Consolidate on this tree's 22-quarter file and retire the main-tree artifact** (A07's version
consolidation).

### (d) "Does not exist" → "not found in public previews"; vendor vintage; the base-rate p-value

In `14_master-synthesis.md` and `docs/overnight/FINAL_SUMMARY.md`:

- The 3Q26 **nights / adjusted-EBITDA consensus** and the published **options implied-move preview** are
  now described as **not found in public previews on 6 Sep 2026**, with the reasons stated (WS16 searched
  free and preview-tier sources only; vendors may carry a nights estimate behind a terminal; implied-move
  previews publish in the week of the print, and the 6 Nov weekly was not yet listed). No external
  re-verification of vendor availability was performed, and the notes now say so.
- The 5 Sep options finding is re-labelled: **"no event premium in the term structure on 5 Sep" is not
  "options contain no event information"**, and a two-monthly √time test is a coarse instrument.
- **Vendor and vintage caveat added to the reconstructed consensus series.** It is spliced from whichever
  vendor a publisher happened to quote at each print — StreetAccount, LSEG, Zacks, Visible Alpha,
  S&P Global — at whatever moment that publisher wrote. Vendors differ materially: one nights comparison
  in the file differs by roughly **2%**, larger than the median nights surprise the regressions are
  fitted on. Keep the `source` and quote-date columns of `04_consensus_at_print.csv` attached, control
  for or drop the vendor before quoting the 20-day nights-drift coefficient, and never splice a Zacks
  number into a StreetAccount history silently.
- The **9-of-9 guide-below-Street** claim now carries **base-rate-adjusted p 0.057** beside it in the two
  places it did not (the "honest statement" in section 6.4 and the risk register in the synthesis), and
  `FINAL_SUMMARY.md`'s stale **"all eight prints"** is corrected to nine with the same p and an explicit
  "exploratory, n 9". The 0.0020 coin-flip p should not be quoted alone.

---

## 6. Corrections to existing work

1. **`analysis/src/abnb_exsbc_stack.py` has a real defect** (section 5c above): the SBC-by-function
   footnote column pick uses nearest-total against an XBRL Q4 target that is itself FY-less-9M, and for
   4Q23 that selects the prior-year column. Overstates 4Q23 product-development cash cost by $29M and
   G&A by $9M. Not fixed here — not this workstream's file.
2. **The main working tree's `data/processed/abnb_quarterly_cost_stack_exsbc.csv` (20 quarters) and its
   uncommitted `data/README.md` ("44 source records") are stale.** Use this tree's 22-quarter file; the
   regulatory database holds 48 sources.
3. **`docs/overnight/FINAL_SUMMARY.md` under-counted the run**: it said 153 CSVs, 39 scripts and 15 notes;
   the 7 Sep count is 191, 56 and 21, and the 19-25 repair workstreams were still writing while WS25 ran.
   Corrected to dated counts that tell the reader to recount.
4. **`research/notes/overnight/16_web-gap-fill.md` rows (d) and (e)** say a 3Q26 nights consensus and an
   options preview "do not exist yet". They are true as availability statements on 6 Sep and false as
   existence claims. Not edited (another workstream's note); the softened wording is in the synthesis and
   the summary, which are what a reader quotes.

---

## 7. Files

**Edited**

| File | Change |
|---|---|
| `model/assumptions.md` | New section "Model conventions, decided 7 Sep 2026" (the four A12 decisions in full); two share-count rows relabelled as proxies |
| `research/notes/overnight/13_driver-model-build.md` | Section 1 notes 1 and 2 relabelled as 12-month targets; "implied upside" → "implied 12-month return"; new section 5b with all four conventions and the proposed share bridge |
| `research/notes/overnight/14_master-synthesis.md` | Section 4.5 convention block; "upside" row relabelled; section 8.1 relabelled; the WS17 open valuation-date item marked decided; vendor/vintage caveat on the consensus series; nights-consensus and options absence softened; base-rate p 0.057 added in two more places; new section 11.4 |
| `docs/overnight/FINAL_SUMMARY.md` | Headline and base-case lines relabelled as 12-month targets with the convention stated; "all eight prints" → nine with p 0.057; Q4-guide card row flagged; stale file counts fixed; a "read the labels" block before the to-do list |
| `research/notes/overnight/17_excel-audit.md` | Dated "HISTORICAL STATE" banner (no text deleted) |
| `research/notes/overnight/18_corrections-applied.md` | Dated "PARTLY HISTORICAL" banner (no text deleted) |
| `data/README.md` | Orphaned table row restored; overnight-run row added; verified-counts block; "Not in this tree" note on the regulatory package and the stale main-tree artifacts |
| `research/sources/README.md` | Duplicate S30 row merged; S32–S37 collisions renumbered S40–S45; table sorted; header warning; branch notes dated rather than deleted |

**Written**

| File | Contents |
|---|---|
| `analysis/src/overnight/25_conventions_and_cleanup.py` | Rebuilds all three CSVs below; re-derives the 4Q23 gap from the letter and the two cost files |
| `data/processed/overnight/25_valuation_conventions.csv` | 12 rows: eight lenses plus four memos — metric year, exit basis, net-cash and share year, actual value date, adopted target date, interim-cash-flow treatment, bear/base/bull price |
| `data/processed/overnight/25_source_id_remap.csv` | 8 rows: every S-number collision, its new ID, and why |
| `data/processed/overnight/25_history_reconciliation.csv` | 12 rows: the 4Q23 identity gap decomposed to the dollar, and the 20-vs-22-quarter question resolved |

**Not edited, deliberately:** `13_excel_builder.py`, `13_driver_model.py` (A10 is another agent's), any
`08_*`, `15_*`, `16_*` or `17_*.py`, and the regulatory / options / Inside Airbnb scripts.

Rebuild: `py -3.13 analysis/src/overnight/25_conventions_and_cleanup.py`.

---

## For the model

No parameter changes. Three conventions the model must carry with its outputs:

| Name | Value | Unit | Source |
|---|---|---|---|
| Valuation basis | 12-month forward target, FY2027E exit metrics | — | WS25 / A12; `25_valuation_conventions.csv` |
| Target date | ~2027-09-30 (arithmetic is end-FY2027; $1.44 or 0.8% apart on the base EBITDA lens) | date | same |
| Football-field date mix | 5 lenses at end-FY2027, 1 at end-FY2028, undiscounted; worth $11.46 of the base mean | $/share | same |
| Share-count basis | 2Q26 diluted weighted-average as a proxy for period-end fully diluted; issuance from SBC ÷ price | M shares | WS25 / A12; `model/assumptions.md` |
| EPS basis | Earnings proxy on modelled shares, not GAAP EPS | $ | same |
| FY2025 cash taxes / WC residual | Estimate ($232M) / reconciliation plug ($139M) | $M | `13_excel_builder.py` History anchors |
| FY2025 interest-expense memo | $0M by classification, not an economic zero | $M | `abnb_fcf_bridge.csv` |
| DCF fade period | 10 years, read-only: inert in Excel, live in Python | yrs | WS17 finding 8; `13_driver_model.py` |

## For the 5 Nov card

Nothing new to forecast. Two wording rules for the card and the deck: the guide-below-Street flag is
**9 of 9 with base-rate-adjusted p 0.057** (exploratory, n 9) — never the 0.0020 coin-flip figure alone;
and the nights bar is "**not found in public previews as of 6 Sep**", with Zacks expected to publish
nights, ADR and GBV consensus on ~2–3 Nov. When that lands, record the vendor and the timestamp next to
the number.
