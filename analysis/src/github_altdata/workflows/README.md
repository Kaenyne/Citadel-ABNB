# Workflow scripts used for the GitHub alt-data run (13-14 Sep 2026)

Verbatim copies of the Claude Code Workflow scripts that orchestrated the run, kept so a teammate can see exactly
what each agent was asked. They are not runnable outside a Claude Code session; the runnable, resumable versions of
the scout/review/sample stages are ../wf_scouts.js, ../wf_reviews.js, ../wf_samples.js with ../state.py.

- 01_scout_and_review.js: 262 Sonnet scouts (123 themes x gh/web + 16 persona lenses), dedupe, Opus review at 5 per batch (the original design; interrupted by the usage limit, then replaced by the tiered triage in ../wf_reviews.js).
- 02_integration_plan.js: seven Fable lane specs mapping the sampled sources onto the team's objects, plus one red-team pass (output: docs/github-altdata/integration_plan_raw.json, INTEGRATION_PLAN.md).
- 03_build_dolthub_l0.js: the G1b build (DoltHub consensus history into the L0 register) with two independent verifiers.
- 04_build_archives_and_daio.js: the WPK-A, WPK-B and C2-daio builds, each with its own verifier.

Session runbook: docs/github-altdata/RUN_STATE.md. Catalogue note: research/notes/github_altdata/2026-09-14_github-altdata-catalog.md.
