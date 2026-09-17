# C09 — q4-margin-direction-sentence

What Airbnb says about 4Q26 adjusted EBITDA margin versus 4Q25's 28.3% at the 3Q26 print (5 Nov 2026): down / approximately flat / up / no quarterly margin sentence. Batch A03 (with C04, whose log carries the fuller FY-sentence evidence).

- `research-log.md` — revision 1, 2026-09-17 (Fable). Final vector a 0.28 / b 0.27 / c 0.40 / d 0.05; anchor (repo prior WS05/M3, decline family) a 0.50; |final − anchor| 22 pts on (a), 5 pts on the final's leading option (c).
- `forecasts/2026-09-17-forecast.json` — machine-readable vector, estimates, sensitivities, monitoring.
- `datasets/` — `quarterly_margin_sentence_ledger.csv` (all 21 next-quarter margin sentences since 2Q21 with direction family and outcome, from the guidance ledger), `fy_margin_guide_ledger.csv`, and the shared Monte Carlo (`mc_sentence_model.py`, `mc_sentence_results.json`, `mc_joint_and_conditionals.json` with the C04 × C09 joint, `mc_run_log.txt`).
- `sources/` — Polymarket and Kalshi API snapshots (2026-09-17T02:52–02:54Z; no margin market) and `web_search_log.md` (shared with C04).

Reproduce: `py -3.13 datasets/mc_sentence_model.py` from the `datasets/` folder (seed 20260917, 400,000 draws, ~10 s).

**Revision 2 (2026-09-17, audit response A03).** Final vector a 0.22 / b 0.26 / c 0.47 / d 0.05 (Astra 0.29 / 0.25 / 0.41 / 0.05). Shared model and outputs mirrored from the C04 folder as `datasets/*_v2.*` (run the script from the C04 folder; it reads C01's histogram by relative path). `mc_joint_and_conditionals_v2.json` carries the C04×C09 joint and the conditionals on C01 and on C04. Revision-1 files kept as the audit trail. Response: `docs/pitch-forecasts/audits/A03-audit-response.md`.
