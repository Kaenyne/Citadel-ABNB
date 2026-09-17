# C04 — fy26-margin-sentence

What FY26 adjusted EBITDA margin sentence Airbnb gives at the 3Q26 print (5 Nov 2026): held "at least 35.5%" / "approximately 36%" or "at least 36%" / ≥36.5% / lower or softer / none. Batch A03 (with C09).

- `research-log.md` — revision 1, 2026-09-17 (Fable). Final vector a 0.26 / b 0.42 / c 0.05 / d 0.24 / e 0.03; anchor (repo prior M3/WS05) b 0.55; |final − anchor| 13 pts.
- `forecasts/2026-09-17-forecast.json` — machine-readable vector, estimates, sensitivities, monitoring.
- `datasets/mc_sentence_model.py` — the decomposition Monte Carlo (numpy only; also produces C09); `mc_sentence_results.json`, `mc_joint_and_conditionals.json`, `mc_run_log.txt` its outputs; `fy_margin_guide_ledger.csv`, `quarterly_margin_sentence_ledger.csv` the guidance-ledger extracts.
- `sources/` — Polymarket and Kalshi API snapshots (2026-09-17T02:52–02:54Z; no margin market exists) and `web_search_log.md` (4 WebSearch calls shared with C09, two fetches, one stale source discarded).

Reproduce: `py -3.13 datasets/mc_sentence_model.py` from the `datasets/` folder (seed 20260917, 400,000 draws, ~10 s).

**Revision 2 (2026-09-17, audit response A03).** Final vector a 0.33 / b 0.30 / c 0.05 / d 0.27 / e 0.05 (leading option now (a); Astra 0.30 / 0.39 / 0.06 / 0.22 / 0.03). Model `datasets/mc_sentence_model_v2.py` (reads C01's `c01_v2_final_mixture_hist.csv`; `py -3.13 -B` from this folder, ~40 s) → `mc_sentence_results_v2.json`, `mc_joint_and_conditionals_v2.json` (the one C04×C09 joint and every conditional), `mc_run_log_v2.txt`; ledgers `fy_margin_guide_ledger_v2.csv`, `quarterly_margin_sentence_ledger_v2.csv`. Revision-1 files kept as the audit trail. Response: `docs/pitch-forecasts/audits/A03-audit-response.md`.
