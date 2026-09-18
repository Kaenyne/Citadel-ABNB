# Codex (gpt-6-astra) research audit — batch {BATCH} ({QIDS})

You are auditing probability forecasts produced overnight by another agent for a stock-pitch calibration run. Repository root
is your working directory; you have read-only access; you may run Python (`py -3.13` has pandas, numpy, statsmodels, yfinance;
`python` is the repo venv with pandas, statsmodels, scipy) to re-compute anything, but you cannot write files except your final
answer, which the harness saves to `docs/pitch-forecasts/audits/{BATCH}-research-audit.md`. No network access is assumed; if a
fetch fails, say so and audit from the saved snapshots under `sources/`. Do not open `data/raw/theo_onedrive` or `data/raw/licensed`.

## Context

Read, in this order: `docs/pitch-forecasts/00_BRIEF.md`; the question blocks for {QIDS} in `docs/pitch-forecasts/QUESTIONS.md`;
then for each question the folder `docs/pitch-forecasts/questions/<slug>/` (research-log.md, forecasts/2026-09-17-forecast.json,
sources/, datasets/). The forecasting standard is `C:/Users/krish/.claude/skills/forecast/SKILL.md` (copy of the log schema at
`docs/pitch-forecasts/examples/research-log-format.md`). A model audit of the required depth is
`docs/pitch-forecasts/examples/example-research-audit.md`.

## What to audit (reproduce before you assert)

1. Question fidelity: does the forecast answer the question exactly as written (object, threshold, date, conditional vs unconditional)?
   Any silent re-definition is a critical finding.
2. Claims ledger: every load-bearing claim traced to the cited file or URL; published/retrieved dates present; stale or
   training-knowledge claims flagged; repo numbers re-read from the CSV/note (state the path and the value you found).
3. Base rates: recompute every base rate from the named repo files (`data/processed/overnight/02_guidance_ledger.csv`,
   `abnb_guidance_reaction_panel.csv`, `abnb_earnings_reactions.csv`, the RNPL ledger, the L0 register, etc.); check n, the
   window, the definition, and whether events failing the question's own gates were excluded.
4. Independence of the three estimates; whether the anchor is a real market/consensus number with a timestamp; whether
   |final − anchor| is justified by a named asymmetry or flagged NOT_INDEPENDENTLY_DERIVED.
5. Coherence: MC vectors sum to 1; continuous percentile tables monotone with sensible bounds mass; binaries respect the
   extreme-probability gate; cross-question coherence inside the batch (e.g., R03 ≤ min(C06a, R01)).
6. Impact tables (R/B questions): every delta traced to a repo sensitivity (brief §Sensitivities) or a shown computation;
   EV arithmetic; materiality verdict consistent with the numbers.
7. Reasoning: the strongest case against the forecast; confirmation-shaped query logs; vivid-but-small factors weighted over
   boring gates; anything the pitch memo would be embarrassed by in front of a Citadel judge.

## Output format (saved as `docs/pitch-forecasts/audits/{BATCH}-research-audit.md`)

Markdown. Start with a five-line verdict per question (is the number defensible as written; what must change first).
Then a findings table: `id | question | severity (critical / major / minor) | file:line or field | what is wrong | how you verified |
proposed fix (with the recomputed number where you have one)`, ordered by severity, at most 25 findings, each verified.
Then a short section per question: "what the log does well and should keep". Then, for each question, your own independent
number (binary point, MC vector, or percentile table) with a two-line derivation, so the response agent can compare.
Finally, a dependency-free reproduction script (Python, stdlib + pandas only) as a fenced code block that recomputes the
base rates you checked from the repo files; the response agent will save it as `audits/{BATCH}-reproduce.py`.
No praise padding; be specific.
