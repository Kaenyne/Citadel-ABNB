# R15 — risk-world-cup-quantified-small

**Question.** By the Feb 2027 print, will management quantify the 2026 World Cup's contribution to nights or GBV at ≤1 point, or state that it was immaterial / not meaningful to the growth rate? Binary. Resolution ~11 Feb 2027. Full text and conventions: `research-log.md` §0b.

**Forecast (revision 1, 2026-09-17, Fable, batch A12 with R10, R11, R16).** **P = 0.14**, credible interval 0.07–0.25.

**Why.** In eight event discussions since 1Q24 (Paris ×4, the Paris lap, Milan, the World Cup ×2) management has never put a points figure on an event; it counts guests, listings and supply and calls the World Cup "the largest event in Airbnb's history". The one size statement on record is the 2Q24 letter's "the impact of a single city for a limited duration is relatively small compared to the total nights booked in a region" (Paris); the Paris lap in 3Q25 was framed as a "slightly unfavorable comparison", a headwind, not nothing. The Yes routes are a ≤1pt figure (0.02 at 5 Nov, 0.04 at Feb) and an "immaterial / not a meaningful driver" statement (0.05 at each print), the latter most likely in February when management has an incentive to defuse the 2Q27 comp before the May guide. Tree 0.15, record 0.10, final 0.14. A lenient resolver who counts "may be temporary"-style language would read 0.24.

**Impact if it happens.** A disclosure, not a booking: it removes the memo's "unsized event" tell and confirms a small 2Q27 lap (+0.1–0.15pt of FY27 nights, ~$20M). Stock ~+$1 (narrative). EV 0.14 × $1 ≈ **$0.15/share: immaterial.** Drop from the risks list; keep the "never sized an event" sentence in the thesis text with the 2Q24 caveat.

**Files.**
- `research-log.md` — claims ledger (verbatim quotes), query log, three estimates, sensitivity, pre-mortem, monitoring, `## 9. Impact`.
- `forecasts/2026-09-17-forecast.json`.
- `datasets/r15_model.py` — deterministic route tree; outputs `r15_event_record.csv` (the eight coded event discussions), `r15_tree.csv`, `r15_sensitivity.csv`.
- `sources/event_passages_letters_transcripts_extract.txt` — regex extract of every event passage from the letters and call transcripts (kept from the first attempt; regenerated content verified this run).

**Not submitted anywhere.** Next: Astra audit, then a revision-2 response.
