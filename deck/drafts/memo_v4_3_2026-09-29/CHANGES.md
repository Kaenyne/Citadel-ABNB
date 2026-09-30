# Memo v4.3: two charts (29 Sep 2026)

Built on v4.2 (`deck/drafts/memo_v4_2_2026-09-29/`, unchanged). The page fit was checked in Microsoft Word with Aptos: 2 pages,
with page 2 ending at 718pt of 756pt (about 2–3 lines of slack).

## Rebuild, from the repo root

```
Rscript analysis/src/pitch_charts_pm/graph1_history.R
python analysis/src/pitch_charts_pm/compose_v4_3.py
NODE_PATH=<dir with node_modules/docx> node deck/drafts/memo_v4_3_2026-09-29/build_memo.js
```

## Changes

| | v4.3 |
|---|---|
| Graph 2 (stays routes + ADR) | **Dropped.** Everything on it was already in the text. Where the text cited it, the Street numbers now appear inline ("lowest of the 28 Street estimates (+10.0%; mean +11.5%)"). |
| Charts | Two charts, each floated right of its paragraph at 3.7in: Graph 1 (nights, 1Q23–4Q27) beside the setup, and Graph 2 (margin bridge, formerly Graph 3) beside margins. At 3.8in the memo spills to 3 pages. |
| Setup | "Strip out the bundle and one-off events and nights grew ~7% in 1H26, slower than in 2025". |
| Illusion | Explains the lap: growth is measured against a year earlier, so once a feature has been live twelve months both years include it. |
| Nowcast | Explains the mapping: covered cities are large, mature markets growing more slowly than the platform; a straight-line fit (one slope, one intercept; `REVIEWS_INDEX_v2.md` §B) estimated on pre-RNPL quarters converts the read. |
| ADR | The FX point is stated plainly. Outside FX, our 3Q26 price growth matches the Street's (thesis 2 draft: ex-FX +2.96% vs +2.95%). |
| Valuation | The three bases are named in words; the NTM move splits about half EBITDA and half multiple. |

## Graph 1's 3Q26 "underlying" bar (7.8%)

This comes from the model; the chart just draws it. `Nights_Engine!X79` is the residual `B77 − bundle − cancellations − events`:
9.20 − 2.31 − (−0.93) = 7.82. That is 1pt above 2Q26's 6.8%, and the chart shows it. See the session answer for the options. It is a team decision, and the memo's wording ("~7% heading to ~6% by 2H27") is consistent with the model as it stands.
