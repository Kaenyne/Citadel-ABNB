# Overnight run 11-12 Sep 2026: shared brief for all workstreams

Branch `krish/overnight-2026-09-11`, worktree `C:\Users\krish\citadel-abnb-overnight2`. Owner Krishang Surapaneni (ksurapaneni@ufl.edu), compiled with Claude Code.

## Context
- Team pivoted 10 Sep 2026 from a bottom-up driver model to trading the 3Q26 print (5 Nov) and forecasting the Q4 guide. Pitch due 2 Oct 2026. Never propose waiting for the print.
- Reconciled team nights baseline: 3Q26 +9.9% (146.8mm, band 8.5-10.3), 4Q26 +8.9% (132.7mm, band 8.1-9.9), FY26 +9.6%. See `research/notes/2026-09-10_nights-baseline-reconciliation.md`.
- The stock trades the forward nights guide and the acceleration sign, not the beat (19/19 beats). A nights deceleration vs 2Q26's 10.3% is the base case.
- RNPL: read `docs/RNPL_HANDOFF.md` before touching cancellations. Key facts: US RNPL began during 3Q25 (announced 14 Aug 2025); global rollout announced 17 Feb 2026 with currency exceptions; ~20% of 1Q26 GBV from RNPL, >20% in 2Q26; management cited ~16% historical vs ~17% aggregate cancellation; the ~3-pt 1Q26 nights lift was RNPL + cancellation-policy + simplified-fees combined.

## Rules
- Forecast every quarter independently. Consensus is a comparison column, never an input. No valuation, no target price, no long/short call.
- Separate sourced facts, descriptive results, assumptions and causal claims. Say what each test can and cannot identify. Preserve evidence that weakens the hypothesis. Small n: report permutation p and leave-one-out RMSE vs naive, as `data/processed/overnight/05_fx_fits.csv` does.
- Raw gitignored inputs (calendars, letters, transcripts, filings, FRED cache) live in the MAIN tree at `C:\Users\krish\citadel-abnb\data\raw` and `C:\Users\krish\citadel-abnb\data\processed`. Read them there. Never modify the main tree.
- Write only inside this worktree: scripts `analysis/src/overnight2/<WS>_*.py`, outputs `data/processed/overnight2/<WS>/`, note `research/notes/overnight2/<WS>_<slug>.md`. Do not touch other workstreams' paths.
- Python: `py -3.13` has pandas 2.3.3, numpy, pyarrow, statsmodels, openpyxl, matplotlib. The venv python `C:\Users\krish\citadel-abnb\.venv\Scripts\python.exe` (3.11, pandas 3.0.5, no pyarrow/statsmodels) ran the original calendar pilot.
- Bash calls time out at 10 minutes. Long computations: write per-unit checkpoints, run in the background with a log file, and poll.
- Notes: date 2026-09-11, author line "Krishang Surapaneni (compiled with Claude Code)", sections: Bottom line, Tables, Method, What this can and cannot identify, Next evidence, Files. Plain prose, no em-dashes.
- At the end, commit ONLY your own files: `git add <your paths> && git commit -m "<WS>: ..."`. If `index.lock` exists, wait 30 s and retry, up to five times. Never push.
