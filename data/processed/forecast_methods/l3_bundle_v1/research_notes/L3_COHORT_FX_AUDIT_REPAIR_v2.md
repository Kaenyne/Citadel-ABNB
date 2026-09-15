# L3 cohort FX — v2 audit repair protocol

2026-09-13. Independent reviewer nclh found three direct-input validation holes after v1 freeze. This new note and cohort_fx_v2 preserve all v1 code/output/results. The numerical research specification and verdict are unchanged; the following engineering gates are fixed before repair tests or v2 scenarios.

1. A rate's quote cutoff must not exceed its stated information cutoff. Date-only information dates represent the close of that UTC date. USD's constant-one identity does not need a market quote, but its metadata will still use a coherent cutoff no later than the source information date.
2. An observed rate's quote cutoff must be within its monthly/quarterly observation period, and an observed full period cannot end after the information cutoff. Missing or future quote timestamps are errors. Month-end weekends can make the last quote earlier than the period end; no unobserved future period is silently deemed observed.
3. The fixed 2025 annual reference cannot be called complete when only a few observations survive. Require at least 240 finite unique daily observations per currency, observations within seven calendar days of both year boundaries, and no consecutive observation gap over ten calendar days. These are explicit coverage gates for a public daily time-average proxy, not transaction-coverage claims or estimated parameters. They do not replace positivity/uniqueness checks.

Tests must reproduce and reject the three attacks: source date 2026-02-01 with Q1 quote 2026-03-31; Q1 observed quote cutoff 2025-01-01; and only one 2025 quote retained per currency while later years remain. Verify the canonical rates pass all gates and the ten analytical outputs (excluding versioned source metadata/manifests) remain numerically equivalent. A fresh v2 rebuild must be byte-identical with matching arguments. No hedge adoption or research pass is inferred from these repairs.

## RESUME

Implement v2, rerun the original boundary suite plus independent review regressions, rebuild into new output directories and provide the reviewer final paths/hashes. Preserve this protocol and publish a separate v2 result receipt once checked. L4 should consume the repaired version only after independent closure.
