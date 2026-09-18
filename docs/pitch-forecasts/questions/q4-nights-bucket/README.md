# C02 — q4-nights-bucket

**Question.** What qualitative growth bucket will Airbnb give for 4Q26 Nights and Seats Booked at the 5 Nov 2026 print? Multiple choice (a) low double digits or ≥10% language; (b) around 10% / high-single-to-low-double / similar to Q3 with Q3 <10; (c) high single digits; (d) mid single digits or lower, or a no-bucket "moderate/decelerate"; (e) no descriptor. Full text and the conventions adopted: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable).** (a) 0.21 · (b) 0.19 · (c) 0.39 · (d) 0.17 · (e) 0.04.

**Why.** Management's next-quarter nights sentence sits below the just-printed rate in 9 of 16 cases and in 3 of 4 November letters; in the bucket era the bucket midpoint is set 1–4 points below the printed rate whenever the comp hardens, and the 4Q26 comp (+9.8%) is one point harder than Q3's. Every repo model has 4Q26 at 7.6–8.9%, the Street bar is 9.9%, and buckets carry a 1–3 point cushion, so "high single digits" is the modal sentence. The (a) mass is the branch where the 3Q26 print lands at or above 10% (0.38 on the team band) and October runs double digits; the (d) mass is mostly format risk (a directional "moderate" with no bucket resolves (d) by the fine print).

**Files.**
- `research-log.md` — claims ledger, query log, estimates, sensitivity, monitoring calendar (schema: forecast skill `references/research-log-format.md`).
- `forecasts/2026-09-17-forecast.json` — the vector and metadata in the brief's schema.
- `datasets/decomposition.py` → `decomposition_output.csv` — reproduces all four vectors (standard library only).
- `datasets/nights_descriptor_vs_printed_and_comp.csv`, `ledger_next_quarter_nights_guides.csv`, `driver_history_nights_revenue.csv`, `reaction_panel_fy_actions.csv` — repo extracts used for the base rate.
- `sources/` — letter outlook extracts (3Q22–2Q26), Kalshi KXABNB/KXABNBA snapshots (zero liquidity, recorded for the audit), Polymarket searches, LSEG consensus snapshot.

**Not submitted anywhere.** Next: Astra audit (`audits/`), then a revision-2 response.
