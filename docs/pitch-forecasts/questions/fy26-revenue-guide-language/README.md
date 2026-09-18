# C03 — fy26-revenue-guide-language

**Question.** How will Airbnb's FY26 revenue growth guidance change at the 5 Nov 2026 print? Multiple choice (a) raised (point/range midpoint ≥16%, "at least 16%", "high teens"); (b) reiterated "at least mid teens"; (c) narrowed to ≈15% ("approximately 15%", "mid teens"); (d) lowered or softened; (e) no FY26 revenue guidance. Full text and the rounding/format conventions adopted: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable).** (a) 0.37 · (b) 0.18 · (c) 0.28 · (d) 0.08 · (e) 0.09.

**Why.** In every November letter that carried an FY line (FY23, FY24, FY25 margin) management converted the floor into an "approximately X" point above the floor, and the FY26 revenue guide has been raised at both of its updates. The point they can state on 5 Nov is fixed by arithmetic: 9M actual (1H26 $6,286M plus a Q3 print the guide history puts at $4,740–4,820M) plus the 4Q26 guide midpoint ($3,059–3,161M across the repo's two constructions) gives FY26 growth of 15.1–16.4%, centred at 15.7%. That straddles the 15.5% rounding line, so "approximately 16%" (a) edges "approximately 15% / mid teens" (c); a plain reiteration (b) has no November precedent but costs nothing; a cut (d) needs a Q4 midpoint below ≈$2,990M; (e) is the risk that a new, now-redundant line is simply dropped.

**Files.**
- `research-log.md` — claims ledger, query log, estimates, sensitivity, monitoring calendar.
- `forecasts/2026-09-17-forecast.json` — the vector and metadata in the brief's schema.
- `datasets/decomposition.py` → `decomposition_output.csv` — reproduces the arithmetic and all four vectors (standard library only).
- `datasets/fy26_guide_arithmetic_grid.csv`, `quarterly_revenue_guide_cushions.csv`, `ledger_fy_revenue_and_margin_guides.csv`, `reaction_panel_fy_actions.csv` — repo extracts.
- `sources/` — letter outlook extracts (3Q22–2Q26), LSEG consensus snapshot (11 Sep), Polymarket/Kalshi searches (no guidance market exists).

**Not submitted anywhere.** Next: Astra audit (`audits/`), then a revision-2 response.
