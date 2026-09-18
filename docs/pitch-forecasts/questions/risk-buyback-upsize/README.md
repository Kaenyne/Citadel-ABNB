# R06 — risk-buyback-upsize

Will Airbnb announce a new share repurchase authorization ≥$5bn between 17 Sep 2026 and the Feb print (4Q26 letter inclusive), or repurchase ≥$1.5bn in 4Q26? Binary. A risk to the short.

- Forecast (revision 1, 2026-09-17): **P = 0.55**, credible interval 0.40–0.68. Base rate 0.50, decomposition 0.54 (Monte Carlo), anchor 0.51 (the team's market-implied note; no market exists).
- **Revision 2 (2026-09-17, after audit A11): P = 0.46**, credible interval 0.30–0.60. Base rate 0.35 (pure frequencies: three board episodes, size ≥$5bn 2 of 4), decomposition 0.47 (`datasets/r06_model_v2.py`: November hazard 0.12 fixed, February rule = blend of the MLE logistic and the hand-set rule, size 0.75 labelled a regime judgement, leg-B bar $1.45bn), anchor withdrawn (NO_EXTERNAL_ANCHOR). Impact: EPS 0.00, stock +$1.2, EV +$0.6/share, immaterial. Revision-1 files untouched; new: `r06_model_v2.py`, `r06_v2_summary.csv`, `r06_v2_sensitivity.csv`, `sources/newsroom_news.airbnb.com_20260917T132231Z.html`.
- Mechanism: $3.4bn remained at 30 Jun 2026 against a ~$1.05–1.1bn quarterly pace; ~$1.2–1.3bn (about 1.2 quarters) will remain at the Feb print, inside the band where the board renewed in Feb 2024 ($750M left) and Aug 2025 ($1.5bn left). Both of the last two programs were $6bn. The $1.5bn-quarter leg is worth ~0.08 on its own.
- Impact: immaterial (EV ≈ +$0.7/share). Authorizations are announced only inside the letter and produce abnormal returns indistinguishable from zero; the FY27 share count already assumes the buyback continues.
- Files: `research-log.md`, `forecasts/2026-09-17-forecast.json`, `datasets/r06_model.py` (numpy, seed 20260917), `datasets/r06_summary.csv`, `r06_sensitivity.csv`, `authorization_history.csv`, `print_state_panel.csv`, `sources/` (Polymarket/Kalshi JSON 2026-09-17T03:41:48Z, EDGAR submissions index, web query log).
- Batch A11 with R08 and R09.
