# Lane 2 CLOSE — pre-registration

Codex parent · 13 Sep 2026 · `codex/lane2-full`. Written before A2 results and before CLOSE.

## Pass line (verbatim from lane2/CLOSE.md)

Every sentence in the claims file has a number, a file, a caveat and both windows; nothing from the kill list; both scorers ran after the last
registration; the branch is pushed; the PR is open or the compare URL is printed.

## Execution rules

Use `lane2_validation_v1/run.py --stage close` to call the frozen scorer then FORMAT 1.1 with outputs in a new snapshot, applying the Gate 1 preregistration. Both must exit 0. The committed frozen board stays byte-identical; every old scoreboard row must survive, with exact keys/counts/flags/missingness and float error below 1e-9 absolute. Record new methods separately and determine leader changes from the added snapshot rows. Only write a new SCOREBOARD_v3.md if an eligible W1/W2 leader changes; an unscored guide_mid row has no baseline and is not a revenue forecasting leader.

For each of A2, B2 and F, use the package's exact proposed memo sentence for three independent refuters (vintage, power, mechanism). Require at least five explicit attacks each. Two `survived` verdicts are required to promote the exact sentence; `partial` is not survived. A research test's failure/underpowered verdict must remain visible even if refuters agree with an appropriately limited negative sentence. A human team's eleven open decisions are never resolved by this promotion process.

List all new FORMAT 1.1 LIVE rows with method, object, target, quarter, vintage, point, and scenario identity. Check each package's intended rows exist in the shared registry, carry true RUN_DATE, and were registered with the existing API. Recompute at least eight saved cells/identities from source inputs across completed packages, without altering their outputs. Check M's register is append-only against its dated backup. Do not promote unsupported macro predictions or undocumented publication-date assumptions.

Write the claims file and a complete PR body; update the workboard and active run log; preserve the initial stopped run. Review staged files and push only this lane's source, outputs, notes and sanctioned L0 append/backup. Attempt the available GitHub PR tool; if unavailable or denied, retain the body on the pushed branch and print the compare URL.

L is skipped: `SANCTIONED_BY_THEO: no` is the observed header. No policy-monitor fetch or scheduled capture is run by this lane.

## RESUME

At CLOSE, turn these checks into evidence, not assumptions. Publish failed or limited package results with their caveats and preserve all refuter verdicts. Finish with the pushed branch and a real PR link or the compare URL.
