# WS32: Morning report, explainer page, WORKBOARD rows

Read `docs/margin-build/00_BRIEF.md`, `SYNTHESIS.md` (post-audit), `audit/AUDIT_RESPONSE.md`, `RUN_STATE.md`. Slug: `32_morning_report`.

## Do

1. `docs/margin-build/MORNING_REPORT.md` for Krish, who has just woken up and has ten minutes: (a) the margin view in eight lines with the
   numbers (3Q26, 4Q26, FY26 vs floor and consensus, FY27 and the incremental margin, FY28); (b) how the model works in one paragraph; (c) the
   backtest evidence in one table (combined object vs baselines, both windows, both weightings, n); (d) what the alt-data search found and did not;
   (e) the cyclicality result; (f) the 5 Nov card numbers; (g) the audit: findings count by severity, what was fixed, what was rejected, what is open;
   (h) what to read next and in what order; (i) decisions Krish must make (numbered); (j) the run log summary (agents, wall time, failures, resumes).
2. An explainer page `docs/explainers/margin_build_2026-09-14.html` (self-contained HTML, inline CSS, no external scripts, light and dark themes
   via prefers-color-scheme, phone-width friendly), following the pattern of the existing pages under `docs/explainers/`: the margin model in
   plain words, the forecast tables, the seasonal and cycle charts as inline SVG (draw from the CSVs; no matplotlib images), the consensus gap,
   the audit summary. Every number from a CSV; state the file for each table.
3. Append rows to `docs/revenue-forecast-strategy/WORKBOARD.md` (append only; do not edit existing rows): one row per workstream of this run
   with status, note path, and the branch `krish/margin-build`; and a "Done (14 Sep 2026)" block in the same style as the existing "Done (11 Sep 2026)".
4. Append a `docs/margin-build/notes/README.md` file map (every note, script folder, data folder, one line each).
5. Final message: the ten-line summary and the file paths. The orchestrator will commit, push, open the PR and publish the artifact.
