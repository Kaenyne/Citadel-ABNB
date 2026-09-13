# B2 mechanism refuter — preregistration

Codex B2 mechanism refuter · 2026-09-13 17:47 UTC · branch `codex/lane2-full`.

The exact sentence under review is: “The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.”

## Pre-registered pass line

Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.

Recorded before executing the independent diagnostic. Verify the exact numerical sentence against the headline PIT weight 2/3, strong threshold |S1| > 0.5%, and W1/W2 origin definitions. Zero revision is a separate sign. The mechanism attack is consensus convergence toward the just-announced guide, which is known at the signal/entry time. These diagnostics are adversarial, retrospective comparisons, not a newly selected strategy or evidence of an investable edge.

Fixed attacks: (1) recompute signal, revisions, counts and executable-return means; (2) compare kernel with raw announced-guide gap on identical rows, with no new threshold tuning; (3) residualize kernel and revisions against announced-guide gap, and measure the change in in-sample fit from adding the kernel; (4) test the revision remaining after a full move to the announced guide; (5) exclude unchanged revisions as a labelled alternative estimand; (6) leave one event out for return-sign fragility; (7) compare raw ABNB returns and QQQ-adjusted returns on the same strong cells. W2 is a subset of W1. No p-values or independent replication claims. Any successful attack on stronger causal/trading language is distinguished from a refutation of the exact descriptive sentence.

Inputs are the metadata-corrected B2 run `run_20260913T171654_499731Z`, its named guidance ledger and executable returns input. All new scripts and outputs go under `refute_b2_mechanism`; no registration or scorer run is required because this is an audit, not a forecast object. The parent owns the shared workboard claim/update.
