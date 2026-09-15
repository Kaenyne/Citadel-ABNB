# GBV Git delivery — 15 September 2026

User-authorized commit/push of the completed GBV sessions. Delivery scope and canonical version map are recorded in `05_backtests/GD_GIT_DELIVERY_v1.md`. Branch `codex/submission-readiness-v1` was fast-forwarded to current `origin/main` at `a3af33ee` before staging; no research-input collisions occurred.

Publication review: no prohibited raw stores, licensed exports or credentials found. All staged files are scoped to the GBV work plus root attributes needed to preserve audit hashes. Existing live team-model and frozen-harness files are unchanged by this research commit. Main's newly merged margin work is not re-audited here.

Validation before commit:66 tests pass across the event, forecast, integration, registry, joint-model and adversarial suites. Pytest emits a local cache-permission warning only; no test failure. Both unchanged scorers return0, agree on328 score rows and preserve every prior328 score row and144 protected files. Publication verifies every new staged blob equals its local audited bytes. The whitespace check passes with a narrow generated-SVG exception that preserves Matplotlib's path-coordinate whitespace.

## RESUME

Push this prepared commit to `origin/codex/submission-readiness-v1` and open the review PR against main. Request teammate review; do not merge. Use `GD_DECISION_REPORT_v2.md` and the five-page `outputs/gbv-decision-20260915-v4/GBV_decision_visuals.pdf` as entry points. Preserve all research caveats and earlier failed tests. Exact commit and PR URLs belong in the Git delivery response.
