# R09 — risk-new-businesses-quantified-material

By the Feb print, will management disclose that hotels, Experiences or Services together are ≥3% of Nights and Seats Booked, or ≥3% of GBV, or give a FY27 revenue figure ≥$500M for them? Binary. A risk to the short.

- Forecast (revision 1, 2026-09-17): **P = 0.25**, credible interval 0.14–0.38. Base rate 0.21 (0 upgrades in 8 "small" descriptor-prints, Laplace), decomposition 0.26, anchor 0.27 (C05's quantification object; no market exists).
- **Revision 2 (2026-09-17, after audit A11): P = 0.25**, credible interval 0.13–0.38 (number unchanged, construction rebuilt). Base rate 0.24 (0 upgrades in 5 descriptor opportunities, Laplace 0.143 per print), decomposition 0.26 (`datasets/r09_model_v2.py`: upgrade hazards 0.12 / 0.20 incl. the same-day 10-K venue, P(figure ≥3) 0.55 from the supply requirement file, aggregation route 0.02), anchor withdrawn (NO_EXTERNAL_ANCHOR; C05 rev 2 = 0.28 as a sibling comparison). Impact unchanged: stock +$2, EV +$0.5/share, immaterial. New: `r09_model_v2.py`, `r09_v2_summary.csv`, `r09_v2_sensitivity.csv`, newsroom snapshot.
- Mechanism: the shares almost certainly exist (hotels "single-digit" and growing ~3x homes; team assumption 3.5%; seats ~2%), so Yes needs only a disclosure. Management has held "single-digit" through three statements, called seats "immaterial", never given a line revenue, and the FY2025 10-K says "substantially all" revenue is stays. The Feb annual review, the new hotels CBO and the credit expiry are the upgrade routes.
- Impact: immaterial (EV ≈ +$0.5/share); a hotel-share disclosure would also make the homes deceleration and the ADR/take-rate dilution explicit.
- Files: `research-log.md`, `forecasts/2026-09-17-forecast.json`, `datasets/r09_model.py`, `r09_summary.csv`, `r09_sensitivity.csv`, `new_business_disclosure_history.csv`, `sources/` (market JSON, web query log).
- Batch A11 with R06 and R08.
